#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""AS 85 OUTRA VEZ PELA PORTA CANONICA — com as duas portas abertas.

    REPROCESSAR NAO E COLHER.
    E A COLHEITA NAO E «A QUE ESTIVER LA»: ELA TEM DE SE NOMEAR.

A `CANONICAL-MICRO` e a `LAST-MILE` levaram 85 documentos italianos a porta.
`raw_asset` cresceu 87, `storage_object` cresceu 85 — e a Sala ficou em 46,
com DUAS causas nomeadas:

    MISSING_ROUTE                     46 itens · nenhum executor abria text/html
    NO_ADMISSION_RULE_FOR_UNIVERSE    39 itens · T10 nao tinha regua

As duas fecharam. Este ficheiro leva os MESMOS 85 pela MESMA porta e mede o que
muda — sem rede, e sem escrever uma unica linha por fora da cadeia.

O QUE ELE FAZ, PASSO A PASSO
-----------------------------
1. RECONSTROI O BALCAO. `data/colheita/` esta no `.gitignore` e os envelopes da
   RUN1C ja nao existem em disco. Quem os refaz e o DONO —
   `coleta/italy_executor.colher(run_id)` — relendo
   `data/collection-ledger/italy/observations.ndjson`, que esta no Git com as
   85 observacoes. Nada e inventado: o envelope volta a declarar o que a
   corrida declarou, e `leis/retorno_da_coleta.conferir()` confere o `sha256`
   contra os bytes no armazem.

2. CHAMA A PORTA. `orquestrador.main()`, com `--so-a-porta` e
   `--colheita-da-corrida=<RUN_ID>`: nao se colhe nada, leva-se a peneira uma
   colheita que JA existe, e a corrida NOVA julga de novo.

3. CONTA A REDE. Tudo corre DENTRO de um processo remendado por
   `medidas/corrida_sem_rede.instrumentar()` — o mesmo instrumento da missao
   anterior, importado e nao copiado. `NETWORK_REQUESTS` tem de ser 0.

O QUE ELE NAO FAZ
-----------------
Nao escreve na Sala. Quem escreve e `admissao/sala_de_espera.py`, chamado por
`orquestrador.pela_porta` depois de a Admissao dizer `SIM`. Aqui nao ha
`INSERT`, nao ha SQL, nao ha fixture e nao ha bypass.

CORRER
------
    SINTONIA_COLLECTION_DSN=... py medidas/duas_portas_reprocessa.py

