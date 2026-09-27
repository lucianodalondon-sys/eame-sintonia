# -*- coding: utf-8 -*-
"""CANAIS-41 · ensaio a seco da fase `canal-youtube` do Scrap, sem rede e sem chave real.

Corre o codigo VERDADEIRO do Scrap (`scrap_colheita.colher` -> `sx.COLLECT` ->
`adaptador_youtube.youtube_uploads` -> `youtube_oficial.uploads_recentes`) numa COPIA,
com duas trocas e so duas:

  * a chave: uma cadeia sem valor (`SECO-SEM-CHAVE`) posta so no ambiente DESTE
    processo — a verdadeira vive no segredo do GitHub e nunca passa por aqui;
  * o transporte da API (`youtube_oficial._http`): devolve respostas literais e CONTA
    cada pedido pelo host e pelo metodo (sem a chave no registo).

Qualquer outro pedido de rede morre no proxy fechado (127.0.0.1:9). O envelope que
sai vai a `regua_social.julgar` com o contrato da copia (o que o B escreveu), e
diz-se o veredito e o porque — e o que falta, se faltar.

Cenarios por canal: NORMAL (3 videos publicos), PRIVADO (um «Private video» no meio),
VAZIO (canal sem uploads).

Uso (na copia): py ferramentas/canais41/ensaio_a_seco.py --ids=IT-..,IT-.. [--saida X.json]
                [--simular-carimbo]   HIPOTESE: os itens com OWNER_AUTHORIZED/PLATFORM_POLICY_STATUS
"""
import json
import os
import sys
import urllib.parse
from collections import Counter
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
if "source-curator-service-v1" in str(RAIZ).replace("\\", "/"):
    sys.exit("RECUSADO: isto e a arvore do bot vivo")
for v in ("HTTP_PROXY", "HTTPS_PROXY", "http_proxy", "https_proxy"):
    os.environ[v] = "http://127.0.0.1:9"
os.environ["YOUTUBE_DATA_API_KEY"] = "SECO-SEM-CHAVE"
for p in ("coleta", "leis", "admissao", "regras", "ferramentas", "medidas", "guarda", "pedido",
          "orquestrador", "curadoria", ""):
    sys.path.insert(0, str(RAIZ / p) if p else str(RAIZ))

import youtube_oficial as yt     # noqa: E402
import scrap_colheita as sc      # noqa: E402
import regua_social as RG        # noqa: E402

PEDIDOS = []
RODADA = []


def _videos(cenario, cid):
    base = [("aaaaaaaaaa1", "Vendemmia 2026", "2026-09-20T10:00:00Z"),
            ("aaaaaaaaaa2", "Potatura del melo", "2026-09-12T08:30:00Z"),
            ("aaaaaaaaaa3", "Fiera di settembre", "2026-09-02T16:00:00Z")]
    if cenario == "VAZIO":
        return []
    if cenario == "PRIVADO":
        base[1] = ("aaaaaaaaaa2", "Private video", None)
    out = []
    for vid, titulo, pub in base:
        cd = {"videoId": vid}
        if pub:
            cd["videoPublishedAt"] = pub
        out.append({"contentDetails": cd,
                    "snippet": {"title": titulo, "description": "descricao do autor",
                                "channelId": cid, "publishedAt": pub or "2026-09-24T00:00:00Z"}})
    return out


def transporte(cenario, cid):
    def _http(url):
        u = urllib.parse.urlparse(url)
        q = urllib.parse.parse_qs(u.query)
        PEDIDOS.append({"HOST": u.hostname, "METODO": u.path.rsplit("/", 1)[-1],
                        "TEM_CHAVE": "key" in q})
        if u.path.endswith("/channels"):
            return {"items": [{"id": cid, "snippet": {"title": "Canale"},
                               "contentDetails": {"relatedPlaylists": {"uploads": "UU" + cid[2:]}}}]}
        if u.path.endswith("/playlistItems"):
            return {"items": _videos(cenario, cid)}
        raise AssertionError("pedido inesperado: %s" % u.path)
    return _http


