#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""A SALA DE ESPERA NÃO TEM MORADA — e a lei não escolhe uma por nós.

    BANCO_DESCARTAVEL_URL=postgresql://postgres@127.0.0.1:5433/descartavel \\
        python3 provas/a_sala_de_espera_nao_tem_morada.py

O QUE ESTA MEDIÇÃO EXISTE PARA RESPONDER
-----------------------------------------
`C-CLOSE-THE-READY-EDGE-V1` pede para fechar dois blockers:

    G-READY-01   READY nao e produzido por nenhuma rota
    G-READY-02   a sala de espera nao tem armazenamento

O primeiro é ligação, e tem caminho. O segundo é uma **morada**, e a casa
nunca a escolheu. Esta medição prova que a escolha existe, que ela é real, e
que nenhuma das duas saídas é ilegítima — e por isso ela não é minha.

    DUAS SAÍDAS LEGÍTIMAS COM CONSEQUÊNCIAS DIFERENTES
    NÃO SÃO UM DETALHE DE IMPLEMENTAÇÃO. SÃO UMA DECISÃO.

O QUE JÁ EXISTE, E QUE NÃO SE INVENTA OUTRA VEZ
------------------------------------------------
    CONTRATO   COL-LAW-043, 11 campos fixos
    DONO       admissao.pronto_para_inteligencia(), e é o único construtor
    ENTRADA    `item` + `Decisao` — e a rota forward JÁ os tem em mãos,
               montados em `rota_forward_documento.admitir()`

Ou seja: `G-READY-01` não precisa de contrato novo nem de tradutor novo.

O QUE NÃO EXISTE
----------------
    MORADA     o destino declarado no mapa é um FICHEIRO por corrida, e ele
               não existe e não tem escritor
    IDENTIDADE a decisão de admissão não tem linha em lado nenhum: o dono
               escreve num livro JSON, e `Decisao` não carrega surrogate

O QUE ESTA MEDIÇÃO NÃO FAZ
---------------------------
Não cria tabela. Não cria migration. Não liga a aresta. Fechar `G-READY-02`
antes de a morada estar escolhida seria escolher em silêncio — e uma morada
escolhida em silêncio é uma que ninguém pode discutir depois.
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

import admissao                                          # noqa: E402
import coleta_checkpoint as cc                           # noqa: E402

# A morada declarada no mapa, e que a `provas/a_fronteira_da_coleta.py` ja
# media como inexistente.
DESTINO_DECLARADO = os.path.join(RAIZ, "data", "samples",
                                 "PRONTO-PARA-INTELIGENCIA")
LIVRO_DA_PORTA = os.path.join(RAIZ, "data", "samples",
                              "LIVRO-DE-DECISOES.json")
# Os 11 campos que a lei declara. Escritos aqui para a comparacao ter dois
# lados — o codigo do dono e a lei — e nao um eco.
CAMPOS_DA_LEI = ("ESTADO", "ITEM_ID", "UNIVERSO", "TEXTO", "SOURCE_ID",
                 "SOURCE_LOCATION", "FACT_LOCATION", "FACT_TIME",
                 "CAPTURED_AT", "CORRIDA", "ADMITIDO_POR")

fora = []


def caso(nome, condicao, detalhe=""):
    fora.append((nome, bool(condicao), detalhe))


def _fonte(caminho):
    return io.open(os.path.join(RAIZ, caminho), encoding="utf-8").read()


def _tabelas(sql, padrao):
    return [x[0] for x in sql.executa(
        "select table_name from information_schema.tables"
        " where table_schema = 'public' and table_name like '%s'" % padrao)]


