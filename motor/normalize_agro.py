#!/usr/bin/env python3
"""
Normalizador agronômico multipaís — FASE 1 da MISSÃO EAME 03 (cruzamento X-007).

Problema: o registro francês (E-Phy) descreve o uso autorizado como
`Cultura * Tratamento * Alvo` em **nome comum francês**, sem código EPPO e sem nome
científico. O registro espanhol (MAPA) traz EPPO e nome científico. Sem uma ponte,
"Mildiou(s)" na França e "Mildiu" na Espanha são duas coisas soltas.

Desenho, e a razão de ele ser defensável:

    o dicionário espanhol PROPÕE um código EPPO candidato (por proximidade lexical
    entre o nome comum francês e o espanhol)
    →
    a EPPO Global Database VERIFICA (o nome francês daquele código realmente contém
    o termo francês? e o contexto de cultura bate?)

A verificação é o que quebra a circularidade: a proposta vem de uma fonte, a
confirmação vem de outra, e o que não confirma **não entra**.

    python3 motor/normalize_agro.py build     # constrói e salva o dicionário
    python3 motor/normalize_agro.py evaluate  # mede em amostra cega
"""
import csv, json, os, re, sys, unicodedata, random
from difflib import SequenceMatcher
from collections import Counter
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import _gavetas  # noqa: E402,F401 — poe as gavetas do processo no caminho
from eppo_gd import names as eppo_names

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EPHY = os.path.join(ROOT, 'data', 'raw', 'FR-T4-001')
ESDICT = os.path.join(ROOT, 'data', 'samples', 'ES-T4-001', 'eppo-dictionary.json')
OUT = os.path.join(ROOT, 'data', 'samples', 'X-007-canonical-agro-dictionary.json')

# Termos franceses que designam GRUPO, não espécie. Não devem receber código de
# espécie — recusar é o comportamento correto, não uma falha.
GROUP_HINTS = ('champignons', 'maladies', 'chenilles', 'insectes', 'ravageurs',
               'pucerons', 'acariens', 'nematodes', 'bacterioses', 'viroses',
               'desherbage', 'traitements', 'divers', 'autres', 'regul',
               'mouches', 'thrips', 'cicadelles', 'noctuelles', 'limaces')


def norm(s):
    s = unicodedata.normalize('NFD', (s or '').lower())
    s = ''.join(c for c in s if unicodedata.category(c) != 'Mn')
    s = re.sub(r'\(.*?\)', ' ', s)
    return re.sub(r'[^a-z0-9 ]', ' ', s).strip()


def toks(s):
    return {t for t in norm(s).split() if len(t) > 2}


def sim(a, b):
    return SequenceMatcher(None, norm(a), norm(b)).ratio()


def load_pairs():
    """Pares (cultura, alvo) do E-Phy, com o número de usos autorizados."""
    from collections import Counter
    c = Counter()
    with open(os.path.join(EPHY, 'usages_des_produits_autorises_utf8.csv'),
              encoding='utf-8') as f:
        for r in csv.DictReader(f, delimiter=';'):
            if not (r.get('etat usage') or '').startswith('Autoris'):
                continue
            q = [x.strip() for x in (r['identifiant usage'] or '').split('*')]
            if len(q) >= 3 and q[0] and q[2]:
                c[(q[0], q[2])] += 1
    return c


def es_dict():
    with open(ESDICT, encoding='utf-8') as f:
        return json.load(f)


PEST_INDEX = os.path.join(ROOT, 'data', 'raw', 'EPPO-CACHE', 'pest_fr_index.json')
_pidx = None


def pest_index():
    """Índice nome-francês → código EPPO de praga, construído da EPPO GD.

    Substitui a geração de candidatos via dicionário espanhol, que falhava em
    pares como `rouille`↔`roya`: a proximidade lexical entre francês e espanhol
    não é confiável, e medimos isso (`Blé × Rouille(s)` ficava UNRESOLVED).
    Agora o candidato vem do **nome francês da própria autoridade EPPO**.
    """
    global _pidx
    if _pidx is None:
        _pidx = {}
        if os.path.exists(PEST_INDEX):
            with open(PEST_INDEX, encoding='utf-8') as f:
                _pidx = json.load(f)
    return _pidx


