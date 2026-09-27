#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""CRUZAMENTOS-MAX — o maximo de cruzamentos que a prova do repo aguenta, e nenhum a mais.

    MISSAO   CRUZAMENTOS-MAX (D114 do dono: «portal com o MAXIMO de cruzamentos possiveis — mas cada
             cruzamento com prova; nada inventado». D114 nao esta escrita no repo; a fonte fica dita aqui)
    ESPECIE  MOTOR (Z-MOTOR). NAO E POTE. NAO E TELA. NAO TOCA REDE NEM LIVRO VIVO.

    python3 motor/cruzamentos_max.py                    # le os insumos do repo e escreve a analise
    python3 -m unittest tests.test_cruzamentos_max -v

A PERGUNTA, E AS TRES QUE ELA GANHOU
------------------------------------
    R7   «o rotulo ADAMA lido autoriza a substancia citada na cultura do boletim?» (86 cruzamentos,
         docs/intelligence/r7/ANALISE-R7.json). Aqui ela e REFEITA com uma tabela de GRAO provada pelo
         rotulo, e os 5 «sim a confirmar» sao conferidos contra o cadastro oficial do Ministero.
    PM   PORTFOLIO_MATCH — para um par cultura x praga que o boletim ESCREVEU na mesma secao, que produto
         ADAMA registado na Italia tem aquela cultura x alvo NO ROTULO (par lido + registo no cadastro).
         Isto NAO e «o boletim recomendou»: e o rotulo a cobrir o par que o boletim citou.
    CS   COMPETITIVE_SET — os produtos de OUTRAS empresas no cadastro oficial com a mesma substancia.
         ⚠️ O cadastro FTS6 NAO tem coluna de cultura nem de alvo, e os rotulos dos concorrentes nao foram
         lidos: o grao do CS e a SUBSTANCIA, dito em cada objeto. Cultura x alvo do concorrente = NAO SEI.

O QUE CONTA COMO PROVA DO GRAO — so o rotulo, e so o MESMO rotulo
----------------------------------------------------------------
O leitor de rotulos (coleta/rotulos_ler.py) funde varias culturas numa chave: «melone», «zucchino» e
«cocomero» viram CUCURBITACEE; «pomacee» vira MELO; «aglio» vira CIPOLLA. A chave canonica igual NAO prova
que o rotulo nomeia a cultura do boletim. Por isso, para as chaves que o leitor usa como GRUPO:

    NOMEADA_NO_ROTULO              a cultura do boletim esta escrita na citacao do proprio par
    MEMBRO_DECLARADO_NO_ROTULO     o MESMO rotulo declara «Pomacee (melo, pero, ...)» e o par cita «Pomacee»
    GRAO_NAO_PROVADO               a chave bate, mas nenhuma das duas coisas acima — continua PARTIAL

Uma declaracao de grupo de um rotulo NUNCA serve para outro rotulo: «Cereali (orzo, frumento)» no MAVRIK
JET nao e o «Cereali (orzo, avena, frumento, segale, triticale)» do KLARTAN. Para as chaves que sao UMA
cultura (VITE = vite|vigneto|uva), a chave igual basta: e o sinonimo do leitor, nao grao.

AUSENCIA E AUSENCIA NA NOSSA LEITURA
------------------------------------
Rotulos com par lido: 102/163. «NO» aqui e sempre «nao esta na referencia lida», nunca «a ADAMA nao tem
produto». Cultura que o leitor de rotulos nao conhece (mirtillo, nocciolo, carciofo...) fica NAO SEI.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
import sys
import unicodedata
from collections import Counter
from datetime import date, datetime

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))   # a raiz
import _gavetas  # noqa: E402,F401 — poe as gavetas do processo no caminho

from boletim_do_campo import CULTURAS as CULTURAS_BOLETIM     # noqa: E402  (leis/)
from boletim_do_campo import FORMAS, nome_do_problema         # noqa: E402
from ponte_intelligence_casco import NAO_SEI, MARCA, ESTADO_TRANSPORTAVEL   # noqa: E402  (pacote/)
# PORTA-UNICA-REFERENCIA (D116): bulas, registos e pares entram pela porta, na edicao da
# referencia. Este motor lia IT-ROTULOS-PARES.json e o CSV PROD_FTS_6_20260907 (OUTRA edicao)
# direto; deixou de ler. O que a edicao nao tem fica LACUNA declarada (ver LACUNAS abaixo).
import porta_da_referencia as PORTA                           # noqa: E402  (motor/)

# ── O VOCABULARIO DO LEITOR DE ROTULOS — COPIA GUARDADA POR TESTE ────────────
# O motor NAO importa codigo da coleta (system-map/tests/test_system_map.py:
# `a_coleta_nao_conversa_com_o_motor_as_centenas`, teto medido de 12 travessias). Mas a chave de
# cultura e de alvo tem de ser a MESMA que o leitor deu aos pares, senao este motor ligava o boletim a
# um par que o leitor nunca produziu. Por isso: copia literal de coleta/rotulos_ler.py:CULTURAS_ROTULO
# e :ALVOS_CANON, e de fontes/adama_it_intelligence.py:ADMIN_ATIVO — e o teste
# `test_Z1_vocabulario_igual_ao_do_leitor` (tests/test_cruzamentos_max.py) REPROVA se divergirem.
# Uma copia que um teste obriga a ser igual e uma verdade so; uma copia sem teste seriam duas.
CULTURAS_ROTULO = [
    ('BARBABIETOLA', 'barbabietola(\\s+da\\s+zucchero)?|bietola\\s+da\\s+(zucchero|coste)'),
    ('MAIS_DOLCE', 'mais\\s+dolce|granoturco\\s+dolce'),
    ('MAIS', '\\bmais\\b|granoturco|granturco'),
    ('FRUMENTO', 'frumento(\\s+(tenero|duro))?|grano\\s+(tenero|duro)'),
    ('ORZO', '\\borzo\\b'),
    ('AVENA', '\\bavena\\b'),
    ('SEGALE', '\\bsegale\\b'),
    ('TRITICALE', 'triticale'),
    ('RISO', '\\briso\\b|risaia'),
    ('SORGO', '\\bsorgo\\b'),
    ('SOIA', '\\bsoia\\b'),
    ('GIRASOLE', 'girasole'),
    ('COLZA', '\\bcolza\\b'),
    ('ERBA_MEDICA', 'erba\\s+medica'),
    ('VITE', '\\bvite\\b|vigneto|uva\\s+da\\s+(tavola|vino)'),
    ('MELO', '\\bmelo\\b|\\bmeli\\b|pomacee'),
    ('PERO', '\\bpero\\b|\\bperi\\b'),
    ('PESCO', '\\bpesco\\b|\\bpeschi\\b|nettarine'),
    ('ALBICOCCO', 'albicocc'),
    ('SUSINO', 'susin|\\bprugn'),
    ('CILIEGIO', 'ciliegi'),
    ('ACTINIDIA', 'actinidia|\\bkiwi\\b'),
    ('OLIVO', '\\bolivo\\b|\\bolivi\\b|oliveto'),
    ('AGRUMI', 'agrumi|arancio|limone|mandarino|clementin'),
    ('POMODORO', 'pomodoro'),
    ('PATATA', '\\bpatata\\b|\\bpatate\\b'),
    ('FRAGOLA', 'fragola|fragole'),
    ('CUCURBITACEE', 'cucurbitac|zucchin|melone|cocomer|cetriolo'),
    ('BRASSICACEE', 'brassicac|\\bcavol'),
    ('LATTUGA', 'lattuga|insalat|radicchio'),
    ('CIPOLLA', 'cipolla|aglio|porro|scalogno'),
    ('CAROTA', '\\bcarota\\b|\\bcarote\\b'),
    ('LEGUMINOSE', '\\bpisello|\\bfagiol|\\bcece\\b|\\bceci\\b|\\bfava\\b|\\blentic'),
    ('TABACCO', 'tabacco'),
    ('OLEAGINOSE', 'oleaginose'),
    ('ORTAGGI', '\\bortagg|orticol'),
    ('FLOREALI', 'floreal|ornamental'),
    ('TAPPETI_ERB', 'tappeti\\s+erbosi|\\btappeto\\s+erboso'),
]
ALVOS_CANON = [
    ('PERONOSPORA', 'peronospora|plasmopara|bremia|phytophthora\\s+infestans'),
    ('OIDIO', 'oidio|erysiphe|uncinula|podosphaera|leveillula|sphaerotheca'),
    ('BOTRITE', 'botrite|botrytis'),
    ('SEPTORIOSI', 'septorio|zymoseptoria|septoria'),
    ('FUSARIOSI', 'fusario|fusarium|gibberella'),
    ('TICCHIOLATURA', 'ticchiolatura|venturia'),
    ('RUGGINE', 'ruggine|puccinia|uromyces'),
    ('CERCOSPORA', 'cercospor'),
    ('RINCOSPORIOSI', 'rhyncosporium|rhynchosporium|rincosporios'),
    ('RAMULARIA', 'ramulari'),
    ('ANTRACNOSE', 'antracnos|colletotrichum|gloeosporium'),
    ('MAL_DEL_PIEDE', 'gaeumannomyces|mal\\s+del\\s+piede|oculimacula'),
    ('CARIE', '\\bcarie\\b|tilletia|ustilago|carbone'),
    ('BATTERIOSI', 'batterios|pseudomonas|xanthomonas|erwinia'),
    ('BRUSONE', 'brusone|pyricularia|magnaporthe'),
    ('ELMINTOSPORIOSI', 'elmintosporio|helminthosporium|drechslera|pyrenophora'),
    ('ALTERNARIA', 'alternari'),
    ('SCLEROTINIA', 'sclerotini'),
    ('MAL_BIANCO', 'mal\\s+bianco'),
    ('MONILIA', 'monili'),
    ('BOLLA', '\\bbolla\\b|taphrina'),
    ('SCAFOIDEO', 'scaphoideus|scafoideo'),
    ('CICALINE', 'cicalin|empoasca|zygina'),
    ('PIRALIDE', 'piralide|ostrinia'),
    ('DIABROTICA', 'diabrotica'),
    ('AFIDI', '\\bafid|aphis|myzus|rhopalosiphum|sitobion|metopolophium|brachycaudus|dysaphis|eriosoma|toxoptera|nasonovia|macrosiphum|aulacorthum|hyalopterus|schizaphis|phorodon|cavariella|hyadaphis'),
    ('ELATERIDI', 'elaterid|agriotes|ferretti'),
    ('ALTICHE', 'chaetocnema|psylliodes|phyllotreta|altic'),
    ('ATOMARIA', 'atomaria'),
    ('MAGGIOLINO', 'melolontha|maggiolino'),
    ('MILLEPIEDI', 'blaniulus|scutigerella|millepiedi'),
    ('DOROIFORA', 'leptinotarsa|dorifora'),
    ('PUNTERUOLO', 'ceutorhynchus|curculio|otiorhynchus|punteruolo'),
    ('CECIDOMIA', 'cecidomi|contarinia|sitodiplosis'),
    ('LEMA', '\\blema\\b|oulema'),
    ('NOTTUE', 'nottu|agrotis|spodoptera|helicoverpa|autographa|mamestra'),
    ('CIMICE', 'cimice|halyomorpha|nezara'),
    ('CARPOCAPSA', 'carpocapsa|cydia'),
    ('TIGNOLE', 'tignol|lobesia|eupoecilia|prays'),
    ('MOSCA_OLIVO', 'bactrocera\\s+oleae|mosca\\s+dell.oliv'),
    ('MOSCA_FRUTTA', 'ceratitis|mosca\\s+della\\s+frutta'),
    ('RAGNETTO', 'ragnetto|tetranychus|panonychus'),
    ('ACARI', '\\bacar|eriophy|aculus'),
    ('TRIPIDI', 'tripid|thrips|frankliniella'),
    ('ALEURODIDI', 'aleurodid|bemisia|trialeurodes|mosca\\s+bianca'),
    ('COCCINIGLIE', 'cocciniglia|cocciniglie|planococcus|saissetia|quadraspidiotus'),
    ('MINATRICI', 'minatric|liriomyza|leucoptera'),
    ('LIMACCE', 'limacc|lumac|helix|deroceras'),
    ('NEMATODI', 'nematod|meloidogyne|globodera|heterodera|pratylenchus'),
    ('DICOTILEDONI', 'dicotiledoni|infestanti\\s+a\\s+foglia\\s+larga'),
    ('GRAMINACEE', 'graminacee|infestanti\\s+graminacee'),
    ('INFESTANTI', 'infestant|malerb'),
]
ADMIN_ATIVO = ('Autorizzato', 'Ri-registrato', 'Rinnovato')

