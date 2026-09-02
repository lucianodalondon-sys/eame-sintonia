#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ESCREVE O `LAST-MILE-REALITY-GAPS.md` — a entrega em prosa do §12.

    python3 scripts/lastmile_relatorio.py

Lê os três JSON já montados e escreve o relatório com os dez contadores que a
missão pede, o que mudou em cada família, e as duas listas finais: o dado novo
mais importante para o demo, e os dez cruzamentos que agora ficam possíveis.

⚠️ O QUE ESTE RELATÓRIO NÃO PODE ESCONDER
------------------------------------------
A taxa de derrubada da conferência. Foram 14 blocos, cada um com uma amostra
levada a um segundo agente com ordem de **derrubar**. Muitos caíram. Se o
relatório mostrar só o que sobreviveu, ele mente por omissão sobre a qualidade
da coleta — e a próxima pessoa confiará mais do que deve.

    UMA COLETA SEM TAXA DE ERRO PUBLICADA É UMA COLETA SEM TAXA DE ERRO MEDIDA.
"""
import json
import os
from collections import Counter, defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SAIDA = os.path.join(ROOT, 'research', 'italy-lastmile')
LM = os.path.join(ROOT, 'data', 'samples', 'IT-LASTMILE')

REGIOES_IT = ['Abruzzo', 'Basilicata', 'Calabria', 'Campania', 'Emilia-Romagna',
              'Friuli-Venezia Giulia', 'Lazio', 'Liguria', 'Lombardia', 'Marche',
              'Molise', 'Piemonte', 'Puglia', 'Sardegna', 'Sicilia', 'Toscana',
              'Trentino-Alto Adige', 'Umbria', "Valle d'Aosta", 'Veneto']


def le(n):
    p = os.path.join(SAIDA, n)
    return json.load(open(p, encoding='utf-8')) if os.path.exists(p) else {}


def main():
    gaps = le('LAST-MILE-REALITY-GAPS.json')
    dados = le('NEW-REAL-DATA.json')
    fontes = le('NEW-REAL-SOURCES.json')
    inv = json.load(open(os.path.join(LM, 'IT-LASTMILE-INVENTARIO.json'),
                         encoding='utf-8'))
    cat = json.load(open(os.path.join(LM, 'IT-ADAMA-CATALOGO.json'), encoding='utf-8'))

    R = dados.get('REGISTROS', [])
    porb = dados.get('POR_BLOCO', {})

    # ── conferência: a taxa que não pode sumir ───────────────────────────────
    ver_t = ver_c = 0
    por_bloco_conf = {}
    for f in gaps.get('FAMILIAS', []):
        c = f.get('CONFERENCIA') or {}
        if c.get('verificados'):
            ver_t += c['verificados']
            ver_c += c.get('confirmados', 0)
            por_bloco_conf[f['FAMILIA']] = (c.get('confirmados', 0), c['verificados'])

    # ⚠️ REGIAO DE ONDE VEM O BOLETIM, nao regiao MENCIONADA no texto.
    # A primeira versao somava qualquer nome de regiao que aparecesse no texto do
    # registro -- e o boletim NACIONAL do CREA cita «Sicilia e Sardegna» numa
    # frase. Com isso o relatorio anunciou «0 regioes sem boletim», o que e falso.
    #
    #     REGIAO CITADA NAO E REGIAO COBERTA. E a mesma lei de CROP_TERM_PRESENT,
    #     em forma de geografia.
    #
    # Agora so conta o campo `region` do proprio registro, e so se ele for CURRENT.
    regs = set()
    for r in R:
        if r.get('BLOCO') not in ('fenologia', 'boletins-regioes-fechadas'):
            continue
        # ⚠️ DUAS TRAVAS, e a segunda e a que a missao exigiu em letra:
        # «Do not infer current presence from historical seasonality».
        # Aceitar classe VAZIA como corrente seria deixar entrar boletim sem
        # rotulo. E CURRENT sem data de ago/set de 2026 nao e corrente em 02/09.
        if (r.get('observation_class') or '').upper() != 'CURRENT':
            continue
        data = str(r.get('publication_date') or '')
        if not (data.startswith('2026-08') or data.startswith('2026-09')
                or '/08/2026' in data or '/09/2026' in data):
            continue
        t = (r.get('region') or '').lower()
        if not t:
            continue
        for reg in REGIOES_IT:
            chave = reg.split()[0].split('-')[0].lower()
            if chave in t:
                regs.add(reg)
    antes = set(inv['FAMILIAS'][0]['TEM']['REGIOES_ALCANCADAS'])
    novas = sorted(regs - antes)
    faltam = sorted(set(REGIOES_IT) - antes - regs)

    L = []
    A = L.append
    A('# LAST-MILE REALITY GAPS — SINTONIA ITALY\n\n')
    A('**02/09/2026** · missão executada com inventário antes da coleta (§11)\n\n')
    A('> Nenhum dado interno. Nenhuma estimativa de receita ou de participação de '
      'mercado. Nenhuma chamada paga — as duas chaves Apify seguem esgotadas.\n')
    A('\n---\n\n## SUMÁRIO DA MISSÃO\n\n```\n')
    # ⚠️ o numero de cobertura precisa vir com a ressalva COLADA, senao mente.
    # De 12 regioes sem nada passamos a 1 -- mas muitos boletins novos sao
    # PROVINCIAIS ou de AREAL. Campania sao cinco documentos provinciais
    # separados; Basilicata cobre so o Metapontino; Sardegna so Oristano;
    # Trentino so a provincia de Trento, e o Sudtirol -- maior area de maca da
    # Italia -- continua sem fonte lida.
    #
    #     BOLETIM PROVINCIAL NAO REPRESENTA A REGIAO. Cobertura nao e censo.
    prov = sum(1 for r in R
               if r.get('BLOCO') in ('fenologia', 'boletins-regioes-fechadas')
               and any(w in (r.get('region') or '').lower()
                       for w in ('provinc', 'areal', 'area ', 'zona', 'lago')))
    A('CURRENT FIELD SIGNAL GAPS   = %d regiao de 20 sem NENHUM boletim '
      'corrente (eram 12)\n' % len(faltam))
    A('                              ATENCAO: %d dos boletins novos sao '
      'PROVINCIAIS ou de AREAL\n' % prov)
    A('                              e NAO representam a regiao.\n')
    A('MARKET GAPS                 = %d de 10 culturas do piloto ainda sem mercado '
      '(eram 7)\n' % 1)
    A('CROP ECONOMIC WEIGHT GAPS   = 0 para 15 culturas · era a lacuna TOTAL\n')
    A('CATALOG GAPS                = 0 no numero · 51 fichas lidas, 5 SPECIALI '
      'confirmados\n')
    A('REGULATORY FUTURE SIGNALS   = %d registros · 4 sinais de risco NOMEADOS em ata\n'
      % porb.get('regulatorio', 0))
    A('WEATHER SOURCES FOUND       = 17 testadas · 13 abertas · era lacuna TOTAL\n')
    A('COMPETITOR NEW PUBLIC SIGNALS = %d, nenhum vindo de anuncio pago\n'
      % porb.get('concorrente', 0))
    A('HIGH-CONFIDENCE FIELD VOICES  = 18 pessoas com nome, cargo provado e frase '
      'assinada\n')
    A('HERBICIDE GAPS CLOSED       = a janela corrente e POST-RACCOLTA, nao '
      'pre-semeadura\n')
    A('FUTURE EVENTS FOUND         = %d · 13 deles novos e datados\n'
      % porb.get('eventos', 0))
    A('\n')
    A('REGISTROS NOVOS             = %d\n' % len(R))
    A('FONTES NOVAS                = %d\n' % fontes.get('COUNT', 0))
    A('EXIGEM ROTA ITALIANA        = %d registros\n'
      % dados.get('EXIGEM_ROTA_ITALIANA', 0))
    A('SINTETICOS                  = 0\n')
    A('```\n')

    # ── a taxa de erro, em destaque ──────────────────────────────────────────
    A('\n---\n\n## ⚠️ A TAXA DE ERRO DA COLETA — leia antes dos números\n\n')
    A('Cada bloco teve uma amostra levada a um segundo agente com a ordem de '
      '**derrubar o registro**, não de confirmá-lo.\n\n')
    A('| | |\n|---|---:|\n')
    A('| registros levados à conferência | **%d** |\n' % ver_t)
    A('| sobreviveram | **%d** |\n' % ver_c)
    A('| **caíram** | **%d (%.0f%%)** |\n'
      % (ver_t - ver_c, 100.0 * (ver_t - ver_c) / max(1, ver_t)))
    A('\n> **Uma coleta sem taxa de erro publicada é uma coleta sem taxa de erro '
      'medida.** Um em cada três registros amostrados não resistiu ao confronto com '
      'a fonte. Os motivos mais comuns foram: valor deslocado de linha na tabela, '
      'lista incompleta que escondia o dado divergente, e rótulo de unidade que a '
      'fonte não dá.\n\n')
    A('Por bloco:\n\n| bloco | sobreviveram |\n|---|---|\n')
    for k, (c, t) in sorted(por_bloco_conf.items(), key=lambda x: x[1][0] / max(1, x[1][1])):
        A('| %s | %d de %d |\n' % (k, c, t))

    # ── a correção de rota ───────────────────────────────────────────────────
    cr = gaps.get('CORRECAO_DE_ROTA')
    if cr:
        A('\n---\n\n## ⚠️ CORREÇÃO — o que a VPN explica, e o que ela não explica\n\n')
        A('%s\n\n' % cr['O_QUE_ACONTECEU'])
        A('> **%s**\n\n' % cr['LEI'])
        A('Medido antes e depois, com a previsão escrita **antes** de a VPN subir:\n\n')
        A('| fonte | sem VPN | com VPN italiana | família |\n|---|---|---|---|\n')
        for m in cr['MEDIDO_ANTES_E_DEPOIS']:
            A('| %s | %s | **%s** | %s |\n'
              % (m['FONTE'], m['SEM_VPN'], m['COM_VPN_IT'], m['FAMILIA']))
        A('\n**Não mudou com a VPN** — e cada um por um motivo diferente, que não é '
          'geografia: %s.\n' % ', '.join(cr['NAO_MUDOU_COM_A_VPN']))
        A('\n⚠️ E uma correção ao meu próprio diagnóstico: eu classifiquei '
          '`regione.veneto.it` como «conexão cortada». **Está errado.** O servidor '
          'manda a cadeia de certificado incompleta — falta o intermediário — e o '
          'Python recusa. Não é geografia, não é robô: é certificado. O Veneto foi '
          'alcançado assim mesmo, por outra rota.\n')

    # ── família por família ──────────────────────────────────────────────────
    A('\n---\n\n## O QUE MUDOU, FAMÍLIA POR FAMÍLIA\n')
    for f in gaps.get('FAMILIAS', []):
        A('\n### %s\n\n' % f['FAMILIA'])
        A('- **classe no inventário:** `%s`\n' % f['CLASSE_NO_INVENTARIO'])
        A('- **por que era lacuna:** %s\n' % f['POR_QUE_ERA_LACUNA'])
        A('- **coletado agora:** %d registros · %d fontes novas\n'
          % (f['COLETADO_AGORA'], f['FONTES_NOVAS']))
        if f.get('RESULTADO'):
            A('\n%s\n' % f['RESULTADO'][:1400])
        if f.get('LACUNAS_QUE_FICARAM'):
            A('\n**O que ficou de fora:**\n\n%s\n' % f['LACUNAS_QUE_FICARAM'][:1200])
        if f.get('RECEITA_PARA_REFAZER'):
            A('\n<details><summary>receita para refazer</summary>\n\n```\n%s\n```\n'
              '</details>\n' % f['RECEITA_PARA_REFAZER'][:1800])

    # ── o catálogo ───────────────────────────────────────────────────────────
    A('\n---\n\n## §4 · O CATÁLOGO COMERCIAL, E O QUE ELE REVELOU\n\n')
    A('A listagem por categoria está atrás de Akamai Bot Manager (`Access Denied`, '
      '`bm-verify`, 403 até no `robots.txt`). **Não foi contornada.** O catálogo veio '
      'por dois caminhos abertos: as sete páginas de cultura do site, e a sitemap '
      'oficial.\n\n')
    A('| categoria | pela ficha impressa |\n|---|---:|\n')
    A('| Erbicidi | 26 |\n| Fungicidi | 14 |\n| Insetticidi | 6 |\n'
      '| **Speciali** | **5** |\n| **total** | **51** |\n')
    A('\n**Os 5 SPECIALI confirmados:** Brevis · Budge · Exelgrow · Parleaf · '
      'Powerfilm.\n\n')
    A('### ⭐ O achado que muda o mapa do portfólio\n\n')
    A('**Seis produtos do catálogo ADAMA têm a autorização fitossanitária em nome de '
      'OUTRA empresa**, confirmado na busca pública do Ministero:\n\n')
    A('| produto | titular do registro |\n|---|---|\n')
    for p, t in [('Mirador SC', 'SYNGENTA CROP PROTECTION AG'),
                 ('Mavita 250 EC', 'SYNGENTA CROP PROTECTION AG'),
                 ('Zakeo 250 SC', 'SYNGENTA CROP PROTECTION AG'),
                 ('Timeline Trio', 'SYNGENTA CROP PROTECTION AG'),
                 ('Clematis', 'ALBAUGH TKI D.O.O'),
                 ('Parleaf', 'MICROCIDE LTD')]:
        A('| %s | %s |\n' % (p, t))
    A('\nEles sumiam do corpus porque **os 163 foram filtrados por titular ADAMA**. '
      'Ou seja: o universo comercial da ADAMA Itália é maior que o universo '
      'regulatório em nome dela.\n\n')
    A('E mais dois — **Budge e Exelgrow** — nem são fitossanitários: carregam número '
      'de registro de fertilizante. São bioestimulantes.\n\n')
    A('⚠️ **Um erro de método vale a pena registrar:** o segmento da URL **não é** a '
      'categoria. `Folpan Energy` mora em `/prodotti/erbicidi/` e a ficha o rotula '
      '**Fungicidi**. Contar pelo caminho daria 27/13/6/5 em vez de 26/14/6/5.\n')

    # ── o que é mais importante para o demo ──────────────────────────────────
    A('\n---\n\n## MOST IMPORTANT NEW REAL DATA FOR CLIENT DEMO\n\n')
    for i, (t, d) in enumerate([
        ('O peso econômico de cada cultura, por região',
         '983 linhas do ISTAT (cubo `101_1015 Coltivazioni`): 20 regiões + Itália, '
         '15 culturas, 2024–2026, área em hectares e produção em quintais. Passou o '
         'teste de censo: a soma das 20 regiões bate com o total nacional. Agora o '
         'portal separa «praga em 200 ha» de «praga em 200 mil ha» — trigo duro tem '
         '1.134.227 ha, e a barbabietola tem 18.680 ha em toda a Itália.'),
        ('O Vêneto deixou de ser um vazio',
         'O demo tem três casos no Vêneto e o pacote não tinha um boletim. Agora tem '
         'boletins do Servizio Fitosanitario de agosto e setembro de 2026 — vite '
         '27/08, olivo 02/09, frutícola e hortícola 26/08.'),
        ('O calendário de vencimento ganhou causa europeia',
         '39 das 50 substâncias do portfólio (78%) estão em aprovação PRORROGADA — '
         'já venceu uma vez e foi esticada. E os agrupamentos italianos ficam '
         'explicados: nov/26 = 9 metamitron + 2 flonicamid; jan/27 = 10 pendimethalin '
         '+ 5 bupirimate + 7 tau-fluvalinate.'),
        ('Quatro sinais de risco NOMEADOS em ata pública',
         'Não-renovação em rascunho para **fludioxonil** (comentários até 03/09/2026) '
         'e **fenmedifam**; revisão do Artigo 21 aberta sobre **tebuconazol** por '
         'classificação Tóxico para Reprodução 1B; e a Comissão registrando que para '
         '**clodinafop** uma não-renovação «provavelmente seria proposta». '
         '⚠️ Prorrogação não é renovação, e nenhum destes é decisão tomada.'),
        ('A janela de herbicida corrente não era a que se supunha',
         'Em 02/09/2026 a única janela de diserbo comprovadamente aberta nos cereais '
         'de outono é a de **post-raccolta** (restolho), não pré-semeadura nem '
         'pré-emergência. Sai de boletim oficial datado de 19–20/08/2026.'),
        ('Dezoito vozes com nome, cargo provado e frase assinada',
         'Antes havia 58 falas de caixa de comentário e 15 pessoas sem nenhuma '
         'declaração. Agora há agricultores, dirigentes de organização, agrônomos, '
         'presidentes de consórcio e o serviço técnico do órgão nacional do arroz.'),
        ('Preço corrente para 6 das 7 culturas que estavam zeradas',
         'Só a barbabietola continua sem. E o ISMEA — a autoridade do setor — falou '
         'com este projeto pela primeira vez.'),
        ('Seis produtos do catálogo registrados em nome de outra empresa',
         'O universo comercial é maior que o regulatório filtrado por titular ADAMA.'),
    ], 1):
        A('\n**%d. %s**\n\n%s\n' % (i, t, d))

    # ── os dez cruzamentos ───────────────────────────────────────────────────
    A('\n---\n\n## TOP 10 NEW CROSSINGS NOW POSSIBLE\n\n')
    A('Cada um só existe porque **duas** camadas novas se encontraram. Nenhum é uma '
      'afirmação: são perguntas que o portal agora consegue formular com lastro.\n\n')
    for i, (c, o) in enumerate([
        ('convergência × peso econômico da região',
         '«este par cultura×alvo aparece numa região que responde por N% da área '
         'italiana da cultura» — antes o portal não sabia se a região era grande'),
        ('vencimento nacional × aprovação europeia × prorrogação',
         'os 101 produtos que vencem em 12 meses agora se separam entre os que '
         'dependem de substância prorrogada e os que não'),
        ('sinal de não-renovação × produtos do portfólio × cultura',
         'fludioxonil, fenmedifam, tebuconazol e clodinafop puxam produtos e culturas '
         'concretas'),
        ('boletim corrente do Vêneto × os três casos do demo no Vêneto',
         'pela primeira vez o caso tem evidência de campo da própria região'),
        ('janela de diserbo declarada × fase fenológica × produto de rótulo',
         'a janela post-raccolta cruza com os herbicidas autorizados para ela'),
        ('resistência GIRE × janela corrente × mecanismo do produto',
         'arroz × Echinochloa × ACCase, com a janela datada'),
        ('voz identificada × par cultura×alvo × região',
         'uma frase assinada por alguém com cargo, sobre o mesmo par que a régua achou'),
        ('clima como CONDIÇÃO × região × cultura',
         '⚠️ e só como condição — nunca como presença de doença'),
        ('catálogo comercial × registro × titular',
         'o que a ADAMA vende, o que está registrado, e em nome de quem'),
        ('evento futuro × concorrente × cultura',
         'quem estará onde, quando a fonte publica — nunca inferido do ano passado'),
    ], 1):
        A('%d. **%s** — %s\n' % (i, c, o))

    # ── o que continua faltando ──────────────────────────────────────────────
    A('\n---\n\n## O QUE CONTINUA FALTANDO, E POR QUÊ\n\n')
    A('| lacuna | motivo | é esforço ou é natureza? |\n|---|---|---|\n')
    A('| %d regiões sem boletim corrente | fonte fora do ar, DNS morto ou só imagem | '
      'esforço — as portas estão listadas |\n' % len(faltam))
    A('| **frumento duro: zero boletim** | em ago/set já foi colhido; e a fonte da '
      'maior produtora descontinuou a fitopatologia em 2018 | **natureza** — a coleta '
      'certa é entre novembro e junho |\n')
    A('| barbabietola sem mercado | nenhuma fonte pública encontrada | esforço |\n')
    A('| pomodoro sem área regional | ISTAT tem, mas a chamada não voltou com corte '
      'regional | esforço |\n')
    A('| olivo e melo: área só por macro-área e de 2017 | o corte regional não existe '
      'nessa fonte | esforço — o ISTAT tem `OLIVTAB_OIL` e `APPLE` |\n')
    A('| Sicília sem boletim regional | o SIAS não abre em HTTPS | esforço |\n')
    A('| venda, share, estoque | dado interno, e o projeto é externo por decisão | '
      '**natureza** |\n')
    A('\n**Região ainda sem nenhum boletim corrente:** %s.\n'
      % (', '.join(faltam) or 'nenhuma'))
    A('\n⚠️ **A ressalva que o número esconde:** de 12 regiões sem nada '
      'passamos a 1. Mas **muitos dos boletins novos são PROVINCIAIS ou de '
      'AREAL** — a Campânia são cinco documentos provinciais separados, a '
      'Basilicata cobre só o Metapontino, a Sardenha só Oristano, e o Trentino '
      'só a província de Trento (o Sudtirol, maior área de maçã da Itália, '
      'continua sem fonte lida). `BOLETIM PROVINCIAL NÃO REPRESENTA A REGIÃO.` '
      'A cobertura subiu; o censo, não.\n')
    if novas:
        A('\n**Regiões alcançadas nesta missão:** %s.\n' % ', '.join(novas))

    A('\n---\n\n## OS ARQUIVOS\n\n```\n')
    A('research/italy-lastmile/LAST-MILE-REALITY-GAPS.md    este relatorio\n')
    A('research/italy-lastmile/LAST-MILE-REALITY-GAPS.json  as lacunas, por familia\n')
    A('research/italy-lastmile/NEW-REAL-DATA.json           %d registros\n' % len(R))
    A('research/italy-lastmile/NEW-REAL-SOURCES.json        %d fontes, estado MEDIDO\n'
      % fontes.get('COUNT', 0))
    A('data/samples/IT-ISTAT-COLTIVAZIONI/                  983 linhas de area/producao\n')
    A('data/samples/IT-LASTMILE/IT-ADAMA-CATALOGO.json      catalogo comercial\n')
    A('data/samples/IT-LASTMILE/IT-ROTA-*.json              o teste de rota, antes e depois\n')
    A('```\n')

    p = os.path.join(SAIDA, 'LAST-MILE-REALITY-GAPS.md')
    open(p, 'w', encoding='utf-8').write(''.join(L))
    print('gravado: %s · %.0f KB' % (os.path.relpath(p, ROOT),
                                     os.path.getsize(p) / 1024))
    print('conferencia: %d de %d sobreviveram (%.0f%% caiu)'
          % (ver_c, ver_t, 100.0 * (ver_t - ver_c) / max(1, ver_t)))
    print('regioes ainda sem boletim: %d · alcancadas agora: %d'
          % (len(faltam), len(novas)))


if __name__ == '__main__':
    main()
