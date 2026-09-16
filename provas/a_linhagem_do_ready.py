#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""A LINHAGEM DO READY — do item pousado de volta ao byte preservado.

    BANCO_DESCARTAVEL_URL=postgresql://postgres@127.0.0.1:5433/descartavel \\
        python3 provas/a_linhagem_do_ready.py

A PERGUNTA
----------
    UM ITEM QUE CHEGOU COMO READY CONSEGUE PROVAR, DE FORMA DETERMINISTICA E
    CANONICA, DE QUAL RAW OBSERVATION E STORAGE OBJECT ELE VEIO?

⚠️ O QUE ESTA PROVA ENCONTROU ANTES DE EXISTIR A PONTE
-------------------------------------------------------
Sem `RAW_OBSERVATION_ID` no contrato, a unica volta possivel era procurar
`derived_artifact` pelo `sha256` do texto — e `derived_sha_idx` NAO e unico.
Medido neste mesmo banco, com a cadeia canonica inteira:

    dois PDFs DIFERENTES com o MESMO texto extraido
    -> 2 derivados com o mesmo sha256
    -> 2 observacoes, 2 objetos de armazem

        READY_TO_RAW (antes)  = AMBIGUOUS, e nao BROKEN.
        DOIS CANDIDATOS NAO SAO UMA LINHAGEM.

E AMBIGUOUS e pior do que BROKEN: uma cadeia partida vê-se; uma cadeia que
devolve dois candidatos plausiveis responde com confianca a pergunta errada.

O QUE ELA MEDE
--------------
A travessia inteira numa corrida so, com bytes REAIS, contra PostgreSQL 16
descartavel e sala descartavel — e depois a VOLTA, sempre a partir do que
esta pousado na sala, nunca do que o setup ja sabia.

    READY -> RAW_OBSERVATION_ID -> raw_asset -> storage_object -> bytes
                                             -> collection_run
                                             -> source_id

