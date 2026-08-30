#!/usr/bin/env python3
"""
Preserva a perna FIELD do IT-CASE-DURUM-FUSARIUM-001 de forma auditável.

O caso ficou em `CONVERGENCE_PARTIAL` por um defeito que eu declarei contra mim mesmo:
a perna do rótulo estava gravada com hash, a perna de campo não. Eu tinha lido o boletim
do LaMMA numa página **rolante** e não o gravei — testemunho de leitura, não evidência
re-verificável.

O QUE A RECUPERAÇÃO ACHOU
--------------------------
A página **ainda carrega a edição de 2026-04-23**. A série de frumento é sazonal: acabada
a colheita, a última edição fica exposta. Ou seja, a rota não mudou e o documento é
recuperável — não foi preciso reconstruir nada, o que seria proibido.

Duas coletas separadas devolveram **o mesmo byte** (`sha256 93527b54…`, 25.680 bytes),
então a captura é determinística e o `PRESERVED = YES` é conferível: qualquer um refaz o
download e recalcula.

Não há PDF do boletim de frumento. Os dois PDFs linkados na página são fichas de
*peronospora* e *oidio* da videira — documentos diferentes. O original é o HTML, e é o
HTML que se preserva, inteiro, sem substituir por resumo.

O QUE A PRESERVAÇÃO CORRIGIU NO MEU PRÓPRIO CASO
-------------------------------------------------
Lendo o texto preservado em vez da memória, o caso estava **mais forte num ponto e mais
fraco noutro**, e o ponto fraco é meu:

  · eu escrevi "alto risco de fusariosi" para o grano duro. O texto diz que o risco
    modelado é *"elevato nelle classi precoci e medie del frumento **tenero** nel sud e
    **in alcune situazioni del duro**"*. Alto para o tenero; para o duro, **em algumas
    situações**. A qualificação não é detalhe — é a diferença entre um alerta de cultura
    e um alerta de sub-área.
  · em compensação, o texto traz algo que eu **não** tinha registrado e que é mais forte
    que risco modelado: *"Si segnala la comparsa di **sintomi lievi nel frumento duro**
    in alcune situazioni, mentre il tenero resta esente."* Sintoma **observado** no duro,
    com o tenero isento. Isso é sinal de campo, não saída de modelo.

`SINTOMA OBSERVADO ≠ RISCO MODELADO`, e o boletim declara os dois separadamente. Guardar
os dois separados é o que a preservação compra.
"""
import datetime
import hashlib
import html
import json
import os
import re
import sys
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DIR = os.path.join(ROOT, 'data', 'samples', 'IT-T3-LAMMA')
RAW = os.path.join(DIR, 'grosseto-ftsnt-2026-04-23.html')
MANIF = os.path.join(DIR, 'IT-T3-LAMMA-grosseto-2026-04-23.json')

URL = 'https://www.lamma.toscana.it/previ/ita/agrometeo/html/Grosseto_ftsnt.html'
SOURCE_DATE = '2026-04-23'
UA = 'SintoniaEAME/1.0 (pesquisa de dado publico)'


def baixar():
    req = urllib.request.Request(URL, headers={'User-Agent': UA, 'Accept': 'text/html,*/*'})
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read(), r.headers.get('Content-Type', '')


def texto(b):
    """Texto determinístico a partir dos bytes. Mesma entrada, mesma saída."""
    s = b.decode('utf-8', 'replace')
    s = re.sub(r'<script.*?</script>|<style.*?</style>', ' ', s, flags=re.S | re.I)
    s = html.unescape(re.sub(r'<[^>]+>', ' ', s))
    return re.sub(r'\s+', ' ', s).strip()


def secao_frumento(t):
    """Recorta o boletim de FRUMENTO. A página traz também os de vite, no mesmo HTML."""
    ini = t.find('Bolletino Frumento del %s' % SOURCE_DATE)
    if ini < 0:
        ini = t.find('Bollettino Frumento del %s' % SOURCE_DATE)
    if ini < 0:
        return None
    fim = t.find('Bollettino Vite', ini)
    return t[ini:fim if fim > ini else ini + 3000]


