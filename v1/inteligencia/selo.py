#!/usr/bin/env python3
"""
selo.py — o artefato diz QUAL CODIGO o produziu.

## O defeito que isto fecha

Os portoes leem `v1/dados/*.json` como fonte de verdade e nenhum recomputa o
veredito. A consequencia foi medida por teste de mutacao na rodada 4, e e a
pior de todas:

  * `heranca_validar.py` (R-15) passou a estourar TypeError na primeira linha
    util — porque `celula()` ganhou um parametro e o chamador nao acompanhou — e
    os 25 portoes continuaram VERDES, certificando o `HERANCA-CHECK.json` da
    execucao anterior. O erro existia; o que faltava era o teste.
  * Um `raise` posto de proposito logo apos os imports de R-15 tem o mesmo
    efeito: 25/25, 50/50, 12/12, sobre um artefato velho.

"Nao declare sucesso por ausencia de erro" nao basta quando o erro acontece num
processo que ninguem observa. O artefato tem de dizer de onde veio.

## A regra

Cada modulo grava, na propria saida, o nome e o sha256 do ARQUIVO DE CODIGO que
a produziu. O portao `ARTIFACTS_MATCH_THE_CODE_THAT_MADE_THEM` recalcula o
sha256 do modulo em disco e compara. Se alguem mexeu no modulo e nao rodou de
novo — ou se o modulo quebrou e a saida ficou velha — o portao cai e diz qual.

Isto NAO prova que o modulo esta certo. Prova que o JSON servido saiu DESTE
codigo, que e a pergunta que nenhum portao fazia.
"""
import hashlib, os


def selo(arquivo_do_modulo):
    """{'MODULE': nome, 'MODULE_SHA256': sha} do arquivo de codigo dado.

    Uso: `'PRODUCED_BY': selo(__file__)` no dicionario de saida.
    """
    cam = os.path.abspath(arquivo_do_modulo)
    try:
        with open(cam, 'rb') as fh:
            sha = hashlib.sha256(fh.read()).hexdigest()
    except OSError:
        return {'MODULE': os.path.basename(cam), 'MODULE_SHA256': 'NOT_READABLE'}
    return {'MODULE': os.path.basename(cam), 'MODULE_SHA256': sha}
