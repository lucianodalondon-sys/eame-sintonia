#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JUNTA O DECLARADO COM O MEDIDO — e calcula o estado. Nunca o recebe pronto.

    python3 system-map/v2/scripts/generate_map_v2.py

    le      : model/machine.model.json      (declarado por gente)
              data/machine.measured.json    (medido pelo scanner)
    escreve : data/state.v2.generated.json  (o que a tela le)

AS QUATRO DIMENSOES NAO SE FUNDEM NUM «OK»
-------------------------------------------
Cada conceito responde a quatro perguntas SEPARADAS, e juntar as respostas numa
so foi o defeito que este mapa nasceu para corrigir:

    CANONICO     alguma autoridade diz que isto faz parte da maquina?
    IMPLEMENTADO existe codigo no repositorio?
    OBSERVADO    ha artefato que prove que isto ja correu?
    IMPEDIDO     falta um ficheiro que a propria maquina exige para correr?

Uma peca pode ser CANONICA e nao implementada — e parte prevista e nao
construida. Pode ser implementada e nao observada — esta escrita e nunca correu.
Pode ter codigo e nao ser canonica — e candidata a legado. Um unico verde por
cima disso esconderia as tres coisas.

    CODIGO EXISTE NAO E FLUXO CORREU.

A pastilha grande do cartao diz a SAUDE, para quem olha de longe. As quatro
dimensoes continuam a vista, em separado, no mesmo cartao. A pastilha nunca
substitui as dimensoes: resume-as.

