#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""O POTE UNICO — uma corrida da Intelligence, um compartimento por ferramenta.

    MISSAO   POTE-UNICO (decisoes D95/D96 do dono, resumidas no pedido da missao;
             D95/D96 nao estao escritas no repositorio, e por isso a fonte fica
             dita aqui)
    ESPECIE  ADAPTADOR DE ENTREGA (Z-PACOTE). NAO E MOTOR. NAO E TELA.
    CONTRATO POTE_INTELLIGENCE_CASCO/v2

    python3 pacote/pote_intelligence_casco.py <entrada.json> <saida.json|sintonia-pote.js>
    python3 -m unittest tests.test_pote_intelligence_casco -v

A PERGUNTA QUE ESTE FICHEIRO RESPONDE, E MAIS NENHUMA
-----------------------------------------------------
    DADA UMA CORRIDA DA INTELLIGENCE JA FECHADA, O QUE CADA FERRAMENTA DO
    CASCO PODE DESENHAR DELA — DE QUE ESPECIE, COM QUE PROVA ATE AO RAW — E,
    ONDE NAO HA NADA, PORQUE?

O portal lia uma inteligencia congelada (meeting-intelligence-snapshot.json,
motor V2.1, 07/09) e dados de demonstracao. A ponte v1
(pacote/ponte_intelligence_casco.py) ja levava cartoes com prova, mas: nao
dizia a ESPECIE do objeto, nao tinha vaga para o Radar Futuro (P2/P5), nem para
o Registro delle fonti e o Archivio (P3), e o portal nao a lia. Este pote e a
v2: UM ficheiro por corrida, que o portal le com precedencia sobre o snapshot e
a demo (italia-portale/client/sintonia-pote-casco.js).

O QUE ELE NUNCA FAZ — INT-LAW-023 e INT-LAW-280, em codigo
----------------------------------------------------------
    NAO refaz crossing. NAO escolhe compartimento para um objeto que nao o
    trouxe. NAO escolhe ESPECIE (a Intelligence diz; na v1, o objeto E um sinal
    por contrato). NAO promove: so EXPERIMENTAL_CANDIDATE atravessa, e um
    FATO_PRESENTE_SOBRE_O_FUTURO nunca vira OPORTUNIDADE. NAO completa chave.
    NAO converte NAO SEI em zero, vazio ou falso. NAO copia a data de
    publicacao para o tempo do facto, nem o lugar do documento para o lugar do
    facto. NAO calcula rendimento de fonte: transporta o que a corrida contou.

O CONTRATO DE ENTRADA (o que a Intelligence traz) — v1 + tres acrescentos
-------------------------------------------------------------------------
    INTELLIGENCE_RUN_ID   obrigatorio (sem ele: recusado)
    SOURCE_HEAD           o commit da arvore que a corrida leu (ausente: NAO SEI)
    CORTE                 o instante de corte da materia-prima (ausente: NAO SEI)
    RESULT_STATE, LINEAGE, GAPS, REQUIREMENTS, SIGNALS, SINTETICA   como na v1
    ITENS_POR_FERRAMENTA  { "<compartimento>": [ objeto, ... ] }
    objeto = { OBJETO_ID | SIGNAL_ID, ESPECIE?, ESTADO = EXPERIMENTAL_CANDIDATE,
               CHAVES {..}, PROVA [ {ITEM_ID, CORRIDA_UPSTREAM?,
               RAW_OBSERVATION_ID, SOURCE_ID, DOCUMENT_ID, URL?, PUBLICADO_EM?,
               COLHIDO_EM?, FACT_TIME?} ], PORQUE?, CONTRADIZ?, INCERTEZA? }

Tambem aceita um PAYLOAD ja pronto no contrato PONTE_INTELLIGENCE_CASCO/v1
(`pote_de_payload_v1`): a especie e a da v1 (SINAL), e o que a v1 nao
transportava (URL, datas, SOURCE_HEAD, CORTE) fica NAO SEI, a vista.
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))   # a raiz
import _gavetas  # noqa: E402,F401 — poe as gavetas do processo no caminho

# O vocabulario e a regra da prova vem de quem os tem: a ponte v1. Duas regras
# de prova divergem, e no dia em que divergissem o pote deixava passar o que a
# ponte recusa.
import ponte_intelligence_casco as V1                  # noqa: E402
from ponte_intelligence_casco import (                 # noqa: E402
    NAO_SEI, MARCA, ESTADO_TRANSPORTAVEL, CAMPOS_DA_PROVA, CORRIDA_SEM_SAIDA,
    CORRIDA_VAZIA, LeiViolada, e_ignorancia)

