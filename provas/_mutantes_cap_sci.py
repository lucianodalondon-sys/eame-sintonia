#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""MUTACAO DA CAP-SCI — cada regra da capacidade tem um teste que a apanha.

    python3 provas/_mutantes_cap_sci.py

Planta um defeito de cada vez em `motor/capacidade_cientifica.py`, corre
`tests.test_capacidade_cientifica` e exige que ele REPROVE. Restaura sempre o
original (finally), mesmo se for interrompido. Sai 1 se algum mutante viver.

Um teste que continua verde com a regra partida nao prova a regra.
"""
import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
P = RAIZ / "motor" / "capacidade_cientifica.py"; ORIG = P.read_text()
M = [
 ("M01 campo fora do READY ignorado", 'if sobra:\n        raise', 'if False:\n        raise'),
 ("M02 local sem base ancora", 'if CORRIDA.base_ignorante(base):\n        return {"VALOR": NAO_SEI, "ESTADO": "NAO_SEI",\n                "PORQUE": "FACT_LOCATION sem base', 'if False:\n        return {"VALOR": NAO_SEI, "ESTADO": "NAO_SEI",\n                "PORQUE": "FACT_LOCATION sem base'),
 ("M03 publicacao vira periodo", 'v, base = item.get("FACT_TIME"), item.get("FACT_TIME_BASIS")', 'v, base = (item.get("FACT_TIME") if not CORRIDA.e_ignorancia(item.get("FACT_TIME")) else item.get("PUBLISHED_AT")), "PUB · ESCRITO"'),
 ("M04 afiliacao vira local", 'v, base = item.get("FACT_LOCATION"), item.get("FACT_LOCATION_BASIS")', 'v, base = (item.get("FACT_LOCATION") if not CORRIDA.e_ignorancia(item.get("FACT_LOCATION")) else _fato(item).get("affiliation")), (item.get("FACT_LOCATION_BASIS") if not CORRIDA.e_ignorancia(item.get("FACT_LOCATION")) else "AFILIACAO")'),
 ("M05 estudo pequeno nao rebaixa", 'N_PEQUENO = 4', 'N_PEQUENO = 0'),
 ("M06 pequeno/negativo vira conclusao", 'if f["NIVEL"] in (NAO_SEI, INDICATIVA):', 'if False:'),
 ("M07 ensaio nao agrupa", '"TRIAL": [trial] if trial != NAO_SEI else [],', '"TRIAL": [],'),
 ("M08 dataset nao agrupa", '"DATASET": _lista(dataset),', '"DATASET": [],'),
 ("M09 sem chave conta como independente", 'if str(e["ITEM_ID"]) not in sem_chave}', '}'),
 ("M10 rotulo revogado liga", 'if r.get("ADMIN_ACTIVE") is True}', '}'),
 ("M11 metalaxyl vira metalaxyl-M", '"METALAXIL": "METALAXYL",', '"METALAXIL": "METALAXYL", "METALAXYL": "METALAXYL-M",'),
 ("M12 liga sem molecula", 'for k in ("CULTURA", "PROBLEMA", "MOLECULA") if e[k] == NAO_SEI]', 'for k in ("CULTURA", "PROBLEMA") if e[k] == NAO_SEI]'),
 ("M13 candidata sem local/periodo", 'completo = (e["LOCAL_DO_ESTUDO"]["ESTADO"] == "PROVADO"', 'completo = True or (e["LOCAL_DO_ESTUDO"]["ESTADO"] == "PROVADO"'),
 ("M14 especie lida do texto", '    if v == NAO_SEI:\n        return NAO_SEI, "o estudo nao declara especie', '    if v == NAO_SEI and "RESIST" in json.dumps(fato).upper() + "RESIST":\n        return ESPECIE_RESISTENCIA, "texto"\n    if v == NAO_SEI:\n        return NAO_SEI, "o estudo nao declara especie'),
 ("M15 model rule liga a produto", 'if e["ESPECIE"] != ESPECIE_MODELO]', ']'),
 ("M16 sem n passa de fraca", 'nivel = _NIVEL[min(degrau, 1)]', 'nivel = _NIVEL[degrau]'),
 ("M17 ignora uso da corrida", 'if l is None or USO_EXIGIDO not in l.get("USOS_DISPONIVEIS", []):', 'if l is None:'),
 ("M18 trava de leitura desligada", 'if sujo:\n        raise LeiViolada("a CAP-SCI ia escrever', 'if False:\n        raise LeiViolada("a CAP-SCI ia escrever'),
 ("M19 semelhanca vira equivalencia", '_dobra(u["CROP_ON_LABEL"]) == cult', 'cult.startswith(_dobra(u["CROP_ON_LABEL"]))'),
 ("M20 conflito escolhe o primeiro", 'if len(valores) > 1:', 'if False:'),
 ("M21 revisao conta como primaria", 'if m in METODOS or m in METODOS_SECUNDARIOS:', 'if m in METODOS_SECUNDARIOS:\n        return "ENSAIO_DE_CAMPO", porque\n    if m in METODOS:'),
 ("M22 tema nao provado ganha leitura", 'if not tema_provado:\n        return', 'if False:\n        return'),
]
mortos = 0
try:
    for nome, a, b in M:
        assert ORIG.count(a) == 1, (nome, ORIG.count(a))
        P.write_text(ORIG.replace(a, b))
        r = subprocess.run([sys.executable, "-m", "unittest", "tests.test_capacidade_cientifica"],
                           capture_output=True, text=True, cwd=RAIZ)
        morto = r.returncode != 0
        mortos += morto
        print(("MORTO " if morto else "VIVO  ") + nome)
finally:
    P.write_text(ORIG)
print("mortos %d/%d" % (mortos, len(M)))
sys.exit(0 if mortos == len(M) else 1)
