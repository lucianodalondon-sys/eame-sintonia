#!/usr/bin/env python3
"""
APARIÇÃO, NÃO POSSE — o vídeo mostra ESTA pessoa? (de graça, sobre o que já foi pago)

    py scripts/youtube_aparicao.py julgar    # decide os 58 candidatos de YouTube
    py scripts/youtube_aparicao.py teste     # as provas, sem rede

⚠️ ESTE ARQUIVO NÃO DECIDE POSSE DE CANAL, E O NOME DIZ ISSO
===============================================================
`sensor_canal_identidade.py` responde "este PERFIL é a pessoa?" — e responde para
LinkedIn, onde o perfil PERTENCE a alguém. Um vídeo não pertence a quem aparece
nele: `Via alle semine a Mais Domani` está no canal de `L'Informatore Agrario`, e
Massimo Blandino aparece dentro. A própria coleta já escreveu isso no campo
`CHANNEL_KIND = INSTITUTIONAL_CHANNEL_FEATURING_PERSON_CANDIDATE`.

    APARECER NUM VÍDEO NÃO É SER DONO DO CANAL.

Por isso os estados aqui são `APPEARANCE_*` e `CHANNEL_OWNERSHIP` sai
`NOT_CLAIMED` em 100% dos casos. Confundir os dois entregaria ao Marketing o
canal de uma revista como se fosse o canal de um pesquisador.

POR QUE ESTE ARQUIVO EXISTE, E NÃO UM PATCH NO OUTRO
======================================================
`sensor_canal_identidade.py` é da missão de sensores. A regra de isolamento desta
casa proíbe corrigir em silêncio código de outra missão. Então a lei dele é
OBEDECIDA e citada aqui, e o arquivo dele não é tocado.

A LEI HERDADA, LITERAL
========================
De `sensor_canal_identidade.py`:

    "SEARCH_HIT != PERSON."
    1. Nome — nome que não bate encerra o assunto; nome que bate não prova nada sozinho.
    2. Corroboração — dois campos declarados, de fontes independentes.
    "Onde o lugar não existe dos dois lados, o resultado é PLAUSIBLE, nunca PROVED."

E a lição que ela já pagou: a busca por "Pasquale De Vita" devolveu o presidente
da Unione Petrolifera, um vendedor de esquadrias e um diretor de TI.

O QUE MUDA NO YOUTUBE: NÃO EXISTE CIDADE
==========================================
Um vídeo não declara cidade. A corroboração disponível é outra, e por ser outra
tem nome próprio: INSTITUIÇÃO citada no texto, ou DOMÍNIO TÉCNICO do conteúdo.
Isso é uma corroboração DIFERENTE, não a mesma com outro rótulo.

⚠️ O ATALHO ÓBVIO ESTÁ PROIBIDO, E FOI MEDIDO
------------------------------------------------
Seria natural exigir que o vídeo falasse do tema do `CASE_ID` da pessoa. Medido
em 2026-09-03, isso reprovaria os acertos:

    Massimo Blandino · CASE_ID = IT-DURUM_WHEAT-FUSARIUM (trigo duro)
      aparições reais: "Via alle semine a Mais Domani 2023"      → MILHO
                       "Tempo di semina del mais"                 → MILHO
                       "Mais e cambiamento climatico"             → MILHO

O `CASE_ID` diz por qual recorte a pessoa ENTROU no universo, não sobre o que ela
fala em público. Um agrônomo de cereais publica sobre o cereal da estação.

    O RECORTE QUE ACHOU A PESSOA NÃO É O ASSUNTO DA PESSOA.

Por isso o domínio técnico é medido de forma LARGA (agronomia em geral), e o
`CASE_ID` entra como reforço quando bate — nunca como portão que reprova.

⚠️ A INICIAL NÃO IDENTIFICA NINGUÉM
=====================================
`F. Quaglino` é inicial + sobrenome. Medido: essa busca devolveu concerto de
orquestra, melanoma, psicologia junguiana e um Open Day de analistas. Nenhuma
regra de corroboração conserta isso, porque o problema é o DENOMINADOR: `F.` são
todos os nomes que começam com F.

    NOME COM INICIAL NÃO PODE SER PROVADO. NO MÁXIMO, PLAUSÍVEL.

⚠️ DUAS PERGUNTAS, DOIS CAMPOS — E FOI A PROVA QUE ME ENSINOU
===============================================================
A primeira versão deste arquivo reprovou `GF 2022 - Intervista sulle strategie di
lotta allo Scaphoideus`, do canal `Giornate Fitopatologiche`, para Nicola Mori.
Tecnicamente correto: o nome dele NÃO está no título. E completamente inútil,
porque Scaphoideus é a especialidade declarada do Mori e o canal é um congresso
de fitopatologia.

O defeito era ter UMA pergunta onde existem DUAS:

    APPEARANCE_STATE    esta pessoa aparece neste vídeo?
    CONTENT_RELEVANCE   este vídeo é do domínio técnico?

No LinkedIn o nome do perfil É a pessoa, e por isso lá uma pergunta bastava. No
YouTube o título não é o nome de ninguém: a busca casou por transcrição, tag ou
metadado que o artefato não preservou.

    NÃO CONSEGUIR PROVAR A PESSOA NÃO TORNA O VÍDEO IRRELEVANTE.

Um vídeo pode sair NOT_PROVED para a pessoa e TECHNICAL_DOMAIN para o conteúdo —
e aí ele não é elo de pessoa, é PISTA DE FONTE: o canal existe, é técnico, e vale
entrar no registro de fontes mesmo sem saber quem aparece.

E o inverso também aparece no corpus: `Don Nicola Mazza` é um colégio nomeado em
homenagem a OUTRO Nicola. Nome dentro de nome de instituição não é a pessoa.
"""
import json
import os
import re
import sys
import unicodedata

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)

