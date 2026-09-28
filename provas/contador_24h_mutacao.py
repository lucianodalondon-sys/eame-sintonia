"""CONTADOR (D90) AGORA ADAPTATIVO (D124) · o ataque: cada peca desligada, uma de cada vez, numa COPIA.

    py provas/contador_24h_mutacao.py [--ref=HEAD] [--so=NOME,NOME]

A copia sai de `git archive <ref>` para uma pasta temporaria: o repositorio nao e tocado.
Cada mutante troca UM trecho exacto de um ficheiro; se o trecho nao existir uma vez so, o
ataque falha alto (um mutante que nao muda nada nao prova nada).
MORTO = `tests/test_cortesia_adaptativa.py` ou `tests/test_contador_24h.py` (este corre o ensaio do
transporte contra o servidor local, `provas/contador_24h_local.mjs`) reprova ou sai com codigo != 0.
Resultado em `provas/CONTADOR-24H-MUTACAO.json`.

Os cinco que a missao D124 nomeou: TIRAR O RECUO · IGNORAR O RETRY-AFTER · RAJADA NO MESMO DOMINIO ·
ROBOTS ILEGIVEL = PERMISSAO · CONTADOR NAO ATOMICO — em Python e no gemeo Node. E mais os que a regra
nova abriu: dobrar sem prova, pausa ignorada, 2 sinais sem pausa, transporte que nao regista a resposta,
prova-teto cega ao Retry-After, livro ilegivel lido como vazio.
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
from concurrent.futures import ThreadPoolExecutor

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PY = "coleta/cortesia_adaptativa.py"
MJS = "coleta/cortesia_adaptativa.mjs"
JS = "coleta/italy_pilot_collect.mjs"
PT = "provas/prova_teto_dominio.py"
MUTANTES = [
    # ── os cinco da missao ──
    ("M1_PY_SEM_RECUO", PY, 'nivel = max(int(k["MINIMO"]), int(math.floor(nivel * R["FATOR"])))', "nivel = nivel"),
    ("M1_JS_SEM_RECUO", MJS, "nivel = Math.max(Math.trunc(k.MINIMO), Math.floor(nivel * R.FATOR));", "nivel = nivel;"),
    ("M2_PY_IGNORA_RETRY_AFTER", PY, 'retry_ate = max(retry_ate, t + float(e["RETRY_AFTER_S"]))', "retry_ate = retry_ate"),
    ("M2_JS_IGNORA_RETRY_AFTER", MJS, "if (e.RETRY_AFTER_S) retryAte = Math.max(retryAte, t + Number(e.RETRY_AFTER_S));", ""),
    ("M3_PY_RAJADA_NO_MESMO_DOMINIO", PY, '            elif e["EM_CURSO_ATE"] is not None:', "            elif False:"),
    ("M3_JS_RAJADA_NO_MESMO_DOMINIO", MJS, 'else if (e.EM_CURSO_ATE !== null) [porque, ate] = ["UM_DE_CADA_VEZ", e.EM_CURSO_ATE];', ""),
    ("M4_JS_ROBOTS_ILEGIVEL_E_PERMISSAO", JS,
     '  if (rb.estado === "ILEGIVEL") return { recusado: "ROBOTS_ILEGIVEL", porque: rb.porque };', ""),
    ("M5_PY_CONTADOR_NAO_ATOMICO", PY, "                os.mkdir(self.d)\n                return self", "                return self"),
    ("M5_JS_CONTADOR_NAO_ATOMICO", MJS, "    try { mkdirSync(t); break; }", "    try { break; }"),
    # ── os que a regra nova abriu ──
    ("M6_PY_DOBRA_SEM_PROVA_DE_USO", PY,
     'if k["DOBRA"] and not teve_sinal and usados > 0 and usados >= math.ceil(R["FRACAO_DE_USO_PARA_DOBRAR"] * nivel):',
     'if k["DOBRA"] and not teve_sinal:'),
    ("M7_PY_DOBRA_SEM_TETO_DE_SEGURANCA", PY, 'nivel = min(int(k["TETO"]), nivel * 2)', "nivel = nivel * 2"),
    ("M8_PY_PAUSA_MINIMA_IGNORADA", PY, '            elif e["PAUSA_ATE"] is not None and e["PAUSA_ATE"] > t:', "            elif False:"),
    ("M9_PY_DOIS_SINAIS_SEM_PAUSA", PY, 'pausado_ate = max(pausado_ate, t + float(R["PAUSA_S"]))', "pausado_ate = pausado_ate"),
    ("M10_JS_TRANSPORTE_NAO_REGISTA_A_RESPOSTA", JS, "    registarResposta(host, url, { ...resposta, cabecalhos });", ""),
    ("M11_JS_TRANSPORTE_NAO_RESERVA", JS, "  if (livro24h()) {\n    let r;", "  if (false) {\n    let r;"),
    ("M12_PY_ILEGIVEL_VIRA_VAZIO", PY, '            raise LivroIlegivel("linha %d nao e JSON: %s" % (i, ex))', "            continue"),
    ("M13_PY_429_NAO_E_SINAL", PY, '        sinais.append("HTTP_429")', "        pass"),
    ("M14_JS_DESAFIO_NAO_E_SINAL", MJS, '  if (desafio) sinais.push("PAGINA_DE_DESAFIO");', ""),
    ("M15_PROVA_CEGA_AO_RETRY_AFTER", PT, "                if t < retry_ate:", "                if False:"),
    ("M16_PY_SEM_ALERTA", PY, "    _acrescentar(a, b)\n    return b", "    return b"),
]
TESTES = ["tests/test_cortesia_adaptativa.py", "tests/test_contador_24h.py"]


def copia(ref, destino):
    tar = subprocess.run(["git", "-C", RAIZ, "archive", "--format=tar", ref], capture_output=True, check=True).stdout
    with tarfile.open(fileobj=io.BytesIO(tar)) as t:
        t.extractall(destino)


def correr(pasta):
    env = dict(os.environ, PYTHONUTF8="1", PYTHONDONTWRITEBYTECODE="1", NODE_DISABLE_COMPILE_CACHE="1",
               HTTPS_PROXY="http://127.0.0.1:9", HTTP_PROXY="http://127.0.0.1:9")
    for k in ("SINTONIA_TETO_24H", "SINTONIA_CORTESIA_LIVRO", "SINTONIA_TETO_POR_HOST", "SINTONIA_CORTESIA_POLITICA"):
        env.pop(k, None)
    cods, n, cauda = [], 0, ""
    for t in TESTES:
        r = subprocess.run([sys.executable, t], cwd=pasta, env=env, capture_output=True,
                           text=True, encoding="utf-8", errors="replace", timeout=1800)
        m = re.search(r"Ran (\d+) test", r.stderr)
        cods.append(r.returncode)
        n += int(m.group(1)) if m else 0
        falhas = re.findall(r"^(?:FAIL|ERROR): (\w+)", r.stderr, re.M)
        cauda += "%s rc=%d falhas=%s\n" % (t, r.returncode, falhas[:6])
    return max(cods), n, cauda


def main():
    ref = next((a.split("=", 1)[1] for a in sys.argv[1:] if a.startswith("--ref=")), "HEAD")
    so = next((a.split("=", 1)[1].split(",") for a in sys.argv[1:] if a.startswith("--so=")), None)
    base = tempfile.mkdtemp(prefix="contador24h-mutacao-")
    out = {"REF": subprocess.run(["git", "-C", RAIZ, "rev-parse", "--short", ref], capture_output=True,
                                 text=True).stdout.strip(), "TESTES": TESTES, "MUTANTES": []}
    try:
        limpa = os.path.join(base, "limpa")
        copia(ref, limpa)
        cod, n, cauda = correr(limpa)
        out["SEM_MUTANTE"] = {"CODIGO": cod, "TESTES": n}
        if cod != 0:
            raise SystemExit("a copia limpa nao passa — o ataque nao tem base:\n" + cauda)

        def um(m):
            nome, alvo, de, para = m
            pasta = os.path.join(base, nome)
            shutil.copytree(limpa, pasta)
            f = os.path.join(pasta, alvo)
            with open(f, encoding="utf-8", newline="") as h:
                s = h.read().replace("\r\n", "\n")
            if s.count(de) != 1:
                return {"MUTANTE": nome, "ALVO": alvo, "ESTADO": "NAO_APLICOU", "OCORRENCIAS": s.count(de)}
            with open(f, "w", encoding="utf-8", newline="\n") as h:
                h.write(s.replace(de, para))
            c, k, cauda = correr(pasta)
            shutil.rmtree(pasta, ignore_errors=True)
            return {"MUTANTE": nome, "ALVO": alvo, "ESTADO": "MORTO" if c != 0 else "VIVO", "CODIGO": c,
                    "TESTES": k, "QUEM_APANHOU": cauda.strip().splitlines()}
        alvo = [m for m in MUTANTES if so is None or m[0] in so]
        with ThreadPoolExecutor(int(os.environ.get("MUTACAO_TRABALHADORES", "3"))) as ex:
            for r in ex.map(um, alvo):
                out["MUTANTES"].append(r)
                print("%-42s %s" % (r["MUTANTE"], r["ESTADO"]), flush=True)
    finally:
        shutil.rmtree(base, ignore_errors=True)
    mortos = sum(1 for m in out["MUTANTES"] if m["ESTADO"] == "MORTO")
    out["RESUMO"] = "%d/%d mortos" % (mortos, len(out["MUTANTES"]))
    with open(os.path.join(RAIZ, "provas", "CONTADOR-24H-MUTACAO.json"), "w", encoding="utf-8") as h:
        json.dump(out, h, ensure_ascii=False, indent=1)
    print("CONTADOR (D124) MUTACAO:", out["RESUMO"])
    return 0 if mortos == len(out["MUTANTES"]) else 1


if __name__ == "__main__":
    raise SystemExit(main())
