#!/usr/bin/env python3
"""
PROVENIÊNCIA — o RUN_ID deixa de ser um rótulo e passa a resolver.

O defeito que este arquivo fecha: até 2026-08-29 o `RUN_ID` agrupava registros entre si e
não resolvia para nada fora do repositório. Dado um vídeo, não havia como responder
"que execução produziu isto, com que ator, que entrada e que custo".

A cadeia que passa a existir:

    CONTENT → RUN_ID → RUN_MANIFEST → INPUT / ACTOR / DATASET / RAW

Três decisões carregadas aqui:

1. **CAMPO DESCONHECIDO É `NOT_PRESERVED`, NUNCA AUSENTE.**
   Execução antiga que não capturou `ACTOR_VERSION` declara `NOT_PRESERVED`. Isso é
   diferente de `NAO_SEI` (a fonte não informa) e muito diferente da chave sumir.

2. **NUNCA GRAVAR TOKEN.** `INPUT` guarda a consulta e os parâmetros; credencial jamais.
   Há teste que varre o manifesto atrás de padrão de token.

3. **TEMPO É MEDIDO, NÃO INFERIDO.** `STARTED_AT`/`FINISHED_AT` vêm da execução. Sem eles,
   nenhuma afirmação de ordem entre camadas é permitida — ver `pode_afirmar_ordem()`.
"""
import datetime
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
MANIFESTO = os.path.join(ROOT, 'data', 'samples', 'RUN-MANIFEST.json')

NAO_SEI = 'NÃO SEI'
NOT_PRESERVED = 'NOT_PRESERVED'

# Campos obrigatórios de todo manifesto de execução.
CAMPOS_RUN = [
    'RUN_ID', 'PLATFORM', 'ACTOR', 'ACTOR_VERSION', 'STARTED_AT', 'FINISHED_AT',
    'INPUT', 'COUNTRY', 'MISSION', 'QUERY', 'DATASET_ID',
    'ITEM_COUNT_RAW', 'ITEM_COUNT_NORMALIZED', 'COST_USD', 'SOURCE_VERSION',
    'STATUS', 'ERROR', 'CAPTURE_METHOD', 'EVIDENCE_PATH', 'RAW_EVIDENCE_PATH',
    'RAW_EVIDENCE_STATE',
    # Hora em que o coletor GRAVOU a saída. É medida de verdade, mas NÃO é a hora da
    # execução na plataforma — por isso vive em campo próprio e nunca é usada como
    # STARTED_AT/FINISHED_AT. Passar hora de escrita por hora de execução seria
    # exatamente o erro que a auditoria derrubou.
    'OUTPUT_WRITTEN_AT',
]

STATUS_RUN = ['SUCCESS', 'PARTIAL', 'FAILED', 'NOT_PRESERVED']
# Estado da evidência bruta. `NOT_PRESERVED` é uma confissão, não um sinônimo de ausência
# de dado: quer dizer que a resposta crua existiu e não foi guardada.
ESTADOS_RAW = ['PRESERVED', 'NOT_PRESERVED', 'NOT_APPLICABLE']

TOKEN = re.compile(r'apify_api_[A-Za-z0-9]{10,}|Bearer\s+[A-Za-z0-9._\-]{20,}')


def run_vazio():
    """Todo campo presente, todo valor em NOT_PRESERVED."""
    return {c: NOT_PRESERVED for c in CAMPOS_RUN}


def novo_run(run_id, **campos):
    """Monta um manifesto completo. Campo não informado fica NOT_PRESERVED, nunca some."""
    r = run_vazio()
    r['RUN_ID'] = run_id
    for k, v in campos.items():
        if k not in CAMPOS_RUN:
            raise KeyError('campo fora do contrato de RUN: %s' % k)
        r[k] = v
    checar_token(r)
    return r


def checar_token(run):
    """Um manifesto nunca pode carregar credencial."""
    achado = TOKEN.search(json.dumps(run, ensure_ascii=False))
    if achado:
        raise ValueError('credencial no manifesto de execução — nunca gravar token')
    return True


def runs_duplicados(manifesto=None):
    """RUN_IDs repetidos no manifesto.

    `carregar()` indexa por RUN_ID. Com um id repetido, o segundo registro SOBRESCREVIA o
    primeiro e uma execução inteira desaparecia sem nada reprovar — medido na MISSÃO 10C:
    11 execuções na lista, 10 carregadas. Perda silenciosa de proveniência.
    """
    caminho = manifesto or MANIFESTO
    if not os.path.exists(caminho):
        return []
    with open(caminho, encoding='utf-8') as f:
        d = json.load(f)
    vistos, dup = set(), []
    for r in d.get('RUNS', []):
        rid = r.get('RUN_ID')
        if rid in vistos:
            dup.append(rid)
        vistos.add(rid)
    return sorted(set(dup))


def carregar():
    if not os.path.exists(MANIFESTO):
        return {}
    with open(MANIFESTO, encoding='utf-8') as f:
        d = json.load(f)
    return {r['RUN_ID']: r for r in d.get('RUNS', [])}


def resolver(run_id):
    """RUN_ID -> manifesto. É isto que faltava: o rótulo agora resolve."""
    return carregar().get(run_id)


def _cabecalho(captured_at):
    """As frases que o manifesto diz sobre si proprio. Um sitio so.

    Estavam dentro de `gravar()`, e por isso quem escrevesse por fora ficava sem
    elas — foi exactamente o que aconteceu com as duas pecas que apendiam o
    recibo a mao. Uma casa com duas cabecas escreve dois ficheiros diferentes
    com o mesmo nome.
    """
    return {
        'SOURCE_ID': 'RUN-MANIFEST',
        'source': 'manifesto de execuções de coleta do SINTONIA EAME',
        'SOURCE_LOCATION': 'interno — metadado de coleta',
        'FACT_LOCATION': 'n/a — descreve execução, não fato do mundo',
        'ORIGINAL_LANGUAGE': 'pt',
        'captured_at': captured_at,
        'PARA_QUE_SERVE': (
            'dado um registro qualquer, o RUN_ID leva a esta tabela e a tabela diz que ator '
            'rodou, com que entrada, quando, quanto custou e onde está a evidência bruta. '
            'Sem isto o RUN_ID só agrupa registros entre si.'),
        'CAMPO_DESCONHECIDO': (
            'NOT_PRESERVED significa que o campo existiu na execução e não foi capturado. '
            'É confissão, não ausência de dado — e é diferente de NÃO SEI, que é a fonte '
            'não informar.'),
        'NUNCA_GRAVAR_TOKEN': 'INPUT guarda consulta e parâmetros. Credencial, jamais.',
    }


def gravar(runs, *, captured_at):
    """Persiste o manifesto. `runs` é lista de dicionários já no contrato."""
    for r in runs:
        faltando = set(CAMPOS_RUN) - set(r)
        if faltando:
            raise KeyError('manifesto incompleto, faltam: %s' % sorted(faltando))
        checar_token(r)
        if r['STATUS'] not in STATUS_RUN:
            raise ValueError('STATUS fora do contrato: %s' % r['STATUS'])
        if r['RAW_EVIDENCE_STATE'] not in ESTADOS_RAW:
            raise ValueError('RAW_EVIDENCE_STATE fora do contrato: %s' % r['RAW_EVIDENCE_STATE'])
    corpo = dict(_cabecalho(captured_at), RUNS=runs)
    with open(MANIFESTO, 'w', encoding='utf-8') as f:
        json.dump(corpo, f, ensure_ascii=False, indent=1)
    return corpo


