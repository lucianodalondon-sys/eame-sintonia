#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""AS TRÊS DECISÕES DE PRODUTO — demonstradas sobre dado real, não sobre prosa.

SOMENTE LEITURA. Nenhum dado é migrado. Este script **demonstra o mapa** para que a
decisão humana seja tomada olhando registros de verdade.

    familias    prova que os três sentidos de "família" são eixos ORTOGONAIS
    evidencia   separa NATUREZA da evidência de FORÇA da prova, sem idioma no código
    capacidade  confirma o dono da relação capacidade → caso/evidência

Uso
    python3 scripts/passaporte_decisoes.py familias   --acervo .
    python3 scripts/passaporte_decisoes.py evidencia  --acervo . [--json saida.json]
    python3 scripts/passaporte_decisoes.py capacidade --acervo .
"""

from __future__ import annotations

import argparse
import collections
import json
import os
import re
import sys

RULE_VERSION = 'DECISOES-2026-09-06'
args_acervo_global = None


# ══════════════════════════════════════════════════════════════════════════════════
# 1 · FAMÍLIA — três sentidos, três nomes, nenhum deles chamado só "FAMILY_ID"
# ══════════════════════════════════════════════════════════════════════════════════
#
# A missão pediu para NÃO eleger um dos três para representar todos. Os nomes abaixo
# preferem o que já existe no repositório:
#
#   SOURCE_FAMILY    já existe, com esse nome, no CONTRATO-DO-PASSAPORTE §1.2
#   EVIDENCE_FAMILY  formaliza o `FAMILIA` de scripts/v2_dedup_e_familias.py:47
#   DATASET_FAMILY   formaliza o `FAMILIAS` de scripts/it_acervo_inventario_v2.py:53
#
# NENHUM dado é migrado aqui. O que segue é a demonstração de que os três respondem
# perguntas diferentes sobre o MESMO registro — e por isso não podem dividir um nome.

EVIDENCE_FAMILY_LEGADO = {           # v2_dedup_e_familias.py:47 — bloco → natureza
    'fenologia': 'CURRENT_FIELD_SIGNALS',
    'boletins-regioes-fechadas': 'CURRENT_FIELD_SIGNALS',
    'mercado': 'MARKET_OBSERVATIONS',
    'ismea-mercado': 'MARKET_OBSERVATIONS',
    'peso-economico': 'CROP_ECONOMIC_WEIGHT',
    'istat-area-producao': 'CROP_ECONOMIC_WEIGHT',
    'catalogo': 'COMMERCIAL_CATALOG',
    'regulatorio': 'REGULATORY_FUTURE',
    'clima': 'AGROMET_CONDITIONS',
    'arpav-clima-veneto': 'AGROMET_CONDITIONS',
    'concorrente': 'COMPETITOR_PUBLIC_SIGNALS',
    'vozes': 'PUBLIC_VOICES',
    'herbicida': 'HERBICIDE_CURRENT_CONTEXT',
    'eventos': 'FUTURE_EVENTS',
}

DATASET_FAMILY_LEGADO = [            # it_acervo_inventario_v2.py:53 — caminho → local
    ('RADAR_FUTURO',      r'IT-FUTURO'),
    ('ROTULOS_PORTFOLIO', r'IT-ROTULOS|IT-VOCAB|IT-PAIRSET|productsRegulatory|productRelationships'),
    ('SINAIS_DE_CAMPO',   r'IT-CAMPO|CURRENT-FIELD|IT-CRUZAMENTO'),
    ('FITOSSANITARIO',    r'IT-CONVEGNO|IT-VIDEO|IT-VOZ-AUDIO|falas/|testemunhas/'),
    ('FONTES',            r'IT-FONTES'),
    ('CONCORRENCIA',      r'COMPETITOR|CONCORREN'),
    ('SOCIAL_INSTAGRAM',  r'IT-INSTAGRAM'),
    ('SENSORES_HUMANOS',  r'SENSOR-PILOT|EARLY_SIGNAL|RESEARCHER|SPEAKER'),
    ('GEOGRAFIA',         r'TERRITORIAL|nuts2|GEOGRAF'),
    ('MERCADO',           r'MARKET|PRICES|ECONOMIC'),
    ('OPORTUNIDADES',     r'IT-RADAR-V21|OPPORTUNIT|IT-SNAPSHOT'),
    ('HANDOFF_METODO',    r'IT-HANDOFF|RUN-MANIFEST|DATA-CLOCK|POLITICA|AUDITORIA|ROTAS-EXTERNAS'),
    ('IT-PORTAL',         r'IT-PORTAL'),
]

SOURCE_FAMILY_VOCAB = (              # CONTRATO-DO-PASSAPORTE §1.2 — rota de coleta
    'PLATFORM_PUBLIC_PAID_ROUTE', 'PLATFORM_PUBLIC_FREE_ROUTE', 'TERRITORIAL_BULLETIN',
    'OFFICIAL_REGISTRY', 'FIELD_MONITORING_NETWORK', 'STATISTICAL_OFFICE',
    'SCIENCE_CORPUS', 'MEDIA_FEED')


def dataset_family(caminho):
    for nome, rx in DATASET_FAMILY_LEGADO:
        if re.search(rx, caminho, re.IGNORECASE):
            return nome
    return 'NAO_CLASSIFICADO'


def universo_de_cada_eixo(acervo):
    """Onde cada eixo tem dado de verdade. Medido, não presumido.

    Achado desta medição: os três eixos **não cobrem o mesmo universo**. A família
    semântica depende do campo `BLOCO`, que não existe em `data/samples` — ele vive
    no pipeline V2 (`IT-V2-QA-ATRIBUIDO.json` → `build/ITALY-REALITY-HANDOFF-V2/`).
    """
    r = {}
    for eixo, campo, raiz in (('EVIDENCE_FAMILY', 'BLOCO', 'data'),
                              ('EVIDENCE_FAMILY', 'BLOCO', 'build'),
                              ('SOURCE_FAMILY', 'SOURCE_FAMILY', 'data')):
        n, arquivos = 0, set()
        base = os.path.join(acervo, raiz)
        if not os.path.isdir(base):
            r[f'{eixo}@{raiz}'] = 'DIRETORIO_AUSENTE'
            continue

        def conta(o, caminho):
            nonlocal n
            if isinstance(o, dict):
                if campo in o:
                    n += 1
                    arquivos.add(caminho)
                for v in o.values():
                    conta(v, caminho)
            elif isinstance(o, list):
                for v in o[:2000]:
                    conta(v, caminho)

        for pasta, _, nomes in os.walk(base):
            for nome in nomes:
                if not nome.endswith('.json'):
                    continue
                p = os.path.join(pasta, nome)
                try:
                    conta(json.load(open(p, encoding='utf-8')), p)
                except Exception:                              # noqa: BLE001
                    pass
        r[f'{eixo}@{raiz}'] = {'OCORRENCIAS': n, 'ARQUIVOS': len(arquivos)}
    return r


def demonstrar_familias(acervo, limite=400):
    """Para registros reais: os três eixos lado a lado, e a prova de ortogonalidade."""
    linhas = []
    base = os.path.join(acervo, 'data', 'samples')
    for pasta, _, nomes in os.walk(base):
        for nome in sorted(nomes):
            if not nome.endswith('.json'):
                continue
            caminho = os.path.join(pasta, nome)
            rel = os.path.relpath(caminho, acervo).replace('\\', '/')
            try:
                dados = json.load(open(caminho, encoding='utf-8'))
            except Exception:                                  # noqa: BLE001
                continue
            if not isinstance(dados, dict):
                continue
            topo = {k: v for k, v in dados.items() if not isinstance(v, (dict, list))}
            arr = None
            for k, v in dados.items():
                if isinstance(v, list) and v and isinstance(v[0], dict):
                    arr = v
                    break
            if not arr:
                continue
            reg = dict(topo, **arr[0])
            linhas.append({
                'ARQUIVO': rel,
                'DATASET_FAMILY': dataset_family(rel),
                # Medido: SOURCE_FAMILY tem ZERO ocorrências em data/ — ele só existe
                # dentro do log do passaporte (3.127 vezes). Aqui a coluna mostra o que
                # o acervo REALMENTE traz, e o cabeçalho diz o nome certo.
                'EVIDENCE_CLASS': reg.get('EVIDENCE_CLASS') or 'NAO_DECLARADA',
                'SOURCE_FAMILY_NO_ACERVO': reg.get('SOURCE_FAMILY') or 'AUSENTE_EM_DATA',
                'EVIDENCE_FAMILY': EVIDENCE_FAMILY_LEGADO.get(str(reg.get('BLOCO') or '').lower(),
                                                              'NAO_DECLARADA'),
                'SOURCE_ID': reg.get('SOURCE_ID'),
            })
            if len(linhas) >= limite:
                return linhas
    return linhas


# ══════════════════════════════════════════════════════════════════════════════════
# 2 · EVIDÊNCIA — natureza, força e estado são TRÊS campos
# ══════════════════════════════════════════════════════════════════════════════════
#
# O código interno é neutro de idioma. Português, italiano e inglês são APRESENTAÇÃO.
# E, como a missão pediu, natureza e força NÃO dividem o mesmo código.

EVIDENCE_CLASS_VOCAB = {             # NATUREZA — o que a evidência É
    'EVC-DOC':    'documento',
    'EVC-STAT':   'série estatística',
    'EVC-SCI':    'literatura científica',
    'EVC-REG':    'ato regulatório',
    'EVC-MKT':    'observação de mercado',
    'EVC-FIELD':  'observação de campo',
    'EVC-TABLE':  'tabela de uso autorizado',
    'EVC-IDENT':  'registro de identidade',
    'EVC-INTERP': 'interpretação',
    'EVC-SCOPE':  'delimitação de escopo',
    'EVC-MEAS':   'medição',
    'EVC-PROBE':  'sonda de fonte',
    'EVC-RAW':    'bruto preservado',
    'EVC-DIR':    'diretório de entidades',
    'EVC-CORPUS': 'corpus de material',
    'EVC-COMM':   'comunicação pública',
}

EVIDENCE_STRENGTH_VOCAB = (          # FORÇA — quanto ela sustenta
    'PRIMARY',      # a fonte original, lida direto
    'OFFICIAL',     # autoridade pública publicando o próprio ato/estatística
    'SCIENTIFIC',   # literatura revisada
    'DERIVED',      # produzido por nós a partir de outra coisa — NUNCA é observação
    'UNKNOWN',
)

# Legado → (natureza, força). Cada valor de hoje vai para DOIS campos, não um.
MAPA_LEGADO = {
    'PRIMARY_SOURCE_RAW':             ('EVC-RAW',    'PRIMARY'),
    'PRIMARY_SOURCE_PROBE':           ('EVC-PROBE',  'PRIMARY'),
    'OFFICIAL_DOCUMENT':              ('EVC-DOC',    'OFFICIAL'),
    'DOCUMENTO_OFICIAL':              ('EVC-DOC',    'OFFICIAL'),   # a mesma coisa, em PT
    'OFFICIAL_STATISTIC':             ('EVC-STAT',   'OFFICIAL'),
    'OFFICIAL_MARKET_OBSERVATION':    ('EVC-MKT',    'OFFICIAL'),
    'REGULATORY_FACT':                ('EVC-REG',    'OFFICIAL'),
    'TECHNICAL_AUTHORITY_DECLARATION': ('EVC-DOC',   'OFFICIAL'),
    'CROP_IN_AUTHORIZED_USE_TABLE':   ('EVC-TABLE',  'OFFICIAL'),
    'SCIENTIFIC_LITERATURE':          ('EVC-SCI',    'SCIENTIFIC'),
    'DERIVED_INTERPRETATION':         ('EVC-INTERP', 'DERIVED'),
    'DERIVED_SCOPE':                  ('EVC-SCOPE',  'DERIVED'),
    'DERIVED_MEASUREMENT':            ('EVC-MEAS',   'DERIVED'),
    'DERIVED_IDENTITY':               ('EVC-IDENT',  'DERIVED'),
    # o nome declara os dois eixos sem ambiguidade — mapeável
    'PRIMARY_SOURCE':                 ('EVC-DOC',    'PRIMARY'),
    'DERIVED_DIRECTORY':              ('EVC-DIR',    'DERIVED'),
    'DERIVED_MATERIAL_CORPUS':        ('EVC-CORPUS', 'DERIVED'),
    'COMPETITOR_PUBLIC_COMMUNICATION_OBSERVED': ('EVC-COMM', 'PRIMARY'),
}

# ── o que NÃO é natureza de evidência, e por isso não entra no mapa ────────────────
#
# Medido: `EVIDENCE_CLASS` está carregando TRÊS conceitos ao mesmo tempo. Só um deles
# é natureza de evidência. Os outros dois estão no campo errado, e mapeá-los seria
# esconder o defeito em vez de mostrá-lo.

FORA_DO_CONCEITO = {
    'PUBLIC_FREE_ROUTE': {
        'ONDE': 'data/samples/.../CANAIS.json',
        'O_QUE_E': 'rota de coleta, não natureza de evidência',
        'CAMPO_CERTO': 'SOURCE_FAMILY (PLATFORM_PUBLIC_FREE_ROUTE)',
        'ACAO': 'mover de campo — não mapear',
    },
    'HUMAN_DECISION': {
        'ONDE': 'data/samples/.../LEXICO-APROVADO.json',
        'O_QUE_E': 'decisão nossa, não evidência sobre o mundo',
        'CAMPO_CERTO': 'campo próprio de decisão (não existe ainda)',
        'ACAO': 'NÃO SEI — precisa de dono',
    },
    'PRESERVATION_MANIFEST': {
        'ONDE': 'data/samples/.../MANIFESTO-PRESERVACAO.json',
        'O_QUE_E': 'declaração sobre o nosso próprio processo',
        'CAMPO_CERTO': 'metadado de preservação, não EVIDENCE_CLASS',
        'ACAO': 'NÃO SEI — precisa de dono',
    },
    'SOURCE_HEALTH': {
        'ONDE': 'data/samples/IT-FONTES/ITALY-SOURCE-PROBE.json',
        'O_QUE_E': 'medição sobre a FONTE (alcançável? responde?), não sobre o mundo',
        'CAMPO_CERTO': 'estado da fonte, não natureza de evidência',
        'ACAO': 'NÃO SEI — precisa de dono',
    },
}

AMBIGUOS = {
    'PRIMARY_SOURCE_CONVERGENCE': {
        'ONDE': 'data/samples/IT-CASOS/IT-CASE-DURUM-FUSARIUM-001.json',
        'CONFLITO': 'o nome diz PRIMARY, e convergência entre fontes é DERIVADA. '
                    'Os dois eixos brigam dentro do mesmo valor.',
        'ACAO': 'NÃO SEI — decidir se a força é a das fontes ou a da análise',
    },
    'PRIMARY_DECLARED_LINK': {
        'ONDE': 'data/samples/COMPETITOR-PUBLIC-COMM/ANCORAS-EVIDENCIA-V1.json',
        'CONFLITO': 'ligação declarada por quem? se por nós, é DERIVED; '
                    'se pela fonte, é PRIMARY. O valor não diz.',
        'ACAO': 'NÃO SEI — decidir quem declara',
    },
}


def medir_evidencia(acervo):
    """Conta os valores reais e mostra o que cada um vira nos dois campos."""
    contagem = collections.Counter()
    arquivos = collections.defaultdict(set)

    def visitar(obj, caminho):
        if isinstance(obj, dict):
            for k, v in obj.items():
                if k == 'EVIDENCE_CLASS' and isinstance(v, str):
                    contagem[v] += 1
                    arquivos[v].add(caminho)
                visitar(v, caminho)
        elif isinstance(obj, list):
            for v in obj:
                visitar(v, caminho)

    for pasta, _, nomes in os.walk(os.path.join(acervo, 'data')):
        for nome in sorted(nomes):
            if not nome.endswith(('.json', '.jsonl')):
                continue
            caminho = os.path.join(pasta, nome)
            try:
                if nome.endswith('.jsonl'):
                    for linha in open(caminho, encoding='utf-8'):
                        if linha.strip():
                            visitar(json.loads(linha), caminho)
                else:
                    visitar(json.load(open(caminho, encoding='utf-8')), caminho)
            except Exception:                                  # noqa: BLE001
                pass
    return contagem, arquivos


# ══════════════════════════════════════════════════════════════════════════════════
# 3 · CAPACIDADE — o dono, confirmado por contagem
# ══════════════════════════════════════════════════════════════════════════════════

def medir_capacidade(acervo):
    """Quem declara CAP-xxx, quem liga CAP a CASE, e o que o portal faz."""
    r = {'DECLARA_CAP': {}, 'LIGA_CAP_A_CASE': {}, 'PORTAL': {}}
    alvos = {
        'ATLAS (vocabulário)': 'docs/capacidades/ATLAS-DE-CAPACIDADES-EAME.md',
        'CONTRATO DE PROVA': 'docs/apresentacao/CONTRATO-DE-PROVA-DA-APRESENTACAO.md',
        'ARQUITETURA (áreas)': 'docs/ferramentas/ARQUITETURA-DE-INFORMACAO-EAME.md',
        'MATRIZ DE CRUZAMENTOS': 'docs/cruzamentos/MATRIZ-DE-CRUZAMENTOS-EAME.md',
        'CASOS': 'docs/apresentacao/CASOS-PARA-APRESENTACAO.md',
    }
    for rotulo, rel in alvos.items():
        caminho = os.path.join(acervo, rel)
        if not os.path.isfile(caminho):
            r['DECLARA_CAP'][rotulo] = 'ARQUIVO_AUSENTE'
            continue
        texto = open(caminho, encoding='utf-8').read()
        caps = set(re.findall(r'CAP-\d{3}', texto))
        # linhas que ligam CAP a CASE na MESMA linha = a relação, não a menção
        ligacoes = [l.strip() for l in texto.splitlines()
                    if re.search(r'CAP-\d{3}', l) and re.search(r'CASE-\d{3}', l)]
        r['DECLARA_CAP'][rotulo] = {'CAPS_DISTINTOS': len(caps),
                                    'OCORRENCIAS': len(re.findall(r'CAP-\d{3}', texto))}
        if ligacoes:
            r['LIGA_CAP_A_CASE'][rotulo] = {'LINHAS': len(ligacoes),
                                            'EXEMPLO': ligacoes[0][:110]}
    portal = os.path.join(acervo, 'italia-portale')
    n_cap, arquivos = 0, []
    if os.path.isdir(portal):
        for pasta, _, nomes in os.walk(portal):
            for nome in nomes:
                if not nome.endswith(('.js', '.html', '.json')):
                    continue
                try:
                    t = open(os.path.join(pasta, nome), encoding='utf-8',
                             errors='ignore').read()
                except Exception:                              # noqa: BLE001
                    continue
                achados = re.findall(r'CAP-\d{3}|CAPABILITY_ID', t)
                if achados:
                    n_cap += len(achados)
                    arquivos.append(os.path.relpath(os.path.join(pasta, nome), acervo))
    r['PORTAL'] = {'OCORRENCIAS_DE_CAP_OU_CAPABILITY_ID': n_cap, 'ARQUIVOS': arquivos[:5]}
    return r


# ══════════════════════════════════════════════════════════════════════════════════

def main(argv=None):
    p = argparse.ArgumentParser()
    p.add_argument('comando', choices=['familias', 'evidencia', 'capacidade'])
    p.add_argument('--acervo', default=os.path.dirname(os.path.dirname(
        os.path.abspath(__file__))))
    p.add_argument('--json', default=None)
    args = p.parse_args(argv)
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:                                          # noqa: BLE001
        pass

    global args_acervo_global
    args_acervo_global = args.acervo

    if args.comando == 'familias':
        linhas = demonstrar_familias(args.acervo)
        print(f'FAMÍLIA — três eixos ortogonais · {RULE_VERSION} · nenhum dado migrado\n')
        print(f'{"DATASET_FAMILY":22s} {"EVIDENCE_CLASS":30s} {"EVIDENCE_FAMILY":26s} arquivo')
        vistos = set()
        for l in linhas:
            chave = (l['DATASET_FAMILY'], l['EVIDENCE_CLASS'])
            if chave in vistos:
                continue
            vistos.add(chave)
            print(f"{l['DATASET_FAMILY']:22s} {str(l['EVIDENCE_CLASS'])[:29]:30s} "
                  f"{l['EVIDENCE_FAMILY']:26s} {l['ARQUIVO'][-46:]}")
        # a prova de ortogonalidade: um DATASET_FAMILY com mais de um SOURCE_FAMILY
        cruz = collections.defaultdict(set)
        for l in linhas:
            cruz[l['DATASET_FAMILY']].add(str(l['EVIDENCE_CLASS']))
        multi = {k: v for k, v in cruz.items() if len(v) > 1}
        print(f'\n── PROVA DE ORTOGONALIDADE ──')
        print(f'  registros amostrados                : {len(linhas)}')
        print(f'  DATASET_FAMILY com >1 EVIDENCE_CLASS: {len(multi)} de {len(cruz)}')
        for k, v in sorted(multi.items())[:6]:
            print(f'     {k:22s} → {sorted(v)}')
        print('\n  Um mesmo LOCAL de dataset recebe evidências de NATUREZAS diferentes.')
        print('  Chamar os dois de FAMILY_ID faria um GROUP BY misturar os dois recortes.')
        print('\n── OS TRÊS EIXOS NÃO COBREM O MESMO UNIVERSO ──')
        for k, v in universo_de_cada_eixo(args_acervo_global or '.').items():
            print(f'  {k:26s} {v}')
        print('\n  MEDIDO — e corrige uma frase que eu quase escrevi:')
        print('   · BLOCO (a chave de EVIDENCE_FAMILY) EXISTE em data/, mas só em DOIS')
        print('     arquivos: IT-V2/IT-V2-CANONICO.json e IT-V2/IT-V2-QA-ATRIBUIDO.json.')
        print('     Mais 13 arquivos em build/. Não é "ausente" — é confinado ao V2.')
        print('   · SOURCE_FAMILY tem ZERO ocorrências em data/. Ele existe apenas dentro')
        print('     do log do passaporte, 3.127 vezes.')
        print('\n  Os três eixos vivem em TRÊS universos diferentes. Um FAMILY_ID único não')
        print('  misturaria só os recortes — misturaria também as coberturas, e o número')
        print('  resultante pareceria total sem ser total de nada.')

    elif args.comando == 'evidencia':
        contagem, arquivos = medir_evidencia(args.acervo)
        print(f'EVIDÊNCIA — natureza ≠ força · {RULE_VERSION} · nenhum dado migrado\n')
        print(f'{"valor de hoje":34s} {"n":>6s}  {"EVIDENCE_CLASS":12s} {"EVIDENCE_STRENGTH":18s}')
        nao_mapeados = []
        for v, n in contagem.most_common():
            par = MAPA_LEGADO.get(v)
            if par:
                print(f'{v:34s} {n:6d}  {par[0]:12s} {par[1]:18s}')
            else:
                nao_mapeados.append((v, n))
                print(f'{v:34s} {n:6d}  {"NAO SEI":12s} {"NAO SEI":18s}  ← não mapeado')
        print(f'\n  valores distintos            : {len(contagem)}')
        print(f'  mapeados                     : {len(contagem) - len(nao_mapeados)}')
        print(f'  NÃO mapeados (ficam NÃO SEI) : {len(nao_mapeados)}')
        print('\n── O CAMPO CARREGA TRES CONCEITOS. So um e natureza de evidencia. ──')
        print('\n  FORA DO CONCEITO — estao no campo errado:')
        for k, v in FORA_DO_CONCEITO.items():
            print(f"    {k}  ({contagem.get(k, 0)}x)")
            print(f"       e: {v['O_QUE_E']}")
            print(f"       campo certo: {v['CAMPO_CERTO']}")
            print(f"       acao: {v['ACAO']}")
        print('\n  AMBIGUOS — os dois eixos brigam dentro do valor:')
        for k, v in AMBIGUOS.items():
            print(f"    {k}  ({contagem.get(k, 0)}x)")
            print(f"       {v['CONFLITO']}")
            print(f"       acao: {v['ACAO']}")
        pt = contagem.get('DOCUMENTO_OFICIAL', 0)
        en = contagem.get('OFFICIAL_DOCUMENT', 0)
        if pt or en:
            print(f'\n  o conflito de idioma, resolvido no código interno:')
            print(f'     OFFICIAL_DOCUMENT ({en}) e DOCUMENTO_OFICIAL ({pt}) → ambos EVC-DOC / OFFICIAL')
        if args.json:
            json.dump({'RULE_VERSION': RULE_VERSION,
                       'EVIDENCE_CLASS_VOCAB': EVIDENCE_CLASS_VOCAB,
                       'EVIDENCE_STRENGTH_VOCAB': list(EVIDENCE_STRENGTH_VOCAB),
                       'MAPA_LEGADO': {k: {'EVIDENCE_CLASS': a, 'EVIDENCE_STRENGTH': b}
                                       for k, (a, b) in MAPA_LEGADO.items()},
                       'CONTAGEM_REAL': dict(contagem),
                       'NAO_MAPEADOS': dict(nao_mapeados),
                       'FORA_DO_CONCEITO': FORA_DO_CONCEITO,
                       'AMBIGUOS': AMBIGUOS},
                      open(args.json, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
            print(f'\ngravado: {args.json}')

    else:
        r = medir_capacidade(args.acervo)
        print(f'CAPACIDADE — quem é o dono · {RULE_VERSION}\n')
        print('── quem MENCIONA CAP-xxx ──')
        for k, v in r['DECLARA_CAP'].items():
            print(f'  {k:26s} {v}')
        print('\n── quem LIGA capacidade a caso (CAP e CASE na mesma linha) ──')
        for k, v in r['LIGA_CAP_A_CASE'].items():
            print(f'  {k:26s} {v["LINHAS"]} linhas')
            print(f'       ex: {v["EXEMPLO"]}')
        print('\n── o portal ──')
        print(f'  ocorrências de CAP-xxx ou CAPABILITY_ID: '
              f'{r["PORTAL"]["OCORRENCIAS_DE_CAP_OU_CAPABILITY_ID"]}')
        print(f'  arquivos: {r["PORTAL"]["ARQUIVOS"] or "nenhum"}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
