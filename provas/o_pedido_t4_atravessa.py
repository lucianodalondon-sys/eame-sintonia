#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""UM PEDIDO T4 ATRAVESSA — de REQUEST ate a SALA DE ESPERA, na MESMA historia.

    BANCO_DESCARTAVEL_URL=postgresql://postgres@127.0.0.1:5433/descartavel \\
    SALA_DESCARTAVEL=/tmp/sala \\
        python3 provas/o_pedido_t4_atravessa.py

POR QUE ESTA PROVA EXISTE AO LADO DA OUTRA, E NAO NO LUGAR DELA
----------------------------------------------------------------
`provas/o_pedido_atravessa.py` mede o pedido T2 e o buraco dele. Essa medicao
continua verdadeira e continua a valer: T2 nao tem regra de admissao escrita, e
a porta responde-lhe `NAO_SE_APLICA` — que e a resposta certa.

    DUAS PERGUNTAS DIFERENTES NAO CABEM NA MESMA PROVA
    SEM QUE UMA DELAS PASSE A SER RUIDO DA OUTRA.

Esta responde a outra pergunta: existe UMA classe que atravessa a Collection
inteira? O censo (`provas/o_canario_da_collection.py`) mediu que T4 estava a
UMA peca — tinha regra e dono STRUCTURED, faltava-lhe aquisicao canonica. Esta
prova mede se essa peca chegou.

O QUE ELA NAO FAZ
-----------------
Nao chama `admitir()`, nem `pronto_para_inteligencia()`, nem
`sala_de_espera.pousar()`. Nao abre `collection_run` a mao. Nao fabrica
`raw_asset`. Aperta o botao em `orquestrador.correr()` com um `Pedido` e
pergunta ao banco e ao disco o que aquela corrida deixou.

    UMA PROVA QUE COMECA PELO MEIO NAO PROVA A ESTRADA:
    PROVA O PEDACO POR ONDE ELA COMECOU.

E O EXECUTOR VAI A FONTE REAL. Nao ha fixture nenhuma nesta prova: o PDF vem do
EUR-Lex, pela rota que o contrato de `EU-T4-001` declara. Sem rede, isto NAO
corre — e diz que nao correu, em vez de passar.

    FIXTURE PROVA PARSER. SO A INTERNET PROVA AQUISICAO.
