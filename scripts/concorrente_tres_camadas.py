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

A META AINDA É FONTE EXTERNA A ESTA MISSÃO
  O handoff da Meta **não foi congelado pelo coordenador**. Por isso mesmo a
  cadeia que passa em tudo sai como:

      PRELIMINARY_CROSS_BRANCH_JOIN = PROVED
      FINAL_REFRESH_INPUT           = NO

  Nenhum merge é feito. A leitura da branch da Meta é somente-leitura, por
  `git show`, e o arquivo lido fica declarado com o commit de origem.
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

BRANCH_META = 'claude/eame-meta-competitor'
ARQUIVO_META = 'data/samples/META-EAME/META-COMPETITOR-PILOT-EAME.json'

# O vocabulário de empresa da Meta e o desta missão precisam encostar. O
# casamento é por caixa alta exata — NÃO por semelhança.
FORA_DA_AMOSTRA = {'ALBAUGH', 'SEIPASA'}


def ler(nome):
    with open(os.path.join(S, nome), encoding='utf-8') as f:
        return json.load(f)


def ler_da_branch_meta():
    """Somente leitura. `git show` não altera índice, working tree nem branch."""
    sha = subprocess.check_output(
        ['git', 'rev-parse', BRANCH_META], cwd=RAIZ, text=True).strip()
    bruto = subprocess.check_output(
        ['git', 'show', f'{BRANCH_META}:{ARQUIVO_META}'], cwd=RAIZ)
    return json.loads(bruto.decode('utf-8')), sha


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
    pilot, sha = ler_da_branch_meta()
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
    return pilot, sha, tuplas, descartadas, provadas, recusadas, nao_sabidas


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
    pilot, sha, tuplas, descartadas, provadas, recusadas, nao_sabidas = auditar()
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
            'COMMIT': sha,
            'ARQUIVO': ARQUIVO_META,
            'COMO_FOI_LIDO': 'git show — somente leitura. Nenhum merge, nenhum '
                             'checkout, nenhuma alteração de índice.',
            'ESTADO_DO_HANDOFF_META': 'NÃO CONGELADO pelo coordenador',
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
                'NOMES_CRUS_NA_META': 145,
                'POR_QUE_145_NAO_E_O_TOTAL_NORMALIZADO': (
                    'o `ads_by_product_proved` do METRICS traz 145 nomes CRUS. '
                    'Quatro pares são o mesmo nome em caixas diferentes — '
                    'SPECTRUM/Spectrum, VELIFER/Velifer, GAXY/Gaxy, '
                    'KUSABI/Kusabi — e colapsam ao normalizar. Por isso o total '
                    'em unidade de produto é 141, e não 145.'),
                'ANUNCIADO_ANTES_COMO': '36 — obtido casando SÓ o nome',
                'DIFERENCA_EXPLICADA': ('o 36 antigo casava nome de produto com '
                                        'nome de marca, sem exigir que o titular '
                                        'da marca, o do registro e a company da '
                                        'Meta fossem o mesmo grupo, nem que o país '
                                        'fosse o mesmo nas três pontas'),
                'NAO_SUBTRAIR_ENTRE_UNIDADES': (
                    '145 - 28 = 117 seria subtração entre um total de nomes crus '
                    'e uma contagem de produtos normalizados. As duas contas '
                    'corretas estão acima, cada uma fechando na sua unidade.'),
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
