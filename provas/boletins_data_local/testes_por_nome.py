"""BOLETINS-V3 — corre a mesma lista de provas numa arvore e escreve, por NOME, o que falha. Serve para comparar
o ramo com o vivo: uma falha so conta como herdada se o vivo falhar com o MESMO nome. Sem rede.
uso: py provas/boletins_data_local/testes_por_nome.py <raiz> <saida.json>"""
import json
import os
import re
import subprocess
import sys
from pathlib import Path

RAIZ, SAIDA = Path(sys.argv[1]), Path(sys.argv[2])
PY_CURADORIA = ["test_canario_detalhe", "test_retirar_duplicadas_d49", "test_retirar_por_decisao", "test_revisao_ready",
                "test_regua_social", "test_soc_onda2_social", "test_soc2_curator_youtube", "test_soc4_handles",
                "test_d21_heranca", "test_nivel_da_fila", "test_ready_split", "test_collection_gate",
                "test_reconciliar_livros", "test_um_so_canario_promove", "test_reparar_contrato",
                "test_pagina_boletim", "test_boletim_data_local", "test_receita_identidade", "test_strip_suffix",
                "test_receita_pdf", "test_canario_pdf", "test_canario_hrefs", "test_robo_diag"]
PY_TESTS = ["test_importar_do_coletor", "test_legacy_colchetes", "test_legacy_recheck", "test_onboardar_rotas_provadas",
            "test_onda3_b_inerte", "test_receita_web_t8_t9_t12", "test_pagina_boletim_local",
            # INTEGRA-NOITE lote 1: os testes que cada pacote traz ou altera
            "test_prova_teto_social", "test_scrap_rc01_release_candidate", "test_social_bruto_leva_a_evidencia",
            "test_semear_so_as_candidatas", "test_d36_envelope_equivalente", "test_rota_video_d53",
            "test_youtube_pelo_scrap", "test_leitor_data_youtube", "test_tempo_e_lugar_da_publicacao"]
NODE = ["regras/motor_de_rota_test.mjs", "regras/boletim_data_local_test.mjs", "regras/recollection_test.mjs",
        "regras/incrementalidade_test.mjs", "regras/paridade_test.mjs", "regras/italy_contract_test.mjs",
        "provas/boletins_data_local/boletim_pdf_local.mjs", "provas/janela_formas/pagina_boletim_local.mjs"]
# REDE FECHADA (D41.3): proxy numa porta morta — nenhum teste sai para a rede, nem por engano
env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1", NODE_DISABLE_COMPILE_CACHE="1",
           HTTP_PROXY="http://127.0.0.1:9", HTTPS_PROXY="http://127.0.0.1:9", http_proxy="http://127.0.0.1:9",
           https_proxy="http://127.0.0.1:9", ALL_PROXY="http://127.0.0.1:9", NO_PROXY="127.0.0.1,localhost",
           no_proxy="127.0.0.1,localhost")
res = {}


def py(mod, cwd, nome):
    if not (cwd / (mod.split(".")[-1] + ".py")).exists():
        res[nome] = {"EXISTE": False}
        return
    r = subprocess.run([sys.executable, "-m", "unittest", mod], cwd=cwd, capture_output=True, text=True,
                       encoding="utf-8", errors="replace", env=env, timeout=1200)
    falhas = sorted(set(re.findall(r"^(?:FAIL|ERROR): (\S+) \(", r.stderr, re.M)))
    ran = re.search(r"^Ran (\d+) test", r.stderr, re.M)
    res[nome] = {"EXISTE": True, "CORRIDOS": int(ran.group(1)) if ran else None, "FALHAS": falhas, "RC": r.returncode}


for m in PY_CURADORIA:
    py(m, RAIZ / "curadoria", "curadoria/" + m)
for m in PY_TESTS:
    if (RAIZ / "tests" / (m + ".py")).exists():
        r = subprocess.run([sys.executable, "-m", "unittest", "tests." + m], cwd=RAIZ, capture_output=True, text=True,
                           encoding="utf-8", errors="replace", env=env, timeout=1200)
        falhas = sorted(set(re.findall(r"^(?:FAIL|ERROR): (\S+) \(", r.stderr, re.M)))
        ran = re.search(r"^Ran (\d+) test", r.stderr, re.M)
        res["tests/" + m] = {"EXISTE": True, "CORRIDOS": int(ran.group(1)) if ran else None, "FALHAS": falhas, "RC": r.returncode}
    else:
        res["tests/" + m] = {"EXISTE": False}
for f in NODE:
    if not (RAIZ / f).exists():
        res[f] = {"EXISTE": False}
        continue
    r = subprocess.run(["node", f], cwd=RAIZ, capture_output=True, text=True, encoding="utf-8", errors="replace",
                       env=env, timeout=1200)
    out = r.stdout + r.stderr
    falhas = sorted(set(l.strip() for l in out.splitlines() if re.match(r"^\s*(FAIL|FALHA)\b", l)))
    res[f] = {"EXISTE": True, "FALHAS": falhas, "RC": r.returncode, "FIM": (out.strip().splitlines() or [""])[-1][:120]}
SAIDA.write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")
print(json.dumps({k: (len(v["FALHAS"]) if v.get("EXISTE") else "nao existe") for k, v in res.items()}, ensure_ascii=False))