# ---------------------------------------------------------------- ordem entre camadas
# ─────────────────────────────────────────────────────────────────────────────
# A PORTA UNICA DO MANIFESTO
# ─────────────────────────────────────────────────────────────────────────────
class ManifestoIlegivel(Exception):
    """O ficheiro existe e nao se consegue ler. Nao se escreve por cima."""


def acrescentar(recibo, *, captured_at=None):
    """A UNICA porta por onde uma corrida entra no RUN-MANIFEST.

    ⚠️ TRES PECAS ESCREVIAM AQUI, CADA UMA A SUA MANEIRA.

        orquestrador/orquestrador.py   le, junta, escreve com indent=2
        coleta/golden_path_pdf.py      le, junta, escreve com indent=2
        regras/proveniencia.py         valida o contrato e escreve com indent=1

    e o mapa elegia dono por ordem alfabetica — ou seja, por sorteio. Duas das
    tres nao passavam por `gravar()`, que e onde o contrato e conferido, e o
    resultado esta medido no proprio ficheiro: das 20 corridas, DEZ nao trazem
    `DATASET_ID`, `SOURCE_VERSION`, `RAW_EVIDENCE_PATH` nem `RAW_EVIDENCE_STATE`,
    e TRES trazem `STATUS: OK` — uma palavra que o contrato nao aceita.

        EXECUTAR UMA CORRIDA NAO E SER A AUTORIDADE SOBRE A PROCEDENCIA DELA.

    Quem corre continua a correr e a trazer o que sabe: run id, ator, horas,
    rota, contagens, custo. Quem ESCREVE e esta casa, que e a dona da lei.

    O QUE ESTA FUNCAO GARANTE, E O QUE ELA RECUSA
    ----------------------------------------------
    · Campo do contrato que o chamador nao trouxe fica `NOT_PRESERVED`, que e a
      confissao definida no proprio manifesto — «existiu na execucao e nao foi
      capturado». Nao fica AUSENTE, que e nao ter havido afirmacao nenhuma, e
      nao fica inventado. A lista dos campos completados VOLTA ao chamador, para
      a divida ter numero em vez de ficar escondida.
    · `STATUS` e `RAW_EVIDENCE_STATE` fora do contrato LEVANTAM. Duas palavras
      para o mesmo estado e o mesmo defeito da autoria, um andar abaixo.
    · Manifesto ilegivel LEVANTA. Um ficheiro truncado lido como zero corridas
      apagaria a historia toda na escrita seguinte — foi assim que o livro de
      decisoes quase se perdeu, e a licao e a mesma:

          FICHEIRO ILEGIVEL != FICHEIRO VAZIO.

    · A historia NAO e revalidada. As corridas que ja la estao ficam como estao:
      sao divida medida, e conferi-las agora rebentaria a escrita de hoje por
      causa de ontem. O aperto e para a frente.
    """
    corpo = {}
    if os.path.exists(MANIFESTO):
        try:
            with open(MANIFESTO, encoding='utf-8') as f:
                corpo = json.load(f)
        except (json.JSONDecodeError, OSError) as e:
            raise ManifestoIlegivel(
                'RUN-MANIFEST ilegivel (%s). NAO foi escrito nada — o que la '
                'esta seria apagado por um ficheiro novo.' % e) from e
        if not isinstance(corpo, dict):
            raise ManifestoIlegivel(
                'RUN-MANIFEST nao e um objecto com RUNS. NAO foi escrito nada.')

    novo = dict(recibo)
    completados = sorted(c for c in CAMPOS_RUN if c not in novo)
    for c in completados:
        novo[c] = NOT_PRESERVED

    checar_token(novo)
    if novo['STATUS'] not in STATUS_RUN:
        raise ValueError(
            'STATUS fora do contrato: %r. O manifesto fala %s.'
            % (novo['STATUS'], STATUS_RUN))
    if novo['RAW_EVIDENCE_STATE'] not in ESTADOS_RAW:
        raise ValueError('RAW_EVIDENCE_STATE fora do contrato: %r'
                         % novo['RAW_EVIDENCE_STATE'])

    runs = list(corpo.get('RUNS') or [])
    if any(r.get('RUN_ID') == novo.get('RUN_ID') for r in runs):
        return completados          # ja registada; nao se duplica nem se reescreve
    runs.append(novo)

    corpo.update(_cabecalho(captured_at or corpo.get('captured_at')
                            or datetime.datetime.now(
                                datetime.timezone.utc).isoformat()))
    corpo['RUNS'] = runs
    os.makedirs(os.path.dirname(MANIFESTO), exist_ok=True)
    with open(MANIFESTO, 'w', encoding='utf-8') as f:
        json.dump(corpo, f, ensure_ascii=False, indent=1)
    return completados


def instante(v):
    """Converte um carimbo em datetime COM FUSO, ou devolve None.

    Por que existe: até a MISSÃO 10C a ordem era decidida comparando STRINGS. Isso produz
    resposta CONFIANTE e ERRADA em dois casos reais e reproduzíveis:

      · fuso — `2026-08-29T09:00:00+02:00` (07:00 UTC) contra `2026-08-29T08:00:00Z`
        (08:00 UTC). A verdade é BEFORE; a comparação lexicográfica devolvia AFTER.
        O repositório JÁ mistura os dois formatos: o export do ROPF traz `+02:00` e as
        execuções do coletor trazem `Z`.
      · zero à esquerda — `2026-8-29` ordena depois de `2026-08-29` como texto.

    E a guarda antiga era uma lista de quatro valores proibidos, não uma validação: um
    `STARTED_AT` com o texto `desconhecido` passava e sustentava um BEFORE.
    Agora só sustenta ordem o que se converte em instante. Falha fechada.
    """
    if not isinstance(v, str):
        return None
    v = v.strip()
    if not v or v in (NOT_PRESERVED, NAO_SEI):
        return None
    try:
        d = datetime.datetime.fromisoformat(v.replace('Z', '+00:00'))
    except ValueError:
        return None
    # Data sem hora não mede execução: '2026-08-29' viraria meia-noite inventada.
    if len(v) <= 10:
        return None
    if d.tzinfo is None:
        return None          # sem fuso não é instante, é hora local de lugar nenhum
    return d


def pode_afirmar_ordem(run_a, run_b):
    """`X BEFORE Y` só é dizível quando as duas execuções têm hora MEDIDA e comparável."""
    for r in (run_a, run_b):
        if not r:
            return False, 'execução sem manifesto'
        for c in ('STARTED_AT', 'FINISHED_AT'):
            if instante(r.get(c)) is None:
                return False, '%s sem %s medido em instante comparável (valor: %r)' % (
                    r.get('RUN_ID'), c, r.get(c))
    return True, ''


def ordem(run_a, run_b):
    """Devolve BEFORE / AFTER / OVERLAPS, ou NAO_DIZIVEL com o motivo.

    Compara INSTANTES, nunca strings.
    """
    ok, motivo = pode_afirmar_ordem(run_a, run_b)
    if not ok:
        return 'NAO_DIZIVEL', motivo
    a_ini, a_fim = instante(run_a['STARTED_AT']), instante(run_a['FINISHED_AT'])
    b_ini, b_fim = instante(run_b['STARTED_AT']), instante(run_b['FINISHED_AT'])
    if a_fim <= b_ini:
        return 'BEFORE', ''
    if b_fim <= a_ini:
        return 'AFTER', ''
    return 'OVERLAPS', ''

