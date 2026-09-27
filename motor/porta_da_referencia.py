#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""A PORTA UNICA DA REFERENCIA ADAMA — bulas e portfolio, UMA edicao, lida por UMA porta.

    MISSAO   PORTA-UNICA-REFERENCIA (D116 do dono: bulas e portfolio sao a BIBLIOTECA DE
             REFERENCIA unica e versionada; toda capacidade que fala de produto consulta a
             MESMA edicao; proibido duplicar a tabela-mestra. D116/D117 nao estao escritas
             no repo; a fonte fica dita aqui e em PORTA-UNICA-REFERENCIA.md)
    DONO     da referencia: fontes/adama_referencia.py (o CONSTRUTOR, que escreve).
             Esta porta so LE. Nao copia a tabela, nao cunha id, nao escreve nada.

    python3 motor/porta_da_referencia.py [--hoje AAAA-MM-DD]     # o carimbo da edicao
    python3 -m unittest tests.test_porta_unica_referencia -v

O QUE A PORTA DEVOLVE
---------------------
    REGISTRO   a autorizacao do Ministero (IT-T4-001): REGISTRATIONS, AUTHORIZED-USES,
               LABEL-READINGS, PRODUCT-ACTIVE-INGREDIENTS, ACTIVE-INGREDIENTS, DOSES,
               LABEL-DOCUMENTS, SNAPSHOTS — com EDICAO (o SNAPSHOT_ID), DATA_DA_EDICAO,
               ULTIMA_CHECAGEM_OK, ESTADO_FRESCOR e o sha256 de cada livro.
    CATALOGO   o que a ADAMA Italia mostra a venda (IT-T9-008): PRODUCT-MASTER, PORTFOLIO,
               PORTFOLIO-OBSERVATIONS, CATALOG-SNAPSHOTS — com a SUA edicao e o SEU frescor.

    CATALOGO NAO E AUTORIZACAO. Estar na vitrine nao prova que a bula autoriza o uso;
    estar autorizado nao prova que esta a venda. As duas metades nunca se somam aqui.

O FRESCOR (D117 do dono)
------------------------
Conta-se da ULTIMA CHECAGEM QUE DEU CERTO (`SNAPSHOTS.LAST_CHECK_OK`, medida pelo construtor
contra o bruto do Ministero), nunca da data do ficheiro:

    < 14 dias   FRESCA
    >= 14       PODE_ESTAR_DESATUALIZADO   (a resposta sai, com o aviso ao lado)
    >= 30       AUTORIZACAO_A_CONFIRMAR    (nenhuma autorizacao sai como afirmada)

`hoje` e declarado por quem pergunta. Se nao for, a porta usa o relogio e ESCREVE que usou
(`HOJE_VEIO_DE = RELOGIO_DO_SISTEMA`): relogio escondido nao existe aqui.

EDICAO MISTURADA
----------------
Todo livro do REGISTRO declara `CURRENT_SNAPSHOT`, e todos tem de dizer o MESMO, que tem de
ser o SNAPSHOT corrente de SNAPSHOTS.json. Um so diferente e a referencia sai NAO SEI inteira:
responder com meia edicao de um dia e meia de outro daria uma autorizacao que nunca existiu.

