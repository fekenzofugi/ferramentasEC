import re
from numpy import median
from functions.lerPDF import lerPDF_palavras

# ─────────────────────────────────────────────────────────────────────────────
# LÓGICA DE EXTRAÇÃO
# ─────────────────────────────────────────────────────────────────────────────

def detectar_limites_pagina(words):
    x_etiquetagem = [w['x0'] for w in words if w['text'] == 'Etiquetagem']
    if x_etiquetagem:
        x_produto_max = min(x_etiquetagem) - 5
    else:
        largura = max((w['x1'] for w in words), default=600)
        x_produto_max = largura * 0.43

    x_unidades_header = [w['x0'] for w in words if w['text'] == 'UNIDADES']
    if x_unidades_header:
        cx = median(x_unidades_header)
        x_unidades_min = cx - 20
        x_unidades_max = cx + 40
    else:
        x_unidades_min = x_produto_max + 5
        x_unidades_max = x_produto_max + 65
    return x_produto_max, x_unidades_min, x_unidades_max

def agrupar_em_linhas(palavras, tolerancia_y=4):
    palavras.sort(key=lambda w: (w['page'], w['top']))
    linhas = []
    linha_atual = []
    top_atual = page_atual = None
    for w in palavras:
        mesma = (w['page'] == page_atual and top_atual is not None and abs(w['top'] - top_atual) < tolerancia_y)
        if mesma:
            linha_atual.append(w)
        else:
            if linha_atual:
                linhas.append({'top': top_atual, 'page': page_atual, 'text': ' '.join(x['text'] for x in linha_atual)})
            linha_atual = [w]
            top_atual = w['top']
            page_atual = w['page']
    if linha_atual:
        linhas.append({'top': top_atual, 'page': page_atual, 'text': ' '.join(x['text'] for x in linha_atual)})
    return linhas

def extrair_unidades(words_pagina, top_ref, x_min, x_max, tolerancia_y=10):
    for w in words_pagina:
        if x_min <= w['x0'] <= x_max and abs(w['top'] - top_ref) < tolerancia_y:
            try: return int(w['text'])
            except ValueError: pass
    return 0

def extrair_numero_frete(all_words):
    """Extrai o número da coleta a partir da linha 'Frete #XXXXXXXX'."""
    linhas = agrupar_em_linhas(list(all_words))
    for linha in linhas:
        m = re.search(r'Frete\s*#(\d+)', linha['text'], re.IGNORECASE)
        if m:
            return m.group(1)
    return None

def extrair_produtos(file_obj):
    all_words = lerPDF_palavras(file_obj)
    paginas_words = {}
    for w in all_words:
        paginas_words.setdefault(w['page'], []).append(w)
    limites = {page: detectar_limites_pagina(words) for page, words in paginas_words.items()}
    numero_frete = extrair_numero_frete(all_words)
    palavras_produto = [w for w in all_words if w['x0'] < limites.get(w['page'], (230, 0, 0))[0]]
    linhas = agrupar_em_linhas(palavras_produto)

    IGNORAR = ('PRODUTO', 'UNIDADES', 'IDENTIF', 'INSTRUÇ', 'Lista de', 'Frete', 'Produtos do envio', 'VERIFIQUE', 'Todos os', 'estarem', 'Além disso', 'externa da', 'Aprenda')
    produtos = []
    i = 0
    while i < len(linhas):
        linha = linhas[i]
        if 'Código ML:' not in linha['text']:
            i += 1
            continue
        m = re.search(r'Código ML:\s*(\w+)', linha['text'])
        codigo_ml = m.group(1) if m else None
        universal = None
        m = re.search(r'Código universal:\s*(\d{8,14})', linha['text'])
        if m: universal = m.group(1)
        sku = None
        m = re.search(r'SKU:\s*(\w+)', linha['text'])
        if m: sku = m.group(1)
        if i + 1 < len(linhas):
            prox = linhas[i + 1]['text']
            if not sku:
                m = re.search(r'SKU:\s*(\w+)', prox)
                if m: sku = m.group(1)
            if not universal:
                m = re.search(r'\b(\d{8,14})\b', prox)
                if m: universal = m.group(1)
        if not sku:
            i += 1
            continue
        _, x_u_min, x_u_max = limites.get(linha['page'], (230, 235, 275))
        unidades = extrair_unidades(paginas_words.get(linha['page'], []), linha['top'], x_u_min, x_u_max)
        desc_linhas = []
        k = i + 1
        while k < len(linhas):
            txt = linhas[k]['text']
            if 'Código ML:' in txt: break
            if any(t in txt for t in IGNORAR):
                k += 1
                continue
            if 'SKU:' in txt:
                k += 1
                continue
            txt_limpo = re.sub(r'^\d{8,14}\s*', '', txt).strip()
            txt_limpo = re.sub(r'SKU:\s*\w+', '', txt_limpo).strip()
            if txt_limpo and len(txt_limpo) > 2:
                desc_linhas.append(txt_limpo)
            k += 1
        produtos.append({
            'SKU': sku,
            'Código ML': codigo_ml,
            'Universal': universal or '-',
            'Unidades': unidades,
            'Produto': ' '.join(desc_linhas).strip(),
        })
        i += 1
    return produtos, numero_frete