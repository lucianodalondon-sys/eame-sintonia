#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
VOCI DAL CAMPO — o extrator de VOZ (ferramenta n.3 do casco · CAP-FIELD da Bíblia da Intelligence §34).

    import voce_dal_campo as vc
    doc = vc.documento(texto, source_id=..., external_id=..., published_at=..., channel=..., title=...)
    r = vc.extrair(doc)          # {'DOCUMENTO', 'FALANTES', 'VOZES', 'RECUSAS'}
    vc.validar_voce(v, doc)      # [] ou a lista de violacoes do contrato

    py motor/voce_dal_campo.py --medir      # corre sobre os transcritos do repo e imprime a contagem

Funcao PURA sobre um texto JA TRANSCRITO: sem rede, sem banco, sem login, sem perfil. Nao transcreve
(isso e de `ferramentas/fala_local.py`), nao coleta (INT-LAW: a Intelligence nao chama coletor), nao
cunha SOURCE_ID nem DOCUMENT_ID (§28): usa os que o chamador traz, e se nao trouxer fica NAO SEI.

O QUE UMA VOCE E (D84, resumo da missao)
------------------------------------------
    SPEAKER_ID + papel + citacao/transcricao + cultura + problema + lugar + data

e a Biblia (CAP-FIELD) acrescenta o que NAO se pode perder:

    speaker/entity · role · prova de expertise · fact location · fact time · crop · issue ·
    observacao · proveniencia · independencia

AS SEPARACOES, UMA POR UMA, E ONDE CADA UMA MORA NESTE FICHEIRO
-----------------------------------------------------------------
  PESSOA != INSTITUICAO    o canal que publica e o PUBLISHER, nunca o falante. Sem pessoa apresentada
                           no transcrito, a voz e da INSTITUICAO (se o texto fala em «nos» dela) ou
                           de ninguem identificado — e ai SPEAKER_ID fica NAO SEI.
  IDENTIDADE != EXPERTISE  (INT-LAW-065) o papel so vem de uma DECLARACAO no transcrito (a propria
                           pessoa ou quem a apresenta), com o trecho e a posicao. Papel declarado nao
                           e expertise no tema: EXPERTISE_TEMATICA so fica PROVADA_NA_DECLARACAO quando
                           a propria declaracao nomeia a cultura ou o problema da citacao.
  AGRONOMO != INFLUENCIADOR  «inscreve-te no canal» e sinal de CRIADOR, nao de papel. Sem papel
                           profissional declarado e com sinal de criador, o papel e INFLUENCIADOR;
                           com os dois, fica o profissional e o sinal fica a vista (CREATOR_SIGNALS).
  AGRICULTOR = T8          o unico papel que faz a voz entrar no universo T8.
  CITACAO != INTERPRETACAO QUOTE_ORIGINAL e um pedaco EXACTO do transcrito (texto[ini:fim]); a
                           leitura nossa vai em INTERPRETACAO, assinada, e nunca dentro da citacao.
  LUGAR DA PESSOA != LUGAR DO FACTO  (INT-LAW-101, MUST_NOT_DO do CAP-FIELD: «inferir localizacao do
                           facto a partir do perfil») o lugar dito na apresentacao vai para
                           SPEAKER_PLACE (especie BASE), e NUNCA para FACT_LOCATION.
  PUBLICACAO != FACTO      PUBLISHED_AT nunca preenche FACT_TIME. «hoje», «este ano», «ieri»
                           ficam NAO SEI: a data em que a pessoa FALOU nao esta provada (um webinar
                           vai para o ar semanas depois), e sem ela nao ha conta a fazer.
  ORIGINAL != TRADUCAO     a legenda da plataforma pode ser traducao automatica. Titulo numa lingua
                           e transcrito noutra = PROVAVEL_TRADUCAO: a frase NAO e a fala da pessoa.
  VOZ != INCIDENCIA        (CAP-FIELD) sem metodo e sem denominador, uma voz nunca mede pressao.

QUEM LE O QUE — um conceito, um dono (INT-LAW-000)
----------------------------------------------------
  cultura e problema   `motor/matriz_recorte.py` (CROPS, ISSUES e a regra de casamento `_padrao`).
                       Nao ha segundo vocabulario aqui. O que la nao esta sai NAO SEI, e isso e
                       lacuna de vocabulario, nao ausencia de problema.
  lugar/tempo em IT    `leis/fato_local.py` (o leitor italiano: gazetteer, ancoras, meses).
  lugar/tempo EN/ES    NAO HAVIA leitor. O deste ficheiro e minimo e declarado: so o que esta NA
                       MESMA FRASE da citacao, so data absoluta, so lugar governado por um marcador
                       de relato em primeira pessoa. Tudo o resto e NAO SEI.

O LIMITE QUE NAO SE ESCONDE
-----------------------------
Nao ha diarizacao. Quem fala numa frase e PRESUMIDO: o ultimo falante que se APRESENTOU a si proprio
antes dela, se nao houver marca de troca de voz («>>») pelo meio e se a distancia for curta
(JANELA_DE_ATRIBUICAO — escolhida, NAO medida). Quem foi apresentado por OUTRO nao passa a ser quem
fala: a apresentacao e de quem apresenta. ATTRIBUTION_STATE nunca e PROVADA aqui.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys
import unicodedata

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _p in (RAIZ, os.path.join(RAIZ, 'motor'), os.path.join(RAIZ, 'leis')):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import matriz_recorte as MR  # noqa: E402  dono do vocabulario de cultura e problema
import fato_local as FL      # noqa: E402  dono do leitor italiano de lugar e tempo

NAO_SEI = 'NAO SEI'
REGRA = 'voce-v1'
AUTOR_DA_INTERPRETACAO = 'SINTONIA · regra lexical %s (nao e fala de ninguem)' % REGRA

# Distancia maxima, em caracteres, entre a apresentacao de alguem e uma frase que lhe e atribuida.
# ~6000 caracteres sao uns 5 minutos de fala. ESCOLHIDA, NAO MEDIDA: sem diarizacao nao ha gabarito.
JANELA_DE_ATRIBUICAO = 6000
# Quanto texto depois do nome se le para achar o papel e a organizacao (caracteres). Escolhido, nao medido.
ALCANCE_AUTO, ALCANCE_TERCEIRO = 160, 80
# Uma citacao e UMA frase. Cortada aqui para o card nao virar o transcrito inteiro.
MAX_CITACAO = 400

# ── os vocabularios fechados do item ────────────────────────────────────────────────────
PESSOA, INSTITUICAO = 'PESSOA', 'INSTITUICAO'
AGRONOMO, TECNICO, INVESTIGADOR, AGRICULTOR, INFLUENCIADOR = (
    'AGRONOMO', 'TECNICO', 'INVESTIGADOR', 'AGRICULTOR', 'INFLUENCIADOR')
PAPEIS = (AGRONOMO, TECNICO, INVESTIGADOR, AGRICULTOR, INFLUENCIADOR, NAO_SEI)
AUTO, TERCEIRO = 'AUTO_DECLARADO', 'DECLARADO_POR_TERCEIRO'
RELATO, AFIRMACAO, RECOMENDACAO = 'RELATO_EM_PRIMEIRA_PESSOA', 'AFIRMACAO_GERAL', 'RECOMENDACAO'
ORIG_AUDIO = 'TRANSCRICAO_DO_AUDIO'
ORIG_DATASET = 'DECLARADA_ORIGINAL_PELO_DATASET'
ORIG_TRADUCAO = 'PROVAVEL_TRADUCAO'

