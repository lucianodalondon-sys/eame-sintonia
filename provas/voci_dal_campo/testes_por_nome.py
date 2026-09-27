"""VOCI-DAL-CAMPO — corre a lista de provas vizinhas numa arvore e escreve, por NOME, o que falha.
Uma falha so conta como herdada se a base falhar com o MESMO nome. Rede fechada (proxy numa porta morta).
uso: py provas/voci_dal_campo/testes_por_nome.py <raiz> <saida.json>"""
import json
import os
import re
import subprocess
import sys
from pathlib import Path

RAIZ, SAIDA = Path(sys.argv[1]), Path(sys.argv[2])
# os testes dos donos que o extrator de voz IMPORTA (leitor italiano do lugar/tempo, lei do lugar, vocabulario
# do recorte, mencoes EPPO), os da transcricao de onde vem o texto, os do mapa, e o novo
PY_TESTS = ["test_voce_dal_campo", "test_fato_do_texto", "test_lugar_do_fato", "test_c7_lugar_do_fato",
            "test_cicatrizes_brasil", "test_c8_convergencia", "test_c6_especie_do_texto", "test_c5_transcript_gate",
            "test_reel_transcricao", "test_artefato_tempo_do_fato", "test_a_collection_preserva_o_fato",
            "test_mapa_nao_mente", "test_o_mapa_da_intelligence_nao_mente"]
env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1",
           HTTP_PROXY="http://127.0.0.1:9", HTTPS_PROXY="http://127.0.0.1:9", http_proxy="http://127.0.0.1:9",
           https_proxy="http://127.0.0.1:9", ALL_PROXY="http://127.0.0.1:9", NO_PROXY="127.0.0.1,localhost",
           no_proxy="127.0.0.1,localhost")
res = {}
for m in PY_TESTS:
    if not (RAIZ / "tests" / (m + ".py")).exists():
        res["tests/" + m] = {"EXISTE": False}
        continue
    r = subprocess.run([sys.executable, "-m", "unittest", "tests." + m], cwd=RAIZ, capture_output=True, text=True,
                       encoding="utf-8", errors="replace", env=env, timeout=1200)
    falhas = sorted(set(re.findall(r"^(?:FAIL|ERROR): (\S+ \(\S+\))", r.stderr, re.M)))
    ran = re.search(r"^Ran (\d+) test", r.stderr, re.M)
    res["tests/" + m] = {"EXISTE": True, "CORRIDOS": int(ran.group(1)) if ran else None, "FALHAS": falhas,
                         "RC": r.returncode}
SAIDA.parent.mkdir(parents=True, exist_ok=True)
SAIDA.write_text(json.dumps(res, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
for k, v in res.items():
    print(k, v.get("CORRIDOS"), len(v.get("FALHAS", [])) if v.get("EXISTE") else "NAO EXISTE")
