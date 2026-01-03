import sys
import os

# --- 1. LIGAÇÃO AO UTILS (CRÍTICO) ---
# Isto garante que encontramos o ficheiro 'utils.py' na pasta de trás
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(current_dir)
sys.path.insert(0, root_dir)

import streamlit as st
import utils # Importa o nosso gestor de chaves

# --- 2. CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Compliance Ambiental", page_icon="🌿", layout="wide")

# --- 3. CARREGAR BARRA LATERAL ---
# Isto vai mostrar a chave que já inseriu, sem pedir de novo
utils.sidebar_comum()

# --- 4. VERIFICAÇÃO DE SEGURANÇA ---
# Lemos a chave diretamente da memória global
api_key = st.session_state.get("api_key", "")

if not api_key:
    st.error("🛑 **ACESSO BLOQUEADO**: A API Key não foi detetada.")
    st.info("⬅️ Por favor, insira a chave na **barra lateral esquerda** e pressione Enter.")
    st.stop() # Pára o código aqui até haver chave

# ==========================================
# DAQUI PARA BAIXO: O SEU CÓDIGO DA APP
# ==========================================
import google.generativeai as genai
# ... (Resto dos imports e lógica da app ambiente.py) ...

st.title("🌿 Módulo de Ambiente Ativo")
st.write("A chave está a funcionar e pronta a usar!")

# (Cole aqui o resto do seu código original do módulo 3...)
# ... Daqui para baixo continua o seu código normal ...
import streamlit as st
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

# ==========================================
# --- CONFIGURAÇÃO ---
# ==========================================
st.set_page_config(page_title="Análise Caso a Caso", page_icon="⚖️", layout="wide")

# Barra Lateral Comum
try:
    utils.sidebar_comum()
except Exception as e:
    st.error(f"Erro no menu lateral: {e}")

# Recuperar API Key Global
api_key = st.session_state.get("api_key", "")
if api_key:
    genai.configure(api_key=api_key)

# ==========================================
# --- BASE DE DADOS JURÍDICA ---
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

# ==========================================
# --- FUNÇÕES ---
# ==========================================
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
        p = None
        if line.startswith('## '):
            p = doc.add_heading(line.replace('##', '').strip(), level=2)
        elif line.startswith('### '):
            p = doc.add_heading(line.replace('###', '').strip(), level=3)
        elif line.startswith('- ') or line.startswith('* '):
            p = doc.add_paragraph(style='List Bullet')
            clean_line = line[2:]
            process_bold(p, clean_line)
            p.paragraph_format.space_after = Pt(6) 
        else:
            p = doc.add_paragraph()
            process_bold(p, line)
            p.paragraph_format.space_after = Pt(10)
        if p and not line.startswith('#'):
            p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY

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
    doc.add_heading("Legislação Consultada e Referências", level=1)
    p = doc.add_paragraph("A presente análise teve por base os seguintes diplomas legais:")
    for name, url in LEGISLATION_DB.items():
        p = doc.add_paragraph(style='List Bullet')
        add_hyperlink(p, name, url)

def extract_text(files, label):
    text = ""
    if not files: return "" 
    for f in files:
        try:
            f.seek(0)
            bytes_data = f.read()
            f_stream = io.BytesIO(bytes_data)
            r = PdfReader(f_stream)
            if r.is_encrypted:
                try: r.decrypt("") 
                except: pass
            file_text = ""
            for i, p in enumerate(r.pages):
                extracted = p.extract_text()
                if extracted:
                    file_text += f"[Pág. {i+1}] {extracted}\n"
            text += f"\n\n>>> FONTE: {label} ({f.name}) <<<\n{file_text}"
        except Exception as e:
            st.error(f"Erro ao ler '{f.name}': {str(e)}")
    return text

def analyze_validation(t_sim, t_form, t_proj, t_leg):
    legislacao_str = ", ".join(LEGISLATION_DB.keys())
    model = genai.GenerativeModel("gemini-1.5-flash")
    return model.generate_content(f"""
    Atua como PERITO AUDITOR AMBIENTAL rigoroso.
    CONTEXTO LEGAL: {legislacao_str}.
    Contexto Local: {t_leg[:30000]}
    DADOS: {t_sim[:25000]} {t_form[:25000]} {t_proj[:80000]}
    TAREFA: Audita a consistência, valida limiares RJAIA e cruza com PDM.
    OUTPUT: Markdown estruturado (##, ###, -).
    """).text

def generate_decision_text(t_sim, t_form, t_proj, t_leg):
    model = genai.GenerativeModel("gemini-1.5-flash")
    return model.generate_content(f"""
    Atua como Técnico Superior da Autoridade de AIA. Redige a MINUTA DE DECISÃO.
    DADOS: {t_proj[:120000]} {t_form[:25000]} Legislação Local: {t_leg[:40000]}
    OUTPUT: Preencher tags ### CAMPO_... (Designacao, Tipologia, Enquadramento, Decisao).
    """).text

def create_validation_doc(text):
    doc = Document()
    doc.add_heading("Auditoria Técnica", 0)
    markdown_to_word(doc, text)
    append_legislation_section(doc)
    bio = io.BytesIO()
    doc.save(bio)
    return bio

def create_decision_doc(text):
    doc = Document()
    doc.add_heading("Minuta de Decisão", 0)
    markdown_to_word(doc, text)
    bio = io.BytesIO()
    doc.save(bio)
    return bio

# --- UI ---
st.title("⚖️ Análise Caso a Caso (RJAIA)")
col1, col2, col3, col4 = st.columns(4)
with col1: files_sim = st.file_uploader("📂 Simulação SILiAmb", type=['pdf'], accept_multiple_files=True, key=f"s_{st.session_state.uploader_key}")
with col2: files_form = st.file_uploader("📂 Formulário", type=['pdf'], accept_multiple_files=True, key=f"f_{st.session_state.uploader_key}")
with col3: files_doc = st.file_uploader("📂 Projeto/Memória", type=['pdf'], accept_multiple_files=True, key=f"p_{st.session_state.uploader_key}")
with col4: files_leg = st.file_uploader("📜 Legislação Local", type=['pdf'], accept_multiple_files=True, key=f"l_{st.session_state.uploader_key}")

st.markdown("---")

if st.button("🚀 Processar", type="primary"):
    if not (files_sim and files_form and files_doc):
        st.error("Carregue os ficheiros necessários.")
    elif not api_key:
        st.error("API Key em falta (Menu Lateral).")
    else:
        with st.status("⚙️ A processar...", expanded=True):
            ts = extract_text(files_sim, "SIM")
            tf = extract_text(files_form, "FORM")
            tp = extract_text(files_doc, "PROJ")
            tl = extract_text(files_leg, "LOCAL") if files_leg else "N/A"
            st.write("🕵️ Auditoria...")
            val = analyze_validation(ts, tf, tp, tl)
            st.session_state.validation_result = val
            st.write("⚖️ Decisão...")
            dec = generate_decision_text(ts, tf, tp, tl)
            st.session_state.decision_result = dec

if st.session_state.validation_result:
    c1, c2 = st.columns(2)
    f_val = create_validation_doc(st.session_state.validation_result)
    c1.download_button("📄 Relatório Auditoria", f_val.getvalue(), "Auditoria.docx")
    f_dec = create_decision_doc(st.session_state.decision_result)

    c2.download_button("📝 Minuta Decisão", f_dec.getvalue(), "Decisao.docx", type="primary")

