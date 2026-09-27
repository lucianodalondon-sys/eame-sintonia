"""COMENTARIOS-V1 — prova de mutacao. Um defeito de cada vez; corre tests.test_comentarios_v1 (e os
dois testes antigos que esta missao ajustou) com rede fechada e sem .pyc; exige que reprove. Repoe cada
ficheiro pelos BYTES guardados (nunca `git checkout`) e confere o sha256 no fim.
uso: py provas/comentarios_v1/mutar.py [saida.json]"""
import glob
import hashlib
import json
import os
import subprocess
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SAIDA = sys.argv[1] if len(sys.argv) > 1 else os.path.join(RAIZ, 'provas', 'comentarios_v1', 'MUTACAO.json')
TESTES = ['tests.test_comentarios_v1', 'tests.test_d24_video_de_pessoa', 'tests.test_c13_route_gate']
F_ENV, F_YT, F_EL = 'coleta/social_envelope.py', 'coleta/youtube_oficial.py', 'pedido/elegibilidade_comentario.py'
F_LI, F_IG, F_MZ, F_WF = ('coleta/adaptador_linkedin.py', 'coleta/instagram_pessoal.py', 'leis/social_matriz.py',
                          '.github/workflows/sintonia-scrap.yml')

MUTANTES = [
    ('M01 comentario vira FACT', F_ENV,
     "CLAIM_KIND_DO_COMENTARIO = 'PUBLIC_ASSERTION'", "CLAIM_KIND_DO_COMENTARIO = 'FACT'"),
    ('M02 comentario sem pai passa', F_ENV,
     "    if not pai or pai.upper() == DESCONHECIDO:\n        raise ValueError(",
     "    if False:\n        raise ValueError("),
    ('M03 COMMENT deixa de ganhar a assercao', F_ENV,
     "    if content_type == 'COMMENT':\n        fora.update(assercao_do_comentario(",
     "    if content_type == 'NUNCA':\n        fora.update(assercao_do_comentario("),
    ('M04 YouTube deixa de nomear o pai', F_YT,
     "        parent_content_id='YOUTUBE:%s' % video_id,", "        parent_content_id='UNKNOWN',"),
    ('M05 lugar do pai vira o de quem fala (IAB §5)', F_EL,
     "        o['SPEAKER_LANGUAGE_LOCATION'] = lugar or env.DESCONHECIDO",
     "        o['SPEAKER_LANGUAGE_LOCATION'] = lugar or pai.get('FACT_LOCATION') or env.DESCONHECIDO"),
    ('M06 controlo deixa de existir', F_EL,
     "        'CONTROLE': [o for o in comentarios if _estavel(o.get('NATIVE_ID')) % FRACAO_CONTROLE == 0],",
     "        'CONTROLE': [],"),
    ('M07 amostra apaga o que fica fora', F_EL,
     "    return {'COMENTARIOS': len(comentarios),",
     "    objetos[:] = [o for o in objetos if o.get('SAMPLE_BUCKETS')]\n    return {'COMENTARIOS': len(comentarios),"),
    ('M08 lacuna de vocabulario volta a ser NO', F_EL,
     "        nivel, porque = NAO_SEI, ('LACUNA_DE_VOCABULARIO:", "        nivel, porque = NO, ('LACUNA_DE_VOCABULARIO:"),
    ('M09 zero declarado passa a colher', F_EL,
     "        'VAI_COLHER': nivel in (HIGH, MEDIUM) and not zero and not comentarios_desligados,",
     "        'VAI_COLHER': nivel in (HIGH, MEDIUM) and not comentarios_desligados,"),
    ('M10 leitor do LinkedIn guarda o nome do autor', F_LI,
     "                     'AUTHOR_NAME': 'REDACTED_BY_POLICY',",
     "                     'AUTHOR_NAME': (autor.get('name') if isinstance(autor, dict) else autor),"),
    ('M11 listagem de comentarios deixa de ser recusada', F_LI,
     "    if _LISTAGEM_DE_COMENTARIOS.search(alvo):\n        raise ValueError(",
     "    if False:\n        raise ValueError("),
    ('M12 Instagram abre o gasto por omissao', F_IG,
     "    if v in ('1', 'sim', 'yes', 'true'):\n        return True, ('OK de GASTO",
     "    if True:\n        return True, ('OK de GASTO"),
    ('M13 LinkedIn declarado PROVED sem prova', F_MZ,
     "            r('linkedin:post-publico:jsonld-comment', 'DIRECT_HTTP', 'SIM',\n              'POSSIBLE_NOT_PROVED', 'zero',",
     "            r('linkedin:post-publico:jsonld-comment', 'DIRECT_HTTP', 'SIM',\n              'PROVED', 'zero',"),
    ('M14 apelido T7 some do workflow', F_WF,
     "              IT-T7-*) echo 'colete agronomos' ;;\n", ""),
]

