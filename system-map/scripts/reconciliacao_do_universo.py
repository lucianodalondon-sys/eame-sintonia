#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""A RECONCILIACAO DO UNIVERSO DO MAPA — de onde vem cada numero publicado.

    py system-map/scripts/reconciliacao_do_universo.py
    py system-map/scripts/reconciliacao_do_universo.py --sem-topologia

POR QUE ISTO EXISTE
-------------------
O mapa publica varios numeros sobre «os cartoes da coleta», e cada um deles
estava certo. O defeito nao era um numero errado: era nao haver NENHUM sitio
onde os numeros se encontrassem.

    UMA FERRAMENTA DE OBSERVABILIDADE NAO E COERENTE PORQUE CADA CENSO
    INDIVIDUAL ESTA CERTO. ELA E COERENTE QUANDO OS CENSOS CONSEGUEM
    RECONCILIAR OS PROPRIOS UNIVERSOS.

Medido nesta arvore, tres numeros que toda a gente chamava «os cartoes da
coleta» e que contam coisas diferentes:

    65   a faixa visual   familia F-COLETA + F-ESPERA
    48   o pente fino     TERRITORIO dentro de uma tupla fixa de nove zonas
    111  a topologia      a mesma familia MAIS tudo o que lhe toca por aresta

Nenhum deles e falso. Todos respondem a perguntas diferentes com a mesma
palavra — e uma palavra que significa tres universos nao significa nenhum.

O QUE ESTE FICHEIRO FAZ, E O QUE ELE NAO FAZ
--------------------------------------------
FAZ: declara cada universo com regra de entrada, regra de saida, pai, cabeca
medida e membros; enumera CARTAO A CARTAO em que lente cada um entra; e fecha
a aritmetica — todo cartao do universo visual esta DENTRO do pente fino ou na
lista de excluidos, com motivo. Nenhum cartao desaparece em silencio.

NAO FAZ: nao decide arquitetura, nao move cartao de familia, nao cria aresta,
nao alarga filtro nenhum. Ele OBSERVA as lentes que ja existem e obriga-as a
responder umas pelas outras.

    O SYSTEM MAP OBSERVA. O SYSTEM MAP NAO INVENTA A ARQUITETURA.

CADA LENTE CONTINUA A SER DONA DE SI
------------------------------------
A regra do pente fino e importada de `pente_fino_da_coleta.py`; a da topologia
de `censo_da_topologia.py`; a contagem visual e lida de `state.generated.json`,
que e quem a calcula. Nenhuma regra e reescrita aqui — copiar a tupla das zonas
para dentro deste ficheiro criaria um SEGUNDO dono dela, e dois donos divergem
no dia em que um deles muda.

A CABECA MEDIDA, E POR QUE UM SHA DE COMMIT NAO SERVE
-----------------------------------------------------
`pente-fino.generated.json` carimba `PROVENANCE.HEAD` com o SHA do commit — e
MEDIDO NESTE REPOSITORIO: em todos os commits que o tocam, o SHA carimbado e o
do commit ANTERIOR. Nao ha erro nenhum nisso; e impossivel por construcao, um
ficheiro commitado nunca pode nomear o commit que o contem. `CADEIA-DO-MAPA.json`
ja tinha escrito essa licao para o mapa e resolveu-a com a IMPRESSAO DA ARVORE,
que mede FONTES e nao commits.

    A PERGUNTA NAO E «QUE COMMIT?». E «QUE ARVORE?».

Por isso este ficheiro trata um carimbo de commit como NAO VERIFICAVEL e compara
frescura pela impressao da arvore — a unica prova que nao envelhece por desenho.

SAIDA: data/derivados/SYSTEM-MAP-UNIVERSE-RECONCILIATION-V1.json
       O JSON e o dono das contagens. Markdown nenhum as reescreve.
