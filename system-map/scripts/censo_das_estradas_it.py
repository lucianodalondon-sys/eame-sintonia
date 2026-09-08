# -*- coding: utf-8 -*-
"""CENSO DAS ESTRADAS DA COLETA ITALIANA — quantas são, e quais já fecham.

POR QUE ISTO VEM ANTES DA SEGUNDA FONTE
---------------------------------------
Provámos UMA estrada de ponta a ponta: a ARPAV. Não sabemos quantas estradas
diferentes existem — e sem isso, «a segunda fonte» tanto pode ser a prova de
uma cadeia nova como a repetição da que já foi provada.

    PROVAR UMA FONTE NÃO PROVA UMA ESTRADA.
    MAS PROVAR UMA ESTRADA PODE POUPAR TRINTA CANÁRIOS.

O QUE É UMA ESTRADA
-------------------
Uma `ROUTE CLASS` **não é uma fonte**. É o conjunto de fontes que partilha a
mesma cadeia operacional:

    descoberta → busca → bruto → corrida → checkpoint → derivação
    → persistência estruturada → admissão

Se duas fontes só diferem em URL, `source_id` e receita, são a **mesma**
estrada. Se uma exige sessão de navegador e a outra um `GET`, são **duas**.

    SOURCE ≠ ENDPOINT ≠ ROUTE ≠ EXECUTOR ≠ ARTIFACT

O QUE ESTE FICHEIRO NÃO FAZ
---------------------------
Não coleta, não chama fonte nenhuma, não gasta API, não escreve produção. Ele
lê o que a casa já tem e agrupa. Medir antes de andar.
"""
import json
import os
import re
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

FONTES = os.path.join("system-map", "data", "sources.generated.json")
CENSO_COLETA = os.path.join("system-map", "data", "censo-da-coleta.generated.json")
LEDGER = os.path.join("data", "collection-ledger", "italy", "observations.ndjson")
RECEITAS = os.path.join("pedido", "receitas.py")


def _abs(rel):
    return os.path.join(RAIZ, rel.replace("/", os.sep))


def _ler(rel):
    caminho = _abs(rel)
    if not os.path.exists(caminho):
        return None
    with open(caminho, encoding="utf-8") as f:
        return json.load(f)


# ─────────────────────────────────────────────────────────────────────────
# OS ESTADOS — e o que cada um recusa dizer
# ─────────────────────────────────────────────────────────────────────────
# A escada é a mesma que esta casa já usa, e a distância entre os dois últimos
# degraus é a que custou caro várias vezes:
#
#     CAN DO  ≠  DID DO.
ESTADOS = ("UNKNOWN", "DECLARED", "CODE", "LOCAL_TESTED", "DB_TESTED",
           "LIVE_SCHEMA", "OBSERVED", "BLOCKED", "RETIRED")


