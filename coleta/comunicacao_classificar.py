#!/usr/bin/env python3
"""
CLASSIFICAÇÃO DA COMUNICAÇÃO PÚBLICA — sobre o artefato já pago, de graça.

    py coleta/comunicacao_classificar.py

POR QUE ISTO É UM ARQUIVO SEPARADO DA COLETA
----------------------------------------------
Porque classificador erra, e erro de classificador não pode custar execução paga. Rodando
sobre `POSTS-*.json`, ele pode ser refeito quantas vezes o critério mudar sem tocar na
Apify. É a mesma separação que o piloto de sensores já usa nesta casa.

A REGRA QUE MANDA EM TUDO: SÓ O QUE O TEXTO SUSTENTA
------------------------------------------------------
    NÃO INFERIR PAÍS PELA LÍNGUA.
    NÃO INFERIR CULTURA PELA IMAGEM.
    NÃO USAR A CONSULTA DE COLETA COMO VERDADE.

A terceira é a mais fácil de quebrar sem perceber. Se eu coletei a conta espanhola da
Syngenta, é tentador escrever `COUNTRY_OF_FACT = ES` em cada post. Mas a conta espanhola
publica sobre a feira de Berlim, sobre resultado global e sobre vaga de emprego em
Basileia. **A conta tem país; o FATO do post pode não ter.** Por isso `COUNTRY_OF_FACT`
nasce `NOT_KNOWN` e só é preenchido quando o próprio texto nomeia o lugar.

    ACCOUNT_COUNTRY != COUNTRY_OF_FACT. São dois campos porque são duas coisas.

UMA PUBLICAÇÃO PODE TER MAIS DE UM TIPO
-----------------------------------------
`COMMUNICATION_TYPES` é LISTA, não escolha única — o §5 manda. Um post que anuncia um
fungicida numa jornada técnica é `PRODUCT_COMMUNICATION` **e** `FIELD_EVENT` **e**
`TECHNICAL_EDUCATION`. Forçar um rótulo só faria a contagem por tipo mentir nos dois
sentidos ao mesmo tempo.

E quando nada casa, o tipo é `NOT_KNOWN` — nunca `OTHER`. `OTHER` significa "é outra
coisa, e eu sei qual"; `NOT_KNOWN` significa "eu não consegui decidir". Colapsar os dois
apaga exatamente a medida de cobertura que o §17 pede.

O QUE ESTA CAMADA NUNCA DIZ
-----------------------------
Nem venda, nem demanda, nem participação de mercado, nem investimento, nem sucesso. A
saída é `COMPETITOR_PUBLIC_COMMUNICATION_OBSERVED` e nada além. Que uma empresa fale
muito de um produto não é evidência de que ele venda, e que ela cale não é evidência de
que ele tenha sumido.
"""
import json
import os
import re
import unicodedata

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SAIDA = os.path.join(ROOT, 'data', 'samples', 'COMPETITOR-PUBLIC-COMM')
DATASET_OWNER = 'COMPETITOR_PUBLIC_COMMUNICATION_EAME'
NAO_SEI = 'NOT_KNOWN'

PLATAFORMAS = ('YOUTUBE', 'INSTAGRAM', 'FACEBOOK', 'LINKEDIN')

# ── §5 · TIPOS DE COMUNICAÇÃO ───────────────────────────────────────────────────
# Termos NA LÍNGUA DE CADA PAÍS. Buscar "webinar" em francês e esperar achar "webinaire"
# é o mesmo erro que a casa já mediu na camada de voz: o vocabulário muda de nome por
# país, e uma lista só em inglês mede a presença do inglês, não a do assunto.
TIPOS = {
    'PRODUCT_COMMUNICATION': [
        'nuevo producto', 'nuevo fungicida', 'nuevo herbicida', 'nuevo insecticida',
        'lanzamiento', 'gama', 'nuovo prodotto', 'lancio', 'nuovo fungicida',
        'nouveau produit', 'lancement', 'nouvelle solution', 'gamme'],
    'TECHNICAL_EDUCATION': [
        'como aplicar', 'recomendacion', 'buenas practicas', 'guia tecnica',
        'come applicare', 'consigli tecnici', 'buone pratiche',
        'comment appliquer', 'conseils techniques', 'bonnes pratiques'],
    'FIELD_EVENT': [
        'jornada', 'jornada tecnica', 'feria', 'giornata', 'convegno', 'fiera',
        'journee', 'salon', 'rencontre'],
    'DEMO_TRIAL': [
        'ensayo', 'ensayos', 'campo de ensayo', 'prova di campo', 'sperimentazione',
        'essai', 'essais', 'demonstration', 'demostracion', 'dimostrazione'],
    'WEBINAR': ['webinar', 'webinaire', 'seminario online', 'diretta online'],
    'REGULATORY_COMMUNICATION': [
        'autorizacion', 'registro', 'retirada', 'normativa',
        'autorizzazione', 'revoca', 'norma', 'autorisation', 'retrait',
        'reglementation', 'homologation'],
    'CORPORATE_COMMUNICATION': [
        'resultados', 'inversion', 'aniversario', 'compromiso',
        'risultati', 'investimento', 'anniversario', 'impegno',
        'resultats', 'investissement', 'anniversaire', 'engagement'],
    # O convite tem que trazer o EMPREGO junto. A primeira versão listava só
    # "rejoignez" e "unisciti", e classificou "Rejoignez notre webinaire sur le mildiou"
    # como vaga de emprego — o verbo de convite é o mesmo para chamar para um webinário
    # e para chamar para o time. Termo genérico não é termo curto: é termo AMBÍGUO, e a
    # correção não é medir o tamanho, é exigir o complemento.
    'RECRUITMENT_HR': [
        'vacante', 'unete al equipo', 'oferta de empleo', 'estamos contratando',
        'posizione aperta', 'unisciti al team', 'offerta di lavoro',
        'offre emploi', 'offre d emploi', 'rejoignez notre equipe',
        'rejoindre notre equipe', 'nous recrutons'],
    'BRAND_AWARENESS': [
        'orgullosos', 'nuestra mision', 'juntos', 'fieri', 'la nostra missione',
        'insieme', 'fiers', 'notre mission', 'ensemble'],
}

