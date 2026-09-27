#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Mutacao da LIGACAO-ADAMA (D123): planta os defeitos que a missao proibe e prova que os testes os apanham.

    python3 provas/ligacao_adama/mutantes.py [saida.json]

Cada mutante e plantado numa COPIA da arvore (pasta temporaria fora do repositorio) e la correm os
testes que ele nomeia. O repositorio nao e tocado. MORTO = um teste falhou por causa dele. VIVO ou
NAO_APLICOU (um texto-alvo nao existe uma vez so) reprovam esta prova.
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
PORTA = "motor/porta_da_referencia.py"
POTE = "pacote/pote_intelligence_casco.py"
LIG = "tests.test_ligacao_adama"
POTES = (LIG, "tests.test_pote_v2_unico", "tests.test_pote_intelligence_casco")
#: A arvore inteira (sem .git): os testes do pote correm o leitor do casco em node e leem .vercelignore.
IGNORAR = shutil.ignore_patterns(".git", "__pycache__", "node_modules")

# (nome, testes, [(ficheiro, texto, troca), ...])
M = [
    # ── 1 · objeto sem ligacao aceito ───────────────────────────────────────────
    ("O1 o gerador do pote aceita objeto sem LIGACAO_ADAMA", POTES, [
        (POTE, '    if "LIGACAO_ADAMA" not in o:\n        return ("SEM_LIGACAO_ADAMA"',
               '    if False:\n        return ("SEM_LIGACAO_ADAMA"'),
        (POTE, '    falhas = PORTA.conferir_ligacao(o["LIGACAO_ADAMA"])\n',
               '    falhas = PORTA.conferir_ligacao(o["LIGACAO_ADAMA"]) if "LIGACAO_ADAMA" in o else []\n')]),
    ("O2 conferir_pote deixa passar pote com objeto sem ligacao", (LIG,), [
        (POTE, '            for x in PORTA.conferir_ligacao(o.get("LIGACAO_ADAMA")):\n'
               '                v.append(f"{comp}/{oid}: D123 {x}")\n', '')]),
    ("O3 o schema deixa de exigir LIGACAO_ADAMA", (LIG, "tests.test_pote_v2_unico"), [
        ("docs/intelligence/pote-v2/POTE_INTELLIGENCE_CASCO-v2.schema.json",
         '"PROVA", "CORRIDA_SINTETICA", "LIGACAO_ADAMA"],', '"PROVA", "CORRIDA_SINTETICA"],')]),
    ("O4 o motor emite janela sem ligacao", ("tests.test_motor_das_capacidades",), [
        ("motor/motor_das_capacidades.py", '           "LIGACAO_ADAMA": j["LIGACAO_ADAMA"]}\n', '           }\n')]),
    ("O5 a voz sai sem ligacao", (LIG,), [
        ("motor/voce_dal_campo.py", "        vozes.append(voz)\n", "        voz.pop('LIGACAO_ADAMA')\n        vozes.append(voz)\n")]),
    # ── 2 · ligacao calculada fora da porta ─────────────────────────────────────
    ("F1 a CAP-WIN monta a ligacao a mao", (LIG,), [
        ("motor/cap_win.py", '        j["LIGACAO_ADAMA"] = ligacao_da_janela(ref, j["CROP_ID"], j["ISSUE_ID"])\n',
         '        j["LIGACAO_ADAMA"] = {"ESTADO": "A_CONFIRMAR", "CALCULADA_POR": "motor/cap_win.py"}\n')]),
    ("F2 cruzamentos_max sela a sua propria ligacao", (LIG,), [
        ("motor/cruzamentos_max.py", "def ligacao_do_competitive_set(ref: Referencia, p: dict) -> dict:\n",
         "def ligacao_do_competitive_set(ref: Referencia, p: dict) -> dict:\n"
         "    return PORTA._selar_ligacao({'ESTADO': 'NAO_SEI'})\n")]),
    ("F3 o boletim deixa de chamar a porta (dict proprio)", (LIG,), [
        ("leis/boletim_do_campo.py", '                          "LIGACAO_ADAMA": PORTA.ligacao_adama(ref, {\n',
         '                          "LIGACAO_ADAMA": dict(ref and {}, ESTADO="NAO_SEI") or PORTA.dobrar({\n')]),
    ("F4 a porta nao confere o selo", (LIG,), [
        (PORTA, '    if lig.get("SELO") != _selo_da_ligacao(lig):\n', '    if False:\n')]),
    ("F5 a fila aceita ligacao sem selo", (LIG,), [
        ("motor/fila_bulas_a_ler.py", "        falhas = PORTA.conferir_ligacao(lig)\n", "        falhas = []\n")]),
    ("F6 a porta aceita texto livre como chave", (LIG,), [
        (PORTA, '    estranhas = sorted(set(chaves) - set(CHAVES_DA_LIGACAO) - {"VEM_DE"})\n',
                '    estranhas = []\n')]),
    # ── 3 · catalogo vira autorizado ─────────────────────────────────────────
    ("K1 registo da vitrine conta como ativo", (LIG,), [
        (PORTA, '    ativos, leituras = _ativos(ref), _leituras(ref)\n    usos = [u for u in livro(ref, "AUTHORIZED-USES")',
                '    ativos, leituras = {**_ativos(ref), **{p["REGISTRATION_NUMBER"]: {"REGISTRATION_NUMBER": '
                'p["REGISTRATION_NUMBER"]} for p in livro(ref, "PORTFOLIO") if p.get("REGISTRATION_NUMBER")}}, '
                '_leituras(ref)\n    usos = [u for u in livro(ref, "AUTHORIZED-USES")')]),
    ("K2 conferir_ligacao aceita autorizado vindo do catalogo", (LIG,), [
        (PORTA, '            if p.get("FONTE_DO_ESTADO") != "REGISTRO.AUTHORIZED-USES":\n', '            if False:\n')]),
    # ── 4 · DECLARACAO_DE_PRODUTO vira autorizado ────────────────────────────
    ("D1 a porta autoriza por DECLARACAO_DE_PRODUTO", (LIG,), [
        (PORTA, '    fortes = {r: [u for u in us if u.get("LINK_LEVEL") in NIVEIS_QUE_AUTORIZAM] for r, us in por_reg.items()}\n',
                '    fortes = {r: list(us) for r, us in por_reg.items()}\n')]),
    ("D2 conferir_ligacao aceita autorizado so por declaracao", (LIG,), [
        (PORTA, '            if not set(p.get("LINK_LEVEL") or []) & set(NIVEIS_QUE_AUTORIZAM):\n', '            if False:\n')]),
    ("D3 D117 ignorado: autoriza com a edicao >= 30 dias", (LIG,), [
        (PORTA, '    estado_uso = AUTORIZADO_BULA_LIDA if estado_uso == AUTORIZADO_NA_BULA_LIDA else estado_uso\n',
                '    estado_uso = AUTORIZADO_BULA_LIDA\n')]),
    # ── 5 · ligacao conta como fonte independente ────────────────────────────
    ("I1 a trava diz que a ligacao e fonte independente", (LIG,), [
        (PORTA, '    "CONTA_COMO_FONTE_INDEPENDENTE": False,\n', '    "CONTA_COMO_FONTE_INDEPENDENTE": True,\n')]),
    ("I2 o pote aceita a referencia como prova do objeto", (LIG,), [
        (POTE, '    if any(PORTA.e_prova_da_referencia(p) for p in o["PROVA"]):\n', '    if False:\n')]),
    ("I3 a ligacao deixa de dizer que nao prova pressao nem demanda", (LIG,), [
        (PORTA, '    "NAO_PROVA": ["PRESSAO_DE_CAMPO", "DEMANDA"],\n', '    "NAO_PROVA": [],\n')]),
    # ── 6 · ADAMA_SEM_PRODUTO sem a porta ter lido ────────────────────────────
    ("S1 bulas por ler e a porta diz que nao ha produto", (LIG,), [
        (PORTA, "    elif fracos or nao_lidas:\n", "    elif fracos:\n")]),
    ("S2 composicao incompleta e a porta diz que nao ha", (LIG,), [
        (PORTA, "            if cobertos == set(ativos):\n", "            if True:\n")]),
    ("S3 conferir_ligacao aceita ADAMA_SEM_PRODUTO com bulas por ler", (LIG,), [
        (PORTA, '        if lig.get("BULAS_A_LER"):\n            v.append("ADAMA_SEM_PRODUTO com bulas por ler',
                '        if False:\n            v.append("ADAMA_SEM_PRODUTO com bulas por ler')]),
    ("S4 conferir_ligacao aceita ADAMA_SEM_PRODUTO sem referencia lida", (LIG,), [
        (PORTA, '        if carim.get("ESTADO") != "LIDA":\n', '        if False:\n')]),
    ("S5 varias culturas e um problema saem autorizados", (LIG,), [
        (PORTA, "    if fortes and len(C) > 1:\n", "    if False:\n")]),
    # ── 7 · a edicao ─────────────────────────────────────────────────────────
    ("E1 o pote aceita ligacoes de duas edicoes", (LIG,), [
        (POTE, "    if len(impressoes) > 1:\n", "    if False:\n")]),
]


