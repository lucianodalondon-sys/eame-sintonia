# -*- coding: utf-8 -*-
"""O PORTAO DA REGUA T2 DESDE A D29 — as condicoes num sitio so.

Lido pelas duas guardas que decidem se `T2` pode ter regra escrita
(`tests/test_a_regra_de_t2.py`, `tests/test_o_canario_da_collection.py`).
"""
import json
import os

MEDICAO = os.path.join(os.path.dirname(os.path.abspath(__file__)), "MEDICAO-REGUA-T2-V2.json")


def medicao_d29():
    if not os.path.isfile(MEDICAO):
        return None
    with open(MEDICAO, encoding="utf-8") as h:
        return json.load(h)


def aberto(m) -> bool:
    """Gabarito >= 20/20, sha a bater, vizinhos intactos, precisao e recall >= 0.8
    no gabarito (medidos DENTRO da amostra — ver a medicao)."""
    if not m:
        return False
    t = m["T2"]
    return (t["OURO_YES"] >= 20 and t["OURO_NO"] >= 20 and not m["SHA_NAO_CONFERE"]
            and m["VIZINHOS"]["VEREDITOS_VIZINHOS_MUDADOS"] == 0
            and (t["PRECISAO"] or 0) >= 0.8 and (t["RECALL"] or 0) >= 0.8)
