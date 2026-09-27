"""COMENTARIOS-V1 — corre a lista de provas vizinhas numa arvore e escreve, por NOME, o que falha.
Uma falha so conta como herdada se a base falhar com o MESMO nome. Rede fechada (proxy numa porta morta).
uso: py provas/comentarios_v1/testes_por_nome.py <raiz> <saida.json>"""
import json
import os
import re
import subprocess
import sys
from pathlib import Path

RAIZ, SAIDA = Path(sys.argv[1]), Path(sys.argv[2])
# os testes dos donos que o extrator de voz IMPORTA (leitor italiano do lugar/tempo, lei do lugar, vocabulario
# do recorte, mencoes EPPO), os da transcricao de onde vem o texto, os do mapa, e o novo
PY_TESTS = ["test_comentarios_v1", "test_mapa_nao_mente", "test_o_mapa_da_intelligence_nao_mente",
            "test_as_duas_portas_do_scrap",
            "test_c10_4_route_gate",
            "test_c10_4b_um_caminho_so",
            "test_c10_4c_rota_aposentada",
            "test_c10_5_collection_flow",
            "test_c10_5d_decisao_instagram",
            "test_c10_6_crash_retry",
            "test_c10_6d_portas_canonicas",
            "test_c10_6e_runtime_pago",
            "test_c10_7_ensaio_canonico",
            "test_c10_8a_bluesky_ao_vivo",
            "test_c10_8af_orcamento_financeiro",
            "test_c10_8ar_orcamento_de_rede",
            "test_c10_8b_live_disparador",
            "test_c10_8b_r_raw_entre_jobs",
            "test_c10_8b_rota_paga_canonica",
            "test_c10_audio_only",
            "test_c12_x_censo",
            "test_c13_executor_wiring",
            "test_c13_route_gate",
            "test_c13_youtube_public_audio",
            "test_c14c_permissao_instagram",
            "test_c2_youtube_oficial",
            "test_c3_youtube_cutover",
            "test_c5_transcript_gate",
            "test_c6_especie_do_texto",
            "test_cadeia_do_audio_offline",
            "test_col_e7_contrato_do_texto",
            "test_d24_video_de_pessoa",
            "test_d36_envelope_equivalente",
            "test_d37_campos_de_politica",
            "test_falhas",
            "test_linkedin_build_01_local_first",
            "test_linkedin_op_01_operacional",
            "test_politica_da_coleta",
            "test_prontidao_social_v1",
            "test_receita_web_t8_t9_t12",
            "test_rota_video_d53",
            "test_scrap_convergencia",
            "test_scrap_flow01_caminho_canonico",
            "test_scrap_rc01_release_candidate",
            "test_social_sessao",
            "test_thread_parcial",
            "test_youtube_antidrift",
            "test_youtube_checkpoint_pg",
            "test_youtube_oficial",
            "test_youtube_piloto",
            "test_yt_metadados_do_audio"]
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
                       encoding="utf-8", errors="replace", env=env, timeout=900)
    falhas = sorted(set(re.findall(r"^(?:FAIL|ERROR): (\S+ \(\S+\))", r.stderr, re.M)))
    ran = re.search(r"^Ran (\d+) test", r.stderr, re.M)
    res["tests/" + m] = {"EXISTE": True, "CORRIDOS": int(ran.group(1)) if ran else None, "FALHAS": falhas,
                         "RC": r.returncode}
SAIDA.parent.mkdir(parents=True, exist_ok=True)
SAIDA.write_text(json.dumps(res, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
for k, v in res.items():
    print(k, v.get("CORRIDOS"), len(v.get("FALHAS", [])) if v.get("EXISTE") else "NAO EXISTE")
