#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""A PONTE INTELLIGENCE -> CASCO — transporta, e so transporta.

    MISSAO   nuvem-int-casco-ponte-v1
    ESPECIE  ADAPTADOR DE ENTREGA (Z-PACOTE). NAO E MOTOR. NAO E TELA.
    ESTADO   IMPLEMENTED · testado com UMA corrida sintetica declarada e com a
             coorte real da Sala (que bloqueia em G0 e da zero cartoes).

    python3 pacote/ponte_intelligence_casco.py <corrida.json> <saida.json|saida.js|saida.html>
    python3 -m unittest tests.test_ponte_intelligence_casco -v

A PERGUNTA QUE ESTE FICHEIRO RESPONDE, E MAIS NENHUMA
-----------------------------------------------------
    DADA UMA CORRIDA DA INTELLIGENCE JA FECHADA, QUE CARTAO CADA FERRAMENTA
    DO CASCO PODE DESENHAR — E COM QUE PROVA?

Pega no livro de um `INTELLIGENCE_RUN` (motor/corrida_da_inteligencia.py e o
seu sucessor) e devolve UM payload com uma entrada para cada uma das doze
ferramentas do portal. Cada cartao leva:

    · a marca  EXPERIMENTAL · NAO_PARA_CLIENTE  — no payload, na ferramenta e
      no cartao, as tres, e a conferencia final reprova se faltar uma;
    · a PROVA: ITEM_ID -> RAW_OBSERVATION_ID -> SOURCE_ID -> DOCUMENT_ID, e o
      ITEM_ID tem de estar na LINHAGEM da propria corrida, com G0 = PASSOU;
    · as chaves do contrato da ferramenta (D84), com `NAO SEI` escrito por
      extenso onde a corrida nao trouxe o valor.

O QUE ELA NUNCA FAZ — INT-LAW-023 e INT-LAW-280, em codigo
----------------------------------------------------------
    NAO refaz crossing.                 NAO completa chave que falta.
    NAO escolhe ferramenta para um sinal que nao a trouxe.
    NAO promove EXPERIMENTAL_CANDIDATE a nada (so esse estado atravessa).
    NAO cunha SIGNAL_ID, DOCUMENT_ID, SOURCE_ID nem RAW_OBSERVATION_ID.
    NAO converte NAO SEI em zero, em vazio nem em falso.
    NAO escreve no portal: recusa destino dentro de italia-portale/.

As cinco operacoes que a Biblia deixa a ferramenta fazer (FILTER, NAVIGATE,
COMPARE, EXPLAIN, RENDER) nao criam informacao. Esta ponte faz menos ainda:
separa por ferramenta o que a corrida ja separou, e poe a prova ao lado.

O CONTRATO DE ENTRADA E DECLARADO AQUI, E E NOVO
------------------------------------------------
Medido a 2026-09-26 na base 69b0e23f: a palavra EXPERIMENTAL_CANDIDATE nao
existe no repositorio nem na historia do Git, e a corrida de hoje so produz
`SIGNALS` com ESTADO = SINAL e sem ferramenta. Esta ponte aceita o livro de
hoje (os sinais dele ficam em RECUSADOS com `SINAL_SEM_FERRAMENTA`, e os
REQUIREMENTS viram lacunas visiveis) e declara o que o sucessor tem de trazer:

    ITENS_POR_FERRAMENTA  { "<ferramenta>": [ sinal, ... ] }
    sinal = { SIGNAL_ID, ESTADO = "EXPERIMENTAL_CANDIDATE",
              CHAVES {..}, PROVA [ {ITEM_ID, RAW_OBSERVATION_ID, SOURCE_ID,
              DOCUMENT_ID} ], PORQUE?, CONTRADIZ?, INCERTEZA? }
    GAPS                  [ { FERRAMENTA?, ... } ]
    SINTETICA             true | false   (ausente = NAO SEI)
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))   # a raiz
import _gavetas  # noqa: E402,F401 — poe as gavetas do processo no caminho

# O vocabulario vem de quem o tem. Duas definicoes de NAO SEI divergem, e no dia
# em que divergissem a ponte deixava passar como valor o que a corrida escreveu
# como ignorancia.
from espinha_da_intelligence import NAO_SEI            # noqa: E402
from corrida_da_inteligencia import e_ignorancia       # noqa: E402

