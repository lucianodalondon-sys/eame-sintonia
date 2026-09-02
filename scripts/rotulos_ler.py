#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LÊ OS PARES CULTURA × ALVO DENTRO DOS RÓTULOS AUTORIZADOS.

    python3 scripts/rotulos_ler.py

Lê SEMPRE do PDF gravado por `rotulos_baixar.py`, nunca da rede.

A LEI QUE MANDA AQUI
---------------------
Herdada de `portal-sintonia/pares-da-bula.py` (Brasil):

    AUDITAR POR PAR, NUNCA POR ALVO.

Um rótulo com 4 culturas e 6 alvos não tem 24 pares. Tem os pares que a TABELA une,
linha a linha. Cruzar tudo com tudo é «pescar alvo de outra cultura» — e produz
autorização que não existe, que é pior que não achar nada.

Por isso o par só nasce DENTRO DE UMA LINHA da tabela. Se a linha não pôde ser
delimitada, o produto sai `TABELA_NAO_LOCALIZADA` e fica em NÃO SEI. Nunca há
recuperação varrendo o documento inteiro atrás de cultura e alvo soltos — seria
exatamente o erro que esta lei existe para impedir.

O QUE É FATO E O QUE É NOSSO
-----------------------------
    ALVO_LITERAL     o que o rótulo escreveu, copiado          → FATO
    CULTURA_LITERAL  o que o rótulo escreveu, copiado          → FATO
    ALVO_CANONICO    o nome que NÓS demos àquilo               → INFERÊNCIA
    CULTURA_CANONICA idem                                      → INFERÊNCIA

O canônico serve para ligar com a régua do corpus público. Quando não sabemos mapear,
sai `NAO_MAPEADO` — e o literal continua lá, inteiro. Perder o literal seria perder o
fato para ficar com o palpite.

O QUE ESTE SCRIPT NÃO PODE SUSTENTAR
-------------------------------------
    ⛔ «a ADAMA não tem produto para X»  — ausência aqui é ausência NA NOSSA LEITURA
    ⛔ eficácia, recomendação, prioridade — o rótulo autoriza, não recomenda
    ⛔ dose comparável entre produtos     — unidades e bases de cálculo diferem