def pest_candidates(fr_target):
    """Códigos cujo nome francês compartilha o termo do alvo francês."""
    ft = toks(fr_target)
    if not ft:
        return []
    out = []
    for code, e in pest_index().items():
        for name in e.get('fr', []):
            if ft & toks(name):
                out.append(code)
                break
    return out


def candidates(fr_term, es_entries, k=4):
    """(legado) Códigos EPPO candidatos propostos pelo dicionário espanhol."""
    scored = []
    ft = toks(fr_term)
    for code, e in es_entries.items():
        if not re.fullmatch(r'[A-Z0-9]{5,6}', code):
            continue
        best = max(sim(fr_term, e.get('es', '')), sim(fr_term, e.get('scientific', '')))
        # bônus quando compartilham um radical (mildiou~mildiu, oidium~oidio)
        for a in ft:
            for b in toks(e.get('es', '')):
                if len(a) > 4 and (a[:5] == b[:5] or b.startswith(a[:4])):
                    best = max(best, 0.62)
        if best > 0.5:
            scored.append((best, code))
    scored.sort(reverse=True)
    return [c for _, c in scored[:k]]


def verify(code, fr_term, fr_crop_names):
    """Confirma o candidato contra a EPPO GD. Devolve (match_type, prova)."""
    n = pest_index().get(code) or eppo_names(code)
    if 'fr' in n:
        n = {'ok': True, 'French': n['fr'], 'preferred': n.get('preferred')}
    if not n.get('ok'):
        return None, None
    fr = [x for x in n.get('French', [])]
    if not fr:
        return None, None
    ft = toks(fr_term)
    fallback = None
    for name in fr:
        nt = toks(name)
        if not (ft & nt):
            continue
        # O nome francês da EPPO cita a cultura? Então o par (cultura,alvo) resolve.
        # É preciso varrer TODOS os nomes antes de decidir: "mildiou de la grappe"
        # casa por termo, mas é "mildiou de la vigne" que casa por contexto — devolver
        # o primeiro que casa faria o desempate se perder.
        if fr_crop_names and (nt & fr_crop_names):
            return 'CONTEXTUAL', name
        if fallback is None and (norm(fr_term) == norm(name) or ft <= nt):
            fallback = name
    return ('EXACT', fallback) if fallback else (None, None)


CROP_INDEX = os.path.join(ROOT, 'data', 'raw', 'EPPO-CACHE', 'crop_fr_index.json')
_cidx = None


def crop_index():
    """Índice nome-francês → código EPPO, construído uma vez a partir da EPPO GD."""
    global _cidx
    if _cidx is None:
        _cidx = {}
        if os.path.exists(CROP_INDEX):
            with open(CROP_INDEX, encoding='utf-8') as f:
                _cidx = json.load(f)
    return _cidx


# Culturas francesas que são GRUPO de espécies, não espécie. Recusar é o certo.
CROP_GROUPS = ('traitements', 'cruciferes', 'fruits a', 'legumes', 'cultures',
               'especes', 'plantes', 'arbres', 'graines', 'porte graine',
               'cereales', 'a paille', 'florales', 'gazon', 'jachere')


def resolve_crop(fr_crop):
    """FR cultura → (código EPPO, científico, nome francês da EPPO, tokens)."""
    if any(g in norm(fr_crop) for g in CROP_GROUPS):
        return None, None, None, set(toks(fr_crop))
    ft = toks(fr_crop)
    best = None
    for code, e in crop_index().items():
        for name in e.get('fr', []):
            nt = toks(name)
            if not nt:
                continue
            if norm(name) == norm(fr_crop):
                return code, e.get('preferred'), name, ft | nt
            if ft and ft <= nt and (best is None or len(nt) < len(best[3])):
                best = (code, e.get('preferred'), name, nt)
    if best:
        return best[0], best[1], best[2], ft | set(best[3])
    return None, None, None, ft


