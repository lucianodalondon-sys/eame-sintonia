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

import calendar
import hashlib
import json
import os
import re
import sys
from datetime import date, datetime, timezone
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
for _gaveta in ("provas", "leis"):
    if str(RAIZ / _gaveta) not in sys.path:
        sys.path.insert(0, str(RAIZ / _gaveta))

# O VOCABULARIO VEM DA ESPINHA, E NAO E COPIADO. Duas listas do mesmo contrato
# divergem, e no dia em que divergissem a corrida media uma coisa e o contrato
# exigia outra.
from espinha_da_intelligence import (           # noqa: E402
    CAMPOS_DO_READY, NAO_SEI, PALAVRAS_QUE_O_REQUISITO_RECUSA,
)
# Os meses italianos tem UM dono: o leitor italiano da casa. Uma segunda lista
# aqui seria a segunda verdade que a espinha proibe.
from fato_local import MES_NUM                  # noqa: E402

CONTRATO = "CORRIDA_DA_INTELLIGENCE/v1"
#: ⚠️ G0/v2 (INT-CONSERTOS-EXP, D1-D4/D6). A v1 aceitava como ancora de tempo
#: qualquer texto que nao comecasse por «NAO SEI»: «UNKNOWN», um valor sem base,
#: uma data sem ano e um evento ainda por acontecer viravam SINAL. Mudar o portao
#: muda a resposta; por isso a versao sobe e entra na identidade da corrida.
RULESET_VERSION = "G0/v2"

BIBLIA = RAIZ / "BIBLIA-DE-ENGENHARIA-DA-INTELLIGENCE.md"
REGISTO_DAS_AUTORIDADES = RAIZ / "controle" / "AUTORIDADES-CANONICAS.json"
CARTAO_DA_BIBLIA = "A-BIBLIA-ENG-INTELIGENCIA"


def carimbo_da_biblia(biblia: Path = BIBLIA,
                      registo: Path = REGISTO_DAS_AUTORIDADES) -> dict:
    """D7 · a Biblia EFETIVA, lida do cabecalho dela e conferida no registo.

    ⚠️ A V1 TINHA A VERSAO ESCRITA A MAO — «V0.2 CANONICAL» — e a lei ja era a
    V0.3. Um carimbo digitado mente no dia em que a lei muda e ninguem edita o
    motor (INT-LAW-052: o run preserva a configuracao EFETIVA).

    Duas fontes, e as duas tem de dizer o mesmo: o cabecalho da Biblia (quem ela
    diz que e) e o registo do Control Plane (quem a casa diz que ela e). Se
    discordarem, ou faltar uma, o carimbo diz `NAO SEI` com o porque — nunca
    escolhe uma das duas.
    """
    try:
        bruto = biblia.read_bytes()
    except OSError as erro:
        return {"BIBLE_VERSION": f"{NAO_SEI} — Biblia ilegivel: {erro}",
                "BIBLE_FILE_SHA256": NAO_SEI}
    cabeca = bruto[:4000].decode("utf-8", "replace")

    def campo(nome):
        m = re.search(r"^%s\s*=\s*(\S+)\s*$" % nome, cabeca, re.M)
        return m.group(1) if m else None

    bid, ver, sts = campo("BIBLE_ID"), campo("VERSION"), campo("STATUS")
    sha = hashlib.sha256(bruto).hexdigest()
    try:
        cartoes = json.loads(registo.read_text(encoding="utf-8"))["AUTHORITIES"]
        cartao = next(a for a in cartoes if a.get("CARD_ID") == CARTAO_DA_BIBLIA)
        reg_ver, reg_sts = cartao.get("VERSION"), cartao.get("LIFECYCLE")
    except (OSError, ValueError, KeyError, StopIteration) as erro:
        reg_ver = reg_sts = None
        porque_reg = f"registo ilegivel ou sem {CARTAO_DA_BIBLIA}: {erro!r}"
    else:
        porque_reg = None
    if not (bid and ver and sts):
        versao = f"{NAO_SEI} — o cabecalho da Biblia nao declara BIBLE_ID/VERSION/STATUS"
    elif porque_reg:
        versao = f"{NAO_SEI} — {porque_reg}"
    elif (ver, sts) != (reg_ver, reg_sts):
        versao = (f"{NAO_SEI} — o cabecalho diz {ver} {sts}, "
                  f"o registo diz {reg_ver} {reg_sts}")
    else:
        versao = f"{bid} {ver} {sts}"
    return {"BIBLE_VERSION": versao, "BIBLE_FILE_SHA256": sha}

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
                        # A lei efetiva faz parte da configuracao: mudar a Biblia
                        # e mudar a pergunta, e o reuso deixa de ser provavel.
                        "BIBLE": carimbo_da_biblia()["BIBLE_FILE_SHA256"],
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
    if valor is None or valor == "":
        return True
    if not isinstance(valor, str):
        return False
    s = valor.strip().upper()
    # ⚠️ D1 · A V1 SO CONHECIA «NAO SEI». A Sala real traz a mesma ignorancia
    # escrita pelos coletores em ingles — «UNKNOWN», «NOT_KNOWN» — e ela passava
    # como se fosse um valor. Ignorancia nao muda de natureza ao mudar de lingua.
    return s.startswith(PALAVRAS_DE_IGNORANCIA) or s in ("?", "-", "NONE", "NULL")


