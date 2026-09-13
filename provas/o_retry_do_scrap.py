#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SCRAP-E2E-04 — O RETRY DE VERDADE: A MESMA CORRIDA, DEPOIS DE TROPEÇAR.

    BANCO_DESCARTAVEL_URL=postgresql://postgres@127.0.0.1:5433/descartavel \\
        python3 provas/o_retry_do_scrap.py

A DIFERENÇA PARA `a_repeticao_do_scrap.py`, E ELA É TODA A PROVA
-----------------------------------------------------------------
Aquela prova corre a MESMA fonte duas vezes e mede o que fica. Isso prova uma
coisa verdadeira e prova-a bem:

    NEW RUN  +  NEW RUN

E não prova esta, que é outra pergunta inteira:

    UMA CORRIDA FALHA  ->  RETRY  ->  CONTINUA

    DUAS CORRIDAS NOVAS NÃO SÃO UMA CORRIDA REPETIDA.
    A primeira mede idempotência entre corridas; esta mede RECUPERAÇÃO
    DENTRO de uma.

A FALHA É REAL, E ACONTECE DEPOIS DE A CORRIDA JÁ ESTAR PERSISTIDA
-------------------------------------------------------------------
Nada de exceção injetada em código de produção. A colheita traz DOIS posts, e
antes da primeira tentativa põe-se uma PASTA exatamente onde o ficheiro do
segundo tem de ser escrito. O sistema de ficheiros recusa — como recusaria com
o disco cheio ou sem permissão — e `guarda/preservar_coleta.py` faz com essa
recusa o que já sabe fazer: manda-a para `FALHADOS` e segue com o resto.

    A FALHA NÃO FOI ENSINADA AO CÓDIGO. FOI POSTA NO MUNDO,
    E O CÓDIGO RESPONDEU COMO RESPONDE.

Quando a primeira tentativa termina, o acervo está com a corrida aberta, o
post A preservado e o post B por fazer. É esse — e não uma árvore vazia — o
estado que um retry tem de saber continuar.

    UMA FALHA NO PRIMEIRO PASSO MEDE ARRANQUE, NÃO RECUPERAÇÃO.

O QUE O RETRY TEM DE PROVAR
---------------------------
    ERROR != REJECTED != ZERO      o B não foi recusado na porta nem
                                   «não existiu»: a escrita dele falhou
    REUSED != NEW                  o A não entra outra vez
    NOT_RUN != PASS                a tentativa 1 não se declara cumprida
    o retry não duplica RAW         nem STORAGE
    o retry não perde linhagem
    o retry não inventa sucesso

E a pergunta que o brief manda não presumir — **o retry mantém o mesmo RUN_ID
ou cria uma corrida nova?** — responde-se MEDINDO, e a resposta está no fim.

    REAL_NETWORK = 0 · PAID_USD = 0 · LIVE_READS = 0 · LIVE_WRITES = 0
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _p in ('orquestrador', 'pedido', 'coleta', 'leis', 'regras', 'ferramentas',
           'medidas', 'guarda', 'admissao', ''):
    sys.path.insert(0, os.path.join(RAIZ, _p) if _p else RAIZ)

import importlib.util as _u        # noqa: E402

_sp = _u.spec_from_file_location(
    'e2e01', os.path.join(RAIZ, 'provas', 'o_scrap_chega_ao_acervo.py'))
_e2e = _u.module_from_spec(_sp)
_sp.loader.exec_module(_e2e)

_spg = _u.spec_from_file_location(
    'prova_pg', os.path.join(RAIZ, 'provas', 'preservar_coleta_no_postgres.py'))
_pg = _u.module_from_spec(_spg)
_spg.loader.exec_module(_pg)

FALHAS = []
SHIM = os.path.join(RAIZ, 'provas', '_e2e02_janela_dois_posts.py')


