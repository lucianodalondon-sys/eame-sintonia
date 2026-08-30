#!/usr/bin/env python3
"""
ITÁLIA — rota da ETICHETTA oficial, e o que ela derruba.

O Atlas registrava, sobre `IT-T4-001`:

    "este arquivo não traz cultura nem alvo (...) Portanto a Itália **não** sustenta
     hoje o mesmo cruzamento cultura × alvo que a França sustenta."

A primeira metade continua verdadeira: o CSV aberto não traz cultura nem alvo. A segunda
metade estava errada, e este arquivo é a medição que a corrige. O rótulo autorizado —
a *etichetta* — é publicado pelo mesmo Ministério, por produto, e traz a tabela
`Coltura × Patogeno × Dose × Intervallo × N° max applicazioni`.

O dado existia. O que faltava era a rota. A rota é esta:

    POST FitosanitariServlet  ACTION=cercaProdotti  NUMERO_REGISTRAZIONE=<reg>
      → HTML de resultado contém  EtichettaServlet?id=<ID_INTERNO>
        → GET EtichettaServlet?id=<ID_INTERNO>  → PDF

TRÊS COISAS QUE CUSTARAM MEDIÇÃO E NÃO PODEM SER ESQUECIDAS

1. **`ID_INTERNO ≠ NUMERO_REGISTRAZIONE`.** O rótulo do registro 015232 vive em
   `id=38654`. O id interno não é derivável do número de registro: tem de ser lido do
   HTML de resultado. Adivinhar id é inventar documento.

2. **O host serve a cadeia TLS incompleta.** `www.fitosanitari.salute.gov.it` envia só a
   folha, sem o intermediário `TI Trust Technologies OV CA`. `curl` recusa, e recusa com
   razão. A correção NÃO é desligar verificação: é buscar o intermediário no próprio
   campo AIA do certificado e completar a cadeia. Continua-se verificando.

3. **O host emite um cabeçalho `Public-Key-Pins` malformado** (linha partida, sem `:`).
   `curl` aborta com "Header without colon"; o parser do Python tolera. Por isso a rota
   é Python, e não `curl` — a escolha é medida, não estética.

Nada disso é motivo para marcar a fonte como morta. É a ficha de saúde da fonte, e ela
entra no Atlas. `HTTP 200 ≠ FONTE VIVA`, e o inverso também vale: **falha de leitura de
uma ferramenta não é ausência do dado.**

O QUE O RÓTULO É, E O QUE NÃO É

O rótulo é `REGULATORY_FACT`: é o uso autorizado. Não é venda, não é recomendação
agronômica, não é disponibilidade comercial. `REGISTRATION ≠ COMMERCIAL AVAILABILITY`
continua valendo inteira depois desta rota.

PDF pesado NÃO é versionado. Fica em `data/raw/IT/etichette/` (ignorado pelo git);
o que se versiona é o manifesto com hash, tamanho, data e caminho.
"""
import datetime
import hashlib
import json
import os
import re
import ssl
import subprocess
import sys
import time
import urllib.parse
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

BASE = 'https://www.fitosanitari.salute.gov.it/fitosanitariws_new/'
SERVLET = BASE + 'FitosanitariServlet'
ETICHETTA = BASE + 'EtichettaServlet?id=%s'
HOST = 'www.fitosanitari.salute.gov.it'

PDF_DIR = os.path.join(ROOT, 'data', 'raw', 'IT', 'etichette')
BUNDLE = os.path.join(ROOT, 'data', 'raw', 'IT', 'chain-bundle.pem')

# Convenção de Storage reservada (IT/<source>/<run>/<asset>). Sem credencial neste
# ambiente, o caminho é declarado e o arquivo fica local — declarar é obrigatório,
# fingir persistência não é opção.
STORAGE_CONVENTION = 'IT/IT-T4-001/%s/etichette/%s'


def construir_cadeia(destino=BUNDLE):
    """Completa a cadeia TLS que o servidor não envia, sem afrouxar verificação.

    Lê o intermediário do campo AIA do próprio certificado da folha. Se o AIA sumir ou
    o intermediário não baixar, isto FALHA — e falhar é o comportamento correto.
    """
    os.makedirs(os.path.dirname(destino), exist_ok=True)
    proxy = os.environ.get('HTTPS_PROXY') or os.environ.get('https_proxy') or ''
    proxy_hostport = proxy.split('//')[-1].rstrip('/')
    cmd = ['openssl', 's_client']
    if proxy_hostport:
        cmd += ['-proxy', proxy_hostport]
    cmd += ['-connect', '%s:443' % HOST, '-servername', HOST]
    leaf = subprocess.run(cmd, input='', capture_output=True, text=True, timeout=90).stdout
    pem = subprocess.run(['openssl', 'x509'], input=leaf, capture_output=True,
                         text=True, timeout=30).stdout
    txt = subprocess.run(['openssl', 'x509', '-noout', '-text'], input=pem,
                         capture_output=True, text=True, timeout=30).stdout
    m = re.search(r'CA Issuers - URI:(\S+)', txt)
    if not m:
        raise RuntimeError('AIA ausente no certificado: não há como completar a cadeia')
    der = urllib.request.urlopen(m.group(1), timeout=60).read()
    inter = subprocess.run(['openssl', 'x509', '-inform', 'DER'], input=der,
                           capture_output=True, timeout=30).stdout.decode()
    base = os.environ.get('CURL_CA_BUNDLE', '/etc/ssl/certs/ca-certificates.crt')
    with open(destino, 'w') as fh:
        fh.write(open(base).read())
        fh.write('\n')
        fh.write(inter)
    return destino, m.group(1)


