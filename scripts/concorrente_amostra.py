#!/usr/bin/env python3
"""
AMOSTRA DO PILOTO COMPETITOR FORESIGHT — quem entra, decidido pelo registro.

A missão nomeou oito concorrentes. Este script NÃO os aceita por serem nomes
conhecidos: conta quantos registros cada um sustenta no ROPF espanhol e deixa
o próprio registro escolher os quatro a seis do piloto.

    python3 scripts/concorrente_amostra.py            # conta e grava a amostra
    python3 scripts/concorrente_amostra.py --cache    # reusa o export já baixado

O QUE ESTE SCRIPT NÃO FAZ
  · não agrupa titular por semelhança de texto. `SHARDA CROPCHEM ESPAÑA S.L.` e
    `SHARDA EUROPE BVBA` são duas pessoas jurídicas; dizer que são "a mesma
    empresa" é uma afirmação societária, e este script não a tem. O agrupamento
    é DECLARADO em GRUPOS, string por string, e cada string casada fica escrita
    no artefato para que alguém possa discordar por escrito.
  · não conta "market share". Número de registros não é volume, não é venda,
    não é presença. É quantas autorizações a empresa detém — nada além disso.

A ARMADILHA QUE A RÉGUA JÁ NOMEIA
  `REGUA-DE-CHANGE-EVENT-EAME.md §6` mede o falso positivo de HOLDER_CHANGE em
  variação de grafia (`KENOGARD, S.A.` × `KENOGARD S.A.U.`). O mesmo risco vale
  aqui, ao contrário: agrupar por parecença junta o que a lei separa. Por isso
  o casamento é por prefixo declarado e o resto vai para NAO_AGRUPADO, visível.

VIGENTE tem duas respostas, e as duas são publicadas
  o CAMPO `Estado` responde "a autorização está em vigor?"; o FILTRO `IdEstado`
  responde "ainda pode ser vendido?". A diferença são os cancelados dentro do
  prazo de escoamento. `mapa_regfi.explain_divergence` já fecha essa conta —
  reusada aqui, não reescrita.
"""
import datetime
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import mapa_regfi  # noqa: E402

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CACHE = os.path.join(RAIZ, 'data', 'raw', 'ES', 'ropf-export.json')
SAIDA = os.path.join(RAIZ, 'data', 'samples', 'COMPETITOR-PILOT-AMOSTRA.json')

# ── os oito da missão, e as strings de titular que os representam no ROPF ──
#
# Cada entrada é um PREFIXO exato, em maiúsculas, tal como aparece no campo
# `Titular` do export. Prefixo — e não substring solta — porque `UPL` como
# substring casaria com qualquer razão social que contivesse essas três letras.
#
# Um concorrente pode ter MAIS DE UMA pessoa jurídica no registro. Elas são
# somadas sob o rótulo do grupo, e as duas ficam listadas no artefato: somar
# sem mostrar o que foi somado é onde o número deixa de ser auditável.
GRUPOS = {
    'BAYER':          ['BAYER CROPSCIENCE'],
    'SYNGENTA':       ['SYNGENTA'],
    'BASF':           ['BASF'],
    'CORTEVA':        ['CORTEVA'],
    'FMC':            ['FMC '],
    'UPL':            ['UPL IBERIA', 'UPL HOLDINGS'],
    'NUFARM':         ['NUFARM'],
    'CERTIS BELCHIM': ['CERTIS BELCHIM'],
}
ADAMA = ['ADAMA']          # a casa. Contada para comparação, fora da amostra.
ALVO_MIN, ALVO_MAX = 4, 6  # a missão pede 4–6 bem feitos, não oito pela metade


def _norm(s):
    """Só caixa e espaços. NÃO remove pontuação: `S.A.` × `S.A.U.` são duas empresas."""
    return ' '.join((s or '').upper().split())


def classificar(titular):
    """Devolve o rótulo do grupo, ou None. Casamento por prefixo declarado."""
    t = _norm(titular)
    for grupo, prefixos in list(GRUPOS.items()) + [('ADAMA', ADAMA)]:
        for p in prefixos:
            if t.startswith(_norm(p)):
                return grupo
    return None


def contar(rows, hoje):
    """Por grupo: registros, estado do campo, escoamento, e as razões sociais somadas."""
    escoando = {r['IdProducto'] for r in mapa_regfi.selling_off(rows, hoje)}
    por_grupo = {}
    for r in rows:
        grupo = classificar(r.get('Titular'))
        if grupo is None:
            continue
        g = por_grupo.setdefault(grupo, {
            'REGISTROS': 0, 'ESTADO_VIGENTE': 0, 'ESTADO_CANCELADO': 0,
            'CANCELADO_EM_ESCOAMENTO': 0, 'RAZOES_SOCIAIS': {},
        })
        g['REGISTROS'] += 1
        estado = r.get('Estado')
        if estado == 'Vigente':
            g['ESTADO_VIGENTE'] += 1
        elif estado == 'Cancelado':
            g['ESTADO_CANCELADO'] += 1
            if r['IdProducto'] in escoando:
                g['CANCELADO_EM_ESCOAMENTO'] += 1
        rs = _norm(r.get('Titular'))
        g['RAZOES_SOCIAIS'][rs] = g['RAZOES_SOCIAIS'].get(rs, 0) + 1
    for g in por_grupo.values():
        # o que o FILTRO IdEstado=1 chamaria de vigente: em vigor + em escoamento
        g['FILTRO_VIGENTE'] = g['ESTADO_VIGENTE'] + g['CANCELADO_EM_ESCOAMENTO']
    return por_grupo


