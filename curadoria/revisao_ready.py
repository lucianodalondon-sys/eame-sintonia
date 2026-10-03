#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""A REVISAO DAS READY DO REPARO — a leitura que a regua nao faz.

    PASSAR A REGUA NAO E SER MATERIA.

Medido na R1 (24/09, `scripts/reparo/R1-REVISAO-READY.json`): das 46 fontes que o
reparo levou a READY numa copia do vivo, 19 tinham como «documento» uma pagina
fixa (tributos, gabinete, «lavora con noi»), um leitor de terceiros (Issuu) ou a
propria listagem. O juiz da casa (retrato_html) mede texto e ligacoes; a regua
dos quatro passos passa-as. Quem as separou foi a LEITURA, uma a uma.

Decisao do coordenador (24/09, missao-r1-instalacao): o motivo dessa leitura
vira ESTADO no livro, pela transicao que ja existe, e so as limpas saem READY:

  SERVICO_OU_INSTITUCIONAL, TEXTO_NAO_E_MATERIA, LISTA_COMO_ITEM
        -> CONTRACTED_CANARY_FAILED com «REVISAO_R1: <classe>: <motivo>»
  TEMA_A_CONFIRMAR
        -> SEMANTIC_REVIEW com «TEMA_A_CONFIRMAR (D2): ...» (pergunta dupla ao dono:
           gaveta certa + relevancia)
  ACESSO_PARCIAL
        -> READY, com a nota «ACESSO_PARCIAL: so o inicio aberto» na razao do livro
  LIMPA -> READY, como a regua decidir

⚠️ FALHA FECHADA PARA O QUE O REPARO TROUXE E NINGUEM LEU. Um contrato reescrito
pela R1 (tem REPARO_DE_CONTRATO) so sai READY se esta revisao tiver uma leitura
LIMPA ou ACESSO_PARCIAL para ESSE contrato (mesmo INDEX_URL e LINK_PATTERN). Sem
leitura — fonte nova, ou o reparo achou outro padrao desde a revisao — fica
CONTRACTED_CANARY_FAILED com «REVISAO_PENDENTE», para a leitura (humana ou a
IA-CUR pela FILA-PRECISA-DE-IA) voltar a ela.

Porque NAO REPAIRING (a sugestao do coordenador para as de servico): nenhum
alimentador pega fontes em REPAIRING — ficariam presas, sem tarefa. Em
CONTRACTED_CANARY_FAILED o motivo fica escrito e o reparo/IA sabem onde as achar.

Quem decide o veredito e a leitura, nunca este modulo: ele so o aplica.
"""
from __future__ import annotations

import json
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
ARQUIVO = RAIZ / "curadoria" / "REVISAO-READY-V1.json"

# ALVO_ERRADO e NAO_SEI (REVISAO-15, 25/09): o padrao reparado aponta para outro tema
# ou seccao que nao a da fonte (fitossanitario -> «qualita produzioni»); ou a leitura
# nao decide. As duas retem, como as outras, com o motivo no livro.
BLOQUEIAM = frozenset({"SERVICO_OU_INSTITUCIONAL", "TEXTO_NAO_E_MATERIA", "LISTA_COMO_ITEM",
                       "ALVO_ERRADO", "NAO_SEI"})
TEMA = "TEMA_A_CONFIRMAR"
PARCIAL = "ACESSO_PARCIAL"
LIMPA = "LIMPA"
CLASSES = BLOQUEIAM | {TEMA, PARCIAL, LIMPA}


def _ler() -> dict:
    if not ARQUIVO.exists():
        return {}
    d = json.loads(ARQUIVO.read_text(encoding="utf-8"))
    return {x["SOURCE_ID"]: x for x in d.get("FONTES", [])}


def _mesmo_contrato(entrada: dict, contrato: dict) -> bool:
    aq = (contrato or {}).get("ACQUISITION") or {}
    return (entrada.get("INDEX_URL") == aq.get("INDEX_URL")
            and entrada.get("LINK_PATTERN") == aq.get("LINK_PATTERN"))


def decisao(source_id: str, contrato: dict | None) -> dict | None:
    """O que a revisao diz sobre promover ESTA fonte com ESTE contrato.

    None = a revisao nao tem nada a dizer (a regua decide sozinha).
    {"ACAO": "RETER", "ESTADO": ..., "RAZAO": ...}   nao promover; registar o estado
    {"ACAO": "PROMOVER_COM_NOTA", "NOTA": ...}        promover, com a nota na razao
    """
    e = _ler().get(source_id)
    mesmo = bool(e) and _mesmo_contrato(e, contrato)
    obs = "" if mesmo else " (o contrato mudou desde a leitura: reler)"
    if e and e.get("CLASSE") in BLOQUEIAM:
        return {"ACAO": "RETER", "ESTADO": "CONTRACTED_CANARY_FAILED", "CLASSE": e["CLASSE"],
                "RAZAO": ("REVISAO_R1: %s: %s%s" % (e["CLASSE"], e.get("MOTIVO", ""), obs))[:200]}
    if e and e.get("CLASSE") == TEMA:
        return {"ACAO": "RETER", "ESTADO": "SEMANTIC_REVIEW", "CLASSE": TEMA,
                "RAZAO": ("TEMA_A_CONFIRMAR (D2: gaveta certa + relevancia): %s%s"
                          % (e.get("MOTIVO", ""), obs))[:200]}
    reparado = bool((contrato or {}).get("REPARO_DE_CONTRATO"))
    lido = bool(e) and e.get("CLASSE") in (LIMPA, PARCIAL) and mesmo
    if reparado and not lido:
        return {"ACAO": "RETER", "ESTADO": "CONTRACTED_CANARY_FAILED", "CLASSE": "REVISAO_PENDENTE",
                "RAZAO": ("REVISAO_PENDENTE: contrato reparado pela R1 passou a regua, mas ninguem "
                          "leu o item deste contrato%s" % (obs if e else ""))[:200]}
    if e and e.get("CLASSE") == PARCIAL and mesmo:
        return {"ACAO": "PROMOVER_COM_NOTA", "CLASSE": PARCIAL,
                "NOTA": "ACESSO_PARCIAL: %s" % e.get("MOTIVO", "so o inicio aberto")}
    return None
