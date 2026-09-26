#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Mutacao do POLSO-DI-MERCATO (leis/preco_de_mercado.py): cada mutante e plantado numa COPIA da arvore
em %TEMP% (nunca na worktree: um red team que restaura com git checkout apaga o que nao foi salvo), com
PYTHONDONTWRITEBYTECODE (mutante do mesmo tamanho engana o .pyc), e so conta se o sha256 do ficheiro mudou.

    py provas/_mutantes_preco_de_mercado.py [saida.json]

MORTO = tests.test_preco_de_mercado reprovou com o defeito plantado. SOBREVIVEU = os testes nao o viram."""
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
ALVO = "leis/preco_de_mercado.py"
COPIAR = ("leis/preco_de_mercado.py", "leis/regua_italia.py", "tests/test_preco_de_mercado.py",
          "data/samples/IT-SOURCE-SAMPLES/IT-T10-002/46622", "data/samples/IT-SOURCE-SAMPLES/IT-T10-002/46647",
          "data/samples/IT-SOURCE-SAMPLES/IT-T1-013/MANIFEST.json", "data/samples/IT-V2/IT-V2-CANONICO.json",
          "data/samples/RUN-MANIFEST.json")
M = [
    ("M1 comparacao desligada (o caso 2,80/2025)",
     [("    for m in RX_COMPARACAO.finditer(f):\n", "    for m in RX_COMPARACAO.finditer(''):\n")]),
    ("M2 «come nel» sai da comparacao",
     [(r"come\s+(?:nel|nello|nella|l['’])|", "")]),
    ("M3 publicacao nao tapada",
     [("    pub = [(m.start(), m.end()) for m in RX_PUBLICACAO.finditer(f)]\n", "    pub = []\n")]),
    ("M4 comparacao tapa so o marcador, nao o ano",
     [("        comp.append((m.start(), _fim_da_oracao(f, m.end())))\n", "        comp.append((m.start(), m.end()))\n")]),
    ("M5 preco da regua vira observacao",
     [("                papel = REFERENCIA\n", "                papel = OBSERVACAO\n")]),
    ("M6 regua sem periodo proprio",
     [("periodo_em(f[dentro[0]:dentro[1]])", "periodo_em(tapado)")]),
    ("M7 montante sem unidade nao e recusado",
     [('            recusados.append({"VALOR_TEXTO"', '            (lambda x: None)({"VALOR_TEXTO"')]),
    ("M8 projecao vira observacao",
     [("            if RX_PROJECAO.search(oracao):\n", "            if False:\n")]),
    ("M9 conflito de estagio escolhe o primeiro",
     [("    if len(achados) == 1:\n        (nome, trecho), = achados.items()\n",
       "    if achados:\n        nome, trecho = next(iter(achados.items()))\n")]),
    ("M10 CUN deixa de ser ingrosso",
     [(r"(?<![\w])CUN(?![\w])|", "")]),
    ("M11 serie sem exigir as cinco chaves",
     [("    if falta:\n", "    if False:\n")]),
    ("M12 milhar italiano lido como decimal",
     [('        return float(s.replace(".", "").replace(",", "."))\n', '        return float(s.replace(",", "."))\n')]),
    ("M13 orientativo vira observado",
     [('("ORIENTATIVO" if RX_ORIENTATIVO.search(f) else', '("ORIENTATIVO" if False else')]),
    ("M14 menu vira comentario",
     [("        if not precos and (len(f.split()) < PALAVRAS_MINIMAS or not RX_MERCADO.search(f)):\n",
       "        if not precos and not RX_MERCADO.search(f):\n")]),
    ("M15 «su base mensile» volta a levar a oracao",
     [("    comp += [(m.start(), m.end()) for m in RX_BASE_DA_VARIACAO.finditer(f)]\n",
       "    comp += [(m.start(), _fim_da_oracao(f, m.end())) for m in RX_BASE_DA_VARIACAO.finditer(f)]\n")]),
    ("M16 procura/venda sem porque proprio",
     [('    if RX_DOMANDA_VENDA.search(t):\n        return "VOLUME_DEMANDA_OU_VENDA_NAO_E_PRECO"\n', "")]),
    ("M17 a porta aceita a publicacao",
     [("def precos_do_texto(texto: str) -> dict:\n", "def precos_do_texto(texto: str, publication_time=None) -> dict:\n")]),
    ("M18 fatturato vira «preco sem unidade»",
     [('r"patrimonio", f, re.I)', 'r"patrimonio", "", re.I)')]),
    ("M19 ano solto da comparacao entra como periodo (sem tapar)",
     [("        tapado = _tapar(f, spans_comp + spans_pub)\n", "        tapado = _tapar(f, spans_pub)\n")]),
    ("M20 mes sem ano sem aviso",
     [('if tipo == "MES" and not re.search(r"\\d{4}", per) else "")', 'if False else "")')]),
]


def _sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    saida = Path(sys.argv[1]) if len(sys.argv) > 1 else None
    fonte = (RAIZ / ALVO).read_text(encoding="utf-8")
    env = dict(os.environ, PYTHONUTF8="1", PYTHONDONTWRITEBYTECODE="1", HTTP_PROXY="http://127.0.0.1:9",
               HTTPS_PROXY="http://127.0.0.1:9")
    res = []
    with tempfile.TemporaryDirectory(prefix="mut-preco-") as tmp:
        tmp = Path(tmp)
        for rel in COPIAR:
            (tmp / rel).parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(RAIZ / rel, tmp / rel)
        (tmp / "tests" / "__init__.py").write_text("", encoding="utf-8")
        base = subprocess.run([sys.executable, "-m", "unittest", "tests.test_preco_de_mercado"], cwd=tmp, env=env,
                              capture_output=True, text=True)
        if base.returncode != 0:
            print("A COPIA SEM MUTANTE JA REPROVA — mutacao sem valor\n" + base.stderr[-2000:])
            return 2
        sha0 = _sha(tmp / ALVO)
        for nome, trocas in M:
            s = fonte
            ok = all(s.count(a) == 1 for a, _b in trocas)
            if not ok:
                res.append({"MUTANTE": nome, "VEREDITO": "NAO_APLICOU"})
                print(nome, "NAO_APLICOU")
                continue
            for a, b in trocas:
                s = s.replace(a, b)
            (tmp / ALVO).write_text(s, encoding="utf-8", newline="\n")
            mudou = _sha(tmp / ALVO) != sha0
            r = subprocess.run([sys.executable, "-m", "unittest", "tests.test_preco_de_mercado"], cwd=tmp, env=env,
                               capture_output=True, text=True)
            ver = ("MORTO" if r.returncode != 0 else "SOBREVIVEU") if mudou else "SEM_DIFERENCA"
            ult = [ln for ln in r.stderr.splitlines() if ln.startswith(("FAIL:", "ERROR:"))]
            res.append({"MUTANTE": nome, "VEREDITO": ver, "SHA_MUDOU": mudou, "TESTES_QUE_APANHARAM": ult})
            print(nome, ver, "(%d testes vermelhos)" % len(ult))
            (tmp / ALVO).write_text(fonte, encoding="utf-8", newline="\n")
    mortos = sum(x["VEREDITO"] == "MORTO" for x in res)
    print("MORTOS %d/%d" % (mortos, len(M)))
    if saida:
        saida.write_text(json.dumps({"DATASET": "MUTACAO-PRECO-DE-MERCADO-V1", "ALVO": ALVO,
                                     "SHA256_DO_ALVO": _sha(RAIZ / ALVO), "MORTOS": mortos, "TOTAL": len(M),
                                     "MUTANTES": res}, ensure_ascii=False, indent=1) + "\n",
                         encoding="utf-8", newline="\n")
    return 0 if mortos == len(M) else 1


if __name__ == "__main__":
    sys.exit(main())
