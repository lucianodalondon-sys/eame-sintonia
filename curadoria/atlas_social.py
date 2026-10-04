"""SOC-ONDA2 · a ficha do Atlas para a conta social que o QUALIFY numerou.

    py curadoria/atlas_social.py                      # só mostra o que faltaria escrever
    py curadoria/atlas_social.py --escrever --copia   # acrescenta as fichas (só numa CÓPIA)

O BURACO QUE ISTO FECHA (medido em 24/09 no canário da SOC-ONDA2): o QUALIFY cunha
o SOURCE_ID no registo de alocação, mas a população que o Scrap consulta antes de
ancorar uma colheita (`leis/fonte_do_atlas.conhece`) é o Atlas + o MASTER. Sem ficha,
o Scrap responde «o atlas NUNCA emitiu este número» e a corrida sai com COLHEITA 0 —
com razão: carimbar com um número que o Atlas não conhece seria fabricar identidade.

A ficha segue o precedente do próprio Atlas para contas sociais (IT-T8-002, página
LinkedIn da Image Line): o que se provou fica escrito, o que não se mediu fica
`NAO SEI`, e o VERDICT é YELLOW até o canário trazer conteúdo.

    O ATLAS REGISTA FONTES, NÃO DESEJOS — e aqui o que se regista é a IDENTIDADE
    provada (o site oficial aponta para a conta), não uma colheita que ainda não houve.

⚠️ `--escrever` recusa a árvore do bot vivo e a ponte viva. No vivo, escrever no
Atlas é passo do plano de instalação — do coordenador.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
ATLAS = RAIZ / "docs" / "fontes" / "ATLAS-DE-FONTES-EAME.md"
ALLOC = RAIZ / "curadoria" / "SOURCE-ID-ALLOCATION-V1.json"
LIVRO = RAIZ / "curadoria" / "italy_contracts_curator.json"
VIVOS = ("source-curator-service-v1", "ponte-viva")
FAMILIAS = {"LINKEDIN": "SOCIAL - pagina institucional LinkedIn",
            "YOUTUBE": "VIDEO_CHANNEL - canal oficial no YouTube"}
CABECALHO = "## ONDA SOCIAL — SOC-ONDA2"


def ficha(n: dict, c: dict) -> str:
    fam = n["FAMILY"]
    aq = c.get("ACQUISITION") or {}
    ligacao = (n.get("MESMA_ORGANIZACAO") or {}).get("SITE") or "ver a candidata %s (ONDE_VIU)" % n["CANDIDATE_ID"]
    linhas = [
        ("SOURCE_ID", n["SOURCE_ID"]),
        ("SOURCE_NAME", n["NOME"]),
        ("SOURCE_OWNER", c.get("OWNER") or "NAO SEI"),
        ("COUNTRY", "ITALY"),
        ("REGION", "NAO SEI"),
        ("LANGUAGE", "it"),
        ("TERRITORY", n["TERRITORY"]),
        ("SOURCE_TYPE", FAMILIAS.get(fam, "NAO SEI")),
        ("URL", c.get("CANONICAL_ENTRY_URL") or n["URL"]),
        ("PLATFORM_NATIVE_ID", "%s (%s)" % (n.get("SOURCE_NATIVE_ID"), n.get("SOURCE_NATIVE_ID_KIND"))),
        ("IDENTITY_PROOF", "o site oficial da organizacao aponta para a conta (D21 cond. 2 / D24): %s"
                           % ligacao),
        ("TERRITORY_REASON", (n.get("TERRITORY_REASON") or "")[:200]),
        ("ACCESS_METHOD", "SCRAP · fase %s (%s) · %s" % (aq.get("FASE"), aq.get("CAPACIDADE"),
                                                         aq.get("AUTORIZACAO", "")[:90])),
        ("CROPS", "NAO SEI"),
        ("TOPICS", "NAO SEI - conteudo ainda nao observado"),
        ("UPDATE_FREQUENCY", "NAO SEI"),
        ("HISTORICAL_DEPTH", "NAO SEI"),
        ("SOURCE_IDENTITY_PRESERVABLE", "SIM - id nativo da plataforma, ligado pelo site oficial"),
        ("DOCUMENT_ID_AVAILABLE", "SIM - id nativo por item (%s)" % c.get("IDENTITY", {}).get("DOCUMENT_ID")),
        ("PUBLICATION_DATE_AVAILABLE", "NAO SEI - declarada pela plataforma; a medir no canario"),
        ("RAW_EVIDENCE_PRESERVABLE", "SIM - o Scrap preserva o bruto antes de normalizar"),
        ("AUTOMATION_FEASIBILITY", "NAO SEI - canario pendente"),
        ("COLLECTION_FEASIBILITY", "CONTRATO ESCRITO (curadoria/italy_contracts_curator.json); CANARIO PENDENTE"),
        ("LEGAL_OR_ACCESS_RISK", "plataforma proibe coleta automatizada; dono autorizou (%s); "
                                 "sem login, sem conta, sem contorno de muro" % (
                                     "D23" if fam == "LINKEDIN" else "D17.4")),
        ("REAL_EXAMPLE", "NAO SEI - canario pendente"),
        ("EVIDENCE", "curadoria/SOURCE-ID-ALLOCATION-V1.json (%s) + candidata %s"
                     % (n["SOURCE_ID"], n["CANDIDATE_ID"])),
        ("VERDICT", "YELLOW - identidade provada pelo site oficial; conteudo ainda nao observado"),
    ]
    corpo = "\n".join("%-30s%s" % (k + ":", v) for k, v in linhas)
    return "#### %s · %s\n\n```\n%s\n```\n" % (n["SOURCE_ID"], n["NOME"], corpo)


def faltam() -> list[tuple[dict, dict]]:
    sys.path.insert(0, str(RAIZ / "leis"))
    import fonte_do_atlas as fa
    alloc = json.loads(ALLOC.read_text(encoding="utf-8"))
    contr = {c["SOURCE_ID"]: c for c in json.loads(LIVRO.read_text(encoding="utf-8"))["FONTES"]}
    pop = fa.populacao(raiz=str(RAIZ), recarregar=True)
    out = []
    for n in alloc.get("NOVAS", []):
        c = contr.get(n["SOURCE_ID"])
        if n.get("FAMILY") in FAMILIAS and c and (c.get("ACQUISITION") or {}).get("STRATEGY") == "SCRAP_FASE" \
                and n["SOURCE_ID"] not in pop:
            out.append((n, c))
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--escrever", action="store_true")
    ap.add_argument("--copia", action="store_true")
    a = ap.parse_args()
    lista = faltam()
    print("fichas sociais em falta no Atlas: %d" % len(lista))
    for n, _c in lista:
        print("  %s  %s  %s" % (n["SOURCE_ID"], n["FAMILY"], n["NOME"][:60]))
    if not a.escrever:
        return 0
    if not a.copia or any(v in str(RAIZ).replace("\\", "/") for v in VIVOS):
        print("RECUSADO: --escrever so numa copia (--copia), nunca em %s" % ", ".join(VIVOS))
        return 2
    if not lista:
        return 0
    txt = ATLAS.read_text(encoding="utf-8")
    cab = "" if CABECALHO in txt else (
        "\n---\n\n%s\n\n*Contas sociais numeradas pelo QUALIFY do Source Curator, com a identidade\n"
        "provada pelo site oficial da propria organizacao. Nenhuma foi colhida ainda.*\n" % CABECALHO)
    ATLAS.write_text(txt.rstrip() + "\n" + cab + "\n" + "\n".join(ficha(n, c) for n, c in lista),
                     encoding="utf-8")
    print("escritas %d" % len(lista))
    return 0


if __name__ == "__main__":
    sys.exit(main())