# Cada afirmação do caso tem de sair de um TRECHO do documento preservado, citado.
def sustentacao(sec):
    def acha(pat):
        m = re.search(pat, sec, re.I)
        return m.group(0).strip() if m else None

    fenol = acha(r'il duro si colloca tra [^.]+\.')
    fenol_n = acha(r'il duro è in spigatura[^.;]*')
    sintoma = acha(r'Si segnala la comparsa di sintomi lievi nel frumento duro[^.]*\.')
    risco = acha(r'Il rischio risulta elevato[^.]*\.')
    chuva = acha(r'considerate le piogge e le previsioni di piogge[^,]*')
    trat = acha(r'è opportuno effettuare un trattamento fitosanitario[^.]*\.')
    # A FONTE ESCREVE "Bolletino", com um t so — erro de digitacao dela, na secao de
    # frumento (a de vite escreve "Bollettino"). Um padrao que exigisse a grafia correta
    # devolveria NOT_SUSTAINED para a data de um documento que TRAZ a data. Preservar
    # inclui aceitar a fonte como ela e, sem corrigi-la.
    data = acha(r'Bollet{1,2}ino Frumento del \d{4}-\d{2}-\d{2}')

    return {
        'DATE': {'CLAIM': 'a edição é de %s' % SOURCE_DATE, 'QUOTE_IT': data,
                 'STATE': 'SUSTAINED' if data else 'NOT_SUSTAINED'},
        'CROP': {'CLAIM': 'grano duro é tratado à parte do tenero',
                 'QUOTE_IT': fenol or fenol_n,
                 'STATE': 'SUSTAINED' if (fenol or fenol_n) else 'NOT_SUSTAINED'},
        'ISSUE': {'CLAIM': 'fusariosi, com SINTOMA OBSERVADO no duro',
                  'QUOTE_IT': sintoma,
                  'STATE': 'SUSTAINED' if sintoma else 'NOT_SUSTAINED',
                  'NOTE': 'sintoma observado, não saída de modelo'},
        'PHENOLOGY': {'CLAIM': 'o duro está entrando em fioritura (sul da província)',
                      'QUOTE_IT': fenol,
                      'STATE': 'SUSTAINED' if fenol else 'NOT_SUSTAINED'},
        'RISK': {
            'CLAIM_AS_ORIGINALLY_WRITTEN': 'alto risco de fusariosi para o grano duro',
            'QUOTE_IT': risco,
            'STATE': 'PARTIALLY_SUSTAINED',
            'CORRECTION': (
                'o texto diz que o risco modelado é elevado no frumento TENERO das '
                'classes precoci e medie no sul, e "in alcune situazioni del duro". '
                'Para o duro é EM ALGUMAS SITUAÇÕES, não em toda a cultura. A minha '
                'formulação anterior generalizava.'),
            'LAW': 'SINTOMA OBSERVADO ≠ RISCO MODELADO',
        },
        'RAIN': {'CLAIM': 'chuva ocorrida e prevista entram na recomendação',
                 'QUOTE_IT': chuva,
                 'STATE': 'SUSTAINED' if chuva else 'NOT_SUSTAINED'},
        'TREATMENT_RECOMMENDATION': {
            'CLAIM': 'o boletim recomenda tratamento',
            'QUOTE_IT': trat,
            'STATE': 'SUSTAINED' if trat else 'NOT_SUSTAINED',
            'CONDITIONED_ON': ('"Dove la fase fenologica sta entrando in fioritura" e '
                               '"se non già protette con un trattamento specifico" — a '
                               'recomendação é condicional, não geral'),
            'PRODUCT_SCOPE_IT': ('con uno dei prodotti previsti dai disciplinari di '
                                 'produzione integrata'),
            'WHAT_IT_DOES_NOT_DO': ('não nomeia produto comercial nenhum, nem da ADAMA '
                                    'nem de concorrente'),
        },
    }


