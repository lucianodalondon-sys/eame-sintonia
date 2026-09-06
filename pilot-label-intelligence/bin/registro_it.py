#!/usr/bin/env python3
"""
registro_it.py — o registro oficial italiano, com historico real.

Baixa instantaneos semanais do dataset Prodotti Fitosanitari do Ministero della
Salute, preserva cada um com sha256, e compara instantaneos consecutivos para
produzir eventos de mudanca REAIS.

O que este script NAO faz: inventar versao. Dois instantaneos com o mesmo sha256
sao UM documento, mesmo com nomes de arquivo diferentes.

Fonte:  https://www.dati.salute.gov.it/it/dataset/fitosanitari
Licenca: Italian Open Data Licence v2.0
"""
import argparse, csv, datetime, hashlib, json, os, subprocess, sys, time

BASE = "https://www.dati.salute.gov.it/sites/default/files/opendata"
PATTERN = "PROD_FTS_6_{date}.csv"
UA = ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/126.0 Safari/537.36")

HOLDER_MATCH = "ADAMA"
# Estados que significam "nao vale mais". Tudo o resto conta como ativo.
INACTIVE = {"Revocato", "Scaduto"}

# Campos que, mudando, sao mudanca regulatoria de verdade.
WATCHED = {
    "ragione_sociale":                "HOLDER_CHANGED",
    "data_scadenza_autorizzazione":   "EXPIRY_CHANGED",
    "stato_amministrativo":           "STATUS_CHANGED",
    "sostanze_attive":                "ACTIVE_INGREDIENT_CHANGED",
    "descrizione_formulazione":       "FORMULATION_CHANGED",
    "denominazione_prodotto":         "PRODUCT_NAME_CHANGED",
    "indicazioni_di_pericolo":        "HAZARD_CHANGED",
    "motivo_della revoca":            "REVOCATION_REASON_CHANGED",
    "data_decreto_revoca":            "REVOCATION_DECREE_CHANGED",
    "data_decorrenza_revoca":         "REVOCATION_EFFECT_CHANGED",
}


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def fetch(date, outdir, sleep=1.0):
    """Baixa um instantaneo. Devolve dict de proveniencia, ou estado de falha.

    Usa curl e nao urllib de proposito: o host do Ministero rejeita o handshake
    TLS do Python com SSLV3_ALERT_HANDSHAKE_FAILURE, e responde normalmente ao
    curl. Medido nesta maquina. Nenhuma verificacao de certificado e desligada.
    """
    os.makedirs(outdir, exist_ok=True)
    name = PATTERN.format(date=date)
    dest = os.path.join(outdir, name)
    url = f"{BASE}/{name}"
    if os.path.exists(dest) and os.path.getsize(dest) > 100000:
        return provenance(dest, url, date, cached=True)
    tmp = dest + ".part"
    cmd = ["curl", "-sS", "-A", UA, "-L", "--max-time", "180",
           "-o", tmp, "-w", "%{http_code}", url]
    try:
        code = subprocess.run(cmd, capture_output=True, text=True,
                              timeout=200).stdout.strip()
    except Exception as e:
        _rm(tmp)
        return {"date": date, "url": url, "http_status": None,
                "state": "FETCH_FAILED", "error": type(e).__name__}
    size = os.path.getsize(tmp) if os.path.exists(tmp) else 0
    # O portal devolve 200 com pagina de erro HTML para datas inexistentes.
    if code != "200" or size < 100000 or _looks_html(tmp):
        _rm(tmp)
        return {"date": date, "url": url, "http_status": code,
                "state": "NOT_PRESENT"}
    os.replace(tmp, dest)
    time.sleep(sleep)
    return provenance(dest, url, date, cached=False)


def _rm(p):
    try: os.remove(p)
    except OSError: pass


def _looks_html(p):
    with open(p, "rb") as fh:
        return fh.read(200).lstrip().lower().startswith(b"<!doctype")


def provenance(dest, url, date, cached):
    return {
        "date": date,
        "url": url,
        "http_status": 200,
        "state": "DOWNLOADED",
        "path": dest,
        "bytes": os.path.getsize(dest),
        "sha256": sha256_file(dest),
        "cached": cached,
    }


def read_rows(path):
    with open(path, encoding="utf-8", errors="replace", newline="") as fh:
        return list(csv.DictReader(fh, delimiter=";"))


def adama_rows(rows):
    """Indexado por numero de registro — a chave estavel do registro italiano."""
    out = {}
    for r in rows:
        if HOLDER_MATCH in (r.get("ragione_sociale") or "").upper():
            out[(r.get("num_registrazione") or "").strip()] = r
    return out


