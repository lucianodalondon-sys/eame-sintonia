"""VOCI-DAL-CAMPO — prova de mutacao. Planta UM defeito de cada vez em motor/voce_dal_campo.py, corre
tests.test_voce_dal_campo (rede fechada, sem .pyc) e exige que reprove. Repoe o ficheiro pelos BYTES guardados
em memoria (nunca `git checkout`), e no fim confere que o ficheiro e igual ao do inicio (sha256).
uso: py provas/voci_dal_campo/mutar.py [saida.json]"""
import glob
import hashlib
import json
import os
import subprocess
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ALVO = os.path.join(RAIZ, 'motor', 'voce_dal_campo.py')
SAIDA = sys.argv[1] if len(sys.argv) > 1 else os.path.join(RAIZ, 'provas', 'voci_dal_campo', 'MUTACAO.json')

MUTANTES = [
    ('M01 data de publicacao aceite como tempo do facto',
     "continue          # PUBLICATION_STAMP_NOT_FACT_TIME", "pass"),
    ('M02 lugar da pessoa copiado para o lugar do facto',
     "        voz.update(lugar)\n",
     "        voz.update(lugar)\n        if voz['FACT_LOCATION'] == NAO_SEI and voz['SPEAKER_PLACE'] != NAO_SEI:\n"
     "            voz['FACT_LOCATION'] = voz['SPEAKER_PLACE']\n"),
    ('M03 apresentado por outro passa a ser quem fala',
     "autos = [a for a in aps if a['ESPECIE'] == AUTO]", "autos = list(aps)"),
    ('M04 troca de voz «>>» ignorada',
     "if '>>' in texto[a['FRASE'][1]:(pos if fim is None else fim)]:", "if False:"),
    ('M05 T8 para qualquer papel',
     "'T8' if f['ROLE'] == AGRICULTOR else 'NAO_T8'", "'T8' if f['ROLE'] != NAO_SEI else 'NAO_T8'"),
    ('M06 sinal de criador apaga o papel profissional',
     "        if f['ROLES_DECLARED']:\n", "        if f['ROLES_DECLARED'] and not criador:\n"),
    ('M07 citacao normalizada (deixa de ser o texto exacto)',
     "'QUOTE_ORIGINAL': texto[a:fim],", "'QUOTE_ORIGINAL': ' '.join(texto[a:fim].split()),"),
    ('M08 traducao automatica nao detectada',
     "        originalidade = ORIG_TRADUCAO\n", "        originalidade = NAO_SEI\n"),
    ('M09 expressao relativa convertida pela data de publicacao',
     "        return {'FACT_TIME': NAO_SEI, 'FACT_TIME_PRECISION': 'NOT_KNOWN',\n"
     "                'FACT_TIME_BASIS': 'RELATIVA_SEM_DATA_DA_FALA",
     "        return {'FACT_TIME': published_at or NAO_SEI, 'FACT_TIME_PRECISION': 'NOT_KNOWN',\n"
     "                'FACT_TIME_BASIS': 'RELATIVA_SEM_DATA_DA_FALA"),
    ('M10 legenda sem pontuacao volta a ser uma frase so',
     "        if b - a <= MAX_FRASE:", "        if True:"),
    ('M11 maiuscula aleatoria do pedaco volta a ser lugar',
     "for m in ([] if so_nomes_conhecidos else RE_LUGAR_DO_RELATO.finditer(frase)):",
     "for m in RE_LUGAR_DO_RELATO.finditer(frase):"),
    ('M12 canal que publica vira pessoa',
     "(INSTITUICAO if institucional and doc['PUBLISHER'] != NAO_SEI else NAO_SEI)",
     "(PESSOA if doc['PUBLISHER'] != NAO_SEI else NAO_SEI)"),
    ('M13 papel declarado vira expertise no tema',
     "expertise = ('PROVADA_NA_DECLARACAO' if f and any(_norm(t) in _norm(decl) for t in tema)",
     "expertise = ('PROVADA_NA_DECLARACAO' if f"),
    ('M14 validador deixa de conferir a citacao',
     "    if texto[v['QUOTE_POS_START']:v['QUOTE_POS_END']] != v['QUOTE_ORIGINAL']:", "    if False:"),
    ('M15 validador deixa de conferir T8',
     "    if (v['UNIVERSO_DO_PAPEL'] == 'T8') != (v['ROLE'] == AGRICULTOR):", "    if False:"),
    ('M16 frase curta de apresentacao volta a emendar a seguinte',
     "            fb2 = fb\n",
     "            fb2 = fs[i + 1][1] if (i is not None and i + 1 < len(fs) and fb - fa < 40) else fb\n"),
    ('M17 segundo vocabulario de cultura (dono duplo)',
     "_PADROES_CULTURA = {k: MR._padrao(v) for k, v in MR.CROPS.items()}",
     "_PADROES_CULTURA = dict({k: MR._padrao(v) for k, v in MR.CROPS.items()}, WHEAT=MR._padrao(['wheat']))"),
    ('M18 «Palavra, …» volta a ser apresentacao',
     "                if not _papeis_em(' '.join(w[:2])):", "                if False:"),
]

