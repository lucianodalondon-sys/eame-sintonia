"""SOCIAL-ONDA · o ataque: cada regra nova da onda social desligada, uma de cada vez, numa COPIA.

    py provas/social_onda/mutacao_onda_social.py [--ref=HEAD]

O metodo e o de `provas/t9_social/mutacao_porta_social.py` (e de `provas/coleta_continua_mutacao.py`): a copia sai
de `git archive <ref>` (o repositorio nao e tocado); cada mutante troca UM trecho exacto; um trecho que nao apareca
exactamente uma vez falha ALTO (MUTANTE_SEM_ALVO — nunca conta como morto); o ficheiro e reposto byte a byte depois
de cada mutante; sem .pyc (PYTHONDONTWRITEBYTECODE e __pycache__ apagado antes de cada corrida). MORTO = os testes
saem com codigo != 0. Proxy fechado no processo dos testes. Resultado em `provas/social_onda/ONDA-SOCIAL-MUTACAO.json`.
"""
import io
import json
import os
import re
import shutil
import subprocess
import sys
import tarfile
import tempfile

RAIZ = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CC = "ferramentas/big_collection/coleta_continua.py"
POS = "curadoria/plano_onda_social.py"
TESTES = ["tests.test_onda_social_coleta", "tests.test_porta_social_t9"]
MUTANTES = [
    # ── a flag do dono ──
    ("S01_FLAG_IGNORADA_NO_ALIMENTADOR", CC, "        if f.get(\"PEDE_AUTORIZACAO\") and not autorizado_social:",
     "        if False:"),
    ("S02_MAIN_LIGA_SEMPRE", CC, "autorizado_social=\"--autorizado-pelo-dono\" in argv)", "autorizado_social=True)"),
    ("S03_CATALOGO_NAO_PEDE_AUTORIZACAO", CC, "            \"PEDE_AUTORIZACAO\": (", "            \"PEDE_AUTORIZACAO_X\": ("),
    ("S04_CANDIDATAS_PASSAM_COM_BLOQUEIO", CC, "\"CANDIDATAS\": [] if motivos else list(f.get(\"CANDIDATAS\") or []),",
     "\"CANDIDATAS\": list(f.get(\"CANDIDATAS\") or []),"),
    # ── a onda da linha ──
    ("S05_SOCIAL_SEM_ONDA", CC, "     \"ONDA\": \"ferramentas/maestro_social/maestro_social.py --correr",
     "     \"ONDA_X\": \"ferramentas/maestro_social/maestro_social.py --correr"),
    ("S06_SOCIAL_NA_ONDA_DOS_SITES", CC, "ONDA_DA_LINHA = {\"SOCIAL\": \"onda_social\"}", "ONDA_DA_LINHA = {}"),
    ("S07_PECAS_REAIS_SEM_ONDA_SOCIAL", CC, "\"fonte\": portao_da_fonte_real, \"onda_social\": onda_social_real}",
     "\"fonte\": portao_da_fonte_real}"),
    # ── so as ACEITES, so com rota que ja existe ──
    ("S08_RECUSADA_VIRA_CANDIDATA", CC, "    cands, sem_rota = candidatas_sociais(sociais, contratos)\n",
     "    cands, sem_rota = candidatas_sociais(sorted(contratos), contratos)\n"),
    ("S09_ROTA_INVENTADA_PARA_QUALQUER_FASE", CC, "        p = previsto.get(fase)\n",
     "        p = previsto.get(fase) or {\"youtube.com\": 4}\n"),
    ("S10_ACEITES_SEM_ROTA_CALADAS", CC, "    if sociais and not cands:\n", "    if False:\n"),
    ("S11_PREVISTOS_SUBCONTADOS", CC, "\"PREVISTOS\": sum(p.values()),", "\"PREVISTOS\": 1,"),
    ("S12_SO_O_PRIMEIRO_DOMINIO", CC, "\"DOMINIOS\": sorted(p),", "\"DOMINIOS\": sorted(p)[:1],"),
    # ── o maestro que ja existia, pela linha de comando de sempre ──
    ("S13_MAESTRO_SEM_A_FLAG", CC, "\"--correr\", \"--autorizado-pelo-dono\", \"--saida=\"", "\"--correr\", \"--saida=\""),
    ("S14_MAESTRO_COM_CANARIO", CC, "           \"--fontes=\" + \",\".join(fontes)]",
     "           \"--fontes=\" + \",\".join(fontes), \"--canario\"]"),
    # ── o estado da onda que o ciclo, a prova e a reconciliacao leem ──
    ("S15_MAESTRO_SEM_ESTADO_NAO_PARA", CC, "        estado[\"PAROU\"] = {\"PORQUE\": \"MAESTRO_SEM_ESTADO:",
     "        estado[\"PAROU_X\"] = {\"PORQUE\": \"MAESTRO_SEM_ESTADO:"),
    ("S16_PAROU_DO_MAESTRO_IGNORADO", CC, "        estado[\"PAROU\"] = m.get(\"PAROU\")\n", "        estado[\"PAROU\"] = None\n"),
    ("S17_RUN_ID_NAO_TRADUZIDO", CC, "(\"SOURCE_ID\", \"CORREU\", \"RUN_ID\", \"STATUS\",", "(\"SOURCE_ID\", \"CORREU\", \"STATUS\","),
    ("S18_PEDIDOS_POR_DOMINIO_A_ZERO", CC, "                ped[d] = ped.get(d, 0) + int(n)\n", "                ped[d] = 0\n"),
    ("S19_LIVRO_DA_ONDA_NAO_SOMA", CC, "                soma[d] = soma.get(d, 0) + int(n)\n", "                soma[d] = 0\n"),
    ("S20_LIVRO_ILEGIVEL_VIRA_ZERO", CC, "json.dumps({\"LIVROS_ILEGIVEIS\": ilegiveis} if ilegiveis else",
     "json.dumps({\"PEDIDOS_POR_DOMINIO\": soma} if ilegiveis else"),
    ("S21_SEM_FOTO_DA_SALA_ANTES", CC, "\"SALA_INICIO\": foto(),", "\"SALA_INICIO\": None,"),
    # ── Instagram: so a URL directa do Reel ──
    ("S22_PERFIL_DO_INSTAGRAM_NAO_E_LISTAGEM", POS, "    if esp.get(\"ESPECIE\") != \"REEL\":\n", "    if False:\n"),
    ("S23_REEL_SEM_URL_SEM_NOME", POS, "    if not url:\n        return [(\"ROTA_NAO_CONFERIDA\"",
     "    if False:\n        return [(\"ROTA_NAO_CONFERIDA\""),
    ("S24_GUARDA_DO_REEL_DESLIGADA", POS, "    m += _reel_por_url_directa(plat, aq) + _rastro_do_dono(plat, aq)",
     "    m += _rastro_do_dono(plat, aq)"),
]