# ── lingua: contagem de palavras funcionais (declarada como tal, nao e um detector) ───────
# Palavras que SO uma das quatro linguas usa (as partilhadas — «de», «la», «en», «in» — ficam de fora).
_FUNCIONAIS = {
    'it': ('il', 'della', 'che', 'sono', 'per', 'non', 'questo', 'anche', 'nel', 'gli', 'delle', 'abbiamo',
           'alla', 'dei', 'di', 'e', 'nella', 'degli', 'lo', 'alle'),
    'es': ('el', 'los', 'que', 'por', 'para', 'una', 'pero', 'como', 'las', 'muy', 'hemos', 'y', 'unos', 'estas'),
    'en': ('the', 'and', 'that', 'with', 'this', 'you', 'have', 'are', 'what', 'from', 'which', 'we', 'how',
           'your', 'of', 'for', 'to', 'why', 'is'),
    'fr': ('le', 'les', 'des', 'est', 'une', 'pour', 'dans', 'avec', 'nous', 'sur', 'pas', 'qui', 'et', 'du',
           'votre', 'au', 'aux', 'quel', 'quelle'),
}


def lingua(texto: str, minimo: int = 3) -> str:
    """'it' | 'es' | 'en' | 'fr' | NAO SEI — a lingua com mais palavras funcionais proprias; empate = NAO SEI."""
    pal = re.findall(r"[a-zà-ÿ']+", (texto or '').lower())
    if not pal:
        return NAO_SEI
    conta = {l: sum(1 for p in pal if p in ws) for l, ws in _FUNCIONAIS.items()}
    ordem = sorted(conta.values(), reverse=True)
    melhor = max(conta, key=lambda l: conta[l])
    if conta[melhor] < minimo or ordem[0] == ordem[1]:
        return NAO_SEI
    return melhor


def _norm(s: str) -> str:
    return MR._norm(s)


def _sha(*partes) -> str:
    return hashlib.sha1('\x1f'.join(str(p) for p in partes).encode('utf-8')).hexdigest()[:12]


# ── frases com posicao (a posicao e o que torna a citacao auditavel) ──────────────────────
_RE_FIM = re.compile(r'[.!?]+(?=\s|$)|\n{2,}')


def frases(texto: str) -> list:
    """[(ini, fim)] das frases do texto, com a posicao NO TEXTO ORIGINAL."""
    fora, ini = [], 0
    for m in _RE_FIM.finditer(texto):
        fim = m.end()
        if texto[ini:fim].strip():
            fora.append(_apara(texto, ini, fim))
        ini = fim
    if texto[ini:].strip():
        fora.append(_apara(texto, ini, len(texto)))
    return fora


def _apara(texto, ini, fim):
    while ini < fim and texto[ini].isspace():
        ini += 1
    while fim > ini and texto[fim - 1].isspace():
        fim -= 1
    return ini, fim


# ── papel: o lexico, e a ordem em que se le ─────────────────────────────────────────────
# Cada entrada e (papel, regex sobre o texto NORMALIZADO sem acento e em minusculas).
# A ordem manda: «ingeniero agronomo» antes de «ingeniero»; «technical agronomist» e AGRONOMO.
LEXICO_DE_PAPEL = (
    (AGRONOMO, r'agronomist|agronom[oa]|agronome|dottore agronomo|ingenier[oa] agronom[oa]|perito agrario'),
    (INVESTIGADOR, r'researcher|scientist|pathologist|entomologist|professor|lecturer|ricercat(?:ore|rice)|'
                   r'fitopatolog[oa]|entomolog[oa]|professore(?:ssa)?|docente|investigador(?:a)?|'
                   r'profesor(?:a)?|catedratic[oa]|chercheur|chercheuse|phd student|doctoral'),
    (TECNICO, r'advis[oe]r|consultant|technician|extension|field technical|technical (?:manager|lead|'
              r'solutions|product lead|advisor)|tecnic[oa]|consulente|asesor(?:a)?|conseill(?:er|ere)|'
              r'responsable tecnic[oa]|director tecnic[oa]|direttore tecnico'),
    (AGRICULTOR, r'farmer|grower|producer|agricultor(?:a)?|agricolt(?:ore|rice)|viticolt(?:ore|rice)|'
                 r'olivicolt(?:ore|rice)|frutticolt(?:ore|rice)|coltivatore|imprenditore agricolo|'
                 r'viticultor(?:a)?|olivarer[oa]|agriculteur|agricultrice|viticulteur|vigneron'),
)
_RE_PAPEL = tuple((p, re.compile(r'(?<![a-z])(?:%s)(?![a-z])' % rx)) for p, rx in LEXICO_DE_PAPEL)

# Sinais de CRIADOR de conteudo. Nao sao papel; sao o que separa influenciador de profissional.
CRIADOR = re.compile(
    r"(?<![a-z])(?:subscribe|like (?:this|the) video|share this video|my channel|this channel|"
    r"welcome back to (?:my|the) channel|iscriviti|iscrivetevi|mio canale|suscr[ií]bete|"
    r"suscribiros|mi canal|abonnez|ma cha[iî]ne|follow me|seguitemi|s[ií]gueme)(?![a-z])", re.I)

# Organizacao: nome em Maiusculas depois de «at/with/from/presso/de/del/…», ate 8 palavras.
_CAP = r"[A-ZÀ-Ý][\w'’&.\-]*"
_LIGA = r"(?:of|and|for|the|de|di|del|della|dei|degli|y|e|la|le|du|des)"
RE_ORG = re.compile(r"(?<![\w])(?:at|with|from|for|presso|dell['’]|del|della|de la|del|de|du|de l['’])\s+"
                    r"(?:the\s+|la\s+|il\s+|l['’])?(%s(?:\s+(?:%s\s+)?%s){0,7})" % (_CAP, _LIGA, _CAP))
# Tipo da organizacao: so por palavra do nome. Empresa conhecida da casa entra por nome proprio.
TIPO_DE_ORG = (
    ('UNIVERSIDADE_PESQUISA', r'universit|universidad|university|college|institut|istituto|instituto|research|'
                              r'crea|cnr|csic|ifapa|inrae|irta|ricerca|investigacion'),
    ('INSTITUICAO_PUBLICA', r'department|ministry|ministero|ministerio|regione|region|junta|consejeria|'
                            r'chamber|camera|chambre|servizio|servicio|agency|agenzia|ente'),
    ('ASSOCIACAO', r'coldiretti|confagricoltura|cia|asaja|coag|upa|cooperativ|consorzio|consejo regulador|'
                   r'association|associazione|asociacion|federation|federazione'),
    ('EMPRESA', r'adama|bayer|syngenta|basf|corteva|fmc|upl|nufarm|sipcam|certis|biogard|belchim|'
                r'winfield|koppert|isagro|gowan|sumitomo|nutrien|s\.?p\.?a|s\.?l\.?|s\.?r\.?l|ltd|inc|gmbh'),
    ('MEDIA', r'agriculture\.com|real ?agriculture|tv|radio|magazine|rivista|revista|news|notizie'),
)

