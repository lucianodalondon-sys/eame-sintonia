#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""O QUE O CONTRATO DE FONTE DECLARA — lido, nunca copiado.

Os 13 contratos de fonte italianos vivem em `regras/italy_contracts.mjs`, e o
dono deles é esse ficheiro. Ele declara, ANTES de qualquer execução:

    SOURCE_LOCATION_RULE   onde está quem publica          13 de 13
    FACT_LOCATION_RULE     onde procurar o lugar do fato   13 de 13
    EVIDENCE_CLASS         que peso probatório isto tem    13 de 13
    DOCUMENT_ID_RULE       qual a identidade semântica     13 de 13

Nada disto atravessava a fronteira para a Sala de Espera. A jusante, um boletim
agroclimático da ARPAV e um relato de campo da ARIF eram o MESMO objecto:
`TEXTO`. E o contrato dizia — em letra, ao lado da fonte —

    AGROCLIMATIC_SIGNAL != PEST_OCCURRENCE
    COMPANY_CLAIM       != REGULATORY_FACT

⚠️ PORQUE ISTO LÊ EM VEZ DE COPIAR, E NÃO É UMA QUESTÃO DE ELEGÂNCIA.

A resposta óbvia era exportar os contratos para um JSON e o Python ler o JSON. O
custo aparece no segundo dia: passam a existir duas verdades sobre a mesma
fonte, e a partir do dia em que alguém editar uma delas — e vai editar o `.mjs`,
porque é onde os coletores vivem — a outra continua a responder, errada e
convincente.

    UMA CÓPIA GERADA É UMA VERDADE COM DATA DE VALIDADE
    E SEM NINGUÉM A VIGIAR O PRAZO.

Aqui o Python **pergunta ao node**, que é quem sabe ler `.mjs`. Um dono, um
leitor, zero cópias. Se o node não existir nesta máquina, a resposta é `NAO SEI`
— nunca um valor de reserva.

⚠️ E ESTE MÓDULO NÃO NORMALIZA NADA. Ele devolve o que está escrito, tal e qual.
Transformar `"Napoli (sede da Regiao) — fixo"` no valor `Napoli` é uma
normalização, precisa de regra e de prova, e vive noutro sítio — em
`lugar_declarado_pela_fonte()`, aqui em baixo, que a faz **conferindo contra o
gazetteer** e recusando o que não confirma.
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)

from leis import artefato as art  # noqa: E402
from leis import fato_local as fl  # noqa: E402

NAO_SEI = art.NAO_SEI

#: Onde o dono mora. Um só caminho, e ele é o do contrato.
CONTRATOS_MJS = os.path.join(RAIZ, "regras", "italy_contracts.mjs")

#: O que se vai buscar. Declarado aqui para que a leitura seja legível e para
#: que acrescentar um campo seja uma decisão e não um acidente.
CAMPOS_DECLARADOS = ("SOURCE_LOCATION_RULE", "FACT_LOCATION_RULE",
                     "EVIDENCE_CLASS", "DOCUMENT_ID_RULE",
                     "DOCUMENT_DATE_FIELD", "OWNER", "TERRITORY")


class ContratosIlegiveis(Exception):
    """O ficheiro de contratos existe e não se conseguiu ler.

    NÃO é «não há contratos». São coisas diferentes, e confundi-las faria uma
    falha de ambiente parecer uma fonte sem contrato — que é o estado que a casa
    usa para dizer «isto não pode ser coletado».
    """


_cache = None


