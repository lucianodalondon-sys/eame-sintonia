"""SOC2 · ENSAIO DO QUALIFY NAS CANDIDATAS YOUTUBE — sem escrever na lane real.

    py curadoria/ensaiar_qualify_youtube.py            # ensaio: tudo em pasta temporaria
    py curadoria/ensaiar_qualify_youtube.py --reabrir  # reabre as QUALIFY barradas pelo
                                                       # bloqueio antigo, na fila REAL

O ensaio corre a etapa QUALIFY do worker (a real, sem copia) sobre cada candidata
YouTube da porta, com a fila, o livro de estado, o registo de alocacao e a
evidencia redirecionados para uma pasta temporaria. Le a porta de candidatas,
os contratos e o Scrap como estao; nao escreve em nenhum deles.

`--reabrir` e o unico verbo que toca a lane: devolve a PENDING as tarefas QUALIFY
que o worker barrou com a frase do bloqueio antigo («YouTube exige channel_id e
molde de video»), pela porta da propria fila (`recuperar_bloqueadas_por_defeito`).
Correr so no cutover, com o servico parado ou pelo dono do servico.
"""
from __future__ import annotations

import json
import sys
import tempfile
from collections import Counter
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "curadoria"))
sys.path.insert(0, str(RAIZ / "candidatas"))

import fila as F  # noqa: E402
import fonte_nova as FN  # noqa: E402
import lifecycle as LC  # noqa: E402
import rota_do_scrap_youtube as RSY  # noqa: E402
import worker as W  # noqa: E402

ASSINATURA_ANTIGA = "YouTube exige channel_id e molde de video"


def ensaiar() -> list[dict]:
    cands = [c for c in FN.carregar()["CANDIDATAS"] if c.get("TIPO") == "YOUTUBE"]
    orig = (F.FILA, LC.LIVRO, W.ALLOCATION, W.EVIDENCIA, W.PULSO)
    with tempfile.TemporaryDirectory(prefix="soc2-qualify-") as tmp:
        t = Path(tmp)
        alloc = W._ler_alloc()
        F.FILA, LC.LIVRO, W.EVIDENCIA, W.PULSO = (t / "fila.json", t / "livro.json",
                                                  t / "evid.json", t / "pulso.json")
        W.ALLOCATION = t / "alloc.json"
        W.ALLOCATION.write_text(json.dumps(alloc, ensure_ascii=False), encoding="utf-8")
        try:
            out = []
            for c in cands:
                res, det = W.etapa_qualify(c["CANDIDATA_ID"], None)
                out.append({"CANDIDATA_ID": c["CANDIDATA_ID"], "NOME": c.get("NOME", "")[:60],
                            "URL": c.get("URL"), "CHANNEL_ID": RSY.channel_id_da_url(c.get("URL", "")),
                            "RESULTADO": res, "CLASSE": det.get("CLASSE"),
                            "SOURCE_ID": det.get("SOURCE_ID_REAL"),
                            "JA_TINHA_IDENTIDADE": det.get("JA_TINHA_IDENTIDADE", False),
                            "PORQUE": (det.get("PORQUE") or "")[:200]})
            return out
        finally:
            F.FILA, LC.LIVRO, W.ALLOCATION, W.EVIDENCIA, W.PULSO = orig


def reabrir() -> list[dict]:
    return F.recuperar_bloqueadas_por_defeito([ASSINATURA_ANTIGA], task_types={F.QUALIFY})


def main(argv=None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    if "--reabrir" in argv:
        mex = reabrir()
        print("REABERTAS", len(mex))
        return 0
    linhas = ensaiar()
    for l in linhas:
        print("%-6s %-10s %-9s %-10s %-24s %s" % (l["RESULTADO"], l["CLASSE"] or "", l["CANDIDATA_ID"],
                                              l["SOURCE_ID"] or "", l["CHANNEL_ID"] or "—", l["PORQUE"][:70]))
    print("RESUMO", dict(Counter((l["RESULTADO"], l["CLASSE"] or ("JA_TEM_SOURCE_ID" if l["JA_TINHA_IDENTIDADE"] else ""))
                                 for l in linhas)), "de", len(linhas))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