def build(pairs, esd, limit):
    """Constrói o dicionário canônico para os `limit` pares de maior valor."""
    crop_cache, out = {}, []
    for (crop, target), uses in pairs.most_common(limit):
        if crop not in crop_cache:
            crop_cache[crop] = resolve_crop(crop)
        ccode, csci, cname, cnametoks = crop_cache[crop]
        rec = {'ORIGINAL_COUNTRY': 'FRANCE', 'ORIGINAL_CROP': crop,
               'ORIGINAL_TARGET': target, 'USES': uses,
               'EPPO_CROP': ccode, 'CANONICAL_CROP': csci,
               'EPPO_TARGET': None, 'CANONICAL_TARGET': None,
               'SCIENTIFIC_NAME': None, 'EVIDENCE': None, 'MATCH_TYPE': None}
        if any(h in norm(target) for h in GROUP_HINTS):
            rec['MATCH_TYPE'] = 'GROUP'
            rec['EVIDENCE'] = 'termo francês designa grupo, não espécie — recusado por desenho'
            out.append(rec)
            continue
        hits = []
        for code in pest_candidates(target):
            mt, proof = verify(code, target, cnametoks)
            if mt:
                hits.append((mt, code, proof))
        # A desambiguação é feita pelo CONTEXTO DE CULTURA: entre vários candidatos
        # verificados, vence aquele cujo nome francês da EPPO cita a cultura francesa
        # do próprio par. "mildiou de la vigne" resolve Vigne × Mildiou(s);
        # o mesmo alvo em Tomate resolve para outro código, e é assim que deve ser.
        # Desempate por contexto de cultura. Quando SOBRA MAIS DE UM candidato e todos
        # citam a cultura do par, a resposta certa NÃO é "ambíguo": é **grupo**.
        # O registro francês escreve `Rouille(s)`, `Septoriose(s)`, `Oïdium(s)` no plural
        # exatamente porque o termo cobre várias espécies na mesma cultura. Forçar uma
        # espécie única aí seria inventar precisão que a fonte não tem.
        ctx = sorted({h[1] for h in hits if h[0] == 'CONTEXTUAL'})
        if not hits:
            rec['MATCH_TYPE'] = 'UNRESOLVED'
            rec['EVIDENCE'] = 'nenhum candidato foi confirmado pela EPPO GD'
        elif len(ctx) > 1:
            names = {c: (pest_index().get(c) or {}).get('preferred') for c in ctx}
            rec['MATCH_TYPE'] = 'GROUP_SCOPED'
            rec['EPPO_TARGET'] = ctx
            rec['CANONICAL_TARGET'] = [names[c] for c in ctx]
            rec['SCIENTIFIC_NAME'] = [names[c] for c in ctx]
            rec['EVIDENCE'] = ('grupo delimitado pela cultura — EPPO GD confirma para '
                               + rec['ORIGINAL_CROP'] + ': '
                               + ', '.join(f'{c} ({names[c]})' for c in ctx))
        elif not ctx:
            rec['MATCH_TYPE'] = 'AMBIGUOUS'
            rec['EVIDENCE'] = ('candidatos verificados mas nenhum citando a cultura: '
                               + ', '.join(sorted({h[1] for h in hits})))
        else:
            exact = [h for h in hits if h[1] == ctx[0]]
            mt, code, proof = exact[0]
            n = pest_index().get(code) or eppo_names(code)
            rec.update({'MATCH_TYPE': mt, 'EPPO_TARGET': code,
                        'SCIENTIFIC_NAME': n.get('preferred'),
                        'CANONICAL_TARGET': n.get('preferred'),
                        'EVIDENCE': f'EPPO GD {code}: nome francês "{proof}"'})
        out.append(rec)
    return out


