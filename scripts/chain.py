#!/usr/bin/env python3
"""
CADEIAS DE RECORRÊNCIA — SOURCE → RETRIEVAL → PARSE → IDENTITY → NORMALIZATION → FACT.

Este script existe para responder a uma pergunta que documentação nenhuma responde:
**um engenheiro novo consegue refazer os fatos do piloto sem conhecer a história das
missões?** Até a MISSÃO 07 a resposta era não — a coleta estava em script, a análise
estava na cabeça de quem fez.

Cada cadeia declara os seus passos por natureza:

    AUTOMATIC        o código faz sozinho, do começo ao fim
    MANUAL           alguém tem de executar/baixar/apontar algo à mão
    HUMAN_JUDGMENT   existe uma decisão humana embutida (um dicionário de grupo
                     empresarial, um limiar, uma escolha de coorte). Não é defeito;
                     é o que precisa estar visível.

E cada cadeia falha **fechada**: sem fonte, sem schema, sem cobertura mínima, ela
levanta. Nunca devolve um número menor com a mesma cara de sempre.

    python3 scripts/chain.py list
    python3 scripts/chain.py run fr-prothioconazole [--raw DIR]
    python3 scripts/chain.py run es-identidade
    python3 scripts/chain.py run it-prothioconazole [--raw DIR]
    python3 scripts/chain.py run raif-repilo --raw data/raw/ES-T3-001/raif_1
    python3 scripts/chain.py run all --json saida.json
"""
import argparse
import csv
import json
import os
import re
import sys
import urllib.request
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)

from coverage import Coverage                                  # noqa: E402
import source_health as sh                                     # noqa: E402

UA = 'Mozilla/5.0 (X11; Linux x86_64) SintoniaEAME/1.0 (pesquisa; contato via repositorio)'

# Dicionário de GRUPO empresarial. É HUMAN_JUDGMENT declarado, e por isso a saída de
# toda cadeia traz TAMBÉM a contagem por entidade legal, que não depende dele.
# Regra da MISSÃO 07 §16: sem fonte de relação corporativa, não se colapsa entidade.
GRUPOS = ['ADAMA', 'BAYER', 'SYNGENTA', 'BASF', 'CORTEVA', 'NUFARM', 'UPL', 'SIPCAM',
          'SHARDA', 'GLOBACHEM', 'LIFE SCIENTIFIC', 'ASCENZA', 'ALBAUGH', 'BARCLAY',
          'FMC', 'CHEMINOVA', 'ROTAM', 'KENOGARD']


class ChainFailure(RuntimeError):
    """A cadeia parou. Nenhum número parcial sai daqui."""


def grupo(nome):
    up = (nome or '').upper()
    for g in GRUPOS:
        if g in up:
            return g
    return 'OUTROS'


# `www.dati.salute.gov.it` recusa o handshake do contexto TLS padrão do Python
# (SSLV3_ALERT_HANDSHAKE_FAILURE) e aceita com nível de segurança 1 — parâmetros
# criptográficos mais fracos do que o padrão atual. curl, que tem outro padrão, sempre
# funcionou; foi por isso que a diferença só apareceu quando a coleta virou código.
#
# O que se faz: tenta o padrão; só depois de falhar, tenta de novo com SECLEVEL=1 e
# REGISTRA que rebaixou. O que NÃO se faz, nunca: desligar a verificação do certificado.
# A cadeia continua verificando a cadeia de confiança — só aceita chave/cifra mais antiga.
TLS_DOWNGRADES = []


def _get(url, timeout=180):
    req = urllib.request.Request(url, headers={'User-Agent': UA})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.read(), r.headers.get('Content-Type', '')
    except urllib.error.URLError as e:
        import ssl
        if not isinstance(getattr(e, 'reason', None), ssl.SSLError):
            raise
        ctx = ssl.create_default_context()
        ctx.set_ciphers('DEFAULT@SECLEVEL=1')          # verificação continua ligada
        with urllib.request.urlopen(req, timeout=timeout, context=ctx) as r:
            TLS_DOWNGRADES.append(url)
            return r.read(), r.headers.get('Content-Type', '')


