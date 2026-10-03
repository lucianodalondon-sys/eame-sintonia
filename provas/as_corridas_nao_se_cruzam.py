#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""DUAS CORRIDAS DO MESMO EXECUTOR CRUZAM-SE?

    python3 provas/as_corridas_nao_se_cruzam.py

A PERGUNTA
----------
    UMA CORRIDA PODE CONSUMIR O QUE OUTRA CORRIDA PRODUZIU,
    SEM QUE NINGUEM DE POR ISSO?

`G-ENV-01` foi medido em `C-T4-CANONICAL-ACQUISITION-TO-WAITING-ROOM-V1` e
ficou escrito como divida: o envelope — o sitio onde a corrida DECLARA o que
produziu — vive num caminho por EXECUTOR, e nao por CORRIDA. Duas corridas do
mesmo executor escrevem no mesmo ficheiro.

    UM ENVELOPE POR EXECUTOR NAO E UM ENVELOPE POR CORRIDA.

Em serie nao morde: cada corrida escreve e o orquestrador le a seguir. Esta
prova existe para medir o que acontece quando elas NAO sao em serie — e para
continuar a medi-lo depois de corrigido.

O QUE ELA NAO FAZ
-----------------
Nao vai a rede. A colisao e de ENDERECO, e nao de bytes: prova-se chamando o
dono da declaracao com duas corridas diferentes e perguntando ao orquestrador
de quem e o que ele encontrou.

    UMA PROVA QUE PRECISA DA INTERNET PARA MEDIR UM CAMINHO
    ESTA A MEDIR A INTERNET.
