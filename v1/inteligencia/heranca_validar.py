#!/usr/bin/env python3
"""
heranca_validar.py — MAX. APLICACOES e INTERVALO tambem tem de sobreviver ao
documento. Sao restricao regulatoria, nao enfeite da tabela.

## Os dois defeitos, medidos

**(a) Heranca de celula mesclada que nunca passou por fio nenhum.**
Em 008259/013560/013590, pagina 2, bloco Orticole: a coluna `n.max` tem um fio
em y=420,96 logo abaixo do "2 (7 giorni)", e os fios seguintes PARAM antes da
coluna. A celula y 420,96..480,96 e MESCLADA e contem um unico valor, "1",
cobrindo Dorifora + Cimici + Nottue. A ferramenta publicava MAX=2 e
INTERVALO=7 giorni para a linha Dorifora, com selo HERDADA e
`CONFERENCIA PELOS FIOS = CONFIRMED_BY_RULE` — alimentando 96 pares publicados.
Os rotulos irmaos 015275 e 017687 leem a MESMA linha como MAX=1: cinco
etichettas identicas publicavam dois n.max diferentes e a ferramenta nao
percebia.

**(b) Nota mesclada que ENUMERA culturas, distribuida por posicao de linha.**
Em 004701 PIRIMOR 50 (e 007876, 014091, 017340, 017409) a coluna "note" e UMA
celula mesclada que diz:

    "1 applicazione: fragola, pomodoro, ..., lattughe e insalate, tranne
     spinacio baby leaf e bietola da foglia baby leaf"
    "2 applicazioni a distanza di 7-12 giorni: carciofo, cetriolo, melone,
     zucca, cocomero, cipolla, aglio, piselli e fagioli da granella"

A ferramenta distribuiu as duas por POSICAO DE LINHA e trocou-as: publicava
"Lattughe e insalate | 0.75 Kg/ha | 2 | 7-12 giorni | CONFIRMADA". Lattuga e
cultura de ciclo curto, onde o excesso de aplicacoes E o risco de residuo.

## As duas regras

  R-15a  o valor herdado tem de estar numa CELULA DESENHADA que cubra a linha,
         **e na mesma tabela que ela**. Mesmo instrumento de R-14: os fios que
         atravessam a coluna DO VALOR dizem ate onde a celula dele vai, e a
         extensao x desses fios diz de que tabela ela e. Se a linha esta fora,
         o valor e da vizinha e sai `CONTRADICTED_BY_RULE`; se nao da para achar
         a celula, sai `NOT_VALIDATED` — nunca numero com selo HERDADA.

         O TESTE EM X FALTAVA, e a rodada 4 mediu o preco: numa pagina com duas
         tabelas lado a lado, a celula que CONFIRMAVA o n.max podia estar na
         OUTRA tabela — mesma altura na folha, tabela diferente. Em `017687`
         ELTIRA a celula da tabela CERTA diz 1 e a ferramenta publicava 2 com o
         selo `MAX_CONFIRMED_BY_RULE`, que e o mais forte que este modulo tem.
         Confirmar pelo vizinho e o mesmo erro que R-11 existe para impedir,
         cometido um eixo adiante.

  R-15b  quando a etichetta escreve "N applicazioni: <lista de culturas>", a
         lista MANDA — **desde que a nota seja do bloco daquela linha.**

         A rodada 4 mediu o buraco: a nota vive numa celula mesclada da coluna
         "note", e uma etichetta com dois blocos (pieno campo e serra) tem uma
         nota por bloco. A regra procurava a cultura em TODAS as notas do
         documento e aplicava a que casasse — podendo trazer a nota de um bloco
         para a linha de outro. A contradicao continuava sendo uma ABSTENCAO na
         tela (o numero nao era publicado, o que e o lado seguro), mas o MOTIVO
         impresso era uma afirmacao sobre o documento que podia estar errada.

         Agora a nota e LOCALIZADA na pagina da linha, pelas caixas de palavra,
         e a ancora da linha tem de cair dentro da banda y dela. Onde a nota nao
         puder ser localizada, o estado e `MAX_NOT_PROVED_NOTE_BLOCK_UNKNOWN`:
         o numero continua nao sendo publicado — nada aqui volta a publicar um
         n.max que a nota contradiz — mas a tela deixa de afirmar de qual nota
         se trata.

## O que este modulo NAO faz

Nao corrige o numero e nao escolhe entre duas leituras. Ele rebaixa e mostra o
que o documento diz. `NOT_VALIDATED` e ignorancia com nome proprio, nao zero.

Saida: HERANCA-CHECK.json, um veredito por `reg#i` para MAX e outro para
INTERVALO, com a coordenada ou a frase que o sustenta.
"""
import argparse, json, os, re, sys
from collections import Counter

