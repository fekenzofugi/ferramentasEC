import streamlit as st
import pandas as pd
import xml.etree.ElementTree as ET
from io import BytesIO

def format_cnpj(cnpj):
    c = ''.join(filter(str.isdigit, cnpj or ''))
    if len(c) == 14:
        return f'{c[:2]}.{c[2:5]}.{c[5:8]}/{c[8:12]}-{c[12:]}'
    return cnpj

def format_ncm(ncm):
    n = ''.join(filter(str.isdigit, ncm or ''))
    if len(n) == 8:
        return f'{n[:4]}.{n[4:6]}.{n[6:]}'
    return ncm

NS = '{http://www.portalfiscal.inf.br/nfe}'
NS_NFSE = '{http://www.sped.fazenda.gov.br/nfse}'

st.set_page_config(page_title="Extrator de XML", page_icon="📦", layout="wide")
st.title("📦 Extrator de XML - NF-e")

uploaded_files = st.file_uploader("Arraste os XMLs", type="xml", accept_multiple_files=True)

if uploaded_files:
    dados = []
    for file in uploaded_files:
        try:
            tree = ET.parse(file)
            root = tree.getroot()

            emit = root.find(f'.//{NS}emit')
            cnpj_emitente = emit.findtext(f'{NS}CNPJ') if emit is not None else 'N/A'
            nome_emitente = emit.findtext(f'{NS}xNome') if emit is not None else 'N/A'

            ide = root.find(f'.//{NS}ide')
            numero_nf = ide.findtext(f'{NS}nNF') if ide is not None else 'N/A'

            produtos = root.findall(f'.//{NS}prod')
            if produtos:
                for prod in produtos:
                    dados.append({
                        'Descrição'       : prod.findtext(f'{NS}xProd'),
                        'EAN'             : prod.findtext(f'{NS}cEAN'),
                        'Cód. Fabricante' : prod.findtext(f'{NS}cProd'),
                        'Vlr Unitário'    : prod.findtext(f'{NS}vUnCom'),
                        'Emitente'        : nome_emitente,
                        'CNPJ Emitente'   : format_cnpj(cnpj_emitente),
                        'NCM'             : format_ncm(prod.findtext(f'{NS}NCM')),
                        'Nº NF'           : numero_nf,
                    })
            else:
                desc = root.find(f'.//{NS_NFSE}xDescServ')
                if desc is not None:
                    dados.append({
                        'Descrição'       : desc.text,
                        'EAN'             : 'N/A (SERVIÇO)',
                        'Cód. Fabricante' : 'N/A',
                        'Vlr Unitário'    : 'N/A',
                        'Emitente'        : nome_emitente,
                        'CNPJ Emitente'   : format_cnpj(cnpj_emitente),
                        'NCM'             : 'N/A',
                        'Nº NF'           : numero_nf,
                    })
        except Exception as e:
            st.error(f"Erro no arquivo {file.name}: {e}")

    if dados:
        df = pd.DataFrame(dados)
        df['Vlr Unitário'] = pd.to_numeric(df['Vlr Unitário'], errors='coerce')
        df['Vlr Unitário'] = df['Vlr Unitário'].apply(lambda x: f"{x:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.') if pd.notna(x) else 'N/A')
        st.success(f"{len(df)} item(s) extraído(s) de {len(uploaded_files)} arquivo(s).")
        st.dataframe(df, use_container_width=True)

        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Itens NF')
        output.seek(0)
        st.download_button(
            label="⬇️ Baixar Excel",
            data=output.getvalue(),
            file_name="extraido.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    else:
        st.warning("Nenhum dado encontrado nos arquivos enviados.")