#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""A AFIRMAÇÃO DA FONTE — o contrato das leis que a Puglia ensinou (D112).

    A FICHA NÃO ACRESCENTA NEM CORTA.
    O NOME DA PRAGA NÃO ESTÁ NO TRECHO SÓ PORQUE ESTÁ NA PÁGINA.

POR QUE ISTO EXISTE
-------------------
O laboratório da Puglia pôs fichas reais diante do dono, e ele respondeu à mão
(D111). O veredito (D112) foi «aprovado com correções», e as correções viraram
lei: `COL-LAW-221` (procedência da entidade), `COL-LAW-222` (fidelidade da
afirmação), `COL-LAW-223` (espécie da afirmação), e do lado da Intelligence
`INT-LAW-078` / `INT-LAW-079` (relações entre afirmações). O vocabulário de
LOCATION_SOURCE (`COL-LAW-032`) mora em `leis/lugar_do_fato.py`, que é o dono
da geografia — não aqui.

O QUE ISTO É, E O QUE NÃO É
---------------------------
É o VOCABULÁRIO e as TRAVAS dessas leis, mais um lint determinístico que
reprova uma ficha infiel. NÃO é um extrator: nada aqui lê um boletim e propõe
entidade, lugar ou espécie. Quem extrai, para os boletins, é
`leis/boletim_do_campo.ler_afirmacao` (BOLETIM-POR-SECAO): desde o
LOTE6-INTEGRA ele lê `ENTITY_SOURCES` daqui e passa cada procedência por
`procedencia_da_entidade` antes de a devolver — medido contra o gold em
`tests/test_metodo_puglia.py` (T7). O lint e a espécie ainda não estão
ligados a nenhuma produção de ficha.

    python3 leis/afirmacao_da_fonte.py     # imprime o contrato
