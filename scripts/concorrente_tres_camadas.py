#!/usr/bin/env python3
"""
RED TEAM DA CADEIA DE TRÊS CAMADAS — IP → REGISTRO LOCAL → ANÚNCIO OBSERVADO.

    python3 scripts/concorrente_tres_camadas.py

⚠️ POR QUE ESTE SCRIPT EXISTE — UM ERRO MEU, ENCONTRADO NO RED TEAM

A rodada anterior anunciou **36 cadeias de três camadas prontas para o
refresh**. Aquele número foi obtido casando o NOME do produto anunciado com o
NOME da marca. **Só o nome.** É exatamente a falha que esta missão passou duas
rodadas provando ser cara, e cuja testemunha tem nome próprio: `URBOLE`.

Aqui a cadeia exige **concordância de titular nas TRÊS pontas**:

    company da Meta  ==  grupo do titular da marca  ==  grupo do titular do
                                                        registro local
    e o PAÍS tem de ser o mesmo nas três.

Nome igual com titular incompatível **não forma cadeia** — vira
`THREE_LAYER_CHAIN_REJECTED`, e a recusa é publicada.

A META FOI CONGELADA — E A FONTE PASSA A SER UM COMMIT FIXO
  A missão Meta declarou seu congelamento em
  `META-HANDOFF-FREEZE-V1.json`:

      meta_canonical_freeze_commit = acfd987
      meta_competitor              = ACCEPTED
      mission_state                = PARKED

  Este script deixa de ler *a ponta de uma branch viva* e passa a ler **um
  commit fixo**. A diferença não é estética: uma branch se move, e um join
  que aponta para a ponta responde diferente a cada hora sem que ninguém
  tenha mudado nada. Um commit fixo é uma fonte com data.

  ⚠️ O QUE MUDOU NESTA REEXECUÇÃO — E O QUE NÃO MUDOU
    MUDOU  apenas o PONTEIRO da fonte externa: `4cee050` → `acfd987`.
    NÃO MUDOU nada do casador. `classificar_tupla`, o portão URBOLE, a
    normalização e as três concordâncias obrigatórias estão exatamente como
    no commit congelado do Foresight, `25194e3`. Afrouxar o casamento para
    recuperar quantidade seria trocar a régua pelo resultado.

  O resultado anterior NÃO é inválido:
      OLD_RESULT = SUPERSEDED_BY_CORRECTED_META_INPUT

  Nenhum merge é feito. A leitura continua somente-leitura, por `git show`.
"""
import json
import os
import subprocess
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
S = os.path.join(RAIZ, 'data', 'samples')
SAIDA = os.path.join(S, 'COMPETITOR-THREE-LAYER-AUDIT.json')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from concorrente_crosswalk import normalizar  # noqa: E402

# ── a fonte externa, FIXADA no commit que a própria missão Meta declarou ──
BRANCH_META = 'claude/eame-meta-competitor'
COMMIT_META = 'acfd987'          # meta_canonical_freeze_commit — o DADO
# ⚠️ A DECLARAÇÃO NÃO MORA NO COMMIT QUE ELA DECLARA.
#   Em `acfd987` o handoff da Meta já existia, mas ainda não podia nomear o
#   próprio commit — um commit não conhece o próprio sha antes de existir. O
#   campo `meta_canonical_freeze_commit` entrou depois, em `68f3cd8`.
#   Então a DECLARAÇÃO é lida da ponta da branch e o DADO é lido do commit
#   congelado. Ler os dois do mesmo lugar seria mais simples e estaria errado.
#   O que impede a ponta de contrabandear dado novo é o teste de igualdade do
#   blob, feito abaixo: se o arquivo tiver mudado entre os dois, o script PARA.
REF_DECLARACAO = 'origin/claude/eame-meta-competitor'
ARQUIVO_META = 'data/samples/META-EAME/META-COMPETITOR-PILOT-EAME.json'
HANDOFF_META = 'data/samples/META-EAME/META-HANDOFF-FREEZE-V1.json'

