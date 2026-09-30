#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MUTANTES DO KNOW HOW VIVO — desligar cada K, um de cada vez.

    py know-how/vivo/mutantes_knowhow.py [--saida resultado.json] [K1 K3 ...]

Para cada K1–K8: copia o `knowhow.py` para uma pasta temporaria, troca a funcao
daquele K por uma que devolve sempre PASS («desligada»), e corre a bateria desta
peca (`test_knowhow.py`) contra a copia, via `KNOWHOW_ALVO`. Antes dos oito, corre
a mesma bateria contra uma copia SEM mutacao: se o controlo nao passar, os
mutantes nao provam nada e o corredor para.

Um K sem nenhum teste morto e um K que a bateria nao guarda. Sai com rc=1.

O ficheiro original nunca e tocado. Sem .pyc (PYTHONDONTWRITEBYTECODE=1): um
mutante do mesmo tamanho e da mesma hora nao pode ser servido pela cache.
"""
import datetime
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

AQUI = os.path.dirname(os.path.abspath(__file__))
ORIGINAL = os.path.join(AQUI, "knowhow.py")
TESTES = os.path.join(AQUI, "test_knowhow.py")

MUTANTES = {
    "K1": "k1_origem", "K2": "k2_tipo", "K3": "k3_evidencia", "K4": "k4_durabilidade",
    "K5": "k5_nao_duplicado", "K6": "k6_nao_contraditorio", "K7": "k7_autoridade",
    "K8": "k8_aprendizado",
}
GANCHO = 'if __name__ == "__main__":'


def fabricar(pasta, k):
    with open(ORIGINAL, encoding="utf-8") as f:
        fonte = f.read()
    if fonte.count(GANCHO) != 1:
        raise SystemExit("o gancho do __main__ nao e unico; o mutante nao seria aplicado")
    if k:
        funcao = MUTANTES[k]
        if not re.search(rf"^def {funcao}\(", fonte, re.M):
            raise SystemExit(f"MUTANTE_NAO_APLICADO: {funcao} nao existe em knowhow.py")
        desligado = (f"def {funcao}(cand, ctx):  # MUTANTE {k}: desligado\n"
                     f"    return \"PASS\", \"MUTANTE {k} desligado\", {{}}\n\n\n")
        fonte = fonte.replace(GANCHO, desligado + GANCHO)
    destino = os.path.join(pasta, "knowhow.py")
    with open(destino, "w", encoding="utf-8", newline="\n") as f:
        f.write(fonte)
    return destino


def correr(alvo):
    env = dict(os.environ, KNOWHOW_ALVO=alvo, PYTHONDONTWRITEBYTECODE="1",
               PYTHONIOENCODING="utf-8", PYTHONUTF8="1")
    r = subprocess.run([sys.executable, TESTES], capture_output=True, text=True,
                       encoding="utf-8", errors="replace", env=env, timeout=3600)
    saida = r.stdout + r.stderr
    ran = re.search(r"Ran (\d+) tests?", saida)
    mortos = sorted(set(re.findall(r"^(?:FAIL|ERROR): (test_\w+)", saida, re.M)))
    return {"RC": r.returncode, "TESTES": int(ran.group(1)) if ran else 0,
            "MORTOS": mortos, "RESUMO": (re.findall(r"^(OK.*|FAILED.*)$", saida, re.M) or ["?"])[-1]}


def main():
    args = sys.argv[1:]
    saida = None
    if "--saida" in args:
        i = args.index("--saida")
        saida = args[i + 1]
        del args[i:i + 2]
    pedidos = args or list(MUTANTES)
    res = {"INICIO": datetime.datetime.now().astimezone().isoformat(timespec="seconds"),
           "ORIGINAL": ORIGINAL.replace("\\", "/"), "LINHAS": {}}
    pasta = tempfile.mkdtemp(prefix="khv-mut-")
    try:
        controlo = correr(fabricar(pasta, None))
        res["CONTROLO"] = controlo
        print(f"CONTROLO (sem mutacao): {controlo['RESUMO']} · {controlo['TESTES']} testes", flush=True)
        if controlo["RC"] != 0 or controlo["TESTES"] == 0:
            print("O CONTROLO NAO PASSA: os mutantes nao provariam nada. Parado.")
            return 2
        sobreviventes = []
        for k in pedidos:
            r = correr(fabricar(pasta, k))
            res["LINHAS"][k] = r
            vivo = not r["MORTOS"] or r["TESTES"] == 0
            if vivo:
                sobreviventes.append(k)
            print(f"{k} {MUTANTES[k]:22} {'SOBREVIVEU' if vivo else 'MORTO'} · "
                  f"{len(r['MORTOS'])}/{r['TESTES']} testes morrem: {', '.join(r['MORTOS'])}",
                  flush=True)
        res["SOBREVIVENTES"] = sobreviventes
        res["FIM"] = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
        print(f"MUTANTES: {len(pedidos) - len(sobreviventes)}/{len(pedidos)} mortos"
              + (f" · SOBREVIVENTES: {', '.join(sobreviventes)}" if sobreviventes else ""))
        return 1 if sobreviventes else 0
    finally:
        if saida:
            with open(saida, "w", encoding="utf-8", newline="\n") as f:
                json.dump(res, f, ensure_ascii=False, indent=1)
        shutil.rmtree(pasta, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main())
