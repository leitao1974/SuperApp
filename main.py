import streamlit as st
import utils

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="Main",
    page_icon="🌍",
    layout="wide"
)

# --- BARRA LATERAL (DO UTILS) ---
# Isto garante que a API Key se mantém
try:
    utils.sidebar_comum()
except Exception as e:
    st.error(f"Erro ao carregar menu lateral: {e}")

# --- TÍTULO PRINCIPAL ---
st.title("Main") 

# --- CONTEÚDO ---
# Recuperar o contexto para personalizar a mensagem
contexto = st.session_state.get("contexto_utilizador", "Analista Geral")

st.markdown(f"""
### Bem-vindo à Plataforma de Avaliação Ambiental.
Perfil ativo: **{contexto}**.

Selecione um módulo no menu lateral esquerdo para começar:

| Módulo | Função |
| :--- | :--- |
| **01. Caso a Caso** | Validação de critérios de sujeição a AIA (Anexo II) |
| **02. Prazos AIA** | Calculadora de Prazos Legais e Cronogramas |
| **03. Ambiente** | Auditoria de conformidade (antigo Compliance) e Pesquisa Web |
| **04. Auditor EIA** | Análise técnica de Estudos de Impacte Ambiental |
| **05. Simplex AIncA** | Verificação de dispensas (DL 11/2023) |

---
ℹ️ *A API Key definida no menu lateral é partilhada por todas as ferramentas.*
""")

