"""Prova dos INDEX_URL propostos: busca a pagina candidata e mede se e LISTAGEM.

    py scripts/receitas/provar_indices.py

Rede so aqui, com as regras do canario: egresso IT medido antes de cada site
(PARA se nao for), robots da casa, 2 pedidos por site (robots + pagina).
Bytes em ~/receitas-paginas/indices/, nunca na Sala nem no armazem.
"""
import hashlib
import json
import sys
import time
from pathlib import Path
from urllib.parse import urlparse

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ / "curadoria"))
sys.path.insert(0, str(RAIZ / "scripts" / "detector_capa"))
import canario as CAN            # noqa: E402
import gate_de_rota as GR        # noqa: E402
import colher_gabarito as CG     # noqa: E402

CANDIDATOS = {
    "IT-T2-039": "https://www.arpae.it/it/notizie",
    "IT-T12-044": "https://calabriaeuropa.regione.calabria.it/news",
    "IT-T11-010": "https://www.svilupposostenibile.regione.lombardia.it/it/educazione-ambientale/eventi",
}


def main() -> int:
    pasta = Path.home() / "receitas-paginas" / "indices"
    pasta.mkdir(parents=True, exist_ok=True)
    out = []
    for sid, url in CANDIDATOS.items():
        eg = CG.egresso()
        if eg.get("PAIS") != "IT":
            out.append({"SOURCE_ID": sid, "PAROU": "EGRESSO_NAO_IT", "EGRESSO": eg})
            break
        rp, porque = GR.robots_de(urlparse(url).netloc)
        if not rp.can_fetch(GR.CAP.UA, url):
            out.append({"SOURCE_ID": sid, "URL": url, "PAROU": "ROBOTS_NEGA", "EGRESSO": eg})
            continue
        time.sleep(1)
        st, b, err = CAN.buscar(url)
        linha = {"SOURCE_ID": sid, "URL": url, "HTTP": st, "EGRESSO": eg, "PEDIDOS": 2,
                 "ROBOTS": porque[:100], "QUANDO": CG.agora()}
        if st == 200 and b:
            sha = hashlib.sha256(b).hexdigest()
            f = pasta / f"{sid}-{sha[:12]}.html"
            f.write_bytes(b)
            linha.update(SHA256=sha, FICHEIRO=str(f), RETRATO=CAN.RH.retrato_do_html(b))
        else:
            linha["ERRO"] = err
        out.append(linha)
    (pasta / "MANIFESTO-INDICES.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    for l in out:
        print(l["SOURCE_ID"], l.get("HTTP"), l.get("PAROU", ""), (l.get("RETRATO") or {}).get("HTML_KIND"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
