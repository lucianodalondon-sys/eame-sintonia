#!/usr/bin/env python3
# -*- coding: utf-8 -*-
u"""O PILOTO DA SALA — a Intelligence lê a Sala de Espera, e só ela.

    MISSAO   C-INT-PILOT-SALA-V1
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

A referência ADAMA é ENTRADA B da Bíblia: a Intelligence pode ler e citar,
nunca fabricar. Nenhuma linha deste ficheiro escreve em `referencia/`.

COMO CORRER
-----------
    export PGPASSFILE=<pgpass do dono da Sala>
    python3 provas/o_piloto_da_sala.py --dsn "$SALA_DSN"
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
PIPELINE_VERSION = "2"

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


def medir_crop(item):
    u"""O GARGALO DA PRIMEIRA RODADA, agora contado em vez de narrado.

    Três estados, e são mesmo três:

        NOT_EXPECTED  a família não devia trazer cultura (edital, FAQ)
        PRESENT       o campo CROP chegou estruturado à Sala
        LOST          a cultura está no TEXTO, e não está em campo nenhum

    ⚠️ `LOST` é o achado, e não é o mesmo que ausência. Ausência seria a
    cultura não existir no documento. `LOST` é ela existir, ter sido colhida,
    ter sobrevivido até ao texto — e não ter campo onde pousar.

        O DADO CHEGOU. A ESTRUTURA NÃO.
    """
    if not item["source_id"].startswith(FAMILIAS_QUE_ESPERAM_CROP):
        return "NOT_EXPECTED", []
    # O contrato READY de 19 campos não tem CROP. Isto não é uma busca
    # esperançosa: é a confirmação de que o campo não existe para ninguém.
    if "crop" in item:
        return "PRESENT", [item["crop"]]
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
    usos = bruto.get("AUTHORIZED_USES") or list(bruto.values())[-1]

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


def cruzar(itens, substancias, usos, vivos):
    u"""O CRUZAMENTO, e o gate que o mata quando ele não se sustenta.

    Aparecer a mesma palavra em dois documentos NÃO é crossing (INT-LAW-037).
    O que promove um candidato aqui é responder a uma pergunta com chave:

        esta substância, que o boletim recomenda,
        tem rótulo ADAMA AUTORIZADO para ESTA cultura?

    ⚠️ E ELE FALHA FECHADO SEMPRE — O QUE NÃO É O MESMO QUE SABER DECIDIR.
    A 2ª rodada mediu isto e corrigiu uma afirmação da 1ª: `cruzar()` nunca lê
    cultura de lado nenhum. Ele declara `JOIN_KEYS_MISSING = [CROP, ...]`
    incondicionalmente, porque o contrato READY não tem o campo — e por isso
    devolve `NOT_POSSIBLE` mesmo quando a palavra «MELO» está escrita no texto.

        RECUSAR SEMPRE PELO MOTIVO CERTO  !=  SABER DISTINGUIR.

    Isto é o comportamento correto hoje (INT-LAW-037: sem join key não há
    crossing), e é honesto chamá-lo pelo nome: a decisão está **por construir**,
    e só faz sentido construí-la quando `CROP` chegar como campo. Ler a cultura
    do corpo do texto para fechar o join seria fabricar a chave — exatamente o
    ataque que este gate existe para barrar.
    """
    reg_para_nome = {p["num_registrazione"]: p["produto"] for p in vivos}
    achados = []
    for item in sorted(itens, key=lambda x: (x["source_id"], x["ordem"])):
        if not item["source_id"].startswith(FAMILIAS_AGRO):
            continue
        texto = normalizar(item["texto"])
        for substancia in sorted(substancias):
            if substancia not in texto:
                continue
            registos = sorted(substancias[substancia])
            # O GATE DURO: cultura na Sala × cultura no rótulo.
            # A Sala de hoje não traz CROP como campo. Enquanto não trouxer,
            # este crossing não pode passar de candidato.
            culturas_no_rotulo = sorted({
                u["CROP_ON_LABEL"] for u in usos
                if u["REGISTRATION_NUMBER"] in registos})
            achados.append({
                "CROSSING_ID": "XC-%s-%s-%s" % (
                    item["source_id"], item["ordem"], substancia[:12]),
                "QUESTION": ("a substância que o boletim recomenda tem rótulo "
                             "ADAMA autorizado para a cultura deste boletim?"),
                "SOURCE_ITEM": {
                    "SOURCE_ID": item["source_id"],
                    "RUN_ID": item["run_id"],
                    "ORDEM": item["ordem"],
                    "RAW_OBSERVATION_ID": item["raw_observation_id"],
                },
                "ACTIVE_INGREDIENT_OBSERVED": substancia,
                "ADAMA_REGISTRATIONS_WITH_THIS_AI": registos,
                "ADAMA_PRODUCTS": sorted(
                    {reg_para_nome.get(r, "?") for r in registos}),
                "ADAMA_CROPS_ON_LABEL": culturas_no_rotulo,
                "JOIN_KEYS_REQUIRED": ["ACTIVE_INGREDIENT", "CROP", "REGION",
                                       "FACT_TIME"],
                "JOIN_KEYS_PRESENT": ["ACTIVE_INGREDIENT"],
                "JOIN_KEYS_MISSING": ["CROP", "REGION", "FACT_TIME"],
                "CROSSING_STATE": "NOT_POSSIBLE",
                "WHY": ("a Sala não carrega CROP, FACT_LOCATION nem FACT_TIME "
                        "para este item; sem a cultura do lado do boletim a "
                        "pergunta não fecha. Casar por substância apenas seria "
                        "crossing por semelhança (INT-LAW-037)."),
                "STATUS": "EVIDENCE_LINKED_OBSERVATION",
            })
    return achados


def main():
    parser = argparse.ArgumentParser(description="O piloto da Sala de Espera")
    parser.add_argument("--dsn", required=True, help="DSN da Sala canônica")
    parser.add_argument("--desde", help="AAAA-MM-DD — filtro por tempo")
    parser.add_argument("--desde-artefato", dest="desde_artefato",
                        help="artefato da corrida anterior — CHECKPOINT por "
                             "identidade (RUN_ID, ORDEM). Vence --desde.")
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

    censo = []
    for item in itens:
        classe, porque, agro, admin = classificar(item)
        estado_crop, culturas = medir_crop(item)
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
            "CROP_OBSERVED_IN_TEXT": culturas,
        })

    crossings = cruzar(itens, substancias, usos, vivos)

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
            ("LOST_IN_DERIVATION", "ABSENT_IN_TEXT")),
        "CROP_LOST_IN_DERIVATION": sum(
            1 for c in censo if c["CROP_STATE"] == "LOST_IN_DERIVATION"),
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
        "CROSSINGS_POSSIVEIS": sum(
            1 for c in crossings if c["CROSSING_STATE"] != "NOT_POSSIBLE"),
        "OPPORTUNITY_CANDIDATES": 0,
        "PORQUE_ZERO_OPPORTUNITY": (
            "NO_DEFENSIBLE_ACTION_YET — nenhum crossing fechou join key. "
            "Produzir oportunidade aqui seria fabricar."),
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
    print("DELTA_REDUNDANTE_VS_SALA     = %d"
          % artefato["DELTA_REDUNDANTE_VS_SALA"])
    print("CROSSINGS_TENTADOS           = %d" % artefato["CROSSINGS_TENTADOS"])
    print("CROSSINGS_POSSIVEIS          = %d" % artefato["CROSSINGS_POSSIVEIS"])
    print("OPPORTUNITY_CANDIDATES       = %d"
          % artefato["OPPORTUNITY_CANDIDATES"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