SAIDA: medidas/DUAS-PORTAS-REPROCESSAMENTO-V1.json
"""

from __future__ import annotations

import json
import os
import sys
import time

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if RAIZ not in sys.path:
    sys.path.insert(0, RAIZ)

import _gavetas  # noqa: E402,F401

SAIDA = os.path.join(RAIZ, "medidas", "DUAS-PORTAS-REPROCESSAMENTO-V1.json")

# ── AS SEIS CORRIDAS DA RUN1C, COM A FONTE E O UNIVERSO DE CADA UMA ─────────
# ⚠️ O UNIVERSO VEM DO PEDIDO, E NAO DO `SOURCE_ID`. Ele esta escrito aqui
# porque e ESTE ficheiro que faz o pedido — e `IT-T10-018` ter um `T10` no nome
# nao e uma declaracao de universo, e uma coincidencia de nomenclatura que ja
# enganou esta casa antes (`ALVO != UNIVERSO`).
#
# A FRASE tem de conter um apelido que `pedido/pedido.py::alvo_de` conheca: a
# linha de comandos junta os argumentos soltos numa frase so, e `fonte=...`
# entraria la dentro. «mercado», «cooperativa» e «ciencia» sao os apelidos que
# `leis/territorios.py::APELIDOS` mapeia para T10, T7 e T5.
CORRIDAS = [
    {"RUN_ID": "IT-T10-2026-09-21-192602-b9c48c5e22f8a0a0",
     "FONTE": "IT-T10-018", "UNIVERSO": "T10", "FRASE": "mercado",
     "OBSERVACOES": 30},
    {"RUN_ID": "IT-T10-2026-09-21-192736-2be29d10cb1d23e4",
     "FONTE": "IT-T10-022", "UNIVERSO": "T10", "FRASE": "mercado",
     "OBSERVACOES": 9},
    {"RUN_ID": "IT-T5-2026-09-21-192807-551e1a130e552533",
     "FONTE": "IT-T5-049", "UNIVERSO": "T5", "FRASE": "ciencia",
     "OBSERVACOES": 4},
    {"RUN_ID": "IT-T7-2026-09-21-192819-b486bc9baf0577d0",
     "FONTE": "IT-T7-017", "UNIVERSO": "T7", "FRASE": "cooperativa",
     "OBSERVACOES": 30},
    {"RUN_ID": "IT-T7-2026-09-21-193015-aae482dfd4ef8cbe",
     "FONTE": "IT-T7-042", "UNIVERSO": "T7", "FRASE": "cooperativa",
     "OBSERVACOES": 10},
    {"RUN_ID": "IT-T7-2026-09-21-193046-344a587db4870ed8",
     "FONTE": "IT-T7-043", "UNIVERSO": "T7", "FRASE": "cooperativa",
     "OBSERVACOES": 2},
]


def reconstruir_o_balcao(corrida):
    """O envelope desta corrida, refeito pelo DONO a partir do livro."""
    from coleta import italy_executor as ix              # noqa: PLC0415
    return ix.colher(corrida["RUN_ID"], raiz=RAIZ)


def pela_porta(corrida):
    """A porta canonica, com o universo declarado. Devolve o codigo de saida."""
    # A gaveta ja poe `orquestrador/` no caminho: o nome do MODULO e
    # `orquestrador`, e nao `orquestrador.orquestrador` — o pacote e o ficheiro
    # tem o mesmo nome e o segundo ganha.
    import orquestrador as orq                           # noqa: PLC0415
    sys.argv = ["orquestrador/orquestrador.py",
                corrida["FRASE"],
                "--so-a-porta",
                "--colheita-da-corrida=%s" % corrida["RUN_ID"],
                "--filtro", "fonte=%s" % corrida["FONTE"],
                "--filtro", "universo=%s" % corrida["UNIVERSO"]]
    try:
        return orq.main(), None
    except SystemExit as ex:
        return int(ex.code or 0), None
    except Exception as ex:                              # noqa: BLE001
        import traceback
        traceback.print_exc()
        return 1, "%s: %s" % (type(ex).__name__, ex)


def a_sala_esta_canonica():
    """A Sala deste processo e a canonica? → a ficha do dono dela.

    ⚠️ ESTA GUARDA NASCEU DE UM ERRO MEU, E FICA ESCRITA PARA NAO SE REPETIR.
    A primeira corrida desta missao atravessou a estrada inteira — `DERIVED
    +74`, `STRUCTURED +74`, `ADMISSION` com **10 SIM** — e a Sala ficou em 46.
    Nada tinha falhado: `admissao/sala_de_espera.py` corre no backend
    `FICHEIRO` por omissao, que ele proprio declara `CANONICO: False` («o
    ficheiro vive no workspace do runner: nao sobrevive ao job»). Os dez
    pousaram num disco efemero.

        UMA CORRIDA QUE DIZ `SUCCESS` COM A SALA NO BACKEND ERRADO
        NAO ESCREVEU NA SALA — E NAO SE QUEIXOU.

    O dono ja tinha a resposta pronta (`estado_operacional()`) e o portao
    (`exigir_canonica()`); faltava alguem PERGUNTAR antes de gastar a corrida.
    """
    import sala_de_espera as espera                      # noqa: PLC0415
    return espera.estado_operacional()


def main(argv):
    import corrida_sem_rede as csr                       # noqa: PLC0415

    # O instrumento e o da missao anterior, IMPORTADO. Uma segunda copia dos
    # remendos seria um segundo dono da mesma medicao.
    csr.instrumentar()

    sala = a_sala_esta_canonica()
    print("SALA: %s · CANONICO=%s · %s"
          % (sala["BACKEND"], sala["CANONICO"], sala["PORQUE"][:90]))
    if not sala["CANONICO"] and "--aceito-sala-nao-canonica" not in argv:
        print("\nRECUSADO: a Sala deste processo nao e a canonica. Declare\n"
              "  SINTONIA_SALA_BACKEND=POSTGRES e SINTONIA_SALA_DSN=...\n"
              "Nada foi corrido. Uma corrida que admite para um disco efemero\n"
              "gasta a estrada inteira e nao deixa a linha que interessa.")
        return 2

    fora = []
    for c in CORRIDAS:
        t0 = time.time()
        print("\n" + "=" * 70)
        print("%s · %s · universo %s" % (c["RUN_ID"], c["FONTE"],
                                         c["UNIVERSO"]))
        balcao = reconstruir_o_balcao(c)
        print("  balcao refeito: %d observacoes -> %s"
              % (balcao["OBSERVACOES_DESTA_CORRIDA"], balcao["DECLAROU_EM"]))
        codigo, erro = pela_porta(c)
        fora.append({**c,
                     "BALCAO": balcao,
                     "CODIGO_DE_SAIDA": codigo,
                     "ERRO": erro,
                     "SEGUNDOS": round(time.time() - t0, 1)})

    censo = {
        "MEDIDOR": "medidas/duas_portas_reprocessa.py",
        "INSTRUMENTO": "medidas/corrida_sem_rede.py (importado)",
        "ESCREVE_NA_SALA_DIRECTAMENTE": False,
        "SALA": sala,
        "CORRIDAS": fora,
        "NETWORK_ALLOWED": False,
        "NETWORK_REQUESTS": len(csr.CENSO["EGRESS_ATTEMPTS"]),
        "EGRESS_ATTEMPTS": csr.CENSO["EGRESS_ATTEMPTS"],
        "DNS_LOOKUPS_FORA": len(csr.CENSO["DNS_LOOKUPS"]),
        "DNS_DETALHE": csr.CENSO["DNS_LOOKUPS"][:20],
        "LOOPBACK_CONNECTS": len(csr.CENSO["LOOPBACK_CONNECTS"]),
        "LOOPBACK_PORTOS": sorted({x["PORTO"] for x in
                                   csr.CENSO["LOOPBACK_CONNECTS"]
                                   if x["PORTO"]}),
        "SUBPROCESSOS": len(csr.CENSO["SUBPROCESSOS"]),
        "SUBPROCESSOS_DETALHE": csr.CENSO["SUBPROCESSOS"][:20],
    }
    with open(SAIDA, "w", encoding="utf-8") as fh:
        json.dump(censo, fh, indent=1, ensure_ascii=False, default=str)

    print("\n=== CENSO DA REDE ===")
    for k in ("NETWORK_REQUESTS", "DNS_LOOKUPS_FORA", "LOOPBACK_CONNECTS",
              "LOOPBACK_PORTOS", "SUBPROCESSOS"):
        print("  %-22s %s" % (k, censo[k]))
    for t in censo["EGRESS_ATTEMPTS"][:5]:
        print("  !! EGRESSO %s:%s" % (t["HOST"], t["PORTO"]))
    print("  escrito: %s" % SAIDA)
    return 0 if censo["NETWORK_REQUESTS"] == 0 else 3


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
