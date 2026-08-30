#!/usr/bin/env python3
"""ES_REGULATORY_IMPORT_V1 — os registros vigentes do ROPF espanhol, no dono certo.

    python3 scripts/regulatorio_importar.py --sql

POR QUE ESTA IMPORTAÇÃO EXISTE

A importação do catálogo ADAMA não roda sozinha: as 52 linhas `ROPF_ONLY` do
crosswalk afirmam "este registro está no ROPF e não estava no catálogo que
lemos", não têm lado de produto, e a trava `crosswalk_tem_pelo_menos_um_lado`
recusa linha sem nenhum dos dois. Sem `registro_regulatorio` povoado, o import
do catálogo para na primeira delas.

Isto NÃO é o ensaio. `supabase/ensaios/ES-ROPF-PRE-REQUISITO-DO-CATALOGO.sql`
continua sendo ensaio, de banco descartável, e não pode ser aplicado como
importação. Esta é a importação canônica, com gerador, chave natural e prova.

ZERO SEGUNDO DONO

Nada é criado. Tudo já tem dono no core:

    registro_regulatorio   a identidade e a captura do registro (001, 013)
    captura_e_unica_por_fonte_e_versao   a chave de captura da 013
    raw_asset              os bytes preservados (001)
    crop_local/issue_local o vocabulário nacional (009)

O QUE ESTA V1 IMPORTA, E O QUE ELA NÃO IMPORTA

IMPORTA: os 96 registros vigentes, com país, id, nome comercial, titular,
formulado, estado, caducidade, fonte, versão da fonte e instante da captura.

NÃO IMPORTA: os usos (CULTIVOS e AGENTES das fichas — 993 e 195 rótulos).
O motivo é de modelagem, não de preguiça: `registro_uso` guarda `crop_id` e
`issue_id` e NÃO tem onde guardar o RÓTULO PUBLICADO quando o casamento não
acontece. Hoje o vocabulário nacional tem 3 culturas e 3 problemas semeados;
importar os usos agora jogaria fora a esmagadora maioria dos rótulos em
silêncio — e perda silenciosa é exatamente o que este repositório persegue.
`catalogo_produto_cultivo` acertou nisso: ela preserva `rotulo_publicado` ao
lado do `crop_id` nulo. `registro_uso` precisa do mesmo antes de receber os
usos, e isso é uma decisão de modelagem própria, não um detalhe deste import.

    NOT_COLLECTED != NOT_REGISTERED

E mais: o artefato traz 96 fichas de 188 registros ADAMA — só as VIGENTES.
Os 92 cancelados não foram coletados. A ausência deles aqui não é "não
registrado": é "não coletado", e a diferença fica escrita no SQL.
"""
import json
import os
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONTE = os.path.join(RAIZ, 'data', 'samples', 'ES-ADAMA-PORTFOLIO-ROPF.json')
SAIDA = os.path.join(RAIZ, 'supabase', 'importacoes',
                     'ES-REGULATORIO-ROPF-2026-08-29.sql')
RUN = 'ES-ROPF-IMPORT-V1-2026-08-29'


def q(v):
    if v is None or v == '':
        return 'null'
    return "'" + str(v).replace("'", "''") + "'"


def data_iso(dmy):
    """'31-08-2026' -> '2026-08-31'. Sem data legível, null — nunca hoje."""
    p = str(dmy or '').split('-')
    if len(p) != 3 or not all(x.isdigit() for x in p):
        return None
    return '%s-%s-%s' % (p[2], p[1], p[0])


def carrega():
    with open(FONTE, encoding='utf-8') as f:
        return json.load(f)


