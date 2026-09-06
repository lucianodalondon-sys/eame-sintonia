#!/usr/bin/env python3
"""
cultura_validar.py — a CULTURA de uma linha de dose tambem tem de sobreviver
aos fios desenhados da tabela.

`dose_validar.py` ja conferia se um fio desenhado separa a linha do VALOR.
Ninguem conferia se um fio separa a linha da CULTURA. O buraco produziu o pior
erro da ferramenta ate agora:

    LAMDEX EXTRA 008259, pagina 3. Coordenadas medidas com pdftotext -bbox-layout:
        y=161.4  "Porro"    na coluna de cultura (x 42.6..62.2)
        y=182.8  "Cimici"   na coluna de alvo    (x 181.5..203.3)
        y=182.8  "600"      na coluna de dose/ha (x 332.8..346.2)
        y=204.2  "Tabacco"  na coluna de cultura (x 42.6..73.4)
    e um fio desenhado em y=193.9..194.9 atravessando x=39.4..418.6, ou seja
    cortando a coluna de cultura entre Cimici e Tabacco.

    A linha "Cimici 600" pertence a PORRO. A ferramenta publicava
    "TABACCO x CIMICI = 600 g/ha" com o selo verde EXATA — o selo mais forte
    que ela tem — em cinco produtos. Eram as unicas cinco juncoes exatas da
    ferramenta inteira: 100% do que ela apresentava com confianca maxima
    estava errado, e errado na cultura autorizada.

REGRA. Para cada linha de dose, o token da cultura tem de estar na MESMA celula
da coluna de cultura que o INICIO da banda y da linha. Basta UMA ocorrencia do
nome da cultura na mesma celula para a atribuicao sobreviver: ocorrencia solta
so pode salvar uma linha, nunca condena-la.

Duas decisoes que custaram medicao:

  * ancorar no TOPO da banda, nao no meio. As bandas que o extrator grava vao
    de um token de alvo ate o proximo e por isso atravessam fios: a banda
    [223.96, 236.96] do LAMDEX comeca dentro da celula de Tabacco (que termina
    no fio y=228) e termina fora dela. O que identifica a linha e onde ela
    COMECA. Com o meio, essa linha — que e legitima — era condenada.

  * aceitar QUALQUER ocorrencia do nome, nao a mais proxima. A palavra
    "tabacco" tambem aparece dentro do ALVO "Tripidi e pulce del tabacco", na
    coluna de alvo; por proximidade era ela que vencia, e linhas boas caiam.

Saida: DOSES-CULTURA-CHECK.json, com um veredito por linha e a coordenada que
o sustenta. Quem consome: dose_plausibilidade / objetos / payload.
"""
import argparse, json, os, re, subprocess, sys

RXP = re.compile(r'<page width="([\d.]+)" height="([\d.]+)">(.*?)</page>', re.S)
RXW = re.compile(r'<word xMin="([\d.]+)" yMin="([\d.]+)" xMax="([\d.]+)" yMax="([\d.]+)">([^<]*)</word>')


def palavras(pdf, cache):
    """Caixas de palavra por pagina, via pdftotext -bbox-layout, com cache."""
    os.makedirs(cache, exist_ok=True)
    alvo = os.path.join(cache, os.path.basename(pdf)[:-4] + '.xml')
    if not os.path.exists(alvo) or os.path.getsize(alvo) == 0:
        subprocess.run(['pdftotext', '-bbox-layout', pdf, alvo],
                       check=True, capture_output=True, timeout=300)
    body = open(alvo, encoding='utf-8', errors='replace').read()
    return [[(float(x0), float(y0), float(x1), float(y1), t)
             for x0, y0, x1, y1, t in RXW.findall(b)] for _, _, b in RXP.findall(body)]


def raiz(s):
    """Primeira palavra util do nome da cultura, so letras minusculas."""
    s = str(s or '').split(',')[0].split('(')[0].strip()
    p = s.split()
    return re.sub(r'[^a-z]', '', p[0].lower()) if p else ''