ENV = dict(os.environ, PYTHONDONTWRITEBYTECODE='1',
           HTTP_PROXY='http://127.0.0.1:9', HTTPS_PROXY='http://127.0.0.1:9', http_proxy='http://127.0.0.1:9',
           https_proxy='http://127.0.0.1:9', ALL_PROXY='http://127.0.0.1:9', NO_PROXY='127.0.0.1,localhost',
           no_proxy='127.0.0.1,localhost')


def sem_pyc():
    # mutante do mesmo tamanho engana o .pyc (memoria da casa): apaga-se antes de cada corrida
    for f in glob.glob(os.path.join(RAIZ, 'motor', '__pycache__', 'voce_dal_campo*.pyc')):
        os.remove(f)


def correr():
    sem_pyc()
    r = subprocess.run([sys.executable, '-m', 'unittest', 'tests.test_voce_dal_campo'], cwd=RAIZ, env=ENV,
                       capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=900)
    falhas = sorted(set(l.split(' (')[0].split(': ', 1)[1] for l in r.stderr.splitlines()
                        if l.startswith(('FAIL: ', 'ERROR: '))))
    return r.returncode, falhas


with open(ALVO, 'rb') as fh:
    ORIGINAL = fh.read()
SHA0 = hashlib.sha256(ORIGINAL).hexdigest()
texto = ORIGINAL.decode('utf-8')
rc0, f0 = correr()
res = {'SHA256_ANTES': SHA0, 'LIMPO': {'RC': rc0, 'FALHAS': f0}, 'MUTANTES': []}
assert rc0 == 0, 'a suite tem de estar verde ANTES de mutar: %s' % f0
try:
    for nome, velho, novo in MUTANTES:
        n = texto.count(velho)
        if n != 1:
            res['MUTANTES'].append({'MUTANTE': nome, 'ESTADO': 'NAO_APLICADO', 'OCORRENCIAS': n})
            continue
        with open(ALVO, 'wb') as fh:
            fh.write(texto.replace(velho, novo).encode('utf-8'))
        rc, falhas = correr()
        res['MUTANTES'].append({'MUTANTE': nome, 'ESTADO': 'MORTO' if rc != 0 else 'SOBREVIVEU',
                                'TESTES_QUE_APANHARAM': falhas})
        print('%-62s %s  %s' % (nome, 'MORTO' if rc != 0 else 'SOBREVIVEU', falhas[:3]))
finally:
    with open(ALVO, 'wb') as fh:
        fh.write(ORIGINAL)
    sem_pyc()
with open(ALVO, 'rb') as fh:
    res['SHA256_DEPOIS'] = hashlib.sha256(fh.read()).hexdigest()
res['REPOSTO_IGUAL'] = res['SHA256_DEPOIS'] == SHA0
res['PLACAR'] = '%d/%d mortos' % (sum(m['ESTADO'] == 'MORTO' for m in res['MUTANTES']), len(MUTANTES))
with open(SAIDA, 'w', encoding='utf-8', newline='\n') as fh:
    json.dump(res, fh, ensure_ascii=False, indent=1)
    fh.write('\n')
print(res['PLACAR'], 'reposto igual:', res['REPOSTO_IGUAL'])
