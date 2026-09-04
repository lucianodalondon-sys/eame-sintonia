#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""O SNAPSHOT DA REUNIÃO · a única fonte de inteligência da interface.

    python3 scripts/meeting_snapshot.py --source-head <sha> [--cutoff ISO8601]

    lê     build/ITALY-REALITY-HANDOFF-V2.1/DESIGN-INGEST/OPPORTUNITIES.json
    grava  italia-portale/client/meeting-intelligence-snapshot.json
           italia-portale/client/meeting-intelligence-snapshot.js

POR QUE UM SNAPSHOT, E NÃO O PACOTE
------------------------------------
O portal não pode ler arquivo intermediário. Se ele lê o pacote, ele passa a
depender de quando o pacote foi construído — e uma reunião não pode depender de
um build que ninguém sabe se terminou.

    O QUE A REUNIÃO MOSTRA TEM DE SER IMUTÁVEL, IDENTIFICADO E DATADO.

O snapshot carrega o `SOURCE_HEAD` do commit da inteligência, o `BUILD_ID` do
pacote e o `MEETING_CUTOFF`. Se qualquer um dos três não bater, a régua reprova.

O QUE ATRAVESSA — E O QUE NÃO
------------------------------
A mesma lei de `site_v21_ingest.py`: LISTA DE PERMISSÃO, campo a campo. Fato e
CÓDIGO atravessam; prosa de pesquisa em português NÃO.

    PROSA QUE NÃO EMBARCA NÃO VAZA.

`WINDOW_CONDITION` é a oração original do boletim, em português de pesquisa.
Ela **não** atravessa como texto: atravessa `WINDOW_CONDITION__PT_ONLY: true` e
a identificação do documento que a contém. A tela diz «a condição está declarada
no documento X» — que é verdade — em vez de mostrar português a um italiano.

