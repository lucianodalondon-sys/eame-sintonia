#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O HANDOFF DO VOCABULARIO — 38 ISSUE_ID PROPOSTOS, MEDIDOS CONTRA O MOTOR REAL.

    python3 scripts/it_vocab_handoff.py

POR QUE ISTO NAO ALTERA NADA
-----------------------------
O motor canonico vive noutra branch (claude/opportunity-commercial-priority-v1,
b3935bd) e o dono unico dos ISSUE_* e o dicionario ISSUE_ALIAS de
scripts/v21_normalizar.py. Escrever nesse ficheiro a partir de uma branch de
coleta criaria um SEGUNDO DONO da mesma taxonomia: duas listas divergindo em
silencio, e nenhuma das duas sabendo que a outra existe.

    QUEM PROPOE VOCABULARIO NAO E QUEM O IMPLANTA.

Entao este script LE o motor da branch dele (git show, so leitura), simula a
adicao em memoria, e mede o que aconteceria. Nao escreve uma linha no motor.

O QUE ELE MEDE, E POR QUE CADA MEDIDA EXISTE
---------------------------------------------
1. ALIAS QUE NAO SOBREVIVE A NORMALIZACAO. O motor casa por LITERAL: `_n()`
   apaga tudo o que nao e letra ou digito. Um alias escrito como expressao
   regular ('carbone (?!attiv|medicinal)') vira a frase literal
   'carbone attiv medicinal', que nunca aparece em texto nenhum. Passa nos
   testes de regressao por nunca casar nada — e e exatamente por isso que e
   um defeito e nao uma protecao.

2. COLISAO. Um alias que ja pertence a outro ISSUE_ID daria dois donos a
   mesma palavra, e `_casa` desempataria pela ordem do dicionario. Ordem de
   dicionario nao e regra defensavel.

3. SEQUESTRO. `_casa` devolve o apelido MAIS LONGO. Um alias novo mais longo
   que contenha um alias antigo rouba o texto ao ID antigo. Isso pode estar
   certo — 'mosca della frutta' e mesmo mais especifico que 'mosca' — mas tem
   de aparecer no relatorio, medido, e nao acontecer por acidente.

4. REGRESSAO NO ACERVO. Rodo issues_no_texto ANTES e DEPOIS sobre os documentos
   italianos e conto o que cada ID existente perdeu e cada ID novo ganhou.
   Um ID existente que perde ocorrencias e uma incompatibilidade, nao um ganho.
