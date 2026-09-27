"""FEED-MEDIR · as 14 fontes com feed, cruzadas com os livros das ultimas 24 h: LIVRE_AGORA ou ABRE_EM. So leitura.

    py provas/scrap_evolucao/feeds_janela.py --livros=C:/Users/London1/sintonia-sala-italia/ondas \
        [--recibos=<pasta,pasta>] [--agora=2026-09-26T22:30-03:00] [--saida=JANELA-FEEDS.json]

A MESMA regra das rodadas (`ferramentas/big_collection/rodadas.py`, D79): cada `TETO-ONDA.json` debaixo de
--livros (instante por fonte a partir do RUN_ID + SEGUNDOS, quando ha ONDA-WEB-ESTADO) e cada `RECIBO*.json`
debaixo de --recibos. Um dominio pedido ha menos de 24 h esta FECHADO ate ultima visita + 24 h.

Diz tambem QUAL livro fechou o dominio, para se conferir a mao. Nao ve o que nao deixou livro nem recibo:
uma corrida com rede sem TETO-ONDA/RECIBO e invisivel aqui (e para as rodadas).
"""
import json
import os
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.parse import urlsplit

RAIZ = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(RAIZ, "ferramentas", "big_collection"))
sys.path.insert(0, os.path.join(RAIZ, "provas"))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import medir_feeds_com_rede as M  # noqa: E402
import rodadas as R               # noqa: E402

BRASILIA = timezone(timedelta(hours=-3))


def janela(livros: Path, recibos: tuple = (), agora: datetime | None = None, horas: int = 24) -> dict:
    agora = agora or datetime.now(timezone.utc)
    # por livro, para dizer quem fechou; a ultima visita e o maximo de todos (igual a ultima_visita_por_dominio)
    fontes_de_prova = [(str(l.relative_to(livros)), R.ultima_visita_por_dominio(l.parent))
                       for l in sorted(Path(livros).glob("**/TETO-ONDA.json"))]
    fontes_de_prova += [(str(p), R.ultima_visita_por_dominio(Path(livros) / "__nenhum__", (Path(p),))) for p in recibos]
    geral = R.ultima_visita_por_dominio(Path(livros), tuple(Path(p) for p in recibos))
    out = {}
    for sid, feed in sorted(M.feeds().items()):
        d = R.PT.dominio_registavel(urlsplit(feed).hostname or "")
        t = geral.get(d)
        quem = next((n for n, u in fontes_de_prova if t and u.get(d) == t), None)
        fecha = t + timedelta(hours=horas) if t else None
        livre = not fecha or agora >= fecha
        out[sid] = {"FEED": feed, "DOMINIO": d, "ESTADO": "LIVRE_AGORA" if livre else "FECHADO",
                    "ULTIMA_VISITA": t.astimezone(BRASILIA).isoformat(timespec="minutes") if t else None,
                    "ABRE_EM": None if livre else fecha.astimezone(BRASILIA).isoformat(timespec="minutes"),
                    "QUEM_PEDIU": quem}
    return out


def main(argv=None):
    a = dict(x[2:].split("=", 1) for x in (sys.argv[1:] if argv is None else argv) if x.startswith("--") and "=" in x)
    if "livros" not in a:
        print(__doc__)
        return 2
    agora = datetime.fromisoformat(a["agora"]).astimezone(timezone.utc) if a.get("agora") else None
    r = janela(Path(a["livros"]), tuple(x for x in a.get("recibos", "").split(",") if x), agora)
    for sid, x in r.items():
        print("%-11s %-28s %-12s %s   (ultima %s · %s)" % (sid, x["DOMINIO"], x["ESTADO"],
              "ABRE_EM " + x["ABRE_EM"] if x["ABRE_EM"] else "", x["ULTIMA_VISITA"] or "nenhuma", x["QUEM_PEDIU"] or "-"))
    livres = [s for s, x in r.items() if x["ESTADO"] == "LIVRE_AGORA"]
    print("LIVRE_AGORA %d/%d: %s" % (len(livres), len(r), ",".join(livres)))
    if a.get("saida"):
        with open(a["saida"], "w", encoding="utf-8") as f:
            json.dump(r, f, ensure_ascii=False, indent=1)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
