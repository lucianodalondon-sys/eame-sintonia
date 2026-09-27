#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Mutacao do CRUZAMENTOS-MAX: o motor (motor/cruzamentos_max.py) e o pote do coordenador
(pacote/pote_cruzamentos_max.py).

    python3 provas/_mutantes_cruzamentos_max.py

Cada mutante e plantado numa COPIA da arvore minima, numa pasta temporaria fora do repositorio, e la
corre tests/test_cruzamentos_max.py. O repositorio nao e tocado.

Um mutante MORTO e um teste que falhou por causa dele. Um VIVO e um defeito que os testes deixam passar,
e reprova esta prova (codigo de saida 1). Um que NAO_APLICOU (o texto-alvo nao existe uma vez so)
tambem reprova: mutante que nao se planta nao prova nada.
"""
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
MOTOR = "motor/cruzamentos_max.py"
POTE = "pacote/pote_cruzamentos_max.py"
COPIAR = ("tests/test_cruzamentos_max.py",
          "docs/intelligence/r7/ANALISE-R7.json", "docs/intelligence/r7/CRUZAMENTOS-MAX.json",
          "docs/intelligence/r7/CRUZAMENTOS-MAX-ITENS-DO-POTE.json",
          "data/samples/IT-ROTULOS/IT-ROTULOS-PARES.json", "data/raw/IT-ROTULOS/_MANIFESTO.json",
          "data/collection-store/italy/IT-T4-001/MINSALUTE_FTS6_20260907/v1_9cd4d156369f/PROD_FTS_6_20260907.csv")

M = [
    # ── o grao ──────────────────────────────────────────────────────────────
    ("G1 declaracao de grupo de OUTRO rotulo serve",
     '    for g in ref.grao_do_reg.get(par["REGISTRATION_ID"], []):\n', "    for g in ref.grao:\n"),
    ("G2 chave de grupo do leitor prova a cultura sozinha",
     "    if k not in GRUPOS_DO_LEITOR:\n", "    if True:\n"),
    ("G3 cultura de rotacao vira uso", "    if _RX_NAO_E_USO.search(zona):\n", "    if False:\n"),
    ("G4 subtipo cobre o generico («cavolo» por «cavolo cappuccio»)",
     "            if _RX_SUBTIPO.match(t[m.end():]) or _RE_GRUPO.match(t[m.start():]):\n", "            if False:\n"),
    ("G5 a zona da cultura e a citacao inteira",
     "    return linha[:m.start()] if m else linha\n", '    return str(par.get("CITACAO_DA_LINHA") or "")\n'),
    ("G6 grupo declarado prova num par de outra cultura",
     '        if k_par not in {canon_cultura(m) for m in g["MEMBROS"]} | {canon_cultura(g["GRUPO"])}:\n',
     "        if False:\n"),
    # ── refazer ─────────────────────────────────────────────────────────────
    ("R1 PARTIAL vira YES sem ligacao no texto",
     "    elif cobertas:\n        depois = PARTIAL\n", "    elif cobertas:\n        depois = YES_A_CONFIRMAR\n"),
    ("R2 rotulo nao lido vira NO", "    elif not algum_lido:\n", "    elif False:\n"),
    ("R3 cultura fora do vocabulario vira NO",
     '    elif all(v["ESTADO"] == "NAO_ESTA_NO_ROTULO_LIDO" for v in por_cultura.values()):\n',
     "    elif not cobertas:\n"),
    ("R4 X3w sem janela (qualquer cultura do troco liga)",
     "                if any(abs(pc - ps_) <= JANELA_X3W for ps_ in ps):\n", "                if True:\n"),
    # ── confirmar / validade ────────────────────────────────────────────────
    ("C1 data do boletim NAO SEI confirma", "    elif d is None:\n", "    elif False:\n"),
    ("C2 cabecalho nao conferido", "    elif not cabecalho:\n", "    elif False:\n"),
    ("C3 empresa nao conferida",
     '            "EMPRESA_ADAMA": bool(linha) and e_adama(linha),\n', '            "EMPRESA_ADAMA": True,\n'),
    ("V1 validade ignora a scadenza", "    if fim and fim < d:\n", "    if False:\n"),
    ("V2 validade ignora a revoga", "    if revoga and revoga <= d:\n", "    if False:\n"),
    ("V3 validade ignora o registo posterior", "    if reg > d:\n", "    if False:\n"),
    ("V4 sem data vira SIM",
     '        return dict(base, VALIDO=NAO_SEI, MOTIVO="data de referencia NAO SEI")\n',
     '        return dict(base, VALIDO="SIM", MOTIVO="data de referencia NAO SEI")\n'),
    # ── portfolio / competitive ─────────────────────────────────────────────
    ("P1 declaracao de produto conta como par forte",
     'NIVEIS_FORTES = ("LINHA_DA_TABELA", "BLOCO_DA_CULTURA")\n',
     'NIVEIS_FORTES = ("LINHA_DA_TABELA", "BLOCO_DA_CULTURA", "DECLARACAO_DE_PRODUTO")\n'),
    ("P2 praga sem alvo ligada ao primeiro alvo",
     "    return next((k for k, rx in _RX_ALVO if rx.search(t)), None)\n",
     '    return next((k for k, rx in _RX_ALVO if rx.search(t)), "PERONOSPORA")\n'),
    ("P3 registo invalido conta como match",
     '    validos = [p for p in fortes_p if p["REGISTO_VALIDO"] == "SIM"]\n', "    validos = fortes_p\n"),
    ("S1 ADAMA entra no competitive set", "        if e_adama(linha):\n            continue\n",
     "        if False:\n            continue\n"),
    ("S2 substancia por pedaco (METALAXYL = METALAXYL-M)",
     '    return chave_substancia(substancia) in {chave_substancia(t) for t in\n'
     '                                            str(linha.get("sostanze_attive") or "").split("|")}\n',
     '    return any(x in chave_substancia(substancia) for x in {chave_substancia(t) for t in\n'
     '                                            str(linha.get("sostanze_attive") or "").split("|")})\n'),
    ("S3 CS com cultura inventada",
     '            "CULTURA_X_ALVO_DO_CONCORRENTE": NAO_SEI,\n', '            "CULTURA_X_ALVO_DO_CONCORRENTE": "VITE",\n'),
    ("S4 secao sem cultura herda a do boletim",
     '            if not isinstance(s, dict) or not s.get("CULTURA"):\n                continue',
     '            if not isinstance(s, dict):\n                continue\n            s = dict(s, CULTURA=s.get("CULTURA") or "vite")'),
    # ── os objetos para o pote ──────────────────────────────────────────────
    ("O1 objeto confirmado vira OPORTUNIDADE",
     '"OBJETO_ID": _oid(r["OBJETO_ID"], p["REGISTRATION_ID"]), "ESPECIE": "CROSSING",',
     '"OBJETO_ID": _oid(r["OBJETO_ID"], p["REGISTRATION_ID"]), "ESPECIE": "OPORTUNIDADE",'),
    ("O2 DOCUMENT_ID fabricado da chave da Sala",
     '            "DOCUMENT_ID": x.get("DOCUMENT_ID") or NAO_SEI,\n',
     '            "DOCUMENT_ID": x.get("DOCUMENT_ID") or str(x.get("SALA_CHAVE")),\n'),
    ("O3 CROSSING_STATE some", '"CROSSING_STATE": r["FINAL"], ', ""),
    # ── o pote do coordenador ───────────────────────────────────────────────
    ("K1 LINEAGE ambigua e ligada a primeira",
     '            return (achadas[0], "+".join(campos)) if len(ids) == 1 else (None, "AMBIGUA:" + "+".join(campos))\n',
     '            return (achadas[0], "+".join(campos))\n', POTE),
    ("K2 a corrida nova usa o id da R7",
     '        "INTELLIGENCE_RUN_ID": "IR-XMAX-" + impressao[:20],\n', '        "INTELLIGENCE_RUN_ID": base,\n', POTE),
    ("K3 --so-cruzamentos leva os objetos da R7",
     "    por_ferr = {} if so_cruzamentos else {", "    por_ferr = {} if False else {", POTE),
]


def correr(pasta: Path) -> subprocess.CompletedProcess:
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1", PYTHONUTF8="1",
               HTTP_PROXY="http://127.0.0.1:9", HTTPS_PROXY="http://127.0.0.1:9")
    return subprocess.run([sys.executable, "-m", "unittest", "tests.test_cruzamentos_max"],
                          cwd=pasta, capture_output=True, text=True, encoding="utf-8",
                          errors="replace", env=env, timeout=900)


def main() -> int:
    alvos = {MOTOR, POTE}
    originais = {a: (RAIZ / a).read_text(encoding="utf-8") for a in alvos}
    vivos, nao_aplicou = [], []
    with tempfile.TemporaryDirectory() as d:
        pasta = Path(d)
        pys = subprocess.run(["git", "-C", str(RAIZ), "ls-files", "*.py"], capture_output=True,
                             text=True, encoding="utf-8").stdout.split()
        for rel in sorted(set(COPIAR) | set(pys) | alvos):
            if not (RAIZ / rel).is_file():
                continue
            (pasta / rel).parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(RAIZ / rel, pasta / rel)
        base = correr(pasta)
        if base.returncode != 0:
            print("BASE VERMELHA na copia — a prova nao vale:\n" + base.stderr[-3000:])
            return 2
        print("base: verde na copia")
        for nome, a, b, *alvo in M:
            alvo = alvo[0] if alvo else MOTOR
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