"""
import json
import os
import re
import subprocess
import sys
import types
from collections import Counter, defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'scripts'))

MOTOR_BRANCH = 'claude/opportunity-commercial-priority-v1'
MOTOR_FILE = 'scripts/v21_normalizar.py'
PROPOSTA = 'data/samples/IT-ROTULOS-V1/IT-VOCAB-PROPOSTA-V1.json'
SAIDA = 'data/samples/IT-ROTULOS-V1/IT-VOCAB-HANDOFF-V1.json'


def _ref():
    """A referencia git do motor. Prefiro a remota: a local pode estar velha."""
    for ref in ('origin/' + MOTOR_BRANCH, MOTOR_BRANCH):
        p = subprocess.run(['git', 'rev-parse', '--verify', '--quiet', ref + '^{commit}'],
                           cwd=ROOT, capture_output=True, text=True)
        if p.returncode == 0:
            return ref, p.stdout.strip()
    raise SystemExit('branch do motor nao esta neste clone: git fetch origin ' + MOTOR_BRANCH)


def motor():
    """Carrega v21_normalizar da branch do motor SEM o escrever em disco."""
    ref, sha = _ref()
    src = subprocess.run(['git', 'show', f'{ref}:{MOTOR_FILE}'],
                         cwd=ROOT, capture_output=True, text=True, check=True).stdout
    mod = types.ModuleType('v21_normalizar_motor')
    mod.__dict__['__file__'] = f'{ref}:{MOTOR_FILE}'
    exec(compile(src, f'{ref}:{MOTOR_FILE}', 'exec'), mod.__dict__)
    return mod, ref, sha


def aprovados():
    d = json.load(open(os.path.join(ROOT, PROPOSTA)))
    linhas = [r for r in d['ROWS'] if r.get('FINAL_DECISION') == 'NEEDS_NEW_ISSUE_ID']
    return d, linhas


def alias_vivos(r):
    """Os apelidos que a regressao do censo aprovou. Os rejeitados ficam fora."""
    return [a['ALIAS'] for a in r.get('ALIASES', [])
            if a.get('REGRESSION') == 'OK']


def main():
    M, ref, sha = motor()
    doc, linhas = aprovados()
    N, CASA, TODOS = M._n, M._casa, M._todos
    VELHO = {k: list(v) for k, v in M.ISSUE_ALIAS.items()}

    # dono de cada apelido existente, ja normalizado
    dono = {}
    for eid, apel in VELHO.items():
        for a in apel:
            dono.setdefault(N(a), eid)

    novos, incompat = {}, []
    for r in linhas:
        iid = r['PROPOSED_ISSUE_ID']
        vivos = []
        for a in alias_vivos(r):
            na = N(a)
            # 1 · sobrevive a normalizacao?
            if not na:
                incompat.append({'ISSUE_ID': iid, 'ALIAS': a, 'TIPO': 'ALIAS_VAZIO_APOS_NORMALIZACAO',
                                 'PORQUE': '_n() nao deixa nada: o apelido nunca casaria'})
                continue
            # So flago o que denuncia INTENCAO DE REGEX. Hifen, apostrofo,
            # virgula e ponto sao inofensivos: _n() cai sobre os dois lados,
            # o apelido e o texto, e 'collo-cygni' casa 'collo cygni' em ambos.
            if re.search(r'\(\?|[\\|\[\]{}*+^$]|\?', a):
                incompat.append({'ISSUE_ID': iid, 'ALIAS': a, 'TIPO': 'ALIAS_NAO_E_LITERAL',
                                 'VIRARIA': na,
                                 'PORQUE': 'o apelido foi escrito como expressao regular. O motor '
                                           'nao aceita regex: _n() apaga os metacaracteres e o '
                                           'apelido vira uma frase literal que nunca aparece em '
                                           'texto nenhum. Passaria na regressao por nunca casar '
                                           'nada — e por isso e um defeito, nao uma protecao.'})
                continue
            # 2 · colisao com dono existente
            if na in dono:
                incompat.append({'ISSUE_ID': iid, 'ALIAS': a, 'TIPO': 'COLISAO_COM_ID_EXISTENTE',
                                 'DONO_ATUAL': dono[na],
                                 'PORQUE': 'dois donos do mesmo apelido; _casa desempata pela '
                                           'ordem do dicionario, que nao e regra'})
                continue
            vivos.append(a)
            dono[na] = iid
        if vivos:
            novos[iid] = vivos
        else:
            incompat.append({'ISSUE_ID': iid, 'ALIAS': None, 'TIPO': 'FICA_SEM_APELIDO_UTILIZAVEL',
                             'PORQUE': 'todos os apelidos cairam nos testes acima'})

    # 3 · sequestro: apelido novo que contem apelido antigo (o mais longo ganha)
    sequestro = []
    for iid, apel in novos.items():
        for a in apel:
            na = ' %s ' % N(a)
            for velho_a, velho_id in list(dono.items()):
                if velho_id in novos or not velho_a:
                    continue
                if ' %s ' % velho_a in na:
                    sequestro.append({'ALIAS_NOVO': a, 'ISSUE_ID_NOVO': iid,
                                      'ALIAS_ANTIGO': velho_a, 'ISSUE_ID_ANTIGO': velho_id,
                                      'EFEITO': 'texto que hoje da %s passa a dar %s quando a '
                                                'frase mais longa aparece' % (velho_id, iid)})

    # 4 · regressao medida no acervo italiano
    import it_futuro_corpus as C
    docs = list(C.corpus())
    NOVA = {k: list(v) for k, v in VELHO.items()}
    NOVA.update(novos)

    antes, depois, exemplos = Counter(), Counter(), defaultdict(list)
    perdas = defaultdict(list)
    for d in docs:
        for fr in C.frases(d['TEXT']):
            a = TODOS(fr, VELHO)
            b = TODOS(fr, NOVA)
            for x in a:
                antes[x] += 1
            for x in b:
                depois[x] += 1
            for x in set(a) - set(b):
                if len(perdas[x]) < 3:
                    perdas[x].append({'SOURCE_ID': d['SOURCE_ID'], 'FRASE': fr[:220]})
            for x in set(b) - set(a):
                if x in novos and len(exemplos[x]) < 3:
                    # a frase vai INTEIRA. Truncada, o apelido pode ficar de fora
                    # do corte e a ancora deixa de provar o que diz provar.
                    exemplos[x].append({'SOURCE_ID': d['SOURCE_ID'], 'FRASE': fr})

    perdeu = {k: antes[k] - depois[k] for k in VELHO if depois[k] < antes[k]}
    ganhou = {k: depois[k] for k in novos if depois[k]}
    mudos = sorted(k for k in novos if not depois[k])

    # 8 · o teste minimo: uma frase real por ID novo que ganhou ocorrencia
    teste = []
    for iid in sorted(ganhou):
        e = exemplos[iid][0]
        teste.append({'ISSUE_ID': iid, 'SOURCE_ID': e['SOURCE_ID'],
                      'FRASE': e['FRASE'],
                      'ESPERADO': 'issues_no_texto(FRASE) contem %s' % iid})

    rows = []
    for r in linhas:
        iid = r['PROPOSED_ISSUE_ID']
        rows.append({
            'ISSUE_ID_PROPOSTO': iid,
            'TERMO_ATUAL_NO_ROTULO': r['TARGET'],
            'TERMO_ATUAL_NO_MOTOR': 'NENHUM — o motor nao tem ID para este alvo',
            'IDENTIDADE': r['IDENTITY'],
            'APELIDOS_PROPOSTOS': novos.get(iid, []),
            'APELIDOS_RECUSADOS_AQUI': [x['ALIAS'] for x in incompat if x['ISSUE_ID'] == iid],
            'APELIDOS_RECUSADOS_NA_REGRESSAO_DO_CENSO': r.get('ALIASES_REJECTED_BY_REGRESSION', []),
            'EVIDENCIA': r.get('EVIDENCE'),
            'RISCO_DE_SINAL_FALSO': r.get('RISK_OF_FALSE_SIGNAL'),
            'CONFIANCA': r.get('CONFIDENCE'),
            'OCORRENCIAS_NO_ACERVO_DEPOIS': depois.get(iid, 0),
            'EXEMPLOS': exemplos.get(iid, []),
            'IMPACTO': ('passa a reconhecer %d trechos que hoje nao reconhece' % depois[iid])
                       if depois.get(iid) else
                       ('nenhum trecho do acervo actual o nomeia: entra para os ROTULOS, '
                        'que e onde o alvo aparece, e fica mudo no acervo de fala'),
            # Um apelido que EU retirei aqui (regex escrita num campo que so
            # aceita literal) e reparo medido, nao duvida: o que fica e mais
            # estreito do que o que foi proposto, nunca mais largo. O que exige
            # gente e outra coisa — confianca MEDIA na propria identidade do
            # alvo, ou dois donos disputando o mesmo apelido.
            'REPARO_APLICADO_AQUI': [x['ALIAS'] for x in incompat
                                     if x['ISSUE_ID'] == iid and x['TIPO'] == 'ALIAS_NAO_E_LITERAL'],
            'SEM_JULGAMENTO_HUMANO': (r.get('CONFIDENCE') == 'HIGH'
                                      and iid in novos
                                      and not any(x['ISSUE_ID'] == iid
                                                  and x['TIPO'] != 'ALIAS_NAO_E_LITERAL'
                                                  for x in incompat)
                                      and iid not in perdeu),
        })

    saida = {
        'DATASET': 'IT-VOCAB-HANDOFF-V1',
        'LAYER': 'CONTROLLED VOCABULARY — HANDOFF, nao implantacao',
        'COUNTRY': 'IT',
        'SOURCE_ID': 'IT-VOCAB-PROPOSTA-V1',
        'CAPTURED_AT': '2026-09-04',
        'SOURCE': 'proposta do censo dos alvos, medida contra o motor canonico lido da branch dele',
        'BRANCH_ATUAL': subprocess.run(['git', 'rev-parse', '--abbrev-ref', 'HEAD'], cwd=ROOT,
                                       capture_output=True, text=True).stdout.strip(),
        'BRANCH_DO_MOTOR': MOTOR_BRANCH,
        'MOTOR_REF_LIDA': ref,
        'MOTOR_SHA': sha,
        'DONO_DA_TAXONOMIA': '%s:%s — o dicionario ISSUE_ALIAS' % (MOTOR_BRANCH, MOTOR_FILE),
        'QUEM_CONSOME': ['scripts/v21_ingest.py', 'scripts/v21_ingest_b.py',
                         'scripts/v21_janelas.py', 'scripts/v21_comercial.py',
                         'scripts/v21_necessidade.py', 'scripts/v21_defeitos_do_vinculo.py',
                         'scripts/v21_censo_das_16_janelas.py', 'scripts/v21_vao_de_janelas.py',
                         'scripts/v21_geografia_contrato.py',
                         'scripts/v21_regressao_do_red_team.py',
                         'tests/test_prioridade_comercial.py'],
        'FORMATO_ACEITE_PELO_MOTOR': (
            "ISSUE_ALIAS[ISSUE_<NOME>] = [apelido, ...]. Apelido e LITERAL minusculo sem "
            "acentos; o motor normaliza com _n() (apaga tudo o que nao e [a-z0-9]) e casa por "
            "PALAVRA INTEIRA, escolhendo o apelido MAIS LONGO. Nao aceita expressao regular, "
            "nao aceita lookahead, nao aceita exclusao."),
        'CONTRATO_MUDA': False,
        'PORQUE_O_CONTRATO_NAO_MUDA': (
            'a adicao e so de chaves novas num dicionario existente. Nenhuma assinatura de '
            'funcao muda, nenhum ID existente e renomeado ou removido, e nenhum consumidor '
            'precisa de saber que ha mais chaves.'),
        'ISSUE_IDS_EXISTENTES': len(VELHO),
        'ISSUE_IDS_PROPOSTOS': len(linhas),
        'ISSUE_IDS_IMPLANTAVEIS': len(novos),
        'INCOMPATIBILIDADES': incompat,
        'SEQUESTROS': sequestro,
        'IDS_EXISTENTES_QUE_PERDEM_OCORRENCIAS': perdeu,
        'EXEMPLOS_DAS_PERDAS': {k: v for k, v in perdas.items() if k in perdeu},
        'IDS_NOVOS_QUE_GANHAM_OCORRENCIAS': ganhou,
        'IDS_NOVOS_MUDOS_NO_ACERVO_DE_FALA': mudos,
        'DOCUMENTOS_DA_REGRESSAO': len(docs),
        'TESTE_MINIMO': teste,
        'ARQUIVOS_QUE_PRECISARIAM_MUDAR': [
            '%s:%s — acrescentar as chaves novas a ISSUE_ALIAS' % (MOTOR_BRANCH, MOTOR_FILE),
            '%s:tests/ — um teste que ancore cada ID novo numa frase real do acervo'
            % MOTOR_BRANCH],
        'O_QUE_NAO_FAZER': (
            'nao editar v21_normalizar.py a partir desta branch, nao fazer cherry-pick para ca, '
            'nao copiar ISSUE_ALIAS para scripts/it_rotulo_vocab.py. Qualquer das tres cria um '
            'segundo dono da mesma taxonomia.'),
        'ROWS': rows,
    }
    saida['PODE_ENTRAR_SEM_JULGAMENTO_HUMANO'] = sorted(
        r['ISSUE_ID_PROPOSTO'] for r in rows if r['SEM_JULGAMENTO_HUMANO'])
    saida['EXIGE_DECISAO_HUMANA'] = sorted(
        r['ISSUE_ID_PROPOSTO'] for r in rows if not r['SEM_JULGAMENTO_HUMANO'])

    with open(os.path.join(ROOT, SAIDA), 'w') as f:
        json.dump(saida, f, ensure_ascii=False, indent=1)

    print('MOTOR            ', ref, sha[:12])
    print('IDS EXISTENTES   ', len(VELHO))
    print('IDS PROPOSTOS    ', len(linhas))
    print('IMPLANTAVEIS     ', len(novos))
    print('INCOMPATIBILIDADES', len(incompat))
    for x in incompat:
        print('   ', x['TIPO'], x['ISSUE_ID'], repr(x['ALIAS']))
    print('SEQUESTROS       ', len(sequestro))
    for x in sequestro:
        print('   ', x['ALIAS_ANTIGO'], '->', x['ALIAS_NOVO'], x['ISSUE_ID_ANTIGO'], '->', x['ISSUE_ID_NOVO'])
    print('IDS QUE PERDEM   ', perdeu or 'nenhum')
    print('IDS NOVOS ATIVOS ', len(ganhou), 'de', len(novos))
    print('IDS NOVOS MUDOS  ', len(mudos))
    print('SEM JULGAMENTO   ', len(saida['PODE_ENTRAR_SEM_JULGAMENTO_HUMANO']))
    print('EXIGE DECISAO    ', len(saida['EXIGE_DECISAO_HUMANA']), saida['EXIGE_DECISAO_HUMANA'])
    print('->', SAIDA)


if __name__ == '__main__':
    main()
