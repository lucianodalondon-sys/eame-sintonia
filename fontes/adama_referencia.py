#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MONTA A CASA CANÔNICA DA REFERÊNCIA ADAMA — a partir do que já existe.

    py fontes/adama_referencia.py            # regenera as vistas
    py fontes/adama_referencia.py --censo    # só mede, não escreve

O QUE ESTE FICHEIRO RESOLVE, E ELE NASCEU DE UMA MEDIÇÃO
--------------------------------------------------------
A casa tinha DUAS referências da ADAMA, construídas no mesmo dia 2026-09-02,
que não se conheciam:

    research/adama-italy-product-intelligence-deep/   602 autorizações · 0 usos
    build/…HANDOFF-V2.1.zip → DESIGN-INGEST/          163 autorizações · 2030 usos

Onde as duas opinavam nunca se contradiziam — a menor cabe inteira dentro da
maior. Não era uma briga; eram duas fotografias parciais que ninguém uniu. E o
consumidor tinha de escolher entre elas sozinho, que é exactamente o que um
dono existe para evitar.

    DUAS FOTOGRAFIAS PARCIAIS NÃO SÃO DUAS VERDADES.
    SÃO UMA VERDADE QUE NINGUÉM ACABOU DE MONTAR.

⚠️ ESTE FICHEIRO NÃO COLETA, NÃO INVENTA E NÃO FUNDE
-----------------------------------------------------
Ele LÊ os dois pacotes e o registo bruto, e escreve a camada de ligação. Não vai
à rede, não lê PDF, não adivinha um par cultura × alvo. Tudo o que ele escreve
tem de vir de um dos artefactos declarados em `FONTES`, e cada linha carrega de
qual veio.

A LEI QUE MANDA AQUI, E ELA JÁ EXISTIA
---------------------------------------
Não se inventou identidade nova. A `COL-LAW-206` da Bíblia da Coleta já separa
as três, e esta casa aplica-a ao produto:

    SOURCE_NATIVE_ID    o id que a própria fonte dá  →  o número do Ministero
    SINTONIA_STABLE_ID  o nosso, e ele não muda      →  ADAMA_PRODUCT_ID
    CANONICAL_URL       um endereço — que muda       →  a página do catálogo

E a `COL-LAW-034`: `"?"` e a string vazia não são identidade; `UNKNOWN` fica
explícito. Um registo sem produto provado escreve `UNKNOWN`, nunca um palpite.

POR QUE O `ADAMA_PRODUCT_ID` NÃO TRAZ `IT` DENTRO
--------------------------------------------------
O identificador anterior chamava-se `IT-PRODUCT-0045`. Parece identidade de
produto e é **o número da linha do registo italiano**: levá-lo para Espanha
obrigaria a renumerar tudo, e o mesmo produto teria RG diferente por país.

    A IDENTIDADE É DO PRODUTO. O PAÍS É PROVA DE PRESENÇA, E É ATRIBUTO.

Por isso `ADAMA-P-0001` e `COUNTRY_SCOPE: ["IT"]` ao lado. Quando Espanha
entrar: se houver prova de que é o mesmo produto, reutiliza-se o ID e acrescenta
`ES` ao escopo; se não houver, nasce outro ID e a reconciliação fica por fazer,
**declarada**. Nunca se afirma que dois produtos de países diferentes são o
mesmo sem prova.

COMO O ID SOBREVIVE A UMA REGENERAÇÃO
--------------------------------------
`referencia/adama/PRODUCT-MASTER.json` é **append-only** e é lido antes de
qualquer alocação. O reconhecimento faz-se por `IDENTITY_ANCHORS` — o conjunto
de coisas observadas que apontam para aquele produto (endereço do catálogo,
número de registo, nomes vistos). Âncora nova **acrescenta-se**; ID já emitido
**nunca muda** e **nunca se recicla**, mesmo que o produto saia do catálogo.

    A ÂNCORA É COMO SE RECONHECE. NÃO É O QUE SE É.

