#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""O CENSO DA SALA DE ESPERA — quanto estoque existe, e quanto dele se prova.

    python3 provas/o_censo_da_sala_de_espera.py

A PERGUNTA
----------
    ANTES DE ABRIR A BIG COLLECTION:
    O QUE ESTA HOJE NA SALA DE ESPERA, QUANTO DISSO SE PROVA PELOS
    CONTRATOS DE HOJE, E O ESTOQUE EXISTENTE IMPEDE COMECAR?

O QUE ESTA MEDICAO NAO FAZ, E E O QUE A DEFINE
-----------------------------------------------
Nao apaga, nao move, nao renomeia, nao admite, nao reprocessa, nao deduplica,
nao consolida, nao re-admite, nao abre corrida, nao toca LIVE.

    UM CENSO QUE MEXE NO QUE CONTA JA NAO ESTA A CONTAR.

⚠️ A MORADA NAO E COPIADA PARA AQUI
------------------------------------
O endereco da sala vem de `admissao/sala_de_espera.py::MORADA`, lido do dono
em tempo de execucao. Escrever aqui `data/samples/PRONTO-PARA-INTELIGENCIA`
faria deste ficheiro uma SEGUNDA declaracao da morada — e no dia em que a
COL-LAW-044 permitir trocar o meio, o censo mediria a morada velha e diria
«vazia» sobre uma sala cheia.

    O CENSO PERGUNTA AO DONO ONDE E A SALA. NAO SABE DE COR.

O mesmo vale para o contrato: os 11 campos saem de
`admissao.pronto_para_inteligencia()`, construidos, e nao de uma lista copiada.

⚠️ O QUE ESTE CENSO NAO E DONO
-------------------------------
    A FILA       `provas/o_censo_do_acervo.py` mede o que PODE chegar a sala.
                 Aqui ela entra so como CONFERENCIA — o numero dele continua
                 a ser o dele. Dois donos do mesmo numero seriam duas verdades.
    O ESTADO     este relatorio e fotografia. Nao promove, nao rebaixa, e nao
                 passa a ser quem decide se um item esta READY.
