#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
COMMENT_COLLECTION_ELIGIBILITY — este PAI merece que se lhe colham os comentários? (D106 · COMENTARIOS-V1)

    import elegibilidade_comentario as el
    e = el.elegibilidade(pai, 'T8', fonte_registada=True, comentarios_declarados=3)
    e['COMMENT_COLLECTION_ELIGIBILITY']    # HIGH | MEDIUM | LOW | NO
    el.marcar(objetos_de_comentario, pai=pai)   # a amostra diversa + controlo + os sinais (D107)

    py pedido/elegibilidade_comentario.py piloto     # os pais do piloto da COMMENT-INTELLIGENCE-FASE1 §7

PORQUE MORA NO PEDIDO (COMMENT-INTELLIGENCE-FASE1 §6.1)
-------------------------------------------------------
É o pedido que sabe o assunto (o universo) e o recorte. O Scrap colhe o vídeo que lhe
nomeiam; ele não julga relevância. Por isso a pergunta «este pai merece comentário?»
responde-se ANTES do despacho, aqui — e a fase `comentarios-youtube` continua a colher
UM vídeo nomeado por execução, sem saber desta régua.

NÃO HÁ RÉGUA NOVA: TRÊS DONOS, TRÊS PERGUNTAS
---------------------------------------------
  universo do pedido  `admissao._do_universo` + `admissao.PERGUNTAS_DO_UNIVERSO` — a mesma
                      pergunta que a porta faz ao item («isto serve a este universo?»).
  tema do pai         a MESMA função, sobre os universos de tema do §6.1 (safra T1,
                      clima T2, praga/doença/infestante T3, regulação T4). SIM = tema
                      forte; NAO_SEI com palavras achadas = indício.
  entidades           `motor/matriz_recorte.py` (CROPS, ISSUES, `_padrao`) — cultura e
                      problema nomeados no texto do pai.

    HIGH    fonte REGISTADA (SOURCE_ID canónico) + (universo SIM ou tema forte) + entidade
    MEDIUM  entidade + (universo SIM/NAO_SEI com palavras, tema forte ou indício) — falta
            o registo da fonte ou a força do tema
    LOW     só indício, sem entidade nomeada
    NO      o universo diz NAO sem tema nem entidade; ou os comentários estão desligados
    NAO_SEI nenhuma palavra reconhecida pelos donos: LACUNA de vocabulário, NÃO prova de
            trivialidade (medido: «maculatura bruna del pero» caía em NO)

VAI_COLHER só com HIGH/MEDIUM E comentários declarados diferentes de 0. «0 declarado» não
é «não consegui colher»: é ZERO_DECLARADO_PELA_FONTE, e fica escrito (FASE1 §7.2).

A AMOSTRA (FASE1 §6.2, §32) — MARCAR, NUNCA APAGAR
--------------------------------------------------
Cada comentário colhido recebe `SAMPLE_BUCKETS`: RELEVANCIA (nomeia entidade canónica),
ENGAJAMENTO (top-N por gostos), CRONOLOGICA (os N mais recentes), DISCORDANTE (marcador
lexical de discordância) e CONTROLE — uma fatia CRUA, escolhida por hash estável do
COMMENT_ID, sem olhar para o texto. Sem controlo nunca se sabe o que a seleção deixou de
fora. Nada é apagado: um item fora de todos os baldes continua lá, com a lista vazia.

OS DOIS SINAIS DA D107 (IAB-REGIONAL-LANGUAGE-INTELLIGENCE §19-22)
-----------------------------------------------------------------
  AGRONOMIC_SIGNAL   YES quando o comentário nomeia cultura ou problema canónico.
  LINGUISTIC_SIGNAL  YES quando o comentário tem frase própria (>= PALAVRAS_LINGUISTICAS
                     palavras). Um comentário sem facto novo pode ter valor linguístico:
                     não se descarta.
  REGIONAL_LANGUAGE_EVIDENCE  EXPLICIT só quando a PRÓPRIA fala diz o lugar («qui in
                     Puglia», «da noi in Veneto») e o lugar está no gazetteer italiano
                     (`leis/fato_local.mencoes`). STRONG/WEAK_CONTEXT pedem contexto da
                     comunidade que esta régua não mede: ficam UNKNOWN, ditos.
  SPEAKER_LANGUAGE_LOCATION = REGION_IF_PROVEN ou UNKNOWN — NUNCA o FACT_LOCATION do pai.

