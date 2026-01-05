import sys
import os
import re

# --- 1. CONFIGURAÇÃO DE CAMINHOS ---
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(current_dir)
sys.path.insert(0, root_dir)

import streamlit as st
import google.generativeai as genai
from pypdf import PdfReader
from docx import Document
from docx.shared import Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH  # Import necessário para justificar
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
st.markdown("""
**Auditoria PATE (Protocolo de Avaliação Técnica) Fundamentada.**
Gera relatórios de conformidade com citação de páginas e transcrição de evidências.
""")

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
        return [m.name for m in models if 'generateContent' in m.supported_generation_methods]
    except:
        return ["models/gemini-2.0-flash", "models/gemini-1.5-flash"]

def get_pdf_text_with_pages(pdf_file, simple_citation=False):
    """
    Extrai texto inserindo marcadores de página.
    Args:
        simple_citation (bool): Se True, usa apenas [PÁG. X]. Se False, usa [DOC: Nome | PÁG. X].
    """
    text = ""
    try:
        reader = PdfReader(pdf_file)
        doc_name = pdf_file.name
        
        text += f"\n\n=== INÍCIO DO DOCUMENTO: {doc_name} ===\n"
        
        for i, page in enumerate(reader.pages):
            content = page.extract_text() or "[Página em branco ou imagem]"
            
            # Lógica de citação condicional
            if simple_citation:
                tag = f"[PÁG. {i+1}]"
            else:
                tag = f"[DOC: {doc_name} | PÁG. {i+1}]"
            
            text += f"\n{tag}\n{content}\n"
        
        text += f"=== FIM DO DOCUMENTO: {doc_name} ===\n"
        
    except Exception as e:
        st.error(f"Erro ao ler PDF {pdf_file.name}: {e}")
    return text

def search_online(query):
    """Realiza pesquisa na Web usando DuckDuckGo."""
    if not query: return ""
    results_text = ""
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(f"{query} legislação portugal dre", max_results=3))
        for r in results:
            results_text += f"\n>>> FONTE WEB: {r['title']} ({r['href']}) <<<\n{r['body']}\n"
        return results_text
    except Exception as e:
        return f"Erro na pesquisa web: {str(e)}"

