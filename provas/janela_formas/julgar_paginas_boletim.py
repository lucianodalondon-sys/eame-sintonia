"""JANELA-FORMAS B — fase 2 (SEM rede): julgar as 8 «a pagina e o boletim» sobre os bytes buscados na
fase 1 (INDICE.json) e, para a que o e, correr o canario da forma + a regua irma, e a DEDUPE contra os
bytes guardados de manha (lote da bancada): a mesma edicao tem de dar a mesma identidade e a mesma
impressao, com bytes diferentes.
uso: py provas/janela_formas/julgar_paginas_boletim.py <copia com os livros vivos> <pasta fase 1> <LOTE.json da manha> <saida.json>
(o codigo e o deste ramo; os contratos vem da copia)"""
import copy
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

RAIZ, FASE1, LOTE, SAIDA = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3]), Path(sys.argv[4])
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "curadoria"))   # o codigo: este ramo
import canario as CAN            # noqa: E402
import ready_split as RS         # noqa: E402
import validar_contratos as VC   # noqa: E402

indice = {p["CASO"]: p for p in json.loads((FASE1 / "INDICE.json").read_text(encoding="utf-8"))["PAGINAS"]}
lote = json.loads(LOTE.read_text(encoding="utf-8"))
manha = {c["CASO"]: [p for p in c["PAGINAS"] if p["PAPEL"] == "ENTRADA"][0] for c in lote["CASOS"]}
contratos = {c["SOURCE_ID"]: c for c in json.loads((RAIZ / "curadoria/italy_contracts_curator.json").read_text(encoding="utf-8"))["FONTES"]}

# ── o que o agente leu nas paginas (prova: bytes da fase 1 e da manha, sha256 no indice) ──
FORMAS = {
    "IT-T2-152": ("PAGINA_E_BOLETIM", "«Aggiornato il DD/MM/AAAA», «aggiornato una volta la settimana (giovedi)», observacoes da semana com periodo — a pagina fixa E o boletim"),
    "IT-T1-006": ("LISTA_POR_EDICAO", "uma publicacao por semana («Pubblicato il bollettino Settimana 31 dal 20/07 al 04/08/2026»); o endereco e UMA edicao de agosto: falta a lista (categoria) — nao e pagina fixa"),
    "IT-T2-148": ("LISTA_PARADA", "lista de boletins «valido fino al 29 novembre 2022» — o site parou em 2022"),
    "IT-T2-136": ("BOLETIM_FORA_DO_TEXTO", "nenhuma data nem corpo de boletim no texto do HTML (so menu): o boletim e imagem/PDF/JS"),
    "IT-T2-138": ("IMAGENS", "mapas semanais em imagem; 2 092 caracteres de texto, quase so menu"),
    "IT-T2-139": ("IMAGENS", "«Pubblicato il 4/8/2020»; 1 357 caracteres, o resto e imagem"),
    "IT-T2-153": ("PAGINA_DESCRITIVA", "descreve os boletins do CAAR; o de viticultura remete para sia.regione.liguria.it (outro site, lista)"),
    "IT-T3-031": ("PAGINA_DESCRITIVA", "pagina de referencia da vigilancia fitossanitaria, sem boletim datado"),
}

