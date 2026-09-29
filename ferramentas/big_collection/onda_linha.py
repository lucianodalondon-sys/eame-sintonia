# -*- coding: utf-8 -*-
"""A ONDA DE UMA LINHA NAO-WEB — YOUTUBE, INSTAGRAM, LINKEDIN, ate RAW e a Sala (RELIGA-MULTICANAL, D155).

    py ferramentas/big_collection/onda_linha.py --correr --linha=YOUTUBE --fontes=<candidatas.json>
          --saida=<pasta da onda> [--max-alvos=N] [--sem-sala]

PORQUE EXISTE: `onda_web.py` corre a COORTE CONGELADA pelo `micro_coleta`, e so sabe fontes que estao
nela. As linhas nao-web nao tem coorte — tem rota propria e alvos proprios. Faltava o EXECUTOR DE CICLO
delas, e era esse o buraco verdadeiro (nao o contador de 24 h).

    O AGENDADOR ESCOLHE; O TRANSPORTE CORTA; A PROVA CONFERE. Esta peca e so o transporte da linha.

O QUE ELA FAZ, E POR QUE ORDEM:
  1. DESCOBRE os alvos pela rota PROVADA da linha (`coleta/rotas_multicanal.py`);
  2. COLHE os bytes de cada alvo pela MESMA porta (`coleta/scrap_http.buscar_bytes`: robots vivo, portao
     de egresso, reserva no livro de 24 h antes do pedido e registo da resposta depois);
  3. PRESERVA pelo DONO DO RAW (`guarda/preservar_coleta.preservar`), numa corrida propria em
     `collection_run` — a mesma forma que `coleta/linha_busca_raw.py` ja usa;
  4. passa cada unidade pela ADMISSION NORMAL, com o RAW_OBSERVATION_ID REAL que o banco devolveu;
  5. poe os PRONTOS na Sala canonica (`sala_de_espera.pousar`), na mesma corrida que acabou de nascer.

    UMA UNIDADE QUE NAO TEM RAW NO BANCO NAO E POUSADA. Sem linhagem nao ha Sala: e por isso que o
    passo 3 vem antes do 4, e nao ao contrario.

ESCREVE `ONDA-WEB-ESTADO.json` com a MESMA FORMA que a onda web — nao por preguica, mas porque o
`coleta_continua._ondas()` le esse ficheiro para contar pedidos, RUN_IDs e o delta da Sala. Duas formas
para a mesma coisa obrigariam o ciclo a saber de que linha veio cada ficheiro, e e exactamente essa
adivinhacao que esta casa ja pagou uma vez.

O QUE ESTA PECA NAO FAZ: nao escolhe fontes (o Curator escolhe), nao julga relevancia (a Admission
julga), nao baixa bytes de video do LinkedIn (ver `URL_MP4_DESCOBERTA` em `rotas_multicanal`), e nao
toca em Apify — proibida nesta instalacao pela D155.
"""
from __future__ import annotations

import hashlib
import json
import os
import sys
import time
import urllib.parse
from datetime import datetime, timezone
from pathlib import Path

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parents[1]
sys.path.insert(0, str(RAIZ))
import _gavetas  # noqa: E402,F401 — as gavetas do processo no caminho (`orquestrador` e um MODULO, nao a pasta)
sys.path.insert(0, str(RAIZ / "scripts" / "micro_coleta"))

RULE_VERSION = "RELIGA-MULTICANAL/v1 (D155)"
ESTADO_F = "ONDA-WEB-ESTADO.json"
RAW_F = "RAW-LINHA.jsonl"
LIVRO_F = "LIVRO-LINHA.jsonl"

# O ACTOR de cada linha: o ficheiro que REALMENTE fez o pedido. Nao um nome bonito — o caminho, para
# quem ler o `collection_run` daqui a um mes saber onde esta o codigo que produziu aquela linha.
ACTOR = {
    "YOUTUBE": "coleta/rotas_multicanal.py::youtube_videos_do_canal",
    "INSTAGRAM": "coleta/rotas_multicanal.py::instagram_reels_da_conta",
    "LINKEDIN": "coleta/rotas_multicanal.py::linkedin_posts_da_organizacao",
}
PLATAFORMA = {"YOUTUBE": "YOUTUBE", "INSTAGRAM": "INSTAGRAM", "LINKEDIN": "LINKEDIN"}
TERRITORIO_POR_OMISSAO = "T9"


def agora_iso() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


