#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""A PONTE CORRE SOZINHA — o observador do livro do bot.

    UMA PONTE QUE SO ATRAVESSA QUANDO ALGUEM A MANDA CORRER
    E UMA PONTE LEVADICA COM O GUARDA DE FOLGA.

Os tres sentidos ja estavam provados (ENTRA · NUNCA_ENTROU · SAI). Faltava o
quarto: que a travessia aconteca **sem ninguem mandar**. Ate aqui os unicos
chamadores de `reconciliar_livros` eram dois testes e duas provas.

AS TRES DECISOES DE DESENHO, E O QUE CADA UMA CUSTA
---------------------------------------------------

**ONDE.** Um processo PROPRIO, nesta lane, que observa a lane do bot de fora.
Nao um hook dentro do supervisor dele. Medido em 2026-09-22: o `supervisor.py`
das duas lanes difere em 175 linhas, a lane do bot tem 20 commits proprios, e
o processo nem sequer estava vivo para ser instrumentado. Enxertar codigo desta
lane la dentro era o merge cego que o briefing proibe.

    CUSTO ASSUMIDO: ha um segundo processo para manter de pe. Em troca, a
    ponte sobrevive ao bot morrer — e o bot morre calado (facto 1).

**TRANSPORTE.** Do DISCO, por snapshot atomico, e NAO por Git.

    O BOT ESCREVE NO DISCO E NAO COMMITA.

Medido: 1275 transicoes no disco contra 1270 no commit — cinco decisoes reais
invisiveis para quem le pelo Git, e o ultimo commit dele tinha 3h40. Ler pelo
Git e correcto contra meia-gravacao e **errado contra a realidade**: atravessa
so o que alguem guardou a mao.

    NAO SE COMMITA NA LANE VIVA DO BOT. Quem pode escrever no repositorio de
    um servico a correr e decisao do dono, nao deste ficheiro.

O perigo do disco e ler meia-gravacao. Resolve-se sem cooperacao do bot, em
`snapshot_do_bot()`: le os bytes, confirma que o JSON fecha, e **rele** para
confirmar que nada mudou entre as duas leituras. Um ficheiro apanhado a meio
falha o parse ou muda de tamanho — nos dois casos tenta-se outra vez. O que se
guarda e o `sha256` dos bytes: e ele o corte logico, e e ele que responde
«ja vi este livro?».

**QUANDO.** So quando o `sha256` do livro muda.

    SEM DECISAO NOVA DO BOT, ZERO ESCRITAS E ZERO EVENTOS.

Isto nao e uma optimizacao: e a lei C do briefing, e existe para nao repetir o
defeito que esta medido ao lado. O supervisor do bot, com a fila vazia, grava
um evento `REALIMENTACAO` identico de 15 em 15 segundos — ~5.760 por dia, todos
a dizer «li 476, enfileirei 0». Um log onde tudo se repete e um log onde nada
se ve. Aqui, um tick sem novidade **nao escreve linha nenhuma**; conta-se, e
diz-se no estado.

**E QUANDO CORRER MAL.** A falha nao derruba nada e nao fica engolida:
`FALHAS_CONSECUTIVAS` e `ULTIMO_ERRO` ficam no estado, o intervalo cresce por
backoff, e ao fim de `FALHAS_ATE_GRITAR` o estado passa a `DEGRADADO`. A licao
e do `DISCOVERY_HOOK_ERRO`: 3054 ocorrencias e uma so mensagem — um erro que se
repete calado e um erro que ninguem conserta.

ZERO LLM. Codigo deterministico. Nao toca na lane do bot (so le), nao promove
fora do gate canonico, nao corre Big Collection e nao escreve na Sala.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "curadoria"))

import collection_gate as CG        # noqa: E402
import lifecycle as LC              # noqa: E402
import reconciliar_livros as R      # noqa: E402

# A lane do bot. So LEITURA — nunca se escreve aqui.
LANE_DO_BOT = Path("C:/Users/London1/orca/workspaces/eame-sintonia/source-curator-service-v1")

ESTADO = RAIZ / "curadoria" / "PONTE-AUTOMATICA-STATE.json"
DIARIO = RAIZ / "curadoria" / "PONTE-AUTOMATICA-LOG.ndjson"

INTERVALO_S = 20                # ritmo normal
BACKOFF_MAX_S = 600             # tecto do backoff
FALHAS_ATE_GRITAR = 3           # a partir daqui o estado e DEGRADADO
TENTATIVAS_SNAPSHOT = 5


def agora() -> str:
    return datetime.now(timezone.utc).isoformat()


