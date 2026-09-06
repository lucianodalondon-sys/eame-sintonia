#!/usr/bin/env python3
"""
dose_validar.py — confere cada dose emitida contra os FIOS DESENHADOS da tabela.

O extrator decide a que linha uma dose pertence pela posicao do texto. Onde a
tabela tem grade desenhada, existe uma autoridade melhor: o fio. Se um fio
horizontal atravessa a coluna de dose entre a linha e o valor que ela recebeu,
esse valor **nao e daquela linha**, por mais centrado que pareca.

Isto foi escrito por causa de dois erros concretos e conhecidos, no rotulo
carro-chefe 015275 DURAVIS, pagina 4:

    Porro / Afidi, mosca bianca              300 g/ha   correto
    Porro / Dorifora, cavolaia, tripidi      300 g/ha   ERRADO, a etichetta diz 600
    Porro / Nottue defogliatrici             300 g/ha   ERRADO, a etichetta diz 600

O fio em y=181,9 vai de x=178 a x=419: atravessa a coluna de dose e separa a
linha do Afidi das tres seguintes — e nao atravessa a coluna de cultura, que vai
ate x=177,6, e por isso "Porro" cobre as quatro linhas. A geometria do documento
responde certo onde a posicao do texto respondeu errado.

## Como a linha e localizada, e por que as duas primeiras tentativas falharam

Localizar por TEXTO reprovou 26 de 68 doses do 015275, varias corretas: "Afidi"
aparece dez vezes na mesma pagina e a primeira ocorrencia quase nunca e a linha
certa.

Localizar pela FAIXA da linha (`SOURCE_Y`, que o extrator agora emite) foi pior,
48 de 68: as faixas do extrator nao coincidem com as celulas desenhadas — a do
Porro/Afidi vai de 172,5 a 188,9 e engole a linha do Dorifora, que comeca em
185,2. Comparar faixa contra fio faz o fio reprovar quase tudo.

O que funciona e usar as duas: a faixa DESAMBIGUA qual "Afidi" e o desta linha, e
a posicao da PALAVRA da o y preciso para perguntar ao fio. Medido no 015275:
60 confirmadas, 1 contradita, 13 nao localizadas — e a contradita e uma das duas
doses que o juiz do painel ja tinha apontado como erradas.

Um validador errado e pior que nenhum, e as duas primeiras versoes eram erradas.

O que este script faz e NAO faz:
  - nao corrige o valor: rebaixa para NOT_PRESENT e marca DOSE_CONTRADICTED_BY_RULE,
    porque adivinhar o valor certo seria trocar um erro por outro;
  - so opina onde HA grade. Sem fio na faixa, devolve UNVERIFIABLE_NO_RULES e nao
    toca em nada — a maioria das etichette nao tem grade desenhada;
  - nunca promove NOT_PRESENT a valor.

    ERRO SILENCIOSO E PIOR QUE LACUNA DECLARADA.
"""
import argparse, json, os, subprocess, sys, tempfile
import xml.etree.ElementTree as ET

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fios as F

NS = "{http://www.w3.org/1999/xhtml}"


def palavras(pdf, cache=None):
    """{pagina: [(yMin,yMax,xMin,xMax,texto)]}"""
    out = cache and os.path.join(cache, os.path.basename(pdf) + ".bbox.xml")
    if not (out and os.path.exists(out)):
        out = out or os.path.join(tempfile.gettempdir(), os.path.basename(pdf) + ".bbox.xml")
        subprocess.run(["pdftotext", "-bbox-layout", pdf, out], check=True, capture_output=True)
    root = ET.parse(out).getroot()
    pgs = {}
    for pno, pg in enumerate(root.iter(f"{NS}page"), 1):
        pgs[pno] = [(float(w.get("yMin")), float(w.get("yMax")),
                     float(w.get("xMin")), float(w.get("xMax")), (w.text or "").strip())
                    for w in pg.iter(f"{NS}word") if (w.text or "").strip()]
    return pgs


def _n(s):
    return " ".join(str(s or "").split()).casefold()


def acha_y(ws, texto, banda=None, folga=3.0):
    """Faixa y da PALAVRA do alvo, procurada dentro da banda da linha.

    A banda sozinha e larga demais (nao bate com a celula desenhada); o texto
    sozinho e ambiguo (o mesmo alvo se repete na pagina). Juntos resolvem.
    """
    toks = _n(texto).split()
    if not toks or len(toks[0]) < 4:
        return None
    alvo = toks[0][:9]
    cand = [(y0, y1) for y0, y1, x0, x1, t in ws if _n(t).startswith(alvo)]
    if banda:
        dentro = [c for c in cand if banda[0] - folga <= c[0] <= banda[1] + folga]
        if dentro:
            return dentro[0]
        return None
    return cand[0] if cand else None


def acha_valor(ws, valor):
    """Todas as posicoes de um valor de dose na pagina."""
    v = _n(valor).replace(" ", "")
    hits = []
    for y0, y1, x0, x1, t in ws:
        tt = _n(t).replace(" ", "")
        if tt == v or tt.rstrip(".,;") == v:
            hits.append((y0, y1, x0, x1))
    return hits