# "2 applicazioni a distanza di 7-12 giorni: carciofo, cetriolo, ..."
# O dois-pontos tem de vir logo depois do numero (ou da clausula "a distanza"):
# sem isso a regex engolia "1 applicazione anno 7 giorni Pomacee Orticole in
# pieno campo:", que e outra coisa — cabecalho de bloco, nao nota de numero de
# aplicacoes.
RX_NOTA = re.compile(
    r"\b(\d+)\s+applicazion[ei]"
    r"(?:\s+a\s+distanza\s+di\s+(\d+\s*-?\s*\d*)\s*giorni)?\s*:\s*",
    re.I)
RX_CORTE = re.compile(r"[.;]|\b\d+\s+applicazion[ei]", re.I)
LISTA_MAX = 400
FOLGA_FIO = 2.5      # pontos: espessura do risco no raster de 150 dpi


def notas_de_aplicacao(texto):
    """[(n_aplicacoes, intervalo_ou_None, lista_de_culturas, literal)]."""
    t = re.sub(r"\s+", " ", texto)
    out = []
    for m in RX_NOTA.finditer(t):
        resto = t[m.end():m.end() + LISTA_MAX]
        c = RX_CORTE.search(resto)
        lista = resto[:c.start()] if c else resto
        out.append((m.group(1), (m.group(2) or "").replace(" ", ""),
                    lista.lower(), (m.group(0) + lista).strip()))
    return out


