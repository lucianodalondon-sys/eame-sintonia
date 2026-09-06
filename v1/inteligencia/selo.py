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


def conteudo_sha(saida):
    """sha256 do CONTEUDO da saida, com o proprio selo de fora.

    O selo do produtor prova que o JSON saiu deste codigo. Nao prova que ninguem
    mexeu no JSON depois. O teste de mutacao da rodada 4 inverteu, a mao, oito
    vereditos de oito regras diferentes — com os cabecalhos de contagem
    ajustados junto — e os 27 portoes, os 50 testes de render e os 12 de ruido
    continuaram verdes. Tambem calou o portao de celula aberta subindo, no mesmo
    arquivo, o teto contra o qual ele comparava.

    Com o sha do conteudo, qualquer edicao a mao num artefato selado e detectada
    pelo portao ARTIFACTS_MATCH_THE_CODE_THAT_MADE_THEM. Continua sendo possivel
    recalcular o sha depois de editar — mas ai nao e mais uma edicao discreta:
    e reescrever o selo, e isso aparece no diff.
    """
    import json
    corpo = {k: v for k, v in saida.items() if k != 'PRODUCED_BY'}
    return hashlib.sha256(
        json.dumps(corpo, ensure_ascii=False, sort_keys=True,
                   separators=(',', ':')).encode()).hexdigest()


def gravar(saida, caminho):
    """Sela o conteudo e grava. Substitui o json.dump direto dos modulos."""
    import json
    if isinstance(saida.get('PRODUCED_BY'), dict):
        saida['PRODUCED_BY']['CONTENT_SHA256'] = conteudo_sha(saida)
    d = os.path.dirname(caminho)
    if d:
        os.makedirs(d, exist_ok=True)
    with open(caminho, 'w', encoding='utf-8') as fh:
        json.dump(saida, fh, ensure_ascii=False, indent=1)
