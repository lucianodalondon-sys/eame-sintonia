#!/usr/bin/env python3
"""
CONTRATO DO ATOR — o portão grátis do gasto. Roda antes de toda fase paga, sem exceção.

    py scripts/contrato_ator.py apify~instagram-scraper
    py scripts/contrato_ator.py --missao instagram        # o conjunto da Missão 14

POR QUE ESTE ARQUIVO É O PRIMEIRO A RODAR
-------------------------------------------
Ler o schema de um ator é um GET. Custa ZERO e prova três coisas que, sem ele, só se
descobrem caro:

    1. o ator EXISTE com aquele identificador;
    2. ele aceita os campos que eu vou mandar — com os NOMES e os VALORES certos;
    3. o build de hoje é o mesmo que a última execução usou.

O piloto italiano desta casa queimou **8 execuções pagas** mandando um campo que o Actor
descartava em silêncio: os 8 runs devolveram o mesmo consultor de cibersegurança.

    ENTRADA ERRADA ≠ PLATAFORMA ERRADA. MATCH VAZIO NÃO AUTORIZA GASTO.

A ROTA NÃO PRECISA DE CHAVE, E ISSO IMPORTA
---------------------------------------------
`scripts/comunicacao_coleta.py` desistia com `POOL_EMPTY` quando não havia chave — e assim
a fase MAIS BARATA da casa era a primeira a parar de rodar. Verificado em 2026-09-02:
`GET https://api.apify.com/v2/acts/{ator}` responde **HTTP 200 sem credencial nenhuma**
para ator público. O portão passa a rodar em qualquer máquina, inclusive em teste.

O QUE ESTE ARQUIVO REPROVA, E POR QUÊ
---------------------------------------
`CAMPO_DESCONHECIDO`   nome que o schema não declara. É o defeito das 8 execuções: a
                       Apify NÃO recusa campo estranho, ela ignora em silêncio.
`VALOR_FORA_DO_ENUM`   medido em `scrapesmith~instagram-comments-scraper` 0.0.164: a
                       DESCRIÇÃO do campo sugere `recent_activity`, e o enum publicado é
                       `["popular","recent"]`. Quem obedece à descrição manda valor
                       inválido — e o padrão silencioso é `popular`, que enviesa a
                       amostra para o comentário mais curtido.
`CREDENCIAL_NA_ENTRADA` qualquer campo com cheiro de sessão, cookie, senha ou token. Esta
                       casa não entrega credencial a ator de terceiro, e um schema limpo
                       hoje não impede um campo novo amanhã.
`NO_INPUT_DECLARED`    entrada vazia contra ator com `required: []`. Tecnicamente passa,
                       e é exatamente por isso que é perigoso: o ator roda com os
                       `prefill` da vitrine (um deles traz `bbcnews`) e a fatura vem de
                       conteúdo que ninguém pediu.
`BUILD_DRIFT`          o build mudou desde a última vez. Os quatro atores oficiais de
                       Instagram foram reconstruídos no MESMO minuto de 2026-08-31; a
                       cadência é semanal. "Entrada provada ontem" aqui vale dias.

    PREFILL NÃO É DEFAULT. `prefill` só preenche a caixinha da interface da Apify; a API
    não o aplica. Quem lê `prefill` como "valor que vai junto se eu não mandar" planeja
    com um número que não existe.
"""
import json
import os
import re
import sys
import urllib.error
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)

API = 'https://api.apify.com/v2'
REGISTRO = os.path.join(ROOT, 'data', 'samples', 'CONTRATOS-DE-ATOR.json')

# Estados do contrato. Cada um é um ESTADO, não um grau de fracasso.
CONTRATO_OK = 'CONTRATO_OK'
ATOR_NAO_ALCANCADO = 'ATOR_NAO_ALCANCADO'
ATOR_NAO_ENCONTRADO = 'ATOR_NAO_ENCONTRADO'
SCHEMA_NAO_PUBLICADO = 'SCHEMA_NAO_PUBLICADO'
ENTRADA_REPROVADA = 'ENTRADA_REPROVADA'

