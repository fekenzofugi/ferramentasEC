
import pdfplumber

def lerPDF_palavras(file_obj):
    all_words = []
    with pdfplumber.open(file_obj) as pdf:
        for page_num, pagina in enumerate(pdf.pages):
            for w in pagina.extract_words(x_tolerance=3, y_tolerance=3):
                w['page'] = page_num
                all_words.append(w)
    return all_words