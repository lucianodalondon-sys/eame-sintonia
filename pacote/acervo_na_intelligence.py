#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""O ACERVO NA INTELLIGENCE — a ENTRADA do acervo antigo passa pelas capacidades
que JA EXISTEM, numa corrida so, e sai como livro que o gerador do pote v2 le.

    MISSAO   ACERVO-NA-INTELLIGENCE (D115: o acervo antigo e real e passa pela
             Intelligence antes do casco; D97: o casco so mostra o que a
             Intelligence produziu). D115, D97 e D119 NAO estao escritas no
             repositorio: seguem o resumo delas no pedido da missao.
    ESPECIE  ADAPTADOR DE LEITURA + ORQUESTRACAO (Z-PACOTE, como
             pacote/rete_voci_dati.py). NAO E CAPACIDADE NOVA: nao julga nada
             que as capacidades da casa nao julguem.
    ESTADO   EXPERIMENTAL / NAO_PARA_CLIENTE. Nada publicado; o casco nao e
             tocado (o pote vai para docs/intelligence/acervo/, fora do portal).

    python3 pacote/acervo_na_intelligence.py            # regera POTE-ACERVO.json e RESUMO-ACERVO.json
    python3 pacote/acervo_na_intelligence.py --livro /tmp/LIVRO.json   # e o livro inteiro (~20 MB)
    python3 pacote/acervo_na_intelligence.py --conferir # regera em memoria e compara
    python3 -m unittest tests.test_acervo_na_intelligence -v

A PERGUNTA QUE ESTE FICHEIRO RESPONDE, E MAIS NENHUMA
-----------------------------------------------------
    DOS 2.080 ITENS JA COLETADOS DO ACERVO, O QUE AS CAPACIDADES DA
    INTELLIGENCE SUSTENTAM — COM PROVA ATE AO REGISTO DE ORIGEM — E O QUE
    ELAS RECUSAM, E PORQUE?

QUEM FAZ O QUE (um dono por coisa)
----------------------------------
    G0 · janela · ciencia   motor/motor_das_capacidades.rodar (corrida G0/v4 +
                            CAP-WIN + CAP-SCI + facto futuro + rendimento)
    vozes                   motor/voce_dal_campo.extrair (CAP-FIELD)
    concorrente -> ADAMA    coleta/concorrencia_meta.adama_no_anuncio, que so
                            pergunta a motor/porta_da_referencia (D116)
    mercado (P8)            pacote/pote_intelligence_casco.ler_serie decide
                            serie x sinal solto; aqui so se juntam os pontos
    o pote                  pacote/pote_intelligence_casco.adaptar +
                            pacote/validar_pote_v2.validar

O QUE ESTE FICHEIRO ESCREVE, E SO ISTO
--------------------------------------
    O READY de cada item, lido do registo de ORIGEM (italy-handoff-v21.js, o
    mesmo sha256 que a ENTRADA declara). As regras de tempo sao uma tabela
    declarada (`REGRA_DO_TEMPO`), e as de lugar sao uma so: o READY nao tem
    FACT_LOCATION (D112 — o lugar so vem do texto, e o texto e lido pelas
    capacidades; REGION_IDS do registo e o lugar do CATALOGO, nao do facto).

O QUE ELE NUNCA FAZ
-------------------
    NAO usa a publicacao como tempo do facto, salvo onde o facto E o acto de
        publicar (atividade do concorrente) — e isso e dito em FACT_TIME_BASIS.
    NAO faz de um anuncio uma OPORTUNIDADE nem uma DEMANDA (so SINAL em
        competitors), NAO afirma a cultura do anuncio, NAO compara concorrente
        por outra coisa que nao a SUBSTANCIA.
    NAO faz de um preco isolado uma mudanca de mercado: a variacao que o
        registo traz (CHANGE_VS_PREV_PCT) nao tem o periodo anterior e viaja
        como texto da fonte, nunca como leitura.
    NAO cunha esquema de ID: usa o do motor (prefixo + sha256(corrida|item))
        e marca todo ID como PROVISORIO (D119). NAO usa COMPOSTO_DE: nao existe
        no contrato do pote v2.
    NAO escreve no casco, NAO chama rede, NAO usa modelo.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
from datetime import date
from pathlib import Path

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))   # a raiz
import _gavetas  # noqa: E402,F401 — poe as gavetas do processo no caminho

import corrida_da_inteligencia as CI            # noqa: E402  (motor/)
import motor_das_capacidades as MOTOR           # noqa: E402  (motor/)
import porta_da_referencia as PORTA             # noqa: E402  (motor/, D116)
import voce_dal_campo as VOZ                    # noqa: E402  (motor/, CAP-FIELD)
import v21_completude_oportunidade as V21       # noqa: E402  (motor/: o leitor do pacote servido, sem navegador)
import concorrencia_meta as CM                  # noqa: E402  (coleta/: adama_no_anuncio, pela porta)
import pote_intelligence_casco as PIC           # noqa: E402  (pacote/)
import validar_pote_v2 as VALIDAR               # noqa: E402  (pacote/)

RAIZ = Path(os.path.dirname(HERE))
NAO_SEI = CI.NAO_SEI
MARCA = "EXPERIMENTAL · NAO_PARA_CLIENTE"
ESTADO = "EXPERIMENTAL_CANDIDATE"
CONTRATO = "ACERVO_NA_INTELLIGENCE/v1"
HOJE = date(2026, 9, 27)

ENTRADA = RAIZ / "docs" / "intelligence" / "acervo" / "ENTRADA-INTELLIGENCE-ACERVO.json"
ORIGEM = RAIZ / "italia-portale" / "client" / "italy-handoff-v21.js"
SAIDA = RAIZ / "docs" / "intelligence" / "acervo" / "corrida-acervo"
POTE_SAIDA = SAIDA / "POTE-ACERVO.json"
RESUMO_SAIDA = SAIDA / "RESUMO-ACERVO.json"

#: O LIMITE SUPERIOR DA CAPTURA, medido no git e nao escrito a mao: o primeiro
#: commit desta arvore onde a origem ja tem o sha256 que a ENTRADA declara. Todo
#: registo dela foi colhido ANTES disto. ⚠️ Nao e DATA_DO_PACOTE (2026-09-02):
#: medido, as transcricoes trazem OBSERVED_AT 2026-09-03, DEPOIS do «pacote» —
#: por isso a data do pacote nao prova limite nenhum. O teste confere o commit.
COMMIT_DA_ORIGEM = "c24ea78aeb11851fc00f90d6347729942abfe33e"
LIMITE_SUPERIOR_DA_CAPTURA = "2026-09-15"

#: D119 (resumo da missao): todo ID desta corrida e PROVISORIO.
ID_ESTADO = "PROVISORIO"
ID_ESTADO_PORQUE = ("D119: ID de uma corrida EXPERIMENTAL do acervo — esquema do motor "
                    "(prefixo + sha256(INTELLIGENCE_RUN_ID|ITEM)); muda se a corrida mudar")

#: O compartimento de cada coleccao da origem — o que a ENTRADA ja escreveu em
#: COMPARTIMENTO_DO_CONTRATO. Aqui so se diz QUE capacidade da casa le cada uma.
CAPACIDADE_DO_TIPO = {
    "anuncio": "CAP-COMP (coleta/concorrencia_meta.adama_no_anuncio pela porta)",
    "preco": "CAP-MKT (P8: pacote/pote_intelligence_casco.ler_serie)",
    "voz": "CAP-FIELD (motor/voce_dal_campo)",
    "transcricao": "CAP-FIELD (motor/voce_dal_campo)",
    "ciencia": "CAP-SCI (motor/capacidade_cientifica pelo motor)",
    "boletim": "CAP-WIN (motor/cap_win pelo motor)",
    "agromet": "CAP-WIN (motor/cap_win pelo motor)",
    "sinal_de_campo": "CAP-WIN (motor/cap_win pelo motor)",
    "evento": "corrida G0/v4 (FATO_PRESENTE_SOBRE_O_FUTURO)",
    "noticia": "arquivo (nenhuma capacidade le noticia: so G0)",
}

#: As regras de tempo, declaradas. Cada linha: (coleccao, campo da origem, e o
#: porque de ele ser o tempo do FACTO). Tudo o que nao esta aqui = NAO SEI.
REGRA_DO_TEMPO = {
    "competitorActivities:START_DATE": "o anuncio no ar E o facto (Meta Ads Library: START_DATE..END_DATE)",
    "competitorActivities:PUBLISHED_AT": ("a atividade do concorrente E publicar o conteudo "
                                          "(ACTIVITY_TYPE ORGANIC_*): aqui a publicacao e o proprio facto"),
    "marketObservations:REFERENCE_PERIOD": "o periodo a que o preco se refere (reescrito em ISO, sem mais)",
    "events:DATE": "a data do evento",
}
#: A publicacao, por coleccao — PUBLISHED_AT do READY. Nunca FACT_TIME (salvo a linha acima).
CAMPO_DA_PUBLICACAO = {
    "scienceCorpus": "PUBLISHED_AT", "scienceRecords": "PUBLISHED_AT",
    "transcripts": "PUBLICATION_DATE", "news": "DATE",
    "competitorActivities": "PUBLISHED_AT", "marketObservations": "PUBLICATION_DATE",
}

