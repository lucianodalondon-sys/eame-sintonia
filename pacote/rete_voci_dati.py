#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""RETE-VOCI-DATI — o dado JA COLETADO que esta no repositorio, no contrato do pote v2.

    MISSAO   nuvem-rete-voci-dati-v1 (D114: o portal hoje com o maximo de informacao)
    ESPECIE  ADAPTADOR DE ENTREGA (Z-PACOTE). NAO E MOTOR. NAO E TELA. NAO VAI A REDE.
    CONTRATO ENTRADA_EXTRA_POTE/v1  ->  juntada a corrida da rodada  ->  POTE_INTELLIGENCE_CASCO/v2

    python3 pacote/rete_voci_dati.py                                   # resumo por compartimento
    python3 pacote/rete_voci_dati.py --saida ENTRADA-EXTRA.json        # a entrada extra
    python3 pacote/rete_voci_dati.py --saida X.json --juntar ENTRADA-DA-PONTE-Rn.json \\
                                     --pote italia-portale/client/sintonia-pote.js
    python3 -m unittest tests.test_rete_voci_dati -v

A PERGUNTA QUE ESTE FICHEIRO RESPONDE, E MAIS NENHUMA
-----------------------------------------------------
    DO QUE A CASA JA COLHEU E GUARDOU NO REPOSITORIO, O QUE CADA GAVETA DO POTE
    (voices, competitors, market, science, sources, archive) PODE MOSTRAR — COM
    PROVA ATE AO REGISTO, E NAO SEI ONDE O REGISTO NAO DIZ?

O raio-X do casco mostrou gavetas com PORQUE_VAZIO e a Rete Commerciale simulada,
enquanto o lote 4 ja tinha no repositorio as vozes, os precos ISMEA, os anuncios
da Meta de 31/08, os trabalhos T6 e a lista do MUR. Este ficheiro NAO colhe: le
esses ficheiros rastreados e devolve UMA ENTRADA-EXTRA no formato do livro de
corrida que `pacote/pote_intelligence_casco.adaptar` ja le (LINEAGE +
ITENS_POR_FERRAMENTA + GAPS). O coordenador junta-a a corrida da rodada
(`juntar`) e o pote sai pelo gerador de sempre, com a conferencia de sempre.

AS REGRAS, EM CODIGO
--------------------
  · PROVA ate ao registo: cada objeto leva ITEM_ID -> RAW_OBSERVATION_ID
    (<ficheiro>#<registo>) -> SOURCE_ID -> DOCUMENT_ID, com URL, PUBLICADO_EM e
    COLHIDO_EM. O que o registo nao diz fica NAO SEI por extenso.
  · O PORTAO E O DA INTELLIGENCE: cada item passa por `portao_g0` do motor
    (quem, de onde, quando). O que ele bloqueia nao vira objeto: vira lacuna
    contada (GAPS), com o motivo.
  · CAPTURA: COLHIDO_EM so e escrito quando o ficheiro o diz. Quando nao diz, o
    G0 recebe o LIMITE INFERIOR PROVADO da captura — a publicacao (nada se colhe
    antes de publicado). Isso so pode BLOQUEAR a mais, nunca deixar passar um
    facto futuro: se o facto comeca ate a publicacao, comeca ate a captura.
  · MARCA DO TIPO: TIPO_DO_DADO em cada objeto — FATO (uma observacao),
    SINAL (uma voz), SERIE (>= 2 pontos, mesma chave e MESMA UNIDADE),
    CONTAGEM (um numero contado sobre um conjunto dito).
  · META ADS: «observado em 31/08/2026», nunca «hoje»; o estado ATIVO/INATIVO e
    o da observacao.
  · PUBLICACAO NAO VIRA TEMPO DO FACTO — excepto quando o facto E a publicacao
    (um trabalho cientifico publicado, um video publicado), e isso fica escrito
    em FACT_TIME_BASIS. O periodo do estudo continua STUDY_PERIOD, como veio.
  · SEM DADO PESSOAL alem do publico e institucional: nome e cargo publico de
    pesquisador sim (MUR, autoria); contacto nunca; nome de pessoa privada
    (agricultor, comentador) nunca — so o papel. Nenhum texto integral de
    artigo: titulo sim, resumo nao.
  · SOURCE_ID vem do registo ou do Atlas (`curadoria/emparelhar_com_atlas`),
    nunca da URL. Sem Atlas, NAO SEI — e G0 bloqueia.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
from collections import Counter, OrderedDict
from pathlib import Path

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))   # a raiz
import _gavetas  # noqa: E402,F401 — poe as gavetas do processo no caminho
# O emparelhador do Atlas vive em curadoria/ (nao e gaveta): o SOURCE_ID vem de
# quem o tem, e nunca da URL.
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "curadoria"))

from corrida_da_inteligencia import portao_g0, e_ignorancia     # noqa: E402
from espinha_da_intelligence import NAO_SEI                     # noqa: E402
import grafo_de_dependencia as GRAFO                            # noqa: E402
import preco_de_mercado as PRECO                                # noqa: E402
import emparelhar_com_atlas as ATLAS                            # noqa: E402
import pote_intelligence_casco as POTE                          # noqa: E402

CONTRATO = "ENTRADA_EXTRA_POTE/v1"
RAIZ = Path(os.path.dirname(HERE))
ESTADO = "EXPERIMENTAL_CANDIDATE"
FATO, SINAL_T, SERIE, CONTAGEM = "FATO", "SINAL", "SERIE", "CONTAGEM"
TIPOS_DO_DADO = (FATO, SINAL_T, SERIE, CONTAGEM)
GERAIS = ("voices", "competitors", "market", "science")
COMPARTIMENTOS = GERAIS + ("sources", "archive")
PROVA_MAX_RENDIMENTO = 3
TEXTO_MAX = 280

#: Os ficheiros lidos — todos rastreados no Git. Nada e colhido aqui.
_H = "build/ITALY-REALITY-HANDOFF-V2/"
FICHEIROS = OrderedDict([
    ("VOZES", _H + "PUBLIC-VOICES.json"),
    ("MERCADO_CURADO", _H + "MARKET-OBSERVATIONS.json"),
    ("EU_CEREAIS", "data/samples/IT-MERCADO/EU-AGRIFOOD-cereal-prices-IT.json"),
    ("EU_AZEITE", "data/samples/IT-MERCADO/EU-AGRIFOOD-oliveOil-prices-IT.json"),
    ("EU_VINHO", "data/samples/IT-MERCADO/EU-AGRIFOOD-wine-prices-IT.json"),
    ("CONCORRENCIA", _H + "PREVIOUS-HANDOFF/01-DESIGN-READY/COMPETITOR-WATCH/competitor-activities.json"),
    ("META_S1_31_08", "tests/dados/concorrencia_meta/SNAPSHOT-S1-IT-31-08.json"),
    ("SINAIS_CONCORRENCIA", _H + "COMPETITOR-PUBLIC-SIGNALS.json"),
    ("T6_TRABALHOS", "data/derivados/PESQUISADORES-T6/ENSAIO-OFFLINE.json"),
    ("T6_POR_EVIDENCIA", "data/derivados/T6-PARA-SALA/POR-EVIDENCIA.json"),
    ("CORPUS_PESQUISADOR", "data/samples/RESEARCHER-CORPUS-EAME-V1.json"),
    ("MUR", "data/derivados/LISTA-MESTRA/CRUZAMENTO-MUR-AGRI05.json"),
])

#: Papeis de voz que NAO sao voz (o registo diz que a leitura falhou).
NAO_E_VOZ = ("ACESSO_DE_FONTE",)
#: Sinais de concorrencia que descrevem o canal, nao um facto da empresa.
NAO_E_SINAL_DE_CONCORRENCIA = ("ESTRUTURA_DE_CANAL", "LEITURA_VAZIA")
#: Paginas da Meta que nao sao agro (medido: «FMC Moto Srl» vende motos).
PAGINAS_FORA_DO_AGRO = {"101167338588947": "FMC Moto Srl vende motocicletas; nao e a FMC agro"}
#: A prova de pessoa que o corpus aceita como forte (a sua EVIDENCE_RULE).
PROVA_FORTE_DE_PESSOA = ("ORCID_SELF_DECLARED", "AFFILIATION_ON_WORK")
#: Cultura dita pelo PROPRIO dataset (o dataset e so disto). Cereais nao: o codigo
#: de produto nao e cultura, e traduzi-lo seria inventar.
CULTURA_DO_DATASET = {"EU_AZEITE": "OLIVO", "EU_VINHO": "VITE"}

