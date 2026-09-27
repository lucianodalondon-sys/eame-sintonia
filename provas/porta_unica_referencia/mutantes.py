#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Mutacao da PORTA-UNICA-REFERENCIA: planta os defeitos que a D116/D117 proibem e prova que os
testes os apanham.

    python3 provas/porta_unica_referencia/mutantes.py [saida.json]

Cada mutante e plantado numa COPIA da arvore, numa pasta temporaria fora do repositorio, e la corre
tests/test_porta_unica_referencia.py. O repositorio nao e tocado. MORTO = um teste falhou por causa
dele. VIVO ou NAO_APLICOU (o texto-alvo nao existe uma vez so) reprovam esta prova.
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
TESTE = "tests.test_porta_unica_referencia"
PORTA = "motor/porta_da_referencia.py"
COPIAR = ("_gavetas.py", "motor", "leis", "coleta", "fontes", "pacote", "provas", "tests", "regras",
          "ferramentas", "admissao", "guarda", "medidas", "pedido", "portoes", "superficie", "orquestrador",
          "candidatas", "referencia", "research/adama-italy-product-intelligence-deep",
          "build/SINTONIA-ITALY-REALITY-HANDOFF-V2.1.zip", "data/samples/IT-SOURCE-SAMPLES/IT-T4-001",
          "data/samples/IT-ROTULOS", "data/samples/IT-DOSE-ROTULO", "docs/intelligence/r7")

