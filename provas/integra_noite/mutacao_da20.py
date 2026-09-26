"""Mutacao da DA-20 (INTEGRA-NOITE lote 3): cada mutante desliga uma parte do conserto; os testes da DA-20
tem de ficar VERMELHOS em todos; o ficheiro volta ao original (sha256 conferido)."""
import hashlib
import os
import subprocess
import sys
from pathlib import Path

R = Path(__file__).resolve().parents[2]
AD = R / "admissao" / "admissao.py"
SE = R / "admissao" / "sala_de_espera.py"
T_PER = ["tests.test_periodo_e_chaves.DA20_SemProvaNaoHaPeriodo",
         "tests.test_quatro_chaves_na_sala.OContratoLevaAsQuatroChaves"]
T_036 = ["tests.test_sala_por_nome.SemA036OPousarContinuaAPousar"]
LINHA = '    if re.search(r"\\b(UNKNOWN|NOT_KNOWN|NAO SEI|NAO_SEI)\\b", _dobrar(base).upper()):\n'
# (1.a volta: a condicao tinha tambem `base == AUSENCIA or`; o mutante que a tirava SOBREVIVEU porque a falta de
#  base chega como «NAO SEI», que a busca ja apanha — era redundante e saiu do codigo.)
MUTANTES = [
    ("P1 o periodo volta a sair sem prova (a trava desligada)", AD, LINHA, "    if False:\n", T_PER),
    ("P2 so a falta de base conta; 'UNKNOWN' passa por prova", AD, LINHA, "    if base == AUSENCIA:\n", T_PER),
    ("P3 so 'UNKNOWN' conta; 'NAO SEI' (e a falta de base) passa", AD, LINHA,
     '    if re.search(r"\\b(UNKNOWN|NOT_KNOWN)\\b", _dobrar(base).upper()):\n', T_PER),
    ("P4 sem a 036 o pousar rebenta", SE,
     '            return "", [{"ESTADO": vdoc.NAO_SEI, "MOTIVO": "036 nao aplicada: sem caderno de versoes"}]\n',
     '            raise SalaIndisponivel("036 ausente")\n', T_036),
    ("P5 o pousar nao pergunta se a 036 existe", SE,
     "        if self._consultar(\"select to_regclass('public.sala_de_espera_versao') is not null\") != [\"t\"]:\n",
     "        if False:\n", T_036),
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
                           capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=600)
    finally:
        alvo.write_bytes(original)
    assert sha(alvo) == antes, "NAO REPOSTO: " + nome
    ult = [l for l in r.stderr.splitlines() if l.startswith(("FAILED", "OK"))]
    morto = r.returncode != 0
    mortos += morto
    print(("MORTO " if morto else "VIVO  ") + nome + " | " + (ult[-1] if ult else "?") + " | reposto sha256 " + antes[:12])
print("MUTANTES %d, MORTOS %d" % (len(MUTANTES), mortos))
sys.exit(0 if mortos == len(MUTANTES) else 1)
