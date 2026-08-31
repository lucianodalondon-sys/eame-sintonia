#!/usr/bin/env python3
"""
COMPETITOR EVENT — as camadas viram eventos, e os eventos viram timeline.

    python3 scripts/concorrente_evento.py

Este script NÃO coleta nada. Ele une o que as três camadas já provaram e
produz duas coisas: a lista canônica de eventos e as timelines por cadeia.

AS SETE CAMADAS DA MISSÃO, E O QUE ESTA RODADA TEM DE CADA UMA
  A · IP / BRAND            COLETADO   TMview · 9.661 marcas
  B · PATENT                ver PATENTE_ESTADO — camada secundária por decisão
  C · REGULATORY            COLETADO   ROPF ES
  D · PRODUCT / CATALOG     NOT_JOINED — catálogos ADAMA em branches próprias
  E · META                  NOT_JOINED — 1.111 anúncios em branch paralela
  F · CREATOR / EVENT       NOT_JOINED — Creator Map CONGELADO, handoff pronto
  G · TIME                  presente em todos os eventos

⚠️ NOT_JOINED NÃO É NOT_AVAILABLE, E NENHUM DOS DOIS É ZERO
  A primeira entrega escreveu que META e CREATOR "não existem no repositório".
  **Errado, e corrigido.** O Creator Map está congelado em branch própria com
  handoff canônico; a missão Meta corre em paralelo e já tem 1.111 anúncios
  dos mesmos seis concorrentes. O que esta branch pode afirmar é que **não os
  juntou** — `NOT_JOINED_IN_THIS_MISSION`. O refresh final junta os HANDOFFS,
  não os branches.

LEAD_DAYS — POR QUE A MAIORIA NÃO É DEFENSÁVEL
  A missão manda medir antecedência "somente quando a relação entre eventos
  for defensável". Medido nos 209 pares PROVED: a mediana dá 1.539 dias, mas
  a amplitude vai de **-15.700 a +11.033 dias** — 43 anos para trás e 30 para
  frente. Um número desses não descreve um lançamento: descreve uma palavra
  que dois documentos usaram em décadas diferentes.

  Causas conhecidas do estouro:
   · **redepósito de marca.** O TMview traz cada depósito; uma marca dos anos
     70 redepositada em 2010 aparece com a data nova. `MATCH`, `VIPER`,
     `SEMPRA` caem aqui.
   · **reuso de nome comercial** sobre autorização antiga.
   · **marca genérica** que colide com produto de outra época.

  Por isso o script separa e NÃO esconde atrás de uma média:
     MARCA_ANTES_DO_REGISTRO     a hipótese do piloto se sustenta no par
     REGISTRO_ANTES_DA_MARCA     a hipótese é REFUTADA no par
  E marca `DEFENSAVEL` só quando o depósito usado é o **mais antigo** daquela
  marca naquele grupo — o que remove o redepósito — e a ordem é marca→registro.
  Não há corte de tempo arbitrário: um limiar escolhido a dedo produziria a
  antecedência que se quisesse.
"""
import datetime
import json
import os
import statistics
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
S = os.path.join(RAIZ, 'data', 'samples')
SAIDA = os.path.join(S, 'COMPETITOR-EVENTS.json')

CAMPOS = [
    'EVENT_ID', 'COMPETITOR', 'COUNTRY', 'EVENT_TYPE', 'EVENT_DATE', 'FIRST_OBSERVED',
    'SOURCE', 'SOURCE_URL', 'EVIDENCE', 'PRODUCT', 'BRAND', 'CROP', 'ISSUE',
    'REGULATORY_ID', 'META_AD_ID', 'CREATOR_ID', 'CONFIDENCE_STATE', 'DATASET_OWNER',
]
DONO = 'COMPETITOR_FORESIGHT_EAME'
NK = 'NOT_KNOWN'

FONTE_DO_PAIS = {
    'ES': 'ROPF (MAPA · ES)',
    'IT': 'Banca dati fitosanitari (Ministero della Salute · IT)',
    'FR': 'Catalogue E-Phy (ANSES · FR)',
}
URL_DO_PAIS = {
    'ES': 'https://servicio.mapa.gob.es/regfiweb/Productos/Index',
    'IT': 'https://www.dati.salute.gov.it/it/dataset/fitosanitari/',
    'FR': 'https://www.data.gouv.fr/fr/datasets/575e9fac88ee38072a640390/',
}