# ─────────────────────────────────────────────────────────────────────────
# AS ESTRADAS, DECLARADAS A PARTIR DO QUE FOI MEDIDO
# ─────────────────────────────────────────────────────────────────────────
# Cada classe diz quem são os donos de cada etapa. Onde não há dono, escreve-se
# `AUSENTE` — não se inventa um nome para o quadrado ficar preenchido.
ESTRADAS = [
    {
        "ID": "RC-01",
        "NOME": "Documento oficial por HTTP",
        "CADEIA": "URL conhecida → GET → PDF/HTML → bruto → texto",
        "DISCOVER": "a URL vem do contrato da fonte (sem descoberta própria)",
        "FETCH": "guarda/portas_live.py::buscar",
        "RAW": "guarda/preservar_coleta.py",
        "RUN": "guarda/preservar_coleta.py (collection_run)",
        "CHECKPOINT": "NAO_SE_APLICA — busca única por documento",
        "PORQUE_SEM_CHECKPOINT": (
            "e um download one-shot: nao ha cursor a guardar. Criar checkpoint "
            "aqui so para pintar um quadradinho verde seria inventar estado."),
        "DERIVED": "coleta/executor_texto_de_pdf.py + guarda/preservar_derivado.py",
        "STRUCTURED": "AUSENTE",
        "ADMISSION": "admissao/admissao.py (nao ligado a esta estrada)",
        "CUSTO": "gratuito",
        "ESTADO": "OBSERVED",
        "PROVA": ("ARPAV IT-T2-002 em producao: run IT-CANARY-20260908T174427Z, "
                  "raw_asset 890, derived_artifact 1, retry REUSED"),
        "BLOQUEADOR": ("sem persistencia estruturada e sem admissao ligada: o "
                       "texto existe e ninguem o julga"),
    },
    {
        "ID": "RC-02",
        "NOME": "Coletor recorrente italiano (piloto)",
        "CADEIA": "catalogo de fontes → GET em lote → loja local → ledger NDJSON",
        "DISCOVER": "coleta/italy_find_docs.mjs",
        "FETCH": "coleta/italy_recurrent_collect.mjs",
        "RAW": "data/collection-store (ficheiros no Git)",
        "RUN": "data/collection-ledger/italy/runs.ndjson",
        "CHECKPOINT": "comparacao por hash do documento",
        "DERIVED": "AUSENTE nesta cadeia",
        "STRUCTURED": "AUSENTE",
        "ADMISSION": "AUSENTE",
        "CUSTO": "gratuito",
        "ESTADO": "CODE",
        "PROVA": "6 corridas e 144 observacoes no ledger, tudo fora do banco",
        "BLOQUEADOR": ("⚠️ ESCREVE ESTADO OPERACIONAL NO GIT (P-011): a loja, o "
                       "ledger e as corridas vivem em ficheiros versionados. E "
                       "nao usa nenhum dos donos canonicos."),
    },
    {
        "ID": "RC-03",
        "NOME": "API oficial de plataforma social",
        "CADEIA": "API com chave → JSON → ficheiro de amostra",
        "DISCOVER": "coleta/youtube_janela.py",
        "FETCH": "coleta/youtube_janela.py",
        "RAW": "AUSENTE — nao passa por preservar_coleta",
        "RUN": "RUN-MANIFEST.json (ficheiro)",
        "CHECKPOINT": "coleta/coleta_checkpoint.py",
        "DERIVED": "ferramentas/youtube_transcrever.py (Whisper)",
        "STRUCTURED": "AUSENTE",
        "ADMISSION": "AUSENTE",
        "CUSTO": "gratuito com quota",
        "ESTADO": "CODE",
        "PROVA": "corpus ES-T8-001 com 15 transcricoes; nenhuma corrida italiana",
        "BLOQUEADOR": ("a legenda que a plataforma entrega e RAW_CAPTURE e nao "
                       "passa por raw_asset; persistencia operacional aberta"),
    },
    {
        "ID": "RC-04",
        "NOME": "Sessão de navegador em página pública",
        "CADEIA": "navegador com sessao → DOM → extracao",
        "DISCOVER": "coleta/instagram_janela.py",
        "FETCH": "coleta/instagram_coleta.py + ferramentas/cdp.py",
        "RAW": "AUSENTE",
        "RUN": "ficheiro de amostra",
        "CHECKPOINT": "coleta/coleta_checkpoint.py",
        "DERIVED": "ferramentas/instagram_transcrever.py",
        "STRUCTURED": "AUSENTE",
        "ADMISSION": "AUSENTE",
        "CUSTO": "gratuito, mas depende de sessao da maquina do operador",
        "ESTADO": "CODE",
        "PROVA": "workflow sintonia-scrap existe e corre",
        "BLOQUEADOR": "sessao nao e reproduzivel no CI; bruto sem dono",
    },
    {
        "ID": "RC-05",
        "NOME": "Rota paga de escalada (Apify)",
        "CADEIA": "ator pago → dataset → ficheiro",
        "DISCOVER": "NAO_SE_APLICA",
        "FETCH": "coleta/comunicacao_coleta.py (ator Apify)",
        "RAW": "data/samples/raw-paid (ficheiros)",
        "RUN": "RUN-MANIFEST.json",
        "CHECKPOINT": "coleta/coleta_checkpoint.py",
        "DERIVED": "AUSENTE",
        "STRUCTURED": "guarda/catalogo_importar.py (so ES)",
        "ADMISSION": "AUSENTE",
        "CUSTO": "PAGO",
        "ESTADO": "CODE",
        "PROVA": "13 corridas no RUN-MANIFEST, todas nao italianas",
        "BLOQUEADOR": ("COL-LAW-019: os cinco campos que justificam a escalada "
                       "para rota paga nao existem em ficheiro nenhum"),
    },
    {
        "ID": "RC-06",
        "NOME": "Conjunto regulatório oficial",
        "CADEIA": "registo nacional → ficheiro → SQL de importacao",
        "DISCOVER": "coleta/mapa_regfi.py",
        "FETCH": "coleta/regulatorio_importar.py",
        "RAW": "AUSENTE — vai direto para SQL",
        "RUN": "SQL de collection_run escrito a mao no importador",
        "CHECKPOINT": "NAO_SE_APLICA",
        "DERIVED": "NAO_SE_APLICA",
        "STRUCTURED": "supabase/importacoes/*.sql",
        "ADMISSION": "AUSENTE",
        "CUSTO": "gratuito",
        "ESTADO": "LIVE_SCHEMA",
        "PROVA": "IT-CAMADAS e IT-LASTMILE aplicados; nenhum menciona raw_asset",
        "BLOQUEADOR": "importa camadas analiticas e NUNCA importou a procedencia",
    },
    {
        "ID": "RC-07",
        "NOME": "Corpus científico (metadados)",
        "CADEIA": "OpenAlex/ORCID → JSON → ficheiro",
        "DISCOVER": "coleta/corpus_pesquisador.py",
        "FETCH": "coleta/corpus_pesquisador.py",
        "RAW": "AUSENTE",
        "RUN": "RUN-MANIFEST.json",
        "CHECKPOINT": "AUSENTE",
        "DERIVED": "NAO_SE_APLICA — metadado nao e documento",
        "STRUCTURED": "AUSENTE",
        "ADMISSION": "AUSENTE",
        "CUSTO": "gratuito",
        "ESTADO": "CODE",
        "PROVA": "declarado em pedido/receitas.py::EXECUTORES T7",
        "BLOQUEADOR": ("⚠️ METADADO DE ARTIGO NAO E PDF PRESERVADO. Descoberto "
                       "nao e coletado, e a cadeia para no metadado."),
    },
]


