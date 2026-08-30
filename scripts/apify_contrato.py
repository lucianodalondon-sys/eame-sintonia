#!/usr/bin/env python3
"""
QUE ENTRADA ESTE ATOR LÊ — perguntado ao próprio ator, de graça, ANTES de gastar.

Os oito runs perdidos não morreram de plataforma errada nem de nome errado. O
ator `apimaestro~linkedin-profile-detail` recebeu `searchQuery`, um campo que ele
não lê, ignorou-o em silêncio e devolveu um perfil qualquer — oito vezes o mesmo.
`SUCCEEDED`, item bem formado, custo cobrado, resposta inútil.

    WRONG_INPUT_CONTRACT ≠ WRONG_PLATFORM

O contrato estava publicado o tempo todo. Todo ator da Apify carrega, no build
marcado como `latest`, um `inputSchema` que diz o nome de cada campo, o tipo, e
quais são obrigatórios. Ler isso é `GET`, é gratuito e não abre execução.

    GET /v2/acts/{ator}                 -> taggedBuilds.latest.buildId
    GET /v2/acts/{ator}/builds/{build}  -> inputSchema (JSON dentro de string)

O QUE ESTE ARQUIVO DECIDE E O QUE NÃO DECIDE
---------------------------------------------
Decide: se o campo que eu pretendo mandar EXISTE no contrato, e se algum campo
obrigatório vai faltar. Isso é verificável antes de qualquer centavo.

NÃO decide: se o ator devolve dado útil. Um contrato satisfeito é `INPUT_ACCEPTED`
— nunca `USEFUL_DATA`. Só a leitura do RAW de uma execução pequena diz isso, e é
outro arquivo que faz essa parte.

    CONTRACT_MATCH ≠ USEFUL_DATA
"""
import datetime
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import apify_pool as ap  # noqa: E402

DEST = os.path.join(ROOT, 'data', 'samples', 'IT-CASOS', 'IT-APIFY-CONTRATO.json')

CONTRACT_MATCH = 'CONTRACT_MATCH'
CONTRACT_FIELD_UNKNOWN = 'CONTRACT_FIELD_UNKNOWN'
CONTRACT_REQUIRED_MISSING = 'CONTRACT_REQUIRED_MISSING'
CONTRACT_NOT_READABLE = 'CONTRACT_NOT_READABLE'

# O ator, e a entrada que eu PRETENDO mandar. Declarar a intenção aqui é o que
# torna a conferência possível: sem entrada pretendida não há o que conferir.
PLANO = [
    ('harvestapi~linkedin-profile-search-by-name',
     {'firstName': 'Pasquale', 'lastName': 'De Vita', 'maxItems': 5}),
    # A leitura anterior mostrou que este ator nao le `searchQuery` nem `maxItems`,
    # e que aceita `authorUrls` — dar-lhe a URL de um perfil ja CONFIRMADO e
    # exatamente a pergunta certa: os posts DAQUELA pessoa, nao de um nome.
    ('harvestapi~linkedin-post-search',
     {'authorUrls': ['https://www.linkedin.com/in/exemplo'], 'maxPosts': 20,
      'postedLimit': 'any'}),
]


def _get(url, token, timeout=90):
    r = subprocess.run(['curl', '-sS', '-H', 'Authorization: Bearer %s' % token, url],
                       capture_output=True, text=True, timeout=timeout)
    if r.returncode != 0:
        raise RuntimeError(ap.redigir(r.stderr[:200]))
    return json.loads(r.stdout)


def campos_do_schema(schema):
    """Devolve (propriedades, obrigatórios). Tolera schema ausente ou malformado."""
    if not isinstance(schema, dict):
        return {}, []
    props = schema.get('properties')
    props = props if isinstance(props, dict) else {}
    req = schema.get('required')
    req = [r for r in req if isinstance(r, str)] if isinstance(req, list) else []
    return props, req


def detalhe(prop):
    """Tipo, valores permitidos e padrão de UM campo do contrato.

    Saber que `profileScraperMode` é obrigatório não basta para preenchê-lo: é
    preciso saber QUE valores ele aceita. O `enum` está publicado no mesmo schema
    gratuito. Chutar o valor de um campo obrigatório é a mesma aposta que mandar
    um campo inexistente — só que mais cara, porque o run abre.
    """
    if not isinstance(prop, dict):
        return {'TYPE': 'NÃO SEI'}
    d = {'TYPE': prop.get('type') or 'NÃO SEI'}
    for chave, rotulo in (('enum', 'ENUM'), ('default', 'DEFAULT'),
                          ('prefill', 'PREFILL'), ('editor', 'EDITOR')):
        if prop.get(chave) is not None:
            d[rotulo] = prop[chave]
    return d


def conferir(props, obrigatorios, entrada):
    """Confere a entrada PRETENDIDA contra o contrato publicado.

    Um contrato vazio não é um contrato satisfeito: sem propriedades declaradas
    não há como saber, e o estado honesto é NOT_READABLE, não MATCH.
    """
    if not props:
        return {'STATE': CONTRACT_NOT_READABLE, 'UNKNOWN_FIELDS': [],
                'REQUIRED_MISSING': [], 'ACCEPTED_FIELDS': []}
    desconhecidos = sorted(k for k in entrada if k not in props)
    faltando = sorted(k for k in obrigatorios if k not in entrada)
    aceitos = sorted(k for k in entrada if k in props)
    estado = CONTRACT_MATCH
    if faltando:
        estado = CONTRACT_REQUIRED_MISSING
    elif desconhecidos:
        estado = CONTRACT_FIELD_UNKNOWN
    return {'STATE': estado, 'UNKNOWN_FIELDS': desconhecidos,
            'REQUIRED_MISSING': faltando, 'ACCEPTED_FIELDS': aceitos}