def diz(ok, titulo, detalhe=''):
    print('  %-5s %-50s %s' % ('ok' if ok else 'FALHA', titulo[:50],
                               str(detalhe)[:58]))
    if not ok:
        FALHAS.append(titulo)


#: O que corre DENTRO da cópia. A primeira tentativa é a corrida canónica
#: inteira — `orquestrador.correr()` — para a corrida nascer como nasce na
#: vida real, com a linha de `collection_run` aberta pelo dono dela.
#:
#: ⚠️ A SEGUNDA TENTATIVA NÃO PODE SER OUTRO `correr()`. Ele cunha um `RUN_ID`
#: novo a cada chamada — e aí estaríamos a medir OUTRA corrida, que é
#: exactamente o que `a_repeticao_do_scrap.py` já mede. O retry entra pela
#: MESMA porta por onde a primeira passou, com o MESMO recibo.
DRIVER = """
import json, os, sys
RAIZ = os.path.dirname(os.path.abspath(__file__))
for p in ('orquestrador','pedido','coleta','leis','regras','ferramentas',
          'medidas','guarda','admissao',''):
    sys.path.insert(0, os.path.join(RAIZ, p) if p else RAIZ)
import importlib.util as u
_s = u.spec_from_file_location(
    'prova_pg', os.path.join(RAIZ, 'provas', 'preservar_coleta_no_postgres.py'))
_m = u.module_from_spec(_s); _s.loader.exec_module(_m)
import coleta_checkpoint as cc
import orquestrador as orq, pedido as pd
import retorno_da_coleta as rc, scrap_colheita as sc
url = os.environ['BANCO_DESCARTAVEL_URL']
fase = sys.argv[1]

if fase == 'primeira':
    p = pd.de_uma_frase('colete concorrentes')
    p.filtros.update({'fase': 'janela-perfis', 'pais': 'IT', 'fonte': sys.argv[2]})
    recibo = orq.correr(p, memoria=_m.MemoriaPostgres(url),
                        banco_do_rastro=cc.Banco(url))
    recibo.pop('_plano', None)
    alvo = os.path.join(RAIZ, rc.endereco_do_envelope(
        sc.ENVELOPE, str(recibo.get('RUN_ID') or '')))
    env = json.load(open(alvo, encoding='utf-8')) if os.path.isfile(alvo) else {}
    json.dump({'RECIBO': recibo, 'ENV': env},
              open(os.path.join(RAIZ, '_estado.json'), 'w', encoding='utf-8'),
              ensure_ascii=False, default=str)
    print('<<<R>>>' + json.dumps(recibo, ensure_ascii=False, default=str))
else:
    d = json.load(open(os.path.join(RAIZ, '_estado.json'), encoding='utf-8'))
    recibo, env = d['RECIBO'], d['ENV']
    itens = rc.so_o_que_entra(env)
    r = orq.pela_entrada(itens, recibo, memoria=_m.MemoriaPostgres(url),
                         banco_do_rastro=cc.Banco(url))
    print('<<<R>>>' + json.dumps(r, ensure_ascii=False, default=str))
"""


def correr_fase(arvore, url, fase, fonte='-'):
    caminho = os.path.join(arvore, '_retry_driver.py')
    with open(caminho, 'w', encoding='utf-8') as f:
        f.write(DRIVER)
    amb = dict(os.environ, FLOW01_MARCA=arvore, PYTHONIOENCODING='utf-8',
               BANCO_DESCARTAVEL_URL=url, PYTHONDONTWRITEBYTECODE='1')
    r = subprocess.run([sys.executable, caminho, fase, fonte], cwd=arvore,
                       capture_output=True, text=True, env=amb, timeout=900)
    for linha in (r.stdout or '').splitlines():
        if linha.startswith('<<<R>>>'):
            return json.loads(linha[len('<<<R>>>'):])
    print((r.stdout or '')[-1200:])
    print((r.stderr or '')[-1200:])
    return {}


