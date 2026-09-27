"""Mutacao LOTE4-FINAL: os 4 consertos da DA-21, sobre o vivo 2ef6fef8 junto. Os 4 mutantes de mutacao_da21.py
(O1-O3 ORCID, D1 reserva_24h) + os que ali faltavam: D2/D3 (os outros dois modulos de runtime que importavam
provas/) e P1 (o `py` fixo da prova do contador — mata-se em Linux, onde `py` nao existe). Cada mutante desfaz uma
parte; o teste que a DA-21 nomeia tem de ficar VERMELHO; o ficheiro volta ao original (sha256 conferido).
uso: python3 provas/integra_noite/mutacao_lote4_final.py   (numa copia/worktree; nunca com o robo a correr)"""
import hashlib
import os
import subprocess
import sys
from pathlib import Path

R = Path(__file__).resolve().parents[2]
ASI = R / "curadoria" / "atribuir_source_id.py"
RES = R / "coleta" / "reserva_24h.py"
ROTA = R / "coleta" / "rota_navegador.py"
ESPERA = R / "coleta" / "espera_por_dominio.py"
MJS = R / "provas" / "contador_24h_local.mjs"
T_ORCID = ["tests.test_pesquisadores_t6", "tests.test_comunicacao_concorrenza"]
T_RUNTIME = ["tests.test_a_porta_cli_liga_o_banco.ORuntimeNaoImportaProvasEHaUmAdaptador"]
MUTANTES = [
    ("O1 a regra ORCID->T6 desligada", ASI,
     "    for rx, t in _IDENTIDADE_NO_ENDERECO:\n        m = rx.search(endereco)\n",
     "    for rx, t in []:\n        m = rx.search(endereco)\n", T_ORCID),
    ("O2 a regra ORCID le so nome + casa (o caminho some)", ASI,
     "        m = rx.search(endereco)\n", "        m = rx.search(_nome_e_casa(c))\n", T_ORCID),
    ("O3 todas as regras voltam a ler o endereco inteiro (o conserto do concorrenza desfeito)", ASI,
     '    return "%s %s" % (c.get("NOME", ""), casa)\n', '    return "%s %s" % (c.get("NOME", ""), url)\n',
     T_ORCID),
    ("D1 o runtime volta a importar provas/ (reserva_24h)", RES,
     "sys.path.insert(0, str(_AQUI))\nimport dominio_registavel as _PT",
     'sys.path.insert(0, str(_AQUI.parent / "provas"))\nimport prova_teto_dominio as _PT', T_RUNTIME),
    ("D2 o runtime volta a importar provas/ (rota_navegador)", ROTA,
     'as rodadas usam."""\n    sys.path.insert(0, os.path.join(RAIZ, "coleta"))\n    import dominio_registavel as DR',
     'as rodadas usam."""\n    sys.path.insert(0, os.path.join(RAIZ, "provas"))\n    import prova_teto_dominio as DR',
     T_RUNTIME),
    ("D3 o runtime volta a importar provas/ (espera_por_dominio)", ESPERA,
     '            sys.path.insert(0, os.path.join(raiz, "coleta"))\n        import dominio_registavel as DR ',
     '            sys.path.insert(0, os.path.join(raiz, "provas"))\n        import prova_teto_dominio as DR ',
     T_RUNTIME),
    ("P1 a prova do contador volta a chamar `py` fixo", MJS,
     'const PY = process.env.SINTONIA_PY || (process.platform === "win32" ? "py" : "python3");',
     'const PY = "py";', ["tests.test_contador_24h"]),
]


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


env = dict(os.environ, PYTHONUTF8="1", HTTPS_PROXY="http://127.0.0.1:9", HTTP_PROXY="http://127.0.0.1:9",
           PYTHONDONTWRITEBYTECODE="1")
env.pop("SINTONIA_PY", None)


def corre(testes):
    return subprocess.run([sys.executable, "-B", "-m", "unittest", *testes], cwd=R, env=env,
                          capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=900)


# a copia limpa tem de passar antes: um mutante so conta como morto se o limpo estava verde
for testes in (T_ORCID, T_RUNTIME, ["tests.test_contador_24h"]):
    r = corre(testes)
    ult = [l for l in r.stderr.splitlines() if l.startswith(("FAILED", "OK"))]
    print("LIMPO " + " ".join(testes) + " | " + (ult[-1] if ult else "?"))
    if r.returncode != 0:
        sys.exit("a copia limpa nao passa: " + " ".join(testes))
mortos = 0
for nome, alvo, velho, novo, testes in MUTANTES:
    original = alvo.read_bytes()
    antes = sha(alvo)
    texto = original.decode("utf-8")
    if "\r\n" in texto:
        velho, novo = velho.replace("\n", "\r\n"), novo.replace("\n", "\r\n")
    assert texto.count(velho) == 1, nome
    try:
        alvo.write_bytes(texto.replace(velho, novo).encode("utf-8"))
        r = corre(testes)
    finally:
        alvo.write_bytes(original)
    assert sha(alvo) == antes, "NAO REPOSTO: " + nome
    ult = [l for l in r.stderr.splitlines() if l.startswith(("FAILED", "OK"))]
    morto = r.returncode != 0
    mortos += morto
    print(("MORTO " if morto else "VIVO  ") + nome + " | " + (ult[-1] if ult else "?") + " | reposto sha256 " + antes[:12])
print("MUTANTES %d, MORTOS %d" % (len(MUTANTES), mortos))
sys.exit(0 if mortos == len(MUTANTES) else 1)
