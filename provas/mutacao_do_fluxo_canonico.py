#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SCRAP-FLOW-01 — A MUTAÇÃO DIZ SE O CAMINHO ESTÁ MESMO GUARDADO.

    py provas/mutacao_do_fluxo_canonico.py

Vinte e duas sentinelas verdes só provam que elas passaram. A pergunta é:

    SE EU PARTIR O CAMINHO, ALGUMA FICA VERMELHA?

Muta-se uma CÓPIA da árvore. A árvore real não é tocada.

    APIFY_RUNS = 0 · REAL_NETWORK = 0 · COST_USD = 0
"""
import os
import shutil
import subprocess
import sys
import tempfile

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BATERIAS = ('tests.test_scrap_flow01_caminho_canonico',)

WF = '.github/workflows/sintonia-scrap.yml'
REC = 'pedido/receitas.py'
ORQ = 'orquestrador/orquestrador.py'
ADP = 'coleta/scrap_colheita.py'
ING = 'coleta/ingresso.py'
DONO = 'coleta/coletor.py'

MUTACOES = [
    ('M1 · o workflow volta a chamar o script direto', WF,
     '              PYTHONIOENCODING=utf-8 $PY orquestrador/orquestrador.py \\\n'
     '                "colete concorrentes" \\\n'
     '                --filtro fase="${{ inputs.fase }}" \\\n'
     '                --filtro pais=IT \\\n'
     '                --filtro fonte="${{ inputs.fonte }}" ;;',
     '              PYTHONIOENCODING=utf-8 $PY coleta/social_scrap.py \\\n'
     '                coletar "${{ inputs.fase }}" $TETO ;;',
     'a fase migrada nao chama mais o script'),

    ('M2 · o disparador passa a nomear o ator', WF,
     '                --filtro fonte="${{ inputs.fonte }}" ;;',
     '                --filtro fonte="${{ inputs.fonte }}" \\\n'
     '                --filtro adaptador=instagram_janela ;;',
     'o disparador nao conhece ator nem rota'),

    # Renomear o `id` era um mutante fraco: o executor continuava a correr, so
    # com outro nome. Este TIRA-O do registo, que e a mudanca real.
    ('M3 · o executor do SCRAP sai do registo', REC,
     '        "roda": ["coleta/scrap_colheita.py"],',
     '        "roda": ["coleta/social_scrap.py", "coletar"],',
     'o pedido chega ao executor do SCRAP'),

    ('M4 · o adapter passa a cunhar a propria corrida', REC,
     '        "recebe_run_id": True,\n'
     '        # A fonte DESCE COM O PEDIDO.',
     '        "recebe_run_id": False,\n'
     '        # A fonte DESCE COM O PEDIDO.',
     'o adapter recebe a corrida, nao a cunha'),

    ('M5 · a porta volta a agarrar a primeira lista', ORQ,
     '    envelope = _envelope_declarado(e, run_id)\n'
     '    if envelope is not None:',
     '    envelope = None\n'
     '    if envelope is not None:',
     'a heuristica morreu'),

    ('M6 · o suporte passa a atravessar a porta', 'leis/retorno_da_coleta.py',
     'ENTRAM_NO_INGRESSO = (COLHEITA,)',
     'ENTRAM_NO_INGRESSO = ESPECIES',
     'so a colheita atravessa'),

    ('M7 · o estagio deixa de atravessar o ingresso', ORQ,
     '    a_julgar = entrados if entrados else itens',
     '    a_julgar = itens',
     'o item que sai do ingresso nao e o que entrou'),

    ('M8 · o adapter fabrica SOURCE_ID a partir da conta', ADP,
     "    if not fonte:",
     "    fonte = fonte or objetos and objetos[0].get('SOURCE_ACCOUNT')\n"
     "    if not fonte:",
     'URL e handle nao sao SOURCE_ID'),

    ('M9 · o DOCUMENT_ID passa a vir do sha', ADP,
     "            'DOCUMENT_ID': rc.NAO_SEI}",
     "            'DOCUMENT_ID': str(objeto.get('NATIVE_ID') or '')}",
     'o DOCUMENT_ID nao se fabrica'),

    ('M10 · o RAW_OBSERVATION_ID passa a vir do caminho', ING,
     '            "RAW_OBSERVATION_ID": NAO_SEI_ID,',
     '            "RAW_OBSERVATION_ID": f.STORAGE_LOCATION,',
     'RAW_OBSERVATION_ID = raw_asset.id'),

    ('M11 · a guarda de gasto sai da primitiva', DONO,
     '    recibo = az.pode_comprar(modo=modo, autorizacao=autorizacao,\n'
     '                             source_id=source_id, proposito=proposito,\n'
     '                             ator=actor)',
     "    recibo = {'CAN_START_PAID_EXECUTION': True, 'MODE': modo,\n"
     "              'BASIS': 'NENHUMA', 'PROMOTES_RELEVANCE': False}",
     'os controlos de gasto continuam no caminho'),

    ('M12 · o adapter passa a autorizar gasto sozinho', ADP,
     "EXECUTOR_ID = 'scrap-colheita'",
     "AUTORIZACAO_HUMANA = 'o adapter autoriza-se'\n"
     "EXECUTOR_ID = 'scrap-colheita'",
     'o adapter nao mexe em autorizacao'),

    ('M13 · o orquestrador passa a conhecer a plataforma', ORQ,
     'PRONTOS = RAIZ / "data" / "samples" / "PRONTO-PARA-INTELIGENCIA"',
     'PRONTOS = RAIZ / "data" / "samples" / "PRONTO-PARA-INTELIGENCIA"\n'
     'PLATAFORMA_PADRAO = "INSTAGRAM"',
     'o orquestrador nao conhece a plataforma'),

    ('M14 · um classificador tematico entra no SCRAP', ADP,
     "DESCONHECIDO = 'UNKNOWN'",
     "DESCONHECIDO = 'UNKNOWN'\nTEMA_T9 = 'relevancia comercial'",
     'nenhum classificador tematico no SCRAP'),

    # O `if itens else []` era um no-op: `itens` e sempre verdadeiro aqui.
    # Este substitui mesmo o juiz.
    ('M15 · a admissao passa a ser fingida', ORQ,
     '    decisoes = [adm.decidir(x, universo, corrida=run_id) for x in itens]',
     '    class _Sim:\n'
     '        resultado = adm.SIM\n'
     '        porque = "fingido"\n'
     '    decisoes = [_Sim() for _ in itens]',
     'a admissao nao e mockada'),

    ('M16 · a fase deixa de escolher o executor', REC,
     '        execs.sort(key=lambda e: 0 if fase in (e.get("serve_fases") or [fase]) else 1)',
     '        pass',
     'o pedido escolhe quem o atende'),

    ('M17 · o legado volta a poder declarar colheita', 'leis/retorno_da_coleta.py',
     '        if especie == COLHEITA:',
     '        if False:',
     'o legado so declara suporte'),

    ('M18 · o envelope deixa de ser conferido', ORQ,
     '        mal = rc.conferir(envelope, str(RAIZ))',
     '        mal = []',
     'um envelope que quebra o contrato nao entrega'),
]


def _copia(destino):
    pesadas = {'.git', 'data', 'node_modules', 'italia-portale', '__pycache__',
               '.tmp', 'build'}
    for nome in os.listdir(RAIZ):
        if nome in pesadas:
            continue
        o, a = os.path.join(RAIZ, nome), os.path.join(destino, nome)
        if os.path.isdir(o):
            shutil.copytree(o, a, symlinks=True,
                            ignore=shutil.ignore_patterns('__pycache__',
                                                          'node_modules'))
        else:
            shutil.copy2(o, a)
    for nome in ('.git', 'data'):
        os.symlink(os.path.join(RAIZ, nome), os.path.join(destino, nome))


def _correr(arvore):
    p = subprocess.run([sys.executable, '-m', 'unittest'] + list(BATERIAS),
                       cwd=arvore, capture_output=True, text=True)
    return p.returncode, (p.stdout or '') + (p.stderr or '')


def main():
    print('SCRAP-FLOW-01 · MUTAÇÃO DO CAMINHO CANÔNICO')
    print('=' * 74)
    base = tempfile.mkdtemp(prefix='flow01-mut-')
    arvore = os.path.join(base, 'arvore')
    os.makedirs(arvore)
    try:
        _copia(arvore)
        codigo, saida = _correr(arvore)
        if codigo != 0:
            print('A CÓPIA JÁ NASCE VERMELHA — a mutação não mediria nada.')
            print(saida[-2500:])
            return 3
        print('cópia limpa: bateria VERDE\n')

        sobreviventes = []
        for nome, rel, velho, novo, garantia in MUTACOES:
            alvo = os.path.join(arvore, rel)
            with open(alvo, encoding='utf-8') as f:
                original = f.read()
            if velho not in original:
                print('%-54s ALVO_AUSENTE' % nome[:54])
                sobreviventes.append((nome, 'ALVO_AUSENTE'))
                continue
            with open(alvo, 'w', encoding='utf-8') as f:
                f.write(original.replace(velho, novo, 1))
            try:
                codigo, saida = _correr(arvore)
            finally:
                with open(alvo, 'w', encoding='utf-8') as f:
                    f.write(original)
            morta = codigo != 0
            quantas = saida.count('FAIL: ') + saida.count('ERROR: ')
            print('%-54s %s (%d sentinelas)'
                  % (nome[:54], 'MORTA  ' if morta else 'SOBREVIVE', quantas))
            print('%-54s   guarda: %s' % ('', garantia))
            if not morta:
                sobreviventes.append((nome, garantia))

        print('=' * 74)
        print('MUTANTS   = %d' % len(MUTACOES))
        print('SURVIVORS = %d' % len(sobreviventes))
        for nome, porque in sobreviventes:
            print('  SOBREVIVEU · %s — ninguém guarda: %s' % (nome, porque))
        return 0 if not sobreviventes else 1
    finally:
        shutil.rmtree(base, ignore_errors=True)


if __name__ == '__main__':
    sys.exit(main())