def main(argv) -> int:
    ids = next((a.split("=", 1)[1].split(",") for a in argv if a.startswith("--ids=")), [])
    contratos = {c["SOURCE_ID"]: c for c in json.loads(
        (RAIZ / "curadoria" / "italy_contracts_curator.json").read_text(encoding="utf-8"))["FONTES"]}
    linhas = []
    for sid in ids:
        c = contratos[sid]
        aq = c.get("ACQUISITION") or {}
        cid = aq.get("CHANNEL_ID")
        for cenario in ("NORMAL", "PRIVADO", "VAZIO"):
            PEDIDOS.clear()
            yt._http = transporte(cenario, cid)
            run_id = "SECO-%s-%s" % (sid, cenario)
            env = sc.colher("canal-youtube", run_id=run_id, fonte=sid, channel_id=cid)
            if "--simular-carimbo" in argv:
                # HIPOTESE, nao facto: como se o executor escrevesse as duas marcas que hoje
                # nao escreve. So para ver o que a regua (e a D53) decidiriam a seguir.
                for it in env.get("COLHEITA") or []:
                    it["OBSERVACAO"].update(OWNER_AUTHORIZED="SIM", PLATFORM_POLICY_STATUS="ALLOWED")
                run_id += "-SIMULADO"
                env["RUN_ID"] = run_id
            caminho = sc.escrever(env)          # o mesmo sitio onde a fase o escreve de verdade
            RODADA.append("%s\t%s" % (sid, run_id))
            # sem banco da corrida no ensaio: conta-se 1 linha RAW para ver o resto da regua;
            # o que a regua diz de RAW 0 ja esta provado nos testes dela
            v, porque = RG.julgar(env, sid, RG.fase_do_contrato(c), 1, contrato=c)
            ob0 = ((env.get("COLHEITA") or [{}])[0].get("OBSERVACAO") or {})
            linhas.append({
                "SOURCE_ID": sid, "CENARIO": cenario, "STRATEGY": aq.get("STRATEGY"), "FASE": aq.get("FASE"),
                "PEDIDOS": len(PEDIDOS), "PEDIDOS_POR_HOST": dict(Counter(p["HOST"] for p in PEDIDOS)),
                "PEDIDOS_POR_METODO": dict(Counter(p["METODO"] for p in PEDIDOS)),
                "COLHEITA": len(env.get("COLHEITA") or []), "ESTADO_DO_ENVELOPE": env.get("ESTADO"),
                "PORQUE_ZERO": (env.get("PORQUE_ZERO_COLHEITA") or "")[:200],
                "CAMPOS_DO_1o_ITEM": sorted(ob0),
                "FALTA_NA_REGUA_ANTIGA": [k for k in RG.CAMPOS_DO_ITEM if not ob0.get(k) or ob0.get(k) == "NAO SEI"],
                "PROVAS_D53_QUE_FALTAM": RG.provas_do_video(ob0, cid) if ob0 else None,
                "ENVELOPE": os.path.relpath(caminho, RAIZ),
                "VEREDITO": v, "PORQUE": porque[:300]})
            print("%-11s %-8s pedidos=%d %s colheita=%d -> %s · %s" % (
                sid, cenario, len(PEDIDOS), linhas[-1]["PEDIDOS_POR_HOST"], linhas[-1]["COLHEITA"], v, porque[:140]))
    (RAIZ / "ferramentas" / "canais41" / "RODADA-SECA.tsv").write_text("\n".join(RODADA) + "\n", encoding="utf-8")
    if "--saida" in argv:
        Path(argv[argv.index("--saida") + 1]).write_text(json.dumps(
            {"DATASET": "CANAIS-41-ENSAIO-A-SECO", "CHAVE": "nenhuma real (SECO-SEM-CHAVE, so neste processo)",
             "REDE": "proxy fechado 127.0.0.1:9; transporte da API trocado por literais", "LINHAS": linhas},
            ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
