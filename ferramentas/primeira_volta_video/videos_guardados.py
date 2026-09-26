# -*- coding: utf-8 -*-
"""PRIMEIRA-VOLTA-VIDEO · os videos que JA estao guardados, lidos dos bytes — sem rede.

Para cada fonte do universo: as paginas /watch que a Sala guardou (raw_asset, SO LEITURA) e o
ficheiro no armazem com o sha256 conferido. De cada pagina tira-se o que ELA declara (nada
inventado): titulo, data de publicacao, canal, duracao, descricao do autor, se ha faixas de
legenda e em que lingua. Pagina em falta ou sha diferente = NAO_SEI, com o porque.

    py ferramentas/primeira_volta_video/videos_guardados.py --universo=UNIVERSO-59.json --saida=VIDEOS-GUARDADOS.json
"""
import hashlib
import html
import json
import os
import re
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
import sala_so_leitura as S   # noqa: E402

ARMAZEM = Path(os.environ.get("SINTONIA_ARMAZEM_RAIZ") or Path.home() / "sintonia-sala-italia" / "armazem")


def _json_depois(b: str, chave: str):
    """O objecto JSON que comeca logo a seguir a `chave` (ex.: ytInitialPlayerResponse = {...})."""
    i = b.find(chave)
    if i < 0:
        return None
    j = b.find("{", i)
    if j < 0:
        return None
    try:
        obj, _ = json.JSONDecoder().raw_decode(b[j:])
        return obj
    except ValueError:
        return None


def _meta(b: str, *nomes):
    for n in nomes:
        m = re.search(r'<meta\s+(?:itemprop|name|property)="%s"\s+content="([^"]*)"' % re.escape(n), b)
        if m:
            return html.unescape(m.group(1))
    return None


def retrato(b: str) -> dict:
    pr = _json_depois(b, "ytInitialPlayerResponse") or {}
    vd = pr.get("videoDetails") or {}
    mf = ((pr.get("microformat") or {}).get("playerMicroformatRenderer")) or {}
    faixas = (((pr.get("captions") or {}).get("playerCaptionsTracklistRenderer") or {}).get("captionTracks")) or []
    return {
        "VIDEO_ID": vd.get("videoId"),
        "TITULO": vd.get("title") or _meta(b, "title", "og:title"),
        "PUBLICADO": mf.get("publishDate") or _meta(b, "datePublished", "uploadDate"),
        "CANAL": vd.get("channelId") or _meta(b, "channelId"),
        "AUTOR": vd.get("author"),
        "DURACAO_S": int(vd["lengthSeconds"]) if str(vd.get("lengthSeconds") or "").isdigit() else None,
        "DESCRICAO": vd.get("shortDescription"),
        "LEGENDAS": [{"LINGUA": f.get("languageCode"), "AUTO": f.get("kind") == "asr"} for f in faixas],
        "AO_VIVO": bool(vd.get("isLiveContent")),
        "SEM_PLAYER_RESPONSE": not pr,
    }


def main(argv) -> int:
    arg = dict(a[2:].split("=", 1) for a in argv[1:] if a.startswith("--") and "=" in a)
    u = json.loads(Path(arg["universo"]).read_text(encoding="utf-8"))["FONTES"]
    ids = ",".join("'%s'" % f["SOURCE_ID"] for f in u)
    linhas = S.consultar(
        "select r.source_id, r.source_url, r.captured_at::text, s.storage_path, s.sha256 "
        "from raw_asset r join storage_object s on s.id = r.storage_object_id "
        "where r.source_id in (%s) and r.source_url like '%%youtube.com/watch%%' "
        "order by r.source_id, r.captured_at desc;" % ids)
    out, nao_sei = [], 0
    for sid, url, quando, caminho, sha in linhas:
        p = ARMAZEM / caminho
        reg = {"SOURCE_ID": sid, "URL": url, "GUARDADO_EM": quando, "FICHEIRO": caminho, "SHA256": sha}
        if not p.exists():
            reg.update(ESTADO="NAO_SEI", PORQUE="ficheiro em falta no armazem")
        else:
            b = p.read_bytes()
            if hashlib.sha256(b).hexdigest() != sha:
                reg.update(ESTADO="NAO_SEI", PORQUE="sha256 do ficheiro nao bate com a Sala")
            else:
                reg.update(ESTADO="LIDO", **retrato(b.decode("utf-8", "replace")))
        nao_sei += reg["ESTADO"] != "LIDO"
        out.append(reg)
    Path(arg["saida"]).write_text(json.dumps({"DATASET": "PRIMEIRA-VOLTA-VIDEO-VIDEOS-GUARDADOS",
                                              "ARMAZEM": str(ARMAZEM), "N": len(out), "NAO_SEI": nao_sei,
                                              "VIDEOS": out}, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print("paginas", len(out), "lidas", len(out) - nao_sei, "NAO_SEI", nao_sei)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
