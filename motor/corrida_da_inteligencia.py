#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""A CORRIDA DA INTELLIGENCE — o `INTELLIGENCE_RUN` mínimo, e só ele.

    MISSAO   C-INT-PILOT-01
    ESPECIE  RUNTIME MINIMO DE ADMISSAO ANALITICA.
    ESTADO   IMPLEMENTED (a corrida) · OBSERVED = ver o relatorio da missao.

    python3 motor/corrida_da_inteligencia.py <ficheiro-de-itens.json>
    python3 -m unittest tests.test_a_primeira_corrida_da_inteligencia -v

A PERGUNTA QUE ESTE FICHEIRO RESPONDE, E MAIS NENHUMA
-----------------------------------------------------
    QUAL EXECUCAO ANALITICA CONSUMIU QUE ITEM READY, QUANDO,
    COM QUE CONFIGURACAO, E O QUE SAIU DISSO?

E a primeira missao que a §32 da Biblia autoriza: um item real, uma corrida
identificada, linhagem provada, sem coleta direta e sem fabricar julgamento.

    NAO PRODUZ FINDING. NAO PRODUZ OPPORTUNITY. NAO PONTUA NADA.

`INTAKE_OK` + `NO_ANALYTIC_OUTPUT_YET` e resultado legitimo e e o esperado
enquanto a materia-prima nao trouxer o que o portao G0 exige.

O QUE ELE NUNCA FAZ
-------------------
    NAO chama coletor.            NAO abre rede.
    NAO cunha SOURCE_ID.          NAO cunha RAW_OBSERVATION_ID.
    NAO converte SOURCE_LOCATION em FACT_LOCATION.
    NAO converte PUBLICATION_TIME em FACT_TIME.
    NAO usa SHA como identidade de observacao.
    NAO transforma NAO SEI em falso, em zero, nem em ausencia.

A ENTRADA VEM DE FORA, E E DE PROPOSITO
----------------------------------------
Esta corrida recebe os itens JA LIDOS. Ela nao sabe abrir a Sala de Espera, e
nao deve saber: o dono da Sala e `admissao/sala_de_espera.py`, da Collection, e
a fronteira entre as duas frentes e o item — nunca o leitor.

    QUEM SABE ABRIR A SALA CONSEGUE, UM DIA, DECIDIR ENCHE-LA.
"""
from __future__ import annotations

import hashlib
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
if str(RAIZ / "provas") not in sys.path:
    sys.path.insert(0, str(RAIZ / "provas"))

# O VOCABULARIO VEM DA ESPINHA, E NAO E COPIADO. Duas listas do mesmo contrato
# divergem, e no dia em que divergissem a corrida media uma coisa e o contrato
# exigia outra.
from espinha_da_intelligence import (           # noqa: E402
    CAMPOS_DO_READY, NAO_SEI, PALAVRAS_QUE_O_REQUISITO_RECUSA,
)

CONTRATO = "CORRIDA_DA_INTELLIGENCE/v1"
RULESET_VERSION = "G0/v1"
BIBLE_VERSION = "SINTONIA-INTELLIGENCE-BIBLE V0.2 CANONICAL"

#: `INT-LAW-053` — cinco perguntas diferentes, cinco estados. Comprimi-los perde
#: a unica informacao que separa «nao corri» de «corri e nao achei».
ESTADOS = ("NOT_RUN", "RUNNING", "DONE", "EMPTY_RESULT", "NO_FINDING",
           "ERROR", "REUSED")

#: O que G0 exige de um item para ele poder virar SINAL. Nao e opiniao: e o que
#: a Biblia pede para que uma leitura analitica saiba SOBRE QUEM fala e QUANDO.
G0_EXIGE = ("ITEM_ID", "SOURCE_ID", "FACT_TIME", "RAW_OBSERVATION_ID")

#: Resultados analiticos possiveis desta V1. Nao ha mais nenhum, de proposito.
INTAKE_OK = "INTAKE_OK"
SEM_SAIDA_ANALITICA = "NO_ANALYTIC_OUTPUT_YET"
BLOQUEADO_EM_G0 = "BLOQUEADO_EM_G0"


class LeiViolada(Exception):
    """A corrida recusou-se, e diz porque. Nao e defeito: e o portao."""


def _agora() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def versao_do_codigo() -> str:
    """A impressao do PROPRIO ficheiro, e nao um numero escrito a mao.

    Um numero de versao digitado mente no dia em que alguem edita e esquece.
    """
    return hashlib.sha256(Path(__file__).read_bytes()).hexdigest()[:16]


def identidade_da_corrida(request_id: str, itens: list) -> str:
    """`RUN_ID` derivado do pedido e das ENTRADAS, nunca do relogio.

    Com o relogio dentro, duas corridas da mesma pergunta sobre o mesmo item
    teriam ids diferentes — e `REUSED` deixaria de ser detetavel. `INT-LAW-054`
    exige que o reuso seja PROVADO, e provar exige que a mesma pergunta sobre a
    mesma materia chegue ao mesmo nome.

        «PARECE A MESMA PERGUNTA» NAO E CACHE KEY. ISTO E.
    """
    corpo = json.dumps({"REQUEST_ID": request_id,
                        "RULESET": RULESET_VERSION,
                        "CODE": versao_do_codigo(),
                        "INPUTS": [referencia_do_item(i) for i in itens]},
                       ensure_ascii=False, sort_keys=True)
    return "IR-" + hashlib.sha256(corpo.encode("utf-8")).hexdigest()[:20]


def referencia_do_item(item: dict) -> dict:
    """A REFERENCIA para cima — nunca uma identidade nova.

    ⚠️ ESTA FUNCAO E O SITIO ONDE SERIA FACIL MENTIR. Um item sem
    `RAW_OBSERVATION_ID` tenta-nos a inventar um a partir do SHA do texto, e
    ficaria bonito. Mas:

        SHA256 IDENTIFICA BYTES. NAO IDENTIFICA OBSERVACAO.

    Dois PDFs diferentes com o mesmo texto extraido dao o mesmo SHA, e a busca
    devolve dois candidatos. DOIS CANDIDATOS NAO SAO UMA LINHAGEM. Quando o
    campo nao vem, a resposta e `NAO SEI` — e a corrida bloqueia em G0.

    ⚠️ E ELA ACEITA LIXO, DE PROPOSITO. A primeira versao rebentava com um
    `None` na lista, e rebentava ANTES de a corrida abrir: o `RUN_ID` deriva das
    entradas, e derivar acontecia fora do `try`. O resultado era uma excepcao
    crua em vez de uma corrida com `RESULT_STATE = ERROR` — ou seja, a corrida
    que falhou nao deixava livro nenhum.

        UMA CORRIDA QUE REBENTA ANTES DE ABRIR NAO DEIXA RASTO,
        E UM ERRO SEM RASTO E INDISTINGUIVEL DE NAO TER CORRIDO.

    Uma entrada que nao e um item vira uma referencia toda `NAO SEI`, marcada —
    e e o laco, ja dentro do `try`, que a recusa.
    """
    if not isinstance(item, dict):
        return {"ITEM_ID": NAO_SEI, "SOURCE_ID": NAO_SEI,
                "RAW_OBSERVATION_ID": NAO_SEI, "CORRIDA_UPSTREAM": NAO_SEI,
                "UNIVERSO": NAO_SEI, "ENTRADA_INVALIDA": True}
    return {
        "ITEM_ID": item.get("ITEM_ID", NAO_SEI),
        "SOURCE_ID": item.get("SOURCE_ID", NAO_SEI),
        "RAW_OBSERVATION_ID": item.get("RAW_OBSERVATION_ID", NAO_SEI),
        "CORRIDA_UPSTREAM": item.get("CORRIDA", NAO_SEI),
        "UNIVERSO": item.get("UNIVERSO", NAO_SEI),
    }


def e_ignorancia(valor) -> bool:
    """`NAO SEI` continua `NAO SEI`, escreva-se como se escrever.

    A porta da Collection escreve `NAO SEI` seco nuns campos e
    `NAO SEI — o documento nao foi lido...` noutros. Comparar por igualdade
    exacta deixaria passar o segundo como se fosse um valor.
    """
    return (valor is None or valor == ""
            or (isinstance(valor, str) and valor.strip().upper().startswith(NAO_SEI)))


def portao_g0(item: dict) -> tuple:
    """`(passou, o_que_falta)`. O unico portao desta V1.

    Ele NAO julga o conteudo: pergunta se da para saber sobre QUEM o item fala,
    de ONDE veio e QUANDO o facto aconteceu. Sem isso nenhuma leitura analitica
    e ancoravel — e uma leitura nao ancoravel e uma invencao com fonte.
    """
    falta = [c for c in G0_EXIGE if e_ignorancia(item.get(c))]
    return (not falta), falta


def requisito(item: dict, falta: list, run_id: str) -> dict:
    """O que a Intelligence PEDE quando lhe falta materia-prima.

    E a unica saida da Intelligence para a Collection, e atravessa por
    `REQUIREMENT_ID` e mais nada. Ela nao escolhe rota, coletor nem executor —
    e esta funcao recusa-o em codigo, e nao so por escrito.
    """
    req = {
        "REQUIREMENT_ID": "REQ-" + hashlib.sha256(
            (run_id + "|" + str(item.get("ITEM_ID", ""))
             + "|" + ",".join(sorted(falta))).encode("utf-8")).hexdigest()[:16],
        "QUESTION_BLOCKED": "o item nao pode virar SINAL: G0 nao consegue "
                            "ancorar sobre quem, de onde e quando.",
        "MISSING_FACT_OR_KEY": sorted(falta),
        "WHY_EXISTING_MATERIAL_IS_INSUFFICIENT":
            "o item existe e foi admitido, mas os campos acima chegaram como "
            f"{NAO_SEI} ou nao chegaram de todo. Preenche-los aqui seria a "
            "Intelligence a fabricar a identidade que a Collection nao cunhou.",
        "REQUIRED_SCOPE": {"ITEM_ID": item.get("ITEM_ID", NAO_SEI),
                           "SOURCE_ID": item.get("SOURCE_ID", NAO_SEI),
                           "UNIVERSO": item.get("UNIVERSO", NAO_SEI)},
        "URGENCY": NAO_SEI,
    }
    sujo = [p for p in PALAVRAS_QUE_O_REQUISITO_RECUSA
            if p in json.dumps(req, ensure_ascii=False).upper()]
    if sujo:
        raise LeiViolada(
            "o requisito nomeou palavra que pertence a Collection: "
            + ", ".join(sujo))
    return req


def correr(pergunta: str, itens: list, request_id: str = "",
           ja_corridas: dict | None = None) -> dict:
    """Abre uma corrida, consome os itens, e devolve o LIVRO dela.

    `ja_corridas` e o que torna `REUSED` provavel em vez de declarado: se a
    mesma pergunta sobre a mesma materia ja correu, devolve-se a corrida
    anterior marcada — nunca uma corrida nova com outro nome.
    """
    if not pergunta or not pergunta.strip():
        raise LeiViolada("uma corrida sem pergunta nao e uma corrida")
    request_id = request_id or ("IQ-" + hashlib.sha256(
        pergunta.encode("utf-8")).hexdigest()[:16])
    run_id = identidade_da_corrida(request_id, itens)

    anterior = (ja_corridas or {}).get(run_id)
    if anterior is not None:
        # ⚠️ REUSO E UMA COPIA MARCADA, E NAO UM ESTADO ESCRITO POR CIMA.
        # Mutar o livro anterior apagava o estado em que ele terminou, e um
        # livro que muda depois de fechado deixa de poder ser conferido.
        copia = json.loads(json.dumps(anterior, ensure_ascii=False))
        copia["RESULT_STATE"] = "REUSED"
        copia["REUSE_OF"] = run_id
        copia["REUSE_PROVED_BY"] = ["REQUEST_ID", "INPUT_REFERENCES",
                                    "RULESET_VERSION", "CODE_VERSION"]
        return copia

    livro = {
        "SCHEMA": CONTRATO,
        "INTELLIGENCE_RUN_ID": run_id,
        "REQUEST_ID": request_id,
        "QUESTION": pergunta,
        "START": _agora(),
        "END": None,
        "RULESET_VERSION": RULESET_VERSION,
        "BIBLE_VERSION": BIBLE_VERSION,
        "CODE_VERSION": versao_do_codigo(),
        "MODEL_VERSION": "NENHUM — esta corrida nao usa modelo",
        "INPUT_REFERENCES": [referencia_do_item(i) for i in itens],
        "RESULT_STATE": "RUNNING",
        "ANALYTIC_OUTPUT": None,
        "SIGNALS": [],
        "REQUIREMENTS": [],
        "ERRORS": [],
        "LINEAGE": [],
        "COLLECTOR_CALLS": 0,
    }
    try:
        if not itens:
            livro["RESULT_STATE"] = "EMPTY_RESULT"
            livro["ANALYTIC_OUTPUT"] = SEM_SAIDA_ANALITICA
            livro["END"] = _agora()
            return livro

        for item in itens:
            if not isinstance(item, dict):
                raise LeiViolada("um item que nao e um item nao se consome")
            passou, falta = portao_g0(item)
            ref = referencia_do_item(item)
            livro["LINEAGE"].append({
                "ITEM_ID": ref["ITEM_ID"],
                "RAW_OBSERVATION_ID": ref["RAW_OBSERVATION_ID"],
                "SOURCE_ID": ref["SOURCE_ID"],
                "CORRIDA_UPSTREAM": ref["CORRIDA_UPSTREAM"],
                "CAMPOS_DO_CONTRATO_PRESENTES":
                    sorted(c for c in CAMPOS_DO_READY if c in item),
                "CAMPOS_DO_CONTRATO_AUSENTES":
                    sorted(c for c in CAMPOS_DO_READY if c not in item),
                "G0": "PASSOU" if passou else BLOQUEADO_EM_G0,
                "G0_FALTA": sorted(falta),
            })
            if passou:
                livro["SIGNALS"].append({
                    "SIGNAL_ID": "SG-" + hashlib.sha256(
                        (run_id + "|" + str(ref["ITEM_ID"])).encode()).hexdigest()[:16],
                    "ITEM_ID": ref["ITEM_ID"],
                    "RAW_OBSERVATION_ID": ref["RAW_OBSERVATION_ID"],
                    "SOURCE_ID": ref["SOURCE_ID"],
                    "FACT_TIME": item.get("FACT_TIME"),
                    "FACT_LOCATION": item.get("FACT_LOCATION", NAO_SEI),
                    "ESTADO": "SINAL",
                    "REGRA": RULESET_VERSION,
                })
            else:
                livro["REQUIREMENTS"].append(requisito(item, falta, run_id))

        livro["RESULT_STATE"] = "DONE"
        livro["ANALYTIC_OUTPUT"] = INTAKE_OK if livro["SIGNALS"] else SEM_SAIDA_ANALITICA
        # ⚠️ NENHUM FINDING. Nao e omissao: a §32 da Biblia autoriza a admissao
        # analitica e para ai. Produzir um achado aqui era fabricar julgamento
        # para a corrida ter o que mostrar.
    except LeiViolada as erro:
        livro["RESULT_STATE"] = "ERROR"
        livro["ERRORS"].append({"TIPO": "LeiViolada", "PORQUE": str(erro)})
        # ⚠️ ERROR != REJEITADO. A corrida falhou; o item a montante nao foi
        # julgado, nao foi rejeitado, e continua exactamente onde estava.
    except Exception as erro:                                    # noqa: BLE001
        livro["RESULT_STATE"] = "ERROR"
        livro["ERRORS"].append({"TIPO": type(erro).__name__, "PORQUE": str(erro)})
    livro["END"] = _agora()
    return livro


def gravar(livro: dict, pasta: Path) -> Path:
    """O livro da corrida, num ficheiro por corrida.

    Sistema de ficheiros pela MESMA razao que a Sala de Espera, e a razao esta
    escrita no ADR dela: nao ha necessidade MEDIDA que exija banco — zero
    consumidores, uma unidade por corrida, nenhuma consulta declarada. Trocar de
    meio mais tarde nao redefine o que uma corrida e.
    """
    pasta.mkdir(parents=True, exist_ok=True)
    destino = pasta / f"{livro['INTELLIGENCE_RUN_ID']}.json"
    tmp = destino.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(livro, ensure_ascii=False, indent=1) + "\n",
                   encoding="utf-8")
    os.replace(tmp, destino)
    return destino


def main() -> int:
    if len(sys.argv) < 2:
        print(__doc__.strip().split("\n\n")[0])
        print("\n  uso: python3 motor/corrida_da_inteligencia.py <itens.json>")
        return 2
    itens = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    if isinstance(itens, dict):
        itens = itens.get("ITENS", [itens])
    livro = correr("primeira admissao analitica de um item real da Sala de Espera",
                   itens)
    print(json.dumps(livro, ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
