# -*- coding: utf-8 -*-
"""A IMPRESSAO DIGITAL DO CONTRATO QUE O ROBO VAI USAR — uma so, para quem prova e para quem onboarda.

    PROVAR UM CONTRATO E ONBOARDAR OUTRO E PIOR DO QUE NAO PROVAR NADA.

MEDIDO (MICRO-PRONTO, 25/09/2026): `medidas/canario_rotas_elegiveis.py` lia os
contratos por `git show HEAD:curadoria/italy_contracts_curator.json`, e o bot
escreve no DISCO e nao commita. No vivo, HEAD tinha 574 fontes e o disco 762;
das 17 fontes que a ponte ia onboardar, 14 tinham no HEAD uma aquisicao
diferente (ou nenhuma). O canario provaria a rota de um contrato e a tabela do
coletor receberia outro — com a prova a dizer ROUTE_PROVEN.

O QUE ENTRA NA IMPRESSAO. Exactamente o que `onboardar_rotas_provadas.linha_da_tabela`
escreve na tabela do coletor e o coletor usa (`regras/italy_contracts.mjs`,
`contratoGenerico`): o SOURCE_ID, o OUTPUT_TYPE e a ACQUISITION inteira. Campos
do curador que o coletor nao le (evidencias, notas, datas de caracterizacao)
ficam de fora de proposito: mudarem nao muda a rota, e nao devem obrigar a
reprovar.

A forma canonica e JSON com chaves ordenadas e sem espacos — o mesmo contrato
da sempre a mesma impressao, venha de onde vier (disco, Git, memoria).
"""
from __future__ import annotations

import hashlib
import json

CAMPOS = ("SOURCE_ID", "OUTPUT_TYPE", "ACQUISITION")


def do_contrato(contrato: dict) -> str:
    """sha256 da parte do contrato que o coletor vai executar."""
    parte = {k: (contrato or {}).get(k) for k in CAMPOS}
    texto = json.dumps(parte, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    return hashlib.sha256(texto.encode("utf-8")).hexdigest()
