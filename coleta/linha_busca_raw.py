#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""LINHA-BUSCA · o RAW CANONICO e a Sala — a divida da v1 fechada pela porta do dono (27/09, coordenacao 11:20).

    py coleta/linha_busca_raw.py --repousar --saidas=<pasta1;pasta2> [--corrida=<RUN_ID>] [--pousar]

O DEFEITO MEDIDO (coordenador, 11:20): `sala_de_espera.pousar` falhou com
`sala_de_espera_run_id_fkey` — a corrida da linha nunca tinha existido em `collection_run`, e os
itens iam com `RAW_OBSERVATION_ID = NAO SEI`. A transacao desfez-se; nada foi escrito (Sala 204).

O QUE ISTO FAZ, SEM PEDIR NADA A REDE (os bytes ja estao no armazem da linha, com sha256):
  1. le as paginas ADMITIDAS de cada pasta da linha (LIVRO-LINHA-BUSCA.jsonl + RAW-LINHA-BUSCA.jsonl) e
     confere o sha256 dos bytes guardados — byte que nao bate nao entra;
  2. preserva-as pelo DONO DO RAW, `guarda/preservar_coleta.preservar()`, numa corrida PROPRIA
     (collection_run com ACTOR = coleta/linha_busca.py), com a memoria que o runtime compoe
     (`orquestrador/persistencia.dependencias_do_runtime`: SINTONIA_COLLECTION_DSN operacional OU
     BANCO_DESCARTAVEL_URL; nenhuma das duas = RECUSA, nunca cai para ficheiro);
  3. volta a passar cada pagina pela Admission NORMAL (`linha_busca.admitir`), agora com o
     RAW_OBSERVATION_ID REAL que o banco devolveu — o READY nasce com a linhagem;
  4. so com `--pousar`: `sala_de_espera.exigir_canonica()` e `pousar(corrida, prontos)` — a mesma corrida
     que acabou de nascer em collection_run (a chave estrangeira fica satisfeita por construcao).
