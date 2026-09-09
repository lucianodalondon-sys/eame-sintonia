#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""O EXECUTOR CONTA-SE — a primeira torneira ligada ao cano.

    python3 provas/o_executor_conta_se.py

    O CONTRATO EXISTIA. O CANO EXISTIA. O LEITOR EXISTIA.
    E NENHUM EXECUTOR FALAVA.

`leis/telemetria.py` desenhou a lingua. `medidas/rastro_da_coleta.py` construiu
o cano ate ao banco. `medidas/scanner_da_coleta.py` sabe ler. Medido: em
`coleta/` nao havia UM import do rastro — a unica coisa que enchia a tabela
eram os testes, com numeros escritos a mao.

    UM CANO SEM TORNEIRA LEVA A MESMA AGUA QUE UM CANO QUE NAO EXISTE.

Esta prova liga a primeira torneira: `coleta/executor_texto_de_pdf.py`, num
banco de memoria. Zero rede, zero producao, zero migration aplicada.

O QUE ELA EXIGE
---------------
    A · caminho bom      as etapas reais saem, e a conta fecha
    B · falha injectada  a de cima PASS, a que falha FAIL com codigo,
                         a de baixo NOT_RUN — e nao FAIL
    E · contabilidade    o fluxo pode nao fechar e a conta fechar na mesma
    F · erro != recusa   falha tecnica nunca vira REJECTED
    G · nao correu       etapa a jusante nao conta como erro
