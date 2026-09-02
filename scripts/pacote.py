#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PONTO DE ENTRADA ÚNICO DO PACOTE — roda todas as camadas em UM processo.

    python3 scripts/pacote.py

⚠️ POR QUE EXISTE, e é um defeito que o próprio validador pegou
----------------------------------------------------------------
O contador de ID (`novo_id`) é estado de MÓDULO. Rodando as camadas em quatro processos
separados, cada um recomeça do 001 — e `IT-PER-001` nasceu duas vezes, uma em
`SCIENCE/researchers.json` e outra em `PEOPLE/people.json`.

    CONTADOR GLOBAL EXIGE PROCESSO ÚNICO. Não é preferência de estilo: é a condição
    para o ID ser estável, e ID instável quebra toda a camada de relações.

A correção certa não era renomear prefixo — isso esconderia a colisão em vez de
resolvê-la. É rodar tudo junto, na ordem de dependência.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from pacote_normalizar import camada_adama, DR                      # noqa: E402
from pacote_camadas import camada_vozes, camada_competidor, camada_ciencia   # noqa: E402
from pacote_camadas2 import (camada_fontes, camada_janelas,          # noqa: E402
                             camada_oportunidades, camada_futuro)
from pacote_camadas3 import (camada_noticias, camada_eventos,        # noqa: E402
                             camada_pessoas, camada_acervo)
from pacote_fenologia import camada_fenologia                    # noqa: E402
from pacote_mercado import camada_mercado                        # noqa: E402
from pacote_convergencia import camada_convergencia              # noqa: E402

TMP = os.path.join(os.path.dirname(HERE), '.tmp')

ORDEM = [
    ('FONTES', camada_fontes),          # primeiro: todo o resto referencia SOURCE_ID
    ('ADAMA', camada_adama),
    ('CIENCIA', camada_ciencia),
    ('PESSOAS', camada_pessoas),
    ('VOCI DAL CAMPO', camada_vozes),
    ('COMPETITOR', camada_competidor),
    ('JANELAS', camada_janelas),
    ('OPORTUNIDADES', camada_oportunidades),
    ('FUTURO', camada_futuro),
    ('NOTICIAS', camada_noticias),
    ('EVENTOS', camada_eventos),
    ('ACERVO', camada_acervo),
    # ⚠️ Estas duas vem de artefato de leque, e por um instante eu as chamei por
    # SUBPROCESSO — o que reintroduziria exatamente o bug que este arquivo existe para
    # impedir: processo novo, contador de ID novo. Aqui elas sao FUNCAO importada, como
    # todas as outras. UM PROCESSO, UM CONTADOR.
    ('FENOLOGIA CORRENTE', lambda: camada_fenologia(
        os.path.join(TMP, 'madrugada.json'))),
    ('MARKET PULSE', lambda: camada_mercado(os.path.join(TMP, 'mkt.json'))),
    # A convergencia vem POR ULTIMO: ela le o rotulo e a conversa, e as duas
    # precisam ja ter passado pelo contador de ID.
    ('CONVERGENCIA', camada_convergencia),
]


def main():
    os.makedirs(DR, exist_ok=True)
    for nome, fn in ORDEM:
        print('CAMADA %s' % nome)
        fn()
    print('\ntodas as camadas em um processo — contador de ID compartilhado')
    return 0


if __name__ == '__main__':
    sys.exit(main())