CONTRATO = "POTE_INTELLIGENCE_CASCO/v2"
NOME_DO_GLOBAL = "SINTONIA_POTE"
#: O unico sitio dentro do portal onde o pote pode ser escrito: fora do Git
#: (italia-portale/client/.gitignore) e fora do deploy (.vercelignore), como os
#: .local.js da Sala. Qualquer outro destino dentro de italia-portale/ e recusado.
DESTINO_NO_CASCO = ("italia-portale", "client", "sintonia-pote.js")

# ── AS ESPECIES ──────────────────────────────────────────────────────────────
SINAL = "SINAL"
FUTURO = "FATO_PRESENTE_SOBRE_O_FUTURO"
CROSSING = "CROSSING"
FINDING = "FINDING"
OPORTUNIDADE = "OPORTUNIDADE"
RENDIMENTO = "RENDIMENTO_DE_FONTE"
ESPECIES = (SINAL, FUTURO, CROSSING, FINDING, OPORTUNIDADE, RENDIMENTO)

#: O motivo de G0 que bloqueia POR DESENHO um facto sobre o futuro (motor/
#: corrida_da_inteligencia.py, `portao_g0`, D4: «data futura nao e facto»). E
#: o UNICO motivo que o Radar Futuro aceita: um item bloqueado por isso e so por
#: isso diz uma coisa presente sobre o futuro — nao e sinal nem oportunidade,
#: e e exatamente a especie FATO_PRESENTE_SOBRE_O_FUTURO. Qualquer outro motivo
#: (sem fonte, sem RAW, captura desconhecida) continua a bloquear.
G0_FUTURO_POR_DESENHO = "FACT_TIME:FUTURO_EM_RELACAO_A_CAPTURA"

# ── OS PORQUES DE UM COMPARTIMENTO VAZIO ─────────────────────────────────────
SEM_CONTRATO = "CASCO_SEM_CONTRATO_DE_INTELLIGENCE"
SEM_OBJETOS = "SEM_OBJETOS_NESTA_CORRIDA"
ENTRADA_V1_SEM_VAGA = "ENTRADA_V1_SEM_VAGA"
PORQUES = {
    SEM_CONTRATO: "o casco nao tem contrato de Intelligence para esta ferramenta; "
                  "nenhum objeto a pode preencher",
    SEM_OBJETOS: "esta corrida nao trouxe objeto que atravessasse para esta ferramenta; "
                 "zero aqui nao prova ausencia no mundo",
    ENTRADA_V1_SEM_VAGA: "a entrada veio no contrato v1, que nao tinha vaga para esta ferramenta",
}

_CHAVES_T4 = ("PRODUCT_ID", "CROP_ID", "TARGET_ID", "ACTIVE_INGREDIENT_ID",
              "REGISTRATION_VERSION")
_GERAIS = (SINAL, FINDING, CROSSING)

