#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O ORQUESTRADOR — quem responde «qual caminho executar para este pedido».

    py pedido/orquestrador.py "colete materiais de pesquisadores"
    py pedido/orquestrador.py "colete materiais novos de pesquisadores da Espanha" --so-plano

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


def correr(p: Pedido, so_plano: bool = False, seco: bool = False) -> dict:
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

    if seco:
        # ensaio: prova o caminho inteiro sem gastar rede nem dinheiro
        saida, codigo = "(ensaio seco: o executor nao foi chamado)", 0
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
        "COST_USD": 0 if e["custo"] == "gratuito" else "NAO SEI",
        "ITEM_COUNT_RAW": "NAO SEI",
        "ITEM_COUNT_NORMALIZED": "NAO SEI",
        "ERROR": erro.strip(),
        "ESTADO_DOS_ITENS": COLHIDO if codigo == 0 else ERRO,
        "FONTES_DO_ASSUNTO": len(plano.fontes_do_assunto),
        "FONTES_SEM_CAMINHO": len(plano.sem_caminho),
        "SAIDA": saida.strip()[-1500:],
        "_plano": plano,
    }
    return recibo


def main() -> int:
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    so_plano = "--so-plano" in sys.argv
    seco = "--seco" in sys.argv
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

    recibo = correr(p, so_plano=so_plano, seco=seco)
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
    if seco:
        print("  (ensaio seco: nada foi coletado e nada foi escrito no manifesto)")
    return 0 if recibo["STATUS"] == "OK" else 1


if __name__ == "__main__":
    raise SystemExit(main())
