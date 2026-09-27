"""COMENTARIOS-BATERIA — mutacao POR REGRA do COMENTARIOS-V1, alem das 14 de `provas/comentarios_v1/mutar.py`.
Cinco regras, varios defeitos em cada: PUBLIC_ASSERTION · LUGAR_DO_PAI · SEM_LUGAR_DO_COMENTARISTA · ELEGIBILIDADE ·
CONTROLE (+ SEM_ROTA_PAGA, D106-3). Um defeito de cada vez; corre os mesmos testes da V1 com rede fechada e sem .pyc; o mutante so conta como
MORTO se fizer aparecer falha NOVA (pelo nome) alem das herdadas da propria arvore. Repoe pelos BYTES e confere sha256.
uso: python3 provas/comentarios_bateria/mutar_regras.py [saida.json]"""
import glob
import hashlib
import json
import os
import subprocess
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SAIDA = sys.argv[1] if len(sys.argv) > 1 else os.path.join(RAIZ, 'provas', 'comentarios_bateria', 'MUTACAO-REGRAS.json')
TESTES = ['tests.test_comentarios_v1', 'tests.test_d24_video_de_pessoa', 'tests.test_c13_route_gate',
          'tests.test_linkedin_build_01_local_first']
F_ENV, F_EL, F_LI = 'coleta/social_envelope.py', 'pedido/elegibilidade_comentario.py', 'coleta/adaptador_linkedin.py'

