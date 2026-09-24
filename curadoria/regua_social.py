"""SOC-ONDA2 · A RÉGUA DO CANÁRIO SOCIAL — o recibo da corrida do Scrap decide READY.

    py curadoria/regua_social.py --corridas RESULTADOS.json [--banco-raw RAW.json]
    py curadoria/regua_social.py --corridas RESULTADOS.json --aplicar --copia

O canário de uma rota do Scrap (`SCRAP_FASE`) NÃO é do worker: é uma corrida do
orquestrador (`scrap-colheita`), a mesma porta que a onda vai usar (D28). O worker
pára em CANARY_PENDING. Faltava quem LESSE o recibo dessa corrida e dissesse ao
livro o que ele prova — e isso é este ficheiro. Não corre nada; lê.

A RÉGUA (uma fonte, uma corrida da fase do SEU contrato, com o SEU SOURCE_ID):

    READY       o envelope diz RESULT=OK e traz >= 1 item de COLHEITA em que
                cada item tem NATIVE_ID (a identidade da plataforma), PUBLISHED_AT,
                OWNER_AUTHORIZED=SIM e PLATFORM_POLICY_STATUS escrito — e o banco
                da corrida tem >= 1 linha RAW (o bruto foi guardado, não só visto).
    ZERO        RESULT=ZERO_RESULTS: a rota abriu e não havia item público.
                Zero legítimo NÃO é falha nem é prontidão: fica CANARY_PENDING,
                com a prova escrita, para voltar a medir.
    FALHA       o resto (erro, muro de login, item sem identidade, RAW 0 com
                colheita > 0): CONTRACTED_CANARY_FAILED, com o porquê.

    UMA FONTE SOCIAL SÓ É PRONTA QUANDO A PORTA QUE A VAI COLHER A COLHEU.

⚠️ O envelope de uma corrida cuja fonte o Atlas não conhece traz COLHEITA 0 com a
razão escrita — isso é FALHA do registo, não ZERO da plataforma, e a régua separa.
⚠️ `--aplicar` recusa a árvore do bot vivo e a ponte viva.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "curadoria"))

VIVOS = ("source-curator-service-v1", "ponte-viva")
READY, ZERO, FALHA = "READY", "ZERO", "FALHA"
CAMPOS_DO_ITEM = ("NATIVE_ID", "PUBLISHED_AT", "OWNER_AUTHORIZED", "PLATFORM_POLICY_STATUS")


RE_LOCALE = re.compile(r"^https?://([a-z]{2,3})\.linkedin\.com/", re.I)
RE_SLUG = re.compile(r"linkedin\.com/(?:company|showcase)/([^/?#]+)", re.I)
RE_PALAVRA = re.compile(r"[a-zà-ú]{4,}", re.I)
VAZIAS = {"linkedin", "ufficiale", "youtube", "canale", "official", "italia", "italy", "della", "delle",
          "degli", "dell", "per", "and", "the"}


def _palavras(t: str) -> set:
    return {w.lower() for w in RE_PALAVRA.findall(t or "")} - VAZIAS


def autor(it: dict) -> tuple[str, str]:
    raw = (it.get("OBSERVACAO") or {}).get("RAW") or {}
    return raw.get("CREATOR_NAME") or "", raw.get("CREATOR_URL") or ""


def conferir_autor(itens: list, slug: str | None, nome_da_fonte: str | None) -> tuple[list, str | None]:
    """→ (itens publicados PELA PROPRIA pagina, divergencia de identidade ou None).

    Medido em 24/09: uma pagina LinkedIn devolve tambem videos REPUBLICADOS de
    outras organizacoes (ASSAM Marche -> «ABC Interreg»); e uma candidata com o
    endereco cortado no registo («company/societ») apontava para uma empresa do
    CANADA. Nome parecido nunca PROVA identidade (D21) — mas nome que nao partilha
    uma unica palavra com a fonte, ou uma pagina servida de outro pais, e sinal
    bastante para parar e chamar um humano. Parar e barato; colher a empresa
    errada e caro.
    """
    if not slug:
        return itens, None
    proprios = []
    for it in itens:
        nome, url = autor(it)
        m = RE_SLUG.search(url)
        if m and m.group(1).lower().rstrip("/") == slug.lower():
            proprios.append(it)
    if not proprios:
        return [], None
    nome, url = autor(proprios[0])
    loc = RE_LOCALE.match(url)
    if loc and loc.group(1).lower() not in ("it", "www"):
        return proprios, "a pagina serve-se como %s.linkedin.com (%s): outro pais?" % (loc.group(1), nome)
    if nome_da_fonte and not (_palavras(nome) & _palavras(nome_da_fonte)):
        return proprios, "quem publica chama-se «%s» e a fonte «%s»: nenhuma palavra em comum" % (
            nome, nome_da_fonte[:60])
    return proprios, None


def _resultado(env: dict) -> str | None:
    for s in env.get("SUPORTE") or []:
        if s.get("ESPECIE") == "RUN_RECEIPT":
            return (s.get("RESUMO") or {}).get("RESULT")
    return None


def julgar(env: dict, sid: str, fase: str, raw_no_banco: int | None,
           slug: str | None = None, nome_da_fonte: str | None = None) -> tuple[str, str]:
    """→ (READY | ZERO | FALHA, porquê). Puro: sem disco, sem rede."""
    if env.get("SOURCE_ID_DO_PEDIDO") != sid:
        return FALHA, "o envelope e de %r, nao de %s" % (env.get("SOURCE_ID_DO_PEDIDO"), sid)
    if env.get("FASE") != fase:
        return FALHA, "o envelope e da fase %r, e o contrato pede %s" % (env.get("FASE"), fase)
    res = _resultado(env)
    col = env.get("COLHEITA")
    itens = col if isinstance(col, list) else []
    if not itens:
        if env.get("PORQUE_ZERO_COLHEITA", "").startswith("o pedido nomeou uma fonte que o atlas"):
            return FALHA, "o Atlas nao conhece %s: a corrida nao pode ancorar nada" % sid
        if res == "ZERO_RESULTS":
            return ZERO, "a rota abriu e nao havia item publico (ZERO_RESULTS): zero legitimo, nao prontidao"
        return FALHA, "colheita vazia com RESULT=%s: %s" % (res, (env.get("PORQUE_ZERO_COLHEITA") or "")[:120])
    if res != "OK":
        return FALHA, "colheita com RESULT=%s" % res
    for i, it in enumerate(itens):
        ob = it.get("OBSERVACAO") or {}
        falta = [k for k in CAMPOS_DO_ITEM if not ob.get(k) or ob.get(k) == "NAO SEI"]
        if falta:
            return FALHA, "item %d sem %s" % (i, ", ".join(falta))
        if ob.get("OWNER_AUTHORIZED") != "SIM":
            return FALHA, "item %d sem autorizacao do dono escrita" % i
    proprios, diverge = conferir_autor(itens, slug, nome_da_fonte)
    if not proprios:
        return FALHA, ("%d itens e NENHUM publicado pela propria pagina (%s): republicacoes de "
                       "outras organizacoes nao provam a fonte" % (len(itens), slug))
    if diverge:
        return FALHA, "IDENTIDADE A CONFERIR POR HUMANO: " + diverge
    if not raw_no_banco:
        return FALHA, "%d itens vistos e 0 linhas RAW no banco da corrida: visto nao e guardado" % len(itens)
    return READY, ("canario do Scrap (%s): %d itens (%d da propria pagina) com identidade da "
                   "plataforma e data, autorizacao do dono e politica escritas; %d linhas RAW no banco"
                   % (fase, len(itens), len(proprios), raw_no_banco))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--corridas", required=True, help="resultados.json do canario (SOURCE_ID, FASE, RUN_ID, MEDIDA.RAW)")
    ap.add_argument("--envelopes", default=str(RAIZ / "data" / "colheita" / "scrap"))
    ap.add_argument("--aplicar", action="store_true")
    ap.add_argument("--copia", action="store_true")
    ap.add_argument("--json")
    a = ap.parse_args()
    corridas = json.loads(Path(a.corridas).read_text(encoding="utf-8"))
    contratos = {c["SOURCE_ID"]: c for c in json.loads(
        (RAIZ / "curadoria" / "italy_contracts_curator.json").read_text(encoding="utf-8"))["FONTES"]}
    linhas = []
    for x in corridas.values():
        env_p = Path(a.envelopes) / str(x.get("RUN_ID")) / "ENVELOPE.json"
        env = json.loads(env_p.read_text(encoding="utf-8")) if env_p.exists() else {}
        med = x.get("MEDIDA") if isinstance(x.get("MEDIDA"), dict) else {}
        c = contratos.get(x["SOURCE_ID"]) or {}
        slug = (c.get("ACQUISITION") or {}).get("LINKEDIN_SLUG")
        v, porque = julgar(env, x["SOURCE_ID"], x["FASE"], len(med.get("RAW") or []) if med else None,
                           slug=slug, nome_da_fonte=c.get("NAME"))
        linhas.append({"SOURCE_ID": x["SOURCE_ID"], "FASE": x["FASE"], "RUN_ID": x.get("RUN_ID"),
                       "VEREDITO": v, "PORQUE": porque})
    print(dict(Counter(l["VEREDITO"] for l in linhas)))
    if a.aplicar:
        if not a.copia or any(s in str(RAIZ).replace("\\", "/") for s in VIVOS):
            print("RECUSADO: --aplicar so numa copia (--copia), nunca em %s" % ", ".join(VIVOS))
            return 2
        import lifecycle as LC
        import worker as W
        for l in linhas:
            sid = l["SOURCE_ID"]
            ref = W._guardar_evidencia(sid, "CANARY_SOCIAL", l)
            de = LC.estado_de(sid)
            if l["VEREDITO"] == READY and de in LC.PODEM_PROMOVER:
                LC.registar(sid, LC.READY_FOR_COLLECTION, l["PORQUE"][:200], evidence_ref=ref)
            elif l["VEREDITO"] == FALHA and de != LC.CONTRACTED_CANARY_FAILED:
                LC.registar(sid, LC.CONTRACTED_CANARY_FAILED, l["PORQUE"][:200], evidence_ref=ref)
            l["ESTADO_DEPOIS"] = LC.estado_de(sid)
        print("estados depois:", dict(Counter(l["ESTADO_DEPOIS"] for l in linhas)))
    if a.json:
        Path(a.json).write_text(json.dumps({"DATASET": "SOC-ONDA2-REGUA-SOCIAL-V1", "LINHAS": linhas},
                                           ensure_ascii=False, indent=1), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
