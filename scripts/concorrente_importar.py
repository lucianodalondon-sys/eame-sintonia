#!/usr/bin/env python3
"""
GERADOR DO SQL DE IMPORTAÇÃO DO COMPETITOR FORESIGHT.

    python3 scripts/concorrente_importar.py

Escreve `supabase/importacoes/COMPETITOR-FORESIGHT-<data>.sql`.

DETERMINÍSTICO: a mesma entrada produz o mesmo arquivo byte a byte. Tudo é
ordenado pela chave natural, e nenhuma data de execução entra no corpo do
SQL — só a data de captura, que vem dos artefatos.

O ARQUIVO NÃO É APLICADO POR ESTE SCRIPT.
Esta máquina não tem `psql` nem senha do Supabase. O SQL é provado no portão
`.github/workflows/concorrente-portao.yml`, contra um Postgres 16 DESCARTÁVEL.
Aplicar em produção é decisão de quem tem a chave, com o arquivo na mão.

O QUE ELE IMPORTA, E O QUE ELE RECUSA A IMPORTAR
  IMPORTA   os concorrentes como `organizacao` (tipo `empresa`)
            os eventos de IP e REGULATORY em `evento_concorrente`
            os links do crosswalk em `evento_concorrente_link`
  NÃO IMPORTA
            marcas fora das classes agro sem nenhuma classe declarada — elas
            existem no artefato, e entrariam como ruído no banco
            eventos de PRODUCT_CATALOG, META e CREATOR: NOT_JOINED_IN_THIS
            _MISSION — existem em outras branches, e o refresh final junta os
            handoffs, não os branches
            patente: DEMOTED, ver COMPETITOR-PATENT-DEMOTE.json

OS REGISTROS NACIONAIS ENTRAM POR TEXTO, NÃO POR CHAVE
  `registro_id` fica null e `registration_id_texto` carrega o número nacional.
  Motivo: a fundação `ES-REGULATORIO-ROPF-2026-08-29.sql` importou só os 96
  registros ADAMA da Espanha. Nem os dos concorrentes nem os de IT/FR estão no
  banco, e apontar chave estrangeira para linha inexistente faria o import
  falhar — ou, pior, faria alguém importar 36 mil registros por tabela vizinha
  e criar um segundo dono dos registros nacionais. O texto espera a fundação.

  A CHAVE DO EVENTO CARREGA O PAÍS. `REG:ES:...`, `REG:IT:...`, `REG:FR:...`
  Os três ministérios numeram por conta própria e nada garante que `008259`
  seja o mesmo produto nos três.
"""
import json
import os
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
S = os.path.join(RAIZ, 'data', 'samples')
DESTINO = os.path.join(RAIZ, 'supabase', 'importacoes')


def q(v):
    """Literal SQL. Vazio e None viram null — nunca string vazia disfarçada."""
    if v is None or v == '' or v == 'NOT_KNOWN':
        return 'null'
    return "'" + str(v).replace("'", "''") + "'"


def ler(nome):
    with open(os.path.join(S, nome), encoding='utf-8') as f:
        return json.load(f)


