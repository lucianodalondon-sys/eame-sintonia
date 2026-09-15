#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O PEDIDO DE COLETA — a unica porta de entrada.

    «colete materiais de pesquisadores»
    «colete materiais novos de pesquisadores da Espanha sobre cereais»

Quem pede diz O QUE quer. Quem atende decide COMO. Este ficheiro e o contrato
entre os dois, e existe por um motivo medido: o censo encontrou **79 pontos de
entrada** em 92 ficheiros de coleta. Setenta e nove maneiras de comecar uma
coleta nao sao «uma coleta»: sao setenta e nove. Cada aba, cada ferramenta
futura, cada peca de inteligencia que quisesse dado tinha de aprender o nome de
um script — e ficava presa a ele.

    NENHUM CHAMADOR DEVE CONHECER `coletor_x.py`.

Trocar o executor por outro melhor nao pode obrigar ninguem a mudar o pedido.

AS QUATRO PERGUNTAS DO PEDIDO
------------------------------
    ALVO         o que se quer. Nao e o script, nao e a fonte: e o assunto
    ACIONAMENTO  quem mandou — pessoa, relogio, ou acontecimento
    ESCOPO       quanto se quer — desta vez, so o novo, ou tudo
    FILTROS      onde, quando, sobre o que

ACIONAMENTO E ESCOPO SAO PERGUNTAS DIFERENTES, e junta-las e um erro comum:
uma coleta TOTAL pode ser MANUAL (alguem clica e pede tudo), e uma coleta
INCREMENTAL pode ser AGENDADA. Sao dois eixos, nao um.

