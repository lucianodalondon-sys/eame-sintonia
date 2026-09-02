#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
COLHE a saída da localização e monta a MEMÓRIA DE TRADUÇÃO.

    python3 scripts/v21_tm_colher.py

POR QUE UMA MEMÓRIA, E NÃO ESCREVER DIRETO NO ARQUIVO
------------------------------------------------------
A mesma frase aparece 1.715 vezes em arquivos diferentes. Traduzida no lugar,
ela vira 1.715 traduções que podem divergir — e no dia em que divergirem,
ninguém vai saber qual está certa.

    A MESMA FRASE TEM DE TER A MESMA TRADUÇÃO. SEMPRE, E EM TODO ARQUIVO.

Então a chave da memória é o próprio texto em português. Frase igual, tradução
igual, por construção — não por disciplina de quem edita.

E a memória fica em `data/i18n/`, versionada, fora do pacote: quando o portal
real for feito, ela é reaproveitada. Traduzir de novo o que já foi traduzido é
onde a divergência nasce.
"""
import json
import os
import re
import unicodedata

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ⚠️ FUTURE-EVENTS é um RECORTE de EVENTS: o mesmo registro foi traduzido duas
# vezes, por dois tradutores que não sabiam um do outro. Não se escolhe uma no
# par de moeda — quem manda é a coleção-fonte, e o recorte herda dela.
#
#     ONDE O MESMO REGISTRO MORA EM DOIS ARQUIVOS, A VERDADE É DO ORIGINAL.
PRECEDENCIA = {'EVENTS.json': 0, 'FUTURE-EVENTS.json': 1}


import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from v21_traducao_trava import conferir


def trava(pt, e):
    """Problemas que a maquina acha nas duas linguas desta entrada."""
    return conferir(pt, e.get('IT'), 'IT') + conferir(pt, e.get('EN'), 'EN')


def _nu(t):
    """Mesmo texto, tirando o que é só grafia: acento, apóstrofo, espaço."""
    t = unicodedata.normalize('NFD', str(t))
    t = ''.join(c for c in t if unicodedata.category(c) != 'Mn')
    t = re.sub(r"['`’´]", '', t)
    return re.sub(r'\s+', ' ', t).strip().lower()
SAIDA = os.path.join(
    os.environ.get('LOCALAPPDATA', r'C:\Users\London1\AppData\Local'),
    'Temp', 'claude', 'C--eame-sintonia',
    'a922b30b-6fd0-4c62-9d83-5b22807c64d1', 'tasks', 'wimgu1ear.output')
EXTRACAO = os.path.join(ROOT, '.tmp', 'v21_localizar.json')
TM = os.path.join(ROOT, 'data', 'i18n', 'v21-traducoes.json')


def main():
    # o português de origem, por (ID, CAMPO)
    pt = {}
    for r in json.load(open(EXTRACAO, encoding='utf-8')):
        for campo, texto in r['CAMPOS'].items():
            pt[(r['ID'], campo)] = texto

    tm, conflitos, orfaos, grafia, travou = {}, [], 0, 0, 0
    d = json.load(open(SAIDA, encoding='utf-8'))['result']
    for arq in d['resultado']:
        for loc in arq['localizacoes']:
            for c in loc['campos']:
                origem = pt.get((loc['ID'], c['CAMPO']))
                if not origem:
                    orfaos += 1
                    continue
                k = origem.strip()
                novo = {'PT': k, 'IT': c['IT'], 'EN': c['EN'],
                        'ONDE_PRIMEIRO': '%s · %s · %s'
                                         % (arq['arquivo'], loc['ID'], c['CAMPO'])}
                if c.get('NOTA'):
                    novo['NOTA_DO_TRADUTOR'] = c['NOTA']
                if k in tm and (tm[k]['IT'] != novo['IT']
                                or tm[k]['EN'] != novo['EN']):
                    velho = tm[k]
                    # ⚠️ DUAS TRADUCOES DA MESMA FRASE. Antes de escolher, PERGUNTAR
                    # SE AS DUAS SAO HONESTAS — nao qual e mais bonita.
                    #
                    # A divergencia aqui e de palavra («proprio» / «stesso»,
                    # «l'elenco» / «la lista»), nao de sentido. Mas isso e uma
                    # leitura minha, e leitura minha nao vale como prova. Entao a
                    # trava mecanica confere as duas: numero, negacao, incerteza,
                    # lugar, enfase.
                    #
                    #     SE AS DUAS PASSAM, A DIFERENCA E DE ESTILO E A
                    #     PRECEDENCIA RESOLVE. SE UMA FALHA, ELA E QUE ESTA ERRADA.
                    fv = trava(k, velho)
                    fn = trava(k, novo)
                    if fv and fn:
                        conflitos.append({'PT': k[:120], 'MOTIVO': 'AS_DUAS_FALHAM',
                                          'A': velho['ONDE_PRIMEIRO'], 'A_ERRO': fv,
                                          'B': novo['ONDE_PRIMEIRO'], 'B_ERRO': fn})
                        continue
                    if fv or fn:
                        # uma falhou: fica a limpa, e o motivo vai escrito
                        vence = novo if fv else velho
                        vence['CONFLITO_RESOLVIDO_POR_TRAVA'] = (
                            'a outra traducao desta frase falhou na trava (%s) e foi '
                            'descartada.' % ' · '.join(fv or fn))
                        tm[k] = vence
                        travou += 1
                        continue
                    pv = PRECEDENCIA.get(velho['ONDE_PRIMEIRO'].split(' · ')[0], 9)
                    pn = PRECEDENCIA.get(arq['arquivo'], 9)
                    grafia += 1
                    if pn >= pv:
                        continue        # o que ja esta vale mais (ou empata)
                    novo['CONFLITO_RESOLVIDO_POR_PRECEDENCIA'] = (
                        'a mesma frase foi traduzida duas vezes, por tradutores que '
                        'nao se viam. AS DUAS passaram na trava — a diferenca era de '
                        'palavra, nao de sentido. Ficou a da colecao-fonte (%s); o '
                        'recorte herda.' % velho['ONDE_PRIMEIRO'].split(' · ')[0])
                tm[k] = novo

    if conflitos:
        print('PARADO: %d frases receberam DUAS traducoes diferentes.' % len(conflitos))
        for c in conflitos[:8]:
            print('  %s\n    %s\n    %s' % (c['PT'], c['A'], c['B']))
        return 1

    os.makedirs(os.path.dirname(TM), exist_ok=True)
    json.dump({
        'MEMORIA': 'SINTONIA_ITALY_V2_1_TRADUCOES',
        'CHAVE': 'o proprio texto em portugues',
        'LEI': 'frase igual tem traducao igual, em todo arquivo, por construcao.',
        'O_QUE_A_TRADUCAO_NAO_PODE': [
            'acrescentar fato', 'fortalecer alegacao', 'mudar alcance geografico',
            'mudar confianca', 'remover incerteza',
        ],
        'CITACAO': 'texto original da fonte NAO entra aqui. Citacao publica fica na '
                   'lingua em que foi publicada — traduzir prova e adultera-la.',
        'COUNT': len(tm),
        'TRADUCOES': sorted(tm.values(), key=lambda x: x['PT']),
    }, open(TM, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('memoria: %d frases · orfaos ignorados: %d' % (len(tm), orfaos))
    print('duplicatas resolvidas: %d por precedencia (as duas limpas) · %d pela '
          'trava (uma falhou)' % (grafia, travou))
    print('gravada em %s' % TM)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