M = [
    # ── leitura direta (a varredura) ─────────────────────────────────────────
    ("L1 cap_win abre o PORTFOLIO por fora", "motor/cap_win.py",
     "import porta_da_referencia as PORTA             # noqa: E402\n",
     "import porta_da_referencia as PORTA             # noqa: E402\n"
     "_PORTFOLIO = RAIZ / \"referencia\" / \"adama\" / \"PORTFOLIO.json\"\n"),
    ("L2 cruzamentos_max volta a ler os pares do leitor", "motor/cruzamentos_max.py",
     "SAIDA = os.path.join(ROOT, \"docs\", \"intelligence\", \"r7\", \"CRUZAMENTOS-MAX.json\")\n",
     "SAIDA = os.path.join(ROOT, \"docs\", \"intelligence\", \"r7\", \"CRUZAMENTOS-MAX.json\")\n"
     "PARES = os.path.join(ROOT, \"data\", \"samples\", \"IT-ROTULOS\", \"IT-ROTULOS-PARES.json\")\n"),
    ("L3 concorrencia_meta le o CSV do Ministero", "coleta/concorrencia_meta.py",
     "import porta_da_referencia as porta  # noqa: E402 — D116: a referencia ADAMA so pela porta\n",
     "import porta_da_referencia as porta  # noqa: E402 — D116: a referencia ADAMA so pela porta\n"
     "CSV = os.path.join(RAIZ, 'data', 'samples', 'PROD_FTS_6_20260914.csv')\n"),
    ("L4 boletim le o COMMERCIAL-CATALOG", "leis/boletim_do_campo.py",
     "    import porta_da_referencia as PORTA   # noqa: PLC0415\n",
     "    import porta_da_referencia as PORTA   # noqa: PLC0415\n"
     "    open(os.path.join(motor, 'COMMERCIAL-CATALOG.json'))\n"),
    # ── edicao misturada ────────────────────────────────────────────────────
    ("E1 a porta aceita livros de edicoes diferentes", PORTA,
     "    if len(correntes) != 1 or len(set(edicoes.values())) != 1 or correntes[0] not in edicoes.values():\n",
     "    if len(correntes) < 1:\n"),
    ("E2 a porta aceita o catalogo misturado", PORTA,
     "            or cat[\"PORTFOLIO-OBSERVATIONS\"].get(\"CURRENT_SNAPSHOT\") != csnap.get(\"CURRENT_SNAPSHOT\"):\n",
     "            or False:\n"),
    ("E3 o motor abre a porta duas vezes (WIN numa edicao, SCI noutra)", "motor/motor_das_capacidades.py",
     "    win = WIN.julgar(livro, itens_win, hoje, fora=para_win, referencia=ref)\n",
     "    win = WIN.julgar(livro, itens_win, hoje, fora=para_win)\n"),
    # ── catalogo tratado como autorizacao ────────────────────────────────────
    ("K1 registo na vitrine conta como autorizado", PORTA,
     "        if u[\"REGISTRATION_NUMBER\"] not in ativos:\n            continue\n",
     "        if u[\"REGISTRATION_NUMBER\"] not in ativos and u[\"REGISTRATION_NUMBER\"] not in {\n"
     "                p[\"REGISTRATION_NUMBER\"] for p in livro(ref, \"PORTFOLIO\")}:\n            continue\n"),
    ("K2 os livros do catalogo entram na metade do registo", PORTA,
     "LIVROS_DO_REGISTRO = (\"SNAPSHOTS\", \"REGISTRATIONS\", \"AUTHORIZED-USES\", \"LABEL-READINGS\",\n",
     "LIVROS_DO_REGISTRO = (\"SNAPSHOTS\", \"REGISTRATIONS\", \"AUTHORIZED-USES\", \"LABEL-READINGS\", \"PORTFOLIO\",\n"),
    # ── frescor ignorado ─────────────────────────────────────────────────────
    ("F1 os 30 dias nao existem", PORTA,
     "    if dias >= DIAS_AUTORIZACAO_A_CONFIRMAR:\n        return AUTORIZACAO_A_CONFIRMAR\n",
     "    if False:\n        return AUTORIZACAO_A_CONFIRMAR\n"),
    ("F2 os 14 dias nao existem", PORTA,
     "    if dias >= DIAS_PODE_ESTAR_DESATUALIZADO:\n", "    if False:\n"),
    ("F3 a resposta ignora o frescor", PORTA,
     "    if ref[\"REGISTRO\"][\"ESTADO_FRESCOR\"] == AUTORIZACAO_A_CONFIRMAR:\n", "    if False:\n"),
    ("F4 frescor contado da data do ficheiro, e nao da checagem", PORTA,
     "    dias = _dias(checagem, hoje) if checagem else None\n",
     "    dias = 0\n"),
    # REANCORADO, DECLARADO (LOTE7-INTEGRA): a CAP-SCI passou a pedir a regra a porta
    # (autorizacao_do_uso); o defeito plantado e o mesmo — o frescor nao chega a regra.
    ("F5 cap_sci ignora o frescor", "motor/capacidade_cientifica.py",
     "        frescor = (ref.get(\"CARIMBO\") or {}).get(\"ESTADO_FRESCOR\")\n",
     "        frescor = None\n"),
    ("F6 cruzamentos confirma com referencia velha", "motor/cruzamentos_max.py",
     "    elif confirmados and ref.autorizacao_a_confirmar:\n", "    elif False:\n"),
    ("F7 sem data de checagem = fresca", PORTA,
     "    if not isinstance(dias, int):\n        return AUTORIZACAO_A_CONFIRMAR\n",
     "    if not isinstance(dias, int):\n        return FRESCA\n"),
    # ── bula nao lida, checagem, carimbo ────────────────────────────────────
    ("B1 bula nao lida some (vira «nao»)", PORTA,
     "                       if not (leituras.get(n) or {}).get(\"LABEL_WAS_READ\"))\n",
     "                       if False)\n"),
    ("C1 a checagem confirma sempre", "fontes/adama_referencia.py",
     "    ok = not (entradas or saidas or estado)\n", "    ok = True\n"),
    ("C2 o carimbo nao e o sha do livro", PORTA,
     "    return json.loads(p.read_text(encoding=\"utf-8\")), _sha(p)\n",
     "    return json.loads(p.read_text(encoding=\"utf-8\")), _sha(p.parent / \"SNAPSHOTS.json\")\n"),
    ("C3 cap_win nao carimba a edicao", "motor/cap_win.py",
     "        \"REFERENCIA_ADAMA\": PORTA.carimbo(ref),\n", ""),
    # ── GRAO do uso (LOTE7-INTEGRA; LAB PESQUISA-CRUZAMENTOS F.2-1) ──────────
    ("G1 a declaracao de produto entra nos niveis que autorizam", PORTA,
     "NIVEIS_QUE_AUTORIZAM = (LINHA_DA_TABELA, BLOCO_DA_CULTURA)\n",
     "NIVEIS_QUE_AUTORIZAM = (LINHA_DA_TABELA, BLOCO_DA_CULTURA, DECLARACAO_DE_PRODUTO)\n"),
    ("G2 a regra ignora o nivel de ligacao", PORTA,
     "    if nivel not in NIVEIS_QUE_AUTORIZAM:\n", "    if False:\n"),
    ("G3 nivel ausente autoriza", PORTA,
     "    nivel = (uso or {}).get(\"LINK_LEVEL\", NAO_SEI)\n",
     "    nivel = (uso or {}).get(\"LINK_LEVEL\") or LINHA_DA_TABELA\n"),
    ("G4 autorizados: qualquer uso lido vira SIM", PORTA,
     "    elif produtos:\n        estado = A_CONFIRMAR\n",
     "    elif produtos:\n        estado = AUTORIZADO_NA_BULA_LIDA\n"),
    ("G5 por_alvo: registo nasce autorizado", PORTA,
     "                \"CULTURAS_SO_DECLARADAS\": set(), \"ESTADO\": A_CONFIRMAR})\n",
     "                \"CULTURAS_SO_DECLARADAS\": set(), \"ESTADO\": AUTORIZADO_NA_BULA_LIDA})\n"),
    ("G6 por_alvo: cultura so declarada conta como cultura na bula", PORTA,
     "            (x[\"CULTURAS_NA_BULA\"] if u.get(\"LINK_LEVEL\") in NIVEIS_QUE_AUTORIZAM\n",
     "            (x[\"CULTURAS_NA_BULA\"] if True\n"),
    ("G7 a regra ignora o frescor (D117)", PORTA,
     "    if estado_frescor == AUTORIZACAO_A_CONFIRMAR:\n", "    if False:\n"),
    ("G8 cap_sci faz o seu proprio SIM (qualquer uso)", "motor/capacidade_cientifica.py",
     "        autorizado = any(est == PORTA.AUTORIZADO_NA_BULA_LIDA for est, _ in julgados)\n",
     "        autorizado = bool(usos)\n"),
    ("G9 cruzamentos_max reescreve os niveis com a declaracao", "motor/cruzamentos_max.py",
     "NIVEIS_FORTES = PORTA.NIVEIS_QUE_AUTORIZAM\n",
     "NIVEIS_FORTES = (\"LINHA_DA_TABELA\", \"BLOCO_DA_CULTURA\", \"DECLARACAO_DE_PRODUTO\")\n"),
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
        pasta = Path(d)
        for rel in COPIAR:
            src, dst = RAIZ / rel, pasta / rel
            dst.parent.mkdir(parents=True, exist_ok=True)
            if src.is_dir():
                shutil.copytree(src, dst, ignore=shutil.ignore_patterns("__pycache__"))
            elif src.is_file():
                shutil.copy2(src, dst)
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
            caidos = sorted(set(re.findall(r"^(?:FAIL|ERROR): (\S+) \(", r.stderr, re.M)) | set(
                re.findall(r"^(?:ModuleNotFoundError|ImportError|NameError|SyntaxError)\b.*$", r.stderr, re.M)))
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
