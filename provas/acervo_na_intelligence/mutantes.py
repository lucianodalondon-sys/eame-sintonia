#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Mutacao do ACERVO-NA-INTELLIGENCE: planta os defeitos que a missao proibe e prova que os testes
os apanham.

    python3 provas/acervo_na_intelligence/mutantes.py [saida.json]

Cada mutante e plantado numa COPIA da arvore (sem .git), numa pasta temporaria fora do repositorio, e
la corre tests/test_acervo_na_intelligence.py. O repositorio nao e tocado. MORTO = um teste falhou por
causa dele. VIVO ou NAO_APLICOU (o texto-alvo nao existe uma vez so) reprovam esta prova.
"""
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
TESTE = "tests.test_acervo_na_intelligence"
ALVO = "pacote/acervo_na_intelligence.py"

M = [
    # ── anuncio nao e oportunidade nem demanda ──────────────────────────────
    ("O1 anuncio vira OPORTUNIDADE", ALVO,
     '        objs.append(_com_id_provisorio({\n            "OBJETO_ID": oid, "ESPECIE": MOTOR.SINAL,',
     '        objs.append(_com_id_provisorio({\n            "OBJETO_ID": oid, "ESPECIE": "OPORTUNIDADE",'),
    ("O2 anuncio entra no Radar delle Opportunita", ALVO,
     'objetos.update({"competitors": comp,', 'objetos.update({"meeting": comp, "competitors": comp,'),
    ("O3 a cultura do anuncio e afirmada (CROP_TERMS)", ALVO,
     '               "CROP_ID": _ent(NAO_SEI, NAO_SEI, iid),\n               "FACT_LOCATION"',
     '               "CROP_ID": _ent(",".join(r.get("CROP_TERMS") or []) or NAO_SEI, "REGISTO.CROP_TERMS", iid),\n'
     '               "FACT_LOCATION"'),
    ("O4 o concorrente liga-se a ADAMA pelo ALVO e nao pela substancia", ALVO,
     'mesma = sorted({g["REGISTRATION_NUMBER"] for s in a.get("SUBSTANCIAS_NO_CRIATIVO", [])',
     'mesma = sorted({g["REGISTRATION_NUMBER"] for s in a.get("ALVOS_NO_CRIATIVO", [])'),
    ("O5 anuncio sem tempo passa sem G0", ALVO,
     '        if not MOTOR._admite(linha, MOTOR.SINAL):\n            nao_vao.append({"OBJETO_ID": oid, "ITEM_ID": iid, '
     '"COMPARTIMENTO": "competitors",',
     '        if False:\n            nao_vao.append({"OBJETO_ID": oid, "ITEM_ID": iid, "COMPARTIMENTO": "competitors",'),
    # ── preco isolado nao e mudanca ─────────────────────────────────────────
    ("P1 o preco anterior da fonte vira ponto da serie", ALVO,
     'serie = sorted(pontos.get(k, []), key=lambda p: p["PERIOD"]) if k else []',
     'serie = ([{"PERIOD": "ANTERIOR", "PRICE": r.get("PREV_PRICE_NUM"), "UNIT": r.get("UNIT")}]'
     ' + sorted(pontos.get(k, []), key=lambda p: p["PERIOD"])) if r.get("PREV_PRICE_NUM") is not None else []'),
    ("P2 a variacao da fonte vira MUDANCA_DE_MERCADO", ALVO,
     '        if len(serie) >= 2:\n',
     '        o["MUDANCA_DE_MERCADO"] = r.get("CHANGE_VS_PREV_PCT") is not None\n        if len(serie) >= 2:\n'),
    ("P3 serie mistura unidades (a chave perde a unidade)", ALVO,
     'k = tuple(r.get(c) for c in ("MARKET", "PRODUCT", "STAGE", "UNIT"))',
     'k = tuple(r.get(c) for c in ("MARKET", "PRODUCT", "STAGE"))'),
    # ── lugar da fonte nao e lugar do facto (D112) ──────────────────────────
    ("L1 o pais da fonte vira o lugar do facto", ALVO,
     '        "FACT_LOCATION": NAO_SEI,\n', '        "FACT_LOCATION": sloc,\n'),
    ("L2 o alcance do anuncio (REGION_IDS) vira o lugar do facto", ALVO,
     '               "FACT_LOCATION": _ent(NAO_SEI, NAO_SEI, iid),',
     '               "FACT_LOCATION": _ent(",".join(r.get("REGION_IDS") or []) or NAO_SEI, "REGISTO.REGION_IDS", iid),'),
    # ── publicacao nao e tempo do facto; limites da captura ────────────────
    ("T1 a publicacao da ciencia vira tempo do facto", ALVO,
     '    return NAO_SEI, NAO_SEI\n\n\ndef publicacao',
     '    if col in ("scienceCorpus", "scienceRecords") and _iso(r.get("PUBLISHED_AT")):\n'
     '        return _iso(r.get("PUBLISHED_AT")), "REGISTO.PUBLISHED_AT"\n'
     '    return NAO_SEI, NAO_SEI\n\n\ndef publicacao'),
    ("T2 a data do pacote vira limite superior da captura", ALVO,
     'LIMITE_SUPERIOR_DA_CAPTURA = "2026-09-15"', 'LIMITE_SUPERIOR_DA_CAPTURA = "2026-09-02"'),
    ("T3 o inicio do facto vira limite inferior para todo tipo", ALVO,
     '    if col in ("competitorActivities", "marketObservations"):\n', '    if True:\n'),
    ("T4 URL ambigua: escolhe a primeira", ALVO,
     'return u[0] if len(u) == 1 else NAO_SEI', 'return u[0] if u else NAO_SEI'),
    # ── ID, contrato, contagem ─────────────────────────────────────────────
    ("I1 o ID deixa de ser PROVISORIO", ALVO,
     '    o["CHAVES"]["ID_ESTADO"] = ID_ESTADO\n', '    o["CHAVES"]["ID_ESTADO"] = "DEFINITIVO"\n'),
    ("I2 o mapa ENTITY_SOURCE do motor vai cru ao pote", ALVO,
     '    ao_contrato_unico(objetos)\n', ''),
    ("I3 quem fica fora da corrida some em silencio", ALVO,
     '            fora_da_corrida.append({"ITEM_ID": x["ACERVO_ID"],',
     '            [].append({"ITEM_ID": x["ACERVO_ID"],'),
    ("I4 o Archivio guarda tambem o que o pote recusou", ALVO,
     'objetos["archive"] = arquivo({c: [o for o in objetos.get(c) or [] if o["OBJETO_ID"] in passaram.get(c, ())]',
     'objetos["archive"] = arquivo({c: [o for o in objetos.get(c) or []]'),
]


def correr(pasta: Path) -> subprocess.CompletedProcess:
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1", PYTHONUTF8="1",
               HTTP_PROXY="http://127.0.0.1:9", HTTPS_PROXY="http://127.0.0.1:9")
    return subprocess.run([sys.executable, "-m", "unittest", TESTE], cwd=pasta, capture_output=True,
                          text=True, encoding="utf-8", errors="replace", env=env, timeout=900)


def main(argv=None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    res = {"TESTE": TESTE, "MUTANTES": []}
    with tempfile.TemporaryDirectory() as d:
        pasta = Path(d) / "arvore"
        shutil.copytree(RAIZ, pasta, ignore=shutil.ignore_patterns(".git", "__pycache__", "node_modules"))
        base = correr(pasta)
        if base.returncode != 0:
            print("BASE VERMELHA na copia — a prova nao vale:\n" + base.stderr[-3000:])
            return 2
        print("base: verde na copia")
        for nome, alvo, a, b in M:
            original = (RAIZ / alvo).read_text(encoding="utf-8")
            if original.count(a) != 1:
                print(f"{nome}: NAO_APLICOU ({original.count(a)} ocorrencias)")
                res["MUTANTES"].append({"MUTANTE": nome, "ALVO": alvo, "ESTADO": "NAO_APLICOU"})
                continue
            (pasta / alvo).write_text(original.replace(a, b), encoding="utf-8")
            r = correr(pasta)
            caidos = sorted(set(re.findall(r"^(?:FAIL|ERROR): (\S+) \(", r.stderr, re.M)))
            estado = "MORTO" if r.returncode != 0 else "VIVO"
            print(f"{nome}: {estado}" + (f"  <- {', '.join(caidos[:4])}" if caidos else ""))
            res["MUTANTES"].append({"MUTANTE": nome, "ALVO": alvo, "ESTADO": estado, "APANHADO_POR": caidos})
            (pasta / alvo).write_text(original, encoding="utf-8")
    est = [m["ESTADO"] for m in res["MUTANTES"]]
    res["MORTOS"], res["TOTAL"] = est.count("MORTO"), len(M)
    print(f"\nMUTACAO: {res['MORTOS']}/{len(M)} mortos · vivos {est.count('VIVO')} · nao aplicados "
          f"{est.count('NAO_APLICOU')}")
    if argv:
        Path(argv[0]).write_text(json.dumps(res, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    return 0 if res["MORTOS"] == len(M) else 1


if __name__ == "__main__":
    sys.exit(main())
