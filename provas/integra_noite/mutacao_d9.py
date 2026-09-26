"""Mutacao do D9: cada mutante faz a Intelligence usar JANELA_DECLARADA = NAO SEI como janela do facto.
O teste D9 tem de ficar VERMELHO em todos; o ficheiro volta ao original (sha256 conferido)."""
import hashlib
import os
import subprocess
import sys
from pathlib import Path

R = Path("C:/Users/London1/orca/workspaces/eame-sintonia/janela-formas-v1")
ESP = R / "provas" / "espinha_da_intelligence.py"
CI = R / "motor" / "corrida_da_inteligencia.py"

MUTANTES = [
    ("M1 G0 deixa passar quando a janela declarada e NAO SEI", ESP,
     "        if item.FACT_TIME == NAO_SEI:\n",
     "        if item.FACT_TIME == NAO_SEI and item.JANELA_DECLARADA != NAO_SEI:\n"),
    ("M2 G2 aceita NAO SEI como janela comum", ESP,
     "        if NAO_SEI in janelas or len(janelas) != 1:\n",
     "        if len(janelas) != 1:\n"),
    ("M3 o sinal leva a janela declarada NAO SEI como tempo", ESP,
     "            FACT_TIME=item.FACT_TIME, FACT_LOCATION=item.FACT_LOCATION,\n",
     "            FACT_TIME=(item.JANELA_DECLARADA if item.JANELA_DECLARADA == NAO_SEI else item.FACT_TIME), FACT_LOCATION=item.FACT_LOCATION,\n"),
    ("M4 a corrida grava a janela declarada no FACT_TIME do sinal", CI,
     '                    "FACT_TIME": item.get("FACT_TIME"),\n',
     '                    "FACT_TIME": item.get("JANELA_DECLARADA", item.get("FACT_TIME")),\n'),
]


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


env = dict(os.environ, PYTHONUTF8="1", HTTPS_PROXY="http://127.0.0.1:9", HTTP_PROXY="http://127.0.0.1:9",
           PYTHONDONTWRITEBYTECODE="1")
mortos = 0
for nome, alvo, velho, novo in MUTANTES:
    original = alvo.read_bytes()
    antes = sha(alvo)
    texto = original.decode("utf-8")
    if "\r\n" in texto:
        velho, novo = velho.replace("\n", "\r\n"), novo.replace("\n", "\r\n")
    assert texto.count(velho) == 1, nome
    try:
        alvo.write_bytes(texto.replace(velho, novo).encode("utf-8"))
        r = subprocess.run([sys.executable, "-B", "-m", "unittest",
                            "tests.test_os_consertos_da_intelligence.D9_JanelaDeclaradaNaoEJanelaDoFacto"],
                           cwd=R, env=env, capture_output=True, text=True, encoding="utf-8", errors="replace")
    finally:
        alvo.write_bytes(original)
    assert sha(alvo) == antes, "NAO REPOSTO: " + nome
    ult = [l for l in r.stderr.splitlines() if l.startswith(("FAILED", "OK"))]
    morto = r.returncode != 0
    mortos += morto
    print(("MORTO " if morto else "VIVO  ") + nome + " | " + (ult[-1] if ult else "?") + " | reposto sha256 " + antes[:12])
print("MUTANTES %d, MORTOS %d" % (len(MUTANTES), mortos))
sys.exit(0 if mortos == len(MUTANTES) else 1)
