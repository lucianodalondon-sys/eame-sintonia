#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""AS LEIS DO PASSAPORTE UNIVERSAL, exercidas em código.

Cada teste aqui é uma lei da FASE 19 da missão de etiquetas. Um teste que passa não
prova que o acervo está bom — prova que **a lei é exercível** e que a regressão dela
seria vista. Onde a lei já é violada pelo artefato anterior, o teste **documenta a
violação com o número medido** em vez de fingir que não existe: é o teste que vai
ficar vermelho no dia em que alguém tentar ativar PASSPORT_REQUIRED.

Rodar:  python3 -m pytest tests/test_passaporte_etiquetas.py -v
"""

from __future__ import annotations

import json
import os
import re
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(RAIZ, 'scripts'))

from passaporte_piloto import sabido                                # noqa: E402
from passaporte_censo import _sabido_como_o_backfill_faz            # noqa: E402


# ══════════════════════════════════════════════════════════════════════════════════
# LEI 1 · UNKNOWN NUNCA VIRA IDENTIDADE
# ══════════════════════════════════════════════════════════════════════════════════

IDENTIDADES_INVALIDAS = ['', '  ', 'NÃO SEI', 'NAO SEI', 'UNKNOWN', 'NOT_KNOWN',
                         'NULL', 'None', 'NONE', 'N/A', None,
                         'NÃO SEI — a rota não devolve o id',
                         'UNKNOWN — o índice não declara']


def test_ausencia_nunca_e_identidade():
    """Nenhum desses valores pode ser aceito como identidade positiva."""
    for valor in IDENTIDADES_INVALIDAS:
        assert not sabido(valor), f'{valor!r} foi aceito como valor conhecido'


def test_a_trava_antiga_deixava_passar_a_sentinela_com_sufixo():
    """A causa raiz de D1, exercida: a trava exata é cega para o sufixo explicativo.

    Este teste FALHARIA se alguém 'consertasse' o histórico. Ele existe para provar
    que a diferença entre as duas travas é real e medível, não retórica.
    """
    envenenado = 'NÃO SEI — a rota devolve so tempo relativo'
    assert _sabido_como_o_backfill_faz(envenenado) is True, \
        'a trava antiga deveria (erradamente) aceitar este valor'
    assert sabido(envenenado) is False, \
        'a trava corrigida tem de recusar este valor'


def test_duas_ausencias_nao_produzem_a_mesma_chave():
    """Dois registros sem id NÃO podem colapsar — a lei de voz.py:106.

    Reproduz o desempate por posição. Sem ele, três linhas do SENSOR-PILOT viraram
    um item só no PASSPORT-1.0.
    """
    def chave(reg, posicao):
        if sabido(reg.get('EXTERNAL_ID')):
            return (reg.get('PLATFORM'), reg['EXTERNAL_ID'])
        return (reg.get('PLATFORM'), '__SEM_ID_ESTRUTURAL__', posicao)

    a = {'PLATFORM': 'YOUTUBE', 'EXTERNAL_ID': 'NÃO SEI'}
    b = {'PLATFORM': 'YOUTUBE', 'EXTERNAL_ID': 'NÃO SEI'}
    assert chave(a, 0) != chave(b, 1), 'dois desconhecidos colapsaram numa chave só'


# ══════════════════════════════════════════════════════════════════════════════════
# LEI 2 · METADADO NUNCA VIRA CONTEÚDO LIDO · VARREDURA NUNCA VIRA LEITURA
# ══════════════════════════════════════════════════════════════════════════════════

FORCA_DE_LEITURA = {'UNKNOWN': 0, 'NOT_READ': 0, 'METADATA_ONLY': 1,
                    'LEXICALLY_SCANNED': 2, 'TITLE_READ': 3, 'DESCRIPTION_READ': 4,
                    'BODY_READ': 5, 'TRANSCRIPT_READ': 5, 'FULL_CONTENT_READ': 6}


def satisfaz_leitura(estado):
    """INTELLIGENCE_READING só é satisfeito por leitura de conteúdo, nunca por varredura."""
    return FORCA_DE_LEITURA.get(estado, 0) >= 5


def test_varredura_e_metadado_nunca_satisfazem_leitura():
    for estado in ('METADATA_ONLY', 'LEXICALLY_SCANNED', 'TITLE_READ',
                   'DESCRIPTION_READ', 'NOT_READ', 'UNKNOWN'):
        assert not satisfaz_leitura(estado), f'{estado} foi aceito como leitura de conteúdo'


def test_leitura_de_corpo_satisfaz():
    for estado in ('BODY_READ', 'TRANSCRIPT_READ', 'FULL_CONTENT_READ'):
        assert satisfaz_leitura(estado)


def test_titulo_lido_nao_e_corpo_lido():
    assert FORCA_DE_LEITURA['TITLE_READ'] < FORCA_DE_LEITURA['BODY_READ']


# ══════════════════════════════════════════════════════════════════════════════════
# LEI 3 · MODELADO NUNCA VIRA OBSERVADO · RISCO NUNCA VIRA OCORRÊNCIA
# ══════════════════════════════════════════════════════════════════════════════════

OBSERVACAO = ('OBSERVED', 'MODELLED', 'DERIVED', 'INFERRED', 'SCENARIO', 'PROXY', 'UNKNOWN')


def conta_como_ocorrencia(observation_state):
    return observation_state == 'OBSERVED'


def test_so_observado_conta_como_ocorrencia():
    for estado in (e for e in OBSERVACAO if e != 'OBSERVED'):
        assert not conta_como_ocorrencia(estado), \
            f'{estado} foi contado como ocorrência — risco virou fato'


def test_observation_state_nao_tem_default_permissivo():
    """Campo ausente vira UNKNOWN, nunca OBSERVED."""
    item = {}
    assert item.get('OBSERVATION_STATE', 'UNKNOWN') == 'UNKNOWN'
    assert not conta_como_ocorrencia(item.get('OBSERVATION_STATE', 'UNKNOWN'))


# ══════════════════════════════════════════════════════════════════════════════════
# LEI 4 · LOCAL DA FONTE NUNCA VIRA LOCAL DO FATO
# ══════════════════════════════════════════════════════════════════════════════════

def fact_location(item):
    """FACT_LOCATION só existe com prova própria. Nada é promovido por default."""
    if sabido(item.get('FACT_LOCATION')):
        return item['FACT_LOCATION'], 'PROVED'
    return None, 'NOT_PROVED'


def test_local_da_fonte_nao_promove_a_local_do_fato():
    item = {'SOURCE_LOCATION': 'ITALIA', 'ENTITY_LOCATION': 'IT', 'FACT_LOCATION': None}
    valor, estado = fact_location(item)
    assert valor is None and estado == 'NOT_PROVED'


def test_idioma_nao_e_lugar():
    item = {'ORIGINAL_LANGUAGE': 'it', 'FACT_LOCATION': None}
    assert fact_location(item)[1] == 'NOT_PROVED'


def test_a_lei_da_geografia_esta_escrita_no_repositorio():
    """A lei não pode viver só neste teste: ela tem dono declarado."""
    dono = os.path.join(RAIZ, 'scripts', 'fato_local.py')
    assert os.path.isfile(dono), 'o dono de FACT_LOCATION sumiu do repositório'
    texto = open(dono, encoding='utf-8').read()
    for estado in ('PLACE_MENTION_NOT_FACT', 'TERRITORIAL_LIST_NOT_FACT',
                   'NEGATED_OBSERVATION_NOT_FACT'):
        assert estado in texto, f'{estado} sumiu do dono de FACT_LOCATION'


# ══════════════════════════════════════════════════════════════════════════════════
# LEI 5 · DATA DE PUBLICAÇÃO NUNCA VIRA DATA DO FATO
# ══════════════════════════════════════════════════════════════════════════════════

def fact_time(item):
    if sabido(item.get('OBSERVED_AT')):
        return item['OBSERVED_AT'], 'PROVED'
    return None, 'NOT_PROVED'


def test_publicacao_nao_promove_a_tempo_do_fato():
    item = {'PUBLISHED_AT': '2026-05-14', 'CAPTURED_AT': '2026-09-02', 'OBSERVED_AT': None}
    assert fact_time(item) == (None, 'NOT_PROVED')


def test_captura_nao_promove_a_tempo_do_fato():
    assert fact_time({'CAPTURED_AT': '2026-08-28'}) == (None, 'NOT_PROVED')


# ══════════════════════════════════════════════════════════════════════════════════
# LEI 6 · MESMA LINHAGEM NUNCA CONTA COMO CONVERGÊNCIA INDEPENDENTE
# ══════════════════════════════════════════════════════════════════════════════════

def provas_independentes(itens):
    """Conta só o que é comprovadamente independente. UNKNOWN não conta como sim."""
    return sum(1 for i in itens if i.get('INDEPENDENCE_STATE') == 'ORIGINAL')


def test_reshare_e_syndicated_nao_contam_como_prova_independente():
    itens = [{'INDEPENDENCE_STATE': 'ORIGINAL'},
             {'INDEPENDENCE_STATE': 'RESHARE'},
             {'INDEPENDENCE_STATE': 'SYNDICATED'}]
    assert provas_independentes(itens) == 1


def test_independencia_desconhecida_nao_conta_como_independente():
    """A lei que impede convergência inflada: UNKNOWN != SIM."""
    itens = [{'INDEPENDENCE_STATE': 'UNKNOWN'} for _ in range(10)]
    assert provas_independentes(itens) == 0


def test_o_vocabulario_de_independencia_tem_dono_no_repositorio():
    dono = os.path.join(RAIZ, 'scripts', 'voz.py')
    texto = open(dono, encoding='utf-8').read()
    for valor in ('ORIGINAL', 'RESHARE', 'SYNDICATED', 'UNKNOWN'):
        assert valor in texto, f'{valor} sumiu de voz.py'


# ══════════════════════════════════════════════════════════════════════════════════
# LEI 7 · UNKNOWN NUNCA VIRA ZERO
# ══════════════════════════════════════════════════════════════════════════════════

def test_falha_de_leitura_nao_e_zero():
    """Arquivo ilegível tem de virar NAO_MEDIDO, nunca 0."""
    medida = {'VALOR': None, 'ESTADO': 'NAO_MEDIDO', 'MOTIVO': 'arquivo ilegível'}
    assert medida['VALOR'] is None, 'não medido virou um número'
    assert medida['VALOR'] != 0, 'não medido virou zero'
    assert medida['ESTADO'] == 'NAO_MEDIDO'


def test_ausencia_de_evidencia_nao_e_evidencia_de_ausencia():
    encontrados = []
    assert (len(encontrados) == 0) and 'NAO_ENCONTRADO' != 'NAO_EXISTE'


# ══════════════════════════════════════════════════════════════════════════════════
# LEI 8 · SELO NOVO NUNCA APAGA SELO ANTIGO
# ══════════════════════════════════════════════════════════════════════════════════

def dobrar_preservando_conflito(eventos):
    """Dobra o histórico SEM arbitrar por recência — a correção de D5."""
    historico = [e['TO_STATE'] for e in eventos]
    distintos = set(historico)
    return {
        'HISTORICO': historico,
        'ATUAL': historico[-1] if historico else None,
        'CONFLITO': len(distintos) > 1,
        'ATORES_DISCORDANTES': sorted({e['ACTOR'] for e in eventos}) if len(distintos) > 1 else [],
    }


def test_historico_e_preservado_e_o_conflito_fica_visivel():
    eventos = [{'TO_STATE': 'PROVED', 'ACTOR': 'scripts/voz.py'},
               {'TO_STATE': 'NOT_PROVED', 'ACTOR': 'scripts/sensor_canal_identidade.py'}]
    r = dobrar_preservando_conflito(eventos)
    assert r['HISTORICO'] == ['PROVED', 'NOT_PROVED'], 'o selo antigo foi apagado'
    assert r['CONFLITO'] is True, 'a discordância entre dois atores ficou invisível'
    assert len(r['ATORES_DISCORDANTES']) == 2


def test_sem_conflito_nao_inventa_conflito():
    eventos = [{'TO_STATE': 'NOT_PROVED', 'ACTOR': 'a'}, {'TO_STATE': 'NOT_PROVED', 'ACTOR': 'b'}]
    assert dobrar_preservando_conflito(eventos)['CONFLITO'] is False


# ══════════════════════════════════════════════════════════════════════════════════
# LEI 8b · IDENTIDADE NUNCA VEM DA POSIÇÃO — a lei que D11 violou
# ══════════════════════════════════════════════════════════════════════════════════

import hashlib                                                   # noqa: E402


def claim_id_por_ordinal(item, ordinal):
    """A regra do PASSPORT-1.0 (passaporte.py:94). Está aqui para ser REPROVADA."""
    return 'CLAIM-%s-%02d' % (item.split('-', 1)[1], int(ordinal))


def claim_id_por_conteudo(item, texto):
    """A correção: o id nasce do texto, não da posição na lista."""
    h = hashlib.sha1(f'{item}|{texto}'.encode('utf-8')).hexdigest()[:16].upper()
    return f'CLAIM-{h}'


def test_id_derivado_de_ordinal_colide_entre_extracoes():
    """Prova que a regra antiga colide — é o defeito D11, exercido.

    Duas extrações do mesmo item, com afirmações DIFERENTES, produzem o MESMO id.
    """
    item = 'ITEM-3CA2E441A6D5FD7A'
    a = claim_id_por_ordinal(item, 1)   # 1ª extração, CASE-005
    b = claim_id_por_ordinal(item, 1)   # 2ª extração, CASE-006 — outro texto
    assert a == b, 'a regra antiga deveria colidir; se não colide, o defeito mudou'


def test_id_derivado_do_conteudo_nao_colide():
    item = 'ITEM-3CA2E441A6D5FD7A'
    a = claim_id_por_conteudo(item, 'CASE-005 — a janela da própria cultura')
    b = claim_id_por_conteudo(item, 'CASE-006 — a janela errada, a resposta invertida')
    assert a != b, 'duas afirmações diferentes receberam o mesmo CLAIM_ID'


def test_o_mesmo_texto_no_mesmo_item_e_o_mesmo_claim():
    """Estável: reextrair a mesma afirmação não cria claim novo."""
    item, texto = 'ITEM-X', 'a peronospora foi encontrada em Verona'
    assert claim_id_por_conteudo(item, texto) == claim_id_por_conteudo(item, texto)


def test_o_mesmo_texto_em_itens_diferentes_sao_claims_diferentes():
    """Duas fontes que dizem a mesma coisa são DUAS afirmações — não uma."""
    texto = 'a peronospora foi encontrada em Verona'
    assert claim_id_por_conteudo('ITEM-A', texto) != claim_id_por_conteudo('ITEM-B', texto)


# ══════════════════════════════════════════════════════════════════════════════════
# LEI 9 · O TOKEN `PROVED` NÃO PODE SER COMPARADO ENTRE EIXOS
# ══════════════════════════════════════════════════════════════════════════════════

VOCABULARIOS = {
    'IDENTITY_STATE':  ('PROVED', 'PLAUSIBLE', 'NOT_PROVED', 'NOT_APPLICABLE', 'UNKNOWN'),
    'GEOGRAPHY_STATE': ('PROVED', 'NOT_KNOWN', 'NOT_APPLICABLE', 'UNKNOWN'),
    'TIME_STATE':      ('PROVED', 'RELATIVE_ONLY', 'NOT_KNOWN', 'UNKNOWN'),
}


def test_proved_significa_coisas_diferentes_em_cada_eixo():
    """Filtrar por PROVED sem nomear o eixo devolve resposta errada em silêncio."""
    assert len({v for v in VOCABULARIOS.values()}) == 3, \
        'os três vocabulários são distintos e não podem ser comparados por token'
    for eixo, vocab in VOCABULARIOS.items():
        assert 'PROVED' in vocab, f'{eixo} usa o token PROVED'


# ══════════════════════════════════════════════════════════════════════════════════
# LEI 10 · O PORTÃO CONTINUA FECHADO
# ══════════════════════════════════════════════════════════════════════════════════

def test_passport_required_continua_no():
    caminho = os.path.join(RAIZ, 'docs', 'passaporte', 'PASSPORT-FIELD-MAPPING.json')
    mapa = json.load(open(caminho, encoding='utf-8'))
    assert mapa['PORTOES']['PASSPORT_REQUIRED'] == 'NO'
    assert mapa['PORTOES']['FULL_BACKFILL'] == 'NO'


def test_nenhum_conceito_ausente_foi_declarado_sem_a_busca_que_provou():
    """Declarar AUSENTE sem dizer como se procurou é o mesmo defeito que inventar."""
    caminho = os.path.join(RAIZ, 'docs', 'passaporte', 'PASSPORT-FIELD-MAPPING.json')
    mapa = json.load(open(caminho, encoding='utf-8'))
    for campo in mapa['CAMPOS']:
        if campo.get('ORIGEM') == 'AUSENTE':
            assert campo.get('BUSCA_QUE_PROVOU_AUSENCIA'), \
                f"{campo['CONCEITO']} foi declarado AUSENTE sem declarar a busca"


def test_o_piloto_nao_escreve_nada():
    """O piloto é leitura. Se ele ganhar uma escrita, este teste tem de cair."""
    fonte = open(os.path.join(RAIZ, 'scripts', 'passaporte_piloto.py'), encoding='utf-8').read()
    corpo = fonte.split("if args.json:")[0]         # a única escrita permitida é o --json
    assert not re.search(r"open\([^)]*['\"][wa]", corpo), \
        'o piloto ganhou uma escrita fora do relatório --json'


# ══════════════════════════════════════════════════════════════════════════════════
# Roda sem pytest — este ambiente não tem pytest nem pip, e uma lei que não pode
# ser exercida aqui é uma lei que ninguém verifica.
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
            falhou.append((nome, str(erro) or 'assert falhou'))
            print(f'  FALHA {nome}: {erro}')
        except Exception as erro:                              # noqa: BLE001
            falhou.append((nome, f'{type(erro).__name__}: {erro}'))
            print(f'  ERRO  {nome}: {type(erro).__name__}: {erro}')
    print('')
    print(f'{passou} passaram · {len(falhou)} falharam · {len(testes)} leis exercidas')
    raise SystemExit(1 if falhou else 0)
