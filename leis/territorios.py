#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""OS TERRITORIOS — o dono unico de T1..T13, derivado do Atlas e nunca digitado.

    ONE CONCEPT -> ONE OWNER.

⚠️ POR QUE ISTO NASCEU, E O QUE ESTAVA MEDIDO
----------------------------------------------
`T7` queria dizer tres coisas diferentes em tres ficheiros desta arvore, e as
tres corriam ao mesmo tempo:

    docs/fontes/ATLAS-DE-FONTES-EAME.md     T7 = TECHNICAL NETWORK
    pedido/pedido.py::ALVOS                 T7 = «Ciencia e ensaio»
    system-map/scripts/scan_sources.py      T7 = «Ciencia e ensaio»

Cinco codigos colidiam — `T5`, `T7`, `T10`, `T11`, `T12` — e a colisao nao era
teorica. Medida ao vivo, com selecao real, antes desta lei existir:

    python3 pedido/receitas.py "colete ciencia da italia"
        -> 12 fontes: IT-T7-001..012, que sao COOPERATIVAS E CONSORCIOS

As cinco fontes cientificas italianas reais — `IT-T5-001..005`, CREA, FEM
OpenPub, Giornate Fitopatologiche, CNR IRIS, SIRFI — ficavam invisiveis ao
pedido. E o dano ja estava escrito no artefato que o portal le:

    sources.generated.json: EU-T5-001 «OpenAlex» -> territory_name
                            «Preco e mercado»

Uma base de literatura cientifica rotulada como preco de mercado, gerada, e a
ninguem ocorreu perguntar porque — porque o rotulo vinha de uma tabela que
parecia autoridade e nao era.

    DUAS TABELAS PARA O MESMO CONCEITO NAO SAO UMA REDUNDANCIA.
    SAO DUAS VERDADES, E A PARTIR DAI NENHUMA DELAS VALE.

⚠️ E O CONSERTO NAO E MAIS UM ALIAS
------------------------------------
Acrescentar `"ciencia": "T5"` ao lado do `"ciencia": "T7"` que ja la estava
faria a casa suportar as duas leituras, que e como se transforma uma colisao
num comportamento. O conserto e haver UM dono, e os outros consumirem-no.

⚠️ E O DONO NAO DIGITA A TABELA: LE-A
--------------------------------------
Uma quarta copia escrita a mao aqui seria exactamente o defeito outra vez, com
um nome mais bonito. A autoridade e o Atlas — e o Atlas que cada ficha de fonte
cita como `evidence.file`, e e dele que `scan_sources.py` ja extrai as proprias
fichas. Esta lei le a MESMA tabela, na mesma leitura que qualquer pessoa faz:

    docs/fontes/ATLAS-DE-FONTES-EAME.md, seccao «OS 12 TERRITORIOS»

Se o Atlas mudar, isto muda com ele. Se o Atlas nao for legivel, isto LEVANTA —
nao cai para uma copia de reserva, porque uma copia de reserva e a quinta
tabela.

    SEM AUTORIDADE LEGIVEL, NAO HA RESPOSTA. E NAO HA PALPITE.

⚠️ O QUE ESTE FICHEIRO NAO E
-----------------------------
Nao e um classificador: nao olha para uma fonte e decide o territorio dela.
Isso e trabalho de quem escreve a ficha, no Atlas, com evidencia. Aqui so vive
o VOCABULARIO — que codigos existem, o que cada um quer dizer, e que palavras
humanas apontam para cada um.

    O QUE A ROTA MEDE  e o TERRITORIO.
    QUEM PUBLICA       e o OWNER_KIND, e nunca um territorio.
    COMO SE ACESSA     e o ACCESS_METHOD, e nunca um territorio.

