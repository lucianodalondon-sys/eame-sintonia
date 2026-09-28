#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""L4-P2-USOS-SEM-DATA — os CONSUMIDORES em dois modos, sobre o MESMO corte da R9.

    MISSAO   L4-P2-USOS-SEM-DATA (D144 do dono real, 28/09/2026)
    ESPECIE  MEDICAO. SO LEITURA. Nao escreve na Sala, nao publica pote, nao
             toca no G0 (motor/corrida_da_inteligencia.py fica byte a byte igual).

    py -3.12 provas/l4-p2/runner.py [--saida provas/l4-p2]

A PERGUNTA QUE ESTE FICHEIRO RESPONDE, E MAIS NENHUMA
-----------------------------------------------------
    SE OS CONSUMIDORES RESPEITASSEM OS `USOS_SEM_TEMPO` QUE O G0/v4 JA DECLARA,
    QUANTOS ITENS DO MESMO CORTE CHEGAVAM A UM COMPARTIMENTO — E O «AGIR AGORA»
    AUMENTAVA?

OS DOIS MODOS
-------------
    ANTES      o codigo do HEAD, sem um byte mudado.
    DEPOIS_P2  o MESMO codigo, com UM monkeypatch em memoria: `_admite` passa a
               aceitar, SO no uso `LEITURA_ATEMPORAL_DE_CAPACIDADE`, o item que
               o G0 bloqueou SO pelo tempo do facto (`so_tempo`) — a regra que o
               gerador do pote ja tem escrita (`ADMITIDA = ... USO_SEM_TEMPO`,
               `pacote/pote_intelligence_casco.py`).

               NADA MAIS MUDA. `CAP-WIN` (a janela, o ACT_NOW), `CAP-FUT` (o
               facto sobre o futuro) e os SINAIS do livro continuam a exigir
               `G0 = PASSOU`, porque sao usos que EXIGEM tempo
               (`corrida_da_inteligencia.USOS_QUE_EXIGEM_TEMPO`).

    MUTANTE    o mesmo monkeypatch, alargado tambem a `CAP-WIN`. Serve para uma
               coisa so: mostrar se o teste de (4) reprova quando o patch deixa
               passar tambem um uso que exige tempo.

O QUE ELE NUNCA FAZ
-------------------
    NAO altera ficheiro nenhum de `motor/`, `leis/` ou `pacote/`: o patch vive
        em memoria, e o proprio runner carimba o sha256 dos ficheiros que leu,
        antes e depois, para provar que nao os escreveu.
    NAO abre rede. NAO abre a Sala: le a COPIA read-only da R9.
    NAO inventa ITEM_ID: o corte com ITEM_ID repetido e recusado pelo motor, e
        isso fica MEDIDO em vez de contornado.