# ── apresentacoes: quem se diz quem ─────────────────────────────────────────────────────
_RUIDO = r"(?:\[[^\]]{0,20}\]\s*|>>\s*)*"
_NOME_CAP = r"(%s(?:[\s\-]+%s){0,3})" % (_CAP, _CAP)
# nome em minusculas (legenda automatica): so depois de marcador FORTE, 1 a 3 palavras.
_NOME_MIN = r"([a-zà-ÿ]{2,}(?:\s+[a-zà-ÿ]{2,}){0,2})"
_PARA_NOME = {'and', 'e', 'y', 'et', 'i', 'im', 'soy', 'sono', 'from', 'de', 'di', 'da', 'del', 'with', 'con',
              'the', 'el', 'la', 'il', 'lo', 'le', 'a', 'an', 'un', 'una', 'uno', 'que', 'che', 'who', 'sobre',
              'y', 'e', 'go', 'going', 'here', 'so', 'just', 'always', 'not', 'sure', 'happy', 'on', 'in', 'at',
              'your', 'our', 'this', 'that', 'thinking', 'talking', 'about', 'coming', 'into', 'also', 'very',
              'ingeniero', 'doctor', 'doctora', 'tecnico', 'agronomo', 'investigador', 'profesor', 'desde',
              'presso', 'per', 'para', 'por', 'es', 'est', 'ho', 'he', 'mi', 'me', 'my', "i'm", 'i’m'}
_PALAVRAS_NAO_NOME = {'Today', 'Here', 'So', 'Well', 'Yes', 'No', 'Now', 'Hello', 'Hi', 'Good', 'Welcome', 'This',
                      'We', 'I', 'It', 'Buongiorno', 'Buonasera', 'Buenos', 'Buenas', 'Hola', 'Ciao', 'Thank',
                      'Thanks', 'Grazie', 'Gracias', 'Bonjour', 'Okay', 'OK', 'Oh', 'Uh', 'Um', 'Currently',
                      'Going', 'Just', 'Always', 'Sure', 'Happy', 'Not', 'Very', 'Desperate', 'Coming', 'Talking',
                      'Thinking', 'Presenting', 'Referring', 'About', 'On', 'In', 'At', 'The', 'Also'}

APRESENTACOES = (
    # (id, especie, regex, grupo do nome, nome em minusculas permitido)
    ('EN_MY_NAME_IS', AUTO, re.compile(r"(?i:my name is)\s+" + _RUIDO + _NOME_CAP), True),
    ('EN_IM', AUTO, re.compile(r"(?<![\w])(?:I'm|I am|I’m)\s+" + _RUIDO + _NOME_CAP + r"(?=\s*[,.]|\s+and\b|\s+from\b"
                                r"|\s+with\b|\s*$)"), False),
    ('EN_NOME_VIRGULA_IAM', AUTO, re.compile(r"(?:^|[.!?]\s+|\bSo\s+|\bhello everyone\.\s*So\s+)" + _NOME_CAP +
                                             r",\s+I am\s+(?:an?|the)\s+"), False),
    ('XX_NOME_VIRGULA_PAPEL', AUTO, re.compile(r"(?:^|[.!?]\s+)" + _RUIDO + _NOME_CAP +
                                               r",\s+(?:an?|un|una|uno|un'|il|la|el)?\s*(?=[a-zà-ÿ])"), False),
    ('IT_MI_CHIAMO', AUTO, re.compile(r"(?i:mi chiamo)\s+" + _RUIDO + _NOME_CAP), True),
    ('IT_SONO', AUTO, re.compile(r"(?<![\w])(?:[Ss]ono)\s+(?:il\s+|la\s+)?(?:dott(?:or)?\.?\s*|dottoressa\s+)?" +
                                 _NOME_CAP + r"(?=\s*,)"), False),
    ('ES_ME_LLAMO', AUTO, re.compile(r"(?i:me llamo|mi nombre es)\s+" + _RUIDO + _NOME_CAP), True),
    ('ES_SOY', AUTO, re.compile(r"(?<![\w])(?:[Ss]oy)\s+" + _NOME_CAP + r"(?=\s*,)"), False),
    # apresentados por OUTRO: a apresentacao e de quem apresenta, e por isso nao muda quem fala
    ('EN_HERE_WITH', TERCEIRO, re.compile(r"(?i:here with|joining me(?: I have)?(?: my colleague)?|I have)\s+" +
                                          _NOME_CAP + r"(?=,?\s+(?:who's|who is|joining me|also from|of|from)\b)"),
     False),
    ('XX_TITULO_NOME', TERCEIRO, re.compile(r"(?i:el doctor|la doctora|il dottor|la dottoressa|il professor|"
                                            r"la professoressa|el profesor|la profesora|dr\.?|doctor|professor)"
                                            r"(?:\s+(?i:ingeniero agr[oó]nomo|agronomo|ingeniero))?\s+" + _NOME_CAP),
     False),
    ('ES_TITULO_NOME_MIN', TERCEIRO, re.compile(r"(?:el|la) (?:doctor|doctora) (?:ingenier[oa] agr[oó]nom[oa] )?" +
                                                _NOME_MIN), True),
)


def _limpa_nome(nome: str, minusculas: bool) -> str:
    toks = re.split(r'\s+', nome.strip())
    fora = []
    for t in toks:
        t = re.sub(r"['’]s$", '', t.strip(",.;:'’"))
        if not t:
            break
        if minusculas and _norm(t) in _PARA_NOME:
            break
        if not minusculas and (t in _PALAVRAS_NAO_NOME or _norm(t) in _PARA_NOME):
            break
        fora.append(t)
    return ' '.join(fora)


def _frase_de(pos: int, fs: list):
    for i, (a, b) in enumerate(fs):
        if a <= pos < b:
            return i, a, b
    return None, pos, pos


def _papeis_em(trecho: str) -> list:
    n = _norm(trecho)
    fora = []
    for papel, rx in _RE_PAPEL:
        m = rx.search(n)
        if m:
            fora.append((m.start(), papel, m.group(0)))
    ordem = [p for p, _ in LEXICO_DE_PAPEL]
    return sorted({p for _, p, _ in fora}, key=ordem.index)


def _organizacao(trecho: str):
    m = RE_ORG.search(trecho)
    if not m:
        return NAO_SEI, NAO_SEI
    org = m.group(1).strip(" .,'’")
    n = _norm(org)
    for tipo, rx in TIPO_DE_ORG:
        if re.search(r'(?<![a-z])(?:%s)' % rx, n):
            return org, tipo
    return org, NAO_SEI


# Lugar dito na apresentacao: «a farmer in the Aras area of Haut-France», «based in Foggia».
RE_LUGAR_DA_PESSOA = re.compile(r"(?<![\w])(?:in|based in|from|near|a|en|de|di)\s+(?:the\s+)?(%s(?:\s+(?:%s\s+)?%s)"
                                r"{0,5})" % (_CAP, _LIGA, _CAP))
_RE_AREA = re.compile(r"(?<![\w])(?:in|en|nel|nella)\s+(?:the\s+|la\s+|il\s+)?([\w\-]+ (?:area|zona|zone|region|"
                      r"regione|comarca) (?:of|de|di|del)\s+[^\s,.]+(?:[\- ][A-ZÀ-Ý][\w\-]*)*)")


def _lugar_da_pessoa(trecho: str, org: str) -> str:
    m = _RE_AREA.search(trecho)
    if m:
        return m.group(1).replace('​', '').strip()
    for m in RE_LUGAR_DA_PESSOA.finditer(trecho):
        cand = m.group(1).strip(" .,'’")
        if org != NAO_SEI and (cand in org or org in cand):
            continue
        if cand.split()[0] in _PALAVRAS_NAO_NOME:
            continue
        return cand
    return NAO_SEI