ROOT = os.path.dirname(HERE)
R7 = os.path.join(ROOT, "docs", "intelligence", "r7", "ANALISE-R7.json")
#: O que a referencia (edicao corrente, pela porta) NAO tem e este motor precisava. Declarado,
#: nunca contornado: o que dependia disto fica A CONFIRMAR / NAO SEI com o motivo.
LACUNAS = {
    "LACUNA-1_PARES_COM_CITACAO": "FECHADA nesta missao: AUTHORIZED-USES ganhou LINK_LEVEL, LINE_QUOTE e "
                                  "CROPS_QUOTE, e nasceu LABEL-READINGS — no CONSTRUTOR "
                                  "(fontes/adama_referencia.py), nao aqui.",
    "LACUNA-2_DATA_DE_REGISTO_E_REVOGA": "ABERTA: a edicao corrente do registo (a de 31/08, via o pacote DEEP) "
                                         "nao traz data_registrazione nem data_decorrenza_revoca. Sem elas a "
                                         "validade NA DATA DO BOLETIM nao se prova: o sim fica A CONFIRMAR. "
                                         "Traze-las e derivar uma edicao nova: missao nuvem-referencia-"
                                         "manutencao-v1.",
    "LACUNA-3_MERCADO_CONCORRENTE": "ABERTA: a referencia e da ADAMA; os registos das outras empresas nao "
                                    "estao nela. COMPETITIVE_SET = NAO SEI ate a referencia os ganhar numa "
                                    "edicao (mesma missao de manutencao). Ler o CSV direto seria uma segunda "
                                    "tabela-mestra, de outra edicao — proibido pela D116.",
}
SAIDA = os.path.join(ROOT, "docs", "intelligence", "r7", "CRUZAMENTOS-MAX.json")
SAIDA_ITENS = os.path.join(ROOT, "docs", "intelligence", "r7", "CRUZAMENTOS-MAX-ITENS-DO-POTE.json")
SCHEMA = "CRUZAMENTOS_MAX/v1"

# ── estados ──────────────────────────────────────────────────────────────────
YES_A_CONFIRMAR = "POSSIBLE_ANSWER_YES_A_CONFIRMAR"
NO = "POSSIBLE_ANSWER_NO"
PARTIAL = "PARTIAL_GRAO_INCOMPATIVEL"
NOT_POSSIBLE = "NOT_POSSIBLE"
CONFIRMED_YES = "CONFIRMED_YES"
UNRESOLVED = "UNRESOLVED"

PM_MATCH = "PORTFOLIO_MATCH"
PM_ESPECTRO = "PORTFOLIO_MATCH_SO_ESPECTRO_DE_PRODUTO"
PM_SEM_PAR = "SEM_PAR_LIDO"
PM_NAO_SEI = "NAO_SEI"

#: Pares do rotulo em que o DOCUMENTO une cultura e alvo. DECLARACAO_DE_PRODUTO sao duas listas que o
#: rotulo manteve separadas (IT-ROTULOS-PARES.json, LEI_DO_NIVEL_DE_LIGACAO): nao se somam.
NIVEIS_FORTES = ("LINHA_DA_TABELA", "BLOCO_DA_CULTURA")

#: As chaves do leitor de rotulos que juntam MAIS DE UMA cultura (medido nas regex de
#: coleta/rotulos_ler.py:CULTURAS_ROTULO). Para elas a chave igual nao prova a cultura do boletim.
GRUPOS_DO_LEITOR = frozenset({
    "CUCURBITACEE",   # cucurbitac|zucchin|melone|cocomer|cetriolo
    "BRASSICACEE",    # brassicac|cavol
    "LEGUMINOSE",     # pisello|fagiol|cece|fava|lentic
    "AGRUMI",         # agrumi|arancio|limone|mandarino|clementin
    "CIPOLLA",        # cipolla|aglio|porro|scalogno
    "LATTUGA",        # lattuga|insalat|radicchio
    "ORTAGGI", "FLOREALI", "OLEAGINOSE", "TAPPETI_ERB",
    "MELO",           # melo|meli|pomacee
    "PESCO",          # pesco|peschi|nettarine
    "FRUMENTO",       # frumento (tenero|duro)|grano (tenero|duro)
    "BARBABIETOLA",   # barbabietola (da zucchero)|bietola da (zucchero|coste)
})

#: As palavras de grupo que um rotulo declara com os membros entre parenteses. Medido nas 2030
#: citacoes de IT-ROTULOS-PARES.json: Pomacee, Cavoli, Cereali, Drupacee, Fruttiferi minori/a guscio.
PALAVRAS_DE_GRUPO = ("pomacee", "drupacee", "cavoli", "cereali", "cucurbitacee", "brassicacee",
                     "leguminose", "agrumi", "orticole", "fruttiferi minori", "fruttiferi a guscio",
                     "fruttiferi", "piccoli frutti", "solanacee", "liliacee")
_RE_GRUPO = re.compile(r"(?<![a-z])(%s)\s*\(([^)]{3,240})\)" % "|".join(
    re.escape(p) for p in sorted(PALAVRAS_DE_GRUPO, key=len, reverse=True)))

#: Grafias italianas da mesma substancia (DCI ingles do cadastro + a forma italiana dos boletins).
#: So para ACHAR a substancia no troco; o cadastro e comparado pela chave normalizada.
FORMAS_DA_SUBSTANCIA = {
    "TAUFLUVALINATE": ("tau-fluvalinate", "tau fluvalinate", "taufluvalinate"),
    "AZOXYSTROBIN": ("azoxystrobin", "azoxistrobina", "azoxystrobina"),
    "CAPTAN": ("captan", "captano"),
    "CYMOXANIL": ("cymoxanil", "cimoxanil"),
    "METALAXYLM": ("metalaxyl-m", "metalaxil-m", "metalaxil m"),
    "CHLORANTRANILIPROLE": ("chlorantraniliprole", "clorantraniliprole"),
    "LAMBDACYHALOTHRIN": ("lambda-cialotrina", "lambdacialotrina", "lambda-cyhalothrin", "lambdacyhalothrin"),
    "PENDIMETHALIN": ("pendimethalin", "pendimetalin"),
    "CLETHODIM": ("clethodim", "cletodim"),
}

#: X3w da R7: cultura a <= 400 caracteres da substancia. Regra nascida na R7 depois de ver os dados, e
#: ainda sem regressao (RELATORIO-RODADA-7.md §3). Aqui so corre DENTRO do troco que o repo guardou.
JANELA_X3W = 400
#: onde o cabecalho de um boletim de uma cultura tem de estar para o conferirmos no troco guardado
JANELA_DO_CABECALHO = 250

_RX_CULTURA_ROTULO = [(k, re.compile(r, re.I)) for k, r in CULTURAS_ROTULO]
_RX_ALVO = [(k, re.compile(r, re.I)) for k, r in ALVOS_CANON]
#: onde acaba a zona da cultura numa linha/bloco: o primeiro alvo do leitor, «contro» ou um numero
_RX_FIM_DA_ZONA = re.compile("|".join("(?:%s)" % r for _, r in ALVOS_CANON) + r"|\bcontro\b|\d", re.I)
_RX_DOSE = re.compile(r"\d+(?:[.,]\d+)?\s*(?:[-–]\s*\d+(?:[.,]\d+)?\s*)?(?:ml|g|kg|l|litri)\s*/\s*"
                      r"(?:hl|ha|ettaro|100\s*l)", re.I)
_RX_INTERVALO = re.compile(r"(?:(?:intervallo\s+di\s+sicurezza|prima\s+della\s+raccolta|carenza)[^.]{0,80}?"
                           r"\d+\s*giorni|\d+\s*giorni\s+prima\s+della\s+raccolta)", re.I)
_RX_ETICHETTA = re.compile(r"etichetta\s+autorizzata\s+con\s+decreto[^”\"]{0,120}", re.I)


# ── texto ────────────────────────────────────────────────────────────────────
def dobrar(s) -> str:
    """minusculas, sem acento. `leis/boletim_do_campo.py` dobra igual."""
    return "".join(c for c in unicodedata.normalize("NFKD", str(s or ""))
                   if not unicodedata.combining(c)).lower()


def chave_substancia(s) -> str:
    """TAU-FLUVALINATE, TAUFLUVALINATE e tau fluvalinate sao a mesma chave. METALAXYL != METALAXYL-M."""
    return re.sub(r"[^A-Z0-9]", "", dobrar(s).upper())


def _sem_espaco(s) -> str:
    return re.sub(r"[\s\-’']+", "", dobrar(s))


