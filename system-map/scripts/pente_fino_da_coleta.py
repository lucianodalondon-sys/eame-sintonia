#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PENTE FINO DA COLETA — toda peca tem de ter um porque que se sustente.

    py system-map/scripts/pente_fino_da_coleta.py

Uma peca no mapa nao se justifica por existir. Justifica-se por responder a
quatro perguntas, e este ficheiro pergunta-as uma a uma, a cada peca da coleta:

    1 · DE ONDE VEM?   alguem a chama, ou ela e uma porta de entrada declarada?
    2 · PARA ONDE VAI?  ela entrega alguma coisa a alguem, ou escreve um ficheiro?
    3 · PORQUE EXISTE?  o «por que esta aqui» diz mais do que repetir o nome?
    4 · ALGUEM CORRE?   um workflow, uma cadeia, um teste — ou esta desligada?

Uma peca que falha as QUATRO nao esta a trabalhar: esta a ocupar espaco no mapa
e atencao de quem o le.

    ISTO NAO APAGA NADA, E NAO DEVE.

«Ninguem chama» e «e lixo» sao coisas diferentes, e ja quase custaram caro nesta
casa: metade dos ficheiros sem chamador sao ferramentas de mao, feitas para uma
pessoa correr quando precisa. Uma ferramenta de mao com um porque escrito e
util; o que nao presta e a peca sem porque nenhum.

Este ficheiro poe a lista na mesa, ordenada pela que tem menos resposta. Quem
decide o que sai e gente.
"""

import json
import re
import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
ESTADO = RAIZ / "system-map" / "data" / "state.generated.json"
SAIDA = RAIZ / "system-map" / "data" / "pente-fino.generated.json"

# As zonas do departamento de coleta, mais a sala de espera que o fecha.
ZONAS = ("Z-PEDIDO", "Z-CANDIDATAS", "Z-FONTES", "Z-FERRAMENTAS", "Z-ACOES",
         "Z-VEICULOS", "Z-REGRAS", "Z-ADMISSAO", "Z-GUARDA")

# Um «porque» que so repete o nome da peca nao explica nada. Estas sao as
# formulas vazias que aparecem quando alguem preenche o campo por obrigacao.
PORQUE_VAZIO = re.compile(
    r"^(existe|serve|e |é |para |usado|utilizado)\b.{0,40}$", re.I)


def workflows() -> str:
    d = RAIZ / ".github" / "workflows"
    if not d.is_dir():
        return ""
    return "".join(p.read_text(encoding="utf-8", errors="replace")
                   for p in sorted(d.glob("*.yml")))


def medir() -> dict:
    S = json.loads(ESTADO.read_text(encoding="utf-8"))
    wf = workflows()
    zn = {t["id"]: t["name"] for t in S["TERRITORIES"]}

    fichas = []
    for n in S["NODES"]:
        if n["territory"] not in ZONAS:
            continue

        vem = bool(n.get("inbound"))
        vai = bool(n.get("outbound")) or bool(n.get("produces"))
        # o veiculo nao escreve — quem escreve e a acao. Ele responde a pergunta
        # de outra maneira, e isso conta como resposta.
        if n.get("o_que_entra_vai_para"):
            vai = True

        porque = (n.get("why_here") or "").strip()
        tem_porque = len(porque) > 60 and not PORQUE_VAZIO.match(porque)

        corre = any(f in wf for f in n.get("files", []))
        # ou a cadeia canonica manda rodar, ou um teste toca-lhe
        if not corre:
            corre = "manda rodar" in (n.get("status_reason") or "").lower()

        respostas = sum((vem, vai, tem_porque, corre))
        fichas.append({
            "id": n["id"], "nome": n["name"], "zona": zn.get(n["territory"], "?"),
            "de_onde_vem": vem, "para_onde_vai": vai,
            "porque_existe": tem_porque, "alguem_corre": corre,
            "respostas": respostas,
            "ficheiros": len(n.get("files", [])),
            "estado": n["ui_status"],
        })

    fichas.sort(key=lambda x: (x["respostas"], x["nome"]))
    sem_nenhuma = [f for f in fichas if f["respostas"] == 0]
    so_uma = [f for f in fichas if f["respostas"] == 1]

    return {
        "SCHEMA": "sintonia.pente-fino-da-coleta/1",
        "PROVENANCE": {"HEAD": subprocess.run(
            ["git", "-C", str(RAIZ), "rev-parse", "HEAD"],
            capture_output=True, text=True).stdout.strip()},
        "PECAS": fichas,
        "RESUMO": {
            "pecas_da_coleta": len(fichas),
            "respondem_as_quatro": sum(1 for f in fichas if f["respostas"] == 4),
            "respondem_a_tres": sum(1 for f in fichas if f["respostas"] == 3),
            "respondem_a_duas": sum(1 for f in fichas if f["respostas"] == 2),
            "respondem_a_uma": len(so_uma),
            "nao_respondem_a_nenhuma": len(sem_nenhuma),
        },
    }


def main() -> int:
    d = medir()
    SAIDA.write_text(json.dumps(d, ensure_ascii=False, indent=2) + "\n",
                     encoding="utf-8")
    r = d["RESUMO"]
    print("PENTE FINO DA COLETA — toda peca responde por que existe?\n")
    for k, v in r.items():
        print(f"  {str(v).rjust(3)}  {k.replace('_', ' ')}")

    fracos = [f for f in d["PECAS"] if f["respostas"] <= 2]
    if fracos:
        print(f"\n  AS QUE MENOS SE EXPLICAM ({len(fracos)}):")
        print(f"    {'':4} {'vem':>3} {'vai':>3} {'pq':>3} {'corre':>5}  peca")
        for f in fracos:
            def m(b):
                return " ok" if b else "  ·"
            print(f"    {f['respostas']}/4 {m(f['de_onde_vem'])}{m(f['para_onde_vai'])}"
                  f"{m(f['porque_existe'])}{m(f['alguem_corre']):>6}  "
                  f"{f['nome'][:44]}  ({f['zona'][:22]})")
    print(f"\n  escrito em {SAIDA.relative_to(RAIZ).as_posix()}")
    print("\n  ISTO NAO APAGA NADA. «Ninguem chama» nao e o mesmo que «e lixo» —")
    print("  uma ferramenta de mao com um porque escrito e util. Quem decide e gente.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
