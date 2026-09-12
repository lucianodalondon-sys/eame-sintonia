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
import ast
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


def uma_corrida_so(quantas):
    """A regra da MESMA historia, isolada para poder ser ela propria conferida.

    ⚠️ ESCRITA A DIREITO NO CASO POSITIVO, ELA SOBREVIVIA A MUTACAO.
    `== 1` trocado por `>= 1` nao muda nada num banco que so tem uma corrida:
    os dois lados dizem a mesma coisa, e nada reprova.

        UM LIMIAR SO ESTA TESTADO SE ALGUM CASO CAIR POR BAIXO DELE.

    Isolada, ela e usada DUAS vezes: no caso positivo, onde tem de dizer SIM
    a uma corrida, e no negativo, onde tem de dizer NAO a duas. Enfraquece-la
    passa a partir o segundo.
    """
    return quantas == 1


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
    # ⚠️ E O LIVRO DA PORTA TAMBEM, PELA MESMA RAZAO.
    # `pela_porta` chama `admissao.escrever()`, que acrescenta as decisoes ao
    # livro REAL da arvore. Uma medicao que escreve no acervo faz a medicao
    # seguinte medir o que esta deixou.
    #
    #     UMA MEDICAO QUE SUJA A ARVORE E UMA MEDICAO QUE A PROXIMA VAI MEDIR.
    #
    # Medido nesta missao: alem do livro, quatro PDFs de `XX/` — a raiz que o
    # armazem local usa — chegaram a ser commitados.
    # ⚠️ E O LIVRO FICA AO LADO DA SALA, E NAO DENTRO DELA.
    # Posto dentro, ele passou a contar como ficheiro da espera — e o caso que
    # exige «sala vazia depois de uma admissao negativa» reprovou por causa da
    # bancada, e nao do codigo. UMA SALA COM O LIVRO DENTRO NAO E A SALA.
    import pathlib
    import tempfile
    admissao.LIVRO = (pathlib.Path(tempfile.mkdtemp(prefix="livro-"))
                      / "LIVRO-DE-DECISOES.json")

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
         uma_corrida_so(int(outras[0][0])),
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
    # A LINHAGEM DO DERIVADO — de quem ele e filho, medido no banco
    # ═══════════════════════════════════════════════════════════════════
    # ⚠️ AQUI VIVIA `D1`, E ELE FOI REMOVIDO PORQUE A PERGUNTA MORREU.
    #
    # `D1` chamava `derivacao_forward.correr()` A MAO, com um PDF encontrado
    # por `glob` e emparelhado com `brutos[0]`, para responder «o DERIVED e
    # ALCANCAVEL a partir deste bruto?». Fazia sentido enquanto a aresta nao
    # existia: separava «nao sabe» de «ninguem chama». Agora a rota chama, e a
    # resposta esta na estrada — um diagnostico que repete o que a estrada ja
    # provou nao acrescenta prova nenhuma.
    #
    # E o `glob` tinha de sair por si so. Ele emparelhava O PRIMEIRO FICHEIRO
    # DA PASTA com A PRIMEIRA LINHA DA TABELA, e as duas ordens nao tem razao
    # nenhuma para coincidir:
    #
    #     PATH != IDENTITY.
    #     O PRIMEIRO FICHEIRO DA PASTA NAO E O FILHO DA PRIMEIRA LINHA.
    #
    # Uma prova que usa a heuristica que a producao tem proibida ensina a
    # heuristica. No lugar dela ficam perguntas ao BANCO sobre a linhagem que
    # a corrida realmente escreveu.
    filhos = sql.executa(
        "select d.id, d.raw_asset_id, r.run_id, d.parent_sha256, r.sha256"
        " from public.derived_artifact d"
        " join public.raw_asset r on r.id = d.raw_asset_id"
        " where r.run_id = '%s' order by d.id" % run_id)
    caso("D1_cada_DERIVADO_tem_pai_REAL_e_o_pai_e_DESTA_corrida",
         bool(filhos) and all(x[2] == run_id for x in filhos),
         "%d derivados · corridas dos pais: %s"
         % (len(filhos), sorted({x[2] for x in filhos}) or "nenhuma"))

    # ⚠️ E O PAI CERTO, E NAO SO «UM PAI DESTA CORRIDA».
    # Quatro observacoes e quatro derivados podem estar todos ligados a
    # corrida certa e na mesma trocados entre si — que e exactamente o que o
    # `glob` produzia. O `parent_sha256` e escrito pelo dono do derivado a
    # partir dos BYTES que ele derivou; se ele bate certo com o `sha256` da
    # observacao que o banco diz ser o pai, entao o par (bruto, bytes) veio
    # inteiro da linhagem, e nao de duas listas ordenadas por acaso.
    #
    #     MESMA CORRIDA != MESMO PAI.
    caso("D1b_o_pai_declarado_e_o_dono_dos_BYTES_que_foram_derivados",
         bool(filhos) and all(x[3] == x[4] for x in filhos),
         "pares (parent_sha256 == sha256 do pai): %d de %d"
         % (sum(1 for x in filhos if x[3] == x[4]), len(filhos)))

    # ⚠️ E UM POR OBSERVACAO, sem uma observacao a ficar com dois nem uma a
    # ficar sem nenhum. O grao desta unidade forward e 1:1 e quem o declara e
    # o runner; aqui so se confere que a corrida o cumpriu.
    pais = [int(x[1]) for x in filhos]
    caso("D1c_cada_observacao_desta_corrida_deu_UM_derivado",
         sorted(pais) == sorted(int(b[0]) for b in brutos)
         and len(set(pais)) == len(pais),
         "%d derivados para %d observacoes · pais distintos: %d"
         % (len(filhos), len(brutos), len(set(pais))))

    # ⚠️ E A ETAPA FALOU NESTA CORRIDA, e nao noutra. Um `derived_artifact`
    # sem passagem no rastro seria uma etapa que aconteceu as escondidas.
    passagem_d = [x for x in sql.executa(
        "select etapa::text, estado::text, edge_from::text, passed, reused,"
        " source_id, coalesce(route_class_id, '<NULL>')"
        " from public.etapa_da_corrida where run_id = '%s'"
        " and etapa = 'DERIVED' order by tentativa" % run_id)]
    caso("D1d_a_etapa_DERIVED_deixou_rasto_NESTA_corrida_vindo_do_RAW",
         bool(passagem_d) and passagem_d[0][2] == "RAW"
         and passagem_d[0][1] in ("PASS", "PARTIAL"),
         "DERIVED %s · edge_from=%s · passed=%s · source_id=%s"
         % (passagem_d[0][1], passagem_d[0][2], passagem_d[0][3],
            passagem_d[0][5]) if passagem_d else "nenhuma passagem DERIVED")

    # ⚠️ E FALOU UMA VEZ, E NAO DUAS. Duas linhas DERIVED para uma passagem
    # fariam a mesma etapa contar-se duas vezes, e quem somasse `passed` leria
    # o dobro do que aconteceu. A chave `(run_id, etapa, tentativa)` existe
    # para isso, e aqui confere-se que a rota nao a contornou.
    #
    #     CONTAR DUAS VEZES O MESMO TRABALHO E INVENTAR TRABALHO.
    caso("D1g_a_etapa_DERIVED_falou_UMA_vez_nesta_passagem",
         len(passagem_d) == 1,
         "linhas DERIVED desta corrida: %d" % len(passagem_d))

    # ⚠️ E A FONTE NAO FOI FABRICADA PARA A PASSAGEM FICAR BONITA.
    # Ela vem do coletor, apurada UMA vez pela porta, e e a mesma que a etapa
    # RAW declarou. Duas etapas da mesma corrida com fontes diferentes seriam
    # duas corridas com o mesmo nome.
    fonte_raw = sql.executa(
        "select source_id from public.etapa_da_corrida where run_id = '%s'"
        " and etapa = 'RAW'" % run_id)
    caso("D1e_a_fonte_do_DERIVED_e_a_MESMA_do_RAW_e_veio_do_coletor",
         bool(passagem_d) and bool(fonte_raw)
         and passagem_d[0][5] == fonte_raw[0][0] == "IT-T2-002",
         "RAW=%s · DERIVED=%s"
         % (fonte_raw[0][0] if fonte_raw else "-",
            passagem_d[0][5] if passagem_d else "-"))

    # ⚠️ E A CLASSE DE ROTA NAO FOI INVENTADA. Nenhuma peca entre o Pedido e a
    # corrida declara `ROUTE_CLASS_ID`; a resposta honesta e NULL. Escrever
    # `RC-1` porque o canario de hoje e RC-1 seria fabricar identidade a
    # partir do caso da vez, e e por isso que isto se mede em vez de se
    # assumir.
    #
    #     UNKNOWN HONESTO > ID INVENTADO.
    caso("D1f_a_ROUTE_CLASS_nao_foi_fabricada_quando_ninguem_a_prova",
         bool(passagem_d) and passagem_d[0][6] == "<NULL>",
         "route_class_id na passagem DERIVED: %s"
         % (passagem_d[0][6] if passagem_d else "-"))

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

    # ⚠️ RT5 · E A REGRA DA «MESMA HISTORIA» TEM DE RECUSAR DUAS.
    # MEDIDO na mutacao: trocar `== 1` por `>= 1` sobrevivia, porque o banco
    # descartavel so tem UMA corrida — os dois lados diziam a mesma coisa.
    #
    #     UM LIMIAR SO ESTA TESTADO SE ALGUM CASO CAIR POR BAIXO DELE.
    #
    # A segunda corrida e REAL: aperta-se o botao outra vez. Tentei primeiro
    # inserir a linha a mao, e o banco recusou-a — `forward_identificado_exige_
    # identidade`. Ele estava certo: uma observacao a mao nao tem identidade,
    # e fabricar-lhe uma para a medicao passar seria o defeito que esta missao
    # existe para nao cometer.
    #
    #     UMA BANCADA QUE FABRICA IDENTIDADE MEDE A FABRICA.
    #
    # Isto corre no FIM, depois de tudo o que dependia do estado limpo.
    orq.correr(Pedido(alvo="T2", filtros={"pais": "IT", "fonte": "IT-T2-002"}),
               memoria=_memoria(url), banco_do_rastro=sql)
    duas = sql.executa("select count(distinct run_id) from public.raw_asset")
    caso("N5_com_DUAS_corridas_a_regra_da_mesma_historia_RECUSA",
         not uma_corrida_so(int(duas[0][0])),
         "corridas distintas depois de uma segunda corrida REAL: %s — e a"
         " regra que diz «uma so» tem de reprovar aqui" % duas[0][0])

    # ⚠️ N6 · A SEGUNDA CORRIDA DERIVOU OS MESMOS BYTES, E NAO DUPLICOU.
    # Os mesmos quatro boletins, colhidos outra vez, sao QUATRO OBSERVACOES
    # NOVAS — `raw_asset` distintos, porque observar duas vezes e observar
    # duas vezes. Mas os BYTES sao os mesmos, e `derivacao_e_unica_por_regua`
    # e UNIQUE em `(parent_sha256, kind, producer, producer_version,
    # parameters_hash, serie_posicao)`: o derivado reencontra-se em vez de
    # nascer outra vez.
    #
    #     REUSED != NOT_RUN. A etapa correu, e o resultado ja existia.
    #
    # Isto e o contrato do dono do derivado, e esta missao NAO o redefine.
    passagens_2 = sql.executa(
        "select run_id, estado::text, passed, reused from"
        " public.etapa_da_corrida where etapa = 'DERIVED'"
        " and run_id <> '%s' order by id" % run_id)
    caso("N6_a_SEGUNDA_corrida_derivou_e_REAPROVEITOU_sem_duplicar",
         bool(passagens_2) and passagens_2[0][1] == "PASS"
         and int(passagens_2[0][3]) > 0 and int(passagens_2[0][2]) == 0,
         "DERIVED da 2a corrida: %s · passed=%s reused=%s"
         % (passagens_2[0][1], passagens_2[0][2], passagens_2[0][3])
         if passagens_2 else "a segunda corrida nao emitiu DERIVED")

    # ⚠️ N7 · E O SHA COLAPSA OS PAIS — MEDIDO, E DECLARADO COMO ACHADO.
    # A regua de unicidade do derivado e sobre os BYTES do pai, e nao sobre a
    # OBSERVACAO. Duas observacoes distintas dos mesmos bytes partilham UM
    # derivado, e esse derivado nomeia como pai so UMA delas — a primeira.
    #
    #     O GRAO DO DERIVADO E POR BYTES DO PAI, E NAO POR OBSERVACAO.
    #
    # Isto NAO se conserta aqui: mudar a regua de unicidade e mexer no
    # contrato do dono do derivado, e esta missao mede a cardinalidade em vez
    # de a redefinir. Fica escrito para nao ser descoberto por acidente:
    # uma corrida cujos bytes JA foram derivados antes nao tem
    # `derived_artifact` proprio, mesmo tendo a etapa DERIVED corrido.
    total_derivados = sql.executa("select count(*) from public.derived_artifact")
    caso("N7_o_sha_do_pai_COLAPSA_as_observacoes_e_isso_esta_medido",
         int(total_derivados[0][0]) == len(brutos),
         "%s derivados no banco para %d observacoes em 2 corridas — o grao e"
         " por BYTES do pai, e nao por observacao"
         % (total_derivados[0][0], int(duas[0][0]) * len(brutos)))

    # ⚠️ N8 · QUEM A PORTA RECUSA NAO CHEGA A DERIVACAO.
    # A lista de unidades sai de `RAW_OBSERVATIONS` — linhas que o banco
    # confirmou — e nao dos itens que o executor largou. Um item recusado na
    # porta nunca vira observacao, e por isso nao tem como virar unidade.
    #
    #     RECUSA NA PORTA -> NAO HA OBSERVACAO -> NAO HA O QUE DERIVAR.
    import ingresso as ing_
    from guarda.preservar_coleta import ArmazemDeMentira as _AM
    vazias, _ = ing_.unidades_para_a_derivacao(
        {"RAW_OBSERVATIONS": []}, ing_.ArmazemLocal(RAIZ))
    caso("N8_uma_passagem_sem_observacao_confirmada_nao_produz_unidade",
         vazias == [],
         "unidades para derivar quando o banco nao confirmou nada: %d"
         % len(vazias))

    # ⚠️ N9 · UM ENDERECO QUE NAO RESPONDE NAO VIRA CAMINHO INVENTADO.
    # O armazem responde `None` quando o byte nao esta la, e a observacao sai
    # em `sem_bytes` com o endereco que falhou — em vez de entrar na lista com
    # um caminho construido a mao que o executor iria abrir e nao encontrar.
    #
    #     AUSENCIA DE BYTES E AUSENCIA. ELA DIZ-SE, NAO SE PREENCHE.
    fantasma = {"RAW_OBSERVATIONS": [
        {"RAW_OBSERVATION_ID": 99, "RUN_ID": run_id,
         "STORAGE_PATH": "XX/nao-existe/DOCUMENT/nunca-aterrou.pdf",
         "SHA256": "0" * 64}]}
    u_f, sem_f = ing_.unidades_para_a_derivacao(fantasma,
                                                ing_.ArmazemLocal(RAIZ))
    caso("N9_endereco_que_nao_responde_nao_vira_caminho_fabricado",
         u_f == [] and len(sem_f) == 1
         and sem_f[0]["PORQUE"] == ing_.DERIVACAO_SEM_BYTES_LOCAIS,
         "unidades=%d · sem_bytes=%s"
         % (len(u_f), [x["PORQUE"] for x in sem_f]))

    # ⚠️ N10 · E UM ARMAZEM QUE NAO E DISCO DIZ QUE NAO TEM CAMINHO.
    # `ArmazemDeMentira` guarda bytes num dicionario, e um armazem de objetos
    # remoto tambem nao tem ficheiro local. Os dois respondem `None`, e a
    # unidade nao se faz — que e melhor do que um caminho que parece bom.
    u_m, sem_m = ing_.unidades_para_a_derivacao(fantasma, _AM())
    caso("N10_um_armazem_sem_disco_nao_inventa_caminho_local",
         u_m == [] and len(sem_m) == 1,
         "armazem de memoria: unidades=%d · sem_bytes=%d"
         % (len(u_m), len(sem_m)))

    # ⚠️ N11 · E A HEURISTICA DE CAMINHO NAO EXISTE NA PRODUCAO.
    # Isto le o CODIGO, e nao o comportamento: um `glob`, um `listdir` ou um
    # `*.pdf` dentro da rota do pedido seria a porta de entrada do defeito que
    # esta missao existe para nao cometer — emparelhar o primeiro ficheiro da
    # pasta com a primeira linha da tabela.
    #
    #     UMA REGRA QUE SO VIVE NA CABECA DE QUEM ESCREVEU
    #     E UMA REGRA QUE O PROXIMO NAO HERDA.
    producao = ("orquestrador/orquestrador.py", "coleta/ingresso.py",
                "coleta/derivacao_forward.py")
    achados = []
    for rel in producao:
        with io.open(os.path.join(RAIZ, rel), encoding="utf-8") as fh:
            arvore = ast.parse(fh.read())
        for no in ast.walk(arvore):
            if isinstance(no, ast.Call):
                alvo = no.func
                nome = (alvo.attr if isinstance(alvo, ast.Attribute)
                        else getattr(alvo, "id", ""))
                if nome in ("glob", "iglob", "listdir", "walk", "scandir"):
                    achados.append("%s: %s()" % (rel, nome))
    caso("N11_a_rota_do_pedido_nao_procura_ficheiros_por_caminho",
         not achados,
         "varrimentos de disco na rota: %s" % (achados or "nenhum"))

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
        "YES" if uma_corrida_so(int(outras[0][0])) else "NO"))
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