# ══════════════════════════════════════════════════════════════════════════
# A ESPÉCIE DO TEXTO — porque «tem texto» nunca provou «é a fala do vídeo»
# ══════════════════════════════════════════════════════════════════════════
# A C5 mediu, no corpus já pago: dos 28 textos com conteúdo, ONZE são inglês
# vindo de vídeo NÃO-inglês. O vídeo `RisRARQSFAg` — canal AIPO Verona, título
# «Periodico olivo 1° Maggio 2026» — guardou «Olive growers, welcome back to
# issue 18 of the May 1, 2026 periodical».
#
#     TEXT EXISTS != ORIGINAL TEXT PROVEN.
#
# Isto vive AQUI, e não no primeiro consumidor que precisou dele, porque a
# pergunta não é do sensor: é da proveniência. Qualquer texto derivado de mídia,
# de qualquer plataforma, tem espécie — e este ficheiro já é o dono do
# vocabulário da ausência (`NAO_SEI`, `NOT_PRESERVED`) e das listas fechadas que
# governam o que uma corrida pode declarar.
#
#     ONE CONCEPT -> ONE OWNER. E o dono da procedência de um texto derivado
#     não é quem o colheu primeiro: é quem governa procedência.
#
# ══════════════════════════════════════════════════════════════════════════
# DOIS EIXOS, PORQUE UM SÓ NÃO CONSEGUE ESCREVER O QUE A CASA PRECISA DIZER
# ══════════════════════════════════════════════════════════════════════════
# A C6 declarou QUATRO valores — `NATIVE_CAPTION_ORIGINAL`,
# `NATIVE_CAPTION_TRANSLATED`, `ASR_LOCAL`, `NÃO SEI` — e eles resolveram o
# problema que ela tinha: legenda de vídeo. Não resolvem o que atravessa a
# fronteira SCRAP -> Collection, e a razão é estrutural, não de gosto:
#
#     `ASR_LOCAL` não tem par traduzido. Um Whisper que traduz enquanto ouve
#     produz texto que NÃO é `ASR_LOCAL` (não está na língua falada) e NÃO é
#     `NATIVE_CAPTION_TRANSLATED` (não é legenda da plataforma). Com quatro
#     nomes num eixo só, esse texto não tem nome — e o que não tem nome vai
#     parar ao nome mais parecido.
#
# Por isso a espécie passa a ser um PAR, e os quatro nomes da C6 continuam a
# resolver como pares (ver `ESPECIE_COMPOSTA`). Não é um segundo modelo: é o
# mesmo, com os dois eixos que já estavam lá dentro, separados.
#
#     ESPÉCIE = (O QUE O TEXTO É) × (QUE RELAÇÃO TEM COM O ORIGINAL)
#
# ── EIXO 1 · O QUE O TEXTO É ───────────────────────────────────────────────
# Cada um destes foi MEDIDO a sair de um produtor real desta árvore, e não
# imaginado. A coluna da direita é o produtor que o prova.
#
#     AUTHOR_TEXT     o que o autor escreveu     bluesky `record.text`,
#                                                mastodon `content`,
#                                                youtube `snippet.description`,
#                                                comentário `textOriginal`,
#                                                bio de perfil `description`
#     NATIVE_CAPTION  a faixa de legenda que     linkedin
#                     a PLATAFORMA serve         `video-auto-caption-srt-…`
#     TRANSCRIPT      fala transcrita por        `adaptador_youtube`
#                     terceiro                   (actor pago, campo `transcript`)
#     ASR             fala reconhecida por       o Whisper desta casa
#                     máquina
#     PAGE_TEXT       texto raspado de uma       telegram `t.me/s/{canal}`,
#                     página renderizada         `_sem_tags(html)[:4000]`
#     DOCUMENT_TEXT   texto extraído de um       `orquestrador`
#                     artefato documental        -> `documento_estruturado`
#     UNKNOWN         ninguém declarou
#
# ⚠️ `AUTHOR_TEXT` CHAMAVA-SE `CAPTION`, E O NOME TINHA DE MUDAR.
# Medido nesta árvore, o mesmo token quer dizer duas coisas incompatíveis:
#
#     coleta/comunicacao_coleta.py   'TEXT_KIND': 'CAPTION'   = o que o autor
#                                                               escreveu
#     regras/proveniencia.py (C6)    NATIVE_CAPTION_*         = a faixa de
#                                                               legenda do vídeo
#
# Um vocabulário em que `CAPTION` é ao mesmo tempo «texto de gente» e «fala de
# máquina» não separa nada: é o ataque `caption tratado como transcript` já
# escrito no dicionário. O `BENCHMARK-V1-FINAL` viu metade disto e pediu o
# terceiro valor (`NATIVE_CAPTION`); a outra metade é esta — o primeiro valor
# também precisava de um nome que não colidisse.
#
#     DOIS SIGNIFICADOS NUM TOKEN NÃO SÃO UM VOCABULÁRIO: SÃO UMA COLISÃO
#     COM AR DE ACORDO.
AUTHOR_TEXT = 'AUTHOR_TEXT'
NATIVE_CAPTION = 'NATIVE_CAPTION'
TRANSCRIPT = 'TRANSCRIPT'
ASR = 'ASR'
PAGE_TEXT = 'PAGE_TEXT'
DOCUMENT_TEXT = 'DOCUMENT_TEXT'

# ⚠️ `UNKNOWN` E NÃO `NÃO SEI`, e a escolha não é de estilo.
# Este valor atravessa a fronteira para `leis/retorno_da_coleta.py`
# (`ESPECIE_DESCONHECIDA = "UNKNOWN"`) e para `coleta/social_envelope.py`
# (`DESCONHECIDO = 'UNKNOWN'`). Os dois já escrevem o desconhecido-de-máquina
# assim. O `NÃO SEI` desta casa é prosa para humano e tem TRÊS grafias medidas
# nesta árvore (`'NÃO SEI'`, `'NAO SEI'`, `'NOT_KNOWN'`) — atravessar uma
# fronteira com um valor que se escreve de três maneiras é entregar ao outro
# lado a obrigação de adivinhar qual delas é a sua.
TEXTO_DESCONHECIDO = 'UNKNOWN'

TEXT_KINDS = (AUTHOR_TEXT, NATIVE_CAPTION, TRANSCRIPT, ASR, PAGE_TEXT,
              DOCUMENT_TEXT, TEXTO_DESCONHECIDO)

# ── EIXO 2 · QUE RELAÇÃO TEM COM O ORIGINAL ────────────────────────────────
#     ORIGINAL    está na língua em que foi produzido
#     TRANSLATED  nasceu de OUTRA unidade de texto, noutra língua
#     UNKNOWN     ninguém declarou
#
# `UNKNOWN` não é um meio-termo entre os dois: é a ausência da declaração, e
# quem a lê tem de a tratar como ausência.
ORIGINAL = 'ORIGINAL'
TRANSLATED = 'TRANSLATED'
TEXT_RELATIONS = (ORIGINAL, TRANSLATED, TEXTO_DESCONHECIDO)

# ── DE ONDE VEIO A ESPÉCIE ─────────────────────────────────────────────────
# `INFERRED_FROM_TEXT` NÃO está aqui, e a ausência é a decisão: ler o texto para
# adivinhar a espécie seria adivinhar duas vezes — primeiro a língua, depois a
# intenção de quem legendou. Há prova que reprova se alguma base contiver `INFER`.
DECLARED_BY_PROVIDER = 'DECLARED_BY_PROVIDER'
PRODUCED_BY_LOCAL_ASR = 'PRODUCED_BY_LOCAL_ASR'
NOT_DECLARED = 'NOT_DECLARED'

