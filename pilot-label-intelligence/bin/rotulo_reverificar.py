#!/usr/bin/env python3
"""
rotulo_reverificar.py — o passo DETECT da esteira, rodado de verdade.

Le o manifesto de leitura ja existente em sintonia/canonical (163 rotulos ADAMA
Italia, cada um com URL oficial, sha256 e data da etichetta) e volta a fonte
oficial HOJE para perguntar uma coisa so:

    o documento ainda e o mesmo?

Nao rebaixa nem reescreve o acervo existente. O acervo e a LINHA DE BASE; este
script produz o DELTA contra ela.

    REUSE_PROVED_EXISTING_READING_BEFORE_NEW_COLLECTION = SIM

Por que sha256 vale como identidade de versao: o proprio acervo canonico mostra
MANIFEST_SHA256 == SHA256 em 163/163 entre duas capturas distintas, e uma terceira
captura independente (esta sessao, 2026-09-06) reproduziu byte a byte o PDF do
registro 015275. O PDF servido e estavel; logo, hash diferente = documento
diferente, nao ruido de servidor.

O cliente HTTP e o wget, e isso e medido, nao preferencia: o host oficial emite um
cabecalho Public-Key-Pins truncado sem CRLF, que faz o curl abortar com
"Header without colon". O wget tolera. Alem disso o host manda cadeia TLS
incompleta e exige a intermediaria em recon/it-chain-fix.pem. Nenhuma verificacao
de certificado e desligada.
"""
import argparse, hashlib, json, os, subprocess, sys, time

UA = ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/126.0 Safari/537.36")
CA = "pilot-label-intelligence/recon/it-chain-fix.pem"
REFERER = "https://www.fitosanitari.salute.gov.it/fitosanitariws_new/FitosanitariServlet"


def baixar(url, dest, ca, sleep):
    tmp = dest + ".part"
    cmd = ["wget", f"--ca-certificate={ca}", "-U", UA, "-q",
           f"--header=Referer: {REFERER}", "-O", tmp,
           "--timeout=90", "--tries=2", url]
    rc = subprocess.run(cmd, capture_output=True).returncode
    size = os.path.getsize(tmp) if os.path.exists(tmp) else 0
    if rc != 0 or size == 0:
        _rm(tmp)
        return None, f"FETCH_FAILED(rc={rc},bytes={size})"
    with open(tmp, "rb") as fh:
        head = fh.read(5)
    if head != b"%PDF-":
        _rm(tmp)
        return None, "NOT_A_PDF"
    os.replace(tmp, dest)
    time.sleep(sleep)
    h = hashlib.sha256()
    with open(dest, "rb") as fh:
        for c in iter(lambda: fh.read(1 << 20), b""):
            h.update(c)
    return {"sha256": h.hexdigest(), "bytes": os.path.getsize(dest)}, "OK"


def _rm(p):
    try: os.remove(p)
    except OSError: pass


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--manifesto", required=True,
                    help="IT-ROTULOS-LEITURA-RUN.json de sintonia/canonical")
    ap.add_argument("--pdfdir", default="pilot-label-intelligence/labels/pdf")
    ap.add_argument("--out", default="pilot-label-intelligence/labels/IT-ROTULOS-REVERIFICACAO.json")
    ap.add_argument("--ca", default=CA)
    ap.add_argument("--sleep", type=float, default=1.2)
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--observed-at", required=True, help="AAAA-MM-DD desta verificacao")
    args = ap.parse_args()

    base = json.load(open(args.manifesto, encoding="utf-8"))
    items = base["ITEMS"]
    if args.limit:
        items = items[:args.limit]
    os.makedirs(args.pdfdir, exist_ok=True)

    linhas, mudou, igual, falhou = [], 0, 0, 0
    for i, it in enumerate(items, 1):
        reg = it["REGISTRATION_ID"]
        url = it["LABEL_URL"]
        antes = it["SHA256"]
        dest = os.path.join(args.pdfdir, f"{reg}.pdf")
        got, state = baixar(url, dest, args.ca, args.sleep)
        row = {
            "REGISTRATION_ID": reg,
            "PRODUCT": it["PRODUCT"],
            "REGULATORY_CATEGORY": it.get("REGULATORY_CATEGORY"),
            "LABEL_URL": url,
            "BASELINE_SHA256": antes,
            "BASELINE_BYTES": it.get("MANIFEST_BYTES"),
            "BASELINE_CAPTURED_AT": base.get("CAPTURED_AT"),
            "LABEL_EFFECTIVE_AT": it.get("MANIFEST_LABEL_DATE") or "NOT_KNOWN",
            "OBSERVED_AT": args.observed_at,
        }
        if got is None:
            row.update({"CHECK_STATE": state, "CURRENT_SHA256": "NOT_KNOWN",
                        "DOCUMENT_CHANGED": "NOT_KNOWN"})
            falhou += 1
        else:
            same = got["sha256"] == antes
            row.update({
                "CHECK_STATE": "CHECKED",
                "CURRENT_SHA256": got["sha256"],
                "CURRENT_BYTES": got["bytes"],
                "DOCUMENT_CHANGED": not same,
                "PDF_PATH": dest,
            })
            igual += same
            mudou += (not same)
        linhas.append(row)
        print(f"  [{i:>3}/{len(items)}] {reg} {it['PRODUCT'][:24]:<24} "
              f"{row['CHECK_STATE']:<12} changed={row['DOCUMENT_CHANGED']}",
              file=sys.stderr)

    out = {
        "DATASET": "IT-ROTULOS-REVERIFICACAO",
        "O_QUE_ISTO_E": ("verificacao de versao dos rotulos oficiais ADAMA Italia contra "
                         "a linha de base ja lida em sintonia/canonical"),
        "O_QUE_ISTO_NAO_E": ("nao e uma nova coleta do acervo, nao substitui a leitura "
                             "existente e nao reabre os pares cultura x alvo"),
        "BASELINE_SOURCE": "sintonia/canonical @ bdb57cf — data/samples/IT-ROTULOS-V1/IT-ROTULOS-LEITURA-RUN.json",
        "BASELINE_CAPTURED_AT": base.get("CAPTURED_AT"),
        "OBSERVED_AT": args.observed_at,
        "OFFICIAL_SOURCE": "Ministero della Salute — EtichettaServlet",
        "VERSION_IDENTITY_METHOD": "sha256 do PDF oficial",
        "LABELS_CHECKED": len(linhas),
        "DOCUMENT_UNCHANGED": igual,
        "DOCUMENT_CHANGED": mudou,
        "CHECK_FAILED": falhou,
        "REGRA": ("hash igual NAO prova que a autorizacao nao mudou; prova que o "
                  "DOCUMENTO nao mudou. Mudanca de registro se ve no registro."),
        "ITEMS": linhas,
    }
    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    json.dump(out, open(args.out, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    print(f"\n  verificados {len(linhas)} | iguais {igual} | mudaram {mudou} | "
          f"falharam {falhou}\n  escrito {args.out}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
