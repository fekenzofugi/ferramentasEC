import pandas as pd
from io import BytesIO
from fpdf import FPDF

# ─────────────────────────────────────────────────────────────────────────────
# GERAÇÃO DO PDF
# ─────────────────────────────────────────────────────────────────────────────

# Larguras das colunas: SKU | Produto | Qtd | Código ML | Universal
# Total = 190mm (margem a margem)
COL_WIDTHS = [25, 72, 12, 30, 51]
HEADERS    = ["SKU", "Produto", "Qtd", "Código ML", "Universal"]

# Cores alternadas das linhas — mais contraste para facilitar leitura
COR_LINHA_PAR   = (255, 255, 255)  # branco
COR_LINHA_IMPAR = (220, 230, 255)  # azul bem claro
COR_BORDA       = (100, 120, 180)  # azul médio — borda visível entre linhas
ESPESSURA_BORDA = 0.5              # mm — mais grosso que o padrão (0.2)

def gerar_pdf_formatado(df, numero_frete=None):
    # Função interna para garantir que o texto não quebre o PDF
    def safe_str(text):
        if pd.isna(text):
            return ""
        # Converte para latin-1 ignorando caracteres que não existem nessa codificação (emojis, símbolos especiais)
        return str(text).encode("latin-1", "ignore").decode("latin-1")

    total_unidades = df['Unidades'].sum()
    total_skus = len(df)

    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=False)

    PAGE_MARGIN_BOTTOM = 287
    LINE_HEIGHT = 8

    def draw_header():
        pdf.set_fill_color(30, 58, 138)
        pdf.set_text_color(255, 255, 255)
        pdf.set_font("Helvetica", "B", 9)
        pdf.set_draw_color(10, 30, 100)
        pdf.set_line_width(0.5)
        for w, h in zip(COL_WIDTHS, HEADERS):
            pdf.cell(w, 9, h, border=1, fill=True, align="C")
        pdf.ln()
        pdf.set_text_color(30, 30, 30)

    def estimate_row_height(produto_text):
        pdf.set_font("Helvetica", "", 8)
        # Sanitiza o texto também na estimativa para evitar o erro no get_string_width
        text = safe_str(produto_text)
        words = text.split(" ")
        lines = 1
        current_line = ""
        max_width = COL_WIDTHS[1] - 3
        for word in words:
            test = (current_line + " " + word).strip()
            if pdf.get_string_width(test) > max_width:
                lines += 1
                current_line = word
            else:
                current_line = test
        return lines * LINE_HEIGHT

    # ── Header do documento ──
    pdf.set_fill_color(230, 235, 255)
    pdf.set_draw_color(30, 58, 138)
    pdf.set_line_width(1.2)
    pdf.rect(10, 10, 190, 22, style='FD')
    pdf.set_line_width(0.2)

    pdf.set_xy(14, 13)
    pdf.set_font("Helvetica", "B", 13)
    pdf.set_text_color(30, 58, 138)
    
    # Sanitiza o título caso o número do frete tenha caracteres especiais
    titulo = "Lista de Separação - Mercado Livre Full"
    if numero_frete:
        titulo += f"   |   Frete #{safe_str(numero_frete)}"
    pdf.cell(0, 7, titulo, ln=True)

    pdf.set_xy(14, 21)
    pdf.set_font("Helvetica", "", 9)
    pdf.set_text_color(51, 51, 51)
    data_hora = pd.Timestamp.now(tz='America/Sao_Paulo').strftime('%d/%m/%Y %H:%M')
    pdf.cell(0, 5, f"Total de SKUs: {total_skus}   |   Total de Unidades: {total_unidades}   |   Data: {data_hora}")

    pdf.ln(18)
    draw_header()

    # ── Rows ──
    for i, (_, row) in enumerate(df.iterrows()):
        # Sanitizamos todos os campos antes de processar
        txt_produto   = safe_str(row['Produto'])
        txt_sku       = safe_str(row['SKU'])
        txt_unidades  = safe_str(row['Unidades'])
        txt_cod_ml    = safe_str(row['Código ML'])
        txt_universal = safe_str(row['Universal'])

        estimated_height = estimate_row_height(txt_produto)

        if pdf.get_y() + estimated_height > PAGE_MARGIN_BOTTOM:
            pdf.add_page()
            draw_header()

        # Cores alternadas
        cor = COR_LINHA_IMPAR if i % 2 != 0 else COR_LINHA_PAR
        pdf.set_fill_color(*cor)
        pdf.set_draw_color(*COR_BORDA)
        pdf.set_line_width(ESPESSURA_BORDA)

        y_before = pdf.get_y()
        x_start  = pdf.get_x()

        # Produto (multi-line)
        pdf.set_font("Helvetica", "", 8)
        pdf.set_xy(x_start + COL_WIDTHS[0], y_before)
        pdf.multi_cell(COL_WIDTHS[1], LINE_HEIGHT, txt_produto, border=1, fill=True)
        row_height = pdf.get_y() - y_before

        # SKU
        pdf.set_font("Helvetica", "B", 8)
        pdf.set_xy(x_start, y_before)
        pdf.cell(COL_WIDTHS[0], row_height, txt_sku, border=1, fill=True, align="L")

        # Qtd
        pdf.set_font("Helvetica", "B", 10)
        pdf.set_xy(x_start + COL_WIDTHS[0] + COL_WIDTHS[1], y_before)
        pdf.cell(COL_WIDTHS[2], row_height, txt_unidades, border=1, fill=True, align="C")

        # Código ML
        pdf.set_font("Helvetica", "", 9)
        pdf.set_xy(x_start + COL_WIDTHS[0] + COL_WIDTHS[1] + COL_WIDTHS[2], y_before)
        pdf.cell(COL_WIDTHS[3], row_height, txt_cod_ml, border=1, fill=True, align="L")

        # Universal
        pdf.set_font("Helvetica", "", 9)
        pdf.set_xy(x_start + COL_WIDTHS[0] + COL_WIDTHS[1] + COL_WIDTHS[2] + COL_WIDTHS[3], y_before)
        pdf.cell(COL_WIDTHS[4], row_height, txt_universal, border=1, fill=True, align="L")

        pdf.set_xy(x_start, y_before + row_height)

    pdf_output = BytesIO()
    pdf.output(pdf_output)
    return pdf_output.getvalue()