#!/usr/bin/env python3
"""GABARITO COMPLETO — escrito a mao, lendo a geometria de cada rotulo.

Por que este arquivo existe e o anterior nao servia
---------------------------------------------------
O gabarito da rodada passada era PARCIAL por construcao: em varios rotulos eu
enumerei so as linhas que fui ler. Precisao medida contra gabarito parcial nao e
precisao — ela pune o parser por par que o gabarito nunca listou. Aqui cada rotulo
declara TODOS os pares que a etiqueta sustenta, e nao apenas exemplos positivos.

Regras que eu segui ao escrever
-------------------------------
1. Enumerar EXAUSTIVAMENTE. Se eu nao consigo defender a exaustividade de um rotulo
   (tabelas-matriz de centenas de blocos), ele NAO entra: entra em EXCLUIDOS com o
   motivo. Um rotulo meio-enumerado envenena a precisao medida.
2. O par nasce de uma declaracao de USO (cultura + alvo na mesma declaracao). Frase
   de escopo ("Fungicida per la difesa della BARBABIETOLA") declara CULTURA, nao par.
3. Alvo escrito na etiqueta vai em TARGET_RAW. O termo canonico vai em TARGET_CANON,
   digitado por mim. Quando o vocabulario controlado NAO tem termo para aquele alvo,
   TARGET_CANON = None e o par entra como VOCAB_GAP — e continua sendo um par que a
   etiqueta autoriza. Esconder esses pares inflaria o recall.
4. EXPECTED_NO_PAIR e EXPECTED_FALSE_POSITIVE_CROP registram o que NAO pode sair.
5. Nada aqui foi gerado pelo parser. O parser e o medido, nao a regua.

Namespace: CULTURAS e ALVOS de scripts/it_rotulo_vocab.py.
"""