_DIA = re.compile(r"(?<!\d)(\d{4})-(\d{2})-(\d{2})(?!\d)")
_DMY = re.compile(r"(?<!\d)(\d{2})/(\d{2})/(\d{4})(?!\d)")


class LeiViolada(Exception):
    """A entrada extra recusou-se, e diz porque."""


# ── pequenas regras ──────────────────────────────────────────────────────────
def _v(x):
    """O valor como veio, ou NAO SEI por extenso."""
    if isinstance(x, (list, tuple)):
        x = [str(i) for i in x if not e_ignorancia(i)]
        return "; ".join(x) if x else NAO_SEI
    return NAO_SEI if e_ignorancia(x) else x


def _iso(s):
    """Uma data ISO (AAAA-MM-DD) escrita no valor, ou None. dd/mm/aaaa tambem."""
    if not isinstance(s, str):
        return None
    m = _DIA.search(s)
    if m:
        return "-".join(m.groups())
    m = _DMY.search(s)
    return f"{m.group(3)}-{m.group(2)}-{m.group(1)}" if m else None


def _publicacao(s):
    """`(publicado_em, colhido_em)` de um `publication_date` curado.

    O curador escreveu `2026-09-02 (lido nesta data; ...)` quando a fonte nao
    data a publicacao: isso e o dia da LEITURA, nao da publicacao. Texto que nao
    comeca por uma data (`NAO_SEI — ...`) nao e data nenhuma."""
    if not isinstance(s, str) or not re.match(r"^\d{4}-\d{2}-\d{2}", s.strip()):
        return NAO_SEI, NAO_SEI
    d = s.strip()[:10]
    return (NAO_SEI, d) if "lido nesta data" in s else (d, NAO_SEI)


def _curto(s, n=TEXTO_MAX):
    s = re.sub(r"\s+", " ", str(s or "")).strip()
    return s if len(s) <= n else s[:n - 1].rstrip() + "…"


def _blob(raiz: Path, rel: str) -> str:
    """O SHA do blob como o Git o calcula — prova de QUE versao do ficheiro se leu."""
    b = (raiz / rel).read_bytes()
    return hashlib.sha1(b"blob %d\0" % len(b) + b).hexdigest()


def _ler(raiz: Path, rel: str):
    return json.loads((raiz / rel).read_text(encoding="utf-8"))


# ── o livro que a entrada extra monta ────────────────────────────────────────
class Livro:
    """LINEAGE + ITENS_POR_FERRAMENTA + GAPS, acumulados por registo lido."""

    def __init__(self, raiz: Path):
        self.raiz = raiz
        self.blobs = {k: _blob(raiz, rel) for k, rel in FICHEIROS.items()}
        self.linhagem, self.gaps, self.recusados_aqui = [], [], []
        self.itens = {c: [] for c in COMPARTIMENTOS}
        self.lidos = []          # (comp, SOURCE_ID, passou, prova)
        self.ids = set()
        self.pontos = []         # pontos de preco para as series

    def item(self, comp, chave, registo, *, source_id, document_id, url, publicado,
             colhido, fact_time, base, captura_g0=None, base_captura=None):
        """Regista um registo lido: G0 do motor decide. Devolve a prova, ou None."""
        rid = f"RVD:{chave}:{registo}"
        item = {"ITEM_ID": rid, "SOURCE_ID": _v(source_id),
                "RAW_OBSERVATION_ID": f"{FICHEIROS[chave]}#{registo}",
                "FACT_TIME": _v(fact_time), "FACT_TIME_BASIS": _v(base),
                "CAPTURED_AT": _v(colhido) if not e_ignorancia(colhido) else _v(captura_g0)}
        passou, falta = portao_g0(item)
        up = f"RETE-VOCI-DATI/{chave}@{self.blobs[chave][:12]}"
        entrada = {"ITEM_ID": rid, "CORRIDA_UPSTREAM": up,
                   "RAW_OBSERVATION_ID": item["RAW_OBSERVATION_ID"], "SOURCE_ID": item["SOURCE_ID"],
                   "G0": "PASSOU" if passou else "BLOQUEADO_EM_G0", "G0_FALTA": sorted(falta),
                   "URL": _v(url), "PUBLICADO_EM": _v(publicado), "COLHIDO_EM": _v(colhido),
                   "FACT_TIME": item["FACT_TIME"], "FACT_TIME_BASIS": item["FACT_TIME_BASIS"],
                   "CAPTURA_PARA_G0": ("COLHIDO_EM" if not e_ignorancia(colhido) else
                                       (base_captura or NAO_SEI) if not e_ignorancia(captura_g0) else NAO_SEI)}
        self.linhagem.append(entrada)
        prova = None
        if passou:
            prova = {"ITEM_ID": rid, "CORRIDA_UPSTREAM": up,
                     "RAW_OBSERVATION_ID": entrada["RAW_OBSERVATION_ID"],
                     "SOURCE_ID": entrada["SOURCE_ID"], "DOCUMENT_ID": _v(document_id),
                     "URL": entrada["URL"], "PUBLICADO_EM": entrada["PUBLICADO_EM"],
                     "COLHIDO_EM": entrada["COLHIDO_EM"], "FACT_TIME": entrada["FACT_TIME"]}
        else:
            self.gaps.append({"FERRAMENTA": comp, "FONTE": chave, "ITEM_ID": rid,
                              "SOURCE_ID": entrada["SOURCE_ID"], "MOTIVO": "BLOQUEADO_EM_G0",
                              "G0_FALTA": entrada["G0_FALTA"]})
        self.lidos.append((comp, entrada["SOURCE_ID"], passou, prova))
        return prova

    def recusa(self, comp, chave, registo, motivo):
        """Registo lido que o adaptador nao leva — contado, nunca escondido."""
        self.recusados_aqui.append({"COMPARTIMENTO": comp, "FONTE": chave,
                                    "REGISTO": str(registo), "MOTIVO": motivo})

    def objeto(self, comp, oid, tipo, chaves, prova, porque, incerteza=None, especie="SINAL"):
        if tipo not in TIPOS_DO_DADO:
            raise LeiViolada(f"TIPO_DO_DADO {tipo!r} nao e {TIPOS_DO_DADO}")
        if oid in self.ids:
            raise LeiViolada(f"OBJETO_ID repetido: {oid}")
        self.ids.add(oid)
        c = dict(chaves)
        c["TIPO_DO_DADO"] = tipo
        c["ORIGEM"] = "ENTRADA_EXTRA rete_voci_dati (dado ja coletado no repositorio; nao e corrida da Intelligence)"
        o = {"OBJETO_ID": oid, "ESPECIE": especie, "ESTADO": ESTADO, "CHAVES": c,
             "PROVA": prova if isinstance(prova, list) else [prova],
             "PORQUE": porque, "INCERTEZA": _v(incerteza)}
        self.itens[comp].append(o)
        return o


# ── VOICES — Voci dal Campo ──────────────────────────────────────────────────
def _lugar(s):
    """`NAO DECLARADA no artigo` e ignorancia escrita por extenso."""
    if e_ignorancia(s) or str(s).strip().upper().startswith(("NAO ", "NÃO ")):
        return NAO_SEI
    return s


def vozes(L: Livro):
    d = _ler(L.raiz, FICHEIROS["VOZES"])
    for r in d["RECORDS"]:
        rid = r["CANONICAL_RECORD_ID"]
        if str(r.get("tipo", "")).startswith(NAO_E_VOZ):
            L.recusa("voices", "VOZES", rid, "NAO_E_VOZ: o registo diz que a leitura da fonte falhou")
            continue
        sid = _source_id_do_atlas(L, r.get("source_url"))
        pub, col = _publicacao(r.get("publication_date"))
        prova = L.item("voices", "VOZES", rid, source_id=sid, document_id=r.get("source_url"),
                       url=r.get("source_url"), publicado=pub, colhido=col,
                       fact_time=r.get("periodo"), base="periodo declarado pelo curador no registo (PUBLIC-VOICES)",
                       captura_g0=pub, base_captura="LIMITE_INFERIOR=PUBLICADO_EM")
        if not prova:
            continue
        L.objeto("voices", f"RVD-VOZ-{rid}", SINAL_T, {
            # A pessoa NAO viaja: o registo curado so a descreve em texto livre,
            # e algumas sao privadas (um agricultor de Ferrara). So o papel.
            "SPEAKER_ID": NAO_SEI, "SPEAKER_ROLE": _v(r.get("tipo")),
            "QUOTE_OR_TRANSCRIPT": _v(r.get("citacao_literal")), "CROP_ID": _v(r.get("crop")),
            "ISSUE_ID": NAO_SEI, "FACT_LOCATION": _lugar(r.get("region")), "FACT_TIME": _v(r.get("periodo")),
            "FONTE_NOME": _v(r.get("source_name")), "CLASSE_DA_OBSERVACAO": _v(r.get("observation_class")),
            "QA_STATUS": _v(r.get("QA_STATUS")), "PESSOA": "nao transportada: so o papel publico",
        }, prova, porque=_porque_da_voz(r), incerteza=_qa(r))


