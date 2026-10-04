#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O ORQUESTRADOR — quem responde «qual caminho executar para este pedido».

    py orquestrador/orquestrador.py "colete materiais de pesquisadores"
    py orquestrador/orquestrador.py "colete concorrentes" --so-a-porta   # so a peneira
    py orquestrador/orquestrador.py "colete materiais novos de pesquisadores da Espanha" --so-plano

ELE NAO COLETA. Nao abre pagina, nao chama API, nao raspa nada. Ele escolhe o
executor e coordena — e essa separacao e a razao de existir: quando o executor
for trocado por outro melhor, quem pediu continua a pedir a mesma coisa.

O QUE ELE ACRESCENTA E O RECIBO
--------------------------------
O censo encontrou o achado mais util desta missao: o `RUN-MANIFEST.json` ja tem
os campos certos — RUN_ID, ACTOR, ACTOR_VERSION, STARTED_AT, FINISHED_AT, INPUT,
COST_USD, ITEM_COUNT_RAW, STATUS, ERROR — e **cinco reguas ja o leem**. So que
nenhum executor o escreve. Por isso metade das corridas guardadas diz
`NOT_PRESERVED` no tempo e na versao: foram preenchidas a mao, depois, de
memoria.

Nao se inventa aqui um recibo novo. Faz-se o orquestrador ASSINAR o que ja
existe, em toda corrida, sem depender de ninguem se lembrar.

    O QUE NAO TEM RECIBO NAO ACONTECEU. Uma coleta sem recibo nao se consegue
    auditar, nao se consegue repetir, e nao se consegue cobrar — e daqui a tres
    meses ninguem sabe dizer se aquele numero veio de uma corrida boa ou de uma
    que falhou a meio.

ERRO NAO E REJEICAO
-------------------
Se o executor rebentar, o estado e ERRO e o recibo guarda a mensagem. Nao e
`REJEITADO`: rejeitado quer dizer «olhei e nao serve», e aqui ninguem chegou a
olhar. Confundir os dois faz uma falha de rede parecer um julgamento sobre a
fonte, e a fonte leva a culpa pela ferramenta.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
import _gavetas  # noqa: E402,F401

from pedido import Pedido, de_uma_frase, PedidoInvalido, ERRO, COLHIDO  # noqa: E402
from receitas import resolver, Plano  # noqa: E402
import admissao as adm  # noqa: E402

PRONTOS = RAIZ / "data" / "samples" / "PRONTO-PARA-INTELIGENCIA"


def a_colheita(e: dict) -> tuple[list, str]:
    """O que o executor largou — e, quando nao largou nada, PORQUE.

    Esta funcao existe por causa de uma pergunta simples que nao tinha resposta:
    «o que o YouTube colhe vai para onde?». Ia para uma pasta que ninguem lia, e
    o caminho acabava ali. A porta de admissao estava construida e NINGUEM
    entregava nela — so o teste.

        UMA PORTA POR ONDE NINGUEM PASSA NAO E UMA PORTA.
        E UMA PAREDE COM MACANETA.

    Aqui a colheita e lida e levada a porta. Quando o sitio declarado nao existe,
    isso nao e um erro a esconder: e o facto mais util que a corrida produziu, e
    sai escrito no recibo.
    """
    itens, notas = [], []
    for onde in e.get("larga_em") or []:
        alvo = RAIZ / onde
        if not alvo.exists():
            notas.append(f"«{onde}» nao existe nesta arvore: o executor declara que "
                         f"larga ai, e nao ha nada. Ou nunca correu aqui, ou o que "
                         f"ele escreveu nunca foi guardado.")
            continue
        ficheiros = sorted(alvo.glob("*.json")) if alvo.is_dir() else [alvo]
        for f in ficheiros:
            try:
                d = json.loads(f.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, OSError) as ex:
                notas.append(f"«{f.name}» nao deu para ler: {type(ex).__name__}")
                continue
            # uma lista, ou o primeiro campo do ficheiro que seja lista de fichas
            lista = d if isinstance(d, list) else next(
                (v for v in d.values() if isinstance(v, list) and v
                 and isinstance(v[0], dict)), [])
            for x in lista:
                if isinstance(x, dict):
                    x.setdefault("_de", f.relative_to(RAIZ).as_posix())
                    itens.append(x)
    return itens, " · ".join(notas)


def pela_porta(itens: list, universo: str, run_id: str) -> dict:
    """Leva cada item a porta de admissao e guarda TODAS as decisoes.

    TODAS, e nao so as que passaram: o «nao» sem testemunha e trabalho perdido
    duas vezes — perde-se o item e perde-se a informacao de que aquela fonte
    entrega lixo.
    """
    decisoes = [adm.decidir(x, universo, corrida=run_id) for x in itens]
    if decisoes:
        adm.escrever(decisoes)

    aceites = []
    for x, d in zip(itens, decisoes):
        if d.resultado == adm.SIM:
            aceites.append(adm.pronto_para_inteligencia(x, d))
    if aceites:
        PRONTOS.mkdir(parents=True, exist_ok=True)
        corpo = json.dumps({"RUN_ID": run_id, "ITENS": aceites},
                           ensure_ascii=False, indent=2)
        (PRONTOS / f"{run_id}.json").write_text(corpo + "\n", encoding="utf-8")

    conta: dict = {}
    for d in decisoes:
        conta[d.resultado] = conta.get(d.resultado, 0) + 1
    return {"itens": len(itens), "por_resultado": conta, "prontos": len(aceites),
            "ficheiro": (PRONTOS / f"{run_id}.json").relative_to(RAIZ).as_posix()
                        if aceites else ""}

