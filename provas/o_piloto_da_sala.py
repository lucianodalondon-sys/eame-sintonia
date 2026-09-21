#!/usr/bin/env python3
# -*- coding: utf-8 -*-
u"""O PILOTO DA SALA — a Intelligence lê a Sala de Espera, e só ela.

    MISSAO   C-INT-PILOT-SALA-V1 · V2 · e a cirurgia C-CROP-E2E-V1 (v3)
    NATUREZA PILOTO ISOLADO, READ-ONLY. Não é Intelligence operacional.

O QUE ESTE FICHEIRO É
---------------------
A medição reprodutível de UMA pergunta:

    com o material JÁ ADMITIDO na Sala de Espera, o Sintonia consegue
    produzir cruzamento defensável?

E de uma segunda, que é a que dá o veredito honesto:

    quando o gate diz NÃO, ele diz NÃO?

O QUE ESTE FICHEIRO NÃO É
-------------------------
    NÃO É um INTELLIGENCE_RUN canônico — esse objeto não existe implementado.
    NÃO É dono de FACT, CLAIM, SIGNAL, FINDING nem OPPORTUNITY.
    NÃO escreve nada. Nem na Sala, nem no banco, nem no Portal.
    NÃO chama coletor, NÃO vai à rede, NÃO relê RAW fora da Sala.

Por isso tudo o que ele emite sai carimbado `*_CANDIDATE`, e o artefato
declara a que gate cada candidato ainda não respondeu.

⚠️ A TRAVA CONTINUA FECHADA, E ESTE FICHEIRO NÃO A ABRE
--------------------------------------------------------
`docs/operacao/TRAVA-DA-INTELIGENCIA.json` diz
`COLLECTION_FOUNDATION_CLOSED = NAO`, e a remedição no HEAD desta árvore
confirma: `ROUTE_CLASSES_ARCHITECTURE_CLOSED = 0 de 12` e
`ROUTE_CLASSES_REQUIRED_TOTAL = UNKNOWN`.

A trava permite explicitamente «medir o que a inteligencia futura vai esperar
da coleta». É isso, e só isso, que este ficheiro faz.

    LER E MEDIR != LIGAR SINAIS != PONTUAR E RECOMENDAR.

A ENTRADA
---------
    SALA DE ESPERA        public.sala_de_espera   (contrato READY, COL-LAW-043)
    REFERÊNCIA FACTUAL    referencia/adama/       (owner próprio; leitura e citação)
    SECÇÕES POR CULTURA   a derivação-irmã do MESMO item admitido, alcançada
                          pela referência canónica que a Sala já carrega (v3)

A referência ADAMA é ENTRADA B da Bíblia: a Intelligence pode ler e citar,
nunca fabricar. Nenhuma linha deste ficheiro escreve em `referencia/`.

⚠️ V3 — A CULTURA CHEGA, E CHEGA PELO PONTEIRO QUE A SALA JÁ TINHA
--------------------------------------------------------------------
A R2 mediu `CROP_LOST_IN_DERIVATION = 5/5` e escreveu: «ler a cultura do
corpo do texto para fechar o join seria fabricar a chave». Continua verdade.
O que mudou é que a Collection passou a preservar, como derivação do mesmo
original, a associação CABEÇALHO DE CULTURA → BLOCO que o documento declara
(`coleta/executor_secoes_por_cultura.py`). A Sala não muda: o grão da cultura
é a SECÇÃO, e o item continua a ser o documento. O que a Intelligence segue é

    sala.item_id = "derived:N" → derived_artifact N → parent_sha256
      → derived_artifact(kind=TABLE_EXTRACTION, producer=secoes-por-cultura)

Isto não relê RAW: lê uma derivação do item ADMITIDO, alcançada a partir da
linha da Sala. Só secções `EXPLICIT` (cabeçalho nomeia a cultura) entram no
gate; `CONTEXT_ONLY` («olivo» no corpo) e `UNKNOWN` continuam `NOT_POSSIBLE`.

COMO CORRER
-----------
    export PGPASSFILE=<pgpass do dono da Sala>
    python3 provas/o_piloto_da_sala.py --dsn "$SALA_DSN" --armazem <raiz>
    python3 provas/o_piloto_da_sala.py --dsn "$SALA_DSN" --desde 2026-09-20

`--desde` é a FASE 14: processa só o que pousou depois do carimbo, sem
scheduler, sem daemon, sem plataforma nova.

⚠️ `--desde` É UM FILTRO, NÃO UM CHECKPOINT — E A DIFERENÇA CUSTOU UMA RODADA
------------------------------------------------------------------------------
Uma data responde «o que pousou depois de quando?». Não responde «o que é que
eu já processei?», que é a pergunta da incrementalidade. As duas só coincidem
enquanto ninguém pousar um item com carimbo antigo, e ninguém correr o piloto
duas vezes no mesmo dia.

    FILTRO POR TEMPO  !=  CHECKPOINT POR IDENTIDADE.

O checkpoint é `--desde-artefato`: lê o artefato da corrida anterior e subtrai,
por `(RUN_ID, ORDEM)` — a chave que a própria migration 031 declara como
endereço da linha. `ITEM_ID` **não** serve: ele é o nome que a fonte deu, e
duas fontes podem dar o mesmo.

E o par que fecha a idempotência é `(RUN_ID, ORDEM) + PIPELINE_VERSION`:
reprocessar com a MESMA versão é ruído e sai vazio; mudar a versão obriga a
reprocessar, porque a lógica deixou de ser a mesma.
"""
import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import unicodedata

