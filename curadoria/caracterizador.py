#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""CARACTERIZAR UMA FONTE — de «a URL abriu» para «eu conheco esta fonte».

    UM EXEMPLO PROVA QUE A FONTE FUNCIONA.
    NAO PROVA O QUE ELA NORMALMENTE PUBLICA.

Um unico item pode ser excepcional: o comunicado do ano numa fonte que so
publica editais, ou o unico video de campo num canal institucional. Decidir
cadencia, temas e rendimento a partir de UM item e generalizar de uma amostra
de tamanho 1 — e uma taxa sem denominador e uma impressao.

    CONNECTIVITY_PROVEN != SOURCE_CHARACTERIZED != ONBOARDING_READY

Os tres sao estados distintos, e uma fonte pode legitimamente estar no
primeiro e nao nos outros dois.

A AMOSTRAGEM E ADAPTATIVA, E PARA QUANDO APRENDE
-------------------------------------------------
Comeca em 3 itens. Se o padrao estabilizar, para. Se houver heterogeneidade,
sobe ate ao tecto. O tecto NAO e uma meta: uma fonte com 4 itens no universo
inteiro fica com 4, e isso e `SAMPLE_IS_FULL_AVAILABLE_UNIVERSE`, nao uma
amostra pobre.

    10 NAO E UM NUMERO OBRIGATORIO.
    O QUE MANDA PARAR E O PADRAO TER ESTABILIZADO.

⚠️ E O INDICE ENSINA O QUE O CONTEUDO NAO ENSINA — E VICE-VERSA
---------------------------------------------------------------
    DO INDICE   quantos itens ha, que datas, que profundidade, que categorias
    DO ITEM     que tipo de conteudo, que temas, que geografia, que lingua