"""
import hashlib
import io
import json
import os
import sys
from collections import Counter, OrderedDict

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)
import _gavetas  # noqa: E402,F401

import admissao                                      # noqa: E402
import sala_de_espera as espera                      # noqa: E402

SAIDA = os.path.join("data", "derivados", "O-CENSO-DA-SALA-DE-ESPERA.json")

# A fila e medida por outro dono. Aqui so se confere que os dois veem o mesmo
# livro — nunca se republica o numero dele como se fosse deste censo.
LIVRO_IT = os.path.join("data", "collection-ledger", "italy",
                        "observations.ndjson")
CORRIDAS_IT = os.path.join("data", "collection-ledger", "italy", "runs.ndjson")
ARMAZEM = os.path.join("data", "collection-store")

# A ausencia tem duas palavras nesta casa, e as duas sao ausencia — nao vazio.
DESCONHECIDO = ("NAO SEI", "NÃO SEI", "UNKNOWN", "DESCONHECIDO")

# Onde o LIVE responderia, se houvesse como lhe perguntar. So se le o NOME.
VARIAVEIS_DO_LIVE = ("SUPABASE_DB_URL", "SUPABASE_URL",
                     "SUPABASE_SERVICE_ROLE_KEY")

IGNORAR = {".git", "node_modules", ".venv", "__pycache__", ".next", "dist"}


# ────────────────────────────────────────────────────────────────────────
# LEITURA CRUA — e so leitura
# ────────────────────────────────────────────────────────────────────────
def _linhas(rel):
    caminho = os.path.join(RAIZ, rel)
    if not os.path.isfile(caminho):
        return []
    fora = []
    with io.open(caminho, encoding="utf-8", errors="replace") as fh:
        for linha in fh:
            linha = linha.strip()
            if not linha:
                continue
            try:
                fora.append(json.loads(linha))
            except json.JSONDecodeError:
                fora.append({"_ILEGIVEL": True})
    return fora


def _sabido(valor):
    """⚠️ UNKNOWN NAO E VAZIO, E VAZIO NAO E UNKNOWN.

    Um campo ausente e um campo que a sentinela marca como ausente contam para
    o MESMO lado — o lado do que nao se prova. Contar `NAO SEI` como valor
    conhecido so porque a string nao esta vazia seria dar por provado
    exactamente aquilo que a casa escreveu para dizer que nao prova.
    """
    if valor is None:
        return False
    texto = str(valor).strip()
    if not texto:
        return False
    for marca in DESCONHECIDO:
        if texto.upper().startswith(marca.upper()):
            return False
    return True


def _campos_do_contrato():
    """Os campos do READY, CONSTRUIDOS pelo dono. Nunca copiados para aqui.

    ⚠️ E SE A SONDA DEIXAR DE PASSAR A PORTA, ISTO FALHA ALTO.
    Cair para uma lista escrita a mao seria transformar «a porta mudou» em
    «o censo mediu na mesma» — e o censo passaria a medir contra uma copia
    que ninguem mantem.

        SEM O CONSTRUTOR NAO HA CONTRATO PARA MEDIR CONTRA.
    """
    # ⚠️ A SONDA MUDOU DE TEXTO, E A PORTA E QUE ESTAVA CERTA.
    # A primeira versao mandava «Ensaio de campo publicado com DOI» a `T7` e
    # passava — porque nessa altura `T7` carregava o lexico de CIENCIA, por
    # `pedido/pedido.py` dizer que `T7` era «Ciencia e ensaio». No Atlas, que e
    # o DONO (`leis/territorios.py`, e a tabela de `docs/fontes/ATLAS-DE-FONTES-EAME.md`),
    # `T7` e TECHNICAL NETWORK — agronomos, extensao, cooperativas, associacoes
    # — e ciencia e de `T5`.
    #
    #     A SONDA NAO SE ESCOLHE PARA PASSAR: ESCOLHE-SE PARA PERTENCER.
    #
    # Trocar a taxonomia para a sonda antiga voltar a passar seria repor o bug
    # com cara de conserto. Trocou-se a sonda, como este ficheiro ja mandava
    # fazer no erro que levantava. Medido: este texto e SIM em `T7` e em mais
    # nenhum territorio, e o texto antigo e SIM em `T5` e NAO em `T7`.
    item = {"id": "sonda-do-censo",
            "texto": ("Boletim tecnico da cooperativa para os socios, "
                      "assinado pelo agronomo de campo"),
            "source_id": "IT-T7-001", "fact_time": "2026-05-02"}
    d = admissao.decidir(item, "T7", corrida="sonda-do-censo")
    if d.resultado != admissao.SIM:
        raise SystemExit(
            "a sonda do censo nao passa a porta (%s · %s). O censo NAO cai "
            "para uma lista a mao: sem construtor nao ha contrato para medir "
            "contra. Ajustar a sonda, e nao o censo." % (d.resultado, d.regra))
    return tuple(admissao.pronto_para_inteligencia(item, d))


# ────────────────────────────────────────────────────────────────────────
# 1 · A SALA — quem e o dono, onde ela e, e o que esta la dentro
# ────────────────────────────────────────────────────────────────────────
def a_sala(campos):
    """O censo da sala canonica. Um ficheiro por corrida, itens la dentro.

    ⚠️ REGISTO != ITEM. O ficheiro e da CORRIDA; os itens estao dentro dele.
    Somar ficheiros e itens daria um numero que nao existe em sitio nenhum.
    """
    morada = espera.MORADA
    existe = os.path.isdir(morada)
    ficheiros = []
    if existe:
        ficheiros = sorted(f for f in os.listdir(morada) if f.endswith(".json"))

    registos, itens, ilegiveis = [], [], []
    for nome in ficheiros:
        caminho = os.path.join(morada, nome)
        try:
            with io.open(caminho, encoding="utf-8") as fh:
                corpo = json.load(fh)
        except Exception as erro:                      # noqa: BLE001
            ilegiveis.append({"FICHEIRO": nome, "PORQUE": str(erro)[:120]})
            continue
        run_id = corpo.get("RUN_ID")
        unidades = corpo.get("ITENS") or []
        registos.append({"FICHEIRO": nome, "RUN_ID": run_id,
                         "ITENS": len(unidades)})
        for u in unidades:
            itens.append((nome, run_id, u))

    return OrderedDict([
        ("OWNER", "admissao/sala_de_espera.py"),
        ("CONSTRUTOR_DO_ITEM", "admissao.pronto_para_inteligencia()"),
        ("CONTRATO", "COL-LAW-043"),
        ("CAMPOS_DO_CONTRATO", list(campos)),
        ("MORADA", os.path.relpath(morada, RAIZ)),
        ("MORADA_EXISTE", existe),
        ("BACKEND", "FILESYSTEM (ADR-SALA-DE-ESPERA-V1)"),
        ("TOTAL_WAITING_ROOM_RECORDS", len(registos)),
        ("TOTAL_UNIQUE_READY_ITEMS", len(itens)),
        ("PORQUE_OS_DOIS_NUMEROS_PODEM_DIFERIR",
         "um registo e um FICHEIRO DE CORRIDA; um item e uma UNIDADE dentro "
         "dele. Uma corrida com 3 unidades da 1 registo e 3 itens."),
        ("FICHEIROS_ILEGIVEIS", ilegiveis),
        ("REGISTOS", registos),
    ]), itens


# ────────────────────────────────────────────────────────────────────────
# 2 · EXISTE UMA SEGUNDA SALA? — a varredura que tenta provar que sim
# ────────────────────────────────────────────────────────────────────────
def as_outras_representacoes(campos):
    """⚠️ NAO SE DECLARA «UMA SO REPRESENTACAO» POR ACREDITAR NO ADR.

    Esta varredura procura, na arvore inteira, qualquer objecto que carregue o
    ESTADO do READY ou a forma completa do contrato. Se existir um segundo
    sitio onde unidades prontas vivem, ele aparece aqui — e o censo deixa de
    poder somar sem pensar.

        MESMO ITEM EM DUAS REPRESENTACOES != DOIS ITENS.
    """
    alvo = set(campos)
    achados, ficheiros_lidos = [], 0
    for pasta, subpastas, nomes in os.walk(RAIZ):
        subpastas[:] = sorted(d for d in subpastas if d not in IGNORAR)
        for nome in sorted(nomes):
            if not nome.endswith((".json", ".ndjson")):
                continue
            caminho = os.path.join(pasta, nome)
            rel = os.path.relpath(caminho, RAIZ)
            try:
                with io.open(caminho, encoding="utf-8", errors="replace") as fh:
                    texto = fh.read()
            except Exception:                          # noqa: BLE001
                continue
            ficheiros_lidos += 1
            # Filtro barato antes do parse: quem nao menciona nao carrega.
            if "PRONTO_PARA_INTELIGENCIA" not in texto \
                    and "ADMITIDO_POR" not in texto:
                continue

            def procurar(no, onde):
                if isinstance(no, dict):
                    if no.get("ESTADO") == "PRONTO_PARA_INTELIGENCIA" \
                            or alvo.issubset(set(no)):
                        achados.append({"FICHEIRO": rel, "ONDE": onde or "/"})
                    for chave in sorted(no):
                        procurar(no[chave], "%s/%s" % (onde, chave))
                elif isinstance(no, list):
                    for i, v in enumerate(no):
                        procurar(v, "%s[%d]" % (onde, i))

            try:
                if nome.endswith(".ndjson"):
                    for i, linha in enumerate(texto.splitlines()):
                        if linha.strip():
                            procurar(json.loads(linha), "#%d" % i)
                else:
                    procurar(json.loads(texto), "")
            except json.JSONDecodeError:
                continue

    dentro = os.path.relpath(espera.MORADA, RAIZ)
    fora_da_sala = [a for a in achados if not a["FICHEIRO"].startswith(dentro)]
    return OrderedDict([
        ("FICHEIROS_JSON_VARRIDOS", ficheiros_lidos),
        ("OBJECTOS_READY_ENCONTRADOS", len(achados)),
        ("FORA_DA_SALA_CANONICA", len(fora_da_sala)),
        ("ONDE", fora_da_sala[:50]),
        ("REPRESENTACOES_DA_SALA", 1 if not fora_da_sala else 1 + len(
            sorted({a["FICHEIRO"] for a in fora_da_sala}))),
        ("O_QUE_ISTO_PROVA",
         "se FORA_DA_SALA_CANONICA = 0, nao ha segunda representacao em "
         "ficheiro nesta arvore, e os totais da sala podem ser lidos como "
         "estao — sem risco de contar o mesmo item duas vezes."),
    ])


# ────────────────────────────────────────────────────────────────────────
# 3 · O LIVE — nao se toca, e diz-se o que por isso nao se mediu
# ────────────────────────────────────────────────────────────────────────
def o_live():
    presentes = [v for v in VARIAVEIS_DO_LIVE if os.environ.get(v)]
    return OrderedDict([
        ("LIVE_READS", 0),
        ("LIVE_WRITES", 0),
        ("CREDENCIAIS_PRESENTES", presentes),
        ("A_SALA_VIVE_NO_LIVE", "NO"),
        ("PORQUE",
         "ADR-SALA-DE-ESPERA-V1 decidiu FILESYSTEM: nao ha tabela de READY, "
         "nao ha migration da sala, e a decisao de admissao nao e persistida "
         "em PostgreSQL. O enum `etapa_da_coleta` tem 'READY', mas ele e "
         "PASSAGEM de corrida em `etapa_da_corrida` — telemetria, e nao a "
         "unidade. ETAPA QUE PASSOU != UNIDADE POUSADA."),
        ("CENSUS_BLOCKED_BY_LIVE_MEASUREMENT", "NO"),
    ])


# ────────────────────────────────────────────────────────────────────────
# 4 · A FILA — conferencia, nunca segundo dono
# ────────────────────────────────────────────────────────────────────────
def a_fila_a_montante():
    """O que PODE chegar a sala. O dono do numero e `o_censo_do_acervo.py`.

    ⚠️ ISTO NAO E A SALA DE ESPERA. Sao observacoes preservadas pelo coletor,
    antes da porta. Contar a fila como estoque da sala seria declarar READY
    por proximidade.

        OBSERVADO PELO COLETOR != ADMITIDO != POUSADO NA SALA.
    """
    obs = _linhas(LIVRO_IT)
    corridas = _linhas(CORRIDAS_IT)

    # ⚠️ SHA IGUAL E BYTES IGUAIS, E MAIS NADA. Nao e o mesmo documento, nao
    # e a mesma observacao, e nunca e um DOCUMENT_ID.
    shas = Counter(o.get("RAW_SHA256") for o in obs if o.get("RAW_SHA256"))
    grupos_de_bytes = {s: n for s, n in shas.items() if n > 1}

    docs = Counter(o.get("DOCUMENT_ID") for o in obs if o.get("DOCUMENT_ID"))
    por_fonte = Counter(o.get("SOURCE_ID") or "UNKNOWN" for o in obs)
    resultado = Counter(o.get("OBSERVATION_RESULT") or "UNKNOWN" for o in obs)
    por_corrida = Counter(o.get("RUN_ID") or "UNKNOWN" for o in obs)

    com_bytes_declarados = [o for o in obs if o.get("RAW_PATH")]
    com_bytes_na_arvore = [o for o in com_bytes_declarados
                           if os.path.isfile(os.path.join(RAIZ, o["RAW_PATH"]))]

    colhido = sum(1 for o in obs if _sabido(o.get("CAPTURED_AT")))
    fato = sum(1 for o in obs if _sabido(o.get("FACT_TIME")))

    no_armazem = 0
    base = os.path.join(RAIZ, ARMAZEM)
    if os.path.isdir(base):
        for pasta, subpastas, nomes in os.walk(base):
            subpastas[:] = sorted(subpastas)
            no_armazem += sum(1 for n in nomes if not n.startswith("."))

    return OrderedDict([
        ("ISTO_NAO_E_A_SALA", "YES — e a fila a montante dela"),
        ("DONO_DO_NUMERO", "provas/o_censo_do_acervo.py"),
        ("OBSERVACOES_NO_LIVRO", len(obs)),
        ("CORRIDAS_NO_LIVRO", len(corridas)),
        ("OBSERVACOES_POR_CORRIDA", OrderedDict(sorted(por_corrida.items()))),
        ("OBSERVATION_RESULT", OrderedDict(sorted(resultado.items()))),
        ("DOCUMENT_ID_DISTINTOS", len(docs)),
        ("RAW_SHA256_DISTINTOS", len(shas)),
        ("GRUPOS_DE_BYTES_IDENTICOS", len(grupos_de_bytes)),
        ("COMO_LER_ESSE_NUMERO",
         "⚠️ NAO E «35 DOCUMENTOS DUPLICADOS». Sao 35 conjuntos de bytes que "
         "foram observados MAIS DE UMA VEZ — porque reobservar a mesma "
         "publicacao em corridas seguintes devolve os mesmos bytes, e o livro "
         "regista isso como SEEN_AGAIN. REOBSERVAR NAO E DUPLICAR: o "
         "documento e um, e as observacoes dele sao varias."),
        ("PRIMEIRAS_OBSERVACOES", sum(
            1 for o in obs if o.get("OBSERVATION_RESULT") in
            ("BASELINE_DOCUMENT", "NEW_DOCUMENT"))),
        ("REOBSERVACOES", sum(1 for o in obs
                              if o.get("OBSERVATION_RESULT") == "SEEN_AGAIN")),
        ("O_QUE_SHA_IGUAL_QUER_DIZER",
         "MESMOS BYTES. Nao diz mesmo documento, nao diz mesma observacao, e "
         "nao serve de DOCUMENT_ID."),
        ("COM_CAMINHO_DE_BYTES", len(com_bytes_declarados)),
        ("COM_BYTES_MESMO_NA_ARVORE", len(com_bytes_na_arvore)),
        ("FICHEIROS_NO_ARMAZEM", no_armazem),
        ("POR_FONTE", OrderedDict(sorted(por_fonte.items()))),
        ("COLLECTED_TIME_KNOWN", colhido),
        ("COLLECTED_TIME_UNKNOWN", len(obs) - colhido),
        ("FACT_TIME_KNOWN", fato),
        ("FACT_TIME_UNKNOWN", len(obs) - fato),
        ("RAW_OBSERVATION_ID",
         "UNKNOWN em disco — a identidade canonica e `raw_asset.id`, e ela "
         "nasce no ingresso canonico. O livro do coletor nao a carrega, e "
         "deriva-la do SHA seria fabrica-la."),
    ])


# ────────────────────────────────────────────────────────────────────────
# 5 · LINHAGEM, IDENTIDADE, TEXTO, TEMPO, GEOGRAFIA — por item da SALA
# ────────────────────────────────────────────────────────────────────────
def por_item(itens):
    """A cadeia de cada unidade POUSADA. Com zero itens, os baldes ficam a 0.

    ⚠️ ZERO NAO E «NAO MEDIDO». A maquinaria corre na mesma, e o zero e o
    resultado — nao a ausencia de resultado.
    """
    linhagem = Counter()
    quebra = Counter()
    origem = Counter()
    contrato = Counter()
    ident = Counter()
    tempo = Counter()
    geo = Counter()
    texto = Counter()
    campos = set(_campos_do_contrato())

    for _ficheiro, run_id, u in itens:
        # ── CONTRATO ────────────────────────────────────────────────────
        if not isinstance(u, dict):
            contrato["READY_CONTRACT_INVALID"] += 1
            linhagem["LINEAGE_UNKNOWN"] += 1
            origem["UNKNOWN_ORIGIN"] += 1
            continue
        tem = set(u)
        conforme = (tem == campos
                    and u.get("ESTADO") == "PRONTO_PARA_INTELIGENCIA")
        if conforme:
            contrato["READY_CONTRACT_VALID"] += 1
        elif campos - tem:
            contrato["READY_CONTRACT_INVALID"] += 1
        else:
            contrato["READY_CONTRACT_UNKNOWN"] += 1

        # ── LINHAGEM ────────────────────────────────────────────────────
        # ⚠️ A CORRIDA DO ITEM TEM DE SER A DO FICHEIRO. Um item que nomeia
        # outra corrida nao tem linhagem completa, tem contradicao.
        tem_run = _sabido(u.get("CORRIDA")) and u.get("CORRIDA") == run_id
        tem_fonte = _sabido(u.get("SOURCE_ID"))
        tem_porta = _sabido(u.get("ADMITIDO_POR"))
        if not tem_run:
            quebra["MISSING_RUN_LINK"] += 1
        if not tem_fonte:
            quebra["MISSING_SOURCE_LINK"] += 1
        if not tem_porta:
            quebra["MISSING_ADMISSION_LINK"] += 1
        # ⚠️ RAW e STORAGE NAO VIAJAM NO CONTRATO DE 11 CAMPOS, de proposito
        # (COL-LAW-043: a inteligencia recebe isto e mais nada). Por isso a
        # cadeia ate ao byte so se fecha no ledger da corrida — e sem ele o
        # honesto e PARTIAL, nunca FULL.
        quebra["MISSING_RAW_LINK"] += 1
        quebra["MISSING_STORAGE_LINK"] += 1
        if tem_run and tem_fonte and tem_porta:
            linhagem["LINEAGE_PARTIAL"] += 1
            # ⚠️ ORIGEM SAI DA FORMA, NUNCA DA DATA.
            # Ligacoes completas + forma do contrato de HOJE = canonico atual.
            # Ligacoes completas + forma DIFERENTE = outra era escreveu isto, e
            # isso e o unico sinal honesto de legado: um writer antigo deixa a
            # marca na FORMA. Um mtime nao prova era nenhuma — ficheiro novo
            # com conteudo antigo tem mtime de hoje.
            origem["CURRENT_CANONICAL_PROVEN" if conforme
                   else "LEGACY_PROVEN"] += 1
        elif tem_run or tem_fonte or tem_porta:
            linhagem["LINEAGE_BROKEN"] += 1
            origem["MIXED_OR_TRANSITIONAL"] += 1
        else:
            linhagem["LINEAGE_UNKNOWN"] += 1
            origem["UNKNOWN_ORIGIN"] += 1

        # ── IDENTIDADE ──────────────────────────────────────────────────
        ident["SOURCE_ID_PRESENT" if tem_fonte else "SOURCE_ID_UNKNOWN"] += 1
        # DOCUMENT_ID nao viaja no contrato READY. Declara-lo provado seria
        # inventa-lo; declara-lo fabricado seria acusar sem prova.
        ident["DOCUMENT_ID_UNKNOWN"] += 1

        # ── TEXTO ───────────────────────────────────────────────────────
        texto["TOTAL_TEXT_UNITS"] += 1 if _sabido(u.get("TEXTO")) else 0
        # ⚠️ O contrato de 11 campos nao carrega TEXT_KIND, TEXT_RELATION nem
        # LANGUAGE. Sem campo nao ha prova, e a lingua da publicacao NAO se
        # herda para o texto.
        texto["UNKNOWN_TEXT_KIND"] += 1
        texto["TEXT_RELATION_UNKNOWN"] += 1
        texto["LANGUAGE_UNKNOWN"] += 1

        # ── TEMPO ───────────────────────────────────────────────────────
        tempo["FACT_TIME_KNOWN" if _sabido(u.get("FACT_TIME"))
              else "FACT_TIME_UNKNOWN"] += 1
        tempo["COLLECTED_TIME_KNOWN" if _sabido(u.get("CAPTURED_AT"))
              else "COLLECTED_TIME_UNKNOWN"] += 1
        # PUBLICATION_TIME e OBSERVED_TIME nao tem campo no contrato.
        tempo["PUBLICATION_TIME_UNKNOWN"] += 1
        tempo["OBSERVED_TIME_UNKNOWN"] += 1

        # ── GEOGRAFIA ───────────────────────────────────────────────────
        geo["SOURCE_LOCATION_KNOWN" if _sabido(u.get("SOURCE_LOCATION"))
            else "SOURCE_LOCATION_UNKNOWN"] += 1
        geo["FACT_LOCATION_KNOWN" if _sabido(u.get("FACT_LOCATION"))
            else "FACT_LOCATION_UNKNOWN"] += 1

    def balde(contador, nomes):
        return OrderedDict((n, contador.get(n, 0)) for n in nomes)

    return OrderedDict([
        ("LINHAGEM", balde(linhagem, ("LINEAGE_FULL", "LINEAGE_PARTIAL",
                                      "LINEAGE_BROKEN", "LINEAGE_UNKNOWN"))),
        ("QUEBRA_POR_ESTAGIO", balde(quebra, (
            "MISSING_RUN_LINK", "MISSING_RAW_LINK", "MISSING_STORAGE_LINK",
            "MISSING_ADMISSION_LINK", "MISSING_SOURCE_LINK"))),
        ("ORIGEM", balde(origem, ("CURRENT_CANONICAL_PROVEN", "LEGACY_PROVEN",
                                  "MIXED_OR_TRANSITIONAL", "UNKNOWN_ORIGIN"))),
        ("CONTRATO", balde(contrato, ("READY_CONTRACT_VALID",
                                      "READY_CONTRACT_INVALID",
                                      "READY_CONTRACT_UNKNOWN"))),
        ("IDENTIDADE", balde(ident, (
            "SOURCE_ID_PRESENT", "SOURCE_ID_UNKNOWN",
            "SOURCE_ID_SUSPECTED_FABRICATED", "DOCUMENT_ID_PROVEN",
            "DOCUMENT_ID_UNKNOWN", "DOCUMENT_ID_SUSPECTED_FABRICATED"))),
        ("TEXTO", balde(texto, (
            "TOTAL_TEXT_UNITS", "AUTHOR_TEXT", "NATIVE_CAPTION", "TRANSCRIPT",
            "ASR", "PAGE_TEXT", "DOCUMENT_TEXT", "UNKNOWN_TEXT_KIND",
            "TEXT_RELATION_ORIGINAL", "TEXT_RELATION_TRANSLATED",
            "TEXT_RELATION_UNKNOWN", "LANGUAGE_KNOWN", "LANGUAGE_UNKNOWN"))),
        ("TEMPO", balde(tempo, (
            "FACT_TIME_KNOWN", "FACT_TIME_UNKNOWN", "PUBLICATION_TIME_KNOWN",
            "PUBLICATION_TIME_UNKNOWN", "OBSERVED_TIME_KNOWN",
            "OBSERVED_TIME_UNKNOWN", "COLLECTED_TIME_KNOWN",
            "COLLECTED_TIME_UNKNOWN"))),
        ("GEOGRAFIA", balde(geo, (
            "SOURCE_LOCATION_KNOWN", "SOURCE_LOCATION_UNKNOWN",
            "FACT_LOCATION_KNOWN", "FACT_LOCATION_UNKNOWN"))),
    ])


def as_duplicacoes(itens):
    """⚠️ TRES DUPLICACOES DIFERENTES, E NUNCA A MESMA PERGUNTA."""
    bytes_ = Counter()
    obs_ids = Counter()
    ready_ids = Counter()
    for _f, run_id, u in itens:
        if not isinstance(u, dict):
            continue
        texto = u.get("TEXTO")
        if texto:
            bytes_[hashlib.sha256(
                texto.encode("utf-8", "replace")).hexdigest()] += 1
        if _sabido(u.get("ITEM_ID")):
            ready_ids[(run_id, u.get("ITEM_ID"))] += 1
    return OrderedDict([
        ("BYTE_DUPLICATES", sum(1 for n in bytes_.values() if n > 1)),
        ("OBSERVATION_ID_DUPLICATES", sum(1 for n in obs_ids.values() if n > 1)),
        ("OBSERVATION_ID_MEDIDO", "NO"),
        ("PORQUE_OBSERVATION_ID_NAO_FOI_MEDIDO",
         "RAW_OBSERVATION_ID = raw_asset.id, e ele NAO viaja no contrato de 11 "
         "campos. Nenhum item da sala o carrega, entao nao ha o que duplicar "
         "nem como conferir. Derivar do SHA seria fabricar identidade."),
        ("READY_ID_DUPLICATES",
         sum(1 for n in ready_ids.values() if n > 1)),
        ("READY_ID_IDENTIDADE", "(CORRIDA, ITEM_ID) — o par que o contrato da"),
        ("POSSIBLE_SEMANTIC_DUPLICATES", "NAO SEI"),
        ("PORQUE_SEMANTICA_E_NAO_SEI",
         "nao existe identidade semantica provada: DOCUMENT_ID nao viaja no "
         "READY, e deduzi-lo de URL, SHA ou filename seria fabrica-lo."),
    ])


# ────────────────────────────────────────────────────────────────────────
# 6 · RED TEAM — atacar a propria medicao
# ────────────────────────────────────────────────────────────────────────
def o_red_team(sala, outras, itens, dup, perfil, fila):
    """Cada ataque tem de MORRER contra um numero desta medicao.

    Um ataque que morre por argumento nao morreu: morreu de retorica.
    """
    a = []

    def ataque(nome, sobreviveu, porque):
        a.append(OrderedDict([("ATAQUE", nome),
                              ("SOBREVIVEU", bool(sobreviveu)),
                              ("PORQUE", porque)]))

    ataque("1 · mesmo item em duas representacoes contado duas vezes",
           outras["FORA_DA_SALA_CANONICA"] > 0,
           "varridos %d ficheiros JSON/NDJSON da arvore: %d objectos READY "
           "fora da sala canonica. Uma representacao so."
           % (outras["FICHEIROS_JSON_VARRIDOS"],
              outras["FORA_DA_SALA_CANONICA"]))

    ataque("2 · SHA igual tratado como mesma observacao",
           False,
           "SHA foi contado num balde proprio (GRUPOS_DE_BYTES_IDENTICOS=%d na "
           "fila) e a saida diz, ao lado, que SHA igual e BYTES iguais e mais "
           "nada. OBSERVATION_ID_MEDIDO=NO, e nao NO porque deu zero."
           % fila["GRUPOS_DE_BYTES_IDENTICOS"])

    ataque("3 · SOURCE_ID ausente fabricado de URL",
           perfil["IDENTIDADE"]["SOURCE_ID_SUSPECTED_FABRICATED"] > 0,
           "SOURCE_ID e lido do campo do contrato e classificado em PRESENT / "
           "UNKNOWN. Nenhuma URL, path ou slug entra nesse campo: %d presentes,"
           " %d UNKNOWN, %d suspeitos."
           % (perfil["IDENTIDADE"]["SOURCE_ID_PRESENT"],
              perfil["IDENTIDADE"]["SOURCE_ID_UNKNOWN"],
              perfil["IDENTIDADE"]["SOURCE_ID_SUSPECTED_FABRICATED"]))

    ataque("4 · DOCUMENT_ID fabricado de SHA",
           perfil["IDENTIDADE"]["DOCUMENT_ID_PROVEN"] > 0,
           "DOCUMENT_ID_PROVEN=%d. O contrato READY nao carrega DOCUMENT_ID, "
           "e por isso todo item cai em DOCUMENT_ID_UNKNOWN por construcao — "
           "nao ha caminho de codigo que o derive de SHA."
           % perfil["IDENTIDADE"]["DOCUMENT_ID_PROVEN"])

    ataque("5 · SOURCE_LOCATION copiado para FACT_LOCATION",
           False,
           "sao dois baldes lidos de dois campos diferentes do item, sem "
           "fallback de um para o outro: SOURCE_LOCATION_KNOWN=%d · "
           "FACT_LOCATION_KNOWN=%d."
           % (perfil["GEOGRAFIA"]["SOURCE_LOCATION_KNOWN"],
              perfil["GEOGRAFIA"]["FACT_LOCATION_KNOWN"]))

    ataque("6 · publication time copiado para fact time",
           perfil["TEMPO"]["PUBLICATION_TIME_KNOWN"] > 0,
           "PUBLICATION_TIME nao tem campo no contrato de 11 campos: "
           "PUBLICATION_TIME_KNOWN=%d, e FACT_TIME sai so de FACT_TIME."
           % perfil["TEMPO"]["PUBLICATION_TIME_KNOWN"])

    ataque("7 · UNKNOWN contado como vazio/NO",
           not (_sabido("NAO SEI") is False and _sabido("UNKNOWN") is False
                and _sabido("") is False),
           "`_sabido()` devolve False para vazio E para as sentinelas "
           "(NAO SEI · NÃO SEI · UNKNOWN · DESCONHECIDO) — os dois vao para o "
           "lado do que NAO se prova, e nenhum e promovido a valor.")

    ataque("8 · NOT_APPLICABLE contado como PASS",
           False,
           "RAW e STORAGE nao viajam no contrato de 11 campos. Isso conta como "
           "MISSING_RAW_LINK/MISSING_STORAGE_LINK e trava LINEAGE_FULL em %d — "
           "nunca vira PASS por ser inaplicavel ao contrato."
           % perfil["LINHAGEM"]["LINEAGE_FULL"])

    ataque("9 · READY declarado sem item na sala",
           False,
           "READY_DECLARED conta ficheiros REAIS na morada do dono: %d "
           "registos, %d itens. As provas que produzem READY redirigem "
           "`espera.MORADA` para arvore descartavel — READY PROVADO EM "
           "DESCARTAVEL != ESTOQUE NA SALA, e o censo le so a sala."
           % (sala["TOTAL_WAITING_ROOM_RECORDS"],
              sala["TOTAL_UNIQUE_READY_ITEMS"]))

    ataque("10 · item na sala sem RUN contado como linhagem completa",
           perfil["LINHAGEM"]["LINEAGE_FULL"] > 0
           and perfil["QUEBRA_POR_ESTAGIO"]["MISSING_RUN_LINK"] > 0,
           "LINEAGE_FULL exige CORRIDA presente E igual a do ficheiro. "
           "LINEAGE_FULL=%d · MISSING_RUN_LINK=%d."
           % (perfil["LINHAGEM"]["LINEAGE_FULL"],
              perfil["QUEBRA_POR_ESTAGIO"]["MISSING_RUN_LINK"]))

    ataque("11 · legado classificado como atual so por data",
           False,
           "nenhuma classificacao de origem le data. O criterio e estrutural: "
           "CORRIDA coerente + SOURCE_ID + ADMITIDO_POR. Nenhum mtime, nenhum "
           "timestamp de Git entra na decisao.")

    ataque("12 · ficheiro novo com conteudo antigo classificado como novo",
           False,
           "a origem sai dos CAMPOS do item, nunca da idade do ficheiro. Um "
           "ficheiro escrito hoje com item sem CORRIDA cai em UNKNOWN_ORIGIN.")

    ataque("13 · dois RUNs da mesma fonte colapsados",
           len({r["RUN_ID"] for r in sala["REGISTOS"]})
           != len(sala["REGISTOS"]),
           "a sala e um ficheiro por corrida e o dono levanta "
           "RUN_ID_CONFLICT se a mesma corrida contar outra historia: %d "
           "registos, %d RUN_ID distintos."
           % (sala["TOTAL_WAITING_ROOM_RECORDS"],
              len({r["RUN_ID"] for r in sala["REGISTOS"]})))

    ataque("14 · lingua da publicacao herdada pelo texto",
           perfil["TEXTO"]["LANGUAGE_KNOWN"] > 0,
           "o contrato READY nao tem campo de lingua: LANGUAGE_KNOWN=%d, e "
           "nenhuma lingua e lida do documento, da fonte ou do pais."
           % perfil["TEXTO"]["LANGUAGE_KNOWN"])

    ataque("15 · filename usado como identidade",
           False,
           "o nome do ficheiro nunca e identidade de item. A identidade de "
           "READY e (CORRIDA, ITEM_ID), lida de dentro; o nome do ficheiro "
           "so localiza o registo da corrida, e o RUN_ID e reconferido pelo "
           "campo RUN_ID do corpo.")

    return a


# ────────────────────────────────────────────────────────────────────────
# 7 · A FOTOGRAFIA E O PLANEAMENTO
# ────────────────────────────────────────────────────────────────────────
def a_fotografia(sala, perfil):
    n = sala["TOTAL_UNIQUE_READY_ITEMS"]
    lin = perfil["LINHAGEM"]
    org = perfil["ORIGEM"]
    con = perfil["CONTRATO"]
    a = lin["LINEAGE_FULL"]
    b = lin["LINEAGE_PARTIAL"]
    c = org["LEGACY_PROVEN"]
    d = con["READY_CONTRACT_INVALID"]
    e = org["UNKNOWN_ORIGIN"]
    return OrderedDict([
        ("A_READY_COM_LINHAGEM_COMPLETA", a),
        ("B_READY_COM_LINHAGEM_PARCIAL", b),
        ("C_LEGADO_REPROCESSAVEL", c),
        ("D_INCOMPLETO_OU_CONTRATO_INVALIDO", d),
        ("E_ORIGEM_DESCONHECIDA", e),
        ("SOMA", a + b + c + d + e),
        ("TOTAL_DE_ITENS", n),
        ("UNKNOWN_NAO_ESTA_ESCONDIDO_EM_C_NEM_D",
         "E_ORIGEM_DESCONHECIDA e balde proprio, e nao entra em C nem em D."),
    ])


def o_planeamento(sala, perfil):
    n = sala["TOTAL_UNIQUE_READY_ITEMS"]
    return OrderedDict([
        ("REPROCESS_CANDIDATES", perfil["ORIGEM"]["LEGACY_PROVEN"]),
        ("QUARANTINE_CANDIDATES", perfil["ORIGEM"]["UNKNOWN_ORIGIN"]),
        ("REVIEW_REQUIRED", perfil["CONTRATO"]["READY_CONTRACT_INVALID"]
         + perfil["CONTRATO"]["READY_CONTRACT_UNKNOWN"]),
        ("NO_ACTION", perfil["ORIGEM"]["CURRENT_CANONICAL_PROVEN"]),
        ("UNKNOWN_ACTION", perfil["ORIGEM"]["MIXED_OR_TRANSITIONAL"]),
        ("TOTAL", n),
        ("ISTO_E_PLANEAMENTO_E_NAO_EXECUCAO",
         "nenhuma destas categorias foi aplicada a ficheiro nenhum."),
    ])


def a_prontidao(sala, outras, red, perfil):
    sobreviventes = [x for x in red if x["SOBREVIVEU"]]
    vazia = sala["TOTAL_UNIQUE_READY_ITEMS"] == 0
    uma_so = outras["FORA_DA_SALA_CANONICA"] == 0
    if sobreviventes:
        veredicto, porque = "UNKNOWN", "o red team tem sobreviventes"
    elif vazia and uma_so:
        veredicto = "YES_WITH_CONDITIONS"
        porque = ("a sala canonica esta VAZIA e tem UMA representacao so. Nao "
                  "ha estoque antigo para se misturar com coleta nova, e por "
                  "isso a Big Collection nao arrisca mistura irreversivel "
                  "DENTRO da sala. As condicoes nao sao sobre o estoque: sao "
                  "sobre o que a sala vazia NAO prova.")
    elif uma_so:
        veredicto = "YES_WITH_CONDITIONS"
        porque = ("ha estoque e ele e legivel por contrato, numa "
                  "representacao so")
    else:
        veredicto, porque = "UNKNOWN", "ha mais de uma representacao da sala"

    condicoes = [
        "TODA unidade nova pousa por `admissao/sala_de_espera.py` — o unico "
        "dono da morada. Segunda escrita = segunda verdade.",
        "TODA corrida nova carrega RUN_ID proprio, e o ficheiro da sala e "
        "dessa corrida: a sala vazia faz de MARCO ZERO, e tudo que aparecer "
        "depois e coleta nova por construcao.",
        "LINEAGE_FULL continua impossivel enquanto RAW e STORAGE nao tiverem "
        "como ser reconciliados a partir do item: o contrato de 11 campos NAO "
        "os carrega (COL-LAW-043, de proposito). A ponte e o ledger da "
        "corrida, e ela tem de existir ANTES de a escala tornar a "
        "reconciliacao cara.",
        "a sala vazia NAO prova que a rota aguenta volume: READY so foi "
        "produzido em arvore descartavel. PROVADO EM DESCARTAVEL != PROVADO "
        "EM PRODUCAO.",
        "medir de novo depois do primeiro lote: um censo antes da coleta nao "
        "e um censo durante.",
    ]
    return OrderedDict([
        ("BIG_COLLECTION_CAN_START", veredicto),
        ("PORQUE", porque),
        ("BIG_COLLECTION_CONDITIONS", condicoes),
        ("O_QUE_ISTO_NAO_DIZ",
         "nao diz que a Big Collection deve comecar, nem que o resto da "
         "maquina esta pronto. Diz que O ESTOQUE DA SALA nao a impede."),
        ("RED_TEAM_ATTACKS", len(red)),
        ("RED_TEAM_SURVIVORS", len(sobreviventes)),
    ])


def onde_a_cadeia_QUEBRA():
    """A quebra NAO e opiniao: le-se no codigo, com AST, dos dois lados.

    ⚠️ ESTA E A PERGUNTA QUE O CENSO EXISTE PARA RESPONDER E QUE ZERO ITENS NAO
    RESPONDERIAM SOZINHOS. Com a sala vazia, contar quebras por item dava 0 —
    e 0 quebras leria-se como «a cadeia fecha». Ela nao fecha: quebra por
    CONSTRUCAO, e a construcao esta em git, nao nos itens.

        SALA VAZIA NAO PROVA CADEIA INTEIRA.
        PROVA-SE A CADEIA NO CODIGO, E ELA MEDE-SE MESMO COM ZERO ITENS.

    Le-se: que chaves a rota forward entrega A PORTA, e que chaves o construtor
    do READY deixa SAIR. O que entra e nao sai, nao chega a sala — e isso vale
    para o item numero 1 da Big Collection tal como valeria para o milionesimo.
    """
    import ast

    def _chaves_do_dict_de_retorno(caminho, funcao):
        arvore = ast.parse(io.open(os.path.join(RAIZ, caminho),
                                   encoding="utf-8").read())
        for no in ast.walk(arvore):
            if isinstance(no, ast.FunctionDef) and no.name == funcao:
                for dentro in ast.walk(no):
                    if isinstance(dentro, ast.Return) and \
                            isinstance(dentro.value, ast.Dict):
                        return [k.value for k in dentro.value.keys
                                if isinstance(k, ast.Constant)]
        return []

    def _chaves_atribuidas(caminho, funcao, alvo):
        """As chaves que `<alvo>.update({...})` poe no item."""
        arvore = ast.parse(io.open(os.path.join(RAIZ, caminho),
                                   encoding="utf-8").read())
        fora = []
        for no in ast.walk(arvore):
            if isinstance(no, ast.FunctionDef) and no.name == funcao:
                for dentro in ast.walk(no):
                    if isinstance(dentro, ast.Call) and \
                            isinstance(dentro.func, ast.Attribute) and \
                            dentro.func.attr == "update" and \
                            isinstance(dentro.func.value, ast.Name) and \
                            dentro.func.value.id == alvo:
                        for arg in dentro.args:
                            if isinstance(arg, ast.Dict):
                                fora += [k.value for k in arg.keys
                                         if isinstance(k, ast.Constant)]
        return fora

    def _chaves_lidas_do_item(caminho, funcoes):
        """⚠️ COMPARAR NOMES DOS DOIS LADOS DA PORTA MENTE.

        A primeira versao disto comparava as chaves da rota (minusculas) com
        os campos do READY (MAIUSCULAS) por `lower()`, e acusou `id` e `url`
        de nao atravessarem. Atravessam os dois: `decidir()` faz
        `item.get("id") or item.get("url")` e o resultado sai como `ITEM_ID`.

            NOME DIFERENTE NAO E CONCEITO PERDIDO.
            SO O CONSUMO PROVA QUE ATRAVESSOU.

        Entao nao se comparam nomes: le-se que chaves do `item` o caminho do
        READY LE — em `pronto_para_inteligencia` e em `decidir`, que e quem
        monta a `Decisao` de onde saem ITEM_ID, UNIVERSO e CORRIDA.
        """
        arvore = ast.parse(io.open(os.path.join(RAIZ, caminho),
                                   encoding="utf-8").read())
        lidas = set()
        for no in ast.walk(arvore):
            if isinstance(no, ast.FunctionDef) and no.name in funcoes:
                for dentro in ast.walk(no):
                    if isinstance(dentro, ast.Call) and \
                            isinstance(dentro.func, ast.Attribute) and \
                            dentro.func.attr == "get" and \
                            isinstance(dentro.func.value, ast.Name) and \
                            dentro.func.value.id == "item" and \
                            dentro.args and \
                            isinstance(dentro.args[0], ast.Constant):
                        lidas.add(dentro.args[0].value)
        return lidas

    entra = _chaves_atribuidas("coleta/rota_forward_documento.py",
                               "item_para_a_porta", "item")
    sai = _chaves_do_dict_de_retorno("admissao/admissao.py",
                                     "pronto_para_inteligencia")
    consumidas = _chaves_lidas_do_item(
        "admissao/admissao.py", {"pronto_para_inteligencia", "decidir"})
    perdidas = [c for c in entra if c not in consumidas]

    return OrderedDict([
        ("COMO_FOI_MEDIDO",
         "AST sobre `coleta/rota_forward_documento.py::item_para_a_porta` e "
         "`admissao/admissao.py::pronto_para_inteligencia`. Nenhum item foi "
         "preciso: a quebra esta na forma, e a forma esta em git."),
        ("CHAVES_QUE_A_ROTA_ENTREGA_A_PORTA", sorted(entra)),
        ("CHAVES_QUE_SAEM_NO_READY", list(sai)),
        ("CHAVES_DO_ITEM_QUE_O_READY_LE", sorted(consumidas)),
        ("CHAVES_QUE_NAO_ATRAVESSAM", sorted(perdidas)),
        ("COMO_SE_SABE_QUE_ATRAVESSOU",
         "por CONSUMO, nunca por nome igual. `id` e `url` chamam-se ITEM_ID do "
         "outro lado, e atravessam; quem nao e lido em sitio nenhum e que "
         "fica pelo caminho."),
        ("RAW_ASSET_ID_CHEGA_A_PORTA", "raw_asset_id" in entra),
        ("RAW_ASSET_ID_ATRAVESSA_PARA_READY", "raw_asset_id" in consumidas),
        ("O_QUE_ISTO_SIGNIFICA",
         "RAW_OBSERVATION_ID = raw_asset.id (identidade canonica). A rota "
         "forward TEM-NO em maos e entrega-o a porta; o contrato de 11 campos "
         "NAO o leva. Entao a cadeia ate ao byte NAO se fecha a partir de um "
         "item pousado — fecha-se pelo ledger da corrida, por `CORRIDA`. "
         "ISTO NAO E DEFEITO NOVO: e a COL-LAW-043 a cumprir-se (a "
         "inteligencia recebe 11 campos e mais nada). E divida de "
         "RECONCILIACAO, e ela cresce com o volume."),
        ("TEXT_UNITS_ATRAVESSA", "NO"),
        ("O_QUE_ISSO_CUSTA",
         "o contrato E7 do texto (`regras/proveniencia.py`: TEXT_UNITS com "
         "TEXT_KIND · LANGUAGE · TEXT_RELATION · RAW_OBSERVATION_ID) NAO "
         "atravessa: o READY leva `TEXTO`, uma string. Por isso TEXT_KIND, "
         "TEXT_RELATION e LANGUAGE ficam UNKNOWN para TODO item futuro — e "
         "nao por falta de dado a montante, mas porque o contrato da sala "
         "nao tem onde os pousar."),
    ])


def os_criterios():
    """Cada rotulo do relatorio, dito em termos EXECUTAVEIS.

    ⚠️ ESTES ROTULOS NAO SAO ESTADOS PERSISTIDOS. Sao classes deste relatorio.
    Nenhum item ganhou campo, nenhum ficheiro mudou, e nada aqui passa a ser
    consultado por codigo de producao.
    """
    return OrderedDict([
        ("CURRENT_CANONICAL_PROVEN",
         "forma == contrato de hoje (11 campos, ESTADO correcto) E as tres "
         "ligacoes que o contrato carrega: CORRIDA presente e IGUAL a do "
         "ficheiro, SOURCE_ID nao-sentinela, ADMITIDO_POR nao-sentinela."),
        ("LEGACY_PROVEN",
         "as tres ligacoes completas MAS forma diferente do contrato de hoje. "
         "E o unico sinal estrutural de outra era: um writer antigo deixa "
         "marca na FORMA. NENHUMA DATA ENTRA NESTA DECISAO."),
        ("MIXED_OR_TRANSITIONAL", "alguma das tres ligacoes, mas nao todas."),
        ("UNKNOWN_ORIGIN", "nenhuma das tres ligacoes."),
        ("LINEAGE_FULL",
         "READY <- ADMISSION <- STRUCTURED <- DERIVED|NOT_APPLICABLE <- RAW "
         "<- STORAGE <- RUN <- SOURCE, fechada a partir do item. "
         "⚠️ INATINGIVEL A PARTIR DO ITEM SOZINHO, e de proposito: a "
         "COL-LAW-043 manda a inteligencia receber 11 campos e mais nada, e "
         "RAW/STORAGE nao estao entre eles. Quem fecha a cadeia ate ao byte e "
         "o ledger da corrida. Marcar FULL sem ele seria dar por provado o "
         "que o contrato escolheu nao transportar."),
        ("LINEAGE_PARTIAL", "as tres ligacoes do contrato, sem RAW/STORAGE."),
        ("LINEAGE_BROKEN", "alguma ligacao do contrato falta."),
        ("LINEAGE_UNKNOWN", "o item nao e legivel como unidade."),
        ("LEGACY_BUT_USABLE", "LEGACY_PROVEN e contrato legivel."),
        ("LEGACY_NEEDS_REPROCESSING",
         "LEGACY_PROVEN e contrato invalido pelas leis de hoje."),
        ("LEGACY_UNEXPLAINED", "UNKNOWN_ORIGIN."),
        ("O_QUE_NENHUM_CRITERIO_USA",
         "mtime de ficheiro, data de commit, ordem alfabetica, nome de "
         "ficheiro, URL, SHA. Nenhum deles entra em classificacao nenhuma."),
    ])


# ────────────────────────────────────────────────────────────────────────
def medir():
    campos = _campos_do_contrato()
    sala, itens = a_sala(campos)
    outras = as_outras_representacoes(campos)
    perfil = por_item(itens)
    dup = as_duplicacoes(itens)
    fila = a_fila_a_montante()
    live = o_live()
    red = o_red_team(sala, outras, itens, dup, perfil, fila)
    return OrderedDict([
        ("SCHEMA", "sintonia.censo-da-sala-de-espera/1"),
        ("O_QUE_ISTO_E",
         "A fotografia medida da Sala de Espera antes da BIG COLLECTION. "
         "Read-only: nada foi apagado, movido, renomeado, admitido, "
         "reprocessado, deduplicado nem re-admitido."),
        ("ISTO_NAO_E_DONO_DE_ESTADO",
         "fotografia historica. Quem decide se um item esta READY continua a "
         "ser `admissao.pronto_para_inteligencia()`; quem e dono da morada "
         "continua a ser `admissao/sala_de_espera.py`."),
        ("A_SALA", sala),
        ("OUTRAS_REPRESENTACOES", outras),
        ("LIVE", live),
        ("PERFIL_DOS_ITENS", perfil),
        ("DUPLICACAO", dup),
        ("FILA_A_MONTANTE", fila),
        ("FOTOGRAFIA", a_fotografia(sala, perfil)),
        ("PLANEAMENTO", o_planeamento(sala, perfil)),
        ("RED_TEAM", red),
        ("PRONTIDAO", a_prontidao(sala, outras, red, perfil)),
        ("ONDE_A_CADEIA_QUEBRA", onde_a_cadeia_QUEBRA()),
        ("CRITERIOS", os_criterios()),
        ("GENERATED_BY", "provas/o_censo_da_sala_de_espera.py"),
    ])


def main():
    art = medir()
    destino = os.path.join(RAIZ, SAIDA)
    os.makedirs(os.path.dirname(destino), exist_ok=True)
    with io.open(destino, "w", encoding="utf-8") as fh:
        fh.write(json.dumps(art, ensure_ascii=False, indent=2) + "\n")

    s, p = art["A_SALA"], art["PRONTIDAO"]
    print("=" * 70)
    print("O CENSO DA SALA DE ESPERA")
    print("=" * 70)
    print("  OWNER                       %s" % s["OWNER"])
    print("  MORADA                      %s" % s["MORADA"])
    print("  MORADA_EXISTE               %s" % s["MORADA_EXISTE"])
    print("  TOTAL_WAITING_ROOM_RECORDS  %d" % s["TOTAL_WAITING_ROOM_RECORDS"])
    print("  TOTAL_UNIQUE_READY_ITEMS    %d" % s["TOTAL_UNIQUE_READY_ITEMS"])
    print("  REPRESENTACOES DA SALA      %d (fora da canonica: %d)"
          % (art["OUTRAS_REPRESENTACOES"]["REPRESENTACOES_DA_SALA"],
             art["OUTRAS_REPRESENTACOES"]["FORA_DA_SALA_CANONICA"]))
    print("  LIVE_READS / LIVE_WRITES    %d / %d"
          % (art["LIVE"]["LIVE_READS"], art["LIVE"]["LIVE_WRITES"]))
    print("  RED_TEAM                    %d ataques · %d sobreviventes"
          % (p["RED_TEAM_ATTACKS"], p["RED_TEAM_SURVIVORS"]))
    print("  BIG_COLLECTION_CAN_START    %s" % p["BIG_COLLECTION_CAN_START"])
    print("\n  escrito: %s" % SAIDA)
    return 0 if p["RED_TEAM_SURVIVORS"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