# (cultura_canonica, alvo_como_escrito_no_rotulo, alvo_canonico_ou_None)
GABARITO = {

    # ---------------------------------------------------------------- TABELA LIMPA
    '009757': {  # SPYRALE — difenoconazolo + fenpropidin
        'PRODUCT': 'SPYRALE',
        'FAMILY': 'C_TABELA',
        'EVIDENCE': 'celula "Barbabietola da zucchero" com a celula de alvo a sua '
                    'direita/acima na mesma faixa vertical',
        'PAIRS': [
            ('BARBABIETOLA', 'Cercosporiosi (Cercospora beticola)', 'CERCOSPORA'),
            ('BARBABIETOLA', 'Oidio (Erysiphe betae)', 'OIDIO'),
        ],
        'EXPECTED_NO_PAIR': [
            ('BARBABIETOLA', 'MALATTIE_FUNGINE',
             'a frase "FUNGICIDA PER LA DIFESA DELLA BARBABIETOLA DA ZUCCHERO DALLE '
             'MALATTIE FUNGINE" declara ESCOPO. A doenca autorizada esta na tabela, '
             'e e nominada. Criar o par generico duplicaria a autorizacao.'),
        ],
    },

    '016152': {  # SEEDRON — concia de sementes
        'PRODUCT': 'SEEDRON',
        'FAMILY': 'C_TABELA',
        'EVIDENCE': 'linhas "Frumento duro, Frumento tenero: ...", "Orzo: ...", '
                    '"Avena: ...", "Segale e Triticale: ..."',
        'PAIRS': [
            ('FRUMENTO', 'Fusariosi (Fusarium spp., Microdochium nivale)', 'FUSARIOSI'),
            ('FRUMENTO', 'Carie (Tilletia caries)', None),
            ('FRUMENTO', 'Carbone (Ustilago nuda f.sp. tritici)', 'CARBONE'),
            ('ORZO', 'Fusariosi (Fusarium spp., Microdochium nivale)', 'FUSARIOSI'),
            ('ORZO', 'Carbone (Ustilago nuda)', 'CARBONE'),
            ('ORZO', 'Striatura bruna (Pyrenophora spp.)', 'ELMINTOSPORIOSI'),
            ('AVENA', 'Fusariosi (Fusarium spp., Microdochium nivale)', 'FUSARIOSI'),
            ('AVENA', 'Carbone (Ustilago avenae)', 'CARBONE'),
            ('SEGALE', 'Fusariosi (Fusarium Microdochium nivale)', 'FUSARIOSI'),
            ('SEGALE', 'Carbone (Urocystis occulta)', 'CARBONE'),
            ('TRITICALE', 'Fusariosi (Fusarium Microdochium nivale)', 'FUSARIOSI'),
            ('TRITICALE', 'Carbone (Urocystis occulta)', 'CARBONE'),
        ],
        'EXPECTED_NO_PAIR': [],
    },

    '018089': {  # AVASTEL
        'PRODUCT': 'AVASTEL',
        'FAMILY': 'C_TABELA',
        'EVIDENCE': 'tabela Coltura|Malattia fungina, faixas y: Frumento 347, Orzo 427, '
                    'Segale 476, Triticale 515',
        'PAIRS': [
            ('FRUMENTO', 'Septoriosi (Zymoseptoria tritici)', 'SEPTORIOSI'),
            ('FRUMENTO', 'Oidio (Blumeria graminis sp. tritici)', 'OIDIO'),
            ('FRUMENTO', 'Ruggine gialla (Puccinia striiformis)', 'RUGGINE'),
            ('FRUMENTO', 'Ruggine bruna (Puccinia recondita)', 'RUGGINE'),
            ('FRUMENTO', 'Fusariosi (Fusarium spp., Microdochium spp.)', 'FUSARIOSI'),
            ('ORZO', 'Rincosporiosi (Rhyncosporium secalis)', 'RINCOSPORIOSI'),
            ('ORZO', 'Elmintosporiosi (Pyrenophora teres)', 'ELMINTOSPORIOSI'),
            ('ORZO', 'Ramularia (Ramularia collo-cygni)', 'RAMULARIA'),
            ('ORZO', 'Ruggine bruna (Puccinia hordei)', 'RUGGINE'),
            ('ORZO', 'Oidio (Blumeria graminis sp. hordei)', 'OIDIO'),
            ('SEGALE', 'Rincosporiosi (Rhyncosporium secalis)', 'RINCOSPORIOSI'),
            ('SEGALE', 'Ruggine bruna (Puccinia recondita)', 'RUGGINE'),
            ('SEGALE', 'Septoriosi (Zymoseptoria tritici)', 'SEPTORIOSI'),
            ('SEGALE', 'Ruggine gialla (Puccinia striiformis)', 'RUGGINE'),
            ('TRITICALE', 'Ruggine bruna (Puccinia recondita)', 'RUGGINE'),
            ('TRITICALE', 'Ruggine gialla (Puccinia striiformis)', 'RUGGINE'),
            ('TRITICALE', 'Septoriosi (Zymoseptoria tritici)', 'SEPTORIOSI'),
            ('TRITICALE', 'Oidio (Blumeria graminis)', 'OIDIO'),
        ],
        'EXPECTED_NO_PAIR': [],
    },

    '017358': {  # BLAISE ULTRA
        'PRODUCT': 'BLAISE ULTRA',
        'FAMILY': 'C_TABELA',
        'EVIDENCE': 'tabela Coltura|Patogeno na coluna x~572-625 da pagina 0, '
                    'ultima linha (Vite) na pagina 1',
        'PAIRS': [
            ('FRUMENTO', 'Fusariosi (Fusarium spp.)', 'FUSARIOSI'),
            ('FRUMENTO', 'Oidio (Erysiphe spp.)', 'OIDIO'),
            ('FRUMENTO', 'Ruggini (Puccinia spp.)', 'RUGGINE'),
            ('FRUMENTO', 'Septoria (Septoria spp.)', 'SEPTORIOSI'),
            ('TRITICALE', 'Fusariosi (Fusarium spp.)', 'FUSARIOSI'),
            ('TRITICALE', 'Oidio (Erysiphe spp.)', 'OIDIO'),
            ('TRITICALE', 'Ruggini (Puccinia spp.)', 'RUGGINE'),
            ('TRITICALE', 'Septoria (Septoria spp.)', 'SEPTORIOSI'),
            ('ORZO', 'Oidio (Erysiphe spp.)', 'OIDIO'),
            ('ORZO', 'Ruggini (Puccinia spp.)', 'RUGGINE'),
            ('ORZO', 'Rincosporiosi (Rhynchosporium spp.)', 'RINCOSPORIOSI'),
            ('ORZO', 'Elmintosporiosi (Pyrenophora spp.)', 'ELMINTOSPORIOSI'),
            ('CETRIOLO', 'Oidio (Sphaerotheca spp., Erysiphe spp.)', 'OIDIO'),
            ('ZUCCHINO', 'Oidio (Sphaerotheca spp., Erysiphe spp.)', 'OIDIO'),
            ('MELONE', 'Oidio (Erysiphe spp.)', 'OIDIO'),
            ('POMODORO', 'Oidio (Leveillula taurica, Sphaerotheca spp.)', 'OIDIO'),
            ('MELANZANA', 'Oidio (Leveillula taurica, Sphaerotheca spp.)', 'OIDIO'),
            ('PEPERONE', 'Oidio (Leveillula taurica, Sphaerotheca spp.)', 'OIDIO'),
            ('AGLIO', 'Ruggini (Puccinia spp.)', 'RUGGINE'),
            ('CIPOLLA', 'Ruggini (Puccinia spp.)', 'RUGGINE'),
            ('VITE', 'Oidio (Uncicola necator)', 'OIDIO'),
        ],
        'EXPECTED_NO_PAIR': [],
    },

    '017955': {  # MAGANIC
        'PRODUCT': 'MAGANIC',
        'FAMILY': 'C_TABELA',
        'EVIDENCE': 'tabela cereais; o bloco achatado mistura as linhas, mas a pagina '
                    'separa Frumento / Orzo / Segale / Triticale',
        'PAIRS': [
            ('FRUMENTO', 'Septoria (Septoria tritici)', 'SEPTORIOSI'),
            ('FRUMENTO', 'Ruggini (Puccinia recondita)', 'RUGGINE'),
            ('FRUMENTO', 'Fusariosi della spiga (Fusarium spp., Microdochium spp.)',
             'FUSARIOSI'),
            ('ORZO', 'Elmintosporiosi (Pyrenophora teres)', 'ELMINTOSPORIOSI'),
            ('ORZO', 'Ramularia (Ramularia collo-cygni)', 'RAMULARIA'),
            ('SEGALE', 'Rincosporiosi (Rhyncosporium secalis)', 'RINCOSPORIOSI'),
            ('SEGALE', 'Ruggine (Puccinia recondita)', 'RUGGINE'),
            ('TRITICALE', 'Septoria (Septoria tritici)', 'SEPTORIOSI'),
            ('TRITICALE', 'Ruggini (Puccinia striiformis e Puccinia recondita)',
             'RUGGINE'),
        ],
        'EXPECTED_NO_PAIR': [],
    },

    # -------------------------------------------------- HEADER_CONTINUATION (sem ':')
    '007555': {  # KLARTAN — testemunha da familia
        'PRODUCT': 'KLARTAN',
        'FAMILY': 'HEADER_CONTINUATION',
        'EVIDENCE': 'cada bloco abre com a cultura em linha propria e a linha seguinte '
                    'comeca em "Contro ..."; nao ha dois-pontos',
        'PAIRS': [
            ('AGRUMI', 'afidi (Aphis spp., Toxoptera aurantii)', 'AFIDI'),
            ('AGRUMI', 'tignola degli agrumi (Prays citri)', 'TIGNOLE'),
            ('MELO', 'afidi (Dysaphis plantaginea, Aphis pomi)', 'AFIDI'),
            ('MELO', 'ditteri cecidomidi (Contarinia pyrivora, Dasineura pyri)',
             'CECIDOMIA'),
            ('MELO', 'lepidotteri (Adoxophyes orana, Yponomeuta malinellus, '
                     'Hyphantria cunea)', 'LEPIDOTTERI'),
            ('MELO', 'Cydia pomonella', 'CARPOCAPSA'),
            ('MELO', 'Phyllonorycter blancardella', 'LITOCOLLETE'),
            ('MELO', 'cimici (Halyomorpha halys)', 'CIMICI'),
            ('MELO', 'forme mobili giovanili di cocciniglia', 'COCCINIGLIE'),
            ('MELO', 'psille (Cacopsylla spp.)', 'PSILLE'),
            ('PERO', 'afidi (Dysaphis plantaginea, Aphis pomi)', 'AFIDI'),
            ('PERO', 'ditteri cecidomidi (Contarinia pyrivora, Dasineura pyri)',
             'CECIDOMIA'),
            ('PERO', 'lepidotteri (Adoxophyes orana, Yponomeuta malinellus, '
                     'Hyphantria cunea)', 'LEPIDOTTERI'),
            ('PERO', 'Cydia pomonella', 'CARPOCAPSA'),
            ('PERO', 'Phyllonorycter blancardella', 'LITOCOLLETE'),
            ('PERO', 'cimici (Halyomorpha halys)', 'CIMICI'),
            ('PERO', 'forme mobili giovanili di cocciniglia', 'COCCINIGLIE'),
            ('PERO', 'psille (Cacopsylla spp.)', 'PSILLE'),
            ('PESCO', 'afidi (Hyalopterus amygdali, Myzus persicae)', 'AFIDI'),
            ('PESCO', 'Anarsia lineatella', 'ANARSIA'),
            ('PESCO', 'lepidotteri (Cydia molesta)', 'LEPIDOTTERI'),
            ('PESCO', 'tripidi (Frankliniella occidentalis, Thrips spp.)', 'TRIPIDI'),
            ('PESCO', 'mosca della frutta (Ceratitis capitata)', 'MOSCA'),
            ('ALBICOCCO', 'afidi (Hyalopterus amygdali, Myzus persicae)', 'AFIDI'),
            ('ALBICOCCO', 'Anarsia lineatella', 'ANARSIA'),
            ('ALBICOCCO', 'lepidotteri (Cydia molesta)', 'LEPIDOTTERI'),
            ('ALBICOCCO', 'tripidi (Frankliniella occidentalis, Thrips spp.)', 'TRIPIDI'),
            ('ALBICOCCO', 'mosca della frutta (Ceratitis capitata)', 'MOSCA'),
            ('CILIEGIO', 'afidi (Myzus spp.)', 'AFIDI'),
            ('VITE', 'cicaline (Empoasca vitis, Scaphoideus titanus)', 'CICALINE'),
            ('VITE', 'tripidi (Frankliniella occidentalis, Drepanothrips reuteri)',
             'TRIPIDI'),
            ('PATATA', 'dorifora (Leptinotarsa decemlineata)', 'DORIFORA'),
            ('PATATA', 'afidi (Myzus persicae, Macrosiphum euphorbia)', 'AFIDI'),
            ('CAROTA', 'afidi (Cavariella aegopodii, Myzus persicae, Semiaphis dauci)',
             'AFIDI'),
            ('CETRIOLO', 'afidi (Aphis gossypii, Myzus persicae, Macrosiphum spp.)',
             'AFIDI'),
            ('CETRIOLO', 'tripidi (Frankliniella occidentalis, Thrips tabaci)', 'TRIPIDI'),
            ('ZUCCHINO', 'afidi (Aphis gossypii, Myzus persicae, Macrosiphum spp.)',
             'AFIDI'),
            ('ZUCCHINO', 'tripidi (Frankliniella occidentalis, Thrips tabaci)', 'TRIPIDI'),
            ('MELONE', 'afidi (Aphis gossypii, Myzus persicae, Macrosiphum spp.)',
             'AFIDI'),
            ('MELONE', 'tripidi (Frankliniella occidentalis, Thrips tabaci)', 'TRIPIDI'),
            ('MELANZANA', 'afidi (Aphis gossypii, Myzus persicae, Macrosiphum spp.)',
             'AFIDI'),
            ('MELANZANA', 'tripidi (Frankliniella occidentalis, Thrips tabaci)',
             'TRIPIDI'),
            ('MELANZANA', 'lepidotteri (Helicoverpa armigera)', 'LEPIDOTTERI'),
            ('MELANZANA', 'Spodoptera spp.', 'NOTTUE'),
            ('CAVOLO', 'afidi (Brevicoryne brassicae, Myzus persicae)', 'AFIDI'),
            ('CAVOLO', 'tripidi (Thrips spp.)', 'TRIPIDI'),
            ('CAVOLO', 'lepidotteri (Pieris spp., Mamestra brassicae)', 'LEPIDOTTERI'),
            ('LATTUGA', 'afidi (Myzus persicae, Nasonovia ribisnigri)', 'AFIDI'),
            ('LATTUGA', 'tripidi (Thrips spp.)', 'TRIPIDI'),
            ('LATTUGA', 'miridi (Lygus spp.)', None),
            ('LATTUGA', 'lepidotteri (Pieris spp., Mamestra brassicae)', 'LEPIDOTTERI'),
            ('LATTUGA', 'minatori fogliari (Liriomyza spp.)', None),
            ('PISELLO', 'afidi (Acyrthosiphon pisum, Aphis fabae)', 'AFIDI'),
            ('PISELLO', 'tripidi (Thrips angusticeps, Thrips tabaci)', 'TRIPIDI'),
            ('PISELLO', 'lepidotteri (Cydia nigricana)', 'LEPIDOTTERI'),
            ('PISELLO', 'Ostrinia nubilalis', 'PIRALIDE'),
            ('PISELLO', 'ditteri cecidomidi (Contarinia pisi)', 'CECIDOMIA'),
            ('FAGIOLO', 'afidi (Acyrthosiphon pisum, Aphis fabae)', 'AFIDI'),
            ('FAGIOLO', 'tripidi (Thrips angusticeps, Thrips tabaci)', 'TRIPIDI'),
            ('FAGIOLO', 'lepidotteri (Cydia nigricana)', 'LEPIDOTTERI'),
            ('FAGIOLO', 'Ostrinia nubilalis', 'PIRALIDE'),
            ('FAGIOLO', 'ditteri cecidomidi (Contarinia pisi)', 'CECIDOMIA'),
            ('CARCIOFO', 'afidi (Aphis fabae solanella, Capitophorus horni)', 'AFIDI'),
            ('CARCIOFO', 'tripidi (Thrips spp.)', 'TRIPIDI'),
            ('CARCIOFO', 'lepidotteri (Spodoptera spp.)', 'LEPIDOTTERI'),
            ('COLZA', 'afidi (Brevicoryne brassicae, Myzus persicae)', 'AFIDI'),
            ('COLZA', 'coleotteri (Meligethes aeneus)', 'MELIGETE'),
            ('COLZA', 'coleotteri (Ceutorhynchus napi, Psylliodes chrysocephala)', None),
            ('ORZO', 'afidi (Sitobion avenae, Rhopalosiphum padi)', 'AFIDI'),
            ('ORZO', 'ditteri cecidomidi (Contarinia tritici, Sitodiplosis mosellana)',
             'CECIDOMIA'),
            ('ORZO', 'cimici (Aelia rostrata, Eurygaster maura)', 'CIMICI'),
            ('ORZO', 'cicaline (Psammotettix alienus)', 'CICALINE'),
            ('AVENA', 'afidi (Sitobion avenae, Rhopalosiphum padi)', 'AFIDI'),
            ('AVENA', 'ditteri cecidomidi (Contarinia tritici, Sitodiplosis mosellana)',
             'CECIDOMIA'),
            ('AVENA', 'cimici (Aelia rostrata, Eurygaster maura)', 'CIMICI'),
            ('AVENA', 'cicaline (Psammotettix alienus)', 'CICALINE'),
            ('FRUMENTO', 'afidi (Sitobion avenae, Rhopalosiphum padi)', 'AFIDI'),
            ('FRUMENTO', 'ditteri cecidomidi (Contarinia tritici, Sitodiplosis '
                         'mosellana)', 'CECIDOMIA'),
            ('FRUMENTO', 'cimici (Aelia rostrata, Eurygaster maura)', 'CIMICI'),
            ('FRUMENTO', 'cicaline (Psammotettix alienus)', 'CICALINE'),
            ('SEGALE', 'afidi (Sitobion avenae, Rhopalosiphum padi)', 'AFIDI'),
            ('SEGALE', 'ditteri cecidomidi (Contarinia tritici, Sitodiplosis mosellana)',
             'CECIDOMIA'),
            ('SEGALE', 'cimici (Aelia rostrata, Eurygaster maura)', 'CIMICI'),
            ('SEGALE', 'cicaline (Psammotettix alienus)', 'CICALINE'),
            ('TRITICALE', 'afidi (Sitobion avenae, Rhopalosiphum padi)', 'AFIDI'),
            ('TRITICALE', 'ditteri cecidomidi (Contarinia tritici, Sitodiplosis '
                          'mosellana)', 'CECIDOMIA'),
            ('TRITICALE', 'cimici (Aelia rostrata, Eurygaster maura)', 'CIMICI'),
            ('TRITICALE', 'cicaline (Psammotettix alienus)', 'CICALINE'),
            ('BARBABIETOLA', 'afidi (Aphis fabae, Macrosiphum spp.)', 'AFIDI'),
            ('BARBABIETOLA', 'lepidotteri (Mamestra spp.)', 'LEPIDOTTERI'),
            ('BARBABIETOLA', 'altica (Chaetocnema tibialis)', 'ALTICA'),
            ('BARBABIETOLA', 'cleono (Conorhynchus mendicus)', 'CLEONO'),
            ('BARBABIETOLA', 'cassida (Cassida vittata)', 'CASSIDA'),
            ('ERBA_MEDICA', 'afidi (Acyrthosiphon pisum, Aphis fabae)', 'AFIDI'),
            ('ERBA_MEDICA', 'coleotteri (Apion pisi)', 'APION'),
            ('ERBA_MEDICA', 'coleotteri (Hypera postica, Sitona lineatus, '
                            'Phytodecta fornicata, Tichius flavus)', None),
            ('ERBA_MEDICA', 'tripidi (Thrips tabaci)', 'TRIPIDI'),
            ('ERBA_MEDICA', 'lepidotteri (Cydia nigricana)', 'LEPIDOTTERI'),
            ('ERBA_MEDICA', 'Ostrinia nubilalis', 'PIRALIDE'),
            ('FRAGOLA', 'afidi (Aphis gossypii)', 'AFIDI'),
            ('FRAGOLA', 'tripidi (Frankliniella occidentalis)', 'TRIPIDI'),
            ('FRAGOLA', 'lepidotteri (Spodoptera spp.)', 'LEPIDOTTERI'),
        ],
        'EXPECTED_NO_PAIR': [
            ('SUSINO', '*',
             'susino nao aparece na lista de usos: "Drupacee (pesco, albicocco, '
             'nettarino)". Expandir DRUPACEE pelo grupo padrao inventaria autorizacao.'),
            ('MAIS', '*', 'mais nao consta em nenhuma declaracao de uso deste rotulo'),
        ],
    },
}

