#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
§19 · O RELATÓRIO DE ACEITAÇÃO — todo número medido, nenhum lembrado.

    python3 scripts/v21_aceitacao.py

POR QUE ESTE ARQUIVO NÃO É UM MARKDOWN ESCRITO À MÃO
-----------------------------------------------------
Porque relatório escrito à mão envelhece em silêncio. O número entra certo no dia
em que se escreve, o pacote muda na semana seguinte, e o relatório continua
afirmando o antigo com a mesma cara de confiança.

    NÚMERO QUE NÃO SE RECALCULA É NÚMERO QUE VAI MENTIR ALGUM DIA.
    A ÚNICA DÚVIDA É QUANDO.

Então aqui se conta tudo de novo, dos arquivos, toda vez. Se um contador
diverge do que o pacote afirma sobre si mesmo, o relatório mostra os dois lados
em vez de escolher um.

O QUE ESTE RELATÓRIO NÃO FAZ
-----------------------------
Ele não aprova o pacote. Ele mede. Quem aprova é quem lê — e para isso precisa
dos números, inclusive os que constrangem.
"""
import json
import os
import re
import sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
V21 = os.path.join(ROOT, 'build', 'ITALY-REALITY-HANDOFF-V2.1')
ING = os.path.join(V21, 'DESIGN-INGEST')
ARQ = os.path.join(V21, 'INTERNAL-ARCHIVE')

sys.path.insert(0, os.path.join(ROOT, 'scripts'))
from v21_campos_de_lingua import (LEITURA, MISTO, campos_do_registro,  # noqa
                                  parte_minha, e_portugues)

SAFE_OK = {'QA_PASS', 'QA_CORRECTED', 'EVIDENCE_DOCUMENTED', 'EVIDENCE_SOURCED'}
SAFE_NAO = {'QA_UNREVIEWED', 'QA_REJECTED', 'EVIDENCE_DERIVED'}


def colecoes():
    for a in sorted(os.listdir(ING)):
        if not a.endswith('.json') or a in ('APP-MANIFEST.json',
                                            'CANONICAL-INTELLIGENCE-MASTER.json'):
            continue
        d = json.load(open(os.path.join(ING, a), encoding='utf-8'))
        if isinstance(d, dict) and isinstance(d.get('RECORDS'), list):
            yield a, d


def main():
    r = {}
    # A identidade de build vem do pacote, nao deste script: o carimbo e feito no
    # passo 7b e este relatorio so o REPETE. Assim o relatorio nunca declara um
    # build diferente do que esta nos arquivos.
    _m = os.path.join(ING, 'APP-MANIFEST.json')
    if os.path.exists(_m):
        r['BUILD_ID'] = json.load(open(_m, encoding='utf-8')).get('BUILD_ID')

    # ── 1 · o registro central ───────────────────────────────────────────────
    m = json.load(open(os.path.join(ING, 'CANONICAL-INTELLIGENCE-MASTER.json'),
                       encoding='utf-8'))
    r['MASTER'] = {
        'RECORDS_TOTAL': m['COUNT_TOTAL'],
        'RECORDS_CLIENT_SAFE': m['COUNT_CLIENT_SAFE'],
        'DUPLICATE_IDS': len(m['DUPLICATE_IDS']),
        'BY_ORIGIN': m['BY_ORIGIN'],
        'VIEWS_NOT_INDEXED': m.get('VIEWS_NOT_INDEXED', []),
    }

    # ── 2 · o portão de QA, conferido registro a registro ────────────────────
    quebras, sem_carimbo, por_arq = [], 0, {}
    for a, d in colecoes():
        real = sum(1 for x in d['RECORDS'] if isinstance(x, dict) and x.get('ID'))
        safe = sum(1 for x in d['RECORDS']
                   if isinstance(x, dict) and x.get('CLIENT_SAFE'))
        por_arq[a] = {'TOTAL': real, 'CLIENT_SAFE': safe,
                      'DECLARADO_TOTAL': d.get('COUNT_TOTAL'),
                      'DECLARADO_SAFE': d.get('COUNT_CLIENT_SAFE')}
        for x in d['RECORDS']:
            if not isinstance(x, dict) or not x.get('ID'):
                continue
            q, s = x.get('QA_STATUS'), bool(x.get('CLIENT_SAFE'))
            if q is None:
                sem_carimbo += 1
                continue
            if s and q in SAFE_NAO:
                quebras.append({'ARQUIVO': a, 'ID': x['ID'], 'QA': q,
                                'ERRO': 'CLIENT_SAFE=true com QA inseguro'})
            if (not s) and q in SAFE_OK:
                # ── R5 · O PORTAO GANHA UMA SEGUNDA CONDICAO, E SO APERTA ─────
                # Ate aqui CLIENT_SAFE era funcao PURA do QA_STATUS: «a evidencia
                # aguenta?». Faltava a outra pergunta: «a alegacao e sobre o
                # mundo?». Um registro pode ser verdadeiro, documentado e
                # verificavel — e ainda assim nao sustentar afirmacao nenhuma ao
                # cliente, porque nao fala do mercado italiano: fala de como o
                # coletor chegou la.
                #
                #     CLIENT_SAFE = a evidencia aguenta E a alegacao e sobre o mundo.
                #
                # Repare no sentido da mudanca: a condicao nova faz MENOS coisa
                # passar, nunca mais. Portao que se reabre para deixar passar e
                # outra coisa, e essa continua proibida.
                if x.get('CLAIM_DOMAIN') == 'SOURCE_ACCESS' and x.get('CLIENT_SAFE_WHY_NOT'):
                    continue
                quebras.append({'ARQUIVO': a, 'ID': x['ID'], 'QA': q,
                                'ERRO': 'CLIENT_SAFE=false com QA seguro'})
    r['QA_GATE'] = {
        'LEI': ('CLIENT_SAFE = a evidencia aguenta (QA_STATUS) E a alegacao e '
                'sobre o mundo (CLAIM_DOMAIN). A segunda condicao entrou em R5 e '
                'so aperta: um registro sobre a rota de coleta nao sustenta '
                'afirmacao ao cliente nem com a melhor evidencia.'),
        'REBAIXADOS_POR_DOMINIO': [
            x['ID'] for _a, _d in colecoes() for x in _d['RECORDS']
            if isinstance(x, dict) and x.get('CLAIM_DOMAIN') == 'SOURCE_ACCESS'],
        'VIOLACOES': len(quebras),
        'DETALHE': quebras[:40],
        'SEM_QA_STATUS': sem_carimbo,
        'CONTAGEM_DECLARADA_DIVERGE': [
            {'ARQUIVO': k, **v} for k, v in por_arq.items()
            if v['DECLARADO_TOTAL'] not in (None, v['TOTAL'])
            or v['DECLARADO_SAFE'] not in (None, v['CLIENT_SAFE'])],
    }
    r['POR_COLECAO'] = por_arq

    # ── 3 · os cruzamentos, reprovados do zero ───────────────────────────────
    idx, qa = {}, {}
    for a, d in colecoes():
        for x in d['RECORDS']:
            if isinstance(x, dict) and x.get('ID'):
                idx.setdefault(x['ID'], []).append((a, x))
                qa[x['ID']] = (x.get('QA_STATUS'), bool(x.get('CLIENT_SAFE')))
    cr = json.load(open(os.path.join(ING, 'CLIENT-SAFE-CROSSINGS.json'),
                        encoding='utf-8'))
    orfaos = inseg = crop_ruim = sem_ressalva = 0
    for x in cr['RECORDS']:
        crops = set(x.get('CROP_IDS') or [])
        for sid in _apoios(x):
            if sid not in qa:
                orfaos += 1
                continue
            if not qa[sid][1]:
                inseg += 1
            reg = idx[sid][0][1]
            rc = set(reg.get('CROP_IDS') or [])
            if crops and rc and not (crops & rc):
                crop_ruim += 1
        if not str(x.get('WHAT_IT_DOES_NOT_PROVE') or '').strip():
            sem_ressalva += 1
    r['CROSSINGS'] = {
        'EMITIDOS': cr['COUNT_TOTAL'],
        'APOIO_ORFAO': orfaos,
        'APOIO_NAO_CLIENT_SAFE': inseg,
        'CULTURA_DIVERGENTE': crop_ruim,
        'SEM_WHAT_IT_DOES_NOT_PROVE': sem_ressalva,
        'POR_TIPO': dict(Counter(x.get('CROSSING_TYPE') for x in cr['RECORDS'])),
    }

    # ── 4 · fontes ───────────────────────────────────────────────────────────
    # ⚠️ O APELIDO CONTA. Quem cita `IT-SRC-MINISTERO` chega na mesma linha que
    # hoje se chama `SRC_SALUTE_GOV_IT` — e um contador que ignora ID_ALIASES
    # relata órfão onde não há, o que é tão ruim quanto esconder um de verdade.
    fontes = set()
    for _a, d in colecoes():
        if d['COLLECTION'] != 'SOURCES':
            continue
        for x in d['RECORDS']:
            if isinstance(x, dict) and x.get('ID'):
                fontes.add(x['ID'])
                fontes.update(x.get('ID_ALIASES') or [])
    citadas, orf = Counter(), Counter()
    for a, d in colecoes():
        for x in d['RECORDS']:
            if not isinstance(x, dict):
                continue
            for sid in (x.get('SOURCE_IDS') or []):
                citadas[sid] += 1
                if sid not in fontes:
                    orf[sid] += 1
    linhas = sum(len(d['RECORDS']) for _a, d in colecoes()
                 if d['COLLECTION'] == 'SOURCES')
    r['SOURCES'] = {
        # ⚠️ LINHA E CHAVE SAO COISAS DIFERENTES. `fontes` inclui os apelidos, e
        # chamar isso de «cadastradas» inflaria o numero de fontes reais.
        'LINHAS_DE_FONTE': linhas,
        'CHAVES_QUE_RESOLVEM': len(fontes),
        'CHAVES_QUE_RESOLVEM_NOTA':
            'maior que o numero de linhas porque cada fonte rechaveada mantem o '
            'identificador antigo em ID_ALIASES. Duas chaves, uma fonte.',
        'CADASTRADAS': linhas,
        'CITADAS_DISTINTAS': len(citadas),
        'CITADAS_SEM_CADASTRO': len(orf),
        'EXEMPLOS_ORFAS': sorted(orf)[:12],
        'CADASTRADAS_NUNCA_CITADAS': len(fontes - set(citadas)),
    }

    # ── 5 · língua ───────────────────────────────────────────────────────────
    pt_sem_par, com_par, orig_guardado = 0, 0, 0
    for a, d in colecoes():
        for x in d['RECORDS']:
            if not isinstance(x, dict) or not x.get('ID'):
                continue
            for campo, v, _dr in campos_do_registro(x):
                meu, _c = parte_minha(campo, v)
                if not e_portugues(meu):
                    continue
                if x.get(campo + '_IT') and x.get(campo + '_EN'):
                    com_par += 1
                    if x.get(campo + '_ORIGINAL_RESEARCH_TEXT'):
                        orig_guardado += 1
                else:
                    pt_sem_par += 1
    r['LINGUA'] = {
        'CAMPOS_COM_IT_E_EN': com_par,
        'COM_ORIGINAL_PRESERVADO': orig_guardado,
        'AINDA_SO_EM_PORTUGUES': pt_sem_par,
        'LEI': 'citacao publica NAO entra nesta conta: ela fica na lingua em que '
               'foi publicada, de proposito.',
    }

    # ── 6 · a separação das pastas ───────────────────────────────────────────
    SUJO = re.compile(r'audit|relatorio|report|plano|plan|demo|quarentena|'
                      r'rascunho|draft|historia|story|fake', re.I)
    # ⚠️ ESTE CONTADOR JA SE DEU UM ATESTADO LIMPO SOBRE O DEFEITO QUE CONTINUAVA
    # ABERTO. Ele media SUJO contra o NOME DO ARQUIVO e nunca contra o conteudo
    # dos RECORDS — entao um registro que e receita de raspagem, carimbado
    # client-safe dentro de REGULATORY-FUTURE.json, passava limpo porque o
    # arquivo se chama REGULATORY-FUTURE.
    #
    #     MEDIR O NOME DA PASTA NAO E MEDIR O QUE ESTA DENTRO DELA.
    ROTA = re.compile(
        r'HTTP \d{3}|curl |urllib|WebFetch|User-Agent|bundle JS|chunk d[ao] rota|'
        r'endpoint|SDMX|dataflow|env-json-config|_ssl\.c|ECONNRESET|'
        r'getaddrinfo|nslookup|raspa|scrape', re.I)
    # ⚠️ E ESTE CONTADOR JA NASCEU CEGO UMA VEZ: olhava 'WHAT_IT_IS', chave que
    # nao existe no registro. O que existe e 'WHAT_IT_IS_IT', 'WHAT_IT_IS_EN' e
    # 'WHAT_IT_IS_ORIGINAL_RESEARCH_TEXT'. Media zero e parecia limpo.
    #
    #     CONTADOR QUE OLHA A CHAVE ERRADA DA SEMPRE ZERO, E ZERO PARECE BOM.
    BASES = ('WHAT_IT_IS', 'WHAT_IT_PROVES', 'WHAT_IT_DOES_NOT_PROVE',
             'INTERPRETATION', 'SO_WHAT', 'NOTE', 'CAVEAT', 'PERMANENT_CAVEAT')
    CAMPOS_DE_TELA = tuple(
        b + suf for b in BASES
        for suf in ('', '_IT', '_EN', '_ORIGINAL_RESEARCH_TEXT'))
    dentro = []
    ix_dom = {}
    for a, d in colecoes():
        for x in d['RECORDS']:
            if isinstance(x, dict) and x.get('ID'):
                ix_dom[x['ID']] = x
    for a, d in colecoes():
        if a == 'SOURCES.json':      # §18 · a casa declarada do metadado de rota
            continue
        for x in d['RECORDS']:
            if not x.get('CLIENT_SAFE'):
                continue
            alvo = ' '.join(str(x.get(c) or '') for c in CAMPOS_DE_TELA)
            if ROTA.search(alvo):
                dentro.append('%s:%s' % (a, x.get('ID')))
    # Um numero que nao distingue «ainda por olhar» de «olhado e mantido de
    # proposito» faz o leitor seguinte reabrir a mesma decisao. O contador diz
    # as duas coisas, e a segunda vem com o motivo escrito no registro.
    #
    #     PENDENCIA E DECISAO NAO PODEM SOMAR NO MESMO NUMERO.
    revistos = [i for i in dentro
                if (ix_dom.get(i.split(':', 1)[1], {}).get('CLAIM_DOMAIN_REVIEWED')
                    or ix_dom.get(i.split(':', 1)[1], {}).get('ROUTE_NOTE_MOVED_OUT_OF_CLAIM'))]
    r['SEPARACAO'] = {
        'ARQUIVOS_EM_DESIGN_INGEST': len(os.listdir(ING)),
        'PAPEL_DE_TRABALHO_EM_DESIGN_INGEST':
            [f for f in os.listdir(ING) if SUJO.search(f)],
        'METADADO_DE_ROTA_EM_REGISTRO_CLIENT_SAFE': dentro,
        'DESSES_LIDOS_E_MANTIDOS_DE_PROPOSITO': revistos,
        'DESSES_AINDA_POR_OLHAR': [i for i in dentro if i not in revistos],
        'POR_QUE_ALGUNS_FICAM':
            'a mencao a rota esta na RESSALVA e protege quem for reler a fonte — '
            'apagá-la removeria a advertencia junto com o suposto defeito. Cada '
            'um traz CLAIM_DOMAIN_REVIEWED com o motivo.',
        'METADADO_DE_ROTA_NOTA':
            'medido no CONTEUDO dos campos de tela, nao no nome do arquivo. '
            'SOURCES.json fica fora: e a casa declarada do metadado de rota (§18).',
        'ITENS_EM_INTERNAL_ARCHIVE':
            len(os.listdir(ARQ)) if os.path.isdir(ARQ) else 0,
    }

    # ── 7 · o que o pacote NÃO tem, procurado de verdade ─────────────────────
    PROIBIDO = ['crm', 'sell-in', 'sell in', 'sell-out', 'sell out', 'estoque',
                'inventory', 'pedido de compra', 'purchase order', 'faturamento',
                'revenue estimate', 'market share', 'participacao de mercado',
                'quota di mercato', 'meta de venda', 'sales target']
    achou = Counter()
    for a, d in colecoes():
        bruto = json.dumps(d, ensure_ascii=False).lower()
        for t in PROIBIDO:
            n = bruto.count(t)
            if n:
                achou[t] += n
    r['DADO_PROIBIDO'] = {
        'TERMOS_PROCURADOS': PROIBIDO,
        'OCORRENCIAS': dict(achou),
        'NOTA': 'ocorrencia nao e violacao: o texto pode estar DIZENDO que nao '
                'prova participacao de mercado. Cada uma precisa de leitura.',
    }

    # ── 8 · R4 · o preço que sustenta tem de ser da cultura ──────────────────
    ix = {}
    for a, d in colecoes():
        for x in d['RECORDS']:
            if x.get('ID'):
                ix[x['ID']] = x
    cx = os.path.join(ING, 'CLIENT-SAFE-CROSSINGS.json')
    apoio_processado = []
    nao_emitidos = []
    if os.path.exists(cx):
        X = json.load(open(cx, encoding='utf-8'))
        nao_emitidos = X.get('NAO_EMITIDOS_POR_ESTAGIO_DA_MERCADORIA') or []
        for x in X['RECORDS']:
            for i in (x.get('SUPPORTING_IDS', {}).get('MARKET') or []):
                if ix.get(i, {}).get('COMMODITY_STAGE') == 'PROCESSED_PRODUCT':
                    apoio_processado.append('%s <- %s' % (x['ID'], i))
    mk = [x for x in ix.values() if x.get('ENTITY_TYPE') == 'MARKET_OBSERVATION']
    r['MERCADO'] = {
        'OBSERVACOES': len(mk),
        'POR_ESTAGIO': dict(Counter(x.get('COMMODITY_STAGE') for x in mk)),
        'PROCESSADO_COM_CROP_IDS': sum(
            1 for x in mk if x.get('COMMODITY_STAGE') == 'PROCESSED_PRODUCT'
            and x.get('CROP_IDS')),
        'CRUZAMENTO_APOIADO_EM_PROCESSADO': apoio_processado,
        'NAO_EMITIDOS_POR_ESTAGIO': [n['CROP_ID'] for n in nao_emitidos],
        'LEI': 'PRECO DE AZEITE NAO E PRECO DA AZEITONA NAO E OPORTUNIDADE NA '
               'OLIVEIRA. Produto processado nao recebe CROP_IDS: recebe '
               'DERIVED_FROM_CROP_ID.',
    }

    p = os.path.join(V21, 'ACCEPTANCE-REPORT.json')
    json.dump(r, open(p, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

    print('== §19 ACEITACAO ==')
    print('mestre        : %d registros · %d client-safe · %d IDs duplicados'
          % (r['MASTER']['RECORDS_TOTAL'], r['MASTER']['RECORDS_CLIENT_SAFE'],
             r['MASTER']['DUPLICATE_IDS']))
    print('portao QA     : %d violacoes · %d sem carimbo · %d contagens divergentes'
          % (r['QA_GATE']['VIOLACOES'], r['QA_GATE']['SEM_QA_STATUS'],
             len(r['QA_GATE']['CONTAGEM_DECLARADA_DIVERGE'])))
    c = r['CROSSINGS']
    print('cruzamentos   : %d emitidos · orfao %d · inseguro %d · cultura errada %d'
          % (c['EMITIDOS'], c['APOIO_ORFAO'], c['APOIO_NAO_CLIENT_SAFE'],
             c['CULTURA_DIVERGENTE']))
    s = r['SOURCES']
    print('fontes        : %d linhas · %d chaves resolvem · %d citadas · %d sem cadastro'
          % (s['LINHAS_DE_FONTE'], s['CHAVES_QUE_RESOLVEM'],
             s['CITADAS_DISTINTAS'], s['CITADAS_SEM_CADASTRO']))
    l = r['LINGUA']
    print('lingua        : %d campos com IT+EN · %d ainda so em portugues'
          % (l['CAMPOS_COM_IT_E_EN'], l['AINDA_SO_EM_PORTUGUES']))
    print('separacao     : %d arquivos no ingest · %d papel de trabalho dentro'
          % (r['SEPARACAO']['ARQUIVOS_EM_DESIGN_INGEST'],
             len(r['SEPARACAO']['PAPEL_DE_TRABALHO_EM_DESIGN_INGEST'])))
    print('              · %d client-safe com rota no texto (%d lidos e mantidos, '
          '%d por olhar)'
          % (len(r['SEPARACAO']['METADADO_DE_ROTA_EM_REGISTRO_CLIENT_SAFE']),
             len(r['SEPARACAO']['DESSES_LIDOS_E_MANTIDOS_DE_PROPOSITO']),
             len(r['SEPARACAO']['DESSES_AINDA_POR_OLHAR'])))
    print('mercado       : %s · %d processado com CROP_IDS · %d cruzamento em processado'
          % (r['MERCADO']['POR_ESTAGIO'], r['MERCADO']['PROCESSADO_COM_CROP_IDS'],
             len(r['MERCADO']['CRUZAMENTO_APOIADO_EM_PROCESSADO'])))
    print('\ngravado em %s' % p)

    # ── A ACEITACAO PASSA A SER PORTAO, E NAO SO RELATORIO ───────────────────
    #
    # ⚠️ ATE AQUI ESTA FUNCAO MEDIA VIOLACOES E DEVOLVIA 0 SEMPRE. A cadeia roda
    # com `set -euo pipefail`, ou seja: quem falha, para tudo. Este passo nunca
    # falhava — entao um pacote com registro sem carimbo de QA, com contagem
    # declarada divergindo do corpo ou com cruzamento apoiado em registro que
    # nao passou no portao saia com EXIT 0 e parecia aceito.
    #
    #     ETAPA OBRIGATORIA QUE NAO PODE REPROVAR NAO E ETAPA: E RELATORIO.
    #
    # Nenhum limiar novo entrou. Cada contador abaixo JA se chamava violacao no
    # proprio relatorio, e cada um JA media zero antes desta mudanca: a trava
    # nasce verde, e e de proposito — trava que nasce vermelha ensina a ignorar
    # trava. O que mudou e que a partir de agora ela e obrigatoria.
    reprova = [
        ('QA_GATE.VIOLACOES', r['QA_GATE']['VIOLACOES']),
        ('QA_GATE.SEM_QA_STATUS', r['QA_GATE']['SEM_QA_STATUS']),
        ('QA_GATE.CONTAGEM_DECLARADA_DIVERGE',
         len(r['QA_GATE']['CONTAGEM_DECLARADA_DIVERGE'])),
        ('MASTER.DUPLICATE_IDS', r['MASTER']['DUPLICATE_IDS']),
        ('CROSSINGS.APOIO_ORFAO', r['CROSSINGS']['APOIO_ORFAO']),
        ('CROSSINGS.APOIO_NAO_CLIENT_SAFE', r['CROSSINGS']['APOIO_NAO_CLIENT_SAFE']),
        ('CROSSINGS.CULTURA_DIVERGENTE', r['CROSSINGS']['CULTURA_DIVERGENTE']),
        ('SOURCES.CITADAS_SEM_CADASTRO', r['SOURCES']['CITADAS_SEM_CADASTRO']),
        # ⚠️ `LINGUA.AINDA_SO_EM_PORTUGUES` NAO ENTRA NESTA LISTA, e a razao foi
        # MEDIDA, nao escolhida. A primeira versao deste portao o incluia, e a
        # testemunha da trilha universal mostrou o efeito: um boletim novo
        # qualquer traz leitura nossa em portugues, ainda sem irma em italiano,
        # e a cadeia INTEIRA parava — o acervo de 7.000 registros ficava sem
        # fechar por causa de UMA frase por traduzir.
        #
        #     LACUNA DE TRADUCAO NAO E FALHA DE INTELIGENCIA.
        #     UMA TRAVA QUE IMPEDE A INGESTAO NORMAL NAO PROTEGE: ELA PARA.
        #
        # O contador continua sendo medido e continua no relatorio; a
        # consequencia dele agora e POR REGISTRO, na catraca (etapa
        # LOCALIZATION), onde ela pertence: quem nao tem a leitura na lingua do
        # leitor nao esta pronto para publicar — mas nao impede o pacote de
        # existir nem os outros registros de fechar.
        ('SEPARACAO.PAPEL_DE_TRABALHO_EM_DESIGN_INGEST',
         len(r['SEPARACAO']['PAPEL_DE_TRABALHO_EM_DESIGN_INGEST'])),
        ('MERCADO.PROCESSADO_COM_CROP_IDS', r['MERCADO']['PROCESSADO_COM_CROP_IDS']),
        ('MERCADO.CRUZAMENTO_APOIADO_EM_PROCESSADO',
         len(r['MERCADO']['CRUZAMENTO_APOIADO_EM_PROCESSADO'])),
    ]
    quebrou = [(k, v) for k, v in reprova if v]
    if quebrou:
        print('\n  PARADO NA ACEITACAO — o pacote nao pode ser dado por aceito:')
        for k, v in quebrou:
            print('    %-46s %d' % (k, v))
        print('  o relatorio completo esta em %s' % p)
        return 1
    print('  ACEITACAO: 0 violacoes em %d contadores obrigatorios' % len(reprova))
    return 0


def _apoios(x):
    """Os IDs que sustentam um cruzamento — venham de onde vierem."""
    fora = []
    for k, v in x.items():
        if k.endswith('_LEADS'):
            continue                      # pista nao e apoio, de proposito
        if isinstance(v, list) and v and all(isinstance(i, str) for i in v):
            if k in ('SUPPORT_IDS', 'SOURCE_IDS', 'EVIDENCE_IDS'):
                fora += v
        if isinstance(v, dict):
            for vv in v.values():
                if isinstance(vv, list):
                    fora += [i for i in vv if isinstance(i, str)]
    return [i for i in fora if i.startswith(('IT-', 'ECW_', 'SRC', 'REL_', 'PR'))]


if __name__ == '__main__':
    raise SystemExit(main())
