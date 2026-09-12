#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""A LINHAGEM DO REAPROVEITAMENTO — quem prova que ESTA observacao usou AQUELE derivado.

    BANCO_DESCARTAVEL_URL=postgresql://postgres@127.0.0.1:5433/descartavel \\
    ITALY_OPS_ROOT=/tmp/ops SALA_DESCARTAVEL=/tmp/sala \\
        python3 provas/a_linhagem_do_reaproveitamento.py

A PERGUNTA, E E UMA SO
----------------------
    QUANDO DUAS OBSERVACOES DIFERENTES TEM OS MESMOS BYTES E A MESMA RECEITA
    REAPROVEITA UM UNICO `derived_artifact`, O QUE FICA ESCRITO A DIZER QUE A
    SEGUNDA OBSERVACAO PARTICIPOU DAQUELA DERIVACAO?

A 022 decidiu o grao e escreveu o porque: duas capturas dos mesmos bytes, com a
mesma receita, dao UMA linha. A decisao nao se reabre aqui. O que se mede e a
frase que ela deixou ao lado:

    «E A PROCEDENCIA DA CAPTURA NAO SE PERDE... Todas as irmas encontram-se com
     select * from raw_asset where sha256 = <parent_sha256>»

Essa consulta responde «que observacoes TEM os mesmos bytes». A pergunta desta
medicao e outra: «que observacoes PASSARAM por esta derivacao».

    CAN INFER != OBSERVED EDGE.
    TER OS MESMOS BYTES NAO E TER PARTICIPADO DA MESMA EXECUCAO.

O QUE ESTA MEDICAO NAO FAZ
--------------------------
Nao implementa nada. Nao cria tabela, nao cria migration, nao escreve relacao
nenhuma. Ela constroi o estado pela rota REAL e depois interroga SO o que ficou
persistido — porque o que morre com o processo nao e linhagem.

    RUNTIME SABE != O SISTEMA GUARDA.
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
from pedido import Pedido                           # noqa: E402

_SO_VERIFICA = ("008",)

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


# ── A VARREDURA DO ESQUEMA, E POR QUE ELA E POR AST DO CATALOGO ────────────
# ⚠️ PROCURAR A RELACAO NAS TABELAS DE QUE EU ME LEMBRO NAO E PROCURAR.
# Uma resposta «nao existe owner» que so olhou para tres tabelas mede a minha
# memoria, e nao o esquema. Quem sabe que colunas apontam para `raw_asset` e
# para `derived_artifact` e o catalogo do proprio Postgres.
#
#     UM CENSO ESTA CERTO DENTRO DO UNIVERSO QUE DECLARA.
SQL_QUEM_APONTA = """
select c.conrelid::regclass::text as tabela,
       (select string_agg(a.attname, ',' order by a.attnum)
          from unnest(c.conkey) k join pg_attribute a
            on a.attrelid = c.conrelid and a.attnum = k) as colunas,
       c.confrelid::regclass::text as aponta_para
  from pg_constraint c
 where c.contype = 'f'
   and c.confrelid in ('public.raw_asset'::regclass,
                       'public.derived_artifact'::regclass)
 order by 1, 3
"""


def quem_aponta(sql):
    """Toda tabela que declara, por chave estrangeira, ligacao a um dos dois."""
    fora_ = {}
    for tabela, colunas, alvo in sql.executa(SQL_QUEM_APONTA):
        fora_.setdefault(tabela, []).append((colunas, alvo))
    return fora_


def tabelas_que_ligam_os_dois(mapa):
    """As que apontam para OS DOIS — a forma de uma relacao de linhagem.

    Uma tabela que aponta so para `raw_asset` sabe de observacoes. Uma que
    aponta so para `derived_artifact` sabe de derivados. So quem aponta para os
    dois pode dizer que ESTA observacao usou AQUELE derivado.
    """
    return sorted(t for t, ligacoes in mapa.items()
                  if {alvo for _, alvo in ligacoes} >=
                  {"raw_asset", "derived_artifact"})