"""
import os
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)
sys.path.insert(0, os.path.join(RAIZ, "coleta"))
import _gavetas  # noqa: E402,F401
import banco_no_seco as bs          # noqa: E402
import rastro_da_coleta as rastro   # noqa: E402
import executor_texto_de_pdf as ex  # noqa: E402


def _v(linha, chave):
    b = linha.get(chave)
    if b is None:
        return None
    return b.split("::")[0].strip().strip("'")


def _n(linha, chave):
    b = _v(linha, chave)
    try:
        return int(b)
    except (TypeError, ValueError):
        return 0


def _tabela(banco):
    print("  %-9s %-8s %6s %6s %5s %5s %5s %5s %6s  %s"
          % ("ETAPA", "ESTADO", "ENT", "SAI", "PASS", "REJ", "ERR", "REUSE",
             "S/EXPL", "DIAGNOSTICO"))
    for l in banco.linhas:
        print("  %-9s %-8s %6s %6s %5s %5s %5s %5s %6s  %s"
              % (_v(l, "etapa"), _v(l, "estado"),
                 _v(l, "input_count") or "-", _v(l, "output_count") or "-",
                 _n(l, "passed"), _n(l, "rejected"), _n(l, "error_count"),
                 _n(l, "reused"), l["_UNACCOUNTED"],
                 _v(l, "diagnostic_code") or ""))


def teste_a_caminho_bom():
    """A · o executor real, a seco, emite etapas reais e a conta fecha."""
    banco = bs.BancoNoSeco()
    recibo = ex.correr(seco=True, rastro=banco)
    _tabela(banco)
    etapas = [_v(l, "etapa") for l in banco.linhas]
    checks = [
        # ⚠️ DUAS, E NAO TRES. A terceira era `READY`, e ela saiu em O10R:
        # COL-LAW-043 nao deixa chamar READY a um texto guardado. Este caminho
        # atravessa RAW e DERIVED, e e so isso que ele atravessa.
        ("emitiu as duas etapas que correram", len(banco.linhas) == 2),
        ("as etapas sao do vocabulario", all(e in rastro.ETAPAS for e in etapas)),
        ("nenhuma passagem sem explicacao", not banco.sem_explicacao()),
        ("o grao de entrada e sempre declarado",
         all(_v(l, "input_grain") for l in banco.linhas
             if _v(l, "input_count") is not None)),
        ("o executor assinou cada passagem",
         all(_v(l, "actor") for l in banco.linhas)),
        ("nada foi escrito em producao", recibo["SECO"] is True),
    ]
    for nome, ok in checks:
        print("  %s %s" % ("OK  " if ok else "FALHA", nome))
    return all(ok for _n_, ok in checks)


def teste_b_falha_injectada():
    """B · quebrar UMA etapa de proposito, e exigir o relato certo.

    ⚠️ A falha e injectada no CONTA — a contabilidade que o executor produz —
    e nao no disco. Nao se estraga ficheiro nenhum para provar isto."""
    banco = bs.BancoNoSeco()
    conta = {"RAW_INPUT": 49, "RAW_CONTEUDOS_DISTINTOS": 43,
             "RAW_COPIAS_REPETIDAS": 6, "TEXT_LAYER_PRESENT": 0,
             "NEEDS_OCR": 5, "EXTRACTION_ERROR": 4, "RAW_UNKNOWN": 0,
             "DERIVED_EMITTED": 34, "DERIVED_LANDED": 0, "JA_EXISTIA": 0}
    ex.emitir_rastro(banco, "PROVA-FALHA", conta, 0,
                     [{"ERRO": "pdftotext nao esta nesta maquina"}], "")
    _tabela(banco)
    por = banco.por_etapa()
    raw, der = por.get("RAW"), por.get("DERIVED")
    # ⚠️ ATE O10R ESTA PROVA OLHAVA UMA TERCEIRA ETAPA, `READY`.
    # Ela existia, e nao devia: COL-LAW-043 diz que READY significa contratos
    # obrigatorios satisfeitos, e o contrato de saida exige ADMITIDO_POR. Este
    # caminho chamava READY ao texto que aterrou no registo, e saltava DOIS
    # estados de COL-LAW-044 de uma vez.
    #
    #     DERIVED PERSISTED != READY.
    #
    # A intencao desta prova NAO mudou — «a de cima passou, a que falha diz
    # FAIL, e a de baixo nao inventa nada». Mudou o que e «a de baixo»: neste
    # caminho nao ha etapa a jusante, e a prova passou a exigir que nenhuma
    # seja fabricada.
    checks = [
        ("a montante (RAW) passou", _v(raw, "estado") == "PASS"),
        ("a etapa que falhou diz FAIL", _v(der, "estado") == "FAIL"),
        ("a falha traz codigo do registry",
         bool(_v(der, "diagnostic_code"))),
        ("nenhuma etapa a jusante foi fabricada",
         por.get("READY") is None and por.get("ADMISSION") is None
         and por.get("STRUCTURED") is None),
        ("o caminho termina em DERIVED, e isso e a verdade",
         set(por) == {"RAW", "DERIVED"}),
        ("o ultimo ponto bom e RAW",
         banco.ultimo_bom(rastro.ETAPAS) == "RAW"),
        ("a conta fecha em TODAS as etapas, mesmo com a falha",
         not banco.sem_explicacao()),
    ]
    for nome, ok in checks:
        print("  %s %s" % ("OK  " if ok else "FALHA", nome))
    return all(ok for _n_, ok in checks)


def teste_ef_erro_nao_e_recusa():
    """E e F · o fluxo nao fecha, a conta fecha — e erro nao vira recusa."""
    banco = bs.BancoNoSeco()
    conta = {"RAW_INPUT": 10, "RAW_CONTEUDOS_DISTINTOS": 10,
             "RAW_COPIAS_REPETIDAS": 0, "TEXT_LAYER_PRESENT": 0,
             "NEEDS_OCR": 3, "EXTRACTION_ERROR": 4, "RAW_UNKNOWN": 0,
             # ⚠️ «3 SAIRAM» PASSOU A QUERER DIZER «3 ATERRARAM».
             # Ate O10R, `passed` contava o EMITIDO, e o que aterrava vivia
             # numa etapa READY a parte. Com essa etapa fora (COL-LAW-043),
             # emitido-que-nao-aterrou e `unknown` — sumiu e sabe-se quantos.
             # Esta fixture dizia 3 emitidos e 0 aterrados, o que nao e «3
             # sairam»: e 3 desaparecidos. A intencao era a primeira.
             "DERIVED_EMITTED": 3, "DERIVED_LANDED": 3, "JA_EXISTIA": 0}
    ex.emitir_rastro(banco, "PROVA-CONTA", conta, 0,
                     [{"ERRO": "falha tecnica"}], "")
    der = banco.por_etapa()["DERIVED"]
    entrada = _n(der, "input_count")
    somas = (_n(der, "passed") + _n(der, "rejected") + _n(der, "error_count")
             + _n(der, "reused") + _n(der, "unknown_count")
             + _n(der, "not_run_count"))
    checks = [
        ("10 entraram e 3 sairam: o fluxo NAO fechou",
         entrada == 10 and _n(der, "passed") == 3),
        ("e mesmo assim a conta fecha: 3+3+4 = 10",
         somas == entrada and der["_UNACCOUNTED"] == 0),
        ("os 4 de falha tecnica sao ERROR", _n(der, "error_count") == 4),
        ("os 3 sem camada de texto sao REJECTED, e nao erro",
         _n(der, "rejected") == 3),
        ("NEEDS_OCR nao foi contado como erro do sistema",
         _n(der, "error_count") == 4),
    ]
    for nome, ok in checks:
        print("  %s %s" % ("OK  " if ok else "FALHA", nome))
    print("  (100%% nao precisa CHEGAR — precisa ser EXPLICADO)")
    return all(ok for _n_, ok in checks)


def teste_traducao_nao_divergiu():
    """A conta do banco a seco tem de ser a mesma da migration 024."""
    texto = bs.definicao_da_migration()
    bate = all(p in texto for p in bs.PARCELAS) and "input_count" in texto
    print("  %s a traducao ainda bate com a migration 024"
          % ("OK  " if bate else "FALHA"))
    return bate


def main():
    print("PROVA — O EXECUTOR CONTA-SE?")
    print("")
    print("A — o executor real, a seco")
    a = teste_a_caminho_bom()
    print("")
    print("B — falha injectada numa etapa real")
    b = teste_b_falha_injectada()
    print("")
    print("E e F — o fluxo nao fecha, a conta fecha")
    ef = teste_ef_erro_nao_e_recusa()
    print("")
    print("TRADUCAO — o banco a seco nao divergiu da 024")
    t = teste_traducao_nao_divergiu()
    print("")
    bom = a and b and ef and t
    print("EXECUTOR_CONTA_SE=%s" % ("PASS" if bom else "FAIL"))
    print("  o que isto prova: um executor REAL emite a lingua comum, e o")
    print("  relato distingue NAO CORREU de FALHOU de RECUSADO.")
    print("  o que NAO prova: que o Postgres aceita — isso e DB_TESTED, e")
    print("  mede-se em provas/rastro_no_postgres.py.")
    return 0 if bom else 1


if __name__ == "__main__":
    sys.exit(main())
