"""Mutacao da DA-21 (INTEGRA-NOITE lote 4): cada mutante desfaz uma parte dos consertos; o teste que a DA-21
nomeia tem de ficar VERMELHO; o ficheiro volta ao original (sha256 conferido)."""
import hashlib
import os
import subprocess
import sys
from pathlib import Path

R = Path(__file__).resolve().parents[2] if Path(__file__).resolve().parents[1].name == "provas" else \
    Path("C:/Users/London1/orca/workspaces/eame-sintonia/janela-formas-v1")
ASI = R / "curadoria" / "atribuir_source_id.py"
RES = R / "coleta" / "reserva_24h.py"
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
]


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


env = dict(os.environ, PYTHONUTF8="1", HTTPS_PROXY="http://127.0.0.1:9", HTTP_PROXY="http://127.0.0.1:9",
           PYTHONDONTWRITEBYTECODE="1")
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
        r = subprocess.run([sys.executable, "-B", "-m", "unittest", *testes], cwd=R, env=env,
                           capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=900)
    finally:
        alvo.write_bytes(original)
    assert sha(alvo) == antes, "NAO REPOSTO: " + nome
    ult = [l for l in r.stderr.splitlines() if l.startswith(("FAILED", "OK"))]
    morto = r.returncode != 0
    mortos += morto
    print(("MORTO " if morto else "VIVO  ") + nome + " | " + (ult[-1] if ult else "?") + " | reposto sha256 " + antes[:12])
print("MUTANTES %d, MORTOS %d" % (len(MUTANTES), mortos))
sys.exit(0 if mortos == len(MUTANTES) else 1)
