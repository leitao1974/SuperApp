import sys
import os

# --- 1. CONFIGURAÇÃO DE CAMINHOS ---
# Isto garante que a página encontra o ficheiro utils.py na pasta raiz
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(current_dir)
sys.path.insert(0, root_dir)

import streamlit as st

# --- 2. CONFIGURAÇÃO DA PÁGINA (Deve ser a primeira instrução 'st') ---
st.set_page_config(
    page_title="Análise Caso a Caso",
    page_icon="⚖️",
    layout="wide"
)

# --- 3. IMPORTS GERAIS ---
try:
    import utils # O nosso gestor de menu e chaves
except ImportError as e:
    st.error(f"Erro ao importar 'utils.py'. Verifique se o ficheiro está na pasta raiz. Detalhe: {e}")
    st.stop()

from pypdf import PdfReader
from docx import Document
from docx.shared import Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
import google.generativeai as genai
import io
import re
from datetime import datetime

# --- 4. CARREGAR BARRA LATERAL (Uma única vez!) ---
utils.sidebar_comum()

# --- 5. RECUPERAR CHAVE DA MEMÓRIA ---
api_key = st.session_state.get("api_key", "")

# --- TÍTULO ---
st.title("⚖️ Análise Caso a Caso (RJAIA)")
st.markdown("### Auditoria Técnica e Decisão Fundamentada")

if not api_key:
    st.warning("⚠️ **Atenção:** A API Key não foi detetada. Por favor insira-a na barra lateral esquerda.")
    # Não usamos st.stop() aqui para permitir ver a interface, mas os botões falharão

# ==========================================
# --- 6. LÓGICA ESPECÍFICA DESTA APP ---
# ==========================================

LEGISLATION_DB = {
    "RJAIA (DL 151-B/2013)": "https://diariodarepublica.pt/dr/legislacao-consolidada/decreto-lei/2013-116043164",
    "Alteração RJAIA (DL 152-B/2017)": "https://diariodarepublica.pt/dr/detalhe/decreto-lei/152-b-2017-114337069",
    "RGGR (DL 102-D/2020)": "https://diariodarepublica.pt/dr/legislacao-consolidada/decreto-lei/2020-150917243",
    "LUA (DL 75/2015)": "https://diariodarepublica.pt/dr/legislacao-consolidada/decreto-lei/2015-106562356",
    "Rede Natura 2000 (DL 140/99)": "https://diariodarepublica.pt/dr/legislacao-consolidada/decreto-lei/1999-34460975",
    "Regulamento Geral do Ruído (DL 9/2007)": "https://diariodarepublica.pt/dr/legislacao-consolidada/decreto-lei/2007-34526556",
    "Lei da Água (Lei 58/2005)": "https://diariodarepublica.pt/dr/legislacao-consolidada/lei/2005-34563267",
    "Emissões Industriais (DL 127/2013)": "https://diariodarepublica.pt/dr/legislacao-consolidada/decreto-lei/2013-34789569"
}

if 'uploader_key' not in st.session_state: st.session_state.uploader_key = 0
if 'validation_result' not in st.session_state: st.session_state.validation_result = None
if 'decision_result' not in st.session_state: st.session_state.decision_result = None

def reset_app():
    st.session_state.uploader_key += 1
    st.session_state.validation_result = None
    st.session_state.decision_result = None
    st.rerun()

# --- Funções Auxiliares (Word/PDF/IA) ---
def add_hyperlink(paragraph, text, url):
    part = paragraph.part
    r_id = part.relate_to(url, "http://schemas.openxmlformats.org/officeDocument/2006/relationships/hyperlink", is_external=True)
    hyperlink = OxmlElement("w:hyperlink")
    hyperlink.set(qn("r:id"), r_id)
    new_run = OxmlElement("w:r")
    rPr = OxmlElement("w:rPr")
    c = OxmlElement("w:color")
    c.set(qn("w:val"), "0000FF")
    rPr.append(c)
    u = OxmlElement("w:u")
    u.set(qn("w:val"), "single")
    rPr.append(u)
    new_run.append(rPr)
    new_run.text = text
    hyperlink.append(new_run)
    paragraph._p.append(hyperlink)

def markdown_to_word(doc, text):
    if not text: return
    lines = text.split('\n')
    for line in lines:
        line = line.strip()
        if not line: continue
        if line.startswith('## '):
            doc.add_heading(line.replace('##', '').strip(), level=2)
        elif line.startswith('### '):
            doc.add_heading(line.replace('###', '').strip(), level=3)
        elif line.startswith('- ') or line.startswith('* '):
            p = doc.add_paragraph(style='List Bullet')
            process_bold(p, line[2:])
        else:
            p = doc.add_paragraph()
            process_bold(p, line)

def process_bold(paragraph, text):
    parts = re.split(r'(\*\*.*?\*\*)', text)
    for part in parts:
        if part.startswith('**') and part.endswith('**'):
            run = paragraph.add_run(part[2:-2])
            run.bold = True
        else:
            paragraph.add_run(part)