⚠️ Tudo isto é LEXICAL e NÃO MEDIDO contra gabarito. Os limiares (N, fração do controlo,
palavras) são escolhidos. Nada aqui promove comentário a facto (a promoção é da Admissão).
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys
import unicodedata

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)
import _gavetas  # noqa: E402,F401 — poe as gavetas no caminho de importacao
import admissao as adm  # noqa: E402  dona da régua do universo
import matriz_recorte as MR  # noqa: E402  dona do vocabulário de cultura e problema
import fato_local as FL  # noqa: E402  dono do gazetteer italiano
import social_envelope as env  # noqa: E402  dono do envelope do comentário

HIGH, MEDIUM, LOW, NO, NAO_SEI = 'HIGH', 'MEDIUM', 'LOW', 'NO', 'NAO_SEI'
NIVEIS = (HIGH, MEDIUM, LOW, NO, NAO_SEI)
#: Os universos de TEMA do §6.1: safra, clima, praga/doença/infestante, regulação.
UNIVERSOS_DE_TEMA = ('T1', 'T2', 'T3', 'T4')
N_POR_BALDE = 5                 # escolhido, não medido
FRACAO_CONTROLE = 5             # 1 em cada 5 (hash estável), escolhido, não medido
PALAVRAS_LINGUISTICAS = 6       # escolhido, não medido
BALDES = ('RELEVANCIA', 'ENGAJAMENTO', 'CRONOLOGICA', 'DISCORDANTE', 'CONTROLE')

_PADROES = {k: MR._padrao(v) for k, v in list(MR.CROPS.items()) + list(MR.ISSUES.items())}
_RE_DISCORDA = re.compile(
    # sem «pero»: em italiano sem acento e tambem a PEREIRA (o piloto tem «maculatura del pero»)
    r"(?<![a-z])(?:non e vero|non sono d'accordo|sbagliato|falso|anzi|invece|ma no|"
    r"non funziona|disagree|not true|wrong|no es verdad)(?![a-z])")
_RE_REGIAO_DITA = re.compile(r"(?<![a-z])(?:qui in|qui a|qui da noi in|da noi in|dalle nostre parti in|"
                             r"noi in|nella mia zona|in zona|nel mio paese in|nella nostra zona in)(?![a-z])")


def _norm(s):
    return re.sub(r'\s+', ' ', MR._norm(s or ''))


def entidades(texto):
    """As entidades canónicas (cultura e problema) que o texto NOMEIA, pelo dono do vocabulário."""
    n = _norm(texto)
    return sorted(k for k, rx in _PADROES.items() if rx.search(n))


def _texto_do_pai(pai):
    return ' '.join(str(pai.get(k) or '') for k in ('TITLE', 'TITULO', 'DESCRIPTION', 'DESCRICAO', 'TEXT'))


