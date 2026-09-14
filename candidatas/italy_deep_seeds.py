#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DE ONDE O GRAFO PARTE — as sementes da descoberta.

Duas origens, e a diferenca entre elas importa:

1 · O QUE A CASA JA CONHECE (240 hosts italianos medidos pelo baseline).
    Estes nao sao descoberta: sao o ponto de partida. Andar pelos links deles
    e o unico jeito honesto de achar o consorcio, a estacao experimental e o
    tecnico que nenhuma busca por palavra devolve.

2 · O QUE FALTA POR REGIAO (tabela escrita a mao, abaixo).
    A rodada anterior acertou nas regioes grandes. Se as sementes vierem so do
    que ja e conhecido, Molise e Valle d'Aosta continuam invisiveis — e a
    ausencia pareceria "nao existe" quando e "nunca fomos ver".

ATENCAO A UMA ARMADILHA: a REGIAO anotada aqui e a regiao de QUEM DESCOBRE, nao
a de quem e descoberto. Deduzir a regiao de uma fonte pelo nome do dominio e um
erro que esta missao procura de proposito (red team #19). A regiao do descobrido
so se afirma quando a propria pagina disser.
"""

import json
import sys
from pathlib import Path

TRABALHO = Path(sys.argv[1] if len(sys.argv) > 1
                else "C:/Users/London1/AppData/Local/Temp/sintonia-italy-deep")

# ── as tabelas escritas a mao vivem ao lado, em DADO ──────────────────────
# `italy_deep_seeds.json` guarda: as 20 regioes com 6 sementes cada (servico
# agricola · fitossanitario · agrometeo/ARPA · agencia regional ·
# universidade/centro · rede local), as nacionais e as universidades.
DADOS = Path(__file__).resolve().parent / "italy_deep_seeds.json"


def tabelas():
    """As tabelas de semente vivem em DADO, nao em codigo — e isto nao e gosto.

    Enquanto as ~260 URLs estavam dentro deste .py, o scanner do System Map
    lia-as como enderecos que o codigo chama: 24 dos 79 enderecos do mapa
    passaram a ser sementes de pesquisa, e empurraram para fora da vista
    enderecos que a maquina chama de verdade em producao — EPPO, EUR-Lex, o
    SDMX do ISTAT. O mapa deixou de contar a historia certa por causa de uma
    lista de pesquisa.

    Lista de pesquisa e dado. Codigo e o que anda por ela.
    """
    d = json.loads(DADOS.read_text(encoding="utf-8"))
    return d["REGIONAL"], d["NACIONAL"], d["UNIVERSIDADES"]


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    TRABALHO.mkdir(parents=True, exist_ok=True)

    REGIONAL, NACIONAL, UNIVERSIDADES = tabelas()
    sementes, vistos = [], set()

    def poe(url, nome, regiao, papel, familia):
        k = url.rstrip("/").lower()
        if k in vistos:
            return
        vistos.add(k)
        sementes.append({"url": url, "nome": nome, "regiao": regiao,
                         "papel": papel, "familia": familia})

    for reg, urls in REGIONAL.items():
        for i, u in enumerate(urls):
            poe(u, f"{reg} · semente {i + 1}", reg, "REGIONAL", "TABELA_REGIONAL")
    for u in NACIONAL:
        poe(u, "nacional", "ITALIA", "NATIONAL", "TABELA_NACIONAL")
    for u in UNIVERSIDADES:
        poe(u, "universidade", None, "SCIENCE", "TABELA_UNIVERSIDADE")

    # o que a casa ja conhece: a raiz de cada host italiano medido no baseline
    base = TRABALHO / "KNOWN-BASELINE.json"
    n_base = 0
    if base.exists():
        d = json.loads(base.read_text(encoding="utf-8"))
        for h in sorted(d["hosts"]):
            if not h.endswith(".it") and not h.endswith(".eu"):
                continue
            if any(x in h for x in ("linkedin", "facebook", "instagram", "youtube",
                                    "twitter", "tiktok", "linktr", "google")):
                continue
            poe(f"https://{h}/", f"conhecido: {h}", None, "KNOWN_HOST", "BASELINE")
            n_base += 1

    (TRABALHO / "SEEDS.json").write_text(
        json.dumps(sementes, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"SEEDS={len(sementes)}")
    print(f"  tabela regional = {sum(len(v) for v in REGIONAL.values())} "
          f"({len(REGIONAL)} regioes)")
    print(f"  tabela nacional = {len(NACIONAL)}")
    print(f"  universidades   = {len(UNIVERSIDADES)}")
    print(f"  hosts do baseline = {n_base}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
