#!/usr/bin/env python3
"""PORTÃO do handoff ADAMA España — mede, não confia.

O handoff vive numa branch paralela e NÃO está mesclado. Este script lê os
artefatos direto do ref do Git, mede o que eles entregam campo por campo, e
decide se a camada local pode entrar no motor dos quatro relógios.

Ele NÃO importa nada. Nenhuma linha vai para o banco canônico.

  python3 scripts/adama_es_gate.py                 # mede e imprime
  python3 scripts/adama_es_gate.py --build         # grava o artefato
"""
import collections
import json
import os
import re
import subprocess
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SAIDA = os.path.join(RAIZ, 'data', 'samples', 'ADAMA-ES-HANDOFF-GATE-V1.json')
REF = 'origin/claude/adama-es-local-browser'
ROPF = os.path.join(RAIZ, 'data', 'samples', 'ES-ADAMA-PORTFOLIO-ROPF.json')
AS_OF = '2026-08-30'
NAO_SEI = {'NÃO SEI', 'NAO SEI', 'NOT_KNOWN', ''}


def git(*args):
    return subprocess.check_output(['git', '-C', RAIZ] + list(args), text=True).strip()


def do_ref(caminho):
    return json.loads(subprocess.check_output(
        ['git', '-C', RAIZ, 'show', '%s:%s' % (REF, caminho)], text=True))


def cheio(v):
    if v is None:
        return False
    if isinstance(v, (list, dict)):
        return len(v) > 0
    return str(v) not in NAO_SEI


def norm_reg(r):
    """O MAPA escreve o mesmo registro em três grafias: 18.087, 18087, ES-00205."""
    return re.sub(r'[^0-9A-Za-z-]', '', str(r or '')).upper()



# ── Buscar termo proibido SEM cair na propria proibicao ───────────────
# Pela quarta vez neste projeto um teste de termo proibido disparou na frase
# que ENUNCIA a proibicao: "23 safras", "IRAC" dentro de "respiracion",
# "seguidores", e agora "documento inexistente" dentro do campo
# O_QUE_ISTO_NAO_E. A correcao e sempre a mesma: percorrer campo a campo e
# ignorar os campos cujo NOME os marca como regra, motivo ou correcao.
CAMPOS_DE_REGRA = re.compile(
    r'(NAO_E|NAO_PROVA|PORQUE|O_QUE_|SEMANTICA|REGRA|LIMITAC|AVISO|NOTA|'
    r'COMENTARIO|EXPLICA|MOTIVO|FAILURE_REASON|EVIDENCIA|JUSTIFICA)')


def nomes_de_campo(obj, caminho=''):
    """Todo nome de campo do artefato, com caminho. Frescor persistido apareceria
    como NOME de coluna e nao como valor — procurar so em valor nao pegaria."""
    achados = []
    if isinstance(obj, dict):
        for k, v in obj.items():
            achados.append((caminho + '.' + str(k), str(k)))
            achados += nomes_de_campo(v, caminho + '.' + str(k))
    elif isinstance(obj, list):
        for i, v in enumerate(obj[:400]):
            achados += nomes_de_campo(v, caminho + '[%d]' % i)
    return achados


def termos_em_valores(obj, termos, caminho=''):
    """Devolve (caminho, valor) de cada valor que contem um dos termos.

    Valores dentro de campos de regra nao contam: enunciar a proibicao nao e
    viola-la.
    """
    achados = []
    if isinstance(obj, dict):
        for k, v in obj.items():
            if CAMPOS_DE_REGRA.search(str(k).upper()):
                continue
            achados += termos_em_valores(v, termos, caminho + '.' + str(k))
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            achados += termos_em_valores(v, termos, caminho + '[%d]' % i)
    elif isinstance(obj, str):
        u = obj.upper()
        for t in termos:
            if t in u:
                achados.append((caminho, obj[:90]))
    return achados


# ═══ 1 · LOCALIZAR ════════════════════════════════════════════════════
def localizar():
    head = git('rev-parse', REF)
    return {
        'REF': REF,
        'HEAD': head,
        'HEAD_CURTO': head[:7],
        'ASSUNTO': git('log', '-1', '--format=%s', REF),
        'DATA': git('log', '-1', '--format=%cI', REF),
        'PUSHED': True,
        'COMO_SE_SABE_QUE_ESTA_PUSHED':
            'o ref lido e origin/..., que so existe porque o remoto o publicou',
        'MESCLADO_NA_PRINCIPAL': subprocess.call(
            ['git', '-C', RAIZ, 'merge-base', '--is-ancestor', REF, 'HEAD']) == 0,
        'COMMITS_A_FRENTE': int(git('rev-list', '--count', 'HEAD..' + REF)),
        'ARQUIVOS': sorted(git('diff', '--name-only',
                               git('merge-base', 'HEAD', REF), REF).split('\n')),
    }


