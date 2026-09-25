# -*- coding: utf-8 -*-
"""LEGACY-99 v3 · mutacao da rota VIDEO (D53): cada guarda nova, desligada, tem de fazer cair um teste.

Cada mutante troca UMA linha, corre os dois ficheiros de teste e repoe o
ficheiro original (pelo conteudo guardado em memoria, nunca por git). Sem
bytecode (PYTHONDONTWRITEBYTECODE): um mutante do mesmo tamanho enganava o .pyc.

Uso: py ferramentas/legacy99v3/mutacao_video.py [--saida X.json]
"""
import json
import os
import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
TESTES = ["tests.test_rota_video", "tests.test_importar_do_coletor", "curadoria.test_pagina_boletim",
          "curadoria.test_canario_pdf"]
RS_, VC_, CAN, W, IMP, EC = ("curadoria/ready_split.py", "curadoria/validar_contratos.py", "curadoria/canario.py",
                            "curadoria/worker.py", "curadoria/importar_do_coletor.py", "curadoria/escrever_contratos.py")
MUTANTES = [
    ("V1 a forma VIDEO nao chega a regua irma", RS_,
     "    if (contrato or {}).get(\"FORMA\") == \"VIDEO\":", "    if False:"),
    ("V2 pagina do video sem HTTP 200", RS_,
     "        \"PAGINA_DO_VIDEO\": (item.get(\"FORMA\") == \"VIDEO\" and item.get(\"HTTP\") == 200",
     "        \"PAGINA_DO_VIDEO\": (True"),
    ("V3 sem prova de titulo", RS_,
     "        \"TITULO\": len(str(item.get(\"TITULO\") or \"\").strip()) >= 3,", "        \"TITULO\": True,"),
    ("V4 sem prova de data", RS_,
     "        \"DATA_DE_PUBLICACAO\": bool(_DATA.match(str(item.get(\"PUBLICATION_TIME\") or \"\"))),",
     "        \"DATA_DE_PUBLICACAO\": True,"),
    ("V5 sem prova de canal", RS_,
     "        \"CANAL\": bool(canal) and item.get(\"CANAL\") == canal,", "        \"CANAL\": True,"),
    ("V6 saida VIDEO deixa de ser exigida", RS_,
     "        \"SAIDA_VIDEO\": c.get(\"OUTPUT_TYPE\") == \"VIDEO\",", "        \"SAIDA_VIDEO\": True,"),
    ("V7 VIDEO/v1 nao e regua corrente", RS_,
     "REGUAS_CORRENTES = frozenset({REGUA_CURRENT, REGUA_PAGINA_BOLETIM, REGUA_VIDEO})",
     "REGUAS_CORRENTES = frozenset({REGUA_CURRENT, REGUA_PAGINA_BOLETIM})"),
    ("V8 FACT_TIME copia a data de publicacao", RS_,
     "            \"FACT_TIME\": \"UNKNOWN\",", "            \"FACT_TIME\": item.get(\"PUBLICATION_TIME\"),"),
    ("V9 transcricao inventada", RS_,
     "            \"TRANSCRICAO\": item.get(\"TRANSCRICAO\") or \"NAO_TRAZIDA (so quando o Scrap a trouxer)\"}",
     "            \"TRANSCRICAO\": item.get(\"TRANSCRICAO\") or item.get(\"TITULO\")}"),
    ("V10 o canario nao abre o video", CAN,
     "    st2, b2, err2 = buscar(url_do_video(vid))", "    st2, b2, err2 = 200, b, \"\""),
    ("V11 o validador aceita VIDEO sem saida VIDEO", VC_,
     "        if c.get(\"OUTPUT_TYPE\") != \"VIDEO\":", "        if False:"),
    ("V12 o worker nao usa o canario VIDEO", W,
     "        elif contrato.get(\"FORMA\") == CANARIO.FORMA_VIDEO:", "        elif False:"),
    ("V13 a importacao do canal nao declara a forma", IMP,
     "        novo[\"FORMA\"], novo[\"OUTPUT_TYPE\"] = \"VIDEO\", \"VIDEO\"", "        pass"),
    ("V14 o molde novo nao declara a forma", EC,
     "        \"FORMA\": \"VIDEO\",", "        \"FORMA_X\": \"VIDEO\","),
]


# ⚠️ MEDIDO a 25/09 (1.a corrida desta mutacao): o mutante C6 fez os testes antigos do
# supervisor chamar o `remedir` verdadeiro, que escreveu nos livros desta arvore
# (LIFECYCLE-LEDGER/QUEUE). Cada corrida passa a ser conferida: se um livro mudar, e
# reposto do retrato e o mutante fica marcado ESCREVEU_LIVRO.
LIVROS = ["curadoria/LIFECYCLE-LEDGER-V1.json", "curadoria/LIFECYCLE-QUEUE-V1.json",
          "curadoria/LIFECYCLE-EVIDENCE-V1.json", "curadoria/italy_contracts_curator.json",
          "regras/italy_contracts_onboarded.json"]
ESCREVEU = []


def _retrato():
    return {p: (RAIZ / p).read_bytes() for p in LIVROS if (RAIZ / p).exists()}


def correr() -> bool:
    antes = _retrato()
    try:
        return _correr()
    finally:
        for p, b in antes.items():
            if (RAIZ / p).read_bytes() != b:
                (RAIZ / p).write_bytes(b)
                ESCREVEU.append(p)


def _correr() -> bool:
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1", PYTHONIOENCODING="utf-8")
    r = subprocess.run([sys.executable, "-m", "unittest", *TESTES], cwd=RAIZ,
                       capture_output=True, text=True, env=env, timeout=600)
    return r.returncode == 0


def main(argv) -> int:
    assert correr(), "a base tem de estar verde antes de mutar"
    out = []
    for nome, rel, velho, novo in MUTANTES:
        f = RAIZ / rel
        original = f.read_bytes()
        texto = original.decode("utf-8")
        if texto.count(velho) != 1:
            out.append({"MUTANTE": nome, "RESULTADO": "ANCORA_NAO_CASA"})
            print(nome, "ANCORA_NAO_CASA")
            continue
        try:
            f.write_text(texto.replace(velho, novo), encoding="utf-8", newline="")
            verde = correr()
        finally:
            f.write_bytes(original)
        out.append({"MUTANTE": nome, "RESULTADO": "SOBREVIVEU" if verde else "MORTO",
                    "ESCREVEU_LIVRO": sorted(set(ESCREVEU))})
        ESCREVEU.clear()
        print(nome, out[-1]["RESULTADO"], flush=True)
    assert correr(), "a base tem de voltar verde depois de mutar"
    mortos = sum(o["RESULTADO"] == "MORTO" for o in out)
    print("MORTOS %d/%d · mutantes que escreveram num livro: %d" % (
        mortos, len(out), sum(1 for o in out if o.get("ESCREVEU_LIVRO"))))
    if "--saida" in argv:
        Path(argv[argv.index("--saida") + 1]).write_text(
            json.dumps({"DATASET": "LEGACY-99-V2-CD-MUTACAO", "MORTOS": mortos, "TOTAL": len(out),
                        "MUTANTES": out}, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    return 0 if mortos == len(out) else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
