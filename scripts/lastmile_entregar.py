#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MONTA AS QUATRO ENTREGAS DO §12 DA MISSÃO LAST-MILE.

    python3 scripts/lastmile_entregar.py

    LAST-MILE-REALITY-GAPS.md     o relatório, para ler
    LAST-MILE-REALITY-GAPS.json   as lacunas, para máquina
    NEW-REAL-DATA.json            os registros novos, com proveniência
    NEW-REAL-SOURCES.json         as fontes novas, com estado de acesso MEDIDO

Junta quatro origens: o inventário (§11), a coleta das 10 famílias, a coleta pela
rota italiana, e o catálogo comercial colhido à mão pelas páginas de cultura.

⚠️ A CORREÇÃO QUE ESTE MONTADOR TEM DE FAZER, E POR QUÊ
--------------------------------------------------------
O bloco de mercado concluiu que «ISMEA NÃO está bloqueada para o nosso IP», porque
recebeu HTTP 200. A conclusão está errada, e o erro é honesto: **a VPN italiana
estava ligada durante a coleta**, e o agente não sabia disso.

A linha de base, medida ANTES de a VPN subir, está gravada:

    IT-ROTA-SEM_VPN.json      ismeamercati.it  →  timeout, TCP não abre
    IT-ROTA-COM_VPN_IT.json   ismeamercati.it  →  HTTP 200

    UM 200 NÃO DIZ NADA SOBRE A ROTA SE VOCÊ NÃO SABE POR ONDE SAIU.

