#!/usr/bin/env python3
"""
MATRIZ DO RECORTE — que COUNTRY×CROP×ISSUE já tem lastro no acervo.

    python3 scripts/matriz_recorte.py                # tabela legível
    python3 scripts/matriz_recorte.py --json         # máquina
    python3 scripts/matriz_recorte.py --build        # grava o artefato

POR QUE ESTE ARQUIVO EXISTE
----------------------------
A arbitragem do Early Signal devolveu `EARLY_SIGNAL_ENGINE = NOT_PROVED`, e a causa medida
foi **`NO_OVERLAP_OF_OBSERVATION`**: a camada de voz do acervo é majoritariamente OLIVAR,
e boa parte dos temas testados era CEREAL e MILHO. As duas coisas nunca se encontraram no
mesmo par crop×issue, e um confronto temporal entre camadas que não se sobrepõem não pode
dar outra coisa senão "não provado".

    NOT_PROVED != REFUTED. O que falhou foi o DESENHO, não a hipótese.

Então o recorte do piloto deixa de ser escolhido por interesse e passa a ser **derivado**:
só entra o par que já tem evidência em outras camadas, porque é nele que a voz nova terá
com o que ser confrontada depois.

A HONESTIDADE DESTA MEDIDA — leia antes de usar o número
---------------------------------------------------------
O que este script mede é **MENÇÃO do par no artefato de uma camada**, não leitura do
conteúdo daquela camada. Um artefato de FIELD que cita "olivar" e "repilo" entra como
lastro de FIELD para OLIVE×REPILO; isso não afirma quantas leituras de campo existem nem
que elas sejam boas.

    MENTION != EVIDENCE. LAYER_HIT != LAYER_STRENGTH.

O número serve para **ordenar candidatos**, exatamente como o índice de exposição ordena
províncias sem dimensionar nada. Quem promove um par a caso lê os artefatos citados.

O ACENTO, QUE JÁ CUSTOU UMA CLASSIFICAÇÃO INTEIRA
---------------------------------------------------
O handoff lista como bug reincidente: `agronom` não casa "agrónomo". Todo termo aqui passa
por `_norm()`, que tira acento e caixa **antes** de comparar — e o vocabulário é
multilíngue de propósito, porque o mesmo problema se escreve `repilo`, `peacock spot`,
`fusariosi`, `fusariose` e `mildiou` conforme o país.

TERMOS CURTOS FICAM DE FORA
-----------------------------
`DON` (deoxinivalenol) e `rust` sozinho casariam dentro de outras palavras e em prosa
comum. Termo com menos de 5 letras só entra como palavra inteira, nunca como pedaço.

O DEFEITO QUE A PRIMEIRA VERSÃO DESTE ARQUIVO TEVE, E COMO ELE FOI PEGO
-------------------------------------------------------------------------
A primeira versão perguntava *"este ARQUIVO cita o país X, a cultura Y e o problema Z?"*.
Rodou, fechou, e devolveu com 8 camadas de lastro:

    IT · MAIZE · REPILO          repilo é doença de OLIVEIRA
    FR · OLIVE · REPILO          não há olivar francês nesta história
    ES · MAIZE · DOWNY_MILDEW    mildiu ali é da VIDEIRA

A causa: arquivos agregados — o ledger de métricas, o Atlas de fontes, o handoff, o radar —
citam vários países, várias culturas e vários problemas **no mesmo arquivo**. Perguntar
pelo arquivo inteiro devolve o **produto cartesiano** de tudo que ele menciona, e o
resultado fecha bonito enquanto mede outra coisa.

    CO-OCORRÊNCIA NO DOCUMENTO != PAR.

A correção é proximidade: a cultura tem de aparecer a menos de `JANELA` caracteres do
problema, na mesma vizinhança de texto — isto é, no mesmo registro, na mesma frase, na
mesma linha de tabela. País segue a mesma regra, com uma concessão declarada: se o próprio
arquivo declara `COUNTRY` ou `FACT_LOCATION`, isso vale como país sem exigir vizinhança,
porque é campo estruturado e não prosa.

É a mesma lição que o repositório já pagou duas vezes em outro lugar: *"cobertura que sobe
porque o classificador ficou permissivo"*. Aqui a contagem subiu porque o casamento ficou
frouxo, e o número alto era o sintoma, não o resultado.
"""
import json
import os
import re
import sys
import unicodedata

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SAMPLES = os.path.join(ROOT, 'data', 'samples')
DOCS = os.path.join(ROOT, 'docs')
DEST = os.path.join(SAMPLES, 'PILOT-SCOPE-MATRIX-V1.json')