def monta():
    ev = ler('COMPETITOR-EVENTS.json')
    paridade = ler('COMPETITOR-EAME-PARIDADE.json')
    amostra = ler('COMPETITOR-PILOT-AMOSTRA.json')
    # os pares dos TRÊS países, cada um sabendo de qual registro nacional veio
    pares_todos = []
    for pais, bloco in paridade['POR_PAIS'].items():
        if bloco.get('ESTADO_DA_MEDICAO') != 'MEASURED':
            continue
        for p in bloco['PARES_TODOS']:
            pares_todos.append(dict(p, PAIS=pais))
    capturado = ev['captured_at']
    concorrentes = sorted(amostra['AMOSTRA_DO_PILOTO'])

    # ── quais eventos entram ──────────────────────────────────────────
    # Ordenados por event_key: o SQL é o mesmo em qualquer máquina.
    eventos = sorted(ev['EVENTOS']['LISTA'], key=lambda e: e['EVENT_ID'])
    entram, recusados = [], {'SEM_CLASSE_DECLARADA': 0, 'SEM_DATA_DO_FATO': 0,
                             'COMPETIDOR_NAO_RESOLVIDO': 0}
    for e in eventos:
        if e['COMPETITOR'] not in concorrentes:
            recusados['COMPETIDOR_NAO_RESOLVIDO'] += 1
            continue
        if e['CONFIDENCE_STATE'] == 'NOT_KNOWN':
            recusados['SEM_CLASSE_DECLARADA'] += 1
            continue
        if e['EVENT_DATE'] in (None, '', 'NOT_KNOWN'):
            recusados['SEM_DATA_DO_FATO'] += 1
            continue
        entram.append(e)

    # ── os links, e a perda que NÃO pode ser silenciosa ───────────────
    #
    # Um link só existe se os DOIS eventos entraram. O `insert ... select`
    # de um par cujo evento foi recusado não dá erro: produz zero linhas, em
    # silêncio. Medido aqui: 33 dos 242 pares do crosswalk caem assim.
    # Deixar o SQL engolir isso significaria publicar "242 links" e gravar
    # 209 — a diferença exata entre o que se afirma e o que existe.
    # Então a viabilidade é decidida ANTES, e a perda é declarada no
    # cabeçalho com o motivo de cada lado.
    entrando = {e['EVENT_ID'] for e in entram}

    def chaves(p):
        return (f"IP:{p['ST13']}",
                f"REG:{p['PAIS']}:{p['REGISTRATION_ID']}:LOCAL_REGISTRATION")

    perdidos = {'FALTA_O_EVENTO_DE_MARCA': 0, 'FALTA_O_EVENTO_DE_REGISTRO': 0,
                'FALTAM_OS_DOIS': 0}
    viaveis = []
    for p in pares_todos:
        a_ok, b_ok = (k in entrando for k in chaves(p))
        if a_ok and b_ok:
            viaveis.append(p)
        elif not a_ok and not b_ok:
            perdidos['FALTAM_OS_DOIS'] += 1
        elif not a_ok:
            perdidos['FALTA_O_EVENTO_DE_MARCA'] += 1
        else:
            perdidos['FALTA_O_EVENTO_DE_REGISTRO'] += 1

    cadeias = {c['CHAIN_ID']: c for c in ev['TIMELINES']['CADEIAS']}
    provados = [p for p in viaveis if p['ESTADO_DO_LINK'] == 'PROVED']
    recusas = [p for p in viaveis if p['ESTADO_DO_LINK'] != 'PROVED']

    linhas = []
    a = linhas.append
    a('-- ═══════════════════════════════════════════════════════════════════════')
    a('-- COMPETITOR_FORESIGHT_IMPORT_V1')
    a('--')
    a(f'-- Gerado por scripts/concorrente_importar.py a partir de')
    a('--   data/samples/COMPETITOR-EVENTS.json')
    a('--   data/samples/COMPETITOR-EAME-PARIDADE.json  (ES + IT + FR)')
    a('--   data/samples/COMPETITOR-PILOT-AMOSTRA.json')
    a('-- Determinístico: a mesma entrada produz este arquivo byte a byte.')
    a('--')
    a(f'-- CAPTURA: {capturado}')
    a(f'-- AMOSTRA: {", ".join(concorrentes)}')
    a('--')
    a('-- OBSERVED_AT != EFFECTIVE_DATE')
    a(f'--   observed_at    = {capturado} para TODAS as linhas: é quando nós olhamos.')
    a('--   effective_date = a data que a fonte declara. Pode ser futura, e isso')
    a('--   é legítimo: caducidade e limite de venda são datas futuras publicadas')
    a('--   hoje pelos registros nacionais.')
    a('--')
    a('-- O QUE NÃO ENTRA, E POR QUÊ')
    for k, v in sorted(recusados.items()):
        a(f'--   {k}: {v} eventos')
    a('--   PRODUCT_CATALOG / META / CREATOR: 0 eventos — NOT_JOINED_IN_THIS')
    a('--   _MISSION. O Creator Map existe em branch própria, com handoff')
    a('--   canônico, e a missão Meta corre em paralelo. Esta branch não os')
    a('--   junta; o refresh final junta os HANDOFFS. Zero aqui NUNCA é')
    a('--   "o concorrente não anuncia".')
    a('--   PATENT: DEMOTED — 0 de 5 marcas recuperaram patente do titular')
    a('--   correto. Ver data/samples/COMPETITOR-PATENT-DEMOTE.json.')
    a('--')
    a('-- OS REGISTROS NACIONAIS ENTRAM POR TEXTO, NÃO POR CHAVE')
    a('--   registro_id fica null. A fundação ES-REGULATORIO importou só os 96')
    a('--   registros ADAMA da Espanha; nem os dos concorrentes nem os de IT/FR')
    a('--   estão no banco. Apontar FK para linha inexistente quebraria o import,')
    a('--   e importá-los por aqui criaria um SEGUNDO dono do registro nacional.')
    a('--   A chave do evento carrega o PAÍS (REG:ES:..., REG:IT:..., REG:FR:...)')
    a('--   porque os três ministérios numeram por conta própria.')
    a('-- ═══════════════════════════════════════════════════════════════════════')
    a('')
    a('begin;')
    a('')
    a('-- ── 1 · os concorrentes, como organizacao. Reuso do dono da 002. ──')
    a('--    Sem ROR: o identificador é declarado, não inferido, e não temos.')
    for c in concorrentes:
        a(f"insert into public.organizacao (nome_canonico, tipo) values ({q(c)}, 'empresa')")
        a('  on conflict do nothing;')
    a('')
    a('-- ── 2 · os eventos ────────────────────────────────────────────────')
    a(f'-- {len(entram)} linhas')
    for e in entram:
        camada = 'IP' if e['EVENT_ID'].startswith('IP:') else 'REGULATORY'
        pais = e['COUNTRY']
        # o escritório EM é a marca da UE: no vocabulário do banco, pais 'EU'
        pais = 'EU' if pais == 'EM' else pais
        a('insert into public.evento_concorrente '
          '(event_key, competidor_id, pais, camada, event_type, observed_at, '
          'effective_date, fonte, source_url, evidencia, registration_id_texto, '
          'brand, confidence_state)')
        a(f'select {q(e["EVENT_ID"])}, o.id, {q(pais)}::pais, {q(camada)}, '
          f'{q(e["EVENT_TYPE"])}, {q(capturado)}::date, {q(e["EVENT_DATE"])}::date,')
        a(f'  {q(e["SOURCE"])}, {q(e["SOURCE_URL"])}, {q(e["EVIDENCE"])}, '
          f'{q(e["REGULATORY_ID"])}, {q(e["BRAND"])}, {q(e["CONFIDENCE_STATE"])}')
        a(f'from public.organizacao o where o.nome_canonico = {q(e["COMPETITOR"])}')
        a('on conflict (event_key) do nothing;')
    a('')
    a('-- ── 3 · os links do crosswalk ─────────────────────────────────────')
    a(f'-- O crosswalk EAME tem {len(pares_todos)} pares nos três países. '
      f'Entram {len(viaveis)}.')
    a(f'-- {len(provados)} PROVED · {len(recusas)} recusados, e a recusa TAMBÉM entra:')
    a('--    um piloto que só grava o que casou esconde a própria taxa de acerto.')
    a('--')
    a(f'-- OS {sum(perdidos.values())} PARES QUE NÃO ENTRAM, E POR QUÊ')
    a('--   Um link precisa dos DOIS eventos. O par cujo evento foi recusado')
    a('--   produziria zero linhas EM SILÊNCIO — a diferença exata entre o que')
    a('--   se afirma e o que existe. Por isso a perda é decidida aqui e escrita:')
    for k, v in sorted(perdidos.items()):
        a(f'--   {k}: {v}')
    a('--   Todos são pares PARTIAL ou REJECTED cujo registro pertence a titular')
    a('--   fora da amostra — logo sem evento REGULATORY nesta rodada.')

    def link(p, estado, lead=None, defensavel=False):
        ip_key, reg_key = chaves(p)
        ev_txt = p['MOTIVO'].replace('\n', ' ')
        a('insert into public.evento_concorrente_link '
          '(evento_a_id, evento_b_id, estado, evidencia, lead_days, lead_days_defensavel)')
        a(f'select a.id, b.id, {q(estado)}, {q(ev_txt)}, '
          f'{"null" if lead is None else lead}, {str(defensavel).lower()}')
        a(f'from public.evento_concorrente a, public.evento_concorrente b')
        a(f'where a.event_key = {q(ip_key)} and b.event_key = {q(reg_key)}')
        a('on conflict (evento_a_id, evento_b_id) do nothing;')

    for p in sorted(provados, key=lambda x: (x['ST13'], x['REGISTRATION_ID'])):
        cid = f"{p['PAIS']}:{p['GRUPO_DA_MARCA']}:{p['ST13']}:{p['REGISTRATION_ID']}"
        c = cadeias[cid]     # KeyError proposital: cadeia faltando é erro, não null
        lead = c['LEAD_DAYS'] if c else None
        defensavel = bool(c and c['LEAD_DAYS_DEFENSAVEL'])
        # a trava do banco só aceita lead sobre PROVED; e defensável exige > 0
        link(p, 'PROVED', lead, defensavel)
    for p in sorted(recusas, key=lambda x: (x['ST13'], x['REGISTRATION_ID'])):
        estado = ('REJECTED_HOLDER_MISMATCH'
                  if p['ESTADO_DO_LINK'] == 'REJECTED_HOLDER_MISMATCH' else 'PARTIAL')
        link(p, estado)          # sem lead_days: a trava do banco recusaria
    a('')
    a('commit;')
    a('')
    return '\n'.join(linhas) + '\n', {
        'EVENTOS_IMPORTADOS': len(entram),
        'EVENTOS_RECUSADOS': recusados,
        'PARES_NO_CROSSWALK_EAME': len(pares_todos),
        'LINKS_PROVED': len(provados),
        'LINKS_RECUSADOS': len(recusas),
        'LINKS_GRAVADOS': len(viaveis),
        'PARES_QUE_NAO_VIRAM_LINK': perdidos,
        'ORGANIZACOES': len(concorrentes),
        'CAPTURA': capturado,
    }


def main():
    sql, contas = monta()
    os.makedirs(DESTINO, exist_ok=True)
    caminho = os.path.join(DESTINO, f'COMPETITOR-FORESIGHT-{contas["CAPTURA"]}.sql')
    with open(caminho, 'w', encoding='utf-8', newline='\n') as f:
        f.write(sql)
    print(json.dumps(contas, ensure_ascii=False, indent=2))
    print('gravado:', caminho)
    if '--contagens' in sys.argv:
        return contas


if __name__ == '__main__':
    main()
