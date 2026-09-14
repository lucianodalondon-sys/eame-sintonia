#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O DENTE DA LEI DO MAPA V2. Falha fechado: engano também é FAIL.

    python3 system-map/v2/scripts/validar_mapa.py

AS MANEIRAS DE UM MAPA MENTIR, E QUAL PROVA APANHA CADA UMA
------------------------------------------------------------
    o repositório mudou e o mapa não .................. V01
    uma afirmação perdeu a autoridade ................. V02
    o mapa citou-se a si próprio como lei ............. V03  ← COL-LAW-047
    uma prova fraca virou forte ....................... V04
    o artefato existia mas não provava AQUILO ......... V05  ← a lição mais cara
    um estado foi escrito à mão ....................... V06
    uma etapa que a máquina mede sumiu do mapa ........ V07
    o legado passou por corrente ...................... V11
    um conceito virou só um ficheiro .................. V13

A V05 é a que este validador existe sobretudo para ter. A tentativa anterior
marcou uma aresta como `OBSERVED` porque o ficheiro de evidência existia — e o
ficheiro era a ENTRADA do motor, não a saída. Existir não é provar. Por isso
toda observação aponta para um CAMINHO dentro do artefato e diz o valor que
espera, e é isso que se confere aqui.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[3]
V2 = RAIZ / "system-map" / "v2"
MODELO = V2 / "model" / "maquina.model.json"
MEDIDA = V2 / "data" / "maquina.medida.json"
ESTADO = V2 / "data" / "estado.gerado.json"
ESTRADA = RAIZ / "system-map" / "data" / "pedido.observado.json"

TETO_NIVEL0, TETO_NIVEL1 = 8, 14

falhas: list[tuple[str, str, list[str]]] = []
passes: list[tuple[str, str]] = []


def prova(chave, frase, ok, detalhe=None):
    (passes if ok else falhas).append((chave, frase) if ok else (chave, frase, detalhe or []))


def git(*a):
    return subprocess.run(["git", "-C", str(RAIZ), *a], capture_output=True,
                          text=True, encoding="utf-8", errors="replace").stdout


def sem_carimbo(b: bytes) -> str:
    """O conteúdo sem PROVENANCE. O HEAD muda no próprio commit que grava o mapa:
    comparar bytes crus reprovaria toda a gente, sempre — inclusive quem acabou
    de fazer o trabalho certo."""
    try:
        d = json.loads(b.decode("utf-8"))
    except (ValueError, UnicodeDecodeError):
        return b.decode("utf-8", "replace")
    d.pop("PROVENANCE", None)
    return json.dumps(d, ensure_ascii=False, sort_keys=True)


