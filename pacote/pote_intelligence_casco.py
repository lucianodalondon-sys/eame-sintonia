#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""O POTE UNICO — uma corrida da Intelligence, um compartimento por ferramenta.

    MISSAO   POTE-UNICO (decisoes D95/D96 do dono, resumidas no pedido da missao;
             D95/D96 nao estao escritas no repositorio, e por isso a fonte fica
             dita aqui)
    ESPECIE  ADAPTADOR DE ENTREGA (Z-PACOTE). NAO E MOTOR. NAO E TELA.
    CONTRATO POTE_INTELLIGENCE_CASCO/v2

    python3 pacote/pote_intelligence_casco.py <entrada.json> <saida.json|sintonia-pote.js>
    python3 pacote/pote_intelligence_casco.py <entrada.json> <saida> --v21 [--anterior POTE-PUBLICADO.json]
                                              # D125: um cartao por pergunta + DELTA contra o publicado
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
import re
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
# D125 · POTES-UM-CARTAO: a identidade, o fecho e o DELTA sao da INTELLIGENCE (INT-LAW-215). O pote
# chama o codigo dela e transporta; nao ha aqui uma segunda regra de identidade.
import identidade_do_cruzamento as IDENT              # noqa: E402  (motor/)

CONTRATO = "POTE_INTELLIGENCE_CASCO/v2"
#: D125 · a v2.1: um CARTAO por pergunta em CARTOES, e cada compartimento guarda SO os IDS.
CONTRATO_V21 = "POTE_INTELLIGENCE_CASCO/v2.1"
#: Campos de identidade que a Intelligence escreve no objeto e o pote TRANSPORTA como vieram.
CAMPOS_DE_IDENTIDADE = ("CROSSING_KEY", "FAMILIA", "ALIAS", "ID_PROVISORIO", "LINKS", "CONTAGENS", "RESPOSTA",
                        "RESPOSTA_DITA_POR", "RESPOSTA_DO_ROTULO", "FUSAO_DIVERGENTE", "ESTADOS_DOS_LINKS",
                        "GRUPO", "REFERENCIAS", "REGRA_DE_IDENTIDADE", "VOCABULARIO", "RELACAO",
                        "HISTORICO_DE_ESTADO")
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
#: POTE-V2-UNICO: a publicacao chama-se PUBLISHED_AT no contrato (o nome que a
#: missao escreveu); PUBLICADO_EM e PUBLICATION_TIME so se LEEM na entrada.
CAMPOS_DA_PROVA_V2 = ("URL", "PUBLISHED_AT", "COLHIDO_EM", "FACT_TIME")
#: URL e PUBLISHED_AT levam sempre a BASE: de onde veio o valor, ou — quando o
#: valor e NAO SEI — porque nao ha valor. NAO SEI sem base e um buraco, nao uma
#: resposta.
CAMPOS_COM_BASE = ("URL", "PUBLISHED_AT")
#: Nomes que a ENTRADA pode usar para o mesmo campo (leitura, nunca escrita).
LER_NA_ENTRADA = {"URL": ("URL", "SOURCE_URL"),
                  "PUBLISHED_AT": ("PUBLISHED_AT", "PUBLICADO_EM", "PUBLICATION_TIME"),
                  "COLHIDO_EM": ("COLHIDO_EM",), "FACT_TIME": ("FACT_TIME",)}

# ── P7 · O QUE EXIGE TEMPO, E O QUE NAO ──────────────────────────────────────
#: Um resultado honesto nao afirma nada no tempo: diz que nao, ou que ainda nao
#: ha acao defensavel. Por isso nao depende de FACT_TIME. Lido (normalizado) de
#: RESULTADO ou de CHAVES.RESULTADO / CHAVES.CROSSING_STATE.
RESULTADOS_HONESTOS = ("NAO", "NAO_TRATAR_AGORA", "NO_DEFENSIBLE_ACTION_YET")
#: Especies que podem trazer um resultado honesto. OPORTUNIDADE e o facto
#: futuro afirmam por natureza, e nunca sao «nao».
_PODEM_SER_HONESTAS = (SINAL, CROSSING, FINDING)
#: Como uma prova foi admitida. So USO_SEM_TEMPO admite um item que G0 bloqueou
#: pelo tempo — e so para um uso que nao exige tempo.
ADMITIDA = ("G0_PASSOU", "FUTURO_POR_DESENHO", "USO_SEM_TEMPO", "PONTE_V1")

# ── D112 · DE ONDE VEM A ENTIDADE E O LUGAR ──────────────────────────────────
#: D112 nao esta escrita no repositorio: segue o resumo no pedido da missao
#: POTE-V2-UNICO. Quando a Intelligence os diz, viajam com o objeto, com o nome
#: deles, e nunca como chave da vista.
CAMPOS_DE_ORIGEM = ("ENTITY_SOURCE", "LOCATION_SOURCE")
#: O lugar da FONTE (sede, editora, dominio) nao e o lugar do FACTO (AGENTS.md:
#: «fonte/location do documento nao vira local do fato»; INT-LAW-101).
LOCATION_SOURCE_PROIBIDA = ("SOURCE_LOCATION", "DOCUMENT_LOCATION", "PUBLISHER_LOCATION",
                            "LOCAL_DA_FONTE", "LOCAL_DO_DOCUMENTO", "SEDE_DA_FONTE")

