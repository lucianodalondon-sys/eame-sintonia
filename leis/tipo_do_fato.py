#!/usr/bin/env python3
"""O TIPO DO FACTO AGRO (agro_fact_kind), TIRADO DO CORPO DO TEXTO — uma etiqueta, nunca um filtro.

    tipo_do_fato(texto) -> {"agro_fact_kind", "agro_fact_kind_basis", "EVIDENCIA"}
    fato_com_tipo(texto, publication_time=None, publication_time_basis=None) -> campos_do_fato + agro_fact_kind

Funcao PURA (sem rede, sem banco, sem ficheiros). Taxonomia v2 (D62 + D71-D73), proposta e medida em
`scripts/regua_fato/` (protocolo + adenda 1, gabarito, prova cega):

    CAMPO_FITOSSANITARIO · CAMPO_CLIMA · CAMPO_PRODUCAO_COLHEITA · MERCADO_PRECO · MERCADO_VAREJO ·
    EVENTO_TECNICO · REGULATORIO_MOLECULA · NEGOCIO_AGRO · MARKETING_CONCORRENCIA · INSTITUCIONAL ·
    NAO_FATO · NAO_SEI

O nome do campo e `agro_fact_kind` (D73): `FACT_KIND` ja existe em superficie/ask_sintonia.py com outro
sentido (frescura da resposta do benchmark).

Regras (mesmo metodo das reguas T1/T2):
  1. SO O CORPO. Menu, cabecalho e rodape nao contam: usa-se `fato_do_texto.corpo` (a mesma regra do
     lugar e do tempo do facto), e as linhas em MAIUSCULAS saem. Sem corpo = NAO_SEI.
  2. CONCEITOS POR PALAVRA INTEIRA. Conta-se quantos conceitos DIFERENTES do tipo aparecem no corpo.
     Um tipo precisa de >= MINIMO_DE_CONCEITOS.
  3. O EVENTO E O FACTO (D62). Evento tecnico anunciado na abertura, com ligacao agro escrita, e
     EVENTO_TECNICO — salvo se for uma EMPRESA a mostrar os proprios produtos no evento (D72: MARKETING).
     Evento sem agro nao e evento tecnico; aviso academico tambem nao.
  4. MARKETING_CONCORRENCIA (D72): voz de empresa a promover os proprios produtos. D71: se o assunto
     tecnico (praga, clima, producao) pesa tanto ou mais, vence o tipo tecnico.
  5. MERCADO_VAREJO (D73): mercado com prova de varejo no CORPO (loja, insignia, e-commerce, prateleira,
     GDO). Abertura/operacao de loja sem facto de produto = INSTITUCIONAL.
  6. NEGOCIO precisa de ligacao agro escrita e de mais conceitos que os outros (palavras genericas).
  7. EMPATE OU SINAL FRACO = NAO_SEI.
  8. SEM CONCEITO NENHUM, com corpo: agro escrito (>= 2 palavras) = INSTITUCIONAL; agro nenhum =
     NAO_FATO; o meio = NAO_SEI. Um titulo solto nunca chega para dizer INSTITUCIONAL ou NAO_FATO.

Nada e descartado: NAO_SEI e uma resposta valida e o item segue como estava.

LIGACAO AO LUGAR E AO TEMPO (`fato_com_tipo`): o lugar/tempo de EVENTO ou de MERCADO nunca preenche um
facto CAMPO_*; um EVENTO_TECNICO so usa lugar/tempo de EVENTO. O que sai fica na base, com o porque.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import fato_do_texto as FT      # noqa: E402  (o corpo, as ancoras de evento e o lugar/tempo por tipo)

NAO_SEI = "NAO_SEI"
FITO, CLIMA, PRODUCAO = "CAMPO_FITOSSANITARIO", "CAMPO_CLIMA", "CAMPO_PRODUCAO_COLHEITA"
MERCADO, VAREJO, EVENTO = "MERCADO_PRECO", "MERCADO_VAREJO", "EVENTO_TECNICO"
REGULATORIO, NEGOCIO, MARKETING = "REGULATORIO_MOLECULA", "NEGOCIO_AGRO", "MARKETING_CONCORRENCIA"
INSTITUCIONAL, NAO_FATO = "INSTITUCIONAL", "NAO_FATO"
TIPOS = (FITO, CLIMA, PRODUCAO, MERCADO, VAREJO, EVENTO, REGULATORIO, NEGOCIO, MARKETING, INSTITUCIONAL,
         NAO_FATO, NAO_SEI)
CAMPO_TIPOS = (FITO, CLIMA, PRODUCAO)
MINIMO_DE_CONCEITOS = 2

# Cada conceito e UMA expressao regular; conta uma vez por texto, por mais que se repita.
CONCEITOS = {
    FITO: (r"mosca\s+(?:dell['’]\s*olivo|delle\s+olive|della\s+frutta)", r"bactrocera", r"peronospora", r"oidio",
           r"botrite", r"cimice", r"afid[ei]", r"tignol[ae]", r"carpocapsa", r"infestazion[ei]", r"parassit[ai]",
           r"fitofag[oi]", r"patogen[oi]", r"trappol[ae]", r"cattur[ae]", r"soglia\s+di\s+intervento",
           r"difesa\s+(?:fitosanitaria|integrata|delle\s+colture)", r"trattament[oi]", r"insetticid[ai]",
           r"fungicid[ai]", r"erbicid[ai]", r"bollettino\s+fitosanitario", r"biocontroll[oi]",
           r"acar[oi]\s+predator[ei]", r"punture\s+fertili", r"avversit[aà]", r"fitopati[ae]", r"malatti[ae]\s+(?:delle\s+piante|fungin[ae])"),
    CLIMA: (r"precipitazion[ei]", r"piogg[ei]a?", r"piovos[oi]", r"temperatur[ae]", r"siccit[aà]", r"gelat[ae]",
            r"grandin[ea]t?[ae]?", r"ondat[ae]\s+di\s+calore", r"caldo\s+(?:record|estremo|anomalo)",
            r"anticiclon[ei]c?[oa]?", r"perturbazion[ei]", r"saccatur[ae]", r"promontori[oi]", r"depressione",
            r"previsioni\s+meteo", r"tempo\s+previsto", r"bilancio\s+idrico", r"evapotraspirazion[ei]",
            r"umidit[aà]", r"anomali[ae]\s+termic[hae]+", r"allerta\s+meteo", r"situazione\s+sinottica",
            r"eventi\s+(?:estremi|meteorologici|atmosferici)"),
    # «raccolta» sozinha e tambem recolha de dados/lixo; «produzione di» sozinha e tambem de biogas ou de
    # desigualdades; «resa/rese» sozinha e tambem o participio («resa possibile»): so contam com o produto
    # agricola ou a medida escritos a seguir
    PRODUCAO: (r"raccolto",
               r"raccolt[ae]\s+(?:delle|della|dell['’]|di)\s*(?:olive|uve?|mele|pere|frutta|nocciole|grano|pomodor[oi]|agrumi)",
               r"vendemmi[ae]", r"fioritur[ae]", r"fenologi[ac]?[ah]?e?", r"semin[ae]",
               r"res[ae]\s+(?:medi[ae]|per\s+ettaro|produttiv[ae]|di\s+\d|unitari[ae]|in\s+(?:granella|uva|olio))",
               r"produzion[ei]\s+(?:agricol[ae]|di\s+(?:olio|vino|uva|mele|pere|frutta|grano|latte|miele|nocciole|pomodor[oi]))",
               r"produttiv[oi]",
               r"annat[ae]", r"invaiatura", r"trebbiatura", r"ettari", r"quintali", r"stadio\s+fenologico",
               r"ingrossamento\s+(?:dei\s+)?frutti",
               r"maturazion[ei]\s+(?:dei\s+frutti|delle\s+(?:uve|olive|mele|pere)|dell['’]\s*uva|del\s+(?:grano|frutto))"),
    MERCADO: (r"prezz[oi]", r"quotazion[ei]", r"euro\s*/\s*kg", r"€\s*/\s*kg", r"listin[oi]",
              r"mercato\s+ortofrutticolo", r"esportazion[ei]", r"\bexport\b", r"importazion[ei]", r"consum[oi]",
              r"vendit[ae]", r"rilevazion[ei]", r"in\s+calo", r"in\s+aumento", r"rialzo", r"ribass[oi]",
              r"domanda\s+e\s+offerta", r"disponibilit[aà]\s+(?:ridotta|di\s+prodotto)"),
    REGULATORIO: (r"sostanz[ae]\s+attiv[ae]", r"prodott[oi]\s+fitosanitari[oi]", r"registrazion[ei]\s+(?:del|di)\s+prodott",
                  r"autorizzazion[ei]\s+(?:all['’]\s*immissione|eccezional[ei]|in\s+deroga)", r"\brevoc[ah]",
                  r"\bderog[ah]e?\b", r"\blmr\b", r"residu[oi]\s+massim[oi]", r"etichett[ae]\s+(?:del\s+prodotto|autorizzat)",
                  r"uso\s+di\s+emergenza", r"principi?o?\s+attiv[oi]", r"molecol[ae]"),
    # v2: as palavras de PROMOCAO (brand, gamma, lancio, packaging…) passaram para MARKETING (D72)
    NEGOCIO: (r"aziend[ae]", r"societ[aà]", r"\bstart\s?-?up\b", r"acquisizion[ei]", r"fusion[ei]",
              r"investiment[oi]", r"fatturato", r"stabiliment[oi]", r"\bbando\b", r"finanziament[oi]",
              r"contribut[oi]\s+(?:a\s+fondo|per)", r"imprenditori[ae]"),
    # D72: a voz da empresa a promover o que e seu
    MARKETING: (r"(?:il|i|la|le)\s+nostr[oiae]", r"presenter[aà]", r"present[ao]\s+(?:la|il|le|i)\s+nuov",
                r"lanci[oa]", r"lanciat[oa]", r"nuov[oae]\s+(?:variet[aà]|gamma|linea|prodott[oi]|formulazion[ei]|stile|referenz[ae])",
                r"\bbrand\b", r"marchi?[oi]", r"gamm[ae]", r"novit[aà]", r"stand", r"degustazion[ei]",
                r"stagione\s+commerciale", r"packaging", r"imballagg[io]", r"portafoglio\s+prodott[oi]",
                r"soluzion[ei]\s+(?:innovativ[ae]|per\s+(?:gli|i)\s+(?:agricoltori|produttori))"),
}
# D73: a prova de VAREJO tem de estar no corpo (o menu do site «Retail | GDO» nao conta)
VAREJO_PROVAS = (r"punt[oi]\s+vendita", r"insegn[ae]", r"e-?commerce", r"online", r"scaffal[ei]",
                 r"grande\s+distribuzione", r"\bgdo\b", r"supermercat[oi]", r"ipermercat[oi]", r"in\s+promozione",
                 r"volantin[oi]", r"retailer")
# D73: abertura ou operacao de loja, sem facto de produto = INSTITUCIONAL
LOJA = (r"nuov[oi]\s+punt[oi]\s+vendita", r"apertur[ae]", r"inaugur\w+", r"superficie\s+(?:di\s+vendita|commerciale)",
        r"amplia(?:mento)?", r"negozi[o]?", r"superstore")
# A palavra agro: sem ela, evento nao e evento tecnico, empresa nao e negocio agro, e o texto e NAO_FATO.
AGRO = (r"agricol[aoie]", r"agrari[aoe]", r"agroaliment\w*", r"agronom\w*", r"ortofrutt\w*", r"frutticol\w*",
        r"viticol\w*", r"vitivinicol\w*", r"\bvin[oi]\b", r"vignet[oi]", r"\boli[oi]\b", r"olivicol\w*", r"oliv[oie]",
        r"\bmel[ae]\b", r"melicoltura", r"meleto", r"coltur[ae]", r"coltivazion[ei]", r"agricoltor[ei]", r"zootecni\w*",
        r"sement[ei]", r"filiera", r"fitosanitar\w*", r"\buva\b", r"cereal[ei]", r"\bgrano\b", r"pomodor[oi]",
        r"serr[ae]\b", r"orticol\w*", r"floricol\w*", r"irrigazion[ei]", r"bonifica", r"agrumi", r"piccoli\s+frutti",
        r"mirtill[oi]", r"frutt[ao]", r"verdur[ae]", r"\bmiele\b", r"apicoltur\w*", r"agricoltura")

_BORDA_A, _BORDA_Z = r"(?<![0-9a-zà-ÿ])", r"(?![0-9a-zà-ÿ])"


def _compilar(lista):
    return [re.compile(_BORDA_A + "(?:%s)" % c + _BORDA_Z, re.I) for c in lista]


_RE = {k: _compilar(v) for k, v in CONCEITOS.items()}
_RE_AGRO = _compilar(AGRO)
_RE_VAREJO = _compilar(VAREJO_PROVAS)
_RE_PRECO = _compilar((r"prezz[oi]", r"quotazion[ei]", r"euro\s*/\s*kg", r"€\s*/\s*kg", r"listin[oi]"))
# a empresa como sujeito: «l'azienda», «sara presente a», «S.p.A.»…
_RE_EMPRESA = re.compile(_BORDA_A + r"(?:aziend[ae]|societ[aà]|gruppo|s\.?p\.?a\.?|s\.?r\.?l\.?|sar[aà]\s+presente|"
                         r"parteciper[aà]|presenter[aà]|consorzio)" + _BORDA_Z, re.I)
_RE_LOJA = _compilar(LOJA)
# evento: as ancoras da LUGAR-FATO (uma so lista), mais os cursos tecnicos
_RE_EVENTO_EXTRA = re.compile(_BORDA_A + r"(?:corso\s+di\s+(?!laurea|studi)|summer\s+school|edizione|in\s+programma\s+(?:a|dal|il))"
                              + _BORDA_Z, re.I)
# O evento conta se for anunciado na ABERTURA: as primeiras linhas DIFERENTES do corpo (o titulo repete-se
# muitas vezes na linha seguinte; contar a repeticao seria perder o primeiro paragrafo).
LINHAS_DE_ABERTURA = 3
LEAD_CARACTERES = 400
AGRO_PARA_NEGOCIO = 2            # regra 6: empresa so e negocio agro com >= 2 palavras agro diferentes
# As palavras de negocio (azienda, societa, investimenti…) aparecem em quase todo o texto institucional:
# o negocio precisa de mais conceitos do que os outros tipos.
MINIMO_NEGOCIO = 3
AGRO_PARA_INSTITUCIONAL = 2      # regra 8
LINHAS_PARA_SEM_FACTO = 3        # regra 8: um titulo solto nao chega para dizer INSTITUCIONAL ou NAO_FATO
# Aviso academico nao e evento tecnico, mesmo com «si svolgera» e o nome do departamento de Agraria.
_RE_ACADEMICO = re.compile(_BORDA_A + r"(?:esam[ei]|appell[oi]|lezion[ei]|laure[ae]|studenti|studentesse|tesi)" + _BORDA_Z, re.I)


def _nao_e_grito(linha: str) -> bool:
    """Linha quase toda em MAIUSCULAS e menu ou titulo de seccao (o menu nao conta, regra 1)."""
    letras = [ch for ch in linha if ch.isalpha()]
    return not letras or sum(ch.isupper() for ch in letras) / len(letras) < 0.6


def _achados(lista, texto):
    out = []
    for rx in lista:
        m = rx.search(texto)
        if m:
            out.append(m.group(0))
    return out


def _saida(k, basis, ev):
    return {"agro_fact_kind": k, "agro_fact_kind_basis": basis, "EVIDENCIA": ev}


def tipo_do_fato(texto: str) -> dict:
    c = "\n".join(l for l in FT.corpo(texto).splitlines() if _nao_e_grito(l))
    if not c:
        return _saida(NAO_SEI, "NAO_SEI · o texto não tem corpo (só menu, título curto ou rodapé)",
                      {"CONCEITOS": {}, "AGRO": [], "EVENTO_NA_ABERTURA": None, "VAREJO": [], "LOJA": [],
                       "LINHAS_DE_CORPO": 0})
    conceitos = {k: _achados(v, c) for k, v in _RE.items()}
    agro = _achados(_RE_AGRO, c)
    abertura = "\n".join(list(dict.fromkeys(l.strip() for l in c.splitlines()))[:LINHAS_DE_ABERTURA])
    # Varejo, loja e empresa-no-evento sao o ASSUNTO: contam so no LEAD (titulo + inicio do primeiro
    # paragrafo, LEAD_CARACTERES). No resto do corpo aparecem nas listas de «outras noticias» da pagina, e
    # muitos artigos sao um paragrafo so de milhares de caracteres (medido no gabarito, myfruit).
    lead = abertura[:LEAD_CARACTERES]
    varejo, loja = _achados(_RE_VAREJO, lead), _achados(_RE_LOJA, lead)
    empresa = _achados([_RE_EMPRESA], lead)
    # so PRECO propriamente dito: «vendita» esta em «superficie/punti di vendita», que e a propria loja
    preco_no_lead = _achados(_RE_PRECO, lead)
    m = FT._RE_EVENTO.search(abertura) or _RE_EVENTO_EXTRA.search(abertura)
    ev = {"LINHAS_DE_CORPO": len(c.splitlines()), "CONCEITOS": {k: v for k, v in conceitos.items() if v},
          "AGRO": agro[:8], "EVENTO_NA_ABERTURA": m.group(0) if m else None, "VAREJO": varejo, "LOJA": loja}
    if m and _RE_ACADEMICO.search(abertura):
        m = None
        ev["EVENTO_NA_ABERTURA"] = None
    if not agro:
        conceitos[MARKETING] = []        # D72 e comunicacao de empresa DO AGRO
    if m and agro:
        # a feira em si (o organizador tambem diz «la nostra») e EVENTO; e MARKETING so com uma EMPRESA
        # na abertura a mostrar o que e seu
        if empresa and len(conceitos[MARKETING]) >= MINIMO_DE_CONCEITOS:
            return _saida(MARKETING, "%s · empresa no evento «%s» a mostrar o que e seu: %s (D72)" % (
                MARKETING, m.group(0), ", ".join("«%s»" % x for x in conceitos[MARKETING][:6])), ev)
        return _saida(EVENTO, "%s · evento na abertura «%s» · ligação agro «%s» · «%s»"
                      % (EVENTO, m.group(0), agro[0], FT._trecho(abertura, 160)), ev)
    # D73: o assunto e abrir/ampliar uma loja, e o lead nao da facto de produto (preco…) = INSTITUCIONAL
    if len(loja) >= MINIMO_DE_CONCEITOS and not preco_no_lead:
        return _saida(INSTITUCIONAL, "%s · abertura/operação de loja no lead, sem facto de produto (D73): %s" % (
            INSTITUCIONAL, ", ".join("«%s»" % x for x in loja[:6])), ev)
    if len(agro) < AGRO_PARA_NEGOCIO or len(conceitos[NEGOCIO]) < MINIMO_NEGOCIO:
        conceitos[NEGOCIO] = []          # regra 6: empresa sem agro nao e negocio agro
    # D71: o assunto tecnico vence a voz da empresa quando pesa tanto ou mais
    tecnico = max(len(conceitos[k]) for k in CAMPO_TIPOS)
    if tecnico >= MINIMO_DE_CONCEITOS and tecnico >= len(conceitos[MARKETING]):
        conceitos[MARKETING] = []
    fortes = sorted(((len(v), k) for k, v in conceitos.items() if len(v) >= MINIMO_DE_CONCEITOS), reverse=True)
    if fortes and (len(fortes) == 1 or fortes[0][0] > fortes[1][0]):
        k = fortes[0][1]
        base = "%s · %d conceitos: %s%s" % (
            k, len(conceitos[k]), ", ".join("«%s»" % x for x in conceitos[k][:6]),
            " · segundo: %s (%d)" % (fortes[1][1], fortes[1][0]) if len(fortes) > 1 else "")
        if k == MERCADO and varejo:
            return _saida(VAREJO, "%s · varejo no lead: %s · %s" % (
                VAREJO, ", ".join("«%s»" % x for x in varejo[:4]), base), ev)
        return _saida(k, base, ev)
    if fortes:
        return _saida(NAO_SEI, "NAO_SEI · empate: %s" % ", ".join("%s (%d)" % (k, n) for n, k in fortes[:3]), ev)
    if not any(conceitos.values()) and ev["LINHAS_DE_CORPO"] >= LINHAS_PARA_SEM_FACTO:
        if not agro:
            return _saida(NAO_FATO, "%s · corpo com %d linhas, nenhum conceito de facto e nenhuma palavra agro"
                          % (NAO_FATO, ev["LINHAS_DE_CORPO"]), ev)
        if len(agro) >= AGRO_PARA_INSTITUCIONAL:
            return _saida(INSTITUCIONAL, "%s · mundo agro (%s) sem conceito de facto" % (
                INSTITUCIONAL, ", ".join("«%s»" % x for x in agro[:4])), ev)
    return _saida(NAO_SEI, "NAO_SEI · sinal fraco: %s" % (
        ", ".join("%s (%d)" % (k, len(v)) for k, v in conceitos.items() if v) or "só palavra agro"), ev)


def fato_com_tipo(texto: str, publication_time: str | None = None, publication_time_basis: str | None = None) -> dict:
    """Os campos do lugar/tempo do facto (LUGAR-FATO) com o tipo do facto, e a regra entre os dois."""
    r = dict(FT.campos_do_fato(texto, publication_time, publication_time_basis))
    t = tipo_do_fato(texto)
    r["agro_fact_kind"], r["agro_fact_kind_basis"] = t["agro_fact_kind"], t["agro_fact_kind_basis"]
    r["EVIDENCIA"] = dict(r["EVIDENCIA"], TIPO_DO_FATO=t["EVIDENCIA"])
    k = t["agro_fact_kind"]
    if k in CAMPO_TIPOS:
        aceita = (FT.CAMPO,)
    elif k == EVENTO:
        aceita = (FT.EVENTO,)
    else:
        return r
    if r["fact_location_kind"] not in aceita + (FT.NAO_SEI,):
        lug = [l for l in r["EVIDENCIA"]["LUGARES"] if l["KIND"] in aceita]
        antes = "%s (%s)" % (r["fact_location"], r["fact_location_kind"])
        if lug:
            r["fact_location"] = FT.SEP.join(l["LUGAR"] for l in lug)
            r["fact_location_kind"], r["fact_location_precision"] = lug[0]["KIND"], lug[0]["PRECISAO"]
        else:
            r["fact_location"] = r["fact_location_kind"] = r["fact_location_precision"] = FT.NAO_SEI
        r["fact_location_basis"] = ("%s · o facto é %s: o lugar %s não é lugar deste facto" % (
            r["fact_location_kind"], k, antes) + " · " + r["fact_location_basis"])[:1000]
    if r["fact_time_kind"] not in aceita + (FT.NAO_SEI,):
        antes = "%s (%s)" % (r["fact_time"], r["fact_time_kind"])
        ev = r["EVIDENCIA"]["TEMPOS_DE_EVENTO"] if aceita == (FT.EVENTO,) else []
        if ev:
            r["fact_time"], r["fact_time_kind"], r["fact_time_precision"] = ev[0]["VALOR"], FT.EVENTO, ev[0]["RESOLUCAO"]
        else:
            r["fact_time"] = r["fact_time_kind"] = FT.NAO_SEI
            r["fact_time_precision"] = "NOT_KNOWN"
        r["fact_time_basis"] = ("%s · o facto é %s: o tempo %s não é tempo deste facto" % (
            r["fact_time_kind"], k, antes) + " · " + r["fact_time_basis"])[:800]
    return r
