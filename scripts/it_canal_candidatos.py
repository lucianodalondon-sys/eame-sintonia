#!/usr/bin/env python3
"""FASE 13 — o que o acervo sustenta sobre CANAL, que e pouco e precisa ser dito.

O acervo NOMEIA cooperativas reais, com cultura e territorio. Isso e material
bruto de canal. Mas nenhuma fonte liga qualquer uma delas a compra de produto,
muito menos a ADAMA: elas aparecem como ANFITRIAS ou COLABORADORAS de eventos
tecnicos.

    ORGANIZACAO NOMEADA NUM CONVEGNO != CANAL COMERCIAL.
    NAO INVENTAR ASSOCIACAO PRODUTOR -> REVENDA.

Entao isto sai como CANDIDATO, com o papel declarado e a citacao ao lado, e o
campo de relacao comercial fica NOT_IN_SOURCE. Quem for construir a camada
comercial comeca daqui sem herdar afirmacao que ninguem fez.
"""
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'scripts'))
from it_futuro_corpus import corpus                              # noqa: E402

DEST = os.path.join(ROOT, 'data/samples/IT-FUTURO-V1')

ORG_RX = re.compile(
    r'\b(?:cooperativa|societ[àa]\s+cooperativa|consorzio\s+agrario|'
    r'associazione|fondazione|organizzazione\s+di\s+produttori)\s+'
    r'([A-Z][\w\'\-]{2,24}(?:\s+[A-Z][\w\'\-]{2,24}){0,2})|'
    r'\b(Melinda|Assomela|Cofrui\w*|Corma|Fruit\s?Imprese|Foianini|APOFRUIT|'
    r'Conserve\s+Italia|Granarolo|Coldiretti|Confagricoltura|CIA)\b')

PAPEL = re.compile(r'ospita|ospitando|sede|grazie a|in collaborazione con|'
                   r'presidente|tecnico della|dell\'ufficio', re.I)

# A ASR transcreve nome de molecula como se fosse nome proprio ('Cimoxaline' por
# cimoxanil) e substantivos comuns em maiuscula. Marcar em vez de excluir: quem ler
# ve o ruido e o motivo, e nao uma lista limpa demais para ser verdade.
RUIDO = re.compile(r'oxalin|sulfur|azol|amid|trina|Citt|^Sole$|^Amve$|^Antesia$',
                   re.I)


def main():
    os.makedirs(DEST, exist_ok=True)
    achados, vistos = [], set()
    for d in corpus():
        for m in ORG_RX.finditer(d['TEXT']):
            nome = (m.group(1) or m.group(2) or '').strip()
            if not nome or len(nome) < 4:
                continue
            k = nome.lower()
            if k in vistos:
                continue
            vistos.add(k)
            a, b = max(0, m.start() - 220), min(len(d['TEXT']), m.end() + 160)
            ctx = re.sub(r'\s+', ' ', d['TEXT'][a:b])
            achados.append({
                'ORGANISATION_AS_WRITTEN': nome,
                'SOURCE_ID': d['SOURCE_ID'], 'SOURCE_DATE': d['SOURCE_DATE'],
                'SOURCE_TITLE': (d.get('TITLE') or '')[:110],
                'QUOTE_IT': ctx[:320],
                'ROLE_IN_SOURCE': ('DECLARED_HOST_OR_COLLABORATOR'
                                   if PAPEL.search(ctx) else 'MENTIONED_ONLY'),
                'IS_ADAMA_CHANNEL': 'NOT_IN_SOURCE',
                'BUYS_PRODUCT': 'NOT_IN_SOURCE',
                'LINKED_TO_A_GROWER': 'NOT_IN_SOURCE',
                'CAN_BECOME_CHANNEL_LAYER': ('LIKELY_ASR_NOISE'
                                             if RUIDO.search(nome)
                                             else 'CANDIDATE_ONLY'),
            })
    out = {
        'DATASET': 'IT-CANAL-CANDIDATOS-V1',
        'LAYER': 'COMMERCIAL CHANNEL — CANDIDATES ONLY',
        'COUNTRY': 'IT', 'SOURCE_ID': 'IT-FUTURO-V1', 'CAPTURED_AT': '2026-09-04',
        'SOURCE': 'organizacoes nomeadas dentro das falas do acervo, com o papel que '
                  'a propria fala lhes da',
        'O_QUE_ISTO_NAO_E': (
            'NAO e uma lista de canal da ADAMA. Nenhuma fonte do acervo liga estas '
            'organizacoes a compra de produto nem a ADAMA. Elas aparecem como '
            'anfitrias e colaboradoras de eventos tecnicos. Publicar isto como '
            'canal seria inventar a relacao comercial que falta.'),
        'CHANNEL_LAYER_STATE': 'NOT_COLLECTED',
        'WHY': 'nunca houve coleta dirigida a cooperativa, revenda ou RTV. As '
               'mencoes sao subproduto das transcricoes de convegno.',
        'CANDIDATES': len(achados),
        'CANDIDATES_NET_OF_NOISE': sum(
            1 for a in achados if a['CAN_BECOME_CHANNEL_LAYER'] == 'CANDIDATE_ONLY'),
        'RUIDO_DECLARADO': 'a ASR transcreve molecula e substantivo comum como nome '
                           'proprio. As entradas marcadas LIKELY_ASR_NOISE ficam na '
                           'lista, sinalizadas, em vez de sumirem.',
        'ITEMS': sorted(achados, key=lambda z: z['ORGANISATION_AS_WRITTEN']),
    }
    json.dump(out, open(os.path.join(DEST, 'IT-CANAL-CANDIDATOS-V1.json'), 'w',
                        encoding='utf-8'), ensure_ascii=False, indent=1)
    print('CHANNEL_LAYER_STATE = %s' % out['CHANNEL_LAYER_STATE'])
    print('CANDIDATOS          = %d' % len(achados))
    for a in out['ITEMS'][:14]:
        print('  %-28s %-30s %s' % (a['ORGANISATION_AS_WRITTEN'][:28],
                                    a['ROLE_IN_SOURCE'], a['SOURCE_ID']))
    return out


if __name__ == '__main__':
    main()
