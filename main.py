import streamlit as st
import utils

# --- 1. CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="Main",
    page_icon="🌍",
    layout="wide"
)

# --- 2. ESTILO VISUAL (CSS) ---
# Força o "main" no menu lateral a ficar "Main" (Maiúscula e Negrito)
st.markdown("""
<style>
    [data-testid="stSidebarNav"] > ul > li:first-child a {
        font-weight: 800 !important;
        text-transform: capitalize !important;
        font-size: 1.1rem !important;
        color: #0e4da4 !important;
    }
</style>
""", unsafe_allow_html=True)

# --- 3. BARRA LATERAL (Gestão de Chaves) ---
try:
    utils.sidebar_comum()
except Exception as e:
    st.error(f"Erro ao carregar menu lateral: {e}")

# --- 4. TÍTULO PRINCIPAL ---
st.title("🌍 Plataforma de Avaliação Ambiental")

# Verifica se a chave existe (apenas visualização)
chave_existe = bool(st.session_state.get("api_key"))

if chave_existe:
    st.success("✅ **Sistema Ativo:** A API Key está configurada. Pode navegar pelos módulos.")
else:
    st.warning("⚠️ **Ação Necessária:** Configure a API Key na barra lateral esquerda para desbloquear a inteligência artificial.")

# --- 5. PAINEL DE CONTROLO (ATUALIZADO) ---
contexto = st.session_state.get("contexto_utilizador", "Analista Geral")

st.markdown(f"""
---
### Painel de Controlo
Perfil ativo: **{contexto}**.

Selecione uma ferramenta no menu à esquerda:

| Módulo | Descrição |
| :--- | :--- |
| **01. Caso a Caso** | Validação de critérios de sujeição a AIA (Anexo II do RJAIA). |
| **02. Prazos AIA** | Calculadora automática de prazos legais e cronogramas. |
| **03. Ambiente** | Auditoria de conformidade PATE, pesquisa Web e análise legal. |
| **04. Auditor EIA** | Análise técnica de Processos de Avaliação de Impacte Ambiental (Tomo I + Anexos). |
| **05. AIncA** | **Avaliação de Incidências Ambientais** (Rede Natura 2000 / DL 140/99). |

---
ℹ️ *Plataforma de apoio técnico e jurídico em Avaliação Ambiental.*
""")