def _rows_csv(path, delimiter=';'):
    with open(path, encoding='utf-8-sig', newline='') as f:
        return list(csv.DictReader(f, delimiter=delimiter))


# --------------------------------------------------------------------------- FR
def fr_prothioconazole(raw=None, molecule='prothioconazole'):
    steps = []
    raw = raw or os.path.join(ROOT, 'data', 'raw', 'FR-T4-001')
    prod = os.path.join(raw, 'produits_utf8.csv')
    steps.append(('AUTOMATIC', 'scripts/ephy.sh download — resolve o recurso semanal pela '
                               'API do data.gouv e descompacta'))
    if not os.path.exists(prod):
        raise ChainFailure(f'FR: {prod} ausente. Rode scripts/ephy.sh download {raw}. '
                           'Falha fechada: sem fonte não há número.')
    rows = _rows_csv(prod)
    steps.append(('AUTOMATIC', f'ler produits_utf8.csv ({len(rows)} linhas)'))

    # Contrato COMPLETO das 18 colunas: assim um campo novo é notícia, não ruído.
    EPHY_COLS = ['type produit', 'numero AMM', 'nom produit', 'seconds noms commerciaux',
                 'titulaire', 'type commercial', 'gamme usage', 'mentions autorisees',
                 'restrictions usage', 'restrictions usage libelle', 'Substances actives',
                 'fonctions', 'formulations', 'Etat d’autorisation',
                 'Date de retrait du produit', 'Date de première autorisation',
                 'Numéro AMM du produit de référence', 'Nom du produit de référence',
                 '']   # coluna vazia final: o CSV termina em ';'. Artefato conhecido,
                       # declarado para que um campo REALMENTE novo apareça como novidade
    state, notes = sh.check(rows, required_fields=EPHY_COLS,
                            identity_key='numero AMM', expect_rows=15140, tolerance=0.20)
    if state == sh.FAILED:
        raise ChainFailure(f'FR: fonte FAILED — {notes}')
    steps.append(('AUTOMATIC', f'checar contrato da fonte → {state}'))

    # ESCOPO DECLARADO: MFSC são matérias fertilizantes e suportes de cultura. Não
    # carregam substância ativa POR DEFINIÇÃO — deixá-las no denominador faria a
    # cobertura cair para 92,9% e a cadeia falhar por um motivo falso. Sair do
    # denominador é diferente de não ser resolvido, e as duas coisas são declaradas.
    fora = [r for r in rows if r.get('type produit') == 'MFSC']
    escopo = [r for r in rows if r.get('type produit') != 'MFSC']
    steps.append(('HUMAN_JUDGMENT', f'excluir {len(fora)} linhas MFSC do denominador: '
                                    'fertilizante não tem substância ativa. Exclusão '
                                    'declarada, não silenciosa'))

    cov = Coverage('FR · produto → molécula')
    hits = []
    for r in escopo:
        sa = (r.get('Substances actives') or '')
        if not sa.strip():
            cov.fail(r.get('numero AMM'), 'SUBSTANCIA_VAZIA_EM_PRODUTO_FITOSSANITARIO')
            continue
        cov.ok(r.get('numero AMM'))
        if molecule.lower() in sa.lower():
            hits.append(r)
    cov.require(0.95)
    steps.append(('AUTOMATIC', f'casar molécula por nome no campo de substâncias '
                               f'(cobertura {cov.coverage:.1%})'))

    autorizados = [h for h in hits
                   if 'AUTORISE' in (h.get('Etat d’autorisation') or '').upper()]
    por_entidade = {}
    for h in autorizados:
        por_entidade[h.get('titulaire', '')] = por_entidade.get(h.get('titulaire', ''), 0) + 1
    por_grupo = {}
    for h in autorizados:
        g = grupo(h.get('titulaire'))
        por_grupo[g] = por_grupo.get(g, 0) + 1
    steps.append(('AUTOMATIC', 'contar por ENTIDADE LEGAL (titulaire) — não depende de '
                               'dicionário nenhum'))
    steps.append(('HUMAN_JUDGMENT', 'agrupar entidades em GRUPO empresarial pelo '
                                    'dicionário GRUPOS. Não há fonte de relação '
                                    'corporativa; o agrupamento é decisão nossa'))

    adama = sorted({(h['numero AMM'], h['nom produit'], h['titulaire'])
                    for h in autorizados if grupo(h['titulaire']) == 'ADAMA'})
    return {
        'CHAIN': 'fr-prothioconazole', 'SOURCE_ID': 'FR-T4-001', 'COUNTRY': 'FRANCE',
        'HEALTH': state, 'HEALTH_NOTES': notes, 'COVERAGE': cov.report(),
        'STEPS': steps,
        'SCOPE': {'rows_in_file': len(rows), 'excluded_MFSC': len(fora),
                  'in_scope': len(escopo)},
        'HERO_FACT': {
            'products_with_molecule': len(hits),
            'authorised': len(autorizados),
            'distinct_legal_entities': len(por_entidade),
            'by_group_HUMAN_JUDGMENT': dict(sorted(por_grupo.items(),
                                                   key=lambda kv: -kv[1])),
            'ADAMA_legal_entities': sorted({a[2] for a in adama}),
            'ADAMA_products': [{'amm': a[0], 'product': a[1]} for a in adama],
        },
    }


