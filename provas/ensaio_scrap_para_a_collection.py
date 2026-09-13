#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NIGHT-SHIFT-01 §11/§12 — O ENSAIO DO SCRAP CONTRA A COLLECTION REAL.

    SCRAP_ENSAIO_COLLECTION=/caminho/para/a/arvore/da/collection \\
        python3 provas/ensaio_scrap_para_a_collection.py

A pergunta não é «o contrato é o mesmo?». É esta:

    A COLHEITA QUE O SCRAP PRODUZ HOJE ATRAVESSA A COLLECTION DE HOJE —
    E, SE NÃO ATRAVESSA, EM QUE ARESTA SE PERDE PRIMEIRO?

O QUE NÃO SE FAZ AQUI, E É METADE DA PROVA
--------------------------------------------
Não se faz `git merge`. A árvore da Collection é lida como está, noutro sítio,
e o que atravessa é UM FICHEIRO JSON — o envelope que o SCRAP escreveu.

    UM ENVELOPE É DADOS. LEVAR DADOS NÃO É MERGEAR CÓDIGO.

E é isso que torna o ensaio honesto: se ele passar, passou com o código DELES
sobre os dados NOSSOS, sem ninguém ter costurado nada primeiro.

O QUE JÁ SE SABE ANTES DE CORRER, E FOI MEDIDO
------------------------------------------------
    leis/retorno_da_coleta.py   BYTE A BYTE IGUAL nas duas árvores
    coleta/scrap_colheita.py    NÃO EXISTE na árvore da Collection
    coleta/scrap_*.py           NENHUM existe lá

    CONTRATO IGUAL != ARESTA LIGADA.

Um contrato partilhado é a condição para a aresta existir, e não é a aresta.

    REAL_NETWORK = 0 · APIFY_RUNS = 0 · PAID_USD = 0