def escolher(por_grupo):
    """Os ALVO_MAX maiores por registros VIGENTES, excluída a ADAMA. Empate: nome."""
    candidatos = [(g, v) for g, v in por_grupo.items() if g != 'ADAMA']
    candidatos.sort(key=lambda kv: (-kv[1]['ESTADO_VIGENTE'], kv[0]))
    return [g for g, _ in candidatos[:ALVO_MAX]]


def main():
    hoje = datetime.date.today()
    if '--cache' in sys.argv and os.path.exists(CACHE):
        with open(CACHE, encoding='utf-8') as f:
            guardado = json.load(f)
        rows, fecha = guardado['rows'], guardado['fecha']
        origem = 'cache local ' + CACHE
    else:
        rows, fecha = mapa_regfi.export()
        os.makedirs(os.path.dirname(CACHE), exist_ok=True)
        with open(CACHE, 'w', encoding='utf-8') as f:
            json.dump({'fecha': fecha, 'rows': rows}, f, ensure_ascii=False)
        origem = 'POST /regfiweb/Exportaciones/ExportJsonProductos'

    por_grupo = contar(rows, hoje)
    amostra = escolher(por_grupo)
    ausentes = [g for g in GRUPOS if g not in por_grupo]
    conta = mapa_regfi.explain_divergence(rows, hoje)

    titulares_distintos = len({_norm(r.get('Titular')) for r in rows})
    cobertos = sum(v['REGISTROS'] for g, v in por_grupo.items() if g in amostra)

    artefato = {
        'SOURCE_ID': 'COMPETITOR-PILOT-AMOSTRA',
        'source': 'ROPF — Registro Oficial de Productos Fitosanitarios (MAPA, Espanha)',
        'SOURCE_LOCATION': 'servicio.mapa.gob.es/regfiweb',
        'FACT_LOCATION': 'ES',
        'ORIGINAL_LANGUAGE': 'es',
        # `layer` neste repositório já significa CAMADA REGULATÓRIA, com
        # vocabulário fechado (tests/test_evidence.py::LAYERS). Usar a mesma
        # chave para "camada do piloto" criaria um segundo significado para
        # o mesmo nome — o defeito de dois donos da mesma lei.
        'CAMADA_DO_PILOTO': 'REGULATORY — usado aqui apenas para DIMENSIONAR a amostra',
        'captured_at': hoje.isoformat(),
        'export_server_timestamp': fecha,
        'access_note': origem,

        'O_QUE_ESTE_NUMERO_E': (
            'quantas autorizações cada empresa detém no registro espanhol, hoje.'),
        'O_QUE_ESTE_NUMERO_NAO_E': (
            'não é market share, não é volume vendido, não é presença comercial e '
            'não é força de portfólio. Um registro pode estar em vigor e o produto '
            'nunca ter ido ao mercado.'),

        'REGISTRO_INTEIRO': conta,
        'TITULARES_DISTINTOS': titulares_distintos,

        'REGRA_DE_AGRUPAMENTO': (
            'prefixo declarado sobre o campo Titular, listado em GRUPOS no script. '
            'Sem casamento por semelhança: duas razões sociais só somam quando o '
            'prefixo declarado as cobre, e as duas ficam visíveis em RAZOES_SOCIAIS.'),
        'POR_GRUPO': por_grupo,

        'AMOSTRA_DO_PILOTO': amostra,
        'CRITERIO': (
            f'os {ALVO_MAX} maiores por registros com Estado=Vigente, excluída a ADAMA. '
            f'A missão pede {ALVO_MIN}–{ALVO_MAX} bem feitos em vez de oito pela metade.'),
        'FORA_DA_AMOSTRA': [g for g in por_grupo if g not in amostra and g != 'ADAMA'],
        'DA_MISSAO_E_AUSENTES_DO_ROPF': ausentes,
        'COBERTURA_DA_AMOSTRA': {
            'REGISTROS_DOS_ESCOLHIDOS': cobertos,
            'REGISTROS_NO_REGISTRO_INTEIRO': len(rows),
            'LEITURA': (f'{cobertos} registros em {len(rows)} — a amostra é uma FATIA '
                        'do registro espanhol, e não o registro espanhol.'),
        },

        'LIMITES': [
            'ES apenas. Este artefato NÃO dimensiona IT nem FR: não há registro '
            'local desses dois países no acervo, e o peso na Espanha não se '
            'transfere para eles.',
            'Uma empresa pode operar na Espanha através de pessoa jurídica cujo '
            'prefixo não está declarado em GRUPOS. Ela apareceria como não '
            'agrupada, e o script não a inventa.',
            'ARYSTA, ALBAUGH, SHARDA, ASCENZA e outras pesam no registro e NÃO '
            'estão na lista da missão. Ficar de fora é decisão do recorte, não '
            'medida de irrelevância.',
        ],
    }

    os.makedirs(os.path.dirname(SAIDA), exist_ok=True)
    with open(SAIDA, 'w', encoding='utf-8') as f:
        json.dump(artefato, f, ensure_ascii=False, indent=2)

    print(f'registro inteiro: {len(rows)} registros · {titulares_distintos} titulares')
    print(f'export do servidor: {fecha}')
    print()
    for g, v in sorted(por_grupo.items(), key=lambda kv: -kv[1]['ESTADO_VIGENTE']):
        marca = '  <== AMOSTRA' if g in amostra else ('  (a casa)' if g == 'ADAMA' else '')
        print(f"  {v['ESTADO_VIGENTE']:>4} vigentes / {v['REGISTROS']:>4} registros  "
              f"{g}{marca}")
    if ausentes:
        print('\nda missão e ausentes do ROPF:', ', '.join(ausentes))
    print(f'\namostra: {", ".join(amostra)}')
    print('gravado:', SAIDA)


if __name__ == '__main__':
    main()
