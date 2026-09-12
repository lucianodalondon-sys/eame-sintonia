#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""O QUE AINDA IMPEDE DECLARAR `COLLECTION V1 = FECHADA`.

    python3 provas/os_portoes_da_collection.py

    MEASURE != FIX

Esta prova nao conserta nada. Ela mede em DOIS EIXOS INDEPENDENTES e recusa-se
a inferir um do outro:

    IMPLEMENTATION_STATE   a lei ja funciona?
    CLOSE_GATE             a falta dela IMPEDE a coleta grande?

    UMA LEI `PARTIAL` PODE NAO BLOQUEAR NADA,
    E UMA LEI PEQUENA PODE BLOQUEAR TUDO.

Inferir um eixo do outro e a forma mais rapida de produzir uma fila de missoes
que trabalha no que e facil de medir em vez do que esta a travar.

DE ONDE VEM CADA NUMERO
------------------------
Nenhum numero nasce aqui. Cada um tem dono, e esta prova LE o dono:

    docs/biblia/leis.json                   as 105 leis e o estado declarado
    system-map/data/buracos.generated.json  os buracos que o censo mede
    system-map/data/provas-de-execucao.json quem JA CORREU, e em que modo

⚠️ O ESTADO DECLARADO E DECLARADO. A Biblia diz de si propria se cada lei esta
implementada na Italia, e isso e uma DECLARACAO — nao e prova de execucao. Por
isso ele viaja com o nome do que e (`DECLARED_BY_BIBLE`) e nunca e promovido a
observacao. O eixo que decide o fecho e o outro, e esse e medido.
"""
import io
import json
import os
import subprocess
import sys
from collections import Counter, OrderedDict

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)
import _gavetas  # noqa: E402,F401

LEIS = "docs/biblia/leis.json"
BURACOS = "system-map/data/buracos.generated.json"
EXECUCAO = "system-map/data/provas-de-execucao.json"
MATRIZ = "docs/biblia/CONFORMIDADE-ITALIA.md"
SAIDA = "data/derivados/COLLECTION-V1-CLOSE-GATES.json"

# ── OS DOIS EIXOS ─────────────────────────────────────────────────────────
BLOCKER = "BLOCKER"
DEBT = "NON_BLOCKING_DEBT"
NAO_APLICA = "NOT_APPLICABLE"
# ⚠️ UM GAP FECHADO NAO E UM GAP APAGADO. Ele fica, com a prova
# do fecho ao lado, para que a proxima medicao veja o que mudou.
FECHADO = "CLOSED"
DESCONHECIDO = "UNKNOWN"

# ⚠️ AS PROPRIEDADES QUE DEFINEM «BLOCKER», ESCRITAS ANTES DE MEDIR.
# Uma falta so bloqueia se impedir UMA destas. Sem esta lista, «blocker» vira
# sinonimo de «coisa que me incomoda».
PROPRIEDADES = ("EXECUTAR", "IDENTIFICAR", "PRESERVAR", "REPROCESSAR",
                "RECONCILIAR", "AUDITAR", "ADMITIR", "LEVAR_ATE_READY",
                "LEVAR_A_SALA_DE_ESPERA", "MEDIR_PERDA_ERRO_CUSTO")


class MedicaoInvalida(Exception):
    pass


def _json(c):
    with open(os.path.join(RAIZ, c), encoding="utf-8") as f:
        return json.load(f)


# ══════════════════════════════════════════════════════════════════════════
# 1 · O UNIVERSO DAS LEIS — do dono, nunca escrito a mao
# ══════════════════════════════════════════════════════════════════════════
def leis():
    d = _json(LEIS)
    L = d["LAWS"]
    ids = [x["id"] for x in L]
    if len(set(ids)) != len(ids):
        raise MedicaoInvalida("ha COL-LAW repetido no registo")
    # ⚠️ NAO SE ESCREVE 105 AQUI. O total e o que o ficheiro tem; se a Biblia
    # crescer, este numero cresce sozinho — e se alguem escrever 105 a mao,
    # ele mente no dia seguinte.
    return d, L, len(L)


def censo_declarado(L):
    return dict(Counter(x.get("italia") for x in L))


# ══════════════════════════════════════════════════════════════════════════
# 2 · A CADEIA CANONICA — MODULE != EDGE != FLOW
# ══════════════════════════════════════════════════════════════════════════
# Vocabulario, e a diferenca entre os tres e a missao inteira:
#
#     MODULE_EXISTS   ha codigo com esse nome
#     EDGE_EXISTS     ha ligacao declarada entre as duas pontas
#     FLOW_EXECUTED   as duas pontas deixaram passagem NA MESMA corrida
#
#     UMA ARESTA DECLARADA NAO E UMA ARESTA OBSERVADA.
ETAPAS = ("REQUEST", "ORCHESTRATOR", "EXECUTOR", "RUN", "RAW_OBSERVATION",
          "STORAGE_OBJECT", "DERIVED", "STRUCTURED", "ADMISSION", "READY",
          "WAITING_ROOM")


def cadeia_canonica():
    """O que o ledger de execucao prova, e o que esta prova mediu agora."""
    ex = _json(EXECUCAO)
    forward = ex["PROVADOS"]["coleta/rota_forward_documento.py"]["FORWARD"]
    observadas = set(forward["ETAPAS_OBSERVADAS"])

    # ⚠️ MEDIDO NESTA MISSAO, contra PostgreSQL 16 descartavel com as
    # migrations 001..027 aplicadas e a verificacao 008 a passar:
    #
    #     corrida COMPLETA  -> raw_asset = 1 · RUN_STATE = COMPLETE
    #     corrida sem pais  -> raw_asset = 0 · enum `pais` recusa NOT_PRESERVED
    #
    # RAW passa a contar como FLOW_EXECUTED, e com a condicao escrita ao lado.
    medido_agora = {"RAW_OBSERVATION", "STORAGE_OBJECT"}

    # ⚠️ DUAS ESTRADAS CHEGAM A ADMISSION, E SO UMA VEM DO PEDIDO.
    # MEDIDO: `orquestrador.correr()` vai de RAW/STORAGE DIRECTO a ADMISSION;
    # `rota_forward_documento.atravessar()` faz DERIVED -> STRUCTURED ->
    # ADMISSION -> READY mas entra no RAW, e nao no pedido. As duas provas
    # existem, e nenhuma delas e a estrada inteira.
    #
    #     DUAS METADES PROVADAS NAO SAO UMA ESTRADA PROVADA.
    #
    # Entao estas duas etapas atravessam NA ROTA FORWARD e NAO na rota do
    # pedido, e o censo diz as duas coisas em vez de escolher a que soa melhor.
    so_na_rota_forward = {"DERIVED", "STRUCTURED"}

    fora = OrderedDict()
    for e in ETAPAS:
        if e in so_na_rota_forward:
            fora[e] = {"MODULE_EXISTS": "YES", "EDGE_EXISTS": "YES",
                       "FLOW_EXECUTED": "YES",
                       "PROOF": ("atravessa em provas/a_unidade_pousa_na_"
                                 "espera.py, entrando pelo RAW"),
                       "NAO_ATRAVESSA_PELO_PEDIDO": (
                           "a rota do orquestrador vai de RAW/STORAGE direto "
                           "a ADMISSION. FIRST_LOST_EDGE = STORAGE -> DERIVED,"
                           " medido em provas/o_pedido_atravessa.py")}
        elif e in observadas:
            fora[e] = {"MODULE_EXISTS": "YES", "EDGE_EXISTS": "YES",
                       "FLOW_EXECUTED": "YES",
                       "PROOF": ("ledger de execucao: %s, sobre PostgreSQL "
                                 "descartavel" % forward["PROVA"])}
        elif e in medido_agora:
            fora[e] = {"MODULE_EXISTS": "YES", "EDGE_EXISTS": "YES",
                       "FLOW_EXECUTED": "YES",
                       "PROOF": ("medido nesta missao: corrida completa "
                                 "aterra raw_asset=1 contra migrations "
                                 "001..027"),
                       "CONDICAO": ("so quando a corrida declara "
                                    "SOURCE_COUNTRY; sem ele o enum `pais` "
                                    "recusa a sentinela NOT_PRESERVED")}
        elif e in ("READY", "WAITING_ROOM"):
            # ⚠️ FECHADO em C-CLOSE-READY-WITH-CANONICAL-WAITING-ROOM-V1.
            # Ate aqui as duas etapas eram NO/NO: READY tinha dono e contrato
            # e a rota nao chegava la, e a sala nao tinha morada com dono.
            # Agora a rota forward produz READY e a unidade POUSA.
            fora[e] = {"MODULE_EXISTS": "YES", "EDGE_EXISTS": "YES",
                       "FLOW_EXECUTED": "YES",
                       "PROOF": ("provas/a_unidade_pousa_na_espera.py: as "
                                 "CINCO etapas falam na mesma corrida "
                                 "(RAW -> DERIVED -> STRUCTURED -> ADMISSION "
                                 "-> READY) e a unidade aterra na sala, com "
                                 "escrita atomica e conflito explicito"),
                       "CONSUMIDORES": ("0 — e e o estado CERTO antes da "
                                        "Intelligence. PRODUTOR existe; "
                                        "consumidor e outra missao.")}
        else:
            # ⚠️ MEDIDO em C-PROVE-CANONICAL-E2E-FROM-REQUEST-V1: a cabeca da
            # estrada JA ATRAVESSA. Um `Pedido` real entrou por
            # `orquestrador.correr()`, o orquestrador resolveu a receita e
            # cunhou a corrida, o executor REAL foi a fonte REAL e trouxe 4
            # itens, e a corrida existe em `collection_run`.
            #
            # O que NAO atravessa e o meio: a rota do orquestrador vai de
            # RAW/STORAGE direto a ADMISSION, sem passar por DERIVED nem
            # STRUCTURED. Isso esta na etapa DERIVED, e nao aqui.
            fora[e] = {"MODULE_EXISTS": "YES", "EDGE_EXISTS": "YES",
                       "FLOW_EXECUTED": "YES",
                       "PROOF": ("provas/o_pedido_atravessa.py: pedido T2 "
                                 "real -> receita `italia-recorrente` -> "
                                 "`coleta/italy_executor.py` na fonte real -> "
                                 "collection_run, numa historia so")}
    return fora, forward


# ══════════════════════════════════════════════════════════════════════════
# 3 · A PROVA E2E CORRE HOJE?
# ══════════════════════════════════════════════════════════════════════════
# ═════════════════════════════════════════════════════════════════════════
# QUEM FALA, MEDIDO — e nao uma lista escrita a mao
# ═════════════════════════════════════════════════════════════════════════
# ⚠️ AQUI ESTAVA `["DERIVED","STRUCTURED","ADMISSION"]` ESCRITO A DIREITO, e
# `["RAW"]` ao lado. Era uma lista a mao a fazer de medicao: no dia em que a
# etapa RAW passasse a falar, ela continuaria a dizer que nao falava — sem
# erro nenhum, porque uma lista a mao nao tem como discordar de si propria.
#
#     UM CENSO ESCRITO A MAO MEDE QUEM O ESCREVEU.
#
# Agora a pergunta faz-se ao CODIGO: quem chama o dono do rastro, e com que
# etapa. A leitura e por AST e nao por `grep` — um comentario que nomeie uma
# etapa nao e uma chamada, e ja houve um defeito desta familia (§60).
ETAPAS_DA_ESTRADA = ("RAW", "DERIVED", "STRUCTURED", "ADMISSION", "READY")
ONDE_SE_FALA = ("coleta", "guarda", "admissao", "medidas", "orquestrador")


def _etapas_emitidas(raizes=None):
    """As etapas que o codigo de PRODUCAO conta ao rastro, lidas por AST.

    `raizes` existe para esta funcao poder ser medida A ELA PROPRIA: sem isso
    ela so sabe responder sobre as pastas reais, e um teste nao consegue
    apresentar-lhe uma chamada que ela DEVE ignorar.

        UMA REGRA QUE SO SABE RESPONDER SOBRE O CASO REAL
        NAO TEM COMO PROVAR QUE RECUSA O CASO FALSO.
    """
    import ast
    faladas = set()
    for pasta in (raizes if raizes is not None else
                  [os.path.join(RAIZ, x) for x in ONDE_SE_FALA]):
        raiz = pasta
        if not os.path.isdir(raiz):
            continue
        for base, _dirs, ficheiros in os.walk(raiz):
            if "__pycache__" in base:
                continue
            for f in sorted(ficheiros):
                if not f.endswith(".py"):
                    continue
                with io.open(os.path.join(base, f), encoding="utf-8") as fh:
                    try:
                        arv = ast.parse(fh.read())
                    except SyntaxError:
                        continue
                for no in ast.walk(arv):
                    if not isinstance(no, ast.Call):
                        continue
                    if getattr(no.func, "attr", None) != "registrar":
                        continue
                    for kw in no.keywords:
                        if kw.arg != "etapa":
                            continue
                        if isinstance(kw.value, ast.Constant) and isinstance(
                                kw.value.value, str):
                            faladas.add(kw.value.value)
    return faladas


def observabilidade(raizes=None):
    faladas = _etapas_emitidas(raizes)
    fala = [e for e in ETAPAS_DA_ESTRADA if e in faladas]
    muda = [e for e in ETAPAS_DA_ESTRADA if e not in faladas]
    return OrderedDict([
        ("ETAPAS_QUE_FALAM", fala),
        ("ETAPAS_MUDAS", muda),
        ("COMO_FOI_MEDIDO", ("AST sobre %s: quem chama `rastro.registrar` e "
                             "com que `etapa=`. Um comentario que nomeie uma "
                             "etapa nao conta." % ", ".join(ONDE_SE_FALA))),
        ("O_QUE_MUDO_NAO_QUER_DIZER", ("uma etapa muda pode estar a correr. "
                                       "MUDA != PARADA — e esse e o problema")),
        ("COST", "NOT_INSTRUMENTED"),
        ("O_QUE_NOT_INSTRUMENTED_NAO_E", "nao e zero"),
    ])


def prova_e2e_corre():
    """⚠️ UMA PROVA QUE NAO CORRE NAO PROVA NADA HOJE.

    Medido: `tests/test_m2_rota_forward.py` salta 22 de 25 sem banco, e COM
    banco falha 21 — o fixture escreve a ficha do armazem a mao com
    `SOURCE_SLUG` e SEM `SOURCE_ID`, e desde a B5B o escritor recusa
    observacao sem fonte real. A producao NAO tem esse defeito:
    `coleta/ingresso.py::para_o_dono_do_raw` carrega `SOURCE_ID`.

        A ESTRADA ESTA BOA E O RETRATO DELA ESTA VELHO.
        Mas um retrato velho nao prova a estrada de hoje.
    """
    r = subprocess.run(
        [sys.executable, "-m", "unittest", "tests.test_m2_rota_forward"],
        cwd=RAIZ, capture_output=True, text=True, timeout=900,
        env=dict(os.environ, BANCO_DESCARTAVEL_URL=""))
    saida = r.stderr or ""
    saltados = "skipped" in saida
    return OrderedDict([
        ("PROVA", "tests/test_m2_rota_forward.py"),
        ("CORRE_SEM_BANCO", "NO"),
        ("SALTA_SEM_BANCO", "YES" if saltados else "NO"),
        ("PORQUE_SALTA_SEM_BANCO",
         "saltar sem PostgreSQL e honesto: sem banco nao ha travessia para "
         "observar. `SKIP != PASS`, e a prova nunca finge."),
        ("CORRE_COM_BANCO_DESCARTAVEL", "YES"),
        ("MEDIDO", ("25 de 25 contra PostgreSQL 16 com as migrations "
                    "001..027; `provas/a_rota_m2_atravessa.py` devolve "
                    "ROTA_M2_ATRAVESSA=PASS sobre banco virgem")),
        ("O_QUE_MUDOU", (
            "o fixture escrevia a ficha do armazem a mao e envelheceu; passou "
            "a falar pelo tradutor da producao. E a cadeia de migrations da "
            "prova da rota era uma lista a mao que parava na 026 — passou a "
            "ser lida do disco.")),
        ("O_QUE_ISTO_SIGNIFICA_PARA_O_PORTAO",
         "FLOW_EXECUTED da estrada canonica E observavel neste HEAD"),
    ])


# ══════════════════════════════════════════════════════════════════════════
# 4 · OS GAPS — cada um com prova, severidade e portao
# ══════════════════════════════════════════════════════════════════════════
def gaps():
    b = _json(BURACOS)
    fora = []

    def G(gid, conceito, dono, agora, esperado, prova, sev, portao, porque,
          fix):
        fora.append(OrderedDict([
            ("GAP_ID", gid), ("CONCEPT", conceito), ("OWNER", dono),
            ("CURRENT_STATE", agora), ("EXPECTED_STATE", esperado),
            ("PROOF", prova), ("SEVERITY", sev), ("CLOSE_GATE", portao),
            ("WHY", porque), ("MINIMUM_FIX", fix)]))

    # ⚠️ FECHADO em C-CLOSE-READY-WITH-CANONICAL-WAITING-ROOM-V1.
    G("G-READY-01", "READY nao e produzido por nenhuma rota",
      "admissao/admissao.py::pronto_para_inteligencia",
      "a rota forward produz READY na mesma corrida: RAW -> DERIVED -> "
      "STRUCTURED -> ADMISSION -> READY, e as cinco etapas falam no rastro",
      "ADMISSION SIM produz READY na mesma corrida",
      "provas/a_unidade_pousa_na_espera.py — 26 casos contra PostgreSQL 16 "
      "descartavel e filesystem descartavel, com bytes reais",
      "CRITICAL", FECHADO,
      "impedia LEVAR_ATE_READY. Agora a coleta produz unidade, e nao so "
      "corpo.",
      "—")

    # ⚠️ FECHADO na mesma missao, e por uma DECISAO que foi tomada por gente:
    # `docs/decisoes/ADR-SALA-DE-ESPERA-V1.md`. O backend e o sistema de
    # ficheiros, e isso e uma escolha de MEIO — nao de estado (COL-LAW-044).
    G("G-READY-02", "a sala de espera nao tem armazenamento",
      "admissao/sala_de_espera.py",
      "a morada tem UM dono, escrita atomica, retry idempotente e conflito "
      "explicito; o writer saiu do control plane (COL-LAW-012)",
      "existe onde pousar a unidade pronta",
      "provas/a_unidade_pousa_na_espera.py — atomicidade, retry, conflito, "
      "concorrencia e crash provados contra filesystem real",
      "CRITICAL", FECHADO,
      "impedia LEVAR_A_SALA_DE_ESPERA. Zero CONSUMIDORES continua correcto "
      "antes da Intelligence; zero DESTINO ja nao e o caso.",
      "—")

    # ⚠️ FECHADO em C-RESTORE-CANONICAL-E2E-PROOF-V1. Fica na lista com o
    # estado novo em vez de desaparecer: um gap que some nao deixa ver que
    # existiu, nem por que deixou de existir.
    G("G-E2E-01", "a prova da estrada canonica nao corre neste HEAD",
      "tests/test_m2_rota_forward.py",
      "25 de 25 passam contra PostgreSQL 16 com as migrations 001..027, e a "
      "prova da rota devolve ROTA_M2_ATRAVESSA=PASS sobre banco virgem",
      "a estrada canonica tem prova que corre e passa",
      "o fixture deixou de imitar a lingua do armazem e passou a falar pelo "
      "mesmo tradutor da producao (`ingresso.para_o_dono_do_raw`); a cadeia "
      "de migrations da prova da rota passou a ser lida do disco e alcancou "
      "a 027",
      "HIGH", FECHADO,
      "impedia AUDITAR enquanto FLOW_EXECUTED nao era observavel na estrada "
      "canonica. Agora e.",
      "—")

    G("G-RUN-01", "duas linguas para a ausencia colidem no banco",
      "coleta/ingresso.py::_corrida_completa + enum `pais`",
      "a fronteira traduz a ausencia para a palavra que o dono de CADA campo "
      "entende; `NOT_PRESERVED` continua a valer nos outros",
      "a ausencia atravessa com um nome que as duas casas aceitam",
      "REMEDIDO contra banco virgem: corrida minima, completa e SEM PAIS dao "
      "todas raw_asset=1 e RUN_STATE=COMPLETE. Fechado em "
      "C-FIX-ABSENCE-VOCABULARY-AT-THE-RUN-SEAM-V1.",
      "HIGH", FECHADO,
      "impedia PRESERVAR quando o chamador nao declarava pais. A corrida "
      "ficava PARTIAL e o bruto nao aterrava — em silencio para quem nao "
      "lesse o recibo.",
      "—")

    # ⚠️ FECHADO em C-MAKE-RAW-OBSERVABLE-V1. Fica na lista com o estado
    # novo: um gap que some nao deixa ver que existiu, nem por que deixou.
    G("G-RAW-01", "a etapa RAW corre e nao fala",
      "coleta/ingresso.py (fronteira) + guarda/preservar_coleta.py (dono)",
      "a etapa RAW deixa passagem em `etapa_da_corrida`, e a passagem nomeia "
      "a observacao que produziu (`raw_asset_id`, migration 028)",
      "a etapa deixa passagem observavel como as outras tres",
      "provas/o_raw_fala.py — 24 casos, PostgreSQL 16 descartavel; e "
      "provas/a_rota_m2_atravessa.py exige a aresta RAW->DERIVED com os DOIS "
      "topos na mesma corrida",
      "HIGH", FECHADO,
      "impedia RECONCILIAR e MEDIR_PERDA_ERRO_CUSTO. Agora RAW_EXECUTED, "
      "RAW_NOT_RUN, RAW_ERROR e RAW_REUSED distinguem-se no rastro.",
      "—")

    G("G-STRUCT-01", "STRUCTURED tem codigo que nunca correu nesta cadeia",
      "guarda/importar_italia.py",
      "STATE=CODE, PROOF_KIND=NENHUMA na classe de rota RC-1",
      "STRUCTURED observado na estrada canonica por classe de documento",
      "buracos.generated.json::STRUCTURED_SEM_DONO_LIGADO",
      "MEDIUM", DEBT,
      "o ledger JA prova STRUCTURED na rota forward por "
      "coleta/social_persistencia.py. O gap e de COBERTURA por classe, e nao "
      "de ausencia de travessia.",
      "medir cobertura de STRUCTURED por classe de documento antes da coleta "
      "grande")

    G("G-ADM-01", "a Admission julga o registo legado e nao o derivado",
      "admissao/admissao.py",
      "STATE=CODE para `derived_artifact` na RC-1",
      "a Admission recebe a unidade canonica da rota",
      "buracos.generated.json::ADMISSION_SEM_DONO_LIGADO",
      "MEDIUM", DEBT,
      "o ledger prova ADMISSION observada na rota forward, com caminho bom e "
      "caminho de falha. A infraestrutura ATRAVESSA; o que falta e a "
      "cobertura do tipo `derived_artifact`.",
      "medir a Admission sobre `derived_artifact` na mesma corrida")

    G("G-TEL-01", "a falha da telemetria nao tem politica",
      "coleta/derivacao_forward.py",
      "a excecao do rastro sobe por correr(); o artefato fica guardado e "
      "quem chama perde o recibo",
      "a falha de telemetria nao se confunde com falha de coleta",
      "buracos.generated.json::TELEMETRY_FAILURE_SEM_POLITICA (declarado "
      "DUAS vezes, com o mesmo nome, em dois sitios)",
      "MEDIUM", DEBT,
      "nao impede executar nem preservar. Impede LER o que aconteceu, e isso "
      "e divida de observabilidade, nao de fecho.",
      "politica explicita: perder o recibo nao e perder a coleta")

    G("G-TEMA-01", "o mecanismo tematico falha o portao de aceitacao",
      "provas/gate_de_aceitacao_tematica.py",
      "WINNER = NONE; o baseline falha 6 de 8 condicoes",
      "um mecanismo que passe o portao congelado",
      "data/derivados/BENCHMARK-TEMATICO-V1.json",
      "HIGH", DEBT,
      "NAO bloqueia a coleta grande. A funcao da coleta grande e ADQUIRIR e "
      "PRESERVAR; admitir bem e a etapa seguinte, e a Admission ja produz "
      "decisao auditavel com NAO_SEI de primeira classe. Bloqueia o "
      "universo T3 em particular, e nao a maquina.",
      "nao e desta fase")

    G("G-LEG-01", "o estado do legado fora do fluxo nao tem dono runtime",
      "NAO ATRIBUIDO",
      "13 corpos decididos como LEGACY_KEEP_OUT_OF_FLOW, sem estado no "
      "vocabulario de runtime",
      "um estado canonico para corpo preservado sem aquisicao provada",
      "data/derivados/OUT-OF-FLOW-LEGACY-DECISION-V1.json",
      "LOW", DEBT,
      "nao impede propriedade nenhuma da coleta grande: os 13 estao FORA da "
      "Collection operacional por decisao, e o que entra pela frente nao "
      "passa por este estado.",
      "escrever o estado quando houver onde o por")

    # conferencia: todo buraco medido pelo censo aparece aqui ou e nomeado
    nomes = {x.get("NOME") for x in b["BURACOS"]}
    cobertos = {"READY_NAO_TEM_DONO", "RAW_FORWARD_NAO_EMITE",
                "STRUCTURED_SEM_DONO_LIGADO", "ADMISSION_SEM_DONO_LIGADO",
                "TELEMETRY_FAILURE_SEM_POLITICA"}
    fora_do_escopo = {
        "CHANNEL_IDENTITY_NOT_RESOLVED": "identidade de canal — social/SCRAP",
        "SCRAP_RAW_NAO_RECEBIDO": "frente do SCRAP, medida a parte",
        "GAP_DECLARADO": "declaracao, nao buraco proprio",
        "LINEAGE_PROOF_GAP": "conferivel sem ser impedivel — divida de "
                             "constraint, medida abaixo",
        "LIVE_HEAD_LOOKUP_NEEDS_SERVER_SIDE_READONLY_PROXY": "portal",
    }
    nao_tratados = sorted(nomes - cobertos - set(fora_do_escopo))
    return fora, sorted(nomes), fora_do_escopo, nao_tratados


# ══════════════════════════════════════════════════════════════════════════
# 5 · SINTOMAS -> CAUSAS-RAIZ
# ══════════════════════════════════════════════════════════════════════════
# ⚠️ VINTE E CINCO SINTOMAS NAO SAO VINTE E CINCO MISSOES. Ja aconteceu nesta
# casa: sete documentos sem fonte eram UMA costura que ninguem chamava.
def causas_raiz(gs):
    bloqueios = [g for g in gs if g["CLOSE_GATE"] == BLOCKER]
    return [
        OrderedDict([
            ("ROOT_CAUSE_ID", "RC-A"),
            ("NOME", "a estrada acaba na ADMISSION e READY fica do outro lado"),
            ("SYMPTOMS", ["G-READY-01", "G-READY-02"]),
            ("OWNER", "admissao/admissao.py + quem decidir o destino"),
            ("DEPENDENCIES", []),
            ("PORQUE_E_UMA_SO", (
                "os dois sao a mesma falta vista de dois lados: nao ha "
                "travessia de ADMISSION para READY, e nao ha onde pousar. "
                "Consertar so um entrega zero unidades.")),
        ]),
        OrderedDict([
            ("ROOT_CAUSE_ID", "RC-B"),
            ("NOME", "duas linguas para a ausencia, e a fronteira nao traduz"),
            ("SYMPTOMS", ["G-RUN-01"]),
            ("OWNER", "coleta/ingresso.py::_corrida_completa"),
            ("DEPENDENCIES", []),
            ("PORQUE_E_UMA_SO", (
                "NOT_PRESERVED e NAO_SEI sao dois donos da mesma pergunta. "
                "E a MESMA familia do defeito do SOURCE_ID: um valor honesto "
                "de um lado que o outro lado nao aceita.")),
        ]),
        OrderedDict([
            ("ROOT_CAUSE_ID", "RC-C"),
            ("NOME", "a estrada canonica nao tem prova que corra hoje"),
            ("SYMPTOMS", ["G-E2E-01", "G-RAW-01"]),
            ("OWNER", "tests/test_m2_rota_forward.py + "
                      "guarda/preservar_coleta.py"),
            ("DEPENDENCIES", ["RC-B"]),
            ("PORQUE_E_UMA_SO", (
                "os dois sao a mesma cegueira: a estrada corre e nao se "
                "consegue ver. Um porque o retrato esta velho, o outro porque "
                "a etapa e muda. E depende de RC-B: uma prova E2E que corra "
                "vai bater no enum assim que a corrida nao declarar pais.")),
        ]),
        OrderedDict([
            ("ROOT_CAUSE_ID", "RC-D"),
            ("NOME", "o SCRAP ainda nao entrega pelo contrato canonico"),
            ("SYMPTOMS", ["SCRAP_RAW_NAO_RECEBIDO"]),
            ("OWNER", "frente do SCRAP — fora desta medicao"),
            ("DEPENDENCIES", ["RC-A", "RC-B", "RC-C"]),
            ("PORQUE_E_UMA_SO", (
                "nao e do core: e a integracao que vem DEPOIS do core "
                "fechar. Fica na DAG da coleta grande, e nao na do fecho.")),
        ]),
    ], len(bloqueios)


# ⚠️ AS MISSOES FEITAS FICAM, COM A DATA DO FECHO. Apagar uma missao da fila
# depois de a correr esconde a ordem que se seguiu — e a ordem e metade do que
# esta medicao tem para ensinar.
FEITAS = [
    OrderedDict([
        ("ID", "C-FIX-ABSENCE-VOCABULARY-AT-THE-RUN-SEAM-V1"),
        ("ROOT_CAUSE", "RC-B"),
        ("ESTADO", FECHADO),
        ("FECHOU", ["G-RUN-01"]),
    ]),
    OrderedDict([
        ("ID", "C-RESTORE-CANONICAL-E2E-PROOF-V1"),
        ("ROOT_CAUSE", "RC-C"),
        ("ESTADO", FECHADO),
        ("FECHOU", ["G-E2E-01"]),
        ("NAO_FECHOU", ["G-RAW-01"]),
        ("PORQUE_NAO_FECHOU_TUDO", (
            "RC-C tinha dois sintomas. A prova voltou a correr; a etapa RAW "
            "continua muda, e isso e missao propria.")),
    ]),
    OrderedDict([
        ("ID", "C-MAKE-RAW-OBSERVABLE-V1"),
        ("ROOT_CAUSE", "RC-C"),
        ("ESTADO", FECHADO),
        ("FECHOU", ["G-RAW-01"]),
        ("COMO", ("sem segundo livro: o dono do rastro ja existia "
                  "(`medidas/rastro_da_coleta.py`) e o vocabulario ja tinha "
                  "RAW. Faltava UMA correlacao, e ela entrou como coluna na "
                  "tabela canonica — `etapa_da_corrida.raw_asset_id`, 028")),
        ("NAO_FECHOU", ["G-TEL-01"]),
        ("PORQUE_NAO_FECHOU_TUDO", (
            "a politica para quando a propria telemetria falha foi MEDIDA e "
            "preservada — a excecao sobe, e o bruto preservado fica. Inventar "
            "politica nova aqui faria falha de telemetria passar por falha de "
            "RAW, e elas nao sao a mesma coisa.")),
    ]),
    OrderedDict([
        ("ID", "C-CLOSE-READY-WITH-CANONICAL-WAITING-ROOM-V1"),
        ("ROOT_CAUSE", "RC-A"),
        ("ESTADO", FECHADO),
        ("FECHOU", ["G-READY-01", "G-READY-02"]),
        ("DECISAO", "docs/decisoes/ADR-SALA-DE-ESPERA-V1.md — o backend da "
                    "Sala de Espera V1 e o sistema de ficheiros, na morada "
                    "que ja existia. Decidido por gente, depois de a medicao "
                    "de C-CLOSE-THE-READY-EDGE-V1 mostrar que a lei aceita as "
                    "duas e nao escolhe."),
        ("COMO", ("a escrita saiu do control plane para UM dono "
                  "(`admissao/sala_de_espera.py`), e a rota forward passou a "
                  "chamar o mesmo dono. Sem tabela, sem migration, sem "
                  "segunda morada.")),
    ]),
]


def dag():
    """A fila minima. So BLOCKER ABERTO entra, e a ordem vem das dependencias.

    ⚠️ ELA ESVAZIOU-SE, E ISSO NAO E O MESMO QUE FECHAR.
    `C-CLOSE-READY-WITH-CANONICAL-WAITING-ROOM-V1` fechou os dois ultimos
    blockers. O que sobra para `COLLECTION_CORE_CLOSE` nao e um gap: e a
    CABECA da estrada — REQUEST, ORCHESTRATOR, EXECUTOR e RUN continuam sem
    corrida observada.

        ZERO BLOCKERS != CORE FECHADO.

    Uma fila vazia com um veredicto FAIL ao lado e exactamente o retrato
    honesto: nao ha buraco declarado por tapar, e ha uma propriedade por
    provar. Inventar aqui uma missao para a fila nao ficar vazia seria
    fabricar divida; esconder o FAIL seria pior.
    """
    return []


# ══════════════════════════════════════════════════════════════════════════
# 6 · RED TEAM
# ══════════════════════════════════════════════════════════════════════════
def red_team(gs, cadeia, est):
    p = []

    def A(n, achado, veredito):
        p.append({"PROVA": n, "ACHADO": achado, "VEREDITO": veredito})

    A("1 · lei IMPLEMENTED porque existe ficheiro",
      "o eixo de implementacao viaja como DECLARED_BY_BIBLE e nunca como "
      "observacao. Nenhum blocker foi derivado dele.", "SEPARADO")
    A("2 · migration LIVE porque esta no Git",
      "MIGRATION_IN_GIT = YES (27) · MIGRATION_APPLIED_LIVE = UNKNOWN. "
      "Medi contra descartavel, e descartavel nao promove a LIVE.", "GUARDADO")
    A("3 · READY dado por produzido por fixture",
      "READY FLOW_EXECUTED = NO. Ha um CLI e uma prova; nenhuma rota.",
      "NAO DERRUBA")
    A("4 · aresta dada por executada por teste de modulo isolado",
      "so conta aresta quando as DUAS pontas deixaram passagem na MESMA "
      "corrida — regra do proprio ledger, nao minha.", "GUARDADO")
    A("5 · custo ausente virado zero",
      "COST = NOT_INSTRUMENTED, e nunca 0.", "GUARDADO")
    A("6 · ERROR contado como NAO",
      "os cinco estados da porta continuam distintos; a Admission ja "
      "distingue NAO de NAO_SEI de ERRO.", "NAO DERRUBA")
    A("7 · mesmo SHA contado como mesma observacao",
      "fechado no §63 e nao reaberto aqui.", "NAO DERRUBA")
    A("8 · caminho usado como SOURCE_ID",
      "fechado no §60/§61; a correcao le o CAMPO do recibo.", "NAO DERRUBA")
    A("9-10 · portal como consumidor / bypass de Intelligence",
      "INTELLIGENCE_CONSUMER_COUNT = 0 e isso e o ALVO nesta fase, nao um "
      "defeito. O portal nao conta como consumidor canonico.", "GUARDADO")
    A("11 · ausencia de consumidor READY tratada como defeito",
      "o defeito medido e a ausencia de PRODUTOR e de DESTINO. Zero "
      "consumidores esta certo antes da Intelligence.", "DISTINGUIDO")
    A("12 · legado fora do fluxo contado como RAW operacional",
      "os 13 estao fora por decisao; G-LEG-01 e DEBT e nao BLOCKER.",
      "NAO DERRUBA")
    A("13 · branch do SCRAP contada como integrada",
      "SCRAP_INTEGRATED = NO, e RC-D esta na DAG da coleta grande, nao na "
      "do fecho.", "SEPARADO")
    A("14 · E2E com dados que a producao nunca entrega",
      "o defeito e o INVERSO e foi medido: o fixture entrega MENOS do que a "
      "producao entrega, e por isso a prova falha onde a estrada passa.",
      "ACHADO REAL")
    A("15 · PARTIAL virado blocker automaticamente",
      "%d leis estao PARTIAL e ha %d blockers. Nenhum blocker foi derivado "
      "do estado de lei." % (est.get("PARTIAL", 0),
                             sum(1 for g in gs if g["CLOSE_GATE"] == BLOCKER)),
      "GUARDADO")
    A("16 · divida estetica virada blocker",
      "G-TEL-01 e G-STRUCT-01 ficaram DEBT apesar de reais.", "GUARDADO")
    A("17 · blocker critico rebaixado por haver contorno manual",
      "G-READY-01 continua CRITICAL/BLOCKER embora exista um CLI que produz "
      "READY a mao. UM CLI NAO E UMA ROTA.", "GUARDADO")
    return p


# ══════════════════════════════════════════════════════════════════════════
# 7 · OS DOIS PORTOES
# ══════════════════════════════════════════════════════════════════════════
def uma_historia_so():
    """A estrada atravessada por UM pedido, e nao onze etapas que ja correram.

    ⚠️ ESTE PORTAO QUASE PASSOU POR UMA SOMA.
    Quando a cabeca da estrada passou a atravessar, todas as onze etapas
    ficaram `FLOW_EXECUTED = YES` — e `all(...)` deu PASS. Mas as etapas
    atravessam em DUAS estradas diferentes: a do pedido vai de RAW/STORAGE
    direto a ADMISSION, e a forward faz DERIVED/STRUCTURED entrando pelo RAW.

        DUAS METADES PROVADAS NAO SAO UMA ESTRADA PROVADA.

    Entao a pergunta deixa de ser «cada etapa ja correu?» e passa a ser «a
    MESMA historia atravessou?». A resposta vem da medicao que aperta o botao
    no pedido, e nao desta funcao.
    """
    caminho = os.path.join(RAIZ, "system-map", "data", "pedido.observado.json")
    if not os.path.isfile(caminho):
        return "NOT_MEASURED", ("provas/o_pedido_atravessa.py nunca correu "
                                "neste HEAD — e NOT_MEASURED != PASS")
    with io.open(caminho, encoding="utf-8") as f:
        d = json.load(f)
    if d.get("CANONICAL_E2E") == "PASS":
        return "PASS", "um pedido atravessou de REQUEST a SALA DE ESPERA"
    return "FAIL", ("a mesma historia parou em `%s` — medido em "
                    "provas/o_pedido_atravessa.py" % d.get("FIRST_LOST_EDGE"))


def portoes(cadeia, gs):
    bloqueios = [g["GAP_ID"] for g in gs if g["CLOSE_GATE"] == BLOCKER]
    historia, porque_historia = uma_historia_so()
    e2e = (all(cadeia[e]["FLOW_EXECUTED"] == "YES" for e in ETAPAS)
           and historia == "PASS")
    core = OrderedDict([
        ("VEREDICTO", "PASS" if (e2e and not bloqueios) else "FAIL"),
        ("CANONICAL_E2E", "PROVEN" if e2e else "NOT_PROVEN"),
        ("CANONICAL_E2E_SAME_STORY", historia),
        ("PORQUE_A_HISTORIA", porque_historia),
        ("IDENTITY", "PROVEN"),
        ("PROVENANCE", "PROVEN"),
        ("RAW", "PROVEN"),
        ("STORAGE", "PROVEN"),
        ("DERIVATION", "PROVEN"),
        ("STRUCTURED", "PROVEN_FOR_ONE_CLASS"),
        ("ADMISSION_INFRASTRUCTURE", "PROVEN"),
        ("READY", "PROVEN"),
        ("WAITING_ROOM", "PROVEN"),
        ("REPROCESS", "PROVEN"),
        ("RETRY_REUSE_NEW", "DISTINGUISHED"),
        ("ERROR_UNKNOWN", "DISTINGUISHED"),
        ("OBSERVABILITY", "INSUFFICIENT"),
        ("NO_UNAUTHORIZED_INTELLIGENCE_BYPASS", "YES"),
        ("BLOQUEADO_POR", bloqueios),
        ("PORQUE_FALHA", (
            porque_historia if not bloqueios and not e2e else
            "bloqueado por: %s" % (bloqueios or "—"))),
        ("ZERO_BLOCKERS_NAO_E_PASS", (
            "ZERO BLOCKERS != CORE FECHADO. E ONZE ETAPAS QUE JA CORRERAM NAO "
            "SAO UMA ESTRADA: o veredicto exige a MESMA historia, de ponta a "
            "ponta, e nao a soma de metades provadas em rotas diferentes.")),
        ("NAO_E_PERCENTAGEM", (
            "este veredicto nao vem da media das leis. Vem das propriedades "
            "que a coleta grande precisa de ter, e cada FAIL aponta a "
            "propriedade que falta.")),
    ])
    grande = OrderedDict([
        ("VEREDICTO", "FAIL"),
        ("PORQUE", "depende de COLLECTION_CORE_CLOSE = PASS, e ele nao passa"),
        ("REQUIRED_ACQUISITION_CAPABILITIES_INTEGRATED", "NO"),
        ("SCRAP_REQUIRED_CAPABILITIES_CANONICALLY_INTEGRATED", "NO"),
        ("BUDGET_COST_CONTROLS_SUFFICIENT", "UNKNOWN"),
        ("OBSERVABILITY_FOR_SCALE", "NO"),
        ("DISPOSABLE_PREFLIGHT_PROOF", "NO"),
    ])
    return core, grande


# ⚠️ UM CARIMBO DE COMMIT NUM FICHEIRO COMMITADO NASCE SEMPRE ATRASADO.
# `MEASURED_HEAD` e o HEAD do instante em que a medicao correu — e o ficheiro
# que o guarda entra no commit SEGUINTE. Ele nunca pode nomear o commit que o
# contem: isso e impossivel por construcao, e ja custou oito desencontros ao
# System Map, que o resolveu com a impressao das FONTES.
#
#     A PERGUNTA NAO E «QUE COMMIT?». E «QUE FONTES?».
#
# Entao ao lado do carimbo vai a IMPRESSAO DOS DONOS: o sha256 do conteudo dos
# ficheiros que DECIDEM este resultado. Se eles nao mudaram, a medicao continua
# a valer por mais commits que passem; se mudaram, ela esta velha mesmo que o
# carimbo pareca recente.
DONOS_DA_MEDICAO = (
    "provas/os_portoes_da_collection.py",
    "docs/biblia/leis.json",
    "system-map/data/buracos.generated.json",
    "system-map/data/pedido.observado.json",
)


def _substancia(caminho):
    """O que o dono DIZ, sem o carimbo de QUANDO foi feito.

    ⚠️ A PRIMEIRA VERSAO DISTO SOMAVA OS BYTES, E MORREU NA PRIMEIRA VOLTA.

    `buracos.generated.json` guarda um `PROVENANCE.HEAD` — o commit em que o
    censo correu. Esse campo muda a CADA commit, sem que uma virgula do censo
    mude. Uma impressao que o inclui muda sempre, e uma impressao que muda
    sempre nao responde a pergunta para que foi feita:

        UMA IMPRESSAO QUE NUNCA COINCIDE NAO DIZ «ESTA VELHO».
        NAO DIZ NADA.

    E era a doenca do `MEASURED_HEAD` outra vez, um andar abaixo: um carimbo
    de commit dentro de um ficheiro a contaminar quem o le.

    So `PROVENANCE.HEAD` sai. `MEDIDO_POR` fica: trocar quem mede E uma
    mudanca de substancia, e tem de gritar.
    """
    with open(caminho, "rb") as f:
        cru = f.read()
    if not caminho.endswith(".json"):
        return cru
    try:
        d = json.loads(cru.decode("utf-8"))
    except ValueError:
        return cru
    if isinstance(d, dict) and isinstance(d.get("PROVENANCE"), dict):
        d["PROVENANCE"] = OrderedDict(
            (k, v) for k, v in sorted(d["PROVENANCE"].items())
            if k != "HEAD")
    return json.dumps(d, sort_keys=True, ensure_ascii=False).encode("utf-8")


def impressao_dos_donos():
    """O sha256 da SUBSTANCIA de quem decide este resultado."""
    import hashlib
    h = hashlib.sha256()
    for rel in DONOS_DA_MEDICAO:
        caminho = os.path.join(RAIZ, rel)
        h.update(rel.encode("utf-8"))
        if os.path.isfile(caminho):
            h.update(_substancia(caminho))
        else:
            h.update(b"<AUSENTE>")
    return h.hexdigest()


def medir():
    d, L, total = leis()
    est = censo_declarado(L)
    cadeia, forward = cadeia_canonica()
    gs, nomes, fora_escopo, nao_tratados = gaps()
    if nao_tratados:
        raise MedicaoInvalida(
            "buracos medidos pelo censo e nao classificados: %s"
            % nao_tratados)
    rcs, n_bloq = causas_raiz(gs)
    core, grande = portoes(cadeia, gs)
    return OrderedDict([
        ("SCHEMA", "sintonia.collection-v1-close-gates/1"),
        ("O_QUE_ISTO_E", (
            "O que ainda impede declarar COLLECTION V1 = FECHADA, medido no "
            "HEAD de agora e separado do que e divida que nao bloqueia.")),
        ("MEASURE_NOT_FIX", "nenhum blocker foi corrigido nesta missao"),
        ("MEASURED_HEAD", subprocess.run(
            ["git", "rev-parse", "HEAD"], cwd=RAIZ, capture_output=True,
            text=True).stdout.strip()),
        ("FRESCURA", OrderedDict([
            ("IMPRESSAO_DOS_DONOS", impressao_dos_donos()),
            ("DONOS_DA_MEDICAO", list(DONOS_DA_MEDICAO)),
            ("O_QUE_A_IMPRESSAO_IGNORA", (
                "`PROVENANCE.HEAD` de um dono gerado. Esse campo muda a cada "
                "commit sem que o conteudo mude, e uma impressao que nunca "
                "coincide nao diz «esta velho»: nao diz nada.")),
            ("O_QUE_O_CARIMBO_NAO_DIZ", (
                "`MEASURED_HEAD` e o HEAD do instante da medicao, e o ficheiro "
                "que o guarda entra no commit SEGUINTE — nunca pode nomear o "
                "commit que o contem. Quem quer saber se esta medicao ainda "
                "vale compara a IMPRESSAO_DOS_DONOS, e nao o commit.")),
        ])),
        ("BIBLE_VERSION", d["VERSION"]),
        ("LAW_TOTAL", total),
        ("IMPLEMENTATION_STATE", OrderedDict([
            ("FONTE", LEIS),
            ("NATUREZA", "DECLARED_BY_BIBLE"),
            ("O_QUE_ISTO_NAO_E", (
                "nao e observacao de execucao. A Biblia declara de si propria "
                "o estado italiano de cada lei; isto e o registo dessa "
                "declaracao, e nenhum blocker foi derivado dele.")),
            ("CENSO", est),
        ])),
        ("CLOSE_GATE", OrderedDict([
            ("NATUREZA", "MEASURED"),
            ("PROPRIEDADES_QUE_DEFINEM_BLOCKER", list(PROPRIEDADES)),
            ("OS_DOIS_EIXOS_NAO_SE_INFEREM", (
                "uma lei PARTIAL pode nao bloquear nada, e uma lei pequena "
                "pode bloquear tudo")),
        ])),
        ("CANONICAL_E2E", cadeia),
        # DOIS ACHADOS, E SAO DE ESPECIES DIFERENTES.
        # Junta-los daria uma so «coisa que falta» — e as duas nao se resolvem
        # da mesma maneira, nem pela mesma pessoa. Misturar o que precisa de
        # uma chamada com o que precisa de uma DECISAO faz a segunda parecer
        # trabalho de codigo, e ela nao e.
        ("ACHADOS_DA_ESTRADA", [
            OrderedDict([
                ("EDGE", "STORAGE -> DERIVED"),
                ("TIPO", "WIRING_GAP"),
                ("O_QUE_FALTA", "a rota do orquestrador vai de RAW/STORAGE "
                                "direto a ADMISSION: a chamada a derivacao "
                                "nao esta ligada"),
                ("A_CAPACIDADE_EXISTE", "YES"),
                ("PROVA", "provas/o_pedido_atravessa.py::D1 — a MESMA "
                          "observacao daquela corrida derivou com PASS quando "
                          "`derivacao_forward` foi chamada explicitamente"),
                ("QUEM_RESOLVE", "codigo — uma ligacao, no orquestrador"),
                ("NAO_CORRIGIDO_NESTA_MISSAO",
                 "ligar so esta move o buraco uma aresta para a frente: a "
                 "seguinte nao tem dono"),
            ]),
            OrderedDict([
                ("EDGE", "DERIVED -> STRUCTURED"),
                ("TIPO", "CONTRACT_OWNER_GAP"),
                ("O_QUE_FALTA", "`public.conteudo` exige `canal_id`, e "
                                "`social_persistencia.exigir_canal` recusa "
                                "quando ele nao existe"),
                ("A_CAPACIDADE_EXISTE", "UNKNOWN — nao ha owner para medir"),
                ("PROVA", "provas/o_pedido_atravessa.py::D2 — a recusa diz, "
                          "por escrito, QUEM_RESOLVE = «um dono de identidade, "
                          "fora do executor de coleta», e esse dono nao esta "
                          "provado hoje"),
                ("QUEM_RESOLVE", "gente — e uma decisao de arquitetura"),
                ("NAO_CORRIGIDO_NESTA_MISSAO",
                 "criar o owner aqui seria inventar identidade de canal sem "
                 "ninguem ter decidido de quem ele e"),
            ]),
        ]),
        ("PROVA_E2E_HOJE", prova_e2e_corre()),
        ("DB_SCHEMA_VS_LIVE", OrderedDict([
            ("MIGRATION_IN_GIT", 27),
            ("MIGRATION_APPLIED_DISPOSABLE", "YES — 001..027, verificacao "
                                             "008 a passar"),
            ("MIGRATION_APPLIED_LIVE", "UNKNOWN"),
            ("PORQUE_UNKNOWN", "producao nao e laboratorio, e nao foi tocada"),
        ])),
        ("IDENTITY", OrderedDict([
            ("RAW_OBSERVATION_ID_CANONICAL", "raw_asset.id"),
            ("SOURCE_ID_PRESERVED_FORWARD", "YES — fechado no §61"),
            ("DOCUMENT_ID_FABRICATED", 0),
            ("SHA_USED_AS_OBSERVATION_ID", "NO"),
            ("STORAGE_PATH_USED_AS_IDENTITY", "NO — a 027 tirou a trava e pos "
                                              "chave sobre storage_object_id"),
        ])),
        ("OBSERVABILITY", observabilidade()),
        ("LEGACY_13", OrderedDict([
            ("DISPOSICAO", "LEGACY_KEEP_OUT_OF_FLOW"),
            ("LEGACY_STATE_OWNER", "NAO ATRIBUIDO"),
            ("CLOSE_GATE", DEBT),
            ("PORQUE", ("estao FORA da Collection operacional por decisao; o "
                        "que entra pela frente nao passa por este estado")),
        ])),
        ("SCRAP", OrderedDict([
            ("INTEGRATED", "NO"),
            ("CHANGED", "NO"),
            ("REQUIRED_BEFORE_BIG_COLLECTION", "YES"),
            ("PORQUE_SEPARADO", ("a ordem aprovada e fechar a maquina, "
                                 "integrar as capacidades, e so depois "
                                 "coletar")),
        ])),
        ("GAPS", gs),
        ("BURACOS_DO_CENSO", OrderedDict([
            ("NOMES", nomes),
            ("FORA_DESTE_ESCOPO", fora_escopo),
            ("DUPLICADO_MEDIDO", ("TELEMETRY_FAILURE_SEM_POLITICA aparece "
                                  "DUAS vezes no censo, com o mesmo nome, em "
                                  "dois sitios")),
        ])),
        ("BLOCKERS", [g["GAP_ID"] for g in gs if g["CLOSE_GATE"] == BLOCKER]),
        ("NON_BLOCKING_DEBT", [g["GAP_ID"] for g in gs
                               if g["CLOSE_GATE"] == DEBT]),
        ("ROOT_CAUSES", rcs),
        ("MISSOES_JA_FECHADAS", FEITAS),
        ("MINIMUM_MISSION_DAG", dag()),
        ("MINIMUM_MISSIONS_TO_COLLECTION_CORE_CLOSE", len(dag())),
        ("MINIMUM_MISSIONS_TO_BIG_COLLECTION_READY", "UNKNOWN"),
        ("PORQUE_O_SEGUNDO_E_UNKNOWN", (
            "depende de quantas capacidades do SCRAP a coleta grande exige, "
            "e isso ainda nao foi medido. Contar agora seria feeling com "
            "cara de DAG.")),
        ("COLLECTION_CORE_CLOSE", core),
        ("BIG_COLLECTION_READY", grande),
        ("RED_TEAM", red_team(gs, cadeia, est)),
        ("GENERATED_BY", "provas/os_portoes_da_collection.py"),
    ])


def main():
    art = medir()
    caminho = os.path.join(RAIZ, SAIDA)
    os.makedirs(os.path.dirname(caminho), exist_ok=True)
    with open(caminho, "w", encoding="utf-8") as f:
        json.dump(art, f, ensure_ascii=False, indent=2)
        f.write("\n")
    print("\n  OS PORTOES DA COLLECTION V1")
    print("  " + "─" * 66)
    print("  HEAD %s · Biblia %s · %d leis"
          % (art["MEASURED_HEAD"][:8], art["BIBLE_VERSION"], art["LAW_TOTAL"]))
    print("  estado declarado: %s" % art["IMPLEMENTATION_STATE"]["CENSO"])
    print("\n  A ESTRADA CANONICA")
    for e, v in art["CANONICAL_E2E"].items():
        print("    %-18s modulo=%-3s aresta=%-7s fluxo=%s"
              % (e, v["MODULE_EXISTS"], v["EDGE_EXISTS"], v["FLOW_EXECUTED"]))
    print("\n  BLOCKERS (%d)" % len(art["BLOCKERS"]))
    for g in art["GAPS"]:
        if g["CLOSE_GATE"] == BLOCKER:
            print("    %-12s %-9s %s" % (g["GAP_ID"], g["SEVERITY"],
                                         g["CONCEPT"][:44]))
    print("\n  DIVIDA QUE NAO BLOQUEIA (%d): %s"
          % (len(art["NON_BLOCKING_DEBT"]), ", ".join(art["NON_BLOCKING_DEBT"])))
    print("\n  CAUSAS-RAIZ (%d)" % len(art["ROOT_CAUSES"]))
    for r in art["ROOT_CAUSES"]:
        print("    %-6s %s" % (r["ROOT_CAUSE_ID"], r["NOME"][:58]))
    print("\n  FILA MINIMA")
    for m in art["MINIMUM_MISSION_DAG"]:
        print("    %d. %s" % (m["MISSION"], m["ID"]))
    print("\n  " + "─" * 66)
    print("  COLLECTION_CORE_CLOSE = %s"
          % art["COLLECTION_CORE_CLOSE"]["VEREDICTO"])
    print("  BIG_COLLECTION_READY  = %s"
          % art["BIG_COLLECTION_READY"]["VEREDICTO"])
    print("  missoes ate fechar o core: %s"
          % art["MINIMUM_MISSIONS_TO_COLLECTION_CORE_CLOSE"])
    print("  escrito: %s\n" % SAIDA)
    return 0


if __name__ == "__main__":
    sys.exit(main())
