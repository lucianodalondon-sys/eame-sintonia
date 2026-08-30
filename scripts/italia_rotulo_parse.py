#!/usr/bin/env python3
"""
ITÁLIA — o que a etichetta oficial diz, extraído sem memória agronômica.

A regra da missão é explícita: `Não criar issues a partir de memória agronômica`. Um
parser que procurasse "piralide, diabrotica, oidio" porque *sabe* que são pragas do
milho estaria escrevendo a resposta antes de ler a fonte, e depois a encontraria.

Então o alvo é extraído por FORMA, não por vocabulário:

    Vernáculo (Binômio)   →   `Fusariosi (Fusarium spp.)` · `Oidio (Erysiphe spp.)`

A etichetta italiana nomeia o alvo em italiano e, entre parênteses, o nome científico.
O binômio é o que valida: nenhuma lista minha decide o que é alvo — decide o padrão
`Maiúscula + minúsculas` seguido de `spp.` ou de epíteto específico, que é a assinatura
de uma nomenclatura binomial. Alvo que a fonte não nomear cientificamente não entra,
e essa recusa é o comportamento correto.

A CULTURA é outro problema, e é honesto dizer por quê. A cultura vive numa COLUNA de
tabela, e o texto extraído de PDF perde a coluna. Não há como derivar a cultura por
forma. Então aqui a cultura é medida como **PRESENÇA DE TERMO**, com o trecho literal
preservado como evidência, e o contrato é declarado:

    `CROP_TERM_PRESENT` significa: o termo aparece no rótulo.
    NÃO significa: o produto é autorizado nessa cultura para todos os alvos listados.
    A associação cultura↔alvo exige a coluna, e a coluna NÃO foi reconstruída.

Termo não procurado é `NOT_SEARCHED`, nunca `ABSENT`. A lista de termos é um índice de
busca declarado, não um julgamento agronômico.

DEFEITO DE EXTRAÇÃO MEDIDO E CORRIGIDO
Parte das etichettas usa fonte com subconjunto sem `/ToUnicode` cujo mapa está deslocado
+29 em relação ao ASCII: `c R Q W U R O O R` é `controllo`. O deslocamento é detectado
por evidência (densidade de letras isoladas + o texto decodificado virar palavra
italiana plausível), nunca aplicado às cegas — aplicar sempre estragaria o texto são.
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import pdf_text  # noqa: E402

# Assinatura de nomenclatura binomial. NÃO é lista de pragas: é a FORMA de um nome
# científico. Quem inventar um alvo terá de inventar também um binômio plausível.
# O epíteto NÃO é opcional. Exigir `spp.` ou um segundo termo minúsculo é o que
# separa binômio de topônimo: `(Israele)` e `(Ungheria)` — endereços de fábrica que
# aparecem em toda etichetta — casavam enquanto o epíteto era opcional, e entravam
# como alvo. Precisão acima de cobertura: `COBERTURA ALTA É SUSPEITA, NÃO CONQUISTA`.
ALVO = re.compile(
    r'([A-ZÀ-Ù][A-Za-zà-ùé\'\- ]{2,44}?)\s*\('
    r'([A-Z][a-z]{3,20}\s+(?:spp\.?|sp\.?|[a-z]{3,20}))'
    r'[^)]{0,40}\)'
)

# Ruído estrutural: rótulos trazem seções cujo título casa com a forma mas não é alvo.
NAO_ALVO = re.compile(
    r'^(?:reg|registrazion|composizion|contenut|partita|stabilimento|distribuit|'
    r'etichetta|decreto|allegato|tabella|scheda|dose|dosi|volum|intervall|avvertenz|'
    r'prescrizion|informazion|indicazion|consigli|caratteristic|caratteri|modalit|'
    r'caren|caso|nota|caption|figura|caps|classe|gruppo|codice|art|tel|fax|via|'
    r'sostanz|coformulant|ingredient|preparat|prodott|formulat|confezion|'
    r'contiene|contenut|miscel|associazion|trattasi|stabiliment|distribut|'
    r'fabbricant|titolar|officina|sede|import)',
    re.I)

# Índice de busca de cultura, DECLARADO. Não é a lista das culturas italianas.
# Termo fora daqui é NOT_SEARCHED, e NOT_SEARCHED nunca é ABSENT.
CROP_TERMS = {
    'MAIZE': [r'\bmais\b', r'\bgranoturco\b'],
    'DURUM_WHEAT': [r'grano\s+duro', r'frumento\s+duro'],
    'COMMON_WHEAT': [r'grano\s+tenero', r'frumento\s+tenero'],
    'WHEAT_GENERIC': [r'\bfrumento\b', r'\bgrano\b'],
    'BARLEY': [r'\borzo\b'],
    'RICE': [r'\briso\b'],
    'SOYBEAN': [r'\bsoia\b'],
    'GRAPEVINE': [r'\bvite\b', r'\bvigneto\b'],
    'OLIVE': [r'\bolivo\b', r'\bolive\b'],
    'SUGARBEET': [r'barbabietola'],
    'TOMATO': [r'\bpomodoro\b'],
    'POTATO': [r'\bpatata\b'],
    'SUNFLOWER': [r'\bgirasole\b'],
    'TRITICALE': [r'\btriticale\b'],
    'SORGHUM': [r'\bsorgo\b'],
    'APPLE': [r'\bmelo\b'],
    'ALFALFA': [r'\berba\s+medica\b'],
}

# CONTEXTO DE ROTAÇÃO — a armadilha que quase publicou 23 "produtos de milho" da ADAMA.
# GOLTIX (METAMITRON) é herbicida de beterraba. `mais` aparece no rótulo dele porque a
# etichetta declara o que se pode semear DEPOIS, em caso de falha da cultura:
#   "In caso di fallimento della coltura: (...) patate e mais possono essere seminate
#    in seguito ad aratura profonda."
# Isso é RESTRIÇÃO DE SUCESSÃO, o oposto de autorização de uso. Contar essa menção como
# presença na cultura inverteria o sentido do documento.
CONTEXTO_ROTACAO = re.compile(
    r'(fallimento della coltura|colture? (?:in )?success|avvertenze agronomiche|'
    r'rotazion|semina(?:re|te|ti)? in seguito|intervallo .{0,30}semina|'
    r'possono essere seminat|puo essere seminat|può essere seminat|'
    r'colture da rinnovo|residui nel terreno)', re.I)

JANELA_ROTACAO = 260

# MODO DE AÇÃO — declarado pelo próprio rótulo (HRAC/FRAC/IRAC).
#
# A primeira versão deste extrator reportava 55% de cobertura e estava ERRADA. Ela
# procurava o código DEPOIS do nome do esquema, e a construção italiana é a inversa:
#
#     "Meccanismo d\u2019azione gruppo B (HRAC)"                      <- código ANTES
#     "Meccanismi d\u2019azione: gruppo 2 (B), gruppo 27 (F2), gruppo 4 (O) (HRAC)"
#     "MECCANISMO D\u2019AZIONE (HRAC): GRUPPO 5 (C1) E GRUPPO 27 (F2)"  <- e DEPOIS
#
# Procurando à frente, o extrator capturava a primeira maiúscula que encontrasse —
# que era a inicial do nome do produto. `TAIFUN MK CL` virou HRAC "T" e
# `HERBITOTAL CL` virou HRAC "H"; ambos são glifosato, HRAC G, e o rótulo dizia G.
# Cobertura de 55% com valor errado é pior que cobertura menor e certa:
# `COBERTURA ALTA É SUSPEITA, NÃO CONQUISTA`.
#
# A versão atual ancora no token `gruppo/gruppi` — que é onde o código realmente vive —
# e só atribui ao esquema cujo nome aparece na mesma vizinhança. Rótulo que não declara
# devolve vazio, e vazio é `NÃO DECLARA`, nunca `não tem`.
ESQUEMA = re.compile(r'\b(HRAC|FRAC|IRAC)\b', re.I)
GRUPO = re.compile(r'\bgrupp[oi]\s*:?\s*([0-9]{1,2}[A-Z]?|[A-Z])\b(?:\s*\(([A-Z][0-9]?)\))?', re.I)
JANELA_MOA = 200

DESLOC = 29


def _corrigir_deslocamento(t):
    """Desfaz o mapa de fonte deslocado +29, e só quando a evidência o indica.

    A primeira versão só reconhecia sequências de LETRAS separadas por espaço, e por
    isso não via o caso mais comum: `0 ( & & $ 1 , 6 0 2` — que é `MECCANISMO` com o
    mesmo deslocamento, escrito com dígitos e pontuação porque o subconjunto da fonte
    remapeia todo o intervalo, não só as letras. O efeito prático era caro: o rótulo do
    glifosato declara `gruppo G (HRAC)` dentro de um trecho assim, e saía como
    `NÃO DECLARA`.

    A decodificação só é ACEITA se o resultado virar texto latino plausível. Decodificar
    e conferir é o que separa correção de chute — um deslocamento aplicado às cegas
    estragaria todo o texto são do documento.
    """
    corridas = list(re.finditer(r'(?:[!-~¶]\s){3,}[!-~¶]', t))
    if len(corridas) < 3:
        return t, False

    def rep(m):
        bruto = m.group(0)
        chars = [c for c in bruto if not c.isspace()]
        dec = ''.join("'" if c == '¶' else chr(ord(c) + DESLOC) for c in chars)
        # Aceita só se virar palavra latina: letras, apóstrofo, espaço.
        if re.fullmatch(r"[A-Za-z'\u00c0-\u00ff ]{3,}", dec) and re.search(r'[aeiouAEIOU]', dec):
            return dec
        return bruto

    novo = re.sub(r'(?:[!-~¶]\s){3,}[!-~¶]', rep, t)
    return novo, novo != t


def texto(caminho):
    with open(caminho, 'rb') as fh:
        bruto = pdf_text.extract(fh.read()) if hasattr(pdf_text, 'extract') else None
    if bruto is None:
        import subprocess
        bruto = subprocess.run([sys.executable, os.path.join(HERE, 'pdf_text.py'), caminho],
                               capture_output=True, text=True, timeout=120).stdout
    t = re.sub(r'\s+', ' ', bruto)
    t, corrigido = _corrigir_deslocamento(t)
    return t, corrigido


def alvos(t):
    """Alvos nomeados cientificamente PELA FONTE."""
    out = {}
    for m in ALVO.finditer(t):
        vern = re.sub(r'\s+', ' ', m.group(1)).strip(' ;,.-')
        sci = re.sub(r'\s+', ' ', m.group(2)).strip()
        vern = re.sub(r'^(?:e|ed|o|di|del|della|dei|delle|il|la|le|lo|i|gli|un|una|'
                      r'per|con|da|in|su|al|alla|contro|and)\s+', '', vern, flags=re.I)
        if len(vern) < 3 or NAO_ALVO.match(vern):
            continue
        if not re.search(r'[aeiouàèéìòù]', vern, re.I):
            continue
        chave = (vern.lower(), sci)
        out.setdefault(chave, {'ISSUE_VERNACULAR_IT': vern, 'SCIENTIFIC_NAME': sci,
                               'MENTIONS': 0})
        out[chave]['MENTIONS'] += 1
    return sorted(out.values(), key=lambda d: (-d['MENTIONS'], d['ISSUE_VERNACULAR_IT']))


def culturas(t):
    """Presença de termo de cultura, separando USO de ROTAÇÃO.

    Duas saídas possíveis, e a diferença é de sentido, não de grau:

      `CROP_TERM_PRESENT`          o termo aparece fora de cláusula de sucessão
      `ROTATION_CONTEXT_ONLY`      TODAS as menções estão em cláusula de sucessão —
                                   o rótulo fala da cultura para RESTRINGIR o que se
                                   semeia depois. Não é uso; é quase o contrário.

    Nenhuma das duas é `AUTHORIZED_ON_CROP`. A autorização por cultura mora na coluna
    da tabela de doses, que a extração de PDF não reconstrói.
    """
    out = {}
    for nome, pats in CROP_TERMS.items():
        usos, rot = [], []
        for p in pats:
            for m in re.finditer(p, t, re.I):
                ini = max(0, m.start() - JANELA_ROTACAO)
                antes = t[ini:m.start()]
                ev = {'MATCH': m.group(0),
                      'CONTEXT': t[max(0, m.start() - 90):m.end() + 90].strip()}
                (rot if CONTEXTO_ROTACAO.search(antes) else usos).append(ev)
        if not usos and not rot:
            continue
        out[nome] = {
            'STATE': 'CROP_TERM_PRESENT' if usos else 'ROTATION_CONTEXT_ONLY',
            'MENTIONS_USE_CONTEXT': len(usos),
            'MENTIONS_ROTATION_CONTEXT': len(rot),
            'EVIDENCE': (usos or rot)[:2],
        }
    return out


def modo_de_acao(t):
    """Grupos de modo de ação declarados PELO RÓTULO. Vazio é 'não declara', não 'não tem'."""
    esquemas = [(m.start(), m.group(1).upper()) for m in ESQUEMA.finditer(t)]
    if not esquemas:
        return {}
    out = {}
    for g in GRUPO.finditer(t):
        perto = [(abs(g.start() - pos), nome) for pos, nome in esquemas
                 if abs(g.start() - pos) <= JANELA_MOA]
        if not perto:
            continue
        nome = min(perto)[1]
        codigo = g.group(1).upper()
        if g.group(2):
            codigo += ' (%s)' % g.group(2).upper()
        out.setdefault(nome, set()).add(codigo)
    return {k: sorted(v) for k, v in sorted(out.items())}


def analisar(caminho):
    t, corrigido = texto(caminho)
    mo = modo_de_acao(t)
    return {
        'MODE_OF_ACTION_DECLARED': mo,
        # Onde a fonte deslocada aparece, MoA pode estar SUB-reportado: o código às vezes
        # fica colado num trecho que a decodificação não recupera com segurança. Recuperá-lo
        # à força arriscaria fundir o código na palavra anterior (`gruppo G` -> `gruppod`),
        # e um valor corrompido é pior que um vazio honesto. Fica declarado como limitação.
        'MODE_OF_ACTION_EXTRACTION': ('LIMITED_BY_FONT_ENCODING' if (corrigido and not mo)
                                      else ('DECLARED' if mo else 'NOT_DECLARED')),
        'TEXT_CHARS': len(t),
        'FONT_SHIFT_CORRECTION_APPLIED': corrigido,
        'ISSUES_FROM_SOURCE': alvos(t),
        'CROP_TERMS_PRESENT': culturas(t),
        'EXTRACTION_STATE': 'OK' if len(t) > 400 else 'TEXT_TOO_SHORT',
    }


def main():
    d = os.path.join(ROOT, 'data', 'raw', 'IT', 'etichette')
    arqs = sorted(f for f in os.listdir(d) if f.endswith('.pdf'))
    if '--um' in sys.argv:
        arqs = arqs[:1]
    for f in arqs[:5]:
        r = analisar(os.path.join(d, f))
        print('==', f, r['EXTRACTION_STATE'], 'shift=%s' % r['FONT_SHIFT_CORRECTION_APPLIED'])
        print('   culturas:', sorted(r['CROP_TERMS_PRESENT']))
        for i in r['ISSUES_FROM_SOURCE'][:8]:
            print('   alvo: %-34s %s' % (i['ISSUE_VERNACULAR_IT'][:34], i['SCIENTIFIC_NAME']))


if __name__ == '__main__':
    main()
