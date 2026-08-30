#!/usr/bin/env python3
"""
PROVA PEQUENA e, depois dela, os oito — contrato conferido antes, RAW lido depois.

A missão manda: antes de ampliar, 1–2 provas pequenas, olhar o RAW, confirmar o
schema. Sem `--todos`, este arquivo faz exatamente isso: DOIS nomes, teto no
código. Com `--todos`, mede os oito — que já estavam identificados antes de
qualquer chave existir. Nome novo não entra por aqui em nenhum dos dois modos.

TRÊS PORTÕES, NESTA ORDEM
--------------------------
1. **CONTRATO** — `apify_contrato` lê o `inputSchema` publicado, de graça. Se o
   campo que eu pretendo mandar não existir no contrato, o gasto **não acontece**:
   sai `CONTRACT_REFUSED_SPEND`. Foi a ausência deste portão que custou 8 runs.
2. **RAW** — o bruto é gravado por `coletor.executar` antes de qualquer leitura.
3. **SCHEMA** — a forma do que voltou é descrita campo a campo, e comparada com o
   que `linkedin_schema` já conhece. Forma nova é `UNKNOWN_SCHEMA`, nunca "vazio".
4. **IDENTIDADE** — nome igual não é pessoa. Medido: a busca por "Pasquale De
   Vita" devolveu o presidente da Unione Petrolifera, um vendedor de esquadrias e
   um diretor de TI, todos de nome idêntico. O título declarado decide, e só até
   onde ele vai — `CONFIRMED` exige que o título NOMEIE a instituição do alvo.

O QUE ESTE ARQUIVO SE RECUSA A CONCLUIR
----------------------------------------
Não conclui que a camada de sensores humanos existe ou não existe. Dois nomes não
medem oito, e oito não medem a Itália. O veredito que ele pode dar é sobre a
ROTA — `ROUTE_PROVED` ou `ROUTE_NOT_PROVED` —, nunca sobre o campo.

    PROVA DE ROTA ≠ MEDIDA DE SINAL
"""
import datetime
import glob
import gzip
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
TETO_NOMES = 2                # teto da PROVA. `--todos` sobe para o teto da missão.
TETO_ALVOS_MISSAO = 8         # teto da MISSÃO. Nenhuma bandeira sobe daqui.
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


# O contrato do ator, lido de graça em 2026-08-30 (run 33320039453, 0 USD), diz:
# obrigatório `profileScraperMode`, com enum ["Short", "Full", "Full + email search"].
#
# "Short" basta e é o certo. Para dizer QUEM voltou eu preciso de nome, título e
# instituição — nada mais. "Full + email search" colheria endereço de e-mail de
# pessoas que não pediram nada a ninguém: dado pessoal que a pergunta desta missão
# não precisa, e por isso não se coleta.
MODO = 'Short'
MODO_PROIBIDO = 'Full + email search'


def entrada_de(alvo, teto=TETO_ITENS):
    """A entrada pretendida. Uma função só, para que contrato e gasto usem a MESMA.

    Se a conferência olhasse uma entrada e a execução mandasse outra, o portão
    do contrato seria decorativo.

    Não filtro por `locations` nem por `currentCompanies`, embora o contrato os
    aceite: um pesquisador que declare outro país ou outra afiliação sairia da
    resposta e viraria NOT_FOUND — que é exatamente a confusão entre "não achei"
    e "não existe". Filtrar é do meu lado, depois, comparando nome e instituição
    com o que voltou.
    """
    return {'firstName': alvo['FIRST'], 'lastName': alvo['LAST'],
            'profileScraperMode': MODO, 'maxItems': teto}


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
    """O mínimo para dizer QUEM voltou. Local declarado nunca vira fato.

    A leitura é delegada a `linkedin_schema.extrair_perfil`: existe UM parser, e
    ele conhece os dois contratos medidos deste fornecedor. Ter aqui uma segunda
    leitura "só para a prova" foi o que quase custou de novo — ela lia `headline`
    num item cujo campo se chama `position`, e devolveria NÃO SEI para um título
    que estava lá.
    """
    p = ls.extrair_perfil(item if isinstance(item, dict) else {})
    nome = p.get('FULLNAME') or ' '.join(
        x for x in (p.get('FIRST_NAME'), p.get('LAST_NAME')) if x)
    return {
        'SCHEMA': p.get('SCHEMA'),
        'NAME': nome or 'NÃO SEI',
        'HEADLINE': (p.get('HEADLINE') or 'NÃO SEI')[:160],
        'PROFILE_URL': p.get('PROFILE_URL') or p.get('PUBLIC_IDENTIFIER') or 'NÃO SEI',
        'PROFILE_DECLARED_LOCATION': str(p.get('LOCATION') or 'NÃO SEI')[:120],
        'FACT_LOCATION': 'NOT_KNOWN — local declarado em perfil não é fato geográfico',
    }


