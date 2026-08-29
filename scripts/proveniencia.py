#!/usr/bin/env python3
"""
PROVENIÊNCIA — o RUN_ID deixa de ser um rótulo e passa a resolver.

O defeito que este arquivo fecha: até 2026-08-29 o `RUN_ID` agrupava registros entre si e
não resolvia para nada fora do repositório. Dado um vídeo, não havia como responder
"que execução produziu isto, com que ator, que entrada e que custo".

A cadeia que passa a existir:

    CONTENT → RUN_ID → RUN_MANIFEST → INPUT / ACTOR / DATASET / RAW

Três decisões carregadas aqui:

1. **CAMPO DESCONHECIDO É `NOT_PRESERVED`, NUNCA AUSENTE.**
   Execução antiga que não capturou `ACTOR_VERSION` declara `NOT_PRESERVED`. Isso é
   diferente de `NAO_SEI` (a fonte não informa) e muito diferente da chave sumir.

2. **NUNCA GRAVAR TOKEN.** `INPUT` guarda a consulta e os parâmetros; credencial jamais.
   Há teste que varre o manifesto atrás de padrão de token.

3. **TEMPO É MEDIDO, NÃO INFERIDO.** `STARTED_AT`/`FINISHED_AT` vêm da execução. Sem eles,
   nenhuma afirmação de ordem entre camadas é permitida — ver `pode_afirmar_ordem()`.
"""
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
MANIFESTO = os.path.join(ROOT, 'data', 'samples', 'RUN-MANIFEST.json')

NAO_SEI = 'NÃO SEI'
NOT_PRESERVED = 'NOT_PRESERVED'

# Campos obrigatórios de todo manifesto de execução.
CAMPOS_RUN = [
    'RUN_ID', 'PLATFORM', 'ACTOR', 'ACTOR_VERSION', 'STARTED_AT', 'FINISHED_AT',
    'INPUT', 'COUNTRY', 'MISSION', 'QUERY', 'DATASET_ID',
    'ITEM_COUNT_RAW', 'ITEM_COUNT_NORMALIZED', 'COST_USD', 'SOURCE_VERSION',
    'STATUS', 'ERROR', 'CAPTURE_METHOD', 'EVIDENCE_PATH', 'RAW_EVIDENCE_PATH',
    'RAW_EVIDENCE_STATE',
    # Hora em que o coletor GRAVOU a saída. É medida de verdade, mas NÃO é a hora da
    # execução na plataforma — por isso vive em campo próprio e nunca é usada como
    # STARTED_AT/FINISHED_AT. Passar hora de escrita por hora de execução seria
    # exatamente o erro que a auditoria derrubou.
    'OUTPUT_WRITTEN_AT',
]

STATUS_RUN = ['SUCCESS', 'PARTIAL', 'FAILED', 'NOT_PRESERVED']
# Estado da evidência bruta. `NOT_PRESERVED` é uma confissão, não um sinônimo de ausência
# de dado: quer dizer que a resposta crua existiu e não foi guardada.
ESTADOS_RAW = ['PRESERVED', 'NOT_PRESERVED', 'NOT_APPLICABLE']

TOKEN = re.compile(r'apify_api_[A-Za-z0-9]{10,}|Bearer\s+[A-Za-z0-9._\-]{20,}')


def run_vazio():
    """Todo campo presente, todo valor em NOT_PRESERVED."""
    return {c: NOT_PRESERVED for c in CAMPOS_RUN}


def novo_run(run_id, **campos):
    """Monta um manifesto completo. Campo não informado fica NOT_PRESERVED, nunca some."""
    r = run_vazio()
    r['RUN_ID'] = run_id
    for k, v in campos.items():
        if k not in CAMPOS_RUN:
            raise KeyError('campo fora do contrato de RUN: %s' % k)
        r[k] = v
    checar_token(r)
    return r


def checar_token(run):
    """Um manifesto nunca pode carregar credencial."""
    achado = TOKEN.search(json.dumps(run, ensure_ascii=False))
    if achado:
        raise ValueError('credencial no manifesto de execução — nunca gravar token')
    return True