# Palavras que denunciam campo de credencial. Larga, mas não larga a ponto de gritar à
# toa: a primeira versão trazia `auth` solto, e `auth` está dentro de **author**. Contra
# `harvestapi~linkedin-post-search` isso acusou `authorKeywords`, `authorUrls`,
# `authorsCompanies` e `authorsIndustryId` — quatro campos de BUSCA POR AUTOR, nenhum
# deles credencial.
#
#     AVISO QUE GRITA À TOA TREINA A CASA A IGNORAR AVISO.
#
# E o dia em que gritar certo, ninguém olha. Então `auth` sai, e entram as formas em que
# credencial de verdade aparece.
CHEIRO_DE_CREDENCIAL = ('sessionid', 'session_id', 'sessioncookie', 'cookie', 'password',
                        'passwd', 'senha', 'token', 'apikey', 'api_key', 'secret',
                        'credential', 'bearer', 'authorization', 'authtoken', 'auth_token',
                        'login', 'signin')

# Campos que CONTÊM uma palavra da lista mas são inocentes. Exceção explícita e curta —
# uma lista de perdão longa seria só outra forma de desligar a trava.
FALSO_POSITIVO = ('author', 'autor')


def _get(url, *, token=None, timeout=60):
    """GET simples. `token` é OPCIONAL: ator público responde sem credencial nenhuma."""
    cab = {'Authorization': 'Bearer %s' % token} if token else {}
    req = urllib.request.Request(url, headers=cab)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode('utf-8', 'replace'))


def ler(ator, *, token=None):
    """→ dict com identidade, build, preço e `inputSchema` do ator. Nunca levanta.

    Devolve sempre um dicionário com `STATE`. Falha de rede é `ATOR_NAO_ALCANCADO` —
    que é diferente de `ATOR_NAO_ENCONTRADO`, e as duas são diferentes de "o ator não
    serve". Confundir os três faz uma queda de rede virar veredito sobre a ferramenta.
    """
    fora = {'ACTOR': ator, 'READ_METHOD': 'GET /v2/acts/{ator} (sem credencial)',
            'TOKEN_USED': 'YES' if token else 'NO'}
    try:
        d = _get('%s/acts/%s' % (API, ator), token=token)
    except urllib.error.HTTPError as e:
        fora.update({'STATE': ATOR_NAO_ENCONTRADO if e.code == 404 else ATOR_NAO_ALCANCADO,
                     'WHY': 'HTTP %d' % e.code})
        return fora
    except Exception as e:                                    # noqa: BLE001
        fora.update({'STATE': ATOR_NAO_ALCANCADO,
                     'WHY': '%s: %s' % (type(e).__name__, str(e)[:140])})
        return fora

    a = (d or {}).get('data') or {}
    if not a:
        fora.update({'STATE': ATOR_NAO_ENCONTRADO, 'WHY': 'resposta sem `data`'})
        return fora

    latest = ((a.get('taggedBuilds') or {}).get('latest') or {})
    fora.update({
        'OWNER': a.get('username'), 'NAME': a.get('name'),
        'TITLE': a.get('title'),
        'BUILD_NUMBER': latest.get('buildNumber'),
        'BUILD_ID': latest.get('buildId'),
        'BUILD_FINISHED_AT': latest.get('finishedAt'),
        'PRICING': _preco(a),
    })

    # O schema vive no BUILD, não no ator — e vem como STRING de JSON dentro do JSON.
    if not latest.get('buildId'):
        fora.update({'STATE': SCHEMA_NAO_PUBLICADO,
                     'WHY': 'o ator não declara build `latest`',
                     'CAMPOS': [], 'OBRIGATORIOS': [], 'PROPRIEDADES': {}})
        return fora
    try:
        b = _get('%s/actor-builds/%s' % (API, latest['buildId']), token=token)
        sch = ((b or {}).get('data') or {}).get('inputSchema')
        if isinstance(sch, str) and sch.strip():
            sch = json.loads(sch)
        if not isinstance(sch, dict):
            raise ValueError('o build não publica inputSchema')
    except Exception as e:                                    # noqa: BLE001
        fora.update({'STATE': SCHEMA_NAO_PUBLICADO,
                     'WHY': '%s: %s' % (type(e).__name__, str(e)[:140]),
                     'CAMPOS': [], 'OBRIGATORIOS': [], 'PROPRIEDADES': {}})
        return fora

    props = sch.get('properties') or {}
    fora.update({
        'STATE': CONTRATO_OK,
        'CAMPOS': sorted(props),
        'OBRIGATORIOS': list(sch.get('required') or []),
        'PROPRIEDADES': {k: {'type': v.get('type'),
                             'enum': v.get('enum'),
                             'default': v.get('default'),
                             'prefill': v.get('prefill'),
                             'title': v.get('title')}
                         for k, v in props.items()},
    })
    return fora