CONTRATO = "PONTE_INTELLIGENCE_CASCO/v1"
MARCA = "EXPERIMENTAL · NAO_PARA_CLIENTE"
ESTADO_TRANSPORTAVEL = "EXPERIMENTAL_CANDIDATE"
CAMPOS_DA_PROVA = ("ITEM_ID", "RAW_OBSERVATION_ID", "SOURCE_ID", "DOCUMENT_ID")

#: `INT-LAW-053` — estados da corrida que nao autorizam cartao nenhum. Cada um
#: fica escrito na ferramenta como o que e, e nunca como «zero cartoes».
CORRIDA_SEM_SAIDA = ("NOT_RUN", "RUNNING", "ERROR")
CORRIDA_VAZIA = ("EMPTY_RESULT", "NO_FINDING")

#: AS DOZE FERRAMENTAS DO CASCO QUE ESTA NO AR — a lista `AMMESSE` de
#: `VIEW_FROM_HASH()` em italia-portale/client/portale.html (as vistas que um
#: endereco consegue abrir). `casa` e outra pagina; `field` nao tem rota.
#: As chaves sao o resumo da decisao D84 que veio no pedido da missao — D84 nao
#: esta escrita no repo, e por isso a fonte fica dita aqui. D84 fala de
#: «Portafoglio/Label» como UM contrato; o casco tem duas vistas (portfolio e
#: etichette), e as duas recebem esse mesmo contrato, sem chave a mais.
#: `None` = sem contrato D84: a ponte nao inventa um, e recusa cartao para ela.
_CHAVES_T4 = ("PRODUCT_ID", "CROP_ID", "TARGET_ID", "ACTIVE_INGREDIENT_ID",
              "REGISTRATION_VERSION")
FERRAMENTAS = {
    "meeting": {
        "NOME_IT": "Radar delle Opportunità", "CAPACIDADE": "CAP-OPP",
        "CHAVES": ("CROP_ID", "ISSUE_ID", "REGION_ID", "TIME_WINDOW",
                   "ADAMA_PRODUCT_ID", "AUTHORIZATION_EVIDENCE_ID")},
    "future": {"NOME_IT": "Archivio segnali", "CAPACIDADE": None, "CHAVES": None},
    "windows": {
        "NOME_IT": "Finestre Colturali", "CAPACIDADE": "CAP-WIN",
        "CHAVES": ("CROP_ID", "REGION_ID", "ISSUE_ID", "DATE_OR_STAGE")},
    "market": {
        "NOME_IT": "Polso di Mercato", "CAPACIDADE": "CAP-MKT",
        "CHAVES": ("CROP_ID", "MARKET_PLACE_ID", "PERIOD", "PRICE", "UNIT",
                   "MARKET_STAGE")},
    "voices": {
        "NOME_IT": "Voci dal Campo", "CAPACIDADE": "CAP-FIELD",
        "CHAVES": ("SPEAKER_ID", "SPEAKER_ROLE", "QUOTE_OR_TRANSCRIPT", "CROP_ID",
                   "ISSUE_ID", "FACT_LOCATION", "FACT_TIME")},
    "competitors": {
        "NOME_IT": "Concorrenza", "CAPACIDADE": "CAP-COMP",
        "CHAVES": ("COMPANY_ID", "PRODUCT_ID", "CROP_ID", "FACT_LOCATION",
                   "FACT_TIME", "T4_REGISTRATION_EVIDENCE_ID")},
    "science": {
        "NOME_IT": "Intelligence Scientifica", "CAPACIDADE": "CAP-SCI",
        "CHAVES": ("DOI", "TRIAL_ID", "RESEARCHER_ORCID", "INSTITUTION_ID",
                   "MOLECULE", "CROP_ID", "ISSUE_ID", "STUDY_LOCATION",
                   "STUDY_PERIOD")},
    "portfolio": {"NOME_IT": "Portafoglio", "CAPACIDADE": "CAP-PORT", "CHAVES": _CHAVES_T4},
    "etichette": {"NOME_IT": "Etichette", "CAPACIDADE": "CAP-LABEL", "CHAVES": _CHAVES_T4},
    "archive": {"NOME_IT": "Archivio", "CAPACIDADE": None, "CHAVES": None},
    "sources": {"NOME_IT": "Registro delle fonti", "CAPACIDADE": None, "CHAVES": None},
    "radarfuturo": {"NOME_IT": "Radar Futuro", "CAPACIDADE": None, "CHAVES": None},
}

