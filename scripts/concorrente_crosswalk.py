#!/usr/bin/env python3
"""
CROSSWALK DE IDENTIDADE — TRADEMARK ↔ REGISTRATION ↔ COMPANY.

    python3 scripts/concorrente_crosswalk.py

A REGRA QUE MANDA AQUI JÁ CUSTOU CARO NA CASA
  do cabeçalho de `ES-REGULATORIO-ROPF-2026-08-29.sql`:
  **NOME_IGUAL != MESMO_REGISTRO.** Uma marca chamada X e um registro chamado
  X são dois documentos que usam a mesma palavra. Só isso, até que a EMPRESA
  também confira.

  Por isso o casamento exige DUAS concordâncias, não uma:
     1 · o nome normalizado da marca == o nome do produto no registro
     2 · o grupo do titular da marca == o grupo do titular do registro
  Nome sozinho nunca promove. Nome + empresa promove a `PROVED`.

E ELA JÁ REPROVOU NESTA RODADA
  `URBOLE` — a marca é da **SYNGENTA**; o registro espanhol com esse nome é da
  **ADAMA** (24157). Um casador por nome teria escrito "a Syngenta tem o
  registro do URBOLE". O crosswalk devolve `REJECTED_HOLDER_MISMATCH` e diz
  quem é o titular de cada lado — sem explicar por quê, porque nenhum dos dois
  documentos explica.

OS QUATRO ESTADOS
  PROVED     nome E empresa conferem nos dois lados
  PARTIAL    nome confere; a empresa do registro está fora da amostra e não
             foi possível confirmar nem negar a relação
  REJECTED   nome confere e a empresa é OUTRO concorrente conhecido — o par é
             recusado, e a recusa é publicada
  NOT_KNOWN  a marca não tem par de nome no registro. Não é "não existe":
             é `NO_LINK`, e a maioria das marcas fica aqui

NORMALIZAÇÃO — O QUE ELA PODE E O QUE NÃO PODE
  Pode: acento, caixa, espaço e pontuação. `PRIMO MAXX` == `Primo Maxx`.
  NÃO pode: sufixo, número, prefixo. `FENOVA S` != `FENOVA SUPER`, `CUREX 3`
  != `CUREX`. A régua de change event mediu que 2 de 10 candidatos a mudança
  de nome eram sobra de prefixo do leitor — encolher a string aqui repetiria
  o mesmo erro com outra roupa.
"""
import json
import os
import re
import sys
import unicodedata

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import registro_local  # noqa: E402

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SAIDA = os.path.join(RAIZ, 'data', 'samples', 'COMPETITOR-CROSSWALK.json')


def normalizar(s):
    """Acento, caixa e pontuação. NADA de sufixo, número ou prefixo."""
    s = unicodedata.normalize('NFKD', s or '').encode('ascii', 'ignore').decode()
    return re.sub(r'[^A-Z0-9]', '', s.upper())


def indice_do_registro(rows):
    """
    Índice por nome normalizado sobre os registros já postos na forma comum
    de `registro_local`. Um registro entra sob o nome do produto E sob cada
    nome comercial alternativo que a fonte declare — na França o campo
    `seconds noms commerciaux` é o mesmo fato que as denominações comuns
    espanholas: o MESMO registro vendido sob outro nome, não outro produto.
    """
    idx = {}
    for r in rows:
        nomes = [(r.get('PRODUCT_NAME'), 'NOME_DO_PRODUTO')]
        nomes += [(a, 'NOME_COMERCIAL_ALTERNATIVO') for a in (r.get('ALT_NAMES') or [])]
        for nome, papel in nomes:
            chave = normalizar(nome)
            if not chave:
                continue
            idx.setdefault(chave, []).append({
                'REGISTRATION_ID': r['REGISTRATION_ID'],
                'PRODUCT_NAME': r.get('PRODUCT_NAME'),
                'NOME_CASADO': nome,
                'PAPEL_DO_NOME': papel,
                'HOLDER': r.get('HOLDER'),
                'GRUPO': r.get('GRUPO'),
                'ESTADO': r.get('STATUS'),
                'COUNTRY': r.get('COUNTRY'),
                'FECHA_INSCRIPCION': r.get('DATE_REGISTRATION'),
            })
    return idx