# 007864 e 009800 sao o MESMO texto de uso de 007555 (mesma familia de produto,
# mesmas linhas). Copiar a enumeracao e legitimo porque eu conferi bloco a bloco que
# as declaracoes de uso coincidem; as diferencas estao fora da area de uso.
GABARITO['007864'] = dict(GABARITO['007555'],
                          PRODUCT='KLARTAN 20 EW',
                          EVIDENCE='mesmas declaracoes de uso de 007555, conferidas '
                                   'bloco a bloco na geometria')
GABARITO['009800'] = dict(GABARITO['007555'],
                          PRODUCT='MAVRIK 20 EW',
                          EVIDENCE='mesmas declaracoes de uso de 007555, com duas '
                                   'adicoes conferidas na geometria')
# 009800 acrescenta cimice asiatica em drupacee e drosofila em vite.
GABARITO['009800'] = dict(GABARITO['009800'], PAIRS=GABARITO['007555']['PAIRS'] + [
    ('PESCO', 'cimice asiatica (Halyomorpha halys)', 'CIMICI'),
    ('ALBICOCCO', 'cimice asiatica (Halyomorpha halys)', 'CIMICI'),
    ('PESCO', 'mosche della frutta (Ceratitis capitata, Bactrocera spp.)', 'MOSCA'),
    ('VITE', 'Moscerino dei piccoli frutti (Drosophila suzukii)', None),
])