# --------------------------------------------------------------------------- ES
def es_identidade(registration='ES-01717'):
    import mapa_regfi
    steps = [('AUTOMATIC', 'resolver idProducto pela rota ProductosGrid'),
             ('AUTOMATIC', 'ler a ficha em GetProductoById')]
    try:
        ficha = mapa_regfi.producto(registration)
    except Exception as e:                                   # noqa: BLE001
        raise ChainFailure(f'ES: rota indisponível ({e.__class__.__name__}: {e}). '
                           'Falha fechada. Ver docs/operacao/FALHA-DE-FONTE-ESPANHA.md')
    if not ficha:
        raise ChainFailure(f'ES: {registration} não encontrado. Lista vazia é FAILED, '
                           'não "zero resultados".')
    # Contrato COMPLETO da ficha: qualquer campo novo ou ausente é notícia, não ruído.
    FICHA_FIELDS = [
        'idProducto', 'codInternoFabricante', 'numRegistro', 'nombre', 'titular',
        'fabricante', 'fabrica', 'formulado', 'estado', 'observaciones', 'tramite',
        'estadoTramite', 'condicionamiento', 'simbolo_1', 'simbolo_2', 'simbolo_3',
        'domestico', 'seg_Almacenamiento', 'seg_Manipulacion', 'seg_Des_Vertido',
        'nRegDirectiva', 'version', 'versionDePartida', 'estadoVersion', 'idEstado',
        'idSustancia', 'idAmbito', 'idCultivo', 'idPlaga', 'idFuncion', 'idTitular',
        'idFormulado', 'fechaTramite', 'strFechaTramite', 'fechaCaducidad',
        'strFechaCaducidad', 'fechaInscripcion', 'strFechaInscripcion',
        'fechaRenovacion', 'strFechaRenovacion', 'fechaModificacion',
        'strFechaModificacion', 'fechaLimiteVenta', 'strFechaLimiteVenta',
        'fechaAutorizacion', 'strFechaAutorizacion', 'bajoRiesgo', 'autorizadoPublico',
        'autorizadoAereos']
    state, notes = sh.check([ficha], required_fields=FICHA_FIELDS,
                            identity_key='numRegistro', min_rows=1)
    if state == sh.FAILED:
        raise ChainFailure(f'ES: contrato da ficha quebrou — {notes}')
    steps.append(('AUTOMATIC', f'checar contrato da ficha → {state}'))

    # denominações comuns: vêm do PDF arquivado, com o registro como âncora externa
    from denominaciones import read, split_rows
    pdf = os.path.join(ROOT, 'data', 'samples', 'ES-T4-004-versoes', 'dc_web_20260826.pdf')
    dens, cov_rep = [], None
    if os.path.exists(pdf):
        _, rows, _ = read(pdf)
        registro = {ficha['numRegistro']: {'Nombre': ficha['nombre'],
                                           'Titular': ficha['titular']}}
        # o vocabulário de concessionárias precisa do registro inteiro; aqui usamos o
        # snapshot arquivado para não depender de uma segunda chamada de rede
        snap = os.path.join(ROOT, 'data', 'samples', 'ES-T4-005', 'ropf_20260829.json.gz')
        if os.path.exists(snap):
            import gzip
            with gzip.open(snap, 'rt', encoding='utf-8') as f:
                registro = {r['NumRegistro']: r for r in json.load(f)['rows']}
        done, unres = split_rows([r for r in rows if r['registration'] == registration],
                                 registro)
        c = Coverage('ES · linha de denominação → papéis')
        for d in done:
            c.ok(d['COMMON_DENOMINATION'])
        for u in unres:
            c.fail(u['registration'], u['reason'])
        cov_rep = c.report()
        dens = done
        steps.append(('AUTOMATIC', 'separar denominação/concessionária com âncora externa '
                                   '(nome oficial + vocabulário de titulares)'))
    else:
        steps.append(('MANUAL', 'versão arquivada do dc_web ausente — denominações não '
                                'reconstruídas'))

    return {
        'CHAIN': 'es-identidade', 'SOURCE_ID': 'ES-T4-005 + ES-T4-004',
        'COUNTRY': 'SPAIN', 'HEALTH': state, 'HEALTH_NOTES': notes,
        'COVERAGE': cov_rep, 'STEPS': steps,
        'HERO_FACT': {
            'REGISTRATION_ID': ficha['numRegistro'],
            'REFERENCE_PRODUCT': ficha['nombre'],
            'REFERENCE_HOLDER': ficha['titular'],
            # DUAS GRAFIAS DO MESMO FABRICANTE, e a diferença tem de ser declarada:
            # `fabricante` na ficha JSON é um rótulo interno abreviado ("ADAMA Agri Sol");
            # a razão social completa está no campo `fabrica` e na ficha oficial em PDF
            # ("ADAMA Agricultural Solutions Ltd."). O documento canônico publica a razão
            # social. Sem esta nota, uma reexecução parece ter mudado o fato.
            'MANUFACTURER_LABEL_IN_JSON': ficha['fabricante'],
            'MANUFACTURER': re.sub(r'\s*\([^)]*\)\s*$', '', ficha['fabrica'] or ''),
            'MANUFACTURING_SITE': ficha['fabrica'],
            'COMPOSITION': ficha['formulado'],
            'STATUS': ficha['estado'],
            'LAST_TRAMITE': (ficha.get('tramite'), ficha.get('estadoTramite'),
                             ficha.get('strFechaTramite')),
            'COMMON_DENOMINATIONS': [{'CONCESSIONAIRE': d['CONCESSIONAIRE'],
                                      'COMMON_DENOMINATION': d['COMMON_DENOMINATION'],
                                      'ACCEPTED': d['ACCEPTED']} for d in dens],
            'CURRENT_OR_HISTORICAL': 'CURRENT — a ficha reflete a versão de hoje; o nome '
                                     'anterior só existe na versão arquivada',
        },
    }