SAMPLES = os.path.join(ROOT, 'data', 'samples')
PILOT = os.path.join(SAMPLES, 'SENSOR-PILOT')
SAIDA = os.path.join(SAMPLES, 'YOUTUBE-APARICAO')
NAO_SEI = 'NOT_KNOWN'
MISSION = '18-APARICAO-DE-PESSOA-EM-VIDEO'

# Domínio técnico agrícola, LARGO de propósito (ver o bloco do CASE_ID acima).
# Raízes em IT/ES/FR/EN porque o corpus é multilíngue.
DOMINIO = [
    'agronom', 'agricol', 'agricultur', 'coltur', 'coltiv', 'semin', 'raccolt',
    'vite', 'vigne', 'viticolt', 'oliv', 'mais', 'frumento', 'grano', 'ceral',
    'cereal', 'riso', 'soia', 'pomodor', 'fitopatolog', 'fitosanitar', 'difesa',
    'diserb', 'erbicid', 'fungicid', 'insetticid', 'parassit', 'micotossin',
    'fusari', 'peronospor', 'oidio', 'scafoide', 'scaphoideus', 'flavescen',
    'popillia', 'agronomia', 'campo', 'terreno', 'concimaz', 'irrigaz',
    'sperimenta', 'prova di campo', 'mycotoxin', 'plant health', 'crop',
]

# Contextos que NAO sao a pessoa mesmo quando o nome aparece. Cada um veio do corpus.
FORA_DE_DOMINIO = [
    'concerto', 'orchestra', 'melanoma', 'psicolog', 'junghian', 'analitica',
    'laurea', 'graduation', 'latine loqui', 'sociologia', 'genome', 'encode',
    'finanziaria', 'imprese pugliesi', 'anno accademico', 'rettore',
]


# ⚠️ COLISOES MEDIDAS EM 2026-09-03 SOBRE OS 58 CANDIDATOS, PALAVRA A PALAVRA.
# Eu preguei fronteira de palavra no classificador de papel e esqueci dela aqui.
# O `semin` de `semina` casou dentro de `seminario` — um seminario de SOCIOLOGIA
# entrou como dominio agricola. E' o `ftalimida contem imida` de novo, e desta vez
# em codigo meu.
#
#     A REGRA QUE EU ESCREVI NUM ARQUIVO NAO SE APLICA SOZINHA NO OUTRO.
#
# A fronteira de INICIO de palavra mata a maioria: `vite` dentro de `activite` e
# `invite` (frances), `riso` dentro de `harrison`, `mais` dentro de `desormais`,
# `rettore` dentro de `direttore`. As que sobrevivem ao inicio de palavra estao
# listadas aqui, uma a uma, porque foram VISTAS — nao imaginadas.
EXCLUSOES = {
    'semin': {'seminario', 'seminari', 'seminarista', 'seminaristi'},
    'riso': {'risorsa', 'risorse'},
    'campo': {'campofiore'},
    'coltur': {'colturale'},          # tecnico, mas nao diz que o video e' de campo
}


def casa(raiz, texto):
    """A raiz aparece como INICIO de palavra, e a palavra nao esta nas exclusoes."""
    for m in re.finditer(r'(?<![a-z])%s[a-z]*' % re.escape(raiz), texto):
        if m.group(0) not in EXCLUSOES.get(raiz, ()):
            return True
    return False