# ------------------------------------------------------------------------ vocabulário
# Multilíngue por necessidade: o mesmo problema tem nome diferente em cada país, e o
# acervo mistura ES, IT, FR, EN e PT.
# O PORTUGUÊS NÃO É OPCIONAL AQUI, E A PRIMEIRA VERSÃO O ESQUECEU.
# Sem `videira` e `flavescencia`, o recorte IT·VINE·FLAVESCENCE saiu com ZERO camadas —
# não porque o acervo não o cite, mas porque o `ITALY-RADAR-DO-FUTURO-V1.json` o escreve
# em PORTUGUÊS ("videira x flavescencia"), que é a língua dos documentos desta casa.
# A ausência tinha cara de "não existe" e era "não procurei na língua certa".
#
#     NOT COLLECTED != DOES NOT EXIST — e aqui a lei se aplicou ao meu próprio vocabulário.
CROPS = {
    'OLIVE': ['olive', 'olivo', 'olivar', 'olivier', 'oliva', 'olea europaea', 'aceituna',
              'oliveira', 'azeitona'],
    'MAIZE': ['maize', 'maiz', 'mais', 'milho', 'corn', 'zea mays'],
    'CEREAL': ['cereal', 'cereali', 'wheat', 'trigo', 'frumento', 'ble', 'triticum',
               'cebada', 'orzo', 'barley', 'orge', 'cevada', 'aveia'],
    'DURUM_WHEAT': ['durum', 'grano duro', 'trigo duro', 'ble dur', 'frumento duro'],
    'VINE': ['vineyard', 'grapevine', 'vigne', 'vite', 'vid ', 'vitis', 'viticola',
             'vina', 'uva', 'videira', 'vinha', 'vinedo'],
}

ISSUES = {
    'REPILO': ['repilo', 'venturia oleaginea', 'spilocaea', 'peacock spot'],
    'VERTICILLIUM': ['verticillium', 'verticilosis'],
    'XYLELLA': ['xylella'],
    'OLIVE_PESTS': ['bactrocera', 'prays oleae', 'olive fruit fly', 'mosca del olivo'],
    'AMARANTHUS': ['amaranthus', 'palmeri'],
    'HERBICIDE_RESISTANCE': ['herbicide resistance', 'herbicide-resistant',
                             'resistencia a herbicida', 'lolium rigidum',
                             'resistance aux herbicides'],
    'SEPTORIA': ['septoria', 'zymoseptoria', 'septoriosi', 'septoriose'],
    'FUSARIUM': ['fusarium', 'fusariosi', 'fusariose', 'mycotoxin', 'micotossin',
                 'micotoxina', 'mycotoxine', 'deoxynivalenol', 'aflatox'],
    'DOWNY_MILDEW': ['plasmopara', 'mildiu', 'mildiou', 'peronospora', 'downy mildew',
                     'mildio'],
    'FLAVESCENCE': ['flavescence', 'flavescenza', 'flavescencia', 'phytoplasma',
                    'fitoplasma'],
    'RUST': ['puccinia', 'roya', 'ruggine', 'rouille', 'ferrugem'],
}

PAISES = {
    'ES': ['spain', 'espana', 'espanha', 'spagna', 'espagne', 'andaluc', 'cordoba',
           'jaen', 'sevilla', 'aragon', 'catalunya', 'cataluna', '"es"', 'ropf'],
    'IT': ['italy', 'italia', 'italie', 'veneto', 'lombardia', 'piemonte', 'puglia',
           'emilia', 'toscana', 'marche', 'umbria', 'friuli'],
    'FR': ['france', 'francia', 'franca', 'french', 'ephy', 'inrae', 'agreste',
           'occitanie', 'bourgogne', 'nouvelle-aquitaine'],
}

# ---------------------------------------------------------------------------- camadas
# Cada camada é reconhecida por padrões no NOME do arquivo. Derivado dos SOURCE_IDs que o
# repositório já usa — não é uma taxonomia nova.
CAMADAS = [
    ('SCIENCE', [r't5-\d', r'corpus-documentos', r'openalex', r'ciencia']),
    ('RESEARCHER', [r'researcher', r'pesquisador', r'speaker-universe']),
    ('FIELD', [r't3-\d', r'raif', r'sensores', r'coorte', r'pressao']),
    ('REGULATORY', [r't4-\d', r'ropf', r'regfi', r'ephy', r'regulator', r'denomina']),
    ('VOICE', [r't8-\d', r'voice', r'voz', r'linkedin', r'youtube', r'instagram']),
    ('TECHNICAL_ORGANIZATION', [r't7-\d', r'media-routes', r'organiza', r'cooperativ']),
    ('RADAR', [r'radar']),
    ('COMPETITOR', [r'competitor', r'concorrente']),
    ('PORTFOLIO', [r'portfolio', r'adama', r'catalogo']),
    ('CASE', [r'case-\d', r'caso', r'hero']),
    ('CROP_SCALE', [r'area', r'nuts2', r'crop-area', r'escala', r'distribution']),
]