# Vocabulário do DOMÍNIO do caso. Não é lista de palavras-chave para pontuar: é o
# mínimo para separar "trabalha com planta/agronomia/pesquisa" de "não trabalha".
DOMINIO = ('crop', 'agron', 'agricol', 'agrar', 'cerealic', 'genom', 'genetic',
           'fitopatolog', 'ricercat', 'research', 'sement', 'grano', 'frumento',
           'colture', 'vegetal', 'plant', 'breeding', 'miglioramento genetico')

# Sinais de que a pessoa está em OUTRO ramo. Existem para que "não achei o domínio"
# não seja confundido com "achei outro domínio": a primeira é ignorância sobre um
# título curto; a segunda é evidência de que é outra pessoa.
FORA_DO_DOMINIO = ('petrolifer', 'infiss', 'bagni', 'it director', 'cloud',
                   'commerciante', 'assicuraz', 'immobili', 'ristorant')

IDENTITY_CONFIRMED = 'IDENTITY_CONFIRMED'
IDENTITY_PLAUSIBLE = 'IDENTITY_PLAUSIBLE_NOT_PROVED'
IDENTITY_MISMATCH = 'IDENTITY_MISMATCH'
IDENTITY_NOT_ENOUGH = 'IDENTITY_NOT_ENOUGH_EVIDENCE'


def conferir_identidade(alvo, ident):
    """Nome igual não é pessoa. O título declarado decide, e só até onde ele vai.

    Medido em 2026-08-30 sobre o RAW já pago: a busca por "Pasquale De Vita"
    devolveu TRÊS pessoas cujo nome bate — o presidente da Unione Petrolifera, um
    vendedor de esquadrias e um diretor de TI. Nenhuma delas é o pesquisador do
    CREA. Um portão que parasse no nome teria promovido o presidente da associação
    do petróleo a pesquisador de trigo duro, e o relatório teria dito isso com toda
    a confiança do mundo.

        NAME_MATCH ≠ PERSON

    Os quatro estados são deliberadamente assimétricos:
      · CONFIRMED  — o título NOMEIA a instituição do alvo. É a única prova.
      · PLAUSIBLE  — o título está no domínio do caso, mas não nomeia a instituição.
                     É candidato, não é resposta.
      · MISMATCH   — o título nomeia outro ramo. Evidência de que é outra pessoa.
      · NOT_ENOUGH — nome truncado pela plataforma, ou título ausente ou curto
                     demais. Ignorância, e ignorância não é divergência.
    """
    nome, titulo = ident.get('NAME') or '', ident.get('HEADLINE') or ''
    if not bate_o_nome(alvo['NAME'], nome):
        if nome_truncado(nome):
            return IDENTITY_NOT_ENOUGH, 'sobrenome abreviado pela plataforma'
        return IDENTITY_MISMATCH, 'o nome devolvido não é o nome pedido'
    t = _norm(titulo)
    if not t or t == 'nao sei':
        return IDENTITY_NOT_ENOUGH, 'nome bate, mas não há título declarado'
    # A instituição casa por QUALQUER token longo dela: "CREA Cerealicoltura e
    # Colture Industriali" no perfil raramente vem por extenso.
    tokens = [w for w in _norm(alvo.get('INSTITUTION', '')).split() if len(w) > 3]
    if any(w in t for w in tokens):
        return IDENTITY_CONFIRMED, 'o título nomeia a instituição do alvo'
    if any(w in t for w in FORA_DO_DOMINIO):
        return IDENTITY_MISMATCH, 'o título nomeia outro ramo de atividade'
    if any(w in t for w in DOMINIO):
        return IDENTITY_PLAUSIBLE, 'o título está no domínio, mas não nomeia a instituição'
    return IDENTITY_NOT_ENOUGH, 'o título não diz nem a favor nem contra'