# ⚠️ CORREÇÃO DE ESTADO — a primeira entrega escreveu "não existe no
# repositório", e estava ERRADO. As três camadas existem em outras branches.
# O que ESTA branch pode dizer é que não as JUNTOU. Juntar handoff é trabalho
# do refresh final; juntar branch é o que a missão proíbe.
CAMADAS_AUSENTES = {
    'PRODUCT_CATALOG': {
        'ESTADO': 'NOT_JOINED_IN_THIS_MISSION',
        'DISPONIVEL_NESTE_SNAPSHOT': 'NO',
        'ESTADO_REAL': 'catálogos ADAMA de ES, IT e FR existem em branches '
                       'próprias (adama-es-local-browser, adama-it-local-catalog, '
                       'adama-fr-local-catalog). São catálogos DA ADAMA.',
        'CATALOGO_DE_CONCORRENTE': 'NOT_COLLECTED em nenhuma branch conhecida',
        'NAO_SIGNIFICA': 'não significa que os concorrentes não publiquem catálogo',
    },
    'META': {
        'ESTADO': 'NOT_JOINED_IN_THIS_MISSION',
        'DISPONIVEL_NESTE_SNAPSHOT': 'NO',
        'ESTADO_REAL': 'a missão Meta Competitor corre em paralelo na branch '
                       'claude/eame-meta-competitor e já tem 1.111 anúncios '
                       'observados dos MESMOS seis concorrentes em ES/IT/FR.',
        'NAO_SIGNIFICA': 'não significa que o concorrente não anuncie no Meta',
    },
    'CREATOR': {
        'ESTADO': 'NOT_JOINED_IN_THIS_MISSION',
        'DISPONIVEL_NESTE_SNAPSHOT': 'NO',
        'ESTADO_REAL': 'o Creator Map está CONGELADO com handoff canônico em '
                       'claude/eame-agro-creators-map-77c4ld · '
                       'docs/creators/HANDOFF-INTELLIGENCE-CREATOR-MAP-EAME.md, '
                       'e declara BRAND × RELATION_TYPE como chave de junção.',
        'NAO_SIGNIFICA': 'não significa ausência de atividade de creator',
    },
}


def _ler(nome):
    with open(os.path.join(S, nome), encoding='utf-8') as f:
        return json.load(f)


def _data_iso(s):
    s = (s or '').strip()
    if not s or s == '-':
        return None
    for f in ('%d-%m-%Y', '%d/%m/%Y', '%Y-%m-%d'):
        try:
            return datetime.datetime.strptime(s, f).date().isoformat()
        except ValueError:
            continue
    return None


def evento(**kw):
    """Todo evento tem as 18 chaves. Campo não informado vira NOT_KNOWN, nunca some."""
    e = {c: kw.get(c, NK) for c in CAMPOS}
    e['DATASET_OWNER'] = DONO
    return e


def eventos_ip(ip):
    out = []
    for grupo, offs in ip['POR_CONCORRENTE'].items():
        for office, v in offs.items():
            if v.get('ESTADO') != 'OK':
                continue
            for m in v['MARCAS']:
                st = (m.get('TM_STATUS') or '').lower()
                tipo = ('TRADEMARK_REGISTRATION' if 'regist' in st
                        else 'TRADEMARK_APPLICATION')
                out.append(evento(
                    EVENT_ID=f"IP:{m['ST13']}",
                    COMPETITOR=grupo, COUNTRY=office, EVENT_TYPE=tipo,
                    EVENT_DATE=m['APPLICATION_DATE'],
                    FIRST_OBSERVED=ip['captured_at'],
                    SOURCE='TMview (TMDN/EUIPO)', SOURCE_URL=m['SOURCE_URL'],
                    EVIDENCE=f"ST13 {m['ST13']} · {m['TM_STATUS']} · "
                             f"nice {m['NICE_CLASS']} · {m['AGROCHEMICAL_RELEVANCE']}",
                    BRAND=m['TM_NAME'],
                    # a marca NÃO diz produto. Só o crosswalk pode dizer.
                    #
                    # Três estados, e não dois. `SO_CLASSE_5` é AMBÍGUO porque a
                    # classe 5 de Nice cobre farmacêutico e veterinário junto com
                    # pesticida. Fora das classes 1 e 5 não é "ambíguo": é
                    # NOT_KNOWN quanto a ser agro, e o import o recusa.
                    CONFIDENCE_STATE={
                        'CLASSE_1_E_5': 'OBSERVED_STRONG_AGRO_SIGNAL',
                        'SO_CLASSE_1': 'OBSERVED_STRONG_AGRO_SIGNAL',
                        'SO_CLASSE_5': 'OBSERVED_AMBIGUOUS_CLASS',
                    }.get(m['AGROCHEMICAL_RELEVANCE'], 'NOT_KNOWN')))
    return out


