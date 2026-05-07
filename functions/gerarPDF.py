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
    pdf.set_auto_page_break(auto=True, margin=10)

    # ── Header ──
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

    # ── Table header ──
    pdf.set_fill_color(30, 58, 138)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Helvetica", "B", 10)

    col_widths = [28, 104, 18, 38]  # SKU, Produto, Qtd, Universal
    headers = ["SKU", "Produto", "Qtd", "Universal"]

    for w, h in zip(col_widths, headers):
        pdf.cell(w, 8, h, fill=True)
    pdf.ln()

    # ── Rows ──
    pdf.set_text_color(51, 51, 51)

    for i, (_, row) in enumerate(df.iterrows()):
        fill = i % 2 == 1
        if fill:
            pdf.set_fill_color(249, 249, 249)
        else:
            pdf.set_fill_color(255, 255, 255)

        pdf.set_draw_color(221, 221, 221)

        y_before = pdf.get_y()

        # SKU (bold)
        pdf.set_font("Helvetica", "B", 8)
        pdf.cell(col_widths[0], 7, str(row['SKU']), border="B", fill=True)

        # Produto (multi-line)
        pdf.set_font("Helvetica", "", 8)
        x_after_sku = pdf.get_x()
        pdf.multi_cell(col_widths[1], 7, str(row['Produto']), border="B", fill=True)
        row_height = pdf.get_y() - y_before

        # Reposiciona para continuar na mesma linha (Qtd e Universal)
        pdf.set_xy(x_after_sku + col_widths[1], y_before)

        # Qtd (bold, centered)
        pdf.set_font("Helvetica", "B", 8)
        pdf.cell(col_widths[2], row_height, str(row['Unidades']), border="B", fill=True, align="C")

        # Universal
        pdf.set_font("Courier", "", 7)
        pdf.cell(col_widths[3], row_height, str(row['Universal']), border="B", fill=True)

        pdf.ln()

    # ── Output ──
    pdf_output = BytesIO()
    pdf.output(pdf_output)
    return pdf_output.getvalue()