#: Papeis de PESSOA PRIVADA: o texto livre do curador descreve-a (nome, terra) e
#: por isso nao viaja — so o papel e a citacao.
PAPEL_PRIVADO = ("AGRICULTOR",)


def _porque_da_voz(r):
    if any(p in str(r.get("tipo", "")).upper() for p in PAPEL_PRIVADO):
        return "voz de agricultor publicada em artigo; a pessoa nao e transportada (pessoa privada)"
    return _v(r.get("o_que_prova"))


def _qa(r):
    q = r.get("QA_STATUS")
    if q in ("QA_PASS", "QA_CORRECTED"):
        return f"{q}; nao prova: {_curto(r.get('o_que_nao_prova'), 200)}"
    return f"{_v(q)}: sem revisao, nao sustenta conclusao sozinho; nao prova: {_curto(r.get('o_que_nao_prova'), 200)}"


_ATLAS_CACHE = {}


#: O registo-mestre italiano ja numerado (54 fontes com SOURCE_ID, p.ex.
#: IT-T10-001 = ismeamercati.it). O Atlas e os contratos do Curator mandam; o
#: mestre so entra para SOURCE_ID que eles nao tem.
MESTRE_ITALIANO = "candidatas/ITALY-SOURCE-MASTER-V1.json"


def _identidades(raiz: Path) -> list:
    fichas = ATLAS.identidades_conhecidas(do_disco=True)
    vistos = {f["SOURCE_ID"] for f in fichas}
    for f in _ler(raiz, MESTRE_ITALIANO).get("sources") or []:
        if f.get("SOURCE_ID") and f["SOURCE_ID"] not in vistos and ATLAS.url_valida(f.get("URL", "")):
            fichas.append({"SOURCE_ID": f["SOURCE_ID"], "URL": f["URL"], "NAME": f.get("SOURCE_NAME", ""),
                           "OWNER": "", "NATIVE_ID": "", "TERRITORY": f.get("TERRITORY", ""),
                           "VERDICT": "REGISTO_MESTRE_ITALIANO"})
            vistos.add(f["SOURCE_ID"])
    return fichas


def _source_id_do_atlas(L: Livro, url):
    """SOURCE_ID do Atlas (disco) + contratos do Curator + registo-mestre.

    Fora de plataforma, o emparelhador casa pelo DOMINIO — e um dominio pode ter
    varias fichas (ec.europa.eu tem varias). Entao: as fichas do mesmo dominio;
    uma so -> essa; varias -> a de maior prefixo de caminho em comum (pelo menos
    um segmento); empate ou nenhum -> NAO SEI (ambiguo nao se escolhe). Em
    plataforma (YouTube, Facebook...) so casa por handle ou id nativo."""
    if e_ignorancia(url) or not ATLAS.url_valida(str(url)):
        return NAO_SEI
    raiz = str(L.raiz)
    if raiz not in _ATLAS_CACHE:
        _ATLAS_CACHE[raiz] = _identidades(L.raiz)
    fichas = _ATLAS_CACHE[raiz]
    dom = ATLAS.dominio(url)
    if dom and dom not in ATLAS.PLATAFORMAS:
        mesmas = [f for f in fichas if ATLAS.dominio(f["URL"]) == dom]
        if len({f["SOURCE_ID"] for f in mesmas}) == 1:
            return mesmas[0]["SOURCE_ID"]
        caminho = [x for x in re.sub(r"^https?://[^/]+", "", url).split("?")[0].split("/") if x]
        def comum(f):
            c = [x for x in re.sub(r"^https?://[^/]+", "", f["URL"]).split("?")[0].split("/") if x]
            n = 0
            while n < min(len(c), len(caminho)) and c[n] == caminho[n]:
                n += 1
            return n
        notas = sorted(((comum(f), f["SOURCE_ID"]) for f in mesmas), reverse=True)
        if notas and notas[0][0] >= 1 and (len(notas) == 1 or notas[1][0] < notas[0][0]):
            return notas[0][1]
        return NAO_SEI
    achados, _, _ = ATLAS.emparelhar([{"CANDIDATE_ID": "RVD", "URL": url}], fichas)
    return achados[0]["MATCHED_SOURCE_ID"] if achados else NAO_SEI


# ── COMPETITORS — Concorrenza ────────────────────────────────────────────────
def concorrencia(L: Livro):
    s1 = _ler(L.raiz, FICHEIROS["META_S1_31_08"])
    obs = {}
    for rec in s1["RECORTES"]:
        for a in rec.get("ads") or []:
            obs[str(a["library_id"])] = (rec["observed_at"], rec.get("completeness"))
    meta_sid = s1.get("SOURCE_ID")
    d = _ler(L.raiz, FICHEIROS["CONCORRENCIA"])
    for a in d["ACTIVITIES"]:
        if a.get("ACTIVITY_TYPE") == "PAID":
            _anuncio(L, a, obs, meta_sid)
        elif a.get("ACTIVITY_TYPE") == "ORGANIC_VIDEO":
            _video(L, a)
        else:
            L.recusa("competitors", "CONCORRENCIA", a.get("ID"), "TIPO_DE_ATIVIDADE_DESCONHECIDO")
    for r in _ler(L.raiz, FICHEIROS["SINAIS_CONCORRENCIA"])["RECORDS"]:
        _sinal_publico(L, r)


def _anuncio(L, a, obs, meta_sid):
    m = re.search(r"[?&]id=(\d+)", a.get("AD_URL") or "")
    lib = m.group(1) if m else None
    if str(a.get("PAGE_ID")) in PAGINAS_FORA_DO_AGRO:
        L.recusa("competitors", "CONCORRENCIA", a["ID"], "PAGINA_FORA_DO_AGRO: " + PAGINAS_FORA_DO_AGRO[str(a["PAGE_ID"])])
        return
    observado, completude = obs.get(lib, (NAO_SEI, NAO_SEI))
    dia_obs = _iso(observado)
    ini, fim = a.get("START_DATE"), a.get("END_DATE")
    if not e_ignorancia(fim):
        ft, base = f"{ini}/{fim}", "periodo de veiculacao declarado pela Biblioteca de Anuncios (inicio/fim)"
    elif a.get("ACTIVE_STATUS") == "ACTIVE" and dia_obs:
        ft, base = f"{ini}/{dia_obs}", "inicio declarado; ATIVO na observacao de " + dia_obs
    else:
        ft, base = ini, "inicio de veiculacao declarado pela Biblioteca de Anuncios; fim NAO SEI"
    prova = L.item("competitors", "CONCORRENCIA", a["ID"], source_id=meta_sid if lib in obs else NAO_SEI,
                   document_id=f"META_AD_LIBRARY:{lib}" if lib else None, url=a.get("AD_URL"),
                   publicado=ini, colhido=observado, fact_time=ft, base=base)
    if not prova:
        return
    estado = {"ACTIVE": "ATIVO", "INACTIVE": "INATIVO"}.get(a.get("ACTIVE_STATUS"), NAO_SEI)
    quando = f"observado em {dia_obs[8:10]}/{dia_obs[5:7]}/{dia_obs[:4]}" if dia_obs else NAO_SEI
    L.objeto("competitors", f"RVD-META-{lib}", FATO, {
        "COMPANY_ID": _v(a.get("COMPANY")), "PRODUCT_ID": _v(a.get("PRODUCTS_PROVED") or []),
        "CROP_ID": NAO_SEI, "FACT_LOCATION": NAO_SEI, "FACT_TIME": ft,
        "T4_REGISTRATION_EVIDENCE_ID": NAO_SEI,
        "OBSERVADO_EM": quando, "ESTADO_NA_OBSERVACAO": NAO_SEI if estado == NAO_SEI else f"{estado} ({quando}; nao e o estado de hoje)",
        "PAGINA": _v(a.get("PAGE")), "PAGE_ID": _v(a.get("PAGE_ID")), "PLATAFORMA": "META_ADS_LIBRARY",
        "PAIS_ALCANCADO": _v(a.get("COUNTRY_REACHED")),
        "PAIS_ALCANCADO_NAO_E": "pais-alvo nem lugar do facto (AD_REACHED_COUNTRY != AD_TARGETED_COUNTRY)",
        "TERMOS_DE_CULTURA": _v(a.get("CROP_TERMS") or []), "TERMOS_DE_PROBLEMA": _v(a.get("ISSUE_TERMS") or []),
        "MIDIA": _v(a.get("MEDIA_TYPE")), "TEXTO_DO_ANUNCIO": _curto(a.get("CREATIVE_TEXT")) or NAO_SEI,
        "COMPLETUDE_DO_RECORTE": _v(completude),
    }, prova, porque=f"anuncio pago da {a.get('COMPANY')} na Biblioteca de Anuncios da Meta, {quando}",
       incerteza="alcance em IT nao e alvo em IT; o estado e o da observacao, nao o de hoje")