O QUE NAO SE FINGE
------------------
`AUTOMATICO_EVENTO` esta declarado porque a arquitetura o preve, mas o censo
mediu: **nao existe hoje** nenhum disparo por acontecimento neste repositorio.
Aceitar um pedido assim e devolver uma promessa que ninguem cumpre. Por isso
ele e recusado com o motivo escrito, em vez de aceite em silencio.
"""

from __future__ import annotations

import json
import os
import re
import sys
from dataclasses import dataclass, field, asdict

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import _gavetas  # noqa: E402,F401 — poe as gavetas no caminho de importacao

# ── ACIONAMENTO: quem mandou coletar ────────────────────────────────────────
MANUAL = "MANUAL"                        # uma pessoa pediu
AGENDADO = "AGENDADO"                    # o relogio pediu
AUTOMATICO_EVENTO = "AUTOMATICO_EVENTO"  # um acontecimento pediu — AINDA NAO EXISTE

ACIONAMENTOS = (MANUAL, AGENDADO, AUTOMATICO_EVENTO)
ACIONAMENTO_QUE_EXISTE = (MANUAL, AGENDADO)

# ── ESCOPO: quanto se quer ──────────────────────────────────────────────────
PONTUAL = "PONTUAL"          # so isto, agora
INCREMENTAL = "INCREMENTAL"  # so o que apareceu desde a ultima vez
TOTAL = "TOTAL"              # tudo, do inicio

ESCOPOS = (PONTUAL, INCREMENTAL, TOTAL)

# ── ALVO: o assunto que se quer ─────────────────────────────────────────────
# ⚠️ ESTE FICHEIRO JA DECLAROU A SUA PROPRIA TABELA, E ELA ESTAVA ERRADA.
#
# O comentario que aqui estava dizia, com todas as letras, a coisa certa:
#
#     «NAO E UMA LISTA INVENTADA. Sao os territorios que o atlas de fontes ja
#      usa (T1..T13) ... Inventar aqui uma segunda lista de assuntos criaria
#      duas verdades sobre a mesma pergunta.»
#
# E depois inventava-a na mesma. Cinco codigos diziam aqui uma coisa e no Atlas
# outra — `T5`, `T7`, `T10`, `T11`, `T12` — e `T6` e `T8` nem existiam nesta
# copia. Medido ao vivo, com selecao real:
#
#     «colete ciencia da italia»  ->  12 COOPERATIVAS (IT-T7-001..012)
#
# porque `T7` aqui era «Ciencia e ensaio» e no Atlas e TECHNICAL NETWORK. As
# cinco fontes cientificas italianas reais ficavam invisiveis ao pedido.
#
#     UMA INTENCAO ESCRITA NO COMENTARIO NAO E UMA LEI NO CODIGO.
#
# Agora nao ha tabela nenhuma aqui. O dono e `leis/territorios.py`, que LE o
# Atlas — a mesma tabela que qualquer pessoa le, e a mesma que `scan_sources.py`
# usa para escrever a ficha de cada fonte.
#
#     ONE CONCEPT -> ONE OWNER.
import territorios as terr  # noqa: E402

#: `{codigo: nome}`, do dono. Mantem-se o nome `ALVOS` porque e ele que os
#: chamadores desta casa ja conhecem — o que muda e de onde o valor vem.
ALVOS = {c: d["NOME"] for c, d in terr.TERRITORIOS.items()}

#: As palavras que uma pessoa usa. Tambem do dono: guardadas longe da tabela,
#: foi assim que `"ciencia" -> T7` sobreviveu a `T7` ter mudado de significado.
APELIDOS = terr.APELIDOS

# ── ESTADOS DA VIDA DE UM ITEM ──────────────────────────────────────────────
# Poucos, e escolhidos para que seja IMPOSSIVEL confundir duas coisas que o
# censo mostrou estarem confundidas hoje:
#
#     REJEITADO nao e ERRO. Rejeitado e «olhei e nao serve»; erro e «nao
#     consegui olhar». Tratar os dois como o mesmo faz uma falha de rede
#     parecer um julgamento, e a fonte leva a culpa pela ferramenta.
#
#     NAO_SEI nao e REJEITADO. Ausencia de prova nao e prova de ausencia.
#     Sem esta separacao, tudo o que nao se conseguiu confirmar vira «nao», e
#     a coleta encolhe sozinha sem ninguem decidir isso.
COLHIDO = "COLHIDO"
CARIMBADO = "CARIMBADO"
NA_PORTA = "NA_PORTA"
ACEITE = "ACEITE"
REJEITADO = "REJEITADO"
NAO_SEI = "NAO_SEI"
PREPARADO = "PREPARADO"
PRONTO_PARA_INTELIGENCIA = "PRONTO_PARA_INTELIGENCIA"
ERRO = "ERRO"

ESTADOS = (COLHIDO, CARIMBADO, NA_PORTA, ACEITE, REJEITADO, NAO_SEI,
           PREPARADO, PRONTO_PARA_INTELIGENCIA, ERRO)


class PedidoInvalido(ValueError):
    """Pedido que nao se pode atender — e o motivo vem escrito na mensagem."""


def _limpa(t: str) -> str:
    t = (t or "").strip().lower()
    for de, para in (("á", "a"), ("ã", "a"), ("â", "a"), ("é", "e"), ("ê", "e"),
                     ("í", "i"), ("ó", "o"), ("ô", "o"), ("õ", "o"), ("ú", "u"),
                     ("ç", "c")):
        t = t.replace(de, para)
    return re.sub(r"\s+", " ", t)


def alvo_de(texto: str) -> str:
    """Traduz o que uma pessoa escreveu para o codigo de territorio do atlas.

    Devolve o codigo (T7) ou levanta PedidoInvalido com a lista do que existe —
    nunca adivinha. Adivinhar aqui significaria coletar o assunto errado e so
    descobrir isso depois de gastar maquina.
    """
    t = _limpa(texto)
    if t.upper() in ALVOS:
        return t.upper()
    if t in APELIDOS:
        return APELIDOS[t]
    for nome, codigo in ALVOS.items():
        if _limpa(codigo) == t:
            return nome
    # ultimo recurso: o apelido esta dentro da frase («materiais de pesquisadores
    # da Espanha»). Prefere-se o apelido mais longo, que e o mais especifico.
    for ap in sorted(APELIDOS, key=len, reverse=True):
        if ap in t:
            return APELIDOS[ap]
    raise PedidoInvalido(
        f"NAO SEI que assunto e «{texto}». Os que existem sao: "
        + ", ".join(f"{k} ({v})" for k, v in sorted(ALVOS.items())))


@dataclass
class Pedido:
    """O que se quer, sem dizer como se faz."""

    alvo: str
    acionamento: str = MANUAL
    escopo: str = PONTUAL
    filtros: dict = field(default_factory=dict)

    def __post_init__(self):
        self.alvo = alvo_de(self.alvo)

        if self.acionamento not in ACIONAMENTOS:
            raise PedidoInvalido(
                f"acionamento «{self.acionamento}» nao existe. "
                f"Ha: {', '.join(ACIONAMENTOS)}")
        if self.acionamento == AUTOMATICO_EVENTO:
            # Ver o cabecalho: nao se aceita o que nao se sabe cumprir.
            raise PedidoInvalido(
                "AUTOMATICO_EVENTO ainda nao existe neste repositorio: nenhum "
                "disparo por acontecimento foi medido. Peca MANUAL ou AGENDADO "
                "— aceitar este pedido seria prometer o que ninguem cumpre.")

        if self.escopo not in ESCOPOS:
            raise PedidoInvalido(
                f"escopo «{self.escopo}» nao existe. Ha: {', '.join(ESCOPOS)}")

        if not isinstance(self.filtros, dict):
            raise PedidoInvalido("os filtros sao um dicionario, mesmo que vazio")

    @property
    def assunto(self) -> str:
        return ALVOS[self.alvo]

    def em_uma_frase(self) -> str:
        f = " · ".join(f"{k}={v}" for k, v in sorted(self.filtros.items()))
        return (f"{self.assunto} ({self.alvo}) · {self.escopo} · "
                f"pedido {self.acionamento.lower()}" + (f" · {f}" if f else ""))

    def para_json(self) -> dict:
        return asdict(self)

    @staticmethod
    def de_json(d: dict) -> "Pedido":
        return Pedido(alvo=d["alvo"], acionamento=d.get("acionamento", MANUAL),
                      escopo=d.get("escopo", PONTUAL), filtros=d.get("filtros") or {})


def de_uma_frase(frase: str) -> Pedido:
    """«colete materiais novos de pesquisadores da Espanha sobre cereais».

    Le a frase e devolve um Pedido. O que nao consegue ler, NAO INVENTA: fica
    de fora, e o plano dira o que ficou por saber.
    """
    t = _limpa(frase)
    filtros = {}

    paises = {"espanha": "ES", "italia": "IT", "franca": "FR", "europa": "EU"}
    for nome, sigla in paises.items():
        if nome in t:
            filtros["pais"] = sigla
            break

    temas = ("cereais", "trigo", "milho", "videira", "oliveira", "tomate",
             "arroz", "citrinos", "batata")
    achados = [x for x in temas if x in t]
    if achados:
        filtros["tema"] = achados[0]

    # «novos» quer dizer: so o que apareceu desde a ultima vez.
    escopo = INCREMENTAL if re.search(r"\bnovos?\b|\brecentes?\b", t) else PONTUAL
    if re.search(r"\btudo\b|\btodos?\b|\bcompleta\b", t):
        escopo = TOTAL

    return Pedido(alvo=frase, acionamento=MANUAL, escopo=escopo, filtros=filtros)


if __name__ == "__main__":
    import sys
    frase = " ".join(sys.argv[1:]) or "colete materiais de pesquisadores"
    try:
        p = de_uma_frase(frase)
    except PedidoInvalido as e:
        print(f"PEDIDO RECUSADO: {e}")
        raise SystemExit(1)
    print(f"PEDIDO ACEITE · {p.em_uma_frase()}")
    print(json.dumps(p.para_json(), ensure_ascii=False, indent=2))
