#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""MATERIAL ITALIANO REAL CHEGA A SALA — ida, volta, e repeticao.

    BANCO_DESCARTAVEL_URL=postgresql://postgres:descartavel@localhost:5432/descartavel \\
        python3 provas/o_material_italiano_chega_a_sala.py

O QUE ELA MEDE
--------------
Uma coisa so, e a mais dificil de fingir: que material italiano REAL — bytes
com SHA no livro, preservados nesta arvore — atravessa a Collection inteira e
POUSA na Sala de Espera CANONICA, que e uma tabela PostgreSQL e nao um ficheiro.

    SOURCE -> REQUEST -> ORCHESTRATOR -> EXECUTOR -> RUN -> RAW -> STORAGE
           -> DERIVED -> STRUCTURED -> ADMISSION -> READY -> WAITING_ROOM

E depois a mesma estrada ao contrario, item a item, sem nenhuma ligacao por
POSICAO DE LISTA: cada degrau e alcancado pela CHAVE que o anterior declarou.

    UMA CADEIA LIGADA POR POSICAO NAO E UMA CADEIA:
    E DUAS LISTAS DO MESMO TAMANHO.

O QUE ELA NAO FAZ
-----------------
⚠️ NAO ADQUIRE NADA DA REDE, e diz porque: nesta sessao a politica de egresso
responde `403 CONNECT` a TODOS os hospedeiros externos. Isso nao e uma fonte
morta e nao e uma rota partida — e o ambiente. O que ela mede e o
REPROCESSAMENTO do que ja foi colhido, que e a primeira meta desta missao.

    FIXTURE PROVA PARSER. SO A INTERNET PROVA AQUISICAO.
    E ESTA PROVA NAO DIZ TER PROVADO AQUISICAO.

⚠️ NAO CHAMA `pousar()`, nem `pronto_para_inteligencia()`, nem `admitir()`.
Aperta o botao em `orquestrador.correr()` e pergunta AO BANCO o que ficou.

    UMA PROVA QUE COMECA PELO MEIO NAO PROVA A ESTRADA:
    PROVA O PEDACO POR ONDE ELA COMECOU.