def _video(L, a):
    pub = _iso(a.get("PUBLISHED_AT"))
    # O dataset diz IT-SRC-YOUTUBE: e a PLATAFORMA, nao a fonte (COL-LAW-034), e
    # nao esta no Atlas. O canal da empresa so tem SOURCE_ID se o Atlas o tiver.
    prova = L.item("competitors", "CONCORRENCIA", a["ID"], source_id=_source_id_do_atlas(L, a.get("URL")),
                   document_id=a.get("URL"), url=a.get("URL"), publicado=pub, colhido=NAO_SEI,
                   fact_time=pub, base="o facto e a propria publicacao do video no canal da empresa",
                   captura_g0=pub, base_captura="LIMITE_INFERIOR=PUBLICADO_EM")
    if not prova:
        return
    L.objeto("competitors", f"RVD-VIDEO-{a['ID']}", FATO, {
        "COMPANY_ID": _v(a.get("COMPANY")), "PRODUCT_ID": NAO_SEI, "CROP_ID": NAO_SEI,
        "FACT_LOCATION": NAO_SEI, "FACT_TIME": _v(pub), "T4_REGISTRATION_EVIDENCE_ID": NAO_SEI,
        "PLATAFORMA": _v(a.get("PLATFORM")), "CANAL": _v(a.get("CHANNEL")), "TITULO": _curto(a.get("TITLE")) or NAO_SEI,
    }, prova, porque=f"video publicado pela {a.get('COMPANY')} no proprio canal",
       incerteza="data da captura NAO SEI; visualizacoes nao transportadas (sem data da contagem)")


def _sinal_publico(L, r):
    rid = r["CANONICAL_RECORD_ID"]
    if str(r.get("tipo")) in NAO_E_SINAL_DE_CONCORRENCIA:
        L.recusa("competitors", "SINAIS_CONCORRENCIA", rid, f"NAO_E_FACTO_DA_EMPRESA: {r.get('tipo')}")
        return
    pub, col = _publicacao(r.get("publication_date"))
    prova = L.item("competitors", "SINAIS_CONCORRENCIA", rid, source_id=_source_id_do_atlas(L, r.get("source_url")),
                   document_id=r.get("source_url"), url=r.get("source_url"), publicado=pub, colhido=col,
                   fact_time=r.get("periodo"), base="periodo declarado pelo curador no registo",
                   captura_g0=pub, base_captura="LIMITE_INFERIOR=PUBLICADO_EM")
    if not prova:
        return
    L.objeto("competitors", f"RVD-COMUNICACAO-{rid}", FATO, {
        "COMPANY_ID": NAO_SEI, "PRODUCT_ID": NAO_SEI, "CROP_ID": _v(r.get("crop")),
        "FACT_LOCATION": _lugar(r.get("region")), "FACT_TIME": _v(r.get("periodo")),
        "T4_REGISTRATION_EVIDENCE_ID": NAO_SEI, "FONTE_NOME": _v(r.get("source_name")),
        "TIPO_DE_COMUNICACAO": _v(r.get("tipo")), "CITACAO": _v(r.get("citacao_literal")),
        "QA_STATUS": _v(r.get("QA_STATUS")),
    }, prova, porque=_v(r.get("o_que_prova")), incerteza=_qa(r))


# ── MARKET — Polso di Mercato ───────────────────────────────────────────────
def mercado(L: Livro):
    d = _ler(L.raiz, FICHEIROS["MERCADO_CURADO"])
    for r in d["RECORDS"]:
        if not str(r.get("source_name", "")).startswith("ISMEA") or str(r.get("tipo")).lower() != "preco":
            continue
        _ismea(L, r)
    for chave in ("EU_CEREAIS", "EU_AZEITE", "EU_VINHO"):
        _agrifood(L, chave)
    series(L)


def _ismea(L, r):
    """O texto literal que o curador copiou do ISMEA, lido pela regua da casa."""
    rid = r["CANONICAL_RECORD_ID"]
    lido = PRECO.precos_do_texto(r.get("citacao_literal") or "")
    if not lido["OBSERVACOES"]:
        L.recusa("market", "MERCADO_CURADO", rid, "SEM_PRECO_QUE_A_REGUA_LEIA: " +
                 "; ".join(sorted({x.get("PORQUE", "") for x in lido["RECUSADOS"]})) or "nenhum")
        return
    pub, col = _publicacao(r.get("publication_date"))
    for i, o in enumerate(lido["OBSERVACOES"], 1):
        periodo = o["PERIODO"] if not e_ignorancia(o["PERIODO"]) else r.get("periodo")
        base = ("periodo escrito no trecho do preco" if not e_ignorancia(o["PERIODO"])
                else "periodo declarado pelo curador no registo (o trecho nao o diz)")
        prova = L.item("market", "MERCADO_CURADO", f"{rid}/{i}", source_id=_source_id_do_atlas(L, r.get("source_url")),
                       document_id=r.get("source_url"), url=r.get("source_url"), publicado=pub, colhido=col,
                       fact_time=periodo, base=base, captura_g0=pub, base_captura="LIMITE_INFERIOR=PUBLICADO_EM")
        if not prova:
            continue
        preco = o["PRECO"] if o["PRECO"] is not None else NAO_SEI
        L.objeto("market", f"RVD-ISMEA-{rid}-{i}", FATO, {
            "CROP_ID": _v(o["CULTURA"]), "MARKET_PLACE_ID": _v(o["PRACA"]), "PERIOD": _v(periodo),
            "PRICE": preco, "UNIT": _v(o["UNIDADE"]), "MARKET_STAGE": _v(o["ESTAGIO"]),
            "MOEDA": _v(o["MOEDA"]), "TRECHO": _curto(o["TRECHO"], 200), "PERIODO_BASE": base,
            "LUGAR_DECLARADO_NO_REGISTO": _v(r.get("region")), "FONTE_NOME": _v(r.get("source_name")),
            "SERIE_CHAVE": _v(o["SERIE"]), "QA_STATUS": _v(r.get("QA_STATUS")),
        }, prova, porque="preco lido pela regua leis/preco_de_mercado.py no trecho que o curador copiou do ISMEA",
           incerteza=_qa(r))
        _ponto(L, o["CULTURA"], o["PRACA"], o["ESTAGIO"], o["UNIDADE"], periodo, preco, prova)