# ---------------------------------------------------------------------------
# O SNAPSHOT ATOMICO — ficheiro inteiro, sem cooperacao de quem escreve.
# ---------------------------------------------------------------------------
class LeituraInstavel(Exception):
    """O ficheiro mudou entre as duas leituras, ou nunca fechou o JSON."""


def _ler_inteiro(caminho: Path, tentativas: int = TENTATIVAS_SNAPSHOT) -> tuple[dict, str]:
    """(conteudo, sha256) — ou `LeituraInstavel`.

    Duas leituras com o parse pelo meio. Se os bytes forem iguais nas duas E o
    JSON fechar, ninguem escreveu durante a leitura: o que se tem e um ficheiro
    inteiro. Se nao, espera e tenta outra vez — NAO se devolve meio livro.
    """
    ultimo = ""
    for i in range(tentativas):
        try:
            a = caminho.read_bytes()
            doc = json.loads(a.decode("utf-8"))
            b = caminho.read_bytes()
        except (OSError, UnicodeDecodeError, json.JSONDecodeError) as e:
            ultimo = "%s: %s" % (type(e).__name__, e)
            time.sleep(0.25 * (i + 1))
            continue
        if a == b:
            return doc, hashlib.sha256(a).hexdigest()
        ultimo = "os bytes mudaram entre as duas leituras (%d -> %d)" % (len(a), len(b))
        time.sleep(0.25 * (i + 1))
    raise LeituraInstavel("%s: %s" % (caminho.name, ultimo))


def snapshot_do_bot(lane: Path = LANE_DO_BOT) -> dict:
    """O livro, as provas e os contratos do bot, lidos do DISCO, inteiros.

    O `sha256` do livro e o corte logico desta volta: tudo o que o bot escrever
    depois pertence a volta seguinte, nunca a esta.
    """
    cur = lane / "curadoria"
    livro, sha = _ler_inteiro(cur / "LIFECYCLE-LEDGER-V1.json")
    provas: dict = {}
    contratos: dict = {}
    p = cur / "LIFECYCLE-EVIDENCE-V1.json"
    if p.exists():
        d, _ = _ler_inteiro(p)
        provas = {x["EVIDENCE_REF"]: x for x in d.get("PROVAS", [])}
    c = cur / "italy_contracts_curator.json"
    if c.exists():
        d, _ = _ler_inteiro(c)
        contratos = {x["SOURCE_ID"]: x for x in d.get("FONTES", [])}
    ts = livro.get("TRANSICOES", [])
    return {
        "LIVRO": livro, "EVIDENCIAS": provas, "CONTRATOS": contratos,
        "SHA256": sha,
        "TRANSICOES": len(ts),
        "ULTIMA_EM": max((t.get("OBSERVED_AT") or "") for t in ts) if ts else None,
        "LIDO_EM": agora(),
        "ORIGEM": str(cur / "LIFECYCLE-LEDGER-V1.json"),
    }


# ---------------------------------------------------------------------------
# ESTADO E DIARIO
# ---------------------------------------------------------------------------
def saude(*, agora_utc: datetime | None = None, tolerancia: int = 3) -> dict:
    """ESTA VIVO, OU SO EXISTE?

        UM PROCESSO QUE EXISTE E NAO TRABALHA LE-SE COMO SAUDAVEL
        EM TODO O LADO ONDE SE OLHE PARA O PID.

    Foi assim que o supervisor do bot enganou toda a gente: o lock afirmava um
    dono, o PID tinha morrido, e ninguem comparava nada com o relogio. Aqui o
    perigo e o irmao disso — o processo VIVO que deixou de dar voltas. O PID
    continua la, o estado continua a dizer SAUDAVEL, e o ficheiro fica parado
    no tempo.

    A pergunta so se responde com duas coisas ao lado uma da outra: quando foi
    a ultima volta, e que horas sao AGORA. Enquanto isso for conta de cabeca,
    ninguem a faz — e o silencio de um servico parado e igual ao silencio de
    um servico sem novidades.

    `tolerancia` e em multiplos do intervalo: uma volta pode atrasar-se sem
    que isso seja avaria.
    """
    e = estado_lido()
    agora_utc = agora_utc or datetime.now(timezone.utc)
    ultima = e.get("ULTIMA_VOLTA_EM")
    if not ultima:
        return dict(e, VIVACIDADE="NUNCA_DEU_UMA_VOLTA", IDADE_S=None,
                    A_TRABALHAR=False)
    idade = (agora_utc - datetime.fromisoformat(ultima)).total_seconds()
    limite = INTERVALO_S * tolerancia
    trabalha = idade <= limite
    return dict(
        e,
        AGORA=agora_utc.isoformat(),
        IDADE_DA_ULTIMA_VOLTA_S=round(idade, 1),
        LIMITE_S=limite,
        A_TRABALHAR=trabalha,
        VIVACIDADE=("A_TRABALHAR" if trabalha else "PARADO_NO_TEMPO"),
        PORQUE=("deu uma volta ha %.0f s (limite %d s)" % (idade, limite) if trabalha
                else "a ultima volta foi ha %.0f s, e o limite e %d s — o processo "
                     "pode estar vivo e nao estar a trabalhar" % (idade, limite)),
    )


