#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""REGRESSÕES DA IDENTIDADE DAS AFIRMAÇÕES E DOS TRÊS PORTÕES.

Roda com ou sem pytest. Neste ambiente não há pytest nem pip, então há um runner
próprio no fim do arquivo — uma lei que não pode ser exercida aqui é uma lei que
ninguém verifica.

    python3 tests/test_claim_id_e_portoes.py
"""

from __future__ import annotations

import json
import os
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REF = os.environ.get('PASSAPORTE_REF', r'C:\eame-sintonia-passport-ref')
sys.path.insert(0, os.path.join(RAIZ, 'scripts'))

from passaporte_claim_id import (                              # noqa: E402
    ESQUEMAS, chave_local, texto_canonico, medir, ler_eventos, ler_casos, propor)
from passaporte_portao_etiquetas import (                      # noqa: E402
    portao_claim_id, portao_universo, separar_estado_e_razao, impressao_digital)

ESQUEMA = ESQUEMAS['C_hibrido']


def _ev(item, texto, caso=None):
    return {'ITEM_ID': item, 'REASON': texto,
            'EVIDENCE_REFERENCE': caso, 'EVENT_TYPE': 'CLAIMS_EXTRACTED',
            'EVENT_ID': 'EVT-TESTE'}


# ══════════════════════════════════════════════════════════════════════════════════
# 1 · CLAIM_ID duplicado com textos diferentes → FAIL
# ══════════════════════════════════════════════════════════════════════════════════

def test_claim_id_repetido_com_textos_diferentes_reprova_o_portao():
    eventos = [
        dict(_ev('ITEM-A', 'CASE-005 — a safra francesa', 'CASE-005'), CLAIM_ID='CLAIM-A-01'),
        dict(_ev('ITEM-A', 'CASE-006 — a seca espanhola', 'CASE-006'), CLAIM_ID='CLAIM-A-01'),
    ]
    r = portao_claim_id(eventos)
    assert r['PROVED'] is False, 'o portão aprovou dois textos sob um CLAIM_ID'
    assert r['COLLIDING_IDS'] == 1
    assert r['BLOQUEIO']


def test_o_portao_aprova_quando_nao_ha_colisao():
    eventos = [
        dict(_ev('ITEM-A', 'CASE-005 — a safra francesa', 'CASE-005'), CLAIM_ID='CLAIM-A-CASE-005-X'),
        dict(_ev('ITEM-A', 'CASE-006 — a seca espanhola', 'CASE-006'), CLAIM_ID='CLAIM-A-CASE-006-Y'),
    ]
    assert portao_claim_id(eventos)['PROVED'] is True


# ══════════════════════════════════════════════════════════════════════════════════
# 2 · a mesma afirmação repetida → identidade ESTÁVEL (e o portão não reprova)
# ══════════════════════════════════════════════════════════════════════════════════

def test_mesma_afirmacao_repetida_da_o_mesmo_id():
    a = _ev('ITEM-A', 'CASE-005 — a safra francesa de 2024', 'CASE-005')
    b = _ev('ITEM-A', 'CASE-005 — a safra francesa de 2024', 'CASE-005')
    assert ESQUEMA(a)[0] == ESQUEMA(b)[0]


def test_reextrair_a_mesma_afirmacao_nao_reprova_o_portao():
    """Repetir não é colidir. O portão só reprova texto factualmente diferente."""
    eventos = [dict(_ev('ITEM-A', 'CASE-005 — igual', 'CASE-005'), CLAIM_ID='CLAIM-A-1'),
               dict(_ev('ITEM-A', 'CASE-005 — igual', 'CASE-005'), CLAIM_ID='CLAIM-A-1')]
    r = portao_claim_id(eventos)
    assert r['PROVED'] is True
    assert r['REPETICOES_LEGITIMAS'] == 1


def test_espaco_e_caixa_nao_criam_afirmacao_nova():
    a = _ev('ITEM-A', 'CASE-005 — A Safra  Francesa', 'CASE-005')
    b = _ev('ITEM-A', 'case-005 — a safra francesa', 'CASE-005')
    assert texto_canonico(a['REASON']) == texto_canonico(b['REASON'])


# ══════════════════════════════════════════════════════════════════════════════════
# 3 · afirmações diferentes → IDs diferentes (o caso-testemunha real)
# ══════════════════════════════════════════════════════════════════════════════════

def test_caso_testemunha_case_005_e_case_006_ganham_identidade_propria():
    """O CLAIM_ID que hoje mistura CASE-005 (França) e CASE-006 (Espanha)."""
    item = 'ITEM-3CA2E441A6D5FD7A'
    a = _ev(item, 'CASE-005 — A safra francesa de 2024 vista pelo clima da própria região',
            'CASE-005')
    b = _ev(item, 'CASE-006 — A mesma pergunta, a janela errada, a resposta invertida',
            'CASE-006')
    ida, idb = ESQUEMA(a)[0], ESQUEMA(b)[0]
    assert ida != idb, 'França e Espanha continuam com a mesma identidade'
    assert 'CASE-005' in ida and 'CASE-006' in idb, 'o caso sumiu do id'
    assert ida.startswith('CLAIM-3CA2E441A6D5FD7A-')


def test_mesma_chave_local_com_textos_diferentes_ainda_separa():
    """A armadilha que o esquema puramente estrutural não pega."""
    a = _ev('ITEM-A', 'CASE-005 — França, colapso 2024', 'CASE-005')
    b = _ev('ITEM-A', 'CASE-005 — Espanha, seca 2023', 'CASE-005')
    assert ESQUEMA(a)[0] != ESQUEMA(b)[0]
    assert ESQUEMAS['A_estrutural'](a)[0] == ESQUEMAS['A_estrutural'](b)[0], \
        'o esquema estrutural deveria colidir aqui — é por isso que ele não foi escolhido'


def test_mesmo_texto_em_itens_diferentes_sao_duas_afirmacoes():
    a = _ev('ITEM-A', 'CASE-009 — a mesma frase', 'CASE-009')
    b = _ev('ITEM-B', 'CASE-009 — a mesma frase', 'CASE-009')
    assert ESQUEMA(a)[0] != ESQUEMA(b)[0]


def test_o_id_nunca_depende_de_posicao_em_lista():
    """A regra antiga: item + ordinal. Duas extrações → o MESMO id. É o defeito D11."""
    def antigo(item, ordinal):
        return 'CLAIM-%s-%02d' % (item.split('-', 1)[1], ordinal)
    assert antigo('ITEM-A', 1) == antigo('ITEM-A', 1)
    a = _ev('ITEM-A', 'primeira afirmação', 'CASE-001')
    b = _ev('ITEM-A', 'segunda afirmação, outra coisa', 'CASE-002')
    assert ESQUEMA(a)[0] != ESQUEMA(b)[0], 'o esquema novo repetiu o defeito antigo'


# ══════════════════════════════════════════════════════════════════════════════════
# 4 · NÃO SEI com motivo continua UNKNOWN — e prosa não vira estado
# ══════════════════════════════════════════════════════════════════════════════════

def test_sentinela_com_motivo_continua_unknown():
    for v in ('NÃO SEI', 'NAO SEI', 'NOT_KNOWN', 'UNKNOWN', '', None,
              'NÃO SEI — a rota devolve so tempo relativo',
              'NAO SEI - a ficha nao declara ano',
              'NOT_KNOWN: sem dump aberto do registro'):
        estado, _ = separar_estado_e_razao(v)
        assert estado == 'UNKNOWN', f'{v!r} não foi reconhecido como ausência'


def test_o_motivo_e_preservado_em_campo_proprio():
    estado, razao = separar_estado_e_razao('NÃO SEI — a rota devolve so tempo relativo')
    assert estado == 'UNKNOWN'
    assert razao == 'a rota devolve so tempo relativo', 'a explicação foi perdida'


def test_o_estado_nao_e_inferido_de_prosa_livre():
    """Uma afirmação que FALA sobre não saber não é uma ausência."""
    for v in ('o autor diz que não sabe a região do estudo',
              'FRANCE — Centre-Val de Loire',
              'REPILO - Venturia oleaginea',
              'NAO SEI se isso importa — frase dentro de uma afirmação real'):
        estado, _ = separar_estado_e_razao(v)
        assert estado == 'PROVED', f'{v!r} virou ausência por causa de prosa'


def test_valor_real_nunca_vira_unknown():
    for v in ('VINE', '2026-05-14', 'Andalusia', 'PROVED', 0, 1, ['VINE']):
        assert separar_estado_e_razao(v)[0] == 'PROVED', f'{v!r} virou UNKNOWN'


# ══════════════════════════════════════════════════════════════════════════════════
# 5 · universo incompleto → FAIL, e ausência de declaração também
# ══════════════════════════════════════════════════════════════════════════════════

def test_universo_sem_declaracao_nao_e_pass():
    r = portao_universo(RAIZ, None)
    assert r['PROVED'] is False
    assert 'NAO_MEDIDO' in r['BLOQUEIO']


def test_universo_declarado_igual_passa():
    real = impressao_digital(RAIZ)
    r = portao_universo(RAIZ, real)
    assert r['PROVED'] is True


def test_universo_declarado_menor_reprova():
    real = impressao_digital(RAIZ)
    menor = dict(real, UNIVERSE_FILE_COUNT=real['UNIVERSE_FILE_COUNT'] - 1,
                 UNIVERSE_FINGERPRINT='0' * 40)
    r = portao_universo(RAIZ, menor)
    assert r['PROVED'] is False
    assert 'subconjunto' in r['BLOQUEIO']


# ══════════════════════════════════════════════════════════════════════════════════
# 6 · VINE vs ["VINE"] — enquanto colidirem, backfill continua proibido
# ══════════════════════════════════════════════════════════════════════════════════

def normalizar_crop(v):
    """A normalização que AINDA NÃO EXISTE no passaporte. Aqui só para o teste medir."""
    if isinstance(v, str) and v.startswith('[') and v.endswith(']'):
        try:
            import ast
            v = ast.literal_eval(v)
        except Exception:                                      # noqa: BLE001
            return None
    return tuple(sorted(v)) if isinstance(v, list) else (v,)


def test_vine_e_lista_vine_sao_a_mesma_cultura_apos_normalizar():
    assert normalizar_crop('VINE') == normalizar_crop("['VINE']")


def test_sem_normalizacao_eles_sao_diferentes_e_o_backfill_fica_proibido():
    assert 'VINE' != "['VINE']"
    mapa = json.load(open(os.path.join(RAIZ, 'docs', 'passaporte',
                                       'PASSPORT-FIELD-MAPPING.json'), encoding='utf-8'))
    assert mapa['PORTOES']['FULL_BACKFILL'] == 'NO', \
        'FULL_BACKFILL foi liberado com CROP ainda em duas grafias'


def test_multi_cultura_nao_e_uma_cultura_so():
    assert normalizar_crop("['CEREAL', 'VINE']") != normalizar_crop("['VINE']")


# ══════════════════════════════════════════════════════════════════════════════════
# 7 · a rota aponta para o claim exato — sobre o log real
# ══════════════════════════════════════════════════════════════════════════════════

def _log_disponivel():
    return os.path.isfile(os.path.join(REF, 'data', 'passaporte', 'EVENTOS.jsonl'))


def test_toda_rota_remapeada_aponta_para_um_claim_que_existe():
    if not _log_disponivel():
        print('      (pulado: NAO_MEDIDO — log de eventos ausente)')
        return
    eventos = ler_eventos(REF)
    casos = ler_casos(REF)
    _, claims, dependentes = medir(eventos, casos)
    mapa, orfas, _ = propor(eventos, claims, dependentes, ESQUEMA)
    ids_de_claim = {m['CLAIM_ID_NOVO'] for m in mapa if not m['TEXTO'].startswith('[')}
    ids_de_rota = {m['CLAIM_ID_NOVO'] for m in mapa if m['TEXTO'].startswith('[')}
    orfas_de_verdade = ids_de_rota - ids_de_claim
    assert not orfas_de_verdade, \
        f'rotas remapeadas para claim inexistente: {sorted(orfas_de_verdade)[:3]}'


def test_o_que_nao_e_reatribuivel_e_declarado_e_nao_chutado():
    if not _log_disponivel():
        print('      (pulado: NAO_MEDIDO — log de eventos ausente)')
        return
    eventos = ler_eventos(REF)
    _, claims, dependentes = medir(eventos, ler_casos(REF))
    _, orfas, _ = propor(eventos, claims, dependentes, ESQUEMA)
    assert orfas, 'a proposta não declarou nenhuma rota não-reatribuível — suspeito'
    for o in orfas:
        assert o['MOTIVO'], 'rota não-reatribuível sem motivo declarado'
        assert o['EVENT_ID'], 'rota não-reatribuível sem evento rastreável'


def test_o_portao_continua_reprovando_o_log_historico():
    """O log antigo é append-only: ele NÃO foi consertado, e o portão tem de dizer isso."""
    if not _log_disponivel():
        print('      (pulado: NAO_MEDIDO — log de eventos ausente)')
        return
    r = portao_claim_id(ler_eventos(REF))
    assert r['PROVED'] is False, 'o portão passou sobre um log que ainda tem 12 colisões'
    assert r['COLLIDING_IDS'] == 12


# ══════════════════════════════════════════════════════════════════════════════════
# 8 · identidade transportada não é recriada
# ══════════════════════════════════════════════════════════════════════════════════

def test_conceito_herdado_nomeia_o_dono_e_nao_inventa_nome():
    mapa = json.load(open(os.path.join(RAIZ, 'docs', 'passaporte',
                                       'PASSPORT-FIELD-MAPPING.json'), encoding='utf-8'))
    for campo in mapa['CAMPOS']:
        if campo.get('ORIGEM') in ('HERDADO', 'TRANSPORTE_AUSENTE'):
            assert campo.get('DONOS'), \
                f"{campo['CONCEITO']} é herdado e não nomeia dono"
            assert campo.get('CANONICO'), \
                f"{campo['CONCEITO']} é herdado e não declara o nome canônico"


def test_conceito_ausente_declara_a_busca_que_provou_a_ausencia():
    mapa = json.load(open(os.path.join(RAIZ, 'docs', 'passaporte',
                                       'PASSPORT-FIELD-MAPPING.json'), encoding='utf-8'))
    for campo in mapa['CAMPOS']:
        if campo.get('ORIGEM') == 'AUSENTE':
            assert campo.get('BUSCA_QUE_PROVOU_AUSENCIA'), \
                f"{campo['CONCEITO']} declarado AUSENTE sem a busca"


def test_a_independencia_e_transportada_de_voz_py_e_nao_reescrita():
    mapa = json.load(open(os.path.join(RAIZ, 'docs', 'passaporte',
                                       'PASSPORT-FIELD-MAPPING.json'), encoding='utf-8'))
    ind = [c for c in mapa['CAMPOS'] if c['CONCEITO'] == 'INDEPENDENCE_STATE'][0]
    assert ind['ORIGEM'] == 'TRANSPORTE_AUSENTE'
    assert any('voz.py' in d for d in ind['DONOS'])
    fonte = open(os.path.join(RAIZ, 'scripts', 'voz.py'), encoding='utf-8').read()
    for v in ind['VOCABULARIO']:
        assert v in fonte, f'{v} não está no dono — o vocabulário foi reinventado'


# ══════════════════════════════════════════════════════════════════════════════════

if __name__ == '__main__':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:                                          # noqa: BLE001
        pass
    testes = [(n, o) for n, o in sorted(globals().items())
              if n.startswith('test_') and callable(o)]
    passou, falhou = 0, []
    for nome, funcao in testes:
        try:
            funcao()
            passou += 1
            print(f'  ok    {nome}')
        except AssertionError as erro:
            falhou.append(nome)
            print(f'  FALHA {nome}: {erro}')
        except Exception as erro:                              # noqa: BLE001
            falhou.append(nome)
            print(f'  ERRO  {nome}: {type(erro).__name__}: {erro}')
    print('')
    print(f'{passou} passaram · {len(falhou)} falharam · {len(testes)} regressões')
    raise SystemExit(1 if falhou else 0)
