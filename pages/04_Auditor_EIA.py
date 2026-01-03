import sys
import os

# --- CAMINHOS ---
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(current_dir)
sys.path.insert(0, root_dir)

import utils
import streamlit as st
from pypdf import PdfWriter, PdfReader
from docx import Document
from docx.shared import Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
import google.generativeai as genai
from google.api_core.exceptions import ResourceExhausted
import io
import time
import tempfile
import re
from datetime import datetime

# --- CONFIGURAÇÃO ---
st.set_page_config(page_title="Auditor EIA Pro", page_icon="⚖️", layout="wide")

# Menu Lateral
try:
    utils.sidebar_comum()
except:
    pass

st.title("⚖️ Auditor EIA Pro (File API)")
st.info("ℹ️ Utilize este módulo para Processos EIA completos (Tomo I, RNT, Anexos). Suporta ficheiros > 200 páginas via Cloud.")

# Recuperar API Key
api_key = st.session_state.get("api_key", "")
if not api_key:
    st.warning("⚠️ Configure a API Key no menu lateral.")

# ==========================================
# --- BASE DE DADOS LEGISLATIVA INTERNA ---
# ==========================================
COMMON_LAWS = {
    "RJAIA (DL 151-B/2013)": "https://diariodarepublica.pt/dr/legislacao-consolidada/decreto-lei/2013-116043164",
    "SIMPLEX (DL 11/2023)": "https://diariodarepublica.pt/dr/detalhe/decreto-lei/11-2023-207604364",
    "REDE NATURA 2000 (DL 140/99)": "https://diariodarepublica.pt/dr/legislacao-consolidada/decreto-lei/1999-34460975",
    "REG. RUÍDO (DL 9/2007)": "https://diariodarepublica.pt/dr/legislacao-consolidada/decreto-lei/2007-34526556",
    "LEI DA ÁGUA (Lei 58/2005)": "https://diariodarepublica.pt/dr/legislacao-consolidada/lei/2005-34563267"
}

SPECIFIC_LAWS = {
    "Indústria Extrativa": {"DL 270/2001 (Massas Minerais)": "#"},
    "Energia (Renováveis)": {"DL 15/2022 (Sistema Elétrico)": "#"},
    "Indústria/Química": {"DL 127/2013 (Emissões)": "#"},
    "Infraestruturas": {"Lei 34/2015 (Estradas)": "#"},
    "Outra Tipologia": {}
}

# ==========================================
# --- FUNÇÕES ---
# ==========================================

def extract_text_from_pdfs_local(files):
    text = ""
    for f in files:
        try:
            reader = PdfReader(f)
            text += f"\n>>> DIPLOMA EXTRA: {f.name} <<<\n"
            for page in reader.pages:
                text += page.extract_text() + "\n"
        except Exception as e:
            text += f"\n[ERRO {f.name}: {str(e)}]\n"
    return text

def merge_pdfs_to_temp(uploaded_files):
    merger = PdfWriter()
    for uploaded_file in uploaded_files:
        merger.append(uploaded_file)
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        merger.write(tmp)
        tmp_path = tmp.name
    return tmp_path

def analyze_large_document(merged_pdf_path, laws_str, extra_laws_text, prompt_instructions, key):
    genai.configure(api_key=key)
    status_msg = st.empty()
    status_msg.info("📤 A enviar processo EIA para a Google Cloud (File API)...")
    
    processo_file = None
    try:
        processo_file = genai.upload_file(path=merged_pdf_path, display_name="EIA Process")
        
        status_msg.info("⚙️ A Google está a processar o PDF...")
        while processo_file.state.name == "PROCESSING":
            time.sleep(2)
            processo_file = genai.get_file(processo_file.name)
        
        if processo_file.state.name == "FAILED":
            raise ValueError("Falha na leitura do PDF pela Google.")
        
        status_msg.success("✅ Processamento concluído. A iniciar análise jurídica...")

        model = genai.GenerativeModel("gemini-1.5-flash")
        
        full_prompt = [
            prompt_instructions,
            "\n=== QUADRO LEGISLATIVO ===\n",
            laws_str,
            "\n=== LEGISLAÇÃO EXTRA ===\n",
            extra_laws_text,
            "\n=== INSTRUÇÃO ===\n",
            "Analisa o PDF anexo face a esta legislação.",
            processo_file
        ]

        response = model.generate_content(full_prompt)
        status_msg.empty()
        return response.text

    except ResourceExhausted:
        return "🚨 ERRO DE COTA: Atingiste o limite da API da Google."
    except Exception as e:
        return f"❌ Erro Técnico: {str(e)}"
    finally:
        if processo_file:
            try: genai.delete_file(processo_file.name)
            except: pass