#: OS DOZE COMPARTIMENTOS (lista do dono, D95/D96). `VISTAS` = as vistas do
#: casco que leem o compartimento. ⚠️ O compartimento `future` e o RADAR FUTURO
#: e e lido pela vista #radarfuturo; a vista #future do casco chama-se
#: «Archivio segnali» e le o compartimento `archive`. O nome igual NAO e a mesma
#: coisa — o casco ja trata as duas como populacoes separadas.
#: `CHAVES` None = o casco nao tem contrato de Intelligence para ela.
COMPARTIMENTOS = {
    "meeting": {
        "NOME_IT": "Radar delle Opportunità", "VISTAS": ("meeting",),
        "ESPECIES": (OPORTUNIDADE, CROSSING, FINDING, SINAL),
        "CHAVES": V1.FERRAMENTAS["meeting"]["CHAVES"]},
    "future": {
        "NOME_IT": "Radar Futuro", "VISTAS": ("radarfuturo",),
        "ESPECIES": (FUTURO,),
        "CHAVES": ("CROP_ID", "ISSUE_ID", "REGION_ID", "FACT_LOCATION", "FACT_TIME",
                   "FACT_TIME_BASIS")},
    "windows": {"NOME_IT": "Finestre Colturali", "VISTAS": ("windows",),
                "ESPECIES": _GERAIS, "CHAVES": V1.FERRAMENTAS["windows"]["CHAVES"]},
    "market": {"NOME_IT": "Polso di Mercato", "VISTAS": ("market",),
               "ESPECIES": _GERAIS, "CHAVES": V1.FERRAMENTAS["market"]["CHAVES"]},
    "voices": {"NOME_IT": "Voci dal Campo", "VISTAS": ("voices",),
               "ESPECIES": _GERAIS, "CHAVES": V1.FERRAMENTAS["voices"]["CHAVES"]},
    "competitors": {"NOME_IT": "Concorrenza", "VISTAS": ("competitors",),
                    "ESPECIES": _GERAIS, "CHAVES": V1.FERRAMENTAS["competitors"]["CHAVES"]},
    "science": {"NOME_IT": "Intelligence Scientifica", "VISTAS": ("science",),
                "ESPECIES": _GERAIS, "CHAVES": V1.FERRAMENTAS["science"]["CHAVES"]},
    "portfolio": {"NOME_IT": "Portafoglio / Etichette", "VISTAS": ("portfolio", "etichette"),
                  "ESPECIES": _GERAIS, "CHAVES": _CHAVES_T4},
    # P3 · o arquivo dos objetos que ESTA corrida produziu. Guarda qualquer
    # especie produzida, e nenhuma muda de especie ao ser arquivada.
    "archive": {"NOME_IT": "Archivio", "VISTAS": ("archive", "future"),
                "ESPECIES": (SINAL, FINDING, CROSSING, OPORTUNIDADE, FUTURO),
                "CHAVES": ("CROP_ID", "ISSUE_ID", "REGION_ID", "FACT_LOCATION", "FACT_TIME")},
    # P3 · o rendimento de cada fonte NESTA corrida, contado pela Intelligence.
    "sources": {"NOME_IT": "Registro delle fonti", "VISTAS": ("sources",),
                "ESPECIES": (RENDIMENTO,),
                "CHAVES": ("SOURCE_ID", "ITENS_LIDOS", "ITENS_QUE_PASSARAM_G0",
                           "OBJETOS_PRODUZIDOS")},
    # `field` nao tem rota no casco; `casa` e outra pagina, e o portao
    # VIEW_READS_ONLY_ITALY_CASA (audit/casa-gate.mjs) so a deixa ler ITALY_CASA.
    "field": {"NOME_IT": "Field", "VISTAS": (), "ESPECIES": (), "CHAVES": None},
    "casa": {"NOME_IT": "Casa", "VISTAS": (), "ESPECIES": (), "CHAVES": None},
}

#: Nomes da v1 que a entrada ainda pode usar. So nomes: o objeto continua a ter
#: de ser da especie que o compartimento admite.
SINONIMOS = {"radarfuturo": "future", "etichette": "portfolio"}
#: Num PAYLOAD v1 os nomes sao os das VISTAS da v1, e la `future` era o
#: «Archivio segnali» — que na v2 le o compartimento `archive`.
DA_V1 = {"future": "archive", "radarfuturo": "future", "etichette": "portfolio"}

#: Campos da PROVA que a v2 acrescenta a v1. Nao sao obrigatorios para
#: atravessar (a v1 nao os pedia), mas nunca viajam em branco: sem valor, NAO SEI.
CAMPOS_DA_PROVA_V2 = ("URL", "PUBLICADO_EM", "COLHIDO_EM", "FACT_TIME")


def _valor(v):
    return NAO_SEI if e_ignorancia(v) else v


def _sintetica(fonte: dict):
    v = fonte.get("SINTETICA", fonte.get("CORRIDA_SINTETICA"))
    return v if isinstance(v, bool) else NAO_SEI


def _id_do_objeto(o):
    if not isinstance(o, dict):
        return None
    return o.get("OBJETO_ID") if not e_ignorancia(o.get("OBJETO_ID")) else o.get("SIGNAL_ID")


def _recusa(comp, objeto, motivo, detalhe=""):
    return {"COMPARTIMENTO": comp, "OBJETO_ID": _valor(_id_do_objeto(objeto)),
            "MOTIVO": motivo, "DETALHE": detalhe}


def _especie(objeto: dict):
    """A especie que a Intelligence disse. Ausente = o objeto da v1, que e SINAL
    POR CONTRATO (a v1 definia `sinal = {SIGNAL_ID, ...}`); nunca outra coisa."""
    e = objeto.get("ESPECIE")
    if e_ignorancia(e):
        return SINAL, "CONTRATO_V1"
    return e, "INTELLIGENCE"


def _admite_para(especie):
    """Que entrada da LINEAGE prova um objeto desta especie."""
    if especie != FUTURO:
        return V1.g0_passou

    def admite(e):
        # P2/P5 · o facto sobre o futuro prova-se por uma entrada que passou G0
        # ou que G0 bloqueou SO porque a data do facto e depois da captura.
        if e.get("G0") == "PASSOU":
            return True
        return e.get("G0") == "BLOQUEADO_EM_G0" and list(e.get("G0_FALTA") or []) == [G0_FUTURO_POR_DESENHO]
    return admite