def _fontes_italianas():
    d = _ler(FONTES) or {}
    return d.get("MASTER_ITALIANO") or []


def _familia(fonte):
    """A família da fonte, lida do que ela declara — não do nome.

    Onde o `access_method` não foi provado, a família fica `NAO_SEI`. É a
    maioria, e escondê-la atrás de um palpite faria o mapa parecer pronto.
    """
    metodo = (fonte.get("access_method") or "").upper()
    dono = (fonte.get("owner_kind") or "").upper()
    if metodo.startswith("NÃO SEI") or metodo.startswith("NAO SEI") or not metodo:
        return "NAO_SEI"
    if "API" in metodo or "SDMX" in metodo or "JSON" in metodo:
        return "OFFICIAL_API"
    if "PDF" in metodo or "HTTP" in metodo or "DOWNLOAD" in metodo:
        return "OFFICIAL_HTTP_DOCUMENT"
    if "RSS" in metodo or "FEED" in metodo:
        return "FEED"
    if "HTML" in metodo or "SITE" in metodo:
        return "STATIC_HTML"
    if dono == "COMPANY":
        return "COMPANY_SITE"
    return "OUTRA"


def _coletadas():
    """Quais fontes italianas têm prova de coleta — do ledger, não da intenção."""
    caminho = _abs(LEDGER)
    if not os.path.exists(caminho):
        return {}
    vistas = {}
    with open(caminho, encoding="utf-8") as f:
        for linha in f:
            linha = linha.strip()
            if not linha:
                continue
            try:
                o = json.loads(linha)
            except ValueError:
                continue
            sid = o.get("SOURCE_ID")
            if sid:
                vistas[sid] = vistas.get(sid, 0) + 1
    return vistas


