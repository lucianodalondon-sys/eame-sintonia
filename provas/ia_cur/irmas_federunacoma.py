"""D32 (1): as irmas FederUnacoma colhem o mesmo item? Le os bytes buscados com rede em 24/09
(C:/cur/irmas/BUSCA.jsonl + bytes/, fora do Git; sha256 do indice na saida) e aplica a identidade
do item (curadoria/irmas_por_item.py). Nao busca nada.
uso: py provas/ia_cur/irmas_federunacoma.py <BUSCA.jsonl> <saida.json>"""
import collections
import hashlib
import json
import re
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ / "curadoria"))
import irmas_por_item as IPI   # noqa: E402
import retrato_html as RH      # noqa: E402

BUSCA, SAIDA = Path(sys.argv[1]), Path(sys.argv[2])
linhas = [json.loads(l) for l in BUSCA.read_text(encoding="utf-8").splitlines()]
lista, itens = collections.defaultdict(set), collections.defaultdict(dict)
for d in linhas:
    if not d.get("BYTES"):
        continue
    b = Path(d["BYTES_EM"]).read_bytes()
    assert hashlib.sha256(b).hexdigest() == d["SHA256"], d["URL"]
    ew = re.search(r"EW_ID=(\d+)", d["URL"])
    if ew:
        r = RH.retrato_do_html(b)
        itens[d["SOURCE_ID"]][ew.group(1)] = {
            "URL": d["URL"], "SHA256_DA_PAGINA": d["SHA256"], "TEXT_SHA256_DO_RETRATO": r["TEXT_SHA256"],
            "ITEM_IDENTITY": IPI.identidade_do_item(b), "CAPA_OU_MATERIA": r["CAPA_OU_MATERIA"],
            "PARAGRAPH_CHARACTERS": r["PARAGRAPH_CHARACTERS"]}
    elif "news-" in d["URL"]:
        lista[d["SOURCE_ID"]] = set(re.findall(r"news_open\.php\?EW_ID=(\d+)", b.decode("utf-8", "replace")))

sids = sorted(lista)
pares = [{"A": a, "B": b, "EW_ID_COMUNS": len(lista[a] & lista[b]), "DE_A": len(lista[a]), "DE_B": len(lista[b])}
         for i, a in enumerate(sids) for b in sids[i + 1:] if lista[a] and lista[b]]
por_ew = collections.defaultdict(dict)
for sid, m in itens.items():
    for ew, v in m.items():
        por_ew[ew][sid] = v
comparados = []
for ew, m in sorted(por_ew.items()):
    comparados.append({"EW_ID": ew, "FONTES": sorted(m),
                       "PAGINAS_DIFERENTES": len({v["SHA256_DA_PAGINA"] for v in m.values()}),
                       "RETRATOS_DIFERENTES": len({v["TEXT_SHA256_DO_RETRATO"] for v in m.values()}),
                       "IDENTIDADES_DIFERENTES": len({v["ITEM_IDENTITY"] for v in m.values()}),
                       "TODOS_MATERIA": all(v["CAPA_OU_MATERIA"] == "MATERIA_PROVAVEL" for v in m.values())})
saida = {
    "DECISAO": "D32 (1) — duplicados entre irmas pela identidade do item",
    "BUSCA": {"INDICE": str(BUSCA), "SHA256": hashlib.sha256(BUSCA.read_bytes()).hexdigest(),
              "BYTES_EM": str(BUSCA.parent / "bytes"), "EGRESSO": "IT (consenso)", "PEDIDOS": len(linhas)},
    "IDENTIDADE": IPI.VERSAO,
    "ITENS_NA_LISTAGEM": {s: len(lista[s]) for s in sids},
    "PARES": pares,
    "ITENS_ABERTOS_COMPARADOS": comparados,
    "LEITURA": ("As listagens partilham os mesmos EW_ID; a pagina (sha256) e o texto visivel do retrato "
                "diferem de irma para irma (rodape com o nome da associacao), a identidade do item nao. "
                "Por isso: a primeira irma que chega a READY colhe; as outras, com o mesmo item, ficam "
                "CONTRACTED_CANARY_FAILED com DUPLICADA_DE_IRMA e o nome da irma."),
}
SAIDA.write_text(json.dumps(saida, ensure_ascii=False, indent=1), encoding="utf-8")
print(json.dumps({k: saida[k] for k in ("ITENS_NA_LISTAGEM", "PARES")}, ensure_ascii=False))
for c in comparados:
    print(c)