# ⚠️ A QUARTA BASE, E PORQUE ELA NÃO É INFERÊNCIA.
# `bluesky_feed_autor` lê `record.text`. Ninguém na Bluesky «declarou a espécie
# daquele texto» — mas o contrato da API diz o que aquele campo É, e quem o leu
# sabe qual campo leu. Sem esta base, TODO post social nasceria `UNKNOWN` e o
# vocabulário passaria a subdeclarar ao ponto de não servir para nada.
#
#     QUAL CAMPO EU LI É UM FACTO SOBRE MIM, NÃO UM PALPITE SOBRE O CONTEÚDO.
#
# E ela tem um limite escrito: `DECLARED_BY_ROUTE` justifica a ESPÉCIE, nunca a
# LÍNGUA. Saber que li `record.text` não me diz em que língua ele está.
DECLARED_BY_ROUTE = 'DECLARED_BY_ROUTE'

BASES_DA_ESPECIE = (DECLARED_BY_PROVIDER, PRODUCED_BY_LOCAL_ASR,
                    DECLARED_BY_ROUTE, NOT_DECLARED)

# ── COMO O TEXTO NASCEU ────────────────────────────────────────────────────
# A linhagem exige método, e o método diz se houve máquina pelo meio. Os que
# têm máquina EXIGEM ferramenta declarada: um texto feito por máquina sem dizer
# qual máquina não se consegue conferir nem repetir.
LIDO_DO_CAMPO = 'READ_FROM_SOURCE_FIELD'
RASPADO_DA_PAGINA = 'SCRAPED_FROM_RENDERED_PAGE'
EXTRAIDO_DO_DOCUMENTO = 'EXTRACTED_FROM_DOCUMENT'
ASR_DO_PROVEDOR = 'PROVIDER_ASR'
ASR_DA_CASA = 'LOCAL_ASR'
TRADUCAO_DO_PROVEDOR = 'PROVIDER_TRANSLATION'
TRADUCAO_DA_CASA = 'LOCAL_TRANSLATION'
METODOS_DE_DERIVACAO = (LIDO_DO_CAMPO, RASPADO_DA_PAGINA, EXTRAIDO_DO_DOCUMENTO,
                        ASR_DO_PROVEDOR, ASR_DA_CASA, TRADUCAO_DO_PROVEDOR,
                        TRADUCAO_DA_CASA, TEXTO_DESCONHECIDO)
#: Os métodos em que uma máquina produziu o texto. Estes exigem `TOOL`.
METODOS_DE_MAQUINA = (EXTRAIDO_DO_DOCUMENTO, ASR_DO_PROVEDOR, ASR_DA_CASA,
                      TRADUCAO_DO_PROVEDOR, TRADUCAO_DA_CASA)

# ── OS NOMES DA C6, QUE CONTINUAM A RESOLVER ───────────────────────────────
# Mudou de forma, não de significado. Quem importava estes nomes continua a
# importá-los, e há prova de que apontam para o mesmo objeto.
NATIVE_CAPTION_ORIGINAL = 'NATIVE_CAPTION_ORIGINAL'
NATIVE_CAPTION_TRANSLATED = 'NATIVE_CAPTION_TRANSLATED'
ASR_LOCAL = 'ASR_LOCAL'
ESPECIES_DO_TEXTO = (NATIVE_CAPTION_ORIGINAL, NATIVE_CAPTION_TRANSLATED,
                     ASR_LOCAL, NAO_SEI)

#: O nome composto da C6 -> o par (espécie, relação) que ele sempre foi.
ESPECIE_COMPOSTA = {
    NATIVE_CAPTION_ORIGINAL: (NATIVE_CAPTION, ORIGINAL),
    NATIVE_CAPTION_TRANSLATED: (NATIVE_CAPTION, TRANSLATED),
    ASR_LOCAL: (ASR, ORIGINAL),
    NAO_SEI: (TEXTO_DESCONHECIDO, TEXTO_DESCONHECIDO),
}

#: As espécies que sustentam uma afirmação sobre O QUE FOI DITO, na língua em
#: que foi dito. Uma tradução não sustenta: as palavras são de quem traduziu.
SERVEM_PARA_ORIGINAL = (NATIVE_CAPTION_ORIGINAL, ASR_LOCAL)


def especie_declarada(item):
    """→ (espécie, base). Do que o PROVEDOR declarou. Nunca do conteúdo.

    O silêncio do provedor é `NÃO SEI` com base `NOT_DECLARED` — e isso é uma
    medição sobre ele, não uma dúvida nossa.
    """
    item = item or {}
    if item.get('trackKind') == 'asr' or item.get('kind') == 'asr':
        return NATIVE_CAPTION_ORIGINAL, DECLARED_BY_PROVIDER
    if item.get('isTranslated') or item.get('translatedFrom'):
        return NATIVE_CAPTION_TRANSLATED, DECLARED_BY_PROVIDER
    return NAO_SEI, NOT_DECLARED


def serve_para_original(especie):
    """O texto sustenta afirmação sobre a fala original? → True/False.

    `NÃO SEI` devolve False, e é o ponto inteiro desta função:

        AUSÊNCIA DE PROVA NÃO É PROVA DE ORIGINAL.

    Aceita o nome composto da C6 OU o par `(espécie, relação)` novo. As duas
    formas respondem o mesmo, porque são a mesma pergunta escrita de dois
    modos — e é isso que impede que a mudança de forma vire mudança de lei.
    """
    if isinstance(especie, (tuple, list)) and len(especie) == 2:
        kind, relacao = especie
    else:
        kind, relacao = ESPECIE_COMPOSTA.get(especie, (None, None))
    if kind in (None, TEXTO_DESCONHECIDO) or relacao != ORIGINAL:
        return False
    return kind in TEXT_KINDS


# ══════════════════════════════════════════════════════════════════════════
# A UNIDADE DE TEXTO — porque UM campo de texto nunca chegou para a casa
# ══════════════════════════════════════════════════════════════════════════
# Isto não é uma escolha de arquitectura elegante: é o que já estava escrito,
# à mão, em `coleta/comunicacao_coleta.py`, e que ninguém tinha nomeado:
#
#     «`TEXT` É A LEGENDA — o que o autor escreveu. Fica dito aqui porque, a
#      partir de 2026-09-10, existe um segundo texto no mesmo item: a FALA.
#      Somar os dois neste campo apagaria qual deles sustentou o que vier
#      depois. A fala entra em `TRANSCRIPT_TEXT`, e nunca aqui.»
#
# Uma observação com legenda E fala tem DOIS textos, e a casa já tinha aberto
# um segundo campo à mão para não os somar. Abrir um terceiro campo quando
# aparecer a tradução, e um quarto quando aparecer o ASR, dá um esquema em que
# cada espécie nova custa um campo novo a toda a gente que lê.
#
#     UM CAMPO POR ESPÉCIE É UM ESQUEMA QUE CRESCE COM O VOCABULÁRIO.
#     UMA LISTA DE UNIDADES COM ESPÉCIE DECLARADA NÃO CRESCE COM NADA.
#
# O campo vive na observação com o nome `TEXT_UNITS`, e o `TEXT` antigo fica
# exactamente onde estava e a dizer o que sempre disse (§ MIGRAÇÃO, abaixo).

#: O nome do campo na observação, escrito UMA vez. Quem o escreve e quem o lê
#: leem daqui — duas literais iguais em dois ficheiros divergem no dia em que
#: alguém mudar uma.
CAMPO_DAS_UNIDADES = 'TEXT_UNITS'

_HASH = re.compile(r'^[0-9a-f]{12,64}$', re.I)