def resolver_alvo(estados):
    """O estado do ALVO a partir dos estados dos seus candidatos.

    Se nenhum candidato serve, o alvo é `NOT_FOUND_IN_RESULTS` — e isso NÃO é
    "não está no LinkedIn". Pedi cinco resultados; a plataforma devolveu três.
    O que não veio nos três não foi negado: não foi perguntado até o fim.

        NOT_FOUND_IN_RESULTS ≠ NOT_ON_PLATFORM ≠ DOES_NOT_EXIST
    """
    if not estados:
        return 'NOT_FOUND_IN_RESULTS'
    for forte in (IDENTITY_CONFIRMED, IDENTITY_PLAUSIBLE):
        if forte in estados:
            return forte
    if all(e == IDENTITY_MISMATCH for e in estados):
        return 'NOT_FOUND_IN_RESULTS'
    return IDENTITY_NOT_ENOUGH


def nome_truncado(nome):
    """LinkedIn abrevia o sobrenome de quem está fora da rede: "Pasquale D.".

    Isso NÃO é outra pessoa e NÃO é uma não-resposta. É a mesma pessoa possível,
    com o sobrenome que eu precisaria para provar retido pela plataforma. Chamar
    isso de MISMATCH inventaria uma divergência; chamar de CONFIRMED inventaria
    uma identidade. É um terceiro estado.

        TRUNCATED_NAME ≠ MISMATCH ≠ CONFIRMED
    """
    partes = _norm(nome).split()
    return bool(partes) and any(len(p) == 1 for p in partes[1:])


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


RAW_DIR = os.path.join(ROOT, 'data', 'samples', 'raw-paid')


def reler_raw():
    """Refaz a leitura sobre o RAW JÁ PAGO. Zero execuções novas.

    É para isto que `coletor` grava o bruto antes de interpretar. Quando o defeito
    está no MEU parser — e estava: eu lia `headline` num item cujo campo se chama
    `position` —, corrigir o parser e reler custa nada. Pagar de novo pelos mesmos
    dados para consertar um erro meu seria transformar

        DINHEIRO GASTO ≠ DADO PRESERVADO

    de lei em desculpa. O bruto está preservado; a releitura é gratuita.
    """
    itens = []
    for caminho in sorted(glob.glob(os.path.join(RAW_DIR, 'IT-LI-PROVA-*.raw.json.gz'))):
        alvo = os.path.basename(caminho)[len('IT-LI-PROVA-'):-len('.raw.json.gz')]
        alvo = alvo.replace('-', ' ')
        try:
            with gzip.open(caminho, 'rt', encoding='utf-8') as fh:
                bruto = json.load(fh)
        except (OSError, ValueError) as e:
            itens.append({'_ALVO': alvo, '_RAW_UNREADABLE': type(e).__name__})
            continue
        for it in (bruto or []):
            if isinstance(it, dict):
                itens.append(dict(it, _ALVO=alvo))
    return itens


def ler_itens(itens, out):
    """Tudo que se conclui a partir dos itens — usado pela execução E pela releitura."""
    formas, schemas = {}, {}
    for it in itens:
        sch = ls.detectar_schema({k: v for k, v in it.items() if k != '_ALVO'})
        schemas[sch] = schemas.get(sch, 0) + 1
        for campo, tipo in esqueleto({k: v for k, v in it.items()
                                      if k != '_ALVO'}).items():
            formas[campo] = tipo
    out['ITEMS_RETURNED'] = len(itens)
    out['SCHEMA_COUNTS'] = schemas
    out['RAW_FIELD_MAP'] = formas
    out['KNOWN_SCHEMAS'] = list(ls.SCHEMAS_CONHECIDOS)

    por_nome = {}
    for it in itens:
        ident = identidade({k: v for k, v in it.items() if k != '_ALVO'})
        ident['REQUESTED_NAME'] = it.get('_ALVO')
        bate = bate_o_nome(it.get('_ALVO'), ident['NAME'])
        ident['NAME_MATCHES_REQUEST'] = bate
        ident['NAME_STATE'] = ('NAME_MATCHES' if bate else
                               'TRUNCATED_BY_PLATFORM' if nome_truncado(ident['NAME'])
                               else 'DIFFERENT_NAME')
        por_nome.setdefault(it.get('_ALVO'), []).append(ident)
    por_alvo = {a['NAME']: a for a in alvos(todos=True)}
    for pedido, candidatos in por_nome.items():
        alvo = por_alvo.get(pedido) or {'NAME': pedido, 'INSTITUTION': ''}
        for c in candidatos:
            c['IDENTITY_STATE'], c['IDENTITY_WHY'] = conferir_identidade(alvo, c)
    out['RETURNED_BY_NAME'] = por_nome
    out['IDENTITY_BY_TARGET'] = {
        pedido: {
            'INSTITUTION_ASKED': (por_alvo.get(pedido) or {}).get('INSTITUTION', 'NÃO SEI'),
            'CANDIDATES': len(cands),
            'STATE': resolver_alvo([c['IDENTITY_STATE'] for c in cands]),
            'BY_CANDIDATE': [{'NAME': c['NAME'], 'HEADLINE': c['HEADLINE'],
                              'IDENTITY_STATE': c['IDENTITY_STATE'],
                              'WHY': c['IDENTITY_WHY'],
                              'PROFILE_URL': c['PROFILE_URL']} for c in cands],
        } for pedido, cands in por_nome.items()}
    out['IDENTITY_CONFIRMED_COUNT'] = sum(
        1 for v in out['IDENTITY_BY_TARGET'].values() if v['STATE'] == IDENTITY_CONFIRMED)
    out['IDENTITY_PLAUSIBLE_COUNT'] = sum(
        1 for v in out['IDENTITY_BY_TARGET'].values() if v['STATE'] == IDENTITY_PLAUSIBLE)

    distintos = {(x['NAME'], x['PROFILE_URL']) for v in por_nome.values() for x in v}
    out['DISTINCT_PEOPLE_RETURNED'] = len(distintos)
    com_match = [n for n, v in por_nome.items()
                 if any(x['NAME_MATCHES_REQUEST'] for x in v)]
    out['NAMES_WITH_A_MATCHING_RETURN'] = sorted(com_match)
    # Mais de um retorno que bate no nome NAO e identidade resolvida: e homonimia
    # por resolver. Nome igual nao prova mesma pessoa.
    out['NAMES_WITH_MORE_THAN_ONE_MATCH'] = sorted(
        n for n, v in por_nome.items()
        if sum(1 for x in v if x['NAME_MATCHES_REQUEST']) > 1)

    repetiu = (len(por_nome) > 1 and out['DISTINCT_PEOPLE_RETURNED'] == 1)
    out['SAME_PERSON_FOR_EVERY_QUERY'] = 'YES' if repetiu else 'NO'
    if not itens:
        out['STATE'], out['VERDICT'] = 'NO_ITEMS', 'ROUTE_NOT_PROVED'
    elif repetiu or not com_match:
        out['STATE'] = 'RETURNED_BUT_NOT_THE_PEOPLE_ASKED'
        out['VERDICT'] = 'ROUTE_NOT_PROVED'
    else:
        out['STATE'] = 'PROVED_ON_%d_NAMES' % len(com_match)
        out['VERDICT'] = 'ROUTE_PROVED'
    out['VERDICT_MUST_CARRY'] = {
        'SCOPE': '%d nome(s) de %d da missao' % (len(por_nome), TETO_ALVOS_MISSAO),
        'IDENTITY': '%d CONFIRMED, %d PLAUSIBLE de %d alvos' % (
            out['IDENTITY_CONFIRMED_COUNT'], out['IDENTITY_PLAUSIBLE_COUNT'],
            len(por_nome)),
        'WHY_NAME_IS_NOT_ENOUGH': ('a busca por Pasquale De Vita devolveu tres '
                                   'pessoas de nome igual e nenhuma do CREA'),
        'HUMAN_SENSOR_LAYER': 'NOT_MEASURED — nenhum post foi lido nesta prova',
        'NEXT_GATE': 'so alvo CONFIRMED ou PLAUSIBLE pode ir para a coleta de posts',
    }
    return out


def alvos(todos=False):
    """Os dois da prova, ou os oito da missão. Nunca um nome novo.

    `--todos` NÃO é uma ampliação de escopo: os oito já estavam identificados
    antes de qualquer chave existir. O que muda é só quantos deles são medidos.
    Nome novo entraria por outra porta, com outra missão.
    """
    if not todos:
        return NOMES[:TETO_NOMES]
    import linkedin_sensores as sn
    fora, vistos = [], {a['NAME'] for a in NOMES}
    for a in NOMES[:TETO_NOMES]:
        fora.append(a)
    for a in sn.ALVOS:
        if a['NAME'] in vistos:
            continue
        pedacos = a['NAME'].split()
        fora.append({'NAME': a['NAME'], 'FIRST': pedacos[0],
                     'LAST': ' '.join(pedacos[1:]),
                     'INSTITUTION': a['INSTITUTION'],
                     'VOICE_CLASS': a['VOICE_CLASS']})
    return fora[:TETO_ALVOS_MISSAO]