def cruzar(marcas_por_grupo, idx):
    """Um par por (marca, registro candidato). Nenhum par é descartado em silêncio."""
    pares, sem_par = [], []
    for grupo, marcas in marcas_por_grupo.items():
        for m in marcas:
            chave = normalizar(m['TM_NAME'])
            if not chave:
                continue
            candidatos = idx.get(chave)
            if not candidatos:
                sem_par.append({'GRUPO': grupo, 'TM_NAME': m['TM_NAME'],
                                'TM_OFFICE': m['TM_OFFICE'], 'ST13': m['ST13'],
                                'ESTADO_DO_LINK': 'NOT_KNOWN',
                                'MOTIVO': 'NO_LINK — nenhum produto do registro '
                                          'espanhol tem este nome'})
                continue
            for c in candidatos:
                if c['GRUPO'] == grupo:
                    estado, motivo = 'PROVED', 'nome e grupo do titular conferem nos dois lados'
                elif c['GRUPO'] is None:
                    estado = 'PARTIAL'
                    motivo = ('o nome confere; o titular do registro está fora da '
                              'amostra e a relação societária não foi verificada')
                else:
                    estado = 'REJECTED_HOLDER_MISMATCH'
                    motivo = (f"o nome confere, mas o registro é de {c['GRUPO']} e a "
                              f'marca é de {grupo}. Nenhum dos dois documentos diz '
                              'por quê, e este crosswalk não inventa a explicação')
                pares.append({
                    'GRUPO_DA_MARCA': grupo,
                    'TM_NAME': m['TM_NAME'], 'ST13': m['ST13'],
                    'TM_OFFICE': m['TM_OFFICE'],
                    'TM_APPLICANT': m['APPLICANT_NAME'],
                    'TM_APPLICATION_DATE': m['APPLICATION_DATE'],
                    'TM_STATUS': m['TM_STATUS'],
                    'AGROCHEMICAL_RELEVANCE': m['AGROCHEMICAL_RELEVANCE'],
                    'REGISTRATION_ID': c['REGISTRATION_ID'],
                    'REGISTRATION_PRODUCT': c['PRODUCT_NAME'],
                    'REGISTRATION_HOLDER': c['HOLDER'],
                    'REGISTRATION_GRUPO': c['GRUPO'],
                    'REGISTRATION_ESTADO': c['ESTADO'],
                    'REGISTRATION_DATE': c['FECHA_INSCRIPCION'],
                    'ESTADO_DO_LINK': estado, 'MOTIVO': motivo,
                })
    return pares, sem_par


def contrafactual_frouxo(marcas_por_grupo, idx):
    """
    Quantos pares a MAIS um casador por prefixo criaria — e quantos deles
    estariam errados. É a medida de ruído do §10-E da missão, feita com número
    em vez de opinião: o casador frouxo é RODADO, e não imaginado.
    """
    chaves = list(idx)
    extras, conflitantes, total_extras = [], 0, 0
    for grupo, marcas in marcas_por_grupo.items():
        for m in marcas:
            k = normalizar(m['TM_NAME'])
            if len(k) < 4 or k in idx:
                continue          # já casou exato, ou é curto demais para prefixo
            for ck in chaves:
                if ck == k or not (ck.startswith(k) or k.startswith(ck)):
                    continue
                for c in idx[ck]:
                    errado = c['GRUPO'] != grupo
                    conflitantes += errado
                    total_extras += 1
                    if len(extras) < 40:
                        extras.append({
                            'TM_NAME': m['TM_NAME'], 'GRUPO_DA_MARCA': grupo,
                            'REGISTRO_QUE_SERIA_LIGADO': c['PRODUCT_NAME'],
                            'REGISTRATION_ID': c['REGISTRATION_ID'],
                            'TITULAR_DO_REGISTRO': c['HOLDER'],
                            'ESTARIA_ERRADO': errado})
                    break
    return extras, conflitantes, total_extras


