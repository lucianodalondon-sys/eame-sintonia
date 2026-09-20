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
"""
import argparse
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

    Sem CROP no item da Sala, a pergunta não fecha, e a resposta correta é
    `NOT_POSSIBLE` — não «provavelmente sim».
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
    parser.add_argument("--desde", help="AAAA-MM-DD — só o que pousou depois")
    parser.add_argument("--json", help="onde gravar o artefato")
    args = parser.parse_args()

    itens = ler_sala(args.dsn, args.desde)
    substancias, usos, vivos = ler_referencia_adama()

    censo = []
    for item in itens:
        classe, porque, agro, admin = classificar(item)
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
        })

    crossings = cruzar(itens, substancias, usos, vivos)

    # A contagem de independência. Texto idêntico NÃO é evidência nova
    # (INT-LAW-070..077): três source_id diferentes com o mesmo md5 são
    # UMA observação, não três.
    import hashlib
    por_impressao = {}
    for item in itens:
        chave = hashlib.md5(item["texto"].encode("utf-8")).hexdigest()
        por_impressao.setdefault(chave, []).append(item["source_id"])

    artefato = {
        "SCHEMA": "sintonia.intelligence.piloto-da-sala/1",
        "O_QUE_ISTO_E": (
            "medição read-only da Sala de Espera. NÃO é INTELLIGENCE_RUN "
            "canônico, NÃO produz FACT, FINDING nem OPPORTUNITY."),
        "TRAVA_DA_INTELIGENCIA": "COLLECTION_FOUNDATION_CLOSED = NAO",
        "ENTRADA_A": "public.sala_de_espera",
        "ENTRADA_B": "referencia/adama/ (lida e citada, nunca escrita)",
        "FILTRO_INCREMENTAL": args.desde or "TODOS",
        "SALA_TOTAL": len(itens),
        "SALA_USABLE_FOR_INTELLIGENCE": sum(
            1 for c in censo if c["CLASSE"] == "USABLE_FOR_INTELLIGENCE"),
        "SALA_WEAK": sum(1 for c in censo if c["CLASSE"] == "WEAK"),
        "SALA_INSUFFICIENT": sum(
            1 for c in censo if c["CLASSE"] == "INSUFFICIENT_FOR_INTELLIGENCE"),
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
    print("CROSSINGS_TENTADOS           = %d" % artefato["CROSSINGS_TENTADOS"])
    print("CROSSINGS_POSSIVEIS          = %d" % artefato["CROSSINGS_POSSIVEIS"])
    print("OPPORTUNITY_CANDIDATES       = %d"
          % artefato["OPPORTUNITY_CANDIDATES"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