def _speaker_id(nome: str) -> str:
    """SPK-<sha do nome normalizado>. Mesmo nome escrito => mesmo id; homonimos NAO se resolvem aqui."""
    return 'SPK-' + _sha('nome', re.sub(r'\s+', ' ', _norm(nome)).strip())


def apresentacoes(texto: str, fs: list | None = None) -> list:
    """Todas as apresentacoes do transcrito, com o trecho, a posicao e o que se leu dela."""
    fs = fs if fs is not None else frases(texto)
    achados, ocupado = [], []
    for rid, especie, rx, minusculas in APRESENTACOES:
        for m in rx.finditer(texto):
            ini_nome = m.start(1)
            nome = _limpa_nome(m.group(1), minusculas)
            if not nome or len(nome) < 3:
                continue
            if any(a <= ini_nome < b for a, b in ocupado):
                continue
            # «Nome, …» so e apresentacao quando o que vem logo a seguir e uma PROFISSAO (4 palavras no maximo):
            # sem isto, «However, …», «Bueno, …» e «Entonces, …» viravam gente.
            if rid == 'XX_NOME_VIRGULA_PAPEL' and not _papeis_em(' '.join(texto[m.end():m.end() + 60].split()[:4])):
                continue
            ocupado.append((ini_nome, ini_nome + len(nome)))
            i, fa, fb = _frase_de(m.start(), fs)
            # o trecho da apresentacao e a frase onde ela esta (e a seguinte, se a frase for so o nome)
            fb2 = fs[i + 1][1] if (i is not None and i + 1 < len(fs) and fb - fa < 40) else fb
            # o papel le-se no que vem DEPOIS do nome, e perto: quem apresenta outro costuma apresentar varios
            # na mesma frase, e o papel do seguinte nao pode colar no anterior
            alcance = ALCANCE_AUTO if especie == AUTO else ALCANCE_TERCEIRO
            depois = texto[m.start(1) + len(nome):min(fb2, m.start(1) + len(nome) + alcance)]
            trecho_papel = texto[m.start():m.start(1) + len(nome) + len(depois)]
            papeis = _papeis_em(depois)
            org, org_tipo = _organizacao(depois)
            achados.append({
                'REGRA': rid, 'ESPECIE': especie, 'NOME': nome,
                'NOME_EM_MINUSCULAS': nome == nome.lower(),
                'POS_NOME': ini_nome, 'POS': m.start(), 'FRASE': (fa, fb2),
                'TRECHO': texto[fa:fb2][:MAX_CITACAO],
                'PAPEIS': papeis, 'ORGANIZACAO': org, 'ORGANIZACAO_TIPO': org_tipo,
                'SPEAKER_PLACE': _lugar_da_pessoa(depois, org) if especie == AUTO else NAO_SEI,
                'TRECHO_DO_PAPEL': trecho_papel[:MAX_CITACAO],
            })
    achados.sort(key=lambda a: a['POS'])
    return achados


def falantes(texto: str, aps: list, publisher: str) -> dict:
    """{SPEAKER_ID: falante}. Um falante junta as apresentacoes do MESMO nome no documento."""
    out = {}
    for a in aps:
        sid = _speaker_id(a['NOME'])
        f = out.setdefault(sid, {
            'SPEAKER_ID': sid, 'SPEAKER_NAME': a['NOME'], 'SPEAKER_KIND': PESSOA,
            'SPEAKER_ID_SCOPE': 'NOME_DECLARADO_NO_TRANSCRITO — mesmo nome, mesmo id; homonimos NAO resolvidos '
                                '(INT-LAW-083: entity resolution nao fabrica identidade)',
            'NAME_EVIDENCE': [], 'ROLE': NAO_SEI, 'ROLES_DECLARED': [], 'ROLE_EVIDENCE': [],
            'ROLE_STATE': NAO_SEI, 'ORGANIZATION': NAO_SEI, 'ORGANIZATION_KIND': NAO_SEI,
            'SPEAKER_PLACE': NAO_SEI, 'SPEAKER_PLACE_KIND': 'BASE',
            'PUBLISHER': publisher or NAO_SEI})
        f['NAME_EVIDENCE'].append({'TRECHO': a['TRECHO'], 'POS': a['POS_NOME'], 'REGRA': a['REGRA'],
                                   'ESPECIE': a['ESPECIE'],
                                   'NOME_EM_MINUSCULAS': a['NOME_EM_MINUSCULAS']})
        for p in a['PAPEIS']:
            if p not in f['ROLES_DECLARED']:
                f['ROLES_DECLARED'].append(p)
                f['ROLE_EVIDENCE'].append({'ROLE': p, 'TRECHO': a['TRECHO_DO_PAPEL'], 'POS': a['POS'],
                                           'ESPECIE': a['ESPECIE']})
        if f['ORGANIZATION'] == NAO_SEI and a['ORGANIZACAO'] != NAO_SEI:
            f['ORGANIZATION'], f['ORGANIZATION_KIND'] = a['ORGANIZACAO'], a['ORGANIZACAO_TIPO']
        if f['SPEAKER_PLACE'] == NAO_SEI and a['SPEAKER_PLACE'] != NAO_SEI:
            f['SPEAKER_PLACE'] = a['SPEAKER_PLACE']
    criador = [m.group(0) for m in CRIADOR.finditer(texto)]
    for f in out.values():
        f['CREATOR_SIGNALS'] = criador[:5]
        if f['ROLES_DECLARED']:
            f['ROLE'] = f['ROLES_DECLARED'][0]
            f['ROLE_STATE'] = f['ROLE_EVIDENCE'][0]['ESPECIE']
        elif criador:
            f['ROLE'], f['ROLE_STATE'] = INFLUENCIADOR, 'SINAL_DE_CRIADOR_SEM_PAPEL_PROFISSIONAL'
        f['UNIVERSO_DO_PAPEL'] = 'T8' if f['ROLE'] == AGRICULTOR else 'NAO_T8'
    return out


# ── o que a frase diz: relato, afirmacao, recomendacao ──────────────────────────────────
RE_RELATO = re.compile(
    r"(?<![a-z])(?:we found|we've found|we have found|we saw|we've seen|we have seen|we're seeing|we are seeing|"
    r"we encountered|we had|we've had|we have had|we're looking at|we are looking at|we're in the field|"
    r"we're standing|we are standing|as you can see|you can see|here we have|on our farm|on my farm|in my field|"
    r"in our field|i've seen|i have seen|i found|i saw|"
    r"abbiamo visto|abbiamo trovato|abbiamo riscontrato|abbiamo avuto|abbiamo osservato|stiamo vedendo|vediamo|"
    r"ho visto|ho trovato|nel mio campo|nella mia azienda|in azienda|come vedete|siamo in|ci troviamo|"
    r"hemos visto|hemos encontrado|hemos tenido|estamos viendo|vemos|como veis|como podeis ver|en mi finca|"
    r"en nuestra finca|en mi parcela|he visto|he encontrado|tuvimos|estamos en)(?![a-z])")
RE_RECOMENDACAO = re.compile(
    r"(?<![a-z])(?:you should|you need to|you'd want to|we recommend|i recommend|make sure|"
    r"bisogna|occorre|consigliamo|si consiglia|dovete|hay que|recomendamos|os recomiendo|debeis|conviene)(?![a-z])")