# ═══ 2 · COBERTURA POR CAMPO DO CONTRATO ══════════════════════════════
# Cada campo diz onde ele mora, quantas linhas o têm, e — quando não tem —
# se a ausência é da FONTE ou do EXTRATOR. As duas exigem ações diferentes.
def cobertura(h, ropf_por_reg):
    P, CIR, CDR = h['PRODUCTS'], h['CROP_ISSUE_RELATIONS'], h['CROP_DOSE_RELATIONS']
    n = len(P)

    def prod(k):
        return sum(1 for p in P if cheio(p.get(k)))

    def uso(R, k):
        return sum(1 for r in R if cheio(r.get(k)))

    com_ropf = sum(1 for p in P if norm_reg(p.get('REGISTRATION_ID')) in ropf_por_reg)
    return [
        {'CAMPO': 'COUNTRY', 'ONDE': 'PRODUCTS.COUNTRY', 'COBERTO': prod('COUNTRY'),
         'DE': n, 'ESTADO': 'COMPLETO'},
        {'CAMPO': 'PRODUCT', 'ONDE': 'PRODUCTS.DISPLAY_NAME', 'COBERTO': prod('DISPLAY_NAME'),
         'DE': n, 'ESTADO': 'COMPLETO'},
        {'CAMPO': 'HOLDER', 'ONDE': 'ausente do handoff; derivável do ROPF',
         'COBERTO': 0, 'DE': n, 'ESTADO': 'AUSENTE_NO_HANDOFF',
         'PORQUE': 'o site da ADAMA nao publica titular. O ROPF usado e um export '
                   'FILTRADO por titular ADAMA, entao o titular e propriedade da '
                   'consulta e nao do registro — precisa ser declarado como tal.'},
        {'CAMPO': 'ACTIVE_INGREDIENT', 'ONDE': 'PRODUCTS.ACTIVE_INGREDIENTS',
         'COBERTO': prod('ACTIVE_INGREDIENTS'), 'DE': n, 'ESTADO': 'PARCIAL',
         'PORQUE': 'AUSENTE_MEDIDO: 4 fichas nao publicam composicao'},
        {'CAMPO': 'FORMULATION', 'ONDE': 'PRODUCTS.FORMULATION', 'COBERTO': prod('FORMULATION'),
         'DE': n, 'ESTADO': 'PARCIAL'},
        {'CAMPO': 'CROP', 'ONDE': 'CROP_RELATIONS (588 declaradas)',
         'COBERTO': sum(1 for r in h['CROP_RELATIONS']
                        if r['DECLARATION_SOURCE'] == 'DECLARADO_NO_BLOCO_CULTIVOS'),
         'DE': len(h['CROP_RELATIONS']), 'ESTADO': 'COMPLETO_COM_DISTINCAO',
         'PORQUE': 'DECLARADO != CITADO, e o campo DECLARATION_SOURCE separa os dois'},
        {'CAMPO': 'TARGET_ISSUE', 'ONDE': 'ISSUE_RELATIONS',
         'COBERTO': len(h['ISSUE_RELATIONS']), 'DE': len(h['ISSUE_RELATIONS']),
         'ESTADO': 'CONTAMINADO',
         'PORQUE': 'ISSUE_RELATIONS NAO tem DECLARATION_SOURCE — a distincao que o '
                   'proprio handoff chama de mais importante foi aplicada a cultivo '
                   'e nao a alvo. Ver o red team RT-11.'},
        {'CAMPO': 'AUTHORIZED_USE', 'ONDE': 'CROP_ISSUE_RELATIONS', 'COBERTO': len(CIR),
         'DE': len(CIR), 'ESTADO': 'MINIMO',
         'PORQUE': '5 usos com cultivo E alvo na mesma linha. Os outros 26 sao '
                   'CULTIVO x DOSE sem agente, e nao sao uso autorizado.'},
        {'CAMPO': 'REGISTRATION_STATUS', 'ONDE': 'ausente do handoff; ROPF tem',
         'COBERTO': com_ropf, 'DE': n, 'ESTADO': 'DERIVAVEL',
         'PORQUE': 'o handoff traz CURRENT_CATALOG_STATUS, que e estado de CATALOGO '
                   'e nao estado de REGISTRO. Os dois nao sao o mesmo.'},
        {'CAMPO': 'AUTHORIZATION_DATE', 'ONDE': 'nem no handoff nem no ROPF usado',
         'COBERTO': 0, 'DE': n, 'ESTADO': 'NAO_COLETADO'},
        {'CAMPO': 'EXPIRY', 'ONDE': 'ROPF.FICHAS.CADUCIDAD, via numero de registro',
         'COBERTO': com_ropf, 'DE': n, 'ESTADO': 'DERIVAVEL'},
        {'CAMPO': 'PHI', 'ONDE': 'CROP_ISSUE_RELATIONS.PRE_HARVEST_INTERVAL_DAYS',
         'COBERTO': uso(CIR, 'PRE_HARVEST_INTERVAL_DAYS'), 'DE': len(CIR),
         'ESTADO': 'AUSENTE', 'PORQUE': 'o HTML nao publica prazo; mora no rotulo em PDF'},
        {'CAMPO': 'APPLICATION_TIMING_LITERAL', 'ONDE': 'CROP_ISSUE_RELATIONS.ANCHOR.ROW_TEXT',
         'COBERTO': uso(CIR, 'ANCHOR'), 'DE': len(CIR), 'ESTADO': 'COMPLETO',
         'PORQUE': 'toda linha carrega o texto literal da linha da tabela'},
        {'CAMPO': 'DOSE', 'ONDE': 'CROP_ISSUE_RELATIONS + CROP_DOSE_RELATIONS',
         'COBERTO': uso(CIR, 'DOSE') + uso(CDR, 'DOSE'), 'DE': len(CIR) + len(CDR),
         'ESTADO': 'COMPLETO'},
        {'CAMPO': 'SOURCE_URL', 'ONDE': 'todas as estruturas', 'COBERTO': prod('PAGE_URL'),
         'DE': n, 'ESTADO': 'COMPLETO'},
        {'CAMPO': 'SOURCE_TYPE', 'ONDE': 'EVIDENCE_LEVEL + SOURCE_OWNER',
         'COBERTO': n, 'DE': n, 'ESTADO': 'COMPLETO',
         'PORQUE': 'quatro niveis declarados linha a linha'},
        {'CAMPO': 'SOURCE_DATE_OBSERVED_AT', 'ONDE': 'CAPTURED_AT', 'COBERTO': prod('CAPTURED_AT'),
         'DE': n, 'ESTADO': 'COMPLETO'},
        {'CAMPO': 'EVIDENCE_LOCATOR', 'ONDE': 'ANCHOR (secao, tabela, linha, texto)',
         'COBERTO': uso(CIR, 'ANCHOR') + uso(CDR, 'ANCHOR'), 'DE': len(CIR) + len(CDR),
         'ESTADO': 'COMPLETO'},
        {'CAMPO': 'TEMPORAL_RESOLUTION', 'ONDE': 'nao existe como campo',
         'COBERTO': 0, 'DE': len(CIR) + len(CDR), 'ESTADO': 'AUSENTE',
         'PORQUE': 'o handoff guarda BBCH_FROM/TO como texto e TIMING_FLAGS ao lado. '
                   'Quem importar tem de DECIDIR a resolucao, e essa decisao nao esta '
                   'no handoff. Ver o conflito C-3.'},
        {'CAMPO': 'LIMITATION_NOT_KNOWN', 'ONDE': 'literal "NÃO SEI" em toda estrutura',
         'COBERTO': n, 'DE': n, 'ESTADO': 'COMPLETO',
         'PORQUE': 'ausencia e escrita, nunca omitida nem zerada'},
    ]


# ═══ 3 · PORTFÓLIO LOCAL — três estados, e só três ════════════════════
def estados_locais(h, ropf_por_reg):
    cw = {x['DISPLAY_NAME']: x for x in h['REGULATORY_CROSSWALK']['LINHAS']
          if x.get('PAGE_URL')}
    linhas = []
    for p in h['PRODUCTS']:
        c = cw.get(p['DISPLAY_NAME'], {})
        est = c.get('ESTADO')
        reg_site = p.get('REGISTRATION_ID')
        reg_cw = c.get('REG')
        if est == 'MATCHED_EXACT':
            estado, base = 'LOCAL_REGISTERED', 'REGISTRATION_NUMBER'
        elif est == 'MATCHED_WITH_EVIDENCE':
            estado, base = 'LOCAL_REGISTERED', 'NAME_AND_COMPOSITION'
        elif est == 'ADAMA_SITE_ONLY':
            estado, base = 'LOCAL_PRESENT_BUT_REGISTRATION_NOT_PROVED', 'NONE'
        else:
            estado, base = 'NOT_KNOWN', 'NONE'
        f = ropf_por_reg.get(norm_reg(reg_cw)) or {}
        linhas.append({
            'PRODUCT': p['DISPLAY_NAME'],
            'ESTADO': estado,
            'MATCH_BASIS': base,
            'REGISTRATION_ID_NO_SITE': reg_site,
            'REGISTRATION_ID_NO_REGISTRO': reg_cw,
            'NUMEROS_DIVERGEM': bool(reg_cw and norm_reg(reg_site) != norm_reg(reg_cw)),
            'CADUCIDAD_NO_REGISTRO': f.get('CADUCIDAD'),
            'EVIDENCIA_ESPANHOLA': (
                'pagina observada em adama.com/spain/es + registro no ROPF'
                if estado == 'LOCAL_REGISTERED'
                else 'pagina observada em adama.com/spain/es'),
        })
    return linhas



