#!/usr/bin/env python3
"""
ITÁLIA — censo regulatório nacional e inventário ADAMA, derivados da fonte.

COUNTRY = IT faz parte da verdade, não é filtro visual.

O defeito que este arquivo fecha: a primeira passagem italiana mediu o portfólio ADAMA
pela string `ADAMA ITALIA S.R.L.` e publicou **155**. A string não é a entidade. O registro
italiano traz **sete** razões sociais do grupo, e cinco delas declaram a própria sede
administrativa como `C/O ADAMA ITALIA S.R.L. - VIA ZANICA, 19 ... GRASSOBBIO`.

Essa declaração é do próprio registro. Não é semelhança de nome, não é conhecimento de
mercado, não é fuzzy match: é um campo que a fonte publica. Por isso o vínculo é
`MATCHED_WITH_EVIDENCE` e a evidência citável é o endereço declarado.

E por isso mesmo duas razões sociais que "parecem" ADAMA **não** entram no núcleo:

  · `MAGAN ITALIA S.R.L.` — VIA G. FALCONE, 13, BERGAMO. Não declara c/o ADAMA. O nome
    lembra Makhteshim-**Agan**, e é exatamente esse tipo de semelhança que a regra proíbe
    usar como prova. Fica `AMBIGUOUS`, contado à parte, nunca somado em silêncio.
  · `MAKHTESHIM AGAN HOLLAND B.V.` — declara c/o `MAKHTESHIM AGAN ITALIA S.R.L.`,
    VIA G. VERDI, 12. Outro endereço e outra razão social. Fica `HISTORICAL_PREDECESSOR`,
    também contado à parte.

Portanto este módulo publica TRÊS denominadores e nunca um só:

    ADAMA_IT_LEGAL_ENTITY   só `ADAMA ITALIA S.R.L.`
    ADAMA_GROUP_IT_CORE     as cinco com c/o ADAMA ITALIA declarado no registro
    ADAMA_IT_ADJACENT       as duas sem evidência de registro, nomeadas uma a uma

Quem citar um número tem de dizer qual dos três está citando.

Leis que este arquivo exerce (docs/regras/, seção O do HANDOFF):
    REGISTRATION ≠ SALES
    REGISTRATION ≠ COMMERCIAL AVAILABILITY
    EXPIRY ≠ WITHDRAWAL          — vencimento de autorização não é retirada do mercado
    SOURCE_LOCATION ≠ FACT_LOCATION — a sede da empresa é local da EMPRESA
    NAME ≠ ORGANIZATION
"""
import csv
import datetime
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

COUNTRY = 'IT'
SOURCE_ID = 'IT-T4-001'
SOURCE_NAME = 'Ministero della Salute — Banca dati dei prodotti fitosanitari'
LICENSE = 'CC BY 4.0'
NAO_SEI = 'NÃO SEI'

# A sede administrativa declarada pelo próprio registro. É esta string, no campo
# `indirizzo_sede_amministrativa`, que prova o vínculo — não o nome da razão social.
SEDE_ADAMA_IT = 'ADAMA ITALIA S.R.L.'
VIA_ADAMA_IT = 'VIA ZANICA'

HOLDER_LEGAL_ENTITY = 'ADAMA ITALIA S.R.L.'

# Estados administrativos que NÃO são autorização vigente.
STATUS_REVOGADO = 'Revocato'
STATUS_SCADUTO = 'Scaduto'
STATUS_SOSPESO = 'Sospeso'
STATUS_NAO_VIGENTE = {STATUS_REVOGADO, STATUS_SCADUTO, STATUS_SOSPESO}


def _data(s):
    """dd/mm/aaaa → date. '-' e vazio devolvem None, e None NÃO é data no passado."""
    s = (s or '').strip()
    if not s or s == '-':
        return None
    try:
        return datetime.datetime.strptime(s, '%d/%m/%Y').date()
    except ValueError:
        return None


def carregar(path):
    with open(path, encoding='utf-8', errors='replace') as fh:
        return list(csv.DictReader(fh, delimiter=';'))


