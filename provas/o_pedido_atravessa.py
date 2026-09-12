#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""UM PEDIDO ATRAVESSA — e ate onde a MESMA historia chega.

    BANCO_DESCARTAVEL_URL=postgresql://postgres@127.0.0.1:5433/descartavel \\
    ITALY_OPS_ROOT=/tmp/ops SALA_DESCARTAVEL=/tmp/sala \\
        python3 provas/o_pedido_atravessa.py

A PERGUNTA, E E UMA SO
----------------------
    UM PEDIDO CANONICO ATRAVESSA HOJE A MAQUINA REAL, DESDE `REQUEST`
    ATE `READY` / SALA DE ESPERA, NUMA MESMA HISTORIA RASTREAVEL?

O QUE ESTA PROVA NAO FAZ, E E O QUE A TORNA DIFERENTE
------------------------------------------------------
Ela NAO chama `atravessar()`, nem `admitir()`, nem `pronto_para_inteligencia()`,
nem `sala_de_espera.pousar()`. Nao abre `collection_run` a mao. Nao fabrica
`raw_asset`.

    UMA PROVA QUE COMECA PELO MEIO NAO PROVA A ESTRADA:
    PROVA O PEDACO POR ONDE ELA COMECOU.

Ela aperta o botao no unico ponto de entrada canonico — `orquestrador.correr()`
com um `Pedido` — e depois pergunta ao banco e ao disco o que aquela corrida
deixou. O executor e o REAL, a ir a fonte REAL. Um executor de mentira provaria
o orquestrador, e nao a aquisicao:

    FAKE EXECUTOR != CANONICAL E2E PROVEN.

O QUE ELA ISOLA
---------------
O livro append-only e o armazem do coletor ficam num `ITALY_OPS_ROOT`
descartavel, e a Sala de Espera numa morada descartavel. Uma medicao que suja
a arvore e uma medicao que a proxima vai medir.
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

import admissao                                     # noqa: E402
import coleta_checkpoint as cc                      # noqa: E402
import sala_de_espera as espera                     # noqa: E402
import social_persistencia as sp                    # noqa: E402
from pedido import Pedido                           # noqa: E402

# A ordem canonica, e ela nao se reordena para o resultado ficar bonito.
ESTRADA = ("REQUEST", "ORCHESTRATOR", "EXECUTOR", "RUN", "RAW",
           "STORAGE", "DERIVED", "STRUCTURED", "ADMISSION", "READY",
           "WAITING_ROOM")
_SO_VERIFICA = ("008",)

fora = []
visto = {}


def caso(nome, condicao, detalhe=""):
    fora.append((nome, bool(condicao), detalhe))


def etapa(nome, observada, evidencia):
    visto[nome] = {"OBSERVED": bool(observada), "EVIDENCE": evidencia}


def cadeia_de_migrations():
    pasta = os.path.join(RAIZ, "supabase", "migrations")
    return [f.split("_", 1)[0] for f in sorted(os.listdir(pasta))
            if f.endswith(".sql") and f.split("_", 1)[0] not in _SO_VERIFICA]