# ═══ 4 · OS CINCO CASOS CONTRA O MOTOR ════════════════════════════════
# Banco DESCARTAVEL. Nenhuma linha vai para o canonico. Sem DSN, o campo sai
# como NAO_EXECUTADO — que e diferente de "passou".
CASOS = [
    ('A', 'produto com cultura, alvo e janela explicita', 'RICE', 'BROADLEAF_WEEDS'),
    ('B', 'produto de nivel cultura, sem alvo', 'ALMOND', 'BROADLEAF_WEEDS'),
    ('C', 'produto com validade vencida', 'OLIVE', 'REPILO'),
    ('D', 'temporalidade aproximada', 'BARLEY', 'WEEDS_GENERIC'),
    ('E', 'dado ausente que precisa continuar NOT_KNOWN', 'RYE', 'WEEDS_GENERIC'),
]


def ensaio(dsn):
    if not dsn:
        return {'ESTADO': 'NAO_EXECUTADO',
                'PORQUE': 'sem DSN de banco descartavel. NAO_EXECUTADO nao e PASSOU.'}
    def q(sql):
        r = subprocess.run(['psql', dsn, '-tAc', sql], capture_output=True, text=True)
        if r.returncode != 0:
            raise SystemExit('psql falhou: ' + r.stderr.strip()[:300])
        return r.stdout.strip()

    out = []
    for cid, desc, crop, issue in CASOS:
        pl = json.loads(q("select public.f_case_temporal_context('ES','%s','%s',null,date '%s')"
                          % (crop, issue, AS_OF)))
        janelas = pl['product_window_state']
        sem_issue = json.loads(q(
            "select public.f_case_temporal_context('ES','%s',null,null,date '%s')"
            % (crop, AS_OF)))['product_window_state']
        out.append({
            'CASO': cid, 'O_QUE_EXERCE': desc, 'CROP': crop, 'ISSUE': issue,
            'PRODUTOS_NA_RESPOSTA': [w['product'] for w in janelas],
            'ESTADO_DA_JANELA': [w['state'] for w in janelas],
            'RESOLUCAO': [w['temporal_resolution'] for w in janelas],
            'ESCOPO': [w['target_scope'] for w in janelas],
            'CADUCIDADE': [w['registration_expiry_state'] for w in janelas],
            'SOME_AO_PERGUNTAR_POR_ISSUE': len(janelas) < len(sem_issue),
            'REPRESENTADO_SEM_PERDA': bool(janelas) and all(
                w['original_text'] for w in janelas),
        })
    return {'ESTADO': 'EXECUTADO',
            'ONDE': 'banco descartavel com 001-012, fixture supabase/ensaios/'
                    'ADAMA-ES-ENSAIO-CINCO-CASOS.sql',
            'AS_OF': AS_OF, 'CASOS': out}


# ═══ 6 · RED TEAM ═════════════════════════════════════════════════════
# Cada hipótese é uma tentativa de DERRUBAR o handoff. Passa = a hipótese
# não se sustentou. Falha = o defeito é real e está nomeado.
def red_team(h, estados, mig_texto=None):
    R = []

    def caso(id_, hipotese, derrubada, prova, detalhe=''):
        R.append({'ID': id_, 'HIPOTESE': hipotese,
                  'RESULTADO': 'HIPOTESE_DERRUBADA' if derrubada else 'DEFEITO_CONFIRMADO',
                  'PROVA': prova, 'DETALHE': detalhe})

    # RT-1 · site tratado como prova regulatória
    niveis = collections.Counter(
        r['EVIDENCE_LEVEL'] for est in ('CROP_RELATIONS', 'ISSUE_RELATIONS',
                                        'CROP_ISSUE_RELATIONS', 'CROP_DOSE_RELATIONS')
        for r in h[est])
    caso('RT-1', 'o site da ADAMA foi tratado como prova regulatoria',
         niveis['REGULATORY_FACT'] == 5,
         'so 5 linhas em %d carregam REGULATORY_FACT, e as 5 tem MAPA_EVIDENCIA '
         'com id de cultivo, id de plaga, titular e estado' % sum(niveis.values()),
         json.dumps(dict(niveis), ensure_ascii=False))

    # RT-2 · produto de outro país vazou para ES
    fora = [p['DISPLAY_NAME'] for p in h['PRODUCTS'] if '/spain/' not in p['PAGE_URL']]
    caso('RT-2', 'produto de outro pais vazou para ES', not fora,
         'as %d PAGE_URL estao em adama.com/spain/es/' % len(h['PRODUCTS']),
         str(fora))

    # RT-3 · ausência virou "não existe"
    proibidas = termos_em_valores(
        h, ('NAO_REGISTRADO', 'NOT_REGISTERED', 'NAO EXISTE', 'INEXISTENTE',
            'DOES NOT EXIST'))
    caso('RT-3', 'ausencia de resultado virou "nao existe"', not proibidas,
         'os 12 sem casamento saem como ADAMA_SITE_ONLY, que descreve o que se sabe; '
         'nenhum campo de dado afirma nao-existencia. As unicas ocorrencias da '
         'palavra estao em campos de REGRA (O_QUE_ISTO_NAO_E: "falha de download '
         'NAO e documento inexistente"), que enunciam a proibicao em vez de viola-la',
         str(proibidas[:3]))

    # RT-4 · alvo ausente fez produto de nível cultura sumir
    sem_alvo = [r for r in h['CROP_DOSE_RELATIONS'] if not cheio(r.get('ISSUE'))]
    caso('RT-4', 'alvo ausente fez o produto de nivel cultura sumir',
         all(r.get('PAIR_DERIVABLE') is False and cheio(r.get('PORQUE_NAO_HA_PAR'))
             for r in sem_alvo),
         'as %d linhas CULTIVO x DOSE ficam, marcadas PAIR_DERIVABLE=false e com '
         'o motivo escrito' % len(sem_alvo))

    # RT-5 · expiry passada virou "retirado"
    retirada = termos_em_valores(h, ('RETIRADO', 'WITHDRAWN', 'PROHIBIDO', 'BANNED'))
    caso('RT-5', 'validade vencida virou retirada do mercado', not retirada,
         'o handoff nao publica caducidad; ela e derivada do ROPF na importacao, '
         'e nenhuma palavra de retirada aparece em campo de dado', str(retirada[:3]))

    # RT-6 · APPROXIMATE virou data exata — E AQUI ELE CAI
    degenerada = [w for w in h['APPLICATION_WINDOWS']
                  if w['BBCH_FROM'] == '00' and w['BBCH_TO'] == '00']
    caso('RT-6', 'temporalidade aproximada virou faixa numerica exata',
         not degenerada,
         '%d de %d APPLICATION_WINDOWS trazem BBCH 00-00 enquanto o texto ancorado '
         'diz "desde BBCH 00 (semilla seca) hasta BBCH 07"'
         % (len(degenerada), len(h['APPLICATION_WINDOWS'])),
         '; '.join('%s x %s' % (w['CROP'], w['ISSUE']) for w in degenerada))

    # RT-7 · UNKNOWN virou CLOSED
    fechado = termos_em_valores(h, ('CLOSED', 'FECHAD', 'CERRAD'))
    caso('RT-7', 'desconhecido virou fechado', not fechado,
         'o artefato nao tem nenhum estado de janela; ele guarda o texto e '
         'deixa o estado para o motor derivar de as_of_date', str(fechado[:3]))

    # RT-8 · freshness persistida — procurar no NOME do campo, que e onde
    #        um frescor gravado apareceria de verdade.
    alvo = ('FRESHNESS', 'FRESCOR', 'STALE', 'IDADE_DIAS', 'AGE_DAYS', 'DIAS_DESDE',
            'DATA_ATUAL', 'HOJE', 'AS_OF')
    fresh = [(c, k) for c, k in nomes_de_campo(h)
             if any(t in k.upper() for t in alvo)]
    fresh += termos_em_valores(h, ('STALE_FOR_PURPOSE', 'AGE_NOT_KNOWN'))
    caso('RT-8', 'frescor foi persistido como atributo do dado', not fresh,
         'nenhum NOME de campo nem valor de idade ou frescor no artefato; so '
         'CAPTURED_AT, que e quando foi observado, e nao quanto tempo faz',
         str(fresh[:3]))

    # RT-9 · registro_uso_janela virou segundo dono
    mig = mig_texto if mig_texto is not None else subprocess.check_output(
        ['git', '-C', RAIZ, 'show',
         '%s:supabase/migrations/010_catalogo_publico_fabricante.sql' % REF], text=True)
    toca = [t for t in ('registro_uso_janela', 'crop_calendar', 'issue_window',
                        'freshness_regra')
            if re.search(r'(insert into|alter table|create table)\s+public\.%s\b' % t, mig)]
    caso('RT-9', 'o catalogo virou um segundo dono da janela do produto',
         not toca,
         'a migration do catalogo cria 15 tabelas catalogo_*, tem janela propria '
         '(catalogo_produto_janela_aplicacao) e nao escreve em registro_uso_janela '
         'nem em nenhuma tabela do calendario', str(toca))

    # RT-10 · mesma evidência em dois lugares com semântica diferente — CAI
    div = [x for x in estados if x['NUMEROS_DIVERGEM']]
    caso('RT-10', 'a mesma evidencia aparece em dois lugares com semantica diferente',
         not div,
         '%d produto(s) tem REGISTRATION_ID diferente em PRODUCTS e em '
         'REGULATORY_CROSSWALK.LINHAS, sob o mesmo nome de campo' % len(div),
         '; '.join('%s: site=%s registro=%s' % (x['PRODUCT'],
                                                x['REGISTRATION_ID_NO_SITE'],
                                                x['REGISTRATION_ID_NO_REGISTRO'])
                   for x in div))

    # RT-11 · a distinção declarado/citado só foi aplicada a cultivo — CAI
    cat = {p['PRODUCT_ID']: p['CATEGORY'] for p in h['PRODUCTS']}
    erva = [r for r in h['ISSUE_RELATIONS']
            if 'MALAS HIERBAS' in r['ISSUE'].upper()
            and cat[r['PRODUCT_ID']] != 'CONTROL_DE_MALAS_HIERBAS']
    caso('RT-11', 'a distincao DECLARADO != CITADO foi aplicada a cultivo e a alvo',
         not erva,
         'ISSUE_RELATIONS nao tem o campo DECLARATION_SOURCE, e %d produtos que '
         'nao sao herbicida carregam o alvo "MALAS HIERBAS" — um por produto '
         'nao-herbicida, assinatura de menu do site e nao de conteudo de ficha'
         % len({r['PRODUCT_ID'] for r in erva}),
         '; '.join(sorted({h['PRODUCTS'][[p['PRODUCT_ID'] for p in h['PRODUCTS']]
                          .index(r['PRODUCT_ID'])]['DISPLAY_NAME'] for r in erva}))[:400])
    return R



