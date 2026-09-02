#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RECHAVEIA AS FONTES — para que a chave que liga volte a ligar.

    python3 scripts/v21_fontes_rechavear.py

O DEFEITO
----------
`SOURCES.json` guardava as fontes sob dois nomes:

    IT-SRC-MINISTERO   (as que vieram do handoff anterior)
    SRCX_ARPAE_IT      (as que vieram da last-mile)

E todas as 23 coleções citavam um terceiro:

    SRC_ARPAE_IT

Resultado: de 123 identificadores de fonte citados no pacote, **119 não achavam
ninguém**. O portal mostraria «fonte: SRC_ARPAE_IT» e não teria como abrir o
nome, a URL ou o estado de acesso dela.

    UMA CHAVE ESTRANGEIRA QUE NÃO ENCONTRA A LINHA NÃO É UMA CHAVE:
    É UM TEXTO QUE PARECE UMA.

O `X` foi posto para distinguir «fonte nova» de «fonte antiga». Distinguir era
desnecessário — `PROVENANCE` e `ORIGIN_LAYER` já dizem isso — e custou a junção.

A CORREÇÃO
-----------
A chave primária da fonte passa a ser a MESMA que o pacote inteiro já cita: a
derivada do host, `SRC_<HOST>`. Ela não é escolha nova; é a que estava em uso.

    QUANDO O NOME DE DENTRO BRIGA COM O NOME DE FORA, QUEM MANDA É O DE FORA —
    porque é ele que já está escrito em 123 lugares.