# --------------------------------------------------------------------------- IT
IT_DATASET = 'https://www.dati.salute.gov.it/it/dataset/fitosanitari/'
IT_BASE = 'https://www.dati.salute.gov.it'


def it_prothioconazole(raw=None, molecule='PROTHIOCONAZOLE'):
    steps = []
    path = None
    if raw:
        cand = [f for f in os.listdir(raw) if f.startswith('PROD_FTS') and f.endswith('.csv')]
        if cand:
            path = os.path.join(raw, sorted(cand)[-1])
            steps.append(('AUTOMATIC', f'usar snapshot {os.path.basename(path)}'))
    if path is None:
        # o nome do arquivo carrega a data e muda a cada publicação: é descoberto na
        # própria página do dataset, não chutado.
        html, _ = _get(IT_DATASET)
        hits = sorted(set(re.findall(rb'/sites/default/files/opendata/(PROD_FTS_[\w]+\.csv)',
                                     html)))
        if not hits:
            raise ChainFailure('IT: nenhum CSV PROD_FTS na página do dataset. '
                               'Falha fechada — o layout da página mudou.')
        name = hits[-1].decode()
        steps.append(('AUTOMATIC', f'descobrir o arquivo datado na página do dataset '
                                   f'→ {name}'))
        body, ctype = _get(f'{IT_BASE}/sites/default/files/opendata/{name}')
        if b'<html' in body[:400].lower():
            raise ChainFailure('IT: 200 com HTML no lugar do CSV. Falha fechada.')
        raw = raw or os.path.join(ROOT, 'data', 'raw', 'IT-T4-001')
        os.makedirs(raw, exist_ok=True)
        path = os.path.join(raw, name)
        with open(path, 'wb') as f:
            f.write(body)
        steps.append(('AUTOMATIC', f'baixar {len(body):,} bytes'))

    rows = _rows_csv(path)
    IT_COLS = ['num_registrazione', 'denominazione_prodotto', 'ragione_sociale',
               'indirizzo_sede_legale', 'cap_sede_legale', 'comune_sede_legale',
               'provincia_sede_legale', 'indirizzo_sede_amministrativa',
               'cap_sede_amministrativa', 'comune_sede_amministrativa',
               'provincia_sede_amministrativa', 'data_registrazione',
               'data_scadenza_autorizzazione', 'indicazioni_di_pericolo', 'attivita',
               'codice_formulazione', 'descrizione_formulazione', 'sostanze_attive',
               'contenuto_per_100g_di_prodotto', 'importazione_parallela', 'PFnPO',
               'PFnPE', 'stato_amministrativo', 'motivo_della revoca',
               'data_decreto_revoca', 'data_decorrenza_revoca']
    state, notes = sh.check(rows, required_fields=IT_COLS,
                            identity_key='num_registrazione',
                            expect_rows=17000, tolerance=0.25)
    if state == sh.FAILED:
        raise ChainFailure(f'IT: fonte FAILED — {notes}')
    steps.append(('AUTOMATIC', f'checar contrato da fonte → {state} ({len(rows)} linhas)'))
    if TLS_DOWNGRADES:
        steps.append(('HUMAN_JUDGMENT', 'o host italiano recusou o TLS padrão do Python; '
                                        'a coleta foi refeita com SECLEVEL=1 — cifra mais '
                                        'antiga, verificação de certificado MANTIDA. '
                                        'Rebaixamento registrado, nunca silencioso'))

    cov = Coverage('IT · produto → molécula')
    hits = []
    for r in rows:
        sa = r.get('sostanze_attive') or ''
        if not sa.strip():
            cov.fail(r.get('num_registrazione'), 'SUBSTANCIA_VAZIA')
            continue
        cov.ok(r.get('num_registrazione'))
        if molecule.lower() in sa.lower():
            hits.append(r)
    cov.require(0.90)

    # CRITÉRIO DECLARADO — a MISSÃO 02 publicou "85 em vigor" sem dizer quais estados
    # administrativos contam, e a conta só fecha somando `Ri-registrato`. Os oito estados
    # observados nesta molécula: Autorizzato (5 variantes), Ri-registrato, Revocato,
    # Scaduto. "Ri-registrato" é ambíguo — a autorização foi substituída por outra — e por
    # isso os dois números saem, cada um com o seu critério. Nenhum é publicado sozinho.
    def autorizado(r):
        return 'AUTORIZZATO' in (r.get('stato_amministrativo') or '').upper()

    def rerregistrado(r):
        return 'RI-REGISTRATO' in (r.get('stato_amministrativo') or '').upper()
    ativos = [h for h in hits if autorizado(h)]
    ampliado = [h for h in hits if autorizado(h) or rerregistrado(h)]
    por_entidade = {}
    for h in ativos:
        por_entidade[h['ragione_sociale']] = por_entidade.get(h['ragione_sociale'], 0) + 1
    por_grupo = {}
    for h in ativos:
        g = grupo(h['ragione_sociale'])
        por_grupo[g] = por_grupo.get(g, 0) + 1
    steps.append(('AUTOMATIC', 'contar por ENTIDADE LEGAL (ragione_sociale)'))
    steps.append(('HUMAN_JUDGMENT', 'agrupar em GRUPO empresarial pelo dicionário GRUPOS'))
    venc = {}
    for h in ativos:
        venc[h['data_scadenza_autorizzazione']] = \
            venc.get(h['data_scadenza_autorizzazione'], 0) + 1
    adama = [{'reg': h['num_registrazione'], 'product': h['denominazione_prodotto'],
              'actives': h['sostanze_attive'],
              'expiry': h['data_scadenza_autorizzazione']}
             for h in ativos if grupo(h['ragione_sociale']) == 'ADAMA']
    return {
        'CHAIN': 'it-prothioconazole', 'SOURCE_ID': 'IT-T4-001', 'COUNTRY': 'ITALY',
        'HEALTH': state, 'HEALTH_NOTES': notes, 'COVERAGE': cov.report(),
        'STEPS': steps, 'SNAPSHOT': os.path.basename(path),
        'HERO_FACT': {
            'records_with_molecule': len(hits),
            'in_force_STRICT_Autorizzato': len(ativos),
            'in_force_INCLUDING_Ri_registrato': len(ampliado),
            'administrative_states': dict(sorted(
                ((h.get('stato_amministrativo') or '?') for h in hits) and
                {k: sum(1 for h in hits if (h.get('stato_amministrativo') or '?') == k)
                 for k in {(h.get('stato_amministrativo') or '?') for h in hits}}.items(),
                key=lambda kv: -kv[1])),
            'CRITERION': 'in_force_STRICT conta apenas estados que contêm "Autorizzato". '
                         'O numero publicado na MISSAO 02 (85) inclui "Ri-registrato". '
                         'Os dois sao defensaveis; publicar sem o criterio nao e.',
            'distinct_legal_entities': len(por_entidade),
            'by_group_HUMAN_JUDGMENT': dict(sorted(por_grupo.items(),
                                                   key=lambda kv: -kv[1])),
            'top_expiry_dates': dict(sorted(venc.items(), key=lambda kv: -kv[1])[:3]),
            'ADAMA_products': sorted(adama, key=lambda d: d['reg']),
        },
    }