def _norm(s):
    s = unicodedata.normalize('NFKD', str(s))
    s = ''.join(c for c in s if not unicodedata.combining(c))
    return s.lower()


# Vizinhança em caracteres. 400 cobre um registro JSON típico e um parágrafo de tabela,
# e é curta o bastante para não atravessar seções de um documento agregado.
JANELA = 400


def _padrao(termos):
    """Um regex por grupo. Termo curto vira palavra inteira; longo casa como pedaço."""
    ps = []
    for t in termos:
        t = _norm(t).strip()
        ps.append(r'\b%s\b' % re.escape(t) if len(t) < 5 else re.escape(t))
    return re.compile('|'.join(ps))


def _tem(texto, termos):
    m = _padrao(termos).search(texto)
    return m.group(0) if m else None


def _perto(texto, base, alvo, janela=JANELA):
    """Ocorrências de `base` que têm `alvo` a menos de `janela` caracteres.

    É isto que separa PAR de CO-OCORRÊNCIA. Sem a janela, um arquivo que fala de cinco
    culturas e seis problemas afirma trinta pares que ninguém escreveu.
    """
    pb, pa = _padrao(base), _padrao(alvo)
    for m in pb.finditer(texto):
        i, j = m.start(), m.end()
        if pa.search(texto[max(0, i - janela):j + janela]):
            return m.group(0)
    return None


def _camada(nome):
    n = _norm(nome)
    for camada, pats in CAMADAS:
        for p in pats:
            if re.search(p, n):
                return camada
    return None


def _arquivos():
    for base, exts in ((SAMPLES, ('.json',)), (DOCS, ('.md', '.json'))):
        for raiz, _, nomes in os.walk(base):
            for n in sorted(nomes):
                if n.endswith(exts):
                    yield os.path.join(raiz, n)


def varrer():
    """→ {(pais, crop, issue): {camada: [arquivos]}}. Derivado, nunca digitado."""
    achados = {}
    lidos, pulados = 0, 0
    for caminho in _arquivos():
        rel = os.path.relpath(caminho, ROOT).replace('\\', '/')
        camada = _camada(rel)
        if not camada:
            continue
        try:
            with open(caminho, encoding='utf-8') as f:
                bruto = f.read()
        except (OSError, UnicodeDecodeError):
            pulados += 1
            continue
        lidos += 1
        texto = _norm(bruto)
        # País declarado em campo estruturado vale sem exigir vizinhança — é declaração,
        # não prosa. O resto tem de estar perto do problema.
        declarados = set()
        for m in re.finditer(r'"(?:country|country_of_person|fact_location|'
                             r'country_of_affiliation)"\s*:\s*"([a-z]{2})"', texto):
            if m.group(1).upper() in PAISES:
                declarados.add(m.group(1).upper())
        for crop, ct in CROPS.items():
            for issue, it in ISSUES.items():
                # O par só existe se cultura e problema estiverem na MESMA vizinhança.
                if not _perto(texto, it, ct):
                    continue
                paises = set(declarados)
                for p, pt in PAISES.items():
                    if _perto(texto, it, pt):
                        paises.add(p)
                for pais in paises:
                    achados.setdefault((pais, crop, issue), {}) \
                           .setdefault(camada, []).append(rel)
    return achados, lidos, pulados