_ISO = re.compile(r"^(\d{4})-(\d{2})-(\d{2})$")
_DMY = re.compile(r"^(\d{2})/(\d{2})/(\d{4})$")


class LeiViolada(Exception):
    """O adaptador recusou-se, e diz porque."""


def _ign(v) -> bool:
    return CI.e_ignorancia(v) or (isinstance(v, str) and v.strip().upper() == "NOT_ESTABLISHED")


def _v(v):
    return NAO_SEI if _ign(v) else v


def _sha256(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def _iso(s):
    """'08/06/2026' -> '2026-06-08'; ISO passa; o resto e None. So reescreve."""
    if not isinstance(s, str):
        return None
    s = s.strip()
    if _ISO.match(s):
        return s
    m = _DMY.match(s)
    return f"{m.group(3)}-{m.group(2)}-{m.group(1)}" if m else None


def _periodo_iso(s):
    """'08/06/2026..14/06/2026' -> '2026-06-08..2026-06-14' (ou None)."""
    if not isinstance(s, str) or ".." not in s:
        return None
    a, b = (_iso(x) for x in s.split("..", 1))
    return f"{a}..{b}" if a and b else None


# ══════════════════════════════════════════════════════════════════════════
# 1 · A ENTRADA E A ORIGEM
# ══════════════════════════════════════════════════════════════════════════
def ler_entrada(entrada: Path = ENTRADA, origem: Path = ORIGEM) -> tuple:
    """-> (entrada, {ACERVO_ID: registo de origem}). Confere o sha da origem."""
    e = json.loads(entrada.read_text(encoding="utf-8"))
    if e.get("SCHEMA") != "ENTRADA_INTELLIGENCE_ACERVO/v1":
        raise LeiViolada("isto nao e a ENTRADA_INTELLIGENCE_ACERVO/v1")
    sha = _sha256(origem)
    if sha != e["ORIGEM"]["SHA256"]:
        raise LeiViolada(f"a origem mudou: sha256 {sha} != {e['ORIGEM']['SHA256']} da ENTRADA")
    V21.PORTAL = str(origem)
    pacote = V21.le_pacote()
    regs = {}
    for x in e["LISTA"]:
        _, col, rid = x["ACERVO_ID"].split("::", 2)
        achados = [r for r in (pacote.get(col) or []) if str(r.get("ID")) == rid]
        if len(achados) != 1:
            raise LeiViolada(f"{x['ACERVO_ID']}: {len(achados)} registos com este ID na origem")
        regs[x["ACERVO_ID"]] = achados[0]
    if len(regs) != e["ITENS"] or len(regs) != len(e["LISTA"]):
        raise LeiViolada("a ENTRADA diz %s itens e a LISTA tem %d" % (e["ITENS"], len(e["LISTA"])))
    return e, regs


def _colecao(x: dict) -> str:
    return x["ACERVO_ID"].split("::")[1]


def raw_id(x: dict, sha: str) -> str:
    _, col, rid = x["ACERVO_ID"].split("::", 2)
    return f"italy-handoff-v21.js@{sha[:12]}#{col}/{rid}"


def _url(x: dict):
    """O endereco do ITEM, como a ENTRADA o escreveu. Varios = NAO SEI (nao se escolhe)."""
    u = x.get("URL")
    if isinstance(u, list):
        u = [a for a in u if not _ign(a)]
        return u[0] if len(u) == 1 else NAO_SEI
    return _v(u)


def _fonte(x: dict):
    s = [a for a in x.get("SOURCE_IDS") or [] if a != "SRC_NAO_DECLARADA"]
    return s[0] if len(s) == 1 else NAO_SEI


# ══════════════════════════════════════════════════════════════════════════
# 2 · O TEMPO — do facto, da publicacao, e os limites provados da captura
# ══════════════════════════════════════════════════════════════════════════
def tempo_do_facto(x: dict, r: dict) -> tuple:
    """-> (FACT_TIME, FACT_TIME_BASIS). So pela tabela `REGRA_DO_TEMPO`."""
    col = _colecao(x)
    if col == "competitorActivities":
        ini, fim = _iso(r.get("START_DATE")), _iso(r.get("END_DATE"))
        if ini:
            return (f"{ini}..{fim}" if fim and fim != ini else ini,
                    "REGISTO.START_DATE/END_DATE — " + REGRA_DO_TEMPO[f"{col}:START_DATE"])
        pub = _iso(r.get("PUBLISHED_AT"))
        if pub and str(r.get("ACTIVITY_TYPE", "")).upper().startswith("ORGANIC"):
            return pub, "REGISTO.PUBLISHED_AT — " + REGRA_DO_TEMPO[f"{col}:PUBLISHED_AT"]
    if col == "marketObservations":
        p = _periodo_iso(r.get("REFERENCE_PERIOD"))
        if p:
            return p, "REGISTO.REFERENCE_PERIOD — " + REGRA_DO_TEMPO[f"{col}:REFERENCE_PERIOD"]
    if col == "events":
        d = _iso(r.get("DATE"))
        if d:
            return d, "REGISTO.DATE — " + REGRA_DO_TEMPO[f"{col}:DATE"]
    return NAO_SEI, NAO_SEI


def publicacao(x: dict, r: dict) -> tuple:
    campo = CAMPO_DA_PUBLICACAO.get(_colecao(x))
    d = _iso(r.get(campo)) if campo else None
    return (d, f"REGISTO.{campo}") if d else (NAO_SEI, NAO_SEI)


def captura(x: dict, r: dict, fact_time, pub) -> tuple:
    """-> (CAPTURED_AT como viaja, COMO). O dia real da colheita, quando o
    registo o diz (OBSERVED_AT); senao, o LIMITE PROVADO que decide o D4 do G0.

        inferior  a publicacao (nao se colhe antes de publicar) e, para o que e
                  OBSERVADO (anuncio no ar, preco de um periodo), o inicio do
                  proprio facto — um anuncio so esta na biblioteca depois de
                  comecar; o preco de uma semana so existe depois de ela comecar.
        superior  LIMITE_SUPERIOR_DA_CAPTURA (o git).
    Facto que comeca ate ao inferior = passado (D4 passa). Facto que comeca
    depois do superior = futuro por desenho. Entre os dois: NAO SEI, e o G0
    bloqueia — como deve.
    """
    real = _iso(r.get("OBSERVED_AT"))
    if real:
        return real, "REGISTO.OBSERVED_AT (o dia real da colheita)"
    t = CI.intervalo_do_tempo(fact_time) if not _ign(fact_time) else {"ESTADO": NAO_SEI}
    if t.get("ESTADO") != "INTERVALO":
        return NAO_SEI, "NAO_VEIO: o registo nao traz o dia da colheita"
    col = _colecao(x)
    inf = [d for d in (pub if not _ign(pub) else None,) if d]
    if col in ("competitorActivities", "marketObservations"):
        inf.append(t["INICIO"])
    inferior = max(inf) if inf else None
    if inferior and t["INICIO"] <= inferior:
        return (f"{inferior} (LIMITE_INFERIOR provado da captura; o dia real da colheita e NAO SEI)",
                "LIMITE_INFERIOR: publicacao / inicio do facto observado")
    if t["INICIO"] > LIMITE_SUPERIOR_DA_CAPTURA:
        return (f"{LIMITE_SUPERIOR_DA_CAPTURA} (LIMITE_SUPERIOR provado: a origem ja estava no git em "
                f"{COMMIT_DA_ORIGEM[:8]}; o dia real da colheita e NAO SEI)",
                "LIMITE_SUPERIOR: git " + COMMIT_DA_ORIGEM[:8])
    return NAO_SEI, "NAO_VEIO: nenhum limite provado decide se o facto comecou antes da colheita"


# ══════════════════════════════════════════════════════════════════════════
# 3 · O READY — o que a Collection teria entregado, lido da origem
# ══════════════════════════════════════════════════════════════════════════
def _fato(x: dict, r: dict) -> dict:
    """O envelope FATO com os NOMES do produtor (COL-LAW-202). So campos que o
    registo traz; nunca a pessoa privada (PERSON, handle) nem resumos."""
    col = _colecao(x)
    f = {}
    if col in ("scienceCorpus", "scienceRecords"):
        # ERRO A (LAB F2, 01/10): `NOT_ESTABLISHED` e o «nao sei» do handoff antigo, nunca um DOI.
        # O motor so conhece as palavras de ignorancia da casa; o adaptador traduz ANTES (_v).
        f["doi"] = _v(r.get("DOI"))
        f["title"] = _v(r.get("TITLE"))
        f["authors"] = _v(r.get("ORCID")) if not _ign(r.get("ORCID")) else _v(r.get("AUTHOR"))
        f["institutions"] = _v(r.get("INSTITUTION"))
        f["material_type"] = _v(r.get("MATERIAL_TYPE"))
        # so o que o produtor PROVOU com trecho (PROVED_*_EVIDENCE); CROP/ISSUE soltos
        # do handoff antigo nao tem evidencia e nao entram como cultura/problema.
        if not _ign(r.get("PROVED_CROP")) and not _ign(r.get("PROVED_CROP_EVIDENCE")):
            f["crop"] = r["PROVED_CROP"]
        if not _ign(r.get("PROVED_ISSUE")) and not _ign(r.get("PROVED_ISSUE_EVIDENCE")):
            f["problem"] = r["PROVED_ISSUE"]
    elif col == "competitorActivities":
        for k in ("COMPANY", "PAGE", "CHANNEL", "PLATFORM", "ACTIVITY_TYPE", "ACTIVE_STATUS", "TITLE"):
            if not _ign(r.get(k)):
                f[k.lower()] = r[k]
        if not _ign(r.get("CREATIVE_TEXT")):
            f["creative_text"] = r["CREATIVE_TEXT"]
        if r.get("PRODUCTS_PROVED"):
            f["products_proved"] = r["PRODUCTS_PROVED"]
    elif col == "marketObservations":
        for k in ("MARKET", "PRODUCT", "STAGE", "UNIT", "PRICE_NUM", "PRICE_RAW", "REFERENCE_PERIOD",
                  "CHANGE_VS_PREV_PCT", "PREV_PRICE_NUM", "GROUP"):
            if r.get(k) is not None and not _ign(r.get(k)):
                f[k.lower()] = r[k]
    else:
        for k in ("TITLE", "EVENT", "BULLETIN_TITLE", "CONTENT_TITLE", "ISSUE", "CROP"):
            if not _ign(r.get(k)):
                f[k.lower()] = r[k]
    return f


def _texto(x: dict, r: dict) -> str:
    for k in ("TITLE", "EVENT", "BULLETIN_TITLE", "CONTENT_TITLE", "PRODUCT"):
        if not _ign(r.get(k)):
            return str(r[k])[:300]
    return NAO_SEI


#: ERRO A, a consequencia (01/10): sem o DOI falso, 85 estudos do acervo perdiam a triagem de estudo
#: (o motor so tria por DOI/TRIAL_ID/especie no FATO ou pela NATUREZA que a ADMISSAO declarou). Neste
#: acervo quem admite e a ENTRADA (ADMITIDO_POR), e ela ja declara TIPO = ciencia por item. Escreve-se essa
#: declaracao na MESMA forma da admissao da Sala (admissao.py: ORIGEM.CAP_SCI + EXTRATOR_DO_ESTUDO), com os
#: nomes do dono (leis/estudo_chaves.NATUREZA, LEI_CAP_SCI) — nunca uma segunda copia. So a natureza:
#: cultura/problema/lugar continuam a vir do FATO provado (PROVED_*), nunca daqui.
EXTRATOR_DA_NATUREZA = "ENTRADA_INTELLIGENCE_ACERVO/v1 (TIPO=ciencia)"


def _natureza_declarada(x: dict):
    if x.get("TIPO") != "ciencia":
        return NAO_SEI
    import estudo_chaves as EC                                     # noqa: PLC0415 (leis/)
    return {"ORIGEM": {"CAP_SCI": {"NATUREZA": EC.NATUREZA, "E_INCIDENCIA_DE_CAMPO": "NAO", "LEI": EC.LEI_CAP_SCI},
                       "EXTRATOR_DO_ESTUDO": EXTRATOR_DA_NATUREZA}}


def ready(x: dict, r: dict, sha: str) -> tuple:
    """-> (READY, RAW, COMO_DA_CAPTURA). FACT_LOCATION e sempre NAO SEI (D112)."""
    ft, ftb = tempo_do_facto(x, r)
    pub, pubb = publicacao(x, r)
    cap, como = captura(x, r, ft, pub)
    col = _colecao(x)
    sloc = _v(r.get("SOURCE_COUNTRY")) if col == "transcripts" else NAO_SEI
    item = {
        "ESTADO": MOTOR.SCI.PRONTO,
        "ITEM_ID": x["ACERVO_ID"],
        "RAW_OBSERVATION_ID": raw_id(x, sha),
        "UNIVERSO": "ACERVO/" + x["TIPO"],
        "ESTAGIO": NAO_SEI,
        "TEXTO": _texto(x, r),
        "SOURCE_ID": _fonte(x),
        # O lugar da FONTE fica no campo dela, com a base — nunca vira FACT_LOCATION.
        "SOURCE_LOCATION": sloc,
        "SOURCE_LOCATION_BASIS": ("REGISTO.SOURCE_COUNTRY (SOURCE_COUNTRY_ORIGIN=%s)" % r.get("SOURCE_COUNTRY_ORIGIN")
                                  if sloc != NAO_SEI else NAO_SEI),
        # D112: o lugar do facto so vem do TEXTO, lido por uma capacidade. REGION_IDS
        # do registo e o lugar do catalogo (medido: um video da Syngenta ESPANA com
        # GEO_ITALY). No READY: NAO SEI.
        "FACT_LOCATION": NAO_SEI,
        "FACT_LOCATION_BASIS": NAO_SEI,
        "FACT_TIME": ft,
        "FACT_TIME_BASIS": ftb,
        "PUBLISHED_AT": pub,
        "PUBLISHED_AT_BASIS": pubb,
        "OBSERVED_AT": NAO_SEI,
        "CAPTURED_AT": cap,
        "COMPLETUDE_TEMPO_LUGAR": NAO_SEI,
        "TEMPO_LUGAR_EVIDENCIA": {"FACT_LOCATION_VEIO_DE": NAO_SEI, "CAPTURA": como},
        "SOURCE_DECLARED_EVIDENCE_CLASS": NAO_SEI,
        "FATO": _fato(x, r),
        "JANELA_DECLARADA": _natureza_declarada(x),
        "CORRIDA": NAO_SEI,
        "ADMITIDO_POR": "ENTRADA_INTELLIGENCE_ACERVO/v1 (" + x["ACERVO_ID"] + ")",
    }
    url = _url(x)
    raw = {"URL": url, "DOCUMENT_ID": url, "DOCUMENT_ID_BASIS": "ENTRADA.URL" if url != NAO_SEI else NAO_SEI}
    return item, raw, como


# ══════════════════════════════════════════════════════════════════════════
# 4 · AS CAPACIDADES QUE O MOTOR NAO CORRE (mesma corrida, mesma LINEAGE)
# ══════════════════════════════════════════════════════════════════════════
def _oid(prefixo: str, run_id: str, chave: str) -> str:
    """O esquema do motor (motor_das_capacidades: 'R7-SCI-' + sha256(run|item)[:16])."""
    return prefixo + hashlib.sha256((run_id + "|" + chave).encode()).hexdigest()[:16]


def _ent(valor, fonte, iid, extra=None):
    return MOTOR._entidade(valor, fonte, [{"ITEM_ID": iid}], extra)


def _prova(ctx, iid):
    return MOTOR._prova(ctx["READY"][iid], ctx["LINHA"][iid], ctx["RAW"])


def _com_id_provisorio(o: dict) -> dict:
    o["CHAVES"]["ID_ESTADO"] = ID_ESTADO
    o["CHAVES"]["ID_ESTADO_PORQUE"] = ID_ESTADO_PORQUE
    return o


def concorrentes(itens, regs, ctx, ref) -> tuple:
    """Anuncio do concorrente -> SUBSTANCIA/alvo que o criativo nomeia -> registo
    ADAMA com a mesma substancia, SO pela porta. SINAL, nunca OPORTUNIDADE."""
    colheita = []
    for x in itens:
        r = regs[x["ACERVO_ID"]]
        texto = " ".join(str(r.get(k) or "") for k in ("CREATIVE_TEXT", "TITLE"))
        colheita.append({"OBSERVACAO": {"CREATIVE_TEXT": texto, "META_AD_LIBRARY_ID": x["ACERVO_ID"],
                                        "COMPANY": r.get("COMPANY")}})
    lido = CM.adama_no_anuncio(colheita, referencia=ref)
    por_id = {a["META_AD_LIBRARY_ID"]: a for a in lido["ANUNCIOS"]}
    objs, nao_vao = [], []
    for x in itens:
        iid = x["ACERVO_ID"]
        r, linha = regs[iid], ctx["LINHA"][iid]
        oid = _oid("R7-COMP-", ctx["RUN_ID"], iid)
        if not MOTOR._admite(linha, MOTOR.SINAL):
            nao_vao.append({"OBJETO_ID": oid, "ITEM_ID": iid, "COMPARTIMENTO": "competitors",
                            "MOTIVO": "SEM_PROVA_ADMITIDA_PELO_POTE",
                            "DETALHE": "G0: " + ", ".join(linha.get("G0_FALTA") or [])})
            continue
        a = por_id.get(iid) or {}
        mesma = sorted({g["REGISTRATION_NUMBER"] for s in a.get("SUBSTANCIAS_NO_CRIATIVO", [])
                        for g in s["ADAMA"].get("REGISTOS", [])})
        ent = {"COMPANY_ID": _ent(_v(r.get("COMPANY")), "REGISTO.COMPANY", iid),
               "PRODUCT_ID": _ent(NAO_SEI, NAO_SEI, iid),
               "CROP_ID": _ent(NAO_SEI, NAO_SEI, iid),
               "FACT_LOCATION": _ent(NAO_SEI, NAO_SEI, iid),
               "FACT_TIME": _ent(_v(linha.get("FACT_TIME")), "READY.FACT_TIME", iid),
               "T4_REGISTRATION_EVIDENCE_ID": _ent(NAO_SEI, NAO_SEI, iid)}
        ent["CROP_ID"]["PORQUE"] = "a cultura do anuncio nao se afirma (o cadastro nao a da)"
        ent["FACT_LOCATION"]["PORQUE"] = ("REGION_IDS %s do registo e o alcance/catalogo, nao o lugar do "
                                          "facto (D112)" % r.get("REGION_IDS"))
        ent["T4_REGISTRATION_EVIDENCE_ID"]["PORQUE"] = ("o registo do CONCORRENTE nao esta na referencia "
                                                        "(lacuna 3 da PORTA-UNICA-REFERENCIA)")
        chaves = {k: ent[k]["VALOR"] for k in PIC.COMPARTIMENTOS["competitors"]["CHAVES"]}
        chaves.update({
            "ESPECIE_DO_MOTOR": "ANALYTIC_JUDGMENT/ANUNCIO_CONCORRENTE",
            "CAPACIDADE": CAPACIDADE_DO_TIPO["anuncio"], "ENTITY_SOURCE": ent,
            "DA_FONTE": {"COMPANY": _v(r.get("COMPANY")), "PAGE": _v(r.get("PAGE") or r.get("CHANNEL")),
                         "PLATFORM": _v(r.get("PLATFORM")), "ACTIVITY_TYPE": _v(r.get("ACTIVITY_TYPE")),
                         "ACTIVE_STATUS": _v(r.get("ACTIVE_STATUS")),
                         "ACTIVE_STATUS_NOTA": "estado lido na colheita, nao o de hoje"},
            "INTERPRETACAO_DO_SISTEMA": {
                "SUBSTANCIAS_NO_CRIATIVO": a.get("SUBSTANCIAS_NO_CRIATIVO", []),
                "ALVOS_NO_CRIATIVO": a.get("ALVOS_NO_CRIATIVO", []),
                "ADAMA_COM_A_MESMA_SUBSTANCIA": mesma or NAO_SEI,
                "GRAO": "SUBSTANCIA — o concorrente so se compara por substancia; cultura NAO SEI",
                "REFERENCIA_ADAMA": lido["REFERENCIA_ADAMA"].get("EDICAO_REGISTRO", NAO_SEI),
                "PORQUE": a.get("PORQUE"),
                "NAO_E": ["DEMANDA", "OPORTUNIDADE", "PRESSAO_DE_MERCADO", "VENDA"]},
        })
        objs.append(_com_id_provisorio({
            "OBJETO_ID": oid, "ESPECIE": MOTOR.SINAL, "ESTADO": ESTADO, "CHAVES": chaves,
            "PROVA": [_prova(ctx, iid)],
            "PORQUE": ("anuncio do concorrente observado; "
                       + ("substancia(s) no criativo com registo ADAMA: " + ", ".join(mesma) if mesma else
                          "nenhuma substancia do vocabulario da referencia com registo ADAMA ativo (NAO SEI, "
                          "nunca «a ADAMA nao tem»)")),
            "CONTRADIZ": None,
            "INCERTEZA": "anuncio nao e demanda nem oportunidade; o alcance nao e o lugar do facto",
            # LOTE8-INTEGRA · D123: a ligacao que concorrencia_meta.adama_no_anuncio pediu A PORTA
            # (por substancia do criativo); anuncio que ela nao leu -> a porta diz NAO_SEI
            "LIGACAO_ADAMA": a.get("LIGACAO_ADAMA") or PORTA.ligacao_adama(ref, {"VEM_DE": {}})}))
    return objs, nao_vao, {"REFERENCIA_ADAMA": lido["REFERENCIA_ADAMA"], "ESTADO": lido["ESTADO"],
                           "ANUNCIOS_COM_SUBSTANCIA": sum(1 for a in lido["ANUNCIOS"]
                                                          if a["SUBSTANCIAS_NO_CRIATIVO"]),
                           "ANUNCIOS_COM_ALVO": sum(1 for a in lido["ANUNCIOS"] if a["ALVOS_NO_CRIATIVO"])}


def chave_da_serie(r: dict):
    """Praca x produto x estagio x unidade — os quatro do registo; falta um = sem serie."""
    k = tuple(r.get(c) for c in ("MARKET", "PRODUCT", "STAGE", "UNIT"))
    return None if any(_ign(v) or v is None for v in k) else k


def mercado(itens, regs, ctx) -> tuple:
    """Cada preco com G0 -> SINAL no Polso. SERIE so com os pontos admitidos da
    MESMA chave; quem le serie x sinal solto e `ler_serie` do pote (P8)."""
    pontos = {}
    admit = []
    nao_vao = []
    for x in itens:
        iid = x["ACERVO_ID"]
        r, linha = regs[iid], ctx["LINHA"][iid]
        oid = _oid("R7-MKT-", ctx["RUN_ID"], iid)
        if r.get("PRICE_NUM") is None or _ign(r.get("UNIT")):
            nao_vao.append({"OBJETO_ID": oid, "ITEM_ID": iid, "COMPARTIMENTO": "market",
                            "MOTIVO": "SEM_PRECO_NO_REGISTO",
                            "DETALHE": "o registo aponta para a fonte e nao traz preco com unidade"})
            continue
        if not MOTOR._admite(linha, MOTOR.SINAL):
            nao_vao.append({"OBJETO_ID": oid, "ITEM_ID": iid, "COMPARTIMENTO": "market",
                            "MOTIVO": "SEM_PROVA_ADMITIDA_PELO_POTE",
                            "DETALHE": "G0: " + ", ".join(linha.get("G0_FALTA") or [])})
            continue
        admit.append((x, oid))
        k = chave_da_serie(r)
        if k:
            pontos.setdefault(k, []).append({"PERIOD": linha["FACT_TIME"], "PRICE": r["PRICE_NUM"],
                                             "UNIT": r["UNIT"], "ITEM_ID": iid})
    objs = []
    for x, oid in admit:
        iid = x["ACERVO_ID"]
        r = regs[iid]
        k = chave_da_serie(r)
        serie = sorted(pontos.get(k, []), key=lambda p: p["PERIOD"]) if k else []
        ent = {"CROP_ID": _ent(NAO_SEI, NAO_SEI, iid),
               "MARKET_PLACE_ID": _ent(_v(r.get("MARKET")), "REGISTO.MARKET", iid),
               "PERIOD": _ent(ctx["LINHA"][iid]["FACT_TIME"], "READY.FACT_TIME (REFERENCE_PERIOD)", iid),
               "PRICE": _ent(r.get("PRICE_NUM"), "REGISTO.PRICE_NUM", iid),
               "UNIT": _ent(_v(r.get("UNIT")), "REGISTO.UNIT", iid),
               "MARKET_STAGE": _ent(_v(r.get("STAGE")), "REGISTO.STAGE", iid)}
        ent["CROP_ID"]["PORQUE"] = "o registo da o PRODUTO de mercado (%s), nao a cultura" % r.get("PRODUCT")
        chaves = {k2: ent[k2]["VALOR"] for k2 in PIC.COMPARTIMENTOS["market"]["CHAVES"]}
        chaves.update({
            "ESPECIE_DO_MOTOR": "OBSERVACAO_DE_PRECO", "CAPACIDADE": CAPACIDADE_DO_TIPO["preco"],
            "ENTITY_SOURCE": ent,
            # A variacao que a FONTE escreveu viaja como texto dela: sem o periodo do
            # ponto anterior nao e ponto medido, e o pote nao a le como mudanca (P8).
            "DA_FONTE": {"PRODUCT": _v(r.get("PRODUCT")), "PRICE_RAW": _v(r.get("PRICE_RAW")),
                         "VARIACAO_ESCRITA_PELA_FONTE": {
                             "CHANGE_VS_PREV_PCT": r.get("CHANGE_VS_PREV_PCT", NAO_SEI),
                             "PREV_PRICE_NUM": r.get("PREV_PRICE_NUM", NAO_SEI),
                             "PERIODO_DO_PONTO_ANTERIOR": NAO_SEI,
                             "LEITURA": "nao e ponto medido: sem periodo nao entra na serie"},
                         "SERIES_STATE": _v(r.get("SERIES_STATE"))},
            "INTERPRETACAO_DO_SISTEMA": {"NAO_E": ["DEMANDA", "VENDA", "MUDANCA_DE_MERCADO_SEM_SERIE"],
                                         "CHAVE_DA_SERIE": list(k) if k else NAO_SEI},
        })
        o = {"OBJETO_ID": oid, "ESPECIE": MOTOR.SINAL, "ESTADO": ESTADO, "CHAVES": chaves,
             "PROVA": [_prova(ctx, iid)],
             "PORQUE": "preco observado para um periodo, numa praca",
             "CONTRADIZ": None, "INCERTEZA": "um ponto so nao e mercado",
             # LOTE8-INTEGRA · D123: pela porta, com as chaves do objeto (CROP_ID NAO SEI -> FALTA CULTURA)
             "LIGACAO_ADAMA": PORTA.ligacao_adama(ctx["REF"], {"VEM_DE": {}})}
        if len(serie) >= 2:
            o["SERIE"] = [{c: p[c] for c in ("PERIOD", "PRICE", "UNIT")} for p in serie]
        objs.append(_com_id_provisorio(o))
    return objs, nao_vao


def _textos_do_repo() -> dict:
    """sha256 do texto -> documento de voce_dal_campo (os transcritos versionados)."""
    return {hashlib.sha256((d["TEXT"] or "").encode("utf-8")).hexdigest(): d
            for d in VOZ.documentos_do_repo(str(RAIZ))}


def vozes(itens, regs, ctx) -> tuple:
    """CAP-FIELD sobre o texto: transcricao so se o TEXTO esta no repositorio e bate
    pelo TEXT_SHA256 do registo; comentario pelo TEXT_ORIGINAL. A pessoa privada
    (handle) NAO viaja: o documento vai sem canal de pessoa."""
    docs = _textos_do_repo()
    objs, nao_vao, medida = [], [], {"DOCUMENTOS_LIDOS": 0, "SEM_TEXTO_NO_REPO": 0, "VOZES_EXTRAIDAS": 0,
                                    "VOZES_SEM_PROVA_ADMITIDA": 0}
    for x in itens:
        iid = x["ACERVO_ID"]
        r, linha = regs[iid], ctx["LINHA"][iid]
        if _colecao(x) == "transcripts":
            d = docs.get(r.get("TEXT_SHA256"))
            if d is None:
                medida["SEM_TEXTO_NO_REPO"] += 1
                nao_vao.append({"OBJETO_ID": NAO_SEI, "ITEM_ID": iid, "COMPARTIMENTO": "voices",
                                "MOTIVO": "TEXTO_NAO_ESTA_NO_REPOSITORIO",
                                "DETALHE": "TEXT_SHA256 %s nao bate com nenhum transcrito versionado "
                                           "(TRANSCRIPT_QUALITY=%s)" % (r.get("TEXT_SHA256", NAO_SEI),
                                                                        r.get("TRANSCRIPT_QUALITY"))})
                continue
            doc = dict(d, SOURCE_ID=ctx["READY"][iid]["SOURCE_ID"])
        else:
            texto = r.get("TEXT_ORIGINAL")
            if _ign(texto):
                nao_vao.append({"OBJETO_ID": NAO_SEI, "ITEM_ID": iid, "COMPARTIMENTO": "voices",
                                "MOTIVO": "SEM_TEXTO", "DETALHE": "o comentario nao traz TEXT_ORIGINAL"})
                continue
            doc = VOZ.documento(texto, source_id=ctx["READY"][iid]["SOURCE_ID"], external_id=r.get("ID"),
                                url=r.get("SOURCE_URL"), platform=r.get("PLATFORM"),
                                channel=None, title=r.get("CONTENT_TITLE"), published_at=None)
        medida["DOCUMENTOS_LIDOS"] += 1
        ex = VOZ.extrair(doc, referencia=ctx["REF"])   # D123: cada voz sai ligada pela porta
        if not ex["VOZES"]:
            nao_vao.append({"OBJETO_ID": NAO_SEI, "ITEM_ID": iid, "COMPARTIMENTO": "voices",
                            "MOTIVO": "SEM_VOZ_EXTRAIDA",
                            "DETALHE": "voce_dal_campo nao achou frase com cultura ou problema do "
                                       "vocabulario (lacuna de vocabulario, nao ausencia)"})
            continue
        for v in ex["VOZES"]:
            medida["VOZES_EXTRAIDAS"] += 1
            oid = _oid("R7-VOZ-", ctx["RUN_ID"], iid + "|" + v["VOICE_ID"])
            if not MOTOR._admite(linha, MOTOR.SINAL):
                medida["VOZES_SEM_PROVA_ADMITIDA"] += 1
                nao_vao.append({"OBJETO_ID": oid, "ITEM_ID": iid, "COMPARTIMENTO": "voices",
                                "MOTIVO": "SEM_PROVA_ADMITIDA_PELO_POTE",
                                "DETALHE": "G0: " + ", ".join(linha.get("G0_FALTA") or []) +
                                           " — a publicacao nao e o dia da fala (voce_dal_campo)"})
                continue
            ent = {"SPEAKER_ID": _ent(_v(v["SPEAKER_ID"]), "voce_dal_campo.SPEAKER_ID", iid),
                   "SPEAKER_ROLE": _ent(_v(v["ROLE"]), "voce_dal_campo.ROLE", iid),
                   "QUOTE_OR_TRANSCRIPT": _ent(v["QUOTE_ORIGINAL"], "voce_dal_campo.QUOTE_ORIGINAL", iid),
                   "CROP_ID": _ent(_v(v["CROP"]), "voce_dal_campo.CROP", iid),
                   "ISSUE_ID": _ent(_v(v["ISSUE"]), "voce_dal_campo.ISSUE", iid),
                   "FACT_LOCATION": _ent(_v(v["FACT_LOCATION"]), "voce_dal_campo.FACT_LOCATION (texto)", iid),
                   "FACT_TIME": _ent(_v(linha.get("FACT_TIME")), "READY.FACT_TIME", iid)}
            chaves = {k: ent[k]["VALOR"] for k in PIC.COMPARTIMENTOS["voices"]["CHAVES"]}
            chaves.update({"ESPECIE_DO_MOTOR": "VOCE", "CAPACIDADE": CAPACIDADE_DO_TIPO["voz"],
                           "ENTITY_SOURCE": ent,
                           "DA_FONTE": {"QUOTE_ORIGINAL": v["QUOTE_ORIGINAL"]},
                           "INTERPRETACAO_DO_SISTEMA": v["INTERPRETACAO"]})
            o = {"OBJETO_ID": oid, "ESPECIE": MOTOR.SINAL, "ESTADO": ESTADO, "CHAVES": chaves,
                 "PROVA": [_prova(ctx, iid)], "PORQUE": v["WHAT_IT_PROVES"], "CONTRADIZ": None,
                 "INCERTEZA": v["WHAT_IT_DOES_NOT_PROVE"],
                 "LIGACAO_ADAMA": v["LIGACAO_ADAMA"]}   # D123: a da voz, feita pela porta
            if ent["FACT_LOCATION"]["VALOR"] != NAO_SEI:
                o["LOCATION_SOURCE"] = "TEXTO (voce_dal_campo: %s)" % v.get("FACT_LOCATION_BASIS", NAO_SEI)
            objs.append(_com_id_provisorio(o))
    return objs, nao_vao, medida


#: ⚠️ DUAS CASAS QUE NUNCA SE ENCONTRARAM, MEDIDO NESTA CORRIDA. O motor das
#: capacidades (INT-R7-CAPS) escreve em CHAVES.ENTITY_SOURCE um MAPA chave ->
#: procedencia (D112b) e o seu portao exige-o. O contrato unico do pote v2 le
#: ENTITY_SOURCE como um TEXTO (schema: string) e levanta-o de CHAVES para o
#: objeto. Com a saida do motor tal como sai, validar_pote_v2 REPROVA todo objeto
#: (o teste do motor que corria o gerador esta em skip: ce775ff5 nao esta no clone).
#: Nenhum dos dois donos e mudado aqui: o mapa viaja com outro NOME, inteiro
#: (FORA_DO_CONTRATO.ENTITY_SOURCE_POR_CHAVE).
#: D-GER-1-MIG (decisao do Intelligence owner, 29/09): no objeto, ENTITY_SOURCE e um
#: valor da COL-LAW-221 — o fiscal do pote so aceita esse vocabulario. O mapa nao e um
#: valor da lei, e o texto que o apontava tambem nao; por isso o objeto diz UNKNOWN, e o
#: mapa continua inteiro ao lado. Nunca se achata o mapa nem se escolhe uma entrada.
ENTITY_SOURCE_TEXTO = "UNKNOWN"


def ao_contrato_unico(objetos: dict) -> None:
    for os_ in objetos.values():
        for o in os_:
            ch = o.get("CHAVES") or {}
            if isinstance(ch.get("ENTITY_SOURCE"), dict):
                ch["ENTITY_SOURCE_POR_CHAVE"] = ch.pop("ENTITY_SOURCE")
                o["ENTITY_SOURCE"] = ENTITY_SOURCE_TEXTO


def arquivo(objetos: dict) -> list:
    """P3 · o Archivio guarda os objetos que ESTA corrida produziu: mesma especie,
    mesma prova, mesmo ID (a unicidade e por compartimento)."""
    out = []
    for comp in ("competitors", "market", "voices", "science", "windows", "future"):
        for o in objetos.get(comp) or []:
            if o["ESPECIE"] not in PIC.COMPARTIMENTOS["archive"]["ESPECIES"]:
                continue
            if MOTOR._e_conhecimento(o):
                # F2 (§5-E): o conhecimento sem tempo nao se arquiva — o Archivio e memoria DATADA, e arquiva-lo
                # obrigava a inventar FACT_TIME (ou a vê-lo recusado la dentro, contado duas vezes)
                continue
            ch = o["CHAVES"]
            chaves = {k: ch.get(k, NAO_SEI) for k in PIC.COMPARTIMENTOS["archive"]["CHAVES"]}
            if chaves["FACT_TIME"] == NAO_SEI and o["PROVA"]:
                chaves["FACT_TIME"] = o["PROVA"][0]["FACT_TIME"]
            chaves.update({"ARQUIVADO_DE": comp, "ID_ESTADO": ID_ESTADO, "ID_ESTADO_PORQUE": ID_ESTADO_PORQUE})
            a = {k: o[k] for k in ("OBJETO_ID", "ESPECIE", "ESTADO", "PROVA", "PORQUE", "CONTRADIZ", "INCERTEZA")}
            a["CHAVES"] = chaves
            for c in ("LOCATION_SOURCE", "LIGACAO_ADAMA"):   # D123: a ligacao viaja com o objeto
                if c in o:
                    a[c] = o[c]
            out.append(a)
    return out


# ══════════════════════════════════════════════════════════════════════════
# 5 · A CORRIDA INTEIRA
# ══════════════════════════════════════════════════════════════════════════
def _source_head() -> str:
    try:
        return subprocess.run(["git", "rev-parse", "HEAD"], cwd=RAIZ, capture_output=True,
                              text=True, check=True).stdout.strip()
    except Exception:  # noqa: BLE001 — sem git, o cabecalho diz NAO SEI
        return NAO_SEI


#: ⚠️ DEFEITO ABERTO, MEDIDO E NAO CONSERTADO AQUI. A corrida G0/v4 recusa-se a
#: escrever um requisito que nomeie palavra da Collection (corrida_da_inteligencia
#: `_requisito`, PALAVRAS_QUE_O_REQUISITO_RECUSA) — e o requisito leva o SOURCE_ID.
#: Um SOURCE_ID como SRC_API_ARPA_VENETO_IT (o dominio tem «api») derruba a corrida
#: INTEIRA em ERROR. Mudar a lei do motor nao e desta missao: estes itens ficam
#: FORA da corrida, contados um a um, com o motivo — nunca em silencio.
FORA_DA_CORRIDA_PORQUE = ("o SOURCE_ID/ITEM_ID contem %s, e a corrida G0/v4 recusa-se a escrever um "
                          "requisito que nomeie palavra da Collection (motor/corrida_da_inteligencia.py, "
                          "PALAVRAS_QUE_O_REQUISITO_RECUSA): com ele dentro a corrida inteira termina em ERROR")


#: ERRO B (LAB F2, 01/10): o handoff antigo traz o MESMO estudo em scienceCorpus e scienceRecords.
#: Identidade = o DOI real (minusculo); sem DOI, so quando as duas listas trazem o mesmo titulo
#: normalizado + a mesma PUBLISHED_AT (o mesmo registo copiado). Titulo igual com DOI diferente
#: NAO e o mesmo estudo (preprint != artigo, ficheiro suplementar != artigo): fica.
#: O melhor = mais campos com valor (nao ignorancia); empate -> scienceCorpus; depois o ACERVO_ID.
COLECOES_DE_CIENCIA = ("scienceCorpus", "scienceRecords")
DUPLICADO_PORQUE = ("o mesmo estudo (%s) ja entra pela copia %s, com mais campos com valor (%d contra %d): "
                    "uma copia pior nao e artigo novo")


def _chave_do_estudo(x: dict, r: dict):
    d = r.get("DOI")
    if not _ign(d) and str(d).strip().lower().startswith("10."):
        return "DOI:" + str(d).strip().lower().rstrip(".")
    t = re.sub(r"\W+", " ", str(r.get("TITLE") or "").lower()).strip()
    if t and not _ign(r.get("PUBLISHED_AT")):
        return "SEM_DOI:%s|%s" % (t, r.get("PUBLISHED_AT"))
    return None


def _cheios(r: dict) -> int:
    return sum(1 for v in r.values() if not _ign(v) and v not in ([], {}, False))


def duplicados_da_ciencia(lista: list, regs: dict) -> dict:
    """-> {ACERVO_ID descartado: (ACERVO_ID que fica, chave, cheios_fica, cheios_sai)}."""
    grupos = {}
    for x in lista:
        if _colecao(x) not in COLECOES_DE_CIENCIA:
            continue
        k = _chave_do_estudo(x, regs[x["ACERVO_ID"]])
        if k:
            grupos.setdefault(k, []).append(x["ACERVO_ID"])
    sai = {}
    for k, ids in grupos.items():
        if len(ids) < 2:
            continue
        if k.startswith("SEM_DOI:") and len({i.split("::")[1] for i in ids}) < 2:
            continue   # sem DOI, so a mesma copia nas DUAS listas
        ordem = sorted(ids, key=lambda i: (-_cheios(regs[i]), i.split("::")[1] != "scienceCorpus", i))
        fica = ordem[0]
        for i in ordem[1:]:
            sai[i] = (fica, k, _cheios(regs[fica]), _cheios(regs[i]))
    return sai


def nomeia_palavra_da_collection(item: dict) -> list:
    escopo = json.dumps({"ITEM_ID": item.get("ITEM_ID"), "SOURCE_ID": item.get("SOURCE_ID"),
                         "UNIVERSO": item.get("UNIVERSO")}, ensure_ascii=False).upper()
    return [p for p in CI.PALAVRAS_QUE_O_REQUISITO_RECUSA if p in escopo]


def correr(entrada=ENTRADA, origem=ORIGEM, hoje: date = HOJE, source_head=NAO_SEI, referencia=None) -> dict:
    e, regs = ler_entrada(Path(entrada), Path(origem))
    sha = e["ORIGEM"]["SHA256"]
    itens, raw, como, fora_da_corrida, duplicados = [], {}, {}, [], []
    dup = duplicados_da_ciencia(e["LISTA"], regs)
    for x in e["LISTA"]:
        if x["ACERVO_ID"] in dup:
            fica, k, cf, cs = dup[x["ACERVO_ID"]]
            duplicados.append({"ITEM_ID": x["ACERVO_ID"], "TIPO": x["TIPO"], "FICA": fica, "CHAVE": k,
                               "MOTIVO": "DUPLICADO_DO_MESMO_ESTUDO",
                               "DETALHE": DUPLICADO_PORQUE % (k, fica, cf, cs)})
            continue
        it, rw, cm = ready(x, regs[x["ACERVO_ID"]], sha)
        sujo = nomeia_palavra_da_collection(it)
        if sujo:
            fora_da_corrida.append({"ITEM_ID": x["ACERVO_ID"], "TIPO": x["TIPO"], "SOURCE_ID": it["SOURCE_ID"],
                                    "MOTIVO": "NAO_ENTRA_NA_CORRIDA_G0",
                                    "DETALHE": FORA_DA_CORRIDA_PORQUE % ", ".join(sujo)})
            continue
        itens.append({"READY": it})
        raw[it["RAW_OBSERVATION_ID"]] = rw
        como[x["ACERVO_ID"]] = cm
    entrada_motor = {"SCHEMA": MOTOR.CONTRATO_DA_ENTRADA, "SINTETICA": False,
                     "CORTE": "ENTRADA_INTELLIGENCE_ACERVO/v1 @ origem " + sha[:12],
                     "ORIGEM": str(Path(entrada).relative_to(RAIZ)) if Path(entrada).is_relative_to(RAIZ)
                     else str(entrada), "ITENS": itens, "RAW": raw}
    ref = referencia if referencia is not None else PORTA.abrir(hoje=hoje)
    livro = MOTOR.rodar(entrada_motor, hoje, source_head, referencia=ref)
    run_id = livro["INTELLIGENCE_RUN_ID"]
    ctx = {"RUN_ID": run_id, "RAW": raw, "REF": ref,   # REF: o motor liga cada objeto pela porta (D123)
           "READY": {x["READY"]["ITEM_ID"]: x["READY"] for x in itens},
           "LINHA": {str(l["ITEM_ID"]): l for l in livro["LINEAGE"]}}
    por_tipo = {}
    for x in e["LISTA"]:
        if x["ACERVO_ID"] in ctx["LINHA"]:          # o que ficou FORA_DA_CORRIDA nao tem LINEAGE
            por_tipo.setdefault(x["TIPO"], []).append(x)

    comp, n_comp, med_comp = concorrentes(por_tipo.get("anuncio", []), regs, ctx, ref)
    mkt, n_mkt = mercado(por_tipo.get("preco", []), regs, ctx)
    voz, n_voz, med_voz = vozes(por_tipo.get("voz", []) + por_tipo.get("transcricao", []), regs, ctx)
    objetos = livro["ITENS_POR_FERRAMENTA"]
    for comp_name in ("windows", "science", "future"):
        for o in objetos.get(comp_name) or []:
            _com_id_provisorio(o)
    objetos.update({"competitors": comp, "market": mkt, "voices": voz})
    # o rendimento conta sobre TODOS os objetos desta corrida (a funcao e a do motor)
    fontes, sem_rend = MOTOR._rendimentos(livro["CORRIDA"], ctx, {k: v for k, v in objetos.items()
                                                                  if k != "sources"})
    for o in fontes:
        _com_id_provisorio(o)
    objetos["sources"] = fontes
    livro["NAO_ENVIADOS_AO_POTE"] = ([n for n in livro["NAO_ENVIADOS_AO_POTE"]
                                      if n.get("COMPARTIMENTO") != "sources"]
                                     + sem_rend + n_comp + n_mkt + n_voz)

    ao_contrato_unico(objetos)
    # o Archivio so com o que atravessou — senao cada recusa contava duas vezes
    pote0 = PIC.adaptar(livro)
    passaram = {c: {o["OBJETO_ID"] for o in pote0["COMPARTIMENTOS"][c]["OBJETOS"]}
                for c in pote0["COMPARTIMENTOS"]}
    objetos["archive"] = arquivo({c: [o for o in objetos.get(c) or [] if o["OBJETO_ID"] in passaram.get(c, ())]
                                  for c in objetos})
    livro["CAPACIDADES_EXECUTADAS"].update({
        "CAP-COMP": {"VIA": CAPACIDADE_DO_TIPO["anuncio"], "RUN": run_id, "MEDIDA": med_comp},
        "CAP-MKT": {"VIA": CAPACIDADE_DO_TIPO["preco"], "RUN": run_id},
        "CAP-FIELD": {"VIA": CAPACIDADE_DO_TIPO["voz"], "REGRA": VOZ.REGRA, "RUN": run_id, "MEDIDA": med_voz}})
    livro["ACERVO"] = {
        "CONTRATO": CONTRATO, "MARCA": MARCA, "NAO_PARA_CLIENTE": True, "NAO_VAI_AO_CASCO": True,
        "ENTRADA": "docs/intelligence/acervo/ENTRADA-INTELLIGENCE-ACERVO.json",
        "ORIGEM": {"FICHEIRO": "italia-portale/client/italy-handoff-v21.js", "SHA256": sha,
                   "COMMIT_DA_ORIGEM": COMMIT_DA_ORIGEM,
                   "LIMITE_SUPERIOR_DA_CAPTURA": LIMITE_SUPERIOR_DA_CAPTURA},
        "HOJE": hoje.isoformat(),
        "ID_ESTADO": ID_ESTADO, "ID_ESTADO_PORQUE": ID_ESTADO_PORQUE,
        "COMPOSTO_DE": "NAO USADO — nao existe no contrato POTE_INTELLIGENCE_CASCO/v2",
        "REGRA_DO_TEMPO": REGRA_DO_TEMPO, "CAMPO_DA_PUBLICACAO": CAMPO_DA_PUBLICACAO,
        "CAPACIDADE_DO_TIPO": CAPACIDADE_DO_TIPO,
        "CAPTURA_POR_ITEM": como,
        "FORA_DA_CORRIDA": fora_da_corrida,
        "DUPLICADOS": duplicados,
        # o lugar que cada READY levou, onde nao e NAO SEI: a prova de que a fonte ficou no campo dela
        "LUGAR_POR_ITEM": {x["READY"]["ITEM_ID"]: {c: x["READY"][c] for c in
                                                   ("SOURCE_LOCATION", "SOURCE_LOCATION_BASIS", "FACT_LOCATION")}
                           for x in itens if x["READY"]["SOURCE_LOCATION"] != NAO_SEI
                           or x["READY"]["FACT_LOCATION"] != NAO_SEI},
        "D112": "FACT_LOCATION do READY = NAO SEI em todo item; lugar so do texto lido por capacidade",
    }
    livro = json.loads(json.dumps(livro, ensure_ascii=False, default=list))
    v = conferir(livro)
    if v:
        raise LeiViolada("livro do acervo reprovado: " + "; ".join(v[:10]))
    return livro


# ══════════════════════════════════════════════════════════════════════════
# 6 · O PORTAO DESTE ADAPTADOR — independente de `correr`
# ══════════════════════════════════════════════════════════════════════════
def conferir(livro: dict) -> list:
    """As leis que esta missao pede, lidas no livro como o pote o leria."""
    v = []
    objs = livro.get("ITENS_POR_FERRAMENTA") or {}
    for comp, os_ in objs.items():
        for o in os_:
            oid = o.get("OBJETO_ID")
            if o.get("ESPECIE") == "OPORTUNIDADE":
                v.append(f"{comp}/{oid}: o acervo nao produz OPORTUNIDADE (anuncio nao e oportunidade)")
            if (o.get("CHAVES") or {}).get("ID_ESTADO") != ID_ESTADO:
                v.append(f"{comp}/{oid}: ID sem a marca {ID_ESTADO} (D119)")
            if "COMPOSTO_DE" in o or "COMPOSTO_DE" in (o.get("CHAVES") or {}):
                v.append(f"{comp}/{oid}: COMPOSTO_DE nao existe no contrato")
            if "MUDANCA_DE_MERCADO" in o or "MUDANCA_DE_MERCADO" in (o.get("CHAVES") or {}):
                v.append(f"{comp}/{oid}: mudanca de mercado afirmada pelo adaptador")
            ls = o.get("LOCATION_SOURCE")
            if ls is not None and PIC.normal(ls) in PIC.LOCATION_SOURCE_PROIBIDA:
                v.append(f"{comp}/{oid}: o lugar da fonte virou o lugar do facto")
            ch = o.get("CHAVES") or {}
            if comp != "archive":
                porch = ch.get("ENTITY_SOURCE_POR_CHAVE")
                if not isinstance(porch, dict):
                    v.append(f"{comp}/{oid}: sem ENTITY_SOURCE_POR_CHAVE (D112b)")
                else:
                    for k in PIC.COMPARTIMENTOS[comp]["CHAVES"] or ():
                        e = porch.get(k)
                        if not isinstance(e, dict) or e.get("VALOR") != ch.get(k):
                            v.append(f"{comp}/{oid}: {k} sem procedencia que bata com o valor")
                        elif ch.get(k) != NAO_SEI and _ign(e.get("ENTITY_SOURCE")):
                            v.append(f"{comp}/{oid}: {k} com valor e sem procedencia (D112b)")
            for p in o.get("PROVA") or []:
                for k in ("URL", "PUBLISHED_AT", "COLHIDO_EM", "FACT_TIME"):
                    if k not in p:
                        v.append(f"{comp}/{oid}: prova sem {k}")
    if objs.get("meeting"):
        v.append("meeting: o acervo nao alimenta o Radar delle Opportunita")
    for c in ("competitors",):
        for o in objs.get(c) or []:
            if o.get("ESPECIE") != "SINAL":
                v.append(f"{c}/{o.get('OBJETO_ID')}: concorrente so como SINAL")
            if (o.get("CHAVES") or {}).get("CROP_ID") != NAO_SEI:
                v.append(f"{c}/{o.get('OBJETO_ID')}: cultura do anuncio afirmada")
    for o in objs.get("market") or []:
        s = o.get("SERIE")
        if s is not None and PIC.ler_serie(o)[0] != PIC.SERIE_MEDIDA:
            v.append(f"market/{o.get('OBJETO_ID')}: SERIE que nao e serie medida")
    return v


def gerar(livro: dict) -> tuple:
    """-> (pote, violacoes do validador, resumo)."""
    pote = PIC.adaptar(livro)
    viol = VALIDAR.validar(pote)
    return pote, viol, resumo(livro, pote)


def resumo(livro: dict, pote: dict) -> dict:
    """Por tipo: entraram, viraram objeto, recusados e porque — contado do livro e do pote."""
    lin = {str(l["ITEM_ID"]): l for l in livro["LINEAGE"]}
    tipo_de = {iid: iid.split("::")[1] for iid in lin}
    no_pote = {}
    for comp, e in pote["COMPARTIMENTOS"].items():
        if comp in ("archive", "sources"):
            continue
        for o in e["OBJETOS"]:
            for p in o["PROVA"]:
                no_pote.setdefault(p["ITEM_ID"], set()).add(comp)
    recusas_pote = {}
    for r in pote["RECUSADOS"]:
        recusas_pote.setdefault(r["MOTIVO"], 0)
        recusas_pote[r["MOTIVO"]] += 1
    tipos = {}
    ent = json.loads(ENTRADA.read_text(encoding="utf-8"))
    for x in ent["LISTA"]:
        t = tipos.setdefault(x["TIPO"], {"ENTRARAM": 0, "G0_PASSOU": 0, "VIRARAM_OBJETO": 0,
                                         "RECUSADOS": 0, "PORQUE": {}})
        t["ENTRARAM"] += 1
        if x["ACERVO_ID"] not in lin:
            t["RECUSADOS"] += 1
            dups = {d["ITEM_ID"] for d in (livro.get("ACERVO") or {}).get("DUPLICADOS") or []}
            m = ("DUPLICADO_DO_MESMO_ESTUDO (fica a melhor copia)" if x["ACERVO_ID"] in dups
                 else "NAO_ENTRA_NA_CORRIDA_G0 (SOURCE_ID com palavra da Collection)")
            t["PORQUE"][m] = t["PORQUE"].get(m, 0) + 1
            continue
        l = lin[x["ACERVO_ID"]]
        if l.get("G0") == "PASSOU":
            t["G0_PASSOU"] += 1
        if x["ACERVO_ID"] in no_pote:
            t["VIRARAM_OBJETO"] += 1
        else:
            t["RECUSADOS"] += 1
            motivo = ("G0: " + "+".join(l.get("G0_FALTA") or [])) if l.get("G0") != "PASSOU" else None
            if motivo is None:
                ns = [n for n in livro["NAO_ENVIADOS_AO_POTE"] if n.get("ITEM_ID") == x["ACERVO_ID"]]
                pr = [r for r in pote["RECUSADOS"] if r.get("OBJETO_ID") in
                      {o["OBJETO_ID"] for c in livro["ITENS_POR_FERRAMENTA"].values() for o in c
                       if any(p["ITEM_ID"] == x["ACERVO_ID"] for p in o["PROVA"])}]
                motivo = (ns[0]["MOTIVO"] if ns else pr[0]["MOTIVO"] + (": " + pr[0]["DETALHE"][:60])
                          if pr else "SEM_OBJETO_DA_CAPACIDADE")
            t["PORQUE"][motivo] = t["PORQUE"].get(motivo, 0) + 1
    return {
        "SCHEMA": "RESUMO_ACERVO_NA_INTELLIGENCE/v1", "MARCA": MARCA,
        "INTELLIGENCE_RUN_ID": livro["INTELLIGENCE_RUN_ID"],
        "SOURCE_HEAD": livro["SOURCE_HEAD"],
        "POR_TIPO": dict(sorted(tipos.items())),
        "POTE_POR_COMPARTIMENTO": {c: {"OBJETOS": len(e["OBJETOS"]), "RECUSADOS_AQUI": e["RECUSADOS_AQUI"],
                                       "ESTADO": e["ESTADO"], "PORQUE_VAZIO": e.get("PORQUE_VAZIO")}
                                   for c, e in pote["COMPARTIMENTOS"].items()},
        "RECUSADOS_NO_POTE_POR_MOTIVO": dict(sorted(recusas_pote.items())),
        "NAO_ENVIADOS_AO_POTE_POR_MOTIVO": _contar(n["MOTIVO"] for n in livro["NAO_ENVIADOS_AO_POTE"]),
        "CAP_SCI": {"JULGADOS": livro["CAP_SCI"]["UNIVERSO"]["JULGADOS"],
                    "FORA": livro["CAP_SCI"]["UNIVERSO"]["FORA"],
                    "TENTATIVAS_DE_LIGACAO_AO_ROTULO": livro["CAP_SCI"]["TENTATIVAS_DE_LIGACAO"],
                    "LIGACOES_PARTIAL_OU_CANDIDATE": len(livro["CAP_SCI"]["LIGACOES"]),
                    "APLICABILIDADE": _contar(e["APLICABILIDADE"]["ESTADO"] for e in livro["CAP_SCI"]["ESTUDOS"])},
        "CAP_WIN": {"JANELAS": len(livro["CAP_WIN"]["CROP_WINDOWS"])},
        "CAPACIDADES_EXECUTADAS": livro["CAPACIDADES_EXECUTADAS"],
        "REFERENCIA_ADAMA": {k: livro["REFERENCIA_ADAMA"].get(k) for k in
                             ("EDICAO_REGISTRO", "DATA_DA_EDICAO_REGISTRO", "ULTIMA_CHECAGEM_OK",
                              "DIAS_SEM_CHECAGEM", "ESTADO_FRESCOR", "EDICAO_CATALOGO")},
    }


def _contar(xs) -> dict:
    out = {}
    for x in xs:
        out[x] = out.get(x, 0) + 1
    return dict(sorted(out.items()))


def _escrever(p: Path, dado) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(dado, ensure_ascii=False, indent=1, sort_keys=False) + "\n", encoding="utf-8")


