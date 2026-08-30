#!/usr/bin/env python3
"""
MIGRAÇÃO PARA FRAGMENTOS COM DONO — uma vez, e reexecutável sem estragar nada.

    python3 scripts/runs_migrar.py --dry-run     # mostra o que faria
    python3 scripts/runs_migrar.py --aplicar     # escreve os fragmentos e reconcilia
    python3 scripts/runs_migrar.py --provar      # só a prova de isolamento

O QUE ELA FAZ
--------------
Lê as execuções que já existem no `RUN-MANIFEST.json` global, deriva o `DATASET_OWNER` de
cada uma pela MISSÃO, e escreve um fragmento por execução em `data/runs/<DONO>/`.

O QUE ELA NÃO FAZ, E ISSO IMPORTA
-----------------------------------
Não apaga o manifesto global, não altera nenhum campo além de acrescentar o dono, e não
toca em arquivo de outra missão. O global continua existindo — só deixa de ser o lugar
onde duas missões escrevem ao mesmo tempo.

É **idempotente**: rodar duas vezes escreve o mesmo conteúdo nos mesmos caminhos. Um
retrofit que não pode ser repetido vira uma operação que ninguém ousa refazer.

POR QUE `UNDECLARED_OWNER` NÃO É ERRO DE EXECUÇÃO
---------------------------------------------------
Missão que ainda não está em `pv.DONOS` sai como `UNDECLARED_OWNER`, o fragmento é escrito
na pasta dela, e o portão fica vermelho até alguém registrar o dono. O dado nunca se perde
por causa de metadado faltando — a lei aqui é a mesma que vale para coleta paga.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import proveniencia as pv  # noqa: E402


def plano():
    """→ lista de (run, dono, caminho). Deriva; não escreve."""
    fora = []
    for rid, r in sorted(pv.carregar().items()):
        dono = r.get('DATASET_OWNER')
        if dono in (None, '', pv.NOT_PRESERVED):
            dono = pv.dono_da_missao(r.get('MISSION'))
        r = dict(r, DATASET_OWNER=dono)
        # Campo novo no contrato: execução antiga não o tinha, e o retrofit é justamente
        # dar-lhe um. Os demais campos ausentes viram NOT_PRESERVED, nunca somem.
        for c in pv.CAMPOS_RUN:
            r.setdefault(c, pv.NOT_PRESERVED)
        fora.append((r, dono, pv.caminho_fragmento(r)))
    return fora


def aplicar(escrever):
    escritos, por_dono = [], {}
    for r, dono, caminho in plano():
        por_dono[dono] = por_dono.get(dono, 0) + 1
        if escrever:
            escritos.append(pv.gravar_fragmento(r))
        else:
            escritos.append(os.path.relpath(caminho, ROOT).replace('\\', '/'))
    return escritos, por_dono


def provar():
    """A prova que o contrato pede, derivada de leitura real dos dois conjuntos."""
    iso = pv.isolamento('EARLY_SIGNAL_EAME', 'CREATOR_MAP_EAME')
    presentes = pv.donos_presentes()
    # Um run do Early Signal não pode aparecer ao carregar o Creator Map, e vice-versa.
    # Também não pode existir RUN_ID em dois donos: isso seria a mesma execução com dois
    # proprietários, que é o estado que o contrato proíbe.
    orfaos = {}
    for dono in presentes:
        meus = pv.carregar_fragmentos(dono)
        outros = {k: v for k, v in pv.carregar_fragmentos().items() if k not in meus}
        orfaos[dono] = [k for k, v in outros.items() if v['DATASET_OWNER'] == dono]
    return {
        'DONOS_PRESENTES': presentes,
        'ISOLAMENTO_EARLY_SIGNAL_x_CREATOR_MAP': iso,
        'ORFAOS_POR_DONO': orfaos,
        'PASS': bool(iso['ISOLATED'] and not any(orfaos.values())),
    }


if __name__ == '__main__':
    if '--provar' in sys.argv:
        p = provar()
        print('DONOS_PRESENTES:', p['DONOS_PRESENTES'])
        i = p['ISOLAMENTO_EARLY_SIGNAL_x_CREATOR_MAP']
        print('%s=%d  %s=%d  compartilhados=%s  contaminados=%s/%s'
              % (i['OWNER_A'], i['RUNS_A'], i['OWNER_B'], i['RUNS_B'],
                 i['SHARED_RUN_IDS'] or 'nenhum',
                 len(i['A_CONTAMINATED_BY_OTHER_OWNER']),
                 len(i['B_CONTAMINATED_BY_OTHER_OWNER'])))
        print('DATASET_OWNER_INFRASTRUCTURE =', 'PASS' if p['PASS'] else 'FAIL')
        raise SystemExit(0 if p['PASS'] else 1)

    escrever = '--aplicar' in sys.argv
    escritos, por_dono = aplicar(escrever)
    print('%s %d execucoes' % ('ESCREVI' if escrever else 'ESCREVERIA', len(escritos)))
    for d, n in sorted(por_dono.items()):
        print('  %-24s %d' % (d, n))
    if escrever:
        pv.reconciliar('2026-08-30')
        print('indice global RECONCILIADO a partir dos fragmentos')
    else:
        print('(dry-run — nada foi escrito)')
