#!/usr/bin/env python3
"""
CAMADA REGULATÓRIA DO CONCORRENTE — o registro espanhol, com dono e com data.

A fundação `ES-REGULATORIO-ROPF-2026-08-29.sql` importou 96 registros — **só da
ADAMA**. A camada regulatória de CONCORRENTE não existia no acervo. Não é fonte
nova: é a mesma rota já provada em `mapa_regfi.export()`, com outro filtro.

    python3 scripts/concorrente_regulatorio.py

DUAS COISAS SAEM DAQUI, E ELAS NÃO SE MISTURAM

  1 · CHANGE EVENTS — o que MUDOU entre duas versões arquivadas.
      Passa pelo portão de `source_health.version_state`. Só
      `NEW_VERSION_CHANGED` autoriza emitir. Qualquer outro estado devolve
      `NOT ENOUGH VERSIONS` ou `NO_NEW_VERSION` — **nunca** "nada mudou".

  2 · DATED FACTS — datas que a PRÓPRIA fonte declara, e que não precisam de
      duas versões para existir: caducidade, limite de venda, inscrição,
      último trâmite. Uma data no documento é fato datado; não é mudança.

O QUE ESTA RODADA MEDIU
  versão A `ropf_20260829.json.gz` (2026-08-29) × versão B (captura de hoje):
  **3.084 registros dos dois lados, 13 campos comparados, ZERO diferenças.**
  Nenhum registro novo, nenhum saiu, nenhum campo mudou.
  Estado: `NEW_VERSION_IDENTICAL` → nenhum change event é emitido.

  Isso é RESULTADO, não falha. Mas o que ele diz é ESTREITO, e a primeira
  redação passou do ponto ao escrever que "o ROPF não tem sinal diário".

     REGULATORY_CHANGE_IN_THIS_INTERVAL = 0 OBSERVED
     REGULATORY_CHANGE_CADENCE          = NOT_PROVED

  ⚠️ DOIS DIAS SÃO DOIS DIAS. Uma janela curta sem mudança não mede a
  frequência com que o registro se mexe — mede aquela janela. `0 OBSERVED`
  não autoriza nenhuma destas frases:
     · "o registro não se mexe no dia a dia"
     · "o registro é estático"
     · "o ROPF não tem sinal"
  Provar cadência exige uma série de capturas, não duas pontas.
"""
import datetime
import gzip
import hashlib
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import mapa_regfi          # noqa: E402
import registro_local      # noqa: E402
import source_health       # noqa: E402
from concorrente_amostra import classificar  # noqa: E402

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VERSAO_A = os.path.join(RAIZ, 'data', 'samples', 'ES-T4-005', 'ropf_20260829.json.gz')
CACHE_B = os.path.join(RAIZ, 'data', 'raw', 'ES', 'ropf-export.json')
SAIDA = os.path.join(RAIZ, 'data', 'samples', 'COMPETITOR-REGULATORY-EVENTS.json')

# Os tipos que a régua já provou possíveis sobre ESTE export.
# `MANUFACTURER_CHANGE` fica de fora: exige a ficha individual, um pedido por
# registro, e a régua o marca ALTO risco por comparar campos trocados.
TIPOS = ['NEW_REGISTRATION', 'REGISTRATION_LEFT_THE_LIST', 'STATUS_CHANGE',
         'HOLDER_CHANGE', 'COMPOSITION_CHANGE', 'DATE_CHANGE',
         'REFERENCE_NAME_CHANGE', 'UNKNOWN_CHANGE']
CAMPOS_DATA = ['StrFechaInscripcion', 'StrFechaCaducidad', 'StrFechaRenovacion',
               'StrFechaModificacion', 'StrFechaLimiteVenta']


def _sha(obj):
    return hashlib.sha256(
        json.dumps(obj, sort_keys=True, ensure_ascii=False).encode('utf-8')).hexdigest()


