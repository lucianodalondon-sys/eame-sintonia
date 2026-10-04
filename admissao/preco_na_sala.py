# -*- coding: utf-8 -*-
"""O PRECO DE CADA ITEM DA SALA — o escritor da tabela da PROPOSTA 038 (myfruit, 28/09).

    motivo_da_recusa(p)                       -> None | "o porque, em texto"
    linha(run_id, ordem, p)                   -> str | None
    sql_de_registo(run_id, pares)             -> str | None      (pares = [(ordem, preco), ...])
    registar(run_id, pares, *, dsn, psql="psql") -> "REGISTADO" | "NADA_A_REGISTAR"

O contrato de UM preco, tal como o extrator o entrega (`p`):

    INDICADOR        PRECO | CUSTO | OUTLOOK
    CULTURA          o nome da cultura COMO A FONTE ESCREVE (literal)
    NIVEL            PIAZZA | NACIONAL | REGIAO  (DECLARADO, nunca inferido do texto)
    PRACA            so obrigatoria quando NIVEL == PIAZZA
    VALOR_TEXTO      LITERAL, tal e qual a fonte publica  («€237,00»)
    VALOR_NUMERICO   o NOSSO parse, ou None — nunca substitui o literal
    UNIDADE          «€/100kg»
    PERIODO_INICIO   ISO, inclusivo
    PERIODO_FIM      ISO, inclusivo
    CLASSE           CURRENT | OUTLOOK | HISTORICAL
    CITACAO          o trecho DE ONDE o preco saiu
    O_QUE_NAO_PROVA  o que este preco NAO prova
    RAW_SHA256       64 hex — a prova de que o ficheiro existiu e e este
    DOCUMENT_ID      quando a fonte o consegue PROVAR; sem prova, «NAO SEI»
    ONDE             onde no ficheiro (pagina, tabela, linha)

⚠️ AUSENCIA NAO GERA LINHA. Um item sem preco lido nao escreve «NAO SEI»: nao escreve nada. Escrever
ausencia como valor seria inventar um preco que ninguem leu — e a vista passaria a mostra-lo.

⚠️ AS REGRAS VIVEM EM DOIS SITIOS DE PROPOSITO: na trava da tabela (`supabase/propostas/038_...sql`) e
aqui. Nao passa aqui o que o banco recusaria, e ha teste que confere que a regra dos dois e a MESMA —
como na 037. Uma regra que so vive num dos lados nao e uma regra: e uma promessa.

⚠️ NAO ESTA LIGADO. Enquanto a 038 for proposta, ninguem chama `registar` na estrada: o sitio onde se
liga (depois do `pousar` da Admissao, com a ordem de cada item) e do dono da Sala. O ensaio
(`provas/migracao_038_ensaio_descartavel.py`) chama-o numa Sala DESCARTAVEL.
"""
from __future__ import annotations

import json
import os
import re
import subprocess

RE_SHA256 = re.compile(r"^[0-9a-f]{64}$")
#: As mesmas tres listas fechadas da trava da proposta 038.
INDICADORES = ("PRECO", "CUSTO", "OUTLOOK")
CLASSES = ("CURRENT", "OUTLOOK", "HISTORICAL")
NIVEIS = ("PIAZZA", "NACIONAL", "REGIAO")
#: O que se escreve quando a fonte nao consegue provar a identidade do documento. Nao se fabrica.
NAO_SEI = "NAO SEI"
#: As chaves que a prova tem de trazer.
CHAVES_OBRIGATORIAS = ("INDICADOR", "CULTURA", "NIVEL", "VALOR_TEXTO", "UNIDADE",
                       "PERIODO_INICIO", "PERIODO_FIM", "CLASSE", "CITACAO",
                       "O_QUE_NAO_PROVA", "RAW_SHA256", "ONDE")


def _txt(p: dict, chave: str) -> str:
    v = p.get(chave)
    return "" if v is None else str(v).strip()


def motivo_da_recusa(p: dict) -> str | None:
    """Porque este preco NAO entra. `None` = entra.

    Devolve o motivo em vez de levantar: quem chama decide (o ensaio conta-os; a estrada pode
    escrever o motivo no recibo). Um preco recusado nao se manda ao banco — nao se pede a uma trava
    que faca o trabalho de quem ja sabe a resposta.
    """
    for chave in CHAVES_OBRIGATORIAS:
        if not _txt(p, chave):
            return "sem %s" % chave
    if _txt(p, "INDICADOR") not in INDICADORES:
        return "indicador %r fora de %s" % (p.get("INDICADOR"), list(INDICADORES))
    if _txt(p, "CLASSE") not in CLASSES:
        return "classe %r fora de %s" % (p.get("CLASSE"), list(CLASSES))
    if _txt(p, "NIVEL") not in NIVEIS:
        return "nivel %r fora de %s" % (p.get("NIVEL"), list(NIVEIS))
    if _txt(p, "VALOR_TEXTO") == NAO_SEI:
        return "o valor e «NAO SEI»: ausencia nao gera linha"
    if _txt(p, "NIVEL") == "PIAZZA" and not _txt(p, "PRACA"):
        return "nivel PIAZZA sem praca: a praca e a praca, a regiao nao e"
    if not RE_SHA256.match(_txt(p, "RAW_SHA256")):
        return "RAW_SHA256 nao e um sha256 de bytes"
    if _txt(p, "PERIODO_FIM") < _txt(p, "PERIODO_INICIO"):
        return "periodo invertido"
    if _txt(p, "DOCUMENT_ID") == "":
        return None  # nao e recusa: e «NAO SEI», e escreve-se na prova
    return None