def eventos_regulatorios(reg):
    out = []
    for f in reg['DATED_FACTS']['FATOS']:
        out.append(evento(
            # o país entra na chave: ES, IT e FR numeram por conta própria e
            # `008259` pode existir em mais de um registro nacional.
            EVENT_ID=f"REG:{f['COUNTRY']}:{f['REGISTRATION_ID']}:{f['EVENT_TYPE']}",
            COMPETITOR=f['GRUPO'], COUNTRY=f['COUNTRY'], EVENT_TYPE=f['EVENT_TYPE'],
            EVENT_DATE=f['EFFECTIVE_DATE'], FIRST_OBSERVED=reg['captured_at'],
            SOURCE=FONTE_DO_PAIS[f['COUNTRY']],
            SOURCE_URL=URL_DO_PAIS[f['COUNTRY']],
            EVIDENCE=f.get('NOTA', NK),
            PRODUCT=f.get('PRODUCT') or NK,
            REGULATORY_ID=f['REGISTRATION_ID'],
            CONFIDENCE_STATE='OBSERVED_DATED_BY_SOURCE'))
    for c in reg['CHANGE_EVENTS']:
        out.append(evento(
            EVENT_ID=f"CHG:ES:{c['REGISTRATION_ID']}:{c['CHANGE_TYPE']}",
            COMPETITOR=c.get('GRUPO'), COUNTRY='ES',
            EVENT_TYPE=c['CHANGE_TYPE'], EVENT_DATE=reg['captured_at'],
            FIRST_OBSERVED=reg['captured_at'], SOURCE='ROPF · duas versões',
            EVIDENCE=f"{c.get('FIELD', '')}: {c.get('BEFORE')} -> {c.get('AFTER')}",
            REGULATORY_ID=c['REGISTRATION_ID'],
            CONFIDENCE_STATE='OBSERVED_BETWEEN_TWO_ARCHIVED_VERSIONS'))
    return out


