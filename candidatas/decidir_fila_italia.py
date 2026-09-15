#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DECIDIR A FILA ITALIANA — sem abrir uma unica fonte.

    py candidatas/decidir_fila_italia.py            # mede e mostra
    py candidatas/decidir_fila_italia.py --escrever # mede, mostra e grava

O QUE ESTE FICHEIRO FAZ, E O QUE NAO FAZ
-----------------------------------------
Ele NAO coleta. Nao abre rede, nao faz HTTP, nao le nada fora desta arvore.
Toda a prova que usa ja estava versionada aqui desde 14/09/2026:

    candidatas/ITALY-SOURCE-DISCOVERY-2026-09-14.xlsx     sonda HTTP read-only
    candidatas/ITALY-SOURCE-QUALIFICATION-2026-09-14.xlsx qualificacao 7D
    docs/fontes/ATLAS-DE-FONTES-EAME.md                   quem ja esta registada
    candidatas/ITALY-SOURCE-MASTER-V1.json                o outro emissor de ID

Ele responde UMA pergunta por candidata: com a prova que EXISTE hoje, esta
fonte pode subir de degrau, tem de ser recusada, ou fica em analise?

AS TRES REGRAS, E PORQUE CADA UMA CUSTOU CARO
----------------------------------------------
REGRA 1 · RECUSAR EXIGE PROVA DE QUE A FONTE NAO SERVE.

    O atlas ja escreve a lei, no proprio cabecalho do VERDICT:
    «Nunca converter "nao consegui verificar" em RED.»

    A qualificacao de 14/09 recusou 25 fontes. Lidas as linhas de sonda
    dessas mesmas 25, a camada de validacao tinha dito PASS nas 25, com
    REJECTION_REASON vazia. A recusa nasceu depois, e assentava em:

        12 x  HTTP 429 + THIN_BODY          -> pedido travado por ritmo
        10 x  PLATFORM_GENERIC_TITLE        -> muro de login da plataforma
         3 x  «duplicata real de ...0221»   -> ver REGRA 1b

    Nenhum desses tres factos diz o que a fonte entrega. Dizem que ninguem
    conseguiu ler. E «nao li» nao e «nao serve».

REGRA 1b · UM MURO DE LOGIN NAO E UMA IDENTIDADE.

    Tres paginas do LinkedIn de TRES donos diferentes — FreshPlaza
    (company/1602695), Koppert Italia (company/24658052) e a Libera
    Universita di Bolzano (company/833389) — foram declaradas duplicatas
    umas das outras. Foram, porque o endereco canonico guardado para todas
    era o mesmo: `https://www.linkedin.com/login`, a pagina para onde o
    LinkedIn atira quem nao esta autenticado.

        DEDUPLICAR PELO ENDERECO FINAL FUNDE TODA A PLATAFORMA NUM SO DONO.

    O identificador estavel de cada uma estava na mesma folha, na coluna
    URL_TESTADA, e distingue as tres sem ambiguidade.

REGRA 2 · REGISTAR EXIGE O QUE O ATLAS EXIGE — E ELE EXIGE UM ITEM.

    «Uma linha so existe aqui depois que alguem abriu a fonte, olhou o que
     ela entrega e guardou evidencia disso.»

    A regua nao foi inventada aqui: e a que as 140 fontes italianas ja
    registadas atravessaram. Lidos os manifestos delas, cada uma tem um
    REAL_EXAMPLE que e um ITEM PROPRIO da fonte — nao a pagina inicial:

        EXAMPLE_URL · TIPO_ITEM · TITULO · HTTP_STATUS · CONTENT_TYPE
        BYTES_LIDOS · SHA256_DO_QUE_FOI_LIDO · DATA_VISIVEL

    A sonda de 14/09 que qualificou as 381 nao tem nada disto. Ela abriu o
    endereco da fonte, leu o titulo da pagina e parou. Prova que o endereco
    responde, quem e o dono e que o pais e Italia — e so.

        «O ENDERECO RESPONDE» NAO E «A FONTE ENTREGA ISTO».

    A diferenca e a diferenca entre saber que uma loja existe e saber o que
    ela vende. Por isso este ficheiro nao promove nenhuma candidata da fila:
    promover 241 fichas com REAL_EXAMPLE em branco poria no atlas 241 linhas
    a dizer «fonte registada» sem ninguem ter aberto um unico item — e com
    isso a palavra REGISTADA deixaria de significar o que significa nas 140
    que la estao.

