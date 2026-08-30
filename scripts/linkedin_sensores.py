#!/usr/bin/env python3
"""
O PAINEL — os oito nomes, e nada além disso.

Este arquivo era a coleta inteira. Não é mais, e a razão importa: ele pedia
`searchQuery` a `apimaestro~linkedin-profile-detail`, um campo que aquele ator
não lê. Ele ignorou a consulta em silêncio, devolveu SUCCEEDED com um perfil bem
formado, e cobrou — oito vezes o mesmo consultor de cibersegurança.

    WRONG_INPUT_CONTRACT ≠ WRONG_PLATFORM

A coleta correta vive em outro lugar, com os portões que faltavam aqui:

    scripts/apify_contrato.py       lê o contrato publicado ANTES de gastar
    scripts/linkedin_prova_busca.py resolve identidade (nome ≠ pessoa)
    scripts/linkedin_posts.py       lê os posts de quem a identidade permite
    scripts/fato_local.py           onde o fato ocorreu ≠ onde a pessoa está

Deixar o código antigo de pé, ao lado do novo, seria manter uma porta que leva
de volta ao defeito — bastaria alguém rodar o arquivo errado. Então ele guarda
só o que continua verdadeiro e continua sendo usado: **quem são os oito**.

Os oito foram identificados por pesquisa pública, antes de qualquer chave existir.
Nome novo não entra por aqui: entra por outra missão.
"""
import datetime

CASE_DATE = datetime.date(2026, 4, 23)
JANELA = (datetime.date(2026, 1, 1), datetime.date(2026, 5, 31))
TETO_PERFIS = 8
TETO_POSTS = 80

# Os oito de sempre. NENHUM nome novo entra aqui.
ALVOS = [
    {'NAME': 'Pasquale De Vita', 'VOICE_CLASS': 'RESEARCHER',
     'INSTITUTION': 'CREA Cerealicoltura e Colture Industriali'},
    {'NAME': 'Nicola Pecchioni', 'VOICE_CLASS': 'RESEARCHER',
     'INSTITUTION': 'CREA Cerealicoltura e Colture Industriali'},
    {'NAME': 'Sabrina Locatelli', 'VOICE_CLASS': 'RESEARCHER',
     'INSTITUTION': 'CREA — Bergamo'},
    {'NAME': 'Francesca Nocente', 'VOICE_CLASS': 'RESEARCHER',
     'INSTITUTION': 'CREA'},
    {'NAME': 'Daniela Pacifico', 'VOICE_CLASS': 'RESEARCHER',
     'INSTITUTION': 'CREA'},
    {'NAME': 'Stefano Biagetti', 'VOICE_CLASS': 'TECHNICAL_FIELD_VOICE',
     'INSTITUTION': 'Consorzio Agrario di Ancona'},
    {'NAME': 'Giovanni Drei', 'VOICE_CLASS': 'TECHNICAL_FIELD_VOICE',
     'INSTITUTION': 'Bayer Crop Science Italia'},
    {'NAME': 'Federico Cavina', 'VOICE_CLASS': 'TECHNICAL_FIELD_VOICE',
     'INSTITUTION': 'Terremerse Soc. Coop.'},
]



if __name__ == '__main__':
    print('painel de sensores humanos — %d nomes' % len(ALVOS))
    for a in ALVOS:
        print('  %-20s %-22s %s' % (a['NAME'], a['VOICE_CLASS'], a['INSTITUTION']))
    print('caso:', CASE_DATE, '| janela:', JANELA[0], 'a', JANELA[1])
    print('a coleta vive em linkedin_prova_busca.py e linkedin_posts.py')