def abrir(bundle):
    ctx = ssl.create_default_context(cafile=bundle)
    op = urllib.request.build_opener(urllib.request.HTTPSHandler(context=ctx),
                                     urllib.request.HTTPCookieProcessor())
    op.addheaders = [('User-Agent', 'Mozilla/5.0 (compatible; SINTONIA-EAME/IT research)')]
    op.open(SERVLET, timeout=60).read()   # cria a sessão (JSESSIONID)
    return op


CAMPOS = ['FROM', 'TO', 'PROVENIENZA', 'NOME', 'NOME_SOSTANZA', 'NUMERO_REGISTRAZIONE',
          'ATTIVITA', 'INDICAZIONE_PERICOLO', 'STATO_AMMINISTRATIVO',
          'DT_IN_REGISTRAZIONE', 'DT_FN_REGISTRAZIONE', 'DT_IN_SCADENZA',
          'DT_FN_SCADENZA', 'PRODOTTO_IP', 'PRODOTTO_PPO', 'PRODOTTO_PFnPE']


def buscar_id_etichetta(op, num_registrazione):
    """Devolve (id_interno, id_ditta) ou (None, None). None é 'não achei', não 'não existe'."""
    d = {k: '' for k in CAMPOS}
    d.update({'ACTION': 'cercaProdotti', 'FROM': '0', 'TO': '49',
              'PROVENIENZA': 'RICERCA', 'NUMERO_REGISTRAZIONE': num_registrazione})
    r = op.open(SERVLET, data=urllib.parse.urlencode(d).encode(), timeout=90)
    h = r.read().decode('iso-8859-1')
    m = re.search(r'EtichettaServlet\?id=(\d+)', h)
    dt = re.search(r'ACTION=cercaDitta&IDD=(\d+)', h)
    return (m.group(1) if m else None), (dt.group(1) if dt else None)


def baixar_etichetta(op, id_interno):
    """Devolve (bytes, filename_declarado). O filename traz a DATA do rótulo."""
    r = op.open(ETICHETTA % id_interno, timeout=120)
    b = r.read()
    disp = r.headers.get('Content-Disposition') or ''
    m = re.search(r'filename=([^;\s]+)', disp)
    return b, (m.group(1) if m else None)


def data_do_nome(filename):
    """`15232_etichettaCLP_29042022.pdf` → 2022-04-29. Sem padrão, NÃO SEI."""
    if not filename:
        return None
    m = re.search(r'_(\d{2})(\d{2})(\d{4})\.pdf$', filename, re.I)
    if not m:
        return None
    try:
        return datetime.date(int(m.group(3)), int(m.group(2)), int(m.group(1))).isoformat()
    except ValueError:
        return None


