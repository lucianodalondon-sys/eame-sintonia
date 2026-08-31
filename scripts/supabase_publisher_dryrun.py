"""Publisher em DRY RUN: valida, transforma, planeja o upsert — e nao grava.

Le os blobs pelos commits FIXOS, mede o que da para medir, deriva as chaves
naturais e confere idempotencia rodando duas vezes. Nenhum INSERT, nenhum UPDATE,
nenhuma conexao: nao existe instancia.

Onde a contagem nao pode ser afirmada, sai NOT_MEASURED. Onde o artefato nao pode
ser identificado com certeza, sai NOT_RESOLVED com os candidatos — escolher por
semelhanca de nome seria inventar proveniencia.

Uso:
    py scripts/supabase_publisher_dryrun.py            # imprime
    py scripts/supabase_publisher_dryrun.py --sync     # grava o artefato
"""
import hashlib
import json
import os
import subprocess
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MAPA = os.path.join(RAIZ, 'data', 'supabase', 'SUPABASE-PUBLISH-MAP.json')
SAIDA = os.path.join(RAIZ, 'data', 'supabase', 'SUPABASE-PUBLISHER-DRYRUN.json')

# Caminhos resolvidos por LEITURA do commit fixo, nao por semelhanca de nome.
# Cada entrada diz qual lista foi contada, para o numero ter denominador.
RESOLVIDOS = {
    'H1': [('data/samples/TERRITORIAL/FINAL.json', 'ITEMS')],
    'H2': [('data/samples/IT-T4-001/IT-T4-001-adama-expiries.json', None)],
    'H3': None,   # nao resolvido — ver CANDIDATOS
    'H4': [('data/samples/META-EAME/META-ADS-EVENTS-EAME-V1.json', 'events')],
    'H5': [('data/samples/ES-T3-001-repilo-serie-historica.json', None),
           ('data/samples/RAIF-COORTE-REPILO.json', None),
           ('data/samples/BACKTEST-REPILO-LEAD-TIME.json', None)],
    'H6': [('data/samples/CREATOR-MAP-EAME/CREATORS-ES-IT-FR.json', 'CREATORS'),
           ('data/samples/CREATOR-CONTENT-CORPUS-EAME/CORPUS-UNIVERSE.json', 'ENTITIES'),
           ('data/samples/CREATOR-CONTENT-CORPUS-EAME/CORPUS-OBSERVATIONS.json', 'MATERIALS')],
    'H7': [('data/samples/ES-RESEARCHERS-OLIVE.json', 'RESEARCHERS'),
           ('data/samples/ES-T5-002-corpus-documentos.json', 'DOCUMENTS')],
    'H8': [('data/samples/COMPETITOR-PUBLIC-COMM/CONTAS-V1.json', 'ACCOUNTS')],
    'H9': [('data/samples/X-007-canonical-agro-dictionary.json', 'records'),
           ('data/samples/X-006-eu-cas-to-ephy.json', 'matches')],
}
CANDIDATOS = {
    'H3': {
        'WHY': ('o mapa descreve "cadeia de identidade competitiva — 36 tuplas" e nenhum '
                'artefato do commit fixo tem 36 de nada: COMPETITOR-CROSSWALK tem 242 pares, '
                'PILOT-AMOSTRA tem 6. Escolher por semelhanca de nome seria inventar '
                'proveniencia.'),
        'PATHS': ['data/samples/COMPETITOR-CROSSWALK.json',
                  'data/samples/COMPETITOR-EAME-PARIDADE.json',
                  'data/samples/COMPETITOR-PILOT-AMOSTRA.json',
                  'data/samples/COMPETITOR-IP-TMVIEW.json'],
    },
}


def blob(sha, path):
    r = subprocess.run(['git', 'cat-file', '-p', '%s:%s' % (sha, path)],
                       cwd=RAIZ, capture_output=True)
    return r.stdout if r.returncode == 0 else None


def chave_natural(familia, partes):
    """Chave estavel e deterministica. NUNCA deriva de titulo traduzido."""
    base = '|'.join(str(p) for p in partes)
    return '%s:%s' % (familia, hashlib.sha256(base.encode('utf-8')).hexdigest()[:16])