def clean_markdown(text):
    return text.replace('**', '').strip()

def create_professional_doc(content, project_type, active_laws_dict, extra_files_names):
    doc = Document()
    style_normal = doc.styles['Normal']
    style_normal.font.name = 'Calibri'
    style_normal.font.size = Pt(11)
    
    title = doc.add_heading('AUDITORIA DE CONFORMIDADE EIA', 0)
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    doc.add_paragraph(f'Setor: {project_type}').alignment = WD_ALIGN_PARAGRAPH.CENTER
    doc.add_paragraph(f'Data: {datetime.now().strftime("%d/%m/%Y")}').alignment = WD_ALIGN_PARAGRAPH.CENTER
    doc.add_paragraph('---')

    for line in content.split('\n'):
        line = line.strip()
        if not line: continue
        if line.startswith('## '):
            clean = clean_markdown(line.replace('## ', ''))
            h = doc.add_heading(clean.upper(), level=1)
            h.style.font.color.rgb = RGBColor(14, 77, 164)
        elif line.startswith('### '):
            clean = clean_markdown(line.replace('### ', ''))
            doc.add_heading(clean, level=2)
        elif line.startswith('- ') or line.startswith('* '):
            doc.add_paragraph(line[2:], style='List Bullet')
        else:
            doc.add_paragraph(line)

    doc.add_page_break()
    doc.add_heading('ANEXO: LEGISLAÇÃO', level=1)
    for name in active_laws_dict.keys():
        doc.add_paragraph(name, style='List Bullet')
        
    bio = io.BytesIO()
    doc.save(bio)
    return bio

# --- UI LATERAL ESPECÍFICA ---
# Usamos st.sidebar APÓS o utils.sidebar_comum, ele adiciona abaixo.
with st.sidebar:
    st.markdown("---")
    st.header("Configuração EIA")
    project_type = st.selectbox("Setor RJAIA:", list(SPECIFIC_LAWS.keys()) + ["Outra Tipologia"])
    
    active_laws = COMMON_LAWS.copy()
    if project_type in SPECIFIC_LAWS:
        active_laws.update(SPECIFIC_LAWS[project_type])
    
    with st.expander(f"📚 Base Legislativa ({len(active_laws)})"):
        for k, v in active_laws.items(): st.markdown(f"- {k}")
            
    extra_laws_files = st.file_uploader("Leis Extra (PDFs)", type=['pdf'], accept_multiple_files=True)

# --- UI CENTRAL ---
uploaded_files = st.file_uploader(
    "📂 Carregar Processo EIA (Tomo I, Anexos, etc.)", 
    type=['pdf'], 
    accept_multiple_files=True
)

instructions = f"""
Atua como Perito Sénior em Engenharia do Ambiente.
Auditoria de conformidade rigorosa ao EIA do setor: {project_type}.

ESTRUTURA OBRIGATÓRIA (Markdown ##):
## 1. ENQUADRAMENTO LEGAL
## 2. PRINCIPAIS IMPACTES (Por descritor)
## 3. MEDIDAS DE MITIGAÇÃO
## 4. ANÁLISE CRÍTICA (Lacunas?)
## 5. FUNDAMENTAÇÃO (Cita páginas do PDF)
## 6. CONCLUSÕES TÉCNICAS

Não emitir parecer administrativo ("Favorável"), mas sim técnico ("Robusto/Insuficiente").
"""

if st.button("🚀 INICIAR AUDITORIA", type="primary"):
    if not api_key: st.error("Falta API Key.")
    elif not uploaded_files: st.warning("Faltam ficheiros.")
    else:
        with st.spinner("A preparar ficheiros e analisar..."):
            # 1. Leis
            laws_str = "\n".join([f"- {k}" for k in active_laws.keys()])
            extra_text = extract_text_from_pdfs_local(extra_laws_files) if extra_laws_files else ""
            
            # 2. Merge & Analyze
            temp_path = merge_pdfs_to_temp(uploaded_files)
            
            result_text = analyze_large_document(
                temp_path, 
                laws_str, 
                extra_text, 
                instructions, 
                api_key
            )
            
            try: os.remove(temp_path)
            except: pass
            
            if "🚨" in result_text or "❌" in result_text:
                st.error(result_text)
            else:
                st.success("Concluído!")
                st.markdown(result_text)
                
                docx = create_professional_doc(result_text, project_type, active_laws, [])

                st.download_button("⬇️ Download Word", docx.getvalue(), "Auditoria_EIA.docx", "application/vnd.openxmlformats-officedocument.wordprocessingml.document")