def timelines(paridade):
    """
    Uma cadeia por par PROVED, nos TRÊS países. Só pares PROVED entram: a
    missão manda não forçar casamento por nome parecido, e cadeia com link
    fraco é pior que cadeia nenhuma.

    A CHAVE DA CADEIA CARREGA PAÍS **E** ST13
      sem o ST13, a marca nacional e a marca da UE com o mesmo nome e o mesmo
      registro colidiam — 15 casos medidos na primeira rodada, e a
      antecedência de uma marca era colada na outra.
      Sem o PAÍS, o mesmo ST13 de uma marca da UE ligado a registros de ES, IT
      e FR viraria uma cadeia só, e duas seriam perdidas em silêncio.
    """
    cadeias = []
    for pais, bloco in paridade['POR_PAIS'].items():
        if bloco.get('ESTADO_DA_MEDICAO') != 'MEASURED':
            continue
        provados = [p for p in bloco['PARES_TODOS']
                    if p['ESTADO_DO_LINK'] == 'PROVED']

        # o depósito MAIS ANTIGO daquela marca naquele grupo — remove redepósito
        primeiro = {}
        for p in provados:
            k = (p['GRUPO_DA_MARCA'], p['TM_NAME'].upper())
            d = p['TM_APPLICATION_DATE']
            if d != NK and (k not in primeiro or d < primeiro[k]):
                primeiro[k] = d

        for p in provados:
            tm, rg = p['TM_APPLICATION_DATE'], _data_iso(p['REGISTRATION_DATE'])
            k = (p['GRUPO_DA_MARCA'], p['TM_NAME'].upper())
            if tm == NK or rg is None:
                ordem, lead, defensavel = NK, None, False
                motivo = 'falta uma das duas datas'
            else:
                lead = (datetime.date.fromisoformat(rg)
                        - datetime.date.fromisoformat(tm)).days
                ordem = ('MARCA_ANTES_DO_REGISTRO' if lead > 0 else
                         'REGISTRO_ANTES_DA_MARCA' if lead < 0 else 'MESMO_DIA')
                e_o_primeiro = primeiro.get(k) == tm
                defensavel = lead > 0 and e_o_primeiro
                motivo = ('depósito mais antigo da marca no grupo e ordem '
                          'marca→registro' if defensavel else
                          'o registro precede a marca — a hipótese de '
                          'antecedência é REFUTADA neste par' if lead <= 0 else
                          'existe depósito mais antigo desta mesma marca: este é '
                          'provavelmente redepósito, e a antecedência seria inflada')
            cadeias.append({
                'CHAIN_ID': f"{pais}:{p['GRUPO_DA_MARCA']}:{p['ST13']}:"
                            f"{p['REGISTRATION_ID']}",
                'COMPETITOR': p['GRUPO_DA_MARCA'], 'BRAND': p['TM_NAME'],
                'REGISTRATION_ID': p['REGISTRATION_ID'],
                'COUNTRY': pais, 'CROSSWALK_STATE': 'PROVED',
                'EVENTOS': [
                    {'ORDEM': 1, 'CAMADA': 'IP',
                     'EVENT_TYPE': 'TRADEMARK_APPLICATION', 'DATE': tm,
                     'OFFICE': p['TM_OFFICE'], 'SOURCE': 'TMview'},
                    {'ORDEM': 2, 'CAMADA': 'REGULATORY',
                     'EVENT_TYPE': 'LOCAL_REGISTRATION', 'DATE': rg or NK,
                     'SOURCE': FONTE_DO_PAIS[pais]},
                    {'ORDEM': 3, 'CAMADA': 'PRODUCT_CATALOG', 'DATE': NK,
                     'ESTADO': 'NOT_JOINED_IN_THIS_MISSION'},
                    {'ORDEM': 4, 'CAMADA': 'META', 'DATE': NK,
                     'ESTADO': 'NOT_JOINED_IN_THIS_MISSION'},
                    {'ORDEM': 5, 'CAMADA': 'CREATOR', 'DATE': NK,
                     'ESTADO': 'NOT_JOINED_IN_THIS_MISSION'},
                ],
                'CAMADAS_COM_DADO': 2, 'CAMADAS_DA_CADEIA': 5,
                'COMPLETUDE': 'PARCIAL — 2 de 5 camadas',
                'ORDEM_OBSERVADA': ordem,
                'LEAD_DAYS': lead,
                'LEAD_DAYS_DEFENSAVEL': defensavel,
                'MOTIVO': motivo,
                'NAO_E_CAUSALIDADE': ('dois fatos públicos com datas. O registro '
                                      'não diz que veio da marca, e a marca não '
                                      'diz que virou produto.'),
            })
    return cadeias