# ── §6 · CONTEXTO AGRONÔMICO ────────────────────────────────────────────────────
# Cultura e problema, na língua de cada país. Mesma regra da matriz de recorte já
# congelada nesta casa: termo com menos de 5 letras só casa como palavra inteira.
CULTURAS = {
    'OLIVE': ['olivo', 'olivar', 'olivicoltura', 'oliveto', 'olivier', 'oliveraie'],
    'CEREAL': ['trigo', 'cebada', 'cereal', 'grano duro', 'frumento', 'orzo',
               'ble', 'orge', 'cereale', 'cereales'],
    'VINE': ['vid', 'viñedo', 'vinedo', 'vite', 'vigneto', 'vigne', 'vignoble'],
    'MAIZE': ['maiz', 'mais', 'granoturco'],
    'POTATO': ['patata', 'pomme de terre'],
    'HORTICULTURE': ['horticola', 'hortalizas', 'orticola', 'maraichage'],
}
PROBLEMAS = {
    'REPILO': ['repilo', 'venturia oleaginea'],
    'SEPTORIA': ['septoria', 'septoriosis', 'septoriose', 'zymoseptoria'],
    'DOWNY_MILDEW': ['mildiu', 'peronospora', 'mildiou', 'plasmopara'],
    'FUSARIUM': ['fusarium', 'fusariosi', 'fusariose', 'micotossine', 'micotoxinas'],
    'FLAVESCENCE': ['flavescenza dorata', 'flavescence doree'],
    'AMARANTHUS': ['amaranthus', 'amaranto'],
    'NEMATODE': ['nematodo', 'nematodi', 'nematode'],
}

# Nome de país e de região DECLARADO no texto. É o único jeito de `COUNTRY_OF_FACT`
# nascer: o texto nomear o lugar. Nunca a língua, nunca a conta.
LUGARES = {
    'ES': ['españa', 'espana', 'andalucia', 'cataluña', 'cataluna', 'aragon',
           'castilla', 'valencia', 'extremadura', 'jaen', 'cordoba', 'sevilla'],
    'IT': ['italia', 'puglia', 'sicilia', 'toscana', 'veneto', 'piemonte',
           'emilia', 'lombardia'],
    'FR': ['france', 'occitanie', 'bourgogne', 'champagne', 'bordeaux',
           'bretagne', 'normandie', 'beauce'],
}


def _norm(s):
    s = unicodedata.normalize('NFKD', str(s or ''))
    s = ''.join(c for c in s if not unicodedata.combining(c))
    return re.sub(r'\s+', ' ', s.lower())


def _casa(texto, termo):
    """Termo curto (<5 letras) só casa como palavra inteira. Herdado da matriz."""
    t = _norm(termo)
    if len(t.replace(' ', '')) < 5:
        return re.search(r'(?<![a-z0-9])%s(?![a-z0-9])' % re.escape(t), texto) is not None
    return t in texto


def _achar(texto, tabela):
    return sorted({k for k, termos in tabela.items()
                   if any(_casa(texto, t) for t in termos)})