def _prova_v2(p: dict, linhagem: dict, run_id) -> dict:
    """O elemento de prova como viaja: os campos da v1, os da v2, e a corrida.

    URL e datas vem da propria prova; se a prova nao os disser, da entrada da
    LINEAGE que a confirmou — so quando essa entrada e unica e os diz. Nunca de
    outro campo: PUBLICADO_EM nao vira FACT_TIME, e vice-versa.
    """
    up = p.get("CORRIDA_UPSTREAM")
    if e_ignorancia(up):
        candidatas = [k for k in linhagem if k[1] == str(p["ITEM_ID"])]
        chave = candidatas[0] if len(candidatas) == 1 else None
    else:
        chave = (str(up), str(p["ITEM_ID"]))
    batem = [e for e in (linhagem.get(chave) or [])
             if all(str(e.get(c)) == str(p[c]) for c in ("SOURCE_ID", "RAW_OBSERVATION_ID"))]
    out = {c: p[c] for c in CAMPOS_DA_PROVA}
    out["CORRIDA_UPSTREAM"] = _valor(up)
    for c in CAMPOS_DA_PROVA_V2:
        v = p.get(c)
        if e_ignorancia(v) and len(batem) == 1:
            v = batem[0].get(c)
        out[c] = _valor(v)
    out["INTELLIGENCE_RUN_ID"] = run_id
    return out


def _objeto(comp: str, o: dict, especie, especie_de, linhagem, run_id, sintetica) -> dict:
    """RENDER + EXPLAIN. Os valores sao os do objeto, ou NAO SEI."""
    contrato = COMPARTIMENTOS[comp]["CHAVES"]
    dadas = o.get("CHAVES") if isinstance(o.get("CHAVES"), dict) else {}
    chaves = {k: _valor(dadas.get(k)) for k in contrato}
    return {
        "MARCA": MARCA, "NAO_PARA_CLIENTE": True,
        "COMPARTIMENTO": comp,
        "OBJETO_ID": _id_do_objeto(o),
        "ESPECIE": especie, "ESPECIE_DITA_POR": especie_de,
        "ESTADO": ESTADO_TRANSPORTAVEL,
        "CHAVES": chaves,
        "CHAVES_NAO_SEI": [k for k in contrato if chaves[k] == NAO_SEI],
        # P4 · chave que veio e o contrato nao pede viaja com o NOME e o VALOR
        # que a corrida lhe deu: FACT_LOCATION continua FACT_LOCATION e nunca
        # vira REGION_ID.
        "FORA_DO_CONTRATO": {k: _valor(dadas[k]) for k in sorted(dadas) if k not in contrato},
        "PORQUE": _valor(o.get("PORQUE")),
        "CONTRADIZ": _valor(o.get("CONTRADIZ")),
        "INCERTEZA": _valor(o.get("INCERTEZA")),
        "PROVA": [_prova_v2(p, linhagem, run_id) for p in o["PROVA"]],
        "CORRIDA_SINTETICA": sintetica,
    }


def _conferir_objeto(comp, o, linhagem, vistos):
    """`(motivo, detalhe)` se o objeto nao atravessa; `None` se atravessa."""
    if not isinstance(o, dict):
        return "ENTRADA_INVALIDA", ""
    if e_ignorancia(_id_do_objeto(o)):
        return "SEM_OBJETO_ID", ""
    if o.get("ESTADO") != ESTADO_TRANSPORTAVEL:
        return ("ESTADO_NAO_TRANSPORTAVEL", f"ESTADO = {o.get('ESTADO', NAO_SEI)}; o pote so leva "
                f"{ESTADO_TRANSPORTAVEL} e nao promove nada")
    especie, _ = _especie(o)
    if especie not in ESPECIES:
        return "ESPECIE_DESCONHECIDA", f"ESPECIE = {especie}"
    admitidas = COMPARTIMENTOS[comp]["ESPECIES"]
    if especie not in admitidas:
        return ("ESPECIE_FORA_DO_COMPARTIMENTO",
                f"{especie} nao cabe em {comp} (admite {', '.join(admitidas)}); o pote nao muda especie")
    falha = V1.conferir_prova(o, linhagem, admite=_admite_para(especie))
    if falha:
        return falha
    if especie == RENDIMENTO:
        fonte = (o.get("CHAVES") or {}).get("SOURCE_ID") if isinstance(o.get("CHAVES"), dict) else None
        if e_ignorancia(fonte):
            return "RENDIMENTO_SEM_FONTE", "RENDIMENTO_DE_FONTE sem CHAVES.SOURCE_ID"
        outras = sorted({str(p["SOURCE_ID"]) for p in o["PROVA"] if str(p["SOURCE_ID"]) != str(fonte)})
        if outras:
            return "PROVA_DE_OUTRA_FONTE", f"a prova do rendimento de {fonte} traz {', '.join(outras)}"
    if _id_do_objeto(o) in vistos:
        return "DUPLICADO_NO_COMPARTIMENTO", ""
    return None