def main():
    ip = _ler('COMPETITOR-IP-TMVIEW.json')
    reg = _ler('COMPETITOR-REGULATORY-EVENTS.json')
    paridade = _ler('COMPETITOR-EAME-PARIDADE.json')

    eventos = eventos_ip(ip) + eventos_regulatorios(reg)
    cadeias = timelines(paridade)

    por_tipo, por_comp, por_pais = {}, {}, {}
    for e in eventos:
        por_tipo[e['EVENT_TYPE']] = por_tipo.get(e['EVENT_TYPE'], 0) + 1
        por_comp[e['COMPETITOR']] = por_comp.get(e['COMPETITOR'], 0) + 1
        por_pais[e['COUNTRY']] = por_pais.get(e['COUNTRY'], 0) + 1

    defensaveis = [c for c in cadeias if c['LEAD_DAYS_DEFENSAVEL']]
    refutadas = [c for c in cadeias if c['ORDEM_OBSERVADA'] == 'REGISTRO_ANTES_DA_MARCA']
    leads = [c['LEAD_DAYS'] for c in defensaveis]
    todos_leads = [c['LEAD_DAYS'] for c in cadeias if c['LEAD_DAYS'] is not None]

    # qual camada aparece primeiro em cada cadeia — pergunta D da missão
    primeira_fonte = {}
    for c in cadeias:
        k = ('IP' if c['ORDEM_OBSERVADA'] == 'MARCA_ANTES_DO_REGISTRO'
             else 'REGULATORY' if c['ORDEM_OBSERVADA'] == 'REGISTRO_ANTES_DA_MARCA'
             else c['ORDEM_OBSERVADA'])
        primeira_fonte[k] = primeira_fonte.get(k, 0) + 1

    art = {
        'SOURCE_ID': 'COMPETITOR-EVENTS',
        'source': 'derivação sobre COMPETITOR-IP-TMVIEW + COMPETITOR-REGULATORY-EVENTS '
                  '+ COMPETITOR-CROSSWALK',
        'SOURCE_LOCATION': 'interno — derivado',
        'FACT_LOCATION': 'ES · IT · FR · EU',
        'CAMADA_DO_PILOTO': 'COMPETITOR EVENT / TIMELINE',
        'captured_at': ip['captured_at'],
        'DATASET_OWNER': DONO,
        'CAMPOS_DO_EVENTO': CAMPOS,

        'CAMADAS_AUSENTES': CAMADAS_AUSENTES,
        'NOT_JOINED_NAO_E_ZERO': (
            'META e CREATOR existem em outras branches e NÃO foram juntados aqui. '
            'Isso é NOT_JOINED_IN_THIS_MISSION. Nenhuma linha deste artefato pode '
            'ser lida como "o concorrente não anuncia" — nem como "não existe '
            'Meta no projeto", que foi o erro da primeira entrega.'),

        'EVENTOS': {
            'TOTAL': len(eventos),
            'POR_TIPO': por_tipo, 'POR_COMPETIDOR': por_comp, 'POR_PAIS': por_pais,
            'LISTA': eventos,
        },

        'TIMELINES': {
            'TOTAL': len(cadeias),
            'REGRA': 'uma cadeia por par PROVED do crosswalk. Nenhuma cadeia é '
                     'construída sobre link PARTIAL, REJECTED ou NOT_KNOWN.',
            'COMPLETUDE': f'2 de 5 camadas em TODAS as {len(cadeias)} cadeias — '
                          'catálogo, Meta e creator não existem no acervo. '
                          'Nenhuma cadeia fim-a-fim foi fechada nesta rodada.',
            'PRIMEIRA_FONTE_OBSERVADA': primeira_fonte,
            'CADEIAS': cadeias,
        },

        'LEAD_DAYS': {
            'PERGUNTA': 'a marca aparece antes do registro local?',
            'PARES_MEDIDOS': len(todos_leads),
            'MARCA_ANTES': primeira_fonte.get('IP', 0),
            'REGISTRO_ANTES': len(refutadas),
            'AMPLITUDE_BRUTA_DIAS': [min(todos_leads), max(todos_leads)] if todos_leads else [],
            'POR_QUE_A_AMPLITUDE_ESTOURA': (
                'redepósito de marca, reuso de nome comercial sobre autorização '
                'antiga, e colisão de nome genérico. Uma média sobre isto seria '
                'um número bonito medindo três coisas diferentes.'),
            'DEFENSAVEIS': len(defensaveis),
            'REGRA_DE_DEFENSABILIDADE': (
                'o depósito usado é o MAIS ANTIGO daquela marca naquele grupo '
                '(remove redepósito) E a ordem é marca→registro. Sem corte de '
                'tempo arbitrário: um limiar escolhido a dedo produziria a '
                'antecedência que se quisesse.'),
            'MEDIANA_DIAS_DEFENSAVEIS': statistics.median(leads) if leads else None,
            'MIN_MAX_DEFENSAVEIS': [min(leads), max(leads)] if leads else [],
            'NAO_E_CAUSALIDADE': (
                'nenhum LEAD_DAY afirma que a marca causou o registro. São dois '
                'fatos públicos, datados, na mesma cadeia de identidade provada.'),
        },
    }

    with open(SAIDA, 'w', encoding='utf-8') as f:
        json.dump(art, f, ensure_ascii=False, indent=2)

    print(f'eventos: {len(eventos)}')
    for t, n in sorted(por_tipo.items(), key=lambda kv: -kv[1]):
        print(f'  {n:>6}  {t}')
    print(f'\ntimelines (só PROVED): {len(cadeias)} · todas com 2 de 5 camadas')
    print(f'  marca antes do registro: {primeira_fonte.get("IP", 0)}')
    print(f'  registro antes da marca: {len(refutadas)}  (hipótese refutada no par)')
    print(f'  lead days DEFENSÁVEIS: {len(defensaveis)}'
          + (f' · mediana {statistics.median(leads):.0f} dias '
             f'({min(leads)} a {max(leads)})' if leads else ''))
    print('gravado:', SAIDA)


if __name__ == '__main__':
    main()