#: Vistas que o casco abre e que NAO sao ferramentas de Intelligence: sao de
#: OPERACAO, so de leitura (lote 2 da INTEGRA-NOITE, vivo 278cd489). `sala` tem
#: contrato PROPRIO de entrada experimental (italia-portale/audit/casco/
#: INTELLIGENCE-EXPERIMENTAL-CONTRATO.json, por item da Sala e com EMENDA
#: EXP-D78) — duas portas para a mesma fronteira, e a escolha e do dono. Esta
#: ponte nao escreve no formato dela: nao tem a EMENDA nem a chave
#: <run_id>#<ordem>, e preenche-las seria fabricar.
VISTAS_QUE_NAO_SAO_FERRAMENTA = {
    "sala": "vista de operacao da Sala, com contrato proprio CASCO_ENTRADA_INTELLIGENCE_EXPERIMENTAL/1",
    "painel": "painel de operacao so de leitura (D78)",
}


class LeiViolada(Exception):
    """A ponte recusou-se, e diz porque."""


def _valor(v):
    """O valor como veio, ou `NAO SEI` por extenso. Nunca vazio, nunca zero."""
    return NAO_SEI if e_ignorancia(v) else v


def _recusa(ferramenta, sinal, motivo, detalhe=""):
    sid = sinal.get("SIGNAL_ID") if isinstance(sinal, dict) else None
    return {"FERRAMENTA": ferramenta, "SIGNAL_ID": _valor(sid),
            "MOTIVO": motivo, "DETALHE": detalhe}


def _chave_upstream(v) -> str:
    """A corrida upstream como parte da chave. Ausente e dita como NAO SEI."""
    return NAO_SEI if e_ignorancia(v) else str(v)


def _linhagem_da_corrida(corrida: dict) -> dict:
    """(CORRIDA_UPSTREAM, ITEM_ID) -> as entradas da LINEAGE com essa chave.

    ⚠️ DEFEITO P1, FECHADO PELA CHAVE E NAO SO PELA LISTA. Na Sala real o mesmo
    ITEM_ID aparece em corridas upstream diferentes (medido na R2: 22 entradas,
    20 ITEM_ID). A v1 indexava so por ITEM_ID — primeiro guardando a ultima
    entrada (o veredito dependia da ordem), depois guardando a lista. Um
    ITEM_ID nao e uma observacao: e um nome dentro de UMA corrida upstream. A
    chave passa a ser o par, e a lista fica so para entradas repetidas da mesma
    corrida (POTE-UNICO, 2026-09-27).
    """
    out = {}
    for e in corrida.get("LINEAGE") or []:
        # G0-POR-AFIRMACAO: uma entrada de AFIRMACAO (tem CLAIM_ID) nao e uma entrada do ITEM — a prova de um
        # item nunca se admite pelo G0 de uma afirmacao dele, nem o inverso. Ela vive noutro indice (pote v2).
        if isinstance(e, dict) and "CLAIM_ID" in e:
            continue
        if isinstance(e, dict) and not e_ignorancia(e.get("ITEM_ID")):
            chave = (_chave_upstream(e.get("CORRIDA_UPSTREAM")), str(e["ITEM_ID"]))
            out.setdefault(chave, []).append(e)
    return out


def g0_passou(entrada: dict) -> bool:
    """A regra de G0 da v1: so PASSOU prova alguma coisa."""
    return entrada.get("G0") == "PASSOU"


