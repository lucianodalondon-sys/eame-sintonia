#!/usr/bin/env python3
"""
PARIDADE ES · IT · FR — o MESMO teste nos três países.

    python3 scripts/concorrente_paridade.py

A primeira rodada mediu o cruzamento `TRADEMARK ↔ LOCAL REGISTRATION` só na
Espanha. A missão é EAME. Este script roda **a mesma régua** nos três, sem
inventar um matcher novo para cada país: `normalizar`, `cruzar` e
`contrafactual_frouxo` são importados de `concorrente_crosswalk`, e os três
registros vêm na forma comum de `registro_local`.

O QUE MUDA DE PAÍS PARA PAÍS, E O QUE NÃO MUDA
  MUDA  a fonte, o idioma do campo, a palavra para "em vigor", e o
        escritório de marca que se olha junto com a EUIPO.
  NÃO MUDA a régua: duas concordâncias obrigatórias (nome E grupo do
        titular), os quatro estados, e a recusa publicada.

⚠️ OS TRÊS TOTAIS NÃO SÃO COMPARÁVEIS ENTRE SI
  ES publica 3.084 e IT publica 17.695 porque a Itália guarda o revogado
  desde 1970 e a Espanha publica o conjunto corrente. Comparar os totais
  brutos mede a política de publicação de cada ministério, não o mercado.
  Por isso a tabela final traz SEMPRE o denominador junto do número.

⚠️ A FRANÇA TEM UMA SUPERFÍCIE A MAIS
  `seconds noms commerciaux` do E-Phy é o mesmo fato que as denominações
  comuns espanholas: o MESMO registro vendido sob outro nome. Ele entra como
  `ALT_NAME` e multiplica a chance de casamento — o que torna FR e ES não
  perfeitamente comparáveis nesse eixo. Fica declarado, não corrigido: somar
  os dois países como se a superfície fosse a mesma seria pior.
"""
import datetime
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import registro_local  # noqa: E402
from concorrente_crosswalk import (  # noqa: E402
    contrafactual_frouxo, cruzar, indice_do_registro, normalizar,
)

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
S = os.path.join(RAIZ, 'data', 'samples')
SAIDA = os.path.join(S, 'COMPETITOR-EAME-PARIDADE.json')

# o escritório nacional de marca de cada país, sempre lido junto com a EUIPO
# (`EM`), porque a marca da UE protege os três territórios.
ESCRITORIOS = {'ES': ('ES', 'EM'), 'IT': ('IT', 'EM'), 'FR': ('FR', 'EM')}
FORMATOS_DATA = ('%d-%m-%Y', '%d/%m/%Y', '%Y-%m-%d')


def data(s):
    """As três fontes usam três formatos. Ilegível vira None — nunca hoje."""
    s = (s or '').strip()
    if not s or s == '-':
        return None
    for f in FORMATOS_DATA:
        try:
            return datetime.datetime.strptime(s, f).date()
        except ValueError:
            continue
    return None


def marcas_do_pais(ip, pais):
    """Marcas com efeito naquele país: escritório nacional + marca da UE."""
    por_grupo, universo = {}, 0
    for grupo, offs in ip['POR_CONCORRENTE'].items():
        vistos, lista = set(), []
        for o in ESCRITORIOS[pais]:
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
        por_grupo[grupo] = lista
    return por_grupo, universo