MANIFESTO = RAIZ / "data" / "samples" / "RUN-MANIFEST.json"


def agora() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def versao_do_executor(caminho: str) -> str:
    """A versao e o commit que tocou o ficheiro pela ultima vez.

    NOT_PRESERVED era o que estava escrito nas corridas antigas — quer dizer
    «ninguem apontou». Com o commit ao lado, da para voltar exatamente ao codigo
    que produziu aquele numero.
    """
    r = subprocess.run(["git", "-C", str(RAIZ), "log", "-1", "--format=%h",
                        "--", caminho], capture_output=True, text=True)
    return (r.stdout.strip() or "NOT_PRESERVED") if r.returncode == 0 else "NOT_PRESERVED"


def novo_run_id(p: Pedido) -> str:
    pais = (p.filtros.get("pais") or "XX").upper()
    return f"{pais}-{p.alvo}-{datetime.now(timezone.utc).strftime('%Y-%m-%d-%H%M%S')}"


def guardar_recibo(recibo: dict) -> None:
    """Acrescenta a corrida ao manifesto que ja existe, sem reescrever o resto.

    Reescrever o ficheiro inteiro ja custou caro nesta casa: `sensor_coleta.py`
    documenta um lote que empurrou primeiro e apagou o outro. Aqui le-se, junta-se
    e escreve-se — nunca se substitui o que estava la.
    """
    d = {"RUNS": []}
    if MANIFESTO.is_file():
        try:
            d = json.loads(MANIFESTO.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            pass
    d.setdefault("RUNS", []).append(recibo)
    MANIFESTO.parent.mkdir(parents=True, exist_ok=True)
    MANIFESTO.write_text(json.dumps(d, ensure_ascii=False, indent=2) + "\n",
                         encoding="utf-8")


def correr(p: Pedido, so_plano: bool = False, seco: bool = False,
           so_a_porta: bool = False) -> dict:
    """Do pedido ao recibo. Devolve o recibo, sempre — mesmo quando falha."""
    plano = resolver(p)

    if so_plano or not plano.da_para_correr:
        return {
            "RUN_ID": novo_run_id(p),
            "STATUS": "PLANO" if so_plano else "SEM_CAMINHO",
            "PEDIDO": p.para_json(),
            "MISSION": p.assunto,
            "COUNTRY": p.filtros.get("pais", "NAO SEI"),
            "FONTES_DO_ASSUNTO": len(plano.fontes_do_assunto),
            "FONTES_SEM_CAMINHO": len(plano.sem_caminho),
            "ERROR": "" if so_plano else plano.porque_nao(),
            "_plano": plano,
        }

    e = plano.executores[0]
    caminho = e["roda"][0]
    # o comando nasce do PEDIDO, nao de quem chama o orquestrador
    comando = list(e["roda"])
    valores = {**(e.get("filtros_por_omissao") or {}), **p.filtros}
    for nome in e.get("argumentos_de_filtros") or []:
        v = valores.get(nome)
        if v:
            comando.append(str(v))
    inicio = agora()
    saida, erro, codigo = "", "", 0

    if seco or so_a_porta:
        # ensaio: prova o caminho inteiro sem gastar rede nem dinheiro.
        # `--so-a-porta` vai mais longe: nao colhe, mas leva a colheita QUE JA
        # EXISTE a peneira. E o que permite reprocessar quando a regra muda —
        # sem isto, mudar a regra obrigaria a coletar tudo outra vez, e ninguem
        # o faria; a regra nova valeria so para o que viesse depois.
        saida, codigo = ("(nao se colheu: so se levou a colheita a porta)"
                         if so_a_porta else
                         "(ensaio seco: o executor nao foi chamado)"), 0
    else:
        try:
            r = subprocess.run([sys.executable, *comando], cwd=str(RAIZ),
                               capture_output=True, text=True, encoding="utf-8",
                               errors="replace", timeout=1800)
            saida, erro, codigo = r.stdout[-4000:], r.stderr[-2000:], r.returncode
        except Exception as ex:                                # noqa: BLE001
            erro, codigo = f"{type(ex).__name__}: {ex}", 1

    recibo = {
        "RUN_ID": novo_run_id(p),
        "STATUS": "OK" if codigo == 0 else ERRO,
        "PEDIDO": p.para_json(),
        "MISSION": p.assunto,
        "COUNTRY": p.filtros.get("pais", "NAO SEI"),
        "PLATFORM": ", ".join(e["rotas"]),
        "ACTOR": caminho,
        "ACTOR_VERSION": versao_do_executor(caminho),
        "CAPTURE_METHOD": e["custo"],
        "INPUT": p.filtros or {},
        "QUERY": p.em_uma_frase(),
        "COMANDO": " ".join(comando),
        "STARTED_AT": inicio,
        "FINISHED_AT": agora(),
        # Custo ZERO quando o executor nao foi chamado: uma passagem so pela
        # peneira nao abre ligacao nenhuma. Escrever «NAO SEI» aqui seria pior
        # que impreciso — o portao do padrao conta os «NAO SEI» como divida, e
        # eu estaria a inventar divida sobre uma corrida que nao gastou nada.
        "COST_USD": (0 if (seco or so_a_porta or e["custo"] == "gratuito")
                     else "NAO SEI"),
        "ITEM_COUNT_RAW": "NAO SEI",
        "ITEM_COUNT_NORMALIZED": "NAO SEI",
        "ERROR": erro.strip(),
        "ESTADO_DOS_ITENS": COLHIDO if codigo == 0 else ERRO,
        "FONTES_DO_ASSUNTO": len(plano.fontes_do_assunto),
        "FONTES_SEM_CAMINHO": len(plano.sem_caminho),
        "SAIDA": saida.strip()[-1500:],
        "_plano": plano,
    }

    # ── E A COLHEITA VAI A PORTA ────────────────────────────────────────────
    # O caminho so esta fechado aqui. Antes desta parte, o executor corria,
    # largava o que trouxe numa pasta, e ninguem ia buscar: a peneira existia e
    # nada passava por ela.
    itens, notas = a_colheita(e)
    recibo["COLHEITA_ENCONTRADA"] = len(itens)
    recibo["COLHEITA_NAO_ENCONTRADA"] = notas
    if itens and (so_a_porta or not seco):
        r = pela_porta(itens, p.alvo, recibo["RUN_ID"])
        recibo["ADMISSAO"] = r
        recibo["ITEM_COUNT_RAW"] = r["itens"]
        recibo["ITEM_COUNT_NORMALIZED"] = r["prontos"]
        recibo["ESTADO_DOS_ITENS"] = ("PRONTO_PARA_INTELIGENCIA" if r["prontos"]
                                      else "NA_PORTA")
    return recibo


def main() -> int:
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    so_plano = "--so-plano" in sys.argv
    so_a_porta = "--so-a-porta" in sys.argv
    seco = "--seco" in sys.argv and not so_a_porta
    # --filtro fase=posts --filtro plataforma=youtube
    extras = {}
    for i, a in enumerate(sys.argv):
        if a == "--filtro" and i + 1 < len(sys.argv) and "=" in sys.argv[i + 1]:
            k, v = sys.argv[i + 1].split("=", 1)
            extras[k.strip()] = v.strip()
    frase = " ".join(args) or "colete materiais de pesquisadores"

    try:
        p = de_uma_frase(frase)
        p.filtros.update(extras)
    except PedidoInvalido as ex:
        print(f"PEDIDO RECUSADO: {ex}")
        return 2

    recibo = correr(p, so_plano=so_plano, seco=seco, so_a_porta=so_a_porta)
    plano = recibo.pop("_plano")
    print(plano.em_palavras())
    print()

    if recibo["STATUS"] == "PLANO":
        print("(so o plano foi pedido; nada correu)")
        return 0
    if recibo["STATUS"] == "SEM_CAMINHO":
        print(f"NAO CORREU · {recibo['ERROR']}")
        return 1

    if not seco:
        guardar_recibo({k: v for k, v in recibo.items() if k != "SAIDA"})
    print(f"CORRIDA {recibo['STATUS']} · {recibo['RUN_ID']}")
    print(f"  executor {recibo['ACTOR']} @ {recibo['ACTOR_VERSION']}")
    print(f"  de {recibo['STARTED_AT']} a {recibo['FINISHED_AT']}")
    if recibo["ERROR"]:
        print(f"  ERRO (nao e rejeicao): {recibo['ERROR'][:300]}")
    print(f"  colheita encontrada: {recibo.get('COLHEITA_ENCONTRADA', 0)} item(ns)")
    if recibo.get("COLHEITA_NAO_ENCONTRADA"):
        print(f"  NAO ENCONTREI O QUE ELE LARGOU: {recibo['COLHEITA_NAO_ENCONTRADA']}")
    a = recibo.get("ADMISSAO")
    if a and a["itens"]:
        print("  pela porta de admissao: "
              + " · ".join(f"{k} {v}" for k, v in sorted(a["por_resultado"].items())))
        if a["ficheiro"]:
            print(f"  prontos para a inteligencia: {a['prontos']} -> {a['ficheiro']}")
    if seco:
        print("  (ensaio seco: nada foi coletado e nada foi escrito no manifesto)")
    return 0 if recibo["STATUS"] == "OK" else 1


if __name__ == "__main__":
    raise SystemExit(main())
