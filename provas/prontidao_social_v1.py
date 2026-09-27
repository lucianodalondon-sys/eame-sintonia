#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SOC1 — A PRONTIDÃO DE LINKEDIN, INSTAGRAM E YOUTUBE PARA A BIG COLLECTION.

    py provas/prontidao_social_v1.py            # tabela no ecrã
    py provas/prontidao_social_v1.py --json F   # e a matriz em F

A pergunta do dono (D16/D17, DECISOES-DONO-2026-09-23) é UMA:

    O QUE FALTA PARA O SCRAP COLHER LI/IG/YT DE GRAÇA
    E ENTRAR NA COLLECTION CANÓNICA?

Esta prova NÃO reconstrói nada. Ela junta, capacidade a capacidade, o que cinco
donos diferentes já dizem — e mostra onde eles discordam:

    1. DECLARADAS  `scrap_capacidades`   o estado medido da capacidade
    2. EXECUTORES  `scrap_registo`       há adaptador e rota ligada?
    3. FASES       `scrap_colheita`      há fase que a PEDE, e de que espécie?
    4. A MATRIZ    `social_matriz`       que rotas existem, de que classe, e se
                                         o projeto as permite
    5. A PORTA     `ponte_candidatas` + `curadoria/worker`  a candidata passa?

e o `scrap_executor.CHECK`, que responde «consigo agora?» sem gastar nada.

A superfície da Release V1 (`superficie_do_scrap_v1.medir`) já mede 1, 2 e o
CHECK. Esta prova LÊ essa medição e acrescenta 3, 4 e 5. Uma segunda medição
do mesmo par seria uma segunda verdade.

    UMA TABELA ESCRITA À MÃO É A MEMÓRIA DE QUEM A ESCREVEU.

⚠️ CREDENCIAIS: só o NOME e a presença. O valor nunca é lido para texto, nunca
é impresso e nunca entra no JSON. `os.environ.get(n)` só é testado como
verdade; a prova tem um teste que injecta um valor-isca e procura-o na saída.

    CREDENCIAL AUSENTE NESTE SHELL != AUSENTE NO SISTEMA.