def classificar_titular(row):
    """Devolve (ESCOPO, EVIDENCE) para a razão social da linha.

    Nunca decide por semelhança de nome. Decide por campo declarado no registro.
    """
    nome = (row.get('ragione_sociale') or '').strip()
    sede_amm = (row.get('indirizzo_sede_amministrativa') or '').upper()

    if nome == HOLDER_LEGAL_ENTITY:
        return 'ADAMA_IT_LEGAL_ENTITY', 'ragione_sociale == %s' % HOLDER_LEGAL_ENTITY

    # O vínculo do núcleo é a sede administrativa declarada, e exige as DUAS marcas:
    # a razão social da entidade italiana E a via. Uma só seria frágil.
    if SEDE_ADAMA_IT in sede_amm and VIA_ADAMA_IT in sede_amm:
        return 'ADAMA_GROUP_IT_CORE', 'indirizzo_sede_amministrativa declara c/o %s' % SEDE_ADAMA_IT

    if 'ADAMA' in nome.upper() or 'MAKHTESHIM' in nome.upper() or 'MAGAN' in nome.upper():
        return 'ADAMA_IT_ADJACENT', 'nome sugere o grupo; registro NÃO declara sede c/o ADAMA ITALIA'

    return 'OUTRO', ''


def censo_nacional(rows):
    """O denominador italiano. Sem ele, nenhum número ADAMA tem escala."""
    por_status = {}
    for r in rows:
        st = (r.get('stato_amministrativo') or '').strip()
        por_status[st] = por_status.get(st, 0) + 1
    vigentes = [r for r in rows
                if (r.get('stato_amministrativo') or '').strip() not in STATUS_NAO_VIGENTE]
    return {
        'TOTAL_PRODUCTS': len(rows),
        'DISTINCT_REGISTRATIONS': len({r['num_registrazione'] for r in rows}),
        'DISTINCT_HOLDERS': len({(r.get('ragione_sociale') or '').strip() for r in rows}),
        'CURRENT_AUTHORIZED': len(vigentes),
        'REVOKED': por_status.get(STATUS_REVOGADO, 0),
        'EXPIRED': por_status.get(STATUS_SCADUTO, 0),
        'SUSPENDED': por_status.get(STATUS_SOSPESO, 0),
        'BY_STATUS': dict(sorted(por_status.items(), key=lambda kv: -kv[1])),
    }


def substancias(valor):
    """`sostanze_attive` vem separado por '|'. '-' é ausência declarada, não substância."""
    v = (valor or '').strip()
    if not v or v == '-':
        return []
    return [s.strip() for s in v.split('|') if s.strip() and s.strip() != '-']