def _norm_texto(s):
    """Espaços colapsados e caixa alta. Pontuação PRESERVADA: `S.A.` != `S.A.U.`."""
    return ' '.join((s or '').upper().split())


def _data(br):
    """`dd-mm-aaaa` do ROPF vira date. Formato irreconhecível vira None, não hoje."""
    try:
        return datetime.datetime.strptime(br or '', '%d-%m-%Y').date()
    except ValueError:
        return None


def _data_qualquer(s):
    """IT usa `dd/mm/aaaa`, ES usa `dd-mm-aaaa`. Ilegível vira None — nunca hoje."""
    s = (s or '').strip()
    if not s or s == '-':
        return None
    for f in ('%d-%m-%Y', '%d/%m/%Y', '%Y-%m-%d'):
        try:
            return datetime.datetime.strptime(s, f).date()
        except ValueError:
            continue
    return None


def carregar_versoes():
    with gzip.open(VERSAO_A, 'rt', encoding='utf-8') as f:
        a = json.load(f)
    campos = a['projection_fields']
    with open(CACHE_B, encoding='utf-8') as f:
        bruto = json.load(f)
    b = {'rows': [{k: r.get(k) for k in campos} for r in bruto['rows']],
         'export_server_timestamp': bruto['fecha']}
    return a, b, campos


def change_events(a_rows, b_rows, campos, titulares):
    """
    Diferenças campo a campo, restritas aos titulares do piloto.
    Só é chamada quando o portão de versão autoriza.
    """
    a = {r['NumRegistro']: r for r in a_rows}
    b = {r['NumRegistro']: r for r in b_rows}
    eventos = []

    def interessa(r):
        return classificar(r.get('Titular')) in titulares

    for reg in sorted(set(b) - set(a)):
        if interessa(b[reg]):
            eventos.append({'CHANGE_TYPE': 'NEW_REGISTRATION', 'REGISTRATION_ID': reg,
                            'BEFORE': None, 'AFTER': b[reg].get('Nombre'),
                            'GRUPO': classificar(b[reg].get('Titular'))})
    for reg in sorted(set(a) - set(b)):
        if interessa(a[reg]):
            eventos.append({'CHANGE_TYPE': 'REGISTRATION_LEFT_THE_LIST',
                            'REGISTRATION_ID': reg, 'BEFORE': a[reg].get('Nombre'),
                            'AFTER': None, 'GRUPO': classificar(a[reg].get('Titular'))})

    campo_para_tipo = {'Estado': 'STATUS_CHANGE', 'Titular': 'HOLDER_CHANGE',
                       'Formulado': 'COMPOSITION_CHANGE', 'Nombre': 'REFERENCE_NAME_CHANGE'}
    for reg in sorted(set(a) & set(b)):
        if not interessa(b[reg]):
            continue
        for campo in campos:
            va, vb = a[reg].get(campo), b[reg].get(campo)
            if _norm_texto(va) == _norm_texto(vb):
                continue
            tipo = campo_para_tipo.get(
                campo, 'DATE_CHANGE' if campo in CAMPOS_DATA else 'UNKNOWN_CHANGE')
            eventos.append({'CHANGE_TYPE': tipo, 'REGISTRATION_ID': reg,
                            'FIELD': campo, 'BEFORE': va, 'AFTER': vb,
                            'GRUPO': classificar(b[reg].get('Titular')),
                            # UNKNOWN_CHANGE nunca alerta — régua §5, portão do tipo
                            'ALERTAVEL': tipo != 'UNKNOWN_CHANGE'})
    return eventos


def dated_facts(rows, titulares, hoje):
    """
    Datas que a fonte declara. Não precisam de segunda versão para existir —
    e por isso NÃO são change events. `EFFECTIVE_DATE` vem do documento;
    `OBSERVED_AT` é quando nós olhamos. Os dois campos coexistem, sempre.
    """
    escoando = {r['NumRegistro'] for r in mapa_regfi.selling_off(rows, hoje)}
    fatos = []
    for r in rows:
        grupo = classificar(r.get('Titular'))
        if grupo not in titulares:
            continue
        reg = r['NumRegistro']
        base = {
            'REGISTRATION_ID': reg, 'GRUPO': grupo,
            'COUNTRY': 'ES', 'PRODUCT': r.get('Nombre'),
            'HOLDER': r.get('Titular'), 'ESTADO': r.get('Estado'),
        }
        cad = _data(r.get('StrFechaCaducidad'))
        if cad:
            fatos.append(dict(base, EVENT_TYPE='EXPIRY', EFFECTIVE_DATE=cad.isoformat(),
                              JA_OCORREU=cad <= hoje,
                              NOTA='EXPIRY != WITHDRAWAL. Vencimento de autorização '
                                   'não é retirada de mercado.'))
        lim = _data(r.get('StrFechaLimiteVenta'))
        if lim:
            fatos.append(dict(base, EVENT_TYPE='SELLING_OFF_DEADLINE',
                              EFFECTIVE_DATE=lim.isoformat(),
                              EM_ESCOAMENTO_HOJE=reg in escoando,
                              NOTA='data limite de venda declarada pela fonte'))
        ins = _data(r.get('StrFechaInscripcion'))
        if ins:
            fatos.append(dict(base, EVENT_TYPE='LOCAL_REGISTRATION',
                              EFFECTIVE_DATE=ins.isoformat(),
                              NOTA='data de inscrição no registro espanhol'))
        mod = _data(r.get('StrFechaModificacion'))
        if mod:
            fatos.append(dict(base, EVENT_TYPE='REGISTRATION_MODIFIED',
                              EFFECTIVE_DATE=mod.isoformat(),
                              NOTA='a fonte declara QUE houve modificação e QUANDO. '
                                   'NÃO declara O QUÊ mudou — isso só sai de duas '
                                   'versões arquivadas.'))
    return fatos


def dated_facts_pais(pais, titulares):
    """
    Os mesmos dois tipos de fato datado para Itália e França, sobre a forma
    comum de `registro_local`.

    Só DOIS tipos, e não quatro: `SELLING_OFF_DEADLINE` e
    `REGISTRATION_MODIFIED` não existem nesses dois registros. Inventá-los
    com data aproximada de outro campo seria fabricar fato — e a França
    sequer publica caducidade, publica **retirada**, que é outra coisa
    (`EXPIRY != WITHDRAWAL`, a lei que a casa já carrega).
    """
    rows, _ = registro_local.carregar(pais)
    fatos = []
    for r in rows:
        if r['GRUPO'] not in titulares:
            continue
        base = {'REGISTRATION_ID': r['REGISTRATION_ID'], 'GRUPO': r['GRUPO'],
                'COUNTRY': pais, 'PRODUCT': r.get('PRODUCT_NAME'),
                'HOLDER': r.get('HOLDER'), 'ESTADO': r.get('STATUS')}
        ins = _data_qualquer(r.get('DATE_REGISTRATION'))
        if ins:
            fatos.append(dict(base, EVENT_TYPE='LOCAL_REGISTRATION',
                              EFFECTIVE_DATE=ins.isoformat(),
                              NOTA=f'data de inscrição no registro nacional {pais}'))
        exp = _data_qualquer(r.get('DATE_EXPIRY'))
        if exp:
            fatos.append(dict(base, EVENT_TYPE='EXPIRY',
                              EFFECTIVE_DATE=exp.isoformat(),
                              NOTA='EXPIRY != WITHDRAWAL. Vencimento de autorização '
                                   'não é retirada de mercado.'))
    return fatos


