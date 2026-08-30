#!/usr/bin/env python3
"""
IDENTIDADE DO CANAL — decide, de graça, quais candidatos são mesmo a pessoa.

    python3 scripts/sensor_canal_identidade.py

POR QUE ISTO NÃO É PARTE DA COLETA
-----------------------------------
A busca por nome devolve CANDIDATOS. Quem decide se o candidato é a pessoa é este
arquivo, que roda sobre o material JÁ PAGO e não gasta nada. Separar as duas coisas tem
uma consequência prática: quando eu errar a regra de identidade — e eu já errei uma vez
nesta missão — o conserto é gratuito e refazível, em vez de exigir nova execução.

    SEARCH_HIT != PERSON.

E a lição que a casa já pagou: a busca por "Pasquale De Vita" no LinkedIn devolveu o
presidente da Unione Petrolifera, um vendedor de esquadrias e um diretor de TI, todos de
nome idêntico. Um portão que parasse no nome teria promovido o presidente da associação
do petróleo a pesquisador de trigo duro.

O QUE DECIDE, E EM QUE ORDEM
-----------------------------
1. **Nome** — normalizado (acento, travessão U+2010, caixa). Nome que não bate encerra o
   assunto; nome que bate não prova nada sozinho.
2. **Lugar** — a cidade que a PRÓPRIA PESSOA declara no ORCID contra a cidade que o perfil
   declara. Dois campos declarados, de duas fontes independentes.

O modo `Short` do ator não devolve cargo nem empresa — só nome, lugar e URL. Então o lugar
é a única corroboração disponível nesta rodada, e o estado publicado diz exatamente isso.
Onde o lugar não existe dos dois lados, o resultado é `PLAUSIBLE`, nunca `PROVED`.

O CASO QUE OBRIGA A OLHAR DUAS CIDADES
----------------------------------------
`Blanca B. Landa` declara **Madrid** no ORCID — que é o endereço central do CSIC — e o
perfil do LinkedIn diz **Córdoba**, que é onde fica o Instituto de Agricultura Sostenible
que o OpenAlex registra para ela. As duas coisas são verdade ao mesmo tempo: a instituição
empregadora é nacional e a lotação é local.

Por isso a comparação aceita a cidade do ORCID **e** a cidade conhecida da instituição do
OpenAlex. Exigir só a primeira reprovaria uma identidade correta; aceitar qualquer coisa
aprovaria homônimo. O meio-termo é declarado, não implícito.
"""
import json
import os
import re
import sys
import unicodedata

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SAMPLES = os.path.join(ROOT, 'data', 'samples')
PILOT = os.path.join(SAMPLES, 'SENSOR-PILOT')
CACHE = os.path.join(ROOT, 'data', 'raw', 'SPEAKER-UNIVERSO', 'orcid')

NAO_SEI = 'NÃO SEI'

# Cidade das instituições que aparecem no quadro. NÃO é um dicionário geral de geografia:
# é a lista fechada das instituições DESTE piloto, escrita à mão e auditável linha a linha.
# Um mapa aberto seria inferência; este é declaração.
CIDADE_DA_INSTITUICAO = {
    'instituto de agricultura sostenible': 'cordoba',
    'estacion experimental del zaidin': 'granada',
    'centre for plant biotechnology and genomics': 'madrid',
    'university of milan': 'milan',
    'university of verona': 'verona',
    'university of turin': 'turin',
    'institute of sciences of food production': 'bari',
}


def _norm(s):
    s = unicodedata.normalize('NFKD', str(s or ''))
    s = ''.join(c for c in s if not unicodedata.combining(c))
    for t in ('‐', '‑', '‒', '–', '—', '−'):
        s = s.replace(t, '-')
    return re.sub(r'[^a-z0-9 ]+', ' ', s.lower())


def _tokens(nome):
    return [t for t in _norm(nome).split() if len(t) > 1]


def _cidades_orcid(orcid):
    """Cidades que a própria pessoa declara no ORCID. Vazio é vazio, não é 'nenhuma'."""
    caminho = os.path.join(CACHE, '%s.employments.json' % orcid)
    if not os.path.exists(caminho):
        return [], []
    with open(caminho, encoding='utf-8') as f:
        d = json.load(f)
    atuais, todas = [], []
    for g in d.get('affiliation-group', []):
        for s in g.get('summaries', []):
            e = s.get('employment-summary') or {}
            cidade = ((e.get('organization') or {}).get('address') or {}).get('city')
            if not cidade:
                continue
            todas.append(_norm(cidade))
            if e.get('end-date') is None:
                atuais.append(_norm(cidade))
    return atuais, todas


