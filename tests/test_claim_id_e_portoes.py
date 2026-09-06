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
    assert r['MOTIVO'] == 'EXPECTED_UNIVERSE_NOT_DECLARED'
    assert 'NÃO é PASS' in r['BLOQUEIO']


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
# 9 · O DRY-RUN — as provas que a reemissão tem de sustentar
# ══════════════════════════════════════════════════════════════════════════════════

def _dry():
    from passaporte_claim_id import dry_run
    eventos = ler_eventos(REF)
    _, claims, dependentes = medir(eventos, ler_casos(REF))
    return dry_run(eventos, claims, dependentes, ESQUEMA)


def test_dry_run_uma_identidade_por_afirmacao():
    if not _log_disponivel():
        print('      (pulado: NAO_MEDIDO — log ausente)')
        return
    pr = _dry()['PROVAS']
    assert pr['CLAIMS_REAL'] == 55
    assert pr['NEW_CLAIM_IDS'] == pr['CLAIMS_REAL'], 'sobrou ou faltou identidade'
    assert pr['COLLISIONS_AFTER'] == 0


def test_dry_run_nenhuma_rota_direct_fica_errada_ou_orfa_de_claim():
    if not _log_disponivel():
        print('      (pulado: NAO_MEDIDO — log ausente)')
        return
    pr = _dry()['PROVAS']
    assert pr['DIRECT_ROUTES_TOTAL'] == 48
    assert pr['DIRECT_ROUTES_RECOVERED'] == 48
    assert pr['DIRECT_ROUTES_WRONG'] == 0
    assert pr['ROUTES_POINTING_TO_MISSING_CLAIM'] == 0


def test_dry_run_e_append_only():
    if not _log_disponivel():
        print('      (pulado: NAO_MEDIDO — log ausente)')
        return
    d = _dry()
    assert d['PROVAS']['OLD_EVENTS_MODIFIED'] == 0
    tipos = {e['EVENT_TYPE'] for e in d['EVENTOS_NOVOS']}
    assert tipos <= {'CLAIM_ID_REISSUED', 'CLAIM_LINK_ORPHANED'}, \
        'a reemissão inventou um tipo de evento fora do contrato'
    for e in d['EVENTOS_NOVOS']:
        assert e['RULE_VERSION'], 'evento de reemissão sem versão de regra'
        assert e['TARGET_EVENT_ID'], 'evento de reemissão sem alvo rastreável'


def test_o_estado_proposto_faz_o_portao_passar():
    if not _log_disponivel():
        print('      (pulado: NAO_MEDIDO — log ausente)')
        return
    r = portao_claim_id(_dry()['ESTADO_PROPOSTO'])
    assert r['PROVED'] is True, f"o estado proposto ainda reprova: {r['BLOQUEIO']}"
    assert r['COLLIDING_IDS'] == 0
    assert r['ROUTES_ON_AMBIGUOUS_ID'] == 0


def test_orfa_fica_orfa_e_nunca_recebe_dono_inventado():
    if not _log_disponivel():
        print('      (pulado: NAO_MEDIDO — log ausente)')
        return
    d = _dry()
    orfaos = {o['EVENT_ID'] for o in d['ORFAS']}
    for e in d['ESTADO_PROPOSTO']:
        if e.get('EVENT_ID') in orfaos:
            assert e.get('CLAIM_ID') is None, 'uma rota órfã recebeu dono inventado'
            assert e.get('CLAIM_LINK_STATE') == 'ORPHANED'


# ══════════════════════════════════════════════════════════════════════════════════
# 10 · ENTRADA VAZIA NÃO É APROVAÇÃO
# ══════════════════════════════════════════════════════════════════════════════════

def test_portao_reprova_entrada_vazia():
    """Um portão que aprova zero afirmações aprova qualquer coisa, inclusive um
    arquivo que não existe. Aconteceu nesta missão, com um caminho errado."""
    r = portao_claim_id([])
    assert r['PROVED'] is False
    assert 'NAO_MEDIDO' in r['BLOQUEIO']


def test_universo_sem_dono_declara_o_codigo_de_motivo():
    r = portao_universo(RAIZ, None)
    assert r['PROVED'] is False
    assert r['MOTIVO'] == 'EXPECTED_UNIVERSE_NOT_DECLARED'
    assert r['EXPECTED_UNIVERSE'] is None
    assert r['SCAN_FINGERPRINT'], 'o que foi varrido tem de ser declarado mesmo no FAIL'


# ══════════════════════════════════════════════════════════════════════════════════
# 11 · AS TRÊS DECISÕES — travadas para não regredirem
# ══════════════════════════════════════════════════════════════════════════════════

def test_natureza_e_forca_sao_campos_distintos():
    from passaporte_decisoes import (MAPA_LEGADO, EVIDENCE_CLASS_VOCAB,
                                     EVIDENCE_STRENGTH_VOCAB)
    for legado, (classe, forca) in MAPA_LEGADO.items():
        assert classe in EVIDENCE_CLASS_VOCAB, f'{legado}: natureza fora do vocabulário'
        assert forca in EVIDENCE_STRENGTH_VOCAB, f'{legado}: força fora do vocabulário'
        assert classe != forca, f'{legado}: natureza e força no mesmo código'


