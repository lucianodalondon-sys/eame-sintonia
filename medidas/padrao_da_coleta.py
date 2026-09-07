#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O PADRAO DO DEPARTAMENTO DE COLETA — medido, e com chao que nao desce.

    py medidas/padrao_da_coleta.py            mede e compara com o chao
    py medidas/padrao_da_coleta.py --fixar    grava o estado de hoje como chao

POR QUE ESTE FICHEIRO EXISTE
-----------------------------
O mapa mediu seis coisas sobre a coleta desta casa, e as seis doem:

    · tres fontes foram coletadas SEM FICHA — as mais coletadas de todas
    · 22 de 26 fontes tem ficha e nunca foram buscadas
    · as dez corridas registadas foram todas num pais so
    · 15 coletores gravam registo sem data nem lugar
    · so 5 de 23 fontes tem contrato de busca escrito
    · o custo ficou guardado em 4 das 10 corridas; a hora, em 2

Medir uma vez nao conserta nada. Uma medicao que ninguem repete vira paragrafo, e
paragrafo nao segura ninguem numa sexta-feira a noite.

    O QUE NAO TEM CHAO, DESCE.

CHAO, E NAO META
----------------
Este portao NAO exige que os seis numeros estejam certos hoje. Exigir isso
reprovaria a casa inteira amanha de manha e a primeira coisa que alguem faria era
desligar o portao — e um portao desligado mede menos que nenhum.

Ele exige outra coisa, que da para cumprir hoje: **NAO PIORAR**. O estado de hoje
fica gravado como chao, e a partir daqui um coletor novo sem carimbo de data faz
o numero descer, e o portao reprova.

    «ESTA TUDO CERTO» NAO E EXECUTAVEL HOJE. «NAO PIOROU» E.

A divida fica a vista, com nome e numero, em vez de virar silencio. E quando
alguem a pagar, `--fixar` sobe o chao — e ele nunca mais desce.

O QUE E MEDIDO, E ONDE
-----------------------
Tudo sai do proprio repositorio, sem nada declarado a mao:

    ficha por fonte          docs/fontes/ATLAS-DE-FONTES-EAME.md
    contrato de busca        docs/operacao/CONTRATOS-DAS-FONTES-EAME.md
    carimbo de data e lugar  o codigo de cada coletor em coleta/ e regras/
    corrida, rendimento,     data/samples/RUN-MANIFEST.json
    custo e pais