def conferir_prova(sinal: dict, linhagem: dict, admite=g0_passou):
    """`(motivo, detalhe)` se a prova nao aguenta; `None` se aguenta.

    UM SINAL SEM PROVA NAO ATRAVESSA. E a prova nao vale por existir: cada
    elemento tem de chegar ao DOCUMENT_ID, e o par (CORRIDA_UPSTREAM, ITEM_ID)
    tem de estar na linhagem DESTA corrida, com o mesmo SOURCE_ID e
    RAW_OBSERVATION_ID, e a entrada tem de ser admitida (`admite`; por omissao
    G0 = PASSOU). Se a prova nao disser a CORRIDA_UPSTREAM e o ITEM_ID existir
    em mais de uma corrida upstream, a prova e AMBIGUA e nao passa: escolher
    uma seria a ponte a decidir que observacao o sinal quis dizer. A resposta
    nao depende da ordem da LINEAGE.
    """
    prova = sinal.get("PROVA")
    if not isinstance(prova, list) or not prova:
        return "SEM_PROVA", "o sinal nao traz PROVA"
    for p in prova:
        if not isinstance(p, dict):
            return "PROVA_INCOMPLETA", "elemento de PROVA que nao e objeto"
        falta = [c for c in CAMPOS_DA_PROVA if e_ignorancia(p.get(c))]
        if falta:
            return "PROVA_INCOMPLETA", "falta " + ", ".join(falta)
        item = str(p["ITEM_ID"])
        corridas = sorted(up for (up, it) in linhagem if it == item)
        if not corridas:
            return "PROVA_FORA_DA_CORRIDA", f"ITEM_ID {item} nao esta na LINEAGE da corrida"
        if e_ignorancia(p.get("CORRIDA_UPSTREAM")):
            if len(corridas) > 1:
                return ("PROVA_AMBIGUA", f"ITEM_ID {item} existe em {len(corridas)} corridas upstream "
                        f"({', '.join(corridas)}); a prova tem de dizer CORRIDA_UPSTREAM")
            up = corridas[0]
        else:
            up = str(p["CORRIDA_UPSTREAM"])
            if up not in corridas:
                return ("PROVA_FORA_DA_CORRIDA", f"ITEM_ID {item} nao esta na LINEAGE da corrida "
                        f"com CORRIDA_UPSTREAM {up}")
        todas = linhagem[(up, item)]
        batem = [e for e in todas
                 if all(str(e.get(c)) == str(p[c]) for c in ("SOURCE_ID", "RAW_OBSERVATION_ID"))]
        if not batem:
            # O motivo mais de base primeiro: um item que nunca passou G0 nao
            # prova nada, bata ou nao bata o resto.
            if all(not admite(e) for e in todas):
                return "ITEM_BLOQUEADO_EM_G0", f"ITEM_ID {item} nunca passou G0 nesta corrida"
            return ("PROVA_CONTRADIZ_A_CORRIDA", "nenhuma entrada da LINEAGE tem o mesmo "
                    "SOURCE_ID, RAW_OBSERVATION_ID e CORRIDA_UPSTREAM")
        if all(admite(e) for e in batem):
            continue
        g0 = sorted({str(e.get("G0")) for e in batem})
        if any(admite(e) for e in batem):
            return ("PROVA_AMBIGUA", f"ITEM_ID {item} tem G0 {g0} na mesma corrida upstream {up}")
        return "ITEM_BLOQUEADO_EM_G0", f"ITEM_ID {item} tem G0 = {g0}"
    return None


def _cartao(ferramenta: str, sinal: dict, corrida: dict) -> dict:
    """RENDER + EXPLAIN, e nada mais. Os valores sao os do sinal, ou NAO SEI."""
    chaves_contrato = FERRAMENTAS[ferramenta]["CHAVES"]
    dadas = sinal.get("CHAVES") if isinstance(sinal.get("CHAVES"), dict) else {}
    chaves = {k: _valor(dadas.get(k)) for k in chaves_contrato}
    return {
        "MARCA": MARCA,
        "NAO_PARA_CLIENTE": True,
        "FERRAMENTA": ferramenta,
        "SIGNAL_ID": sinal["SIGNAL_ID"],
        "ESTADO": ESTADO_TRANSPORTAVEL,
        "CHAVES": chaves,
        "CHAVES_NAO_SEI": [k for k in chaves_contrato if chaves[k] == NAO_SEI],
        # Chave que veio e o contrato nao pede: NAO entra em CHAVES (FACT_LOCATION
        # nao e REGION_ID, e converter seria fabricar identidade), mas viaja com o
        # VALOR, a parte e rotulada — largar o valor escondia o que a corrida disse
        # (defeito P4, achado pelo bot da Intelligence a 2026-09-26).
        "FORA_DO_CONTRATO": {k: _valor(dadas[k]) for k in sorted(dadas)
                             if k not in chaves_contrato},
        # INT-LAW-244 — por que apareceu, o que contradiz, o que e incerto.
        "PORQUE": _valor(sinal.get("PORQUE")),
        "CONTRADIZ": _valor(sinal.get("CONTRADIZ")),
        "INCERTEZA": _valor(sinal.get("INCERTEZA")),
        "PROVA": [dict({c: p[c] for c in CAMPOS_DA_PROVA},
                       CORRIDA_UPSTREAM=_valor(p.get("CORRIDA_UPSTREAM")),
                       INTELLIGENCE_RUN_ID=corrida["INTELLIGENCE_RUN_ID"])
                  for p in sinal["PROVA"]],
        "CORRIDA_SINTETICA": _sintetica(corrida),
    }


