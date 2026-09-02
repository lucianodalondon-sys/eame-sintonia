#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
IMPORTAÇÃO ITÁLIA → SUPABASE — gera o SQL a partir dos artefatos JSON.

    python3 scripts/importar_italia.py

Escreve `supabase/importacoes/IT-CAMADAS-<data>.sql`, determinístico: a mesma entrada
produz o mesmo arquivo byte a byte. **Não executa nada** — as credenciais do Supabase são
secrets do GitHub Actions e não existem nesta sessão.

O QUE ELE CARREGA, E POR QUE NESTA ORDEM
-----------------------------------------
    1  substancia_ativa            a entidade que faltava
    2  substancia_aprovacao_ue     a fronteira europeia — a camada nova da 017
    3  registro_regulatorio (IT)   os 163 registros vigentes do Ministero
    4  registro_substancia         a ponte, que é o que faz a fronteira valer para o produto
    5  resistencia_confirmada      as declarações do GIRE

A ordem é de dependência, não de importância. Sem a 4, a 2 é trivia europeia; com ela,
o sistema responde «este produto vence porque a Europa ainda não decidiu».

AS TRAVAS QUE VIAJAM COM OS DADOS
----------------------------------
    CAPTURE != REGISTRATION     `fonte_versao` entra na chave. Captura nova fica AO LADO.
    TÍTULO CASADO != ATO LIDO   `ato_lido` sai false quando só o título nomeou a substância.
    CITAÇÃO OBRIGATÓRIA         resistência sem `citacao_literal` NÃO é inserida — é
                                descartada com aviso. Linha sem a frase que a sustenta não
                                pode existir no banco, porque alguém a publicaria.
