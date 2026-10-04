#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""CHANGED_IN_PLACE E MUDANCA REAL, OU E O RASTO DA NOSSA VISITA?

    UM SITE QUE CARIMBA A HORA DE QUEM O VISITA DEVOLVE UM FICHEIRO
    DIFERENTE A CADA VISITA SEM TER MUDADO NADA.
    QUEM COMPARA BYTES CONTA A PROPRIA PEGADA COMO NOTICIA.

Medido no canario do cutover (2026-09-22, duas passagens a 4 minutos de
distancia sobre IT-T10-018 e IT-T10-022):

    71 versoes novas no armazem
    32 documentos comparados versao a versao
    TEXTO VISIVEL IGUAL em 32 de 32 — nenhuma palavra mudou

De onde vinha o «mudou»:

    23 documentos   article:modified_time com a hora do NOSSO pedido ·
                    contador de visualizacoes 132 -> 134 (as nossas duas
                    visitas) · _session_key e _token novos por pedido.
                    22 deles com o MESMO numero de bytes nos dois lados.
     9 documentos   banners a rodar (`zoote-target`, links utm_source,
                    imagem do banner) e as tags de fecho que se
                    deslocaram com eles.

⚠️ ZERO REDE. Le so o que ja esta no armazem.

⚠️ A PRIMEIRA VERSAO DESTE FICHEIRO DAVA «9 COM MUDANCA REAL». Ao olhar as
linhas que ela contou, as 9 eram publicidade. O classificador foi apertado
e cada padrao leva a razao ao lado.

    UM CLASSIFICADOR GENEROSO DEVOLVE «MUDOU» E NINGUEM CONFERE.
    O NUMERO SO VALE DEPOIS DE SE OLHAR AS LINHAS QUE ELE CONTOU.

A prova FORTE nao e esta classificacao por padrao — e a comparacao do TEXTO
VISIVEL, que nao depende de saber os padroes de antemao: tira-se toda a
marcacao e normalizam-se os numeros (o contador de visualizacoes e um
numero no texto). Se o texto for igual, nao houve noticia nova, quaisquer
que sejam os bytes.

    py provas/a_mudanca_e_nossa_pegada.py