"""
import io
import json
import os
import subprocess
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)
import _gavetas                                    # noqa: E402,F401
import coleta_checkpoint as cc                     # noqa: E402
import italy_executor as ie                        # noqa: E402
import sala_de_espera as espera                    # noqa: E402
from pedido import Pedido                          # noqa: E402

#: A corrida-piloto REAL cujos bytes estao nesta arvore. Escolhida por ser a
#: unica das seis cujas dez observacoes tem ficheiro presente — medido, e nao
#: escolhido por dar bom resultado.
PILOT = "PILOT_RUN_20260907153737_4c34b3"

ESTRADA = ("REQUEST", "ORCHESTRATOR", "EXECUTOR", "RUN", "RAW", "STORAGE",
           "DERIVED", "STRUCTURED", "ADMISSION", "READY", "WAITING_ROOM")

FALHAS, PASSOU = [], []
SAIDA = os.path.join(RAIZ, "system-map", "data",
                     "material-italiano-na-sala.observado.json")


def T(nome, condicao, detalhe=""):
    (PASSOU if condicao else FALHAS).append(nome)
    print("  %s  %s%s" % ("ok  " if condicao else "FALHA", nome,
                          ("" if condicao else "\n        " + detalhe)))


def _psql(url, sql):
    r = subprocess.run(["psql", "-X", "-q", "-A", "-t", "-F", "\x1f",
                        "-v", "ON_ERROR_STOP=1", url, "-c", sql],
                       capture_output=True, text=True)
    if r.returncode != 0:
        raise SystemExit("psql falhou: %s" % r.stderr[:400])
    return [l.split("\x1f") for l in r.stdout.splitlines() if l.strip()]


def _memoria(url):
    import importlib.util as u
    sp = u.spec_from_file_location(
        "prova_pg", os.path.join(RAIZ, "provas",
                                 "preservar_coleta_no_postgres.py"))
    m = u.module_from_spec(sp)
    sp.loader.exec_module(m)
    return m.MemoriaPostgres(url)


def aplicar_migrations(url):
    pasta = os.path.join(RAIZ, "supabase", "migrations")
    for f in sorted(os.listdir(pasta)):
        if not f.endswith(".sql") or f.split("_", 1)[0] in ("008",):
            continue
        r = subprocess.run(["psql", url, "-v", "ON_ERROR_STOP=1", "-q",
                            "-f", os.path.join(pasta, f)],
                           capture_output=True, text=True)
        if r.returncode != 0:
            raise SystemExit("migration %s falhou:\n%s" % (f, r.stderr[:500]))


def main():
    url = os.environ.get("BANCO_DESCARTAVEL_URL")
    if not url:
        print("FALTA AMBIENTE DESCARTAVEL — e SKIP != PASS.")
        print("  BANCO_DESCARTAVEL_URL")
        print("MATERIAL_ITALIANO_NA_SALA = NOT_MEASURED")
        return 2
    os.environ["SINTONIA_SALA_BACKEND"] = "POSTGRES"
    os.environ["SINTONIA_SALA_DSN"] = url

    import pathlib
    import tempfile
    import admissao as adm
    adm.LIVRO = (pathlib.Path(tempfile.mkdtemp(prefix="livro-it-"))
                 / "LIVRO-DE-DECISOES.json")

    print("=" * 72)
    print("MATERIAL ITALIANO REAL CHEGA A SALA")
    print("  corrida-piloto reprocessada: %s" % PILOT)
    aplicar_migrations(url)

    # ── A SALA CANONICA, E NAO UM FICHEIRO ─────────────────────────────
    e = espera.estado_operacional()
    T("a Sala usada e a CANONICA (PostgreSQL), e ela diz que e",
      e["BACKEND"] == espera.BACKEND_POSTGRES and e["CANONICO"],
      "backend=%s canonico=%s" % (e["BACKEND"], e["CANONICO"]))

    antes = espera.listar_pendentes()
    T("P0_a_sala_comeca_VAZIA", not antes, "ja havia %d a espera" % len(antes))

    # ── O BALCAO: a colheita do piloto, traduzida SEM REDE ─────────────
    r_colher = ie.colher(PILOT)
    T("as dez observacoes do piloto traduzem-se, e TEM bytes no armazem",
      r_colher["OBSERVACOES_DESTA_CORRIDA"] == 10
      and r_colher["COM_BYTES_NO_ARMAZEM"] == 10,
      json.dumps(r_colher, ensure_ascii=False))

    # ── O BOTAO ────────────────────────────────────────────────────────
    import orquestrador as orq
    p = Pedido(alvo="T3", filtros={"pais": "IT"})
    recibo = orq.correr(p, memoria=_memoria(url), banco_do_rastro=cc.Banco(url),
                        colheita_da_corrida=PILOT)
    recibo.pop("_plano", None)
    run_id = recibo["RUN_ID"]
    ing = recibo.get("INGRESSO") or {}
    dv = recibo.get("DERIVACAO") or {}
    es = recibo.get("ESTRUTURACAO") or {}
    ad = recibo.get("ADMISSAO") or {}

    print()
    print("  A ESTRADA, DEGRAU A DEGRAU")
    visto = {}

    def degrau(nome, ok, prova):
        visto[nome] = {"OBSERVED": bool(ok), "EVIDENCE": prova}
        T("%-12s %s" % (nome, "atravessou"), ok, prova)

    degrau("REQUEST", (recibo.get("PEDIDO") or {}).get("alvo") == "T3",
           "alvo=%s pais=%s" % ((recibo.get("PEDIDO") or {}).get("alvo"),
                                (recibo.get("PEDIDO") or {}).get("filtros")))
    degrau("ORCHESTRATOR", bool(recibo.get("ACTOR")) and bool(run_id),
           "ACTOR=%s RUN_ID=%s" % (recibo.get("ACTOR"), run_id))
    degrau("EXECUTOR", (recibo.get("COLHEITA_ENCONTRADA") or 0) == 10,
           "colheita=%s" % recibo.get("COLHEITA_ENCONTRADA"))

    corridas = _psql(url, "select run_id, status from public.collection_run "
                          "where run_id = '%s'" % run_id)
    degrau("RUN", len(corridas) == 1,
           "collection_run: %s" % corridas)

    raws = _psql(url, "select id, storage_path, sha256, captured_at, source_id "
                      "from public.raw_asset where run_id = '%s' order by id"
                      % run_id)
    degrau("RAW", len(raws) == 10, "%d linhas em raw_asset" % len(raws))

    objs = _psql(url, "select count(*) from public.storage_object o "
                      "join public.raw_asset a on a.storage_object_id = o.id "
                      "where a.run_id = '%s'" % run_id)
    degrau("STORAGE", objs and int(objs[0][0]) == 10,
           "%s copias ligadas por chave estrangeira" % (objs and objs[0][0]))

    ders = _psql(url, "select d.id, d.raw_asset_id, d.sha256 "
                      "from public.derived_artifact d "
                      "join public.raw_asset a on a.id = d.raw_asset_id "
                      "where a.run_id = '%s' order by d.id" % run_id)
    degrau("DERIVED", len(ders) == 7, "%d derivados" % len(ders))

    docs = _psql(url, "select derived_artifact_id, source_id "
                      "from public.documento_estruturado "
                      "where run_id = '%s' order by derived_artifact_id" % run_id)
    degrau("STRUCTURED", len(docs) == 7, "%d documentos estruturados" % len(docs))

    degrau("ADMISSION", (ad.get("por_resultado") or {}).get("SIM") == 7,
           "por_resultado=%s" % ad.get("por_resultado"))
    degrau("READY", ad.get("prontos") == 7, "prontos=%s" % ad.get("prontos"))

    sala = _psql(url, "select ordem, item_id, raw_observation_id, source_id, "
                      "captured_at, estado_da_fila from public.sala_de_espera "
                      "where run_id = '%s' order by ordem" % run_id)
    degrau("WAITING_ROOM", len(sala) == 7, "%d na Sala" % len(sala))

    depois = espera.listar_pendentes()
    T("WAITING_ROOM_DELTA == ADMITTED_READY_FOR_WAITING_ROOM",
      len(depois) - len(antes) == ad.get("prontos"),
      "delta=%d prontos=%s" % (len(depois) - len(antes), ad.get("prontos")))

    # ── NENHUM CAMPO DA SALA FICOU `NAO SEI` POR TRANSPORTE ────────────
    # ⚠️ A DIFERENCA QUE IMPORTA: `FACT_TIME = NAO SEI` e HONESTO — o boletim
    # nao declara a data do fato, e inventa-la seria fabricar. `CAPTURED_AT =
    # NAO SEI` NAO era honesto: o valor existia, medido, e perdia-se.
    print()
    print("  O QUE A SALA GUARDOU")
    sem_obs = [l for l in sala if not (l[2] or "").strip()]
    T("toda a unidade na Sala nomeia a OBSERVACAO que a originou",
      not sem_obs, "%d sem raw_observation_id" % len(sem_obs))
    sem_fonte = [l for l in sala if not (l[3] or "").strip()
                 or l[3] == "NAO SEI"]
    T("toda a unidade na Sala nomeia a FONTE dela",
      not sem_fonte, "%d sem source_id" % len(sem_fonte))
    sem_captura = [l for l in sala if (l[4] or "").strip() in ("", "NAO SEI")]
    T("toda a unidade na Sala traz CAPTURED_AT medido, e nao `NAO SEI`",
      not sem_captura, "%d com CAPTURED_AT ausente" % len(sem_captura))
    # E ele e a hora REAL da captura, e nao a do reprocessamento.
    de_2026_09_07 = [l for l in sala if (l[4] or "").startswith("2026-09-07")]
    T("e CAPTURED_AT e a hora da CAPTURA (2026-09-07), nao a do reprocessamento",
      len(de_2026_09_07) == len(sala),
      "so %d de %d trazem a data real" % (len(de_2026_09_07), len(sala)))

    # ── A ESTRADA AO CONTRARIO, POR CHAVE E NUNCA POR POSICAO ──────────
    print()
    print("  A VOLTA — de UM item da Sala ate a fonte, so por chave")
    alvo = sala[0]
    ordem, item_id, obs_id, fonte_sala, captura, fila = alvo
    cadeia = {}
    cadeia["WAITING_ROOM"] = {"run_id": run_id, "ordem": int(ordem),
                              "item_id": item_id,
                              "raw_observation_id": int(obs_id)}
    # READY -> ADMISSION: o `item_id` e `derived:<id>`, e o id e do registo.
    der_id = int(str(item_id).split(":", 1)[1])
    cadeia["READY"] = {"ITEM_ID": item_id, "DERIVED_ARTIFACT_ID": der_id}
    d = _psql(url, "select derived_artifact_id, source_id, run_id "
                   "from public.documento_estruturado "
                   "where derived_artifact_id = %d" % der_id)
    T("VOLTA 1 · o item da Sala encontra o STRUCTURED pelo proprio id",
      len(d) == 1, "documento_estruturado: %s" % d)
    cadeia["STRUCTURED"] = {"derived_artifact_id": der_id,
                            "source_id": d[0][1] if d else None}
    da = _psql(url, "select id, raw_asset_id, parent_sha256, storage_path "
                    "from public.derived_artifact where id = %d" % der_id)
    T("VOLTA 2 · o STRUCTURED encontra o DERIVED pela chave dele",
      len(da) == 1, "derived_artifact: %s" % da)
    raw_id = int(da[0][1])
    cadeia["DERIVED"] = {"id": der_id, "raw_asset_id": raw_id,
                         "parent_sha256": da[0][2]}
    T("VOLTA 3 · o DERIVED aponta para a MESMA observacao que a Sala nomeia",
      raw_id == int(obs_id),
      "derived.raw_asset_id=%d · sala.raw_observation_id=%s" % (raw_id, obs_id))
    ra = _psql(url, "select id, run_id, storage_object_id, sha256, "
                    "captured_at, source_id, source_url "
                    "from public.raw_asset where id = %d" % raw_id)
    T("VOLTA 4 · a OBSERVACAO existe, e e da corrida desta prova",
      len(ra) == 1 and ra[0][1] == run_id, "raw_asset: %s" % ra)
    cadeia["RAW"] = {"id": raw_id, "run_id": ra[0][1], "sha256": ra[0][3],
                     "captured_at": ra[0][4], "source_id": ra[0][5]}
    so = _psql(url, "select id, storage_path, sha256, bytes "
                    "from public.storage_object where id = %s" % ra[0][2])
    T("VOLTA 5 · a observacao encontra a COPIA pela chave estrangeira",
      len(so) == 1 and so[0][2] == ra[0][3],
      "storage_object: %s" % so)
    cadeia["STORAGE"] = {"id": int(so[0][0]), "sha256": so[0][2],
                         "bytes": int(so[0][3])}
    cr = _psql(url, "select run_id, actor, started_at, status "
                    "from public.collection_run where run_id = '%s'" % ra[0][1])
    T("VOLTA 6 · a observacao encontra a CORRIDA que a produziu",
      len(cr) == 1, "collection_run: %s" % cr)
    cadeia["RUN"] = {"run_id": cr[0][0], "actor": cr[0][1]}
    # E a fonte fecha o circulo: a mesma que a Sala declara.
    T("VOLTA 7 · a FONTE da observacao e a mesma que a Sala declara",
      ra[0][5] == fonte_sala,
      "raw_asset.source_id=%s · sala.source_id=%s" % (ra[0][5], fonte_sala))
    cadeia["SOURCE"] = {"source_id": ra[0][5], "source_url": ra[0][6]}
    # E os BYTES ainda la estao, e sao os do livro italiano.
    livro = [o for o in ie.observacoes_da_corrida(PILOT)
             if o.get("RAW_SHA256") == ra[0][3]]
    T("VOLTA 8 · o SHA da observacao e o que o livro italiano registou",
      len(livro) == 1,
      "sha=%s encontrado no livro: %d vez(es)" % (ra[0][3][:16], len(livro)))
    cadeia["LIVRO_ITALIANO"] = {"SOURCE_ID": livro[0]["SOURCE_ID"],
                                "SOURCE_URL": livro[0]["SOURCE_URL"],
                                "CAPTURED_AT": livro[0]["CAPTURED_AT"],
                                "RUN_ID": livro[0]["RUN_ID"]} if livro else {}

    # ── A REPETICAO — retry nao duplica nada ───────────────────────────
    print()
    print("  A REPETICAO — o retry da MESMA corrida")
    n_raw_antes = len(_psql(url, "select id from public.raw_asset"))
    n_so_antes = len(_psql(url, "select id from public.storage_object"))
    n_sala_antes = len(_psql(url, "select ordem from public.sala_de_espera"))
    prontos = [adm_i for adm_i in []]                       # noqa: F841
    # A MESMA corrida, o MESMO conteudo: tem de dar REUSED e nao escrever.
    unidades = espera.ler(run_id)["ITENS"]
    r2 = espera.pousar(run_id, unidades)
    T("pousar a MESMA corrida com o MESMO conteudo devolve REUSED",
      r2["ESTADO"] == espera.JA_ESTAVA, "devolveu %s" % r2["ESTADO"])
    T("e REUSED nao e PRODUCED: nenhuma linha nova na Sala",
      len(_psql(url, "select ordem from public.sala_de_espera")) == n_sala_antes,
      "a Sala passou de %d linhas para %d"
      % (n_sala_antes,
         len(_psql(url, "select ordem from public.sala_de_espera"))))
    T("o retry nao duplicou RAW",
      len(_psql(url, "select id from public.raw_asset")) == n_raw_antes,
      "raw_asset passou de %d" % n_raw_antes)
    T("o retry nao duplicou STORAGE",
      len(_psql(url, "select id from public.storage_object")) == n_so_antes,
      "storage_object passou de %d" % n_so_antes)

    # A mesma corrida com conteudo DIFERENTE: recusa, e nao escreve.
    try:
        espera.pousar(run_id, unidades[:-1])
        conflitou = False
    except espera.ConflitoDeCorrida:
        conflitou = True
    T("a MESMA corrida com conteudo DIFERENTE e recusada, e nada e escrito",
      conflitou
      and len(_psql(url, "select ordem from public.sala_de_espera")) == n_sala_antes,
      "uma RUN_ID nao pode contar duas historias")

    # ── A SAIDA DA SALA EXISTE, E NAO E CONSUMIDA AQUI ─────────────────
    print()
    print("  A SAIDA — existe, e esta missao NAO a usa no material real")
    pendentes = espera.listar_pendentes(limite=3)
    T("WAITING_ITEM_CAN_BE_SELECTED", len(pendentes) >= 1,
      "listar_pendentes devolveu %d" % len(pendentes))
    T("e a Collection NAO consome o material do canario",
      all(l[5] == espera.A_ESPERA for l in
          _psql(url, "select ordem, item_id, raw_observation_id, source_id, "
                     "captured_at, estado_da_fila from public.sala_de_espera "
                     "where run_id = '%s' order by ordem" % run_id)),
      "algum item real saiu da fila nesta prova")

    estado = {
        "O_QUE_ISTO_E": ("Material italiano REAL, reprocessado da corrida "
                         "piloto %s, atravessando a Collection ate a Sala de "
                         "Espera canonica em PostgreSQL." % PILOT),
        "COMO_REFAZER": ("BANCO_DESCARTAVEL_URL=... python3 "
                         "provas/o_material_italiano_chega_a_sala.py"),
        "AMBIENTE": "DESCARTAVEL",
        "AQUISICAO_NOVA": ("NAO — a politica de egresso desta sessao responde "
                           "403 CONNECT a todos os hospedeiros externos. Isto e "
                           "REPROCESSAMENTO de bytes ja colhidos, com SHA no "
                           "livro italiano."),
        "RUN_ID": run_id,
        "CORRIDA_DE_ORIGEM": PILOT,
        "ESTRADA": {k: visto.get(k) for k in ESTRADA},
        "CADEIA_DE_VOLTA": cadeia,
        "WAITING_ROOM_BEFORE": len(antes),
        "WAITING_ROOM_AFTER": len(depois),
        "WAITING_ROOM_DELTA": len(depois) - len(antes),
        "SALA": [{"ORDEM": int(l[0]), "ITEM_ID": l[1],
                  "RAW_OBSERVATION_ID": int(l[2]), "SOURCE_ID": l[3],
                  "CAPTURED_AT": l[4], "ESTADO_DA_FILA": l[5]} for l in sala],
        "PASSOU": len(PASSOU), "FALHOU": len(FALHAS),
    }
    os.makedirs(os.path.dirname(SAIDA), exist_ok=True)
    with io.open(SAIDA, "w", encoding="utf-8") as f:
        json.dump(estado, f, ensure_ascii=False, indent=1)
        f.write("\n")

    print()
    print("  gravado: %s" % os.path.relpath(SAIDA, RAIZ))
    print()
    print("WAITING_ROOM_BEFORE = %d" % len(antes))
    print("WAITING_ROOM_AFTER  = %d" % len(depois))
    print("WAITING_ROOM_DELTA  = %d" % (len(depois) - len(antes)))
    print("VALID_REAL_MATERIAL_REACHED_WAITING_ROOM = %s"
          % ("YES" if not FALHAS and len(sala) > 0 else "NO"))
    print("MATERIAL_ITALIANO_NA_SALA = %s · %d passaram · %d falharam"
          % ("PASS" if not FALHAS else "FAIL", len(PASSOU), len(FALHAS)))
    return 1 if FALHAS else 0


if __name__ == "__main__":
    raise SystemExit(main())