def main() -> int:
    for f in (MODELO, MEDIDA, ESTADO):
        if not f.is_file():
            print(f"FALTA {f.relative_to(RAIZ)}", file=sys.stderr)
            return 1

    # ── V01 · o mapa commitado é o que este repositório produz hoje ─────────
    antes = (sem_carimbo(MEDIDA.read_bytes()), sem_carimbo(ESTADO.read_bytes()))
    erro = None
    for passo in ("medir_maquina.py", "gerar_mapa.py"):
        r = subprocess.run([sys.executable, str(V2 / "scripts" / passo)],
                           capture_output=True, text=True)
        if r.returncode:
            erro = f"{passo}: {r.stderr.strip()[:300]}"
            break
    if erro:
        prova("V01_SEM_DRIFT", "o mapa commitado corresponde ao repositório", False, [erro])
    else:
        depois = (sem_carimbo(MEDIDA.read_bytes()), sem_carimbo(ESTADO.read_bytes()))
        mudou = [n for n, a, b in (("maquina.medida.json", antes[0], depois[0]),
                                   ("estado.gerado.json", antes[1], depois[1])) if a != b]
        prova("V01_SEM_DRIFT", "o mapa commitado corresponde ao repositório", not mudou,
              [f"regerar mudou: {', '.join(mudou)}",
               "Conserto: python3 system-map/v2/scripts/gerar_mapa.py && git add system-map/v2/data"])

    modelo = json.loads(MODELO.read_text(encoding="utf-8"))
    medida = json.loads(MEDIDA.read_text(encoding="utf-8"))
    S = json.loads(ESTADO.read_text(encoding="utf-8"))
    C, L = S["CONCEITOS"], S["LIGACOES"]
    mc = {c["id"]: c for c in medida["CONCEITOS"]}

    # ── V02 · toda peça cita um contrato que existe e diz aquilo ────────────
    # CITAR MAL E MENTIR. NAO CITAR NADA E UMA LACUNA — e sao coisas diferentes.
    #
    # Quem aponta um contrato que nao existe, ou que nao diz aquilo, perdeu a
    # autoridade: a peca afirma-se apoiada em algo que nao a apoia, e isso
    # reprova. Quem nao aponta contrato nenhum nao esta a afirmar nada de falso
    # — esta a dizer que nao ha contrato escrito. Quatro ferramentas do portal
    # estao exatamente nesse caso, e a maquina ja o tinha medido antes de este
    # mapa existir («esta ferramenta nao tem contrato de bloco nenhum escrito»).
    #
    # Obrigar as quatro a citar alguma coisa so para a prova passar era inventar
    # autoridade — o defeito que a V03 existe para apanhar. Por isso a lacuna
    # NAO reprova aqui: fica CONTADA e IMPRESSA, o cartao mostra NAO SEI, e a
    # peca cai para ATENCAO. Some da vista em lado nenhum; deixa e de se
    # disfarcar de erro de citacao.
    sem = [x["id"] for x in medida["DEPARTAMENTOS"] + medida["CONCEITOS"]
           if x["declarado"]["estado"] not in ("CONFIRMADA", "SEM_DECLARACAO")]
    lacuna = sorted(x["id"] for x in medida["DEPARTAMENTOS"] + medida["CONCEITOS"]
                    if x["declarado"]["estado"] == "SEM_DECLARACAO")
    prova("V02_CONTRATO_CONFIRMA", "toda peça cita contrato que existe e diz aquilo",
          not sem, [f"{len(sem)}: {', '.join(sem[:8])}"])

    # ── V03 · COL-LAW-047 · o mapa não se cita a si próprio como lei ────────
    laco = [f"{x['id']} → {x['declarado']['file']}"
            for x in medida["DEPARTAMENTOS"] + medida["CONCEITOS"]
            if x["declarado"].get("gerado_pelo_mapa")]
    laco += [f"{e['de']}→{e['para']} → {e['declarada']['file']}"
             for e in medida["LIGACOES"] if e["declarada"].get("gerado_pelo_mapa")]
    prova("V03_SEM_LACO", "nenhum artefato gerado pelo mapa é usado como autoridade",
          not laco, laco + ["UM ARTEFATO GERADO PROVA «O SCANNER VIU». NUNCA «ISTO É A ARQUITETURA»."]
          if laco else [])

    # ── V04 · nenhuma prova fraca aparece como forte ────────────────────────
    maus = []
    for l in L:
        o, c, d = l["prova_observada"], l["prova_codigo"], l["prova_declarada"]
        if l["status"] == "OBSERVED" and o.get("estado") != "CONFIRMA":
            maus.append(f"{l['de']}→{l['para']}: OBSERVED sem medição que confirme")
        if l["status"] == "IMPLEMENTED" and c["estado"] != "ENCONTRADA":
            maus.append(f"{l['de']}→{l['para']}: IMPLEMENTED sem linha de código")
        if l["status"] == "DECLARED" and d["estado"] != "CONFIRMADA":
            maus.append(f"{l['de']}→{l['para']}: DECLARED sem contrato")
    prova("V04_NAO_PROMOVE", "nenhuma prova fraca aparece como prova forte", not maus, maus)

    # ── V05 · a evidência tem de provar AQUELA ligação ──────────────────────
    irrel = []
    for e in medida["LIGACOES"]:
        o = e["observada"]
        if o.get("estado") in ("ARTEFATO_AUSENTE", "ARTEFATO_ILEGIVEL", "CAMINHO_AUSENTE"):
            irrel.append(f"{e['de']}→{e['para']}: {o['estado']} em "
                         f"{o.get('artefato')}::{o.get('caminho')}")
    for cid, c in mc.items():
        for o in c["observado"]:
            if o["estado"] in ("ARTEFATO_AUSENTE", "ARTEFATO_ILEGIVEL", "CAMINHO_AUSENTE"):
                irrel.append(f"{cid}: {o['estado']} em {o['artefato']}::{o['caminho']}")
    prova("V05_EVIDENCIA_RELEVANTE",
          "toda medição aponta para um caminho que existe dentro do artefato",
          not irrel, irrel + ["ARTEFATO QUE EXISTE NÃO É ARTEFATO QUE PROVA."] if irrel else [])

    # ── V06 · estado não se escreve à mão ───────────────────────────────────
    cru = MODELO.read_text(encoding="utf-8")
    proib = sorted({p for p in ('"status"', '"saude"', '"observado":', '"codigo_status"',
                                '"OBSERVED"', '"IMPLEMENTED"', '"biblia":')
                    if p in cru})
    prova("V06_ESTADO_NAO_SE_DECLARA",
          "o modelo diz o que a peça é e onde se confere — nunca o estado dela",
          not proib, [f"o modelo contém {p}" for p in proib])

    # ── V07 · nenhuma etapa que a máquina mede ficou sem cartão ────────────
    if ESTRADA.is_file():
        etapas = set(json.loads(ESTRADA.read_text(encoding="utf-8"))
                     .get("ESTRADA", {}).keys())
        cobertas = {c.get("etapa_medida") for c in C.values() if c.get("etapa_medida")}
        faltam = sorted(etapas - cobertas)
        prova("V07_ETAPA_MEDIDA_TEM_CARTAO",
              "toda etapa que a máquina mede tem conceito no mapa",
              not faltam, [f"sem cartão: {', '.join(faltam)}",
                           "UM CONCEITO CANÓNICO NÃO SOME POR ESTAR PARCIAL."])
    else:
        prova("V07_ETAPA_MEDIDA_TEM_CARTAO", "toda etapa medida tem conceito", False,
              ["pedido.observado.json não existe — não dá para conferir"])

    # ── V08 · toda ligação diz o que significa ──────────────────────────────
    mudas = [f"{l['de']}→{l['para']}" for l in L
             if not (l.get("significado") or "").strip() or not l.get("tipo")]
    prova("V08_ARESTA_TEM_SIGNIFICADO", "toda ligação diz o que significa e de que tipo é",
          not mudas, mudas)

    # ── V09 · um ficheiro, um dono ──────────────────────────────────────────
    prova("V09_UM_DONO", "nenhum ficheiro reivindicado por duas peças com a mesma força",
          not S["CONFLITOS_DE_DONO"],
          [f"{x['ficheiro']} ← {', '.join(x['por'])}" for x in S["CONFLITOS_DE_DONO"]])

    # ── V10 · nenhum órfão sem explicação ───────────────────────────────────
    prova("V10_SEM_ORFAO", "toda peça de fluxo tem entrada, saída, ou papel que a explique",
          not S["ORFAOS_INEXPLICADOS"],
          [f"{x['id']} ({x['papel']})" for x in S["ORFAOS_INEXPLICADOS"]])

    # ── V11 · legado não se confunde com corrente ───────────────────────────
    leg = {cid for cid, c in C.items() if c["legacy"]}
    dentro = [f"{l['de']}→{l['para']}" for l in L if l["de"] in leg or l["para"] in leg]
    maus = dentro + [cid for cid in leg if C[cid]["status"] != "LEGADO"]
    prova("V11_LEGADO_SEPARADO",
          "peça de legado não participa do fluxo e tem estado próprio", not maus, maus)

    # ── V12 · a hierarquia fecha ────────────────────────────────────────────
    deps = {d["id"] for d in S["DEPARTAMENTOS"]}
    fams = {f["id"] for f in S["FAMILIAS"]}
    maus = []
    for cid, c in C.items():
        if c["departamento"] not in deps:
            maus.append(f"{cid}: departamento inexistente")
        if c["parent"] and c["parent"] not in C:
            maus.append(f"{cid}: parent inexistente")
        if c["nivel"] == 2 and not c["parent"]:
            maus.append(f"{cid}: nível 2 sem parent")
        if c["nivel"] == 1 and c["parent"]:
            maus.append(f"{cid}: nível 1 com parent")
    maus += [f"{d['id']}: família inexistente" for d in S["DEPARTAMENTOS"]
             if d["familia"] not in fams]
    reais = set(C) | deps
    maus += [f"ponta solta {l['de']}→{l['para']}" for l in L
             if l["de"] not in reais or l["para"] not in reais]
    prova("V12_HIERARQUIA_FECHA", "departamentos, famílias, níveis e pontas fecham",
          not maus, maus)

    # ── V13 · conceito arquitetural não é só um ficheiro ────────────────────
    so_ficheiro = [cid for cid, c in C.items()
                   if not (c.get("frase") or "").strip()
                   or not (c.get("porque") or "").strip()
                   or not (c.get("papel_canonico") or "").strip()]
    prova("V13_CONCEITO_NAO_E_FICHEIRO",
          "todo conceito diz o que é, por que existe e que papel canónico tem",
          not so_ficheiro, so_ficheiro)

    # ── V14 · o agrupamento não afrouxou ────────────────────────────────────
    maus = []
    if S["CONTAS"]["NIVEL_0"] > TETO_NIVEL0:
        maus.append(f"nível 0 tem {S['CONTAS']['NIVEL_0']} cartões (teto {TETO_NIVEL0})")
    for d, n in S["CONTAS"]["NIVEL_1_POR_DEPARTAMENTO"].items():
        if n > TETO_NIVEL1:
            maus.append(f"{d} tem {n} no nível 1 (teto {TETO_NIVEL1})")
    prova("V14_AGRUPAMENTO", "nenhum nível virou inventário de irmãos", not maus, maus)

    # ── V15 · a tela não guarda factos da máquina ───────────────────────────
    app = (V2 / "app" / "map.js")
    if app.is_file():
        txt = app.read_text(encoding="utf-8")
        nomes = [c["nome"] for c in C.values()] + [d["nome"] for d in S["DEPARTAMENTOS"]]
        vaz = sorted({n for n in nomes if len(n) > 6 and n in txt})
        prova("V15_TELA_SEM_FACTOS", "nenhum nome de peça está escrito dentro da tela",
              not vaz, [f"a tela contém «{n}»" for n in vaz])
    else:
        prova("V15_TELA_SEM_FACTOS", "nenhum nome de peça está escrito dentro da tela", True)

    # ── V16 · o mapa oficial não foi substituído ────────────────────────────
    # Atenção ao que esta prova mede, e ao que NÃO mede. Os dados do mapa desta
    # base MUDAM quando se declara código novo — a lei dela exige-o, e regenerar
    # é o conserto, não o defeito. O que não pode mudar é a TELA oficial, e o que
    # não pode acontecer é o candidato ocupar a rota do oficial.
    #
    #     REGENERAR O MAPA OFICIAL != SUBSTITUIR O MAPA OFICIAL.
    maus = []
    ui = [l[3:] for l in git("status", "--porcelain", "system-map/app").splitlines()]
    if ui:
        maus += [f"a tela oficial foi alterada: {x}" for x in ui]
    oficial = RAIZ / "italia-portale" / "client" / "system-map" / "index.html"
    if not oficial.is_file():
        maus.append("o mapa oficial deixou de existir em /system-map/")
    cand = RAIZ / "italia-portale" / "client" / "system-map-v2" / "index.html"
    if not cand.is_file():
        maus.append("o candidato não foi publicado em /system-map-v2/")
    if oficial.is_file() and cand.is_file() and oficial.read_bytes() == cand.read_bytes():
        maus.append("o candidato e o oficial são o mesmo ficheiro — uma rota está a ocupar a outra")
    prova("V16_OFICIAL_NAO_SUBSTITUIDO",
          "a tela oficial não mudou, e o candidato vive noutra rota", not maus, maus)

    # ── V17 · O PORTAL NAO E SO CASCA ───────────────────────────────────────
    # A maquina mede onze ferramentas na tela que o cliente abre. Se o mapa
    # mostrar menos do que onze, esta a esconder telas que existem — que era
    # exatamente o defeito: o casco a tapar tudo o que esta dentro dele.
    casco_f = RAIZ / "system-map" / "data" / "casco.generated.json"
    maus = []
    medidas = {}
    if casco_f.is_file():
        medidas = {f["vista"]: f for f in
                   json.loads(casco_f.read_text(encoding="utf-8")).get("FERRAMENTAS", [])
                   if isinstance(f, dict) and f.get("vista")}
    else:
        maus.append("system-map/data/casco.generated.json nao existe — nada foi medido")
    no_mapa = {c["ferramenta"]["vista"]: c for c in S["CONCEITOS"].values()
               if c.get("ferramenta") and c["ferramenta"].get("vista")}
    for v in sorted(set(medidas) - set(no_mapa)):
        maus.append(f"a maquina mede a ferramenta «{medidas[v]['nome']}» ({v}) e o mapa nao tem cartao dela")
    for v in sorted(set(no_mapa) - set(medidas)):
        maus.append(f"o mapa tem um cartao para «{v}» que a maquina nao mede em lado nenhum")
    prova("V17_FERRAMENTA_TEM_CARTAO",
          "toda ferramenta que o cliente abre tem cartao proprio no mapa", not maus, maus)

    # ── V18 · O NOME E O DA TELA, NAO O QUE ALGUEM ESCREVEU ─────────────────
    # O nome do cartao vem da medicao. Se o modelo trouxer outro, alguem
    # renomeou a tela num sitio e nao no outro — e o mapa passaria a chamar-lhe
    # uma coisa que o cliente nunca ve.
    maus = []
    for v, c in sorted(no_mapa.items()):
        medido = (medidas.get(v) or {}).get("nome")
        if medido and c["nome"] != medido:
            maus.append(f"{c['id']}: o mapa mostra «{c['nome']}» e a tela diz «{medido}»")
    prova("V18_NOME_E_O_DA_TELA",
          "o nome de cada ferramenta e o que foi medido na tela servida", not maus, maus)

    # ── V19 · NENHUMA SETA INVENTADA PARA DENTRO DO PORTAL ──────────────────
    # Uma ferramenta so recebe uma seta de origem se a camada que a alimenta
    # foi MEDIDA nela, com procedencia. Sem isto, o desenho ficava bonito e
    # dizia que o portal e alimentado onde ninguem provou que e.
    maus = []
    for l in S["LIGACOES"]:
        alvo = no_mapa.get((S["CONCEITOS"].get(l["para"], {}).get("ferramenta") or {}).get("vista"))
        if not alvo:
            continue
        cam = (medidas.get(alvo["ferramenta"]["vista"]) or {}).get("camadas") or {}
        reais = [k for k, x in cam.items()
                 if isinstance(x, dict) and x.get("tipo") in ("CANONICO", "REAL")]
        if not reais:
            maus.append(f"{l['de']} -> {l['para']}: nenhuma camada com procedencia foi medida nesta tela")
    sem_seta = sorted(v for v, c in no_mapa.items()
                      if not [x for x in S["LIGACOES"] if x["para"] == c["id"]])
    prova("V19_SETA_SO_ONDE_FOI_MEDIDA",
          f"so recebe seta quem tem camada medida ({len(no_mapa) - len(sem_seta)} de {len(no_mapa)})",
          not maus, maus)

    largura = 78
    print("=" * largura)
    print("SYSTEM MAP V2 — o mapa mostra a máquina, e prova cada coisa que diz")
    print("=" * largura)
    for k, f in passes:
        print(f"  PASS  {k:30s} {f}")
    for k, f, det in falhas:
        print(f"  FAIL  {k:30s} {f}")
        for d in det:
            print(f"        {d}")
    c = S["CONTAS"]
    print()
    print(f"  departamentos {c['NIVEL_0']} · nível 2 {c['NIVEL_2']} · legado {c['LEGADO']}")
    print(f"  arestas  {c['ARESTAS']}")
    print(f"  verdades {json.dumps(c['VERDADES'], ensure_ascii=False)}")
    print(f"  órfãos {c['ORFAOS']} · conflitos {c['CONFLITOS_DE_DONO']}")
    if lacuna:
        print(f"  SEM CONTRATO ESCRITO · {len(lacuna)}: {', '.join(lacuna)}")
        print("    não reprova — é lacuna medida, não citação errada. O cartão diz NÃO SEI.")
    print("=" * largura)
    if falhas:
        print(f"SYSTEM_MAP_V2_CHECK=FAIL · {len(falhas)} prova(s) reprovada(s)")
        return 1
    print(f"SYSTEM_MAP_V2_CHECK=PASS · {len(passes)} prova(s)")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except SystemExit:
        raise
    except Exception as e:
        print(f"SYSTEM_MAP_V2_CHECK=FAIL · erro inesperado: {e!r}", file=sys.stderr)
        raise SystemExit(1)