# ⚠️ TERCEIRO EIXO: APARECER, FALAR E SER CREDITADO SAO TRES COISAS.
# Medido em 2026-09-03: de 18 casamentos de nome nos italianos, so UM tem o nome
# no TITULO. Todos os outros casam na DESCRICAO — e ali o nome tanto pode estar em
# "Intervista a Nicola Mori" quanto em "Moretti Antonio, Logrieco Antonio,
# Institute of Sciences of Food Production, Bari".
#
# O segundo caso e' real e e' outra coisa: Logrieco assina o trabalho, e quem
# apresenta e' Moretti. Contar coautoria como aparicao entregaria como "voz
# publica" alguem que nao abriu a boca no video.
#
#     COAUTORIA NAO E FALA. CREDITO NAO E APARICAO.
#
# Isto nao muda APPEARANCE_STATE — muda de pergunta, e por isso ganha campo proprio.
FALA = ['intervista', 'intervento', 'relatore', 'relazione di', 'ospite',
        'a cura di', 'presenta', 'parla', 'testimonianza', 'interview',
        'speaker', 'entrevista', 'ponente', 'con la partecipazione']

# ⚠️ VERBOS DE EXPOSICAO — o sinal que separou o falante do coautor, medido no corpus.
# A primeira versao classificou como CREDITED a descricao real:
#
#   "Nicola Mori, Dip. di Biotecnologie - Universita di Verona, RIPORTA i dati
#    sull'aumentata pericolosita dello Scaphoideus titanus [...] SOTTOLINEANDO
#    l'importanza del monitoraggio e DESCRIVENDO [...]"
#
# Ela viu nome + virgula + instituicao e concluiu "lista de autores". Mas ali ha UM
# nome so, e depois dele um verbo de exposicao — e' aposto de PALESTRANTE.
#
# O caso Moretti/Logrieco e' o oposto e nao tem verbo nenhum:
#   "Moretti Antonio, Logrieco Antonio, Institute of Sciences of Food Production"
#
#     UM NOME + INSTITUICAO + VERBO = ALGUEM EXPONDO.
#     DOIS NOMES + INSTITUICAO, SEM VERBO = ASSINATURA DE TRABALHO.
VERBOS_DE_EXPOSICAO = ['riporta', 'sottolinea', 'descriv', 'spiega', 'illustra',
                       'racconta', 'analizza', 'commenta', 'espone', 'mostra',
                       'ha presentato', 'interviene']


def papel_na_aparicao(nome, titulo, descricao):
    """→ (papel, por_que). SPEAKING / CREDITED / UNSPECIFIED."""
    t, d = norm(titulo), norm(descricao)
    if nome_no_texto(nome, t)[0]:
        return 'SPEAKING', 'o nome esta no TITULO do video'
    janela = ''
    m = None
    partes = [x for x in re.split(r'[^a-z]+', norm(nome)) if len(x) > 1]
    if partes:
        m = re.search(re.escape(partes[-1]), d)
    if m:
        janela = d[max(0, m.start() - 90):m.end() + 90]
    for f in FALA:
        if f in janela:
            return 'SPEAKING', 'marcador de fala perto do nome: "%s"' % f
    for v in VERBOS_DE_EXPOSICAO:
        if v in janela:
            return 'SPEAKING', 'verbo de exposicao perto do nome: "%s"' % v

    # ⚠️ LISTA DE AUTORES exige DOIS nomes de pessoa, nao so' virgulas. A contagem
    # de virgulas sozinha reprovou um palestrante real (ver o bloco acima).
    orig = descricao or ''
    m2 = re.search(re.escape(partes[-1]), norm(orig)) if partes else None
    jan_orig = orig[max(0, m2.start() - 90):m2.end() + 90] if m2 else ''
    nomes = re.findall(r'\b[A-Z][a-zà-ÿ]{2,}\s+[A-Z][a-zà-ÿ]{2,}\b', jan_orig)
    if len(set(nomes)) >= 2 and re.search(
            r'(institut|universit|dipartiment|cnr|department)', janela):
        return 'CREDITED', ('o nome aparece numa LISTA de %d nomes seguida de instituicao, '
                            'sem verbo de exposicao — e assinatura de trabalho, nao prova '
                            'de fala' % len(set(nomes)))
    return 'UNSPECIFIED', 'o nome aparece, e nada em volta diz se ele fala ou e citado'


def norm(s):
    s = unicodedata.normalize('NFD', str(s or '').lower())
    s = ''.join(c for c in s if unicodedata.category(c) != 'Mn')
    return re.sub(r'[‐-―]', '-', re.sub(r'\s+', ' ', s)).strip()


