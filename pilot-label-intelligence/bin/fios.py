#!/usr/bin/env python3
"""
fios.py — encontra os FIOS DESENHADOS da tabela na etichetta.

Por que isto importa mais do que parece. Duas leituras da mesma tabela discordam
sobre celula mesclada: uma espalha o valor pelas linhas que a celula cobre, a
outra recusa por nao conseguir provar a mescla. As duas estao certas dentro do
que enxergam — `pdftotext -bbox-layout` da a caixa de cada PALAVRA e nao da os
FIOS, entao a mescla so podia ser inferida.

Mas os fios existem no documento: no PDF do registro 015275 sao 373 retangulos
longos e finos (0,7 pt), que e como um gerador de PDF desenha a grade. Com eles a
mescla deixa de ser inferencia e vira leitura: **duas linhas de texto estao na
mesma celula quando nenhum fio horizontal passa entre elas.**

Como sao lidos: a pagina e rasterizada com `pdftoppm -gray` e os fios saem por
contagem de pixel escuro. E de proposito nao ler o content stream do PDF — ali os
retangulos vem em coordenadas locais, sujeitas a matriz de transformacao, e uma
etichetta com `cm` no lugar errado daria fio deslocado sem avisar. O raster e o
que o leitor humano ve, que e o mesmo criterio do gabarito feito a mao.

Devolve as coordenadas ja no espaco do `-bbox-layout` (origem no topo, em pontos),
para casar direto com as palavras.

## O detalhe que faz a coisa funcionar: o fio tem inicio e fim

Uma celula mesclada nao e "sem fio entre as linhas". E **sem fio NAQUELA COLUNA**.
Na tabela do 015275, entre as linhas de alvo do Agrumi existe fio — mas ele para
na borda da coluna de cultura, e e exatamente por isso que a celula de cultura
cobre os tres alvos. Um fio lido como uma altura, sem inicio e fim, nao distingue
os dois casos e responde sempre "celulas diferentes".

Por isso cada fio horizontal e guardado como SEGMENTO (y, x_inicio, x_fim), e a
pergunta e sempre feita com a faixa x da coluna junto.
"""
import argparse, json, os, subprocess, sys, tempfile


def _pgm(path):
    """Le PGM binario (P5) da stdlib. Devolve (largura, altura, bytes)."""
    with open(path, "rb") as fh:
        b = fh.read()
    if not b.startswith(b"P5"):
        raise ValueError("esperado PGM binario P5")
    campos, i = [], 2
    while len(campos) < 3:
        while i < len(b) and b[i:i + 1].isspace():
            i += 1
        if b[i:i + 1] == b"#":
            while i < len(b) and b[i] != 0x0A:
                i += 1
            continue
        j = i
        while j < len(b) and not b[j:j + 1].isspace():
            j += 1
        campos.append(int(b[i:j])); i = j
    i += 1
    w, h, _ = campos
    return w, h, b[i:i + w * h]