O proprio Atlas ja escreve esta separacao, e o `ITALY-SOURCE-MASTER-V1.json`
repete-a: «COOPERATIVE e OWNER_KIND, nunca TERRITORY».
"""
from __future__ import annotations

import os
import re
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

#: A AUTORIDADE. Nao ha segunda.
ATLAS = os.path.join("docs", "fontes", "ATLAS-DE-FONTES-EAME.md")

#: O titulo da seccao que carrega a tabela canonica.
SECCAO = "OS 12 TERRITÓRIOS"

#: A linha de uma celula de codigo: `| **T1** | CROP & PRODUCTION | escopo |`
_LINHA = re.compile(r"^\|\s*\*{0,2}(T\d{1,2})\*{0,2}\s*\|\s*([^|]+?)\s*\|\s*([^|]*?)\s*\|\s*$")

#: O cabecalho de uma seccao de registo: `### T13 · DISTRIBUTION — FRANCE`
_SECCAO_DE_REGISTO = re.compile(r"^#{2,4}\s+(T\d{1,2})\s*·\s*([^—\-]+?)\s*(?:[—\-].*)?$")


class AtlasIlegivel(Exception):
    """O Atlas nao esta ao alcance, ou nao tem a tabela dos territorios.

    ⚠️ ISTO NAO CAI PARA UMA COPIA. Cair seria voltar a ter duas tabelas, e a
    segunda ficaria a responder no dia em que a primeira mudasse — calada.

        FALHAR ALTO E MELHOR DO QUE RESPONDER PELA TABELA ERRADA.
    """


def _texto_do_atlas(raiz=None) -> str:
    caminho = os.path.join(raiz or RAIZ, ATLAS)
    if not os.path.isfile(caminho):
        raise AtlasIlegivel(
            "a autoridade da taxonomia nao esta ao alcance: %s. Sem ela nao ha "
            "resposta — e uma tabela de reserva seria a quinta copia do mesmo "
            "conceito." % ATLAS)
    with open(caminho, encoding="utf-8", errors="replace") as f:
        return f.read()


def _tabela(texto: str) -> dict:
    """Os territorios da tabela canonica, na ordem em que o Atlas os escreve."""
    fora, dentro = {}, False
    for linha in texto.splitlines():
        if linha.startswith("## "):
            # A tabela acaba quando comeca outra seccao de topo.
            if dentro:
                break
            dentro = SECCAO in linha
            continue
        if not dentro:
            continue
        m = _LINHA.match(linha)
        if m:
            fora[m.group(1)] = {"NOME": m.group(2).strip(),
                                "ESCOPO": m.group(3).strip()}
    if not fora:
        raise AtlasIlegivel(
            "o Atlas existe mas a seccao «%s» nao devolveu territorio nenhum. "
            "A tabela mudou de forma, e adivinhar a forma nova seria inventar "
            "a taxonomia." % SECCAO)
    return fora


def _em_divida(texto: str, canonicos: dict) -> dict:
    """Codigos que o Atlas USA em registo mas NAO declara na tabela.

    ⚠️ ISTO NAO E UMA GAVETA DE «OUTRO». `T13` existe no Atlas com nome proprio
    — `DISTRIBUTION` — e tem uma fonte real classificada nele. O que ele nao
    tem e lugar na tabela dos doze, e `ITALY-SOURCE-MASTER-V1.json` declara
    porque, com a reconciliacao proposta e por executar.

    Chamar-lhe «Outro», como `pedido/pedido.py` fazia, apagava as duas coisas
    ao mesmo tempo: o nome que ele tem e a divida que ele e.

        UMA DIVIDA DECLARADA E UMA DIVIDA. UMA DIVIDA RENOMEADA E UMA MENTIRA.
    """
    fora = {}
    for linha in texto.splitlines():
        m = _SECCAO_DE_REGISTO.match(linha)
        if not m:
            continue
        codigo, nome = m.group(1), m.group(2).strip()
        if codigo in canonicos or codigo in fora:
            continue
        fora[codigo] = {
            "NOME": nome,
            "ESCOPO": "",
            "PORQUE": ("usado em registo no Atlas e AUSENTE da tabela dos doze. "
                       "A reconciliacao esta proposta em "
                       "candidatas/ITALY-SOURCE-MASTER-V1.json::taxonomy_debt e "
                       "NAO foi executada."),
        }
    return fora


def carregar(raiz=None) -> dict:
    """Le a autoridade. Devolve `{codigo: {NOME, ESCOPO, ESTADO, ...}}`."""
    texto = _texto_do_atlas(raiz)
    canonicos = _tabela(texto)
    divida = _em_divida(texto, canonicos)
    fora = {}
    for c, d in canonicos.items():
        fora[c] = dict(d, ESTADO="CANONICO")
    for c, d in divida.items():
        fora[c] = dict(d, ESTADO="EM_DIVIDA")
    return fora


# ── A LEITURA, FEITA UMA VEZ ───────────────────────────────────────────────
# Modulo-nivel de proposito: se o Atlas nao for legivel, quem importa esta lei
# fica a saber no `import`, e nao tres etapas mais tarde com meia coleta feita.
TERRITORIOS = carregar()

#: So os doze da tabela. E esta a lista que um pedido pode pedir.
CANONICOS = tuple(c for c, d in TERRITORIOS.items() if d["ESTADO"] == "CANONICO")

#: Os que o Atlas usa e nao declara. Existem, e dizem que sao divida.
EM_DIVIDA = tuple(c for c, d in TERRITORIOS.items() if d["ESTADO"] == "EM_DIVIDA")


def nome(codigo: str) -> str:
    """O nome canonico, ou `NAO SEI`. Nunca um palpite e nunca «Outro»."""
    d = TERRITORIOS.get(str(codigo or "").strip().upper())
    return d["NOME"] if d else "NAO SEI"


def existe(codigo: str) -> bool:
    return str(codigo or "").strip().upper() in TERRITORIOS


def e_canonico(codigo: str) -> bool:
    return str(codigo or "").strip().upper() in CANONICOS


# ═══════════════════════════════════════════════════════════════════════════
# AS PALAVRAS QUE UMA PESSOA USA
# ═══════════════════════════════════════════════════════════════════════════
# ⚠️ ELAS VIVEM AQUI, AO LADO DAS DEFINICOES QUE APONTAM.
# Estavam em `pedido/pedido.py`, longe da tabela — e foi exactamente assim que
# `"ciencia" -> T7` sobreviveu meses depois de `T7` ter passado a querer dizer
# rede tecnica. Um apelido guardado longe do significado nao envelhece: ele
# fica igual enquanto o significado muda debaixo dele.
#
#     UM APELIDO SO SE CONSEGUE CONFERIR AO LADO DO QUE ELE NOMEIA.
#
# Cada linha abaixo aponta para o territorio cujo ESCOPO, no Atlas, contem a
# palavra. Nao e opiniao: `provas/a_taxonomia_tem_um_dono.py` confere-o contra
# o texto do proprio Atlas, e reprova quem se afastar.
APELIDOS = {
    # T1 · CROP & PRODUCTION
    "cultura": "T1", "culturas": "T1", "producao": "T1", "cereais": "T1",
    "safra": "T1", "colheita": "T1",
    # T2 · CLIMATE / WATER / SOIL
    "clima": "T2", "tempo": "T2", "meteorologia": "T2", "chuva": "T2",
    "seca": "T2", "solo": "T2", "agua": "T2", "irrigacao": "T2",
    # T3 · PEST / DISEASE / WEEDS
    "praga": "T3", "pragas": "T3", "doenca": "T3", "doencas": "T3",
    "daninha": "T3", "daninhas": "T3", "infestante": "T3", "alerta": "T3",
    # T4 · REGULATORY
    "regulatorio": "T4", "rotulo": "T4", "rotulos": "T4", "registro": "T4",
    "autorizacao": "T4", "substancia ativa": "T4", "moa": "T4",
    # T5 · SCIENCE
    "ciencia": "T5", "cientifico": "T5", "artigo": "T5", "artigos": "T5",
    "artigos cientificos": "T5", "paper": "T5", "papers": "T5",
    "estudo": "T5", "ensaio": "T5", "ensaios": "T5", "trial": "T5",
    "publicacao": "T5",
    # T6 · RESEARCHERS
    "pesquisador": "T6", "pesquisadores": "T6",
    "materiais de pesquisadores": "T6", "investigador": "T6",
    "investigadores": "T6", "autoria": "T6",
    # T7 · TECHNICAL NETWORK
    "rede tecnica": "T7", "agronomo": "T7", "agronomos": "T7",
    "cooperativa": "T7", "cooperativas": "T7", "consorcio": "T7",
    "consorcios": "T7", "assistencia tecnica": "T7", "extensao": "T7",
    "consultor": "T7", "consultores": "T7",
    # T8 · FARMERS & INFLUENCERS
    "agricultor": "T8", "agricultores": "T8", "influenciador": "T8",
    "influenciadores": "T8", "creator": "T8", "creators": "T8",
    # T9 · COMPETITORS
    "concorrente": "T9", "concorrentes": "T9", "concorrencia": "T9",
    "competidor": "T9", "competidores": "T9",
    # T10 · MARKET / TRADE / INDUSTRY
    "preco": "T10", "precos": "T10", "mercado": "T10", "comercio": "T10",
    "importacao": "T10", "exportacao": "T10", "commodity": "T10",
    "commodities": "T10", "industria": "T10",
    # T11 · EVENTS
    "evento": "T11", "eventos": "T11", "feira": "T11", "feiras": "T11",
    "congresso": "T11", "congressos": "T11", "webinar": "T11",
    # T12 · POLICY / AGRICULTURAL ENVIRONMENT
    "politica": "T12", "politicas": "T12", "subsidio": "T12",
    "subsidios": "T12", "pac": "T12", "sustentabilidade": "T12",
    # T13 · DISTRIBUTION — EM DIVIDA, e o apelido di-lo apontando para o
    # codigo que o Atlas usa. Nao ha apelido que invente um territorio.
    "distribuicao": "T13", "distribuidor": "T13", "distribuidores": "T13",
}


def do_apelido(palavra: str):
    """A palavra humana -> codigo, ou `None`. Nao adivinha por semelhanca."""
    return APELIDOS.get(str(palavra or "").strip().lower())


def em_palavras() -> str:
    L = ["OS TERRITORIOS — dono unico, lido de %s" % ATLAS, ""]
    for c in sorted(TERRITORIOS, key=lambda x: int(x[1:])):
        d = TERRITORIOS[c]
        marca = "" if d["ESTADO"] == "CANONICO" else "   [EM DIVIDA]"
        L.append("  %-4s %s%s" % (c, d["NOME"], marca))
        if d["ESTADO"] != "CANONICO":
            L.append("       %s" % d["PORQUE"])
    L.append("")
    L.append("  apelidos declarados: %d" % len(APELIDOS))
    return "\n".join(L)


if __name__ == "__main__":
    print(em_palavras())
    if "--json" in sys.argv:
        import json
        print(json.dumps({"TERRITORIOS": TERRITORIOS, "APELIDOS": APELIDOS},
                         ensure_ascii=False, indent=1))