def _formas_da_cultura(nome) -> set:
    """A cultura do boletim e as formas que o leitor do boletim declara (FORMAS: plural -> singular)."""
    n = re.sub(r"\s+", " ", dobrar(nome).strip())
    base = FORMAS.get(n, n)
    return {base} | {p for p, s in FORMAS.items() if s == base}


def _literal(formas, texto) -> str | None:
    t = dobrar(texto)
    for f in sorted(formas, key=len, reverse=True):
        m = re.search(r"(?<![a-z])%s(?![a-z])" % re.escape(f), t)
        if m:
            return str(texto)[max(0, m.start() - 60):m.end() + 60].strip()
    return None


def canon_cultura(nome) -> str | None:
    """A chave que o LEITOR DE ROTULOS daria a esta cultura (a primeira regex, pela ordem dele)."""
    t = dobrar(nome)
    return next((k for k, rx in _RX_CULTURA_ROTULO if rx.search(t)), None)


def canon_alvo(nome) -> str | None:
    """Praga do boletim -> chave do rotulo: o nome com que o boletim a conta (MESMO_PROBLEMA de
    leis/boletim_do_campo.py) e depois a regex do leitor de rotulos. Nenhuma equivalencia nova."""
    t = dobrar(nome_do_problema(nome))
    return next((k for k, rx in _RX_ALVO if rx.search(t)), None)


def _data(v):
    """ISO do boletim ('2026-06-30T17:12:38+02:00') ou dd/mm/aaaa do cadastro. Ausente = None."""
    s = str(v or "").strip()
    for fmt, n in (("%Y-%m-%d", 10), ("%d/%m/%Y", 10)):
        try:
            return datetime.strptime(s[:n], fmt).date()
        except ValueError:
            continue
    return None


