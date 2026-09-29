#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""L2-DISPARADOR — o ensaio num PostgreSQL DESCARTAVEL, sem rede: Sala -> copia -> motor -> pote.

    py provas/l2/ensaio_disparador.py [--saida=provas/l2/ENSAIO-DISPARADOR.json]

O QUE E REAL (o mesmo codigo que o agendador chama)
    admissao/gatilho_da_inteligencia.uma_volta -> correr_se_devido -> backup PROVA_VALE (pg_dump +
    restauro + fotografia) -> export read-only DA COPIA (RUNBOOK-R7) + pousos -> corte vigente ->
    motor_das_capacidades.rodar -> pote_intelligence_casco -> validar_pote_v2 -> sobe ou nao sobe.
    O .cmd do arranque: um .cmd de verdade le SALA_DSN.txt com `set /p` e corre `--medir` (so SELECT).
    O banco: PostgreSQL descartavel numa porta livre, com a cadeia `migrations` inteira.

O QUE E DE ENSAIO (dito para ninguem ler isto como prova de producao)
  * A «Sala» e o banco descartavel, semeado com a fixture SINTETICA de tests/dados/int-r7 pelos DONOS
    (`sala_de_espera.pousar` e `rever`), como `provas/int_r7/export_numa_copia_descartavel.py`.
  * O defeito (a) e PLANTADO: a linha 0 da fixture pousa outra vez por uma segunda corrida, NOUTRO
    universo (o mesmo ITEM_ID em duas linhas da vista — como derived:6/56/57/60/62/66 na Sala real).
    Noutro universo porque `pousar` ja recusa o mesmo ITEM_ID no MESMO universo vindo de outra corrida
    (lido no SQL de `pousar`: `not exists (... s.item_id = e.item_id and s.universo = e.universo and
    s.run_id <> e.run_id)`, admissao/sala_de_espera.py). Como os 6 da Sala real la
    chegaram (universos diferentes, ou antes da trava do C6): NAO SEI daqui.
  * Os itens novos (passos 5 e 7) levam document_key novo: com o da fixture, a Sala os funde (C6).
  * A janela pousa com as quatro chaves em NAO SEI (JANELA_NAO_MEDIDA) e a da fixture entra por `rever`.
  * O «agora» das voltas e declarado (agora, +10 min, +20 min, +4 h 30).
  * Passo 7 usa um MOTOR DUBLE (a corrida sintetica valida de tests/fixtures/pote, com o ENTITY_SOURCE
    do unico objeto que o traz trocado por DOCUMENT_TITLE, um valor da lei COL-LAW-221) para provar que
    um pote APROVADO chega a entrega com sha. Esta dito no resultado: nao e o motor real.
  * A FRONTEIRA (correcao do coordenador, 28/09): o disparador PARA na entrega PARA-O-CASCO. O ensaio
    fotografa italia-portale/ inteiro no inicio e no fim: tem de estar igual.
  * Tudo escreve numa pasta temporaria; a arvore e o casco verdadeiros nao sao tocados.

A SALA NUNCA MUDA POR CAUSA DO DISPARADOR: antes e depois de cada disparo tira-se a impressao da Sala
(md5 das linhas de sala_de_espera, das revisoes, e a contagem de consumido_em). Tem de ser IGUAL.