AUSENCIA E AUSENCIA NA NOSSA LEITURA
------------------------------------
Bula nao lida (LABEL-READINGS.LABEL_WAS_READ = false, ou registo sem leitura) nunca vira «nao
autoriza»: vira A_CONFIRMAR. Cultura ou alvo que a bula nao escreve nesta forma vira NAO SEI.
A frase «a ADAMA nao tem produto» nao sai desta porta.
"""
from __future__ import annotations

import functools
import hashlib
import json
import sys
import unicodedata
from datetime import date
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
#: A casa. E o UNICO sitio do motor/, leis/ e coleta/ que a nomeia
#: (tests/test_porta_unica_referencia.py varre e reprova quem a abrir por fora).
CASA = RAIZ / "referencia" / "adama"
PORTA = "motor/porta_da_referencia.py"
CONSTRUTOR = "fontes/adama_referencia.py"
CONTRATO = "PORTA_DA_REFERENCIA_ADAMA/v1"
NAO_SEI = "NAO SEI"

LIVROS_DO_REGISTRO = ("SNAPSHOTS", "REGISTRATIONS", "AUTHORIZED-USES", "LABEL-READINGS",
                      "PRODUCT-ACTIVE-INGREDIENTS", "ACTIVE-INGREDIENTS", "DOSES",
                      "LABEL-DOCUMENTS")
LIVROS_DO_CATALOGO = ("CATALOG-SNAPSHOTS", "PRODUCT-MASTER", "PORTFOLIO",
                      "PORTFOLIO-OBSERVATIONS")

# ── D117 ────────────────────────────────────────────────────────────────────
DIAS_PODE_ESTAR_DESATUALIZADO = 14
DIAS_AUTORIZACAO_A_CONFIRMAR = 30
FRESCA = "FRESCA"
PODE_ESTAR_DESATUALIZADO = "PODE_ESTAR_DESATUALIZADO"
AUTORIZACAO_A_CONFIRMAR = "AUTORIZACAO_A_CONFIRMAR"

# ── o que a porta responde sobre um uso ─────────────────────────────────────
AUTORIZADO_NA_BULA_LIDA = "AUTORIZADO_NA_BULA_LIDA"
A_CONFIRMAR = "A_CONFIRMAR"
REGISTRADO_COM_A_SUBSTANCIA = "REGISTRADO_COM_A_SUBSTANCIA"


class ReferenciaIlegivel(Exception):
    """A porta nao abriu. O consumidor recebe NAO SEI — nunca «a ADAMA nao tem»."""


# ═══════════════════════════════════════════════════════════════════════════
# ABRIR
# ═══════════════════════════════════════════════════════════════════════════
def _sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def _ler(pasta: Path, nome: str) -> tuple:
    p = pasta / (nome + ".json")
    return json.loads(p.read_text(encoding="utf-8")), _sha(p)


def _dias(d0: str, hoje: date):
    try:
        return (hoje - date.fromisoformat(str(d0)[:10])).days
    except ValueError:
        return None


def estado_frescor(dias) -> str:
    """D117. Sem data de checagem nao ha frescor provado: a autorizacao fica A CONFIRMAR."""
    if not isinstance(dias, int):
        return AUTORIZACAO_A_CONFIRMAR
    if dias >= DIAS_AUTORIZACAO_A_CONFIRMAR:
        return AUTORIZACAO_A_CONFIRMAR
    if dias >= DIAS_PODE_ESTAR_DESATUALIZADO:
        return PODE_ESTAR_DESATUALIZADO
    return FRESCA


def _impressao(shas: dict) -> str:
    return hashlib.sha256("|".join("%s=%s" % kv for kv in sorted(shas.items())).encode()).hexdigest()


def abrir(pasta: Path | str | None = None, hoje: date | None = None) -> dict:
    """A referencia inteira, com as duas edicoes e os dois frescores. Nunca levanta.

    Falha de leitura ou edicao misturada -> {"ESTADO": "NAO SEI", "PORQUE": ...}.
    """
    pasta = Path(pasta) if pasta is not None else CASA
    veio = "DECLARADO" if isinstance(hoje, date) else "RELOGIO_DO_SISTEMA"
    hoje = hoje if isinstance(hoje, date) else date.today()
    try:
        reg, reg_sha = {}, {}
        for n in LIVROS_DO_REGISTRO:
            reg[n], reg_sha[n] = _ler(pasta, n)
        cat, cat_sha = {}, {}
        for n in LIVROS_DO_CATALOGO:
            cat[n], cat_sha[n] = _ler(pasta, n)
    except (OSError, ValueError) as erro:
        return {"ESTADO": NAO_SEI, "PORQUE": "referencia ilegivel: %r" % erro,
                "PORTA": PORTA, "HOJE": hoje.isoformat(), "HOJE_VEIO_DE": veio}

    # ── a edicao do REGISTRO: uma so ────────────────────────────────────────
    snaps = reg["SNAPSHOTS"]
    correntes = [r["SNAPSHOT_ID"] for r in snaps.get("RECORDS", []) if r.get("CURRENT") is True]
    edicoes = {n: reg[n].get("CURRENT_SNAPSHOT") for n in LIVROS_DO_REGISTRO}
    if len(correntes) != 1 or len(set(edicoes.values())) != 1 or correntes[0] not in edicoes.values():
        return {"ESTADO": NAO_SEI, "PORTA": PORTA, "HOJE": hoje.isoformat(), "HOJE_VEIO_DE": veio,
                "PORQUE": "EDICAO_MISTURADA: correntes em SNAPSHOTS=%s; livros=%s"
                          % (correntes, edicoes)}
    edicao = correntes[0]
    foto = next(r for r in snaps["RECORDS"] if r["SNAPSHOT_ID"] == edicao)
    checagem = snaps.get("LAST_CHECK_OK")
    dias = _dias(checagem, hoje) if checagem else None

    # ── a edicao do CATALOGO: a dele, nunca a do registo ────────────────────
    csnap = cat["CATALOG-SNAPSHOTS"]
    ccorr = [r for r in csnap.get("RECORDS", []) if r.get("CURRENT") is True]
    if len(ccorr) != 1 or ccorr[0]["SNAPSHOT_ID"] != csnap.get("CURRENT_SNAPSHOT") \
            or cat["PORTFOLIO-OBSERVATIONS"].get("CURRENT_SNAPSHOT") != csnap.get("CURRENT_SNAPSHOT"):
        return {"ESTADO": NAO_SEI, "PORTA": PORTA, "HOJE": hoje.isoformat(), "HOJE_VEIO_DE": veio,
                "PORQUE": "EDICAO_MISTURADA no catalogo: CATALOG-SNAPSHOTS=%s, OBSERVATIONS=%s"
                          % (csnap.get("CURRENT_SNAPSHOT"),
                             cat["PORTFOLIO-OBSERVATIONS"].get("CURRENT_SNAPSHOT"))}
    cdias = _dias(ccorr[0].get("OBSERVED_AT"), hoje)

    try:
        rel = str(pasta.resolve().relative_to(RAIZ))
    except ValueError:
        rel = str(pasta)
    registro = {
        "PAPEL": "AUTORIZACAO (Ministero della Salute, IT-T4-001)",
        "EDICAO": edicao,
        "DATA_DA_EDICAO": foto.get("OBSERVED_AT", NAO_SEI),
        "ULTIMA_CHECAGEM_OK": checagem or NAO_SEI,
        "DIAS_SEM_CHECAGEM": dias if dias is not None else NAO_SEI,
        "ESTADO_FRESCOR": estado_frescor(dias),
        "SHA256": reg_sha,
        "LIVROS": {n: reg[n].get("RECORDS", []) for n in LIVROS_DO_REGISTRO},
    }
    catalogo = {
        "PAPEL": "CATALOGO COMERCIAL (ADAMA Italia, IT-T9-008) — NAO E AUTORIZACAO",
        "EDICAO": ccorr[0]["SNAPSHOT_ID"],
        "DATA_DA_EDICAO": ccorr[0].get("OBSERVED_AT", NAO_SEI),
        "ULTIMA_CHECAGEM_OK": ccorr[0].get("OBSERVED_AT", NAO_SEI),
        "DIAS_SEM_CHECAGEM": cdias if cdias is not None else NAO_SEI,
        "ESTADO_FRESCOR": estado_frescor(cdias),
        "SHA256": cat_sha,
        "LIVROS": {"PRODUCT-MASTER": cat["PRODUCT-MASTER"].get("PRODUCTS", []),
                   **{n: cat[n].get("RECORDS", []) for n in LIVROS_DO_CATALOGO
                      if n != "PRODUCT-MASTER"}},
    }
    ref = {"ESTADO": "LIDA", "CONTRATO": CONTRATO, "PORTA": PORTA, "CONSTRUTOR": CONSTRUTOR,
           "PASTA": rel, "HOJE": hoje.isoformat(), "HOJE_VEIO_DE": veio,
           "REGISTRO": registro, "CATALOGO": catalogo}
    ref["CARIMBO"] = carimbo(ref)
    return ref


def lida(ref) -> bool:
    """So conta como lida a referencia que PASSOU pela porta (tem as duas metades)."""
    return (isinstance(ref, dict) and ref.get("ESTADO") == "LIDA"
            and isinstance(ref.get("REGISTRO"), dict) and isinstance(ref.get("CATALOGO"), dict))


def carimbo(ref: dict) -> dict:
    """O que cada consumidor ESCREVE no resultado: que edicao usou, e quao fresca estava."""
    if not lida(ref):
        return {"PORTA": PORTA, "ESTADO": NAO_SEI,
                "PORQUE": ((ref or {}).get("PORQUE") or "a referencia nao passou pela porta")
                if isinstance(ref, dict) else NAO_SEI,
                "EDICAO_REGISTRO": NAO_SEI, "EDICAO_CATALOGO": NAO_SEI}
    r, c = ref["REGISTRO"], ref["CATALOGO"]
    return {"PORTA": PORTA, "ESTADO": "LIDA", "HOJE": ref["HOJE"], "HOJE_VEIO_DE": ref["HOJE_VEIO_DE"],
            "EDICAO_REGISTRO": r["EDICAO"], "DATA_DA_EDICAO_REGISTRO": r["DATA_DA_EDICAO"],
            "ULTIMA_CHECAGEM_OK": r["ULTIMA_CHECAGEM_OK"], "DIAS_SEM_CHECAGEM": r["DIAS_SEM_CHECAGEM"],
            "ESTADO_FRESCOR": r["ESTADO_FRESCOR"],
            "EDICAO_CATALOGO": c["EDICAO"], "DATA_DA_EDICAO_CATALOGO": c["DATA_DA_EDICAO"],
            "ESTADO_FRESCOR_CATALOGO": c["ESTADO_FRESCOR"],
            "IMPRESSAO_DOS_LIVROS": _impressao({**r["SHA256"], **c["SHA256"]}),
            "SHA256": {**r["SHA256"], **c["SHA256"]}}


def exigir(ref: dict) -> dict:
    """Para quem nao pode seguir sem a referencia: levanta com o motivo."""
    if not lida(ref):
        raise ReferenciaIlegivel((ref or {}).get("PORQUE", NAO_SEI) if isinstance(ref, dict) else NAO_SEI)
    return ref


def livro(ref: dict, nome: str) -> list:
    """Um livro pelo nome. O do REGISTRO e o do CATALOGO vivem em metades separadas."""
    exigir(ref)
    if nome in LIVROS_DO_REGISTRO:
        return ref["REGISTRO"]["LIVROS"][nome]
    if nome in LIVROS_DO_CATALOGO:
        return ref["CATALOGO"]["LIVROS"][nome]
    raise KeyError(nome)


# ═══════════════════════════════════════════════════════════════════════════
# PERGUNTAS — so do REGISTRO. O catalogo nunca responde «autorizado».
# ═══════════════════════════════════════════════════════════════════════════
def dobrar(s) -> str:
    """Maiusculas, sem acento, espacos e hifens como `_`: VITE, ERBA_MEDICA, MAIS_DOLCE."""
    t = "".join(c for c in unicodedata.normalize("NFKD", str(s or ""))
                if not unicodedata.combining(c)).upper().strip()
    return "_".join(t.replace("-", " ").split())


def _ativos(ref: dict) -> dict:
    return {r["REGISTRATION_NUMBER"]: r for r in livro(ref, "REGISTRATIONS")
            if r.get("ADMIN_ACTIVE") is True}


def _leituras(ref: dict) -> dict:
    return {r["REGISTRATION_NUMBER"]: r for r in livro(ref, "LABEL-READINGS")}


def _estado_do_uso(ref: dict) -> tuple:
    """Uso lido numa bula de registo ativo: afirmado, salvo se o frescor o proibe (D117)."""
    if ref["REGISTRO"]["ESTADO_FRESCOR"] == AUTORIZACAO_A_CONFIRMAR:
        return A_CONFIRMAR, ("a edicao %s nao e conferida ha %s dias (>= %d, D117): "
                             "a autorizacao fica a confirmar"
                             % (ref["REGISTRO"]["EDICAO"], ref["REGISTRO"]["DIAS_SEM_CHECAGEM"],
                                DIAS_AUTORIZACAO_A_CONFIRMAR))
    return AUTORIZADO_NA_BULA_LIDA, None


def _aviso(ref: dict):
    r = ref["REGISTRO"]
    if r["ESTADO_FRESCOR"] == FRESCA:
        return None
    return ("%s: ultima checagem da edicao %s em %s (%s dias)"
            % (r["ESTADO_FRESCOR"], r["EDICAO"], r["ULTIMA_CHECAGEM_OK"], r["DIAS_SEM_CHECAGEM"]))


def autorizados(ref: dict, cultura, alvo=None) -> dict:
    """Que produto ADAMA tem esta cultura (x alvo) NA BULA, com registo ativo nesta edicao.

    -> {ESTADO, EDICAO..., PRODUTOS: [...], A_CONFIRMAR: [...], PORQUE}
       ESTADO: AUTORIZADO_NA_BULA_LIDA | A_CONFIRMAR | NAO SEI
       PRODUTOS    os usos lidos (cada um com USE_ID, nivel de ligacao e estado)
       A_CONFIRMAR as bulas de registo ativo que NAO foram lidas (contagem + numeros): podem
                   autorizar, nao sabemos
    """
    base = {"PERGUNTA": {"CULTURA": cultura, "ALVO": alvo}, "CARIMBO": carimbo(ref)}
    if not lida(ref):
        return dict(base, ESTADO=NAO_SEI, PRODUTOS=[], A_CONFIRMAR={},
                    PORQUE="referencia nao lida pela porta: %s" % carimbo(ref)["PORQUE"])
    usos = livro(ref, "AUTHORIZED-USES")
    culturas = {u["CROP_ON_LABEL"] for u in usos}
    alvos = {u["TARGET_ON_LABEL"] for u in usos}
    c, a = dobrar(cultura), (dobrar(alvo) if alvo is not None else None)
    if c not in culturas:
        return dict(base, ESTADO=NAO_SEI, PRODUTOS=[], A_CONFIRMAR={},
                    PORQUE="a cultura %r nao esta escrita nesta forma em nenhuma bula lida "
                           "(vocabulario das bulas: %d culturas). NAO quer dizer que nao ha "
                           "produto." % (cultura, len(culturas)))
    if a is not None and a not in alvos:
        return dict(base, ESTADO=NAO_SEI, PRODUTOS=[], A_CONFIRMAR={},
                    PORQUE="o alvo %r nao esta escrito nesta forma em nenhuma bula lida. NAO "
                           "quer dizer que nao ha produto." % (alvo,))
    ativos, leituras = _ativos(ref), _leituras(ref)
    estado_uso, porque_uso = _estado_do_uso(ref)
    produtos = []
    for u in usos:
        if u["CROP_ON_LABEL"] != c or (a is not None and u["TARGET_ON_LABEL"] != a):
            continue
        if u["REGISTRATION_NUMBER"] not in ativos:
            continue
        produtos.append({"USE_ID": u["USE_ID"], "REGISTRATION_NUMBER": u["REGISTRATION_NUMBER"],
                         "ADAMA_PRODUCT_ID": u["ADAMA_PRODUCT_ID"],
                         "NOME_NA_BULA": u["OBSERVED_PRODUCT_NAME"],
                         "CULTURA": u["CROP_ON_LABEL"], "ALVO": u["TARGET_ON_LABEL"],
                         "LINK_LEVEL": u.get("LINK_LEVEL", NAO_SEI),
                         "ESTADO": estado_uso, "USOS_LIDOS_CONTRA": u.get("SOURCE_SNAPSHOT", NAO_SEI)})
    # As bulas ativas que ninguem leu: podem cobrir o par. A_CONFIRMAR, nunca «nao».
    nao_lidas = sorted(n for n in ativos
                       if not (leituras.get(n) or {}).get("LABEL_WAS_READ"))
    a_confirmar = {"N_BULAS_ATIVAS_NAO_LIDAS": len(nao_lidas), "REGISTRATION_NUMBERS": nao_lidas,
                   "ESTADO": A_CONFIRMAR,
                   "PORQUE": "registo ativo nesta edicao cuja bula nao foi lida (ou foi lida sem "
                             "tabela): pode autorizar o par, nao sabemos. Nunca «nao autoriza»."}
    if produtos:
        estado = estado_uso
    else:
        estado = A_CONFIRMAR if nao_lidas else NAO_SEI
    return dict(base, ESTADO=estado, PRODUTOS=produtos, A_CONFIRMAR=a_confirmar,
                AVISO_DE_FRESCOR=_aviso(ref),
                PORQUE=porque_uso or ("nenhum uso lido casa; %d bulas ativas nao lidas ficam a "
                                      "confirmar — ausencia NA NOSSA LEITURA" % len(nao_lidas)
                                      if not produtos else None),
                NAO_PROVA="a bula autoriza o uso. NAO diz que o produto esta a venda hoje, "
                          "nem dose, nem que foi recomendado.")


def ativos_conhecidos(ref: dict) -> list:
    """Os nomes das substancias da referencia — o unico vocabulario de substancia da porta."""
    return sorted({a["NAME"] for a in livro(ref, "ACTIVE-INGREDIENTS")})


def por_substancia(ref: dict, substancia) -> dict:
    """Registo ADAMA ativo com esta substancia. So substancia: cultura e alvo NAO entram.

    Serve a concorrencia: o cadastro nao da cultura, e o concorrente so se compara por
    substancia. Substancia que a referencia conhece mas nao liga a registo -> A_CONFIRMAR.
    """
    base = {"PERGUNTA": {"SUBSTANCIA": substancia}, "CARIMBO": carimbo(ref)}
    if not lida(ref):
        return dict(base, ESTADO=NAO_SEI, REGISTOS=[],
                    PORQUE="referencia nao lida pela porta: %s" % carimbo(ref)["PORQUE"])
    k = dobrar(substancia).replace("_", "")
    conhecidas = {dobrar(a).replace("_", "") for a in ativos_conhecidos(ref)}
    ativos = _ativos(ref)
    regs = sorted({p["REGISTRATION_NUMBER"] for p in livro(ref, "PRODUCT-ACTIVE-INGREDIENTS")
                   if dobrar(p["ACTIVE_INGREDIENT"]).replace("_", "") == k})
    if not regs:
        return dict(base, ESTADO=(A_CONFIRMAR if k in conhecidas else NAO_SEI), REGISTOS=[],
                    PORQUE=("a referencia conhece a substancia mas nao a liga a registo "
                            "(PRODUCT-ACTIVE-INGREDIENTS cobre 163 registos): a confirmar"
                            if k in conhecidas else
                            "a substancia nao esta entre os ativos da referencia"))
    estado_uso, porque = _estado_do_uso(ref)
    registos = [{"REGISTRATION_NUMBER": n, "NOME_REGISTADO": ativos[n].get("REGISTERED_NAME"),
                 "HOLDER": ativos[n].get("HOLDER"), "ADAMA_PRODUCT_IDS": ativos[n].get("ADAMA_PRODUCT_IDS", []),
                 "ESTADO": REGISTRADO_COM_A_SUBSTANCIA if estado_uso != A_CONFIRMAR else A_CONFIRMAR}
                for n in regs if n in ativos]
    return dict(base, ESTADO=(registos[0]["ESTADO"] if registos else NAO_SEI), REGISTOS=registos,
                AVISO_DE_FRESCOR=_aviso(ref),
                PORQUE=porque if registos else "os registos com a substancia nao estao ativos nesta edicao",
                GRAO="SUBSTANCIA — cultura e alvo NAO entram nesta pergunta")


def alvos_conhecidos(ref: dict) -> list:
    """Os alvos como as bulas lidas os escrevem (TARGET_ON_LABEL), sem o NAO_MAPEADO."""
    return sorted({u["TARGET_ON_LABEL"] for u in livro(ref, "AUTHORIZED-USES")} - {"NAO_MAPEADO", NAO_SEI})


def por_alvo(ref: dict, alvo) -> dict:
    """Registo ADAMA ativo cuja bula lida nomeia este alvo — em QUALQUER cultura.

    Para quem nao tem cultura (um anuncio de concorrente): a resposta diz que culturas a bula
    liga ao alvo, e nao afirma nenhuma cultura do anuncio.
    """
    base = {"PERGUNTA": {"ALVO": alvo}, "CARIMBO": carimbo(ref)}
    if not lida(ref):
        return dict(base, ESTADO=NAO_SEI, REGISTOS=[],
                    PORQUE="referencia nao lida pela porta: %s" % carimbo(ref)["PORQUE"])
    a = dobrar(alvo)
    if a not in alvos_conhecidos(ref):
        return dict(base, ESTADO=NAO_SEI, REGISTOS=[],
                    PORQUE="o alvo %r nao esta escrito nesta forma em nenhuma bula lida" % (alvo,))
    ativos = _ativos(ref)
    estado_uso, porque = _estado_do_uso(ref)
    por = {}
    for u in livro(ref, "AUTHORIZED-USES"):
        if u["TARGET_ON_LABEL"] == a and u["REGISTRATION_NUMBER"] in ativos:
            x = por.setdefault(u["REGISTRATION_NUMBER"], {
                "REGISTRATION_NUMBER": u["REGISTRATION_NUMBER"], "NOME_NA_BULA": u["OBSERVED_PRODUCT_NAME"],
                "ADAMA_PRODUCT_ID": u["ADAMA_PRODUCT_ID"], "CULTURAS_NA_BULA": set(), "ESTADO": estado_uso})
            x["CULTURAS_NA_BULA"].add(u["CROP_ON_LABEL"])
    registos = [dict(x, CULTURAS_NA_BULA=sorted(x["CULTURAS_NA_BULA"])) for _, x in sorted(por.items())]
    return dict(base, ESTADO=(estado_uso if registos else A_CONFIRMAR), REGISTOS=registos,
                AVISO_DE_FRESCOR=_aviso(ref),
                PORQUE=porque or (None if registos else "nenhum registo ativo com bula lida nomeia o alvo; "
                                  "bulas nao lidas ficam a confirmar"))


def no_catalogo(ref: dict, adama_product_id) -> dict:
    """O produto esta na vitrine da edicao corrente do catalogo? NAO responde autorizacao."""
    exigir(ref)
    ed = ref["CATALOGO"]["EDICAO"]
    obs = [o for o in livro(ref, "PORTFOLIO-OBSERVATIONS")
           if o.get("ADAMA_PRODUCT_ID") == adama_product_id and o.get("SNAPSHOT_ID") == ed]
    return {"ADAMA_PRODUCT_ID": adama_product_id, "EDICAO_CATALOGO": ed,
            "MEMBERSHIP_STATE": obs[0]["MEMBERSHIP_STATE"] if obs else NAO_SEI,
            "NAO_E": "autorizacao de uso: essa so vem do REGISTRO"}


# ═══════════════════════════════════════════════════════════════════════════
# LIGACAO_ADAMA — D123 do dono (27/09): «todo fato do sintonia tem que estar
# linkado a bula e ao portfolio senao nada faz sentido». D123 nao esta escrita no
# repositorio; a fonte fica dita aqui e em LIGACAO-ADAMA.md.
#
# UMA funcao, AQUI, na porta. Nenhum consumidor calcula a ligacao: cada um chama
# `ligacao_adama(ref, chaves)` e anexa o resultado ao objeto que emite. O pote
# confere o SELO com `conferir_ligacao` e recusa objeto sem ligacao, ou com uma
# ligacao que nao saiu daqui (tests/test_ligacao_adama.py varre os consumidores).
# ═══════════════════════════════════════════════════════════════════════════
if str(Path(__file__).resolve().parent) not in sys.path:
    sys.path.insert(0, str(Path(__file__).resolve().parent))
import v21_normalizar as _VOCAB   # noqa: E402 — o dono do vocabulario CROP_*/ISSUE_* (chamado, nao copiado)

CONTRATO_LIGACAO = "LIGACAO_ADAMA/v1"
AUTORIZADO_BULA_LIDA = "AUTORIZADO_BULA_LIDA"
SO_CULTURA = "SO_CULTURA"
ADAMA_SEM_PRODUTO = "ADAMA_SEM_PRODUTO"
NAO_SEI_LIGACAO = "NAO_SEI"
ESTADOS_DA_LIGACAO = (AUTORIZADO_BULA_LIDA, A_CONFIRMAR, SO_CULTURA, ADAMA_SEM_PRODUTO, NAO_SEI_LIGACAO)
FALTAS = ("CULTURA", "PROBLEMA", "SUBSTANCIA", "REFERENCIA")
#: So estes dois niveis dizem que cultura E alvo estao na MESMA linha/bloco da bula.
NIVEIS_QUE_AUTORIZAM = ("LINHA_DA_TABELA", "BLOCO_DA_CULTURA")
DECLARACAO_DE_PRODUTO = "DECLARACAO_DE_PRODUTO"
#: As chaves que a porta aceita. Nao ha campo de TEXTO: a porta nao extrai nada de
#: prosa — as chaves vem da Collection (ou do objeto que a Intelligence ja fechou),
#: cada uma com o VEM_DE dito.
CHAVES_DA_LIGACAO = ("CULTURA", "PROBLEMA", "SUBSTANCIA")
#: As fontes da propria referencia. A ligacao contextualiza; nunca e uma fonte a mais.
FONTES_DA_REFERENCIA = ("IT-T4-001", "IT-T9-008")
TRAVAS_DA_LIGACAO = {
    "NAO_PROVA": ["PRESSAO_DE_CAMPO", "DEMANDA"],
    "NAO_PROVA_LEI": "INT-LAW-145: autorizacao/portfolio/label contextualizam; nao criam sinal de campo/demanda",
    "CONTA_COMO_FONTE_INDEPENDENTE": False,
    "FONTE_INDEPENDENTE_LEI": "INT-LAW-076: catalogo, label e registro validam estrutura; nao sao sinais independentes",
    "CATALOGO_E_AUTORIZACAO": False,
    "CATALOGO_LEI": "D116: a vitrine (CATALOGO) nunca responde autorizacao; so o REGISTRO (bula lida)",
}


class ChaveInvalida(ValueError):
    """A ligacao recebeu o que nao e chave (texto livre, chave sem procedencia...)."""


def _vazio(v) -> bool:
    return v is None or (isinstance(v, str) and (not v.strip() or dobrar(v) in ("NAO_SEI", "UNKNOWN", "NONE")))


def _lista(v) -> list:
    if _vazio(v):
        return []
    vs = v if isinstance(v, (list, tuple)) else [v]
    return sorted({str(x) for x in vs if not _vazio(x)})


@functools.lru_cache(maxsize=None)
def _id_do_vocabulario(valor: str, eixo: str):
    """O id do dono (v21_normalizar) para um valor: ja e id, ou um apelido declarado.
    (Memorizado: funcao pura do valor; o vocabulario e do dono e nao muda durante a corrida.)"""
    tabela, funcao = ((_VOCAB.CROP_ALIAS, _VOCAB.crop_id) if eixo == "CULTURA"
                      else (_VOCAB.ISSUE_ALIAS, _VOCAB.issue_id))
    d = dobrar(valor)
    if d in tabela:
        return d
    return funcao(str(valor).replace("_", " "))


def _casa(valor_do_fato, valor_da_bula, eixo) -> str | None:
    """Como a palavra do fato casa com a da bula: EXATO, pelo vocabulario do dono, ou nao casa."""
    if dobrar(valor_do_fato) == dobrar(valor_da_bula):
        return "EXATO"
    a = _id_do_vocabulario(str(valor_do_fato), eixo)
    if a and a == _id_do_vocabulario(str(valor_da_bula), eixo):
        return "VOCABULARIO:" + a
    return None


def _casa_cultura(f, b):
    return _casa(f, b, "CULTURA")


def _casa_problema(f, b):
    return _casa(f, b, "PROBLEMA")


def _selo_da_ligacao(lig: dict) -> str:
    corpo = {k: v for k, v in lig.items() if k != "SELO"}
    return hashlib.sha256((PORTA + "|" + json.dumps(corpo, ensure_ascii=False, sort_keys=True,
                                                    default=str)).encode()).hexdigest()


def _selar_ligacao(lig: dict) -> dict:
    lig["SELO"] = _selo_da_ligacao(lig)
    return lig


def _bula(ref: dict, reg: str, uso: dict | None = None) -> dict:
    """A bula de um registo: DOCUMENT_ID quando a referencia o tem; nunca cunhado."""
    docs = sorted({d for d in ((uso or {}).get("SOURCE_DOCUMENT_IDS") or [])})
    if not docs:
        docs = sorted(d["DOCUMENT_ID"] for d in livro(ref, "LABEL-DOCUMENTS")
                      if d.get("REGISTRATION_NUMBER") == reg and d.get("DOCUMENT_TYPE") == "ETICHETTA")
    urls = sorted({u for u in (((uso or {}).get("PROVENANCE") or {}).get("SOURCE_URLS") or [])})
    if not urls:
        urls = sorted({d.get("SOURCE_URL") for d in livro(ref, "LABEL-DOCUMENTS")
                       if d.get("REGISTRATION_NUMBER") == reg and d.get("DOCUMENT_TYPE") == "ETICHETTA"
                       and d.get("SOURCE_URL")})
    return {"DOCUMENT_ID": docs[0] if docs else NAO_SEI, "URL": urls[0] if urls else NAO_SEI}


def _a_ler(ref, reg, porque, leituras, ativos, empresa="ADAMA") -> dict:
    lr = leituras.get(reg) or {}
    return {"EMPRESA": empresa, "REGISTRO": reg,
            "PRODUTO": (ativos.get(reg) or {}).get("REGISTERED_NAME", NAO_SEI),
            "BULA": _bula(ref, reg), "ESTADO_DA_LEITURA": lr.get("READING_STATE", NAO_SEI),
            "PORQUE": porque}


def _chaves_da_pergunta(chaves) -> tuple:
    if not isinstance(chaves, dict):
        raise ChaveInvalida("chaves tem de ser um objeto {CULTURA, PROBLEMA, SUBSTANCIA, VEM_DE}")
    estranhas = sorted(set(chaves) - set(CHAVES_DA_LIGACAO) - {"VEM_DE"})
    if estranhas:
        raise ChaveInvalida("a porta nao le %s: so chaves %s (nunca texto; D123: as chaves vem da "
                            "Collection)" % (estranhas, list(CHAVES_DA_LIGACAO)))
    vem = chaves.get("VEM_DE") if isinstance(chaves.get("VEM_DE"), dict) else {}
    pergunta, sem_procedencia = {}, []
    for k in CHAVES_DA_LIGACAO:
        vals = _lista(chaves.get(k))
        if vals and _vazio(vem.get(k)):
            sem_procedencia.append(k)      # valor sem VEM_DE nao conta: nao se sabe de onde veio
            vals = []
        pergunta[k] = vals
    return pergunta, {k: (vem.get(k) if pergunta[k] else NAO_SEI) for k in CHAVES_DA_LIGACAO}, sem_procedencia


def ligacao_adama(ref, chaves) -> dict:
    """D123. A ligacao de UM fato a bula e ao portfolio ADAMA, calculada SO aqui.

    chaves = {"CULTURA": ..., "PROBLEMA": ..., "SUBSTANCIA": str|list, "VEM_DE": {chave: origem}}
    Valores ausentes ou NAO SEI ficam ausentes; valor sem VEM_DE nao conta.

    -> LIGACAO_ADAMA/v1 {ESTADO, FALTA, PERGUNTA, CARIMBO, PRODUTOS_ADAMA,
       CONCORRENTES_MESMA_SUBSTANCIA, BULAS_A_LER, travas, SELO}
       ESTADO  AUTORIZADO_BULA_LIDA  cultura E alvo na mesma linha/bloco de uma bula lida
               A_CONFIRMAR           bula nao lida, so DECLARACAO_DE_PRODUTO, ou D117 >= 30 dias
               SO_CULTURA            fato sem problema: produtos cuja bula lida nomeia a cultura
               ADAMA_SEM_PRODUTO     a porta LEU (todas as bulas ativas do grao, ou a composicao
                                     de todos os registos ativos) e nao ha produto: lacuna de portfolio
               NAO_SEI               FALTA = CULTURA | PROBLEMA | SUBSTANCIA | REFERENCIA
    """
    pergunta, vem_de, sem_proc = _chaves_da_pergunta(chaves)
    lig = {"CONTRATO": CONTRATO_LIGACAO, "CALCULADA_POR": PORTA,
           "PERGUNTA": pergunta, "VEM_DE": vem_de,
           "CHAVES_SEM_PROCEDENCIA_IGNORADAS": sem_proc,
           "CARIMBO": {k: v for k, v in carimbo(ref).items() if k != "SHA256"} if isinstance(ref, dict)
           else carimbo(None),
           "ESTADO": NAO_SEI_LIGACAO, "FALTA": [], "PORQUE": None,
           "PRODUTOS_ADAMA": [], "CONCORRENTES_MESMA_SUBSTANCIA": [],
           "CONCORRENTES_ESTADO": NAO_SEI, "BULAS_A_LER": [], "PROVA_DA_LEITURA": {},
           **{k: (list(v) if isinstance(v, list) else v) for k, v in TRAVAS_DA_LIGACAO.items()}}
    if not lida(ref):
        lig.update(FALTA=["REFERENCIA"], PORQUE="a referencia nao passou pela porta: %s"
                   % lig["CARIMBO"].get("PORQUE", NAO_SEI))
        return _selar_ligacao(lig)
    C, P, S = pergunta["CULTURA"], pergunta["PROBLEMA"], pergunta["SUBSTANCIA"]
    ativos, leituras = _ativos(ref), _leituras(ref)
    usos = [u for u in livro(ref, "AUTHORIZED-USES") if u["REGISTRATION_NUMBER"] in ativos]
    lig["CONCORRENTES_ESTADO"] = NAO_SEI
    lig["CONCORRENTES_PORQUE"] = ("sem substancia no fato nao ha concorrente por substancia" if not S else
                                  "a edicao %s so traz registos ADAMA; o cadastro das outras empresas "
                                  "nao esta na referencia (lacuna 3 de PORTA-UNICA-REFERENCIA.md)"
                                  % ref["REGISTRO"]["EDICAO"])

    # ── o grao da substancia: que registos ativos a contem ────────────────────
    regs = set(ativos)
    if S:
        conhecidas = {dobrar(a).replace("_", "") for a in ativos_conhecidos(ref)}
        ks = {s: dobrar(s).replace("_", "") for s in S}
        fora = sorted(s for s, k in ks.items() if k not in conhecidas)
        pai = livro(ref, "PRODUCT-ACTIVE-INGREDIENTS")
        cobertos = {p["REGISTRATION_NUMBER"] for p in pai} & set(ativos)
        lig["PROVA_DA_LEITURA"] = {"REGISTOS_ATIVOS": len(ativos), "COM_COMPOSICAO_LIDA": len(cobertos),
                                   "LIVRO": "PRODUCT-ACTIVE-INGREDIENTS", "EDICAO": ref["REGISTRO"]["EDICAO"]}
        if fora:
            lig.update(FALTA=["SUBSTANCIA"], SUBSTANCIAS_NAO_RECONHECIDAS=fora,
                       PORQUE="substancia fora do vocabulario da referencia (%s): pode ser lacuna ou "
                              "grafia — a porta nao decide" % ", ".join(fora))
            return _selar_ligacao(lig)
        regs = {p["REGISTRATION_NUMBER"] for p in pai
                if dobrar(p["ACTIVE_INGREDIENT"]).replace("_", "") in set(ks.values())} & set(ativos)
        if not regs:
            if cobertos == set(ativos):
                lig.update(ESTADO=ADAMA_SEM_PRODUTO, GRAO="SUBSTANCIA",
                           PORQUE="a composicao de %d/%d registos ativos foi lida e nenhum contem %s: "
                                  "lacuna de portfolio (nao prova falta de demanda nem de pressao)"
                                  % (len(cobertos), len(ativos), ", ".join(S)))
            else:
                lig.update(ESTADO=A_CONFIRMAR, PORQUE="%d registos ativos sem composicao lida"
                           % (len(ativos) - len(cobertos)))
            return _selar_ligacao(lig)

    nao_lidas = sorted(r for r in regs if not (leituras.get(r) or {}).get("LABEL_WAS_READ"))
    estado_uso, porque_d117 = _estado_do_uso(ref)
    # a palavra de D123 (AUTORIZADO_BULA_LIDA); o resto da porta continua a dizer AUTORIZADO_NA_BULA_LIDA
    estado_uso = AUTORIZADO_BULA_LIDA if estado_uso == AUTORIZADO_NA_BULA_LIDA else estado_uso

    def produto(reg, us, estado):
        u0 = us[0] if us else {}
        niveis = sorted({u.get("LINK_LEVEL", NAO_SEI) for u in us})
        return {"PRODUTO": (ativos[reg].get("REGISTERED_NAME") or u0.get("OBSERVED_PRODUCT_NAME", NAO_SEI)),
                "REGISTRO": reg, "ADAMA_PRODUCT_IDS": ativos[reg].get("ADAMA_PRODUCT_IDS", []),
                "BULA": _bula(ref, reg, u0), "BULA_LIDA": bool((leituras.get(reg) or {}).get("LABEL_WAS_READ")),
                "LINK_LEVEL": niveis, "USE_IDS": sorted(u["USE_ID"] for u in us),
                "CASOU_POR": sorted({x for u in us for x in (u.get("_CASOU") or [])}),
                "FONTE_DO_ESTADO": "REGISTRO.AUTHORIZED-USES" if us else "REGISTRO.PRODUCT-ACTIVE-INGREDIENTS",
                "ESTADO": estado}

    def a_ler(porque):
        return [_a_ler(ref, r, porque, leituras, ativos) for r in nao_lidas]

    if not C:
        # sem cultura nao ha pergunta de autorizacao. Com substancia, os registos dela.
        lig.update(FALTA=["CULTURA"] + (["PROBLEMA"] if not P else []) + (["SUBSTANCIA"] if not S else []),
                   PORQUE="o fato nao traz CULTURA com procedencia: nao ha pergunta de autorizacao")
        if S:
            e = A_CONFIRMAR if estado_uso == A_CONFIRMAR else REGISTRADO_COM_A_SUBSTANCIA
            lig["PRODUTOS_ADAMA"] = [produto(r, [], e) for r in sorted(regs)]
            lig["BULAS_A_LER"] = a_ler("registo ADAMA com a substancia e bula nao lida: diz em que "
                                       "culturas a substancia esta autorizada")
        return _selar_ligacao(lig)

    # ── cultura (x problema) nas bulas lidas ──────────────────────────────────
    casados = []
    for u in usos:
        if u["REGISTRATION_NUMBER"] not in regs:
            continue
        mc = next((m for m in (_casa_cultura(c, u["CROP_ON_LABEL"]) for c in C) if m), None)
        if not mc:
            continue
        mp = None
        if P:
            mp = next((m for m in (_casa_problema(p, u["TARGET_ON_LABEL"]) for p in P) if m), None)
            if not mp:
                continue
        casados.append(dict(u, _CASOU=["CULTURA:" + mc] + (["PROBLEMA:" + mp] if mp else [])))
    por_reg = {}
    for u in casados:
        por_reg.setdefault(u["REGISTRATION_NUMBER"], []).append(u)

    if not P:
        if por_reg:
            lig.update(ESTADO=SO_CULTURA, FALTA=["PROBLEMA"],
                       PORQUE="fato sem problema: produtos ADAMA cuja bula lida nomeia a cultura "
                              "(nao diz para que alvo)")
            lig["PRODUTOS_ADAMA"] = [produto(r, us, SO_CULTURA) for r, us in sorted(por_reg.items())]
            lig["BULAS_A_LER"] = a_ler("bula ativa nao lida: pode nomear a cultura")
        elif nao_lidas:
            lig.update(ESTADO=A_CONFIRMAR, FALTA=["PROBLEMA"],
                       PORQUE="nenhuma bula lida nomeia a cultura; %d bulas ativas nao lidas" % len(nao_lidas))
            lig["BULAS_A_LER"] = a_ler("bula ativa nao lida: pode nomear a cultura")
        else:
            lig.update(ESTADO=ADAMA_SEM_PRODUTO, GRAO="CULTURA",
                       PORQUE="todas as %d bulas ativas do grao foram lidas e nenhuma nomeia a cultura"
                              % len(regs))
        return _selar_ligacao(lig)

    fortes = {r: [u for u in us if u.get("LINK_LEVEL") in NIVEIS_QUE_AUTORIZAM] for r, us in por_reg.items()}
    fortes = {r: us for r, us in fortes.items() if us and (leituras.get(r) or {}).get("LABEL_WAS_READ")}
    fracos = {r: us for r, us in por_reg.items() if r not in fortes}
    lig["PRODUTOS_ADAMA"] = ([produto(r, us, estado_uso) for r, us in sorted(fortes.items())]
                             + [produto(r, us, A_CONFIRMAR) for r, us in sorted(fracos.items())])
    releitura = [_a_ler(ref, r, "so DECLARACAO_DE_PRODUTO (ou bula nao lida) liga cultura e alvo: ler a "
                        "tabela da bula", leituras, ativos) for r in sorted(fracos) if r not in nao_lidas]
    if fortes and len(C) > 1:
        # o FATO nao liga o problema a uma das culturas: a bula liga, o fato nao — a confirmar
        lig["PRODUTOS_ADAMA"] = [dict(p, ESTADO=A_CONFIRMAR) for p in lig["PRODUTOS_ADAMA"]]
        lig.update(ESTADO=A_CONFIRMAR,
                   PORQUE="o fato traz %d culturas e o problema nao esta ligado a uma delas no fato: a bula "
                          "liga cultura e alvo, o fato nao" % len(C))
        lig["BULAS_A_LER"] = a_ler("bula ativa nao lida: pode autorizar o par") + releitura
    elif fortes:
        lig.update(ESTADO=estado_uso, PORQUE=porque_d117 or "cultura e alvo na mesma linha/bloco de bula lida")
        lig["BULAS_A_LER"] = a_ler("bula ativa nao lida: pode autorizar tambem") + releitura
    elif fracos or nao_lidas:
        lig.update(ESTADO=A_CONFIRMAR,
                   PORQUE=("so DECLARACAO_DE_PRODUTO liga cultura e alvo" if fracos else
                           "nenhuma bula lida liga cultura e alvo; %d bulas ativas nao lidas" % len(nao_lidas)))
        lig["BULAS_A_LER"] = a_ler("bula ativa nao lida: pode autorizar o par") + releitura
    else:
        lig.update(ESTADO=ADAMA_SEM_PRODUTO, GRAO="CULTURA_X_PROBLEMA",
                   PORQUE="todas as %d bulas ativas do grao foram lidas e nenhuma liga cultura e alvo"
                          % len(regs))
    return _selar_ligacao(lig)


def conferir_ligacao(lig) -> list:
    """O que o pote (e qualquer leitor) confere. Lista vazia = a ligacao e da porta e diz a verdade."""
    if not isinstance(lig, dict):
        return ["objeto sem LIGACAO_ADAMA"]
    v = []
    if lig.get("CONTRATO") != CONTRATO_LIGACAO or lig.get("CALCULADA_POR") != PORTA:
        v.append("LIGACAO_ADAMA nao foi calculada pela porta (%s)" % lig.get("CALCULADA_POR"))
    if lig.get("SELO") != _selo_da_ligacao(lig):
        v.append("LIGACAO_ADAMA com SELO que nao bate: calculada ou mexida fora da porta")
    e = lig.get("ESTADO")
    if e not in ESTADOS_DA_LIGACAO:
        v.append("ESTADO da ligacao fora de %s: %r" % (ESTADOS_DA_LIGACAO, e))
    if e == NAO_SEI_LIGACAO and (not lig.get("FALTA") or set(lig["FALTA"]) - set(FALTAS)):
        v.append("NAO_SEI sem FALTA valida")
    for k, val in TRAVAS_DA_LIGACAO.items():
        if lig.get(k) != val:
            v.append("trava %s violada: %r" % (k, lig.get(k)))
    carim = lig.get("CARIMBO") or {}
    if e != NAO_SEI_LIGACAO or lig.get("FALTA") != ["REFERENCIA"]:
        for k in ("EDICAO_REGISTRO", "DATA_DA_EDICAO_REGISTRO", "ULTIMA_CHECAGEM_OK", "ESTADO_FRESCOR",
                  "IMPRESSAO_DOS_LIVROS"):
            if _vazio(carim.get(k)) or carim.get(k) == NAO_SEI:
                v.append("ligacao sem o carimbo da edicao: %s" % k)
    prods = lig.get("PRODUTOS_ADAMA") or []
    for p in prods:
        if p.get("ESTADO") == AUTORIZADO_BULA_LIDA:
            if not p.get("BULA_LIDA"):
                v.append("%s AUTORIZADO sem bula lida" % p.get("REGISTRO"))
            if not set(p.get("LINK_LEVEL") or []) & set(NIVEIS_QUE_AUTORIZAM):
                v.append("%s AUTORIZADO so por %s (DECLARACAO_DE_PRODUTO nao autoriza)"
                         % (p.get("REGISTRO"), p.get("LINK_LEVEL")))
            if p.get("FONTE_DO_ESTADO") != "REGISTRO.AUTHORIZED-USES":
                v.append("%s AUTORIZADO por %s: so o REGISTRO autoriza (catalogo nao)"
                         % (p.get("REGISTRO"), p.get("FONTE_DO_ESTADO")))
            if carim.get("ESTADO_FRESCOR") == AUTORIZACAO_A_CONFIRMAR:
                v.append("%s AUTORIZADO com a edicao >= %d dias sem checagem (D117)"
                         % (p.get("REGISTRO"), DIAS_AUTORIZACAO_A_CONFIRMAR))
    if e == AUTORIZADO_BULA_LIDA:
        if not any(p.get("ESTADO") == AUTORIZADO_BULA_LIDA for p in prods):
            v.append("AUTORIZADO_BULA_LIDA sem nenhum produto autorizado em bula lida")
        if not (lig.get("PERGUNTA") or {}).get("CULTURA") or not (lig.get("PERGUNTA") or {}).get("PROBLEMA"):
            v.append("AUTORIZADO_BULA_LIDA exige cultura E alvo")
    if e == ADAMA_SEM_PRODUTO:
        if carim.get("ESTADO") != "LIDA":
            v.append("ADAMA_SEM_PRODUTO sem a porta ter lido a referencia")
        if prods:
            v.append("ADAMA_SEM_PRODUTO com produtos listados")
        if lig.get("BULAS_A_LER"):
            v.append("ADAMA_SEM_PRODUTO com bulas por ler: a porta nao leu tudo")
        pl = lig.get("PROVA_DA_LEITURA") or {}
        if lig.get("GRAO") == "SUBSTANCIA" and (not pl or pl.get("COM_COMPOSICAO_LIDA") != pl.get("REGISTOS_ATIVOS")):
            v.append("ADAMA_SEM_PRODUTO por substancia sem a composicao de todos os registos ativos lida")
        if lig.get("GRAO") not in ("SUBSTANCIA", "CULTURA", "CULTURA_X_PROBLEMA"):
            v.append("ADAMA_SEM_PRODUTO sem GRAO")
    return v


def e_prova_da_referencia(prova: dict) -> bool:
    """A prova de um fato vem da propria referencia? (INT-LAW-076: isso nao e fonte independente.)"""
    return isinstance(prova, dict) and str(prova.get("SOURCE_ID")) in FONTES_DA_REFERENCIA


def main(argv=None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    hoje = date.fromisoformat(argv[argv.index("--hoje") + 1]) if "--hoje" in argv else None
    c = carimbo(abrir(hoje=hoje))
    c.pop("SHA256", None)
    print(json.dumps(c, ensure_ascii=False, indent=1))
    return 0 if c["ESTADO"] == "LIDA" else 1


if __name__ == "__main__":
    sys.exit(main())