def test_o_conflito_de_idioma_resolve_no_mesmo_codigo():
    from passaporte_decisoes import MAPA_LEGADO
    assert MAPA_LEGADO['OFFICIAL_DOCUMENT'] == MAPA_LEGADO['DOCUMENTO_OFICIAL'], \
        'o mesmo conceito em duas línguas caiu em códigos diferentes'


def test_o_codigo_interno_nao_e_palavra_de_idioma():
    from passaporte_decisoes import EVIDENCE_CLASS_VOCAB
    for codigo in EVIDENCE_CLASS_VOCAB:
        assert codigo.startswith('EVC-'), f'{codigo} não é código interno'


def test_o_que_nao_e_natureza_de_evidencia_nao_foi_mapeado_a_forca():
    from passaporte_decisoes import MAPA_LEGADO, FORA_DO_CONCEITO, AMBIGUOS
    for k in list(FORA_DO_CONCEITO) + list(AMBIGUOS):
        assert k not in MAPA_LEGADO, \
            f'{k} foi mapeado apesar de estar declarado fora do conceito ou ambíguo'


def test_as_tres_familias_tem_nomes_distintos():
    from passaporte_decisoes import (EVIDENCE_FAMILY_LEGADO, DATASET_FAMILY_LEGADO,
                                     SOURCE_FAMILY_VOCAB)
    semantica = set(EVIDENCE_FAMILY_LEGADO.values())
    local = {n for n, _ in DATASET_FAMILY_LEGADO}
    rota = set(SOURCE_FAMILY_VOCAB)
    assert not (semantica & local), 'família semântica e de local compartilham valor'
    assert not (semantica & rota), 'família semântica e de rota compartilham valor'
    assert not (local & rota), 'família de local e de rota compartilham valor'


def test_o_dono_da_relacao_capacidade_caso_existe_no_repositorio():
    dono = os.path.join(RAIZ, 'docs', 'apresentacao',
                        'CONTRATO-DE-PROVA-DA-APRESENTACAO.md')
    assert os.path.isfile(dono), 'o dono declarado da relação sumiu'
    texto = open(dono, encoding='utf-8').read()
    ligacoes = [l for l in texto.splitlines()
                if 'CAP-' in l and 'CASE-' in l]
    assert ligacoes, 'o dono não liga mais capacidade a caso'


def test_o_portal_nao_declara_capacidade():
    """O portal renderiza. Se ele passar a declarar CAP-xxx, este teste cai."""
    import re as _re
    portal = os.path.join(RAIZ, 'italia-portale')
    if not os.path.isdir(portal):
        print('      (pulado: NAO_MEDIDO — portal ausente)')
        return
    achados = []
    for pasta, _, nomes in os.walk(portal):
        for nome in nomes:
            if not nome.endswith(('.js', '.html', '.json')):
                continue
            try:
                t = open(os.path.join(pasta, nome), encoding='utf-8', errors='ignore').read()
            except Exception:                                  # noqa: BLE001
                continue
            if _re.search(r'CAP-\d{3}|CAPABILITY_ID', t):
                achados.append(nome)
    assert not achados, f'o portal passou a declarar capacidade: {achados[:3]}'


# ══════════════════════════════════════════════════════════════════════════════════
# 12 · O ESTADO ATIVO, DEPOIS DA REEMISSÃO — medido do zero
# ══════════════════════════════════════════════════════════════════════════════════

def _segmento():
    return os.path.join(RAIZ, 'data', 'passaporte', 'EVENTOS-REEMISSAO-CLAIM-ID.jsonl')


def _reemitido():
    return os.path.isfile(_segmento()) and _log_disponivel()


def _estado_ativo():
    from passaporte_reemitir import dobrar_identidade
    antigos = ler_eventos(REF)
    novos = [json.loads(l) for l in open(_segmento(), encoding='utf-8') if l.strip()]
    return antigos, novos, dobrar_identidade(antigos + novos)


def test_ativo_o_historico_antigo_nao_foi_alterado():
    """Append-only, provado pelo hash do arquivo e pelo prefixo íntegro."""
    if not _reemitido():
        print('      (pulado: NAO_MEDIDO — reemissão não aplicada)')
        return
    from passaporte_reemitir import sha256_de
    man = json.load(open(os.path.join(RAIZ, 'data', 'passaporte',
                                      'REEMISSAO-CLAIM-ID-MANIFESTO.json'),
                         encoding='utf-8'))
    canonico = os.path.join(REF, 'data', 'passaporte', 'EVENTOS.jsonl')
    assert sha256_de(canonico) == man['APPLIES_TO']['SHA256'], \
        'o log canônico mudou depois da reemissão'
    antigos, novos, _ = _estado_ativo()
    assert len(antigos) == man['APPLIES_TO']['EVENT_COUNT'] == 33886
    assert len(novos) == 187