def summarise(recs, titulo):
    from collections import Counter
    c = Counter(r['MATCH_TYPE'] for r in recs)
    n = len(recs)
    print(f'\n=== {titulo} ({n} pares)')
    for k in ('EXACT', 'CONTEXTUAL', 'GROUP_SCOPED', 'GROUP', 'AMBIGUOUS', 'UNRESOLVED'):
        print(f'   {k:11s} {c[k]:4d}  {100*c[k]/n:5.1f}%')
    resolved = c['EXACT'] + c['CONTEXTUAL'] + c['GROUP_SCOPED']
    nongroup = n - c['GROUP']
    print(f'   resolvidos: {resolved}/{n} = {100*resolved/n:.1f}% do total; '
          f'{100*resolved/nongroup:.1f}% dos que não são grupo')
    crops = sum(1 for r in recs if r['EPPO_CROP'])
    print(f'   cultura com EPPO: {crops}/{n} = {100*crops/n:.1f}%')
    return c


def evaluate(pairs, esd):
    """Amostra cega: pares que NÃO estão entre os 40 de construção.

    As regras (contexto de cultura, plural = grupo, recusa de grupo francês) foram
    desenhadas olhando os 40 pares de maior valor. A amostra cega mede se elas
    valem fora deles.
    """
    top = [k for k, _ in pairs.most_common(40)]
    resto = [k for k in pairs if k not in set(top)]
    rng = random.Random(20260828)
    rng.shuffle(resto)
    blind = resto[:60]
    sub = Counter({k: pairs[k] for k in blind})
    recs = build(sub, esd, len(blind))
    c = summarise(recs, 'AMOSTRA CEGA (60 pares fora da construção)')
    with open(OUT, encoding='utf-8') as f:
        prev = json.load(f)
    prev['blind'] = {'pairs': len(recs), 'by_match_type': dict(c),
                     'resolved': c['EXACT'] + c['CONTEXTUAL'] + c['GROUP_SCOPED'],
                     'records': recs}
    with open(OUT, 'w', encoding='utf-8') as f:
        json.dump(prev, f, ensure_ascii=False, indent=2)
    return recs


# ═══════════════════════════════════════════════════════════════════════════
# A IDENTIDADE DO PROBLEMA NUM TEXTO JÁ GUARDADO — sem rede, e sem parecido-com
# ═══════════════════════════════════════════════════════════════════════════
#
# O estudo da Intelligence mediu, na linha dela, 7.078 registos e 836 com
# `ISSUE_ID` utilizável — 11,8 % — e disse que havia nomes de praga e de doença
# **já presentes no texto** sem identidade estruturada nenhuma.
#
# Medido outra vez, nesta árvore, contra os textos REAIS que já estão guardados
# (`data/derivados/texto/*.txt`, 43 ficheiros extraídos de documentos italianos):
#
#     34 dos 43 contêm um BINÓMIO LATINO que casa EXACTAMENTE com o nome
#     científico de uma entrada do dicionário EPPO que esta casa já tem.
#
# Isso é reprocessável **sem coleta nova**, e é o que esta função faz.
#
# ── AS QUATRO RECUSAS, E SÃO ELAS QUE TORNAM ISTO DEFENSÁVEL ────────────────
#
# 1 · NADA DE PARECIDO-COM. Só casamento exacto, palavra inteira, do binómio
#     latino. `SequenceMatcher` existe neste ficheiro e NÃO é usado aqui: um
#     `ratio()` alto entre dois nomes de espécie é a maneira mais rápida de
#     fabricar um `ISSUE_ID` que ninguém vai reabrir.
#
# 2 · NOME COMUM ITALIANO NÃO CUNHA NADA. `peronospora`, `oidio`, `botrite`,
#     `ticchiolatura` estão nos boletins às dezenas — e esta árvore NÃO tem
#     autoridade italiano→EPPO nenhuma. Sem autoridade, `ISSUE_ID = UNKNOWN`
#     e o termo original fica preservado. Inventar o código a partir da
#     semelhança com o espanhol seria exactamente o defeito que a `COL-LAW-034`
#     proíbe: junção por semelhança textual.
#
#         VITE · VITE DA VINO · VINE PARECEM-SE E NÃO SE AUTORIZAM.
#
# 3 · UMA MENÇÃO NÃO É UMA OCORRÊNCIA. O nome sai daqui como `ISSUE_MENTION`,
#     nunca como «esta praga ocorreu». A `COL-LAW-032` já tinha escrito a mesma
#     lei para o lugar — *«MENÇÃO NÃO É FATO»* — e um boletim que LISTA trinta
#     pragas num índice não afirma trinta ocorrências.
#
# 4 · A NORMALIZAÇÃO NÃO DESTRÓI O ORIGINAL (COL-LAW-203). O que sai traz o
#     termo tal como está no texto, a posição onde foi encontrado, a autoridade
#     que confirmou e a versão da regra — para que um erro de amanhã seja
#     reprocessável em vez de permanente.
#
# ⚠️ E NÃO HÁ REDE AQUI. `pest_index()` e `crop_index()` vão à EPPO Global
# Database e guardam cache em `data/raw/EPPO-CACHE/`, que NÃO existe nesta
# árvore. Esta função lê só o dicionário que já está no repositório.
VERSAO_DA_REGRA_DE_MENCAO = 'mencao-eppo-v1'

