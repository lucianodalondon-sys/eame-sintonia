# -*- coding: utf-8 -*-
"""PEDIDO-API-125 · os metadados dos 125 videos dos 9 canais de pesquisa, pela API oficial (videos.list).

    py ferramentas/primeira_volta_video/pedido_api_125.py --canais=PESQUISA-9.json --plano=PEDIDO-API-125.json
    py ferramentas/primeira_volta_video/pedido_api_125.py --canais=PESQUISA-9.json --seco [--saida=SECO.json]

`--plano` escreve o pedido: uma corrida por canal (o recibo tem UM SOURCE_ID: misturar canais num
pedido atribuiria videos a fonte errada), com a fase `video-youtube`, o universo e a frase do pedido
pelo territorio da fonte, e o comando exacto do workflow.

`--seco` corre o codigo VERDADEIRO do Scrap (`scrap_colheita.colher('video-youtube', ...)`) numa copia,
SEM rede e SEM chave real: chave falsa so neste processo, transporte da API trocado por respostas
literais que contam cada pedido, proxy fechado para o resto. Passa a lista EXACTAMENTE como o workflow
a entrega (texto separado por virgulas, `--filtro videos='a,b,c'`) e diz quantos pedidos saem, para que
host, com que IDs, e se o prazo D20 vem escrito nos itens.
"""
import json
import os
import sys
import urllib.parse
from collections import Counter
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]

# territorio da fonte -> (universo da Admissao, apelido do pedido) — os apelidos sao os de
# `leis/territorios.APELIDOS` (T5: «ciencia»; T7: «cooperativas»), nunca inventados aqui
PEDIDO_POR_TERRITORIO = {"T5": ("T5", "colete ciencia"), "T7": ("T7", "colete cooperativas"),
                         "T8": ("T8", "colete agricultores"), "T9": ("T9", "colete concorrentes")}