HERE = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(HERE)

# A referência factual. Owner: referencia/adama/. Aqui só se lê.
PORTFOLIO = os.path.join(RAIZ, "data", "samples", "IT-T4-001",
                         "IT-T4-001-adama-portfolio.json")
USOS = os.path.join(RAIZ, "referencia", "adama", "AUTHORIZED-USES.json")

# Universo agronômico: as famílias que carregam cultura/praga/limiar.
# T5 (academia), T7 (ordem profissional) e T9 (concorrente) entram na
# contagem mas não no crossing — e o artefato diz por quê, item a item.
FAMILIAS_AGRO = ("IT-T3",)

TERMOS_AGRO = (
    "COLTUR", "FITOSANITAR", "PARASSIT", "INFESTAZ", "TRATTAMENT", "SOGLIA",
    "OLIVO", "VITE", "POMODORO", "AGRUM", "BACTROCERA", "PERONOSPORA",
    "AFID", "TRAPPOL", "FENOLOG", "DISCIPLINARE", "AVVERSITA",
)
TERMOS_ADMIN = (
    "UNIVERSIT", "DIPARTIMENT", "REGOLAMENTO", "BANDO", "AVVISO",
    "CALLFORPAPERS", "ISCRIZION", "DOCENTE", "ATENEO", "CONSIGLIODI", "STATUTO",
)
# O limiar é declarado ANTES de olhar a saída. Mudá-lo depois de ver o
# resultado seria escolher o número que dá a resposta que se queria.
LIMIAR_AGRO = 20
LIMIAR_FRACO = 5

# ⚠️ A VERSÃO DO PIPELINE ENTRA NA CHAVE DE IDEMPOTÊNCIA.
# Reprocessar com a mesma versão é ruído. Mudar a régua, o limiar ou o gate
# muda a resposta — e aí reprocessar deixa de ser ruído e passa a ser dever.
# Quem mexer em LIMIAR_AGRO, TERMOS_AGRO ou `cruzar()` tem de subir isto.
# v3: `cruzar()` passou a ler CROP da derivação de secções. Sobe.
PIPELINE_VERSION = "3"

# As famílias que se ESPERA que tragam cultura. Um edital de universidade não
# tem cultura e isso não é defeito — por isso ele não entra no denominador.
FAMILIAS_QUE_ESPERAM_CROP = ("IT-T3",)

# Culturas italianas, como aparecem nos boletins. Esta lista NÃO é ontologia
# nem normalização canônica: é a sonda mínima para responder «o campo CROP
# sobreviveu à derivação?». Achar a palavra não promove nada a CROP — o
# contrato READY continua sem o campo, e é isso que a contagem mede.
SONDA_CROP = (
    "OLIVO", "OLIVE", "VITE", "UVA", "POMODORO", "AGRUMI", "ARANCIO",
    "LIMONE", "MELO", "PERO", "PESCO", "ACTINIDIA", "FRUMENTO", "GRANO",
    "MAIS", "PATATA", "CAROTA", "BARBABIETOLA", "FRAGOLA", "COLZA",
    "NOCCIOLO", "MANDORLO", "CILIEGIO", "SUSINO", "ALBICOCCO", "CARCIOFO",
)

# ── A DERIVAÇÃO DE SECÇÕES: a referência canónica, e só ela ─────────────────
# O nome do `kind` e do `producer` são os do executor que a escreve. Não se
# repete a lógica dele aqui: lê-se o artefato que ele deixou.
SECOES_KIND = "TABLE_EXTRACTION"
SECOES_PRODUCER = "secoes-por-cultura"
SECAO_EXPLICIT = "EXPLICIT"

# ── OS TRÊS ESTADOS DO GATE DE CULTURA ──────────────────────────────────────
CROP_AUTHORIZED = "AUTHORIZED"
CROP_NOT_AUTHORIZED = "NOT_AUTHORIZED"
CROP_UNKNOWN = "UNKNOWN"

# ── OS ESTADOS DO CROSSING, E O QUE CADA UM NÃO É ───────────────────────────
#   NOT_POSSIBLE       falta chave (cultura desconhecida, ou nem derivação)
#   BLOCKED_BY_CROP    a cultura é conhecida e o rótulo ADAMA NÃO a autoriza
#   CROP_GATE_PASSED   a cultura é conhecida e o rótulo a autoriza — e os
#                      gates seguintes (REGION, FACT_TIME) continuam abertos.
#                      NÃO é «possível», NÃO é oportunidade.
NOT_POSSIBLE = "NOT_POSSIBLE"
BLOCKED_BY_CROP = "BLOCKED_BY_CROP"
CROP_GATE_PASSED = "CROP_GATE_PASSED"


