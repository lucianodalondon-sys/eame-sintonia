"""A saida do motor das capacidades ATRAVESSA o gerador do pote v2 de verdade?

    python3 provas/int_r7/aceite_pelo_gerador.py <saida-do-motor.json> [<pote.json>]

O gerador (`pacote/pote_intelligence_casco.py`) e a ponte v1 que ele importa NAO
estao neste ramo: vivem em `claude/intelligence-bridge-v2-7mngha`, e outra
equipa esta a unifica-los. Copiar os dois para aqui seria uma segunda verdade do
contrato do pote. Por isso esta prova tira os DOIS ficheiros do objeto git do
commit fixado (ce775ff5), numa pasta temporaria, e corre `adaptar()` sobre a
saida do motor — o gerador de verdade, byte a byte, e nao uma imitacao.

Sem o commit no clone (ex.: clone raso), a resposta e NAO SEI, e diz-se:
codigo 4, e nenhuma aprovacao inventada.
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile

RAIZ = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
GERADOR_COMMIT = "ce775ff5ad2287d8f6fc19bee5feebd02843b8de"
FICHEIROS = ("pacote/pote_intelligence_casco.py", "pacote/ponte_intelligence_casco.py")

_FILHO = r"""
import json, sys
raiz, pasta, saida = sys.argv[1], sys.argv[2], sys.argv[3]
# a pasta temporaria primeiro (o gerador e a ponte de ce775ff5 e o _gavetas
# copiado para ela), depois as gavetas do repo de que a ponte depende (a
# espinha em provas/, a corrida em motor/, os meses em leis/).
sys.path[:0] = [pasta + "/pacote", pasta, raiz + "/motor", raiz + "/provas", raiz + "/leis"]
import pote_intelligence_casco as P
dado = json.load(open(saida, encoding="utf-8"))
pote = P.adaptar(dado)
print(json.dumps(pote, ensure_ascii=False))
"""


def blob_existe() -> bool:
    r = subprocess.run(["git", "cat-file", "-e", GERADOR_COMMIT + "^{commit}"],
                       cwd=RAIZ, capture_output=True)
    return r.returncode == 0


def correr_gerador(caminho_da_saida: str) -> dict:
    """-> o pote v2 que o gerador de ce775ff5 produz. Levanta se ele recusar."""
    if not blob_existe():
        raise FileNotFoundError("NAO SEI: o commit do gerador %s nao esta neste clone" % GERADOR_COMMIT)
    pasta = tempfile.mkdtemp(prefix="pote-ce775ff5-")
    try:
        os.makedirs(os.path.join(pasta, "pacote"))
        for f in FICHEIROS:
            corpo = subprocess.run(["git", "show", "%s:%s" % (GERADOR_COMMIT, f)], cwd=RAIZ,
                                   capture_output=True, check=True).stdout
            with open(os.path.join(pasta, f), "wb") as fh:
                fh.write(corpo)
        shutil.copy(os.path.join(RAIZ, "_gavetas.py"), pasta)
        r = subprocess.run([sys.executable, "-c", _FILHO, RAIZ, pasta, os.path.abspath(caminho_da_saida)],
                           capture_output=True, text=True, encoding="utf-8")
        if r.returncode != 0:
            raise RuntimeError("o gerador ce775ff5 recusou a saida: " + r.stderr.strip()[-2000:])
        return json.loads(r.stdout)
    finally:
        shutil.rmtree(pasta, ignore_errors=True)


def resumo(pote: dict) -> dict:
    return {"SCHEMA": pote["SCHEMA"], "INTELLIGENCE_RUN_ID": pote["INTELLIGENCE_RUN_ID"],
            "SOURCE_HEAD": pote["SOURCE_HEAD"], "CORTE": pote["CORTE"],
            "RUN_SCHEMA": pote["RUN_SCHEMA"],
            "OBJETOS": {c: [o["OBJETO_ID"] for o in e["OBJETOS"]] for c, e in pote["COMPARTIMENTOS"].items()
                        if e["OBJETOS"]},
            "VAZIOS": {c: e["PORQUE_VAZIO"] for c, e in pote["COMPARTIMENTOS"].items() if not e["OBJETOS"]},
            "RECUSADOS": pote["RECUSADOS"]}


if __name__ == "__main__":
    try:
        pote = correr_gerador(sys.argv[1])
    except FileNotFoundError as erro:
        print(str(erro))
        sys.exit(4)
    if len(sys.argv) > 2:
        with open(sys.argv[2], "w", encoding="utf-8") as fh:
            json.dump(pote, fh, ensure_ascii=False, indent=1)
    print(json.dumps(resumo(pote), ensure_ascii=False, indent=1))
