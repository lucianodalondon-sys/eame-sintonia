import json, urllib.request, urllib.parse, sys, time

BASE = "https://www.venetoagricoltura.org/myportal/AVPISP"
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36")


def post(path, payload, params):
    url = BASE + path + "?" + urllib.parse.urlencode(params)
    body = json.dumps(payload).encode()
    req = urllib.request.Request(url, data=body, method="POST", headers={
        "User-Agent": UA, "Content-Type": "application/json", "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=90) as r:
        raw = r.read()
    return r.status, len(raw), json.loads(raw.decode("utf-8", "replace"))


def get(path, params):
    url = BASE + path + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=90) as r:
        raw = r.read()
    return r.status, len(raw), json.loads(raw.decode("utf-8", "replace"))


def adv(attrs, page=1, size=1):
    return post("/api/search-advanced", {"preconditions": {}, "attributes": attrs},
                {"page": page, "pageSize": size})


TERMS = ["vite", "viticoltura", "peronospora", "oidio", "difesa", "bollettino",
         "fitosanitario", "Plasmopara", "botrite", "flavescenza"]

if __name__ == "__main__":
    mode = sys.argv[1]
    if mode == "counts":
        out = {}
        for t in TERMS:
            row = {}
            for field, rend in [("sys_title", "TEXT"), ("sys_description", "HTMLAREA"),
                                ("sys_name", "TEXT")]:
                try:
                    st, n, d = adv({field: {"type": rend, "value": t}})
                    row[field] = d["page"]["entitiesCount"]
                except Exception as e:
                    row[field] = "ERR:" + str(e)[:80]
                time.sleep(0.3)
            try:
                st, n, d = get("/api/search", {"query": t, "page": 1, "pageSize": 1})
                row["federated_api_search"] = d["page"]["entitiesCount"]
            except Exception as e:
                row["federated_api_search"] = "ERR:" + str(e)[:80]
            out[t] = row
            print(t, row, flush=True)
        json.dump(out, open("counts.json", "w"), indent=1)
    elif mode == "control":
        # control terms: must be 0 if the filter really filters
        for t in ["zzqqxx", "peronosporaXX", ""]:
            try:
                st, n, d = adv({"sys_title": {"type": "TEXT", "value": t}})
                print(repr(t), d["page"]["entitiesCount"])
            except Exception as e:
                print(repr(t), "ERR", e)
        st, n, d = adv({})
        print("no-attrs baseline", d["page"]["entitiesCount"])