# o input que esta missão usava antes do congelamento da Meta. Fica escrito
# porque um número que some não é corrigido: é apagado.
INPUT_SUPERADO = {
    'AD_CARDS': 1111,
    'RAW_PRODUCT_NAMES': 145,
    'NORMALIZED_PRODUCTS': 141,
    'PROVED_TUPLES': 35,
    'PROVED_PRODUCTS': 28,
    'COMMIT_META_DE_ONDE_VEIO': '4cee050',
    'ESTADO': 'SUPERSEDED_BY_CORRECTED_META_INPUT',
    'NAO_E': 'inválido — foi medido corretamente sobre o input daquele momento',
}

# O vocabulário de empresa da Meta e o desta missão precisam encostar. O
# casamento é por caixa alta exata — NÃO por semelhança.
FORA_DA_AMOSTRA = {'ALBAUGH', 'SEIPASA'}


def ler(nome):
    with open(os.path.join(S, nome), encoding='utf-8') as f:
        return json.load(f)


def ler_da_branch_meta():
    """
    Somente leitura, de um COMMIT FIXO. `git show` não altera índice, working
    tree nem branch — e um commit não se move enquanto ninguém olha.

    Confere também que o commit fixado é o que a própria missão Meta declara
    como canônico. Se ela mudar de ideia, este script PARA em vez de seguir
    lendo um congelamento que já não é o congelamento.
    """
    sha = subprocess.check_output(
        ['git', 'rev-parse', COMMIT_META], cwd=RAIZ, text=True).strip()

    # 1 · a DECLARAÇÃO, lida de onde ela existe
    handoff = json.loads(subprocess.check_output(
        ['git', 'show', f'{REF_DECLARACAO}:{HANDOFF_META}'], cwd=RAIZ).decode('utf-8'))
    declarado = handoff.get('meta_canonical_freeze_commit')
    if not declarado:
        raise SystemExit(
            'PARADO: o handoff da Meta não declara meta_canonical_freeze_commit. '
            'Sem declaração, um join não escolhe sozinho de onde lê.')
    if not sha.startswith(declarado):
        raise SystemExit(
            f'PARADO: este script lê {COMMIT_META}, mas o handoff da Meta '
            f'declara {declarado} como canônico. Um join não escolhe sozinho '
            'de qual congelamento ele lê.')

    # 2 · o DADO, lido do commit congelado — e a prova de que ler a
    #     declaração da ponta não trouxe dado novo junto
    blob_congelado = subprocess.check_output(
        ['git', 'rev-parse', f'{COMMIT_META}:{ARQUIVO_META}'],
        cwd=RAIZ, text=True).strip()
    blob_na_ponta = subprocess.check_output(
        ['git', 'rev-parse', f'{REF_DECLARACAO}:{ARQUIVO_META}'],
        cwd=RAIZ, text=True).strip()
    if blob_congelado != blob_na_ponta:
        raise SystemExit(
            f'PARADO: {ARQUIVO_META} mudou entre o commit congelado '
            f'({blob_congelado[:9]}) e a ponta da branch ({blob_na_ponta[:9]}). '
            'A declaração e o dado deixaram de descrever a mesma coisa.')

    bruto = subprocess.check_output(
        ['git', 'show', f'{COMMIT_META}:{ARQUIVO_META}'], cwd=RAIZ)
    handoff['_BLOB_DO_ARQUIVO_LIDO'] = blob_congelado
    handoff['_REF_DA_DECLARACAO'] = REF_DECLARACAO
    return json.loads(bruto.decode('utf-8')), sha, handoff


# ⚠️ `{"state": "NOT_KNOWN"}` É A MISSÃO META DIZENDO "NENHUM PRODUTO PROVADO
# NESTE BLOCO" — NÃO É UM PRODUTO CHAMADO "state".
#
# A primeira versão deste extrator leu essa chave como nome de produto e criou
# CINCO tuplas fantasma (Seipasa ES, Albaugh FR, Nufarm FR, Syngenta FR,
# Bayer IT). Elas caíam todas em NOT_KNOWN, então nada "quebrava" — só o
# denominador ficava 5 maior do que a realidade. Foi a conferência de unidade
# que as encontrou: 146 nomes nos blocks contra 145 no METRICS, e a diferença
# era exatamente `state`.
#
# `ABSENCE_MARKER` é ausência declarada pela outra missão, e ausência
# declarada nunca entra como observação.
ABSENCE_MARKER = 'state'