GABARITO.update({

    # ------------------------------------------------- APYZA (testemunha do item 9)
    '018165': {
        'PRODUCT': 'APYZA 500 WG',
        'FAMILY': 'G_TEXTO_CORRIDO',
        'EVIDENCE': 'declaracoes "Melo e pero: contro afidi (...)" etc.',
        'PAIRS': [
            ('MELO', 'afidi (Dysaphis plantaginea, Aphis pomi, Dysaphis pyri)', 'AFIDI'),
            ('PERO', 'afidi (Dysaphis plantaginea, Aphis pomi, Dysaphis pyri)', 'AFIDI'),
            ('PESCO', 'afidi (Myzus persicae, Brachycaudus helichrysi, '
                      'Hyalopterus pruni)', 'AFIDI'),
            ('SUSINO', 'afidi (Myzus persicae, Brachycaudus helichrysi, '
                       'Hyalopterus pruni)', 'AFIDI'),
            ('POMODORO', 'afidi (Myzus persicae e Aphis gossypii)', 'AFIDI'),
            ('POMODORO', 'mosche bianche (Trialeurodes vaporariorum, Bemisia tabaci)',
             'ALEURODIDI'),
            ('MELONE', 'Aphis gossypii', 'AFIDI'),
            ('CETRIOLO', 'Aphis gossypii', 'AFIDI'),
            ('COCOMERO', 'Aphis gossypii', 'AFIDI'),
            ('ZUCCHINO', 'Aphis gossypii', 'AFIDI'),
            ('MELONE', 'mosche bianche (Trialeurodes vaporariorum, Bemisia tabaci)',
             'ALEURODIDI'),
            ('CETRIOLO', 'mosche bianche (Trialeurodes vaporariorum, Bemisia tabaci)',
             'ALEURODIDI'),
            ('COCOMERO', 'mosche bianche (Trialeurodes vaporariorum, Bemisia tabaci)',
             'ALEURODIDI'),
            ('ZUCCHINO', 'mosche bianche (Trialeurodes vaporariorum, Bemisia tabaci)',
             'ALEURODIDI'),
            ('AGRUMI', 'afidi (Aphis citricola, Toxoptera aurantii, Myzus persicae, '
                       'Aphis gossypii)', 'AFIDI'),
        ],
        'EXPECTED_NO_PAIR': [
            ('MELO', 'ERIOSOMA',
             'Eriosoma lanigerum NAO aparece neste rotulo. O conjunto antigo o listava '
             'para APYZA; inventa-lo aqui seria promover autorizacao inexistente.'),
        ],
    },

    '018156': {
        'PRODUCT': 'APYZA WG',
        'FAMILY': 'G_TEXTO_CORRIDO',
        'EVIDENCE': 'mesmo texto de uso de 018165, conferido bloco a bloco',
        'PAIRS': None,   # preenchido abaixo
        'EXPECTED_NO_PAIR': [
            ('MELO', 'ERIOSOMA', 'Eriosoma lanigerum nao aparece neste rotulo'),
        ],
    },

    # ---------------------------------------------- G_TEXTO_CORRIDO com dois-pontos
    '008102': {
        'PRODUCT': 'fungicida pomacee/drupacee/frutta a guscio',
        'FAMILY': 'G_TEXTO_CORRIDO',
        'EVIDENCE': 'declaracoes "Melo, Cotogno, Pero, Nashi: ... per la protezione da"',
        'PAIRS': [
            ('MELO', 'ticchiolatura (Venturia spp.)', 'TICCHIOLATURA'),
            ('MELO', 'Gloeosporium', 'ANTRACNOSI'),
            ('PERO', 'ticchiolatura (Venturia spp.)', 'TICCHIOLATURA'),
            ('PERO', 'Gloeosporium', 'ANTRACNOSI'),
            ('PERO', 'maculatura bruna del pero (Stemphylium vesicarium)', None),
            ('PESCO', 'mal della bolla (Taphrina deformans)', None),
            ('PESCO', 'corineo (Coryneum beijerinckii)', None),
            ('PESCO', 'cancro dei nodi o fusicocco (Phomopsis amygdali)', None),
            ('PESCO', 'moniliosi (Monilia spp.)', 'MONILIA'),
            ('ALBICOCCO', 'corineo (Wilsonomyces carpophilus)', None),
            ('ALBICOCCO', 'moniliosi (Monilia spp.)', 'MONILIA'),
            ('SUSINO', 'corineo (Wilsonomyces carpophilus)', None),
            ('SUSINO', 'moniliosi (Monilia spp.)', 'MONILIA'),
            ('CILIEGIO', 'moniliosi (Monilia spp.)', 'MONILIA'),
            ('CILIEGIO', 'corineo (Wilsonomyces carpophilus)', None),
            ('MANDORLO', 'fusicocco (Phomopsis amygdali)', None),
            ('MANDORLO', 'bolla (Taphrina deformans)', None),
            ('MANDORLO', 'ticchiolatura delle drupacee (Venturia carpophila)',
             'TICCHIOLATURA'),
            ('MANDORLO', 'corineo (Wilsonomyces carpophilus)', None),
            ('MANDORLO', 'macchie fogliari rosse (Polystigma ochraceum)', None),
            # CORRECAO DE GABARITO. Eu tinha marcado noce, nocciolo e castagno como
            # EXPECTED_AMBIGUOUS por ter lido o bloco truncado em 300 caracteres. A
            # pagina 1 enumera cada um deles com a sua propria doenca. O parser
            # afirmava NOCE x ANTRACNOSI e a minha medicao chamava isso de promocao
            # indevida de ambiguidade: o errado era o gabarito, e nao o parser.
            ('NOCE', 'antracnosi (Gnomonia juglandis)', 'ANTRACNOSI'),
            ('CASTAGNO', 'fersa (Mycosphaerella maculiformis)', None),
            ('NOCCIOLO', 'alternaria (Alternaria sp.)', 'ALTERNARIA'),
            ('NOCCIOLO', 'antracnosi (Colletotrichum sp.)', 'ANTRACNOSI'),
        ],
        'EXPECTED_NO_PAIR': [],
    },

    '008601': {
        'PRODUCT': 'fungicida vite/pomodoro (granuli idrodispersibili)',
        'FAMILY': 'G_TEXTO_CORRIDO',
        'EVIDENCE': 'blocos "VITE (UVA DA VINO E DA TAVOLA): ..." e "POMODORO ...:"',
        'PAIRS': [
            ('VITE', 'Escoriosi (Phomopsis viticola)', None),
            ('VITE', 'Marciume nero (Guignardia bidwellii)', 'MARCIUME'),
            ('VITE', 'Peronospora (Plasmopara viticola)', 'PERONOSPORA'),
            ('VITE', 'Marciume bianco (Coniella diplodiella)', 'MARCIUME'),
            ('VITE', 'Oidio (Erysipha necator)', 'OIDIO'),
            ('VITE', 'Muffa grigia (Botrytis cinerea)', 'MUFFA'),
            ('POMODORO', 'Peronospora (Phytophthora infestans)', 'PERONOSPORA'),
            ('POMODORO', 'Alternariosi (Alternaria solani)', 'ALTERNARIA'),
            ('POMODORO', 'Cladosporiosi (Fulvia fulva)', None),
            ('POMODORO', 'Septoriosi (Septoria lycopersici)', 'SEPTORIOSI'),
            ('POMODORO', 'Muffa grigia (Botrytis cinerea)', 'MUFFA'),
        ],
        'EXPECTED_NO_PAIR': [],
    },

    '010587': {
        'PRODUCT': 'fungicida vite/pomodoro (sospensione)',
        'FAMILY': 'G_TEXTO_CORRIDO',
        'EVIDENCE': 'mesmas declaracoes de 008601 em formulacao liquida',
        'PAIRS': [
            ('VITE', 'Escoriosi (Phomopsis viticola)', None),
            ('VITE', 'Marciume nero (Guignardia bidwellii)', 'MARCIUME'),
            ('VITE', 'Peronospora (Plasmopara viticola)', 'PERONOSPORA'),
            ('VITE', 'Marciume bianco (Coniella diplodiella)', 'MARCIUME'),
            ('VITE', 'Oidio (Erysiphe necator)', 'OIDIO'),
            ('VITE', 'Muffa grigia (Botrytis cinerea)', 'MUFFA'),
            ('POMODORO', 'Peronospora (Phytophthora infestans)', 'PERONOSPORA'),
            ('POMODORO', 'Alternaria (Alternaria solani)', 'ALTERNARIA'),
            ('POMODORO', 'Cladosporiosi (Fulvia fulva)', None),
            ('POMODORO', 'Septoria (Septoria lycopersici)', 'SEPTORIOSI'),
            ('POMODORO', 'Muffa grigia (Botrytis cinerea)', 'MUFFA'),
        ],
        'EXPECTED_NO_PAIR': [],
    },

    '002983': {
        'PRODUCT': 'anti-oidico multicultura',
        'FAMILY': 'G_TEXTO_CORRIDO',
        'EVIDENCE': 'bloco EPOCHE DI APPLICAZIONE, uma declaracao "Cultura: contro X" '
                    'por cultura',
        'PAIRS': [
            ('MELO', 'Podosphaera leucotricha', 'OIDIO'),
            ('VITE', 'Uncinula necator', 'OIDIO'),
            ('PESCO', 'Sphaerotheca pannosa', 'OIDIO'),
            ('ALBICOCCO', 'Sphaerotheca pannosa', 'OIDIO'),
            ('FRAGOLA', 'Sphaerotheca macularis', 'OIDIO'),
            ('CETRIOLO', 'Podosphaera fusca e Erysiphe cichoracearum', 'OIDIO'),
            ('ZUCCHINO', 'Podosphaera fusca e Erysiphe cichoracearum', 'OIDIO'),
            ('MELONE', 'Podosphaera fusca e Erysiphe cichoracearum', 'OIDIO'),
            ('COCOMERO', 'Podosphaera fusca e Erysiphe cichoracearum', 'OIDIO'),
            ('POMODORO', 'Leveillula taurica', 'OIDIO'),
            ('MELANZANA', 'Leveillula taurica', 'OIDIO'),
            ('PEPERONE', 'Leveillula taurica', 'OIDIO'),
        ],
        'EXPECTED_NO_PAIR': [],
    },

    '013405': {
        'PRODUCT': 'anti-oidico multicultura (2)',
        'FAMILY': 'G_TEXTO_CORRIDO',
        'EVIDENCE': 'mesmas declaracoes de 002983, com o bloco de uso intercalado '
                    'com a prosa de seguranca na mesma faixa geometrica',
        'PAIRS': [
            ('VITE', 'Uncinula necator', 'OIDIO'),
            ('FRAGOLA', 'Sphaerotheca macularis', 'OIDIO'),
            ('CETRIOLO', 'Podosphaera fusca e Erysiphe cichoracearum', 'OIDIO'),
            ('ZUCCHINO', 'Podosphaera fusca e Erysiphe cichoracearum', 'OIDIO'),
            ('MELONE', 'Podosphaera fusca e Erysiphe cichoracearum', 'OIDIO'),
            ('COCOMERO', 'Podosphaera fusca e Erysiphe cichoracearum', 'OIDIO'),
            ('POMODORO', 'Leveillula taurica', 'OIDIO'),
            ('MELANZANA', 'Leveillula taurica', 'OIDIO'),
            ('PEPERONE', 'Leveillula taurica', 'OIDIO'),
        ],
        'EXPECTED_NO_PAIR': [
            ('MELO', '*', 'melo NAO consta nas epoche di applicazione deste rotulo, '
                          'ao contrario de 002983'),
        ],
    },

    '013585': {
        'PRODUCT': 'SOLOFOL',
        'FAMILY': 'INLINE_WITH_CROP_QUALIFIER',
        'EVIDENCE': '"VITE da VINO: contro Peronospora, Botrite, Escoriosi e Black rot"',
        'PAIRS': [
            ('VITE', 'Peronospora', 'PERONOSPORA'),
            ('VITE', 'Botrite', 'BOTRITE'),
            ('VITE', 'Escoriosi', None),
            ('VITE', 'Black rot', None),
        ],
        'EXPECTED_NO_PAIR': [],
    },

    # -------------------------------------------------------- OLIO MINERALE (classe)
    '014386': {
        'PRODUCT': 'OLIONET',
        'FAMILY': 'G_TEXTO_CORRIDO',
        'EVIDENCE': 'bloco unico DOSI E MODALITA, uma declaracao "CULTURA: contro ..." '
                    'por grupo, cada grupo com enumeracao entre parenteses',
        'PAIRS': [
            (c, t, a)
            for grupo, alvos in [
                (['MELO', 'PERO'],
                 [('Acari', 'ACARI'), ('Afidi', 'AFIDI'), ('Cicaline', 'CICALINE'),
                  ('Cocciniglie', 'COCCINIGLIE'), ('Eriofidi', 'ERIOFIDI'),
                  ('Psille', 'PSILLE'), ('Metcalfa', 'METCALFA'),
                  ('Tignola', 'TIGNOLE'), ('uova di Lepidotteri', 'LEPIDOTTERI')]),
                (['ALBICOCCO', 'PESCO', 'CILIEGIO', 'SUSINO', 'MANDORLO'],
                 [('Afidi', 'AFIDI'), ('Acari', 'ACARI'), ('Cicaline', 'CICALINE'),
                  ('Cocciniglie', 'COCCINIGLIE'), ('Eriofidi', 'ERIOFIDI'),
                  ('Metcalfa', 'METCALFA'), ('Tripidi', 'TRIPIDI'),
                  ('uova di Lepidottero', 'LEPIDOTTERI')]),
                (['VITE'],
                 [('Acari', 'ACARI'), ('Afidi', 'AFIDI'), ('Cicaline', 'CICALINE'),
                  ('Cocciniglie', 'COCCINIGLIE'), ('Eriofidi', 'ERIOFIDI'),
                  ('Metcalfa', 'METCALFA'), ('Tignole', 'TIGNOLE'),
                  ('Tripidi', 'TRIPIDI'), ('uova di Lepidotteri', 'LEPIDOTTERI')]),
                (['OLIVO'],
                 [('Cocciniglie', 'COCCINIGLIE'), ('Tignole', 'TIGNOLE')]),
                (['NOCE', 'NOCCIOLO'],
                 [('Acari', 'ACARI'), ('Afidi', 'AFIDI'), ('Cocciniglie', 'COCCINIGLIE'),
                  ('Cicaline', 'CICALINE'), ('Cimici', 'CIMICI'),
                  ('Eriofidi', 'ERIOFIDI'), ('Metcalfa', 'METCALFA'),
                  ('Psille', 'PSILLE'), ('uova di Lepidotteri', 'LEPIDOTTERI')]),
                (['AGRUMI'],
                 [('Acari', 'ACARI'), ('Afidi', 'AFIDI'), ('Aleurodidi', 'ALEURODIDI'),
                  ('Cimice verde', 'CIMICI'), ('Cocciniglie', 'COCCINIGLIE'),
                  ('Minatori fogliari', None), ('Tripidi', 'TRIPIDI')]),
                (['COCOMERO', 'MELONE', 'ZUCCHINO', 'CETRIOLO'],
                 [('Acari', 'ACARI'), ('Afidi', 'AFIDI'), ('Aleurodidi', 'ALEURODIDI'),
                  ('Cimice verde', 'CIMICI'), ('Cocciniglie', 'COCCINIGLIE'),
                  ('Ditteri agromizidi', 'DITTERI'), ('Minatori fogliari', None),
                  ('Tripidi', 'TRIPIDI'), ('uova di Lepidotteri e Ditteri',
                                           'LEPIDOTTERI')]),
                (['PEPERONE', 'POMODORO', 'PATATA'],
                 [('Afidi', 'AFIDI'), ('Acari', 'ACARI'), ('Aleurodidi', 'ALEURODIDI'),
                  ('Ditteri agromizidi', 'DITTERI'), ('Tripidi', 'TRIPIDI'),
                  ('uova di Dorifora', 'DORIFORA'),
                  ('uova di Lepidotteri', 'LEPIDOTTERI')]),
                (['FAGIOLO'],
                 [('Afidi', 'AFIDI'), ('Acari', 'ACARI'), ('Aleurodidi', 'ALEURODIDI'),
                  ('Ditteri', 'DITTERI'), ('Tripidi', 'TRIPIDI'),
                  ('uova di Lepidotteri e Coleotteri', 'LEPIDOTTERI')]),
                (['CARCIOFO'],
                 [('Acari', 'ACARI'), ('Afidi', 'AFIDI'), ('Aleurodidi', 'ALEURODIDI'),
                  ('Ditteri', 'DITTERI'), ('Tripidi', 'TRIPIDI'),
                  ('uova di Lepidotteri', 'LEPIDOTTERI')]),
                (['BARBABIETOLA'],
                 [('Afidi', 'AFIDI'), ('adulti di Altica', 'ALTICA'),
                  ('Cassida', 'CASSIDA'), ('Mosca', 'MOSCA')]),
            ]
            for c in grupo for t, a in alvos
        ],
        'EXPECTED_NO_PAIR': [
            ('FRUMENTO', '*', 'nenhum cereal consta nos usos deste rotulo'),
        ],
        'EXPECTED_AMBIGUOUS': [
            ('CASTAGNO', 'FICO, CACO, RIBES nao pertencem ao vocabulario; a linha '
                         '"FICO, CACO, RIBES, NOCE, NOCCIOLO" sustenta NOCE e NOCCIOLO, '
                         'que enumerei, e nada alem disso'),
        ],
    },

    '012573': {
        'PRODUCT': 'EKO OIL SPRAY',
        'FAMILY': 'G_TEXTO_CORRIDO',
        'EVIDENCE': 'mesmo texto de uso de OLIONET, mais SEDANO/FINOCCHIO e '
                    'ORNAMENTALI; conferido bloco a bloco',
        'PAIRS': None,   # preenchido abaixo
        'EXPECTED_NO_PAIR': [
            ('MAIS', '*',
             'mais aparece SO na tabela de coadiuvante de diserbanti ("Mais | 2,4 D, '
             'MCPA, Bentazone"). Ali a coluna vizinha traz HERBICIDAS, nao alvos: e '
             'uma tabela de mistura, nao de uso inseticida.'),
            ('SOIA', '*', 'idem — soia so aparece na tabela de coadiuvante'),
        ],
    },
})