def elegibilidade(pai, universo, *, fonte_registada, comentarios_declarados=None,
                  comentarios_desligados=False):
    """→ o veredito, com o porquê de cada peça. Não pede nada à rede."""
    texto = _texto_do_pai(pai)
    item = {'texto': texto, 'title': pai.get('TITLE') or pai.get('TITULO') or ''}
    uv, umotivo, _ = adm._do_universo(item, universo, adm.PERGUNTAS_DO_UNIVERSO.get(universo, []))
    fortes, indicios = [], []
    for t in UNIVERSOS_DE_TEMA:
        v, _m, ev = adm._do_universo(item, t, adm.PERGUNTAS_DO_UNIVERSO.get(t, []))
        if v == adm.SIM:
            fortes.append(t)
        elif v == adm.NAO_SEI and (ev or {}).get('palavras'):
            indicios.append(t)
    ents = entidades(texto)
    universo_sim = uv == adm.SIM
    if comentarios_desligados:
        nivel, porque = NO, 'o dono do material desligou os comentários (FEATURE_DISABLED): nada a colher'
    elif fonte_registada and (universo_sim or fortes) and ents:
        nivel, porque = HIGH, 'fonte registada + %s + entidade %s' % (
            'universo %s SIM' % universo if universo_sim else 'tema forte %s' % ','.join(fortes), ents[:3])
    elif ents and (universo_sim or fortes or indicios or uv == adm.NAO_SEI):
        falta = [] if fonte_registada else ['fonte NAO registada (CANDIDATA)']
        if not (universo_sim or fortes):
            falta.append('tema so por indicio')
        nivel, porque = MEDIUM, 'entidade %s; falta: %s' % (ents[:3], '; '.join(falta) or 'nada')
    elif indicios or fortes:
        nivel, porque = LOW, 'so indicio de tema (%s), sem entidade canónica nomeada' % ','.join(fortes + indicios)
    elif uv == adm.NAO:
        nivel, porque = NO, 'a regua do universo %s diz NAO e nao ha tema nem entidade' % universo
    else:
        # MEDIDO no piloto: «maculatura bruna del pero» saia NO — pera e maculatura nao estao
        # nos vocabularios dos donos. Nenhuma palavra reconhecida NAO prova trivialidade.
        nivel, porque = NAO_SEI, ('LACUNA_DE_VOCABULARIO: nem a regua da Admissao nem o matriz_recorte '
                                  'reconhecem o tema deste pai. Nao se prova que e trivial — fica NAO_SEI, '
                                  'para leitura humana ou vocabulario maior')
    zero = comentarios_declarados == 0
    return {
        'COMMENT_COLLECTION_ELIGIBILITY': nivel, 'PORQUE': porque,
        'UNIVERSO': universo, 'REGUA_DO_UNIVERSO': {'VEREDITO': uv, 'MOTIVO': umotivo[:240]},
        'TEMAS_FORTES': fortes, 'TEMAS_INDICIO': indicios, 'ENTIDADES_DO_PAI': ents,
        'FONTE_REGISTADA': bool(fonte_registada), 'COMENTARIOS_DECLARADOS': comentarios_declarados,
        'VAI_COLHER': nivel in (HIGH, MEDIUM) and not zero and not comentarios_desligados,
        'SE_NAO_COLHE': ('ZERO_DECLARADO_PELA_FONTE — nao e «nao consegui colher»' if zero and nivel in (HIGH, MEDIUM)
                         else None),
        'DONOS': 'admissao._do_universo/PERGUNTAS_DO_UNIVERSO · motor/matriz_recorte.py',
    }


def _estavel(cid):
    return int(hashlib.sha1(str(cid).encode('utf-8')).hexdigest()[:8], 16)


def _regiao_dita(texto):
    """A região que a PRÓPRIA fala diz, com o gatilho perto do topónimo. Senão None."""
    m = _RE_REGIAO_DITA.search(_norm(texto))
    if not m:
        return None, None
    janela = (texto or '')[max(0, m.start() - 5): m.end() + 60]
    lugares = FL.mencoes(janela)
    return (lugares[0]['PLACE'], janela.strip()) if lugares else (None, None)


def marcar(objetos, *, pai, n=N_POR_BALDE):
    """Marca a amostra e os sinais (D107) nos objetos `COMMENT`. Devolve o relatório. Não apaga nada."""
    comentarios = [o for o in objetos if o.get('CONTENT_TYPE') == 'COMMENT']
    topico = ', '.join(entidades(_texto_do_pai(pai))) or env.DESCONHECIDO
    for o in comentarios:
        texto = o.get('TEXT') or ''
        ents = entidades(texto)
        o['CANONICAL_ENTITIES'] = ents
        o['PARENT_TOPIC'] = topico
        o['AGRONOMIC_SIGNAL'] = 'YES' if ents else 'NO'
        o['LINGUISTIC_SIGNAL'] = 'YES' if len(re.findall(r"[^\W\d_]{2,}", texto)) >= PALAVRAS_LINGUISTICAS else 'NO'
        lugar, trecho = _regiao_dita(texto)
        o['REGIONAL_LANGUAGE_EVIDENCE'] = 'EXPLICIT' if lugar else env.DESCONHECIDO
        o['REGION_IF_PROVEN'] = lugar or env.DESCONHECIDO
        o['REGIONAL_LANGUAGE_EVIDENCE_TRECHO'] = trecho
        # NUNCA o lugar do facto do pai (IAB §5): sem evidência explícita é UNKNOWN.
        o['SPEAKER_LANGUAGE_LOCATION'] = lugar or env.DESCONHECIDO
        o['SAMPLE_BUCKETS'] = []
    def gostos(o):
        v = (o.get('RAW') or {}).get('LIKE_COUNT')
        return v if isinstance(v, int) else -1
    escolhas = {
        'RELEVANCIA': [o for o in comentarios if o['CANONICAL_ENTITIES']][:n],
        'ENGAJAMENTO': sorted(comentarios, key=gostos, reverse=True)[:n],
        'CRONOLOGICA': sorted(comentarios, key=lambda o: str(o.get('PUBLISHED_AT') or ''), reverse=True)[:n],
        'DISCORDANTE': [o for o in comentarios if _RE_DISCORDA.search(_norm(o.get('TEXT')))][:n],
        'CONTROLE': [o for o in comentarios if _estavel(o.get('NATIVE_ID')) % FRACAO_CONTROLE == 0],
    }
    for balde, lista in escolhas.items():
        for o in lista:
            if balde not in o['SAMPLE_BUCKETS']:
                o['SAMPLE_BUCKETS'].append(balde)
    return {'COMENTARIOS': len(comentarios), 'POR_BALDE': {b: len(l) for b, l in escolhas.items()},
            'FORA_DE_TODOS_OS_BALDES': sum(1 for o in comentarios if not o['SAMPLE_BUCKETS']),
            'APAGADOS': 0, 'AGRONOMIC_YES': sum(o['AGRONOMIC_SIGNAL'] == 'YES' for o in comentarios),
            'LINGUISTIC_YES': sum(o['LINGUISTIC_SIGNAL'] == 'YES' for o in comentarios),
            'REGIONAL_EXPLICIT': sum(o['REGIONAL_LANGUAGE_EVIDENCE'] == 'EXPLICIT' for o in comentarios)}