def _agrifood(L, chave):
    d = _ler(L.raiz, FICHEIROS[chave])
    col = _iso(d.get("CAPTURED_AT")) or NAO_SEI
    cultura = CULTURA_DO_DATASET.get(chave, NAO_SEI)
    for i, e in enumerate(d["LATEST_BY_PRODUCT_MARKET"], 1):
        ini, fim = _iso(e.get("BEGIN")), _iso(e.get("END"))
        ft = f"{ini}/{fim}" if ini and fim else NAO_SEI
        doc = f"{d['DATASET']}|{e.get('PRODUCT')}|{e.get('MARKET')}|{fim}"
        # REFERENCE_PERIOD da API nao diz se e publicacao: viaja como veio, e
        # PUBLICADO_EM fica NAO SEI.
        prova = L.item("market", chave, i, source_id=_source_id_do_atlas(L, d.get("source")), document_id=doc,
                       url=d.get("RESOLVED_URL"), publicado=NAO_SEI, colhido=col, fact_time=ft,
                       base="semana de referencia do preco (BEGIN/END) declarada pela API")
        if not prova:
            continue
        preco = e["PRICE_NUM"] if e.get("PRICE_NUM") is not None else NAO_SEI
        L.objeto("market", f"RVD-{chave}-{i}", FATO, {
            "CROP_ID": cultura, "MARKET_PLACE_ID": _v(e.get("MARKET")), "PERIOD": ft, "PRICE": preco,
            "UNIT": _v(e.get("UNIT")), "MARKET_STAGE": _v(e.get("STAGE")),
            "PRODUTO_DA_FONTE": _v(e.get("PRODUCT")), "PRECO_COMO_VEIO": _v(e.get("PRICE_RAW")),
            "REFERENCE_PERIOD_DA_API": _v(e.get("REFERENCE_PERIOD")),
            # O ficheiro declara EU-T10-002; o Atlas tem o Agri-food Data Portal
            # como EU-T10-001. O Atlas manda; a divergencia fica a vista.
            "SOURCE_ID_DECLARADO_NO_FICHEIRO": _v(d.get("SOURCE_ID")),
            "CULTURA_BASE": "o dataset e so desta cultura" if cultura != NAO_SEI else "codigo de produto nao e cultura",
            "FONTE_NOME": _v(d.get("SOURCE_NAME")), "IDADE": f"semana que acaba em {fim}; nao e o preco de hoje",
        }, prova, porque="ultimo preco da serie por produto e praca, na captura de " + col,
           incerteza="a captura guardou so o ultimo ponto e o de ha um ano; o ponto anterior (PREV) nao tem data e nao entra em serie")
        _ponto(L, cultura, e.get("MARKET"), e.get("STAGE") or NAO_SEI, e.get("UNIT"), ft, preco, prova,
               produto=e.get("PRODUCT"))
        if e.get("YEAR_AGO_PRICE_NUM") is not None and _iso(e.get("YEAR_AGO_END")):
            _ponto(L, cultura, e.get("MARKET"), e.get("STAGE") or NAO_SEI, e.get("UNIT"),
                   f"semana que acaba em {_iso(e['YEAR_AGO_END'])}", e["YEAR_AGO_PRICE_NUM"], prova,
                   fim=_iso(e["YEAR_AGO_END"]), produto=e.get("PRODUCT"))


def _ponto(L, cultura, praca, estagio, unidade, periodo, preco, prova, fim=None, produto=None):
    """Um ponto de preco. A identidade da serie e o PRODUTO da fonte quando ela o
    diz (codigo da API), senao a cultura da regua — e a cultura so e CROP_ID
    quando e cultura."""
    ident = produto if not e_ignorancia(produto) else cultura
    L.pontos.append({"CHAVE": (str(ident), str(praca), str(estagio)), "UNIDADE": unidade, "CULTURA": cultura,
                     "PERIODO": periodo, "PRECO": preco, "PROVA": prova,
                     "FIM": fim or (_iso(str(periodo).split("/")[-1]) if periodo else None)})


def series(L: Livro):
    """SERIE so com >= 2 pontos de periodos distintos, chave inteira conhecida e a
    MESMA unidade. Unidade diferente e outra serie — nunca se converte."""
    grupos = OrderedDict()
    for p in L.pontos:
        if any(e_ignorancia(k) for k in p["CHAVE"]) or e_ignorancia(p["UNIDADE"]) \
                or e_ignorancia(p["PRECO"]) or not p["FIM"]:
            continue
        grupos.setdefault(p["CHAVE"] + (str(p["UNIDADE"]),), []).append(p)
    for chave, ps in grupos.items():
        periodos = {p["PERIODO"] for p in ps}
        unidades = {str(p["UNIDADE"]) for p in ps}
        if len(periodos) < 2 or len(unidades) != 1:
            continue
        ps = sorted(ps, key=lambda p: p["FIM"])
        provas = []
        for p in ps:
            if p["PROVA"] not in provas:
                provas.append(p["PROVA"])
        oid = "RVD-SERIE-" + hashlib.sha256("|".join(chave).encode("utf-8")).hexdigest()[:12]
        L.objeto("market", oid, SERIE, {
            "CROP_ID": _v(ps[-1]["CULTURA"]), "PRODUTO_DA_SERIE": chave[0], "MARKET_PLACE_ID": chave[1], "PERIOD": f"{ps[0]['FIM']}/{ps[-1]['FIM']}",
            "PRICE": ps[-1]["PRECO"], "UNIT": chave[3], "MARKET_STAGE": chave[2],
            "PONTOS": [{"PERIODO": p["PERIODO"], "PRECO": p["PRECO"], "UNIDADE": p["UNIDADE"]} for p in ps],
            "N_PONTOS": len(ps),
        }, provas, porque=f"{len(ps)} pontos da mesma serie (mesma praca, estagio e unidade)",
           incerteza="dois pontos nao sao tendencia; o ultimo ponto nao e o preco de hoje")


# ── SCIENCE — Intelligence Scientifica ──────────────────────────────────────
#: Os tres ficheiros de ciencia declaram a rota: «OpenAlex /works» (ENSAIO-OFFLINE,
#: PEDIDO_ORIGINAL), «3 rodadas × {OpenAlex…}» (T6-PARA-SALA.md), «OpenAlex (rota
#: REST gratuita)» (RESEARCHER-CORPUS, source). O SOURCE_ID sai do Atlas para
#: ESSA rota (EU-T5-001 hoje), nunca do endereco de cada obra.
ROTA_OPENALEX = "https://api.openalex.org/works"


def _mur(L: Livro):
    """OpenAlex ID -> o que o MUR diz em publico (nome, fascia, ateneo, SSD). E as
    278 linhas passam pelo G0: sem data de observacao, ficam lacuna contada."""
    d = _ler(L.raiz, FICHEIROS["MUR"])
    por_id = {}
    for r in d["LISTA"]:
        # O MUR (CERCA UNIVERSITA) nao tem ficha no Atlas: SOURCE_ID NAO SEI.
        L.item("science", "MUR", r["MUR_NOME"], source_id=NAO_SEI, document_id=None,
               url=NAO_SEI, publicado=NAO_SEI, colhido=NAO_SEI, fact_time=NAO_SEI,
               base="a lista do MUR no repositorio nao diz de quando e (LISTA-MESTRA-PESQUISADORES.md)")
        if r.get("ESTADO") in ("MUR_E_OBRAS", "VARIOS_IDS"):
            for oa in r.get("OPENALEX_IDS") or []:
                por_id[oa] = {"NOME_NO_MUR": r["MUR_NOME"], "FASCIA": r.get("FASCIA"),
                              "ATENEO": r.get("ATENEO"), "SSD_2024": r.get("SSD_2024"),
                              "LIGACAO": r.get("ESTADO")}
    return por_id


def ciencia(L: Livro):
    mur = _mur(L)
    ens = _ler(L.raiz, FICHEIROS["T6_TRABALHOS"])
    gravado = _iso(ens["FIXTURES"].get("GRAVADO_EM")) or NAO_SEI
    for u in ens["UNIDADES"]:
        _trabalho_t6(L, u, gravado, mur)
    _por_evidencia(L, mur)
    _corpus(L, mur)


def _pares(lista):
    return [x.get("VALOR") for x in lista if isinstance(x, dict)] if isinstance(lista, list) else []