def _porque(codigo, estado=None):
    texto = PORQUES.get(codigo) or f"a corrida terminou em {estado}: nao ha saida utilizavel"
    return {"PORQUE_VAZIO": codigo, "PORQUE_TEXTO": texto}


def _cabecalho(run_id, fonte, estado, origem, sintetica) -> dict:
    return {
        "SCHEMA": CONTRATO, "MARCA": MARCA, "NAO_PARA_CLIENTE": True,
        # UM POTE POR CORRIDA: estes tres dizem QUE corrida, sobre QUE arvore,
        # com materia-prima cortada QUANDO.
        "INTELLIGENCE_RUN_ID": run_id,
        "SOURCE_HEAD": _valor(fonte.get("SOURCE_HEAD")),
        "CORTE": _valor(fonte.get("CORTE")),
        "RESULT_STATE": estado,
        "RUN_SCHEMA": fonte.get("SCHEMA", NAO_SEI),
        "CORRIDA_SINTETICA": sintetica,
        "ENTRADA": origem,
        "LEI": "o casco desenha isto; nao refaz crossing, nao completa NAO SEI, nao promove, "
               "nao muda especie (INT-LAW-023 · INT-LAW-280)",
    }


def _vazio_ou_cheio(entrada, comp, estado):
    meta = COMPARTIMENTOS[comp]
    if entrada["OBJETOS"]:
        entrada["ESTADO"] = "COM_OBJETOS"
        entrada.update(PORQUE_VAZIO=None, PORQUE_TEXTO=None)
    elif meta["CHAVES"] is None:
        entrada["ESTADO"] = "VAZIO"
        entrada.update(_porque(SEM_CONTRATO))
    elif estado in CORRIDA_SEM_SAIDA or estado == NAO_SEI or estado in CORRIDA_VAZIA:
        entrada["ESTADO"] = "VAZIO"
        entrada.update(_porque("CORRIDA_" + str(estado).replace(" ", "_"), estado))
    else:
        entrada["ESTADO"] = "VAZIO"
        entrada.update(_porque(SEM_OBJETOS))


def _fechar(saida: dict, recusados: list):
    """Quantos objetos cada compartimento recusou — contados, nunca escondidos."""
    for comp, e in saida.items():
        e["UNIVERSO"]["OBJETOS"] = len(e["OBJETOS"])
        e["RECUSADOS_AQUI"] = sum(1 for r in recusados if r.get("COMPARTIMENTO") == comp)


def _compartimento_base(comp, run_id, lacunas, nomes=SINONIMOS):
    meta = COMPARTIMENTOS[comp]
    return {
        "MARCA": MARCA, "NAO_PARA_CLIENTE": True, "COMPARTIMENTO": comp,
        "NOME_IT": meta["NOME_IT"], "VISTAS_DO_CASCO": list(meta["VISTAS"]),
        "ESPECIES_ADMITIDAS": list(meta["ESPECIES"]),
        "CONTRATO_CHAVES": list(meta["CHAVES"]) if meta["CHAVES"] else NAO_SEI,
        "OBJETOS": [],
        "LACUNAS": [g for g in lacunas if nomes.get(g.get("FERRAMENTA"), g.get("FERRAMENTA")) == comp],
        "UNIVERSO": {"INTELLIGENCE_RUN_ID": run_id,
                     "LEITURA": "objetos NESTA corrida; zero aqui nao prova ausencia no mundo"},
    }


