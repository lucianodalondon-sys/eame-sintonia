#!/usr/bin/env python3
"""
CREATOR CONTENT CORPUS — o acervo que responde POR QUE alguém é relevante.

    py scripts/creator_corpus.py                 # contrato, taxonomias, portões
    py scripts/creator_corpus.py universo        # fecha o universo nos 10 congelados

DOIS DONOS, UMA PESSOA
------------------------
O `CREATOR_MAP_EAME` continua **congelado** e continua dono de três coisas:
IDENTITY, ROLE e ACTIVATION_STATE. Nada aqui reabre discovery, muda os 8
`PERSON_CREATOR_ACTIVATION_READY`, muda os 2 `FARM_BUSINESS_PARTNER_READY`,
abre hub novo ou amplia país.

Este arquivo é dono de outra coisa: CONTENT MATERIALS, CONTENT OBSERVATIONS,
AUDIENCE SAMPLE e BRAND RELATIONSHIP EVIDENCE. `DATASET_OWNER` diferente,
diretório diferente, manifesto diferente. Dois donos para o mesmo campo é como
uma medição vira duas verdades — e foi por isso que a missão pediu a separação
antes de pedir o acervo.

A PERGUNTA MUDA, E POR ISSO A RÉGUA MUDA
------------------------------------------
O Creator Map perguntou *"quem existe e quem o Marketing pode avaliar?"*. Aqui
a pergunta é *"por que essa pessoa é relevante para a ADAMA naquele
COUNTRY × REGION × CROP?"*. Isso exige MATERIAL — e material tem armadilhas
próprias, que este arquivo executa como código e não como recomendação:

  1. **SEM SCORE ÚNICO.** Não existe `ADAMA_RELEVANCE_SCORE`. Existe um PERFIL
     com oito eixos medidos lado a lado (§7). Somar os oito produziria um número
     que esconde qual eixo está vazio — e o eixo vazio é a informação.

  2. **N=30 NÃO É RÉGUA.** É alvo de profundidade. `CONTENT_RATE_MIN_N` continua
     `PROPOSAL_ONLY` no congelamento. Chegar a 30 materiais NÃO autoriza publicar
     `FIELD_CONTENT_RATE` nem `TECHNICAL_CONTENT_RATE`. `taxa()` recusa.

  3. **ANTIGO PROVA HISTÓRICO, NUNCA ATIVIDADE.** As janelas 30/90/180/365 são
     separadas e nunca somadas em "atividade atual".

  4. **MENÇÃO != PARCERIA PAGA.** A escada de marca tem sete degraus (§8) e só
     sobe com evidência do degrau. `promover_marca()` recusa o salto.

  5. **NOT_OBSERVED != NO_RELATIONSHIP.** O corpus é uma amostra do que é
     público. `COMPETITOR_HISTORY` tem o estado `NOT_OBSERVED_IN_CORPUS`, com o
     escopo no nome, exatamente para que ninguém leia "não tem".

  6. **COMMENTER != FARMER.** Comentário é reação pública, não incidência de
     campo. `classificar_comentario()` não tem classe que promova comentarista a
     produtor.

  7. **LANGUAGE != COUNTRY. QUERY_CROP != PROVED_CROP.** E busca de país é por
     PALAVRA INTEIRA. A missão do corpus de pesquisador mediu o preço da busca
     por pedaço de string: 22 materiais foram para a Grécia porque a palavra
     encontrada era *secreted*; sobrou 1 depois da correção.

  8. **SEM ORDENAR POR SEGUIDOR.** Seguidores, views e likes são preservados
     como métrica pública. `FOLLOWERS DESC` não é sinônimo de valor, e esta casa
     já mediu conta de milhões com audiência errada.
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SAMPLES = os.path.join(ROOT, 'data', 'samples')
BASE = os.path.join(SAMPLES, 'CREATOR-CONTENT-CORPUS-EAME')
MAPA = os.path.join(SAMPLES, 'CREATOR-MAP-EAME')          # somente LEITURA

DATASET_OWNER = 'CREATOR_CONTENT_CORPUS_EAME'
MISSION = '15-CREATOR-CONTENT-CORPUS-EAME'
NAO_SEI = 'NÃO SEI'
NOT_KNOWN = 'NOT_KNOWN'

# O Creator Map é dono destes três campos. Nada aqui os escreve.
CAMPOS_DO_CREATOR_MAP = ('IDENTITY', 'ROLE', 'ACTIVATION_STATE',
                         'ACTIVATION_READY', 'CROP_PROOF', 'IDENTITY_EVIDENCE')

# ───────────────────────────────────────────── §2 · contrato do material
# Um campo que some do registro é indistinguível de um campo que nunca existiu.
CAMPOS_MATERIAL = [
    'CONTENT_ID', 'PERSON_ID', 'ENTITY_ID', 'PLATFORM', 'URL',
    'PUBLISHED_AT', 'FIRST_OBSERVED', 'LAST_OBSERVED',
    'TEXT', 'CAPTION', 'TITLE', 'MEDIA_TYPE',
    'PUBLIC_METRICS', 'RAW_REFERENCE', 'AS_OF_DATE',
    # derivados — sempre presentes, ainda que NOT_KNOWN
    'RECENCY_WINDOW', 'CONTENT_TYPES', 'COUNTRY_OF_FACT', 'REGION_OF_FACT',
    'CROP', 'ISSUE', 'PEST', 'DISEASE', 'WEED', 'SEASON', 'CROP_STAGE',
    'APPLICATION_TIMING', 'BRANDS_OBSERVED', 'BRAND_EVIDENCE_LEVEL',
    'TEXT_COMPLETENESS',
]

PLATAFORMAS = ('INSTAGRAM', 'YOUTUBE', 'TIKTOK', 'LINKEDIN', 'WEB', 'PODCAST')

# ───────────────────────────────────────────── §5 · tipos de material
# Um material pode ter MAIS DE UM tipo. Forçar tipo técnico onde o material é
# lifestyle é a forma mais rápida de inventar profundidade técnica.
TIPOS_DE_CONTEUDO = (
    'FIELD_ROUTINE', 'CROP_MANAGEMENT', 'TECHNICAL_EXPLANATION',
    'DISEASE_CONTENT', 'PEST_CONTENT', 'WEED_CONTENT', 'APPLICATION_CONTENT',
    'MACHINERY', 'HARVEST', 'PLANTING', 'IRRIGATION', 'NUTRITION',
    'CROP_PROTECTION', 'BIOLOGICALS', 'PRODUCT_MENTION', 'BRAND_MENTION',
    'FIELD_TRIAL', 'EVENT', 'FARM_BUSINESS', 'FARM_LIFESTYLE',
    'GENERAL_AG_AWARENESS', 'CONSUMER_FACING', 'ENTERTAINMENT',
    'SPONSORED_CONTENT', 'OTHER', 'NOT_KNOWN',
)

# Quais tipos contam como conteúdo de proteção de cultivos (§7-E). A lista é
# explícita porque "é agro" não prova "fala de defensivo" — a mesma lei que o
# Creator Map já executava para cultura.
TIPOS_CROP_PROTECTION = (
    'DISEASE_CONTENT', 'PEST_CONTENT', 'WEED_CONTENT', 'APPLICATION_CONTENT',
    'CROP_PROTECTION', 'BIOLOGICALS', 'FIELD_TRIAL',
)
TIPOS_TECNICOS = (
    'TECHNICAL_EXPLANATION', 'CROP_MANAGEMENT', 'FIELD_TRIAL',
) + TIPOS_CROP_PROTECTION
TIPOS_DE_CAMPO = ('FIELD_ROUTINE', 'HARVEST', 'PLANTING', 'IRRIGATION',
                  'APPLICATION_CONTENT', 'FIELD_TRIAL', 'CROP_MANAGEMENT')

# ───────────────────────────────────────────── §4 · janelas de recência
JANELAS = (30, 90, 180, 365)


def janela(dias):
    """A janela onde o material cai. Janelas SEPARADAS, nunca somadas.

    Material de 200 dias prova histórico. Não prova `CURRENT_ACTIVITY`, e por
    isso a função devolve a faixa e não um booleano de "ativo".
    """
    if dias is None or dias < 0:
        return NOT_KNOWN
    for d in JANELAS:
        if dias <= d:
            return 'LAST_%dD' % d
    return 'OLDER_THAN_365D'


# ───────────────────────────────────────────── §7 · eixos de relevância
# Oito eixos, medidos lado a lado. NUNCA somados num score.
EIXOS_DE_RELEVANCIA = {
    'A_CROP_ALIGNMENT': 'a pessoa realmente produz/trabalha/fala das culturas relevantes naquele país?',
    'B_REGION_ALIGNMENT': 'existe ligação real com região agrícola que importa para aquele crop?',
    'C_FARM_PROXIMITY': 'é produtor, está no campo, trabalha com produtores — ou é mídia/awareness?',
    'D_TECHNICAL_DEPTH': 'existe material técnico/agronômico?',
    'E_CROP_PROTECTION_RELEVANCE': 'há conteúdo de doença, praga, erva daninha, manejo, aplicação?',
    'F_AUDIENCE_FACING': 'o conteúdo parece dirigido a quem?',
    'G_ACTIVATION_STYLE': 'que tipo de ação essa pessoa sustenta publicamente?',
    'H_LOCAL_ADAMA_CONTEXT': 'o universo cultura/região dela tem contexto de portfólio ADAMA local provado?',
}
SCORE_PROIBIDO = {
    'NAME': 'ADAMA_RELEVANCE_SCORE',
    'STATUS': 'PROHIBITED_METRIC',
    'WHY': 'oito eixos somados viram um número que esconde qual eixo está vazio — '
           'e o eixo vazio é a informação que o Marketing precisa ver.',
}

AUDIENCIAS = ('FARMERS', 'AGRONOMISTS', 'TECHNICIANS', 'GENERAL_AG',
              'CONSUMERS', 'MIXED', 'NOT_KNOWN')
ESTILOS_DE_ATIVACAO = ('FIELD_CONTENT', 'TECHNICAL_EXPLANATION', 'PRODUCT_DEMO',
                       'EVENT', 'FARM_VISIT', 'INTERVIEW', 'AWARENESS',
                       'STORYTELLING', 'OTHER')
CONTEXTO_ADAMA_LOCAL = ('LOCAL_CONTEXT_OVERLAP_PROVED', 'PARTIAL', 'NOT_KNOWN')
CONTEXTO_ADAMA_NAO_SIGNIFICA = (
    'ADAMA deve usar esta pessoa',
    'produto X deve ser anunciado com ela',
)

# §14 — a pergunta muda quando a entidade é empresa.
USOS_FARM_BUSINESS = ('FIELD_VISIT', 'TECHNICAL_DEMO', 'CONTENT_PRODUCTION',
                      'CASE_STUDY', 'EVENT', 'FARMER_ACCESS',
                      'FIELD_TRIAL_CONTEXT', 'OTHER')
USOS_PESSOA = ('FIELD_CONTENT', 'TECHNICAL_EDUCATION', 'EVENT', 'FARM_VISIT',
               'STORYTELLING', 'PRODUCT_DEMO', 'GENERAL_AWARENESS', 'OTHER')

# ───────────────────────────────────────────── §8 · a escada de marca
# Sete degraus. A escada existe porque "a marca apareceu no vídeo" e "a marca
# pagou por este vídeo" são fatos diferentes que cabem na mesma frase solta.
ESCADA_DE_MARCA = (
    'BRAND_MENTION',                        # o nome apareceu
    'BRAND_PRODUCT_MENTION',                # um produto nomeado
    'BRAND_EVENT_APPEARANCE',               # a pessoa apareceu em evento da marca
    'BRAND_COLLABORATION_OBSERVED',         # há sinal de trabalho conjunto
    'PAID_PARTNERSHIP_PROVED',              # rótulo/declaração de pagamento
    'SPONSORED_CONTENT_PROVED',             # rótulo de conteúdo patrocinado
    'COMPETITOR_PRODUCT_ACTIVATION_PROVED',  # ativação de produto do concorrente
)
MARCAS_VIGIADAS = ('BAYER', 'SYNGENTA', 'BASF', 'CORTEVA', 'FMC', 'UPL',
                   'NUFARM', 'CERTIS BELCHIM', 'SEIPASA', 'ADAMA')
# Concorrente é todo mundo dessa lista MENOS a ADAMA.
CONCORRENTES = tuple(m for m in MARCAS_VIGIADAS if m != 'ADAMA')

HISTORICO_CONCORRENTE = ('OBSERVED', 'NOT_OBSERVED_IN_CORPUS', 'NOT_KNOWN')

# ───────────────────────────────────────────── §10 · comentários
CLASSES_DE_COMENTARIO = ('QUESTION', 'TECHNICAL_QUESTION',
                         'FIRST_PERSON_FIELD_REPORT', 'TECHNICAL_REPLY',
                         'OPINION', 'MARKETING', 'NOISE', 'OTHER')
COMENTARISTA_NAO_E = 'COMMENTER != FARMER — comentário é reação pública, não incidência de campo.'


# ───────────────────────────────────────────── portões executáveis
def promover_marca(degrau_atual, degrau_pedido, evidencia):
    """§8 · sobe a escada de marca SÓ com evidência do degrau pedido.

    Devolve (degrau, motivo). Sem evidência, o degrau não muda — e o motivo diz
    porquê, para que a recusa apareça no artefato em vez de sumir.
    """
    if degrau_pedido not in ESCADA_DE_MARCA:
        return degrau_atual, 'DEGRAU_INEXISTENTE: %s' % degrau_pedido
    if not evidencia:
        return (degrau_atual or ESCADA_DE_MARCA[0],
                'RECUSADO: %s exige evidência própria; menção não vira parceria paga'
                % degrau_pedido)
    atual = ESCADA_DE_MARCA.index(degrau_atual) if degrau_atual in ESCADA_DE_MARCA else -1
    pedido = ESCADA_DE_MARCA.index(degrau_pedido)
    if pedido <= atual:
        return degrau_atual, 'JÁ_ESTÁ_ACIMA'
    return degrau_pedido, 'EVIDÊNCIA_ACEITA: %s' % (evidencia[0] if isinstance(evidencia, list) else evidencia)


def taxa(nome, positivos, n):
    """§3 · recusa publicar taxa de conteúdo enquanto a régua não for arbitrada.

    Devolve sempre o N real e a contagem. NUNCA devolve a divisão: `N=30` é alvo
    de profundidade, e `CONTENT_RATE_MIN_N` continua `PROPOSAL_ONLY` no
    congelamento do piloto. Publicar `FIELD_CONTENT_RATE = 0,62` porque o corpus
    chegou a 30 seria transformar um alvo operacional em régua canônica sem que
    ninguém tivesse decidido isso.
    """
    return {
        'METRIC': nome,
        'STATE': 'WITHHELD_PENDING_ARBITRATION',
        'N_OBSERVED': n,
        'N_MATCHING': positivos,
        'WHY_WITHHELD': 'CONTENT_RATE_MIN_N=30 é PROPOSAL_ONLY no PILOT-FREEZE-STATE. '
                        'Chegar a 30 materiais não torna a taxa publicável.',
    }


def historico_de_concorrente(eventos):
    """§9 · estado do histórico competitivo, com o escopo dentro do nome.

    `NOT_OBSERVED_IN_CORPUS` diz o que foi olhado. `NOT_OBSERVED` sozinho seria
    lido como "não tem relação" — e o corpus é uma amostra do que é público.
    """
    if eventos:
        return 'OBSERVED'
    return 'NOT_OBSERVED_IN_CORPUS'


_PALAVRA = {}


def contem_palavra(texto, termo):
    """Busca por PALAVRA INTEIRA — nunca por pedaço de string.

    A missão do corpus de pesquisador mediu o preço do contrário: 22 materiais
    foram carimbados com `COUNTRY_OF_FACT = GR` porque a busca por "crete"
    encontrava *secreted*. Depois da correção, sobrou 1.
    """
    if not texto or not termo:
        return False
    rx = _PALAVRA.get(termo)
    if rx is None:
        rx = re.compile(r'(?<!\w)%s(?!\w)' % re.escape(termo), re.IGNORECASE)
        _PALAVRA[termo] = rx
    return bool(rx.search(texto))


def classificar_comentario(texto):
    """§10 · classe do comentário. Nenhuma classe promove comentarista a produtor."""
    t = (texto or '').strip()
    if not t:
        return 'NOISE'
    baixo = t.lower()
    tem_pergunta = '?' in t
    tecnico = any(contem_palavra(baixo, p) for p in
                  ('dose', 'dosis', 'fungicida', 'herbicida', 'insecticida',
                   'aplicación', 'aplicacion', 'aplicação', 'tratamiento',
                   'plaga', 'hongo', 'mildiu', 'repilo', 'septoria', 'maleza',
                   'variedad', 'siembra', 'traitement', 'fongicide', 'désherbage',
                   'trattamento', 'fungicida', 'diserbo', 'concime'))
    primeira_pessoa = any(contem_palavra(baixo, p) for p in
                          ('tengo', 'mi finca', 'mi parcela', 'mis olivos',
                           'chez moi', 'ma parcelle', 'nel mio campo', 'ho fatto'))
    if tem_pergunta and tecnico:
        return 'TECHNICAL_QUESTION'
    if tem_pergunta:
        return 'QUESTION'
    if primeira_pessoa:
        return 'FIRST_PERSON_FIELD_REPORT'
    if tecnico:
        return 'TECHNICAL_REPLY'
    if any(contem_palavra(baixo, p) for p in ('whatsapp', 'contacto', 'compra',
                                              'venta', 'promo', 'descuento')):
        return 'MARKETING'
    if len(t) <= 3:
        return 'NOISE'
    return 'OPINION'


def registro_vazio(**kw):
    """Todo material nasce com TODAS as chaves do contrato — nada some calado."""
    r = {c: NOT_KNOWN for c in CAMPOS_MATERIAL}
    r['CONTENT_TYPES'] = []
    r['BRANDS_OBSERVED'] = []
    r['PUBLIC_METRICS'] = {}
    r.update(kw)
    return r


def checar(registro):
    """Devolve a lista de defeitos do registro. Lista vazia = registro íntegro."""
    faltam = [c for c in CAMPOS_MATERIAL if c not in registro]
    defeitos = ['CAMPO_AUSENTE: %s' % c for c in faltam]
    if registro.get('PLATFORM') not in PLATAFORMAS + (NOT_KNOWN,):
        defeitos.append('PLATAFORMA_FORA_DO_CONTRATO: %s' % registro.get('PLATFORM'))
    for t in registro.get('CONTENT_TYPES') or []:
        if t not in TIPOS_DE_CONTEUDO:
            defeitos.append('TIPO_FORA_DA_TAXONOMIA: %s' % t)
    if registro.get('URL') in (None, '', NOT_KNOWN):
        defeitos.append('SEM_URL: material sem endereço não é evidência')
    return defeitos


def carregar(nome, base=None):
    caminho = os.path.join(base or BASE, nome)
    if not os.path.exists(caminho):
        return []
    with open(caminho, encoding='utf-8') as f:
        d = json.load(f)
    for chave in ('MATERIALS', 'ENTITIES', 'PROFILES', 'COMMENTS',
                  'OBSERVATIONS', 'BRAND_EVENTS', 'RUNS'):
        if isinstance(d, dict) and chave in d:
            return d[chave]
    return d


def gravar(nome, corpo):
    os.makedirs(BASE, exist_ok=True)
    corpo.setdefault('DATASET_OWNER', DATASET_OWNER)
    corpo.setdefault('SOURCE_ID', MISSION)
    with open(os.path.join(BASE, nome), 'w', encoding='utf-8') as f:
        json.dump(corpo, f, ensure_ascii=False, indent=2)
    print('gravado: data/samples/CREATOR-CONTENT-CORPUS-EAME/%s' % nome)


# ───────────────────────────────────────────── §1 · o universo fechado
def universo():
    """Lê o artefato CONGELADO e fecha o universo nos 10. Não resolve identidade.

    Identidade já está PROVED no Creator Map. Reabrir isso aqui criaria um
    segundo dono do campo — que é exatamente o que a missão proibiu. O que ESTA
    missão precisa saber é outra coisa: existe um CANAL COLETÁVEL? São perguntas
    diferentes, e uma delas tem um NÃO conhecido.

    Medido: `Gilles vk agriculteur du Loiret` está `ACTIVATION_READY` com
    identidade provada, mas o `PUBLIC_CHANNEL` registrado é uma URL de BUSCA do
    YouTube (`/results?search_query=`), não um canal. Buscar não é ter endereço.
    Coletar acervo a partir de uma página de resultados devolveria vídeos de
    quem o buscador quisesse — e o acervo sairia atribuído à pessoa errada. Ele
    entra como `CHANNEL_NOT_RESOLVED`: contado no universo, fora da coleta, com
    o motivo escrito.
    """
    caminho = os.path.join(MAPA, 'CREATOR-CAPABILITY-EAME.json')
    if not os.path.exists(caminho):
        print('ARTEFATO_CONGELADO_AUSENTE=%s' % caminho); raise SystemExit(1)
    with open(caminho, encoding='utf-8') as f:
        cap = json.load(f)

    vistos, ordem = {}, []
    for grupo in ('PERSON_CREATOR', 'FARM_BUSINESS'):
        for p in cap.get('LOOKUP_BY_ENTITY_TYPE', {}).get(grupo, []):
            if p.get('ACTIVATION_STATE') != 'ACTIVATION_READY':
                continue
            chave = (p.get('HANDLE') or p.get('CREATOR')).strip()
            if chave in vistos:
                continue
            vistos[chave] = p
            ordem.append(chave)

    entidades = []
    for i, chave in enumerate(ordem, 1):
        p = vistos[chave]
        tipo = p.get('ENTITY_TYPE')
        url = (p.get('PUBLIC_CHANNEL') or '').strip()
        plataforma, coletavel, motivo = _canal(url)
        eid = '%s-%02d' % ('PC' if tipo == 'PERSON_CREATOR' else 'FB', i)
        entidades.append({
            'ENTITY_ID': eid,
            'PERSON_ID': eid if tipo == 'PERSON_CREATOR' else NOT_KNOWN,
            'NAME': p.get('CREATOR'),
            'HANDLE': p.get('HANDLE'),
            'ENTITY_TYPE': tipo,
            'COUNTRY': p.get('COUNTRY'),
            'REGION': p.get('REGION'),
            'CROPS_PROVED': (p.get('CROP_PROOF') or {}).get('CROPS', []),
            'PUBLIC_CHANNEL': url or NOT_KNOWN,
            'PUBLIC_CONTACT': p.get('PUBLIC_CONTACT', NOT_KNOWN),
            'PLATFORM': plataforma,
            'CHANNEL_STATE': 'CHANNEL_RESOLVED' if coletavel else 'CHANNEL_NOT_RESOLVED',
            'COLLECTABLE': 'YES' if coletavel else 'NO',
            'WHY_NOT_COLLECTABLE': NOT_KNOWN if coletavel else motivo,
            'FROZEN_SOURCE': 'CREATOR-CAPABILITY-EAME.json',
            'INHERITED_READ_ONLY': list(CAMPOS_DO_CREATOR_MAP),
            'AS_OF_DATE': cap.get('CAPTURED_AT'),
        })

    pessoas = [e for e in entidades if e['ENTITY_TYPE'] == 'PERSON_CREATOR']
    fazendas = [e for e in entidades if e['ENTITY_TYPE'] == 'FARM_BUSINESS']
    coletaveis = [e for e in entidades if e['COLLECTABLE'] == 'YES']

    gravar('CORPUS-UNIVERSE.json', {
        'CAPTURED_AT': cap.get('CAPTURED_AT'),
        'QUESTION_ANSWERED': 'quais canais deste universo congelado têm endereço '
                             'público coletável — e quais não têm?',
        'WHAT_THIS_IS_NOT': 'não reabre discovery, não muda ACTIVATION_STATE, '
                            'não resolve identidade. Identidade é do CREATOR_MAP_EAME.',
        'FROZEN_INPUT': 'CREATOR-MAP-EAME/CREATOR-CAPABILITY-EAME.json',
        'PERSON_CREATOR_ATTEMPTED': len(pessoas),
        'FARM_BUSINESS_ATTEMPTED': len(fazendas),
        'CHANNELS_COLLECTABLE': len(coletaveis),
        'CHANNELS_NOT_RESOLVED': len(entidades) - len(coletaveis),
        'METRIC_LAW': 'a soma NUNCA se chama CREATORS_READY. Pessoa != empresa.',
        'ENTITIES': entidades,
    })
    print('PERSON_CREATOR_ATTEMPTED=%d' % len(pessoas))
    print('FARM_BUSINESS_ATTEMPTED=%d' % len(fazendas))
    print('CHANNELS_COLLECTABLE=%d' % len(coletaveis))
    for e in entidades:
        print('  %-6s %-9s %-34s %-9s %s' % (
            e['ENTITY_ID'], e['PLATFORM'], (e['HANDLE'] or '')[:34],
            e['COLLECTABLE'], e['WHY_NOT_COLLECTABLE'][:60]))
    return entidades


def _canal(url):
    """Plataforma e coletabilidade de um endereço público.

    Página de RESULTADO DE BUSCA não é canal. É a distinção entre "sei onde ela
    publica" e "sei como procurar por ela" — e só a primeira sustenta acervo.
    """
    u = (url or '').lower()
    if not u:
        return NOT_KNOWN, False, 'sem PUBLIC_CHANNEL no artefato congelado'
    if '/results?search_query=' in u or '/search?' in u:
        return ('YOUTUBE' if 'youtube' in u else NOT_KNOWN), False, (
            'o endereço registrado é uma BUSCA, não um canal. Coletar de uma '
            'página de resultados atribuiria à pessoa o que o buscador devolvesse.')
    if 'instagram.com' in u:
        return 'INSTAGRAM', True, NOT_KNOWN
    if 'youtube.com' in u and '/@' in u:
        return 'YOUTUBE', True, NOT_KNOWN
    if 'tiktok.com' in u:
        return 'TIKTOK', True, NOT_KNOWN
    if 'linkedin.com' in u:
        return 'LINKEDIN', True, NOT_KNOWN
    return NOT_KNOWN, False, 'endereço não reconhecido como canal de plataforma'


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'universo':
        universo(); raise SystemExit
    print('CREATOR CONTENT CORPUS — contrato e portões')
    print('DATASET_OWNER =', DATASET_OWNER)
    print('campos por material:', len(CAMPOS_MATERIAL))
    print('tipos de conteúdo:', len(TIPOS_DE_CONTEUDO))
    print('degraus da escada de marca:', len(ESCADA_DE_MARCA))
    print('eixos de relevância:', len(EIXOS_DE_RELEVANCIA), '— somados: NUNCA')
    print('métrica proibida:', SCORE_PROIBIDO['NAME'])
    print('janelas separadas:', JANELAS, '· antigo prova histórico, não atividade')