def normalizar(texto):
    u"""Dobra acento e pontuação. NÃO prova equivalência — só compara forma.

    INT-LAW-080: similaridade não prova equivalência. Por isso o resultado
    desta função nunca vira identidade: ela só encontra candidatos, e o
    gate de rótulo a seguir é quem decide.
    """
    s = unicodedata.normalize("NFKD", str(texto))
    s = s.encode("ascii", "ignore").decode()
    return re.sub(r"[^A-Z0-9]", "", s.upper())


def _psql(dsn, sql):
    u"""⚠️ OPÇÕES PRIMEIRO, DSN POR ÚLTIMO — a mesma cicatriz da Sala.

    O `getopt` do Windows pára de ler opções no primeiro não-opção. Com a DSN
    à frente, o `-f -` é ignorado, o processo liga-se e NÃO corre nada — e
    devolve 0. Um sucesso que não mediu coisa nenhuma.
    """
    binario = os.environ.get("SINTONIA_PSQL") or "psql"
    proc = subprocess.run(
        [binario, "-w", "-v", "ON_ERROR_STOP=1", "-At", "-f", "-", dsn],
        input=sql.encode("utf-8"), stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if proc.returncode != 0:
        erro = proc.stderr.decode("utf-8", "replace")
        # A DSN pode vir dentro do erro do psql. Nunca a deixar sair.
        raise SystemExit("psql falhou: " + re.sub(r"postgres(ql)?://\S+",
                                                  "<DSN>", erro))
    return proc.stdout.decode("utf-8", "replace")


def ler_sala(dsn, desde=None):
    u"""A ENTRADA CANÔNICA, e a única.

    ⚠️ Lê `sala_de_espera` e mais nada. Não toca em `raw_asset`, não toca no
    armazém, não abre ficheiro do disco. Se o item não foi admitido, ele não
    existe para esta função — que é exatamente o que INT-LAW-010 manda.
    """
    filtro = ""
    if desde:
        if not re.match(r"^\d{4}-\d{2}-\d{2}$", desde):
            raise SystemExit("--desde precisa de AAAA-MM-DD")
        filtro = "where pousado_em >= '%s'::timestamptz" % desde
    sql = """
select coalesce(json_agg(t order by t.source_id, t.ordem), '[]'::json) from (
  select run_id, ordem, item_id, raw_observation_id, universo, source_id,
         source_location, fact_location, fact_time, fact_time_basis,
         fact_location_basis, published_at, observed_at, captured_at,
         source_declared_evidence_class, admitido_por, estado_da_fila,
         estagio, texto
  from public.sala_de_espera %s) t;
""" % filtro
    return json.loads(_psql(dsn, sql).strip() or "[]")


def ler_secoes_por_cultura(dsn, itens, armazem):
    u"""A derivação-irmã de cada item admitido, pela REFERÊNCIA CANÓNICA.

    Não é uma segunda entrada: é o mesmo item, visto por outra receita. A
    consulta parte da LINHA DA SALA (`item_id = derived:N`) e só chega a
    `derived_artifact` por esse ponteiro — nunca por sha do texto, que a
    Bíblia mediu ambíguo, e nunca por caminho, nome ou fonte.

    Devolve {(RUN_ID, ORDEM): artefato JSON}. Sem `--armazem`, ou sem a
    derivação, o item simplesmente não tem secções — e o gate diz NOT_POSSIBLE
    pelo motivo antigo.
    """
    if not armazem or not itens:
        return {}
    alvo = {(i["run_id"], i["ordem"]) for i in itens
            if i["source_id"].startswith(FAMILIAS_AGRO)}
    if not alvo:
        return {}
    sql = """
select coalesce(json_agg(t), '[]'::json) from (
  select s.run_id, s.ordem, d.id as derived_id, i.id as secoes_id,
         i.storage_path
  from public.sala_de_espera s
  join public.derived_artifact d on s.item_id = 'derived:' || d.id
  join lateral (
    select x.id, x.storage_path from public.derived_artifact x
    where x.parent_sha256 = d.parent_sha256
      and x.kind = '%s' and x.producer = '%s'
    order by x.id desc limit 1) i on true
  where s.source_id like 'IT-T3%%') t;
""" % (SECOES_KIND, SECOES_PRODUCER)
    fora = {}
    for linha in json.loads(_psql(dsn, sql).strip() or "[]"):
        chave = (linha["run_id"], linha["ordem"])
        if chave not in alvo:
            continue
        caminho = os.path.join(armazem, linha["storage_path"])
        if not os.path.isfile(caminho):
            # A linha existe e o byte não. NÃO se inventa: fica sem secções,
            # e o artefato diz porquê.
            fora[chave] = {"_AUSENTE": caminho, "_SECOES_ID": linha["secoes_id"]}
            continue
        with open(caminho, encoding="utf-8") as fh:
            dados = json.load(fh)
        dados["_SECOES_ID"] = linha["secoes_id"]
        dados["_DERIVED_ID"] = linha["derived_id"]
        fora[chave] = dados
    return fora


def medir_crop(item, secoes=None):
    u"""O GARGALO DA PRIMEIRA RODADA, contado — e na v3 com a quarta resposta.

        NOT_EXPECTED         a família não devia trazer cultura (edital, FAQ)
        PRESENT              a derivação de secções nomeia a cultura (EXPLICIT)
        UNKNOWN_IN_DERIVED   a derivação existe e NÃO nomeia — só contexto ou
                             nada (ARIF: a cultura é um ícone)
        LOST_IN_DERIVATION   a cultura está no TEXTO, e não há derivação

    ⚠️ `PRESENT` só quando um CABEÇALHO declara. Menção no corpo não promove,
    e `UNKNOWN_IN_DERIVED` é a honestidade de dizer «olhei e não havia chave».
    """
    if not item["source_id"].startswith(FAMILIAS_QUE_ESPERAM_CROP):
        return "NOT_EXPECTED", []
    if secoes and "SECOES" in secoes:
        explicit = sorted({s["CROP_EXPLICIT"] for s in secoes["SECOES"]
                           if s["STATUS"] == SECAO_EXPLICIT})
        if explicit:
            return "PRESENT", explicit
        return "UNKNOWN_IN_DERIVED", []
    texto = normalizar(item["texto"])
    achadas = sorted({c for c in SONDA_CROP if c in texto})
    if achadas:
        return "LOST_IN_DERIVATION", achadas
    return "ABSENT_IN_TEXT", []


def classificar(item):
    u"""USABLE != INSUFFICIENT, e a razão fica escrita.

    Um documento administrativo de universidade é material verdadeiro,
    preservado e legitimamente admitido. Ele só não responde a uma pergunta
    agronômica — e isso é uma propriedade da PERGUNTA, não um defeito do item.
    """
    n = normalizar(item["texto"])
    agro = sum(n.count(t) for t in TERMOS_AGRO)
    admin = sum(n.count(t) for t in TERMOS_ADMIN)
    if agro >= LIMIAR_AGRO:
        classe = "USABLE_FOR_INTELLIGENCE"
        porque = "densidade agronômica %d >= %d" % (agro, LIMIAR_AGRO)
    elif agro >= LIMIAR_FRACO:
        classe = "WEAK"
        porque = "densidade agronômica %d entre %d e %d" % (
            agro, LIMIAR_FRACO, LIMIAR_AGRO)
    else:
        classe = "INSUFFICIENT_FOR_INTELLIGENCE"
        porque = ("densidade agronômica %d < %d; densidade administrativa %d"
                  % (agro, LIMIAR_FRACO, admin))
    return classe, porque, agro, admin


def ler_referencia_adama():
    u"""ENTRADA B — referência factual. LER E CITAR, nunca escrever."""
    with open(PORTFOLIO, encoding="utf-8") as fh:
        portfolio = json.load(fh)
    with open(USOS, encoding="utf-8") as fh:
        bruto = json.load(fh)
    usos = bruto.get("AUTHORIZED_USES") or bruto.get("RECORDS") \
        or list(bruto.values())[-1]

    vivos = [p for p in portfolio["produtos"] if p.get("vivo")]
    substancia_para_registos = {}
    for produto in vivos:
        for campo in produto["substancias_ativas"]:
            for uma in campo.split("|"):
                chave = normalizar(uma)
                if len(chave) >= 6:
                    substancia_para_registos.setdefault(chave, set()).add(
                        produto["num_registrazione"])
    return substancia_para_registos, usos, vivos


def gate_de_cultura(crop, culturas_no_rotulo):
    u"""O GATE DURO, agora com a chave a participar — e três respostas.

        AUTHORIZED      a cultura da secção está entre as culturas do rótulo
        NOT_AUTHORIZED  a cultura é conhecida e o rótulo NÃO a lista
        UNKNOWN         não há cultura (secção CONTEXT_ONLY/UNKNOWN, ou item
                        sem derivação) — e sem chave não há decisão

    A equivalência é a IGUALDADE DE CHAVE, e só ela. `leis/regua_italia.py`
    nomeia as culturas como o rótulo ADAMA as nomeia onde as duas se cruzam
    (OLIVO, VITE, AGRUMI, MELO, PERO, POMODORO, PESCO, FRAGOLA, ACTINIDIA...);
    o que não é igual não é equivalente (INT-LAW-081, INT-LAW-084). Chaves
    genéricas da régua (GRANO_GEN, ORTICOLE) nunca casam, e é assim que deve
    ser: «cereal» não é um rótulo.
    """
    if not crop:
        return CROP_UNKNOWN
    if culturas_no_rotulo is None:
        return CROP_UNKNOWN
    return CROP_AUTHORIZED if crop in set(culturas_no_rotulo) else CROP_NOT_AUTHORIZED


def _crossing(item, substancia, registos, reg_para_nome, culturas_no_rotulo,
              secao=None):
    crop = secao["CROP_EXPLICIT"] if secao and secao["STATUS"] == SECAO_EXPLICIT else None
    gate = gate_de_cultura(crop, culturas_no_rotulo)
    if gate == CROP_AUTHORIZED:
        estado = CROP_GATE_PASSED
        presentes = ["ACTIVE_INGREDIENT", "CROP"]
        faltam = ["REGION", "FACT_TIME"]
        porque = ("a cultura da secção (%s) tem rótulo ADAMA para esta substância. "
                  "O gate de cultura PASSOU; REGION e FACT_TIME continuam sem "
                  "chave — o crossing não fecha, e isto não é oportunidade." % crop)
    elif gate == CROP_NOT_AUTHORIZED:
        estado = BLOCKED_BY_CROP
        presentes = ["ACTIVE_INGREDIENT", "CROP"]
        faltam = ["REGION", "FACT_TIME"]
        porque = ("a cultura da secção (%s) NÃO está no rótulo ADAMA desta "
                  "substância (%s). Bloqueado pela chave — que é o que o gate "
                  "existe para fazer." % (crop, ", ".join(culturas_no_rotulo) or "—"))
    else:
        estado = NOT_POSSIBLE
        presentes = ["ACTIVE_INGREDIENT"]
        faltam = ["CROP", "REGION", "FACT_TIME"]
        if secao is None:
            porque = ("este item não tem derivação de secções; a Sala não carrega "
                      "CROP e ler a cultura do corpo seria fabricar a chave "
                      "(INT-LAW-037).")
        else:
            porque = ("a secção é %s: o documento não NOMEIA a cultura num "
                      "cabeçalho (candidatos no corpo: %s). Sem chave declarada "
                      "não há decisão." % (
                          secao["STATUS"],
                          ", ".join(c["CROP"] for c in secao["CROP_CONTEXT"]["CANDIDATES"]) or "nenhum"))
    sufixo = ("-s%d" % secao["ORDEM"]) if secao is not None else ""
    return {
        "CROSSING_ID": "XC-%s-%s%s-%s" % (item["source_id"], item["ordem"], sufixo,
                                          substancia[:12]),
        "QUESTION": ("a substância que o boletim recomenda tem rótulo "
                     "ADAMA autorizado para a cultura deste boletim?"),
        "SOURCE_ITEM": {
            "SOURCE_ID": item["source_id"],
            "RUN_ID": item["run_id"],
            "ORDEM": item["ordem"],
            "RAW_OBSERVATION_ID": item["raw_observation_id"],
        },
        "SECTION": (None if secao is None else {
            "ORDEM": secao["ORDEM"], "KIND": secao["KIND"],
            "STATUS": secao["STATUS"], "CROP_EXPLICIT": secao["CROP_EXPLICIT"],
            "CROP_TERM_AS_WRITTEN": secao["CROP_TERM_AS_WRITTEN"],
            "PRECISION": secao["PRECISION"], "CERTEZA": secao["CERTEZA"],
            "EVIDENCE_ANCHOR": secao["EVIDENCE_ANCHOR"],
        }),
        "ACTIVE_INGREDIENT_OBSERVED": substancia,
        "ADAMA_REGISTRATIONS_WITH_THIS_AI": registos,
        "ADAMA_PRODUCTS": sorted({reg_para_nome.get(r, "?") for r in registos}),
        "ADAMA_CROPS_ON_LABEL": culturas_no_rotulo,
        "CROP_KEY": crop,
        "CROP_GATE": gate,
        "JOIN_KEYS_REQUIRED": ["ACTIVE_INGREDIENT", "CROP", "REGION", "FACT_TIME"],
        "JOIN_KEYS_PRESENT": presentes,
        "JOIN_KEYS_MISSING": faltam,
        "CROSSING_STATE": estado,
        "WHY": porque,
        "STATUS": "EVIDENCE_LINKED_OBSERVATION",
    }


def cruzar(itens, substancias, usos, vivos, secoes_por_item=None):
    u"""O CRUZAMENTO, e o gate que o mata quando ele não se sustenta.

    Aparecer a mesma palavra em dois documentos NÃO é crossing (INT-LAW-037).
    O que promove um candidato aqui é responder a uma pergunta com chave:

        esta substância, que o boletim recomenda,
        tem rótulo ADAMA AUTORIZADO para ESTA cultura?

    ⚠️ ATÉ À V2 ELE FALHAVA FECHADO SEMPRE — E ISSO NÃO ERA SABER DECIDIR.
    A 2ª rodada mediu (defeito D-01): `cruzar()` nunca lia cultura de lado
    nenhum e devolvia `NOT_POSSIBLE` mesmo com «MELO» escrito no texto.
    Recusar sempre pelo motivo certo != saber distinguir.

    V3: a cultura entra pela derivação de secções do MESMO item admitido, e
    só quando um CABEÇALHO a declara (`EXPLICIT`). O crossing passa a ser por
    (item, secção, substância), com três saídas:

        CROP_GATE_PASSED   cultura no rótulo   → segue para o gate seguinte
        BLOCKED_BY_CROP    cultura fora do rótulo → bloqueia
        NOT_POSSIBLE       cultura desconhecida → sem decisão

    Nenhuma das três é oportunidade. REGION e FACT_TIME continuam por chegar,
    e `OPPORTUNITY_CANDIDATES` continua 0 enquanto não chegarem.
    """
    secoes_por_item = secoes_por_item or {}
    reg_para_nome = {p["num_registrazione"]: p["produto"] for p in vivos}
    achados = []
    for item in sorted(itens, key=lambda x: (x["source_id"], x["ordem"])):
        if not item["source_id"].startswith(FAMILIAS_AGRO):
            continue
        secoes = secoes_por_item.get((item["run_id"], item["ordem"]))
        unidades = ([(s, normalizar(s["TEXTO"])) for s in secoes["SECOES"]]
                    if secoes and "SECOES" in secoes
                    else [(None, normalizar(item["texto"]))])
        for secao, texto in unidades:
            for substancia in sorted(substancias):
                if substancia not in texto:
                    continue
                registos = sorted(substancias[substancia])
                # O GATE DURO: cultura da SECÇÃO × cultura no RÓTULO.
                culturas_no_rotulo = sorted({
                    u["CROP_ON_LABEL"] for u in usos
                    if u["REGISTRATION_NUMBER"] in registos})
                achados.append(_crossing(item, substancia, registos, reg_para_nome,
                                         culturas_no_rotulo, secao))
    return achados


def main():
    parser = argparse.ArgumentParser(description="O piloto da Sala de Espera")
    parser.add_argument("--dsn", required=True, help="DSN da Sala canônica")
    parser.add_argument("--desde", help="AAAA-MM-DD — filtro por tempo")
    parser.add_argument("--desde-artefato", dest="desde_artefato",
                        help="artefato da corrida anterior — CHECKPOINT por "
                             "identidade (RUN_ID, ORDEM). Vence --desde.")
    parser.add_argument("--armazem", help="raiz do armazém onde vivem as "
                                          "derivações de secções (v3)")
    parser.add_argument("--json", help="onde gravar o artefato")
    args = parser.parse_args()

    itens = ler_sala(args.dsn, args.desde)

    # ── O CHECKPOINT ────────────────────────────────────────────────────
    # Subtrai por identidade, não por tempo. E conta o que DESAPARECEU:
    # um item processado que já não está na Sala é um facto sobre a Sala,
    # não um erro de contagem — e ficaria invisível num filtro por data.
    processados_antes = set()
    sumidos = []
    versao_anterior = None
    if args.desde_artefato:
        with open(args.desde_artefato, encoding="utf-8") as fh:
            anterior = json.load(fh)
        versao_anterior = anterior.get("PIPELINE_VERSION")
        processados_antes = {(c["RUN_ID"], c["ORDEM"])
                             for c in anterior.get("CENSO", [])}
        presentes = {(i["run_id"], i["ordem"]) for i in itens}
        sumidos = sorted(processados_antes - presentes)
        if versao_anterior == PIPELINE_VERSION:
            itens = [i for i in itens
                     if (i["run_id"], i["ordem"]) not in processados_antes]
        else:
            # A lógica mudou. Reprocessar TUDO deixa de ser desperdício e
            # passa a ser obrigação: a resposta de v1 não é a resposta de v2.
            sys.stderr.write(
                "PIPELINE_VERSION mudou (%s -> %s): reprocessando tudo\n"
                % (versao_anterior, PIPELINE_VERSION))

    substancias, usos, vivos = ler_referencia_adama()
    secoes_por_item = ler_secoes_por_cultura(args.dsn, itens, args.armazem)

    censo = []
    for item in itens:
        classe, porque, agro, admin = classificar(item)
        secoes = secoes_por_item.get((item["run_id"], item["ordem"]))
        estado_crop, culturas = medir_crop(item, secoes)
        censo.append({
            "SOURCE_ID": item["source_id"],
            "RUN_ID": item["run_id"],
            "ORDEM": item["ordem"],
            "ITEM_ID": item["item_id"],
            "RAW_OBSERVATION_ID": item["raw_observation_id"],
            "UNIVERSO": item["universo"],
            "ESTAGIO": item["estagio"],
            "TEXTO_CARACTERES": len(item["texto"]),
            "FACT_TIME": item["fact_time"],
            "FACT_LOCATION": item["fact_location"],
            "SOURCE_LOCATION": item["source_location"],
            "PUBLISHED_AT": item["published_at"],
            "CAPTURED_AT": item["captured_at"],
            "EVIDENCE_CLASS": item["source_declared_evidence_class"],
            "CLASSE": classe,
            "PORQUE": porque,
            "DENSIDADE_AGRO": agro,
            "DENSIDADE_ADMIN": admin,
            "CROP_STATE": estado_crop,
            "CROP_OBSERVED_IN_TEXT": (
                culturas if estado_crop != "PRESENT"
                else sorted({c for c in SONDA_CROP if c in normalizar(item["texto"])})),
            "CROP_EXPLICIT": culturas if estado_crop == "PRESENT" else [],
            "CROP_SECOES_DERIVED_ID": (secoes or {}).get("_SECOES_ID"),
            "CROP_SECOES_RESUMO": (secoes or {}).get("RESUMO"),
            "CROP_SECOES_BYTES_AUSENTES": (secoes or {}).get("_AUSENTE"),
        })

    crossings = cruzar(itens, substancias, usos, vivos, secoes_por_item)

    # A contagem de independência. Texto idêntico NÃO é evidência nova
    # (INT-LAW-070..077): três source_id diferentes com o mesmo md5 são
    # UMA observação, não três.
    #
    # ⚠️ A DEPENDÊNCIA MEDE-SE CONTRA A SALA INTEIRA, NÃO CONTRA O DELTA.
    # Um item novo que repete o texto de um item JÁ PROCESSADO é dependente
    # — e olhar só para o delta não o veria, porque o gémeo dele ficou de
    # fora do recorte. Medido na 2ª rodada: 12 dos 17 novos eram re-observação
    # de texto que já estava na Sala. Vistos só entre si, pareciam 15 textos
    # distintos; contra a Sala inteira, eram 3.
    #
    #     NOVO NA FILA  !=  NOVO COMO EVIDÊNCIA.
    todos = ler_sala(args.dsn, None)
    delta = {(i["run_id"], i["ordem"]) for i in itens}
    por_impressao = {}
    for item in todos:
        chave = hashlib.md5(item["texto"].encode("utf-8")).hexdigest()
        por_impressao.setdefault(chave, []).append(item["source_id"])

    # Quantos itens do delta trazem texto que a Sala JÁ tinha antes dele?
    md5_ja_processado = {
        hashlib.md5(i["texto"].encode("utf-8")).hexdigest()
        for i in todos if (i["run_id"], i["ordem"]) not in delta}
    redundantes = [
        {"SOURCE_ID": i["source_id"], "RUN_ID": i["run_id"],
         "ORDEM": i["ordem"], "RAW_OBSERVATION_ID": i["raw_observation_id"]}
        for i in itens
        if hashlib.md5(i["texto"].encode("utf-8")).hexdigest()
        in md5_ja_processado]

    artefato = {
        "SCHEMA": "sintonia.intelligence.piloto-da-sala/1",
        "PIPELINE_VERSION": PIPELINE_VERSION,
        "O_QUE_ISTO_E": (
            "medição read-only da Sala de Espera. NÃO é INTELLIGENCE_RUN "
            "canônico, NÃO produz FACT, FINDING nem OPPORTUNITY."),
        "TRAVA_DA_INTELIGENCIA": "COLLECTION_FOUNDATION_CLOSED = NAO",
        "ENTRADA_A": "public.sala_de_espera",
        "ENTRADA_B": "referencia/adama/ (lida e citada, nunca escrita)",
        "ENTRADA_A_SECOES": (
            "derivação-irmã do item admitido, por sala.item_id=derived:N -> "
            "parent_sha256 -> derived_artifact(kind=%s, producer=%s); armazém=%s"
            % (SECOES_KIND, SECOES_PRODUCER, args.armazem or "NAO DADO")),
        "FILTRO_INCREMENTAL": args.desde or "TODOS",
        "CHECKPOINT": {
            "MODO": ("IDENTIDADE (RUN_ID, ORDEM)" if args.desde_artefato
                     else "NENHUM — corrida completa"),
            "ARTEFATO_ANTERIOR": args.desde_artefato,
            "PIPELINE_VERSION_ANTERIOR": versao_anterior,
            "PREVIOUSLY_PROCESSED": len(processados_antes),
            "PROCESSADOS_QUE_SUMIRAM_DA_SALA": [
                {"RUN_ID": r, "ORDEM": o} for r, o in sumidos],
        },
        "SALA_TOTAL": len(itens),
        "SALA_USABLE_FOR_INTELLIGENCE": sum(
            1 for c in censo if c["CLASSE"] == "USABLE_FOR_INTELLIGENCE"),
        "SALA_WEAK": sum(1 for c in censo if c["CLASSE"] == "WEAK"),
        "SALA_INSUFFICIENT": sum(
            1 for c in censo if c["CLASSE"] == "INSUFFICIENT_FOR_INTELLIGENCE"),
        # ── CROP: o gargalo, contado ────────────────────────────────────
        "ITEMS_EXPECTING_CROP": sum(
            1 for c in censo if c["CROP_STATE"] != "NOT_EXPECTED"),
        "ITEMS_WITH_CROP": sum(
            1 for c in censo if c["CROP_STATE"] == "PRESENT"),
        "ITEMS_MISSING_CROP": sum(
            1 for c in censo if c["CROP_STATE"] in
            ("LOST_IN_DERIVATION", "ABSENT_IN_TEXT", "UNKNOWN_IN_DERIVED")),
        "CROP_LOST_IN_DERIVATION": sum(
            1 for c in censo if c["CROP_STATE"] == "LOST_IN_DERIVATION"),
        "CROP_UNKNOWN_IN_DERIVED": sum(
            1 for c in censo if c["CROP_STATE"] == "UNKNOWN_IN_DERIVED"),
        "DELTA_REDUNDANTE_VS_SALA": len(redundantes),
        "DELTA_REDUNDANTE_ITENS": redundantes,
        "SALA_INTEIRA_ITENS": len(todos),
        "TEXTOS_DISTINTOS": len(por_impressao),
        "OBSERVACOES_DUPLICADAS": {
            k[:12]: v for k, v in por_impressao.items() if len(v) > 1},
        "FACT_TIME_CONHECIDO": sum(
            1 for c in censo if c["FACT_TIME"] != "NAO SEI"),
        "FACT_LOCATION_CONHECIDO": sum(
            1 for c in censo if c["FACT_LOCATION"] != "NAO SEI"),
        "CLAIM_CANDIDATES": 0,
        "FACT_CANDIDATES": 0,
        "FINDINGS": 0,
        "CROSSINGS_TENTADOS": len(crossings),
        # «Possível» continua a querer dizer «todas as chaves presentes».
        # Nenhum crossing chega lá: REGION e FACT_TIME não atravessam.
        "CROSSINGS_POSSIVEIS": sum(
            1 for c in crossings if not c["JOIN_KEYS_MISSING"]),
        "CROSSINGS_CROP_GATE_PASSED": sum(
            1 for c in crossings if c["CROSSING_STATE"] == CROP_GATE_PASSED),
        "CROSSINGS_BLOCKED_BY_CROP": sum(
            1 for c in crossings if c["CROSSING_STATE"] == BLOCKED_BY_CROP),
        "CROSSINGS_NOT_POSSIBLE": sum(
            1 for c in crossings if c["CROSSING_STATE"] == NOT_POSSIBLE),
        "CROSSING_STATES_OBSERVED": sorted({c["CROSSING_STATE"] for c in crossings}),
        "OPPORTUNITY_CANDIDATES": 0,
        "PORQUE_ZERO_OPPORTUNITY": (
            "NO_DEFENSIBLE_ACTION_YET — nenhum crossing fechou todas as join "
            "keys (REGION e FACT_TIME continuam ausentes). Produzir oportunidade "
            "aqui seria fabricar."),
        "CENSO": censo,
        "CROSSINGS": crossings,
    }

    saida = json.dumps(artefato, ensure_ascii=False, indent=2)
    if args.json:
        with open(args.json, "w", encoding="utf-8") as fh:
            fh.write(saida + "\n")
        print("artefato: %s" % args.json)
    print("SALA_TOTAL                   = %d" % artefato["SALA_TOTAL"])
    print("SALA_USABLE_FOR_INTELLIGENCE = %d"
          % artefato["SALA_USABLE_FOR_INTELLIGENCE"])
    print("SALA_INSUFFICIENT            = %d" % artefato["SALA_INSUFFICIENT"])
    print("ITEMS_EXPECTING_CROP         = %d" % artefato["ITEMS_EXPECTING_CROP"])
    print("ITEMS_WITH_CROP              = %d" % artefato["ITEMS_WITH_CROP"])
    print("CROP_LOST_IN_DERIVATION      = %d"
          % artefato["CROP_LOST_IN_DERIVATION"])
    print("CROP_UNKNOWN_IN_DERIVED      = %d"
          % artefato["CROP_UNKNOWN_IN_DERIVED"])
    print("DELTA_REDUNDANTE_VS_SALA     = %d"
          % artefato["DELTA_REDUNDANTE_VS_SALA"])
    print("CROSSINGS_TENTADOS           = %d" % artefato["CROSSINGS_TENTADOS"])
    print("CROSSINGS_CROP_GATE_PASSED   = %d"
          % artefato["CROSSINGS_CROP_GATE_PASSED"])
    print("CROSSINGS_BLOCKED_BY_CROP    = %d"
          % artefato["CROSSINGS_BLOCKED_BY_CROP"])
    print("CROSSINGS_NOT_POSSIBLE       = %d"
          % artefato["CROSSINGS_NOT_POSSIBLE"])
    print("CROSSINGS_POSSIVEIS          = %d" % artefato["CROSSINGS_POSSIVEIS"])
    print("OPPORTUNITY_CANDIDATES       = %d"
          % artefato["OPPORTUNITY_CANDIDATES"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
