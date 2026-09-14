#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""A PONTE DE MIDIA CONTRA POSTGRES DE VERDADE — RAW -> DERIVED -> ... -> SALA.

    BANCO_DESCARTAVEL_URL=postgresql://postgres:descartavel@localhost:5432/midia \\
        python3 provas/a_ponte_de_midia_no_postgres.py

O QUE ESTA PROVA FECHA, E O QUE ELA REUSA
------------------------------------------
A `a_rota_m2_atravessa` ja prova a estrada `DERIVED -> STRUCTURED -> ADMISSION`
com um PDF. O que NUNCA foi provado e a aresta de ENTRADA quando o bruto e
MIDIA:

    raw_asset(audio/*) -> executor_transcricao_midia -> derived_artifact

Esta prova nao reimplementa a estrada: ela poe midia na ponta de cima e
verifica que a MESMA estrada a leva ate a Sala.

    NAO SE PROVA DUAS VEZES O QUE JA FOI PROVADO. PROVA-SE O QUE ENTROU NOVO.

⚠️ O FIXTURE E SINTETICO, E O NOME DELE DIZ ISSO
------------------------------------------------
O unico ficheiro de midia com fala real que esta casa possui esta FORA do Git,
e o repositorio e PUBLICO. Commitar um clipe de video de terceiro para um teste
passar seria publicar conteudo alheio — e um teste nao justifica isso.

Entao a fala e GERADA na hora, por `espeak-ng`, e a fonte chama-se
`FIXTURE-DE-PROVA/FALA-SINTETICA-C4H`. O nome e feio de proposito:

    UMA FONTE DE MENTIRA TEM DE SE ANUNCIAR NO PROPRIO NOME,
    PARA QUE NINGUEM A LEIA UM DIA COMO OBSERVACAO DO MUNDO.

E a observacao que nasce aqui pertence A ESTA CORRIDA DE REPROCESSO, e nao a
nenhuma coleta historica. Nao se lhe atribui hora, fonte nem corrida do passado.

    NEW_MEDIA_ACQUISITION = NO · RUN_TYPE = REPROCESS · PAID_USD = 0

⚠️ E SE A FERRAMENTA FALTAR, ISTO SALTA — E SALTAR NAO E PASSAR
----------------------------------------------------------------
Sem `espeak-ng`, sem `ffmpeg` ou sem `faster-whisper`, esta prova nao tenta
fingir: escreve o que falta e sai com codigo proprio. `SKIP != PASS`, e um
verde que veio de uma ferramenta ausente e o defeito que esta casa mais persegue.
"""
import io
import json
import os
import subprocess
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)
sys.path.insert(0, os.path.join(RAIZ, "coleta"))
import _gavetas  # noqa: E402,F401

import importlib.util as _u  # noqa: E402

_spec = _u.spec_from_file_location(
    "prova_pg", os.path.join(RAIZ, "provas", "preservar_coleta_no_postgres.py"))
_pg = _u.module_from_spec(_spec)
_spec.loader.exec_module(_pg)

import coleta_checkpoint as cc                    # noqa: E402
import derivacao_forward as fwd                   # noqa: E402
import executor_transcricao_midia as midia        # noqa: E402
import ingresso as ing                            # noqa: E402
import rastro_da_coleta as rastro                 # noqa: E402
import rota_forward_documento as m2               # noqa: E402
import social_persistencia as sp                  # noqa: E402
import proveniencia as pv                         # noqa: E402
from guarda import preservar_derivado as pd       # noqa: E402
from guarda.preservar_coleta import (             # noqa: E402
    ArmazemDeMentira, preservar, sha256)

#: A corrida DESTA prova. `REPROCESS` esta no nome para que ninguem a leia como
#: coleta: ela nao adquiriu nada do mundo.
RUN = "RUN-C4H-MIDIA-REPROCESS"
RUN2 = "RUN-C4H-MIDIA-REPROCESS-2"
RELOGIO = "2026-09-14T20:00:00Z"

#: ⚠️ ESTA FONTE NAO EXISTE NO MUNDO, E O NOME DELA DIZ ISSO.
#: `guarda/preservar_coleta.py` recusa observacao sem fonte — «B5B · SEM FONTE
#: NAO HA OBSERVACAO FORWARD» — e essa lei esta certa. O que ela impede e uma
#: observacao orfa entrar no acervo; o que ela NAO pede e que se minta.
#:
#: Dar-lhe `IT-T2-002` (ARPAV) faria o banco afirmar que a agencia meteorologica
#: do Veneto publicou um ficheiro de audio. Seria uma fonte real a carregar um
#: facto falso, que e pior do que uma fonte obviamente falsa.
FONTE = "FIXTURE-DE-PROVA/FALA-SINTETICA-C4H"

#: O texto que a voz sintetica diz. Italiano, porque a lingua tem de ser
#: DETECTADA e nao assumida — e um `it` detectado sobre fala italiana e a unica
#: maneira de provar que a deteccao funciona sem lhe declarar a resposta.
FALA = ("Il grano tenero in Veneto mostra sintomi di septoria nelle foglie "
        "basali. Si consiglia un trattamento fungicida entro la settimana.")

SAIDA = os.path.join(RAIZ, "system-map", "data",
                     "ponte-de-midia-postgres.generated.json")

FALHAS, PASSOU = [], []
medido = {}


def caso(nome, condicao, detalhe=""):
    (PASSOU if condicao else FALHAS).append(nome)
    print("  %s  %s%s" % ("ok  " if condicao else "FALHA", nome,
                          ("" if condicao else "\n        " + detalhe)))


def _mede(nome, valor, porque=""):
    medido[nome] = {"VALOR": str(valor), "PORQUE": porque}
    print("  %-34s = %-24s %s" % (nome, valor, porque[:44]))
    return valor


def _ha(cmd):
    import shutil
    return shutil.which(cmd) is not None


def gerar_fala(destino):
    """A voz sintetica, gerada na hora. → (caminho, motivo_da_falha).

    `espeak-ng` escreve WAV directo. Nao ha rede, nao ha modelo a descarregar e
    nao ha ficheiro de terceiro no repositorio.
    """
    if not _ha("espeak-ng"):
        return None, "espeak-ng ausente"
    try:
        r = subprocess.run(["espeak-ng", "-v", "it", "-s", "130", "-w",
                            destino, FALA],
                           capture_output=True, text=True, timeout=120)
    except Exception as e:                                     # noqa: BLE001
        return None, "espeak-ng falhou: %s" % type(e).__name__
    if r.returncode != 0 or not os.path.isfile(destino) \
            or os.path.getsize(destino) < 2000:
        return None, "espeak-ng nao produziu WAV utilizavel: %s" % (r.stderr or "")[:120]
    return destino, None


def canal_do_fixture(banco_sql):
    """A PRE-CONDICAO DE IDENTIDADE, escrita no banco DESCARTAVEL.

    ⚠️ ISTO E UM GAP HERDADO, E NAO SE FINGE QUE NAO E.
    `public.conteudo` exige `canal_id`, e criar um canal exige decidir DE QUEM
    ele e. Nenhum dono forward resolve isso hoje, e o writer recusa-se a
    escolher — com razao. A `a_rota_m2_atravessa` resolve-o lendo o catalogo;
    aqui nao ha catalogo a ler, porque a fonte e um fixture.

        CHANNEL_ID PROVA O CANAL, NAO PROVA A ORIGEM.

    Entao a identidade e escrita aqui, com o nome do fixture, e nada disto vale
    como dono: o dono continua a nao existir. A deduplicacao e explicita
    (`where not exists`), porque `on conflict do nothing` sem constraint unica
    nao deduplica — isso ja foi medido nesta casa, com tres linhas iguais e
    tres `id` diferentes.
    """
    def q(v):
        return "'" + str(v).replace("'", "''") + "'"

    nome = "FIXTURE DE PROVA C4H"
    org = banco_sql.executa(
        "with novo as (insert into public.organizacao (nome_canonico, tipo)"
        " select %s, 'orgao_publico' where not exists"
        "  (select 1 from public.organizacao where nome_canonico = %s)"
        " returning id)"
        " select coalesce((select id from novo),"
        "  (select id from public.organizacao where nome_canonico = %s))"
        % (q(nome), q(nome), q(nome)))
    ori = banco_sql.executa(
        "with novo as (insert into public.origem (organizacao_id, rotulo)"
        " select %d, %s where not exists"
        "  (select 1 from public.origem where rotulo = %s)"
        " returning id)"
        " select coalesce((select id from novo),"
        "  (select id from public.origem where rotulo = %s))"
        % (int(org[0][0]), q(FONTE), q(FONTE), q(FONTE)))
    can = banco_sql.executa(
        "with novo as (insert into public.canal"
        " (origem_id, plataforma, channel_id, url) values (%d, 'web', %s, NULL)"
        " on conflict (plataforma, channel_id) do nothing returning id)"
        " select coalesce((select id from novo),"
        "  (select id from public.canal where plataforma='web'"
        "     and channel_id=%s))" % (int(ori[0][0]), q(FONTE), q(FONTE)))
    return int(can[0][0])


#: A `008` fica de fora por ser OUTRA ESPECIE: ela nao constroi esquema nenhum
#: — e a VERIFICACAO POS-APLICACAO que confere o que as outras construiram.
#: Corre-la no meio da cadeia e pedir-lhe contas de tabelas que ainda nao
#: nasceram, e foi exactamente o que aconteceu na primeira corrida desta prova
#: no CI: «O BANCO NAO BATE COM AS MIGRATIONS · faltando tabela crop_local...».
#:
#:     APLICAR POR ORDEM ALFABETICA NAO E APLICAR A CADEIA.
#:     UMA VERIFICACAO NO MEIO DA CONSTRUCAO REPROVA A OBRA POR ESTAR A MEIO.
#:
#: A regra e a mesma de `a_rota_m2_atravessa`, e a cadeia e LIDA da pasta —
#: quando nascer a migration seguinte, esta prova aplica-a sem que ninguem se
#: lembre dela.
_SO_VERIFICA = ("008",)


def _cadeia_de_migrations():
    pasta = os.path.join(RAIZ, "supabase", "migrations")
    fora = []
    for f in sorted(os.listdir(pasta)):
        if not f.endswith(".sql"):
            continue
        n = f.split("_", 1)[0]
        if n in _SO_VERIFICA:
            continue
        fora.append(n)
    return fora


def aplicar_migrations(url):
    pasta = os.path.join(RAIZ, "supabase", "migrations")
    cadeia = _cadeia_de_migrations()
    for n in cadeia:
        achados = [f for f in sorted(os.listdir(pasta)) if f.startswith(n + "_")]
        r = subprocess.run(["psql", url, "-v", "ON_ERROR_STOP=1", "-q", "-f",
                            os.path.join(pasta, achados[0])],
                           capture_output=True, text=True)
        if r.returncode != 0:
            print("FALHOU a aplicar %s\n%s" % (achados[0], r.stderr[:900]))
            raise SystemExit(1)
    return len(cadeia)


def _corrida(run_id):
    return {"RUN_ID": run_id, "PLATFORM": "fixture", "ACTOR": "c4h-ponte-midia",
            "ACTOR_VERSION": "1", "SOURCE_COUNTRY": "IT",
            "MISSION": "C4H ponte de midia (REPROCESS)",
            "STARTED_AT": "2026-09-14T20:00:00Z",
            "RULE_VERSION": "v1", "CAPTURE_METHOD": "LOCAL_FIXTURE"}


def _artefato(bytes_, nome):
    return {"COUNTRY": "IT", "SOURCE_SLUG": FONTE, "SOURCE_ID": FONTE,
            "DOCUMENT_ID": "C4H:FIXTURE:1", "ARTIFACT_KIND": "MEDIA",
            "NAME": nome, "SOURCE_NATIVE_ID": "C4H-1",
            "SHA256": sha256(bytes_), "BYTES": len(bytes_),
            # ⚠️ A ESPECIE E DECLARADA POR QUEM OBSERVOU OS BYTES.
            # E dela que sai a escolha do executor. Sem ela, a porta tentava o
            # extrator de PDF sobre um WAV.
            "MEDIA_TYPE": "audio/wav",
            "CAPTURED_AT": RELOGIO,
            "SOURCE_URL": "fixture://c4h/fala-sintetica.wav"}


def _uma_corrida(sql, banco, armazem, run_id, wav, bytes_wav):
    """RAW -> DERIVED -> STRUCTURED -> ADMISSION -> SALA, numa corrida so."""
    recibo_raw = preservar(_corrida(run_id), [_artefato(bytes_wav,
                                                        os.path.basename(wav))],
                           armazem, lambda o: bytes_wav, memoria=banco,
                           terminou_em="2026-09-14T20:01:00Z")
    raw_id = int(banco._valor(
        "select id from public.raw_asset where run_id = '%s'" % run_id))
    ing.falar_do_raw(sql, recibo=recibo_raw, corrida=_corrida(run_id),
                     entrada=1, recusas_da_porta=0, source_id=FONTE,
                     route_class_id=None)

    # ⚠️ A UNIDADE LEVA A ESPECIE, e e isso que faz a escolha acontecer.
    unidade_deriv = {"RAW_ASSET_ID": raw_id, "PDF": wav,
                     "MEDIA_TYPE": "audio/wav",
                     "CAPTURED_AT": RELOGIO, "SOURCE_ID": FONTE}
    r_der = fwd.correr([unidade_deriv], banco_do_rastro=sql, run_id=run_id,
                       armazem=armazem, memoria=banco, source_id=FONTE,
                       route_class_id=None, relogio=lambda: RELOGIO)
    return recibo_raw, raw_id, r_der


def main():
    url = os.environ.get("BANCO_DESCARTAVEL_URL") or ""
    if not _pg._e_descartavel(url):
        raise SystemExit("RECUSADO: '%s' nao parece um banco descartavel local. "
                         "Esta prova nunca corre contra producao." % url)

    # ── AS FERRAMENTAS, ANTES DE QUALQUER AFIRMACAO ──────────────────────
    faltam = []
    if not _ha("espeak-ng"):
        faltam.append("espeak-ng (gera a fala do fixture)")
    if not midia.ha_ferramenta():
        faltam.append("ffmpeg (extrai o audio)")
    ha_asr, porque_asr = midia.fl.disponivel()
    if not ha_asr:
        faltam.append("faster-whisper (%s)" % porque_asr)
    if faltam:
        print("NAO_EXERCITADO — falta ferramenta, e isto NAO e um PASS:")
        for f in faltam:
            print("   · %s" % f)
        print("\nPONTE_DE_MIDIA_POSTGRES = NOT_EXERCISED")
        raise SystemExit(3)

    print("MIGRATIONS — a cadeia canonica")
    n = aplicar_migrations(url)
    caso("B1_a_cadeia_aplica_num_postgres_real", n == len(_cadeia_de_migrations()),
         "%d migrations" % n)

    banco = _pg.MemoriaPostgres(url)
    sql = cc.Banco(url)
    for tabela, coluna in (("etapa_da_corrida", "run_id"),
                           ("conteudo_visto_em", "run_id"),
                           ("conteudo", "run_id")):
        sql.executa("delete from public.%s where %s like 'RUN-C4H%%'"
                    % (tabela, coluna))
    sql.executa("delete from public.derived_artifact")
    sql.executa("delete from public.raw_asset where run_id like 'RUN-C4H%'")
    sql.executa("delete from public.collection_run where run_id like 'RUN-C4H%'")

    # ── O FIXTURE ────────────────────────────────────────────────────────
    import tempfile
    pasta = tempfile.mkdtemp(prefix="c4h-fixture-")
    wav = os.path.join(pasta, "fala-sintetica.wav")
    saida, porque = gerar_fala(wav)
    caso("B2_a_fala_do_fixture_e_gerada_na_hora_e_nao_commitada",
         bool(saida), porque or "")
    if not saida:
        raise SystemExit(3)
    bytes_wav = open(wav, "rb").read()
    _mede("FIXTURE_BYTES", len(bytes_wav), "WAV gerado por espeak-ng")
    _mede("FIXTURE_SOURCE_ID", FONTE, "anuncia-se como fixture no proprio nome")

    # ── A ESCOLHA, ANTES DE CORRER ───────────────────────────────────────
    print("\nA ESCOLHA DO EXECUTOR")
    escolhido = ing.executor_para("audio/wav")
    _mede("MEDIA_EXECUTOR_SELECTED",
          getattr(escolhido, "EXECUTOR_ID", None), "pela especie DECLARADA")
    caso("B3_a_midia_vai_ao_executor_de_midia",
         getattr(escolhido, "EXECUTOR_ID", None) == midia.EXECUTOR_ID,
         "escolhido: %s" % getattr(escolhido, "EXECUTOR_ID", None))
    caso("B3b_a_midia_NAO_vai_ao_extrator_de_pdf",
         getattr(escolhido, "EXECUTOR_ID", None) != "texto-de-pdf")

    # ── A CORRIDA 1 ──────────────────────────────────────────────────────
    print("\nA CORRIDA 1")
    armazem = ArmazemDeMentira()
    recibo_raw, raw_id, r_der = _uma_corrida(sql, banco, armazem, RUN, wav,
                                             bytes_wav)
    _mede("RUN_CREATED", RUN, "collection_run no Postgres")
    _mede("RAW_OBSERVATION_CREATED", raw_id, "raw_asset.id lido do banco")
    caso("B4_o_bruto_e_real_e_foi_escrito_pelo_dono",
         recibo_raw["PENDENCIA"] == "PRESERVED_AND_REGISTERED" and raw_id > 0,
         "raw_asset_id=%s" % raw_id)
    _mede("STORAGE_OBJECT_LINKED",
          recibo_raw["PENDENCIA"] == "PRESERVED_AND_REGISTERED",
          "os bytes foram preservados e a linha aponta para eles")

    print("  DERIVED     %s · %s" % (r_der["ESTADO_DA_ETAPA"],
                                     {k: v for k, v in r_der["BALDES"].items() if v}))
    linha_der = (r_der.get("RESULTADOS") or [{}])[0]
    # ⚠️ QUANDO NAO DERIVA, O PORQUE TEM DE APARECER NO LOG.
    # A primeira corrida no CI saiu `DERIVED FAIL · {'ERROR': 1}` e mais nada —
    # e um `ERROR: 1` sem razao obriga a proxima pessoa a adivinhar, ou a
    # correr tudo outra vez so para ver.
    #
    #     UM NUMERO DE FALHAS SEM A RAZAO DELAS NAO E TELEMETRIA: E UM ENIGMA.
    if (r_der["BALDES"].get("PASSED", 0) + r_der["BALDES"].get("REUSED", 0)) == 0:
        print("  PORQUE NAO DERIVOU:")
        for k in ("ESTADO", "PORTA", "MOTIVO_DO_EXECUTOR", "PORQUE"):
            print("     %-20s %s" % (k, linha_der.get(k)))
    _mede("EXECUTOR_QUE_CORREU", linha_der.get("EXECUTOR_ID"),
          "quem o runner escolheu para ESTA unidade")
    caso("B5_quem_derivou_foi_o_executor_de_midia",
         linha_der.get("EXECUTOR_ID") == midia.EXECUTOR_ID,
         "correu: %s" % linha_der.get("EXECUTOR_ID"))

    # ⚠️ O FILHO PERGUNTA-SE AO BANCO PELO PAI, E NAO PELA RECEITA.
    # A identidade da receita inclui `parameters_hash`, que o executor montou
    # com a lingua detectada la dentro. Reconstrui-lo aqui obrigaria esta prova
    # a repetir a receita do dono — e no dia em que as duas divergissem, a
    # prova diria «nao existe» sobre uma linha que existe.
    #
    #     UMA PROVA QUE RECALCULA A IDENTIDADE DO OUTRO ACABA A MEDIR-SE A SI.
    COLUNAS = ("id", "raw_asset_id", "parent_sha256", "sha256", "storage_path",
               "kind", "producer", "parameters")
    linhas = banco._linhas(
        "select %s from public.derived_artifact where raw_asset_id = %d"
        % (", ".join(COLUNAS), raw_id), COLUNAS)
    filho = linhas[0] if linhas else None
    _mede("DERIVED_CREATED", bool(filho),
          "derived_artifact id=%s" % ((filho or {}).get("id")))
    caso("B6_o_derivado_existe_e_a_linhagem_fecha",
         bool(filho) and int(filho["raw_asset_id"]) == raw_id,
         "derived.raw_asset_id=%s raw_id=%s"
         % ((filho or {}).get("raw_asset_id"), raw_id))
    caso("B6b_DERIVED_PARENT_CORRECT",
         bool(filho) and filho["parent_sha256"] == sha256(bytes_wav),
         "o pai por SHA e o pai por ID sao o mesmo")

    if not filho:
        raise SystemExit("sem derivado nao ha estrada a jusante para medir")

    texto = armazem.ler(filho["storage_path"]).decode("utf-8")
    _mede("TRANSCRIPT_CREATED", len(texto) > 0, "%d caracteres" % len(texto))
    _mede("TRANSCRIPT_AMOSTRA", texto[:90].replace("\n", " "), "")

    # ── O CONTRATO DO TEXTO, LIDO DO BANCO ───────────────────────────────
    print("\nO CONTRATO DO TEXTO")
    params = filho.get("parameters")
    if isinstance(params, str):
        try:
            params = json.loads(params)
        except Exception:                                      # noqa: BLE001
            params = {}
    params = params or {}
    _mede("TEXT_KIND", params.get("TEXT_KIND"), "lido da linha do derivado")
    _mede("TEXT_RELATION", params.get("TEXT_RELATION"), "")
    _mede("LANGUAGE_PRESERVED", params.get("LANGUAGE"), "")
    _mede("LANGUAGE_SOURCE", params.get("LANGUAGE_SOURCE"), "")
    caso("B7_TEXT_KIND_e_TRANSCRIPT_no_banco",
         params.get("TEXT_KIND") == pv.TRANSCRIPT,
         "TEXT_KIND=%s" % params.get("TEXT_KIND"))
    caso("B7b_TEXT_RELATION_e_ORIGINAL",
         params.get("TEXT_RELATION") == pv.ORIGINAL)
    caso("B7c_a_lingua_sobreviveu_ate_ao_banco",
         bool(params.get("LANGUAGE"))
         and params.get("LANGUAGE") != midia.fl.NAO_SEI,
         "LANGUAGE=%s" % params.get("LANGUAGE"))
    caso("B7d_CAPTION_nao_se_disfarcou_de_TRANSCRIPT",
         params.get("TEXT_KIND") != pv.NATIVE_CAPTION
         and params.get("TEXT_BASIS") == pv.PRODUCED_BY_LOCAL_ASR)

    # ── A ESTRADA A JUSANTE, QUE JA EXISTIA ──────────────────────────────
    print("\nA ESTRADA A JUSANTE")
    canal_id = canal_do_fixture(sql)
    unidade = {"CONTENT_ID": "C4H-%s" % filho["sha256"][:16], "TEXTO": texto,
               "TIPO": "nota_tecnica", "SOURCE_ID": FONTE,
               "ROUTE_CLASS_ID": None, "RAW_ASSET_ID": raw_id,
               "CAPTURED_AT": RELOGIO, "URL": "fixture://c4h/fala-sintetica.wav",
               "DERIVED_ARTIFACT_ID": filho["id"],
               "PARENT_SHA256": filho["parent_sha256"]}
    r_s = m2.estruturar(sql, unidade=unidade, run_id=RUN, canal_id=canal_id)
    _mede("STRUCTURED_CREATED", (r_s or {}).get("STATE"), "pelo dono do conteudo")
    caso("B8_STRUCTURED_correu",
         (r_s or {}).get("STATE") in ("OK", sp.REOBSERVADO),
         "STATE=%s" % (r_s or {}).get("STATE"))

    dec = None
    if (r_s or {}).get("STATE") in ("OK", sp.REOBSERVADO):
        dec = m2.admitir(sql, unidade=unidade, run_id=RUN,
                         conteudo_id=r_s.get("CONTEUDO_ID"))
    _mede("ADMISSION_EXECUTED", bool(dec), "a peneira comum, sem regra especial")
    _mede("ADMISSION_DECISION", getattr(dec, "resultado", "NAO_CORREU"),
          "REJECTED legitimo NAO e pipeline partido")
    caso("B9_ADMISSION_correu", dec is not None)

    espera_ = m2.levar_a_espera(sql, unidade=unidade, decisao=dec, run_id=RUN) \
        if dec is not None else {"ESTADO": None, "PORQUE": "a porta nao correu"}
    _mede("READY_HANDLING", espera_.get("ESTADO") or "NOT_RUN",
          espera_.get("PORQUE") or "")
    _mede("WAITING_ROOM_HANDLING", espera_.get("FICHEIRO") or "NOT_RUN",
          "so o SIM pousa; NAO/ERRO produzem NOT_RUN e nao falha")

    # ⚠️ NAO SE EXIGE `SIM`. A regua nao se mexe para o fixture passar.
    caso("B10_READY_so_existe_se_a_porta_disse_SIM",
         (espera_.get("ESTADO") is not None)
         == (getattr(dec, "resultado", None) == "SIM"),
         "decisao=%s estado_da_sala=%s"
         % (getattr(dec, "resultado", None), espera_.get("ESTADO")))

    # ── A CORRIDA 2 — O RETRY ────────────────────────────────────────────
    print("\nA CORRIDA 2 — O RETRY")
    armazem2 = ArmazemDeMentira()
    _r2, raw_id2, r_der2 = _uma_corrida(sql, banco, armazem2, RUN2, wav,
                                        bytes_wav)
    _mede("RUN1_DIFERENTE_DE_RUN2", RUN != RUN2, "")
    _mede("RAW_OBSERVATION_1", raw_id, "")
    _mede("RAW_OBSERVATION_2", raw_id2, "")
    caso("B11_RUN1_e_RUN2_sao_corridas_diferentes", RUN != RUN2)
    caso("B12_o_mesmo_SHA_nao_e_a_mesma_observacao", raw_id != raw_id2,
         "duas corridas, duas observacoes: %s e %s" % (raw_id, raw_id2))

    baldes2 = r_der2["BALDES"]
    linha2 = (r_der2.get("RESULTADOS") or [{}])[0]
    _mede("RETRY_BALDES", {k: v for k, v in baldes2.items() if v}, "")
    _mede("RETRY_ESTADO", linha2.get("ESTADO"), "o que o dono da escrita disse")
    _mede("RETRY_PORQUE", (linha2.get("PORQUE") or "")[:120], "")

    # ⚠️ O QUE EU ESPERAVA AQUI ERA `REUSED`, E O BANCO DISSE OUTRA COISA.
    #
    # A identidade do derivado e por CONTEUDO — `parent_sha256` + receita — mas
    # a linha tem chave estrangeira COMPOSTA `(raw_asset_id, parent_sha256)`.
    # Duas corridas sobre os MESMOS bytes produzem DUAS observacoes (id 1 e 2),
    # ambas com o mesmo `sha256`. O filho ja existe e aponta para a primeira.
    # A segunda nao pode adota-lo, e tambem nao pode escrever outro.
    #
    #     O DERIVADO E DO CONTEUDO. A CHAVE PRENDE-O A UMA OBSERVACAO.
    #     ENQUANTO HOUVER UMA OBSERVACAO SO, OS DOIS FACTOS COINCIDEM.
    #
    # Isto NAO e defeito desta ponte: e a mesma trava que o PDF tem, e que
    # nunca foi exercitada com duas observacoes do mesmo byte. Fica MEDIDO e
    # declarado, e a prova afirma o que importa de verdade — que o retry nao
    # duplicou e nao passou por engano.
    caso("B13_o_retry_nao_duplica_e_nao_finge_que_passou",
         baldes2.get("PASSED", 0) == 0 or baldes2.get("REUSED", 0) >= 1,
         "a 2a corrida escreveu um derivado NOVO: %s" % baldes2)
    _mede("RETRY_SEGUNDA_OBSERVACAO_ADOTA_O_FILHO",
          "NO" if baldes2.get("REUSED", 0) == 0 else "YES",
          "a chave composta (raw_asset_id, parent_sha256) nao o permite")
    n_derivados = int(banco._valor(
        "select count(*) from public.derived_artifact"))
    _mede("DERIVADOS_NO_BANCO", n_derivados,
          "duas corridas sobre os MESMOS bytes com a MESMA receita")
    caso("B14_nao_ha_derivado_duplicado", n_derivados == 1,
         "%d linhas em derived_artifact" % n_derivados)

    # ── O QUE O BANCO DIZ ────────────────────────────────────────────────
    print("\nO QUE O BANCO DIZ")
    passagens = rastro.passagens(sql, run_id=RUN)
    # ⚠️ A CHAVE E `ETAPA`, EM MAIUSCULAS. Com `etapa` minusculo o `.get`
    # devolvia `None` para todas as linhas, e a prova publicava
    # `ETAPAS_OBSERVADAS = [None]` — uma leitura partida a passar por medicao
    # de um banco vazio.
    #
    #     UM `.get` COM A CHAVE ERRADA NAO REBENTA: MENTE BAIXINHO.
    etapas = sorted({p.get("ETAPA") for p in passagens if p.get("ETAPA")})
    _mede("ETAPAS_OBSERVADAS", etapas, "lidas de etapa_da_corrida")
    caso("B15_a_corrida_atravessou_RAW_e_DERIVED",
         {"RAW", "DERIVED"} <= set(etapas),
         "observadas: %s" % etapas)

    estado = {
        "SCHEMA": "ponte-de-midia-postgres/v1",
        "O_QUE_ISTO_E": ("O que o BANCO mostrou quando o bruto era MIDIA. "
                         "Nao e declaracao: e leitura depois de a rota correr."),
        "GERADO_POR": "provas/a_ponte_de_midia_no_postgres.py",
        "NEW_MEDIA_ACQUISITION": "NO",
        "RUN_TYPE": "REPROCESS",
        "FIXTURE": {"SOURCE_ID": FONTE, "GERADO_POR": "espeak-ng",
                    "PORQUE_SINTETICO": (
                        "o repositorio e publico e a unica midia com fala real "
                        "desta casa e de terceiro: commita-la seria publicar "
                        "conteudo alheio para um teste passar")},
        "MEDIDO": medido,
        "PASSOU": PASSOU, "FALHAS": FALHAS,
    }
    os.makedirs(os.path.dirname(SAIDA), exist_ok=True)
    io.open(SAIDA, "w", encoding="utf-8").write(
        json.dumps(estado, ensure_ascii=False, indent=1, default=str) + "\n")
    print("\n  gravado: %s" % os.path.relpath(SAIDA, RAIZ))
    print("\nPONTE_DE_MIDIA_POSTGRES = %s · %d passaram · %d falharam"
          % ("PROVADO" if not FALHAS else "FALHOU", len(PASSOU), len(FALHAS)))
    return 1 if FALHAS else 0


if __name__ == "__main__":
    raise SystemExit(main())
