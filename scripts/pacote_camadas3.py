#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NOTÍCIA, EVENTO, PESSOA, ACERVO, MERCADO e RELAÇÕES.

    python3 scripts/pacote_camadas3.py

⚠️ Estas camadas são as que mais tentam o inventor. Três travas:

    NOTICIA        toda linha traz `CONTENT_KIND`. «Contenuto promosso da: Bayer» é
                   BRANDED_CONTENT, não editorial, e a diferença muda a leitura.
    EVENTO         participação FUTURA nunca se infere de participação passada. Cada
                   evento traz `PARTICIPATION_STATE` por empresa.
    PESSOA         a evidência de identidade e a de papel são CAMPOS DIFERENTES. Saber
                   quem é não é saber o que faz.
"""
import json
import os
import sys
from collections import OrderedDict

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from pacote_normalizar import (git_json, local_json, grava, env, novo_id,  # noqa: E402
                               DR, ROOT)

REAL, DERIV, FACT, SYNTH, INTERNAL = ('REAL_SOURCE', 'REAL_DERIVED', 'REAL_FACT',
                                      'SYNTHETIC_DEMO', 'INTERNAL_DATA_REQUIRED')


def camada_noticias():
    N = [
        dict(pub='AgroNotizie (Image Line)', t='Mais e micotossine, un 2025 da dimenticare',
             a='Barbara Righini', d='2026-02-13', crop='MAIS', issue='micotossine',
             kind='EDITORIAL', url='https://agronotizie.imagelinenetwork.com/difesa-e-diserbo/2026/02/13/mais-e-micotossine-un-2025-da-dimenticare/88873',
             s='Fumonisinas acima de 4 mg/kg em 72% das amostras e aflatoxina B1 com 15% '
               'fora do limite, segundo dados do CREA apresentados na Giornata del Mais 2026.',
             o='texto integral preservado em data/samples/IT-T5-SENSORES/'),
        dict(pub='ADAMA Italia', t='Soluzioni innovative per la vite: dalla protezione del '
                                   'grappolo al controllo degli insetti vettori',
             a='ADAMA Italia', d='2026-04-20', crop='VITE',
             issue='peronospora + Scaphoideus titanus', kind='COMPANY_PROVIDED',
             url='https://www.adama.com/italia/it/articolo/soluzioni-innovative-la-vite-dalla-protezione-del-grappolo-al-controllo-degli-insetti',
             s='A propria ADAMA posiciona Mavrik Smart contra Scaphoideus titanus, vetor da '
               'flavescencia dourada, e a linha Folpan contra peronospora.',
             o='o artigo declara continuacao no AgroNotizie — republicacao'),
        dict(pub='ADAMA Italia', t='Orticole: come controllare le infestanti, anche quelle '
                                   'piu difficili', a='ADAMA Italia', d='2026-06-03',
             crop='ORTICOLE', issue='infestanti', kind='COMPANY_PROVIDED',
             url='https://www.adama.com/italia/it/articolo/orticole-come-controllare-le-infestanti-anche-quelle-piu-difficili',
             s='Sonavio (bifenox) posicionado como erbicida de pre-transplante.', o=''),
        dict(pub='Bayer Crop Science Italia', t='Frumento, come migliorare il controllo '
                                                'delle infestanti resistenti',
             a='Bayer Crop Science Italia', d='NAO SEI', crop='FRUMENTO',
             issue='infestanti resistentes', kind='COMPANY_PROVIDED',
             url='https://www.cropscience.bayer.it/magazine/articoli/approfondimenti/frumento-come-migliorare-il-controllo-delle-infestanti-resistenti',
             s='Concorrente posiciona Zodiac DFF citando OS DADOS DO GIRE sobre papoula, '
               'aveia e azevem resistentes.',
             o='competidor usando a autoridade independente para dar credibilidade'),
        dict(pub='Agronotizie', t='Frumento, gestione integrata delle infestanti',
             a='Tommaso Cinquemani', d='2021-02-24', crop='FRUMENTO',
             issue='resistencia a ACCasi e ALS', kind='BRANDED_CONTENT',
             url='https://www.youtube.com/watch?v=Wltg7mxV0Sw',
             s='Video com Maurizio Sattin, CNR-IPSP e membro do GIRE.',
             o='a descricao declara literalmente «Contenuto promosso da: Bayer» — '
               'e conteudo patrocinado, nao editorial'),
        dict(pub="L'Informatore Agrario", t='Infestanti resistenti della soia: le strategie '
                                            'di controllo', a="L'Informatore Agrario",
             d='2022-05-03', crop='SOIA', issue='Amaranthus resistente a ALS',
             kind='EDITORIAL', url='https://www.youtube.com/watch?v=6qXTJhz7iJY',
             s='Maurizio Sattin, coordenador do GIRE, sobre Amaranthus hybridus, '
               'tuberculatus e palmeri. No mesmo video, Belchim mostra ensaio em Verona.',
             o='editorial com demonstracao de produto de empresa dentro'),
        dict(pub='Terra e Vita (Edagricole)', t='Contro le micotossine serve l agronomia',
             a='Riccardo Bugiani e Massimo Bariselli', d='2026-04-29', crop='CEREAIS',
             issue='micotossine', kind='EDITORIAL',
             url='https://terraevita.edagricole.it/agrofarmaci-difesa/contro-le-micotossine-serve-lagronomia/',
             s='Autores do servico fitossanitario da Emilia-Romagna sobre manejo agronomico.',
             o='conteudo reservado a assinante — so o resumo publico foi lido'),
        dict(pub='Consorzio Fitosanitario di Modena', t='Cocciniglie della vite in aumento',
             a='Consorzio Fitosanitario Provinciale di Modena', d='2026-08/09', crop='VITE',
             issue='Planococcus spp.', kind='EDITORIAL',
             url='https://www.fitosanitario.mo.it/fito3/news/cocciniglie-della-vite-aumento/',
             s='O servico provincial declara aumento e explica a mecanica: geracoes '
               'exponenciais, esgotamento do efeito dos inseticidas anteriores, cobertura '
               'cerosa e o inseto dentro do cacho.',
             o='e UMA provincia. Nao representa a regiao nem o pais.'),
    ]
    fora = []
    for n in N:
        fora.append(OrderedDict([
            ('ID', novo_id('IT-NEWS')), ('PUBLISHER', n['pub']), ('TITLE', n['t']),
            ('AUTHOR', n['a']), ('DATE', n['d']),
            ('CROP', n['crop']), ('ISSUE', n['issue']), ('REGION', 'NAO SEI'),
            ('CONTENT_KIND', n['kind']),
            ('CONTENT_KIND_MEANING',
             {'EDITORIAL': 'redacao propria do veiculo',
              'BRANDED_CONTENT': 'conteudo pago/promovido por empresa, declarado na fonte',
              'COMPANY_PROVIDED': 'publicado pela propria empresa no canal dela',
              'REPUBLICATION': 'reproducao de conteudo de outro veiculo'}[n['kind']]),
            ('SINTONIA_SUMMARY', n['s']),
            ('CAVEAT', n['o'] or 'NAO SEI'),
            ('SOURCE_URL', n['url']), ('PROVENANCE', REAL)]))
    grava('NEWS', 'news.json', OrderedDict(list(env(
        'NEWS', 'pesquisa publica 2026-09-01/02', REAL,
        'Nao guardamos copia integral de materia protegida. Metadado, resumo proprio e '
        'link — o suficiente para inteligencia, sem duplicar a biblioteca de ninguem.'
    ).items()) + [('COUNT', len(fora)),
                  ('BY_KIND', {k: sum(1 for x in fora if x['CONTENT_KIND'] == k)
                               for k in {x['CONTENT_KIND'] for x in fora}}),
                  ('NEWS', fora)]))
    return fora


def camada_eventos():
    E = [
        dict(n='EIMA International 2026', d='2026-11-10 a 2026-11-14', l='BolognaFiere, Bologna',
             s='maquinas agricolas e de jardinagem', crop='TRANSVERSAL',
             u='https://www.eima.it/', org='FederUnacoma + BolognaFiere',
             exp='NAO CONSULTADA', st='FUTURO', part={},
             o='bienal. Edicao de 2024 teve 1.750 expositores de 51 paises.'),
        dict(n='Enovitis in Campo 2026', d='2026-06-17 a 2026-06-18',
             l='Tenuta di Nozzole, Greve in Chianti (FI)', s='viticultura', crop='VITE',
             u='https://www.enovitisincampo.it/', org='Unione Italiana Vini',
             exp='161 marcas, segundo a UIV', st='PASSADO',
             part={'ADAMA': 'CONFIRMADO — Stand Area B, numero B2, com Folpan Energy e '
                            'Mavrik Smart (pagina propria da ADAMA)',
                   'SYNGENTA': 'CONFIRMADO — pagina propria com formulario de inscricao'},
             o='20a edicao. Evento itinerante: o local de 2027 nao esta definido.'),
        dict(n='Fieragricola 2026', d='2026-02-04 a 2026-02-07', l='Veronafiere, Verona',
             s='agricultura geral', crop='TRANSVERSAL', u='https://www.fieragricola.it/',
             org='Veronafiere', exp='NAO CONSULTADA', st='PASSADO', part={},
             o='117a edicao, tema «Full Innovation». Bienal — a 118a e esperada em 2028. '
               'As datas de 2026 foram deslocadas por causa das Olimpiadas de inverno.'),
        dict(n='Macfrut 2026', d='2026-04-21 a 2026-04-23', l='Rimini Expo Centre, Rimini',
             s='hortifruti', crop='FRUTA E HORTALICAS', u='https://www.macfrut.com/',
             org='Cesena Fiera', exp='NAO CONSULTADA', st='PASSADO', part={},
             o='43a edicao, claim «Make it Juicy».'),
        dict(n='Vinitaly 2027', d='2027-04-11 a 2027-04-14', l='Veronafiere, Verona',
             s='vinho e destilados', crop='VITE', u='https://www.vinitaly.com/',
             org='Veronafiere', exp='NAO CONSULTADA', st='FUTURO', part={},
             o='59a edicao. A de 2026 teve 90.000 visitantes e 4.000 expositores.'),
    ]
    fora = []
    for e in E:
        fora.append(OrderedDict([
            ('ID', novo_id('IT-EVT')), ('EVENT', e['n']), ('DATE', e['d']),
            ('LOCATION', e['l']), ('SECTOR', e['s']), ('CROP_RELEVANCE', e['crop']),
            ('ORGANIZER', e['org']), ('OFFICIAL_URL', e['u']),
            ('EXHIBITOR_LIST_STATE', e['exp']),
            ('TIME_STATE', e['st']),
            ('CONFIRMED_PARTICIPATION', e['part']),
            ('PARTICIPATION_LAW', 'participacao FUTURA nunca se infere de participacao '
                                  'passada. Empresa sem linha aqui = NAO SEI.'),
            ('NOTE', e['o']), ('PROVENANCE', REAL)]))
    # ADAMA in campo
    campo = [
        ('2026-05-28', 'Campi mais SAGEA a Scalenghe (TO)', 'MAIS', 'Piemonte',
         'giornata com clientes sobre solucoes para o milho'),
        ('2026-05-28', 'Evento SATA a Rovigo', 'NAO SEI', 'Veneto', ''),
        ('2026-05-26', 'Campo cereali CAP Nord Ovest Fossano (CN)', 'CEREAIS', 'Piemonte',
         'apresentou EDAPTIS, graminicida de pos-emergencia com dois mecanismos de acao, '
         'posicionado para gestao de resistencias'),
        ('2026-05-22', 'Campo Mais Azienda Agricola Isolone (LO)', 'MAIS', 'Lombardia', ''),
        ('2026-05-21', 'Campi sperimentali dell Universita di Perugia', 'NAO SEI', 'Umbria', ''),
        ('2026-05-19', 'San Mauro Pascoli (FC) — Giornate in Campo CAI', 'NAO SEI',
         'Emilia-Romagna', ''),
        ('2026-05-18', 'Campo CAI c/o Coop. Cerealicola Colline della Murgia, Spinazzola (BT)',
         'CEREAIS', 'Puglia', ''),
        ('2026-05-15', 'Giornata del Grano — Consorzio Agrario di Ravenna, Faenza (RA)',
         'GRANO', 'Emilia-Romagna', ''),
        ('2026-05-14', 'Open Day con CAI a San Lazzaro di Savena (BO)', 'NAO SEI',
         'Emilia-Romagna', ''),
        ('2026-05-13', 'Open Day con Terremerse a San Romualdo (RA)', 'NAO SEI',
         'Emilia-Romagna', ''),
        ('2026-05-12', 'Pianeta Grano CAI a Montepulciano (SI)', 'GRANO', 'Toscana', ''),
        ('2026-05-08', 'Prove cereali con UNIBO a Bologna', 'CEREAIS', 'Emilia-Romagna', ''),
        ('2026-04-29', 'Prove cereali con SATA ad Ascoli Satriano (FG)', 'CEREAIS', 'Puglia', ''),
    ]
    for d, nome, crop, reg, nota in campo:
        fora.append(OrderedDict([
            ('ID', novo_id('IT-EVT')), ('EVENT', nome), ('DATE', d),
            ('LOCATION', reg), ('SECTOR', 'demonstracao de campo do fabricante'),
            ('CROP_RELEVANCE', crop), ('ORGANIZER', 'ADAMA Italia + parceiro local'),
            ('OFFICIAL_URL', 'https://www.adama.com/italia/it/adama-campo'),
            ('EXHIBITOR_LIST_STATE', 'NAO APLICAVEL'),
            ('TIME_STATE', 'PASSADO'),
            ('CONFIRMED_PARTICIPATION', {'ADAMA': 'CONFIRMADO — a propria ADAMA publica'}),
            ('PARTICIPATION_LAW', 'idem'),
            ('NOTE', nota or 'NAO SEI'), ('PROVENANCE', REAL)]))
    grava('EVENTS', 'events.json', OrderedDict(list(env(
        'EVENTS', ['adama.com/italia/it/adama-campo', 'pesquisa publica 2026-09-01'], REAL,
        'ADAMA IN CAMPO sao 29 no site; 13 estao aqui, os que trazem cultura ou local '
        'legivel. Os outros existem e nao foram abertos — NOT_READ, nao ausencia.'
    ).items()) + [('COUNT', len(fora)),
                  ('ADAMA_IN_CAMPO_ON_SITE', 29),
                  ('ADAMA_IN_CAMPO_HERE', len(campo)),
                  ('EVENTS', fora)]))
    return fora


def camada_pessoas():
    P = [
        ('Maurizio Sattin', 'RESEARCHER', 'CNR-IPSP', 'coordenador do GIRE',
         'nomeado na descricao de 3 videos publicos e presente no recorte OpenAlex '
         'WEED_HERBICIDE_RESISTANCE com 4 obras',
         'duas rotas independentes: video publico e indice bibliografico'),
        ('Laura Scarabel', 'RESEARCHER', 'CNR-IPSP', 'NAO SEI',
         '6 obras no recorte WEED_HERBICIDE_RESISTANCE — a maior do corte', 'OpenAlex'),
        ('Silvia Panozzo', 'RESEARCHER', 'CNR-IPSP', 'NAO SEI',
         '5 obras no mesmo recorte', 'OpenAlex'),
        ('Donato Loddo', 'RESEARCHER', 'CNR', 'membro do GIRE',
         'nomeado na descricao do video da Bayer Crop Science Italia, 36.412 views',
         'descricao de video publico'),
        ('Cristina Marzachi', 'RESEARCHER', 'CNR — Institute for Sustainable Plant Protection',
         'NAO SEI', '30 obras no recorte VINE_FLAVESCENCE — a maior', 'OpenAlex'),
        ('Luciana Galetto', 'RESEARCHER', 'CNR — IPSP', 'NAO SEI',
         '27 obras, ultima atividade 2026-07-01', 'OpenAlex'),
        ('Elisa Angelini', 'RESEARCHER', 'CREA', 'NAO SEI',
         '20 obras, ultima atividade 2026-07-30. O CREA-VE e citado no decreto do Veneto '
         'como referente scientifico das janelas de tratamento', 'OpenAlex + decreto'),
        ('Luisa Filippin', 'RESEARCHER', 'CREA', 'NAO SEI',
         '20 obras, ultima atividade 2026-07-30', 'OpenAlex'),
        ('Domenico Bosco', 'RESEARCHER', 'Universita di Torino', 'NAO SEI',
         '19 obras no recorte VINE_FLAVESCENCE, e nomeado como palestrante no convegno '
         'da Coldiretti Emilia Romagna', 'OpenAlex + convegno'),
        ('Antonio Logrieco', 'RESEARCHER', 'CNR — Institute of Sciences of Food Production',
         'NAO SEI', '27 publicacoes no recorte MAIZE_MYCOTOXIN', 'OpenAlex'),
        ('Paola Battilani', 'RESEARCHER', 'Universita Cattolica del Sacro Cuore', 'NAO SEI',
         '24 publicacoes no recorte MAIZE_MYCOTOXIN', 'OpenAlex'),
        ('Stefano Boncompagni', 'INSTITUTIONAL_EXPERT',
         'Regione Emilia-Romagna — Settore Fitosanitario e Difesa delle Produzioni',
         'responsavel do setor',
         'assina as determinacoes regionais de lotta obbligatoria e falou no convegno da '
         'Coldiretti Emilia Romagna de 26/02/2026', 'atos regionais + convegno'),
        ('Luca Casoli', 'INSTITUTIONAL_EXPERT', 'Consorzio Fitosanitario Provinciale di Modena',
         'NAO SEI', 'nomeado como palestrante do convegno Coldiretti', 'convegno'),
        ('Mirco Casagrandi', 'COMPANY_PERSON', 'ADAMA Italia',
         'Marketing Technical Manager',
         'nomeado e citado no proprio blog da ADAMA Italia, respondendo perguntas sobre '
         'amaranto resistente na soja', 'site da ADAMA'),
        ('Riccardo Castaldi', 'CREATOR', 'canal proprio de viticultura',
         'formacao declarada em Scienze Agrarie, Viticoltura ed Enologia',
         'canal YouTube @viticolturariccardocastaldi com conteudo tecnico de vite; '
         'aparece como fonte de 2 vozes de campo deste acervo', 'canal publico'),
    ]
    fora = []
    for nome, cat, org, papel, ev_id, ev_papel in P:
        fora.append(OrderedDict([
            ('ID', novo_id('IT-PER')), ('PERSON', nome), ('CATEGORY', cat),
            ('ORGANIZATION', org), ('ROLE', papel),
            ('IDENTITY_EVIDENCE', ev_id),
            ('ROLE_EVIDENCE', ev_papel),
            ('LAW', 'IDENTITY_EVIDENCE e ROLE_EVIDENCE sao coisas diferentes. Saber quem '
                    'e nao e saber o que faz.'),
            ('COUNTRY', 'IT'), ('PROVENANCE', REAL)]))
    grava('PEOPLE', 'people.json', OrderedDict(list(env(
        'PEOPLE', ['OpenAlex', 'sites oficiais', 'videos publicos'], REAL,
        'so pessoas nomeadas por fonte publica. Nenhuma inferencia de papel.'
    ).items()) + [('COUNT', len(fora)),
                  ('NOTE', 'os 60 pesquisadores do recorte estao em SCIENCE/researchers.json; '
                           'aqui ficam os que tem papel ou evidencia extra'),
                  ('PEOPLE', fora)]))
    return fora


def camada_acervo():
    itens = [
        ('SENSOR-PILOT', 'data/samples/SENSOR-PILOT/', '603 videos, 24 transcricoes, '
         '1.326 comentarios, 9 recortes', '8,1 MB', 'REAL_SOURCE'),
        ('META-EAME', 'data/samples/META-EAME/ (branch claude/eame-meta-competitor)',
         '1.340 cartoes de anuncio, 414 alcancando a Italia', '6,5 MB', 'REAL_SOURCE'),
        ('REGULATORIO IT', 'data/samples/IT-T4-001/ (branch claude/adama-it-local-catalog)',
         '163 registros vigentes, 163 rotulos parseados', '1,2 MB', 'REAL_FACT'),
        ('CATALOGO ADAMA IT', 'data/samples/IT-CATALOGO/', '51 produtos, 141 documentos',
         '620 KB', 'REAL_SOURCE'),
        ('BOLETINS DE CAMPO', 'data/samples/IT-T5-SENSORES/', '6 boletins em texto integral '
         '+ LaMMA Grosseto', '95 KB', 'REAL_SOURCE'),
        ('PIEMONTE FLAVESCENZA', 'data/samples/PIEMONTE-FD/ + data/raw/IT/PIEMONTE-FD/',
         '8 documentos oficiais; texto no Git, PDF fora', '11,4 MB', 'REAL_FACT'),
        ('CORPUS PESQUISADOR', 'data/samples/RESEARCHER-CORPUS-EAME-V1.json',
         '763 materiais, 582 como evidencia, 12 identidades provadas', '2,1 MB',
         'REAL_SOURCE'),
        ('CIENCIA POR RECORTE', 'data/samples/IT-CIENCIA/IT-CIENCIA-UNIVERSO-V1.json',
         '5 recortes, 320 obras, 876 autores italianos', '76 KB', 'REAL_SOURCE'),
        ('GIRE', 'data/samples/IT-CIENCIA/IT-GIRE-RESISTENCIA-V2.json',
         '23 fichas, 34 linhas de resistencia', '168 KB', 'REAL_FACT'),
        ('CAMADA UE', 'data/samples/IT-REGUA/IT-ADAMA-EU-ACTIVE-SUBSTANCE-V2.json',
         '15 atos lidos e verificados por refutador', '192 KB', 'REAL_FACT'),
        ('PARES CULTURA x ALVO', 'data/samples/IT-REGUA/IT-PARES-CULTURA-ALVO-V0.json',
         '46 pares do corpus de video/comentario', '127 KB', 'REAL_DERIVED'),
        ('PRECO UE', 'data/samples/IT-MERCADO/', 'cereal 16.193 registros, azeite 23.387',
         '35 KB (resumo; a serie completa se rebusca pela API)', 'REAL_SOURCE'),
    ]
    fora = [OrderedDict([('ID', novo_id('IT-ARC')), ('DATASET', n), ('REPO_PATH', p),
                         ('CONTENT', c), ('SIZE', s), ('PROVENANCE', pr)])
            for n, p, c, s, pr in itens]
    grava('ARCHIVE', 'archive-index.json', OrderedDict(list(env(
        'ARCHIVE_INDEX', 'repositorio eame-sintonia', DERIV,
        'PONTEIRO, nao copia. O bruto pesado fica no repositorio; o pacote leva o caminho.'
    ).items()) + [('COUNT', len(fora)),
                  ('REPO', 'https://github.com/lucianodalondon-sys/eame-sintonia'),
                  ('WARNING', 'varios destes vivem em OUTRAS branches. A lista diz qual.'),
                  ('DATASETS', fora)]))
    return fora


if __name__ == '__main__':
    os.makedirs(DR, exist_ok=True)
    print('CAMADA NOTICIAS'); camada_noticias()
    print('CAMADA EVENTOS'); camada_eventos()
    print('CAMADA PESSOAS'); camada_pessoas()
    print('CAMADA ACERVO'); camada_acervo()
    print('\nok')