def manifesto(b, ct, sec):
    sha = hashlib.sha256(b).hexdigest()
    return {
        'SOURCE_ID': 'IT-T3-LAMMA',
        'source': ('Consorzio LaMMA — Regione Toscana / CNR, bollettino fitosanitario '
                   'provinciale'),
        'SOURCE_LOCATION': 'Toscana, Italia',
        'FACT_LOCATION': 'ITALY — Toscana, provincia di Grosseto',
        'ORIGINAL_LANGUAGE': 'it',
        'EVIDENCE_CLASS': 'PRIMARY_SOURCE_RAW',
        'FOR_CASE': 'IT-CASE-DURUM-FUSARIUM-001',
        'LEG': 'FIELD',
        'ARTIFACT_NAME': os.path.basename(RAW),
        'FILE_NAME': os.path.relpath(RAW, ROOT),
        'MIME': (ct or 'text/html').split(';')[0].strip(),
        'BYTES': len(b),
        'SHA256': sha,
        'SOURCE_URL': URL,
        'SOURCE_DATE': SOURCE_DATE,
        'captured_at': datetime.date.today().isoformat(),
        'CAPTURED_AT': datetime.date.today().isoformat(),
        'PRESERVED': 'YES',
        'WHY_PRESERVED_IS_YES': (
            'os bytes estão no repositório e o hash é reconferível: duas coletas '
            'separadas devolveram o mesmo sha256, e o modo --verify recalcula a partir '
            'do disco e do remoto.'),
        'DETERMINISTIC': True,
        'ORIGINAL_FORMAT_NOTE': (
            'não existe PDF deste boletim. Os dois PDFs linkados na página são fichas de '
            'peronospora e oidio da VIDEIRA — outros documentos. O original é o HTML, '
            'preservado inteiro e não substituído por resumo.'),
        'LOCATOR': {
            'DOCUMENT': 'página provincial de Grosseto (traz frumento E vite no mesmo HTML)',
            'SECTION': 'Provincia di Grosseto - Bolletino Frumento del 2026-04-23',
            'SUBSECTIONS_USED': ['Fenologia', 'Fusariosi'],
            'HOW_TO_REACH': ('recortar do título da seção de frumento até "Bollettino '
                             'Vite" — é o que faz scripts/italia_preservar_lamma.py'),
        },
        'ROUTE_STATE': 'RECOVERED_UNCHANGED',
        'WHY_ROUTE_STILL_WORKS': (
            'a série de frumento é sazonal: encerrada a campanha, a última edição fica '
            'exposta na página rolante. A rota não mudou e nada precisou ser '
            'reconstruído — reconstruir seria proibido.'),
        'CONTENT_SUPPORT': sustentacao(sec),
        'WHAT_THIS_DOES_NOT_PROVE': [
            'que o tratamento tenha sido feito por alguém',
            'nada sobre venda, estoque ou disponibilidade comercial',
            'nada sobre outras províncias ou regiões',
        ],
    }


def verificar():
    """PRESERVED só vale se o byte puder ser reconferido. Disco E remoto."""
    if not (os.path.exists(RAW) and os.path.exists(MANIF)):
        print('AUSENTE — rode sem --verify primeiro'); return 1
    m = json.load(open(MANIF, encoding='utf-8'))
    disco = open(RAW, 'rb').read()
    sd = hashlib.sha256(disco).hexdigest()
    ok_disco = (sd == m['SHA256'] and len(disco) == m['BYTES'])
    print('disco  sha256 %s  bytes %d  -> %s' % (sd, len(disco),
                                                 'OK' if ok_disco else 'DIVERGE'))
    try:
        b, _ = baixar()
        sr = hashlib.sha256(b).hexdigest()
        print('remoto sha256 %s  bytes %d  -> %s' % (sr, len(b),
              'OK' if sr == m['SHA256'] else 'MUDOU NA ORIGEM'))
        ok_rem = sr == m['SHA256']
    except Exception as e:
        print('remoto INDISPONIVEL (%s) — a conferencia de disco continua valendo'
              % type(e).__name__)
        ok_rem = None
    print('CONTENT_SUPPORT:')
    for k, v in m['CONTENT_SUPPORT'].items():
        print('  %-26s %s' % (k, v['STATE']))
    return 0 if ok_disco else 1


def main():
    if '--verify' in sys.argv:
        raise SystemExit(verificar())
    b, ct = baixar()
    t = texto(b)
    sec = secao_frumento(t)
    if not sec:
        print('SOURCE_NOT_RECOVERED — a pagina nao traz mais a edicao de %s' % SOURCE_DATE)
        raise SystemExit(2)
    os.makedirs(DIR, exist_ok=True)
    with open(RAW, 'wb') as fh:
        fh.write(b)
    m = manifesto(b, ct, sec)
    # Recalcula A PARTIR DO DISCO, não da variável em memória: é o que prova a escrita.
    m['SHA256_RECHECKED_FROM_DISK'] = hashlib.sha256(open(RAW, 'rb').read()).hexdigest()
    m['RECHECK_MATCHES'] = m['SHA256_RECHECKED_FROM_DISK'] == m['SHA256']
    with open(MANIF, 'w', encoding='utf-8') as fh:
        json.dump(m, fh, ensure_ascii=False, indent=2)
    print('preservado: %s' % os.path.relpath(RAW, ROOT))
    print('  bytes %d  mime %s  sha256 %s' % (m['BYTES'], m['MIME'], m['SHA256']))
    print('  recheck do disco: %s' % ('OK' if m['RECHECK_MATCHES'] else 'DIVERGE'))
    print('  source_date %s  captured_at %s' % (m['SOURCE_DATE'], m['CAPTURED_AT']))
    for k, v in m['CONTENT_SUPPORT'].items():
        print('  %-26s %s' % (k, v['STATE']))
    print('->', os.path.relpath(MANIF, ROOT))


if __name__ == '__main__':
    main()
