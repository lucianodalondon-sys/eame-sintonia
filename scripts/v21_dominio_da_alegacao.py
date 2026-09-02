#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""R5 · O DOMÍNIO DA ALEGAÇÃO: sobre o mundo, ou sobre o nosso encanamento?

    python3 scripts/v21_dominio_da_alegacao.py

O DEFEITO
---------
Dois registros `CLIENT_SAFE=true` dentro de `REGULATORY-FUTURE.json` não eram
sinal regulatório: eram a **receita de como raspar** o site da UE. E a mesma URL
estava cadastrada em `SOURCES.json` como `CLIENT_SAFE=false`. O pacote
contradizia a própria §18, que diz que metadado de rota é infraestrutura de
coleta.

    SABER COMO ABRIR A PORTA NÃO É SABER O QUE HÁ NA SALA.

A EXTENSÃO DO PORTÃO
--------------------
O portão de QA respondia «esta evidência é boa?». Faltava a outra pergunta:
«esta afirmação é sobre o mundo?». Um registro pode ser verdadeiro, documentado e
verificável — e ainda assim não sustentar afirmação nenhuma ao cliente, porque
não fala do mercado italiano: fala de como o coletor chegou lá.

    CLIENT_SAFE = a evidência aguenta  E  a alegação é sobre o mundo.

POR QUE A LISTA É ESCRITA À MÃO, E NÃO UM REGEX
------------------------------------------------
Porque o regex erra para os dois lados, e já errou aqui: ele marcou três
registros do ISTAT — área de trigo duro, de olival e de milho — que são fato
econômico real, e cuja menção a `SDMX` está na RESSALVA, avisando que a consulta
nacional não sustenta quebra regional. Rebaixar esses seria apagar a advertência
junto com o suposto defeito.

    UM CLASSIFICADOR AUTOMÁTICO QUE REBAIXA A RESSALVA
    APAGA JUSTAMENTE O QUE PROTEGIA O LEITOR.

Então cada registro foi lido e decidido, e a decisão fica escrita aqui com o
motivo. Se um ID sumir do pacote, este arquivo FALHA — decisão que não encontra
o seu registro é decisão que envelheceu sem avisar.
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ING = os.path.join(ROOT, 'build', 'ITALY-REALITY-HANDOFF-V2.1', 'DESIGN-INGEST')

SOBRE_O_MUNDO = 'DOMAIN_INTELLIGENCE'
SOBRE_A_ROTA = 'SOURCE_ACCESS'

# ── O REGISTRO DE DECISÕES, lido um a um ────────────────────────────────────
REBAIXAR = {
    'IT-CAN-4DAA0F9889': (
        'e a receita de como alcancar a API do EU Pesticides Database (arquivo '
        'de configuracao de runtime, palpite /api que devolve pagina cacheada). '
        'Nao afirma nada sobre regulacao: afirma como se abre a porta.'),
    'IT-CAN-4D6754F52F': (
        'e o corpo do POST de busca do EU Pesticides Database e o HTTP 500 que '
        'ele devolve sem os criterios completos. Instrucao de coleta, nao sinal '
        'regulatorio.'),
    'IT-CAN-7F521FB52E': (
        'o proprio registro declara: "este registro e sobre um CATALOGO, nunca '
        'sobre o campo". Estava em CURRENT-FIELD-SIGNALS como FIELD_SIGNAL '
        'client-safe, e o que ele prova e que uma pagina de indice tem duas '
        'series e que uma delas nao foi lida.'),
    'IT-CAN-4167324DBA': (
        'e um aviso de qualidade sobre a FONTE — a serie de preco de vinho da '
        'Comissao parou em 06/07/2025 —, nao uma observacao de mercado. Como '
        'MARKET_OBSERVATION client-safe, um preco de 14 meses atras iria a tela '
        'como corrente. O aviso e valioso; o lugar dele nao era esse.'),
}

# Rota vazando para dentro de uma alegação que, no resto, é verdadeira.
# Aqui não se rebaixa o registro: tira-se a frase que não é sobre o mundo.
APARAR = {
    'IT-CAN-785827E751': [
        ' E que a pagina esta acessivel ao nosso IP (HTTP 200).',
        ', e que a pagina esta acessivel ao nosso IP (HTTP 200)',
    ],
}

