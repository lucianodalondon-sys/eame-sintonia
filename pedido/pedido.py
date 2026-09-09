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
import re
from dataclasses import dataclass, field, asdict

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
# NAO E UMA LISTA INVENTADA. Sao os territorios que o atlas de fontes ja usa
# (T1..T13) — a mesma taxonomia com que as 54 fontes italianas e as 23 do atlas
# europeu ja estao classificadas. Inventar aqui uma segunda lista de assuntos
# criaria duas verdades sobre a mesma pergunta.
#
# Os apelidos existem porque uma pessoa nao diz «T7»: diz «pesquisadores».
ALVOS = {
    "T1": "Cultura e producao",
    "T2": "Clima e tempo",
    "T3": "Praga e doenca",
    "T4": "Regulatorio",
    "T5": "Preco e mercado",
    "T7": "Ciencia e ensaio",
    "T9": "Concorrente",
    "T10": "Politica e subsidio",
    "T11": "Solo e agua",
    "T12": "Substancia ativa",
    "T13": "Outro",
}

APELIDOS = {
    "pesquisadores": "T7", "materiais de pesquisadores": "T7",
    "pesquisador": "T7", "ciencia": "T7", "artigos": "T7",
    "artigos cientificos": "T7", "ensaio": "T7",
    "concorrentes": "T9", "concorrente": "T9", "competidores": "T9",
    "regulatorio": "T4", "rotulos": "T4", "registro": "T4",
    "praga": "T3", "pragas": "T3", "doenca": "T3", "doencas": "T3",
    "clima": "T2", "tempo": "T2",
    "preco": "T5", "precos": "T5", "mercado": "T5",
    "cultura": "T1", "producao": "T1", "cereais": "T1",
    "politica": "T10", "subsidio": "T10",
    "solo": "T11", "agua": "T11",
    "substancia ativa": "T12", "moa": "T12",
}

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