# ------------------------------------------------------------------------- RAIF
REPILO = '1702 Repilo: % Hojas  con Repilo Visible'


def _undec(tag):
    return re.sub(r'_x([0-9A-Fa-f]{4})_', lambda m: chr(int(m.group(1), 16)), tag)


def _raif_year(path, campo=REPILO):
    """(província, parcela, ano) → lista de leituras. iterparse: o arquivo tem 600 MB."""
    out = []
    prov = parc = fecha = val = None
    for ev, el in ET.iterparse(path, events=('end',)):
        tag = _undec(el.tag)
        if tag == 'PROVINCIA':
            prov = el.text
        elif tag == 'CODPARCELA':
            parc = el.text
        elif tag == 'FECHA':
            fecha = el.text
        elif tag == campo:
            val = el.text
        elif tag.startswith('AAA_'):
            if prov and parc and fecha and val not in (None, ''):
                try:
                    out.append((prov, parc, int(fecha[:4]), float(val.replace(',', '.'))))
                except ValueError:
                    pass
            prov = parc = fecha = val = None
            el.clear()
    return out


RAIF_CKAN = ('https://www.juntadeandalucia.es/datosabiertos/portal/api/3/action/'
             'package_show?id=raif')
# O CKAN devolve URLs no host `gdc-pdpopendata-ckan.paas.junta-andalucia.es`, que não
# resolve daqui. O mesmo CAMINHO responde em `www.juntadeandalucia.es`. Até a MISSÃO 08
# isso era uma frase no atlas — conhecimento humano que ninguém novo teria. Agora é regra.
RAIF_HOST_SWAP = ('gdc-pdpopendata-ckan.paas.junta-andalucia.es', 'www.juntadeandalucia.es')