def _trabalho_t6(L, u, gravado, mur):
    doi = u.get("DOI")
    prova = L.item("science", "T6_TRABALHOS", doi or u.get("OPENALEX_WORK_ID"),
                   source_id=_source_id_do_atlas(L, ROTA_OPENALEX),
                   document_id=doi or u.get("OPENALEX_WORK_ID"), url=u.get("OPENALEX_WORK_ID"),
                   publicado=u.get("PUBLICADO_EM"), colhido=gravado, fact_time=u.get("PUBLICADO_EM"),
                   base="o facto registado e a PUBLICACAO do trabalho; o periodo do estudo e STUDY_PERIOD")
    if not prova:
        return
    it = [a for a in u.get("AUTORES") or [] if a.get("AFILIACAO_ITALIANA_NESTA_OBRA")]
    ror = sorted({i["ROR"] for a in it if isinstance(a.get("INSTITUICOES_NESTA_OBRA"), list)
                  for i in a["INSTITUICOES_NESTA_OBRA"] if not e_ignorancia(i.get("ROR"))})
    L.objeto("science", f"RVD-T6-{doi}", FATO, {
        "DOI": _v(doi), "TRIAL_ID": _v(u.get("TRIAL_ID")),
        "RESEARCHER_ORCID": _v(sorted({a["ORCID_NO_INDICE"] for a in it if not e_ignorancia(a.get("ORCID_NO_INDICE"))})),
        "INSTITUTION_ID": _v(ror), "MOLECULE": _v(u.get("MOLECULA")), "CROP_ID": _v(_pares(u.get("CULTURA"))),
        "ISSUE_ID": _v(_pares(u.get("PROBLEMA"))), "STUDY_LOCATION": _v(_pares(u.get("LOCAL_DO_ESTUDO_ESCRITO"))),
        "STUDY_PERIOD": _v(u.get("PERIODO_DO_ESTUDO")), "TITULO": _curto(u.get("TITULO")) or NAO_SEI,
        "TIPO_DE_MATERIAL": _v(u.get("TIPO")),
        "AUTORES_COM_AFILIACAO_ITALIANA": [_autor(a, mur) for a in it],
    }, prova, porque="trabalho publicado que a consulta T6 trouxe num par do casco",
       incerteza="a ligacao autor -> pessoa e a do indice (PROVA_DA_PESSOA por autor)")


def _autor(a, mur):
    """Nome e casa publicos de quem assina; o que o MUR diz, quando liga. Nada mais."""
    inst = a.get("INSTITUICOES_NESTA_OBRA")
    return {"NOME": _v(a.get("NOME")), "ORCID": _v(a.get("ORCID_NO_INDICE")),
            "PROVA_DA_PESSOA": _v(a.get("PROVA_DA_PESSOA")),
            "INSTITUICOES": _v([i.get("NOME") for i in inst] if isinstance(inst, list) else inst),
            "MUR": mur.get(a.get("OPENALEX_ID"), NAO_SEI)}


def _por_evidencia(L, mur):
    d = _ler(L.raiz, FICHEIROS["T6_POR_EVIDENCIA"])
    vistos = set()
    pessoas = list(d.get("TOP_30") or []) + [p for ps in (d.get("POR_PAR") or {}).values() for p in ps]
    for p in pessoas:
        k = (p["PAR"], p["OPENALEX_ID"])
        if k in vistos:
            continue
        vistos.add(k)
        reg = f"{p['PAR']}|{p['OPENALEX_ID'].rsplit('/', 1)[-1]}"
        desde, ultimo = _iso(d.get("DESDE")), _iso(p.get("ULTIMO"))
        prova = L.item("science", "T6_POR_EVIDENCIA", reg, source_id=_source_id_do_atlas(L, ROTA_OPENALEX),
                       document_id=p["OPENALEX_ID"], url=p["OPENALEX_ID"], publicado=NAO_SEI, colhido=NAO_SEI,
                       fact_time=f"{desde}/{ultimo}" if desde and ultimo else NAO_SEI,
                       base="janela da contagem: DESDE do ficheiro ate ao ULTIMO trabalho contado",
                       captura_g0=ultimo, base_captura="LIMITE_INFERIOR=ULTIMO_TRABALHO_CONTADO")
        if not prova:
            continue
        cultura, _, problema = p["PAR"].partition(" x ")
        L.objeto("science", f"RVD-PESQ-{reg}", CONTAGEM, {
            "DOI": NAO_SEI, "TRIAL_ID": NAO_SEI, "RESEARCHER_ORCID": _v(p.get("ORCID")),
            "INSTITUTION_ID": NAO_SEI, "MOLECULE": NAO_SEI, "CROP_ID": _v(cultura), "ISSUE_ID": _v(problema),
            "STUDY_LOCATION": NAO_SEI, "STUDY_PERIOD": NAO_SEI,
            "PESQUISADOR": _v(p.get("NOME")), "INSTITUICOES": _v(p.get("INSTITUICOES_IT") or []),
            "PROVA_DA_PESSOA": _v(p.get("PROVA")), "MUR": mur.get(p["OPENALEX_ID"], NAO_SEI),
            "TRABALHOS_DO_PAR": p.get("TRABALHOS_DO_PAR", NAO_SEI), "DESDE_2023": p.get("DESDE_2023", NAO_SEI),
            "ULTIMO_TRABALHO": _v(ultimo), "DOIS_DE_EXEMPLO": p.get("DOIS") or NAO_SEI,
            "CRITERIO_DA_CONTAGEM": _v(d.get("CRITERIO")),
        }, prova, porque=f"{p.get('TRABALHOS_DO_PAR')} trabalhos no par {p['PAR']} (contados nas 589 obras T6)",
           incerteza="contagem nao e ranking de pessoa; data da captura NAO SEI")


def _corpus(L, mur):
    d = _ler(L.raiz, FICHEIROS["CORPUS_PESQUISADOR"])
    col = _iso(d.get("captured_at")) or NAO_SEI
    por_obra = OrderedDict()
    for m in d["MATERIALS"]:
        if not str(m.get("CASE_ID", "")).startswith("IT-"):
            continue
        por_obra.setdefault(m["MATERIAL_ID"], []).append(m)
    for mid, ms in por_obra.items():
        fortes = [m for m in ms if m.get("PERSON_PROOF") in PROVA_FORTE_DE_PESSOA and m.get("DOMAIN_STATE") == "IN_DOMAIN"]
        if not fortes:
            L.recusa("science", "CORPUS_PESQUISADOR", mid, "NAO_E_EVIDENCIA_PELA_REGRA_DO_CORPUS: "
                     "prova de pessoa fraca ou fora do dominio (EVIDENCE_RULE do proprio ficheiro)")
            continue
        m = fortes[0]
        # A obra veio pela rota OpenAlex (SOURCE_ROUTE); o SOURCE_ID e o do Atlas
        # para essa rota, nao o nome do dataset.
        prova = L.item("science", "CORPUS_PESQUISADOR", mid, source_id=_source_id_do_atlas(L, ROTA_OPENALEX),
                       document_id=m.get("DOI") or mid, url=m.get("SOURCE_URL"), publicado=m.get("PUBLISHED_AT"),
                       colhido=col, fact_time=m.get("PUBLISHED_AT"),
                       base="o facto registado e a PUBLICACAO do trabalho; o periodo do estudo e STUDY_PERIOD")
        if not prova:
            continue
        L.objeto("science", f"RVD-CORPUS-{mid.rsplit('/', 1)[-1]}", FATO, {
            "DOI": _v(m.get("DOI")), "TRIAL_ID": NAO_SEI,
            "RESEARCHER_ORCID": _v(sorted({x["ORCID"] for x in fortes if not e_ignorancia(x.get("ORCID"))})),
            "INSTITUTION_ID": NAO_SEI, "MOLECULE": NAO_SEI, "CROP_ID": _v(m.get("PROVED_CROP")),
            "ISSUE_ID": _v(m.get("PROVED_ISSUE")), "STUDY_LOCATION": _v(m.get("COUNTRY_OF_FACT")),
            "STUDY_PERIOD": NAO_SEI, "TITULO": _curto(m.get("TITLE")) or NAO_SEI, "REVISTA": _v(m.get("VENUE")),
            "CASO": _v(m.get("CASE_ID")), "PAPEL_DO_MATERIAL": _v(m.get("MATERIAL_ROLE")),
            "PESQUISADORES": [{"NOME": _v(x.get("NAME")), "ORCID": _v(x.get("ORCID")),
                               "INSTITUICAO": _v(x.get("INSTITUTION")), "PROVA_DA_PESSOA": _v(x.get("PERSON_PROOF")),
                               "MUR": mur.get(x.get("PERSON_ID"), NAO_SEI)} for x in fortes],
        }, prova, porque="trabalho publico de pesquisador com identidade provada, no caso italiano congelado",
           incerteza="classificador lexical (LIMITE_DO_CLASSIFICADOR do ficheiro); resumo nao transportado")