def _preco(a):
    """O preço publicado, sem interpretar. Preço de tabela NÃO é custo medido."""
    infos = a.get('pricingInfos') or []
    if not infos:
        return {'MODEL': a.get('pricingModel') or 'NOT_KNOWN',
                'AVISO': 'o ator não publica pricingInfos por esta rota'}
    atual = infos[-1]
    return {
        'MODEL': atual.get('pricingModel') or 'NOT_KNOWN',
        'PRICE_PER_UNIT_USD': atual.get('pricePerUnitUsd'),
        'UNIT': atual.get('unitName'),
        'TRIAL_MINUTES': atual.get('trialMinutes'),
        'EVENTS': sorted((atual.get('pricingPerEvent') or {})
                         .get('actorChargeEvents') or {}),
        'AVISO': ('preço de TABELA lido agora. NÃO é custo medido — o real só aparece '
                  'em GET /v2/actor-runs depois da execução. Um piloto desta casa '
                  'anunciou US$0,90 e gastou US$5,04.'),
    }


# `author` neutraliza — MENOS quando é o começo de `authorization`, que é credencial de
# verdade. Apagar `author` cru fazia `authorization` virar `ization` e passar batido: a
# correção do falso positivo tinha aberto um falso NEGATIVO, que é muito pior.
_PERDAO = re.compile(r'autor(?!iz)|author(?!iz)')


def cheira_a_credencial(campo):
    """→ True se o NOME do campo indica credencial. `authorUrls` não é; `authorization` é."""
    limpo = _PERDAO.sub('', str(campo or '').lower())
    return any(t in limpo for t in CHEIRO_DE_CREDENCIAL)


def conferir(contrato, entrada, *, build_esperado=None):
    """→ (aprovado, lista_de_problemas). O portão propriamente dito.

    Não corrige a entrada e não adivinha: ele APROVA ou REPROVA, e diz por quê. Corrigir
    entrada em silêncio seria a mesma classe de defeito que o portão existe para pegar.
    """
    problemas = []
    if contrato.get('STATE') == SCHEMA_NAO_PUBLICADO:
        # Não é reprovação: é ausência de régua. Quem chama decide se anda com entrada
        # PROVADA (a que já rodou e está no manifesto) ou não anda.
        problemas.append({
            'GRAVIDADE': 'AVISO', 'CODIGO': SCHEMA_NAO_PUBLICADO,
            'DETALHE': ('este ator não publica inputSchema: %s. A entrada NÃO pode ser '
                        'conferida aqui. Só ande com entrada JÁ PROVADA e preservada no '
                        'RUN-MANIFEST — entrada provada vale mais que entrada inferida.'
                        % contrato.get('WHY'))})
        return True, problemas
    if contrato.get('STATE') != CONTRATO_OK:
        problemas.append({'GRAVIDADE': 'REPROVA', 'CODIGO': contrato.get('STATE'),
                          'DETALHE': str(contrato.get('WHY'))})
        return False, problemas

    props = contrato.get('PROPRIEDADES') or {}
    obrig = contrato.get('OBRIGATORIOS') or []

    # 1. entrada vazia. Passa no `required: []` e é justamente aí que dói.
    if not entrada:
        problemas.append({
            'GRAVIDADE': 'REPROVA', 'CODIGO': 'NO_INPUT_DECLARED',
            'DETALHE': ('entrada vazia. Mesmo com `required: []` isto não autoriza gasto: '
                        'o ator roda com os exemplos da vitrine e a fatura vem de '
                        'conteúdo que ninguém pediu.')})

    # 2. campo que o schema não conhece. A Apify IGNORA em silêncio — foi o defeito
    #    das 8 execuções que devolveram o mesmo consultor de cibersegurança.
    for k in entrada:
        if k not in props:
            perto = [c for c in props if c.lower().startswith(k[:4].lower())][:3]
            problemas.append({
                'GRAVIDADE': 'REPROVA', 'CODIGO': 'CAMPO_DESCONHECIDO', 'CAMPO': k,
                'DETALHE': ('o schema do build %s não declara `%s`. A Apify não recusa '
                            'campo estranho: ela DESCARTA em silêncio e cobra o run. '
                            'Campos parecidos: %s'
                            % (contrato.get('BUILD_NUMBER'), k, perto or 'nenhum'))})

    # 3. valor fora do enum publicado.
    for k, v in entrada.items():
        enum = (props.get(k) or {}).get('enum')
        if enum and not isinstance(v, (list, dict)) and v not in enum:
            problemas.append({
                'GRAVIDADE': 'REPROVA', 'CODIGO': 'VALOR_FORA_DO_ENUM', 'CAMPO': k,
                'DETALHE': ('`%s` = %r não está no enum publicado %s. A DESCRIÇÃO de um '
                            'campo pode citar valor que o enum não aceita — obedecer à '
                            'prosa em vez do enum manda valor inválido.' % (k, v, enum))})

    # 4. obrigatório ausente.
    for k in obrig:
        if k not in entrada:
            problemas.append({
                'GRAVIDADE': 'REPROVA', 'CODIGO': 'OBRIGATORIO_AUSENTE', 'CAMPO': k,
                'DETALHE': 'o schema declara `%s` como obrigatório e ele não foi mandado' % k})

    # 5. credencial — na entrada que eu mando E no schema que o ator oferece.
    for k in entrada:
        if cheira_a_credencial(k):
            problemas.append({
                'GRAVIDADE': 'REPROVA', 'CODIGO': 'CREDENCIAL_NA_ENTRADA', 'CAMPO': k,
                'DETALHE': ('esta casa não entrega credencial a ator de terceiro. '
                            'Rota que exige sessão de alguém é rota recusada.')})
    oferecidos = sorted(k for k in props if cheira_a_credencial(k))
    if oferecidos:
        problemas.append({
            'GRAVIDADE': 'AVISO', 'CODIGO': 'ATOR_ACEITA_CREDENCIAL',
            'DETALHE': ('o ator ACEITA campo de credencial (%s). Não mandamos nenhum — '
                        'mas fica registrado que a rota tem essa porta, e que o preço '
                        'anunciado pode supor que ela seja usada.' % ', '.join(oferecidos))})

    # 6. o build mudou desde a última vez.
    if build_esperado and contrato.get('BUILD_NUMBER') != build_esperado:
        problemas.append({
            'GRAVIDADE': 'REPROVA', 'CODIGO': 'BUILD_DRIFT',
            'DETALHE': ('o build era %s e hoje é %s (terminado em %s). Contrato de ator '
                        'muda em dias: reler o schema antes de gastar.'
                        % (build_esperado, contrato.get('BUILD_NUMBER'),
                           contrato.get('BUILD_FINISHED_AT')))})

    aprovado = not any(p['GRAVIDADE'] == 'REPROVA' for p in problemas)
    return aprovado, problemas