def _especie_da_frase(n: str) -> str:
    if RE_RELATO.search(n):
        return RELATO
    if RE_RECOMENDACAO.search(n):
        return RECOMENDACAO
    return AFIRMACAO


# ── cultura e problema: o dono e matriz_recorte ─────────────────────────────────────────
_PADROES_CULTURA = {k: MR._padrao(v) for k, v in MR.CROPS.items()}
_PADROES_PROBLEMA = {k: MR._padrao(v) for k, v in MR.ISSUES.items()}


def _achados(n: str, padroes: dict) -> list:
    fora = []
    for chave, rx in padroes.items():
        m = rx.search(n)
        if m:
            fora.append({'CANONICAL': chave, 'TERMO_ORIGINAL': m.group(0).strip(), 'POS_NA_FRASE': m.start()})
    return sorted(fora, key=lambda x: x['POS_NA_FRASE'])


# ── tempo do facto, NA MESMA FRASE ──────────────────────────────────────────────────────
_MESES = {
    'en': ('january', 'february', 'march', 'april', 'may', 'june', 'july', 'august', 'september', 'october',
           'november', 'december'),
    'es': ('enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 'julio', 'agosto', 'septiembre', 'octubre',
           'noviembre', 'diciembre'),
}
_M = '|'.join(_MESES['en'] + _MESES['es'])
TEMPO_ABSOLUTO = (
    (re.compile(r'(?<![a-z0-9])(\d{1,2}\s+(?:de\s+)?(?:%s)(?:\s+(?:de\s+)?\d{4}))(?![0-9])' % _M), 'DATE_EXACT'),
    (re.compile(r'(?<![a-z0-9])((?:%s)\s+\d{1,2},?\s+\d{4})(?![0-9])' % _M), 'DATE_EXACT'),
    (re.compile(r'(?<![a-z0-9])((?:%s)\s+(?:de\s+|of\s+)?\d{4})(?![0-9])' % _M), 'MONTH'),
    (re.compile(r'(?<![a-z0-9])((?:season|campaign|harvest|campana|cosecha|campagne)\s+\d{4}(?:[/-]\d{2,4})?)'
                r'(?![0-9])'), 'SEASON'),
    (re.compile(r'(?<![a-z0-9])((?:in|en|durante|during|since|desde)\s+(?:el\s+|the\s+)?(?:ano\s+|year\s+)?'
                r'(?:19|20)\d{2})(?![0-9/])'), 'APPROXIMATE'),
)
TEMPO_RELATIVO = re.compile(
    r"(?<![a-z])(?:today|yesterday|this (?:year|season|week|month|spring|summer|autumn|fall|winter)|last "
    r"(?:year|week|season|month)|right now|at the moment|currently|hoy|ayer|este ano|esta campana|esta semana|"
    r"la semana pasada|el ano pasado|ahora mismo|actualmente|oggi|ieri|quest'anno|questa settimana|"
    r"quest'annata|l'anno scorso|la settimana scorsa|attualmente|in questo momento)(?![a-z])")


def _tempo(frase: str, lang: str, published_at: str | None) -> dict:
    n = _norm(frase)
    if lang == 'it':
        r = FL.tempo_do_fato(frase, published_at=(published_at or '')[:10] or None)
        if r.get('FACT_TIME') not in (None, 'NOT_KNOWN'):
            return {'FACT_TIME': r['FACT_TIME'], 'FACT_TIME_PRECISION': r['FACT_TIME_PRECISION'],
                    'FACT_TIME_BASIS': 'leis/fato_local.tempo_do_fato · ' + str(r.get('FACT_TIME_ORIGIN')),
                    'FACT_TIME_EVIDENCE': frase[:MAX_CITACAO]}
    for rx, precisao in TEMPO_ABSOLUTO:
        m = rx.search(n)
        if m:
            valor = m.group(1)
            ano = re.search(r'(?:19|20)\d{2}', valor)
            if precisao == 'DATE_EXACT' and published_at and ano and _mesmo_dia(valor, published_at):
                continue          # PUBLICATION_STAMP_NOT_FACT_TIME
            return {'FACT_TIME': valor, 'FACT_TIME_PRECISION': precisao,
                    'FACT_TIME_BASIS': 'ESCRITO_NA_FRASE_DA_CITACAO', 'FACT_TIME_EVIDENCE': frase[:MAX_CITACAO]}
    rel = TEMPO_RELATIVO.search(n)
    if rel:
        return {'FACT_TIME': NAO_SEI, 'FACT_TIME_PRECISION': 'NOT_KNOWN',
                'FACT_TIME_BASIS': 'RELATIVA_SEM_DATA_DA_FALA: «%s» conta a partir do dia em que a pessoa falou, '
                                   'e esse dia NAO esta provado (publicacao != gravacao)' % rel.group(0),
                'FACT_TIME_EXPRESSAO': rel.group(0), 'FACT_TIME_EVIDENCE': frase[:MAX_CITACAO]}
    return {'FACT_TIME': NAO_SEI, 'FACT_TIME_PRECISION': 'NOT_KNOWN',
            'FACT_TIME_BASIS': 'nenhuma data na frase da citacao; a data de publicacao NAO preenche este campo',
            'FACT_TIME_EVIDENCE': None}


def _mesmo_dia(valor: str, published_at: str) -> bool:
    ano = re.search(r'(?:19|20)\d{2}', valor).group(0)
    dia = re.search(r'(?<![0-9])(\d{1,2})(?![0-9])', valor)
    mes = next((i + 1 for l in _MESES.values() for i, m in enumerate(l) if m in valor), None)
    if not (dia and mes):
        return False
    return '%s-%02d-%02d' % (ano, mes, int(dia.group(1))) == str(published_at)[:10]


# ── lugar do facto, NA MESMA FRASE e governado por um relato ────────────────────────────
_PAISES = {'spain': 'ES', 'espana': 'ES', 'italy': 'IT', 'italia': 'IT', 'france': 'FR', 'francia': 'FR',
           'portugal': 'PT', 'greece': 'GR', 'grecia': 'GR', 'germany': 'DE', 'alemania': 'DE',
           'united kingdom': 'GB', 'england': 'GB', 'morocco': 'MA', 'marruecos': 'MA', 'tunisia': 'TN'}
RE_LUGAR_DO_RELATO = re.compile(r"(?<![\w])(?:in|on|at|near|of|en|cerca de|a|in|nel|nella|presso)\s+(?:the\s+|la\s+|el\s+)?"
                                r"(%s(?:\s+(?:%s\s+)?%s){0,4})" % (_CAP, _LIGA, _CAP))
_NAO_LUGAR = {'T0', 'T1', 'T2', 'T3', 'Septoria', 'Fusarium', 'The', 'This', 'Today', 'Currently', 'So', 'I'}


