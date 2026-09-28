"""Mutantes do D36 · a equivalência de fase só vale com as quatro provas.

Cada mutação tira UMA coisa ao dono do critério (`curadoria/regua_social.py`) e corre
o teste do D36. Se o teste continuar verde, a mutação sobreviveu — e a lei não está a
ser guardada por ninguém. Nenhuma mutação pode sobreviver.

Corre:  python provas/_mutantes_d36_equivalencia.py
"""
import io
import pathlib
import subprocess
import sys

RAIZ = pathlib.Path(__file__).resolve().parents[1]
ALVO = RAIZ / "curadoria" / "regua_social.py"
TESTE = RAIZ / "tests" / "test_d36_envelope_equivalente.py"

# ⚠️ AJUSTE DECLARADO (SOCIAL-ATE-A-SALA, 27/09): a regua deixou de ter a tabela de PARES
# de fases (`FASES_EQUIVALENTES`) e passou a julgar so as PROVAS (`provas_sociais`). As nove
# mutacoes sao as MESMAS nove perguntas de antes, apontadas ao texto novo — nenhuma saiu.
MUTACOES = [
    ("M1 · a conta do contrato YouTube deixa de ser lida",
     '    if aq.get("CHANNEL_ID"):\n        return "YOUTUBE", str(aq["CHANNEL_ID"])',
     '    if False:\n        return "YOUTUBE", str(aq["CHANNEL_ID"])'),
    ("M2 · tira a prova do CANAL DE ORIGEM",
     "    if not contas:\n        falta.append(",
     "    if False:\n        falta.append("),
    ("M3 · tira a prova da DATA DE PUBLICACAO",
     "    if pub is None:\n        falta.append(",
     "    if False:\n        falta.append("),
    ("M4 · tira a prova da AUTORIZACAO DO DONO",
     '    if _primeiro(ob, CAMPOS_DA_AUTORIZACAO) != "SIM":\n        falta.append(',
     "    if False:\n        falta.append("),
    ("M5 · tira a prova da LIGACAO CANAL-VIDEO-AUDIO (a midia)",
     "    if midia is None:",
     "    if False:"),
    ("M6 · excecao generica: qualquer fase satisfaz qualquer contrato",
     "        if falta:",
     "        if False:"),
    ("M7 · a ligacao deixa de conferir o canal contra o do contrato",
     "    elif contas and contas != {conta}:",
     "    elif False:"),
    ("M8 · a data deixa de exigir precisao declarada",
     "    elif _primeiro(ob, CAMPOS_DA_PRECISAO) is None:",
     "    elif False:"),
    ("M9 · o som guardado deixa de ter de nomear o video",
     '    elif pubid is not None and str(pubid) not in str(_valor(ob, midia[2]) or ""):',
     "    elif False:"),
]


def corre_os_testes() -> tuple[int, str]:
    p = subprocess.run([sys.executable, str(TESTE)], cwd=str(RAIZ),
                       capture_output=True, text=True, encoding="utf-8", errors="replace")
    return p.returncode, (p.stdout or "") + (p.stderr or "")


def main() -> int:
    original = io.open(ALVO, encoding="utf-8").read()
    base_rc, base_out = corre_os_testes()
    print("TESTE SEM MUTACAO: rc %d%s" % (base_rc, "  <-- o teste tem de passar primeiro!" if base_rc else ""))
    if base_rc != 0:
        print(base_out[-600:])
        return 2
    mortes, sobreviventes = 0, []
    try:
        for nome, de, para in MUTACOES:
            if de not in original:
                sobreviventes.append(nome + " (NAO APLICAVEL: o texto mudou)")
                print("  %-64s NAO APLICAVEL" % nome[:64])
                continue
            io.open(ALVO, "w", encoding="utf-8", newline="").write(original.replace(de, para, 1))
            rc, out = corre_os_testes()
            if rc != 0:
                mortes += 1
                print("  %-64s MORTA" % nome[:64])
            else:
                sobreviventes.append(nome)
                print("  %-64s SOBREVIVEU  <-- defeito" % nome[:64])
    finally:
        io.open(ALVO, "w", encoding="utf-8", newline="").write(original)
    print("\nMUTACOES %d · MORTAS %d · SOBREVIVENTES %d" % (len(MUTACOES), mortes, len(sobreviventes)))
    for s in sobreviventes:
        print("  SOBREVIVEU:", s)
    return 0 if not sobreviventes else 1


if __name__ == "__main__":
    sys.exit(main())