def aplicar_migrations(url):
    pasta = os.path.join(RAIZ, "supabase", "migrations")
    for n in cadeia_de_migrations():
        a = [f for f in sorted(os.listdir(pasta)) if f.startswith(n + "_")]
        r = subprocess.run(["psql", url, "-v", "ON_ERROR_STOP=1", "-q", "-f",
                            os.path.join(pasta, a[0])],
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
    ops = os.environ.get("ITALY_OPS_ROOT")
    sala = os.environ.get("SALA_DESCARTAVEL")
    if not url or not ops or not sala:
        print("FALTA AMBIENTE DESCARTAVEL — e SKIP != PASS.")
        print("  BANCO_DESCARTAVEL_URL · ITALY_OPS_ROOT · SALA_DESCARTAVEL")
        print("PEDIDO_ATRAVESSA=NOT_MEASURED")
        return 2
    espera.MORADA = sala

    print("=" * 70)
    print("UM PEDIDO ATRAVESSA — %d migrations · ambiente descartavel"
          % len(cadeia_de_migrations()))
    aplicar_migrations(url)
    sql = cc.Banco(url)

    # ⚠️ A SALA TEM DE ESTAR VAZIA ANTES DE COMECAR.
    # Um ficheiro que ja la estivesse provaria a corrida de ONTEM.
    antes_na_sala = sorted(os.listdir(sala)) if os.path.isdir(sala) else []
    caso("P0_a_sala_comeca_VAZIA", not antes_na_sala,
         "ficheiros na sala antes de apertar o botao: %s"
         % (antes_na_sala or "nenhum"))

    # ── O BOTAO, NO UNICO PONTO DE ENTRADA CANONICO ─────────────────────
    import orquestrador as orq
    p = Pedido(alvo="T2", filtros={"pais": "IT", "fonte": "IT-T2-002"})
    recibo = orq.correr(p, memoria=_memoria(url), banco_do_rastro=sql)
    recibo.pop("_plano", None)

    # ── REQUEST ─────────────────────────────────────────────────────────
    pedido_no_recibo = recibo.get("PEDIDO") or {}
    etapa("REQUEST", pedido_no_recibo.get("alvo") == "T2",
          "recibo.PEDIDO = %s" % json.dumps(pedido_no_recibo,
                                            ensure_ascii=False))
    caso("R1_o_PEDIDO_entrou_e_ficou_escrito_no_recibo",
         pedido_no_recibo.get("alvo") == "T2"
         and pedido_no_recibo.get("filtros", {}).get("fonte") == "IT-T2-002",
         p.em_uma_frase())

    # ── ORCHESTRATOR ────────────────────────────────────────────────────
    etapa("ORCHESTRATOR", bool(recibo.get("ACTOR")),
          "receita resolvida: ACTOR=%s · PLATFORM=%s · CAPTURE_METHOD=%s"
          % (recibo.get("ACTOR"), recibo.get("PLATFORM"),
             recibo.get("CAPTURE_METHOD")))
    caso("R2_o_ORQUESTRADOR_escolheu_a_receita_e_cunhou_a_corrida",
         recibo.get("ACTOR") == "coleta/italy_executor.py"
         and bool(recibo.get("RUN_ID")),
         "%s -> %s" % (recibo.get("ACTOR"), recibo.get("RUN_ID")))

    # ── EXECUTOR ────────────────────────────────────────────────────────
    # ⚠️ CAN DO != DID DO. Um modulo importavel nao e um executor que correu.
    # O que prova a execucao e o COMANDO que foi lancado, a versao do
    # executor (o commit que lhe tocou) e a colheita que ele largou.
    correu = (recibo.get("STATUS") == "SUCCESS"
              and "italy_executor.py" in (recibo.get("COMANDO") or "")
              and (recibo.get("COLHEITA_ENCONTRADA") or 0) > 0)
    etapa("EXECUTOR", correu,
          "COMANDO=%s · versao=%s · colheita=%s"
          % (recibo.get("COMANDO"), recibo.get("ACTOR_VERSION"),
             recibo.get("COLHEITA_ENCONTRADA")))
    caso("R3_o_EXECUTOR_REAL_correu_e_trouxe_da_fonte_REAL", correu,
         "%s itens · %s" % (recibo.get("COLHEITA_ENCONTRADA"),
                            (recibo.get("RETORNO") or {}).get("ESTADO")))
    caso("R3b_e_nao_foi_um_ensaio_seco",
         "(ensaio seco" not in (recibo.get("SAIDA") or "")
         and "(nao se colheu" not in (recibo.get("SAIDA") or ""),
         "o executor foi mesmo chamado")

    # ── RUN ─────────────────────────────────────────────────────────────
    run_id = recibo.get("RUN_ID")
    corridas = sql.executa(
        "select run_id, status::text, source_country::text, actor"
        " from public.collection_run where run_id = '%s'" % run_id)
    etapa("RUN", bool(corridas),
          "collection_run: %s" % (corridas[0] if corridas else "nenhuma"))
    caso("R4_a_RUN_existe_no_banco_e_e_a_MESMA_do_recibo",
         len(corridas) == 1 and corridas[0][0] == run_id,
         "RUN_ID=%s · status=%s" % (run_id,
                                    corridas[0][1] if corridas else "-"))

    # ── RAW e STORAGE ───────────────────────────────────────────────────
    brutos = sql.executa(
        "select id, coalesce(source_id,'<NULL>'), storage_object_id, sha256"
        " from public.raw_asset where run_id = '%s' order by id" % run_id)
    etapa("RAW", bool(brutos),
          "raw_asset da corrida: %s" % [int(x[0]) for x in brutos])
    caso("R5_o_RAW_aterrou_e_e_da_MESMA_corrida", len(brutos) > 0,
         "%d observacoes · ids %s"
         % (len(brutos), [int(x[0]) for x in brutos]))
    caso("R5b_e_a_fonte_NAO_foi_inferida_do_caminho",
         all(x[1] == "IT-T2-002" for x in brutos),
         "source_id declarado pelo coletor: %s"
         % sorted({x[1] for x in brutos}))
    objetos = sql.executa(
        "select count(*) from public.storage_object o join public.raw_asset r"
        " on r.storage_object_id = o.id where r.run_id = '%s'" % run_id)
    etapa("STORAGE", int(objetos[0][0]) > 0,
          "storage_object ligados a esta corrida: %s" % objetos[0][0])
    caso("R6_o_OBJETO_guardado_existe_e_esta_ligado_a_observacao",
         int(objetos[0][0]) == len(brutos),
         "%s objetos para %d observacoes" % (objetos[0][0], len(brutos)))

    # ── E A CORRIDA DEIXOU RASTO? ───────────────────────────────────────
    passagens = sql.executa(
        "select etapa::text, estado::text, passed from public.etapa_da_corrida"
        " where run_id = '%s' order by id" % run_id)
    caso("R7_a_corrida_canonica_deixou_RASTO",
         bool(passagens),
         "passagens: %s" % ([x[0] for x in passagens] or "NENHUMA"))

    # ── DERIVED · STRUCTURED · ADMISSION · READY ────────────────────────
    derivados = sql.executa(
        "select count(*) from public.derived_artifact d join public.raw_asset r"
        " on d.raw_asset_id = r.id where r.run_id = '%s'" % run_id)
    etapa("DERIVED", int(derivados[0][0]) > 0,
          "derived_artifact desta corrida: %s" % derivados[0][0])
    conteudos = sql.executa(
        "select count(*) from public.conteudo where run_id = '%s'" % run_id)
    etapa("STRUCTURED", int(conteudos[0][0]) > 0,
          "conteudo desta corrida: %s" % conteudos[0][0])
    adm = recibo.get("ADMISSAO") or {}
    etapa("ADMISSION", bool(adm.get("itens")),
          "a porta julgou %s itens: %s"
          % (adm.get("itens"), adm.get("por_resultado")))
    etapa("READY", bool(adm.get("prontos")),
          "unidades prontas: %s" % adm.get("prontos"))
    depois_na_sala = sorted(os.listdir(sala)) if os.path.isdir(sala) else []
    etapa("WAITING_ROOM", bool(depois_na_sala),
          "ficheiros na sala DEPOIS: %s" % (depois_na_sala or "nenhum"))

    # ── A MESMA HISTORIA, OU HISTORIAS DIFERENTES? ──────────────────────
    outras = sql.executa(
        "select count(distinct run_id) from public.raw_asset")
    caso("R8_tudo_o_que_aterrou_pertence_a_UMA_corrida_so",
         int(outras[0][0]) == 1,
         "corridas distintas em raw_asset: %s" % outras[0][0])
    caso("R9_e_a_sala_so_tem_o_que_ESTA_execucao_produziu",
         set(depois_na_sala) - set(antes_na_sala) == set(depois_na_sala),
         "antes=%s · depois=%s" % (antes_na_sala or "-",
                                   depois_na_sala or "-"))

    # ── O PRIMEIRO EDGE PERDIDO ─────────────────────────────────────────
    # ⚠️ O PRIMEIRO EDGE PERDIDO E O PRIMEIRO, E NAO O ULTIMO BURACO.
    # A primeira versao disto guardava a ultima etapa observada da lista
    # INTEIRA — e como a ADMISSION corre depois de DERIVED faltar, ela dizia
    # `ADMISSION -> DERIVED`. Uma aresta ao contrario, que faria procurar o
    # defeito a jusante de onde ele esta.
    #
    #     O PRIMEIRO BURACO E O QUE EXPLICA OS SEGUINTES.
    #     OS QUE VEM DEPOIS PODEM SER SO O ECO DELE.
    #
    # A ultima provada e a que vem IMEDIATAMENTE ANTES do primeiro buraco.
    perdido, ultima = None, None
    for e in ESTRADA:
        if perdido is None:
            if visto.get(e, {}).get("OBSERVED"):
                ultima = e
            else:
                perdido = e
    inteira = perdido is None
    # E as etapas que correram DEPOIS do buraco ficam ditas, para ninguem as
    # ler como se a estrada estivesse inteira.
    depois_do_buraco = [e for e in ESTRADA
                        if perdido and ESTRADA.index(e) > ESTRADA.index(perdido)
                        and visto.get(e, {}).get("OBSERVED")]
    caso("R10_a_estrada_inteira_foi_atravessada_pelo_MESMO_pedido", inteira,
         "primeiro edge perdido: %s -> %s" % (ultima, perdido)
         if perdido else "REQUEST -> SALA DE ESPERA")

    # ═══════════════════════════════════════════════════════════════════
    # A CAUSA DO BURACO — medida, e nao afirmada
    # ═══════════════════════════════════════════════════════════════════
    # Duas perguntas diferentes, e as respostas classificam o gap:
    #   · o DERIVED nao corre porque NAO SABE, ou porque NINGUEM O CHAMA?
    #   · e o STRUCTURED, logo a seguir, o que e que lhe falta?
    import derivacao_forward as fwd
    from guarda.preservar_coleta import ArmazemDeMentira
    import glob
    pdfs = sorted(glob.glob(os.path.join(
        ops, "data", "collection-store", "italy", "**", "*.pdf"),
        recursive=True))
    alcancavel, porque_d = False, "nao havia bruto desta corrida para tentar"
    if brutos and pdfs:
        r_d = fwd.correr([{"RAW_ASSET_ID": int(brutos[0][0]), "PDF": pdfs[0]}],
                         banco_do_rastro=sql, run_id=run_id,
                         armazem=ArmazemDeMentira(), memoria=_memoria(url),
                         source_id="IT-T2-002")
        alcancavel = r_d.get("ESTADO_DA_ETAPA") == "PASS"
        porque_d = "%s · %s" % (r_d.get("ESTADO_DA_ETAPA"),
                                {k: v for k, v in r_d["BALDES"].items() if v})
    caso("D1_o_DERIVED_E_alcancavel_a_partir_deste_MESMO_bruto", alcancavel,
         "%s — logo o buraco e de LIGACAO, e nao de capacidade" % porque_d)

    # ⚠️ E A ETAPA SEGUINTE NAO E DA MESMA ESPECIE DE BURACO.
    # `public.conteudo` exige `canal_id`, e `social_persistencia.exigir_canal`
    # recusa quando ele nao existe — dizendo, por escrito, que quem o resolve
    # e «um dono de identidade, fora do executor de coleta». Esse dono NAO
    # existe. Isso nao e uma chamada em falta: e um contrato sem dono.
    cid, recusa = sp.exigir_canal(sql, platform="web", channel_id="IT-T2-002")
    caso("D2_o_STRUCTURED_para_por_FALTA_DE_DONO_e_nao_por_falta_de_chamada",
         cid is None and recusa is not None
         and "fora do executor de coleta" in (recusa.get("QUEM_RESOLVE") or ""),
         (recusa or {}).get("QUEM_RESOLVE", "o canal resolveu-se sozinho?"))

    # ═══════════════════════════════════════════════════════════════════
    # OS NEGATIVOS — a maquina tambem tem de falhar direito
    # ═══════════════════════════════════════════════════════════════════
    from pedido import PedidoInvalido
    recusou = False
    try:
        Pedido(alvo="T2", acionamento="AUTOMATICO_EVENTO")
    except PedidoInvalido:
        recusou = True
    caso("N1_um_pedido_que_a_casa_nao_sabe_cumprir_NAO_entra", recusou,
         "AUTOMATICO_EVENTO e recusado no contrato do pedido")

    sem_caminho = orq.correr(Pedido(alvo="T4", filtros={"pais": "ZZ"}),
                             so_plano=True)
    caso("N2_um_pedido_sem_caminho_nao_cunha_corrida_operacional",
         sem_caminho.get("STATUS") in ("PLANO", "SEM_CAMINHO")
         and not sql.executa(
             "select 1 from public.collection_run where run_id = '%s'"
             % sem_caminho.get("RUN_ID")),
         "STATUS=%s · nenhuma linha em collection_run"
         % sem_caminho.get("STATUS"))

    caso("N3_a_ADMISSION_negativa_nao_produziu_unidade_nem_ficheiro",
         (adm.get("prontos") or 0) == 0 and not depois_na_sala,
         "por_resultado=%s · sala=%s"
         % (adm.get("por_resultado"), depois_na_sala or "vazia"))

    caso("N4_o_SOURCE_ID_nao_saiu_do_caminho_nem_do_sha",
         all(x[1] == "IT-T2-002" and x[1] not in (x[3] or "")
             for x in brutos),
         "a fonte veio declarada pelo coletor, e nao do endereco")

    print("=" * 70)
    print("  A ESTRADA, ETAPA A ETAPA")
    for e in ESTRADA:
        v = visto.get(e, {"OBSERVED": False, "EVIDENCE": "nao medida"})
        print("    %-13s %-4s %s" % (e, "SIM" if v["OBSERVED"] else "NAO",
                                     str(v["EVIDENCE"])[:88]))
    print()
    for nome, ok, detalhe in fora:
        print("  %-4s %-52s %s" % ("PASS" if ok else "FALHA", nome, detalhe))
    print("=" * 70)
    print("CANONICAL_E2E=%s" % ("PASS" if inteira else "FAIL"))
    if not inteira:
        print("  LAST_PROVEN_STAGE   = %s" % ultima)
        print("  NEXT_EXPECTED_STAGE = %s" % perdido)
        print("  FIRST_LOST_EDGE     = %s -> %s" % (ultima, perdido))
        if depois_do_buraco:
            print("  ETAPAS QUE CORRERAM DEPOIS DO BURACO: %s"
                  % ", ".join(depois_do_buraco))
            print("  (correram, e nao provam a estrada: a historia ja estava"
                  " partida antes delas)")
    print("  SAME_STORY=%s · uma corrida so em raw_asset" % (
        "YES" if int(outras[0][0]) == 1 else "NO"))
    json.dump({"RUN_ID": run_id, "ESTRADA": visto,
               "FIRST_LOST_EDGE": (None if inteira
                                   else "%s -> %s" % (ultima, perdido)),
               "ETAPAS_DEPOIS_DO_BURACO": depois_do_buraco,
               "CANONICAL_E2E": "PASS" if inteira else "FAIL"},
              io.open(os.path.join(RAIZ, "system-map", "data",
                                   "pedido.observado.json"), "w",
                      encoding="utf-8"),
              ensure_ascii=False, indent=2)
    # ⚠️ O VEREDITO DA PROVA E «MEDI SEM AMBIGUIDADE», e nao «a estrada
    # esta inteira». Uma prova que so passa quando o mundo esta bom nao
    # serve para medir um mundo que ainda nao esta.
    medido = all(ok for n, ok, _d in fora
                 if n != "R10_a_estrada_inteira_foi_atravessada_pelo_MESMO_pedido")
    print("PEDIDO_ATRAVESSA=%s" % ("MEDIDO" if medido else "MEDICAO_FALHOU"))
    return 0 if medido else 1


if __name__ == "__main__":
    raise SystemExit(main())