# APYZA WG (018156) tem exatamente as mesmas declaracoes de uso de 018165.
GABARITO['018156']['PAIRS'] = list(GABARITO['018165']['PAIRS'])
# EKO OIL SPRAY repete o corpo de usos de OLIONET.
GABARITO['012573']['PAIRS'] = list(GABARITO['014386']['PAIRS'])

# ---------------------------------------------------------------------------------
# HERBICIDAS. Aqui o alvo E "infestanti" — e a unica familia em que a frase de escopo
# produz par legitimo, porque o alvo do herbicida sao as proprias infestantes e a
# etiqueta as enumera. Para fungicida/inseticida a mesma frase declara so a cultura.
# ---------------------------------------------------------------------------------
GABARITO.update({

    '016218': {
        'PRODUCT': 'herbicida olivo/cereali',
        'FAMILY': 'SCOPE_SENTENCE_HERBICIDA',
        'EVIDENCE': '"Frumento duro: applicare ... in pre-emergenza o post-emergenza"; '
                    '"Orzo: ..."; "Olivo: applicare il prodotto in pre-emergenza o '
                    'post-emergenza precoce delle infestanti"; secao INFESTANTI '
                    'SENSIBILI enumerada por cultura',
        'PAIRS': [
            ('FRUMENTO', 'malerbe da controllare (INFESTANTI SENSIBILI su FRUMENTO)',
             'INFESTANTI'),
            ('ORZO', 'malerbe da controllare (INFESTANTI SENSIBILI su ORZO)',
             'INFESTANTI'),
            ('OLIVO', 'infestanti (INFESTANTI SENSIBILI su OLIVO)', 'INFESTANTI'),
        ],
        'EXPECTED_NO_PAIR': [
            ('LATTUGA', '*',
             '"Lactuca serriola (lattuga selvatica)" e uma INFESTANTE listada, nao a '
             'cultura LATTUGA. Promove-la a cultura inverteria o papel na frase.'),
            ('AVENA', '*',
             '"Avena sterilis (Avena)" aparece como infestante mediamente sensivel'),
        ],
    },

    '018101': {
        'PRODUCT': 'herbicida post-emergenza (1)',
        'FAMILY': 'GLOBAL_TARGET_SCOPE',
        'EVIDENCE': '"Usi autorizzati: frumento tenero e duro, segale, triticale, orzo, '
                    'avena, mais, cipolla, pomacee, drupacee, agrumi, olivo, prati e '
                    'pascoli, aree non coltivate." mais uma declaracao por cultura',
        'PAIRS': [(c, 'infestanti (elenco Infestanti sensibili / moderatamente '
                      'sensibili)', 'INFESTANTI')
                  for c in ['FRUMENTO', 'SEGALE', 'TRITICALE', 'ORZO', 'AVENA', 'MAIS',
                            'CIPOLLA', 'MELO', 'PERO', 'ALBICOCCO', 'PESCO', 'CILIEGIO',
                            'SUSINO', 'AGRUMI', 'OLIVO']],
        'EXPECTED_NO_PAIR': [
            ('BARBABIETOLA', '*',
             'barbabietola aparece so na advertencia de deriva ("Barbabietola da '
             'zucchero ... sono sensibili al prodotto"): e cultura a PROTEGER, o '
             'oposto de cultura autorizada.'),
            ('PISELLO', '*', 'idem — pisello aparece na fascia de seguranca de deriva'),
            ('PATATA', '*', 'idem'),
            ('ERBA_MEDICA', '*',
             'aparece na deriva e tambem como infestante ("erba medica (Medicago '
             'sativa)") na lista de sensiveis'),
            ('AGLIO', '*', 'aglio nao consta em "Usi autorizzati" de 018101'),
            ('NOCE', '*', 'fruttiferi a guscio nao constam em 018101'),
        ],
    },

    '016312': {
        'PRODUCT': 'herbicida post-emergenza (2)',
        'FAMILY': 'GLOBAL_TARGET_SCOPE',
        'EVIDENCE': '"Usi autorizzati: ... cipolla, aglio, pomacee, drupacee, agrumi, '
                    'olivo, nocciolo, mandorlo, noce, prati e pascoli"',
        'PAIRS': [(c, 'infestanti (elenco Infestanti sensibili / moderatamente '
                      'sensibili)', 'INFESTANTI')
                  for c in ['FRUMENTO', 'SEGALE', 'TRITICALE', 'ORZO', 'AVENA', 'MAIS',
                            'CIPOLLA', 'AGLIO', 'MELO', 'PERO', 'ALBICOCCO', 'PESCO',
                            'CILIEGIO', 'SUSINO', 'AGRUMI', 'OLIVO', 'NOCCIOLO',
                            'MANDORLO', 'NOCE']],
        'EXPECTED_NO_PAIR': [
            ('BARBABIETOLA', '*', 'so na advertencia de deriva'),
            ('PISELLO', '*', 'so na advertencia de deriva'),
            ('PATATA', '*', 'so na advertencia de deriva'),
        ],
    },

    '016823': {
        'PRODUCT': 'ACTIVUS 40 SC',
        'FAMILY': 'GLOBAL_TARGET_SCOPE',
        'EVIDENCE': 'bloco unico com uma declaracao de dose por cultura; secao '
                    'INFESTANTI SENSIBILI global (graminacee + dicotiledoni)',
        'PAIRS': [(c, 'INFESTANTI SENSIBILI (graminacee e dicotiledoni)', 'INFESTANTI')
                  for c in ['AGRUMI', 'MELO', 'PERO', 'PESCO', 'ALBICOCCO', 'CILIEGIO',
                            'SUSINO', 'VITE', 'FRAGOLA', 'AGLIO', 'CARCIOFO', 'CAVOLO',
                            'CIPOLLA', 'FRUMENTO', 'ORZO', 'GIRASOLE', 'FAGIOLO',
                            'PISELLO', 'MAIS', 'PATATA', 'PEPERONE', 'POMODORO',
                            'SOIA', 'TABACCO']],
        'EXPECTED_NO_PAIR': [
            ('LATTUGA', '*', '"Lactuca serriola (lattuga selvatica)" e infestante'),
        ],
    },

    '011243': {
        'PRODUCT': 'LEOPARD 5 EC',
        'FAMILY': 'GLOBAL_TARGET_SCOPE',
        'EVIDENCE': '"Infestanti controllate: Graminacee annuali ... poliennali ..." '
                    'declarado uma vez, e "LEOPARD 5 EC puo essere impiegato nel '
                    'diserbo delle seguenti colture", cada cultura com sua epoca',
        'PAIRS': [(c, 'Infestanti controllate (graminacee annuali e poliennali)',
                   'INFESTANTI')
                  for c in ['CAVOLO', 'POMODORO', 'MELANZANA', 'COLZA', 'TABACCO',
                            'PATATA', 'ERBA_MEDICA', 'VITE', 'MELO', 'PERO', 'PESCO',
                            'AGRUMI', 'ALBICOCCO', 'SUSINO', 'CILIEGIO',
                            'BARBABIETOLA', 'CIPOLLA', 'AGLIO', 'CAROTA', 'RAVANELLO',
                            'FAGIOLO', 'PISELLO', 'SOIA', 'GIRASOLE']],
        'EXPECTED_NO_PAIR': [
            ('AVENA', '*',
             '"Avena spp. (Avena)" esta na lista de GRAMINACEE ANNUALI controladas: '
             'e a infestante, e nao a cultura.'),
            ('RISO', '*', 'nao consta como cultura autorizada'),
        ],
    },

    '002732': {
        'PRODUCT': 'diserbante barbabietola/spinacio',
        'FAMILY': 'SCOPE_SENTENCE_HERBICIDA',
        'EVIDENCE': '"DISERBANTE SELETTIVO PER LA BARBABIETOLA DA ZUCCHERO E SPINACIO" '
                    'mais "SPETTRO D\'AZIONE ERBE INFESTANTI SENSIBILI:"',
        'PAIRS': [
            ('BARBABIETOLA', 'ERBE INFESTANTI SENSIBILI', 'INFESTANTI'),
            ('SPINACIO', 'ERBE INFESTANTI SENSIBILI', 'INFESTANTI'),
        ],
        'EXPECTED_NO_PAIR': [
            ('MAIS', '*', 'mais aparece so em AVVERTENZE AGRONOMICHE, sobre o que '
                          'semear se a cultura falhar'),
            ('PATATA', '*', 'idem'),
        ],
    },

    '007603': {
        'PRODUCT': 'diserbante barbabietola',
        'FAMILY': 'SCOPE_SENTENCE_HERBICIDA',
        'EVIDENCE': '"DISERBANTE SELETTIVO PER LA BARBABIETOLA DA ZUCCHERO" mais '
                    '"SPETTRO D\'AZIONE ERBE INFESTANTI SENSIBILI: Amaranto ..."',
        'PAIRS': [
            ('BARBABIETOLA', 'ERBE INFESTANTI SENSIBILI', 'INFESTANTI'),
        ],
        'EXPECTED_NO_PAIR': [],
    },

    '009790': {
        'PRODUCT': 'CONTATTO 320',
        'FAMILY': 'SCOPE_SENTENCE_HERBICIDA',
        'EVIDENCE': '"Viene impiegato per il diserbo di: BARBABIETOLA DA ZUCCHERO E DA '
                    'FORAGGIO - BIETOLA ROSSA:"',
        'PAIRS': [
            ('BARBABIETOLA', 'infestanti (diserbo)', 'INFESTANTI'),
        ],
        'EXPECTED_NO_PAIR': [
            ('AVENA', '*', 'avena aparece na lista de infestantes, nao como cultura'),
        ],
    },

    '013402': {
        'PRODUCT': 'LUMA KL',
        'FAMILY': 'GLOBAL_TARGET_SCOPE',
        'EVIDENCE': '"LUMA KL distrugge limacce, lumache, chiocciole e gasteropodi in '
                    'genere infestanti le colture di seguito riportate" seguido da '
                    'lista de culturas',
        'PAIRS': [(c, 'limacce, lumache, chiocciole e gasteropodi', None)
                  for c in ['MELONE', 'COCOMERO', 'CAVOLO', 'PISELLO', 'FAGIOLO',
                            'COLZA', 'GIRASOLE', 'SOIA', 'BARBABIETOLA', 'ORZO',
                            'AVENA', 'SEGALE', 'TRITICALE', 'FRUMENTO', 'MAIS',
                            'SORGO', 'FRAGOLA', 'AGLIO', 'POMODORO', 'MELANZANA',
                            'PEPERONE']],
        'EXPECTED_NO_PAIR': [],
        'NOTA': 'todos os pares deste rotulo sao VOCAB_GAP: o vocabulario controlado '
                'nao tem termo para moluscos. O rotulo autoriza; o vocabulario nao '
                'sabe dizer. Isto e lacuna de vocabulario, e nao ausencia de uso.',
    },
})