def create_docx(text):
    """Gera ficheiro Word formatado e justificado."""
    doc = Document()
    
    title = doc.add_heading('Relatório de Auditoria Ambiental Fundamentado', 0)
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    doc.add_paragraph(f"Data: {time.strftime('%d/%m/%Y')}")
    doc.add_paragraph("---")
    
    for line in text.split('\n'):
        line = line.strip()
        if not line: continue
        
        # Limpa asteriscos que a IA possa colocar nos títulos (ex: ## **Título**)
        clean_line = line.replace('**', '')
        
        if line.startswith('## '): 
            # Remove o markdown '## ' e aplica estilo
            h_text = clean_line.replace('## ', '')
            h = doc.add_heading(h_text, level=1)
            h.style.font.color.rgb = RGBColor(0, 100, 0) # Verde escuro
            
        elif line.startswith('### '): 
            h_text = clean_line.replace('### ', '')
            doc.add_heading(h_text, level=2)
            
        elif line.startswith('- ') or line.startswith('* '): 
            p = doc.add_paragraph(style='List Bullet')
            p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY # Justificar Bullet Points
            
            # Processa citações para negrito/cinza
            parts = re.split(r'(\[.*?PÁG.*?\])', line[2:])
            for part in parts:
                run = p.add_run(part)
                if "[" in part and "PÁG" in part:
                    run.bold = True
                    run.font.size = Pt(9)
                    run.font.color.rgb = RGBColor(100, 100, 100) # Cinza
                    
        elif line.startswith('>'): 
            p = doc.add_paragraph(style='Intense Quote')
            p.add_run(line.replace('>', '').strip()).italic = True
            p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
            
        else: 
            # Parágrafos normais
            p = doc.add_paragraph(line)
            p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY # Justificar Texto Normal
            
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
    
    === LEGISLAÇÃO APLICÁVEL (Contexto Legal) ===
    {lib_ctx}
    
    === DOCUMENTOS EXTRA / ANEXOS (Com paginação) ===
    {manual_ctx}
    
    === PESQUISA WEB RECENTE ===
    {web_ctx}
    
    === DOCUMENTO DO PROJETO EM ANÁLISE (Com paginação) ===
    {target_text}
    
    TAREFA:
    Realiza uma auditoria de conformidade rigorosa e FUNDAMENTADA.
    
    REGRAS DE FUNDAMENTAÇÃO (OBRIGATÓRIO):
    1. **Cita a Fonte:** Sempre que afirmares algo sobre o projeto, indica a página conforme fornecido no texto (ex: [PÁG. X] ou [DOC: Y | PÁG. X]).
    2. **Transcreve Evidências:** Usa aspas para citar frases do texto original que provem a conformidade ou o erro.
    
    ESTRUTURA DO RELATÓRIO:
    
    ## 1. Enquadramento e Maturidade
    (Resumo do projeto citando a Memória Descritiva).
    
    ## 2. Check-up de Conformidade Legal
    (Cruza o projeto com a legislação fornecida. Cita artigos da lei e páginas do projeto).
    - [Diploma Legal]: [Cumpre/Não Cumpre] -> Evidência: "..." [PÁG. X].
    
    ## 3. Riscos Críticos e Omissões
    (O que falta? O que está mal fundamentado? Cita onde procuraste e não encontraste).
    
    ## 4. Conclusões e Recomendações de Melhoria
    (Síntese final e ações concretas para mitigar os riscos).
    """
    
    try:
        return model.generate_content(prompt, request_options={"timeout": 600}).text
    except Exception as e:
        return f"Erro durante a análise IA: {e}"

# ==========================================
# --- 7. INTERFACE ---
# ==========================================

if 'uploader_key' not in st.session_state: st.session_state.uploader_key = 0

# --- A. CONFIGURAÇÕES ---
with st.sidebar:
    st.divider()
    st.markdown("### 🧠 Motor de IA")
    opcoes_modelos = get_available_models(api_key)
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
            
    selected_model = st.selectbox("Modelo:", opcoes_modelos, index=idx_padrao)

library = legislacao.get_library() if legislacao else {}
lib_context = ""

with st.expander("📚 Base Legislativa (Configuração)", expanded=False):
    st.markdown("**Selecione os diplomas aplicáveis:**")
    if not library:
        st.info("Ficheiro 'legislacao.py' não encontrado ou vazio.")
    
    c1, c2 = st.columns(2)
    i = 0
    for cat, laws in library.items():
        with (c1 if i % 2 == 0 else c2):
            st.markdown(f"**{cat}**")
            for name, info in laws.items():
                if st.checkbox(name, key=f"leg_{name}"):
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
    web_q = st.text_input("Pesquisa Web", help="Ex: 'PDM de Sintra regulamento'")

# --- C. BOTÃO DE AÇÃO ---
if st.button("🚀 EXECUTAR AUDITORIA FUNDAMENTADA", type="primary", use_container_width=True):
    if not f_main:
        st.warning("⚠️ Carregue o documento principal primeiro.")
    else:
        with st.status("⚙️ A realizar auditoria...", expanded=True):
            
            # Verifica se existem múltiplos ficheiros para decidir formato da citação
            multiple_files = True if f_extra else False
            
            # 1. Leitura do Principal
            st.write("📖 A indexar páginas do documento principal...")
            # Se não houver extras, usa citação simples [PÁG. X]
            txt_main = get_pdf_text_with_pages(f_main, simple_citation=not multiple_files)
            
            # 2. Leitura dos Extras
            txt_extra = ""
            if f_extra:
                st.write(f"📖 A indexar {len(f_extra)} anexos...")
                for f in f_extra: 
                    # Extras têm sempre nome do documento [DOC: Nome | PÁG. X]
                    txt_extra += get_pdf_text_with_pages(f, simple_citation=False) + "\n"
            
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
                "📥 Descarregar Word Fundamentado", 
                create_docx(res), 
                "Relatorio_Ambiente_Fundamentado.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )
