#!/usr/bin/env python3
"""
PROVA PEQUENA — dois nomes, contrato conferido antes, RAW lido depois.

Não é a coleta. É a prova de que a coleta pode começar.

A missão manda: antes de ampliar, 1–2 provas pequenas, olhar o RAW, confirmar o
schema. Este arquivo faz exatamente isso e nada além — dois nomes é o teto, e
está no código, não na intenção.

TRÊS PORTÕES, NESTA ORDEM
--------------------------
1. **CONTRATO** — `apify_contrato` lê o `inputSchema` publicado, de graça. Se o
   campo que eu pretendo mandar não existir no contrato, o gasto **não acontece**:
   sai `CONTRACT_REFUSED_SPEND`. Foi a ausência deste portão que custou 8 runs.
2. **RAW** — o bruto é gravado por `coletor.executar` antes de qualquer leitura.
3. **SCHEMA** — a forma do que voltou é descrita campo a campo, e comparada com o
   que `linkedin_schema` já conhece. Forma nova é `UNKNOWN_SCHEMA`, nunca "vazio".

O QUE ESTE ARQUIVO SE RECUSA A CONCLUIR
----------------------------------------
Não conclui que a camada de sensores humanos existe ou não existe. Dois nomes não
medem oito, e oito não medem a Itália. O veredito que ele pode dar é sobre a
ROTA — `ROUTE_PROVED` ou `ROUTE_NOT_PROVED` —, nunca sobre o campo.

    PROVA DE ROTA ≠ MEDIDA DE SINAL
"""
import datetime
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import apify_contrato as ac      # noqa: E402
import apify_pool as ap          # noqa: E402
import coletor                   # noqa: E402
import linkedin_schema as ls     # noqa: E402

DEST = os.path.join(ROOT, 'data', 'samples', 'IT-CASOS', 'IT-LINKEDIN-PROVA-BUSCA.json')

ACTOR = 'harvestapi~linkedin-profile-search-by-name'
TETO_NOMES = 2                # teto da PROVA. Ampliar exige outra missão.
TETO_ITENS = 5

# Dois dos oito. Escolhidos por serem os de instituição mais verificável: se o
# ator devolver alguém do CREA, a identidade tem âncora; se devolver um perfil
# qualquer, o defeito reaparece e a prova falha alto, que é o que se quer.
NOMES = [
    {'NAME': 'Pasquale De Vita', 'FIRST': 'Pasquale', 'LAST': 'De Vita',
     'INSTITUTION': 'CREA Cerealicoltura e Colture Industriali',
     'VOICE_CLASS': 'RESEARCHER'},
    {'NAME': 'Nicola Pecchioni', 'FIRST': 'Nicola', 'LAST': 'Pecchioni',
     'INSTITUTION': 'CREA Cerealicoltura e Colture Industriali',
     'VOICE_CLASS': 'RESEARCHER'},
]


def entrada_de(alvo, teto=TETO_ITENS):
    """A entrada pretendida. Uma função só, para que contrato e gasto usem a MESMA.

    Se a conferência olhasse uma entrada e a execução mandasse outra, o portão
    do contrato seria decorativo.
    """
    return {'firstName': alvo['FIRST'], 'lastName': alvo['LAST'],
            'maxItems': teto}


def esqueleto(item, prefixo=''):
    """Nome e tipo de cada campo, sem valor. Descreve a forma sem publicar pessoa."""
    fora = {}
    if isinstance(item, dict):
        for k, v in sorted(item.items()):
            cam = prefixo + k
            if isinstance(v, dict):
                fora[cam] = 'object'
                fora.update(esqueleto(v, cam + '.'))
            elif isinstance(v, list):
                fora[cam] = 'array[%d]' % len(v)
                if v:
                    fora.update(esqueleto(v[0], cam + '[].'))
            else:
                fora[cam] = type(v).__name__
    return fora


def identidade(item):
    """O mínimo para dizer QUEM voltou. Local declarado nunca vira fato."""
    bi = item.get('basic_info') if isinstance(item, dict) else None
    bi = bi if isinstance(bi, dict) else (item if isinstance(item, dict) else {})
    return {
        'NAME': bi.get('fullname') or bi.get('name')
                or ' '.join(x for x in (bi.get('first_name'), bi.get('last_name')) if x)
                or 'NÃO SEI',
        'HEADLINE': (bi.get('headline') or 'NÃO SEI')[:160],
        'PROFILE_URL': bi.get('profile_url') or bi.get('public_identifier') or 'NÃO SEI',
        'PROFILE_DECLARED_LOCATION': str(bi.get('location') or 'NÃO SEI')[:120],
        'FACT_LOCATION': 'NOT_KNOWN — local declarado em perfil não é fato geográfico',
    }


def _norm(s):
    return ''.join(c for c in str(s).lower() if c.isalnum() or c == ' ').strip()


def bate_o_nome(pedido, voltou):
    """Sobrenome E prenome presentes no que voltou. Posição na lista não vale nada.

    Partículas curtas ("de", "di", "van") são descartadas: o ator pode devolvê-las
    ou não, e exigi-las produziria falso negativo em "De Vita". Mas se SÓ sobrarem
    partículas, não há o que comparar — e `all()` sobre lista vazia devolveria
    `True`, isto é, "bate com qualquer um". Esse é o mesmo falso verde que fez oito
    consultas diferentes aceitarem a mesma pessoa. Sem token comparável: False.
    """
    a, b = _norm(pedido), _norm(voltou)
    if not a or not b:
        return False
    tokens = [p for p in a.split() if len(p) > 2]
    if not tokens:
        return False
    devolvidos = b.split()
    return all(p in devolvidos for p in tokens)


def executar():
    out = {'CASE_ID': 'IT-CASE-DURUM-FUSARIUM-001',
           'SOURCE_ID': 'DERIVED/IT-LINKEDIN-PROVA-BUSCA',
           'source': 'Apify %s — prova pequena de rota' % ACTOR,
           'SOURCE_LOCATION': 'LinkedIn', 'FACT_LOCATION': 'ITALY',
           'ORIGINAL_LANGUAGE': 'it', 'EVIDENCE_CLASS': 'PRIMARY_SOURCE_PROBE',
           'captured_at': datetime.date.today().isoformat(),
           'CAPTURED_AT': datetime.date.today().isoformat(),
           'ACTOR': ACTOR, 'CAPS': {'NAMES': TETO_NOMES, 'ITEMS_PER_NAME': TETO_ITENS,
                                    'NOTE': 'teto da PROVA, não da coleta'},
           'TOKEN_VALUE_LOGGED': 'NO', 'TOKEN_VALUE_COMMITTED': 'NO',
           'LAWS': ['WRONG_INPUT_CONTRACT ≠ WRONG_PLATFORM',
                    'CONTRACT_MATCH ≠ USEFUL_DATA',
                    'ACTOR_SUCCESS ≠ USEFUL_DATA',
                    'PROVA DE ROTA ≠ MEDIDA DE SINAL']}
    ks = ap.pool()
    if not ks:
        out['STATE'] = 'APIFY_ENV_MISSING'
        out['VERDICT'] = 'ROUTE_NOT_PROVED'
        return out

    # ------------------------------------------------- portão 1 · contrato
    entrada_modelo = entrada_de(NOMES[0])
    try:
        meta, schema = ac.contrato(ACTOR, ks[0])
        props, req = ac.campos_do_schema(schema)
        conf = ac.conferir(props, req, entrada_modelo)
        conf['CONTRACT_FIELDS'] = sorted(props)
        conf['REQUIRED'] = sorted(req)
        conf['ACTOR_TITLE'] = meta.get('title')
    except Exception as e:
        conf = {'STATE': ac.CONTRACT_NOT_READABLE, 'ERROR': ap.redigir(str(e))[:180]}
    out['CONTRACT'] = conf
    out['INTENDED_INPUT_FIELDS'] = sorted(entrada_modelo)

    if conf['STATE'] not in (ac.CONTRACT_MATCH, ac.CONTRACT_NOT_READABLE):
        # Campo inexistente ou obrigatorio faltando: o gasto NAO acontece.
        out['STATE'] = 'CONTRACT_REFUSED_SPEND'
        out['VERDICT'] = 'ROUTE_NOT_PROVED'
        out['NEW_ACTOR_RUNS'] = 0
        out['WHY'] = ('a entrada pretendida nao satisfaz o contrato publicado. '
                      'Gastar aqui repetiria o defeito dos 8 runs.')
        return out
    if conf['STATE'] == ac.CONTRACT_NOT_READABLE:
        # Contrato ilegivel nao e contrato aprovado. Mas tambem nao e prova de
        # que a entrada esta errada — e ignorancia. A prova segue com DOIS nomes
        # justamente porque o custo de estar errado aqui e de dois runs.
        out['CONTRACT_NOTE'] = ('contrato nao lido — a prova segue no menor tamanho '
                                'possivel, e o RAW decide')

    # ------------------------------------------------------ portão 2 · RAW
    def trabalho(alvo, token):
        entrada = entrada_de(alvo)
        itens, man = coletor.executar(
            ACTOR, entrada, token=token,
            run_id='IT-LI-PROVA-%s' % alvo['NAME'].replace(' ', '-'),
            platform='LINKEDIN', country='IT', mission='HUMAN-SENSOR-LINKEDIN-PROVA',
            query=ap.redigir(json.dumps(entrada, ensure_ascii=False)),
            source_version=datetime.date.today().isoformat(),
            evidence_path='data/samples/IT-CASOS/IT-LINKEDIN-PROVA-BUSCA.json')
        est = ap.classificar(status=None if man['STATUS'] == 'SUCCESS' else 'FAILED',
                             status_message=str(man.get('ERROR') or ''), itens=itens)
        coletor.registrar(man, item_count_normalized=len(itens or []))
        return ([dict(i, _ALVO=alvo['NAME']) for i in (itens or []) if isinstance(i, dict)],
                est)

    r = ap.executar_com_pool(NOMES[:TETO_NOMES], trabalho,
                             identidade=lambda i: (i.get('_ALVO'), json.dumps(
                                 identidade(i), sort_keys=True, ensure_ascii=False)))
    out['NEW_ACTOR_RUNS'] = len(r['UNITS_DONE'])
    out['POOL'] = {'TOKENS_AVAILABLE': r['TOKENS_AVAILABLE'],
                   'TOKENS_USED': r['TOKENS_USED'],
                   'BY_POSITION': r['BY_POSITION'], 'STATE': r['STATE'],
                   'UNITS_DONE': [u['NAME'] for u in r['UNITS_DONE']],
                   'UNITS_PENDING': [u['NAME'] for u in r['UNITS_PENDING']]}

    # --------------------------------------------------- portão 3 · schema
    itens = r['ITEMS']
    formas, schemas = {}, {}
    for it in itens:
        sch = ls.detectar_schema(it)
        schemas[sch] = schemas.get(sch, 0) + 1
        for campo, tipo in esqueleto({k: v for k, v in it.items()
                                      if k != '_ALVO'}).items():
            formas[campo] = tipo
    out['ITEMS_RETURNED'] = len(itens)
    out['SCHEMA_COUNTS'] = schemas
    out['RAW_FIELD_MAP'] = formas
    out['KNOWN_SCHEMA'] = ls.SCHEMA_V1

    por_nome = {}
    for it in itens:
        ident = identidade(it)
        ident['REQUESTED_NAME'] = it.get('_ALVO')
        ident['NAME_MATCHES_REQUEST'] = bate_o_nome(it.get('_ALVO'), ident['NAME'])
        por_nome.setdefault(it['_ALVO'], []).append(ident)
    out['RETURNED_BY_NAME'] = por_nome

    distintos = {json.dumps(i, sort_keys=True) for v in por_nome.values() for i in
                 [{k: x[k] for k in ('NAME', 'PROFILE_URL')} for x in v]}
    out['DISTINCT_PEOPLE_RETURNED'] = len(distintos)
    com_match = [n for n, v in por_nome.items() if any(x['NAME_MATCHES_REQUEST'] for x in v)]
    out['NAMES_WITH_A_MATCHING_RETURN'] = sorted(com_match)

    # O defeito dos 8 runs, dito em uma condicao: consultas diferentes, mesma
    # pessoa de volta. Se isso reaparecer, a rota NAO esta provada.
    repetiu = (len(por_nome) > 1 and out['DISTINCT_PEOPLE_RETURNED'] == 1)
    out['SAME_PERSON_FOR_EVERY_QUERY'] = 'YES' if repetiu else 'NO'
    if not itens:
        out['STATE'], out['VERDICT'] = 'NO_ITEMS', 'ROUTE_NOT_PROVED'
    elif repetiu or not com_match:
        out['STATE'], out['VERDICT'] = 'RETURNED_BUT_NOT_THE_PEOPLE_ASKED', 'ROUTE_NOT_PROVED'
    else:
        out['STATE'], out['VERDICT'] = 'PROVED_ON_%d_NAMES' % len(com_match), 'ROUTE_PROVED'
    out['VERDICT_MUST_CARRY'] = {
        'SCOPE': '%d nome(s) de 8 — prova de rota' % len(por_nome),
        'HUMAN_SENSOR_LAYER': 'NOT_MEASURED — nenhum post foi lido nesta prova',
        'NEXT_GATE': 'ler o RAW preservado antes de ampliar para os 8',
    }
    return out


def main():
    out = executar()
    os.makedirs(os.path.dirname(DEST), exist_ok=True)
    with open(DEST, 'w', encoding='utf-8') as fh:
        fh.write(ap.redigir(json.dumps(out, ensure_ascii=False, indent=2)))
    print('CONTRACT =', (out.get('CONTRACT') or {}).get('STATE'))
    print('campos do contrato:',
          ', '.join((out.get('CONTRACT') or {}).get('CONTRACT_FIELDS', []))[:240])
    print('STATE    =', out.get('STATE'), '| VERDICT =', out.get('VERDICT'))
    print('runs     =', out.get('NEW_ACTOR_RUNS', 0),
          '| itens =', out.get('ITEMS_RETURNED', 0),
          '| pessoas distintas =', out.get('DISTINCT_PEOPLE_RETURNED', 0))
    for campo, tipo in sorted((out.get('RAW_FIELD_MAP') or {}).items())[:60]:
        print('   %-46s %s' % (campo[:46], tipo))
    for nome, v in (out.get('RETURNED_BY_NAME') or {}).items():
        for x in v:
            print('   pedido=%-20s voltou=%-26s bate=%s' % (
                nome[:20], x['NAME'][:26], x['NAME_MATCHES_REQUEST']))
    print('->', os.path.relpath(DEST, ROOT))


if __name__ == '__main__':
    main()
