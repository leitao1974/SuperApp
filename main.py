# main.py
import streamlit as st
import google.generativeai as genai

# Configuração da Página Principal
st.set_page_config(
    page_title="Avaliação Ambiental",  # <--- NOME ALTERADO
    page_icon="🌿",
    layout="wide"
)

# --- ESTADO GLOBAL (Sessão) ---
if "api_key" not in st.session_state:
    st.session_state["api_key"] = ""
if "contexto_utilizador" not in st.session_state:
    st.session_state["contexto_utilizador"] = "Analista Geral"

# --- SIDEBAR GLOBAL ---
with st.sidebar:
    st.title("Avaliação Ambiental") # <--- TÍTULO ALTERADO
    st.divider()
    
    # 1. Definição do Contexto (PERFIS ATUALIZADOS)
    st.header("👤 Perfil do Utilizador")
    contexto = st.selectbox(
        "Modo de Operação:",
        [
            "Analista Geral", 
            "Revisor Técnico",       # <--- SUBSTITUIU "Fiscalização"
            "Promotor/Consultor", 
            "Autoridade de AIA"      # <--- SUBSTITUIU "Decisor (CCDR)"
        ]
    )
    st.session_state["contexto_utilizador"] = contexto
    st.caption(f"Contexto Ativo: **{contexto}**")
    
    st.divider()

    # 2. Chave API Única
    st.header("🔑 Credenciais IA")
    api_input = st.text_input("Google Gemini API Key", type="password", value=st.session_state["api_key"])
    
    if api_input:
        st.session_state["api_key"] = api_input
        try:
            genai.configure(api_key=api_input)
            st.success("API Conectada!")
        except Exception as e:
            st.error(f"Erro na Chave: {e}")
    else:
        st.warning("Insira a chave para usar os módulos de IA.")

# --- CONTEÚDO DA HOMEPAGE ---
st.title("🌿 Plataforma de Avaliação Ambiental")

st.markdown(f"""
### Bem-vindo.
Está a operar com o perfil de: **{contexto}**.

Utilize o **Menu Lateral Esquerdo** para aceder às ferramentas de análise:

| Módulo | Função |
| :--- | :--- |
| **01. Caso a Caso** | Validação de critérios de sujeição a AIA (Anexo II) |
| **02. Prazos AIA** | Calculadora de Prazos Legais e Cronogramas |
| **03. Compliance** | Auditoria de conformidade legal e normativa |
| **04. Auditor EIA** | Análise técnica de Estudos de Impacte Ambiental |
| **05. Simplex AIncA** | Verificação de dispensas (DL 11/2023) |

---
ℹ️ *Plataforma de apoio à decisão técnica em Avaliação de Impacte Ambiental.*
""")