def unidade_de_texto(*, texto, kind, kind_basis, relation=TEXTO_DESCONHECIDO,
                     language=None, unit_id=None, translated_from=None,
                     raw_observation_id=None, source_artifact=None,
                     derivation_method=TEXTO_DESCONHECIDO, tool=None, model=None):
    """Uma unidade de evidência textual, com espécie e linhagem. Nunca infere.

    ⚠️ `language` NÃO SE DEDUZ DO TEXTO, e esta função não tem por onde o
    fazer: ela recebe o que a fonte DECLAROU, e escreve `UNKNOWN` quando não
    recebeu nada. É a mesma lei que `social_envelope` já aplica ao campo
    `LANGUAGE` da observação — «idioma DECLARADO, nunca inferido do texto» — e
    é aqui que ela passa a valer também para cada texto lá dentro.

        LÍNGUA ITALIANA NÃO PROVA ITÁLIA, E TEXTO ITALIANO NÃO PROVA `it`.

    ⚠️ O `TEXT_UNIT_ID` É MORADA DENTRO DESTA OBSERVAÇÃO, E NÃO IDENTIDADE.
    Ele serve para uma tradução apontar para o seu original e para o recibo
    dizer qual unidade foi lida. Não é `DOCUMENT_ID`, não se lê de volta noutra
    corrida, e NÃO PODE SER UM SHA — `leis/retorno_da_coleta.py::_fabricado`
    já mediu porquê: 35 valores de `sha256` aparecem em observações DISTINTAS
    desta árvore, e uma identidade tirada do hash colaria duas em uma.

        SHA IDENTIFICA BYTES. NÃO IDENTIFICA DOCUMENTO, NEM UNIDADE DE TEXTO.
    """
    return {
        'TEXT_UNIT_ID': unit_id or '',
        'TEXT': texto,
        'TEXT_KIND': kind,
        'TEXT_KIND_BASIS': kind_basis,
        'TEXT_RELATION': relation,
        # Ausência declarada, nunca string vazia: `''` lê-se como «mediu-se e
        # não havia», e o que aqui há é «ninguém disse».
        'LANGUAGE': language or TEXTO_DESCONHECIDO,
        'TRANSLATED_FROM_TEXT_UNIT_ID': translated_from,
        'LINEAGE': {
            'RAW_OBSERVATION_ID': raw_observation_id or TEXTO_DESCONHECIDO,
            'SOURCE_ARTIFACT': source_artifact or TEXTO_DESCONHECIDO,
            'DERIVATION_METHOD': derivation_method,
            'TOOL': tool or TEXTO_DESCONHECIDO,
            'MODEL': model or TEXTO_DESCONHECIDO,
        },
    }


def conferir_unidade_de_texto(u):
    """As leis que UMA unidade de texto não pode quebrar. Devolve os motivos."""
    mal = []
    if not isinstance(u, dict):
        return ['a unidade de texto tem de ser uma ficha, e veio %s' % type(u).__name__]

    kind = u.get('TEXT_KIND')
    if kind not in TEXT_KINDS:
        mal.append('TEXT_KIND fora do vocabulario: %r. Ha: %s'
                   % (kind, ', '.join(TEXT_KINDS)))
    relacao = u.get('TEXT_RELATION')
    if relacao not in TEXT_RELATIONS:
        mal.append('TEXT_RELATION fora do vocabulario: %r. Ha: %s'
                   % (relacao, ', '.join(TEXT_RELATIONS)))
    base = u.get('TEXT_KIND_BASIS')
    if base not in BASES_DA_ESPECIE:
        # ⚠️ AQUI ESTAVA UM `elif 'INFER' in base`, E ELE NUNCA CORRIA.
        # `INFERRED_FROM_TEXT` nao esta em `BASES_DA_ESPECIE`, entao cai sempre
        # na linha de cima e a guarda por baixo era codigo morto com ar de lei.
        # A lei da C6 continua provada — mas onde ela e verdadeira: sobre a
        # LISTA (`test_nenhuma_base_da_especie_e_inferencia`), e nao sobre um
        # valor que a lista ja recusou.
        #
        #     UMA GUARDA QUE NUNCA CORRE NAO PROTEGE NADA,
        #     E ENSINA O PROXIMO LEITOR A CONFIAR NELA.
        mal.append('TEXT_KIND_BASIS fora do vocabulario: %r. Ha: %s'
                   % (base, ', '.join(BASES_DA_ESPECIE)))

    # ── UNKNOWN PERMANECE UNKNOWN, NOS DOIS SENTIDOS ───────────────────────
    # ⚠️ A PRIMEIRA VERSAO SO GUARDAVA UM LADO, E O RED TEAM ENTROU PELO OUTRO.
    # Ela exigia que `UNKNOWN` viesse com base `NOT_DECLARED`, e deixava passar
    # o contrario: uma unidade que ninguem declarou (`NOT_DECLARED`) a dizer-se
    # `AUTHOR_TEXT`. E esse e o ataque inteiro — a promocao silenciosa nao entra
    # pela porta de quem admite nao saber; entra pela de quem passa a afirmar.
    #
    #     ESPECIE CONHECIDA <-> ALGUEM A DECLAROU. As duas implicacoes, ou a
    #     que falta e por onde se passa.
    sabida = kind not in (None, TEXTO_DESCONHECIDO)
    declarada = base not in (None, NOT_DECLARED)
    if kind in TEXT_KINDS and base in BASES_DA_ESPECIE and sabida != declarada:
        mal.append(
            'TEXT_KIND = %r com base %r. Uma especie so e conhecida se alguem a '
            'declarou, e so e desconhecida se ninguem a declarou: %s'
            % (kind, base,
               'esta especie nao tem quem a declare' if sabida else
               'ha quem declare, e a especie ficou UNKNOWN'))

    # ── UMA TRADUCAO APONTA PARA O SEU ORIGINAL, OU NAO E UMA TRADUCAO ─────
    de_onde = u.get('TRANSLATED_FROM_TEXT_UNIT_ID')
    if relacao == TRANSLATED and not str(de_onde or '').strip():
        mal.append('TEXT_RELATION = TRANSLATED sem TRANSLATED_FROM_TEXT_UNIT_ID. '
                   'Uma traducao que nao diz de que original nasceu e '
                   'indistinguivel de um original noutra lingua')
    if relacao != TRANSLATED and str(de_onde or '').strip():
        mal.append('TRANSLATED_FROM_TEXT_UNIT_ID declarado numa unidade que diz '
                   'TEXT_RELATION = %r. Apontar para um original sem ser traducao '
                   'e uma contradicao, e o proximo leitor vai acreditar num dos '
                   'dois campos' % relacao)

    # ── A MORADA NAO PODE SER UM HASH ─────────────────────────────────────
    uid = str(u.get('TEXT_UNIT_ID') or '').strip()
    if not uid:
        mal.append('unidade de texto sem TEXT_UNIT_ID: sem morada, nenhuma '
                   'traducao lhe pode apontar e nenhum recibo a pode nomear')
    elif _HASH.match(uid):
        mal.append('TEXT_UNIT_ID com cara de hash (%r). SHA identifica bytes, e '
                   'nao unidade de texto: dois textos iguais em observacoes '
                   'diferentes sao dois textos' % uid)

    # ── A LINHAGEM ────────────────────────────────────────────────────────
    lin = u.get('LINEAGE')
    if not isinstance(lin, dict):
        mal.append('unidade de texto sem LINEAGE. De onde o texto nasceu nao e '
                   'opcional: sem isso ele e indistinguivel de texto escrito a mao')
    else:
        metodo = lin.get('DERIVATION_METHOD')
        if metodo not in METODOS_DE_DERIVACAO:
            mal.append('DERIVATION_METHOD fora do vocabulario: %r. Ha: %s'
                       % (metodo, ', '.join(METODOS_DE_DERIVACAO)))
        elif metodo in METODOS_DE_MAQUINA:
            if str(lin.get('TOOL') or '').strip() in ('', TEXTO_DESCONHECIDO):
                mal.append('%s produziu este texto e nao diz com que ferramenta. '
                           'Um texto de maquina sem maquina declarada nao se '
                           'confere nem se repete' % metodo)
        for campo in ('RAW_OBSERVATION_ID', 'SOURCE_ARTIFACT', 'TOOL', 'MODEL'):
            if campo not in lin:
                mal.append('LINEAGE sem %s. Ausente e «nao sei»; «%s» escrito e '
                           'uma medicao' % (campo, TEXTO_DESCONHECIDO))
    return mal