def so_inicial(nome):
    """`F. Quaglino` -> True. `Massimo Blandino` -> False."""
    return bool(re.match(r'^[a-z]\.?\s', norm(nome)))


def nome_no_texto(nome, texto):
    """Nome COMPLETO em sequencia. `mori` sozinho nao basta — a lei diz nome, nao token."""
    n = norm(nome)
    partes = [p for p in re.split(r'[^a-z]+', n) if len(p) > 1]

    # ⚠️ DEFEITO ACHADO PELA PROVA, E ELE TORNAVA UM RAMO INTEIRO CODIGO MORTO.
    # A primeira versao descartava toda parte de UMA letra. Com isso `F. Quaglino`
    # ficava com uma parte so, caia no `return False` e NUNCA chegava ao ramo que
    # limita inicial a PLAUSIBLE. O arquivo dizia, na propria docstring, que
    # inicial no maximo e plausivel — e na pratica reprovava sempre.
    #
    #     REGRA QUE NUNCA E ALCANCADA NAO E REGRA CONSERVADORA. E REGRA MORTA.
    #
    # Agora a inicial CASA (inicial + sobrenome em sequencia) e o teto de
    # PLAUSIBLE passa a ser aplicado de verdade, por `so_inicial`.
    iniciais = [p for p in re.split(r'[^a-z]+', n) if len(p) == 1]
    if len(partes) == 1 and iniciais:
        seq = re.escape(iniciais[0]) + r'[^a-z]{0,3}' + re.escape(partes[0])
        if re.search(r'(?<![a-z])%s(?![a-z])' % seq, texto):
            return True, 'inicial + sobrenome em sequencia'
        return False, 'inicial + sobrenome nao aparece em sequencia'

    if len(partes) < 2:
        return False, 'nome com menos de duas partes utilizaveis'
    seq = r'[^a-z]{0,3}'.join(re.escape(p) for p in partes)
    if re.search(r'(?<![a-z])%s(?![a-z])' % seq, texto):
        return True, 'nome completo em sequencia'
    # sobrenome + inicial do primeiro nome, na ordem invertida ("Moretti Antonio")
    inv = r'[^a-z]{0,3}'.join(re.escape(p) for p in reversed(partes))
    if re.search(r'(?<![a-z])%s(?![a-z])' % inv, texto):
        return True, 'nome completo em ordem invertida'
    return False, 'nome completo nao aparece em sequencia'


