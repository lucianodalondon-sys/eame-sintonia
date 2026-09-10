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

FONTES_MEDIDAS = RAIZ / "system-map" / "data" / "sources.generated.json"

# ── OS EXECUTORES QUE A CASA TEM, E O QUE CADA UM SABE PERCORRER ────────────
# Isto e a unica lista escrita a mao deste ficheiro, e e curta de proposito:
# sao 18 executores medidos pelo censo, e so estes declaram saber percorrer uma
# rota inteira ate ao fim. Cada linha diz o que o executor faz e como se chama
# — nunca o chamador precisa de saber isto.
#
# Um executor entra aqui quando prova que percorre a rota; sai quando deixa de
# a percorrer. Nao ha «talvez».
EXECUTORES = {
    "T7": [{
        "id": "corpus-pesquisador",
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
        "roda": ["coleta/rotulos_baixar.py"],
        "larga_em": ["data/raw/IT-ROTULOS"],
        "rotas": ["registro oficial (HTTP)"],
        "o_que_traz": "o rotulo oficial do produto, como PDF, com a data em que "
                      "foi baixado",
        "custo": "gratuito",
    }],
    "T3": [{
        "id": "eppo",
        "roda": ["coleta/eppo_gd.py"],
        "larga_em": ["data/samples/IT-PRAGAS"],
        "rotas": ["EPPO Global Database"],
        "o_que_traz": "a ficha da praga ou doenca, com o nome cientifico e a "
                      "distribuicao declarada",
        "custo": "gratuito",
    }],
    "T2": [{
        "id": "italia-recorrente",
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
        "roda": ["coleta/comunicacao_coleta.py"],
        # O executor precisa de saber a fase e a plataforma, e essas vem do
        # pedido — nao de quem o chama. Declarar aqui QUE filtros viram
        # argumentos e o que permite ao botao do GitHub parar de conhecer a
        # linha de comando do script: ele pede, e a receita traduz.
        # `fase` aceita hoje: `contratos` (gratis, le o schema do ator),
        # `posts` (a coleta paga) e `transcrever` — a FALA dos videos ja
        # coletados, que corre local e custa zero dolares.
        #
        # A fala entrou por AQUI, e nao como executor novo, de proposito: o
        # orquestrador chama apenas o PRIMEIRO executor de cada alvo, portanto
        # um segundo registo em T9 nunca seria aberto e ficaria a mentir nesta
        # lista. Uma capacidade, uma porta.
        "argumentos_de_filtros": ["fase", "plataforma"],
        "filtros_por_omissao": {"fase": "posts"},
        "larga_em": ["data/samples/COMPETITOR-PUBLIC-COMM",
                     "data/samples/REEL-TRANSCRICOES"],
        "rotas": ["YouTube", "Instagram", "LinkedIn", "Facebook"],
        "o_que_traz": "o que o concorrente publicou em canal aberto, com a data "
                      "e o endereco de onde veio — e, com `fase=transcrever`, a "
                      "FALA do video, num campo separado da legenda",
        "custo": "pago quando passa pela rota Apify; `transcrever` custa zero "
                 "dolares e paga-se em tempo de maquina",
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
    """A ficha diz COMO se chega la? «NAO SEI» nao conta como caminho."""
    m = str(f.get("access_method") or "").strip()
    return bool(m) and "NAO SEI" not in m.upper() and "NÃO SEI" not in m.upper()


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

    @property
    def da_para_correr(self) -> bool:
        return bool(self.executores)

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
        if self.executores:
            L.append("  quem vai correr:")
            for e in self.executores:
                L.append(f"      {e['id']}  ->  {' '.join(e['roda'])}")
                L.append(f"          traz: {e['o_que_traz']}")
                L.append(f"          rota: {', '.join(e['rotas'])} · {e['custo']}")
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

    return Plano(
        pedido=p,
        fontes_do_assunto=do_assunto,
        com_caminho=com,
        sem_caminho=sem,
        executores=execs,
        saida_esperada=(f"itens de «{p.assunto}» com procedencia, tempo do fato e "
                        f"lugar do fato carimbados, prontos para a porta de admissao"),
    )


if __name__ == "__main__":
    from pedido import de_uma_frase
    frase = " ".join(sys.argv[1:]) or "colete materiais de pesquisadores"
    print(resolver(de_uma_frase(frase)).em_palavras())