"""
import io, os, re, subprocess, sys, json

#: A raiz operacional NAO vive escrita aqui. Vem de `ITALY_OPS_ROOT`, que e a
#: variavel que o proprio coletor agendado usa; sem ela, le o armazem desta
#: arvore. Um caminho de maquina escrito no codigo faz a prova dar zero numa
#: maquina que nao e a do autor — e zero le-se como «nada mudou».
RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OPS = os.environ.get('ITALY_OPS_ROOT') or RAIZ
STORE = os.path.join(OPS, 'data', 'collection-store', 'italy')

#: Padroes que provam rasto de maquina. Cada um com a razao ao lado — quem o
#: quiser tirar tem de apagar tambem a razao.
RASTO = [
    (re.compile(r'article:modified_time', re.I), 'o site carimba a hora do pedido'),
    (re.compile(r'_session_key|_token|csrf|authenticity_token', re.I), 'token por pedido'),
    (re.compile(r'nonce=', re.I), 'nonce por pedido'),
    (re.compile(r'^\s*\d{1,7}\s*$'), 'numero solto — contador de visualizacoes'),
    (re.compile(r'og:updated_time|dateModified', re.I), 'data de modificacao servida'),
    # ⚠️ ACRESCENTADO DEPOIS DA PRIMEIRA MEDICAO, E O PORQUE FICA ESCRITO.
    # A primeira volta deu «9 documentos com mudanca real». Olhando as linhas,
    # TODAS as 9 eram BANNERS A RODAR: `zoote-target` com id novo a cada
    # pedido, `data-zoote-trackid`, links de patrocinador com `utm_source`, e
    # a imagem do banner. Isso e churn de publicidade, nao materia editorial.
    #
    #     UM CLASSIFICADOR GENEROSO DEVOLVE «MUDOU» E NINGUEM CONFERE.
    #     O NUMERO SO VALE DEPOIS DE SE OLHAR AS LINHAS QUE ELE CONTOU.
    (re.compile(r'zoote-target|data-zoote-track|zoote-\d+'), 'banner a rodar (slot de anuncio)'),
    (re.compile(r'utm_source=|utm_medium=|utm_campaign='), 'link de patrocinador com etiqueta de campanha'),
    (re.compile(r'wp-content/uploads/.*(banner|_670x|ET\d\d)', re.I), 'imagem de banner'),
    (re.compile(r'data-no-instant="1"\s+href='), 'ancora de banner'),
]



def _texto_visivel(p):
    """O texto que uma pessoa leria, sem nada de marcacao."""
    t = open(p, 'rb').read().decode('utf-8', 'replace')
    t = re.sub(r'(?is)<(script|style|noscript)[^>]*>.*?</\1>', ' ', t)
    t = re.sub(r'(?s)<[^>]+>', ' ', t)
    t = re.sub(r'&[a-z#0-9]{2,8};', ' ', t)
    return re.sub(r'\s+', ' ', t).strip()


def versoes(d):
    vs = sorted([x for x in os.listdir(d) if re.match(r'^v\d+_', x)],
                key=lambda x: int(x.split('_')[0][1:]))
    return vs


def linhas(p):
    b = open(p, 'rb').read()
    t = b.decode('utf-8', 'replace').replace('>', '>\n')
    return t.split('\n')


def _alvos():
    """Os documentos a comparar. Duas maneiras, e nenhuma delas silenciosa.

    `--fonte IT-T10-018,IT-T10-022`  todos os documentos dessas fontes que
                                     tenham ao menos DUAS versoes.
    sem argumento                    so os que ganharam versao AGORA e ainda
                                     nao estao commitados (o modo de correr
                                     logo depois de uma coleta).

    ⚠️ O MODO SEM ARGUMENTO DA ZERO DEPOIS DE SE COMMITAR. A primeira versao
    desta prova so tinha esse modo, e depois de o canario ser commitado ela
    imprimia `0 de 0` — que se le como «nenhuma mudanca encontrada» quando
    quer dizer «nada havia para comparar».

        ZERO COMPARADO NAO E ZERO MUDADO.
        UMA PROVA SEM ALVOS TEM DE REPROVAR, NUNCA PASSAR.
    """
    i = sys.argv.index('--fonte') if '--fonte' in sys.argv else -1
    if i > 0 and i + 1 < len(sys.argv):
        fontes = [f.strip() for f in sys.argv[i + 1].split(',') if f.strip()]
        docs = []
        for f in fontes:
            fd = os.path.join(STORE, f)
            if not os.path.isdir(fd):
                print('FONTE SEM ARMAZEM: %s (%s)' % (f, fd))
                continue
            for doc in sorted(os.listdir(fd)):
                if os.path.isdir(os.path.join(fd, doc)):
                    docs.append(os.path.relpath(os.path.join(fd, doc), OPS)
                                .replace('\\', '/'))
        return sorted(docs), '--fonte %s' % ','.join(fontes)
    r = subprocess.run(['git', '-C', OPS, 'status', '--short',
                        'data/collection-store'], capture_output=True)
    novos = [l[3:].strip() for l in r.stdout.decode('utf-8').split('\n') if l.strip()]
    docs = sorted(set('/'.join(p.rstrip('/').split('/')[:-1]) for p in novos))
    return docs, 'versoes novas ainda nao commitadas'


def main():
    docs, modo = _alvos()
    print('MODO  %s' % modo)
    print('ALVOS %d documento(s)' % len(docs))
    print()
    if not docs:
        print('SEM ALVOS PARA COMPARAR. Isto NAO e «nada mudou».')
        print('Corre logo depois de uma coleta, ou nomeia as fontes:')
        print('    py provas/a_mudanca_e_nossa_pegada.py --fonte IT-T10-018,IT-T10-022')
        return 2

    reais, rasto_so, sem_par = [], [], []
    detalhe = []
    for rel in docs:
        d = os.path.join(OPS, rel)
        if not os.path.isdir(d):
            continue
        vs = versoes(d)
        if len(vs) < 2:
            sem_par.append(rel); continue
        va, vb = vs[-2], vs[-1]
        fa = os.path.join(d, va, os.listdir(os.path.join(d, va))[0])
        fb = os.path.join(d, vb, os.listdir(os.path.join(d, vb))[0])
        ta, tb = linhas(fa), linhas(fb)
        import difflib
        dif = [l for l in difflib.unified_diff(ta, tb, n=0)
               if (l.startswith('+') or l.startswith('-'))
               and not l.startswith('+++') and not l.startswith('---')]
        classificadas = []
        for l in dif:
            corpo = l[1:]
            porque = None
            for rx, razao in RASTO:
                if rx.search(corpo):
                    porque = razao; break
            classificadas.append((porque or 'MUDANCA_REAL', corpo[:120]))
        n_real = sum(1 for c, _ in classificadas if c == 'MUDANCA_REAL')
        bytes_iguais = os.path.getsize(fa) == os.path.getsize(fb)
        detalhe.append({
            'DOC': rel.split('/')[-1][:70],
            'DE': va, 'PARA': vb,
            'BYTES_IGUAIS': bytes_iguais,
            'LINHAS_DIFERENTES': len(classificadas),
            'MUDANCA_REAL': n_real,
            'MOTIVOS_DO_RASTO': sorted(set(c for c, _ in classificadas if c != 'MUDANCA_REAL')),
            'AMOSTRA_REAL': [t for c, t in classificadas if c == 'MUDANCA_REAL'][:3],
                    '_PAR': (fa, fb),
        })
        (reais if n_real else rasto_so).append(rel)

    print('DOCUMENTOS_COM_VERSAO_NOVA        %d' % len(detalhe))
    print('SO_RASTO_DA_VISITA                %d' % len(rasto_so))
    print('COM_AO_MENOS_UMA_MUDANCA_REAL     %d' % len(reais))
    print('SEM_VERSAO_ANTERIOR_PARA_COMPARAR %d' % len(sem_par))
    print()
    print('BYTES_IGUAIS_NOS_DOIS_LADOS       %d de %d'
          % (sum(1 for d in detalhe if d['BYTES_IGUAIS']), len(detalhe)))
    print()
    import collections
    c = collections.Counter()
    for d in detalhe:
        for m in d['MOTIVOS_DO_RASTO']:
            c[m] += 1
    for m, n in c.most_common():
        print('  %-45s em %d documentos' % (m, n))
    print()
    for d in detalhe[:3]:
        print('  %s  %s->%s  %d linhas dif, %d reais  %s'
              % (d['DOC'][:48], d['DE'][:2], d['PARA'][:2],
                 d['LINHAS_DIFERENTES'], d['MUDANCA_REAL'], d['MOTIVOS_DO_RASTO']))
    if reais:
        print()
        print('CLASSIFICADOS COMO REAIS PELA REGRA DE PADROES:')
        for d in detalhe:
            if d['MUDANCA_REAL']:
                print('  %s  %d linhas  %s' % (d['DOC'][:50], d['MUDANCA_REAL'], d['AMOSTRA_REAL']))

    # ── A PROVA FORTE: O TEXTO VISIVEL ───────────────────────────────────
    # Nao depende de conhecer os padroes de antemao. Tira TODA a marcacao e
    # normaliza os numeros (o contador de visualizacoes e um numero no
    # texto). Se o texto for igual, nao houve noticia nova — quaisquer que
    # sejam os bytes, o hash ou o veredito do comparador.
    print()
    print('TEXTO VISIVEL, SEM MARCACAO (a prova que nao precisa de padroes):')
    ti = td = 0
    diferentes = []
    for d in detalhe:
        if not d.get('_PAR'):
            continue
        fa, fb = d['_PAR']
        na = re.sub(r'\b\d{1,7}\b', 'N', _texto_visivel(fa))
        nb = re.sub(r'\b\d{1,7}\b', 'N', _texto_visivel(fb))
        if na == nb:
            ti += 1
        else:
            td += 1
            diferentes.append(d['DOC'])
    print('   TEXTO_IGUAL      %d de %d' % (ti, ti + td))
    print('   TEXTO_DIFERENTE  %d de %d' % (td, ti + td))
    for x in diferentes[:8]:
        print('     mudou de verdade: %s' % x)
    print()
    veredito = 'A_MUDANCA_E_NOSSA_PEGADA' if td == 0 else 'HOUVE_MUDANCA_REAL'
    print('VEREDITO = %s   (%d de %d documentos sem uma palavra mudada)'
          % (veredito, ti, ti + td))

    saida = os.path.join(RAIZ, 'provas', 'A-MUDANCA-E-NOSSA-PEGADA-V1.json')
    for d in detalhe:
        d.pop('_PAR', None)
    with io.open(saida, 'w', encoding='utf-8', newline='\n') as fh:
        json.dump({'MODO': modo, 'OPS': OPS,
                   'RESUMO': {'DOCS': len(detalhe), 'SO_RASTO': len(rasto_so),
                              'CLASSIFICADOS_REAIS_POR_PADRAO': len(reais),
                              'TEXTO_IGUAL': ti, 'TEXTO_DIFERENTE': td,
                              'VEREDITO': veredito},
                   'DETALHE': detalhe}, fh, ensure_ascii=False, indent=1)
        fh.write('\n')
    print('escrito em %s' % saida)
    return 0


if __name__ == '__main__':
    sys.exit(main())
