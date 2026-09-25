"""LI-ONDA · semear QUALIFY para as candidatas LinkedIn (ou YouTube, `--tipo YOUTUBE`) com identidade provada.

    py curadoria/semear_qualify_social.py                     # só mostra quantas e quais
    py curadoria/semear_qualify_social.py --aplicar --copia   # numa cópia
    py curadoria/semear_qualify_social.py --aplicar --vivo    # no vivo, SÓ com o bot parado (PARAR.flag)

PORQUE ISTO EXISTE (medido no LI-ONDA, 24/09): a ponte (`ponte_candidatas.POLITICA`)
marca toda candidata LinkedIn POLICY_BLOCK e NUNCA lhe enfileira QUALIFY (D15). A D23
abriu o vídeo de página de ORGANIZAÇÃO, e o worker já sabe qualificá-la — mas sem
tarefa na fila nada acontece. Mudar a ponte é mexer na lei da D15 (tem teste de
mutação) e fica para decisão; isto é o degrau mínimo: pôr na fila, UMA vez, as que
têm identidade provada — `/company/<slug>` + o site oficial a apontar para a conta.
O resto (número, contrato, rota) é o worker que faz, pelo caminho de sempre.

Idempotente: `fila.enfileirar` devolve a tarefa aberta que já exista.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
for _p in ("curadoria", "candidatas"):
    sys.path.insert(0, str(RAIZ / _p))

VIVOS = ("source-curator-service-v1", "ponte-viva")
PARAR = RAIZ / "curadoria" / "PARAR.flag"


def identidade(c: dict) -> str | None:
    """O id da plataforma que o QUALIFY vai usar — o mesmo teste, sem fabricar."""
    import rota_do_scrap_social as RSS
    import rota_do_scrap_youtube as RSY
    url = c.get("URL", "")
    if c.get("TIPO") == "LINKEDIN":
        return RSS.slug_linkedin(url)[0]
    if c.get("TIPO") == "YOUTUBE":
        return RSY.channel_id_da_url(url) or RSY.canal_resolvido(c["CANDIDATA_ID"], url)
    return None


def elegiveis(tipo: str = "LINKEDIN") -> list[dict]:
    import fonte_nova as FN
    import rota_do_scrap_youtube as RSY
    out = []
    for c in FN.carregar()["CANDIDATAS"]:
        if c.get("TIPO") != tipo or c.get("SOURCE_ID"):
            continue
        pagina, _ = RSY.ligacao_oficial(c)
        if identidade(c) and pagina:
            out.append(c)
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--aplicar", action="store_true")
    ap.add_argument("--copia", action="store_true")
    ap.add_argument("--vivo", action="store_true")
    ap.add_argument("--tipo", choices=("LINKEDIN", "YOUTUBE"), default="LINKEDIN")
    a = ap.parse_args()
    lista = elegiveis(a.tipo)
    print("candidatas %s com identidade provada e sem SOURCE_ID: %d" % (a.tipo, len(lista)))
    if not a.aplicar:
        for c in lista:
            print("  %s  %s" % (c["CANDIDATA_ID"], c.get("URL")))
        return 0
    no_vivo = any(v in str(RAIZ).replace("\\", "/") for v in VIVOS)
    if no_vivo and not (a.vivo and PARAR.exists()):
        print("RECUSADO: no vivo so com --vivo E o bot parado (%s presente)" % PARAR.name)
        return 2
    if not no_vivo and not a.copia:
        print("RECUSADO: fora do vivo, declare --copia")
        return 2
    import fila as F
    antes = {t["TASK_ID"] for t in F._ler()["TAREFAS"]}
    for c in lista:
        F.enfileirar(c["CANDIDATA_ID"], F.QUALIFY, priority=30,
                     motivo=("LI-ONDA: LinkedIn de organizacao com identidade provada (D23)"
                             if a.tipo == "LINKEDIN" else
                             "YT-ONDA: canal YouTube com identidade provada (D17.4/D21/D36)"))
    novas = [t for t in F._ler()["TAREFAS"] if t["TASK_ID"] not in antes]
    print("tarefas QUALIFY novas: %d (as outras ja estavam abertas)" % len(novas))
    return 0


if __name__ == "__main__":
    sys.exit(main())