SPEAKER = "        o['SPEAKER_LANGUAGE_LOCATION'] = lugar or env.DESCONHECIDO\n"
MUTANTES = [
    # ── PUBLIC_ASSERTION: o comentario nasce asserção, nunca facto ──
    ('PUBLIC_ASSERTION', 'N01 evidencia vira problema confirmado', F_ENV,
     "EVIDENCE_CLASS_DO_COMENTARIO = 'FIELD_VOICE_OBSERVED'",
     "EVIDENCE_CLASS_DO_COMENTARIO = 'FIELD_PROBLEM_CONFIRMED'"),
    ('PUBLIC_ASSERTION', 'N02 origem vira verificada', F_ENV,
     "ORIGIN_STATUS_DO_COMENTARIO = 'UNVERIFIED'", "ORIGIN_STATUS_DO_COMENTARIO = 'VERIFIED'"),
    ('PUBLIC_ASSERTION', 'N03 comentario do LinkedIn nasce POST (sem assercao)', F_LI,
     "url=url, content_type='COMMENT',", "url=url, content_type='POST',"),
    # ── LUGAR DO PAI: FACT_LOCATION so herdado do material pai, e so quando provado ──
    ('LUGAR_DO_PAI', 'N04 lugar provado do pai deixa de ser herdado', F_ENV,
     "        'FACT_LOCATION': parent_fact_location if tem_lugar else DESCONHECIDO,",
     "        'FACT_LOCATION': DESCONHECIDO,"),
    ('LUGAR_DO_PAI', 'N05 lugar sem prova passa como herdado', F_ENV,
     "    tem_lugar = parent_fact_location not in (None, '', DESCONHECIDO, 'NOT_KNOWN', 'NAO SEI')",
     "    tem_lugar = True"),
    ('LUGAR_DO_PAI', 'N06 envelope perde o lugar do pai no caminho', F_ENV,
     "parent_content_id=parent_content_id, parent_fact_location=parent_fact_location,",
     "parent_content_id=parent_content_id, parent_fact_location=None,"),
    ('LUGAR_DO_PAI', 'N07 LinkedIn nomeia o pai pelo url e nao pela activity', F_LI,
     "parent_content_id='LINKEDIN:%s' % activity,", "parent_content_id='LINKEDIN:%s' % url,"),
    # ── SEM LUGAR DO COMENTARISTA: quem fala nao ganha o lugar do post, e o lugar dele nao se coleta ──
    ('SEM_LUGAR_DO_COMENTARISTA', 'N08 localizacao do autor passa a coletar-se', F_ENV,
     "LUGAR_DO_AUTOR_DO_COMENTARIO = 'NAO_SE_COLETA'", "LUGAR_DO_AUTOR_DO_COMENTARIO = DESCONHECIDO"),
    ('SEM_LUGAR_DO_COMENTARISTA', 'N09 REGION_IF_PROVEN herda o lugar do pai', F_EL,
     "        o['REGION_IF_PROVEN'] = lugar or env.DESCONHECIDO",
     "        o['REGION_IF_PROVEN'] = lugar or pai.get('FACT_LOCATION') or env.DESCONHECIDO"),
    ('SEM_LUGAR_DO_COMENTARISTA', 'N10 EXPLICIT sem a fala dizer o lugar', F_EL,
     "        o['REGIONAL_LANGUAGE_EVIDENCE'] = 'EXPLICIT' if lugar else env.DESCONHECIDO",
     "        o['REGIONAL_LANGUAGE_EVIDENCE'] = 'EXPLICIT'"),
    ('SEM_LUGAR_DO_COMENTARISTA', 'N11 lugar dito na fala vira FACT_LOCATION', F_EL,
     SPEAKER, SPEAKER + "        o['FACT_LOCATION'] = lugar or o.get('FACT_LOCATION')\n"),
    # ── ELEGIBILIDADE DO PAI: HIGH/MEDIUM/LOW/NO (+ NAO_SEI); so HIGH/MEDIUM colhem ──
    ('ELEGIBILIDADE', 'N12 HIGH sem fonte registada', F_EL,
     "    elif fonte_registada and (universo_sim or fortes) and ents:",
     "    elif (universo_sim or fortes) and ents:"),
    ('ELEGIBILIDADE', 'N13 LOW passa a colher', F_EL,
     "'VAI_COLHER': nivel in (HIGH, MEDIUM) and not zero", "'VAI_COLHER': nivel in (HIGH, MEDIUM, LOW) and not zero"),
    ('ELEGIBILIDADE', 'N14 NAO_SEI passa a colher', F_EL,
     "'VAI_COLHER': nivel in (HIGH, MEDIUM) and not zero",
     "'VAI_COLHER': nivel in (HIGH, MEDIUM, NAO_SEI) and not zero"),
    ('ELEGIBILIDADE', 'N15 so indicio sobe a MEDIUM', F_EL,
     "        nivel, porque = LOW, 'so indicio", "        nivel, porque = MEDIUM, 'so indicio"),
    ('ELEGIBILIDADE', 'N16 universo NAO deixa de ser NO', F_EL,
     "        nivel, porque = NO, 'a regua do universo", "        nivel, porque = NAO_SEI, 'a regua do universo"),
    ('ELEGIBILIDADE', 'N17 comentarios desligados deixam de ser NO', F_EL,
     "        nivel, porque = NO, 'o dono do material desligou", "        nivel, porque = MEDIUM, 'o dono do material desligou"),
    ('ELEGIBILIDADE', 'N18 MEDIUM sem entidade nomeada', F_EL,
     "    elif ents and (universo_sim or fortes or indicios or uv == adm.NAO_SEI):",
     "    elif (universo_sim or fortes or indicios):"),
    # ── CONTROLE: fatia crua por hash estavel do id, sem olhar o texto, sem corte ──
    ('CONTROLE', 'N19 controlo passa a olhar o texto', F_EL,
     "_estavel(o.get('NATIVE_ID')) % FRACAO_CONTROLE == 0]", "_estavel(o.get('TEXT')) % FRACAO_CONTROLE == 0]"),
    ('CONTROLE', 'N20 controlo so entre os relevantes', F_EL,
     "        'CONTROLE': [o for o in comentarios if _estavel",
     "        'CONTROLE': [o for o in comentarios if o['CANONICAL_ENTITIES'] and _estavel"),
    ('CONTROLE', 'N21 controlo cortado a um', F_EL,
     "_estavel(o.get('NATIVE_ID')) % FRACAO_CONTROLE == 0]", "_estavel(o.get('NATIVE_ID')) % FRACAO_CONTROLE == 0][:1]"),
    ('CONTROLE', 'N22 controlo tirado dos mais curtidos', F_EL,
     "        'CONTROLE': [o for o in comentarios if _estavel",
     "        'CONTROLE': [o for o in sorted(comentarios, key=gostos, reverse=True)[:n] if _estavel"),
    # ── D106-3: sem rota paga. A falha NOVA que a bateria achou (test_linkedin_build_01 test_21/test_M12) ──
    ('SEM_ROTA_PAGA', 'N23 comentario do LinkedIn volta a pedir rota paga', F_LI,
     "    'COMMENTS_TEXT': {'NIVEL': FREE, 'MATRIZ': 'FETCH_COMMENTS',",
     "    'COMMENTS_TEXT': {'NIVEL': PAID, 'MATRIZ': 'FETCH_COMMENTS',"),
]