def valida(pdf, rows, cache=None, cache_fios=None):
    pgs = palavras(pdf, cache)
    fcache = {}
    saida = {"CHECKED": 0, "OK": 0, "CONTRADICTED": 0,
             "UNVERIFIABLE_NO_RULES": 0, "NOT_LOCATED": 0}
    for r in rows:
        val = r.get("DOSE_PER_HECTARE")
        if val in (None, "", "NOT_PRESENT"):
            continue
        try:
            pg = int(r.get("SOURCE_PAGE"))
        except (TypeError, ValueError):
            continue
        ws = pgs.get(pg)
        if not ws:
            continue
        banda = r.get("SOURCE_Y")
        yl = acha_y(ws, r.get("TARGET"), banda)
        vs = acha_valor(ws, val)
        if not yl or not vs:
            saida["NOT_LOCATED"] += 1
            r["DOSE_RULE_CHECK"] = "NOT_LOCATED"
            continue
        if pg not in fcache:
            try:
                fcache[pg] = F.fios(pdf, pg, cache=cache_fios)
            except Exception:
                fcache[pg] = {"SEG": []}
        SEG = fcache[pg]["SEG"]
        saida["CHECKED"] += 1
        # a coluna de dose e a faixa x da propria ocorrencia do valor
        melhor = min(vs, key=lambda v: abs((v[0] + v[1]) / 2 - (yl[0] + yl[1]) / 2))
        vy0, vy1, vx0, vx1 = melhor
        col = (vx0 - 6, vx1 + 6)
        cruza = [s for s in SEG
                 if min(col[1], s[2]) - max(col[0], s[1]) >= 0.6 * (col[1] - col[0])]
        if not cruza:
            saida["UNVERIFIABLE_NO_RULES"] += 1
            r["DOSE_RULE_CHECK"] = "UNVERIFIABLE_NO_RULES"
            continue
        if F.mesma_celula(min(yl[0], vy0), max(yl[1], vy1), *col, SEG):
            saida["OK"] += 1
            r["DOSE_RULE_CHECK"] = "CONFIRMED_BY_RULE"
        else:
            saida["CONTRADICTED"] += 1
            r["DOSE_RULE_CHECK"] = "CONTRADICTED_BY_RULE"
            r["DOSE_PER_HECTARE_REJECTED"] = val
            r["DOSE_PER_HECTARE"] = "NOT_PRESENT"
            r["DOSE_PER_HECTARE_UNIT"] = "NOT_PRESENT"
            r["NEEDS_REVIEW"] = True
            r["REVIEW_NOTE"] = ("um fio desenhado da tabela separa esta linha do valor que "
                                "ela recebera; o valor foi rebaixado, nao substituido")
    return saida


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--doses", default="pilot-label-intelligence/demo/IT-DOSES.json")
    ap.add_argument("--pdfdir", default="pilot-label-intelligence/labels/pdf")
    ap.add_argument("--cache-fios", default=None)
    ap.add_argument("--out", default=None)
    a = ap.parse_args()
    d = json.load(open(a.doses, encoding="utf-8"))
    tot = {"CHECKED": 0, "OK": 0, "CONTRADICTED": 0,
           "UNVERIFIABLE_NO_RULES": 0, "NOT_LOCATED": 0}
    for lab in d["LABELS"]:
        rows = lab.get("ROWS") or []
        if not rows:
            continue
        pdf = os.path.join(a.pdfdir, f'{lab["REGISTRATION_ID"]}.pdf')
        if not os.path.exists(pdf):
            continue
        s = valida(pdf, rows, cache_fios=a.cache_fios)
        for k in tot:
            tot[k] += s[k]
        if s["CONTRADICTED"]:
            print(f'  {lab["REGISTRATION_ID"]} {str(lab.get("PRODUCT"))[:22]:<22} '
                  f'{s["CONTRADICTED"]} dose(s) rebaixada(s) por contradicao de fio',
                  file=sys.stderr)
    d["DOSE_RULE_VALIDATION"] = tot
    d["DOSE_RULE_VALIDATION_NOTE"] = (
        "cada dose por hectare foi conferida contra os fios desenhados da tabela. "
        "CONTRADICTED = um fio separa a linha do valor, e o valor foi rebaixado a "
        "NOT_PRESENT com NEEDS_REVIEW. UNVERIFIABLE_NO_RULES = a etichetta nao tem "
        "grade desenhada naquela faixa, entao o fio nao opina.")
    json.dump(d, open(a.out or a.doses, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    print(f'\n  conferidas {tot["CHECKED"]} | confirmadas {tot["OK"]} | '
          f'contraditas {tot["CONTRADICTED"]} | sem grade {tot["UNVERIFIABLE_NO_RULES"]} | '
          f'nao localizadas {tot["NOT_LOCATED"]}', file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