# ── P8 · O POLSO SO LE MUDANCA NUMA SERIE ────────────────────────────────────
#: Um preco solto e um ponto. Mudanca de mercado so se le numa SERIE medida:
#: pelo menos dois pontos, cada um com periodo, preco e unidade, todos na MESMA
#: unidade e em periodos diferentes. O pote CONFERE a serie; nao calcula a
#: variacao (INT-LAW-023: quem calcula e a Intelligence).
SERIE_MEDIDA = "SERIE_MEDIDA"
SINAL_SOLTO = "SINAL_SOLTO"
CAMPOS_DO_PONTO = ("PERIOD", "PRICE", "UNIT")
#: Campos do objeto que o pote le com significado proprio, e por isso nunca
#: caem em FORA_DO_CONTRATO como se fossem uma chave qualquer.
_CAMPOS_LIDOS = CAMPOS_DE_ORIGEM + ("SERIE", "MUDANCA_DE_MERCADO", "RESULTADO")


def normal(v) -> str:
    """'não tratar agora' -> 'NAO_TRATAR_AGORA'. So para comparar vocabulario."""
    import unicodedata
    s = unicodedata.normalize("NFKD", str(v)).encode("ascii", "ignore").decode("ascii")
    return "_".join(s.upper().replace("-", " ").split())


def _dadas(o: dict) -> dict:
    return o.get("CHAVES") if isinstance(o.get("CHAVES"), dict) else {}


def _lido(o: dict, campo):
    """O campo com significado proprio: no objeto, ou (so se la nao estiver) em CHAVES."""
    v = o.get(campo)
    return _dadas(o).get(campo) if v is None else v


def resultado_honesto(o: dict):
    """O resultado honesto que o objeto traz, normalizado — ou None."""
    for v in (o.get("RESULTADO"), _dadas(o).get("RESULTADO"), _dadas(o).get("CROSSING_STATE")):
        if not e_ignorancia(v) and normal(v) in RESULTADOS_HONESTOS:
            return normal(v)
    return None


def uso_exige_tempo(especie, o: dict) -> bool:
    """P7. So um uso que afirma alguma coisa NO TEMPO depende de FACT_TIME.

    Nao dependem: o rendimento de uma fonte (Registro delle fonti: quantos itens
    leu, quantos passaram) e um resultado honesto «nao» / «nao tratar agora» /
    NO_DEFENSIBLE_ACTION_YET. Tudo o resto — sinal, oportunidade, janela,
    crossing afirmativo — exige tempo ancorado.
    """
    if especie == RENDIMENTO:
        return False
    if especie in _PODEM_SER_HONESTAS and resultado_honesto(o):
        return False
    return True


def so_tempo(falta) -> bool:
    """Os motivos de G0 sao TODOS do tempo do facto (e ha pelo menos um)."""
    falta = [str(f) for f in (falta or [])]
    return bool(falta) and all(f == "FACT_TIME" or f.startswith("FACT_TIME:") for f in falta)


def ler_serie(o: dict):
    """P8. `(leitura, porque, pontos, unidade)` de um objeto do Polso."""
    serie = _lido(o, "SERIE")
    if not isinstance(serie, list) or not serie:
        return SINAL_SOLTO, "um ponto so: sem SERIE nao ha mudanca de mercado", [], NAO_SEI
    pontos = [p for p in serie if isinstance(p, dict)]
    if len(pontos) != len(serie) or len(pontos) < 2:
        return SINAL_SOLTO, f"SERIE com {len(pontos)} ponto(s) medido(s): mudanca exige pelo menos 2", pontos, NAO_SEI
    for p in pontos:
        falta = [c for c in CAMPOS_DO_PONTO if e_ignorancia(p.get(c))]
        if falta:
            return SINAL_SOLTO, f"ponto da SERIE sem {', '.join(falta)}: nao e medido", pontos, NAO_SEI
    unidades = sorted({str(p["UNIT"]) for p in pontos})
    if len(unidades) != 1:
        return SINAL_SOLTO, f"SERIE com unidades diferentes ({' | '.join(unidades)}): nao se comparam", pontos, NAO_SEI
    if len({str(p["PERIOD"]) for p in pontos}) != len(pontos):
        return SINAL_SOLTO, "SERIE com o mesmo periodo repetido: nao e serie no tempo", pontos, NAO_SEI
    return SERIE_MEDIDA, f"{len(pontos)} pontos medidos na mesma unidade", pontos, unidades[0]


def _afirma_mudanca(o: dict) -> bool:
    v = _lido(o, "MUDANCA_DE_MERCADO")
    return v is True or (isinstance(v, str) and not e_ignorancia(v) and normal(v) in ("SIM", "YES", "TRUE"))


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


def _admite_para(especie, o=None):
    """Que entrada da LINEAGE prova um objeto desta especie, NESTE uso."""
    if especie == FUTURO:
        def admite(e):
            # P2/P5 · o facto sobre o futuro prova-se por uma entrada que passou G0
            # ou que G0 bloqueou SO porque a data do facto e depois da captura.
            if e.get("G0") == "PASSOU":
                return True
            return e.get("G0") == "BLOQUEADO_EM_G0" and list(e.get("G0_FALTA") or []) == [G0_FUTURO_POR_DESENHO]
        return admite
    if not uso_exige_tempo(especie, o or {}):
        def admite(e):
            # P7 · um uso que nao exige tempo prova-se por uma entrada cuja
            # PROVENIENCIA esta inteira (ITEM_ID, SOURCE_ID, RAW) — o tempo do
            # facto pode faltar, porque este uso nao o usa. Faltar a fonte ou o
            # RAW continua a bloquear.
            if e.get("G0") == "PASSOU":
                return True
            return e.get("G0") == "BLOQUEADO_EM_G0" and so_tempo(e.get("G0_FALTA"))
        return admite
    return V1.g0_passou


