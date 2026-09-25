# -*- coding: utf-8 -*-
"""LEGACY-99 v3 · as 41 YouTube pela regua VIDEO/v1 com o que JA esta guardado — sem rede.

Para cada fonte: a pagina /watch mais recente que a Sala guardou (raw_asset, so leitura),
o ficheiro no armazem com o sha256 conferido, as quatro provas da D53 tiradas dele
(canario.retrato_do_video) e a regua (ready_split.passos_da_promocao). Nao promove nada.

Resultado por fonte: PASSARIA / NAO_PASSARIA (a prova que falta) / NAO_SEI (sem pagina
guardada, ficheiro em falta ou sha diferente). E uma estimativa sobre bytes de 20/09: a
promocao a serio e o canario de hoje.

Uso: py ferramentas/legacy99v3/video_com_o_guardado.py --ids <ficheiro,ids> --saida X.json
"""
import hashlib
import json
import os
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ / "curadoria"))
sys.path.insert(0, "C:/rend-fontes/ferramentas/rendimento")
import canario as CAN      # noqa: E402
import ready_split as RS   # noqa: E402
from sala_por_fonte import psql  # noqa: E402

ARMAZEM = Path(os.environ.get("SINTONIA_ARMAZEM_RAIZ") or Path.home() / "sintonia-sala-italia" / "armazem")


def main(argv):
    ids = Path(argv[argv.index("--ids") + 1]).read_text().strip().split(",")
    vivo = Path("C:/Users/London1/orca/workspaces/eame-sintonia/source-curator-service-v1")
    cur = {c["SOURCE_ID"]: c for c in json.loads((vivo / "curadoria/italy_contracts_curator.json")
                                                  .read_text(encoding="utf-8"))["FONTES"]}
    lista = ",".join("'%s'" % i for i in ids)
    linhas = psql("select distinct on (r.source_id) r.source_id, r.source_url, r.captured_at::text, "
                  "s.storage_path, s.sha256 from raw_asset r join storage_object s on s.id = r.storage_object_id "
                  "where r.source_id in (%s) and r.source_url like '%%youtube.com/watch%%' "
                  "order by r.source_id, r.captured_at desc" % lista)
    por = {l[0]: l for l in linhas}
    out = []
    for sid in ids:
        c = cur.get(sid) or {}
        contrato = {"SOURCE_ID": sid, "FORMA": "VIDEO", "OUTPUT_TYPE": "VIDEO",
                    "ACQUISITION": {"STRATEGY": "CUSTOM_ADAPTER", "ADAPTER_ID": "CANAL_PUBLICO_YOUTUBE_V1",
                                    "CHANNEL_ID": (c.get("ACQUISITION") or {}).get("CHANNEL_ID")}}
        l = por.get(sid)
        if not l:
            out.append({"SOURCE_ID": sid, "RESULTADO": "NAO_SEI", "PORQUE": "sem pagina /watch guardada"})
            continue
        _, url, quando, caminho, sha = l
        f = ARMAZEM / caminho
        if not f.exists():
            out.append({"SOURCE_ID": sid, "RESULTADO": "NAO_SEI", "PORQUE": "ficheiro em falta no armazem: " + caminho})
            continue
        b = f.read_bytes()
        if hashlib.sha256(b).hexdigest() != sha:
            out.append({"SOURCE_ID": sid, "RESULTADO": "NAO_SEI", "PORQUE": "sha256 do ficheiro != registado"})
            continue
        item = {"URL": url.split("&")[0], "HTTP": 200, "FORMA": "VIDEO", "COLLECTION_TIME": quando}
        item.update(CAN.retrato_do_video(b))
        r = RS.passos_da_promocao({"OBSERVED_AT": quando}, {"DADOS": {"ITEM_ABERTO": item}}, contrato)
        out.append({"SOURCE_ID": sid, "RESULTADO": "PASSARIA" if r["REGUA"] == RS.REGUA_VIDEO else "NAO_PASSARIA",
                    "FALTA": [k for k, v in r["PASSOS"].items() if not v], "PAGINA": url, "GUARDADA_EM": quando,
                    "TITULO": item.get("TITULO"), "PUBLICATION_TIME": item.get("PUBLICATION_TIME"),
                    "CANAL_NA_PAGINA": item.get("CANAL"), "CANAL_DO_CONTRATO": contrato["ACQUISITION"]["CHANNEL_ID"]})
    from collections import Counter
    d = {"DATASET": "LEGACY-99-V3-VIDEO-COM-O-GUARDADO", "REDE": "nenhuma (Sala so leitura + armazem)",
         "RESUMO": dict(Counter(o["RESULTADO"] for o in out)),
         "FALTAS": dict(Counter(k for o in out for k in o.get("FALTA", []))), "FONTES": out}
    Path(argv[argv.index("--saida") + 1]).write_text(json.dumps(d, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(d["RESUMO"], d["FALTAS"])
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
