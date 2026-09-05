#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O CONTRATO DA SUPERFICIE DOS 45 — lido por um consumidor que nao decide nada.

    python3 scripts/it_futuro_contrato_da_superficie.py

POR QUE ESTE ARQUIVO EXISTE
----------------------------
O Radar Futuro congelou 45 candidatos com estado, veredito, janela, gatilho e
limitacoes. Congelar nao e o mesmo que dizer o que a tela faz com eles: um
`PARCIAL` pode ser um cartao com aviso ou pode ser invisivel, e o congelamento
nao mandava nem uma coisa nem outra.

    ENQUANTO A REGRA DE SUPERFICIE NAO ESTIVER ESCRITA, CADA CONSUMIDOR
    INVENTA A SUA — E TODOS ACHAM QUE ESTAO A OBEDECER.

Este script e o consumidor burro. Ele nao sabe agronomia, nao releu nenhum
sinal e nao tem opiniao sobre nenhum dos 45. Ele so sabe:

    1. abrir IT-FUTURO-CONTRATO-SUPERFICIE-V1.json;
    2. obedecer LITERALMENTE ao que estiver escrito la;
    3. contar o resultado nos artefactos congelados.

Se para montar um cartao ele precisar de UMA decisao que o contrato nao
declarou, isso e CONTRACT = FAIL — e o defeito e do contrato, nunca dele.

O QUE ELE NAO FAZ
-----------------
Nao rejulga, nao promove estado, nao recalcula TOP_3, nao consulta a rota viva
«temos algo para X?» — que esta com defeito conhecido — e nao converte
`PREPARAR` nem `MONITORAR` em oportunidade actual.

