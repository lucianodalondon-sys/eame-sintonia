# -*- coding: utf-8 -*-
"""A TRAVA MORDE? — a prova de que ela reprova quando tem de reprovar.

    UM TESTE QUE PASSA NÃO PROVOU NADA
    ENQUANTO NÃO SE MOSTRAR QUE ELE REPROVA.

Uma trava que passa sempre é indistinguível de uma trava desligada. Esta prova
viola a trava de propósito, das duas maneiras possíveis, e exige que ela
reprove nas duas. Depois desfaz a violação e confere que ficou tudo como estava.

    CENÁRIO 1  mexer num artefato que está congelado
    CENÁRIO 2  não mexer em nada e escrever inteligência NOVA ao lado

É reversível e não sai desta máquina: escreve em ficheiros do repositório,
desfaz no fim, e confere byte a byte que desfez. Zero rede, zero produção,
zero Git — nem `add`, nem `commit`.
"""
import json
import os
import subprocess
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CENSO = os.path.join(RAIZ, "system-map", "scripts", "censo_do_congelamento.py")
GERADO = os.path.join(RAIZ, "system-map", "data", "congelamento.generated.json")
CONTRATO = os.path.join(RAIZ, "docs", "operacao", "TRAVA-DA-INTELIGENCIA.json")

# O intruso: um ficheiro que qualquer pessoa bem-intencionada escreveria.
INTRUSO = os.path.join(RAIZ, "motor", "v21_scoring_provisorio.py")
CORPO_DO_INTRUSO = (
    "# -*- coding: utf-8 -*-\n"
    '"""Ficheiro de MENTIRA, escrito por provas/trava_da_inteligencia_morde.py\n'
    "para verificar se a trava o apanha. Se este ficheiro sobreviver a uma\n"
    'corrida desta prova, a prova falhou em limpar — apague-o."""\n'
    "OPPORTUNITY_SCORE = 0.0\n"
    "PROMOTED_TO_RADAR = False\n")


def _correr(*args):
    return subprocess.run(list(args), cwd=RAIZ, capture_output=True, text=True)


def _sha(rel):
    return _correr("git", "hash-object", "--", rel).stdout.strip()


def _teste(nome):
    """Devolve True se PASSOU."""
    r = _correr(sys.executable, "-m", "unittest",
                "tests.test_trava_da_inteligencia.%s" % nome)
    return r.returncode == 0, r.stderr


def _censo():
    _correr(sys.executable, CENSO)


def cenario_1_mexer_no_que_esta_congelado():
    """Pega no primeiro artefato congelado e acrescenta-lhe uma linha."""
    with open(CONTRATO, encoding="utf-8") as f:
        alvo = json.load(f)["FREEZE_MANIFEST"]["FROZEN_INTELLIGENCE_ARTIFACTS"][0]
    caminho = os.path.join(RAIZ, alvo["PATH"])

    with open(caminho, "rb") as f:
        original = f.read()
    sha_antes = _sha(alvo["PATH"])
    if sha_antes != alvo["GIT_BLOB_SHA"]:
        print("  ABORTA: o alvo ja estava diferente do manifesto antes de eu "
              "lhe tocar. Nao se prova nada mexendo no que ja mudou.")
        return False

    try:
        with open(caminho, "wb") as f:
            f.write(original + b"\n# linha posta pela prova da trava\n")
        passou, _e = _teste(
            "AInteligenciaCongeladaNaoAvancou.test_nenhum_artefato_congelado_mudou")
        print("  alvo: %s" % alvo["PATH"])
        print("  trava com o ficheiro mexido: %s"
              % ("PASSOU  <-- MAU, nao mordeu" if passou else "REPROVOU  <-- bom"))
        mordeu = not passou
    finally:
        with open(caminho, "wb") as f:
            f.write(original)

    voltou = _sha(alvo["PATH"]) == sha_antes
    print("  desfeito e conferido: %s" % ("SIM" if voltou else "NAO <-- GRAVE"))
    return mordeu and voltou


def cenario_2_escrever_inteligencia_nova_ao_lado():
    """A violação mais provável na vida real: ninguém mexe no que existe."""
    if os.path.exists(INTRUSO):
        print("  ABORTA: %s ja existe. Nao apago ficheiro que nao criei."
              % os.path.relpath(INTRUSO, RAIZ))
        return False
    try:
        with open(INTRUSO, "w", encoding="utf-8") as f:
            f.write(CORPO_DO_INTRUSO)
        _censo()
        passou, _e = _teste(
            "AInteligenciaCongeladaNaoAvancou.test_nao_apareceu_inteligencia_nova")
        print("  intruso: %s" % os.path.relpath(INTRUSO, RAIZ))
        print("  trava com inteligencia nova: %s"
              % ("PASSOU  <-- MAU, nao mordeu" if passou else "REPROVOU  <-- bom"))
        mordeu = not passou
    finally:
        if os.path.exists(INTRUSO):
            os.remove(INTRUSO)
        _censo()

    with open(GERADO, encoding="utf-8") as f:
        gerado = json.load(f)
    with open(CONTRATO, encoding="utf-8") as f:
        manifesto = json.load(f)["FREEZE_MANIFEST"]
    limpo = (sorted(a["PATH"] for a in gerado["FROZEN_INTELLIGENCE_ARTIFACTS"])
             == sorted(a["PATH"] for a in
                       manifesto["FROZEN_INTELLIGENCE_ARTIFACTS"]))
    print("  desfeito e conferido: %s" % ("SIM" if limpo else "NAO <-- GRAVE"))
    return mordeu and limpo


def main():
    print("PROVA — A TRAVA DA INTELIGENCIA MORDE?")
    print("")
    print("CENARIO 1 — mexer num artefato congelado")
    um = cenario_1_mexer_no_que_esta_congelado()
    print("")
    print("CENARIO 2 — escrever inteligencia nova ao lado")
    dois = cenario_2_escrever_inteligencia_nova_ao_lado()
    print("")

    passou_no_fim, _e = _teste("AInteligenciaCongeladaNaoAvancou")
    print("com tudo desfeito, a trava volta a passar: %s"
          % ("SIM" if passou_no_fim else "NAO <-- ficou sujeira"))
    print("")

    bom = um and dois and passou_no_fim
    print("TRAVA_MORDE=%s" % ("PASS" if bom else "FAIL"))
    print("  o que isto prova: a trava reprova nas DUAS maneiras de a violar,")
    print("  e nao reprova quando nao ha violacao. Uma trava que passasse")
    print("  sempre seria indistinguivel de uma trava desligada.")
    return 0 if bom else 1


if __name__ == "__main__":
    sys.exit(main())