Deixar passar produziria a pior classe de erro deste projeto: um estado de acesso
falso, que faria a próxima pessoa desistir de ligar a VPN e concluir que a fonte
sumiu. Cada fonte que só a rota italiana abre sai marcada
`EXIGE_ROTA_ITALIANA: true`.
"""
import glob
import json
import os
import re
from collections import Counter, defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TMP = os.path.join(ROOT, '.tmp')
LM = os.path.join(ROOT, 'data', 'samples', 'IT-LASTMILE')
SAIDA = os.path.join(ROOT, 'research', 'italy-lastmile')

# Fontes que a medição provou dependerem da saída italiana.
SO_COM_ROTA_ITALIANA = ['ismeamercati.it', 'ismea.it', 'esploradati.istat.it',
                        'arpa.veneto.it', 'arpav']


def carrega(p, chave=None):
    if not os.path.exists(p):
        return None
    d = json.load(open(p, encoding='utf-8'))
    return d.get(chave) if chave else d


def exige_rota(url):
    u = (url or '').lower()
    return any(s in u for s in SO_COM_ROTA_ITALIANA)


def main():
    os.makedirs(SAIDA, exist_ok=True)
    inv = carrega(os.path.join(LM, 'IT-LASTMILE-INVENTARIO.json'))
    cat = carrega(os.path.join(LM, 'IT-ADAMA-CATALOGO.json'))
    rota_sem = carrega(os.path.join(LM, 'IT-ROTA-SEM_VPN.json'))
    rota_com = carrega(os.path.join(LM, 'IT-ROTA-COM_VPN_IT.json'))

    colheitas = []
    for f in ('lastmile1.json', 'lastmile2.json'):
        d = carrega(os.path.join(TMP, f))
        if d:
            colheitas.append((f, d))

    # ── registros e fontes, de todas as colheitas ─────────────────────────────
    registros, fontes = [], []
    por_bloco = {}
    for arq, d in colheitas:
        for b in d.get('blocos', []):
            nome = b['bloco']
            por_bloco.setdefault(nome, {'REGISTROS': 0, 'FONTES': 0,
                                        'CLASSE': b.get('classe'),
                                        'RESUMO': b.get('resumo'),
                                        'LACUNAS': b.get('lacunas_que_ficaram')
                                        or b.get('lacunas'),
                                        'CONFERENCIA': b.get('verificacao'),
                                        'RECEITA': b.get('receita_para_refazer')})
            for r in b.get('registros', []):
                registros.append(dict(r, BLOCO=nome, ORIGEM_DA_COLETA=arq,
                                      EXIGE_ROTA_ITALIANA=exige_rota(r.get('source_url'))))
                por_bloco[nome]['REGISTROS'] += 1
            for s in b.get('fontes_novas', []) + b.get('endpoints', []):
                url = s.get('url') or s.get('URL')
                fontes.append({
                    'NOME': s.get('nome') or s.get('o_que_serve') or 'NAO_SEI',
                    'URL': url,
                    'O_QUE_PUBLICA': s.get('o_que_publica') or s.get('o_que_serve'),
                    'PERIODICIDADE': s.get('periodicidade'),
                    'ESTADO_DE_ACESSO': s.get('estado_de_acesso') or s.get('estado'),
                    'EVIDENCIA_DO_ESTADO': s.get('evidencia_do_estado'),
                    'FORMATO': s.get('formato'),
                    'BLOCO': nome,
                    'EXIGE_ROTA_ITALIANA': exige_rota(url),
                })
                por_bloco[nome]['FONTES'] += 1

    # dedup de fonte por URL
    vistas, fontes_u = set(), []
    for s in fontes:
        k = (s['URL'] or '').rstrip('/').lower()
        if k and k in vistas:
            continue
        vistas.add(k)
        fontes_u.append(s)

    # ── a correção da rota, com a evidência das duas medições ─────────────────
    correcao_rota = None
    if rota_sem and rota_com:
        antes = {x['FONTE']: x for x in rota_sem['ITENS']}
        mudou = [{'FONTE': x['FONTE'], 'URL': x['URL'],
                  'SEM_VPN': antes[x['FONTE']]['ESTADO'], 'COM_VPN_IT': x['ESTADO'],
                  'FAMILIA': x['FAMILIA_DA_MISSAO'],
                  'O_QUE_TRAZ': x['O_QUE_TRAZ_SE_ABRIR']}
                 for x in rota_com['ITENS']
                 if x['FONTE'] in antes and x['ESTADO'] != antes[x['FONTE']]['ESTADO']]
        correcao_rota = {
            'O_QUE_ACONTECEU':
                'o bloco de mercado concluiu que ISMEA nao estava bloqueada, porque '
                'recebeu HTTP 200. A VPN italiana estava ligada durante a coleta e o '
                'agente nao sabia.',
            'LEI': 'UM 200 NAO DIZ NADA SOBRE A ROTA SE VOCE NAO SABE POR ONDE SAIU',
            'POR_QUE_IMPORTA':
                'um estado de acesso falso faria a proxima pessoa desistir de ligar a '
                'VPN e concluir que a fonte sumiu',
            'MEDIDO_ANTES_E_DEPOIS': mudou,
            'NAO_MUDOU_COM_A_VPN': [x['FONTE'] for x in rota_com['ITENS']
                                    if x['FONTE'] in antes
                                    and x['ESTADO'] == antes[x['FONTE']]['ESTADO']
                                    and not x['ESTADO'].startswith('HTTP 2')],
            'O_QUE_A_VPN_NAO_MUDA': rota_com.get('O_QUE_A_VPN_NAO_MUDA'),
        }

    # ── as lacunas, família por família ───────────────────────────────────────
    lacunas = []
    for f in (inv or {}).get('FAMILIAS', []):
        nome_curto = re.sub(r'^\d+\s*·\s*', '', f['FAMILIA']).split('(')[0].strip()
        chave = next((k for k in por_bloco
                      if k.split('-')[0].lower()[:5] in nome_curto.lower()), None)
        b = por_bloco.get(chave, {})
        lacunas.append({
            'FAMILIA': f['FAMILIA'],
            'CLASSE_NO_INVENTARIO': f['CLASSE'],
            'O_QUE_JA_TINHA': f['TEM'],
            'POR_QUE_ERA_LACUNA': f['POR_QUE'],
            'COLETADO_AGORA': b.get('REGISTROS', 0),
            'FONTES_NOVAS': b.get('FONTES', 0),
            'RESULTADO': b.get('RESUMO'),
            'CONFERENCIA': b.get('CONFERENCIA'),
            'LACUNAS_QUE_FICARAM': b.get('LACUNAS'),
            'RECEITA_PARA_REFAZER': b.get('RECEITA'),
        })

    gaps = {
        'DATASET': 'IT-LAST-MILE-REALITY-GAPS',
        'DATA_DE_REFERENCIA': '2026-09-02',
        'REGRA_DA_MISSAO': 'inventariar antes de coletar; so PARTIAL e REAL_GAP '
                           'autorizam coleta',
        'RESUMO_DO_INVENTARIO': (inv or {}).get('RESUMO'),
        'CORRECAO_DE_ROTA': correcao_rota,
        'FAMILIAS': lacunas,
    }
    novo_dado = {
        'DATASET': 'IT-NEW-REAL-DATA',
        'DATA_DE_REFERENCIA': '2026-09-02',
        'O_QUE_E': 'registros externos publicos coletados nesta missao',
        'SINTETICOS': 0,
        'LEI': 'todo registro carrega source_url e o que NAO prova',
        'COUNT': len(registros),
        'POR_BLOCO': {k: v['REGISTROS'] for k, v in por_bloco.items()},
        'EXIGEM_ROTA_ITALIANA': sum(1 for r in registros if r['EXIGE_ROTA_ITALIANA']),
        'CATALOGO_COMERCIAL': (cat or {}).get('PRODUTOS', []),
        'REGISTROS': registros,
    }
    novas_fontes = {
        'DATASET': 'IT-NEW-REAL-SOURCES',
        'DATA_DE_REFERENCIA': '2026-09-02',
        'LEI': 'estado de acesso MEDIDO, nunca presumido. Fonte bloqueada nao e fonte '
               'inexistente.',
        'COUNT': len(fontes_u),
        'POR_ESTADO': dict(Counter(s['ESTADO_DE_ACESSO'] or 'NAO_DECLARADO'
                                   for s in fontes_u)),
        'EXIGEM_ROTA_ITALIANA': [s for s in fontes_u if s['EXIGE_ROTA_ITALIANA']],
        'FONTES': fontes_u,
    }

    for nome, corpo in (('LAST-MILE-REALITY-GAPS.json', gaps),
                        ('NEW-REAL-DATA.json', novo_dado),
                        ('NEW-REAL-SOURCES.json', novas_fontes)):
        json.dump(corpo, open(os.path.join(SAIDA, nome), 'w', encoding='utf-8'),
                  ensure_ascii=False, indent=1)

    print('registros: %d  (exigem rota italiana: %d)'
          % (len(registros), novo_dado['EXIGEM_ROTA_ITALIANA']))
    print('fontes novas: %d' % len(fontes_u))
    print('por bloco:', {k: v['REGISTROS'] for k, v in por_bloco.items()})
    print('catalogo comercial:', len((cat or {}).get('PRODUTOS', [])))
    if correcao_rota:
        print('rota: %d fontes mudaram de estado com a VPN'
              % len(correcao_rota['MEDIDO_ANTES_E_DEPOIS']))
    print('gravado em', os.path.relpath(SAIDA, ROOT))


if __name__ == '__main__':
    main()
