#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""CENSO DO CORPUS ROTULADO DA ADMISSION — ha chao para medir um classificador?

    python3 provas/censo_corpus_rotulado_admission.py

Sem rede, sem banco, sem recoleta, sem escrita. Nenhum classificador e treinado
aqui, e nenhum rotulo e gerado. Isto CONTA o que ja existe.

A PERGUNTA
----------
    O SINTONIA tem hoje corpus rotulado, confiavel e diverso o bastante para
    AVALIAR — e eventualmente TREINAR — um classificador semantico da Admission?

A REGRA QUE GOVERNA TODA ESTA CONTAGEM
--------------------------------------
    ROTULO EXISTE  !=  ROTULO E VERDADE CONFIAVEL

e o caso particular que decide a missao:

    DECISAO GERADA POR `PERGUNTAS_DO_UNIVERSO`  !=  GABARITO

Uma decisao produzida pela lista de palavras de hoje nao pode virar gabarito do
substituto dela. Se virasse, o mecanismo novo aprenderia as respostas do velho e
herdaria o mesmo defeito — com um numero bonito por cima.

    UM CLASSIFICADOR TREINADO NAS RESPOSTAS DO ANTERIOR
    NAO O SUBSTITUI: CONFIRMA-O.
"""
import json
import os
import re
import sys
from collections import Counter, defaultdict

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)
import _gavetas  # noqa: E402,F401
import admissao as adm  # noqa: E402


# ══════════════════════════════════════════════════════════════════════════
# OS CRITERIOS — ESCRITOS ANTES DE OLHAR PARA QUALQUER NUMERO
# ══════════════════════════════════════════════════════════════════════════
# Escrever o limiar depois de ver a contagem e desenhar o alvo a volta da
# flecha. Estes numeros nao foram escolhidos para dar PASS a nada: foram
# escolhidos pelo que cada uso EXIGE, e a razao de cada um esta ao lado.
#
# A licao que os fixou e a da missao de T2: uma regra ajustada em 10 positivos
# de 3 publicadores cobriu o treino 9/9 e acertou 0/10 no publicador que nao
# viu. Diversidade de publicador nao e um extra — e a unica coisa que separou
# «aprendeu o assunto» de «decorou o papel timbrado».
CRITERIOS = {
    "SANITY": {
        "POSITIVOS_MIN": 3,
        "NEGATIVOS_MIN": 3,
        "PUBLICADORES_MIN": 2,
        "PORQUE": "derrubar uma implementacao obviamente errada. Com menos de "
                  "3 de cada lado, uma coincidencia passa; com 1 publicador so, "
                  "nao se distingue o assunto do papel timbrado.",
    },
    "EVALUATION": {
        "POSITIVOS_MIN": 10,
        "NEGATIVOS_MIN": 10,
        "PUBLICADORES_MIN": 3,
        "EXIGE_HOLDOUT_DE_PUBLICADOR": True,
        "PORQUE": "comparar mecanismos sem ter servido para os ajustar. 3 "
                  "publicadores e o minimo em que tirar um ainda deixa 2 — com "
                  "2, tirar um deixa 1, e um publicador nao e uma distribuicao.",
    },
    "TRAINING": {
        "POSITIVOS_MIN": 100,
        "NEGATIVOS_MIN": 100,
        "PUBLICADORES_MIN": 5,
        "FAMILIAS_DE_DOCUMENTO_MIN": 2,
        "EXIGE_EVALUATION": True,
        "PORQUE": "ajustar sem memorizar. 100 por classe e modesto ate para um "
                  "modelo linear sobre saco-de-palavras; abaixo disso o modelo "
                  "decora documentos. 5 publicadores e o minimo em que reter um "
                  "ainda deixa 4 para aprender.",
    },
}

# As especies de autoridade. Nao se somam numa contagem unica de «rotulados»:
# a diferenca entre elas E a medicao.
HUMAN_VERIFIED = "HUMAN_VERIFIED"
DOCUMENT_SELF_DECLARED = "DOCUMENT_SELF_DECLARED"
SOURCE_CONTRACT_DECLARED = "SOURCE_CONTRACT_DECLARED"
RULE_DERIVED = "RULE_DERIVED"
KEYWORD_DERIVED = "KEYWORD_DERIVED"
MODEL_DERIVED = "MODEL_DERIVED"
DESCONHECIDA = "UNKNOWN"

# Quais especies podem servir de gabarito. `KEYWORD_DERIVED` esta de fora por
# definicao — e a saida do mecanismo que se quer substituir.
SERVEM_DE_GABARITO = (HUMAN_VERIFIED, DOCUMENT_SELF_DECLARED)

# O gabarito humano de T3. Ate existir, T3 estava em D por falta de qualquer
# rotulo independente com corpo.
GABARITO_T3 = "data/samples/T3-GROUND-TRUTH-EVAL-V1.json"


def _ler(caminho):
    with open(os.path.join(RAIZ, caminho), "rb") as f:
        return f.read().decode("utf-8", "replace")


def _json(caminho):
    return json.loads(_ler(caminho))


# ══════════════════════════════════════════════════════════════════════════
# 1 · AS ORIGENS DE ROTULO — todas, e nenhuma presumida confiavel
# ══════════════════════════════════════════════════════════════════════════
def origens_de_rotulo():
    """Tudo o que nesta arvore possa conter uma decisao tematica."""
    fora = []

    # ── O LIVRO DE DECISOES ────────────────────────────────────────────────
    livro = _json("data/samples/LIVRO-DE-DECISOES.json")["DECISOES"]
    fora.append({
        "PATH": "data/samples/LIVRO-DE-DECISOES.json",
        "FORMAT": "JSON · lista DECISOES",
        "ITEMS": len(livro),
        "WHO_ASSIGNED": "admissao.decidir() — `PERGUNTAS_DO_UNIVERSO`, "
                        "regra v%s" % adm.VERSAO_DA_REGRA,
        "WHEN": _intervalo(x.get("quando", "") for x in livro),
        "LABELS": sorted({x["universo"] for x in livro}),
        "MULTILABEL": "SIM · uma linha por par (item, universo)",
        "EVIDENCE": "SIM · campo `evidencia` com as palavras que casaram",
        "REPRODUCIBLE": "SIM · a regra esta no codigo e tem versao",
        "AUTORIDADE": KEYWORD_DERIVED,
        "_dados": livro,
    })

    # ── O GABARITO DE T2 ───────────────────────────────────────────────────
    gab = _gabarito_t2()
    fora.append({
        "PATH": "provas/a_regra_de_t2.py :: GABARITO",
        "FORMAT": "Python · lista de tuplos (caminho, EXPECTED, WHY)",
        "ITEMS": len(gab),
        "WHO_ASSIGNED": "pessoa, lendo a abertura de cada documento; cada "
                        "rotulo traz WHY escrito",
        "WHEN": "2026-09-11 (missao C-PROVA-REGRA-T2-V1)",
        "LABELS": ["T2:SIM", "T2:NAO", "T2:AMBIGUO"],
        "MULTILABEL": "NAO · so responde sobre T2",
        "EVIDENCE": "SIM · o caminho do corpo do documento",
        "REPRODUCIBLE": "SIM · `py provas/a_regra_de_t2.py`",
        "AUTORIDADE": DOCUMENT_SELF_DECLARED,
        "_dados": gab,
    })

    # ── AS FICHAS DAS FONTES ───────────────────────────────────────────────
    mestre = _json("system-map/data/sources.generated.json")["MASTER_ITALIANO"]
    fora.append({
        "PATH": "system-map/data/sources.generated.json :: MASTER_ITALIANO",
        "FORMAT": "JSON · uma ficha por fonte",
        "ITEMS": len(mestre),
        "WHO_ASSIGNED": "pessoa, ao abrir a ficha da FONTE — nao do documento",
        "WHEN": "antes desta cadeia de missoes",
        "LABELS": sorted({s.get("territory") for s in mestre if s.get("territory")}),
        "MULTILABEL": "NAO · um territorio por fonte",
        "EVIDENCE": "url e topics declarados; NAO o corpo de um documento",
        "REPRODUCIBLE": "SIM",
        "AUTORIDADE": SOURCE_CONTRACT_DECLARED,
        "_dados": mestre,
    })

    # ── OS MANIFESTOS DE AMOSTRA ───────────────────────────────────────────
    man = _manifestos()
    fora.append({
        "PATH": "data/samples/IT-SOURCE-SAMPLES/*/MANIFEST.json",
        "FORMAT": "JSON · SOURCE_ID + FILES[] com SHA256",
        "ITEMS": sum(len(m["FICHEIROS"]) for m in man),
        "WHO_ASSIGNED": "herdado do SOURCE_ID da pasta — a ficha da fonte, "
                        "outra vez",
        "WHEN": "2026-09-07 (captura das amostras)",
        "LABELS": sorted({m["TERRITORIO"] for m in man}),
        "MULTILABEL": "NAO",
        "EVIDENCE": "SIM · o ficheiro existe, com SHA256",
        "REPRODUCIBLE": "SIM",
        "AUTORIDADE": SOURCE_CONTRACT_DECLARED,
        "_dados": man,
    })

    # ── O REGISTO DE ARTEFATOS ─────────────────────────────────────────────
    reg = _json("data/derivados/REGISTO-DE-ARTEFATOS.json")["ARTEFATOS"]
    fora.append({
        "PATH": "data/derivados/REGISTO-DE-ARTEFATOS.json",
        "FORMAT": "JSON · uma ficha por artefato derivado",
        "ITEMS": len(reg),
        "WHO_ASSIGNED": "ninguem — NAO HA CAMPO DE UNIVERSO",
        "WHEN": "2026-09-08",
        "LABELS": [],
        "MULTILABEL": "n/a",
        "EVIDENCE": "SIM · corpo e linhagem",
        "REPRODUCIBLE": "SIM",
        "AUTORIDADE": DESCONHECIDA,
        "_dados": reg,
    })

    # ── O GABARITO DE T3 — o primeiro rotulo HUMANO desta arvore ───────────
    # Ate a missao de fecho, toda a origem acima era herdada da ficha da
    # fonte, derivada das palavras da Admission, ou nao tinha universo nenhum.
    # Nenhuma delas podia servir de gabarito do substituto das keywords.
    #
    #     UM CLASSIFICADOR TREINADO NAS RESPOSTAS DO ANTERIOR
    #     NAO O SUBSTITUI: CONFIRMA-O.
    #
    # Esta e a primeira que escapa disso: uma PESSOA leu o documento e
    # respondeu, em duas passagens, e onde as duas nao fecharam NAO ha rotulo.
    if os.path.isfile(os.path.join(RAIZ, GABARITO_T3)):
        gt3 = _json(GABARITO_T3)
        fora.append({
            "PATH": GABARITO_T3,
            "FORMAT": "JSON · GROUND_TRUTH[] + EXCLUDED_FROM_EVALUATION[]",
            "ITEMS": len(gt3["GROUND_TRUTH"]),
            "WHO_ASSIGNED": "uma PESSOA, em duas passagens (A e A2); a segunda "
                            "cega nos itens de releitura. NAO houve segundo "
                            "revisor independente.",
            "WHEN": gt3["GENERATED_AT"][:10],
            "LABELS": sorted({x["LABEL"] for x in gt3["GROUND_TRUTH"]}),
            "MULTILABEL": "NAO",
            "EVIDENCE": "SIM · corpo no disco, evidencia exibida e atestada",
            "REPRODUCIBLE": "SIM · " + gt3["GENERATOR"],
            "AUTORIDADE": HUMAN_VERIFIED,
            "_dados": gt3,
        })

    return fora


def _intervalo(datas):
    d = sorted(x for x in datas if x)
    return f"{d[0][:10]} .. {d[-1][:10]}" if d else "NAO SEI"


def _gabarito_t2():
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "_t2", os.path.join(RAIZ, "provas", "a_regra_de_t2.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m.GABARITO


def _manifestos():
    base = os.path.join(RAIZ, "data", "samples", "IT-SOURCE-SAMPLES")
    fora = []
    for nome in sorted(os.listdir(base)):
        p = os.path.join(base, nome, "MANIFEST.json")
        if not os.path.isfile(p):
            continue
        with open(p, encoding="utf-8") as f:
            d = json.load(f)
        m = re.match(r"IT-(T\d+)-\d+", nome)
        fora.append({
            "SOURCE_ID": nome,
            "TERRITORIO": m.group(1) if m else "?",
            "DONO": d.get("OWNER_ID", "NAO SEI"),
            "FICHEIROS": [f["RAW_FILE"] for f in d.get("FILES", [])],
        })
    return fora


# ══════════════════════════════════════════════════════════════════════════
# 2 · CONTAMINACAO — o rotulo foi feito com o sinal que queremos avaliar?
# ══════════════════════════════════════════════════════════════════════════
def contaminacao(livro):
    """Um rotulo produzido pela palavra que o classificador vai ver.

    Uma decisao `SIM` cuja evidencia e «casou a palavra fungo» nao serve para
    provar que um mecanismo baseado em «fungo» funciona. Prova que duas copias
    da mesma regra concordam — o que nao e informacao nenhuma.

        SELF_CONFIRMING_LABEL: o rotulo E a saida do sinal que se quer testar.
    """
    vazamento = [d for d in livro if (d.get("evidencia") or {}).get("palavras")]
    achado_noutro = [d for d in livro
                     if (d.get("evidencia") or {}).get("achado_noutro")]
    return vazamento, achado_noutro


# ══════════════════════════════════════════════════════════════════════════
# 3 · O CORPUS COM CORPO VERIFICAVEL
# ══════════════════════════════════════════════════════════════════════════
# Um rotulo sem corpo nao e elegivel nem para treino nem para avaliacao: nao se
# consegue voltar ao conteudo que o recebeu.
PUBLICADOR = {
    "IT-T1-001": "ISTAT", "IT-T2-001": "ARPAE", "IT-T2-002": "ARPAV",
    "IT-T2-004": "SIAS", "IT-T3-002": "REGIONE CAMPANIA",
    "IT-T3-005": "TERRE DELL'ETRURIA", "IT-T3-008": "ARIF PUGLIA",
    "IT-T3-010": "APOL LECCE", "IT-T3-011": "AGRIOS",
    "IT-T4-001": "MINISTERO DELLA SALUTE", "IT-T5-002": "ISMEA",
    "IT-T5-003": "GIORNATE FITOPATOLOGICHE", "IT-T7-002": "MASAF",
    "IT-T9-002": "CONCORRENTE", "IT-T9-008": "CONCORRENTE",
    "IT-T10-002": "AGEA",
}
# Publicadores que o gabarito de T2 alcanca sem passar por SOURCE_ID.
# `IT-BOLLETTINI-VPN-2026` NAO e um publicador: e uma pasta com boletins de
# QUATRO regioes diferentes. Conta-la como um so publicador escondia
# diversidade real do lado negativo — e, pior, ensinava a prova a tratar uma
# pasta como uma instituicao.
PUBLICADOR_POR_CAMINHO = [
    ("IT-ARPAV-VENETO", "ARPAV"), ("PIEMONTE-FD", "REGIONE PIEMONTE"),
    ("/CAMP_", "REGIONE CAMPANIA"), ("/LAZIO_", "REGIONE LAZIO"),
    ("/TN_DIB", "FONDAZIONE EDMUND MACH"), ("/MOLISE_", "REGIONE MOLISE"),
]


# ⚠️ ESTE DEFEITO ESTEVE NESTA PROVA, E ELA DEU VERDE COM ELE.
# A primeira versao procurava `IT-Txx-yyy` no CAMINHO. Os 43 textos derivados
# chamam-se `data/derivados/texto/RAW-<sha>.txt` e nao carregam fonte nenhuma no
# nome — portanto 43 dos 46 itens cairam num balde chamado «NAO SEI», e
# `PUBLISHER_HOLDOUT_POSSIBLE` respondeu YES porque «NAO SEI» contava como UM
# publicador.
#
#     UM BALDE DE DESCONHECIDOS CONTADO COMO CATEGORIA
#     E DIVERSIDADE FABRICADA.
#
# Agora o publicador vem da LINHAGEM: o registo de artefatos diz de que pai cada
# derivado nasceu, e o caminho do pai diz a fonte. Quem nao se resolve continua
# «NAO SEI» — e «NAO SEI» NAO conta como publicador em lado nenhum.
def _linhagem():
    fora = {}
    for a in _json("data/derivados/REGISTO-DE-ARTEFATOS.json")["ARTEFATOS"]:
        pais = a.get("NOTES", {}).get("PARENT_STORAGE_LOCATIONS", [])
        fora[a["STORAGE_LOCATION"]] = pais
    return fora


LINHAGEM = None


def publicador_de(caminho):
    global LINHAGEM
    if LINHAGEM is None:
        LINHAGEM = _linhagem()
    candidatos = [caminho] + list(LINHAGEM.get(caminho, []))
    for c in candidatos:
        m = re.search(r"(IT-T\d+-\d+)", c)
        if m:
            return PUBLICADOR.get(m.group(1), m.group(1))
    for c in candidatos:
        for marca, nome in PUBLICADOR_POR_CAMINHO:
            if marca in c:
                return nome
    return "NAO SEI"


def fonte_de(caminho):
    global LINHAGEM
    if LINHAGEM is None:
        LINHAGEM = _linhagem()
    for c in [caminho] + list(LINHAGEM.get(caminho, [])):
        m = re.search(r"(IT-T\d+-\d+)", c)
        if m:
            return m.group(1)
    return "NAO SEI"


def familia_de(caminho):
    ext = os.path.splitext(caminho)[1].lower()
    if "derivados/texto" in caminho:
        return "TEXTO-DERIVADO-DE-PDF"
    return {".pdf": "PDF", ".html": "HTML", ".csv": "CSV",
            ".ods": "PLANILHA", ".txt": "TEXTO"}.get(ext, "OUTRO")


def corpus_t3():
    """Os itens de T3 com rotulo HUMANO, corpo e razao estruturada.

    ⚠️ A UNIDADE DE CONTAGEM E O GRUPO, NAO O FICHEIRO. Quatro edicoes
    seguidas do mesmo boletim regional sao quatro ficheiros e uma observacao;
    conta-las como quatro enche o censo sem acrescentar evidencia.
    O agrupamento vem medido do proprio gabarito.
    """
    if not os.path.isfile(os.path.join(RAIZ, GABARITO_T3)):
        return [], []
    d = _json(GABARITO_T3)
    pares = [(x["A"], x["B"]) for x in d["NEAR_DUPLICATES"]["PARES"]]
    pai = {x["DOC_SHA256"]: x["DOC_SHA256"] for x in d["GROUND_TRUTH"]}

    def raiz(x):
        while pai[x] != x:
            x = pai[x]
        return x
    for a, b in pares:
        ra, rb = raiz(a), raiz(b)
        if ra != rb:
            pai[ra] = rb

    todos, visto = [], set()
    for x in sorted(d["GROUND_TRUTH"], key=lambda y: y["ITEM_ID"]):
        item = {
            "ITEM_ID": x["ITEM_ID"],
            "SOURCE_ID": x["SOURCE_ID"],
            "CONTENT_PATH": x["CONTENT_PATH"],
            "LABEL": "T3:%s" % ("SIM" if x["LABEL"] == "T3_SIM" else "NAO"),
            "LABEL_AUTHORITY": HUMAN_VERIFIED,
            "LABEL_REASON": x["HUMAN_REASON_CODE"],
            "PUBLICADOR": x["PUBLISHER"],
            "FAMILIA": familia_de(x["CONTENT_PATH"]),
            "GRUPO": raiz(x["DOC_SHA256"]),
        }
        todos.append(item)
        if item["GRUPO"] not in visto:
            visto.add(item["GRUPO"])
    independentes = []
    visto = set()
    for item in todos:
        if item["GRUPO"] not in visto:
            visto.add(item["GRUPO"])
            independentes.append(item)
    return todos, independentes


def corpus_com_corpo(gabarito):
    """O gabarito de T2 — rotulo E corpo E razao escrita."""
    fora = []
    for caminho, rotulo, porque in gabarito:
        fora.append({
            "ITEM_ID": caminho.split("/")[-1],
            "SOURCE_ID": fonte_de(caminho),
            "CONTENT_PATH": caminho,
            "LABEL": f"T2:{rotulo}",
            "LABEL_AUTHORITY": DOCUMENT_SELF_DECLARED,
            "LABEL_REASON": porque,
            "PUBLICADOR": publicador_de(caminho),
            "FAMILIA": familia_de(caminho),
        })
    return fora


# ══════════════════════════════════════════════════════════════════════════
# 4 · O PORTAO, POR UNIVERSO
# ══════════════════════════════════════════════════════════════════════════
def portao(universo, positivos, negativos, publicadores, familias):
    """A · avaliacao E treino · B · so avaliacao · C · so sanidade · D · nada."""
    c = CRITERIOS
    # «NAO SEI» e a ausencia de publicador, nao um publicador.
    publicadores = [p for p in publicadores if p != "NAO SEI"]
    sanity = (len(positivos) >= c["SANITY"]["POSITIVOS_MIN"]
              and len(negativos) >= c["SANITY"]["NEGATIVOS_MIN"]
              and len(publicadores) >= c["SANITY"]["PUBLICADORES_MIN"])
    # holdout: tirar QUALQUER publicador tem de deixar positivo e negativo
    holdout = len(publicadores) >= c["EVALUATION"]["PUBLICADORES_MIN"] and all(
        any(p["PUBLICADOR"] != fora for p in positivos)
        and any(n["PUBLICADOR"] != fora for n in negativos)
        for fora in publicadores)
    pub_pos = {p["PUBLICADOR"] for p in positivos} - {"NAO SEI"}
    evaluation = (sanity
                  and len(positivos) >= c["EVALUATION"]["POSITIVOS_MIN"]
                  and len(negativos) >= c["EVALUATION"]["NEGATIVOS_MIN"]
                  and len(pub_pos) >= c["EVALUATION"]["PUBLICADORES_MIN"]
                  and holdout)
    training = (evaluation
                and len(positivos) >= c["TRAINING"]["POSITIVOS_MIN"]
                and len(negativos) >= c["TRAINING"]["NEGATIVOS_MIN"]
                and len(pub_pos) >= c["TRAINING"]["PUBLICADORES_MIN"]
                and len(familias) >= c["TRAINING"]["FAMILIAS_DE_DOCUMENTO_MIN"])
    veredicto = ("A" if training else "B" if evaluation
                 else "C" if sanity else "D")
    return {"UNIVERSE": universo, "SANITY": sanity, "EVALUATION": evaluation,
            "TRAINING": training, "HOLDOUT_PUBLICADOR": holdout,
            "VEREDICTO": veredicto}


# ══════════════════════════════════════════════════════════════════════════
# 5 · O RELATORIO
# ══════════════════════════════════════════════════════════════════════════
def main():
    print("CENSO DO CORPUS ROTULADO DA ADMISSION")
    print("=" * 74)

    print("\n0 · OS CRITERIOS — escritos antes de qualquer contagem")
    print("-" * 74)
    for uso, c in CRITERIOS.items():
        req = " · ".join(f"{k}={v}" for k, v in c.items() if k != "PORQUE")
        print(f"  {uso}\n     {req}\n     {c['PORQUE']}")

    origens = origens_de_rotulo()
    livro = next(o for o in origens if "LIVRO" in o["PATH"])["_dados"]
    gab = next(o for o in origens if "a_regra_de_t2" in o["PATH"])["_dados"]

    print("\n1 · LABEL_SOURCES_FOUND")
    print("-" * 74)
    for o in origens:
        print(f"  PATH        {o['PATH']}")
        print(f"  FORMAT      {o['FORMAT']}")
        print(f"  ITEMS       {o['ITEMS']}")
        print(f"  WHO         {o['WHO_ASSIGNED']}")
        print(f"  WHEN        {o['WHEN']}")
        print(f"  LABELS      {o['LABELS']}")
        print(f"  MULTILABEL  {o['MULTILABEL']}")
        print(f"  EVIDENCE    {o['EVIDENCE']}")
        print(f"  REPRODUCE   {o['REPRODUCIBLE']}")
        print(f"  AUTORIDADE  {o['AUTORIDADE']}"
              f"{'   <- NAO SERVE DE GABARITO' if o['AUTORIDADE'] not in SERVEM_DE_GABARITO else ''}")
        print()
    print(f"  LABEL_SOURCES_FOUND = {len(origens)}")

    print("\n2 · O LIVRO DE DECISOES, MEDIDO")
    print("-" * 74)
    itens = {d["item"] for d in livro}
    print(f"  TOTAL_DECISIONS  {len(livro)}")
    print(f"  UNIQUE_ITEMS     {len(itens)}")
    print(f"  POR UNIVERSO     {dict(Counter(d['universo'] for d in livro))}")
    print(f"  POR RESULTADO    {dict(Counter(d['resultado'] for d in livro))}")
    vaz, noutro = contaminacao(livro)
    print(f"\n  DECISIONS_PRODUCED_BY_CURRENT_KEYWORDS = {len(livro)}  (TODAS)")
    print(f"  DECISIONS_WITH_INDEPENDENT_GROUND_TRUTH = 0")
    print(f"  LABEL_LEAKAGE (rotulo feito com a palavra a avaliar) = {len(vaz)}")
    print(f"  SELF_CONFIRMING_LABEL (idem, por exclusao) = {len(noutro)}")
    print("\n  Serve para: comparacao · diagnostico · hard-negative mining.")
    print("  NAO serve para: gabarito do substituto das keywords.")

    print("\n3 · MULTIRROTULO — decisoes multiplas nao sao multirrotulo")
    print("-" * 74)
    por_item = defaultdict(set)
    for d in livro:
        por_item[d["item"]].add(d["universo"])
    sim_por_item = defaultdict(set)
    for d in livro:
        if d["resultado"] == adm.SIM:
            sim_por_item[d["item"]].add(d["universo"])
    n1 = sum(1 for u in por_item.values() if len(u) == 1)
    n2 = sum(1 for u in por_item.values() if len(u) >= 2)
    conf = {i: u for i, u in sim_por_item.items() if len(u) >= 2}
    print(f"  ITEMS_WITH_1_UNIVERSE      {n1}")
    print(f"  ITEMS_WITH_2_PLUS_UNIVERSES {n2}")
    print(f"  MAX_UNIVERSES_PER_ITEM      "
          f"{max((len(u) for u in por_item.values()), default=0)}")
    print(f"\n  MULTIPLE_DECISIONS_ONLY   {n2}")
    print(f"  MULTILABEL_CONFIRMED      {len(conf)}   "
          f"(dois SIM no mesmo item)")
    print("  Ter tres decisoes registadas nao prova que as tres estao certas:")
    print("  no livro real elas sao NAO_SEI e NAO_SE_APLICA, que nao sao rotulos.")

    print("\n4 · O CORPUS COM CORPO VERIFICAVEL")
    print("-" * 74)
    corpo = corpus_com_corpo(gab)
    t3_todos, t3_ind = corpus_t3()
    pos = [c for c in corpo if c["LABEL"] == "T2:SIM"]
    neg = [c for c in corpo if c["LABEL"] == "T2:NAO"]
    amb = [c for c in corpo if c["LABEL"] == "T2:AMBIGUO"]
    faltam = [c for c in corpo
              if not os.path.isfile(os.path.join(RAIZ, c["CONTENT_PATH"]))]
    print(f"  itens com rotulo, corpo e razao escrita: {len(corpo)}")
    print(f"  sem corpo no disco (TRAINING/EVAL inelegiveis): {len(faltam)}")
    print(f"  CLEAR_POSITIVE {len(pos)} · CLEAR_NEGATIVE {len(neg)} · "
          f"AMBIGUOUS {len(amb)}")
    print(f"\n  publicadores: {dict(Counter(c['PUBLICADOR'] for c in corpo))}")
    print(f"  familias:     {dict(Counter(c['FAMILIA'] for c in corpo))}")
    print(f"  paises:       {{'IT': {len(corpo)}}}   linguas: {{'it': {len(corpo)}}}")

    print("\n5 · POR UNIVERSO")
    print("-" * 74)
    print(f"  {'UNIV':<6}{'POS':>5}{'NEG':>5}{'AMB':>5}{'PUBL':>6}"
          f"{'FAM':>5}  {'VEREDICTO':<10} porque")
    vereditos = {}
    for u in ("T2", "T3", "T4", "T7", "T9"):
        if u == "T2":
            p, n, a = pos, neg, amb
        elif u == "T3":
            # O portao conta as observacoes INDEPENDENTES, nao os ficheiros.
            p = [c for c in t3_ind if c["LABEL"] == "T3:SIM"]
            n = [c for c in t3_ind if c["LABEL"] == "T3:NAO"]
            a = []
        else:
            # Nenhuma outra origem produz positivo/negativo com corpo e razao.
            p, n, a = [], [], []
        publ = sorted({c["PUBLICADOR"] for c in p + n})
        fam = sorted({c["FAMILIA"] for c in p + n})
        g = portao(u, p, n, publ, fam)
        vereditos[u] = g
        porque = ("gabarito de T2" if u == "T2"
                  else "gabarito HUMANO de T3 (%d ficheiros -> %d grupos)"
                       % (len(t3_todos), len(t3_ind)) if u == "T3"
                  else "zero itens com rotulo independente E corpo")
        print(f"  {u:<6}{len(p):>5}{len(n):>5}{len(a):>5}{len(publ):>6}"
              f"{len(fam):>5}  {g['VEREDICTO']:<10} {porque}")
    outros = [u for u in ("T1", "T5", "T10", "T11", "T12", "T13")]
    print(f"\n  outros alvos canonicos de pedido/pedido.py: {', '.join(outros)}")
    print("  nenhum tem regra na Admission e nenhum tem gabarito. VEREDICTO = D")

    print("\n6 · DIVERSIDADE E HOLDOUT")
    print("-" * 74)
    t2 = vereditos["T2"]
    pub_pos = sorted({c["PUBLICADOR"] for c in pos} - {"NAO SEI"})
    print(f"  T2 · publicadores do lado positivo: {pub_pos}")
    print(f"  PUBLISHER_HOLDOUT_POSSIBLE = "
          f"{'YES' if t2['HOLDOUT_PUBLICADOR'] else 'NO'}")
    src_pos = sorted({c["SOURCE_ID"] for c in pos} - {"NAO SEI"})
    print(f"  SOURCE_HOLDOUT_POSSIBLE    = "
          f"{'YES' if len(src_pos) >= 3 else 'NO'}   fontes: {src_pos}")
    print(f"  COUNTRY_HOLDOUT_POSSIBLE   = NO   (todo o corpus e IT)")
    print(f"  LANGUAGE_HOLDOUT_POSSIBLE  = NO   (todo o corpus e it)")

    if t3_ind:
        gt3 = _json(GABARITO_T3)
        h3, ind3 = gt3["HOLDOUT"], gt3["INDEPENDENCIA"]
        t3p = [c for c in t3_ind if c["LABEL"] == "T3:SIM"]
        print(f"\n  T3 · publicadores do lado positivo: "
              f"{sorted({c['PUBLICADOR'] for c in t3p})}")
        print(f"  PUBLISHER_HOLDOUT_WITH_BOTH_CLASSES_POSSIBLE = "
              f"{ind3['PUBLISHER_HOLDOUT_APOS_FUNDIR']}")
        print(f"  SOURCE_HOLDOUT_WITH_BOTH_CLASSES_POSSIBLE    = "
              f"{ind3['SOURCE_HOLDOUT_APOS_FUNDIR']}")
        print(f"  COUNTRY_HOLDOUT_POSSIBLE                     = "
              f"{h3['COUNTRY_HOLDOUT_POSSIBLE']}")
        print(f"  LANGUAGE_HOLDOUT_POSSIBLE                    = "
              f"{h3['LANGUAGE_HOLDOUT_POSSIBLE']}")
        print(f"\n  T3 · DOCUMENTS {ind3['DOCUMENTS']} · "
              f"PUBLICATION_SERIES {len(gt3['DIVERSITY']['PUBLICATION_SERIES'])} · "
              f"PUBLISHERS {len(set(gt3['DIVERSITY']['POSITIVE_PUBLISHERS']) | set(gt3['DIVERSITY']['NEGATIVE_PUBLISHERS']))} · "
              f"SOURCES {len(set(gt3['DIVERSITY']['POSITIVE_SOURCE_IDS']) | set(gt3['DIVERSITY']['NEGATIVE_SOURCE_IDS']))}")
        print(f"  T3 · ficheiros {ind3['DOCUMENTS']} -> grupos independentes "
              f"{ind3['GRUPOS_INDEPENDENTES']}  "
              f"(positivos {ind3['POSITIVOS_DOCUMENTOS']} -> "
              f"{ind3['POSITIVOS_INDEPENDENTES']})")

    print("\n7 · O VEREDICTO")
    print("-" * 74)
    for u, g in vereditos.items():
        print(f"  {u}_SANITY={'YES' if g['SANITY'] else 'NO':<4}"
              f"{u}_EVALUATION={'YES' if g['EVALUATION'] else 'NO':<4}"
              f"{u}_TRAINING={'YES' if g['TRAINING'] else 'NO':<4}"
              f"-> {g['VEREDICTO']}")
    geral = ("B" if any(g["EVALUATION"] for g in vereditos.values())
             else "C" if any(g["SANITY"] for g in vereditos.values()) else "D")
    print(f"\n  OVERALL_VERDICT = {geral}   (o melhor universo manda; os outros"
          f" estao em D)")

    print("\n8 · A RESSALVA QUE O NUMERO NAO MOSTRA")
    print("-" * 74)
    print("  `T2 = B` significa «serve para AVALIAR», e com uma condicao:")
    print("  as candidatas `A3` e `A5` da missao anterior NASCERAM de olhar")
    print("  para este corpus. Um mecanismo derivado deste gabarito NAO e")
    print("  avaliado de forma independente por ele.")
    print()
    print("      UM CONJUNTO SO E INDEPENDENTE DE QUEM NAO OLHOU PARA ELE.")
    print()
    print("  Para essas candidatas o gabarito e treino, nao teste. Para um")
    print("  mecanismo que ninguem ajustou aqui, continua a servir de teste.")

    if t3_ind:
        gt3 = _json(GABARITO_T3)
        ind3, idi3 = gt3["INDEPENDENCIA"], gt3["IDIOMA_MEDIDO"]
        print()
        print("  `T3 = B` tem tres ressalvas, e nenhuma delas aparece no 11.")
        print()
        print(f"  1 · A MARGEM E DE UM. O criterio pede 10 positivos e ha "
              f"{ind3['POSITIVOS_INDEPENDENTES']}.")
        print("      Um item que se descubra mal rotulado derruba o veredicto.")
        print()
        print(f"  2 · OS 14 POSITIVOS SAO {ind3['POSITIVOS_INDEPENDENTES']} "
              f"OBSERVACOES. Quatro deles sao edicoes")
        print("      seguidas do mesmo boletim regional, e partilham a abertura")
        print("      quase inteira.")
        print()
        print("          QUATRO COPIAS DO MESMO BOLETIM NAO SAO QUATRO PROVAS.")
        print()
        print(f"  3 · O IDIOMA NAO FOI MEDIDO EM TODOS. "
              f"{idi3['NAO_RESOLVIDO']} dos {ind3['DOCUMENTS']} nao")
        print(f"      resolvem LANGUAGE, e {len(idi3['NAO_ITALIANO'])} esta em "
              f"ingles. O pais e IT em todos,")
        print("      e e isso — e so isso — que EVALUATION_SCOPE afirma.")
        print()
        print(f"      EVALUATION_SCOPE = {gt3['EVALUATION_SCOPE']}")
        print("      Nao autoriza afirmar Franca, Espanha nem EAME.")

    print("\n9 · A LACUNA, MEDIDA — de onde poderia vir, sem coletar nada agora")
    print("-" * 74)
    alcancavel = material_que_se_declara(gab)
    for universo, docs in sorted(alcancavel.items()):
        publ = sorted({publicador_de(d) for d in docs} - {"NAO SEI"})
        print(f"  {universo:<5} {len(docs):>3} documentos JA NESTA ARVORE abrem "
              f"declarando-se · {len(publ)} publicadores")
    c = CRITERIOS["EVALUATION"]
    print(f"\n  Para levar UM universo de D a B faltam, por universo:")
    print(f"    NEEDED_POSITIVES   {c['POSITIVOS_MIN']}  (com corpo e razao escrita)")
    print(f"    NEEDED_NEGATIVES   {c['NEGATIVOS_MIN']}")
    print(f"    NEEDED_PUBLISHERS  {c['PUBLICADORES_MIN']}  no lado positivo")
    print(f"    NEEDED_AMBIGUOUS   0  — ambiguo nao e requisito, e resultado")
    t = CRITERIOS["TRAINING"]
    print(f"\n  Para levar T2 de B a A faltam:")
    print(f"    positivos {t['POSITIVOS_MIN'] - len(pos)}  ·  "
          f"negativos {max(0, t['NEGATIVOS_MIN'] - len(neg))}  ·  "
          f"publicadores positivos {t['PUBLICADORES_MIN'] - len(pub_pos)}")
    print(f"    NEEDED_LANGUAGES  >=1 alem de `it` — hoje o corpus e 100% italiano")
    print("\n  ISTO NAO E UM PEDIDO DE COLETA. E a conta que a proxima missao")
    print("  precisa para decidir entre rotular o que ha, coletar, ou pedir")
    print("  revisao humana.")
    return 0


# Quantos documentos DESTA ARVORE abrem declarando o seu genero. NAO e um
# rotulo: e a medida de quanto material e ROTULAVEL sem coletar nada. Quem
# rotula continua a ser uma pessoa, a ler.
SE_DECLARAM = {
    "T2": ("bollettino agrometeorologico", "agrometeo… informa", "meteo veneto",
           "bollettino agrometeorologico settimanale"),
    "T3": ("bollettino fitosanitario", "servizio fitosanitario",
           "u.o. fitosanitario", "difesa integrata", "difesa delle colture",
           "monitoraggio"),
    "T4": ("dataset fitosanitari", "prodotti fitosanitari autorizzati"),
}


def material_que_se_declara(gabarito):
    fora = defaultdict(list)
    for caminho, _rotulo, _why in gabarito:
        abertura = _ler(caminho)[:600].lower()
        for universo, marcas in SE_DECLARAM.items():
            if any(m in abertura for m in marcas):
                fora[universo].append(caminho)
    return fora


if __name__ == "__main__":
    raise SystemExit(main())
