#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
R4 · O CONTRATO DA SUPERFICIE — o manifesto lido por um consumidor burro.

    python3 scripts/v21_contrato_da_superficie.py

POR QUE ESTE ARQUIVO EXISTE
----------------------------
O APP-MANIFEST e o arquivo de entrada do portal. Durante uma missao inteira ele
carregou tres campos que PARECIAM portao de visibilidade — CLIENT_SAFE,
RENDERABLE_WITH_METHOD, PUBLICATION_STATE — e uma lei que mandava os 43 casos
para RESEARCH_LEADS. Quem implementasse o manifesto ao pe da letra chegava a uma
tela vazia; quem implementasse «o que faz sentido» chegava a tela certa por
sorte.

    UM CONTRATO QUE SO FUNCIONA SE O LEITOR ADIVINHAR NAO E CONTRATO:
    E UM TESTE DE ADIVINHACAO QUE O CONSUMIDOR VAI PERDER.

Este script e o consumidor burro. Ele nao sabe nada sobre agronomia, sobre a
reuniao da ADAMA nem sobre a intencao de quem escreveu o pacote. Ele so sabe:

    1. abrir APP-MANIFEST.json;
    2. obedecer LITERALMENTE o que estiver escrito la;
    3. contar o resultado no pacote.

Se para montar a tela ele precisar de UMA decisao que o manifesto nao declarou,
isso e CONTRACT = FAIL — e o defeito e do manifesto, nunca dele.

O QUE ELE PRECISA CONCLUIR SEM INFERENCIA
------------------------------------------
    mostrar os 43 · 5 AGIRE ORA · 8 PREPARARE ORA · 13 DA MONITORARE ·
    17 SEGNALI · nao filtrar por CLIENT_SAFE · nao filtrar por
    RENDERABLE_WITH_METHOD · nao filtrar por PUBLICATION_STATE ·
    impedir distribuicao externa dos 38 VALIDATION_REQUIRED

