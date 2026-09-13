#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SCRAP-E2E-03 — A REPETIÇÃO, MEDIDA. E O QUE ELA REVELA SOBRE O ENDEREÇO.

    BANCO_DESCARTAVEL_URL=postgresql://postgres@127.0.0.1:5433/descartavel \\
        python3 provas/a_repeticao_do_scrap.py

A PERGUNTA
----------
    CORRER A MESMA COLHEITA DUAS VEZES — O QUE A CASA FAZ?
    REAPROVEITA, DUPLICA, RECUSA, OU NENHUMA DAS TRÊS?

    REUSED != PASSED != REJECTED != ERROR != NOT_RUN.
    E «não deu conflito» não é nenhuma delas: é a ausência de resposta.

O QUE ESTA PROVA MEDE, E NÃO CONSERTA
--------------------------------------
Ela corre a MESMA fonte falsa DUAS vezes, na MESMA árvore e contra o MESMO
banco, e depois pergunta ao banco quantas corridas, quantas observações e
quantos objetos ficaram lá. Depois compara os DOIS brutos preservados campo a
campo, e NOMEIA o campo que difere.

    MEASURE != FIX. Esta prova fecha com um número, e não com um conserto.

O QUE ELA JÁ ENCONTROU, E ESTÁ AQUI PARA NÃO SE PERDER
--------------------------------------------------------
Os dois brutos diferem em UM campo só, e esse campo é `RUN_ID`. O bruto
preservado carrega, dentro dele, o nome da corrida que o trouxe — escrito por
`coleta/ingresso.py`, e assim desde antes desta integração (`974e39a6`).

A consequência não é pequena, e não é um defeito disfarçado de detalhe:

    O SHA DE UM BRUTO NUNCA IDENTIFICA O CONTEÚDO OBSERVADO.
    IDENTIFICA A OBSERVAÇÃO.

Daí sai tudo o resto. Duas observações do MESMO facto externo são, para o
armazém, dois conteúdos diferentes. O endereço por conteúdo nunca colide, e
por isso:

    DEDUPLICAÇÃO POR CONTEÚDO QUE NUNCA COLIDE NÃO É DEDUPLICAÇÃO:
    É UM NOME NOVO DE CADA VEZ.

E o conflito que `provas/objeto_e_observacao_no_postgres.py` documenta no caso
`H` — a segunda corrida do mesmo conteúdo a bater na trava — não acontece
nesta rota. NÃO porque esteja curado: porque é inalcançável.

    UM PERIGO INALCANÇÁVEL NÃO É UM PERIGO RESOLVIDO.
    E UMA TRAVA QUE NUNCA É TOCADA NÃO ESTÁ PROVADA.

É defensável — `RAW_OBSERVATION_ID = raw_asset.id, E MAIS NADA`, e a casa já
escreveu que SHA IDENTIFICA BYTES E NÃO IDENTIFICA DOCUMENTO. O que NÃO é
defensável é isto ficar por dizer: quem correr uma coleta grande precisa de
saber, ANTES, que o armazém cresce com o número de corridas e não com o
número de factos.

    UMA CAPACIDADE DECLARADA A MEIO DE UMA COLHEITA GRANDE
    JÁ NÃO É UMA DECISÃO: É UMA CONTA.

O QUE ELA NÃO MEDE, DITO COM NOME
----------------------------------
Não mede crash a meio (isso é de `provas/a_unidade_pousa_na_espera.py`), nem
concorrência de duas corridas ao mesmo segundo (isso é de
`provas/as_corridas_nao_se_cruzam.py`), nem retry com `tentativa` a subir.

    REAL_NETWORK = 0 · PAID_USD = 0 · LIVE_READS = 0 · LIVE_WRITES = 0