def is_active(row):
    return (row.get("stato_amministrativo") or "").strip() not in INACTIVE


# Campos que a fonte serializa com "|" e cuja ORDEM nao e estavel entre
# publicacoes. Comparar como texto cru gera mudanca falsa toda semana.
MULTIVALUED = {"indicazioni_di_pericolo", "sostanze_attive"}


def norm(field, value):
    v = (value or "").strip()
    if field in MULTIVALUED:
        return "|".join(sorted(p.strip() for p in v.split("|") if p.strip()))
    return v


def mark_oscillations(events):
    """Marca ida-e-volta como instabilidade da fonte, nao mudanca regulatoria.

    Se um mesmo (registro, campo) volta a um valor que ja tinha antes, a fonte
    esta oscilando. Isso nao e regulacao mudando: e serializacao instavel. A
    missao proibe promover mudanca textual sem significado regulatorio provado.
    """
    history = {}
    for e in events:
        key = (e["REGISTRATION_ID"], e["FIELD"])
        seen = history.setdefault(key, set())
        seen.add(e["BEFORE"])
        if e["AFTER"] in seen:
            e["CHANGE_TYPE"] = "TEXT_CHANGE_OTHER"
            e["UNSTABLE_SOURCE"] = True
            e["NOTE"] = ("valor ja observado antes neste registro/campo: a fonte "
                         "oscila entre publicacoes. Nao promovido a mudanca "
                         "regulatoria.")
        seen.add(e["AFTER"])
    return events


def contar_diffs_de_campo(old_idx, new_idx, normalizar):
    """Diferencas de CAMPO entre dois instantaneos, com e sem normalizacao.

    Compara so registros presentes nos dois lados, e so campos — entrada e saida
    de produto ficam de fora de proposito, para que os dois numeros sejam
    comparaveis entre si. Um differ ingenuo entregaria o numero sem normalizar.
    """
    n = 0
    for reg in set(old_idx) & set(new_idx):
        o, nn = old_idx[reg], new_idx[reg]
        for field in WATCHED:
            if normalizar:
                a, b = norm(field, o.get(field)), norm(field, nn.get(field))
            else:
                a, b = (o.get(field) or "").strip(), (nn.get(field) or "").strip()
            if a != b:
                n += 1
    return n