"""
import argparse
import glob
import json
import os
import re
import sys
from datetime import datetime, timezone

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _p in ('coleta', 'leis', 'admissao', 'regras', 'ferramentas', 'medidas',
           'guarda', 'pedido', 'orquestrador', 'curadoria', 'provas', ''):
    sys.path.insert(0, os.path.join(RAIZ, _p) if _p else RAIZ)

import scrap_capacidades as cap                                   # noqa: E402
import social_matriz as mz                                        # noqa: E402
import superficie_do_scrap_v1 as sup                              # noqa: E402

PLATAFORMAS = ('LINKEDIN', 'INSTAGRAM', 'YOUTUBE')

#: A classe da rota na matriz → o tipo de rota que o dono entende.
#: `LOCAL_SESSION` é navegador JÁ LOGADO: conta de alguém. D17 tirou-a da mesa.
TIPO_DA_CLASSE = {
    'OFFICIAL_API_FREE': 'GRATIS_OFICIAL',
    'PUBLIC_NATIVE': 'GRATIS_PUBLICA',
    'DIRECT_HTTP': 'GRATIS_PUBLICA',
    'PUBLIC_BROWSER': 'GRATIS_PUBLICA',
    'LOCAL_EXECUTOR': 'GRATIS_PUBLICA',
    'LOCAL_SESSION': 'CONTA_PESSOAL',
    'OFFICIAL_API_PAID': 'PAGA',
    'APIFY': 'PAGA',
}
GRATIS = ('GRATIS_OFICIAL', 'GRATIS_PUBLICA')

#: O nome da credencial que cada classe de rota pede. Só NOMES.
#: O da API do YouTube é conferido por teste contra `youtube_oficial.ENV_CHAVE`.
CREDENCIAL_DA_ROTA = {
    'youtube-data-api-v3': 'YOUTUBE_DATA_API_KEY',
    'apify': 'APIFY_TOKEN_POOL',
    'graph:business_discovery': 'META_GRAPH (token de conta Business/Creator — sem nome no repo)',
}

# ── ESTADOS DE PRONTIDÃO DESTA PROVA ────────────────────────────────────────
READY = 'READY'
READY_PENDING_CREDENTIAL = 'READY_PENDING_CREDENTIAL'
PROVED_BUT_NOT_WIRED = 'PROVED_BUT_NOT_WIRED'
ROUTE_NOT_ALLOWED = 'ROUTE_NOT_ALLOWED'
FAIL_CLOSED = 'FAIL_CLOSED'
DESCONHECIDO = 'UNKNOWN'


def _tipo_da_rota(rota):
    return TIPO_DA_CLASSE.get(rota.get('CLASSE'), DESCONHECIDO)


def _credencial_de(nome_rota):
    for prefixo, cred in CREDENCIAL_DA_ROTA.items():
        if (nome_rota or '').startswith(prefixo):
            return cred
    return None


def rotas_da_matriz(plat, capacidade):
    """→ todas as rotas declaradas na matriz para a capacidade, com tipo."""
    grossa = cap.da_matriz(capacidade)
    fora = []
    for r in (mz.MATRIZ.get(plat) or {}).get(grossa) or []:
        fora.append({
            'ROTA': r['ROTA'], 'CLASSE': r['CLASSE'], 'TIPO': _tipo_da_rota(r),
            # COPIA da resposta do dono (leis/social_matriz.py), com nome de copia:
            # esta prova nao responde «pode?» — le quem responde (test_c10_4_route_gate).
            'PERMITIDA_NA_MATRIZ': r['PERMITIDA'], 'ESTADO': r['ESTADO'],
            'OWNER_AUTHORIZED': r.get('OWNER_AUTHORIZED'),
            'PLATFORM_POLICY_STATUS': r.get('PLATFORM_POLICY_STATUS'),
            'CREDENCIAL': _credencial_de(r['ROTA']),
        })
    return grossa, fora


def fases_de(capacidade):
    """→ [(nome da fase, espécie)] de `scrap_colheita.FASES` que a pedem."""
    import scrap_colheita as sc
    return [(nome, linha[3]) for nome, linha in sorted(sc.FASES.items())
            if linha[1] == capacidade]


def porta_da_candidata(plat):
    """→ o que a porta (ponte) e o QUALIFY do worker fazem a uma candidata
    deste tipo. O worker é chamado de verdade, com a ficha substituída por uma
    em memória — e só nos tipos que devolvem antes de qualquer escrita."""
    import ponte_candidatas as pc
    import worker as wk
    if plat in pc.POLITICA:
        ponte = 'POLICY_BLOCK'
    elif plat in pc.CAPACIDADE:
        ponte = 'CAPABILITY_BLOCK'
    elif plat in pc.ENFILAVEIS:
        ponte = 'ENFILAVEL'
    else:
        ponte = DESCONHECIDO
    original = wk._ficha_candidata
    wk._ficha_candidata = lambda _cid: {'TIPO': plat, 'PAIS': 'IT',
                                        'NOME': 'sonda SOC1', 'URL': ''}
    try:
        res, det = wk.etapa_qualify('CAND-SOC1-SONDA', None)
    finally:
        wk._ficha_candidata = original
    worker = res if res != 'BLOCK' else 'BLOCK/%s' % det.get('CLASSE')
    return ponte, worker


def credenciais_nos_workflows():
    """→ {nome: [workflows]} dos `secrets.X` declarados. Só nomes."""
    fora = {}
    for f in sorted(glob.glob(os.path.join(RAIZ, '.github', 'workflows', '*.yml'))):
        with open(f, encoding='utf-8', errors='replace') as fh:
            txt = fh.read()
        for n in sorted(set(re.findall(r'secrets\.([A-Z0-9_]+)', txt))):
            fora.setdefault(n, []).append(os.path.basename(f))
    return fora


def estado_da_credencial(nome, globais, ambiente=None):
    """LOCAL_CREDENTIAL_STATE / GLOBAL / SECRET_WIRING_GAP — sem o valor."""
    amb = os.environ if ambiente is None else ambiente
    local = 'PRESENT_LOCAL' if amb.get(nome) else 'ABSENT_LOCAL'
    wfs = globais.get(nome) or []
    glob_ = 'DECLARED_IN_WORKFLOW' if wfs else 'NOT_IN_ANY_WORKFLOW'
    return {'NOME': nome, 'LOCAL': local, 'GLOBAL': glob_, 'WORKFLOWS': wfs,
            # Ninguém nesta máquina consegue ver se o secret está PREENCHIDO no
            # GitHub (gh sem sessão). Declarado no workflow != preenchido.
            'SECRET_PREENCHIDO_NO_GITHUB': 'NAO_SEI',
            'SECRET_WIRING_GAP': 'NAO' if wfs else 'SIM'}


def classificar(l):
    """A prontidão desta prova. Cada ramo diz porquê; nenhum adivinha.

    A ordem é a da pergunta do dono: primeiro a POLÍTICA (a lei não se contorna
    com engenharia), depois o CAMINHO, depois a CREDENCIAL, depois a FASE.
    """
    rotas = l['ROTAS']
    livres_sim = [r for r in rotas if r['TIPO'] in GRATIS and r['PERMITIDA_NA_MATRIZ'] == 'SIM']
    if l['PORTA_PONTE'] == 'POLICY_BLOCK':
        return ROUTE_NOT_ALLOWED
    if rotas and not any(r['PERMITIDA_NA_MATRIZ'] in ('SIM', 'CONDICIONAL') for r in rotas):
        return ROUTE_NOT_ALLOWED
    if not l['EDGE_EXISTS']:
        return FAIL_CLOSED
    if l['CHECK_STATE'] == 'CREDENTIAL_MISSING':
        return READY_PENDING_CREDENTIAL
    if l['CAN'] is True and not l['FASES']:
        return PROVED_BUT_NOT_WIRED
    if l['CAN'] is True and livres_sim:
        return READY
    if l['CAN'] is True:
        # Corre, mas a única rota que corre não é grátis-e-permitida.
        return FAIL_CLOSED
    if l['CAN'] is None:
        return DESCONHECIDO
    return FAIL_CLOSED


def o_que_falta(l, globais=None):
    """→ lista curta do que separa esta capacidade de chegar à Sala, grátis."""
    f = []
    if l['PORTA_PONTE'] == 'POLICY_BLOCK':
        f.append('DONO: D15 POLICY_BLOCK na porta (termos proíbem); sai só com rota autorizada')
    tipos = {r['TIPO'] for r in l['ROTAS'] if r['PERMITIDA_NA_MATRIZ'] in ('SIM', 'CONDICIONAL')}
    if l['ROTAS'] and not (tipos & set(GRATIS)):
        f.append('NAO_EXISTE rota grátis permitida na matriz')
    if l['CHECK_STATE'] == 'CREDENTIAL_MISSING':
        nomes = sorted({r['CREDENCIAL'] for r in l['ROTAS'] if r['CREDENCIAL']})
        onde = sorted({w for n in nomes for w in (globais or {}).get(n, [])})
        # ⚠️ Declarada num workflow NÃO quer dizer que chega à fase: o
        # `scrap-social.yml` injecta a chave do YouTube e corre `social_scrap`,
        # que para no COLLECT; as fases canónicas (`scrap_colheita`) correm
        # pelo `sintonia-scrap.yml`, que não a injecta.
        f.append('CREDENCIAL: ausente neste shell; declarada só em %s'
                 % (', '.join(onde) or 'nenhum workflow'))
    if not l['EDGE_EXISTS']:
        f.append('ENGENHARIA: sem rota ligada no Scrap')
    elif not l['FASES']:
        f.append('ENGENHARIA: sem fase em scrap_colheita (ninguém a pede)')
    elif all(e != 'COLHEITA' for _n, e in l['FASES']):
        f.append('CATALOG: identidade/descoberta — não atravessa a porta de ingresso')
    if l['WORKER_QUALIFY'].startswith('BLOCK'):
        f.append('CURATOR: QUALIFY devolve %s — a candidata não chega à fase' % l['WORKER_QUALIFY'])
    return f


def avisos(l):
    """O que o dono tem de VER mesmo quando nada falta: a rota corre por
    autorização dele contra a política escrita da plataforma.

        OWNER_AUTHORIZED = SIM  +  PLATFORM_POLICY_STATUS = DISALLOWED
        AS DUAS FRASES CONVIVEM; NENHUMA APAGA A OUTRA.
    """
    return ['%s: dono autorizou (%s) e a plataforma diz %s'
            % (r['ROTA'], 'OWNER_AUTHORIZED=SIM', r['PLATFORM_POLICY_STATUS'])
            for r in l['ROTAS']
            if r['OWNER_AUTHORIZED'] == 'SIM'
            and r['PLATFORM_POLICY_STATUS'] not in (None, 'ALLOWED')]


def medir(ambiente=None):
    base = [l for l in sup.medir() if l['PLATFORM'] in PLATAFORMAS]
    globais = credenciais_nos_workflows()
    portas = {p: porta_da_candidata(p) for p in PLATAFORMAS}
    linhas = []
    for b in base:
        plat, capac = b['PLATFORM'], b['CAPABILITY']
        grossa, rotas = rotas_da_matriz(plat, capac)
        l = {
            'PLATFORM': plat, 'CAPABILITY': capac, 'MATRIZ_CAPABILITY': grossa,
            'DECLARED_STATE': b['DECLARED_STATE'],        # registo DECLARADAS
            'MODULE_EXISTS': b['MODULE_EXISTS'],          # registo EXECUTORES
            'EDGE_EXISTS': b['EDGE_EXISTS'],
            'FASES': fases_de(capac),                     # registo FASES
            'CHECK_STATE': b['CHECK_STATE'], 'CAN': b['CAN'],
            'V1_DA_SUPERFICIE': b['V1'],
            'ROTAS': rotas,
            'PORTA_PONTE': portas[plat][0], 'WORKER_QUALIFY': portas[plat][1],
        }
        l['PRONTIDAO'] = classificar(l)
        l['FALTA'] = o_que_falta(l, globais)
        l['AVISOS'] = avisos(l)
        linhas.append(l)
    nomes = sorted({r['CREDENCIAL'] for l in linhas for r in l['ROTAS']
                    if r['CREDENCIAL'] and r['CREDENCIAL'].isupper()})
    creds = [estado_da_credencial(n, globais, ambiente) for n in nomes]
    return {
        'DATASET': 'SOC1-PRONTIDAO-SOCIAL-V1',
        'MEDIDO_EM': datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
        'LEI': ('D16/D17: social é requisito da Big Collection; rota paga só como '
                'último recurso; nenhuma conta pessoal; YouTube pelas rotas que o '
                'Scrap declara. Esta matriz é MEDIDA no runtime, sem rede e sem gasto.'),
        'LINHAS': linhas, 'CREDENCIAIS': creds,
    }


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument('--json')
    a = ap.parse_args(argv)
    m = medir()
    print('SOC1 · PRONTIDÃO SOCIAL (LI/IG/YT) · medido %s' % m['MEDIDO_EM'])
    print('=' * 110)
    print('%-34s %-10s %-5s %-22s %-14s %-26s' % (
        'CAPABILITY', 'DECLARED', 'EDGE', 'CHECK', 'PORTA', 'PRONTIDAO'))
    print('-' * 110)
    for l in m['LINHAS']:
        print('%-34s %-10s %-5s %-22s %-14s %-26s' % (
            l['CAPABILITY'][:34], str(l['DECLARED_STATE'])[:10],
            'sim' if l['EDGE_EXISTS'] else '—', str(l['CHECK_STATE'])[:22],
            l['PORTA_PONTE'][:14], l['PRONTIDAO']))
        for f in l['FALTA']:
            print('      falta: %s' % f)
        for f in l['AVISOS']:
            print('      aviso: %s' % f)
    print('=' * 110)
    for c in m['CREDENCIAIS']:
        print('CREDENCIAL %-20s local=%-13s global=%-20s workflows=%s preenchido_no_github=%s'
              % (c['NOME'], c['LOCAL'], c['GLOBAL'], ','.join(c['WORKFLOWS']) or '—',
                 c['SECRET_PREENCHIDO_NO_GITHUB']))
    conta = {}
    for l in m['LINHAS']:
        conta[(l['PLATFORM'], l['PRONTIDAO'])] = conta.get((l['PLATFORM'], l['PRONTIDAO']), 0) + 1
    print()
    for (p, e), n in sorted(conta.items()):
        print('%-10s %-26s %d' % (p, e, n))
    if a.json:
        with open(a.json, 'w', encoding='utf-8', newline='\n') as fh:
            json.dump(m, fh, ensure_ascii=False, indent=1)
            fh.write('\n')
    return 0


if __name__ == '__main__':
    sys.exit(main())