"""
import json
import os
import shutil
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

import sala_de_espera as espera    # noqa: E402

FALHAS = []
SHIM = os.path.join(RAIZ, 'provas', '_e2e01_janela_admissivel.py')


def diz(ok, titulo, detalhe=''):
    print('  %-5s %-50s %s' % ('ok' if ok else 'FALHA', titulo[:50],
                               str(detalhe)[:58]))
    if not ok:
        FALHAS.append(titulo)


def achata(o, p=''):
    """Um dicionário em pares (caminho, valor). Para comparar SEM adivinhar."""
    if isinstance(o, dict):
        for k, v in o.items():
            yield from achata(v, p + '/' + str(k))
    elif isinstance(o, list):
        for i, v in enumerate(o):
            yield from achata(v, p + '/[%d]' % i)
    else:
        yield p, o


def main():
    url = os.environ.get('BANCO_DESCARTAVEL_URL')
    if not url:
        print('FALTA BANCO_DESCARTAVEL_URL — e SKIP != PASS.')
        print('REPETICAO_DO_SCRAP=NOT_MEASURED')
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

    base = tempfile.mkdtemp(prefix='scrap-repete-')
    arvore = os.path.join(base, 'arvore')
    os.makedirs(arvore)
    try:
        # A MESMA árvore nas duas voltas, de propósito. Duas árvores dariam
        # dois armazéns, e dois armazéns nunca colidem por construção — o que
        # tornaria a pergunta desta prova impossível de responder.
        _e2e.com_este_falso(arvore, SHIM)
        sala = os.path.join(arvore, 'data', 'samples',
                            'PRONTO-PARA-INTELIGENCIA')
        antes_sala = set(os.listdir(sala)) if os.path.isdir(sala) else set()
        antes = {t: int(_e2e.q(url, 'select count(*) from ' + t)[0][0])
                 for t in ('collection_run', 'raw_asset', 'storage_object')}

        voltas = []
        for _ in (1, 2):
            recibo, env, _idas = _e2e.correr_com_banco(arvore, _e2e.FONTE, url)
            rid = (recibo or {}).get('RUN_ID') or ''
            a = rid.replace("'", "''")
            linhas = _e2e.q(url, "select id, sha256, storage_object_id, "
                                 "storage_path from raw_asset where "
                                 "run_id = '%s'" % a) if rid else []
            voltas.append({'RUN_ID': rid, 'STATUS': (recibo or {}).get('STATUS'),
                           'LINHAS': linhas, 'ENV': env,
                           'ADMISSAO': (recibo or {}).get('ADMISSAO') or {}})

        v1, v2 = voltas
        print('\n1 · AS DUAS VOLTAS CORRERAM, E SÃO DUAS')
        diz(v1['STATUS'] == 'SUCCESS' and v2['STATUS'] == 'SUCCESS',
            'as duas correram', '%s · %s' % (v1['STATUS'], v2['STATUS']))
        diz(bool(v1['RUN_ID']) and v1['RUN_ID'] != v2['RUN_ID'],
            'e cada uma ganhou o SEU RUN_ID', v2['RUN_ID'])

        print('\n2 · O QUE FICOU NO BANCO, CONTADO')
        depois = {t: int(_e2e.q(url, 'select count(*) from ' + t)[0][0])
                  for t in antes}
        for t in ('collection_run', 'raw_asset', 'storage_object'):
            print('      %-18s %d -> %d  (delta %+d)'
                  % (t, antes[t], depois[t], depois[t] - antes[t]))
        diz(depois['collection_run'] - antes['collection_run'] == 2,
            'duas corridas, duas linhas de corrida',
            depois['collection_run'] - antes['collection_run'])

        print('\n3 · REAPROVEITOU? A RESPOSTA MEDIDA, E NÃO A ESPERADA')
        sha1 = v1['LINHAS'][0][1] if v1['LINHAS'] else ''
        sha2 = v2['LINHAS'][0][1] if v2['LINHAS'] else ''
        obj1 = v1['LINHAS'][0][2] if v1['LINHAS'] else ''
        obj2 = v2['LINHAS'][0][2] if v2['LINHAS'] else ''
        reaproveitou = bool(sha1) and sha1 == sha2 and obj1 == obj2
        novos_objetos = depois['storage_object'] - antes['storage_object']
        print('      sha da volta 1 = %s' % sha1[:24])
        print('      sha da volta 2 = %s' % sha2[:24])
        print('      objeto 1 = %s · objeto 2 = %s' % (obj1, obj2))
        print('      REUSED = %s · STORAGE_OBJECTS_NOVOS = %d'
              % ('YES' if reaproveitou else 'NO', novos_objetos))

        print('\n4 · E PORQUÊ — O CAMPO QUE DIFERE, NOMEADO')
        # A pergunta que separa um facto de uma suposição. «Os shas diferem»
        # é o sintoma; o campo que difere é a causa, e ela tem dono.
        corpos = []
        for v in (v1, v2):
            cam = v['LINHAS'][0][3] if v['LINHAS'] else None
            if cam and os.path.isfile(os.path.join(arvore, cam)):
                with open(os.path.join(arvore, cam), encoding='utf-8') as f:
                    corpos.append(json.load(f))
        diferencas = []
        if len(corpos) == 2:
            da, db = dict(achata(corpos[0])), dict(achata(corpos[1]))
            diferencas = [k for k in sorted(set(da) | set(db))
                          if da.get(k) != db.get(k)]
        print('      campos que diferem: %d · %s'
              % (len(diferencas), diferencas or 'nenhum'))
        diz(len(corpos) == 2, 'os dois brutos leram-se do armazém',
            '%d de 2' % len(corpos))
        # ── A LEI QUE ESTA PROVA GUARDA ─────────────────────────────────
        # Não é «os shas têm de ser iguais» nem «têm de ser diferentes»: é que
        # a razão seja CONHECIDA. No dia em que alguém tirar o `RUN_ID` de
        # dentro do bruto, os shas passam a colidir, a trava do caso `H`
        # acorda, e esta linha reprova a dizer exatamente isso — que é o
        # aviso que se quer, e não um silêncio verde.
        esperado = ['/RUN_ID']
        diz(diferencas == esperado,
            'e diferem EXATAMENTE no `/RUN_ID`, e em mais nada',
            diferencas or 'iguais — o endereco passou a colidir')
        diz(not reaproveitou and novos_objetos == 2,
            'logo: REUSED = NO, e por construção, não por política',
            '%d objeto(s) novo(s)' % novos_objetos)

        print('\n5 · A SALA RECEBEU AS DUAS, E NÃO AS CONFUNDIU')
        agora_sala = set(os.listdir(sala)) if os.path.isdir(sala) else set()
        novos = sorted(x for x in (agora_sala - antes_sala)
                       if x.endswith('.json'))
        diz(len(novos) == 2, 'duas corridas, dois ficheiros na sala', novos)
        diz('%s.json' % v1['RUN_ID'] in novos
            and '%s.json' % v2['RUN_ID'] in novos,
            'e cada ficheiro tem o nome da SUA corrida', len(novos))

        print('\n6 · POUSAR OUTRA VEZ A MESMA CORRIDA É IDEMPOTENTE')
        # O último degrau da estrada tem de aguentar um retry. Duas leis, e
        # são diferentes: repetir o MESMO conteúdo não escreve nada e diz
        # `JA ESTAVA`; repetir com conteúdo DIFERENTE não escreve nada e
        # LEVANTA — porque UMA CORRIDA NÃO PODE CONTAR DUAS HISTÓRIAS.
        espera.MORADA = sala
        alvo = os.path.join(sala, '%s.json' % v1['RUN_ID'])
        with open(alvo, encoding='utf-8') as f:
            corpo = json.load(f)
        itens = list(corpo.get('ITENS') or [])
        antes_bytes = open(alvo, 'rb').read()
        r = espera.pousar(v1['RUN_ID'], itens)
        diz(r.get('ESTADO') == espera.JA_ESTAVA,
            'o mesmo conteúdo responde JA ESTAVA', r.get('ESTADO'))
        diz(open(alvo, 'rb').read() == antes_bytes,
            'e não reescreve um único byte', 'ficheiro intacto')
        outro = [dict(itens[0], TEXTO='outra coisa')] if itens else [{'x': 1}]
        try:
            espera.pousar(v1['RUN_ID'], outro)
            diz(False, 'conteúdo DIFERENTE na mesma corrida é recusado',
                'ACEITE — a corrida contou duas histórias')
        except espera.ConflitoDeCorrida as ex:
            diz(True, 'conteúdo DIFERENTE na mesma corrida é recusado',
                str(ex).split(':')[0][:50])
        diz(open(alvo, 'rb').read() == antes_bytes,
            'e o ficheiro anterior fica INTACTO depois da recusa',
            'intacto')

        print('\n' + '=' * 74)
        print('  REUSED                       = %s' % ('YES' if reaproveitou
                                                       else 'NO'))
        print('  RUNS                         = 2')
        print('  RAW_ROWS_NOVAS               = %d'
              % (depois['raw_asset'] - antes['raw_asset']))
        print('  STORAGE_OBJECTS_NOVOS        = %d' % novos_objetos)
        print('  CAMPO_QUE_DIFERE             = %s' % (diferencas or 'nenhum'))
        print('  CONTENT_ADDRESS_DEDUP        = UNREACHABLE '
              '(o bruto carrega o RUN_ID)')
        print('  DONO                         = coleta/ingresso.py '
              '(anterior a 974e39a6)')
        print('  SALA_FICHEIROS               = %d' % len(novos))
        print('  REAL_NETWORK = 0 · PAID_USD = 0')
        print('=' * 74)
        if FALHAS:
            print('FALHAS (%d):' % len(FALHAS))
            for f in FALHAS:
                print('   · %s' % f.strip())
            print('REPETICAO_DO_SCRAP=NO')
            return 1
        print('REPETICAO_DO_SCRAP=MEDIDA')
        return 0
    finally:
        shutil.rmtree(base, ignore_errors=True)


if __name__ == '__main__':
    raise SystemExit(main())
