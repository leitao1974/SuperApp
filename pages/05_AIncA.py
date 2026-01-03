import sys
import os

# --- 1. CONFIGURAÇÃO DE CAMINHOS ---
# Garante que o Python encontra o utils.py na pasta raiz
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

# --- 3. BARRA LATERAL (Base) ---
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

# Recuperar API Key da memória global
api_key = st.session_state.get("api_key", "")
if not api_key:
    st.warning("⚠️ **Atenção:** API Key não detetada. Por favor insira-a no menu lateral esquerdo.")
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

def get_available_models(key):
    """Lista modelos disponíveis na API (Flash vs Pro) de forma dinâmica."""
    try:
        genai.configure(api_key=key)
        # Filtra apenas modelos capazes de gerar conteúdo de texto
        models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        return models
    except:
        # Fallback caso a listagem falhe
        return ["models/gemini-1.5-pro-latest", "models/gemini-1.5-flash"]

def get_text_from_multiple_files(file_list):
    """Extrai texto de múltiplos PDFs carregados."""
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
    """Gera um ficheiro Word formatado com o parecer."""
    doc = Document()
    doc.add_heading('Parecer Técnico AIncA (Rede Natura 2000)', 0)
    
    doc.add_paragraph(f"Tipologia do Projeto: {tipologia}")
    doc.add_paragraph(f"Documentos Analisados: {', '.join(p_files) if p_files else 'N/A'}")
    doc.add_paragraph("---")
    
    # Processa Markdown simples para Word
    for line in text.split('\n'):
        line = line.strip()
        if not line: continue
        
        if line.startswith('## '): 
            doc.add_heading(line.replace('##', '').strip(), 1)
        elif line.startswith('### '): 
            doc.add_heading(line.replace('###', '').strip(), 2)
        elif line.startswith('- ') or line.startswith('* '): 
            doc.add_paragraph(line[2:], style='List Bullet')
        else: 
            doc.add_paragraph(line)
        
    buffer = BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer

# ==========================================
# --- INTERFACE ---
# ==========================================

# --- A. BARRA LATERAL (CONFIGURAÇÕES) ---
with st.sidebar:
    st.divider()
    st.markdown("### 🧠 Motor de IA")
    
    # 1. Seletor de Modelo Dinâmico
    # Permite ao utilizador escolher entre Flash (rápido) ou Pro (inteligente)
    opcoes_modelos = get_available_models(api_key)
    
    # Tenta selecionar o 'Pro' por defeito (Recomendado para análises jurídicas AIncA)
    idx_padrao = 0
    for i, m in enumerate(opcoes_modelos):
        if "pro" in m or "1.5-pro" in m:
            idx_padrao = i
            break
            
    selected_model = st.selectbox(
        "Modelo de Análise:", 
        opcoes_modelos, 
        index=idx_padrao,
        help="Use modelos 'Pro' para maior rigor jurídico na análise e 'Flash' para rapidez."
    )
    
    st.divider()
    
    # 2. Tipologia do Projeto
    st.header("Contexto Setorial")
    selected_sector = st.selectbox(
        "Selecione o setor para carregar critérios específicos:",
        list(SECTOR_GUIDES.keys())
    )
    st.info(f"📚 **Referência Técnica:** {SECTOR_GUIDES[selected_sector]}")

# --- B. ÁREA PRINCIPAL (UPLOADS) ---
col1, col2 = st.columns(2)
with col1:
    files_p = st.file_uploader(
        "1. Projeto (Memória Descritiva / Peças Desenhadas)", 
        type=["pdf"], 
        accept_multiple_files=True
    )
with col2:
    files_l = st.file_uploader(
        "2. Cartografia / Estudo de Incidências (Opcional)", 
        type=["pdf"], 
        accept_multiple_files=True
    )