#: Uma menção é do que o texto NOMEIA. Estas duas palavras separam o que a
#: função faz do que ela NÃO faz, e são parte do resultado.
ISSUE_MENTION = 'ISSUE_MENTION'
ISSUE_OCCURRENCE = 'ISSUE_OCCURRENCE'   # NUNCA devolvido aqui.

_BINOMIO = re.compile(r'^[A-Z][a-z]{2,}\s+[a-z][a-z.\-]{2,}$')


def _binomios_do_dicionario(tabela):
    """`{forma normalizada: (codigo, cientifico)}`, só para binómios de verdade.

    O dicionário do MAPA mistura espécies com GRUPOS — `3WEEDT` tem
    `scientific = "Malas hierbas"`, que não é um nome científico nenhum. Deixar
    um grupo entrar aqui faria a frase «malas hierbas» de um texto qualquer
    cunhar um código de praga.

        UM GRUPO NÃO É UMA ESPÉCIE, E UM RÓTULO DE GAVETA NÃO É UM TÁXON.

    ⚠️ E A FORMA NÃO CHEGA — ISTO FOI MEDIDO A FALHAR.
    A primeira versão só olhava para o FEITIO do nome (`Xxxx yyyy`), e
    `"Malas hierbas"` tem exactamente esse feitio: maiúscula, minúscula, duas
    palavras. O ataque passou:

        mencoes_de_problema("malas hierbas no campo")  ->  3WEEDT

    O que separa um táxon de um rótulo não é o feitio: é a tabela dizer a MESMA
    coisa nas duas colunas. Quando o MAPA não tem nome científico para uma
    gaveta, ele repete o nome comum na coluna científica — e é essa repetição
    que denuncia a gaveta.

        PARECER UM NOME CIENTÍFICO != SER UM NOME CIENTÍFICO.
    """
    fora = {}
    for codigo, v in tabela.items():
        cientifico = (v.get('scientific') or '').strip()
        comum = (v.get('es') or '').strip()
        if not _BINOMIO.match(cientifico):
            continue
        if comum and norm(comum) == norm(cientifico):
            continue
        fora.setdefault(norm(cientifico), (codigo, cientifico))
    return fora


