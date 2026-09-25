"""Replay idempotente dos achados da RESEARCH-MEDIA-SOURCES-V1 pela porta do dono.

    py research/media-sources-v1/replay.py --fila <caminho/FONTES-CANDIDATAS.json> [--gravar]

Sem --gravar mede apenas (NOVA / DEDUP) e nao escreve. Com --gravar chama
candidatas.fonte_nova.registar para cada achado, apontando a porta para --fila.
O dedup e o do dono (normalizar(URL)); o CANDIDATA_ID e o que a porta der na
fila alvo — o ID da bancada (ID_NA_BANCADA) nao se transporta.
"""
import argparse, json, sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ / "candidatas"))
import fonte_nova  # noqa: E402

ACHADOS = Path(__file__).resolve().parent / "ACHADOS.json"


def replay(fila: Path, gravar: bool) -> dict:
    if not Path(fila).is_file():
        # a porta cria uma fila vazia quando o ficheiro nao existe: aqui isso seria
        # registar 5 «novas» numa fila fantasma. Caminho errado falha alto.
        raise SystemExit(f"fila alvo nao existe: {fila}")
    fonte_nova.FILA = Path(fila)
    antes = fonte_nova.carregar()["CANDIDATAS"]
    foto = {c["CANDIDATA_ID"]: json.dumps(c, sort_keys=True, ensure_ascii=False) for c in antes}
    existentes = {fonte_nova.normalizar(c["URL"]): c["CANDIDATA_ID"] for c in antes}
    out = {"FILA": str(fila), "GRAVAR": gravar, "LINHAS_ANTES": len(antes), "ACHADOS": []}
    for a in json.loads(ACHADOS.read_text(encoding="utf-8"))["ACHADOS"]:
        chave = fonte_nova.normalizar(a["url"])
        r = {"ID_NA_BANCADA": a["ID_NA_BANCADA"], "URL": a["url"]}
        if chave in existentes:
            r.update(RESULTADO="DEDUP", CANDIDATA_ID=existentes[chave])
        else:
            r["RESULTADO"] = "NOVA"
        if gravar:
            args = {k: a[k] for k in ("tipo", "pais", "nome", "url", "para_que", "quem_viu", "onde_viu", "nota")}
            r["CANDIDATA_ID"] = fonte_nova.registar(**args)["CANDIDATA_ID"]
            existentes.setdefault(chave, r["CANDIDATA_ID"])
        out["ACHADOS"].append(r)
    depois = fonte_nova.carregar()["CANDIDATAS"]
    ids = [c["CANDIDATA_ID"] for c in depois]
    urls = [fonte_nova.normalizar(c["URL"]) for c in depois]
    agora = {c["CANDIDATA_ID"]: json.dumps(c, sort_keys=True, ensure_ascii=False) for c in depois}
    # toda linha que ja existia sai byte-igual (o dedup do dono so acrescenta VISTA_TAMBEM_POR
    # na linha repetida; isso fica listado a parte, nunca escondido)
    dedup_ids = {r.get("CANDIDATA_ID") for r in out["ACHADOS"] if r["RESULTADO"] == "DEDUP"}
    alteradas = [i for i in foto if agora.get(i) != foto[i]]
    out["LINHAS_ANTIGAS_ALTERADAS"] = [i for i in alteradas if i not in dedup_ids]
    out["LINHAS_DEDUP_COM_VISTA_TAMBEM_POR"] = [i for i in alteradas if i in dedup_ids]
    out.update(LINHAS_DEPOIS=len(depois), NOVAS=sum(r["RESULTADO"] == "NOVA" for r in out["ACHADOS"]),
               DEDUP=sum(r["RESULTADO"] == "DEDUP" for r in out["ACHADOS"]),
               IDS_DUPLICADOS=len(ids) - len(set(ids)), URLS_DUPLICADAS=len(urls) - len(set(urls)))
    if gravar and out["LINHAS_ANTIGAS_ALTERADAS"]:
        raise SystemExit(f"linhas antigas alteradas: {out['LINHAS_ANTIGAS_ALTERADAS']}")
    if gravar and out["IDS_DUPLICADOS"]:
        # a porta numera por len+1; uma fila com buracos pode repetir um ID. Falha alto.
        raise SystemExit(f"ID DUPLICADO na fila alvo depois do replay: {out['IDS_DUPLICADOS']}")
    return out


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--fila", required=True)
    ap.add_argument("--gravar", action="store_true")
    a = ap.parse_args()
    print(json.dumps(replay(Path(a.fila), a.gravar), ensure_ascii=False, indent=2))