"""
from __future__ import annotations

import json
import re
import sys
import unicodedata

# ── COL-LAW-221 · DE ONDE VEIO A ENTIDADE ─────────────────────────────
# Toda praga, doença, cultura, produto ou molécula de uma afirmação diz de onde
# o NOME dela veio. SPAN só quando o nome está dentro do trecho.
ENTITY_SOURCES = ('SPAN', 'PARAGRAPH_CONTEXT', 'SECTION_TITLE',
                  'DOCUMENT_TITLE', 'UNKNOWN')


def procedencia_da_entidade(entity_source, *, nome_no_trecho,
                            concorrente=False, troca_de_secao=False):
    """→ (ok, porque). A trava da COL-LAW-221, sem ler texto nenhum.

    `concorrente`: outra entidade da mesma espécie aparece entre o nome e o
    trecho. `troca_de_secao`: há mudança de secção entre o nome e o trecho.
    Qualquer um dos dois, com o nome fora do trecho, obriga UNKNOWN.
    """
    if entity_source not in ENTITY_SOURCES:
        return False, 'ENTITY_SOURCE %r fora do vocabulário' % (entity_source,)
    if entity_source == 'SPAN':
        if not nome_no_trecho:
            return False, 'SPAN exige o nome dentro do trecho'
        return True, 'o nome está no trecho'
    if nome_no_trecho:
        return False, 'o nome está no trecho: a procedência é SPAN, não %s' % entity_source
    if (concorrente or troca_de_secao) and entity_source != 'UNKNOWN':
        return False, ('entidade concorrente ou troca de secção entre o nome e o trecho '
                       '— só UNKNOWN é honesto')
    return True, 'herdada de %s, dita como herdada' % entity_source


# ── CHAVE-PROBLEMA (27/09) · O PROBLEMA COMO CHAVE DA COLLECTION ──────
# Medido: `motor/cap_win.py` dizia «PROBLEMA NAO EXISTE no contrato 033», e todo
# item real saía NOT_POSSIBLE. A porta JÁ escrevia um bloco PROBLEMA dentro da
# `janela_declarada` (boletins T2/T3, estudos T5), mas fora de contrato: VALOR
# era uma LISTA (a CAP-WIN colava-a com vírgulas num ISSUE_ID que ninguém
# escreveu), VEIO_DE era uma frase livre e a BASE uma descrição da regra, não
# o trecho. Este é o contrato — a forma, e só a forma; quem o preenche é a
# Collection (INT-LAW-083/084), e quem o lê não volta ao texto para o refazer.
#
#     VALOR     UM nome canónico (tabela versionada `MESMO_PROBLEMA`, D111), ou «NAO SEI»
#     VEIO_DE   TEXT · SECTION_HEADER · DOCUMENT_TITLE — onde o nome está ESCRITO
#     BASE      o trecho LITERAL que contém o nome (confere-se contra o texto do item)
#     FORMA     o nome como a fonte o escreve (tem de estar dentro da BASE)
#     CODIGO    EPPO só com o binómio latino escrito no texto e casado EXACTAMENTE com a
#               tabela do repo; senão NOME_CANONICO. Nunca por semelhança (COL-LAW-034).
#
# ⚠️ DUAS PRAGAS NO ITEM = NAO SEI (D112: «outra praga no meio»). Escolher uma
# seria inferir; os CANDIDATOS ficam à vista, com a base de cada um.
# ⚠️ Mora na `janela_declarada` que a 033 já guarda (a trava da 033 só exige as
# quatro chaves e não proíbe uma quinta) e revê-se pelo campo `janela_declarada`
# que a 033 já aceita. Não há migração (CHAVE-PROBLEMA.md).
CONTRATO_PROBLEMA = 'PROBLEMA/v1'
VEIO_DE_DO_PROBLEMA = ('TEXT', 'SECTION_HEADER', 'DOCUMENT_TITLE')
#: a mesma pergunta da COL-LAW-221, feita ao item e não à afirmação
ENTITY_SOURCE_DO_VEIO_DE = {'TEXT': 'SPAN', 'SECTION_HEADER': 'SECTION_TITLE',
                            'DOCUMENT_TITLE': 'DOCUMENT_TITLE'}
SISTEMAS_DO_CODIGO = ('EPPO', 'NOME_CANONICO')
AUSENCIA_DO_PROBLEMA = 'NAO SEI'
_CODIGO_EPPO = re.compile(r'^[0-9A-Z]{5,6}$')


def _espacos(s):
    return re.sub(r'\s+', ' ', str(s or '')).strip()


def _dobra(s):
    s = unicodedata.normalize('NFKD', _espacos(s))
    return ''.join(c for c in s if not unicodedata.combining(c)).lower()


def problema_conforme(bloco, texto=None):
    """→ (ok, porque). A trava do contrato PROBLEMA/v1, sem extrair nada.

    Com `texto` (o texto do item), a BASE tem de estar LITERALMENTE nele, e a
    prova do código EPPO também: um problema cuja base o texto não contém foi
    inferido, não lido. «NAO SEI» com PORQUE é conforme (é a verdade dita)."""
    if not isinstance(bloco, dict):
        return False, 'PROBLEMA ausente'
    if bloco.get('CONTRATO') != CONTRATO_PROBLEMA:
        return False, 'PROBLEMA fora do contrato %s (CONTRATO=%r)' % (
            CONTRATO_PROBLEMA, bloco.get('CONTRATO'))
    valor = bloco.get('VALOR')
    if not isinstance(valor, str) or not valor.strip():
        return False, 'VALOR tem de ser UM nome (texto), nunca lista nem vazio'
    if valor == AUSENCIA_DO_PROBLEMA:
        if not _espacos(bloco.get('PORQUE')):
            return False, 'NAO SEI sem PORQUE'
        return True, 'NAO SEI declarado: %s' % bloco['PORQUE']
    if bloco.get('VEIO_DE') not in VEIO_DE_DO_PROBLEMA:
        return False, 'VEIO_DE %r fora de %s' % (bloco.get('VEIO_DE'), VEIO_DE_DO_PROBLEMA)
    base, forma = _espacos(bloco.get('BASE')), _espacos(bloco.get('FORMA'))
    if not base or base == AUSENCIA_DO_PROBLEMA:
        return False, 'VALOR sem BASE'
    if not forma or _dobra(forma) not in _dobra(base):
        return False, 'a FORMA %r nao esta dentro da BASE' % forma
    if texto is not None and base not in _espacos(texto):
        return False, 'a BASE nao esta no texto do item: foi inferida, nao lida'
    codigo = bloco.get('CODIGO')
    if not isinstance(codigo, dict) or codigo.get('SISTEMA') not in SISTEMAS_DO_CODIGO:
        return False, 'CODIGO sem SISTEMA de %s' % (SISTEMAS_DO_CODIGO,)
    if codigo['SISTEMA'] == 'EPPO':
        prova = _espacos(codigo.get('PROVA'))
        if not _CODIGO_EPPO.match(str(codigo.get('VALOR') or '')) or not prova:
            return False, 'CODIGO EPPO sem codigo valido ou sem PROVA escrita'
        if texto is not None and _dobra(prova) not in _dobra(texto):
            return False, 'a PROVA do EPPO nao esta no texto: codigo cunhado, nao lido'
    elif codigo.get('VALOR') != valor or not _espacos(codigo.get('TABELA')):
        return False, 'NOME_CANONICO tem de ser o proprio VALOR, com a TABELA que o da'
    return True, 'conforme %s' % CONTRATO_PROBLEMA


def problema_da_chave(bloco, texto=None):
    """→ (valor | None, porque). O que QUEM CRUZA lê: o nome canónico, só se o
    bloco é conforme e não é NAO SEI. O leitor não volta ao texto para o refazer."""
    ok, porque = problema_conforme(bloco, texto)
    if not ok:
        return None, porque
    if bloco['VALOR'] == AUSENCIA_DO_PROBLEMA:
        return None, 'VALOR = NAO SEI (%s)' % _espacos(bloco.get('PORQUE'))
    return bloco['VALOR'], porque


# ── COL-LAW-223 · A ESPÉCIE DA AFIRMAÇÃO ──────────────────────────────
ESPECIES_DA_AFIRMACAO = ('FATO_OBSERVADO', 'PREVISAO', 'RECOMENDACAO')


def usavel_como_fato_observado(especie):
    """Só um fato observado prova que algo aconteceu no campo."""
    return especie == 'FATO_OBSERVADO'


# ── INT-LAW-078 / INT-LAW-079 · RELAÇÕES ENTRE AFIRMAÇÕES ─────────────
RELACOES = ('SAME_CLAIM_TERRITORIAL_APPLICATION',
            'TEMPORAL_CHANGE_IN_RECOMMENDATION',
            'DIVERGENT_RECOMMENDATIONS', 'NAO_SEI')
CONTRADICTION_STATUS = ('UNRESOLVED', 'NO')


def _instituicao(publisher):
    """«A.P.OL. (Associazione …)» e «A.P.OL. (o conteúdo …)» são a mesma casa."""
    p = re.split(r'\s+[(—–-]\s*', (publisher or '').strip(), maxsplit=1)[0]
    return p.strip().upper()


def relacao(a, b):
    """Relação entre duas afirmações. Cada uma é um dict com PUBLISHER,
    SPAN_SHA256, TERRITORIO, VALIDADE e VALOR (o que foi afirmado).

    Nunca conclui contradição, e nunca conclui que o campo mudou: o que a
    ficha prova é o que a FONTE disse, não o que o mundo fez.
    """
    mesma_casa = _instituicao(a.get('PUBLISHER')) == _instituicao(b.get('PUBLISHER'))
    if (mesma_casa and a.get('SPAN_SHA256') == b.get('SPAN_SHA256')
            and a.get('TERRITORIO') != b.get('TERRITORIO')):
        return {'RELATION': 'SAME_CLAIM_TERRITORIAL_APPLICATION',
                'INSTITUICOES_INDEPENDENTES': 1, 'CONTRADICTION_STATUS': 'NO',
                'CONCLUIR_MUDANCA_DO_CAMPO': False}
    if a.get('VALOR') == b.get('VALOR'):
        return {'RELATION': 'NAO_SEI', 'CONTRADICTION_STATUS': 'UNRESOLVED',
                'CONCLUIR_MUDANCA_DO_CAMPO': False}
    if mesma_casa and a.get('VALIDADE') and b.get('VALIDADE') \
            and a.get('VALIDADE') != b.get('VALIDADE'):
        return {'RELATION': 'TEMPORAL_CHANGE_IN_RECOMMENDATION',
                'INSTITUICOES_INDEPENDENTES': 1, 'CONTRADICTION_STATUS': 'NO',
                'CONCLUIR_MUDANCA_DO_CAMPO': False}
    if not mesma_casa:
        return {'RELATION': 'DIVERGENT_RECOMMENDATIONS',
                'INSTITUICOES_INDEPENDENTES': 2, 'CONTRADICTION_STATUS': 'UNRESOLVED',
                'CONCLUIR_MUDANCA_DO_CAMPO': False}
    return {'RELATION': 'NAO_SEI', 'CONTRADICTION_STATUS': 'UNRESOLVED',
            'CONCLUIR_MUDANCA_DO_CAMPO': False}


# ── COL-LAW-222 · O LINT DA FIDELIDADE ────────────────────────────────
# Determinístico, sem rede e sem modelo. Ele não sabe traduzir: ele confere o
# que atravessa qualquer tradução — colchete acrescentado, número, negação,
# exceção e entidade citada. Falha de menos é possível (o lint não vê tudo);
# por isso aprovar aqui não prova fidelidade, e reprovar prova infidelidade.

# O único colchete que cabe numa tradução é o rótulo da espécie da afirmação,
# que já está na ficha: não diz nada novo sobre o mundo. Qualquer outra coisa
# entre colchetes é o sistema a falar dentro da boca da fonte.
ROTULOS_PERMITIDOS = ('PREVISAO', 'RECOMENDACAO', 'FATO OBSERVADO', 'OBSERVADO')

# Vocabulário de SUPERFÍCIE do lint: como o nome aparece escrito, e a chave com
# que a ficha o guarda. Não é taxonomia nem saber agronómico — é o que permite
# ver que o trecho cita um nome que a ficha não guardou. Nome fora da lista não
# é verificado, e o lint diz isso em vez de aprovar por ele.
NOMES_DE_SUPERFICIE = {
    "mosca dell'olivo": 'PEST:DACUOL',
    'mosca delle olive': 'PEST:DACUOL',
    'bactrocera oleae': 'PEST:DACUOL',
    'margaronia': 'margaronia',
    'prays oleae': 'prays oleae',
    'tignola delle olive': 'prays oleae',
    'oziorrinco': 'oziorrinco',
    'otiorhynchus cribricollis': 'oziorrinco',
}

MARCAS_DE_EXCECAO_IT = r"\b(?:salvo|tranne|eccetto|ad eccezione d\w*|solo|soltanto|unicamente|esclusivamente|purch[eé]|a condizione che)\b"
MARCAS_DE_EXCECAO_PT = r"(?<!\w)(?:salvo|exceto|com exce[cç][aã]o d\w*|s[oó]|somente|apenas|unicamente|exclusivamente|desde que|a n[aã]o ser)(?!\w)"
FIM_IT = r"\s+e comunque\b|[;.]|$"
FIM_PT = r",?\s+e\s|[;.]|$"
NEGACAO_IT = r"\b(?:non|n[eé]|nessun\w*)\b"
NEGACAO_PT = r"(?<!\w)(?:n[aã]o|nem|nenhum\w*)(?!\w)"
NUMERO = r"\d+(?:[.,]\d+)?"


def _norm(s):
    s = unicodedata.normalize('NFKD', s or '')
    return ''.join(c for c in s if not unicodedata.combining(c)).upper().strip()


def _clausula(texto, marcas, fim):
    """Os itens (separados por vírgula) da primeira cláusula de exceção."""
    m = re.search(marcas, texto, re.I)
    if not m:
        return None
    resto = texto[m.end():]
    f = re.search(fim, resto, re.I)
    corpo = resto[:f.start()] if f else resto
    return [x for x in (p.strip() for p in corpo.split(',')) if x]


def _texto_da_ficha(ficha):
    partes = []
    for k in ('SUJEITO', 'PREDICADO', 'OBJETO', 'CULTURA', 'ENTIDADES'):
        v = ficha.get(k)
        partes.extend(v if isinstance(v, list) else [v] if v else [])
    return ' '.join(str(p) for p in partes)


def fidelidade(trecho, traducao, ficha):
    """→ {'FIEL': bool, 'ERROS': [...], 'NAO_VERIFICADO': [...]}."""
    erros, nao_verificado = [], []
    traducao = traducao or ''
    ficha_txt = _texto_da_ficha(ficha or {})

    for dentro in re.findall(r'\[([^\]]*)\]', traducao):
        if _norm(dentro) not in ROTULOS_PERMITIDOS:
            erros.append('ACRESCENTA_COLCHETE: [%s]' % dentro)

    for n in re.findall(NUMERO, trecho):
        if n not in traducao:
            erros.append('OMITE_NUMERO: %s' % n)

    if re.search(NEGACAO_IT, trecho, re.I) and not re.search(NEGACAO_PT, traducao, re.I):
        erros.append('OMITE_NEGACAO')

    na_fonte = _clausula(trecho, MARCAS_DE_EXCECAO_IT, FIM_IT)
    if na_fonte:
        na_traducao = _clausula(traducao, MARCAS_DE_EXCECAO_PT, FIM_PT) or []
        if len(na_traducao) < len(na_fonte):
            erros.append('OMITE_QUALIFICADOR_NA_TRADUCAO: %d de %d (%s)'
                         % (len(na_traducao), len(na_fonte), '; '.join(na_fonte)))
        if not (re.search(MARCAS_DE_EXCECAO_PT, ficha_txt, re.I)
                or re.search(MARCAS_DE_EXCECAO_IT, ficha_txt, re.I)):
            erros.append('OMITE_QUALIFICADOR_NA_FICHA')

    baixo = (trecho or '').lower()
    for nome, chave in NOMES_DE_SUPERFICIE.items():
        if nome in baixo and chave not in ficha_txt and nome not in ficha_txt.lower():
            erros.append('OMITE_ENTIDADE: %s' % nome)
    if not any(nome in baixo for nome in NOMES_DE_SUPERFICIE):
        nao_verificado.append('nenhum nome do vocabulário de superfície no trecho')

    return {'FIEL': not erros, 'ERROS': erros, 'NAO_VERIFICADO': nao_verificado}


def contrato():
    return {
        'SOURCE_ID': 'AFIRMACAO-DA-FONTE-CONTRATO',
        'VERSION': 'V1',
        'DECISAO': 'D112',
        'LEIS': ['COL-LAW-221', 'COL-LAW-222', 'COL-LAW-223',
                 'INT-LAW-078', 'INT-LAW-079'],
        'ENTITY_SOURCES': list(ENTITY_SOURCES),
        'CONTRATO_PROBLEMA': CONTRATO_PROBLEMA,
        'VEIO_DE_DO_PROBLEMA': list(VEIO_DE_DO_PROBLEMA),
        'SISTEMAS_DO_CODIGO': list(SISTEMAS_DO_CODIGO),
        'ESPECIES_DA_AFIRMACAO': list(ESPECIES_DA_AFIRMACAO),
        'RELACOES': list(RELACOES),
        'CONTRADICTION_STATUS': list(CONTRADICTION_STATUS),
        'ROTULOS_PERMITIDOS_NA_TRADUCAO': list(ROTULOS_PERMITIDOS),
        'O_QUE_ISTO_NAO_E': 'não é extrator: não lê boletim, não propõe entidade nem lugar.',
    }


if __name__ == '__main__':
    json.dump(contrato(), sys.stdout, ensure_ascii=False, indent=1)
    print()