# ── o piloto da COMMENT-INTELLIGENCE-FASE1 §7, julgado sem rede ───────────────
#: (SOURCE_ID ou None se CANDIDATA, VIDEO_ID, universo do pedido). Metade A (fonte
#: registada) e metade B (controlo, fora do atlas).
PILOTO = (
    ('IT-T8-006', 'soP-t7nvvq8', 'T8'), ('IT-T8-006', 'F5uLnId6fJk', 'T8'),
    ('IT-T8-006', 'w87w51fSWAw', 'T8'), ('IT-T8-006', 'QGE7h4gztQ8', 'T8'),
    ('IT-T8-006', 'R5FJWJkCbKI', 'T8'), ('IT-T8-006', '5MNenAiGtlQ', 'T8'),
    ('IT-T9-016', 'QmeVN7SNnMU', 'T9'), ('IT-T9-016', '2cF0yHZXiMs', 'T9'),
    ('IT-T9-016', 'ioLYGSazexk', 'T9'),
    (None, 'ezRyN8vLVvc', 'T8'), (None, 'u91bnWQZOOM', 'T8'), (None, '2ECn7o-Prc8', 'T8'),
)


def _pais_do_acervo():
    """Os metadados dos vídeos que o acervo JÁ tem (SENSOR-PILOT/VIDEOS-*). Só leitura."""
    import glob
    fora = {}
    for f in sorted(glob.glob(os.path.join(RAIZ, 'data', 'samples', 'SENSOR-PILOT', 'VIDEOS-*.json'))):
        with open(f, encoding='utf-8') as fh:
            for it in json.load(fh).get('ITEMS', []):
                fora.setdefault(it.get('EXTERNAL_ID'), it)
    return fora


def piloto():
    pais = _pais_do_acervo()
    linhas = []
    for sid, vid, universo in PILOTO:
        p = pais.get(vid)
        if p is None:
            linhas.append({'SOURCE_ID': sid, 'VIDEO_ID': vid, 'COMMENT_COLLECTION_ELIGIBILITY': 'NAO_SEI',
                           'PORQUE': 'o acervo nao tem os metadados deste pai (titulo/descricao): sem texto nao se julga',
                           'VAI_COLHER': False})
            continue
        n = p.get('COMMENTS_COUNT')
        e = elegibilidade(p, universo, fonte_registada=sid is not None,
                          comentarios_declarados=n if isinstance(n, int) else None)
        e.update({'SOURCE_ID': sid or 'CANDIDATA (D93)', 'VIDEO_ID': vid, 'TITLE': (p.get('TITLE') or '')[:80],
                  'CHANNEL': p.get('CHANNEL')})
        if e['VAI_COLHER'] and sid:
            e['COMANDO'] = ('gh workflow run sintonia-scrap.yml -f fase=comentarios-youtube -f fonte=%s '
                            '-f video=%s -f runner=2' % (sid, vid))
        linhas.append(e)
    return linhas


if __name__ == '__main__':
    if sys.argv[1:2] == ['piloto']:
        for l in piloto():
            print('%-18s %-12s %-7s colhe=%-5s %s' % (l['SOURCE_ID'], l['VIDEO_ID'], l['COMMENT_COLLECTION_ELIGIBILITY'],
                                                    l['VAI_COLHER'], l['PORQUE'][:110]))
    else:
        print(__doc__)
