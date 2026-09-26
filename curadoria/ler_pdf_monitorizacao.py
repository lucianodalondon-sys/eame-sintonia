#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""LER PDF DE MONITORIZACAO — o SINAL PRECOCE dentro dos boletins/relatorios em PDF, SEM RESUMIR.
(LOTE-MONITORIZACAO, 26/09: a sonda achou os PDFs; este leitor tira as linhas.)

Nao e rota de coleta: nao escreve RAW, nao toca a Sala, nao regista nada. 1 pedido por PDF; por dominio no MAXIMO 5
pedidos (teto D38, contando o robots.txt), robots lido e CUMPRIDO, portao IT antes de cada dominio. Bytes do PDF e o
TEXTO INTEGRAL (`pdftotext -layout`, o mesmo utensilio da casa: coleta/executor_texto_de_pdf.py) ficam fora do Git
com sha256.

    py curadoria/ler_pdf_monitorizacao.py --lote=<PDFS.json> --bytes=<pasta fora do Git> --saida=<LINHAS.json>

Por PDF devolve TODAS as linhas com sinal (nenhuma e cortada nem resumida — `LINHA` e o texto tal como saiu):
  - CONTAGEM: numero + unidade de monitorizacao (catture, adulti, larve, uova, individui, esemplari, ovideposizioni...);
  - PERCENTAGEM: % de infestacao/attacco/frutti colpiti/punture/germogli;
  - LIMIAR: «soglia»; VOO: volo/voli/sfarfallamento/inizio del volo; TABELA: linha com >= 2 numeros ao lado de uma
    palavra de local/armadilha/praga (a linha de uma tabela em -layout).