# ---------------------------------------------------------------------------------
# ZEROS ESPERADOS. Sem estes o gabarito so sabe premiar extracao, e um parser que
# afirma sempre pareceria bom. Aqui zero e a resposta CERTA.
# ---------------------------------------------------------------------------------
GABARITO.update({

    '009783': {
        'PRODUCT': 'fungicida di post raccolta agrumi',
        'FAMILY': 'GENUINE_ZERO_VOCAB_GAP',
        'EVIDENCE': '"FUNGICIDA DI POST RACCOLTA PER IL TRATTAMENTO DEGLI AGRUMI"; '
                    'o unico alvo nominado e "contro Penicillum digitatum"',
        'PAIRS': [
            ('AGRUMI', 'Penicillum digitatum', None),
        ],
        'EXPECTED_NO_PAIR': [
            ('AGRUMI', 'MALATTIE_FUNGINE',
             'a frase de titulo declara CULTURA e categoria, nao alvo'),
        ],
    },

    '017852': {
        'PRODUCT': 'POWERFILM',
        'FAMILY': 'GENUINE_ZERO',
        'EVIDENCE': 'coadiuvante (olio di colza metilestere). Nenhuma declaracao de uso '
                    'cultura x alvo em todo o documento.',
        'PAIRS': [],
        'EXPECTED_NO_PAIR': [
            ('COLZA', '*',
             '"Olio di colza metilestere" e a COMPOSICAO do produto, nao a cultura '
             'tratada. Este e o falso positivo classico deste rotulo.'),
        ],
    },

    '015592': {
        'PRODUCT': 'TAIFUN JARDIN',
        'FAMILY': 'WEED_NAMES_MISTAKEN_FOR_CROPS',
        'EVIDENCE': 'erbicida para "ROSE, VIVAI DI FLOREALI, ORNAMENTALI" — nenhuma '
                    'destas esta no vocabulario de culturas agricolas',
        'PAIRS': [],
        'EXPECTED_NO_PAIR': [
            ('AVENA', '*', '"Avena sp. (Avena)" e infestante anual listada'),
            ('RISO', '*', '"Oriza sativa var. silvatica (Riso crodo)" e o arroz '
                          'daninho, infestante'),
            ('AGLIO', '*', '"Alium sp. (Aglio selvatico)" e infestante vivaz'),
        ],
    },

    '009757_NOTA_ESCOPO': None,   # marcador removido abaixo
})
del GABARITO['009757_NOTA_ESCOPO']

