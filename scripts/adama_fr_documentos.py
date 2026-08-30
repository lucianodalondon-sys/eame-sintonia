#!/usr/bin/env python3
"""
TIPAR OS DOCUMENTOS FRANCESES PELO MIOLO, não pelo nome do arquivo.

    python scripts/adama_fr_documentos.py --tipar    # lê os PDFs e grava o tipo
    python scripts/adama_fr_documentos.py --medir    # só mostra a contagem

POR QUE O NOME NÃO SERVE
--------------------------
A rota de documentos da ADAMA France é `/france/fr/media/NNNN/download?attachment`.
O nome do arquivo é literalmente `download` para 122 documentos diferentes. Tipar
por nome dava 144 de 153 em `AUTRE_DOCUMENT` — ou seja, não tipava nada.

    FILENAME ≠ DOCUMENT TYPE

E POR QUE A PALAVRA "ÉTIQUETTE" TAMBÉM NÃO SERVE
--------------------------------------------------
95 dos 122 documentos contêm a palavra `étiquette`. Nenhum deles é um rótulo por
causa disso: a lei francesa obriga TODO material de promoção a trazer

    "AVANT TOUTE UTILISATION, LISEZ L'ÉTIQUETTE ET LES INFORMATIONS
     CONCERNANT LE PRODUIT"

Então a menção obrigatória num folheto de venda faria o folheto virar rótulo.
É o ataque 7 do red team, e ele passa fácil em quem procura palavra solta.

    MENTION_OF_LABEL ≠ IS_A_LABEL

O QUE DE FATO SEPARA UM DO OUTRO, MEDIDO NOS 122
--------------------------------------------------
    frases H (H302, H410...) ........ 73
    número de AMM .................... 82
    "usages autorisés" ............... 83
    "DESCRIPTIF DU PRODUIT" .......... 28
    menção legal obrigatória ......... 83
    título de FDS / REACH / RUBRIQUE .. 0
    "Détenteur de l'autorisation" ..... 0
    "certificat" ...................... 0

Os dois zeros do fim são o achado: **o catálogo público da ADAMA France não
publica rótulo legal nem ficha de segurança**. O que ele publica é ficha técnica
de produto — que carrega o AMM e a tabela de usos, e por isso não é folheto —
e material promocional sem AMM, que é folheto.

O rótulo legal francês existe: mora no E-Phy e no phytodata, não na vitrine.

    CATALOG_DOCUMENT ≠ LEGAL_LABEL

O QUE ESTE ARQUIVO SE RECUSA A FAZER
--------------------------------------
Adivinhar a codificação. Onze PDFs saem embaralhados porque usam fonte com
subconjunto SEM mapa `/ToUnicode`: cada caractere sai deslocado por um valor que
depende da fonte. Um deslocamento de +29 revela "HERBICIDE CODIX Désherber en
souplesse" no começo de um deles — e desanda no meio, porque o documento usa
mais de uma fonte, cada uma com seu deslocamento.

Dava para procurar o deslocamento que mais parece francês. Não vai ser feito:
a margem entre o melhor palpite (0,275 de palavras francesas) e o segundo
(0,249) é fina, e um texto quase-certo decidindo o TIPO de um documento produz
um rótulo que parece medido e não é. Eles saem `UNKNOWN_DOCUMENT_TYPE` com a
causa escrita, e o diagnóstico fica aqui para quem for resolver.

    SCRAMBLED_TEXT ≠ NO_DOCUMENT
    UNKNOWN ≠ OTHER — o primeiro é "não consegui ler"; o segundo é
                      "li, e não é nenhum dos tipos conhecidos"
"""
import json
import os
import re
import sys
import unicodedata

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)

import pdf_text                                                  # noqa: E402

MANIFESTO = os.path.join(ROOT, 'data', 'raw', 'FR', 'adama-website',
                         'MANIFESTO-CATALOGO.json')

# ── tipos, e o que cada um exige ─────────────────────────────────────────────
ETIQUETTE = 'ETIQUETTE'
FICHE_TECHNIQUE = 'FICHE_TECHNIQUE'
FICHE_SECURITE = 'FICHE_DE_DONNEES_DE_SECURITE'
BROCHURE = 'BROCHURE'
NOTICE = 'NOTICE'
CERTIFICATE = 'CERTIFICATE'
OUTRO = 'OTHER'
DESCONHECIDO = 'UNKNOWN_DOCUMENT_TYPE'

TIPOS = (ETIQUETTE, FICHE_TECHNIQUE, FICHE_SECURITE, BROCHURE, NOTICE,
         CERTIFICATE, OUTRO, DESCONHECIDO)

# ── estados da leitura ───────────────────────────────────────────────────────
TEXTO_OK = 'TEXT_OK'
TEXTO_VAZIO = 'TEXT_EMPTY'
TEXTO_EMBARALHADO = 'TEXT_SCRAMBLED'

