#!/usr/bin/env python3
"""Vocabulario CONTROLADO de rotulo italiano: cultura, alvo, e normalizacao de substancia.

POR QUE ESTE ARQUIVO EXISTE SEPARADO DO PARSER
----------------------------------------------
O caso OLIO MINERALE provou o defeito: conferi a string 'OLIO MINERALE' contra a lista
das 53 substancias ADAMA, a lista escreve 'PARAFFIN OIL/(CAS 97862-82-3)', e eu conclui
ZERO. A equivalencia existia e eu nao a tinha escrito em lugar nenhum.

A correcao nao e casar por similaridade. E ter uma camada EXPLICITA onde cada
equivalencia tem RAW_TERM, CANONICAL_TERM, RELATION_TYPE, SOURCE e CONFIDENCE — e onde
o que nao tem fonte fica como NAO_SEI em vez de virar casamento.

  NADA AQUI PODE SER PROMOVIDO POR EMBEDDING OU POR PARECENCA DE TEXTO.
"""

# ── CULTURAS ──────────────────────────────────────────────────────────────────
# CANONICAL -> lista de formas como o rotulo italiano as escreve.
CULTURAS = {
    'OLIVO': [r'oliv[oi]', r'oliveti', r'olea\s+europaea'],
    'MELO': [r'mel[oi]\b', r'malus'],
    'PERO': [r'per[oi]\b', r'pyrus'],
    'PESCO': [r'pesc[oh]?[oi]\b', r'nettarin\w*', r'prunus\s+persica'],
    'SUSINO': [r'susin[oi]'],
    'ALBICOCCO': [r'albicocc\w*'],
    'CILIEGIO': [r'cilieg\w*'],
    'ACTINIDIA': [r'actinidia', r'kiwi'],
    'VITE': [r'vite\b', r'vigneto', r'vitis', r'uva\s+da\s+(?:vino|tavola)'],
    # Nomes de citros que faltavam e que fizeram a celula de AGRUMI de 018244
    # ser recusada como prosa: a densidade dava 0,53 contra o limite de 0,72
    # so porque oito dos catorze nomes enumerados nao existiam aqui. Sao
    # especies e hibridos reais de Citrus, conferidos na propria enumeracao do
    # rotulo ('arancio dolce, arancio amaro, mandarino, clementino, limone,
    # pompelmo, pomelo, bergamotto, cedro, tangerino, chinotto, mapo, tangelo,
    # limetta'). Nao e aproximacao: e a lista que a etiqueta escreve.
    'AGRUMI': [r'agrum[ie]', r'aranci[oi]', r'limon[ei]', r'mandarin[oi]',
               r'clementin\w*', r'limetta', r'pompelmo', r'pomelo', r'bergamott[oi]',
               r'\bcedro\b', r'tangerin[oi]', r'chinott[oi]', r'\bmapo\b',
               r'tangel[oi]'],
    'FRUMENTO': [r'frumento', r'grano\s+(?:tenero|duro)', r'triticum'],
    'ORZO': [r'orzo', r'hordeum'],
    'SEGALE': [r'segale'],
    'TRITICALE': [r'triticale'],
    'AVENA': [r'avena\b'],
    'MAIS': [r'mais\b', r'granoturco', r'zea\s+mays'],
    'RISO': [r'riso\b', r'oryza'],
    'SOIA': [r'soia', r'glycine\s+max'],
    'GIRASOLE': [r'girasol\w*'],
    'COLZA': [r'colza', r'brassica\s+napus'],
    'BARBABIETOLA': [r'barbabietol\w*'],
    'PATATA': [r'patat[ae]', r'solanum\s+tuberosum'],
    'POMODORO': [r'pomodor[oi]', r'lycopersic\w*'],
    'FRAGOLA': [r'fragol\w*'],
    'LATTUGA': [r'lattuga'],
    'CIPOLLA': [r'cipoll[ae]'],
    'AGLIO': [r'aglio'],
    'CAROTA': [r'carot[ae]'],
    'CARCIOFO': [r'carciof[oi]'],
    'CUCURBITACEE': [r'cucurbitacee'],
    'MELONE': [r'melon[ei]'],
    'COCOMERO': [r'cocomer[oi]'],
    'CETRIOLO': [r'cetriol\w*'],
    'ZUCCHINO': [r'zucchin[oi]', r'zucca'],
    'MELANZANA': [r'melanzan[ae]'],
    'PEPERONE': [r'peperon[ei]'],
    'TABACCO': [r'tabacco'],
    'ERBA_MEDICA': [r'erba\s+medica'],
    'PISELLO': [r'pisell[oi]'],
    'FAGIOLO': [r'fagiol\w*'],
    'NOCE': [r'noce\b', r'noci\b', r'juglans'],
    'NOCCIOLO': [r'nocciol[oi]\b'],
    'MANDORLO': [r'mandorl[oi]'],
    'CASTAGNO': [r'castagn[oi]'],
    'SPINACIO': [r'spinaci[oi]'],
    'SORGO': [r'sorgo'],
    'RAVANELLO': [r'ravanell[oi]'],
    'CAVOLO': [r'cavol\w*'],
}

