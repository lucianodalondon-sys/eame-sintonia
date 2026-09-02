#!/usr/bin/env python3
"""O PRÉ-REQUISITO DO CATÁLOGO, escrito como ENSAIO — não como importação.

Descoberto ao tentar rodar a importação do catálogo ADAMA España num banco
limpo: ela NÃO roda sozinha. As 52 linhas `ROPF_ONLY` do crosswalk não têm
lado de produto — elas afirmam "este registro está no ROPF e não estava no
catálogo que lemos" — e a trava `crosswalk_tem_pelo_menos_um_lado` recusa
uma linha sem nenhum dos dois lados. Sem `registro_regulatorio` povoado, as
52 falham e o import inteiro para.

E a importação do REGISTRO REGULATÓRIO não existe: não está nesta branch
nem na do handoff. É outra importação, com gate próprio — `ES-CASE-001`
continua ABERTA e a ambiguidade do CUPROXI FLO vive lá.

Por isso este arquivo gera um ENSAIO e não uma importação:

    · vai para supabase/ensaios/, que é banco DESCARTÁVEL por contrato;
    · existe para PROVAR que o catálogo funciona quando o pré-requisito
      existe, e para MEDIR exatamente o que falta;
    · não é caminho de produção, e o cabeçalho do SQL diz isso.

Construir a importação do registro por conta própria, sob uma autorização
que diz "catálogo", seria alargar escopo por julgamento meu.

    python3 scripts/ropf_pre_requisito.py
"""
import json
import os
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONTE = os.path.join(RAIZ, 'data', 'samples', 'ES-ADAMA-PORTFOLIO-ROPF.json')
SAIDA = os.path.join(RAIZ, 'supabase', 'ensaios',
                     'ES-ROPF-PRE-REQUISITO-DO-CATALOGO.sql')

RUN = 'ES-ENSAIO-ROPF-PRE-REQUISITO'


def q(v):
    if v is None or v == '':
        return 'null'
    return "'" + str(v).replace("'", "''") + "'"


def data_iso(dmy):
    """'31-08-2026' -> '2026-08-31'. Sem data, null — nunca hoje."""
    p = str(dmy or '').split('-')
    return '%s-%s-%s' % (p[2], p[1], p[0]) if len(p) == 3 else None


def monta():
    with open(FONTE, encoding='utf-8') as f:
        d = json.load(f)
    fichas = sorted(d['FICHAS'], key=lambda x: str(x['REG']))
    versao = d['SOURCE_VERSION']

    o = ["""-- ═══════════════════════════════════════════════════════════════════════
-- ENSAIO — NÃO É IMPORTAÇÃO. Banco DESCARTÁVEL.
--
-- O PRÉ-REQUISITO QUE A IMPORTAÇÃO DO CATÁLOGO NÃO DECLARAVA.
--
-- A importação do catálogo ADAMA España não roda num banco limpo. As 52
-- linhas ROPF_ONLY do crosswalk afirmam "este registro está no ROPF e não
-- estava no catálogo que lemos" — elas não têm lado de produto, e a trava
-- `crosswalk_tem_pelo_menos_um_lado` recusa linha sem nenhum dos dois. Sem
-- registro_regulatorio povoado, o import inteiro para na primeira delas.
--
-- E a importação do REGISTRO REGULATÓRIO não existe em lugar nenhum: nem
-- nesta branch, nem na branch do handoff. Ela é OUTRA importação, com gate
-- próprio, e `ES-CASE-001` continua ABERTA.
--
-- ⚠️ ESTE ARQUIVO NÃO É ESSA IMPORTAÇÃO E NÃO PODE VIRAR ELA.
--
-- Ele existe para uma coisa só: provar, em banco descartável, que o
-- catálogo funciona quando o pré-requisito existe — e medir exatamente o
-- que a produção ainda precisa. Gerado por scripts/ropf_pre_requisito.py,
-- deterministicamente, a partir de data/samples/ES-ADAMA-PORTFOLIO-ROPF.json.
--
-- CAPTURE != REGISTRATION: entra pela chave de captura da 013,
-- (pais, registration_id, fonte, fonte_versao). Reimportar a mesma versão
-- da fonte insere zero; uma versão nova entra AO LADO, nunca por cima.
--
-- NOME_IGUAL != MESMO_REGISTRO: `REG` vem em duas formas que o próprio
-- registro espanhol usa — %d numéricas e %d no formato ES-NNNNN. Nenhuma
-- é convertida na outra. O CUPROXI FLO é ES-00979 aqui e 19232 no catálogo,
-- e os dois continuam sendo identificadores tipados DIFERENTES.
-- ═══════════════════════════════════════════════════════════════════════

begin;

insert into public.collection_run
 (run_id, platform, actor, source_country, started_at, status, item_count_raw, rule_version)
values (%s, 'web', 'ensaio/ropf-pre-requisito', 'ES', %s, 'concluida', %d, 'ensaio-v1')
on conflict (run_id) do nothing;
""" % (sum(1 for x in fichas if not str(x['REG']).startswith('ES-')),
       sum(1 for x in fichas if str(x['REG']).startswith('ES-')),
       q(RUN), q(d['captured_at'] + 'T00:00:00Z'), len(fichas))]

    o.append('\n-- %d registros vigentes do ROPF, ordenados pela chave natural.\n'
             '-- estado = vigente: é o que a fonte diz. EXPIRY != WITHDRAWAL — uma\n'
             '-- caducidade vencida NÃO vira "retirado do mercado" aqui.\n' % len(fichas))
    o.append('insert into public.registro_regulatorio\n'
             ' (pais, registration_id, nome_comercial, titular, formulado, estado,\n'
             '  fecha_caducidad, fonte, fonte_versao, capturado_em) values\n')
    linhas = []
    for x in fichas:
        linhas.append(" ('ES', %s, %s, 'ADAMA', %s, 'vigente', %s, 'MAPA_ROPF', %s, %s)"
                      % (q(x['REG']), q(x['NOME']), q(x['FORMULADO']),
                         q(data_iso(x['CADUCIDAD'])), q(versao),
                         q(d['captured_at'] + 'T00:00:00Z')))
    o.append(',\n'.join(linhas))
    o.append('\non conflict on constraint captura_e_unica_por_fonte_e_versao'
             ' do nothing;\n\ncommit;\n')
    return ''.join(o), len(fichas)


if __name__ == '__main__':
    sql, n = monta()
    with open(SAIDA, 'w', encoding='utf-8') as f:
        f.write(sql)
    print('escrito: %s  (%d registros)' % (SAIDA, n))