def tuplas_da_meta(pilot):
    """
    (competidor, país, produto normalizado) → anúncios observados.

    Devolve também o que foi DESCARTADO, porque um extrator que descarta em
    silêncio é indistinguível de um que nunca viu nada.
    """
    out, descartadas = {}, []
    for b in pilot['blocks']:
        comp = (b.get('competitor') or '').upper()
        pais = b.get('country_reached')
        produtos = b.get('products') or {}
        itens = produtos.items() if isinstance(produtos, dict) else \
            ((p, 1) for p in produtos)
        for nome, n in itens:
            if not nome:
                continue
            if nome == ABSENCE_MARKER:
                descartadas.append({
                    'COMPETITOR': comp, 'COUNTRY': pais, 'CHAVE': nome,
                    'VALOR': n,
                    'MOTIVO': 'marcador de AUSÊNCIA declarado pela missão Meta '
                              '("nenhum produto provado neste bloco"), não é '
                              'nome de produto'})
                continue
            k = (comp, pais, normalizar(nome))
            atual = out.setdefault(k, {'ANUNCIOS': 0, 'NOMES_NA_META': set()})
            atual['ANUNCIOS'] += n if isinstance(n, int) else 1
            atual['NOMES_NA_META'].add(nome)
    return out, descartadas


def indices_da_missao():
    """Marcas por (grupo, país, nome) e registros por (grupo, país, nome)."""
    ip = ler('COMPETITOR-IP-TMVIEW.json')
    par = ler('COMPETITOR-EAME-PARIDADE.json')

    # marcas: o escritório nacional e o da UE valem para o país
    marcas = {}
    for grupo, offs in ip['POR_CONCORRENTE'].items():
        for office, v in offs.items():
            if v.get('ESTADO') != 'OK':
                continue
            paises = ['ES', 'IT', 'FR'] if office == 'EM' else [office]
            for m in v['MARCAS']:
                for pais in paises:
                    marcas.setdefault((grupo, pais, normalizar(m['TM_NAME'])),
                                      []).append(m)

    # registros: só os pares PROVED, que já passaram pela dupla concordância
    registros, por_nome_qualquer_titular = {}, {}
    for pais, b in par['POR_PAIS'].items():
        if b.get('ESTADO_DA_MEDICAO') != 'MEASURED':
            continue
        for p in b['PARES_TODOS']:
            chave_nome = (pais, normalizar(p['TM_NAME']))
            por_nome_qualquer_titular.setdefault(chave_nome, []).append(p)
            if p['ESTADO_DO_LINK'] == 'PROVED':
                registros.setdefault(
                    (p['GRUPO_DA_MARCA'], pais, normalizar(p['TM_NAME'])),
                    []).append(p)
    return marcas, registros, por_nome_qualquer_titular