def carregar():
    if not os.path.exists(MANIFESTO):
        return {}
    with open(MANIFESTO, encoding='utf-8') as f:
        d = json.load(f)
    return {r['RUN_ID']: r for r in d.get('RUNS', [])}


def resolver(run_id):
    """RUN_ID -> manifesto. É isto que faltava: o rótulo agora resolve."""
    return carregar().get(run_id)


def gravar(runs, *, captured_at):
    """Persiste o manifesto. `runs` é lista de dicionários já no contrato."""
    for r in runs:
        faltando = set(CAMPOS_RUN) - set(r)
        if faltando:
            raise KeyError('manifesto incompleto, faltam: %s' % sorted(faltando))
        checar_token(r)
        if r['STATUS'] not in STATUS_RUN:
            raise ValueError('STATUS fora do contrato: %s' % r['STATUS'])
        if r['RAW_EVIDENCE_STATE'] not in ESTADOS_RAW:
            raise ValueError('RAW_EVIDENCE_STATE fora do contrato: %s' % r['RAW_EVIDENCE_STATE'])
    corpo = {
        'SOURCE_ID': 'RUN-MANIFEST',
        'source': 'manifesto de execuções de coleta do SINTONIA EAME',
        'SOURCE_LOCATION': 'interno — metadado de coleta',
        'FACT_LOCATION': 'n/a — descreve execução, não fato do mundo',
        'ORIGINAL_LANGUAGE': 'pt',
        'captured_at': captured_at,
        'PARA_QUE_SERVE': (
            'dado um registro qualquer, o RUN_ID leva a esta tabela e a tabela diz que ator '
            'rodou, com que entrada, quando, quanto custou e onde está a evidência bruta. '
            'Sem isto o RUN_ID só agrupa registros entre si.'),
        'CAMPO_DESCONHECIDO': (
            'NOT_PRESERVED significa que o campo existiu na execução e não foi capturado. '
            'É confissão, não ausência de dado — e é diferente de NÃO SEI, que é a fonte '
            'não informar.'),
        'NUNCA_GRAVAR_TOKEN': 'INPUT guarda consulta e parâmetros. Credencial, jamais.',
        'RUNS': runs,
    }
    with open(MANIFESTO, 'w', encoding='utf-8') as f:
        json.dump(corpo, f, ensure_ascii=False, indent=1)
    return corpo


# ---------------------------------------------------------------- ordem entre camadas
def pode_afirmar_ordem(run_a, run_b):
    """`X BEFORE Y` só é dizível quando as duas execuções têm hora medida.

    A auditoria de 2026-08-29 derrubou a afirmação "o YouTube veio antes do LinkedIn":
    as duas rotas saíram do mesmo orçamento sem carimbo que as separasse, e o horário de
    commit do git NÃO mede hora de coleta — mede hora de escrita.
    """
    for r in (run_a, run_b):
        if not r:
            return False, 'execução sem manifesto'
        for c in ('STARTED_AT', 'FINISHED_AT'):
            if r.get(c) in (NOT_PRESERVED, NAO_SEI, None, ''):
                return False, '%s sem %s medido' % (r.get('RUN_ID'), c)
    return True, ''


def ordem(run_a, run_b):
    """Devolve BEFORE / AFTER / OVERLAPS, ou NAO_DIZIVEL com o motivo."""
    ok, motivo = pode_afirmar_ordem(run_a, run_b)
    if not ok:
        return 'NAO_DIZIVEL', motivo
    if run_a['FINISHED_AT'] <= run_b['STARTED_AT']:
        return 'BEFORE', ''
    if run_b['FINISHED_AT'] <= run_a['STARTED_AT']:
        return 'AFTER', ''
    return 'OVERLAPS', ''



