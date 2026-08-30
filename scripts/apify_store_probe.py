#!/usr/bin/env python3
"""
Que Actor de LinkedIn existe, e QUE ENTRADA ele espera. Consulta gratuita.

Existe por causa do achado mais caro desta rodada: oito execuções pagas
devolveram, todas, o MESMO perfil de um consultor de cibersegurança — alguém sem
nenhuma relação com os oito alvos italianos.

O Actor não falhou. Ele teve sucesso: `SUCCEEDED`, um item completo, perfil de
LinkedIn real e bem formado. Só que a entrada que eu mandei (`searchQuery`) não é
a que ele lê. Um Actor de *profile detail* espera a URL ou o identificador de UM
perfil; dando-lhe uma consulta de busca, ele ignorou o campo e devolveu um perfil
padrão. Oito vezes o mesmo.

    ACTOR_SUCCESS ≠ USEFUL_DATA
    WRONG_INPUT_CONTRACT ≠ WRONG_PLATFORM

A resposta certa não é insistir no mesmo Actor com outros parâmetros. É olhar o
catálogo ANTES: `GET /v2/store` é **gratuito** e diz nome, título e descrição de
cada Actor. Escolher às cegas foi o defeito que custou os oito runs — e custou
barato só porque cada run custa meio centavo.
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

DEST = os.path.join(ROOT, 'data', 'samples', 'IT-CASOS', 'IT-APIFY-STORE-PROBE.json')
TERMOS = ('linkedin profile', 'linkedin search', 'linkedin posts')


def _get(url, token):
    r = subprocess.run(['curl', '-sS', '-G', '-H',
                        'Authorization: Bearer %s' % token, url],
                       capture_output=True, text=True, timeout=120)
    if r.returncode != 0:
        raise RuntimeError(ap.redigir(r.stderr[:200]))
    return json.loads(r.stdout)


def main():
    ks = ap.pool()
    out = {'SOURCE_ID': 'DERIVED/IT-APIFY-STORE-PROBE',
           'source': 'catalogo publico de Actors da Apify — consulta gratuita',
           'SOURCE_LOCATION': 'Apify', 'FACT_LOCATION': 'n/a — metadado de coleta',
           'ORIGINAL_LANGUAGE': 'pt', 'EVIDENCE_CLASS': 'PRIMARY_SOURCE_PROBE',
           'captured_at': datetime.date.today().isoformat(),
           'CAPTURED_AT': datetime.date.today().isoformat(),
           'NEW_ACTOR_RUNS': 0, 'COST': 0,
           'WHY': ('oito runs pagos devolveram o MESMO perfil de um consultor de '
                   'ciberseguranca — o Actor ignorou searchQuery. Escolher Actor as '
                   'cegas foi o defeito; o catalogo e gratuito.'),
           'LAWS': ['ACTOR_SUCCESS ≠ USEFUL_DATA',
                    'WRONG_INPUT_CONTRACT ≠ WRONG_PLATFORM']}
    if not ks:
        out['STATE'] = 'APIFY_ENV_MISSING'
    else:
        achados = {}
        for termo in TERMOS:
            try:
                d = _get('https://api.apify.com/v2/store?search=%s&limit=12'
                         % termo.replace(' ', '%20'), ks[0])
            except Exception as e:
                out.setdefault('ERRORS', []).append(ap.redigir(str(e))[:150])
                continue
            for a in (d.get('data', {}).get('items') or []):
                nome = '%s/%s' % (a.get('username'), a.get('name'))
                if nome in achados:
                    continue
                achados[nome] = {
                    'ACTOR': nome, 'TITLE': a.get('title'),
                    'DESCRIPTION': (a.get('description') or '')[:200],
                    'TOTAL_USERS': a.get('stats', {}).get('totalUsers'),
                    'PRICING_MODEL': (a.get('currentPricingInfo') or {}).get('pricingModel'),
                    'FOUND_BY': termo}
        out['STATE'] = 'PROBED'
        out['ACTORS_FOUND'] = len(achados)
        out['ACTORS'] = sorted(achados.values(),
                               key=lambda x: -(x.get('TOTAL_USERS') or 0))
    os.makedirs(os.path.dirname(DEST), exist_ok=True)
    with open(DEST, 'w', encoding='utf-8') as fh:
        fh.write(ap.redigir(json.dumps(out, ensure_ascii=False, indent=2)))
    print('STATE =', out['STATE'], '| actors =', out.get('ACTORS_FOUND', 0))
    for a in (out.get('ACTORS') or [])[:14]:
        print('  %-44s users=%-7s %s' % (a['ACTOR'][:44], a['TOTAL_USERS'],
                                         (a['TITLE'] or '')[:50]))
    print('->', os.path.relpath(DEST, ROOT))


if __name__ == '__main__':
    main()
