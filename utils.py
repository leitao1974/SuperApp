import streamlit as st
import google.generativeai as genai

def sidebar_comum():
    """
    Gera a barra lateral e garante que a API Key persiste na memória
    mesmo quando se muda de página ou se carregam ficheiros.
    """
    # --- 1. INICIALIZAR MEMÓRIA (O COFRE) ---
    if "api_key" not in st.session_state:
        st.session_state.api_key = ""
    
    if "contexto_utilizador" not in st.session_state:
        st.session_state.contexto_utilizador = "Analista Geral"

    # --- 2. BARRA LATERAL ---
    with st.sidebar:
        st.header("🔧 Configuração Global")
        
        # --- A. SELETOR DE PERFIL ---
        # Função que grava a escolha na memória imediatamente
        def update_perfil():
            st.session_state.contexto_utilizador = st.session_state.widget_perfil
            
        opcoes = ["Analista Geral", "Revisor Técnico", "Promotor/Consultor", "Autoridade de AIA"]
        
        # Recupera o índice atual para o seletor não "saltar"
        try:
            idx = opcoes.index(st.session_state.contexto_utilizador)
        except ValueError:
            idx = 0

        st.selectbox(
            "Modo de Operação:",
            opcoes,
            index=idx,
            key="widget_perfil",    # Chave temporária do widget
            on_change=update_perfil # Grava assim que muda
        )

        st.divider()

        # --- B. API KEY (A CORREÇÃO DEFINITIVA) ---
        st.header("🔑 Credenciais IA")
        
        # Função que grava a chave na memória imediatamente
        def update_key():
            st.session_state.api_key = st.session_state.widget_key

        # O Campo de Texto
        st.text_input(
            "Google Gemini API Key",
            type="password",
            value=st.session_state.api_key, # Lê o valor guardado no cofre
            key="widget_key",               # Chave temporária do widget
            on_change=update_key,           # Ação: Gravar no cofre ao escrever
            help="Pressione Enter para gravar. A chave ficará fixa enquanto o browser estiver aberto."
        )

        # --- 3. VALIDAÇÃO VISUAL ---
        if st.session_state.api_key:
            st.success("✅ Chave Guardada!")
            # Tenta configurar a IA silenciosamente
            try:
                genai.configure(api_key=st.session_state.api_key)
            except:
                pass
        else:
            st.warning("⚠️ Chave em falta.")

        st.divider()
        if st.button("🏠 Voltar ao Início"):
            st.switch_page("main.py")