# GRUPOS de cultura. So podem ser expandidos quando o PROPRIO ROTULO enumera os
# membros entre parenteses ao lado do grupo. 'Pomacee' sozinho NAO vira melo+pero.
GRUPOS = {
    'POMACEE': ['MELO', 'PERO'],
    'DRUPACEE': ['PESCO', 'SUSINO', 'ALBICOCCO', 'CILIEGIO'],
    'ARBOREE': [],
    'FRUTTIFERI': [],
    'ORTICOLE': [],
    'CUCURBITACEE': ['MELONE', 'COCOMERO', 'CETRIOLO', 'ZUCCHINO'],
}

# ── ALVOS ─────────────────────────────────────────────────────────────────────
ALVOS = {
    'AFIDI': [r'afid[ei]', r'afide', r'aphis', r'myzus', r'dysaphis', r'brachycaudus',
              r'hyalopterus', r'toxoptera', r'eriosoma', r'macrosiphum'],
    'COCCINIGLIE': [r'cocciniglie?', r'saissetia', r'planococcus', r'quadraspidiotus'],
    'TIGNOLE': [r'tignol\w*', r'prays', r'lobesia', r'eupoecilia'],
    'MOSCA': [r'\bmosca\b', r'\bmosche\b', r'bactrocera', r'ceratitis', r'\bmosca\s+bianca'],
    'CIMICI': [r'cimic[ei]', r'halyomorpha', r'nezara'],
    'ACARI': [r'acar[oi]', r'tetranychus', r'panonychus'],
    'ERIOFIDI': [r'eriofid[ei]'],
    'TRIPIDI': [r'tripid[ei]', r'thrips', r'frankliniella'],
    'CICALINE': [r'cicalin[ae]', r'scaphoideus', r'empoasca'],
    'PSILLE': [r'psill[ae]', r'cacopsylla'],
    'METCALFA': [r'metcalfa'],
    'ALEURODIDI': [r'aleurodid[ei]', r'trialeurodes', r'bemisia'],
    'LEPIDOTTERI': [r'lepidotter[oi]', r'ricamatric\w*', r'tortricid\w*', r'adoxophyes',
                    r'yponomeuta', r'hyphantria'],
    'CARPOCAPSA': [r'carpocaps\w*', r'cydia\s+pomonella'],
    'CEMIOSTOMA': [r'cemiostoma', r'leucoptera'],
    'LITOCOLLETE': [r'litocollete', r'phyllonorycter'],
    'ANARSIA': [r'anarsia'],
    'CIDIA': [r'\bcidia\b'],
    'CECIDOMIA': [r'cecidomi\w*', r'cecidomid\w*', r'contarinia', r'dasineura'],
    'PIRALIDE': [r'piralide', r'ostrinia'],
    'DIABROTICA': [r'diabrotica'],
    'DORIFORA': [r'dorifora', r'leptinotarsa'],
    'ELATERIDI': [r'elaterid[ei]', r'agriotes'],
    'NOTTUE': [r'nottua\b', r'nottue\b', r'nottuid\w*', r'agrotis', r'spodoptera',
               r'helicoverpa'],
    'ALTICA': [r'altica'],
    'CASSIDA': [r'cassida'],
    'LEMA': [r'\blema\b'],
    # 'coleotteri (Meligethes aeneus)' na colza: o rotulo escreve so o genero.
    'MELIGETE': [r'meligete', r'meligethes'],
    'TENTREDINE': [r'tentredine'],
    'CLEONO': [r'cleono'],
    'LISSO': [r'\blisso\b'],
    'APION': [r'\bapion\b'],
    'FITONOMO': [r'fitonomo'],
    'IDRELLIA': [r'idrellia', r'hydrellia'],
    'SIGARAIO': [r'sigaraio', r'byctiscus'],
    'AGRILO': [r'agrilo'],
    'MAGGIOLINO': [r'maggiolino', r'melolontha'],
    'OZIORRINCO': [r'oziorrinco', r'otiorhynchus'],
    'MARGARONIA': [r'margaroni\w*', r'palpita'],
    'DITTERI': [r'ditter[oi]'],
    'NEMATODI': [r'nematod[ei]'],
    # Os oidios sao Erysiphales. A etiqueta as vezes escreve so o nome cientifico
    # ('Leveillula taurica' no pimentao, 'Sphaerotheca pannosa' no pessego,
    # 'Erysiphe necator' na videira) sem nunca escrever a palavra oidio. Sem estes
    # generos o par existia no rotulo e sumia na normalizacao. Fonte: nomenclatura
    # de Erysiphales; conferido nos rotulos 002983, 013405, 017358, 008601, 010587.
    # ADICIONADO nesta rodada, depois que a conferencia do gabarito expos a lacuna —
    # o efeito no numero esta medido e publicado lado a lado (antes/depois).
    'OIDIO': [r'oidio', r'blumeria', r'erisife', r'erysiph\w*', r'uncinula',
              r'uncicola', r'podosphaera', r'sphaerotheca', r'leveillula'],
    'PERONOSPORA': [r'peronospora', r'plasmopara'],
    'TICCHIOLATURA': [r'ticchiolatura', r'venturia'],
    'RUGGINE': [r'ruggine', r'puccinia'],
    'SEPTORIOSI': [r'septorios[ei]', r'septoria', r'zymoseptoria'],
    'FUSARIOSI': [r'fusarios[ei]', r'fusarium', r'microdochium'],
    'RINCOSPORIOSI': [r'rincosporios[ei]', r'rhyncosporium'],
    'ELMINTOSPORIOSI': [r'elmintosporios[ei]', r'helminthosporium', r'pyrenophora'],
    'RAMULARIA': [r'ramularia'],
    'CARBONE': [r'\bcarbone\b', r'urocystis', r'ustilago'],
    'BOTRITE': [r'botrite', r'botrytis'],
    'ALTERNARIA': [r'alternaria'],
    'MONILIA': [r'monilia'],
    'CERCOSPORA': [r'cercospor\w*'],
    'ANTRACNOSI': [r'antracnos[ei]', r'colletotrichum', r'gloeosporium'],
    'MUFFA': [r'muffa\s+\w+'],
    'MARCIUME': [r'marciume'],
    # Duas avversita que cinco rotulos ADAMA declaram na coluna Avversita e que
    # o dicionario nunca teve. Nao sao aproximacao: sao o que a etiqueta escreve.
    #
    #   018244/015235/017335/017337/017898 · "Gommosi parassitaria (Phytophtora
    #   spp.)"  ·  015235/017335/017337/017898 · "gemme nere (Pseudominas
    #   syringae)"     (os erros de grafia sao do proprio PDF)
    #
    # O QUE FICA DELIBERADAMENTE DE FORA, E POR QUE
    # ---------------------------------------------
    # O genero NAO entra em nenhuma das duas. 'phytophthora' casaria Phytophthora
    # infestans, que na batata e a PERONOSPORA — o alvo mais frequente do
    # conjunto — e transformaria peronospora de batata em gomose de citros.
    # 'pseudomonas' casaria as bacterioses de kiwi e de drupaceas, que nao sao
    # gemas negras de pereira. O nome italiano da doenca e especifico; o nome do
    # genero nao e.
    #
    #     O GENERO NOMEIA O FUNGO. A DOENCA E QUE NOMEIA O PROBLEMA.
    #
    # Regressao rodada antes de acrescentar: 10 ocorrencias nos 163 rotulos, zero
    # numa janela que ja tivesse outro alvo; 1 ocorrencia nos 131 documentos de
    # fala, e e mesmo a gomose dos citros ("il controllo della gommosi si fa
    # sempre con il rame"); 'gommoso', 'gommosita', 'gommista', 'gemme' e 'nere'
    # sozinhas nao casam.
    'GOMMOSI': [r'gommos[ai]'],
    'GEMME_NERE': [r'gemme\s+nere'],
    'VERTICILLIOSI': [r'verticill\w*'],
    'MALATTIE_FUNGINE': [r'malattie\s+fungine', r'anti-?oidic\w*'],
    'INFESTANTI': [r'infestanti', r'malerbe', r'graminacee', r'dicotiledoni',
                   r'\bdiserbo\b'],
}