def monta():
    d = carrega()
    # Ordenado pela chave natural: o SQL é o mesmo em qualquer máquina.
    fichas = sorted(d['FICHAS'], key=lambda x: str(x['REG']))
    versao = d['SOURCE_VERSION']
    capturado = d['captured_at'] + 'T00:00:00Z'
    num = sum(1 for x in fichas if not str(x['REG']).startswith('ES-'))
    esn = len(fichas) - num
    sem_data = [x['REG'] for x in fichas if data_iso(x['CADUCIDAD']) is None]

    o = ["""-- ═══════════════════════════════════════════════════════════════════════
-- ES_REGULATORY_IMPORT_V1 — %d registros vigentes do ROPF espanhol
--
-- Gerado por scripts/regulatorio_importar.py a partir de
-- data/samples/ES-ADAMA-PORTFOLIO-ROPF.json. Determinístico: a mesma
-- entrada produz este arquivo byte a byte.
--
-- ESTE ARQUIVO NÃO É O ENSAIO. O ensaio
-- supabase/ensaios/ES-ROPF-PRE-REQUISITO-DO-CATALOGO.sql continua sendo
-- ensaio, de banco descartável, e não deve ser aplicado como importação.
--
-- CAPTURE != REGISTRATION
--   identidade do registro : (pais, registration_id)
--   identidade da captura  : (pais, registration_id, fonte, fonte_versao)
--   A trava `captura_e_unica_por_fonte_e_versao`, da 013, é o dono. Uma
--   versão nova da fonte entra AO LADO, nunca por cima: nova captura NÃO
--   cria registro novo, e não apaga o que a captura anterior disse.
--
-- NOME_IGUAL != MESMO_REGISTRO
--   `REG` vem em duas formas que o próprio registro espanhol usa: %d
--   numéricas e %d no formato ES-NNNNN. Nenhuma é convertida na outra, e
--   nenhuma é casada por nome comercial. O CUPROXI FLO é ES-00979 aqui e
--   19232 no catálogo do fabricante; quem os aproxima é o crosswalk, com
--   estado e evidência, e não este import.
--
-- NOT_COLLECTED != NOT_REGISTERED
--   O artefato traz %d fichas de %s registros ADAMA no ROPF: só as
--   VIGENTES. Os %s cancelados NÃO foram coletados. A ausência deles aqui
--   não é "não registrado" — é "não coletado", e as duas são respostas
--   diferentes.
--
-- EXPIRY != WITHDRAWAL
--   `fecha_caducidad` é uma data. Uma data vencida NÃO vira "retirado do
--   mercado": este import não escreve estado nenhum além do que a fonte
--   diz, e a fonte diz `vigente` para as %d.
--
-- O QUE NÃO ENTRA: os usos. As fichas trazem %d rótulos de cultivo e %d de
--   agente, e `registro_uso` não tem onde guardar o rótulo publicado quando
--   o casamento com o vocabulário canônico não acontece. Importá-los hoje
--   descartaria a maioria em silêncio. Fica declarado, não feito.
-- ═══════════════════════════════════════════════════════════════════════

begin;

-- A rodada de coleta. Sem ela não há de onde pendurar a captura.
insert into public.collection_run
 (run_id, platform, actor, source_country, started_at, status,
  item_count_raw, rule_version)
values (%s, 'web', 'ropf/regfiweb', 'ES', %s, 'concluida', %d, 'ropf-v1')
on conflict (run_id) do nothing;
""" % (len(fichas), num, esn, len(fichas), d['ADAMA_REGISTRATIONS_TOTAL'],
       d['ADAMA_CANCELADO'], len(fichas),
       sum(len(x.get('CULTIVOS') or []) for x in fichas),
       sum(len(x.get('AGENTES') or []) for x in fichas),
       q(RUN), q(capturado), len(fichas))]

    if sem_data:
        o.append('\n-- %d ficha(s) sem data de caducidade legível: %s.\n'
                 '-- Entram com fecha_caducidad NULL. Null é "a fonte não disse",\n'
                 '-- e nunca a data de hoje.\n' % (len(sem_data), ', '.join(sem_data)))

    o.append('\n-- Os %d registros. ON CONFLICT sobre a chave de CAPTURA: reaplicar\n'
             '-- a mesma versão da fonte insere zero, e não sobrescreve nada.\n'
             % len(fichas))
    o.append('insert into public.registro_regulatorio\n'
             ' (pais, registration_id, nome_comercial, titular, formulado, estado,\n'
             '  fecha_caducidad, fonte, fonte_versao, capturado_em) values\n')
    o.append(',\n'.join(
        " ('ES', %s, %s, 'ADAMA', %s, 'vigente', %s, 'MAPA_ROPF', %s, %s)"
        % (q(x['REG']), q(x['NOME']), q(x['FORMULADO']),
           q(data_iso(x['CADUCIDAD'])), q(versao), q(capturado))
        for x in fichas))
    o.append('\non conflict on constraint captura_e_unica_por_fonte_e_versao'
             ' do nothing;\n\ncommit;\n')
    return ''.join(o)


def contagens():
    d = carrega()
    f = d['FICHAS']
    return {
        'ROPF_RECORDS_EXPECTED': len(f),
        'REG_DISTINTOS': len({x['REG'] for x in f}),
        'FORMA_NUMERICA': sum(1 for x in f if not str(x['REG']).startswith('ES-')),
        'FORMA_ES_NNNNN': sum(1 for x in f if str(x['REG']).startswith('ES-')),
        'ADAMA_REGISTRATIONS_TOTAL': d['ADAMA_REGISTRATIONS_TOTAL'],
        'ADAMA_CANCELADO_NAO_COLETADO': d['ADAMA_CANCELADO'],
        'CULTIVOS_NAS_FICHAS_NAO_IMPORTADOS': sum(len(x.get('CULTIVOS') or []) for x in f),
        'AGENTES_NAS_FICHAS_NAO_IMPORTADOS': sum(len(x.get('AGENTES') or []) for x in f),
    }


if __name__ == '__main__':
    if '--contagens' in sys.argv:
        for k, v in contagens().items():
            print('%-38s %s' % (k, v))
    else:
        sql = monta()
        with open(SAIDA, 'w', encoding='utf-8') as f:
            f.write(sql)
        print('SQL %s  %d bytes' % (SAIDA, len(sql)))
