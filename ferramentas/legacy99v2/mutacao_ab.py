# -*- coding: utf-8 -*-
"""LEGACY-99 v2 · mutacao (A+B): cada guarda nova, desligada, tem de fazer cair um teste.

Cada mutante troca UMA linha, corre os dois ficheiros de teste e repoe o
ficheiro original (pelo conteudo guardado em memoria, nunca por git). Sem
bytecode (PYTHONDONTWRITEBYTECODE): um mutante do mesmo tamanho enganava o .pyc.

Uso: py ferramentas/legacy99v2/mutacao.py [--saida X.json]
"""
import json
import os
import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
TESTES = ["tests.test_importar_do_coletor", "tests.test_legacy_recheck", "tests.test_onboardar_rotas_provadas"]
IMP, CAN, W, EC = ("curadoria/importar_do_coletor.py", "curadoria/canario.py", "curadoria/worker.py",
                   "curadoria/escrever_contratos.py")
MUTANTES = [
    ("A1 a aquisicao nao e a da linha", IMP,
     "    novo[\"ACQUISITION\"] = copy.deepcopy(aq)", "    novo[\"ACQUISITION\"] = dict(aq, MAX_TARGETS=1)"),
    ("A2 sem a guarda da impressao igual a da linha", IMP,
     "    if SHA.do_contrato(novo) != SHA.do_contrato(linha):", "    if False:"),
    ("A3 a aquisicao historica passa a PROVADA", IMP,
     "        \"PROVADA\": False,", "        \"PROVADA\": True,"),
    ("A4 importa PDF (o canario nao o prova)", IMP,
     "    return (aq.get(\"STRATEGY\") == \"HTML_LINK_DISCOVERY\" and bool(aq.get(\"INDEX_URL\"))) or \\",
     "    return True or \\"),
    ("A5 reimporta quem ja tem contrato HTML", IMP,
     "        precisa = (not atual) or aq_atual.get(\"STRATEGY\") == \"YOUTUBE_CHANNEL_FEED\"", "        precisa = True"),
    ("A6 importa quem nao e READY_LEGACY", IMP,
     "        if CG.avaliar(sid, **ctx).get(\"MOTIVO\") != CG.READY_LEGACY:", "        if False:"),
    ("A7 importa sem mandar ao canario", IMP,
     "    feitas = remedir_fn(ids)", "    feitas = [{\"FEITO\": True} for _ in ids]"),
    ("A8 aceita fontes fora do plano", IMP,
     "    if fora:", "    if False:"),
    ("A9 SO_CASE deixa de ser dito", IMP,
     "            fica.append({\"SOURCE_ID\": sid, \"PORQUE\": \"SO_CASE: o coletor tem esta fonte so como `case` — \"",
     "            continue; fica.append({\"SOURCE_ID\": sid, \"PORQUE\": \"SO_CASE: o coletor tem esta fonte so como `case` — \""),
    ("B1 a rota do contrato ignora o canal", CAN,
     "    if aq.get(\"STRATEGY\") == \"CUSTOM_ADAPTER\" and aq.get(\"ADAPTER_ID\") == YOUTUBE_CANAL:", "    if False:"),
    ("B2 nao confere que a pagina e do canal", CAN,
     "    if cid.encode() not in b:", "    if False:"),
    ("B3 o worker nao usa o canario do canal", W,
     "        elif contrato.get(\"ACQUISITION\", {}).get(\"ADAPTER_ID\") == CANARIO.YOUTUBE_CANAL:", "        elif False:"),
    ("B4 o VALIDATE_ROUTE volta a perguntar pelo feed", W,
     "    url = CANARIO.url_da_rota(aq)   # LEGACY-99 B: o canal YouTube pela rota do coletor",
     "    url = aq.get(\"FEED_URL\") or aq.get(\"INDEX_URL\")"),
    ("B5 o molde novo volta a nascer no feed", EC,
     "            \"STRATEGY\": \"CUSTOM_ADAPTER\",", "            \"STRATEGY\": \"YOUTUBE_CHANNEL_FEED\","),
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