O identificador antigo não some: fica em `ID_ANTERIOR`, para quem tiver um link
velho na mão.
"""
import json
import os
import re
from collections import Counter
from urllib.parse import urlsplit

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ING = os.path.join(ROOT, 'build', 'ITALY-REALITY-HANDOFF-V2.1', 'DESIGN-INGEST')


def chave_do_host(url):
    """SRC_<HOST> — a mesma regra que gerou os identificadores já citados."""
    h = (urlsplit(str(url or '')).netloc or '').lower()
    h = re.sub(r'^www\.', '', h)
    return 'SRC_' + re.sub(r'[^A-Z0-9]+', '_', h.upper()).strip('_')


def main():
    p = os.path.join(ING, 'SOURCES.json')
    d = json.load(open(p, encoding='utf-8'))

    # quem é citado, e quantas vezes — a demanda real manda na chave
    citado = Counter()
    for arq in sorted(os.listdir(ING)):
        if not arq.endswith('.json') or arq in ('SOURCES.json',):
            continue
        dd = json.load(open(os.path.join(ING, arq), encoding='utf-8'))
        for r in dd.get('RECORDS') or []:
            if isinstance(r, dict):
                for s in (r.get('SOURCE_IDS') or []):
                    citado[s] += 1

    por_chave, colisao = {}, []
    for r in d['RECORDS']:
        url = (r.get('SOURCE_URLS') or [None])[0] or r.get('URL')
        # 1º o que o próprio registro declara; 2º o host da URL
        declarada = next((s for s in (r.get('SOURCE_IDS') or [])
                          if str(s).startswith('SRC_')), None)
        nova = declarada or chave_do_host(url)
        # ⚠️ SEM URL NAO HA HOST, E SEM HOST NAO HA CHAVE. A primeira versao
        # gerou `SRC_` e `SRC___NONE` a partir de URL vazia — identificadores que
        # nao identificam nada e ainda parecem legitimos numa lista.
        #
        #     QUANDO NAO DA PARA DERIVAR A CHAVE, O CERTO E FICAR COM A ANTIGA,
        #     NAO INVENTAR UMA BONITA.
        if nova in ('SRC_', 'SRC__', 'SRC___NONE') or not url:
            nova = r['ID']
            r['ID_KEEP_NOTE'] = (
                'esta fonte nao tem URL, entao nao ha host de onde derivar a '
                'chave. O identificador original fica.')
        if nova in por_chave:
            # ⚠️ MESMO HOST, FONTE DIFERENTE. Não se funde: um site publica
            # estatística E preço, e são duas fontes com dois estados de acesso.
            outro = por_chave[nova]
            u_outro = (outro.get('SOURCE_URLS') or [None])[0] or ''
            if str(url).rstrip('/') == str(u_outro).rstrip('/'):
                colisao.append({'DESCARTADA': r['ID'], 'MANTIDA': outro['ID'],
                                'MOTIVO': 'mesma URL'})
                continue
            cauda = re.sub(r'[^A-Z0-9]+', '_',
                           (urlsplit(str(url)).path or '').upper()).strip('_')
            nova = (nova + '__' + cauda[-24:]).strip('_')
            r['ID_NOTE'] = ('o host ja tinha fonte com outra URL; o caminho entra '
                            'na chave. UM HOST PUBLICA MAIS DE UMA COISA.')
        if r['ID'] != nova:
            # ⚠️ O NOME ANTIGO CONTINUA VALENDO. Rechavear sem guardar o apelido
            # troca um conjunto de citacoes quebradas por outro: `IT-SRC-MINISTERO`
            # era citado 12 vezes e sumiria.
            #
            #     RENOMEAR NAO PODE QUEBRAR QUEM JA CHAMAVA PELO NOME VELHO.
            r['ID_ANTERIOR'] = r['ID']
            r['ID_ALIASES'] = sorted(set((r.get('ID_ALIASES') or []) + [r['ID']]))
            r['ID_REKEY_NOTE'] = (
                'a chave primaria passou a ser a mesma que as 23 colecoes ja '
                'citavam (SRC_<HOST>). A anterior (%s) continua resolvendo por '
                'ID_ALIASES.' % r['ID'])
            r['ID'] = nova
        por_chave[nova] = r

    d['RECORDS'] = list(por_chave.values())
    d['COUNT_TOTAL'] = len(d['RECORDS'])
    d['COUNT_CLIENT_SAFE'] = sum(1 for x in d['RECORDS'] if x.get('CLIENT_SAFE'))
    d['PRIMARY_KEY'] = 'ID'
    d['PRIMARY_KEY_NOTE'] = (
        'ID = SRC_<HOST>, derivado da URL. E a MESMA chave que SOURCE_IDS usa em '
        'todas as colecoes: e por ela que o portal abre o nome, a URL e o estado '
        'de acesso da fonte. IDs anteriores ficam em ID_ANTERIOR.')
    d['REKEY_COLLAPSED'] = colisao

    # ── o sentinela não é uma fonte, e precisa dizer isso ────────────────────
    #
    # ⚠️ `SRC_NAO_DECLARADA` aparece 5.470 vezes. Ele não é o endereço de nada:
    # é a marca honesta de «este registro não declarou fonte». Sem uma linha que
    # o explique, a tela mostra 5.470 links quebrados — e link quebrado o usuário
    # lê como defeito do portal, não como ausência declarada do dado.
    #
    #     A AUSÊNCIA PRECISA DE UM LUGAR ONDE MORAR, SENÃO VIRA ERRO.
    for chave, nome, porque in (
        ('SRC_NAO_DECLARADA', 'fonte não declarada',
         'o registro de origem nao trouxe URL nem nome de fonte. Nao e link '
         'quebrado: e ausencia declarada. A tela mostra o aviso, nunca um link.'),
        ('SRC_DESCONHECIDA', 'fonte desconhecida',
         'igual a SRC_NAO_DECLARADA, com outra grafia herdada do pacote anterior. '
         'As duas significam a mesma coisa e nenhuma e endereco.')):
        if chave in citado and chave not in por_chave:
            por_chave[chave] = {
                'ID': chave, 'ENTITY_TYPE': 'SOURCE_SENTINEL',
                'PROVENANCE': 'SENTINELA', 'ORIGIN_LAYER': 'DERIVED_V2_1',
                'ORIGIN_LAYER_NOTE':
                    'este registro nao veio de camada nenhuma: foi criado aqui '
                    'para dar endereco a uma ausencia que ja era citada 5.470 '
                    'vezes sem ter onde morar.',
                'QA_STATUS': 'QA_UNREVIEWED',
                'CLIENT_SAFE': False, 'SOURCE_URLS': [], 'SOURCE_IDS': [],
                'NAME': nome, 'IS_SOURCE': False,
                'WHAT_IT_PUBLISHES': 'nada — nao e uma fonte',
                'ACCESS_STATE': 'NAO_SE_APLICA',
                'SENTINEL_NOTE': porque,
                'CITADO_VEZES': citado[chave],
            }

    # quanto passou a resolver — contando os apelidos
    apelido = {}
    for k, r in por_chave.items():
        for a in (r.get('ID_ALIASES') or []):
            apelido[a] = k
    tem = set(por_chave) | set(apelido)
    resolve = sum(n for k, n in citado.items() if k in tem)
    orfa = {k: n for k, n in citado.items() if k not in tem}
    d['RECORDS'] = list(por_chave.values())
    d['COUNT_TOTAL'] = len(d['RECORDS'])
    d['COUNT_CLIENT_SAFE'] = sum(1 for x in d['RECORDS'] if x.get('CLIENT_SAFE'))
    d['ID_ALIAS_MAP'] = apelido
    d['ID_ALIAS_NOTE'] = (
        'identificador antigo -> identificador atual. Quem tiver um link velho '
        'na mao continua chegando ao mesmo lugar.')
    d['CITATION_HEALTH'] = {
        'CITACOES_TOTAIS': sum(citado.values()),
        'CITACOES_QUE_RESOLVEM': resolve,
        'CITADOS_SEM_CADASTRO': [{'ID': k, 'VEZES': n}
                                 for k, n in sorted(orfa.items(),
                                                    key=lambda x: -x[1])],
        'NOTA': 'fonte citada sem cadastro NAO e erro de digitacao: e fonte cujo '
                'registro nunca foi criado. Fica listada aqui, com a contagem, em '
                'vez de sumir — para o portal mostrar o identificador cru e o '
                'aviso, e nunca um link que nao abre.',
    }

    json.dump(d, open(p, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('fontes: %d · colapsadas por URL igual: %d' % (len(d['RECORDS']), len(colisao)))
    print('citacoes: %d de %d resolvem (%.1f%%)'
          % (resolve, sum(citado.values()), 100.0 * resolve / max(1, sum(citado.values()))))
    print('IDs citados que ainda nao tem cadastro: %d' % len(orfa))
    for k, n in sorted(orfa.items(), key=lambda x: -x[1])[:12]:
        print('   %-46s citado %dx' % (k, n))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