ENV = dict(os.environ, PYTHONDONTWRITEBYTECODE='1',
           HTTP_PROXY='http://127.0.0.1:9', HTTPS_PROXY='http://127.0.0.1:9', http_proxy='http://127.0.0.1:9',
           https_proxy='http://127.0.0.1:9', ALL_PROXY='http://127.0.0.1:9', NO_PROXY='127.0.0.1,localhost',
           no_proxy='127.0.0.1,localhost')


def sem_pyc():
    for f in glob.glob(os.path.join(RAIZ, '**', '__pycache__', '*.pyc'), recursive=True):
        if any(x in f for x in ('social_envelope', 'elegibilidade_comentario', 'adaptador_linkedin')):
            os.remove(f)


def correr():
    sem_pyc()
    r = subprocess.run([sys.executable, '-m', 'unittest'] + TESTES, cwd=RAIZ, env=ENV, capture_output=True,
                       text=True, encoding='utf-8', errors='replace', timeout=900)
    return sorted(set(l.split(' (')[0].split(': ', 1)[1] for l in r.stderr.splitlines()
                      if l.startswith(('FAIL: ', 'ERROR: '))))


originais = {}
for _, _, f, _, _ in MUTANTES:
    if f not in originais:
        with open(os.path.join(RAIZ, f), 'rb') as fh:
            originais[f] = fh.read()
sha0 = {f: hashlib.sha256(b).hexdigest() for f, b in originais.items()}
HERDADAS = set(correr())
res = {'TESTES': TESTES, 'SHA256_ANTES': sha0, 'FALHAS_HERDADAS_ANTES': sorted(HERDADAS), 'MUTANTES': []}
try:
    for regra, nome, f, velho, novo in MUTANTES:
        texto = originais[f].decode('utf-8')
        if texto.count(velho) == 0 and '\n' in velho and '\r\n' in texto:
            velho, novo = velho.replace('\n', '\r\n'), novo.replace('\n', '\r\n')
        n = texto.count(velho)
        if n != 1:
            res['MUTANTES'].append({'REGRA': regra, 'MUTANTE': nome, 'ESTADO': 'NAO_APLICADO', 'OCORRENCIAS': n})
            print('%-55s NAO_APLICADO (%d)' % (nome, n), flush=True)
            continue
        with open(os.path.join(RAIZ, f), 'wb') as fh:
            fh.write(texto.replace(velho, novo).encode('utf-8'))
        try:
            falhas = correr()
        finally:
            with open(os.path.join(RAIZ, f), 'wb') as fh:
                fh.write(originais[f])
        novas = sorted(set(falhas) - HERDADAS)
        res['MUTANTES'].append({'REGRA': regra, 'MUTANTE': nome, 'FICHEIRO': f,
                                'ESTADO': 'MORTO' if novas else 'SOBREVIVEU', 'TESTES_QUE_APANHARAM': novas})
        print('%-55s %s %s' % (nome, 'MORTO' if novas else 'SOBREVIVEU', novas[:2]), flush=True)
finally:
    for f, b in originais.items():
        with open(os.path.join(RAIZ, f), 'wb') as fh:
            fh.write(b)
    sem_pyc()
res['SHA256_DEPOIS'] = {f: hashlib.sha256(open(os.path.join(RAIZ, f), 'rb').read()).hexdigest() for f in originais}
res['REPOSTO_IGUAL'] = res['SHA256_DEPOIS'] == sha0
por_regra = {}
for m in res['MUTANTES']:
    t = por_regra.setdefault(m['REGRA'], [0, 0])
    t[0] += m['ESTADO'] == 'MORTO'
    t[1] += 1
res['PLACAR_POR_REGRA'] = {k: '%d/%d mortos' % tuple(v) for k, v in por_regra.items()}
res['PLACAR'] = '%d/%d mortos' % (sum(m['ESTADO'] == 'MORTO' for m in res['MUTANTES']), len(MUTANTES))
with open(SAIDA, 'w', encoding='utf-8', newline='\n') as fh:
    json.dump(res, fh, ensure_ascii=False, indent=1)
    fh.write('\n')
print(res['PLACAR'], res['PLACAR_POR_REGRA'], 'reposto igual:', res['REPOSTO_IGUAL'])