"""
import json
import os
import subprocess
import sys
import tempfile

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _p in ('provas', 'coleta', 'leis', 'medidas', 'ferramentas', 'guarda', ''):
    sys.path.insert(0, os.path.join(RAIZ, _p) if _p else RAIZ)

#: O ficheiro que corre DENTRO da árvore da Collection. Escrito aqui e passado
#: por caminho: importar os dois lados no mesmo processo faria dois módulos com
#: o mesmo nome disputarem o `sys.path`, e o que respondesse seria o que a
#: ordem da lista decidisse.
#:
#:     DOIS FICHEIROS COM O MESMO NOME DE MÓDULO SÃO DOIS DONOS DO MESMO NOME.
DO_LADO_DE_LA = r'''
import json, os, sys, tempfile
RAIZ = sys.argv[1]
ENVELOPE = sys.argv[2]
sys.path.insert(0, RAIZ)
import _gavetas                                                    # noqa: F401
import admissao as adm
import ingresso as ing
import retorno_da_coleta as rdc

fora = []
def caso(nome, ok, detalhe=''):
    fora.append({'ARESTA': nome, 'OK': bool(ok), 'PORQUE': detalhe})

env = json.load(open(ENVELOPE, encoding='utf-8'))
run = env.get('RUN_ID')

mal = rdc.conferir(env, RAIZ)
caso('E1_o_contrato_da_collection_aceita_o_envelope_do_scrap',
     not mal, '; '.join(mal[:3]))

itens = rdc.so_o_que_entra(env)
caso('E2_a_lei_deixa_passar_a_colheita', len(itens) == len(env['COLHEITA']),
     '%d de %d' % (len(itens), len(env['COLHEITA'])))

recibo = {'RUN_ID': run, 'PLATFORM': env.get('PLATFORM'),
          'ACTOR': 'coleta/scrap_colheita.py',
          'ACTOR_VERSION': env.get('EXECUTOR_VERSION'),
          'SOURCE_COUNTRY': 'IT', 'STARTED_AT': '2026-09-13T00:00:00Z'}
# ⚠️ UMA ARESTA, UM `try`. A primeira versao desta sonda envolvia as QUATRO
# num so `except` e carimbava qualquer queda com o nome da PRIMEIRA: ela dizia
# que a colheita se perdia no ingresso, e perdia-se na admissao.
#
#     UM `except` QUE REESCREVE O NOME DA ARESTA MENTE SOBRE ONDE SE PERDEU.
#     E `FIRST_LOST_EDGE` E EXACTAMENTE O NOME QUE ELE ESTAVA A REESCREVER.
def medir(nome, fn, detalhe=lambda v: ''):
    try:
        v = fn()
    except Exception as e:
        caso(nome, False, '%s: %s' % (type(e).__name__, str(e)[:200]))
        return None
    caso(nome, bool(v), detalhe(v))
    return v

r = medir('E3_o_ingresso_aceita_a_unidade',
          lambda: ing.receber(itens, corrida=recibo,
                              armazem=ing.ArmazemLocal(RAIZ), memoria=None,
                              raiz=RAIZ),
          lambda v: ('aceites=%d recusas=%s'
                     % (len(v['ACEITES']),
                        json.dumps([x.get('PORQUE') for x in v['RECUSAS']])[:160])
                     if len(v['ACEITES']) != len(itens) else ''))
if r is not None:
    caso('E4_o_raw_foi_preservado', bool(r.get('RAW')),
         '' if r.get('RAW') else 'o ingresso nao devolveu recibo de RAW')
    unidade = (r.get('PARA_A_PORTA') or [None])[0]
    caso('E5_a_fronteira_devolve_a_unidade_canonica', unidade is not None,
         '' if unidade is not None else 'o ingresso nao entregou unidade')
    if unidade is not None:
        # `decidir` devolve uma `Decisao` — um dataclass, e nao um dicionario.
        # `json.dumps` sobre ela rebentava, e a sonda culpava o ingresso.
        d = medir('E6_a_admissao_julga_a_unidade',
                  lambda: adm.decidir(unidade, 'T9', corrida=run),
                  lambda x: '%s · regra=%s · %s'
                            % (x.resultado, x.regra, str(x.motivo)[:90]))
        # ── E O QUE A DECISAO DIZ, QUE NAO E A MESMA PERGUNTA ──────────────
        # A aresta PASSA quando a admissao CONSEGUE julgar. O que ela julgou e
        # outra coisa, e misturar as duas faria um `NAO SEI` parecer travessia
        # completa.
        #
        #     A CADEIA LIGAR E A ADMISSAO DIZER SIM SAO DUAS PERGUNTAS.
        caso('E7_a_unidade_leva_texto_para_quem_julga',
             bool(str(unidade.get('texto') or unidade.get('title')
                      or unidade.get('nome') or '').strip()),
             'campos da unidade: %s' % ', '.join(sorted(unidade)))
        if d is not None:
            caso('E8_o_veredito_nao_e_uma_confissao_de_ignorancia',
                 d.resultado != 'NAO_SEI', '%s · %s' % (d.resultado, d.regra))

print(json.dumps(fora, ensure_ascii=False))
'''


def o_envelope_do_scrap():
    """Corre o canário gratuito e devolve o envelope que ele produz.

    O mundo é falso só no socket, como em toda a Release. O envelope é o de
    verdade — é este ficheiro que a Collection receberia.
    """
    import _rc01_mundo_falso as mundo
    import scrap_colheita as sc
    import social_envelope as env
    banco = tempfile.mkdtemp(prefix='ns-ensaio-')
    os.environ['RC01_MARCA'] = banco
    env.RAW_DIR = os.path.join(banco, 'raw')
    mundo.MARCA = banco
    mundo.IDAS = os.path.join(banco, 'IDAS.json')
    mundo.instalar()
    handle = mundo.FEED['feed'][0]['post']['author']['handle']
    return sc.colher('canario-bluesky', run_id='NS01-ENSAIO',
                     fonte='IT-T9-001', handle=handle)


def main():
    print(__doc__.strip().splitlines()[0])
    print('=' * 78)
    arvore = os.environ.get('SCRAP_ENSAIO_COLLECTION')
    envelope = o_envelope_do_scrap()
    print('\nO ENVELOPE DO SCRAP, COMO ELE SAI HOJE')
    print('   COLHEITA=%d · SUPORTE=%d · ESTADO=%s · CAPABILITY=%s'
          % (len(envelope['COLHEITA']), len(envelope['SUPORTE']),
             envelope['ESTADO'], envelope['CAPABILITY']))
    u = (envelope['COLHEITA'] or [{}])[0]
    print('   SOURCE_ID=%s · DOCUMENT_ID=%s · PAYLOAD=%s'
          % (u.get('SOURCE_ID'), u.get('DOCUMENT_ID'), u.get('PAYLOAD')))

    if not arvore or not os.path.isdir(arvore):
        # ── AUSÊNCIA DE ÁRVORE É AUSÊNCIA, E DIZ-SE ────────────────────────
        # Nunca um verde por omissão: uma prova que não encontra o que devia
        # medir não mediu nada, e o pior que pode fazer é parecer que mediu.
        print('\nCOLLECTION_TREE = NOT_PROVIDED')
        print('   Aponte `SCRAP_ENSAIO_COLLECTION` para uma árvore da '
              'Collection. Sem ela, nada foi medido sobre a travessia.')
        print('FIRST_LOST_EDGE = NAO_MEDIDO')
        return 2

    caminho = os.path.join(tempfile.mkdtemp(prefix='ns-env-'), 'ENVELOPE.json')
    with open(caminho, 'w', encoding='utf-8') as f:
        f.write(json.dumps(envelope, ensure_ascii=False, indent=1,
                           sort_keys=True))
    driver = os.path.join(os.path.dirname(caminho), 'ensaio_do_lado_de_la.py')
    with open(driver, 'w', encoding='utf-8') as f:
        f.write(DO_LADO_DE_LA)

    print('\nA ÁRVORE DA COLLECTION')
    sha = subprocess.run(['git', '-C', arvore, 'rev-parse', '--short', 'HEAD'],
                         capture_output=True, text=True).stdout.strip()
    print('   %s · HEAD=%s' % (arvore, sha or 'DESCONHECIDO'))
    print('   scrap_colheita.py existe lá? %s'
          % ('SIM' if os.path.isfile(os.path.join(arvore, 'coleta',
                                                  'scrap_colheita.py')) else 'NÃO'))

    saida = subprocess.run([sys.executable, driver, arvore, caminho],
                           capture_output=True, text=True)
    linhas = [l for l in saida.stdout.splitlines() if l.startswith('[')]
    if not linhas:
        print('\nO LADO DE LÁ NÃO RESPONDEU')
        print((saida.stderr or saida.stdout or '')[-800:])
        print('FIRST_LOST_EDGE = E0_A_ARVORE_NAO_CORREU')
        return 1

    print('\nARESTA A ARESTA, COM O CÓDIGO DELES SOBRE OS DADOS NOSSOS')
    primeiro = None
    for c in json.loads(linhas[-1]):
        print('   %-48s %s%s'
              % (c['ARESTA'], 'PASSA' if c['OK'] else 'PARA',
                 ('  · ' + c['PORQUE']) if c['PORQUE'] else ''))
        if not c['OK'] and primeiro is None:
            primeiro = c['ARESTA']
    print('=' * 78)
    print('FIRST_LOST_EDGE = %s' % (primeiro or 'NENHUMA — a colheita atravessa'))
    print()
    print('O QUE ISTO NAO RESOLVE, E POR QUE NAO SE RESOLVE SOZINHO')
    print('   `social_envelope` guarda o texto da observacao em `TEXT`, e')
    print('   quem julga le `texto`. Nao ha entrada para ele em NENHUM dos')
    print('   dois mapas — nem em `scrap_colheita.DO_SCRAP_PARA_A_PORTA`,')
    print('   nem em `ingresso.PARA_A_PORTA`. O texto existe dos dois lados')
    print('   e nao atravessa; por isso a admissao responde NAO SEI, que e')
    print('   a resposta CERTA para um item sem conteudo.')
    print()
    print('   E liga-lo sao DUAS decisoes, e nao uma:')
    print('     1 · TEXT -> texto          o texto atravessa')
    print('     2 · CONTENT_TYPE -> ?      para quem julga saber O QUE leu')
    print()
    print('   Fazer 1 sem 2 entrega texto de autor e fala reconhecida no')
    print('   MESMO campo, indistinguiveis — que e exactamente a soma que a')
    print('   casa proibe: CAPTION != TRANSCRIPT. E a segunda precisa de um')
    print('   campo que o vocabulario da porta hoje nao tem.')
    print()
    print('   BLOCKED_BY_HUMAN = VOCABULARIO_DO_TEXTO_NA_PORTA')
    print('REAL_NETWORK = 0 · APIFY_RUNS = 0 · PAID_USD = 0')
    return 1 if primeiro else 0


if __name__ == '__main__':
    sys.exit(main())
