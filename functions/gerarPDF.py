import pandas as pd
from io import BytesIO
from weasyprint import HTML

# ─────────────────────────────────────────────────────────────────────────────
# GERAÇÃO DO PDF
# ─────────────────────────────────────────────────────────────────────────────

def gerar_pdf_formatado(df):
    total_unidades = df['Unidades'].sum()
    total_skus = len(df)
    
    rows_html = ""
    for _, row in df.iterrows():
        rows_html += f"""
        <tr>
            <td style="font-weight: bold; border-bottom: 1px solid #ddd;">{row['SKU']}</td>
            <td style="border-bottom: 1px solid #ddd;">{row['Produto']}</td>
            <td style="text-align: center; font-weight: bold; border-bottom: 1px solid #ddd;">{row['Unidades']}</td>
            <td style="font-family: monospace; font-size: 8pt; border-bottom: 1px solid #ddd;">{row['Universal']}</td>
        </tr>
        """

    html_string = f"""
    <html>
    <head>
        <style>
            @page {{ size: A4; margin: 1cm; }}
            body {{ font-family: sans-serif; color: #333; }}
            .header {{ background: #f4f4f4; padding: 15px; border-radius: 5px; margin-bottom: 20px; border-left: 5px solid #1e3a8a; }}
            h1 {{ margin: 0; font-size: 16pt; color: #1e3a8a; }}
            .summary {{ margin-top: 5px; font-size: 10pt; }}
            table {{ width: 100%; border-collapse: collapse; margin-top: 10px; }}
            th {{ background: #1e3a8a; color: white; text-align: left; padding: 8px; font-size: 10pt; }}
            td {{ padding: 8px; font-size: 9pt; vertical-align: top; }}
            tr:nth-child(even) {{ background: #f9f9f9; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>Lista de Separação - Mercado Livre Full</h1>
            <div class="summary">
                <strong>Total de SKUs:</strong> {total_skus} | 
                <strong>Total de Unidades:</strong> {total_unidades} | 
                <strong>Data:</strong> {pd.Timestamp.now().strftime('%d/%m/%Y %H:%M')}
            </div>
        </div>
        <table>
            <thead>
                <tr>
                    <th style="width: 15%;">SKU</th>
                    <th style="width: 55%;">Produto</th>
                    <th style="width: 10%; text-align: center;">Qtd</th>
                    <th style="width: 20%;">Universal</th>
                </tr>
            </thead>
            <tbody>
                {rows_html}
            </tbody>
        </table>
    </body>
    </html>
    """
    
    pdf_output = BytesIO()
    HTML(string=html_string).write_pdf(pdf_output)
    return pdf_output.getvalue()