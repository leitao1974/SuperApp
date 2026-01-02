import streamlit as st
import google.generativeai as genai

# Configuração da Página Principal
st.set_page_config(
    page_title="Super App Ambiental",
    page_icon="🌍",
    layout="wide"
)

# --- ESTADO GLOBAL (Sessão) ---
# Garante que a chave API e o contexto persistem entre páginas
if "api_key" not in st.session_state:
    st.session_state["api_key"] = ""
if "contexto_utilizador" not in st.session_state:
    st.session_state["contexto_utilizador"] = "Analista Geral"

# --- SIDEBAR GLOBAL ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2037/2037649.png", width=80)
    st.title("Central Ambiental")
    st.divider()
    
    # 1. Definição do Contexto
    st.header("👤 Perfil do Utilizador")
    contexto = st.selectbox(
        "Modo de Operação:",
        ["Analista Geral", "Fiscalização (IGAMAOT)", "Promotor/Consultor", "Decisor (CCDR)"]
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
st.title("🌍 Super App de Inteligência Ambiental")

st.markdown(f"""
### Bem-vindo à Central de Comando.
Está a operar com o perfil de: **{contexto}**.

Utilize o **Menu Lateral Esquerdo** para navegar entre os módulos especializados:

| Módulo | Descrição | Tecnologia |
| :--- | :--- | :---: |
| **01. Caso a Caso** | Validação RJAIA e Minutas de Decisão (Anexo II) | 🤖 IA |
| **02. Prazos AIA** | Calculadora de Prazos Legais e Gráficos de Gantt | 📅 Algoritmo |
| **03. Compliance** | Análise 'PATE' e Pesquisa Web de Legislação | 🤖 IA + 🌐 Web |
| **04. Auditor EIA** | Análise profunda de EIAs grandes (File API) | 🤖 IA Pro |
| **05. Simplex AIncA** | Verificação rápida DL 11/2023 | 🤖 IA Flash |

---
ℹ️ *Todas as ferramentas partilham a mesma Chave API definida aqui.*
""")
