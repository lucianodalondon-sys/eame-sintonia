#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Mutacao da IDENTIDADE DO CRUZAMENTO e do POTE v2.1 (D125 · POTES-UM-CARTAO).

    python3 provas/_mutantes_identidade.py

Os 9 mutantes do red team do LAB (docs/lab/identidade-cruzamento/redteam_identidade.py --mutar, M1..M9) deixam
de ser bandeiras dentro de uma copia da regra: sao plantados no CODIGO REAL (motor/, pacote/, casco). Mais os
da D125 (copia no pote, dependente que nao muda junto, fecho que soma, SAIU sem causa, ANTERIOR sem SHA,
F1 pelo «melhor link», run no SG2, ALIAS apagado, casco que inventa o selo, ...).

Cada mutante e plantado numa COPIA da arvore, numa pasta temporaria fora do repositorio, e la correm
tests.test_identidade_cruzamento e tests.test_pote_v21 (este corre tambem o .mjs do casco). O repositorio nao
e tocado. MORTO = um teste caiu. VIVO ou NAO_APLICOU = esta prova reprova (saida 1).
"""
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
IDN = "motor/identidade_do_cruzamento.py"
VOC = "motor/vocabulario_unico.py"
XMX = "motor/cruzamentos_max.py"
CRR = "motor/corrida_da_inteligencia.py"
POT = "pacote/pote_intelligence_casco.py"
JSC = "italia-portale/client/sintonia-pote-casco.js"
TESTES = ["tests.test_identidade_cruzamento", "tests.test_pote_v21"]

M = [
    # ── os 9 do LAB (M1..M9) ─────────────────────────────────────────────────
    ("M1 NAO SEI junta com NAO SEI", IDN, 'v = "NAO_SEI@" + str(documento)', 'v = "NAO_SEI"'),
    ("M2 grupo vira membro (drupacee/pomacee)", VOC, "    if n in XM.PALAVRAS_DE_GRUPO:\n", "    if False:\n"),
    ("M3 lugar sobe para a regiao", VOC, "    fino = min(_NIVEL[n] for n, _ in achados)", "    fino = max(_NIVEL[n] for n, _ in achados)"),
    ("M4 substancia agressiva (METALAXYL = METALAXYL-M)", XMX,
     '    return re.sub(r"[^A-Z0-9]", "", dobrar(s).upper())\n',
     '    return re.sub(r"M$", "", re.sub(r"[^A-Z0-9]", "", dobrar(s).upper()))\n'),
    ("M5 evidencia por item, nao por documento", IDN, "    for c in _DOC:\n        if not _ign(prova.get(c)):",
     "    return \"ITEM:\" + str(prova.get(\"ITEM_ID\"))\n    for c in _DOC:\n        if not _ign(prova.get(c)):"),
    ("M6 independencia por SOURCE_ID", IDN, 'for c in ("ORIGINADOR", "ORIGINATOR", "ORIGINATOR_ID"):', 'for c in ("SOURCE_ID",):'),
    ("M7 tudo e conflito (TEMPORAL_CHANGE vira DIVERGENT)", IDN,
     '    if a["originador"] == b["originador"] and a["periodo"] != b["periodo"]:', "    if False:"),
    ("M8 edicao da bula na chave", IDN, '    partes = [familia + "/v1"]\n',
     '    partes = [familia + "/v1"] + (["EDICAO=" + str(slots["_EDICAO"])] if slots.get("_EDICAO") else [])\n'),
    ("M9 publicacao vira fact time", IDN, "    if _ign(fact_time):\n        return None", "    if _ign(fact_time):\n        return \"2026\""),
    # ── D125 ────────────────────────────────────────────────────────────────
    ("D1 o compartimento guarda copia", POT, '        e = {k: v for k, v in e.items() if k != "OBJETOS"}\n', "        e = dict(e)\n"),
    ("D2 a conferencia aceita a copia", POT, '        if "OBJETOS" in e:\n            v.append(f"{comp}: COPIA_NO_POTE',
     '        if False:\n            v.append(f"{comp}: COPIA_NO_POTE'),
    ("D3 o dependente nao muda junto com o pai", IDN, "        if mud == SEM_REVISAO and pais:", "        if False:"),
    ("D4 o fecho soma os filhos", IDN, '"N_EVIDENCIAS_DOCUMENTO": len(evs),',
     '"N_EVIDENCIAS_DOCUMENTO": len(evs) + len(c.get("REFERENCIAS") or []),'),
    ("D5 o fecho esquece o pai", IDN, '    for r in c.get("REFERENCIAS") or []:\n        alvo = r.get("CROSSING_ID")\n        if alvo in cartoes:',
     '    for r in []:\n        alvo = r.get("CROSSING_ID")\n        if alvo in cartoes:'),
    ("D6 ausencia vira SAIU", IDN, "            if a in causas_de_saida and not _ign(causas_de_saida[a]):", "            if True:"),
    ("D7 ANTERIOR sem SHA256 aceite", POT, "    if anterior is not None and (e_ignorancia(anterior_sha256)",
     "    if False and (e_ignorancia(anterior_sha256)"),
    ("D8 F1 pelo estado dos links, nao do rotulo", XMX, '        return av["RESPOSTA"]\n', "        return None\n"),
    ("D9 o run volta para o SG2", CRR,
     '                sg2 = IDENT.sg2_id(IDENT.evidencia(item), ref["RAW_OBSERVATION_ID"], item.get("FACT_TIME"))\n',
     '                sg2 = IDENT.sg2_id(run_id + IDENT.evidencia(item), ref["RAW_OBSERVATION_ID"], item.get("FACT_TIME"))\n'),
    ("D10 o ID antigo nao vai para ALIAS (migracao)", IDN,
     "    if antigo and antigo != novo and antigo not in alias:\n        alias.append(antigo)\n    out =",
     "    out ="),
    ("D11 o ID antigo nao vai para ALIAS (cruzamentos)", IDN,
     "        if antigo and antigo != novo and antigo not in alias:\n            alias.append(antigo)\n        return",
     "        return"),
    ("D12 o casco aceita a copia", JSC, "if (e.OBJETOS) v.push(", "if (false) v.push("),
    ("D13 o casco inventa o selo", JSC, "delta: !d ? '' : txt(d.MUDANCA) + ' · '", "delta: !d ? '' : 'NOVO' + ' · '"),
    ("D14 «mosca» sozinho vira mosca da oliveira", VOC, "    n = dobrar(nome_do_problema(n))\n",
     "    n = dobrar(nome_do_problema(n))\n    n = n.replace(\"mosca\", \"mosca dell'olivo\") if n == \"mosca\" else n\n"),
    ("D15 ID repetido no compartimento aceite", POT, "        if len(ids) != len(set(ids)):", "        if False:"),
    ("D16 a mesma pergunta com dois cartoes aceite", POT, "            if n in nomes and nomes[n] != oid:", "            if False:"),
]


def correr(pasta: Path) -> subprocess.CompletedProcess:
    import os
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1", PYTHONUTF8="1",
               HTTP_PROXY="http://127.0.0.1:9", HTTPS_PROXY="http://127.0.0.1:9")
    return subprocess.run([sys.executable, "-m", "unittest", *TESTES], cwd=pasta, capture_output=True, text=True,
                          encoding="utf-8", errors="replace", env=env, timeout=900)


def main() -> int:
    alvos = {x[1] for x in M}
    originais = {a: (RAIZ / a).read_text(encoding="utf-8") for a in alvos}
    vivos, nao_aplicou = [], []
    with tempfile.TemporaryDirectory() as d:
        pasta = Path(d)
        rastreados = subprocess.run(["git", "-C", str(RAIZ), "ls-files", "*.py", "*.json", "*.mjs", "*.js",
                                     "*.csv", "docs/intelligence/**", "italia-portale/client/**"],
                                    capture_output=True, text=True, encoding="utf-8").stdout.split()
        novos = subprocess.run(["git", "-C", str(RAIZ), "ls-files", "--others", "--exclude-standard"],
                               capture_output=True, text=True, encoding="utf-8").stdout.split()
        for rel in sorted(set(rastreados) | set(novos) | alvos):
            if not (RAIZ / rel).is_file() or rel.startswith(("system-map/", "data/", "research/")):
                continue
            (pasta / rel).parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(RAIZ / rel, pasta / rel)
        base = correr(pasta)
        if base.returncode != 0:
            print("BASE VERMELHA na copia — a prova nao vale:\n" + base.stderr[-3000:])
            return 2
        print("base: verde na copia (%s)" % ", ".join(TESTES))
        for nome, alvo, a, b in M:
            original = originais[alvo]
            if original.count(a) != 1:
                print(f"{nome}: NAO_APLICOU ({original.count(a)} ocorrencias)")
                nao_aplicou.append(nome)
                continue
            (pasta / alvo).write_text(original.replace(a, b), encoding="utf-8")
            r = correr(pasta)
            caidos = sorted(set(re.findall(r"^(?:FAIL|ERROR): (\S+) \(", r.stderr, re.M)))
            estado = "MORTO" if r.returncode != 0 else "VIVO"
            if estado == "VIVO":
                vivos.append(nome)
            print(f"{nome}: {estado}" + (f"  <- {', '.join(caidos[:4])}" if caidos else ""))
            (pasta / alvo).write_text(original, encoding="utf-8")
    mortos = len(M) - len(vivos) - len(nao_aplicou)
    print(f"\nMUTACAO: {mortos}/{len(M)} mortos · vivos {vivos or 0} · nao aplicados {nao_aplicou or 0}")
    return 0 if not vivos and not nao_aplicou else 1


if __name__ == "__main__":
    sys.exit(main())
