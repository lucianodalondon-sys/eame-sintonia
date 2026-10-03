#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""O QUE FAZER COM O NAO SEI DO DETECTOR CAPA != MATERIA — preparado, NAO LIGADO.

    NAO SEI NAO E «SIM» POR OMISSAO — MAS QUEM DECIDE E O DONO (D11).

Hoje `retrato_html.gate_capa_nao_e_materia` so reprova CAPA_PROVAVEL: uma pagina
julgada NAO_SEI passa calada. Medido (LD2): com o detector de hoje, 26/109 capas do
gabarito original e 18/49 do de controlo atravessam como NAO_SEI.

A pergunta foi ao bot Luciano (decisao D11). Este modulo tem as tres respostas
possiveis prontas, com teste, e NENHUM chamador: ligar e trocar ACTIVA (e depois
chamar decidir() no portao) — um passo pequeno, depois da decisao, nao antes.

    PASSA       NAO_SEI atravessa (o comportamento de HOJE)
    PESSOA      NAO_SEI vai para uma fila de leitura humana; nao entra ate alguem ler
    QUARENTENA  NAO_SEI entra marcada, fora do que conta como coleta provada, ate
                prova (ex.: a regua dos 4 passos) — nunca e apagada

Consequencias medidas no LD2 (juiz ACTUAL): com PESSOA, as capas que passam caladas
caem de 63/109 para 37/109 (original) e de 28/49 para 10/49 (controlo), e ficam para
ler 34/146 e 19/69 paginas; nenhuma materia a mais e barrada (as NAO_SEI ficam a espera).
"""
from __future__ import annotations

CAPA = "CAPA_PROVAVEL"
MATERIA = "MATERIA_PROVAVEL"
NAO_SEI = "NAO_SEI"

PASSA, PESSOA, QUARENTENA = "PASSA", "PESSOA", "QUARENTENA"
POLITICAS = (PASSA, PESSOA, QUARENTENA)

# ⚠️ O VALOR DE HOJE. So muda com a decisao D11 do dono — e muda-se aqui, num sitio.
ACTIVA = QUARENTENA   # D11 (bot Luciano, delegado do dono, 23/09): opcao C


def decidir(retrato: dict | None, politica: str | None = None) -> dict:
    """O que o portao faz com um retrato. Nunca decide CAPA/MATERIA — so le.

    Devolve {"ACCAO": REPROVA | ENTRA | PESSOA_LE | QUARENTENA, "PORQUE": str}.
    CAPA_PROVAVEL e sempre REPROVA e MATERIA_PROVAVEL sempre ENTRA, seja qual for
    a politica: a politica so responde a pergunta que o detector deixou aberta.
    """
    politica = ACTIVA if politica is None else politica
    if politica not in POLITICAS:
        raise ValueError("politica desconhecida: %r (validas: %s)" % (politica, ", ".join(POLITICAS)))
    k = (retrato or {}).get("CAPA_OU_MATERIA")
    if k == CAPA:
        return {"ACCAO": "REPROVA", "PORQUE": "o detector diz capa"}
    if k == MATERIA:
        return {"ACCAO": "ENTRA", "PORQUE": "o detector diz materia"}
    # NAO_SEI, ou retrato sem veredito: e a mesma pergunta aberta
    if politica == PASSA:
        return {"ACCAO": "ENTRA", "PORQUE": "NAO SEI — politica PASSA (a de hoje)"}
    if politica == PESSOA:
        return {"ACCAO": "PESSOA_LE", "PORQUE": "NAO SEI — uma pessoa le antes de entrar"}
    return {"ACCAO": "QUARENTENA", "PORQUE": "NAO SEI — entra marcada, fora da coleta provada"}