# ── NORMALIZACAO DE SUBSTANCIA ────────────────────────────────────────────────
# Cada equivalencia tem DONO e FONTE. Sem fonte, nao entra.
SUBSTANCIA_NORM = [
    {
        'RAW_TERM': 'OLIO MINERALE',
        'CANONICAL_TERM': 'PARAFFIN OIL/(CAS 97862-82-3)',
        'RELATION_TYPE': 'COMMON_NAME_OF_REGISTERED_SUBSTANCE',
        'SOURCE': 'os rotulos ADAMA 012573 (EKO OIL SPRAY) e 014386 (OLIONET) declaram '
                  'ACTIVE_INGREDIENTS = PARAFFIN OIL/(CAS 97862-82-3) e sao vendidos como '
                  'olio bianco/minerale; o registro do Ministero e a fonte do nome canonico.',
        'CONFIDENCE': 'MEDIUM',
        'RESSALVA': 'olio minerale e nome de CLASSE. Nem todo olio minerale do mercado e '
                    'este CAS. A equivalencia serve para NAO PERDER o elo, e nao para '
                    'afirmar que qualquer mencao a olio minerale e produto ADAMA.',
    },
    {
        'RAW_TERM': 'OLIO BIANCO',
        'CANONICAL_TERM': 'PARAFFIN OIL/(CAS 97862-82-3)',
        'RELATION_TYPE': 'COMMON_NAME_OF_REGISTERED_SUBSTANCE',
        'SOURCE': 'mesma base de OLIO MINERALE',
        'CONFIDENCE': 'MEDIUM',
    },
    {
        'RAW_TERM': 'CLORTOLURON',
        'CANONICAL_TERM': 'CHLOROTOLURON',
        'RELATION_TYPE': 'ITALIAN_SPELLING',
        'SOURCE': 'o rotulo 016218 escreve "Clortoluron puro 35.7 g" e o registro declara '
                  'ACTIVE_INGREDIENTS = CHLOROTOLURON para o mesmo numero.',
        'CONFIDENCE': 'HIGH',
    },
    {
        'RAW_TERM': 'LAMBDACIALOTRINA',
        'CANONICAL_TERM': 'LAMBDA-CYHALOTHRIN',
        'RELATION_TYPE': 'ITALIAN_SPELLING',
        'SOURCE': 'registro do Ministero para os produtos de lambda-cialotrina da ADAMA',
        'CONFIDENCE': 'HIGH',
    },
    {
        'RAW_TERM': 'CAPTANO',
        'CANONICAL_TERM': 'CAPTAN',
        'RELATION_TYPE': 'ITALIAN_SPELLING',
        'SOURCE': 'registro do Ministero; e o defeito de fronteira que o FIX de '
                  'IT-CRUZAMENTOS-V2 ja tinha apontado nos boletins.',
        'CONFIDENCE': 'HIGH',
    },
    {
        'RAW_TERM': 'PROTIOCONAZOLO',
        'CANONICAL_TERM': 'PROTHIOCONAZOLE',
        'RELATION_TYPE': 'ITALIAN_SPELLING',
        'SOURCE': 'rotulo 018089 escreve "Protioconazolo puro 13.9 g"; registro declara '
                  'PROTHIOCONAZOLE',
        'CONFIDENCE': 'HIGH',
    },
    {
        'RAW_TERM': 'DIFENOCONAZOLO',
        'CANONICAL_TERM': 'DIFENOCONAZOLE',
        'RELATION_TYPE': 'ITALIAN_SPELLING',
        'SOURCE': 'registro do Ministero',
        'CONFIDENCE': 'HIGH',
    },
]

