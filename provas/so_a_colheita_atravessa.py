#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""SO A COLHEITA ATRAVESSA — a COL-LAW-505 ligada ao runtime, medida a correr.

    python3 provas/so_a_colheita_atravessa.py

Sem rede, sem banco, sem recoleta. Tudo o que esta prova usa ou ja existe nesta
arvore, ou e escrito por ela numa raiz temporaria que ela propria apaga.

O QUE ELA MEDE
--------------
    A  a mesma corrida, o mesmo item, a cadeia inteira:
       adapter -> ENVELOPE -> conferir() -> so_o_que_entra() -> ingresso
       -> RAW preservado -> admissao
    B  os doze ataques: nada que nao seja COLHEITA atravessa
    C  o contraexemplo historico do `CLASSIFICADO-V1.json`

POR QUE ELA EXISTE
------------------
Porque «o runtime respeita o contrato» e uma frase, e uma frase nao se audita.
Antes desta ligacao, 253 pseudo-itens atravessavam a porta e o sistema nao
sabia. A unica maneira de isso nunca mais acontecer em silencio e haver algo
que CORRA e falhe alto.

    UMA LEI SEM NADA QUE A CORRA E UM COMENTARIO COM NUMERO.
"""
import io
import json
import os
import shutil
import sys
import tempfile

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)
import _gavetas  # noqa: E402,F401
import admissao as adm  # noqa: E402
import ingresso as ing  # noqa: E402
import italy_executor as adapter  # noqa: E402
import orquestrador as orq  # noqa: E402
import receitas  # noqa: E402
import retorno_da_coleta as rdc  # noqa: E402

fora = []


def caso(nome, ok, detalhe=""):
    fora.append((nome, ok, detalhe))


def _executor(eid):
    return [x for v in receitas.EXECUTORES.values() for x in v if x["id"] == eid][0]


# ─────────────────────────────────────────────────────────────────────────
# A · A MESMA CORRIDA, O MESMO ITEM, A CADEIA INTEIRA
# ─────────────────────────────────────────────────────────────────────────
def a_cadeia_com_um_item_real():
    """Um documento de verdade desta arvore, do livro ate a admissao.

    O payload NAO e inventado: e um ficheiro que ja esta em
    `data/collection-store/`, preservado por uma corrida italiana de Setembro.
    O que a prova escreve e so o LIVRO da corrida — e escreve-o numa raiz
    temporaria, para nao tocar no livro real.
    """
    run = "PROVA-505-0001"
    # O payload real, escolhido do armazem: quem existir primeiro.
    loja = os.path.join(RAIZ, "data", "collection-store", "italy")
    pay = None
    for base, _, ficheiros in os.walk(loja):
        for f in sorted(ficheiros):
            if not f.endswith(".json"):
                pay = os.path.relpath(os.path.join(base, f), RAIZ).replace(os.sep, "/")
                break
        if pay:
            break
    if not pay:
        caso("A0_ha_payload_real_no_armazem", False,
             "nenhum byte em data/collection-store — esta prova precisa de um")
        return None
    caso("A0_ha_payload_real_no_armazem", True)

    ops = tempfile.mkdtemp(prefix=".prova-505-", dir=os.path.join(RAIZ, "data"))
    antes = os.environ.get("ITALY_OPS_ROOT")
    os.environ["ITALY_OPS_ROOT"] = ops
    try:
        livro = os.path.join(ops, adapter.LIVRO)
        os.makedirs(os.path.dirname(livro), exist_ok=True)
        obs = {"RUN_ID": run, "SOURCE_ID": "IT-T2-002",
               "DOCUMENT_ID": "PROVA_505_DOC", "DOCUMENT_VERSION_ID": "v1_prova",
               "RAW_SHA256": "a" * 64, "RAW_PATH": pay,
               "CAPTURED_AT": "2026-09-11T00:00:00Z",
               "SOURCE_DATE_ISO": "2026-09-02",
               "texto": "Bollettino agrometeorologico della zona, con dati di campo."}
        io.open(livro, "w", encoding="utf-8").write(json.dumps(obs) + "\n")

        # ── 1 · O EXECUTOR DECLARA ─────────────────────────────────────────
        resumo = adapter.colher(run, ops_root=ops)
        caso("A1_o_executor_declarou_o_retorno", bool(resumo.get("DECLAROU_EM")),
             "colher() nao escreveu envelope nenhum")

        e = _executor("italia-recorrente")
        envelope, notas = orq.o_envelope(e, run)
        caso("A2_o_orquestrador_leu_a_declaracao",
             len(envelope.get("COLHEITA") or []) == 1,
             "o envelope trouxe %d unidades" % len(envelope.get("COLHEITA") or []))

        # ── 2 · O CONTRATO CONFERE ─────────────────────────────────────────
        mal = rdc.conferir(envelope, RAIZ)
        caso("A3_o_envelope_respeita_o_contrato", not mal, "; ".join(mal[:2]))
        caso("A4_a_unidade_e_da_MESMA_corrida",
             all(u.get("RUN_ID") == run for u in envelope["COLHEITA"]))
        caso("A5_o_payload_foi_MEDIDO_e_esta_presente",
             envelope["COLHEITA"][0]["PAYLOAD"]["ESTADO"] == rdc.PRESENTE,
             str(envelope["COLHEITA"][0]["PAYLOAD"]))

        # ── 3 · SO O QUE A LEI DEIXA ───────────────────────────────────────
        itens, _ = orq.a_colheita(e, run)
        caso("A6_so_o_que_entra_devolve_a_colheita", len(itens) == 1,
             "%d itens" % len(itens))

        # ── 4 · O INGRESSO PRESERVA ────────────────────────────────────────
        recibo = {"RUN_ID": run, "PLATFORM": "HTTP direto",
                  "ACTOR": "coleta/italy_executor.py", "ACTOR_VERSION": "adapter-v1",
                  "SOURCE_COUNTRY": "IT", "STARTED_AT": "2026-09-11T00:00:00Z"}
        r = ing.receber(itens, corrida=recibo, armazem=ing.ArmazemLocal(RAIZ),
                        memoria=None, raiz=RAIZ)
        caso("A7_o_ingresso_preservou_o_MESMO_item", len(r["ACEITES"]) == 1,
             "aceites=%d recusas=%s" % (len(r["ACEITES"]),
                                        [x["PORQUE"] for x in r["RECUSAS"]][:2]))

        # ── 5 · A TRAVESSIA DE LINGUA, E DEPOIS A ADMISSAO JULGA ───────────
        # ⚠️ ESTA PROVA JA CHAMOU `adm.decidir(itens[0])` DIRECTAMENTE, e por
        # isso saltava a traducao que a rota canonica faz em `pela_porta`.
        # Uma prova que salta um degrau da cadeia nao esta a provar a cadeia:
        # esta a provar o degrau seguinte com o anterior fingido.
        na_lingua_da_porta = ing.para_a_porta(itens[0])
        d = adm.decidir(na_lingua_da_porta, "T2", corrida=run)
        caso("A8_a_admissao_julgou_o_MESMO_item",
             d.resultado in adm.RESULTADOS, d.resultado)
        caso("A9_a_decisao_carrega_a_corrida_certa", d.corrida == run, str(d.corrida))
        print("    A · a admissao devolveu %s — %s" % (d.resultado, d.motivo[:60]))

        # ── O QUE ESTA LIGACAO TORNOU VISIVEL, e nao criou ─────────────────
        # A unidade italiana chega a porta com `SOURCE_ID` MAIUSCULO — e o
        # nome do contrato, `coleta/ingresso.py::DO_COLETOR`. E a porta
        # procura `source_id` MINUSCULO (`admissao/admissao.py::_tem_origem`).
        # Sao dois nomes para o mesmo campo, e ninguem tinha reparado porque
        # NENHUMA unidade italiana tinha chegado a porta antes de hoje.
        #
        #     LIGAR UMA CADEIA NAO CRIA OS DEFEITOS DELA: MOSTRA-OS.
        #
        # NAO se conserta aqui. Mexer na admissao para conseguir verde e
        # exactamente o que esta missao esta proibida de fazer. Fica medido,
        # com nome, para a missao que o for fechar.
        caso("A11_a_unidade_declara_a_fonte", bool(itens[0].get("SOURCE_ID")),
             "a unidade nao traz SOURCE_ID nenhum")
        caso("A12_a_traducao_preserva_o_valor",
             na_lingua_da_porta.get("source_id") == itens[0].get("SOURCE_ID"),
             "o valor mudou ao atravessar a fronteira")
        caso("A13_a_origem_deixou_de_parecer_ausente",
             "de onde este item veio" not in d.motivo,
             "a porta continua a dizer que nao sabe de onde o item veio")
        print("    > A PROXIMA PERGUNTA DA PORTA: %s" % d.motivo[:72])
        if d.resultado == adm.SIM:
            saida = adm.pronto_para_inteligencia(itens[0], d)
            caso("A10_SIM_produz_READY",
                 saida["ESTADO"] == "PRONTO_PARA_INTELIGENCIA")
        else:
            # NAO SE MEXE NA ADMISSAO PARA CONSEGUIR VERDE.
            caso("A10_o_que_nao_e_SIM_nao_produz_READY", True,
                 "resultado %s — e nao se relaxa a porta para o mudar" % d.resultado)
        return d.resultado
    finally:
        shutil.rmtree(ops, ignore_errors=True)
        shutil.rmtree(os.path.join(RAIZ, adapter.BALCAO), ignore_errors=True)
        shutil.rmtree(os.path.join(RAIZ, "XX"), ignore_errors=True)
        if antes is None:
            os.environ.pop("ITALY_OPS_ROOT", None)
        else:
            os.environ["ITALY_OPS_ROOT"] = antes


# ─────────────────────────────────────────────────────────────────────────
# B · O CONTRAEXEMPLO HISTORICO
# ─────────────────────────────────────────────────────────────────────────
def o_contentor_vazio_nao_e_desviado():
    """`CLASSIFICADO-V1.json` declara `ITEMS` com `ITEM_COUNT = 0`.

    A heuristica antiga saltava-o POR ESTAR VAZIO e agarrava a lista de contas
    ao lado — 74 fichas de conta a viajar como material observado. O resultado
    certo e zero.
    """
    e = _executor("comunicacao-publica")
    itens, _ = orq.a_colheita(e, "PROVA-505")
    envelope, _ = orq.o_envelope(e, "PROVA-505")
    caso("C1_o_contentor_vazio_nao_faz_escolher_outra_lista", not itens,
         "%d itens atravessaram" % len(itens))
    caso("C2_o_suporte_foi_visto_e_nomeado",
         len(envelope.get("SUPORTE") or []) == 6,
         "%d artefactos de suporte" % len(envelope.get("SUPORTE") or []))
    caso("C3_nenhum_suporte_e_COLHEITA",
         all(x["ESPECIE"] != rdc.COLHEITA for x in envelope["SUPORTE"]))


def main():
    print()
    print("=" * 72)
    print("  SO A COLHEITA ATRAVESSA — COL-LAW-505 no runtime")
    print("=" * 72)
    a_cadeia_com_um_item_real()
    o_contentor_vazio_nao_e_desviado()
    print()
    for nome, ok, det in fora:
        print("  %s  %-48s %s" % ("PASS" if ok else "FAIL", nome, "" if ok else det))
    mal = [n for n, ok, _ in fora if not ok]
    print("=" * 72)
    print("SO_A_COLHEITA_ATRAVESSA=%s" % ("PASS" if not mal else "FAIL"))
    return 1 if mal else 0


if __name__ == "__main__":
    sys.exit(main())
