#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""A ROTA DO HTML NAO ABRE LIGACAO NENHUMA — medido, nao prometido.

    UMA ETAPA QUE PROMETE NAO IR A REDE
    NAO E UMA MEDICAO DE QUE NAO FOI.

`coleta/texto_fonte.py` TEM um cliente de rede la dentro (`_bruto`, com
`urllib`) — ele serve o `main()` de linha de comandos. O executor de HTML
importa dali SO a `limpar()`, que nao abre socket nenhum. Isto parece obvio e
nao e: a funcao esta no MESMO ficheiro que sabe ir a internet, e um dia
alguem pode achar comodo ir buscar o documento em falta.

Esta prova corre a extracao DENTRO do processo remendado por
`medidas/corrida_sem_rede.instrumentar()` — o mesmo instrumento da missao
anterior — e exige `NETWORK_REQUESTS = 0`.

    py provas/a_rota_do_html_nao_vai_a_rede.py
"""
from __future__ import annotations

import json
import os
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if RAIZ not in sys.path:
    sys.path.insert(0, RAIZ)
if os.path.join(RAIZ, "medidas") not in sys.path:
    sys.path.insert(0, os.path.join(RAIZ, "medidas"))

#: Bytes reais, do armazem, do canario da missao. Um HTML inventado nao
#: exercitaria o tamanho nem a forma que a fonte publica de verdade.
CANARIO = ("data/collection-store/italy/IT-T5-049/"
           "IT-T5-049_URL_it_notizie_welcome-day-1/"
           "v1_70ae4c4a6eed/welcome-day-1.html")


def main():
    import corrida_sem_rede as csr                       # noqa: PLC0415
    csr.instrumentar()

    # ⚠️ O `import` VEM DEPOIS DO REMENDO, de proposito: uma ligacao aberta no
    # momento do `import` tambem tem de ser apanhada.
    sys.path.insert(0, RAIZ)
    import _gavetas                                      # noqa: E402,F401,PLC0415
    import executor_texto_de_html as html                # noqa: E402,PLC0415

    caminho = os.path.join(RAIZ, CANARIO)
    fora = {"PROVA": "provas/a_rota_do_html_nao_vai_a_rede.py",
            "FICHEIRO": CANARIO, "EXISTE": os.path.isfile(caminho)}
    if not fora["EXISTE"]:
        fora["VEREDICTO"] = "FAIL: os bytes do canario nao estao no disco"
        print(json.dumps(fora, ensure_ascii=False, indent=1))
        return 1

    apanhado = None
    try:
        with open(caminho, "rb") as fh:
            texto, estado, erro, medidas = html.extrair(fh.read())
    except csr.RedeProibida as ex:
        apanhado = str(ex)[:300]
        texto, estado, erro, medidas = "", "REDE", apanhado, {}

    fora.update({
        "ESTADO": estado,
        "CARACTERES": len(texto),
        "MEDIDAS": medidas,
        "REDE_APANHADA": apanhado,
        "NETWORK_REQUESTS": len(csr.CENSO["EGRESS_ATTEMPTS"]),
        "EGRESS_ATTEMPTS": csr.CENSO["EGRESS_ATTEMPTS"][:5],
        "DNS_LOOKUPS_FORA": len(csr.CENSO["DNS_LOOKUPS"]),
        "SUBPROCESSOS": len(csr.CENSO["SUBPROCESSOS"]),
    })
    # Os tres, escritos a mao: nao houve egresso, nao houve DNS, e a extracao
    # produziu texto de verdade. Sem o terceiro, uma extracao que nao correu
    # passaria por «nao foi a rede».
    ok = (fora["NETWORK_REQUESTS"] == 0
          and fora["DNS_LOOKUPS_FORA"] == 0
          and estado == "TEXT_LAYER_PRESENT"
          and fora["CARACTERES"] > 0)
    fora["VEREDICTO"] = "PASS" if ok else "FAIL"
    print(json.dumps(fora, ensure_ascii=False, indent=1))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