def _utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def run_id(source_id: str | None, territorio: str | None = None) -> str:
    """O RUN_ID no formato que a PROVA-TETO le (`provas/prova_teto_dominio.RE_RUN_ID`):
    (IT|XX)-T<n>-AAAA-MM-DD-HHMMSS-<16 hex>. Um formato proprio ficaria invisivel para a prova."""
    t = territorio
    if not t:
        p = str(source_id or "").split("-")
        t = p[1] if len(p) > 2 and p[1].startswith("T") and p[1][1:].isdigit() else TERRITORIO_POR_OMISSAO
    pais = "IT" if str(source_id or "").startswith("IT-") else "XX"
    quando = datetime.now(timezone.utc).strftime("%Y-%m-%d-%H%M%S")
    salga = hashlib.sha256(("%s|%s|%s" % (source_id, t, time.time())).encode("utf-8")).hexdigest()[:16]
    return "%s-%s-%s-%s" % (pais, t, quando, salga)


# ══════════════════════════════════════════════════════════════════════════════
# 1. A DESCOBERTA E A COLHEITA, POR LINHA
# ══════════════════════════════════════════════════════════════════════════════
def alvos_da_fonte(linha: str, cand: dict, buscar, *, max_alvos=None) -> dict:
    """→ {"ALVOS": [...], "PEDIDOS": n, "ROTA": ..., "RAW_DA_DESCOBERTA": bytes|None} ou {"ERRO": ...}."""
    import rotas_multicanal as RM                                  # noqa: PLC0415
    alvo = cand.get("ALVO") or {}
    if linha == "YOUTUBE":
        r = RM.youtube_videos_do_canal(channel_id=alvo.get("CHANNEL_ID"), buscar=buscar, max_alvos=max_alvos)
        if r.get("ERRO"):
            return r
        return {"ALVOS": r["ALVOS"], "PEDIDOS": r["PEDIDOS"], "ROTA": r["ROTA"], "URL": r["URL"],
                "RAW_DA_DESCOBERTA": r.get("HTML"), "IDENTIDADE_CONFERIDA": r.get("IDENTIDADE_CONFERIDA"),
                "ALVOS_NA_PAGINA": r.get("VIDEOS_NA_PAGINA")}
    if linha == "INSTAGRAM":
        # Os Reels que o Curator JA provou entram primeiro, por URL DIRECTA (D22) — eles nao dependem da
        # listagem. A listagem por /embed/ (rota provada a 23/09) acrescenta o que a conta servir hoje.
        conhecidos = [{"URL": u, "NOME": (u.rstrip("/").rsplit("/", 1) or [""])[-1],
                       "NATIVE_ID": (u.rstrip("/").rsplit("/", 1) or [""])[-1],
                       "DESCOBERTO_POR": "CURATOR_REELS_JA_NO_REPOSITORIO", "CONTA": alvo.get("HANDLE")}
                      for u in (alvo.get("REELS_CONHECIDOS") or [])]
        r = RM.instagram_reels_da_conta(handle=alvo.get("HANDLE"), buscar=buscar, max_alvos=max_alvos)
        if r.get("ERRO"):
            # A listagem falhou; os Reels PROVADOS continuam a valer — e isso e um resultado, nao um erro.
            if conhecidos:
                return {"ALVOS": conhecidos, "PEDIDOS": r.get("PEDIDOS", 1), "ROTA": RM.ROTA_IG_REEL,
                        "RAW_DA_DESCOBERTA": None, "LISTAGEM_FALHOU": r["ERRO"]}
            return r
        novos = [a for a in r["ALVOS"] if a["URL"] not in {c["URL"] for c in conhecidos}]
        return {"ALVOS": conhecidos + novos, "PEDIDOS": r["PEDIDOS"], "ROTA": r["ROTA"], "URL": r.get("URL"),
                "RAW_DA_DESCOBERTA": r.get("HTML"), "ALVOS_NA_PAGINA": r.get("REELS_NA_PAGINA"),
                "REELS_CONHECIDOS": len(conhecidos)}
    if linha == "LINKEDIN":
        r = RM.linkedin_posts_da_organizacao(pagina_url=alvo.get("PAGINA"), run_id=cand.get("_RUN_ID") or "LI",
                                             buscar=buscar, teto=max_alvos)
        if r.get("ERRO"):
            return r
        return {"ALVOS": [dict(c, URL=c.get("URL_DO_POST")) for c in r["CARTOES"] if c.get("URL_DO_POST")],
                "PEDIDOS": r["PEDIDOS"], "ROTA": r["ROTA"], "URL": alvo.get("PAGINA"),
                "RAW_DA_DESCOBERTA": None, "VIDEO_BYTES_ACQUIRED": False,
                "FETCH_POST": r.get("FETCH_POST"), "CARTOES_COM_VIDEO": r.get("CARTOES_COM_VIDEO")}
    return {"ERRO": "LINHA_SEM_ROTA_NESTE_EXECUTOR: %s" % linha, "PEDIDOS": 0}