def adaptar(corrida: dict) -> dict:
    """O livro de uma corrida -> o pote v2, conferido antes de sair."""
    if not isinstance(corrida, dict):
        raise LeiViolada("uma corrida que nao e objeto nao se adapta")
    run_id = corrida.get("INTELLIGENCE_RUN_ID")
    if e_ignorancia(run_id):
        raise LeiViolada("corrida sem INTELLIGENCE_RUN_ID: um pote e de UMA corrida")
    estado = corrida.get("RESULT_STATE") or NAO_SEI
    linhagem = V1._linhagem_da_corrida(corrida)
    lacunas = V1._lacunas(corrida)
    sintetica = _sintetica(corrida)
    brutos = corrida.get("ITENS_POR_FERRAMENTA") or {}
    if not isinstance(brutos, dict):
        raise LeiViolada("ITENS_POR_FERRAMENTA tem de ser um objeto por compartimento")

    recusados = []
    for s in corrida.get("SIGNALS") or []:
        recusados.append(_recusa(NAO_SEI, s, "SINAL_SEM_FERRAMENTA",
                                 "a corrida nao disse para que ferramenta; o pote nao escolhe"))
    por_comp = {}
    for f, objs in brutos.items():
        objs = objs if isinstance(objs, list) else [objs]
        comp = SINONIMOS.get(f, f)
        if comp not in COMPARTIMENTOS:
            recusados += [_recusa(f, o, "COMPARTIMENTO_DESCONHECIDO") for o in objs]
            continue
        por_comp.setdefault(comp, []).extend(objs)

    saida = {}
    for comp, meta in COMPARTIMENTOS.items():
        entrada = _compartimento_base(comp, run_id, lacunas)
        objs = por_comp.get(comp) or []
        if meta["CHAVES"] is None:
            recusados += [_recusa(comp, o, SEM_CONTRATO) for o in objs]
        elif estado in CORRIDA_SEM_SAIDA or estado == NAO_SEI:
            recusados += [_recusa(comp, o, "CORRIDA_SEM_SAIDA_UTILIZAVEL", estado) for o in objs]
        else:
            vistos = set()
            for o in objs:
                falha = _conferir_objeto(comp, o, linhagem, vistos)
                if falha:
                    recusados.append(_recusa(comp, o, *falha))
                    continue
                vistos.add(_id_do_objeto(o))
                especie, de = _especie(o)
                entrada["OBJETOS"].append(_objeto(comp, o, especie, de, linhagem, run_id, sintetica))
        _vazio_ou_cheio(entrada, comp, estado)
        saida[comp] = entrada
    _fechar(saida, recusados)

    pote = _cabecalho(run_id, corrida, estado, "CORRIDA", sintetica)
    pote.update({
        "COMPARTIMENTOS": saida,
        "LACUNAS_SEM_COMPARTIMENTO": [g for g in lacunas
                                      if SINONIMOS.get(g.get("FERRAMENTA"), g.get("FERRAMENTA"))
                                      not in COMPARTIMENTOS],
        "RECUSADOS": recusados,
    })
    return _conferido(pote)


def pote_de_payload_v1(payload: dict) -> dict:
    """Um PAYLOAD PONTE_INTELLIGENCE_CASCO/v1 ja pronto -> o pote v2.

    A prova ja foi conferida pela ponte v1 contra a LINEAGE da corrida, e o
    payload nao traz a LINEAGE: por isso ele so atravessa se a conferencia da
    v1 o aprovar, e o pote diz que a prova foi conferida pela v1. O que a v1 nao
    levava (especie, URL, datas, SOURCE_HEAD, CORTE) fica NAO SEI — ou, para a
    especie, SINAL, que e o que o objeto da v1 e por contrato.
    """
    if not isinstance(payload, dict) or payload.get("SCHEMA") != V1.CONTRATO:
        raise LeiViolada(f"isto nao e um payload {V1.CONTRATO}")
    violacoes = V1.conferir_payload(payload)
    if violacoes:
        raise LeiViolada("o payload v1 reprova na conferencia da v1: " + "; ".join(violacoes))
    origem = payload.get("ORIGEM") or {}
    run_id = origem.get("INTELLIGENCE_RUN_ID")
    if e_ignorancia(run_id):
        raise LeiViolada("payload sem INTELLIGENCE_RUN_ID: um pote e de UMA corrida")
    estado = origem.get("RESULT_STATE") or NAO_SEI
    sintetica = _sintetica(origem)
    lacunas = []
    por_comp = {}
    for f, e in payload["FERRAMENTAS"].items():
        comp = DA_V1.get(f, f)
        lacunas += [dict(g, FERRAMENTA=f) for g in e.get("LACUNAS") or []]
        if comp in COMPARTIMENTOS and COMPARTIMENTOS[comp]["CHAVES"] is not None \
                and V1.FERRAMENTAS[f]["CHAVES"] is not None:
            por_comp.setdefault(comp, []).extend(e.get("CARTOES") or [])

    recusados = [dict(r, COMPARTIMENTO=DA_V1.get(r.get("FERRAMENTA"), r.get("FERRAMENTA")),
                      OBJETO_ID=r.get("SIGNAL_ID"), ORIGEM="PONTE_V1")
                 for r in payload.get("RECUSADOS") or []]
    saida = {}
    for comp, meta in COMPARTIMENTOS.items():
        entrada = _compartimento_base(comp, run_id, lacunas, DA_V1)
        vistos = set()
        for c in por_comp.get(comp) or []:
            sid = c.get("SIGNAL_ID")
            if sid in vistos:
                recusados.append({"COMPARTIMENTO": comp, "OBJETO_ID": sid,
                                  "MOTIVO": "DUPLICADO_NO_COMPARTIMENTO",
                                  "DETALHE": "o mesmo sinal vinha em duas vistas da v1"})
                continue
            vistos.add(sid)
            dadas = dict(c.get("CHAVES") or {})
            dadas = {k: v for k, v in dadas.items() if not e_ignorancia(v)}
            dadas.update(c.get("FORA_DO_CONTRATO") or {})
            o = {"SIGNAL_ID": sid, "CHAVES": dadas, "PROVA": c["PROVA"],
                 "PORQUE": c.get("PORQUE"), "CONTRADIZ": c.get("CONTRADIZ"),
                 "INCERTEZA": c.get("INCERTEZA")}
            obj = _objeto(comp, o, SINAL, "CONTRATO_V1", {}, run_id, sintetica)
            obj["PROVA_CONFERIDA_POR"] = V1.CONTRATO
            entrada["OBJETOS"].append(obj)
        if not entrada["OBJETOS"] and meta["CHAVES"] is not None and not any(
                V1.FERRAMENTAS.get(f, {}).get("CHAVES") for f in payload["FERRAMENTAS"]
                if DA_V1.get(f, f) == comp):
            entrada["ESTADO"] = "VAZIO"
            entrada.update(_porque(ENTRADA_V1_SEM_VAGA))
        else:
            _vazio_ou_cheio(entrada, comp, estado)
        saida[comp] = entrada
    _fechar(saida, recusados)

    pote = _cabecalho(run_id, origem, estado, "PAYLOAD_V1", sintetica)
    pote.update({
        "COMPARTIMENTOS": saida,
        "LACUNAS_SEM_COMPARTIMENTO": list(payload.get("LACUNAS_SEM_FERRAMENTA") or [])
        + [g for g in lacunas if DA_V1.get(g["FERRAMENTA"], g["FERRAMENTA"]) not in COMPARTIMENTOS],
        "RECUSADOS": recusados,
    })
    return _conferido(pote)