def _sintetica(corrida: dict):
    v = corrida.get("SINTETICA")
    return v if isinstance(v, bool) else NAO_SEI


def _lacunas(corrida: dict) -> list:
    """As lacunas da corrida, VERBATIM. A ponte nao cria lacuna nova."""
    out = []
    for g in corrida.get("GAPS") or []:
        if isinstance(g, dict):
            out.append(dict(g, ORIGEM="GAPS"))
    for r in corrida.get("REQUIREMENTS") or []:
        if isinstance(r, dict):
            out.append(dict(r, ORIGEM="REQUIREMENTS"))
    return out


def adaptar(corrida: dict) -> dict:
    """O livro de uma corrida -> o payload do casco, conferido antes de sair."""
    if not isinstance(corrida, dict):
        raise LeiViolada("uma corrida que nao e objeto nao se adapta")
    run_id = corrida.get("INTELLIGENCE_RUN_ID")
    if e_ignorancia(run_id):
        raise LeiViolada("corrida sem INTELLIGENCE_RUN_ID: nao ha a que ligar a prova")
    estado = corrida.get("RESULT_STATE") or NAO_SEI
    linhagem = _linhagem_da_corrida(corrida)
    lacunas = _lacunas(corrida)
    recusados = []
    por_ferramenta = corrida.get("ITENS_POR_FERRAMENTA") or {}
    if not isinstance(por_ferramenta, dict):
        raise LeiViolada("ITENS_POR_FERRAMENTA tem de ser um objeto por ferramenta")

    # O sinal do livro de hoje nao traz ferramenta. Escolher-lha seria a ponte
    # a completar um UNKNOWN (RT-TOOL-02) — fica a vista, e fica fora.
    for s in corrida.get("SIGNALS") or []:
        recusados.append(_recusa(NAO_SEI, s, "SINAL_SEM_FERRAMENTA",
                                 "a corrida nao disse para que ferramenta; a ponte nao escolhe"))
    for f, sinais in por_ferramenta.items():
        if f not in FERRAMENTAS:
            for s in (sinais if isinstance(sinais, list) else [sinais]):
                recusados.append(_recusa(f, s, "FERRAMENTA_DESCONHECIDA"))

    saida = {}
    for f, meta in FERRAMENTAS.items():
        sinais = por_ferramenta.get(f) or []
        if not isinstance(sinais, list):
            sinais = [sinais]
        entrada = {
            "MARCA": MARCA, "NAO_PARA_CLIENTE": True, "FERRAMENTA": f,
            "NOME_IT": meta["NOME_IT"], "CAPACIDADE": meta["CAPACIDADE"] or NAO_SEI,
            "CONTRATO_CHAVES": list(meta["CHAVES"]) if meta["CHAVES"] else NAO_SEI,
            "CARTOES": [],
            "LACUNAS": [g for g in lacunas if g.get("FERRAMENTA") == f],
        }
        if meta["CHAVES"] is None:
            for s in sinais:
                recusados.append(_recusa(f, s, "FERRAMENTA_SEM_CONTRATO_D84"))
            entrada["ESTADO"] = "SEM_CONTRATO_D84"
        elif estado in CORRIDA_SEM_SAIDA or estado == NAO_SEI:
            for s in sinais:
                recusados.append(_recusa(f, s, "CORRIDA_SEM_SAIDA_UTILIZAVEL", estado))
            entrada["ESTADO"] = "CORRIDA_" + str(estado).replace(" ", "_")
        else:
            vistos = set()
            for s in sinais:
                if not isinstance(s, dict):
                    recusados.append(_recusa(f, s, "ENTRADA_INVALIDA"))
                    continue
                if e_ignorancia(s.get("SIGNAL_ID")):
                    recusados.append(_recusa(f, s, "SEM_SIGNAL_ID"))
                    continue
                if s.get("ESTADO") != ESTADO_TRANSPORTAVEL:
                    recusados.append(_recusa(f, s, "ESTADO_NAO_TRANSPORTAVEL",
                                             f"ESTADO = {s.get('ESTADO', NAO_SEI)}; a ponte so leva "
                                             f"{ESTADO_TRANSPORTAVEL} e nao promove nada"))
                    continue
                falha = conferir_prova(s, linhagem)
                if falha:
                    recusados.append(_recusa(f, s, *falha))
                    continue
                if s["SIGNAL_ID"] in vistos:
                    # INT-LAW-299 — um item contribui uma vez por capacidade.
                    recusados.append(_recusa(f, s, "DUPLICADO_NA_FERRAMENTA"))
                    continue
                vistos.add(s["SIGNAL_ID"])
                entrada["CARTOES"].append(_cartao(f, s, corrida))
            if entrada["CARTOES"]:
                entrada["ESTADO"] = "COM_CARTOES_EXPERIMENTAIS"
            elif estado in CORRIDA_VAZIA:
                entrada["ESTADO"] = "CORRIDA_" + estado
            else:
                entrada["ESTADO"] = "SEM_CARTOES_NESTA_CORRIDA"
        # INT-LAW-112/281 — o numero e desta corrida, nao do mundo.
        entrada["UNIVERSO"] = {
            "INTELLIGENCE_RUN_ID": run_id, "CARTOES": len(entrada["CARTOES"]),
            "LEITURA": "cartoes NESTA corrida; zero aqui nao prova ausencia no mundo",
        }
        saida[f] = entrada

    payload = {
        "SCHEMA": CONTRATO,
        "MARCA": MARCA,
        "NAO_PARA_CLIENTE": True,
        "ORIGEM": {"INTELLIGENCE_RUN_ID": run_id, "RESULT_STATE": estado,
                   "RUN_SCHEMA": corrida.get("SCHEMA", NAO_SEI),
                   "CORRIDA_SINTETICA": _sintetica(corrida)},
        "LEI": "o portal desenha isto; nao refaz crossing, nao completa NAO SEI, "
               "nao promove (INT-LAW-023 · INT-LAW-280)",
        "FERRAMENTAS": saida,
        "LACUNAS_SEM_FERRAMENTA": [g for g in lacunas
                                   if g.get("FERRAMENTA") not in FERRAMENTAS],
        "RECUSADOS": recusados,
    }
    violacoes = conferir_payload(payload)
    if violacoes:
        raise LeiViolada("payload reprovado na conferencia: " + "; ".join(violacoes))
    return payload


