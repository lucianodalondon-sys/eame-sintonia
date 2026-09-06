#!/usr/bin/env python3
"""
alvo_literal.py — o texto do ALVO de uma linha de dose existe no documento?

O red team provou uma FUSAO real: em 008259 a linha publicada como
    Soia | "Nottue defogliatrici (allo scoperto) tentredine" | 420-800 g/ha
junta a cauda de uma linha ("...altica, meligete e tentredine", 420-800) com o
texto de outra ("Nottue defogliatrici (allo scoperto)", 400-500). A quimera
recebeu a dose da primeira: 800 contra 500 autorizados.

ESTE MODULO NAO DETECTA FUSAO. Ele mede uma coisa mais fraca e verificavel: se
o texto do alvo aparece LITERALMENTE no texto do rotulo. E publica o estado.

Por que nao detecta fusao, escrito aqui para nao virar promessa:

  * o teste literal sobre o texto da pagina inteira acusa 180 das 839 linhas, e
    a maioria e ALVO QUEBRADO EM COLUNA, nao fusao: numa etichetta de tres
    colunas, "Cemiostoma, litocollete (prima della comparsa delle mine ed in
    presenza di uova mature della 1a generazione), carpocapsa" chega ao
    pdftotext -layout intercalado com texto das colunas vizinhas. **Separar os
    dois casos exige reconstruir o texto POR COLUNA — e desde SF-01 e o que
    este modulo faz** (ver abaixo);

  * a heuristica "o alvo contem outro alvo inteiro do mesmo rotulo" acusa 86
    linhas e erra em cheio nas legitimas: `Pomacee x "Dysaphis spp., Eriosoma
    spp., Aphis spp."` e um alvo multiplo verdadeiro que apenas TERMINA com
    outro alvo usado noutra linha. Uma regra que condena esse par condena a
    propria etichetta;

  * tentei tambem ancorar primeira e ultima palavra do alvo pelos fios
    desenhados: 629 linhas conferiveis, ZERO acusacoes, porque a banda y do
    extrator nao contem as duas pontas do alvo fundido. O detector nao
    detectava o caso que existe.

Entao: nenhuma linha e rebaixada POR ESTE MODULO. Ele emite
TARGET_TEXT_NOT_FOUND_LITERALLY, que a tela usa como portao em juntaDose. As
duas coisas sao diferentes e a distincao importa para quem audita: o MODULO
emite estado, o CASCO usa o estado. REGRAS.md@5 diz as duas.

## SF-01 · O TEXTO E RECONSTRUIDO POR COLUNA ANTES DO TESTE

O arbitro da rodada 3 reproduziu as supressoes e mediu: os pares que a tela
recusava por este estado vinham de POUCAS linhas distintas, e cada uma era uma
celula REAL, inteira, apenas quebrada em duas linhas de texto — em nenhuma delas
havia fusao. As supressoes eram falso alarme de quebra de coluna sobre fato
verdadeiro. O motivo era mecanico: o teste comparava o alvo com o texto do
`pdftotext -layout` da pagina INTEIRA, onde uma etichetta de tres colunas
intercala as linhas das tres.

O conserto usa os mesmos instrumentos que R-11 e R-14 ja usam. Para cada pagina:
os FIOS VERTICAIS (`fios.py`) dizem onde estao as goteiras entre colunas; as
CAIXAS DE PALAVRA (`pdftotext -bbox-layout`) sao repartidas por essas bandas; e
dentro de cada banda o texto e remontado linha a linha, de cima para baixo. O
alvo e procurado nessa reconstrucao. O texto da pagina inteira continua valendo
como segunda chance: achar em qualquer um dos dois e achar.

O que isso NAO faz: continua sem detectar fusao. Uma linha fundida continua
sendo duas celulas coladas, e coladas elas nao existem em coluna nenhuma — o
estado `TARGET_TEXT_NOT_FOUND_LITERALLY` que sobra depois da reconstrucao e mais
estreito e mais util, nao mais completo. `FUSION_DETECTOR` continua
`NOT_IMPLEMENTED`.
"""
import argparse, json, os, re, subprocess, sys, unicodedata