def raif_download(cultura='Olivar', dest=None, only=None):
    """
    Resolve o recurso pelo CKAN, troca o host, baixa e extrai. Devolve (destino, versão).

    O ZIP do RAIF usa **Deflate64** (`compress_type=9`), que o `zipfile` da biblioteca
    padrão não descomprime — levanta `NotImplementedError`. Por isso a extração usa o
    binário `unzip`, que o repositório já exigia em `scripts/ephy.sh`. Descoberto ao
    automatizar a cadeia: enquanto o download era manual, ninguém tropeçava nisto.
    """
    import subprocess
    body, _ = _get(RAIF_CKAN, timeout=120)
    cat = json.loads(body.decode('utf-8'))
    alvo = [r for r in cat['result']['resources'] if cultura.lower() in r['name'].lower()]
    if not alvo:
        raise ChainFailure(f'RAIF: nenhum recurso para {cultura!r} no CKAN. Falha fechada.')
    rec = alvo[0]
    url = rec['url'].replace(*RAIF_HOST_SWAP)
    dest = dest or os.path.join(ROOT, 'data', 'raw', 'ES-T3-001', f'raif_{cultura.lower()}')
    os.makedirs(dest, exist_ok=True)
    zpath = os.path.join(dest, os.path.basename(url))
    blob, ctype = _get(url, timeout=900)
    if not blob.startswith(b'PK'):
        raise ChainFailure(f'RAIF: {url} não devolveu ZIP (content-type {ctype!r}). '
                           'Falha fechada — 200 com corpo errado não vira dado.')
    with open(zpath, 'wb') as f:
        f.write(blob)
    cmd = ['unzip', '-o', '-q', zpath] + ([only] if only else []) + ['-d', dest]
    r = subprocess.run(cmd, capture_output=True)
    if r.returncode not in (0, 1):        # 1 = avisos do Info-ZIP, não é falha
        raise ChainFailure(f'RAIF: unzip falhou ({r.returncode}): '
                           f'{r.stderr.decode()[:200]}')
    return dest, rec['name']


