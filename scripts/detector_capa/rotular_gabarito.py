import json, sys, collections as Co
sys.path.insert(0, 'curadoria'); import retrato_html as R
p = 'C:/Users/London1/detector-capa-gabarito/'
d = json.load(open(p + 'MANIFESTO.json', encoding='utf-8'))
C, M = 'CAPA', 'MATERIA'
L = {0: (C, 'pagina inicial do magazine'), 1: (M, 'noticia individual'), 2: (C, 'pagina de cortesia (site antigo), nao-materia'),
4: (C, 'pagina inicial'), 6: (C, 'pagina inicial do departamento'), 7: (C, 'calendario didactico'), 8: (C, 'arquivo de noticias'),
9: (M, 'noticia: balanco da cooperativa'), 10: (C, 'pagina inicial da revista'), 11: (C, 'pagina inicial longa (capa dificil)'),
12: (C, 'listagem de comunicados (capa dificil: CONTENT)'), 13: (C, 'pagina inicial'), 14: (M, 'noticia'), 15: (C, 'pagina inicial do evento'),
16: (M, 'pagina de um evento concreto (Reggio Calabria 8-9/08/2026)'), 17: (C, 'pagina inicial'), 18: (M, 'comunicado de imprensa longo'),
19: (C, 'indice redirigido para a pagina inicial Ri.Nova'), 21: (C, 'pagina inicial'), 22: (C, 'pagina inicial'), 23: (M, 'noticia/inquerito'),
24: (C, 'pagina inicial'), 25: (M, 'noticia'), 26: (C, 'pagina inicial'), 27: (C, 'ferramenta calendario de maturacao'),
28: (M, 'INDEX_URL que e uma pagina de evento concreto (Fiera 2026) - materia'), 29: (M, 'noticia'), 30: (C, 'pagina inicial'),
31: (C, 'arquivo'), 32: (C, 'pagina inicial longa'), 34: (C, 'pagina inicial'), 35: (M, 'projecto descrito (CSIS)'), 37: (C, 'pagina inicial'),
38: (M, 'noticia curta'), 39: (C, 'arquivo de noticias'), 40: (M, 'noticia em ingles'), 41: (C, 'pagina inicial'), 42: (C, 'chi siamo'),
43: (C, 'pagina inicial curta'), 44: (C, 'listagem de noticias'), 45: (M, 'aviso individual curto (resultados de doutoramento)'),
46: (C, 'pagina inicial'), 47: (C, 'listagem de comunicados'), 48: (C, 'pagina inicial'), 50: (C, 'pagina inicial'),
51: (M, 'projecto descrito (MRV4SOC)'), 52: (C, 'pagina inicial'), 53: (M, 'pagina de orientacoes tecnicas'),
54: (C, 'pagina inicial (com spam de apostas injectado)'), 55: (C, 'contatti'), 56: (C, 'pagina inicial de noticias'),
58: (C, 'pagina inicial do ministerio (longa)'), 60: (C, 'pagina inicial'), 61: (C, 'listagem de comunicados'), 62: (C, 'pagina inicial da revista'),
63: (M, 'artigo cientifico (resumo) curto'), 64: (C, 'listagem de noticias (CONTENT)'), 65: (M, 'noticia curta'), 66: (C, 'pagina inicial'),
69: (C, 'pagina inicial da revista'), 70: (M, 'artigo cientifico'), 71: (C, 'pagina inicial'), 73: (C, 'pagina inicial'), 74: (C, 'resultados de pesquisa'),
75: (C, 'pagina inicial'), 76: (C, 'organigrama'), 79: (C, 'listagem de noticias'), 80: (C, 'chi siamo'), 81: (C, 'listagem Ultime notizie (longa)'),
82: (M, 'aviso de concurso curto'), 83: (C, 'pagina inicial'), 84: (M, 'aviso de concurso'), 85: (C, 'pagina inicial'), 86: (M, 'publicacao/relatorio'),
87: (C, 'pagina inicial'), 88: (C, 'contatti'), 89: (C, 'arquivo de noticias'), 90: (M, 'noticia'), 91: (C, 'pagina de seccao'),
92: (M, 'noticia curta'), 93: (C, 'pagina inicial'), 94: (M, 'boletim meteorologico do dia'), 95: (C, 'pagina inicial longa'), 96: (C, 'contatti'),
97: (C, 'listagem de noticias'), 98: (M, 'noticia curta'), 99: (C, 'pagina inicial'), 100: (C, 'listagem de actos'),
101: (M, 'INDEX_URL que e uma noticia (polens) - materia curta'), 102: (C, 'pagina inicial (escolhida como materia; e capa)'),
103: (C, 'pagina de faculdade'), 104: (C, 'pagina inicial'), 105: (M, 'noticia'), 106: (C, 'pagina inicial'), 107: (C, 'pagina inicial'),
108: (M, 'aviso de concurso curto'), 109: (C, 'pagina de login, nao-materia'), 110: (C, 'pagina inicial'), 111: (M, 'aviso de concurso'),
112: (C, 'pagina inicial'), 113: (M, 'noticia'), 114: (C, 'pagina inicial'), 115: (C, 'listagem de pessoal'), 116: (C, 'pagina inicial'),
117: (M, 'projecto descrito'), 118: (C, 'pagina inicial'), 119: (M, 'aviso individual curto (plataforma funghi/tartufi)'), 121: (C, 'pagina inicial'),
122: (C, 'categoria/numero da revista'), 123: (C, 'pagina inicial'), 124: (M, 'video individual com legenda curta (TG1 riso)'),
125: (C, 'pagina inicial'), 126: (C, 'painel de alertas'), 127: (C, 'FAQ'), 128: (C, 'pagina inicial'), 129: (C, 'listagem de noticias'),
130: (C, 'pagina inicial'), 131: (C, 'portal transparencia'), 132: (C, 'seccao de transparencia'), 133: (C, 'listagem de publicacoes'),
134: (C, 'pagina de marketing generica'), 135: (C, 'pagina inicial'), 136: (C, 'chi siamo longa'), 137: (C, 'pagina inicial'), 139: (C, 'pagina inicial'),
141: (C, 'portal transparencia'), 142: (C, 'seccao de transparencia'), 143: (C, 'anagrafe (listagem)'), 144: (C, 'pagina institucional de departamento'),
145: (C, 'area reservada'), 146: (C, 'pagina inicial'), 147: (C, 'pagina inicial'), 148: (C, 'listagem de noticias'), 150: (C, 'pagina inicial'),
151: (M, 'noticia'), 152: (C, 'pagina institucional'), 153: (C, 'pagina de links'), 154: (C, 'pagina inicial'), 155: (M, 'comunicacao curta (graduatorie)'),
157: (C, 'pagina inicial'), 158: (C, 'pagina inicial'), 159: (C, 'pagina de servico (seccao)'), 161: (M, 'INDEX_URL que e uma noticia'),
162: (M, 'noticia'), 164: (C, 'contatti'), 165: (C, 'pagina institucional URP'), 166: (C, 'pagina inicial')}
AMB = {33: 'pagina de um numero de revista: indice do numero ou materia? ambigua',
       160: 'pagina de servico sobre um procedimento: nem noticia nem capa'}