"""

import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.dirname(HERE))   # a raiz
import _gavetas  # noqa: E402,F401 — poe as gavetas do processo no caminho

ATLAS = os.path.join(ROOT, 'docs', 'fontes', 'ATLAS-DE-FONTES-EAME.md')
CONTRATOS = os.path.join(ROOT, 'docs', 'operacao', 'CONTRATOS-DAS-FONTES-EAME.md')
MANIFESTO = os.path.join(ROOT, 'data', 'samples', 'RUN-MANIFEST.json')
CHAO = os.path.join(ROOT, 'data', 'samples', 'PADRAO-DA-COLETA-CHAO.json')
LEDGER = os.path.join(ROOT, 'data', 'collection-ledger', 'italy', 'observations.ndjson')
LEDGER_RUNS = os.path.join(ROOT, 'data', 'collection-ledger', 'italy', 'runs.ndjson')

GAVETAS_DE_COLETA = ('coleta', 'regras')
CARIMBO_DATA = ('CAPTURED_AT', 'PUBLICATION_DATE', 'FACT_DATE', 'CAPTURE_DATE')
MARCA_DESCARTE = ('EXCLUSION_REASON', 'DESCARTAD', 'RECUSAD', 'NOT_ELIGIBLE',
                  'EXCLUID', 'MOTIVO_DA_RECUSA', 'REJEIT')
VAZIO = ('NOT_PRESERVED', None, '', 'NAO SEI')

RE_ID = re.compile(r'^(EU|FR|ES|IT)-T\d{1,2}-\d{3}$')


def _texto(p):
    try:
        with open(p, encoding='utf-8', errors='replace') as f:
            return f.read()
    except OSError:
        return ''


def fichas_e_citadas():
    """Fonte com FICHA e fonte apenas CITADA em tabela sao coisas diferentes."""
    t, dentro, com_ficha = _texto(ATLAS), False, set()
    atual = None
    for linha in t.splitlines():
        if linha.strip().startswith('```'):
            if dentro and atual and RE_ID.match(atual):
                com_ficha.add(atual)
            dentro, atual = not dentro, None
            continue
        if dentro:
            m = re.match(r'^SOURCE_ID:\s*(\S+)', linha)
            if m:
                atual = m.group(1).strip()
    citadas = set(re.findall(r'^\|\s*`((?:EU|FR|ES|IT)-T\d{1,2}-\d{3})`\s*\|',
                             t, re.M))
    return com_ficha, citadas - com_ficha


def coletores():
    """Cada ficheiro das gavetas de coleta que GRAVA registo."""
    grava = re.compile(r'open\(|json\.dump|write_text')
    fora = []
    for g in GAVETAS_DE_COLETA:
        d = os.path.join(ROOT, g)
        if not os.path.isdir(d):
            continue
        for nome in sorted(os.listdir(d)):
            if not nome.endswith('.py'):
                continue
            t = _texto(os.path.join(d, nome))
            if grava.search(t):
                fora.append(('%s/%s' % (g, nome), t))
    return fora


def medir():
    com_ficha, so_citadas = fichas_e_citadas()
    contratos = set(re.findall(r'^SOURCE_ID\s{2,}(\S+)', _texto(CONTRATOS), re.M))

    cols = coletores()
    com_data = [n for n, t in cols if any(c in t for c in CARIMBO_DATA)]
    com_lugar = [n for n, t in cols
                 if 'SOURCE_LOCATION' in t and 'FACT_LOCATION' in t]
    com_descarte = [n for n, t in cols
                    if any(m in t.upper() for m in MARCA_DESCARTE)]

    runs = []
    if os.path.exists(MANIFESTO):
        try:
            runs = json.loads(_texto(MANIFESTO)).get('RUNS', [])
        except ValueError:
            runs = []
    coletadas = set()
    for r in runs:
        rid = r.get('RUN_ID', '')
        alvo = None
        for i in sorted(com_ficha | so_citadas, key=len, reverse=True):
            if rid.startswith(i):
                alvo = i
                break
        if alvo:
            coletadas.add(alvo)

    def cheio(campo):
        return [r['RUN_ID'] for r in runs if r.get(campo) not in VAZIO]

    # O REGISTO ITALIANO ENTRA NA MEDICAO — e o chao sobe com ele.
    #
    # A coleta de Italia guarda tres coisas que a espanhola nao guardava, e as
    # tres sao boas demais para ficarem so num pais:
    #
    #   RAW_SHA256      a impressao digital do documento. Testemunho nao e prova.
    #   FACT_TIME       o tempo do FACTO, separado do tempo da CAPTURA.
    #   CADENCE_STATE   quando a fonte DEVERIA publicar outra vez — sem isto,
    #                   uma fonte que morreu parece so uma fonte quieta.
    #
    # E nas corridas: EGRESS_IP, por onde a requisicao saiu. Numa coleta que
    # depende de sair por um pais, nao guardar isso e nao saber se o que voltou
    # veio do sitio certo.
    obs = []
    for caminho in (LEDGER,):
        if os.path.exists(caminho):
            for linha in _texto(caminho).splitlines():
                if linha.strip():
                    try:
                        obs.append(json.loads(linha))
                    except ValueError:
                        pass
    runs_it = []
    if os.path.exists(LEDGER_RUNS):
        for linha in _texto(LEDGER_RUNS).splitlines():
            if linha.strip():
                try:
                    runs_it.append(json.loads(linha))
                except ValueError:
                    pass

    return {
        'fontes_com_ficha': sorted(com_ficha),
        'fontes_so_citadas': sorted(so_citadas),
        'fontes_com_contrato_de_busca': sorted(contratos),
        'coletadas_sem_ficha': sorted(coletadas & so_citadas),
        'coletores': sorted(n for n, _ in cols),
        'coletores_que_carimbam_data': sorted(com_data),
        'coletores_que_separam_fonte_do_fato': sorted(com_lugar),
        'coletores_que_registam_descarte': sorted(com_descarte),
        # o que FALTA. E este numero que nao pode crescer: um coletor novo sem
        # carimbo entra aqui na hora, e o portao acorda.
        'coletores_SEM_data': sorted(n for n, _ in cols if n not in com_data),
        'coletores_SEM_lugar': sorted(n for n, _ in cols if n not in com_lugar),
        'coletores_SEM_descarte': sorted(n for n, _ in cols if n not in com_descarte),
        'corridas_SEM_rendimento': sorted(
            r.get('RUN_ID') for r in runs
            if not (isinstance(r.get('ITEM_COUNT_RAW'), int)
                    and isinstance(r.get('ITEM_COUNT_NORMALIZED'), int))),
        'corridas_SEM_custo': sorted(r.get('RUN_ID') for r in runs
                                     if r.get('COST_USD') in VAZIO),
        'corridas': [r.get('RUN_ID') for r in runs],
        'corridas_com_rendimento': sorted(
            r['RUN_ID'] for r in runs
            if isinstance(r.get('ITEM_COUNT_RAW'), int)
            and isinstance(r.get('ITEM_COUNT_NORMALIZED'), int)),
        'corridas_com_custo': sorted(cheio('COST_USD')),
        'corridas_com_hora': sorted(cheio('STARTED_AT')),
        'observacoes': [o.get('DOCUMENT_VERSION_ID') or o.get('DOCUMENT_ID')
                        for o in obs],
        'observacoes_SEM_sha256': [o.get('DOCUMENT_ID') for o in obs
                                   if not o.get('RAW_SHA256')],
        'observacoes_SEM_fact_time': [o.get('DOCUMENT_ID') for o in obs
                                      if o.get('FACT_TIME') in VAZIO],
        'observacoes_SEM_cadencia': [o.get('DOCUMENT_ID') for o in obs
                                     if o.get('CADENCE_STATE') in VAZIO],
        'corridas_SEM_egress': [r.get('RUN_ID') for r in runs_it
                                if r.get('EGRESS_IP') in VAZIO],
        '_runs_it': [r.get('RUN_ID') for r in runs_it],
        'paises_ja_exercitados': sorted({r.get('COUNTRY') for r in runs
                                         if r.get('COUNTRY') not in VAZIO}),
    }


# ── AS SEIS REGRAS ───────────────────────────────────────────────────────────
# Cada uma diz o que conta, e a frase que explica por que ela existe. A frase
# nao e enfeite: quem for reprovado por ela precisa de saber o que consertar.
REGRAS = [
    ('FONTE_TEM_FICHA_ANTES_DE_SER_COLETADA', 'coletadas_sem_ficha', 'menor',
     'Fonte coletada sem ficha e descoberta que a proxima pessoa vai refazer do '
     'zero, e pagar outra vez. Linha de tabela nao e ficha.'),
    ('COLETOR_CARIMBA_A_DATA', 'coletores_SEM_data', 'menor',
     'Data so vale se for posta NO MOMENTO da coleta. Depois e tarde: o dado ja '
     'entrou sem ela e ninguem recupera quando foi visto.'),
    ('COLETOR_SEPARA_A_FONTE_DO_FATO', 'coletores_SEM_lugar', 'menor',
     'Uma fonte italiana a falar de Espanha nao torna o facto italiano. '
     'SOURCE_LOCATION e FACT_LOCATION sao dois campos, e nao um.'),
    ('COLETOR_REGISTA_O_QUE_DESCARTOU', 'coletores_SEM_descarte', 'menor',
     'O que foi deixado de fora, e porque, e metade do que a coleta aprendeu. '
     'Sem isso, a proxima coleta repete o mesmo descarte sem saber.'),
    ('CORRIDA_MEDE_O_RENDIMENTO', 'corridas_SEM_rendimento', 'menor',
     'Trouxe quanto, sobrou quanto. A diferenca nao e desperdicio: e o filtro a '
     'trabalhar. So se sabe se ele trabalha bem com os dois numeros lado a lado.'),
    ('CORRIDA_GUARDA_O_CUSTO', 'corridas_SEM_custo', 'menor',
     'Coleta paga sem custo guardado e coleta que nunca se aprende a orcamentar.'),
    # ── o chao que subiu com a coleta italiana ──────────────────────────────
    ('DOCUMENTO_TEM_IMPRESSAO_DIGITAL', 'observacoes_SEM_sha256', 'menor',
     'Testemunho nao e prova. Sem SHA256, nada distingue o documento guardado de '
     'uma copia trocada — e a prova vira palavra.'),
    ('OBSERVACAO_SEPARA_O_TEMPO_DO_FATO_DA_CAPTURA', 'observacoes_SEM_fact_time', 'menor',
     'A data em que eu vi nao e a data em que aconteceu. Publicacao nao vira '
     'fact time.'),
    ('FONTE_DECLARA_QUANDO_VOLTA_A_PUBLICAR', 'observacoes_SEM_cadencia', 'menor',
     'Sem cadencia esperada, uma fonte que morreu parece so uma fonte quieta — e '
     'o silencio dela nunca vira aviso.'),
    ('CORRIDA_GUARDA_POR_ONDE_SAIU', 'corridas_SEM_egress', 'menor',
     'Numa coleta que depende de sair por um pais, nao guardar o IP de saida e '
     'nao saber se o que voltou veio do sitio certo.'),
]


def main():
    fixar = '--fixar' in sys.argv
    agora = medir()
    runs_it_n = agora['_runs_it']

    if fixar or not os.path.exists(CHAO):
        with open(CHAO, 'w', encoding='utf-8') as f:
            json.dump({
                'LEI': ('O chao do departamento de coleta. Nenhum destes numeros '
                        'pode descer. Subir e sempre permitido, e quando subir, '
                        'corra `--fixar` para o chao subir junto e nunca mais descer.'),
                'FIXADO_EM': agora,
            }, f, ensure_ascii=False, indent=2)
            f.write('\n')
        print('CHAO_FIXADO=OK · %s' % os.path.relpath(CHAO, ROOT))
        if fixar:
            return 0

    with open(CHAO, encoding='utf-8') as f:
        chao = json.load(f)['FIXADO_EM']

    print('PADRAO DA COLETA — o chao nao desce\n')
    falhou = False
    for nome, campo, sentido, porque in REGRAS:
        a, c = len(agora.get(campo, [])), len(chao.get(campo, []))
        pior = a > c if sentido == 'menor' else a < c
        seta = '=' if a == c else ('melhor' if (a < c) == (sentido == 'menor') else 'PIOROU')
        print('  %-6s %-40s faltam hoje %-3d  chao %-3d  %s'
              % ('FAIL' if pior else 'ok', nome, a, c, seta))
        if pior:
            falhou = True
            print('         %s' % porque)
            novos = sorted(set(agora.get(campo, [])) - set(chao.get(campo, []))) \
                if sentido == 'menor' else \
                sorted(set(chao.get(campo, [])) - set(agora.get(campo, [])))
            if novos:
                print('         mudou: %s' % ', '.join(novos[:6]))

    print('\n  A DIVIDA, hoje:')
    for r, t in (('fontes_so_citadas', 'fontes citadas em tabela, sem ficha'),
                 ('coletadas_sem_ficha', 'DESTAS, ja coletadas'),
                 ('paises_ja_exercitados', 'paises ja exercitados')):
        v = agora.get(r, [])
        print('    %-38s %s' % (t, ', '.join(v) if v else 'nenhuma'))
    print('    %-38s %d de %d' % ('coletores que carimbam data',
                                  len(agora['coletores_que_carimbam_data']),
                                  len(agora['coletores'])))
    print('    %-38s %d de %d' % ('fontes com contrato de busca',
                                  len(agora['fontes_com_contrato_de_busca']),
                                  len(agora['fontes_com_ficha'])))
    print('    %-38s %d de %d' % ('observacoes com impressao digital',
                                  len(agora['observacoes']) - len(agora['observacoes_SEM_sha256']),
                                  len(agora['observacoes'])))
    print('    %-38s %d de %d' % ('observacoes com tempo do fato',
                                  len(agora['observacoes']) - len(agora['observacoes_SEM_fact_time']),
                                  len(agora['observacoes'])))
    print('    %-38s %d de %d' % ('corridas com o IP de saida',
                                  len(runs_it_n) - len(agora['corridas_SEM_egress']),
                                  len(runs_it_n)))
    print('    %-38s %d de %d' % ('corridas com custo guardado',
                                  len(agora['corridas_com_custo']),
                                  len(agora['corridas'])))

    if falhou:
        print('\nPADRAO_DA_COLETA=FAIL · alguma coisa piorou desde o chao.')
        print('Se a mudanca for deliberada e justificada, corra --fixar e explique no commit.')
        return 1
    print('\nPADRAO_DA_COLETA=PASS · nada desceu.')
    return 0


if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except SystemExit:
        raise
    except Exception as e:   # falha fechado, como o resto da casa
        print('PADRAO_DA_COLETA=FAIL · erro inesperado: %s' % e, file=sys.stderr)
        raise SystemExit(1)