REGRA 3 · O RESTO FICA EM_ANALISE, COM O QUE FALTA ESCRITO.

    EM_ANALISE nao e limbo. Cada linha leva a prova que tem e a frase exacta
    do que falta — que e, quase sempre, uma unica coisa: um exemplo real.
"""
from __future__ import annotations

import csv
import json
import os
import re
import sys
from datetime import date
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
GAVETA = RAIZ / "candidatas"
sys.path.insert(0, str(GAVETA))
sys.path.insert(0, str(RAIZ / "leis"))

import fonte_do_atlas as ATLAS          # noqa: E402  a autoridade do SOURCE_ID
import fonte_nova                       # noqa: E402  a UNICA porta da fila
import xlsx_simples as XL               # noqa: E402  leitor de xlsx sem dependencia

DISCOVERY = GAVETA / "ITALY-SOURCE-DISCOVERY-2026-09-14.xlsx"
QUALIFICACAO = GAVETA / "ITALY-SOURCE-QUALIFICATION-2026-09-14.xlsx"
DECISOES = GAVETA / "ITALY-SOURCE-DECISIONS-2026-09-15.csv"
CONTRATOS_CAND = GAVETA / "ITALY-CONTRACT-CANDIDATES-2026-09-15.csv"

#: A sonda declara o proprio limite nesta frase. E dela que sai a REGRA 2.
PAYLOAD_NAO_PRESERVADO = "payload nao preservado"

#: O que falta a TODAS as 241, escrito uma vez so para nao divergir.
FALTA_O_ITEM = ("um item real da fonte, aberto e identificado como o atlas exige "
                "das 140 ja registadas: endereco proprio do item, tipo, titulo, "
                "HTTP, content-type, bytes e data visivel. A sonda de 14/09 leu "
                "o titulo da pagina de entrada e parou")

#: Enderecos para onde uma plataforma atira quem nao esta autenticado. Um
#: destes no lugar do endereco da fonte significa que ninguem leu a fonte.
MURO_DE_LOGIN = re.compile(
    r"(?:linkedin\.com/(?:uas/)?login"
    r"|facebook\.com/(?:login|checkpoint)"
    r"|instagram\.com/accounts/login"
    r"|/login[/?]?$|/signin[/?]?$)", re.I)

#: Codigos que dizem «nao consegui ler», nunca «nao serve».
NAO_LI = {"429", "403", "401", "408", "500", "502", "503", "504", "", "0"}


# --------------------------------------------------------------------- leitura
def _tabela(caminho: Path, folha: str) -> list[dict]:
    return XL.tabela(caminho, folha)


def normalizar(url: str) -> str:
    """A mesma chave que a porta da fila usa. Duas chaves = duas filas."""
    return fonte_nova.normalizar(url)


def _indexar(linhas: list[dict], *colunas_url: str) -> dict:
    """Indexa por cada endereco que a linha declara. A primeira ganha."""
    fora: dict[str, dict] = {}
    for r in linhas:
        for c in colunas_url:
            k = normalizar(r.get(c, ""))
            if k:
                fora.setdefault(k, r)
    return fora


def _por_nome(linhas: list[dict], coluna: str = "NOME") -> dict:
    fora: dict[str, dict] = {}
    for r in linhas:
        fora.setdefault((r.get(coluna) or "").strip().lower(), r)
    return fora


def anfitriao(url: str) -> str:
    """So o dominio. Serve para AVISAR de vizinhanca, nunca para decidir."""
    return normalizar(url).split("/")[0]


def enderecos_do_atlas(texto: str) -> dict[str, str]:
    """endereco normalizado -> SOURCE_ID da ficha que o declara.

    ⚠️ O atlas PARTE URL LONGO EM DUAS LINHAS. Medido: 6 das 155 linhas `URL:`
    continuam na linha seguinte, indentadas. Um leitor de `^URL:\\s*(\\S+)`
    fica com metade do endereco — e meia chave nunca casa, o que faz uma fonte
    JA REGISTADA aparecer como candidata por registar.

        UM ENDERECO TRUNCADO NAO DA ERRO. DA UMA FONTE DUPLICADA.
    """
    fora: dict[str, str] = {}
    linhas = texto.splitlines()
    bloco = None
    for n, bruta in enumerate(linhas):
        s = bruta.strip()
        m = re.match(r"^SOURCE_ID:\s*(\S+)", s)
        if m:
            bloco = m.group(1)
            continue
        u = re.match(r"^URL:\s*(\S+)", s)
        if not u:
            continue
        endereco = u.group(1)
        # Junta as continuacoes: linha indentada que nao abre campo novo.
        k = n + 1
        while k < len(linhas):
            seg = linhas[k]
            if not re.match(r"^\s{6,}\S", seg) or re.match(r"^\s*[A-Z_0-9]{3,}:", seg):
                break
            endereco += seg.strip()
            k += 1
        fora.setdefault(normalizar(endereco.strip("`<>,;")), bloco or "?")
    return fora


# ------------------------------------------------------------------- o contrato
def decidir(cand: dict, q: dict, v: dict, recusa_anterior: dict | None,
            ja_no_atlas: str | None, vizinha: str = "") -> dict:
    """A decisao de UMA candidata. Devolve DECISION · WHY · EVIDENCE · STATUS."""
    nome = cand.get("NOME", "")
    url_declarado = cand.get("URL", "")
    q = q or {}
    v = v or {}

    http = str(q.get("HTTP_STATUS") or v.get("HTTP_STATUS") or "").strip()
    canonico = (q.get("URL_CANONICAL") or v.get("URL_FINAL") or url_declarado).strip()
    testado = (v.get("URL_TESTADA") or q.get("URL_ORIGINAL") or url_declarado).strip()
    metodo = v.get("VALIDATION_METHOD", "")
    prova = q.get("EVIDENCE") or ""

    # Degrau ja vencido: o atlas mostra esta fonte. Nada a decidir.
    if ja_no_atlas:
        return dict(DECISION="JA_REGISTADA", STATUS="PROMOVIDA", SOURCE_ID=ja_no_atlas,
                    WHY="o atlas ja tem ficha para este endereco",
                    EVIDENCE="docs/fontes/ATLAS-DE-FONTES-EAME.md",
                    O_QUE_FALTA="", VIZINHA_NO_ATLAS="")

    # ⚠️ Vizinhanca NAO e identidade — mas ignora-la emite ID a dobrar.
    # O atlas tem ficha para `unitus.it/dipartimenti/dafne/` (IT-T5-014) e a
    # fila traz `unitus.it/it/dipartimento/dafne`: o mesmo departamento, por
    # duas portas. Quem alocar ID novo sem olhar cria a segunda identidade da
    # mesma fonte, e o atlas proibe-o por escrito (campo DERIVA_DE).
    aviso_vizinha = ""
    if vizinha:
        aviso_vizinha = ("ATENCAO antes de emitir SOURCE_ID: o atlas ja tem ficha "
                         "no mesmo dominio (%s). Reconciliar — pode ser a mesma "
                         "fonte por outra porta, e nesse caso escreve-se DERIVA_DE, "
                         "nao um numero novo." % vizinha)

    # REGRA 1b — o endereco guardado e um muro, nao a fonte.
    endereco_e_muro = bool(MURO_DE_LOGIN.search(canonico))

    # REGRA 1 — recusar exige prova de que NAO SERVE.
    if recusa_anterior:
        motivo = (recusa_anterior.get("REASON") or "").strip()
        flags = (v.get("FLAGS") or "").strip()
        nao_leu = (http in NAO_LI) or ("THIN_BODY" in flags) \
            or ("PLATFORM_GENERIC_TITLE" in flags) or endereco_e_muro
        if nao_leu:
            razao = []
            if http in NAO_LI and http:
                razao.append("HTTP %s nao entrega corpo legivel" % http)
            if "THIN_BODY" in flags:
                razao.append("THIN_BODY: veio corpo, e vazio de conteudo")
            if "PLATFORM_GENERIC_TITLE" in flags:
                razao.append("o titulo lido era o nome da plataforma, nao o da fonte")
            if endereco_e_muro:
                razao.append("o endereco guardado (%s) e o muro de login da "
                             "plataforma, nao a fonte" % canonico)
            return dict(
                DECISION="EM_ANALISE", STATUS="EM_ANALISE", SOURCE_ID="",
                WHY=("RECUSA ANTERIOR REVOGADA. Estava escrito «%s», e a prova "
                     "citada nao sustenta isso: %s. O atlas proibe converter "
                     "«nao consegui verificar» em recusa."
                     % (motivo[:70], "; ".join(razao))),
                EVIDENCE=("qualificacao 2026-09-14 REJECT · sonda diz "
                          "VALIDATION_RESULT=%s · FLAGS=%s"
                          % (v.get("VALIDATION_RESULT", "?"), flags or "nenhuma")),
                O_QUE_FALTA=("uma leitura que atravesse a plataforma, ou um exemplo "
                             "real da propria fonte. Enderecos estaveis conhecidos: "
                             "%s" % testado),
                VIZINHA_NO_ATLAS=aviso_vizinha)
        # Recusa que a propria prova sustenta.
        return dict(DECISION="RECUSADA", STATUS="RECUSADA", SOURCE_ID="",
                    WHY=motivo,
                    EVIDENCE=(recusa_anterior.get("EVIDENCE") or "")[:220],
                    O_QUE_FALTA="", VIZINHA_NO_ATLAS=aviso_vizinha)

    # REGRA 2 — registar exige exemplo real preservado.
    sem_exemplo = PAYLOAD_NAO_PRESERVADO in metodo or not metodo
    provado = []
    if q.get("OWNER_MATCH"):
        provado.append("dono %s" % q["OWNER_MATCH"])
    if q.get("ITALY_SCOPE_PROVED"):
        provado.append("pais: %s" % q["ITALY_SCOPE_PROVED"])
    if http:
        provado.append("endereco responde HTTP %s" % http)
    if q.get("QUALIFICATION_GATE"):
        provado.append("portao 7D = %s (%s/100)"
                       % (q["QUALIFICATION_GATE"], q.get("QUALIFICATION_SCORE", "?")))

    falta = []
    if sem_exemplo:
        falta.append(FALTA_O_ITEM)
    if endereco_e_muro:
        falta.append("endereco proprio da fonte — o guardado e muro de login; "
                     "o estavel e %s" % testado)
    if str(q.get("UPDATE_SCORE", "")).upper() == "UNKNOWN":
        falta.append("frequencia de actualizacao, nunca medida")
    if q.get("URL_STATUS") in ("NEEDS_CORRECTION", "BROKEN"):
        falta.append("endereco por reconciliar (%s -> %s)"
                     % (q.get("URL_ORIGINAL", ""), canonico))

    return dict(
        DECISION="EM_ANALISE", STATUS="EM_ANALISE", SOURCE_ID="",
        WHY=("prova de existencia, nao de entrega: %s. Falta o degrau que o "
             "atlas exige para virar ficha." % ("; ".join(provado) or "nenhuma")),
        EVIDENCE=prova[:220] or ("sonda %s" % metodo[:120]),
        O_QUE_FALTA="; ".join(falta) or "nada identificado — rever a mao",
        VIZINHA_NO_ATLAS=aviso_vizinha)


# ----------------------------------------------------------------------- medida
def medir() -> dict:
    cadastro = _tabela(DISCOVERY, "CADASTRO_FONTES")
    validacao = _tabela(DISCOVERY, "VALIDACAO_URL")
    qualif = _tabela(QUALIFICACAO, "QUALIFICACAO")
    recusas = _tabela(QUALIFICACAO, "REJECT")

    ids_atlas = ATLAS._do_atlas(ATLAS._texto(str(RAIZ)))
    texto_atlas = ATLAS._texto(str(RAIZ))

    # Quem o atlas ja mostra — pelo endereco, que e o que a fila conhece.
    enderecos_atlas = enderecos_do_atlas(texto_atlas)
    anfitrioes_atlas = {}
    for endereco, sid in enderecos_atlas.items():
        anfitrioes_atlas.setdefault(endereco.split("/")[0], sid)

    idx_q = _indexar(qualif, "URL_ORIGINAL", "URL_CANONICAL")
    idx_q_nome = _por_nome(qualif)
    idx_v = _indexar(validacao, "URL_ENCONTRADA", "URL_TESTADA", "URL_FINAL")
    idx_v_nome = _por_nome(validacao)
    idx_rej_nome = _por_nome(recusas)

    linhas = []
    for c in cadastro:
        u = normalizar(c.get("URL", ""))
        n = (c.get("NOME") or "").strip().lower()
        q = idx_q.get(u) or idx_q_nome.get(n)
        v = idx_v.get(u) or idx_v_nome.get(n)
        # O endereco canonico tambem conta: a reconciliacao de 14/09 corrigiu
        # 125 enderecos, e o atlas foi escrito com o corrigido, nao com o que a
        # fila declara.
        candidatos_de_endereco = [u]
        for col in ("URL_CANONICAL", "URL_ORIGINAL"):
            k = normalizar((q or {}).get(col, ""))
            if k and k not in candidatos_de_endereco:
                candidatos_de_endereco.append(k)
        no_atlas = next((enderecos_atlas[k] for k in candidatos_de_endereco
                         if k in enderecos_atlas), None)
        vizinha = ""
        if not no_atlas:
            sid = next((anfitrioes_atlas[anfitriao(k)] for k in candidatos_de_endereco
                        if anfitriao(k) in anfitrioes_atlas), "")
            vizinha = sid or ""
        d = decidir(c, q, v, idx_rej_nome.get(n), no_atlas, vizinha)
        d.update(CANDIDATE=c.get("NOME", ""), TIPO=c.get("TIPO", ""),
                 PAIS=c.get("PAIS", ""), URL=c.get("URL", ""),
                 PARA_QUE_SERVE=c.get("PARA_QUE_SERVE", ""),
                 QUEM_VIU=c.get("QUEM_VIU", ""), ONDE_VIU=c.get("ONDE_VIU", ""),
                 NOTA=c.get("NOTA", ""))
        linhas.append(d)

    return {"linhas": linhas, "ids_atlas": ids_atlas,
            "enderecos_atlas": enderecos_atlas}


# ------------------------------------------------ o degrau seguinte da escada
CONTRATOS = RAIZ / "docs" / "operacao" / "CONTRATOS-DAS-FONTES-EAME.md"


def candidatas_a_contrato() -> list[dict]:
    """REGISTADA com rota provada e SEM contrato — o degrau 2 -> 3 da escada.

    Nao promove nada. Lista quem tem, hoje, o unico material de que um contrato
    precisa: um endereco que ja devolveu bytes, com o estado HTTP e o tipo do
    que voltou escritos no manifesto.

        ROTA PROVADA NAO E CONTRATO. E a materia-prima de um.

    Um contrato acrescenta o que isto NAO sabe: cadencia, o que fazer quando
    quebra, que campos se esperam de volta e quem responde. Por isso a lista
    sai como CANDIDATAS, e a decisao fica para a missao que escrever contratos.
    """
    amostras = RAIZ / "data" / "samples" / "IT-SOURCE-SAMPLES"
    if not amostras.is_dir():
        return []
    ids_atlas = ATLAS._do_atlas(ATLAS._texto(str(RAIZ)))
    ja_contratadas = set(re.findall(r"(?:EU|FR|ES|IT)-T\d{1,2}-\d{3}",
                                    CONTRATOS.read_text(encoding="utf-8"))) \
        if CONTRATOS.is_file() else set()
    master = json.loads((GAVETA / "ITALY-SOURCE-MASTER-V1.json")
                        .read_text(encoding="utf-8"))
    por_id = {s["SOURCE_ID"]: s for s in master.get("sources", [])}

    fora = []
    for sid in sorted(set(os.listdir(amostras)) - ja_contratadas,
                      key=lambda s: (int(s.split("-")[1][1:]), s)):
        manifesto = amostras / sid / "MANIFEST.json"
        if not manifesto.is_file() or sid not in ids_atlas:
            continue
        man = json.loads(manifesto.read_text(encoding="utf-8"))
        rotas, guarda = _rotas_provadas(man)
        if not rotas:
            continue                      # sem rota provada nao ha o que contratar
        fora.append({
            "SOURCE_ID": sid,
            "MASTER": por_id.get(sid, {}),
            "MANIFEST": man,
            "ROTAS": rotas,
            "BYTES_GUARDADOS": guarda,
            "PASTA": str(manifesto.relative_to(RAIZ)).replace("\\", "/")})
    return fora


def _rotas_provadas(man: dict) -> tuple[list[dict], bool]:
    """Enderecos que ja devolveram 200, nos DOIS formatos de manifesto.

    ⚠️ Esta pasta guarda duas geracoes de manifesto, e ler so uma perde 140 de
    155 fontes em silencio:

        FILES[]                  onda de 07/09 — bytes guardados em disco
        REAL_EXAMPLE{}           onda de 14/09 — item aberto, bytes NAO guardados,
                                 mas com SHA256 do que foi lido

    A segunda nao e' inferior para efeito de contrato: o que um contrato precisa
    e' do ENDERECO que devolveu 200 e do tipo do que voltou, e ambos os formatos
    dao isso. O que muda e' se os bytes ficaram — e isso vai numa coluna propria,
    nao escondido numa media.
    """
    rotas = []
    for f in man.get("FILES", []):
        if f.get("SOURCE_URL") and str(f.get("HTTP_STATUS")) == "200":
            rotas.append({"URL": f["SOURCE_URL"], "MIME": f.get("MIME", ""),
                          "BYTES": f.get("BYTES")})
    if rotas:
        return rotas, True
    ex = man.get("REAL_EXAMPLE") or {}
    if ex.get("EXAMPLE_URL") and str(ex.get("HTTP_STATUS")) == "200":
        rotas.append({"URL": ex["EXAMPLE_URL"], "MIME": ex.get("CONTENT_TYPE", ""),
                      "BYTES": ex.get("BYTES_LIDOS")})
    return rotas, False


# ------------------------------------------------------------------- impressao
def main(argv=None) -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    argv = list(argv if argv is not None else sys.argv[1:])
    escrever = "--escrever" in argv

    m = medir()
    linhas = m["linhas"]
    conta = {}
    for d in linhas:
        conta[d["DECISION"]] = conta.get(d["DECISION"], 0) + 1

    fila = [d for d in linhas if d["DECISION"] != "JA_REGISTADA"]
    contrato = candidatas_a_contrato()

    print("CANDIDATAS_MEDIDAS        = %d" % len(linhas))
    print("JA_REGISTADAS_NO_ATLAS    = %d" % conta.get("JA_REGISTADA", 0))
    print("FILA_RESTANTE             = %d" % len(fila))
    print("  EM_ANALISE              = %d" % conta.get("EM_ANALISE", 0))
    print("  RECUSADA                = %d" % conta.get("RECUSADA", 0))
    print("RECUSAS_ANTERIORES_REVOGADAS = %d"
          % sum(1 for d in fila if "RECUSA ANTERIOR REVOGADA" in d["WHY"]))
    print("CONTRACT_CANDIDATES       = %d" % len(contrato))
    print("POPULACAO_SOURCE_ID       = %d" % len(ATLAS.populacao(str(RAIZ))))

    if not escrever:
        print("\n(nada gravado — corra com --escrever)")
        return 0

    # A fila, pela porta que ja existe. Nao se escreve o JSON a mao: a porta
    # e' que sabe a forma da linha, e duas formas seriam duas filas.
    # ⚠️ So se bate a' porta para quem AINDA NAO esta na fila.
    #
    # `registar()` de um URL que ja la' esta nao cria linha nova — acrescenta
    # uma marca em VISTA_TAMBEM_POR, e esta certa em faze-lo: e' assim que a
    # fila regista que duas pessoas viram a mesma pista. Mas correr o decisor
    # nao e' ver a fonte outra vez.
    #
    #     DECIDIR SOBRE UMA CANDIDATA NAO E TER VISTO A CANDIDATA.
    #
    # Sem esta guarda, cada re-corrida carimbava 241 avistamentos que nunca
    # aconteceram, e o ficheiro crescia a cada vez sem nada mudar de facto.
    ja_na_fila = {normalizar(c["URL"]) for c in fonte_nova.carregar()["CANDIDATAS"]}
    for d in fila:
        if normalizar(d["URL"]) in ja_na_fila:
            continue
        fonte_nova.registar(
            tipo=d["TIPO"] if d["TIPO"] in fonte_nova.TIPOS else "OUTRO",
            pais=d["PAIS"] if d["PAIS"] in fonte_nova.PAISES else "OUTRO",
            nome=d["CANDIDATE"], url=d["URL"],
            para_que=d["PARA_QUE_SERVE"] or "por declarar",
            quem_viu=d["QUEM_VIU"] or "candidatas/decidir_fila_italia.py",
            onde_viu=d["ONDE_VIU"], nota=d["NOTA"])

    # ⚠️ A decisao entra num segundo passe, e nao no objecto que `registar()`
    # devolve. `registar()` re-le a fila do disco a cada chamada — mutar o que
    # ela devolve perde-se na chamada seguinte, e o ficheiro final fica com 241
    # linhas todas em CANDIDATA, sem uma unica decisao. Acontece em silencio:
    # o total esta certo e o conteudo esta vazio.
    d_fila = fonte_nova.carregar()
    por_url = {normalizar(c["URL"]): c for c in d_fila["CANDIDATAS"]}
    escritas = 0
    for d in fila:
        linha = por_url.get(normalizar(d["URL"]))
        if linha is None:
            continue
        linha["ESTADO"] = d["STATUS"]
        linha["MOTIVO_DA_RECUSA"] = d["WHY"] if d["STATUS"] == "RECUSADA" else None
        linha["PORQUE"] = d["WHY"]
        linha["EVIDENCIA"] = d["EVIDENCE"]
        linha["O_QUE_FALTA"] = d["O_QUE_FALTA"]
        linha["VIZINHA_NO_ATLAS"] = d.get("VIZINHA_NO_ATLAS") or None
        linha["DECIDIDA_EM"] = "2026-09-15"
        escritas += 1
    if escritas != len(fila):
        raise SystemExit("PARADO: decidi %d e escrevi %d. Uma fila com decisao a "
                         "menos e pior do que uma fila sem decisao nenhuma."
                         % (len(fila), escritas))
    fonte_nova.gravar(d_fila)
    print("\nFILA=%s · %d linhas" % (fonte_nova.FILA.name, d_fila["TOTAL"]))

    campos = ["CANDIDATE", "TIPO", "PAIS", "URL", "DECISION", "WHY",
              "EVIDENCE", "SOURCE_ID", "STATUS", "O_QUE_FALTA"]
    with open(DECISOES, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=campos, extrasaction="ignore")
        w.writeheader()
        for d in linhas:
            w.writerow(d)
    print("DECISOES=%s · %d linhas" % (DECISOES.name, len(linhas)))

    with open(CONTRATOS_CAND, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["SOURCE_ID", "SOURCE_NAME", "TERRITORY", "ROTAS_PROVADAS",
                    "MIME", "ROTA_EXEMPLO", "BYTES_GUARDADOS_EM_DISCO",
                    "O_QUE_O_CONTRATO_AINDA_TEM_DE_DIZER", "EVIDENCIA"])
        for o in contrato:
            mimes = sorted({str(r.get("MIME", "")).split(";")[0]
                            for r in o["ROTAS"]})
            w.writerow([
                o["SOURCE_ID"],
                o["MASTER"].get("SOURCE_NAME") or o["MANIFEST"].get("SOURCE", ""),
                o["MASTER"].get("TERRITORY") or o["SOURCE_ID"].split("-")[1],
                len(o["ROTAS"]), " · ".join(m for m in mimes if m),
                o["ROTAS"][0]["URL"],
                "SIM" if o["BYTES_GUARDADOS"] else
                "NAO — o item foi aberto e resumido (com SHA256 do que foi lido), "
                "os bytes nao ficaram",
                "cadencia · o que fazer quando quebrar · campos esperados · dono "
                "que responde — nada disto esta medido, e nenhum e adivinhavel "
                "a partir da rota",
                o["PASTA"]])
    print("CONTRACT_CANDIDATES=%s · %d linhas"
          % (CONTRATOS_CAND.name, len(contrato)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