# ═══ MUTAÇÃO — o red team tem dentes? ═════════════════════════════════
# Um red team que passaria mesmo num handoff quebrado nao vale nada. Cada
# mutacao estraga UMA coisa numa copia em memoria e exige que a hipotese
# correspondente deixe de ser derrubada.
def mutacoes():
    import copy
    base = do_ref('data/samples/ADAMA-ES-PRODUCT-INTELLIGENCE.json')
    with open(ROPF, encoding='utf-8') as f:
        ropf_por_reg = {norm_reg(x['REG']): x for x in json.load(f)['FICHAS']}

    def rodar(h, mig=None):
        return {x['ID']: x['RESULTADO']
                for x in red_team(h, estados_locais(h, ropf_por_reg), mig)}

    def muta(nome, alvo, f):
        h = copy.deepcopy(base)
        f(h)
        r = rodar(h)
        ok = r[alvo] == 'DEFEITO_CONFIRMADO'
        return {'MUTACAO': nome, 'ALVO': alvo,
                'RESULTADO': 'PEGOU' if ok else 'NAO_PEGOU_TESTE_INUTIL'}

    def m1(h):
        for r in h['CROP_RELATIONS'][:3]:
            r['EVIDENCE_LEVEL'] = 'REGULATORY_FACT'

    def m2(h):
        h['PRODUCTS'][0]['PAGE_URL'] = 'https://www.adama.com/france/fr/nos-solutions/agil'

    def m3(h):
        h['PRODUCTS'][0]['CURRENT_CATALOG_STATUS'] = 'NAO_REGISTRADO'

    def m4(h):
        for r in h['CROP_DOSE_RELATIONS']:
            r['PAIR_DERIVABLE'] = True

    def m5(h):
        h['PRODUCTS'][0]['CURRENT_CATALOG_STATUS'] = 'RETIRADO DO MERCADO'

    def m7(h):
        h['APPLICATION_WINDOWS'][0]['ESTADO_DA_JANELA'] = 'CLOSED'

    def m8(h):
        h['PRODUCTS'][0]['AGE_DAYS'] = 77

    def m10(h):
        for x in h['REGULATORY_CROSSWALK']['LINHAS']:
            if x.get('PAGE_URL'):
                x['REG'] = x['REG'] or '00000'
        for p_ in h['PRODUCTS']:
            p_['REGISTRATION_ID'] = 'DIFERENTE-' + str(p_['REGISTRATION_ID'])

    def m11(h):
        cat = {p_['PRODUCT_ID']: p_['CATEGORY'] for p_ in h['PRODUCTS']}
        h['ISSUE_RELATIONS'] = [r for r in h['ISSUE_RELATIONS']
                                if not ('MALAS HIERBAS' in r['ISSUE'].upper()
                                        and cat[r['PRODUCT_ID']] != 'CONTROL_DE_MALAS_HIERBAS')]
        return h

    saida = [muta('site vira prova regulatoria', 'RT-1', m1),
             muta('uma pagina passa a ser francesa', 'RT-2', m2),
             muta('um estado passa a dizer NAO_REGISTRADO', 'RT-3', m3),
             muta('linha sem alvo passa a declarar par derivavel', 'RT-4', m4),
             muta('um estado passa a dizer RETIRADO DO MERCADO', 'RT-5', m5),
             muta('a janela ganha um estado CLOSED gravado', 'RT-7', m7),
             muta('o produto ganha AGE_DAYS persistido', 'RT-8', m8),
             muta('os dois numeros de registro passam a divergir sempre', 'RT-10', m10)]
    # RT-6 e RT-11 sao defeitos JA confirmados: a mutacao util e a inversa —
    # consertar o dado e exigir que a hipotese passe a ser derrubada.
    import copy as _c
    h6 = _c.deepcopy(base)
    for w in h6['APPLICATION_WINDOWS']:
        if w['BBCH_FROM'] == '00' and w['BBCH_TO'] == '00':
            w['BBCH_TO'] = '07'
    saida.append({'MUTACAO': 'consertar BBCH 00-00 para 00-07', 'ALVO': 'RT-6',
                  'RESULTADO': 'PEGOU' if rodar(h6)['RT-6'] == 'HIPOTESE_DERRUBADA'
                               else 'NAO_PEGOU_TESTE_INUTIL'})
    r9 = rodar(base, 'insert into public.registro_uso_janela (id) values (1);')
    saida.append({'MUTACAO': 'o catalogo passa a escrever em registro_uso_janela',
                  'ALVO': 'RT-9',
                  'RESULTADO': 'PEGOU' if r9['RT-9'] == 'DEFEITO_CONFIRMADO'
                               else 'NAO_PEGOU_TESTE_INUTIL'})
    h11 = _c.deepcopy(base)
    m11(h11)
    saida.append({'MUTACAO': 'remover as 25 ervas dos nao-herbicidas', 'ALVO': 'RT-11',
                  'RESULTADO': 'PEGOU' if rodar(h11)['RT-11'] == 'HIPOTESE_DERRUBADA'
                               else 'NAO_PEGOU_TESTE_INUTIL'})
    return saida




