#!/usr/bin/env python3
"""O TIPO DO FACTO (FACT_KIND), TIRADO DO CORPO DO TEXTO — uma etiqueta, nunca um filtro.

    tipo_do_fato(texto) -> {"fact_kind", "fact_kind_basis", "EVIDENCIA"}
    fato_com_tipo(texto, publication_time=None, publication_time_basis=None) -> campos_do_fato + fact_kind

Funcao PURA (sem rede, sem banco, sem ficheiros). A taxonomia e a da D62, proposta e medida em
`scripts/regua_fato/` (protocolo, gabarito, prova cega):

    CAMPO_FITOSSANITARIO · CAMPO_CLIMA · CAMPO_PRODUCAO_COLHEITA · MERCADO_PRECO · EVENTO_TECNICO ·
    REGULATORIO_MOLECULA · NEGOCIO_AGRO · INSTITUCIONAL_NAO_FATO · NAO_SEI

Regras (mesmo metodo das reguas T1/T2):
  1. SO O CORPO. Menu, cabecalho e rodape nao contam: usa-se `fato_do_texto.corpo` (a mesma regra do
     lugar e do tempo do facto). Sem corpo = NAO_SEI (nao se sabe ler; nao e «nao e facto»).
  2. CONCEITOS POR PALAVRA INTEIRA. Cada tipo tem os seus conceitos; conta-se quantos conceitos
     DIFERENTES do tipo aparecem no corpo. Um tipo precisa de >= MINIMO_DE_CONCEITOS.
  3. O EVENTO E O FACTO (D62). Um evento tecnico anunciado no inicio do corpo, com ligacao agro escrita,
     e EVENTO_TECNICO mesmo que o corpo fale de variedades ou pragas. Evento sem ligacao agro nao e
     evento tecnico. «Eventi estremi» e tempo, nao evento (a ancora vem da LUGAR-FATO).
  4. NEGOCIO precisa de ligacao agro escrita (D62: loja/empresa so se for do ecossistema agro).
  5. EMPATE OU SINAL FRACO = NAO_SEI. O vencedor tem de ter mais conceitos do que o segundo.
  6. INSTITUCIONAL_NAO_FATO so quando ha corpo, nenhum tipo acende e nao ha palavra agro nenhuma.

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
MERCADO, EVENTO, REGULATORIO = "MERCADO_PRECO", "EVENTO_TECNICO", "REGULATORIO_MOLECULA"
NEGOCIO, NAO_FATO = "NEGOCIO_AGRO", "INSTITUCIONAL_NAO_FATO"
TIPOS = (FITO, CLIMA, PRODUCAO, MERCADO, EVENTO, REGULATORIO, NEGOCIO, NAO_FATO, NAO_SEI)
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
    # desigualdades: so contam com o produto agricola escrito a seguir
    PRODUCAO: (r"raccolto",
               r"raccolt[ae]\s+(?:delle|della|dell['’]|di)\s*(?:olive|uve?|mele|pere|frutta|nocciole|grano|pomodor[oi]|agrumi)",
               # «resa/rese» sozinha e tambem o participio («resa possibile»): so com a medida a seguir
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
    NEGOCIO: (r"aziend[ae]", r"societ[aà]", r"\bstart\s?-?up\b", r"lanci[oa]", r"acquisizion[ei]", r"fusion[ei]",
              r"\bbrand\b", r"marchi?[oi]", r"gamm[ae]", r"investiment[oi]", r"fatturato", r"stabiliment[oi]",
              r"\bbando\b", r"finanziament[oi]", r"contribut[oi]\s+(?:a\s+fondo|per)", r"imprenditori[ae]",
              r"stagione\s+commerciale", r"packaging", r"imballagg[io]"),
}
# A palavra agro: sem ela, evento nao e evento tecnico e empresa nao e negocio agro.
AGRO = (r"agricol[aoie]", r"agrari[aoe]", r"agroaliment\w*", r"agronom\w*", r"ortofrutt\w*", r"frutticol\w*",
        r"viticol\w*", r"vitivinicol\w*", r"\bvin[oi]\b", r"vignet[oi]", r"\boli[oi]\b", r"olivicol\w*", r"oliv[oie]",
        r"\bmel[ae]\b", r"melicoltura", r"meleto", r"coltur[ae]", r"coltivazion[ei]", r"agricoltor[ei]", r"zootecni\w*",
        r"sement[ei]", r"filiera", r"fitosanitar\w*", r"\buva\b", r"cereal[ei]", r"\bgrano\b", r"pomodor[oi]",
        r"serr[ae]\b", r"orticol\w*", r"floricol\w*", r"irrigazion[ei]", r"bonifica", r"agrumi", r"piccoli\s+frutti",
        r"mirtill[oi]", r"frutt[ao]", r"verdur[ae]", r"\bmiele\b", r"apicoltur\w*", r"agricoltura")

_BORDA_A, _BORDA_Z = r"(?<![0-9a-zà-ÿ])", r"(?![0-9a-zà-ÿ])"
_RE = {k: [re.compile(_BORDA_A + "(?:%s)" % c + _BORDA_Z, re.I) for c in v] for k, v in CONCEITOS.items()}
_RE_AGRO = [re.compile(_BORDA_A + "(?:%s)" % c + _BORDA_Z, re.I) for c in AGRO]
# evento: as ancoras da LUGAR-FATO (uma so lista), mais os cursos tecnicos
_RE_EVENTO_EXTRA = re.compile(_BORDA_A + r"(?:corso\s+di\s+(?!laurea|studi)|summer\s+school|edizione|in\s+programma\s+(?:a|dal|il))"
                              + _BORDA_Z, re.I)
# O evento conta se for anunciado na ABERTURA: as primeiras linhas DIFERENTES do corpo (o titulo repete-se
# muitas vezes na linha seguinte; contar a repeticao seria perder o primeiro paragrafo).
LINHAS_DE_ABERTURA = 3
AGRO_PARA_NEGOCIO = 2            # regra 4: empresa so e negocio agro com >= 2 palavras agro diferentes
# As palavras de negocio (azienda, societa, investimenti…) aparecem em quase todo o texto institucional:
# o negocio precisa de mais conceitos do que os outros tipos.
MINIMO_NEGOCIO = 3
# Aviso academico nao e evento tecnico, mesmo com «si svolgera» e o nome do departamento de Agraria.
_RE_ACADEMICO = re.compile(_BORDA_A + r"(?:esam[ei]|appell[oi]|lezion[ei]|laure[ae]|studenti|studentesse|tesi)" + _BORDA_Z, re.I)


def _nao_e_grito(linha: str) -> bool:
    """Linha quase toda em MAIUSCULAS e menu ou titulo de seccao (o menu nao conta, regra 1)."""
    letras = [ch for ch in linha if ch.isalpha()]
    return not letras or sum(ch.isupper() for ch in letras) / len(letras) < 0.6
LINHAS_PARA_NAO_FATO = 3         # regra 6: um titulo solto nao chega para dizer «nao e facto»


def _achados(lista, texto):
    out = []
    for rx in lista:
        m = rx.search(texto)
        if m:
            out.append(m.group(0))
    return out


def tipo_do_fato(texto: str) -> dict:
    c = "\n".join(l for l in FT.corpo(texto).splitlines() if _nao_e_grito(l))
    if not c:
        return {"fact_kind": NAO_SEI, "fact_kind_basis": "NAO_SEI · o texto não tem corpo (só menu, título curto ou rodapé)",
                "EVIDENCIA": {"CONCEITOS": {}, "AGRO": [], "EVENTO_NA_ABERTURA": None, "LINHAS_DE_CORPO": 0}}
    conceitos = {k: _achados(v, c) for k, v in _RE.items()}
    agro = _achados(_RE_AGRO, c)
    abertura = "\n".join(list(dict.fromkeys(l.strip() for l in c.splitlines()))[:LINHAS_DE_ABERTURA])
    m = FT._RE_EVENTO.search(abertura) or _RE_EVENTO_EXTRA.search(abertura)
    ev = {"LINHAS_DE_CORPO": len(c.splitlines()), "CONCEITOS": {k: v for k, v in conceitos.items() if v},
          "AGRO": agro[:8], "EVENTO_NA_ABERTURA": m.group(0) if m else None}
    if m and _RE_ACADEMICO.search(abertura):
        m = None
        ev["EVENTO_NA_ABERTURA"] = None
    if m and agro:
        return {"fact_kind": EVENTO, "EVIDENCIA": ev,
                "fact_kind_basis": "%s · evento na abertura «%s» · ligação agro «%s» · «%s»"
                                   % (EVENTO, m.group(0), agro[0], FT._trecho(abertura, 160))}
    if len(agro) < AGRO_PARA_NEGOCIO or len(conceitos[NEGOCIO]) < MINIMO_NEGOCIO:
        conceitos[NEGOCIO] = []          # regra 4: empresa sem agro nao e negocio agro
    fortes = sorted(((len(v), k) for k, v in conceitos.items() if len(v) >= MINIMO_DE_CONCEITOS), reverse=True)
    if fortes and (len(fortes) == 1 or fortes[0][0] > fortes[1][0]):
        k = fortes[0][1]
        return {"fact_kind": k, "EVIDENCIA": ev,
                "fact_kind_basis": "%s · %d conceitos: %s%s" % (
                    k, len(conceitos[k]), ", ".join("«%s»" % x for x in conceitos[k][:6]),
                    " · segundo: %s (%d)" % (fortes[1][1], fortes[1][0]) if len(fortes) > 1 else "")}
    if fortes:
        return {"fact_kind": NAO_SEI, "EVIDENCIA": ev,
                "fact_kind_basis": "NAO_SEI · empate: %s" % ", ".join("%s (%d)" % (k, n) for n, k in fortes[:3])}
    if not agro and not any(conceitos.values()) and ev["LINHAS_DE_CORPO"] >= LINHAS_PARA_NAO_FATO:
        return {"fact_kind": NAO_FATO, "EVIDENCIA": ev,
                "fact_kind_basis": "%s · corpo com %d linhas, nenhum conceito de facto e nenhuma palavra agro"
                                   % (NAO_FATO, ev["LINHAS_DE_CORPO"])}
    return {"fact_kind": NAO_SEI, "EVIDENCIA": ev,
            "fact_kind_basis": "NAO_SEI · sinal fraco: %s" % (
                ", ".join("%s (%d)" % (k, len(v)) for k, v in conceitos.items() if v) or "só palavra agro")}


def fato_com_tipo(texto: str, publication_time: str | None = None, publication_time_basis: str | None = None) -> dict:
    """Os campos do lugar/tempo do facto (LUGAR-FATO) com o tipo do facto, e a regra entre os dois."""
    r = dict(FT.campos_do_fato(texto, publication_time, publication_time_basis))
    t = tipo_do_fato(texto)
    r["fact_kind"], r["fact_kind_basis"] = t["fact_kind"], t["fact_kind_basis"]
    r["EVIDENCIA"] = dict(r["EVIDENCIA"], TIPO_DO_FATO=t["EVIDENCIA"])
    k = t["fact_kind"]
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