def diff(old_idx, new_idx, old_meta, new_meta):
    """Eventos de mudanca entre dois instantaneos oficiais consecutivos."""
    events = []
    def ev(reg, row, kind, field, before, after):
        events.append({
            "REGISTRATION_ID": reg,
            "PRODUCT": (row.get("denominazione_prodotto") or "").strip(),
            "HOLDER": (row.get("ragione_sociale") or "").strip(),
            "CHANGE_TYPE": kind,
            "FIELD": field,
            "BEFORE": before,
            "AFTER": after,
            "OLD_VERSION": old_meta["sha256"][:16],
            "NEW_VERSION": new_meta["sha256"][:16],
            "OLD_SNAPSHOT": old_meta["date"],
            "NEW_SNAPSHOT": new_meta["date"],
            "SOURCE": new_meta["url"],
            "OBSERVATION_WINDOW": f'{old_meta["date"]}..{new_meta["date"]}',
        })
    for reg in sorted(set(new_idx) - set(old_idx)):
        ev(reg, new_idx[reg], "PRODUCT_ADDED", "*", "NOT_PRESENT",
           new_idx[reg].get("stato_amministrativo"))
    for reg in sorted(set(old_idx) - set(new_idx)):
        ev(reg, old_idx[reg], "PRODUCT_REMOVED", "*",
           old_idx[reg].get("stato_amministrativo"), "NOT_PRESENT")
    for reg in sorted(set(old_idx) & set(new_idx)):
        o, n = old_idx[reg], new_idx[reg]
        for field, kind in WATCHED.items():
            a, b = norm(field, o.get(field)), norm(field, n.get(field))
            if a != b:
                ev(reg, n, kind, field, a or "NOT_PRESENT", b or "NOT_PRESENT")
    return events


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--outdir", default="pilot-label-intelligence/registry/snapshots")
    ap.add_argument("--weeks", type=int, default=12)
    ap.add_argument("--end", default="2026-08-31",
                    help="data do instantaneo mais recente (AAAA-MM-DD)")
    ap.add_argument("--emit", default="pilot-label-intelligence/registry")
    args = ap.parse_args()

    end = datetime.date.fromisoformat(args.end)
    dates = [(end - datetime.timedelta(weeks=i)).strftime("%Y%m%d")
             for i in range(args.weeks)][::-1]

    metas = []
    for d in dates:
        m = fetch(d, args.outdir)
        metas.append(m)
        print(f'  {d}  {m["state"]:<12} {m.get("sha256","")[:16]} '
              f'{m.get("bytes","")}', file=sys.stderr)

    got = [m for m in metas if m["state"] == "DOWNLOADED"]
    if not got:
        print("nenhum instantaneo obtido", file=sys.stderr)
        return 1

    # Um documento e um sha256. Republicacao identica nao e versao nova.
    versions, seen = [], {}
    for m in got:
        if m["sha256"] in seen:
            seen[m["sha256"]]["republished_as"].append(m["date"])
            continue
        v = dict(m, republished_as=[])
        seen[m["sha256"]] = v
        versions.append(v)

    print(f'\n  instantaneos baixados : {len(got)}', file=sys.stderr)
    print(f'  documentos distintos  : {len(versions)}', file=sys.stderr)

    all_events, per_version = [], []
    bruto = normalizado = 0
    prev = None
    for v in versions:
        rows = read_rows(v["path"])
        idx = adama_rows(rows)
        active = {k: r for k, r in idx.items() if is_active(r)}
        per_version.append({
            "SNAPSHOT_DATE": v["date"],
            "VERSION_ID": v["sha256"][:16],
            "SHA256": v["sha256"],
            "BYTES": v["bytes"],
            "SOURCE_URL": v["url"],
            "REPUBLISHED_UNCHANGED_ON": v["republished_as"],
            "PRODUCTS_TOTAL": len(rows),
            "ADAMA_ROWS": len(idx),
            "ADAMA_ACTIVE": len(active),
        })
        if prev is not None:
            all_events += diff(prev[0], idx, prev[1], v)
            bruto += contar_diffs_de_campo(prev[0], idx, normalizar=False)
            normalizado += contar_diffs_de_campo(prev[0], idx, normalizar=True)
        prev = (idx, v)

    all_events = mark_oscillations(all_events)
    stable = [e for e in all_events if not e.get("UNSTABLE_SOURCE")]
    unstable = [e for e in all_events if e.get("UNSTABLE_SOURCE")]

    os.makedirs(args.emit, exist_ok=True)
    out = {
        "SOURCE": "Ministero della Salute — Banca dati prodotti fitosanitari",
        "SOURCE_PAGE": "https://www.dati.salute.gov.it/it/dataset/fitosanitari",
        "LICENSE": "Italian Open Data Licence v2.0",
        "DATASET": "PROD_FTS_6",
        "HOLDER_FILTER": HOLDER_MATCH,
        "SNAPSHOTS_REQUESTED": len(dates),
        "SNAPSHOTS_DOWNLOADED": len(got),
        "DISTINCT_DOCUMENTS": len(versions),
        "VERSION_IDENTITY_METHOD": "sha256 do CSV oficial; republicacao identica nao conta como versao",
        "MISSING_SNAPSHOTS": [m["date"] for m in metas if m["state"] != "DOWNLOADED"],
        "VERSIONS": per_version,
        "FIELD_DIFFS_WITHOUT_NORMALISATION": bruto,
        "FIELD_DIFFS_WITH_NORMALISATION": normalizado,
        "SERIALIZATION_NOISE_SUPPRESSED": bruto - normalizado,
        "NOISE_SHARE": round(100.0 * (bruto - normalizado) / bruto, 1) if bruto else 0,
        "NOISE_NOTE": ("os dois numeros contam a MESMA coisa — diferencas de campo entre "
                       "registros presentes nos dois instantaneos — e por isso sao comparaveis. "
                       "Entrada e saida de produto ficam fora dos dois. A fonte reordena a lista "
                       "de indicacoes de perigo entre publicacoes e o mesmo valor vai e volta; "
                       "um differ que comparasse texto cru entregaria o numero sem normalizar."),
        "CHANGE_EVENTS_TOTAL": len(all_events),
        "CHANGE_EVENTS_REGULATORY": len(stable),
        "CHANGE_EVENTS_TEXT_ONLY": len(unstable),
        "TEXT_ONLY_RULE": ("valor que reaparece no mesmo registro/campo indica fonte "
                           "oscilando; rebaixado a TEXT_CHANGE_OTHER e fora das "
                           "contagens regulatorias"),
        "CHANGE_EVENTS": all_events,
    }
    p = os.path.join(args.emit, "IT-REGISTRO-VERSOES.json")
    with open(p, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=1)
    print(f'  diffs de campo brutos : {bruto} -> normalizados {normalizado} '
          f'({bruto - normalizado} de ruido)', file=sys.stderr)
    print(f'  eventos regulatorios  : {len(stable)}', file=sys.stderr)
    print(f'  texto/instaveis       : {len(unstable)}', file=sys.stderr)
    print(f'  escrito               : {p}', file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