# ── AS DUAS FONTES DE TEXTO DE UMA PUBLICAÇÃO, E ELAS NÃO SE SOMAM ──────────
# `TEXT` é a LEGENDA: o que o autor escreveu. `TRANSCRIPT_TEXT` é a FALA: o que
# alguém disse no vídeo. São dois textos do mesmo minuto, de dois atos
# diferentes — e um Reel pode ter noventa segundos de septoriose na fala e
# «confira nosso dia de campo» na legenda.
#
# Antes de 2026-09-10 esta camada lia só `TITLE` e `TEXT`, e o conteúdo falado
# era invisível. Fechar esse buraco NÃO é concatenar os dois: se uma
# classificação nascer de uma frase falada, tem de continuar a ser possível
# prová-lo — e um campo somado apaga exatamente essa prova.
#
#     CASAR NOS DOIS, MAS SABER EM QUAL CASOU.
FONTES_DE_TEXTO = (
    ('CAPTION', ('TITLE', 'TEXT')),
    ('TRANSCRIPT', ('TRANSCRIPT_TEXT',)),
)


def _textos(item):
    """→ {fonte: texto normalizado} para cada fonte que REALMENTE trouxe texto."""
    fora = {}
    for fonte, campos in FONTES_DE_TEXTO:
        pedaços = [item.get(c) for c in campos]
        pedaços = [p for p in pedaços if p and p != NAO_SEI]
        t = _norm(' '.join(str(p) for p in pedaços))
        if t.strip():
            fora[fonte] = t
    return fora


def _achar_por_fonte(textos, tabela):
    """→ (rótulos ordenados, {rótulo: [fontes que o sustentam]}).

    A segunda metade é o que impede a evidência de se perder: saber QUE um post
    fala de septoriose vale pouco se ninguém puder dizer se isso estava escrito
    ou foi dito em voz alta.
    """
    origem = {}
    for fonte, texto in textos.items():
        for rotulo in _achar(texto, tabela):
            origem.setdefault(rotulo, []).append(fonte)
    return sorted(origem), {k: sorted(v) for k, v in origem.items()}


def classificar(item):
    """→ o item com os campos do §5 e do §6. Não altera o original."""
    textos = _textos(item)
    # Compatibilidade: `texto` continua a existir e continua a ser a legenda +
    # título, porque é isso que os campos antigos sempre mediram.
    texto = textos.get('CAPTION', '')
    tem_texto = bool(textos)

    tipos, tipos_de = _achar_por_fonte(textos, TIPOS)
    culturas, culturas_de = _achar_por_fonte(textos, CULTURAS)
    problemas, problemas_de = _achar_por_fonte(textos, PROBLEMAS)
    paises, paises_de = _achar_por_fonte(textos, LUGARES)

    fontes = sorted(textos)
    so_da_fala = sorted({r for r, f in list(tipos_de.items()) + list(culturas_de.items())
                         + list(problemas_de.items()) if f == ['TRANSCRIPT']})

    fora = dict(item)
    fora.update({
        'TEXT_AVAILABLE': 'YES' if tem_texto else 'NO',
        # QUAIS fontes de texto este item tinha. Sem isto, «não casou nada» num
        # Reel mudo e num Reel nunca transcrito leem-se igual.
        'TEXT_SOURCES': fontes or [NAO_SEI],
        'CAPTION_AVAILABLE': 'YES' if 'CAPTION' in textos else 'NO',
        'TRANSCRIPT_AVAILABLE': 'YES' if 'TRANSCRIPT' in textos else 'NO',
        'TRANSCRIPT_STATE': item.get('TRANSCRIPT_STATE', NAO_SEI),
        # O QUE SÓ A FALA TROUXE. É a medida do buraco que a transcrição fechou.
        'FOUND_ONLY_IN_TRANSCRIPT': so_da_fala or [],
        'EVIDENCE_BY_LABEL': {
            'COMMUNICATION_TYPES': tipos_de,
            'CROP': culturas_de,
            'ISSUE': problemas_de,
            'COUNTRY_OF_FACT': paises_de,
        },
        'COMMUNICATION_TYPES': tipos or [NAO_SEI],
        'COMMUNICATION_TYPE_EVIDENCE': (
            'termos casados em: %s' % ', '.join(
                sorted({f for fs in tipos_de.values() for f in fs})) if tipos else
            ('nenhum termo da tabela casou — NOT_KNOWN, não OTHER'
             if tem_texto else 'a coleta não devolveu texto para este item')),
        'CROP': culturas or [NAO_SEI],
        'ISSUE': problemas or [NAO_SEI],
        # §6 em letra: o país do FATO só existe se o TEXTO nomear o lugar. A conta é
        # espanhola; o post pode ser sobre Berlim.
        'COUNTRY_OF_FACT': (paises[0] if len(paises) == 1 else
                            (paises if paises else NAO_SEI)),
        # ONDE o lugar foi nomeado importa tanto quanto QUE lugar. Um nome ouvido
        # numa fala e um nome escrito pelo autor não têm o mesmo peso, e quem
        # decidir depois precisa de saber qual dos dois foi.
        'COUNTRY_OF_FACT_EVIDENCE': (
            'o lugar é nomeado em: %s' % ', '.join(
                sorted({f for fs in paises_de.values() for f in fs})) if paises else
            'o texto não nomeia lugar. A conta é de %s, mas conta != fato — e a língua '
            'não decide país.' % item.get('COUNTRY_SCOPE', NAO_SEI)),
        'REGION_OF_FACT': NAO_SEI,
        'PRODUCT': NAO_SEI,
        'ACTIVE_INGREDIENT': NAO_SEI,
        'APPLICATION_TIMING': NAO_SEI,
        'SEASON': NAO_SEI,
        # §10: produto e marca são do Competitor Foresight. Aqui só se houver ID pronto.
        'FORESIGHT_PRODUCT_ID': NAO_SEI,
        'FORESIGHT_ID_SOURCE': (
            'o Foresight é dono de IP/BRAND/PRODUTO. Sem ID resolvido lá, NOT_KNOWN — '
            'esta camada não cria ID de produto próprio.'),
        'EVIDENCE_CLASS': 'COMPETITOR_PUBLIC_COMMUNICATION_OBSERVED',
        'DATASET_OWNER': DATASET_OWNER,
    })
    return fora