# ------------------------------------------------- inventário do bruto de rota paga
# Por que este bloco existe: até 2026-08-29 duas coisas inventariavam o MESMO diretório —
# `POLITICA-RAW-ROTA-PAGA.json` (lista digitada) e o DATA CLOCK (lista derivada). Elas
# divergiram em silêncio: um bruto novo entrou, o relógio o pegou, a política não. Um
# inventário digitado de uma população que muda é o mesmo defeito de sempre, agora em JSON.
#
# A partir daqui o DONO da população é este módulo, e o inventário é DERIVADO do diretório.

RAW_PAID_REL = 'data/samples/raw-paid'

# Duas populações vivem no mesmo diretório e NÃO têm a mesma obrigação. Sem distinguir,
# um bruto operacional órfão se esconde atrás de um artefato de teste — e foi assim que
# GATE-TEST-...-b passou despercebido.
PRODUCTION_RAW = 'PRODUCTION_RAW'
GATE_TEST_RAW = 'GATE_TEST_RAW'
CLASSES_RAW = [PRODUCTION_RAW, GATE_TEST_RAW]

# Convenção de nome aplicada pelo coletor nas execuções de verificação do portão.
# Não é heurística sobre conteúdo: é declaração, e este módulo é o dono de interpretá-la.
PREFIXO_GATE_TEST = 'GATE-TEST-'

MOTIVO_GATE_TEST = (
    'artefato de verificação do portão do coletor, não coleta. Não produz registro '
    'analítico publicado, por isso não há execução de produção que o cite. '
    'EXCLUDED_WITH_REASON — nunca ausência silenciosa.')


def classificar_raw(caminho):
    """PRODUCTION_RAW ou GATE_TEST_RAW."""
    base = os.path.basename(str(caminho))
    return GATE_TEST_RAW if base.startswith(PREFIXO_GATE_TEST) else PRODUCTION_RAW


def arquivos_raw_pagos(root=ROOT):
    """O conjunto REAL em disco. O denominador nunca é uma lista digitada."""
    d = os.path.join(root, RAW_PAID_REL)
    if not os.path.isdir(d):
        return []
    return sorted('%s/%s' % (RAW_PAID_REL, n)
                  for n in os.listdir(d) if not n.startswith('.'))


def _caminhos_declarados(run):
    """RAW_EVIDENCE_PATH normalizado: aceita string ou lista, ignora NOT_PRESERVED."""
    p = run.get('RAW_EVIDENCE_PATH')
    for c in (p if isinstance(p, list) else [p]):
        c = str(c).split(' (')[0].strip()
        if c and c != NOT_PRESERVED:
            yield c


def runs_por_bruto(runs=None):
    """A direção INVERSA da cadeia: ARQUIVO BRUTO -> execuções que o declaram.

    `CONTENT -> RUN_ID -> MANIFEST` já existia. Faltava esta: um arquivo bruto que
    nenhuma execução reivindica é evidência sem procedência, e não pode ficar em silêncio.
    """
    runs = carregar() if runs is None else runs
    idx = {}
    for rid, r in sorted(runs.items()):
        for c in _caminhos_declarados(r):
            idx.setdefault(c, []).append(rid)
    return idx


def _itens(path):
    """Quantos itens o bruto carrega. Derivado do arquivo, não declarado."""
    import gzip
    try:
        with gzip.open(path, 'rt', encoding='utf-8') as f:
            o = json.load(f)
        return len(o) if isinstance(o, (list, dict)) else NAO_SEI
    except (OSError, ValueError):
        return NAO_SEI


def inventario_raw_pago(root=ROOT, runs=None):
    """Reconciliação executável entre DISCO, MANIFESTO e CLASSE.

    Cada arquivo do diretório sai daqui com tamanho e contagem DERIVADOS, a classe
    declarada, e as execuções que o citam — ou o motivo explícito de não ter nenhuma.
    """
    idx = runs_por_bruto(runs)
    inv = []
    for rel in arquivos_raw_pagos(root):
        classe = classificar_raw(rel)
        citado = sorted(idx.get(rel, []))
        item = {'FILE': rel, 'CLASS': classe,
                'GZ_BYTES': os.path.getsize(os.path.join(root, rel)),
                'ITEMS': _itens(os.path.join(root, rel)),
                'RUNS': citado}
        if not citado:
            item['EXCLUDED_WITH_REASON'] = (
                MOTIVO_GATE_TEST if classe == GATE_TEST_RAW else None)
        inv.append(item)
    return inv