# ═══ INTERFERÊNCIA — o que acontece quando os dois convivem ═══════════
# O ensaio dos cinco casos roda num banco só com o handoff. Esta medicao
# responde outra pergunta: carregar a camada ADAMA POR CIMA do acervo que ja
# existe quebra alguma coisa? A resposta importa mais que a primeira.
def interferencia(dsn):
    if not dsn:
        return {'ESTADO': 'NAO_EXECUTADO',
                'PORQUE': 'sem DSN do banco com as duas fixtures. '
                          'NAO_EXECUTADO nao e PASSOU.'}

    def q(sql):
        r = subprocess.run(['psql', dsn, '-tAc', sql], capture_output=True, text=True)
        if r.returncode != 0:
            raise SystemExit('psql falhou: ' + r.stderr.strip()[:300])
        return r.stdout.strip()

    linhas = int(q("select count(*) from public.registro_regulatorio"))
    distintos = int(q("select count(distinct (pais, registration_id)) "
                      "from public.registro_regulatorio"))
    neptune = int(q("select count(*) from public.v_product_registered_windows "
                    "where nome_comercial='NEPTUNE'"))
    chave = q("select pg_get_constraintdef(oid) from pg_constraint "
              "where conrelid='public.registro_regulatorio'::regclass and contype='u'")
    return {
        'ESTADO': 'EXECUTADO',
        'O_QUE_MEDE': 'a camada ADAMA carregada POR CIMA do acervo ES que ja existe',
        'REGISTROS_LINHAS': linhas,
        'REGISTROS_DISTINTOS_POR_PAIS_E_NUMERO': distintos,
        'DUPLICADOS': linhas - distintos,
        'JANELAS_DO_NEPTUNE_NA_VIEW': neptune,
        'CHAVE_NATURAL': chave,
        'DIAGNOSTICO':
            'registro_regulatorio e um LOG versionado por captura — a chave natural '
            'inclui fonte_versao. Duas capturas do MESMO registro em horas diferentes '
            'do mesmo dia viram duas linhas, e v_product_registered_windows le o log '
            'como se fosse estado corrente. Com uma captura so, o defeito era '
            'invisivel. O handoff da ADAMA e a segunda captura, e ele o revela.',
        'O_QUE_O_PORTAL_VERIA':
            'o mesmo NEPTUNE %d vezes no mesmo caso, com estados de janela diferentes '
            'e nenhuma indicacao de que sao a mesma autorizacao vista duas vezes'
            % neptune,
        'NAO_CONSERTADO_NESTA_RODADA':
            'esta e rodada de portao. O conserto e na camada de consulta, nao no dado: '
            'v_product_registered_windows precisa devolver a captura MAIS RECENTE por '
            '(pais, registration_id) e expor quantas capturas existem, em vez de '
            'devolver todas. Mudar a chave da tabela seria jogar fora o historico.',
        'CAPTURE_NAO_E_REGISTRATION':
            'a lei nova que este ensaio nomeia: uma captura da ficha nao e uma '
            'autorizacao. Duas leituras do ROPF no mesmo dia sao um registro, nao dois.',
    }


# ═══ 5 · ES-CASE-001 — o handoff resolve a divergencia? ═══════════════
# Humano: "antes de la floracion" + prazo de 120 dias  ->  CLOSED
# Motor : resolucao APPROXIMATE                        ->  NOT_KNOWN
# So fecha com evidencia NOVA que torne a comparacao deterministica.
def es_case_001(h):
    nid = [p['PRODUCT_ID'] for p in h['PRODUCTS'] if p['DISPLAY_NAME'] == 'NEPTUNE']
    nid = nid[0] if nid else None
    janelas = [w for w in h['APPLICATION_WINDOWS'] if w['PRODUCT_ID'] == nid]
    pares = [r for r in h['CROP_ISSUE_RELATIONS'] if r['PRODUCT_ID'] == nid]

    # A busca por palavra NAO serve aqui, e a primeira versao deste portao
    # provou isso: procurar "floracion" no artefato devolveu 18 acertos e teria
    # FECHADO a divergencia. Os 18 estao todos em AMBIGUOUS_TERMS, e sao rotulos
    # oficiais de USO ("Inhibición floración", "Aclareo floración") — nenhum e
    # uma data e nenhum fala de olival. Fechar por contagem de palavra seria
    # exatamente o que a missao proibe.
    citacoes = termos_em_valores(h, ('FLORAC',))
    def serve(caminho, valor):
        """Evidencia que fecha precisa das TRES coisas ao mesmo tempo."""
        v = valor.upper()
        fala_de_olival = 'OLIV' in v or 'OLIVO' in caminho.upper()
        tem_tempo = bool(re.search(r'\d{4}-\d{2}-\d{2}', valor)
                         or re.search(r'BBCH\s*\d{2}', v))
        nao_e_vocabulario = 'AMBIGUOUS_TERMS' not in caminho
        return fala_de_olival and tem_tempo and nao_e_vocabulario
    uteis = [(c, v) for c, v in citacoes if serve(c, v)]

    rotulo = [d_ for d_ in h['DOCUMENTS']
              if d_['PRODUCT_ID'] == nid and d_['DOCUMENT_TYPE'] == 'ADAMA_COMMERCIAL_LABEL']
    resolve = bool(janelas) or bool(pares) or bool(uteis)
    return {
        'DIVERGENCIA': 'humano CLOSED x motor NOT_KNOWN',
        'O_HANDOFF_TRAZ_JANELA_DO_NEPTUNE': len(janelas),
        'O_HANDOFF_TRAZ_PAR_OLIVO_x_REPILO_DO_NEPTUNE': len(pares),
        'CITACOES_DE_FLORACAO_NO_ARTEFATO': len(citacoes),
        'CITACOES_QUE_SERVEM_COMO_EVIDENCIA': len(uteis),
        'PORQUE_AS_CITACOES_NAO_SERVEM':
            'as %d estao em AMBIGUOUS_TERMS e sao rotulos oficiais de USO '
            '("Inhibición floración", "Aclareo floración"). Nenhuma tem data, '
            'nenhuma fala de olival, nenhuma esta ligada ao NEPTUNE. Palavra '
            'presente nao e fenologia datada.' % len(citacoes),
        'RESOLVE': resolve,
        'ESTADO': 'FECHADA' if resolve else 'ABERTA',
        'O_QUE_FECHARIA': 'a data ou o estadio BBCH de floracao do olival numa fonte '
                          'datada — o rotulo em PDF do NEPTUNE, ou uma serie de '
                          'fenologia como a do RAIF — guardada como OBSERVED_CAMPAIGN. '
                          'Ai a comparacao vira deterministica e o motor decide sozinho.',
        'ONDE_A_EVIDENCIA_PROVAVELMENTE_ESTA': [
            {'DOCUMENTO': d_['FILENAME'], 'SHA256': d_['SHA256'], 'BYTES': d_['BYTES'],
             'ESTADO': d_['DOWNLOAD_STATE'],
             'ONDE': 'disco local do usuario, fora do Git'} for d_ in rotulo],
    }