def conferir_payload(payload: dict) -> list:
    """O portao de saida. Devolve a lista de violacoes; vazia = passa.

    E independente de `adaptar`: le o payload como o portal o leria. Por isso
    serve tambem para conferir um payload que chegou por outro caminho.
    """
    v = []
    if not isinstance(payload, dict):
        return ["payload nao e objeto"]
    if payload.get("MARCA") != MARCA or payload.get("NAO_PARA_CLIENTE") is not True:
        v.append("payload sem a marca EXPERIMENTAL · NAO_PARA_CLIENTE")
    ferramentas = payload.get("FERRAMENTAS")
    if not isinstance(ferramentas, dict) or set(ferramentas) != set(FERRAMENTAS):
        v.append("o payload nao traz as doze ferramentas")
        return v
    for f, e in ferramentas.items():
        if e.get("MARCA") != MARCA or e.get("NAO_PARA_CLIENTE") is not True:
            v.append(f"{f}: ferramenta sem a marca")
        contrato = FERRAMENTAS[f]["CHAVES"]
        cartoes = e.get("CARTOES") or []
        if contrato is None and cartoes:
            v.append(f"{f}: cartao numa ferramenta sem contrato D84")
        for c in cartoes:
            sid = c.get("SIGNAL_ID", "?")
            if c.get("MARCA") != MARCA or c.get("NAO_PARA_CLIENTE") is not True:
                v.append(f"{f}/{sid}: cartao sem a marca EXPERIMENTAL · NAO_PARA_CLIENTE")
            if c.get("ESTADO") != ESTADO_TRANSPORTAVEL:
                v.append(f"{f}/{sid}: estado {c.get('ESTADO')} nao e {ESTADO_TRANSPORTAVEL}")
            prova = c.get("PROVA")
            if not isinstance(prova, list) or not prova:
                v.append(f"{f}/{sid}: cartao sem prova")
            else:
                for p in prova:
                    falta = [k for k in CAMPOS_DA_PROVA + ("INTELLIGENCE_RUN_ID",)
                             if e_ignorancia((p or {}).get(k))]
                    if falta:
                        v.append(f"{f}/{sid}: prova sem {', '.join(falta)}")
            chaves = c.get("CHAVES")
            if not isinstance(chaves, dict) or (contrato and set(chaves) != set(contrato)):
                v.append(f"{f}/{sid}: chaves nao batem com o contrato D84")
            else:
                for k, val in chaves.items():
                    if e_ignorancia(val) and val != NAO_SEI:
                        v.append(f"{f}/{sid}: {k} esconde a ignorancia ({val!r} em vez de NAO SEI)")
    return v


