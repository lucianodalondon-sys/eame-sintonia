#!/usr/bin/env python3
"""O CENSO DAS CLASSES DE ESTRADA DA COLETA ITALIANA.

    python3 system-map/scripts/censo_das_estradas_it.py

A unidade de analise nao e a fonte. E a CLASSE DE ESTRADA — o conjunto de
fontes que compartilham a mesma cadeia operacional:

    DISCOVER -> FETCH -> RAW -> RUN -> CHECKPOINT -> DERIVED
             -> STRUCTURED -> ADMISSION

Uma fonte nova numa estrada ja fechada nao e missao: e configuracao. So estrada
NOVA justifica canario novo.

O vocabulario de classe NAO foi inventado aqui: `leis/social_matriz.py` ja
declara `CLASSE` por rota, e as classes nao-sociais saem do codigo medido. O
que este script faz e CONTAR, para que o mapa em
`docs/operacao/MAPA-DE-FECHAMENTO-DA-COLETA-ITALIANA.md` nunca dependa de
memoria.
"""
import collections
import json
import os
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(os.path.dirname(AQUI))
sys.path.insert(0, RAIZ)
import _gavetas  # noqa: E402,F401
import social_matriz as mz          # noqa: E402
import fundacao_da_coleta as fdc    # noqa: E402

CATALOGO = os.path.join(RAIZ, 'candidatas', 'ITALY-SOURCE-MASTER-V1.json')
SAIDA = os.path.join(RAIZ, 'system-map', 'data', 'estradas-it.generated.json')
LEDGER_GIT = os.path.join(RAIZ, 'data', 'collection-ledger', 'italy')


def fontes_it():
    with open(CATALOGO, encoding='utf-8') as f:
        return json.load(f).get('sources') or []


def rota_conhecida(fonte):
    """A rota da fonte esta declarada, ou o catalogo diz NAO SEI?

    `NAO SEI` e uma resposta legitima e por isso e CONTADA, nunca convertida
    em palpite. Enquanto ela existir, ninguem sabe quantas missoes faltam.
    """
    return not str(fonte.get('ACCESS_METHOD') or '').upper().startswith('NÃO SEI')


def classes_sociais():
    """As classes que a matriz social ja declara, com quantas rotas permitidas."""
    dec, perm, sem_razao = collections.Counter(), collections.Counter(), 0
    for _plat, caps in mz.MATRIZ.items():
        for cap, rotas in caps.items():
            if cap.startswith('_') or not isinstance(rotas, (list, tuple)):
                continue
            for r in rotas:
                if not isinstance(r, dict):
                    continue
                dec[r.get('CLASSE')] += 1
                if r.get('PERMITIDA') == 'SIM':
                    perm[r.get('CLASSE')] += 1
                if not str(r.get('NOTA') or '').strip():
                    sem_razao += 1
    return dec, perm, sem_razao


def apify():
    """Apify e default em alguma rota? A pergunta que a casa mais erra de cabeca."""
    default = fallback = 0
    for _plat, caps in mz.MATRIZ.items():
        for cap, rotas in caps.items():
            if cap.startswith('_') or not isinstance(rotas, (list, tuple)):
                continue
            for r in rotas:
                if isinstance(r, dict) and 'apify' in str(r.get('ROTA', '')).lower():
                    if r.get('PRIORIDADE') == 1:
                        default += 1
                    else:
                        fallback += 1
    return default, fallback


def git_como_banco():
    """Onde o Git ainda guarda estado operacional. Historico nao se apaga."""
    achados = []
    if os.path.isdir(LEDGER_GIT):
        for n in sorted(os.listdir(LEDGER_GIT)):
            caminho = os.path.join(LEDGER_GIT, n)
            with open(caminho, encoding='utf-8', errors='ignore') as f:
                linhas = sum(1 for _ in f)
            achados.append({'FICHEIRO': os.path.relpath(caminho, RAIZ).replace('\\', '/'),
                            'LINHAS': linhas})
    return achados


# ═════════════════════════════════════════════════════════════════════════
# AS CLASSES DE ESTRADA — MEDIDAS, NAO DECLARADAS
# ═════════════════════════════════════════════════════════════════════════
# O MODELO diz quais etapas cada estrada tem e quem SERIA o dono. Este censo
# mede duas coisas diferentes, que a versao anterior deste mapa confundiu:
#
#     OWNER_EXISTS        o ficheiro do dono existe no disco
#     CONNECTED_TO_ROUTE  esse ficheiro toca o artefato da etapa anterior
#
#     OWNER EXISTS NAO E OWNER CONNECTED.
#
# Foi exatamente aqui que a RC-1 foi promovida cedo demais: `importar_italia.py`
# existe e escreve estrutura — mas nao le `derived_artifact` nenhum. Ele lia
# outros artefatos JSON e gerava SQL por conta propria. Um writer existir nao
# prova que ele e o writer DESTA estrada.
MODELO = os.path.join(RAIZ, 'system-map', 'data', 'estradas-it.model.json')