"""
import json
import os
import re
import sys
import unicodedata
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CRUS = os.path.join(ROOT, 'data', 'raw', 'IT-ROTULOS')
SAIDA = os.path.join(ROOT, 'data', 'samples', 'IT-ROTULOS')


def _n(t):
    return ''.join(c for c in unicodedata.normalize('NFD', t or '')
                   if unicodedata.category(c) != 'Mn').lower()


# ── CULTURA, COMO O RÓTULO ESCREVE ──────────────────────────────────────────────
# A ordem importa: o mais específico primeiro, senão «mais dolce» vira «mais».
CULTURAS_ROTULO = [
    ('BARBABIETOLA', r'barbabietola(\s+da\s+zucchero)?|bietola\s+da\s+(zucchero|coste)'),
    ('MAIS_DOLCE',   r'mais\s+dolce|granoturco\s+dolce'),
    ('MAIS',         r'\bmais\b|granoturco|granturco'),
    ('FRUMENTO',     r'frumento(\s+(tenero|duro))?|grano\s+(tenero|duro)'),
    ('ORZO',         r'\borzo\b'),
    ('AVENA',        r'\bavena\b'),
    ('SEGALE',       r'\bsegale\b'),
    ('TRITICALE',    r'triticale'),
    ('RISO',         r'\briso\b|risaia'),
    ('SORGO',        r'\bsorgo\b'),
    ('SOIA',         r'\bsoia\b'),
    ('GIRASOLE',     r'girasole'),
    ('COLZA',        r'\bcolza\b'),
    ('ERBA_MEDICA',  r'erba\s+medica'),
    ('VITE',         r'\bvite\b|vigneto|uva\s+da\s+(tavola|vino)'),
    ('MELO',         r'\bmelo\b|\bmeli\b|pomacee'),
    ('PERO',         r'\bpero\b|\bperi\b'),
    ('PESCO',        r'\bpesco\b|\bpeschi\b|nettarine'),
    ('ALBICOCCO',    r'albicocc'),
    ('SUSINO',       r'susin|\bprugn'),
    ('CILIEGIO',     r'ciliegi'),
    ('ACTINIDIA',    r'actinidia|\bkiwi\b'),
    ('OLIVO',        r'\bolivo\b|\bolivi\b|oliveto'),
    ('AGRUMI',       r'agrumi|arancio|limone|mandarino|clementin'),
    ('POMODORO',     r'pomodoro'),
    ('PATATA',       r'\bpatata\b|\bpatate\b'),
    ('FRAGOLA',      r'fragola|fragole'),
    ('CUCURBITACEE', r'cucurbitac|zucchin|melone|cocomer|cetriolo'),
    ('BRASSICACEE',  r'brassicac|\bcavol'),
    ('LATTUGA',      r'lattuga|insalat|radicchio'),
    ('CIPOLLA',      r'cipolla|aglio|porro|scalogno'),
    ('CAROTA',       r'\bcarota\b|\bcarote\b'),
    ('LEGUMINOSE',   r'\bpisello|\bfagiol|\bcece\b|\bceci\b|\bfava\b|\blentic'),
    ('TABACCO',      r'tabacco'),
    ('OLEAGINOSE',   r'oleaginose'),
    ('ORTAGGI',      r'\bortagg|orticol'),
    ('FLOREALI',     r'floreal|ornamental'),
    ('TAPPETI_ERB',  r'tappeti\s+erbosi|\btappeto\s+erboso'),
]
CULTURAS_RX = [(k, re.compile(r, re.I)) for k, r in CULTURAS_ROTULO]

# Uma linha «começa» uma cultura quando o texto da cultura está NO INÍCIO dela.
INICIO_CULTURA = [(k, re.compile(r'^\s*(' + r + r')', re.I)) for k, r in CULTURAS_ROTULO]

# ── CABEÇALHO DA TABELA DE USO ──────────────────────────────────────────────────
# Só entra se as DUAS colunas aparecem perto uma da outra. «COLTURE TRATTATE»
# sozinho costuma ser intervalo de sicurezza, não tabela de uso.
CABECALHO = re.compile(
    r'coltur[ae][\s\S]{0,60}?(parassit|avversit|infestant|malerb|patogen|insett)'
    r'|(parassit|avversit|infestant|malerb)[\s\S]{0,60}?coltur[ae]', re.I)

# Onde a tabela termina: começou outra seção do rótulo.
FIM_TABELA = re.compile(
    r'^\s*(AVVERTENZ|COMPATIBILIT|ATTENZIONE|FITOTOSSICIT|INFORMAZIONI\s+PER\s+IL\s+MEDICO|'
    r'PRESCRIZIONI\s+SUPPLEMENTARI|SMALTIMENTO|INDICAZIONI\s+DI\s+PERICOLO|'
    r'CONSIGLI\s+DI\s+PRUDENZA|ETICHETTA\s+AUTORIZZATA|SOSTANZE\s+PERICOLOSE|'
    r'NON\s+APPLICARE|DA\s+NON\s+VENDERSI|IL\s+CONTENITORE|PER\s+EVITARE\s+RISCHI|PERICOLO|AVVERTENZA|NORME\s+PRECAUZIONAL|MISURE\s+DI|DISPOSITIVI\s+DI|MANIPOLAZIONE|IMMAGAZZINAMENTO|PRIMO\s+SOCCORSO|H\d{3}|P\d{3}|FRASI\s+DI\s+RISCHIO|CONSIGLI\s+P|CLASSIFICAZIONE)', re.I | re.M)

# ── ALVO ────────────────────────────────────────────────────────────────────────
# Binômio latino: o rótulo é escrito em nome científico. Este é o achado literal.
BINOMIO = re.compile(
    r'\b([A-Z][a-z]{3,})\s+(sp{1,2}\.|spp|[a-z]{3,})\b')

ALVOS_CANON = [
    ('PERONOSPORA',    r'peronospora|plasmopara|bremia|phytophthora\s+infestans'),
    ('OIDIO',          r'oidio|erysiphe|uncinula|podosphaera|leveillula|sphaerotheca'),
    ('BOTRITE',        r'botrite|botrytis'),
    ('SEPTORIOSI',     r'septorio|zymoseptoria|septoria'),
    ('FUSARIOSI',      r'fusario|fusarium|gibberella'),
    ('TICCHIOLATURA',  r'ticchiolatura|venturia'),
    ('RUGGINE',        r'ruggine|puccinia|uromyces'),
    ('CERCOSPORA',     r'cercospor'),
    ('RINCOSPORIOSI',  r'rhyncosporium|rhynchosporium|rincosporios'),
    ('RAMULARIA',      r'ramulari'),
    ('ANTRACNOSE',     r'antracnos|colletotrichum|gloeosporium'),
    ('MAL_DEL_PIEDE',  r'gaeumannomyces|mal\s+del\s+piede|oculimacula'),
    ('CARIE',          r'\bcarie\b|tilletia|ustilago|carbone'),
    ('BATTERIOSI',     r'batterios|pseudomonas|xanthomonas|erwinia'),
    ('BRUSONE',        r'brusone|pyricularia|magnaporthe'),
    ('ELMINTOSPORIOSI', r'elmintosporio|helminthosporium|drechslera|pyrenophora'),
    ('ALTERNARIA',     r'alternari'),
    ('SCLEROTINIA',    r'sclerotini'),
    ('MAL_BIANCO',     r'mal\s+bianco'),
    ('MONILIA',        r'monili'),
    ('BOLLA',          r'\bbolla\b|taphrina'),
    ('SCAFOIDEO',      r'scaphoideus|scafoideo'),
    ('CICALINE',       r'cicalin|empoasca|zygina'),
    ('PIRALIDE',       r'piralide|ostrinia'),
    ('DIABROTICA',     r'diabrotica'),
    ('AFIDI',          r'\bafid|aphis|myzus|rhopalosiphum|sitobion|metopolophium|'
                       r'brachycaudus|dysaphis|eriosoma|toxoptera|nasonovia|'
                       r'macrosiphum|aulacorthum|hyalopterus|schizaphis|'
                       r'phorodon|cavariella|hyadaphis'),
    ('ELATERIDI',      r'elaterid|agriotes|ferretti'),
    ('ALTICHE',        r'chaetocnema|psylliodes|phyllotreta|altic'),
    ('ATOMARIA',       r'atomaria'),
    ('MAGGIOLINO',     r'melolontha|maggiolino'),
    ('MILLEPIEDI',     r'blaniulus|scutigerella|millepiedi'),
    ('DOROIFORA',      r'leptinotarsa|dorifora'),
    ('PUNTERUOLO',     r'ceutorhynchus|curculio|otiorhynchus|punteruolo'),
    ('CECIDOMIA',      r'cecidomi|contarinia|sitodiplosis'),
    ('LEMA',           r'\blema\b|oulema'),
    ('NOTTUE',         r'nottu|agrotis|spodoptera|helicoverpa|autographa|mamestra'),
    ('CIMICE',         r'cimice|halyomorpha|nezara'),
    ('CARPOCAPSA',     r'carpocapsa|cydia'),
    ('TIGNOLE',        r'tignol|lobesia|eupoecilia|prays'),
    ('MOSCA_OLIVO',    r'bactrocera\s+oleae|mosca\s+dell.oliv'),
    ('MOSCA_FRUTTA',   r'ceratitis|mosca\s+della\s+frutta'),
    ('RAGNETTO',       r'ragnetto|tetranychus|panonychus'),
    ('ACARI',          r'\bacar|eriophy|aculus'),
    ('TRIPIDI',        r'tripid|thrips|frankliniella'),
    ('ALEURODIDI',     r'aleurodid|bemisia|trialeurodes|mosca\s+bianca'),
    ('COCCINIGLIE',    r'cocciniglia|cocciniglie|planococcus|saissetia|quadraspidiotus'),
    ('MINATRICI',      r'minatric|liriomyza|leucoptera'),
    ('LIMACCE',        r'limacc|lumac|helix|deroceras'),
    ('NEMATODI',       r'nematod|meloidogyne|globodera|heterodera|pratylenchus'),
    ('DICOTILEDONI',   r'dicotiledoni|infestanti\s+a\s+foglia\s+larga'),
    ('GRAMINACEE',     r'graminacee|infestanti\s+graminacee'),
    ('INFESTANTI',     r'infestant|malerb'),
]
ALVOS_RX = [(k, re.compile(r, re.I)) for k, r in ALVOS_CANON]

# Palavras que parecem alvo mas não são — barram binômio falso do texto legal.
NAO_E_ALVO = re.compile(
    r'^(dose|dosi|coltura|colture|parassiti|avversita|dopo|prima|durante|contro|'
    r'litri|kg|grammi|ettaro|acqua|trattament|applicazion|intervallo|giorni|'
    r'nota|attenzione|vedi|tabella|numero|massimo|impiego|periodo|fase|'
    # ── o cabeçalho jurídico do rótulo produzia 20 «espécies» inexistentes ──
    r'etichetta|decreto|dirigenzial|autorizzat|ministero|registrazione|'
    r'stabilimento|officina|contenuto|composizione|formulazione|distribuit|'
    r'titolare|fabbricante|partita|scadenza|classificazione|indicazioni|'
    r'consigli|prescrizioni|smaltiment|conservare|tenere|utilizzare|leggere|'
    r'informazioni|sostanz|preparat|miscela|volume|epoca|modalita|avvertenz|'
    r'sicurezza|protezione|ambiente|operator|riferimento|seguito|quando|'
    # ── unidades e números que o extrator gruda em palavra ──
    r'grammo|centimetr|metri|ore|anno|mese|settiman|'
    # ⚠️ o vocabulário de PERIGO da rotulagem CLP
    # «Indossare guanti», «Molto tossico», «Provoca grave lesione oculare» têm a
    # forma de um binômio (Maiúscula + minúscula) e nenhuma delas é organismo.
    # Entravam porque a janela do espectro atravessava para a seção de risco.
    r'indossar|proteggere|proteggersi|molto|provoca|sciacquar|mediamente|'
    r'devono|evitare|lavare|togliersi|chiamare|contattare|nocivo|pericolos|'
    r'irritant|corrosiv|infiammabil|tossico|altamente|estremamente|sospetta|'
    r'nuoce|reazione|allergic|letale|dannos|smaltire|raccogliere|eliminare|'
    r'richiedere|consultare|portare|intervenire|sensibili|resistenti|'
    r'scarsamente|poco|assai|inoltre|pertanto|qualora|laddove|essere|'
    r'venire|avere|questo|questa|questi|queste|rispettare|ripetere|'
    r'effettuare|borsa|erba|foglia|foglie)', re.I)

# ⚠️ A ARMADILHA DO HERBICIDA
# Em rótulo de herbicida a coluna de «parassiti» é uma LISTA DE DANINHAS — e várias
# daninhas TÊM NOME DE CULTURA. `Avena spp.` é aveia-brava; `Sorghum halepense` é
# sorgo-de-alepo. O parser leu «Avena spp. (avena), Bromus sterilis (forasacco rosso),
# Echinochloa crus-galli (giavone)» e promoveu AVENA a cultura da linha. Falso.
#
#     NOME DE PLANTA NO INÍCIO DA LINHA NÃO É, POR SI, A CULTURA DA LINHA.
#
# O sinal que separa: a cultura é nomeada SOZINHA («Avena», «Frumento»); a espécie
# daninha vem com epíteto ou `spp.` («Avena spp.», «Avena fatua»). Duas palavras
# latinas seguidas é enumeração de espécie, não coluna de cultura.
EH_ESPECIE_NAO_CULTURA = re.compile(
    r'^\s*[A-Za-z]+\s+(sp{1,2}\.|spp|[a-z]{4,}\s*\()', re.I)



# ══════════════════════════════════════════════════════════════════════════════
# A SEGUNDA PORTA: O RÓTULO DE HERBICIDA
# ══════════════════════════════════════════════════════════════════════════════
# Herbicida é 56% do portfólio italiano da ADAMA e QUASE NENHUM tem tabela
# `COLTURA | PARASSITI | DOSE`. Ele declara duas listas separadas, em prosa:
#
#     «agisce ... sulle seguenti infestanti: Amaranthus retroflexus, ...»   ← espectro
#     «Viene impiegato per il diserbo di: BARBABIETOLA DA ZUCCHERO ...»     ← culturas
#
# ⚠️ LEI NOVA, E ELA É A DIFERENÇA ENTRE LER E INVENTAR:
#
#     ESPECTRO DE PRODUTO ≠ ESPECTRO NA CULTURA
#
# Um herbicida que lista 18 daninhas e 3 culturas NÃO controla as 18 nas 3. A
# seletividade e a dose mudam por cultura, e o próprio rótulo costuma dizer isso
# na seção de cada cultura. Cruzar as duas listas produziria 54 «autorizações»
# das quais o rótulo afirma nenhuma.
#
# Por isso o par que nasce aqui sai com `LIGACAO_NIVEL = DECLARACAO_DE_PRODUTO`,
# e nunca se confunde com o `LINHA_DA_TABELA`, que é o par que o documento une.
# É a mesma família de `CROP_TERM_PRESENT ≠ AUTHORIZED_ON_CROP`.

ABRE_ESPECTRO = re.compile(
    r'(sulle\s+seguenti\s+infestanti|infestanti\s+sensibili|spettro\s+d.azione|'
    r'controlla\s+le\s+seguenti|efficace\s+(contro|sulle)|attivo\s+(contro|sulle)|'
    r'infestanti\s+control|erbe\s+infestanti\s+seguenti)', re.I)

ABRE_CULTURAS = re.compile(
    r'(per\s+il\s+diserbo\s+di|viene\s+impiegato\s+(su|per|nel|nella)|'
    r'(nel|del)\s+diserbo\s+(di|delle|dei|della)|'
    r'seguenti\s+colture|colture\s+autorizzate|per\s+la\s+difesa\s+di|'
    r'impieghi\s+autorizzati|colture\s+di\s+impiego|si\s+impiega\s+(su|nel|nella)|'
    r'autorizzato\s+(su|nelle|nei)|indicato\s+per\s+il\s+diserbo)', re.I)

# O subtítulo do rótulo declara a cultura antes de qualquer seção:
#   «DISERBANTE SELETTIVO PER LA BARBABIETOLA DA ZUCCHERO»
SUBTITULO_CULTURA = re.compile(
    r'(diserbante|erbicida|fungicida|insetticida|acaricida)[^.\n]{0,120}?'
    r'\b(per|nel|nella|su)\b([^.\n]{0,120})', re.I)


def _blocos_ate(texto, ini, limite=2600):
    """Da abertura até o próximo cabeçalho de seção, ou `limite` chars."""
    trecho = texto[ini:ini + limite]
    m = FIM_TABELA.search(trecho)
    return trecho[:m.start()] if m else trecho


def ler_herbicida(texto):
    """→ (culturas, daninhas, evidencia) do rótulo em prosa. Vazio = não sei."""
    daninhas, evid = [], {}
    m = ABRE_ESPECTRO.search(texto)
    if m:
        bloco = _blocos_ate(texto, m.end(), 1800)
        evid['CITACAO_DO_ESPECTRO'] = re.sub(r'\s+', ' ', bloco).strip()[:700]
        vistos = set()
        for b in BINOMIO.finditer(bloco):
            lit = re.sub(r'\s+', ' ', b.group(0)).strip()
            if NAO_E_ALVO.match(lit) or len(lit) < 7 or lit.lower() in vistos:
                continue
            vistos.add(lit.lower())
            daninhas.append(lit)

    culturas = []
    # ⚠️ A JANELA GREEDY REINTRODUZIU A ARMADILHA DA AVENA
    # Ler 900 caracteres depois de «per il diserbo di:» atravessa a seção da
    # cultura e entra no texto seguinte — que menciona OUTRAS culturas e outras
    # daninhas. No CONTATTO 320 a cultura é BARBABIETOLA; a janela pescou «avena»
    # de um trecho adiante e criou AVENA x Polygonum persicaria, que o rótulo não
    # afirma em lugar nenhum.
    #
    #     A CULTURA DO HERBICIDA ESTÁ DECLARADA EM CAIXA ALTA, LOGO APÓS O ABRIDOR:
    #         «per il diserbo di: BARBABIETOLA DA ZUCCHERO E DA FORAGGIO - BIETOLA
    #          ROSSA:»
    #
    # Ler só o trecho em caixa alta troca uma janela de tamanho arbitrário por um
    # sinal que o próprio documento emite. E percorremos TODAS as aberturas, porque
    # a primeira pode ter casado dentro do texto de segurança — foi o que aconteceu
    # no 016823, onde o abridor caiu no meio de «utilizzare guanti, indumenti».
    for m2 in ABRE_CULTURAS.finditer(texto):
        janela = texto[m2.end():m2.end() + 320]
        caixa = ' '.join(re.findall(r"[A-ZÀ-Ý][A-ZÀ-Ý'\- ]{3,}", janela))
        alvo_da_busca = caixa if len(caixa) >= 5 else janela[:160]
        achadas = []
        for k, rx in CULTURAS_RX:
            m = rx.search(_n(alvo_da_busca))
            if not m:
                continue
            # o mesmo guarda da tabela: «Avena spp.» é espécie, não coluna
            depois = alvo_da_busca[m.end():m.end() + 14]
            if re.match(r"\s*(sp{1,2}\.|spp|[a-z]{4,}\s*\()", depois, re.I):
                continue
            achadas.append(k)
        if achadas:
            culturas = achadas
            evid['CITACAO_DAS_CULTURAS'] = re.sub(r'\s+', ' ', alvo_da_busca).strip()[:300]
            evid['COMO_A_CULTURA_FOI_LIDA'] = ('declaracao em caixa alta apos o abridor'
                                               if len(caixa) >= 5 else
                                               'primeiros 160 chars apos o abridor')
            break
    if not culturas:
        cabeca = re.sub(r'\s+', ' ', texto[:1800])
        m3 = SUBTITULO_CULTURA.search(cabeca)
        if m3:
            evid['CITACAO_DO_SUBTITULO'] = m3.group(0).strip()[:220]
            evid['COMO_A_CULTURA_FOI_LIDA'] = 'subtitulo do rotulo, texto achatado'
            for k, rx in CULTURAS_RX:
                m = rx.search(_n(m3.group(3) or ''))
                if not m or k in culturas:
                    continue
                depois = (m3.group(3) or '')[m.end():m.end() + 14]
                if re.match(r"\s*(sp{1,2}\.|spp|[a-z]{4,}\s*\()", depois, re.I):
                    continue
                culturas.append(k)
    return culturas, daninhas, evid


# ── DANINHAS ────────────────────────────────────────────────────────────────────
# Herbicida é 56% do portfólio italiano. Sem esta tabela, 1.263 dos 1.893 pares
# saíam `NAO_MAPEADO` — e eram todos daninhas REAIS: Amaranthus, Echinochloa,
# Solanum nigrum, Papaver rhoeas. O literal já estava certo; faltava o nome nosso.
#
# A divisão em folha larga / gramínea é a que o herbicida usa para existir: um
# produto graminicida e um dicotiledonicida não competem pelo mesmo problema.
DANINHAS_CANON = [
    ('AMARANTO',      r'amaranthus|amaranto', 'FOLHA_LARGA'),
    ('CHENOPODIUM',   r'chenopodium|chenopidium|farinaccio|farinello', 'FOLHA_LARGA'),
    ('SOLANUM_NIGRUM', r'solanum\s+nigrum|erba\s+morella', 'FOLHA_LARGA'),
    ('POLYGONUM',     r'polygonum|persicaria|fallopia|correggiola|poligono', 'FOLHA_LARGA'),
    ('MATRICARIA',    r'matricaria|camomilla', 'FOLHA_LARGA'),
    ('PAPAVER',       r'papaver|papavero', 'FOLHA_LARGA'),
    ('STELLARIA',     r'stellaria|centocchio', 'FOLHA_LARGA'),
    ('VERONICA',      r'veronica', 'FOLHA_LARGA'),
    ('FUMARIA',       r'fumaria', 'FOLHA_LARGA'),
    ('SINAPIS',       r'sinapis|senape|rapistrum|rapistro|diplotaxis|raphanus', 'FOLHA_LARGA'),
    ('CAPSELLA',      r'capsella|borsa\s+del\s+pastore', 'FOLHA_LARGA'),
    ('GALIUM',        r'galium|attaccamani', 'FOLHA_LARGA'),
    ('CIRSIUM',       r'cirsium|sonchus|cardo|crespigno', 'FOLHA_LARGA'),
    ('CONVOLVULUS',   r'convolvulus|vilucchio', 'FOLHA_LARGA'),
    ('ABUTILON',      r'abutilon|cencio\s+molle', 'FOLHA_LARGA'),
    ('XANTHIUM',      r'xanthium|nappola', 'FOLHA_LARGA'),
    ('AMBROSIA',      r'ambrosia', 'FOLHA_LARGA'),
    ('DATURA',        r'datura|stramonio', 'FOLHA_LARGA'),
    ('MERCURIALIS',   r'mercurialis|mercorella', 'FOLHA_LARGA'),
    ('LAMIUM',        r'lamium|falsa\s+ortica', 'FOLHA_LARGA'),
    ('URTICA',        r'urtica|ortica', 'FOLHA_LARGA'),
    ('ANAGALLIS',     r'anagallis|mordigallina', 'FOLHA_LARGA'),
    ('SENECIO',       r'senecio|calderina', 'FOLHA_LARGA'),
    ('PORTULACA',     r'portulaca|porcellana', 'FOLHA_LARGA'),
    ('DAUCUS',        r'daucus|carota\s+selvatica', 'FOLHA_LARGA'),
    ('VIOLA',         r'\bviola\b|viola\s+spp|violetta', 'FOLHA_LARGA'),
    ('CALEPINA',      r'calepina', 'FOLHA_LARGA'),
    ('GERANIUM',      r'geranium|geranio', 'FOLHA_LARGA'),
    ('LEGUMINOSA_INF', r'vicia|trifolium|medicago\s+spp|melilotus', 'FOLHA_LARGA'),
    ('EUPHORBIA',     r'euphorbia|euforbia', 'FOLHA_LARGA'),
    ('BIFORA',        r'bifora', 'FOLHA_LARGA'),
    ('SILENE',        r'silene', 'FOLHA_LARGA'),
    ('MYOSOTIS',      r'myosotis|nontiscordardime', 'FOLHA_LARGA'),
    ('CARDARIA',      r'cardaria|lepidium', 'FOLHA_LARGA'),
    ('ECHINOCHLOA',   r'echinochloa|giavone|giavona', 'GRAMINEA'),
    ('SETARIA',       r'setaria|pabbio', 'GRAMINEA'),
    ('DIGITARIA',     r'digitaria|sanguinella', 'GRAMINEA'),
    ('SORGHUM_HAL',   r'sorghum\s+halepense|sorghetta', 'GRAMINEA'),
    ('LOLIUM',        r'lolium|loglio|loietto', 'GRAMINEA'),
    ('AVENA_FATUA',   r'avena\s+(fatua|sterilis|spp|ludoviciana)|avena\s+selvatica', 'GRAMINEA'),
    ('ALOPECURUS',    r'alopecurus|coda\s+di\s+topo', 'GRAMINEA'),
    ('PHALARIS',      r'phalaris|scagliola|falaride', 'GRAMINEA'),
    ('POA',           r'\bpoa\b|fienarola', 'GRAMINEA'),
    ('BROMUS',        r'bromus|forasacco', 'GRAMINEA'),
    ('AGROPYRON',     r'agropyron|elytrigia|gramigna', 'GRAMINEA'),
    ('CYPERUS',       r'cyperus|zigolo', 'CIPERACEA'),
    ('ORYZA_CRODO',   r'riso\s+crodo|oryza\s+sativa\s+var', 'GRAMINEA'),
    ('CYNODON',       r'cynodon', 'GRAMINEA'),
    ('APERA',         r'\bapera\b', 'GRAMINEA'),
]
DANINHAS_RX = [(k, re.compile(r, re.I), g) for k, r, g in DANINHAS_CANON]


def canonizar_daninha(txt):
    """→ (chave, grupo) ou ('NAO_MAPEADO', 'NAO_SEI'). Nunca inventa grupo."""
    t = _n(txt)
    for k, rx, g in DANINHAS_RX:
        if rx.search(t):
            return k, g
    return 'NAO_MAPEADO', 'NAO_SEI'


# Alvos que o rótulo escreve em nome comum de TRÊS palavras. O regex de binômio
# pega duas e devolvia «Mosca della» — que não nomeia organismo nenhum.
NOMES_COMPOSTOS = [
    re.compile(r"mosca\s+dell[a']\s*\w+", re.I),
    re.compile(r'ragnetto\s+rosso', re.I),
    re.compile(r'mosca\s+bianca', re.I),
    re.compile(r'mal\s+bianco', re.I),
    re.compile(r'muffa\s+grigia', re.I),
    re.compile(r'marciume\s+\w+', re.I),
    re.compile(r'minator[ie]\s+fogliar\w*', re.I),
    re.compile(r'tignol[ae]\s+\w+', re.I),
    re.compile(r'cimice\s+asiatica', re.I),
]


def canonizar(txt, tabela):
    t = _n(txt)
    for k, rx in tabela:
        if rx.search(t):
            return k
    return 'NAO_MAPEADO'


def regiao_da_tabela(texto):
    """→ lista de blocos de texto que são tabela de uso. Vazia = não localizada."""
    blocos = []
    for m in CABECALHO.finditer(texto):
        ini = m.start()
        linhas = texto[ini:].split('\n')
        corpo = []
        for ln in linhas[1:]:
            if FIM_TABELA.match(ln):
                break
            corpo.append(ln)
            if len(corpo) > 400:
                break
        if corpo:
            blocos.append('\n'.join(corpo))
    return blocos


def linhas_da_tabela(bloco):
    """Quebra o bloco em LINHAS DE CULTURA. É aqui que a lei do par se cumpre.

    Uma linha nova começa quando o texto da cultura aparece NO INÍCIO da linha.
    Tudo até a próxima abertura pertence àquela cultura — e só a ela.
    """
    linhas, atual = [], None
    for ln in bloco.split('\n'):
        achou = None
        if not EH_ESPECIE_NAO_CULTURA.match(ln):
            for k, rx in INICIO_CULTURA:
                if rx.search(ln):
                    achou = k
                    break
        if achou:
            if atual:
                linhas.append(atual)
            atual = {'CULTURA_CANONICA': achou, 'TEXTO': [ln]}
        elif atual is not None:
            atual['TEXTO'].append(ln)
    if atual:
        linhas.append(atual)
    return linhas


def _e_nome_de_cultura_solto(lit):
    """«Cavolo cappuccio» e «Mais dolce» viraram alvo. São culturas.

    A ressalva que impede o remédio de virar doença: em rótulo de herbicida uma
    cultura PODE ser daninha (o milho voluntário no trigo seguinte). Por isso só
    barra quando o literal é nome italiano puro, SEM epíteto latino.
    """
    if re.search(r'(sp{1,2}\.|spp)', lit, re.I):
        return False
    for _, rx in CULTURAS_RX:
        if rx.fullmatch(lit.strip()) or rx.match(_n(lit)) and len(lit.split()) <= 2:
            palavras = lit.strip().split()
            if len(palavras) <= 2 and palavras[-1].islower():
                return True
    return False


def alvos_da_linha(texto):
    """→ [(literal, canonico)]. O literal é o fato; o canônico é nossa leitura."""
    achados, vistos = [], set()
    for rx in NOMES_COMPOSTOS:
        for m in rx.finditer(texto):
            lit = re.sub(r'\s+', ' ', m.group(0)).strip()
            if lit.lower() not in vistos:
                vistos.add(lit.lower())
                achados.append((lit, canonizar(lit, ALVOS_RX)))
    for m in BINOMIO.finditer(texto):
        lit = m.group(0).strip()
        if NAO_E_ALVO.match(lit) or len(lit) < 7:
            continue
        if _e_nome_de_cultura_solto(lit):
            continue
        # «Mosca della frutta» já entrou pelos nomes compostos; o binômio de duas
        # palavras produziria «Mosca della», que não nomeia organismo nenhum.
        if any(v.startswith(lit.lower()) and v != lit.lower() for v in vistos):
            continue
        if lit.lower() in vistos:
            continue
        vistos.add(lit.lower())
        achados.append((lit, canonizar(lit, ALVOS_RX)))
    # nomes comuns italianos, que não são binômio
    for k, rx in ALVOS_RX:
        m = rx.search(_n(texto))
        if m and not any(c == k for _, c in achados):
            achados.append((texto[m.start():m.end()].strip(), k))
    return achados


def main():
    import pypdf
    man = json.load(open(os.path.join(CRUS, '_MANIFESTO.json'), encoding='utf-8'))
    os.makedirs(SAIDA, exist_ok=True)

    pares, por_produto, estados = [], [], Counter()
    for it in man['ITENS']:
        if it['ESTADO'] != 'OK':
            estados[it['ESTADO']] += 1
            por_produto.append({'REGISTRATION_ID': it['REGISTRATION_ID'],
                                'PRODUCT': it.get('PRODUCT'),
                                'ESTADO_DA_LEITURA': 'PDF_' + it['ESTADO'],
                                'PARES': 0})
            continue
        caminho = os.path.join(CRUS, it['ARQUIVO'])
        try:
            texto = '\n'.join((p.extract_text() or '')
                              for p in pypdf.PdfReader(caminho).pages)
        except Exception as e:
            estados['ERRO_LEITURA'] += 1
            por_produto.append({'REGISTRATION_ID': it['REGISTRATION_ID'],
                                'PRODUCT': it.get('PRODUCT'),
                                'ESTADO_DA_LEITURA': 'ERRO_%s' % type(e).__name__,
                                'PARES': 0})
            continue
        texto = texto.replace('\x00', ' ')

        blocos = regiao_da_tabela(texto)
        if not blocos:
            # A tabela nao existe neste rotulo. Antes de desistir, a porta em prosa.
            culturas, daninhas, evid = ler_herbicida(texto)
            if culturas and daninhas:
                n0 = len(pares)
                for c in culturas:
                    for lit in daninhas:
                        pares.append({
                            'REGISTRATION_ID': it['REGISTRATION_ID'],
                            'PRODUCT': it.get('PRODUCT'),
                            'PRODUCT_ID': it.get('PRODUCT_ID'),
                            'CULTURA_CANONICA': c,
                            'ALVO_LITERAL': lit,
                            'ALVO_CANONICO': canonizar_daninha(lit)[0],
                            'ALVO_GRUPO': canonizar_daninha(lit)[1],
                            'ALVO_E': 'PLANTA_INFESTANTE',
                            'CITACAO_DA_LINHA': evid.get('CITACAO_DO_ESPECTRO', ''),
                            'CITACAO_DAS_CULTURAS': evid.get('CITACAO_DAS_CULTURAS')
                                                    or evid.get('CITACAO_DO_SUBTITULO'),
                            'LIGACAO_NIVEL': 'DECLARACAO_DE_PRODUTO',
                            'LIGACAO_O_QUE_SIGNIFICA':
                                'o rotulo declara SEPARADAMENTE que o produto atua sobre '
                                'esta daninha e que e usado nesta cultura. NAO afirma que '
                                'controla esta daninha NESTA cultura. Espectro de produto '
                                'nao e espectro na cultura.',
                            'LIGACAO_MAIS_FRACA_QUE': 'LINHA_DA_TABELA',
                            'ORIGEM': 'prosa do rotulo de herbicida',
                            'EVIDENCE_CLASS': 'DOCUMENTO_OFICIAL',
                            'O_QUE_NAO_PROVA': 'nao prova eficacia, seletividade nem dose '
                                               'nesta cultura. O rotulo autoriza.',
                        })
                estados['LIDO_COMO_HERBICIDA'] += 1
                por_produto.append({'REGISTRATION_ID': it['REGISTRATION_ID'],
                                    'PRODUCT': it.get('PRODUCT'),
                                    'ESTADO_DA_LEITURA': 'LIDO_COMO_HERBICIDA',
                                    'CULTURAS': culturas,
                                    'N_DANINHAS_NO_ESPECTRO': len(daninhas),
                                    'PARES': len(pares) - n0})
                continue
            estados['TABELA_NAO_LOCALIZADA'] += 1
            por_produto.append({'REGISTRATION_ID': it['REGISTRATION_ID'],
                                'PRODUCT': it.get('PRODUCT'),
                                'ESTADO_DA_LEITURA': 'TABELA_NAO_LOCALIZADA',
                                'CHARS_DO_PDF': len(texto),
                                'ACHOU_CULTURA': bool(culturas),
                                'ACHOU_ESPECTRO': bool(daninhas),
                                'O_QUE_ISTO_SIGNIFICA':
                                    'nao achamos a tabela nem as duas listas NESTA '
                                    'extracao. Nao significa que o rotulo nao autoriza '
                                    'usos.',
                                'PARES': 0})
            continue

        n0 = len(pares)
        for bloco in blocos:
            for ln in linhas_da_tabela(bloco):
                txt = re.sub(r'\s+', ' ', ' '.join(ln['TEXTO'])).strip()
                if len(txt) > 600:
                    txt = txt[:600]
                for lit, canon in alvos_da_linha(txt):
                    grupo = None
                    if canon == 'NAO_MAPEADO':
                        canon_d, grupo = canonizar_daninha(lit)
                        if canon_d != 'NAO_MAPEADO':
                            canon = canon_d
                    pares.append({
                        'REGISTRATION_ID': it['REGISTRATION_ID'],
                        'PRODUCT': it.get('PRODUCT'),
                        'PRODUCT_ID': it.get('PRODUCT_ID'),
                        'CULTURA_CANONICA': ln['CULTURA_CANONICA'],
                        'ALVO_LITERAL': lit,
                        'ALVO_CANONICO': canon,
                        'ALVO_GRUPO': grupo,
                        'ALVO_E': ('PLANTA_INFESTANTE' if grupo
                                   else 'PRAGA_OU_DOENCA'),
                        'CITACAO_DA_LINHA': txt,
                        'LIGACAO_NIVEL': 'LINHA_DA_TABELA',
                        'LIGACAO_O_QUE_SIGNIFICA':
                            'a cultura e o alvo estao NA MESMA LINHA da tabela de '
                            'uso. E o documento que os une, nao nos.',
                        'ORIGEM': 'linha da tabela de uso do rotulo autorizado',
                        'EVIDENCE_CLASS': 'DOCUMENTO_OFICIAL',
                        'O_QUE_NAO_PROVA': 'nao prova eficacia, recomendacao nem '
                                           'prioridade. O rotulo autoriza.',
                    })
        n = len(pares) - n0
        estados['LIDO' if n else 'TABELA_SEM_PAR'] += 1
        por_produto.append({'REGISTRATION_ID': it['REGISTRATION_ID'],
                            'PRODUCT': it.get('PRODUCT'),
                            'ESTADO_DA_LEITURA': 'LIDO' if n else 'TABELA_SEM_PAR',
                            'PARES': n})

    # dedup por (produto, cultura, alvo canonico) preservando a primeira citação
    vistos, unicos = set(), []
    for p in pares:
        ch = (p['REGISTRATION_ID'], p['CULTURA_CANONICA'], p['ALVO_CANONICO'],
              p['ALVO_LITERAL'].lower(), p.get('LIGACAO_NIVEL'))
        if ch in vistos:
            continue
        vistos.add(ch)
        unicos.append(p)

    com = sum(1 for x in por_produto
              if x['ESTADO_DA_LEITURA'] in ('LIDO', 'LIDO_COMO_HERBICIDA'))
    saida = {
        'DATASET': 'IT-ROTULOS-PARES',
        'UNIDADE': 'PAR produto x cultura x alvo, lido DENTRO de uma linha da tabela',
        'LEI': 'AUDITAR POR PAR, NUNCA POR ALVO. Cruzar cultura de uma linha com alvo '
               'de outra produz autorizacao que nao existe.',
        'HERDADO_DE': 'portal-sintonia/pares-da-bula.py (Brasil)',
        'FONTE': 'PDF do rotulo autorizado, Ministero della Salute',
        'PRODUTOS_NO_REGISTRO': len(por_produto),
        'PRODUTOS_COM_PAR_LIDO': com,
        'COBERTURA': '%d/%d (%.1f%%)' % (com, len(por_produto),
                                         100.0 * com / max(1, len(por_produto))),
        'COBERTURA_E_PISO': 'ausencia aqui e ausencia NA NOSSA LEITURA, nunca no registro',
        'AFIRMACAO_PROIBIDA': 'a ADAMA nao tem produto para X',
        'PARES_TOTAL': len(unicos),
        'PARES_POR_NIVEL_DE_LIGACAO': dict(Counter(
            p.get('LIGACAO_NIVEL', 'NAO_SEI') for p in unicos)),
        'LEI_DO_NIVEL_DE_LIGACAO':
            'LINHA_DA_TABELA e DECLARACAO_DE_PRODUTO NAO SE SOMAM numa afirmacao '
            'de tela. O primeiro e o documento unindo cultura e alvo. O segundo '
            'somos nos aproximando duas listas que o rotulo manteve separadas. '
            'ESPECTRO DE PRODUTO NAO E ESPECTRO NA CULTURA.',
        'ESTADOS_DA_LEITURA': dict(estados),
        'CULTURAS_DISTINTAS': len(set(p['CULTURA_CANONICA'] for p in unicos)),
        'ALVOS_CANONICOS_DISTINTOS': len(set(p['ALVO_CANONICO'] for p in unicos)),
        'ALVOS_NAO_MAPEADOS': sum(1 for p in unicos
                                  if p['ALVO_CANONICO'] == 'NAO_MAPEADO'),
        'POR_PRODUTO': por_produto,
        'PARES': unicos,
    }
    destino = os.path.join(SAIDA, 'IT-ROTULOS-PARES.json')
    json.dump(saida, open(destino, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

    print('produtos:', len(por_produto), '| com par lido:', com,
          '(%s)' % saida['COBERTURA'])
    print('pares:', len(unicos), '| culturas:', saida['CULTURAS_DISTINTAS'],
          '| alvos canonicos:', saida['ALVOS_CANONICOS_DISTINTOS'],
          '| nao mapeados:', saida['ALVOS_NAO_MAPEADOS'])
    print('estados:', dict(estados))
    print('gravado:', os.path.relpath(destino, ROOT))


if __name__ == '__main__':
    main()