def como_js(payload: dict) -> str:
    """O mesmo payload na forma que o casco carrega (um global no window).

    O nome do global diz o que ele e. NAO e ligado a portale.html aqui: ligar e
    deploy, e deploy nao e desta missao.
    """
    return ("/* GERADO por pacote/ponte_intelligence_casco.py — " + MARCA + ".\n"
            "   Nao e para cliente. Nao editar a mao. */\n"
            "window.SINTONIA_PONTE_EXPERIMENTAL = "
            + json.dumps(payload, ensure_ascii=False, indent=1) + ";\n")


#: Os tokens da ADAMA vem do extrato versionado, ligados — nunca copiados. O
#: extrato nao traz componente de faixa/aviso (esses vivem no Claude Design), e
#: por isso a faixa abaixo e padrao novo, declarado no relatorio da missao.
CSS_ADAMA = Path(os.path.dirname(HERE)) / "italia-portale" / "client" / "_ds" / "adama-brandwell" / "styles.css"

_CSS_PAGINA = """
body{margin:0;font-family:'BrownLL',sans-serif;color:var(--color-text-body);background:var(--color-surface-muted)}
.faixa{position:sticky;top:0;z-index:9;background:var(--color-black);color:var(--color-white);
 padding:12px 24px;font-weight:700;letter-spacing:.08em;text-align:center}
main{max-width:1100px;margin:0 auto;padding:24px}
h1,h2{color:var(--color-text-heading)} h2{border-bottom:2px solid var(--color-brand);padding-bottom:4px}
.ferramenta{background:var(--color-surface);border:1px solid var(--color-border);margin:18px 0;padding:14px 18px}
.estado{font-size:.85em;color:var(--color-brand-dark)}
.cartao{border:1px solid var(--color-border-subtle);margin:10px 0;padding:10px 12px}
.marca{display:inline-block;background:var(--color-black);color:var(--color-white);font-size:.75em;
 font-weight:700;padding:2px 8px;letter-spacing:.06em}
.naosei{font-weight:700;background:var(--color-earth-20);padding:0 4px}
table{border-collapse:collapse;width:100%} td,th{border-bottom:1px solid var(--color-border-subtle);
 text-align:left;padding:4px 6px;font-size:.9em;vertical-align:top}
"""