def portao(ator, entrada, *, token=None, build_esperado=None):
    """Leitura + conferência num passo. É esta que as fases pagas chamam."""
    c = ler(ator, token=token)
    ok, probs = conferir(c, entrada, build_esperado=build_esperado)
    return {
        'ACTOR': ator,
        'BUILD_NUMBER': c.get('BUILD_NUMBER'),
        'BUILD_ID': c.get('BUILD_ID'),
        'CONTRACT_STATE': c.get('STATE'),
        'PRICING': c.get('PRICING'),
        'FIELDS_DECLARED': c.get('CAMPOS'),
        'REQUIRED': c.get('OBRIGATORIOS'),
        'INPUT_CHECKED': entrada,
        'APPROVED': 'YES' if ok else 'NO',
        'PROBLEMS': probs,
        'COST_USD': 0,
        'LEI': 'MATCH VAZIO NÃO AUTORIZA GASTO. Fase paga não roda com APPROVED=NO.',
    }, ok


def _imprimir(r):
    print('%-46s %-20s build %-10s %s'
          % (r['ACTOR'], r['CONTRACT_STATE'], r.get('BUILD_NUMBER'),
             'APROVADO' if r['APPROVED'] == 'YES' else 'REPROVADO'))
    for p in r['PROBLEMS']:
        print('    [%s] %s%s' % (p['GRAVIDADE'], p['CODIGO'],
                                 (' · campo `%s`' % p['CAMPO']) if p.get('CAMPO') else ''))
        print('        %s' % p['DETALHE'])


if __name__ == '__main__':
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    tok = os.environ.get('APIFY_TOKEN') or None
    if not args:
        print(__doc__.strip().splitlines()[0])
        print('uso: contrato_ator.py <owner~name> [outro~ator ...]')
        raise SystemExit(2)
    saida, todos_ok = [], True
    for ator in args:
        r, ok = portao(ator, {}, token=tok)     # sem entrada: só lê e mostra o contrato
        todos_ok = todos_ok and ok
        _imprimir(r)
        if r['FIELDS_DECLARED']:
            print('    campos: %s' % ', '.join(r['FIELDS_DECLARED']))
        saida.append(r)
    raise SystemExit(0 if todos_ok else 1)
