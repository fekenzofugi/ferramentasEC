import streamlit as st

# Página home das ferramentas
st.set_page_config(page_title="Ferramentas", page_icon="🛠️", layout="wide")
st.title("🛠️ Ferramentas")
st.write("Escolha uma das ferramentas abaixo para começar:")
col1, col2 = st.columns(2)
with col1:
    st.subheader("📦 Extrator de XML")
    if st.button("Acessar Extrator", use_container_width=True):
        # Certifique-se que o nome do arquivo aqui é IGUAL ao nome no disco
        st.switch_page("pages/extratorNFe.py")
with col2:
    st.subheader("📄 Ordenador de Coleta")
    if st.button("Acessar Ordenador", use_container_width=True):
        # Tente o caminho relativo simples
        st.switch_page("pages/extratorColetas.py")