def copia(ref, destino):
    tar = subprocess.run(["git", "-C", RAIZ, "archive", "--format=tar", ref], capture_output=True, check=True).stdout
    with tarfile.open(fileobj=io.BytesIO(tar)) as t:
        t.extractall(destino)


def sem_pyc(pasta):
    for d in ("curadoria", os.path.join("ferramentas", "big_collection"), os.path.join("ferramentas", "maestro_social"),
              "tests", "coleta"):
        shutil.rmtree(os.path.join(pasta, d, "__pycache__"), ignore_errors=True)


def correr(pasta):
    sem_pyc(pasta)
    env = dict(os.environ, PYTHONUTF8="1", PYTHONDONTWRITEBYTECODE="1",
               HTTPS_PROXY="http://127.0.0.1:9", HTTP_PROXY="http://127.0.0.1:9", NO_PROXY="127.0.0.1,localhost")
    r = subprocess.run([sys.executable, "-m", "unittest"] + TESTES, cwd=pasta, env=env, capture_output=True,
                       text=True, encoding="utf-8", errors="replace", timeout=900)
    m = re.search(r"Ran (\d+) test", r.stderr)
    return r.returncode, int(m.group(1)) if m else None, r.stderr[-600:]


def main():
    ref = next((a.split("=", 1)[1] for a in sys.argv[1:] if a.startswith("--ref=")), "HEAD")
    base = tempfile.mkdtemp(prefix="onda-social-mutacao-")
    out = {"REF": subprocess.run(["git", "-C", RAIZ, "rev-parse", "--short", ref], capture_output=True,
                                 text=True).stdout.strip(), "TESTES": TESTES, "MUTANTES": []}
    try:
        limpa = os.path.join(base, "limpa")
        copia(ref, limpa)
        cod, n, cauda = correr(limpa)
        out["SEM_MUTANTE"] = {"CODIGO": cod, "TESTES": n}
        if cod != 0:
            raise SystemExit("a copia limpa nao passa — o ataque nao tem base:\n" + cauda)
        for nome, alvo, de, para in MUTANTES:
            f = os.path.join(limpa, alvo)
            with open(f, "rb") as h:
                original = h.read()
            s = original.decode("utf-8")
            s2 = s.replace("\r\n", "\n")
            if s2.count(de) != 1:
                raise SystemExit("MUTANTE_SEM_ALVO %s: o trecho aparece %d vezes em %s" % (nome, s2.count(de), alvo))
            s2 = s2.replace(de, para)
            with open(f, "wb") as h:
                h.write((s2.replace("\n", "\r\n") if "\r\n" in s else s2).encode("utf-8"))
            try:
                cod, n, cauda = correr(limpa)
            finally:
                with open(f, "wb") as h:
                    h.write(original)
            morto = cod != 0
            out["MUTANTES"].append({"MUTANTE": nome, "ALVO": alvo, "MORTO": morto, "CODIGO": cod, "TESTES": n,
                                    "CAUDA": None if morto else cauda})
            print(nome, "MORTO" if morto else "SOBREVIVEU", flush=True)
        cod, n, cauda = correr(limpa)                                  # a copia reposta volta a passar
        out["DEPOIS_DO_ATAQUE"] = {"CODIGO": cod, "TESTES": n}
        if cod != 0:
            raise SystemExit("a copia nao voltou ao original depois do ataque:\n" + cauda)
    finally:
        shutil.rmtree(base, ignore_errors=True)
    out["MORTOS"] = sum(1 for m in out["MUTANTES"] if m["MORTO"])
    out["TOTAL"] = len(out["MUTANTES"])
    with open(os.path.join(RAIZ, "provas", "social_onda", "ONDA-SOCIAL-MUTACAO.json"), "w", encoding="utf-8",
              newline="\n") as h:
        json.dump(out, h, ensure_ascii=False, indent=1)
        h.write("\n")
    print("ONDA_SOCIAL_MUTACAO · mortos=%d de %d" % (out["MORTOS"], out["TOTAL"]))
    return 0 if out["MORTOS"] == out["TOTAL"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
