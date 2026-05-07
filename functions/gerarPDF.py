import pandas as pd
from io import BytesIO
from fpdf import FPDF

# ─────────────────────────────────────────────────────────────────────────────
# GERAÇÃO DO PDF
# ─────────────────────────────────────────────────────────────────────────────
def gerar_pdf_formatado(df):
    total_unidades = df['Unidades'].sum()
    total_skus = len(df)

    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=False)  # controle manual de página

    PAGE_MARGIN_BOTTOM = 287  # limite Y antes de virar página
    LINE_HEIGHT = 7

    def draw_header():
        pdf.set_fill_color(30, 58, 138)
        pdf.set_text_color(255, 255, 255)
        pdf.set_font("Helvetica", "B", 10)
        col_widths = [28, 104, 18, 38]
        headers = ["SKU", "Produto", "Qtd", "Universal"]
        for w, h in zip(col_widths, headers):
            pdf.cell(w, 8, h, fill=True)
        pdf.ln()
        pdf.set_text_color(51, 51, 51)

    def estimate_row_height(produto_text):
        """Estima quantas linhas o produto vai ocupar."""
        pdf.set_font("Helvetica", "", 8)
        words = produto_text.split(" ")
        lines = 1
        current_line = ""
        max_width = 104 - 2
        for word in words:
            test = (current_line + " " + word).strip()
            if pdf.get_string_width(test) > max_width:
                lines += 1
                current_line = word
            else:
                current_line = test
        return lines * LINE_HEIGHT

    # ── Header do documento ──
    pdf.set_fill_color(244, 244, 244)
    pdf.set_draw_color(30, 58, 138)
    pdf.set_line_width(1.2)
    pdf.rect(10, 10, 190, 22, style='FD')
    pdf.set_line_width(0.2)

    pdf.set_xy(14, 13)
    pdf.set_font("Helvetica", "B", 14)
    pdf.set_text_color(30, 58, 138)
    pdf.cell(0, 7, "Lista de Separação - Mercado Livre Full", ln=True)

    pdf.set_xy(14, 21)
    pdf.set_font("Helvetica", "", 9)
    pdf.set_text_color(51, 51, 51)
    data_hora = pd.Timestamp.now().strftime('%d/%m/%Y %H:%M')
    pdf.cell(0, 5, f"Total de SKUs: {total_skus}   |   Total de Unidades: {total_unidades}   |   Data: {data_hora}")

    pdf.ln(18)
    draw_header()

    col_widths = [28, 104, 18, 38]

    # ── Rows ──
    for i, (_, row) in enumerate(df.iterrows()):
        estimated_height = estimate_row_height(str(row['Produto']))

        # Verifica se a linha cabe na página atual
        if pdf.get_y() + estimated_height > PAGE_MARGIN_BOTTOM:
            pdf.add_page()
            draw_header()

        fill = i % 2 == 1
        pdf.set_fill_color(249, 249, 249) if fill else pdf.set_fill_color(255, 255, 255)
        pdf.set_draw_color(221, 221, 221)

        y_before = pdf.get_y()
        x_start = pdf.get_x()

        # Produto (multi-line) — renderiza primeiro para calcular altura real
        pdf.set_font("Helvetica", "", 8)
        pdf.set_xy(x_start + col_widths[0], y_before)
        pdf.multi_cell(col_widths[1], LINE_HEIGHT, str(row['Produto']), border="B", fill=True)
        row_height = pdf.get_y() - y_before

        # SKU
        pdf.set_font("Helvetica", "B", 8)
        pdf.set_xy(x_start, y_before)
        pdf.cell(col_widths[0], row_height, str(row['SKU']), border="B", fill=True, align="L")

        # Qtd
        pdf.set_font("Helvetica", "B", 8)
        pdf.set_xy(x_start + col_widths[0] + col_widths[1], y_before)
        pdf.cell(col_widths[2], row_height, str(row['Unidades']), border="B", fill=True, align="C")

        # Universal
        pdf.set_font("Courier", "", 7)
        pdf.set_xy(x_start + col_widths[0] + col_widths[1] + col_widths[2], y_before)
        pdf.cell(col_widths[3], row_height, str(row['Universal']), border="B", fill=True)

        pdf.set_xy(x_start, y_before + row_height)

    # ── Output ──
    pdf_output = BytesIO()
    pdf.output(pdf_output)
    return pdf_output.getvalue()