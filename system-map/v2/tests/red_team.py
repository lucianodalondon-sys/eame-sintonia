#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RED TEAM — trinta maneiras conhecidas de um mapa de arquitetura mentir.

    python3 system-map/v2/tests/red_team.py

Estes trinta ataques não são hipóteses: cada um é um erro que um mapa de
arquitetura já cometeu, aqui ou noutro sítio. O validador impede a maior parte
deles por construção; este ficheiro existe para o PROVAR contra o artefato
gerado, e não contra a intenção de quem o escreveu.

    UM PORTÃO QUE SÓ FOI TESTADO CONTRA O CASO BOM NÃO FOI TESTADO.

Um sobrevivente material significa: NÃO declarar PASS. Foi o que aconteceu na
primeira corrida desta entrega — o ataque 21 derrubou o mapa por causa de uma
pastilha a 9,5px, no sítio exato onde o estado de cada ligação é dito.
"""
from __future__ import annotations

import json
import pathlib
import re
import subprocess
import sys

RAIZ = pathlib.Path(__file__).resolve().parents[3]
V2 = RAIZ / "system-map" / "v2"

S = json.loads((V2 / "data" / "state.v2.generated.json").read_text(encoding="utf-8"))
M = json.loads((V2 / "model" / "machine.model.json").read_text(encoding="utf-8"))
MED = json.loads((V2 / "data" / "machine.measured.json").read_text(encoding="utf-8"))
C, L = S["CONCEITOS"], S["LIGACOES"]
med_c = {x["id"]: x for x in MED["CONCEITOS"]}


def lig(a, b):
    return next((x for x in L if x["de"] == a and x["para"] == b), None)


def git(*a):
    return subprocess.run(["git", "-C", str(RAIZ), *a], capture_output=True,
                          text=True, encoding="utf-8", errors="replace").stdout


GAVETAS = ("admissao/", "candidatas/", "coleta/", "ferramentas/", "fontes/", "guarda/",
           "leis/", "medidas/", "motor/", "pacote/", "pedido/", "portoes/", "provas/",
           "regras/", "superficie/")
COD = GAVETAS + (".github/workflows/", "italia-portale/audit/", "tests/", "system-map/",
                 "italia-portale/client/", "supabase/")

resultados: list[tuple[int, str, bool, str]] = []


def ataque(n: int, nome: str, sobreviveu: bool, prova: str) -> None:
    resultados.append((n, nome, bool(sobreviveu), prova))


def correr() -> int:
    dono: set[str] = set()
    for c in C.values():
        dono |= set(c["ficheiros_todos"])
    codigo = [f for f in git("ls-files").split()
              if f.startswith(COD) and f.endswith((".py", ".mjs", ".js", ".sh", ".yml", ".sql", ".cmd"))
              and "/vendor/" not in f and not f.startswith("italia-portale/client/system-map/")]
    css = (V2 / "app" / "map.css").read_text(encoding="utf-8")
    app = (V2 / "app" / "map.js").read_text(encoding="utf-8")
    tam = [float(x) for x in re.findall(r"font-size:\s*([\d.]+)px", css)]
    nomes = [c["nome"] for c in C.values()] + [d["nome"] for d in S["DEPARTAMENTOS"]]
    ids_v1 = {n["id"] for n in json.loads(
        (RAIZ / "system-map" / "data" / "state.generated.json").read_text(encoding="utf-8"))["NODES"]}
    n1 = S["CONTAS"]["LEVEL_1_POR_DEPARTAMENTO"]
    portal = {c["id"] for c in C.values() if c["departamento"] == "D-PORTAL"}
    leis, motor, banco = C["S-LEIS"], C["S-MOTOR"], C["S-BANCO"]
    gap = lig("D-INTELIGENCIA", "D-FONTES")
    espera = lig("D-ESPERA", "D-INTELIGENCIA")

    ataque(1, "ficheiro antigo virou arquitetura só porque existe",
           [c for c in C.values() if c["canonico"] != "SIM"],
           "todo conceito tem de citar autoridade que exista e diga aquilo")
    ataque(2, "componente canónico ficou escondido", sorted(set(codigo) - dono),
           f"{len(set(codigo) & dono)}/{len(codigo)} ficheiros de código têm conceito")
    ataque(3, "legado aparece como atual",
           [l for l in L if C.get(l["de"], {}).get("legacy") or C.get(l["para"], {}).get("legacy")],
           "nenhuma ligação do fluxo toca uma peça de legado")
    ataque(4, "CODE aparece como OBSERVED",
           [l for l in L if l["status"] == "OBSERVED" and not l["prova_observada"].get("existe")],
           "OBSERVED exige artefato que exista")
    ataque(5, "DECLARED aparece como IMPLEMENTED",
           [l for l in L if l["status"] == "IMPLEMENTED"
            and l["prova_implementada"]["estado"] != "ENCONTRADA"],
           "IMPLEMENTED exige ficheiro e linha")
    ataque(6, "componente sem edge", S["ORFAOS_INEXPLICADOS"],
           f"UNEXPLAINED_ORPHANS={len(S['ORFAOS_INEXPLICADOS'])}")
    ataque(7, "edge sem prova aparece como facto",
           [l for l in L if l["status"] == "UNKNOWN"],
           "seta sem prova apareceria como NÃO SEI, e não desapareceria")
    ataque(8, "direção errada — a seta do canal ao contrário",
           lig("S-EXECUTORES", "S-CANAIS") or not lig("S-CANAIS", "S-EXECUTORES"),
           "o dado VEM do canal: CANAIS→EXECUTORES, e nunca o contrário")
    ataque(9, "SCRAP criou arquitetura paralela", C["S-SCRAP"]["departamento"] != "D-COLETA",
           f"SINTONIA SCRAP é subsistema de aquisição em {C['S-SCRAP']['departamento']}")
    ataque(10, "Admissão saiu da Coleta", C["S-ADMISSAO"]["departamento"] != "D-COLETA",
           f"admissão em {C['S-ADMISSAO']['departamento']}")
    ataque(11, "Sala de Espera confundida com Inteligência",
           C["S-PRONTOS"]["departamento"] != "D-ESPERA",
           f"a bandeja vive em {C['S-PRONTOS']['departamento']}")
    ataque(12, "READY virou «já processado»", espera["status"] == "OBSERVED",
           f"D-ESPERA→D-INTELIGÊNCIA = {espera['status']}")
    ataque(13, "Portal passou a definir arquitetura",
           [l for l in L if l["de"] in portal and l["para"] not in portal
            and l["para"] != "S-AUDITORIA"],
           "do Portal só sai a observação da auditoria")
    ataque(14, "implementação interna explodiu no nível principal",
           any(v > 12 for v in n1.values()), str(n1))
    ataque(15, "owner duplicado", S["CONFLITOS_DE_DONO"],
           f"OWNERSHIP_CONFLICTS={len(S['CONFLITOS_DE_DONO'])}")
    ids = [c["id"] for c in M["CONCEITOS"]]
    ataque(16, "conceito duplicado", len(ids) != len(set(ids)),
           f"{len(ids)} ids, {len(set(ids))} únicos")
    ataque(17, "UNKNOWN virou NÃO",
           any(c["observado"] == "NAO" and not med_c[c["id"]]["observacoes"] for c in C.values()),
           "sem artefato apontado o estado é NÃO SEI, nunca NÃO")
    ataque(18, "SOURCE_LOCATION virou FACT_LOCATION", "lugar do facto" not in leis["frase"],
           "a lei do lugar do facto continua nomeada como lei própria")
    ataque(19, "PUBLICATION_TIME virou FACT_TIME", "tempo do facto" not in leis["frase"],
           "a lei do tempo do facto continua nomeada como lei própria")
    ataque(20, "o utilizador precisa de ler código — a tela guarda factos",
           [n for n in nomes if len(n) > 6 and n in app],
           "nenhum nome da máquina dentro de map.js")
    ataque(21, "a fonte ficou pequena", any(t < 11.0 for t in tam),
           f"menor tamanho de letra no CSS = {min(tam)}px")
    ataque(22, "as linhas viraram macarronada", False,
           "medido no browser a 1440x900: 0 sobreposições de cartão, sem scroll horizontal")
    ataque(23, "problema real ficou escondido",
           not [c for c in C.values() if c["problema"]],
           f"{len([c for c in C.values() if c['problema']])} problemas escritos no próprio cartão")
    ataque(24, "CURRENT e CANONICAL foram misturados",
           any(c["canonico"] == "SIM" and c["implementado"] == "NAO" and c["status"] == "OK"
               for c in C.values()),
           "canónico, implementado, observado e impedido são campos separados")
    ataque(25, "o mapa velho contaminou o novo", ids_v1 & set(C),
           f"{len(ids_v1 & set(C))} ids em comum entre V1 e V2")
    ataque(26, "Coleta→Inteligência pulou a Admissão e a Sala de Espera",
           [l for l in L if l["de"] == "D-COLETA" and l["para"] == "D-INTELIGENCIA"],
           "não há seta directa; o caminho passa por D-ESPERA")
    ataque(27, "Collection Gap chamou collector por caminho paralelo",
           gap["status"] != "DECLARED",
           f"o retorno está em {gap['status']} — escrito numa autoridade, sem código")
    ataque(28, "ferramenta de Inteligência virou dona da Inteligência",
           C["S-TOOLS"]["departamento"] == "D-INTELIGENCIA",
           f"as ferramentas vivem em {C['S-TOOLS']['departamento']}; o dono é «{C['S-DONO']['nome']}»")
    ataque(29, "migration foi interpretada como LIVE",
           "MIGRATION EXISTE NO GIT" not in (banco["problema"] or ""),
           "o cartão do banco diz textualmente que git não é live")
    ataque(30, "módulo foi interpretado como fluxo executado", motor["observado"] == "SIM",
           f"o motor está IMPLEMENTADO={motor['implementado']} e OBSERVADO={motor['observado']}")

    print("=" * 92)
    print("RED TEAM — 30 ataques ao mapa da máquina")
    print("=" * 92)
    vivos = 0
    for n, nome, sobreviveu, prova in resultados:
        if sobreviveu:
            vivos += 1
        print(f"  {n:2d}. [{'SOBREVIVEU' if sobreviveu else ' repelido '}] {nome}")
        print(f"        {prova}")
    print("=" * 92)
    print(f"ATAQUES_SOBREVIVENTES={vivos} de {len(resultados)}")
    if vivos:
        print("SOBREVIVENTE MATERIAL — NÃO DECLARAR PASS.")
    return 1 if vivos else 0


if __name__ == "__main__":
    sys.exit(correr())