# ── sinais, cada um com o que ele prova ──────────────────────────────────────
SINAIS = {
    'FDS_TITULO': r'fiche de donn.{0,4}es de s.{0,4}curit',
    'FDS_REACH': r'1907\s*/\s*2006|\bREACH\b',
    'FDS_RUBRICA': r'RUBRIQUE\s*[1-9]|SECTION\s*[1-9](?![0-9])',
    'FRASES_H': r'\bH\d{3}\b',
    'DETENTEUR': (r'd.tenteur\s+de\s+l|titulaire\s+de\s+l.{0,3}autorisation'
                  r'|d.tenteur\s+d.{0,3}homologation'),
    'AMM_NUMERO': r'AMM\s*(?:n|N)?.{0,3}\s*\d{7}|\bn.{0,3}\s*AMM\s*:?\s*\d{7}',
    'USAGES_AUTORISES': r'usages?\s+autoris',
    'DESCRIPTIF': r'descriptif\s+du\s+produit',
    'NOTICE_TITULO': r'\bnotice\b',
    'CERTIFICAT': r'\bcertificat',
    'MENCAO_LEGAL': (r'lisez\s+l.{0,3}.tiquette|avant\s+toute\s+utilisation'
                     r'|utilisez\s+les\s+produits\s+phytopharmaceutiques'),
}

_AMM_NO_TEXTO = re.compile(r'AMM\s*(?:n|N)?[^0-9]{0,4}(\d{7})|(?<![0-9])(\d{7})(?=\s*[.,;)]?\s*$)',
                           re.I | re.M)


def _achatar(paginas):
    return ' '.join(''.join(p) for p in (paginas or []))


def _proporcao_ilegivel(t):
    """Quanto do texto é caractere de controle. Fonte sem mapa enche disso."""
    if not t:
        return 1.0
    ruins = sum(1 for ch in t
                if unicodedata.category(ch) in ('Cc', 'Co', 'Cn') and ch not in '\t\n\r ')
    return ruins / len(t)


def ler(caminho):
    """→ (texto, estado). Nunca conserta o que não conseguiu ler."""
    try:
        bruto = _achatar(pdf_text.text(caminho))
    except Exception as e:                                        # noqa: BLE001
        return '', TEXTO_VAZIO, 'o extrator falhou: %s' % str(e)[:120]
    limpo = bruto.strip()
    if not limpo:
        return '', TEXTO_VAZIO, ('nenhum texto extraível — provavelmente o PDF é '
                                 'imagem, e ler exigiria OCR')
    p = _proporcao_ilegivel(bruto)
    if p > 0.15:
        return bruto, TEXTO_EMBARALHADO, (
            'fonte com subconjunto SEM mapa /ToUnicode: %.0f%% do texto sai como '
            'caractere de controle. Decodificar por deslocamento seria adivinhar'
            % (100 * p))
    return bruto, TEXTO_OK, None


def sinais_presentes(texto):
    return sorted(k for k, p in SINAIS.items() if re.search(p, texto, re.I))


def tipar(texto, estado, motivo_leitura=None):
    """→ o tipo, com a evidência que o sustenta. Sem evidência: UNKNOWN.

    A ordem é do mais exigente para o menos: o que define uma FDS é o título
    dela, não o fato de ela também falar de perigo. E o rótulo legal exige o
    titular da autorização, porque é isso que um ato administrativo declara e um
    folheto não.
    """
    if estado != TEXTO_OK:
        return {'DOC_TYPE': DESCONHECIDO, 'TEXT_STATE': estado,
                'EVIDENCE': [], 'WHY': motivo_leitura or 'texto não legível'}

    s = set(sinais_presentes(texto))

    if {'FDS_TITULO'} & s or ({'FDS_REACH', 'FDS_RUBRICA'} <= s):
        return {'DOC_TYPE': FICHE_SECURITE, 'TEXT_STATE': estado,
                'EVIDENCE': sorted(s),
                'WHY': 'traz o título de ficha de dados de segurança, ou REACH com rubricas'}

    if 'DETENTEUR' in s and 'AMM_NUMERO' in s:
        return {'DOC_TYPE': ETIQUETTE, 'TEXT_STATE': estado, 'EVIDENCE': sorted(s),
                'WHY': ('declara o titular da autorização junto com o número de AMM '
                        '— é o que um ato administrativo diz e um folheto não')}

    if 'CERTIFICAT' in s and 'AMM_NUMERO' in s:
        return {'DOC_TYPE': CERTIFICATE, 'TEXT_STATE': estado, 'EVIDENCE': sorted(s),
                'WHY': 'texto de certificado com número de autorização'}

    if 'AMM_NUMERO' in s and 'USAGES_AUTORISES' in s:
        return {'DOC_TYPE': FICHE_TECHNIQUE, 'TEXT_STATE': estado,
                'EVIDENCE': sorted(s),
                'WHY': ('traz o AMM E a tabela de usos autorizados. Folheto de venda '
                        'não publica tabela de usos; rótulo legal declararia o titular, '
                        'e este não declara')}

    if s & {'MENCAO_LEGAL', 'FRASES_H', 'USAGES_AUTORISES', 'DESCRIPTIF'}:
        return {'DOC_TYPE': BROCHURE, 'TEXT_STATE': estado, 'EVIDENCE': sorted(s),
                'WHY': ('material de produto sem o par AMM + usos autorizados. '
                        'A menção legal obrigatória NÃO o torna rótulo')}

    return {'DOC_TYPE': OUTRO, 'TEXT_STATE': estado, 'EVIDENCE': sorted(s),
            'WHY': 'texto legível, e nenhum sinal de tipo conhecido'}