def colher_alvo(linha: str, a: dict, buscar) -> dict:
    """Os bytes de UM alvo, pela porta. → {"BYTES", "URL", "MEDIA_TYPE", "PEDIDOS"} ou {"ERRO"}."""
    import rotas_multicanal as RM                                  # noqa: PLC0415
    if linha == "YOUTUBE":
        # FETCH_VIDEO_METADATA `youtube:oembed` = PROVED na matriz social, 0 USD, sem chave.
        # A transcricao NAO entra aqui: `yt-dlp:public_audio` esta PROVED mas e PROCESSO FILHO, e o
        # registo de rotas desta casa proibe processo filho. Metadados/descricao, como a missao manda.
        o = "https://www.youtube.com/oembed?url=%s&format=json" % urllib.parse.quote(a["URL"], safe="")
        r = buscar(o, "application/json")
        if r.get("ERRO") or r.get("STATUS") != 200:
            return {"ERRO": "oembed nao respondeu 200 (status %s%s)" % (r.get("STATUS") or 0,
                    ", " + r["ERRO"] if r.get("ERRO") else ""), "PEDIDOS": 1, "URL": o}
        return {"BYTES": r["BYTES"], "URL": a["URL"], "URL_PEDIDA": o, "MEDIA_TYPE": "application/json",
                "PEDIDOS": 1, "ROTA": "youtube:oembed"}
    if linha == "INSTAGRAM":
        r = RM.instagram_reel(url=a["URL"], buscar=buscar)
        if r.get("ERRO"):
            return r
        return {"BYTES": r["BYTES"], "URL": r["URL_PUBLICA"], "URL_PEDIDA": r["URL"],
                "MEDIA_TYPE": "text/html", "PEDIDOS": r["PEDIDOS"], "ROTA": r["ROTA"]}
    if linha == "LINKEDIN":
        # ⚠️ O post individual NAO se pede: `FETCH_POST` esta ROUTE_NOT_ALLOWED na matriz e continua
        # fechado. O que existe e o que a PAGINA PUBLICA ja serviu na descoberta — o texto publico do
        # cartao. Zero pedidos novos, e zero bytes de video.
        texto = a.get("TEXTO_PUBLICO") or ""
        corpo = json.dumps({"URL_DO_POST": a.get("URL_DO_POST"), "TEXTO_PUBLICO": texto,
                            "URL_MP4_DESCOBERTA": a.get("URL_MP4_DESCOBERTA"),
                            "VIDEO_BYTES_ACQUIRED": False}, ensure_ascii=False).encode("utf-8")
        if not texto.strip():
            return {"ERRO": "CARTAO_SEM_TEXTO_PUBLICO", "PEDIDOS": 0, "URL": a.get("URL_DO_POST")}
        return {"BYTES": corpo, "URL": a.get("URL_DO_POST"), "MEDIA_TYPE": "application/json",
                "PEDIDOS": 0, "ROTA": "linkedin:texto-publico-do-cartao", "VIDEO_BYTES_ACQUIRED": False}
    return {"ERRO": "LINHA_SEM_COLHEITA: %s" % linha, "PEDIDOS": 0}


# ══════════════════════════════════════════════════════════════════════════════
# 2. RAW e SALA — a porta canonica, a mesma de `coleta/linha_busca_raw.py`
# ══════════════════════════════════════════════════════════════════════════════
def _slug(v: str) -> str:
    from coleta import ingresso as ing                             # noqa: PLC0415
    return ing._slug(v)


