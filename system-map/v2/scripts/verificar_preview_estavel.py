#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O ENDERECO FIXO ESTA A SERVIR O QUE ACABAMOS DE PUBLICAR?

    EPHEMERAL_DEPLOYMENT_URL  !=  STABLE_BRANCH_PREVIEW_URL
    READY DEPLOYMENT          !=  ALIAS ACTUALIZADO
    HTTP 200                  !=  VERSAO NOVA

`verificar_deploy.py` ja prova que um commit produziu deployment, e que o
DEPLOYMENT serve esse commit. Nao prova a coisa seguinte, que e a que interessa
a quem so tem um link: que o ALIAS FIXO da branch andou com ele. Sao dois
factos, e o segundo mede-se no endereco fixo DEPOIS de publicar — nunca se
infere do deployment ter ficado READY.

PORQUE NAO SE COMPARA O CARIMBO
-------------------------------
A tentacao e ler `PROVENANCE.HEAD` dentro de `estado.gerado.json` servido e
compara-lo com o HEAD desta arvore. Isso reprovaria SEMPRE, e por desenho: a
copia publicada nasce um commit atras de si mesma, porque o HEAD muda no proprio
commit que a grava. Esta escrito em `CANONICAL-PUBLICATION.json`, em
`O_QUE_O_PORTAO_DO_RELEASE_NAO_PODE_SER`.

    UM PORTAO QUE REPROVA SEMPRE NAO E RIGOR. E RUIDO, E DESLIGA-SE NUMA SEMANA.

O QUE SE COMPARA SAO OS BYTES
-----------------------------
Os ficheiros que o endereco fixo devolve tem de ser identicos, por SHA-256, aos
que estao COMMITADOS em `italia-portale/client/system-map-v2/` no HEAD desta
branch. Se o alias ficou parado num deployment antigo, os bytes diferem — e
diferem mesmo quando o HTTP e 200, que e exactamente o caso que este ficheiro
existe para apanhar.

SEM TOKEN NENHUM. So um GET publico e `git show`. Nenhum segredo novo entra no
repositorio, pela mesma razao ja declarada em `verificar_deploy.py`.

    O URL VEM DO CONTRATO, NAO DAQUI.

O endereco nao esta escrito neste ficheiro: le-se de
`system-map/CANONICAL-PUBLICATION.json`, que e o dono do conceito. Dois sitios
com o mesmo endereco sao dois enderecos no dia em que um deles mudar.

    python3 system-map/v2/scripts/verificar_preview_estavel.py
    python3 system-map/v2/scripts/verificar_preview_estavel.py --tentativas 20
"""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[3]
CONTRATO = RAIZ / "system-map" / "CANONICAL-PUBLICATION.json"
PUBLICADO = "italia-portale/client/system-map-v2"
FICHEIROS = ("index.html", "map.js", "map.css", "estado.gerado.json")


def git(*a: str) -> str:
    return subprocess.run(["git", "-C", str(RAIZ), *a], capture_output=True,
                          text=True, encoding="utf-8", errors="replace").stdout.strip()


def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def baixar(url: str, timeout: int = 30) -> bytes | None:
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "sintonia-system-map-v2"})
        with urllib.request.urlopen(req, timeout=timeout) as r:
            if r.status != 200:
                return None
            return r.read()
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, OSError):
        return None


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--tentativas", type=int, default=1,
                    help="quantas vezes tentar antes de reprovar (a Vercel demora)")
    ap.add_argument("--espera", type=int, default=20, help="segundos entre tentativas")
    args = ap.parse_args()

    if not CONTRATO.is_file():
        print("PREVIEW_STABLE_URL=FAIL · o contrato de publicacao nao existe", file=sys.stderr)
        return 1
    c = json.loads(CONTRATO.read_text(encoding="utf-8"))
    bloco = c.get("CANDIDATO_SYSTEM_MAP_V2") or {}
    url = bloco.get("SYSTEM_MAP_V2_PREVIEW_STABLE_URL")
    if not url:
        print("PREVIEW_STABLE_URL=FAIL · o contrato nao declara "
              "SYSTEM_MAP_V2_PREVIEW_STABLE_URL", file=sys.stderr)
        return 1
    base = url.rstrip("/")

    head = git("rev-parse", "HEAD")
    branch = git("rev-parse", "--abbrev-ref", "HEAD")
    esperada = bloco.get("CANDIDATE_BRANCH")
    print("ENDERECO_FIXO  ", url)
    print("BRANCH         ", branch, "" if branch == esperada else f"(contrato diz {esperada})")
    print("HEAD           ", head)

    # O que esta COMMITADO neste HEAD — nao o que esta no disco. O disco pode
    # ter alteracoes por publicar, e o alias so pode servir o que foi empurrado.
    esperado = {}
    for f in FICHEIROS:
        r = subprocess.run(["git", "-C", str(RAIZ), "show", f"{head}:{PUBLICADO}/{f}"],
                           capture_output=True)
        if r.returncode:
            print(f"PREVIEW_STABLE_URL=FAIL · {PUBLICADO}/{f} nao esta commitado em {head[:8]}",
                  file=sys.stderr)
            return 1
        esperado[f] = sha(r.stdout)

    for tentativa in range(1, args.tentativas + 1):
        servido, faltou = {}, []
        for f in FICHEIROS:
            alvo = base + "/" if f == "index.html" else f"{base}/{f}"
            b = baixar(alvo)
            if b is None:
                faltou.append(f)
            else:
                servido[f] = sha(b)

        if not faltou:
            maus = [f for f in FICHEIROS if servido[f] != esperado[f]]
            if not maus:
                print("HTTP           ", "200 nos quatro ficheiros")
                for f in FICHEIROS:
                    print(f"  IGUAL  {f}")
                print()
                print(f"PREVIEW_STABLE_URL=PASS · o endereco fixo serve o HEAD {head[:8]}")
                return 0
            if tentativa == args.tentativas:
                print("HTTP            200, mas os bytes nao sao os deste HEAD:")
                for f in maus:
                    print(f"  DIFERE {f}  servido={servido[f][:12]} commitado={esperado[f][:12]}")
                print()
                print("O alias ficou parado num deployment anterior. HTTP 200 nao e versao nova.",
                      file=sys.stderr)
                print(f"PREVIEW_STABLE_URL=FAIL · o endereco fixo NAO serve {head[:8]}",
                      file=sys.stderr)
                return 1
        elif tentativa == args.tentativas:
            print(f"PREVIEW_STABLE_URL=FAIL · nao respondeu 200: {', '.join(faltou)}",
                  file=sys.stderr)
            return 1

        print(f"  ainda nao ({tentativa}/{args.tentativas}) — espero {args.espera}s")
        time.sleep(args.espera)

    return 1


if __name__ == "__main__":
    raise SystemExit(main())