def conferir_unidades_de_texto(unidades):
    """As leis do CONJUNTO — as que uma unidade sozinha nao consegue quebrar."""
    mal = []
    if unidades in (None, ''):
        return mal
    if not isinstance(unidades, list):
        return ['%s tem de ser uma lista, mesmo vazia' % CAMPO_DAS_UNIDADES]

    por_id = {}
    for i, u in enumerate(unidades):
        for m in conferir_unidade_de_texto(u):
            mal.append('%s[%d]: %s' % (CAMPO_DAS_UNIDADES, i, m))
        if isinstance(u, dict):
            uid = str(u.get('TEXT_UNIT_ID') or '').strip()
            if uid and uid in por_id:
                mal.append('%s[%d]: TEXT_UNIT_ID %r repetido. Duas unidades com a '
                           'mesma morada fazem uma traducao apontar para as duas'
                           % (CAMPO_DAS_UNIDADES, i, uid))
            elif uid:
                por_id[uid] = u

    for i, u in enumerate(unidades):
        if not isinstance(u, dict):
            continue
        de_onde = str(u.get('TRANSLATED_FROM_TEXT_UNIT_ID') or '').strip()
        if not de_onde:
            continue
        if de_onde not in por_id:
            mal.append('%s[%d]: a traducao aponta para %r, que nao esta nesta '
                       'observacao. Um original fora do alcance de quem le e um '
                       'original que ninguem vai conferir'
                       % (CAMPO_DAS_UNIDADES, i, de_onde))
            continue
        origem = por_id[de_onde]
        if origem.get('TEXT_RELATION') == TRANSLATED:
            mal.append('%s[%d]: a traducao aponta para outra traducao (%r). O '
                       'original tem de ser um original — senao a cadeia perde o '
                       'ponto onde estavam as palavras de quem falou'
                       % (CAMPO_DAS_UNIDADES, i, de_onde))
        # ── UMA TRADUCAO PARA A MESMA LINGUA NAO E UMA TRADUCAO ───────────
        # Medido como ataque: copiar o original, chamar-lhe traducao e deixar a
        # lingua na mesma faz o par (original, traducao) mentir sem que nenhum
        # dos dois campos esteja, sozinho, errado.
        lo, lt = origem.get('LANGUAGE'), u.get('LANGUAGE')
        if (lo and lt and lo != TEXTO_DESCONHECIDO and lt != TEXTO_DESCONHECIDO
                and str(lo).lower() == str(lt).lower()):
            mal.append('%s[%d]: traducao declarada na MESMA lingua do original '
                       '(%s). Ou nao e traducao, ou a lingua esta errada'
                       % (CAMPO_DAS_UNIDADES, i, lo))
        if u.get('TEXT_KIND') != origem.get('TEXT_KIND'):
            # Traduzir nao muda a especie: a traducao de uma legenda continua a
            # ser uma legenda. Deixar mudar seria o caminho por onde um
            # transcript vira caption sem ninguem decidir isso.
            mal.append('%s[%d]: a traducao diz TEXT_KIND = %r e o original diz '
                       '%r. Traduzir muda a LINGUA, nunca a ESPECIE'
                       % (CAMPO_DAS_UNIDADES, i, u.get('TEXT_KIND'),
                          origem.get('TEXT_KIND')))
    return mal


# ══════════════════════════════════════════════════════════════════════════
# QUAL TEXTO É QUE QUEM JULGA LÊ — a regra, escrita uma vez e num sítio só
# ══════════════════════════════════════════════════════════════════════════
# A porta de admissão lê UM texto (`item['texto']`). A observação traz N. Entre
# as duas coisas há uma escolha, e uma escolha sem regra escrita é o defeito
# mais barato de cometer e o mais caro de encontrar:
#
#     PEGAR NO PRIMEIRO DA LISTA É UMA REGRA. É SÓ UMA REGRA QUE NINGUÉM
#     DECIDIU, QUE NINGUÉM CONSEGUE LER, E QUE MUDA QUANDO A ORDEM MUDA.
#
# E não é uma escolha inócua: `admissao._do_universo` casa o texto contra
# léxico ITALIANO e PORTUGUÊS. Está medido nesta árvore, no comentário dele:
# «contra o único texto italiano real desta árvore: **1 de 28** palavras
# aparecia lá». Dar-lhe a TRADUÇÃO INGLESA em vez do original italiano não faz
# a porta falhar — faz a porta responder OUTRA COISA, com ar de quem julgou.
#
#     ENTREGAR A TRADUÇÃO A QUEM MEDE O ORIGINAL NÃO PARTE NADA:
#     MUDA O VEREDITO E NÃO DEIXA MARCA.
#
# ── A ORDEM, E A RAZÃO DE CADA DEGRAU ──────────────────────────────────────
#  1 · ORIGINAL antes de TRADUZIDO, e TRADUZIDO antes de UNKNOWN.
#      Pela medição de cima. `UNKNOWN` fica atrás da tradução porque de uma
#      tradução sabe-se o que ela é; de um `UNKNOWN` não se sabe nada.
#  2 · Depois, por quantas máquinas há entre o autor e o texto:
#      o que ele escreveu · a legenda que a plataforma serviu · a fala que um
#      terceiro transcreveu · a fala que uma máquina ouviu · a página raspada ·
#      o documento extraído · o que ninguém declarou.
#      A casa já escrevia este degrau à mão, em `youtube_oficial._comentario`:
#      «O ORIGINAL vem primeiro. `textDisplay` traz HTML e links reescritos
#      pela plataforma; `textOriginal` é o que a pessoa digitou.»
#  3 · Empate só entre unidades iguais nos DOIS eixos — e aí desempata a
#      morada declarada (`TEXT_UNIT_ID`), que é estável e está escrita.
#      Não é «a primeira que apareceu»: é a que a observação nomeou primeiro.
ORDEM_DA_RELACAO = (ORIGINAL, TRANSLATED, TEXTO_DESCONHECIDO)
ORDEM_DA_ESPECIE = (AUTHOR_TEXT, NATIVE_CAPTION, TRANSCRIPT, ASR, PAGE_TEXT,
                    DOCUMENT_TEXT, TEXTO_DESCONHECIDO)

#: Porque nao havia nada para escolher. Sao dois silencios diferentes, e
#: chamar-lhes o mesmo faria «ninguem colheu texto» parecer «o texto veio vazio».
SEM_UNIDADES = 'SEM_UNIDADES_DE_TEXTO'
SEM_TEXTO_LEGIVEL = 'UNIDADES_SEM_TEXTO'


def _posicao(valor, ordem):
    try:
        return ordem.index(valor)
    except ValueError:
        # Fora do vocabulario vai para o fim, e nunca para a frente: um valor
        # que esta lei nao conhece nao pode ganhar a um que ela conhece.
        return len(ordem)