def inventario_adama(rows, hoje):
    """Inventário por escopo. Cada escopo é um denominador próprio."""
    escopos = {}
    for r in rows:
        escopo, evid = classificar_titular(r)
        if escopo == 'OUTRO':
            continue
        # O núcleo inclui a entidade legal italiana: ela é o centro do vínculo.
        alvos = [escopo]
        if escopo == 'ADAMA_IT_LEGAL_ENTITY':
            alvos.append('ADAMA_GROUP_IT_CORE')
        for a in alvos:
            escopos.setdefault(a, []).append((r, evid))

    saida = {}
    for escopo, itens in escopos.items():
        rs = [r for r, _ in itens]
        vigentes = [r for r in rs
                    if (r.get('stato_amministrativo') or '').strip() not in STATUS_NAO_VIGENTE]
        subst = set()
        for r in vigentes:
            subst.update(substancias(r.get('sostanze_attive')))

        # Vencimento: só conta quem TEM data. Data ausente é NÃO SEI, nunca "não vence".
        venc = []
        sem_data = 0
        for r in vigentes:
            d = _data(r.get('data_scadenza_autorizzazione'))
            if d is None:
                sem_data += 1
            else:
                venc.append((d, r))
        d6 = hoje + datetime.timedelta(days=183)
        d12 = hoje + datetime.timedelta(days=365)
        futuros = [(d, r) for d, r in venc if d >= hoje]
        passados = [(d, r) for d, r in venc if d < hoje]

        saida[escopo] = {
            'HOLDER_STRINGS': sorted({(r.get('ragione_sociale') or '').strip() for r in rs}),
            'IDENTITY_EVIDENCE': sorted({e for _, e in itens if e}),
            'REGISTRATIONS_TOTAL': len(rs),
            'ACTIVE': len(vigentes),
            'REVOKED': sum(1 for r in rs
                           if (r.get('stato_amministrativo') or '').strip() == STATUS_REVOGADO),
            'EXPIRED_STATUS': sum(1 for r in rs
                                  if (r.get('stato_amministrativo') or '').strip() == STATUS_SCADUTO),
            'SUSPENDED': sum(1 for r in rs
                             if (r.get('stato_amministrativo') or '').strip() == STATUS_SOSPESO),
            'UNIQUE_PRODUCT_NAMES': len({(r.get('denominazione_prodotto') or '').strip() for r in rs}),
            'UNIQUE_PRODUCT_NAMES_ACTIVE': len({(r.get('denominazione_prodotto') or '').strip()
                                                for r in vigentes}),
            'ACTIVE_SUBSTANCES': sorted(subst),
            'ACTIVE_SUBSTANCES_COUNT': len(subst),
            # Autorização vigente cuja data já passou: o registro não a moveu para 'Scaduto'.
            # É anomalia da fonte, e se declara como anomalia — não se "corrige" por conta própria.
            'ACTIVE_WITH_PAST_EXPIRY': len(passados),
            'ACTIVE_WITHOUT_EXPIRY_DATE': sem_data,
            'ACTIVE_WITH_FUTURE_EXPIRY': len(futuros),
            'EXPIRING_6M': sum(1 for d, _ in futuros if d <= d6),
            'EXPIRING_12M': sum(1 for d, _ in futuros if d <= d12),
            'EXPIRING_6M_DETAIL': [
                {
                    'expiry': d.isoformat(),
                    'reg': r['num_registrazione'],
                    'product': (r.get('denominazione_prodotto') or '').strip(),
                    'holder': (r.get('ragione_sociale') or '').strip(),
                    'actives': (r.get('sostanze_attive') or '').strip(),
                    'formulation': (r.get('descrizione_formulazione') or '').strip(),
                    'status': (r.get('stato_amministrativo') or '').strip(),
                }
                for d, r in sorted(futuros, key=lambda t: t[0]) if d <= d6
            ],
        }
    return saida


def main():
    path = os.path.join(ROOT, 'data', 'raw', 'IT', 'PROD_FTS_6_20260824.csv')
    if len(sys.argv) > 1 and not sys.argv[1].startswith('--'):
        path = sys.argv[1]
    hoje = datetime.date.today()
    rows = carregar(path)
    censo = censo_nacional(rows)
    inv = inventario_adama(rows, hoje)

    if '--json' in sys.argv:
        print(json.dumps({'CENSO': censo, 'ADAMA': inv}, ensure_ascii=False, indent=2))
        return

    print('COUNTRY = %s · SOURCE = %s' % (COUNTRY, SOURCE_ID))
    print('ARQUIVO  %s' % os.path.basename(path))
    print()
    print('CENSO NACIONAL')
    for k in ('TOTAL_PRODUCTS', 'DISTINCT_HOLDERS', 'CURRENT_AUTHORIZED',
              'REVOKED', 'EXPIRED', 'SUSPENDED'):
        print('  %-24s %s' % (k, censo[k]))
    print()
    for escopo in ('ADAMA_IT_LEGAL_ENTITY', 'ADAMA_GROUP_IT_CORE', 'ADAMA_IT_ADJACENT'):
        d = inv.get(escopo)
        if not d:
            continue
        print('%s  (%d razões sociais)' % (escopo, len(d['HOLDER_STRINGS'])))
        for h in d['HOLDER_STRINGS']:
            print('    · %s' % h)
        for k in ('REGISTRATIONS_TOTAL', 'ACTIVE', 'REVOKED', 'EXPIRED_STATUS',
                  'UNIQUE_PRODUCT_NAMES_ACTIVE', 'ACTIVE_SUBSTANCES_COUNT',
                  'ACTIVE_WITH_FUTURE_EXPIRY', 'ACTIVE_WITH_PAST_EXPIRY',
                  'EXPIRING_6M', 'EXPIRING_12M'):
            print('  %-28s %s' % (k, d[k]))
        print()


if __name__ == '__main__':
    main()