# ── SOURCES e ARCHIVE — derivados do que ESTA entrada leu ───────────────────
def _evidencia(o):
    p = o["PROVA"][0]
    ev = {"ID": o["OBJETO_ID"], "SOURCE_ID": p["SOURCE_ID"], "DOCUMENT_ID": p["DOCUMENT_ID"]}
    if not e_ignorancia(p.get("URL")):
        ev["URL"] = p["URL"]
    if not e_ignorancia(o["CHAVES"].get("PAGE_ID")):
        ev["PAGE_ID"] = o["CHAVES"]["PAGE_ID"]
    return ev


def independencia(L: Livro) -> dict:
    """O grafo de dependencia do motor sobre os objetos de cada gaveta: quantas
    fontes independentes a gaveta tem, e quem domina. Nao junta perguntas."""
    out = OrderedDict()
    for comp in GERAIS:
        g = GRAFO.grafo([_evidencia(o) for o in L.itens[comp]])
        out[comp] = {k: g.get(k) for k in ("EXTERNAL_SIGNAL_COUNT", "EVIDENCE_BASE_COUNT",
                                           "INDEPENDENT_SOURCE_COUNT", "DOMINANT_SOURCE",
                                           "DOMINANT_SOURCE_SHARE_PCT", "CONVERGENCE", "INDEPENDENCE_BASIS")}
    return out


def fontes(L: Livro, indep: dict):
    """RENDIMENTO_DE_FONTE contado sobre o que ESTA entrada leu — provado so por
    itens da propria fonte que passaram G0. Fonte sem item que passou: lacuna."""
    por = OrderedDict()
    for comp, sid, passou, prova in L.lidos:
        e = por.setdefault(sid, {"LIDOS": 0, "PASSOU": 0, "PROVAS": [], "COMPS": set()})
        e["LIDOS"] += 1
        e["COMPS"].add(comp)
        if passou:
            e["PASSOU"] += 1
            if len(e["PROVAS"]) < PROVA_MAX_RENDIMENTO:
                e["PROVAS"].append(prova)
    produzidos = Counter(p["SOURCE_ID"] for comp in GERAIS for o in L.itens[comp]
                         for p in {q["ITEM_ID"]: q for q in o["PROVA"]}.values())
    for sid in sorted(por, key=str):
        e = por[sid]
        if e_ignorancia(sid) or not e["PROVAS"]:
            L.gaps.append({"FERRAMENTA": "sources", "SOURCE_ID": sid, "ITENS_LIDOS": e["LIDOS"],
                           "ITENS_QUE_PASSARAM_G0": e["PASSOU"],
                           "MOTIVO": "SEM_SOURCE_ID_NO_REGISTO_NEM_NO_ATLAS" if e_ignorancia(sid)
                           else "NENHUM_ITEM_PASSOU_G0: o rendimento nao se prova"})
            continue
        L.objeto("sources", f"RVD-FONTE-{sid}", CONTAGEM, {
            "SOURCE_ID": sid, "ITENS_LIDOS": e["LIDOS"], "ITENS_QUE_PASSARAM_G0": e["PASSOU"],
            "OBJETOS_PRODUZIDOS": produzidos.get(sid, 0), "GAVETAS": sorted(e["COMPS"]),
        }, e["PROVAS"], porque="contado sobre os registos que ESTA entrada extra leu; nao e o rendimento historico da fonte",
           incerteza="uma entrada extra nao e uma corrida de coleta", especie="RENDIMENTO_DE_FONTE")


def arquivo(L: Livro):
    """Archivio: os objetos que ESTA entrada produziu, com a mesma especie e a mesma
    prova (P3 do pote). Nada muda de especie ao ser arquivado."""
    for comp in GERAIS:
        for o in list(L.itens[comp]):
            c = o["CHAVES"]
            serie = {"PONTOS": c["PONTOS"], "N_PONTOS": c["N_PONTOS"]} if c["TIPO_DO_DADO"] == SERIE else {}
            L.objeto("archive", "ARQ-" + o["OBJETO_ID"], c["TIPO_DO_DADO"], dict(serie, **{
                "CROP_ID": c.get("CROP_ID", NAO_SEI), "ISSUE_ID": c.get("ISSUE_ID", NAO_SEI),
                "REGION_ID": NAO_SEI, "FACT_LOCATION": c.get("FACT_LOCATION", c.get("STUDY_LOCATION", NAO_SEI)),
                "FACT_TIME": c.get("FACT_TIME", c.get("PERIOD", o["PROVA"][0]["FACT_TIME"])),
                "GAVETA_DE_ORIGEM": comp, "OBJETO_DE_ORIGEM": o["OBJETO_ID"],
            }), o["PROVA"], porque=o["PORQUE"], incerteza=o["INCERTEZA"], especie=o["ESPECIE"])


# ── montar, juntar, conferir ─────────────────────────────────────────────────
def _head(raiz: Path):
    try:
        r = subprocess.run(["git", "rev-parse", "HEAD"], cwd=raiz, capture_output=True, text=True, timeout=30)
        return r.stdout.strip() if r.returncode == 0 and r.stdout.strip() else NAO_SEI
    except (OSError, subprocess.SubprocessError):
        return NAO_SEI


def montar(raiz: Path = RAIZ) -> dict:
    """Le os ficheiros e devolve a ENTRADA-EXTRA. Deterministica: a mesma arvore
    da a mesma entrada (sem relogio, sem rede, sem sorteio)."""
    raiz = Path(raiz)
    L = Livro(raiz)
    vozes(L)
    concorrencia(L)
    mercado(L)
    ciencia(L)
    indep = independencia(L)
    fontes(L, indep)
    arquivo(L)
    impressao = hashlib.sha256("|".join(f"{k}={v}" for k, v in L.blobs.items()).encode()).hexdigest()
    colhidos = sorted({e["COLHIDO_EM"][:10] for e in L.linhagem if not e_ignorancia(e["COLHIDO_EM"])})
    extra = {
        "SCHEMA": CONTRATO, "MARCA": POTE.MARCA, "NAO_PARA_CLIENTE": True, "SINTETICA": False,
        "INTELLIGENCE_RUN_ID": "RVD-" + impressao[:16], "SOURCE_HEAD": _head(raiz),
        "CORTE": colhidos[-1] if colhidos else NAO_SEI, "RESULT_STATE": "INTAKE_OK",
        "LEI": "dado ja coletado, no contrato do pote; G0 do motor decide; NAO SEI onde o registo nao diz",
        "FICHEIROS_LIDOS": [{"CHAVE": k, "CAMINHO": FICHEIROS[k], "GIT_BLOB": L.blobs[k]} for k in FICHEIROS],
        "LINEAGE": L.linhagem, "SIGNALS": [], "REQUIREMENTS": [], "GAPS": L.gaps,
        "ITENS_POR_FERRAMENTA": {c: L.itens[c] for c in COMPARTIMENTOS},
        "RECUSADOS_PELO_ADAPTADOR": L.recusados_aqui,
        "INDEPENDENCIA_POR_COMPARTIMENTO": indep,
    }
    extra["CONTAGEM"] = contagem(extra)
    violacoes = conferir(extra)
    if violacoes:
        raise LeiViolada("entrada extra reprovada: " + "; ".join(violacoes[:10]))
    return extra


def contagem(extra: dict) -> dict:
    """Quantos objetos por gaveta e por TIPO_DO_DADO, e quanto ficou de fora."""
    por = OrderedDict()
    for c in COMPARTIMENTOS:
        objs = extra["ITENS_POR_FERRAMENTA"][c]
        por[c] = {"OBJETOS": len(objs),
                  "POR_TIPO": dict(sorted(Counter(o["CHAVES"]["TIPO_DO_DADO"] for o in objs).items())),
                  "LACUNAS_G0": sum(1 for g in extra["GAPS"] if g.get("FERRAMENTA") == c and g.get("MOTIVO") == "BLOQUEADO_EM_G0"),
                  "RECUSADOS_PELO_ADAPTADOR": sum(1 for r in extra["RECUSADOS_PELO_ADAPTADOR"] if r["COMPARTIMENTO"] == c)}
    return {"POR_COMPARTIMENTO": por, "ITENS_NA_LINHAGEM": len(extra["LINEAGE"]),
            "PASSARAM_G0": sum(1 for e in extra["LINEAGE"] if e["G0"] == "PASSOU"),
            "FICHEIROS": {f["CHAVE"]: f["GIT_BLOB"] for f in extra["FICHEIROS_LIDOS"]}}