def classificar_tupla(comp, pais, nome, base, marcas, registros, por_nome):
    """
    A decisão de UMA tupla (competidor, país, produto), isolada.

    Está numa função própria por um motivo: um portão que nunca dispara e um
    portão sem dentes são indistinguíveis olhando só o resultado. Com a
    decisão isolada, o teste consegue EXERCER a recusa com o caso URBOLE em
    vez de torcer para que ela aconteça no dado real.
    """
    if comp in FORA_DA_AMOSTRA:
        return dict(base, ESTADO='THREE_LAYER_CHAIN_NOT_KNOWN',
                    MOTIVO=f'{comp} não está na amostra dos seis concorrentes '
                           'desta missão')

    tem_marca = marcas.get((comp, pais, nome))
    tem_registro = registros.get((comp, pais, nome))

    # O PORTÃO URBOLE: o nome é procurado no país SEM olhar o titular. Se ele
    # aparecer sob titular de outro grupo, a cadeia é RECUSADA — e o dono do
    # outro lado é dito, porque nenhum dos documentos explica por quê.
    todos_com_esse_nome = por_nome.get((pais, nome), [])
    outros = [p for p in todos_com_esse_nome
              if p['GRUPO_DA_MARCA'] != comp
              or (p['REGISTRATION_GRUPO'] not in (None, comp))]
    conflito = [p for p in todos_com_esse_nome
                if p['REGISTRATION_GRUPO'] not in (None, comp)]

    if conflito:
        return dict(
            base, ESTADO='THREE_LAYER_CHAIN_REJECTED',
            MOTIVO=('o nome existe no registro local deste país sob titular de '
                    'OUTRO grupo. Nome igual não é mesmo produto de concorrente'),
            TEM_MARCA_DO_GRUPO=bool(tem_marca),
            TEM_REGISTRO_DO_GRUPO=bool(tem_registro),
            TITULAR_CONFLITANTE=sorted({p['REGISTRATION_HOLDER'] for p in conflito}),
            GRUPO_CONFLITANTE=sorted({p['REGISTRATION_GRUPO'] for p in conflito}),
            REGISTRATION_ID=sorted({p['REGISTRATION_ID'] for p in conflito}),
            LEI='SAME_NAME != SAME_COMPETITOR_PRODUCT')

    if tem_marca and tem_registro:
        r = tem_registro[0]
        return dict(
            base,
            ESTADO='THREE_LAYER_CHAIN_PROVED',
            PRELIMINARY_CROSS_BRANCH_JOIN='PROVED',
            FINAL_REFRESH_INPUT='NO',
            MOTIVO_DO_NAO_FINAL='o handoff da Meta ainda não foi congelado pelo '
                                'coordenador',
            TM_ST13=[m['ST13'] for m in tem_marca[:3]],
            TM_OFFICE=sorted({m['TM_OFFICE'] for m in tem_marca}),
            TM_APPLICANT=sorted({str(m['APPLICANT_NAME']) for m in tem_marca})[:3],
            REGISTRATION_ID=r['REGISTRATION_ID'],
            REGISTRATION_HOLDER=r['REGISTRATION_HOLDER'],
            REGISTRATION_GRUPO=r['REGISTRATION_GRUPO'],
            CONCORDANCIA_DE_TITULAR='META == MARCA == REGISTRO',
            SOURCE_URL=tem_marca[0]['SOURCE_URL'])

    falta = []
    if not tem_marca:
        falta.append('nenhuma marca deste grupo com este nome neste país')
    if not tem_registro:
        falta.append('nenhum registro local PROVED deste grupo com este nome')
    return dict(base, ESTADO='THREE_LAYER_CHAIN_NOT_KNOWN',
                MOTIVO=' · '.join(falta),
                EXISTE_SOB_OUTRO_TITULAR=bool(outros))


def auditar():
    pilot, sha, handoff = ler_da_branch_meta()
    tuplas, descartadas = tuplas_da_meta(pilot)
    marcas, registros, por_nome = indices_da_missao()

    provadas, recusadas, nao_sabidas = [], [], []
    for (comp, pais, nome), info in sorted(tuplas.items()):
        base = {
            'META_COMPANY': comp, 'COUNTRY': pais,
            'PRODUCT_NAME_NA_META': sorted(info['NOMES_NA_META']),
            'ADS_OBSERVED': info['ANUNCIOS'],
            'NOME_NORMALIZADO': nome,
        }
        r = classificar_tupla(comp, pais, nome, base, marcas, registros, por_nome)
        {'THREE_LAYER_CHAIN_PROVED': provadas,
         'THREE_LAYER_CHAIN_REJECTED': recusadas,
         'THREE_LAYER_CHAIN_NOT_KNOWN': nao_sabidas}[r['ESTADO']].append(r)
    return pilot, sha, handoff, tuplas, descartadas, provadas, recusadas, nao_sabidas