def declarados(recarregar: bool = False) -> dict:
    """`{SOURCE_ID: {campo: valor declarado}}`. Vazio se o node não existir.

    Não levanta por falta de node: numa máquina sem node a resposta honesta é
    «não consigo ler o contrato», e quem chama recebe `{}` e escreve `NAO SEI`.
    Levanta quando o ficheiro EXISTE e o node o recusa — aí não é ausência de
    ferramenta, é um contrato partido, e isso tem de gritar.
    """
    global _cache
    if _cache is not None and not recarregar:
        return _cache
    if not os.path.isfile(CONTRATOS_MJS):
        _cache = {}
        return _cache
    # ⚠️ `file://`, E NAO O CAMINHO. No Windows um caminho absoluto comeca por
    # `C:`, e o carregador de modulos do node le `c:` como um ESQUEMA de URL —
    # `ERR_UNSUPPORTED_ESM_URL_SCHEME`. A mesma linha funciona no Linux e falha
    # aqui, e a falha parece um contrato partido.
    from pathlib import Path
    endereco = Path(CONTRATOS_MJS).resolve().as_uri()
    guiao = (
        "import { CONTRACTS } from %s;\n"
        "const campos = %s;\n"
        "const fora = {};\n"
        "for (const [id, c] of Object.entries(CONTRACTS)) {\n"
        "  const linha = {};\n"
        "  for (const k of campos) if (c[k] !== undefined) linha[k] = String(c[k]);\n"
        "  fora[id] = linha;\n"
        "}\n"
        "process.stdout.write(JSON.stringify(fora));\n"
        % (json.dumps(endereco), json.dumps(list(CAMPOS_DECLARADOS)))
    )
    try:
        # ⚠️ `encoding="utf-8"`, E NAO O PADRAO DA MAQUINA.
        # O node escreve UTF-8 sempre. `text=True` sozinho manda o Python
        # descodificar com a pagina de codigo do sistema — em Windows, `cp1252`.
        # Medido: `"Napoli (sede da Regiao) — fixo"` chegava como
        # `'Napoli (sede da Regiao) â€” fixo'`, o travessao deixava de ser
        # travessao, a regra deixava de casar e a fonte saia `NAO SEI`.
        #
        #     UM `NAO SEI` NASCIDO DE CODIFICACAO E O PIOR TIPO DE `NAO SEI`:
        #     ELE PARECE UMA MEDICAO, E MUDA DE RESPOSTA CONFORME A MAQUINA.
        r = subprocess.run(["node", "--input-type=module", "-e", guiao],
                           capture_output=True, text=True, encoding="utf-8",
                           errors="strict", cwd=RAIZ, timeout=60)
    except (FileNotFoundError, OSError, subprocess.TimeoutExpired):
        _cache = {}
        return _cache
    if r.returncode != 0:
        raise ContratosIlegiveis(
            "%s existe e o node recusou-o: %s. NAO se devolve lista vazia: um "
            "contrato partido nao e uma fonte sem contrato."
            % (CONTRATOS_MJS, (r.stderr or "").strip()[:400]))
    try:
        _cache = json.loads(r.stdout)
    except json.JSONDecodeError as e:
        raise ContratosIlegiveis("o node respondeu e nao era JSON: %s" % e) from e
    return _cache


def especie_de_evidencia_declarada(source_id: str) -> str:
    """O `EVIDENCE_CLASS` do contrato, TAL E QUAL. Ausente: `NAO SEI`.

    ⚠️ NÃO SE PARSEIA, NÃO SE ENCURTA, NÃO SE VIRA ENUM. Medido nos próprios
    contratos, o valor é texto livre e às vezes é uma instrução:

        "OBSERVED_FIELD_SIGNAL + TECHNICAL_GUIDELINE (separar por bloco)"
        "TECHNICAL_GUIDELINE + OBSERVED_FIELD_SIGNAL pontual"

    `docs/operacao/STRUCTURED-POR-ESPECIE-E-NOT-APPLICABLE.md` §14.4 deixou em
    aberto, de propósito, se isto deve virar lista fechada — *«não decido sem
    caso que obrigue»*. Esta missão não é esse caso: ela precisa que a espécie
    ATRAVESSE, não que ela seja arrumada.

        PRESERVAR O QUE A FONTE DECLAROU != DECIDIR O VOCABULÁRIO DA CASA.
    """
    return (declarados().get(source_id) or {}).get("EVIDENCE_CLASS") or NAO_SEI


# ── A ÚNICA NORMALIZAÇÃO DESTE MÓDULO, E ELA CONFERE ANTES DE AFIRMAR ──────
# `SOURCE_LOCATION_RULE` é quase sempre um nome de sítio com um aparte:
#
#     "Napoli (sede da Regiao) — fixo"     "Roma"      "Terlano (BZ)"
#     "Teolo/Padova"                       "site nacional"
#
# Pôr a frase inteira no campo `SOURCE_LOCATION` seria meter prosa num sítio de
# valor. Tirar o nome à força seria adivinhar. O que se faz é o que a casa já
# faz para lugar: propor e **conferir contra o gazetteer** de
# `leis/fato_local.py`, que é a autoridade declarada — e recusar o que não
# confirma, com o motivo escrito.
#
#     NOT_IN_GAZETTEER != NOT_A_PLACE != REJECTED_BY_LAW
#
# "site nacional" cai por aqui, e cai bem: não é um lugar.
_APARTE = re.compile(r"\s*\(.*?\)")
_SUFIXO = re.compile(r"\s*[—–-]\s.*$")