"""
import json
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SAMPLES = os.path.join(ROOT, 'data', 'samples')
DEST = os.path.join(ROOT, 'supabase', 'importacoes')
DATA = '2026-09-02'
FONTE_VERSAO = 'PROD_FTS_6_20260824'


def q(v):
    """Literal SQL. None vira NULL — nunca string vazia, que mentiria de 'não há'."""
    if v is None or v == '':
        return 'null'
    if isinstance(v, bool):
        return 'true' if v else 'false'
    if isinstance(v, (int, float)):
        return str(v)
    return "'" + str(v).replace("'", "''") + "'"


def qarr(vs):
    if not vs:
        return 'null'
    return 'array[' + ', '.join(q(v) for v in vs) + ']::text[]'


def data_iso(txt):
    """'31 January 2027' -> '2027-01-31'. Formato que não reconheço vira None."""
    if not txt or txt == 'NAO_SEI':
        return None
    meses = {'january': '01', 'february': '02', 'march': '03', 'april': '04',
             'may': '05', 'june': '06', 'july': '07', 'august': '08',
             'september': '09', 'october': '10', 'november': '11', 'december': '12'}
    p = str(txt).strip().replace(',', '').split()
    if len(p) == 3 and p[1].lower() in meses:
        return '%s-%s-%02d' % (p[2], meses[p[1].lower()], int(p[0]))
    if len(str(txt)) == 10 and str(txt)[4] == '-':
        return str(txt)
    return None


def ler_git(caminho):
    br = subprocess.run(['git', 'branch', '-r'], capture_output=True, text=True,
                        cwd=ROOT).stdout.split()
    for b in br:
        if 'HEAD' in b or '->' in b:
            continue
        if subprocess.run(['git', 'cat-file', '-e', '%s:%s' % (b, caminho)],
                          cwd=ROOT, capture_output=True).returncode == 0:
            return json.loads(subprocess.run(['git', 'show', '%s:%s' % (b, caminho)],
                                             cwd=ROOT, capture_output=True).stdout
                              .decode('utf-8'))
    return None


def ler_local(rel):
    p = os.path.join(SAMPLES, rel)
    return json.load(open(p, encoding='utf-8')) if os.path.exists(p) else None


def main():
    # V2 quando existir: ela tem os 15 atos LIDOS na integra e verificados por refutador,
    # e as 23 fichas do GIRE ficha a ficha. A V1 tinha 1 ato lido e so o indice.
    eu = ler_local('IT-REGUA/IT-ADAMA-EU-ACTIVE-SUBSTANCE-V2.json') or          ler_local('IT-REGUA/IT-ADAMA-EU-ACTIVE-SUBSTANCE-V1.json')
    eu_v1 = ler_local('IT-REGUA/IT-ADAMA-EU-ACTIVE-SUBSTANCE-V1.json')
    gire = ler_local('IT-CIENCIA/IT-GIRE-RESISTENCIA-V2.json') or            ler_local('IT-CIENCIA/IT-GIRE-RESISTENCIA-V1.json')
    reg = ler_git('data/samples/IT-T4-001/ITALY-ADAMA-REGULATORY-INTELLIGENCE.json')
    faltando = [n for n, v in (('EU', eu), ('GIRE', gire), ('REGULATORIO', reg)) if not v]
    if faltando:
        print('FALTA_ARTEFATO: %s — nao gero import parcial em silencio' % ', '.join(faltando))
        return 1

    L = []
    A = L.append
    A('-- ' + '═' * 69)
    A('-- IT_CAMADAS_IMPORT_V1 — camada UE da substancia + resistencia + registro IT')
    A('--')
    A('-- Gerado por scripts/importar_italia.py. Deterministico.')
    A('-- Requer a migration 017_camada_ue_e_resistencia.sql aplicada.')
    A('--')
    A('-- NAO EXECUTADO nesta sessao: as credenciais do Supabase sao secrets do')
    A('-- GitHub Actions e nao existem aqui.')
    A('-- ' + '═' * 69)
    A('begin;')
    A('')

    # ── 1 · substancia_ativa ──────────────────────────────────────────────────
    subs = sorted({s['ACTIVE_SUBSTANCE'] for s in (eu_v1 or eu)['SUBSTANCIAS']})
    A('-- 1 · SUBSTANCIA ATIVA (%d)' % len(subs))
    for s in subs:
        A("insert into public.substancia_ativa (nome_canonico) values (%s) "
          "on conflict (nome_canonico) do nothing;" % q(s))
    A('')

    # ── 2 · aprovacao UE, do artefato VERIFICADO ────────────────────────────
    # ⚠️ A chave (substancia_id, celex) e do ATO, nao da substancia. Um ato que troca a
    # data de seis substancias vira SEIS linhas — uma por par. Guardar uma linha por ato
    # perderia justamente a data, que e por substancia.
    n_ue = n_lido = n_sem_data = 0
    A('-- 2 · APROVACAO UE — %d atos lidos na integra e verificados por refutador'
      % len(eu.get('ATOS') or []))
    for at in (eu.get('ATOS') or []):
        v = at.get('ADVERSARIAL_VERDICT') or {}
        refutado = bool(v.get('REFUTED'))
        for sb in (at.get('SUBSTANCES') or []):
            nome = (sb.get('name') or '').split('(')[0].strip()
            alvo = next((x for x in subs if x.lower().startswith(nome.lower()[:9])), None)
            if not alvo:
                continue
            d_novo = data_iso(sb.get('new_expiry_date'))
            if not d_novo:
                n_sem_data += 1
            n_ue += 1
            n_lido += 1
            cit = ' | '.join(at.get('LITERAL_QUOTES') or [])[:1800]
            if refutado:
                cit = ('⚠️ REFUTADO PELO VERIFICADOR: %s || %s'
                       % (str(v.get('REASON'))[:900], cit))[:1800]
            A("insert into public.substancia_aprovacao_ue "
              "(substancia_id, celex, ato_data, ato_tipo, expiry_novo, anexo_parte, "
              "anexo_linha, risk_assessment, candidate_for_substitution, citacao_literal, "
              "ato_lido, capturado_em) "
              "select id, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s "
              "from public.substancia_ativa where nome_canonico = %s "
              "on conflict (substancia_id, celex) do nothing;"
              % (q(at['CELEX']), q(DATA), q(at.get('ACT_TYPE')), q(d_novo),
                 q(sb.get('annex_part')), q(sb.get('annex_row')),
                 q(sb.get('risk_assessment_state')),
                 q(sb.get('candidate_for_substitution')),
                 q(cit), q(True), q(DATA + 'T00:00:00Z'), q(alvo)))
    A('')

    # ── 3 · registro_regulatorio IT ───────────────────────────────────────────
    A('-- 3 · REGISTRO REGULATORIO IT (%d vigentes do Ministero)' % len(reg['PRODUCTS']))
    for p in reg['PRODUCTS']:
        A("insert into public.registro_regulatorio "
          "(pais, registration_id, nome_comercial, titular, formulado, estado, "
          "fecha_caducidad, fonte, fonte_versao, capturado_em) values "
          "('IT', %s, %s, %s, %s, %s, %s, %s, %s, %s) "
          "on conflict (pais, registration_id, fonte_versao) do nothing;"
          % (q(p.get('REGISTRATION_ID')), q(p.get('PRODUCT')), q(p.get('HOLDER')),
             q(p.get('FORMULATION')), q(p.get('STATUS')), q(p.get('EXPIRY')),
             q('Ministero della Salute — Banca dati prodotti fitosanitari'),
             q(FONTE_VERSAO), q(DATA + 'T00:00:00Z')))
    A('')

    # ── 4 · a ponte ───────────────────────────────────────────────────────────
    n_ponte = 0
    A('-- 4 · PONTE registro x substancia — e o que faz a fronteira UE valer no produto')
    for p in reg['PRODUCTS']:
        for s in (p.get('ACTIVE_INGREDIENTS') or []):
            if s not in subs:
                continue
            n_ponte += 1
            A("insert into public.registro_substancia (registro_id, substancia_id) "
              "select r.id, s.id from public.registro_regulatorio r, public.substancia_ativa s "
              "where r.pais='IT' and r.registration_id=%s and r.fonte_versao=%s "
              "and s.nome_canonico=%s on conflict do nothing;"
              % (q(p.get('REGISTRATION_ID')), q(FONTE_VERSAO), q(s)))
    A('')

    # ── 5 · resistencia, ficha a ficha ──────────────────────────────────────
    # ⛔ Linha sem CITACAO_LITERAL nao entra. Nao e rigor decorativo: alguem publicaria
    # a linha, e sem a frase que a sustenta ninguem poderia conferir.
    n_res = n_pulado = 0
    A('-- 5 · RESISTENCIA CONFIRMADA (GIRE) — %d linhas' % len(gire.get('LINHAS') or []))
    for l in (gire.get('LINHAS') or []):
        if not l.get('CITACAO_LITERAL'):
            n_pulado += 1
            continue
        ano = l.get('PRIMEIRO_CASO_ANO')
        try:
            ano = int(str(ano)[:4])
        except (TypeError, ValueError):
            ano = None
        n_res += 1
        A("insert into public.resistencia_confirmada "
          "(pais, especie, especie_comum, cultura_declarada, mecanismo, primeiro_caso_ano, "
          "regioes, resistencia_multipla, autoridade, fonte_url, citacao_literal, capturado_em) "
          "values ('IT', %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) "
          "on conflict (pais, especie, mecanismo, cultura_declarada, autoridade) do nothing;"
          % (q(l.get('ESPECIE')), q(l.get('ESPECIE_COMUM_IT')), q(l.get('CULTURA_DECLARADA')),
             q(l.get('MECANISMO')), q(ano), qarr(l.get('REGIOES')),
             q('MULTIPLA' in str(l.get('RESISTENCIA_MULTIPLA_DECLARADA')).upper()
               or 'multipl' in str(l.get('RESISTENCIA_MULTIPLA_DECLARADA')).lower()),
             q('GIRE (CNR-IPSP)'), q(l.get('FONTE_URL')),
             q(str(l.get('CITACAO_LITERAL'))[:1800]), q(DATA + 'T00:00:00Z')))
    A('')
    A('commit;')
    A('')
    A('-- MEDIDO NESTE ARQUIVO')
    A('--   substancias ativas ............ %d' % len(subs))
    A('--   linhas de aprovacao UE ........ %d, todas de ato LIDO na integra' % n_ue)
    A('--   sem data nova no ato .......... %d (o ato trata a substancia sem trocar a data)'
      % n_sem_data)
    A('--   registros IT .................. %d' % len(reg['PRODUCTS']))
    A('--   pontes registro x substancia .. %d' % n_ponte)
    A('--   resistencias confirmadas ...... %d' % n_res)
    A('--')
    A('--   resistencias sem citacao, PULADAS: %d' % n_pulado)
    A('--')
    A('-- ⛔ Toda linha aqui vem de ato LIDO na integra e verificado por um refutador')
    A('--    independente. Onde o refutador refutou, a citacao comeca por REFUTADO.')

    os.makedirs(DEST, exist_ok=True)
    cam = os.path.join(DEST, 'IT-CAMADAS-%s.sql' % DATA)
    with open(cam, 'w', encoding='utf-8', newline='\n') as f:
        f.write('\n'.join(L) + '\n')
    print('gravado: supabase/importacoes/IT-CAMADAS-%s.sql' % DATA)
    print('  substancias %d · atos %d (lidos %d) · registros %d · pontes %d · resistencias %d'
          % (len(subs), n_ue, n_lido, len(reg['PRODUCTS']), n_ponte, n_res))
    return 0


if __name__ == '__main__':
    sys.exit(main())