def _lugar(frase: str, lang: str, especie: str, orgs: set) -> dict:
    nao = {'FACT_LOCATION': NAO_SEI, 'FACT_LOCATION_PRECISION': 'NOT_KNOWN', 'FACT_LOCATION_EVIDENCE': None}
    if lang == 'it':
        aceitas, _rec = FL.localizacoes_do_fato(frase, origem='TRANSCRIPT_QUOTE')
        if aceitas:
            a = aceitas[0]
            return {'FACT_LOCATION': ' ; '.join(x['FACT_LOCATION'] for x in aceitas),
                    'FACT_LOCATION_PRECISION': a['FACT_LOCATION_PRECISION'],
                    'FACT_LOCATION_BASIS': 'leis/fato_local.localizacoes_do_fato · ancora «%s»'
                                           % a['FACT_LOCATION_ANCHOR'],
                    'FACT_LOCATION_EVIDENCE': frase[:MAX_CITACAO]}
    if especie != RELATO:
        return dict(nao, FACT_LOCATION_BASIS='a frase nao e relato em primeira pessoa: um lugar nomeado numa '
                                             'afirmacao geral e MENCAO, nao lugar do facto')
    lugares = []
    for m in RE_LUGAR_DO_RELATO.finditer(frase):
        cand = m.group(1).strip(" .,'’")
        if cand.split()[0] in _NAO_LUGAR or cand in _NAO_LUGAR:
            continue
        if any(cand in o or o in cand for o in orgs):
            continue
        if cand not in lugares:
            lugares.append(cand)
    n = _norm(frase)
    for nome, iso in _PAISES.items():
        if re.search(r'(?<![a-z])%s(?![a-z])' % nome, n) and not any(_norm(l) == nome for l in lugares):
            lugares.append(nome.title())
    if not lugares:
        return dict(nao, FACT_LOCATION_BASIS='relato sem lugar escrito na mesma frase')
    so_pais = all(_norm(l) in _PAISES for l in lugares)
    return {'FACT_LOCATION': ' ; '.join(lugares),
            'FACT_LOCATION_PRECISION': 'PAIS' if so_pais else 'NOT_KNOWN',
            'FACT_LOCATION_BASIS': 'ESCRITO_NA_FRASE_DO_RELATO — topónimo nao resolvido num gazetteer; a precisao '
                                   'so e dita quando e nome de pais',
            'FACT_LOCATION_EVIDENCE': frase[:MAX_CITACAO]}


# ── o documento ─────────────────────────────────────────────────────────────────────────
def documento(texto, *, source_id=None, external_id=None, url=None, platform=None, channel=None, title=None,
              published_at=None, origem_do_texto=None, lingua_declarada=None, segmentos=None) -> dict:
    """O envelope de UM transcrito. Nada aqui e inventado: o que o chamador nao traz fica NAO SEI.

    origem_do_texto: ORIG_AUDIO (ASR local sobre o audio) · ORIG_DATASET (o dataset declara ORIGINAL
    e TRANSLATION separados) · None (legenda da plataforma sem lingua declarada)."""
    texto = texto if isinstance(texto, str) else ''
    lt = lingua(texto)
    ltit = lingua(title or '', minimo=2)
    if origem_do_texto in (ORIG_AUDIO, ORIG_DATASET):
        originalidade, porque = origem_do_texto, 'declarada por quem produziu o texto'
    elif ltit not in (NAO_SEI, lt) and lt != NAO_SEI:
        originalidade = ORIG_TRADUCAO
        porque = 'titulo em «%s» e transcrito em «%s»: a legenda e provavelmente traducao automatica' % (ltit, lt)
    else:
        originalidade, porque = NAO_SEI, 'a rota da legenda nao declara se e a lingua falada ou uma traducao'
    return {
        'SOURCE_ID': source_id or NAO_SEI, 'EXTERNAL_ID': external_id or NAO_SEI, 'URL': url or NAO_SEI,
        'PLATFORM': platform or NAO_SEI, 'PUBLISHER': channel or NAO_SEI, 'TITLE': title or NAO_SEI,
        'PUBLISHED_AT': published_at or NAO_SEI,
        'TEXT': texto, 'TEXT_SHA1': hashlib.sha1(texto.encode('utf-8')).hexdigest(),
        'TEXT_LANGUAGE': lingua_declarada or lt,
        'TEXT_LANGUAGE_BASIS': 'DECLARADA' if lingua_declarada else 'CONTAGEM_DE_PALAVRAS_FUNCIONAIS',
        'TITLE_LANGUAGE': ltit, 'QUOTE_ORIGINALITY': originalidade, 'QUOTE_ORIGINALITY_WHY': porque,
        'SEGMENTS': segmentos or [],
    }


def _tempo_do_segmento(doc: dict, pos: int):
    """Segundo do audio onde a citacao comeca, se os segmentos cobrem o texto por ordem. Senao NAO SEI."""
    segs, texto, cursor = doc.get('SEGMENTS') or [], doc['TEXT'], 0
    for s in segs:
        t = (s.get('text') or s.get('TEXTO') or '').strip()
        ini = s.get('start', s.get('T_S'))
        if not t:
            continue
        at = texto.find(t, cursor)
        if at < 0:
            return NAO_SEI
        if at <= pos < at + len(t):
            return ini
        cursor = at + len(t)
    return NAO_SEI


def _atribuir(pos: int, texto: str, autos: list):
    """O ultimo falante que se APRESENTOU A SI PROPRIO antes de `pos`, se nada o impede."""
    antes = [a for a in autos if a['POS'] <= pos]
    if not antes:
        return None, 'NINGUEM_SE_APRESENTOU_ANTES'
    a = antes[-1]
    if pos - a['POS'] > JANELA_DE_ATRIBUICAO:
        return None, 'APRESENTACAO_LONGE_DEMAIS (%d > %d caracteres)' % (pos - a['POS'], JANELA_DE_ATRIBUICAO)
    if '>>' in texto[a['FRASE'][1]:pos]:
        return None, 'TROCA_DE_VOZ_MARCADA («>>») entre a apresentacao e a frase'
    return a, 'PRESUMIDA_ULTIMA_AUTO_APRESENTACAO_SEM_TROCA_MARCADA'


_RE_NOS_INSTITUCIONAL = re.compile(r"(?<![a-z])(?:we at|noi di|nosotros en|desde|en nombre de|a nome di|on behalf of)"
                                   r"(?![a-z])")