def exercer_o_portao_urbole():
    """
    A MUTAÇÃO: e se a Meta anunciasse `URBOLE` como sendo da SYNGENTA na
    Espanha? A marca é da Syngenta; o registro 24157 com esse nome é da ADAMA.

    Zero recusas no dado real e um portão sem dentes dão o mesmo resultado na
    tela. Este exercício separa os dois.
    """
    marcas, registros, por_nome = indices_da_missao()
    base = {'META_COMPANY': 'SYNGENTA', 'COUNTRY': 'ES',
            'PRODUCT_NAME_NA_META': ['URBOLE'], 'ADS_OBSERVED': 0,
            'NOME_NORMALIZADO': normalizar('URBOLE')}
    r = classificar_tupla('SYNGENTA', 'ES', normalizar('URBOLE'), base,
                          marcas, registros, por_nome)
    return {
        'MUTACAO': 'a Meta anuncia URBOLE como SYNGENTA na Espanha',
        'ESTADO_DEVOLVIDO': r['ESTADO'],
        'PEGOU': r['ESTADO'] == 'THREE_LAYER_CHAIN_REJECTED',
        'TITULAR_CONFLITANTE': r.get('TITULAR_CONFLITANTE'),
        'REGISTRATION_ID': r.get('REGISTRATION_ID'),
        'MOTIVO': r.get('MOTIVO'),
    }


def portao_urbole(por_nome):
    """
    URBOLE_GUARD — a testemunha obrigatória, exercida como teste.

    A marca `URBOLE` é da SYNGENTA; o registro espanhol 24157 com esse nome é
    da ADAMA. Se alguma cadeia de três camadas aceitasse esse par, a regra
    inteira teria perdido os dentes.
    """
    pares = por_nome.get(('ES', normalizar('URBOLE')), [])
    if not pares:
        return {'URBOLE_GUARD': 'FAIL', 'MOTIVO': 'a testemunha sumiu do acervo'}
    aceitos = [p for p in pares if p['ESTADO_DO_LINK'] == 'PROVED']
    return {
        'URBOLE_GUARD': 'PASS' if not aceitos else 'FAIL',
        'PARES_ENCONTRADOS': len(pares),
        'ACEITOS_COMO_PROVED': len(aceitos),
        'DETALHE': [{'GRUPO_DA_MARCA': p['GRUPO_DA_MARCA'],
                     'REGISTRATION_ID': p['REGISTRATION_ID'],
                     'REGISTRATION_HOLDER': p['REGISTRATION_HOLDER'],
                     'REGISTRATION_GRUPO': p['REGISTRATION_GRUPO'],
                     'ESTADO_DO_LINK': p['ESTADO_DO_LINK']} for p in pares],
        'LEI': 'SAME_NAME != SAME_COMPETITOR_PRODUCT',
    }


def colisoes(provadas):
    """Um mesmo nome normalizado reivindicado por mais de um grupo."""
    por_nome = {}
    for c in provadas:
        por_nome.setdefault(c['NOME_NORMALIZADO'], set()).add(c['META_COMPANY'])
    return {n: sorted(g) for n, g in por_nome.items() if len(g) > 1}