# O vocabulario de estado ja e da casa. `CODE` nunca vira `OBSERVED` por
# simpatia: sao duas perguntas, e uma delas custa uma execucao real.
ESTADOS = ('UNKNOWN', 'DECLARED', 'CODE', 'LOCAL_TESTED', 'DB_TESTED',
           'LIVE_SCHEMA', 'OBSERVED', 'BLOCKED', 'NOT_APPLICABLE')

# Estados que provam que a etapa ACONTECEU, nao so que ha codigo para ela.
ESTADOS_OBSERVADOS = ('OBSERVED',)
ESTADOS_PROVADOS_EM_BANCO = ('DB_TESTED', 'LIVE_SCHEMA')

ETAPAS = ('DISCOVER', 'FETCH', 'RAW', 'RUN', 'CHECKPOINT', 'DERIVED',
          'STRUCTURED', 'ADMISSION')


def _existe(caminho):
    return bool(caminho) and os.path.exists(os.path.join(RAIZ, caminho))


def _liga(edge):
    """A aresta e MEDIDA: o ficheiro do dono cita o artefato da etapa anterior?

    Grep e um instrumento grosseiro, e e de proposito que ele seja o mesmo para
    todas as estradas: um criterio que muda por estrada deixa de comparar. O que
    ele responde e estreito e honesto — «este ficheiro sequer MENCIONA aquilo?».
    Um NAO aqui e definitivo: quem nao menciona nao pode estar ligado.
    """
    if not edge:
        return None                      # etapa sem aresta a medir (ex.: catalogo)
    ficheiro, agulha = edge
    caminho = os.path.join(RAIZ, ficheiro)
    if not os.path.exists(caminho):
        return False
    with open(caminho, encoding='utf-8', errors='ignore') as f:
        return agulha in f.read()


def rotas_medidas():
    with open(MODELO, encoding='utf-8') as f:
        modelo = json.load(f)
    saida = []
    for rc in modelo['ROUTE_CLASSES']:
        etapas, faltam = {}, []
        for nome in ETAPAS:
            passo = (rc.get('STEPS') or {}).get(nome)
            if passo is None:
                if rc.get('BLOCKED_REASON') or rc.get('DEBT_REASON'):
                    continue
                etapas[nome] = {'STATE': 'UNKNOWN', 'OWNER': None,
                                'OWNER_EXISTS': False, 'CONNECTED_TO_ROUTE': False}
                faltam.append(nome)
                continue
            estado = passo.get('STATE', 'UNKNOWN')
            assert estado in ESTADOS, 'estado fora do vocabulario: %s' % estado
            dono = passo.get('OWNER')
            existe = _existe(dono)
            ligado = _liga(passo.get('EDGE'))
            linha = {
                'STATE': estado,
                'OWNER': dono,
                'OWNER_EXISTS': existe,
                'CONNECTED_TO_ROUTE': ligado,
                'PROOF_KIND': passo.get('PROOF_KIND'),
                'PROOF_REF': passo.get('PROOF_REF'),
            }
            if estado == 'NOT_APPLICABLE':
                linha['NOT_APPLICABLE_REASON'] = passo.get('NOT_APPLICABLE_REASON')
                if not linha['NOT_APPLICABLE_REASON']:
                    faltam.append(nome)          # N/A sem razao NAO vale
            else:
                # A etapa so conta como fechada se tem dono NO DISCO e a aresta
                # foi MEDIDA. `ligado is None` = nao ha aresta a medir; nesse
                # caso basta o dono existir.
                if not existe or ligado is False:
                    faltam.append(nome)
            etapas[nome] = linha

        bloqueada = bool(rc.get('BLOCKED_REASON'))
        divida = bool(rc.get('DEBT_REASON'))
        fechada = (not bloqueada and not divida and not faltam and bool(etapas))
        observadas = [n for n, e in etapas.items()
                      if e['STATE'] in ESTADOS_OBSERVADOS]
        em_banco = [n for n, e in etapas.items()
                    if e['STATE'] in ESTADOS_PROVADOS_EM_BANCO]
        if bloqueada:
            observacao = 'BLOCKED'
        elif divida:
            observacao = 'DEBT'
        elif observadas and len(observadas) + len(
                [n for n, e in etapas.items() if e['STATE'] == 'NOT_APPLICABLE']) == len(etapas):
            observacao = 'OBSERVED'
        elif observadas:
            observacao = 'PARTIALLY_OBSERVED'
        elif em_banco:
            observacao = 'DB_TESTED'
        else:
            observacao = 'NOT_OBSERVED'
        saida.append({
            'ROUTE_CLASS_ID': rc['ID'], 'NAME': rc['NAME'],
            'STEPS': etapas,
            'ARCHITECTURE_CLOSED': fechada,
            'STEPS_BLOQUEANDO': faltam,
            'OBSERVATION_STATE': observacao,
            'BLOCKED_REASON': rc.get('BLOCKED_REASON'),
            'DEBT_REASON': rc.get('DEBT_REASON'),
        })
    return saida