RXP = re.compile(r'<page width="([\d.]+)" height="([\d.]+)">(.*?)</page>', re.S)
RXW = re.compile(r'<word xMin="([\d.]+)" yMin="([\d.]+)" xMax="([\d.]+)" yMax="([\d.]+)">([^<]*)</word>')
TOL_LINHA = 2.5      # pontos: duas palavras na mesma linha visual


def nrm(s):
    s = unicodedata.normalize("NFD", str(s or ""))
    s = "".join(c for c in s if unicodedata.category(c) != "Mn").lower()
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9 ]+", " ", s)).strip()


def texto(reg, pdfs, cache):
    os.makedirs(cache, exist_ok=True)
    alvo = os.path.join(cache, f"{reg}.txt")
    if not os.path.exists(alvo) or os.path.getsize(alvo) == 0:
        pdf = os.path.join(pdfs, f"{reg}.pdf")
        if not os.path.exists(pdf):
            return None
        try:
            subprocess.run(["pdftotext", "-layout", pdf, alvo], check=True,
                           capture_output=True, timeout=180)
        except Exception:
            return None
    return open(alvo, encoding="utf-8", errors="replace").read()


def caixas(pdf, cache):
    """Caixas de palavra por pagina, via pdftotext -bbox-layout, com cache."""
    os.makedirs(cache, exist_ok=True)
    alvo = os.path.join(cache, os.path.basename(pdf)[:-4] + ".xml")
    if not os.path.exists(alvo) or os.path.getsize(alvo) == 0:
        subprocess.run(["pdftotext", "-bbox-layout", pdf, alvo],
                       check=True, capture_output=True, timeout=300)
    body = open(alvo, encoding="utf-8", errors="replace").read()
    return [[(float(x0), float(y0), float(x1), float(y1), t)
             for x0, y0, x1, y1, t in RXW.findall(b)] for _, _, b in RXP.findall(body)]