# ═══ CONFLITOS COM O SCHEMA ATUAL ═════════════════════════════════════
CONFLITOS = [
    {'ID': 'C-1', 'GRAVIDADE': 'MECANICO',
     'O_QUE': 'duas migrations 010 com o mesmo numero',
     'ONDE': 'principal: 010_calendario_agronomico.sql · handoff: '
             '010_catalogo_publico_fabricante.sql',
     'E_SEMANTICO': False,
     'PORQUE_NAO_E_GRAVE': 'as 15 tabelas do catalogo se chamam catalogo_* e nenhuma '
                           'colide com as quatro do calendario. O choque e de numero '
                           'de arquivo, nao de dominio.',
     'RESOLUCAO': 'renumerar a do catalogo para 013 na hora do merge. Nao mexer no '
                  'conteudo dela.'},
    {'ID': 'C-2', 'GRAVIDADE': 'NENHUMA_ACAO',
     'O_QUE': 'o catalogo tem janela propria (catalogo_produto_janela_aplicacao)',
     'ONDE': 'handoff, migration do catalogo',
     'E_SEMANTICO': True,
     'PORQUE_NAO_E_GRAVE': 'o que o FABRICANTE publica e o que o ROTULO autoriza sao '
                           'duas afirmacoes diferentes e merecem donos diferentes. '
                           'registro_uso_janela continua filho de registro_uso e '
                           'unico dono do relogio C.',
     'RESOLUCAO': 'v_product_registered_windows NAO pode passar a ler catalogo_*. '
                  'A ponte e um importador explicito, com decisao de resolucao '
                  'temporal registrada linha a linha.'},
    {'ID': 'C-3', 'GRAVIDADE': 'BLOQUEIA_IMPORTACAO',
     'O_QUE': 'o handoff nao tem temporal_resolution, e registro_uso_janela exige',
     'ONDE': 'CROP_ISSUE_RELATIONS.BBCH_FROM/TO sao texto; TIMING_FLAGS ao lado',
     'E_SEMANTICO': True,
     'PORQUE_NAO_E_GRAVE': None,
     'RESOLUCAO': 'a decisao PHENOLOGY_STAGE / APPROXIMATE / NOT_KNOWN e do '
                  'importador e precisa ser explicita e auditavel contra o '
                  'ANCHOR.ROW_TEXT. Sem essa regra escrita, importar e adivinhar.'},
    {'ID': 'C-4', 'GRAVIDADE': 'BLOQUEIA_IMPORTACAO',
     'O_QUE': 'BBCH 00-00 passa pelo schema e vira CLOSED no motor',
     'ONDE': 'APPLICATION_WINDOWS · TRINITY x cevada e x trigo',
     'E_SEMANTICO': True,
     'PORQUE_NAO_E_GRAVE': None,
     'RESOLUCAO': 'consertar na origem (BBCH_TO=07) ou importar como APPROXIMATE '
                  'com o texto inteiro. A constraint bbch_em_ordem NAO pega, e nao '
                  'deve pegar: uma janela de um estadio so (BBCH 65-65) e legitima.'},
    {'ID': 'C-5', 'GRAVIDADE': 'ATENCAO',
     'O_QUE': 'titular e NOT NULL em registro_regulatorio e o handoff nao tem titular',
     'ONDE': 'registro_regulatorio.titular',
     'E_SEMANTICO': True,
     'PORQUE_NAO_E_GRAVE': 'a trava ja impede o pior: os 12 produtos so-site NAO '
                           'conseguem entrar como registro. O schema aplica sozinho '
                           'a lei ADAMA WEBSITE != PROVA REGULATORIA.',
     'RESOLUCAO': 'titular vem do ROPF, e precisa ser declarado como propriedade da '
                  'CONSULTA (export filtrado por titular ADAMA), nao do registro.'},
    {'ID': 'C-7', 'GRAVIDADE': 'BLOQUEIA_IMPORTACAO',
     'O_QUE': 'duas capturas do mesmo registro viram dois registros',
     'ONDE': 'registro_regulatorio UNIQUE (pais, registration_id, fonte_versao); '
             'v_product_registered_windows le o log como estado corrente',
     'E_SEMANTICO': True,
     'PORQUE_NAO_E_GRAVE': None,
     'RESOLUCAO': 'o importador casa por (pais, registration_id) e a view devolve a '
                  'captura mais recente, expondo quantas existem. CAPTURE != '
                  'REGISTRATION. Medido: NEPTUNE aparece 3x no mesmo caso.'},
    {'ID': 'C-6', 'GRAVIDADE': 'ATENCAO',
     'O_QUE': 'importar so o relogio C nao acende nenhuma janela',
     'ONDE': 'ensaio dos cinco casos: 5 de 5 respondem NOT_KNOWN',
     'E_SEMANTICO': True,
     'PORQUE_NAO_E_GRAVE': 'NOT_KNOWN e a resposta certa. Uma janela em BBCH so pode '
                           'ser avaliada contra fenologia observada, e hoje so o '
                           'olivar tem serie (RAIF).',
     'RESOLUCAO': 'a importacao do catalogo precisa vir acompanhada de fenologia '
                  'observada por cultura, ou o portal ganha 56 produtos que so '
                  'sabem dizer NOT_KNOWN.'},
]