# --- C. BOTÃO DE AÇÃO E LÓGICA ---
if st.button("🚀 Analisar Incidências (AIncA)", type="primary", use_container_width=True):
    if not files_p:
        st.error("⚠️ Por favor carregue os ficheiros do projeto (Campo 1).")
    else:
        # Spinner/Status expandível para mostrar progresso
        with st.status("A realizar Avaliação de Incidências Ambientais...", expanded=True) as status:
            
            # 1. Leitura dos ficheiros
            status.write("📖 A ler documentos do projeto...")
            text_p, names_p = get_text_from_multiple_files(files_p)
            text_l, names_l = get_text_from_multiple_files(files_l)
            
            # 2. Configuração da IA com o modelo escolhido
            genai.configure(api_key=api_key)
            status.write(f"🤖 A carregar motor de inteligência: **{selected_model}**...")
            model = genai.GenerativeModel(selected_model)
            
            # 3. Construção do Prompt (Rigoroso e Jurídico)
            guia_especifico = SECTOR_GUIDES[selected_sector]
            
            prompt = f"""
            Atua como Perito Sénior em Conservação da Natureza e Avaliação Ambiental.
            Realiza uma pré-avaliação AIncA (Avaliação de Incidências Ambientais) rigorosa.
            
            === QUADRO LEGAL DE REFERÊNCIA ===
            1. Decreto-Lei n.º 140/99 (Rede Natura 2000), atualizado pelo DL 49/2005.
            2. Artigo 10.º: A AIncA aplica-se se o projeto afetar ZEC/ZPE de forma significativa e NÃO for de gestão direta da área.
            3. RELAÇÃO COM AIA: Verifica prioritariamente se o projeto está sujeito a AIA (DL 151-B/2013). Se estiver, a AIncA é integrada na AIA.
            
            === GUIAS TÉCNICOS ESPECÍFICOS APLICÁVEIS ===
            Setor selecionado: {selected_sector}
            Referência técnica a utilizar: {guia_especifico}
            (Usa os critérios destes manuais para avaliar impactos, ex: mortalidade de avifauna, fragmentação de habitat, efeito barreira).
            
            === DADOS DO PROJETO ===
            {text_p}
            {text_l}
            
            === TAREFA: RELATÓRIO TÉCNICO AIncA ===
            Produz um parecer estruturado seguindo as 4 fases metodológicas da Comissão Europeia (2011):
            
            ## 1. TRIAGEM (SCREENING) E ENQUADRAMENTO
            - O projeto é necessário para a gestão do Sítio? (Se sim, dispensa AIncA).
            - O projeto está sujeito a AIA geral (Anexos DL 151-B/2013)? Se sim, deve remeter para procedimento de AIA.
            - Se não for AIA nem Gestão: Existe probabilidade de afetar ZEC/ZPE (efeitos diretos, indiretos ou cumulativos)?
            
            ## 2. AVALIAÇÃO ADEQUADA (PREVISÃO DE IMPACTES)
            - Identifica valores naturais concretos que podem ser afetados (Habitats Anexo I, Espécies Anexo II, Aves Anexo I Diretiva Aves).
            - Analisa impactos na INTEGRIDADE do Sítio (estrutura e função ecológica).
            - Para o setor {selected_sector}, considera os impactos específicos conhecidos.
            
            ## 3. SOLUÇÕES ALTERNATIVAS E MITIGAÇÃO
            - O projeto apresenta alternativas de localização ou traçado para evitar áreas sensíveis?
            - As medidas de mitigação propostas são eficazes? Garantem a inexistência de impacto residual significativo?
            
            ## 4. CONCLUSÃO TÉCNICA E RECOMENDAÇÕES
            - O projeto pode ser aprovado tal como está?
            - Requer AIncA aprofundada?
            - Requer medidas de compensação (apenas aplicável se houver Razões Imperativas de Reconhecido Interesse Público - RIRIP)?
            
            Usa linguagem técnica adequada, cita a legislação e os manuais de referência indicados.
            """

            try:
                # 4. Envio para a IA (Com timeout aumentado para 600s para suportar modelos Pro)
                response = model.generate_content(prompt, request_options={"timeout": 600})
                status.update(label="✅ Análise Concluída com Sucesso", state="complete")
                
                # 5. Apresentação de Resultados
                st.markdown("### 🦅 Parecer Técnico AIncA")
                st.markdown(response.text)
                
                # 6. Geração do Documento Word
                doc = create_word_docx(response.text, names_p, names_l, selected_sector)
                
                st.download_button(
                    label="📥 Descarregar Parecer (Word)", 
                    data=doc, 
                    file_name="Parecer_AIncA.docx", 
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                )
                
            except Exception as e:
                status.update(label="❌ Erro na Análise", state="error")
                st.error(f"Ocorreu um erro durante a comunicação com a IA: {e}")
