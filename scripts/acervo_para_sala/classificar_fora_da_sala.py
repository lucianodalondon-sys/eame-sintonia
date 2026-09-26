#!/usr/bin/env python3
"""ACERVO-PARA-SALA · porque cada conteudo guardado NAO esta na Sala — so leitura, sem rede, sem banco.

Le os ficheiros tirados da Sala por SELECT so-leitura (raw_asset, derived_artifact, sala_de_espera_atual,
collection_run), o LIVRO-DE-DECISOES do vivo (os vereditos da Admissao, por derivado) e a previsao do
ACERVO-TEMPO-LUGAR (que diz, por sha256, se os bytes e o texto foram achados com o sha certo).

Cada conteudo (sha256 distinto) fora da Sala recebe UM motivo, pela ordem abaixo (o primeiro que se aplica):

  SEM_BYTES               nenhum ficheiro com o sha256 do banco foi achado em nenhuma raiz
  SEM_TEXTO:<especie>     nao ha derivado de texto (TEXT_EXTRACTION/TRANSCRIPTION): JSON, video, audio,
                          csv, ou HTML/PDF cuja extracao nao deu texto — a Admissao nao tem o que ler
  ADMISSAO:<resultado>:<regra>   a Admissao respondeu (a decisao MAIS RECENTE de qualquer derivado dele)
  NUNCA_PERGUNTADO:<rota> ha texto, nao ha decisao nenhuma no livro: o documento nunca foi a porta

e, a parte (nao exclusivo), MARCAS: YOUTUBE, MESMO_URL_DE_UM_DA_SALA, DUPLICADO_DE_URL.

    py scripts/acervo_para_sala/classificar_fora_da_sala.py --dados <pasta> --previsao <previsao.json> --saida <out.json>
"""
import argparse
import collections
import json
import os

TEXTUAIS = ("TEXT_EXTRACTION", "TRANSCRIPTION")


def rota_da_corrida(run_id):
    """A estrada que trouxe o RAW, pelo prefixo e pela forma do RUN_ID (o que o coletor escreve)."""
    r = str(run_id or "")
    if r.startswith("XX-"):
        return "PILOTO_SEM_PAIS (XX-)"
    if r.startswith("IT-"):
        return "CORRIDA_IT"
    return "OUTRA (%s)" % (r.split("-")[0] or "?")