def _sem_relogio(livro: dict) -> dict:
    """O livro sem o relogio da corrida (START/END): o resto e deterministico."""
    c = livro.get("CORRIDA") or {}
    for k in ("START", "END"):
        if k in c:
            c[k] = "NAO_GRAVADO (relogio da corrida; o livro commitado nao carrega a hora)"
    return livro


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="o acervo pelas capacidades da Intelligence -> pote v2")
    ap.add_argument("--conferir", action="store_true", help="regera em memoria e compara com o commitado")
    ap.add_argument("--source-head", default=None)
    ap.add_argument("--livro", default=None, help="onde escrever o livro inteiro (~20 MB; nao se commita: "
                                                 "regera-se deterministicamente)")
    a = ap.parse_args(argv)
    livro = _sem_relogio(correr(source_head=a.source_head or _source_head()))
    pote, viol, res = gerar(livro)
    if viol:
        print("POTE REPROVADO no validar_pote_v2:\n  " + "\n  ".join(viol[:20]), file=sys.stderr)
        return 1
    if a.conferir:
        antigo = json.loads(POTE_SAIDA.read_text(encoding="utf-8"))
        iguais = {k: antigo.get(k) == pote.get(k) for k in pote if k not in ("SOURCE_HEAD",)}
        print("POTE commitado == regerado:", all(iguais.values()))
        return 0 if all(iguais.values()) else 1
    if a.livro:
        _escrever(Path(a.livro), livro)
    _escrever(POTE_SAIDA, pote)
    _escrever(RESUMO_SAIDA, res)
    n = {c: len(e["OBJETOS"]) for c, e in pote["COMPARTIMENTOS"].items()}
    print(f"{MARCA} · corrida {pote['INTELLIGENCE_RUN_ID']} · objetos {n} · recusados "
          f"{len(pote['RECUSADOS'])} · validar_pote_v2 PASSA")
    return 0


if __name__ == "__main__":
    sys.exit(main())