Cada linha leva: DATA (da linha, senao a mais recente do documento), LOCAL (o texto antes do 1.o numero), NUMEROS,
PRAGA (na linha, senao o ultimo cabecalho com praga), CULTURA (do nome do PDF/ancora) e NUMERO_DA_LINHA.
"""
from __future__ import annotations

import hashlib
import json
import re
import shutil
import subprocess
import sys
import time
import urllib.robotparser
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
import colher_prova_territorio as CPT   # noqa: E402  (datas)
import medir_contagens as MC            # noqa: E402  (pragas, culturas)

TETO = 5
UNIDADE = re.compile(r"(\d{1,6}(?:[.,]\d+)?)\s*(catture|adulti|adulto|larve|larva|uova|individui|esemplari|"
                     r"ovideposizioni|femmine|maschi|punture|capture|forme mobili|neanidi|ninfe)\b", re.I)
PCT = re.compile(r"\d{1,3}(?:[.,]\d+)?\s*%", re.I)
PCT_CONTEXTO = re.compile(r"infestaz|attacc|colpit|puntur|germogl|frutti|olive|drupe|grappol|foglie|piante", re.I)
LIMIAR = re.compile(r"soglia", re.I)
VOO = re.compile(r"\bvol[oi]\b|sfarfallament\w*|inizio (del )?volo|picco di volo|curva di volo", re.I)
LOCAL_OU_ARMADILHA = re.compile(r"trappol\w*|stazion\w*|localit\w*|zona|comune|azienda|punto|sito|areale|provincia", re.I)
# morada/contacto nunca e linha de tabela (via, piazza, telefone, CAP de 5 algarismos, e-mail, P.IVA)
ENDERECO = re.compile(r"\b(via|viale|piazza|piazzale|corso|loc\.|tel\.?|telefono|fax|pec|e-?mail|www\.|p\.? ?iva|c\.f\.)(?=\W)"
                      r"|@|(?<!\d)\d{5}(?!\d)", re.I)
NUM = re.compile(r"(?<![\w/])\d{1,6}(?:[.,]\d+)?(?![\w/])")


def texto_do_pdf(pdf: Path) -> str:
    """`pdftotext -layout`: as colunas das tabelas ficam no sitio. Sem a ferramenta, falha alto (nunca vazio calado)."""
    if not shutil.which("pdftotext"):
        raise RuntimeError("pdftotext ausente nesta maquina")
    r = subprocess.run(["pdftotext", "-layout", "-enc", "UTF-8", str(pdf), "-"], capture_output=True, timeout=120)
    if r.returncode != 0:
        raise RuntimeError("pdftotext falhou: %s" % r.stderr.decode("utf-8", "replace")[:200])
    return r.stdout.decode("utf-8", "replace")


def linhas_com_sinal(texto: str, cultura: str | None = None) -> list[dict]:
    """TODAS as linhas com sinal precoce, tal como estao. Nada e resumido."""
    linhas = texto.splitlines()
    datas_doc = sorted("%04d-%02d-%02d" % d for d in CPT._datas(texto) if 1990 <= d[0] and 1 <= d[1] <= 12 and 1 <= d[2] <= 31)
    praga_atual, out = None, []
    for i, l in enumerate(linhas, 1):
        s = l.strip()
        if not s:
            continue
        pr = MC.PRAGAS.search(s)
        if pr:
            praga_atual = pr.group(0)                   # a ultima praga citada vale para as linhas seguintes (tabela)
        tipos = []
        if UNIDADE.search(s):
            tipos.append("CONTAGEM")
        if PCT.search(s) and PCT_CONTEXTO.search(s):
            tipos.append("PERCENTAGEM")
        if LIMIAR.search(s):
            tipos.append("LIMIAR")
        if VOO.search(s):
            tipos.append("VOO")
        nums = NUM.findall(s)
        if len(nums) >= 2 and (LOCAL_OU_ARMADILHA.search(s) or MC.PRAGAS.search(s) or praga_atual) and \
                re.search(r"[A-Za-zÀ-ÿ]{3,}", s) and not ENDERECO.search(s):
            tipos.append("TABELA")
        if not tipos:
            continue
        ds = ["%04d-%02d-%02d" % d for d in CPT._datas(s) if 1990 <= d[0]]
        primeiro = NUM.search(s)
        out.append({"NUMERO_DA_LINHA": i, "TIPOS": tipos, "LINHA": l.rstrip(),
                    "DATA": ds[-1] if ds else (datas_doc[-1] if datas_doc else None),
                    "DATA_DE_ONDE": "linha" if ds else ("documento" if datas_doc else None),
                    "LOCAL": s[:primeiro.start()].strip(" :-|") if primeiro else None,
                    "NUMEROS": nums,
                    "PRAGA": (pr.group(0) if pr else praga_atual),
                    "CULTURA": cultura})
    return out


def ler(alvo: dict, buscar, pasta: Path, extrair=texto_do_pdf) -> dict:
    """Um PDF ja autorizado (robots/portao/teto decididos por `correr`)."""
    st, b, err = buscar(alvo["URL"])
    out = {**{k: alvo.get(k) for k in ("ID", "SOURCE_ID", "REGIAO", "URL", "ANCORA", "CULTURA")}, "HTTP": st}
    if st != 200 or not b:
        return {**out, "ESTADO": "NAO_ABRIU", "PORQUE": str(err or st)}
    if b.lstrip()[:5] != b"%PDF-":
        return {**out, "ESTADO": "NAO_E_PDF", "PORQUE": "os bytes nao comecam por %PDF- (pagina HTML ou erro)",
                "BYTES": len(b)}
    dest = pasta / (alvo["ID"] + ".pdf")
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(b)
    try:
        texto = extrair(dest)
    except Exception as e:  # noqa: BLE001
        return {**out, "ESTADO": "SEM_TEXTO", "PORQUE": str(e)[:200], "SHA256": hashlib.sha256(b).hexdigest()}
    txt = dest.with_suffix(".txt")
    txt.write_text(texto, encoding="utf-8")
    linhas = linhas_com_sinal(texto, alvo.get("CULTURA"))
    return {**out, "ESTADO": "LIDO" if texto.strip() else "PDF_SEM_TEXTO (imagem? precisa OCR)",
            "SHA256": hashlib.sha256(b).hexdigest(), "BYTES": len(b), "BYTES_EM": str(dest),
            "TEXTO_INTEGRAL_EM": str(txt), "TEXTO_SHA256": hashlib.sha256(texto.encode("utf-8")).hexdigest(),
            "LINHAS_DO_TEXTO": len(texto.splitlines()),
            "POR_TIPO": {t: sum(1 for x in linhas if t in x["TIPOS"]) for t in ("CONTAGEM", "PERCENTAGEM", "LIMIAR", "VOO", "TABELA")},
            "LINHAS_COM_SINAL": linhas}


def correr(alvos: list[dict], buscar, portao, pasta: Path, dormir=time.sleep, pausa: float = 3.0) -> list[dict]:
    """Agrupa por dominio: portao, robots (1 pedido), e no maximo TETO-1 PDFs por dominio."""
    por_dom: dict[str, list] = {}
    for a in alvos:
        por_dom.setdefault(urlparse(a["URL"]).netloc.lower().removeprefix("www."), []).append(a)
    res = []
    for dom, lista in por_dom.items():
        g = portao()
        if g.get("EGRESS_GATE") != "PASS":
            res += [{**a, "ESTADO": "NAO_PEDIDO", "PORQUE": "portao sem PASS IT"} for a in lista]
            continue
        p = urlparse(lista[0]["URL"])
        st, txt, err = buscar("%s://%s/robots.txt" % (p.scheme or "https", p.netloc))
        rp = urllib.robotparser.RobotFileParser()
        if st == 200:
            rp.parse(txt.decode("utf-8", "replace").splitlines())
        elif st == 404:
            rp.parse([])
        else:
            res += [{**a, "ESTADO": "NAO_PEDIDO", "PORQUE": "robots ilegivel (%s)" % (err or st)} for a in lista]
            continue
        pedidos = 1
        for a in lista:
            if pedidos >= TETO:
                res.append({**a, "ESTADO": "NAO_PEDIDO", "PORQUE": "teto D38 (%d pedidos a %s)" % (TETO, dom)})
                continue
            if not rp.can_fetch("*", a["URL"]):
                res.append({**a, "ESTADO": "NAO_PEDIDO", "PORQUE": "robots.txt proibe"})
                continue
            dormir(pausa)
            pedidos += 1
            res.append(ler(a, buscar, pasta))
    return res


def main(argv=None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    a = dict(x[2:].split("=", 1) for x in argv if x.startswith("--") and "=" in x)
    if not a.get("lote") or not a.get("bytes"):
        print(__doc__)
        return 2
    import canario as CAN      # noqa: E402
    import rede                # noqa: E402
    lote = json.loads(Path(a["lote"]).read_text(encoding="utf-8"))
    res = correr(lote["PDFS"], CAN.buscar, lambda: rede.portao_de_egresso("IT"), Path(a["bytes"]))
    out = {"DATASET": "LINHAS-DE-MONITORIZACAO", "GERADO_EM": datetime.now(timezone.utc).isoformat(),
           "PEDIDOS_PDF": sum(1 for r in res if r.get("HTTP") is not None),
           "POR_ESTADO": {e: sum(1 for r in res if r.get("ESTADO") == e) for e in sorted({r.get("ESTADO") for r in res})},
           "PDFS": res}
    Path(a.get("saida", "LINHAS-DE-MONITORIZACAO.json")).write_text(json.dumps(out, ensure_ascii=False, indent=1) + "\n",
                                                                     encoding="utf-8")
    print(json.dumps({k: out[k] for k in ("PEDIDOS_PDF", "POR_ESTADO")}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