# ------------------------------------------------------------------- os seis do piloto
# ESTES SEIS FORAM CONGELADOS PELA ABA ÁRBITRA em 2026-08-30, ANTES da coleta. Esta aba
# é a COLETORA e não os escolheu: ela os recebe. A regra que vem junto é dura, e existe
# para impedir o vício mais comum de experimento:
#
#     não trocar recorte no meio · não afrouxar limiar · não otimizar o desenho
#     depois de ver o resultado
#
# Um recorte que não conseguir sobreposição sai como `OVERLAP_FAILED` e FICA. Substituí-lo
# por outro mais conveniente depois de ver os dados transformaria o piloto num gerador de
# resultado bonito.
#
# NOTA DE COBERTURA DA MEDIDA: o acervo italiano de CASO vive na branch
# `claude/sintonia-italy-pilot-b1l401` e NÃO está nesta árvore. A varredura lê só esta
# árvore e portanto SUBESTIMA a Itália — `IT·VINE·FLAVESCENCE` e `IT·DURUM_WHEAT·FUSARIUM`
# têm lastro lá que não aparece aqui. Onde isso ocorre, o caso diz de onde vem.
CASOS = [
    ('ES', 'OLIVE', 'REPILO', 'FROZEN_BY_ARBITER',
     'o par mais lastreado de todo o acervo, e o único com série de campo longa: RAIF, 23 '
     'safras, 148.964 leituras. É o único caso em que um confronto temporal posterior tem '
     'baseline real. A voz JÁ existe aqui (252 vídeos, 16 vozes técnicas de olivar), então '
     'a sobreposição está garantida por construção — exatamente o que faltou na rodada '
     'que deu NO_OVERLAP_OF_OBSERVATION.'),
    ('ES', 'CEREAL', 'SEPTORIA', 'FROZEN_BY_ARBITER',
     '6 camadas medidas nesta árvore (CASE, FIELD, PORTFOLIO, RADAR, RESEARCHER, SCIENCE) '
     'e 14 artefatos — o segundo par espanhol mais lastreado. VOICE NÃO aparece entre as '
     'camadas: é o lado cereal do desencontro que a arbitragem nomeou, e é aqui que a voz '
     'nova tem de cair para fechá-lo. Tem hero case próprio (ES-HERO-003-CEREAIS-SEPTORIA) '
     'e campo em ES-T3-002-raif-cereales-invierno.'),
    ('IT', 'VINE', 'FLAVESCENCE', 'FROZEN_BY_ARBITER',
     'o radar italiano registra videira × flavescência como caso CORRENTE (IT-HERO-001), '
     'com janela de monitoramento aberta — por isso ele não entrou como tema futuro. Caso '
     'aberto é o melhor lugar para testar sensor humano: existe o que confrontar. A rota '
     'gratuita achou o recorte mais denso da Itália aqui: 75 obras e 216 autores com '
     'afiliação italiana na janela 2022-2026.'),
    ('IT', 'DURUM_WHEAT', 'FUSARIUM', 'FROZEN_BY_ARBITER',
     'é o caso IT-CASE-DURUM-FUSARIUM-001, onde a camada de voz humana JÁ foi medida e '
     'deu HUMAN_SENSOR_ADDS_NOTHING_IN_THIS_PANEL: 8 alvos, 4 com identidade resolvível, '
     '3 posts em um ano inteiro, 0 sinais do caso. Funciona como controle negativo '
     'conhecido — um piloto sem um "não" já medido não distingue rota boa de sorte. A '
     'perna de campo existe (LaMMA, boletim de 23/04/2026).'),
    ('FR', 'VINE', 'DOWNY_MILDEW', 'FROZEN_BY_ARBITER',
     'o par francês mais lastreado da varredura: 6 camadas. É também o par regulatório '
     'número um do país no dicionário canônico — "Vigne / Mildiou(s)", 168 usos em X-007 — '
     'e tem comunidade científica densa e datável (IFV e INRAE): 100 obras, 278 autores.'),
    ('FR', 'CEREAL', 'SEPTORIA', 'FROZEN_BY_ARBITER',
     'espelha ES·CEREAL·SEPTORIA, e o mesmo par nos dois países permite comparação '
     'cross-market pela molécula — o eixo que o repositório já provou forte (X-006 cobre '
     '82,1% do uso). A ciência francesa de septoriose é a mais densa que a rota gratuita '
     'achou em qualquer país: 147 obras e 326 autores na janela.'),
]

# A assimetria francesa, declarada ANTES de coletar para não ser descoberta depois.
ASSIMETRIA_FR = (
    'a França NÃO tem camada de campo provada nestes testes. Nenhum LEAD_DAYS francês '
    'pode ser fabricado contra campo. Os dois recortes franceses servem a cobertura, '
    'cross-market, voz técnica, regulatório, área e sobreposição — e qualquer antecedência '
    'francesa só é mensurável se existir T1 real em outra camada datada.')