def test_ativo_uma_identidade_por_afirmacao_e_zero_colisao():
    if not _reemitido():
        print('      (pulado: NAO_MEDIDO — reemissão não aplicada)')
        return
    _, _, ativo = _estado_ativo()
    r = portao_claim_id(ativo)
    assert r['PROVED'] is True, f"o estado ativo reprova: {r['BLOQUEIO']}"
    assert r['CLAIMS_TOTAL'] == 55
    assert r['CLAIM_IDS_TOTAL'] == 55
    assert r['COLLIDING_IDS'] == 0
    assert r['ROUTES_ON_AMBIGUOUS_ID'] == 0


def test_ativo_rota_direct_aponta_para_o_claim_certo():
    if not _reemitido():
        print('      (pulado: NAO_MEDIDO — reemissão não aplicada)')
        return
    _, _, ativo = _estado_ativo()
    direct = [e for e in ativo if e.get('RELEVANCE') == 'DIRECT']
    assert len(direct) == 48
    for r in direct:
        caso = chave_local(r)
        assert caso, 'rota DIRECT sem caso declarado'
        assert caso in str(r.get('CLAIM_ID')), \
            f"rota DIRECT de {caso} aponta para {r.get('CLAIM_ID')}"


def test_ativo_nenhuma_rota_aponta_para_claim_inexistente():
    if not _reemitido():
        print('      (pulado: NAO_MEDIDO — reemissão não aplicada)')
        return
    _, _, ativo = _estado_ativo()
    existentes = {e['CLAIM_ID'] for e in ativo
                  if e.get('EVENT_TYPE') == 'CLAIMS_EXTRACTED' and e.get('CLAIM_ID')}
    apontam = [e for e in ativo
               if e.get('EVENT_TYPE') in ('ROUTED_TO_CAPABILITY', 'CONSUMED_BY_CAPABILITY')
               and e.get('CLAIM_ID') and e['CLAIM_ID'] not in existentes]
    assert not apontam, f'{len(apontam)} rotas apontam para claim inexistente'


def test_ativo_orfa_continua_orfa_e_sem_dono_inventado():
    if not _reemitido():
        print('      (pulado: NAO_MEDIDO — reemissão não aplicada)')
        return
    _, _, ativo = _estado_ativo()
    orfas = [e for e in ativo if e.get('CLAIM_LINK_STATE') == 'ORPHANED']
    assert len(orfas) == 32
    for o in orfas:
        assert o.get('CLAIM_ID') is None, 'uma órfã recebeu dono'
        assert o.get('CAPABILITY_ID') == 'OPPORTUNITY'


def test_ativo_o_caso_testemunha_esta_separado():
    if not _reemitido():
        print('      (pulado: NAO_MEDIDO — reemissão não aplicada)')
        return
    _, _, ativo = _estado_ativo()
    alvo = [e for e in ativo
            if e.get('EVENT_TYPE') == 'CLAIMS_EXTRACTED'
            and e.get('ITEM_ID') == 'ITEM-3CA2E441A6D5FD7A']
    ids = {e['CLAIM_ID'] for e in alvo}
    assert len(alvo) == 2 and len(ids) == 2, 'França e Espanha ainda dividem identidade'
    assert any('CASE-005' in i for i in ids) and any('CASE-006' in i for i in ids)


def test_ativo_todo_evento_de_reemissao_e_rastreavel():
    if not _reemitido():
        print('      (pulado: NAO_MEDIDO — reemissão não aplicada)')
        return
    _, novos, _ = _estado_ativo()
    ids_antigos = {e.get('EVENT_ID') for e in ler_eventos(REF)}
    for e in novos:
        assert e['PREVIOUS_EVENT_REFERENCE'] in ids_antigos, \
            'evento de reemissão aponta para um evento que não existe'
        assert e['RULE_VERSION'] and e['ACTOR'] and e['EVENT_ID']
        if e['EVENT_TYPE'] == 'CLAIM_ID_REISSUED':
            assert e['OLD_CLAIM_ID'] and e['NEW_CLAIM_ID'] and e['REISSUE_REASON']
        else:
            assert e['RECOVERY_STATE'] == 'UNRECOVERABLE' and e['ORPHAN_REASON']
            assert e['CASE_ID'] is None, 'um órfão ganhou CASE_ID inferido'


def test_ativo_o_segmento_nao_pode_ser_lido_sozinho():
    if not _reemitido():
        print('      (pulado: NAO_MEDIDO — reemissão não aplicada)')
        return
    man = json.load(open(os.path.join(RAIZ, 'data', 'passaporte',
                                      'REEMISSAO-CLAIM-ID-MANIFESTO.json'),
                         encoding='utf-8'))
    assert man['READ_ALONE'].startswith('FORBIDDEN')
    assert man['GARANTIAS']['OLD_EVENTS_MODIFIED'] == 0
    assert man['GARANTIAS']['ORFAOS_RESOLVIDOS_POR_INFERENCIA'] == 0


def test_ativo_o_universo_continua_reprovando():
    """O FAIL do universo não pode ter sido maquiado pela reemissão."""
    r = portao_universo(RAIZ, None)
    assert r['PROVED'] is False
    assert r['MOTIVO'] == 'EXPECTED_UNIVERSE_NOT_DECLARED'


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
