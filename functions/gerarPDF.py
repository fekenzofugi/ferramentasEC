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
    total_unidades = df['Unidades'].sum()
    total_skus = len(df)

    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=False)  # controle manual de página

    PAGE_MARGIN_BOTTOM = 287  # limite Y antes de virar página
    LINE_HEIGHT = 8           # um pouco mais alto para respirar

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
        """Estima quantas linhas o produto vai ocupar."""
        pdf.set_font("Helvetica", "", 8)
        words = produto_text.split(" ")
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

    # Título com número do frete
    pdf.set_xy(14, 13)
    pdf.set_font("Helvetica", "B", 13)
    pdf.set_text_color(30, 58, 138)
    titulo = "Lista de Separação - Mercado Livre Full"
    if numero_frete:
        titulo += f"   |   Frete #{numero_frete}"
    pdf.cell(0, 7, titulo, ln=True)

    # Subtítulo com totais e data
    pdf.set_xy(14, 21)
    pdf.set_font("Helvetica", "", 9)
    pdf.set_text_color(51, 51, 51)
    data_hora = pd.Timestamp.now(tz='America/Sao_Paulo').strftime('%d/%m/%Y %H:%M')
    pdf.cell(0, 5, f"Total de SKUs: {total_skus}   |   Total de Unidades: {total_unidades}   |   Data: {data_hora}")

    pdf.ln(18)
    draw_header()

    # ── Rows ──
    for i, (_, row) in enumerate(df.iterrows()):
        estimated_height = estimate_row_height(str(row['Produto']))

        # Verifica se a linha cabe na página atual
        if pdf.get_y() + estimated_height > PAGE_MARGIN_BOTTOM:
            pdf.add_page()
            draw_header()

        # Cores alternadas com mais contraste
        cor = COR_LINHA_PAR
        pdf.set_fill_color(*cor)
        pdf.set_draw_color(*COR_BORDA)
        pdf.set_line_width(ESPESSURA_BORDA)

        y_before = pdf.get_y()
        x_start  = pdf.get_x()

        # Produto (multi-line) — renderiza primeiro para calcular altura real
        pdf.set_font("Helvetica", "", 8)
        pdf.set_xy(x_start + COL_WIDTHS[0], y_before)
        pdf.multi_cell(COL_WIDTHS[1], LINE_HEIGHT, str(row['Produto']), border=1, fill=True)
        row_height = pdf.get_y() - y_before

        # SKU
        pdf.set_font("Helvetica", "B", 8)
        pdf.set_xy(x_start, y_before)
        pdf.cell(COL_WIDTHS[0], row_height, str(row['SKU']), border=1, fill=True, align="L")

        # Qtd — destaque em negrito e centralizado
        pdf.set_font("Helvetica", "B", 10)
        pdf.set_xy(x_start + COL_WIDTHS[0] + COL_WIDTHS[1], y_before)
        pdf.cell(COL_WIDTHS[2], row_height, str(row['Unidades']), border=1, fill=True, align="C")

        # Código ML
        pdf.set_font("Helvetica", "", 9)
        pdf.set_xy(x_start + COL_WIDTHS[0] + COL_WIDTHS[1] + COL_WIDTHS[2], y_before)
        pdf.cell(COL_WIDTHS[3], row_height, str(row['Código ML']), border=1, fill=True, align="L")

        # Universal
        pdf.set_font("Helvetica", "", 9)
        pdf.set_xy(x_start + COL_WIDTHS[0] + COL_WIDTHS[1] + COL_WIDTHS[2] + COL_WIDTHS[3], y_before)
        pdf.cell(COL_WIDTHS[4], row_height, str(row['Universal']), border=1, fill=True, align="L")

        pdf.set_xy(x_start, y_before + row_height)

    # ── Output ──
    pdf_output = BytesIO()
    pdf.output(pdf_output)
    return pdf_output.getvalue()