def julgar(cand):
    """A regra, sozinha numa funcao, para a prova chamar ELA e nao uma copia dela."""
    nome = cand.get('NAME') or ''
    inst = norm(cand.get('INSTITUTION') or '')
    texto = norm(' '.join(str(cand.get(k) or '') for k in
                          ('TITLE', 'DESCRIPTION', 'CHANNEL', 'SOURCE_ENTITY')))
    canal = norm(cand.get('CHANNEL') or '')

    base = {'CHANNEL_OWNERSHIP': 'NOT_CLAIMED',
            'CHANNEL_OWNERSHIP_POR_QUE': ('aparecer num video nao e ser dono do canal. '
                                          'A coleta ja registrou CHANNEL_KIND = '
                                          'INSTITUTIONAL_CHANNEL_FEATURING_PERSON_CANDIDATE.')}

    if not texto:
        return dict(base, CONTENT_RELEVANCE='NOT_KNOWN',
                    APPEARANCE_STATE='NOT_PROVED',
                    POR_QUE='o resultado nao trouxe texto para ler — falta de evidencia, '
                            'nao evidencia de ausencia', EVIDENCIA=[])

    fora = [f for f in FORA_DE_DOMINIO if casa(f, texto)]
    dom = [d for d in DOMINIO if casa(d, texto)]
    bate_nome, base_nome = nome_no_texto(nome, texto)
    bate_inst = bool(inst) and any(
        t in texto for t in [p for p in re.split(r'[^a-z]+', inst) if len(p) > 4])

    # ⚠️ O SEGUNDO EIXO. Ele responde OUTRA pergunta e nao desempata a primeira.
    rel = ('OUT_OF_DOMAIN' if fora and not dom else
           'TECHNICAL_DOMAIN' if dom else 'NOT_KNOWN')
    base = dict(base, CONTENT_RELEVANCE=rel,
                CONTENT_RELEVANCE_POR_QUE=(
                    'dominio: %s' % (', '.join(dom[:6]) if dom else 'nenhum termo tecnico')
                    + ('; fora: %s' % ', '.join(fora[:3]) if fora else '')),
                DOIS_EIXOS=('APPEARANCE_STATE fala da PESSOA; CONTENT_RELEVANCE fala do '
                            'VIDEO. Nao conseguir provar a pessoa nao torna o video '
                            'irrelevante — pode ser pista de fonte.'))

    base = dict(base, **dict(zip(('APPEARANCE_ROLE', 'APPEARANCE_ROLE_POR_QUE'),
                                 papel_na_aparicao(nome, cand.get('TITLE') or '',
                                                   cand.get('DESCRIPTION') or ''))))

    evid = []
    if bate_nome:
        evid.append({'EIXO': 'NOME', 'COMO': base_nome})
    if bate_inst:
        evid.append({'EIXO': 'INSTITUICAO', 'COMO': 'token da instituicao no texto'})
    if dom:
        evid.append({'EIXO': 'DOMINIO_TECNICO', 'COMO': ', '.join(dom[:6])})
    if fora:
        evid.append({'EIXO': 'FORA_DE_DOMINIO', 'COMO': ', '.join(fora[:4])})

    # ⚠️ NOME QUE NAO BATE ENCERRA O ASSUNTO. E' a lei herdada, literal.
    if not bate_nome:
        return dict(base, APPEARANCE_STATE='NOT_PROVED',
                    POR_QUE='o nome completo nao aparece no titulo, na descricao nem no '
                            'canal: %s' % base_nome, EVIDENCIA=evid)

    # O nome bate. Agora: ele bate DENTRO de nome de instituicao? "Don Nicola Mazza"
    # e um colegio homenageando OUTRO Nicola.
    # ⚠️ SE O NOME SO' EXISTE NO NOME DO CANAL, NAO E' APARICAO — TENHA DOMINIO OU NAO.
    # A primeira versao exigia `and not dom`, e por isso `Don NIcola Mazza` — um
    # colegio que homenageia OUTRO Nicola — saiu APPEARANCE_PROVED para Nicola Mori
    # assim que uma palavra de dominio apareceu na descricao. Nome dentro de nome de
    # instituicao e' homonimia, e homonimia nao melhora porque o assunto e' agricola.
    texto_sem_canal = norm(' '.join(str(cand.get(k) or '') for k in
                                    ('TITLE', 'DESCRIPTION')))
    if nome_no_texto(nome, canal)[0] and not nome_no_texto(nome, texto_sem_canal)[0]:
        return dict(base, APPEARANCE_STATE='NOT_PROVED',
                    POR_QUE='o nome so aparece no NOME DO CANAL, nunca no titulo nem na '
                            'descricao: e homonimia de instituicao, nao aparicao',
                    EVIDENCIA=evid)

    if fora and not dom:
        return dict(base, APPEARANCE_STATE='NOT_PROVED',
                    POR_QUE='o nome bate e o conteudo e de outro dominio (%s): '
                            'homonimo' % ', '.join(fora[:3]), EVIDENCIA=evid)

    # ⚠️ INICIAL NAO PROVA. O denominador de `F.` sao todos os nomes com F.
    if so_inicial(nome):
        return dict(base, APPEARANCE_STATE='APPEARANCE_PLAUSIBLE',
                    POR_QUE='o nome e INICIAL + sobrenome. Nenhuma corroboracao conserta '
                            'o denominador: `F.` sao todos os nomes que comecam com F.',
                    EVIDENCIA=evid)

    # Nome + corroboracao independente = PROVED. Nome sozinho = PLAUSIBLE.
    if bate_inst and dom:
        return dict(base, APPEARANCE_STATE='APPEARANCE_PROVED',
                    POR_QUE='nome completo, instituicao citada E dominio tecnico — tres '
                            'eixos independentes', EVIDENCIA=evid)
    if dom:
        return dict(base, APPEARANCE_STATE='APPEARANCE_PROVED',
                    POR_QUE='nome completo em sequencia E conteudo do dominio tecnico da '
                            'pessoa', EVIDENCIA=evid)
    return dict(base, APPEARANCE_STATE='APPEARANCE_PLAUSIBLE',
                POR_QUE='o nome bate e nada corrobora. A lei herdada: sem corroboracao '
                        'dos dois lados, PLAUSIBLE, nunca PROVED', EVIDENCIA=evid)


def _candidatos():
    import glob
    yt = []
    for p in sorted(glob.glob(os.path.join(PILOT, 'CANAIS-*.json'))):
        with open(p, encoding='utf-8') as f:
            for x in (json.load(f).get('ITEMS') or []):
                if x.get('SOURCE_PLATFORM') == 'YOUTUBE':
                    yt.append(x)
    return yt


