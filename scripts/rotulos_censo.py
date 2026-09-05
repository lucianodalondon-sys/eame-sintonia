#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CENSO DE TERMOS NO TEXTO DOS 163 RÓTULOS — o que sustenta um «N de 163».

    python3 scripts/rotulos_censo.py

POR QUE ISTO É DIFERENTE DA LEITURA DE PARES
---------------------------------------------
`rotulos_ler.py` estrutura o rótulo em pares cultura × alvo, e consegue fazer isso
em **102 dos 163** (62,6%). É leitura estruturada, e portanto é AMOSTRA.

Este script não estrutura nada. Ele só pergunta: **a palavra está no texto?** — e
pergunta nos 163. É CENSO.

    «6 dos 163 rótulos nomeiam Scaphoideus titanus»   ← censo, firme
    «102 dos 163 tiveram par lido»                     ← amostra, é um piso

A diferença muda o que a tela tem direito de dizer. Um zero de censo é uma
afirmação forte; um zero de amostra não é afirmação nenhuma.

O QUE O CENSO AINDA NÃO PODE DIZER
-----------------------------------
    NÃO ESTÁ NO TEXTO DO RÓTULO ≠ NÃO ESTÁ AUTORIZADO

O rótulo é o documento publicado; o registro pode conter usos que o rótulo escreve
de outro jeito, ou com sinonímia que não prevemos. Por isso todo termo entra com
uma lista de **grafias alternativas**, e o resultado declara quais foram testadas.