def como_html(payload: dict, css_href: str | None = None) -> str:
    """Uma pagina LOCAL que desenha o payload — RENDER, e mais nada.

    A marca aparece numa faixa fixa no topo e em cada cartao. `NAO SEI` sai em
    destaque, nunca em branco. Todo texto e escapado: o que veio da corrida e
    dado, nao marcacao (INT-LAW-161).
    """
    from html import escape as E
    href = css_href or CSS_ADAMA.resolve().as_uri()

    def val(v):
        s = v if isinstance(v, str) else json.dumps(v, ensure_ascii=False)
        return f'<span class="naosei">{E(s)}</span>' if s == NAO_SEI else E(s)

    o = payload["ORIGEM"]
    partes = [
        "<!doctype html><html lang=\"it\"><head><meta charset=\"utf-8\">",
        f"<title>{E(MARCA)} · ponte Intelligence -> casco</title>",
        f'<link rel="stylesheet" href="{E(href)}"><style>{_CSS_PAGINA}</style></head><body>',
        f'<div class="faixa" data-marca="1">{E(MARCA)} — anteprima locale, non per il cliente, non pubblicata</div>',
        "<main>",
        f"<h1>Ponte Intelligence → casco</h1><p>corrida <b>{E(str(o['INTELLIGENCE_RUN_ID']))}</b> · "
        f"estado {val(o['RESULT_STATE'])} · schema {val(o['RUN_SCHEMA'])} · sintetica {val(o['CORRIDA_SINTETICA'])}</p>",
        f"<p>{E(payload['LEI'])}</p>",
    ]
    for f, e in payload["FERRAMENTAS"].items():
        partes.append(f'<section class="ferramenta" id="{E(f)}"><h2>{E(e["NOME_IT"])} '
                      f'<span class="marca">{E(MARCA)}</span></h2>'
                      f'<div class="estado">{E(f)} · {E(e["ESTADO"])} · capacidade {val(e["CAPACIDADE"])} · '
                      f'{e["UNIVERSO"]["CARTOES"]} cartoes — {E(e["UNIVERSO"]["LEITURA"])}</div>')
        for c in e["CARTOES"]:
            linhas = "".join(f"<tr><th>{E(k)}</th><td>{val(v)}</td></tr>" for k, v in c["CHAVES"].items())
            fora = "".join(f"<tr><th>{E(k)}</th><td>{val(v)}</td></tr>"
                           for k, v in c["FORA_DO_CONTRATO"].items())
            if fora:
                linhas += ('<tr><th colspan="2">fuori contratto D84 — non e una chiave '
                           'della vista</th></tr>' + fora)
            prova = "".join("<li>" + " → ".join(f"{E(k)} {val(p[k])}" for k in
                                                 CAMPOS_DA_PROVA + ("INTELLIGENCE_RUN_ID",)) + "</li>"
                            for p in c["PROVA"])
            partes.append(
                f'<div class="cartao"><span class="marca" data-marca="1">{E(c["MARCA"])}</span> '
                f'<b>{E(str(c["SIGNAL_ID"]))}</b> · {E(c["ESTADO"])}<table>{linhas}</table>'
                f"<p>porque {val(c['PORQUE'])} · contradiz {val(c['CONTRADIZ'])} · incerteza {val(c['INCERTEZA'])}</p>"
                f"<p>prova:</p><ul>{prova}</ul></div>")
        for g in e["LACUNAS"]:
            partes.append(f"<p>lacuna: {E(json.dumps(g, ensure_ascii=False))}</p>")
        partes.append("</section>")
    partes.append("<h2>Recusados</h2><table><tr><th>ferramenta</th><th>sinal</th><th>motivo</th><th>detalhe</th></tr>")
    for r in payload["RECUSADOS"]:
        partes.append(f"<tr><td>{val(r['FERRAMENTA'])}</td><td>{val(r['SIGNAL_ID'])}</td>"
                      f"<td>{E(r['MOTIVO'])}</td><td>{E(str(r['DETALHE']))}</td></tr>")
    partes.append("</table><h2>Lacunas sem ferramenta</h2><ul>")
    for g in payload["LACUNAS_SEM_FERRAMENTA"]:
        partes.append(f"<li>{E(json.dumps(g, ensure_ascii=False))}</li>")
    partes.append("</ul></main></body></html>\n")
    return "".join(partes)


def destino_permitido(destino: Path) -> bool:
    """Nada desta ponte cai dentro do portal. Escrever la seria publicar."""
    raiz = Path(os.path.dirname(HERE)).resolve()
    try:
        rel = destino.resolve().relative_to(raiz)
    except ValueError:
        return True
    return not (rel.parts and rel.parts[0] == "italia-portale")


def main(argv=None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    if len(argv) != 2:
        print(__doc__.strip().split("\n\n")[0])
        print("\n  uso: python3 pacote/ponte_intelligence_casco.py <corrida.json> <saida.json|saida.js>")
        return 2
    corrida = json.loads(Path(argv[0]).read_text(encoding="utf-8"))
    destino = Path(argv[1])
    if not destino_permitido(destino):
        print("RECUSADO: o destino fica dentro de italia-portale/ — isto e NAO_PARA_CLIENTE e nao e deploy.")
        return 3
    payload = adaptar(corrida)
    if destino.suffix == ".js":
        texto = como_js(payload)
    elif destino.suffix == ".html":
        texto = como_html(payload)
    else:
        texto = json.dumps(payload, ensure_ascii=False, indent=1) + "\n"
    destino.write_text(texto, encoding="utf-8")
    n = sum(len(e["CARTOES"]) for e in payload["FERRAMENTAS"].values())
    print(f"{MARCA} · {n} cartoes · {len(payload['RECUSADOS'])} recusados · -> {destino}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