def executar(todos=False):
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
    lista = alvos(todos)
    out['TARGETS_ASKED'] = [a['NAME'] for a in lista]
    entrada_modelo = entrada_de(lista[0])
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
        # A traducao do manifesto para estado vive em UM lugar. Repeti-la aqui foi
        # o que mandou 'FAILED' para todo manifesto que nao fosse SUCCESS — e
        # 'PARTIAL por zero itens' virava falha do ator, parando a fila inteira.
        est = ap.estado_da_execucao(man, itens)
        coletor.registrar(man, item_count_normalized=len(itens or []))
        return ([dict(i, _ALVO=alvo['NAME']) for i in (itens or []) if isinstance(i, dict)],
                est)

    r = ap.executar_com_pool(lista, trabalho,
                             identidade=lambda i: (i.get('_ALVO'), json.dumps(
                                 identidade(i), sort_keys=True, ensure_ascii=False)))
    out['NEW_ACTOR_RUNS'] = len(r['UNITS_DONE'])
    out['POOL'] = {'TOKENS_AVAILABLE': r['TOKENS_AVAILABLE'],
                   'TOKENS_USED': r['TOKENS_USED'],
                   'BY_POSITION': r['BY_POSITION'], 'STATE': r['STATE'],
                   'UNITS_DONE': [u['NAME'] for u in r['UNITS_DONE']],
                   'UNITS_PENDING': [u['NAME'] for u in r['UNITS_PENDING']]}

    # --------------------------------------------------- portão 3 · schema
    return ler_itens(r['ITEMS'], out)


def main():
    if '--reler-raw' in sys.argv:
        out = {'CASE_ID': 'IT-CASE-DURUM-FUSARIUM-001',
               'SOURCE_ID': 'DERIVED/IT-LINKEDIN-PROVA-BUSCA',
               'source': 'releitura do RAW já pago — nenhuma execução nova',
               'SOURCE_LOCATION': 'LinkedIn', 'FACT_LOCATION': 'ITALY',
               'ORIGINAL_LANGUAGE': 'it', 'EVIDENCE_CLASS': 'PRIMARY_SOURCE_PROBE',
               'captured_at': datetime.date.today().isoformat(),
               'CAPTURED_AT': datetime.date.today().isoformat(),
               'ACTOR': ACTOR, 'NEW_ACTOR_RUNS': 0, 'COST_USD': 0,
               'READ_MODE': 'REREAD_PRESERVED_RAW',
               'TOKEN_VALUE_LOGGED': 'NO', 'TOKEN_VALUE_COMMITTED': 'NO',
               'LAWS': ['DINHEIRO GASTO ≠ DADO PRESERVADO',
                        'PROVA DE ROTA ≠ MEDIDA DE SINAL',
                        'TRUNCATED_NAME ≠ MISMATCH ≠ CONFIRMED',
                        'SEARCH_HIT ≠ PERSON']}
        itens = reler_raw()
        if not itens:
            out['STATE'] = 'RAW_NOT_PRESENT'
            out['VERDICT'] = 'NOT_MEASURED'
            out['WHY'] = ('nenhum RAW de prova em %s — releitura sem bruto não é '
                          'releitura' % os.path.relpath(RAW_DIR, ROOT))
        else:
            ler_itens(itens, out)
    else:
        out = executar('--todos' in sys.argv)
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
            print('   pedido=%-18s voltou=%-22s %-30s %s' % (
                nome[:18], x['NAME'][:22], x.get('IDENTITY_STATE', ''),
                (x['HEADLINE'] or '')[:56]))
    for alvo, v in (out.get('IDENTITY_BY_TARGET') or {}).items():
        print('   ALVO %-20s %-30s candidatos=%d' % (alvo[:20], v['STATE'],
                                                     v['CANDIDATES']))
    print('->', os.path.relpath(DEST, ROOT))


if __name__ == '__main__':
    main()