def escolher_para_leitura(unidades):
    """→ (unidade, porque). A unidade que quem julga pode ler, pela regra acima.

    Devolve `(None, motivo)` quando nao ha nada para ler — e o motivo distingue
    «nao havia unidades» de «havia unidades e nenhuma tinha texto».

        AUSENCIA NAO VIRA STRING VAZIA. Uma unidade vazia admitida como texto
        faria a porta dizer «tem conteudo legivel» sobre o nada.
    """
    if not unidades:
        return None, SEM_UNIDADES
    com_texto = [u for u in unidades
                 if isinstance(u, dict) and str(u.get('TEXT') or '').strip()]
    if not com_texto:
        return None, SEM_TEXTO_LEGIVEL
    escolhida = min(com_texto, key=lambda u: (
        _posicao(u.get('TEXT_RELATION'), ORDEM_DA_RELACAO),
        _posicao(u.get('TEXT_KIND'), ORDEM_DA_ESPECIE),
        unidades.index(u),
    ))
    return escolhida, (
        'escolhida por TEXT_RELATION=%s e TEXT_KIND=%s, pela ordem canonica de '
        '`regras/proveniencia.py`' % (escolhida.get('TEXT_RELATION'),
                                      escolhida.get('TEXT_KIND')))


# ── O QUE A ESCOLHA ENTREGA A QUEM JULGA ───────────────────────────────────
#     A ESPECIE VIAJA COM O VALOR, OU O VALOR CHEGA SOZINHO E MENTE.
#
# Quem le `texto` passa a poder perguntar de que especie ele e sem voltar atras
# — e a inteligencia, que faz essa pergunta primeiro que todas («o que
# sustentou isto: o que a pessoa escreveu, ou o que a maquina ouviu?»), deixa de
# ter de adivinhar.
#
# ⚠️ `texto_especie` PODE SER `UNKNOWN`, E ISSO NAO E UM BURACO.
# Promover um `UNKNOWN` a `AUTHOR_TEXT` porque «e um post, deve ser do autor»
# seria exactamente a inferencia que `BASES_DA_ESPECIE` proibe — so que feita
# no fim da estrada, onde ja ninguem a ve.
CAMPOS_DA_ESCOLHA = ('texto', 'texto_especie', 'texto_relacao', 'texto_lingua',
                     'texto_unidade', 'texto_escolha_porque')


# ── O ENVELOPE ANTIGO, QUE SÓ TEM `TEXT` ───────────────────────────────────
# Há envelopes escritos antes desta lei, e há uma linha inteira (o SCRAP) cujo
# mapeador ainda não passa `TEXT_UNITS` para a unidade de colheita. Os dois
# precisam de uma ponte, e a ponte tem de ser segura por construção:
#
#     UM `TEXT` SEM ESPÉCIE DECLARADA VIRA UMA UNIDADE `UNKNOWN`.
#     NUNCA UMA UNIDADE `AUTHOR_TEXT` PORQUE «É UM POST, DEVE SER DO AUTOR».
#
# É a mesma forma de `leis/retorno_da_coleta.py::envelope_do_legado`: o legado
# pode declarar o que é inofensivo estar errado, e não pode declarar o que não
# é. Ali, o legado só declara SUPORTE. Aqui, só declara `UNKNOWN` — porque uma
# espécie errada não se conserta a jusante: ela vira o que o próximo leitor
# achar que ela é.
#
# ⚠️ E A LÍNGUA DO ENVELOPE NÃO DESCE PARA A UNIDADE.
# `envelope['LANGUAGE']` é o idioma da PUBLICAÇÃO. Colá-lo a um texto de espécie
# desconhecida seria afirmar, sobre um texto que não sabemos o que é, que está
# na língua de outra coisa. `UNKNOWN` é mais barato que errado.
def unidades_do_envelope(envelope):
    """→ as unidades de texto de um envelope social. Uma função, um dono.

    Quem escreve o envelope já lhes deu espécie (`coleta/social_envelope.py`);
    esta função é para quem o LÊ — o mapeador da colheita, a prova, e o que
    vier. Existir uma só evita o defeito que `PARA_A_PORTA` veio curar: a mesma
    travessia escrita à mão em dois sítios, com subconjuntos diferentes.
    """
    envelope = envelope or {}
    unidades = envelope.get(CAMPO_DAS_UNIDADES)
    if unidades is not None:
        return list(unidades)
    texto = envelope.get('TEXT')
    if texto is None or not str(texto).strip():
        return []
    return [unidade_de_texto(
        texto=texto, kind=TEXTO_DESCONHECIDO, kind_basis=NOT_DECLARED,
        relation=TEXTO_DESCONHECIDO, unit_id='TU-1',
        source_artifact=envelope.get('URL'),
        derivation_method=TEXTO_DESCONHECIDO)]


def texto_para_quem_julga(unidades):
    """→ a ficha, na lingua de quem julga, do texto escolhido. `{}` se nao ha.

    ⚠️ DEVOLVE `{}` E NAO `{'texto': ''}` QUANDO NAO HA TEXTO.
    `coleta/ingresso.py::para_a_porta` ja tem esta lei escrita — «um campo que o
    coletor nao deu nao aparece do lado de la como string vazia» — e
    `admissao._legivel` conta com ela: com o campo AUSENTE responde `NAO_SEI`
    («nao consegui ver»), que e a resposta certa; com `''` responderia o mesmo
    por acaso, e no dia em que alguem mudar o teste de `not t.strip()` para
    `'texto' in item` a casa passaria a admitir o vazio.
    """
    escolhida, porque = escolher_para_leitura(unidades)
    if escolhida is None:
        return {}
    return {
        'texto': escolhida.get('TEXT'),
        'texto_especie': escolhida.get('TEXT_KIND'),
        'texto_relacao': escolhida.get('TEXT_RELATION'),
        'texto_lingua': escolhida.get('LANGUAGE'),
        'texto_unidade': escolhida.get('TEXT_UNIT_ID'),
        'texto_escolha_porque': porque,
    }



# ------------------------------------------------- inventário do bruto de rota paga
# Por que este bloco existe: até 2026-08-29 duas coisas inventariavam o MESMO diretório —
# `POLITICA-RAW-ROTA-PAGA.json` (lista digitada) e o DATA CLOCK (lista derivada). Elas
# divergiram em silêncio: um bruto novo entrou, o relógio o pegou, a política não. Um
# inventário digitado de uma população que muda é o mesmo defeito de sempre, agora em JSON.
#
# A partir daqui o DONO da população é este módulo, e o inventário é DERIVADO do diretório.


# ── UMA COPIA ANTIGA DESTE VOCABULARIO VIVIA AQUI, E FOI RETIRADA ────────
# A integracao do SCRAP trouxe, APENSO AO FIM DESTE FICHEIRO, o vocabulario
# da especie do texto tal como ele era na SCRAP-C6: as quatro especies, as
# tres bases, `SERVEM_PARA_ORIGINAL`, `especie_declarada` e
# `serve_para_original`. Tudo isso ja vive em cima, na forma que a COL-E7-01
# fechou — a mesma lei, mais larga.
#
# O `git merge` juntou os dois SEM UM UNICO CONFLITO, porque um apenso ao fim
# de um ficheiro nao colide com nada. E em Python a SEGUNDA definicao ganha:
# `BASES_DA_ESPECIE` passou a ser a de tres valores, e `DECLARED_BY_ROUTE`
# — que a E7 acrescentou — deixou de existir para quem conferisse.
#
#     AUTO-MERGE SEM CONFLITO NAO E MERGE CORRECTO.
#     DUAS DEFINICOES DO MESMO NOME NAO SAO CONFLITO PARA O GIT,
#     E SAO CONFLITO PARA A CASA.
#
# Cinco casos do contrato do texto reprovaram, e foi assim que isto apareceu.
# Nada se perdeu: cada simbolo do bloco antigo tem par mais completo acima.


RAW_PAID_REL = 'data/samples/raw-paid'