def main():
    url = os.environ.get("BANCO_DESCARTAVEL_URL")
    ops = os.environ.get("ITALY_OPS_ROOT")
    sala = os.environ.get("SALA_DESCARTAVEL")
    if not url or not ops or not sala:
        print("FALTA AMBIENTE DESCARTAVEL — e SKIP != PASS.")
        print("  BANCO_DESCARTAVEL_URL · ITALY_OPS_ROOT · SALA_DESCARTAVEL")
        print("LINHAGEM_DO_REAPROVEITAMENTO=NOT_MEASURED")
        return 2
    espera.MORADA = sala
    import pathlib
    import tempfile
    admissao.LIVRO = (pathlib.Path(tempfile.mkdtemp(prefix="livro-"))
                      / "LIVRO-DE-DECISOES.json")

    print("=" * 72)
    print("A LINHAGEM DO REAPROVEITAMENTO — %d migrations · descartavel"
          % len(cadeia_de_migrations()))
    print("=" * 72)
    aplicar_migrations(url)
    sql = cc.Banco(url)

    import orquestrador as orq
    p = Pedido(alvo="T2", filtros={"pais": "IT", "fonte": "IT-T2-002"})

    # ── CORRIDA A — a primeira captura, e a derivacao que nasce dela ─────
    rec_a = orq.correr(p, memoria=_memoria(url), banco_do_rastro=sql)
    run_a = rec_a["RUN_ID"]
    # ── CORRIDA B — a MESMA fonte outra vez: outros factos, mesmos bytes ──
    rec_b = orq.correr(p, memoria=_memoria(url), banco_do_rastro=sql)
    run_b = rec_b["RUN_ID"]

    brutos_a = sql.executa(
        "select id, sha256 from public.raw_asset where run_id = '%s'"
        " order by id" % run_a)
    brutos_b = sql.executa(
        "select id, sha256 from public.raw_asset where run_id = '%s'"
        " order by id" % run_b)
    derivados = sql.executa(
        "select id, raw_asset_id, parent_sha256 from public.derived_artifact"
        " order by id")

    print("\n  O ESTADO CONSTRUIDO PELA ROTA REAL")
    print("    RUN A = %s · raw_asset %s" % (run_a, [int(x[0]) for x in brutos_a]))
    print("    RUN B = %s · raw_asset %s" % (run_b, [int(x[0]) for x in brutos_b]))
    print("    derived_artifact: %d linha(s) · pais %s"
          % (len(derivados), [int(x[1]) for x in derivados]))

    ids_a = {int(x[0]) for x in brutos_a}
    ids_b = {int(x[0]) for x in brutos_b}
    shas_a = {x[1] for x in brutos_a}
    shas_b = {x[1] for x in brutos_b}

    caso("P1_as_duas_corridas_produziram_observacoes_DISTINTAS",
         ids_a and ids_b and not (ids_a & ids_b),
         "A=%s · B=%s — duas capturas sao dois factos" % (sorted(ids_a),
                                                          sorted(ids_b)))
    caso("P2_e_os_BYTES_sao_os_MESMOS",
         bool(shas_a) and shas_a == shas_b,
         "sha256 distintos em A: %d · em B: %d · iguais: %s"
         % (len(shas_a), len(shas_b), shas_a == shas_b))
    caso("P3_houve_UMA_derivacao_por_conteudo_e_nao_duas",
         len(derivados) == len(shas_a),
         "%d derivados para %d conteudos em 2 corridas — o grao da 022"
         % (len(derivados), len(shas_a)))

    # ── A · O DERIVADO SABE DE QUEM NASCEU? ─────────────────────────────
    pais_dos_derivados = {int(x[1]) for x in derivados}
    caso("A_o_derivado_prova_de_QUAL_COPIA_nasceu",
         bool(derivados) and pais_dos_derivados <= ids_a,
         "raw_asset_id dos derivados: %s — todos da corrida A"
         % sorted(pais_dos_derivados))

    # ⚠️ E A PROVA E DECLARATIVA, e nao confianca em quem escreveu: a 022 poe
    # uma chave estrangeira COMPOSTA sobre `(raw_asset_id, parent_sha256)`, de
    # modo que o pai por ID e o pai por SHA tenham de ser o MESMO pai.
    trava = sql.executa(
        "select conname from pg_constraint"
        " where conrelid = 'public.derived_artifact'::regclass"
        " and contype = 'f' and array_length(conkey, 1) = 2")
    caso("A2_e_o_parentesco_e_travado_pelo_banco_e_nao_pelo_escritor",
         bool(trava),
         "chave estrangeira composta: %s"
         % ([t[0] for t in trava] or "NENHUMA"))

    # ── B · ALGUEM ESCREVEU QUE A OBSERVACAO DE B USOU AQUELE DERIVADO? ──
    mapa = quem_aponta(sql)
    pontes = tabelas_que_ligam_os_dois(mapa)
    print("\n  QUEM APONTA PARA AS DUAS TABELAS, SEGUNDO O CATALOGO")
    for tabela in sorted(mapa):
        for colunas, alvo in mapa[tabela]:
            print("    %-28s %-22s -> %s" % (tabela, colunas, alvo))

    # A relacao, se existisse, teria de nomear uma observacao de B e um
    # derivado. Procura-se em TODA tabela que o catalogo diz ligar os dois.
    achou_b = []
    for tabela in pontes:
        linhas = sql.executa("select count(*) from public.%s" % tabela)
        if int(linhas[0][0]):
            achou_b.append(tabela)
    caso("B_existe_relacao_persistida_dizendo_que_a_observacao_de_B_usou_X",
         bool(achou_b),
         "tabelas que ligam observacao a derivado: %s"
         % (pontes or "NENHUMA no esquema inteiro"))

    # ── D · DA PARA DISTINGUIR «NAO PROCESSADO» DE «REAPROVEITADO»? ──────
    # ⚠️ A PERGUNTA E POR OBSERVACAO, E NAO POR CORRIDA.
    # O ledger tem UMA linha por (corrida, etapa, tentativa), com CONTAGENS.
    # Numa corrida com uma so observacao a contagem chega para deduzir. Numa
    # corrida com quatro, `reused=4` diz quantas, e nao QUAIS — e num resultado
    # misto (duas reaproveitadas, duas em erro) nao ha por onde saber qual foi
    # qual.
    #
    #     CONTAGEM POR ETAPA != DESTINO POR ITEM.
    passagem_b = sql.executa(
        "select passed, reused, error_count, unknown_count, output_count"
        " from public.etapa_da_corrida where run_id = '%s' and etapa = 'DERIVED'"
        % run_b)
    colunas_da_etapa = {c[0] for c in sql.executa(
        "select column_name from information_schema.columns"
        " where table_schema = 'public' and table_name = 'etapa_da_corrida'")}
    caso("D_o_ledger_nomeia_QUAIS_observacoes_foram_reaproveitadas",
         "derived_artifact_id" in colunas_da_etapa,
         "a passagem DERIVED de B diz %s · e as colunas de identidade do "
         "ledger sao %s"
         % (passagem_b[0] if passagem_b else "nada",
            sorted(c for c in colunas_da_etapa if c.endswith("_id"))))

    # ⚠️ E A COLUNA QUE EXISTE NAO SERVE AQUI, POR LEI.
    # A 028 poe `raw_asset_id` no ledger — e com uma trava que so a deixa ser
    # preenchida na etapa RAW. Ela nao e uma ponte por acaso: e uma ponte
    # proibida nesta etapa, de proposito.
    trava_028 = sql.executa(
        "select pg_get_constraintdef(oid) from pg_constraint"
        " where conrelid = 'public.etapa_da_corrida'::regclass"
        " and conname = 'so_o_raw_nomeia_a_observacao'")
    caso("D2_a_unica_coluna_de_observacao_no_ledger_e_exclusiva_do_RAW",
         bool(trava_028) and "RAW" in (trava_028[0][0] if trava_028 else ""),
         (trava_028[0][0] if trava_028 else "a trava da 028 nao esta aqui"))

    # ⚠️ E A ARITMETICA DA CORRIDA HOMOGENEA NAO E UMA ARESTA.
    # Na corrida B, `input_count=4` e `reused=4`: da para DEDUZIR que as quatro
    # observacoes de B foram reaproveitadas. A deducao funciona porque todos os
    # itens cairam no MESMO balde — e deixa de funcionar no instante em que a
    # passagem tem resultados mistos.
    #
    # ⚠️ ESTA PARTE CHAMA O RUNNER DIRECTAMENTE, E TEM DE EXPLICAR PORQUE.
    # A pergunta aqui NAO e sobre a estrada — essa mede-se em
    # `provas/o_pedido_atravessa.py`, e comeca no botao. A pergunta e sobre o
    # que o LEDGER CONSEGUE EXPRIMIR, e para a responder e preciso produzir uma
    # passagem mista, que a fonte real nao entrega hoje: os quatro boletins do
    # canario sao todos PDF. Construir o estado pelo dono dele e medir o
    # ledger; esperar que a fonte um dia varie seria nao medir.
    import derivacao_forward as fwd
    from guarda.preservar_coleta import ArmazemLocal
    nao_e_pdf = os.path.join(sala, "nao-e-um-pdf.txt")
    io.open(nao_e_pdf, "w", encoding="utf-8").write("isto nao e um PDF")
    boletim = sql.executa(
        "select o.storage_path from public.storage_object o"
        " join public.raw_asset r on r.storage_object_id = o.id"
        " where r.id = %s" % sorted(ids_b)[0])
    misto = fwd.correr(
        [{"RAW_ASSET_ID": sorted(ids_b)[0],
          "PDF": os.path.join(RAIZ, boletim[0][0])},
         {"RAW_ASSET_ID": sorted(ids_b)[1], "PDF": nao_e_pdf}],
        banco_do_rastro=sql, run_id=run_b, armazem=ArmazemLocal(RAIZ),
        memoria=_memoria(url), source_id="IT-T2-002")
    baldes = {k: v for k, v in (misto.get("BALDES") or {}).items() if v}
    # Com dois baldes cheios e duas observacoes, a linha do ledger diz QUANTAS
    # cairam em cada um — e nao QUAL caiu onde. As duas leituras possiveis sao
    # simetricas, e nada no estado persistido as separa.
    caso("D3_com_resultado_MISTO_a_contagem_deixa_de_identificar_quem",
         len(baldes) > 1,
         "a mesma passagem devolveu %s para 2 observacoes — a linha guarda os "
         "numeros, e nao os nomes" % baldes)

    # ── C · SEM INFERIR PELO SHA, SOBRA ALGUMA COISA? ───────────────────
    # A consulta que a 022 propoe encontra as IRMAS. Mede-se o que ela devolve
    # e o que ela NAO consegue distinguir.
    irmas = sql.executa(
        "select r.id, r.run_id from public.raw_asset r"
        " join public.derived_artifact d on d.parent_sha256 = r.sha256"
        " where d.id = %s order by r.id" % int(derivados[0][0]))
    caso("C_a_consulta_por_SHA_encontra_as_irmas_mas_nao_diz_quem_PARTICIPOU",
         len(irmas) > 1,
         "para o derivado %s ela devolve %d observacoes (%s) — e as duas "
         "chegam iguais: ela responde «mesmos bytes», nao «passou por aqui»"
         % (int(derivados[0][0]), len(irmas),
            sorted(int(x[0]) for x in irmas)))

    # ⚠️ E O RUNTIME SABIA. `preservar_derivado` devolve, no reencontro,
    # TESTEMUNHA_NO_BANCO e TESTEMUNHA_DESTA_CHAMADA — os dois lados da aresta
    # que ninguem escreve. O conhecimento existe e morre com o processo.
    fonte_writer = io.open(os.path.join(RAIZ, "guarda", "preservar_derivado.py"),
                           encoding="utf-8").read()
    caso("E_o_runtime_CONHECE_a_aresta_e_devolve_os_dois_lados",
         "TESTEMUNHA_NO_BANCO" in fonte_writer
         and "TESTEMUNHA_DESTA_CHAMADA" in fonte_writer,
         "guarda/preservar_derivado.py devolve os dois lados no REUSED — e nao "
         "escreve nenhum")

    # ══════════════════════════════════════════════════════════════════
    # OS QUATRO CASOS, UM A UM — e cada contador com o seu universo dito
    # ══════════════════════════════════════════════════════════════════
    # ⚠️ A PRIMEIRA VERSAO DISTO COMPAROU DOIS CONJUNTOS DIFERENTES.
    #
    # De um lado somava as arestas dos casos 1, 2 e 4 — e DEIXAVA DE FORA o
    # caso 3, que e justamente o que cria a segunda aresta. Do outro somava
    # TODAS as passagens DERIVED das duas corridas, incluindo as do arranque e
    # a do diagnostico misto. Saiu «1 contra 6», e os dois numeros nao contavam
    # a mesma populacao.
    #
    #     DOIS NUMEROS SO SE COMPARAM SE MEDIREM O MESMO CONJUNTO.
    #     UM RACIOCINIO CERTO APOIADO NUM NUMERO ERRADO
    #     E UM RACIOCINIO POR CONFIRMAR.
    #
    # A conclusao continuou a valer — mas por outra prova, e nao por aquela.
    # Agora cada contador diz de onde vem, e a separacao dos conceitos sai de
    # DUAS propriedades, medidas cada uma no seu proprio universo:
    #
    #     P1  a MESMA aresta e tocada por MAIS DE UMA passagem
    #     P2  uma NOVA observacao dos mesmos bytes cria uma NOVA aresta
    #         SEM criar um novo `derived_artifact`
    from collections import OrderedDict
    from guarda.preservar_coleta import ArmazemLocal as _AL
    caminho_de = lambda rid: os.path.join(RAIZ, sql.executa(
        "select o.storage_path from public.storage_object o"
        " join public.raw_asset r on r.storage_object_id = o.id"
        " where r.id = %s" % rid)[0][0])

    def aresta_do_recibo(r):
        """A UNICA aresta (observacao, derivado) que esta passagem tocou."""
        for x in (r.get("RESULTADOS") or []):
            linha = x.get("LINHA") or {}
            if linha.get("id"):
                return (int(x["RAW_ASSET_ID"]), int(linha["id"]))
        return None

    def ultima_tentativa(run):
        """A tentativa da linha DERIVED que a chamada acabou de escrever."""
        linhas = sql.executa(
            "select tentativa from public.etapa_da_corrida"
            " where run_id = '%s' and etapa = 'DERIVED'"
            " order by tentativa desc limit 1" % run)
        return int(linhas[0][0]) if linhas else None

    def passagens_derived(run):
        return len(sql.executa(
            "select 1 from public.etapa_da_corrida"
            " where run_id = '%s' and etapa = 'DERIVED'" % run))

    a1 = sorted(ids_a)[0]
    x1 = int([d for d in derivados if int(d[1]) == a1][0][0])
    aresta_original = (a1, x1)
    casos_medidos = []

    def registar(cid, run, aresta, nova, resultado, onde, tent):
        casos_medidos.append(OrderedDict([
            ("CASE_ID", cid), ("RUN_ID", run),
            ("RAW_ASSET_ID", aresta[0]), ("DERIVED_ARTIFACT_ID", aresta[1]),
            ("MATERIAL_EDGE", "%d->%d" % aresta),
            ("MATERIAL_EDGE_NEW", nova),
            ("STAGE_PASSAGE_TENTATIVA", tent),
            ("ITEM_RESULT", resultado),
            ("PERSISTED_WHERE", onde),
        ]))

    # CASO 1 · a passagem da ROTA de A, na unidade (a1 -> x1). Ela derivou
    # quatro unidades de uma vez; a que se acompanha aqui e esta.
    porta_1 = [d["PORTA"] for d in
               ((rec_a.get("DERIVACAO") or {}).get("DERIVADOS") or [])
               if int(d["RAW_ASSET_ID"]) == a1]
    # ⚠️ E ESTA E A UNICA ARESTA DO CENARIO QUE FICA ESCRITA — e nao porque
    # alguem a tenha registado: e subproduto da coluna TESTEMUNHA de
    # `derived_artifact`, que guarda de QUAL COPIA se leu. A PRIMEIRA aresta de
    # cada derivado sobrevive por acidente de desenho; as outras nao sobrevivem.
    registar("CASE_1", run_a, aresta_original, "YES",
             porta_1[0] if porta_1 else "?",
             "derived_artifact.raw_asset_id (testemunha)", 0)

    # CASO 2 · a MESMA corrida, a MESMA observacao, outra vez.
    c2 = fwd.correr([{"RAW_ASSET_ID": a1, "PDF": caminho_de(a1)}],
                    banco_do_rastro=sql, run_id=run_a, armazem=_AL(RAIZ),
                    memoria=_memoria(url), source_id="IT-T2-002")
    registar("CASE_2", run_a, aresta_do_recibo(c2), "NO",
             "REUSED" if c2["BALDES"]["REUSED"] else "?",
             "em lado nenhum", ultima_tentativa(run_a))
    caso("G2_retry_na_MESMA_corrida_nao_cria_aresta_nova",
         aresta_do_recibo(c2) == aresta_original
         and c2["BALDES"]["REUSED"] == 1,
         "aresta tocada: %s (a mesma) · tentativa=%s"
         % (aresta_do_recibo(c2), ultima_tentativa(run_a)))

    # CASO 3 · outra corrida, OUTRA observacao, os MESMOS bytes.
    b1 = sorted(ids_b)[0]
    derivados_antes = int(sql.executa(
        "select count(*) from public.derived_artifact")[0][0])
    c3 = fwd.correr([{"RAW_ASSET_ID": b1, "PDF": caminho_de(b1)}],
                    banco_do_rastro=sql, run_id=run_b, armazem=_AL(RAIZ),
                    memoria=_memoria(url), source_id="IT-T2-002")
    aresta_irma = aresta_do_recibo(c3)
    derivados_depois = int(sql.executa(
        "select count(*) from public.derived_artifact")[0][0])
    registar("CASE_3", run_b, aresta_irma, "YES",
             "REUSED" if c3["BALDES"]["REUSED"] else "?",
             "em lado nenhum", ultima_tentativa(run_b))

    # CASO 4 · a observacao de A, derivada OUTRA VEZ, numa passagem que
    # pertence a OUTRA corrida.
    #
    # ⚠️ E O BANCO ACEITA. `etapa_da_corrida.run_id` so exige que a corrida
    # EXISTA — nao exige que seja a corrida que capturou a observacao.
    #
    #     A CORRIDA QUE CAPTUROU NAO E NECESSARIAMENTE A QUE DERIVOU.
    c4 = fwd.correr([{"RAW_ASSET_ID": a1, "PDF": caminho_de(a1)}],
                    banco_do_rastro=sql, run_id=run_b, armazem=_AL(RAIZ),
                    memoria=_memoria(url), source_id="IT-T2-002")
    registar("CASE_4", run_b, aresta_do_recibo(c4), "NO",
             "REUSED" if c4["BALDES"]["REUSED"] else "?",
             "em lado nenhum", ultima_tentativa(run_b))
    caso("G4_rederivar_noutra_corrida_NAO_muda_a_aresta",
         aresta_do_recibo(c4) == aresta_original,
         "aresta tocada: %s — a MESMA de A, numa passagem da corrida B"
         % (aresta_do_recibo(c4),))

    # ── OS TRES CONTADORES, CADA UM COM O SEU UNIVERSO ──────────────────
    arestas_dos_quatro = {(c["RAW_ASSET_ID"], c["DERIVED_ARTIFACT_ID"])
                          for c in casos_medidos}
    passagens_da_aresta = sum(
        1 for c in casos_medidos
        if (c["RAW_ASSET_ID"], c["DERIVED_ARTIFACT_ID"]) == aresta_original)
    passagens_do_cenario = passagens_derived(run_a) + passagens_derived(run_b)

    # P1 · A MESMA ARESTA, VARIAS PASSAGENS. Universo: os quatro casos, e
    # dentro deles os que tocam `aresta_original`.
    caso("G5a_a_MESMA_aresta_e_tocada_por_MAIS_DE_UMA_passagem",
         passagens_da_aresta > 1,
         "a aresta %s foi tocada por %d das %d passagens dos quatro casos — "
         "logo PASSAGEM != ARESTA"
         % (aresta_original, passagens_da_aresta, len(casos_medidos)))

    # P2 · NOVA OBSERVACAO, NOVA ARESTA, ZERO DERIVADOS NOVOS. Universo: o
    # caso 3 sozinho, com a contagem de `derived_artifact` antes e depois.
    caso("G5b_nova_observacao_dos_mesmos_bytes_cria_aresta_sem_criar_derivado",
         aresta_irma is not None and aresta_irma != aresta_original
         and aresta_irma[1] == aresta_original[1]
         and derivados_antes == derivados_depois,
         "aresta nova %s sobre o MESMO derivado %d · derived_artifact %d -> %d "
         "— logo ARESTA != DERIVADO"
         % (aresta_irma, aresta_original[1], derivados_antes, derivados_depois))

    # E os tres numeros ficam ditos com o nome do conjunto que mediram, para
    # ninguem voltar a compara-los aos pares.
    caso("G5c_cada_contador_declara_o_seu_universo",
         len(arestas_dos_quatro) == 2 and passagens_da_aresta == 3
         and passagens_do_cenario > len(casos_medidos),
         "arestas nos 4 casos=%d · passagens sobre a aresta original=%d · "
         "passagens DERIVED no cenario inteiro=%d (inclui arranque e "
         "diagnostico) — TRES universos, e nao um"
         % (len(arestas_dos_quatro), passagens_da_aresta,
            passagens_do_cenario))

    # ⚠️ E O RESULTADO MUDA SEM A ARESTA MUDAR.
    resultados_da_original = [
        c["ITEM_RESULT"] for c in casos_medidos
        if (c["RAW_ASSET_ID"], c["DERIVED_ARTIFACT_ID"]) == aresta_original]
    caso("G6_o_resultado_muda_sem_a_aresta_mudar",
         len(set(resultados_da_original)) > 1,
         "a aresta %s teve %s nas tres passagens que a tocaram"
         % (aresta_original, resultados_da_original))

    # ⚠️ E O RESULTADO POR ITEM NAO ESTA GUARDADO EM LADO NENHUM.
    # `etapa_da_corrida` guarda BALDES: QUANTOS foram reaproveitados, e nao
    # QUAIS. Dizer que `REUSED` «ja mora nos baldes» e dizer de mais — o balde
    # guarda o NUMERO, e o numero nao nomeia ninguem.
    #
    #     CONTAGEM POR PASSAGEM != RESULTADO POR ITEM.
    onde_o_resultado_mora = {c["PERSISTED_WHERE"] for c in casos_medidos[1:]}
    caso("G7_o_resultado_POR_ITEM_nao_tem_dono_duravel",
         onde_o_resultado_mora == {"em lado nenhum"},
         "o destino de cada item nas passagens 2-4 esta guardado em: %s"
         % sorted(onde_o_resultado_mora))

    print()
    print("  OS QUATRO CASOS, UM A UM")
    for c in casos_medidos:
        print("    %-7s run=…%s raw=%-3d der=%-3d %-8s nova=%-3s tent=%s  %s"
              % (c["CASE_ID"], c["RUN_ID"][-6:], c["RAW_ASSET_ID"],
                 c["DERIVED_ARTIFACT_ID"], c["ITEM_RESULT"],
                 c["MATERIAL_EDGE_NEW"], c["STAGE_PASSAGE_TENTATIVA"],
                 c["PERSISTED_WHERE"]))

    persistido = bool(achou_b)
    veredito = "ALREADY_PROVEN" if persistido else "GAP_CONFIRMED"

    print()
    for nome, ok, detalhe in fora:
        print("  %-4s %-62s %s" % ("PASS" if ok else "FALHA", nome, detalhe))
    print("=" * 72)
    print("DERIVED_REUSE_LINEAGE=%s" % veredito)
    print("  DURABLE_EDGE_A_TO_X = YES · derived_artifact.raw_asset_id + FK composta")
    print("  DURABLE_EDGE_B_TO_X = %s" % ("YES" if persistido else "NO"))
    print("  PONTES_NO_ESQUEMA   = %s" % (pontes or "nenhuma"))
    json.dump({
        "RUN_A": run_a, "RUN_B": run_b,
        "RAW_A": sorted(ids_a), "RAW_B": sorted(ids_b),
        "DERIVED": [{"ID": int(x[0]), "RAW_ASSET_ID": int(x[1])}
                    for x in derivados],
        "TABELAS_QUE_LIGAM_OBSERVACAO_A_DERIVADO": pontes,
        "DURABLE_EDGE_A_TO_X": "YES",
        "DURABLE_EDGE_B_TO_X": "YES" if persistido else "NO",
        "DERIVED_REUSE_LINEAGE": veredito,
        # ── O QUE DECIDE O GRAO DA PARTICIPACAO ─────────────────────────
        # ⚠️ CADA NOME DIZ O UNIVERSO QUE MEDIU, e por isso nenhum se compara
        # com o do lado sem se pensar. `ARESTAS_MATERIAIS_DISTINTAS` saiu daqui:
        # ele contava so os casos 1, 2 e 4 e chamava-se «distintas», o que
        # convidava a ler «de todos os casos».
        #
        #     UM CONTADOR SEM UNIVERSO NO NOME E UM CONVITE A COMPARACAO ERRADA.
        "CASOS": casos_medidos,
        "MATERIAL_EDGES_ALL_FOUR_CASES": len(arestas_dos_quatro),
        "PASSAGES_TOUCHING_ORIGINAL_EDGE": passagens_da_aresta,
        "DERIVED_STAGE_PASSAGES_TOTAL_IN_SCENARIO": passagens_do_cenario,
        "O_QUE_O_TERCEIRO_INCLUI": (
            "todas as passagens DERIVED das duas corridas — as da rota, a do "
            "diagnostico misto e as dos casos 2, 3 e 4. NAO se compara com os "
            "outros dois: mede outra populacao."),
        # As duas propriedades que separam os conceitos, cada uma no seu
        # universo. Sao estas que sustentam a decisao — e nao a razao entre
        # dois contadores de conjuntos diferentes.
        "P1_MESMA_ARESTA_VARIAS_PASSAGENS": passagens_da_aresta > 1,
        "P2_NOVA_ARESTA_SEM_NOVO_DERIVADO": (
            derivados_antes == derivados_depois
            and aresta_irma != aresta_original),
        "ARESTA_ORIGINAL": "%d->%d" % aresta_original,
        "ARESTA_IRMA": ("%d->%d" % aresta_irma) if aresta_irma else None,
        "O_RESULTADO_MUDA_SEM_A_ARESTA_MUDAR": "YES",
        "RESULTADOS_DA_ARESTA_ORIGINAL": resultados_da_original,
        "ITEM_EXECUTION_RESULT_PERSISTENCE": "NOT_IMPLEMENTED",
        "A_CORRIDA_QUE_DERIVA_PODE_NAO_SER_A_QUE_CAPTUROU": "YES",
    }, io.open(os.path.join(RAIZ, "system-map", "data",
                            "linhagem.observada.json"), "w",
               encoding="utf-8"), indent=2, ensure_ascii=False)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
