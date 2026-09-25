# -*- coding: utf-8 -*-
"""PROVA-ROTA-CICLO · mutacao: cada guarda nova, desligada, tem de fazer cair um teste.

Cada mutante troca UMA linha, corre os dois ficheiros de teste e repoe o
ficheiro original (pelo conteudo guardado em memoria, nunca por git). Sem
bytecode (PYTHONDONTWRITEBYTECODE): um mutante do mesmo tamanho enganava o .pyc.

Uso: py ferramentas/prova_rota_ciclo/mutacao.py [--saida X.json]
"""
import json
import os
import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
TESTES = ["tests.test_prova_rota_ciclo", "tests.test_onboardar_rotas_provadas", "tests.test_canario_rotas_contrato_certo"]
PRC, SUP = "curadoria/prova_rota_ciclo.py", "curadoria/supervisor.py"
MUTANTES = [
    ("P1 a rodada sai mesmo sem portao PASS", PRC,
     "    if not ok:", "    if False:"),
    ("P2 dominio repetido entra na mesma rodada", PRC,
     "        if not d or d in vistos:", "        if not d:"),
    ("P3 nao-elegiveis entram (le o curador inteiro)", PRC,
     "    for sid in G.elegiveis(ctx=ctx):", "    for sid in curator:"),
    ("P4 prova recente de OUTRO contrato conta como recente", PRC,
     "                   and l.get(\"CONTRATO_SHA256\") == SHA.do_contrato(c))", "                   )"),
    ("P5 prova velha conta como recente", PRC,
     "        recente = (quando is not None and agora - quando <= ONB.PROVA_MAX_IDADE",
     "        recente = (quando is not None and agora - quando <= ONB.PROVA_MAX_IDADE * 1000"),
    ("P6 sem intervalo entre rodadas", PRC,
     "    if fim and agora - fim < RONDA_INTERVALO:", "    if False:"),
    ("P7 rodada em curso nao impede outra", PRC,
     "            return {\"ACCAO\": \"RONDA_EM_CURSO\"}", "            pass"),
    ("P8 sem teto de fontes por rodada", PRC,
     "        if len(ronda) >= maximo:", "        if False:"),
    ("P9 o portao aceita qualquer veredito", PRC,
     "    return v == \"PASS\", \"EGRESS_GATE=%s\" % v", "    return True, \"EGRESS_GATE=%s\" % v"),
    ("P10 o loop vai a rede por omissao", SUP,
     "def _loop(pausa_worker: float, poll: float, prova_de_rota: bool = False) -> int:",
     "def _loop(pausa_worker: float, poll: float, prova_de_rota: bool = True) -> int:"),
    ("P11 o servico nao liga a prova de rota", SUP,
     "    return supervisionar(a.pausa, a.poll, prova_de_rota=not a.sem_prova_de_rota)",
     "    return supervisionar(a.pausa, a.poll)"),
    ("P12 o gancho da prova nao e chamado", SUP,
     "                _hook_prova_rota()", "                pass"),
    ("P13 rodada presa nunca e terminada", PRC,
     "            if desde and agora - desde > RONDA_TEMPO_MAXIMO:", "            if False:"),
]


def correr() -> bool:
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
        out.append({"MUTANTE": nome, "RESULTADO": "SOBREVIVEU" if verde else "MORTO"})
        print(nome, out[-1]["RESULTADO"], flush=True)
    assert correr(), "a base tem de voltar verde depois de mutar"
    mortos = sum(o["RESULTADO"] == "MORTO" for o in out)
    print("MORTOS %d/%d" % (mortos, len(out)))
    if "--saida" in argv:
        Path(argv[argv.index("--saida") + 1]).write_text(
            json.dumps({"DATASET": "PROVA-ROTA-CICLO-MUTACAO", "MORTOS": mortos, "TOTAL": len(out),
                        "MUTANTES": out}, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    return 0 if mortos == len(out) else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