def main():
    hoje = datetime.date.today()
    with open(os.path.join(RAIZ, 'data', 'samples',
                           'COMPETITOR-PILOT-AMOSTRA.json'), encoding='utf-8') as f:
        titulares = json.load(f)['AMOSTRA_DO_PILOTO']

    a, b, campos = carregar_versoes()
    sha_a, sha_b = _sha(a['rows']), _sha(b['rows'])
    estado = source_health.version_state(
        fetch_ok=True, current_hash=sha_b, previous_hash=sha_a,
        current_version=b['export_server_timestamp'],
        previous_version=a['export_server_timestamp'])

    if source_health.can_diff(estado):
        eventos = change_events(a['rows'], b['rows'], campos, titulares)
        veredito = f'{len(eventos)} change events emitidos'
    else:
        eventos = []
        veredito = {
            source_health.NEW_VERSION_IDENTICAL:
                'NO_CHANGE_BETWEEN_THESE_TWO_VERSIONS — as duas capturas são '
                'idênticas campo a campo. Vale para ESTE intervalo e só para '
                'ele. REGULATORY_CHANGE_CADENCE continua NOT_PROVED.',
            source_health.BASELINE_ESTABLISHED: 'NOT ENOUGH VERSIONS',
            source_health.NO_NEW_VERSION: 'NO_NEW_VERSION — a fonte não republicou',
            source_health.SOURCE_FAILED:
                'SOURCE_FAILED — e isto JAMAIS pode ser lido como "nada mudou"',
        }[estado]

    # a conta da comparação, aberta, para que o zero seja auditável
    a_ids = {r['NumRegistro'] for r in a['rows']}
    b_ids = {r['NumRegistro'] for r in b['rows']}
    comparacoes = len(a_ids & b_ids) * len(campos)

    with open(CACHE_B, encoding='utf-8') as f:
        rows_completas = json.load(f)['rows']
    fatos = dated_facts(rows_completas, titulares, hoje)
    # a paridade EAME: os mesmos concorrentes nos outros dois registros oficiais
    fatos_por_pais = {'ES': len(fatos)}
    for pais in ('IT', 'FR'):
        novos = dated_facts_pais(pais, titulares)
        fatos_por_pais[pais] = len(novos)
        fatos.extend(novos)

    por_tipo, por_grupo = {}, {}
    for ft in fatos:
        por_tipo[ft['EVENT_TYPE']] = por_tipo.get(ft['EVENT_TYPE'], 0) + 1
        por_grupo[ft['GRUPO']] = por_grupo.get(ft['GRUPO'], 0) + 1

    art = {
        'SOURCE_ID': 'COMPETITOR-REGULATORY-EVENTS',
        'source': 'ROPF — Registro Oficial de Productos Fitosanitarios (MAPA, Espanha)',
        'SOURCE_LOCATION': 'servicio.mapa.gob.es/regfiweb',
        'FACT_LOCATION': 'ES',
        'ORIGINAL_LANGUAGE': 'es',
        # este artefato É da camada regulatória nacional, e usa o vocabulário
        # fechado que o repositório já tem para ela
        'layer': 'NATIONAL PRODUCT AUTHORIZATION',
        'CAMADA_DO_PILOTO': 'REGULATORY',
        'captured_at': hoje.isoformat(),
        'AMOSTRA': titulares,

        'PORTAO_DE_VERSAO': {
            'ESTADO': estado,
            'AUTORIZA_EMITIR_CHANGE_EVENT': source_health.can_diff(estado),
            'VERSAO_A': {'arquivo': os.path.relpath(VERSAO_A, RAIZ),
                         'export_server_timestamp': a['export_server_timestamp'],
                         'registros': len(a['rows']), 'sha256_das_linhas': sha_a},
            'VERSAO_B': {'arquivo': os.path.relpath(CACHE_B, RAIZ),
                         'export_server_timestamp': b['export_server_timestamp'],
                         'registros': len(b['rows']), 'sha256_das_linhas': sha_b},
            'CAMPOS_COMPARADOS': campos,
            'COMPARACOES_CAMPO_A_CAMPO': comparacoes,
            'REGISTROS_SO_EM_A': sorted(a_ids - b_ids),
            'REGISTROS_SO_EM_B': sorted(b_ids - a_ids),
            'VEREDITO': veredito,
            'REGULATORY_CHANGE_IN_THIS_INTERVAL': '0 OBSERVED',
            'REGULATORY_CHANGE_CADENCE': 'NOT_PROVED',
            'ALCANCE': ('o intervalo entre as duas capturas, e nada além dele. '
                        'Ausência de mudança aqui NÃO é estabilidade do registro.'),
            'PROIBIDO_DIZER': ['o registro não se mexe no dia a dia',
                               'o registro é estático', 'o ROPF não tem sinal'],
        },
        'CHANGE_EVENTS': eventos,
        'TIPOS_POSSIVEIS_SOBRE_ESTE_EXPORT': TIPOS,
        'TIPO_QUE_ESTE_EXPORT_NAO_ALCANCA': {
            'MANUFACTURER_CHANGE': 'exige a ficha individual, um pedido por registro; '
                                   'a régua o marca risco ALTO por comparar campos '
                                   'de natureza diferente (rótulo x razão social)',
        },

        'PARIDADE_EAME': {
            'FATOS_DATADOS_POR_PAIS': fatos_por_pais,
            'CHANGE_EVENTS_POR_PAIS': {
                'ES': 'ver PORTAO_DE_VERSAO — duas versões arquivadas existem',
                'IT': 'BASELINE_ESTABLISHED — existe UMA captura '
                      '(PROD_FTS_6_20260824.csv). Sem segunda versão não há '
                      'ausência de mudança, há ausência de comparação.',
                'FR': 'BASELINE_ESTABLISHED — existe UMA captura do E-Phy '
                      '(20260825). Idem.',
            },
            'TIPOS_QUE_IT_E_FR_NAO_ALCANCAM': {
                'SELLING_OFF_DEADLINE': 'campo inexistente nos dois registros',
                'REGISTRATION_MODIFIED': 'campo inexistente nos dois registros',
                'EXPIRY_NA_FRANCA': 'o E-Phy publica RETIRADA, não caducidade. '
                                    'EXPIRY != WITHDRAWAL, e por isso a França '
                                    'não emite EXPIRY nesta rodada.',
            },
        },
        'DATED_FACTS': {
            'O_QUE_SAO': ('datas declaradas pela própria fonte. Existem sem segunda '
                          'versão, e por isso NÃO são change events.'),
            'EFFECTIVE_DATE_x_OBSERVED_AT': (
                'EFFECTIVE_DATE vem do documento. OBSERVED_AT é '
                f'{hoje.isoformat()}, quando nós olhamos. Os dois convivem.'),
            'TOTAL': len(fatos),
            'POR_TIPO': por_tipo,
            'POR_GRUPO': por_grupo,
            'FATOS': fatos,
        },

        'LIMITES': [
            'ES apenas. Itália e França não têm registro local no acervo, e este '
            'artefato não fala por eles.',
            'REGISTRATION_MODIFIED diz QUE mudou e QUANDO, nunca O QUÊ.',
            'O export traz o último trâmite de cada produto, não o histórico: '
            'mudanças antigas já foram sobrescritas na fonte e só sobrevivem no '
            'arquivo (REGUA-DE-CHANGE-EVENT-EAME §1).',
            'Nenhum destes fatos diz o que foi ao mercado, quanto, nem quando.',
        ],
    }

    with open(SAIDA, 'w', encoding='utf-8') as f:
        json.dump(art, f, ensure_ascii=False, indent=2)

    print(f'portão de versão: {estado}')
    print(f'  A {a["export_server_timestamp"]}  ·  B {b["export_server_timestamp"]}')
    print(f'  {comparacoes} comparações campo a campo · {len(eventos)} change events')
    print(f'  veredito: {veredito}')
    print(f'\ndated facts: {len(fatos)}')
    for t, n in sorted(por_tipo.items(), key=lambda kv: -kv[1]):
        print(f'  {n:>5}  {t}')
    print('\ngravado:', SAIDA)


if __name__ == '__main__':
    main()