ENV = dict(os.environ, PYTHONDONTWRITEBYTECODE='1',
           HTTP_PROXY='http://127.0.0.1:9', HTTPS_PROXY='http://127.0.0.1:9', http_proxy='http://127.0.0.1:9',
           https_proxy='http://127.0.0.1:9', ALL_PROXY='http://127.0.0.1:9', NO_PROXY='127.0.0.1,localhost',
           no_proxy='127.0.0.1,localhost')


def sem_pyc():
    for f in glob.glob(os.path.join(RAIZ, '**', '__pycache__', '*.pyc'), recursive=True):
        if any(x in f for x in ('social_envelope', 'youtube_oficial', 'elegibilidade_comentario',
                                'adaptador_linkedin', 'instagram_pessoal', 'social_matriz')):
            os.remove(f)


def correr():
    sem_pyc()
    r = subprocess.run([sys.executable, '-m', 'unittest'] + TESTES, cwd=RAIZ, env=ENV, capture_output=True,
                       text=True, encoding='utf-8', errors='replace', timeout=900)
    falhas = sorted(set(l.split(' (')[0].split(': ', 1)[1] for l in r.stderr.splitlines()
                        if l.startswith(('FAIL: ', 'ERROR: '))))
    return r.returncode, falhas


originais = {}
for _, f, _, _ in MUTANTES:
    if f not in originais:
        with open(os.path.join(RAIZ, f), 'rb') as fh:
            originais[f] = fh.read()
sha0 = {f: hashlib.sha256(b).hexdigest() for f, b in originais.items()}
rc0, f0 = correr()
# HERDADAS: `test_c13_route_gate` ja falha na base 2ef6fef8 (YOUTUBE/INCREMENTAL, 2 testes), igual.
# Um mutante so conta como MORTO se fizer aparecer falha NOVA alem destas.
HERDADAS = set(f0)
res = {'TESTES': TESTES, 'SHA256_ANTES': sha0, 'FALHAS_HERDADAS_ANTES': sorted(HERDADAS), 'MUTANTES': []}
try:
    for nome, f, velho, novo in MUTANTES:
        texto = originais[f].decode('utf-8')
        n = texto.count(velho)
        if n != 1:
            res['MUTANTES'].append({'MUTANTE': nome, 'ESTADO': 'NAO_APLICADO', 'OCORRENCIAS': n})
            print('%-50s NAO_APLICADO (%d)' % (nome, n))
            continue
        with open(os.path.join(RAIZ, f), 'wb') as fh:
            fh.write(texto.replace(velho, novo).encode('utf-8'))
        rc, falhas = correr()
        with open(os.path.join(RAIZ, f), 'wb') as fh:
            fh.write(originais[f])
        novas = sorted(set(falhas) - HERDADAS)
        res['MUTANTES'].append({'MUTANTE': nome, 'FICHEIRO': f, 'ESTADO': 'MORTO' if novas else 'SOBREVIVEU',
                                'TESTES_QUE_APANHARAM': novas})
        print('%-50s %s %s' % (nome, 'MORTO' if novas else 'SOBREVIVEU', novas[:2]), flush=True)
finally:
    for f, b in originais.items():
        with open(os.path.join(RAIZ, f), 'wb') as fh:
            fh.write(b)
    sem_pyc()
res['SHA256_DEPOIS'] = {f: hashlib.sha256(open(os.path.join(RAIZ, f), 'rb').read()).hexdigest() for f in originais}
res['REPOSTO_IGUAL'] = res['SHA256_DEPOIS'] == sha0
res['PLACAR'] = '%d/%d mortos' % (sum(m['ESTADO'] == 'MORTO' for m in res['MUTANTES']), len(MUTANTES))
with open(SAIDA, 'w', encoding='utf-8', newline='\n') as fh:
    json.dump(res, fh, ensure_ascii=False, indent=1)
    fh.write('\n')
print(res['PLACAR'], 'reposto igual:', res['REPOSTO_IGUAL'])
