#!/usr/bin/env python3
"""FRAC Code List 2026 -> codigo por ingrediente ativo, lido por GEOMETRIA.

A tentativa anterior falhou por dois motivos distintos, e so o segundo era da fonte:

  1. o extrator caseiro perdia glifos ('M 04' saia 'M 0'). Resolvido com pdfminer.six.
  2. o texto plano embaralha as colunas da tabela: a lista de ingredientes e a
     coluna de codigo saem em blocos separados, e casar por ordem de leitura seria
     adivinhar. Resolvido lendo as CAIXAS com coordenadas.

Casar por sobreposicao vertical tambem nao servia: em linha alta o codigo fica
centralizado ABAIXO da lista de nomes e as faixas nao se tocam — foi assim que o
fosetyl-Al ficou de fora na primeira tentativa. A regra final le as REGUAS
HORIZONTAIS que a propria tabela desenha e trata como uma linha tudo que cai entre
a mesma dupla de reguas. E a estrutura que o documento afirma, nao uma heuristica.

Nenhum digito e reconstruido. Ingrediente cuja faixa nao cai dentro de nenhuma
celula de codigo sai de fora, nao sai com palpite.

    ./scripts/adama_it_frac.py            # usa data/raw/FRAC/frac-code-list-2026.pdf
"""
import json
import os
import re
import subprocess
import sys

URL = "https://www.frac.info/media/s1zfrjqa/frac-code-list-2026.pdf"
RAW = "data/raw/FRAC"
PDF = os.path.join(RAW, "frac-code-list-2026.pdf")
OUT = "research/adama-italy-product-intelligence-deep"
UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/126.0 Safari/537.36"

# Colunas medidas na propria tabela (pontos PDF, pagina de 612 de largura).
COL_NOME = (325, 400)
COL_CODIGO = (500, 560)


def baixar():
    os.makedirs(RAW, exist_ok=True)
    if not os.path.exists(PDF):
        subprocess.run(["curl", "-sSL", "-m", "180", "-A", UA, "--retry", "4",
                        "-o", PDF, URL], check=True)
    return PDF


def _sha(caminho):
    import hashlib
    h = hashlib.sha256()
    with open(caminho, "rb") as fh:
        for bloco in iter(lambda: fh.read(1 << 16), b""):
            h.update(bloco)
    return h.hexdigest()


def extrair():
    from pdfminer.high_level import extract_pages
    from pdfminer.layout import LTCurve, LTLine, LTRect, LTTextContainer

    achados, sem_codigo = {}, []
    for n_pag, pagina in enumerate(extract_pages(PDF), start=1):
        nomes, codigos, reguas = [], [], []
        for e in pagina:
            if isinstance(e, (LTLine, LTRect, LTCurve)):
                x0, y0, x1, y1 = e.bbox
                if abs(y1 - y0) < 2 and (x1 - x0) > 200:
                    reguas.append(y0)
                continue
            if not isinstance(e, LTTextContainer):
                continue
            txt = e.get_text()
            if COL_NOME[0] <= e.x0 <= COL_NOME[1]:
                nomes.append((e.y0, e.y1, txt))
            elif COL_CODIGO[0] <= e.x0 <= COL_CODIGO[1]:
                bruto = re.sub(r"\s+", " ", txt).strip()
                # o codigo e curto por natureza: '27', 'M 01', 'U 12', 'P 07', 'NC'
                if re.fullmatch(r"(?:[A-Z]{1,2} ?\d{1,2}|\d{1,2}|NC|[A-Z]{1,2})", bruto):
                    codigos.append((e.y0, e.y1, bruto))

        reguas = sorted(set(round(r, 1) for r in reguas))

        def faixa(y):
            """Entre quais duas reguas desenhadas esta altura cai."""
            abaixo = [r for r in reguas if r <= y]
            acima = [r for r in reguas if r > y]
            return (max(abaixo) if abaixo else None, min(acima) if acima else None)

        for y0, y1, bloco in nomes:
            alvo = faixa((y0 + y1) / 2)
            if alvo == (None, None):
                cand = []
            else:
                cand = [c for c in codigos if faixa((c[0] + c[1]) / 2) == alvo]
            if len(cand) != 1:
                for linha in bloco.splitlines():
                    if linha.strip():
                        sem_codigo.append({"INGREDIENT": linha.strip(), "PAGE": n_pag,
                                           "WHY": "%d celulas de codigo entre as mesmas duas reguas" % len(cand)})
                continue
            codigo = cand[0][2].replace(" ", " ").strip()
            for linha in bloco.splitlines():
                nome = linha.strip()
                if not nome or nome.lower().startswith("(iso)"):
                    continue
                nome = re.sub(r"\s*\((Bactericide|Insecticide|Herbicide|Nematicide)\)\s*$", "", nome).strip()
                if not re.match(r"^[A-Za-z]", nome):
                    continue
                achados.setdefault(nome.upper(), {"FRAC_CODE": codigo, "PAGE": n_pag})
    return achados, sem_codigo


def main():
    baixar()
    achados, sem_codigo = extrair()
    pacote = {
        "SOURCE": "FRAC Code List 2026",
        "SOURCE_URL": URL,
        "SOURCE_VERSION": "FRAC Code List© 2026",
        "SOURCE_CITATION": "FRAC Code List 2026, tabela MOA/TARGET SITE AND CODE, coluna '(ISO) COMMON NAME' x coluna 'FRAC GROUP CODE'",
        "DOCUMENT_SHA256": _sha(PDF),
        "READ_AT": "2026-09-02",
        "METHOD": ("pdfminer.six com coordenadas; a linha da tabela e definida pelas reguas "
                   "horizontais que o proprio PDF desenha, e ingrediente e codigo sao a mesma "
                   "linha quando caem entre a mesma dupla de reguas"),
        "NO_DIGIT_RECONSTRUCTED": True,
        "COUNT": len(achados),
        "INGREDIENTS": achados,
        "NOT_ASSIGNED": sem_codigo,
    }
    os.makedirs(OUT, exist_ok=True)
    caminho = os.path.join(OUT, "MOA-SOURCE-FRAC.json")
    with open(caminho, "w", encoding="utf-8") as fh:
        json.dump(pacote, fh, ensure_ascii=False, indent=2)
    print("FRAC: %d ingredientes com codigo, %d sem -> %s"
          % (len(achados), len(sem_codigo), caminho))
    return pacote


if __name__ == "__main__":
    main()