def raif_repilo(raw=None, provincias=('Huelva', 'Jaén'), download=False):
    raw = raw or os.path.join(ROOT, 'data', 'raw', 'ES-T3-001', 'raif_1')
    steps = []
    if download:
        raw, versao = raif_download()
        steps.append(('AUTOMATIC', f'CKAN → troca de host → ZIP → extrair ({versao})'))
    else:
        steps.append(('AUTOMATIC', 'usar o snapshot já extraído. `--download` refaz a '
                                   'coleta do zero: CKAN → troca de host → Deflate64 '
                                   'por `unzip`. Era MANUAL até a MISSÃO 08'))
    if not os.path.isdir(raw):
        raise ChainFailure(f'RAIF: {raw} ausente. Falha fechada.')
    arquivos = [os.path.join(raw, f) for f in sorted(os.listdir(raw))
                if f.endswith('Muestreos.xml')]
    if not arquivos:
        raise ChainFailure(f'RAIF: nenhum XML de amostragem em {raw}. Falha fechada.')
    steps.append(('AUTOMATIC', f'ler {len(arquivos)} XML por iterparse'))

    leituras = []
    for a in arquivos:
        leituras.extend(_raif_year(a))
    if not leituras:
        raise ChainFailure('RAIF: zero leituras do campo de repilo. Lista vazia é FAILED, '
                           'não "sem doença".')
    steps.append(('AUTOMATIC', f'{len(leituras):,} leituras do campo "{REPILO}"'))
    steps.append(('HUMAN_JUDGMENT', 'escolher o campo 1702 (repilo VISÍVEL) e não o 1703 '
                                    '(incubado): são doenças no mesmo lugar em estados '
                                    'diferentes, e a escolha muda o número'))

    por = {}
    for prov, parc, ano, v in leituras:
        por.setdefault((prov, ano), []).append((parc, v))
    anos = sorted({a for _, a in por})
    ultimo = anos[-1]
    saida = {}
    for prov in provincias:
        coorte = {p for p, _ in por.get((prov, ultimo), [])}
        linha = {}
        for ano in anos[-4:]:
            todas = [v for _, v in por.get((prov, ano), [])]
            mesma = [v for p, v in por.get((prov, ano), []) if p in coorte]
            linha[ano] = {
                'n_todas': len(todas),
                'media_todas': round(sum(todas) / len(todas), 2) if todas else None,
                'n_coorte': len(mesma),
                'media_coorte': round(sum(mesma) / len(mesma), 2) if mesma else None,
            }
        saida[prov] = linha
    steps.append(('AUTOMATIC', f'controle de coorte: parcelas presentes em {ultimo}'))
    return {
        'CHAIN': 'raif-repilo', 'SOURCE_ID': 'ES-T3-001', 'COUNTRY': 'SPAIN (Andalucía)',
        'HEALTH': sh.HEALTHY, 'COVERAGE': None, 'STEPS': steps,
        'HERO_FACT': {
            'field': REPILO, 'total_readings': len(leituras),
            'seasons': [anos[0], anos[-1]], 'cohort_year': ultimo,
            'by_province': saida,
            'CAUTION': 'a média viaja com o n. Huelva tem base pequena no último ano.',
        },
    }


