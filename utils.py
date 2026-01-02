import streamlit as st
import google.generativeai as genai

def sidebar_comum():
    with st.sidebar:
        st.divider()
        st.caption("🔧 DEFINIÇÕES GLOBAIS")
        
        # 1. GESTÃO DE CONTEXTO (PERFIL)
        if "contexto_utilizador" not in st.session_state:
            st.session_state["contexto_utilizador"] = "Analista Geral"
        
        opcoes = ["Analista Geral", "Revisor Técnico", "Promotor/Consultor", "Autoridade de AIA"]
        # Evita erro se o valor atual não estiver na lista
        idx = 0
        if st.session_state["contexto_utilizador"] in opcoes:
            idx = opcoes.index(st.session_state["contexto_utilizador"])

        # O key="contexto_utilizador" liga este campo diretamente à memória
        st.selectbox("Perfil:", opcoes, index=idx, key="contexto_utilizador_widget", 
                     on_change=lambda: st.session_state.update({"contexto_utilizador": st.session_state.contexto_utilizador_widget}))
        
        # Sincronização manual para garantir consistência
        if "contexto_utilizador_widget" in st.session_state:
             st.session_state["contexto_utilizador"] = st.session_state.contexto_utilizador_widget

        st.divider()

        # 2. API KEY (A CORREÇÃO ESTÁ AQUI)
        st.header("🔑 Credenciais IA")
        
        # Se a chave ainda não existe, cria vazia
        if "api_key" not in st.session_state:
            st.session_state["api_key"] = ""

        # O SEGREDO: Usar key="api_key" obriga o Streamlit a nunca esquecer o valor
        st.text_input(
            "Gemini API Key", 
            type="password", 
            key="api_key",
            help="A chave ficará guardada enquanto a aba estiver aberta."
        )
        
        # Configura a IA imediatamente se a chave existir
        if st.session_state.get("api_key"):
            try:
                genai.configure(api_key=st.session_state["api_key"])
            except Exception:
                pass # Ignora erros silenciosos na sidebar
        else:
            st.warning("⚠️ Insira a Chave para usar a IA")
        
        st.divider()
        if st.button("🏠 Voltar ao Início"):
            st.switch_page("main.py")