def contrato(actor, token):
    """Lê o contrato publicado do ator. Nenhuma execução é aberta."""
    ator = _get('https://api.apify.com/v2/acts/%s' % actor, token).get('data') or {}
    build = ((ator.get('taggedBuilds') or {}).get('latest') or {}).get('buildId')
    if not build:
        raise RuntimeError('ator sem build marcado como latest')
    b = _get('https://api.apify.com/v2/acts/%s/builds/%s' % (actor, build), token)
    bruto = (b.get('data') or {}).get('inputSchema')
    # A Apify entrega o inputSchema como STRING de JSON dentro do JSON do build.
    # Decodificar duas vezes nao e paranoia: e o formato.
    if isinstance(bruto, str):
        try:
            bruto = json.loads(bruto)
        except ValueError:
            bruto = None
    return ator, bruto


def main():
    ks = ap.pool()
    out = {'SOURCE_ID': 'DERIVED/IT-APIFY-CONTRATO',
           'source': 'inputSchema publicado de cada Actor — GET gratuito, sem run',
           'SOURCE_LOCATION': 'Apify', 'FACT_LOCATION': 'n/a — metadado de coleta',
           'ORIGINAL_LANGUAGE': 'pt', 'EVIDENCE_CLASS': 'PRIMARY_SOURCE_PROBE',
           'captured_at': datetime.date.today().isoformat(),
           'CAPTURED_AT': datetime.date.today().isoformat(),
           'NEW_ACTOR_RUNS': 0, 'COST_USD': 0,
           'WHY': ('o contrato de entrada estava publicado quando os 8 runs foram '
                   'gastos. Le-lo custa zero e teria evitado todos os oito.'),
           'LAWS': ['WRONG_INPUT_CONTRACT ≠ WRONG_PLATFORM',
                    'CONTRACT_MATCH ≠ USEFUL_DATA']}
    if not ks:
        out['STATE'] = 'APIFY_ENV_MISSING'
        out['ACTORS'] = []
    else:
        linhas = []
        for actor, entrada in PLANO:
            reg = {'ACTOR': actor, 'INTENDED_INPUT': sorted(entrada)}
            try:
                meta, schema = contrato(actor, ks[0])
                props, req = campos_do_schema(schema)
                reg['TITLE'] = meta.get('title')
                reg['CONTRACT_FIELDS'] = sorted(props)
                reg['REQUIRED'] = sorted(req)
                # Detalhe SO dos campos que importam para preencher a entrada: os
                # obrigatorios e os que eu pretendo mandar. O contrato inteiro tem
                # dezenas de campos e publicar todos aqui esconderia esses.
                reg['FIELD_DETAIL'] = {k: detalhe(props[k])
                                       for k in sorted(set(req) | set(entrada))
                                       if k in props}
                reg.update(conferir(props, req, entrada))
            except Exception as e:
                reg['STATE'] = CONTRACT_NOT_READABLE
                reg['ERROR'] = ap.redigir(str(e))[:180]
            linhas.append(reg)
        out['STATE'] = 'PROBED'
        out['ACTORS'] = linhas
        # Intencao VAZIA satisfaz qualquer contrato sem campo obrigatorio — e esse
        # MATCH nao autoriza nada: nao pedir nada nao e pedir certo. So entra aqui
        # quem declarou uma entrada e ela passou.
        out['READY_TO_SPEND'] = sorted(r['ACTOR'] for r in linhas
                                       if r.get('STATE') == CONTRACT_MATCH
                                       and r.get('INTENDED_INPUT'))
        out['CONTRACT_READ_BUT_NO_INPUT_DECLARED'] = sorted(
            r['ACTOR'] for r in linhas if not r.get('INTENDED_INPUT'))
    os.makedirs(os.path.dirname(DEST), exist_ok=True)
    with open(DEST, 'w', encoding='utf-8') as fh:
        fh.write(ap.redigir(json.dumps(out, ensure_ascii=False, indent=2)))
    print('STATE =', out['STATE'])
    for r in out.get('ACTORS', []):
        print('  %-46s %s' % (r['ACTOR'][:46], r.get('STATE')))
        print('     campos do contrato:', ', '.join(r.get('CONTRACT_FIELDS', []))
              or 'NÃO SEI')
        print('     obrigatorios      :', ', '.join(r.get('REQUIRED', [])) or 'nenhum')
        for campo, d in sorted((r.get('FIELD_DETAIL') or {}).items()):
            print('       %-22s %s' % (campo[:22], json.dumps(d, ensure_ascii=False)[:170]))
        if r.get('UNKNOWN_FIELDS'):
            print('     NAO EXISTEM       :', ', '.join(r['UNKNOWN_FIELDS']))
        if r.get('ERROR'):
            print('     erro              :', r['ERROR'])
    print('->', os.path.relpath(DEST, ROOT))


if __name__ == '__main__':
    main()
