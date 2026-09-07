#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
A PORTA DE ADMISSAO — a peneira comum, e o livro que guarda cada nao.

O censo mediu o buraco com numero: **um** ficheiro em toda a coleta decide o que
presta (`coleta/youtube_relevancia.py`), para **cinco** veiculos. Nos outros
quatro canais nao ha peneira nenhuma. O caminho de hoje e:

    colher -> carimbar -> guardar TUDO -> inteligencia

e nao:

    colher -> carimbar -> separar -> guardar o que passou -> inteligencia

A tentacao era escrever `instagram_relevancia.py`, `linkedin_relevancia.py`,
`facebook_relevancia.py`. Seriam quatro arquitecturas independentes para um
problema que e um so — e daqui a um ano seriam quatro leis diferentes sobre a
mesma pergunta, cada uma com o seu bug.

AS TRES REGRAS QUE ESTA PORTA NAO QUEBRA
-----------------------------------------

1 · RELEVANCIA NAO E UM BOOLEANO UNIVERSAL.
    O mesmo video pode ser ouro para Ciencia, ruido para Concorrencia e NAO_SEI
    para Regulatorio. Guardar `relevante=true` no item obriga a escolher um
    dono para a verdade, e o segundo universo que perguntar recebe a resposta
    do primeiro. Por isso a decisao e sempre do PAR (item, universo), e o mesmo
    bruto pode ter tres decisoes diferentes ao mesmo tempo, todas certas.

2 · ERRO NAO VIRA NAO.
    «Nao consegui ler o ficheiro» nao e «li e nao serve». Se a ferramenta
    falhou, o estado e ERRO, e o item volta a fila — nao morre com um carimbo
    de rejeitado que ninguem vai reabrir.

3 · AUSENCIA DE PROVA NAO VIRA NAO.
    NAO_SEI e uma resposta legitima e fica escrita como tal. Empurrar o NAO_SEI
    para o NAO faz a coleta encolher sozinha, sem ninguem ter decidido isso — e
    o encolhimento nao aparece em lado nenhum, porque um «nao» parece uma
    decisao tomada.

O LIVRO DE DECISOES
-------------------
`discarded=true` nao serve para nada: nao diz porque, nem por qual regra, nem
com que prova, nem se a regra mudou entretanto. Descarte sem testemunha e
trabalho perdido duas vezes — perde-se o item, e perde-se a informacao de que
aquela fonte entrega lixo. Na coleta seguinte gasta-se maquina para redescobrir
exatamente a mesma coisa.

Cada decisao guarda: o item, o universo, a regra, a versao da regra, o
resultado, o motivo em palavras, a prova, e de que corrida veio. Com a versao
guardada, quando a regra mudar da para reprocessar so o que ela decidiu.