O CAPTURED_AT de cada observacao e o da colheita original (a proveniencia ACHADO_POR_BUSCA vem no livro da
linha e no manifesto; a observacao guarda consulta+motor+posicao na NOTA da corrida via MISSION/CAPTURE_METHOD).
"""
from __future__ import annotations

import hashlib
import json
import os
import sys
import urllib.parse
from datetime import datetime, timezone
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
import _gavetas  # noqa: E402,F401

ACTOR = "coleta/linha_busca.py"
RULE_VERSION = "LINHA-BUSCA/v1 (D93 · D94-b)"


def _slug(v: str) -> str:
    from coleta import ingresso as ing
    return ing._slug(v)


def paginas_admitidas(pastas: list) -> list:
    """As paginas ADMITIDAS das pastas da linha, uma por sha256, com os bytes conferidos."""
    fora, vistos = [], set()
    for pasta in pastas:
        pasta = Path(pasta)
        raws = {}
        for l in (pasta / "RAW-LINHA-BUSCA.jsonl").read_text(encoding="utf-8").splitlines():
            if l.strip():
                r = json.loads(l)
                raws.setdefault(r["SHA256"], r)
        for l in (pasta / "LIVRO-LINHA-BUSCA.jsonl").read_text(encoding="utf-8").splitlines():
            if not l.strip():
                continue
            e = json.loads(l)
            if e.get("ESTADO") != "ADMITIDA":
                continue
            sha = (e.get("RAW") or {}).get("SHA256")
            if not sha or sha in vistos or sha not in raws:
                continue
            raw = raws[sha]
            f = pasta / raw["STORAGE_PATH"]
            if not f.is_file():
                continue
            dados = f.read_bytes()
            if hashlib.sha256(dados).hexdigest() != sha:
                continue                                       # byte que nao bate nao entra
            vistos.add(sha)
            fora.append({"RAW": raw, "LIVRO": e, "DADOS": dados, "PASTA": str(pasta)})
    return fora


def artefato(p: dict) -> dict:
    """A ficha na lingua do dono do RAW (a mesma que `coleta/ingresso.para_o_dono_do_raw` escreve)."""
    raw = p["RAW"]
    mt = (raw.get("MEDIA_TYPE") or "text/html").split(";")[0].strip().lower()
    url = raw["SOURCE_URL"]
    host = (urllib.parse.urlsplit(url).hostname or "").lower()
    nome = os.path.basename(urllib.parse.urlsplit(url).path.rstrip("/")) or "index"
    nome = _slug(nome)[:60] or "index"
    return {
        "COUNTRY": "IT" if host.endswith(".it") else "XX",
        "SOURCE_SLUG": _slug(raw["SOURCE_ID"]),
        "ARTIFACT_KIND": "DOCUMENT" if mt == "application/pdf" else "OBSERVATION",
        "NAME": nome + (".pdf" if mt == "application/pdf" else ".html"),
        "SOURCE_NATIVE_ID": "u" + hashlib.sha256(url.split("#")[0].encode("utf-8")).hexdigest()[:16],
        "SHA256": raw["SHA256"], "BYTES": len(p["DADOS"]), "MEDIA_TYPE": mt,
        "CAPTURED_AT": raw["CAPTURED_AT"], "SOURCE_URL": url, "USED_BY": None,
        "SOURCE_ID": raw["SOURCE_ID"],
        # DOCUMENT_ID: a pagina achada por busca nao traz identificador documental da fonte. Nao se inventa
        # (nem do sha, nem da URL): a observacao fica FORWARD_IDENTITY_UNPROVEN, que e a verdade.
        "DOCUMENT_ID": None,
    }


def a_corrida(corrida: str, paginas: list) -> dict:
    origens = sorted({p["RAW"].get("CORRIDA") or "NAO SEI" for p in paginas})
    motores = sorted({(p["RAW"].get("PROVENIENCIA") or {}).get("MOTOR") or "NAO SEI" for p in paginas})
    return {"RUN_ID": corrida, "PLATFORM": "HTTP direto", "ACTOR": ACTOR,
            "ACTOR_VERSION": "linha-busca-v1", "SOURCE_COUNTRY": "IT",
            "STARTED_AT": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "RULE_VERSION": RULE_VERSION,
            "MISSION": ("LINHA-BUSCA: paginas ACHADO_POR_BUSCA (D93) colhidas nas corridas %s; motor %s; "
                        "preservadas sem novo pedido a rede" % (", ".join(origens), ", ".join(motores)))[:500],
            "CAPTURE_METHOD": "ACHADO_POR_BUSCA + HTTP coleta/scrap_http.buscar_bytes (robots vivo, teto_da_onda)"}


def repousar(pastas: list, *, corrida: str = None, pousar: bool = False, persistencia=None,
             preservar=None, pousar_fn=None) -> dict:
    """Preserva (collection_run + raw_asset), refaz o READY com o RAW_OBSERVATION_ID real e, com
    `pousar`, poe na Sala canonica. `persistencia`/`preservar`/`pousar_fn` injectam-se nos testes."""
    import linha_busca as LB
    corrida = corrida or "LINHA-BUSCA-RAW-%s" % datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    paginas = paginas_admitidas(pastas)
    if persistencia is None:
        from orquestrador import persistencia as PERS
        persistencia = PERS.dependencias_do_runtime()
    if persistencia.memoria is None:
        raise SystemExit("RECUSADO: sem memoria canonica (%s). Sem collection_run/raw_asset nao ha RAW, e sem "
                         "RAW a Sala recusa. Declare SINTONIA_COLLECTION_DSN (operacional) ou "
                         "BANCO_DESCARTAVEL_URL (ensaio)." % persistencia.ESTADO)
    if preservar is None:
        from guarda import preservar_coleta as PC
        armazem = PC.ArmazemLocal(persistencia.raiz_do_armazem)

        def preservar(run, artefatos, bytes_de):
            return PC.preservar(run, artefatos, armazem, bytes_de, memoria=persistencia.memoria)
    por_sha = {p["RAW"]["SHA256"]: p for p in paginas}
    run = a_corrida(corrida, paginas)
    recibo = preservar(run, [artefato(p) for p in paginas], lambda o: por_sha[o["SHA256"]]["DADOS"])
    ids = {}
    for o in recibo.get("RAW_OBSERVATIONS") or []:
        if o.get("RUN_ID") == corrida and isinstance(o.get("RAW_OBSERVATION_ID"), int):
            ids.setdefault(o.get("SHA256"), o["RAW_OBSERVATION_ID"])
    prontos, relato = [], []
    for p in paginas:
        raw, e = p["RAW"], p["LIVRO"]
        rid = ids.get(raw["SHA256"])
        linha = {"SHA256": raw["SHA256"], "URL": raw["SOURCE_URL"], "SOURCE_ID": raw["SOURCE_ID"],
                 "RAW_OBSERVATION_ID": rid}
        if rid is None:
            linha["ESTADO"] = "SEM_RAW_CANONICO"                  # nao se pousa sem linhagem
            relato.append(linha)
            continue
        r = {"UNIVERSO": e.get("UNIVERSO"), "CONSULTA": (raw.get("PROVENIENCIA") or {}).get("CONSULTA")}
        a = LB.admitir(p["DADOS"], raw.get("MEDIA_TYPE") or "", raw["SOURCE_URL"], {"SOURCE_ID": raw["SOURCE_ID"]},
                       r, raw["SHA256"], raw["CAPTURED_AT"], corrida, raw_asset_id=rid)
        linha["ADMISSION"] = {k: a[k] for k in ("RESULTADO", "REGRA", "MOTIVO")}
        if a["READY"]:
            prontos.append(a["READY"])
            linha["ESTADO"] = "PRONTO_COM_RAW"
        else:
            linha["ESTADO"] = "ADMISSION_%s" % a["RESULTADO"]
        relato.append(linha)
    pousado = None
    if pousar and prontos:
        if pousar_fn is None:
            import sala_de_espera as SE
            SE.exigir_canonica()                               # Sala canonica ou nada; nunca ficheiro
            pousar_fn = SE.pousar
        pousado = pousar_fn(corrida, prontos)
    unicos = {x["ITEM_ID"] for x in prontos}
    return {"CORRIDA": corrida, "PAGINAS_ADMITIDAS_LIDAS": len(paginas),
            "RAW": {"RUN_STATE": recibo.get("RUN_STATE"), "OBSERVACOES": len(ids),
                    "MEMORIA": (recibo.get("MEMORIA") or {}).get("APLICADA"),
                    "FECHO": (recibo.get("FECHO_NO_BANCO") or {}).get("STATUS_NO_BANCO")},
            "PRONTOS_COM_RAW": len(prontos), "ITENS_UNICOS": len(unicos), "POUSADO": pousado,
            "PAGINAS": relato, "READY": prontos}


def main(argv) -> int:
    arg = dict(a[2:].split("=", 1) for a in argv[1:] if a.startswith("--") and "=" in a)
    if "--repousar" not in argv:
        print(__doc__)
        return 2
    pastas = [x for x in arg["saidas"].split(";") if x.strip()]
    doc = repousar(pastas, corrida=arg.get("corrida"), pousar="--pousar" in argv)
    saida = Path(pastas[0]).parent
    (saida / ("REPOUSO-%s.json" % doc["CORRIDA"])).write_text(
        json.dumps(doc, ensure_ascii=False, indent=1, default=str) + "\n", encoding="utf-8")
    print(json.dumps({k: doc[k] for k in ("CORRIDA", "PAGINAS_ADMITIDAS_LIDAS", "RAW", "PRONTOS_COM_RAW",
                                          "ITENS_UNICOS", "POUSADO")}, ensure_ascii=False, default=str))
    return 0 if (not ("--pousar" in argv) or doc["POUSADO"] is not None) else 1


if __name__ == "__main__":
    sys.path.insert(0, str(RAIZ / "coleta"))
    sys.exit(main(sys.argv))