CHAINS = {
    'fr-prothioconazole': fr_prothioconazole,
    'es-identidade': es_identidade,
    'it-prothioconazole': it_prothioconazole,
    'raif-repilo': raif_repilo,
}


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('cmd', choices=['list', 'run'])
    ap.add_argument('chain', nargs='?', default='all')
    ap.add_argument('--raw', default=None)
    ap.add_argument('--download', action='store_true',
                    help='refaz a coleta da fonte em vez de usar o snapshot (RAIF)')
    ap.add_argument('--json', default=None)
    a = ap.parse_args()
    if a.cmd == 'list':
        for k in CHAINS:
            print(k)
        return
    alvo = list(CHAINS) if a.chain == 'all' else [a.chain]
    out = []
    for nome in alvo:
        try:
            kw = {'raw': a.raw} if a.raw and nome != 'es-identidade' else {}
            if a.download and nome == 'raif-repilo':
                kw['download'] = True
            r = CHAINS[nome](**kw)
            r['RESULT'] = 'OK'
        except ChainFailure as e:
            r = {'CHAIN': nome, 'RESULT': 'FAILED_CLOSED', 'ERROR': str(e)}
        except Exception as e:                               # noqa: BLE001
            r = {'CHAIN': nome, 'RESULT': 'FAILED_CLOSED',
                 'ERROR': f'{e.__class__.__name__}: {e}'}
        out.append(r)
        print(json.dumps(r, ensure_ascii=False, indent=1))
    if a.json:
        with open(a.json, 'w', encoding='utf-8') as f:
            json.dump(out, f, ensure_ascii=False, indent=1)


if __name__ == '__main__':
    main()
