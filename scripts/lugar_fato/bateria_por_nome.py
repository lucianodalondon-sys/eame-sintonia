#!/usr/bin/env python3
"""LUGAR-FATO · D70 · a bateria das leis do tempo do facto, POR NOME, antes e depois de mexer em
`leis/artefato.py`.

    py scripts/lugar_fato/bateria_por_nome.py <raiz da arvore> <saida.json>

Corre, um modulo de cada vez, todos os testes que importam `leis/artefato.py` (mais a lei do lugar e o
extrator), e a prova `provas/testa_golden_path_pdf.py`. Guarda o veredito de CADA teste pelo nome.
A rede fica fechada (proxy para uma porta morta): nenhum teste daqui deve sair para fora.
Comparar duas saidas: `--comparar antes.json depois.json` -> NEW_FAILURES_BY_NAME.
"""
import hashlib
import json
import os
import re
import subprocess
import sys
from pathlib import Path

MODULOS = (
    "test_a_collection_preserva_o_fato", "test_a_prova_e2e_segue_a_producao", "test_a_rota_do_html",
    "test_c10_1_source_id", "test_c10_3_location", "test_c4g_a_especie_do_video",
    "test_estagio_atravessa_a_fronteira", "test_fato_do_texto", "test_fonte_atravessa",
    "test_forward_instrumentado", "test_lingua_da_porta", "test_m2_rota_forward", "test_red_team_estrada",
    "test_reel_transcricao", "test_lugar_do_fato", "test_artefato_tempo_do_fato",
)
PROVAS = ("provas/testa_golden_path_pdf.py",)
RX = re.compile(r"^(test\w+) \(([\w.]+)\)(?:\s*\n?.*?)? \.\.\. (ok|FAIL|ERROR|skipped.*|expected failure|unexpected success)$",
                re.M)


def ambiente():
    e = dict(os.environ)
    for k in ("HTTP_PROXY", "HTTPS_PROXY", "http_proxy", "https_proxy", "ALL_PROXY"):
        e[k] = "http://127.0.0.1:9"
    e["NO_PROXY"] = e["no_proxy"] = ""
    e["PYTHONIOENCODING"] = "utf-8"
    return e


def correr(raiz):
    raiz = Path(raiz)
    res, brutos = {}, {}
    for m in MODULOS:
        if not (raiz / "tests" / (m + ".py")).exists():
            res["%s::(modulo)" % m] = "AUSENTE"
            continue
        p = subprocess.run([sys.executable, "-m", "unittest", "-v", "tests.%s" % m], cwd=raiz, env=ambiente(),
                           capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=900)
        brutos[m] = hashlib.sha256(p.stderr.encode("utf-8")).hexdigest()
        achados = RX.findall(p.stderr)
        for nome, classe, veredito in achados:
            res["%s::%s" % (classe, nome)] = "SKIP" if veredito.startswith("skipped") else veredito.upper()
        if not achados:
            res["%s::(modulo)" % m] = "SEM_TESTES_LIDOS rc=%d" % p.returncode
    for pv in PROVAS:
        p = subprocess.run([sys.executable, pv], cwd=raiz, env=ambiente(), capture_output=True, text=True,
                           encoding="utf-8", errors="replace", timeout=900)
        res["%s::(rc)" % pv] = "OK" if p.returncode == 0 else "FAIL rc=%d" % p.returncode
        brutos[pv] = hashlib.sha256((p.stdout + p.stderr).encode("utf-8")).hexdigest()
    return res, brutos


def main():
    if sys.argv[1] == "--comparar":
        a = json.loads(Path(sys.argv[2]).read_text(encoding="utf-8"))["TESTES"]
        d = json.loads(Path(sys.argv[3]).read_text(encoding="utf-8"))["TESTES"]
        mau = lambda v: v not in ("OK", "SKIP")
        novas = sorted(k for k in d if mau(d[k]) and not mau(a.get(k, "OK")))
        curadas = sorted(k for k in a if mau(a[k]) and not mau(d.get(k, "AUSENTE")))
        so_antes = sorted(set(a) - set(d))
        so_depois = sorted(set(d) - set(a))
        print(json.dumps({"NEW_FAILURES_BY_NAME": novas, "CURADAS": curadas, "SO_ANTES": so_antes,
                          "SO_DEPOIS": len(so_depois), "VERMELHOS_ANTES": sum(map(mau, a.values())),
                          "VERMELHOS_DEPOIS": sum(map(mau, d.values())), "TESTES_ANTES": len(a),
                          "TESTES_DEPOIS": len(d)}, ensure_ascii=False, indent=1))
        return
    res, brutos = correr(sys.argv[1])
    out = {"DATASET": "BATERIA-TEMPO-DO-FACTO-POR-NOME-V1", "RAIZ": sys.argv[1], "TESTES": dict(sorted(res.items())),
           "SHA256_DA_SAIDA_BRUTA": brutos}
    Path(sys.argv[2]).write_text(json.dumps(out, ensure_ascii=False, indent=1) + "\n", encoding="utf-8", newline="\n")
    mau = sum(v not in ("OK", "SKIP") for v in res.values())
    print("%d testes, %d nao-verdes -> %s" % (len(res), mau, sys.argv[2]))


if __name__ == "__main__":
    main()