def estado_lido() -> dict:
    if not ESTADO.exists():
        return {"ULTIMO_SHA": None, "VOLTAS": 0, "NOOPS": 0, "TRAVESSIAS": 0,
                "FALHAS_CONSECUTIVAS": 0, "ULTIMO_ERRO": None, "SAUDE": "NUNCA_CORREU"}
    return json.loads(ESTADO.read_text(encoding="utf-8"))


def estado_gravado(e: dict) -> None:
    ESTADO.write_text(json.dumps(e, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")


def anotar(evento: dict) -> None:
    """O diario so recebe o que MUDOU. Um tick sem novidade nao escreve nada —
    e a diferenca entre um registo e um ruido de 5.760 linhas por dia."""
    with DIARIO.open("a", encoding="utf-8") as f:
        f.write(json.dumps(evento, ensure_ascii=False) + "\n")


# ---------------------------------------------------------------------------
# UMA VOLTA
# ---------------------------------------------------------------------------
def uma_volta(*, lane: Path = LANE_DO_BOT, forcar: bool = False) -> dict:
    """Observa, e so atravessa se houver decisao nova. Devolve o que aconteceu.

    NUNCA levanta: uma falha e um facto sobre o mundo, e tem de poder ser
    contada. Quem levantasse excepcao aqui derrubava o ciclo — e o briefing
    pede o contrario.
    """
    e = estado_lido()
    e["VOLTAS"] = e.get("VOLTAS", 0) + 1
    e["ULTIMA_VOLTA_EM"] = agora()
    try:
        snap = snapshot_do_bot(lane)
    except LeituraInstavel as erro:
        e["FALHAS_CONSECUTIVAS"] = e.get("FALHAS_CONSECUTIVAS", 0) + 1
        e["ULTIMO_ERRO"] = str(erro)
        e["ULTIMO_ERRO_EM"] = agora()
        e["SAUDE"] = ("DEGRADADO" if e["FALHAS_CONSECUTIVAS"] >= FALHAS_ATE_GRITAR
                      else "A_TENTAR")
        estado_gravado(e)
        anotar({"EVENTO": "FALHA_A_LER_O_LIVRO_DO_BOT", "AT": e["ULTIMO_ERRO_EM"],
                "ERRO": str(erro), "FALHAS_CONSECUTIVAS": e["FALHAS_CONSECUTIVAS"],
                "SAUDE": e["SAUDE"]})
        return {"ACCAO": "FALHA", "ERRO": str(erro),
                "FALHAS_CONSECUTIVAS": e["FALHAS_CONSECUTIVAS"], "SAUDE": e["SAUDE"]}

    # ler correu bem: a contagem de falhas volta a zero, e diz-se que voltou.
    if e.get("FALHAS_CONSECUTIVAS"):
        anotar({"EVENTO": "RECUPEROU", "AT": agora(),
                "DEPOIS_DE_FALHAS": e["FALHAS_CONSECUTIVAS"]})
    e["FALHAS_CONSECUTIVAS"] = 0
    e["ULTIMO_LIVRO_VISTO"] = {"SHA256": snap["SHA256"], "TRANSICOES": snap["TRANSICOES"],
                               "ULTIMA_EM": snap["ULTIMA_EM"]}

    # ⚠️ A LEI DA IDEMPOTENCIA: livro igual, nada acontece.
    if not forcar and snap["SHA256"] == e.get("ULTIMO_SHA"):
        e["NOOPS"] = e.get("NOOPS", 0) + 1
        e["SAUDE"] = "SAUDAVEL"
        estado_gravado(e)
        return {"ACCAO": "NO_OP", "PORQUE": "o livro do bot nao mudou",
                "SHA256": snap["SHA256"], "NOOPS": e["NOOPS"]}

    elegiveis_antes = sorted(CG.elegiveis())
    ctx = R.carregar_contexto()
    # o livro C vem do DISCO, nao do Git — e o corte logico e o sha.
    ctx["C"] = snap["LIVRO"]
    ctx["EVIDENCIA_C"] = snap["EVIDENCIAS"]
    ctx["CONTRATOS_C"] = snap["CONTRATOS"]
    ctx["COMMITS"]["C"] = "disco:" + snap["SHA256"][:12]

    doc = R.censo(ctx)
    aplicado = R.aplicar(doc, ctx)
    elegiveis_depois = sorted(CG.elegiveis())

    e["ULTIMO_SHA"] = snap["SHA256"]
    e["SAUDE"] = "SAUDAVEL"

    r = {
        "ACCAO": "ATRAVESSOU",
        "AT": agora(),
        "BOT": {"SHA256": snap["SHA256"], "TRANSICOES": snap["TRANSICOES"],
                "ULTIMA_DECISAO_EM": snap["ULTIMA_EM"]},
        "LIVRO_CANONICO": {"ANTES": aplicado["LINHAS_ANTES"],
                           "DEPOIS": aplicado["LINHAS_DEPOIS"],
                           "APENDIDAS": aplicado["APENDIDAS"]},
        "PROVAS_IMPORTADAS": aplicado["EVIDENCIA"]["PROVAS_IMPORTADAS"],
        "PORTAO": {
            "ELIGIBLE_ANTES": len(elegiveis_antes),
            "ELIGIBLE_DEPOIS": len(elegiveis_depois),
            "ENTRARAM": sorted(set(elegiveis_depois) - set(elegiveis_antes)),
            "SAIRAM": sorted(set(elegiveis_antes) - set(elegiveis_depois)),
        },
    }
    # ⚠️ LIVRO DIFERENTE NAO E O MESMO QUE NOTICIA NOVA, e os dois contam-se em
    # separado. Visto ao vivo: depois de se limpar o residuo de uma prova, o
    # livro do bot ficou com outro `sha256` sem ter decisao nova nenhuma — a
    # volta atravessou e nao acrescentou uma linha. Somar isso a TRAVESSIAS
    # dava um contador que sobrestima, e um contador que sobrestima e um
    # contador que engana: alguem leria «3 travessias» onde houve 2.
    houve_noticia = bool(aplicado["APENDIDAS"] or r["PORTAO"]["ENTRARAM"]
                         or r["PORTAO"]["SAIRAM"])
    if houve_noticia:
        e["TRAVESSIAS"] = e.get("TRAVESSIAS", 0) + 1
        estado_gravado(e)
        anotar(dict(r, EVENTO="TRAVESSIA"))
    else:
        e["LIVRO_NOVO_SEM_NOTICIA"] = e.get("LIVRO_NOVO_SEM_NOTICIA", 0) + 1
        estado_gravado(e)
        r["ACCAO"] = "ATRAVESSOU_SEM_NOVIDADE"
    return r


def servir(*, intervalo: int = INTERVALO_S, voltas: int | None = None,
           lane: Path = LANE_DO_BOT) -> int:
    """O ciclo. `voltas=None` corre para sempre."""
    anotar({"EVENTO": "ARRANQUE", "AT": agora(), "INTERVALO_S": intervalo,
            "LANE_DO_BOT": str(lane), "PID": __import__("os").getpid()})
    n = 0
    espera = intervalo
    while voltas is None or n < voltas:
        r = uma_volta(lane=lane)
        if r["ACCAO"] == "FALHA":
            espera = min(espera * 2, BACKOFF_MAX_S)
        else:
            espera = intervalo
        n += 1
        if voltas is not None and n >= voltas:
            break
        time.sleep(espera)
    return 0


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description="A ponte do curator, a correr sozinha.")
    p.add_argument("--servir", action="store_true", help="ciclo continuo")
    p.add_argument("--voltas", type=int, default=None)
    p.add_argument("--intervalo", type=int, default=INTERVALO_S)
    p.add_argument("--forcar", action="store_true", help="atravessa mesmo sem livro novo")
    p.add_argument("--estado", action="store_true", help="so mostra o estado")
    p.add_argument("--saude", action="store_true",
                   help="esta a trabalhar, ou so existe? (sai 1 se parado)")
    a = p.parse_args(argv)

    if a.saude:
        s = saude()
        print(json.dumps(s, ensure_ascii=False, indent=1))
        return 0 if s["A_TRABALHAR"] else 1
    if a.estado:
        print(json.dumps(estado_lido(), ensure_ascii=False, indent=1))
        return 0
    if a.servir:
        return servir(intervalo=a.intervalo, voltas=a.voltas)
    r = uma_volta(forcar=a.forcar)
    print(json.dumps(r, ensure_ascii=False, indent=1))
    return 0 if r["ACCAO"] != "FALHA" else 1


if __name__ == "__main__":
    raise SystemExit(main())