Sem binarios do Postgres (SINTONIA_PG_BIN ou o PG_BIN do ensaio): sai 4 e NAO SEI — nunca PASS.
"""
from __future__ import annotations

import importlib.util
import json
import os
import shutil
import subprocess
import sys
import tempfile
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from unittest import mock

AQUI = Path(__file__).resolve()
RAIZ = AQUI.parents[2]
for p in ("", "admissao", "motor", "medidas"):
    sys.path.insert(0, str(RAIZ / p))
import _gavetas                            # noqa: E402,F401
import sala_de_espera as espera            # noqa: E402
import motor_das_capacidades as M          # noqa: E402
import gatilho_da_inteligencia as GI       # noqa: E402
import vigia_da_esteira as VIG             # noqa: E402
import admissao as ADM                     # noqa: E402  (admissao/admissao.py: JANELA_NAO_MEDIDA)

_spec = importlib.util.spec_from_file_location("ensaio_offline", RAIZ / "scripts" / "micro_coleta" / "ensaio_offline.py")
E = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(E)

FIXTURE = RAIZ / "tests" / "dados" / "int-r7" / "SINTETICO-R7-SALA-EXPORT.json"
CORRIDA_VALIDA = RAIZ / "tests" / "fixtures" / "pote" / "CORRIDA-SINTETICA-V2-UNICO.json"
SAIDA = AQUI.parent / "ENSAIO-DISPARADOR.json"
REPETIDA = "L2-REPETIDO-2026-09-28"
NOVA = "L2-ITEM-NOVO-2026-09-28"


def _psql(base, env, sql, opcoes="-c standard_conforming_strings=on"):
    return subprocess.run([base.exe("psql"), "-X", "-q", "-A", "-t", "-v", "ON_ERROR_STOP=1", "-c", sql, base.url],
                          capture_output=True, text=True, encoding="utf-8", env=dict(env, PGOPTIONS=opcoes))


def impressao(base, env) -> dict:
    """A impressao da Sala: se o disparador escrevesse uma virgula, isto mudava."""
    r = _psql(base, env, "select (select count(*) from sala_de_espera) || '|' || "
                         "(select count(*) from sala_de_espera where consumido_em is not null) || '|' || "
                         "(select coalesce(md5(string_agg(t::text, '#' order by t.run_id, t.ordem)), '-') "
                         "   from sala_de_espera t) || '|' || "
                         "(select count(*) from sala_de_espera_revisao)")
    n, consumidos, md5, rev = r.stdout.strip().split("|")
    return {"LINHAS": int(n), "CONSUMIDO_EM_PREENCHIDO": int(consumidos), "MD5": md5, "REVISOES": int(rev)}


def foto_do_portal() -> dict:
    """Todo ficheiro sob italia-portale/ (tamanho e mtime): a fronteira e a Intelligence parar na entrega."""
    b = RAIZ / "italia-portale"
    return {str(q.relative_to(b)): (q.stat().st_size, q.stat().st_mtime_ns) for q in b.rglob("*") if q.is_file()}


def semear(base, env, fx, linhas, run_extra=None):
    """Pousa `linhas` da fixture pelos DONOS da Sala (pousar + rever), como a prova do R7."""
    entrada = M.entrada_do_export(dict(fx, LINHAS=linhas))
    runs = sorted({l["run_id"] for l in linhas})
    r = _psql(base, env, "insert into collection_run (run_id, platform, started_at, rule_version) values "
              + ", ".join("(%s, 'SINTETICO', now(), 'SINTETICO')" % espera._lit(x) for x in runs)
              + " on conflict do nothing")
    assert r.returncode == 0, r.stderr
    for l in linhas:
        rid = l["raw_observation_id"]
        r = _psql(base, env, "insert into raw_asset (id, run_id, storage_path, media_type, bytes, sha256, "
                  "captured_at, source_url, source_id, document_key, document_key_basis, identity_state, "
                  "preserved, not_preserved_reason) values (%d, %s, %s, 'text/html', 1, %s, %s, %s, %s, %s, %s, %s, "
                  "false, 'SINTETICO: fixture INT-R7-CAPS, sem bytes') on conflict do nothing"
                  % (rid, espera._lit(l["run_id"]), espera._lit("SINTETICO/%d" % rid), espera._lit("%064x" % rid),
                     espera._lit(l["captured_at"]), espera._lit(l["raw_source_url"]), espera._lit(l["source_id"]),
                     espera._lit(l["raw_document_key"]), espera._lit(l["raw_document_key_basis"]),
                     espera._lit("FORWARD_IDENTIFIED" if l["raw_document_key"] else "FORWARD_IDENTITY_UNPROVEN")))
        assert r.returncode == 0, r.stderr
    por_run = {}
    for reg, l in zip(entrada["ITENS"], linhas):
        # A janela pousa como o dono pousa o que nao mediu (as quatro chaves em NAO SEI: a trava
        # janela_declara_as_quatro_chaves da 033); a da fixture entra depois como REVISAO, pelo `rever`.
        por_run.setdefault(l["run_id"], []).append((l["ordem"], dict(reg["READY"], CORRIDA=l["run_id"],
                                                                     JANELA_DECLARADA=ADM.JANELA_NAO_MEDIDA),
                                                    l["janela_declarada"]))
    recibos = {}
    for run, us in por_run.items():
        us.sort(key=lambda x: x[0])
        recibo = espera.pousar(run, [u for _o, u, _j in us])
        recibos[run] = {k: recibo[k] for k in recibo if k in ("ESTADO", "INSERIDAS")}
        # Pelo ITEM_ID, nao pela posicao: a Sala funde itens do mesmo documento na mesma corrida (C6;
        # na fixture, SINT-R7-ARIF-38#0 e #1 partilham o raw 9003), e a posicao desalinharia a janela.
        pousadas = {str(x["ITEM_ID"]): x for x in espera.ler_atual(run)["ITENS"]}
        for _o, u, jd in us:
            linha = pousadas.get(str(u["ITEM_ID"]))
            if linha is not None and isinstance(jd, dict):
                espera.rever(run, linha["ORDEM"], [{"CAMPO": "janela_declarada",
                                                    "VALOR": json.dumps(jd, ensure_ascii=False, sort_keys=True),
                                                    "BASE": "SINTETICO · fixture INT-R7-CAPS"}],
                             extrator="SINTETICO-R7", versao="1", motivo="fixture SINTETICA L2")
    return recibos


def correr(saida: Path) -> dict:
    if os.environ.get("SINTONIA_PG_BIN"):
        E.PG_BIN = Path(os.environ["SINTONIA_PG_BIN"])
    initdb = E.PG_BIN / ("initdb.exe" if os.name == "nt" else "initdb")
    if not initdb.exists() or (hasattr(os, "geteuid") and os.geteuid() == 0):
        return {"ESTADO": "NAO SEI", "PORQUE": "sem Postgres em %s, ou a correr como root" % E.PG_BIN}
    t = Path(tempfile.mkdtemp(prefix="l2-disparador-"))
    base = E.Base(t / "pg-sala")
    assert ":54330/" not in base.url, "isto e a Sala real"
    env = {k: v for k, v in os.environ.items()
           if k not in ("SINTONIA_COLLECTION_DSN", "SINTONIA_SALA_DSN", "SUPABASE_DB_URL", "BANCO_DESCARTAVEL_URL")}
    env["PATH"] = str(E.PG_BIN) + os.pathsep + env.get("PATH", "")
    amb = dict(os.environ)
    out = {"QUANDO": datetime.now(timezone.utc).isoformat(), "BASE_DA_ARVORE": "ver git rev-parse HEAD no relatorio",
           "PASSOS": {}}
    P = out["PASSOS"]
    try:
        r = base.subir(RAIZ, env)
        P["0_MIGRATIONS"] = {"CODIGO": r["CODIGO"], "PASS": r["MIGRATIONS_PASS"]}
        if r["CODIGO"] != 0:
            out["ESTADO"], out["ERRO"] = "FAIL", r["ERRO"] or r["SAIDA"]
            return out
        os.environ.update({"SINTONIA_SALA_BACKEND": "POSTGRES", "SINTONIA_SALA_DSN": base.url,
                           "SINTONIA_PSQL_EXE": base.exe("psql")})
        os.environ.pop("SINTONIA_COLLECTION_DSN", None)
        fx = json.loads(FIXTURE.read_text(encoding="utf-8"))

        # 1 · a Sala: a fixture + o defeito (a) plantado (a linha 0 pousa outra vez por outra corrida)
        P["1_SEMEAR"] = semear(base, env, fx, fx["LINHAS"])
        rep = dict(fx["LINHAS"][0], run_id=REPETIDA, ordem=1, universo=fx["LINHAS"][0]["universo"] + "-OUTRA-GAVETA")
        P["1_SEMEAR"].update(semear(base, env, fx, [rep]))
        # a Sala funde uma das 9 linhas da fixture (mesmo documento, C6): um decimo item, com documento
        # proprio, para a regra dos 10 novos ser a que dispara no passo 3
        dez = dict(fx["LINHAS"][3], run_id=NOVA + "-10", ordem=1, item_id="L2-NOVO-10", raw_observation_id=990010,
                   raw_document_key="L2-DOC-NOVO-10")
        P["1_SEMEAR"].update(semear(base, env, fx, [dez]))
        vista = _psql(base, env, "select item_id, count(*) from sala_de_espera_atual group by 1 having count(*) > 1")
        P["1_ITEM_ID_REPETIDO_NA_VISTA"] = [l.split("|") for l in vista.stdout.split() if l]

        kw = dict(parar=t / "PARAR.flag", trinco=t / "ESTEIRA-INTELLIGENCE", pasta=t / "esteira")
        GI.ENTREGA = t / "esteira" / "PARA-O-CASCO"
        portal_antes = foto_do_portal()
        estado_em, volta = t / "ESTADO.json", t / "ESTEIRA-INTELLIGENCE-VOLTA"

        def uma(agora, **mais):
            antes = impressao(base, env)
            r = GI.uma_volta(estado_em=estado_em, trinco_da_volta=volta, agora=agora, forcar_medida=True,
                             **dict(kw, **mais))
            depois = impressao(base, env)
            return r, antes == depois, depois

        agora = datetime.now(timezone.utc)

        # 2 · dois disparos: o segundo encontra o trinco preso (a corrida em curso) -> OCUPADO, sem copia
        with espera._Trava(str(kw["trinco"])):
            r2, igual2, _ = uma(agora)
        P["2_DOIS_DISPAROS_TRINCO"] = {"ACCAO": r2.get("ACCAO"), "SALA_IGUAL": igual2,
                                       "COPIA_FEITA": (t / "esteira").exists() and any((t / "esteira").glob("*/backup"))}
        estado_em.unlink(missing_ok=True)                              # o 2.º disparo nao conta como medida

        # 3 · item novo -> dispara (10 READY novos: 9 da fixture + 1 repetido)
        r3, igual3, imp3 = uma(agora)
        est = json.loads(estado_em.read_text(encoding="utf-8"))
        P["3_ITEM_NOVO_DISPARA"] = {k: r3.get(k) for k in ("ACCAO", "GATILHO", "SUBIU", "PORQUE", "CORRIDA",
                                                         "VIOLACOES", "PRIMEIRAS", "CORTE")}
        P["3_SALA_IGUAL_ANTES_E_DEPOIS"] = igual3
        P["3_SALA"] = imp3
        P["3_ESTADO"] = {k: est.get(k) for k in ("INT_MARCA", "INT_ULTIMA_CORRIDA_EM", "INT_ULTIMA_CORRIDA_ID",
                                                "INT_ULTIMO_POTE", "INT_ULTIMO_CORTE")}
        pastas = sorted(p for p in (t / "esteira").iterdir() if (p / "backup").is_dir())
        ult = pastas[-1]
        motor_json = json.loads((ult / "MOTOR.json").read_text(encoding="utf-8")) if (ult / "MOTOR.json").exists() else {}
        P["3_MOTOR"] = {"CORRIDA": motor_json.get("INTELLIGENCE_RUN_ID"),
                        "OBJETOS": {k: len(v) for k, v in (motor_json.get("ITENS_POR_FERRAMENTA") or {}).items()},
                        "CRUZAMENTOS_D112_RELACOES": len(((motor_json.get("D112") or {}).get("RELACOES")) or []),
                        "JANELAS_CAP_WIN": len(((motor_json.get("CAP_WIN") or {}).get("CROP_WINDOWS")) or []),
                        "ESTUDOS_CAP_SCI": len(((motor_json.get("CAP_SCI") or {}).get("ESTUDOS")) or [])}
        backup = json.loads((ult / "backup" / "PROVA-BACKUP-SALA.json").read_text(encoding="utf-8"))
        exp = json.loads((ult / "EXPORT-DA-COPIA.json").read_text(encoding="utf-8"))
        P["3_COPIA"] = {"PROVA_VALE": backup.get("PROVA_VALE"), "IGUAL_A_SALA_REAL": backup.get("IGUAL_A_SALA_REAL"),
                        "EXPORT_READ_ONLY": exp.get("READ_ONLY"), "EXPORT_ORIGEM": exp.get("ORIGEM"),
                        "EXPORT_LINHAS": len(exp.get("LINHAS") or [])}
        P["3_POTE_REPROVADO_GUARDADO"] = sorted(p.name for p in ult.glob("POTE-REPROVADO-*.js"))
        P["3_ENTREGA_VAZIA"] = not GI.ENTREGA.exists()

        # 4 · sem item novo -> SEM_DELTA
        r4, igual4, _ = uma(agora + timedelta(minutes=10))
        P["4_SEM_ITEM_NOVO"] = {"ACCAO": r4.get("ACCAO"), "PORQUE": r4.get("PORQUE"), "SALA_IGUAL": igual4}

        # 5 · um item novo (outra corrida, ITEM_ID novo): recente espera; com 4 h, dispara
        nova = dict(fx["LINHAS"][1], run_id=NOVA, ordem=1, item_id="L2-NOVO-1", raw_observation_id=990001,
                    raw_document_key="L2-DOC-NOVO-1")
        P["5_SEMEAR_NOVO"] = semear(base, env, fx, [nova])
        r5a, igual5a, _ = uma(agora + timedelta(minutes=20))
        r5b, igual5b, _ = uma(datetime.now(timezone.utc) + timedelta(hours=4, minutes=30))
        P["5_ITEM_NOVO"] = {"RECENTE": {"ACCAO": r5a.get("ACCAO"), "PORQUE": r5a.get("PORQUE"), "SALA_IGUAL": igual5a},
                            "COM_4H": {k: r5b.get(k) for k in ("ACCAO", "GATILHO", "SUBIU", "PORQUE", "VIOLACOES")},
                            "COM_4H_SALA_IGUAL": igual5b}

        # 6 · o .cmd do arranque: `set /p` le SALA_DSN.txt, --medir (so SELECT); a DSN nao aparece na saida
        dsn_txt = t / "SALA_DSN.txt"
        dsn_txt.write_text(base.url + "\n", encoding="utf-8")
        if os.name == "nt":
            cmd = t / "disparador_intelligence.cmd"
            cmd.write_text("@echo off\r\ncd /d %s\r\nset SINTONIA_SALA_BACKEND=POSTGRES\r\n"
                           "set /p SINTONIA_SALA_DSN=<%s\r\nset SINTONIA_PSQL_EXE=%s\r\n"
                           "\"%s\" admissao\\gatilho_da_inteligencia.py --medir\r\n"
                           % (RAIZ, dsn_txt, base.exe("psql"), sys.executable), encoding="utf-8")
            envc = {k: v for k, v in env.items() if not k.startswith("SINTONIA_")}
            rc = subprocess.run(["cmd", "/c", str(cmd)], capture_output=True, text=True, encoding="utf-8",
                                errors="replace", env=envc, timeout=300)
            try:
                medido = json.loads(rc.stdout[rc.stdout.index("{"):])
            except ValueError:
                medido = {"SAIDA": rc.stdout[-400:], "ERRO": rc.stderr[-400:]}
            P["6_CMD_LE_SALA_DSN_TXT"] = {"CODIGO": rc.returncode, "MEDIDO": medido,
                                          "DSN_NA_SAIDA": base.url in (rc.stdout + rc.stderr),
                                          "SENHA_OU_PORTA_NA_SAIDA": (":%s/" % base.porto) in (rc.stdout + rc.stderr)}
        else:
            P["6_CMD_LE_SALA_DSN_TXT"] = "NAO SEI: .cmd so no Windows"

        # 7 · MOTOR DUBLE: um pote que o fiscal APROVA chega a entrega com sha (o caminho da subida)
        item7 = dict(fx["LINHAS"][2], run_id=NOVA + "-7", ordem=1, item_id="L2-NOVO-7", raw_observation_id=990007,
                     raw_document_key="L2-DOC-NOVO-7")
        semear(base, env, fx, [item7])
        # o duble: a corrida sintetica valida com o ENTITY_SOURCE do unico objeto que o traz trocado por um
        # valor da lei COL-LAW-221 (sem isso a conversao da decisao do owner poe UNKNOWN e o fiscal reprova)
        duble = json.loads(CORRIDA_VALIDA.read_text(encoding="utf-8"))
        for objs in (duble.get("ITENS_POR_FERRAMENTA") or {}).values():
            for o in objs if isinstance(objs, list) else [objs]:
                if isinstance(o, dict) and "ENTITY_SOURCE" in o:
                    o["ENTITY_SOURCE"] = "DOCUMENT_TITLE"
        with mock.patch.object(GI, "correr_o_motor", lambda *a: duble):
            r7, igual7, _ = uma(datetime.now(timezone.utc) + timedelta(hours=9))
        man = json.loads((GI.ENTREGA / "MANIFESTO.json").read_text(encoding="utf-8")) if GI.ENTREGA.exists() else {}
        somas = (GI.ENTREGA / "SHA256SUMS.txt").read_text(encoding="utf-8") if GI.ENTREGA.exists() else ""
        import hashlib
        bate = bool(somas) and all(
            hashlib.sha256((GI.ENTREGA / l.split(" *")[1]).read_bytes()).hexdigest() == l.split(" *")[0]
            for l in somas.splitlines())
        P["7_MOTOR_DUBLE_POTE_APROVADO"] = {"AVISO": "motor DUBLE (corrida sintetica valida): prova o caminho da subida, "
                                                     "NAO o motor real",
                                            "ACCAO": r7.get("ACCAO"), "SUBIU": r7.get("SUBIU"), "SALA_IGUAL": igual7,
                                            "ENTREGA": sorted(p.name for p in GI.ENTREGA.iterdir()) if GI.ENTREGA.exists() else [],
                                            "SHA256SUMS_BATE": bate, "MANIFESTO": man,
                                            "ENTITY_SOURCE_CONVERTIDOS": r7.get("ENTITY_SOURCE_CONVERTIDOS")}

        # 8 · o vigia
        saude = t / "ESTEIRA-SAUDE.json"
        rel = VIG.medir(estado_sup=json.loads(estado_em.read_text(encoding="utf-8")))
        VIG.escrever(rel, saude, t / "H.ndjson")
        P["8_VIGIA"] = {"ALERTA": rel["ALERTA"], "ALERTAS": [(a["ETAPA"], a["ESTADO"]) for a in rel["ALERTAS"]]}

        imp_final = impressao(base, env)
        P["9_PORTAL_IGUAL"] = foto_do_portal() == portal_antes
        P["9_SALA_FINAL"] = imp_final
        corte = P["3_ITEM_NOVO_DISPARA"].get("CORTE") or {}
        ok = {
            "MIGRATIONS": P["0_MIGRATIONS"]["CODIGO"] == 0,
            "DEFEITO_PLANTADO_NA_VISTA": bool(P["1_ITEM_ID_REPETIDO_NA_VISTA"]),
            "TRINCO": P["2_DOIS_DISPAROS_TRINCO"]["ACCAO"] == "OCUPADO" and not P["2_DOIS_DISPAROS_TRINCO"]["COPIA_FEITA"],
            "DISPAROU_E_O_MOTOR_CORREU": r3.get("ACCAO") in ("POTE_SUBIU", "POTE_NAO_SUBIU")
                                         and bool(P["3_MOTOR"]["CORRIDA"]),
            "CORTE_VIGENTE_DECLARADO": corte.get("DEFEITO_NA_SALA") is True and corte.get("ITEM_ID_REPETIDO")
                                       == [fx["LINHAS"][0]["item_id"]]
                                       and corte.get("LINHAS_NO_EXPORT") - corte.get("LINHAS_NO_CORTE") == 1,
            "COPIA_READ_ONLY": P["3_COPIA"]["PROVA_VALE"] is True and P["3_COPIA"]["EXPORT_READ_ONLY"] == "on",
            "O_FISCAL_MANDA": (r3.get("SUBIU") is True) == (not P["3_ENTREGA_VAZIA"]),
            "NADA_ESCRITO_SOB_ITALIA_PORTALE": P["9_PORTAL_IGUAL"],
            "SEM_DELTA": P["4_SEM_ITEM_NOVO"]["PORQUE"] == "SEM_DELTA",
            "NOVO_RECENTE_ESPERA_E_COM_4H_DISPARA": (P["5_ITEM_NOVO"]["RECENTE"]["ACCAO"] == "ESPERA"
                                                    and r5b.get("GATILHO", "").startswith("NOVO_A_ESPERA_HA_4H")),
            "SALA_NUNCA_MUDOU_NUM_DISPARO": all((igual2, igual3, igual4, igual5a, igual5b, igual7)),
            "CONSUMIDO_EM_NUNCA": imp_final["CONSUMIDO_EM_PREENCHIDO"] == 0,
            "CMD_LE_SALA_DSN_TXT": (not isinstance(P["6_CMD_LE_SALA_DSN_TXT"], dict))
                                   or (P["6_CMD_LE_SALA_DSN_TXT"]["CODIGO"] == 0
                                       and isinstance(P["6_CMD_LE_SALA_DSN_TXT"]["MEDIDO"].get("NOVOS"), int)
                                       and not P["6_CMD_LE_SALA_DSN_TXT"]["DSN_NA_SAIDA"]),
            "POTE_APROVADO_CHEGA_A_ENTREGA": P["7_MOTOR_DUBLE_POTE_APROVADO"]["SUBIU"] is True and bate,
            "VIGIA_DIZ_O_DEFEITO": ("sala", VIG.DEFEITO_NA_SALA) in [tuple(a) for a in P["8_VIGIA"]["ALERTAS"]],
        }
        out["CONFERE"] = ok
        out["DISPARADOR_INTELLIGENCE"] = "PASS" if all(ok.values()) else "FAIL"
        out["POTE_NOVO_GERADO_SEM_MAO_HUMANA"] = (
            "PASS" if r3.get("SUBIU") is True or r5b.get("SUBIU") is True else
            "FAIL: o motor real gerou o pote sem mao humana, e o fiscal o REPROVOU (%s violacoes; primeiras: %s)"
            % (r3.get("VIOLACOES"), (r3.get("PRIMEIRAS") or [])[:2]))
        out["ESTADO"] = out["DISPARADOR_INTELLIGENCE"]
        return out
    except Exception:  # noqa: BLE001
        import traceback
        out["ESTADO"], out["ERRO"] = "FAIL", traceback.format_exc()[-12000:]
        return out
    finally:
        os.environ.clear()
        os.environ.update(amb)
        base.descer()
        shutil.rmtree(t, ignore_errors=True)
        saida.write_text(json.dumps(out, ensure_ascii=False, indent=1, default=str) + "\n", encoding="utf-8")


if __name__ == "__main__":
    a = sys.argv[1:]
    s = Path(next((x.split("=", 1)[1] for x in a if x.startswith("--saida=")), SAIDA)).resolve()
    res = correr(s)
    print(json.dumps({k: res.get(k) for k in ("ESTADO", "DISPARADOR_INTELLIGENCE", "POTE_NOVO_GERADO_SEM_MAO_HUMANA",
                                              "CONFERE", "ERRO")}, ensure_ascii=False, indent=1))
    sys.exit(0 if res.get("ESTADO") == "PASS" else 4 if res.get("ESTADO") == "NAO SEI" else 1)
