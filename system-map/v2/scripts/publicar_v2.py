#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PUBLICA O V2 NUMA ROTA PRÓPRIA — sem tocar no mapa oficial.

    python3 system-map/v2/scripts/publicar_v2.py

    escreve: italia-portale/client/system-map-v2/{index.html,map.js,map.css,estado.gerado.json}

UMA ROTA, E SÓ UMA
------------------
`/system-map/` continua a ser o mapa oficial e NÃO é tocado. O V2 sai em
`/system-map-v2/`, que é uma rota nova e vazia até agora. Duas rotas a competir
pelo mesmo endereço é a forma mais barata de servir a versão errada sem ninguém
perceber — por isso são duas rotas DISTINTAS, e a nova diz na cara que é
candidata.

POR QUE O ESTADO VIAJA AO LADO DA APP
--------------------------------------
A app lê `estado.gerado.json` do seu próprio directório. Assim o que se testa no
browser é exactamente o que se publica: mesma pasta, mesmos ficheiros, mesmo
caminho relativo. Um teste feito noutra árvore que não a publicada prova a outra
árvore.
"""

from __future__ import annotations

import shutil
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[3]
APP = RAIZ / "system-map" / "v2" / "app"
ESTADO = RAIZ / "system-map" / "v2" / "data" / "estado.gerado.json"
DESTINO = RAIZ / "italia-portale" / "client" / "system-map-v2"
OFICIAL = RAIZ / "italia-portale" / "client" / "system-map"


def main() -> int:
    if not ESTADO.is_file():
        print("falta o estado gerado — corra gerar_mapa.py", file=sys.stderr)
        return 2
    antes = sorted(p.name for p in OFICIAL.iterdir()) if OFICIAL.is_dir() else []

    DESTINO.mkdir(parents=True, exist_ok=True)
    # Os ficheiros são NOMEADOS, não varridos: varrer copiava em silêncio o que
    # lá estivesse — um rascunho, uma sobra — e faltava em silêncio o que não
    # estivesse. Nomear falha alto quando falta.
    for nome in ("index.html", "map.js", "map.css"):
        origem = APP / nome
        if not origem.is_file():
            print(f"FALTA {origem.relative_to(RAIZ)} — a app está incompleta", file=sys.stderr)
            return 2
        shutil.copyfile(origem, DESTINO / nome)
    shutil.copyfile(ESTADO, DESTINO / "estado.gerado.json")

    depois = sorted(p.name for p in OFICIAL.iterdir()) if OFICIAL.is_dir() else []
    if antes != depois:
        print("ABORTAR: o mapa oficial mudou durante a publicação", file=sys.stderr)
        return 3

    print(f"publicado em {DESTINO.relative_to(RAIZ)}/ · "
          f"{len(list(DESTINO.iterdir()))} ficheiros")
    print(f"o mapa oficial em {OFICIAL.relative_to(RAIZ)}/ NAO foi tocado "
          f"({len(depois)} ficheiros, iguais)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