# Lidos, e mantidos de propósito. Ficam nomeados para que ninguém os "corrija"
# de novo por engano.
MANTER = {
    'IT-CAN-CD65E224E7': 'area de frumento duro (ISTAT). A mencao a SDMX esta na ressalva.',
    'IT-CAN-0312ECA427': 'area de olival (ISTAT). Idem.',
    'IT-CAN-3CDDA32E89': 'area de milho (ISTAT). A ressalva avisa que a consulta '
                         'nacional NAO sustenta quebra regional — apagar isso seria pior.',
    'IT-CAN-15F34E6605': 'flonicamid: a aprovacao UE tem data-limite 30/11/2026 por '
                         'PRORROGACAO, nao renovacao. E fato regulatorio real, e a '
                         'ressalva do endpoint protege quem for reler o JSON.',
}


def colecoes():
    for a in sorted(os.listdir(ING)):
        if not a.endswith('.json') or a in ('APP-MANIFEST.json',
                                            'CANONICAL-INTELLIGENCE-MASTER.json'):
            continue
        p = os.path.join(ING, a)
        d = json.load(open(p, encoding='utf-8'))
        if isinstance(d, dict) and isinstance(d.get('RECORDS'), list):
            yield a, p, d


def main():
    vistos, reb, apa, man = set(), 0, 0, 0
    for arq, caminho, d in colecoes():
        mudou = False
        for r in d['RECORDS']:
            rid = r.get('ID')
            if rid in REBAIXAR:
                vistos.add(rid)
                r['CLAIM_DOMAIN'] = SOBRE_A_ROTA
                r['CLAIM_DOMAIN_WHY'] = REBAIXAR[rid]
                r['CLIENT_SAFE'] = False
                r['CLIENT_SAFE_WHY_NOT'] = (
                    'a alegacao nao e sobre o mercado italiano: e sobre como a '
                    'fonte foi alcancada. SABER COMO ABRIR A PORTA NAO E SABER O '
                    'QUE HA NA SALA.')
                reb += 1
                mudou = True
            elif rid in APARAR:
                vistos.add(rid)
                for campo in list(r):
                    if not isinstance(r.get(campo), str):
                        continue
                    novo = r[campo]
                    for trecho in APARAR[rid]:
                        novo = novo.replace(trecho, '')
                    if novo != r[campo]:
                        r[campo] = novo.strip()
                        base = campo
                        for suf in ('_IT', '_EN', '_ORIGINAL_RESEARCH_TEXT'):
                            if base.endswith(suf):
                                base = base[:-len(suf)]
                        for suf in ('', '_IT', '_EN', '_ORIGINAL_RESEARCH_TEXT'):
                            if base + suf != campo:
                                r.pop(base + suf, None)
                        mudou = True
                r['CLAIM_DOMAIN'] = SOBRE_O_MUNDO
                r['ROUTE_NOTE_MOVED_OUT_OF_CLAIM'] = (
                    'a frase sobre o IP e o HTTP 200 saiu da alegacao: e rota, '
                    'nao mercado. O fato de preco fica inteiro.')
                apa += 1
            elif rid in MANTER:
                vistos.add(rid)
                r['CLAIM_DOMAIN'] = SOBRE_O_MUNDO
                r['CLAIM_DOMAIN_REVIEWED'] = MANTER[rid]
                man += 1
                mudou = True
            elif r.get('CLIENT_SAFE') and not r.get('CLAIM_DOMAIN'):
                r['CLAIM_DOMAIN'] = SOBRE_O_MUNDO
                mudou = True
        if mudou:
            json.dump(d, open(caminho, 'w', encoding='utf-8'),
                      ensure_ascii=False, indent=1)

    esperados = set(REBAIXAR) | set(APARAR) | set(MANTER)
    sumiram = sorted(esperados - vistos)
    print('== R5 · DOMINIO DA ALEGACAO ==')
    print('  rebaixados (rota, nao mundo) : %d' % reb)
    print('  aparados (rota dentro da frase): %d' % apa)
    print('  lidos e mantidos             : %d' % man)
    if sumiram:
        print('  !! DECISAO SEM REGISTRO: %s' % ', '.join(sumiram))
        print('     decisao que nao encontra o seu registro envelheceu sem avisar.')
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