"""
from __future__ import annotations

import argparse
import collections
import hashlib
import json
import re
import subprocess
import sys
from datetime import date
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
for _g in ("motor", "leis", "pacote", "provas"):
    if str(RAIZ / _g) not in sys.path:
        sys.path.insert(0, str(RAIZ / _g))

import corrida_da_inteligencia as CI            # noqa: E402
import motor_das_capacidades as MC              # noqa: E402
import capacidade_cientifica as SCI             # noqa: E402
import cap_win as WIN                           # noqa: E402
import pote_intelligence_casco as POTE          # noqa: E402

CONTRATO = "L4_P2_USOS_SEM_DATA/v1"
HOJE = date(2026, 9, 28)          # o «agora» DECLARADO (a R9 correu em 28/09/2026)

R9 = Path("C:/Users/London1/sintonia-sala-italia/intelligence-experimental"
          "/EXPD78-R9-20260928T155047Z")
SALA_DA_R9 = R9 / "copia" / "SALA_ATUAL.json"
LIVRO_DA_R9 = R9 / "saida" / "LIVRO-IR-56c79b0c78fc3fa1e747.json"

LAB = Path("C:/Users/London1/AppData/Local/hermes/profiles/sintonia-lab/lab/estudos"
           "/2026-09-28-AUDITORIA-CEGA-275")
AB_DO_LAB = LAB / "AB-DETECCAO-V1.json"
CONTRAPROVA = LAB / "contraprova" / "CONTRAPROVA-TEMPORAL.md"

#: Os ficheiros que este runner LE e nao pode escrever. O sha256 entra no
#: resultado antes e depois — uma medicao que muda o que mede nao mede nada.
INTOCAVEIS = ("motor/corrida_da_inteligencia.py", "motor/motor_das_capacidades.py",
              "motor/capacidade_cientifica.py", "motor/cap_win.py",
              "pacote/pote_intelligence_casco.py")

#: O uso do G0/v4 que o monkeypatch do P2 passa a respeitar. UM, e so este.
USO_DO_P2 = "LEITURA_ATEMPORAL_DE_CAPACIDADE"
#: Os usos que continuam a exigir `G0 = PASSOU` no DEPOIS_P2 — sao os que
#: EXIGEM tempo pela propria lei (CI.USOS_QUE_EXIGEM_TEMPO).
USOS_QUE_CONTINUAM_FECHADOS = ("SINAL_TEMPORAL", "ACT_NOW", "CAP-WIN", "CAP-FUT", "CAP-OPP")
#: Compartimentos do pote que este motor alimenta, e que uso do G0 cada um e.
USO_DO_COMPARTIMENTO = {"windows": "CAP-WIN", "science": USO_DO_P2,
                        "future": "CAP-FUT", "sources": "EVIDENCIA_NAVEGAVEL"}
#: Os compartimentos cujo uso EXIGE tempo: aqui nada pode aumentar (item 4).
COMPARTIMENTOS_COM_TEMPO = ("windows", "future")


# ══════════════════════════════════════════════════════════════════════════
# 0 · AS IMPRESSOES — a prova de que a medicao nao escreveu no que mediu
# ══════════════════════════════════════════════════════════════════════════
def impressoes() -> dict:
    return {f: hashlib.sha256((RAIZ / f).read_bytes()).hexdigest() for f in INTOCAVEIS}


def head() -> str:
    try:
        return subprocess.run(["git", "-C", str(RAIZ), "rev-parse", "HEAD"],
                              capture_output=True, text=True, check=True).stdout.strip()
    except Exception as erro:                                    # noqa: BLE001
        return CI.NAO_SEI + " — git nao respondeu: %r" % erro


# ══════════════════════════════════════════════════════════════════════════
# 1 · O CORTE — as MESMAS linhas da R9, e o que o motor recusa nelas
# ══════════════════════════════════════════════════════════════════════════
def corte_da_r9() -> dict:
    """As 275 linhas da copia da R9, e a separacao que o motor OBRIGA.

    ⚠️ O motor das capacidades recusa ITEM_ID repetido no corte
    (`motor_das_capacidades.rodar`, l.769-770: «ITEM_ID repetido no corte: nao
    serve de endereco da prova»). A copia da R9 tem 275 LINHAS e 269 ITEM_ID: 6
    documentos entram duas vezes. Isto NAO se contorna inventando identidade —
    fica medido, e a comparacao ANTES x DEPOIS corre sobre as MESMAS 269 linhas
    nos dois modos, o que a mantem uma comparacao valida.
    """
    bruto = SALA_DA_R9.read_bytes()
    linhas = json.loads(bruto.decode("utf-8"))
    contagem = collections.Counter(l["item_id"] for l in linhas)
    repetidos = sorted(k for k, v in contagem.items() if v > 1)
    vistos, unicas, fora = set(), [], []
    for i, l in enumerate(linhas):
        if l["item_id"] in vistos:
            fora.append({"ORDEM_NO_FICHEIRO": i, "ITEM_ID": l["item_id"],
                         "RUN_ID": l.get("run_id"), "ORDEM": l.get("ordem")})
            continue
        vistos.add(l["item_id"])
        unicas.append(l)
    return {
        "FICHEIRO": str(SALA_DA_R9),
        "SHA256": hashlib.sha256(bruto).hexdigest(),
        "LINHAS_NO_FICHEIRO": len(linhas),
        "ITEM_ID_DISTINTOS": len(contagem),
        "ITEM_ID_REPETIDOS": repetidos,
        "LINHAS_FORA_POR_ITEM_ID_REPETIDO": fora,
        "PORQUE_NAO_SAO_275": ("motor_das_capacidades.rodar l.769-770 recusa ITEM_ID "
                               "repetido; 275 linhas trazem 269 ITEM_ID (6 documentos "
                               "duas vezes). Nada foi renomeado: a 2.a linha de cada "
                               "repetido fica fora, e esta listada."),
        "LINHAS": unicas,
    }


def entrada_do_corte(corte: dict) -> dict:
    export = {"EXPORT": MC.EXPORT_DA_SALA, "LINHAS": corte["LINHAS"],
              "CORTE": {"SALA_ATUAL_SHA256": corte["SHA256"],
                        "LINHAS_NO_FICHEIRO": corte["LINHAS_NO_FICHEIRO"],
                        "ITENS_NA_CORRIDA": len(corte["LINHAS"]),
                        "ORIGEM": "EXPD78-R9-20260928T155047Z/copia/SALA_ATUAL.json"},
              "ORIGEM": str(SALA_DA_R9)}
    return MC.entrada_do_export(export)


# ══════════════════════════════════════════════════════════════════════════
# 2 · O MONKEYPATCH — em memoria, com o uso corrente a vista
# ══════════════════════════════════════════════════════════════════════════
_USO = {"corrente": None}
_ORIGINAIS = {"_admite": MC._admite, "_objeto_da_janela": MC._objeto_da_janela,
              "_objeto_do_estudo": MC._objeto_do_estudo,
              "_objeto_do_futuro": MC._objeto_do_futuro,
              "_rendimentos": MC._rendimentos, "conferir_saida": MC.conferir_saida}


def _com_uso(fn, uso):
    """Envolve um consumidor para dizer, enquanto ele corre, QUE uso ele e."""
    def dentro(*a, **k):
        anterior = _USO["corrente"]
        _USO["corrente"] = uso
        try:
            return fn(*a, **k)
        finally:
            _USO["corrente"] = anterior
    dentro.__name__ = getattr(fn, "__name__", "dentro")
    return dentro


def _admite_p2(usos_abertos):
    """`_admite` do P2: o item bloqueado SO pelo tempo prova um uso SEM tempo.

    A regra de `so_tempo` nao e nova nem inventada aqui: e a do gerador do pote
    (`pote_intelligence_casco.so_tempo`). Falta de SOURCE_ID ou de
    RAW_OBSERVATION_ID continua a bloquear TUDO — sem proveniencia nao ha uso.
    """
    original = _ORIGINAIS["_admite"]

    def admite(linha: dict, especie: str) -> bool:
        if original(linha, especie):
            return True
        if especie == MC.FUTURO:
            return False                      # CAP-FUT exige tempo: nunca se abre
        if _USO["corrente"] not in usos_abertos:
            return False
        return (linha.get("G0") == CI.BLOQUEADO_EM_G0
                and POTE.so_tempo(linha.get("G0_FALTA")))
    return admite


def ligar_patch(usos_abertos: tuple) -> None:
    # ⚠️ O PORTAO DA SAIDA tem de saber a MESMA regra, senao reprova a propria
    # prova que o patch admitiu. Ele entra na lista, e nada mais entra nela.
    MC._admite = _admite_p2(tuple(usos_abertos) + ("CONFERENCIA_DA_SAIDA",))
    MC._objeto_da_janela = _com_uso(_ORIGINAIS["_objeto_da_janela"], "CAP-WIN")
    MC._objeto_do_estudo = _com_uso(_ORIGINAIS["_objeto_do_estudo"], USO_DO_P2)
    MC._objeto_do_futuro = _com_uso(_ORIGINAIS["_objeto_do_futuro"], "CAP-FUT")
    MC._rendimentos = _com_uso(_ORIGINAIS["_rendimentos"], "EVIDENCIA_NAVEGAVEL")
    MC.conferir_saida = _com_uso(_ORIGINAIS["conferir_saida"], "CONFERENCIA_DA_SAIDA")


def desligar_patch() -> None:
    for nome, fn in _ORIGINAIS.items():
        setattr(MC, nome, fn)
    _USO["corrente"] = None


# ══════════════════════════════════════════════════════════════════════════
# 3 · A LEITURA DE UMA SAIDA — os numeros que a tabela usa
# ══════════════════════════════════════════════════════════════════════════
def leitura(saida: dict) -> dict:
    """O que se conta numa saida do motor. Nenhuma conta nova: tudo lido dela."""
    livro = saida["CORRIDA"]
    linha = {str(l["ITEM_ID"]): l for l in livro["LINEAGE"]}
    regra_original = _ORIGINAIS["_admite"]
    por_comp, objetos = {}, {}
    for comp, objs in saida["ITENS_POR_FERRAMENTA"].items():
        itens = sorted({str(p["ITEM_ID"]) for o in objs for p in o["PROVA"]})
        sem_g0 = sorted(i for i in itens if linha.get(i, {}).get("G0") != "PASSOU")
        # ⚠️ «Sem G0 = PASSOU» NAO e violacao em `future`: a regra ORIGINAL ja
        # admite ali o item que o G0 bloqueou SO por ser futuro (por desenho).
        # O que apanha um patch alargado e isto: prova que a regra ORIGINAL nao
        # admitia, para a especie do proprio objeto.
        fora_da_regra = sorted({str(p["ITEM_ID"]) for o in objs for p in o["PROVA"]
                                if not regra_original(linha.get(str(p["ITEM_ID"])) or {},
                                                      o.get("ESPECIE"))})
        por_comp[comp] = {
            "USO_DO_G0": USO_DO_COMPARTIMENTO.get(comp, CI.NAO_SEI),
            "OBJETOS": len(objs),
            "ITENS_NA_PROVA": len(itens),
            "ITENS": itens,
            "OBJETO_IDS": sorted(str(o["OBJETO_ID"]) for o in objs),
            "ITENS_NA_PROVA_SEM_G0_PASSOU": sem_g0,
            "ITENS_QUE_A_REGRA_ORIGINAL_NAO_ADMITIA": fora_da_regra,
        }
        for o in objs:
            objetos[str(o["OBJETO_ID"])] = {
                "COMPARTIMENTO": comp,
                "CAPACIDADE": (o.get("CHAVES") or {}).get("CAPACIDADE", CI.NAO_SEI),
                "ESPECIE_DO_MOTOR": (o.get("CHAVES") or {}).get("ESPECIE_DO_MOTOR", CI.NAO_SEI),
                "ITENS": sorted({str(p["ITEM_ID"]) for p in o["PROVA"]}),
                "RESULT": ((o.get("CHAVES") or {}).get("INTERPRETACAO_DO_SISTEMA")
                           or {}).get("RESULT", CI.NAO_SEI),
            }
    janelas = saida["CAP_WIN"]["CROP_WINDOWS"]
    act_now_janelas = sorted(j["CROP_WINDOW_ID"] for j in janelas if j["RESULT"] == WIN.ACT_NOW)
    act_now_objetos = sorted(oid for oid, o in objetos.items() if o["RESULT"] == WIN.ACT_NOW)
    return {
        "INTELLIGENCE_RUN_ID": saida["INTELLIGENCE_RUN_ID"],
        "ITENS_NA_CORRIDA": livro["INTAKE"]["RECEBIDOS"],
        "INTAKE": livro["INTAKE"],
        "SINAIS_DO_LIVRO": len(livro["SIGNALS"]),
        "SINAL_IDS": sorted(s["SIGNAL_ID"] for s in livro["SIGNALS"]),
        "ITENS_COM_G0_PASSOU": sorted(i for i, l in linha.items() if l["G0"] == "PASSOU"),
        "FACTOS_SOBRE_O_FUTURO_NO_LIVRO": len(livro["FUTURE_DATED_FACTS"]),
        "POR_COMPARTIMENTO": por_comp,
        "OBJETOS": objetos,
        "CAP_WIN": {"JANELAS": len(janelas),
                    "POR_RESULT": dict(collections.Counter(j["RESULT"] for j in janelas)),
                    "ACT_NOW_JANELAS": act_now_janelas,
                    "ACT_NOW_OBJETOS_NO_POTE": act_now_objetos},
        "CAP_SCI": {"ITENS": saida["CAP_SCI"]["UNIVERSO"]["ITENS"],
                    "JULGADOS": saida["CAP_SCI"]["UNIVERSO"]["JULGADOS"],
                    "FORA": saida["CAP_SCI"]["UNIVERSO"]["FORA"],
                    "ESTUDOS_JULGADOS": sorted(str(e["ITEM_ID"]) for e in saida["CAP_SCI"]["ESTUDOS"])},
        "NAO_ENVIADOS_AO_POTE": len(saida["NAO_ENVIADOS_AO_POTE"]),
        "NAO_ENVIADOS_POR_MOTIVO": dict(collections.Counter(
            "%s/%s" % (n["COMPARTIMENTO"], n["MOTIVO"]) for n in saida["NAO_ENVIADOS_AO_POTE"])),
    }


def correr_modo(entrada: dict, nome: str, usos_abertos: tuple | None) -> dict:
    """Uma rodada do motor, num modo. Devolve `(leitura, erro)` como dicionario."""
    antes = impressoes()
    if usos_abertos:
        ligar_patch(usos_abertos)
    try:
        saida = MC.rodar(entrada, HOJE, source_head=head())
        lido, erro = leitura(saida), None
    except Exception as e:                                       # noqa: BLE001
        saida, lido, erro = None, None, {"TIPO": type(e).__name__, "PORQUE": str(e)}
    finally:
        desligar_patch()
    depois = impressoes()
    return {"MODO": nome, "USOS_ABERTOS": list(usos_abertos or []),
            "LEITURA": lido, "ERRO": erro, "SAIDA": saida,
            "IMPRESSOES_IGUAIS_ANTES_E_DEPOIS": antes == depois}


# ══════════════════════════════════════════════════════════════════════════
# 4 · O TESTE — ACT_NOW_NAO_AUMENTOU_INCORRETAMENTE
# ══════════════════════════════════════════════════════════════════════════
def clausula_da_regra(usos_abertos: tuple, lineage: list) -> list:
    """A clausula de REGRA: o patch RECUSA os usos que exigem tempo?

    ⚠️ ESTA CLAUSULA EXISTE POR UMA RAZAO MEDIDA. Neste corte a CAP-WIN produz
    ZERO janelas por falta de LUGAR (D112a), e por isso as clausulas de SAIDA
    nunca veem um objeto de janela — um patch alargado passaria por elas sem
    deixar marca. Aqui a regra e interrogada directamente, linha a linha do
    LINEAGE real: para cada uso de `USOS_QUE_CONTINUAM_FECHADOS`, uma linha que
    nao passou G0 tem de continuar a NAO ser admitida.
    """
    admite = _admite_p2(tuple(usos_abertos) + ("CONFERENCIA_DA_SAIDA",))
    falhas = []
    anterior = _USO["corrente"]
    try:
        for uso in USOS_QUE_CONTINUAM_FECHADOS:
            _USO["corrente"] = uso
            abertos = sorted(str(l["ITEM_ID"]) for l in lineage
                             if l.get("G0") != "PASSOU" and admite(l, MC.SINAL))
            if abertos:
                falhas.append({"CLAUSULA": "o patch abriu o uso %s, que EXIGE tempo" % uso,
                               "ANTES": [], "DEPOIS_P2": abertos,
                               "ENTROU_NO_DEPOIS": abertos, "SAIU_NO_DEPOIS": []})
    finally:
        _USO["corrente"] = anterior
    return falhas


def act_now_nao_aumentou(antes: dict, depois: dict, usos_abertos: tuple,
                         lineage: list) -> dict:
    """PASS/FAIL. Onze clausulas, cada uma com a lista do que a quebrou.

    Um uso que EXIGE tempo nao pode ganhar NEM UM item por um patch que so
    devia abrir usos SEM tempo. Por isso o teste nao olha «aumentou quanto»:
    olha IGUALDADE de conjuntos na SAIDA, confere que nenhuma prova de um uso com
    tempo entrou fora da regra ORIGINAL, e ainda interroga a REGRA em si.
    """
    falhas = []

    def igual(nome, a, b):
        a, b = list(a), list(b)
        if a != b:
            falhas.append({"CLAUSULA": nome, "ANTES": a, "DEPOIS_P2": b,
                           "ENTROU_NO_DEPOIS": sorted(set(b) - set(a)),
                           "SAIU_NO_DEPOIS": sorted(set(a) - set(b))})

    igual("SINAIS_DO_LIVRO (SINAL_TEMPORAL)", antes["SINAL_IDS"], depois["SINAL_IDS"])
    igual("ITENS_COM_G0_PASSOU", antes["ITENS_COM_G0_PASSOU"], depois["ITENS_COM_G0_PASSOU"])
    igual("ACT_NOW (janelas da CAP-WIN)", antes["CAP_WIN"]["ACT_NOW_JANELAS"],
          depois["CAP_WIN"]["ACT_NOW_JANELAS"])
    igual("ACT_NOW (objetos no pote)", antes["CAP_WIN"]["ACT_NOW_OBJETOS_NO_POTE"],
          depois["CAP_WIN"]["ACT_NOW_OBJETOS_NO_POTE"])
    for comp in COMPARTIMENTOS_COM_TEMPO:
        a, b = antes["POR_COMPARTIMENTO"][comp], depois["POR_COMPARTIMENTO"][comp]
        igual("%s (%s): objetos" % (comp, USO_DO_COMPARTIMENTO[comp]),
              a["OBJETO_IDS"], b["OBJETO_IDS"])
        igual("%s (%s): itens na prova" % (comp, USO_DO_COMPARTIMENTO[comp]),
              a["ITENS"], b["ITENS"])
        igual("%s (%s): prova fora da regra ORIGINAL" % (comp, USO_DO_COMPARTIMENTO[comp]),
              a["ITENS_QUE_A_REGRA_ORIGINAL_NAO_ADMITIA"],
              b["ITENS_QUE_A_REGRA_ORIGINAL_NAO_ADMITIA"])
    da_regra = clausula_da_regra(usos_abertos, lineage)
    falhas += da_regra
    return {"ACT_NOW_NAO_AUMENTOU_INCORRETAMENTE": "PASS" if not falhas else "FAIL",
            "CLAUSULAS_CONFERIDAS": 4 + 3 * len(COMPARTIMENTOS_COM_TEMPO)
                                    + len(USOS_QUE_CONTINUAM_FECHADOS),
            "CLAUSULAS_DE_SAIDA": 4 + 3 * len(COMPARTIMENTOS_COM_TEMPO),
            "CLAUSULAS_DE_REGRA": len(USOS_QUE_CONTINUAM_FECHADOS),
            "FALHAS": falhas}


def prova_de_que_o_patch_dispara(lineage: list) -> dict:
    """O patch MUDA alguma coisa? Contado sobre as linhas reais do LINEAGE.

    Sem isto, um `P2_RECUPERA = 0` podia ser defeito do patch em vez de medicao.
    """
    original = _ORIGINAIS["_admite"]
    p2 = _admite_p2((USO_DO_P2, "CONFERENCIA_DA_SAIDA"))
    anterior = _USO["corrente"]
    try:
        _USO["corrente"] = USO_DO_P2
        orig = sorted(str(l["ITEM_ID"]) for l in lineage if original(l, MC.SINAL))
        novo = sorted(str(l["ITEM_ID"]) for l in lineage if p2(l, MC.SINAL))
    finally:
        _USO["corrente"] = anterior
    return {
        "ADMITIDOS_PELA_REGRA_ORIGINAL": len(orig),
        "ADMITIDOS_PELO_P2_NO_USO_ATEMPORAL": len(novo),
        "ABERTOS_PELO_P2": len(set(novo) - set(orig)),
        "O_PATCH_DISPARA": "SIM" if set(novo) - set(orig) else "NAO",
        "PORQUE_IMPORTA": ("se o patch nao disparasse, um P2_RECUPERA = 0 nao media nada: "
                           "mediria o patch a nao existir"),
    }


# ══════════════════════════════════════════════════════════════════════════
# 5 · O CRUZAMENTO COM O LAB
# ══════════════════════════════════════════════════════════════════════════
#: Os 69 «conhecimento sem FACT_TIME que deveria sobreviver» da CONTRAPROVA-TEMPORAL.md
#: (l.145-147): 60 de CAUSA = REGUA (53 artigos EU-T5-001 + 7 fichas, nomeadas la)
#: + 9 da lista 2D (l.93-94). As 7 fichas e os 9 da 2D vem escritos no documento; os
#: 53 artigos lem-se do proprio AB-DETECCAO-V1.json (FONTE = EU-T5-001, CAUSA = REGUA),
#: e o runner CONFERE que dao 53 — se nao derem, diz NAO SEI em vez de assumir.
FICHAS_DA_CONTRAPROVA = ("busca-3316e9e3", "busca-a18d7cd4", "busca-031b2d67",
                         "busca-51840211", "busca-85c288a9", "derived:1149", "derived:1152")
LISTA_2D_DA_CONTRAPROVA = ("derived:66", "derived:1060", "busca-9092d98a", "busca-c0e3cdb9",
                           "busca-c5037556", "busca-65e1cf45", "busca-ed6112bf",
                           "busca-4a84529c", "busca-43b74d4b")


def _casa(prefixo: str, ids: set) -> list:
    """O ITEM_ID inteiro que comeca pelo prefixo escrito na contraprova."""
    p = prefixo if prefixo.startswith("derived:") else "derived:" + prefixo
    return sorted(i for i in ids if i == p or i.startswith(p))


def lab() -> dict:
    """Os 100 A+B nao detetados e os 69 «conhecimento sem FACT_TIME», por ITEM_ID."""
    registos = json.loads(AB_DO_LAB.read_text(encoding="utf-8"))
    todos = {str(r["ITEM_ID"]) for r in registos}
    ab_100 = sorted({str(r["ITEM_ID"]) for r in registos if r["DETECTOU"] == "NAO"})
    n_100 = len([r for r in registos if r["DETECTOU"] == "NAO"])
    artigos = sorted({str(r["ITEM_ID"]) for r in registos
                      if r["FONTE"] == "EU-T5-001" and r["CAUSA"] == "REGUA"})
    fichas, faltam = [], []
    for p in FICHAS_DA_CONTRAPROVA + LISTA_2D_DA_CONTRAPROVA:
        achados = _casa(p, todos)
        fichas += achados
        if not achados:
            faltam.append(p)
    os_69 = sorted(set(artigos) | set(fichas))
    return {
        "FICHEIRO_AB": str(AB_DO_LAB),
        "SHA256_AB": hashlib.sha256(AB_DO_LAB.read_bytes()).hexdigest(),
        "SHA256_CONTRAPROVA": hashlib.sha256(CONTRAPROVA.read_bytes()).hexdigest(),
        "REGISTOS_AB": len(registos),
        "AB_NAO_DETECTADOS_REGISTOS": n_100,
        "AB_NAO_DETECTADOS_ITEM_IDS": ab_100,
        "ARTIGOS_EU_T5_001_REGUA": len(artigos),
        "OS_69_ITEM_IDS": os_69,
        "OS_69_RECONSTRUIDOS": len(os_69),
        "OS_69_CONFERE": ("SIM" if len(artigos) == 53 and not faltam else
                          "%s — artigos EU-T5-001/REGUA = %d (esperado 53), prefixos sem "
                          "item no AB: %s" % (CI.NAO_SEI, len(artigos), faltam or "nenhum")),
        "PORQUE_269_E_NAO_275": ("o AB do LAB tem 115 registos sobre 113 ITEM_ID (o mesmo "
                                 "documento rotulado duas vezes); o cruzamento e por ITEM_ID"),
    }


def recuperados(antes: dict, depois: dict, do_lab: dict) -> dict:
    """Os itens que o DEPOIS_P2 poe num compartimento e o ANTES nao punha."""
    linhas = []
    for comp in sorted(depois["POR_COMPARTIMENTO"]):
        a = set(antes["POR_COMPARTIMENTO"][comp]["ITENS"])
        for iid in depois["POR_COMPARTIMENTO"][comp]["ITENS"]:
            if iid in a:
                continue
            obj = next((o for o in depois["OBJETOS"].values()
                        if o["COMPARTIMENTO"] == comp and iid in o["ITENS"]), {})
            linhas.append({"ITEM_ID": iid, "COMPARTIMENTO": comp,
                           "CAPACIDADE": obj.get("CAPACIDADE", CI.NAO_SEI),
                           "ESPECIE_DO_MOTOR": obj.get("ESPECIE_DO_MOTOR", CI.NAO_SEI),
                           "USO_DO_G0": USO_DO_COMPARTIMENTO.get(comp, CI.NAO_SEI),
                           "ESTA_NOS_100_AB": iid in set(do_lab["AB_NAO_DETECTADOS_ITEM_IDS"]),
                           "ESTA_NOS_69": iid in set(do_lab["OS_69_ITEM_IDS"])})
    ids = {l["ITEM_ID"] for l in linhas}
    return {
        "P2_RECUPERA": len(ids),
        "P2_RECUPERA_OBJETOS": len(linhas),
        "LISTA": sorted(linhas, key=lambda l: (l["COMPARTIMENTO"], l["ITEM_ID"])),
        "DOS_100_AB": sorted(ids & set(do_lab["AB_NAO_DETECTADOS_ITEM_IDS"])),
        "DOS_100_AB_N": len(ids & set(do_lab["AB_NAO_DETECTADOS_ITEM_IDS"])),
        "DOS_69_N": len(ids & set(do_lab["OS_69_ITEM_IDS"])),
        "DOS_69": sorted(ids & set(do_lab["OS_69_ITEM_IDS"])),
        "DOS_69_QUE_FICAM_DE_FORA": sorted(set(do_lab["OS_69_ITEM_IDS"]) - ids),
        "POR_COMPARTIMENTO": dict(collections.Counter(l["COMPARTIMENTO"] for l in linhas)),
    }


def porque_a_ciencia_e_zero(entrada: dict) -> dict:
    """O portao que esta ANTES do `_admite`: a TRIAGEM pelo envelope FATO.

    `e_estudo` (motor_das_capacidades.py:319-334) le SO o envelope `FATO` do
    READY, e so aceita DOI, TRIAL_ID ou especie cientifica. Se `FATO` nem for um
    objeto, nao ha o que ler. Isto e medido item a item, e explica um zero que
    NAO e do tempo.
    """
    tipos, estudos, doi_no_item_id = collections.Counter(), 0, 0
    exemplos = []
    for r in entrada["ITENS"]:
        ready = r["READY"]
        fato = ready.get("FATO")
        tipos["dict" if isinstance(fato, dict) else "texto: %r" % fato
              if isinstance(fato, str) and len(str(fato)) < 30 else type(fato).__name__] += 1
        e, porque = MC.e_estudo(ready)
        estudos += 1 if e else 0
        iid = str(ready.get("ITEM_ID"))
        if "doi.org/" in iid:
            doi_no_item_id += 1
            if len(exemplos) < 3:
                exemplos.append({"ITEM_ID": iid, "SOURCE_ID": ready.get("SOURCE_ID"),
                                 "FATO": fato, "E_ESTUDO": e, "PORQUE": porque})
    return {
        "ITENS": len(entrada["ITENS"]),
        "FATO_POR_TIPO": dict(tipos),
        "ITENS_QUE_A_TRIAGEM_CHAMA_ESTUDO": estudos,
        "ITENS_CUJO_ITEM_ID_JA_E_UM_DOI": doi_no_item_id,
        "EXEMPLOS": exemplos,
        "LEITURA": ("a CAP-SCI julga %d estudos porque a triagem (e_estudo) nao acha identidade "
                    "de estudo em nenhum item. Os artigos cientificos trazem o DOI no proprio "
                    "ITEM_ID, e o envelope FATO deles diz «NAO_SE_APLICA» — e o FATO e o unico "
                    "sitio onde `e_estudo` olha. Este portao esta ANTES do `_admite`, e por isso "
                    "o P2 nao lhe chega." % estudos),
    }


def onde_morre(entrada: dict, saida: dict, do_lab: dict) -> dict:
    """Para cada item dos 69 e dos 100 A+B: QUAL portao o segura, por ordem.

    A ordem e a do codigo, e nao uma opiniao: primeiro a TRIAGEM (`e_estudo`),
    que decide a QUE capacidade o item vai; depois o portao de LUGAR da D112(a),
    que a CAP-WIN exige para formar uma janela; e so depois o `_admite` do G0,
    que e o unico que o P2 mexe. Quem morre num portao ANTERIOR ao `_admite` nao
    e recuperado pelo P2 — e essa e a medicao.
    """
    linha = {str(l["ITEM_ID"]): l for l in saida["CORRIDA"]["LINEAGE"]}
    d112 = saida["D112"]["LUGAR"]
    registo = {str(r["READY"]["ITEM_ID"]): r for r in entrada["ITENS"]}
    interesse = sorted(set(do_lab["OS_69_ITEM_IDS"]) | set(do_lab["AB_NAO_DETECTADOS_ITEM_IDS"]))
    fora_do_corte, linhas = [], []
    for iid in interesse:
        r = registo.get(iid)
        if r is None:
            fora_do_corte.append(iid)
            continue
        l = linha.get(iid) or {}
        estudo, porque_triagem = MC.e_estudo(r["READY"])
        regiao = (d112.get(iid) or {}).get("JANELA_DECLARADA.REGIAO_DO_FATO") or {}
        g0_ok = l.get("G0") == "PASSOU"
        so_do_tempo = POTE.so_tempo(l.get("G0_FALTA"))
        if not estudo and not regiao.get("SUSTENTADO"):
            portao, muda = ("TRIAGEM + LUGAR: nao e estudo (nao vai a CAP-SCI) e a janela nao tem "
                            "REGIAO_DO_FATO sustentada (D112a) — nao ha janela para admitir"), "NAO"
        elif not estudo:
            portao, muda = ("TRIAGEM: nao e estudo; vai a CAP-WIN, e a janela precisa de "
                            "CULTURA x PROBLEMA x REGIAO em campo"), "NAO"
        elif g0_ok:
            portao, muda = "nenhum: passou G0 e ja chegava ANTES", "NAO"
        elif so_do_tempo:
            portao, muda = ("_admite (motor_das_capacidades.py:521-526/606): bloqueado SO pelo "
                            "tempo — e exactamente o que o P2 abre"), "SIM"
        else:
            portao, muda = ("G0 por mais do que o tempo (%s): o P2 nao abre" % ", ".join(
                l.get("G0_FALTA") or []), "NAO")
        linhas.append({
            "ITEM_ID": iid, "SOURCE_ID": r["READY"].get("SOURCE_ID"),
            "NOS_69": iid in set(do_lab["OS_69_ITEM_IDS"]),
            "NOS_100_AB": iid in set(do_lab["AB_NAO_DETECTADOS_ITEM_IDS"]),
            "G0": l.get("G0"), "G0_FALTA": l.get("G0_FALTA"),
            "BLOQUEADO_SO_PELO_TEMPO": so_do_tempo,
            "USOS_DISPONIVEIS": l.get("USOS_DISPONIVEIS"),
            "E_ESTUDO": estudo, "PORQUE_A_TRIAGEM": porque_triagem,
            "REGIAO_DO_FATO_SUSTENTADA": bool(regiao.get("SUSTENTADO")),
            "PORQUE_A_REGIAO": regiao.get("PORQUE", CI.NAO_SEI),
            "PORTAO_QUE_SEGURA": portao, "O_P2_MUDA_ESTE": muda,
        })
    return {
        "ITENS_CRUZADOS": len(linhas),
        "FORA_DESTE_CORTE": fora_do_corte,
        "RESUMO_POR_PORTAO": dict(collections.Counter(
            l["PORTAO_QUE_SEGURA"].split(":")[0] for l in linhas)),
        "O_P2_MUDA": dict(collections.Counter(l["O_P2_MUDA_ESTE"] for l in linhas)),
        "LINHAS": linhas,
    }


# ══════════════════════════════════════════════════════════════════════════
# 6 · A LEITURA SOBRE OS PONTOS DO PEDIDO (item 1: ficheiro:linha no HEAD)
# ══════════════════════════════════════════════════════════════════════════
#: (ficheiro, linha, um pedaco de texto que TEM de estar nessa linha). Se a linha
#: mudar de sitio, o runner diz em que linha esta agora — nao finge que confirmou.
PONTOS = (
    ("motor/corrida_da_inteligencia.py", 155, "O QUE A FALTA DE TEMPO BLOQUEIA"),
    ("motor/corrida_da_inteligencia.py", 158, "USOS_QUE_EXIGEM_TEMPO = ("),
    ("motor/corrida_da_inteligencia.py", 169, "USOS_SEM_TEMPO = ("),
    ("motor/corrida_da_inteligencia.py", 170, "EVIDENCIA_NAVEGAVEL"),
    ("motor/corrida_da_inteligencia.py", 171, "CROSSING_SEM_CHAVE_TIME"),
    ("motor/corrida_da_inteligencia.py", 172, "LEITURA_ATEMPORAL_DE_CAPACIDADE"),
    ("motor/corrida_da_inteligencia.py", 177, "def estado_temporal("),
    ("motor/corrida_da_inteligencia.py", 206, "USOS_DISPONIVEIS"),
    ("motor/motor_das_capacidades.py", 521, "def _admite("),
    ("motor/motor_das_capacidades.py", 522, "so G0 = PASSOU prova"),
    ("motor/motor_das_capacidades.py", 526, 'return linha.get("G0") == "PASSOU"'),
    ("motor/motor_das_capacidades.py", 606, 'if not _admite(linha, SINAL):'),
    ("pacote/pote_intelligence_casco.py", 193, "So USO_SEM_TEMPO admite"),
    ("pacote/pote_intelligence_casco.py", 195, "USO_SEM_TEMPO"),
    ("pacote/pote_intelligence_casco.py", 320, "def _admite_para("),
    ("pacote/pote_intelligence_casco.py", 326, 'if e.get("G0") == "PASSOU"'),
    ("pacote/pote_intelligence_casco.py", 340, "return V1.g0_passou"),
)
MONTAR_R9 = Path("C:/Users/London1/sintonia-sala-italia/intelligence-experimental"
                 "/PARA-O-CASCO-R9/montar_r9.py")


def conferir_pontos() -> list:
    out = []
    for ficheiro, n, trecho in PONTOS:
        texto = (RAIZ / ficheiro).read_text(encoding="utf-8").splitlines()
        tem = texto[n - 1] if 0 < n <= len(texto) else ""
        onde = [i + 1 for i, l in enumerate(texto) if trecho in l]
        out.append({"ONDE": "%s:%d" % (ficheiro, n), "PROCURADO": trecho,
                    "LINHA_LIDA": tem.strip(),
                    "CONFIRMA": "SIM" if trecho in tem else "NAO",
                    "ESTA_NAS_LINHAS": onde})
    texto = MONTAR_R9.read_text(encoding="utf-8", errors="replace").splitlines()
    onde = [i + 1 for i, l in enumerate(texto) if 'LIVRO["SIGNALS"]' in l]
    out.append({"ONDE": "%s:230" % MONTAR_R9.name, "PROCURADO": 'LIVRO["SIGNALS"]',
                "LINHA_LIDA": (texto[229].strip() if len(texto) > 229 else ""),
                "CONFIRMA": "SIM" if 229 < len(texto) and 'LIVRO["SIGNALS"]' in texto[229] else "NAO",
                "ESTA_NAS_LINHAS": onde,
                "FICHEIRO": str(MONTAR_R9),
                "SHA256": hashlib.sha256(MONTAR_R9.read_bytes()).hexdigest()})
    return out


def capacidades_pedidas(antes: dict) -> dict:
    """CIENCIA · CONHECIMENTO · FICHA_TECNICA · ESTUDO — o nome REAL, ou NAO EXISTE."""
    fonte = (RAIZ / "pacote" / "pote_intelligence_casco.py").read_text(encoding="utf-8")
    nomes = set(re.findall(r'^\s*"([a-z_]+)": \{', fonte, re.M))
    def existe(*palavras):
        return sorted(p for p in palavras if p.lower() in fonte.lower() or p.lower() in nomes)
    return {
        "CIENCIA": {"NOME_REAL": "compartimento `science` («Intelligence Scientifica»); "
                                "capacidade `CAP-SCI` (motor/capacidade_cientifica.py:65)",
                    "EXISTE": "SIM",
                    "N_ANTES": antes["POR_COMPARTIMENTO"]["science"]["OBJETOS"]},
        "ESTUDO": {"NOME_REAL": "a especie de objeto `ANALYTIC_JUDGMENT/ESTUDO`, dentro de "
                               "`science` (motor/motor_das_capacidades.py:642); o julgamento "
                               "vive em CAP_SCI.ESTUDOS",
                   "EXISTE": "SIM",
                   "N_ANTES": antes["CAP_SCI"]["JULGADOS"]},
        "CONHECIMENTO": {"NOME_REAL": CI.NAO_SEI, "EXISTE": "NAO EXISTE",
                         "PORQUE": "nenhuma capacidade, compartimento nem especie deste motor "
                                   "se chama CONHECIMENTO. A palavra e do LAB (CONTRAPROVA-"
                                   "TEMPORAL.md l.145: «CONHECIMENTO_SEM_FACT_TIME»), e o "
                                   "equivalente em codigo e o uso `LEITURA_ATEMPORAL_DE_"
                                   "CAPACIDADE` (corrida_da_inteligencia.py:172) — um USO, "
                                   "nao um compartimento",
                         "ENCONTRADO_NO_POTE": existe("conhecimento", "knowledge")},
        "FICHA_TECNICA": {"NOME_REAL": CI.NAO_SEI, "EXISTE": "NAO EXISTE neste motor",
                          "PORQUE": "o compartimento mais proximo e `portfolio` («Portafoglio / "
                                    "Etichette», pote_intelligence_casco.py) lido pela CAP-LABEL, "
                                    "e o motor das capacidades NAO o alimenta: CHAVES_DO_POTE "
                                    "(motor_das_capacidades.py:144-151) so tem windows, science, "
                                    "future e sources",
                          "ENCONTRADO_NO_POTE": existe("ficha_tecnica", "portfolio", "etichette")},
    }


# ══════════════════════════════════════════════════════════════════════════
# 7 · O MAIN
# ══════════════════════════════════════════════════════════════════════════
def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="L4-P2: os consumidores em dois modos")
    ap.add_argument("--saida", default=str(Path(__file__).resolve().parent))
    a = ap.parse_args(argv)
    pasta = Path(a.saida)
    pasta.mkdir(parents=True, exist_ok=True)

    impressao_inicial = impressoes()
    corte = corte_da_r9()
    entrada = entrada_do_corte(corte)

    # O corte de 275 LINHAS, tal e qual, contra o motor — medido, nao contornado.
    todas = {"EXPORT": MC.EXPORT_DA_SALA, "LINHAS": json.loads(
        SALA_DA_R9.read_text(encoding="utf-8")), "CORTE": {"ORIGEM": "R9 275 linhas"}}
    try:
        MC.rodar(MC.entrada_do_export(todas), HOJE)
        prova_275 = {"ACEITOU_275": True}
    except Exception as e:                                       # noqa: BLE001
        prova_275 = {"ACEITOU_275": False, "TIPO": type(e).__name__, "PORQUE": str(e)}

    modos = {
        "ANTES": correr_modo(entrada, "ANTES", None),
        "DEPOIS_P2": correr_modo(entrada, "DEPOIS_P2", (USO_DO_P2,)),
        "MUTANTE_ACT_NOW": correr_modo(entrada, "MUTANTE_ACT_NOW", (USO_DO_P2, "CAP-WIN")),
    }
    for m in modos.values():
        if m["ERRO"]:
            print("MODO %s ERRO: %s" % (m["MODO"], m["ERRO"]), file=sys.stderr)

    la, ld = modos["ANTES"]["LEITURA"], modos["DEPOIS_P2"]["LEITURA"]
    if la is None or ld is None:
        Path(pasta / "RESULTADO-P2.json").write_text(json.dumps(
            {"SCHEMA": CONTRATO, "ESTADO": "ERRO", "CORTE": {k: v for k, v in corte.items()
                                                             if k != "LINHAS"},
             "PROVA_DAS_275_LINHAS": prova_275,
             "MODOS": {k: {"MODO": v["MODO"], "ERRO": v["ERRO"]} for k, v in modos.items()}},
            ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
        print("ERRO: um dos modos nao correu — ver RESULTADO-P2.json", file=sys.stderr)
        return 1

    lineage = modos["ANTES"]["SAIDA"]["CORRIDA"]["LINEAGE"]
    teste = act_now_nao_aumentou(la, ld, (USO_DO_P2,), lineage)
    do_lab = lab()
    rec = recuperados(la, ld, do_lab)
    diagnostico = onde_morre(entrada, modos["ANTES"]["SAIDA"], do_lab)

    lm = modos["MUTANTE_ACT_NOW"]["LEITURA"]
    if lm is None:
        mutante = {"MUTANTE": "NAO_CORREU", "ERRO": modos["MUTANTE_ACT_NOW"]["ERRO"],
                   "O_TESTE_REPROVA_O_MUTANTE": CI.NAO_SEI}
    else:
        tm = act_now_nao_aumentou(la, lm, (USO_DO_P2, "CAP-WIN"), lineage)
        mutante = {
            "O_QUE_O_MUTANTE_MUDA": ("o mesmo patch, com `CAP-WIN` tambem na lista de usos "
                                     "abertos: a janela passa a aceitar item bloqueado so pelo "
                                     "tempo — exactamente o que o P2 promete NAO fazer"),
            "RESULTADO_DO_TESTE": tm["ACT_NOW_NAO_AUMENTOU_INCORRETAMENTE"],
            "O_TESTE_REPROVA_O_MUTANTE": "SIM" if tm["ACT_NOW_NAO_AUMENTOU_INCORRETAMENTE"] == "FAIL" else "NAO",
            "CLAUSULAS_QUE_O_APANHARAM": [f["CLAUSULA"] for f in tm["FALHAS"]],
            "FALHAS": tm["FALHAS"],
            "ACT_NOW_NO_MUTANTE": lm["CAP_WIN"]["ACT_NOW_JANELAS"],
            "ACT_NOW_NO_ANTES": la["CAP_WIN"]["ACT_NOW_JANELAS"],
            "WINDOWS_NO_MUTANTE": lm["POR_COMPARTIMENTO"]["windows"]["OBJETOS"],
            "WINDOWS_NO_ANTES": la["POR_COMPARTIMENTO"]["windows"]["OBJETOS"],
            "CLAUSULAS_DE_SAIDA_APANHARAM": sorted(
                f["CLAUSULA"] for f in tm["FALHAS"] if not f["CLAUSULA"].startswith("o patch abriu")),
            "CLAUSULAS_DE_REGRA_APANHARAM": sorted(
                f["CLAUSULA"] for f in tm["FALHAS"] if f["CLAUSULA"].startswith("o patch abriu")),
            "RESSALVA": ("neste corte as clausulas de SAIDA sozinhas NAO apanhariam o mutante: a "
                         "CAP-WIN produz ZERO janelas por falta de REGIAO_DO_FATO sustentada "
                         "(D112a), e a CAP-WIN ainda tem uma SEGUNDA tranca de tempo "
                         "(cap_win.py:459: sem TEMPORAL_STATE = ANCORADO o estado nao e CURRENT, "
                         "e o W8 do ACT_NOW exige CURRENT). Por isso o teste tem clausula de "
                         "REGRA: pergunta ao proprio patch se ele abriu um uso que exige tempo. "
                         "As duas familias de clausula estao separadas em cima, e diz-se qual "
                         "apanhou o mutante."),
        }

    # Quantas fontes ganhariam rendimento se `sources` tambem respeitasse o uso
    # sem tempo — MEDIDO, e NAO aplicado (o P2 desta medicao nao toca `_rendimentos`).
    linha_a = {str(l["ITEM_ID"]): l for l in modos["ANTES"]["SAIDA"]["CORRIDA"]["LINEAGE"]}
    por_fonte = collections.defaultdict(list)
    for l in linha_a.values():
        por_fonte[str(l.get("SOURCE_ID"))].append(l)
    fontes_sem_g0 = sorted(f for f, ls in por_fonte.items()
                           if not any(x["G0"] == "PASSOU" for x in ls)
                           and any(x["PROVENIENCIA"] == "COMPLETA" for x in ls))

    resultado = {
        "SCHEMA": CONTRATO,
        "MISSAO": "L4-P2-USOS-SEM-DATA (D144, 28/09/2026) — SO LEITURA/MEDICAO",
        "SOURCE_HEAD": head(),
        "HOJE_DECLARADO": HOJE.isoformat(),
        "RULESET_DA_CORRIDA": CI.RULESET_VERSION,
        "G0_INTOCADO": {"IMPRESSOES_ANTES": impressao_inicial,
                        "IMPRESSOES_DEPOIS": impressoes(),
                        "IGUAIS": impressao_inicial == impressoes(),
                        "PORQUE": "o patch do DEPOIS_P2 vive em memoria; nenhum ficheiro de "
                                  "motor/ leis/ pacote/ foi escrito"},
        "ITEM_1_PONTOS_CONFIRMADOS_NO_HEAD": conferir_pontos(),
        "CORTE": {k: v for k, v in corte.items() if k != "LINHAS"},
        "PROVA_DAS_275_LINHAS": prova_275,
        "R9_PARA_COMPARAR": {
            "LIVRO": str(LIVRO_DA_R9),
            "INTELLIGENCE_RUN_ID": "IR-56c79b0c78fc3fa1e747",
            "NOTA": ("o RUN_ID desta medicao NAO pode ser o da R9: o RUN_ID leva o CODE_VERSION "
                     "do motor (corrida_da_inteligencia.identidade_da_corrida) e o universo, e "
                     "aqui o codigo e o do HEAD e o universo tem 269 linhas. O CORTE (sha256 da "
                     "copia) e o mesmo."),
        },
        "ITEM_3_CAPACIDADES_PEDIDAS": capacidades_pedidas(la),
        "ITEM_3_TABELA": {
            "ANTES": {"POR_COMPARTIMENTO": {c: {k: v for k, v in d.items() if k != "ITENS"}
                                            for c, d in la["POR_COMPARTIMENTO"].items()},
                      "CAP_WIN": la["CAP_WIN"], "CAP_SCI": {k: v for k, v in la["CAP_SCI"].items()
                                                            if k != "ESTUDOS_JULGADOS"},
                      "SINAIS_DO_LIVRO": la["SINAIS_DO_LIVRO"],
                      "NAO_ENVIADOS_AO_POTE": la["NAO_ENVIADOS_AO_POTE"],
                      "NAO_ENVIADOS_POR_MOTIVO": la["NAO_ENVIADOS_POR_MOTIVO"]},
            "DEPOIS_P2": {"POR_COMPARTIMENTO": {c: {k: v for k, v in d.items() if k != "ITENS"}
                                                for c, d in ld["POR_COMPARTIMENTO"].items()},
                          "CAP_WIN": ld["CAP_WIN"], "CAP_SCI": {k: v for k, v in ld["CAP_SCI"].items()
                                                                if k != "ESTUDOS_JULGADOS"},
                          "SINAIS_DO_LIVRO": ld["SINAIS_DO_LIVRO"],
                          "NAO_ENVIADOS_AO_POTE": ld["NAO_ENVIADOS_AO_POTE"],
                          "NAO_ENVIADOS_POR_MOTIVO": ld["NAO_ENVIADOS_POR_MOTIVO"]},
        },
        "PROVA_DE_QUE_O_PATCH_DISPARA": prova_de_que_o_patch_dispara(lineage),
        "ITEM_4_TESTE": teste,
        "ITEM_5_MUTANTE": mutante,
        "ITEM_6_LAB": do_lab,
        "ITEM_6_RECUPERADOS": rec,
        "ITEM_6_ONDE_MORRE_CADA_UM": diagnostico,
        "PORQUE_A_CIENCIA_E_ZERO": porque_a_ciencia_e_zero(entrada),
        "P2_CAUSA_REGRESSAO_ACT_NOW": ("NAO" if teste["ACT_NOW_NAO_AUMENTOU_INCORRETAMENTE"] == "PASS"
                                       else "SIM"),
        "MEDIDO_E_NAO_APLICADO": {
            "SOURCES_RENDIMENTO": {
                "PORQUE": ("`_rendimentos` (motor_das_capacidades.py:718) nao passa por `_admite`: "
                           "conta `G0 == PASSOU` a mao. O patch do P2 nao o alcanca, e mudar aquela "
                           "contagem mudava um FACTO (quantos passaram G0), nao um uso. Fica MEDIDO."),
                "FONTES_SEM_NENHUM_G0_PASSOU_MAS_COM_PROVENIENCIA_COMPLETA": len(fontes_sem_g0),
                "FONTES": fontes_sem_g0,
                "O_QUE_A_LEI_DO_POTE_DIZ": ("pote_intelligence_casco.uso_exige_tempo: especie "
                                            "RENDIMENTO nao exige tempo — logo estas fontes tambem "
                                            "seriam recuperaveis por um P2 mais largo"),
            },
        },
        "MODOS": {k: {"MODO": v["MODO"], "USOS_ABERTOS": v["USOS_ABERTOS"], "ERRO": v["ERRO"],
                      "IMPRESSOES_IGUAIS_ANTES_E_DEPOIS": v["IMPRESSOES_IGUAIS_ANTES_E_DEPOIS"],
                      "LEITURA": v["LEITURA"]} for k, v in modos.items()},
    }
    destino = pasta / "RESULTADO-P2.json"
    destino.write_text(json.dumps(resultado, ensure_ascii=False, indent=1) + "\n",
                       encoding="utf-8")
    print("P2_RECUPERA = %d (dos 100 A+B: %d · dos 69: %d) · ACT_NOW_NAO_AUMENTOU_INCORRETAMENTE = %s "
          "· MUTANTE REPROVADO = %s · %s"
          % (rec["P2_RECUPERA"], rec["DOS_100_AB_N"], rec["DOS_69_N"],
             teste["ACT_NOW_NAO_AUMENTOU_INCORRETAMENTE"],
             mutante["O_TESTE_REPROVA_O_MUTANTE"], destino), file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
