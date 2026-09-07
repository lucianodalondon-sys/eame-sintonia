#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
QUAL CAMPO SE TRADUZ, QUAL NÃO — a regra, num lugar só.

    python3 scripts/v21_campos_de_lingua.py        # relatório do que falta

A MISSÃO DIZ DUAS COISAS QUE PARECEM BRIGAR
--------------------------------------------
1. o Design nunca pode precisar mostrar prosa de pesquisa em português;
2. «Original public quotes remain in their original language».

Não brigam. Separam-se por uma pergunta só:

    QUEM ESCREVEU ESTA FRASE — A FONTE, OU EU?

O que a fonte escreveu é PROVA. Traduzir prova é adulterar prova: some o que o
agricultor de fato digitou, some a palavra que o rótulo de fato usa. O que eu
escrevi é LEITURA, e leitura pode — e deve — chegar na língua de quem lê.

    A CITAÇÃO É O DOCUMENTO. A LEITURA É MINHA OPINIÃO SOBRE ELE.
    Só a segunda vira _IT e _EN.

O CASO MISTO
-------------
Alguns campos têm as duas coisas na mesma linha:

    MECHANISM = 'ALS (gruppo B) — literal: "erbicidi inibitori dell'ALS (gruppo B)"'

Aqui o trecho depois de `literal:` é da fonte e fica intacto; o resto é meu. O
tradutor tem de enxergar a costura, e por isso ela está declarada, não adivinhada.
"""
import json
import os
import re
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ING = os.path.join(ROOT, 'build', 'ITALY-REALITY-HANDOFF-V2.1', 'DESIGN-INGEST')

# ── 1 · MINHA LEITURA — vira _IT e _EN ──────────────────────────────────────
LEITURA = [
    'WHAT_IT_IS', 'WHAT_IT_PROVES', 'WHAT_IT_DOES_NOT_PROVE', 'WHY_IT_MATTERS',
    'PERMANENT_CAVEAT', 'CAVEAT', 'LINK_MEANS', 'EVIDENCE_STATUS_WHY',
    'WHAT_IT_PUBLISHES', 'COMMERCIAL_CONTRACT_WHY', 'INTERVENTION_GUIDANCE',
    'SUMMARY_CLAIM_NOTE', 'ACCESS_EVIDENCE', 'ACCESS_STATE', 'MULTIPLE_RESISTANCE',
    'ROUTE_EVIDENCE_NOTE',
    'WHAT_IT_LETS_YOU_ASK', 'SOURCE_SCOPE', 'ECONOMIC_WEIGHT_LEADS_LAW',
    'SERIES_WARNING', 'PARTICIPATION_LAW', 'WHY_WATCH', 'LIMITATIONS',
    'WHAT_WOULD_MAKE_IT_AN_OPPORTUNITY', 'SCIENCE_CONTEXT', 'NEXT_IMPORTANT_WINDOW',
    'ROLE_EVIDENCE', 'FIELD_REPORTED_STAGE', 'CONFIDENCE', 'NOTE', 'SO_WHAT',
    'WHAT_THIS_IS_NOT', 'READING_NOTE', 'INTERPRETATION', 'ANALYST_NOTE',
    'WHAT_IT_SHOWS', 'DESCRIPTION_PT',
    # ── camada comercial V1.1 · leitura nossa, e por isso traduzível ────────
    'COMMERCIAL_PRIORITY_MEANS', 'WHY_COMMERCIAL', 'CLAIM_GEOGRAPHY_WHY',
    'COMMERCIAL_DOES_NOT_PROVE',
]

# ── 2 · PALAVRA DA FONTE — não se toca ──────────────────────────────────────
#
# ⚠️ Traduzir qualquer um destes destrói a prova. O comentário do agricultor em
# italiano É o dado; a versão em inglês dele é uma paráfrase minha com aspas
# emprestadas.
FONTE = [
    'TEXT_ORIGINAL', 'CREATIVE_TEXT', 'DESCRIPTION', 'NAME', 'TITLE',
    'SPECIES_IT', 'SPECIES_LATIN', 'CROP_DECLARED_IT', 'PRODUCT_NAME',
    'PHENOLOGICAL_STAGE_DECLARED', 'REGION', 'QUOTE', 'HEADLINE', 'AD_TEXT',
    # ⚠️ NEED_EXCERPT é a FRASE DO BOLETIM que sustenta a direção da
    # necessidade. Ela é a prova; a leitura sobre ela é NEED_DIRECTION, que é
    # valor controlado e não tem língua. Traduzir a frase seria adulterar a
    # prova para explicar a minha leitura dela.
    'NEED_EXCERPT',
    # ── a palavra da fonte nas travessias ACERVO→PACOTE ─────────────────────
    # `TEXT` é a FALA transcrita e `ABSTRACT_ORIGINAL` é o resumo publicado do
    # paper. Traduzir qualquer um destrói a prova — e o detector de português
    # marca-os por engano, porque italiano e português partilham «que», «para»,
    # «com», «cultura». Declarados aqui, param de ser confundidos com prosa minha.
    'TEXT', 'ABSTRACT_ORIGINAL',
]

# ── 3 · COSTURA — meu rótulo + citação literal na mesma linha ───────────────
#
# O padrão é sempre o mesmo: `<minha leitura> — literal: "<palavra da fonte>"`.
# Traduz-se o lado esquerdo; o direito atravessa inteiro.
MISTO = ['MECHANISM', 'FIRST_CASE_YEAR', 'CROP_DECLARED']
COSTURA = re.compile(r'\s*[—-]\s*literal:\s*(.*)$', re.S)

# ── 4 · PAPEL DE TRABALHO — o Design nunca lê; fica em português ────────────
INTERNO = [
    'QA_RECONCILIATION', 'ID_NOTE', 'ORIGIN_LAYER_NOTE', 'DEDUPE_NOTE',
    'QA_NOTE', 'RESEARCH_NOTE', 'ORIGINAL_RESEARCH_TEXT',
    # ── as leis das travessias ACERVO→PACOTE ────────────────────────────────
    # São o texto do CONTRATO do registro — dizem o que o campo ao lado prova e
    # o que não prova. O Design não as imprime; quem as lê é quem consome o
    # pacote. Ficam em português, declaradas, e não entram na conta de tradução.
    'ACTIVE_PROOF_WHY', 'ACTIVE_PROOF_LAW', 'OBSERVATION_LAW',
    'CHANGE_OBSERVED_LAW', 'COUNTRY_REACHED_WHY', 'TEMPORAL_PROOF_WHY',
    'STATE_REASON', 'COUNTRY_LAW', 'ROUTE_TERM_LAW', 'LADDER_LAW',
    'ISSUE_IDS_LAW', 'CROP_IDS_LAW', 'QUERY_VS_PROVED_LAW', 'ABSTRACT_LAW',
    'SAME_ENTITY_LAW', 'QUERY_TERM_LAW', 'ACERVO_MATCH_WHY',
    'CITED_IN_PACKAGE_LAW', 'ACERVO_MATCH',
    # as frases de MÉTODO que o acervo escreve sobre a própria leitura —
    # «o texto traz "olive"», «nenhum lugar nomeado no texto». São nota de
    # trabalho sobre como se provou, não afirmação ao cliente.
    'PROVED_CROP_EVIDENCE', 'PROVED_ISSUE_EVIDENCE', 'COUNTRY_OF_FACT_EVIDENCE',
    'PERSON_PROOF_EVIDENCE', 'MATERIAL_ROLE_EVIDENCE', 'STATE_REASON_ACERVO',
    'ABSTRACT_TRANSLATION_METHOD', 'EPISODE_DESCRIPTION_LAW',
    # o que a rota DECLAROU, preservado à letra — incluindo a sentinela com
    # razão: «NÃO SEI — a rota nao declara o idioma da legenda». É a declaração
    # da fonte sobre o que ela própria não sabe, e reescrevê-la apagaria a razão.
    'SOURCE_LANGUAGE_DECLARED', 'SOURCE_COUNTRY_DECLARED',
    'SOURCE_COUNTRY_EVIDENCE',
]

# ⚠️ ESTA LISTA NÃO ERA LIDA POR NINGUÉM.
# `INTERNO` existia como documentação: nenhum código a consumia. E `varrer()` só
# percorre LEITURA + MISTO. Consequência medida: um campo de prosa portuguesa
# cujo NOME não estivesse em LEITURA não era traduzido, não era contado, e não
# acendia nada — `AINDA_SO_EM_PORTUGUES` continuava 0 com português na tela.
#
#     A LISTA QUE NINGUÉM LÊ NÃO CLASSIFICA NADA: DECORA.
#
# Agora há um contador para o que não está em lista nenhuma. Ele não reprova a
# cadeia — declara um número que antes não existia, e quem o vir decide.
CLASSIFICADOS = set(LEITURA) | set(MISTO) | set(FONTE) | set(INTERNO)
SUFIXO_DERIVADO = ('_IT', '_EN', '_ORIGINAL_RESEARCH_TEXT', '_PROMOVIDO_DE')

# ── 5 · O BLOCO RESEARCH — e a armadilha que ele esconde ────────────────────
#
# 314 registros da last-mile guardam a leitura SÓ aqui dentro, em português, e
# não têm campo client-facing nenhum. A regra «a pesquisa fica em português
# dentro de RESEARCH, o Design nunca precisa lê-la» só vale se houver outro
# lugar de onde ler. Nestes 314 não há.
#
#     SE A ÚNICA CÓPIA DA RESSALVA ESTÁ NUMA LÍNGUA QUE A TELA NÃO MOSTRA,
#     A TELA NÃO MOSTRA A RESSALVA. E RESSALVA QUE NÃO APARECE É RESSALVA
#     QUE NÃO EXISTE.
#
# Então a leitura SOBE para o topo, traduzida, e o original fica embaixo intacto.
# `citacao_literal` NÃO sobe traduzida: é a palavra da fonte.
PROMOVE = {
    'o_que': 'WHAT_IT_IS',
    'o_que_prova': 'WHAT_IT_PROVES',
    'o_que_nao_prova': 'WHAT_IT_DOES_NOT_PROVE',
}
RESEARCH_NAO_SOBE = ['citacao_literal', 'IDIOMA', 'valor', 'unidade', 'periodo']

PT = re.compile(
    r'\b(nao|não|que|para|com|prova|foi|são|sao|est[aá]|pelo|pela|'
    r'isso|aqui|porque|cultura|regi[aã]o|r[oó]tulo|fonte|linha|apenas|'
    r'ainda|tamb[eé]m|sobre|dizer|mesmo|cada|dentro|fora|onde|quem|'
    r'coment[aá]rio|agricultor|produto|neg[oó]cio|pre[cç]o)\b', re.I)


def parte_minha(campo, valor):
    """Devolve (o que traduzo, o que atravessa intacto)."""
    if campo in MISTO:
        m = COSTURA.search(valor)
        if m:
            return valor[:m.start()], valor[m.start():]
    return valor, ''


def e_portugues(t):
    return isinstance(t, str) and len(t) > 25 and len(PT.findall(t)) >= 2


def campos_do_registro(r):
    """[(campo_de_destino, texto_pt, veio_de_research)] deste registro."""
    fora = []
    for campo in LEITURA + MISTO:
        v = r.get(campo)
        if isinstance(v, str):
            fora.append((campo, v, False))
    R = r.get('RESEARCH')
    if isinstance(R, dict):
        for sub, destino in PROMOVE.items():
            v = R.get(sub)
            # ⚠️ só sobe se o topo ainda não tiver: campo do topo é a verdade
            # publicada, RESEARCH é o rascunho. O rascunho nunca sobrescreve.
            if isinstance(v, str) and not isinstance(r.get(destino), str):
                fora.append((destino, v, True))
    return fora


def campos_nao_classificados(r):
    """Prosa em português num campo que NENHUMA lista classifica.

    Não é erro por si: pode ser nota de trabalho legítima. É o número que
    faltava — sem ele, «zero em português» podia significar «nada em português»
    ou «ninguém olhou».
    """
    fora = []
    for campo, v in r.items():
        if campo in CLASSIFICADOS or not isinstance(v, str):
            continue
        if campo.endswith(SUFIXO_DERIVADO):
            continue
        base = campo
        for suf in SUFIXO_DERIVADO:
            if campo.endswith(suf):
                base = campo[:-len(suf)]
        if base in CLASSIFICADOS:
            continue
        if e_portugues(v):
            fora.append(campo)
    return fora


def varrer():
    """{frase_em_pt: [(arquivo, id, campo), ...]} — só do que é leitura minha."""
    achados = {}
    for arq in sorted(os.listdir(ING)):
        if not arq.endswith('.json') or arq.startswith('CANONICAL'):
            continue
        d = json.load(open(os.path.join(ING, arq), encoding='utf-8'))
        for r in d.get('RECORDS') or []:
            if not isinstance(r, dict) or not r.get('ID'):
                continue
            for campo, v, _ in campos_do_registro(r):
                meu, _c = parte_minha(campo, v)
                if e_portugues(meu):
                    achados.setdefault(meu.strip(), []).append(
                        (arq, r['ID'], campo))
    return achados


def main():
    a = varrer()
    print('frases DISTINTAS a traduzir : %d' % len(a))
    print('ocorrencias                 : %d' % sum(len(v) for v in a.values()))
    print('caracteres                  : %d' % sum(len(t) for t in a))
    print()
    c = Counter(x[2] for v in a.values() for x in v)
    for k, n in c.most_common():
        print('  %-34s %6d' % (k, n))
    p = os.path.join(ROOT, '.tmp', 'v21_frases_pt.json')
    json.dump([{'PT': t, 'ONDE': v} for t, v in sorted(a.items(),
                                                      key=lambda x: -len(x[1]))],
              open(p, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('\nlista em %s' % p)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