def texto_por_coluna(pg, verticais, largura):
    """O texto da pagina remontado DENTRO de cada banda entre fios verticais.

    Uma banda e uma coluna do documento. Dentro dela as linhas voltam a ser
    consecutivas, e um alvo que ocupa duas linhas da mesma celula volta a ser
    uma frase — que e exatamente o que o teste literal precisa.
    """
    cortes = sorted({0.0, largura} | {v for v in verticais if 0 < v < largura})
    saida = []
    for a, b in zip(cortes, cortes[1:]):
        if b - a < 20:                     # banda estreita demais para ser coluna
            continue
        dentro = [w for w in pg if a <= (w[0] + w[2]) / 2 <= b]
        if not dentro:
            continue
        linhas = {}
        for x0, y0, x1, y1, t in dentro:
            cy = (y0 + y1) / 2
            k = next((k for k in linhas if abs(k - cy) <= TOL_LINHA), round(cy, 1))
            linhas.setdefault(k, []).append((x0, t))
        saida.append(" ".join(" ".join(t for _, t in sorted(linhas[k]))
                              for k in sorted(linhas)))
    return saida


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--doses", default="pilot-label-intelligence/demo/IT-DOSES.json")
    ap.add_argument("--pdfs", default="pilot-label-intelligence/labels/pdf")
    ap.add_argument("--cache", default="/tmp/tetotxt")
    ap.add_argument("--bbox", default="/tmp/bboxcache")
    ap.add_argument("--fios", default="/tmp/fioscache")
    ap.add_argument("--bin", default="pilot-label-intelligence/bin")
    ap.add_argument("--out", default="v1/dados/ALVO-LITERAL.json")
    a = ap.parse_args()
    sys.path.insert(0, a.bin)
    import fios as F
    os.makedirs(a.fios, exist_ok=True)

    d = json.load(open(a.doses, encoding="utf-8"))
    ver, achados = {}, []
    n_ok = n_nao = n_sem = n_col = 0
    cache, colcache = {}, {}

    def colunas(reg):
        """Textos por coluna do rotulo inteiro, normalizados. [] se nao der."""
        if reg in colcache:
            return colcache[reg]
        pdf = os.path.join(a.pdfs, f"{reg}.pdf")
        out = []
        if os.path.exists(pdf):
            try:
                pgs = caixas(pdf, a.bbox)
                for pi, pg in enumerate(pgs):
                    r = F.fios(pdf, pi + 1, cache=a.fios)
                    out += [nrm(x) for x in
                            texto_por_coluna(pg, r.get("V") or [],
                                             r.get("PAGE_WIDTH_PT") or 0)]
            except Exception:
                out = []
        colcache[reg] = out
        return out

    for lab in d["LABELS"]:
        reg = lab["REGISTRATION_ID"]
        if reg not in cache:
            t = texto(reg, a.pdfs, a.cache)
            cache[reg] = nrm(t) if t else None
        t = cache[reg]
        for i, r in enumerate(lab.get("ROWS") or []):
            chave = f"{reg}#{i}"
            alvo = nrm(r.get("TARGET"))
            if t is None or len(alvo) < 8:
                ver[chave] = "TARGET_TEXT_NOT_CHECKED"; n_sem += 1; continue
            if alvo in t:
                ver[chave] = "TARGET_TEXT_FOUND_LITERALLY"; n_ok += 1
            elif any(alvo in c for c in colunas(reg)):
                # SF-01 · achado na reconstrucao POR COLUNA. Nao e um achado mais
                # fraco: e o mesmo documento lido do jeito certo. O que era
                # "quebra de coluna" agora e frase.
                ver[chave] = "TARGET_TEXT_FOUND_LITERALLY"; n_ok += 1; n_col += 1
            else:
                ver[chave] = "TARGET_TEXT_NOT_FOUND_LITERALLY"; n_nao += 1
                achados.append({"REGISTRATION_ID": reg, "PRODUCT": lab.get("PRODUCT"),
                                "ROW_INDEX": i, "CROP": r.get("CROP"),
                                "TARGET": r.get("TARGET"),
                                "DOSE_PER_HECTARE": r.get("DOSE_PER_HECTARE"),
                                "DOSE_PER_HECTARE_UNIT": r.get("DOSE_PER_HECTARE_UNIT")})
    saida = {
        "DATASET": "V1-ALVO-LITERAL",
        "RULE_ID": "R-13",
        "O_QUE_ISTO_E": "o texto do alvo da linha de dose aparece literalmente no texto do rotulo",
        "O_QUE_ISTO_NAO_E": ("NAO e um detector de fusao de linha. Nao separa alvo quebrado em "
                             "coluna de alvo fundido, e por isso NAO rebaixa nenhuma linha"),
        "FUSION_DETECTOR": "NOT_IMPLEMENTED",
        "FUSION_PROVEN_EXAMPLE": ('008259: "Nottue defogliatrici (allo scoperto) tentredine" com '
                                  'dose 420-800 g/ha; na etichetta sao duas linhas distintas, e a '
                                  'de Nottue vale 400-500'),
        "WHY_NOT_IMPLEMENTED": ("tres tentativas medidas: teste literal acusa 180/839 e a maioria "
                                "e quebra de coluna; heuristica de conteudo acusa 86 e condena "
                                "alvo multiplo legitimo (Pomacee x Dysaphis/Eriosoma/Aphis); "
                                "ancoragem por fios nas duas pontas do alvo acusa ZERO porque a "
                                "banda do extrator nao contem as duas pontas do alvo fundido"),
        "TEXT_RECONSTRUCTION": ("por COLUNA, com os fios verticais de fios.py e as caixas de "
                                "palavra do pdftotext -bbox-layout; o texto da pagina inteira "
                                "vale como segunda chance"),
        "ROWS_FOUND_ONLY_AFTER_COLUMN_RECONSTRUCTION": n_col,
        "ROWS_FOUND_LITERALLY": n_ok,
        "ROWS_NOT_FOUND_LITERALLY": n_nao,
        "ROWS_NOT_CHECKED": n_sem,
        "VERDICT": ver,
        "NOT_FOUND": achados,
    }
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    json.dump(saida, open(a.out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"  alvos: literais {n_ok} (dos quais {n_col} so apos remontar por coluna) | "
          f"NAO literais {n_nao} | nao conferiveis {n_sem} "
          f"(nenhuma linha rebaixada por este modulo)", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
