#!/usr/bin/env python3
"""
COLETOR ADAMA ITÁLIA — para rodar numa MÁQUINA RESIDENCIAL, não neste ambiente.

POR QUE ESTE ARQUIVO EXISTE
`adama.com` responde **403 (WAF de origem)** a este datacenter, inclusive em
`/robots.txt`. Medido três vezes, em rodadas diferentes, por duas rotas de saída. E não é
específico da ADAMA: `syngenta.it`, `cropscience.bayer.it` e `omnitrattore.it` respondem o
mesmo. É a **classe** de sites do agronegócio que bloqueia IP de datacenter — o que
transforma a lacuna comercial de "problema da ADAMA" em característica estrutural do
setor.

O QUE ESTE SCRIPT É E O QUE ELE NÃO É
É um cliente HTTP comum, com pausa entre requisições, que roda de uma conexão residencial
— a mesma porta que qualquer pessoa usa ao abrir o site no navegador.

NÃO faz, e não deve ser modificado para fazer:
  · exportar ou reutilizar cookies de sessão de alguém;
  · falsificar credencial ou burlar autenticação;
  · rotacionar IP, usar proxy residencial pago ou qualquer técnica de evasão de WAF;
  · ignorar `robots.txt` — o script LÊ e RESPEITA o arquivo, e para se ele proibir.

Se o site continuar bloqueando mesmo de casa, a resposta certa é
`ADAMA_COMMERCIAL_SITE = BLOCKED`, não uma técnica mais agressiva.

COMO RODAR
    python3 coletar_adama_italia.py --saida ./adama-it-raw
    # depois, traga de volta APENAS a pasta gerada; ela já vem com hash por arquivo

O que volta é `RAW` — HTML e PDF como saíram da fonte, mais um manifesto com SHA-256.
A normalização acontece no repositório, não aqui: `RAW → NORMALIZED → ANALYTICAL`, e o
bruto é escrito primeiro, sempre.
"""
import argparse
import datetime
import hashlib
import json
import os
import re
import time
import urllib.parse
import urllib.request

BASE = 'https://www.adama.com'
INICIO = ['/italia/it', '/italia/it/prodotti', '/italia/it/colture']
UA = ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 '
      '(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36')
PAUSA = 2.5          # segundos entre requisições. Não reduzir.
MAX_PAGINAS = 400


def pedir(url, timeout=45):
    req = urllib.request.Request(url, headers={
        'User-Agent': UA,
        'Accept': 'text/html,application/xhtml+xml,application/pdf;q=0.9,*/*;q=0.8',
        'Accept-Language': 'it-IT,it;q=0.9,en;q=0.6',
    })
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.status, r.read(), dict(r.headers)


def robots_permite(caminho='/italia/it'):
    """Lê robots.txt e obedece. Bloqueio explícito encerra a coleta."""
    try:
        _, corpo, _ = pedir(BASE + '/robots.txt')
    except Exception as e:                                     # noqa: BLE001
        return None, 'robots.txt não lido: %s' % str(e)[:80]
    txt = corpo.decode('utf-8', 'replace')
    regras, aplica = [], False
    for linha in txt.splitlines():
        l = linha.strip().lower()
        if l.startswith('user-agent:'):
            aplica = l.split(':', 1)[1].strip() in ('*',)
        elif aplica and l.startswith('disallow:'):
            regras.append(l.split(':', 1)[1].strip())
    for r in regras:
        if r and caminho.startswith(r):
            return False, 'robots.txt proíbe %s' % r
    return True, 'robots.txt lido; %d regras Disallow para *' % len(regras)


def links(html, atual):
    out = set()
    for m in re.finditer(r'href="([^"#?]+)', html):
        u = urllib.parse.urljoin(atual, m.group(1))
        if u.startswith(BASE) and '/italia/it' in u:
            out.add(u.split('#')[0])
    return out


def coletar(saida):
    os.makedirs(saida, exist_ok=True)
    os.makedirs(os.path.join(saida, 'raw'), exist_ok=True)
    ok, motivo = robots_permite()
    manifesto = {
        'COUNTRY': 'IT', 'SOURCE_ID': 'IT-T9-001',
        'SOURCE': 'ADAMA Italia — site comercial público',
        'CAPTURED_AT': datetime.date.today().isoformat(),
        'COLLECTED_FROM': 'máquina residencial (handoff)',
        'ROBOTS_CHECK': {'ALLOWED': ok, 'REASON': motivo},
        'EVIDENCE_CLASS': 'MANUFACTURER_PUBLIC_CONTENT',
        'PAGES': [], 'ERRORS': [],
    }
    if ok is False:
        manifesto['STATE'] = 'STOPPED_BY_ROBOTS'
        json.dump(manifesto, open(os.path.join(saida, 'MANIFEST.json'), 'w',
                                  encoding='utf-8'), ensure_ascii=False, indent=2)
        print('PARADO por robots.txt:', motivo)
        return manifesto

    fila = [BASE + p for p in INICIO]
    vistos = set()
    while fila and len(vistos) < MAX_PAGINAS:
        u = fila.pop(0)
        if u in vistos:
            continue
        vistos.add(u)
        try:
            st, corpo, hdr = pedir(u)
        except Exception as e:                                 # noqa: BLE001
            manifesto['ERRORS'].append({'URL': u, 'ERROR': str(e)[:160]})
            time.sleep(PAUSA)
            continue
        nome = re.sub(r'[^A-Za-z0-9._-]', '_', u.replace(BASE, '').strip('/')) or 'index'
        ct = (hdr.get('Content-Type') or '').split(';')[0]
        ext = '.pdf' if 'pdf' in ct else '.html'
        caminho = os.path.join(saida, 'raw', nome[:120] + ext)
        with open(caminho, 'wb') as fh:
            fh.write(corpo)
        manifesto['PAGES'].append({
            'URL': u, 'HTTP': st, 'CONTENT_TYPE': ct, 'BYTES': len(corpo),
            'SHA256': hashlib.sha256(corpo).hexdigest(),
            'FILE': os.path.relpath(caminho, saida),
            'CAPTURED_AT': datetime.datetime.utcnow().replace(microsecond=0).isoformat() + 'Z',
        })
        if ext == '.html':
            html = corpo.decode('utf-8', 'replace')
            for l in links(html, u):
                if l not in vistos:
                    fila.append(l)
        print('%3d  %s  %s' % (st, str(len(corpo)).rjust(8), u[:96]), flush=True)
        time.sleep(PAUSA)

    manifesto['STATE'] = 'COLLECTED'
    manifesto['PAGES_TOTAL'] = len(manifesto['PAGES'])
    manifesto['ERRORS_TOTAL'] = len(manifesto['ERRORS'])
    json.dump(manifesto, open(os.path.join(saida, 'MANIFEST.json'), 'w', encoding='utf-8'),
              ensure_ascii=False, indent=2)
    print('\npáginas %d · erros %d · manifesto em %s/MANIFEST.json'
          % (len(manifesto['PAGES']), len(manifesto['ERRORS']), saida))
    return manifesto


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--saida', default='./adama-it-raw')
    coletar(ap.parse_args().saida)