def _da_entrada(p: dict, campo):
    for nome in LER_NA_ENTRADA[campo]:
        if not e_ignorancia(p.get(nome)):
            return p.get(nome), nome
    return None, None


def _prova_v2(p: dict, linhagem: dict, run_id, especie=None) -> dict:
    """O elemento de prova como viaja: os campos da v1, os da v2, e a corrida.

    URL e datas vem da propria prova; se a prova nao os disser, da entrada da
    LINEAGE que a confirmou — so quando essa entrada e unica e os diz. Nunca de
    outro campo: a publicacao nao vira FACT_TIME, e vice-versa. URL e
    PUBLISHED_AT levam a BASE (de onde veio, ou porque e NAO SEI).
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
        v, nome = _da_entrada(p, c)
        base = f"PROVA.{nome}" if nome else None
        if v is None and len(batem) == 1:
            v, nome = _da_entrada(batem[0], c)
            base = f"LINEAGE.{nome}" if nome else None
        out[c] = _valor(v)
        if c in CAMPOS_COM_BASE:
            dita = p.get(c + "_BASE")
            out[c + "_BASE"] = base or (dita if not e_ignorancia(dita) else
                                        f"NAO_VEIO: nem a prova nem a entrada unica da LINEAGE trazem {c}")
    # De onde veio, e como foi admitida: a Sala aparece so aqui, como prova.
    g0 = sorted({str(e.get("G0")) for e in batem})
    out["G0"] = "|".join(g0) if g0 else NAO_SEI
    if g0 == ["PASSOU"]:
        out["ADMITIDA_POR"] = "G0_PASSOU"
    elif not g0:
        out["ADMITIDA_POR"] = NAO_SEI
    elif especie == FUTURO:
        out["ADMITIDA_POR"] = "FUTURO_POR_DESENHO"
    else:
        out["ADMITIDA_POR"] = "USO_SEM_TEMPO"
    out["INTELLIGENCE_RUN_ID"] = run_id
    return out


def _objeto(comp: str, o: dict, especie, especie_de, linhagem, run_id, sintetica) -> dict:
    """RENDER + EXPLAIN. Os valores sao os do objeto, ou NAO SEI."""
    contrato = COMPARTIMENTOS[comp]["CHAVES"]
    dadas = _dadas(o)
    chaves = {k: _valor(dadas.get(k)) for k in contrato}
    out = {
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
        "FORA_DO_CONTRATO": {k: _valor(dadas[k]) for k in sorted(dadas)
                             if k not in contrato and k not in _CAMPOS_LIDOS},
        "PORQUE": _valor(o.get("PORQUE")),
        "CONTRADIZ": _valor(o.get("CONTRADIZ")),
        "INCERTEZA": _valor(o.get("INCERTEZA")),
        # P7 · o uso diz se o tempo e preciso; o resultado honesto viaja dito.
        "RESULTADO": resultado_honesto(o) or NAO_SEI,
        "USO_EXIGE_TEMPO": uso_exige_tempo(especie, o),
        "PROVA": [_prova_v2(p, linhagem, run_id, especie) for p in o["PROVA"]],
        "CORRIDA_SINTETICA": sintetica,
    }
    # D112 · a origem da entidade e do lugar, quando a Intelligence as diz. Se
    # ha lugar do facto e ninguem disse de onde ele veio, isso fica a vista.
    for c in CAMPOS_DE_ORIGEM:
        v = _lido(o, c)
        if v is not None:
            out[c] = _valor(v)
    # D125 · a identidade da pergunta viaja como a Intelligence a escreveu (o pote nao a calcula).
    for c in CAMPOS_DE_IDENTIDADE:
        if c in o:
            out[c] = o[c]
    lugar = dadas.get("FACT_LOCATION")
    if not e_ignorancia(lugar) and "LOCATION_SOURCE" not in out:
        out["LOCATION_SOURCE"] = NAO_SEI
    # P8 · no Polso, cada objeto diz se e serie medida ou sinal solto.
    if comp == "market":
        leitura, porque, pontos, unidade = ler_serie(o)
        out["MERCADO"] = {"LEITURA": leitura, "PORQUE": porque, "PONTOS": len(pontos),
                          "UNIDADE": unidade, "SERIE": pontos if leitura == SERIE_MEDIDA else []}
    return out


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
    falha = V1.conferir_prova(o, linhagem, admite=_admite_para(especie, o))
    if falha:
        return falha
    # P8 · afirmar mudanca de mercado sem SERIE medida e promover um ponto.
    if _afirma_mudanca(o) and ler_serie(o)[0] != SERIE_MEDIDA:
        return ("SINAL_SOLTO_NAO_E_MUDANCA_DE_MERCADO",
                f"afirma MUDANCA_DE_MERCADO sem serie medida: {ler_serie(o)[1]}")
    # D112 · o lugar da fonte nao e o lugar do facto.
    ls = _lido(o, "LOCATION_SOURCE")
    if not e_ignorancia(ls) and normal(ls) in LOCATION_SOURCE_PROIBIDA:
        return ("LUGAR_DA_FONTE_NAO_E_LUGAR_DO_FACTO",
                f"LOCATION_SOURCE = {ls}: o lugar do documento nao vira o lugar do facto")
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


#: Campos do topo que uma entrada antiga (o formato R5 do bot da Intelligence)
#: trazia dentro de CABECALHO. Lidos de la SO se o topo nao os tiver, e a
#: leitura fica escrita no pote (LEITURA_DE_COMPATIBILIDADE). O pote que sai
#: tem-nos SEMPRE no topo: o contrato e um so.
LIDOS_DO_CABECALHO = ("INTELLIGENCE_RUN_ID", "SOURCE_HEAD", "CORTE", "RESULT_STATE")


def ler_topo(corrida: dict):
    """`(topo, leituras)`: os campos do topo, com a compatibilidade DECLARADA.

    Se o topo e o CABECALHO disserem coisas diferentes, sao duas corridas num
    ficheiro so — e isso nao se adapta.
    """
    cab = corrida.get("CABECALHO") if isinstance(corrida.get("CABECALHO"), dict) else {}
    topo, leituras = {}, []
    for c in LIDOS_DO_CABECALHO:
        v, w = corrida.get(c), cab.get(c)
        if not e_ignorancia(v) and not e_ignorancia(w) and v != w:
            raise LeiViolada(f"{c} no topo ({v}) e em CABECALHO ({w}) divergem: um pote e de UMA corrida")
        if e_ignorancia(v) and not e_ignorancia(w):
            v = w
            leituras.append(f"{c} lido de CABECALHO (formato antigo R5 do bot da Intelligence): "
                            "leitura de compatibilidade declarada; no pote ele vai no topo")
        topo[c] = v
    return topo, leituras


def _cabecalho(run_id, fonte, estado, origem, sintetica, leituras=()) -> dict:
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
        "LEITURA_DE_COMPATIBILIDADE": list(leituras),
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
    if "COMPARTIMENTOS" in corrida and "ITENS_POR_FERRAMENTA" not in corrida:
        raise LeiViolada("isto ja e um pote (de outro formato), nao o livro de uma corrida: "
                         "regenere-o a partir da saida do motor (ENTRADA-DA-PONTE / livro da corrida)")
    topo, leituras = ler_topo(corrida)
    run_id = topo["INTELLIGENCE_RUN_ID"]
    if e_ignorancia(run_id):
        raise LeiViolada("corrida sem INTELLIGENCE_RUN_ID: um pote e de UMA corrida")
    estado = topo["RESULT_STATE"] or NAO_SEI
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

    pote = _cabecalho(run_id, dict(corrida, **topo), estado, "CORRIDA", sintetica, leituras)
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
            for pr in obj["PROVA"]:
                pr["ADMITIDA_POR"] = "PONTE_V1"
                for c in CAMPOS_COM_BASE:
                    if pr[c] == NAO_SEI:
                        pr[c + "_BASE"] = f"PAYLOAD_V1: o contrato {V1.CONTRATO} nao transportava {c}"
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
    if pote.get("SCHEMA") == CONTRATO_V21:
        return conferir_pote_v21(pote)
    if pote.get("SCHEMA") != CONTRATO:
        v.append(f"SCHEMA nao e {CONTRATO}")
    if pote.get("MARCA") != MARCA or pote.get("NAO_PARA_CLIENTE") is not True:
        v.append("pote sem a marca EXPERIMENTAL · NAO_PARA_CLIENTE")
    for k in ("INTELLIGENCE_RUN_ID", "SOURCE_HEAD", "CORTE"):
        if k not in pote or (e_ignorancia(pote.get(k)) and pote.get(k) != NAO_SEI):
            v.append(f"cabecalho sem {k} (ou NAO SEI escondido)")
    if e_ignorancia(pote.get("INTELLIGENCE_RUN_ID")):
        v.append("um pote e de UMA corrida: INTELLIGENCE_RUN_ID obrigatorio NO TOPO"
                 + (" (esta so em CABECALHO: a compatibilidade e so de leitura da ENTRADA)"
                    if isinstance(pote.get("CABECALHO"), dict) else ""))
    if not isinstance(pote.get("LEITURA_DE_COMPATIBILIDADE"), list):
        v.append("cabecalho sem LEITURA_DE_COMPATIBILIDADE (lista; vazia = nenhuma)")
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
                    for k in CAMPOS_COM_BASE:
                        if p.get(k) == NAO_SEI and e_ignorancia(p.get(k + "_BASE")):
                            v.append(f"{comp}/{oid}: prova com {k} NAO SEI sem a base (porque nao ha {k})")
                    adm = p.get("ADMITIDA_POR")
                    if adm not in ADMITIDA:
                        v.append(f"{comp}/{oid}: prova sem ADMITIDA_POR valido ({adm!r})")
                    elif adm == "USO_SEM_TEMPO" and uso_exige_tempo(o.get("ESPECIE"), o):
                        v.append(f"{comp}/{oid}: item sem tempo ancorado prova um uso que EXIGE tempo")
                    elif adm == "FUTURO_POR_DESENHO" and o.get("ESPECIE") != FUTURO:
                        v.append(f"{comp}/{oid}: bloqueio por futuro prova o que nao e facto futuro")
                    elif adm == "PONTE_V1" and pote.get("ENTRADA") != "PAYLOAD_V1":
                        v.append(f"{comp}/{oid}: prova dita conferida pela v1 num pote que nao veio da v1")
            if o.get("ESPECIE_DITA_POR") not in ("INTELLIGENCE", "CONTRATO_V1"):
                v.append(f"{comp}/{oid}: ESPECIE sem quem a disse")
            if not isinstance(o.get("USO_EXIGE_TEMPO"), bool):
                v.append(f"{comp}/{oid}: sem USO_EXIGE_TEMPO")
            elif o["USO_EXIGE_TEMPO"] != uso_exige_tempo(o.get("ESPECIE"), o):
                v.append(f"{comp}/{oid}: USO_EXIGE_TEMPO nao bate com a especie e o RESULTADO")
            ls = o.get("LOCATION_SOURCE")
            if not e_ignorancia(ls) and normal(ls) in LOCATION_SOURCE_PROIBIDA:
                v.append(f"{comp}/{oid}: LOCATION_SOURCE = {ls} (o lugar da fonte nao e o lugar do facto)")
            for c in CAMPOS_DE_ORIGEM:
                if c in o and e_ignorancia(o[c]) and o[c] != NAO_SEI:
                    v.append(f"{comp}/{oid}: {c} esconde a ignorancia")
            lugar = (o.get("CHAVES") or {}).get("FACT_LOCATION") if isinstance(o.get("CHAVES"), dict) else None
            if e_ignorancia(lugar):
                lugar = (o.get("FORA_DO_CONTRATO") or {}).get("FACT_LOCATION")
            if not e_ignorancia(lugar) and "LOCATION_SOURCE" not in o:
                v.append(f"{comp}/{oid}: lugar do facto sem LOCATION_SOURCE (nem NAO SEI)")
            if "MUDANCA_DE_MERCADO" in o or "MUDANCA_DE_MERCADO" in (o.get("FORA_DO_CONTRATO") or {}):
                v.append(f"{comp}/{oid}: MUDANCA_DE_MERCADO nao e campo do pote (so MERCADO.LEITURA)")
            if comp == "market":
                m = o.get("MERCADO")
                if not isinstance(m, dict) or m.get("LEITURA") not in (SERIE_MEDIDA, SINAL_SOLTO):
                    v.append(f"{comp}/{oid}: objeto do Polso sem MERCADO.LEITURA")
                elif m["LEITURA"] == SERIE_MEDIDA and ler_serie({"SERIE": m.get("SERIE")})[0] != SERIE_MEDIDA:
                    v.append(f"{comp}/{oid}: sinal solto apresentado como SERIE_MEDIDA (mudanca de mercado)")
            elif "MERCADO" in o:
                v.append(f"{comp}/{oid}: leitura de mercado fora do Polso")
            chaves = o.get("CHAVES")
            if not isinstance(chaves, dict) or set(chaves) != set(meta["CHAVES"]):
                v.append(f"{comp}/{oid}: chaves nao batem com o contrato do compartimento")
            else:
                for k, val in chaves.items():
                    if e_ignorancia(val) and val != NAO_SEI:
                        v.append(f"{comp}/{oid}: {k} esconde a ignorancia ({val!r} em vez de NAO SEI)")
    return v


# ═════════════════════════════════════════════════════════════════════════════
# D125 · POTE_INTELLIGENCE_CASCO/v2.1 — UM CARTAO POR PERGUNTA (POTES-UM-CARTAO)
# ═════════════════════════════════════════════════════════════════════════════
#
#   CARTOES        { ID: cartao }      o UNICO sitio onde um cartao existe. Nenhum compartimento guarda
#                                      copia: cada um guarda so os IDS (D125.4). O Arquivo deixa de repetir.
#   COMPARTIMENTOS { comp: {..., IDS} } o mesmo cartao pode estar em VARIOS (D125.1); muda uma vez e
#                                      todos mudam juntos, porque e o MESMO cartao (D125.2).
#   ANTERIOR       {INTELLIGENCE_RUN_ID, POTE_SHA256} do pote anterior PUBLICADO | "NENHUM" (opcao A)
#   DELTA          por cartao: NOVO | FORTALECEU | MUDOU_ESTADO | ENFRAQUECEU | SEM_REVISAO, com CAUSA e
#                  GATILHO. SAIU so com causa (SAIRAM); ausencia sem causa e SEM_REVISAO (NAO_REVISTOS).
#   REFERENCIAS    [{CROSSING_ID, AVALIACAO_ID, PAPEL}] — Finding/Oportunidade/Futuro/Agenda/Concorrencia/
#                  Vozes/Label apontam o cartao de que dependem; so para baixo (DAG).
#   FECHO          a prova conta 1 vez: evidencias do cartao e dos que ele referencia, por documento e
#                  por originador — nunca a soma dos filhos.
#
# Quem calcula identidade, fecho e DELTA e motor/identidade_do_cruzamento.py (a Intelligence). Aqui so se
# junta o que tem o MESMO ID, se transporta e se confere.

_POR_COMP_SO = ("COMPARTIMENTO", "CHAVES_NAO_SEI", "MERCADO")


def _mesma_prova(a, b) -> bool:
    k = lambda o: sorted(json.dumps(p, sort_keys=True, ensure_ascii=False) for p in o.get("PROVA") or [])  # noqa: E731
    return k(a) == k(b)


def _juntar(membros: list) -> dict:
    """Os objetos do MESMO ID (em um ou mais compartimentos) -> um cartao."""
    base = membros[0]
    if len({m.get("ESPECIE") for m in membros}) != 1:
        raise LeiViolada("o ID %s chega com especies diferentes: um cartao tem UMA especie" % base["OBJETO_ID"])
    consolidado = False
    if all(_mesma_prova(base, m) for m in membros[1:]):
        c = dict(base)
    elif any("LINKS" in m for m in membros):
        raise LeiViolada("o ID %s chega duas vezes com provas diferentes e ja consolidado pela Intelligence: "
                         "o pote nao escolhe um" % base["OBJETO_ID"])
    else:
        # esquema anterior: varios links da MESMA pergunta (ex.: 13 PM de OLIVO x mosca) — quem junta e a
        # Intelligence (IDENT.consolidar), com o estado de cada link no link.
        c = IDENT.consolidar(membros)[0]
        consolidado = True
    chaves, fora = {}, {}
    for m in membros:
        for k, v in (m.get("CHAVES") or {}).items():
            if k not in chaves or (chaves[k] == NAO_SEI and v != NAO_SEI):
                chaves[k] = v
        fora.update(m.get("FORA_DO_CONTRATO") or {})
    if consolidado:
        chaves = c["CHAVES"]      # a juncao da Intelligence: valores diferentes ficam todos, a vista
    c["CHAVES"] = chaves
    c["FORA_DO_CONTRATO"] = {k: v for k, v in fora.items() if k not in chaves}
    for k in _POR_COMP_SO:
        c.pop(k, None)
    merc = next((m.get("MERCADO") for m in membros if m.get("COMPARTIMENTO") == "market"), None)
    if merc is not None:
        c["MERCADO"] = merc
    c["COMPARTIMENTOS"] = sorted({m["COMPARTIMENTO"] for m in membros}, key=list(COMPARTIMENTOS).index)
    return c


def v21_do_v2(pote: dict, anterior: dict | None = None, anterior_sha256: str | None = None,
              causas_de_saida: dict | None = None, conferir: bool = True) -> dict:
    """Um pote v2 (ja conferido) -> o pote v2.1. `anterior` = o pote anterior PUBLICADO (v2 ou v2.1) e o
    sha256 dos BYTES dele — o DELTA e contra ele (opcao A). `conferir=False` so para MEDIR um pote antigo
    que a lei de hoje ja nao aprova (fica dito em ENTRADA)."""
    if pote.get("SCHEMA") != CONTRATO:
        raise LeiViolada("v21_do_v2 recebe um pote %s" % CONTRATO)
    if anterior is not None and (e_ignorancia(anterior_sha256) or not re.fullmatch(r"[0-9a-f]{64}", str(anterior_sha256))):
        raise LeiViolada("ANTERIOR sem o SHA256 dos bytes do pote publicado: o DELTA nao tem base")
    run = pote["INTELLIGENCE_RUN_ID"]
    grupos, ordem, ids_por_comp = {}, [], {}
    for comp, e in pote["COMPARTIMENTOS"].items():
        ids_por_comp[comp] = []
        for o in e.get("OBJETOS") or []:
            o = dict(o)
            ident = IDENT.identificar(o)
            if ident["OBJETO_ID"] != o["OBJETO_ID"] or ident.get("CROSSING_KEY"):
                o.update(ident)
            oid = o["OBJETO_ID"]
            if oid not in grupos:
                grupos[oid] = []
                ordem.append(oid)
            grupos[oid].append(o)
            if oid not in ids_por_comp[comp]:
                ids_por_comp[comp].append(oid)
    cartoes = {oid: _juntar(grupos[oid]) for oid in ordem}
    alias = {a: oid for oid, c in cartoes.items() for a in c.get("ALIAS") or []}
    for oid, c in cartoes.items():
        c["AVALIACAO_ID"] = IDENT.avaliacao_id(oid, run)
        c.setdefault("ALIAS", [])
        c.setdefault("ID_PROVISORIO", True)
        c.setdefault("REGRA_DE_IDENTIDADE", IDENT.REGRA)
        c.setdefault("VOCABULARIO", IDENT.VOCAB.carimbo())
        c.setdefault("CONTAGENS", IDENT.contar_provas(c.get("PROVA")))
        if not c.get("GRUPO") and IDENT.grupo(c.get("CROSSING_KEY"), c.get("PROVA")):
            c["GRUPO"] = IDENT.grupo(c.get("CROSSING_KEY"), c.get("PROVA"))
    for c in cartoes.values():
        refs = []
        for r in c.get("REFERENCIAS") or []:
            alvo = alias.get(r.get("CROSSING_ID"), r.get("CROSSING_ID"))
            refs.append({"CROSSING_ID": alvo, "PAPEL": r.get("PAPEL"),
                         "AVALIACAO_ID": (cartoes.get(alvo) or {}).get("AVALIACAO_ID", NAO_SEI)})
        if "REFERENCIAS" in c:
            c["REFERENCIAS"] = refs
    ant = IDENT.ler_anterior(anterior, anterior_sha256) if anterior is not None else None
    info = IDENT.delta(cartoes, ant, causas_de_saida, corrida_parcial=pote.get("RESULT_STATE") != "DONE")
    comps = {}
    for comp, e in pote["COMPARTIMENTOS"].items():
        e = {k: v for k, v in e.items() if k != "OBJETOS"}
        e["IDS"] = ids_por_comp[comp]
        e["UNIVERSO"] = dict(e["UNIVERSO"], OBJETOS=len(e["IDS"]),
                             LEITURA="IDS de cartoes desta corrida (o cartao vive em CARTOES, uma vez); zero aqui "
                                     "nao prova ausencia no mundo")
        comps[comp] = e
    out = {k: v for k, v in pote.items() if k != "COMPARTIMENTOS"}
    out.update({
        "SCHEMA": CONTRATO_V21, "ENTRADA": pote.get("ENTRADA") if conferir else "POTE_V2_SO_MEDICAO",
        "REGRA_DE_IDENTIDADE": IDENT.REGRA, "VOCABULARIO": IDENT.VOCAB.carimbo(),
        "ANTERIOR": info["ANTERIOR"], "DELTA_CONTAGEM": info["DELTA_CONTAGEM"],
        "SAIRAM": info["SAIRAM"], "NAO_REVISTOS": info["NAO_REVISTOS"],
        "CONTAGEM_DE_CARTOES": {"LUGARES_NOS_COMPARTIMENTOS": sum(len(x) for x in ids_por_comp.values()),
                                "CARTOES_DISTINTOS": len(cartoes)},
        "LEI": pote.get("LEI", "") + " · D125: um cartao por pergunta; o compartimento guarda o ID, nunca a copia; "
               "o casco mostra DELTA/GRUPO, nao os calcula (INT-LAW-215)",
        "COMPARTIMENTOS": comps, "CARTOES": cartoes,
    })
    return _conferido(out) if conferir else out


def adaptar_v21(corrida: dict, anterior: dict | None = None, anterior_sha256: str | None = None,
                causas_de_saida: dict | None = None) -> dict:
    """O livro de uma corrida -> o pote v2.1 (passa pela lei v2 inteira antes, compartimento a compartimento)."""
    return v21_do_v2(adaptar(corrida), anterior, anterior_sha256, causas_de_saida)


def materializar(pote: dict) -> dict:
    """A vista v2 de um pote v2.1: cada compartimento com o cartao RESOLVIDO pelo ID (e as CHAVES do
    contrato dele). Serve a lei v2 (e ao casco); nao e um pote que se guarde — seria a copia proibida."""
    v2 = {k: v for k, v in pote.items() if k not in ("CARTOES",)}
    v2["SCHEMA"] = CONTRATO
    cartoes = pote.get("CARTOES") or {}
    comps = {}
    for comp, e in (pote.get("COMPARTIMENTOS") or {}).items():
        e2 = {k: v for k, v in e.items() if k != "IDS"}
        objs = []
        contrato = (COMPARTIMENTOS.get(comp) or {}).get("CHAVES") or ()
        for oid in e.get("IDS") or []:
            c = cartoes.get(oid)
            if not isinstance(c, dict):
                continue
            o = {k: v for k, v in c.items() if k not in ("COMPARTIMENTOS", "MERCADO")}
            o["COMPARTIMENTO"] = comp
            dadas = c.get("CHAVES") or {}
            o["CHAVES"] = {k: dadas.get(k, NAO_SEI) for k in contrato}
            o["CHAVES_NAO_SEI"] = [k for k in contrato if o["CHAVES"][k] == NAO_SEI]
            o["FORA_DO_CONTRATO"] = dict(c.get("FORA_DO_CONTRATO") or {},
                                         **{k: v for k, v in dadas.items() if k not in contrato})
            if comp == "market" and "MERCADO" in c:
                o["MERCADO"] = c["MERCADO"]
            objs.append(o)
        e2["OBJETOS"] = objs
        comps[comp] = e2
    v2["COMPARTIMENTOS"] = comps
    return v2


def conferir_pote_v21(pote: dict) -> list:
    """O portao de saida da v2.1: a lei v2 inteira sobre a vista materializada + a lei D125."""
    v = []
    cartoes = pote.get("CARTOES")
    comps = pote.get("COMPARTIMENTOS")
    if not isinstance(cartoes, dict) or not isinstance(comps, dict):
        return ["v2.1 sem CARTOES ou sem COMPARTIMENTOS"]
    run = pote.get("INTELLIGENCE_RUN_ID")
    lugares = {}
    for comp, e in comps.items():
        if "OBJETOS" in e:
            v.append(f"{comp}: COPIA_NO_POTE — na v2.1 o compartimento guarda so IDS (D125.4)")
        ids = e.get("IDS")
        if not isinstance(ids, list):
            v.append(f"{comp}: sem IDS")
            continue
        if len(ids) != len(set(ids)):
            v.append(f"{comp}: ID repetido no compartimento")
        for oid in ids:
            if oid not in cartoes:
                v.append(f"{comp}/{oid}: ID sem cartao em CARTOES")
            lugares.setdefault(oid, set()).add(comp)
        if (e.get("UNIVERSO") or {}).get("OBJETOS") != len(ids):
            v.append(f"{comp}: UNIVERSO.OBJETOS nao e o numero de IDS")
    nomes = {}
    for oid, c in cartoes.items():
        if not isinstance(c, dict) or c.get("OBJETO_ID") != oid:
            v.append(f"CARTOES/{oid}: a chave nao e o OBJETO_ID do cartao")
            continue
        if set(c.get("COMPARTIMENTOS") or []) != lugares.get(oid, set()):
            v.append(f"{oid}: COMPARTIMENTOS do cartao nao batem com os IDS dos compartimentos")
        if not lugares.get(oid):
            v.append(f"{oid}: cartao que nenhum compartimento mostra")
        for n in [oid] + list(c.get("ALIAS") or []):
            if n in nomes and nomes[n] != oid:
                v.append(f"{oid}: o nome {n} ja e de {nomes[n]} — a mesma pergunta com dois cartoes")
            nomes[n] = oid
        k = c.get("CROSSING_KEY")
        if k is not None and oid != IDENT.crossing_id(k):
            v.append(f"{oid}: OBJETO_ID nao e XQ-sha(CROSSING_KEY)")
        if c.get("AVALIACAO_ID") != IDENT.avaliacao_id(oid, run):
            v.append(f"{oid}: AVALIACAO_ID nao e desta corrida")
        if not isinstance(c.get("ALIAS"), list) or not isinstance(c.get("ID_PROVISORIO"), bool):
            v.append(f"{oid}: sem ALIAS (lista) ou ID_PROVISORIO")
        d = c.get("DELTA")
        if not isinstance(d, dict) or d.get("MUDANCA") not in IDENT.MUDANCAS or e_ignorancia(d.get("CAUSA")):
            v.append(f"{oid}: DELTA ausente, invalido ou sem CAUSA")
        try:
            f = IDENT.fecho(oid, cartoes)
            if (c.get("FECHO") or {}).get("EVIDENCIAS") != f["EVIDENCIAS"] \
                    or (c.get("FECHO") or {}).get("N_ORIGINADORES") != f["N_ORIGINADORES"]:
                v.append(f"{oid}: FECHO nao e o fecho das provas (a prova conta 1 vez)")
        except (ValueError, KeyError) as erro:
            v.append(f"{oid}: {erro}")
        if "GRUPO" in c and e_ignorancia(c["GRUPO"]):
            v.append(f"{oid}: GRUPO vazio")
    v += IDENT.conferir_referencias(cartoes)
    ant = pote.get("ANTERIOR")
    if ant == "NENHUM":
        if any((c.get("DELTA") or {}).get("MUDANCA") != IDENT.NOVO for c in cartoes.values() if isinstance(c, dict)):
            v.append("ANTERIOR = NENHUM e ha cartao que nao e NOVO")
    elif not (isinstance(ant, dict) and not e_ignorancia(ant.get("INTELLIGENCE_RUN_ID"))
              and re.fullmatch(r"[0-9a-f]{64}", str(ant.get("POTE_SHA256")))):
        v.append("ANTERIOR tem de ser NENHUM ou {INTELLIGENCE_RUN_ID, POTE_SHA256}")
    cont = {m: 0 for m in IDENT.MUDANCAS}
    for c in cartoes.values():
        m = ((c or {}).get("DELTA") or {}).get("MUDANCA")
        if m in cont:
            cont[m] += 1
    cont[IDENT.SEM_REVISAO] += len(pote.get("NAO_REVISTOS") or [])
    cont[IDENT.SAIU] = len(pote.get("SAIRAM") or [])
    if pote.get("DELTA_CONTAGEM") != cont:
        v.append(f"DELTA_CONTAGEM nao bate com os cartoes: {pote.get('DELTA_CONTAGEM')} != {cont}")
    for s_ in pote.get("SAIRAM") or []:
        if e_ignorancia((s_ or {}).get("CAUSA")):
            v.append(f"SAIU sem causa: {s_}")
        if (s_ or {}).get("CROSSING_ID") in cartoes:
            v.append(f"SAIU e continua nos CARTOES: {s_.get('CROSSING_ID')}")
    for s_ in pote.get("NAO_REVISTOS") or []:
        if (s_ or {}).get("MUDANCA") != IDENT.SEM_REVISAO:
            v.append(f"ausente sem causa tem de ser SEM_REVISAO: {s_}")
    n = pote.get("CONTAGEM_DE_CARTOES") or {}
    if n.get("CARTOES_DISTINTOS") != len(cartoes) or \
            n.get("LUGARES_NOS_COMPARTIMENTOS") != sum(len(e.get("IDS") or []) for e in comps.values()):
        v.append("CONTAGEM_DE_CARTOES nao bate")
    if pote.get("ENTRADA") != "POTE_V2_SO_MEDICAO":
        v += ["v2: " + x for x in conferir_pote(materializar(pote))]
    return v


def como_js(pote: dict) -> str:
    """O pote na forma que o casco carrega: `window.SINTONIA_POTE`."""
    return ("/* GERADO por pacote/pote_intelligence_casco.py — " + MARCA + ".\n"
            "   " + str(pote.get("SCHEMA", CONTRATO)) + " · corrida " + str(pote["INTELLIGENCE_RUN_ID"]) + ".\n"
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


def ler_anterior_do_disco(caminho):
    """(pote, sha256 dos BYTES) do pote anterior PUBLICADO (.json ou o .js do casco). Opcao A do DELTA."""
    b = Path(caminho).read_bytes()
    texto = b.decode("utf-8")
    marca = "window." + NOME_DO_GLOBAL + " = "
    if marca in texto:
        texto = texto[texto.find(marca) + len(marca):].rstrip().rstrip(";")
    return json.loads(texto), IDENT.impressao_do_pote(b)


def _opcoes_v21(argv):
    """`--v21` e `--anterior <pote publicado>` (D125). Devolve (argv sem elas, v21?, anterior, sha)."""
    argv = list(argv)
    v21 = "--v21" in argv
    anterior = sha = None
    if "--anterior" in argv:
        i = argv.index("--anterior")
        anterior, sha = ler_anterior_do_disco(argv[i + 1])
        del argv[i:i + 2]
        v21 = True
    argv = [a for a in argv if a != "--v21"]
    return argv, v21, anterior, sha


def main(argv=None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    argv, v21, anterior, sha = _opcoes_v21(argv)
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
    if v21:
        pote = v21_do_v2(pote, anterior, sha)
    texto = como_js(pote) if destino.suffix == ".js" else json.dumps(pote, ensure_ascii=False, indent=1) + "\n"
    destino.write_text(texto, encoding="utf-8")
    if v21:
        print(f"{MARCA} · {CONTRATO_V21} · corrida {pote['INTELLIGENCE_RUN_ID']} · {pote['CONTAGEM_DE_CARTOES']} · "
              f"DELTA {pote['DELTA_CONTAGEM']} · {len(pote['RECUSADOS'])} recusados -> {destino}")
        return 0
    n = sum(len(e["OBJETOS"]) for e in pote["COMPARTIMENTOS"].values())
    vazios = sum(1 for e in pote["COMPARTIMENTOS"].values() if not e["OBJETOS"])
    print(f"{MARCA} · {CONTRATO} · corrida {pote['INTELLIGENCE_RUN_ID']} · {n} objetos · "
          f"{vazios} compartimentos vazios com o porque · {len(pote['RECUSADOS'])} recusados -> {destino}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