⚠️ A VOLTA COMECA NO FICHEIRO, E ISSO E A PROVA.
Ler o `raw_id` que o setup cunhou e depois «confirmar» que ele bate seria
medir a variavel, nao a estrada. Aqui abre-se o JSON da sala e resolve-se a
partir do que la esta escrito — como faria quem encontrasse o ficheiro sem
ter corrido nada.
"""
import io
import json
import os
import shutil
import subprocess
import sys
import tempfile

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)
sys.path.insert(0, os.path.join(RAIZ, "coleta"))
import _gavetas  # noqa: E402,F401

import admissao                                      # noqa: E402
import coleta_checkpoint as cc                       # noqa: E402
import rota_forward_documento as m2                  # noqa: E402
import sala_de_espera as espera                      # noqa: E402
from coleta import ingresso as ing                   # noqa: E402

RUN = "RUN-LINHAGEM"
RUN2 = "RUN-LINHAGEM-2"
_SO_VERIFICA = ("008",)
FONTE = "IT-T3-002"

fora = []


def caso(nome, condicao, detalhe=""):
    fora.append((nome, bool(condicao), detalhe))


def cadeia_de_migrations():
    pasta = os.path.join(RAIZ, "supabase", "migrations")
    return [f.split("_", 1)[0] for f in sorted(os.listdir(pasta))
            if f.endswith(".sql") and f.split("_", 1)[0] not in _SO_VERIFICA]


def aplicar_migrations(url):
    pasta = os.path.join(RAIZ, "supabase", "migrations")
    for n in cadeia_de_migrations():
        achados = [f for f in sorted(os.listdir(pasta)) if f.startswith(n + "_")]
        r = subprocess.run(["psql", "-v", "ON_ERROR_STOP=1", "-q", "-f",
                            os.path.join(pasta, achados[0]), url],
                           capture_output=True, text=True)
        if r.returncode != 0:
            print("FALHOU a aplicar %s\n%s" % (achados[0], r.stderr[:900]))
            raise SystemExit(1)


def o_pdf_da_fonte():
    import glob
    achados = sorted(glob.glob(os.path.join(
        RAIZ, "data", "collection-store", "italy", FONTE, "*", "*", "*.pdf")))
    if not achados:
        raise SystemExit("nao ha PDF preservado da fonte %s" % FONTE)
    return achados[0]


def _memoria(url):
    import importlib.util as u
    sp = u.spec_from_file_location(
        "prova_pg", os.path.join(RAIZ, "provas",
                                 "preservar_coleta_no_postgres.py"))
    m = u.module_from_spec(sp)
    sp.loader.exec_module(m)
    return m.MemoriaPostgres(url)


_ARMAZEM = []


def _armazem():
    if not _ARMAZEM:
        from guarda.preservar_coleta import ArmazemDeMentira
        _ARMAZEM.append(ArmazemDeMentira())
    return _ARMAZEM[0]


def canal_da_fonte(sql):
    import importlib.util as u
    sp = u.spec_from_file_location(
        "rota_m2", os.path.join(RAIZ, "provas", "a_rota_m2_atravessa.py"))
    m = u.module_from_spec(sp)
    sp.loader.exec_module(m)
    canal_id, _quem = m.canal_da_fonte(sql, FONTE)
    return canal_id


# ────────────────────────────────────────────────────────────────────────
# A VOLTA — e ela e uma consulta so, por id canonico
# ────────────────────────────────────────────────────────────────────────
def resolver(sql, unidade):
    """Do item pousado ate ao byte. NENHUMA heuristica, NENHUM sha, NENHUM path.

    ⚠️ A ENTRADA E A UNIDADE DA SALA, e mais nada. Nao recebe `raw_id` de
    fora: se o recebesse, esta funcao provaria que uma variavel do teste bate
    consigo propria.

    E `storage_object` NAO precisa de viajar no contrato: `raw_asset` ja aponta
    para a copia por chave estrangeira COMPOSTA `(storage_object_id, sha256)`,
    e por isso a copia sai deste mesmo join, sem segundo campo e sem segunda
    verdade.

        A MENOR IDENTIDADE QUE FECHA A ESTRADA E A CERTA.
    """
    ident = unidade.get("RAW_OBSERVATION_ID")
    if ident is None or str(ident).strip().upper() in (
            "NAO SEI", "NÃO SEI", "UNKNOWN", ""):
        return {"RESOLVIDO": False, "PORQUE": "a unidade nao nomeia observacao",
                "CANDIDATOS": 0}
    if not str(ident).isdigit():
        # Um id que nao e um id do banco nao se «tenta na mesma».
        return {"RESOLVIDO": False, "CANDIDATOS": 0,
                "PORQUE": "RAW_OBSERVATION_ID nao e um id de raw_asset: %r"
                          % ident}
    linhas = sql.executa(
        "select r.id, r.run_id, r.source_id, r.sha256, r.storage_object_id,"
        "       s.id, s.storage_path, s.sha256"
        "  from public.raw_asset r"
        "  left join public.storage_object s on s.id = r.storage_object_id"
        " where r.id = %d" % int(ident))
    if len(linhas) != 1:
        return {"RESOLVIDO": False, "CANDIDATOS": len(linhas),
                "PORQUE": "a observacao nomeada nao existe" if not linhas
                          else "mais de uma linha para um id — impossivel"}
    x = linhas[0]
    return {"RESOLVIDO": True, "CANDIDATOS": 1,
            "RAW_OBSERVATION_ID": int(x[0]), "RUN_ID": x[1],
            "SOURCE_ID": x[2], "RAW_SHA256": x[3],
            "STORAGE_OBJECT_ID": x[4], "STORAGE_PATH": x[6],
            "STORAGE_SHA256": x[7]}


def pela_procura_do_sha(sql, unidade):
    """A volta ANTIGA, para o contraste ficar medido e nao afirmado.

    Era a unica maneira antes da ponte: procurar o derivado pelo sha do texto.
    Ela continua aqui SO para medir quantos candidatos devolve.
    """
    linhas = sql.executa(
        "select d.id, d.raw_asset_id from public.derived_artifact d"
        " where d.sha256 = '%s'" % str(unidade.get("ITEM_ID") or "")[:64])
    return len(linhas)


def medir(url, sala):
    print("=" * 70)
    print("A LINHAGEM DO READY — %d migrations · sala descartavel"
          % len(cadeia_de_migrations()))
    aplicar_migrations(url)
    sql = cc.Banco(url)

    # ── 0 · O CONTRATO LEVA A OBSERVACAO ────────────────────────────────
    sonda = {"id": "sonda", "texto": "Ensaio de campo publicado com DOI",
             "source_id": "IT-T7-001", "fact_time": "2026-05-02",
             "raw_asset_id": 7}
    d = admissao.decidir(sonda, "T7", corrida="sonda")
    u0 = admissao.pronto_para_inteligencia(sonda, d)
    caso("L0_o_contrato_leva_RAW_OBSERVATION_ID",
         u0.get("RAW_OBSERVATION_ID") == 7 and len(u0) == 12,
         "%d campos · RAW_OBSERVATION_ID=%s" % (len(u0),
                                                u0.get("RAW_OBSERVATION_ID")))
    sem = {k: v for k, v in sonda.items() if k != "raw_asset_id"}
    u1 = admissao.pronto_para_inteligencia(
        sem, admissao.decidir(sem, "T7", corrida="sonda"))
    caso("L1_sem_observacao_o_campo_diz_NAO_SEI_e_nao_inventa",
         u1.get("RAW_OBSERVATION_ID") == "NAO SEI",
         "ausencia continua ausencia: %r" % u1.get("RAW_OBSERVATION_ID"))

    # ── 1 · A TRAVESSIA REAL, NUMA CORRIDA SO ───────────────────────────
    pdf = o_pdf_da_fonte()
    rel = os.path.relpath(pdf, RAIZ)
    r = ing.receber([{"SOURCE_ID": FONTE,
                      "SOURCE_URL": "https://exemplo.it/%s"
                                    % os.path.basename(pdf),
                      "STORAGE_LOCATION": rel}],
                    corrida={"RUN_ID": RUN, "PLATFORM": "HTTP direto",
                             "ACTOR": "coleta/italy_executor.py",
                             "ACTOR_VERSION": "adapter-v1",
                             "SOURCE_COUNTRY": "IT", "RULE_VERSION": "1",
                             "STARTED_AT": "2026-09-10T00:00:00Z"},
                    armazem=ing.ArmazemLocal(RAIZ),
                    memoria=_memoria(url), raiz=RAIZ, banco_do_rastro=sql)
    obs = (r["RAW"] or {}).get("RAW_OBSERVATIONS") or []
    raw_id = obs[0]["RAW_OBSERVATION_ID"] if len(obs) == 1 else None
    canal_id = canal_da_fonte(sql)
    unidade = {"RAW_ASSET_ID": raw_id, "PDF": pdf, "SOURCE_ID": FONTE,
               "ROUTE_CLASS_ID": "RC-1", "TIPO": "nota_tecnica",
               "CAPTURED_AT": "2026-09-10T00:00:00Z",
               "URL": "https://exemplo.it/%s" % os.path.basename(pdf)}
    saida = m2.atravessar(sql, unidade=unidade, run_id=RUN,
                          armazem=_armazem(), memoria=_memoria(url),
                          canal_id=canal_id)
    caso("L2_a_unidade_pousou_na_sala",
         (saida.get("READY") or {}).get("ESTADO") == espera.POUSOU,
         "estado=%s" % (saida.get("READY") or {}).get("ESTADO"))
    if (saida.get("READY") or {}).get("ESTADO") != espera.POUSOU:
        import pprint
        print("DIAGNOSTICO — a travessia parou:")
        for k in ("DERIVED", "STRUCTURED", "ADMISSION", "READY", "PORQUE_PAROU"):
            v = saida.get(k)
            print("  %-14s %s" % (k, str(v)[:400]))
        return None, None, sql

    # ⚠️ DAQUI PARA BAIXO SO SE LE O FICHEIRO. `raw_id` fica guardado apenas
    # para CONFERIR o resultado no fim — nunca para o alcancar.
    corpo = json.loads(io.open(espera.caminho_da_corrida(RUN),
                               encoding="utf-8").read())
    pousada = (corpo.get("ITENS") or [{}])[0]

    # ── 2 · READY -> RAW ────────────────────────────────────────────────
    res = resolver(sql, pousada)
    caso("L3_READY_TO_RAW_resolve_a_UMA_observacao",
         res["RESOLVIDO"] and res["CANDIDATOS"] == 1,
         "candidatos=%d · raw=%s" % (res["CANDIDATOS"],
                                     res.get("RAW_OBSERVATION_ID")))
    caso("L4_e_e_a_observacao_CERTA",
         res.get("RAW_OBSERVATION_ID") == raw_id,
         "resolvido=%s · real=%s" % (res.get("RAW_OBSERVATION_ID"), raw_id))

    # ── 3 · RAW -> STORAGE, e READY -> STORAGE ──────────────────────────
    caso("L5_RAW_TO_STORAGE_pela_chave_composta",
         res.get("STORAGE_OBJECT_ID") is not None
         and res.get("STORAGE_SHA256") == res.get("RAW_SHA256"),
         "storage=%s · sha bate=%s" % (res.get("STORAGE_OBJECT_ID"),
                                       res.get("STORAGE_SHA256")
                                       == res.get("RAW_SHA256")))
    caso("L6_READY_TO_STORAGE_sem_segundo_campo_no_contrato",
         res.get("STORAGE_PATH") and "STORAGE_OBJECT_ID" not in pousada,
         "o contrato NAO carrega storage: sai do join · %s"
         % res.get("STORAGE_PATH"))

    # ── 4 · RUN e SOURCE, pela observacao ───────────────────────────────
    caso("L7_RUN_LINEAGE_pela_observacao_e_nao_pelo_campo_do_item",
         res.get("RUN_ID") == RUN and pousada.get("CORRIDA") == RUN,
         "raw.run_id=%s · READY.CORRIDA=%s" % (res.get("RUN_ID"),
                                               pousada.get("CORRIDA")))
    caso("L8_SOURCE_LINEAGE_declarada_e_nao_inferida",
         res.get("SOURCE_ID") == FONTE,
         "raw.source_id=%s" % res.get("SOURCE_ID"))

    # ── 5 · O CONTRASTE, CONSTRUIDO E MEDIDO ────────────────────────────
    # ⚠️ ESTE CASO EXISTE PORQUE «A VOLTA ANTIGA E AMBIGUA» TEM DE SER UM
    # NUMERO, E NAO UMA FRASE. Sem o gemeo, a procura pelo sha devolve 1 nesta
    # arvore limpa e pareceria suficiente — e e exactamente assim que ela
    # engana: ela acerta enquanto so houver um.
    #
    #     UMA PONTE QUE ACERTA ENQUANTO HOUVER UM SO NAO E UMA PONTE.
    #
    # O cenario e real: dois PDFs DIFERENTES cujo texto extraido e o MESMO.
    # `derivacao_e_unica_por_regua` e sobre (parent_sha256, receita) — dois
    # pais diferentes dao DUAS linhas legitimas, e o `sha256` do FILHO nao tem
    # indice unico nenhum.
    antes_sha = pela_procura_do_sha(sql, pousada)
    sql.executa(
        "insert into public.collection_run (run_id, platform, actor,"
        " actor_version, source_country, rule_version, started_at, status)"
        " values ('RUN-GEMEO','HTTP direto','x','v1','IT','1',"
        "'2026-09-10T00:00:00Z','rodando') on conflict do nothing")
    sql.executa(
        "insert into public.storage_object (storage_path, media_type, bytes,"
        " sha256) values ('it/outro/outro.pdf','application/pdf', 99,"
        " '%s')" % ("d" * 64))
    outro_raw = sql.executa(
        "insert into public.raw_asset (run_id, storage_object_id,"
        " storage_path, media_type, bytes, sha256, captured_at,"
        " identity_state, source_id)"
        " select 'RUN-GEMEO', s.id, s.storage_path, 'application/pdf', 99,"
        " s.sha256, now(), 'FORWARD_IDENTITY_UNPROVEN', '%s'"
        "  from public.storage_object s where s.sha256 = '%s' returning id"
        % (FONTE, "d" * 64))
    # O MESMO texto (mesmo sha do filho), de OUTRO pai.
    sql.executa(
        "insert into public.derived_artifact (raw_asset_id, parent_sha256,"
        " kind, producer, producer_version, parameters_hash, storage_path,"
        " media_type, bytes, sha256, derived_at)"
        " select %d, '%s', 'TEXT_EXTRACTION', 'texto-de-pdf', 'v1', '%s',"
        " 'it/derived/gemeo.txt', 'text/plain', 50, '%s', now()"
        % (int(outro_raw[0][0]), "d" * 64, "0" * 64,
           str(pousada.get("ITEM_ID"))[:64]))
    depois_sha = pela_procura_do_sha(sql, pousada)
    caso("L9_a_volta_antiga_pelo_sha_fica_AMBIGUA_com_dois_pais",
         antes_sha == 1 and depois_sha == 2,
         "procurar derived pelo sha do ITEM_ID: %d candidato antes, %d depois "
         "— e nenhum deles e «o errado», sao os dois legitimos"
         % (antes_sha, depois_sha))

    res2 = resolver(sql, pousada)
    caso("L10_e_a_ponte_nova_continua_a_devolver_UMA_SO",
         res2["RESOLVIDO"] and res2["CANDIDATOS"] == 1
         and res2["RAW_OBSERVATION_ID"] == raw_id,
         "READY_WRONG_RAW_MATCHES=0 · READY_AMBIGUOUS_RAW_MATCHES=0 · raw=%s"
         % res2.get("RAW_OBSERVATION_ID"))

    # ── 6 · O RETRY — a mesma corrida outra vez ─────────────────────────
    # ⚠️ REPETIR NAO PODE MUDAR A OBSERVACAO DO ITEM, nem criar segunda copia.
    brutos_antes = int(sql.executa(
        "select count(*) from public.raw_asset")[0][0])
    obj_antes = int(sql.executa(
        "select count(*) from public.storage_object")[0][0])
    r2 = ing.receber([{"SOURCE_ID": FONTE,
                       "SOURCE_URL": "https://exemplo.it/%s"
                                     % os.path.basename(pdf),
                       "STORAGE_LOCATION": rel}],
                     corrida={"RUN_ID": RUN, "PLATFORM": "HTTP direto",
                              "ACTOR": "coleta/italy_executor.py",
                              "ACTOR_VERSION": "adapter-v1",
                              "SOURCE_COUNTRY": "IT", "RULE_VERSION": "1",
                              "STARTED_AT": "2026-09-10T00:00:00Z"},
                     armazem=ing.ArmazemLocal(RAIZ),
                     memoria=_memoria(url), raiz=RAIZ, banco_do_rastro=sql)
    obs2 = (r2["RAW"] or {}).get("RAW_OBSERVATIONS") or []
    saida2 = m2.atravessar(sql, unidade=unidade, run_id=RUN,
                           armazem=_armazem(), memoria=_memoria(url),
                           canal_id=canal_id)
    brutos_depois = int(sql.executa(
        "select count(*) from public.raw_asset")[0][0])
    obj_depois = int(sql.executa(
        "select count(*) from public.storage_object")[0][0])
    corpo2 = json.loads(io.open(espera.caminho_da_corrida(RUN),
                                encoding="utf-8").read())
    pousada2 = (corpo2.get("ITENS") or [{}])[0]
    res3 = resolver(sql, pousada2)
    caso("L11_READY_TO_RAW_AFTER_RETRY_continua_a_apontar_para_a_MESMA",
         res3["RESOLVIDO"] and res3["RAW_OBSERVATION_ID"] == raw_id,
         "antes=%s · depois do retry=%s" % (raw_id,
                                            res3.get("RAW_OBSERVATION_ID")))
    caso("L12_RAW_DUPLICATION_ON_RETRY_zero",
         brutos_depois == brutos_antes,
         "raw_asset: %d -> %d" % (brutos_antes, brutos_depois))
    caso("L13_STORAGE_DUPLICATION_ON_RETRY_zero",
         obj_depois == obj_antes,
         "storage_object: %d -> %d" % (obj_antes, obj_depois))
    caso("L14_o_retry_reencontrou_a_observacao_e_nao_cunhou_outra",
         len(obs2) == 1
         and obs2[0]["RAW_OBSERVATION_ID"] == raw_id,
         "a segunda passagem devolveu raw=%s"
         % (obs2[0]["RAW_OBSERVATION_ID"] if obs2 else "-"))

    return res, raw_id, sql


# ────────────────────────────────────────────────────────────────────────
# ATAQUES DE IDENTIDADE
# ────────────────────────────────────────────────────────────────────────
def os_ataques(sql, raw_id):
    """Seis maneiras de a ponte se enganar. Nenhuma pode passar."""
    # 1 · DOIS RAW COM O MESMO SHA — a ponte tem de os separar.
    sql.executa(
        "insert into public.collection_run (run_id, platform, actor,"
        " actor_version, source_country, rule_version, started_at, status)"
        " values ('%s','HTTP direto','x','v1','IT','1',"
        "'2026-09-10T00:00:00Z','rodando') on conflict do nothing" % RUN2)
    gemeo = sql.executa(
        "insert into public.raw_asset (run_id, storage_object_id,"
        " storage_path, media_type, bytes, sha256, captured_at,"
        " identity_state, source_id)"
        " select '%s', r.storage_object_id, r.storage_path, r.media_type,"
        " r.bytes, r.sha256, now(), r.identity_state, r.source_id"
        "  from public.raw_asset r where r.id = %d returning id"
        % (RUN2, raw_id))
    gid = int(gemeo[0][0])
    mesmo_sha = sql.executa(
        "select count(*) from public.raw_asset where sha256 ="
        " (select sha256 from public.raw_asset where id = %d)" % raw_id)
    caso("A1_dois_RAW_com_o_MESMO_sha_existem_e_a_ponte_nao_os_confunde",
         int(mesmo_sha[0][0]) >= 2
         and resolver(sql, {"RAW_OBSERVATION_ID": raw_id})["RAW_OBSERVATION_ID"]
         == raw_id
         and resolver(sql, {"RAW_OBSERVATION_ID": gid})["RAW_OBSERVATION_ID"]
         == gid,
         "%s observacoes com o mesmo sha · a ponte devolve %d e %d"
         % (mesmo_sha[0][0], raw_id, gid))

    # 2 · DUAS CORRIDAS DA MESMA FONTE.
    duas = sql.executa(
        "select count(distinct run_id) from public.raw_asset where id in (%d,%d)"
        % (raw_id, gid))
    caso("A2_duas_corridas_da_mesma_fonte_nao_colapsam",
         int(duas[0][0]) == 2
         and resolver(sql, {"RAW_OBSERVATION_ID": gid})["RUN_ID"] == RUN2,
         "%s corridas distintas para o mesmo sha" % duas[0][0])

    # 3 · SHA COMO ID — recusado por forma, e nao por sorte.
    sha = sql.executa("select sha256 from public.raw_asset where id=%d"
                      % raw_id)[0][0]
    r_sha = resolver(sql, {"RAW_OBSERVATION_ID": sha})
    caso("A3_um_sha_no_lugar_do_id_NAO_resolve",
         not r_sha["RESOLVIDO"],
         "recusado: %s" % r_sha["PORQUE"][:60])

    # 4 · STORAGE_PATH COMO IDENTIDADE.
    caminho = sql.executa("select storage_path from public.raw_asset"
                          " where id=%d" % raw_id)[0][0]
    r_path = resolver(sql, {"RAW_OBSERVATION_ID": caminho})
    caso("A4_um_storage_path_no_lugar_do_id_NAO_resolve",
         not r_path["RESOLVIDO"], "recusado: %s" % r_path["PORQUE"][:60])

    # 5 · SOURCE_ID COMO ESCOLHA DE RAW.
    r_src = resolver(sql, {"RAW_OBSERVATION_ID": FONTE})
    caso("A5_um_SOURCE_ID_no_lugar_do_id_NAO_resolve",
         not r_src["RESOLVIDO"], "recusado: %s" % r_src["PORQUE"][:60])

    # 6 · RAW INEXISTENTE — nao devolve o vizinho.
    r_nada = resolver(sql, {"RAW_OBSERVATION_ID": 999999})
    caso("A6_um_RAW_inexistente_devolve_NADA_e_nao_o_vizinho",
         not r_nada["RESOLVIDO"] and r_nada["CANDIDATOS"] == 0,
         "candidatos=%d" % r_nada["CANDIDATOS"])

    # 7 · READY SEM LINK NAO E LINHAGEM COMPLETA.
    r_sem = resolver(sql, {"RAW_OBSERVATION_ID": "NAO SEI"})
    caso("A7_READY_sem_link_NAO_conta_como_linhagem",
         not r_sem["RESOLVIDO"], "recusado: %s" % r_sem["PORQUE"][:60])


# ────────────────────────────────────────────────────────────────────────
# A ROTA SOCIAL — DERIVED NAO SE APLICA, E ISSO NAO E UMA FALHA
# ────────────────────────────────────────────────────────────────────────
def a_rota_social(sql, url):
    """Uma observacao social: bytes alcancaveis, e NADA que um extractor de PDF
    possa fazer com eles.

    ⚠️ `NOT_APPLICABLE` != `FAIL` != `MISSING`. A etapa nao correu porque nao se
    aplica — e contar isso como derivacao em falta mandaria procurar avaria
    onde nao ha nenhuma.

    ⚠️ E E AQUI QUE A PERGUNTA DO TEXTO SE RESPONDE. As `TEXT_UNITS` — com
    `TEXT_KIND`, `TEXT_RELATION` e `LANGUAGE` — NAO viajam no contrato READY. A
    pergunta nunca foi «viajam?»: foi «PERDEM-SE?». E nao se perdem, porque
    `coleta/ingresso.py::_bytes_do_item` serializa o ITEM INTEIRO como bytes da
    observacao. Elas ficam DENTRO do bruto preservado, e a mesma ponte que
    devolve o bruto devolve-as.

        NAO VIAJAR != PERDER-SE.
        RESOLVIVEL PELA LINHAGEM SO E VERDADE SE A LINHAGEM RESOLVER.
    """
    import importlib
    pv = importlib.import_module("proveniencia")
    unidade_texto = pv.unidade_de_texto(
        texto="Il fungo ha colpito il vigneto dopo la pioggia",
        kind=pv.NATIVE_CAPTION, kind_basis=pv.DECLARED_BY_PROVIDER,
        relation=pv.ORIGINAL, language="it", unit_id="TU-1")
    item = {"SOURCE_ID": "IT-T9-001",
            "SOURCE_URL": "https://social.example/p/1",
            "MEDIA_TYPE": "application/json",
            pv.CAMPO_DAS_UNIDADES: [unidade_texto]}
    r = ing.receber([item],
                    corrida={"RUN_ID": "RUN-SOCIAL", "PLATFORM": "INSTAGRAM",
                             "ACTOR": "coleta/adaptador_instagram.py",
                             "ACTOR_VERSION": "v1", "SOURCE_COUNTRY": "IT",
                             "RULE_VERSION": "1",
                             "STARTED_AT": "2026-09-10T00:00:00Z"},
                    armazem=ing.ArmazemLocal(RAIZ),
                    memoria=_memoria(url), raiz=RAIZ, banco_do_rastro=sql)
    obs = (r["RAW"] or {}).get("RAW_OBSERVATIONS") or []
    caso("S1_a_observacao_social_preservou_RAW_e_STORAGE",
         len(obs) == 1 and obs[0].get("RAW_OBSERVATION_ID"),
         "raw=%s · storage=%s" % (obs[0].get("RAW_OBSERVATION_ID") if obs
                                  else "-",
                                  obs[0].get("STORAGE_PATH") if obs else "-"))
    sem_bytes = r.get("SEM_BYTES_PARA_DERIVAR") or []
    para_derivar = r.get("PARA_A_DERIVACAO") or []
    caso("S2_DERIVED_e_NOT_APPLICABLE_e_nao_uma_derivacao_em_falta",
         not para_derivar and len(sem_bytes) == 1
         and "ESPECIE" in str(sem_bytes[0].get("PORQUE", "")).upper(),
         "nao-derivaveis=%d · porque=%s"
         % (len(sem_bytes), (sem_bytes[0].get("PORQUE") if sem_bytes else "-")))
    caso("S3_e_a_observacao_nao_derivavel_NAO_perde_o_id",
         bool(sem_bytes) and sem_bytes[0].get("RAW_ASSET_ID")
         == obs[0].get("RAW_OBSERVATION_ID"),
         "o nao-derivavel continua a nomear raw=%s"
         % (sem_bytes[0].get("RAW_ASSET_ID") if sem_bytes else "-"))

    # ── A PERGUNTA DO TEXTO, RESPONDIDA PELOS BYTES ─────────────────────
    raw_social = obs[0]["RAW_OBSERVATION_ID"] if obs else None
    res = resolver(sql, {"RAW_OBSERVATION_ID": raw_social})
    guardado = None
    if res.get("RESOLVIDO"):
        try:
            guardado = json.loads(
                ing.ArmazemLocal(RAIZ).ler(res["STORAGE_PATH"])
                .decode("utf-8"))
        except Exception:                              # noqa: BLE001
            guardado = None
    unidades = (guardado or {}).get(pv.CAMPO_DAS_UNIDADES) or []
    primeira = unidades[0] if unidades else {}
    caso("S4_TEXT_KIND_resolve_se_pela_linhagem_e_nao_por_inferencia",
         primeira.get("TEXT_KIND") == pv.NATIVE_CAPTION,
         "do byte preservado: TEXT_KIND=%s" % primeira.get("TEXT_KIND"))
    caso("S5_TEXT_RELATION_resolve_se_pela_linhagem",
         primeira.get("TEXT_RELATION") == pv.ORIGINAL,
         "TEXT_RELATION=%s" % primeira.get("TEXT_RELATION"))
    caso("S6_LANGUAGE_resolve_se_pela_linhagem_e_nao_se_herda",
         primeira.get("LANGUAGE") == "it",
         "LANGUAGE=%s — da unidade, nunca da publicacao"
         % primeira.get("LANGUAGE"))
    caso("S7_e_nada_disto_viaja_no_contrato_READY",
         "TEXT_KIND" not in admissao.pronto_para_inteligencia(
             {"id": "x", "texto": "t", "source_id": "IT-T7-001",
              "fact_time": "2026-05-02", "raw_asset_id": 1},
             admissao.decidir({"id": "x",
                               "texto": "Ensaio de campo publicado com DOI",
                               "source_id": "IT-T7-001",
                               "fact_time": "2026-05-02"},
                              "T7", corrida="x")),
         "o contrato continua com 12 campos, e a especie fica no bruto")


def _fechar():
    print("")
    maus = [n for n, ok, _ in fora if not ok]
    for nome, ok, det in fora:
        print("  %s  %-58s %s" % ("PASS" if ok else "FAIL", nome, det[:70]))
    print("")
    print("=" * 70)
    print("LINHAGEM_DO_READY=%s · %d casos · %d falha(s)"
          % ("PASS" if not maus else "FAIL", len(fora), len(maus)))
    print("=" * 70)
    return 0 if not maus else 1


def main():
    url = os.environ.get("BANCO_DESCARTAVEL_URL")
    if not url:
        print("SEM BANCO DESCARTAVEL — e SKIP != PASS.")
        print("LINHAGEM_DO_READY=NOT_MEASURED")
        return 2
    sala = tempfile.mkdtemp(prefix="espera-linhagem-")
    espera.MORADA = sala
    try:
        res, raw_id, sql = medir(url, sala)
        os_ataques(sql, raw_id)
        a_rota_social(sql, url)
        return _fechar()
    finally:
        shutil.rmtree(sala, ignore_errors=True)


if __name__ == "__main__":
    raise SystemExit(main())
