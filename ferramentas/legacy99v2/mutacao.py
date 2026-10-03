# -*- coding: utf-8 -*-
"""LEGACY-99 v2 (C+D) · mutacao: cada guarda nova, desligada, tem de fazer cair um teste.

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
TESTES = ["tests.test_legacy_recheck", "tests.test_legacy_colchetes", "tests.test_onboardar_rotas_provadas"]
CAN, GD, SUP = "curadoria/canario.py", "curadoria/gatilho_discovery.py", "curadoria/supervisor.py"
MUTANTES = [
    ("D1 o link malformado volta a passar", CAN,
     "            p = urlparse(h)", "            p = urlparse('http://ok/')"),
    ("C1 entram fontes que nao sao READY_LEGACY", GD,
     "        if CG.avaliar(sid, **ctx).get(\"MOTIVO\") != CG.READY_LEGACY:", "        if False:"),
    ("C2 entram contratos que o canario nao prova (YouTube feed)", GD,
     "        if aq.get(\"STRATEGY\") not in ESTRATEGIAS_QUE_O_CANARIO_PROVA or not aq.get(\"INDEX_URL\"):",
     "        if not aq.get(\"INDEX_URL\"):"),
    ("C3 duas do mesmo dominio no lote", GD,
     "        if c[\"DOMINIO\"] in vistos:", "        if False:"),
    ("C4 lote sem maximo", GD,
     "        if len(lote) >= maximo:", "        if False:"),
    ("C5 sem intervalo entre lotes", GD,
     "    if ultimo and (agora - ultimo).total_seconds() < LEGACY_INTERVALO_H * 3600:", "    if False:"),
    ("C6 o loop remede por omissao", SUP,
     "def _loop(pausa_worker: float, poll: float, revalidar_legacy: bool = False) -> int:",
     "def _loop(pausa_worker: float, poll: float, revalidar_legacy: bool = True) -> int:"),
    ("C7 o servico nao liga o re-check", SUP,
     "    return supervisionar(a.pausa, a.poll, revalidar_legacy=not a.sem_revalidar_legacy)",
     "    return supervisionar(a.pausa, a.poll)"),
    ("C8 o gancho nao e chamado", SUP,
     "                _hook_revalidar_legacy()", "                pass"),
    ("C9 a ordem deixa de ser a mais antiga primeiro", GD,
     "    return sorted(out, key=lambda x: (x[\"PROMOVIDA_EM\"], x[\"SOURCE_ID\"]))",
     "    return sorted(out, key=lambda x: x[\"SOURCE_ID\"])"),
    ("C10 remede mesmo sem candidatas", GD,
     "    if not lote:", "    if False:"),
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
