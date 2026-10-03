#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ONDE ESTA, EXECUTAVELMENTE, O CORTE QUE FAZ «ENTROU = 0».

    python3 provas/o_corte_de_cr1.py

O censo dos cards e dos sensores mediu `ENTROU = 0` e classificou
`ORQUESTRADOR -> EXECUCAO` e `EXECUCAO -> PORTA` como CORTADOS. Mas o codigo
do orquestrador chama executor, ingresso e admissao numa so funcao, e
`pela_porta()` ESCREVE a Sala de Espera. Duas leituras do mesmo sistema, e uma
delas tinha de estar a medir outra coisa.

    CAN DO != DID DO — E DESTA VEZ NOS DOIS SENTIDOS.

Esta prova responde correndo, e nao lendo. Ela e READ-ONLY: nao escreve um
unico ficheiro no repositorio.

O QUE ELA MEDE
--------------
    A  reproduz `ENTROU` a partir dos artefactos, e mostra a formula
    B  corre a cadeia REAL sobre TODO o material que as receitas alcancam
    C  agrupa os vereditos da porta pela CAUSA, e nao pela suposicao

A DESCOBERTA, e ela nao e a que se esperava
--------------------------------------------
A cadeia NAO esta cortada. Ela corre inteira, e a porta julga. O que chega a
porta e que nao e material colhido:

    larga_em ->  _MANIFESTO.json    o INDICE dos documentos descarregados
                 CORPUS-*.json      o CATALOGO de pessoas
                 CONTAS-V1.json     a ficha de ONDE se pode coletar

`a_colheita()` tem uma heuristica generica — «uma lista, ou o primeiro campo
do ficheiro que seja lista de fichas» — e essa heuristica transforma as LINHAS
DE UM INDICE em pseudo-itens. A porta recusa-os, e recusa-os bem, com o
vocabulario certo: `NAO_SE_APLICA` para ficha de catalogo, `NAO_SEI` para
linha sem texto.

    O INDICE DE UMA COLHEITA NAO E A COLHEITA.
    E UM RECIBO — E UM RECIBO NAO SE ADMITE, LE-SE.

A hipotese anterior («43 derivados sem FACT_TIME davam 43 NAO_SEI») NAO se
confirma nesta rota: nenhuma das decisoes medidas aqui fala de FACT_TIME.