pag, vistos, fora = [], {}, []
for i, x in enumerate(d['PAGINAS']):
    r = R.retrato_do_html(open(p + x['FICHEIRO'], 'rb').read())
    base = dict(ID=i, SOURCE_ID=x['SOURCE_ID'], URL=x['URL'], FICHEIRO=x['FICHEIRO'], SHA256=x['SHA256'],
                TEXT_SHA256=r['TEXT_SHA256'], EGRESSO=f"{x['EGRESSO'].get('IP')} {x['EGRESSO'].get('PAIS')}",
                QUANDO=x['QUANDO'], GRUPO=x['PAPEL_CANDIDATO'], TEXTO=r['NON_WHITESPACE_CHARACTERS'],
                PARAGRAFO=r['PARAGRAPH_CHARACTERS'], LIGACOES=r['LINKS'])
    if r['TEXT_SHA256'] in vistos:
        fora.append({**base, 'VEREDITO': 'DUPLICADA', 'PORQUE': f"mesmo texto que #{vistos[r['TEXT_SHA256']]}"}); continue
    vistos[r['TEXT_SHA256']] = i
    if r['NON_WHITESPACE_CHARACTERS'] < 500:
        fora.append({**base, 'VEREDITO': 'VAZIA', 'PORQUE': 'menos de 500 caracteres de texto (desenhada por JavaScript ou pagina tecnica)'}); continue
    if i in AMB:
        fora.append({**base, 'VEREDITO': 'AMBIGUA', 'PORQUE': AMB[i]}); continue
    v, pq = L[i]
    base['CURTA'] = v == 'MATERIA' and (r['NON_WHITESPACE_CHARACTERS'] < 1500 or r['PARAGRAPH_CHARACTERS'] < 800)
    base['LONGA'] = v == 'CAPA' and r['PARAGRAPH_CHARACTERS'] >= 800
    pag.append({**base, 'VEREDITO': v, 'PORQUE': pq})
print('gold', Co.Counter(x['VEREDITO'] for x in pag), 'fora', Co.Counter(x['VEREDITO'] for x in fora))
print('dominios', len({x['URL'].split('/')[2].removeprefix('www.') for x in pag}),
      'materias curtas', sum(x['CURTA'] for x in pag), 'capas longas', sum(x['LONGA'] for x in pag))
print('sem rotulo', [i for i in range(len(d['PAGINAS'])) if i not in L and i not in AMB and all(f['ID'] != i for f in fora)])
json.dump({'DATASET': 'GABARITO-CAPA-V1', 'MISSAO': '6-PREP-c',
           'AUTOR': 'Claude Opus 5.5, lendo titulo, texto visivel e estrutura de cada pagina. Veredito HUMANO-PROPOSTO: precisa de visto do dono.',
           'DEFINICAO': {'MATERIA': 'pagina individual com conteudo proprio: noticia, comunicado, aviso, artigo, boletim, projecto descrito',
                         'CAPA': 'pagina de entrada ou navegacao: inicio, listagem, contatti, chi siamo, calendario, arquivo, organigrama, FAQ, login, cortesia'},
           'RECOLHA': 'scripts/detector_capa/colher_gabarito.py; bytes em ~/detector-capa-gabarito/ (fora da Sala e do armazem oficial); manifesto com sha256, egresso e hora',
           'PAGINAS': pag, 'FORA_DA_CONTAGEM': fora},
          open('scripts/detector_capa/GABARITO-CAPA-V1.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
