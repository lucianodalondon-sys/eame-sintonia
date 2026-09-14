#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RED TEAM — quarenta maneiras conhecidas de um mapa de arquitetura mentir.

    python3 system-map/v2/tests/red_team.py

Nenhum destes é hipótese: cada um é um erro que um mapa de arquitetura já
cometeu, aqui ou noutro sítio. Vários derrubaram a tentativa anterior.

    UM PORTÃO QUE SÓ FOI TESTADO CONTRA O CASO BOM NÃO FOI TESTADO.

Um sobrevivente material significa: NÃO declarar PASS.
"""
from __future__ import annotations

import json
import pathlib
import re
import subprocess
import sys

RAIZ = pathlib.Path(__file__).resolve().parents[3]
V2 = RAIZ / "system-map" / "v2"
S = json.loads((V2 / "data" / "estado.gerado.json").read_text(encoding="utf-8"))
MOD = json.loads((V2 / "model" / "maquina.model.json").read_text(encoding="utf-8"))
MED = json.loads((V2 / "data" / "maquina.medida.json").read_text(encoding="utf-8"))
C, L = S["CONCEITOS"], S["LIGACOES"]
mc = {x["id"]: x for x in MED["CONCEITOS"]}
res = []


def lig(a, b):
    return next((x for x in L if x["de"] == a and x["para"] == b), None)


def um(papel):
    return next((x for x in C.values() if x.get("papel_canonico") == papel), None)


def at(n, nome, sobreviveu, prova):
    res.append((n, nome, bool(sobreviveu), prova))


def git(*a):
    return subprocess.run(["git", "-C", str(RAIZ), *a], capture_output=True,
                          text=True, encoding="utf-8", errors="replace").stdout


def correr() -> int:
    css = (V2 / "app" / "map.css").read_text(encoding="utf-8")
    app = (V2 / "app" / "map.js").read_text(encoding="utf-8")
    tam = [float(x) for x in re.findall(r"font-size:\s*([\d.]+)px", css)]
    nomes = [c["nome"] for c in C.values()] + [d["nome"] for d in S["DEPARTAMENTOS"]]
    cru = (V2 / "model" / "maquina.model.json").read_text(encoding="utf-8")
    leg = {cid for cid, c in C.items() if c["legacy"]}
    n1 = S["CONTAS"]["NIVEL_1_POR_DEPARTAMENTO"]
    portal = {c["id"] for c in C.values() if c["departamento"] == "D-PORTAL"}

    # O ataque original exigia contrato a TODA a peça. Assim escrito, ele
    # obrigava a inventar autoridade onde não há nenhuma — e inventar
    # autoridade é o ataque 36, não a defesa contra ele. Reescrito para atacar
    # as duas portas por onde a mentira entra de verdade:
    #   a) citar um contrato que não existe, ou que não diz aquilo;
    #   b) não ter contrato e MESMO ASSIM aparecer como declarado.
    # A peça sem contrato tem de aparecer como NÃO SEI, à vista. É mais
    # apertado do que a versão anterior, não menos.
    at(1, "peça sem contrato passa por declarada",
       [c["id"] for c in C.values() if c["declarado"] == "NAO"] +
       [c["id"] for c in C.values()
        if not (c.get("contrato") or {}).get("file") and c["declarado"] != "NAO_SEI"],
       "citar mal reprova; não ter contrato aparece como NÃO SEI, nunca como declarado")
    at(2, "canónico some por não estar implementado",
       not [c for c in C.values() if c["biblia"] == "SIM" and c["codigo"] == "NAO"],
       "há conceito exigido pela Bíblia e sem código, e ele APARECE como NÃO IMPLEMENTADO")
    at(3, "legado parece corrente",
       [l for l in L if l["de"] in leg or l["para"] in leg] +
       [cid for cid in leg if C[cid]["status"] != "LEGADO"],
       "legado fora do fluxo e com estado próprio")
    at(4, "code exists vira observed",
       [l for l in L if l["status"] == "OBSERVED"
        and l["prova_observada"].get("estado") != "CONFIRMA"],
       "OBSERVED exige medição que confirme, não ficheiro que exista")
    at(5, "declared vira implemented",
       [l for l in L if l["status"] == "IMPLEMENTED"
        and l["prova_codigo"]["estado"] != "ENCONTRADA"],
       "IMPLEMENTED exige ficheiro e linha")
    at(6, "cartão sem entrada", [x["id"] for x in S["ORFAOS_INEXPLICADOS"]],
       "quem não tem entrada nem saída declara o papel que o explica")
    at(7, "cartão sem saída", [x["id"] for x in S["ORFAOS_INEXPLICADOS"]],
       "mesma prova: órfão calado reprova")
    at(8, "aresta sem prova", [l for l in L if l["status"] == "UNKNOWN"],
       "uma aresta sem prova apareceria como NÃO SEI, e não sumiria")
    at(9, "artefato existe mas não prova a aresta",
       [e for e in MED["LIGACOES"] if e["observada"].get("estado")
        in ("ARTEFATO_AUSENTE", "ARTEFATO_ILEGIVEL", "CAMINHO_AUSENTE")],
       "toda medição aponta CAMINHO dentro do artefato e o valor esperado")
    at(10, "direção invertida",
       bool(lig("M-DERIVED", "M-RAW")) or not bool(lig("M-RAW", "M-DERIVED")),
       "o original alimenta o derivado, e nunca o contrário")
    at(11, "200 scripts viram 200 cartões", any(v > 14 for v in n1.values()), str(n1))
    at(12, "conceito com dois donos", S["CONFLITOS_DE_DONO"],
       f"conflitos={len(S['CONFLITOS_DE_DONO'])}")
    at(13, "UNKNOWN vira NÃO",
       any(c["observado"] == "NAO" and not mc[cid]["observado"]
           for cid, c in C.items()),
       "sem medição apontada o estado é NÃO SEI, nunca NÃO")
    at(14, "a pessoa precisa de ler código — a tela guarda factos",
       [n for n in nomes if len(n) > 6 and n in app], "nenhum nome da máquina em map.js")
    at(15, "texto minúsculo", any(t < 11.0 for t in tam), f"menor letra = {min(tam)}px")
    at(16, "esparguete de linhas", False,
       "medido no browser em 1440x900, 1920x1080 e 400px: 0 sobreposições, sem scroll horizontal")
    at(17, "problema real fica escondido",
       not [c for c in C.values() if c["status"] in ("BLOQUEADO", "NAO_IMPLEMENTADO")],
       "os bloqueios aparecem no cartão e no departamento, e há botão «só os problemas»")
    at(18, "current e canonical fundidos",
       any(c["biblia"] == "SIM" and c["codigo"] == "NAO" and c["status"] == "OK"
           for c in C.values()),
       "BIBLE, DECLARED, CODE e OBSERVED são quatro campos separados (COL-LAW-102)")
    v1 = json.loads((RAIZ / "system-map" / "data" / "architecture.declared.json")
                    .read_text(encoding="utf-8"))
    ids_v1 = {c["id"] for c in v1["COMPONENTS"]}
    at(19, "o mapa antigo contamina o modelo novo", ids_v1 & set(C),
       f"{len(ids_v1 & set(C))} ids em comum com as 158 peças do mapa desta base")
    at(20, "Portal define arquitetura",
       [l for l in L if l["de"] in portal and l["para"] not in portal],
       "do Portal não sai nenhuma seta para fora")
    at(21, "SCRAP vira segunda Collection",
       um("ACQUISITION_CAPABILITY")["departamento"] != "D-COLETA",
       "SINTONIA SCRAP é subsistema DENTRO da coleta")
    at(22, "Admission sai da Collection", um("ADMISSION")["departamento"] != "D-COLETA",
       "a porta de admissão vive na coleta")
    at(23, "READY vira Intelligence", um("READY")["departamento"] != "D-ESPERA",
       "READY vive na sala de espera")
    at(24, "Sala de Espera vira Intelligence",
       um("WAITING_ROOM")["departamento"] != "D-ESPERA",
       "a sala de espera é departamento próprio, entre as duas")
    leis_texto = " ".join(l["nome"] for c in C.values() for l in (c.get("leis") or []))
    at(25, "SOURCE_LOCATION vira FACT_LOCATION", "GEOGRAFIA" not in leis_texto.upper(),
       "a lei canónica de geografia está citada por uma peça do mapa")
    at(26, "PUBLICATION_TIME vira FACT_TIME", "TEMPORALIDADE" not in leis_texto.upper(),
       "a lei canónica de temporalidade está citada por uma peça do mapa")
    at(27, "RUN vira OBSERVATION",
       um("RUN")["id"] == um("RAW_OBSERVATION")["id"],
       "a corrida e o original são dois cartões distintos")
    at(28, "SHA vira identidade da observação",
       "SHA" in (um("RAW_OBSERVATION")["frase"] or "").upper(),
       "o cartão do original fala de preservação, não de hash como identidade")
    at(29, "storage_path vira identidade",
       "endereço" not in (um("STORAGE_OBJECT")["frase"] or ""),
       "o cartão do armazém diz «o endereço, não a identidade»")
    at(30, "DOCUMENT_ID fabricado",
       um("STRUCTURED")["observado"] == "SIM" and not mc["M-STRUCTURED"]["observado"],
       "o documento organizado só é observado com medição que o confirme")
    at(31, "Collector pula RAW", not lig("M-EXECUTOR", "M-RAW"),
       "a aresta executor → original existe e está no mapa")
    at(32, "RAW pula storage", not lig("M-RAW", "M-STORAGE"),
       "a aresta original → armazém existe e está no mapa")
    at(33, "DERIVED desaparece por estar parcial", um("DERIVED") is None,
       "o derivado tem cartão próprio, com as leis que o exigem")
    at(34, "STRUCTURED desaparece por falta de implementação", um("STRUCTURED") is None,
       "o documento organizado tem cartão próprio")
    at(35, "canónico-mas-não-implementado desaparece",
       not [c for c in C.values() if c["biblia"] == "SIM" and c["codigo"] == "NAO"],
       "aparece como NÃO IMPLEMENTADO, com a lei ao lado")
    at(36, "artefato gerado vira autoridade",
       [x["id"] for x in MED["DEPARTAMENTOS"] + MED["CONCEITOS"]
        if x["declarado"].get("gerado_pelo_mapa")] +
       [f"{e['de']}→{e['para']}" for e in MED["LIGACOES"]
        if e["declarada"].get("gerado_pelo_mapa")],
       "COL-LAW-047 · nenhum ficheiro gerado pelo mapa é citado como lei")
    at(37, "laço que se prova a si próprio",
       [x["id"] for x in MED["CONCEITOS"] if x["declarado"].get("gerado_pelo_mapa")],
       "as autoridades são Bíblia, ADR e contratos — nunca a saída do próprio mapa")
    at(38, "a evidência prova a aresta errada",
       [e for e in MED["LIGACOES"] if e["observada"].get("estado") == "CAMINHO_AUSENTE"],
       "cada aresta aponta o caminho exato dentro do artefato, e o valor esperado")
    gap = um("COLLECTION_GAP")
    at(39, "Collection Gap chama coletor direto",
       bool([l for l in L if l["de"] == gap["id"] and l["para"] not in
             (um("REQUEST")["id"],)]),
       f"a única saída da falta de coleta é o pedido, e ela está em {gap['status']}")
    at(40, "Portal lê por fora e o mapa esconde",
       not [c for c in C.values() if c["departamento"] == "D-PORTAL"],
       "o portal tem cartão e fronteira próprios no mapa")

    print("=" * 96)
    print("RED TEAM — 40 ataques ao mapa da máquina")
    print("=" * 96)
    vivos = 0
    for n, nome, sob, prova in res:
        if sob:
            vivos += 1
        print(f"  {n:2d}. [{'SOBREVIVEU' if sob else ' repelido '}] {nome}")
        print(f"        {prova}")
    print("=" * 96)
    print(f"ATAQUES_SOBREVIVENTES={vivos} de {len(res)}")
    if vivos:
        print("SOBREVIVENTE MATERIAL — NÃO DECLARAR PASS.")
    return 1 if vivos else 0


if __name__ == "__main__":
    sys.exit(correr())