def plano(canais: list) -> dict:
    corridas = []
    for c in canais:
        t = c["SOURCE_ID"].split("-")[1]
        universo, frase = PEDIDO_POR_TERRITORIO[t]
        vids = ",".join(c["VIDEO_IDS"])
        corridas.append({
            "SOURCE_ID": c["SOURCE_ID"], "NOME": c["NOME"], "VIDEOS": len(c["VIDEO_IDS"]),
            "CHAMADAS_VIDEOS_LIST": -(-len(c["VIDEO_IDS"]) // 50), "UNIVERSO": universo, "FRASE": frase,
            "WORKFLOW": ("gh workflow run sintonia-scrap.yml --ref <ramo do vivo> -f fase=video-youtube "
                         "-f fonte=%s -f videos=%s -f runner=1" % (c["SOURCE_ID"], vids)),
            "ORQUESTRADOR": ("py orquestrador/orquestrador.py \"%s\" --filtro fase=video-youtube --filtro fonte=%s "
                             "--filtro pais=IT --filtro universo=%s --filtro videos='%s'" % (frase, c["SOURCE_ID"], universo, vids)),
        })
    return {"DATASET": "PEDIDO-API-125", "CORRIDAS": corridas,
            "TOTAL_VIDEOS": sum(x["VIDEOS"] for x in corridas),
            "TOTAL_CHAMADAS_VIDEOS_LIST": sum(x["CHAMADAS_VIDEOS_LIST"] for x in corridas),
            "QUOTA_UNIDADES": sum(x["CHAMADAS_VIDEOS_LIST"] for x in corridas),
            "PEDIDOS_YOUTUBE_COM": 0}


def seco(canais: list) -> list:
    if "source-curator-service-v1" in str(RAIZ).replace("\\", "/"):
        sys.exit("RECUSADO: isto e a arvore do bot vivo")
    for v in ("HTTP_PROXY", "HTTPS_PROXY", "http_proxy", "https_proxy"):
        os.environ[v] = "http://127.0.0.1:9"
    os.environ["YOUTUBE_DATA_API_KEY"] = "SECO-SEM-CHAVE"
    for p in ("coleta", "leis", "admissao", "regras", "ferramentas", "medidas", "guarda", "pedido",
              "orquestrador", "curadoria", ""):
        sys.path.insert(0, str(RAIZ / p) if p else str(RAIZ))
    import youtube_oficial as yt      # noqa: E402
    import scrap_colheita as sc       # noqa: E402
    out = []
    for c in canais:
        pedidos = []

        def _http(url, c=c, pedidos=pedidos):
            u = urllib.parse.urlparse(url)
            q = urllib.parse.parse_qs(u.query)
            ids = (q.get("id") or [""])[0].split(",")
            pedidos.append({"HOST": u.hostname, "METODO": u.path.rsplit("/", 1)[-1], "IDS": ids})
            return {"items": [{"id": i, "snippet": {"channelId": c["CHANNEL_ID"], "channelTitle": c["NOME"],
                                                    "title": "titulo %s" % i, "description": "descricao",
                                                    "publishedAt": "2026-05-01T10:00:00Z"},
                               "contentDetails": {"duration": "PT12M3S"}, "statistics": {}, "status": {}}
                              for i in ids if len(i) == 11]}
        yt._http = _http
        env = sc.colher("video-youtube", run_id="SECO-API-%s" % c["SOURCE_ID"], fonte=c["SOURCE_ID"],
                        video_ids=",".join(c["VIDEO_IDS"]))          # como o workflow entrega: TEXTO
        col = env.get("COLHEITA") or []
        ob0 = (col[0].get("OBSERVACAO") or {}) if col else {}
        pedidos_ids = [i for p in pedidos for i in p["IDS"]]
        out.append({"SOURCE_ID": c["SOURCE_ID"], "PEDIDOS": len(pedidos),
                    "POR_HOST": dict(Counter(p["HOST"] for p in pedidos)),
                    "IDS_PEDIDOS": len(pedidos_ids), "IDS_DE_11_CARACTERES": sum(len(i) == 11 for i in pedidos_ids),
                    "IDS_ESPERADOS": len(c["VIDEO_IDS"]),
                    "AMOSTRA_DO_ID_PEDIDO": pedidos_ids[:3],
                    "COLHEITA": len(col), "ESTADO": env.get("ESTADO"),
                    "SOURCE_ID_DO_PEDIDO": env.get("SOURCE_ID_DO_PEDIDO"),
                    "D20_PRAZO": ob0.get("RETENTION_POLICY"), "D20_DIAS": ob0.get("RETENTION_DAYS"),
                    "PORQUE_ZERO": (env.get("PORQUE_ZERO_COLHEITA") or "")[:160]})
    return out


def main(argv) -> int:
    arg = dict(a[2:].split("=", 1) for a in argv[1:] if a.startswith("--") and "=" in a)
    canais = json.loads(Path(arg["canais"]).read_text(encoding="utf-8"))
    if "plano" in arg:
        p = plano(canais)
        Path(arg["plano"]).write_text(json.dumps(p, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
        print({k: v for k, v in p.items() if k != "CORRIDAS"})
    if "--seco" in argv:
        r = seco(canais)
        for x in r:
            print(x["SOURCE_ID"], "pedidos", x["PEDIDOS"], x["POR_HOST"], "ids pedidos", x["IDS_PEDIDOS"],
                  "de 11 car.", x["IDS_DE_11_CARACTERES"], "esperados", x["IDS_ESPERADOS"], "amostra", x["AMOSTRA_DO_ID_PEDIDO"],
                  "colheita", x["COLHEITA"], "D20", x["D20_PRAZO"], x["D20_DIAS"])
        if "saida" in arg:
            Path(arg["saida"]).write_text(json.dumps({"DATASET": "PEDIDO-API-125-SECO", "LINHAS": r},
                                                     ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