_CONTATO = re.compile(r"[\w.+-]+@[\w-]+\.[a-z]{2,}|(?<![\w/=])\+\d{2}[\d .]{7,}\d", re.I)


#: «hoje» so pode aparecer NEGADO («nao e o estado de hoje»). Afirmado, e mentira
#: sobre um dado com data.
_NEGA_HOJE = re.compile(r"n[aã]o (?:e )?o (?:estado |preco )?de hoje")


def conferir(extra: dict) -> list:
    """O portao de saida da entrada extra, independente de `montar`."""
    v = []
    if extra.get("SCHEMA") != CONTRATO:
        v.append("SCHEMA errado")
    itens = extra.get("ITENS_POR_FERRAMENTA") or {}
    if set(itens) - set(COMPARTIMENTOS):
        v.append("compartimento fora dos seis desta missao")
    linhagem = {(e["CORRIDA_UPSTREAM"], e["ITEM_ID"]): e for e in extra.get("LINEAGE") or []}
    for comp, objs in itens.items():
        for o in objs:
            oid = o.get("OBJETO_ID")
            tipo = (o.get("CHAVES") or {}).get("TIPO_DO_DADO")
            if tipo not in TIPOS_DO_DADO:
                v.append(f"{comp}/{oid}: sem marca do tipo")
            if o.get("ESTADO") != ESTADO:
                v.append(f"{comp}/{oid}: estado {o.get('ESTADO')}")
            for p in o.get("PROVA") or [{}]:
                e = linhagem.get((p.get("CORRIDA_UPSTREAM"), p.get("ITEM_ID")))
                if not e or e["G0"] != "PASSOU":
                    v.append(f"{comp}/{oid}: prova fora da linhagem ou bloqueada em G0")
                for k in ("URL", "PUBLICADO_EM", "COLHIDO_EM", "FACT_TIME"):
                    if k not in p or (e_ignorancia(p.get(k)) and p.get(k) != NAO_SEI):
                        v.append(f"{comp}/{oid}: prova esconde {k}")
            if tipo == SERIE:
                pts = o["CHAVES"].get("PONTOS") or []
                if len(pts) < 2 or len({str(x["UNIDADE"]) for x in pts}) != 1 \
                        or len({x["PERIODO"] for x in pts}) < 2:
                    v.append(f"{comp}/{oid}: serie com menos de 2 pontos ou unidades misturadas")
            texto = json.dumps(o, ensure_ascii=False)
            if _CONTATO.search(texto):
                v.append(f"{comp}/{oid}: contacto pessoal (email/telefone) no objeto")
            if "hoje" in _NEGA_HOJE.sub("", texto.lower()):
                v.append(f"{comp}/{oid}: diz «hoje»")
    return v


def juntar(corrida: dict, extra: dict) -> dict:
    """A corrida da rodada + a entrada extra -> UM livro de corrida para o pote.

    A corrida manda no cabecalho (INTELLIGENCE_RUN_ID, SOURCE_HEAD, CORTE,
    RESULT_STATE). A extra so ACRESCENTA: LINEAGE, GAPS e objetos nas gavetas. Um
    OBJETO_ID ou um par (CORRIDA_UPSTREAM, ITEM_ID) que ja exista na corrida para."""
    if not isinstance(extra, dict) or extra.get("SCHEMA") != CONTRATO:
        raise LeiViolada(f"isto nao e uma {CONTRATO}")
    violacoes = conferir(extra)
    if violacoes:
        raise LeiViolada("entrada extra reprovada: " + "; ".join(violacoes[:10]))
    if not isinstance(corrida, dict) or e_ignorancia(corrida.get("INTELLIGENCE_RUN_ID")):
        raise LeiViolada("corrida da rodada sem INTELLIGENCE_RUN_ID")
    if corrida.get("SCHEMA") == POTE.V1.CONTRATO:
        raise LeiViolada("um payload v1 ja fechado nao tem LINEAGE: junte a extra ao LIVRO da corrida")
    out = json.loads(json.dumps(corrida))
    chaves = {(str(e.get("CORRIDA_UPSTREAM")), str(e.get("ITEM_ID"))) for e in out.get("LINEAGE") or []}
    repetidas = [e for e in extra["LINEAGE"] if (e["CORRIDA_UPSTREAM"], e["ITEM_ID"]) in chaves]
    if repetidas:
        raise LeiViolada(f"{len(repetidas)} entradas da LINEAGE ja estao na corrida")
    out["LINEAGE"] = list(out.get("LINEAGE") or []) + extra["LINEAGE"]
    out["GAPS"] = list(out.get("GAPS") or []) + extra["GAPS"]
    ipf = out.setdefault("ITENS_POR_FERRAMENTA", {})
    ids = {POTE._id_do_objeto(o) for objs in ipf.values() for o in (objs if isinstance(objs, list) else [objs])}
    for comp, objs in extra["ITENS_POR_FERRAMENTA"].items():
        dup = [o["OBJETO_ID"] for o in objs if o["OBJETO_ID"] in ids]
        if dup:
            raise LeiViolada(f"OBJETO_ID ja existe na corrida: {dup[:3]}")
        atual = ipf.get(comp) or []
        ipf[comp] = (atual if isinstance(atual, list) else [atual]) + objs
    out["ENTRADAS_EXTRA"] = list(out.get("ENTRADAS_EXTRA") or []) + [{
        "SCHEMA": CONTRATO, "INTELLIGENCE_RUN_ID_DA_EXTRA": extra["INTELLIGENCE_RUN_ID"],
        "FICHEIROS_LIDOS": extra["FICHEIROS_LIDOS"], "CONTAGEM": extra["CONTAGEM"]}]
    return out


def resumo(extra: dict) -> str:
    c = extra["CONTAGEM"]
    linhas = [f"{POTE.MARCA} · {CONTRATO} · {extra['INTELLIGENCE_RUN_ID']} · "
              f"{c['PASSARAM_G0']}/{c['ITENS_NA_LINHAGEM']} itens passaram G0"]
    for comp, e in c["POR_COMPARTIMENTO"].items():
        linhas.append(f"  {comp:12s} {e['OBJETOS']:5d} objetos {e['POR_TIPO']} · lacunas G0 {e['LACUNAS_G0']}"
                      f" · recusados {e['RECUSADOS_PELO_ADAPTADOR']}")
    return "\n".join(linhas)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="RETE-VOCI-DATI: dado ja coletado -> ENTRADA-EXTRA do pote v2")
    ap.add_argument("--raiz", default=str(RAIZ))
    ap.add_argument("--saida", help="onde escrever a ENTRADA-EXTRA (.json)")
    ap.add_argument("--juntar", help="o livro da corrida da rodada a que a extra se junta")
    ap.add_argument("--saida-junta", help="onde escrever o livro juntado (.json)")
    ap.add_argument("--pote", help="gerar o pote v2 do livro juntado (ou so da extra) neste destino")
    ap.add_argument("--contagem", help="escrever so a CONTAGEM (.json)")
    a = ap.parse_args(argv)
    extra = montar(Path(a.raiz))
    for destino in (a.saida, a.saida_junta, a.contagem):
        if destino and "italia-portale" in Path(destino).resolve().parts:
            print("RECUSADO: a entrada extra nao se escreve dentro de italia-portale/")
            return 3
    if a.pote and not POTE.destino_permitido(Path(a.pote)):
        print("RECUSADO: dentro de italia-portale/ o pote so pode ir para client/sintonia-pote.js")
        return 3
    if a.saida:
        Path(a.saida).write_text(json.dumps(extra, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    if a.contagem:
        Path(a.contagem).write_text(json.dumps(extra["CONTAGEM"], ensure_ascii=False, indent=1) + "\n",
                                    encoding="utf-8")
    livro = extra
    if a.juntar:
        livro = juntar(json.loads(Path(a.juntar).read_text(encoding="utf-8")), extra)
        if a.saida_junta:
            Path(a.saida_junta).write_text(json.dumps(livro, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    if a.pote:
        pote = POTE.adaptar(livro)
        texto = POTE.como_js(pote) if a.pote.endswith(".js") else json.dumps(pote, ensure_ascii=False, indent=1) + "\n"
        Path(a.pote).write_text(texto, encoding="utf-8")
    print(resumo(extra))
    return 0


if __name__ == "__main__":
    sys.exit(main())
