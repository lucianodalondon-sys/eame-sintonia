#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""TEMPO-E-LUGAR · antes/depois — a estrada REAL, sobre as 78 da Sala, num banco
DESCARTÁVEL. Nunca a Sala real.

Para cada item da Sala real (lido de um dump JSON feito em modo só-leitura):

    livro do coletor (RAW_SHA256)  ->  italy_executor.traduzir
      -> orquestrador.pela_entrada  (raw_asset, no banco descartável)
      -> orquestrador.pela_derivacao (derived_artifact)
      -> orquestrador.pela_estruturacao (documento_estruturado)
      -> orquestrador.item_documental_para_a_porta
      -> orquestrador.pela_porta     (admissão + sala_de_espera descartável)

As mesmas peças, na mesma ordem, que `orquestrador.correr` usa. Os bytes são os
guardados (sha256 conferido pelo medidor); não se abre rede.

Corre-se DUAS vezes: com `--arvore` na árvore de base (código antigo) e na
árvore nova. A diferença entre as duas é o conserto — e não o ensaio.

    py provas/tempo_e_lugar_replay.py --arvore <raiz> --sala-json <dump>
       --medida <medida-antes.json> --livros "<glob;glob>" --saida <out.json>
"""
import argparse
import glob
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

CAMPOS = ("PUBLISHED_AT", "SOURCE_LOCATION", "FACT_TIME", "FACT_LOCATION",
          "FACT_TIME_BASIS", "FACT_LOCATION_BASIS", "OBSERVED_AT")
NS = "NAO SEI"


def carregar_livros(padroes):
    por_sha = {}
    for padrao in padroes:
        for f in glob.glob(padrao):
            with open(f, encoding="utf-8", errors="replace") as fh:
                for linha in fh:
                    try:
                        o = json.loads(linha)
                    except json.JSONDecodeError:
                        continue
                    s = o.get("RAW_SHA256")
                    # a observacao mais completa ganha (a que tem RAW_PATH)
                    if s and (s not in por_sha or (o.get("RAW_PATH") and not por_sha[s].get("RAW_PATH"))):
                        por_sha[s] = o
    return por_sha


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--arvore", required=True)
    ap.add_argument("--sala-json", required=True)
    ap.add_argument("--medida", required=True)
    ap.add_argument("--livros", required=True)
    ap.add_argument("--saida", required=True)
    a = ap.parse_args()
    arvore = Path(a.arvore).resolve()

    for p in ("", "coleta", "orquestrador", "admissao", "guarda", "regras"):
        sys.path.insert(0, str(arvore / p))
    os.chdir(arvore)
    import _gavetas  # noqa: F401
    spec_e = __import__("importlib.util").util.spec_from_file_location(
        "ensaio_offline", arvore / "scripts" / "micro_coleta" / "ensaio_offline.py")
    E = __import__("importlib.util").util.module_from_spec(spec_e)
    spec_e.loader.exec_module(E)

    itens_sala = json.load(open(a.sala_json, encoding="utf-8"))
    medida = {x["OBS"]: x for x in json.load(open(a.medida, encoding="utf-8"))["ITENS"]}
    livros = carregar_livros([x for x in a.livros.split(";") if x])

    tmp = Path(tempfile.mkdtemp(prefix="tempo-lugar-"))
    base = E.Base(tmp / "pg")
    env_pg = {**os.environ, "PATH": str(E.PG_BIN) + os.pathsep + os.environ.get("PATH", "")}
    r = base.subir(arvore, env_pg)
    if r["CODIGO"] != 0:
        base.descer()
        raise SystemExit("migrations falharam: %s" % r["ERRO"])
    assert ":54330/" not in base.url, "isto e a Sala real"
    # ── O AMBIENTE: SO O BANCO DESCARTAVEL, E A REDE FECHADA ──────────────
    for v in ("SINTONIA_COLLECTION_DSN", "SUPABASE_DB_URL", "SINTONIA_ARMAZEM_RAIZ"):
        os.environ.pop(v, None)
    os.environ.update({
        "BANCO_DESCARTAVEL_URL": base.url,
        "SINTONIA_SALA_BACKEND": "POSTGRES", "SINTONIA_SALA_DSN": base.url,
        "SINTONIA_PSQL_EXE": base.exe("psql"), "SINTONIA_PSQL": base.exe("psql"),
        "HTTP_PROXY": "http://127.0.0.1:9", "HTTPS_PROXY": "http://127.0.0.1:9",
        "NO_PROXY": "127.0.0.1,localhost",
    })
    try:
        import admissao as adm
        import ingresso as ing
        import italy_executor as ex
        import orquestrador as ORQ
        import persistencia as P
        adm.LIVRO = tmp / "LIVRO-DE-DECISOES.json"
        adm.QUARENTENA_HUMANA = tmp / "QUARENTENA.jsonl"
        pers = P.dependencias_do_runtime(dict(os.environ))
        assert pers.ESTADO == P.DESCARTAVEL, pers.PORQUE
        armazem = ing.ArmazemLocal(str(tmp / "armazem"))

        grupos = {}
        sem = []
        for it in itens_sala:
            m = medida.get(it["obs"]) or {}
            o = livros.get(it["sha256"].strip())
            if not o or m.get("BYTES_ACHADOS", NS) == NS:
                sem.append({"OBS": it["obs"], "PORQUE": "sem livro" if not o else "sem bytes"})
                continue
            o = dict(o, RAW_PATH=m["BYTES_ACHADOS"])
            grupos.setdefault((it["run_id"], it["universo"]), []).append((it, o))

        resultados = []
        for n, ((run_orig, universo), lista) in enumerate(sorted(grupos.items())):
            run_id = "TL-%02d-%s" % (n, run_orig[-16:])
            corrida = {"RUN_ID": run_id, "PLATFORM": "HTTP direto",
                       "ACTOR": "coleta/italy_executor.py", "ACTOR_VERSION": "tempo-lugar",
                       "RULE_VERSION": "tempo-lugar", "SOURCE_COUNTRY": "IT",
                       "STARTED_AT": ORQ.agora(), "MISSION": "TEMPO-E-LUGAR replay"}
            itens = [ex.traduzir(o) for _, o in lista]
            ent = ORQ.pela_entrada(itens, corrida, memoria=pers.memoria, armazem=armazem)
            der = ORQ.pela_derivacao(ent.get("PARA_A_DERIVACAO") or [], run_id=run_id,
                                     armazem=armazem, memoria=pers.memoria,
                                     source_id=ent.get("FONTE_PROVADA"),
                                     nao_derivaveis=ent.get("SEM_BYTES_PARA_DERIVAR") or [])
            est = ORQ.pela_estruturacao(der, run_id=run_id, armazem=armazem,
                                        memoria=pers.memoria, source_id=ent.get("FONTE_PROVADA"))
            julgar = [ORQ.item_documental_para_a_porta(e, source_id=ent.get("FONTE_PROVADA"))
                      for e in (est.get("ESTRUTURADOS") or [])]
            porta = ORQ.pela_porta(julgar, universo, run_id)
            # o READY de cada item julgado, tambem dos que a porta nao admitiu,
            # SO para medir os campos (a Sala descartavel guarda so os SIM)
            por_raw = {}
            for x in julgar:
                d = adm.Decisao(item=x["id"], universo=universo, resultado=adm.SIM,
                                regra="medicao", motivo="medicao")
                por_raw[x.get("raw_asset_id")] = adm.pronto_para_inteligencia(
                    ing.para_a_porta(x), d)
            for it, o in lista:
                rd = next((v for k, v in por_raw.items()
                           if k is not None and _sha_de(pers, k) == it["sha256"].strip()),
                          None)
                resultados.append({"OBS_SALA_REAL": it["obs"], "SOURCE_ID": it["source_id"],
                                   "RUN_ID": run_id, "UNIVERSO": universo,
                                   "READY": {c: (rd or {}).get(c, "SEM_READY") for c in CAMPOS},
                                   "PRONTOS_NA_CORRIDA": porta.get("prontos"),
                                   "ENTRADA": {k: ent.get(k) for k in ("PRESERVADOS", "RECUSADOS",
                                                                      "PORQUE_RECUSADOS")}})
        sala = subprocess.run(
            [base.exe("psql"), "-X", "-A", "-t", "-c",
             "select coalesce(json_agg(json_build_object('run_id',run_id,'raw',raw_observation_id,"
             "'published_at',published_at,'source_location',source_location,'fact_time',fact_time,"
             "'fact_location',fact_location,'fact_time_basis',fact_time_basis,"
             "'fact_location_basis',fact_location_basis,'observed_at',observed_at)),'[]') "
             "from sala_de_espera", base.url],
            capture_output=True, text=True, encoding="utf-8", check=True).stdout.strip()
        sala_desc = json.loads(sala or "[]")
    finally:
        base.descer()
        shutil.rmtree(tmp, ignore_errors=True)

    resumo = {"ITENS_NA_SALA_REAL": len(itens_sala), "SEM_LIVRO_OU_BYTES": sem,
              "REPRODUZIDOS": len(resultados)}
    for c in CAMPOS:
        resumo["SAI_DE_NAO_SEI_" + c] = sum(
            1 for x in resultados if x["READY"][c] not in (NS, "SEM_READY", "", None))
    resumo["SEM_READY"] = sum(1 for x in resultados if x["READY"]["FACT_TIME"] == "SEM_READY")
    resumo["SALA_DESCARTAVEL_LINHAS"] = len(sala_desc)
    for c in ("published_at", "source_location", "fact_time", "fact_location",
              "fact_time_basis", "fact_location_basis"):
        resumo["SALA_DESCARTAVEL_" + c.upper() + "_PREENCHIDO"] = sum(
            1 for x in sala_desc if x[c] not in (NS, "", None))
    # as duas leis, medidas na saida
    resumo["FACT_TIME_IGUAL_A_PUBLISHED_AT"] = sum(
        1 for x in resultados if x["READY"]["FACT_TIME"] not in (NS, "SEM_READY")
        and x["READY"]["FACT_TIME"] == x["READY"]["PUBLISHED_AT"])
    resumo["FACT_LOCATION_IGUAL_A_SOURCE_LOCATION"] = sum(
        1 for x in resultados if x["READY"]["FACT_LOCATION"] not in (NS, "SEM_READY")
        and x["READY"]["FACT_LOCATION"] == x["READY"]["SOURCE_LOCATION"])
    out = {"ARVORE": str(arvore), "RESUMO": resumo, "ITENS": resultados,
           "SALA_DESCARTAVEL": sala_desc}
    with open(a.saida, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=1)
    print(json.dumps(resumo, ensure_ascii=False, indent=1))


_CACHE_SHA = {}


def _sha_de(pers, raw_id):
    """O sha256 do raw_asset descartavel — para ligar o READY ao item da Sala real."""
    if raw_id not in _CACHE_SHA:
        url = os.environ["BANCO_DESCARTAVEL_URL"]
        r = subprocess.run([os.environ["SINTONIA_PSQL_EXE"], "-X", "-A", "-t", "-c",
                            "select sha256 from raw_asset where id=%d" % int(raw_id), url],
                           capture_output=True, text=True, encoding="utf-8")
        _CACHE_SHA[raw_id] = r.stdout.strip()
    return _CACHE_SHA[raw_id]


if __name__ == "__main__":
    main()