Contar itens pelo indice e legitimo. Caracterizar CONTEUDO pelo indice nao e:
foi esse o bug da missao anterior (`LISTING != CONTENT ITEM`).
"""
from __future__ import annotations

import json
import re
import statistics
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "curadoria"))
import capturador as CAP  # noqa: E402

CONTRATO = "SOURCE_CHARACTERIZATION/v1"

AMOSTRA_INICIAL = 3
AMOSTRA_TECTO = 10


# ─────────────────────────────────────────────────────────────────────────
# VOCABULARIO — reutilizado da casa quando existe
# ─────────────────────────────────────────────────────────────────────────
# ⚠️ ACTIVIDADE E CADENCIA SAO EIXOS DIFERENTES. Um canal pode ter publicado
# 40 videos numa semana e estar calado ha dois anos: ritmo alto, actividade
# nula. Achata-los faz uma fonte morta parecer a melhor da base.
ACTIVIDADE = (
    "ACTIVE_HIGH_FREQUENCY",     # publica e publicou agora
    "ACTIVE_MEDIUM_FREQUENCY",
    "ACTIVE_LOW_FREQUENCY",
    "SEASONAL",                  # janelas regulares com silencio entre elas
    "DORMANT",                   # sem publicacao ha mais de um ano
    "UNKNOWN",                   # ninguem mediu — NAO e DORMANT
)

# ⚠️ DORMANT != IRRELEVANT, e LOW_YIELD != LOW_VALUE.
# Uma fonte regulatoria que publica 4x por ano nao e fraca: e rara e decisiva
# (INT-LAW-296). O Curator mede PRODUCAO; VALOR mede-se depois, e nao aqui.
POR_QUE_DORMANT_NAO_E_RECUSA = (
    "uma fonte parada continua dona do que ja publicou, e o arquivo dela pode "
    "ser exactamente o que uma pergunta historica precisa. O que muda nao e a "
    "relevancia — e a CADENCIA com que se volta la."
)

TIPOS_DE_COBERTURA = (
    "PHYTOSANITARY", "CLIMATE", "REGULATORY", "SCIENCE", "PORTFOLIO",
    "MARKET", "TECHNICAL_FIELD_SIGNAL", "COMPETITOR_COMMUNICATION",
    "AGRICULTURAL_NEWS", "OTHER", "UNKNOWN",
)

# Sinais lexicais, em italiano — a lingua das fontes. Cada tema precisa de
# termos que NAO apareçam em qualquer pagina institucional.
SINAIS = {
    "PHYTOSANITARY": r"fitosanitar|fitopatolog|avversit|parassit|peronospor|oidio|"
                     r"cimice|dorifora|tignola|botrite|mosca dell|difesa integrata|"
                     r"bollettino fitosanitario|soglia di intervento|antiparassitar",
    "CLIMATE":       r"meteo|meteorolog|precipitazion|temperatur|siccit|gelat|"
                     r"agrometeo|previsioni|pioggia|umidit relativa|bollettino agrometeo",
    "REGULATORY":    r"decreto|delibera|determina|regolamento|normativa|gazzetta|"
                     r"bando|graduatoria|autorizzazione|revoca|disciplinare|"
                     r"registro nazionale|PSR|PAC",
    "SCIENCE":       r"ricerca|sperimentazion|prova di campo|pubblicazion scientif|"
                     r"convegno|tesi|dottorat|articolo scientific|rivista|abstract",
    "MARKET":        r"prezzi|mercato|quotazion|borsa merci|export|import|"
                     r"produzione stimata|listino|domanda e offerta|fatturato",
    "TECHNICAL_FIELD_SIGNAL": r"monitoraggio|rilievo|trappol|catture|stazione di|"
                              r"rete di monitoraggio|campionament|infestazion",
    "PORTFOLIO":     r"prodotto|formulato|etichetta|catalogo|scheda tecnica|"
                     r"sostanza attiva|dose|coltura target",
    "COMPETITOR_COMMUNICATION": r"syngenta|bayer|basf|corteva|adama|sipcam|"
                                r"gowan|certis|biolchim|valagro|isagro",
    "AGRICULTURAL_NEWS": r"notizie|attualit|comunicato|rassegna|intervista|editoriale",
}

# Regioes italianas — para GEOGRAPHIES_OBSERVED. O nome tem de aparecer no
# conteudo, nao no dominio: onde a fonte esta != sobre onde ela fala.
REGIOES = ("abruzzo", "basilicata", "calabria", "campania", "emilia-romagna",
           "friuli", "lazio", "liguria", "lombardia", "marche", "molise",
           "piemonte", "puglia", "sardegna", "sicilia", "toscana",
           "trentino", "umbria", "valle d'aosta", "veneto", "bolzano", "trento")

CULTURAS = ("vite", "uva", "olivo", "oliva", "grano", "frumento", "mais", "riso",
            "pomodoro", "melo", "pero", "pesco", "agrumi", "arancia", "limone",
            "nocciol", "mandorl", "soia", "girasole", "barbabietola", "patata",
            "orticol", "vivaismo", "floricol")


def texto_de(b: bytes) -> str:
    """Texto legivel de um HTML/PDF/XML, o suficiente para contar termos.

    ⚠️ INCLUI AS METATAGS OPEN GRAPH, E ISSO NAO E UM EXTRA. Medido: uma pagina
    de Facebook com 981 KB devolve 58 caracteres de texto visivel — o conteudo
    e montado por JavaScript, e 189 blocos `<script>` nao dizem nada a quem le
    o HTML. Mas a propria pagina declara quem e em `og:title` e `og:description`:

        og:description = «Provincia autonoma di Trento - Pagina Ufficiale,
                          Trento. Follower: 105.998 …»

    Sem elas, 14 fontes reais ficariam «sem sinal tematico» por um defeito de
    leitura — a repeticao exacta do erro que ja custou caro nesta casa.

        LER SO O QUE ESTA VISIVEL NAO E LER A PAGINA.
        E isto NAO contorna muro nenhum: sao metatags publicas, servidas a
        qualquer cliente anonimo, e e o proprio site que as poe la para ser lido.
    """
    metas = " ".join(m.decode("utf-8", "replace") for m in re.findall(
        rb'<meta[^>]+(?:property|name)="(?:og:title|og:description|description|'
        rb'twitter:title|twitter:description)"[^>]+content="([^"]{0,600})"', b, re.I))
    if b[:4] == b"%PDF":
        # os PDF nao se abrem aqui; o que se le e o que estiver em claro
        t = b.decode("latin-1", "ignore")
    else:
        t = b.decode("utf-8", "replace")
    t = re.sub(r"(?is)<(script|style)[^>]*>.*?</\1>", " ", t)
    t = re.sub(r"(?s)<[^>]+>", " ", t)
    return re.sub(r"\s+", " ", metas + " " + t).lower()


def temas_de(txt: str) -> list[str]:
    """Temas com sinal MEDIDO no texto. Sem sinal, `UNKNOWN` — nunca `OTHER`
    por defeito, porque `OTHER` afirma que se olhou e nao se encaixou."""
    achados = []
    for tema, rx in SINAIS.items():
        n = len(re.findall(rx, txt))
        if n >= 2:                      # 1 ocorrencia pode ser um menu
            achados.append((tema, n))
    achados.sort(key=lambda x: -x[1])
    return [t for t, _ in achados[:4]] or ["UNKNOWN"]


def geografias_de(txt: str) -> list[str]:
    return sorted({r for r in REGIOES if txt.count(r) >= 2})


def culturas_de(txt: str) -> list[str]:
    return sorted({c for c in CULTURAS if txt.count(c) >= 2})


def lingua_de(txt: str) -> str:
    it = len(re.findall(r"\b(della|degli|nella|sono|anche|questo|per il|con la)\b", txt))
    en = len(re.findall(r"\b(the|and|with|from|this|that|which)\b", txt))
    if it >= 5 and it > en:
        return "it"
    if en >= 5 and en > it:
        return "en"
    return "NAO SEI"


_DATA_ISO = re.compile(r"(20\d{2})-(\d{2})-(\d{2})")
_DATA_IT = re.compile(r"\b(\d{2})[/-](\d{2})[/-](20\d{2})\b")


def datas_de(txt_ou_bytes) -> list[str]:
    t = txt_ou_bytes if isinstance(txt_ou_bytes, str) else txt_ou_bytes.decode("utf-8", "replace")
    saida = {"%s-%s-%s" % m for m in _DATA_ISO.findall(t)}
    saida |= {"%s-%s-%s" % (a, m, d) for d, m, a in _DATA_IT.findall(t)}
    return sorted(saida)


# ─────────────────────────────────────────────────────────────────────────
# ESTABILIDADE — o criterio que manda parar de amostrar
# ─────────────────────────────────────────────────────────────────────────
def padrao_estavel(itens: list[dict]) -> tuple[str, str]:
    """A amostra ja ensina o padrao? Devolve (SIM|NAO|NAO SEI, porque).

    ⚠️ ESTABILIDADE NAO E «TODOS IGUAIS». E «a proxima amostra provavelmente
    nao muda a conclusao». Tres itens do mesmo tipo, com o mesmo tema
    dominante e todos com data, ja dizem o que a fonte publica. Tres itens de
    tres tipos diferentes nao dizem nada — pedem mais.
    """
    if len(itens) < 2:
        return "NAO SEI", "amostra de %d item: nao ha padrao a observar" % len(itens)

    tipos = Counter(i["ITEM_TYPE"] for i in itens)
    temas = Counter(t for i in itens for t in i["TOPICS"])
    com_data = sum(1 for i in itens if i["PUBLISHED_AT"] != "NAO SEI")

    tipo_dom = tipos.most_common(1)[0][1] / len(itens)
    tema_dom = (temas.most_common(1)[0][1] / len(itens)) if temas else 0
    taxa_data = com_data / len(itens)

    if tipo_dom >= 0.75 and tema_dom >= 0.5:
        return "SIM", ("%d itens: %.0f%% do mesmo tipo, tema dominante em %.0f%%, "
                       "data em %.0f%%" % (len(itens), tipo_dom * 100,
                                           tema_dom * 100, taxa_data * 100))
    return "NAO", ("%d itens heterogeneos: tipo dominante so %.0f%%, tema dominante "
                   "%.0f%% — a proxima amostra ainda pode mudar a conclusao"
                   % (len(itens), tipo_dom * 100, tema_dom * 100))


def actividade(datas: list[str], itens_n: int) -> tuple[str, str]:
    """ACTIVIDADE, que e recencia — nao ritmo. Ver a nota do enum."""
    if not datas:
        return "UNKNOWN", "nenhuma data legivel na amostra — NAO e DORMANT"
    try:
        ds = sorted({datetime.strptime(d, "%Y-%m-%d").replace(tzinfo=timezone.utc)
                     for d in datas})
    except Exception:
        return "UNKNOWN", "datas ilegiveis"
    ultimo = ds[-1]
    dias = (datetime.now(timezone.utc) - ultimo).days
    if dias > 365:
        return "DORMANT", ("ultimo conteudo datado ha %d dias (%s). %s"
                           % (dias, ultimo.date(), POR_QUE_DORMANT_NAO_E_RECUSA))
    if len(ds) < 3:
        return "UNKNOWN", "so %d datas distintas: recente, mas sem ritmo observavel" % len(ds)
    gaps = sorted((ds[i + 1] - ds[i]).days for i in range(len(ds) - 1))
    med = gaps[len(gaps) // 2]
    if med <= 9:
        return "ACTIVE_HIGH_FREQUENCY", "mediana %dd, ultimo ha %dd" % (med, dias)
    if med <= 45:
        return "ACTIVE_MEDIUM_FREQUENCY", "mediana %dd, ultimo ha %dd" % (med, dias)
    return "ACTIVE_LOW_FREQUENCY", "mediana %dd, ultimo ha %dd" % (med, dias)


def cadencia_inicial(act: str, familia: str) -> tuple[str, str]:
    """CADENCIA INICIAL — so de caracteristicas OBSERVAVEIS da fonte.

    ⚠️ NAO ENTRA VALOR AQUI. A Intelligence ainda nao existe e nao tem como
    opinar; usar «importancia» agora seria inventar a medida que falta. Entra
    ritmo observado, recencia e custo da rota — e mais nada.
    """
    base = {
        "ACTIVE_HIGH_FREQUENCY":   ("DAILY", "publica em dias ou dentro da semana"),
        "ACTIVE_MEDIUM_FREQUENCY": ("WEEKLY", "publica em semanas"),
        "ACTIVE_LOW_FREQUENCY":    ("MONTHLY", "publica em meses"),
        "SEASONAL":                ("SEASONAL_WINDOW", "janelas com silencio entre elas"),
        "DORMANT":                 ("QUARTERLY_WATCH", "parada ha mais de um ano: "
                                    "visita rara para detectar regresso, nao coleta regular"),
        "UNKNOWN":                 ("MONTHLY_PROBE", "ritmo nao medido: visita para medir, "
                                    "nao para colher"),
    }[act]
    if familia == "FACEBOOK" and base[0] in ("DAILY", "WEEKLY"):
        return "WEEKLY", base[1] + " · rebaixado: rota de navegador tem custo"
    return base


def relevancia(temas: list[str], geos: list[str], culturas: list[str],
               act: str) -> tuple[str, str]:
    """RELEVANTE PARA O SINTONIA? Decidida por evidencia, nao devolvida ao dono.

    ⚠️ «Ainda nao consegui ler» NAO sobe a humano. Sobe a humano ambiguidade
    SEMANTICA real: a fonte le-se, e mesmo assim nao se sabe se serve.
    """
    agro = [t for t in temas if t in ("PHYTOSANITARY", "CLIMATE", "REGULATORY",
                                      "SCIENCE", "MARKET", "TECHNICAL_FIELD_SIGNAL",
                                      "PORTFOLIO", "COMPETITOR_COMMUNICATION")]
    if agro and (geos or culturas):
        return "YES", ("temas agro medidos (%s) + %d regiao(oes) e %d cultura(s) "
                       "nomeadas no conteudo" % (", ".join(agro[:3]), len(geos), len(culturas)))
    if agro:
        return "YES", "temas agro medidos no conteudo: %s" % ", ".join(agro[:3])
    if culturas:
        return "YES", "culturas nomeadas no conteudo: %s" % ", ".join(culturas[:4])
    if temas == ["UNKNOWN"]:
        return "UNKNOWN", ("a amostra nao trouxe sinal tematico suficiente — falta "
                           "medida, nao julgamento")
    return "UNKNOWN", "temas %s sem ancora geografica nem de cultura" % ", ".join(temas[:3])


# ─────────────────────────────────────────────────────────────────────────
# O NOME DA CANDIDATA CONTRA O QUE A FONTE DIZ SER
# ─────────────────────────────────────────────────────────────────────────
_RUIDO = re.compile(r"\b(youtube|facebook|ufficiale|official|canale|canal|pagina|"
                    r"page|profilo|it|the|di|de|del|della|e|and|srl|spa|scpa|"
                    r"soc|coop|gruppo|group)\b", re.I)


def _palavras(nome: str) -> set:
    n = _RUIDO.sub(" ", nome.lower())
    n = re.sub(r"[^a-z0-9àèéìòù ]+", " ", n)
    return {p for p in n.split() if len(p) >= 4}


def identidade_bate(nome_da_fila: str, url: str, titulos: list[str]) -> tuple[str, str]:
    """O NOME QUE A FILA DECLARA APARECE NO QUE A FONTE PUBLICA?

    ⚠️ ESTE TESTE EXISTE POR UM CASO MEDIDO. Uma candidata registada como
    «Valagro — Youtube ufficiale» aponta para `youtube.com/@syngenta`, e os
    videos sao todos da Syngenta: a Valagro foi absorvida, e o canal e do
    comprador. A captura funciona, o conteudo e real, a fonte e boa — e a
    FICHA esta errada sobre quem ela e.

        REBRANDING E AQUISICAO NAO PARTEM O ENDERECO: PARTEM A IDENTIDADE.
        Uma captura com HTTP 200 nao acusa isto, porque nao ha nada avariado.

    Promover assim poria no Atlas uma ficha com o nome do vendido e o conteudo
    do comprador — e o erro atravessaria calado, porque tudo «funciona».
    Isto NAO e recusa: e `SEMANTIC_REVIEW_REQUIRED`, ambiguidade semantica
    genuina, que e exactamente o caso que a lei manda levar a humano.
    """
    nome_p = _palavras(nome_da_fila)
    if not nome_p:
        return "NAO SEI", "nome da fila sem palavras distintivas"

    handle = ""
    m = re.search(r"(?:@|company/|/c/|/user/|facebook\.com/)([^/?#]+)", url or "")
    if m:
        handle = m.group(1).lower()

    corpo = " ".join(titulos).lower()
    achou_no_conteudo = any(p in corpo for p in nome_p)
    achou_no_handle = any(p in handle for p in nome_p)

    if achou_no_handle or achou_no_conteudo:
        return "SIM", ("o nome declarado aparece %s"
                       % ("no endereco" if achou_no_handle else "no conteudo publicado"))

    CONCORRENTES = ("syngenta", "bayer", "basf", "corteva", "adama", "sipcam",
                    "yara", "nufarm", "upl", "certis", "biolchim", "koppert")

    # ⚠️ NO HANDLE, UMA OCORRENCIA BASTA. O endereco e uma declaracao de
    # identidade — `youtube.com/@syngenta` DIZ de quem e o canal. No corpo
    # exige-se 2, porque uma mencao solta pode ser uma parceria citada.
    no_handle = [e for e in CONCORRENTES if e in handle and e not in " ".join(nome_p)]
    if no_handle:
        return "NAO", ("o ENDERECO declara «%s» e a ficha diz «%s». O endereco e a "
                       "declaracao mais forte de identidade que uma plataforma da. "
                       "Aquisicao/rebranding provavel: a fonte funciona, a FICHA e que "
                       "esta errada sobre quem ela e."
                       % (no_handle[0], nome_da_fila.split("—")[0].strip()))

    no_corpo = [e for e in CONCORRENTES
                if corpo.count(e) >= 2 and e not in " ".join(nome_p)]
    if no_corpo:
        return "NAO", ("o conteudo nomeia consistentemente «%s», e nao «%s». "
                       "Possivel aquisicao/rebranding — a fonte funciona, a FICHA e "
                       "que pode estar errada sobre quem ela e."
                       % (no_corpo[0], nome_da_fila.split("—")[0].strip()))
    return "NAO SEI", ("o nome declarado nao aparece nem no endereco nem nos "
                       "titulos amostrados — pode ser so estilo editorial")


if __name__ == "__main__":
    print("CONTRATO %s" % CONTRATO)
    print("actividade: %s" % ", ".join(ACTIVIDADE))
    print("cobertura : %s" % ", ".join(TIPOS_DE_COBERTURA))
    print("amostra   : inicial %d · tecto %d (tecto NAO e meta)"
          % (AMOSTRA_INICIAL, AMOSTRA_TECTO))
