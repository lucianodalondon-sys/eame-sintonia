#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BAIXA OS 163 RÓTULOS AUTORIZADOS do Ministero della Salute e preserva o PDF cru.

    python3 scripts/rotulos_baixar.py

POR QUE ISTO EXISTE
--------------------
O pacote de entrega declara `LABEL_COVERAGE: 163/163 (100%)`. Esse número conta
**rótulo baixado**, não **uso lido**. A cobertura de uso lido é 19 de 163 — 11,7% — e
é a limitação mais cara do projeto, porque alimenta o pior erro possível do sistema:

    AFIRMAR QUE O CLIENTE NÃO TEM PRODUTO PARA UM ALVO QUANDO ELE TEM.

(Lição paga pelo Portal Sintonia Brasil: o Nimitz EC tinha 3 culturas no catálogo e 19
no registro.)

A PORTA ESTAVA ABERTA O TEMPO TODO
-----------------------------------
O `curl` 8 recusa a resposta do servlet com `Header without colon` e devolve 0 bytes,
mesmo com HTTP 200. O servidor manda um cabeçalho malformado; o curl é estrito, o
`urllib` é tolerante. O mesmo pedido, pelo `urllib`, devolve 222 KB de PDF real.

    FERRAMENTA QUE RECUSA ≠ PORTA FECHADA.

É a mesma família da lei do IP: `FONTE BLOQUEADA POR IP ≠ FONTE INEXISTENTE`. Aqui o
obstáculo não era a fonte nem a rota — era o nosso cliente HTTP.

O QUE ESTE SCRIPT NÃO FAZ
--------------------------
Não interpreta. Só busca, confere a assinatura `%PDF`, grava o cru e registra o que
aconteceu com cada um. A leitura é do `rotulos_ler.py`, e ela lê SEMPRE do arquivo
gravado — nunca da rede — para que a leitura seja reproduzível sem repetir a coleta.
"""
import hashlib
import json
import os
import time
import urllib.error
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PRODUTOS = os.path.join(ROOT, 'build', 'SINTONIA-ITALY-PILOT-REALITY-HANDOFF',
                        '01-DESIGN-READY', 'ADAMA', 'adama-italy-products.json')
CRUS = os.path.join(ROOT, 'data', 'raw', 'IT-ROTULOS')
MANIFESTO = os.path.join(CRUS, '_MANIFESTO.json')

UA = ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
      '(KHTML, like Gecko) Chrome/128.0 Safari/537.36')
PAUSA = 1.2   # o Ministero é um serviço público; não se bate na porta sem intervalo


def baixar(url):
    """→ (bytes, estado). Nunca levanta: o erro vira estado declarado."""
    req = urllib.request.Request(url, headers={
        'User-Agent': UA,
        'Accept': 'application/pdf,application/octet-stream,*/*',
        'Referer': 'https://www.fitosanitari.salute.gov.it/',
    })
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            b = r.read()
    except urllib.error.HTTPError as e:
        return b'', 'HTTP_%d' % e.code
    except Exception as e:
        return b'', 'ERRO_%s' % type(e).__name__
    if not b:
        return b'', 'VAZIO'
    if b[:4] != b'%PDF':
        # HTML de erro devolvido com 200 é a armadilha clássica deste tipo de servlet
        return b, 'NAO_E_PDF'
    return b, 'OK'


def main():
    produtos = json.load(open(PRODUTOS, encoding='utf-8'))['PRODUCTS']
    os.makedirs(CRUS, exist_ok=True)

    ja = {}
    if os.path.exists(MANIFESTO):
        ja = {r['REGISTRATION_ID']: r for r in json.load(
            open(MANIFESTO, encoding='utf-8'))['ITENS'] if r['ESTADO'] == 'OK'}

    itens, contagem = [], {}
    for i, p in enumerate(produtos, 1):
        reg = p.get('REGISTRATION_ID') or 'SEM-REG-%03d' % i
        url = p.get('LABEL_URL')
        nome = '%s.pdf' % reg
        destino = os.path.join(CRUS, nome)

        if reg in ja and os.path.exists(destino):
            itens.append(ja[reg])
            contagem['JA_TINHA'] = contagem.get('JA_TINHA', 0) + 1
            continue
        if not url:
            itens.append({'REGISTRATION_ID': reg, 'PRODUCT': p.get('PRODUCT'),
                          'ESTADO': 'SEM_URL', 'URL': None})
            contagem['SEM_URL'] = contagem.get('SEM_URL', 0) + 1
            continue

        b, estado = baixar(url)
        if estado == 'OK':
            open(destino, 'wb').write(b)
        itens.append({
            'REGISTRATION_ID': reg,
            'PRODUCT': p.get('PRODUCT'),
            'PRODUCT_ID': p.get('ID'),
            'URL': url,
            'ESTADO': estado,
            'BYTES': len(b),
            'SHA256': hashlib.sha256(b).hexdigest() if estado == 'OK' else None,
            'ARQUIVO': nome if estado == 'OK' else None,
            'BAIXADO_EM': time.strftime('%Y-%m-%dT%H:%M:%S'),
        })
        contagem[estado] = contagem.get(estado, 0) + 1
        print('  %3d/%d  %-10s %-8s %8d b  %s' % (
            i, len(produtos), reg, estado, len(b), (p.get('PRODUCT') or '')[:34]),
            flush=True)
        time.sleep(PAUSA)

    json.dump({
        'DATASET': 'IT-ROTULOS-CRUS',
        'O_QUE_E': 'PDF cru do rotulo autorizado, como o Ministero entrega',
        'FONTE': 'https://www.fitosanitari.salute.gov.it/ · EtichettaServlet',
        'PORTA': 'urllib (o curl 8 recusa o cabecalho malformado do servlet)',
        'LEI': 'FERRAMENTA QUE RECUSA NAO E PORTA FECHADA',
        'O_QUE_ISTO_NAO_E': 'nao e uso lido. E o documento bruto. A leitura e do '
                            'rotulos_ler.py, e le SEMPRE deste arquivo, nunca da rede.',
        'CAPTURADO_EM': time.strftime('%Y-%m-%dT%H:%M:%S'),
        'TOTAL': len(itens),
        'POR_ESTADO': contagem,
        'ITENS': itens,
    }, open(MANIFESTO, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

    print()
    print('por estado:', contagem)
    print('manifesto:', os.path.relpath(MANIFESTO, ROOT))


if __name__ == '__main__':
    main()
