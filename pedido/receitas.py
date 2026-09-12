#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
A RECEITA — como se atende um pedido, sem que quem pede precise de saber.

O conhecimento de «como se coleta ciencia italiana» estava espalhado por
cabecalho de script, README, prompt de aba e `if` solto dentro do coletor.
Espalhado assim, ele nao se consulta: redescobre-se. E redescobrir custa uma
coleta inteira de cada vez.

Aqui ele fica num sitio so, e — isto e o essencial — **derivado, nao escrito**:

    o assunto pedido (T7)
        -> as fontes que o atlas ja classificou nesse territorio
        -> a rota que a ficha de cada fonte declara
        -> o executor que sabe percorrer essa rota
        -> os contratos que ele e obrigado a cumprir
        -> o que se espera de volta

Se amanha alguem escrever a ficha de uma fonte nova, ela entra na receita
sozinha. Nao ha lista para atualizar a mao — listas a mao envelhecem caladas.

O NAO SEI E O PRODUTO MAIS IMPORTANTE DAQUI
-------------------------------------------
O censo mediu: **35 das 54 fontes italianas tem `access_method: NAO SEI`**. A
ficha diz que a fonte existe e o que ela tem, mas nao diz como se chega la.

Um planeador honesto nao pode esconder isso. Se o pedido tocar 12 fontes e a
casa souber percorrer 3, o plano diz «3 de 12», e nomeia as outras 9. A
alternativa — devolver so as 3 e calar as 9 — faz uma coleta parcial parecer
completa, que e o erro mais caro que este sistema pode cometer.
"""

from __future__ import annotations

import json
import os
import sys
from dataclasses import dataclass, field
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
import _gavetas  # noqa: E402,F401 — poe as gavetas no caminho de importacao

from pedido import Pedido, ALVOS  # noqa: E402
import relevancia_da_fonte as rel  # noqa: E402 — o portao antes do gasto

FONTES_MEDIDAS = RAIZ / "system-map" / "data" / "sources.generated.json"

# ── OS EXECUTORES QUE A CASA TEM, E O QUE CADA UM SABE PERCORRER ────────────
# Isto e a unica lista escrita a mao deste ficheiro, e e curta de proposito:
# sao 18 executores medidos pelo censo, e so estes declaram saber percorrer uma
# rota inteira ate ao fim. Cada linha diz o que o executor faz e como se chama
# — nunca o chamador precisa de saber isto.
#
# Um executor entra aqui quando prova que percorre a rota; sai quando deixa de
# a percorrer. Nao ha «talvez».
# ── O QUE CADA EXECUTOR DEVOLVE, E O QUE ISSO E ─────────────────────────────
# `larga_em` diz ONDE. A chave `retorno` diz O QUE — e e a COL-LAW-505 a entrar
# no runtime.
#
#     ENVELOPE   o ficheiro onde a CORRIDA declara o que produziu.
#                E a unica origem possivel de COLHEITA.
#
#     LEGADO     {caminho: ESPECIE} para o que ja esta em disco e cujo produtor
#                nao corre offline. SO PODE DECLARAR SUPORTE: manifesto,
#                catalogo, recibo de execucao ou plano.
#
# ⚠️ POR QUE O LEGADO NAO PODE DECLARAR COLHEITA. Uma declaracao escrita aqui e
# feita ANTES da corrida e envelhece sozinha — o proprio `larga_em` prova isso,
# com dois caminhos a apontar para pastas que nao existem sem ninguem notar. Se
# esta chave pudesse dizer «aqui ha colheita», uma linha desactualizada mandava
# suporte para o ingresso outra vez, e teriamos trocado uma heuristica por um
# literal. `leis/retorno_da_coleta.py::envelope_do_legado` recusa, e escreve o
# motivo no recibo.
#
#     DECLARAR SUPORTE E INOFENSIVO MESMO QUANDO ERRADO: SUPORTE NAO ATRAVESSA.
#     DECLARAR COLHEITA NAO E — E POR ISSO NAO SE PODE.
EXECUTORES = {
    "T7": [{
        "id": "corpus-pesquisador",
        # F3 · o retorno e o CATALOGO das pessoas de quem se PODE colher
        # obra — nao as obras. Medido: 12 fichas de pessoa, zero unidades.
        "retorno": {"LEGADO": {
            "data/samples/RESEARCHER-CORPUS-EAME-V1.json": "CATALOG"}},
        "roda": ["coleta/corpus_pesquisador.py", "coletar"],
        # ONDE ELE LARGA o que traz. Sem isto declarado, o orquestrador corre o
        # executor e fica sem saber o que procurar — e a colheita nunca chega a
        # porta de admissao. Foi o que se descobriu ao perguntar «o que o YouTube
        # colhe vai para onde?»: ia para uma pasta que ninguem lia.
        "larga_em": ["data/samples/RESEARCHER-CORPUS-EAME-V1.json"],
        "rotas": ["OpenAlex", "ORCID"],
        "o_que_traz": "obra publicada com data, tipo, veiculo e DOI, e a autoria "
                      "declarada obra a obra",
        "custo": "gratuito",
    }],
    "T4": [{
        "id": "rotulos-oficiais",
        # F3 · o retorno e o MANIFESTO de 163 descargas. Os 163 PDF que ele
        # indexa nao estao nesta arvore: `PAYLOAD = AUSENTE`, e ausencia
        # nao e erro nem e item.
        "retorno": {"LEGADO": {
            "data/raw/IT-ROTULOS/_MANIFESTO.json": "MANIFEST"}},
        "roda": ["coleta/rotulos_baixar.py"],
        "larga_em": ["data/raw/IT-ROTULOS"],
        "rotas": ["registro oficial (HTTP)"],
        "o_que_traz": "o rotulo oficial do produto, como PDF, com a data em que "
                      "foi baixado",
        "custo": "gratuito",
    }],
    "T3": [{
        "id": "eppo",
        # F2 · nunca correu, e o sitio declarado nao existe. Nao ha nada a
        # declarar, e inventar uma especie para um ficheiro inexistente
        # seria a casa a fingir que sabe. Fica sem `retorno`, e o recibo
        # diz porque.
        "roda": ["coleta/eppo_gd.py"],
        "larga_em": ["data/samples/IT-PRAGAS"],
        "rotas": ["EPPO Global Database"],
        "o_que_traz": "a ficha da praga ou doenca, com o nome cientifico e a "
                      "distribuicao declarada",
        "custo": "gratuito",
    }],
    "T2": [{
        "id": "italia-recorrente",
        # F1 · a corrida DECLARA o que produziu. E a unica origem legitima
        # de COLHEITA nesta casa.
        "retorno": {"ENVELOPE": "data/colheita/italia/RETORNO.json"},
        # O COLETOR ITALIANO E NODE, e a rota canonica corre executores com
        # `sys.executable`. Quem entra aqui e o ADAPTER em Python — ele e que
        # sabe chamar o Node, ler o livro append-only e largar a colheita DESTA
        # corrida na lingua da porta. Sem ele, a Italia colhia ha meses e nunca
        # passava por `coleta/ingresso.py`: 144 observacoes preservadas num
        # armazem paralelo, zero linhas em `raw_asset`.
        "roda": ["coleta/italy_executor.py"],
        # ⚠️ O ADAPTER PRECISA DA CORRIDA QUE O T-04 CUNHOU, e nao de uma que
        # ele proprio invente. Este campo e OPT-IN: os outros executores nao o
        # declaram e continuam a ser chamados exactamente como antes.
        "recebe_run_id": True,
        "larga_em": ["data/colheita/italia/"],
        # precedente: o T9 ja traduz filtros do pedido em argumentos do executor.
        "argumentos_de_filtros": ["fonte"],
        # A A5.2 autorizou UMA fonte para o primeiro corte. O coletor sabe
        # percorrer sete; registar as sete de uma vez seria prometer o que nao
        # foi provado por aqui.
        "filtros_por_omissao": {"fonte": "IT-T2-002"},
        "rotas": ["HTTP direto"],
        "o_que_traz": "o boletim agrometeorologico da zona, como PDF, com a "
                      "versao do documento e o sitio onde o byte ficou",
        "custo": "gratuito",
    }],
    "T9": [{
        "id": "comunicacao-publica",
        # F3 · seis ficheiros, quatro especies, zero colheita. O
        # `CLASSIFICADO-V1.json` DECLARA um contentor `ITEMS` com
        # `ITEM_COUNT = 0`: e o recibo de uma coleta que nao trouxe nada,
        # e a heuristica antiga saltava-o por estar vazio para agarrar a
        # lista de contas ao lado.
        "retorno": {"LEGADO": {
            "data/samples/COMPETITOR-PUBLIC-COMM/ANCORAS-EVIDENCIA-V1.json": "CATALOG",
            "data/samples/COMPETITOR-PUBLIC-COMM/CONTAS-V1.json": "CATALOG",
            "data/samples/COMPETITOR-PUBLIC-COMM/UNIVERSO-CONTAS-V1.json": "CATALOG",
            "data/samples/COMPETITOR-PUBLIC-COMM/PUBLIC-COMM-FIRST-BATCH-EAME.json": "PLAN",
            "data/samples/COMPETITOR-PUBLIC-COMM/MEDICAO-PRIMEIRO-LOTE-V1.json": "RUN_RECEIPT",
            "data/samples/COMPETITOR-PUBLIC-COMM/CLASSIFICADO-V1.json": "RUN_RECEIPT"}},
        "roda": ["coleta/comunicacao_coleta.py"],
        # O executor precisa de saber a fase e a plataforma, e essas vem do
        # pedido — nao de quem o chama. Declarar aqui QUE filtros viram
        # argumentos e o que permite ao botao do GitHub parar de conhecer a
        # linha de comando do script: ele pede, e a receita traduz.
        "argumentos_de_filtros": ["fase", "plataforma"],
        "filtros_por_omissao": {"fase": "posts"},
        "larga_em": ["data/samples/COMPETITOR-PUBLIC-COMM"],
        "rotas": ["YouTube", "Instagram", "LinkedIn", "Facebook"],
        "o_que_traz": "o que o concorrente publicou em canal aberto, com a data "
                      "e o endereco de onde veio",
        "custo": "pago quando passa pela rota Apify",
    }],
}

# Contratos que NENHUMA coleta pode dispensar. Nao sao conselhos: sem eles o
# item nao consegue provar de onde veio nem quando aconteceu, e a inteligencia
# recebe um numero sem passado.
CONTRATOS_OBRIGATORIOS = (
    ("procedencia", "regras/proveniencia.py",
     "carimba de onde veio, no momento em que entra"),
    ("tempo do fato", "leis/data_clock.py",
     "separa quando o fato aconteceu de quando nos o capturamos"),
    ("lugar do fato", "leis/fato_local.py",
     "separa o lugar de onde veio o documento do lugar onde o fato aconteceu"),
    ("recibo da corrida", "data/samples/RUN-MANIFEST.json",
     "quem correu, quando, com que entrada, quanto trouxe e quanto custou"),
)


def _fontes() -> list:
    """As fontes que a casa ja tem em ficha — atlas europeu e master italiano."""
    if not FONTES_MEDIDAS.is_file():
        return []
    S = json.loads(FONTES_MEDIDAS.read_text(encoding="utf-8"))
    return list(S.get("SOURCES") or []) + list(S.get("MASTER_ITALIANO") or [])


def _sabe_o_caminho(f: dict) -> bool:
    """A ficha diz COMO se chega la? «NAO SEI» nao conta como caminho.

    ⚠️ ISTO E ACESSO, E ACESSO NAO E RELEVANCIA. Uma fonte com caminho escrito
    pode nao servir para nada, e uma fonte bloqueada pode ser a mais relevante
    que ha. As duas perguntas correm lado a lado neste ficheiro, e nenhuma
    responde pela outra:

        ACCESSIBLE != RELEVANT · BLOCKED != IRRELEVANT
    """
    m = str(f.get("access_method") or "").strip()
    return bool(m) and "NAO SEI" not in m.upper() and "NÃO SEI" not in m.upper()


def fonte_nomeada(executor: dict, p: Pedido):
    """→ o SOURCE_ID que ESTE plano vai buscar, ou None quando nao nomeia nenhum.

    Um executor de territorio corre sobre o assunto inteiro; so alguns aceitam
    o filtro `fonte`, e so esses tem um par (fonte, proposito) para julgar.

        NAO SE AUTORIZA GASTO SOBRE UMA FONTE QUE O PLANO NAO NOMEIA.

    Devolver a primeira fonte da lista do assunto seria pior do que devolver
    `None`: o portao julgaria uma fonte que o executor talvez nem visite, e um
    `SIM` nela abriria a porta as outras sete.
    """
    if "fonte" not in (executor.get("argumentos_de_filtros") or []):
        return None
    valores = {**(executor.get("filtros_por_omissao") or {}), **p.filtros}
    v = str(valores.get("fonte") or "").strip()
    return v or None


@dataclass
class Plano:
    """O caminho que se vai percorrer — e o que ficou por saber."""

    pedido: Pedido
    fontes_do_assunto: list = field(default_factory=list)
    com_caminho: list = field(default_factory=list)
    sem_caminho: list = field(default_factory=list)
    executores: list = field(default_factory=list)
    contratos: tuple = CONTRATOS_OBRIGATORIOS
    saida_esperada: str = ""
    # O VEREDITO DO PORTAO DE RELEVANCIA, do dono dele. Este ficheiro nao o
    # calcula: pergunta, transporta e mostra. A regra vive em
    # `leis/relevancia_da_fonte.py`, e nao esta copiada aqui — uma lei em dois
    # sitios diverge, e a partir dai nenhuma das duas vale.
    relevancia: dict = field(default_factory=dict)

    @property
    def da_para_correr(self) -> bool:
        """HA CAMINHO? Continua a ser so isto — e de proposito.

        ⚠️ O PORTAO DE RELEVANCIA NAO ENTRA AQUI. Achatar «nao ha executor» e
        «a fonte nao foi avaliada» num booleano so daria a mesma resposta a
        duas perguntas diferentes, e quem lesse `SEM_CAMINHO` nunca saberia
        qual das duas tinha acontecido. O gasto e barrado noutro campo, com o
        seu proprio nome: `bloqueia_a_corrida`.
        """
        return bool(self.executores)

    @property
    def bloqueia_a_corrida(self) -> bool:
        """→ True quando ha gasto aberto e a relevancia nao o autoriza."""
        return bool(self.relevancia.get("BLOQUEIA_A_CORRIDA"))

    def porque_nao(self) -> str:
        if self.executores:
            return ""
        if not self.fontes_do_assunto:
            return (f"NAO SEI: nenhuma fonte em ficha esta classificada como "
                    f"«{self.pedido.assunto}» ({self.pedido.alvo}). Antes de "
                    f"coletar isto, alguem tem de levantar pelo menos uma fonte.")
        return (f"NAO SEI COMO: ha {len(self.fontes_do_assunto)} fonte(s) de "
                f"«{self.pedido.assunto}», mas nenhum executor desta casa declara "
                f"saber percorrer a rota delas. A ficha diz que existem; ninguem "
                f"escreveu ainda como se chega la.")

    def em_palavras(self) -> str:
        L = [f"PLANO PARA: {self.pedido.em_uma_frase()}", ""]
        L.append(f"  fontes deste assunto em ficha : {len(self.fontes_do_assunto)}")
        L.append(f"  destas, com caminho escrito   : {len(self.com_caminho)}")
        L.append(f"  destas, NAO SEI como se chega : {len(self.sem_caminho)}")
        if self.sem_caminho:
            nomes = ", ".join(x.get("source_id") or x.get("name", "?")
                              for x in self.sem_caminho[:6])
            L.append(f"      ({nomes}{' ...' if len(self.sem_caminho) > 6 else ''})")
        L.append("")
        if self.relevancia:
            r = self.relevancia
            L.append("  portao de relevancia da fonte (antes do gasto):")
            L.append(f"      fonte nomeada pelo plano : {r['SOURCE_ID'] or 'NENHUMA'}")
            L.append(f"      relevancia para {r['PROPOSITO']:<8s} : {r['ESTADO_DA_RELEVANCIA']}")
            L.append(f"      veredito                 : {r['VEREDITO']}")
            gastos = r["FORMAS_DE_GASTO_ABERTAS"]
            L.append(f"      formas de gasto abertas  : "
                     f"{' · '.join(gastos) if gastos else 'nenhuma (observacao barata)'}")
            L.append("")
        if self.executores:
            L.append("  quem vai correr:")
            for e in self.executores:
                L.append(f"      {e['id']}  ->  {' '.join(e['roda'])}")
                L.append(f"          traz: {e['o_que_traz']}")
                L.append(f"          rota: {', '.join(e['rotas'])} · {e['custo']}")
            if self.bloqueia_a_corrida:
                # A CORRIDA ESTA BARRADA, e o plano di-lo no sitio onde alguem
                # o leria — nao so no recibo, depois de nada ter acontecido.
                L.append("")
                L.append(f"  GASTO BARRADO PELO PORTAO DE RELEVANCIA:")
                L.append(f"      {self.relevancia['PORQUE']}")
        else:
            L.append(f"  NAO DA PARA CORRER: {self.porque_nao()}")
        L.append("")
        L.append("  contratos que a corrida tem de cumprir:")
        for nome, onde, porque in self.contratos:
            L.append(f"      {nome:18s} {porque}")
        if self.saida_esperada:
            L.append("")
            L.append(f"  saida esperada: {self.saida_esperada}")
        return "\n".join(L)


def resolver(p: Pedido) -> Plano:
    """Do pedido ao caminho. Tudo medido do atlas; nada adivinhado."""
    pais = (p.filtros.get("pais") or "").upper()
    tema = (p.filtros.get("tema") or "").lower()

    do_assunto = []
    for f in _fontes():
        if str(f.get("territory") or "").upper() != p.alvo:
            continue
        if pais:
            c = str(f.get("country") or "").upper()
            mapa = {"ES": ("ES", "ESPANHA"), "IT": ("IT", "ITALIA"),
                    "FR": ("FR", "FRANCA"), "EU": ("EU", "EUROPA")}
            # EUROPA serve qualquer pais europeu: nao se descarta uma base
            # continental so porque o pedido nomeou um pais dela.
            if c not in mapa.get(pais, (pais,)) and c not in ("EU", "EUROPA"):
                continue
        if tema:
            texto = " ".join(str(f.get(k) or "") for k in
                             ("crops", "topics", "name", "use_case")).lower()
            if tema not in texto:
                continue
        do_assunto.append(f)

    com = [f for f in do_assunto if _sabe_o_caminho(f)]
    sem = [f for f in do_assunto if not _sabe_o_caminho(f)]
    execs = EXECUTORES.get(p.alvo, [])

    # ── O PORTAO DE RELEVANCIA, ANTES DO GASTO ──────────────────────────────
    # ⚠️ ATE AQUI, O UNICO REQUISITO PARA CORRER ERA EXISTIR UMA LINHA EM
    # `EXECUTORES`. Medido: as oito fontes de T9 tem `verdict = NAO SEI`, o
    # executor de T9 declara `custo = «pago quando passa pela rota Apify»`, e o
    # plano dizia «quem vai correr: comunicacao-publica» sem que ninguem
    # tivesse perguntado se alguma delas servia.
    #
    #     FIRST_PRE_SPEND_RELEVANCE_GATE = NONE.
    #
    # A pergunta e feita aqui porque e aqui que o pedido vira fonte e
    # executor — mas a RESPOSTA e do dono da lei, e quem OBEDECE e o
    # orquestrador, que e quem gasta.
    relevancia = {}
    if execs:
        e = execs[0]
        relevancia = rel.portao(
            fonte_nomeada(e, p), p.alvo, rel.ler_livro(str(RAIZ)),
            custo=e.get("custo"), acionamento=p.acionamento, escopo=p.escopo)

    return Plano(
        pedido=p,
        fontes_do_assunto=do_assunto,
        com_caminho=com,
        sem_caminho=sem,
        executores=execs,
        relevancia=relevancia,
        saida_esperada=(f"itens de «{p.assunto}» com procedencia, tempo do fato e "
                        f"lugar do fato carimbados, prontos para a porta de admissao"),
    )


if __name__ == "__main__":
    from pedido import de_uma_frase
    frase = " ".join(sys.argv[1:]) or "colete materiais de pesquisadores"
    print(resolver(de_uma_frase(frase)).em_palavras())