def censo_das_fontes():
    fontes = _fontes_italianas()
    coletadas = _coletadas()
    por_familia, por_veredito, sem_rota = {}, {}, []
    detalhe = []
    for s in fontes:
        fam = _familia(s)
        por_familia[fam] = por_familia.get(fam, 0) + 1
        v = s.get("verdict") or "NAO SEI"
        por_veredito[v] = por_veredito.get(v, 0) + 1
        obs = coletadas.get(s["source_id"], 0)
        if fam == "NAO_SEI":
            sem_rota.append(s["source_id"])
        detalhe.append({
            "SOURCE_ID": s["source_id"], "NOME": s.get("name", "")[:60],
            "TERRITORIO": s.get("territory"), "PAPEL": s.get("role"),
            "FAMILIA": fam, "VEREDITO": v,
            "OBSERVACOES_NO_LEDGER": obs,
            "ROUTE_CLASS": ("RC-02" if obs else
                            "RC-01" if fam == "OFFICIAL_HTTP_DOCUMENT" else
                            "NAO_ATRIBUIDA"),
        })
    return {
        "O_QUE_E": (
            "As fontes italianas do registo mestre, agrupadas por familia. A "
            "familia sai do `access_method` DECLARADO — onde ele nao foi "
            "provado, fica NAO_SEI, porque um palpite faria o mapa parecer "
            "pronto."),
        "FONTES_ITALIANAS": len(fontes),
        "POR_FAMILIA": dict(sorted(por_familia.items())),
        "POR_VEREDITO": dict(sorted(por_veredito.items())),
        "COM_PROVA_DE_COLETA": len([d for d in detalhe
                                    if d["OBSERVACOES_NO_LEDGER"]]),
        "SEM_ROTA_CONHECIDA": len(sem_rota),
        "QUAIS_SEM_ROTA": sem_rota,
        "FONTES": detalhe,
    }


def censo_dos_executores():
    d = _ler(CENSO_COLETA) or {}
    medidos = (d.get("LISTAS") or {}).get("executores") or []
    # Os coletores em JavaScript nao entram no censo de Python, e sao
    # justamente os da estrada italiana recorrente. Contam-se a parte para
    # ninguem os dar por inexistentes.
    mjs = sorted(n for n in os.listdir(_abs("coleta")) if n.endswith(".mjs"))
    fonte_receitas = ""
    if os.path.exists(_abs(RECEITAS)):
        with open(_abs(RECEITAS), encoding="utf-8") as f:
            fonte_receitas = f.read()
    declarados = re.findall(r'"id":\s*"([a-z0-9-]+)"', fonte_receitas)
    return {
        "O_QUE_E": (
            "Quem sai para fora e traz alguma coisa. O censo de Python mede "
            "uns; os coletores em JavaScript sao outros, e sao justamente os da "
            "estrada italiana recorrente."),
        "EXECUTORES_PYTHON": len(medidos),
        "COLETORES_MJS": len(mjs),
        "QUAIS_MJS": ["coleta/%s" % n for n in mjs],
        "DECLARADOS_NA_RECEITA": sorted(set(declarados)),
        "QUANTOS_DECLARADOS": len(set(declarados)),
        "A_LACUNA": (
            "%d executores medidos e %d declarados na receita. O que nao esta "
            "declarado nao passa pelo orquestrador — corre por chamada direta, "
            "e e a G-05." % (len(medidos), len(set(declarados)))),
    }