#: As maneiras como a casa escreve «nao sei». `NAO SEI` e a da porta; as outras
#: sao as dos coletores e do leitor italiano (`fato_local` devolve NOT_KNOWN).
PALAVRAS_DE_IGNORANCIA = (NAO_SEI, "NAO_SEI", "UNKNOWN", "NOT_KNOWN")


def base_ignorante(base) -> bool:
    """D2 · a BASE de um valor diz se ele foi provado. Sem base, nao ancora.

    A base e texto livre da Collection («EVENTO · ESCRITO_NO_TEXTO · DATE_EXACT ·
    ancora ...»). Ela e ignorancia quando comeca por uma palavra de ignorancia OU
    quando declara, em qualquer ponto, que o proprio coletor nao sabia
    («o coletor declarou: «UNKNOWN — ...»»). INT-LAW-062: PROVED exige razao.
    """
    if e_ignorancia(base):
        return True
    return bool(re.search(r"\b(UNKNOWN|NOT_KNOWN|NAO SEI)\b", str(base).upper()))


_ISO = re.compile(r"(?<!\d)(\d{4})-(\d{2})-(\d{2})(?!\d)")
_ANO = re.compile(r"\b(19\d{2}|20\d{2})\b")
_DIAS_MES_ANO = re.compile(
    r"\b(\d{1,2})(?:\s*[-–]\s*(\d{1,2}))?\s+(%s)\s+(19\d{2}|20\d{2})\b" % "|".join(MES_NUM))
_MES_ANO = re.compile(r"\b(%s)\s+(19\d{2}|20\d{2})\b" % "|".join(MES_NUM))


def _dia(a, m, d):
    try:
        return date(int(a), int(m), int(d))
    except ValueError:
        return None


def _fim_do_mes(a, m):
    return date(a, m, calendar.monthrange(a, m)[1])


def intervalo_do_tempo(valor) -> dict:
    """D3 · o INTERVALO que um FACT_TIME escrito cobre — ou porque nao cobre nenhum.

    So le o valor que a Collection ja entregou; nao vai ao texto, nao completa.
    Sem ANO nao ha intervalo: «21-23 ottobre» pode ser deste ano, do passado ou
    do proximo, e escolher um seria fabricar o tempo do facto (INT-LAW-100).

        → {"ESTADO": "INTERVALO" | "SEM_ANO" | "NAO_ANALISAVEL",
           "INICIO": "AAAA-MM-DD"|None, "FIM": ..., "PRECISAO": ...}
    """
    s = str(valor).strip().lower()
    isos = [d for d in (_dia(*t) for t in _ISO.findall(s)) if d]
    if isos:
        return {"ESTADO": "INTERVALO", "INICIO": min(isos).isoformat(),
                "FIM": max(isos).isoformat(),
                "PRECISAO": "DIA" if len(set(isos)) == 1 else "INTERVALO_DE_DIAS"}
    m = _DIAS_MES_ANO.search(s)
    if m:
        a, mes = int(m.group(4)), MES_NUM[m.group(3)]
        ini = _dia(a, mes, m.group(1))
        fim = _dia(a, mes, m.group(2) or m.group(1))
        if ini and fim and ini <= fim:
            return {"ESTADO": "INTERVALO", "INICIO": ini.isoformat(),
                    "FIM": fim.isoformat(),
                    "PRECISAO": "DIA" if ini == fim else "INTERVALO_DE_DIAS"}
        return {"ESTADO": "NAO_ANALISAVEL", "INICIO": None, "FIM": None,
                "PRECISAO": NAO_SEI}
    m = _MES_ANO.search(s)
    if m:
        a, mes = int(m.group(2)), MES_NUM[m.group(1)]
        return {"ESTADO": "INTERVALO", "INICIO": date(a, mes, 1).isoformat(),
                "FIM": _fim_do_mes(a, mes).isoformat(), "PRECISAO": "MES"}
    anos = sorted({int(x) for x in _ANO.findall(s)})
    # «2025/26» e uma SAFRA: cobre os dois anos. So quando o segundo e o seguinte
    # do primeiro — «2011-2025» e serie historica, e fica como os anos que diz.
    for a, b in re.findall(r"\b(19\d{2}|20\d{2})\s*/\s*(\d{2})\b", s):
        if (int(a) + 1) % 100 == int(b):
            anos = sorted(set(anos) | {int(a) + 1})
    if anos:
        return {"ESTADO": "INTERVALO", "INICIO": date(anos[0], 1, 1).isoformat(),
                "FIM": date(anos[-1], 12, 31).isoformat(),
                "PRECISAO": "ANO" if len(anos) == 1 else "ANOS"}
    tem_mes_ou_dia = any(mes in s for mes in MES_NUM) or re.search(r"\b\d{1,2}\b", s)
    return {"ESTADO": "SEM_ANO" if tem_mes_ou_dia else "NAO_ANALISAVEL",
            "INICIO": None, "FIM": None, "PRECISAO": NAO_SEI}