# ── TAXONOMIA ─────────────────────────────────────────────────────────────────
# A trava que a casa mediu duas vezes: nome comum NAO e identidade taxonomica.
TAXONOMIA = [
    {
        'RAW_TARGET_NAME': 'antracnosi del melo',
        'CANONICAL_TARGET_NAME': 'ANTRACNOSI',
        'TAXONOMIC_STATUS': 'COMMON_NAME_ONLY',
        'NOTA': 'o rotulo ADAMA escreve Gloeosporium; as vozes tratam o complexo '
                'Colletotrichum/Glomerella. Generos diferentes. NAO promover.',
        'TESTEMUNHA': 'IT-CRUZAMENTOS-V2 / IT-GAP-TAXONOMIA-V1 (TAX-01)',
    },
    {
        'RAW_TARGET_NAME': 'lebbra',
        'CANONICAL_TARGET_NAME': 'ANTRACNOSI',
        'TAXONOMIC_STATUS': 'CONFLICTING_IDENTIFICATION',
        'NOTA': 'nas Marche o campo chamava de lebbra (= Colletotrichum) o que o '
                'laboratorio identificou como Camarosporium. Identificacao conflitante, '
                'MEDIDA em laboratorio.',
        'TESTEMUNHA': 'IT-OLIVO-LEITURA-V2 achado OLIVO-F12 / IT-GAP-TAXONOMIA-V1 (TAX-02)',
    },
    {
        'RAW_TARGET_NAME': 'Gloeosporium',
        'CANONICAL_TARGET_NAME': 'ANTRACNOSI',
        'TAXONOMIC_STATUS': 'COMMON_NAME_ONLY',
        'NOTA': 'literal do rotulo. Preservado como TARGET_AS_WRITTEN; nao equivale a '
                'Colletotrichum sem fonte.',
        'TESTEMUNHA': 'TAX-01',
    },
]

STATUS_TAXONOMICO_PADRAO = 'UNKNOWN'
