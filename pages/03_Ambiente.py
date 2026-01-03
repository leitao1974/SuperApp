import sys
import os

# --- 1. CONFIGURAÇÃO DE CAMINHOS ---
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(current_dir)
sys.path.insert(0, root_dir)

import streamlit as st
import google.generativeai as genai
from pypdf import PdfReader
from docx import Document
from io import BytesIO
from duckduckgo_search import DDGS
import time

# --- 2. CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="Ambiente & Compliance",
    page_icon="🌿",
    layout="wide"
)

# --- 3. IMPORTS LOCAIS ---
try:
    import utils
    import legislacao
except ImportError as e:
    st.error(f"Erro de configuração: {e}")
    st.stop()

# --- 4. BARRA LATERAL (Apenas Key e Perfil) ---
utils.sidebar_comum()

# --- 5. TÍTULO E CHAVE ---
st.title("🌿 Análise Ambiental & Compliance")
st.caption("Auditoria PATE | Pesquisa Web | Análise Legal")

# Recuperar a chave da memória
api_key = st.session_state.get("api_key", "")

if not api_key:
    st.info("⬅️ **Aguardando API Key:** Insira a chave no menu lateral esquerdo para começar.")
    st.stop()

# ==========================================
# --- FUNÇÕES ---
# ==========================================

def get_available_models(key):
    """Lista os modelos disponíveis na API (Flash, Pro, etc.)"""
    try:
        genai.configure(api_key=key)
        models = genai.list_models()
        # Filtra apenas modelos que geram texto
        return [m.name for m in models if 'generateContent' in m.supported_generation_methods]
    except:
        return ["models/gemini-1.5-flash"] # Fallback

def get_pdf_text(pdf_file):
    text = ""
    try:
        reader = PdfReader(pdf_file)
        for page in reader.pages:
            text += page.extract_text() or ""
    except Exception as e:
        st.error(f"Erro ao ler PDF: {e}")
    return text

def search_online(query):
    if not query: return ""
    results_text = ""
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(f"{query} legislação oficial", max_results=3))
        for r in results:
            results_text += f"\n>>> WEB: {r['title']} ({r['href']}) <<<\n{r['body']}\n"
        return results_text
    except: return ""

def create_docx(text):
    doc = Document()
    doc.add_heading('Relatório de Auditoria Ambiental', 0)
    for line in text.split('\n'):
        line = line.strip()
        if not line: continue
        if line.startswith('## '): 
            doc.add_heading(line.replace('## ', ''), level=1)
        elif line.startswith('### '): 
            doc.add_heading(line.replace('### ', ''), level=2)
        elif line.startswith('- ') or line.startswith('* '): 
            doc.add_paragraph(line[2:], style='List Bullet')
        else: 
            doc.add_paragraph(line)
    b = BytesIO()
    doc.save(b)
    b.seek(0)
    return b

def run_analysis(target_text, lib_ctx, manual_ctx, web_ctx, key, model_name):
    """Executa a análise com o modelo escolhido pelo utilizador."""
    genai.configure(api_key=key)
    
    # Usa o modelo dinâmico
    model = genai.GenerativeModel(model_name)
    
    prompt = f"""
    Atua como Auditor Ambiental Sénior (Protocolo PATE).
    
    === LEGISLAÇÃO APLICÁVEL ===
    {lib_ctx}
    
    === DOCUMENTOS EXTRA / WEB ===
    {manual_ctx}
    {web_ctx}
    
    === DOCUMENTO DO PROJETO ===
    {target_text}
    
    TAREFA:
    Realiza uma auditoria de conformidade rigorosa. Identifica:
    1. Enquadramento Legal e Maturidade.
    2. Check-up de Conformidade (Detetar falhas face à legislação fornecida).
    3. Riscos Críticos e Omissões.
    4. Recomendações de Melhoria.
    """
    
    try:
        return model.generate_content(prompt).text
    except Exception as e:
        return f"Erro IA ({model_name}): {e}"

# ==========================================
# --- INTERFACE ---
# ==========================================

if 'uploader_key' not in st.session_state: st.session_state.uploader_key = 0

# --- A. CONFIGURAÇÕES (Legislação + Modelo) ---
library = legislacao.get_library()
lib_context = ""

with st.expander("⚙️ Configurações de Análise (Modelo & Leis)", expanded=False):
    
    # 1. Seletor de Modelo Dinâmico
    col_mod, col_info = st.columns([1, 2])
    with col_mod:
        modelos_disponiveis = get_available_models(api_key)
        # Tenta encontrar o 1.5 Flash como padrão, senão usa o primeiro
        idx_padrao = 0
        for i, m in enumerate(modelos_disponiveis):
            if "1.5-flash" in m: 
                idx_padrao = i
                break
        
        selected_model = st.selectbox("Modelo de IA:", modelos_disponiveis, index=idx_padrao)
    with col_info:
        st.caption(f"Modelo ativo: **{selected_model}**")
        st.caption("Nota: Modelos 'Pro' são mais inteligentes mas mais lentos.")

    st.divider()
    
    # 2. Seleção de Legislação
    st.markdown("**Base Legislativa:**")
    c1, c2 = st.columns(2)
    i = 0
    for cat, laws in library.items():
        with (c1 if i % 2 == 0 else c2):
            st.markdown(f"**{cat}**")
            for name, info in laws.items():
                if st.checkbox(name, key=f"leg_{name}"):
                    lib_context += f"- {name}: {info['mandato']}\n"
        i += 1

st.divider()

# --- B. UPLOADS ---
col_main, col_extra = st.columns([3, 2])

with col_main:
    st.subheader("📄 Documento Principal")
    f_main = st.file_uploader(
        "Carregar Relatório ou Projeto (PDF)", 
        type="pdf", 
        key=f"main_doc_{st.session_state.uploader_key}"
    )

with col_extra:
    st.subheader("🔗 Contexto Extra")
    f_extra = st.file_uploader(
        "Anexos Legais (PDF)", 
        type="pdf", 
        accept_multiple_files=True, 
        key=f"extra_doc_{st.session_state.uploader_key}"
    )
    web_q = st.text_input("Pesquisa Web (Ex: 'PDM de Sintra regulamento')")

# --- C. BOTÃO DE AÇÃO ---
if st.button("🚀 EXECUTAR AUDITORIA", type="primary", use_container_width=True):
    if not f_main:
        st.warning("⚠️ Carregue o documento principal primeiro.")
    else:
        with st.status("⚙️ A realizar auditoria...", expanded=True):
            # 1. Leitura
            st.write("📖 A ler documento principal...")
            txt_main = get_pdf_text(f_main)
            
            txt_extra = ""
            if f_extra:
                st.write(f"📖 A ler {len(f_extra)} anexos...")
                for f in f_extra: txt_extra += get_pdf_text(f) + "\n"
            
            txt_web = ""
            if web_q:
                st.write(f"🌍 A pesquisar: {web_q}...")
                txt_web = search_online(web_q)
            
            # 2. Análise
            st.write(f"🤖 A analisar com **{selected_model}**...")
            res = run_analysis(txt_main, lib_context, txt_extra, txt_web, api_key, selected_model)
            
            # 3. Resultado
            st.success("Concluído!")
            st.markdown("### 📋 Relatório")
            st.markdown(res)
            
            st.download_button(
                "📥 Descarregar Word", 
                create_docx(res), 
                "Relatorio_Ambiente.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )


