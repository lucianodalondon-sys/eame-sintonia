#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""A CORRIDA CANONICA DA MICRO-COLHEITA — o instrumento que mede a ida a rede.

    A LISTA DE FONTES NAO SE DIGITA. PERGUNTA-SE AO PORTAO.

Este ficheiro nao decide quem entra. Ele pergunta tres vezes, a tres donos
diferentes, e so vai a fonte quando os tres responderem que sim:

    1. `curadoria/collection_gate.py`   — ESTA FONTE PODE SER COLHIDA?
       A regra e `READY_CURRENT AND NOT HUMAN_REVIEW AND NOT bloqueada`.
       Perguntado por `coleta/italy_executor.py::admissao_do_curator`.

    2. `regras/italy_contracts.mjs`     — SABE-SE O CAMINHO ATE ELA?
       Um contrato com bloco `ACQUISITION` que o motor de rota aceita.
       Portao aprovar quem o coletor nao sabe percorrer e um facto medido
       nesta casa, nao uma hipotese: em 2026-09-20 a intersecao era ZERO.

    3. `coleta/scrap_http.py::permitido` — O SITIO DEIXA?
       O robots.txt VIVO do host, lido NESTA visita.

    TRES PERGUNTAS DIFERENTES. NENHUMA RESPONDE PELA OUTRA.
    Elegivel nao e percorrivel; percorrivel nao e permitido.

PORQUE O ROBOTS SE LE AQUI, E NAO NO COLETOR
--------------------------------------------
Medido em 2026-09-21: `coleta/italy_pilot_collect.mjs` NAO le `robots.txt` —
zero ocorrencias da palavra no ficheiro, e o livro de observacoes nao tem
campo nenhum para o veredito. Colher sete fontes novas sem essa leitura era
ir a casa de alguem sem bater a porta.

Nao se acrescentou um leitor ao coletor. Esta casa tem uma lei — o portao de
transporte tem UM dono, `coleta/scrap_http.py` — e ja esta em divida com ela
(`curadoria/descobrir.py` e `curadoria/gate_de_rota.py` leem robots tambem).
Um quarto leitor agravava a divida. Pergunta-se ao DONO, antes de lancar o
coletor, e o veredito fica escrito ao lado da observacao.

    NAO CONSEGUI LER NUNCA VIRA O SITE PROIBIU.

Os quatro estados ficam separados, e o instrumento nunca os funde:

    ROBOTS_ALLOW       o robots foi lido e permite este caminho
    ROBOTS_DISALLOW    o robots foi lido e barra este caminho
    ROBOTS_UNREADABLE  o robots respondeu, mas nao e um robots legivel
    ROBOTS_GATE_FAIL   nao se conseguiu LER o robots (o transporte caiu)

`ROBOTS_GATE_FAIL` tambem NAO colhe: nao saber se se pode e motivo para
parar, nunca para prosseguir. Mas fica com o nome dele, porque «o site
proibiu» e uma acusacao ao site, e essa nao se faz sem prova.

SEM CACHE ENTRE CORRIDAS
------------------------
Medido na MICRO-COLLECTION-V1: entre a RUN1 e a RUN3 o bloqueio MUDOU de
fonte. Um veredito guardado teria mentido nas duas direcoes. O cache de
processo de `scrap_http` e limpo ANTES DE CADA VISITA, e por isso cada linha
deste manifesto e uma leitura propria, com hora propria.

O QUE ESTE INSTRUMENTO NAO FAZ
------------------------------
Nao promove, nao escreve no livro do lifecycle, nao toca na Sala, nao decide
custo e nao inventa campo. Ele lanca o corredor canonico
(`coleta/italy_executor.py`), le o DELTA do livro de observacoes e escreve
um manifesto. Quem preserva e a porta; quem admite e a admissao.
"""
from __future__ import annotations

import argparse
import io
import json
import os
import secrets
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "coleta"))
sys.path.insert(0, str(RAIZ / "curadoria"))

import collection_gate as CG        # noqa: E402
import italy_executor as EX         # noqa: E402
import scrap_http as HTTP           # noqa: E402

LIVRO = RAIZ / "data" / "collection-ledger" / "italy" / "observations.ndjson"
CORRIDAS = RAIZ / "data" / "collection-ledger" / "italy" / "runs.ndjson"

# Os campos que o briefing pede por observacao. Escritos aqui para que a
# ausencia de um deles apareca como AUSENTE, e nao como silencio.
CAMPOS_PEDIDOS = ("SOURCE_ID", "DETAIL_URL", "OBSERVATION_ID", "RAW_ASSET_ID",
                  "SHA256", "STORAGE_PATH", "BYTES", "HTTP_STATUS", "ROBOTS_RESULT")


def agora() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")


def alvo_de(source_id: str) -> str:
    """`IT-T7-033` -> `T7`. O alvo esta no proprio SOURCE_ID; nao se escolhe."""
    return source_id.split("-")[1]


def cunhar_run_id(source_id: str) -> str:
    """O MESMO formato do cunhador canonico (`orquestrador.novo_run_id`).

    Nao se importa a funcao porque ela pede um `Pedido` inteiro, e um Pedido
    exige uma receita — e nao ha receita para T5, T7 nem T10 nesta arvore
    (medido: `pedido/receitas.py` tem T2, T3, T4, T6 e T9). O FORMATO e que e
    a lei, e e ele que se cumpre, letra por letra:

        {PAIS}-{ALVO}-{AAAA-MM-DD-HHMMSS}-{16 hex}
    """
    quando = datetime.now(timezone.utc).strftime("%Y-%m-%d-%H%M%S")
    return "IT-%s-%s-%s" % (alvo_de(source_id), quando, secrets.token_hex(8))


def linhas_do_livro() -> list[dict]:
    if not LIVRO.is_file():
        return []
    with io.open(LIVRO, encoding="utf-8") as fh:
        return [json.loads(l) for l in fh if l.strip()]


def contratos_executaveis() -> dict:
    """Pergunta ao dono do contrato, em Node. Zero rede, zero rescrita da regra."""
    prog = (
        "import { CONTRACTS } from './regras/italy_contracts.mjs';"
        "import { conferirAquisicao } from './regras/motor_de_rota.mjs';"
        "const out = {};"
        "for (const id of Object.keys(CONTRACTS)) {"
        "  const c = CONTRACTS[id];"
        "  if (!c.ACQUISITION) { out[id] = { PERCORRIVEL: false, PORQUE: 'contrato sem bloco ACQUISITION' }; continue; }"
        "  try { conferirAquisicao(id, c.ACQUISITION);"
        "        out[id] = { PERCORRIVEL: true, STRATEGY: c.ACQUISITION.STRATEGY,"
        "                    ENTRADA: c.ACQUISITION.INDEX_URL || c.ACQUISITION.URL || c.CANONICAL_ENTRY_URL || '' }; }"
        "  catch (e) { out[id] = { PERCORRIVEL: false, PORQUE: 'motor de rota recusa: ' + e.message }; }"
        "}"
        "console.log(JSON.stringify(out));")
    r = subprocess.run(["node", "--input-type=module", "-e", prog], cwd=str(RAIZ),
                       capture_output=True, text=True, encoding="utf-8",
                       errors="replace", timeout=300)
    if r.returncode != 0:
        raise SystemExit("o dono do contrato nao respondeu:\n" + r.stderr[-1500:])
    return json.loads(r.stdout.strip().splitlines()[-1])


def robots_desta_visita(url: str, ler=True) -> dict:
    """O portao de transporte, perguntado ao DONO, SEM cache entre visitas.

    ⚠️ `ler=False` e o ensaio seco, e existe por um defeito DESTE ficheiro,
    apanhado na primeira execucao: `--sem-rede` travava o COLETOR e deixava
    esta funcao ir a rede na mesma. Sete pedidos de `robots.txt` sairam num
    ensaio que se dizia seco. Um ensaio que toca a rede nao e um ensaio.
    """
    if not ler:
        return {"ROBOTS_RESULT": "NAO_LIDO", "PODE_IR": True, "LIDO_EM": agora(),
                "PORQUE": "ensaio seco: o robots NAO foi lido, e por isso este "
                          "PODE_IR nao e uma permissao — e a ausencia de leitura"}
    HTTP._ROBOTS.clear()                      # o veredito e desta visita, nao da anterior
    quando = agora()
    try:
        ok, motivo = HTTP.permitido(url)
    except HTTP.PortaoIndisponivel as ex:
        return {"ROBOTS_RESULT": "ROBOTS_GATE_FAIL", "PORQUE": str(ex),
                "LIDO_EM": quando, "PODE_IR": False,
                "LEI": "nao consegui LER != o site proibiu"}
    except Exception as ex:                                     # noqa: BLE001
        return {"ROBOTS_RESULT": "ROBOTS_GATE_FAIL",
                "PORQUE": "%s: %s" % (type(ex).__name__, ex),
                "LIDO_EM": quando, "PODE_IR": False,
                "LEI": "nao consegui LER != o site proibiu"}
    if ok:
        return {"ROBOTS_RESULT": "ROBOTS_ALLOW", "PORQUE": motivo,
                "LIDO_EM": quando, "PODE_IR": True}
    # O dono devolve False por duas razoes DIFERENTES, e a diferenca importa.
    ilegivel = "ilegível" in motivo or "ilegivel" in motivo
    return {"ROBOTS_RESULT": "ROBOTS_UNREADABLE" if ilegivel else "ROBOTS_DISALLOW",
            "PORQUE": motivo, "LIDO_EM": quando, "PODE_IR": False,
            "LEI": "nao consegui LER != o site proibiu"}


def observacao_para_o_relatorio(o: dict, robots: dict) -> dict:
    """Traduz UMA linha do livro para os campos do briefing, sem inventar.

    ⚠️ Campo que o livro nao tem sai `AUSENTE_NO_LIVRO`, com o nome do campo.
    Preencher para melhorar a completude e a unica coisa que este tradutor
    tem proibida.
    """
    return {
        "SOURCE_ID": o.get("SOURCE_ID", "AUSENTE_NO_LIVRO"),
        "DETAIL_URL": o.get("SOURCE_URL", "AUSENTE_NO_LIVRO"),
        # O livro italiano NAO carimba OBSERVATION_ID nem RAW_ASSET_ID: esses
        # nascem na porta (`coleta/ingresso.py`), que e outra etapa. Dizer que
        # nao estao aqui e mais honesto que os fabricar a partir do hash.
        "OBSERVATION_ID": o.get("OBSERVATION_ID", "AUSENTE_NO_LIVRO — nasce na porta"),
        "RAW_ASSET_ID": o.get("RAW_ASSET_ID", "AUSENTE_NO_LIVRO — nasce na porta"),
        "SHA256": o.get("RAW_SHA256", "AUSENTE_NO_LIVRO"),
        "STORAGE_PATH": o.get("RAW_PATH", "AUSENTE_NO_LIVRO"),
        "BYTES": o.get("BYTES", "AUSENTE_NO_LIVRO"),
        # O coletor nao grava o codigo HTTP da resposta boa; grava-o so quando
        # falha, dentro de OBSERVATION_RESULT. Nao se inventa um 200.
        "HTTP_STATUS": o.get("HTTP_STATUS", "AUSENTE_NO_LIVRO — o livro guarda o RESULTADO, nao o codigo"),
        "ROBOTS_RESULT": robots.get("ROBOTS_RESULT", "NAO SEI"),
        "OBSERVATION_RESULT": o.get("OBSERVATION_RESULT", "NAO SEI"),
        "DOCUMENT_ID": o.get("DOCUMENT_ID", "AUSENTE_NO_LIVRO"),
        "DOCUMENT_VERSION_ID": o.get("DOCUMENT_VERSION_ID", "AUSENTE_NO_LIVRO"),
        "FACT_TIME": o.get("FACT_TIME", "AUSENTE_NO_LIVRO"),
        "CONTENT_TYPE": o.get("CONTENT_TYPE", "AUSENTE_NO_LIVRO"),
        "MIME_ASSINATURA": o.get("MIME_ASSINATURA", "AUSENTE_NO_LIVRO"),
        "RAW_PRESERVED_BEFORE_PARSE": o.get("RAW_PRESERVED_BEFORE_PARSE", "AUSENTE_NO_LIVRO"),
        "RAW_OBJECT_CREATED": o.get("RAW_OBJECT_CREATED", "AUSENTE_NO_LIVRO"),
    }


def correr(corrida: str, lancar=None) -> dict:
    """UMA corrida sobre a populacao que o portao entrega.

    `lancar` e injectavel pela MESMA razao que em `correr_coletor`: uma prova
    que chame esta funcao a serio vai a rede. Com lancador injectado, prova-se
    o caminho sem que a rede seja alcancavel.
    """
    contratos = contratos_executaveis()
    elegiveis = CG.elegiveis()
    antes = linhas_do_livro()
    chave = lambda o: (o.get("RUN_ID"), o.get("SOURCE_ID"), o.get("SOURCE_URL"), o.get("RAW_SHA256"))
    vistas_antes = {chave(o) for o in antes}

    manifesto = {
        "INSTRUMENTO": "medidas/corrida_canonica.py",
        "CORRIDA": corrida,
        "COMECOU_EM": agora(),
        "REDE_REAL": lancar is None,
        "ELIGIBLE_INPUT": len(elegiveis),
        "ELEGIVEIS": elegiveis,
        "PAINEL_DO_PORTAO": CG.painel(),
        "LIVRO_ANTES": len(antes),
        "FONTES": [],
    }

    for sid in elegiveis:
        linha = {"SOURCE_ID": sid, "RUN_ID": None, "FOI_A_REDE": False}
        c = contratos.get(sid) or {"PERCORRIVEL": False, "PORQUE": "SOURCE_ID sem contrato nenhum"}
        linha["CONTRACT_RESOLVED"] = bool(contratos.get(sid))
        linha["ROUTE_RESOLVED"] = bool(c.get("PERCORRIVEL"))
        linha["ENTRADA"] = c.get("ENTRADA", "")
        linha["STRATEGY"] = c.get("STRATEGY", "NAO SEI")
        if not c.get("PERCORRIVEL"):
            linha["DESFECHO"] = "SEM_ROTA"
            linha["PORQUE"] = c.get("PORQUE", "NAO SEI")
            linha["ROBOTS"] = {"ROBOTS_RESULT": "NAO_LIDO",
                               "PORQUE": "nao se le o robots de um sitio onde nao se vai"}
            manifesto["FONTES"].append(linha)
            continue

        linha["ROBOTS"] = robots_desta_visita(c["ENTRADA"], ler=(lancar is None))
        if not linha["ROBOTS"]["PODE_IR"]:
            linha["DESFECHO"] = linha["ROBOTS"]["ROBOTS_RESULT"]
            linha["PORQUE"] = linha["ROBOTS"]["PORQUE"]
            manifesto["FONTES"].append(linha)
            continue

        run_id = cunhar_run_id(sid)
        linha["RUN_ID"] = run_id
        linha["LANCADO_EM"] = agora()
        r = EX.correr_coletor(run_id, fonte=sid, lancar=lancar)
        linha["FOI_A_REDE"] = lancar is None and not r.get("BLOQUEADA_PELO_CURATOR")
        linha["COLETOR"] = {k: v for k, v in r.items() if k != "ERRO"}
        linha["COLETOR_ERRO"] = (r.get("ERRO") or "")[-800:]
        if r.get("BLOQUEADA_PELO_CURATOR"):
            linha["DESFECHO"] = "BLOQUEADA_PELO_PORTAO"
            linha["PORQUE"] = r["BLOQUEADA_PELO_CURATOR"].get("MOTIVO", "NAO SEI")
            manifesto["FONTES"].append(linha)
            continue

        novas = [o for o in linhas_do_livro()
                 if o.get("RUN_ID") == run_id and chave(o) not in vistas_antes]
        for o in novas:
            vistas_antes.add(chave(o))
        linha["OBSERVACOES"] = [observacao_para_o_relatorio(o, linha["ROBOTS"]) for o in novas]
        linha["OBSERVACOES_NOVAS"] = len(novas)
        linha["DESFECHO"] = "COLHEU" if novas else (
            "CORREU_E_NAO_DEIXOU_OBSERVACAO" if r.get("CODIGO") == 0 else "FALHOU")
        manifesto["FONTES"].append(linha)

    manifesto["ACABOU_EM"] = agora()
    manifesto["LIVRO_DEPOIS"] = len(linhas_do_livro())
    manifesto["OBSERVACOES_NOVAS_TOTAL"] = (manifesto["LIVRO_DEPOIS"] - manifesto["LIVRO_ANTES"])
    # ZERO NAO E UMA SUPOSICAO. Estas rotas sao GET em HTTP publico: nenhuma
    # delas passa por API paga, e nenhuma linha deste instrumento chama uma.
    manifesto["PAID_USD"] = 0.00
    manifesto["PAID_USD_PORQUE"] = ("todas as rotas sao GET em HTTP publico pelo "
                                    "transporte proprio; nenhuma rota paga foi invocada")
    return manifesto


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    p.add_argument("--corrida", required=True, help="nome desta corrida, p.ex. RUN1")
    p.add_argument("--saida", default="", help="onde escrever o manifesto")
    p.add_argument("--sem-rede", action="store_true",
                   help="ensaio: lancador falso, a rede nao e alcancada")
    a = p.parse_args(argv)

    lancar = None
    if a.sem_rede:
        def lancar(cmd):                                        # noqa: ARG001
            return {"CODIGO": 0, "ERRO": "", "CORREU": False,
                    "LANCADOR": "FAKE — ensaio sem rede"}

    m = correr(a.corrida, lancar=lancar)
    destino = Path(a.saida) if a.saida else (
        RAIZ / "medidas" / ("CORRIDA-CANONICA-%s.json" % a.corrida))
    with io.open(destino, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(m, fh, ensure_ascii=False, indent=1)
        fh.write("\n")

    print("CORRIDA           %s   REDE_REAL=%s" % (m["CORRIDA"], m["REDE_REAL"]))
    print("ELIGIBLE_INPUT    %d" % m["ELIGIBLE_INPUT"])
    print("PAID_USD          %.2f" % m["PAID_USD"])
    print("LIVRO             %d -> %d" % (m["LIVRO_ANTES"], m["LIVRO_DEPOIS"]))
    print("")
    print("SOURCE_ID     DESFECHO                         ROBOTS             OBS  ENTRADA")
    for f in m["FONTES"]:
        print("%-13s %-32s %-18s %-4s %s" % (
            f["SOURCE_ID"], f.get("DESFECHO", "NAO SEI"),
            (f.get("ROBOTS") or {}).get("ROBOTS_RESULT", "NAO SEI"),
            f.get("OBSERVACOES_NOVAS", "-"), f.get("ENTRADA", "")[:44]))
    print("\nmanifesto: %s" % destino)
    return 0


if __name__ == "__main__":
    sys.exit(main())
