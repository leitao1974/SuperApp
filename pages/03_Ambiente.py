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
    # Tenta importar legislacao.py, se não existir usa dicionário vazio
    try:
        import legislacao
    except ImportError:
        legislacao = None
except ImportError as e:
    st.error(f"Erro de configuração: {e}")
    st.stop()

# --- 4. BARRA LATERAL (Base) ---
try:
    utils.sidebar_comum()
except:
    pass

# --- 5. TÍTULO E CHAVE ---
st.title("🌿 Análise Ambiental & Compliance")
st.caption("Auditoria PATE (Protocolo de Avaliação Técnica), Pesquisa Web e Análise Legal.")

# Recuperar a chave da memória
api_key = st.session_state.get("api_key", "")

if not api_key:
    st.warning("⚠️ **Atenção:** API Key não detetada. Por favor insira-a no menu lateral esquerdo.")
    st.stop()

# ==========================================
# --- 6. FUNÇÕES ---
# ==========================================

def get_available_models(key):
    """Lista os modelos disponíveis na API."""
    try:
        genai.configure(api_key=key)
        models = genai.list_models()
        # Filtra apenas modelos que geram texto
        return [m.name for m in models if 'generateContent' in m.supported_generation_methods]
    except:
        return ["models/gemini-2.0-flash", "models/gemini-1.5-flash"] # Fallback

def get_pdf_text(pdf_file):
    """Extrai texto de um ficheiro PDF."""
    text = ""
    try:
        reader = PdfReader(pdf_file)
        for page in reader.pages:
            text += page.extract_text() or ""
    except Exception as e:
        st.error(f"Erro ao ler PDF: {e}")
    return text

def search_online(query):
    """Realiza pesquisa na Web usando DuckDuckGo."""
    if not query: return ""
    results_text = ""
    try:
        with DDGS() as ddgs:
            # Pesquisa focada em legislação portuguesa
            results = list(ddgs.text(f"{query} legislação portugal dre", max_results=3))
        for r in results:
            results_text += f"\n>>> FONTE WEB: {r['title']} ({r['href']}) <<<\n{r['body']}\n"
        return results_text
    except Exception as e:
        return f"Erro na pesquisa web: {str(e)}"

def create_docx(text):
    """Gera ficheiro Word formatado."""
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
    """Executa a análise com o modelo escolhido."""
    genai.configure(api_key=key)
    
    model = genai.GenerativeModel(model_name)
    
    prompt = f"""
    Atua como Auditor Ambiental Sénior (Especialista em Protocolo PATE).
    
    === LEGISLAÇÃO APLICÁVEL (Base de Dados) ===
    {lib_ctx}
    
    === DOCUMENTOS EXTRA (Anexos) ===
    {manual_ctx}
    
    === PESQUISA WEB RECENTE ===
    {web_ctx}
    
    === DOCUMENTO DO PROJETO EM ANÁLISE ===
    {target_text}
    
    TAREFA:
    Realiza uma auditoria de conformidade rigorosa. O relatório deve conter:
    
    ## 1. Enquadramento e Maturidade do Projeto
    (O que é o projeto e em que fase está).
    
    ## 2. Check-up de Conformidade Legal
    (Cruza o texto do projeto com a legislação fornecida. Identifica artigos cumpridos e não cumpridos).
    
    ## 3. Riscos Críticos e Omissões
    (O que falta? O que está mal fundamentado?).
    
    ## 4. Recomendações de Melhoria
    (Ações concretas para o promotor).
    """
    
    try:
        return model.generate_content(prompt).text
    except Exception as e:
        return f"Erro durante a análise IA: {e}"

# ==========================================
# --- 7. INTERFACE ---
# ==========================================

if 'uploader_key' not in st.session_state: st.session_state.uploader_key = 0

# --- A. CONFIGURAÇÕES (Legislação + Modelo) ---

# Seletor de Modelo na Barra Lateral
with st.sidebar:
    st.divider()
    st.markdown("### 🧠 Motor de IA")
    
    opcoes_modelos = get_available_models(api_key)
    
    # Lógica de Prioridade: 2.5 Flash > 2.0 Flash > 1.5 Flash
    targets = ["2.5-flash", "2.0-flash", "1.5-flash", "flash"]
    idx_padrao = 0
    found = False
    
    for t in targets:
        for i, m in enumerate(opcoes_modelos):
            if t in m.lower():
                idx_padrao = i
                found = True
                break
        if found: break
            
    selected_model = st.selectbox(
        "Modelo:", 
        opcoes_modelos, 
        index=idx_padrao,
        help="O sistema seleciona automaticamente o modelo Flash mais recente."
    )

# Área Principal - Legislação
library = legislacao.get_library() if legislacao else {}
lib_context = ""

with st.expander("📚 Base Legislativa (Configuração)", expanded=False):
    st.markdown("**Selecione os diplomas aplicáveis:**")
    if not library:
        st.info("Ficheiro 'legislacao.py' não encontrado ou vazio. A análise será feita apenas com base nos documentos PDF.")
    
    c1, c2 = st.columns(2)
    i = 0
    for cat, laws in library.items():
        with (c1 if i % 2 == 0 else c2):
            st.markdown(f"**{cat}**")
            for name, info in laws.items():
                if st.checkbox(name, key=f"leg_{name}"):
                    # Tenta aceder ao campo 'mandato' ou 'descricao', adaptando-se à estrutura
                    desc = info.get('mandato', info.get('descricao', 'Lei aplicável'))
                    lib_context += f"- {name}: {desc}\n"
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
        "Anexos Legais / PDM (PDF)", 
        type="pdf", 
        accept_multiple_files=True, 
        key=f"extra_doc_{st.session_state.uploader_key}"
    )
    web_q = st.text_input("Pesquisa Web (Ex: 'PDM de Sintra regulamento')", help="Pesquisa no Google/DuckDuckGo para complementar a análise.")

# --- C. BOTÃO DE AÇÃO ---
if st.button("🚀 EXECUTAR AUDITORIA", type="primary", use_container_width=True):
    if not f_main:
        st.warning("⚠️ Carregue o documento principal primeiro.")
    else:
        with st.status("⚙️ A realizar auditoria...", expanded=True):
            
            # 1. Leitura do Principal
            st.write("📖 A ler documento principal...")
            txt_main = get_pdf_text(f_main)
            
            # 2. Leitura dos Extras
            txt_extra = ""
            if f_extra:
                st.write(f"📖 A ler {len(f_extra)} anexos...")
                for f in f_extra: txt_extra += get_pdf_text(f) + "\n"
            
            # 3. Pesquisa Web
            txt_web = ""
            if web_q:
                st.write(f"🌍 A pesquisar na Web: '{web_q}'...")
                txt_web = search_online(web_q)
            
            # 4. Análise IA
            st.write(f"🤖 A analisar com **{selected_model}**...")
            res = run_analysis(txt_main, lib_context, txt_extra, txt_web, api_key, selected_model)
            
            # 5. Apresentação
            st.success("Concluído!")
            st.markdown("### 📋 Relatório de Auditoria")
            st.markdown(res)
            
            # 6. Download
            st.download_button(
                "📥 Descarregar Word", 
                create_docx(res), 
                "Relatorio_Ambiente.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )


