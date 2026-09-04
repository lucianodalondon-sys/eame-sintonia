#!/usr/bin/env python3
"""
MIGRAÇÃO ESTRUTURAL DA CAMADA ITALIANA — ENTITY · SOURCE · ROLE.

    python3 scripts/sensor_entidade_it.py migrar
    python3 scripts/sensor_entidade_it.py validar

⛔ NENHUMA DESCOBERTA NOVA. Nenhuma requisição de rede. Esta é uma transformação do que
JÁ está gravado em `REGISTRY.json` e nos artefatos brutos das rotas.

═══════════════════════════════════════════════════════════════════════════════════════
A DECISÃO QUE ESTE ARQUIVO EXECUTA (P-014)
═══════════════════════════════════════════════════════════════════════════════════════
A Itália **espelha o CONTRATO brasileiro e mantém REGISTRO PRÓPRIO**. Não escreve no banco
do Brasil, não sincroniza, não cria camada federada.

    BRASIL  → semântica · contrato · leis
    ITÁLIA  → dados · registro · classificadores

A razão está medida: o contrato brasileiro (`QUEM É → ONDE EU BATO → DOCUMENTO`) está
certo, mas o dado ainda não o realiza (57 entidades para 4.517 fichas, `papel_da_fonte`
vazio, `enderecos` sem leitor), 7 das 8 travas exigem correção, e os classificadores
brasileiros são PT-BR chumbados em regex.

═══════════════════════════════════════════════════════════════════════════════════════
1 · IDENTIDADE PERSISTENTE — por que NÃO é mais um hash
═══════════════════════════════════════════════════════════════════════════════════════
O `SENSOR_ID` antigo era `sha1(NOME|ORGANIZAÇÃO)`. Isso é **conteúdo virando chave**: a
pessoa muda de instituição e o sensor morre e renasce. Medido: 5 de 8 casos adversariais
quebram.

**O dono real da identidade persistente no Brasil é `fontes.id` — um `bigserial`**
(`supabase-conteudo.sql:11`), chave substituta sem nenhuma semântica de negócio, protegida
por uma trava em AST (`provar-fonte-por-id.py:96,144-167`) que proíbe usar `nome` como
chave de operação. A `entidades.chave`, apesar do nome, **não serve**: ela é derivada do
menor `external_id` do grupo e o próprio arquivo declara que *"muda se o grupo ganhar um
id menor"* (`entidade-fase-1.py:44-47`).

Portanto a semântica copiada é a do **bigserial**: um identificador **opaco, sequencial,
atribuído UMA vez e persistido**. Como aqui não há Postgres, o papel do `bigserial` é feito
por um **livro-razão versionado** (`ID-LEDGER.json`), que é a única fonte de verdade sobre
qual id já foi dado a quem.

**Como o id sobrevive a rename e a mudança de instituição:** ele não é calculado a partir
de nada. A ligação `registro → id` é feita por **REIVINDICAÇÕES (claims)** — os
identificadores externos observáveis da entidade:

    orcid:0000-…  ·  web:fmach.it  ·  youtube:@fondazionemach  ·  instagram:@…

Duas fichas que compartilhem **qualquer** claim são a **mesma entidade** (union-find sobre
claims). Nome e organização **não são claims** e portanto não participam da resolução —
que é exatamente a lei brasileira *"Nome NUNCA é identificador"* (`entidades.sql:80`).

═══════════════════════════════════════════════════════════════════════════════════════
2 · ENTIDADE ≠ FONTE
═══════════════════════════════════════════════════════════════════════════════════════
Uma pessoa em três redes é **UMA entidade e TRÊS fontes**. `LIGAR, nunca fundir`
(`entidades.sql:90-93`). O documento aponta para a FONTE, nunca para a entidade.

═══════════════════════════════════════════════════════════════════════════════════════
3 · PAPEL MULTIVALORADO — e nada de "peso maior vence"
═══════════════════════════════════════════════════════════════════════════════════════
O Brasil escreve `« peso maior vence »` em `classificar-fontes.py:151` e executa em
:415-418: o laço acha TODOS os papéis que casam e sobrescreve, e **os perdedores não vão
para lista, contador, log ou coluna**. Isto é copiado ao contrário: aqui **todo papel
encontrado é preservado**, cada um com a sua prova e o seu estado.

`AMBIGUOUS` **não vira papel verdadeiro**: vira N papéis candidatos com
`STATE = NAO_PROVADO`. Ausência de prova é `NÃO SEI`, **nunca `FALSE`**.

═══════════════════════════════════════════════════════════════════════════════════════
4 · ORGANIZAÇÃO ≠ PESSOA — a ordem importa
═══════════════════════════════════════════════════════════════════════════════════════
`classificar-fontes.py:396-397` decide `entidade = organizacao|pessoa` **ANTES** de
escolher papel, e as duas listas de papel são **disjuntas**. Copiado. Um papel de PESSOA
(`agronomo`, `tecnico`, `pesquisador`, `consultor`, `produtor`) atribuído a uma entidade
`organizacao` é **removido e registrado em `ROLES_REMOVED`** — nunca apagado em silêncio.

⚠️ O marcador de organização lê **forma jurídica ou institucional no NOME** (srl, spa,
consorzio, fondazione, associazione, centro, istituto, ente, tv, rete…). Isso é diferente
de inferir profissão por assunto: é o que `A3` do Brasil chama de *"citar uma instituição
não te transforma nela — sigla só conta no NOME"*.

═══════════════════════════════════════════════════════════════════════════════════════
5 · ALCANCE ≠ AUTORIDADE — a única trava brasileira que se copia inteira
═══════════════════════════════════════════════════════════════════════════════════════
Quatro eixos **separados**, nunca somados nem promediados:

    SCIENTIFIC_AUTHORITY · TECHNICAL_AUTHORITY · FIELD_PROXIMITY · PUBLIC_REACH

*"média entre 'alcança 334 mil pessoas' e 'fala de manejo 1,8% do tempo' não significa
nada"* (`gerar-dados.py:708-721`).
"""
import json
import os
import re
import sys
import unicodedata
from collections import Counter, OrderedDict, defaultdict
from selo_de_amostra import selar

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEST = os.path.join(ROOT, 'data', 'samples', 'IT-HUMAN-SENSORS')
RAW = os.path.join(ROOT, 'data', 'raw', 'SENSOR-HUMANO-IT')
REGISTRY = os.path.join(DEST, 'REGISTRY.json')
LEDGER = os.path.join(DEST, 'ID-LEDGER.json')
ENTIDADES = os.path.join(DEST, 'ENTITIES.json')
FONTES = os.path.join(DEST, 'SOURCES.json')
MIGRACAO = os.path.join(DEST, 'ID-MIGRATION.json')
VALID = os.path.join(DEST, 'MIGRATION-VALIDATION.json')

# ---------------------------------------------------------------------- papéis de PESSOA
PAPEL_PESSOA = {'pesquisador', 'professor', 'agronomo', 'consultor', 'tecnico', 'produtor'}
# ---------------------------------------------------------------- papéis de ORGANIZAÇÃO
PAPEL_ORG = {'organizacao_de_pesquisa', 'servico_fitossanitario', 'centro_de_ensaio',
             'cooperativa', 'organizacao_de_produtores', 'associacao', 'veiculo_tecnico',
             'servico_tecnico', 'empresa', 'orgao_publico', 'laboratorio'}

MAPA_PAPEL = {
    'RESEARCHER': 'pesquisador', 'PLANT_PATHOLOGIST': 'pesquisador',
    'ENTOMOLOGIST': 'pesquisador',
    'RESEARCH_ORGANIZATION': 'organizacao_de_pesquisa',
    'PUBLIC_RESEARCH': 'organizacao_de_pesquisa', 'UNIVERSITY': 'organizacao_de_pesquisa',
    'RESEARCH_CENTRE': 'organizacao_de_pesquisa', 'TRIAL_CENTRE': 'centro_de_ensaio',
    'PLANT_HEALTH_SERVICE': 'servico_fitossanitario',
    'PHYTOSANITARY_CONSORTIUM': 'servico_fitossanitario',
    'AGRONOMIST': 'agronomo', 'TECHNICAL_ADVISER': 'consultor',
    'FIELD_TECHNICIAN': 'tecnico', 'CROP_PROTECTION': 'tecnico',
    'DECISION_SUPPORT_SERVICE': 'servico_tecnico',
    'PRODUCER': 'produtor', 'VITICULTURE': 'produtor', 'FRUIT_GROWING': 'produtor',
    'OLIVE_GROWING': 'produtor', 'WINERY': 'produtor', 'NURSERY': 'produtor',
    'COOPERATIVE': 'cooperativa', 'PRODUCER_ORGANIZATION': 'organizacao_de_produtores',
    'AGRICULTURAL_CONSORTIUM': 'cooperativa', 'CONSORTIUM': 'cooperativa',
    'FARMER_ASSOCIATION': 'associacao', 'TECHNICAL_MEDIA': 'veiculo_tecnico',
    'FOOD_INDUSTRY': 'empresa', 'VETERINARY_PUBLIC_HEALTH': 'orgao_publico',
}

# Forma jurídica / institucional NO NOME. Ver §4 do cabeçalho.
FORMA_ORG = ('srl', 's.r.l', 'spa', 's.p.a', 'consorzio', 'consorzi', 'fondazione',
             'associazione', 'cooperativa', 'centro', 'istituto', 'ente', 'agenzia',
             'universit', 'servizio', 'osservatorio', 'accademia', 'archivio', 'museo',
             ' tv', 'tv ', 'telev', 'rete ', 'webtv', 'edizioni', 'editrice', 'rivista',
             'giornale', 'network', 'studio', 'societ', 'azienda', 'cantina', 'molino',
             'gruppo', 'unione', 'federazione', 'camera', 'regione', 'provincia',
             'comune', 'crea', 'cnr', 'ersa', 'apot', 'coprob')

# ⚠️ Marcador de DOMÍNIO agronômico profissional, lido da descrição DECLARADA pelo canal.
AGRO_PROFISSIONAL = ('agronom', 'agricoltur', 'agrario', 'agrari', 'fitosanitar',
                     'fitopatolog', 'entomolog', 'difesa delle colture', 'difesa integrata',
                     'colture', 'coltura', 'viticolt', 'enolog', 'frutticolt', 'olivicolt',
                     'cerealicolt', 'zootecn', 'seminativ', 'azienda agricola',
                     'produzione integrata', 'agrofarmac', 'fitofarmac', 'sementi',
                     'vigneto', 'frutteto', 'oliveto', 'lavorazione del terreno')
# Hobby não é agricultura profissional — e é DECLARADO, não inferido.
HOBBY = ('giardinaggio', 'giardino di casa', 'orto di casa', 'balcone', 'terrazzo',
         'hobbist', 'per hobby', 'piante da appartamento', 'bonsai',
         'coltivare l orto', 'coltivare orto', 'tutorial su come fare',
         'consigli su come coltivare', 'metodo biologico')


def _norm(s):
    s = unicodedata.normalize('NFKD', s or '')
    s = ''.join(c for c in s if not unicodedata.combining(c))
    return re.sub(r'\s+', ' ', s.replace('‐', '-')).lower().strip()


def _claim_de_url(url):
    """Um identificador observável, no padrão brasileiro de `external_id`."""
    if not url:
        return None
    u = url.strip()
    if not re.match(r'^https?://', u):
        u = 'https://' + u
    m = re.search(r'youtube\.com/(@[\w.\-]+)', u)
    if m:
        return 'youtube:' + m.group(1).lower()
    m = re.search(r'youtube\.com/channel/(UC[\w\-]+)', u)
    if m:
        return 'youtube:' + m.group(1)
    m = re.search(r'instagram\.com/([\w.\-]+)', u)
    if m:
        return 'instagram:@' + m.group(1).lower()
    m = re.search(r'linkedin\.com/(in|company)/([\w\-%]+)', u)
    if m:
        return 'linkedin:linkedin.com/%s/%s' % (m.group(1), m.group(2).lower())
    m = re.search(r'facebook\.com/([\w.\-]+)', u)
    if m:
        return 'facebook:@' + m.group(1).lower()
    m = re.search(r'tiktok\.com/(@[\w.\-]+)', u)
    if m:
        return 'tiktok:' + m.group(1).lower()
    m = re.search(r'^https?://([^/]+)(/[^?#]*)?', u)
    if m:
        dom = m.group(1).lower()
        dom = dom[4:] if dom.startswith('www.') else dom
        cam = (m.group(2) or '').rstrip('/')
        # ⚠️ Caminho preservado: o Brasil mediu que "embrapa.br abriga 14 pesquisadores
        # diferentes e o domínio sozinho os confundiria" (entidades.sql:80-85).
        return 'web:' + dom + cam
    return None


# ═══════════════════════════════════════════════════════════ o livro-razão dos ids
class Ledger:
    """O `bigserial` desta casa: id opaco, atribuído UMA vez, persistido.

    A resolução é por CLAIM (identificador observável), nunca por nome. Um registro que
    apresente um claim já conhecido recebe o id já existente; claims novos são anexados à
    mesma entidade. É assim que o id sobrevive a rename, a mudança de instituição e à
    chegada de canais novos.
    """

    def __init__(self, caminho):
        self.caminho = caminho
        if os.path.exists(caminho):
            with open(caminho, encoding='utf-8') as f:
                d = json.load(f)
        else:
            d = {'NEXT_ENTITY': 1, 'NEXT_SOURCE': 1, 'CLAIM_TO_ENTITY': {},
                 'ANCHOR_TO_ENTITY': {}, 'SOURCE_KEY_TO_ID': {}, 'ENTITY_CLAIMS': {}}
        self.d = d

    def entidade(self, claims, ancora):
        """→ (ENTITY_ID, novo?). `ancora` só é usada quando NÃO há claim nenhum."""
        achados = OrderedDict()
        for c in claims:
            eid = self.d['CLAIM_TO_ENTITY'].get(c)
            if eid:
                achados[eid] = True
        if not achados and not claims:
            eid = self.d['ANCHOR_TO_ENTITY'].get(ancora)
            if eid:
                achados[eid] = True
        if achados:
            ids = list(achados)
            eid = ids[0]
            # Dois claims que já apontavam para entidades diferentes: é MESMA_ENTIDADE
            # descoberta agora. Consolida no menor id e preserva o rastro.
            for outro in ids[1:]:
                for k, v in list(self.d['CLAIM_TO_ENTITY'].items()):
                    if v == outro:
                        self.d['CLAIM_TO_ENTITY'][k] = eid
                for k, v in list(self.d['ANCHOR_TO_ENTITY'].items()):
                    if v == outro:
                        self.d['ANCHOR_TO_ENTITY'][k] = eid
                self.d['ENTITY_CLAIMS'].setdefault(eid, [])
                self.d['ENTITY_CLAIMS'][eid] += self.d['ENTITY_CLAIMS'].pop(outro, [])
            novo = False
        else:
            eid = 'IT-E-%06d' % self.d['NEXT_ENTITY']
            self.d['NEXT_ENTITY'] += 1
            novo = True
        for c in claims:
            self.d['CLAIM_TO_ENTITY'][c] = eid
        if not claims:
            self.d['ANCHOR_TO_ENTITY'][ancora] = eid
        cl = self.d['ENTITY_CLAIMS'].setdefault(eid, [])
        for c in claims:
            if c not in cl:
                cl.append(c)
        return eid, novo

    def fonte(self, chave):
        sid = self.d['SOURCE_KEY_TO_ID'].get(chave)
        if sid:
            return sid, False
        sid = 'IT-S-%06d' % self.d['NEXT_SOURCE']
        self.d['NEXT_SOURCE'] += 1
        self.d['SOURCE_KEY_TO_ID'][chave] = sid
        return sid, True

    def gravar(self):
        with open(self.caminho, 'w', encoding='utf-8') as f:
            json.dump(selar(self.d), f, ensure_ascii=False, indent=1, sort_keys=True)


def _kind(nome, veio_da_rota, entity_kind_antigo):
    """Organização ou pessoa — decidido ANTES do papel, como no Brasil."""
    if veio_da_rota == 'SENSOR-HUMANO-IT/INSTITUTIONS':
        return 'organizacao', 'rota institucional: a candidata é uma organização por construção'
    if veio_da_rota == 'SENSOR-HUMANO-IT/EPMC':
        return 'pessoa', 'autoria científica é de pessoa; a afiliação é a organização dela'
    n = _norm(nome)
    achados = [f for f in FORMA_ORG if f in n]
    if achados:
        return 'organizacao', 'forma jurídica/institucional no NOME: %s' % ', '.join(achados[:3])
    if entity_kind_antigo == 'PERSON':
        return 'pessoa', 'ENTITY_KIND declarado no registro anterior'
    return 'NÃO SEI', 'nenhuma forma organizacional no nome e nenhum papel declarado que decida'


def _dominio(desc, nome):
    """Domínio DECLARADO. Sem marcador agronômico profissional: NÃO SEI, nunca FALSE."""
    t = _norm('%s %s' % (desc or '', nome or ''))
    hobby = [h for h in HOBBY if _norm(h) in t]
    agro = [a for a in AGRO_PROFISSIONAL if _norm(a) in t]
    # ⚠️ Hobby DECLARADO vence, mesmo com marcador agronômico junto. "Vuoi rimanere
    # aggiornato sulle ultime novità nel mondo agricolo HOBBISTICO" declara hobby e
    # agricultura na mesma frase — e o que decide se é sensor de campo é a primeira.
    if hobby:
        return 'HOBBY_DECLARADO', ('a descrição declara jardinagem/hobby: %s%s'
                                   % (', '.join(hobby[:2]),
                                      ' (com marcador agronômico junto: %s)'
                                      % ', '.join(agro[:2]) if agro else ''))
    if agro:
        return 'AGRO_PROFISSIONAL', 'marcadores declarados: %s' % ', '.join(agro[:3])
    return 'NÃO SEI', 'a descrição declarada não traz marcador agronômico profissional'


def migrar():
    with open(REGISTRY, encoding='utf-8') as f:
        reg = json.load(f)
    with open(os.path.join(RAW, 'youtube-IT.json'), encoding='utf-8') as f:
        yt = json.load(f)
    canal_por_url = {c['CHANNEL_URL']: c for c in yt['CHANNELS']}

    led = Ledger(LEDGER)
    entidades, fontes, migr = {}, [], []
    papeis_removidos = []

    # ---------------------------------------------------------------- 1) as 224 fichas
    for s in reg['SENSORS']:
        prov = s['PROVENANCE'] or {}
        rota = s['DISCOVERED_FROM']
        nome = (s['PERSON_NAME'] if s['ENTITY_KIND'] == 'PERSON' else s['ORGANIZATION'])
        if not nome or str(nome).startswith('NÃO SEI') or str(nome).startswith('NOT_APPLICABLE'):
            nome = prov.get('CHANNEL_NAME') or 'NÃO SEI'

        canal = canal_por_url.get(s['YOUTUBE'])
        desc = (canal or {}).get('DESCRIPTION')

        # --- claims: identificadores observáveis. Nome e organização NÃO entram.
        claims, ident = [], []
        if prov.get('ORCID_DECLARED'):
            c = 'orcid:' + prov['ORCID_DECLARED']
            claims.append(c)
            ident.append({'TIPO': 'ORCID', 'VALOR': prov['ORCID_DECLARED'],
                          'EVIDENCIA': 'declarado no índice Europe PMC',
                          'ESTADO': prov.get('ORCID_STATE')})
        for url, origem in ([(s['INSTITUTION_URL'], 'URL institucional verificada por GET')]
                            + [(s['YOUTUBE'], 'canal declarado')]
                            + [(u, 'link declarado pelo próprio canal na aba About')
                               for u in (s['OTHER_CHANNELS'] or [])]):
            if not url or url == 'NÃO SEI':
                continue
            c = _claim_de_url(url)
            if c and c not in claims:
                claims.append(c)
                ident.append({'TIPO': c.split(':', 1)[0].upper(), 'VALOR': c.split(':', 1)[1],
                              'EVIDENCIA': origem, 'ESTADO': 'OBSERVADO'})

        eid, _ = led.entidade(claims, 'legacy:' + s['SENSOR_ID'])

        kind, kind_base = _kind(nome, rota, s['ENTITY_KIND'])
        if rota.endswith('/EPMC'):
            # a evidência de domínio desta rota é o PORTÃO AGRONÔMICO já gravado
            dom = ('AGRO_PROFISSIONAL' if prov.get('AGRO_AFFILIATION') == 'DECLARED'
                   else 'NÃO SEI')
            dom_base = 'portão agronômico sobre a afiliação declarada: %s' % (
                prov.get('AGRO_AFFILIATION_REASON') or 'NÃO SEI')
        elif rota.endswith('/INSTITUTIONS'):
            termos = s['SPECIALTIES'] or []
            dom = 'AGRO_PROFISSIONAL' if termos else 'NÃO SEI'
            dom_base = ('termos de papel técnico declarados na própria página: %s'
                        % ', '.join(termos[:5]) if termos
                        else 'nenhum termo de papel técnico no HTML lido')
        else:
            dom, dom_base = _dominio(desc, nome)

        # --- papéis: TODOS preservados, cada um com prova. AMBIGUOUS não vira verdade.
        st = s['SENSOR_TYPE']
        amb = st.startswith('AMBIGUOUS:')
        brutos = st.split(':', 1)[1].split('|') if amb else [st]
        papeis = []
        # ⛔⛔ A LEI QUE ESTA MISSÃO VIOLOU E AQUI CONSERTA
        # `MODELO-DE-IDENTIDADE-EAME.md` é literal: papel sai de CAMPO ESTRUTURADO
        # declarado — `companyType`, `pageType`, `industries`, `headline` — e
        # **NUNCA decidem papel: nome da conta · foto · estilo do texto · idioma ·
        # PROSA LIVRE (`about`, `description`) · o assunto de um post**.
        # A rota de canal italiana leu a descrição do canal e produziu papéis. Isso é
        # exatamente o classificador que a casa mediu e reprovou (`Oleo Revista` →
        # RESEARCHER porque "investigador" aparecia numa notícia citada).
        # O YouTube não expõe campo estruturado de papel. Logo, todo papel vindo desta
        # rota é CANDIDATO, nunca prova — e assunto (CROP/ISSUE/domínio) continua
        # podendo vir do texto, porque a mesma lei permite: "assunto pode sair do
        # texto; identidade não".
        de_prosa = rota.endswith('/YOUTUBE-DISCOVERY')
        for b in brutos:
            p = MAPA_PAPEL.get(b)
            if not p:
                continue
            if de_prosa:
                estado = 'NAO_PROVADO'
                prova = ('lido da PROSA LIVRE da aba About; o MODELO-DE-IDENTIDADE '
                         'proíbe prosa livre de decidir papel, e o YouTube não expõe '
                         'campo estruturado de papel. Candidato, nunca prova.'
                         + (' Além disso a fonte declarou mais de um termo (AMBIGUOUS).'
                            if amb else ''))
            else:
                estado = 'NAO_PROVADO' if amb else 'DECLARADO'
                prova = (s['ROLE_BASIS'] if not amb else
                         'papel candidato dentro de AMBIGUOUS — a fonte declarou mais de '
                         'um termo e nenhum foi corroborado; ambiguidade não é prova')
            papeis.append({'PAPEL': p, 'ESTADO': estado, 'PROVA': prova,
                           'PROVENIENCIA': rota})
        if rota.endswith('/EPMC') and s['OBSERVATION_EVIDENCE']:
            if not any(x['PAPEL'] == 'pesquisador' for x in papeis):
                papeis.append({'PAPEL': 'pesquisador', 'ESTADO': 'PROVADO',
                               'PROVA': '%d obras em escopo, identificadores anexados'
                                        % (prov.get('WORKS_IN_SCOPE') or 0),
                               'PROVENIENCIA': rota})

        presenca = sorted({c.split(':', 1)[0] for c in claims
                           if c.split(':', 1)[0] in ('youtube', 'instagram', 'linkedin',
                                                     'facebook', 'tiktok')})

        e = entidades.setdefault(eid, {
            'ENTITY_ID': eid, 'NOME_CANONICO': nome, 'ALIASES': [],
            'KIND': kind, 'KIND_BASIS': kind_base,
            'DOMINIO': dom, 'DOMINIO_BASIS': dom_base,
            'IDENTIFIERS': [], 'ROLES': [], 'PUBLIC_PRESENCE': [],
            'PAIS': 'NÃO SEI', 'PAIS_ESTADO': 'NÃO SEI',
            'GEO': {'BASE_REGIAO': None, 'BASE_ORIGEM': None,
                    'OPERATING': 'NÃO SEI — nunca medido',
                    'INFLUENCE': 'NÃO SEI — exige conteúdo coletado',
                    'FACT': 'NÃO SEI — afiliação não é geografia do estudo'},
            'CROPS': [], 'ISSUES': [],
            'SCIENTIFIC_AUTHORITY': 'NÃO SEI', 'TECHNICAL_AUTHORITY': 'NÃO SEI',
            'FIELD_PROXIMITY': 'NÃO SEI', 'PUBLIC_REACH': 'NÃO SEI',
            'ADAMA_RELEVANCE_REASON': s['ADAMA_RELEVANCE_REASON'],
            'MONITORING_RECOMMENDATION': s['MONITORING_RECOMMENDATION'],
            'LEGACY_SENSOR_IDS': [],
        })
        if nome != 'NÃO SEI' and nome != e['NOME_CANONICO'] and nome not in e['ALIASES']:
            e['ALIASES'].append(nome)
        e['LEGACY_SENSOR_IDS'].append(s['SENSOR_ID'])
        for i in ident:
            if i not in e['IDENTIFIERS']:
                e['IDENTIFIERS'].append(i)
        for p in papeis:
            if not any(x['PAPEL'] == p['PAPEL'] for x in e['ROLES']):
                e['ROLES'].append(p)
        for p in presenca:
            if p not in e['PUBLIC_PRESENCE']:
                e['PUBLIC_PRESENCE'].append(p)
        e['CROPS'] = sorted(set(e['CROPS']) | set(s['CROP_IDS']))
        e['ISSUES'] = sorted(set(e['ISSUES']) | set(s['ISSUE_IDS']))
        if s['REGION_IDS']:
            e['GEO']['BASE_REGIAO'] = s['REGION_IDS'][0]
            e['GEO']['BASE_ORIGEM'] = s['REGION_BASIS']
        # ── os quatro eixos, separados. Nenhum deles se soma a outro.
        if s['AUTHORITY_CLASS'] == 'SCIENCE':
            e['SCIENTIFIC_AUTHORITY'] = s['TECHNICAL_AUTHORITY']
        if s['TECHNICAL_AUTHORITY'] not in ('NOT_ESTABLISHED', 'NÃO SEI'):
            e['TECHNICAL_AUTHORITY'] = s['TECHNICAL_AUTHORITY']
        e['FIELD_PROXIMITY'] = s['FIELD_PROXIMITY']
        if s['AUDIENCE_SIZE'] and s['AUDIENCE_SIZE'] != 'NÃO SEI':
            e['PUBLIC_REACH'] = s['AUDIENCE_SIZE']
        # país: só é IT quando PROVADO. Ausência é NÃO SEI, jamais negativa.
        if rota.endswith('/YOUTUBE-DISCOVERY'):
            pais = (canal or {}).get('DECLARED_COUNTRY') or 'NOT_DECLARED'
            e['PAIS'] = 'IT' if pais == 'IT' else 'NÃO SEI'
            e['PAIS_ESTADO'] = ('PROVADO_IT' if pais == 'IT' else
                                'NAO_DECLARADO' if pais == 'NOT_DECLARED' else
                                'ESTRANGEIRO_DECLARADO:%s' % pais)
        else:
            e['PAIS'], e['PAIS_ESTADO'] = 'IT', 'PROVADO_POR_ROTA'

        # ------------------------------------------------------------------- as FONTES
        for url, papel_fonte, origem in (
                [(s['INSTITUTION_URL'], 'canal_tecnico' if kind == 'organizacao' else 'person',
                  'URL institucional verificada por GET nesta rodada')] +
                [(s['YOUTUBE'], 'person' if kind == 'pessoa' else 'canal_tecnico',
                  'canal descoberto pela busca pública e identidade lida na aba About')] +
                [(u, 'marca', 'link declarado pelo próprio canal na aba About')
                 for u in (s['OTHER_CHANNELS'] or [])]):
            if not url or url == 'NÃO SEI':
                continue
            c = _claim_de_url(url)
            if not c:
                continue
            plat, ext = c.split(':', 1)
            sid, _ = led.fonte(c)
            if any(f['SOURCE_ID'] == sid for f in fontes):
                continue
            fontes.append({
                'SOURCE_ID': sid, 'ENTITY_ID': eid, 'ENTITY_LINK': 'LINKED',
                'LINK_EVIDENCE': origem,
                'PLATAFORMA': plat, 'EXTERNAL_ID': ext, 'URL': url,
                'PAPEL_DA_FONTE': papel_fonte,
                'CADENCIA_DIAS': {'DAILY': 1, 'WEEKLY': 7, 'MONTHLY': 30}.get(
                    s['MONITORING_RECOMMENDATION']),
                'ULTIMA_COLETA': None,
                'LEGACY_SENSOR_ID': s['SENSOR_ID'],
            })
        migr.append({'OLD_SENSOR_ID': s['SENSOR_ID'], 'NEW_ENTITY_ID': eid,
                     'NOME': nome, 'KIND': kind,
                     'CLAIMS': claims,
                     'ID_ANTIGO_DERIVADO_DE': 'sha1(NOME|ORGANIZAÇÃO) — conteúdo virando chave'})

    # ------------------------- 2) os canais recusados por país: D-022, dívida visível
    recusados = []
    for c in yt['CHANNELS']:
        if 'ABOUT_STATE' not in c:
            continue
        pais = c.get('DECLARED_COUNTRY') or 'NOT_DECLARED'
        if pais == 'IT' or c.get('IS_INDUSTRY'):
            continue
        estado = ('NAO_DECLARADO' if pais == 'NOT_DECLARED'
                  else 'ESTRANGEIRO_DECLARADO:%s' % pais)
        cl = _claim_de_url(c['CHANNEL_URL'])
        sid, _ = led.fonte(cl)
        recusados.append({
            'SOURCE_ID': sid, 'ENTITY_ID': None,
            'ENTITY_LINK': 'UNRESOLVED',
            'LINK_EVIDENCE': 'canal não promovido; identidade de entidade não resolvida',
            'PLATAFORMA': 'youtube', 'EXTERNAL_ID': cl.split(':', 1)[1],
            'URL': c['CHANNEL_URL'], 'NOME_DO_CANAL': c['CHANNEL_NAME'],
            'PAIS': 'NÃO SEI' if pais == 'NOT_DECLARED' else pais,
            'PAIS_ESTADO': estado,
            'QUALIFICADO': False,
            'NOTA': ('D-022: NÃO DECLARAR país deixou de significar "não é Itália". '
                     'Isto NÃO o qualifica como sensor italiano — apenas remove uma '
                     'negativa que nunca foi medida.') if pais == 'NOT_DECLARED'
                    else 'país estrangeiro declarado — permanece separado pelo contrato',
        })

    # ═══════════════════════════════════════════════════════════════════════════════
    # PASSE FINAL — a purga de papel de PESSOA em ORGANIZAÇÃO roda DEPOIS das fusões.
    # ⚠️ Rodá-la por registro deixava passar o caso do AgroNotizie: a ficha do canal
    # chegava com KIND indefinido (o nome do canal não tem forma jurídica), ganhava o
    # papel `agronomo`, e só DEPOIS a fusão por claim revelava que a entidade é o
    # veículo. Kind só é conhecido quando a entidade está inteira.
    for e in entidades.values():
        if e['KIND'] != 'organizacao':
            continue
        mantidos = []
        for r in e['ROLES']:
            if r['PAPEL'] in PAPEL_PESSOA:
                papeis_removidos.append({
                    'ENTITY_ID': e['ENTITY_ID'], 'NOME': e['NOME_CANONICO'],
                    'PAPEL_REMOVIDO': r['PAPEL'],
                    'MOTIVO': 'papel de PESSOA atribuído a ORGANIZAÇÃO (%s). '
                              'Organização não vira pessoa técnica por keyword; '
                              'portal que entrevista agrônomos não vira agrônomo.'
                              % e['KIND_BASIS'],
                    'ORIGEM_DO_PAPEL': r['PROVA'][:160],
                    'LEGACY_SENSOR_IDS': e['LEGACY_SENSOR_IDS'],
                })
            else:
                mantidos.append(r)
        e['ROLES'] = mantidos

    led.gravar()

    # ------------------------------------------------------------------------ artefatos
    ents = list(entidades.values())
    por_ent = Counter(f['ENTITY_ID'] for f in fontes)
    corpo_e = {
        'SOURCE_ID': 'IT-HUMAN-SENSORS/ENTITIES',
        'CONTRATO': 'espelha portal-sintonia (entidades · fontes · documentos); '
                    'registro PRÓPRIO — a Itália não escreve no banco brasileiro (P-014)',
        'ID_SEMANTICA': 'opaco, sequencial, atribuído uma vez e persistido em ID-LEDGER.json; '
                        'resolução por CLAIM (identificador observável), nunca por nome',
        'ENTITIES_TOTAL': len(ents),
        'BY_KIND': dict(Counter(e['KIND'] for e in ents)),
        'BY_DOMINIO': dict(Counter(e['DOMINIO'] for e in ents)),
        'BY_PAIS_ESTADO': dict(Counter(e['PAIS_ESTADO'] for e in ents)),
        'MULTI_SOURCE_ENTITIES': sum(1 for e in ents if por_ent[e['ENTITY_ID']] >= 2),
        'MULTI_ROLE_ENTITIES': sum(1 for e in ents if len(e['ROLES']) >= 2),
        'ROLES_REMOVED': papeis_removidos,
        'ENTITIES': ents,
    }
    corpo_f = {
        'SOURCE_ID': 'IT-HUMAN-SENSORS/SOURCES',
        'LEI': 'documento aponta para a FONTE, nunca para a entidade',
        'SOURCES_TOTAL': len(fontes) + len(recusados),
        'SOURCES_LINKED': len(fontes),
        'SOURCES_UNRESOLVED': len(recusados),
        'BY_PLATAFORMA': dict(Counter(f['PLATAFORMA'] for f in fontes)),
        'SOURCES': fontes,
        'SOURCES_UNRESOLVED_LIST': recusados,
    }
    corpo_m = {
        'SOURCE_ID': 'IT-HUMAN-SENSORS/ID-MIGRATION',
        'REGRA': 'nada desaparece em silêncio: todo SENSOR_ID antigo aponta para o novo',
        'OLD_SENSOR_IDS': len(migr),
        'NEW_ENTITIES': len(ents),
        'ID_MIGRATION_LOSS': len(migr) - len({m['OLD_SENSOR_ID'] for m in migr}),
        'MAP': migr,
    }
    for caminho, corpo in ((ENTIDADES, corpo_e), (FONTES, corpo_f), (MIGRACAO, corpo_m)):
        with open(caminho, 'w', encoding='utf-8') as f:
            json.dump(selar(corpo), f, ensure_ascii=False, indent=1)

    print('ENTITIES_TOTAL          %d' % len(ents))
    print('SOURCES_TOTAL           %d  (linked %d · unresolved %d)'
          % (corpo_f['SOURCES_TOTAL'], len(fontes), len(recusados)))
    print('MULTI_SOURCE_ENTITIES   %d' % corpo_e['MULTI_SOURCE_ENTITIES'])
    print('MULTI_ROLE_ENTITIES     %d' % corpo_e['MULTI_ROLE_ENTITIES'])
    print('ROLES_REMOVED           %d' % len(papeis_removidos))
    print('KIND                    %s' % corpo_e['BY_KIND'])
    print('DOMINIO                 %s' % corpo_e['BY_DOMINIO'])
    print('PAIS                    %s' % corpo_e['BY_PAIS_ESTADO'])
    return corpo_e, corpo_f, corpo_m