def mencoes_de_problema(texto, dicionario=None):
    """Os problemas que ESTE texto NOMEIA, com o código EPPO que os confirma.

    Devolve uma lista de recibos. Cada um diz o que foi encontrado, onde, qual
    a autoridade e o que isto NÃO afirma. Texto sem binómio nenhum devolve `[]`
    — e `[]` quer dizer «não encontrei nome que eu saiba confirmar», nunca
    «não há problema nenhum aqui».

        NENHUMA MENÇÃO ENCONTRADA != NENHUM PROBLEMA NO DOCUMENTO.
    """
    dic = dicionario if dicionario is not None else es_dict()
    alvo = norm(texto or '')
    if not alvo.strip():
        return []
    fora = []
    for chave, (codigo, cientifico) in sorted(_binomios_do_dicionario(dic['pests']).items()):
        at = re.search(r'(?<![a-z0-9])' + re.escape(chave) + r'(?![a-z0-9])', alvo)
        if not at:
            continue
        fora.append({
            'ESPECIE_DO_ACHADO': ISSUE_MENTION,
            'ISSUE_EPPO': codigo,
            'ISSUE_CANONICO': cientifico,
            # COL-LAW-203: o valor original nunca se perde.
            'TERMO_ORIGINAL': cientifico,
            'ONDE': at.start(),
            'COMO': 'CASAMENTO_EXACTO_DE_BINOMIO_LATINO',
            'AUTORIDADE': 'data/samples/ES-T4-001/eppo-dictionary.json '
                          '(tabelas oficiais do MAPA · ES-T4-001)',
            'RULE_VERSION': VERSAO_DA_REGRA_DE_MENCAO,
            'O_QUE_ISTO_NAO_AFIRMA':
                'que o problema OCORREU, nem onde, nem quando. E uma mencao '
                'nomeada no texto (COL-LAW-032: MENCAO NAO E FATO).',
        })
    return fora


def termos_sem_autoridade(texto, vocabulario):
    """Os nomes comuns que o texto usa e que esta casa NÃO sabe traduzir.

    Existe para a lacuna ser DIZÍVEL. Sem isto, um boletim cheio de
    `peronospora` sai com zero menções e parece um documento sem problema
    nenhum — quando a verdade é que o problema está lá e falta a autoridade.

        NOT_IN_AUTHORITY != NOT_A_PROBLEM != REJECTED_BY_LAW
    """
    alvo = norm(texto or '')
    fora = []
    for termo in vocabulario:
        chave = norm(termo)
        at = re.search(r'(?<![a-z0-9])' + re.escape(chave) + r'(?![a-z0-9])', alvo)
        if at:
            fora.append({
                'TERMO_ORIGINAL': termo,
                'ISSUE_EPPO': 'UNKNOWN',
                'ONDE': at.start(),
                'PORQUE': 'NO_AUTHORITY_FOR_THIS_LANGUAGE: esta arvore nao tem '
                          'crosswalk italiano->EPPO. Cunhar um codigo por '
                          'semelhanca com o espanhol seria juncao por semelhanca '
                          'textual, que a COL-LAW-034 proibe.',
                'RULE_VERSION': VERSAO_DA_REGRA_DE_MENCAO,
            })
    return fora


if __name__ == '__main__':
    cmd = sys.argv[1] if len(sys.argv) > 1 else 'build'
    pairs, esd = load_pairs(), es_dict()
    if cmd == 'evaluate':
        evaluate(pairs, esd)
    elif cmd == 'build':
        recs = build(pairs, esd, 40)
        c = summarise(recs, 'CONSTRUÇÃO (40 pares de maior valor)')
        with open(OUT, 'w', encoding='utf-8') as f:
            json.dump({'source': 'derivado de FR-T4-001 (E-Phy), ES-T4-001 (MAPA) e '
                                 'EPPO Global Database (gd.eppo.int)',
                       'sources': ['FR-T4-001', 'ES-T4-001', 'EU-T3-001'],
                       'captured_at': '2026-08-28',
                       'SOURCE_LOCATION': 'FRANCE / SPAIN / EPPO',
                       'FACT_LOCATION': 'FRANCE (o par normalizado é o uso francês)',
                       'ORIGINAL_LANGUAGE': 'FR', 'set': 'CONSTRUCTION',
                       'records': recs}, f, ensure_ascii=False, indent=2)
        print(f'\ngravado: {OUT}')