SAIDA: data/samples/LIVRO-DE-DECISOES.json
"""

from __future__ import annotations

import json
import sys
from dataclasses import dataclass, asdict, field
from datetime import datetime, timezone
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
import _gavetas  # noqa: E402,F401

LIVRO = RAIZ / "data" / "samples" / "LIVRO-DE-DECISOES.json"

# ── OS QUATRO RESULTADOS, E SO ESTES ────────────────────────────────────────
SIM = "SIM"                      # entra
NAO = "NAO"                      # olhei e nao serve para ESTE universo
NAO_SEI = "NAO_SEI"              # nao ha prova suficiente para dizer sim ou nao
NAO_SE_APLICA = "NAO_SE_APLICA"  # a pergunta nao faz sentido para este item
ERRO = "ERRO"                    # nao consegui olhar — NAO e uma rejeicao

RESULTADOS = (SIM, NAO, NAO_SEI, NAO_SE_APLICA, ERRO)

# A versao da regra vive aqui e sobe quando a regra muda. E o que permite dizer
# «reprocessa tudo o que a versao 1 rejeitou» sem reprocessar o resto.
VERSAO_DA_REGRA = "1"


@dataclass
class Decisao:
    item: str
    universo: str
    resultado: str
    regra: str
    motivo: str
    evidencia: dict = field(default_factory=dict)
    versao: str = VERSAO_DA_REGRA
    corrida: str = "NAO SEI"
    quando: str = ""

    def __post_init__(self):
        if self.resultado not in RESULTADOS:
            raise ValueError(f"resultado «{self.resultado}» nao existe. "
                             f"Ha: {', '.join(RESULTADOS)}")
        self.quando = self.quando or datetime.now(timezone.utc).strftime(
            "%Y-%m-%dT%H:%M:%SZ")


# ── AS PERGUNTAS DA PORTA ───────────────────────────────────────────────────
# Cada uma devolve (resultado, motivo, evidencia). A ordem importa: as que
# apuram se DA PARA OLHAR vem primeiro, porque nao se julga o que nao se leu.
# NAO E UMA COISA COLHIDA — E UM REGISTO SOBRE A COLETA.
#
# Sao duas especies diferentes, e confundi-las escondeu o achado mais duro desta
# missao. Ao ligar a porta pela primeira vez a uma colheita real, 253 registos
# sairam todos barrados na primeira pergunta, e o motivo dizia so «veio sem
# texto». Parecia um defeito da peneira. Nao era.
#
#     `RESEARCHER-CORPUS` guarda 12 PESSOAS com o campo MATERIALS_FOUND = 124.
#     Guarda a CONTAGEM dos materiais. Nao guarda os materiais.
#
# Um registo destes nao e um item mal colhido: e outra especie de coisa — a
# ficha de onde se pode coletar, ou o resumo do que se coletou. Chamar-lhe
# NAO_SEI e dar uma resposta educada a uma pergunta que nao se devia ter feito,
# e por isso ninguem vai investigar.
NAO_E_ITEM = (
    # ficha de conta: onde se pode coletar
    "ACCOUNT_HANDLE", "ACCOUNT_URL", "ACCOUNT_IDENTITY_STATE",
    "COLLECTION_AUTHORIZED", "ELIGIBLE_FOR_COMPANY_LOCAL_BATCH", "ANCHOR_KIND",
    # ficha de pessoa com contagem: o resumo do que se coletou
    "PERSON_ID", "MATERIALS_FOUND", "ORCID_WORKS_DECLARED", "IDENTITY_STATE",
    "PUBLIC_CHANNELS_DECLARED",
)
CHEIRA_A_CATALOGO = NAO_E_ITEM  # nome antigo, mantido para nao partir chamadas


def _legivel(item: dict) -> tuple:
    t = item.get("texto") or item.get("title") or item.get("nome") or ""
    if item.get("erro_de_leitura"):
        return ERRO, ("nao consegui ler este item — a ferramenta falhou. "
                      "Isto nao e uma rejeicao: ninguem chegou a olhar."), \
               {"erro": str(item["erro_de_leitura"])[:200]}
    if not str(t).strip():
        # SEPARAR «VEIO VAZIO» DE «NAO E UM ITEM».
        # A primeira vez que a porta correu sobre uma colheita real, os 78
        # registos sairam todos NAO_SEI — e isso escondia o que importava: nao
        # eram publicacoes mal colhidas, eram FICHAS DE CONTA. A pasta guardava
        # o catalogo de quem se pode coletar, nao o que foi coletado.
        # NAO_SEI ali era uma resposta educada a uma pergunta que nao se devia
        # ter feito, e por isso ninguem ia investigar.
        marcas = [k for k in CHEIRA_A_CATALOGO if k in item]
        if marcas:
            return NAO_SE_APLICA, (
                "isto nao e uma coisa colhida: e uma ficha de conta ou de "
                "catalogo. A pergunta «serve para este universo?» nao se aplica "
                "— o que esta aqui e o registo de ONDE se pode coletar, nao o "
                "que se coletou."), {"campos_de_catalogo": marcas[:4]}
        return NAO_SEI, ("o item veio sem texto nenhum. Sem conteudo nao da para "
                         "dizer se serve — e «nao consegui ver» nao e «nao serve»."), {}
    return SIM, "tem conteudo legivel", {"caracteres": len(str(t))}


def _tem_origem(item: dict) -> tuple:
    fonte = item.get("source_id") or item.get("fonte") or item.get("url")
    if not fonte:
        return NAO_SEI, ("nao da para dizer de onde este item veio. Um item sem "
                         "origem nao se consegue conferir depois, e um numero que "
                         "nao se confere e um palpite bem vestido."), {}
    return SIM, "a origem esta declarada", {"origem": str(fonte)[:160]}


def _tem_quando(item: dict) -> tuple:
    q = item.get("fact_time") or item.get("data") or item.get("published_at")
    if not q:
        return NAO_SEI, ("o item nao diz quando o fato aconteceu. Fica NAO_SEI, "
                         "nao NAO: falta a prova, nao o valor."), {}
    return SIM, "tem tempo do fato", {"quando": str(q)[:40]}


def _do_universo(item: dict, universo: str, palavras: list) -> tuple:
    """Pertence ao universo pedido? A resposta muda com o universo — de proposito."""
    if not palavras:
        return NAO_SE_APLICA, (f"nao ha regra escrita do que conta como «{universo}». "
                               f"Sem regra, esta porta nao inventa uma."), {}
    texto = " ".join(str(item.get(k) or "") for k in
                     ("texto", "title", "nome", "topics", "crops", "resumo")).lower()
    achadas = [p for p in palavras if p.lower() in texto]
    if achadas:
        return SIM, (f"fala de {', '.join(achadas[:4])} — que e do que «{universo}» "
                     f"trata"), {"palavras": achadas[:8]}
    return NAO, (f"nao encontrei nada de «{universo}» neste item. Isto e um NAO "
                 f"para ESTE universo — o mesmo item pode ser SIM noutro."), {}


PERGUNTAS_DO_UNIVERSO = {
    "T7": ["estudo", "ensaio", "pesquisa", "doi", "orcid", "revista", "artigo",
           "universidade", "instituto", "publicacao"],
    "T9": ["lancamento", "campanha", "produto", "concorrente", "anuncio", "evento"],
    "T4": ["autorizacao", "registro", "rotulo", "bula", "ministero", "decreto"],
    "T3": ["praga", "doenca", "fungo", "inseto", "infestacao", "sintoma"],
}


def decidir(item: dict, universo: str, corrida: str = "NAO SEI") -> Decisao:
    """A porta. Uma decisao por par (item, universo) — nunca uma por item."""
    for nome, f in (("legivel", _legivel), ("origem", _tem_origem),
                    ("tempo do fato", _tem_quando)):
        r, motivo, ev = f(item)
        if r != SIM:
            return Decisao(item=str(item.get("id") or item.get("url") or "?"),
                           universo=universo, resultado=r, regra=nome,
                           motivo=motivo, evidencia=ev, corrida=corrida)

    r, motivo, ev = _do_universo(item, universo, PERGUNTAS_DO_UNIVERSO.get(universo, []))
    return Decisao(item=str(item.get("id") or item.get("url") or "?"),
                   universo=universo, resultado=r, regra="pertence ao universo",
                   motivo=motivo, evidencia=ev, corrida=corrida)


def escrever(decisoes: list) -> int:
    """Junta ao livro; nunca reescreve o que ja estava la."""
    d = {"DECISOES": []}
    if LIVRO.is_file():
        try:
            d = json.loads(LIVRO.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            pass
    d.setdefault("DECISOES", []).extend(asdict(x) for x in decisoes)
    LIVRO.parent.mkdir(parents=True, exist_ok=True)
    LIVRO.write_text(json.dumps(d, ensure_ascii=False, indent=2) + "\n",
                     encoding="utf-8")
    return len(d["DECISOES"])


# ── A FRONTEIRA DESTA MISSAO ────────────────────────────────────────────────
def pronto_para_inteligencia(item: dict, decisao: Decisao) -> dict:
    """O contrato de saida. A inteligencia recebe ISTO, e mais nada.

    Ela nao sabe — nem precisa de saber — qual raspador trouxe, qual API, qual
    veiculo, nem que remendo foi preciso pelo caminho. Se amanha o executor for
    outro, este contrato nao muda, e nenhum consumidor a jusante mexe uma linha.
    """
    if decisao.resultado != SIM:
        raise ValueError(f"item {decisao.item} nao passou a porta ({decisao.resultado})")
    return {
        "ESTADO": "PRONTO_PARA_INTELIGENCIA",
        "ITEM_ID": decisao.item,
        "UNIVERSO": decisao.universo,
        "TEXTO": item.get("texto") or item.get("title") or "",
        "SOURCE_ID": item.get("source_id") or item.get("fonte") or "NAO SEI",
        "SOURCE_LOCATION": item.get("source_location", "NAO SEI"),
        "FACT_LOCATION": item.get("fact_location", "NAO SEI"),
        "FACT_TIME": item.get("fact_time") or item.get("data") or "NAO SEI",
        "CAPTURED_AT": item.get("captured_at", "NAO SEI"),
        "CORRIDA": decisao.corrida,
        "ADMITIDO_POR": f"{decisao.regra} v{decisao.versao}",
    }


if __name__ == "__main__":
    exemplo = {"id": "demo-1", "texto": "Ensaio de campo publicado com DOI",
               "source_id": "IT-T7-001", "fact_time": "2026-05-02"}
    d = decidir(exemplo, "T7", corrida="demo")
    print(f"{d.resultado} · {d.regra} · {d.motivo}")
    print(json.dumps(pronto_para_inteligencia(exemplo, d), ensure_ascii=False, indent=2))
