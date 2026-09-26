#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""VOZES-EXECUTAR · colhe a página que prova o PAPEL de cada voz do plano. REDE: só o coordenador corre, com VPN IT.

    cd C:/g/mprova
    py <ramo>/ferramentas/vozes/colher_papel.py --casa=. --plano=<ramo>/data/derivados/VOZES-AGRONOMOS/PLANO-EXECUCAO.json \\
        --ronda=1 --saida=C:/Users/London1/sintonia-sala-italia/vozes-agronomos

Não é rota de coleta: não escreve RAW, não toca a Sala, não enfileira, não escreve em livro nenhum do vivo. Por ficha
da ronda pedida, no MÁXIMO 2 pedidos ao domínio: `robots.txt` (lido e CUMPRIDO, `urllib.robotparser`, agente «*» como a
casa) e o ALVO do plano (a busca do próprio site ou a entrada que já está nos livros). Tudo pelo leitor da casa
(`canario.buscar`: UA, TLS, timeout, teto 4 MB) e o portão de egresso IT por consenso (`rede.portao_de_egresso`) antes
de CADA domínio — sem PASS, 0 pedidos.

Recusa, mesmo que o plano peça (defesa em profundidade): CNR/Coldiretti/ANGA/Unaprol (coordenação 10:13) ·
`reterurale.it` fora da janela 01–03 h UTC (robots Visit-time) e só com `--ronda=NOTURNA-1` · qualquer domínio da
4.ª onda (`--onda4=<rodadas.txt>`; sem o ficheiro, não corre) · mais de 2 pedidos ao mesmo domínio na mesma corrida.

