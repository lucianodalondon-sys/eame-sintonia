#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Valida os contratos ANTES do canario. Nenhum invalido passa daqui.

    UM CONTRATO QUE NAO RESOLVE NAO CHEGA A REDE.

Gastar um pedido HTTP num contrato que nem sequer tem endereco e desperdicar
o unico recurso caro desta operacao — e, pior, trazer de volta um erro de
rede que parece defeito da FONTE quando e defeito do CONTRATO.

    ANTES DE CULPAR A FONTE, PROVAR QUE O LEITOR FUNCIONA.
    Este ficheiro prova que o leitor esta escrito antes de o mandar ler.

Quatro portas, todas deterministas e sem rede:

    CONTRACT_SCHEMA_VALID   tem os campos que o motor exige?
    ROUTE_RESOLVED          da para chegar ao documento?
    IDENTITY_RESOLVED       da para nomear o que se trouxer?
    OUTPUT_RESOLVED         sabe-se o que se espera de volta?
"""
from __future__ import annotations

import json
import re
import sys
import unittest
from pathlib import Path
from urllib.parse import urlparse

RAIZ = Path(__file__).resolve().parents[1]
TABELA = RAIZ / "curadoria" / "italy_contracts_curator.json"

# o motor de rota so conhece estas; inventar uma terceira seria criar um
# segundo motor, e um segundo motor diverge
STRATEGIES = {"HTML_LINK_DISCOVERY", "STATIC_ENDPOINT", "YOUTUBE_CHANNEL_FEED",
              # SOC2: o contrato nomeia uma fase do Scrap; a rota e a do Scrap.
              "SCRAP_FASE"}
OUTPUTS = {"HTML", "PDF", "VIDEO_METADATA"}
ROTAS = {"DISCOVERED_ROUTE", "STATIC_ROUTE", "APPLICATION_ROUTE"}

OBRIGATORIOS = ("SOURCE_ID", "OWNER", "TERRITORY", "BATCH_ID", "OUTPUT_TYPE",
                "CANONICAL_ENTRY_URL", "ACQUISITION", "IDENTITY", "ROUTE_TYPE",
                "FAIL_CLOSED_RULE", "NEGATIVE_CONTROL", "SOURCE_CONTRACT_VERSION",
                "SOURCE_CONTRACT_HASH")


def schema_valid(c: dict) -> tuple[bool, str]:
    falta = [k for k in OBRIGATORIOS if not c.get(k)]
    if falta:
        return False, "campos em falta: %s" % ", ".join(falta)
    if not re.match(r"^IT-T\d+-\d{3}$", c["SOURCE_ID"]):
        return False, "SOURCE_ID fora do formato IT-T<n>-<nnn>: %s" % c["SOURCE_ID"]
    if c["OUTPUT_TYPE"] not in OUTPUTS:
        return False, "OUTPUT_TYPE desconhecido: %s" % c["OUTPUT_TYPE"]
    if c["ROUTE_TYPE"] not in ROTAS:
        return False, "ROUTE_TYPE desconhecido: %s" % c["ROUTE_TYPE"]
    return True, "ok"


def route_resolved(c: dict) -> tuple[bool, str]:
    aq = c.get("ACQUISITION") or {}
    st = aq.get("STRATEGY")
    if st not in STRATEGIES:
        return False, "STRATEGY fora do motor: %s" % st
    if st == "HTML_LINK_DISCOVERY":
        if not aq.get("INDEX_URL"):
            return False, "sem INDEX_URL"
        if not aq.get("LINK_PATTERN"):
            return False, "sem LINK_PATTERN"
        try:
            rx = re.compile(aq["LINK_PATTERN"])
        except re.error as e:
            return False, "LINK_PATTERN nao compila: %s" % e
        # ⚠️ O PADRAO TEM DE RECUSAR A PROPRIA ENTRADA.
        # Se o LINK_PATTERN casar com o INDEX_URL, o coletor «descobre» a
        # pagina de indice e guarda-a como documento — o erro listagem != item,
        # agora com cara de sucesso.
        if rx.match(aq["INDEX_URL"].rstrip("/")):
            return False, "LINK_PATTERN casa com a propria INDEX_URL (listagem viraria item)"
        return True, "descoberta por padrao, entrada excluida"
    if st == "STATIC_ENDPOINT":
        return (bool(aq.get("URL")), "URL fixa" if aq.get("URL") else "sem URL")
    if st == "YOUTUBE_CHANNEL_FEED":
        ch = aq.get("CHANNEL_ID") or ""
        if not re.match(r"^UC[\w-]{20,26}$", ch):
            return False, "CHANNEL_ID invalido: %r" % ch
        if ch not in (aq.get("FEED_URL") or ""):
            return False, "FEED_URL nao aponta para o CHANNEL_ID"
        return True, "feed publico do canal"
    if st == "SCRAP_FASE":
        # A rota nao se valida aqui: le-se no Scrap, que e o dono dela. Se o
        # Scrap deixar de a declarar (ou a matriz deixar de a permitir), o
        # contrato reprova ANTES de chegar a fila — sem rede, sem gasto.
        sys.path.insert(0, str(RAIZ / "curadoria"))
        import rota_do_scrap_youtube as RSY
        return RSY.conferir(aq)
    return False, "estrategia nao coberta"


def identity_resolved(c: dict) -> tuple[bool, str]:
    idt = c.get("IDENTITY") or {}
    if not idt.get("DOCUMENT_ID"):
        return False, "sem DOCUMENT_ID"
    if not idt.get("CAPTURES"):
        return False, "sem CAPTURES"
    # ⚠️ O DOCUMENT_ID TEM DE COMECAR PELO SOURCE_ID.
    # Sem isso, dois documentos de fontes diferentes podem colidir no mesmo
    # identificador — e o RAW deixa de saber de quem e o que guardou.
    if not idt["DOCUMENT_ID"].startswith(c["SOURCE_ID"] + ":"):
        return False, "DOCUMENT_ID nao e prefixado pelo SOURCE_ID"
    # toda captura citada no DOCUMENT_ID tem de existir em CAPTURES
    for ref in re.findall(r"\{([a-z_]+)\.", idt["DOCUMENT_ID"]):
        if ref not in idt["CAPTURES"]:
            return False, "DOCUMENT_ID usa captura inexistente: %s" % ref
    if "FACT_TIME" not in idt:
        return False, "sem declaracao de FACT_TIME"
    return True, "identidade prefixada e capturas coerentes"


def output_resolved(c: dict) -> tuple[bool, str]:
    if not c.get("EXPECTED_FAILURES"):
        return False, "sem EXPECTED_FAILURES"
    if not (c.get("NEGATIVE_CONTROL") or {}).get("esperado"):
        return False, "sem controlo negativo"
    # ⚠️ FALHA TEM DE SER FALHA. Um contrato que trate lista vazia como
    # sucesso regista zero documentos e diz que correu bem.
    txt = " ".join(c["EXPECTED_FAILURES"]) + c["FAIL_CLOSED_RULE"]
    if "FAILED" not in txt:
        return False, "nenhuma falha declarada resulta em FAILED"
    return True, "falhas declaradas e fecham"


PORTAS = (("CONTRACT_SCHEMA_VALID", schema_valid),
          ("ROUTE_RESOLVED", route_resolved),
          ("IDENTITY_RESOLVED", identity_resolved),
          ("OUTPUT_RESOLVED", output_resolved))


def validar(contratos: list[dict]) -> tuple[list, list]:
    ok, mau = [], []
    for c in contratos:
        falhas = []
        for nome, fn in PORTAS:
            passou, porque = fn(c)
            if not passou:
                falhas.append("%s: %s" % (nome, porque))
        (ok if not falhas else mau).append(
            c if not falhas else {"SOURCE_ID": c.get("SOURCE_ID"), "FALHAS": falhas})
    return ok, mau


def main() -> int:
    d = json.loads(TABELA.read_text(encoding="utf-8"))
    ok, mau = validar(d["FONTES"])

    # SOURCE_ID duplicado e erro de identidade, nao de contrato: conferir a parte
    ids = [c["SOURCE_ID"] for c in d["FONTES"]]
    dup = {i for i in ids if ids.count(i) > 1}

    print("contratos            %d" % len(d["FONTES"]))
    print("CONTRACTS_VALID      %d" % len(ok))
    print("CONTRACTS_INVALID    %d" % len(mau))
    print("SOURCE_ID duplicados %d %s" % (len(dup), sorted(dup)[:5] if dup else ""))
    for m in mau[:10]:
        print("  %s -> %s" % (m["SOURCE_ID"], m["FALHAS"][0]))

    (RAIZ / "curadoria" / "CONTRACT-VALIDATION-V1.json").write_text(
        json.dumps({"TOTAL": len(d["FONTES"]), "VALID": len(ok),
                    "INVALID": len(mau), "DUPLICADOS": sorted(dup),
                    "PORTAS": [n for n, _ in PORTAS],
                    "FALHAS": mau}, ensure_ascii=False, indent=1) + "\n",
        encoding="utf-8")
    return 1 if (mau or dup) else 0


# ─────────────────────────────────────────────────────────────────────────
class TesteValidacao(unittest.TestCase):
    """As portas so valem se reprovarem mesmo."""

    def _yt(self, **kw):
        c = {"SOURCE_ID": "IT-T7-999", "OWNER": "x", "TERRITORY": "T7",
             "BATCH_ID": "LOTE-YOUTUBE-FEED", "OUTPUT_TYPE": "VIDEO_METADATA",
             "CANONICAL_ENTRY_URL": "https://youtube.com/@x",
             "ROUTE_TYPE": "APPLICATION_ROUTE",
             "ACQUISITION": {"STRATEGY": "YOUTUBE_CHANNEL_FEED",
                             "CHANNEL_ID": "UCJi1Vrelq8obdmS_UXP3T2g",
                             "FEED_URL": "https://www.youtube.com/feeds/videos.xml"
                                         "?channel_id=UCJi1Vrelq8obdmS_UXP3T2g"},
             "IDENTITY": {"CAPTURES": {"video": {"FROM": "FEED"}},
                          "DOCUMENT_ID": "IT-T7-999:YT:{video.videoId}",
                          "FACT_TIME": "UNKNOWN"},
             "EXPECTED_FAILURES": ["feed vazio = FAILED"],
             "FAIL_CLOSED_RULE": "sem videoId e FAILED",
             "NEGATIVE_CONTROL": {"esperado": "FAILED"},
             "SOURCE_CONTRACT_VERSION": "v1", "SOURCE_CONTRACT_HASH": "abc"}
        c.update(kw)
        return c

    def test_contrato_bom_passa_as_quatro_portas(self):
        for nome, fn in PORTAS:
            passou, porque = fn(self._yt())
            self.assertTrue(passou, "%s reprovou um contrato bom: %s" % (nome, porque))

    def test_channel_id_invalido_reprova(self):
        aq = dict(self._yt()["ACQUISITION"], CHANNEL_ID="youtube.com")
        self.assertFalse(route_resolved(self._yt(ACQUISITION=aq))[0])

    def test_document_id_sem_prefixo_reprova(self):
        # ⚠️ sem prefixo, duas fontes colidem no mesmo DOCUMENT_ID
        idt = dict(self._yt()["IDENTITY"], DOCUMENT_ID="YT:{video.videoId}")
        self.assertFalse(identity_resolved(self._yt(IDENTITY=idt))[0])

    def test_document_id_com_captura_inexistente_reprova(self):
        idt = dict(self._yt()["IDENTITY"], DOCUMENT_ID="IT-T7-999:YT:{fantasma.id}")
        self.assertFalse(identity_resolved(self._yt(IDENTITY=idt))[0])

    def test_link_pattern_que_casa_a_entrada_reprova(self):
        # ⚠️ A REGRA QUE IMPEDE «LISTAGEM VIRA ITEM».
        c = {"SOURCE_ID": "IT-T5-999", "OWNER": "x", "TERRITORY": "T5",
             "BATCH_ID": "b", "OUTPUT_TYPE": "HTML", "ROUTE_TYPE": "DISCOVERED_ROUTE",
             "CANONICAL_ENTRY_URL": "https://exemplo.it/notizie",
             "ACQUISITION": {"STRATEGY": "HTML_LINK_DISCOVERY", "MATCH": "URL",
                             "INDEX_URL": "https://exemplo.it/a-b-c",
                             "LINK_PATTERN": r"^https?://exemplo\.it/.*$"},
             "IDENTITY": {"CAPTURES": {"doc": {}}, "DOCUMENT_ID": "IT-T5-999:URL:{doc.1}",
                          "FACT_TIME": "UNKNOWN"},
             "EXPECTED_FAILURES": ["FAILED"], "FAIL_CLOSED_RULE": "FAILED",
             "NEGATIVE_CONTROL": {"esperado": "FAILED"},
             "SOURCE_CONTRACT_VERSION": "v1", "SOURCE_CONTRACT_HASH": "a"}
        passou, porque = route_resolved(c)
        self.assertFalse(passou)
        self.assertIn("listagem viraria item", porque)

    def test_sem_falha_fechada_reprova(self):
        self.assertFalse(output_resolved(
            self._yt(EXPECTED_FAILURES=["feed vazio = tudo bem"],
                     FAIL_CLOSED_RULE="segue em frente"))[0])

    def test_source_id_fora_do_formato_reprova(self):
        self.assertFalse(schema_valid(self._yt(SOURCE_ID="youtube-com-x"))[0])

    def test_output_type_xml_reprova(self):
        # XML nao esta no motor: um feed nao e um documento
        self.assertFalse(schema_valid(self._yt(OUTPUT_TYPE="XML"))[0])


if __name__ == "__main__":
    if "--teste" in sys.argv:
        sys.argv.remove("--teste")
        unittest.main(verbosity=2)
    raise SystemExit(main())