⚠️ E há uma condição que teve de ser medida antes, senão o denominador seria falso:
**nenhum dos 163 PDFs é imagem escaneada** — todos devolvem texto. Se algum fosse
digitalização sem OCR, o censo estaria correndo sobre menos de 163 e o «0 de 163»
seria mentira. Isto é reconferido a cada execução.
"""
import json
import os
import re
import time
import unicodedata

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CRUS = os.path.join(ROOT, 'data', 'raw', 'IT-ROTULOS')
SAIDA = os.path.join(ROOT, 'data', 'samples', 'IT-ROTULOS')

MIN_TEXTO = 800   # abaixo disto o PDF é suspeito de ser imagem sem OCR

# (chave, [grafias], o que a presença/ausência significa para o demo)
TERMOS = [
    ('SCAPHOIDEUS_TITANUS', ['scaphoideus', 'scafoideo'],
     'vetor da flavescencia dourada, de controle obrigatorio em 5 regioes'),
    ('FLAVESCENZA_DOURADA', ['flavescenza', 'giallumi della vite'],
     'a doenca em si; o rotulo trata o vetor, nao o fitoplasma'),
    ('BACTROCERA_OLEAE', ['bactrocera oleae', 'mosca dell.oliva', 'mosca dell.olivo'],
     'mosca da oliveira -- a principal praga do olival italiano'),
    ('BACTROCERA_OUTRAS', ['bactrocera dorsalis', 'bactrocera zonata'],
     'outras Bactrocera; NAO sao a mosca da oliveira'),
    ('OCCHIO_DI_PAVONE', ['occhio di pavone', 'spilocaea', 'cicloconio', 'venturia oleaginea'],
     'a principal doenca do olival italiano'),
    ('OLIVO', ['olivo', 'oliveto', 'olive da', 'olivicol'],
     'a cultura oliveira, em qualquer uso'),
    ('VENTURIA_MELO', ['ticchiolatura', 'venturia inaequalis'],
     'sarna da macieira'),
    ('HALYOMORPHA', ['halyomorpha', 'cimice asiatica'],
     'percevejo asiatico'),
    ('DIABROTICA', ['diabrotica'], 'praga do milho'),
    ('OSTRINIA', ['ostrinia', 'piralide'], 'broca do milho'),
    ('FUSARIUM', ['fusarium', 'fusarios'], 'fusariose, ligada a micotoxina'),
    ('ZYMOSEPTORIA', ['zymoseptoria', 'septoria', 'septorios'], 'septoriose do trigo'),
    ('ECHINOCHLOA', ['echinochloa', 'giavone'], 'a daninha do arroz'),
    ('ORYZA_CRODO', ['riso crodo'], 'arroz daninho'),
    ('AMBROSIA', ['ambrosia artemisiifolia'], 'daninha invasora com impacto de saude'),
    ('POPILLIA', ['popillia japonica'], 'praga quarentenaria em expansao no norte'),
    ('XYLELLA', ['xylella'], 'bacteria de quarentena do olival do sul'),
]


def _n(t):
    return ''.join(c for c in unicodedata.normalize('NFD', t or '')
                   if unicodedata.category(c) != 'Mn').lower()


def main():
    import pypdf
    man = json.load(open(os.path.join(CRUS, '_MANIFESTO.json'), encoding='utf-8'))
    os.makedirs(SAIDA, exist_ok=True)

    textos, sem_texto, falhou = {}, [], []
    for it in man['ITENS']:
        if it['ESTADO'] != 'OK':
            falhou.append(it['REGISTRATION_ID'])
            continue
        try:
            t = '\n'.join((p.extract_text() or '')
                          for p in pypdf.PdfReader(
                              os.path.join(CRUS, it['ARQUIVO'])).pages)
        except Exception:
            falhou.append(it['REGISTRATION_ID'])
            continue
        if len(t) < MIN_TEXTO:
            sem_texto.append({'REGISTRATION_ID': it['REGISTRATION_ID'],
                              'CHARS': len(t)})
        textos[it['REGISTRATION_ID']] = (_n(t), it.get('PRODUCT'))

    resultado = []
    for chave, grafias, nota in TERMOS:
        achados = []
        for reg, (t, nome) in sorted(textos.items()):
            for g in grafias:
                if re.search(g, t):
                    achados.append({'REGISTRATION_ID': reg, 'PRODUCT': nome,
                                    'GRAFIA_QUE_BATEU': g})
                    break
        resultado.append({
            'TERMO': chave,
            'GRAFIAS_TESTADAS': grafias,
            'O_QUE_E': nota,
            'ROTULOS_QUE_CITAM': len(achados),
            'DE_UM_TOTAL_DE': len(textos),
            'FRASE_PERMITIDA': '%d dos %d rotulos ADAMA vigentes na Italia citam este '
                               'termo no texto publicado' % (len(achados), len(textos)),
            'ITENS': achados,
        })

    denominador_confiavel = not sem_texto and not falhou
    saida = {
        'DATASET': 'IT-ROTULOS-CENSO-DE-TERMOS',
        'METODO': 'busca de termo no texto extraido de TODOS os rotulos, sem estruturar',
        'POR_QUE_CENSO_E_NAO_AMOSTRA':
            'a leitura de pares estrutura 102 dos 163 (62,6%) e por isso e amostra. '
            'Este censo so pergunta se a palavra esta no texto, e pergunta nos 163.',
        'O_QUE_O_CENSO_NAO_DIZ':
            'NAO ESTA NO TEXTO DO ROTULO nao e NAO ESTA AUTORIZADO. O registro pode '
            'conter uso que o rotulo escreve de outro jeito. Por isso cada termo lista '
            'as grafias testadas.',
        'CAPTURADO_EM': time.strftime('%Y-%m-%dT%H:%M:%S'),
        'ROTULOS_COM_TEXTO': len(textos),
        'ROTULOS_SEM_TEXTO_UTIL': sem_texto,
        'ROTULOS_QUE_FALHARAM': falhou,
        'DENOMINADOR_CONFIAVEL': denominador_confiavel,
        'DENOMINADOR_POR_QUE_IMPORTA':
            'se algum PDF fosse imagem sem OCR, o censo correria sobre menos de 163 e '
            'um «0 de 163» seria mentira. Reconferido a cada execucao.',
        'TERMOS': resultado,
    }
    destino = os.path.join(SAIDA, 'IT-CENSO-DE-TERMOS.json')
    json.dump(saida, open(destino, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

    print('rotulos com texto: %d · sem texto util: %d · falharam: %d · denominador %s'
          % (len(textos), len(sem_texto), len(falhou),
             'CONFIAVEL' if denominador_confiavel else 'COMPROMETIDO'))
    print()
    for r in resultado:
        marca = '  <-- ZERO' if r['ROTULOS_QUE_CITAM'] == 0 else ''
        print('  %-22s %3d de %d%s' % (r['TERMO'], r['ROTULOS_QUE_CITAM'],
                                       r['DE_UM_TOTAL_DE'], marca))
    print()
    print('gravado:', os.path.relpath(destino, ROOT))


if __name__ == '__main__':
    main()