Grava em `--saida`: `<ID>/<n>_<PAPEL>.bin` (os bytes, com sha256 no recibo) e `RECIBO-RONDA-<r>.json`.
"""
from __future__ import annotations

import hashlib
import json
import re
import sys
import time
import urllib.robotparser
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

TETO_POR_DOMINIO = 2
PROIBIDOS = ("cnr.it", "coldiretti.it", "anga.it", "unaprol.it")
NOTURNOS = ("reterurale.it",)
JANELA_NOTURNA_UTC = (1, 3)                 # 01:00 <= hora < 03:00


def _agora() -> str:
    return datetime.now(timezone.utc).isoformat()


def dominio(u: str) -> str:
    return urlparse(u or "").netloc.lower().removeprefix("www.")


def mesmo_site(a: str, b: str) -> bool:
    return a == b or a.endswith("." + b) or b.endswith("." + a)


def dominios_da_onda4(caminho: Path) -> set[str]:
    if not caminho or not Path(caminho).exists():
        raise SystemExit("sem --onda4 (rodadas da 4.a onda): a colisao nao se mede, nao se pede nada")
    return set(re.findall(r"^\s+([a-z0-9.-]+\.[a-z]{2,})\s", Path(caminho).read_text("utf-8"), re.M))


def porque_nao(ficha: dict, ronda: str, onda4: set[str], hora_utc: int) -> str | None:
    """O motivo para NÃO pedir nada desta ficha, ou None."""
    d = dominio(ficha.get("ALVO"))
    if not d:
        return "ficha sem ALVO"
    if any(p == d or d.endswith("." + p) for p in PROIBIDOS):
        return "dominio fechado pela coordenacao (10:13)"
    if any(mesmo_site(d, o) for o in onda4):
        return "dominio da 4.a onda: colisao 0"
    noturno = any(n == d or d.endswith("." + n) for n in NOTURNOS)
    if noturno and not ronda.startswith("NOTURNA"):
        return "reterurale so na ronda NOTURNA"
    if noturno and not (JANELA_NOTURNA_UTC[0] <= hora_utc < JANELA_NOTURNA_UTC[1]):
        return "fora da janela 01-03 h UTC do robots"
    if ronda.startswith("NOTURNA") and not noturno:
        return "a ronda NOTURNA e so para os sites com janela"
    return None


def colher_ficha(ficha: dict, buscar, portao, pasta: Path, contagem: dict, dormir=time.sleep, pausa: float = 3.0) -> dict:
    """`buscar(url)->(status, bytes, erro)` e `portao()->dict` injectados (testável sem rede)."""
    fid, alvo = ficha["ID"], ficha["ALVO"]
    d = dominio(alvo)
    out = {"ID": fid, "PESSOA": ficha.get("PESSOA"), "ALVO": alvo, "MODO": ficha.get("MODO"), "PEDIDOS": 0,
           "PROVAS": [], "COMECOU_EM": _agora()}
    g = portao()
    out["EGRESS_GATE"] = g.get("EGRESS_GATE")
    if g.get("EGRESS_GATE") != "PASS":
        out["PORQUE_PAROU"] = "portao de egresso sem PASS IT: 0 pedidos"
        return out

    def pedir(u):
        if contagem.get(d, 0) >= TETO_POR_DOMINIO:
            return 0, b"", "teto %d/dominio" % TETO_POR_DOMINIO
        if contagem.get(d, 0):
            dormir(pausa)
        contagem[d] = contagem.get(d, 0) + 1
        out["PEDIDOS"] += 1
        return buscar(u)

    def guardar(papel, u, st, b):
        sha = hashlib.sha256(b).hexdigest()
        dest = pasta / fid / ("%d_%s.bin" % (len(out["PROVAS"]), papel))
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(b)
        out["PROVAS"].append({"PAPEL": papel, "URL": u, "HTTP": st, "SHA256": sha, "BYTES": len(b),
                              "LIDO_EM": _agora(), "EGRESSO": "IT", "BYTES_EM": str(dest)})

    p = urlparse(alvo)
    st, txt, err = pedir("%s://%s/robots.txt" % (p.scheme or "https", p.netloc))
    rp = urllib.robotparser.RobotFileParser()
    if st == 200:
        rp.parse(txt.decode("utf-8", "replace").splitlines())
        out["ROBOTS"] = "LIDO"
        guardar("ROBOTS", "%s://%s/robots.txt" % (p.scheme or "https", p.netloc), st, txt)
    elif st == 404:
        rp.parse([])
        out["ROBOTS"] = "404 (nao publica: tudo permitido)"
    else:
        out["ROBOTS"] = "ILEGIVEL (%s)" % (err or st)
        out["PORQUE_PAROU"] = "robots.txt ilegivel: UNKNOWN nao e licenca"
        return out
    if not rp.can_fetch("*", alvo):
        out["PORQUE_PAROU"] = "robots.txt proibe o alvo"
        return out
    st, b, err = pedir(alvo)
    if st == 200 and b:
        guardar("ALVO", alvo, st, b)
    else:
        out["PORQUE_PAROU"] = "alvo nao abriu: %s" % (err or st)
    return out


def correr(plano: dict, ronda: str, buscar, portao, pasta: Path, onda4: set[str], hora_utc: int,
           dormir=time.sleep) -> dict:
    fichas = [f for f in plano["FICHAS"] if f.get("RONDA") == ronda]
    if not fichas:
        raise SystemExit("ronda %r sem fichas no plano" % ronda)
    contagem, feitas, recusadas = {}, [], []
    for f in fichas:
        motivo = porque_nao(f, ronda, onda4, hora_utc)
        if motivo:
            recusadas.append({"ID": f["ID"], "ALVO": f.get("ALVO"), "PORQUE": motivo})
            continue
        feitas.append(colher_ficha(f, buscar, portao, pasta, contagem, dormir=dormir))
    return {"DATASET": "VOZES-RECIBO", "RONDA": ronda, "GERADO_EM": _agora(),
            "PEDIDOS": sum(x["PEDIDOS"] for x in feitas), "PEDIDOS_POR_DOMINIO": contagem,
            "COLHIDAS": feitas, "RECUSADAS": recusadas}


def main(argv=None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    a = dict(x[2:].split("=", 1) for x in argv if x.startswith("--") and "=" in x)
    for k in ("casa", "plano", "ronda", "saida", "onda4"):
        if not a.get(k):
            print(__doc__)
            return 2
    casa = Path(a["casa"]).resolve()
    sys.path[:0] = [str(casa / "curadoria"), str(casa / "superficie")]
    import canario as CAN      # noqa: E402  — o leitor da casa
    import rede                # noqa: E402  — o portão de egresso
    pasta = Path(a["saida"])
    pasta.mkdir(parents=True, exist_ok=True)
    rec = correr(json.loads(Path(a["plano"]).read_text("utf-8")), a["ronda"], CAN.buscar,
                 lambda: rede.portao_de_egresso("IT"), pasta, dominios_da_onda4(Path(a["onda4"])),
                 datetime.now(timezone.utc).hour)
    destino = pasta / ("RECIBO-RONDA-%s.json" % a["ronda"])
    destino.write_text(json.dumps(rec, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(json.dumps({k: rec[k] for k in ("RONDA", "PEDIDOS", "PEDIDOS_POR_DOMINIO")}, ensure_ascii=False))
    print("recusadas:", [(r["ID"], r["PORQUE"]) for r in rec["RECUSADAS"]])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
