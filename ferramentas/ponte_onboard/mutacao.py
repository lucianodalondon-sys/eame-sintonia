# -*- coding: utf-8 -*-
"""PONTE-ONBOARD · mutacao: cada guarda nova, desligada, tem de fazer cair um teste.

Cada mutante troca UMA linha, corre os dois ficheiros de teste e repoe o
ficheiro original (pelo conteudo guardado em memoria, nunca por git). Sem
bytecode (PYTHONDONTWRITEBYTECODE): um mutante do mesmo tamanho enganava o .pyc.

Uso: py ferramentas/ponte_onboard/mutacao.py [--saida X.json]
"""
import json
import os
import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
TESTES = ["tests.test_onboardar_rotas_provadas", "tests.test_canario_rotas_contrato_certo"]
CAN, ONB, SUP, SHA = ("medidas/canario_rotas_elegiveis.py", "curadoria/onboardar_rotas_provadas.py",
                      "curadoria/supervisor.py", "curadoria/sha_do_contrato.py")
MUTANTES = [
    ("M1 canario volta a ler o Git HEAD por omissao", CAN,
     "        ref = ref or DISCO", '        ref = ref or "HEAD"'),
    ("M2 canario nao escreve a impressao do contrato", CAN,
     '        l["CONTRATO_SHA256"] = SHA.do_contrato(c)', '        l["CONTRATO_SHA256"] = None'),
    ("M3 --juntar volta a apagar a ronda anterior", CAN,
     '    if "--juntar" in argv and SAIDA.exists():', '    if False:'),
    ("M4 onboarding deixa de comparar a impressao", ONB,
     '        elif p["CONTRATO_SHA256"] != SHA.do_contrato(c):', '        elif False:'),
    ("M5 onboarding aceita prova de qualquer idade", ONB,
     "              or agora - _quando(p.get(\"PROVADO_EM\") or canario.get(\"GERADO_EM\")) > PROVA_MAX_IDADE):",
     "              or agora - _quando(p.get(\"PROVADO_EM\") or canario.get(\"GERADO_EM\")) > PROVA_MAX_IDADE * 1000):"),
    ("M6 prova sem impressao passa", ONB,
     '        elif not p.get("CONTRATO_SHA256"):', '        elif False:'),
    ("M7 gancho corre a cada volta (sem intervalo)", ONB,
     "    if sha == estado.get(\"ONBOARD_PROVA_SHA\") and ultima and agora - ultima < ONBOARD_INTERVALO:",
     "    if False:"),
    ("M8 o supervisor nao chama o gancho", SUP,
     "            _hook_onboarding()", "            pass"),
    ("M9 a impressao esquece a ACQUISITION", SHA,
     'CAMPOS = ("SOURCE_ID", "OUTPUT_TYPE", "ACQUISITION")', 'CAMPOS = ("SOURCE_ID", "OUTPUT_TYPE")'),
    ("M10 a impressao passa a ler o contrato inteiro", SHA,
     "    parte = {k: (contrato or {}).get(k) for k in CAMPOS}", "    parte = dict(contrato or {})"),
    ("M11 aplicar reescreve a tabela sem novas", ONB,
     "    if not novas:", "    if False:"),
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
            json.dumps({"DATASET": "PONTE-ONBOARD-MUTACAO", "MORTOS": mortos, "TOTAL": len(out),
                        "MUTANTES": out}, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    return 0 if mortos == len(out) else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