# ---------------------------------------------------------------------------------
# EXCLUIDOS DO GABARITO — declarados, e nao omitidos.
# Um rotulo meio-enumerado nao mede precisao: ele inventa falso positivo. Estes sao
# tabelas-matriz de centenas de blocos cuja exaustividade eu nao consigo defender
# lendo a geometria achatada. Ficam de fora COM O MOTIVO, e o denominador da
# cobertura os conta como nao-medidos.
# ---------------------------------------------------------------------------------
EXCLUIDOS = [
    {'LABEL_ID': '008259', 'BLOCOS': 393,
     'WHY': 'matriz cultura x alvo x epoca com celulas mescladas em varias paginas; '
            'enumerar a mao sem erro nao e defensavel nesta rodada'},
    {'LABEL_ID': '013560', 'BLOCOS': 387, 'WHY': 'mesma matriz de 008259'},
    {'LABEL_ID': '004701', 'BLOCOS': 131,
     'WHY': 'multi-cultura extenso; enumeracao parcial contaminaria a precisao'},
    {'LABEL_ID': '007876', 'BLOCOS': 260, 'WHY': 'idem 004701'},
    {'LABEL_ID': '008189', 'BLOCOS': 31,
     'WHY': 'geoinseticida: a tabela alinha cultura, alvo e forma de distribuicao em '
            'colunas que o achatamento entrelaca; eu nao consegui separar as linhas '
            'com confianca suficiente para chamar de gabarito'},
    {'LABEL_ID': '008929', 'BLOCOS': 36,
     'WHY': 'a declaracao de cultura esta numa pagina que a geometria nao trouxe '
            'legivel; sem ela eu enumeraria por suposicao'},
]


