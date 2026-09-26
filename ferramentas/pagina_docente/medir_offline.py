# -*- coding: utf-8 -*-
"""PAGINA-DO-DOCENTE · a medida SEM REDE: os leitores sobre as paginas reais que ja temos.

    py ferramentas/pagina_docente/medir_offline.py --p5=<EVIDENCIA-P5.json> --bytes=<pasta p5-evidencia>
       --pessoas=<PESSOAS-ORDENADAS.json> --extra=<pasta vozes-agronomos> --saida=<MEDIDA-OFFLINE.json>

1. Por FORMA medida (Milano, Palermo, Verona, Padova, Udine): quantas paginas reais de docente trazem
   algum canal/pagina propria DENTRO do bloco da pessoa (a moldura do site fora).
2. Para os 63: quem ja se acha nas LISTAS guardadas (sem pedido nenhum), e quem ja tem a pagina guardada
   (le-se ja).
3. Para as universidades com a casa do site guardada: o link para a lista de pessoas.
Sai so: nomes publicos (MUR), enderecos publicos e contagens. Nenhum e-mail/telefone.
"""
import hashlib
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import leitor as L                                                    # noqa: E402
import universidades as U                                             # noqa: E402

FORMA_DO_URL = [("MILANO", r"www\.unimi\.it/it/ugov/rubrica/person"), ("PALERMO", r"unipa\.it/persone/docenti/[a-z]/"),
                ("VERONA", r"dbt\.univr\.it/\?ent=persona&id="), ("PADOVA", r"unipd\.it/category/ruoli/personale-docente\?key="),
                ("UDINE", r"cercapersone_detail\?person-id=")]
LISTAS = {"MILANO": "https://disaa.unimi.it/it/dipartimento/contatti/persone",
          "PALERMO": "https://www.unipa.it/dipartimenti/saaf/?pagina=personale&ruolo=docenti",
          "VERONA": "https://www.dbt.univr.it/?ent=persona",
          "PADOVA": ["https://www.dafnae.unipd.it/category/ruoli/personale-docente",
                     "https://www.tesaf.unipd.it/category/ruoli/personale-docente"],
          "UDINE": "https://di4a.uniud.it/it/cercapersone/cercapersone_dept?afferenza=107404"}