def _dia_da_captura(item: dict):
    """O dia em que a Collection OBSERVOU o documento (COLLECTED_TIME)."""
    v = item.get("CAPTURED_AT")
    if e_ignorancia(v):
        return None
    m = _ISO.search(str(v))
    return _dia(*m.groups()) if m else None


def portao_g0(item: dict) -> tuple:
    """`(passou, o_que_falta)`. O unico portao desta corrida.

    Ele NAO julga o conteudo: pergunta se da para saber sobre QUEM o item fala,
    de ONDE veio e QUANDO o facto aconteceu. Sem isso nenhuma leitura analitica
    e ancoravel — e uma leitura nao ancoravel e uma invencao com fonte.

    ⚠️ G0/v2. «QUANDO» deixou de ser «o campo nao diz NAO SEI». Passou a ser:

        D1  o valor nao e ignorancia, em nenhuma das linguas da casa;
        D2  a BASE do valor nao e ignorancia (valor sem razao nao e prova);
        D3  o valor cobre um intervalo com ANO;
        D4  o intervalo COMECA ate ao dia em que o documento foi observado.
            Um evento anunciado para depois da captura ainda nao aconteceu:
            data futura nao e facto (Biblia §28). Sem dia de captura, nao ha
            como saber — e NAO SEI bloqueia, nao passa.

    Cada motivo sai com nome proprio em `o_que_falta` («FACT_TIME:SEM_BASE»),
    para o livro dizer POR QUE o tempo nao ancorou, e nao so QUE nao ancorou.
    """
    falta = [c for c in G0_EXIGE if e_ignorancia(item.get(c))]
    if "FACT_TIME" not in falta:
        if base_ignorante(item.get("FACT_TIME_BASIS")):
            falta.append("FACT_TIME:SEM_BASE")
        tempo = intervalo_do_tempo(item.get("FACT_TIME"))
        if tempo["ESTADO"] == "SEM_ANO":
            falta.append("FACT_TIME:SEM_ANO")
        elif tempo["ESTADO"] != "INTERVALO":
            falta.append("FACT_TIME:NAO_ANALISAVEL")
        else:
            captura = _dia_da_captura(item)
            if captura is None:
                falta.append("FACT_TIME:CAPTURA_DESCONHECIDA_FUTURO_NAO_EXCLUIDO")
            elif date.fromisoformat(tempo["INICIO"]) > captura:
                falta.append("FACT_TIME:FUTURO_EM_RELACAO_A_CAPTURA")
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
            f"{NAO_SEI}, sem base, sem ano, depois da captura, ou nao chegaram "
            "de todo. Preenche-los aqui seria a "
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
                                    "RULESET_VERSION", "CODE_VERSION",
                                    "BIBLE_FILE_SHA256"]
        return copia

    livro = {
        "SCHEMA": CONTRATO,
        "INTELLIGENCE_RUN_ID": run_id,
        "REQUEST_ID": request_id,
        "QUESTION": pergunta,
        "START": _agora(),
        "END": None,
        "RULESET_VERSION": RULESET_VERSION,
        **carimbo_da_biblia(),
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
                tempo = intervalo_do_tempo(item.get("FACT_TIME"))
                base_lugar = item.get("FACT_LOCATION_BASIS", NAO_SEI)
                lugar = item.get("FACT_LOCATION", NAO_SEI)
                livro["SIGNALS"].append({
                    "SIGNAL_ID": "SG-" + hashlib.sha256(
                        (run_id + "|" + str(ref["ITEM_ID"])).encode()).hexdigest()[:16],
                    "ITEM_ID": ref["ITEM_ID"],
                    "RAW_OBSERVATION_ID": ref["RAW_OBSERVATION_ID"],
                    "SOURCE_ID": ref["SOURCE_ID"],
                    "FACT_TIME": item.get("FACT_TIME"),
                    # ⚠️ D6 · O SINAL LEVA A BASE, NAO SO O VALOR. A v1 copiava
                    # FACT_TIME e FACT_LOCATION e deixava a razao na porta: quem
                    # lesse o sinal via «Napoli» sem saber se era o lugar do facto
                    # provado ou um palpite. Valor sem base e meia prova.
                    "FACT_TIME_BASIS": item.get("FACT_TIME_BASIS", NAO_SEI),
                    "FACT_TIME_INTERVALO": tempo,
                    "FACT_LOCATION": lugar,
                    "FACT_LOCATION_BASIS": base_lugar,
                    # O lugar NAO e apagado nem completado: fica como veio, e diz
                    # se ancora. SOURCE_LOCATION nunca entra aqui (INT-LAW-101).
                    "FACT_LOCATION_ESTADO": (
                        NAO_SEI if e_ignorancia(lugar)
                        else "SEM_BASE_NAO_ANCORA" if base_ignorante(base_lugar)
                        else "COM_BASE"),
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