def nomes_da_celula(crop):
    """Palavras de cultura da celula, para procurar dentro da lista da nota."""
    bruto = re.sub(r"\(.*?\)", " ", str(crop or "")).lower()
    bruto = re.split(r"\btranne\b|\beccetto\b|\bescluso\b", bruto)[0]
    return [w for w in re.split(r"[^a-zà-ÿ]+", bruto) if len(w) >= 5]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--doses", default="pilot-label-intelligence/demo/IT-DOSES.json")
    ap.add_argument("--pdfs", default="pilot-label-intelligence/labels/pdf")
    ap.add_argument("--bbox", default="/tmp/bboxcache")
    ap.add_argument("--fios", default="/tmp/fioscache")
    ap.add_argument("--texto", default="/tmp/leiturafluxo")
    ap.add_argument("--out", default="v1/dados/HERANCA-CHECK.json")
    ap.add_argument("--bin", default="pilot-label-intelligence/bin")
    a = ap.parse_args()
    sys.path.insert(0, a.bin)
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import fios as F
    from par_validar import palavras, celula, celula_coerente, radical, raizes_alvo
    import subprocess
    os.makedirs(a.fios, exist_ok=True)
    os.makedirs(a.texto, exist_ok=True)

    memo = {}

    def segmentos(pdf, pagina1):
        k = (pdf, pagina1)
        if k not in memo:
            try:
                r = F.fios(pdf, pagina1, cache=a.fios)
                memo[k] = (r["SEG"], r.get("PAGE_HEIGHT_PT") or 1e6)
            except Exception:
                memo[k] = None
        return memo[k]

    def texto_do(pdf, reg):
        alvo = os.path.join(a.texto, reg + ".txt")
        if not os.path.exists(alvo) or os.path.getsize(alvo) == 0:
            try:
                subprocess.run(["pdftotext", pdf, alvo], check=True,
                               capture_output=True, timeout=120)
            except Exception:
                return ""
        return open(alvo, encoding="utf-8", errors="replace").read()

    d = json.load(open(a.doses, encoding="utf-8"))
    ver_max, ver_int, contra = {}, {}, []
    cont = Counter()
    for lab in d["LABELS"]:
        reg = lab["REGISTRATION_ID"]
        rows = lab.get("ROWS") or []
        pdf = os.path.join(a.pdfs, f"{reg}.pdf")
        if not rows or not os.path.exists(pdf):
            continue
        try:
            pgs = palavras(pdf, a.bbox)
        except Exception:
            pgs = []
        notas = notas_de_aplicacao(texto_do(pdf, reg))
        for i, r in enumerate(rows):
            chave = f"{reg}#{i}"
            mx = str(r.get("MAX_APPLICATIONS") or "")
            iv = str(r.get("APPLICATION_INTERVAL") or "")

            # ---- R-15b · a nota que enumera culturas manda sobre a posicao
            nota_bate = None
            nota_no_bloco = None
            if notas and mx and mx.isdigit():
                nomes = nomes_da_celula(r.get("CROP"))
                casadas = [n for n in notas if any(w in n[2] for w in nomes)]
                if len(casadas) == 1:
                    nota_bate = casadas[0]
                    # A NOTA E DE QUAL BLOCO? Localiza-se o inicio literal dela
                    # na pagina da linha e exige-se que a ancora da linha caia
                    # dentro da banda y da nota. Sem isso, a nota de um bloco
                    # cai sobre a linha de outro.
                    y, pg = r.get("SOURCE_Y"), r.get("SOURCE_PAGE")
                    pi = (int(pg) - 1) if pg else -1
                    if y and 0 <= pi < len(pgs):
                        chave_nota = [w for w in re.findall(r"[a-zà-ÿ]{5,}",
                                                           nota_bate[3].lower())][:4]
                        ys = [(wy0 + wy1) / 2 for _a, wy0, _b, wy1, t in pgs[pi]
                              if t.strip(" .,;:()").lower() in chave_nota]
                        if ys:
                            lo, hi = min(ys), max(ys)
                            meio = (float(y[0]) + float(y[1])) / 2
                            nota_no_bloco = (lo - 6 <= meio <= hi + 6)
                        else:
                            nota_no_bloco = None
                    else:
                        nota_no_bloco = None
            if nota_bate and nota_bate[0] != mx and nota_no_bloco is not True:
                ver_max[chave] = "MAX_NOT_PROVED_NOTE_BLOCK_UNKNOWN"
                cont[ver_max[chave]] += 1
                contra.append({
                    "KEY": chave, "REGISTRATION_ID": reg, "PRODUCT": lab.get("PRODUCT"),
                    "CROP": r.get("CROP"), "TARGET": r.get("TARGET"),
                    "FIELD": "MAX_APPLICATIONS", "PUBLISHED": mx,
                    "LABEL_SAYS": "NOTE_FOUND_BUT_BLOCK_NOT_ESTABLISHED",
                    "LABEL_NOTE": nota_bate[3][:300],
                    "PROOF": ("ha nota de numero de aplicacoes que enumera culturas e nomeia esta, "
                              "e ela diz um numero diferente do publicado — mas este leitor NAO "
                              "conseguiu estabelecer que a nota e do bloco desta linha. O numero "
                              "nao e publicado; a nota tambem nao e afirmada"),
                })
                continue
            if nota_bate and nota_bate[0] != mx:
                ver_max[chave] = "MAX_CONTRADICTED_BY_LABEL_NOTE"
                cont[ver_max[chave]] += 1
                contra.append({
                    "KEY": chave, "REGISTRATION_ID": reg, "PRODUCT": lab.get("PRODUCT"),
                    "CROP": r.get("CROP"), "TARGET": r.get("TARGET"),
                    "FIELD": "MAX_APPLICATIONS",
                    "PUBLISHED": mx, "LABEL_SAYS": nota_bate[0],
                    "LABEL_NOTE": nota_bate[3][:300],
                    "PROOF": (f"a etichetta escreve uma nota de numero de aplicacoes que "
                              f"ENUMERA culturas, e esta cultura esta na lista de "
                              f"\"{nota_bate[0]} applicazion\". A tabela publicava {mx} por "
                              f"POSICAO DE LINHA. A lista manda sobre a posicao"),
                })
                if nota_bate[1] and iv:
                    ver_int[chave] = "INTERVAL_CONTRADICTED_BY_LABEL_NOTE"
                    cont[ver_int[chave]] += 1
                continue

            # ---- R-15a · o valor herdado tem de estar em celula que cubra a linha
            for campo, valor, herd, dest, rot in (
                    ("MAX_APPLICATIONS", mx, r.get("MAX_APPLICATIONS_INHERITED"),
                     ver_max, "MAX"),
                    ("APPLICATION_INTERVAL", iv, r.get("APPLICATION_INTERVAL_INHERITED"),
                     ver_int, "INTERVAL")):
                if not herd:
                    dest[chave] = f"{rot}_NOT_INHERITED"
                    cont[dest[chave]] += 1
                    continue
                num = (re.findall(r"\d+", valor) or [None])[0]
                y, pg = r.get("SOURCE_Y"), r.get("SOURCE_PAGE")
                pi = (int(pg) - 1) if pg else -1
                if not num or not y or pi < 0 or pi >= len(pgs):
                    dest[chave] = f"{rot}_NOT_VALIDATED"
                    cont[dest[chave]] += 1
                    continue
                # ancora da linha: um glifo do ALVO dentro da banda que o
                # extrator gravou — a mesma ancora de R-11
                alvos = raizes_alvo(str(r.get("TARGET") or "").upper().replace(" ", "_"))
                y0b, y1b = float(y[0]) - 2, float(y[1]) + 2
                # a ancora guarda x TAMBEM: sem ele nao ha como saber se o
                # valor que confirma esta na mesma tabela que a linha
                anc_xy = sorted({(round((wx0 + wx1) / 2, 1), round((wy0 + wy1) / 2, 1))
                                 for wx0, wy0, wx1, wy1, t in pgs[pi]
                                 if radical(t) in alvos
                                 and y0b <= (wy0 + wy1) / 2 <= y1b})
                anc = sorted({y for _x, y in anc_xy})
                sg = segmentos(pdf, pi + 1)
                if not anc or sg is None:
                    dest[chave] = f"{rot}_NOT_VALIDATED"
                    cont[dest[chave]] += 1
                    continue
                seg, altura = sg
                cobre = houve = False
                for wx0, wy0, wx1, wy1, t in pgs[pi]:
                    if t.strip().strip(".,;:()") != num:
                        continue
                    cel = celula(pgs[pi], wx0, wx1, (wy0 + wy1) / 2, seg, altura)
                    if (cel is None or cel == 'RULES_ARE_TEXT_UNDERLINES'
                            or not celula_coerente(pgs[pi], *cel)):
                        continue
                    houve = True
                    # FOLGA DA ESPESSURA DO FIO. O risco da tabela nao e uma
                    # linha matematica: o raster o detecta em tres alturas
                    # vizinhas (~1,5 pt) e a ancora de uma linha pode cair EM
                    # CIMA dele. Medido em 008259: a linha "Pesco e nettarine x
                    # Tripidi" ancora em y=190,0, entre o fio de 188,64 e o de
                    # 192,0 — sem folga ela era condenada por estar na propria
                    # borda da sua celula. A folga cobre a espessura do fio e
                    # nada mais.
                    # cobre em Y **e** e da mesma tabela em X. A extensao x dos
                    # fios que fecham a celula do valor diz de que tabela ela e;
                    # a ancora da linha tem de cair dentro dela.
                    if any(cel[0] - FOLGA_FIO < ay < cel[1] + FOLGA_FIO
                           and cel[2] - 1 <= ax <= cel[3] + 1
                           for ax, ay in anc_xy):
                        cobre = True
                        break
                if cobre:
                    dest[chave] = f"{rot}_CONFIRMED_BY_RULE"
                elif houve:
                    dest[chave] = f"{rot}_CONTRADICTED_BY_RULE"
                    contra.append({
                        "KEY": chave, "REGISTRATION_ID": reg, "PRODUCT": lab.get("PRODUCT"),
                        "CROP": r.get("CROP"), "TARGET": r.get("TARGET"),
                        "FIELD": campo, "PUBLISHED": valor, "LABEL_SAYS": "VALUE_BELONGS_TO_ANOTHER_ROW",
                        "SOURCE_PAGE": pg, "ROW_ANCHOR_Y": anc[0],
                        "PROOF": (f"o valor {valor} foi herdado de celula mesclada, e nenhuma "
                                  f"celula desenhada que contem \"{num}\" na coluna dele cobre "
                                  f"esta linha (ancora em y={anc[0]}). O valor e da linha "
                                  f"vizinha"),
                    })
                else:
                    dest[chave] = f"{rot}_NOT_VALIDATED"
                cont[dest[chave]] += 1

    saida = {
        "DATASET": "V1-HERANCA-CHECK",
        "RULE_ID": "R-15",
        "O_QUE_ISTO_E": ("conferencia de MAX. APLICACOES e INTERVALO herdados de celula "
                         "mesclada contra os fios da coluna do valor, e contra a nota da "
                         "etichetta que enumera culturas"),
        "O_QUE_ISTO_NAO_E": ("nao corrige o numero, nao escolhe entre duas leituras e nao "
                             "inventa o valor certo"),
        "NOTAS_DE_APLICACAO_ENCONTRADAS": sum(
            1 for _ in ()),   # preenchido abaixo
        "COUNTS": dict(sorted(cont.items(), key=lambda kv: -kv[1])),
        "VERDICT_MAX": ver_max,
        "VERDICT_INTERVAL": ver_int,
        "CONTRADICTED": contra,
    }
    saida["NOTAS_DE_APLICACAO_ENCONTRADAS"] = len(
        [c for c in contra if c["FIELD"] == "MAX_APPLICATIONS"
         and c["LABEL_SAYS"] != "VALUE_BELONGS_TO_ANOTHER_ROW"])
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    json.dump(saida, open(a.out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    for k, v in saida["COUNTS"].items():
        print(f"  {v:>5}  {k}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