def main():
    pilot, sha, handoff, tuplas, descartadas, provadas, recusadas, nao_sabidas = auditar()
    _, _, por_nome = indices_da_missao()
    guarda = portao_urbole(por_nome)
    exercicio = exercer_o_portao_urbole()
    guarda['EXERCIDO_POR_MUTACAO'] = exercicio
    col = colisoes(provadas)

    # ── CONSERVAÇÃO 1 · na unidade TUPLA ────────────────────────────────
    total = len(provadas) + len(recusadas) + len(nao_sabidas)
    assert total == len(tuplas), (
        f'a auditoria não conserva na unidade TUPLA: {total} classificadas de '
        f'{len(tuplas)} candidatas')

    # ── CONSERVAÇÃO 2 · na unidade PRODUTO ──────────────────────────────
    #
    # Uma conta separada, e NUNCA misturada com a de tuplas: o mesmo produto
    # pode ser anunciado por um concorrente em dois países, e viraria dois na
    # conta de tuplas e um na de produtos. `145 - 28 = 117` seria uma
    # subtração entre unidades diferentes.
    produtos_todos = {k[2] for k in tuplas}
    # os nomes CRUS, contados — não cravados. `145` era o número da rodada
    # anterior e ficou escrito no código; com a Meta congelada ele virou
    # mentira silenciosa. Agora sai do dado e é conferido contra o que a
    # própria Meta declara em `snapshot_1.raw_product_names_proved`.
    nomes_crus = set()
    for b in pilot['blocks']:
        prods = b.get('products') or {}
        nomes_crus.update(x for x in (prods if isinstance(prods, dict) else prods)
                          if x != ABSENCE_MARKER)
    crus_declarados = (handoff.get('snapshot_1') or {}).get('raw_product_names_proved')
    assert crus_declarados is None or len(nomes_crus) == crus_declarados, (
        f'os blocos trazem {len(nomes_crus)} nomes crus e a Meta declara '
        f'{crus_declarados}. Duas fontes da mesma missão discordando não é '
        'detalhe: é sinal de que uma das duas mudou sem a outra.')
    produtos_provados = {c['NOME_NORMALIZADO'] for c in provadas}
    produtos_sem_cadeia = produtos_todos - produtos_provados
    assert len(produtos_provados) + len(produtos_sem_cadeia) == len(produtos_todos), (
        'a auditoria não conserva na unidade PRODUTO')
    assert produtos_provados <= produtos_todos

    motivos = {}
    for c in nao_sabidas:
        motivos[c['MOTIVO']] = motivos.get(c['MOTIVO'], 0) + 1

    art = {
        'SOURCE_ID': 'COMPETITOR-THREE-LAYER-AUDIT',
        'source': 'red team da junção IP × REGISTRO LOCAL × META',
        'SOURCE_LOCATION': 'interno — derivado',
        'FACT_LOCATION': 'ES · IT · FR',
        'CAMADA_DO_PILOTO': 'CROSS-BRANCH JOIN AUDIT',
        'captured_at': ler('COMPETITOR-EVENTS.json')['captured_at'],

        'O_QUE_ESTA_AUDITORIA_CORRIGE': (
            'a rodada anterior anunciou 36 cadeias de três camadas casando '
            'APENAS o nome do produto anunciado com o nome da marca. Só o nome. '
            'É a falha que a testemunha URBOLE existe para impedir. Aqui a '
            'cadeia exige concordância de titular nas TRÊS pontas e o mesmo país.'),
        'REGRA': ('company da Meta == grupo do titular da marca == grupo do '
                  'titular do registro local, e o PAÍS igual nas três.'),

        'FONTE_EXTERNA': {
            'BRANCH': BRANCH_META,
            'META_CANONICAL_SOURCE_COMMIT': sha,
            'DECLARADO_PELA_PROPRIA_META_EM': HANDOFF_META,
            'REF_DE_ONDE_A_DECLARACAO_FOI_LIDA': handoff.get('_REF_DA_DECLARACAO'),
            'BLOB_DO_ARQUIVO_LIDO': handoff.get('_BLOB_DO_ARQUIVO_LIDO'),
            'POR_QUE_DECLARACAO_E_DADO_VEM_DE_LUGARES_DIFERENTES': (
                'em acfd987 o handoff já existia mas ainda não podia nomear o '
                'próprio commit. O campo entrou depois. A declaração vem da '
                'ponta, o dado vem do congelado, e o script PARA se o arquivo '
                'tiver mudado entre os dois — foi verificado: mesmo blob.'),
            'ARQUIVO': ARQUIVO_META,
            'COMO_FOI_LIDO': 'git show sobre COMMIT FIXO — somente leitura. '
                             'Nenhum merge, nenhum checkout, nenhuma alteração '
                             'de índice.',
            'ESTADO_DO_HANDOFF_META': {
                'meta_competitor': handoff.get('meta_competitor'),
                'mission_state': handoff.get('mission_state'),
                'mandatory_handoff_ready': handoff.get('mandatory_handoff_ready'),
            },
            'POR_QUE_COMMIT_E_NAO_BRANCH': (
                'uma branch se move. Um join que aponta para a ponta responde '
                'diferente a cada hora sem que ninguém tenha mudado nada.'),
            'SNAPSHOT_DECLARADO_PELA_META': handoff.get('snapshot_1'),
        },
        'LINHAGEM': {
            'OLD_META_INPUT': INPUT_SUPERADO,
            'LINEAGE_CORRECTION': 'COMPLETE',
            'O_QUE_MUDOU': 'apenas o ponteiro da fonte externa: 4cee050 -> acfd987',
            'O_QUE_NAO_MUDOU': ('o casador. classificar_tupla, o portão URBOLE, a '
                                'normalização e as três concordâncias obrigatórias '
                                'são as do commit congelado do Foresight 25194e3'),
        },

        'UNIVERSO': {
            'ANUNCIOS_OBSERVADOS_NA_META': 1111,
            'THREE_LAYER_CANDIDATE_UNIT': 'TUPLA (competidor, país, produto '
                                          'normalizado)',
            'THREE_LAYER_CANDIDATES_TOTAL': len(tuplas),
            'DESCARTADAS_ANTES_DE_CANDIDATAR': {
                'N': len(descartadas),
                'MOTIVO': f'a chave `{ABSENCE_MARKER}` é marcador de AUSÊNCIA '
                          'declarado pela missão Meta, não nome de produto',
                'QUAIS': descartadas,
                'EFEITO_DO_DEFEITO': ('a primeira contagem publicou '
                                      f'{len(tuplas) + len(descartadas)} candidatas '
                                      f'e {len(nao_sabidas) + len(descartadas)} '
                                      'NOT_KNOWN. O denominador estava 5 maior que '
                                      'a realidade — nada "quebrava", porque as '
                                      'fantasmas caíam todas em NOT_KNOWN.'),
            },
            'ATENCAO_A_UNIDADE': (
                'TUPLA e PRODUTO são unidades diferentes e não se subtraem entre '
                'si. O mesmo produto anunciado em dois países é DUAS tuplas e UM '
                'produto. Cada decomposição fecha por assert, separadamente.'),
        },

        'RESULTADO': {
            'UNIDADE': 'TUPLA (competidor, país, produto normalizado)',
            'THREE_LAYER_CHAIN_PROVED_TUPLES': len(provadas),
            'THREE_LAYER_CHAIN_REJECTED_TUPLES': len(recusadas),
            'THREE_LAYER_CHAIN_NOT_KNOWN_TUPLES': len(nao_sabidas),
            'CONSERVACAO_TUPLAS': {
                'SOMA': total, 'TOTAL': len(tuplas), 'FECHA': total == len(tuplas),
                'VERIFICADO_POR': 'assert, não por leitura',
            },
            # nomes antigos, sem unidade no nome, mantidos para não quebrar
            # quem já os cita — mas apontando para a unidade certa
            'THREE_LAYER_CHAIN_PROVED': len(provadas),
            'THREE_LAYER_CHAIN_REJECTED': len(recusadas),
            'THREE_LAYER_CHAIN_NOT_KNOWN': len(nao_sabidas),
            'MOTIVOS_DO_NOT_KNOWN': motivos,
            'POR_UNIDADE_PRODUTO': {
                'UNIDADE': 'PRODUTO (nome normalizado)',
                'META_PRODUCTS_TOTAL': len(produtos_todos),
                'META_PRODUCTS_WITH_PROVED_THREE_LAYER_CHAIN': len(produtos_provados),
                'META_PRODUCTS_WITHOUT_PROVED_THREE_LAYER_CHAIN': len(
                    produtos_sem_cadeia),
                'CONSERVACAO_PRODUTOS': {
                    'SOMA': len(produtos_provados) + len(produtos_sem_cadeia),
                    'TOTAL': len(produtos_todos),
                    'FECHA': (len(produtos_provados) + len(produtos_sem_cadeia)
                              == len(produtos_todos)),
                    'VERIFICADO_POR': 'assert, não por leitura',
                },
                'NOMES_CRUS_NA_META': len(nomes_crus),
                'NOMES_CRUS_DECLARADOS_PELA_META': crus_declarados,
                'CONFERENCIA_CRUZADA': (
                    'contados nos blocos e comparados com '
                    '`snapshot_1.raw_product_names_proved` do handoff da Meta. '
                    'Divergência PARA o script.'),
                'POR_QUE_O_CRU_NAO_E_O_TOTAL_NORMALIZADO': (
                    f'os blocos trazem {len(nomes_crus)} nomes CRUS. '
                    f'{len(nomes_crus) - len(produtos_todos)} pares são o mesmo '
                    'nome em caixas diferentes — SPECTRUM/Spectrum, '
                    'VELIFER/Velifer, GAXY/Gaxy, KUSABI/Kusabi — e colapsam ao '
                    f'normalizar. Por isso o total em unidade de produto é '
                    f'{len(produtos_todos)}, e não {len(nomes_crus)}.'),
                'RESULTADO_SUPERADO': {
                    'PRODUTOS_COM_CADEIA': INPUT_SUPERADO['PROVED_PRODUCTS'],
                    'SOBRE_QUAL_INPUT': f"{INPUT_SUPERADO['RAW_PRODUCT_NAMES']} "
                                        'nomes crus · '
                                        f"{INPUT_SUPERADO['AD_CARDS']} cartões",
                    'ESTADO': INPUT_SUPERADO['ESTADO'],
                    'NAO_E': INPUT_SUPERADO['NAO_E'],
                },
                'NAO_SUBTRAIR_ENTRE_UNIDADES': (
                    f'{len(nomes_crus)} - '
                    f'{len(produtos_provados)} seria subtração entre um total de '
                    'nomes CRUS e uma contagem de produtos NORMALIZADOS. As duas '
                    'contas corretas estão acima, cada uma fechando na sua '
                    'unidade, por assert.'),
            },
        },

        'URBOLE_GUARD': guarda,
        'COLISOES_DE_NOME_ENTRE_AS_PROVADAS': col or 'nenhuma',

        'ESTADO_DAS_PROVADAS': {
            'PRELIMINARY_CROSS_BRANCH_JOIN': 'PROVED',
            'FINAL_REFRESH_INPUT': 'NO',
            'POR_QUE': ('a Meta é fonte externa a esta missão e seu handoff ainda '
                        'não foi congelado. Entrada final de refresh só depois do '
                        'handoff canônico da Meta.'),
        },

        'PROVADAS': provadas,
        'RECUSADAS': recusadas,
        'NOT_KNOWN': nao_sabidas,

        'O_QUE_UMA_CADEIA_PROVADA_PROVA': (
            'que a mesma empresa, no mesmo país, tem marca depositada com aquele '
            'nome, autorização local com aquele nome, e anúncio observado com '
            'aquele nome. Três fatos públicos sobre a mesma identidade.'),
        'O_QUE_ELA_NAO_PROVA': [
            'não prova que o anúncio seja daquele produto registrado',
            'não prova venda, investimento, share nem pressão competitiva',
            'não prova lançamento nem intenção',
            'a company da Meta é a classificação DELES; esta missão a aceita como '
            'declarada e não a re-verifica contra registro societário',
        ],
    }

    with open(SAIDA, 'w', encoding='utf-8') as f:
        json.dump(art, f, ensure_ascii=False, indent=2)

    print(f'UNIDADE TUPLA (competidor, país, produto): {len(tuplas)} candidatas '
          f'· {len(descartadas)} descartadas antes (marcador de ausência)')
    print(f'  THREE_LAYER_CHAIN_PROVED_TUPLES     {len(provadas)}')
    print(f'  THREE_LAYER_CHAIN_REJECTED_TUPLES   {len(recusadas)}')
    print(f'  THREE_LAYER_CHAIN_NOT_KNOWN_TUPLES  {len(nao_sabidas)}')
    print(f'UNIDADE PRODUTO: {len(produtos_todos)} no total · '
          f'{len(produtos_provados)} com cadeia · '
          f'{len(produtos_sem_cadeia)} sem')
    for m, n in sorted(motivos.items(), key=lambda kv: -kv[1]):
        print(f'      {n:>4}  {m}')
    print(f"\nURBOLE_GUARD = {guarda['URBOLE_GUARD']}")
    print(f"  exercido por mutação: {exercicio['ESTADO_DEVOLVIDO']} · "
          f"PEGOU={exercicio['PEGOU']} · conflito={exercicio['TITULAR_CONFLITANTE']}")
    print(f'colisões de nome entre as provadas: {col or "nenhuma"}')
    print('gravado:', SAIDA)


if __name__ == '__main__':
    main()
