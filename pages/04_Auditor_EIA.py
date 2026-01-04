import sys
import os

# --- 1. CONFIGURAÇÃO DE CAMINHOS ---
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(current_dir)
sys.path.insert(0, root_dir)

import utils
import streamlit as st
from pypdf import PdfWriter
from docx import Document
from docx.shared import Pt, RGBColor
import google.generativeai as genai
import io
import time
import tempfile

# --- 2. CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="Auditor EIA Pro", 
    page_icon="⚖️", 
    layout="wide"
)

# --- 3. BARRA LATERAL (Base) ---
try:
    utils.sidebar_comum()
except:
    pass

# --- 4. TÍTULO E ENQUADRAMENTO ---
st.title("⚖️ Auditor EIA Pro (File API)")
st.markdown("""
**Análise Técnica de Processos de Avaliação de Impacte Ambiental.**
Este módulo suporta processos volumosos (Tomo I, RNT, Anexos) enviando-os temporariamente para a Cloud da Google para análise profunda.
""")

# Recuperar API Key
api_key = st.session_state.get("api_key", "")
if not api_key:
    st.warning("⚠️ **Atenção:** API Key não detetada. Por favor insira-a no menu lateral esquerdo.")
    st.stop()

# ==========================================
# --- 5. SELETOR DE MODELO (DINÂMICO) ---
# ==========================================

def get_available_models(key):
    """Lista modelos disponíveis na API."""
    try:
        genai.configure(api_key=key)
        return [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
    except:
        return ["models/gemini-2.0-flash", "models/gemini-1.5-flash"]

with st.sidebar:
    st.divider()
    st.markdown("### 🧠 Motor de IA")
    
    opcoes_modelos = get_available_models(api_key)
    
    # Lógica de Prioridade: 2.5 Flash > 2.0 Flash > 1.5 Flash > Qualquer Flash
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
        help="A IA analisa documentos grandes. O modelo Flash é recomendado pela rapidez e capacidade de contexto."
    )

# ==========================================
# --- 6. FUNÇÕES AUXILIARES ---
# ==========================================

def merge_pdfs_to_temp(uploaded_files):
    """
    Combina múltiplos ficheiros PDF num único ficheiro temporário.
    Essencial para enviar Tomo I + Anexos como um só contexto.
    """
    merger = PdfWriter()
    for uploaded_file in uploaded_files:
        merger.append(uploaded_file)
    
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        merger.write(tmp)
        tmp_path = tmp.name
    
    return tmp_path

def analyze_large_document(merged_pdf_path, prompt, key, model_name):
    """
    1. Faz Upload para a Google File API.
    2. Espera o processamento.
    3. Gera a análise.
    4. Apaga o ficheiro da cloud.
    """
    genai.configure(api_key=key)
    
    status_msg = st.empty()
    status_msg.info("📤 A enviar processo EIA para a Google Cloud (File API)...")
    
    processo_file = None
    try:
        # 1. Upload
        processo_file = genai.upload_file(path=merged_pdf_path, display_name="EIA Process")
        
        # 2. Polling (Espera ativa)
        status_msg.info("⚙️ A Google está a indexar o documento (isto pode demorar 10-20s)...")
        while processo_file.state.name == "PROCESSING":
            time.sleep(2)
            processo_file = genai.get_file(processo_file.name)
        
        if processo_file.state.name == "FAILED":
            raise ValueError("A Google não conseguiu processar o PDF (formato inválido ou protegido).")
            
        status_msg.success(f"✅ Documento indexado. A iniciar análise com **{model_name}**...")

        # 3. Geração
        model = genai.GenerativeModel(model_name)
        
        # Timeout aumentado para 600s para garantir que não corta a análise
        response = model.generate_content(
            [prompt, processo_file], 
            request_options={"timeout": 600}
        )
        
        status_msg.empty()
        return response.text

    finally:
        # 4. Limpeza (Apagar ficheiro da Cloud)
        if processo_file:
            try: 
                genai.delete_file(processo_file.name)
            except: 
                pass

