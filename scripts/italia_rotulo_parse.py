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

DESLOC = 29


def _corrigir_deslocamento(t):
    """Desfaz o mapa de fonte deslocado +29, e só quando a evidência o indica."""
    isoladas = len(re.findall(r'(?:\b[A-Za-z]\s){4,}', t))
    if isoladas < 3:
        return t, False

    def rep(m):
        bruto = m.group(0)
        letras = re.findall(r'[A-Za-z¶]', bruto)
        dec = ''.join("'" if c == '¶' else chr(ord(c) + DESLOC) for c in letras)
        # Só aceita se o resultado for minúsculas latinas — decodificação que produz
        # lixo é decodificação errada, e nesse caso o bruto é preservado.
        return dec if re.fullmatch(r"[a-z']{3,}", dec) else bruto

    return re.sub(r'(?:[A-Za-z¶]\s){2,}[A-Za-z¶]', rep, t), True


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
    """Presença de termo de cultura, com trecho literal como evidência."""
    out = {}
    for nome, pats in CROP_TERMS.items():
        achados = []
        for p in pats:
            for m in re.finditer(p, t, re.I):
                ini = max(0, m.start() - 60)
                achados.append({'MATCH': m.group(0),
                                'CONTEXT': t[ini:m.end() + 60].strip()})
                break
        if achados:
            out[nome] = {'STATE': 'CROP_TERM_PRESENT', 'EVIDENCE': achados[:2]}
    return out


def analisar(caminho):
    t, corrigido = texto(caminho)
    return {
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