LAMMA = "IT-T2-152"
base = copy.deepcopy(contratos[LAMMA])
url = indice[LAMMA]["URL"]
base.update({
    "FORMA": "PAGINA_E_BOLETIM", "OUTPUT_TYPE": "HTML", "CANONICAL_ENTRY_URL": url,
    "ACQUISITION": {"STRATEGY": "STATIC_ENDPOINT", "URL": url, "NAME": "agrometeo-firenze.html"},
    "RECOLLECTION": {"DETAIL_CONTENT": "MUTABLE", "TTL_SECONDS": 86400},
    "IDENTITY": {
        "STRATEGY": "CONTENT_CAPTURE",
        "DOCUMENT_ID": LAMMA + ":BOLETIM:FIRENZE:{aggiornato.3}-{aggiornato.2}-{aggiornato.1}",
        "SOURCE_DATE": "{aggiornato.1}/{aggiornato.2}/{aggiornato.3}",
        "SOURCE_DATE_ISO": "{aggiornato.3}-{aggiornato.2}-{aggiornato.1}",
        "FACT_TIME": "{settimana.1} a {settimana.2}",
        "CONTENT_SCOPE": {"START": "Aggiornato il", "END": "Condividi"},
        "CAPTURES": {
            "aggiornato": {"FROM": "PAGE_TEXT", "PATTERN": "Aggiornato il\\s+(\\d{2})/(\\d{2})/(\\d{4})",
                           "REQUIRED": False, "DEFAULTS": ["UNKNOWN", "UNKNOWN", "UNKNOWN"]},
            "settimana": {"FROM": "PAGE_TEXT", "PATTERN": "Osservazioni della settimana da (\\d{2}/\\d{2}/\\d{4}) a (\\d{2}/\\d{2}/\\d{4})",
                          "REQUIRED": False, "DEFAULTS": ["UNKNOWN", "UNKNOWN"]},
        },
    },
    "ROUTE_PROVENANCE": {"MISSAO": "JANELA-FORMAS B (D42 2)", "INTEGRADO_EM": "2026-09-25T09:00:00+00:00",
                         "ANTERIOR": contratos[LAMMA].get("ROUTE_PROVENANCE")},
})
_, falhas = VC.validar([base])
velho = CAN.buscar
agora_b = Path(indice[LAMMA]["BYTES_EM"]).read_bytes()
CAN.buscar = lambda u: (200, agora_b, None) if u == url else (404, b"", "HTTP 404")
try:
    r = CAN.canario_pagina_boletim(base)
finally:
    CAN.buscar = velho
reg = RS.passos_da_promocao({"OBSERVED_AT": "2026-09-25T09:30:00+00:00", "EVIDENCE_REF": "copia"}, {"DADOS": r}, base)
manha_b = Path(manha[LAMMA]["BYTES_EM"]).read_bytes()
id_manha = CAN.identidade_pelo_motor(base, url, manha_b)
dedupe = {"BYTES_IGUAIS": hashlib.sha256(manha_b).hexdigest() == hashlib.sha256(agora_b).hexdigest(),
          "SHA_BYTES_MANHA": hashlib.sha256(manha_b).hexdigest(), "SHA_BYTES_AGORA": hashlib.sha256(agora_b).hexdigest(),
          "DOCUMENT_ID_MANHA": id_manha.get("DOCUMENT_ID"), "DOCUMENT_ID_AGORA": r.get("ITEM_ABERTO", {}).get("DOCUMENT_ID"),
          "CONTENT_SHA256_MANHA": id_manha.get("CONTENT_SHA256"),
          "CONTENT_SHA256_AGORA": r.get("ITEM_ABERTO", {}).get("CONTENT_SHA256")}
dedupe["MESMA_EDICAO_DEDUPLICADA"] = (dedupe["DOCUMENT_ID_MANHA"] == dedupe["DOCUMENT_ID_AGORA"]
                                      and dedupe["CONTENT_SHA256_MANHA"] == dedupe["CONTENT_SHA256_AGORA"])
saida = {"CANARIO": "JANELA-FORMAS B — a pagina e o boletim (fase 2, sem rede)",
         "FORMAS_LIDAS": {s: {"FORMA": f, "PORQUE": p, "BYTES_SHA256": indice.get(s, {}).get("SHA256")} for s, (f, p) in FORMAS.items()},
         "LAMMA": {"CONTRATO": base, "VALIDADOR": falhas or "OK",
                   "CANARIO": {k: r.get(k) for k in ("PASS", "CLASSE", "PORQUE", "ITEM_ABERTO", "DETAIL_GATE")},
                   "REGUA": reg, "DEDUPE_MANHA_VS_AGORA": dedupe}}
SAIDA.write_text(json.dumps(saida, ensure_ascii=False, indent=1), encoding="utf-8")
it = r.get("ITEM_ABERTO") or {}
print("validador:", falhas or "OK")
print("canario:", r.get("PASS"), r.get("PORQUE"), it.get("DOCUMENT_ID"), it.get("SOURCE_DATE_ISO"), it.get("FACT_TIME"), it.get("BOLETIM_CARACTERES"))
print("regua:", reg["REGUA"], reg.get("INFO"))
print("dedupe:", {k: dedupe[k] for k in ("BYTES_IGUAIS", "MESMA_EDICAO_DEDUPLICADA", "DOCUMENT_ID_MANHA")})
