"""INDEPENDENCIA-V1 — corre a mesma lista de modulos de teste numa arvore e escreve, por NOME, o que falha.
Serve para comparar a base (69b0e23f) com o ramo: uma falha so conta como herdada se a base falhar com o
MESMO nome. Rede fechada por proxy numa porta morta (D41.3).
uso: py provas/independencia/testes_por_nome.py <raiz> <saida.json> [modulo ...]

Sem pytest nesta maquina (medido 26/09: `No module named pytest`). Os modulos escritos como funcoes soltas
`test_*` (estilo pytest) davam «Ran 0» no unittest — zero protecao calada. Para esses, e so esses, o corredor
chama cada funcao `test_*` numa copia do Python, e uma excepcao e FALHA com o nome da funcao."""
import json
import os
import re
import subprocess
import sys
from pathlib import Path

RAIZ, SAIDA = Path(sys.argv[1]), Path(sys.argv[2])
# os modulos de tests/ que tocam a Intelligence, o motor V2.1 ou a espinha (git grep, 26/09), mais o novo
MODULOS = [
    "test_a_collection_preserva_o_fato", "test_a_demanda_de_dados_da_italia", "test_a_fase_10_entra_no_acervo",
    "test_a_porta_cli_liga_o_banco", "test_a_primeira_corrida_da_inteligencia", "test_a_sala_de_espera_tem_um_dono",
    "test_adama_catalogo_drift", "test_adama_relevance", "test_atomicidade_da_intelligence", "test_c10_4_route_gate",
    "test_c10_4b_um_caminho_so", "test_c10_4c_rota_aposentada", "test_c10_8b_live_disparador", "test_c10_audio_only",
    "test_c2_youtube_oficial", "test_c4_gpu_local", "test_c4d_ferro_negociado", "test_c7_lugar_do_fato",
    "test_calendario_temporal", "test_cliente_postgres", "test_completude_oportunidade",
    "test_consumo_da_referencia_adama", "test_espinha_da_intelligence", "test_fase_italiana_no_workflow",
    "test_integracao_04a_curator", "test_migracao_033_sala", "test_migrations",
    "test_modelo_de_objetos_da_intelligence", "test_nome_da_pasta_windows", "test_o_controle_separa_lei_de_mencao",
    "test_o_mapa_da_intelligence_nao_mente", "test_o10r_a_verdade_dos_nomes", "test_operacao",
    "test_porta_de_producao", "test_preflight_de_egresso", "test_preservar_coleta_no_banco",
    "test_prioridade_comercial", "test_psql_argv", "test_reel_transcricao", "test_relevance_priority_sobrecarga",
    "test_scrap_convergencia", "test_security_ratchet", "test_social_sessao", "test_trava_da_inteligencia",
    "test_v21_datas", "test_v21_geografia", "test_v21_mercado", "test_v21_traducao_trava",
    "test_youtube_pelo_scrap", "test_ausencia_na_fronteira_da_corrida", "test_corrida_abortada",
    # INDEPENDENCIA-V1: o teste novo (na base nao existe, e fica registado assim)
    "test_independencia_de_fontes",
]
env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1",
           HTTP_PROXY="http://127.0.0.1:9", HTTPS_PROXY="http://127.0.0.1:9", http_proxy="http://127.0.0.1:9",
           https_proxy="http://127.0.0.1:9", ALL_PROXY="http://127.0.0.1:9", NO_PROXY="127.0.0.1,localhost",
           no_proxy="127.0.0.1,localhost")
SOLTAS = r"""
import importlib, sys, traceback
sys.path.insert(0, '.')
mod = importlib.import_module('tests.' + sys.argv[1])
n = 0
for nome in sorted(dir(mod)):
    f = getattr(mod, nome)
    if nome.startswith('test_') and callable(f) and not isinstance(f, type):
        n += 1
        try:
            f()
        except Exception:
            print('FAIL: %s (funcao)' % nome, file=sys.stderr)
print('Ran %d tests' % n, file=sys.stderr)
"""
if len(sys.argv) > 3:
    MODULOS = sys.argv[3:]
res = {}
for m in MODULOS:
    if not (RAIZ / "tests" / (m + ".py")).exists():
        res["tests/" + m] = {"EXISTE": False}
        continue
    r = subprocess.run([sys.executable, "-m", "unittest", "tests." + m], cwd=RAIZ, capture_output=True, text=True,
                       encoding="utf-8", errors="replace", env=env, timeout=1200)
    falhas = sorted(set(re.findall(r"^(?:FAIL|ERROR): (\S+) \(", r.stderr, re.M)))
    ran = re.search(r"^Ran (\d+) test", r.stderr, re.M)
    modo = "unittest"
    if ran and int(ran.group(1)) == 0:
        r = subprocess.run([sys.executable, "-c", SOLTAS, m], cwd=RAIZ, capture_output=True, text=True,
                           encoding="utf-8", errors="replace", env=env, timeout=1200)
        falhas = sorted(set(re.findall(r"^(?:FAIL|ERROR): (\S+) \(", r.stderr, re.M)))
        ran = re.search(r"^Ran (\d+) test", r.stderr, re.M)
        modo = "funcoes_soltas"
    res["tests/" + m] = {"EXISTE": True, "CORRIDOS": int(ran.group(1)) if ran else None, "FALHAS": falhas,
                         "RC": r.returncode, "MODO": modo}
    print(m, res["tests/" + m].get("CORRIDOS"), len(falhas), flush=True)
SAIDA.parent.mkdir(parents=True, exist_ok=True)
SAIDA.write_text(json.dumps(res, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
