#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""CONTROLES DA LEI DE PERTENÇA.

    PASSPORT_MEMBERSHIP = EXTERNAL_WORLD_INFORMATION
                          AND INDIVIDUALLY_DECIDED_OR_EXECUTED

Controles POSITIVOS que têm de entrar, NEGATIVOS que não podem entrar, e pelo menos um
AMBÍGUO que tem de sair `UNKNOWN_SCOPE` — a prova de que `UNKNOWN` não foi eliminado por
conveniência.

Roda sem pytest.
    python3 tests/test_pertenca.py
"""

from __future__ import annotations

import json
import os
import shutil
import sys
import tempfile

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REF = os.environ.get('PASSAPORTE_REF', r'C:\eame-sintonia-passport-ref')
sys.path.insert(0, os.path.join(RAIZ, 'scripts'))

from passaporte_pertenca import (                              # noqa: E402
    ESTADOS, classificar, cobertura_atual, granularidade, referente,
    universo, varrer)


def _classificar(obj, nome='x.json'):
    d = tempfile.mkdtemp(prefix='pertenca_')
    try:
        p = os.path.join(d, nome)
        with open(p, 'w', encoding='utf-8') as f:
            json.dump(obj, f, ensure_ascii=False)
        return classificar(p)
    finally:
        shutil.rmtree(d, ignore_errors=True)


# ══════════════════════════════════════════════════════════════════════════════════
# CONTROLES POSITIVOS — mundo externo + granularidade ⇒ TÊM de entrar
# ══════════════════════════════════════════════════════════════════════════════════

POSITIVOS = {
    'TRANSCRIPT': {'TRANSCRIPTS': [
        {'EXTERNAL_ID': 'abc123', 'TRANSCRIPT': 'la peronospora è arrivata',
         'COLLECTION_RUN_ID': 'R1'}]},
    'SCIENTIFIC_PAPER': {'PAPERS': [
        {'DOI': '10.1000/x', 'TITLE': 'Downy mildew in Veneto', 'AUTHOR': 'Rossi',
         'ORCID': '0000-0002', 'IDENTITY_STATE': 'PROVED'}]},
    'PUBLIC_COMMUNICATION': {'ACCOUNTS': [
        {'ACCOUNT_HANDLE': '@syngenta_it', 'COMPANY': 'Syngenta',
         'ACCOUNT_IDENTITY_STATE': 'PROVED'}]},
    'ADVERTISEMENT': {'ADS': [
        {'POST_URL': 'https://x/1', 'TITLE': 'Novo fungicida', 'COMPANY': 'BASF',
         'PUBLISHED_AT': '2026-05-01', 'RELEVANCIA': 'DIRECT'}]},
    'REGULATORY_RECORD': {'REGISTOS': [
        {'REGISTRATION_ID': 'ES-01717', 'REFERENCE_PRODUCT': 'SORATEL MAX',
         'REFERENCE_HOLDER': 'ADAMA', 'IDENTITY_STATE': 'PROVED'}]},
    'FIELD_OBSERVATION': {'ITEMS': [
        {'OBSERVATION_TEXT': 'peronospora em Verona', 'COUNTRY_OF_FACT': 'IT',
         'CROP': 'VITE', 'BATCH_ID': 'B1'}]},
    'EXTERNAL_EVENT': {'EVENTOS': [
        {'EVENT_NAME': 'Convegno Vite 2026', 'EVENT_DATE': '2026-03-10',
         'REGION': 'Veneto', 'TIME_STATE': 'PROVED'}]},
    'EXTERNAL_ACTOR_RECORD': {'RESEARCHERS': [
        {'NAME': 'Massimo Blandino', 'INSTITUTION': 'UNITO', 'ORCID': '0000-1',
         'IDENTITY_STATE': 'NOT_PROVED'}]},
    'SENSOR_READING': {'LETTURE': [
        {'CODICE_STAZIONE': '123', 'NOME_SENSORE': 'PIOGGIA', 'DATAORA': '2026-05-01',
         'VALORE': 12.4, 'CROP_STATE': 'NOT_APPLICABLE'}]},
}


def test_controles_positivos_entram():
    falhas = []
    for nome, obj in POSITIVOS.items():
        estado, motivo, _ = _classificar(obj)
        if estado != 'IN_SCOPE_EXTERNAL_WORLD':
            falhas.append(f'{nome} → {estado} ({motivo})')
    assert not falhas, 'controle positivo ficou de fora: ' + ' · '.join(falhas)


def test_a_ferramenta_nao_torna_o_conteudo_interno():
    """A lei, literal: coletar com Apify não transforma um vídeo em metadado nosso."""
    estado, _, info = _classificar({'VIDEOS': [
        {'EXTERNAL_ID': 'v1', 'TITLE': 'poda da vinha', 'APIFY_ACTOR': 'streamers~yt',
         'RUNNER_NAME': 'SINTONIA-LOCAL', 'COLLECTION_RUN_ID': 'R1'}]})
    assert estado == 'IN_SCOPE_EXTERNAL_WORLD', 'o vídeo virou registro de processo'
    assert info['REFERENTE'] == 'EXTERNO'


# ══════════════════════════════════════════════════════════════════════════════════
# CONTROLES NEGATIVOS — referente é o próprio SINTONIA ⇒ NÃO podem entrar
# ══════════════════════════════════════════════════════════════════════════════════

NEGATIVOS = {
    'ACTOR_CONTRACT': {'ACTORS': [
        {'ACTOR': 'streamers~youtube-scraper', 'CONTRACT_STATE': 'CONTRATO_OK',
         'ACTOR_VERSION': '1.2'}]},
    'PIPELINE_EXECUTION': {'RUNS': [
        {'RUN_ID': 'R1', 'ACTOR': 'x', 'COST_USD': 3.2, 'DATASET_ID': 'D',
         'FINISHED_AT': '2026-05-01', 'ITEM_COUNT_RAW': 400}]},
    'QA_RECORD': {'QA': [
        {'QA_STATUS': 'APROVADO', 'REVIEWER': 'missao-07', 'STAGE': 'ingest'}]},
    'INGESTION_REPORT': {'INGESTION': [
        {'INGESTION_STATE': 'OK', 'STAGE': 'normalize', 'BYTES': 1200,
         'ELAPSED_S': 3.4}]},
    'BUILD_MANIFEST': {'BUILDS': [
        {'BUILD_ID': 'b1', 'BUILD_STATE': 'GREEN', 'SHA256': 'ab', 'STAGE': 'build'}]},
    'PRESERVATION_MANIFEST': {'PRESERVACAO': [
        {'PRESERVATION_STATE': 'PRESERVED', 'SHA256_16': 'abc', 'BYTES': 99}]},
    'HUMAN_DECISION': {'DECISOES': [
        {'HUMAN_DECISION': 'aprovado', 'APROVADO_POR': 'dono', 'MISSION_ID': 'M7'}]},
    'SOURCE_HEALTH_DO_PROCESSO': {'SONDAS': [
        {'HTTP': 403, 'ELAPSED_S': 1.1, 'ERROR': 'forbidden', 'STAGE': 'probe'}]},
    'SCHEMA_CONTRACT': {'SCHEMAS': [
        {'SCHEMA_VERSION': 'v2', 'SCHEMA_STATE': 'STABLE', 'STAGE': 'contract'}]},
}


def test_controles_negativos_ficam_fora():
    falhas = []
    for nome, obj in NEGATIVOS.items():
        estado, motivo, _ = _classificar(obj)
        if estado == 'IN_SCOPE_EXTERNAL_WORLD':
            falhas.append(f'{nome} ENTROU como evidência ({motivo})')
    assert not falhas, 'controle negativo entrou: ' + ' · '.join(falhas)


def test_controles_negativos_sao_classificados_como_processo():
    """Não basta ficar fora: tem de ficar fora **pelo motivo certo**."""
    fracos = []
    for nome, obj in NEGATIVOS.items():
        estado, motivo, _ = _classificar(obj)
        if estado != 'OUT_OF_SCOPE_PROCESS':
            fracos.append(f'{nome} → {estado} ({motivo})')
    assert not fracos, ('saiu, mas não como processo — o motivo importa: '
                        + ' · '.join(fracos))


def test_o_fato_sobre_a_coleta_e_processo_e_o_conteudo_e_externo():
    """A distinção que a lei faz com todas as letras."""
    conteudo, _, _ = _classificar({'T': [
        {'EXTERNAL_ID': 'v1', 'TRANSCRIPT': 'texto real', 'BATCH_ID': 'B'}]})
    sobre_a_coleta, _, _ = _classificar({'RUNS': [
        {'RUN_ID': 'R1', 'ACTOR': 'apify', 'COST_USD': 1, 'DATASET_ID': 'D',
         'FINISHED_AT': 'x', 'ITEM_COUNT_RAW': 1}]})
    assert conteudo == 'IN_SCOPE_EXTERNAL_WORLD'
    assert sobre_a_coleta == 'OUT_OF_SCOPE_PROCESS'


# ══════════════════════════════════════════════════════════════════════════════════
# O AMBÍGUO — a prova de que UNKNOWN não foi eliminado por conveniência
# ══════════════════════════════════════════════════════════════════════════════════

def test_caso_ambiguo_produz_unknown_e_nao_chute():
    """Registro sem marcador de mundo externo nem de processo. Não se decide no chute."""
    estado, motivo, _ = _classificar({'COISAS': [
        {'A': 1, 'B': 2, 'OBS': 'sem referente declarado'}]})
    assert estado == 'UNKNOWN_SCOPE'
    assert 'NAO_CHUTAR' in motivo


def test_source_health_sem_contrato_nao_e_promovido():
    """CASO B da lei: só vira fato externo se houver contrato. Sem contrato, UNKNOWN."""
    estado, _, _ = _classificar({'FONTES': [
        {'FONTE': 'ARPAV', 'ESTADO_PUBLICO': 'no ar'}]})
    assert estado != 'IN_SCOPE_EXTERNAL_WORLD', \
        'estado público da fonte foi promovido a evidência sem contrato'


def test_unknown_nao_foi_zerado_no_acervo_real():
    """Se o UNKNOWN zerar, é sinal de que alguém decidiu no chute."""
    r = varrer(RAIZ)
    n = sum(1 for v in r.values() if v[0] == 'UNKNOWN_SCOPE')
    assert n > 0, 'UNKNOWN_SCOPE = 0 — a incerteza sumiu, e isso é suspeito'


# ══════════════════════════════════════════════════════════════════════════════════
# AS DUAS CONDIÇÕES SÃO INDEPENDENTES
# ══════════════════════════════════════════════════════════════════════════════════

def test_mundo_externo_sem_granularidade_fica_fora_mas_nao_como_processo():
    estado, motivo, _ = _classificar({'ITEMS': [
        {'TITLE': 'algo do mundo', 'COUNTRY': 'IT'}]})
    assert estado == 'OUT_OF_SCOPE_OTHER'
    assert 'MUNDO_EXTERNO_MAS' in motivo, 'o motivo não distingue as duas condições'


def test_granularidade_sem_mundo_externo_fica_fora_como_processo():
    estado, _, _ = _classificar({'RUNS': [
        {'RUN_ID': 'R1', 'ACTOR': 'x', 'STAGE': 'y', 'COST_USD': 1,
         'DATASET_ID': 'D', 'FINISHED_AT': 'z'}]})
    assert estado == 'OUT_OF_SCOPE_PROCESS'


def test_a_granularidade_de_1_5_nao_foi_alterada():
    assert granularidade({'RUN_ID'})[0] is True
    assert granularidade({'COLLECTION_RUN_ID'})[0] is True
    assert granularidade({'IDENTITY_STATE'})[0] is True
    assert granularidade({'TITLE'})[0] is False


# ══════════════════════════════════════════════════════════════════════════════════
# O ACERVO REAL
# ══════════════════════════════════════════════════════════════════════════════════

def test_a_soma_fecha():
    r = varrer(RAIZ)
    c = {e: sum(1 for v in r.values() if v[0] == e) for e in ESTADOS}
    assert sum(c.values()) == len(r), 'a soma não fecha'
    assert set(v[0] for v in r.values()) <= set(ESTADOS), 'estado fora dos quatro'


def test_nenhuma_unidade_desaparece_sem_classificacao():
    r = varrer(RAIZ)
    for rel, (estado, motivo, _) in r.items():
        assert estado in ESTADOS, f'{rel} sem estado válido'
        assert motivo, f'{rel} sem motivo declarado'


def test_nenhum_registro_de_processo_entrou_como_evidencia():
    r = varrer(RAIZ)
    dentro = [k for k, v in r.items() if v[0] == 'IN_SCOPE_EXTERNAL_WORLD']
    for rel in dentro:
        assert r[rel][2].get('REFERENTE') == 'EXTERNO', \
            f'{rel} entrou com referente {r[rel][2].get("REFERENTE")}'


def test_nenhuma_unidade_externa_foi_excluida_so_por_estar_em_pasta_inesperada():
    """A lei proíbe decidir pela pasta. Prova: o universo cruza muitas pastas."""
    u = universo(RAIZ, varrer(RAIZ))
    assert len(u['FAMILIES']) >= 10, \
        'o universo ficou concentrado em poucas pastas — cheiro de decisão por pasta'


def test_a_lista_historica_nao_foi_gabarito_e_mesmo_assim_e_coberta():
    if not os.path.isfile(os.path.join(REF, 'scripts', 'passaporte_backfill.py')):
        print('      (pulado: NAO_MEDIDO — referência ausente)')
        return
    coberto = cobertura_atual(REF)
    dentro = set(universo(RAIZ, varrer(RAIZ))['FILES'])
    fora = sorted(coberto - dentro)
    assert not fora, f'a lei perdeu o que o passaporte já cobre: {fora}'
    assert len(dentro) > len(coberto), 'a lei virou a lista'


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
    print(f'{passou} passaram · {len(falhou)} falharam · {len(testes)} controles')
    raise SystemExit(1 if falhou else 0)