def amms_no_documento(texto, estado):
    """AMMs que o PRÓPRIO documento declara. Não os da ficha que o citou.

    A ficha do catálogo diz "este documento é meu"; o documento diz "eu falo do
    AMM X". São afirmações diferentes, e um documento pode cobrir vários AMMs.
    """
    if estado != TEXTO_OK:
        return []
    achados = set()
    for m in re.finditer(r'AMM\s*(?:n|N)?[^0-9A-Za-z]{0,4}(\d{7})', texto, re.I):
        achados.add(m.group(1))
    return sorted(achados)


def _dobra(s):
    s = unicodedata.normalize('NFKD', str(s or '').upper())
    return ''.join(c for c in s if not unicodedata.combining(c))


def produtos_mencionados(texto, estado, nomes):
    """Nomes de produto que aparecem no texto. Só os que foram procurados."""
    if estado != TEXTO_OK:
        return []
    t = _dobra(texto)
    fora = []
    for n in nomes:
        chave = _dobra(n)
        if len(chave) < 3:
            continue
        if re.search(r'(?<![A-Z0-9])%s(?![A-Z0-9])' % re.escape(chave), t):
            fora.append(n)
    return sorted(set(fora))


# ══════════════════════════════════════════════════════════════════════════════

def tipar_manifesto():
    with open(MANIFESTO, encoding='utf-8') as fh:
        m = json.load(fh)

    nomes_catalogo = sorted({p.get('PRODUCT_NAME') for p in m['PRODUCTS']
                             if p.get('PRODUCT_NAME')})
    fora = []
    for i, d in enumerate(m['DOCUMENTS'], 1):
        if not d.get('LOCAL_PATH'):
            fora.append(dict(d, DOC_TYPE=DESCONHECIDO,
                             WHY='documento não baixado'))
            continue
        caminho = os.path.join(ROOT, d['LOCAL_PATH'])
        texto, estado, motivo = ler(caminho)
        t = tipar(texto, estado, motivo)
        d = dict(d)
        d.update(t)
        d['TEXT_CHARS'] = len(texto)
        d['AMMS_IN_DOCUMENT_TEXT'] = amms_no_documento(texto, estado)
        d['PRODUCT_NAMES_MENTIONED'] = produtos_mencionados(texto, estado,
                                                            nomes_catalogo)
        fora.append(d)
        if i % 25 == 0 or i == len(m['DOCUMENTS']):
            print('  tipados %d/%d' % (i, len(m['DOCUMENTS'])))

    m['DOCUMENTS'] = fora
    m['DOCUMENT_TYPING'] = resumo(fora)
    with open(MANIFESTO, 'w', encoding='utf-8') as fh:
        json.dump(m, fh, ensure_ascii=False, indent=1)
    return m['DOCUMENT_TYPING']


def resumo(docs):
    tipos, estados = {}, {}
    for d in docs:
        tipos[d.get('DOC_TYPE')] = tipos.get(d.get('DOC_TYPE'), 0) + 1
        estados[d.get('TEXT_STATE')] = estados.get(d.get('TEXT_STATE'), 0) + 1
    desconhecidos = tipos.get(DESCONHECIDO, 0)
    return {
        'DOCUMENTS': len(docs),
        'BY_TYPE': tipos,
        'BY_TEXT_STATE': estados,
        'UNKNOWN_DOCUMENT_TYPE': desconhecidos,
        'TYPED': len(docs) - desconhecidos,
        'STATE': ('COMPLETE' if not desconhecidos
                  else 'PARTIAL_WITH_EXACT_UNKNOWN_COUNT'),
        'DOCUMENTS_COVERING_MORE_THAN_ONE_PAGE': sum(
            1 for d in docs if (d.get('CATALOG_PAGE_COUNT') or 0) > 1),
        'DOCUMENTS_DECLARING_OWN_AMM': sum(
            1 for d in docs if d.get('AMMS_IN_DOCUMENT_TEXT')),
    }


def medir():
    with open(MANIFESTO, encoding='utf-8') as fh:
        m = json.load(fh)
    return m.get('DOCUMENT_TYPING') or resumo(m['DOCUMENTS'])


def main():
    modo = sys.argv[1] if len(sys.argv) > 1 else '--medir'
    r = tipar_manifesto() if modo == '--tipar' else medir()
    for k, v in r.items():
        print('%-38s : %s' % (k, v))
    return 0


if __name__ == '__main__':
    sys.exit(main())