def brutos_orfaos(root=ROOT, runs=None):
    """PRODUCTION_RAW que nenhuma execução reivindica. Tem de ser sempre vazio."""
    return [i['FILE'] for i in inventario_raw_pago(root, runs)
            if i['CLASS'] == PRODUCTION_RAW and not i['RUNS']]


def brutos_declarados_e_ausentes(root=ROOT, runs=None):
    """O inverso: execução que diz PRESERVED apontando para arquivo que não existe."""
    runs = carregar() if runs is None else runs
    faltando = []
    for rid, r in sorted(runs.items()):
        if r.get('RAW_EVIDENCE_STATE') != 'PRESERVED':
            continue
        for c in _caminhos_declarados(r):
            if not os.path.exists(os.path.join(root, c)):
                faltando.append((rid, c))
    return faltando


POLITICA = os.path.join(ROOT, 'data', 'samples', 'POLITICA-RAW-ROTA-PAGA.json')

# As chaves que a política NÃO digita mais: saem do diretório real a cada sincronização.
CHAVES_DERIVADAS = ('ARQUIVOS', 'TAMANHO_ATUAL_BYTES', 'TOTAL_POR_CLASSE',
                    'BRUTOS_ORFAOS', 'DERIVADO_POR')


def politica_derivada(root=ROOT, runs=None):
    """O bloco derivado da política. É esta função que a política publica."""
    inv = inventario_raw_pago(root, runs)
    por_classe = {}
    for i in inv:
        c = por_classe.setdefault(i['CLASS'], {'ARQUIVOS': 0, 'GZ_BYTES': 0})
        c['ARQUIVOS'] += 1
        c['GZ_BYTES'] += i['GZ_BYTES']
    return {
        'ARQUIVOS': inv,
        'TAMANHO_ATUAL_BYTES': sum(i['GZ_BYTES'] for i in inv),
        'TOTAL_POR_CLASSE': por_classe,
        'BRUTOS_ORFAOS': brutos_orfaos(root, runs),
        'DERIVADO_POR': (
            'scripts/proveniencia.py --sync-politica. O inventário e os tamanhos são '
            'DERIVADOS do diretório real; nenhum é digitado. Há teste que reprova se a '
            'política divergir do disco.'),
    }


def sincronizar_politica(root=ROOT):
    """Reescreve só o bloco derivado, preservando a prosa da política."""
    with open(POLITICA, encoding='utf-8') as f:
        d = json.load(f)
    antes = {k: d.get(k) for k in CHAVES_DERIVADAS}
    d.update(politica_derivada(root))
    with open(POLITICA, 'w', encoding='utf-8') as f:
        json.dump(d, f, ensure_ascii=False, indent=1)
    return [k for k in CHAVES_DERIVADAS if antes.get(k) != d.get(k)]


if __name__ == '__main__':
    import sys
    runs = carregar()
    print('execuções no manifesto:', len(runs))
    for rid, r in sorted(runs.items()):
        print('  %-34s %-9s %-8s raw=%s' % (rid, r['PLATFORM'], r['STATUS'],
                                            r['RAW_EVIDENCE_STATE']))
    if '--campos' in sys.argv:
        for c in CAMPOS_RUN:
            print(' ', c)
    if '--raw' in sys.argv:
        print()
        for i in inventario_raw_pago():
            print('  %-52s %-15s %9s bytes  itens=%-5s %s'
                  % (i['FILE'].split('/')[-1], i['CLASS'], format(i['GZ_BYTES'], ','),
                     i['ITEMS'], ','.join(i['RUNS']) or 'EXCLUDED_WITH_REASON'))
        print('\n  orfaos de producao:', brutos_orfaos() or 'nenhum')
    if '--sync-politica' in sys.argv:
        mud = sincronizar_politica()
        print('politica sincronizada; chaves alteradas:', mud or 'nenhuma')
