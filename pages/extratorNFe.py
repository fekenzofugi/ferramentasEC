import streamlit as st
import pandas as pd
import xml.etree.ElementTree as ET
from io import BytesIO

# Endpoint
st.set_page_config(page_title="Extrator de XML", page_icon="📦", layout="wide")

st.title("📦 Extrator de XML")
uploaded_files = st.file_uploader("Arraste os XMLs", type="xml", accept_multiple_files=True)

if uploaded_files:
    dados = []
    for file in uploaded_files:
        try:
            tree = ET.parse(file)
            root = tree.getroot()
            
            # Busca recursiva para ignorar problemas de Namespace
            produtos = root.findall('.//{http://www.portalfiscal.inf.br/nfe}prod')
            if produtos:
                for prod in produtos:
                    dados.append({
                        'Descricao': prod.findtext('{http://www.portalfiscal.inf.br/nfe}xProd'),
                        'EAN': prod.findtext('{http://www.portalfiscal.inf.br/nfe}cEAN')
                    })
            else:
                # Tenta formato NFSe (Serviço)
                desc = root.find('.//{http://www.sped.fazenda.gov.br/nfse}xDescServ')
                if desc is not None:
                    dados.append({'Descricao': desc.text, 'EAN': 'N/A (SERVIÇO)'})
        except Exception as e:
            st.error(f"Erro no arquivo {file.name}")

    if dados:
        df = pd.DataFrame(dados)
        st.dataframe(df)
        
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, header=False)
        
        st.download_button("Baixar Excel", output.getvalue(), "extraido.xlsx")
    else:
        st.warning("Nenhum EAN encontrado nos arquivos enviados.")