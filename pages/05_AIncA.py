import sys
import os

# --- 1. CONFIGURAÇÃO DE CAMINHOS ---
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(current_dir)
sys.path.insert(0, root_dir)

import utils
import streamlit as st
import google.generativeai as genai
import pypdf
from docx import Document
from io import BytesIO
import time

# --- 2. CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="AIncA (Rede Natura 2000)", 
    page_icon="🦅", 
    layout="wide"
)

# --- 3. BARRA LATERAL ---
try:
    utils.sidebar_comum()
except:
    pass

# --- 4. TÍTULO E ENQUADRAMENTO ---
st.title("🦅 Avaliação de Incidências Ambientais (AIncA)")
st.markdown("""
**Enquadramento Legal:** Decreto-Lei n.º 140/99, de 24 de abril (alterado pelos DL n.º 49/2005 e DL n.º 156-A/2013).

Este módulo apoia a avaliação de ações, planos ou projetos **não diretamente relacionados com a gestão** de um Sítio da Rede Natura 2000 (ZEC/ZPE), mas suscetíveis de o afetar de forma significativa.
""")

# Recuperar API Key
api_key = st.session_state.get("api_key", "")
if not api_key:
    st.warning("⚠️ Aguardando API Key no menu lateral.")
    st.stop()

# ==========================================
# --- 5. BASE DE CONHECIMENTO SETORIAL ---
# ==========================================
SECTOR_GUIDES = {
    "Geral / Outros": "Guia da Comissão Europeia (2011) - Avaliação de planos e projetos.",
    "Infraestruturas Lineares (Estradas)": "Manual de apoio ICNB (2008) e Guia APA (2009) para Infraestruturas Rodoviárias.",
    "Linhas Elétricas (Transporte >110kV)": "Manual CIBIO/ICNF/REN (2020) - Muito Alta Tensão e Avifauna. Atenção a Áreas Críticas.",
    "Linhas Elétricas (Distribuição <110kV)": "Manual ICNB (2008) - Linhas de Distribuição e Avifauna.",
    "Parques Eólicos": "Guias ICNB (2008) para Morcegos e APA (2009) para Parques Eólicos.",
    "ETAR / Hidráulica": "Guia APA (2008) para ETARs.",
    "Indústria Extrativa": "Guia CCDR-LVT (2008) para Minas e Pedreiras."
}

# ==========================================
# --- FUNÇÕES ---
# ==========================================
def get_text_from_multiple_files(file_list):
    combined_text = ""
    file_names = []
    if not file_list: return None, None

    for uploaded_file in file_list:
        try:
            reader = pypdf.PdfReader(uploaded_file)
            file_text = ""
            for page in reader.pages:
                file_text += page.extract_text() or "" 
            
            combined_text += f"\n--- FICHEIRO: {uploaded_file.name} ---\n{file_text}\n"
            file_names.append(uploaded_file.name)
        except Exception as e:
            st.error(f"Erro a ler {uploaded_file.name}: {e}")
            
    return combined_text, file_names

def create_word_docx(text, p_files, l_files, tipologia):
    doc = Document()
    doc.add_heading('Parecer Técnico AIncA (Rede Natura 2000)', 0)
    doc.add_paragraph(f"Tipologia: {tipologia}")
    doc.add_paragraph(f"Documentos Analisados: {', '.join(p_files) if p_files else 'N/A'}")
    
    for line in text.split('\n'):
        line = line.strip()
        if not line: continue
        if line.startswith('## '): doc.add_heading(line.replace('##',''), 1)
        elif line.startswith('### '): doc.add_heading(line.replace('###',''), 2)
        elif line.startswith('- '): doc.add_paragraph(line[2:], style='List Bullet')
        else: doc.add_paragraph(line)
        
    buffer = BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer

# ==========================================
# --- INTERFACE ---
# ==========================================

# A. Configuração do Projeto
st.sidebar.markdown("---")
st.sidebar.header("Tipologia do Projeto")
selected_sector = st.sidebar.selectbox(
    "Selecione o setor para carregar guias específicos:",
    list(SECTOR_GUIDES.keys())
)
st.sidebar.info(f"📚 **Referência:** {SECTOR_GUIDES[selected_sector]}")