def _candidatos_do_texto(regra: str):
    """Os nomes que a regra propõe, na ordem em que aparecem. Não confere nada."""
    limpo = _SUFIXO.sub("", _APARTE.sub("", regra or "")).strip()
    return [p.strip() for p in limpo.split("/") if p.strip()]


def lugar_declarado_pela_fonte(source_id: str) -> dict:
    """O `SOURCE_LOCATION` que o contrato declara, conferido. Nunca inventado.

    Devolve sempre o recibo inteiro — o valor, a precisão, a regra original e o
    porquê. Quem chama escreve o `VALOR` no contrato de saída e a `BASE` no
    artefato de reprocessamento; a regra original nunca se perde
    (COL-LAW-203: *«NORMALIZAÇÃO NÃO DESTRÓI O VALOR ORIGINAL»*).
    """
    regra = (declarados().get(source_id) or {}).get("SOURCE_LOCATION_RULE")
    if not regra:
        return {"VALOR": NAO_SEI, "PRECISAO": NAO_SEI, "REGRA_ORIGINAL": NAO_SEI,
                "BASE": "o contrato de fonte nao declara SOURCE_LOCATION_RULE",
                "ESPECIE": "SOURCE_LOCATION",
                "AUTORIDADE": "regras/italy_contracts.mjs"}
    conhecidos = {n: p for n, p in fl.GAZETTEER}
    for nome in _candidatos_do_texto(regra):
        if nome in conhecidos:
            return {
                "VALOR": nome, "PRECISAO": conhecidos[nome],
                "REGRA_ORIGINAL": regra,
                "BASE": ("DECLARADO_NO_CONTRATO_DE_FONTE e conferido contra o "
                         "gazetteer de leis/fato_local.py"),
                "ESPECIE": "SOURCE_LOCATION",
                "AUTORIDADE": "regras/italy_contracts.mjs",
            }
    return {
        "VALOR": NAO_SEI, "PRECISAO": NAO_SEI, "REGRA_ORIGINAL": regra,
        "BASE": ("NOT_IN_GAZETTEER: o contrato declara «%s» e nenhum nome dentro "
                 "dela esta no gazetteer. NAO_IN_GAZETTEER nao e NOT_A_PLACE — e "
                 "falta de cobertura, e fica dizivel em vez de virar um valor "
                 "adivinhado." % regra[:120]),
        "ESPECIE": "SOURCE_LOCATION",
        "AUTORIDADE": "regras/italy_contracts.mjs",
    }


def regra_do_lugar_do_fato(source_id: str) -> str:
    """O `FACT_LOCATION_RULE`, tal e qual. NÃO é um valor — é onde procurar.

    ⚠️ E NÃO SE PROMOVE A `FACT_LOCATION`, nunca. Medido nos 13 contratos, duas
    das regras dizem literalmente o contrário de um valor:

        "UNKNOWN por padrao — so preencher se o proprio trabalho declarar"
        "UNKNOWN — artigo de empresa nao localiza fato de campo."

    e as outras mandam ir procurar no documento — a província do ficheiro, o
    comprensório impresso, a coordenada do ponto. Uma regra que manda procurar
    não é o que se procurou.

        SOURCE_LOCATION != FACT_LOCATION, e uma REGRA != um VALOR.
    """
    return (declarados().get(source_id) or {}).get("FACT_LOCATION_RULE") or NAO_SEI


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    d = declarados()
    print("contratos lidos: %d" % len(d))
    for sid in sorted(d):
        lugar = lugar_declarado_pela_fonte(sid)
        print("%-12s SOURCE_LOCATION=%-14s  %s"
              % (sid, lugar["VALOR"], especie_de_evidencia_declarada(sid)[:60]))