Os numeros acima sao o CRITERIO, e por isso estao escritos aqui. Tudo o mais —
quais campos consultar, que faixa cada valor recebe, quem pode sair para fora —
o consumidor le do manifesto. Se ele lesse tambem os numeros de la, o teste
provaria apenas que o manifesto concorda consigo mesmo.
"""
import json
import os
import sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ING = os.path.join(ROOT, 'build', 'ITALY-REALITY-HANDOFF-V2.1', 'DESIGN-INGEST')
SAIDA = os.path.join(os.path.dirname(ING), 'SURFACE-CONTRACT.json')

# O criterio. Nao sai do manifesto de proposito — veja o docstring.
FAIXAS_ESPERADAS = {'AGIRE ORA': 5, 'PREPARARE ORA': 8,
                    'DA MONITORARE': 13, 'SEGNALI': 17}
TOTAL_ESPERADO = 43
BLOQUEADOS_ESPERADOS = {'VALIDATION_REQUIRED': 38}
LIBERADOS_ESPERADOS = {'PUBLISHABLE': 5}

# Os campos que ja foram confundidos com portao de visibilidade. O manifesto tem
# de dizer, sobre CADA um deles, que nao filtra a tela.
NAO_FILTRAM = ('CLIENT_SAFE', 'RENDERABLE_WITH_METHOD', 'PUBLICATION_STATE')

# Palavra que, sozinha, autoriza a saida para terceiro. Qualquer outra coisa —
# «bloqueado», «sujeito a», silencio — o consumidor le como NAO.
AUTORIZA = 'permitido'


def _abre(nome):
    p = os.path.join(ING, nome)
    if not os.path.exists(p):
        print('pacote nao construido: falta %s — rode bash scripts/v21_cadeia.sh'
              % nome, file=sys.stderr)
        raise SystemExit(2)
    return json.load(open(p, encoding='utf-8'))


def main():
    man = _abre('APP-MANIFEST.json')
    falhas, passos = [], []

    def exige(cond, chave, detalhe):
        passos.append({'PERGUNTA': chave, 'RESPONDIDA_PELO_MANIFESTO': bool(cond),
                       'DETALHE': detalhe})
        if not cond:
            falhas.append('%s · %s' % (chave, detalhe))
        return bool(cond)

    # ── 1 · de qual colecao sai a tela, e ela inclui todos os casos? ─────────
    regra = man.get('MEETING_SURFACE_RULE') or {}
    if not exige(regra, 'ONDE_ESTA_A_REGRA_DA_SUPERFICIE',
                 'MEETING_SURFACE_RULE ausente do manifesto'):
        return _fecha(falhas, passos, {})

    colecao = regra.get('SOURCE_COLLECTION')
    exige(colecao, 'QUAL_COLECAO_VAI_PARA_A_TELA', 'SOURCE_COLLECTION=%r' % colecao)
    exige(regra.get('INCLUDE_ALL_CURRENT_CASES') is True,
          'INCLUO_TODOS_OS_CASOS',
          'INCLUDE_ALL_CURRENT_CASES=%r' % regra.get('INCLUDE_ALL_CURRENT_CASES'))

    # O consumidor descobre o ARQUIVO pela propria tabela de colecoes: ele nao
    # pode chutar «OPPORTUNITIES vira OPPORTUNITIES.json».
    arquivo = None
    for c in man.get('COLLECTIONS') or []:
        if c.get('COLLECTION_NAME') == colecao:
            arquivo = c.get('FILE')
    exige(arquivo, 'QUE_ARQUIVO_ABRO',
          'COLLECTIONS nao diz o FILE de %s' % colecao)
    if not arquivo:
        return _fecha(falhas, passos, {})

    pacote = _abre(arquivo)
    registros = pacote.get('RECORDS') or []

    # ── 2 · quem manda na faixa, e que faixa cada valor recebe? ──────────────
    dono = regra.get('LANE_OWNER')
    faixas = regra.get('LANES') or {}
    exige(dono, 'QUEM_DECIDE_A_FAIXA', 'LANE_OWNER=%r' % dono)
    exige(faixas, 'QUAL_FAIXA_CADA_VALOR_RECEBE', 'LANES=%r' % faixas)
    if not (dono and faixas):
        return _fecha(falhas, passos, {})

    # ── 3 · o consumidor monta a tela. Obedecendo, nao interpretando. ────────
    na_tela = list(registros) if regra.get('INCLUDE_ALL_CURRENT_CASES') else []
    sem_faixa = [r.get('ID') for r in na_tela if r.get(dono) not in faixas]
    contagem = Counter(faixas[r[dono]] for r in na_tela if r.get(dono) in faixas)

    exige(not sem_faixa, 'TODO_CASO_TEM_FAIXA',
          '%d caso(s) com %s fora de LANES: %s'
          % (len(sem_faixa), dono, sem_faixa[:5]))
    exige(len(na_tela) == TOTAL_ESPERADO, 'QUANTOS_APARECEM',
          '%d na tela · criterio %d' % (len(na_tela), TOTAL_ESPERADO))
    exige(regra.get('EXPECTED_TOTAL') == len(na_tela), 'O_TOTAL_DECLARADO_CONFERE',
          'EXPECTED_TOTAL=%r · contados %d' % (regra.get('EXPECTED_TOTAL'),
                                               len(na_tela)))
    for faixa, quanto in sorted(FAIXAS_ESPERADAS.items()):
        exige(contagem.get(faixa, 0) == quanto, 'FAIXA_%s' % faixa.replace(' ', '_'),
              '%d · criterio %d' % (contagem.get(faixa, 0), quanto))

    # ── 4 · algum campo manda esconder? Tem de estar escrito que NAO. ───────
    for campo in NAO_FILTRAM:
        chave = '%s_IS_VISIBILITY_GATE' % campo
        exige(regra.get(chave) is False, 'NAO_FILTRO_POR_%s' % campo,
              '%s=%r (precisa ser False, declarado — ausente e adivinhacao)'
              % (chave, regra.get(chave)))

    # A lei antiga do CLIENT_SAFE mandava os 43 para RESEARCH_LEADS. Se ela
    # voltar, o consumidor obediente esvazia a tela outra vez.
    cs = man.get('CLIENT_SAFE_RULE') or {}
    exige(cs.get('NAO_E_PORTAO_DE_VISIBILIDADE') is True,
          'CLIENT_SAFE_NAO_E_PORTAO',
          'CLIENT_SAFE_RULE nao declara NAO_E_PORTAO_DE_VISIBILIDADE=True')
    exige('RESEARCH_LEADS' not in (cs.get('LEI') or ''),
          'CLIENT_SAFE_FALSE_NAO_VAI_PARA_RESEARCH_LEADS',
          'a LEI do CLIENT_SAFE ainda manda o false para RESEARCH_LEADS')

    # ── 5 · e o que pode sair da ADAMA para terceiro? ────────────────────────
    exp = man.get('EXTERNAL_EXPORT_ALLOWED') or {}
    exige(exp, 'O_QUE_PODE_SAIR_PARA_FORA', 'EXTERNAL_EXPORT_ALLOWED ausente')
    por_estado = Counter(r.get('PUBLICATION_STATE') for r in na_tela)
    liberado, bloqueado = Counter(), Counter()
    for est, quantos in por_estado.items():
        regra_do_estado = exp.get(est)
        if regra_do_estado is None:
            exige(False, 'ESTADO_SEM_REGRA_DE_EXPORTACAO',
                  'PUBLICATION_STATE=%s aparece em %d caso(s) e o manifesto nao '
                  'diz se pode sair' % (est, quantos))
            continue
        if AUTORIZA in regra_do_estado.lower():
            liberado[est] += quantos
        else:
            bloqueado[est] += quantos
    for est, quanto in sorted(BLOQUEADOS_ESPERADOS.items()):
        exige(bloqueado.get(est, 0) == quanto, 'BLOQUEIO_EXTERNO_%s' % est,
              '%d bloqueado(s) · criterio %d' % (bloqueado.get(est, 0), quanto))
    for est, quanto in sorted(LIBERADOS_ESPERADOS.items()):
        exige(liberado.get(est, 0) == quanto, 'LIBERADO_EXTERNO_%s' % est,
              '%d liberado(s) · criterio %d' % (liberado.get(est, 0), quanto))

    # RENDER != EXPORT: bloquear a saida nao pode ter tirado ninguem da tela.
    exige(len(na_tela) == TOTAL_ESPERADO and sum(bloqueado.values()) > 0,
          'RENDER_NAO_E_EXPORT',
          'tela %d · bloqueados para fora %d — bloquear a saida nao pode '
          'esvaziar a tela' % (len(na_tela), sum(bloqueado.values())))

    return _fecha(falhas, passos, {
        'MEETING_SURFACE_TOTAL': len(na_tela),
        'POR_FAIXA': dict(contagem),
        'EXTERNAL_EXPORT_LIBERADO': dict(liberado),
        'EXTERNAL_EXPORT_BLOQUEADO': dict(bloqueado),
    })


def _fecha(falhas, passos, tela):
    r = {
        'COLLECTION': 'SURFACE_CONTRACT',
        'FILE': 'SURFACE-CONTRACT.json',
        'WHAT_IT_IS': 'o manifesto lido por um consumidor que nao interpreta nada',
        'CONTRACT': 'FAIL' if falhas else 'PASS',
        'LEI': 'o consumidor que le somente APP-MANIFEST + pacote precisa montar a '
               'superficie sem UMA decisao propria. Se alguma resposta exigir '
               'interpretacao do portal, CONTRACT = FAIL — e o defeito e do '
               'manifesto, nao do portal.',
        'DECISOES_QUE_O_PORTAL_TERIA_DE_ADIVINHAR': falhas,
        'O_QUE_O_CONSUMIDOR_MONTOU': tela,
        'PASSOS': passos,
    }
    os.makedirs(os.path.dirname(SAIDA), exist_ok=True)
    json.dump(r, open(SAIDA, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

    print('== R4 · CONTRATO DA SUPERFICIE ==')
    print('  perguntas respondidas pelo manifesto : %d/%d'
          % (sum(1 for p in passos if p['RESPONDIDA_PELO_MANIFESTO']), len(passos)))
    for k, v in sorted(tela.items()):
        print('  %-26s %s' % (k, v))
    print('\n  CONTRACT: %s' % r['CONTRACT'])
    if falhas:
        print('  O PORTAL TERIA DE ADIVINHAR:')
        for f in falhas:
            print('   · %s' % f)
    print('  gravado: %s' % SAIDA)
    return 1 if falhas else 0


if __name__ == '__main__':
    raise SystemExit(main())