def artefato(linha: str, cand: dict, colhido: dict, capturado: str) -> dict:
    """A ficha na lingua do DONO DO RAW. `SOURCE_ID` vai como o Curator o deu — ou None, declarado."""
    url = colhido["URL"]
    mt = colhido.get("MEDIA_TYPE") or "text/html"
    nome = _slug(os.path.basename(urllib.parse.urlsplit(url).path.rstrip("/")) or "item")[:60] or "item"
    return {
        "COUNTRY": "IT",
        "SOURCE_SLUG": _slug(str(cand.get("SOURCE_ID") or cand.get("NOME") or linha)),
        "ARTIFACT_KIND": "OBSERVATION",
        "NAME": nome + (".json" if mt == "application/json" else ".html"),
        "SOURCE_NATIVE_ID": "u" + hashlib.sha256(url.split("#")[0].encode("utf-8")).hexdigest()[:16],
        "SHA256": hashlib.sha256(colhido["BYTES"]).hexdigest(),
        "BYTES": len(colhido["BYTES"]), "MEDIA_TYPE": mt,
        "CAPTURED_AT": capturado, "SOURCE_URL": url, "USED_BY": None,
        "SOURCE_ID": cand.get("SOURCE_ID"),
        # Nao se inventa DOCUMENT_ID: a observacao fica FORWARD_IDENTITY_UNPROVEN, que e a verdade.
        "DOCUMENT_ID": None,
    }


def a_corrida(linha: str, corrida: str, cand: dict, descoberta: dict) -> dict:
    return {"RUN_ID": corrida, "PLATFORM": PLATAFORMA.get(linha, "HTTP direto"), "ACTOR": ACTOR.get(linha, linha),
            "ACTOR_VERSION": "religa-multicanal-v1", "SOURCE_COUNTRY": "IT",
            "STARTED_AT": _utc(), "RULE_VERSION": RULE_VERSION,
            "MISSION": ("RELIGA-MULTICANAL (D155): linha %s, fonte %s, rota %s; rota publica provada, sem "
                        "login, sem chave, sem rota paga" % (linha, cand.get("SOURCE_ID") or "SEM_SOURCE_ID",
                                                             descoberta.get("ROTA")))[:500],
            "CAPTURE_METHOD": "%s + coleta/scrap_http.buscar_bytes (robots vivo, teto_da_onda -> livro de 24 h)"
                              % descoberta.get("ROTA")}


def para_a_sala(linha: str, cand: dict, colhidos: list, corrida: str, *, persistencia, pousar: bool) -> dict:
    """PRESERVA -> ADMISSION com o RAW real -> Sala. Devolve o relato, sem levantar por item mau."""
    from guarda import preservar_coleta as PC                      # noqa: PLC0415
    import linha_busca as LB                                       # noqa: PLC0415
    armazem = PC.ArmazemLocal(persistencia.raiz_do_armazem)
    capturado = _utc()
    fichas, por_sha = [], {}
    for c in colhidos:
        f = artefato(linha, cand, c, capturado)
        if f["SHA256"] in por_sha:
            continue                                               # o mesmo byte nao entra duas vezes
        por_sha[f["SHA256"]] = c
        fichas.append(f)
    if not fichas:
        return {"RAW": None, "PRONTOS": [], "ITENS": 0, "RELATO": []}
    run = a_corrida(linha, corrida, cand, colhidos[0].get("_DESCOBERTA") or {})
    recibo = PC.preservar(run, fichas, armazem, lambda o: por_sha[o["SHA256"]]["BYTES"],
                          memoria=persistencia.memoria)
    ids = {}
    for o in recibo.get("RAW_OBSERVATIONS") or []:
        if o.get("RUN_ID") == corrida and isinstance(o.get("RAW_OBSERVATION_ID"), int):
            ids.setdefault(o.get("SHA256"), o["RAW_OBSERVATION_ID"])
    prontos, relato = [], []
    for f in fichas:
        c = por_sha[f["SHA256"]]
        rid = ids.get(f["SHA256"])
        l = {"SHA256": f["SHA256"], "URL": f["SOURCE_URL"], "SOURCE_ID": cand.get("SOURCE_ID"),
             "SOURCE_STATUS": cand.get("SOURCE_STATUS"), "RAW_OBSERVATION_ID": rid, "ROTA": c.get("ROTA")}
        if rid is None:
            l["ESTADO"] = "SEM_RAW_CANONICO"                       # nao se pousa sem linhagem
            relato.append(l)
            continue
        a = LB.admitir(c["BYTES"], f["MEDIA_TYPE"], f["SOURCE_URL"],
                       {"SOURCE_ID": cand.get("SOURCE_ID") or "SEM_SOURCE_ID"},
                       {"UNIVERSO": cand.get("UNIVERSO") or "NAO SEI"}, f["SHA256"], capturado, corrida,
                       raw_asset_id=rid)
        l["ADMISSION"] = {k: a[k] for k in ("RESULTADO", "REGRA", "MOTIVO")}
        if a["READY"]:
            prontos.append(a["READY"])
            l["ESTADO"] = "PRONTO_COM_RAW"
        else:
            l["ESTADO"] = "ADMISSION_%s" % a["RESULTADO"]
        relato.append(l)
    pousado = None
    if pousar and prontos:
        import sala_de_espera as SE                                # noqa: PLC0415
        SE.exigir_canonica()                                       # Sala canonica ou nada; nunca ficheiro
        pousado = SE.pousar(corrida, prontos)
    return {"RAW": {"RUN_STATE": recibo.get("RUN_STATE"), "OBSERVACOES": len(ids)},
            "PRONTOS": prontos, "ITENS": len({x["ITEM_ID"] for x in prontos}), "POUSADO": pousado,
            "RELATO": relato}