def fase_julgar():
    import collections, datetime
    yt = _candidatos()
    if not yt:
        print('sem candidatos de YouTube em SENSOR-PILOT/CANAIS-*.json')
        return 1
    itens, por_estado, por_pais = [], collections.Counter(), collections.Counter()
    for c in yt:
        r = julgar(c)
        por_estado[r['APPEARANCE_STATE']] += 1
        if r['APPEARANCE_STATE'] != 'NOT_PROVED':
            por_pais[c.get('COUNTRY_OF_PERSON')] += 1
        itens.append({
            'PERSON_ID': c.get('PERSON_ID'), 'NAME': c.get('NAME'),
            'COUNTRY_OF_PERSON': c.get('COUNTRY_OF_PERSON'),
            'INSTITUTION': c.get('INSTITUTION'), 'CASE_ID': c.get('CASE_ID'),
            'VIDEO_ID': c.get('EXTERNAL_ID'), 'VIDEO_URL': c.get('SOURCE_URL'),
            'TITLE': c.get('TITLE'), 'CHANNEL': c.get('CHANNEL'),
            'CHANNEL_URL': c.get('CHANNEL_URL'),
            'PUBLISHED_AT': c.get('PUBLISHED_AT'), 'VIEWS': c.get('VIEWS'),
            'COLLECTION_RUN_ID': c.get('COLLECTION_RUN_ID'),
            'APIFY_ACTOR': c.get('APIFY_ACTOR'), **r})

    pessoas = {i['NAME'] for i in itens if i['APPEARANCE_STATE'] != 'NOT_PROVED'}
    os.makedirs(SAIDA, exist_ok=True)
    corpo = {
        'SOURCE_ID': 'YOUTUBE-APARICAO/APARICAO-EM-VIDEO',
        'source': 'derivado de SENSOR-PILOT/CANAIS-A e CANAIS-B, ja pagos — zero coleta nova',
        'SOURCE_LOCATION': 'derivado — interno', 'FACT_LOCATION': 'ver por item',
        'ORIGINAL_LANGUAGE': 'multi', 'EVIDENCE_CLASS': 'DERIVED_SCOPE',
        'captured_at': datetime.date.today().isoformat(),
        'CAPTURED_AT': datetime.datetime.now(
            datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
        'APIFY_RUNS': 0, 'COST_USD': 0, 'MISSION': MISSION,
        'O_QUE_ISTO_RESPONDE': 'este video mostra ESTA pessoa?',
        'O_QUE_ISTO_NAO_RESPONDE': ('de quem e o canal. APARECER NUM VIDEO NAO E SER DONO '
                                    'DO CANAL — CHANNEL_OWNERSHIP sai NOT_CLAIMED em 100%.'),
        'LEI_HERDADA': ('scripts/sensor_canal_identidade.py: "SEARCH_HIT != PERSON"; nome '
                        'que nao bate encerra o assunto, nome que bate nao prova sozinho, '
                        'e sem corroboracao dos dois lados o estado e PLAUSIBLE.'),
        'POR_QUE_ARQUIVO_NOVO': ('sensor_canal_identidade.py e da missao de sensores. A '
                                 'regra de isolamento proibe corrigir em silencio codigo '
                                 'de outra missao: a lei dele e obedecida e citada, e o '
                                 'arquivo dele nao foi tocado.'),
        'O_CASE_ID_NAO_E_PORTAO': (
            'Blandino entrou por IT-DURUM_WHEAT-FUSARIUM e aparece falando de MILHO. O '
            'recorte que achou a pessoa nao e o assunto da pessoa. Exigir o tema do '
            'CASE_ID reprovaria os acertos — medido.'),
        'A_INICIAL_NAO_IDENTIFICA': (
            '`F. Quaglino` devolveu concerto de orquestra, melanoma e psicologia '
            'junguiana. Nenhuma corroboracao conserta o denominador de uma inicial: no '
            'maximo PLAUSIBLE.'),
        'CANDIDATOS': len(itens),
        'BY_STATE': dict(por_estado),
        'TRES_EIXOS': ('APPEARANCE_STATE = e a pessoa? · CONTENT_RELEVANCE = o video e do '
                       'dominio? · APPEARANCE_ROLE = ela fala ou so e creditada? Tres '
                       'perguntas, tres campos, nenhum desempata o outro.'),
        'BY_ROLE': dict(collections.Counter(
            i['APPEARANCE_ROLE'] for i in itens if i['APPEARANCE_STATE'] != 'NOT_PROVED')),
        'APARICOES_POR_PAIS_DA_PESSOA': dict(por_pais),
        'PESSOAS_COM_ALGUMA_APARICAO': sorted(pessoas),
        'ITEMS': itens}
    with open(os.path.join(SAIDA, 'APARICAO-EM-VIDEO.json'), 'w', encoding='utf-8') as f:
        json.dump(corpo, f, ensure_ascii=False, indent=1)
    print('candidatos julgados: %d' % len(itens))
    for k, n in por_estado.most_common():
        print('   %-24s %s' % (k, n))
    print('pessoas com alguma aparicao: %d' % len(pessoas))
    print('gravado: data/samples/YOUTUBE-APARICAO/APARICAO-EM-VIDEO.json')
    return 0


def _testes():
    falhas = []

    def diz(cond, oq, det=''):
        print(('  OK   ' if cond else '  FALHA ') + oq + (' · ' + det if det else ''))
        if not cond:
            falhas.append(oq)

    # 1 · O RUIDO QUE ABRE O CORPUS: formatura em latim no canal de outra pessoa.
    r = julgar({'NAME': 'Massimo Blandino', 'INSTITUTION': 'University of Turin',
                'TITLE': 'LATINE LOQUI - Graduation in Latin language (master degree)',
                'CHANNEL': 'Gianluca Vindigni', 'DESCRIPTION': 'Durante la mia discussione di Laurea'})
    diz(r['APPEARANCE_STATE'] == 'NOT_PROVED', 'formatura em latim nao e aparicao', r['POR_QUE'][:52])

    # 2 · O ACERTO, E ELE E' SOBRE MILHO enquanto o CASE_ID diz trigo duro.
    r = julgar({'NAME': 'Massimo Blandino', 'INSTITUTION': 'University of Turin',
                'CASE_ID': 'IT-DURUM_WHEAT-FUSARIUM',
                'TITLE': 'Cambiamento Climatico - L intervento del Prof. Massimo Blandino',
                'CHANNEL': 'LEANDRO MAGGI', 'DESCRIPTION': 'semina del mais e agronomia'})
    diz(r['APPEARANCE_STATE'] == 'APPEARANCE_PROVED',
        'aparicao sobre MILHO passa mesmo com CASE_ID de trigo duro', r['APPEARANCE_STATE'])

    # 3 · A INICIAL nao pode ser provada NEM quando o nome aparece e o dominio bate.
    r = julgar({'NAME': 'F. Quaglino', 'INSTITUTION': 'University of Milan',
                'TITLE': 'F. Quaglino - la fitoplasmosi del mandorlo',
                'CHANNEL': 'UN EXPO PER TUTTI',
                'DESCRIPTION': 'agronomia e fitopatologia della vite'})
    diz(r['APPEARANCE_STATE'] == 'APPEARANCE_PLAUSIBLE',
        'inicial + sobrenome nunca vira PROVED', r['APPEARANCE_STATE'])

    # 4 · Nome DENTRO de nome de instituicao nao e a pessoa.
    r = julgar({'NAME': 'Nicola Mori', 'INSTITUTION': 'University of Verona',
                'TITLE': 'Il Magnifico Rettore ha inaugurato l anno accademico',
                'CHANNEL': 'Don Nicola Mazza', 'DESCRIPTION': 'collegio universitario'})
    diz(r['APPEARANCE_STATE'] == 'NOT_PROVED',
        'colegio Don Nicola Mazza nao e Nicola Mori', r['POR_QUE'][:52])

    # 5 · Homonimo em outro dominio cai, mesmo com nome completo.
    r = julgar({'NAME': 'Antonio Logrieco', 'INSTITUTION': 'CNR',
                'TITLE': 'Le imprese pugliesi: una situazione finanziaria complessa',
                'CHANNEL': 'Ria Grant Thornton', 'DESCRIPTION': 'analisi finanziaria'})
    diz(r['APPEARANCE_STATE'] == 'NOT_PROVED', 'financas nao e dominio agro', r['POR_QUE'][:52])

    # 6 · Ordem invertida do nome ("Moretti Antonio") continua sendo o nome.
    ok, como = nome_no_texto('Antonio Moretti', 'moretti antonio_novel integrated strategies')
    diz(ok and 'invertida' in como, 'nome em ordem invertida e reconhecido', como)

    # 7 · POSSE DE CANAL NUNCA E' AFIRMADA.
    r = julgar({'NAME': 'Nicola Mori', 'INSTITUTION': 'University of Verona',
                'TITLE': 'GF 2022 - Intervista sulle strategie di lotta allo Scaphoideus',
                'CHANNEL': 'Giornate Fitopatologiche', 'DESCRIPTION': 'difesa della vite'})
    diz(r['CHANNEL_OWNERSHIP'] == 'NOT_CLAIMED', 'posse de canal nunca e afirmada')

    # 8 · A LICAO QUE A PROVA ME DEU: sem o nome no texto, a PESSOA nao se prova —
    # e o VIDEO continua sendo do dominio. Duas perguntas, dois campos.
    diz(r['APPEARANCE_STATE'] == 'NOT_PROVED',
        'sem o nome no texto, a pessoa NAO se prova', r['APPEARANCE_STATE'])
    diz(r['CONTENT_RELEVANCE'] == 'TECHNICAL_DOMAIN',
        'e o mesmo video continua TECHNICAL_DOMAIN — pista de fonte',
        r['CONTENT_RELEVANCE'])

    # 9a · A COLISAO MEDIDA: seminario de sociologia nao e semeadura.
    diz(not casa('semin', 'seminario di sociologia all universita'),
        'seminario NAO casa com semin (semeadura)')
    diz(casa('semin', 'tempo di semina del mais'), 'semina casa com semin')
    diz(not casa('vite', 'les activites de la ferme'), 'activite NAO casa com vite')
    diz(not casa('riso', 'harrison farm'), 'harrison NAO casa com riso')

    # 9b · Nome so' no NOME DO CANAL nunca e aparicao, mesmo com dominio no texto.
    r3 = julgar({'NAME': 'Nicola Mori', 'INSTITUTION': 'University of Verona',
                 'TITLE': 'Il Magnifico Rettore ha inaugurato l anno accademico',
                 'CHANNEL': 'Don NIcola Mazza',
                 'DESCRIPTION': 'collegio universitario, visita in campo agricola'})
    diz(r3['APPEARANCE_STATE'] == 'NOT_PROVED',
        'nome so no nome do canal nao vira aparicao nem com dominio', r3['APPEARANCE_STATE'])

    # 9c · COAUTORIA NAO E FALA — o caso Moretti/Logrieco, texto real do corpus.
    pr, _ = papel_na_aparicao('Antonio Logrieco', 'Moretti Antonio_Novel integrated strategies',
        'Moretti Antonio, Logrieco Antonio, Institute of Sciences of Food Production, Bari, Italy')
    diz(pr == 'CREDITED', 'lista de autores vira CREDITED, nao SPEAKING', pr)
    pr, _ = papel_na_aparicao('Nicola Mori', 'GF 2022 - Intervista sulle strategie',
                              'Intervista a Nicola Mori sulle strategie di lotta')
    diz(pr == 'SPEAKING', '"Intervista a X" vira SPEAKING', pr)
    pr, _ = papel_na_aparicao('Massimo Blandino',
                              'Cambiamento Climatico - L intervento del Prof. Massimo Blandino', '')
    diz(pr == 'SPEAKING', 'nome no TITULO vira SPEAKING', pr)

    # 9d · UM NOME + VERBO DE EXPOSICAO E' PALESTRANTE — texto real do corpus.
    pr, _ = papel_na_aparicao('Nicola Mori', 'GF 2022 - Intervista sulle strategie',
        'Nicola Mori, Dip. di Biotecnologie - Universita di Verona, riporta i dati '
        'sull aumentata pericolosita dello Scaphoideus titanus, sottolineando l importanza')
    diz(pr == 'SPEAKING', 'um nome + instituicao + verbo de exposicao vira SPEAKING', pr)

    # 9 · E o inverso: dominio errado nao vira pista de fonte.
    r2 = julgar({'NAME': 'Antonio Logrieco', 'INSTITUTION': 'CNR',
                 'TITLE': 'Le imprese pugliesi: situazione finanziaria',
                 'CHANNEL': 'Ria Grant Thornton', 'DESCRIPTION': 'analisi finanziaria'})
    diz(r2['CONTENT_RELEVANCE'] == 'OUT_OF_DOMAIN',
        'financas sai OUT_OF_DOMAIN, nao NOT_KNOWN', r2['CONTENT_RELEVANCE'])

    print()
    print('FALHAS: %d' % len(falhas))
    return 1 if falhas else 0


if __name__ == '__main__':
    cmd = sys.argv[1] if len(sys.argv) > 1 else 'julgar'
    if cmd == 'julgar':
        raise SystemExit(fase_julgar())
    if cmd == 'teste':
        raise SystemExit(_testes())
    print('uso: youtube_aparicao.py {julgar|teste}')
    raise SystemExit(2)