def main():
    url = os.environ.get('BANCO_DESCARTAVEL_URL')
    if not url:
        print('FALTA BANCO_DESCARTAVEL_URL — e SKIP != PASS.')
        print('RETRY_DO_SCRAP=NOT_MEASURED')
        return 2
    if not _pg._e_descartavel(url):
        print('RECUSADO: a URL nao e de um banco descartavel local.')
        return 2

    print(__doc__.strip().splitlines()[0])
    print('=' * 74)
    # ⚠️ O ESQUEMA, PELO DONO DELE — e nao por uma segunda copia da
    # cadeia escrita aqui. O workflow entrega um banco recem-criado, e
    # sem isto esta prova morria em «relation does not exist» a dizer
    # outra coisa qualquer.
    #
    #     UM PORTAO QUE NAO CHEGA A CORRER NAO E UM PORTAO A FALHAR:
    #     E UM PORTAO QUE NAO EXISTE.
    _e2e.garantir_o_esquema(url)
    base = tempfile.mkdtemp(prefix='scrap-retry-')
    arvore = os.path.join(base, 'arvore')
    os.makedirs(arvore)
    try:
        _e2e.com_este_falso(arvore, SHIM)

        # ── A PEDRA NO CAMINHO ──────────────────────────────────────────
        # ⚠️ A PRIMEIRA VERSÃO DESTA PROVA PÔS A PEDRA NO SÍTIO ERRADO, e a
        # própria prova apanhou-a: calculou o endereço do segundo bruto com um
        # `RUN_ID` inventado (`DESCOBERTA`), e o endereço REAL saiu outro.
        #
        # A razão está medida em `provas/a_repeticao_do_scrap.py`: o bruto
        # preservado carrega dentro dele o nome da corrida que o trouxe, e o
        # endereço é o sha do conteúdo. Logo O ENDEREÇO SÓ EXISTE DEPOIS DE A
        # CORRIDA TER NOME — e antes disso não há caminho nenhum para bloquear.
        #
        #     UM ENDEREÇO QUE DEPENDE DA CORRIDA NÃO SE ADIVINHA ANTES DELA.
        #
        # O que apanhou o engano não foi releitura: foram as asserções do passo
        # 1, que exigiam UM post preservado e a corrida NÃO cumprida. Sem elas,
        # a pedra teria caído no vazio, os dois posts teriam entrado, e esta
        # prova diria «retry provado» tendo medido uma corrida que nunca falhou.
        #
        #     UMA FALHA QUE NÃO ACONTECEU PASSA EM QUALQUER PROVA
        #     QUE NÃO EXIJA VER A FALHA.
        #
        # A alavanca que resta é do MUNDO e não do endereço: o armazém fica sem
        # permissão de escrita durante a primeira tentativa. É o disco a
        # recusar — como recusaria cheio ou sem permissão — e `preservar()`
        # responde como já sabe responder: manda para `FALHADOS` e segue.
        #
        # O QUE ISTO COBRE, DITO SEM ALARGAR: a corrida chega a existir no
        # acervo (a linha de `collection_run` é aberta por `preservar()` antes
        # dos objetos) e NENHUMA observação entra. É recuperação de uma corrida
        # persistida, e NÃO é recuperação a meio de um lote — essa exigiria
        # falhar o segundo bruto e não o primeiro, e o endereço dele não é
        # conhecível antes da corrida.
        #
        #     COBERTURA DECLARADA É COBERTURA. COBERTURA SUPOSTA É BURACO.
        # ⚠️ E `chmod` NÃO SERVE AQUI, o que também foi medido: esta prova
        # corre como `root`, e o root ignora os bits de permissão de um
        # directório. A primeira tentativa com `0o555` preservou os dois posts
        # à mesma.
        #
        #     UMA TRANCA QUE O UTILIZADOR DESTA MÁQUINA IGNORA
        #     NÃO É UMA TRANCA: É UMA DECORAÇÃO.
        #
        # O que o root NÃO consegue contornar é a forma do sistema de
        # ficheiros: debaixo de um FICHEIRO não existe caminho. Pondo um
        # ficheiro onde tem de haver a pasta, o `os.makedirs` de
        # `ArmazemLocal.enviar` levanta `NotADirectoryError` — um `OSError`
        # como o do disco cheio — e `preservar()` trata-o como já trata.
        # E O DEPÓSITO NÃO É O QUE EU SUPUS — TAMBÉM ISSO FOI MEDIDO.
        # A primeira versão bloqueou `data/raw/observacoes/`, que é onde a
        # FICHA do contrato comum diz que o artefato mora. O `raw_asset` real
        # desta rota guarda outra coisa:
        #
        #     IT/it-t9-001/OBSERVATION/<...>.json
        #
        # Duas moradas, e só uma é a que o armazém usa.
        #
        #     O SÍTIO ONDE EU ACHO QUE OS BYTES FICAM
        #     NÃO É O SÍTIO ONDE ELES FICAM.
        #
        # Esta depende do PAÍS e da FONTE — as duas conhecidas antes da corrida
        # — e não do sha. Por isso pode ser bloqueada de antemão, e é ela.
        deposito = os.path.join(arvore, 'IT',
                                _e2e.FONTE.lower(), 'OBSERVATION')
        if os.path.isdir(deposito):
            shutil.rmtree(deposito)
        os.makedirs(os.path.dirname(deposito), exist_ok=True)
        with open(deposito, 'w', encoding='utf-8') as f:
            f.write('o armazem esta fechado nesta tentativa')
        print('  · o armazem nao aceita escrita na 1a tentativa (%s)'
              % os.path.relpath(deposito, arvore))

        print('\n1 · A PRIMEIRA TENTATIVA — E ELA TROPEÇA')
        recibo = correr_fase(arvore, url, 'primeira', _e2e.FONTE)
        run_id = (recibo or {}).get('RUN_ID') or ''
        if not run_id:
            diz(False, 'a corrida nasceu', 'sem RUN_ID')
            print('RETRY_DO_SCRAP=NOT_MEASURED')
            return 1
        a = run_id.replace("'", "''")
        ing1 = (recibo.get('INGRESSO') or {})
        d1 = medir(url, a, arvore)
        print('      RUN_ID=%s' % run_id)
        print('      PRESERVADOS=%s RECUSADOS=%s RUN_STATE=%s'
              % (ing1.get('PRESERVADOS'), ing1.get('RECUSADOS'),
                 ing1.get('RUN_STATE')))
        diz(d1['run_rows'] == 1,
            'a CORRIDA chegou a existir no acervo (persistiu)', d1['run_rows'])
        diz(d1['raw'] == 0, 'e NENHUMA observação entrou — o disco recusou',
            d1['raw'])
        diz(d1['obj'] == 0, 'nem nenhum objeto de armazenamento', d1['obj'])
        # ── ERROR != REJECTED != ZERO ───────────────────────────────────
        # O B não foi recusado na porta (isso seria REJECTED, e a porta teria
        # dito porquê), e não é «não havia nada» (isso seria ZERO). A escrita
        # dele falhou, e o estado da corrida diz isso.
        diz(ing1.get('RECUSADOS') == 0,
            'e o que falhou NÃO foi recusado na porta',
            'RECUSADOS=%s' % ing1.get('RECUSADOS'))
        diz(ing1.get('RUN_STATE') != 'COMPLETE',
            'a corrida NÃO se declara cumprida', ing1.get('RUN_STATE'))
        diz(d1['etapas'] and d1['etapas'][0][1] == '0',
            'a tentativa registada é a 0', d1['etapas'])

        print('\n2 · TIRA-SE A PEDRA, E O RETRY ENTRA PELA MESMA PORTA')
        os.remove(deposito)                # o armazem volta a aceitar
        os.makedirs(deposito, exist_ok=True)
        r2 = correr_fase(arvore, url, 'retry')
        d2 = medir(url, a, arvore)
        print('      PRESERVADOS=%s RECUSADOS=%s RUN_STATE=%s'
              % (r2.get('PRESERVADOS'), r2.get('RECUSADOS'),
                 r2.get('RUN_STATE')))

        print('\n3 · O QUE O RETRY FEZ, MEDIDO NO BANCO')
        diz(d2['run_rows'] == 1,
            'o retry NÃO abriu uma corrida nova — é a MESMA',
            '%d linha(s) de collection_run' % d2['run_rows'])
        diz(d2['raw'] == 2, 'os posts que faltavam entraram', d2['raw'])
        diz(d2['obj'] == 2, 'e cada um ganhou objeto próprio', d2['obj'])
        diz(d2['raw_total'] == 2, 'e NADA se duplicou no acervo inteiro',
            d2['raw_total'])
        # ── REUSED != NEW ───────────────────────────────────────────────
        # O A não entrou outra vez: a linha dele é a MESMA (mesmo id), e o
        # contador de tentativas subiu — que é a diferença entre «reaproveitei»
        # e «criei outro».
        diz(d2['raw_total'] == d2['raw'],
            'e o acervo inteiro tem exactamente estas — nada a mais',
            '%d no total' % d2['raw_total'])
        tentativas = [e[1] for e in d2['etapas'] if e[0] == 'RAW']
        diz(tentativas == ['0', '1'],
            'a etapa RAW tem DUAS tentativas, e a primeira ficou',
            tentativas)
        diz(d2['sem_objeto'] == 0, 'nenhuma observação ficou sem linhagem',
            d2['sem_objeto'])
        diz(d2['linhagem_fechada'] == d2['raw'],
            'e a cadeia RUN → RAW → STORAGE fecha para as duas',
            '%d/%d' % (d2['linhagem_fechada'], d2['raw']))
        diz(r2.get('RUN_STATE') == 'COMPLETE',
            'e SÓ AGORA a corrida se declara cumprida', r2.get('RUN_STATE'))

        print('\n4 · CHECKPOINT — O QUE ESTA ROTA TEM, E O QUE NÃO TEM')
        # ⚠️ AUSÊNCIA DE IMPLEMENTAÇÃO NÃO É PASS, e por isso isto mede-se em
        # vez de se supor. O mecanismo EXISTE nesta casa —
        # `coleta/coleta_checkpoint.py`, com `abrir`, `pode_gastar` e
        # `unidades_pendentes` — e é a rota PAGA que o usa. A rota SCRAP livre
        # não lhe toca: nem o adapter, nem o executor, nem a receita o
        # mencionam.
        #
        #     MECANISMO EXISTE != ROTA USA.
        #     E «não usa» dito com nome é dívida; calado é defeito.
        #
        # A consequência é concreta e vale dizer: o retry desta rota REFAZ a
        # colheita inteira. Como nada duplica no acervo, isso custa TEMPO e não
        # correcção — mas numa colheita grande o tempo é a conta.
        cps = int(_e2e.q(url, 'select count(*) from checkpoint_coleta')[0][0])
        ligado = _e2e.q(url, "select coalesce(checkpoint_id::text,'-') from "
                             "collection_run where run_id = '%s'" % a)
        diz(cps == 0 and ligado and ligado[0][0] == '-',
            'CHECKPOINT = NOT_SUPPORTED nesta rota, e medido',
            'linhas=%d · checkpoint_id=%s' % (cps, ligado[0][0] if ligado else '?'))

        print('\n' + '=' * 74)
        print('  RETRY_SAME_LOGICAL_RUN       = %s'
              % ('YES' if d2['run_rows'] == 1 else 'NO'))
        print('  RUN_ID                       = o MESMO (%s)' % run_id)
        print('  ATTEMPT_PROPAGATION          = etapa %s · observacao %s -> %s'
              % (tentativas, d1['attempts_do_A'], d2['attempts_do_A']))
        print('  RAW_DUPLICATION_ON_RETRY     = %d' % (d2['raw_total'] - 2))
        print('  STORAGE_DUPLICATION_ON_RETRY = %d' % (d2['obj'] - 2))
        print('  ERROR_STATE                  = %s (1a tentativa)'
              % ing1.get('RUN_STATE'))
        print('  RETRY_FINAL_STATE            = %s' % r2.get('RUN_STATE'))
        print('  CHECKPOINT                   = NOT_SUPPORTED (medido)')
        print('  LINEAGE                      = %d/%d fechadas'
              % (d2['linhagem_fechada'], d2['raw']))
        print('  REAL_NETWORK = 0 · PAID_USD = 0')
        print('=' * 74)
        if FALHAS:
            print('FALHAS (%d):' % len(FALHAS))
            for f in FALHAS:
                print('   · %s' % f.strip())
            print('RETRY_DO_SCRAP=NO')
            return 1
        print('RETRY_DO_SCRAP=YES')
        return 0
    finally:
        shutil.rmtree(base, ignore_errors=True)