def create_docx(text):
    """Gera um relatório Word formatado."""
    doc = Document()
    
    title = doc.add_heading('Relatório de Auditoria Técnica EIA', 0)
    title.alignment = 1
    doc.add_paragraph(f"Data: {time.strftime('%d/%m/%Y')}")
    doc.add_paragraph("---")
    
    for line in text.split('\n'):
        line = line.strip()
        if not line: continue
        
        if line.startswith('## '): 
            h = doc.add_heading(line.replace('##', '').strip(), 1)
            h.style.font.color.rgb = RGBColor(0, 51, 102)
        elif line.startswith('### '): 
            doc.add_heading(line.replace('###', '').strip(), 2)
        elif line.startswith('- ') or line.startswith('* '): 
            doc.add_paragraph(line[2:], style='List Bullet')
        else: 
            doc.add_paragraph(line)
            
    b = io.BytesIO()
    doc.save(b)
    b.seek(0)
    return b

# ==========================================
# --- 7. INTERFACE ---
# ==========================================

# --- Upload ---
uploaded_files = st.file_uploader(
    "Carregar Processo EIA (Tomo I, RNT, Anexos)", 
    type=['pdf'], 
    accept_multiple_files=True,
    help="Pode carregar vários ficheiros. O sistema vai juntá-los e analisá-los como um todo."
)

# --- Instruções para a IA ---
instructions = """
Atua como Perito Auditor de Avaliação de Impacte Ambiental (Engenheiro do Ambiente Sénior).
Realiza uma auditoria técnica detalhada e crítica ao documento fornecido.

ESTRUTURA OBRIGATÓRIA DO RELATÓRIO:

## 1. ENQUADRAMENTO LEGAL E ADMINISTRATIVO
(Verifica a tipologia do projeto, localização, PDM e conformidade com o RJAIA).

## 2. CARATERIZAÇÃO DOS IMPACTES (Factores Ambientais)
(Analisa a qualidade da avaliação nos descritores: Ar, Ruído, Recursos Hídricos, Biodiversidade, Solos, Paisagem).
- Identifica se a avaliação está bem fundamentada.

## 3. MEDIDAS DE MITIGAÇÃO
(Lista as medidas propostas e critica a sua eficácia. São vagas? São concretas? Faltam medidas?).

## 4. ANÁLISE CRÍTICA E LACUNAS
(Identifica erros técnicos, dados em falta, má fundamentação ou omissões graves que impeçam a decisão).

## 5. CONCLUSÕES TÉCNICAS
(Parecer técnico fundamentado: O EIA é robusto o suficiente para uma decisão favorável ou precisa de Título Adicional?).
"""

# --- Botão de Ação ---
if st.button("🚀 INICIAR AUDITORIA EIA", type="primary", use_container_width=True):
    if not uploaded_files:
        st.error("⚠️ Faltam ficheiros. Por favor carregue o Processo EIA.")
    else:
        # Spinner visual
        with st.status("A realizar Auditoria Técnica...", expanded=True) as status:
            
            # 1. Juntar PDFs localmente
            status.write("📚 A unificar ficheiros do processo...")
            temp_path = merge_pdfs_to_temp(uploaded_files)
            
            try:
                # 2. Enviar e Analisar
                # Nota: A mensagem de status de upload é gerida dentro da função analyze_large_document
                res = analyze_large_document(temp_path, instructions, api_key, selected_model)
                
                status.update(label="✅ Auditoria Concluída!", state="complete")
                
                # 3. Mostrar Resultados
                st.divider()
                st.subheader("📋 Relatório de Auditoria")
                st.markdown(res)
                
                # 4. Botão Download
                doc_file = create_docx(res)
                st.download_button(
                    label="📥 Descarregar Relatório (Word)", 
                    data=doc_file, 
                    file_name="Auditoria_EIA.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                )
                
            except Exception as e:
                status.update(label="❌ Erro", state="error")
                st.error(f"Ocorreu um erro durante a análise: {e}")
                
            finally:
                # Limpar o ficheiro temporário local
                try: 
                    os.remove(temp_path)
                except: 
                    pass