def main():
    ap = argparse.ArgumentParser()
    for a in ("--dados", "--previsao", "--saida"):
        ap.add_argument(a, required=True)
    a = ap.parse_args()
    ler = lambda n: json.load(open(os.path.join(a.dados, n), encoding="utf-8"))
    raws, ders, sala = ler("raw.json"), ler("derivados.json"), ler("sala.json")
    livro = ler("LIVRO-DE-DECISOES.json")["DECISOES"]
    prev = {x["SHA256"]: x for x in json.load(open(a.previsao, encoding="utf-8"))["ITENS"]}

    der_por_raw = collections.defaultdict(list)
    for d in ders:
        der_por_raw[d["raw_asset_id"]].append(d)
    decisoes = collections.defaultdict(list)
    for x in livro:
        if str(x.get("item", "")).startswith("derived:"):
            decisoes[int(x["item"].split(":")[1])].append(x)
    der_na_sala = {int(s["item_id"].split(":")[1]) for s in sala if str(s["item_id"]).startswith("derived:")}

    por_sha = collections.OrderedDict()
    for r in raws:
        por_sha.setdefault(r["sha256"].strip(), []).append(r)
    url_da_sala = set()
    for sha, linhas in por_sha.items():
        if any(d["id"] in der_na_sala for rr in linhas for d in der_por_raw.get(rr["id"], [])):
            url_da_sala.update(rr["source_url"] for rr in linhas if rr.get("source_url"))
    conta_url = collections.Counter(linhas[0]["source_url"] for linhas in por_sha.values() if linhas[0].get("source_url"))

    itens = []
    for sha, linhas in por_sha.items():
        r = linhas[0]
        dd = [d for rr in linhas for d in der_por_raw.get(rr["id"], [])]
        if any(d["id"] in der_na_sala for d in dd):
            continue                                                   # esta na Sala
        p = prev.get(sha, {})
        textuais = [d for d in dd if d["kind"] in TEXTUAIS]
        decs = sorted((x for d in dd for x in decisoes.get(d["id"], [])), key=lambda x: x.get("quando") or "")
        url = r.get("source_url") or ""
        marcas = []
        if "youtube.com" in url or "youtu.be" in url:
            marcas.append("YOUTUBE")
        if url and url in url_da_sala:
            marcas.append("MESMO_URL_DE_UM_DA_SALA")
        if url and conta_url[url] > 1:
            marcas.append("DUPLICADO_DE_URL")
        if not p.get("BYTES"):
            motivo = "SEM_BYTES"
        elif not textuais:
            motivo = "SEM_TEXTO:%s" % (r["media_type"] or "?")
        elif decs:
            u = decs[-1]
            motivo = "ADMISSAO:%s:%s" % (u["resultado"], u["regra"])
        else:
            motivo = "NUNCA_PERGUNTADO:%s" % rota_da_corrida(r["run_id"])
        u = decs[-1] if decs else None
        itens.append({"SHA256": sha, "SOURCE_ID": r["source_id"], "CLASSE_T": (r["source_id"] or "?").split("-")[1] if "-" in (r["source_id"] or "") else "?",
                      "MEDIA_TYPE": r["media_type"], "URL": url[:160], "RAW_IDS": [x["id"] for x in linhas],
                      "RUN_IDS": sorted({x["run_id"] for x in linhas}), "DERIVADOS": [d["id"] for d in dd],
                      "DERIVADOS_DE_TEXTO": [d["id"] for d in textuais], "MOTIVO": motivo, "MARCAS": marcas,
                      "DECISAO": ({"ITEM": u["item"], "UNIVERSO": u["universo"], "RESULTADO": u["resultado"],
                                   "REGRA": u["regra"], "MOTIVO": (u.get("motivo") or "")[:200], "CORRIDA": u.get("corrida"),
                                   "QUANDO": u.get("quando"), "VERSAO": u.get("versao")} if u else None),
                      "N_DECISOES": len(decs)})

    def agrupa(chave):
        c = collections.Counter(chave(x) for x in itens)
        return dict(c.most_common())

    grosso = lambda m: m.split(":")[0] + (":" + m.split(":")[1] if m.startswith(("ADMISSAO", "SEM_TEXTO")) else "")
    out = collections.OrderedDict()
    out["DATASET"] = "ACERVO-PARA-SALA-MOTIVOS-V1"
    out["FORA_DA_SALA"] = len(itens)
    out["POR_MOTIVO"] = agrupa(lambda x: x["MOTIVO"])
    out["POR_MOTIVO_GROSSO"] = agrupa(lambda x: grosso(x["MOTIVO"]))
    out["MARCAS"] = dict(collections.Counter(m for x in itens for m in x["MARCAS"]).most_common())
    out["POR_CLASSE_T_E_MOTIVO"] = {}
    for x in itens:
        out["POR_CLASSE_T_E_MOTIVO"].setdefault(x["CLASSE_T"], collections.Counter())[grosso(x["MOTIVO"])] += 1
    out["POR_CLASSE_T_E_MOTIVO"] = {k: dict(v.most_common()) for k, v in sorted(out["POR_CLASSE_T_E_MOTIVO"].items())}
    fontes = collections.defaultdict(collections.Counter)
    for x in itens:
        fontes[x["SOURCE_ID"]][grosso(x["MOTIVO"])] += 1
    out["POR_FONTE"] = {k: dict(v.most_common()) for k, v in sorted(fontes.items(), key=lambda kv: -sum(kv[1].values()))}
    out["ITENS"] = itens
    with open(a.saida, "w", encoding="utf-8", newline="\n") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    print(json.dumps({k: out[k] for k in ("FORA_DA_SALA", "POR_MOTIVO_GROSSO", "MARCAS", "POR_MOTIVO")}, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
