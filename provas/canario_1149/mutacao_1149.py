"""CANARIO-1149 · o ataque: cada defeito plantado, um de cada vez, numa COPIA — e os testes tem de o apanhar.

    python3 provas/canario_1149/mutacao_1149.py [--ref=HEAD]

A copia sai de `git archive <ref>` (o repositorio nao e tocado). Cada mutante troca UM trecho exacto de um
ficheiro; um trecho que nao exista exactamente uma vez falha alto (NAO_APLICOU). MORTO = algum teste reprova.
Resultado em `provas/canario_1149/MUTACAO-1149.json`.
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

RAIZ = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
FT, H, EX, BC = "leis/fato_do_texto.py", "coleta/executor_texto_de_html.py", "coleta/italy_executor.py", \
    "leis/boletim_do_campo.py"
EC, T6, R1, RTL = "leis/estudo_chaves.py", "coleta/pesquisadores_t6.py", "admissao/reprocessar_um_item.py", \
    "admissao/reprocessar_tempo_lugar.py"
T = [sys.executable, "-m", "unittest", "tests.test_canario_1149"]

MUTANTES = [
    # C · o corpo da pagina achatada
    ("M01_ACHATADA_NAO_SE_PARTE", FT, "            fora.extend(_RE_FIM_DE_FRASE.split(linha))\n",
     "            fora.append(linha)\n"),
    # P · a publicacao no texto
    ("M02_DUAS_DATAS_NAO_SAO_AMBIGUAS", H, "    if len(achadas) > 1:\n        return", "    if False:\n        return"),
    ("M03_SECCAO_NO_PLURAL_CONTA", H, 'r"(?i:comunicato\\s+stampa|', 'r"(?i:comunicat[oi]\\s+stampa|'),
    ("M04_O_TEXTO_GANHA_AO_METADADO", H, '    if r.get("VALOR") not in (art.NAO_SEI, "", None):\n        return r\n',
     '    if r.get("VALOR") not in (art.NAO_SEI, "", None):\n        pass\n'),
    ("M05_O_EXECUTOR_NAO_PASSA_O_TEXTO", EX, "publicacao_da_pagina(dados_da_pagina, texto)",
     "publicacao_da_pagina(dados_da_pagina)"),
    ("M06_O_REPROCESSO_NAO_PASSA_O_TEXTO", RTL, 'dados, linha.get("TEXTO"))', "dados)"),
    # N · o agente de controlo
    ("M07_HOSPEDEIRO_NAO_SE_CONFERE", BC, "    if not (_RE_HOSPEDEIRO_ANIMAL.match(h) or _RE_PROBLEMA.match(h)):\n",
     "    if False:\n"),
    ("M08_AGENTE_CONTA_COMO_PROBLEMA", BC, '    lidas = [m for m in lidas if not m.get("AGENTE")]\n',
     "    lidas = list(lidas)\n"),
    ("M09_AGENTE_ATRAVESSA_PONTUACAO", BC, '    r"^(?:\\s+[a-z]+){0,2}?\\s+(?:', '    r"^\\W*(?:\\s*[a-z]+){0,3}?\\s+(?:'),
    ("M10_PAGINA_ACHATADA_E_TITULO", BC, "    if len(re.findall(r\"[A-Za-zÀ-ÿ']+\", linha)) >= _ft().LINHA_ACHATADA:\n",
     "    if False:\n"),
    # L · o lugar do estudo
    ("M11_AREA_DE_DESLIGADA", EC, " or _AREA_DE.search(antes) or coordenado", " or coordenado"),
    ("M12_SELEZIONATO_NAO_E_ESTUDO", EC, 'r"selezionat[oaie]|fenotipizzat', 'r"xselezionat[oaie]|fenotipizzat'),
    ("M13_SALENTO_VIRA_PUGLIA", T6, "            'Salento': ('salento',)}", "            'Puglia': ('salento',)}"),
    ("M14_LUGAR_SEM_VERBO_DE_ESTUDO", EC, "        if not pista:\n", "        if False:\n"),
    # R · a porta de um item
    ("M15_SEM_LIVRO_TUDO_SE_REVE", R1, 'SEM_LIVRO_NAO_SE_REVEEM = ("fact_time", "source_location")',
     "SEM_LIVRO_NAO_SE_REVEEM = ()"),
    ("M16_APLICAR_SEM_PARAR_FLAG", R1, "    if not os.path.exists(parar):\n", "    if False:\n"),
    ("M17_APLICAR_SEM_PROVA_VALE", R1, '    if not isinstance(backup, dict) or backup.get("PROVA_VALE") is not True:\n',
     "    if False:\n"),
    ("M18_APLICAR_SEM_CONFERIR_O_TEXTO", R1,
     '    if sha_do_texto(linha.get("TEXTO")) != revisoes.get("TEXTO_SHA256"):\n', "    if False:\n"),
    ("M19_MAIS_DE_UM_ITEM", R1, "    if len(achadas) != 1:\n", "    if not achadas:\n"),
]


def copia(ref, destino):
    tar = subprocess.run(["git", "-C", RAIZ, "archive", "--format=tar", ref], capture_output=True, check=True).stdout
    with tarfile.open(fileobj=io.BytesIO(tar)) as t:
        t.extractall(destino)


def correr(pasta):
    env = {k: v for k, v in os.environ.items() if not k.startswith("SINTONIA_")}
    env.update(PYTHONUTF8="1", PYTHONDONTWRITEBYTECODE="1", HTTPS_PROXY="http://127.0.0.1:9",
               HTTP_PROXY="http://127.0.0.1:9")
    r = subprocess.run(T, cwd=pasta, env=env, capture_output=True, text=True, encoding="utf-8", errors="replace",
                       timeout=900)
    saida = r.stdout + r.stderr
    return r.returncode, re.findall(r"^(?:FAIL|ERROR): (\w+)", saida, re.M)


def main():
    ref = next((a.split("=", 1)[1] for a in sys.argv[1:] if a.startswith("--ref=")), "HEAD")
    base = tempfile.mkdtemp(prefix="canario-1149-mutacao-")
    out = {"REF": subprocess.run(["git", "-C", RAIZ, "rev-parse", "--short", ref], capture_output=True,
                                 text=True).stdout.strip(), "TESTES": " ".join(T[1:]), "MUTANTES": []}
    try:
        limpa = os.path.join(base, "limpa")
        copia(ref, limpa)
        cod, falhas = correr(limpa)
        out["SEM_MUTANTE"] = {"CODIGO": cod, "FALHAS": falhas}
        if cod != 0:
            raise SystemExit("a copia limpa nao passa — o ataque nao tem base: %s" % falhas)

        def um(m):
            nome, alvo, de, para = m
            pasta = os.path.join(base, nome)
            shutil.copytree(limpa, pasta)
            f = os.path.join(pasta, alvo)
            with open(f, encoding="utf-8", newline="") as h:
                s = h.read().replace("\r\n", "\n")
            if s.count(de) != 1:
                shutil.rmtree(pasta, ignore_errors=True)
                return {"MUTANTE": nome, "ALVO": alvo, "ESTADO": "NAO_APLICOU", "OCORRENCIAS": s.count(de)}
            with open(f, "w", encoding="utf-8", newline="\n") as h:
                h.write(s.replace(de, para))
            cod, falhas = correr(pasta)
            shutil.rmtree(pasta, ignore_errors=True)
            return {"MUTANTE": nome, "ALVO": alvo, "ESTADO": "MORTO" if cod != 0 else "VIVO", "APANHADO_POR": falhas}
        with ThreadPoolExecutor(4) as ex:
            out["MUTANTES"] = list(ex.map(um, MUTANTES))
    finally:
        shutil.rmtree(base, ignore_errors=True)
    mortos = sum(1 for m in out["MUTANTES"] if m["ESTADO"] == "MORTO")
    out["RESUMO"] = "%d/%d mortos" % (mortos, len(MUTANTES))
    with open(os.path.join(RAIZ, "provas", "canario_1149", "MUTACAO-1149.json"), "w", encoding="utf-8",
              newline="\n") as h:
        json.dump(out, h, ensure_ascii=False, indent=1)
        h.write("\n")
    for m in out["MUTANTES"]:
        print(m["ESTADO"], m["MUTANTE"], m.get("APANHADO_POR", m.get("OCORRENCIAS")))
    print(out["RESUMO"])
    return 0 if mortos == len(MUTANTES) else 1


if __name__ == "__main__":
    sys.exit(main())