def censo_das_estradas():
    fontes = censo_das_fontes()
    por_estado = {}
    for e in ESTRADAS:
        por_estado[e["ESTADO"]] = por_estado.get(e["ESTADO"], 0) + 1
    fechadas = [e["ID"] for e in ESTRADAS if e.get("FECHADA")]
    # Quantas fontes cabem na estrada ja provada sem novo canario de fundacao.
    mesma_estrada = [f["SOURCE_ID"] for f in fontes["FONTES"]
                     if f["ROUTE_CLASS"] == "RC-01"]
    return {
        "O_QUE_E": (
            "Uma ROUTE CLASS e o conjunto de fontes que partilha a mesma cadeia "
            "operacional. Duas fontes que so diferem em URL e receita sao a "
            "MESMA estrada; uma que exige sessao de navegador e outra."),
        "ESTRADAS": len(ESTRADAS),
        "POR_ESTADO": dict(sorted(por_estado.items())),
        "FECHADAS": len(fechadas),
        "PORQUE_NENHUMA_FECHA": (
            "COLLECTION_ROUTE_CLOSED exige doze condicoes. Ate a RC-01, que e a "
            "unica OBSERVED, falha em duas: nao tem persistencia estruturada nem "
            "admissao ligada. O texto existe e ninguem o julga."),
        "FONTES_QUE_CABEM_NA_RC01_SEM_NOVO_CANARIO": len(mesma_estrada),
        "QUAIS": mesma_estrada,
        "DETALHE": ESTRADAS,
    }


def a_trava_da_inteligencia():
    """A regra que impede a inteligência de começar antes da coleta fechar.

    Ela **não** impede ler o código, preservar histórico ou consertar um defeito
    que ameace dados. Impede **desenvolvimento novo** — porque construir
    interpretação sobre uma coleta que ainda não sabe guardar a verdade é
    construir o andar de cima antes das fundações.
    """
    return {
        "REGRA": "COLLECTION_FOUNDATION_CLOSED != SIM → INTELLIGENCE_IMPLEMENTATION_BLOCKED",
        "O_QUE_NAO_IMPEDE": ["ler codigo", "preservar historico",
                             "corrigir defeito que ameace dados"],
        "O_QUE_IMPEDE": ["desenvolvimento novo de inteligencia",
                         "ligar sinais", "pontuacao", "recomendacao",
                         "alimentar o portal com dado de inteligencia"],
        "ONDE_SE_PROVA": "tests/test_trava_da_inteligencia.py",
        "ESTADO_HOJE": "COLLECTION_FOUNDATION_CLOSED = NAO",
    }


def main():
    fora = {
        "FONTES": censo_das_fontes(),
        "EXECUTORES": censo_dos_executores(),
        "ESTRADAS": censo_das_estradas(),
        "TRAVA_DA_INTELIGENCIA": a_trava_da_inteligencia(),
    }
    destino = os.path.join(RAIZ, "system-map", "data",
                           "estradas-it.generated.json")
    with open(destino, "w", encoding="utf-8") as f:
        json.dump(fora, f, ensure_ascii=False, indent=2)
        f.write("\n")
    F, E, R = fora["FONTES"], fora["EXECUTORES"], fora["ESTRADAS"]
    print("fontes=%d · sem rota=%d · executores py=%d mjs=%d declarados=%d "
          "· estradas=%d fechadas=%d" % (
              F["FONTES_ITALIANAS"], F["SEM_ROTA_CONHECIDA"],
              E["EXECUTORES_PYTHON"], E["COLETORES_MJS"],
              E["QUANTOS_DECLARADOS"], R["ESTRADAS"], R["FECHADAS"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
