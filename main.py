import streamlit as st
import utils

# --- 1. CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="Main",
    page_icon="🌍",
    layout="wide"
)

# --- 2. TRUQUE VISUAL (CSS) ---
# Isto força o item "main" no menu a ficar "Main" (Maiúscula) e a Negrito
st.markdown("""
<style>
    /* Seleciona o primeiro item da lista de navegação (que é o main) */
    [data-testid="stSidebarNav"] > ul > li:first-child a {
        font-weight: 800 !important; /* Negrito extra */
        text-transform: capitalize !important; /* Transforma 'main' em 'Main' */
        font-size: 1.1rem !important; /* Um pouco maior */
        color: #0e4da4 !important; /* Destaque azul (opcional) */
    }
</style>
""", unsafe_allow_html=True)

# --- 3. BARRA LATERAL (DO UTILS) ---
try:
    utils.sidebar_comum()
except Exception as e:
    st.error(f"Erro ao carregar menu lateral: {e}")

# --- 4. TÍTULO PRINCIPAL ---
st.title("🌍 Plataforma de Avaliação Ambiental")

# Verifica estado da chave (Visualização apenas)
chave_existe = bool(st.session_state.get("api_key"))

if chave_existe:
    st.success("✅ **Sistema Ativo:** A API Key está configurada. Pode utilizar todos os módulos.")
else:
    st.warning("⚠️ **Ação Necessária:** Configure a API Key na barra lateral esquerda para desbloquear a inteligência artificial.")

# --- 5. DASHBOARD DE ENTRADA ---
# Recuperar o contexto para personalizar a mensagem
contexto = st.session_state.get("contexto_utilizador", "Analista Geral")

st.markdown(f"""
---
### Painel de Controlo
Está a operar com o perfil: **{contexto}**.

Selecione um módulo no menu à esquerda para iniciar:

| Módulo | Descrição |
| :--- | :--- |
| **01. Caso a Caso** | Validação de critérios de sujeição a AIA (Anexo II do RJAIA). |
| **02. Prazos AIA** | Calculadora automática de prazos legais e cronogramas. |
| **03. Ambiente** | Auditoria de conformidade PATE e pesquisa de legislação. |
| **04. Auditor EIA** | Análise técnica de Processos de Avaliação de Impacte Ambiental. |
| **05. Simplex** | Verificação de dispensas de AIA (DL 11/2023). |

---
ℹ️ *Dica: Se a chave API desaparecer, basta voltar a inseri-la no menu lateral. O sistema memoriza-a enquanto a janela estiver aberta.*
""")