def _texto_local(v):
    """O ator devolve o lugar ora como string, ora como {'linkedinText': ...}."""
    if isinstance(v, dict):
        return v.get('linkedinText') or v.get('text') or ''
    return v if isinstance(v, str) else ''


def resolver(cand, pessoa):
    """→ (estado, evidência). Nome decide o veto; lugar decide a promoção."""
    alvo, achado = cand.get('NAME'), cand.get('PROFILE_NAME')
    ta, tf = _tokens(alvo), _tokens(achado)
    if not tf:
        return 'NOT_PROVED', 'o resultado não trouxe nome'

    # ORDEM E CONTIGUIDADE, não só presença. Este teste nasceu de um falso positivo que a
    # primeira versão produziu e publicou:
    #
    #     alvo   Blanca B. Landa            -> [blanca, landa]
    #     achado BLANCA PARGA LANDA         -> [blanca, parga, landa]   OUTRA PESSOA
    #     achado Blanca B. Landa del Castillo -> [blanca, landa, del, castillo]  a mesma
    #
    # "contém todos os termos" aprova os dois. E a cidade não salvava: o ORCID dela declara
    # Madrid (endereço central do CSIC) e a homônima também é de Madrid. Nome fraco mais
    # lugar coincidente produz uma identidade errada com cara de provada.
    #
    # Sobrenome composto ESPANHOL acrescenta ao FIM ("Landa del Castillo"); homônimo
    # diferente INTERCALA no meio ("Parga" entre Blanca e Landa). Exigir os termos do alvo
    # em sequência separa os dois casos sem precisar de lista de exceções.
    faltam = [t for t in ta if t not in tf]
    if faltam:
        return 'NOT_PROVED', (
            'o perfil "%s" não contém todos os termos do nome-alvo "%s" (falta: %s). '
            'NAME_MATCH parcial não é pessoa.' % (achado, alvo, ', '.join(faltam)))
    seguido = any(tf[i:i + len(ta)] == ta for i in range(len(tf) - len(ta) + 1))
    if not seguido:
        return 'NOT_PROVED', (
            'o perfil "%s" tem os termos de "%s" mas NÃO em sequência — há outro '
            'sobrenome no meio. Sobrenome composto acrescenta ao fim; homônimo diferente '
            'intercala. Este intercala.' % (achado, alvo))

    atuais, todas = _cidades_orcid(cand.get('ORCID_DA_FICHA') or '')
    inst = _norm(pessoa.get('INSTITUTION'))
    cidade_inst = next((c for k, c in CIDADE_DA_INSTITUICAO.items() if k in inst), None)
    esperadas = set(atuais) | ({cidade_inst} if cidade_inst else set())
    local = _norm(_texto_local(cand.get('PROFILE_LOCATION')))

    if not esperadas:
        return 'PLAUSIBLE', (
            'nome completo bate ("%s"), mas o ORCID não declara cidade e a instituição '
            'não está no mapa fechado — não há segundo campo para corroborar.' % achado)
    if not local:
        return 'PLAUSIBLE', (
            'nome completo bate ("%s"), mas o perfil não declara lugar.' % achado)

    bate = [c for c in esperadas if c and c in local]
    if bate:
        return 'PROVED', (
            'nome completo bate ("%s") E o lugar declarado no perfil ("%s") contém a '
            'cidade declarada de forma independente (%s). Duas fontes, dois campos '
            'declarados.' % (achado, _texto_local(cand.get('PROFILE_LOCATION')),
                             ', '.join(sorted(bate))))
    passadas = [c for c in todas if c and c in local]
    if passadas:
        return 'PLAUSIBLE', (
            'nome bate e o lugar ("%s") casa com uma cidade que o ORCID declara como '
            'vínculo ENCERRADO (%s). Vínculo passado não sustenta o presente.'
            % (_texto_local(cand.get('PROFILE_LOCATION')), ', '.join(sorted(passadas))))
    return 'NOT_PROVED', (
        'nome bate, mas o lugar do perfil ("%s") não casa com nenhuma cidade declarada '
        '(%s). Homônimo em outra cidade é o caso mais comum e mais caro.'
        % (_texto_local(cand.get('PROFILE_LOCATION')), ', '.join(sorted(esperadas))))