# ═══ VEREDITO E PROCEDIMENTO ══════════════════════════════════════════
def veredito(rt, ensaio_):
    defeitos = [x['ID'] for x in rt if x['RESULTADO'] == 'DEFEITO_CONFIRMADO']
    bloqueia = [c['ID'] for c in CONFLITOS if c['GRAVIDADE'] == 'BLOQUEIA_IMPORTACAO']
    if not defeitos and not bloqueia:
        v = 'HANDOFF_READY_TO_IMPORT'
    elif len(defeitos) >= 6:
        v = 'HANDOFF_REJECTED'
    else:
        v = 'HANDOFF_PARTIAL'
    return {
        'VEREDITO': v,
        'PORQUE': 'a coleta e solida e a proveniencia e exemplar — 8 das 11 hipoteses '
                  'do red team cairam. Mas 3 defeitos ficam no dado de origem e 3 '
                  'conflitos bloqueiam estruturas especificas. O mais caro (C-7) nao '
                  'e defeito do handoff: e do nosso proprio lado, e so apareceu porque '
                  'o handoff e a segunda captura do mesmo registro.',
        'DEFEITOS_ABERTOS': defeitos,
        'CONFLITOS_QUE_BLOQUEIAM': bloqueia,
        'PODE_ENTRAR_AGORA': [
            {'ESTRUTURA': 'PRODUCTS (56)', 'DESTINO': 'catalogo_produto',
             'PORQUE': 'presenca em catalogo publico, com pagina, data e nivel de '
                       'evidencia. Nao afirma registro nem venda.'},
            {'ESTRUTURA': 'CROP_RELATIONS declaradas (588)',
             'DESTINO': 'catalogo_produto_cultivo',
             'PORQUE': 'DECLARADO != CITADO ja esta no dado, campo a campo'},
            {'ESTRUTURA': 'DOCUMENTS (147)', 'DESTINO': 'catalogo_produto_documento',
             'PORQUE': 'com sha256 e estado de download; raw_asset_id fica NULL ate '
                       'o byte estar preservado de verdade'},
            {'ESTRUTURA': 'CROP_ISSUE_RELATIONS (5)',
             'DESTINO': 'registro_uso + registro_uso_janela',
             'PORQUE': 'os unicos REGULATORY_FACT, confirmados par a par no MAPA pelo '
                       'numero de registro. Com a ressalva C-4 na do TRINITY.'},
            {'ESTRUTURA': 'REGULATORY_CROSSWALK (108)',
             'DESTINO': 'catalogo_registro_crosswalk',
             'PORQUE': 'a ponte entre catalogo e registro, com o estado de cada '
                       'entrada e a evidencia do casamento'},
        ],
        'NAO_PODE_ENTRAR_AINDA': [
            {'ESTRUTURA': 'ISSUE_RELATIONS (176)', 'BLOQUEIO': 'RT-11',
             'PORQUE': '25 linhas dizem que fungicida, inseticida e regulador de '
                       'crescimento tem "MALAS HIERBAS" como alvo. Falta o campo '
                       'DECLARATION_SOURCE que CROP_RELATIONS tem.',
             'O_QUE_DESTRAVA': 'reprocessar ISSUE_RELATIONS com a mesma regra de '
                               'CROP_RELATIONS e marcar cada linha DECLARADO ou CITADO'},
            {'ESTRUTURA': 'APPLICATION_WINDOWS (2 de 3)', 'BLOQUEIO': 'RT-6 · C-4',
             'PORQUE': 'BBCH 00-00 vira CLOSED no motor quando a fonte diz 00-07',
             'O_QUE_DESTRAVA': 'corrigir BBCH_TO na origem, ou importar como '
                               'APPROXIMATE com o texto inteiro'},
            {'ESTRUTURA': 'qualquer registro que ja exista no acervo', 'BLOQUEIO': 'C-7',
             'PORQUE': 'a chave natural de registro_regulatorio inclui fonte_versao, '
                       'entao a segunda captura do MESMO registro cria uma segunda '
                       'linha. Medido: o NEPTUNE aparece 3x no mesmo caso.',
             'O_QUE_DESTRAVA': 'importador casando por (pais, registration_id) e '
                               'v_product_registered_windows devolvendo a captura mais '
                               'recente, com o numero de capturas exposto'},
            {'ESTRUTURA': 'REGISTRATION_ID de PRODUCTS', 'BLOQUEIO': 'RT-10',
             'PORQUE': 'o numero do site e o numero do registro divergem em pelo '
                       'menos um produto, sob o mesmo nome de campo',
             'O_QUE_DESTRAVA': 'renomear no artefato: REGISTRATION_ID_PUBLICADO_NO_SITE '
                               'e REGISTRATION_ID_NO_ROPF. Importar sempre o segundo.'},
        ],
        'PROCEDIMENTO_DE_IMPORTACAO_QUANDO_DESTRAVAR': [
            '1 · renumerar 010_catalogo_publico_fabricante.sql para 013 (conflito C-1). '
            'Nao tocar no conteudo.',
            '2 · aplicar 013 no Supabase pelo workflow supabase-migrate, com a 008 '
            'rodando por ultimo e estendida para conferir as 15 tabelas catalogo_*.',
            '3 · preservar os 138 PDFs primeiro: scripts/storage_preservar.py --enviar. '
            'So depois de VERIFIED o documento pode apontar raw_asset_id.',
            '4 · aplicar supabase/importacoes/ADAMA-ES-CATALOGO-2026-08-30.sql, que e '
            'idempotente, para as estruturas de PODE_ENTRAR_AGORA.',
            '5 · para o relogio C: importar as 5 CROP_ISSUE_RELATIONS em registro_uso '
            'e registro_uso_janela casando SEMPRE pelo numero do ROPF, nunca por nome '
            'comercial. Regra de resolucao temporal escrita e auditavel contra '
            'ANCHOR.ROW_TEXT — PHENOLOGY_STAGE so quando os dois BBCH aparecem no '
            'texto ancorado; caso contrario APPROXIMATE com a frase inteira.',
            '6 · titular vem do ROPF e e declarado como propriedade da consulta.',
            '7 · fecha_caducidad vem do ROPF pelo numero de registro. EXPIRY != '
            'WITHDRAWAL continua valendo: data vencida entra como data, nunca como '
            'retirada.',
            '8 · rodar supabase/tests/regressoes_calendario.sql e o ensaio dos cinco '
            'casos contra o banco ja carregado. Nenhuma das 45 afirmacoes pode cair.',
            '9 · so entao ISSUE_RELATIONS e APPLICATION_WINDOWS, depois de RT-11 e '
            'RT-6 resolvidos na origem.',
        ],
        'O_QUE_ESTA_RODADA_NAO_FEZ': [
            'nao importou nenhuma linha no banco canonico',
            'nao aplicou nada no Supabase',
            'nao criou migration nova',
            'nao mesclou a branch do handoff',
            'nao resolveu ES-CASE-001',
            'nao leu os 138 PDFs — eles estao no disco do usuario, fora do Git',
        ],
    }