def main():
    print("=" * 70)
    print("A SALA DE ESPERA NAO TEM MORADA")

    # ── 1 · O CONTRATO EXISTE, E TEM UM DONO SO ─────────────────────────
    d = admissao.decidir({"id": "medicao-1", "texto": "Ensaio de campo com DOI",
                          "source_id": "IT-T7-001", "fact_time": "2026-05-02"},
                         "T7", corrida="medicao")
    unidade = admissao.pronto_para_inteligencia(
        {"id": "medicao-1", "texto": "Ensaio de campo com DOI",
         "source_id": "IT-T7-001", "fact_time": "2026-05-02"}, d)
    caso("S1_o_contrato_READY_existe_e_bate_com_a_lei",
         tuple(unidade) == CAMPOS_DA_LEI,
         "%d campos, na ordem da COL-LAW-043" % len(unidade))

    # ⚠️ PROCURAR A PALAVRA APANHOU QUEM SO A MENCIONA.
    # A primeira versao desta medicao procurava a string
    # `PRONTO_PARA_INTELIGENCIA` no ficheiro, e acusou o orquestrador de ser um
    # segundo construtor. Ele nao e: a linha 442 dele escreve aquele texto como
    # ESTADO de um recibo. Ele CHAMA o dono, e chamar nao e construir.
    #
    #     MENCIONAR UM CONTRATO NAO E IMPLEMENTA-LO.
    #     E A DIFERENCA SO SE VE NA ESTRUTURA, NUNCA NO TEXTO.
    #
    # Quem constroi e quem devolve o dicionario com os 11 campos da lei. Isso
    # le-se por AST, e por AST o orquestrador sai da lista sozinho.
    import ast
    construtores, chamadores = [], []
    for pasta in ("admissao", "coleta", "guarda", "orquestrador", "medidas"):
        base = os.path.join(RAIZ, pasta)
        if not os.path.isdir(base):
            continue
        for raiz_, _d, fs in os.walk(base):
            if "__pycache__" in raiz_:
                continue
            for f in sorted(fs):
                if not f.endswith(".py"):
                    continue
                rel = os.path.relpath(os.path.join(raiz_, f), RAIZ)
                arv = ast.parse(io.open(os.path.join(raiz_, f),
                                        encoding="utf-8").read())
                for no in ast.walk(arv):
                    if isinstance(no, ast.Dict):
                        chaves = {k.value for k in no.keys
                                  if isinstance(k, ast.Constant)
                                  and isinstance(k.value, str)}
                        if set(CAMPOS_DA_LEI) <= chaves and rel not in construtores:
                            construtores.append(rel)
                    if isinstance(no, ast.Call) and getattr(
                            no.func, "attr", None) == "pronto_para_inteligencia":
                        if rel not in chamadores:
                            chamadores.append(rel)
    caso("S2_o_READY_tem_UM_construtor_e_nao_dois",
         construtores == ["admissao/admissao.py"],
         "constroi: %s · chama: %s" % (construtores, chamadores))

    # ── 2 · E A ENTRADA DELE JA ESTA EM MAOS DA ROTA ────────────────────
    # `rota_forward_documento.admitir()` monta o `item` e recebe a `Decisao`.
    # Isto importa: `G-READY-01` nao precisa de tradutor novo.
    rota = _fonte("coleta/rota_forward_documento.py")
    caso("S3_a_rota_JA_tem_o_item_e_a_decisao_que_o_dono_pede",
         "admissao.decidir(item, universo, corrida=run_id)" in rota
         and "item.update({" in rota,
         "a ligacao que falta e uma CHAMADA, e nao uma traducao")

    # ── 3 · E A MORADA NAO EXISTE ───────────────────────────────────────
    caso("S4_a_morada_declarada_no_mapa_nao_existe",
         not os.path.isdir(DESTINO_DECLARADO),
         "declarado: data/samples/PRONTO-PARA-INTELIGENCIA/<RUN_ID>.json")
    # ⚠️ E AQUI ESTA A CORRECAO QUE MUDA A DECISAO.
    # Eu ia declarar que a morada declarada «nao tem escritor». TEM.
    # `orquestrador/orquestrador.py` decide, escreve o livro da porta, chama o
    # dono do READY por cada SIM e GRAVA o ficheiro da corrida. A pasta nao
    # existe porque nenhuma corrida daquele caminho produziu aceites — e nao
    # porque falte codigo.
    #
    #     DESTINO VAZIO != DESTINO SEM DONO.
    #
    # Isto pesa na decisao: a saida (A) nao e hipotese, e implementacao que ja
    # existe. Criar uma tabela ao lado seria um SEGUNDO dono da mesma espera.
    escritor = _fonte("orquestrador/orquestrador.py")
    caso("S5_a_morada_declarada_TEM_escritor_e_ele_esta_completo",
         'PRONTOS / f"{run_id}.json"' in escritor
         and ".write_text(" in escritor
         and "adm.pronto_para_inteligencia(x, d)" in escritor,
         "orquestrador/orquestrador.py decide, admite e grava a corrida")

    # ── 4 · A DECISAO DE ADMISSAO NAO TEM IDENTIDADE PERSISTIDA ─────────
    campos_da_decisao = set(d.__dataclass_fields__)
    caso("S6_a_decisao_de_admissao_nao_carrega_surrogate",
         not {"id", "decision_id", "ID"} & campos_da_decisao,
         "campos de `Decisao`: %s" % sorted(campos_da_decisao))
    caso("S7_e_o_dono_dela_escreve_num_livro_JSON_e_nao_no_banco",
         "LIVRO" in _fonte("admissao/admissao.py")
         and "data" in os.path.relpath(LIVRO_DA_PORTA, RAIZ),
         "livro: %s" % os.path.relpath(LIVRO_DA_PORTA, RAIZ))

    # ── 5 · A LEI PERMITE AS DUAS MORADAS, E NAO ESCOLHE ────────────────
    biblia = _fonte("BIBLIA-CANONICA-DA-COLETA.md")
    i = biblia.find("COL-LAW-044")
    trecho = biblia[i:i + 600] if i > 0 else ""
    caso("S8_a_lei_lista_ficheiro_E_banco_como_armazenamento_legitimo",
         "data/samples" in trecho and "Supabase" in trecho,
         "COL-LAW-044 · ONDE ESTA: Supabase · git · data/raw · data/samples")
    caso("S9_e_a_COL_LAW_043_nao_diz_onde_a_unidade_pousa",
         "PRONTO-PARA-INTELIGENCIA" not in biblia[
             biblia.find("COL-LAW-043"):biblia.find("COL-LAW-044")],
         "a lei fixa os 11 campos e cala-se sobre a morada")

    # ── 6 · E A ESPERA QUE JA EXISTE E DE OUTRA ESPECIE ─────────────────
    url = os.environ.get("BANCO_DESCARTAVEL_URL")
    if not url:
        print("\nSEM BANCO DESCARTAVEL — e SKIP != PASS.")
        print("SALA_DE_ESPERA=NOT_MEASURED")
        return 2
    sql = cc.Banco(url)

    destinos = [x[0] for x in sql.executa(
        "select unnest(enum_range(null::destino_de_normalizacao))::text")]
    caso("S10_a_espera_do_LASTMILE_e_outro_conceito",
         "pessoa_e_origem" in destinos and "READY" not in destinos,
         "ela espera por normalizacao em tabelas de dominio: %s"
         % destinos[:3])

    esperas = _tabelas(sql, "%espera%") + _tabelas(sql, "%ready%") \
        + _tabelas(sql, "%pronto%")
    caso("S11_nao_ha_tabela_nenhuma_para_a_unidade_pronta",
         not [t for t in esperas if not t.startswith("v_")],
         "tabelas candidatas no banco: %s" % (esperas or "nenhuma"))

    # ── 7 · A BASELINE, CONTRA O BANCO ──────────────────────────────────
    etapas = [x[0] for x in sql.executa(
        "select distinct etapa::text from public.etapa_da_corrida")]
    caso("S12_BASELINE_a_ADMISSION_corre",
         "ADMISSION" in etapas, "etapas com passagem: %s" % sorted(etapas))
    caso("S13_BASELINE_o_READY_nao_e_produzido",
         "READY" not in etapas,
         "nenhuma passagem de READY — G-READY-01 confirmado no HEAD")
    caso("S14_BASELINE_e_nao_ha_linha_de_espera_para_contar",
         not [t for t in esperas if not t.startswith("v_")],
         "G-READY-02 confirmado no HEAD")

    print("=" * 70)
    for nome, ok, detalhe in fora:
        print("  %-4s %-52s %s" % ("PASS" if ok else "FALHA", nome, detalhe))
    veredito = all(ok for _n, ok, _d in fora)
    print("=" * 70)
    print("SALA_DE_ESPERA=%s" % ("MEDIDA" if veredito else "MEDICAO_FALHOU"))
    print("""
  A DECISAO QUE FALTA, E QUE NAO E MINHA:

    ONDE POUSA A UNIDADE PRONTA DA ROTA FORWARD?

  O que esta medicao corrigiu a meio: a saida (A) NAO e hipotese. Ela esta
  implementada e completa em `orquestrador/orquestrador.py` — ele decide,
  escreve o livro da porta, chama o dono do READY por cada SIM e grava
  `data/samples/PRONTO-PARA-INTELIGENCIA/<RUN_ID>.json`. A pasta nao existe
  porque nenhuma corrida daquele caminho produziu aceites.

    DESTINO VAZIO != DESTINO SEM DONO.

    (A) A ROTA FORWARD PASSA A USAR A MORADA QUE JA EXISTE
        Um dono, um destino, zero migrations. `G-READY-01` fecha por uma
        CHAMADA: a rota ja tem o `item` e a `Decisao` em maos.
        Consequencia: a espera continua em ficheiro. Sem chave estrangeira,
        sem unicidade, sem transacao — e esta missao pede concorrencia e
        crash/retry PROVADOS em PostgreSQL. Com ficheiro, nao se provam.
        `G-READY-02` fecharia por «ja tem morada», e nao por «tem armazem».

    (B) A SALA DE ESPERA GANHA TABELA (migration 029)
        E a unica saida que suporta unicidade e concorrencia reais, e poe a
        espera ao lado das outras etapas da estrada.
        Consequencia: passa a haver DUAS moradas para a mesma espera — a
        nova, e a que o orquestrador ja escreve. Uma delas tem de ser
        retirada, e retirar a do orquestrador muda o comportamento de um
        caminho que NAO e destes dois blockers.
        Alem disso a decisao de admissao nao tem linha nenhuma: ou READY se
        liga a ela por chave NATURAL (item + universo + corrida), ou a
        ADMISSION ganha armazenamento — e isso e `G-ADM-01`, divida de OUTRO
        portao.

  As duas sao legitimas pela lei: a COL-LAW-044 lista `data/samples` E
  `Supabase` como armazenamento, e a COL-LAW-043 fixa os 11 campos e cala-se
  sobre a morada. Nao ha contrato para consultar — ha uma escolha por fazer.

    UMA MORADA ESCOLHIDA EM SILENCIO
    E UMA QUE NINGUEM PODE DISCUTIR DEPOIS.

  `provas/a_fronteira_da_coleta.py` ja dizia, antes desta missao:

    «Sao duas coisas, e liga-las e uma DECISAO DE ARQUITETURA
     — nao um remendo de codigo.»
""")
    return 0 if veredito else 1


if __name__ == "__main__":
    raise SystemExit(main())