def caminhos_dos_brutos(arvore):
    """Os endereços que o ingresso VAI usar, pelo caminho que ele usa.

    Corre-se o mapeador do adapter sobre os itens do falso e pede-se a ficha ao
    dono do contrato. Nada de `glob`, nada de adivinhar o sha.
    """
    r = subprocess.run(
        [sys.executable, '-c', DESCOBRIR], cwd=arvore, capture_output=True,
        text=True, env=dict(os.environ, PYTHONDONTWRITEBYTECODE='1'))
    for linha in (r.stdout or '').splitlines():
        if linha.startswith('<<<C>>>'):
            return json.loads(linha[len('<<<C>>>'):])
    print((r.stderr or '')[-800:])
    return []


DESCOBRIR = """
import json, os, sys
RAIZ = os.getcwd()
for p in ('coleta','leis','regras','guarda','medidas','ferramentas',''):
    sys.path.insert(0, os.path.join(RAIZ, p) if p else RAIZ)
import _gavetas                                                 # noqa: F401
import ingresso as ing
import scrap_colheita as sc
sys.path.insert(0, os.path.join(RAIZ, 'provas'))
import _e2e02_janela_dois_posts as falso
fora = []
for item in falso.ITENS:
    u = sc.unidade(item, run_id='DESCOBERTA', fonte='IT-T9-001')
    f = ing.ficha(u, corrida={'RUN_ID': 'DESCOBERTA'}, raiz=RAIZ)
    fora.append(f.STORAGE_LOCATION)
print('<<<C>>>' + json.dumps(fora))
"""


def medir(url, a, arvore):
    q = _e2e.q
    obs = q(url, "select id, attempts, storage_object_id from raw_asset "
                 "where run_id = '%s' order by id" % a)
    fechadas = int(q(url,
                     "select count(*) from raw_asset ra "
                     "join collection_run cr on cr.run_id = ra.run_id "
                     "join storage_object so on so.id = ra.storage_object_id "
                     "where ra.run_id = '%s' and so.sha256 = ra.sha256" % a)[0][0])
    return {
        'raw': len(obs),
        'raw_total': int(q(url, 'select count(*) from raw_asset')[0][0]),
        'obj': int(q(url, 'select count(*) from storage_object')[0][0]),
        'run_rows': int(q(url, "select count(*) from collection_run "
                               "where run_id = '%s'" % a)[0][0]),
        'id_do_A': obs[0][0] if obs else None,
        'attempts_do_A': int(obs[0][1]) if obs and obs[0][1] else None,
        'sem_objeto': len([o for o in obs if not o[2]]),
        'linhagem_fechada': fechadas,
        'etapas': q(url, "select etapa, tentativa, estado from "
                         "etapa_da_corrida where run_id = '%s' order by id" % a),
    }


if __name__ == '__main__':
    raise SystemExit(main())