# ══════════════════════════════════════════════════════════════════════════════
# 3. A ONDA
# ══════════════════════════════════════════════════════════════════════════════
def correr(linha: str, candidatas: list, saida: Path, *, max_alvos=None, pousar=True,
           buscar=None, persistencia=None) -> int:
    saida.mkdir(parents=True, exist_ok=True)
    livro_onda = saida / "TETO-ONDA.json"
    os.environ["SINTONIA_TETO_ONDA"] = str(livro_onda)
    os.environ["SINTONIA_LINHA"] = linha
    if buscar is None:
        import rotas_multicanal as RM                              # noqa: PLC0415
        buscar = RM.transporte()
    if persistencia is None and pousar:
        from orquestrador import persistencia as PERS              # noqa: PLC0415
        persistencia = PERS.dependencias_do_runtime()
        if persistencia.memoria is None:
            raise SystemExit("RECUSADO: sem memoria canonica (%s). Sem collection_run/raw_asset nao ha RAW, "
                             "e sem RAW a Sala recusa. Declare BANCO_DESCARTAVEL_URL (ensaio) ou "
                             "SINTONIA_COLLECTION_DSN (operacional)." % persistencia.ESTADO)
    foto = _fotografia if pousar else (lambda: None)
    estado = {"INICIO": agora_iso(), "LINHA": linha, "EXECUTOR": "ferramentas/big_collection/onda_linha.py",
              "LIVRO_DA_ONDA": str(livro_onda), "SALA_INICIO": foto(), "FONTES": [], "PAROU": None}

    def grava():
        (saida / ESTADO_F).write_text(json.dumps(estado, ensure_ascii=False, indent=1, default=str),
                                      encoding="utf-8")
    grava()
    raw_jsonl, livro_jsonl = saida / RAW_F, saida / LIVRO_F
    for i, cand in enumerate(candidatas, 1):
        t0 = time.time()
        corrida = run_id(cand.get("SOURCE_ID"))
        os.environ["SINTONIA_RUN_ID"] = corrida
        cand["_RUN_ID"] = corrida
        antes = foto()
        linha_reg = {"N": i, "SOURCE_ID": cand.get("SOURCE_ID"), "SOURCE_STATUS": cand.get("SOURCE_STATUS"),
                     "HORA": agora_iso(), "RUN_ID": corrida, "CORREU": False, "DOMINIO": cand.get("DOMINIO"),
                     "ALVOS_DESCOBERTOS": 0, "ALVOS_COLHIDOS": 0, "PEDIDOS_POR_DOMINIO": {}}
        d = alvos_da_fonte(linha, cand, buscar, max_alvos=max_alvos)
        pedidos = int(d.get("PEDIDOS") or 0)
        dom = cand.get("DOMINIO") or ""
        if d.get("ERRO"):
            linha_reg.update(STATUS="FAILED", PORQUE_NAO_CORREU=d["ERRO"], SEGUNDOS=round(time.time() - t0),
                             PEDIDOS_POR_DOMINIO={dom: pedidos} if pedidos else {},
                             QUEM_DISSE_NAO=d.get("QUEM_DISSE_NAO"))
            estado["FONTES"].append(linha_reg)
            grava()
            print("%02d %s %s FAILED %s" % (i, linha, cand.get("SOURCE_ID"), d["ERRO"][:120]), flush=True)
            continue
        alvos = d.get("ALVOS") or []
        linha_reg["ALVOS_DESCOBERTOS"] = len(alvos)
        linha_reg["ROTA"] = d.get("ROTA")
        for k in ("IDENTIDADE_CONFERIDA", "ALVOS_NA_PAGINA", "REELS_CONHECIDOS", "LISTAGEM_FALHOU",
                  "VIDEO_BYTES_ACQUIRED", "FETCH_POST", "CARTOES_COM_VIDEO"):
            if d.get(k) is not None:
                linha_reg[k] = d[k]
        colhidos = []
        for a in alvos[:max_alvos] if max_alvos else alvos:
            c = colher_alvo(linha, a, buscar)
            pedidos += int(c.get("PEDIDOS") or 0)
            if c.get("ERRO"):
                with open(livro_jsonl, "a", encoding="utf-8") as fh:
                    fh.write(json.dumps({"ESTADO": "FALHOU", "URL": a.get("URL"), "PORQUE": c["ERRO"],
                                         "LINHA": linha, "CORRIDA": corrida}, ensure_ascii=False) + "\n")
                continue
            c["_DESCOBERTA"] = d
            c["_ALVO"] = a
            colhidos.append(c)
            with open(raw_jsonl, "a", encoding="utf-8") as fh:
                fh.write(json.dumps({"SHA256": hashlib.sha256(c["BYTES"]).hexdigest(), "SOURCE_URL": c["URL"],
                                     "SOURCE_ID": cand.get("SOURCE_ID"), "MEDIA_TYPE": c.get("MEDIA_TYPE"),
                                     "BYTES": len(c["BYTES"]), "CORRIDA": corrida, "LINHA": linha,
                                     "ROTA": c.get("ROTA"), "CAPTURED_AT": _utc(),
                                     "PROVENIENCIA": dict(cand.get("PROVENIENCIA") or {},
                                                          DESCOBERTO_POR=a.get("DESCOBERTO_POR") or d.get("ROTA"),
                                                          CONTA=a.get("CONTA"))},
                                    ensure_ascii=False) + "\n")
        linha_reg["ALVOS_COLHIDOS"] = len(colhidos)
        linha_reg["PEDIDOS_POR_DOMINIO"] = {dom: pedidos} if dom else {}
        if colhidos and pousar:
            try:
                r = para_a_sala(linha, cand, colhidos, corrida, persistencia=persistencia, pousar=True)
                linha_reg.update(RAW=r["RAW"], ITENS_NA_SALA=r["ITENS"], POUSADO=r.get("POUSADO"),
                                 RELATO=r["RELATO"], CORREU=True, STATUS="OK")
            except Exception as ex:                                # noqa: BLE001 — a falha da Sala tem nome
                linha_reg.update(STATUS="FAILED", PORQUE_NAO_CORREU="SALA: %s: %s" % (type(ex).__name__, ex))
        else:
            linha_reg.update(CORREU=bool(colhidos), STATUS="OK" if colhidos else "ZERO",
                             PORQUE_NAO_CORREU=None if colhidos else "ZERO_ALVOS_COLHIDOS")
        linha_reg["SEGUNDOS"] = round(time.time() - t0)
        linha_reg["SALA_ANTES"], linha_reg["SALA_DEPOIS"] = antes, foto()
        estado["FONTES"].append(linha_reg)
        grava()
        print("%02d %s %s %s alvos=%d colhidos=%d pedidos=%d" % (i, linha, cand.get("SOURCE_ID"),
              linha_reg["STATUS"], len(alvos), len(colhidos), pedidos), flush=True)
    estado["FIM"] = agora_iso()
    estado["SALA_FIM"] = foto()
    grava()
    return 0


def _fotografia():
    import ensaio_offline as E                                     # noqa: PLC0415
    return {k: v["LINHAS"] for k, v in E.fotografia().items()}


def main(argv=None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    arg = dict(a[2:].split("=", 1) for a in argv if a.startswith("--") and "=" in a)
    if "--correr" not in argv or "linha" not in arg or "fontes" not in arg or "saida" not in arg:
        print(__doc__)
        return 2
    cands = json.loads(Path(arg["fontes"]).read_text(encoding="utf-8"))
    if isinstance(cands, dict):
        cands = cands.get("CANDIDATAS", cands).get(arg["linha"], [])
    return correr(arg["linha"], cands, Path(arg["saida"]),
                  max_alvos=int(arg["max-alvos"]) if arg.get("max-alvos") else None,
                  pousar="--sem-sala" not in argv)


if __name__ == "__main__":
    raise SystemExit(main())