def _lit(v) -> str:
    return "null" if v is None else "'" + str(v).replace("'", "''") + "'"


def _prova(p: dict) -> str:
    prova = {"RAW_SHA256": _txt(p, "RAW_SHA256"),
             "ONDE": _txt(p, "ONDE"),
             # Sem prova de identidade escreve-se «NAO SEI». Fabricar um DOCUMENT_ID com url, slug,
             # sha ou nome de ficheiro e o que a lei de identidade proibe.
             "DOCUMENT_ID": _txt(p, "DOCUMENT_ID") or NAO_SEI}
    return _lit(json.dumps(prova, ensure_ascii=False, sort_keys=True)) + "::jsonb"


def linha(run_id: str, ordem: int, p: dict) -> str | None:
    if motivo_da_recusa(p):
        return None
    return ("(%s, %d, %s, %s, %s, %s, %s, %s, %s, %s::date, %s::date, %s, %s, %s, %s)" % (
        _lit(run_id), int(ordem),
        _lit(_txt(p, "INDICADOR")), _lit(_txt(p, "CULTURA")), _lit(_txt(p, "NIVEL")),
        _lit(_txt(p, "PRACA") or None),
        _lit(_txt(p, "VALOR_TEXTO")),
        _lit(_txt(p, "VALOR_NUMERICO") or None),
        _lit(_txt(p, "UNIDADE")),
        _lit(_txt(p, "PERIODO_INICIO")), _lit(_txt(p, "PERIODO_FIM")),
        _lit(_txt(p, "CLASSE")), _lit(_txt(p, "CITACAO")), _lit(_txt(p, "O_QUE_NAO_PROVA")),
        _prova(p)))


def sql_de_registo(run_id: str, pares: list) -> str | None:
    """O INSERT. `None` = nada a registar (e isso NAO e uma falha: e um item sem preco lido)."""
    valores = [x for x in (linha(run_id, o, p) for o, p in pares) if x]
    if not valores:
        return None
    return ("insert into public.sala_de_espera_preco "
            "(run_id, ordem, indicador, cultura_literal, nivel, praca, valor_texto, valor_numerico, "
            "unidade, periodo_inicio, periodo_fim, classe, citacao_literal, o_que_nao_prova, prova) "
            "values %s on conflict on constraint preco_do_item_uma_vez do nothing;" % ", ".join(valores))


def registar(run_id: str, pares: list, *, dsn: str, psql: str = "psql") -> str:
    """Escreve os precos lidos de UMA corrida. Um preco por pauta do item.

    Reprocessar com o mesmo codigo NAO escreve duas vezes: a chave natural da tabela
    (`run_id, ordem, indicador, cultura, praca, periodo`) e a mesma, e o `on conflict` cala-se.
    """
    sql = sql_de_registo(run_id, pares)
    if sql is None:
        return "NADA_A_REGISTAR"
    # pela ENTRADA em UTF-8 (a linha de comando do Windows muda a codificacao; medido no ensaio da 037),
    # e com o cliente em UTF8 declarado: o «€» e a virgula decimal nao podem depender da consola.
    r = subprocess.run([psql, "-X", "-v", "ON_ERROR_STOP=1", "-q", "-d", dsn, "-f", "-"], input=sql,
                       capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=120,
                       env=dict(os.environ, PGCLIENTENCODING="UTF8"))
    if r.returncode:
        raise RuntimeError("SALA_PRECO_RECUSOU: " + (r.stderr or "")[-400:])
    return "REGISTADO"


def ler(run_id: str, *, dsn: str, psql: str = "psql") -> list:
    """O que a Inteligencia le, pelo mesmo caminho dela (a vista). So para o ensaio e o diagnostico."""
    sql = ("select ordem, indicador, valor_texto, unidade, raw_sha256, document_id, classe "
           "from public.sala_de_espera_precos where run_id = %s order by ordem, indicador;" % _lit(run_id))
    r = subprocess.run([psql, "-X", "-A", "-t", "-F", "|", "-v", "ON_ERROR_STOP=1", "-d", dsn, "-f", "-"],
                       input=sql, capture_output=True, text=True, encoding="utf-8", errors="replace",
                       timeout=120, env=dict(os.environ, PGCLIENTENCODING="UTF8"))
    if r.returncode:
        return []
    return [l.split("|") for l in r.stdout.strip().splitlines() if l.strip()]