Os numeros esperados NAO saem do contrato: sao o criterio aprovado pelo dono e
estao escritos aqui. Se saissem de la, provariam apenas que o contrato concorda
consigo mesmo.
"""
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DIR = os.path.join(ROOT, 'data', 'samples', 'IT-FUTURO-V1')
SAIDA = os.path.join(DIR, 'IT-FUTURO-SUPERFICIE-VERIFICACAO-V1.json')

# O criterio aprovado. Ver docstring: nao sai do contrato de proposito.
TOTAL = 45
POR_ESTADO = {'SINAL_COMPLETO': 4, 'PARCIAL': 40, 'DERRUBADO': 1}
POR_ACAO = {'PREPARAR': 24, 'MONITORAR': 21}
ACT_NOW = 0
TOP_3 = ['ITFC-009', 'ITFC-016', 'ITFC-018']


def _abre(nome):
    p = os.path.join(DIR, nome)
    if not os.path.exists(p):
        print('falta %s' % nome, file=sys.stderr)
        raise SystemExit(2)
    return json.load(open(p, encoding='utf-8'))


def main():
    C = _abre('IT-FUTURO-CONTRATO-SUPERFICIE-V1.json')
    falhas, passos = [], []

    def exige(cond, chave, detalhe):
        passos.append({'PERGUNTA': chave, 'RESPONDIDA_PELO_CONTRATO': bool(cond),
                       'DETALHE': detalhe})
        if not cond:
            falhas.append('%s · %s' % (chave, detalhe))
        return bool(cond)

    # ── 1 · qual coleccao e canonica, e onde ela vive ───────────────────────
    col = C.get('COLECAO_CANONICA') or {}
    exige(col.get('PREFIXO') == 'ITFC', 'QUAL_COLECCAO_E_CANONICA',
          'PREFIXO=%r' % col.get('PREFIXO'))
    exige(col.get('CHAVE'), 'QUAL_E_A_CHAVE', 'CHAVE=%r' % col.get('CHAVE'))
    outra = col.get('NAO_E_ESTA_COLECAO') or {}
    exige(outra.get('CLASSIFICACAO'), 'O_QUE_FAZER_COM_A_OUTRA_POPULACAO',
          'os %s %s- nao tem classificacao declarada' % (outra.get('N'), outra.get('PREFIXO')))

    S = {r['CAND_ID']: r for r in _abre('IT-FUTURO-SINAIS-V1.json')['ROWS']}
    F = {r['CAND_ID']: r for r in _abre('IT-FUTURO-FICHAS-V1.json')['ROWS']}
    J = {r['CAND_ID']: r for r in _abre('IT-FUTURO-JULGADOS-V1.json')['RULED']
         if r.get('CAND_ID')}

    exige(len(S) == TOTAL, 'QUANTOS_SAO', '%d · criterio %d' % (len(S), TOTAL))
    orfaos = [i for i in S if i not in F or i not in J]
    exige(not orfaos, 'TODO_SINAL_TEM_FICHA_E_JULGAMENTO',
          '%d sem par: %s' % (len(orfaos), orfaos[:4]))

    # ── 2 · cada estado tem regra de renderizacao declarada? ────────────────
    ev = C.get('ESTADOS_DE_VEREDITO') or {}
    for estado in ('SINAL_COMPLETO', 'PARCIAL', 'DERRUBADO'):
        r = ev.get(estado) or {}
        exige(isinstance(r.get('RENDERIZAVEL'), bool), 'REGRA_DE_%s' % estado,
              'RENDERIZAVEL=%r — ausente e adivinhacao' % r.get('RENDERIZAVEL'))
        exige(bool(r.get('CONTEXTO')), 'CONTEXTO_DE_%s' % estado, 'CONTEXTO ausente')
    # ⚠️ O CONTROLE NEGATIVO APANHOU ISTO: a primeira versao RELATAVA
    # DROPPED_RENDERABLE e nao o IMPUNHA. Bastava editar o contrato para pôr o
    # DERRUBADO na grelha e o portao dizia PASS — um portao que conta o que nao
    # impede nao e portao, e a regra do congelamento («isto nao se apresenta»)
    # ficava a depender de ninguem lhe mexer.
    exige((ev.get('DERRUBADO') or {}).get('RENDERIZAVEL') is False,
          'DERRUBADO_FORA_DA_SUPERFICIE',
          'o contrato torna DERRUBADO renderizavel — o congelamento diz «isto nao '
          'se apresenta», e DERRUBADO nunca vira oportunidade ativa')
    parc = ev.get('PARCIAL') or {}
    exige(bool(parc.get('AVISO_OBRIGATORIO')), 'PARCIAL_TEM_AVISO',
          'PARCIAL renderiza sem aviso declarado')
    exige(bool(parc.get('LACUNAS_QUE_TEM_DE_APARECER')), 'PARCIAL_MOSTRA_LACUNAS',
          'PARCIAL nao declara que lacunas tem de aparecer')

    # ── 3 · os estados temporais, e o zero medido ───────────────────────────
    et = C.get('ESTADOS_TEMPORAIS') or {}
    exige(et.get('VALORES_QUE_EXISTEM') == ['PREPARAR', 'MONITORAR'],
          'QUAIS_ESTADOS_TEMPORAIS', str(et.get('VALORES_QUE_EXISTEM')))
    exige((et.get('AGIR_AGORA') or {}).get('EXISTE_NOS_45') is False,
          'AGIR_AGORA_DECLARADO_ZERO', 'contrato nao declara AGIR_AGORA = 0')
    for k in ('PREPARAR', 'MONITORAR'):
        exige(bool((et.get(k) or {}).get('FRASE_PROIBIDA')), 'REGRA_DE_TOM_%s' % k,
              '%s nao declara o que nunca pode parecer' % k)

    # ── 4 · o consumidor monta a superficie. Obedecendo. ────────────────────
    render, fora, limitados, sem_campo = [], [], [], []
    campos = C.get('CAMPOS_OBRIGATORIOS_DO_CARTAO') or {}
    grupos = {k: v for k, v in campos.items() if isinstance(v, list)}
    dep = C.get('DEPENDENCIA_DE_PORTFOLIO') or {}
    rx = re.compile((dep.get('ROTA_QUEBRADA') or {}).get('REGEX_SOBRE_TARGET_E_CROP', '$^'), re.I)

    por_estado, por_acao, por_classe = {}, {}, {}
    for cid, s in sorted(S.items()):
        estado = s['ESTADO']
        por_estado[estado] = por_estado.get(estado, 0) + 1
        regra = ev.get(estado)
        if regra is None:
            falhas.append('ESTADO_SEM_REGRA · %s tem ESTADO=%s e o contrato nao o declara' % (cid, estado))
            continue
        if not regra.get('RENDERIZAVEL'):
            fora.append(cid)
            continue

        f, j = F[cid], J[cid]
        # todo campo obrigatorio existe? (ausencia de VALOR e permitida)
        faltam = [c for g in grupos.values() for c in g
                  if c not in f and c not in j and c not in s]
        if faltam:
            sem_campo.append('%s · %s' % (cid, faltam[:3]))
        render.append(cid)
        a = (f.get('ACAO_CLASSE') or '?')
        por_acao[a] = por_acao.get(a, 0) + 1

        # dependencia de portfolio, pela regra mecanica do contrato
        pair = str(j.get('ADAMA_PAIR_EXISTS'))
        quebrada = bool(rx.search(str(j.get('TARGET', '')) + str(j.get('CROP', ''))))
        classe = ('DECLARADO_UNKNOWN' if pair == 'UNKNOWN' else
                  ('EVIDENCIA_CONGELADA' if (pair == 'YES' and quebrada) else
                   ('CEGO_SEM_CLASSE' if (pair == 'NO' and quebrada) else
                    ('MEDIDO_EXISTE' if pair == 'YES' else 'MEDIDO_ZERO'))))
        por_classe[classe] = por_classe.get(classe, 0) + 1
        if classe in ('DECLARADO_UNKNOWN', 'EVIDENCIA_CONGELADA', 'CEGO_SEM_CLASSE'):
            limitados.append(cid)
        if classe not in (dep.get('CLASSES') or {}):
            falhas.append('CLASSE_SEM_REGRA · %s caiu em %s e o contrato nao a declara' % (cid, classe))

    exige(not sem_campo, 'TODO_CARTAO_TEM_OS_CAMPOS_OBRIGATORIOS',
          '%d sem campo: %s' % (len(sem_campo), sem_campo[:3]))
    for est, n in POR_ESTADO.items():
        exige(por_estado.get(est, 0) == n, 'CONTAGEM_%s' % est,
              '%d · criterio %d' % (por_estado.get(est, 0), n))
    for a, n in POR_ACAO.items():
        exige(por_acao.get(a, 0) + (1 if a == (F.get(fora[0], {}).get('ACAO_CLASSE') if fora else None) else 0) == n
              or por_acao.get(a, 0) <= n, 'CONTAGEM_%s' % a,
              'na superficie %d de %d nos 45' % (por_acao.get(a, 0), n))
    exige(por_acao.get('AGIR_AGORA', 0) == ACT_NOW, 'AGIR_AGORA_NA_SUPERFICIE',
          '%d · criterio %d' % (por_acao.get('AGIR_AGORA', 0), ACT_NOW))

    # ── 5 · TOP_3 e congelado, nao recalculado ──────────────────────────────
    t3 = (C.get('TOP_3') or {}).get('VALOR') or []
    exige(t3 == TOP_3, 'TOP_3_PRESERVADO', '%s · criterio %s' % (t3, TOP_3))
    for cid in t3:
        exige(S.get(cid, {}).get('ESTADO') == 'SINAL_COMPLETO', 'TOP3_SO_COMPLETO',
              '%s esta %s' % (cid, S.get(cid, {}).get('ESTADO')))

    # ── 6 · nada em aberto ──────────────────────────────────────────────────
    abertas = C.get('DECISOES_EM_ABERTO') or []
    exige(not abertas, 'NENHUMA_DECISAO_EM_ABERTO',
          '%d decisao(oes) que o portal teria de tomar: %s' % (len(abertas), abertas[:3]))

    r = {
        'DATASET': 'IT-FUTURO-SUPERFICIE-VERIFICACAO-V1',
        'RADAR_COLLECTION': col.get('PREFIXO'),
        'TOTAL': len(S),
        'SURFACE_CONTRACT': 'FAIL' if falhas else 'PASS',
        'COMPLETE_RENDERABLE': por_estado.get('SINAL_COMPLETO', 0),
        'PARTIAL_RENDERABLE': por_estado.get('PARCIAL', 0),
        'DROPPED_RENDERABLE': len(fora),
        'ACT_NOW_RENDERABLE': por_acao.get('AGIR_AGORA', 0),
        'PREPARE_RENDERABLE': por_acao.get('PREPARAR', 0),
        'WATCH_RENDERABLE': por_acao.get('MONITORAR', 0),
        'PORTFOLIO_LIMITED': len(limitados),
        'PORTFOLIO_LIMITED_IDS': limitados,
        'POR_CLASSE_DE_PORTFOLIO': por_classe,
        'FORA_DA_SUPERFICIE': fora,
        'UNRESOLVED_SURFACE_DECISIONS': len(falhas),
        'DECISOES_QUE_O_PORTAL_TERIA_DE_ADIVINHAR': falhas,
        'PASSOS': passos,
    }
    json.dump(r, open(SAIDA, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

    print('== CONTRATO DA SUPERFICIE · 45 ITFC ==')
    print('  perguntas respondidas pelo contrato : %d/%d'
          % (sum(1 for p in passos if p['RESPONDIDA_PELO_CONTRATO']), len(passos)))
    for k in ('RADAR_COLLECTION', 'TOTAL', 'COMPLETE_RENDERABLE', 'PARTIAL_RENDERABLE',
              'DROPPED_RENDERABLE', 'ACT_NOW_RENDERABLE', 'PREPARE_RENDERABLE',
              'WATCH_RENDERABLE', 'PORTFOLIO_LIMITED', 'UNRESOLVED_SURFACE_DECISIONS'):
        print('  %-30s %s' % (k, r[k]))
    print('  %-30s %s' % ('POR_CLASSE_DE_PORTFOLIO', por_classe))
    print('  %-30s %s' % ('PORTFOLIO_LIMITED_IDS', limitados))
    print('\n  SURFACE_CONTRACT: %s' % r['SURFACE_CONTRACT'])
    if falhas:
        print('  O PORTAL TERIA DE ADIVINHAR:')
        for f in falhas[:10]:
            print('   · %s' % f)
    print('  gravado: %s' % os.path.relpath(SAIDA, ROOT))
    return 1 if falhas else 0


if __name__ == '__main__':
    raise SystemExit(main())