def orquestrador():
    """Existe uma peca que ESCOLHE o executor e coordena? MEDIDO, nao lembrado.

    O mapa anterior publicou «nao existe orquestrador» apoiado numa metrica de
    `censo_da_coleta.py` — «0 pecas coordenam mais de um executor». Essa metrica
    conta IMPORT direto, e `orquestrador/orquestrador.py` despacha por
    `subprocess`. A metrica estava certa; a leitura dela e que respondia outra
    pergunta.

        UMA METRICA NAO E UMA RESPOSTA
        ENQUANTO NINGUEM CONFERIR O QUE ELA MEDE.

    Aqui a pergunta e direta: o ficheiro existe, e quantos executores as
    receitas lhe dao para escolher?
    """
    caminho = os.path.join(RAIZ, 'orquestrador', 'orquestrador.py')
    if not os.path.exists(caminho):
        return {'EXISTE': False, 'PROVA': 'orquestrador/orquestrador.py nao existe'}
    alcance = None
    try:
        import receitas                                    # noqa: PLC0415
        alcance = len(getattr(receitas, 'EXECUTORES', ()) or ())
    except Exception:                                      # noqa: BLE001
        alcance = None
    return {
        'EXISTE': True,
        'FICHEIRO': 'orquestrador/orquestrador.py',
        'EXECUTORES_ALCANCADOS': alcance,
        'PROVA': ('recebe um Pedido, resolve um Plano em `pedido/receitas.py` e '
                  'despacha por subprocess. NAO coleta: escolhe quem coleta.'),
        'RESSALVA': ('alcanca %s dos executores medidos por censo_da_coleta.py — '
                     'existir nao e cobrir. E `SINTONIA SCRAP` continua sendo '
                     'COMPOSITE_EXECUTOR, nao um segundo orquestrador: ele '
                     'coordena rotas de UMA aquisicao.' % alcance),
    }