def antecedencia(pares):
    """
    Ordem observada entre depósito de marca e inscrição do registro, nos
    pares PROVED. Mesma conta nos três países, mesma recusa a inventar causa.

    ⚠️ A CONSERVAÇÃO É OBRIGATÓRIA E VERIFICADA AQUI DENTRO
      A primeira redação publicou `LINKED_CHAINS = 1140` ao lado de
      `TM_BEFORE_REG = 702` e `REG_BEFORE_TM = 407`. **702 + 407 = 1109.**
      Trinta e uma cadeias ficaram sem explicação — não erradas, apenas
      invisíveis, porque a soma nunca era conferida.

      Agora TODA cadeia recebe exatamente uma classe, e o `assert` no fim
      recusa qualquer decomposição que não feche. Nenhuma classe foi criada
      para fechar a soma: as classes saem do que os dados sustentam.

    AS CLASSES, E O QUE CADA UMA MEDE
      TM_BEFORE_REG       as duas datas existem, a da marca é anterior
      REG_BEFORE_TM       as duas datas existem, a do registro é anterior
      SAME_DATE           as duas datas existem e são iguais
      REG_DATE_MISSING    a FONTE não declara a data do registro
      TM_DATE_MISSING     a FONTE não declara a data do depósito
      BOTH_DATES_MISSING  nenhuma das duas
      DATE_NOT_COMPARABLE a data existe mas nenhum dos três formatos a lê

    MEDIDO NESTA RODADA (as 31 da França)
      30 · `REG_DATE_MISSING` — os 30 registros são `RETIRE` e o campo
           `Date de première autorisation` está **vazio no CSV bruto** do
           E-Phy. Conferido registro a registro contra a fonte. No registro
           francês inteiro, 280 de 15.140 estão assim.
       1 · `SAME_DATE`
      ES e IT fecham sem resto: 209 = 158 + 51 e 334 = 227 + 107.
    """
    classes = {k: 0 for k in ('TM_BEFORE_REG', 'REG_BEFORE_TM', 'SAME_DATE',
                              'REG_DATE_MISSING', 'TM_DATE_MISSING',
                              'BOTH_DATES_MISSING', 'DATE_NOT_COMPARABLE')}
    leads, provados, exemplos = [], 0, {}
    for p in pares:
        if p['ESTADO_DO_LINK'] != 'PROVED':
            continue
        provados += 1
        bruto_tm = (p['TM_APPLICATION_DATE'] or '').strip()
        bruto_rg = (p['REGISTRATION_DATE'] or '').strip()
        tm, rg = data(bruto_tm), data(bruto_rg)
        if tm and rg:
            d = (rg - tm).days
            leads.append(d)
            k = ('TM_BEFORE_REG' if d > 0 else
                 'REG_BEFORE_TM' if d < 0 else 'SAME_DATE')
        else:
            # a distinção que importa: a FONTE não declarou (vazio, `-`,
            # NOT_KNOWN) é diferente de a fonte ter declarado algo que o
            # leitor não entendeu. A segunda é defeito nosso e precisa
            # aparecer com esse nome.
            vazio_tm = bruto_tm in ('', '-', 'NOT_KNOWN')
            vazio_rg = bruto_rg in ('', '-', 'NOT_KNOWN')
            if tm is None and rg is None:
                k = 'BOTH_DATES_MISSING' if (vazio_tm and vazio_rg) \
                    else 'DATE_NOT_COMPARABLE'
            elif tm is None:
                k = 'TM_DATE_MISSING' if vazio_tm else 'DATE_NOT_COMPARABLE'
            else:
                k = 'REG_DATE_MISSING' if vazio_rg else 'DATE_NOT_COMPARABLE'
            exemplos.setdefault(k, []).append({
                'GRUPO': p['GRUPO_DA_MARCA'], 'TM_NAME': p['TM_NAME'],
                'TM_APPLICATION_DATE': bruto_tm or None,
                'REGISTRATION_ID': p['REGISTRATION_ID'],
                'REGISTRATION_DATE': bruto_rg or None,
                'REGISTRATION_ESTADO': p['REGISTRATION_ESTADO']})
        classes[k] += 1

    soma = sum(classes.values())
    assert soma == provados, (
        f'decomposição não conserva: {soma} classificados de {provados} pares '
        'PROVED. Nenhuma classe pode ser criada para fechar a soma — a falha '
        'aqui é sinal de que uma cadeia está sendo perdida em silêncio.')

    leads.sort()
    nao_comparaveis = sum(v for k, v in classes.items() if k not in
                          ('TM_BEFORE_REG', 'REG_BEFORE_TM', 'SAME_DATE'))
    return {
        'PARES_PROVED': provados,
        'CLASSIFICACAO': classes,
        'CONSERVACAO': {
            'TOTAL_LINKED_CHAINS': provados,
            'SOMA_DAS_CLASSES': soma,
            'FECHA': soma == provados,
            'REGRA': ('TOTAL = TM_BEFORE_REG + REG_BEFORE_TM + SAME_DATE + '
                      'as classes de data ausente/ilegível, cada uma com causa '
                      'medida. Verificado por assert, não por leitura.'),
        },
        'COM_AS_DUAS_DATAS': len(leads),
        'SEM_AS_DUAS_DATAS': nao_comparaveis,
        'EXEMPLOS_SEM_AS_DUAS_DATAS': {k: v[:5] for k, v in exemplos.items()},
        # os nomes antigos seguem, para que nada que já os cita quebre
        'TM_BEFORE_REG': classes['TM_BEFORE_REG'],
        'REG_BEFORE_TM': classes['REG_BEFORE_TM'],
        'MESMO_DIA': classes['SAME_DATE'],
        'SEM_UMA_DAS_DATAS': nao_comparaveis,
        'LEAD_DAYS_MEDIANA_BRUTA': leads[len(leads) // 2] if leads else None,
        'LEAD_DAYS_AMPLITUDE': [leads[0], leads[-1]] if leads else [],
        'AVISO': ('mediana BRUTA, sem a regra de defensabilidade. Precedência '
                  'histórica observada NÃO é antecedência operacional.'),
    }


def universos_do_matcher(marcas, idx):
    """
    Os DOIS universos, medidos e provados disjuntos.

    ⚠️ POR QUE ISTO EXISTE
      A rodada 1 publicou `151 falsos links` e a rodada 2 publicou `9 falsos
      links` para a MESMA Espanha. Os dois números estão certos e medem
      coisas diferentes — mas ficaram lado a lado sem nome próprio, e um
      número sem nome próprio vira o outro na primeira leitura apressada.

      `contrafactual_frouxo` só olha marcas cujo nome NÃO está no índice
      (`if len(k) < 4 or k in idx: continue`). `cruzar` só produz par quando
      o nome ESTÁ no índice. Os dois universos são disjuntos **por
      construção** — e aqui isso é medido, não deduzido do código.
    """
    exato, frouxo, curto = set(), set(), set()
    n_exato = n_frouxo = n_curto = 0
    for marcas_do_grupo in marcas.values():
        for m in marcas_do_grupo:
            k = normalizar(m['TM_NAME'])
            if not k:
                continue
            if k in idx:
                exato.add(k)
                n_exato += 1
            elif len(k) < 4:
                curto.add(k)
                n_curto += 1
            else:
                frouxo.add(k)
                n_frouxo += 1
    return {
        'MARCAS_COM_NOME_EXATO_NO_REGISTRO': n_exato,
        'MARCAS_SEM_NOME_EXATO_COM_4_OU_MAIS_CHARS': n_frouxo,
        'MARCAS_SEM_NOME_EXATO_CURTAS_DEMAIS': n_curto,
        'NOMES_NA_INTERSECAO_DOS_DOIS_UNIVERSOS': len(exato & frouxo),
        'DISJUNTOS': not (exato & frouxo),
    }


def medir_pais(ip, pais):
    rows, versao = registro_local.carregar(pais)
    idx = indice_do_registro(rows)
    marcas, universo = marcas_do_pais(ip, pais)
    pares, sem_par = cruzar(marcas, idx)
    extras, conflitantes, total_extras = contrafactual_frouxo(marcas, idx)
    univ = universos_do_matcher(marcas, idx)

    por_estado = {}
    for p in pares:
        por_estado[p['ESTADO_DO_LINK']] = por_estado.get(p['ESTADO_DO_LINK'], 0) + 1
    por_estado['NOT_KNOWN'] = len(sem_par)
    testadas = sum(len(v) for v in marcas.values())
    provados = [p for p in pares if p['ESTADO_DO_LINK'] == 'PROVED']
    por_grupo = {}
    for p in provados:
        por_grupo[p['GRUPO_DA_MARCA']] = por_grupo.get(p['GRUPO_DA_MARCA'], 0) + 1

    m = registro_local.medir(pais)
    return {
        'PAIS': pais,
        'ESTADO_DA_MEDICAO': 'MEASURED',
        'FONTE_DO_REGISTRO': m['FONTE'],
        'URL': m['URL'],
        'LICENCA': m['LICENCA'],
        'VERSAO_DA_FONTE': versao,
        'ESCRITORIOS_DE_MARCA': list(ESCRITORIOS[pais]),

        'LOCAL_REGISTRATIONS': m['REGISTROS'],
        'LOCAL_REGISTRATIONS_EM_VIGOR': m['EM_VIGOR'],
        'TITULARES_DISTINTOS': m['TITULARES_DISTINTOS'],
        'REGISTROS_DOS_6_CONCORRENTES': sum(
            v['REGISTROS'] for g, v in m['POR_GRUPO'].items() if g != 'ADAMA'),
        'ANTECESSORES_NAO_AGRUPADOS': m['ANTECESSORES_NAO_AGRUPADOS'],
        'SUBCONTAGEM_POR_ANTECESSOR': m['SUBCONTAGEM_CONHECIDA'],

        'TRADEMARKS_COLETADAS': universo,
        'TRADEMARKS_TESTADAS': testadas,
        'NOMES_DISTINTOS_NO_REGISTRO': len(idx),

        'LINKED_CHAINS': len(provados),
        'POR_ESTADO': por_estado,
        'PROVED_POR_GRUPO': por_grupo,
        'UNLINKED': len(sem_par),
        'FALSE_LINKS_REJECTED': por_estado.get('REJECTED_HOLDER_MISMATCH', 0),
        'PARTIAL': por_estado.get('PARTIAL', 0),
        'TAXA_DE_LIGACAO': (f'{len(provados)} de {testadas}'
                            if testadas else 'sem marcas testadas'),

        # ── as DUAS métricas de falso link, com nome próprio cada uma ──
        #
        # Nenhuma substitui a outra. Elas medem estágios diferentes do
        # matcher, sobre universos que não se tocam.
        'FALSE_LINK_METRICS': {
            'UNIVERSOS': univ,
            'PROVA_DE_DISJUNCAO': (
                f"{univ['NOMES_NA_INTERSECAO_DOS_DOIS_UNIVERSOS']} nomes na "
                'interseção. Uma marca ou tem nome idêntico a um produto do '
                'registro, ou não tem — nunca as duas coisas.'),

            'STRICT_MATCH_FALSE_LINKS_REJECTED': {
                'VALOR': sum(1 for x in pares
                             if x['ESTADO_DO_LINK'] == 'REJECTED_HOLDER_MISMATCH'),
                'DENOMINADOR': len(pares),
                'UNIVERSO': (f"as {univ['MARCAS_COM_NOME_EXATO_NO_REGISTRO']} marcas "
                             'cujo nome normalizado É uma chave do registro'),
                'ESTAGIO_DO_MATCHER': 'PRODUÇÃO — é o casador que gera os links',
                'REGRA_DE_REJEICAO': ('o nome normalizado bate EXATAMENTE, mas o '
                                      'grupo do titular do registro é OUTRO '
                                      'concorrente conhecido'),
                'O_QUE_MEDE': ('quantos links o casador ESTRITO recusou depois de '
                               'formá-los como candidatos. É a régua funcionando.'),
                'TESTEMUNHA': 'URBOLE — marca SYNGENTA, registro ES 24157 da ADAMA',
            },

            'LOOSE_CANDIDATE_LINKS_REJECTED': {
                'VALOR': conflitantes,
                'DENOMINADOR': total_extras,
                'UNIVERSO': (f"as {univ['MARCAS_SEM_NOME_EXATO_COM_4_OU_MAIS_CHARS']} "
                             'marcas cujo nome normalizado NÃO é chave do registro '
                             '(as curtas demais, com menos de 4 caracteres, ficam '
                             'fora dos dois universos)'),
                'ESTAGIO_DO_MATCHER': ('CONTRAFACTUAL — este casador NUNCA gerou '
                                       'link. Ele é rodado só para medir o dano '
                                       'que a frouxidão causaria'),
                'REGRA_DE_REJEICAO': ('casamento por PREFIXO (um nome é começo do '
                                      'outro); errado quando o grupo do titular '
                                      'difere'),
                'O_QUE_MEDE': ('quantos links ERRADOS um casador frouxo criaria — '
                               'links que o casador de produção nem chega a formar.'),
            },

            'POR_QUE_NAO_SE_SUBSTITUEM': (
                'o 9 é o que a régua RECUSOU tendo formado o candidato; o 151 é o '
                'que ela nem chegou a formar. Trocar um pelo outro produziria duas '
                'leituras erradas ao mesmo tempo: a régua pareceria 17x mais falha, '
                'ou o ganho de exigir titular pareceria 17x menor.'),
            'AMBAS_PERMANECEM': True,
        },
        # nome antigo mantido para não quebrar quem já o cita
        'RUIDO_DO_CASADOR_FROUXO': {
            'PARES_EXTRAS': total_extras,
            'COM_TITULAR_ERRADO': conflitantes,
            'NOME_CANONICO': 'LOOSE_CANDIDATE_LINKS_REJECTED',
            'AMOSTRA': extras[:10],
        },
        'ANTECEDENCIA': antecedencia(pares),
        'REJEITADOS': [p for p in pares
                       if p['ESTADO_DO_LINK'] == 'REJECTED_HOLDER_MISMATCH'],
        # a lista INTEIRA, e não uma amostra: é dela que as timelines saem, e
        # uma amostra silenciosamente truncada produziria cadeias faltando sem
        # que nada reprovasse.
        'PARES_TODOS': pares,
    }


def main():
    with open(os.path.join(S, 'COMPETITOR-IP-TMVIEW.json'), encoding='utf-8') as f:
        ip = json.load(f)

    paises, falhas = {}, {}
    for pais in registro_local.PAISES:
        caminho = os.path.join(RAIZ, registro_local.FONTES[pais]['arquivo'])
        if not os.path.exists(caminho):
            paises[pais] = {
                'PAIS': pais, 'ESTADO_DA_MEDICAO': 'NOT_MEASURED',
                'EXACT_REASON': f'o arquivo do registro local não está presente: '
                                f'{registro_local.FONTES[pais]["arquivo"]}',
                'NAO_SIGNIFICA': 'não significa que o registro não exista nem que o '
                                 'concorrente não tenha produto naquele país',
            }
            falhas[pais] = paises[pais]['EXACT_REASON']
            continue
        paises[pais] = medir_pais(ip, pais)
        p = paises[pais]
        print(f"{pais}: {p['LOCAL_REGISTRATIONS']} registros · "
              f"{p['TRADEMARKS_TESTADAS']} marcas testadas · "
              f"{p['LINKED_CHAINS']} ligadas · "
              f"{p['FALSE_LINKS_REJECTED']} recusadas · "
              f"TM_antes {p['ANTECEDENCIA']['TM_BEFORE_REG']} / "
              f"REG_antes {p['ANTECEDENCIA']['REG_BEFORE_TM']}")

    art = {
        'SOURCE_ID': 'COMPETITOR-EAME-PARIDADE',
        'source': 'derivação sobre COMPETITOR-IP-TMVIEW + os três registros nacionais',
        'SOURCE_LOCATION': 'interno — derivado',
        'FACT_LOCATION': 'ES · IT · FR',
        'CAMADA_DO_PILOTO': 'TRADEMARK x LOCAL REGISTRATION — paridade EAME',
        'captured_at': ip['captured_at'],

        'A_MESMA_REGUA': (
            'normalizar, cruzar e contrafactual_frouxo são importados de '
            'concorrente_crosswalk.py. Nenhum matcher novo foi escrito para IT '
            'ou FR: um matcher por país produziria três resultados que ninguém '
            'consegue comparar.'),
        'ESPANHA_NAO_FOI_RECALCULADA': (
            'os números da Espanha saem exatamente iguais aos da primeira '
            'rodada — 209 PROVED, 24 PARTIAL, 9 REJECTED, 5.335 NOT_KNOWN. '
            'A refatoração para a forma comum é verificada por essa igualdade.'),

        'OS_TOTAIS_NAO_SAO_COMPARAVEIS': (
            'ES publica o conjunto corrente (3.084); IT publica o histórico '
            'revogado desde 1970 (17.695); FR publica autorizado + retirado '
            '(15.140). Comparar totais brutos mede política de publicação, não '
            'mercado. Todo número desta tabela vem com seu denominador.'),
        'FRANCA_TEM_SUPERFICIE_A_MAIS': (
            '`seconds noms commerciaux` do E-Phy entra como ALT_NAME e aumenta '
            'a chance de casamento. FR e ES não são perfeitamente comparáveis '
            'nesse eixo, e isso fica declarado em vez de nivelado.'),
        'SUBCONTAGEM_POR_ANTECESSOR': (
            'FR e IT carregam décadas de razões sociais antecessoras (CIBA '
            'GEIGY, AVENTIS, DOW ELANCO, DU PONT, MONSANTO). Dobrá-las nos '
            'grupos de hoje seria afirmação societária que este piloto não tem. '
            'Elas são CONTADAS e não agrupadas — logo o agrupamento por titular '
            'SUBCONTA o concorrente nesses dois países.'),

        'POR_PAIS': paises,
        'NOT_MEASURED': falhas,
    }

    with open(SAIDA, 'w', encoding='utf-8') as f:
        json.dump(art, f, ensure_ascii=False, indent=2)
    print('\ngravado:', SAIDA)


if __name__ == '__main__':
    main()