def fios(pdf, pagina, dpi=150, escuro=128, minimo_pt=60.0, cache=None):
    """Fios horizontais e verticais da pagina, em pontos, origem no topo.

    Um fio e uma CORRIDA CONTINUA de pixel escuro, nao uma fracao da pagina.
    Medir fracao confunde texto denso com fio: numa etichetta cheia, uma coluna
    de texto tem tanto pixel escuro quanto um fio, so que picotado. A corrida
    contigua separa os dois sem depender de limiar fino.
    """
    tmpd = cache or tempfile.mkdtemp()
    pref = os.path.join(tmpd, f"p{pagina}")
    alvo = f"{pref}-{pagina}.pgm"
    if not os.path.exists(alvo):
        subprocess.run(["pdftoppm", "-gray", "-r", str(dpi),
                        "-f", str(pagina), "-l", str(pagina), pdf, pref],
                       check=True, capture_output=True)
        cand = [f for f in os.listdir(tmpd)
                if f.startswith(os.path.basename(pref)) and f.endswith(".pgm")]
        if not cand:
            return {"H": [], "V": [], "STATE": "RENDER_FAILED"}
        alvo = os.path.join(tmpd, sorted(cand)[0])
    w, h, px = _pgm(alvo)
    esc = 72.0 / dpi                                  # pixel -> ponto

    minpx = int(minimo_pt * dpi / 72.0)

    def maior_corrida(vals, falha_ok=2):
        """Maior sequencia de escuros, tolerando pequenas falhas de anti-aliasing."""
        melhor = atual = falhas = 0
        for v in vals:
            if v:
                atual += 1; falhas = 0
            else:
                falhas += 1
                if falhas > falha_ok:
                    melhor = max(melhor, atual); atual = 0
                else:
                    atual += 1
        return max(melhor, atual)

    def corridas(vals, minimo):
        """[(inicio, fim)] das corridas continuas de escuro com tamanho minimo."""
        out, ini = [], None
        for i, v in enumerate(vals):
            if v and ini is None:
                ini = i
            elif not v and ini is not None:
                if i - ini >= minimo:
                    out.append((ini, i))
                ini = None
        if ini is not None and len(vals) - ini >= minimo:
            out.append((ini, len(vals)))
        return out

    segs = []
    for y in range(h):
        base = y * w
        linha = [px[base + x] < escuro for x in range(w)]
        for a, b in corridas(linha, minpx):
            segs.append((y, a, b))
    vert = []
    for x in range(w):
        coluna = [px[y * w + x] < escuro for y in range(h)]
        if any(b - a >= minpx for a, b in corridas(coluna, minpx)):
            vert.append(x)
    horiz = sorted({y for y, _, _ in segs})

    def agrupa(vals):
        out, cur = [], []
        for v in vals:
            if cur and v - cur[-1] > 2:
                out.append(sum(cur) / len(cur)); cur = []
            cur.append(v)
        if cur:
            out.append(sum(cur) / len(cur))
        return [round(v * esc, 2) for v in out]

    # segmentos agrupados por altura, ja em pontos
    porY = {}
    for y, a, b in segs:
        porY.setdefault(y, []).append((a, b))
    SEG = []
    for y in sorted(porY):
        for a, b in porY[y]:
            SEG.append((round(y * esc, 2), round(a * esc, 2), round(b * esc, 2)))
    return {"H": agrupa(horiz), "V": agrupa(vert), "SEG": SEG, "STATE": "READ",
            "PAGE_WIDTH_PT": round(w * esc, 2), "PAGE_HEIGHT_PT": round(h * esc, 2)}


def mesma_celula(y0, y1, x0, x1, segmentos, folga=1.0, cobre=0.6):
    """Mesma celula = nenhum fio ATRAVESSA a coluna [x0,x1] entre y0 e y1.

    `cobre` e a fracao da largura da coluna que o fio precisa cruzar para contar
    como separador. Um fio que so encosta na borda nao separa nada.
    """
    a, b = (y0, y1) if y0 <= y1 else (y1, y0)
    larg = max(x1 - x0, 1e-6)
    for y, xa, xb in segmentos:
        if not (a + folga < y < b - folga):
            continue
        inter = min(x1, xb) - max(x0, xa)
        if inter / larg >= cobre:
            return False
    return True


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("pdf")
    ap.add_argument("--pagina", type=int, default=1)
    ap.add_argument("--dpi", type=int, default=150)
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    r = fios(a.pdf, a.pagina, a.dpi)
    if a.json:
        json.dump(r, sys.stdout, ensure_ascii=False, indent=1)
    else:
        print(f'pagina {a.pagina}: {len(r["H"])} fios horizontais, '
              f'{len(r["V"])} verticais  ({r["STATE"]})')
        print("  H:", ", ".join(f"{v:.0f}" for v in r["H"][:24]))
        print("  V:", ", ".join(f"{v:.0f}" for v in r["V"][:24]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