def montar():
    with open(os.path.join(SAMPLES, 'SPEAKER-UNIVERSE-PILOT-V1.json'), encoding='utf-8') as f:
        pessoas = {p['NAME']: p for p in json.load(f)['PEOPLE']}
    saida, vistos = [], set()
    for lote in ('A', 'B'):
        caminho = os.path.join(PILOT, 'CANAIS-%s.json' % lote)
        if not os.path.exists(caminho):
            continue
        with open(caminho, encoding='utf-8') as f:
            d = json.load(f)
        for c in d['ITEMS']:
            if c['SOURCE_PLATFORM'] != 'LINKEDIN':
                continue
            p = pessoas.get(c['NAME']) or {}
            c = dict(c, ORCID_DA_FICHA=p.get('ORCID'))
            estado, ev = resolver(c, p)
            # DEDUPE GLOBAL: dois lotes podem devolver o mesmo perfil. É UM objeto
            # lógico com duas rotas de descoberta, nunca duas evidências.
            chave = (c['SOURCE_PLATFORM'], c.get('EXTERNAL_ID'))
            if chave in vistos:
                continue
            vistos.add(chave)
            saida.append({
                'PERSON_ID': c['PERSON_ID'], 'NAME': c['NAME'],
                'CASE_ID': c['CASE_ID'], 'COUNTRY_OF_PERSON': c['COUNTRY_OF_PERSON'],
                'INSTITUTION': c['INSTITUTION'],
                'PLATFORM': 'LINKEDIN', 'PROFILE_NAME': c['PROFILE_NAME'],
                'PROFILE_LOCATION': _texto_local(c.get('PROFILE_LOCATION')) or NAO_SEI,
                'SOURCE_URL': c['SOURCE_URL'], 'EXTERNAL_ID': c.get('EXTERNAL_ID'),
                'CHANNEL_KIND': 'PERSON_OWN_CHANNEL',
                'CHANNEL_IDENTITY_STATE': estado,
                'CHANNEL_IDENTITY_EVIDENCE': ev,
                'LOTE': c.get('LOTE'), 'RUNNER_NAME': c.get('RUNNER_NAME'),
                'COLLECTION_RUN_ID': c.get('COLLECTION_RUN_ID'),
            })
    return saida


if __name__ == '__main__':
    itens = montar()
    est = {}
    for i in itens:
        est[i['CHANNEL_IDENTITY_STATE']] = est.get(i['CHANNEL_IDENTITY_STATE'], 0) + 1
    pessoas_com = len({i['NAME'] for i in itens if i['CHANNEL_IDENTITY_STATE'] == 'PROVED'})
    corpo = {
        'SOURCE_ID': 'SENSOR-PILOT/CANAL-IDENTIDADE',
        'source': 'derivado dos candidatos já pagos — nenhuma execução nova',
        'SOURCE_LOCATION': 'derivado', 'FACT_LOCATION': 'n/a',
        'ORIGINAL_LANGUAGE': 'pt', 'EVIDENCE_CLASS': 'DERIVED_IDENTITY',
        'APIFY_RUNS': 0, 'COST_USD': 0,
        'METODO': ('nome completo normalizado decide o veto; cidade declarada no ORCID '
                   '(ou cidade conhecida da instituição do OpenAlex) decide a promoção'),
        'LIMITE_DECLARADO': ('o modo Short do ator não devolve cargo nem empresa. O papel '
                             'declarado — que é a evidência mais forte — não foi lido '
                             'nesta rodada, e por isso nenhum estado se apoia nele.'),
        'CANDIDATES': len(itens),
        'BY_STATE': est,
        'PEOPLE_WITH_PROVED_PROFILE': pessoas_com,
        'ITEMS': itens,
    }
    destino = os.path.join(PILOT, 'CANAL-IDENTIDADE.json')
    os.makedirs(PILOT, exist_ok=True)
    with open(destino, 'w', encoding='utf-8') as f:
        json.dump(corpo, f, ensure_ascii=False, indent=1)
    print('%d candidatos LinkedIn · %s' % (len(itens), est))
    print('pessoas com perfil PROVADO: %d' % pessoas_com)
    for i in itens:
        if i['CHANNEL_IDENTITY_STATE'] != 'NOT_PROVED':
            print('  %-10s %-24s -> %-30s %s' % (
                i['CHANNEL_IDENTITY_STATE'], i['NAME'][:24],
                str(i['PROFILE_NAME'])[:30], i['PROFILE_LOCATION'][:28]))