# Duas populações vivem no mesmo diretório e NÃO têm a mesma obrigação. Sem distinguir,
# um bruto operacional órfão se esconde atrás de um artefato de teste — e foi assim que
# GATE-TEST-...-b passou despercebido.
PRODUCTION_RAW = 'PRODUCTION_RAW'
GATE_TEST_RAW = 'GATE_TEST_RAW'
CLASSES_RAW = [PRODUCTION_RAW, GATE_TEST_RAW]

# Convenção de nome aplicada pelo coletor nas execuções de verificação do portão.
# Não é heurística sobre conteúdo: é declaração, e este módulo é o dono de interpretá-la.
PREFIXO_GATE_TEST = 'GATE-TEST-'

MOTIVO_GATE_TEST = (
    'artefato de verificação do portão do coletor, não coleta. Não produz registro '
    'analítico publicado, por isso não há execução de produção que o cite. '
    'EXCLUDED_WITH_REASON — nunca ausência silenciosa.')


def classificar_raw(caminho):
    """PRODUCTION_RAW ou GATE_TEST_RAW."""
    base = os.path.basename(str(caminho))
    return GATE_TEST_RAW if base.startswith(PREFIXO_GATE_TEST) else PRODUCTION_RAW


def arquivos_raw_pagos(root=ROOT):
    """O conjunto REAL em disco. O denominador nunca é uma lista digitada."""
    d = os.path.join(root, RAW_PAID_REL)
    if not os.path.isdir(d):
        return []
    return sorted('%s/%s' % (RAW_PAID_REL, n)
                  for n in os.listdir(d) if not n.startswith('.'))


def _caminhos_declarados(run):
    """RAW_EVIDENCE_PATH normalizado: aceita string ou lista, ignora NOT_PRESERVED."""
    p = run.get('RAW_EVIDENCE_PATH')
    for c in (p if isinstance(p, list) else [p]):
        c = str(c).split(' (')[0].strip()
        if c and c != NOT_PRESERVED:
            yield c


def runs_por_bruto(runs=None):
    """A direção INVERSA da cadeia: ARQUIVO BRUTO -> execuções que o declaram.

    `CONTENT -> RUN_ID -> MANIFEST` já existia. Faltava esta: um arquivo bruto que
    nenhuma execução reivindica é evidência sem procedência, e não pode ficar em silêncio.
    """
    runs = carregar() if runs is None else runs
    idx = {}
    for rid, r in sorted(runs.items()):
        for c in _caminhos_declarados(r):
            idx.setdefault(c, []).append(rid)
    return idx


def _itens(path):
    """Quantos itens o bruto carrega. Derivado do arquivo, não declarado."""
    import gzip
    try:
        with gzip.open(path, 'rt', encoding='utf-8') as f:
            o = json.load(f)
        return len(o) if isinstance(o, (list, dict)) else NAO_SEI
    except (OSError, ValueError):
        return NAO_SEI


def inventario_raw_pago(root=ROOT, runs=None):
    """Reconciliação executável entre DISCO, MANIFESTO e CLASSE.

    Cada arquivo do diretório sai daqui com tamanho e contagem DERIVADOS, a classe
    declarada, e as execuções que o citam — ou o motivo explícito de não ter nenhuma.
    """
    idx = runs_por_bruto(runs)
    inv = []
    for rel in arquivos_raw_pagos(root):
        classe = classificar_raw(rel)
        citado = sorted(idx.get(rel, []))
        item = {'FILE': rel, 'CLASS': classe,
                'GZ_BYTES': os.path.getsize(os.path.join(root, rel)),
                'ITEMS': _itens(os.path.join(root, rel)),
                'RUNS': citado}
        if not citado:
            item['EXCLUDED_WITH_REASON'] = (
                MOTIVO_GATE_TEST if classe == GATE_TEST_RAW else None)
        inv.append(item)
    return inv


def brutos_orfaos(root=ROOT, runs=None):
    """PRODUCTION_RAW que nenhuma execução reivindica. Tem de ser sempre vazio."""
    return [i['FILE'] for i in inventario_raw_pago(root, runs)
            if i['CLASS'] == PRODUCTION_RAW and not i['RUNS']]


def brutos_declarados_e_ausentes(root=ROOT, runs=None):
    """O inverso: execução que diz PRESERVED apontando para arquivo que não existe."""
    runs = carregar() if runs is None else runs
    faltando = []
    for rid, r in sorted(runs.items()):
        if r.get('RAW_EVIDENCE_STATE') != 'PRESERVED':
            continue
        for c in _caminhos_declarados(r):
            if not os.path.exists(os.path.join(root, c)):
                faltando.append((rid, c))
    return faltando


POLITICA = os.path.join(ROOT, 'data', 'samples', 'POLITICA-RAW-ROTA-PAGA.json')

# As chaves que a política NÃO digita mais: saem do diretório real a cada sincronização.
CHAVES_DERIVADAS = ('ARQUIVOS', 'TAMANHO_ATUAL_BYTES', 'TOTAL_POR_CLASSE',
                    'BRUTOS_ORFAOS', 'DERIVADO_POR')


def politica_derivada(root=ROOT, runs=None):
    """O bloco derivado da política. É esta função que a política publica."""
    inv = inventario_raw_pago(root, runs)
    por_classe = {}
    for i in inv:
        c = por_classe.setdefault(i['CLASS'], {'ARQUIVOS': 0, 'GZ_BYTES': 0})
        c['ARQUIVOS'] += 1
        c['GZ_BYTES'] += i['GZ_BYTES']
    return {
        'ARQUIVOS': inv,
        'TAMANHO_ATUAL_BYTES': sum(i['GZ_BYTES'] for i in inv),
        'TOTAL_POR_CLASSE': por_classe,
        'BRUTOS_ORFAOS': brutos_orfaos(root, runs),
        'DERIVADO_POR': (
            'regras/proveniencia.py --sync-politica. O inventário e os tamanhos são '
            'DERIVADOS do diretório real; nenhum é digitado. Há teste que reprova se a '
            'política divergir do disco.'),
    }


def sincronizar_politica(root=ROOT):
    """Reescreve só o bloco derivado, preservando a prosa da política."""
    with open(POLITICA, encoding='utf-8') as f:
        d = json.load(f)
    antes = {k: d.get(k) for k in CHAVES_DERIVADAS}
    d.update(politica_derivada(root))
    with open(POLITICA, 'w', encoding='utf-8') as f:
        json.dump(d, f, ensure_ascii=False, indent=1)
    return [k for k in CHAVES_DERIVADAS if antes.get(k) != d.get(k)]


if __name__ == '__main__':
    import sys
    runs = carregar()
    print('execuções no manifesto:', len(runs))
    for rid, r in sorted(runs.items()):
        print('  %-34s %-9s %-8s raw=%s' % (rid, r['PLATFORM'], r['STATUS'],
                                            r['RAW_EVIDENCE_STATE']))
    if '--campos' in sys.argv:
        for c in CAMPOS_RUN:
            print(' ', c)
    if '--raw' in sys.argv:
        print()
        for i in inventario_raw_pago():
            print('  %-52s %-15s %9s bytes  itens=%-5s %s'
                  % (i['FILE'].split('/')[-1], i['CLASS'], format(i['GZ_BYTES'], ','),
                     i['ITEMS'], ','.join(i['RUNS']) or 'EXCLUDED_WITH_REASON'))
        print('\n  orfaos de producao:', brutos_orfaos() or 'nenhum')
    if '--sync-politica' in sys.argv:
        mud = sincronizar_politica()
        print('politica sincronizada; chaves alteradas:', mud or 'nenhuma')