def colher(registros, run_id, pausa=1.2, limite=None):
    """Colhe rótulos. Falha de rede vira registro FAILED, nunca silêncio."""
    bundle, aia = construir_cadeia()
    os.makedirs(PDF_DIR, exist_ok=True)
    out = []
    alvo = registros[:limite] if limite else registros
    for i, reg in enumerate(alvo, 1):
        num = reg['num_registrazione']
        rec = {
            'COUNTRY': 'IT', 'SOURCE_ID': 'IT-T4-001-ETICHETTA', 'RUN_ID': run_id,
            'REGISTRATION_ID': num,
            'PRODUCT': reg.get('denominazione_prodotto'),
            'HOLDER': reg.get('ragione_sociale'),
            'ACTIVE_SUBSTANCE': reg.get('sostanze_attive'),
            'AUTHORIZATION_DATE': reg.get('data_registrazione'),
            'EXPIRY': reg.get('data_scadenza_autorizzazione'),
            'STATUS': reg.get('stato_amministrativo'),
            'CAPTURED_AT': datetime.datetime.utcnow().replace(microsecond=0).isoformat() + 'Z',
        }
        try:
            # SESSÃO NOVA POR CONSULTA — medido: o servlet atende UMA busca por
            # JSESSIONID. Reusar a sessão devolve "nessun risultato" a partir da
            # segunda consulta, e esse vazio é indistinguível de "não existe".
            # Um laço que reusa a sessão publicaria 1 achado e 162 ausências falsas.
            # E RETENTATIVA COM ESPERA: medido que o host estrangula consultas
            # seguidas e devolve resultado VAZIO — não erro HTTP. Vazio de
            # estrangulamento é indistinguível de vazio de inexistência, então a
            # única saída honesta é insistir antes de declarar ausência.
            # `NO_LABEL_LINK` só é publicado depois de esgotadas as tentativas.
            idl = idd = None
            for tentativa, espera in enumerate((0, 4, 9), 1):
                if espera:
                    time.sleep(espera)
                op = abrir(bundle)
                idl, idd = buscar_id_etichetta(op, num)
                if idl:
                    break
            rec['LOOKUP_ATTEMPTS'] = tentativa
            rec['LABEL_INTERNAL_ID'] = idl
            rec['HOLDER_REGISTRY_ID'] = idd
            if not idl:
                rec['STATE'] = 'NO_LABEL_LINK'
                out.append(rec)
                continue
            b, fname = baixar_etichetta(op, idl)
            if not b.startswith(b'%PDF'):
                rec['STATE'] = 'NOT_A_PDF'
                out.append(rec)
                continue
            nome = '%s_%s.pdf' % (num, idl)
            caminho = os.path.join(PDF_DIR, nome)
            with open(caminho, 'wb') as fh:
                fh.write(b)
            rec.update({
                'STATE': 'OK',
                'LABEL_URL': ETICHETTA % idl,
                'LABEL_FILENAME_DECLARED': fname,
                'LABEL_DATE': data_do_nome(fname) or 'NÃO SEI',
                'BYTES': len(b),
                'SHA256': hashlib.sha256(b).hexdigest(),
                'STORAGE_PATH_LOCAL': os.path.relpath(caminho, ROOT),
                'STORAGE_PATH_CONVENTION': STORAGE_CONVENTION % (run_id, nome),
            })
        except Exception as e:                                  # noqa: BLE001
            rec['STATE'] = 'FAILED'
            rec['ERROR'] = '%s: %s' % (type(e).__name__, str(e)[:160])
        out.append(rec)
        if i % 10 == 0:
            print('  ... %d/%d' % (i, len(alvo)), flush=True)
        time.sleep(pausa)
    return out, aia


def main():
    sys.path.insert(0, HERE)
    import italia  # noqa: E402
    csvp = os.path.join(ROOT, 'data', 'raw', 'IT', 'PROD_FTS_6_20260824.csv')
    rows = italia.carregar(csvp)
    alvo = []
    for r in rows:
        escopo, _ = italia.classificar_titular(r)
        if escopo in ('ADAMA_IT_LEGAL_ENTITY', 'ADAMA_GROUP_IT_CORE'):
            if (r.get('stato_amministrativo') or '').strip() not in italia.STATUS_NAO_VIGENTE:
                alvo.append(r)
    limite = None
    for a in sys.argv[1:]:
        if a.startswith('--limite='):
            limite = int(a.split('=')[1])
    run_id = 'IT-ETICHETTE-%s' % datetime.datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')
    print('ALVO: %d registros ADAMA vigentes%s' % (len(alvo), ' (limite %d)' % limite if limite else ''))
    recs, aia = colher(alvo, run_id, limite=limite)
    ok = [r for r in recs if r.get('STATE') == 'OK']
    saida = {
        'RUN_ID': run_id, 'COUNTRY': 'IT', 'SOURCE_ID': 'IT-T4-001-ETICHETTA',
        # Data de captura no nível do manifesto: sem ela a amostra não declara QUANDO
        # foi observada, e há teste que reprova amostra sem esta data.
        'CAPTURED_AT': datetime.date.today().isoformat(),
        'SOURCE_NAME': 'Ministero della Salute — etichetta autorizzata (EtichettaServlet)',
        'ROUTE': 'POST cercaProdotti → EtichettaServlet?id=<ID_INTERNO> → PDF',
        'TLS_NOTE': 'host serve cadeia incompleta; intermediário obtido do AIA: %s' % aia,
        'SOURCE_LOCATION': 'ITALY', 'FACT_LOCATION': 'ITALY', 'ORIGINAL_LANGUAGE': 'IT',
        'EVIDENCE_CLASS': 'REGULATORY_FACT',
        'TARGET_TOTAL': len(alvo),
        'ATTEMPTED': len(recs),
        'LABELS_OBTAINED': len(ok),
        'COVERAGE_PCT': round(100.0 * len(ok) / len(recs), 1) if recs else 0.0,
        'STATE': 'COMPLETE' if len(ok) == len(alvo) else 'PARTIAL',
        'BY_STATE': {s: sum(1 for r in recs if r.get('STATE') == s)
                     for s in sorted({r.get('STATE') for r in recs})},
        'LABELS': recs,
    }
    dest = os.path.join(ROOT, 'data', 'samples', 'IT-T4-001', 'IT-T4-001-etichette-manifest.json')
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    with open(dest, 'w', encoding='utf-8') as fh:
        json.dump(saida, fh, ensure_ascii=False, indent=2)
    print('OBTIDOS %d/%d → %s' % (len(ok), len(alvo), os.path.relpath(dest, ROOT)))


if __name__ == '__main__':
    main()
