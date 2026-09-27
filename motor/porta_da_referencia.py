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


def main(argv=None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    hoje = date.fromisoformat(argv[argv.index("--hoje") + 1]) if "--hoje" in argv else None
    c = carimbo(abrir(hoje=hoje))
    c.pop("SHA256", None)
    print(json.dumps(c, ensure_ascii=False, indent=1))
    return 0 if c["ESTADO"] == "LIDA" else 1


if __name__ == "__main__":
    sys.exit(main())