E O MOTOR NÃO VAI JUNTO
-----------------------
Nenhuma regra é recalculada aqui. Este arquivo COPIA campos já decididos e
recusa os que não estão na lista. Se um dia ele começar a decidir alguma coisa,
haverá dois donos — e o gate `NO_RAW_BYPASS` existe para isso não acontecer em
silêncio.
"""
import json
import os
import re
import subprocess
import sys
from collections import Counter
from datetime import datetime, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ING = os.path.join(ROOT, 'build', 'ITALY-REALITY-HANDOFF-V2.1', 'DESIGN-INGEST')
OUT = os.path.join(ROOT, 'italia-portale', 'client')

# ── CAMPOS QUE ATRAVESSAM · fato, código, número. Nunca prosa de pesquisa. ──
CAMPOS = (
    'ID', 'ARCHETYPE', 'CROP', 'TARGET', 'GEOGRAPHY', 'GEOGRAPHIC_SCOPE',
    'STATUS', 'OPPORTUNITY_STATE', 'RENDERABLE_WITH_METHOD',
    # a régua comercial
    'COMMERCIAL_PRIORITY', 'WHY_COMMERCIAL_CODES',
    'EXTERNAL_MATERIAL_READY', 'EXTERNAL_BLOCKER_CODES',
    # a cadeia do agora
    'WHY_NOW_CODES', 'WHY_NOW_CHAIN', 'ACTION_CHAIN_LINKS',
    'SIGNAL_DATE', 'SIGNAL_AGE_DAYS', 'SIGNAL_CURRENCY',
    'COMMERCIAL_TIMING_BASIS',
    # a janela
    'WINDOW_TYPE', 'WINDOW_DEFINED', 'WINDOW_OPEN_NOW',
    'WINDOW_OPEN_NOW_METHOD', 'WINDOW_EVIDENCE_ID',
    'WINDOW_RULE_STATE', 'WINDOW_RULE_EVIDENCE_ID',
    'WINDOW_START', 'WINDOW_END', 'DAYS_REMAINING', 'WINDOW_STATE',
    # os três estados declarados, com dono separado
    'PEST_STAGE_STATE', 'PEST_STAGE_EVIDENCE_ID',
    'ACTION_RECOMMENDATION_STATE', 'ACTION_RECOMMENDATION_EVIDENCE_ID',
    'THRESHOLD_STATE', 'THRESHOLD_STATE_EVIDENCE_ID',
    'NEED_DIRECTION', 'NEED_EVIDENCE_ID', 'NEED_METHOD', 'NEED_AMBIGUITY_CODES',
    # o portfólio, produto a produto
    'PORTFOLIO_MATCHES', 'PRIMARY_MATCH', 'PRIMARY_MATCH_REASON',
    'PRODUCT_LINK_STATE', 'MATCHED_COMMERCIAL_PRODUCT_IDS',
    'MATCHED_COMMERCIAL_PRODUCT_NAMES', 'COMMERCIAL_PRODUCT_COUNT',
    'ACTIVE_INGREDIENT_NAMES', 'MODE_OF_ACTION_CODES', 'MODE_OF_ACTION_STATE',
    'PRODUCT_RESTRICTIONS', 'APPLICATION_STATE',
    # o que falta, quem age, e o papel de cada evidência
    'WHAT_IS_MISSING', 'ACTION_BY_DEPARTMENT', 'EVIDENCE_ROLES',
    'INTELLIGENCE_BRIEF', 'EVIDENCE_IDS', 'EVIDENCE_COUNT',
    'EVIDENCE_FAMILIES',
    # tamanho e confiança
    'COMMERCIAL_MAGNITUDE', 'COMMERCIAL_MAGNITUDE_DIMENSIONS',
    'SIGNAL_CONFIDENCE', 'WINDOW_CONFIDENCE', 'PRODUCT_MATCH_CONFIDENCE',
    'CONFIDENCE', 'OPPORTUNITY_SCORE',
    # a catraca
    'PUBLICATION_STATE', 'TRAIL_STATE',
    # a geografia da afirmação
    'CLAIM_GEOGRAPHY', 'CLAIM_GEOGRAPHY_HOLDS',
    'SOURCE_IDS', 'SOURCE_URLS', 'REFERENCE_DATE',
)

# Campos localizáveis: só atravessam com o par IT+EN aprovado.
LOCALIZAVEIS = ('WHY_COMMERCIAL', 'WHAT_IT_PROVES', 'WHAT_IT_DOES_NOT_PROVE',
                'COMMERCIAL_DOES_NOT_PROVE')

# Prosa de pesquisa que NÃO atravessa como texto — só como declaração de que
# existe, e do documento que a contém.
SO_DECLARADOS = ('WINDOW_CONDITION', 'NEED_EXCERPT', 'PEST_STAGE_EXCERPT',
                 'ACTION_RECOMMENDATION_EXCERPT')


# ── A LISTA DE PERMISSÃO TAMBÉM DESCE ──────────────────────────────────────
# O filtro anterior era de UM NÍVEL: `r[c] = o[c]` copiava o contêiner inteiro.
# Sete dos campos permitidos são dicionários e listas, e tudo que morava dentro
# deles atravessava sem nunca ter sido julgado. Foi assim que
# `ACTION_BY_DEPARTMENT.<dept>.NEXT_TRIGGER` — uma oração de pesquisa em
# português — chegou a 215 dos 215 blocos de departamento.
#
#     UMA LISTA DE PERMISSÃO QUE SÓ OLHA A PRIMEIRA CAMADA
#     NÃO É UMA LISTA DE PERMISSÃO: É UMA PORTA ENTREABERTA.
#
# Agora a permissão desce até a folha. A gramática abaixo é lida assim:
#
#     FOLHA          copia o valor como está (escalar, ou lista de escalares)
#     {chave: ...}   dicionário de chaves fixas; o que não está aqui não desce
#     {'*': ...}     dicionário de chaves abertas (departamentos), mesmo molde
#     [ ... ]        lista; o molde vale para cada item
#
# Um campo aninhado que o motor acrescentar amanhã NÃO atravessa por omissão —
# ele aparece como ausente, que é visível, em vez de atravessar por descuido,
# que não é.
FOLHA = 'FOLHA'

_RESTRICAO = {'CODE': FOLHA, 'ACTIVE_INGREDIENT': FOLHA,
              'DATE': FOLHA, 'EVIDENCE_ID': FOLHA}

_ELO = {'OK': FOLHA, 'EVIDENCE': FOLHA, 'FACT': FOLHA}

ANINHADOS = {
    'WHY_NOW_CHAIN': {'SINAL_ATUAL': _ELO, 'JANELA_DEFINIDA': _ELO,
                      'JANELA_ABERTA_AGORA': _ELO,
                      'VINCULO_COM_PORTFOLIO': _ELO, 'TEMPO_PARA_ACAO': _ELO},
    'ACTION_CHAIN_LINKS': {'SINAL_ATUAL': FOLHA, 'JANELA_DEFINIDA': FOLHA,
                           'JANELA_ABERTA_AGORA': FOLHA,
                           'VINCULO_COM_PORTFOLIO': FOLHA,
                           'TEMPO_PARA_ACAO': FOLHA},
    'COMMERCIAL_MAGNITUDE_DIMENSIONS': {
        'SINAIS_DE_CAMPO': FOLHA, 'FONTES_INDEPENDENTES': FOLHA,
        'REGIOES_DO_PAR': FOLHA, 'AREA_OFICIAL_HA': FOLHA,
        'AREA_OFICIAL_ANO': FOLHA, 'AREA_SELECTION_RULE': FOLHA,
        'AREA_EVIDENCE_ID': FOLHA},
    # ⚠️ NEXT_TRIGGER fica DE FORA, e não perde nada: medido, ele é a mesma
    # coisa que DEPENDENCY dita em português — 185/185 sobre SINAL_ATUAL,
    # 20/20 sobre JANELA_ABERTA_AGORA, 10/10 quando ambos são nulos. A tela
    # mostra o CÓDIGO, que o dicionário traduz, em vez da oração, que não se
    # traduz sozinha.
    'ACTION_BY_DEPARTMENT': {'*': {
        'DEPARTMENT': FOLHA, 'ACTION_STATE': FOLHA, 'ACTION': FOLHA,
        'WHY_CODE': FOLHA, 'DEPENDENCY': FOLHA,
        'EVIDENCE': FOLHA, 'MISSING_LINKS': FOLHA}},
    'EVIDENCE_ROLES': [{'EVIDENCE_ID': FOLHA, 'ENTITY_TYPE': FOLHA,
                        'ROLE': FOLHA, 'WHY_CODE': FOLHA}],
    'INTELLIGENCE_BRIEF': [{'CODE': FOLHA, 'VALUES': {
        'ALVO': FOLHA, 'CULTURA': FOLHA, 'REGIAO': FOLHA, 'SINAIS': FOLHA,
        'FONTES': FOLHA, 'PRODUTOS': FOLHA, 'ACAO': FOLHA,
        'DEPARTAMENTO': FOLHA}}],
    'PORTFOLIO_MATCHES': [{
        'PRODUCT_ID': FOLHA, 'PRODUCT_NAME': FOLHA,
        'REGISTRATION_NUMBER': FOLHA, 'ACTIVE_INGREDIENTS': FOLHA,
        'MODE_OF_ACTION': FOLHA, 'CROP_FIT': FOLHA, 'TARGET_FIT': FOLHA,
        'REGIONAL_FIT': FOLHA, 'REGULATORY_FIT': FOLHA, 'WINDOW_FIT': FOLHA,
        'VALIDATION_STATE': FOLHA, 'EVIDENCE': FOLHA,
        'SOURCE_NAMES_THIS_ACTIVE': FOLHA, 'MATCH_REASON': FOLHA,
        'RESTRICTIONS': [_RESTRICAO]}],
    'PRODUCT_RESTRICTIONS': [_RESTRICAO],
}

# Prosa que fica de fora lá no fundo, e é DECLARADA no lugar onde morava, para
# que a tela possa dizer «existe, e está no documento X» sem exibi-la.
ANINHADOS_SO_DECLARADOS = {
    'ACTION_BY_DEPARTMENT': ('NEXT_TRIGGER',),
}


def _desce(valor, molde, so_declarados=()):
    """Aplica o molde a um valor aninhado. O que o molde não nomeia não desce.

    Contêiner vazio continua contêiner vazio: uma lista sem itens sai `[]` e um
    dicionário sem chaves sai `{}`, exatamente como antes. Suprimi-los mudaria o
    que a tela vê em casos que nada têm de errado.
    """
    if molde == FOLHA:
        return valor
    if isinstance(molde, list):
        if not isinstance(valor, list):
            return []
        return [_desce(v, molde[0], so_declarados) for v in valor]
    if isinstance(molde, dict):
        if not isinstance(valor, dict):
            return {}
        fixo = molde.get('*')
        saida = {}
        for k, v in valor.items():
            sub = fixo if fixo is not None else molde.get(k)
            if sub is None:
                continue
            saida[k] = _desce(v, sub, so_declarados)
            if fixo is not None and isinstance(v, dict):
                for pt in so_declarados:
                    if v.get(pt):
                        saida[k][pt + '__PT_ONLY'] = True
        for pt in so_declarados:
            if fixo is None and valor.get(pt):
                saida[pt + '__PT_ONLY'] = True
        return saida
    return None


def cabeca_do_commit(argv):
    """→ o HEAD da INTELIGÊNCIA, não o do checkout de agora.

    O pacote é construído na branch canônica e o snapshot é gerado na branch da
    reunião — `git rev-parse HEAD` aqui devolveria a casca visual, e o snapshot
    passaria a declarar uma procedência que não é a sua.

        UM SNAPSHOT QUE DECLARA O COMMIT ERRADO É PIOR QUE UM SEM COMMIT:
        ELE PARECE AUDITÁVEL.
    """
    if '--source-head' in argv:
        sha = argv[argv.index('--source-head') + 1]
        try:
            subprocess.check_output(['git', 'cat-file', '-e', sha + '^{commit}'],
                                    cwd=ROOT, stderr=subprocess.DEVNULL)
        except Exception:
            raise SystemExit('--source-head %s nao e um commit deste repositorio'
                             % sha)
        return sha
    raise SystemExit('faltou --source-head <sha da inteligencia canonica>')


# ── UNA FRASE PER IL CLIENTE NON NOMINA UN CAMPO DEL MOTORE ────────────────
# Undici delle quarantatre frasi `WHY_COMMERCIAL_IT/_EN` finiscono con un rimando
# interno: «— vedi NEED_DIRECTION e la frase originale in NEED_EXCERPT». È scritto
# per chi legge la scheda del caso di qua dalla frontiera, ed è corretto lì. Su uno
# schermo italiano è SCREAMING_SNAKE portoghese in mezzo a una frase.
#
#     UNA FRASE CHE RIMANDA A UN CAMPO PARLA A CHI HA IL CAMPO.
#     IL CLIENTE NON CE L'HA.
#
# Non si riscrive la frase e non se ne inventa un'altra: si taglia la SUBORDINATA
# che nomina il campo, e la principale — che è già una frase intera e vera — resta
# intatta. I nomi tagliati viaggiano come `__REFERS_TO_FIELDS`, così l'auditor
# vede che il rimando esisteva e a che cosa puntava. Se il taglio lasciasse una
# frase vuota, non si taglia: la frase non attraversa affatto.
NOME_DE_CAMPO = re.compile(r'\b[A-Z][A-Z0-9]*(?:_[A-Z0-9]+)+\b')


def sem_nome_de_campo(frase):
    """→ (frase senza il rimando interno, [nomi di campo rimossi])"""
    nomes = NOME_DE_CAMPO.findall(frase)
    if not nomes:
        return frase, []
    cabeca = re.split(r'\s+[—–-]\s+', frase)[0].strip()
    if not cabeca or NOME_DE_CAMPO.search(cabeca):
        # Il nome non sta in una subordinata staccabile: la frase non attraversa.
        return '', nomes
    if not cabeca.endswith('.'):
        cabeca += '.'
    return cabeca, nomes


def linha(o):
    r = {}
    for c in CAMPOS:
        if c not in o:
            continue
        if c in ANINHADOS:
            r[c] = _desce(o[c], ANINHADOS[c],
                          ANINHADOS_SO_DECLARADOS.get(c, ()))
        else:
            r[c] = o[c]
    for c in LOCALIZAVEIS:
        it, en = o.get(c + '_IT'), o.get(c + '_EN')
        if it and en:
            it2, ref1 = sem_nome_de_campo(it)
            en2, ref2 = sem_nome_de_campo(en)
            r[c + '_IT'], r[c + '_EN'] = it2, en2
            refs = sorted(set(ref1) | set(ref2))
            if refs:
                r[c + '__REFERS_TO_FIELDS'] = refs
        elif o.get(c):
            r[c + '__PT_ONLY'] = True
    for c in SO_DECLARADOS:
        if o.get(c):
            r[c + '__PT_ONLY'] = True
    return r


def main():
    cutoff = None
    if '--cutoff' in sys.argv:
        cutoff = sys.argv[sys.argv.index('--cutoff') + 1]
    cutoff = cutoff or datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')

    with open(os.path.join(ING, 'OPPORTUNITIES.json'), encoding='utf-8') as f:
        pac = json.load(f)
    regras_p = os.path.join(ING, 'OPPORTUNITY-RULES.json')
    with open(regras_p, encoding='utf-8') as f:
        regras = json.load(f)

    casos = [linha(o) for o in pac['RECORDS']]
    conta = lambda k: dict(Counter(str(c.get(k)) for c in casos))  # noqa: E731

    snap = {
        'COLLECTION': 'MEETING-INTELLIGENCE-SNAPSHOT',
        'LAW': 'esta e a UNICA fonte de inteligencia da interface. O portal '
               'apresenta; ele nao recalcula STATUS, COMMERCIAL_PRIORITY, '
               'WHY_NOW, janela, produto, papel de evidencia, mapa de acao nem '
               'PUBLICATION_STATE.',
        'SOURCE_HEAD': cabeca_do_commit(sys.argv),
        'BUILD_ID': pac.get('BUILD_ID'),
        'ENGINE_VERSION': 'scripts/v21_oportunidades.py + v21_janelas.py + '
                          'v21_necessidade.py + v21_comercial.py',
        'RULE_VERSION': regras.get('BUILD_ID') or pac.get('BUILD_ID'),
        'GENERATED_AT': datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
        'MEETING_CUTOFF': cutoff,
        'TOTAL_CASES': len(casos),
        'BY_STATUS': conta('STATUS'),
        'BY_COMMERCIAL_PRIORITY': conta('COMMERCIAL_PRIORITY'),
        'BY_PUBLICATION_STATE': conta('PUBLICATION_STATE'),
        'BY_WINDOW_DEFINED': conta('WINDOW_DEFINED'),
        'BY_WINDOW_OPEN_NOW': conta('WINDOW_OPEN_NOW'),
        'BY_WINDOW_RULE_STATE': conta('WINDOW_RULE_STATE'),
        # BRIEF_TEMPLATES saiu: eram as frases-molde do motor, escritas em
        # português de pesquisa, e nenhuma tela pode exibi-las a um
        # italiano. Os CÓDIGOS do brief atravessam; as frases vivem no
        # dicionário de lingua, em IT e EN, do lado de cá da fronteira.
        'BRIEF_CODES': sorted({b.get('CODE') for o in pac['RECORDS']
                               for b in (o.get('INTELLIGENCE_BRIEF') or [])
                               if b.get('CODE')}),
        'WINDOW_TYPES_AGRONOMIC': regras.get('WINDOW_TYPES_AGRONOMIC') or [],
        'CASES': casos,
    }

    os.makedirs(OUT, exist_ok=True)
    pj = os.path.join(OUT, 'meeting-intelligence-snapshot.json')
    with open(pj, 'w', encoding='utf-8') as f:
        json.dump(snap, f, ensure_ascii=False, indent=1)
    pjs = os.path.join(OUT, 'meeting-intelligence-snapshot.js')
    with open(pjs, 'w', encoding='utf-8') as f:
        f.write('/* GERADO por scripts/meeting_snapshot.py — NAO EDITAR A MAO.\n'
                '   SOURCE_HEAD %s · BUILD_ID %s · MEETING_CUTOFF %s */\n'
                % (snap['SOURCE_HEAD'], snap['BUILD_ID'], snap['MEETING_CUTOFF']))
        f.write('window.MEETING_INTELLIGENCE = ')
        json.dump(snap, f, ensure_ascii=False, separators=(',', ':'))
        f.write(';\n')

    print('SOURCE_HEAD     %s' % snap['SOURCE_HEAD'])
    print('BUILD_ID        %s' % snap['BUILD_ID'])
    print('MEETING_CUTOFF  %s' % snap['MEETING_CUTOFF'])
    print('TOTAL_CASES     %d' % snap['TOTAL_CASES'])
    for k in ('BY_STATUS', 'BY_COMMERCIAL_PRIORITY', 'BY_PUBLICATION_STATE',
              'BY_WINDOW_DEFINED', 'BY_WINDOW_OPEN_NOW', 'BY_WINDOW_RULE_STATE'):
        print('%-24s %s' % (k, snap[k]))
    print('\ngravado: %s' % os.path.relpath(pj, ROOT))
    print('gravado: %s (%.0f KB)'
          % (os.path.relpath(pjs, ROOT), os.path.getsize(pjs) / 1024.0))
    return 0


if __name__ == '__main__':
    sys.exit(main())
