import streamlit as st
import google.generativeai as genai

def sidebar_comum():
    """
    Gera a barra lateral padrão para todas as páginas da Super App.
    Garante que a API Key e o Contexto não se perdem ao mudar de página.
    """
    with st.sidebar:
        # Título pequeno para indicar que é uma sub-página
        st.caption("Navegação Global")
        st.divider()
        
        # 1. RECUPERAR/DEFINIR O CONTEXTO
        # Se não existir na memória, define o padrão
        if "contexto_utilizador" not in st.session_state:
            st.session_state["contexto_utilizador"] = "Analista Geral"
        
        # Lista de perfis (Tem de ser IGUAL à do main.py)
        opcoes_perfis = [
            "Analista Geral", 
            "Revisor Técnico", 
            "Promotor/Consultor", 
            "Autoridade de AIA"
        ]
        
        # Tenta encontrar o índice do perfil atual na lista
        try:
            indice_atual = opcoes_perfis.index(st.session_state["contexto_utilizador"])
        except ValueError:
            indice_atual = 0
            
        novo_contexto = st.selectbox(
            "Modo de Operação:",
            opcoes_perfis,
            index=indice_atual
        )
        
        # Atualiza a memória se o utilizador mudar aqui
        st.session_state["contexto_utilizador"] = novo_contexto
        st.caption(f"Perfil Ativo: **{novo_contexto}**")

        st.divider()

        # 2. GESTÃO DA API KEY
        st.header("🔑 Credenciais IA")
        
        if "api_key" not in st.session_state:
            st.session_state["api_key"] = ""
            
        # O value vem da session_state, para já vir preenchido se foi posto no main.py
        api_input = st.text_input(
            "Google Gemini API Key", 
            type="password", 
            value=st.session_state["api_key"]
        )
        
        if api_input:
            st.session_state["api_key"] = api_input
            try:
                genai.configure(api_key=api_input)
                # Não mostramos mensagem de sucesso aqui para não poluir a sidebar
            except:
                pass
        else:
            st.warning("⚠️ IA inativa (Falta Key)")
            
        st.divider()
        st.markdown("---")
        if st.button("🏠 Voltar ao Início"):
            st.switch_page("main.py")