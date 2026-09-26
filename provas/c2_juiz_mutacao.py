"""C2-JUIZ · o ataque: cada peca da V2 (lista com «leia mais») desligada, uma de cada vez, numa COPIA.

    py provas/c2_juiz_mutacao.py [--ref=HEAD]

A copia sai de `git archive <ref>` para uma pasta temporaria: o repositorio nao e tocado.
Cada mutante troca UM trecho exacto de um ficheiro; se o trecho nao existir uma vez so, o
ataque falha alto (um mutante que nao muda nada nao prova nada).
MORTO = `tests/test_c2_juiz.py` reprova ou sai com codigo != 0.
Resultado em `provas/C2-JUIZ-MUTACAO.json`.
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

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PY = "curadoria/retrato_html.py"
JS = "coleta/retrato_html.mjs"
ADM = "admissao/admissao.py"
MUTANTES = [
    ("M01_V2_DESLIGADA", PY, "V2_LIGADA = True", "V2_LIGADA = False"),
    ("M02_LIMIAR_11", PY, "LEIA_MAIS_MINIMO = 6", "LEIA_MAIS_MINIMO = 11"),
    ("M03_SEM_LEGGI_TUTTO", PY, '_LEIA_MAIS = re.compile(r"(leggi\\s+tutto|', '_LEIA_MAIS = re.compile(r"('),
    ("M04_VEREDITO_IGNORA_V2", PY, '    if e_lista_com_leia_mais(retrato):\n        return REGRA_V2, "CAPA_PROVAVEL"\n', ""),
    ("M05_V2_APERTA_TAMBEM_NAO_SEI", PY, 'r.get("CAPA_OU_MATERIA") == "MATERIA_PROVAVEL"\n            and ', ""),
    # D79: contar LIGACOES, nao ocorrencias
    ("M06_PY_CONTA_A_FRASE_NO_HTML", PY, '"READ_MORE_LINKS": ligacoes_leia_mais(fonte),',
     '"READ_MORE_LINKS": len(_LEIA_MAIS.findall(fonte)),'),
    ("M07_PY_CONTEM_EM_VEZ_DE_COMECA", PY, "if any(_LEIA_MAIS.match(t) for t in [texto] + rotulos):",
     "if any(_LEIA_MAIS.search(t) for t in [texto] + rotulos):"),
    ("M08_PY_SEM_ROTULO", PY, "if any(_LEIA_MAIS.match(t) for t in [texto] + rotulos):",
     "if any(_LEIA_MAIS.match(t) for t in [texto]):"),
    ("M09_NODE_LIMIAR_11", JS, "export const LEIA_MAIS_MINIMO = 6;", "export const LEIA_MAIS_MINIMO = 11;"),
    ("M10_NODE_FRONTEIRA_ASCII", JS, ")(?![\\p{L}\\p{N}_])/iu;", ")\\b/iu;"),
    ("M11_NODE_VEREDITO_IGNORA_V2", JS, '  if (eListaComLeiaMais(retrato)) return [REGRA_V2, "CAPA_PROVAVEL"];\n', ""),
    ("M12_NODE_CONTA_A_FRASE_NO_HTML", JS, "    READ_MORE_LINKS: ligacoesLeiaMais(fonte),",
     "    READ_MORE_LINKS: (fonte.match(/(leggi\\s+tutto|leggi\\s+di\\s+pi[uù]|continua\\s+a\\s+leggere)/giu) || []).length,"),
    ("M13_NODE_CONTEM_EM_VEZ_DE_COMECA", JS, "const LEIA_MAIS = /^(leggi", "const LEIA_MAIS = /(leggi"),
    ("M14_NODE_SEM_ROTULO", JS, "if ([texto, ...rotulos].some(", "if ([texto].some("),
    ("M15_ADMISSAO_V2_VIRA_V1", ADM, 'if ev.get("v1") and regra == rh.REGRA_V2:', "if False:"),
]


def copia(ref, destino):
    tar = subprocess.run(["git", "-C", RAIZ, "archive", "--format=tar", ref], capture_output=True, check=True).stdout
    with tarfile.open(fileobj=io.BytesIO(tar)) as t:
        t.extractall(destino)


def correr(pasta):
    env = dict(os.environ, PYTHONUTF8="1", PYTHONDONTWRITEBYTECODE="1", NODE_DISABLE_COMPILE_CACHE="1",
               HTTPS_PROXY="http://127.0.0.1:9", HTTP_PROXY="http://127.0.0.1:9")
    r = subprocess.run([sys.executable, "tests/test_c2_juiz.py"], cwd=pasta, env=env, capture_output=True,
                       text=True, encoding="utf-8", errors="replace", timeout=600)
    m = re.search(r"Ran (\d+) test", r.stderr)
    return r.returncode, int(m.group(1)) if m else None, r.stderr[-600:]


def main():
    ref = next((a.split("=", 1)[1] for a in sys.argv[1:] if a.startswith("--ref=")), "HEAD")
    base = tempfile.mkdtemp(prefix="c2-juiz-mutacao-")
    out = {"REF": subprocess.run(["git", "-C", RAIZ, "rev-parse", "--short", ref], capture_output=True,
                                 text=True).stdout.strip(), "MUTANTES": []}
    try:
        limpa = os.path.join(base, "limpa")
        copia(ref, limpa)
        cod, n, cauda = correr(limpa)
        out["SEM_MUTANTE"] = {"CODIGO": cod, "TESTES": n}
        if cod != 0:
            raise SystemExit("a copia limpa nao passa — o ataque nao tem base:\n" + cauda)
        for nome, alvo, de, para in MUTANTES:
            pasta = os.path.join(base, nome)
            shutil.copytree(limpa, pasta)
            f = os.path.join(pasta, alvo)
            with open(f, encoding="utf-8", newline="") as h:
                s = h.read()
            s2 = s.replace("\r\n", "\n")
            if s2.count(de) != 1:
                raise SystemExit("MUTANTE_SEM_ALVO %s: o trecho aparece %d vezes em %s" % (nome, s2.count(de), alvo))
            s2 = s2.replace(de, para)
            with open(f, "w", encoding="utf-8", newline="") as h:
                h.write(s2.replace("\n", "\r\n") if "\r\n" in s else s2)
            cod, n, cauda = correr(pasta)
            morto = cod != 0
            out["MUTANTES"].append({"MUTANTE": nome, "ALVO": alvo, "MORTO": morto, "CODIGO": cod,
                                    "CAUDA": None if morto else cauda})
            print(nome, "MORTO" if morto else "SOBREVIVEU", flush=True)
            shutil.rmtree(pasta, ignore_errors=True)
    finally:
        shutil.rmtree(base, ignore_errors=True)
    out["MORTOS"] = sum(1 for m in out["MUTANTES"] if m["MORTO"])
    out["TOTAL"] = len(out["MUTANTES"])
    with open(os.path.join(RAIZ, "provas", "C2-JUIZ-MUTACAO.json"), "w", encoding="utf-8") as h:
        json.dump(out, h, ensure_ascii=False, indent=1)
    print("C2_JUIZ_MUTACAO · mortos=%d de %d" % (out["MORTOS"], out["TOTAL"]))
    return 0 if out["MORTOS"] == out["TOTAL"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