"""

import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parents[1]
DADOS = RAIZ / "system-map" / "data"
SAIDA = RAIZ / "data" / "derivados" / "SYSTEM-MAP-UNIVERSE-RECONCILIATION-V1.json"

sys.path.insert(0, str(AQUI))
import impressao_da_arvore as IMPRESSAO          # noqa: E402
from pente_fino_da_coleta import ZONAS as PENTE_ZONAS   # noqa: E402
from censo_da_topologia import LADO_DA_COLETA           # noqa: E402

NAO_SEI = "NAO SEI"

# ─────────────────────────────────────────────────────────────────────────
# A ESPECIE DE CADA SUPERFICIE DE CONTAGEM — G0 do contrato de confianca.
#
# «65 cartoes» nao e auditavel. `65 SYSTEM_MAP_VISUAL_CARD` e.
#
#     ENTITY_SPECIES RESPONDE A UMA PERGUNTA SO:
#     O QUE E CADA MEMBRO DESTA CONTAGEM?
#
# Ela NAO responde como o cartao e desenhado, em que territorio vive, que
# familia tem, que papel cumpre, que evidencia o sustenta, nem se esta provado.
# Cada uma dessas e outra coluna, com outro dono:
#
#     ENTITY_SPECIES != ROLE != TERRITORY != FAMILY != EVIDENCE_CLASS != TRUST
#
# O VOCABULARIO E FECHADO e vive em `docs/arquitetura/SYSTEM-MAP-TRUST-CONTRACT.md`
# §5. Ele nao e reescrito aqui: `ESPECIES_VALIDAS` e derivada da tabela que
# `especies()` ja constroi, para nao existirem duas listas de nomes.
#
# E O MAPEAMENTO VIVE NUM SITIO SO. Escrever `ENTITY_SPECIES` a mao dentro de
# cada um dos treze blocos criaria treze donos do mesmo facto, e bastava um
# deles divergir para a contagem voltar a nao dizer o que conta. Aqui ele e
# declarado uma vez e CARIMBADO por `carimbar_especies()`, que RECUSA uma
# superficie que a tabela nao conheca — porque uma superficie nova que entra
# em silencio e exactamente o defeito que o G0 veio fechar.
# ─────────────────────────────────────────────────────────────────────────
ESPECIE_DA_SUPERFICIE = {
    # ── UNIVERSOS ────────────────────────────────────────────────────────
    "SYSTEM_MAP_NODE_UNIVERSE":               "SYSTEM_MAP_VISUAL_CARD",
    "SYSTEM_MAP_COLLECTION_WAITING_UNIVERSE": "SYSTEM_MAP_VISUAL_CARD",
    # O pente fino nao conta «cartoes»: conta as pecas a que ele faz as quatro
    # perguntas. Os membros sao os MESMOS objectos do universo pai, e a especie
    # e outra porque a pergunta e outra.
    "PENTE_FINO_UNIVERSE":                    "COLLECTION_INTERNAL_PIECE",
    "TOPOLOGY_CENSUS_UNIVERSE":               "SYSTEM_MAP_VISUAL_CARD",
    "CASCO_TOOL_CARD_UNIVERSE":               "PORTAL_TOOL_CARD",
    # ⚠️ ESTA CONTA FICHEIROS, E NAO CARTOES — e por isso e que ela obrigou o
    # contrato a declarar uma especie que nao e de cartao (§5.3). Dizer-lhe
    # UNKNOWN seria mentir para o outro lado: sabe-se exactamente o que sao.
    "COLLECTION_CODE_FILE_UNIVERSE":          "COLLECTION_CODE_FILE",
    # ── LENTES ───────────────────────────────────────────────────────────
    "FRONTEND_FAMILY_COUNTER":                "SYSTEM_MAP_VISUAL_CARD",
    "FRONTEND_DEFAULT_VIEW_DRAWN":            "SYSTEM_MAP_VISUAL_CARD",
    "PENTE_FINO":                             "COLLECTION_INTERNAL_PIECE",
    "CENSO_DA_TOPOLOGIA":                     "SYSTEM_MAP_VISUAL_CARD",
    "CENSO_DA_COLETA":                        "COLLECTION_CODE_FILE",
    "CENSO_CARDS_SENSORES":                   "PORTAL_TOOL_CARD",
    "STATE_COUNTS":                           "SYSTEM_MAP_VISUAL_CARD",
}


def validar_vocabulario(mapeamento: dict, validas: set) -> None:
    """O mapeamento so pode apontar nomes que a tabela das especies declara.

    ⚠️ ESTA GUARDA SOBREVIVEU A MUTACAO NA PRIMEIRA RONDA, e por uma razao que
    vale a pena escrever: ela estava INLINE em `medir()`, onde nada a podia
    chamar com um defeito na mao. Desligar o `if` nao mudava nada, porque nesta
    arvore nao ha nome invalido nenhum para ela apanhar.

        UMA GUARDA QUE SO CORRE SOBRE DADOS SAOS NUNCA FOI TESTADA.

    Sendo funcao, `test_reconciliacao_do_universo.py` corre-a contra um nome
    inventado e exige que ela recuse.
    """
    fora = sorted(set(mapeamento.values()) - set(validas))
    if fora:
        raise SystemExit(
            "ESPECIE_FORA_DO_VOCABULARIO=%s · o mapeamento aponta um nome que a "
            "tabela de especies nao declara." % ", ".join(fora))


def carimbar_especies(universos: dict, lentes: list) -> None:
    """Poe `ENTITY_SPECIES` em cada superficie, a partir do dono unico.

    Recusa em vez de omitir. Uma superficie que a tabela nao conheca para a
    cadeia aqui, com o nome dela na mensagem — e nao sai um artefacto com uma
    contagem muda la dentro.

        UMA CONTAGEM QUE NAO DIZ O QUE CONTA E UM NUMERO, NAO UMA MEDICAO.
    """
    orfas = ([k for k in universos if k not in ESPECIE_DA_SUPERFICIE]
             + [l["LENS_ID"] for l in lentes
                if l["LENS_ID"] not in ESPECIE_DA_SUPERFICIE])
    if orfas:
        raise SystemExit(
            "SUPERFICIE_SEM_ESPECIE=%s · acrescente-a a ESPECIE_DA_SUPERFICIE "
            "em reconciliacao_do_universo.py, com a especie do contrato §5."
            % ", ".join(sorted(orfas)))
    for nome, u in universos.items():
        u["ENTITY_SPECIES"] = ESPECIE_DA_SUPERFICIE[nome]
    for l in lentes:
        l["ENTITY_SPECIES"] = ESPECIE_DA_SUPERFICIE[l["LENS_ID"]]

# ─────────────────────────────────────────────────────────────────────────
# A REGRA DA VISTA PADRAO — CITADA DO BROWSER, NAO REESCRITA AQUI.
#
# A faixa conta 65 e a tela desenha 64: um cartao com bandeira que nao e de
# Italia nem TRANSVERSAL nao e desenhado na vista padrao. As duas coisas estao
# certas e nao sao a mesma, e a diferenca nunca estava escrita em lado nenhum.
#
#     CONTADO PELA FAIXA  !=  DESENHADO NA TELA.
#
# A regra e do `map.js`, e continua a ser. O que esta aqui e a CITACAO literal
# da linha, e `test_reconciliacao_do_universo.py` reprova se ela deixar de
# existir no ficheiro de onde saiu — uma regra copiada que ninguem confere
# envelhece em silencio, e a partir dai descreve uma tela que ja nao existe.
# ─────────────────────────────────────────────────────────────────────────
REGRA_DA_VISTA_PADRAO = (
    "&& n.pais && n.pais !== 'ITALIA' && n.pais !== 'TRANSVERSAL') return false;")
REGRA_DA_VISTA_PADRAO_VEM_DE = "system-map/app/map.js · activeView()"
PAISES_QUE_A_VISTA_PADRAO_DESENHA = ("ITALIA", "TRANSVERSAL")

# ─────────────────────────────────────────────────────────────────────────
# OS CAMPOS QUE CARREGAM UM SHA DE COMMIT — E POR QUE ESTAO NOMEADOS AQUI.
#
# Esta reconciliacao diz, sobre os outros, que um SHA de commit nao serve de
# prova de frescura. Ela nao pode escapar a propria lei: um SHA dentro deste
# artefato muda a cada commit, e por isso o ficheiro commitado NUNCA poderia
# ser igual ao que a arvore produz — a prova anti-drift reprovaria sempre, e
# quem a lesse aprenderia a ignora-la.
#
#     UMA PROVA QUE REPROVA SEMPRE NAO E UMA PROVA. E UM RUIDO.
#
# Entao os SHAs ficam, porque quem le quer saber de que corrida veio o numero,
# e ficam NOMEADOS: a comparacao anti-drift retira exactamente estas chaves, e
# o que sobra e conteudo. A identidade verificavel viaja ao lado, em
# MEASURED_TREE — a impressao da arvore, que nao muda por se guardar o mapa.
# ─────────────────────────────────────────────────────────────────────────
CARIMBOS_NAO_COMPARAVEIS = [
    "MEASURED_HEAD",
    "FROM_WHICH_HEAD",
    "GENERATED_AT",
    # A IMPRESSAO DA ARVORE TAMBEM E CARIMBO, E ISTO FOI MEDIDO.
    # Ela nao muda quando se guarda o mapa — para isso foi feita —, mas MUDA
    # quando qualquer ficheiro-fonte muda, e treze censos deste repositorio
    # carimbam o SHA do commit e nao estao excluidos da impressao. Efeito: todo
    # commit move a impressao, e a prova anti-drift reprovava por uma diferenca
    # que nao e populacao nenhuma.
    #
    #     ESTA PROVA PERGUNTA «A POPULACAO MUDOU?», NAO «A ARVORE MUDOU?».
    #
    # Quem responde por «a arvore mudou e o mapa nao» ja existe e e o passo 2b
    # do CI, `impressao_da_arvore.py --conferir-carimbo`. Duas provas para a
    # mesma pergunta nao dao duas respostas: dao uma resposta e um ruido.
    "MEASURED_TREE",
]

# O QUE SE LE DO RELOGIO NAO SE COMPARA COM O QUE ESTA COMMITADO.
#
# `FRESCURA` e uma leitura do estado da arvore NO MOMENTO em que o gerador
# correu: que artefato bate com esta arvore, qual ficou para tras, qual nem
# consegue dizer. Ela muda sem que uma unica populacao mude — e comparar uma
# leitura de relogio com um ficheiro guardado e pedir que o passado preveja o
# presente. As provas da frescura leem o bloco VIVO, e estao noutro sitio.
BLOCOS_NAO_COMPARAVEIS = ["PROVENANCE", "FRESCURA"]


def git(*args: str) -> str:
    return subprocess.run(["git", "-C", str(RAIZ), *args],
                          capture_output=True, text=True,
                          encoding="utf-8", errors="replace").stdout.strip()


def ler(caminho: Path):
    if not caminho.exists():
        return None
    return json.loads(caminho.read_text(encoding="utf-8"))


# ─────────────────────────────────────────────────────────────────────────
# 1 · POR QUE CADA EXCLUIDO ESTA FORA
#
# A razao NAO e inventada cartao a cartao: ela e derivada do TERRITORIO, que
# e a dimensao pela qual o pente fino filtra. Um motivo por cartao seria uma
# opiniao escrita a mao; um motivo por territorio e a leitura da regra que
# de facto exclui.
#
#     EXCLUSION_INTENTIONAL diz se alguem DECIDIU excluir, ou se o cartao
#     caiu de fora porque a tupla nao o continha. As duas coisas parecem
#     iguais no resultado e sao opostas na causa.
# ─────────────────────────────────────────────────────────────────────────
MOTIVO_POR_TERRITORIO = {
    "Z-BIBLIA": {
        "EXCLUSION_REASON": "CONSTITUICAO_DA_COLETA",
        "EXCLUSION_OWNER": "pente_fino_da_coleta.ZONAS",
        "EXCLUSION_INTENTIONAL": "YES",
        "PORQUE": "a lei escrita nao e uma peca que colhe. Perguntar-lhe «quem te "
                  "chama?» e perguntar a uma constituicao quem a executa.",
    },
    "Z-ENTRADA": {
        "EXCLUSION_REASON": "CARTAO_DA_AVENIDA_PRINCIPAL",
        "EXCLUSION_OWNER": "pente_fino_da_coleta.ZONAS",
        "EXCLUSION_INTENTIONAL": "NO",
        "PORQUE": "cartao nivel=PRINCIPAL. A avenida tem cinco cartoes PRINCIPAL e "
                  "a tupla apanha UM deles (C-ADMISSAO, em Z-ADMISSAO). Quatro "
                  "ficam de fora e um fica dentro, sem regra que separe os dois.",
    },
    "Z-ORQUESTRADOR": {
        "EXCLUSION_REASON": "CARTAO_DA_AVENIDA_PRINCIPAL",
        "EXCLUSION_OWNER": "pente_fino_da_coleta.ZONAS",
        "EXCLUSION_INTENTIONAL": "NO",
        "PORQUE": "cartao nivel=PRINCIPAL, mesma incoerencia de Z-ENTRADA.",
    },
    "Z-EXECUCAO": {
        "EXCLUSION_REASON": "CARTAO_DA_AVENIDA_PRINCIPAL",
        "EXCLUSION_OWNER": "pente_fino_da_coleta.ZONAS",
        "EXCLUSION_INTENTIONAL": "NO",
        "PORQUE": "cartoes nivel=PRINCIPAL, mesma incoerencia de Z-ENTRADA.",
    },
    "Z-MEDIDAS": {
        "EXCLUSION_REASON": "INSTRUMENTO_QUE_MEDE_A_COLETA",
        "EXCLUSION_OWNER": "pente_fino_da_coleta.ZONAS",
        "EXCLUSION_INTENTIONAL": "UNKNOWN",
        "PORQUE": "sao as MEDIDAS da coleta — censos, rastro, contratos e regras. "
                  "Fazer as quatro perguntas ao instrumento que mede e uma "
                  "pergunta de outra especie; mas ninguem escreveu essa decisao "
                  "em lado nenhum: ela cai da tupla, nao de uma regra.",
    },
    "Z-ESPERA": {
        "EXCLUSION_REASON": "SALA_DE_ESPERA_CANONICA_FORA_DA_TUPLA",
        "EXCLUSION_OWNER": "pente_fino_da_coleta.ZONAS",
        "EXCLUSION_INTENTIONAL": "UNKNOWN",
        "PORQUE": "e a UNICA peca da familia F-ESPERA, e esta fora do pente fino — "
                  "enquanto as 13 pecas mostradas sob o MESMO NOME de zona "
                  "(Z-GUARDA, «A SALA DE ESPERA») estao dentro. Dois territorios "
                  "com o mesmo nome, um dentro e outro fora.",
    },
}


def razao_da_exclusao(t: str, motivo: dict | None) -> dict:
    """POR QUE ESTE CARTAO NAO ESTA NO PENTE FINO — e ha TRES causas, nao uma.

    A terceira foi descoberta por ataque, e parecia a segunda.

        O TERRITORIO ESTA NA TUPLA E O CARTAO NAO ESTA NO PENTE FINO.

    Medido: injectou-se um cartao em `Z-ACOES` — territorio que a tupla CONHECE
    — e o pente fino nao o viu. Correr a cadeia UMA SEGUNDA VEZ, sem mexer em
    mais nada, e ele aparece: 48 -> 49. A causa e a ORDEM da cadeia:
    `pente_fino_da_coleta.py` LE `state.generated.json` no passo 5, e
    `generate_system_map.py` ESCREVE-O no passo 7.

        O PENTE FINO MEDE SEMPRE O CONJUNTO DE NOS DA CORRIDA ANTERIOR.

    Chamar a isto «territorio fora da tupla» seria diagnosticar a doenca errada
    com confianca — e mandar a proxima pessoa alargar um filtro que nao tem
    defeito nenhum.
    """
    if t in PENTE_ZONAS:
        return {
            "EXCLUSION_REASON": "PENTE_FINO_MEDIU_OUTRO_CONJUNTO_DE_NOS",
            "EXCLUSION_OWNER": "system-map/scripts/CADEIA-DO-MAPA.json · REGERAR",
            "EXCLUSION_INTENTIONAL": "NO",
            "PORQUE": "o territorio ESTA na tupla do pente fino. O cartao falta "
                      "porque o pente fino le `state.generated.json` antes de o "
                      "gerador o escrever, e por isso mede o conjunto de nos da "
                      "corrida anterior. Correr a cadeia outra vez apanha-o.",
            "MECANICA": "territory=%s esta em ZONAS, e o id nao esta em "
                        "pente-fino.generated.json · PECAS[]" % t,
        }
    return {
        "EXCLUSION_REASON": (motivo or {}).get(
            "EXCLUSION_REASON", "TERRITORIO_FORA_DA_TUPLA_SEM_MOTIVO_ESCRITO"),
        "EXCLUSION_OWNER": (motivo or {}).get(
            "EXCLUSION_OWNER", "pente_fino_da_coleta.ZONAS"),
        "EXCLUSION_INTENTIONAL": (motivo or {}).get(
            "EXCLUSION_INTENTIONAL", "UNKNOWN"),
        "PORQUE": (motivo or {}).get(
            "PORQUE",
            "territorio novo: entrou no mapa e a tupla estatica do pente fino "
            "nao o conhece. Expandir o sistema encolheu a auditoria."),
        "MECANICA": "territory=%s nao esta em pente_fino_da_coleta.ZONAS" % t,
    }


def especies(S, declarada, matriz, pente, coleta):
    """AS ESPECIES DE «CARD» QUE ESTE REPOSITORIO USA — e o que cada uma conta.

    Nao se inventa especie: cada uma aqui tem dono, ficheiro e sitio onde
    aparece. Duas que fossem a mesma coisa levariam o mesmo nome; as que estao
    aqui foram medidas e sao diferentes.
    """
    telas = [n["id"] for n in S["NODES"] if n["territory"] == "Z-TELAS"]
    cards_do_casco = [c["CARD_ID"] for c in (matriz or {}).get("CARDS", [])]
    nomes_telas = {n["name"] for n in S["NODES"] if n["territory"] == "Z-TELAS"}
    nomes_casco = {c["NOME"] for c in (matriz or {}).get("CARDS", [])}
    return [
        {
            "E_ESPECIE_DE_CARTAO": True,
            "NAME": "ARCHITECTURE_NODE",
            "OWNER": "system-map/data/architecture.declared.json",
            "DEFINITION": "peca DECLARADA a mao por gente, com id, territorio e porque.",
            "SOURCE": "COMPONENTS[]",
            "WHERE_DISPLAYED": "nao aparece sozinha; e a entrada do gerador.",
            "COUNT": len(declarada["COMPONENTS"]),
        },
        {
            "E_ESPECIE_DE_CARTAO": True,
            "NAME": "SYSTEM_MAP_VISUAL_CARD",
            "OWNER": "system-map/scripts/generate_system_map.py",
            "DEFINITION": "o rectangulo que a tela desenha. E o ARCHITECTURE_NODE "
                          "MAIS as pecas que o gerador sintetiza a partir de medicao "
                          "(telas do portal, veiculos, linhagens).",
            "SOURCE": "system-map/data/state.generated.json · NODES[]",
            "WHERE_DISPLAYED": "system-map/app/map.js · $('nodes')",
            "COUNT": len(S["NODES"]),
            "RELACAO_COM_ARCHITECTURE_NODE": "SUPERSET",
            "SINTETIZADOS_SEM_DECLARACAO": len(
                {n["id"] for n in S["NODES"]}
                - {c["id"] for c in declarada["COMPONENTS"]}),
        },
        {
            "E_ESPECIE_DE_CARTAO": True,
            "NAME": "COLLECTION_INTERNAL_PIECE",
            "OWNER": "system-map/scripts/pente_fino_da_coleta.py",
            "DEFINITION": "SYSTEM_MAP_VISUAL_CARD cujo TERRITORIO esta na tupla ZONAS "
                          "e que por isso recebe as quatro perguntas.",
            "SOURCE": "system-map/data/pente-fino.generated.json · PECAS[]",
            "WHERE_DISPLAYED": "so no artefato e na saida do script; a tela nao o mostra.",
            "COUNT": len((pente or {}).get("PECAS", [])),
            "RELACAO_COM_VISUAL_CARD": "SUBSET",
        },
        {
            "E_ESPECIE_DE_CARTAO": True,
            "NAME": "PORTAL_TOOL_CARD",
            "OWNER": "system-map/scripts/censo_cards_sensores.py (via scan_casco.py)",
            "DEFINITION": "uma das ferramentas do portal italiano. A palavra «card» "
                          "aqui NAO e a palavra «card» do pente fino.",
            "SOURCE": "data/derivados/MATRIZ-CARDS-SENSORES-V1.json · CARDS[]",
            "WHERE_DISPLAYED": "o portal italiano; e, como no do mapa, a zona Z-TELAS.",
            "COUNT": len(cards_do_casco),
            "MESMA_COISA_QUE": "os %d nos de Z-TELAS — provado por nome, nao por id: "
                               "os ids sao diferentes (`meeting` vs `C-TELA-MEETING`)."
                               % len(telas),
            "PROVA_DE_IDENTIDADE": ("NOMES_IGUAIS"
                                    if nomes_telas and nomes_telas == nomes_casco
                                    else "NOMES_DIFEREM"),
            "INTERSECCAO_COM_A_COLETA": 0,
        },
        {
            # ⚠️ ESTA NAO E UMA ESPECIE DE CARTAO, E ISSO E O PONTO.
            # A §5 do contrato respondia «o que quer dizer CARD». So que o
            # `ENTITY_SPECIES` e exigido a TODA superficie de contagem, e uma
            # delas conta FICHEIROS. Sem esta linha, a unica saida honesta seria
            # UNKNOWN — e UNKNOWN aqui seria mentir para o outro lado: sabe-se
            # exactamente o que estes membros sao, e quem os mede.
            #
            #     NAO SABER E UM ESTADO. FINGIR QUE NAO SE SABE E OUTRO.
            "NAME": "COLLECTION_CODE_FILE",
            "E_ESPECIE_DE_CARTAO": False,
            "OWNER": "system-map/scripts/censo_da_coleta.py",
            "DEFINITION": "ficheiro de codigo numa das gavetas da coleta. Um "
                          "cartao pode ter zero ou muitos destes; nao se somam.",
            "SOURCE": "system-map/data/censo-da-coleta.generated.json · FICHEIROS[]",
            "WHERE_DISPLAYED": "nenhures na tela.",
            "COUNT": (coleta or {}).get("RESUMO", {}).get("ficheiros_de_codigo", 0),
            "RELACAO_COM_VISUAL_CARD": "UNIDADE DIFERENTE — nao ha subconjunto "
                                       "nem sobreposicao possivel entre um "
                                       "ficheiro e um cartao.",
        },
        {
            "E_ESPECIE_DE_CARTAO": True,
            "NAME": "VISUAL_ONLY_BLOCK",
            "OWNER": "system-map/scripts/generate_system_map.py · desenhar()",
            "DEFINITION": "rectangulo de FAMILIA ou de ZONA. Nao e peca: e o fundo "
                          "que agrupa pecas, e carrega a contagem que se le de longe.",
            "SOURCE": "state.generated.json · FAMILIES[] e TERRITORIES[]",
            "WHERE_DISPLAYED": "map.js linhas 83-99",
            "COUNT": len(S["FAMILIES"]) + len(S["TERRITORIES"]),
        },
    ]


def medir(com_topologia: bool) -> dict:
    S = ler(DADOS / "state.generated.json")
    declarada = ler(DADOS / "architecture.declared.json")
    gerada = ler(DADOS / "architecture.generated.json")
    pente = ler(DADOS / "pente-fino.generated.json")
    coleta = ler(DADOS / "censo-da-coleta.generated.json")
    matriz = ler(RAIZ / "data" / "derivados" / "MATRIZ-CARDS-SENSORES-V1.json")

    # O VOCABULARIO SAI DA TABELA DAS ESPECIES, e nao de uma segunda lista de
    # nomes ao lado dela. Duas listas divergem no dia em que alguem acrescenta
    # uma especie de um lado so — e a validacao passaria a aprovar um nome que
    # a tabela ja nao conhece, ou a reprovar um que ela conhece.
    ESPECIES = especies(S, declarada, matriz, pente, coleta)
    validar_vocabulario(ESPECIE_DA_SUPERFICIE, {e["NAME"] for e in ESPECIES})

    nos = {n["id"]: n for n in S["NODES"]}
    terr = {t["id"]: t for t in S["TERRITORIES"]}
    fam = {f["id"]: f for f in S["FAMILIES"]}

    # ── O UNIVERSO VISUAL ────────────────────────────────────────────────
    # Quem e dono dele: `generate_system_map.desenhar()`, que conta os membros
    # colocados em cada zona (linha 2612) e soma as zonas de cada familia
    # (linha 2634). Nao ha numero escrito a mao em lado nenhum desta cadeia.
    visual = sorted(i for i, n in nos.items() if n.get("family") in LADO_DA_COLETA)
    pente_ids = {p["id"] for p in (pente or {}).get("PECAS", [])}

    topologia = None
    if com_topologia:
        r = subprocess.run([sys.executable, str(AQUI / "censo_da_topologia.py"), "--json"],
                           capture_output=True, text=True, encoding="utf-8")
        if r.returncode == 0:
            topologia = json.loads(r.stdout)
    topo_ids = ({f["CARD_ID"] for f in topologia["FICHAS"]}
                if topologia else None)

    impressao, ficheiros, ausentes = IMPRESSAO.do_disco()
    carimbo_do_mapa = ((gerada or {}).get("PROVENANCE") or {}).get(
        "SOURCE_TREE_FINGERPRINT")

    cabeca = {
        "HEAD": git("rev-parse", "HEAD"),
        "BRANCH": git("rev-parse", "--abbrev-ref", "HEAD"),
        "GENERATED_AT": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "SOURCE_TREE_FINGERPRINT": impressao,
        "FICHEIROS_NA_IMPRESSAO": ficheiros,
        "FICHEIROS_AUSENTES_DO_DISCO": ausentes,
    }

    # ── CARTAO A CARTAO ──────────────────────────────────────────────────
    cartoes = []
    for i in visual:
        n = nos[i]
        dentro = i in pente_ids
        t = n["territory"]
        motivo = MOTIVO_POR_TERRITORIO.get(t)
        cartoes.append({
            "CARD_ID": i,
            "NAME": n["name"],
            "FAMILY": n.get("family"),
            "TERRITORY": t,
            "TERRITORY_NAME": terr.get(t, {}).get("name", NAO_SEI),
            "KIND": n.get("kind"),
            "NIVEL": n.get("nivel", NAO_SEI),
            "FILES": n.get("files", []),
            "FILE_COUNT": len(n.get("files", [])),
            "VIEWS": n.get("views", []),
            "IN_VISUAL_COLLECTION_WAITING": True,
            "IN_PENTE_FINE": dentro,
            "IN_TOPOLOGY_CENSUS": (i in topo_ids) if topo_ids is not None else NAO_SEI,
            "IN_COLLECTION_CENSUS": NAO_SEI,
            "WHY_INCLUDED": (
                "territory=%s esta em pente_fino_da_coleta.ZONAS" % t if dentro
                else None),
            "WHY_EXCLUDED": (None if dentro else razao_da_exclusao(t, motivo)),
            # A IDENTIDADE DA MEDICAO E A ARVORE, NAO O COMMIT. O SHA viaja
            # ao lado, nomeado como carimbo, e nao entra na comparacao.
            "MEASURED_TREE": impressao,
            "MEASURED_HEAD": cabeca["HEAD"],
        })
    cartoes.sort(key=lambda c: c["CARD_ID"])

    incluidos = [c for c in cartoes if c["IN_PENTE_FINE"]]
    excluidos = [c for c in cartoes if not c["IN_PENTE_FINE"]]

    # ── O PENTE FINO CONHECE ALGUEM QUE A VISTA NAO TEM? ─────────────────
    # A conta so fecha nos dois sentidos. Um membro do pente fino fora do
    # universo visual seria um cartao auditado que a tela nao mostra — e um
    # cartao que ninguem ve e um cartao que ninguem audita.
    orfaos_do_pente = sorted(pente_ids - set(visual))

    universos = {
        "SYSTEM_MAP_NODE_UNIVERSE": {
            "UNIVERSE_DEFINITION": "toda peca desenhada pela tela do mapa.",
            "OWNER": "system-map/scripts/generate_system_map.py",
            "MEASURED_HEAD": (S.get("PROVENANCE") or {}).get("HEAD", NAO_SEI),
            "MEASURED_TREE": (S.get("PROVENANCE") or {}).get(
                "SOURCE_TREE_FINGERPRINT", NAO_SEI),
            "COUNT": len(nos),
            "INCLUSION_RULE": "existe em state.generated.json · NODES[]",
            "EXCLUSION_RULE": "nada; e o universo de topo desta reconciliacao.",
            "PARENT_UNIVERSE_ID": None,
            "MEMBERS": sorted(nos),
        },
        "SYSTEM_MAP_COLLECTION_WAITING_UNIVERSE": {
            "UNIVERSE_DEFINITION": "os cartoes que a tela desenha dentro das faixas "
                                   "COLETA e A ESPERA. E este o universo que a "
                                   "faixa visual conta.",
            "OWNER": "system-map/scripts/generate_system_map.py · desenhar()",
            "MEASURED_HEAD": (S.get("PROVENANCE") or {}).get("HEAD", NAO_SEI),
            "MEASURED_TREE": (S.get("PROVENANCE") or {}).get(
                "SOURCE_TREE_FINGERPRINT", NAO_SEI),
            "COUNT": len(visual),
            "INCLUSION_RULE": "family in %s" % (list(LADO_DA_COLETA),),
            "EXCLUSION_RULE": "qualquer outra familia (F-INTELIGENCIA, F-GOVERNANCA, "
                              "F-ENTREGA) — sao outras faixas da mesma tela.",
            "PARENT_UNIVERSE_ID": "SYSTEM_MAP_NODE_UNIVERSE",
            "MEMBERS": visual,
            "POR_FAMILIA": {f: sum(1 for i in visual if nos[i]["family"] == f)
                            for f in LADO_DA_COLETA},
            "POR_TERRITORIO": {t: sum(1 for i in visual if nos[i]["territory"] == t)
                               for t in sorted({nos[i]["territory"] for i in visual})},
        },
        "PENTE_FINO_UNIVERSE": {
            "UNIVERSE_DEFINITION": "as pecas da coleta a que se fazem as quatro "
                                   "perguntas (de onde vem, para onde vai, porque "
                                   "existe, alguem corre).",
            "OWNER": "system-map/scripts/pente_fino_da_coleta.py",
            "MEASURED_HEAD": (pente or {}).get("PROVENANCE", {}).get("HEAD", NAO_SEI),
            "MEASURED_HEAD_VERIFICAVEL": False,
            "MEASURED_HEAD_PORQUE_NAO": (
                "carimba o SHA do commit. Um ficheiro commitado nunca pode nomear o "
                "commit que o contem, logo este carimbo aponta sempre para o commit "
                "ANTERIOR — medido em todos os commits que tocam este artefato. "
                "A prova de frescura verificavel e SOURCE_TREE_FINGERPRINT."),
            "MEASURED_TREE": NAO_SEI,
            "COUNT": len(pente_ids),
            "INCLUSION_RULE": "territory in %s" % (list(PENTE_ZONAS),),
            "EXCLUSION_RULE": "territorio fora da tupla. A tupla e ESTATICA: um "
                              "territorio novo fica de fora sem que nada reclame.",
            "PARENT_UNIVERSE_ID": "SYSTEM_MAP_COLLECTION_WAITING_UNIVERSE",
            "DIMENSAO": "TERRITORY",
            "MEMBERS": sorted(pente_ids),
            "EXCLUDED_MEMBERS": [c["CARD_ID"] for c in excluidos],
            "EXCLUSION_REASON_BY_MEMBER": {
                c["CARD_ID"]: c["WHY_EXCLUDED"]["EXCLUSION_REASON"] for c in excluidos},
            "MEMBROS_FORA_DO_PAI": orfaos_do_pente,
        },
    }

    if topo_ids is not None:
        universos["TOPOLOGY_CENSUS_UNIVERSE"] = {
            "UNIVERSE_DEFINITION": "a coleta e a espera MAIS tudo o que lhes toca por "
                                   "aresta. E um fecho de vizinhanca, nao uma familia.",
            "OWNER": "system-map/scripts/censo_da_topologia.py",
            "MEASURED_HEAD": cabeca["HEAD"],
            "MEASURED_TREE": impressao,
            "COUNT": len(topo_ids),
            "INCLUSION_RULE": "family in %s, OU ligado por aresta a alguem que esteja."
                              % (list(LADO_DA_COLETA),),
            "EXCLUSION_RULE": "nenhuma aresta ate a coleta ou a espera.",
            "PARENT_UNIVERSE_ID": "SYSTEM_MAP_NODE_UNIVERSE",
            "DIMENSAO": "FAMILY + FECHO_POR_ARESTA",
            "MEMBERS": sorted(topo_ids),
            "RELACAO_COM_O_UNIVERSO_VISUAL": "SUPERSET",
            "VIZINHOS_DE_FORA_DA_COLETA": sorted(topo_ids - set(visual)),
        }

    universos["CASCO_TOOL_CARD_UNIVERSE"] = {
        "UNIVERSE_DEFINITION": "as ferramentas do portal italiano. Chamam-se «cards» "
                               "e nao tem UM membro em comum com a coleta.",
        "OWNER": "system-map/scripts/censo_cards_sensores.py",
        "MEASURED_HEAD": ((matriz or {}).get("PROVENANCE") or {}).get("HEAD", NAO_SEI),
        "MEASURED_HEAD_VERIFICAVEL": False,
        "MEASURED_TREE": NAO_SEI,
        "COUNT": len((matriz or {}).get("CARDS", [])),
        "INCLUSION_RULE": "ferramenta declarada no casco do portal.",
        "EXCLUSION_RULE": "tudo o resto do repositorio.",
        "PARENT_UNIVERSE_ID": None,
        "DIMENSAO": "FERRAMENTA_DO_PORTAL",
        "MEMBERS": sorted(c["CARD_ID"] for c in (matriz or {}).get("CARDS", [])),
        "INTERSECCAO_COM_O_UNIVERSO_VISUAL": 0,
    }

    universos["COLLECTION_CODE_FILE_UNIVERSE"] = {
        "UNIVERSE_DEFINITION": "FICHEIROS de codigo das gavetas da coleta. Nao sao "
                               "cartoes: um cartao pode ter zero ou muitos ficheiros.",
        "OWNER": "system-map/scripts/censo_da_coleta.py",
        "MEASURED_HEAD": ((coleta or {}).get("PROVENANCE") or {}).get("HEAD", NAO_SEI),
        "MEASURED_HEAD_VERIFICAVEL": False,
        "MEASURED_TREE": NAO_SEI,
        "COUNT": (coleta or {}).get("RESUMO", {}).get("ficheiros_de_codigo", 0),
        "INCLUSION_RULE": "ficheiro de codigo numa das gavetas %s"
                          % (((coleta or {}).get("PROVENANCE") or {}).get("GAVETAS"),),
        "EXCLUSION_RULE": "ficheiro fora das gavetas, ou que nao e codigo.",
        "PARENT_UNIVERSE_ID": None,
        "DIMENSAO": "FICHEIRO",
        "UNIDADE": "FICHEIRO, NAO CARTAO",
    }

    # O QUE A VISTA PADRAO DESENHA DE FACTO — a regra e citada, nao inventada.
    desenhados = [i for i in visual
                  if not nos[i].get("pais")
                  or nos[i]["pais"] in PAISES_QUE_A_VISTA_PADRAO_DESENHA]

    # ── AS LENTES ────────────────────────────────────────────────────────
    lentes = [
        {
            "LENS_ID": "FRONTEND_FAMILY_COUNTER",
            "PARENT_UNIVERSE": "SYSTEM_MAP_COLLECTION_WAITING_UNIVERSE",
            "MEMBER_COUNT": len(visual),
            "DIMENSAO": "FAMILY",
            "INCLUSION_RULE": "a zona pertence a familia; a familia soma as zonas.",
            "EXCLUSION_RULE": "nenhuma; conta o universo inteiro.",
            "WHO_COMPUTES": "system-map/scripts/generate_system_map.py · desenhar()",
            "FROM_WHICH_FILE": "system-map/data/state.generated.json",
            "FROM_WHICH_FIELD": "FAMILIES[].count (soma de TERRITORIES[].count)",
            "FROM_WHICH_HEAD": (S.get("PROVENANCE") or {}).get("HEAD", NAO_SEI),
            "WHERE_DISPLAYED": "system-map/app/map.js:88 — «${f.count} peças»",
            "HARDCODED": False,
            "VALORES": {f: fam[f]["count"] for f in LADO_DA_COLETA if f in fam},
        },
        {
            "LENS_ID": "FRONTEND_DEFAULT_VIEW_DRAWN",
            "PARENT_UNIVERSE": "SYSTEM_MAP_COLLECTION_WAITING_UNIVERSE",
            "MEMBER_COUNT": len(desenhados),
            "DIMENSAO": "PAIS",
            "INCLUSION_RULE": "sem bandeira, ou bandeira em %s"
                              % (list(PAISES_QUE_A_VISTA_PADRAO_DESENHA),),
            "EXCLUSION_RULE": "bandeira de outro pais — a vista padrao nao o "
                              "desenha, e a faixa conta-o na mesma.",
            "WHO_COMPUTES": "o browser, em tempo de render",
            "FROM_WHICH_FILE": "system-map/app/map.js",
            "FROM_WHICH_FIELD": "activeView() · n.pais",
            "FROM_WHICH_HEAD": (S.get("PROVENANCE") or {}).get("HEAD", NAO_SEI),
            "WHERE_DISPLAYED": "os rectangulos que aparecem; e o contador kNodes",
            "HARDCODED": False,
            "REGRA_CITADA": REGRA_DA_VISTA_PADRAO,
            "REGRA_VEM_DE": REGRA_DA_VISTA_PADRAO_VEM_DE,
            "CONTADO_PELA_FAIXA": len(visual),
            "DESENHADO_NA_TELA": len(desenhados),
            "ESCONDIDOS_PELA_VISTA_PADRAO": [
                {"CARD_ID": i, "PAIS": nos[i].get("pais"),
                 "TERRITORY": nos[i]["territory"], "NAME": nos[i]["name"]}
                for i in visual if i not in set(desenhados)],
            "NOTA": "ORFAO NA VISTA != ORFAO NO GRAFO. Um cartao escondido por "
                    "bandeira continua a existir, continua a ser auditado pelo "
                    "pente fino e continua a ser contado pela faixa.",
        },
        {
            "LENS_ID": "PENTE_FINO",
            "PARENT_UNIVERSE": "SYSTEM_MAP_COLLECTION_WAITING_UNIVERSE",
            "MEMBER_COUNT": len(pente_ids),
            "DIMENSAO": "TERRITORY",
            "INCLUSION_RULE": "territory in ZONAS (tupla estatica de %d zonas)"
                              % len(PENTE_ZONAS),
            "EXCLUSION_RULE": "territorio fora da tupla — sem regra semantica.",
            "WHO_COMPUTES": "system-map/scripts/pente_fino_da_coleta.py",
            "FROM_WHICH_FILE": "system-map/data/pente-fino.generated.json",
            "FROM_WHICH_FIELD": "RESUMO.pecas_da_coleta",
            "FROM_WHICH_HEAD": (pente or {}).get("PROVENANCE", {}).get("HEAD", NAO_SEI),
            "WHERE_DISPLAYED": "nenhures na tela — so no artefato.",
            "HARDCODED": False,
        },
        {
            "LENS_ID": "CENSO_DA_TOPOLOGIA",
            "PARENT_UNIVERSE": "SYSTEM_MAP_NODE_UNIVERSE",
            "MEMBER_COUNT": len(topo_ids) if topo_ids is not None else NAO_SEI,
            "DIMENSAO": "FAMILY + FECHO_POR_ARESTA",
            "INCLUSION_RULE": "family in LADO_DA_COLETA, ou vizinho por aresta.",
            "EXCLUSION_RULE": "sem aresta ate a coleta.",
            "WHO_COMPUTES": "system-map/scripts/censo_da_topologia.py",
            "FROM_WHICH_FILE": "(nenhum — o censo so imprime; nao escreve artefato)",
            "FROM_WHICH_FIELD": "RESUMO.CARTOES_NO_UNIVERSO",
            "FROM_WHICH_HEAD": cabeca["HEAD"],
            "WHERE_DISPLAYED": "docs/operacao/TOPOLOGIA-DA-COLETA.md (escrito a mao)",
            "HARDCODED": False,
        },
        {
            "LENS_ID": "CENSO_DA_COLETA",
            "PARENT_UNIVERSE": "COLLECTION_CODE_FILE_UNIVERSE",
            "MEMBER_COUNT": (coleta or {}).get("RESUMO", {}).get("ficheiros_de_codigo", 0),
            "DIMENSAO": "FICHEIRO",
            "INCLUSION_RULE": "ficheiro de codigo nas gavetas da coleta.",
            "EXCLUSION_RULE": "fora das gavetas.",
            "WHO_COMPUTES": "system-map/scripts/censo_da_coleta.py",
            "FROM_WHICH_FILE": "system-map/data/censo-da-coleta.generated.json",
            "FROM_WHICH_FIELD": "RESUMO.ficheiros_de_codigo",
            "FROM_WHICH_HEAD": ((coleta or {}).get("PROVENANCE") or {}).get("HEAD", NAO_SEI),
            "WHERE_DISPLAYED": "nenhures na tela.",
            "HARDCODED": False,
            "AVISO": "conta FICHEIROS. Comparar com uma contagem de CARTOES e somar "
                     "duas unidades diferentes.",
        },
        {
            "LENS_ID": "CENSO_CARDS_SENSORES",
            "PARENT_UNIVERSE": "CASCO_TOOL_CARD_UNIVERSE",
            "MEMBER_COUNT": len((matriz or {}).get("CARDS", [])),
            "DIMENSAO": "FERRAMENTA_DO_PORTAL",
            "INCLUSION_RULE": "ferramenta do casco do portal italiano.",
            "EXCLUSION_RULE": "tudo o que nao e ferramenta do portal.",
            "WHO_COMPUTES": "system-map/scripts/censo_cards_sensores.py",
            "FROM_WHICH_FILE": "data/derivados/MATRIZ-CARDS-SENSORES-V1.json",
            "FROM_WHICH_FIELD": "CONTAGENS.CARDS_TOTAL",
            "FROM_WHICH_HEAD": ((matriz or {}).get("PROVENANCE") or {}).get("HEAD", NAO_SEI),
            "WHERE_DISPLAYED": "o portal italiano.",
            "HARDCODED": False,
            "AVISO": "a palavra «card» aqui nao e a palavra «card» do pente fino. "
                     "Interseccao com a coleta: zero.",
        },
        {
            "LENS_ID": "STATE_COUNTS",
            "PARENT_UNIVERSE": "SYSTEM_MAP_NODE_UNIVERSE",
            "MEMBER_COUNT": S["COUNTS"]["components"],
            "DIMENSAO": "NO",
            "INCLUSION_RULE": "todo no do mapa.",
            "EXCLUSION_RULE": "nenhuma.",
            "WHO_COMPUTES": "system-map/scripts/generate_system_map.py",
            "FROM_WHICH_FILE": "system-map/data/state.generated.json",
            "FROM_WHICH_FIELD": "COUNTS.components",
            "FROM_WHICH_HEAD": (S.get("PROVENANCE") or {}).get("HEAD", NAO_SEI),
            "WHERE_DISPLAYED": "map.js · $('kNodes') (depois dos filtros da tela)",
            "HARDCODED": False,
        },
    ]

    # ── FRESCURA: QUEM MEDIU QUE ARVORE ──────────────────────────────────
    # Nao basta cada artefato dizer um HEAD. A pergunta e se os artefatos que
    # aparecem lado a lado foram medidos sobre A MESMA ARVORE.
    frescura = {"IMPRESSAO_DA_ARVORE_AGORA": impressao,
                "CARIMBO_DO_MAPA": carimbo_do_mapa,
                "MAPA_E_DESTA_ARVORE": carimbo_do_mapa == impressao,
                "ARTEFATOS": [], "STALE": [], "NAO_VERIFICAVEL": []}
    for nome, caminho in (
            ("state.generated.json", DADOS / "state.generated.json"),
            ("architecture.generated.json", DADOS / "architecture.generated.json"),
            ("sources.generated.json", DADOS / "sources.generated.json"),
            ("pente-fino.generated.json", DADOS / "pente-fino.generated.json"),
            ("censo-da-coleta.generated.json", DADOS / "censo-da-coleta.generated.json"),
            ("MATRIZ-CARDS-SENSORES-V1.json",
             RAIZ / "data" / "derivados" / "MATRIZ-CARDS-SENSORES-V1.json")):
        d = ler(caminho) or {}
        prov = d.get("PROVENANCE") or {}
        impressao_dele = prov.get("SOURCE_TREE_FINGERPRINT")
        head_dele = prov.get("HEAD", NAO_SEI)
        if impressao_dele:
            estado = "CURRENT" if impressao_dele == impressao else "STALE"
        else:
            # Um SHA de commit nao serve de prova: ele nasce a apontar para o
            # commit anterior. Dizer CURRENT a partir dele seria inventar.
            estado = "UNVERIFIABLE"
        ficha = {"ARTEFATO": nome, "HEAD_CARIMBADO": head_dele,
                 "IMPRESSAO_CARIMBADA": impressao_dele or NAO_SEI,
                 "ESTADO": estado,
                 "PORQUE": ("carimba SOURCE_TREE_FINGERPRINT, e ele bate com esta arvore"
                            if estado == "CURRENT" else
                            "carimba SOURCE_TREE_FINGERPRINT, e ele NAO bate com esta arvore"
                            if estado == "STALE" else
                            "so carimba SHA de commit — impossivel de verificar por "
                            "construcao: um ficheiro commitado nunca nomeia o commit "
                            "que o contem")}
        frescura["ARTEFATOS"].append(ficha)
        if estado == "STALE":
            frescura["STALE"].append(nome)
        elif estado == "UNVERIFIABLE":
            frescura["NAO_VERIFICAVEL"].append(nome)

    aritmetica = {
        "VISUAL_TOTAL": len(visual),
        "PENTE_FINE_INCLUDED": len(incluidos),
        "PENTE_FINE_EXCLUDED": len(excluidos),
        "SOMA": len(incluidos) + len(excluidos),
        "MATCH": len(visual) == len(incluidos) + len(excluidos),
        "PENTE_FINO_DECLARA": (pente or {}).get("RESUMO", {}).get("pecas_da_coleta"),
        "PENTE_FINO_MEMBROS": len(pente_ids),
        "PENTE_FINO_BATE_CONSIGO": (
            (pente or {}).get("RESUMO", {}).get("pecas_da_coleta") == len(pente_ids)),
        "MEMBROS_DO_PENTE_FORA_DA_VISTA": orfaos_do_pente,
        "NENHUM_CARTAO_DESAPARECE": (
            len(visual) == len(incluidos) + len(excluidos) and not orfaos_do_pente),
    }

    # G0 · toda superficie passa a dizer o que conta, a partir do dono unico.
    carimbar_especies(universos, lentes)

    achados = achar(S, terr, nos, visual, excluidos, frescura, aritmetica,
                    lentes)

    return {
        "SCHEMA": "sintonia.system-map.reconciliacao-do-universo/1",
        "O_QUE_ISTO_E": [
            "O sitio onde os numeros do System Map se encontram.",
            "O JSON e o dono das contagens; markdown nenhum as reescreve.",
            "Nao decide arquitetura: observa as lentes que ja existem.",
        ],
        "PROVENANCE": cabeca,
        "CARIMBOS_NAO_COMPARAVEIS": CARIMBOS_NAO_COMPARAVEIS,
        "BLOCOS_NAO_COMPARAVEIS": BLOCOS_NAO_COMPARAVEIS,
        "CARD_SPECIES": ESPECIES,
        "UNIVERSOS": universos,
        "LENTES": lentes,
        "ARITMETICA": aritmetica,
        "EXCLUIDOS": [
            {k: c[k] for k in ("CARD_ID", "NAME", "FAMILY", "TERRITORY",
                               "TERRITORY_NAME", "NIVEL", "WHY_EXCLUDED")}
            for c in excluidos],
        "FRESCURA": frescura,
        "ACHADOS": achados,
        "CARTOES": cartoes,
    }


def achar(S, terr, nos, visual, excluidos, frescura, aritmetica,
          lentes) -> list:
    """O QUE A RECONCILIACAO ENCONTROU — medido, nao opinado.

    Um achado aqui nao manda consertar nada. Ele nomeia uma coisa que a
    medicao mostrou e que ninguem tinha escrito em lado nenhum.
    """
    a = []

    # ── 1 · DOIS TERRITORIOS COM O MESMO NOME ───────────────────────────
    por_nome = {}
    for t in S["TERRITORIES"]:
        por_nome.setdefault(t["name"].lstrip("· ").strip().upper(), []).append(t)
    for nome, ts in sorted(por_nome.items()):
        if len(ts) > 1:
            a.append({
                "ACHADO": "NOME_DE_ZONA_REPETIDO",
                "GRAVIDADE": "ALTA",
                "O_QUE": "%d territorios chamam-se «%s»: %s"
                         % (len(ts), nome, ", ".join(
                             "%s (familia %s, %d pecas)"
                             % (t["id"], t.get("family"), t.get("count", 0)) for t in ts)),
                "PORQUE_IMPORTA": "quem le a tela ve o nome, nao o id. Duas zonas com "
                                  "o mesmo nome em familias diferentes fazem duas "
                                  "contagens parecerem a mesma coisa.",
                "OWNER": "system-map/data/architecture.declared.json · TERRITORIES[].name",
                "ESTA_MISSAO_CORRIGE": False,
            })

    # ── 2 · A AVENIDA PARTIDA AO MEIO PELO FILTRO ────────────────────────
    principais = [i for i in visual if nos[i].get("nivel") == "PRINCIPAL"]
    fora = [c["CARD_ID"] for c in excluidos if nos[c["CARD_ID"]].get("nivel") == "PRINCIPAL"]
    dentro = [i for i in principais if i not in set(fora)]
    if fora and dentro:
        a.append({
            "ACHADO": "FILTRO_ESTATICO_PARTE_UMA_ESPECIE_AO_MEIO",
            "GRAVIDADE": "ALTA",
            "O_QUE": "dos %d cartoes nivel=PRINCIPAL da coleta, %d entram no pente "
                     "fino (%s) e %d ficam de fora (%s) — a diferenca e o territorio "
                     "estar ou nao na tupla, nao uma regra sobre o que e um cartao "
                     "de avenida." % (len(principais), len(dentro), ", ".join(dentro),
                                      len(fora), ", ".join(fora)),
            "PORQUE_IMPORTA": "a exclusao tem de vir de uma regra semantica, nao de "
                              "«o territorio nao estava na tupla».",
            "OWNER": "system-map/scripts/pente_fino_da_coleta.py · ZONAS",
            "ESTA_MISSAO_CORRIGE": False,
        })

    # ── 3 · TERRITORIO DA COLETA QUE A TUPLA NAO CONHECE ─────────────────
    desconhecidos = sorted({nos[c["CARD_ID"]]["territory"] for c in excluidos
                            if c["WHY_EXCLUDED"]["EXCLUSION_REASON"]
                            == "TERRITORIO_FORA_DA_TUPLA_SEM_MOTIVO_ESCRITO"})
    if desconhecidos:
        a.append({
            "ACHADO": "TERRITORIO_NOVO_CAIU_FORA_EM_SILENCIO",
            "GRAVIDADE": "ALTA",
            "O_QUE": "territorios da coleta que o pente fino nao conhece: %s"
                     % ", ".join(desconhecidos),
            "PORQUE_IMPORTA": "expandir o mapa passou a encolher a auditoria, sem "
                              "uma queixa.",
            "OWNER": "system-map/scripts/pente_fino_da_coleta.py · ZONAS",
            "ESTA_MISSAO_CORRIGE": False,
        })

    # ── 3b · O PENTE FINO MEDIU OUTRO CONJUNTO DE NOS ────────────────────
    atrasados = sorted(c["CARD_ID"] for c in excluidos
                       if c["WHY_EXCLUDED"]["EXCLUSION_REASON"]
                       == "PENTE_FINO_MEDIU_OUTRO_CONJUNTO_DE_NOS")
    if atrasados:
        a.append({
            "ACHADO": "PENTE_FINO_UMA_CORRIDA_ATRASADO",
            "GRAVIDADE": "ALTA",
            "O_QUE": "cartoes em territorio que a tupla CONHECE e que o pente fino "
                     "nao viu: %s" % ", ".join(atrasados),
            "PORQUE_IMPORTA": "`CADEIA-DO-MAPA.json` poe `pente_fino_da_coleta.py` "
                              "(passo 5, LE state.generated.json) antes de "
                              "`generate_system_map.py` (passo 7, ESCREVE-O). O "
                              "pente fino mede o conjunto de nos da corrida "
                              "anterior — e em regime parado ninguem repara, "
                              "porque o conjunto raramente muda.",
            "OWNER": "system-map/scripts/CADEIA-DO-MAPA.json · REGERAR",
            "ESTA_MISSAO_CORRIGE": False,
        })

    # ── 4 · FRESCURA QUE NAO SE CONSEGUE VERIFICAR ───────────────────────
    if frescura["NAO_VERIFICAVEL"]:
        a.append({
            "ACHADO": "CARIMBO_DE_FRESCURA_IMPOSSIVEL_DE_VERIFICAR",
            "GRAVIDADE": "MEDIA",
            "O_QUE": "%s carimbam SHA de commit e nada mais."
                     % ", ".join(frescura["NAO_VERIFICAVEL"]),
            "PORQUE_IMPORTA": "um ficheiro commitado nunca nomeia o commit que o "
                              "contem: o carimbo nasce a apontar para o anterior. "
                              "Quem o le como prova de frescura le uma coisa que nao "
                              "pode estar certa.",
            "OWNER": "cada gerador · PROVENANCE",
            "ESTA_MISSAO_CORRIGE": False,
        })
    if frescura["STALE"]:
        a.append({
            "ACHADO": "ARTEFATO_MEDIDO_NOUTRA_ARVORE",
            "GRAVIDADE": "ALTA",
            "O_QUE": "%s tem impressao de arvore diferente desta."
                     % ", ".join(frescura["STALE"]),
            "PORQUE_IMPORTA": "dois censos lado a lado que mediram arvores diferentes "
                              "nao sao contemporaneos, e a tela nao dizia isso.",
            "OWNER": "a cadeia do mapa",
            "ESTA_MISSAO_CORRIGE": False,
        })

    # ── 4b · A FAIXA CONTA O QUE A TELA NAO DESENHA ──────────────────────
    lente = next((x for x in lentes if x["LENS_ID"] == "FRONTEND_DEFAULT_VIEW_DRAWN"),
                 None)
    if lente and lente["ESCONDIDOS_PELA_VISTA_PADRAO"]:
        a.append({
            "ACHADO": "A_FAIXA_CONTA_O_QUE_A_VISTA_PADRAO_NAO_DESENHA",
            "GRAVIDADE": "MEDIA",
            "O_QUE": "a faixa publica %d pecas e a vista padrao desenha %d. "
                     "Escondido(s) por bandeira: %s"
                     % (lente["CONTADO_PELA_FAIXA"], lente["DESENHADO_NA_TELA"],
                        ", ".join("%s (%s)" % (e["CARD_ID"], e["PAIS"])
                                  for e in lente["ESCONDIDOS_PELA_VISTA_PADRAO"])),
            "PORQUE_IMPORTA": "quem conta os rectangulos no ecra e quem le o numero "
                              "da faixa obtem respostas diferentes, e a tela nao "
                              "diz qual das duas esta a responder a que pergunta. "
                              "Nao e defeito de nenhuma das duas: e a falta da "
                              "relacao entre elas.",
            "OWNER": "system-map/app/map.js · activeView() e desenhar()",
            "ESTA_MISSAO_CORRIGE": False,
        })

    # ── 5 · A LENTE QUE NAO DEIXA RASTO ──────────────────────────────────
    a.append({
        "ACHADO": "CENSO_SEM_ARTEFATO",
        "GRAVIDADE": "MEDIA",
        "O_QUE": "censo_da_topologia.py nao escreve ficheiro nenhum: so imprime. "
                 "A contagem dele so existe enquanto alguem olha para o terminal.",
        "PORQUE_IMPORTA": "um numero sem artefato nao tem como ser comparado amanha, "
                          "e por isso nao tem como envelhecer a vista de toda a gente.",
        "OWNER": "system-map/scripts/censo_da_topologia.py",
        "ESTA_MISSAO_CORRIGE": False,
    })

    if not aritmetica["MATCH"] or aritmetica["MEMBROS_DO_PENTE_FORA_DA_VISTA"]:
        a.append({
            "ACHADO": "ARITMETICA_NAO_FECHA",
            "GRAVIDADE": "CRITICA",
            "O_QUE": json.dumps(aritmetica, ensure_ascii=False),
            "PORQUE_IMPORTA": "algum cartao esta a desaparecer entre lentes.",
            "OWNER": "esta reconciliacao",
            "ESTA_MISSAO_CORRIGE": False,
        })
    return a


def main() -> int:
    d = medir(com_topologia="--sem-topologia" not in sys.argv)
    SAIDA.parent.mkdir(parents=True, exist_ok=True)
    SAIDA.write_text(json.dumps(d, ensure_ascii=False, indent=2) + "\n",
                     encoding="utf-8")

    ar = d["ARITMETICA"]
    print("RECONCILIACAO DO UNIVERSO DO MAPA\n" + "=" * 70)
    print("  HEAD          %s" % d["PROVENANCE"]["HEAD"][:12])
    print("  ARVORE        %s" % d["PROVENANCE"]["SOURCE_TREE_FINGERPRINT"][:16])
    print("  MAPA E DESTA ARVORE?  %s" % d["FRESCURA"]["MAPA_E_DESTA_ARVORE"])
    print()
    print("  AS ESPECIES (· = nao e especie de cartao):")
    for e in d["CARD_SPECIES"]:
        print("    %5s %s %-26s %s" % (e["COUNT"],
                                       " " if e["E_ESPECIE_DE_CARTAO"] else "·",
                                       e["NAME"], e["OWNER"][:42]))
    print()
    print("  OS UNIVERSOS — cada contagem diz o que conta:")
    for k, u in d["UNIVERSOS"].items():
        print("    %5s  %-26s %-40s pai=%s"
              % (u["COUNT"], u["ENTITY_SPECIES"], k, u["PARENT_UNIVERSE_ID"]))
    print()
    print("  AS LENTES:")
    for l in d["LENTES"]:
        print("    %5s  %-26s %s"
              % (l["MEMBER_COUNT"], l["ENTITY_SPECIES"], l["LENS_ID"]))
    print()
    print("  A ARITMETICA:")
    print("    VISUAL_TOTAL          %s" % ar["VISUAL_TOTAL"])
    print("    PENTE_FINE_INCLUDED   %s" % ar["PENTE_FINE_INCLUDED"])
    print("    PENTE_FINE_EXCLUDED   %s" % ar["PENTE_FINE_EXCLUDED"])
    print("    SOMA                  %s   MATCH=%s" % (ar["SOMA"], ar["MATCH"]))
    print()
    print("  OS EXCLUIDOS (%d):" % len(d["EXCLUIDOS"]))
    for c in d["EXCLUIDOS"]:
        w = c["WHY_EXCLUDED"]
        print("    %-24s %-16s %-36s intencional=%s"
              % (c["CARD_ID"][:24], c["TERRITORY"], w["EXCLUSION_REASON"][:36],
                 w["EXCLUSION_INTENTIONAL"]))
    print()
    print("  FRESCURA:")
    for f in d["FRESCURA"]["ARTEFATOS"]:
        print("    %-12s %s" % (f["ESTADO"], f["ARTEFATO"]))
    print()
    print("  ACHADOS (%d):" % len(d["ACHADOS"]))
    for x in d["ACHADOS"]:
        print("    %-9s %s" % (x["GRAVIDADE"], x["ACHADO"]))
    print()
    print("  escrito em %s" % SAIDA.relative_to(RAIZ).as_posix())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
