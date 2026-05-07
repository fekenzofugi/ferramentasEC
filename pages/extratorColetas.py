import streamlit as st
import pandas as pd
from functions.gerarPDF import gerar_pdf_formatado
from functions.extrairDadosPDF import extrair_produtos

# ─────────────────────────────────────────────────────────────────────────────
# INTERFACE STREAMLIT
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(page_title="Ordenador de Coleta", page_icon="📄", layout="wide")

st.title("📄 Ordenador de Coleta")
st.write("Ordene sua coleta.")

uploaded = st.file_uploader("Subir PDF da Coleta do Mercado Livre", type="pdf")

if uploaded:
    with st.spinner("Processando dados..."):
        dados = extrair_produtos(uploaded)
        df = pd.DataFrame(dados)
    
    if not df.empty:
        st.success(f"Encontrados {len(df)} produtos!")
        st.dataframe(df, use_container_width=True)
        
        # Gerar os três PDFs (Original, SKU e Produto)
        pdf_bytes_original = gerar_pdf_formatado(df)
        
        df_ordenado_sku = df.sort_values(by="SKU")
        pdf_bytes_ordenado_sku = gerar_pdf_formatado(df_ordenado_sku)

        df_ordenado_produto = df.sort_values(by="Produto")
        pdf_bytes_ordenado_produto = gerar_pdf_formatado(df_ordenado_produto)
        
        # Colunas para organizar os botões lado a lado
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.download_button(
                label="⬇️ Ordem Original do PDF",
                data=pdf_bytes_original,
                file_name=f"Separacao_Original_{uploaded.name}",
                mime="application/pdf",
                use_container_width=True
            )
            
        with col2:
            st.download_button(
                label="⬇️ Ordem por SKU",
                data=pdf_bytes_ordenado_sku,
                file_name=f"Separacao_SKU_{uploaded.name}",
                mime="application/pdf",
                use_container_width=True
            )

        with col3:
            st.download_button(
                label="⬇️ Ordem por Nome do Produto",
                data=pdf_bytes_ordenado_produto,
                file_name=f"Separacao_Produto_{uploaded.name}",
                mime="application/pdf",
                use_container_width=True
            )
    else:
        st.error("Não foi possível extrair dados deste PDF.")