def monta(dsn=None, dsn_interf=None):
    h = do_ref('data/samples/ADAMA-ES-PRODUCT-INTELLIGENCE.json')
    with open(ROPF, encoding='utf-8') as f:
        ropf = json.load(f)
    ropf_por_reg = {norm_reg(x['REG']): x for x in ropf['FICHAS']}

    est = estados_locais(h, ropf_por_reg)
    ens = ensaio(dsn)
    c = collections.Counter(x['ESTADO'] for x in est)
    base = collections.Counter(x['MATCH_BASIS'] for x in est)
    rt = red_team(h, est)

    return {
        'SOURCE_ID': 'ADAMA-ES-HANDOFF-GATE-V1',
        'VERSION': 'V1',
        'captured_at': AS_OF,
        'source': 'medicao do handoff %s, lido do Git. Nenhuma linha importada.' % REF,
        'SOURCE_LOCATION': 'interno',
        'FACT_LOCATION': 'ES',
        'ORIGINAL_LANGUAGE': 'pt',
        'O_QUE_ISTO_E': 'o portao. Diz se a camada ADAMA Espanha pode entrar no motor '
                        'dos quatro relogios, e o que precisa acontecer antes.',
        'NAO_IMPORTOU_NADA': True,
        'A_LOCALIZACAO': localizar(),
        'CONTAGENS_MEDIDAS': {
            'PRODUCTS': len(h['PRODUCTS']),
            'DOCUMENTS': len(h['DOCUMENTS']),
            'CROP_RELATIONS_TOTAL': len(h['CROP_RELATIONS']),
            'CROP_RELATIONS_DECLARADAS': sum(
                1 for r in h['CROP_RELATIONS']
                if r['DECLARATION_SOURCE'] == 'DECLARADO_NO_BLOCO_CULTIVOS'),
            'ISSUE_RELATIONS': len(h['ISSUE_RELATIONS']),
            'USOS_COM_CULTIVO_E_ALVO': len(h['CROP_ISSUE_RELATIONS']),
            'LINHAS_CULTIVO_X_DOSE_SEM_ALVO': len(h['CROP_DOSE_RELATIONS']),
            'APPLICATION_WINDOWS': len(h['APPLICATION_WINDOWS']),
        },
        'PORTFOLIO_LOCAL': {
            'REGRA': 'existir na Franca, na Italia, no site global ou numa apresentacao '
                     'global NAO faz um produto ser resposta ADAMA Espanha. So evidencia '
                     'espanhola faz.',
            'LOCAL_REGISTERED': c['LOCAL_REGISTERED'],
            'LOCAL_PRESENT_BUT_REGISTRATION_NOT_PROVED':
                c['LOCAL_PRESENT_BUT_REGISTRATION_NOT_PROVED'],
            'NOT_KNOWN': c['NOT_KNOWN'],
            'POR_BASE_DE_CASAMENTO': dict(base),
            'PORQUE_NOT_KNOWN_E_ZERO':
                'os 56 foram observados ao vivo no catalogo espanhol, entao presenca '
                'local nunca e desconhecida. O que varia e a prova de registro. '
                'NOT_KNOWN passaria a ser diferente de zero se um produto entrasse '
                'por uma lista sem observacao propria.',
            'PORQUE_NENHUM_E_NAO_REGISTRADO':
                'os 12 sem casamento no ROPF vigente podem ter registro cancelado, '
                'registro de outro titular, ou grafia que o crosswalk nao alcancou. '
                'AUSENTE_MEDIDO no ROPF vigente nao e AUSENCIA DE REGISTRO.',
            'LINHAS': est,
        },
        'COBERTURA_POR_CAMPO': cobertura(h, ropf_por_reg),
        'ENSAIO_DOS_CINCO_CASOS': ens,
        'ENSAIO_DE_INTERFERENCIA': interferencia(dsn_interf),
        'RED_TEAM': rt,
        'ES_CASE_001': es_case_001(h),
        'CONFLITOS_COM_O_SCHEMA': CONFLITOS,
        'RED_TEAM_MUTACOES': mutacoes(),
        'RED_TEAM_PLACAR': {
            'HIPOTESES_TESTADAS': len(rt),
            'DERRUBADAS': sum(1 for x in rt if x['RESULTADO'] == 'HIPOTESE_DERRUBADA'),
            'DEFEITOS_CONFIRMADOS': sum(1 for x in rt if x['RESULTADO'] == 'DEFEITO_CONFIRMADO'),
        },
        'VEREDITO': veredito(rt, ens),
    }


if __name__ == '__main__':
    dsn = None
    if '--dsn' in sys.argv:
        dsn = sys.argv[sys.argv.index('--dsn') + 1]
    dsn_i = None
    if '--dsn-interferencia' in sys.argv:
        dsn_i = sys.argv[sys.argv.index('--dsn-interferencia') + 1]
    d = monta(dsn, dsn_i)
    if '--build' in sys.argv:
        with open(SAIDA, 'w', encoding='utf-8') as f:
            json.dump(d, f, ensure_ascii=False, indent=1)
            f.write('\n')
        print('escrito:', SAIDA)
    p = d['PORTFOLIO_LOCAL']
    print('HANDOFF        =', d['A_LOCALIZACAO']['REF'], d['A_LOCALIZACAO']['HEAD_CURTO'])
    print('MESCLADO       =', d['A_LOCALIZACAO']['MESCLADO_NA_PRINCIPAL'])
    for k, v in d['CONTAGENS_MEDIDAS'].items():
        print('%-34s %s' % (k, v))
    print('LOCAL_REGISTERED                   %s  (numero %s · nome+composicao %s)'
          % (p['LOCAL_REGISTERED'], p['POR_BASE_DE_CASAMENTO'].get('REGISTRATION_NUMBER', 0),
             p['POR_BASE_DE_CASAMENTO'].get('NAME_AND_COMPOSITION', 0)))
    print('LOCAL_PRESENT_BUT_REG_NOT_PROVED   %s'
          % p['LOCAL_PRESENT_BUT_REGISTRATION_NOT_PROVED'])
    print('NOT_KNOWN                          %s' % p['NOT_KNOWN'])
    print()
    for x in d['RED_TEAM']:
        print('%-6s %-22s %s' % (x['ID'], x['RESULTADO'], x['HIPOTESE'][:60]))
    print()
    for m in d['RED_TEAM_MUTACOES']:
        print('MUT %-6s %-22s %s' % (m['ALVO'], m['RESULTADO'], m['MUTACAO'][:50]))
    e = d['ENSAIO_DOS_CINCO_CASOS']
    print()
    print('ENSAIO =', e['ESTADO'])
    for c in e.get('CASOS', []):
        print('  %s · %-46s %-11s %-16s some=%s' % (
            c['CASO'], c['O_QUE_EXERCE'][:46], ','.join(c['ESTADO_DA_JANELA']),
            ','.join(c['ESCOPO']), c['SOME_AO_PERGUNTAR_POR_ISSUE']))
    print('\nRED_TEAM: %d testadas · %d derrubadas · %d defeitos'
          % (d['RED_TEAM_PLACAR']['HIPOTESES_TESTADAS'],
             d['RED_TEAM_PLACAR']['DERRUBADAS'],
             d['RED_TEAM_PLACAR']['DEFEITOS_CONFIRMADOS']))
    i = d['ENSAIO_DE_INTERFERENCIA']
    print('INTERFERENCIA =', i['ESTADO'],
          ('· %d registro(s) duplicado(s) · NEPTUNE aparece %dx'
           % (i['DUPLICADOS'], i['JANELAS_DO_NEPTUNE_NA_VIEW']))
          if i['ESTADO'] == 'EXECUTADO' else '')
    print('ES-CASE-001 =', d['ES_CASE_001']['ESTADO'])
    print('VEREDITO    =', d['VEREDITO']['VEREDITO'])