def extrair(doc: dict) -> dict:
    texto, lang = doc['TEXT'], doc['TEXT_LANGUAGE']
    fs = frases(texto)
    aps = apresentacoes(texto, fs)
    fal = falantes(texto, aps, doc['PUBLISHER'])
    autos = [a for a in aps if a['ESPECIE'] == AUTO]
    frases_de_apresentacao = {a['FRASE'] for a in aps}
    orgs = {f['ORGANIZATION'] for f in fal.values() if f['ORGANIZATION'] != NAO_SEI}
    if doc['PUBLISHER'] != NAO_SEI:
        orgs.add(doc['PUBLISHER'])
    institucional = bool(_RE_NOS_INSTITUCIONAL.search(_norm(texto)))
    vozes, recusas = [], []
    for (a, b) in fs:
        frase = texto[a:b]
        n = _norm(frase)
        culturas, problemas = _achados(n, _PADROES_CULTURA), _achados(n, _PADROES_PROBLEMA)
        if not culturas and not problemas:
            continue
        if any(fa <= a < fb for fa, fb in frases_de_apresentacao):
            recusas.append({'POS': a, 'WHY': 'FRASE_DE_APRESENTACAO — diz quem a pessoa e, nao o que viu'})
            continue
        fim = min(b, a + MAX_CITACAO)
        especie = _especie_da_frase(n)
        ap, porque_atr = _atribuir(a, texto, autos)
        if ap is not None:
            f = fal[_speaker_id(ap['NOME'])]
            sid, kind = f['SPEAKER_ID'], PESSOA
        else:
            f = None
            sid, kind = NAO_SEI, (INSTITUICAO if institucional and doc['PUBLISHER'] != NAO_SEI else NAO_SEI)
        tempo = _tempo(frase, lang, doc['PUBLISHED_AT'] if doc['PUBLISHED_AT'] != NAO_SEI else None)
        lugar = _lugar(frase, lang, especie, orgs)
        papel = f['ROLE'] if f else NAO_SEI
        decl = ' '.join(e['TRECHO'] for e in f['ROLE_EVIDENCE']) if f else ''
        tema = [c['TERMO_ORIGINAL'] for c in culturas + problemas]
        expertise = ('PROVADA_NA_DECLARACAO' if f and any(_norm(t) in _norm(decl) for t in tema)
                     else 'NAO_PROVADA')
        voz = {
            'VOICE_ID': 'VOZ-' + _sha(doc['SOURCE_ID'], doc['EXTERNAL_ID'], doc['TEXT_SHA1'], a, fim),
            'RULE_VERSION': REGRA,
            # quem publica e quem fala sao dois factos
            'SOURCE_ID': doc['SOURCE_ID'], 'EXTERNAL_ID': doc['EXTERNAL_ID'], 'URL': doc['URL'],
            'PLATFORM': doc['PLATFORM'], 'PUBLISHER': doc['PUBLISHER'], 'TITLE': doc['TITLE'],
            'PUBLISHED_AT': doc['PUBLISHED_AT'],
            'SPEAKER_ID': sid, 'SPEAKER_KIND': kind,
            'SPEAKER_NAME': f['SPEAKER_NAME'] if f else NAO_SEI,
            'SPEAKER_KIND_WHY': ('pessoa apresentada no transcrito' if f else
                                 'sem pessoa apresentada; o texto fala em nome da instituicao que publica'
                                 if kind == INSTITUICAO else
                                 'ninguem se apresentou; o canal que publica NAO e o falante'),
            'ATTRIBUTION_STATE': porque_atr if f else NAO_SEI,
            'ATTRIBUTION_WHY': porque_atr,
            'ROLE': papel if kind == PESSOA else NAO_SEI,
            'ROLE_STATE': f['ROLE_STATE'] if f else NAO_SEI,
            'ROLE_EVIDENCE': f['ROLE_EVIDENCE'] if f else [],
            'EXPERTISE_TEMATICA': expertise,
            'CREATOR_SIGNALS': f['CREATOR_SIGNALS'] if f else [],
            'UNIVERSO_DO_PAPEL': f['UNIVERSO_DO_PAPEL'] if f else 'NAO_T8',
            'ORGANIZATION': f['ORGANIZATION'] if f else NAO_SEI,
            'ORGANIZATION_KIND': f['ORGANIZATION_KIND'] if f else NAO_SEI,
            'SPEAKER_PLACE': f['SPEAKER_PLACE'] if f else NAO_SEI,
            'SPEAKER_PLACE_KIND': 'BASE',
            # a citacao, exacta, com a posicao
            'QUOTE_ORIGINAL': texto[a:fim], 'QUOTE_POS_START': a, 'QUOTE_POS_END': fim,
            'QUOTE_TRUNCATED': fim < b,
            'QUOTE_T_S': _tempo_do_segmento(doc, a),
            'QUOTE_LANGUAGE': doc['TEXT_LANGUAGE'],
            'QUOTE_ORIGINALITY': doc['QUOTE_ORIGINALITY'], 'QUOTE_ORIGINALITY_WHY': doc['QUOTE_ORIGINALITY_WHY'],
            'STATEMENT_KIND': especie,
            'CROP': culturas[0]['CANONICAL'] if culturas else NAO_SEI, 'CROP_MATCHES': culturas,
            'ISSUE': problemas[0]['CANONICAL'] if problemas else NAO_SEI, 'ISSUE_MATCHES': problemas,
            'VOCABULARY_OWNER': 'motor/matriz_recorte.py (CROPS, ISSUES)',
        }
        voz.update(tempo)
        voz.update(lugar)
        voz['INTERPRETACAO'] = {
            'AUTOR': AUTOR_DA_INTERPRETACAO,
            'LEITURA': '%s · cultura=%s · problema=%s' % (especie, voz['CROP'], voz['ISSUE']),
        }
        voz['WHAT_IT_PROVES'] = ('que esta frase foi dita/escrita neste documento publicado'
                                 + (' e que o falante a disse em primeira pessoa como relato'
                                    if especie == RELATO else ''))
        voz['WHAT_IT_DOES_NOT_PROVE'] = ('incidencia ou pressao (sem metodo e sem denominador, VOZ DE CAMPO NAO E '
                                         'INCIDENCIA); expertise do falante no tema'
                                         + ('' if expertise == 'PROVADA_NA_DECLARACAO' else ' (nao declarada)')
                                         + '; lugar do facto a partir do lugar da pessoa')
        vozes.append(voz)
    return {'DOCUMENTO': {k: v for k, v in doc.items() if k not in ('TEXT', 'SEGMENTS')},
            'FALANTES': list(fal.values()), 'VOZES': vozes, 'RECUSAS': recusas}


# ── o contrato do item Voce ─────────────────────────────────────────────────────────────
CAMPOS_OBRIGATORIOS = (
    'VOICE_ID', 'RULE_VERSION', 'SOURCE_ID', 'EXTERNAL_ID', 'PUBLISHER', 'PUBLISHED_AT',
    'SPEAKER_ID', 'SPEAKER_KIND', 'SPEAKER_NAME', 'ATTRIBUTION_STATE', 'ROLE', 'ROLE_STATE', 'ROLE_EVIDENCE',
    'EXPERTISE_TEMATICA', 'UNIVERSO_DO_PAPEL', 'ORGANIZATION', 'SPEAKER_PLACE',
    'QUOTE_ORIGINAL', 'QUOTE_POS_START', 'QUOTE_POS_END', 'QUOTE_ORIGINALITY', 'STATEMENT_KIND',
    'CROP', 'ISSUE', 'FACT_TIME', 'FACT_TIME_BASIS', 'FACT_LOCATION', 'FACT_LOCATION_BASIS',
    'INTERPRETACAO', 'WHAT_IT_PROVES', 'WHAT_IT_DOES_NOT_PROVE',
)