def append_legislation_section(doc):
    doc.add_page_break()
    doc.add_heading("Legislação Consultada", level=1)
    for name, url in LEGISLATION_DB.items():
        p = doc.add_paragraph(style='List Bullet')
        add_hyperlink(p, name, url)

def extract_text(files, label):
    text = ""
    if not files: return "" 
    for f in files:
        try:
            reader = PdfReader(f)
            file_text = ""
            for page in reader.pages:
                file_text += page.extract_text() or ""
            text += f"\n\n>>> FONTE: {label} ({f.name}) <<<\n{file_text}"
        except Exception as e:
            st.error(f"Erro ao ler '{f.name}': {e}")
    return text

def analyze_validation(t_sim, t_form, t_proj, t_leg, key):
    genai.configure(api_key=key)
    model = genai.GenerativeModel("gemini-1.5-flash")
    prompt = f"""
    Atua como Auditor Ambiental. Contexto Legal: {", ".join(LEGISLATION_DB.keys())}.
    Contexto Local: {t_leg[:20000]}
    DADOS: {t_sim[:20000]} {t_form[:20000]} {t_proj[:60000]}
    TAREFA: Audita a consistência e valida limiares RJAIA.
    OUTPUT: Markdown estruturado (##, -, **).
    """
    return model.generate_content(prompt).text

def generate_decision_text(t_sim, t_form, t_proj, t_leg, key):
    genai.configure(api_key=key)
    model = genai.GenerativeModel("gemini-1.5-flash")
    prompt = f"""
    Redige MINUTA DE DECISÃO (Técnico Superior).
    DADOS: {t_proj[:80000]} {t_form[:20000]}
    OUTPUT: Preencher tags ### CAMPO_... (Designacao, Tipologia, Enquadramento, Decisao).
    """
    return model.generate_content(prompt).text

def create_doc_from_text(text, title):
    doc = Document()
    doc.add_heading(title, 0)
    markdown_to_word(doc, text)
    if "Auditoria" in title: append_legislation_section(doc)
    bio = io.BytesIO()
    doc.save(bio)
    return bio

# --- INTERFACE ---
col1, col2, col3, col4 = st.columns(4)
with col1: files_sim = st.file_uploader("📂 Simulação SILiAmb", type=['pdf'], accept_multiple_files=True, key=f"s_{st.session_state.uploader_key}")
with col2: files_form = st.file_uploader("📂 Formulário", type=['pdf'], accept_multiple_files=True, key=f"f_{st.session_state.uploader_key}")
with col3: files_doc = st.file_uploader("📂 Projeto/Memória", type=['pdf'], accept_multiple_files=True, key=f"p_{st.session_state.uploader_key}")
with col4: files_leg = st.file_uploader("📜 Legislação Local", type=['pdf'], accept_multiple_files=True, key=f"l_{st.session_state.uploader_key}")

st.markdown("---")

if st.button("🚀 Processar", type="primary", use_container_width=True):
    if not (files_sim and files_form and files_doc):
        st.error("⚠️ Faltam ficheiros obrigatórios (Simulação, Formulário e Projeto).")
    elif not api_key:
        st.error("🛑 API Key em falta. Insira-a no menu lateral.")
    else:
        with st.status("⚙️ A processar...", expanded=True):
            st.write("📖 A ler documentos...")
            ts = extract_text(files_sim, "SIM")
            tf = extract_text(files_form, "FORM")
            tp = extract_text(files_doc, "PROJ")
            tl = extract_text(files_leg, "LOCAL") if files_leg else "N/A"
            
            st.write("🕵️ A realizar Auditoria Técnica...")
            try:
                val = analyze_validation(ts, tf, tp, tl, api_key)
                st.session_state.validation_result = val
                
                st.write("⚖️ A redigir Minuta de Decisão...")
                dec = generate_decision_text(ts, tf, tp, tl, api_key)
                st.session_state.decision_result = dec
                
            except Exception as e:
                st.error(f"Erro na IA: {e}")

if st.session_state.validation_result:
    st.success("Processo concluído!")
    c1, c2 = st.columns(2)
    
    # Botão 1: Auditoria
    f_val = create_doc_from_text(st.session_state.validation_result, "Relatório de Auditoria Técnica")
    c1.download_button("📄 Descarregar Auditoria (.docx)", f_val.getvalue(), "Auditoria.docx", "application/vnd.openxmlformats-officedocument.wordprocessingml.document")
    
    # Botão 2: Decisão
    f_dec = create_doc_from_text(st.session_state.decision_result, "Minuta de Decisão")
    c2.download_button("📝 Descarregar Decisão (.docx)", f_dec.getvalue(), "Decisao.docx", "application/vnd.openxmlformats-officedocument.wordprocessingml.document", type="primary")
    
    if st.button("🔄 Limpar e Começar de Novo"):
        reset_app()


