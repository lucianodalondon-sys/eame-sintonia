#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""O RED TEAM PEGA O CÓDIGO DE ONTEM? · a travessia que prova a prova.

    python3 scripts/v21_regressao_do_red_team.py

Um red team que passa na primeira execução prova pouco: pode estar a medir o
que já estava certo. Este script põe o código ANTERIOR de volta em memória —
`git show <commit>:scripts/...` para um diretório de rascunho — e passa por ele
as mesmas orações. Se o código de ontem passar, o red team não vale nada.

    UM TESTE QUE NÃO REPROVA A VERSÃO ANTIGA NÃO ESTÁ A TESTAR NADA.

O que ele reproduz, com as frases REAIS do acervo:

1 · «reporta terceiro voo de Cydia pomonella terminado com danos em aumento»
    virava `PEST_STAGE_WINDOW`. O boletim RELATA o inseto; não diz quando tratar.
2 · e essa janela falsa saía com o método `CONDICAO_EXIGE_MEDICAO_QUE_NAO_TEMOS`
    sobre um documento que declarava a medição em letras.
3 · «siamo nella fase conclusa della difesa» ABRIA a janela, porque o padrão de
    presente lia «siamo nella fase» e não lia «conclusa».
4 · «il quadro rimane tendenzialmente buono» chegava ao mesmo lugar que o
    silêncio total — a fonte falar e a fonte calar davam a mesma frase.
"""
import os
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
COMMIT = os.environ.get('RED_TEAM_ANTES', '4b97cf5')
MODULOS = ('v21_normalizar', 'v21_necessidade', 'v21_janelas')

# As orações são REAIS: saem de IT-CAN-D9582B1FD6, IT-COL-2609-VN-CARPOCAPSA e
# IT-COL-2609-RE-TIGNOLETTA, que estão no pacote de hoje.
VOO = ('O boletim frutticolo do Veneto declara terminada a colheita das '
       'variedades do grupo Gala e reporta terceiro voo de Cydia pomonella '
       'terminado com danos em aumento tambem em pomares de manejo integrado.')
CONCLUSA = 'siamo nella fase conclusa della difesa'
QUADRO = ('o quadro a nivel territorial permanece tendencialmente bom na '
          'generalidade dos casos, com excecoes')


def _antigo(tmp):
    """Escreve os módulos do commit ANTES no rascunho e importa-os de lá."""
    for m in MODULOS:
        alvo = os.path.join(tmp, m + '.py')
        with open(alvo, 'wb') as f:
            f.write(subprocess.check_output(
                ['git', 'show', '%s:scripts/%s.py' % (COMMIT, m)], cwd=ROOT))
    sys.path.insert(0, tmp)
    for m in MODULOS:
        sys.modules.pop(m, None)
    import v21_janelas as velho          # noqa: E402  — o do rascunho
    return velho


def main():
    import v21_janelas as novo
    achados, falhas = [], []
    with tempfile.TemporaryDirectory() as tmp:
        velho = _antigo(tmp)
        assert os.path.dirname(velho.__file__) == tmp, 'importou o modulo de hoje'

        # 1 · o voo relatado virava janela
        tipos_v = [t for t, _p in velho.tipos_da_oracao(VOO)]
        tipos_n = [t for t, _p in novo.tipos_da_oracao(VOO)]
        achados.append(('voo relatado vira janela?', tipos_v, tipos_n))
        if 'PEST_STAGE_WINDOW' not in tipos_v:
            falhas.append('o codigo antigo NAO produzia a janela falsa — '
                          'o defeito nao esta reproduzido')
        if 'PEST_STAGE_WINDOW' in tipos_n:
            falhas.append('o codigo de hoje ainda produz a janela falsa')

        # 2 · e com que razão ela saía
        av, mv = velho.aberta_agora('PEST_STAGE_WINDOW', VOO, None, True)
        an, mn = novo.aberta_agora('PEST_STAGE_WINDOW', VOO, None, True)
        achados.append(('razao do UNKNOWN', (av, mv), (an, mn)))
        if mv != 'CONDICAO_EXIGE_MEDICAO_QUE_NAO_TEMOS':
            falhas.append('a razao falsa nao esta reproduzida')
        if mn == 'CONDICAO_EXIGE_MEDICAO_QUE_NAO_TEMOS':
            falhas.append('o codigo de hoje ainda acusa falta de medicao')

        # 3 · «fase conclusa» abria a janela
        av, mv = velho.aberta_agora('PHENOLOGY_WINDOW', CONCLUSA, None, True)
        an, mn = novo.aberta_agora('PHENOLOGY_WINDOW', CONCLUSA, None, True)
        achados.append(('fase conclusa abre?', (av, mv), (an, mn)))
        if av != 'YES':
            falhas.append('o buraco do padrao de presente nao esta reproduzido')
        if an == 'YES':
            falhas.append('o codigo de hoje ainda abre em «fase conclusa»')

        # 4 · falar em prosa e calar davam a mesma frase
        _av, mv = velho.aberta_agora('THRESHOLD_WINDOW', QUADRO, None, True)
        _ax, mx = velho.aberta_agora('THRESHOLD_WINDOW', 'x', None, True)
        _an, mn = novo.aberta_agora('THRESHOLD_WINDOW', QUADRO, None, True)
        _ay, my = novo.aberta_agora('THRESHOLD_WINDOW', 'x', None, True)
        achados.append(('prosa qualitativa distingue-se do silencio?',
                        mv == mx and 'NAO', mn != my and 'SIM'))
        if mv != mx:
            falhas.append('a confusao entre prosa e silencio nao esta reproduzida')
        if mn == my:
            falhas.append('o codigo de hoje ainda confunde prosa com silencio')

    print('ANTES = %s   ·   DEPOIS = arvore de trabalho\n' % COMMIT)
    for titulo, antes, depois in achados:
        print('── %s' % titulo)
        print('   antes  : %s' % (antes,))
        print('   depois : %s' % (depois,))
    print('\nFALHAS: %s' % (falhas or 'nenhuma'))
    print('REGRESSAO_DO_RED_TEAM = %s' % ('PASS' if not falhas else 'FAIL'))
    return 0 if not falhas else 1


if __name__ == '__main__':
    sys.exit(main())