def _conferido(pote):
    violacoes = conferir_pote(pote)
    if violacoes:
        raise LeiViolada("pote reprovado na conferencia: " + "; ".join(violacoes))
    return pote


def conferir_pote(pote: dict) -> list:
    """O portao de saida. Lista de violacoes; vazia = passa.

    Independente de `adaptar`: le o pote como o casco o leria, e por isso serve
    para conferir um pote que chegou por outro caminho.
    """
    v = []
    if not isinstance(pote, dict):
        return ["pote nao e objeto"]
    if pote.get("SCHEMA") != CONTRATO:
        v.append(f"SCHEMA nao e {CONTRATO}")
    if pote.get("MARCA") != MARCA or pote.get("NAO_PARA_CLIENTE") is not True:
        v.append("pote sem a marca EXPERIMENTAL · NAO_PARA_CLIENTE")
    for k in ("INTELLIGENCE_RUN_ID", "SOURCE_HEAD", "CORTE"):
        if k not in pote or (e_ignorancia(pote.get(k)) and pote.get(k) != NAO_SEI):
            v.append(f"cabecalho sem {k} (ou NAO SEI escondido)")
    if e_ignorancia(pote.get("INTELLIGENCE_RUN_ID")):
        v.append("um pote e de UMA corrida: INTELLIGENCE_RUN_ID obrigatorio")
    comps = pote.get("COMPARTIMENTOS")
    if not isinstance(comps, dict) or set(comps) != set(COMPARTIMENTOS):
        return v + ["o pote nao traz os doze compartimentos"]
    for comp, e in comps.items():
        meta = COMPARTIMENTOS[comp]
        if e.get("MARCA") != MARCA or e.get("NAO_PARA_CLIENTE") is not True:
            v.append(f"{comp}: compartimento sem a marca")
        objs = e.get("OBJETOS") or []
        if not objs:
            if e.get("ESTADO") != "VAZIO" or e_ignorancia(e.get("PORQUE_VAZIO")) \
                    or e_ignorancia(e.get("PORQUE_TEXTO")):
                v.append(f"{comp}: vazio sem o PORQUE")
            continue
        if meta["CHAVES"] is None:
            v.append(f"{comp}: objeto num compartimento sem contrato de Intelligence")
            continue
        for o in objs:
            oid = o.get("OBJETO_ID", "?")
            if o.get("MARCA") != MARCA or o.get("NAO_PARA_CLIENTE") is not True:
                v.append(f"{comp}/{oid}: objeto sem a marca")
            if o.get("ESTADO") != ESTADO_TRANSPORTAVEL:
                v.append(f"{comp}/{oid}: estado {o.get('ESTADO')} nao e {ESTADO_TRANSPORTAVEL}")
            if o.get("ESPECIE") not in meta["ESPECIES"]:
                v.append(f"{comp}/{oid}: especie {o.get('ESPECIE')} nao cabe em {comp}")
            prova = o.get("PROVA")
            if not isinstance(prova, list) or not prova:
                v.append(f"{comp}/{oid}: objeto sem prova")
            else:
                for p in prova:
                    p = p or {}
                    falta = [k for k in CAMPOS_DA_PROVA + ("INTELLIGENCE_RUN_ID",) if e_ignorancia(p.get(k))]
                    if falta:
                        v.append(f"{comp}/{oid}: prova sem {', '.join(falta)}")
                    if str(p.get("INTELLIGENCE_RUN_ID")) != str(pote.get("INTELLIGENCE_RUN_ID")):
                        v.append(f"{comp}/{oid}: prova de outra corrida")
                    for k in CAMPOS_DA_PROVA_V2 + ("CORRIDA_UPSTREAM",):
                        if k not in p or (e_ignorancia(p.get(k)) and p.get(k) != NAO_SEI):
                            v.append(f"{comp}/{oid}: prova esconde {k}")
            chaves = o.get("CHAVES")
            if not isinstance(chaves, dict) or set(chaves) != set(meta["CHAVES"]):
                v.append(f"{comp}/{oid}: chaves nao batem com o contrato do compartimento")
            else:
                for k, val in chaves.items():
                    if e_ignorancia(val) and val != NAO_SEI:
                        v.append(f"{comp}/{oid}: {k} esconde a ignorancia ({val!r} em vez de NAO SEI)")
    return v