É por isso que a âncora pode ser um endereço — que a `COL-LAW-206` proíbe como
identidade — sem violar a lei: ela não é o ID, e o histórico dela fica escrito.
"""
from __future__ import annotations

import argparse
import csv
import io
import json
import os
import re
import sys
import unicodedata
import zipfile
from collections import Counter, defaultdict

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CASA = os.path.join(RAIZ, "referencia", "adama")

#: Os artefactos que provam esta casa. Nada é escrito sem vir de um destes.
FONTES = {
    "DEEP": os.path.join(RAIZ, "research", "adama-italy-product-intelligence-deep"),
    "V21_ZIP": os.path.join(RAIZ, "build", "SINTONIA-ITALY-REALITY-HANDOFF-V2.1.zip"),
    "RAW_0907": os.path.join(RAIZ, "data", "samples", "IT-SOURCE-SAMPLES",
                             "IT-T4-001", "PROD_FTS_6_20260907.csv"),
    # As doses vieram de `claude/label-intelligence-v1-italy`. Só o DADO foi
    # trazido, e trazido para DENTRO da árvore: um construtor que fosse buscar
    # a uma branch ficaria refém dela, e a referência deixaria de se poder
    # reconstruir a partir deste commit.
    "DOSES": os.path.join(RAIZ, "data", "samples", "IT-DOSE-ROTULO",
                          "IT-DOSES-2026-09-06.json"),
}
V21_BASE = "ITALY-REALITY-HANDOFF-V2.1/DESIGN-INGEST/"

#: O sentinela da casa. `leis/artefato.py` usa a mesma palavra.
NAO_SEI = "NAO SEI"
UNKNOWN = "UNKNOWN"

#: `SOURCE_ID` canônico, na língua do Atlas reconciliado na FASE 1B.
#: O vocabulário antigo não se apaga — vive em SOURCE-ID-MAP.json.
#:
#: ⚠️ `IT-ADAMA-CATALOG` DEIXOU DE SER CANÔNICO EM 2026-09-16. Nasceu a 30/08
#: (commit 77fe16d3) como identificador do catálogo comercial e nunca teve ficha
#: no Atlas. A faixa Sources decidiu que o catálogo (`/it/prodotti-adama/*` e
#: `/it/prodotti/*` — 31 + 20 páginas de produto) é
#: outro ENDPOINT da fonte que já existia — `IT-T9-008`, ADAMA Italia S.r.l. —
#: e não uma segunda fonte: mesmo publicador, mesmo site, o MESMO sitemap enumera
#: os artigos e as páginas de produto (`catalog-enumeration.json`, SHA 7648b9…).
#: Ficha: docs/fontes/ATLAS-DE-FONTES-EAME.md · IT-T9-008 · IDENTIFICADORES_LEGADOS.
#: Decisão: SINTONIA-EAME-KNOW-HOW.md §127.
#:
#:     LEGADO != CANÔNICO. O nome antigo continua a responder «como se chamava
#:     este registo quando foi produzido?» — em SOURCE_IDS_LEGACY e no mapa.
#:     PATH != SOURCE_ID: a pasta data/samples/IT-ADAMA-CATALOG/ não muda de nome.
#:
#: Este dicionário é o ÚNICO dono do mapeamento legado→canônico da casa ADAMA.
#: `adama_catalogo_snapshot.py` importa-o daqui; não há segunda cópia.
SOURCE_ID_CANONICO = {
    "SRC_FITOSANITARI_SALUTE_GOV_IT": "IT-T4-001",
    "IT-T4-001": "IT-T4-001",
    "SRC_ADAMA_COM": "IT-T9-008",
    "IT-ADAMA-CATALOG": "IT-T9-008",
    "IT-T9-008": "IT-T9-008",
}

#: Por que cada identificador legado é a MESMA fonte que o canônico. Uma prova
#: por canônico, escrita uma vez: o SOURCE-ID-MAP.json lê daqui.
SAME_SOURCE_PROOF = {
    "IT-T4-001": ("IT-T4-001 e a ficha do Ministero della Salute no "
                  "ATLAS-DE-FONTES-EAME.md, com a mesma CANONICAL_URL que o "
                  "vocabulario antigo usava."),
    "IT-T9-008": ("IT-T9-008 e a ficha «ADAMA Italia — comunicacao publica» no "
                  "ATLAS-DE-FONTES-EAME.md (dono ADAMA Italia S.r.l., IT-OWN-040). "
                  "O catalogo comercial (www.adama.com/italia/it/prodotti-adama/* e "
                  "/it/prodotti/*, 31 + 20 paginas de produto) e "
                  "outro ENDPOINT dessa fonte: mesmo publicador, mesmo site, mesmo "
                  "sitemap (/it/sitemap.xml enumera artigos e paginas de produto). "
                  "Por COL-LAW-009/205 endpoint nao e fonte. Decidido em 2026-09-16 "
                  "(know-how §127; ficha IT-T9-008, IDENTIFICADORES_LEGADOS). "
                  "IT-ADAMA-CATALOG passa a identificador LEGADO e nao se apaga."),
}


def _ler(caminho):
    with io.open(caminho, encoding="utf-8") as fh:
        return json.load(fh)


def deep(nome):
    return _ler(os.path.join(FONTES["DEEP"], nome))


_ZIP = None


def v21(nome):
    global _ZIP
    if _ZIP is None:
        _ZIP = zipfile.ZipFile(FONTES["V21_ZIP"])
    return json.loads(_ZIP.read(V21_BASE + nome).decode("utf-8"))


# ── O NOME: OBSERVADO E CANÔNICO, NUNCA UM NO LUGAR DO OUTRO ──────────────
#
# O símbolo ® chegou a montante transformado na letra R:
#
#     registo    NIMROD 250 EW     APYZA WG      COSAYR 200 SC    GOLTIX TOP
#     catálogo   NIMRODR 250 EW    APYZAR WG     COSAYRR 200 SC   GOLTIXR TOP 0
#
# ⚠️ E o mesmo ficheiro usa as DUAS convenções: dez nomes mantêm o ® verdadeiro
# (`Folpan® Energy`, `Diode®`) e nove trazem a letra colada. Meio arrumado é
# pior do que nada arrumado, porque `NIMRODR` lê-se como nome legítimo.
#
# O conserto existia — em `italia-portale/audit/product-identity.mjs`, que
# chama à falha o que ela é: *«un'assenza FABBRICATA — il registro li contiene,
# con un'altra ortografia»*. Mas vivia na CAMADA DE APRESENTAÇÃO. Quem lesse os
# dados sem passar pelo site apanhava o defeito inteiro.
#
#     CORRIGIR IDENTIDADE NÃO É TRABALHO DE QUEM DESENHA A TELA.
#
# Aqui a regra passa a viver na referência. O nome observado **não se apaga**:
# fica em `OBSERVED_NAMES` com a razão da transformação ao lado, para que a
# mudança seja auditável e reversível.
_SUFIXO_R = re.compile(r"^(?P<marca>[A-Za-zÀ-ÿ]{4,})R(?P<resto>\s.*|)$")


def _sem_acento(s):
    return "".join(c for c in unicodedata.normalize("NFD", s)
                   if unicodedata.category(c) != "Mn")


def chave(nome):
    """A chave de comparação de nomes. NÃO é identidade — é como se procura."""
    return re.sub(r"[^A-Z0-9]", "", _sem_acento(str(nome or "")).upper())


def canonizar_nome(observado, nomes_do_registo):
    """`(canônico, razão)`. Só transforma quando a marca existe por si só.

    A trava é essa: `NIMRODR` só vira `NIMROD®` porque `NIMROD` existe no
    registo como nome inteiro. Sem isso, um produto que legitimamente acabe em
    R — e há — seria mutilado.
    """
    bruto = str(observado or "").strip()
    if "®" in bruto:
        return bruto, "NOME_JA_TRAZ_O_SIMBOLO"
    m = _SUFIXO_R.match(bruto)
    if not m:
        return bruto, "SEM_TRANSFORMACAO"
    marca = m.group("marca")
    if chave(marca) not in nomes_do_registo:
        # NÃO se transforma: o R pode ser do nome. `STOPPER P` e `TRIMMER 50 WG`
        # caem por aqui, e caem bem.
        return bruto, "SUFIXO_R_SEM_MARCA_CORRESPONDENTE_NO_REGISTO"
    return ("%s®%s" % (marca, m.group("resto")),
            "SIMBOLO_REGISTADO_LIDO_COMO_LETRA_R · a marca «%s» existe sozinha "
            "no registo do Ministero" % marca)


def _selo(product_id, primeira_ancora):
    """Assina o par ID↔âncora no momento da emissão. Ver a nota na alocação."""
    import hashlib
    return hashlib.sha256(("%s|%s" % (product_id, primeira_ancora))
                          .encode("utf-8")).hexdigest()[:16]


def _e_r_corrompido(observado, canonico):
    """`APYZAR WG` contra `APYZA® WG` → True. Compara SEM o R e sem o símbolo.

    ⚠️ E tolera o ZERO PENDURADO. `GOLTIX® TOP` chega do V2.1 como
    `GOLTIXR TOP 0`: são dois defeitos na mesma linha — o símbolo virou letra
    **e** apareceu um zero que o registo não tem. Comparar só o R deixava este
    de fora, e ele é um dos quinze que o Portal já tinha nomeado.
    """
    m = _SUFIXO_R.match(str(observado or ""))
    if not m:
        return False
    limpo = chave(m.group("marca") + m.group("resto")).rstrip("0")
    return limpo == chave(canonico).rstrip("0")


def _nome_no_v21(canonico, observado, vcom):
    """O nome com que o V2.1 chama este produto, se for diferente do canônico.

    Procura por três chaves porque é exactamente aí que o defeito vive: a chave
    ingénua (`trim` e maiúsculas) é a que deixou quinze produtos órfãos.
    """
    for k in (chave(canonico), chave(observado)):
        x = vcom.get(k)
        if x is not None:
            nome = str(x.get("NAME") or "").strip()
            return nome if chave(nome) != chave(canonico) else None
    # a chave ingénua falhou: procura-se a grafia com o R colado
    alvo = chave(canonico)
    for k, x in vcom.items():
        nome = str(x.get("NAME") or "").strip()
        if _e_r_corrompido(nome, canonico) or chave(nome).rstrip("0") == alvo:
            return nome
    return None


def _proveniencia(source_ids, urls, artefacto, snapshot):
    return {
        "SOURCE_IDS": [SOURCE_ID_CANONICO.get(s, s) for s in (source_ids or [])],
        "SOURCE_IDS_LEGACY": [s for s in (source_ids or [])
                              if s in SOURCE_ID_CANONICO and SOURCE_ID_CANONICO[s] != s],
        "SOURCE_URLS": list(urls or [])[:3],
        "PROVING_ARTIFACT": artefacto,
        "SNAPSHOT_ID": snapshot,
    }


# ── SNAPSHOTS · NENHUM VIRA LIXO ──────────────────────────────────────────
# Três fotografias do mesmo registo. A mais nova NÃO apaga as outras: uma
# afirmação feita em 02/09 foi feita contra a foto de 24/08, e continua a ser
# verdade sobre ELA. Reescrever o passado com a foto de hoje é a forma mais
# silenciosa de mentir sobre o que se sabia.
SNAPSHOTS = [
    {"SNAPSHOT_ID": "PROD_FTS_6_20260824", "OBSERVED_AT": "2026-08-24",
     "SOURCE_ID": "IT-T4-001", "AUTHORITY": "Ministero della Salute",
     "CURRENT": False, "REGISTRATIONS_ADAMA": 163,
     "PROVING_ARTIFACT": "build/SINTONIA-ITALY-REALITY-HANDOFF-V2.1.zip",
     "WHY_KEPT": "os 2030 usos autorizados foram lidos contra ESTA foto. "
                 "Descartá-la tornaria os 2030 pares afirmacoes sem data."},
    {"SNAPSHOT_ID": "PROD_FTS_6_20260831", "OBSERVED_AT": "2026-08-31",
     "SOURCE_ID": "IT-T4-001", "AUTHORITY": "Ministero della Salute",
     "CURRENT": True, "REGISTRATIONS_ADAMA": 602,
     "PROVING_ARTIFACT": "research/adama-italy-product-intelligence-deep/PRODUCTS-REGULATORY.json",
     "WHY_CURRENT": "populacao regulatoria maior (602 > 163) e posterior; e o "
                    "bruto de 07/09 confirma-a linha a linha, 602 de 602."},
    {"SNAPSHOT_ID": "PROD_FTS_6_20260907", "OBSERVED_AT": "2026-09-07",
     "SOURCE_ID": "IT-T4-001", "AUTHORITY": "Ministero della Salute",
     "CURRENT": False, "REGISTRATIONS_ADAMA": 602,
     "PROVING_ARTIFACT": "data/samples/IT-SOURCE-SAMPLES/IT-T4-001/PROD_FTS_6_20260907.csv",
     "STATE": "RAW_PRESENT_NOT_DERIVED",
     "WHY_NOT_CURRENT": "e o bruto integral (17695 linhas), ainda nao derivado "
                        "para esta casa. Usado aqui so para CONFERIR a foto de "
                        "31/08: 602 de 602, zero entradas e zero saidas. "
                        "Deriva-lo e missao propria, nao esta."},
]
SNAPSHOT_ATUAL = "PROD_FTS_6_20260831"


def carregar_master():
    """O registo append-only. Ausente = primeira emissão."""
    caminho = os.path.join(CASA, "PRODUCT-MASTER.json")
    if not os.path.isfile(caminho):
        return {"DATASET": "ADAMA-PRODUCT-MASTER", "PRODUCTS": [], "NEXT_SERIAL": 1}
    return _ler(caminho)


def montar(escrever=True):
    dim = deep("PRODUCT-IDENTITY-MAP.json")["PRODUCTS"]
    dcom = {p.get("PRODUCT_NAME"): p for p in deep("PRODUCTS-COMMERCIAL.json")["PRODUCTS"]}
    dreg = deep("PRODUCTS-REGULATORY.json")["PRODUCTS"]
    dlab = deep("LABEL-MANIFEST.json")["DOCUMENTS"]
    drec = {r["PRODUCT_ID"]: r for r in deep("COMMERCIAL-REGULATORY-RECONCILIATION.json")["ROWS"]}
    dai = deep("ACTIVE-INGREDIENTS.json")["ACTIVE_INGREDIENTS"]
    vusos = v21("PRODUCT-RELATIONSHIPS.json")["RECORDS"]
    vpai = v21("PRODUCT-ACTIVE-INGREDIENTS.json")["RECORDS"]
    vcom = {chave(x["NAME"]): x for x in v21("PRODUCTS-COMMERCIAL.json")["RECORDS"]}

    nomes_registo = {chave(r.get("PRODUCT")) for r in dreg}

    # ── PRODUCT MASTER ────────────────────────────────────────────────────
    # Só o que o catálogo comercial mostra vira PRODUTO. As outras 560
    # autorizações são REGISTOS — a §16 da missão e a lei do próprio V2.1
    # (`CATALOG_PRODUCT != REGULATORY_PRODUCT`) proíbem promovê-las.
    master = carregar_master()
    por_ancora = {}
    for p in master["PRODUCTS"]:
        for a in p["IDENTITY_ANCHORS"]:
            por_ancora[a] = p
    serial = master.get("NEXT_SERIAL", 1)
    vivos = []

    catalogo = [p for p in dim if p.get("COMMERCIAL_CATALOG_PRESENT")]
    for p in sorted(catalogo, key=lambda x: x["PRODUCT_ID"]):
        obs = p.get("COMMERCIAL_NAME") or p.get("REGULATORY_NAME") or ""
        canon, razao = canonizar_nome(obs, nomes_registo)
        com = dcom.get(obs, {})
        url = com.get("CANONICAL_URL") or com.get("PRODUCT_URL") or ""
        # A âncora é como se reconhece, e o endereço é a mais estável que há
        # aqui: dois produtos podem partilhar registo (017995 partilha), e o
        # nome já se provou corrompível.
        ancoras = sorted({a for a in ("URL:" + url if url else "",
                                      "LEGACY:" + p["PRODUCT_ID"]) if a})
        ja = next((por_ancora[a] for a in ancoras if a in por_ancora), None)
        if ja is None:
            pid = "ADAMA-P-%04d" % serial
            serial += 1
            # ⚠️ O SELO, E ELE NASCEU DE UM ATAQUE QUE SOBREVIVEU.
            #
            # O red team rodou os IDs entre os produtos — a âncora `X` passou a
            # trazer o ID de `Y`. A prova de estabilidade não apanhou: ela
            # regenerava A PARTIR DO PRÓPRIO FICHEIRO, portanto lia a rotação e
            # reproduzia-a, e as duas metades batiam certo.
            #
            #     REGENERAR A PARTIR DE SI MESMO PROVA QUE O CONSTRUTOR REPETE.
            #     NÃO PROVA QUE A IDENTIDADE ESTÁ PRESA A ALGUMA COISA.
            #
            # O selo é a testemunha que faltava: assina, no momento da emissão,
            # o par ID↔primeira âncora. Trocar o ID sem trocar a âncora deixa de
            # fechar, e a fraude passa a ter de reescrever também o selo — que
            # é o que um adversário distraído não faz.
            ja = {"ADAMA_PRODUCT_ID": pid, "IDENTITY_ANCHORS": [],
                  "IDENTITY_SEAL": _selo(pid, ancoras[0]),
                  "IDENTITY_SEAL_LAW": "sha256(ADAMA_PRODUCT_ID|primeira ancora), "
                                       "assinado na emissao e nunca reescrito.",
                  "OBSERVED_NAMES": [], "FIRST_SEEN_SNAPSHOT": SNAPSHOT_ATUAL}
            master["PRODUCTS"].append(ja)
            for a in ancoras:
                por_ancora[a] = ja
        for a in ancoras:
            if a not in ja["IDENTITY_ANCHORS"]:
                ja["IDENTITY_ANCHORS"].append(a)
            por_ancora[a] = ja
        for n in ([obs] + list(p.get("ALIASES") or [])):
            reg = {"OBSERVED_NAME": n, "SEEN_IN": "IT-ADAMA-CATALOG",
                   "NAME_STATE": "OK"}
            if reg not in ja["OBSERVED_NAMES"]:
                ja["OBSERVED_NAMES"].append(reg)
        # ⚠️ A GRAFIA CORROMPIDA TAMBÉM É UM NOME OBSERVADO, E PRECISA DE MORADA.
        # O defeito do ® não está no pacote DEEP — está no V2.1, que é quem o
        # Portal serve. Se a referência só guardasse a grafia certa, quem
        # chegasse com `APYZAR WG` na mão continuaria sem encontrar o produto,
        # e a «assenza fabbricata» mudava de sítio em vez de acabar.
        #
        #     APAGAR O NOME ERRADO NÃO CONSERTA QUEM O TEM NA MÃO.
        vn = _nome_no_v21(canon, obs, vcom)
        if vn is not None:
            estado = ("SIMBOLO_REGISTADO_LIDO_COMO_LETRA_R"
                      if _e_r_corrompido(vn, canon) else "VARIANTE_DE_GRAFIA")
            reg = {"OBSERVED_NAME": vn, "SEEN_IN": "V2.1 DESIGN-INGEST",
                   "NAME_STATE": estado,
                   "MAPS_TO_CANONICAL": canon,
                   "WHY": ("o catalogo publicou o simbolo ® como a letra R. A "
                           "marca «%s» existe sozinha no registo do Ministero, "
                           "e e isso que autoriza a leitura."
                           % _SUFIXO_R.match(vn).group("marca")
                           if estado.startswith("SIMBOLO") else
                           "a mesma entidade escrita de outra maneira (ponto, "
                           "espaco duplo, zero pendurado ou simbolo ausente)")}
            if reg not in ja["OBSERVED_NAMES"]:
                ja["OBSERVED_NAMES"].append(reg)
        ja.update({
            "CANONICAL_NAME": canon,
            "CANONICAL_NAME_RULE": razao,
            "COUNTRY_SCOPE": ["IT"],
            "COUNTRY_SCOPE_LAW": "presenca provada no pais. NAO afirma que um "
                                 "produto de outro pais e o mesmo produto.",
            "CATEGORY": p.get("CATEGORY_PRINTED_ON_PAGE") or NAO_SEI,
            "CATEGORY_SOURCE": p.get("CATEGORY_SOURCE") or NAO_SEI,
            "IDENTITY_STATUS": "CATALOG_OBSERVED",
            "PROVENANCE": _proveniencia(p.get("SOURCE_IDS"), [url],
                                        "research/adama-italy-product-intelligence-deep/"
                                        "PRODUCT-IDENTITY-MAP.json", SNAPSHOT_ATUAL),
            "_legacy": p["PRODUCT_ID"], "_obs": obs,
            "_reg": (p.get("REGISTRATION_NUMBER") or "").strip(),
        })
        vivos.append(ja)
    master["NEXT_SERIAL"] = serial
    master["SCHEMA"] = "sintonia.adama-reference.product-master/1"
    master["LAW"] = (
        "APPEND-ONLY. Um ADAMA_PRODUCT_ID emitido NUNCA muda, NUNCA se recicla e "
        "NUNCA se renumera — nem quando o produto sai do catalogo. Ele e o "
        "SINTONIA_STABLE_ID da COL-LAW-206 aplicado ao produto. NAO deriva de "
        "numero de registo, de nome, de posicao de linha, de snapshot nem de pais.")
    master["COUNT"] = len(master["PRODUCTS"])

    por_legacy = {p["_legacy"]: p for p in vivos}

    # ── REGISTRATIONS ─────────────────────────────────────────────────────
    # 602 autorizações. Cada uma é entidade própria; o produto entra só quando
    # provado. `MULTIPLE` quando duas ofertas de catálogo partilham a mesma
    # autorização — foi medido, e é real: 017995.
    reg_para_prod = defaultdict(list)
    for p in vivos:
        if p["_reg"]:
            reg_para_prod[p["_reg"]].append(p["ADAMA_PRODUCT_ID"])
    registos = []
    for r in dreg:
        num = str(r.get("NUM_REGISTRAZIONE") or "").strip()
        ligados = sorted(reg_para_prod.get(num, []))
        registos.append({
            "REGISTRATION_NUMBER": num,
            "COUNTRY": "IT",
            "AUTHORITY": "Ministero della Salute",
            "REGISTERED_NAME": r.get("PRODUCT"),
            "HOLDER": r.get("AUTHORIZATION_HOLDER") or _holder(num, dim) or NAO_SEI,
            "ADMIN_STATUS": r.get("REGULATORY_ADMIN_STATE") or NAO_SEI,
            "ADMIN_ACTIVE": r.get("ADMIN_ACTIVE"),
            "FORMAL_VALIDITY": r.get("FORMAL_VALIDITY_STATE") or UNKNOWN,
            "CURRENTLY_MARKETABLE": r.get("CURRENTLY_MARKETABLE_STATE") or UNKNOWN,
            # ⚠️ AS DUAS DATAS SEPARADAS, E ESTA É A CORREÇÃO DE UM DEFEITO REAL.
            # No V2.1 `REFERENCE_DATE == EXPIRY` em 163 de 163 registos, com
            # valores até 2040-10-31. Um campo chamado «data de referência» que
            # guarda o futuro faz quem o leia concluir que o dado está fresco
            # por mais catorze anos.
            "OBSERVED_AT": _observado(SNAPSHOT_ATUAL),
            "EXPIRY_DATE": r.get("AUTHORIZATION_EXPIRY_DATE") or NAO_SEI,
            "ADAMA_PRODUCT_ID": (ligados[0] if len(ligados) == 1
                                 else ("MULTIPLE" if ligados else UNKNOWN)),
            "ADAMA_PRODUCT_IDS": ligados,
            "PROVENANCE": _proveniencia(["IT-T4-001"], [], FONTES_REL["DEEP_REG"], SNAPSHOT_ATUAL),
        })

    # ── LABEL DOCUMENTS ───────────────────────────────────────────────────
    documentos = []
    for d in dlab:
        p = por_legacy.get(d.get("PRODUCT_ID"))
        documentos.append({
            "DOCUMENT_ID": "ADAMA-DOC-%s" % d.get("SHA256", "")[:12],
            "DOCUMENT_TYPE": d.get("DOCUMENT_TYPE") or NAO_SEI,
            "REGISTRATION_NUMBER": (d.get("REGISTRATION_NUMBER") or "").strip() or UNKNOWN,
            "ADAMA_PRODUCT_ID": p["ADAMA_PRODUCT_ID"] if p else UNKNOWN,
            "OBSERVED_NAME": d.get("PRODUCT_NAME"),
            "LABEL_DATE": d.get("LABEL_DATE") or NAO_SEI,
            "LABEL_DATE_STATE": d.get("LABEL_DATE_STATE") or UNKNOWN,
            "SHA256": d.get("SHA256"),
            "BYTES": d.get("BYTES"),
            "CAPTURED_AT": d.get("CAPTURED_AT"),
            "SOURCE_URL": d.get("SOURCE_URL"),
            "PROVENANCE": _proveniencia([d.get("SOURCE_ID")], [d.get("SOURCE_URL")],
                                        FONTES_REL["DEEP_LAB"], "IT-ADAMA-CATALOG-20260830"),
        })

    # ── AUTHORIZED USES ───────────────────────────────────────────────────
    # Os 2030 pares NÃO são reconstruídos nem recolhidos. São lidos e ganham
    # a identidade que lhes faltava: eles sabiam de que PAPEL vinham, nunca de
    # que PRODUTO.
    por_num = {r["REGISTRATION_NUMBER"]: r for r in registos}
    doc_por_reg = defaultdict(list)
    for d in documentos:
        if d["DOCUMENT_TYPE"] == "ETICHETTA" and d["REGISTRATION_NUMBER"] != UNKNOWN:
            doc_por_reg[d["REGISTRATION_NUMBER"]].append(d["DOCUMENT_ID"])
    usos = []
    for u in vusos:
        num = str(u.get("REGISTRATION_NUMBER") or "").strip()
        r = por_num.get(num)
        pid = r["ADAMA_PRODUCT_ID"] if r else UNKNOWN
        usos.append({
            "USE_ID": u.get("ID"),
            "REGISTRATION_NUMBER": num or UNKNOWN,
            "ADAMA_PRODUCT_ID": pid if pid in ("MULTIPLE", UNKNOWN) or pid.startswith("ADAMA-P-") else UNKNOWN,
            "OBSERVED_PRODUCT_NAME": u.get("PRODUCT_NAME"),
            "CROP_ON_LABEL": u.get("CROP_ON_LABEL"),
            # O alvo guarda-se nas DUAS formas. `TARGET_ON_LABEL` é o valor
            # mapeado e diz `NAO_MAPEADO` quando o vocabulário da casa não
            # cobre o que o rótulo escreveu; `TARGET_AS_WRITTEN` é o que está
            # no papel. Ficar só com o mapeado apagaria 375 alvos reais.
            "TARGET_ON_LABEL": u.get("TARGET_ON_LABEL") or NAO_SEI,
            "TARGET_AS_WRITTEN": u.get("TARGET_AS_WRITTEN") or NAO_SEI,
            "TARGET_KIND": u.get("TARGET_KIND") or NAO_SEI,
            "SOURCE_DOCUMENT_IDS": doc_por_reg.get(num, []),
            "SOURCE_SNAPSHOT": "PROD_FTS_6_20260824",
            "PROVENANCE": _proveniencia(u.get("SOURCE_IDS"), u.get("SOURCE_URLS"),
                                        FONTES_REL["V21_USOS"], "PROD_FTS_6_20260824"),
            "WHAT_IT_DOES_NOT_PROVE": "o par diz que o rotulo autoriza o uso. NAO diz "
                                      "dose, NAO diz que o produto esta a venda hoje.",
        })

    # ── ACTIVE INGREDIENTS ────────────────────────────────────────────────
    # Entidade própria, nunca texto dentro do produto. A camada europeia
    # (Reg. 540/2011) é transversal EAME e não se torna italiana aqui.
    ingredientes = [{
        "ACTIVE_INGREDIENT_ID": a.get("ACTIVE_INGREDIENT_ID"),
        "NAME": a.get("NAME"), "NORMALIZED_NAME": a.get("NORMALIZED_NAME"),
        "HRAC": a.get("HRAC") or NAO_SEI, "FRAC": a.get("FRAC") or NAO_SEI,
        "CHEMICAL_FAMILY": a.get("CHEMICAL_FAMILY") or NAO_SEI,
        "IT_REGISTRATION_COUNT": len(a.get("REGISTRATION_NUMBERS") or []),
        "EU_LAYER": "Reg. (UE) 540/2011 — transversal EAME, nao italiana",
        "PROVENANCE": _proveniencia(["IT-T4-001"], [], FONTES_REL["DEEP_AI"], SNAPSHOT_ATUAL),
    } for a in dai]
    relacoes = []
    for x in vpai:
        num = str(x.get("REGISTRATION_NUMBER") or "").strip()
        r = por_num.get(num)
        relacoes.append({
            "RELATION_ID": x.get("ID"),
            "REGISTRATION_NUMBER": num or UNKNOWN,
            "ADAMA_PRODUCT_ID": r["ADAMA_PRODUCT_ID"] if r else UNKNOWN,
            "ACTIVE_INGREDIENT_ID": x.get("ACTIVE_INGREDIENT_ID"),
            "ACTIVE_INGREDIENT": x.get("ACTIVE_INGREDIENT"),
            "IS_MIXTURE_COMPONENT": x.get("IS_MIXTURE_COMPONENT"),
            "COMPONENTS_IN_PRODUCT": x.get("COMPONENTS_IN_PRODUCT"),
            "PROVENANCE": _proveniencia(x.get("SOURCE_IDS"), x.get("SOURCE_URLS"),
                                        FONTES_REL["V21_PAI"], "PROD_FTS_6_20260824"),
            "WHAT_IT_DOES_NOT_PROVE": x.get("WHAT_IT_DOES_NOT_PROVE"),
        })

    # ── DOSES ─────────────────────────────────────────────────────────────
    # Dose, unidade, intervalo e nº máximo de aplicações, lidos do PDF do
    # rótulo por geometria. Auditados antes de entrar:
    #
    #   · cada linha traz `SOURCE_QUOTE`, `SOURCE_PAGE` e `SOURCE_Y` — o sítio
    #     exacto no papel, não «está no rótulo»;
    #   · `DOSE_RULE_CHECK` confere a dose/ha contra os fios da tabela:
    #     647 conferidas, 647 OK, 0 contraditas;
    #   · `*_INHERITED` diz quando o valor veio da linha de cima;
    #   · os 142 rótulos sem linha ENTRAM na mesma — com `PARSE_STATE`.
    #
    #     PARSER_FAILURE != REGULATORY_ABSENCE.
    #
    # ⚠️ O cabeçalho do ficheiro de origem declara `LABELS_WITH_ROWS 23` e
    # `TOTAL_DOSE_ROWS 848`. Contados, são **21** e **839**: a diferença são as
    # duas tabelas que o próprio filtro de plausibilidade descartou (`P-01`) e
    # que o cabeçalho não acompanhou. Aqui vale o que está nos dados; o número
    # declarado fica escrito ao lado, para que a diferença não se perca.
    doses = []
    dz = _ler(FONTES["DOSES"])
    for lab in dz["LABELS"]:
        num = str(lab.get("REGISTRATION_ID") or "").strip()
        r = por_num.get(num)
        pid = r["ADAMA_PRODUCT_ID"] if r else UNKNOWN
        doses.append({
            "REGISTRATION_NUMBER": num or UNKNOWN,
            "ADAMA_PRODUCT_ID": pid,
            "OBSERVED_PRODUCT_NAME": lab.get("PRODUCT"),
            "SOURCE_DOCUMENT_IDS": doc_por_reg.get(num, []),
            "PARSE_STATE": lab.get("PARSE_STATE"),
            "ROW_COUNT": len(lab.get("ROWS") or []),
            "ROWS": lab.get("ROWS") or [],
            "PROVENANCE": _proveniencia(["IT-T4-001"], [],
                                        "data/samples/IT-DOSE-ROTULO/IT-DOSES-2026-09-06.json",
                                        "IT-ETICHETTA-20260906"),
        })

    # ── PORTFOLIO ─────────────────────────────────────────────────────────
    portfolio = []
    for p in vivos:
        com = dcom.get(p["_obs"], {})
        v = vcom.get(chave(p["_obs"])) or vcom.get(chave(p["CANONICAL_NAME"])) or {}
        rec = drec.get(p["_legacy"], {})
        portfolio.append({
            "ADAMA_PRODUCT_ID": p["ADAMA_PRODUCT_ID"],
            "CANONICAL_NAME": p["CANONICAL_NAME"],
            "OBSERVED_NAME": p["_obs"],
            "CATEGORY": p["CATEGORY"],
            "CATALOG_URL": com.get("CANONICAL_URL") or com.get("PRODUCT_URL") or NAO_SEI,
            "ACTIVE_INGREDIENT_TEXT": com.get("ACTIVE_INGREDIENT") or NAO_SEI,
            "FORMULATION": com.get("FORMULATION") or NAO_SEI,
            "REGISTRATION_NUMBER": p["_reg"] or UNKNOWN,
            "REGISTRATION_LINK_METHOD": rec.get("JOIN_METHOD") or UNKNOWN,
            "REGISTRATION_LINK_CONFIDENCE": rec.get("JOIN_CONFIDENCE") or "NONE",
            "REGISTRATION_LINK_WHY_UNKNOWN": rec.get("WHY_UNKNOWN") or "",
            "NOT_A_PLANT_PROTECTION_PRODUCT": v.get("NOT_A_PLANT_PROTECTION_PRODUCT"),
            "IS_SYSTEM_NOT_PRODUCT": v.get("IS_SYSTEM_NOT_PRODUCT"),
            "PAGE_SHA256": com.get("SHA256") or NAO_SEI,
            "PROVENANCE": p["PROVENANCE"],
        })

    for p in vivos:
        for k in ("_legacy", "_obs", "_reg"):
            p.pop(k, None)

    saida = {
        "PRODUCT-MASTER.json": master,
        "SNAPSHOTS.json": _env("ADAMA-SNAPSHOTS", SNAPSHOTS,
                               "Nenhuma foto vira lixo. A actual e a de %s." % SNAPSHOT_ATUAL),
        "PORTFOLIO.json": _env("ADAMA-PORTFOLIO", portfolio,
                               "O que o catalogo publico da ADAMA Italia mostra. "
                               "CATALOG_PRODUCT != REGULATORY_PRODUCT."),
        "REGISTRATIONS.json": _env("ADAMA-REGISTRATIONS", registos,
                                   "Autorizacoes do Ministero em nome de entidades ADAMA. "
                                   "As 5 entidades legais NAO se fundem."),
        "LABEL-DOCUMENTS.json": _env("ADAMA-LABEL-DOCUMENTS", documentos,
                                     "Documentos oficiais com sha256 e data de captura."),
        "AUTHORIZED-USES.json": _env("ADAMA-AUTHORIZED-USES", usos,
                                     "Pares cultura x alvo lidos do rotulo. Nao recolhidos "
                                     "aqui: lidos do V2.1 e ligados ao produto."),
        "DOSES.json": _env("ADAMA-DOSES", doses,
                           "Dose lida do rotulo oficial, com citacao e pagina. Os 142 "
                           "rotulos sem tabela lida ficam na lista com PARSE_STATE: "
                           "PARSER_FAILURE != REGULATORY_ABSENCE. O ficheiro de origem "
                           "declara 23 rotulos e 848 linhas; contados sao 21 e 839 — a "
                           "diferenca sao as 2 tabelas que o filtro P-01 descartou."),
        "ACTIVE-INGREDIENTS.json": _env("ADAMA-ACTIVE-INGREDIENTS", ingredientes,
                                        "Substancia activa e ENTIDADE, nunca texto no produto."),
        "PRODUCT-ACTIVE-INGREDIENTS.json": _env("ADAMA-PRODUCT-ACTIVE-INGREDIENTS", relacoes,
                                                "Uma relacao por componente."),
        "SOURCE-ID-MAP.json": _env("ADAMA-SOURCE-ID-MAP", [
            {"LEGACY_SOURCE_ID": k, "CANONICAL_SOURCE_ID": v,
             "SAME_SOURCE_PROOF": SAME_SOURCE_PROOF[v]}
            for k, v in sorted(SOURCE_ID_CANONICO.items()) if k != v],
            "O identificador antigo NAO se apaga: fica ligado ao canonico. "
            "LEGADO != CANONICO: nenhum CANONICAL_SOURCE_ID deste mapa pode ser um "
            "identificador que o Atlas nao tem como ficha."),
    }
    if escrever:
        os.makedirs(CASA, exist_ok=True)
        for nome, obj in saida.items():
            with io.open(os.path.join(CASA, nome), "w", encoding="utf-8") as fh:
                json.dump(obj, fh, ensure_ascii=False, indent=1, sort_keys=False)
                fh.write("\n")
    return saida


FONTES_REL = {
    "DEEP_REG": "research/adama-italy-product-intelligence-deep/PRODUCTS-REGULATORY.json",
    "DEEP_LAB": "research/adama-italy-product-intelligence-deep/LABEL-MANIFEST.json",
    "DEEP_AI": "research/adama-italy-product-intelligence-deep/ACTIVE-INGREDIENTS.json",
    "V21_USOS": "build/SINTONIA-ITALY-REALITY-HANDOFF-V2.1.zip → DESIGN-INGEST/PRODUCT-RELATIONSHIPS.json",
    "V21_PAI": "build/SINTONIA-ITALY-REALITY-HANDOFF-V2.1.zip → DESIGN-INGEST/PRODUCT-ACTIVE-INGREDIENTS.json",
}


def _observado(snapshot_id):
    for s in SNAPSHOTS:
        if s["SNAPSHOT_ID"] == snapshot_id:
            return s["OBSERVED_AT"]
    return NAO_SEI


def _holder(num, dim):
    for p in dim:
        if str(p.get("REGISTRATION_NUMBER") or "").strip() == num:
            return p.get("AUTHORIZATION_HOLDER")
    return None


def _env(dataset, registos, lei):
    return {"DATASET": dataset,
            "SCHEMA": "sintonia.adama-reference/1",
            "OWNER": "IT — ADAMA REFERENCE (referencia/adama/)",
            "BUILDER": "fontes/adama_referencia.py",
            "LAW": lei,
            "CURRENT_SNAPSHOT": SNAPSHOT_ATUAL,
            "COUNT": len(registos),
            "RECORDS": registos}


def main():
    ap = argparse.ArgumentParser(description="Monta a referencia canonica da ADAMA.")
    ap.add_argument("--censo", action="store_true", help="mede e nao escreve")
    a = ap.parse_args()
    sys.stdout.reconfigure(encoding="utf-8")
    s = montar(escrever=not a.censo)
    print("ADAMA REFERENCE %s" % ("(censo, nada escrito)" if a.censo else "-> referencia/adama/"))
    for nome, obj in s.items():
        print("  %-34s %d" % (nome, obj.get("COUNT", len(obj.get("RECORDS", [])))))
    lig = Counter(r["ADAMA_PRODUCT_ID"] == UNKNOWN for r in s["AUTHORIZED-USES.json"]["RECORDS"])
    print("  usos com produto provado          %d de %d"
          % (lig[False], sum(lig.values())))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