def selecionar(achados):
    idx = {}
    for (p, c, i), camadas in achados.items():
        idx[(p, c, i)] = camadas
    fora = []
    for pais, crop, issue, papel, porque in CASOS:
        camadas = idx.get((pais, crop, issue), {})
        fora.append({
            'CASE_ID': '%s-%s-%s' % (pais, crop, issue),
            'COUNTRY': pais, 'CROP': crop, 'ISSUE': issue,
            'DESIGN_ROLE': papel,
            'EXISTING_LAYERS': sorted(camadas),
            'LAYER_COUNT': len(camadas),
            'ARTEFACT_COUNT': sum(len(v) for v in camadas.values()),
            'ARTEFACTS_BY_LAYER': {k: sorted(set(v))[:6] for k, v in sorted(camadas.items())},
            'WHY_SELECTED': porque,
            'MEASURED_IN_THIS_TREE': bool(camadas),
            'SPEAKERS_TARGET': '3-5',
            'SPEAKERS_RESOLVED': 0,
            'PUBLIC_CHANNEL_STATUS': 'NOT_TESTED',
            'CONTENT_STATUS': 'NOT_COLLECTED',
        })
    return fora


def montar():
    achados, lidos, pulados = varrer()
    linhas = []
    for (pais, crop, issue), camadas in achados.items():
        linhas.append({
            'COUNTRY': pais, 'CROP': crop, 'ISSUE': issue,
            'EXISTING_LAYERS': sorted(camadas),
            'LAYER_COUNT': len(camadas),
            'ARTEFACT_COUNT': sum(len(v) for v in camadas.values()),
            'ARTEFACTS_BY_LAYER': {k: sorted(set(v))[:6] for k, v in sorted(camadas.items())},
        })
    linhas.sort(key=lambda r: (-r['LAYER_COUNT'], -r['ARTEFACT_COUNT'],
                               r['COUNTRY'], r['CROP'], r['ISSUE']))
    return {
        'SOURCE_ID': 'PILOT-SCOPE-MATRIX-V1',
        'source': 'varredura derivada de data/samples e docs — nenhuma coleta',
        'SOURCE_LOCATION': 'derivado',
        'FACT_LOCATION': 'n/a — descreve o acervo, não o mundo',
        'ORIGINAL_LANGUAGE': 'pt',
        'EVIDENCE_CLASS': 'DERIVED_MEASUREMENT',
        'PARA_QUE_SERVE': ('ordenar candidatos a recorte do piloto pelo lastro que já '
                           'existe no acervo, para não repetir NO_OVERLAP_OF_OBSERVATION'),
        'O_QUE_ISTO_MEDE': 'MENÇÃO do par no artefato de uma camada',
        'O_QUE_ISTO_NAO_MEDE': [
            'não mede a força da camada — MENTION != EVIDENCE',
            'não mede quantas leituras de campo, quantos papers ou quantos vídeos',
            'não afirma que o artefato trate do par: afirma que o cita',
            'não é lugar do fato: o país aqui é o país citado no artefato',
        ],
        'VOCABULARY_IS_MULTILINGUAL': 'o mesmo problema muda de nome por país',
        'SHORT_TERM_RULE': 'termo com menos de 5 letras só casa como palavra inteira',
        'FILES_READ': lidos, 'FILES_SKIPPED': pulados,
        'PAIRS_FOUND': len(linhas),
        'FROZEN_BY': 'aba ÁRBITRA, 2026-08-30, ANTES da coleta',
        'FROZEN_RULE': ('não trocar recorte, não afrouxar limiar, não otimizar o desenho '
                        'depois de ver o resultado. Recorte sem sobreposição sai '
                        'OVERLAP_FAILED e fica.'),
        'FRENCH_ASYMMETRY': ASSIMETRIA_FR,
        'SELECTED_CASES': selecionar(achados),
        'ROWS': linhas,
    }


if __name__ == '__main__':
    d = montar()
    if '--json' in sys.argv:
        print(json.dumps(d, ensure_ascii=False, indent=1))
    elif '--build' in sys.argv:
        quando = '2026-08-30'
        d['captured_at'] = quando
        d['CAPTURED_AT'] = quando
        with open(DEST, 'w', encoding='utf-8') as f:
            json.dump(d, f, ensure_ascii=False, indent=1)
        print('gravado:', os.path.relpath(DEST, ROOT))
    else:
        print('%d arquivos lidos · %d pares' % (d['FILES_READ'], d['PAIRS_FOUND']))
        print('%-3s %-12s %-22s %-3s %-4s %s' % (
            'P', 'CROP', 'ISSUE', 'CAM', 'ART', 'CAMADAS'))
        for r in d['ROWS'][:40]:
            print('%-3s %-12s %-22s %-3d %-4d %s' % (
                r['COUNTRY'], r['CROP'], r['ISSUE'], r['LAYER_COUNT'],
                r['ARTEFACT_COUNT'], ','.join(l[:4] for l in r['EXISTING_LAYERS'])))