def correr(pasta: Path, testes) -> subprocess.CompletedProcess:
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1", PYTHONUTF8="1",
               HTTP_PROXY="http://127.0.0.1:9", HTTPS_PROXY="http://127.0.0.1:9")
    return subprocess.run([sys.executable, "-m", "unittest", *testes], cwd=pasta, capture_output=True,
                          text=True, encoding="utf-8", errors="replace", env=env, timeout=1800)


def main(argv=None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    res = {"MUTANTES": []}
    todos = sorted({t for _, ts, _ in M for t in ts})
    with tempfile.TemporaryDirectory() as d:
        pasta = Path(d)
        pasta = pasta / "arvore"
        shutil.copytree(RAIZ, pasta, ignore=IGNORAR, symlinks=True)
        # um repositorio vazio: os testes perguntam ao git o que ele ignora (.gitignore da copia)
        subprocess.run(["git", "init", "-q", str(pasta)], check=True)
        base = correr(pasta, todos)
        if base.returncode != 0:
            print("BASE VERMELHA na copia — a prova nao vale:\n"
                  + "\n".join(re.findall(r"^(?:FAIL|ERROR): .*$", base.stderr, re.M)) + base.stderr[-2000:])
            return 2
        print("base: verde na copia (%s)" % ", ".join(todos))
        for nome, testes, trocas in M:
            originais, ok = {}, True
            for alvo, a, b in trocas:
                texto = originais.get(alvo) or (pasta / alvo).read_text(encoding="utf-8")
                originais.setdefault(alvo, texto)
                atual = (pasta / alvo).read_text(encoding="utf-8")
                if atual.count(a) != 1:
                    ok = False
                    break
                (pasta / alvo).write_text(atual.replace(a, b), encoding="utf-8")
            if not ok:
                print(f"{nome}: NAO_APLICOU")
                res["MUTANTES"].append({"MUTANTE": nome, "ESTADO": "NAO_APLICOU"})
            else:
                r = correr(pasta, testes)
                caidos = sorted(set(re.findall(r"^(?:FAIL|ERROR): (\S+) \(", r.stderr, re.M)))
                estado = "MORTO" if r.returncode != 0 else "VIVO"
                print(f"{nome}: {estado}" + (f"  <- {', '.join(caidos[:4])}" if caidos else ""))
                res["MUTANTES"].append({"MUTANTE": nome, "ALVOS": sorted({t[0] for t in trocas}),
                                        "TESTES": list(testes), "ESTADO": estado, "APANHADO_POR": caidos})
            for alvo, texto in originais.items():
                (pasta / alvo).write_text(texto, encoding="utf-8")
    est = [m["ESTADO"] for m in res["MUTANTES"]]
    res["MORTOS"], res["TOTAL"] = est.count("MORTO"), len(M)
    print(f"\nMUTACAO: {res['MORTOS']}/{len(M)} mortos · vivos {est.count('VIVO')} · nao aplicados "
          f"{est.count('NAO_APLICOU')}")
    if argv:
        Path(argv[0]).write_text(json.dumps(res, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    return 0 if res["MORTOS"] == len(M) else 1


if __name__ == "__main__":
    sys.exit(main())
