import streamlit as st
import utils

# 1. Configuração da Página
st.set_page_config(
    page_title="Main",
    page_icon="🌍",
    layout="wide"
)

# 2. Carregar a Barra Lateral (Onde a chave é gerida)
try:
    utils.sidebar_comum()
except Exception as e:
    st.error(f"Erro ao carregar menu: {e}")

# 3. Conteúdo Principal
st.title("🌍 Plataforma de Avaliação Ambiental")

# Verifica se já temos chave (vem do utils)
chave_existe = bool(st.session_state.get("api_key"))

if chave_existe:
    st.info("👋 Bem-vindo! A sua **API Key está ativa**. Pode navegar para qualquer módulo no menu esquerdo.")
else:
    st.warning("⬅️ **Comece aqui:** Insira a sua API Key na barra lateral esquerda para desbloquear a plataforma.")

st.markdown("""
---
### Módulos Disponíveis:
| Módulo | Função |
| :--- | :--- |
| **01. Caso a Caso** | Validação RJAIA (Anexo II) |
| **02. Prazos AIA** | Calculadora de Prazos Legais |
| **03. Ambiente** | Compliance e Pesquisa Web |
| **04. Auditor EIA** | Análise de Grandes Processos |
| **05. Simplex** | Verificação DL 11/2023 |
""")