def main(argv) -> int:
    arg = dict(a[2:].split("=", 1) for a in argv[1:] if a.startswith("--") and "=" in a)
    ev = [x for x in json.loads(Path(arg["p5"]).read_text(encoding="utf-8"))["PAGINAS"] if x.get("URL")]
    pasta = Path(arg["bytes"])
    pagina = {}
    for x in ev:
        f = pasta / Path(x["FICHEIRO"].replace("\\", "/")).name
        if f.exists():
            b = f.read_bytes()
            if hashlib.sha256(b).hexdigest() == x["SHA256"]:
                pagina.setdefault(x["URL"], (b.decode("utf-8", "replace"), x["SHA256"]))
    out = {"DATASET": "PAGINA-DOCENTE-MEDIDA-OFFLINE", "REDE": 0,
           "FONTE_DOS_BYTES": "P5 pessoas-docentes-v1 (EVIDENCIA-P5.json, 24/09/2026), sha256 conferido", "FORMAS": {},
           "PESSOAS": [], "DESCOBERTA_NA_CASA": {}}
    # 1 · por forma
    por = defaultdict(list)
    for url, (html, sha) in pagina.items():
        for uni, rx in FORMA_DO_URL:
            if re.search(rx, url):
                por[uni].append((html, url, sha))
    for uni, ps in sorted(por.items()):
        mold = L.gabarito([(h, u) for h, u, _ in ps])
        c, plats, blocos, ex = Counter(), Counter(), Counter(), []
        for html, url, _ in ps:
            r = L.ler_pagina(html, url, uni, mold)
            blocos[r["BLOCO"]] += 1
            if r["CANAIS"] or r["NAO_ENTRAM"]:
                c["COM_CANAL_OU_PERFIL"] += 1
            if r["CANAIS"]:
                c["COM_CANAL_QUE_ENTRA"] += 1
            if r["PAGINAS_PROPRIAS"]:
                c["COM_PAGINA_PROPRIA_NO_DOMINIO"] += 1
            if r["EXTERNOS_SEM_ROTULO"]:
                c["COM_EXTERNO_SEM_ROTULO"] += 1
            for x in r["CANAIS"] + r["NAO_ENTRAM"]:
                plats[x["PLATAFORMA"]] += 1
                ex.append({"PAGINA": url, "URL": x["URL"], "PLATAFORMA": x["PLATAFORMA"]})
        out["FORMAS"][uni] = {"PAGINAS_REAIS": len(ps), "BLOCO": dict(blocos), "CONTAGEM": dict(c),
                              "PLATAFORMAS": dict(plats), "EXEMPLOS": ex[:12]}
    # 2 · os 63
    P = json.loads(Path(arg["pessoas"]).read_text(encoding="utf-8"))
    prio = [p for p in P["PESSOAS"] if p.get("PRIORIDADE") is True]
    for p in prio:
        uni = p["UNIVERSIDADE"]
        linha = {"ORDEM": p["ORDEM"], "NOME": p["NOME"], "UNIVERSIDADE": uni, "DEPARTAMENTO": p.get("DEPARTAMENTO"),
                 "LEITOR": U.UNIVERSIDADES[uni]["FORMA"] if uni in U.UNIVERSIDADES else "FORA_DAS_19"}
        if uni not in U.UNIVERSIDADES:
            linha["ESTADO"] = "FORA_DAS_19 (sem universidade MUR: %s)" % uni[:60]
            out["PESSOAS"].append(linha)
            continue
        listas = LISTAS.get(uni)
        listas = [U.entrada_para(uni, p.get("DEPARTAMENTO"))] if isinstance(listas, list) else ([listas] if listas else [])
        achado = None
        for lu in listas:
            if lu in pagina:
                achado = L.achar_pessoa(pagina[lu][0], lu, p, uni)
                linha["LISTA_GUARDADA"] = lu
                break
        if achado is None:
            linha["ESTADO"] = "SEM_BYTES (a lista pede rede)"
        else:
            linha["ESTADO"] = "NA_LISTA_GUARDADA: " + achado["ESTADO"]
            if achado["ESTADO"] == "NAO_ACHEI":
                linha["NOTA"] = ("so a 1.a pagina da lista esta guardada (lista em paginas): a rodada segue as outras"
                                 if U.UNIVERSIDADES[uni].get("PAGINACAO") else
                                 "a lista guardada e de outro departamento: a rodada tenta a regra de endereco medida"
                                 if U.UNIVERSIDADES[uni].get("CONSTRUIR") else "NAO SEI")
            linha["URLS"] = achado["URLS"]
            url = achado.get("URL")
            if url and url in pagina:
                r = L.ler_pagina(pagina[url][0], url, uni, L.gabarito([(h, u) for h, u, _ in por[uni]]))
                linha["PAGINA_GUARDADA_LIDA"] = {k: r[k] for k in ("BLOCO", "CANAIS", "NAO_ENTRAM", "PAGINAS_PROPRIAS",
                                                                    "EXTERNOS_SEM_ROTULO")}
                linha["PAGINA_GUARDADA_LIDA"]["NOME_CONFERE"] = L.nome_confere(pagina[url][0], p, uni)
                linha["PAGINA_GUARDADA_SHA256"] = pagina[url][1]
        out["PESSOAS"].append(linha)
    # 3 · casas guardadas (acervo/ronda 1): o link para a lista
    extra = Path(arg["extra"]) if arg.get("extra") else None
    casas = {"Napoli Federico II": ("V17", "https://www.agraria.unina.it/"),
             "PADOVA": ("V03", "https://www.dafnae.unipd.it/"), "MILANO": ("V04", "https://disaa.unimi.it/")}
    for uni, (v, base) in casas.items():
        f = extra / v / "1_ALVO.bin" if extra else None
        if f and f.exists():
            out["DESCOBERTA_NA_CASA"][uni] = {"PAGINA": "%s/1_ALVO.bin (ronda 1)" % v,
                                              "LISTAS": L.descobrir_lista(f.read_bytes().decode("utf-8", "replace"), base, uni)[:5]}
    Path(arg["saida"]).write_text(json.dumps(out, ensure_ascii=False, indent=1) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({k: {"paginas": v["PAGINAS_REAIS"], **v["CONTAGEM"], "bloco": v["BLOCO"]} for k, v in out["FORMAS"].items()},
                     ensure_ascii=False, indent=1))
    print(Counter(x["ESTADO"] for x in out["PESSOAS"]))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