# ── insumos ──────────────────────────────────────────────────────────────────
def _sha256(caminho) -> str:
    h = hashlib.sha256()
    with open(caminho, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


class Referencia:
    """Os rotulos lidos + o cadastro, indexados. Nada aqui vem da rede."""

    def __init__(self, pares: dict, cadastro: list, manifesto: dict | None = None,
                 data_do_cadastro: date | None = None, cadastro_id: str = NAO_SEI,
                 tem_mercado: bool = True, carimbo: dict | None = None):
        self.cadastro_id = cadastro_id
        #: o cadastro tem os registos das OUTRAS empresas? (a referencia ADAMA nao tem: LACUNA-3)
        self.tem_mercado = tem_mercado
        self.carimbo = carimbo or {"ESTADO": NAO_SEI, "PORQUE": "referencia montada fora da porta (teste)"}
        self.pares = [p for p in pares.get("PARES") or [] if isinstance(p, dict)]
        self.por_produto = {p["PRODUCT"]: p for p in pares.get("POR_PRODUTO") or []}
        self.cobertura = pares.get("COBERTURA", NAO_SEI)
        self.data_do_cadastro = data_do_cadastro or date(2026, 9, 7)
        self.cadastro = {r.get("num_registrazione"): r for r in cadastro}
        self.linhas = cadastro
        self.product_id = {}
        for it in (manifesto or {}).get("ITENS") or []:
            self.product_id[it.get("REGISTRATION_ID")] = it.get("PRODUCT_ID")
        self.pares_do_reg = {}
        for p in self.pares:
            self.pares_do_reg.setdefault(p["REGISTRATION_ID"], []).append(p)
        self._zonas = {}
        self.grao = tabela_de_grao(self.pares)
        self.grao_do_reg = {}
        for g in self.grao:
            self.grao_do_reg.setdefault(g["REGISTRATION_ID"], []).append(g)

    @classmethod
    def da_porta(cls, ref: dict) -> "Referencia":
        """A referencia aberta pela porta -> os indices deste motor. So a edicao corrente.

        Pares = AUTHORIZED-USES (com a citacao que o construtor passou a guardar); leitura por
        bula = LABEL-READINGS; «cadastro» = REGISTRATIONS da ADAMA nesta edicao, com as
        substancias de PRODUCT-ACTIVE-INGREDIENTS. Datas de registo e revoga: NAO SEI (LACUNA-2).
        """
        PORTA.exigir(ref)
        usos = PORTA.livro(ref, "AUTHORIZED-USES")
        pares = [{"REGISTRATION_ID": u["REGISTRATION_NUMBER"], "PRODUCT": u["OBSERVED_PRODUCT_NAME"],
                  "PRODUCT_ID": u["ADAMA_PRODUCT_ID"], "USE_ID": u["USE_ID"],
                  "CULTURA_CANONICA": u["CROP_ON_LABEL"], "ALVO_CANONICO": u["TARGET_ON_LABEL"],
                  "ALVO_LITERAL": u["TARGET_AS_WRITTEN"], "LIGACAO_NIVEL": u.get("LINK_LEVEL", NAO_SEI),
                  "CITACAO_DA_LINHA": u.get("LINE_QUOTE", ""), "CITACAO_DAS_CULTURAS": u.get("CROPS_QUOTE", "")}
                 for u in usos]
        leituras = PORTA.livro(ref, "LABEL-READINGS")
        por_produto = [{"REGISTRATION_ID": x["REGISTRATION_NUMBER"], "PRODUCT": x["OBSERVED_PRODUCT_NAME"],
                        "ESTADO_DA_LEITURA": x["READING_STATE"]} for x in leituras]
        lidas = sum(1 for x in leituras if x["PAIRS"])
        subs = {}
        for rel in PORTA.livro(ref, "PRODUCT-ACTIVE-INGREDIENTS"):
            subs.setdefault(rel["REGISTRATION_NUMBER"], []).append(rel["ACTIVE_INGREDIENT"])
        ed = ref["REGISTRO"]
        cadastro, pid = [], {}
        for r in PORTA.livro(ref, "REGISTRATIONS"):
            n = r["REGISTRATION_NUMBER"]
            cadastro.append({"num_registrazione": n, "denominazione_prodotto": r.get("REGISTERED_NAME"),
                             "ragione_sociale": r.get("HOLDER"), "stato_amministrativo": r.get("ADMIN_STATUS"),
                             "data_scadenza_autorizzazione": r.get("EXPIRY_DATE"),
                             "data_registrazione": None, "data_decorrenza_revoca": None,
                             "sostanze_attive": "|".join(sorted(subs.get(n, []))),
                             "importazione_parallela": NAO_SEI, "_EDICAO": ed["EDICAO"]})
            p = r.get("ADAMA_PRODUCT_ID")
            pid[n] = p if str(p).startswith("ADAMA-P-") else NAO_SEI
        self = cls({"PARES": pares, "POR_PRODUTO": por_produto,
                    "COBERTURA": "%d/%d bulas com par lido (LABEL-READINGS, edicao %s)"
                                 % (lidas, len(leituras), ed["EDICAO"])},
                   cadastro, None, date.fromisoformat(ed["DATA_DA_EDICAO"]),
                   cadastro_id="IT-T4-001:" + ed["EDICAO"], tem_mercado=False, carimbo=PORTA.carimbo(ref))
        self.product_id = pid
        return self

    @property
    def autorizacao_a_confirmar(self) -> bool:
        """D117: edicao sem checagem ha >= 30 dias -> nenhum sim sai como afirmado."""
        return self.carimbo.get("ESTADO_FRESCOR") == PORTA.AUTORIZACAO_A_CONFIRMAR

    def zona(self, par) -> str:
        """`zona_da_cultura`, calculada uma vez por par."""
        z = self._zonas.get(id(par))
        if z is None:
            z = self._zonas[id(par)] = zona_da_cultura(par)
        return z

    def reg_do_produto(self, nome):
        p = self.por_produto.get(nome)
        return p["REGISTRATION_ID"] if p else None

    def leitura(self, reg):
        """O estado da leitura do rotulo deste registo (LIDO, LIDO_POR_BLOCO, TABELA_NAO_LOCALIZADA...)."""
        return next((p.get("ESTADO_DA_LEITURA") for p in self.por_produto.values()
                     if p.get("REGISTRATION_ID") == reg), NAO_SEI)


# ── (1) a tabela de GRAO — so o que o rotulo declara ─────────────────────────
def tabela_de_grao(pares) -> list:
    """Cada «GRUPO (membro, membro, ...)» escrito num rotulo, com o registo e a citacao.

    Membro so entra se for cultura para um dos dois leitores do repo (vocabulario do boletim ou do
    rotulo): «piccoli frutti (Drosophila suzukii)» e uma praga entre parenteses, nao um membro.
    """
    vocab = {_sem_espaco(c) for c in CULTURAS_BOLETIM} | {_sem_espaco(f) for f in FORMAS}
    vistos, out = set(), []
    for p in pares:
        for campo in ("CITACAO_DA_LINHA", "CITACAO_DAS_CULTURAS"):
            texto = p.get(campo) or ""
            for m in _RE_GRUPO.finditer(dobrar(texto)):
                grupo = m.group(1)
                brutos = re.split(r",|;|\be\b|/", m.group(2))
                membros = []
                for b in brutos:
                    b = re.sub(r"\s+", " ", b).strip(" .:-")
                    if not b:
                        continue
                    if _sem_espaco(b) in vocab or canon_cultura(b):
                        membros.append(_sem_espaco(b))
                if not membros:
                    continue
                k = (p["REGISTRATION_ID"], grupo, tuple(membros))
                if k in vistos:
                    continue
                vistos.add(k)
                out.append({"REGISTRATION_ID": p["REGISTRATION_ID"], "PRODUCT": p.get("PRODUCT"),
                            "GRUPO": grupo, "MEMBROS": membros,
                            "CITACAO": texto[m.start():m.end()][:240],
                            "FONTE": "rotulo autorizado (PDF do Ministero), AUTHORIZED-USES pela porta/" + campo})
    return out


#: Frases em que o rotulo nomeia culturas que NAO sao de uso: as de rotacao / sucessao. Medido: o
#: POSTSCRIPT 80 tem um par LEGUMINOSE cuja «cultura» e «possono essere seminate fava, cece, trifoglio».
_RX_NAO_E_USO = re.compile(r"possono\s+essere\s+seminat|in\s+successione|colture?\s+successiv|"
                           r"rotazion|risemin|dopo\s+il\s+trattamento|colture?\s+in\s+avvicendamento", re.I)
#: palavra que, logo depois da cultura, faz dela um SUBTIPO («cavolo cappuccio», «melo cotogno»)
_RX_SUBTIPO = re.compile(r"^\s+(?:cappuccio|verza|cotogno|cinese|rapa|nero|riccio|broccolo|di\s+bruxelles)\b", re.I)


def zona_da_cultura(par) -> str:
    """O pedaco do par onde o rotulo escreve a CULTURA — e nenhum outro.

    Linha/bloco: o inicio da citacao, ate ao primeiro alvo, «contro» ou numero (o leitor le a cultura no
    inicio da linha). Declaracao de produto: a citacao das culturas. Uma cultura escrita noutro sitio da
    citacao (a proxima secao, um intervalo de seguranca) nao prova nada.
    """
    if par.get("LIGACAO_NIVEL") == "DECLARACAO_DE_PRODUTO":
        return str(par.get("CITACAO_DAS_CULTURAS") or "")
    linha = str(par.get("CITACAO_DA_LINHA") or "")[:240]
    m = _RX_FIM_DA_ZONA.search(dobrar(linha))
    return linha[:m.start()] if m else linha


def _literal_de_uso(formas, zona) -> str | None:
    """A cultura escrita na zona, como cultura inteira (nao subtipo, nao cabeca de grupo declarado)."""
    t = dobrar(zona)
    for f in sorted(formas, key=len, reverse=True):
        for m in re.finditer(r"(?<![a-z])%s(?![a-z])" % re.escape(f), t):
            if _RX_SUBTIPO.match(t[m.end():]) or _RE_GRUPO.match(t[m.start():]):
                continue
            return str(zona)[max(0, m.start() - 60):m.end() + 60].strip()
    return None


def cultura_no_par(cultura, par, ref: Referencia):
    """A cultura do boletim esta coberta por este par do rotulo? -> (COMO, evidencia) ou (None, motivo)."""
    k = canon_cultura(cultura)
    zona = ref.zona(par)
    if _RX_NAO_E_USO.search(zona):
        return None, "PAR_COM_CULTURA_DE_ROTACAO"
    formas = _formas_da_cultura(cultura)
    k_par = par.get("CULTURA_CANONICA")
    # (b) o MESMO rotulo declara o grupo, o grupo esta na zona da cultura deste par, e o par e desse grupo
    for g in ref.grao_do_reg.get(par["REGISTRATION_ID"], []):
        if not ({_sem_espaco(f) for f in formas} & set(g["MEMBROS"])):
            continue
        if not _literal({g["GRUPO"]}, zona):
            continue
        if k_par not in {canon_cultura(m) for m in g["MEMBROS"]} | {canon_cultura(g["GRUPO"])}:
            continue
        return "MEMBRO_DECLARADO_NO_ROTULO", {"GRUPO": g["GRUPO"], "DECLARACAO": g["CITACAO"],
                                              "NO_PAR": zona[:200]}
    if k is None:
        return None, "FORA_DO_VOCABULARIO_DO_LEITOR"
    if k_par != k:
        return None, "OUTRA_CULTURA"
    if k not in GRUPOS_DO_LEITOR:
        rx = dict(_RX_CULTURA_ROTULO)[k]
        if rx.search(dobrar(zona)):
            return "MESMA_CULTURA", {"CHAVE": k, "NO_PAR": zona[:200]}
        return None, "CULTURA_FORA_DA_ZONA_DA_CULTURA"
    lit = _literal_de_uso(formas, zona)
    if lit:
        return "NOMEADA_NO_ROTULO", {"CHAVE": k, "NO_PAR": lit}
    return None, "GRAO_NAO_PROVADO"


def cobertura_da_cultura(cultura, regs, ref: Referencia, alvo=None, niveis=None) -> dict:
    """Em que pares dos rotulos `regs` a cultura esta coberta (e, se `alvo`, com esse alvo)."""
    provas, motivos = [], Counter()
    for reg in regs:
        for par in ref.pares_do_reg.get(reg, []):
            if alvo is not None and par.get("ALVO_CANONICO") != alvo:
                continue
            if niveis is not None and par.get("LIGACAO_NIVEL") not in niveis:
                continue
            como, ev = cultura_no_par(cultura, par, ref)
            if como:
                provas.append({"REGISTRATION_ID": reg, "PRODUCT": par.get("PRODUCT"),
                               "CULTURA_CANONICA": par.get("CULTURA_CANONICA"),
                               "ALVO_CANONICO": par.get("ALVO_CANONICO"), "LIGACAO_NIVEL": par.get("LIGACAO_NIVEL"),
                               "COMO": como, "EVIDENCIA": ev, "_PAR": par})
            else:
                motivos[ev] += 1
    return {"PROVAS": provas, "MOTIVOS": dict(motivos)}


def _limpa(provas, n=3):
    return [{k: v for k, v in p.items() if not k.startswith("_")} for p in provas[:n]]


# ── o cadastro ───────────────────────────────────────────────────────────────
def e_adama(linha) -> bool:
    return "ADAMA" in str(linha.get("ragione_sociale") or "").upper()


def tem_substancia(linha, substancia) -> bool:
    return chave_substancia(substancia) in {chave_substancia(t) for t in
                                            str(linha.get("sostanze_attive") or "").split("|")}


def validade(linha, d: date | None, data_do_cadastro: date = date(2026, 9, 7),
             cadastro_id: str = NAO_SEI) -> dict:
    """O registo valia na data `d`? SIM / NAO / NAO SEI, com o que o cadastro diz.

    O cadastro e UMA fotografia (a sua data); nao traz historico intermedio. «SIM» quer dizer: registado
    antes de `d`, validade depois de `d`, sem revoga antes de `d` — no cadastro daquela data.
    """
    if linha is None:
        return {"VALIDO": NAO_SEI, "MOTIVO": "registo ausente do cadastro"}
    estado = linha.get("stato_amministrativo") or NAO_SEI
    reg, fim = _data(linha.get("data_registrazione")), _data(linha.get("data_scadenza_autorizzazione"))
    revoga = _data(linha.get("data_decorrenza_revoca"))
    base = {"NUM_REGISTRAZIONE": linha.get("num_registrazione"), "STATO_NO_CADASTRO": estado,
            "DATA_REGISTRAZIONE": linha.get("data_registrazione"),
            "DATA_SCADENZA": linha.get("data_scadenza_autorizzazione"),
            "DECORRENZA_REVOCA": linha.get("data_decorrenza_revoca"),
            "CADASTRO": cadastro_id, "CADASTRO_DATA": data_do_cadastro.isoformat(),
            "ATIVO_NO_CADASTRO": str(estado).startswith(ADMIN_ATIVO)}
    if d is None:
        return dict(base, VALIDO=NAO_SEI, MOTIVO="data de referencia NAO SEI")
    base["DATA_DE_REFERENCIA"] = d.isoformat()
    if reg is None:
        if linha.get("_EDICAO"):
            return dict(base, VALIDO=NAO_SEI, MOTIVO="A CONFIRMAR: a edicao %s da referencia nao traz data "
                                                     "de registo nem de revoga (LACUNA-2)" % linha["_EDICAO"])
        return dict(base, VALIDO=NAO_SEI, MOTIVO="data de registo ausente no cadastro")
    if reg > d:
        return dict(base, VALIDO="NAO", MOTIVO="registado depois da data de referencia")
    if revoga and revoga <= d:
        return dict(base, VALIDO="NAO", MOTIVO="revoga com decorrencia antes da data de referencia")
    if fim and fim < d:
        return dict(base, VALIDO="NAO", MOTIVO="validade terminada antes da data de referencia")
    if fim is None and not base["ATIVO_NO_CADASTRO"]:
        return dict(base, VALIDO=NAO_SEI, MOTIVO="sem data de validade e estado nao ativo no cadastro")
    if d > data_do_cadastro and not base["ATIVO_NO_CADASTRO"]:
        return dict(base, VALIDO="NAO", MOTIVO="estado nao ativo no cadastro, que e anterior a data")
    nota = []
    if fim and fim < data_do_cadastro and base["ATIVO_NO_CADASTRO"]:
        nota.append("validade ja terminada na data do cadastro, com estado ativo: o cadastro nao diz porque")
    if d > data_do_cadastro:
        nota.append("data de referencia depois do cadastro: o estado entre as duas datas nao esta provado")
    return dict(base, VALIDO="SIM", MOTIVO="registado antes, validade depois, sem revoga antes",
                NOTA=nota or None)


# ── o texto que o repo guardou ───────────────────────────────────────────────
def _posicoes(formas, texto):
    t = dobrar(texto)
    out = []
    for f in formas:
        rx = r"(?<![a-z])%s(?![a-z])" % re.escape(dobrar(f)).replace(r"\-", r"[\s\-]?").replace(r"\ ", r"[\s\-]?")
        out += [m.start() for m in re.finditer(rx, t)]
    return sorted(out)


def formas_da_substancia(sub) -> tuple:
    return FORMAS_DA_SUBSTANCIA.get(chave_substancia(sub), (dobrar(sub),))


def culturas_ligadas_no_troco(sub, trocos) -> list:
    """X3w dentro do troco guardado: culturas (vocabulario do boletim) a <= 400 caracteres da substancia."""
    vocab = set(CULTURAS_BOLETIM) | set(FORMAS)
    achadas = []
    for t in trocos or []:
        ps = _posicoes(formas_da_substancia(sub), t)
        if not ps:
            continue
        for c in sorted(vocab, key=len, reverse=True):
            for pc in _posicoes({c}, t):
                if any(abs(pc - ps_) <= JANELA_X3W for ps_ in ps):
                    forma = FORMAS.get(c, c)
                    if forma not in achadas:
                        achadas.append(forma)
    return achadas


def substancia_no_troco(sub, trocos) -> bool:
    return any(_posicoes(formas_da_substancia(sub), t) for t in trocos or [])


# ── (1) refazer um cruzamento da R7 ──────────────────────────────────────────
def _culturas_do_documento(c) -> list:
    out = []
    for x in (c.get("FONTE") or {}).get("CULTURA_NO_READY") or []:
        x = FORMAS.get(dobrar(x).strip(), dobrar(x).strip())
        if x and x not in out:
            out.append(x)
    return out


def refazer(c: dict, ref: Referencia) -> dict:
    """Um cruzamento da R7 -> o mesmo cruzamento com a tabela de GRAO e o troco guardado.

    So muda de estado com prova: YES exige a substancia ligada a uma cultura no texto E o rotulo a cobrir;
    NO exige que nenhuma cultura do documento esteja no rotulo lido E que todas sejam do vocabulario do
    leitor (senao e NAO SEI, nao e NO).
    """
    antes = c.get("ESTADO_R7") or (c.get("INTERPRETACAO") or {}).get("ESTADO") or NAO_SEI
    regs = [r for r in (ref.reg_do_produto(n) for n in c.get("PRODUTOS_ADAMA") or []) if r]
    leituras = {r: ref.leitura(r) for r in regs}
    culturas = _culturas_do_documento(c)
    por_cultura = {}
    for cult in culturas:
        cob = cobertura_da_cultura(cult, regs, ref)
        if cob["PROVAS"]:
            por_cultura[cult] = {"ESTADO": "COBERTA_NO_ROTULO",
                                 "COMO": sorted({p["COMO"] for p in cob["PROVAS"]}),
                                 "PROVAS": _limpa(cob["PROVAS"])}
        elif canon_cultura(cult) is None and not any(
                {_sem_espaco(f) for f in _formas_da_cultura(cult)} & set(g["MEMBROS"])
                for r in regs for g in ref.grao_do_reg.get(r, [])):
            por_cultura[cult] = {"ESTADO": "FORA_DO_VOCABULARIO_DO_LEITOR"}
        elif cob["MOTIVOS"].get("GRAO_NAO_PROVADO"):
            por_cultura[cult] = {"ESTADO": "GRAO_NAO_PROVADO", "MOTIVOS": cob["MOTIVOS"]}
        else:
            por_cultura[cult] = {"ESTADO": "NAO_ESTA_NO_ROTULO_LIDO"}
    cobertas = [k for k, v in por_cultura.items() if v["ESTADO"] == "COBERTA_NO_ROTULO"]
    trocos = (c.get("FONTE") or {}).get("TROCO_COM_A_SUBSTANCIA") or []
    ligadas = culturas_ligadas_no_troco(c.get("SUBSTANCIA"), trocos)
    algum_lido = any(str(v).startswith("LIDO") for v in leituras.values())
    x2_r7 = sorted(set((c.get("INTERPRETACAO") or {}).get("X2_CULTURAS_QUE_CASAM") or []))

    if antes in (NOT_POSSIBLE, YES_A_CONFIRMAR):
        depois, motivo = antes, ("sem cultura no documento" if antes == NOT_POSSIBLE
                                 else "vai para a confirmacao contra o cadastro (passo 2)")
    elif ligadas:
        sim = [x for x in ligadas if x in cobertas]
        todas_lidas_e_ausentes = all(por_cultura.get(x, {}).get("ESTADO") == "NAO_ESTA_NO_ROTULO_LIDO"
                                     for x in ligadas)
        if sim:
            depois, motivo = YES_A_CONFIRMAR, f"substancia a <= {JANELA_X3W} car. de {', '.join(sim)} no troco"
        elif todas_lidas_e_ausentes and algum_lido:
            depois, motivo = NO, f"substancia ligada a {', '.join(ligadas)} no troco; nao esta no rotulo lido"
        else:
            depois, motivo = UNRESOLVED, "substancia ligada a cultura fora do vocabulario ou de grao nao provado"
    elif cobertas:
        depois = PARTIAL
        motivo = ("a substancia nao esta ligada a nenhuma cultura no texto guardado no repo (a cultura e a "
                  "lista do DOCUMENTO; o texto integral nao esta versionado): o rotulo cobre "
                  + ", ".join(cobertas) + ", mas nao se sabe se e dessa cultura que o boletim fala")
    elif not culturas:
        depois, motivo = NOT_POSSIBLE, "sem cultura no documento"
    elif not algum_lido:
        depois, motivo = UNRESOLVED, ("nenhum rotulo ADAMA desta substancia teve tabela lida "
                                      "(TABELA_NAO_LOCALIZADA / TABELA_SEM_PAR): NAO SEI, nao e NO")
    elif all(v["ESTADO"] == "NAO_ESTA_NO_ROTULO_LIDO" for v in por_cultura.values()):
        depois, motivo = NO, "nenhuma cultura do documento esta nos rotulos lidos (ausencia NA NOSSA LEITURA)"
    else:
        fora = sorted(k for k, v in por_cultura.items() if v["ESTADO"] != "NAO_ESTA_NO_ROTULO_LIDO")
        depois, motivo = UNRESOLVED, ("nenhuma cultura coberta, mas " + ", ".join(fora) + " fica(m) fora do "
                                      "vocabulario do leitor de rotulos ou com grao nao provado: NAO SEI, nao e NO")
    return {
        "OBJETO_ID": c.get("OBJETO_ID"), "VIA": c.get("VIA"), "SOURCE_ID": c.get("SOURCE_ID"),
        "SALA_CHAVE": c.get("SALA_CHAVE"), "RAW_OBSERVATION_ID": c.get("RAW_OBSERVATION_ID", NAO_SEI),
        "URL": c.get("URL", NAO_SEI), "PUBLISHED_AT": c.get("PUBLISHED_AT", NAO_SEI),
        "SUBSTANCIA": c.get("SUBSTANCIA"), "PRODUTOS_ADAMA": c.get("PRODUTOS_ADAMA") or [],
        "LEITURA_DOS_ROTULOS": leituras,
        "ANTES": antes, "DEPOIS": depois, "MOTIVO": motivo,
        "X2_R7": x2_r7, "COBERTAS_COM_GRAO": cobertas,
        "GANHAS_PELO_GRAO": sorted(set(cobertas) - set(x2_r7)),
        "PERDIDAS_PELO_GRAO": sorted(set(x2_r7) - set(cobertas)),
        "CULTURAS_LIGADAS_NO_TROCO": ligadas,
        "SUBSTANCIA_NO_TROCO_GUARDADO": substancia_no_troco(c.get("SUBSTANCIA"), trocos),
        "POR_CULTURA": por_cultura,
        "X3H_R7": (c.get("INTERPRETACAO") or {}).get("X3H_CABECALHO") or [],
        "TROCO": trocos[:1],
        "NAO_E": ["RECOMENDACAO", "USO", "OPPORTUNITY"],
    }


# ── (2) confirmar um «sim» contra o cadastro ─────────────────────────────────
def _literais(rx, textos):
    out = []
    for t in textos:
        for m in rx.finditer(str(t or "")):
            s = re.sub(r"\s+", " ", m.group(0)).strip()
            if s not in out:
                out.append(s)
    return out[:4]


def confirmar(r: dict, c: dict, ref: Referencia) -> dict:
    """Um POSSIBLE_ANSWER_YES_A_CONFIRMAR -> CONFIRMED_YES com evidencia, ou NO / UNRESOLVED com o motivo.

    CONFIRMED_YES exige, para pelo menos um produto ADAMA: registo no cadastro em nome da ADAMA, a
    substancia na composicao registada, validade NA DATA DO BOLETIM, a cultura no rotulo lido; e o
    cabecalho de uma cultura (X3h) visivel no troco guardado. Dose e intervalo sao TRANSCRITOS quando o
    rotulo lido os escreve na linha (DOSE_E_VOLUME_LITERAIS: «l/ha» pode ser volume de calda — o texto vai
    como esta, sem interpretacao); senao ficam NAO SEI (nao bloqueiam: o rotulo e que os fixa).
    """
    x3h = [FORMAS.get(dobrar(x), dobrar(x)) for x in (c.get("INTERPRETACAO") or {}).get("X3H_CABECALHO") or []]
    cultura = x3h[0] if x3h else (r["CULTURAS_LIGADAS_NO_TROCO"] or [None])[0]
    trocos = (c.get("FONTE") or {}).get("TROCO_COM_A_SUBSTANCIA") or []
    cabecalho = bool(cultura) and any(_literal(_formas_da_cultura(cultura), str(t)[:JANELA_DO_CABECALHO])
                                      for t in trocos)
    d = _data(c.get("PUBLISHED_AT"))
    produtos = []
    for nome in c.get("PRODUTOS_ADAMA") or []:
        reg = ref.reg_do_produto(nome)
        linha = ref.cadastro.get(reg)
        cob = cobertura_da_cultura(cultura, [reg], ref) if (reg and cultura) else {"PROVAS": [], "MOTIVOS": {}}
        textos = [p["_PAR"].get("CITACAO_DA_LINHA") for p in cob["PROVAS"]]
        val = validade(linha, d, ref.data_do_cadastro, ref.cadastro_id)
        cheques = {
            "REGISTO_NO_CADASTRO": linha is not None,
            "EMPRESA_ADAMA": bool(linha) and e_adama(linha),
            "SUBSTANCIA_NA_COMPOSICAO": bool(linha) and tem_substancia(linha, c.get("SUBSTANCIA")),
            "VALIDO_NA_DATA_DO_BOLETIM": val["VALIDO"],
            "CULTURA_NO_ROTULO": ("SIM" if cob["PROVAS"] else
                                  "NAO_NA_LEITURA" if str(ref.leitura(reg)).startswith("LIDO") else NAO_SEI),
        }
        ok = (cheques["REGISTO_NO_CADASTRO"] and cheques["EMPRESA_ADAMA"] and cheques["SUBSTANCIA_NA_COMPOSICAO"]
              and val["VALIDO"] == "SIM" and cheques["CULTURA_NO_ROTULO"] == "SIM")
        produtos.append({
            "PRODUCT": nome, "REGISTRATION_ID": reg or NAO_SEI,
            "PRODUCT_ID": ref.product_id.get(reg, NAO_SEI),
            "EMPRESA": (linha or {}).get("ragione_sociale", NAO_SEI),
            "SOSTANZE_ATTIVE": (linha or {}).get("sostanze_attive", NAO_SEI),
            "LEITURA_DO_ROTULO": ref.leitura(reg), "CHEQUES": cheques, "VALIDADE": val,
            "CULTURA_NO_ROTULO_PROVA": _limpa(cob["PROVAS"], 2),
            "ALVOS_DO_ROTULO_NESSA_CULTURA": sorted({p["ALVO_CANONICO"] for p in cob["PROVAS"]}),
            "DOSE_E_VOLUME_LITERAIS": _literais(_RX_DOSE, textos) or NAO_SEI,
            "INTERVALO_LITERAL": _literais(_RX_INTERVALO, textos) or NAO_SEI,
            "ETICHETTA_LITERAL": _literais(_RX_ETICHETTA, textos) or NAO_SEI,
            "CONFIRMA": ok,
        })
    confirmados = [p for p in produtos if p["CONFIRMA"]]
    lidos_sem = [p for p in produtos if p["CHEQUES"]["CULTURA_NO_ROTULO"] == "NAO_NA_LEITURA"]
    a_confirmar = [p for p in produtos if not p["CONFIRMA"] and p["VALIDADE"]["VALIDO"] == NAO_SEI
                   and p["CHEQUES"]["REGISTO_NO_CADASTRO"] and p["CHEQUES"]["EMPRESA_ADAMA"]
                   and p["CHEQUES"]["SUBSTANCIA_NA_COMPOSICAO"] and p["CHEQUES"]["CULTURA_NO_ROTULO"] == "SIM"]
    if not cultura:
        estado, motivo = UNRESOLVED, "sem cultura de cabecalho"
    elif not cabecalho:
        estado, motivo = UNRESOLVED, ("o cabecalho de uma cultura (X3h) nao esta no troco guardado no repo: "
                                      "nao o consigo conferir")
    elif d is None:
        estado, motivo = UNRESOLVED, ("data do boletim NAO SEI: a validade do registo NA DATA DO BOLETIM nao "
                                      "se prova (o pedido de data a Coleta ja existe)")
    elif confirmados and ref.autorizacao_a_confirmar:
        estado, motivo = YES_A_CONFIRMAR, ("D117: a edicao da referencia nao e conferida ha >= 30 dias — "
                                           "o sim fica a confirmar (%s)" % ref.carimbo.get("EDICAO_REGISTRO"))
    elif confirmados:
        estado, motivo = CONFIRMED_YES, (f"{len(confirmados)} produto(s) ADAMA com registo valido em "
                                         f"{d.isoformat()}, a substancia na composicao e {cultura} no rotulo lido")
    elif a_confirmar:
        estado, motivo = YES_A_CONFIRMAR, (f"{len(a_confirmar)} produto(s) ADAMA passam empresa, substancia e "
                                           f"{cultura} no rotulo lido, mas a validade na data do boletim nao "
                                           f"se prova: {a_confirmar[0]['VALIDADE']['MOTIVO']}")
    elif lidos_sem and len(lidos_sem) == len(produtos):
        estado, motivo = NO, f"nenhum rotulo lido destes produtos tem {cultura} (ausencia NA NOSSA LEITURA)"
    else:
        estado, motivo = UNRESOLVED, "nenhum produto passou todos os cheques, e ha rotulo nao lido"
    return {"CULTURA": cultura or NAO_SEI, "CABECALHO_NO_TROCO_GUARDADO": cabecalho,
            "DATA_DO_BOLETIM": d.isoformat() if d else NAO_SEI,
            "ESTADO": estado, "MOTIVO": motivo, "PRODUTOS": produtos,
            "PRODUTOS_QUE_CONFIRMAM": [p["PRODUCT"] for p in confirmados],
            "PRODUTOS_A_CONFIRMAR": [p["PRODUCT"] for p in a_confirmar],
            "REGRA_DE_ENTRADA": "X3h (R7): boletim de uma cultura nomeada no cabecalho — regra ainda sem "
                                "regressao; o CONFIRMED_YES herda essa condicao",
            "NAO_PROVA": ["uso", "recomendacao de produto ADAMA", "lugar", "momento", "eficacia"]}


# ── (3) PORTFOLIO_MATCH e (4) COMPETITIVE_SET ────────────────────────────────
def pares_do_boletim(analise: dict, livro=None) -> list:
    """Os pares cultura x praga ESCRITOS NA MESMA SECAO de um boletim.

    No repo: o corte vertical da R7 (PAR = SECAO) e os boletins de uma cultura cuja praga traz a cultura
    no nome (a regra de leis/boletim_do_campo.py: «a praga que traz a cultura no nome diz de quem e»).
    Fora do repo (o coordenador, localmente): `livro` = itens com PROBLEMA.SECOES da saida de
    `ler_boletim` — cada praga fica na secao da cultura onde esta escrita.
    """
    out = []
    for it in (analise.get("CORTE_VERTICAL") or {}).get("ITENS") or []:
        if it.get("PAR") != "SECAO":
            continue
        out.append({"SALA_CHAVE": it.get("SALA_CHAVE"), "SOURCE_ID": it.get("SOURCE_ID"),
                    "RAW_OBSERVATION_ID": it.get("RAW_OBSERVATION_ID", NAO_SEI), "URL": it.get("URL", NAO_SEI),
                    "PUBLISHED_AT": it.get("PUBLISHED_AT", NAO_SEI), "CULTURA": "olivo",
                    "PRAGA": "mosca dell'olivo", "ESTADO_NO_BOLETIM": "CITADA",
                    "TRECHO": it.get("PAR_TRECHO"), "ORIGEM_DO_PAR": "R7 CORTE_VERTICAL (PAR = SECAO)"})
    for c in analise.get("CROSSINGS") or []:
        trocos = (c.get("FONTE") or {}).get("TROCO_COM_A_SUBSTANCIA") or []
        for x in (c.get("INTERPRETACAO") or {}).get("X3H_CABECALHO") or []:
            for t in trocos:
                cab = dobrar(str(t)[:JANELA_DO_CABECALHO])
                for nome in _pragas_com_a_cultura_no_nome(cab, x):
                    out.append({"SALA_CHAVE": c.get("SALA_CHAVE"), "SOURCE_ID": c.get("SOURCE_ID"),
                                "RAW_OBSERVATION_ID": c.get("RAW_OBSERVATION_ID", NAO_SEI),
                                "URL": c.get("URL", NAO_SEI), "PUBLISHED_AT": c.get("PUBLISHED_AT", NAO_SEI),
                                "CULTURA": x, "PRAGA": nome, "ESTADO_NO_BOLETIM": "CITADA",
                                "TRECHO": str(t)[:JANELA_DO_CABECALHO],
                                "ORIGEM_DO_PAR": "cabecalho de boletim de uma cultura (X3h) com a praga "
                                                 "que traz a cultura no nome"})
    for it in livro or []:
        secoes = (it.get("PROBLEMA") or {}).get("SECOES") if isinstance(it.get("PROBLEMA"), dict) else None
        secoes = secoes if isinstance(secoes, list) else it.get("SECOES")
        if not isinstance(secoes, list):
            continue
        for s in secoes:
            if not isinstance(s, dict) or not s.get("CULTURA"):
                continue        # texto antes da 1.a cultura nao herda cultura (boletim_do_campo)
            for p in s.get("PROBLEMAS") or []:
                out.append({"SALA_CHAVE": it.get("SALA_CHAVE") or it.get("ITEM_ID"),
                            "SOURCE_ID": it.get("SOURCE_ID"),
                            "RAW_OBSERVATION_ID": it.get("RAW_OBSERVATION_ID", NAO_SEI),
                            "DOCUMENT_ID": it.get("DOCUMENT_ID", NAO_SEI),
                            "URL": it.get("URL", NAO_SEI), "PUBLISHED_AT": it.get("PUBLISHED_AT", NAO_SEI),
                            "CULTURA": s["CULTURA"], "PRAGA": p.get("NOME") or p.get("FORMA"),
                            "ESTADO_NO_BOLETIM": p.get("ESTADO", NAO_SEI), "TRECHO": p.get("TRECHO"),
                            "ORIGEM_DO_PAR": "livro: PROBLEMA.SECOES (leis/boletim_do_campo.ler_boletim)"})
    vistos, unicos = set(), []
    for p in out:
        k = (p["SALA_CHAVE"], dobrar(p["CULTURA"]), dobrar(nome_do_problema(p["PRAGA"] or "")))
        if k not in vistos:
            vistos.add(k)
            unicos.append(p)
    return unicos


def _pragas_com_a_cultura_no_nome(texto, cultura):
    """«flavescenza dorata della vite», «mosca dell'olivo», «tignoletta della vite» escritos no cabecalho."""
    out = []
    for m in re.finditer(r"([a-z]+(?:\s+[a-z]+)?)\s+(?:della|dell['’ ]?|delle|del)\s*(%s)" %
                         "|".join(re.escape(f) for f in _formas_da_cultura(cultura)), texto):
        nome = m.group(0).strip()
        if nome.split()[0] in ("bollettino", "lotta", "difesa", "strategie", "consorzio", "fitosanitario"):
            nome = " ".join(nome.split()[1:])
        if nome and nome not in out:
            out.append(nome)
    return out


def portfolio_match(par_b: dict, ref: Referencia, adama_regs) -> dict:
    """O par cultura x praga do boletim -> os produtos ADAMA cujo rotulo lido tem essa cultura x alvo."""
    cultura, praga = par_b["CULTURA"], par_b["PRAGA"]
    k, a = canon_cultura(cultura), canon_alvo(praga)
    d = _data(par_b.get("PUBLISHED_AT"))
    ref_data = d or ref.data_do_cadastro
    base = {"PAR_DO_BOLETIM": {kk: par_b.get(kk) for kk in ("SALA_CHAVE", "SOURCE_ID", "URL", "PUBLISHED_AT",
                                                           "CULTURA", "PRAGA", "ESTADO_NO_BOLETIM",
                                                           "TRECHO", "ORIGEM_DO_PAR")},
            "CROP_ID": k or NAO_SEI, "TARGET_ID": a or NAO_SEI,
            "VALIDADE_REFERIDA_A": d.isoformat() if d else f"CADASTRO {ref.data_do_cadastro.isoformat()} "
                                                            f"(data do boletim NAO SEI)",
            "NAO_E": "o boletim recomendou — e o rotulo a cobrir o par que o boletim citou"}
    if a is None:
        return dict(base, ESTADO=PM_NAO_SEI, MOTIVO=f"a praga «{praga}» nao tem alvo no vocabulario do leitor "
                                                     "de rotulos: ligar a outro alvo seria inventar",
                    PRODUTOS=[], ESPECTRO=[])
    fortes = cobertura_da_cultura(cultura, adama_regs, ref, alvo=a, niveis=NIVEIS_FORTES)
    fracos = cobertura_da_cultura(cultura, adama_regs, ref, alvo=a, niveis=("DECLARACAO_DE_PRODUTO",))
    if k is None and not fortes["PROVAS"] and not fracos["PROVAS"]:
        return dict(base, ESTADO=PM_NAO_SEI, MOTIVO=f"a cultura «{cultura}» nao esta no vocabulario do leitor "
                                                     "de rotulos", PRODUTOS=[], ESPECTRO=[])

    def produtos(provas):
        por = {}
        for p in provas:
            por.setdefault(p["REGISTRATION_ID"], []).append(p)
        out = []
        for reg, ps in sorted(por.items()):
            linha = ref.cadastro.get(reg)
            val = validade(linha, ref_data, ref.data_do_cadastro, ref.cadastro_id)
            out.append({"REGISTRATION_ID": reg, "PRODUCT": ps[0]["PRODUCT"],
                        "PRODUCT_ID": ref.product_id.get(reg, NAO_SEI),
                        "EMPRESA": (linha or {}).get("ragione_sociale", NAO_SEI),
                        "SOSTANZE_ATTIVE": (linha or {}).get("sostanze_attive", NAO_SEI),
                        "VALIDADE": val, "REGISTO_VALIDO": val["VALIDO"],
                        "PROVA_DO_ROTULO": _limpa(ps, 2),
                        "DOSE_E_VOLUME_LITERAIS": _literais(_RX_DOSE, [x["_PAR"].get("CITACAO_DA_LINHA") for x in ps]) or NAO_SEI})
        return out
    fortes_p, fracos_p = produtos(fortes["PROVAS"]), produtos(fracos["PROVAS"])
    validos = [p for p in fortes_p if p["REGISTO_VALIDO"] == "SIM"]
    if validos and ref.autorizacao_a_confirmar:
        estado, motivo = PM_NAO_SEI, "D117: a edicao da referencia nao e conferida ha >= 30 dias — a confirmar"
    elif validos:
        estado = PM_MATCH
        motivo = f"{len(validos)} produto(s) ADAMA com {k or cultura} x {a} na mesma linha/bloco do rotulo lido e registo valido"
    elif fortes_p:
        estado, motivo = PM_NAO_SEI, ("A CONFIRMAR: ha par no rotulo, mas o registo nao se prova valido na "
                                      "data — " + fortes_p[0]["VALIDADE"]["MOTIVO"])
    elif fracos_p:
        estado, motivo = PM_ESPECTRO, ("so ha DECLARACAO_DE_PRODUTO (cultura e alvo em listas separadas do "
                                       "rotulo): espectro de produto nao e espectro na cultura")
    else:
        estado, motivo = PM_SEM_PAR, (f"nenhum par {k or cultura} x {a} nos rotulos lidos (cobertura "
                                      f"{ref.cobertura}); ausencia NA NOSSA LEITURA, nunca «a ADAMA nao tem»")
        if fortes["MOTIVOS"].get("GRAO_NAO_PROVADO"):
            estado, motivo = PM_NAO_SEI, "ha par com a chave do grupo, mas o grao nao esta provado pelo rotulo"
    return dict(base, ESTADO=estado, MOTIVO=motivo, PRODUTOS=fortes_p, ESPECTRO=fracos_p)


def competitive_set(substancias, d: date, ref: Referencia) -> dict:
    """Produtos de OUTRAS empresas no cadastro, com a substancia, validos na data `d`. So contagem e nomes."""
    subs = sorted({chave_substancia(s) for s in substancias if s})
    if not ref.tem_mercado:
        return {"SUBSTANCIAS": subs, "DATA_DE_REFERENCIA": d.isoformat() if d else NAO_SEI,
                "ESTADO": NAO_SEI, "LACUNA": LACUNAS["LACUNA-3_MERCADO_CONCORRENTE"],
                "GRAO": "SUBSTANCIA", "CULTURA_X_ALVO_DO_CONCORRENTE": NAO_SEI,
                "CONTAGEM": NAO_SEI, "CONTAGEM_ESTRITA": NAO_SEI, "EMPRESAS": [], "PRODUTOS": []}
    por = {}
    for linha in ref.linhas:
        if e_adama(linha):
            continue
        comuns = [s for s in subs if tem_substancia(linha, s)]
        if not comuns:
            continue
        val = validade(linha, d, ref.data_do_cadastro, ref.cadastro_id)
        if val["VALIDO"] != "SIM":
            continue
        por[linha["num_registrazione"]] = {
            "NUM_REGISTRAZIONE": linha["num_registrazione"], "PRODOTTO": linha.get("denominazione_prodotto"),
            "EMPRESA": linha.get("ragione_sociale"), "STATO": linha.get("stato_amministrativo"),
            "SOSTANZE_ATTIVE": linha.get("sostanze_attive"), "SUBSTANCIA_EM_COMUM": comuns,
            "IMPORTAZIONE_PARALLELA": linha.get("importazione_parallela"),
            "T4_REGISTRATION_EVIDENCE_ID": f"{ref.cadastro_id}:{linha['num_registrazione']}",
            "ESTRITO": "AUTORIZZATO" in str(linha.get("stato_amministrativo") or "").upper()}
    produtos = sorted(por.values(), key=lambda x: (x["EMPRESA"] or "", x["PRODOTTO"] or ""))
    return {"SUBSTANCIAS": subs, "DATA_DE_REFERENCIA": d.isoformat(), "ESTADO": "MEDIDO",
            "GRAO": "SUBSTANCIA (o cadastro FTS6 nao tem cultura nem alvo; rotulos de concorrentes nao lidos)",
            "CULTURA_X_ALVO_DO_CONCORRENTE": NAO_SEI,
            "CONTAGEM": len(produtos), "CONTAGEM_ESTRITA": sum(1 for p in produtos if p["ESTRITO"]),
            "CRITERIO": "estado ativo (Autorizzato*/Ri-registrato/Rinnovato, fontes/adama_it_intelligence.py) "
                        "e valido na data; ESTRITA = so «Autorizzato*» (provas/chain.py: Ri-registrato e ambiguo)",
            "EMPRESAS": sorted({p["EMPRESA"] for p in produtos}),
            "PRODUTOS": produtos}


# ── a corrida inteira ────────────────────────────────────────────────────────
def analisar(analise: dict, ref: Referencia, livro=None) -> dict:
    crossings = analise.get("CROSSINGS") or []
    refeitos = []
    for c in crossings:
        r = refazer(c, ref)
        if r["DEPOIS"] == YES_A_CONFIRMAR:
            r["CONFIRMACAO"] = confirmar(r, c, ref)
            r["FINAL"] = r["CONFIRMACAO"]["ESTADO"]
        else:
            r["FINAL"] = r["DEPOIS"]
        refeitos.append(r)
    adama_regs = sorted({r for r, linha in ref.cadastro.items() if linha and e_adama(linha)
                         and r in ref.pares_do_reg})
    pms = [portfolio_match(p, ref, adama_regs) for p in pares_do_boletim(analise, livro)]
    for pm in pms:
        subs = sorted({t for p in pm["PRODUTOS"] if p["REGISTO_VALIDO"] == "SIM"
                       for t in str(p["SOSTANZE_ATTIVE"]).split("|")})
        d = _data(pm["PAR_DO_BOLETIM"].get("PUBLISHED_AT")) or ref.data_do_cadastro
        pm["COMPETITIVE_SET"] = competitive_set(subs, d, ref) if subs else None
    for r in refeitos:
        if r["FINAL"] == CONFIRMED_YES or (r["FINAL"] == YES_A_CONFIRMAR and r.get("CONFIRMACAO")):
            d = _data(r["CONFIRMACAO"]["DATA_DO_BOLETIM"])
            r["COMPETITIVE_SET"] = competitive_set([r["SUBSTANCIA"]], d, ref)
    return {"REFEITOS": refeitos, "PORTFOLIO": pms, "CONTAGENS": contar(refeitos, pms)}


def contar(refeitos, pms) -> dict:
    def mudancas(filtro):
        sel = [r for r in refeitos if r["ANTES"] == filtro]
        return {"TOTAL": len(sel), "DEPOIS": dict(Counter(r["FINAL"] for r in sel)),
                "GANHARAM_CULTURA_PELO_GRAO": sum(1 for r in sel if r["GANHAS_PELO_GRAO"]),
                "PERDERAM_CULTURA_PELO_GRAO": sum(1 for r in sel if r["PERDIDAS_PELO_GRAO"])}
    return {
        "ANTES": dict(Counter(r["ANTES"] for r in refeitos)),
        "DEPOIS": dict(Counter(r["FINAL"] for r in refeitos)),
        "OS_48_PARTIAL": mudancas(PARTIAL),
        "OS_5_YES_A_CONFIRMAR": mudancas(YES_A_CONFIRMAR),
        "OS_29_NO": mudancas(NO),
        "NOT_POSSIBLE": mudancas(NOT_POSSIBLE),
        "PORTFOLIO_PARES": len(pms),
        "PORTFOLIO_POR_ESTADO": dict(Counter(p["ESTADO"] for p in pms)),
        "COMPETITIVE_SETS": sum(1 for p in pms if (p.get("COMPETITIVE_SET") or {}).get("ESTADO") == "MEDIDO")
        + sum(1 for r in refeitos if (r.get("COMPETITIVE_SET") or {}).get("ESTADO") == "MEDIDO"),
        "COMPETITIVE_SETS_NAO_SEI_LACUNA_3": sum(1 for p in pms if (p.get("COMPETITIVE_SET") or {}).get("ESTADO") == NAO_SEI)
        + sum(1 for r in refeitos if (r.get("COMPETITIVE_SET") or {}).get("ESTADO") == NAO_SEI),
    }


# ── (5) os objetos para o pote v2 ────────────────────────────────────────────
def _prova(x) -> dict:
    """O elemento de PROVA do objeto: o item do boletim. DOCUMENT_ID vem do item, ou fica NAO SEI —
    e o pote recusa, a vista (defeito C1 da R7: as 38 novas nao tem document_key)."""
    return {"ITEM_ID": x.get("SALA_CHAVE") or NAO_SEI,
            "RAW_OBSERVATION_ID": x.get("RAW_OBSERVATION_ID", NAO_SEI),
            "SOURCE_ID": x.get("SOURCE_ID") or NAO_SEI,
            "DOCUMENT_ID": x.get("DOCUMENT_ID") or NAO_SEI,
            "CORRIDA_UPSTREAM": NAO_SEI,
            "URL": x.get("URL") or NAO_SEI,
            "PUBLICADO_EM": x.get("PUBLISHED_AT") or NAO_SEI}


def _oid(*partes) -> str:
    return "XMAX-" + hashlib.sha256("|".join(str(p) for p in partes).encode()).hexdigest()[:16]


def itens_do_pote(res: dict, ref: Referencia) -> dict:
    """ITENS_POR_FERRAMENTA no contrato de entrada do pote v2 (pacote/pote_intelligence_casco.py).

    ESPECIE = CROSSING (nenhum destes objetos e SINAL nem OPORTUNIDADE). O estado viaja em CHAVES e, por
    o compartimento portfolio nao ter vaga para ele, sai em FORA_DO_CONTRATO com o nome e o valor.
    """
    portfolio, competitors = [], []
    for r in res["REFEITOS"]:
        if r["FINAL"] == NOT_POSSIBLE:
            continue
        conf = r.get("CONFIRMACAO") or {}
        base_chaves = {"CROP_ID": NAO_SEI, "TARGET_ID": NAO_SEI, "ACTIVE_INGREDIENT_ID": r["SUBSTANCIA"],
                       "CROSSING_STATE": r["FINAL"], "CRUZAMENTO": "ROTULO_X_SUBSTANCIA_CITADA_NO_BOLETIM"}
        confirmam = [p for p in conf.get("PRODUTOS") or [] if p["CONFIRMA"]]
        if confirmam:
            for p in confirmam:
                portfolio.append({
                    "OBJETO_ID": _oid(r["OBJETO_ID"], p["REGISTRATION_ID"]), "ESPECIE": "CROSSING",
                    "ESTADO": ESTADO_TRANSPORTAVEL,
                    "CHAVES": dict(base_chaves, PRODUCT_ID=p["PRODUCT_ID"],
                                   CROP_ID=canon_cultura(conf["CULTURA"]) or NAO_SEI,
                                   REGISTRATION_VERSION=f"{ref.cadastro_id}:{p['REGISTRATION_ID']}",
                                   PRODUCT=p["PRODUCT"], VALIDO_EM=conf["DATA_DO_BOLETIM"]),
                    "PROVA": [_prova(r)],
                    "PORQUE": f"{r['FINAL']}: {conf['MOTIVO']}. Rotulo: "
                              f"{(p['CULTURA_NO_ROTULO_PROVA'] or [{}])[0].get('EVIDENCIA')}",
                    "INCERTEZA": conf["REGRA_DE_ENTRADA"],
                    "CONTRADIZ": NAO_SEI})
        else:
            portfolio.append({
                "OBJETO_ID": _oid(r["OBJETO_ID"]), "ESPECIE": "CROSSING", "ESTADO": ESTADO_TRANSPORTAVEL,
                "CHAVES": dict(base_chaves, PRODUCT_ID=NAO_SEI, REGISTRATION_VERSION=NAO_SEI,
                               PRODUTOS_ADAMA=r["PRODUTOS_ADAMA"]),
                "PROVA": [_prova(r)],
                "PORQUE": f"{r['FINAL']}: {conf.get('MOTIVO') or r['MOTIVO']}",
                "INCERTEZA": "ausencia NA NOSSA LEITURA de rotulos (cobertura " + str(ref.cobertura) + ")",
                "CONTRADIZ": NAO_SEI})
        cs = r.get("COMPETITIVE_SET")
        if cs:
            competitors += _objetos_cs(cs, r, canon_cultura(conf.get("CULTURA")) or NAO_SEI, ref)
    for pm in res["PORTFOLIO"]:
        pb = pm["PAR_DO_BOLETIM"]
        prova = [_prova(dict(pb, RAW_OBSERVATION_ID=_raw(res, pb)))]
        validos = [p for p in pm["PRODUTOS"] if p["REGISTO_VALIDO"] == "SIM"]
        for p in validos or [None]:
            portfolio.append({
                "OBJETO_ID": _oid("PM", pb["SALA_CHAVE"], pb["CULTURA"], pb["PRAGA"], p and p["REGISTRATION_ID"]),
                "ESPECIE": "CROSSING", "ESTADO": ESTADO_TRANSPORTAVEL,
                "CHAVES": {"PRODUCT_ID": p["PRODUCT_ID"] if p else NAO_SEI, "CROP_ID": pm["CROP_ID"],
                           "TARGET_ID": pm["TARGET_ID"],
                           "ACTIVE_INGREDIENT_ID": p["SOSTANZE_ATTIVE"] if p else NAO_SEI,
                           "REGISTRATION_VERSION": f"{ref.cadastro_id}:{p['REGISTRATION_ID']}" if p else NAO_SEI,
                           "CROSSING_STATE": pm["ESTADO"], "CRUZAMENTO": "PORTFOLIO_MATCH",
                           "PRODUCT": p["PRODUCT"] if p else NAO_SEI,
                           "PAR_DO_BOLETIM": f"{pb['CULTURA']} x {pb['PRAGA']}"},
                "PROVA": prova, "PORQUE": f"{pm['ESTADO']}: {pm['MOTIVO']}",
                "INCERTEZA": "o rotulo cobre o par; o boletim nao recomendou produto nenhum",
                "CONTRADIZ": NAO_SEI})
        if pm.get("COMPETITIVE_SET"):
            competitors += _objetos_cs(pm["COMPETITIVE_SET"], dict(pb, OBJETO_ID=pb["SALA_CHAVE"],
                                                                    RAW_OBSERVATION_ID=_raw(res, pb)),
                                       pm["CROP_ID"], ref)
    return {"portfolio": portfolio, "competitors": competitors}


def _raw(res, pb):
    """O RAW_OBSERVATION_ID do par, se o proprio par o trouxer (o corte vertical da R7 nao o trouxe)."""
    return pb.get("RAW_OBSERVATION_ID", NAO_SEI)


def _objetos_cs(cs, origem, crop_cs, ref):
    out = []
    for p in cs["PRODUTOS"]:
        out.append({
            "OBJETO_ID": _oid("CS", origem.get("OBJETO_ID") or origem.get("SALA_CHAVE"), p["NUM_REGISTRAZIONE"]),
            "ESPECIE": "CROSSING", "ESTADO": ESTADO_TRANSPORTAVEL,
            "CHAVES": {"COMPANY_ID": p["EMPRESA"], "PRODUCT_ID": f"{ref.cadastro_id}:{p['NUM_REGISTRAZIONE']}",
                       "CROP_ID": NAO_SEI, "FACT_LOCATION": "ITALIA (registo nacional do Ministero)",
                       "FACT_TIME": cs["DATA_DE_REFERENCIA"],
                       "T4_REGISTRATION_EVIDENCE_ID": p["T4_REGISTRATION_EVIDENCE_ID"],
                       "CRUZAMENTO": "COMPETITIVE_SET", "GRAO": "SUBSTANCIA",
                       "SUBSTANCIA_EM_COMUM": p["SUBSTANCIA_EM_COMUM"], "PRODOTTO": p["PRODOTTO"],
                       "CULTURA_DO_PAR_ADAMA": crop_cs},
            "PROVA": [_prova(origem)],
            "PORQUE": f"COMPETITIVE_SET: registo {p['NUM_REGISTRAZIONE']} ({p['STATO']}) com "
                      f"{', '.join(p['SUBSTANCIA_EM_COMUM'])}, valido em {cs['DATA_DE_REFERENCIA']}",
            "INCERTEZA": "grao = substancia: a cultura x alvo no rotulo deste concorrente NAO SEI",
            "CONTRADIZ": NAO_SEI})
    return out


# ── CLI ──────────────────────────────────────────────────────────────────────
def _head() -> str:
    try:
        return subprocess.run(["git", "-C", ROOT, "rev-parse", "HEAD"], capture_output=True, text=True,
                              check=True).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        return NAO_SEI


def correr(livro=None, caminhos=None, hoje: date | None = None, referencia: dict | None = None) -> dict:
    """A analise inteira. A referencia vem da PORTA (uma edicao); `hoje` decide o frescor (D117)."""
    cam = dict(R7=R7, **(caminhos or {}))
    analise = json.load(open(cam["R7"], encoding="utf-8"))
    ref = Referencia.da_porta(referencia if referencia is not None else PORTA.abrir(hoje=hoje))
    res = analisar(analise, ref, livro)
    itens = itens_do_pote(res, ref)
    carimbo = dict(ref.carimbo)
    return {
        "SCHEMA": SCHEMA, "MARCA": MARCA, "NAO_PARA_CLIENTE": True,
        "CORRIDA_DE_ORIGEM": analise.get("INTELLIGENCE_RUN_ID", NAO_SEI),
        "LIDO_SOBRE_A_ARVORE": _head(),
        "INSUMOS": {k: {"CAMINHO": os.path.relpath(v, ROOT), "SHA256": _sha256(v)} for k, v in cam.items()},
        "REFERENCIA_ADAMA": carimbo,
        "LACUNAS_DA_REFERENCIA": LACUNAS,
        "LIVRO_DAS_SECOES": "ENTREGUE PELO COORDENADOR" if livro else "NAO (so os pares que o repo guarda)",
        "COBERTURA_DOS_ROTULOS": ref.cobertura,
        "TABELA_DE_GRAO": ref.grao,
        "GRUPOS_DO_LEITOR": sorted(GRUPOS_DO_LEITOR),
        "CONTAGENS": res["CONTAGENS"],
        "REFEITOS": res["REFEITOS"],
        "PORTFOLIO": res["PORTFOLIO"],
        "ITENS_POR_FERRAMENTA": {k: len(v) for k, v in itens.items()},
        "_ITENS": itens,
    }


def main(argv=None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    livro = None
    if argv and argv[0] in ("-h", "--help"):
        print(__doc__.strip().split("\n\n")[0])
        print("\n  uso: python3 motor/cruzamentos_max.py [--hoje AAAA-MM-DD] [--livro LIVRO-COM-SECOES.json] [--saida X.json]")
        return 0
    saida, saida_itens = SAIDA, SAIDA_ITENS
    if "--livro" in argv:
        livro = json.load(open(argv[argv.index("--livro") + 1], encoding="utf-8"))
        livro = livro.get("ITENS") if isinstance(livro, dict) else livro
    if "--saida" in argv:
        saida = argv[argv.index("--saida") + 1]
        saida_itens = os.path.splitext(saida)[0] + "-ITENS-DO-POTE.json"
    hoje = date.fromisoformat(argv[argv.index("--hoje") + 1]) if "--hoje" in argv else None
    out = correr(livro, hoje=hoje)
    itens = out.pop("_ITENS")
    with open(saida, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
        f.write("\n")
    with open(saida_itens, "w", encoding="utf-8") as f:
        json.dump({"SCHEMA": SCHEMA + "/ITENS_POR_FERRAMENTA", "MARCA": MARCA, "NAO_PARA_CLIENTE": True,
                   "CORRIDA_DE_ORIGEM": out["CORRIDA_DE_ORIGEM"], "ITENS_POR_FERRAMENTA": itens},
                  f, ensure_ascii=False, indent=1)
        f.write("\n")
    c = out["CONTAGENS"]
    print(f"{MARCA} · {SCHEMA} · origem {out['CORRIDA_DE_ORIGEM']}")
    print(f"  86 antes  {c['ANTES']}")
    print(f"  86 depois {c['DEPOIS']}")
    print(f"  48 PARTIAL -> {c['OS_48_PARTIAL']['DEPOIS']}   5 YES -> {c['OS_5_YES_A_CONFIRMAR']['DEPOIS']}")
    print(f"  portfolio {c['PORTFOLIO_PARES']} pares {c['PORTFOLIO_POR_ESTADO']} · competitive sets "
          f"{c['COMPETITIVE_SETS']} · itens {out['ITENS_POR_FERRAMENTA']}")
    print(f"  -> {os.path.relpath(saida, ROOT)} · {os.path.relpath(saida_itens, ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