def como_js(pote: dict) -> str:
    """O pote na forma que o casco carrega: `window.SINTONIA_POTE`."""
    return ("/* GERADO por pacote/pote_intelligence_casco.py — " + MARCA + ".\n"
            "   " + CONTRATO + " · corrida " + str(pote["INTELLIGENCE_RUN_ID"]) + ".\n"
            "   FORA DO GIT E DO DEPLOY. Nao e para cliente. Nao editar a mao. */\n"
            "window." + NOME_DO_GLOBAL + " = "
            + json.dumps(pote, ensure_ascii=False, indent=1) + ";\n")


def destino_permitido(destino: Path) -> bool:
    """Fora do portal, qualquer sitio. Dentro, so `client/sintonia-pote.js`."""
    raiz = Path(os.path.dirname(HERE)).resolve()
    try:
        rel = destino.resolve().relative_to(raiz)
    except ValueError:
        return True
    if not (rel.parts and rel.parts[0] == "italia-portale"):
        return True
    return rel.parts == DESTINO_NO_CASCO


def ler_entrada(dado: dict) -> dict:
    """Corrida ou payload v1 -> pote. A escolha e pelo SCHEMA, nunca adivinhada."""
    if isinstance(dado, dict) and dado.get("SCHEMA") == V1.CONTRATO:
        return pote_de_payload_v1(dado)
    return adaptar(dado)


def main(argv=None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    if len(argv) != 2:
        print(__doc__.strip().split("\n\n")[0])
        print("\n  uso: python3 pacote/pote_intelligence_casco.py <corrida.json|payload-v1.json> "
              "<saida.json|italia-portale/client/sintonia-pote.js>")
        return 2
    dado = json.loads(Path(argv[0]).read_text(encoding="utf-8"))
    destino = Path(argv[1])
    if not destino_permitido(destino):
        print("RECUSADO: dentro de italia-portale/ o pote so pode ir para client/sintonia-pote.js "
              "(fora do Git e do deploy).")
        return 3
    pote = ler_entrada(dado)
    texto = como_js(pote) if destino.suffix == ".js" else json.dumps(pote, ensure_ascii=False, indent=1) + "\n"
    destino.write_text(texto, encoding="utf-8")
    n = sum(len(e["OBJETOS"]) for e in pote["COMPARTIMENTOS"].values())
    vazios = sum(1 for e in pote["COMPARTIMENTOS"].values() if not e["OBJETOS"])
    print(f"{MARCA} · {CONTRATO} · corrida {pote['INTELLIGENCE_RUN_ID']} · {n} objetos · "
          f"{vazios} compartimentos vazios com o porque · {len(pote['RECUSADOS'])} recusados -> {destino}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
