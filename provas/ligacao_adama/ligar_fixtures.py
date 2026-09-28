#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""AJUSTE DECLARADO DE FIXTURE (LIGACAO-ADAMA, D123 do dono, 27/09/2026).

O pote passou a recusar objeto sem LIGACAO_ADAMA. As corridas SINTETICAS de tests/fixtures/pote/
nao tem referencia ADAMA (sao sinteticas: nenhum valor e real), e por isso cada objeto recebe a
ligacao que a PORTA da a quem nao tem referencia: NAO_SEI · FALTA=REFERENCIA — calculada pela
porta (motor/porta_da_referencia.ligacao_adama), nunca escrita a mao. Nenhum outro campo muda.

    python3 provas/ligacao_adama/ligar_fixtures.py           # reescreve as duas corridas
    python3 provas/ligacao_adama/ligar_fixtures.py --conferir # sai 1 se alguma nao estiver ligada

Os potes sinteticos (POTE-SINTETICO*.json) regeneram-se DEPOIS pelo comando que os testes K2 citam.
A corrida R6-equivalente e gerada por provas/pote_v2/medir_recusas_r6.py (que chama `ligacao_sintetica`).
"""
import json
import os
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(RAIZ, "motor"))
import porta_da_referencia as PORTA  # noqa: E402

CORRIDAS = ("tests/fixtures/pote/CORRIDA-SINTETICA-POTE.json",
            "tests/fixtures/pote/CORRIDA-SINTETICA-V2-UNICO.json")


def ligacao_sintetica() -> dict:
    """A ligacao de um objeto de corrida SINTETICA: a porta sem referencia -> NAO_SEI/REFERENCIA."""
    return PORTA.ligacao_adama(None, {"VEM_DE": {}})


def ligar(corrida: dict) -> int:
    n = 0
    for objs in (corrida.get("ITENS_POR_FERRAMENTA") or {}).values():
        for o in (objs if isinstance(objs, list) else [objs]):
            if isinstance(o, dict) and "LIGACAO_ADAMA" not in o:
                o["LIGACAO_ADAMA"] = ligacao_sintetica()
                n += 1
    return n


def main(argv=None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    faltam = 0
    for rel in CORRIDAS:
        p = os.path.join(RAIZ, rel)
        with open(p, encoding="utf-8") as f:
            texto = f.read()
        c = json.loads(texto)
        n = ligar(c)
        faltam += n
        if "--conferir" not in argv and n:
            with open(p, "w", encoding="utf-8") as f:
                f.write(json.dumps(c, ensure_ascii=False, indent=1) + ("\n" if texto.endswith("\n") else ""))
        print(f"{rel}: {n} objetos ligados agora")
    return 1 if ("--conferir" in argv and faltam) else 0


if __name__ == "__main__":
    sys.exit(main())