"""
import io
import json
import os
import sys
import threading

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)
import _gavetas  # noqa: E402,F401

import orquestrador as orq                                  # noqa: E402
import retorno_da_coleta as rdc                             # noqa: E402
from receitas import EXECUTORES                             # noqa: E402

fora = []


def caso(nome, condicao, detalhe=""):
    fora.append((nome, bool(condicao), detalhe))


def _executores_com_envelope():
    """Todos os que declaram ENVELOPE — e nao so o que me lembrei de testar.

    ⚠️ UMA PROVA QUE NOMEIA UM EXECUTOR MEDE UM EXECUTOR. A propriedade e do
    CONTRATO, e por isso a lista sai do registo.
    """
    fora_ = []
    for universo, lista in sorted(EXECUTORES.items()):
        for e in lista:
            if (e.get("retorno") or {}).get("ENVELOPE"):
                fora_.append((universo, e))
    return fora_


def _envelope_falso(run_id, marca):
    """Um envelope minimo e VALIDO, com a corrida dentro dele.

    Nao se escreve lixo: um envelope mal formado seria recusado pelo contrato,
    e entao a prova mediria a recusa em vez da colisao de endereco.
    """
    return {"RUN_ID": run_id, "EXECUTOR_ID": marca,
            "EXECUTOR_VERSION": "prova", "ESTADO": rdc.SUCCESS,
            "COLHEITA": [], "SUPORTE": [], "ERROS": []}


def _escrever(caminho, dados):
    alvo = os.path.join(RAIZ, caminho)
    os.makedirs(os.path.dirname(alvo), exist_ok=True)
    with io.open(alvo, "w", encoding="utf-8") as fh:
        json.dump(dados, fh, ensure_ascii=False, indent=1)


def main():
    print("=" * 70)
    print("AS CORRIDAS CRUZAM-SE? — medicao de endereco, sem rede")
    print("=" * 70)

    com_envelope = _executores_com_envelope()
    caso("E0_ha_executores_com_ENVELOPE_para_medir", bool(com_envelope),
         "executores que declaram ENVELOPE: %s"
         % [e["id"] for _u, e in com_envelope])

    guardados = []
    for _u, e in com_envelope:
        padrao = e["retorno"]["ENVELOPE"]
        for run_id in ("CORRIDA-A", "CORRIDA-B"):
            alvo = os.path.join(RAIZ, rdc.endereco_do_envelope(padrao, run_id))
            if os.path.isfile(alvo):
                with io.open(alvo, encoding="utf-8") as fh:
                    guardados.append((alvo, fh.read()))
                os.unlink(alvo)

    try:
        for universo, e in com_envelope:
            ident = e["id"]
            padrao = e["retorno"]["ENVELOPE"]

            # ── DUAS CORRIDAS DECLARAM, UMA A SEGUIR A OUTRA ──────────────
            a = rdc.endereco_do_envelope(padrao, "CORRIDA-A")
            b = rdc.endereco_do_envelope(padrao, "CORRIDA-B")
            caso("E1_%s_o_endereco_do_envelope_MUDA_com_a_corrida" % ident,
                 a != b,
                 "A=%s · B=%s" % (a, b))

            _escrever(a, _envelope_falso("CORRIDA-A", "marca-A"))
            _escrever(b, _envelope_falso("CORRIDA-B", "marca-B"))

            env_a, _n = orq.o_envelope(e, "CORRIDA-A")
            env_b, _n = orq.o_envelope(e, "CORRIDA-B")
            caso("E2_%s_cada_corrida_recebe_O_SEU_envelope" % ident,
                 env_a.get("RUN_ID") == "CORRIDA-A"
                 and env_b.get("RUN_ID") == "CORRIDA-B",
                 "A recebeu %s · B recebeu %s"
                 % (env_a.get("RUN_ID"), env_b.get("RUN_ID")))

            # ── UMA CORRIDA SEM ENVELOPE NAO HERDA O DE NINGUEM ───────────
            # ⚠️ ESTE E O CASO QUE `G-ENV-01` FALHAVA.
            # Antes, perguntar pela colheita de uma corrida que nunca escreveu
            # devolvia a colheita da ULTIMA que escreveu — sem nota nenhuma.
            #
            #     NAO CORREU != CORREU E NAO DEU NADA.
            #     E NENHUM DOS DOIS E «PEGUEI O QUE ESTAVA LA».
            env_c, notas = orq.o_envelope(e, "CORRIDA-QUE-NUNCA-CORREU")
            itens_c, notas_c = orq.a_colheita(e, "CORRIDA-QUE-NUNCA-CORREU")
            caso("E3_%s_corrida_sem_envelope_NAO_recebe_o_de_outra" % ident,
                 env_c.get("RUN_ID") not in ("CORRIDA-A", "CORRIDA-B")
                 and not itens_c,
                 "recebeu RUN_ID=%s · itens=%d · notas=%s"
                 % (env_c.get("RUN_ID"), len(itens_c),
                    (notas_c or "(nenhuma)")[:60]))
            caso("E3b_%s_e_a_ausencia_e_DITA_e_nao_calada" % ident,
                 bool(notas) or bool(notas_c),
                 "notas: %s" % ((notas or notas_c or "(nenhuma)")[:80]))

            # ── E EM PARALELO ────────────────────────────────────────────
            # ⚠️ ESCREVER A SEGUIR NAO E ESCREVER AO MESMO TEMPO.
            # O caso de cima ja passaria com um endereco por corrida escrito
            # em serie. Aqui os dois fios escrevem juntos, que e o que a
            # coleta grande vai fazer.
            resultados = {}

            def declara_e_le(run_id, marca):
                _escrever(rdc.endereco_do_envelope(padrao, run_id),
                          _envelope_falso(run_id, marca))
                env, _x = orq.o_envelope(e, run_id)
                resultados[run_id] = env.get("EXECUTOR_ID")

            fios = [threading.Thread(target=declara_e_le,
                                     args=("PAR-%d" % i, "marca-%d" % i))
                    for i in range(4)]
            for f in fios:
                f.start()
            for f in fios:
                f.join()
            certos = [r for r in resultados
                      if resultados[r] == "marca-%s" % r.split("-")[1]]
            caso("E4_%s_quatro_corridas_em_PARALELO_nao_se_cruzam" % ident,
                 len(certos) == 4,
                 "cada fio recebeu a sua marca: %d de 4 · %s"
                 % (len(certos), resultados))

            for i in range(4):
                alvo = os.path.join(
                    RAIZ, rdc.endereco_do_envelope(padrao, "PAR-%d" % i))
                if os.path.isfile(alvo):
                    os.unlink(alvo)
            for caminho in (a, b):
                alvo = os.path.join(RAIZ, caminho)
                if os.path.isfile(alvo):
                    os.unlink(alvo)
    finally:
        for alvo, conteudo in guardados:
            os.makedirs(os.path.dirname(alvo), exist_ok=True)
            with io.open(alvo, "w", encoding="utf-8") as fh:
                fh.write(conteudo)

    print()
    for nome, ok, detalhe in fora:
        print("  %-5s %-56s %s" % ("PASS" if ok else "FALHA", nome,
                                   str(detalhe)[:64]))
    print("=" * 70)
    inteiro = all(ok for _n, ok, _d in fora)
    print("CORRIDAS_NAO_SE_CRUZAM=%s" % ("PASS" if inteiro else "FAIL"))
    return 0 if inteiro else 1


if __name__ == "__main__":
    raise SystemExit(main())