def montar():
    itens, lidos, ausentes = [], [], []
    for p in PLATAFORMAS:
        caminho = os.path.join(SAIDA, 'POSTS-%s.json' % p)
        if not os.path.exists(caminho):
            ausentes.append(p)
            continue
        with open(caminho, encoding='utf-8') as f:
            d = json.load(f)
        lidos.append(p)
        itens.extend(classificar(i) for i in (d.get('ITEMS') or []))

    por_tipo, por_cultura, por_problema, por_pais = {}, {}, {}, {}
    for i in itens:
        for t in i['COMMUNICATION_TYPES']:
            por_tipo[t] = por_tipo.get(t, 0) + 1
        for c in i['CROP']:
            por_cultura[c] = por_cultura.get(c, 0) + 1
        for q in i['ISSUE']:
            por_problema[q] = por_problema.get(q, 0) + 1
        k = i['COUNTRY_OF_FACT']
        k = '+'.join(k) if isinstance(k, list) else k
        por_pais[k] = por_pais.get(k, 0) + 1

    com_texto = sum(1 for i in itens if i['TEXT_AVAILABLE'] == 'YES')
    return {
        'SOURCE_ID': 'COMPETITOR-PUBLIC-COMM/CLASSIFICADO-V1',
        'DATASET_OWNER': DATASET_OWNER,
        'source': 'derivado de POSTS-*.json — nenhuma execução, nenhum custo',
        'SOURCE_LOCATION': 'derivado',
        'EVIDENCE_CLASS': 'COMPETITOR_PUBLIC_COMMUNICATION_OBSERVED',
        'APIFY_RUNS': 0, 'COST_USD': 0,
        'O_QUE_ISTO_NUNCA_DIZ': ['SALES', 'DEMAND', 'MARKET_SHARE', 'INVESTMENT',
                                 'SUCCESS'],
        'PLATFORMS_READ': lidos,
        'PLATFORMS_NOT_COLLECTED_YET': ausentes,
        'PLATFORMS_NOT_COLLECTED_MEANS': (
            'a coleta ainda não rodou nesta plataforma. NÃO é "a plataforma não '
            'devolveu nada" e NÃO é "a empresa não comunica lá".'),
        'ITEM_COUNT': len(itens),
        'TEXT_COVERAGE': '%d/%d' % (com_texto, len(itens)),
        'BY_COMMUNICATION_TYPE': por_tipo,
        'BY_CROP': por_cultura,
        'BY_ISSUE': por_problema,
        'BY_COUNTRY_OF_FACT': por_pais,
        'ITEMS': itens,
    }


if __name__ == '__main__':
    corpo = montar()
    os.makedirs(SAIDA, exist_ok=True)
    with open(os.path.join(SAIDA, 'CLASSIFICADO-V1.json'), 'w', encoding='utf-8') as f:
        json.dump(corpo, f, ensure_ascii=False, indent=1)
    print('plataformas lidas:            %s' % (corpo['PLATFORMS_READ'] or 'nenhuma'))
    print('plataformas ainda não coletadas: %s'
          % (corpo['PLATFORMS_NOT_COLLECTED_YET'] or 'nenhuma'))
    print('itens classificados:          %d' % corpo['ITEM_COUNT'])
    print('cobertura de texto:           %s' % corpo['TEXT_COVERAGE'])
    print('por tipo:    %s' % corpo['BY_COMMUNICATION_TYPE'])
    print('por cultura: %s' % corpo['BY_CROP'])
    print('por problema:%s' % corpo['BY_ISSUE'])
    print('país do fato:%s' % corpo['BY_COUNTRY_OF_FACT'])
