#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CRUZA O MODELO CANÓNICO COM O ESTADO MEDIDO — e calcula. Nunca recebe pronto.

    python3 system-map/v2/scripts/gerar_mapa.py

    lê     : model/maquina.model.json   (declarado)  + data/maquina.medida.json (medido)
    escreve: data/estado.gerado.json    (é isto que a tela lê)

O QUE ELE CALCULA, E NUNCA FUNDE (COL-LAW-102)
-----------------------------------------------
    BIBLE     a Bíblia exige?          → e com que estado de implementação ela própria declara
    DECLARED  o contrato diz?
    CODE      há implementação?
    OBSERVED  alguma execução provou?

E por cima delas UMA pastilha de saúde, para quem olha de longe. A pastilha
RESUME; nunca substitui. As quatro continuam à vista no detalhe, porque foi
exatamente fundi-las que fez a tentativa anterior esconder três factos.

    O QUE DEVERIA EXISTIR · O QUE EXISTE · O QUE JÁ CORREU · O QUE NÃO SABEMOS

UM CONCEITO CANÓNICO NÃO DESAPARECE POR NÃO ESTAR IMPLEMENTADO
---------------------------------------------------------------
É a razão de a dimensão BIBLE existir. Se a Bíblia exige `STRUCTURED` e o
repositório não o tem, ele aparece no mapa como `NÃO IMPLEMENTADO` — visível,
nomeado, com a lei que o exige ao lado. Sumir seria o mapa decidir que a lei não
existe, e o mapa não decide leis.
"""

from __future__ import annotations

import json
import sys
from collections import defaultdict
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[3]
V2 = RAIZ / "system-map" / "v2"
MODELO = V2 / "model" / "maquina.model.json"
MEDIDA = V2 / "data" / "maquina.medida.json"
SAIDA = V2 / "data" / "estado.gerado.json"

OK, ATENCAO, BLOQUEADO, NAO_IMPL, UNKNOWN, LEGADO = (
    "OK", "ATENCAO", "BLOQUEADO", "NAO_IMPLEMENTADO", "UNKNOWN", "LEGADO")

# O CÓDIGO do estado é ASCII porque é ele que os testes comparam. O que a PESSOA
# lê sai daqui — a tela não escreve vocabulário nenhum, para não haver duas
# listas de nomes a divergir.
ROTULOS = {
    OK: "OK", ATENCAO: "ATENÇÃO", BLOQUEADO: "BLOQUEADO",
    NAO_IMPL: "NÃO IMPLEMENTADO", UNKNOWN: "NÃO SEI", LEGADO: "LEGADO",
    "SIM": "SIM", "NAO": "NÃO", "PARCIAL": "PARCIAL", "NAO_SEI": "NÃO SEI",
    "OBSERVED": "JÁ CORREU", "IMPLEMENTED": "HÁ CÓDIGO",
    "DECLARED": "SÓ ESCRITO", "UNKNOWN_EDGE": "NÃO SEI",
}


def d_biblia(med: dict) -> tuple[str, str]:
    b = med["biblia"]
    if not b["exigido"]:
        return "NAO_SEI", "nenhuma lei da Bíblia foi apontada para esta peça."
    est = {l["italia"] for l in b["leis"]}
    nomes = ", ".join(l["id"] for l in b["leis"][:4])
    if est <= {"IMPLEMENTED", "NOT_APPLICABLE"}:
        return "SIM", f"a Bíblia exige ({nomes}), e declara-a cumprida na Itália."
    if "ABSENT" in est:
        return "SIM", f"a Bíblia exige ({nomes}), e declara alguma delas AUSENTE na Itália."
    return "SIM", f"a Bíblia exige ({nomes}), e declara-a PARCIAL na Itália."


def d_declared(med: dict) -> tuple[str, str]:
    s = med["declarado"]
    if s["estado"] == "CONFIRMADA":
        return "SIM", f"{s['file']} diz isto, com a frase citada."
    if s["estado"] == "SEM_DECLARACAO":
        return "NAO_SEI", "nenhum contrato foi apontado."
    if s["estado"] == "FICHEIRO_AUSENTE":
        return "NAO", f"o contrato apontado ({s['file']}) não existe aqui."
    return "NAO", f"a frase citada não foi encontrada em {s['file']}."


def d_code(med: dict) -> tuple[str, str]:
    c = med["codigo"]
    dentro = med.get("codigo_em", [])
    if dentro:
        bons = [x for x in dentro if x["estado"] == "ENCONTRADO"]
        if bons and len(bons) == len(dentro):
            onde = "; ".join(f"{x['simbolo']} em {x['file']}:{x['line']}" for x in bons)
            return "SIM", f"implementado dentro de ficheiro de outro dono — {onde}"
        if bons:
            return "PARCIAL", "parte dos símbolos declarados não foi encontrada."
        return "NAO", "; ".join(f"{x['simbolo']} não existe em {x['file']}" for x in dentro)
    if not c["declarou"]:
        return "NAO", "nenhum caminho de implementação foi declarado — não há código para isto."
    if c["ficheiros"] and c["padroes_vazios"]:
        return "PARCIAL", (f"{len(c['ficheiros'])} ficheiro(s) existem; "
                           f"{len(c['padroes_vazios'])} caminho(s) declarados não existem.")
    if c["ficheiros"]:
        return "SIM", f"{len(c['ficheiros'])} ficheiro(s) reais sustentam esta peça."
    return "NAO", "nenhum dos caminhos declarados existe no repositório."


def d_observed(med: dict) -> tuple[str, str]:
    obs = med["observado"]
    if not obs:
        return "NAO_SEI", "ninguém apontou uma medição que provasse que isto correu."
    bons = [o for o in obs if o["estado"] == "CONFIRMA"]
    maus = [o for o in obs if o["estado"] != "CONFIRMA"]
    if not maus:
        return "SIM", "; ".join(f"{o['prova']} (medido: {o['valor']})" for o in bons)
    if not bons:
        return "NAO", "; ".join(
            f"{o['artefato']}::{o['caminho']} = {o['valor']} — esperava {o['espera']}"
            for o in maus)
    return "PARCIAL", ("parte das medições confirma; falha em " +
                       ", ".join(f"{o['caminho']}={o['valor']}" for o in maus))


def saude(mod, biblia, declared, code, observed) -> tuple[str, str]:
    if mod.get("legacy"):
        return LEGADO, "ficou para trás; está fora do fluxo de hoje."
    if code == "NAO":
        return (NAO_IMPL, "a Bíblia exige, e não existe implementação aqui."
                if biblia == "SIM" else "não existe implementação aqui.")
    if observed == "NAO":
        return BLOQUEADO, "a medição diz que este passo não aconteceu."
    if observed == "PARCIAL" or code == "PARCIAL":
        return ATENCAO, "funciona em parte; parte não se confirma."
    if observed == "NAO_SEI":
        return UNKNOWN, "existe no código, e ninguém provou que já correu."
    if declared == "NAO_SEI":
        # NAO HA CONTRATO nao e O CONTRATO NAO CONFIRMA.
        # Dizer «o contrato não se confirma» sobre uma peça que não tem
        # contrato nenhum manda procurar um documento que não existe, e faz
        # parecer defeito de citação o que é uma lacuna de contrato. Quatro
        # ferramentas do portal estão neste caso.
        return ATENCAO, "corre, e ninguém escreveu contrato que a descreva."
    if declared != "SIM":
        return ATENCAO, "corre, mas o contrato que a descreve não se confirma."
    return OK, "exigida, contratada, implementada e provada a correr."


def estado_ligacao(med: dict) -> tuple[str, str]:
    """NUNCA promove. E OBSERVED exige que a prova seja RELEVANTE."""
    o = med["observada"]
    if o.get("estado") == "CONFIRMA":
        return "OBSERVED", f"{o['prova']} (medido: {o['valor']})"
    if med["codigo"]["estado"] == "ENCONTRADA":
        c = med["codigo"]
        extra = ""
        if o.get("estado") not in (None, "SEM_OBSERVACAO"):
            extra = (f" · a medição apontada não confirma: "
                     f"{o.get('caminho')}={o.get('valor')}, esperava {o.get('espera')}")
        return "IMPLEMENTED", f"{c['file']}:{c['line']}{extra}"
    if med["declarada"]["estado"] == "CONFIRMADA":
        return "DECLARED", med["declarada"]["file"]
    return "UNKNOWN", "nada prova esta ligação."


def main() -> int:
    if not (MODELO.is_file() and MEDIDA.is_file()):
        print("falta o modelo ou a medição — corra o medidor primeiro", file=sys.stderr)
        return 2
    modelo = json.loads(MODELO.read_text(encoding="utf-8"))
    medida = json.loads(MEDIDA.read_text(encoding="utf-8"))
    mc = {c["id"]: c for c in medida["CONCEITOS"]}
    md = {d["id"]: d for d in medida["DEPARTAMENTOS"]}

    filhos = defaultdict(list)
    for c in modelo["CONCEITOS"]:
        if c.get("parent"):
            filhos[c["parent"]].append(c["id"])

    nomes = {d["id"]: d["nome"] for d in modelo["DEPARTAMENTOS"]}
    nomes.update({c["id"]: c["nome"] for c in modelo["CONCEITOS"]})

    ligacoes, por_origem, por_destino = [], defaultdict(list), defaultdict(list)
    for e in modelo["LIGACOES"]:
        m = next(x for x in medida["LIGACOES"]
                 if x["de"] == e["de"] and x["para"] == e["para"])
        st, motivo = estado_ligacao(m)
        lig = {"de": e["de"], "para": e["para"], "nivel": e.get("nivel", 1),
               "tipo": e.get("tipo", "DATA"), "retorno": bool(e.get("retorno")),
               "significado": e["significado"], "status": st, "motivo": motivo,
               "prova_declarada": m["declarada"], "prova_codigo": m["codigo"],
               "prova_observada": m["observada"]}
        ligacoes.append(lig)
        por_origem[e["de"]].append(lig)
        por_destino[e["para"]].append(lig)

    conceitos = {}
    for mod in modelo["CONCEITOS"]:
        m = mc[mod["id"]]
        b, rb = d_biblia(m); dc, rd = d_declared(m)
        co, rc = d_code(m);  ob, ro = d_observed(m)
        st, rs = saude(mod, b, dc, co, ob)
        conceitos[mod["id"]] = {
            **{k: mod.get(k) for k in
               ("id", "nome", "nivel", "departamento", "parent", "tipo",
                "papel_canonico", "frase", "porque", "entra", "sai", "dono",
                "papel_de_fluxo", "etapa_medida")},
            "legacy": bool(mod.get("legacy")),
            "biblia": b, "biblia_motivo": rb, "leis": m["biblia"]["leis"],
            "declarado": dc, "declarado_motivo": rd,
            "codigo": co, "codigo_motivo": rc,
            "observado": ob, "observado_motivo": ro,
            "status": st, "status_motivo": rs,
            "contrato": m["declarado"],
            "medicoes": m["observado"],
            "ficheiros_todos": m["codigo"]["ficheiros"],
            "caminhos_ausentes": m["codigo"]["padroes_vazios"],
            # O QUE O CLIENTE VE, MEDIDO NA TELA QUE ELE ABRE.
            # Só as ferramentas do portal trazem isto, e nenhuma linha é escrita
            # aqui: `scan_casco.py` leu `portale.html` e os contratos de bloco, e
            # o medidor foi buscar a linha desta vista. O nome do cartão passa a
            # ser o nome medido — se alguém renomear a tela no portal e não no
            # modelo, a prova V17 reprova em vez de o mapa mentir calado.
            "ferramenta": m.get("ferramenta"),
        }
        if m.get("ferramenta") and m["ferramenta"].get("nome"):
            conceitos[mod["id"]]["nome"] = m["ferramenta"]["nome"]

    # ── UM FICHEIRO, UM DONO ────────────────────────────────────────────────
    # A DECLARAÇÃO MAIS ESPECÍFICA GANHA. Quem nomeia `coleta/coletor.py` é dono
    # dele; quem apanhou `coleta/**` fica com o resto da gaveta. A alternativa
    # seria escrever dezanove exceções à mão — e exceção escrita à mão envelhece
    # calada, enquanto a regra se vê e se reaplica sozinha quando a gaveta cresce.
    def _espec(p):
        return (0 if p.endswith("/**") else 1,
                0 if ("*" in p or "?" in p) else 1,
                len(p.replace("*", "").replace("?", "")))

    candidatos = defaultdict(list)
    for cid, c in conceitos.items():
        for f, padrao in mc[cid]["codigo"].get("por_padrao", {}).items():
            candidatos[f].append((_espec(padrao), cid, padrao))
    dono_de = {}
    empates = []
    for f, lista in candidatos.items():
        lista.sort(reverse=True)
        dono_de[f] = lista[0][1]
        if len(lista) > 1 and lista[0][0] == lista[1][0]:
            empates.append({"ficheiro": f, "por": sorted(x[1] for x in lista
                                                         if x[0] == lista[0][0])})
    for cid, c in conceitos.items():
        c["ficheiros_proprios"] = sorted(f for f in c["ficheiros_todos"]
                                         if dono_de.get(f) == cid)
        c["engenharia"] = len(c["ficheiros_proprios"])

    # Conflito real é EMPATE de especificidade: duas peças a reivindicar o mesmo
    # ficheiro com a mesma força. Aí ninguém pode decidir por elas.
    conflitos = sorted(empates, key=lambda x: x["ficheiro"])

    for cid, c in conceitos.items():
        c["entra_de"] = [{"id": l["de"], "nome": nomes.get(l["de"], l["de"]),
                          "status": l["status"], "tipo": l["tipo"],
                          "significado": l["significado"]} for l in por_destino.get(cid, [])]
        c["sai_para"] = [{"id": l["para"], "nome": nomes.get(l["para"], l["para"]),
                          "status": l["status"], "tipo": l["tipo"],
                          "significado": l["significado"]} for l in por_origem.get(cid, [])]

    orfaos = []
    for cid, c in conceitos.items():
        if c["legacy"] or c["nivel"] != 1 or c["entra_de"] or c["sai_para"]:
            continue
        if c["papel_de_fluxo"] in ("SOURCE", "SINK", "TERMINAL", "INSTRUMENTO",
                                   "FERRAMENTA_DE_MAO"):
            continue
        orfaos.append({"id": cid, "nome": c["nome"], "papel": c["papel_de_fluxo"]})

    ordem_decl = {c["id"]: i for i, c in enumerate(modelo["CONCEITOS"])}

    def por_fluxo(ids):
        """A ordem dos cartões É o fluxo, não o alfabeto."""
        dentro = set(ids)
        antes = {i: set() for i in ids}
        for l in ligacoes:
            if l["de"] in dentro and l["para"] in dentro and l["de"] != l["para"] \
               and not l["retorno"]:
                antes[l["para"]].add(l["de"])
        saida, restam = [], dict(antes)
        while restam:
            livres = [i for i, dep in restam.items() if not (dep & set(restam))]
            if not livres:
                livres = sorted(restam, key=lambda i: ordem_decl.get(i, 1e9))[:1]
            for i in sorted(livres, key=lambda i: ordem_decl.get(i, 1e9)):
                saida.append(i); restam.pop(i)
        return saida

    departamentos = []
    for d in modelo["DEPARTAMENTOS"]:
        dentro = [c for c in conceitos.values()
                  if c["departamento"] == d["id"] and not c["legacy"]]
        n1 = [c for c in dentro if c["nivel"] == 1]
        pior = [c["status"] for c in n1]
        st = (BLOQUEADO if BLOQUEADO in pior else
              NAO_IMPL if NAO_IMPL in pior else
              ATENCAO if ATENCAO in pior else
              UNKNOWN if UNKNOWN in pior else OK)
        departamentos.append({
            **{k: d[k] for k in ("id", "nome", "ordem", "familia", "frase", "papel_de_fluxo")},
            "contrato": md[d["id"]]["declarado"], "status": st,
            "n1": por_fluxo([c["id"] for c in n1]), "conta_n1": len(n1),
            "conta_n2": len([c for c in dentro if c["nivel"] == 2]),
            "engenharia": sum(c["engenharia"] for c in dentro),
        })

    st_lig = defaultdict(int)
    for l in ligacoes:
        st_lig[l["status"]] += 1

    estado = {
        "SCHEMA": "sintonia.system-map-v2.estado/2",
        "LEI": modelo["LEI"],
        "AS_QUATRO_VERDADES": modelo["AS_QUATRO_VERDADES"],
        "PROVENANCE": medida["PROVENANCE"],
        "BIBLIA": medida["BIBLIA"],
        "ROTULOS": ROTULOS,
        "FAMILIAS": modelo["FAMILIAS"],
        "DEPARTAMENTOS": sorted(departamentos, key=lambda x: x["ordem"]),
        "CONCEITOS": conceitos,
        "LIGACOES": ligacoes,
        "ORFAOS_INEXPLICADOS": orfaos,
        "CONFLITOS_DE_DONO": conflitos,
        "CONTAS": {
            "NIVEL_0": len(departamentos),
            "NIVEL_1_POR_DEPARTAMENTO": {d["id"]: d["conta_n1"] for d in departamentos},
            "NIVEL_2": sum(d["conta_n2"] for d in departamentos),
            "LEGADO": sum(1 for c in conceitos.values() if c["legacy"]),
            "ENGENHARIA": sum(c["engenharia"] for c in conceitos.values()),
            "FILES_TRACKED": medida["FILES_TRACKED"],
            "ARESTAS": {"OBSERVED": st_lig["OBSERVED"], "IMPLEMENTED": st_lig["IMPLEMENTED"],
                        "DECLARED": st_lig["DECLARED"], "UNKNOWN": st_lig["UNKNOWN"],
                        "TOTAL": len(ligacoes)},
            "ORFAOS": len(orfaos), "CONFLITOS_DE_DONO": len(conflitos),
            "SAUDE": {s: sum(1 for c in conceitos.values() if c["status"] == s)
                      for s in (OK, ATENCAO, BLOQUEADO, NAO_IMPL, UNKNOWN, LEGADO)},
            "VERDADES": {
                d: {v: sum(1 for c in conceitos.values() if c[d] == v)
                    for v in ("SIM", "NAO", "PARCIAL", "NAO_SEI")}
                for d in ("biblia", "declarado", "codigo", "observado")},
        },
    }
    SAIDA.write_text(json.dumps(estado, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    c = estado["CONTAS"]
    print(f"mapa gerado · {c['NIVEL_0']} departamentos · {len(conceitos)} conceitos · "
          f"{c['ARESTAS']['TOTAL']} ligacoes")
    print(f"  arestas  : {c['ARESTAS']}")
    print(f"  saude    : {c['SAUDE']}")
    print(f"  verdades : {json.dumps(c['VERDADES'], ensure_ascii=False)}")
    print(f"  orfaos={c['ORFAOS']} conflitos={c['CONFLITOS_DE_DONO']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