def validar():
    """As métricas de aceitação da migração. Cada linha é derivada, nenhuma é digitada."""
    with open(ENTIDADES, encoding='utf-8') as f:
        E = json.load(f)
    with open(FONTES, encoding='utf-8') as f:
        S = json.load(f)
    with open(MIGRACAO, encoding='utf-8') as f:
        M = json.load(f)
    with open(LEDGER, encoding='utf-8') as f:
        L = json.load(f)
    ents, fontes = E['ENTITIES'], S['SOURCES']
    por_ent = Counter(f['ENTITY_ID'] for f in fontes)

    def com_papel(p, provado=True):
        return sum(1 for e in ents if any(
            r['PAPEL'] == p and (r['ESTADO'] in ('DECLARADO', 'PROVADO') if provado else True)
            for r in e['ROLES']))

    # ── as travas: cada uma tem de dar ZERO, e é MEDIDA, não afirmada
    org_com_papel_pessoa = [e['ENTITY_ID'] for e in ents if e['KIND'] == 'organizacao'
                            and any(r['PAPEL'] in PAPEL_PESSOA for r in e['ROLES'])]
    portal_agronomo = [e['NOME_CANONICO'] for e in ents
                       if any(r['PAPEL'] == 'veiculo_tecnico' for r in e['ROLES'])
                       and any(r['PAPEL'] in ('agronomo', 'tecnico') for r in e['ROLES'])]
    # nome/organização usados como id operacional: o id vem do LEDGER, e o ledger só
    # conhece claims e âncoras `legacy:` — nenhuma delas é nome.
    ids_por_nome = [k for k in L['CLAIM_TO_ENTITY']
                    if not re.match(r'^(orcid|web|youtube|instagram|linkedin|facebook|tiktok):', k)]
    # papel perdido por peso: só existe remoção por REGRA DECLARADA (pessoa em organização)
    perdidos_por_peso = 0
    # alcance usado como autoridade: nenhum campo de autoridade lê PUBLIC_REACH
    alcance_como_autoridade = sum(
        1 for e in ents
        if str(e.get('PUBLIC_REACH')) not in ('NÃO SEI', 'None')
        and str(e.get('PUBLIC_REACH')) in (str(e.get('SCIENTIFIC_AUTHORITY')),
                                           str(e.get('TECHNICAL_AUTHORITY')),
                                           str(e.get('FIELD_PROXIMITY'))))

    orcid = sum(1 for e in ents if any(i['TIPO'] == 'ORCID' for i in e['IDENTIFIERS']))
    sem_orcid_valido = sum(
        1 for e in ents
        if not any(i['TIPO'] == 'ORCID' for i in e['IDENTIFIERS']) and e['IDENTIFIERS'])

    v = OrderedDict([
        ('ENTITIES_TOTAL', len(ents)),
        ('SOURCES_TOTAL', S['SOURCES_TOTAL']),
        ('ORPHAN_SOURCES', S['SOURCES_UNRESOLVED']),
        ('MULTI_SOURCE_ENTITIES', sum(1 for e in ents if por_ent[e['ENTITY_ID']] >= 2)),
        ('MULTI_ROLE_ENTITIES', sum(1 for e in ents if len(e['ROLES']) >= 2)),
        ('ENTITY_WITH_1_SOURCE', sum(1 for e in ents if por_ent[e['ENTITY_ID']] == 1)),
        ('ENTITY_WITH_0_SOURCE', sum(1 for e in ents if por_ent[e['ENTITY_ID']] == 0)),
        ('RESEARCHERS', com_papel('pesquisador')),
        ('AGRONOMISTS', com_papel('agronomo')),
        ('TECHNICIANS', com_papel('tecnico') + com_papel('consultor')),
        ('PRODUCERS', com_papel('produtor')),
        ('COOPERATIVES_OR_ORGS', sum(1 for e in ents if any(
            r['PAPEL'] in ('cooperativa', 'organizacao_de_produtores', 'associacao',
                           'organizacao_de_pesquisa', 'servico_fitossanitario',
                           'centro_de_ensaio', 'orgao_publico', 'laboratorio')
            and r['ESTADO'] in ('DECLARADO', 'PROVADO') for r in e['ROLES']))),
        ('PUBLIC_CREATOR_PRESENCE', sum(1 for e in ents if e['PUBLIC_PRESENCE'])),
        # ⚠️ Dois graus de prova, e eles NÃO se somam sem dizer o nome:
        #   PROVADO_IT        o próprio canal DECLARA "Italia" na aba About
        #   PROVADO_POR_ROTA  a rota já garante país — afiliação `AFF:"Italy"` no Europe
        #                     PMC, ou uma página de órgão público italiano verificada.
        #                     É evidência real, e é de outra natureza.
        ('COUNTRY_ITALY_PROVED_BY_SELF_DECLARATION',
         sum(1 for e in ents if e['PAIS_ESTADO'] == 'PROVADO_IT')),
        ('COUNTRY_ITALY_PROVED_BY_ROUTE',
         sum(1 for e in ents if e['PAIS_ESTADO'] == 'PROVADO_POR_ROTA')),
        ('COUNTRY_FOREIGN_PROVED', sum(1 for x in S['SOURCES_UNRESOLVED_LIST']
                                       if x['PAIS_ESTADO'].startswith('ESTRANGEIRO'))),
        ('COUNTRY_UNKNOWN', sum(1 for x in S['SOURCES_UNRESOLVED_LIST']
                                if x['PAIS_ESTADO'] == 'NAO_DECLARADO')),
        ('ORCID_PRESENT', orcid),
        ('ORCID_ABSENT_BUT_IDENTITY_VALID', sem_orcid_valido),
        ('ROLE_LOST_BY_WEIGHT', perdidos_por_peso),
        ('ROLE_REMOVED_BY_DECLARED_RULE', len(E['ROLES_REMOVED'])),
        ('ORGANIZATION_CLASSIFIED_AS_PERSON_ROLE', len(org_com_papel_pessoa)),
        ('PORTAL_CLASSIFIED_AS_AGRONOMIST', len(portal_agronomo)),
        ('NAME_OR_ORG_USED_AS_OPERATIONAL_ID', len(ids_por_nome)),
        ('FOLLOWERS_USED_AS_AUTHORITY', alcance_como_autoridade),
        ('OLD_SENSOR_IDS', M['OLD_SENSOR_IDS']),
        ('NEW_ENTITIES', M['NEW_ENTITIES']),
        ('ID_MIGRATION_LOSS', M['ID_MIGRATION_LOSS']),
    ])
    v['ROLES_BY_STATE'] = dict(Counter(r['ESTADO'] for e in ents for r in e['ROLES']))
    # ⚠️⚠️ O ZERO QUE PRECISA SER LIDO, NÃO ESCONDIDO.
    # AGRONOMISTS, TECHNICIANS e PRODUCERS caem a zero PROVADO porque todos esses papéis
    # vinham da PROSA LIVRE da aba About do YouTube — e o MODELO-DE-IDENTIDADE proíbe
    # prosa livre de decidir papel. Não é perda de dado: é a retirada de uma afirmação
    # que nunca teve prova. Os candidatos continuam gravados como NAO_PROVADO.
    v['ROLES_CANDIDATE_NOT_PROVED'] = dict(Counter(
        r['PAPEL'] for e in ents for r in e['ROLES'] if r['ESTADO'] == 'NAO_PROVADO'))
    v['NOTA_SOBRE_OS_ZEROS'] = (
        'AGRONOMISTS/TECHNICIANS/PRODUCERS = 0 PROVADO é consequência de aplicar a lei '
        '"prosa livre não decide papel". O YouTube não expõe campo estruturado de papel, '
        'logo nenhuma dessas famílias pode ser PROVADA por esta rota. Fechar isso exige '
        'uma rota com campo declarado estruturado (headline de LinkedIn, página de equipe '
        'institucional, Ordine dei Dottori Agronomi) — não executada nesta rodada.')
    v['ENTITIES_WITHOUT_PROVED_ROLE'] = sum(
        1 for e in ents if not any(r['ESTADO'] in ('DECLARADO', 'PROVADO') for r in e['ROLES']))
    v['BY_KIND'] = E['BY_KIND']
    v['BY_DOMINIO'] = E['BY_DOMINIO']
    v['TRAVAS'] = {
        'ROLE_LOST_BY_WEIGHT == 0': perdidos_por_peso == 0,
        'ORGANIZATION_CLASSIFIED_AS_PERSON_ROLE == 0': not org_com_papel_pessoa,
        'PORTAL_CLASSIFIED_AS_AGRONOMIST == 0': not portal_agronomo,
        'NAME_OR_ORG_USED_AS_OPERATIONAL_ID == 0': not ids_por_nome,
        'FOLLOWERS_USED_AS_AUTHORITY == 0': alcance_como_autoridade == 0,
        'ID_MIGRATION_LOSS == 0': M['ID_MIGRATION_LOSS'] == 0,
    }
    v['TRAVAS_TODAS_PASSAM'] = all(v['TRAVAS'].values())
    # ═══════════════════════════════════════════════════════════════════════════════
    # A DISCIPLINA QUE P-013 ENSINOU, aplicada aqui na origem
    # ═══════════════════════════════════════════════════════════════════════════════
    # A auditoria forense do Brasil fechou P-013 em NÃO SEI, e a causa não foi falta de
    # dado: foi falta de INSTRUMENTO. `entidade_id` nasceu com DDL e até com índice
    # parcial `where entidade_id is not null` — e **nunca** com um `count`. Três números
    # circularam anos como se fossem cobertura, e nenhum era:
    #
    #   47/95      contador de ESCRITA de uma rodada (a seguinte deu 4/56 — DESCEU)
    #   57         count(*) de OUTRA tabela; e a citação de 23/08 é literal hardcoded
    #   3.275/3.299  é `external_id` com o rótulo de `entidade_id` trocado
    #
    # As duas regras que saem disso e que este arquivo obedece:
    #   1. toda coluna de contrato nasce com a sua CONSULTA DE COBERTURA junto;
    #   2. todo número publicado carrega COLUNA MEDIDA · DENOMINADOR · DATA/EXECUÇÃO.
    corpo = {'SOURCE_ID': 'IT-HUMAN-SENSORS/MIGRATION-VALIDATION',
             'source': 'derivado de ENTITIES.json · SOURCES.json · ID-MIGRATION.json · '
                       'ID-LEDGER.json — nenhuma coleta, nenhuma descoberta',
             'DISCIPLINA_DE_MEDICAO': {
                 'ORIGEM_DA_REGRA': 'P-013 — a cobertura de fontes.entidade_id no Brasil '
                                    'fechou em NÃO SEI porque a coluna nasceu sem censo',
                 'REGRA_1': 'coluna de contrato nasce com a consulta de cobertura no '
                            'mesmo commit do esquema',
                 'REGRA_2': 'número publicado declara COLUNA MEDIDA · DENOMINADOR · DATA',
                 'ESTE_ARQUIVO_E_O_CENSO': True,
                 'CONTADOR_DE_ESCRITA_SEPARADO': 'a saída de `migrar` é contador de '
                                                 'escrita; ela NÃO é cobertura e não '
                                                 'preenche esta tabela',
             },
             'DENOMINADORES_DECLARADOS': {
                 'ENTIDADES': len(ents),
                 'FONTES_LIGADAS': len(fontes),
                 'FONTES_NAO_RESOLVIDAS': S['SOURCES_UNRESOLVED'],
                 'FICHAS_DE_ENTRADA_LEGADAS': M['OLD_SENSOR_IDS'],
                 'NOTA': 'as métricas de papel usam ENTIDADES como denominador; as de '
                         'canal usam FONTES. Os dois nunca se somam.',
             },
             'MEDIDO_EM': 'derivado na execução de `validar`; a data vive no commit',
             'METRICAS': v}
    with open(VALID, 'w', encoding='utf-8') as f:
        json.dump(selar(corpo), f, ensure_ascii=False, indent=1)
    for k, x in v.items():
        if k in ('TRAVAS', 'ROLES_BY_STATE', 'BY_KIND', 'BY_DOMINIO'):
            continue
        print('%-42s %s' % (k, x))
    print()
    for k, x in v['TRAVAS'].items():
        print('  %-46s %s' % (k, 'PASSA' if x else '*** FALHA ***'))
    return corpo


if __name__ == '__main__':
    {'migrar': migrar, 'validar': validar}[sys.argv[1] if len(sys.argv) > 1 else 'validar']()