POR QUE «BLOQUEADO» NAO SE ESCREVE A MAO
-----------------------------------------
Ele nasce de uma medicao: a maquina exige um caminho, e o caminho nao esta la.
Um veredito escrito a mao envelhece calado — alguem conserta o defeito e o mapa
continua a dizer que esta partido, ou o contrario, que e pior.
"""

from __future__ import annotations

import json
import sys
from collections import defaultdict
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[3]
V2 = RAIZ / "system-map" / "v2"
MODELO = V2 / "model" / "machine.model.json"
MEDIDO = V2 / "data" / "machine.measured.json"
SAIDA = V2 / "data" / "state.v2.generated.json"

OK, ATENCAO, BLOQUEADO, NAO_IMPL, UNKNOWN, LEGADO = (
    "OK", "ATENCAO", "BLOQUEADO", "NAO IMPLEMENTADO", "UNKNOWN", "LEGADO")

# O CODIGO do estado e ASCII porque e ele que o validador e os testes comparam —
# um acento a mais num sitio e a comparacao passa a falhar por ortografia. O que
# a PESSOA le e outra coisa, e sai daqui: a tela nao escreve vocabulario nenhum,
# para nao haver duas listas de nomes a divergir.
ROTULOS = {
    OK: "OK", ATENCAO: "ATENCAO", BLOQUEADO: "BLOQUEADO",
    NAO_IMPL: "NAO IMPLEMENTADO", UNKNOWN: "NAO SEI", LEGADO: "LEGADO",
    "SIM": "SIM", "NAO": "NAO", "PARCIAL": "PARCIAL",
    "NAO SEI": "NAO SEI", "NAO SE APLICA": "NAO SE APLICA",
    "OBSERVED": "JA CORREU", "IMPLEMENTED": "HA CODIGO",
    "DECLARED": "SO ESCRITO", "UNKNOWN_EDGE": "NAO SEI",
}
ROTULOS.update({
    "OK": "OK", "ATENCAO": "ATEN\u00c7\u00c3O", "BLOQUEADO": "BLOQUEADO",
    "NAO IMPLEMENTADO": "N\u00c3O IMPLEMENTADO", "UNKNOWN": "N\u00c3O SEI",
    "LEGADO": "LEGADO", "SIM": "SIM", "NAO": "N\u00c3O", "PARCIAL": "PARCIAL",
    "NAO SEI": "N\u00c3O SEI", "NAO SE APLICA": "N\u00c3O SE APLICA",
    "OBSERVED": "J\u00c1 CORREU", "IMPLEMENTED": "H\u00c1 C\u00d3DIGO",
    "DECLARED": "S\u00d3 ESCRITO", "UNKNOWN_EDGE": "N\u00c3O SEI",
})


def estado_canonico(med: dict) -> tuple[str, str]:
    a = med["autoridade"]
    if a["estado"] == "CONFIRMADA":
        return "SIM", f"a autoridade {a['file']} diz isto, e a frase citada foi encontrada lá."
    if a["estado"] == "SEM_AUTORIDADE":
        return "NAO SEI", "nenhuma autoridade foi apontada para esta peça."
    if a["estado"] == "FICHEIRO_AUSENTE":
        return "NAO SEI", f"a autoridade apontada ({a['file']}) não existe no repositório."
    return "NAO SEI", f"a frase citada não foi encontrada em {a['file']}."


def estado_implementado(mod: dict, med: dict) -> tuple[str, str]:
    if mod.get("implementado_declarado") == "NAO":
        return "NAO", "está declarado, e o código não está nesta árvore."
    padroes = mod.get("implementa", [])
    achados, vazios = med["ficheiros"], med["padroes_vazios"]
    if not padroes:
        return "NAO SE APLICA", "não é feita de ficheiros: mede-se no código de quem a usa."
    if achados and vazios:
        return "PARCIAL", f"{len(achados)} ficheiro(s) encontrados; {len(vazios)} caminho(s) declarados não existem."
    if achados:
        return "SIM", f"{len(achados)} ficheiro(s) reais sustentam esta peça."
    return "NAO", "nenhum dos caminhos declarados existe no repositório."


def estado_observado(med: dict) -> tuple[str, str]:
    obs = med.get("observacoes", [])
    if not obs:
        return "NAO SEI", "nenhum artefato foi apontado como prova de que isto já correu."
    faltam = [o for o in obs if not o["existe"]]
    if not faltam:
        return "SIM", "; ".join(o["prova"] for o in obs)
    if len(faltam) == len(obs):
        return "NAO", "o artefato que provaria a execução não existe: " + \
                      ", ".join(o["path"] for o in faltam)
    return "PARCIAL", "parte dos artefatos existe; falta " + ", ".join(o["path"] for o in faltam)


def saude(mod, canonico, implementado, observado, impedido) -> tuple[str, str]:
    if mod.get("legacy"):
        return LEGADO, "ficou para trás; está fora do fluxo de hoje."
    if impedido:
        return BLOQUEADO, "falta um ficheiro que a própria máquina exige para correr."
    if implementado == "NAO":
        return NAO_IMPL, "parte prevista da máquina que ainda não existe em código aqui."
    if mod.get("problema") and observado in ("NAO", "PARCIAL"):
        return BLOQUEADO, "tem defeito conhecido, e não há prova de que tenha corrido."
    if mod.get("problema"):
        return ATENCAO, "funciona, e há um defeito conhecido escrito no cartão."
    if canonico != "SIM":
        return UNKNOWN, "nenhuma autoridade confirma esta peça."
    if implementado == "PARCIAL":
        return UNKNOWN, "parte dos caminhos declarados não existe."
    return OK, "canónica, implementada, e sem defeito conhecido."


def estado_ligacao(med: dict) -> tuple[str, str]:
    """NUNCA promove. Cada degrau exige a sua propria prova."""
    if med["observada"].get("existe"):
        return "OBSERVED", med["observada"].get("prova", "")
    if med["implementada"]["estado"] == "ENCONTRADA":
        i = med["implementada"]
        return "IMPLEMENTED", f"{i['file']}:{i['line']}"
    if med["declarada"]["estado"] == "CONFIRMADA":
        return "DECLARED", f"{med['declarada']['file']}"
    return "UNKNOWN", "nada prova esta ligação."


def main() -> int:
    if not (MODELO.is_file() and MEDIDO.is_file()):
        print("falta o modelo ou a medicao — corra o scanner primeiro", file=sys.stderr)
        return 2
    modelo = json.loads(MODELO.read_text(encoding="utf-8"))
    medido = json.loads(MEDIDO.read_text(encoding="utf-8"))
    med_c = {c["id"]: c for c in medido["CONCEITOS"]}
    med_d = {d["id"]: d for d in medido["DEPARTAMENTOS"]}

    filhos = defaultdict(list)
    for c in modelo["CONCEITOS"]:
        if c.get("parent"):
            filhos[c["parent"]].append(c["id"])

    # ── as ligacoes, primeiro: os cartoes precisam de saber quem entra e quem sai
    ligacoes, por_origem, por_destino = [], defaultdict(list), defaultdict(list)
    for e in modelo["LIGACOES"]:
        m = next(x for x in medido["LIGACOES"]
                 if x["de"] == e["de"] and x["para"] == e["para"])
        st, motivo = estado_ligacao(m)
        lig = {
            "de": e["de"], "para": e["para"], "nivel": e.get("nivel", 1),
            "retorno": bool(e.get("retorno")),
            "significado": e["significado"],
            "status": st, "motivo": motivo,
            "prova_declarada": m["declarada"],
            "prova_implementada": m["implementada"],
            "prova_observada": m["observada"],
        }
        ligacoes.append(lig)
        por_origem[e["de"]].append(lig)
        por_destino[e["para"]].append(lig)

    nomes = {d["id"]: d["nome"] for d in modelo["DEPARTAMENTOS"]}
    nomes.update({c["id"]: c["nome"] for c in modelo["CONCEITOS"]})

    # ── os conceitos ────────────────────────────────────────────────────────
    conceitos = {}
    for mod in modelo["CONCEITOS"]:
        m = med_c[mod["id"]]
        canonico, r_can = estado_canonico(m)
        impl, r_impl = estado_implementado(mod, m)
        obs, r_obs = estado_observado(m)
        imped = [i for i in m.get("impedimentos", []) if i["bloqueia"]]
        st, r_st = saude(mod, canonico, impl, obs, bool(imped))
        conceitos[mod["id"]] = {
            **{k: mod.get(k) for k in
               ("id", "nome", "nivel", "departamento", "parent", "tipo", "frase",
                "porque", "entra", "sai", "dono", "papel", "problema")},
            "legacy": bool(mod.get("legacy")),
            "canonico": canonico, "canonico_motivo": r_can,
            "implementado": impl, "implementado_motivo": r_impl,
            "observado": obs, "observado_motivo": r_obs,
            "status": st, "status_motivo": r_st,
            "autoridade": m["autoridade"],
            "observacoes": m.get("observacoes", []),
            "impedimentos": m.get("impedimentos", []),
            "ficheiros_todos": m["ficheiros"],
            "caminhos_ausentes": m["padroes_vazios"],
        }

    # ── nivel 3: cada ficheiro pertence ao dono MAIS ESPECIFICO ─────────────
    # O pai fica com o que nenhum filho reivindica. Nao ha balde de sobra:
    # ficheiro sem filho fica com o pai, e isso e dizivel numa frase.
    for pid, kids in filhos.items():
        dos_filhos = set()
        for k in kids:
            dos_filhos |= set(conceitos[k]["ficheiros_todos"])
        conceitos[pid]["ficheiros_proprios"] = [
            f for f in conceitos[pid]["ficheiros_todos"] if f not in dos_filhos]
    for cid, c in conceitos.items():
        c.setdefault("ficheiros_proprios", list(c["ficheiros_todos"]))
        c["engenharia"] = len(c["ficheiros_proprios"])

    # ── um ficheiro, um dono: dois irmaos a reivindicar o mesmo e conflito ──
    reivindicado = defaultdict(list)
    for cid, c in conceitos.items():
        for f in c["ficheiros_proprios"]:
            reivindicado[f].append(cid)
    conflitos = [{"ficheiro": f, "reivindicado_por": d}
                 for f, d in sorted(reivindicado.items()) if len(d) > 1]

    # ── o bloqueio sobe: um pai com filho bloqueado nao pode parecer inteiro ─
    for mod in modelo["CONCEITOS"]:
        cid = mod["id"]
        if not filhos.get(cid):
            continue
        presos = [k for k in filhos[cid] if conceitos[k]["status"] == BLOQUEADO]
        conceitos[cid]["bloqueados_dentro"] = presos
        if presos and conceitos[cid]["status"] in (OK, UNKNOWN):
            conceitos[cid]["status"] = ATENCAO
            conceitos[cid]["status_motivo"] = (
                f"{len(presos)} peça(s) bloqueada(s) lá dentro.")

    # ── entra de / sai para, em palavras ────────────────────────────────────
    for cid, c in conceitos.items():
        c["entra_de"] = [{"id": l["de"], "nome": nomes.get(l["de"], l["de"]),
                          "status": l["status"], "significado": l["significado"]}
                         for l in por_destino.get(cid, [])]
        c["sai_para"] = [{"id": l["para"], "nome": nomes.get(l["para"], l["para"]),
                          "status": l["status"], "significado": l["significado"]}
                         for l in por_origem.get(cid, [])]

    # ── orfandade: quem diz estar no fluxo tem de ter entrada ou saida ──────
    orfaos = []
    for cid, c in conceitos.items():
        if c["legacy"] or c["nivel"] != 1:
            continue
        if c["entra_de"] or c["sai_para"]:
            continue
        if c["papel"] in ("SOURCE_BY_DESIGN", "SINK_BY_DESIGN",
                          "TERMINAL_BY_DESIGN", "FERRAMENTA_DE_MAO", "INSTRUMENTO"):
            continue
        orfaos.append({"id": cid, "nome": c["nome"], "papel": c["papel"]})

    # ── a ordem dos cartoes E o fluxo, e nao o alfabeto ─────────────────────
    # Um mapa de processo que lista por ordem alfabetica obriga as setas a
    # cruzar-se para contar a historia certa, e quem olha le a macarronada em vez
    # do caminho. A ordem sai das proprias ligacoes: quem nao depende de ninguem
    # vem primeiro. Empate desfaz-se pela ordem em que o modelo os declara —
    # nunca pelo nome.
    ordem_decl = {c["id"]: i for i, c in enumerate(modelo["CONCEITOS"])}

    def por_fluxo(ids: list[str]) -> list[str]:
        dentro = set(ids)
        antes = {i: set() for i in ids}
        for l in ligacoes:
            if l["de"] in dentro and l["para"] in dentro and l["de"] != l["para"] \
               and not l["retorno"]:
                antes[l["para"]].add(l["de"])
        saida, restam = [], dict(antes)
        while restam:
            livres = [i for i, dep in restam.items() if not (dep & set(restam))]
            if not livres:                       # ciclo: o resto entra declarado
                livres = sorted(restam, key=lambda i: ordem_decl.get(i, 1e9))[:1]
            livres.sort(key=lambda i: ordem_decl.get(i, 1e9))
            for i in livres:
                saida.append(i)
                restam.pop(i)
        return saida

    # ── departamentos ───────────────────────────────────────────────────────
    departamentos = []
    for d in modelo["DEPARTAMENTOS"]:
        dentro = [c for c in conceitos.values()
                  if c["departamento"] == d["id"] and not c["legacy"]]
        n1 = [c for c in dentro if c["nivel"] == 1]
        piores = [c["status"] for c in n1]
        st = (BLOQUEADO if BLOQUEADO in piores else
              ATENCAO if ATENCAO in piores else
              UNKNOWN if UNKNOWN in piores or NAO_IMPL in piores else OK)
        departamentos.append({
            **{k: d[k] for k in ("id", "nome", "ordem", "familia", "frase", "papel")},
            "autoridade": med_d[d["id"]]["autoridade"],
            "status": st,
            "n1": por_fluxo([c["id"] for c in n1]),
            "conta_n1": len(n1),
            "conta_n2": len([c for c in dentro if c["nivel"] == 2]),
            "engenharia": sum(c["engenharia"] for c in dentro),
            "legado_escondido": len([c for c in conceitos.values()
                                     if c["departamento"] == d["id"] and c["legacy"]]),
        })

    st_lig = defaultdict(int)
    for l in ligacoes:
        st_lig[l["status"]] += 1

    estado = {
        "SCHEMA": "sintonia.system-map-v2.state/1",
        "LEI": modelo["LEI"],
        "PROVENANCE": medido["PROVENANCE"],
        "FAMILIAS": modelo["FAMILIAS"],
        "ROTULOS": ROTULOS,
        "DEPARTAMENTOS": sorted(departamentos, key=lambda d: d["ordem"]),
        "CONCEITOS": conceitos,
        "LIGACOES": ligacoes,
        "CANAIS": medido["CANAIS"],
        "ORFAOS_INEXPLICADOS": orfaos,
        "CONFLITOS_DE_DONO": conflitos,
        "CONTAS": {
            "LEVEL_0_CARD_COUNT": len(departamentos),
            "LEVEL_1_POR_DEPARTAMENTO": {d["id"]: d["conta_n1"] for d in departamentos},
            "SECOND_LEVEL_CARD_COUNT": sum(d["conta_n2"] for d in departamentos),
            "LEGACY_HIDDEN_COUNT": sum(1 for c in conceitos.values() if c["legacy"]),
            "ENGENHARIA_FICHEIROS": sum(c["engenharia"] for c in conceitos.values()),
            "FILES_TRACKED": medido["FILES_TRACKED"],
            "EDGES": {
                "DECLARED_COUNT": st_lig["DECLARED"],
                "IMPLEMENTED_COUNT": st_lig["IMPLEMENTED"],
                "OBSERVED_COUNT": st_lig["OBSERVED"],
                "UNKNOWN_COUNT": st_lig["UNKNOWN"],
                "TOTAL": len(ligacoes),
            },
            "UNEXPLAINED_ORPHANS": len(orfaos),
            "OWNERSHIP_CONFLICTS": len(conflitos),
            "STATUS": {s: sum(1 for c in conceitos.values() if c["status"] == s)
                       for s in (OK, ATENCAO, BLOQUEADO, NAO_IMPL, UNKNOWN, LEGADO)},
        },
    }
    SAIDA.write_text(json.dumps(estado, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    c = estado["CONTAS"]
    print(f"mapa V2 gerado · {c['LEVEL_0_CARD_COUNT']} departamentos · "
          f"{len(conceitos)} conceitos · {c['EDGES']['TOTAL']} ligacoes")
    print(f"  arestas: DECLARED={c['EDGES']['DECLARED_COUNT']} "
          f"IMPLEMENTED={c['EDGES']['IMPLEMENTED_COUNT']} "
          f"OBSERVED={c['EDGES']['OBSERVED_COUNT']} UNKNOWN={c['EDGES']['UNKNOWN_COUNT']}")
    print(f"  orfaos inexplicados: {c['UNEXPLAINED_ORPHANS']} · "
          f"conflitos de dono: {c['OWNERSHIP_CONFLICTS']} · legado: {c['LEGACY_HIDDEN_COUNT']}")
    print(f"  saude: {c['STATUS']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