"""
import io
import json
import os
import subprocess
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)
import _gavetas  # noqa: E402,F401

import admissao                                     # noqa: E402
import coleta_checkpoint as cc                      # noqa: E402
import sala_de_espera as espera                     # noqa: E402
from pedido import Pedido                           # noqa: E402

ESTRADA = ("REQUEST", "ORCHESTRATOR", "EXECUTOR", "RUN", "RAW",
           "STORAGE", "DERIVED", "STRUCTURED", "ADMISSION", "READY",
           "WAITING_ROOM")
_SO_VERIFICA = ("008",)
SAIDA = os.path.join("system-map", "data", "pedido-t4.observado.json")

# ⚠️ O CRITERIO DO CANARIO POSITIVO, ESCRITO ANTES DE SE VER A RESPOSTA.
# A missao exige-o por escrito, e a razao e boa: escolher o caso depois de ver
# o resultado da porta e desenhar o alvo a volta da flecha.
#
# O ato nao foi escolhido por mim. `EU-T4-001` declara-o no campo
# `real_example` da propria ficha, escrito por outra missao, muito antes desta.
# Nao se varreu catalogo nenhum a procura de um ato que casasse com o
# vocabulario de T4.
#
#     O CRITERIO TEM DE SER MAIS VELHO DO QUE A MEDICAO.
CELEX = "32026R1696"
PORQUE_ELE_E_T4 = (
    "o atlas declara `EU-T4-001` com `territory: T4` e `type: Registro legal "
    "oficial primario`, e este CELEX e o `real_example` da propria ficha. O "
    "ato e um Regulamento de Execucao publicado no Jornal Oficial da UE que "
    "renova a aprovacao de uma substancia ativa ao abrigo do Reg. 1107/2009 — "
    "regulatorio por aquilo que E, e nao por casar com uma palavra")

fora = []
visto = {}
# A origem dos bytes desta medicao — `REDE`, `ARQUIVO_LOCAL` ou `NAO_MEDIDA`.
ORIGEM_DOS_BYTES = "NAO_MEDIDA"


def _origem_declarada(recibo):
    """O que o executor DECLAROU sobre a origem dos bytes desta corrida.

    Le o envelope que a corrida escreveu. Nao se adivinha pela presenca do
    ficheiro em disco: o ficheiro estar la nao diz se ele foi buscado agora ou
    ha duas horas — e essa e exactamente a pergunta.
    """
    import retorno_da_coleta as rdc_
    from receitas import EXECUTORES as EX_
    e = (EX_.get("T4") or [{}])[0]
    padrao = (e.get("retorno") or {}).get("ENVELOPE")
    run_id = recibo.get("RUN_ID")
    if not padrao or not run_id:
        return "NAO_MEDIDA"
    caminho = os.path.join(RAIZ, rdc_.endereco_do_envelope(padrao, run_id))
    if not os.path.isfile(caminho):
        return "NAO_MEDIDA"
    with io.open(caminho, encoding="utf-8") as fh:
        env = json.load(fh)
    origens = {u.get("ORIGEM_DOS_BYTES") for u in (env.get("COLHEITA") or [])}
    if len(origens) == 1:
        return origens.pop() or "NAO_MEDIDA"
    return "MISTURADA" if origens else "NAO_MEDIDA"


def caso(nome, condicao, detalhe=""):
    fora.append((nome, bool(condicao), detalhe))


def etapa(nome, observada, evidencia):
    visto[nome] = {"OBSERVED": bool(observada), "EVIDENCE": evidencia}


def uma_corrida_so(quantas):
    """Isolada para poder ser ela propria conferida — e usada nos dois lados.

    ⚠️ ESCRITA A DIREITO NO CASO POSITIVO, ELA SOBREVIVE A MUTACAO: `== 1`
    trocado por `>= 1` nao muda nada num banco com uma corrida so.
    """
    return quantas == 1


def cadeia_de_migrations():
    pasta = os.path.join(RAIZ, "supabase", "migrations")
    return [f.split("_", 1)[0] for f in sorted(os.listdir(pasta))
            if f.endswith(".sql") and f.split("_", 1)[0] not in _SO_VERIFICA]


def aplicar_migrations(url):
    pasta = os.path.join(RAIZ, "supabase", "migrations")
    for n in cadeia_de_migrations():
        a = [f for f in sorted(os.listdir(pasta)) if f.startswith(n + "_")]
        r = subprocess.run(["psql", "-v", "ON_ERROR_STOP=1", "-q", "-f",
                            os.path.join(pasta, a[0]), url],
                           capture_output=True, text=True)
        if r.returncode != 0:
            print("FALHOU a aplicar %s\n%s" % (a[0], r.stderr[:600]))
            raise SystemExit(1)


def _memoria(url):
    import importlib.util as u
    sp_ = u.spec_from_file_location(
        "prova_pg", os.path.join(RAIZ, "provas",
                                 "preservar_coleta_no_postgres.py"))
    m = u.module_from_spec(sp_)
    sp_.loader.exec_module(m)
    return m.MemoriaPostgres(url)


def main():
    url = os.environ.get("BANCO_DESCARTAVEL_URL")
    sala = os.environ.get("SALA_DESCARTAVEL")
    if not url or not sala:
        print("FALTA AMBIENTE DESCARTAVEL — e SKIP != PASS.")
        print("  BANCO_DESCARTAVEL_URL · SALA_DESCARTAVEL")
        print("PEDIDO_T4_ATRAVESSA=NOT_MEASURED")
        return 2
    espera.MORADA = sala
    import pathlib
    import tempfile
    # O livro fica FORA da sala: posto dentro, conta como ficheiro da espera.
    admissao.LIVRO = (pathlib.Path(tempfile.mkdtemp(prefix="livro-t4-"))
                      / "LIVRO-DE-DECISOES.json")

    print("=" * 70)
    print("UM PEDIDO T4 ATRAVESSA — %d migrations · ambiente descartavel"
          % len(cadeia_de_migrations()))
    print("  canario: CELEX %s" % CELEX)
    print("  criterio (escrito ANTES da medicao): %s" % PORQUE_ELE_E_T4[:110])
    aplicar_migrations(url)
    sql = cc.Banco(url)

    antes_na_sala = sorted(os.listdir(sala)) if os.path.isdir(sala) else []
    caso("P0_a_sala_comeca_VAZIA", not antes_na_sala,
         "ficheiros na sala antes de apertar o botao: %s"
         % (antes_na_sala or "nenhum"))

    # ── O BOTAO, NO UNICO PONTO DE ENTRADA CANONICO ─────────────────────
    import orquestrador as orq
    p = Pedido(alvo="T4", filtros={"pais": "IT", "celex": CELEX})
    recibo = orq.correr(p, memoria=_memoria(url), banco_do_rastro=sql)
    recibo.pop("_plano", None)
    run_id = recibo.get("RUN_ID")

    # ── REQUEST ─────────────────────────────────────────────────────────
    ped = recibo.get("PEDIDO") or {}
    etapa("REQUEST", ped.get("alvo") == "T4",
          "recibo.PEDIDO = %s" % json.dumps(ped, ensure_ascii=False))
    caso("T1_o_PEDIDO_T4_entrou_e_ficou_escrito_no_recibo",
         ped.get("alvo") == "T4"
         and ped.get("filtros", {}).get("celex") == CELEX,
         p.em_uma_frase())

    # ── ORCHESTRATOR ────────────────────────────────────────────────────
    etapa("ORCHESTRATOR", bool(recibo.get("ACTOR")),
          "ACTOR=%s · PLATFORM=%s · CAPTURE_METHOD=%s"
          % (recibo.get("ACTOR"), recibo.get("PLATFORM"),
             recibo.get("CAPTURE_METHOD")))
    caso("T2_o_ORQUESTRADOR_escolheu_o_executor_CANONICO_e_cunhou_a_corrida",
         recibo.get("ACTOR") == "coleta/eu_regulatorio_executor.py"
         and bool(run_id),
         "%s -> %s" % (recibo.get("ACTOR"), run_id))

    # ── EXECUTOR ────────────────────────────────────────────────────────
    # CAN DO != DID DO: o que prova a execucao e o COMANDO lancado e a
    # colheita que ele declarou.
    correu = (recibo.get("STATUS") == "SUCCESS"
              and "eu_regulatorio_executor.py" in (recibo.get("COMANDO") or "")
              and (recibo.get("COLHEITA_ENCONTRADA") or 0) > 0)
    etapa("EXECUTOR", correu,
          "COMANDO=%s · versao=%s · colheita=%s"
          % (recibo.get("COMANDO"), recibo.get("ACTOR_VERSION"),
             recibo.get("COLHEITA_ENCONTRADA")))
    caso("T3_o_EXECUTOR_REAL_correu_e_TROUXE_COLHEITA", correu,
         "%s itens · %s" % (recibo.get("COLHEITA_ENCONTRADA"),
                            (recibo.get("RETORNO") or {}).get("ESTADO")))

    # ⚠️ DE ONDE VIERAM OS BYTES — E SAO DUAS PROPRIEDADES, NAO UMA.
    # A estrada atravessar e uma coisa. A AQUISICAO estar provada e outra: so
    # a rede prova aquisicao, e um executor que reaproveita bytes que ja tinha
    # em disco atravessou a estrada sem ter ido a fonte.
    #
    #     FIXTURE PROVA PARSER. SO A INTERNET PROVA AQUISICAO.
    #     E REAPROVEITAR O QUE JA SE TEM NAO E FIXTURE — E TAMBEM NAO E REDE.
    #
    # Escondendo esta diferenca, uma noite inteira de provas verdes diria
    # «a aquisicao funciona» sem ninguem ter aberto uma ligacao. O executor
    # DECLARA a origem, e esta prova le a declaracao em vez de a supor.
    global ORIGEM_DOS_BYTES
    ORIGEM_DOS_BYTES = _origem_declarada(recibo)
    caso("T3c_o_executor_DECLARA_de_onde_vieram_os_bytes",
         ORIGEM_DOS_BYTES in ("REDE", "ARQUIVO_LOCAL"),
         "ORIGEM_DOS_BYTES=%s" % ORIGEM_DOS_BYTES)
    caso("T3b_e_nao_foi_um_ensaio_seco",
         "(ensaio seco" not in (recibo.get("SAIDA") or "")
         and "(nao se colheu" not in (recibo.get("SAIDA") or ""),
         "o executor foi mesmo chamado")
    # ⚠️ E A COLHEITA E COLHEITA, E NAO SUPORTE.
    # Esta e a peca que faltava a T4, e e o unico sitio onde ela se ve.
    ret = recibo.get("RETORNO") or {}
    caso("T3d_o_retorno_e_ENVELOPE_e_nao_LEGADO",
         (ret.get("ESPECIE_DECLARADA") or ret.get("ORIGEM") or "") != "LEGADO"
         and (recibo.get("COLHEITA_ENCONTRADA") or 0) > 0,
         "retorno=%s" % json.dumps(ret, ensure_ascii=False)[:150])

    # ── RUN ─────────────────────────────────────────────────────────────
    corrida = sql.executa(
        "select run_id, status from public.collection_run where run_id = '%s'"
        % run_id)
    etapa("RUN", bool(corrida), "collection_run: %s" % (corrida or "vazio"))
    caso("T4_a_RUN_existe_no_banco_e_e_a_MESMA_do_recibo",
         bool(corrida) and corrida[0][0] == run_id,
         "RUN_ID=%s · status=%s" % (run_id, corrida[0][1] if corrida else "-"))

    # ── RAW ─────────────────────────────────────────────────────────────
    brutos = sql.executa(
        "select id, source_id, document_key, document_key_basis,"
        " identity_state from public.raw_asset where run_id = '%s' order by id"
        % run_id)
    etapa("RAW", bool(brutos), "raw_asset da corrida: %s"
          % [b[0] for b in brutos])
    caso("T5_o_RAW_aterrou_e_e_da_MESMA_corrida", len(brutos) == 1,
         "%d observacao(oes) · ids %s" % (len(brutos), [b[0] for b in brutos]))
    caso("T5b_a_fonte_NAO_foi_inferida_do_caminho",
         bool(brutos) and brutos[0][1] == "EU-T4-001",
         "source_id declarado pelo coletor: %s"
         % sorted({b[1] for b in brutos}))
    # ⚠️ E AQUI ESTA A COISA RARA DESTA MISSAO.
    # Pela primeira vez nesta casa uma observacao aterra com IDENTIDADE
    # DOCUMENTAL PROVADA. Nao e o sha, nao e o caminho, nao e a URL: e o CELEX,
    # que o contrato da fonte declara como `identity_keys`.
    caso("T5c_a_identidade_do_DOCUMENTO_veio_PROVADA_pela_fonte",
         bool(brutos) and brutos[0][2] == CELEX
         and brutos[0][3] == "SOURCE_DOCUMENT_ID"
         and brutos[0][4] == "FORWARD_IDENTIFIED",
         "document_key=%s · basis=%s · estado=%s"
         % (brutos[0][2], brutos[0][3], brutos[0][4]) if brutos else "sem RAW")

    # ── STORAGE ─────────────────────────────────────────────────────────
    objetos = sql.executa(
        "select count(*) from public.storage_object o"
        " join public.raw_asset r on r.storage_object_id = o.id"
        " where r.run_id = '%s'" % run_id)
    n_obj = int(objetos[0][0]) if objetos else 0
    etapa("STORAGE", n_obj > 0, "storage_object ligados a esta corrida: %d"
          % n_obj)
    caso("T6_o_OBJETO_guardado_existe_e_esta_ligado_a_observacao",
         n_obj == len(brutos), "%d objetos para %d observacoes"
         % (n_obj, len(brutos)))

    # ── DERIVED ─────────────────────────────────────────────────────────
    derivados = sql.executa(
        "select d.id, d.kind from public.derived_artifact d"
        " join public.participacao_na_derivacao p"
        "   on p.derived_artifact_id = d.id"
        " join public.raw_asset r on r.id = p.raw_asset_id"
        " where r.run_id = '%s' order by d.id" % run_id)
    etapa("DERIVED", bool(derivados), "derived_artifact desta corrida: %d"
          % len(derivados))
    caso("T7_o_DERIVADO_nasceu_e_a_participacao_material_existe",
         len(derivados) == len(brutos),
         "%d derivados · %d participacoes com a observacao desta corrida"
         % (len(derivados), len(derivados)))

    # ── STRUCTURED ──────────────────────────────────────────────────────
    docs = sql.executa(
        "select derived_artifact_id, source_id, document_id, hash_texto"
        " from public.documento_estruturado where run_id = '%s'" % run_id)
    etapa("STRUCTURED", bool(docs), "documento_estruturado: %d" % len(docs))
    caso("T8_o_documento_foi_ESTRUTURADO_nesta_corrida",
         len(docs) == len(derivados),
         "%d registos para %d derivados" % (len(docs), len(derivados)))
    caso("T8b_e_o_registo_NAO_fabricou_identidade",
         all(d[2] != d[3] for d in docs),
         "document_id nunca e o hash do texto: %s"
         % [(d[2] or "<NULL>") for d in docs])

    # ── ADMISSION ───────────────────────────────────────────────────────
    adm = recibo.get("ADMISSAO") or {}
    por_res = adm.get("por_resultado") or {}
    etapa("ADMISSION", bool(por_res),
          "a porta julgou %s itens: %s" % (adm.get("itens"), por_res))
    caso("T9_a_porta_JULGOU_com_a_regra_de_T4_que_JA_EXISTIA",
         "T4" in admissao.PERGUNTAS_DO_UNIVERSO and bool(por_res),
         "universo T4 tem %d termos escritos, e nenhum foi acrescentado nesta"
         " missao" % len(admissao.PERGUNTAS_DO_UNIVERSO.get("T4") or []))
    caso("T9b_o_resultado_foi_SIM_e_por_um_documento_REAL",
         por_res.get(admissao.SIM, 0) == len(docs) and len(docs) > 0,
         "por_resultado=%s" % por_res)

    # ── READY ───────────────────────────────────────────────────────────
    prontos = adm.get("prontos") or 0
    etapa("READY", prontos > 0, "unidades prontas: %d" % prontos)
    caso("T10_o_SIM_produziu_READY", prontos == por_res.get(admissao.SIM, 0)
         and prontos > 0, "prontos=%d" % prontos)

    # ── WAITING ROOM ────────────────────────────────────────────────────
    na_sala = sorted(os.listdir(sala)) if os.path.isdir(sala) else []
    ficheiros = [f for f in na_sala if f.endswith(".json")]
    etapa("WAITING_ROOM", bool(ficheiros),
          "ficheiros na sala DEPOIS: %s" % (ficheiros or "nenhum"))
    caso("T11_a_unidade_POUSOU_na_sala_e_o_ficheiro_e_DESTA_corrida",
         bool(ficheiros) and any(run_id in f for f in ficheiros),
         "sala=%s · corrida=%s" % (ficheiros, run_id))

    # ── A MESMA HISTORIA ────────────────────────────────────────────────
    outras = sql.executa("select count(distinct run_id) from public.raw_asset")
    inteira = all(visto.get(e, {}).get("OBSERVED") for e in ESTRADA)
    caso("T12_a_estrada_inteira_foi_atravessada_pelo_MESMO_pedido",
         inteira and uma_corrida_so(int(outras[0][0])),
         "etapas observadas: %d de %d · corridas em raw_asset: %s"
         % (sum(1 for e in ESTRADA if visto.get(e, {}).get("OBSERVED")),
            len(ESTRADA), outras[0][0]))

    ultima, perdido = None, None
    for e in ESTRADA:
        if visto.get(e, {}).get("OBSERVED"):
            ultima = e
        elif perdido is None:
            perdido = e

    _depois_do_fecho(sql, url, run_id, brutos, docs, sala)

    print("=" * 70)
    print("  A ESTRADA T4, ETAPA A ETAPA")
    for e in ESTRADA:
        v = visto.get(e, {"OBSERVED": False, "EVIDENCE": "nao medida"})
        print("    %-13s %-4s %s" % (e, "SIM" if v["OBSERVED"] else "NAO",
                                     str(v["EVIDENCE"])[:88]))
    print()
    for nome, ok, detalhe in fora:
        print("  %-4s %-56s %s" % ("PASS" if ok else "FALHA", nome,
                                   str(detalhe)[:70]))
    if ACHADOS:
        print()
        print("  ACHADOS — medidos, e o estado ao lado diz se ja curaram")
        for nome, estado, detalhe in ACHADOS:
            print("    %-22s %-12s %s" % (nome, estado, detalhe[:60]))
    print("=" * 70)
    print("CANONICAL_E2E_T4=%s" % ("PASS" if inteira else "FAIL"))
    if not inteira:
        print("  LAST_PROVEN_STAGE   = %s" % ultima)
        print("  FIRST_LOST_EDGE     = %s -> %s" % (ultima, perdido))
    print("  SAME_STORY=%s · uma corrida so em raw_asset"
          % ("YES" if uma_corrida_so(int(outras[0][0])) else "NO"))
    print("  ORIGEM_DOS_BYTES=%s" % ORIGEM_DOS_BYTES)
    print("  AQUISICAO_PELA_REDE=%s"
          % ("PASS" if ORIGEM_DOS_BYTES == "REDE" else "NOT_PROVEN"))
    if ORIGEM_DOS_BYTES != "REDE":
        print("    a estrada atravessou com bytes que esta arvore JA tinha "
              "preservado.\n    A maquina esta provada; a ida a fonte, nesta "
              "corrida, nao esta.")

    with io.open(os.path.join(RAIZ, SAIDA), "w", encoding="utf-8") as fh:
        json.dump({"CLASSE": "T4", "CELEX": CELEX,
                   "CRITERIO_DO_CANARIO": PORQUE_ELE_E_T4,
                   "RUN_ID": run_id, "ESTRADA": visto,
                   "FIRST_LOST_EDGE": (None if inteira
                                       else "%s -> %s" % (ultima, perdido)),
                   "ACHADOS_NAO_CONSERTADOS": [
                       {"NOME": n, "ESTADO": e_, "DETALHE": d}
                       for n, e_, d in ACHADOS],
                   "ORIGEM_DOS_BYTES": ORIGEM_DOS_BYTES,
                   "AQUISICAO_PELA_REDE": ("PASS" if ORIGEM_DOS_BYTES == "REDE"
                                           else "NOT_PROVEN"),
                   "CANONICAL_E2E": "PASS" if inteira else "FAIL"},
                  fh, ensure_ascii=False, indent=2)
        fh.write("\n")

    medido = all(ok for n, ok, _d in fora)
    print("PEDIDO_T4_ATRAVESSA=%s" % ("MEDIDO" if medido else "MEDICAO_FALHOU"))
    return 0 if medido else 1


def _depois_do_fecho(sql, url, run_id, brutos, docs, sala):
    """O que a missao manda medir DEPOIS do primeiro PASS.

    ⚠️ PARAR NO PRIMEIRO VERDE E MEDIR O PRIMEIRO DIA.
    Uma estrada que atravessa uma vez e uma estrada que atravessou uma vez. O
    que a coleta grande precisa e que ela atravesse OUTRA vez sem duplicar o
    que nao deve e sem calar o que mudou.
    """
    import orquestrador as orq

    # ── A SEGUNDA CORRIDA, REAL ─────────────────────────────────────────
    r2 = orq.correr(Pedido(alvo="T4", filtros={"pais": "IT", "celex": CELEX}),
                    memoria=_memoria(url), banco_do_rastro=sql)
    r2.pop("_plano", None)
    run2 = r2.get("RUN_ID")
    caso("R1_a_SEGUNDA_corrida_e_outra_corrida", bool(run2) and run2 != run_id,
         "corridas: %s e %s" % (run_id, run2))

    # ⚠️ OBSERVAR DUAS VEZES E OBSERVAR DUAS VEZES.
    # Os mesmos bytes, colhidos de novo, sao uma observacao NOVA: `raw_asset`
    # e por corrida. Confundir isto com reaproveitamento apagaria a segunda
    # visita ao mundo.
    brutos2 = sql.executa(
        "select id from public.raw_asset where run_id = '%s'" % run2)
    caso("R2_a_observacao_nova_NAO_e_reaproveitada",
         len(brutos2) == len(brutos),
         "observacoes da 2a corrida: %d" % len(brutos2))

    # ── O DERIVADO REENCONTRA-SE, E ISSO NAO E «NAO CORREU» ─────────────
    pas = sql.executa(
        "select estado::text, passed, reused from public.etapa_da_corrida"
        " where etapa = 'DERIVED' and run_id = '%s'" % run2)
    caso("R3_o_DERIVADO_foi_REAPROVEITADO_e_a_etapa_CORREU",
         bool(pas) and pas[0][0] == "PASS" and int(pas[0][2]) > 0
         and int(pas[0][1]) == 0,
         "DERIVED da 2a corrida: %s · passed=%s reused=%s"
         % (pas[0][0], pas[0][1], pas[0][2]) if pas
         else "a 2a corrida nao emitiu DERIVED")

    # ── E A PARTICIPACAO DA OBSERVACAO NOVA EXISTE ──────────────────────
    # REUSED != NOT_RUN, e tambem != «esta observacao nao participou».
    part = sql.executa(
        "select count(*) from public.participacao_na_derivacao p"
        " join public.raw_asset r on r.id = p.raw_asset_id"
        " where r.run_id = '%s'" % run2)
    caso("R4_a_observacao_REAPROVEITADA_declara_que_participou",
         int(part[0][0]) == len(brutos2),
         "participacoes da 2a corrida: %s" % part[0][0])

    # ── O DOCUMENTO NAO DUPLICA ─────────────────────────────────────────
    # `documento_estruturado` e chaveada pelo `derived_artifact_id`. Um
    # derivado reaproveitado ja tem registo, e o dono devolve REUSED.
    docs2 = sql.executa("select count(*) from public.documento_estruturado")
    caso("R5_o_DOCUMENTO_nao_duplicou_com_o_derivado_reaproveitado",
         int(docs2[0][0]) == len(docs),
         "documentos no banco depois de duas corridas: %s" % docs2[0][0])

    # ── A SALA RECEBE A SEGUNDA, E COM O NOME DELA ──────────────────────
    na_sala = sorted(f for f in os.listdir(sala) if f.endswith(".json"))
    caso("R6_a_SALA_guarda_as_duas_historias_separadas",
         len(na_sala) == 2 and any(run2 in f for f in na_sala),
         "sala: %s" % na_sala)

    # ── OS QUATRO ESTADOS CONTINUAM DIFERENTES ──────────────────────────
    baldes = sql.executa(
        "select coalesce(sum(passed),0), coalesce(sum(reused),0),"
        " coalesce(sum(rejected),0), coalesce(sum(error_count),0),"
        " coalesce(sum(not_run_count),0) from public.etapa_da_corrida"
        " where etapa = 'DERIVED'")
    passed, reused, rej, err, notrun = [int(x) for x in baldes[0]]
    # ── O QUE SE MEDIU E NAO SE CONSERTOU ───────────────────────────────
    # ⚠️ ISTO NAO E UM CASO COM VEREDICTO, E E DE PROPOSITO.
    # Um `caso()` que AFIRMASSE o comportamento de hoje passaria a ABENCOA-LO:
    # no dia em que alguem o consertasse, a prova reprovava a correccao.
    #
    #     UMA GUARDA QUE FIXA O DEFEITO DE HOJE DEFENDE O DEFEITO.
    #
    # Entao mede-se, escreve-se, e fica como divida com nome — nao como
    # promessa de que esta certo.
    _achado_do_envelope_partilhado()

    caso("R7_NEW_REUSED_ERROR_e_NOT_RUN_continuam_baldes_diferentes",
         passed > 0 and reused > 0 and rej == 0 and err == 0 and notrun == 0,
         "passed=%d reused=%d rejected=%d error=%d not_run=%d"
         % (passed, reused, rej, err, notrun))


ACHADOS = []


def _achado_do_envelope_partilhado():
    """O ENVELOPE VIVIA NUM CAMINHO FIXO, E DUAS CORRIDAS PARTILHAVAM-NO.

    ⚠️ CURADO EM `C-COLLECTION-OPERATIONAL-READINESS-OVERNIGHT-V1`, e esta
    medicao FICA — porque uma cura sem guarda desfaz-se sozinha. Ela mede o
    comportamento, e nao a correcao: se alguem voltar a por um endereco fixo,
    isto passa a dizer `NAO_DETECTA` outra vez.

        UMA CURA SEM MEDICAO AO LADO E UMA CURA ATE ALGUEM MEXER.


    `retorno.ENVELOPE` e uma constante da receita — um caminho por executor, e
    nao por corrida. Duas corridas do mesmo executor escrevem no mesmo sitio.

    Medido aqui: pergunta-se a colheita em nome de uma corrida que nao existe,
    e o orquestrador devolve a colheita da ULTIMA corrida que escreveu — sem
    nota, sem recusa.

        UM ENVELOPE POR EXECUTOR NAO E UM ENVELOPE POR CORRIDA.

    NAO E DEFEITO DESTA MISSAO e nao se conserta aqui: e propriedade do
    contrato partilhado, e o adapter italiano tem-na exactamente igual.
    Corrigi-la e mudar a convencao de TODOS os executores — trabalho
    deliberado, e nao efeito secundario de uma missao de aquisicao.

    Em serie nao morde: cada corrida escreve, o orquestrador le a seguir. Morde
    quando duas corridas do mesmo executor se cruzarem no tempo — que e
    exactamente o que a coleta grande vai fazer.
    """
    import orquestrador as orq_
    from receitas import EXECUTORES as EX_
    e = (EX_.get("T4") or [{}])[0]
    try:
        env, _n = orq_.o_envelope(e, "CORRIDA-QUE-NAO-EXISTE")
        itens, notas = orq_.a_colheita(e, "CORRIDA-QUE-NAO-EXISTE")
    except Exception as ex:                                  # noqa: BLE001
        ACHADOS.append(("ENVELOPE_PARTILHADO", "NAO_MEDIDO", str(ex)[:120]))
        return
    detectou = bool(notas) or not itens
    ACHADOS.append((
        "ENVELOPE_PARTILHADO",
        "DETECTA" if detectou else "NAO_DETECTA",
        "perguntei pela colheita de `CORRIDA-QUE-NAO-EXISTE` e recebi %d "
        "item(ns) de `%s`%s" % (len(itens), env.get("RUN_ID"),
                                "" if detectou else " — sem nota nenhuma")))


if __name__ == "__main__":
    raise SystemExit(main())
