#!/usr/bin/env python3
"""
UNIVERSO DE CONTAS DO CONCORRENTE — o quadro fechado ANTES de qualquer coleta.

    py regras/comunicacao_universo.py

O QUE ESTE ARQUIVO FAZ, E O QUE ELE DELIBERADAMENTE NÃO FAZ
------------------------------------------------------------
Ele desenha o TABULEIRO: quais `COMPANY x COUNTRY x PLATFORM` a missão vai tentar
resolver. Cada casa nasce em `NOT_KNOWN` e **nenhuma** nasce em `CANDIDATE`.

    TABULEIRO != CONTA. CASA ABERTA != CONTA ENCONTRADA.

Quem promove uma casa é `comunicacao_identidade.py`, sobre evidência gravada. Este
arquivo não busca, não adivinha handle, não escreve URL de perfil. Se ele escrevesse
`instagram.com/bayer_es` "porque é o padrão", o erro nasceria com cara de dado.

POR QUE ESTES CINCO CONCORRENTES, E NÃO UMA LISTA DE GOSTO
------------------------------------------------------------
A missão manda começar pelos concorrentes JÁ relevantes nas outras camadas. A regra
que escolhe não é minha: é o `COMPETITOR-CROSSWALK`, que já resolveu identidade de
marca contra registro espanhol e publicou `PROVED_POR_GRUPO`. Os grupos com par
PROVED lá são os que já carregam ID no Foresight — e §10 manda reusar ID existente.

    BAYER 47 · CORTEVA 46 · SYNGENTA 39 · BASF 39 · NUFARM 24 · UPL 14

O primeiro lote leva os CINCO maiores por pares provados. NUFARM, FMC, Certis
Belchim, Albaugh e Seipasa ficam no universo declarado como `FORA_DO_PRIMEIRO_LOTE`
— não como esquecidos. §17 manda medir rendimento antes de ampliar, e uma lista que
não distingue "não tentei" de "tentei e não achei" apaga exatamente essa medição.

O ÂNCORA É O SITE, NUNCA O NOME
--------------------------------
Para cada `COMPANY x COUNTRY` a missão precisa de um ÂNCORA: o site oficial LOCAL.
Ele também nasce `NOT_KNOWN`. O caminho de prova aceito é um só, e nos dois sentidos:

    site oficial local  --link declarado-->  conta social
    conta social        --link declarado-->  site oficial local

`NAME_SIMILARITY != ACCOUNT_PROOF` é a lei desta missão, e ela existe porque a casa
já pagou por quebrá-la: a busca por nome no LinkedIn devolveu, para "Pasquale De
Vita", o presidente da Unione Petrolifera. Com EMPRESA o risco é outro e pior — há
conta global, conta regional, conta de produto e conta de RH, todas com o nome certo
e todas erradas para a pergunta "o que a Bayer fala na França".

Por isso `ACCOUNT_SCOPE` é campo de primeira classe, e `LOCAL_COUNTRY` nunca é o
padrão: uma conta que o site global lista sem dizer o país sai `GLOBAL`, e conta
global não vira atividade francesa.
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SAMPLES = os.path.join(ROOT, 'data', 'samples')
SAIDA = os.path.join(SAMPLES, 'COMPETITOR-PUBLIC-COMM')

DATASET_OWNER = 'COMPETITOR_PUBLIC_COMMUNICATION_EAME'
NAO_SEI = 'NOT_KNOWN'

PAISES = ['ES', 'IT', 'FR']

# Plataformas do §3. A ordem é a ordem de tentativa, e ela não é estética: LinkedIn e
# YouTube publicam página de empresa com link de site na própria página — o que fecha o
# caminho de prova em UMA leitura. Instagram e Facebook muitas vezes só têm o link no
# sentido site->conta, e por isso dependem do âncora ter sido resolvido antes.
PLATAFORMAS = ['LINKEDIN', 'YOUTUBE', 'INSTAGRAM', 'FACEBOOK']

# Grupos com par PROVED no COMPETITOR-CROSSWALK, em ordem de pares provados. A contagem
# é lida do artefato em tempo de execução — não copiada — para que uma rodada nova do
# crosswalk mude esta lista sozinha em vez de deixar um número velho aqui dentro.
CROSSWALK = os.path.join(SAMPLES, 'COMPETITOR-CROSSWALK.json')
TAMANHO_DO_PRIMEIRO_LOTE = 5

# Concorrentes que a MISSÃO nomeia. Esta lista é o universo declarado; quem fica de fora
# do primeiro lote é CALCULADO contra ela, nunca escrito à mão.
#
# A primeira versão deste arquivo escrevia a lista de fora à mão — e publicou NUFARM nas
# DUAS listas ao mesmo tempo, porque o empate BASF/SYNGENTA em 39 pares empurrou a NUFARM
# para dentro do corte e a lista fixa não soube. Um relatório que diz "não tentei" sobre
# uma empresa que ele mesmo mandou coletar é pior que um relatório sem a lista.
NOMEADOS_PELA_MISSAO = ['BAYER', 'SYNGENTA', 'BASF', 'CORTEVA', 'FMC', 'UPL',
                        'NUFARM', 'CERTIS BELCHIM', 'ALBAUGH', 'SEIPASA']

# Estados de conta do §0. Lista fechada: um estado inventado no meio da rodada é a
# forma mais silenciosa de afrouxar o portão.
ESTADOS = ['CANDIDATE', 'PARTIAL', 'PROVED', 'REJECTED', 'NOT_KNOWN']

# Escopos do §1. `LOCAL_COUNTRY` é o único que autoriza ler a conta como atividade
# daquele país — e ele precisa ser provado, nunca assumido.
ESCOPOS = ['LOCAL_COUNTRY', 'REGIONAL_EUROPE', 'GLOBAL', 'PRODUCT', 'OTHER', NAO_SEI]


class CrosswalkIndisponivel(RuntimeError):
    """O COMPETITOR-CROSSWALK não está em condições de ser lido. NADA foi derivado.

    A hierarquia é fechada de propósito, e cada folha é uma causa distinta:

        CrosswalkAusente    o ficheiro não existe no caminho dado
        CrosswalkIlegivel   existe e não é o crosswalk (JSON partido, forma errada,
                            PROVED_POR_GRUPO em falta, vazio ou com contagens que
                            não são inteiros)

    POR QUE ISTO LEVANTA EM VEZ DE DEVOLVER `[]`
    ---------------------------------------------
    Até 2026-09-17 `grupos_do_crosswalk()` devolvia lista vazia quando o ficheiro
    faltava, e `montar()` seguia em frente: lote vazio, 0 âncoras, 0 casas — e um
    JSON com `SOURCE_ID`, `DATASET_OWNER` e `EVIDENCE_CLASS` iguais aos do universo
    verdadeiro. Corrido pela linha de comando, ele ESCREVIA esse vazio por cima do
    `UNIVERSO-CONTAS-V1.json` versionado. E o crosswalk NUNCA esteve no Git
    (know-how §139): em qualquer clone, «correr o script» era «apagar o universo».

        UM DERIVADO SEM FONTE NÃO É UM DERIVADO VAZIO. É UM NÃO-DERIVADO.
        E ELE NÃO ESCREVE: NÃO CRIA PASTA, NÃO CRIA FICHEIRO, NÃO TOCA NO QUE LÁ ESTÁ.

    Este ficheiro NÃO reconstrói o crosswalk, NÃO guarda uma cópia das contagens e
    NÃO inventa grupos: sem a fonte, a resposta é uma recusa com a causa escrita.
    """


class CrosswalkAusente(CrosswalkIndisponivel):
    pass


class CrosswalkIlegivel(CrosswalkIndisponivel):
    pass


def grupos_do_crosswalk(caminho=CROSSWALK):
    """→ [(GRUPO, PARES_PROVED)] em ordem decrescente. Lê, não copia.

    Levanta `CrosswalkAusente` se o ficheiro não existe e `CrosswalkIlegivel` se
    existe mas não tem a forma do crosswalk. Nunca devolve lista vazia: um crosswalk
    sem nenhum par PROVED não é um tabuleiro — é uma fonte que não responde.
    """
    if not os.path.isfile(caminho):
        raise CrosswalkAusente(
            'COMPETITOR-CROSSWALK não encontrado em %s. O universo é DERIVADO dele e '
            'não se monta sem ele: nada foi derivado e nada foi escrito. Este ficheiro '
            'nunca esteve no Git — obtenha-o da rodada do crosswalk, ou passe outro '
            'caminho em `montar(caminho=...)`.' % caminho)
    try:
        with open(caminho, encoding='utf-8') as f:
            d = json.load(f)
    except (OSError, ValueError) as e:
        raise CrosswalkIlegivel(
            '%s existe e não é JSON legível (%s). Nada foi derivado.' % (caminho, e)) from e
    if not isinstance(d, dict):
        raise CrosswalkIlegivel(
            '%s tem JSON válido mas não é um objecto (é %s). Nada foi derivado.'
            % (caminho, type(d).__name__))
    por_grupo = d.get('PROVED_POR_GRUPO')
    if not isinstance(por_grupo, dict) or not por_grupo:
        raise CrosswalkIlegivel(
            '%s não traz PROVED_POR_GRUPO com pelo menos um grupo (veio %r). Sem pares '
            'PROVED não há critério de selecção, e um lote vazio não é um lote. Nada '
            'foi derivado.' % (caminho, por_grupo))
    for grupo, pares in por_grupo.items():
        if not isinstance(grupo, str) or not grupo.strip() or isinstance(pares, bool)                 or not isinstance(pares, int) or pares < 0:
            raise CrosswalkIlegivel(
                '%s: PROVED_POR_GRUPO[%r] = %r não é uma contagem inteira de pares. '
                'Nada foi derivado.' % (caminho, grupo, pares))
    if not any(pares > 0 for pares in por_grupo.values()):
        # O red team de 2026-09-17 provou que um crosswalk com todos os grupos a ZERO
        # passava e montava um lote «dos cinco maiores» entre iguais a nada. Sem um par
        # PROVED sequer não há critério de selecção — a fonte não respondeu.
        raise CrosswalkIlegivel(
            '%s: nenhum grupo em PROVED_POR_GRUPO tem um par PROVED (todos a zero). Sem '
            'pares PROVED não há critério de selecção. Nada foi derivado.' % caminho)
    return sorted(por_grupo.items(), key=lambda kv: (-kv[1], kv[0]))


def montar(caminho=CROSSWALK):
    ordenados = grupos_do_crosswalk(caminho)
    lote = [g for g, _ in ordenados[:TAMANHO_DO_PRIMEIRO_LOTE]]
    pares = dict(ordenados)
    # Universo declarado = quem a missão nomeia MAIS quem o crosswalk já provou. Fora do
    # lote é o complemento, calculado. Nenhum nome pode estar nos dois lados.
    universo = list(dict.fromkeys(NOMEADOS_PELA_MISSAO + [g for g, _ in ordenados]))
    fora = [g for g in universo if g not in lote]

    ancoras, casas = [], []
    for empresa in lote:
        for pais in PAISES:
            ancoras.append({
                'COMPANY': empresa,
                'COUNTRY': pais,
                'ANCHOR_SITE_URL': NAO_SEI,
                'ANCHOR_SITE_STATE': NAO_SEI,
                'ANCHOR_SITE_EVIDENCE': (
                    'nenhuma leitura feita. O âncora é o site oficial LOCAL e ele é '
                    'resolvido por leitura, não por padrão de domínio.'),
            })
            for plataforma in PLATAFORMAS:
                casas.append({
                    'ACCOUNT_CELL_ID': '%s|%s|%s' % (empresa, pais, plataforma),
                    'COMPANY': empresa,
                    'COMPANY_PROVED_BRAND_PAIRS': pares.get(empresa),
                    'COUNTRY': pais,
                    'PLATFORM': plataforma,
                    'ACCOUNT_URL': NAO_SEI,
                    'ACCOUNT_ID': NAO_SEI,
                    'ACCOUNT_NAME': NAO_SEI,
                    'ACCOUNT_SCOPE': NAO_SEI,
                    'ACCOUNT_IDENTITY_STATE': NAO_SEI,
                    'ACCOUNT_IDENTITY_EVIDENCE': (
                        'casa aberta no tabuleiro. Nenhuma busca executada.'),
                    'COLLECTION_AUTHORIZED': 'NO',
                })

    return {
        'SOURCE_ID': 'COMPETITOR-PUBLIC-COMM/UNIVERSO-CONTAS-V1',
        'DATASET_OWNER': DATASET_OWNER,
        'source': 'derivado de COMPETITOR-CROSSWALK — nenhuma coleta executada',
        'SOURCE_LOCATION': 'derivado',
        'FACT_LOCATION': 'n/a — descreve o tabuleiro, não o mundo',
        'ORIGINAL_LANGUAGE': 'pt',
        'EVIDENCE_CLASS': 'DERIVED_SCOPE',
        'APIFY_RUNS': 0,
        'COST_USD': 0,
        'O_QUE_ISTO_E': ('o quadro fechado de COMPANY x COUNTRY x PLATFORM que a missão '
                         'vai TENTAR resolver, antes de qualquer coleta'),
        'O_QUE_ISTO_NAO_E': [
            'não é uma lista de contas encontradas',
            'não é uma lista de contas oficiais',
            'nenhuma casa aqui autoriza coleta — COLLECTION_AUTHORIZED nasce NO',
        ],
        'REGRA_DE_SELECAO': (
            'os %d grupos com mais pares de marca PROVED no COMPETITOR-CROSSWALK. '
            'Critério herdado de outra camada, não escolhido aqui.'
            % TAMANHO_DO_PRIMEIRO_LOTE),
        'COMPANY_UNIVERSE_DECLARED': universo,
        'FIRST_BATCH_COMPANIES': lote,
        'OUT_OF_FIRST_BATCH': fora,
        'OUT_OF_FIRST_BATCH_MEANS': (
            'NÃO TENTADO nesta rodada. Não é "não achei conta" e não é "não comunica".'),
        'COUNTRIES': PAISES,
        'PLATFORMS': PLATAFORMAS,
        'IDENTITY_STATES': ESTADOS,
        'ACCOUNT_SCOPES': ESCOPOS,
        'PROMOTION_RULE': (
            'só PROVED entra na coleta. PROVED exige caminho declarado em dois sentidos '
            'independentes: site oficial local -> conta, ou conta -> site oficial local. '
            'NAME_SIMILARITY != ACCOUNT_PROOF.'),
        'ANCHOR_CELLS': len(ancoras),
        'ACCOUNT_CELLS': len(casas),
        'ANCHORS': ancoras,
        'CELLS': casas,
    }


def main(caminho=None, destino=None):
    """A porta da linha de comando. Monta PRIMEIRO; so escreve se montou.

    Sem crosswalk (ou com um ilegivel) imprime a causa e sai com codigo 2 — e
    NAO cria a pasta de saida, NAO cria o ficheiro e NAO toca no que ja la esta.
    Os caminhos leem-se dos nomes do modulo no momento da chamada, para que uma
    prova possa aponta-los a uma casa de mentira sem mexer na de verdade.

    A escrita fica AQUI, na forma `destino = os.path.join(SAIDA, 'X.json')` →
    `open(destino, 'w')`, porque e essa a forma que o scanner do System Map
    segue (`escritas_por_constante`): e assim que o mapa sabe que esta peca
    produz o universo. Esconder a escrita atras de um temporario apagaria a seta
    mais importante do cartao — medido em 2026-09-17, «o que sai: NAO SEI».
    """
    caminho = caminho or CROSSWALK
    try:
        corpo = montar(caminho)
    except CrosswalkIndisponivel as e:
        print('UNIVERSO = NAO_DERIVADO — %s: %s' % (type(e).__name__, e), file=sys.stderr)
        return 2
    destino = destino or os.path.join(SAIDA, 'UNIVERSO-CONTAS-V1.json')
    os.makedirs(os.path.dirname(destino) or '.', exist_ok=True)
    with open(destino, 'w', encoding='utf-8') as f:
        json.dump(corpo, f, ensure_ascii=False, indent=1)
    print('empresas do primeiro lote: %s' % ', '.join(corpo['FIRST_BATCH_COMPANIES']))
    print('fora do primeiro lote:     %s' % ', '.join(corpo['OUT_OF_FIRST_BATCH']))
    print('âncoras a resolver:  %d (empresa x país)' % corpo['ANCHOR_CELLS'])
    print('casas a resolver:    %d (empresa x país x plataforma)' % corpo['ACCOUNT_CELLS'])
    print('contas autorizadas a coletar: 0 — nenhuma casa foi resolvida ainda')
    return 0


if __name__ == '__main__':
    sys.exit(main())