# B. Uploads
col1, col2 = st.columns(2)
with col1:
    files_p = st.file_uploader("1. Projeto (Memória Descritiva / Peças Desenhadas)", type=["pdf"], accept_multiple_files=True)
with col2:
    files_l = st.file_uploader("2. Cartografia / Estudo de Incidências (Opcional)", type=["pdf"], accept_multiple_files=True)

# C. Botão de Ação
if st.button("🚀 Analisar Incidências (AIncA)", type="primary"):
    if not files_p:
        st.error("⚠️ Carregue os ficheiros do projeto.")
    else:
        with st.status("A realizar Avaliação de Incidências Ambientais...", expanded=True) as status:
            
            # 1. Leitura
            status.write("📖 A ler documentos do projeto...")
            text_p, names_p = get_text_from_multiple_files(files_p)
            text_l, names_l = get_text_from_multiple_files(files_l)
            
            # 2. Configuração IA
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel("gemini-1.5-flash") # Pode alterar para Pro se disponível
            
            # 3. Construção do Prompt Rigoroso
            guia_especifico = SECTOR_GUIDES[selected_sector]
            
            prompt = f"""
            Atua como Perito em Conservação da Natureza e Avaliação Ambiental.
            Realiza uma pré-avaliação AIncA (Avaliação de Incidências Ambientais).
            
            === QUADRO LEGAL ===
            1. Decreto-Lei n.º 140/99 (Rede Natura 2000), atualizado pelo DL 49/2005.
            2. Artigo 10.º: AIncA aplica-se se o projeto afetar ZEC/ZPE significativamente e NÃO for gestão da área.
            3. RELAÇÃO COM AIA: Se o projeto estiver sujeito a AIA (DL 151-B/2013), a AIncA é integrada na AIA. Verifica isto primeiro.
            
            === GUIAS TÉCNICOS ESPECÍFICOS APLICÁVEIS ===
            Setor selecionado: {selected_sector}
            Referência técnica: {guia_especifico}
            (Usa os critérios destes manuais para avaliar impactos, ex: colisão de aves em linhas, fragmentação em estradas).
            
            === DADOS DO PROJETO ===
            {text_p}
            {text_l}
            
            === TAREFA: RELATÓRIO AIncA ===
            Produz um parecer estruturado nas 4 fases metodológicas da CE (2011):
            
            ## 1. TRIAGEM (SCREENING) E ENQUADRAMENTO
            - O projeto é de gestão do Sítio? (Se sim, dispensa AIncA).
            - O projeto está sujeito a AIA (Anexos DL 151-B/2013)? Se sim, remeter para procedimento AIA.
            - Se não for AIA nem Gestão: Há probabilidade de afetar ZEC/ZPE (efeitos diretos, indiretos ou cumulativos)?
            
            ## 2. AVALIAÇÃO ADEQUADA (PREVISÃO DE IMPACTES)
            - Identifica valores naturais afetados (Habitats Anexo I, Espécies Anexo II, Aves Anexo I Diretiva Aves).
            - Analisa impactos na INTEGRIDADE do Sítio (estrutura e função).
            - Para {selected_sector}, considera os impactos específicos (ex: mortalidade, barreira, perturbação).
            
            ## 3. SOLUÇÕES ALTERNATIVAS E MITIGAÇÃO
            - O projeto apresenta alternativas de localização/traçado?
            - As medidas de mitigação propostas são eficazes e garantem que não há impacto residual significativo?
            
            ## 4. CONCLUSÃO TÉCNICA
            - O projeto pode ser aprovado tal como está?
            - Requer medidas de compensação (apenas se houver RIRIP - Razões Imperativas de Reconhecido Interesse Público)?
            
            Usa linguagem técnica, cita a legislação e os manuais de referência.
            """

            try:
                status.write(f"🤖 A analisar com base nos manuais de {selected_sector}...")
                response = model.generate_content(prompt)
                status.update(label="Concluído", state="complete")
                
                # Visualização
                st.markdown("### 🦅 Parecer Técnico AIncA")
                st.markdown(response.text)
                
                # Download
                doc = create_word_docx(response.text, names_p, names_l, selected_sector)
                st.download_button(
                    "📥 Descarregar Parecer Word", 
                    doc, 
                    "Parecer_AIncA.docx", 
                    "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                )
                
            except Exception as e:
                status.update(label="Erro", state="error")
                st.error(f"Erro na análise: {e}")