def processar(hose, commits, mapa_entrada):
    """VALIDATE -> TRANSFORM -> UPSERT PLAN, sem gravar."""
    resolvidos = RESOLVIDOS.get(hose)
    if resolvidos is None:
        return {'HOSE_ID': hose, 'STATUS': 'NOT_RESOLVED',
                'CANDIDATOS': CANDIDATOS[hose]}

    shas = [commits] if isinstance(commits, str) else list(commits)
    artefatos, chaves = [], []
    for path, lista in resolvidos:
        achado = None
        for sha in shas:
            b = blob(sha, path)
            if b is not None:
                achado = (sha, b)
                break
        if achado is None:
            artefatos.append({'PATH': path, 'STATUS': 'BLOB_AUSENTE_NOS_COMMITS'})
            continue
        sha, b = achado
        try:
            d = json.loads(b.decode('utf-8'))
        except Exception:
            d = None
        contagem = 'NOT_MEASURED'
        if isinstance(d, dict) and lista and isinstance(d.get(lista), list):
            contagem = len(d[lista])
        artefatos.append({
            'PATH': path, 'STATUS': 'OK', 'COMMIT': sha,
            'BYTES': len(b),
            'CONTENT_SHA256': hashlib.sha256(b).hexdigest(),
            'COUNTED_LIST': lista, 'MEASURED_COUNT': contagem,
        })
        # chaves naturais derivadas do conteudo congelado
        if isinstance(contagem, int):
            for i in range(contagem):
                chaves.append(chave_natural(hose, (sha, path, lista, i)))

    declarado = mapa_entrada.get('EXPECTED_ENTITY_COUNT', {})
    medido = {a['PATH'].split('/')[-1]: a.get('MEASURED_COUNT')
              for a in artefatos if a['STATUS'] == 'OK'}
    return {
        'HOSE_ID': hose, 'STATUS': 'PLANNED',
        'ARTEFATOS': artefatos,
        'UPSERT_KEYS': len(chaves),
        'UPSERT_KEYS_DISTINTAS': len(set(chaves)),
        'DESTINATION_TABLES': mapa_entrada.get('DESTINATION_TABLES', []),
        'GUARDS_A_APLICAR': mapa_entrada.get('GUARDS', []),
        'EXPECTED_DECLARADO': declarado,
        'MEASURED_AGORA': medido,
    }


def medir():
    with open(MAPA, encoding='utf-8') as fh:
        mapa = json.load(fh)

    passo1 = [processar(i['HOSE_ID'], i['SOURCE_COMMIT'], i) for i in mapa['INPUTS']]
    passo2 = [processar(i['HOSE_ID'], i['SOURCE_COMMIT'], i) for i in mapa['INPUTS']]

    k1 = [p.get('UPSERT_KEYS', 0) for p in passo1]
    k2 = [p.get('UPSERT_KEYS', 0) for p in passo2]
    identico = json.dumps(passo1, sort_keys=True) == json.dumps(passo2, sort_keys=True)

    resolvidas = [p for p in passo1 if p['STATUS'] == 'PLANNED']
    nao_resolvidas = [p['HOSE_ID'] for p in passo1 if p['STATUS'] == 'NOT_RESOLVED']
    sem_duplicata = all(p['UPSERT_KEYS'] == p['UPSERT_KEYS_DISTINTAS'] for p in resolvidas)

    # divergencias entre o que o mapa declara e o que o blob mede
    # Zero declarado NAO e contagem de lista: e resultado de guard — "nenhuma pessoa
    # com expertise provada", "nenhuma traducao". Cobrar que um zero apareca como
    # tamanho de lista seria confundir resultado com fonte.
    divergencias = []
    for p in resolvidas:
        for k, v in p['EXPECTED_DECLARADO'].items():
            if not isinstance(v, int) or v == 0:
                continue
            if v not in [m for m in p['MEASURED_AGORA'].values() if isinstance(m, int)]:
                divergencias.append({
                    'HOSE_ID': p['HOSE_ID'], 'DECLARADO': {k: v},
                    'MEDIDO': p['MEASURED_AGORA'],
                    'ACAO': 'o numero declarado nao aparece em nenhuma lista medida do '
                            'blob congelado; vira NOT_MEASURED ate alguem apontar a lista'})

    return {
        'SOURCE_ID': 'SUPABASE-PUBLISHER-DRYRUN-EAME-2026-08-31',
        'source': 'Publisher em dry run sobre os commits fixos. Nada gravado.',
        'MODE': {'DRY_RUN': 'YES', 'COMMIT': 'NO', 'DB_CONNECTION': 'NONE',
                 'REAL_DATA_PUBLISHED': 'NO'},
        'INPUTS_TOTAL': len(passo1),
        'INPUTS_PLANNED': len(resolvidas),
        'INPUTS_NOT_RESOLVED': nao_resolvidas,
        'PLANO': passo1,
        'IDEMPOTENCIA': {
            'DUAS_PASSAGENS_IDENTICAS': identico,
            'CHAVES_PASSAGEM_1': sum(k1),
            'CHAVES_PASSAGEM_2': sum(k2),
            'NOVAS_ENTIDADES_NA_SEGUNDA': sum(k2) - sum(k1) if identico else 'INDETERMINADO',
            'SEM_CHAVE_DUPLICADA': sem_duplicata,
            'CHAVE_NAO_USA_TITULO': True,
            'COMO': ('a chave deriva de (commit, caminho, lista, indice) — tudo imutavel. '
                     'Titulo traduzido nunca entra: ele muda por idioma e por revisao.'),
        },
        'DIVERGENCIAS_DECLARADO_x_MEDIDO': divergencias,
    }


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    m = medir()
    if '--sync' in sys.argv:
        with open(SAIDA, 'w', encoding='utf-8', newline='\n') as fh:
            json.dump(m, fh, ensure_ascii=False, indent=2)
            fh.write('\n')
        print('gravado em', os.path.relpath(SAIDA, RAIZ))
    resumo = {k: v for k, v in m.items() if k != 'PLANO'}
    print(json.dumps(resumo, ensure_ascii=False, indent=2))