def pares_planos():
    """Devolve (label, cultura, alvo_canon, alvo_raw, in_vocab) para cada par."""
    for rid, d in sorted(GABARITO.items()):
        for cult, raw, canon in d['PAIRS']:
            yield rid, cult, canon, raw, canon is not None


def resumo():
    n_lab = len(GABARITO)
    pares = list(pares_planos())
    return {
        'LABELS': n_lab,
        'PAIRS_TOTAL': len(pares),
        'PAIRS_IN_VOCAB': sum(1 for p in pares if p[4]),
        'PAIRS_VOCAB_GAP': sum(1 for p in pares if not p[4]),
        'LABELS_EXPECTED_NO_PAIR': sum(1 for d in GABARITO.values() if not d['PAIRS']),
        'EXPECTED_NO_PAIR_RULES': sum(len(d.get('EXPECTED_NO_PAIR', []))
                                      for d in GABARITO.values()),
        'EXPECTED_AMBIGUOUS_RULES': sum(len(d.get('EXPECTED_AMBIGUOUS', []))
                                        for d in GABARITO.values()),
        'EXCLUDED_LABELS': len(EXCLUIDOS),
    }


if __name__ == '__main__':
    import json
    print(json.dumps(resumo(), indent=1))


# ---------------------------------------------------------------------------------
# EQUIVALENCIAS DE ALVO DENTRO DO GABARITO
#
# Alguns alvos escritos na etiqueta admitem MAIS DE UM nome canonico igualmente
# correto, porque a etiqueta escreve nome comum e nome cientifico juntos:
#
#   "ditteri cecidomidi (Contarinia pyrivora)"  -> DITTERI e CECIDOMIA
#   "lepidotteri (Spodoptera spp.)"             -> LEPIDOTTERI e NOTTUE
#   "Muffa grigia (Botrytis cinerea)"           -> MUFFA e BOTRITE
#
# Sem esta declaracao eu estaria escolhendo um dos dois nomes e contando o outro como
# falso positivo — o mesmo erro de espaco de nomes que ja cometi uma vez com
# 'MOSCA DELLA FRUTTA' contra 'MOSCA'. Declarar aqui e honesto; escolher em silencio
# o nome que melhora o numero nao seria.
#
# ATENCAO: equivalencia NAO cria par novo. Ela so diz que, para um par de ouro ja
# enumerado, o parser acerta se devolver qualquer um dos nomes do conjunto.
ALVO_EQUIVALENTE = {
    'CECIDOMIA': {'CECIDOMIA', 'DITTERI'},
    'DITTERI': {'DITTERI', 'CECIDOMIA'},
    'LEPIDOTTERI': {'LEPIDOTTERI', 'NOTTUE'},
    'NOTTUE': {'NOTTUE', 'LEPIDOTTERI'},
    'MUFFA': {'MUFFA', 'BOTRITE'},
    'BOTRITE': {'BOTRITE', 'MUFFA'},
    'TIGNOLE': {'TIGNOLE', 'CIDIA'},
    'CARPOCAPSA': {'CARPOCAPSA', 'CIDIA', 'LEPIDOTTERI'},
    'ANARSIA': {'ANARSIA', 'LEPIDOTTERI'},
    'PIRALIDE': {'PIRALIDE', 'LEPIDOTTERI'},
    'LITOCOLLETE': {'LITOCOLLETE', 'LEPIDOTTERI'},
}


def equivalentes(canon):
    return ALVO_EQUIVALENTE.get(canon, {canon})