def main():
    fontes = ordenadas = fontes_it()
    dec, perm, sem_razao = classes_sociais()
    ap_def, ap_fb = apify()
    rotas = rotas_medidas()

    # ── AS CONTAGENS SAO DERIVADAS, NUNCA DIGITADAS ──────────────────────
    # A versao anterior deste mapa publicava «2 CLOSED» porque uma pessoa
    # escreveu 2. Agora o numero nao existe ate ser contado.
    fechadas = [r['ROUTE_CLASS_ID'] for r in rotas if r['ARCHITECTURE_CLOSED']]
    observadas = [r['ROUTE_CLASS_ID'] for r in rotas
                  if r['OBSERVATION_STATE'] in ('OBSERVED', 'PARTIALLY_OBSERVED')]
    em_banco = [r['ROUTE_CLASS_ID'] for r in rotas
                if r['OBSERVATION_STATE'] == 'DB_TESTED']
    bloqueadas = [r['ROUTE_CLASS_ID'] for r in rotas
                  if r['OBSERVATION_STATE'] == 'BLOCKED']
    dividas = [r['ROUTE_CLASS_ID'] for r in rotas
               if r['OBSERVATION_STATE'] == 'DEBT']

    # PROVEN so conta a fonte cuja rota foi MEDIDA nela — nao a que «parece»
    # documento oficial por causa da descricao. So o canario tem essa prova.
    provadas = 1
    desconhecidas = sum(1 for f in ordenadas if not rota_conhecida(f))
    candidatas = len(ordenadas) - provadas - desconhecidas

    rel = {
        'SCHEMA': 'estradas-it/v1',
        'PROVENANCE': {
            'CATALOGO': os.path.relpath(CATALOGO, RAIZ).replace('\\', '/'),
            'MATRIZ': 'leis/social_matriz.py',
            'NOTA': ('a CLASSE de rota social vem da matriz, que ja era a dona. '
                     'As classes nao-sociais sao derivadas do codigo medido, e '
                     'estao no mapa em prosa — este ficheiro conta o que da para '
                     'contar sem opinar.'),
        },
        'ROUTE_CLASSES': rotas,
        'ROUTE_CLASSES_MODELED': len(rotas),
        'ROUTE_CLASSES_ARCHITECTURE_CLOSED': fechadas,
        'ROUTE_CLASSES_OBSERVED': observadas,
        'ROUTE_CLASSES_DB_TESTED': em_banco,
        'ROUTE_CLASSES_BLOCKED': bloqueadas,
        'ROUTE_CLASSES_DEBT': dividas,
        # Quantas classes o sistema PRECISA no total? Enquanto houver fonte com
        # rota desconhecida, nao da para saber: uma delas pode exigir uma
        # estrada que ninguem modelou ainda. UNKNOWN e a resposta honesta.
        'ROUTE_CLASSES_REQUIRED_TOTAL': 'UNKNOWN',
        'ROUTE_CLASSES_REQUIRED_TOTAL_PORQUE': (
            '%d fonte(s) sem rota conhecida. Ate a M1 provar, nenhuma delas '
            'garante caber nas %d classes modeladas.' % (desconhecidas, len(rotas))),
        'FONTES_IT': {
            'TOTAL': len(fontes),
            'SOURCE_ROUTE_PROVEN': provadas,
            'SOURCE_ROUTE_CANDIDATE': candidatas,
            'SOURCE_ROUTE_UNKNOWN': desconhecidas,
            'PROVEN_PORQUE': ('so o canario italiano teve a rota MEDIDA ponta a '
                              'ponta. Descricao («boletim», «PDF») NAO prova '
                              'route class: CANDIDATE NAO E PROVEN.'),
            'COM_ROTA_DECLARADA': sum(1 for f in ordenadas if rota_conhecida(f)),
            'ROTA_NAO_SEI': desconhecidas,
            'POR_PAPEL': dict(collections.Counter(str(f.get('SOURCE_ROLE')) for f in fontes)),
        },
        'CLASSES_SOCIAIS': {
            'DECLARADAS': dict(dec),
            'PERMITIDAS': dict(perm),
            'ROTAS_SEM_RAZAO_ESCRITA': sem_razao,
        },
        'APIFY': {'DEFAULT': ap_def, 'FALLBACK': ap_fb,
                  'NOTA': 'APIFY-LAST: default zero e a leitura correta'},
        'GIT_COMO_BANCO_OPERACIONAL': git_como_banco(),
        'ORQUESTRADOR': orquestrador(),
        'COLLECTION_FOUNDATION_CLOSED': fdc.COLLECTION_FOUNDATION_CLOSED,
    }
    with open(SAIDA, 'w', encoding='utf-8') as f:
        json.dump(rel, f, ensure_ascii=False, indent=1)
    print('FONTES IT %d · PROVEN %d · CANDIDATE %d · UNKNOWN %d'
          % (rel['FONTES_IT']['TOTAL'], provadas, candidatas, desconhecidas))
    print()
    print('ROTA  NOME                        ARQUITETURA  OBSERVACAO')
    for r in rotas:
        print('  %-4s %-26s %-12s %s%s'
              % (r['ROUTE_CLASS_ID'], r['NAME'],
                 'FECHADA' if r['ARCHITECTURE_CLOSED'] else 'ABERTA',
                 r['OBSERVATION_STATE'],
                 ('  falta: ' + ', '.join(r['STEPS_BLOQUEANDO'])) if r['STEPS_BLOQUEANDO'] else ''))
    print()
    print('ARCHITECTURE_CLOSED %d · OBSERVED %d · DB_TESTED %d · BLOCKED %d · DEBT %d'
          % (len(fechadas), len(observadas), len(em_banco), len(bloqueadas), len(dividas)))
    print('CLASSES SOCIAIS %d · APIFY default %d / fallback %d'
          % (len(dec), ap_def, ap_fb))
    print('GIT COMO BANCO: %d ficheiro(s)' % len(rel['GIT_COMO_BANCO_OPERACIONAL']))
    orq = rel['ORQUESTRADOR']
    print('ORQUESTRADOR: %s%s'
          % ('EXISTE' if orq['EXISTE'] else 'nao existe',
             (' · alcanca %s executores' % orq.get('EXECUTORES_ALCANCADOS'))
             if orq['EXISTE'] else ''))
    print('COLLECTION_FOUNDATION_CLOSED = %s'
          % ('SIM' if rel['COLLECTION_FOUNDATION_CLOSED'] else 'NAO'))
    print('\nescrito em %s' % os.path.relpath(SAIDA, RAIZ).replace('\\', '/'))


if __name__ == '__main__':
    main()