O QUE ISTO NAO PROVA
--------------------
Nao prova que a admissao esteja certa em toda a parte. Prova que, para todo o
material que as receitas alcancam hoje, ela nunca chega a ver um item colhido.
E nao prova nada sobre rotas que precisam de rede — essas nao correram.
"""
import collections
import json
import os
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)
import _gavetas  # noqa: E402,F401
import receitas  # noqa: E402
import orquestrador as orq  # noqa: E402
import admissao as adm  # noqa: E402
import retorno_da_coleta as rdc  # noqa: E402

fora = []


def caso(nome, ok, detalhe=""):
    fora.append((nome, ok, detalhe))


def a_formula_de_entrou():
    """A — de onde vem o zero, e o que ele mede depois do conserto."""
    with open(os.path.join(RAIZ, "system-map", "data",
                           "fronteira.observada.json"), encoding="utf-8") as f:
        fr = json.load(f)
    print("  A · A FORMULA DE «ENTROU»")
    print("  " + "-" * 68)
    print("    censo_cards_sensores.py :: sensores()   atravessou = READY_PRODUZIDO")
    print("      <- system-map/data/fronteira.observada.json")
    print("        <- provas/a_fronteira_da_coleta.py :: main()")
    print()
    for k in ("READY_PRODUZIDO", "CONSUMIDORES", "GAP"):
        print("    %-18s %s" % (k, json.dumps(fr.get(k), ensure_ascii=False)))
    # ⚠️ ESTE CHECK JA ESTEVE ERRADO, e o erro e instrutivo: ele fazia
    # `split("atravessou =")[1]` e apanhava a PRIMEIRA ocorrencia — que e o
    # comentario onde a formula ANTIGA esta documentada. O comentario que
    # explica o defeito fazia o check acusar o defeito.
    #
    #     PROCURAR TEXTO NUM FICHEIRO DE CODIGO APANHA OS COMENTARIOS,
    #     E UM COMENTARIO HONESTO CITA O QUE FOI CONSERTADO.
    #
    # Agora le-se a linha de atribuicao real, ignorando comentarios.
    fonte = open(os.path.join(RAIZ, "system-map", "scripts",
                              "censo_cards_sensores.py"), encoding="utf-8")
    atribuicoes = [l.strip() for l in fonte
                   if l.strip().startswith("atravessou =")]
    caso("A1_entrou_nao_depende_de_consumidor",
         len(atribuicoes) == 1 and "CONSUMIDORES" not in atribuicoes[0],
         "a formula real de ENTROU e: %s" % (atribuicoes or "NAO ENCONTRADA"))
    caso("A2_o_gap_nomeia_a_producao", fr.get("GAP") != "READY_SEM_CONSUMIDOR",
         "o gap ainda culpa o consumidor")
    return fr


def a_cadeia_corre():
    """B/C — o que o runtime entrega a porta, e o que ele BLOQUEIA.

    ⚠️ ESTA SECCAO MUDOU DE RESPOSTA, E NAO DE PERGUNTA. A pergunta e a mesma
    desde que esta prova nasceu: «o que chega a porta, e porque?». Em
    2026-09-11 a resposta era 253 pseudo-itens vindos de indices e catalogos.
    Depois de a COL-LAW-505 entrar no runtime, a resposta e ZERO — e o zero
    esta certo, porque nenhum desses ficheiros era colheita.

        O NUMERO CAIU DE 253 PARA 0 SEM NINGUEM PERDER UM UNICO ITEM REAL:
        NAO HAVIA NENHUM.
    """
    print()
    print("  B · O QUE O RUNTIME ENTREGA A PORTA, POR ESPECIE DECLARADA")
    print("  " + "-" * 68)
    print("    %-5s %-22s %8s %9s  %s" % ("UNIV", "EXECUTOR", "COLHEITA",
                                          "BLOQUEADO", "SUPORTE DECLARADO"))
    total = collections.Counter()
    motivos = collections.Counter()
    bloqueado = 0
    falsos = 0
    for universo, exes in receitas.EXECUTORES.items():
        for e in exes:
            envelope, _ = orq.o_envelope(e, "O-CORTE-DE-CR1")
            itens, _ = orq.a_colheita(e, "O-CORTE-DE-CR1")
            suporte = [x.get("ESPECIE") for x in (envelope.get("SUPORTE") or [])]
            bloqueado += len(suporte)
            print("    %-5s %-22s %8d %9d  %s" % (
                universo, e["id"], len(itens), len(suporte),
                ", ".join(suporte) or "—"))
            for x in itens:
                # FALSA COLHEITA: algo que atravessou sem ser especie COLHEITA.
                if x.get("ESPECIE") != rdc.COLHEITA:
                    falsos += 1
                d = adm.decidir(x, universo, corrida="O-CORTE-DE-CR1")
                total[d.resultado] += 1
                motivos[d.motivo[:64]] += 1

    print()
    print("  C · A CONTA")
    print("  " + "-" * 68)
    print("    FALSE_HARVEST_ANTES      253   (medido em 2026-09-11, heuristica)")
    print("    FALSE_HARVEST_AGORA      %d" % falsos)
    print("    SUPPORT_ITEMS_BLOCKED    %d" % bloqueado)
    print("    INGRESS_ITEMS            %d" % sum(total.values()))
    for m, n in motivos.most_common():
        print("    %3d x  %s" % (n, m))
    for k in ("SIM", "NAO", "NAO_SEI", "NAO_SE_APLICA", "ERRO"):
        print("    ADMISSION_%-14s %d" % (k, total.get(k, 0)))
    print("    READY_PRODUCED         %d" % total.get("SIM", 0))

    caso("B1_nenhuma_falsa_colheita_atravessa", falsos == 0,
         "%d itens atravessaram sem serem especie COLHEITA" % falsos)
    caso("B2_o_suporte_foi_visto_e_bloqueado", bloqueado > 0,
         "nenhum artefacto de suporte foi sequer reconhecido — o runtime "
         "deixou de ver o que existe, em vez de o classificar")
    caso("B3_a_porta_nunca_devolveu_ERRO", total.get("ERRO", 0) == 0,
         "houve ERRO: a porta nao conseguiu olhar, e isso NAO e rejeicao")
    # A hipotese que se veio testar, e que NAO se confirma.
    fala_de_tempo = sum(n for m, n in motivos.items()
                        if "fact_time" in m.lower() or "quando" in m.lower())
    caso("C1_a_causa_NAO_e_falta_de_FACT_TIME", fala_de_tempo == 0,
         "%d decisoes falam de tempo — a hipotese antiga volta a estar viva"
         % fala_de_tempo)
    return total


def main():
    print()
    print("=" * 72)
    print("  O CORTE DE CR-1 — medido, e nao deduzido")
    print("=" * 72)
    a_formula_de_entrou()
    a_cadeia_corre()
    print()
    print("=" * 72)
    for nome, ok, det in fora:
        print("  %s  %-46s %s" % ("PASS" if ok else "FAIL", nome,
                                  "" if ok else det))
    mal = [n for n, ok, _ in fora if not ok]
    print("=" * 72)
    print("O_CORTE_DE_CR1=%s" % ("PASS" if not mal else "FAIL"))
    print()
    print("  O QUE ISTO PROVA:")
    print("    a cadeia CORRE, a porta JULGA, e o runtime deixou de adivinhar:")
    print("    a especie vem DECLARADA e so a COLHEITA atravessa. O indice, o")
    print("    catalogo, o plano e o recibo ficam do lado de fora — vistos,")
    print("    nomeados e bloqueados.")
    print()
    print("  O QUE ISTO NAO PROVA:")
    print("    que exista colheita real. Nao existe, e ZERO e a resposta certa")
    print("    enquanto nenhum payload puder ser provado. Nada aqui diz respeito")
    print("    a rotas que precisam de rede — essas nao correram.")
    return 1 if mal else 0


if __name__ == "__main__":
    sys.exit(main())
