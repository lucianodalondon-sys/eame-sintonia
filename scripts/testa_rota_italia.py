#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TESTA A ROTA — o que abre daqui, e o que abriria de um IP italiano.

    python3 scripts/testa_rota_italia.py

Rode UMA VEZ sem VPN e UMA VEZ com VPN italiana. O script grava as duas leituras
e mostra a diferença, fonte por fonte.

POR QUE ISTO EXISTE
--------------------
Três fontes que o projeto precisa não abrem TCP deste IP: ISMEA Mercati, ISTAT
esploradati e ARPAV. As três são donas exatamente do que falta no pacote —
mercado, área/produção por região e clima. Se um IP italiano as abrir, duas
lacunas totais e a maior lacuna parcial caem de uma vez.

    FONTE BLOQUEADA POR IP NÃO É FONTE INEXISTENTE. É PROBLEMA DE ROTA.

O QUE ESTE TESTE NÃO DECIDE
----------------------------
Nem todo obstáculo é geografia, e confundir isso faz perder tempo com VPN onde o
problema é outro:

    TIMEOUT / TCP não abre .... compatível com filtro geográfico → a VPN pode resolver
    DH_KEY_TOO_SMALL ......... chave fraca DO SERVIDOR → a VPN não muda nada
    SSL handshake failure .... TLS do servidor ou SNI → provavelmente não muda
    Akamai / bm-verify ....... detecção de ROBÔ, lê o navegador, não o IP → não muda
                               ⛔ e não se contorna: é limite do projeto, não obstáculo

Por isso cada linha sai com um veredito de CAUSA, não só de sucesso ou falha.
"""
import json
import os
import socket
import ssl
import sys
import time
import urllib.error
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SAIDA = os.path.join(ROOT, 'data', 'samples', 'IT-LASTMILE')
UA = ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
      '(KHTML, like Gecko) Chrome/128.0 Safari/537.36')

# (nome, url, familia da missao que depende dela, o que esperar se abrir)
ALVOS = [
    ('ISMEA Mercati', 'https://www.ismeamercati.it/', '2 · MERCADO',
     'precos por praca e por cultura, a autoridade italiana do setor'),
    ('ISMEA portal', 'https://www.ismea.it/istituzionale', '2 · MERCADO',
     'publicacoes e series'),
    ('ISTAT esploradati', 'https://esploradati.istat.it/', '3 · PESO ECONOMICO',
     'area e producao por cultura e por regiao — o REAL_GAP inteiro'),
    ('ISTAT dati (legado)', 'https://dati.istat.it/', '3 · PESO ECONOMICO',
     'mesma coisa, interface antiga'),
    ('ARPAV Veneto', 'https://www.arpa.veneto.it/', '6 · CLIMA',
     'clima e agrometeorologia do Veneto — o outro REAL_GAP'),
    ('ARPA Lombardia', 'https://www.arpalombardia.it/', '6 · CLIMA', 'clima'),
    ('ARPAE Emilia-Romagna', 'https://www.arpae.it/', '6 · CLIMA', 'clima'),
    ('Regione Veneto · fitosanitario',
     'https://www.regione.veneto.it/web/agricoltura-e-foreste', '1 · FENOLOGIA',
     'boletins do Veneto — 3 casos do demo estao la e nao ha nenhum boletim'),
    ('Regione Sicilia · agricoltura', 'https://www.regione.sicilia.it/', '1 · FENOLOGIA',
     'boletins da Sicilia — o caso da mosca da oliveira'),
    ('Prov. Aut. Bolzano · agricoltura', 'https://www.provinz.bz.it/agricoltura-foreste/',
     '1 · FENOLOGIA', 'maca do Trentino-Alto Adige'),
    ('Ente Nazionale Risi', 'https://www.enterisi.it/', '9 · HERBICIDA / ARROZ',
     'diserbo do arroz — ⚠️ falha por DH fraco, nao por geografia'),
    ('BMTI borse merci', 'https://www.bmti.it/', '2 · MERCADO', 'ja funciona'),
    ('Eurostat API', 'https://ec.europa.eu/eurostat/api/dissemination/statistics/'
     '1.0/data/apro_cpshr?format=JSON&geo=IT', '3 · PESO ECONOMICO', 'ja funciona'),
    ('EC Agri-food Data Portal', 'https://agridata.ec.europa.eu/', '2 · MERCADO',
     'ja funciona'),
    ('Copernicus EDO (seca)', 'https://edo.jrc.ec.europa.eu/', '6 · CLIMA',
     'indice de seca por regiao'),
    ('JRC MARS', 'https://joint-research-centre.ec.europa.eu/'
     'monitoring-agricultural-resources-mars_en', '6 · CLIMA',
     'boletim agrometeorologico da UE'),
]

MARCAS = ['geo_ip_block', 'access denied', 'captcha', 'not available in your',
          'forbidden', 'blocked']


def causa(estado, detalhe):
    """→ (CAUSA, A VPN RESOLVE?). O ponto do script: separar rota de outra coisa."""
    d = (detalhe or '').lower()
    if 'timeout' in estado.lower() or '10060' in d:
        return ('TCP_NAO_ABRE', 'PROVAVEL — compativel com filtro geografico')
    if 'dh_key_too_small' in d:
        return ('TLS_DO_SERVIDOR', 'NAO — chave fraca do servidor, igual em qualquer pais')
    if 'handshake' in d or 'unexpected_eof' in d or 'sslv3' in d:
        return ('TLS_OU_WAF', 'TALVEZ — pode ser servidor velho, nao geografia')
    if 'geo_ip_block' in d:
        return ('BLOQUEIO_GEOGRAFICO_DECLARADO', 'SIM — a fonte diz o motivo')
    if 'bm-verify' in d or 'access denied' in d:
        return ('DETECCAO_DE_ROBO', 'NAO — le o navegador, nao o IP. E nao se contorna.')
    if estado.startswith('HTTP 2'):
        return ('ABERTO', 'desnecessario')
    if estado.startswith('HTTP 4') or estado.startswith('HTTP 5'):
        return ('RESPONDE_MAS_RECUSA', 'TALVEZ — depende do motivo')
    return ('NAO_SEI', 'NAO SEI')


def testa(url):
    t0 = time.time()
    req = urllib.request.Request(url, headers={'User-Agent': UA,
                                               'Accept-Language': 'it-IT,it;q=0.9'})
    try:
        with urllib.request.urlopen(req, timeout=25) as r:
            b = r.read(4000)
            estado = 'HTTP %d' % r.status
            low = b.decode('utf-8', errors='replace').lower()
            marca = next((m for m in MARCAS if m in low), None)
            det = ('marca no corpo: %s' % marca) if marca else '%d bytes' % len(b)
    except urllib.error.HTTPError as e:
        estado, det = 'HTTP %d' % e.code, str(e.reason)
    except socket.timeout:
        estado, det = 'TIMEOUT', 'TCP nao abriu em 25s'
    except Exception as e:
        estado, det = type(e).__name__, str(e)[:110]
    return estado, det, round(time.time() - t0, 1)


def main():
    rotulo = sys.argv[1] if len(sys.argv) > 1 else 'SEM_VPN'
    os.makedirs(SAIDA, exist_ok=True)
    linhas = []
    print('rodada: %s\n' % rotulo)
    print('%-32s %-9s %-24s %s' % ('FONTE', 'ESTADO', 'CAUSA', 'VPN RESOLVE?'))
    print('-' * 104)
    for nome, url, fam, esperado in ALVOS:
        est, det, seg = testa(url)
        c, v = causa(est, det)
        linhas.append({'FONTE': nome, 'URL': url, 'FAMILIA_DA_MISSAO': fam,
                       'O_QUE_TRAZ_SE_ABRIR': esperado, 'ESTADO': est,
                       'DETALHE': det, 'SEGUNDOS': seg, 'CAUSA': c,
                       'VPN_RESOLVE': v})
        print('%-32s %-9s %-24s %s' % (nome[:32], est, c, v))

    destino = os.path.join(SAIDA, 'IT-ROTA-%s.json' % rotulo)
    json.dump({
        'DATASET': 'IT-TESTE-DE-ROTA',
        'RODADA': rotulo,
        'QUANDO': time.strftime('%Y-%m-%dT%H:%M:%S'),
        'LEI': 'FONTE BLOQUEADA POR IP NAO E FONTE INEXISTENTE. E PROBLEMA DE ROTA.',
        'O_QUE_A_VPN_NAO_MUDA': [
            'deteccao de robo (Akamai/bm-verify) — le o navegador, nao o IP',
            'TLS fraco do servidor (DH_KEY_TOO_SMALL)',
            'qualquer coisa que exija login, licenca ou chave paga',
            'os termos de uso da fonte',
        ],
        'ITENS': linhas,
    }, open(destino, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('\ngravado:', os.path.relpath(destino, ROOT))

    # comparação automática quando as duas rodadas existirem
    outro = os.path.join(SAIDA, 'IT-ROTA-%s.json'
                         % ('SEM_VPN' if rotulo != 'SEM_VPN' else 'COM_VPN_IT'))
    if os.path.exists(outro):
        base = {x['FONTE']: x for x in json.load(open(outro, encoding='utf-8'))['ITENS']}
        print('\n%-32s %-14s %-14s %s' % ('FONTE', rotulo, os.path.basename(outro)[8:-5],
                                          'MUDOU?'))
        print('-' * 88)
        for x in linhas:
            b = base.get(x['FONTE'])
            if not b:
                continue
            mudou = 'SIM' if x['ESTADO'] != b['ESTADO'] else '—'
            print('%-32s %-14s %-14s %s' % (x['FONTE'][:32], x['ESTADO'],
                                            b['ESTADO'], mudou))


if __name__ == '__main__':
    main()
