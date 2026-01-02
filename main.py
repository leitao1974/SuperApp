import streamlit as st
import google.generativeai as genai

# Configuração da Página Principal
st.set_page_config(
    page_title="Super App Ambiental",
    page_icon="🌍",
    layout="wide"
)

# --- ESTADO GLOBAL (Sessão) ---
# Aqui garantimos que a Chave API e o Contexto passam para as outras apps
if "api_key" not in st.session_state:
    st.session_state["api_key"] = ""
if "contexto_utilizador" not in st.session_state:
    st.session_state["contexto_utilizador"] = "Geral"

# --- SIDEBAR GLOBAL ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2037/2037649.png", width=80)
    st.title("Central Ambiental")
    st.divider()
    
    # 1. Definição do Contexto (O seu pedido principal)
    st.header("👤 Perfil do Utilizador")
    contexto = st.selectbox(
        "Modo de Operação:",
        ["Analista Geral", "Fiscalização (IGAMAOT)", "Promotor/Consultor", "Decisor (CCDR)"]
    )
    st.session_state["contexto_utilizador"] = contexto
    
    st.info(f"Modo Ativo: **{contexto}**")
    
    st.divider()

    # 2. Chave API Única (Para não pedir em cada app)
    st.header("🔑 Credenciais IA")
    api_input = st.text_input("Google Gemini API Key", type="password", value=st.session_state["api_key"])
    
    if api_input:
        st.session_state["api_key"] = api_input
        genai.configure(api_key=api_input)
        st.success("Chave API Configurada Globalmente!")
    else:
        st.warning("Insira a chave para desbloquear os módulos de IA.")

# --- CONTEÚDO DA PÁGINA PRINCIPAL ---
st.title("🌍 Super App de Inteligência Ambiental")
st.markdown(f"""
Bem-vindo à plataforma integrada. Está a operar com o perfil de **{contexto}**.

### 🚀 Módulos Disponíveis (Menu Lateral):

| Módulo | Função Principal | IA Ativa? |
| :--- | :--- | :---: |
| **01. Caso a Caso** | Validação RJAIA e Minutas de Decisão | ✅ |
| **02. Gestão Prazos** | Calculadora de Prazos Legais e Gantt | ❌ |
| **03. Compliance** | Análise 'PATE' e Pesquisa Web | ✅ |
| **04. Auditor Pro** | Análise de Grandes EIA (File API) | ✅ |
| **05. Simplex** | Verificação rápida DL 11/2023 | ✅ |

---
🔽 **Selecione um módulo na barra lateral esquerda para começar.**
""")

# Lógica de Contexto (Exemplo de como afeta a "Homepage")
if contexto == "Fiscalização (IGAMAOT)":
    st.error("⚠️ ALERTA: Foco em detetar desconformidades e incumprimento de prazos.")
elif contexto == "Promotor/Consultor":
    st.success("💡 DICA: Utilize o módulo 'Simplex' para pré-validar o seu projeto antes da submissão.")