PARADAS = {'de', 'da', 'del', 'della', 'dei', 'delle', 'degli', 'in', 'con', 'per',
           'su', 'al', 'alla', 'allo', 'ed', 'contro', 'sp', 'spp'}


def raizes_alvo(s):
    """Palavras do ALVO que servem para ancorar a linha na pagina.

    A BANDA y que o extrator grava NAO serve de ancora: ela vai de um token de
    alvo ate o proximo e por isso atravessa fios nos dois extremos. Medido: com
    o meio da banda, 27 linhas caem; com o topo, 63 — e nas duas contagens caem
    linhas legitimas (Tabacco x "Afidi e mosca bianca" e uma linha real do
    bloco Tabacco e era condenada pelo topo). A ancora tem de ser um GLIFO que
    esta escrito na linha: o proprio texto do alvo.
    """
    out = []
    for w in re.split(r'[^A-Za-zÀ-ÿ]+', str(s or '')):
        w = re.sub(r'[^a-z]', '', w.lower())
        if len(w) >= 4 and w not in PARADAS:
            out.append(w)
    return out[:4]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--doses', default='pilot-label-intelligence/demo/IT-DOSES.json')
    ap.add_argument('--pdfs', default='pilot-label-intelligence/labels/pdf')
    ap.add_argument('--bbox', default='/tmp/bboxcache')
    ap.add_argument('--fios', default='/tmp/fioscache')
    ap.add_argument('--out', default='v1/dados/DOSES-CULTURA-CHECK.json')
    ap.add_argument('--bin', default='pilot-label-intelligence/bin')
    a = ap.parse_args()
    sys.path.insert(0, a.bin)
    import fios as F

    d = json.load(open(a.doses, encoding='utf-8'))
    ver, contra = {}, []
    n_ok = n_bad = n_sem = 0
    for lab in d['LABELS']:
        reg = lab['REGISTRATION_ID']
        rows = lab.get('ROWS') or []
        pdf = os.path.join(a.pdfs, f'{reg}.pdf')
        if not rows or not os.path.exists(pdf):
            continue
        try:
            pgs = palavras(pdf, a.bbox)
        except Exception:
            pgs = []
        for i, r in enumerate(rows):
            chave = f'{reg}#{i}'
            y, pg, crop = r.get('SOURCE_Y'), r.get('SOURCE_PAGE'), r.get('CROP')
            pi = (int(pg) - 1) if pg else -1
            rz = raiz(crop)
            if not y or pi < 0 or pi >= len(pgs) or len(rz) < 4:
                ver[chave] = 'CROP_ASSIGNMENT_NOT_CHECKED'; n_sem += 1; continue
            cands = [(x0, y0, x1, y1) for x0, y0, x1, y1, t in pgs[pi]
                     if re.sub(r'[^a-z]', '', t.lower()) == rz]
            if not cands:
                ver[chave] = 'CROP_ASSIGNMENT_NOT_CHECKED'; n_sem += 1; continue
            # ancora: um glifo do ALVO dentro da banda da linha
            alvos = raizes_alvo(r.get('TARGET'))
            y0b, y1b = float(y[0]) - 2, float(y[1]) + 2
            anc = [ (wy0 + wy1) / 2 for wx0, wy0, wx1, wy1, t in pgs[pi]
                    if re.sub(r'[^a-z]', '', t.lower()) in alvos
                    and y0b <= (wy0 + wy1) / 2 <= y1b ]
            if not anc:
                ver[chave] = 'CROP_ASSIGNMENT_NOT_CHECKED'; n_sem += 1; continue
            anc = sorted(set(round(x, 1) for x in anc))
            topo = anc[0]
            try:
                # fios() e 1-INDEXADO: passa a pagina direto para pdftoppm -f/-l.
                # palavras() devolve lista 0-indexada. Misturar os dois faz o
                # modulo comparar as palavras de uma pagina com os fios da
                # anterior — foi o que aconteceu na primeira medicao, e os fios
                # da pagina errada condenavam linhas boas e absolviam ruins.
                seg = F.fios(pdf, pi + 1, cache=a.fios)['SEG']
            except Exception:
                ver[chave] = 'CROP_ASSIGNMENT_NOT_CHECKED'; n_sem += 1; continue
            # CONSERVADOR NOS DOIS EIXOS: basta UMA combinacao (ocorrencia do
            # alvo, ocorrencia da cultura) na mesma celula para a linha
            # sobreviver. A banda que o extrator grava e folgada e engloba
            # glifos de linhas vizinhas — com min(anc) o modulo pegava um
            # "Afidi" do cabecalho e condenava a linha Agrumi, que e boa.
            # Combinacao solta so pode SALVAR uma linha, nunca condena-la.
            achou = None
            for ay in anc:
                for x0, cy0, x1, cy1 in cands:
                    c = (cy0 + cy1) / 2
                    if F.mesma_celula(min(c, ay), max(c, ay), x0, x1, seg):
                        achou = c; break
                if achou is not None:
                    break
            if achou is not None:
                ver[chave] = 'CROP_ASSIGNMENT_CONSISTENT_WITH_RULES'; n_ok += 1
            else:
                ver[chave] = 'CROP_ASSIGNMENT_CONTRADICTED_BY_RULE'; n_bad += 1
                perto = min(cands, key=lambda c: abs((c[1] + c[3]) / 2 - topo))
                contra.append({
                    'REGISTRATION_ID': reg, 'PRODUCT': lab.get('PRODUCT'), 'ROW_INDEX': i,
                    'CROP': crop, 'TARGET': r.get('TARGET'),
                    'DOSE_PER_HECTARE': r.get('DOSE_PER_HECTARE'),
                    'DOSE_PER_HECTARE_UNIT': r.get('DOSE_PER_HECTARE_UNIT'),
                    'SOURCE_PAGE': pg, 'ANCHOR_Y': round(topo, 2),
                    'CROP_TOKEN_Y': round((perto[1] + perto[3]) / 2, 2),
                    'DOSE_RULE_CHECK': r.get('DOSE_RULE_CHECK', 'NOT_CHECKED'),
                    'PROOF': (f'na pagina {pg} um fio desenhado da tabela separa o inicio da '
                              f'linha (alvo em y={topo:.1f}) de toda ocorrencia de "{rz}" na coluna de '
                              f'cultura (a mais proxima em y={(perto[1]+perto[3])/2:.1f}). '
                              f'A linha nao pertence a esta cultura'),
                })
    saida = {
        'DATASET': 'V1-DOSE-CULTURA-CHECK',
        'RULE_ID': 'R-11',
        'O_QUE_ISTO_E': ('conferencia da CULTURA de cada linha de dose contra os fios '
                         'desenhados da tabela, do mesmo jeito que dose_validar confere o valor'),
        'O_QUE_ISTO_NAO_E': ('nao le dose nova, nao corrige a cultura e nao adivinha a certa: '
                             'so diz que a atribuida nao sobrevive ao documento'),
        'ANCHOR': 'y do primeiro glifo do ALVO dentro da banda da linha',
        'ROWS_CONSISTENT': n_ok,
        'ROWS_CONTRADICTED': n_bad,
        'ROWS_NOT_CHECKED': n_sem,
        'VERDICT': ver,
        'CONTRADICTED': contra,
    }
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    json.dump(saida, open(a.out, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print(f'  linhas de dose: coerentes {n_ok} | CULTURA CONTRADITA POR FIO {n_bad} | '
          f'nao conferiveis {n_sem}', file=sys.stderr)
    for c in contra[:12]:
        print(f'    CONTRADITA {c["REGISTRATION_ID"]} {str(c["PRODUCT"])[:14]:<14} '
              f'{str(c["CROP"])[:24]:<24} x {str(c["TARGET"])[:20]:<20} '
              f'= {c["DOSE_PER_HECTARE"]} {c["DOSE_PER_HECTARE_UNIT"]}', file=sys.stderr)
    return 0


if __name__ == '__main__':
    sys.exit(main())