def validar_voce(v: dict, doc: dict) -> list:
    """[] se a voz cumpre o contrato; senao, a lista do que falha (uma frase por lei)."""
    erros = []
    for c in CAMPOS_OBRIGATORIOS:
        if c not in v or v[c] in (None, ''):
            erros.append('CAMPO_EM_FALTA: %s' % c)
    if erros:
        return erros
    texto = doc['TEXT']
    if texto[v['QUOTE_POS_START']:v['QUOTE_POS_END']] != v['QUOTE_ORIGINAL']:
        erros.append('CITACAO_NAO_E_O_TEXTO: QUOTE_ORIGINAL != texto[inicio:fim]')
    if v['INTERPRETACAO'].get('AUTOR') != AUTOR_DA_INTERPRETACAO or v['INTERPRETACAO'].get('LEITURA', '') in \
            v['QUOTE_ORIGINAL']:
        erros.append('INTERPRETACAO_SEM_ASSINATURA_OU_DENTRO_DA_CITACAO')
    if v['ROLE'] not in PAPEIS:
        erros.append('PAPEL_FORA_DO_VOCABULARIO: %s' % v['ROLE'])
    if v['ROLE'] not in (NAO_SEI, INFLUENCIADOR):
        ev = [e for e in v['ROLE_EVIDENCE'] if e['ROLE'] == v['ROLE']]
        if not ev or ev[0]['TRECHO'] not in texto:
            erros.append('PAPEL_SEM_PROVA_NO_TRANSCRITO: %s' % v['ROLE'])
    if v['ROLE'] == INFLUENCIADOR and (v['ROLE_EVIDENCE'] or not v['CREATOR_SIGNALS']):
        erros.append('INFLUENCIADOR_COM_PAPEL_PROFISSIONAL_OU_SEM_SINAL')
    if (v['UNIVERSO_DO_PAPEL'] == 'T8') != (v['ROLE'] == AGRICULTOR):
        erros.append('T8_SO_E_AGRICULTOR')
    if v['SPEAKER_KIND'] != PESSOA and (v['SPEAKER_ID'] != NAO_SEI or v['ROLE'] != NAO_SEI):
        erros.append('INSTITUICAO_OU_NINGUEM_NAO_TEM_SPEAKER_ID_NEM_PAPEL_DE_PESSOA')
    if v['SPEAKER_KIND'] == PESSOA and v['SPEAKER_ID'] == NAO_SEI:
        erros.append('PESSOA_SEM_SPEAKER_ID')
    if v['SPEAKER_ID'] != NAO_SEI and v['SPEAKER_NAME'] == v['PUBLISHER']:
        erros.append('PUBLISHER_VIROU_FALANTE')
    if v['ATTRIBUTION_STATE'].startswith('PROVADA'):
        erros.append('ATRIBUICAO_PROVADA_SEM_DIARIZACAO')
    if v['FACT_LOCATION'] != NAO_SEI:
        ev = v.get('FACT_LOCATION_EVIDENCE') or ''
        if ev not in v['QUOTE_ORIGINAL'] and v['QUOTE_ORIGINAL'] not in ev:
            erros.append('LUGAR_DO_FACTO_FORA_DA_CITACAO')
        if v['SPEAKER_PLACE'] != NAO_SEI and v['SPEAKER_PLACE'] in v['FACT_LOCATION'] and \
                v['SPEAKER_PLACE'] not in v['QUOTE_ORIGINAL']:
            erros.append('LUGAR_DA_PESSOA_VIROU_LUGAR_DO_FACTO')
    if v['FACT_TIME'] != NAO_SEI:
        if v['FACT_TIME'] == v['PUBLISHED_AT'] or str(v['PUBLISHED_AT'])[:10] == v['FACT_TIME']:
            erros.append('PUBLICACAO_VIROU_TEMPO_DO_FACTO')
        if not v.get('FACT_TIME_EVIDENCE'):
            erros.append('TEMPO_DO_FACTO_SEM_TRECHO')
    if 'INCIDENCIA' not in v['WHAT_IT_DOES_NOT_PROVE'].upper():
        erros.append('VOZ_SEM_A_RESSALVA_DE_INCIDENCIA')
    if v['CROP'] == NAO_SEI and v['ISSUE'] == NAO_SEI:
        erros.append('VOZ_SEM_CULTURA_NEM_PROBLEMA')
    return erros


# ── adaptadores dos transcritos que estao no repositorio ────────────────────────────────
def documentos_do_repo(raiz: str = RAIZ) -> list:
    """Os transcritos versionados (fixtures), cada um com o seu envelope. So leitura."""
    import glob
    docs = []
    es = os.path.join(raiz, 'data', 'samples', 'ES-T8-001-transcricoes.json')
    if os.path.exists(es):
        d = json.load(open(es, encoding='utf-8'))
        for t in d['TRANSCRIPTS']:
            docs.append(documento(t.get('TRANSCRIPT_ORIGINAL'), source_id=d.get('SOURCE_ID'),
                                  external_id=t.get('EXTERNAL_ID'), url=t.get('URL'), platform=t.get('PLATFORM'),
                                  channel=t.get('CHANNEL_NAME'), title=t.get('TITLE'),
                                  published_at=t.get('PUBLICATION_DATE'),
                                  origem_do_texto=ORIG_DATASET if t.get('TRANSLATION') is None else None))
    meta = {}
    for f in sorted(glob.glob(os.path.join(raiz, 'data', 'samples', 'SENSOR-PILOT', 'VIDEOS-*.json'))):
        for it in json.load(open(f, encoding='utf-8')).get('ITEMS', []):
            meta.setdefault(it.get('EXTERNAL_ID'), it)
    for f in sorted(glob.glob(os.path.join(raiz, 'data', 'samples', 'SENSOR-PILOT', 'TRANSCRICOES-*.json'))):
        d = json.load(open(f, encoding='utf-8'))
        for it in d.get('ITEMS', []):
            if not isinstance(it.get('TRANSCRIPT'), str):
                continue
            vid = (it.get('SOURCE_URL') or '').rsplit('v=', 1)[-1] or None
            m = meta.get(vid, {})
            docs.append(documento(it['TRANSCRIPT'], source_id=d.get('SOURCE_ID'), external_id=vid,
                                  url=it.get('SOURCE_URL'), platform='YOUTUBE', channel=m.get('CHANNEL'),
                                  title=m.get('TITLE'), published_at=(m.get('PUBLISHED_AT') or '')[:10] or None))
    reel = os.path.join(raiz, 'data', 'samples', 'REEL-TRANSCRICOES', 'TRANSCRICOES-REEL.json')
    if os.path.exists(reel):
        d = json.load(open(reel, encoding='utf-8'))
        for it in d.get('ITEMS', []):
            r = it.get('REEL') or {}
            if not it.get('TRANSCRIPT_TEXT'):
                continue
            docs.append(documento(it['TRANSCRIPT_TEXT'], source_id=d.get('SOURCE_ID'), external_id=r.get('POST_ID'),
                                  url=r.get('SOURCE_URL'), platform=r.get('PLATFORM'), channel=r.get('ACCOUNT_NAME'),
                                  title=r.get('TITLE'), published_at=(r.get('PUBLISHED_AT') or '')[:10] or None,
                                  origem_do_texto=ORIG_AUDIO, segmentos=it.get('SEGMENTS'),
                                  lingua_declarada=it.get('LANGUAGE') if it.get('LANGUAGE_SOURCE') == 'DECLARED'
                                  else None))
    return docs


def medir(raiz: str = RAIZ) -> dict:
    from collections import Counter
    docs = documentos_do_repo(raiz)
    c = Counter()
    violacoes = Counter()
    for d in docs:
        r = extrair(d)
        c['DOCUMENTOS'] += 1
        c['FALANTES'] += len(r['FALANTES'])
        for v in r['VOZES']:
            c['VOZES'] += 1
            c['KIND=' + v['SPEAKER_KIND']] += 1
            c['ROLE=' + v['ROLE']] += 1
            c['STATEMENT=' + v['STATEMENT_KIND']] += 1
            c['ORIGINALITY=' + v['QUOTE_ORIGINALITY']] += 1
            c['FACT_TIME=' + ('SIM' if v['FACT_TIME'] != NAO_SEI else NAO_SEI)] += 1
            c['FACT_LOCATION=' + ('SIM' if v['FACT_LOCATION'] != NAO_SEI else NAO_SEI)] += 1
            for e in validar_voce(v, d):
                violacoes[e.split(':')[0]] += 1
    return {'CONTAGEM': dict(sorted(c.items())), 'VIOLACOES_DO_CONTRATO': dict(violacoes)}


if __name__ == '__main__':
    if '--medir' in sys.argv:
        print(json.dumps(medir(), ensure_ascii=False, indent=1))
    else:
        print(__doc__)