def main():
    with open(os.path.join(RAIZ, 'data', 'samples',
                           'COMPETITOR-IP-TMVIEW.json'), encoding='utf-8') as f:
        ip = json.load(f)
    # os registros já vêm na forma comum dos três países; aqui só a Espanha
    rows, _ = registro_local.carregar('ES')

    # só marcas com efeito na Espanha entram: o registro do outro lado é espanhol.
    # ES = marca nacional. EM = marca da União Europeia, que protege a Espanha.
    marcas_por_grupo, universo = {}, 0
    for grupo, offs in ip['POR_CONCORRENTE'].items():
        vistos, lista = set(), []
        for o in ('ES', 'EM'):
            v = offs.get(o, {})
            if v.get('ESTADO') != 'OK':
                continue
            for m in v['MARCAS']:
                universo += 1
                k = (normalizar(m['TM_NAME']), o)
                if k in vistos:
                    continue
                vistos.add(k)
                lista.append(m)
        marcas_por_grupo[grupo] = lista

    idx = indice_do_registro(rows)
    pares, sem_par = cruzar(marcas_por_grupo, idx)
    extras, conflitantes, total_extras = contrafactual_frouxo(marcas_por_grupo, idx)

    por_estado = {}
    for p in pares:
        por_estado[p['ESTADO_DO_LINK']] = por_estado.get(p['ESTADO_DO_LINK'], 0) + 1
    por_estado['NOT_KNOWN'] = len(sem_par)
    testadas = sum(len(v) for v in marcas_por_grupo.values())

    provados = [p for p in pares if p['ESTADO_DO_LINK'] == 'PROVED']
    por_grupo = {}
    for p in provados:
        por_grupo[p['GRUPO_DA_MARCA']] = por_grupo.get(p['GRUPO_DA_MARCA'], 0) + 1

    art = {
        'SOURCE_ID': 'COMPETITOR-CROSSWALK',
        'source': 'derivação sobre COMPETITOR-IP-TMVIEW + ROPF (ES)',
        'SOURCE_LOCATION': 'interno — derivado',
        'FACT_LOCATION': 'ES',
        'CAMADA_DO_PILOTO': 'IDENTITY CROSSWALK',
        'captured_at': ip['captured_at'],

        'REGRA': ('duas concordâncias obrigatórias: nome normalizado do produto E '
                  'grupo do titular. Nome sozinho nunca promove a PROVED.'),
        'NORMALIZACAO': ('acento, caixa e pontuação. NÃO remove sufixo, número nem '
                         'prefixo: FENOVA S != FENOVA SUPER, CUREX 3 != CUREX.'),
        'ESCOPO': ('marcas com efeito na Espanha — escritório ES (nacional) e EM '
                   '(marca da UE, que protege a Espanha). IT e FR ficam de fora '
                   'deste crosswalk porque o registro do outro lado é espanhol.'),

        'UNIVERSO': {
            'MARCAS_ES_MAIS_EM_COLETADAS': universo,
            'MARCAS_TESTADAS_APOS_DEDUPLICAR': testadas,
            'PRODUTOS_NO_REGISTRO_ES': len(rows),
            'NOMES_DISTINTOS_NO_REGISTRO': len(idx),
        },
        'POR_ESTADO': por_estado,
        'PROVED_POR_GRUPO': por_grupo,
        'TAXA_DE_LIGACAO': (
            f'{len(provados)} pares PROVED em {testadas} marcas testadas — '
            f'{100 * len(provados) / testadas:.1f}%. A maioria esmagadora das marcas '
            'de um concorrente NÃO tem registro espanhol de mesmo nome.'),

        'RUIDO_MEDIDO': {
            'O_QUE_FOI_TESTADO': ('um casador por PREFIXO foi realmente rodado sobre '
                                  'as mesmas marcas, para medir o que a frouxidão '
                                  'produziria. Ele não foi usado para gerar links.'),
            'PARES_EXTRAS_QUE_ELE_CRIARIA': total_extras,
            'DESTES_COM_TITULAR_ERRADO': conflitantes,
            'TAXA_DE_FALSO_LINK_DO_CASADOR_FROUXO': (
                f'{conflitantes} de {total_extras}' if total_extras else '0 de 0'),
            'AMOSTRA': extras[:20],
            'REJEITADOS_PELO_CASADOR_ESTRITO': [
                p for p in pares if p['ESTADO_DO_LINK'] == 'REJECTED_HOLDER_MISMATCH'],
        },

        'PARES': pares,
        'SEM_PAR': sem_par[:200],
        'SEM_PAR_TOTAL': len(sem_par),

        'O_QUE_UM_PAR_PROVED_PROVA': (
            'que existe uma marca registrada com este nome e um produto autorizado '
            'com este nome, e que os dois titulares pertencem ao mesmo grupo '
            'declarado. NADA ALÉM DISSO.'),
        'O_QUE_ELE_NAO_PROVA': [
            'não prova que o produto está à venda',
            'não prova que a marca foi depositada PARA aquele produto',
            'não prova lançamento, estratégia, nem intenção',
            'não prova relação societária: o agrupamento de titular é declarado '
            'em GRUPOS, por prefixo, e não lido de registro societário',
        ],
    }

    with open(SAIDA, 'w', encoding='utf-8') as f:
        json.dump(art, f, ensure_ascii=False, indent=2)

    print(f'marcas testadas (ES + EM, deduplicadas): {testadas}')
    for e, n in sorted(por_estado.items(), key=lambda kv: -kv[1]):
        print(f'  {n:>5}  {e}')
    print(f'\nPROVED por grupo: {por_grupo}')
    print(f'casador frouxo criaria {total_extras} pares extras · '
          f'{conflitantes} com titular errado')
    print('gravado:', SAIDA)


if __name__ == '__main__':
    main()
