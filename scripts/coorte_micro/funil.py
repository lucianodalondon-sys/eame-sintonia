"""G0 — a coorte da micro-coleta no universo inteiro: funil A→E.

    py scripts/coorte_micro/funil.py --snap=<copia do servico vivo> [--escrever]

So leitura. O servico vivo so por COPIA (--snap). Nao toca micro_coleta.py
(importa-o, nao o muda), catalogo, Admission ou detector.

UNIVERSO = READY do livro vivo ∪ ELIGIBLE do gate desta linha ∪ as 15 da M3 ∪
           as 121 do censo das receitas (deduplicado por SOURCE_ID).
           Candidatas sem SOURCE_ID ficam fora: nao ha contrato a medir.

DEGRAUS (cada fonte leva o primeiro que falha; os seguintes medem-se na mesma):
  A  READY — no livro vivo (canario do worker) OU READY_CURRENT nesta linha
     (regua dos 4 passos). READY_LEGACY sozinho nao passa (o gate recusa-o).
     Os dois ficam escritos; nao se decide qual manda (e da M5).
  B  rota EXECUTABLE — contrato na tabela do coletor (regras/italy_contracts_onboarded.json)
     + receita web para o universo (pedido/receitas.py -> italy_executor) + sem
     CAPABILITY/POLICY/AUTH block no livro vivo nem na M3. Senao BLOCK_REASON:
     NEEDS_CONTRACT · MISSING_ROUTE · CAPABILITY_BLOCK · POLICY_BLOCK · AUTH_BLOCK
  C  a receita reconhece noticia REAL — uma materia lida da fonte casa o
     LINK_PATTERN que o coletor usa (o da tabela do coletor; senao o do Curator).
     Sem materia lida: UNKNOWN (nao passa: nao se sabe).
  D  relevancia (D2 do dono): SINTONIA_RELEVANT = YES — pela decisao da 3b,
     do dono (gabarito) ou pela leitura da materia (ROTULOS-RELEVANCIA-G0.json).
     O idioma nao exclui (D3).
  E  nao e propaganda de marca. DEPOIS DA D8 (23/09) NAO CORTA: as 3 de propaganda
     (IT-T7-017, IT-T7-033, IT-T7-042) ficam e sao julgadas pagina a pagina — so passa
     em D a noticia com facto de mercado (D8_FACTO_DE_MERCADO no rotulo).
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
from collections import Counter
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "curadoria"))
sys.path.insert(0, str(RAIZ / "scripts" / "micro_coleta"))
sys.path.insert(0, str(RAIZ / "scripts" / "receitas"))
import micro_coleta as MC        # noqa: E402  so leitura: receita_web, universo_de
import censo_e_proposta as CP    # noqa: E402  paginas com veredito
import collection_gate as GATE   # noqa: E402

MARCA = {"IT-T7-017", "IT-T7-033", "IT-T7-042"}
BLOQUEIOS_VIVOS = {"CAPABILITY_BLOCK": "CAPABILITY_BLOCK", "POLICY_BLOCK": "POLICY_BLOCK",
                   "AUTH_BLOCK": "AUTH_BLOCK", "CONTRACT_READY_ROUTE_BLOCKED": "POLICY_BLOCK"}
SAIDA = AQUI / "FUNIL-COORTE-MICRO-V1.json"


def git_json(ref_caminho: str) -> dict:
    r = subprocess.run(["git", "show", ref_caminho], cwd=RAIZ, capture_output=True)
    if r.returncode != 0:
        raise SystemExit(f"FALTA {ref_caminho}: {r.stderr.decode('utf-8', 'replace')[:200]}")
    return json.loads(r.stdout.decode("utf-8"))


def carregar(snap: Path, livro: Path | None = None, tabela: Path | None = None) -> dict:
    T = json.loads((snap / "LIFECYCLE-LEDGER-V1.json").read_text(encoding="utf-8"))["TRANSICOES"]
    ultimo = {}
    for t in T:
        ultimo[t["SOURCE_ID"]] = t
    curador = {f["SOURCE_ID"]: f for f in json.loads(
        Path(livro or snap / "italy_contracts_curator.json").read_text(encoding="utf-8"))["FONTES"]}
    onboarded = {f["SOURCE_ID"]: f for f in json.loads(
        Path(tabela or RAIZ / "regras/italy_contracts_onboarded.json").read_text(encoding="utf-8"))["FONTES"]}
    m3 = {l["SOURCE_ID"]: l["VEREDITO"] for l in
          git_json("origin/rotas-elegiveis-v1:curadoria/ROTAS-ELEGIVEIS-V1.json")["LINHAS"]}
    ctx = GATE._contexto()
    linha = {l["SOURCE_ID"]: l for l in GATE.inventario(ctx=ctx)}
    universo = json.loads((snap / "universo.json").read_text(encoding="utf-8"))
    rel3b = git_json("origin/relevancia-elegiveis-v1:curadoria/RELEVANCIA-ELEGIVEIS-V1.json")
    rel3b_md = subprocess.run(["git", "show", "origin/relevancia-elegiveis-v1:RELATORIO-RELEVANCIA-ELEGIVEIS.md"],
                              cwd=RAIZ, capture_output=True).stdout.decode("utf-8")
    dec3b = {m.group(1): m.group(2) for m in
             (re.match(r"^\|\s*(IT-T\d+-\d+)\b.*\|\s*\*\*([A-Z_]+)\*\*\s*\|[^|]*\|\s*$", l.strip())
              for l in rel3b_md.splitlines()) if m}
    rot = json.loads((AQUI / "ROTULOS-RELEVANCIA-G0.json").read_text(encoding="utf-8"))["FONTES"] \
        if (AQUI / "ROTULOS-RELEVANCIA-G0.json").exists() else {}
    paginas = CP.paginas()
    paragens, visitadas, dominios = {}, set(), set()
    for mf in (Path.home() / "coorte-paginas" / "MANIFESTO.json",
               Path.home() / "receitas-paginas" / "MANIFESTO.json",
               Path.home() / "detector-capa-gabarito" / "MANIFESTO.json"):
        if mf.exists():
            for r in json.loads(mf.read_text(encoding="utf-8"))["REGISTO"]:
                visitadas.add(r["SOURCE_ID"])
                if r.get("HOST"):
                    dominios.add(r["HOST"].lower().removeprefix("www."))
                if r.get("PAROU"):
                    paragens.setdefault(r["SOURCE_ID"], str(r["PAROU"])[:60])
    pc = Path.home() / "coorte-paginas"
    if (pc / "MANIFESTO.json").exists():
        m = json.loads((pc / "MANIFESTO.json").read_text(encoding="utf-8"))["PAGINAS"]
        rp = json.loads((AQUI / "ROTULOS-PAGINAS-COORTE-G0.json").read_text(encoding="utf-8"))["ROTULOS"]
        for i, p in enumerate(m):
            paginas.append({"SOURCE_ID": p["SOURCE_ID"], "URL": p["URL"], "VEREDITO": rp[str(i)][0],
                            "PAPEL": p["PAPEL_CANDIDATO"], "BYTES": pc / p["FICHEIRO"],
                            "ORIGEM": f"coorte#{i}"})
    return dict(ultimo=ultimo, curador=curador, onboarded=onboarded, m3=m3, linha=linha,
                universo=universo["UNIVERSO"], dec3b=dec3b, rot=rot,
                n3b=len(rel3b["FONTES"]), paginas=paginas, paragens=paragens,
                visitadas=visitadas, dominios=dominios)


def avaliar(sid: str, D: dict) -> dict:
    u = MC.universo_de(sid)
    v = D["ultimo"].get(sid, {})
    l = D["linha"].get(sid, {})
    r = {"SOURCE_ID": sid, "UNIVERSO": u, "ESTADO_VIVO": v.get("NEW_STATE", "SEM_HISTORIA"),
         "RAZAO_VIVO": str(v.get("REASON", ""))[:120], "READY_RULE_LINHA": l.get("READY_RULE"),
         "GATE_LINHA": l.get("MOTIVO")}
    # A
    a_vivo = r["ESTADO_VIVO"] == "READY_FOR_COLLECTION"
    a_linha = l.get("READY_RULE") == "DETAIL/v1"
    r["A"] = a_vivo or a_linha
    r["A_PORQUE"] = ("VIVO(canario do worker)" if a_vivo else "") + \
                    (" LINHA(regua dos 4 passos)" if a_linha else "") or \
                    (f"LINHA so READY_LEGACY" if l.get("READY_RULE") else f"vivo={r['ESTADO_VIVO']}")
    # B
    c = D["curador"].get(sid)
    bloq = BLOQUEIOS_VIVOS.get(r["ESTADO_VIVO"]) or \
        {"CAPABILITY_BLOCK": "CAPABILITY_BLOCK", "UNKNOWN": None}.get(D["m3"].get(sid))
    if bloq:
        r["B"], r["B_PORQUE"] = False, bloq
    elif sid not in D["onboarded"]:
        r["B"], r["B_PORQUE"] = False, "NEEDS_CONTRACT (fora da tabela do coletor)" + \
            (" — rota provada pela M3, por aplicar" if D["m3"].get(sid) == "ROUTE_PROVEN" else "")
    elif MC.receita_web(u) is None:
        r["B"], r["B_PORQUE"] = False, f"MISSING_ROUTE (sem receita web para {u})"
    else:
        r["B"], r["B_PORQUE"] = True, "EXECUTABLE"
    # C
    aq = (D["onboarded"].get(sid) or c or {}).get("ACQUISITION") or {}
    lp = aq.get("LINK_PATTERN")
    mats = [p["URL"] for p in D["paginas"] if p["SOURCE_ID"] == sid and p["VEREDITO"] == "MATERIA"]
    r["MATERIAS_LIDAS"] = mats
    if not mats:
        par = D.get("paragens", {}).get(sid)
        if par and "ROBOTS" in par:
            motivo = "ROBOTS_NEGA — politica do site; nao se contorna"
        elif par:
            motivo = f"visitada sem materia ({par})"
        elif sid not in D["curador"]:
            motivo = "sem contrato no livro vivo: nao ha onde ir"
        elif sid in D.get("visitadas", set()):
            motivo = "visitada: a pagina-alvo era capa, nao materia"
        elif (lambda h: h in D.get("dominios", set()))(
                ((c.get("ACQUISITION") or {}).get("INDEX_URL", "").split("/")[2:3] or [""])[0].lower().removeprefix("www.")):
            motivo = "dominio ja visitado por outra fonte: teto de 3 pedidos por site gasto"
        else:
            motivo = "PRECISA_REDE_IT"
        r["C"], r["C_PORQUE"] = False, f"UNKNOWN (nenhuma materia lida) — {motivo}"
    elif lp and any(re.match(lp, m) for m in mats):
        r["C"], r["C_PORQUE"] = True, "a receita casa materia lida"
    else:
        r["C"], r["C_PORQUE"] = False, "a receita nao casa a materia lida"
    # D
    d3b = D["dec3b"].get(sid)
    rot = D["rot"].get(sid)
    if rot:
        r["SINTONIA_RELEVANT"], r["D_PORQUE"] = rot["SINTONIA_RELEVANT"], "leitura G0: " + rot["PORQUE"]
        r["UNIVERSE_MATCH"], r["ACTION"] = rot.get("UNIVERSE_MATCH"), rot.get("ACTION")
    elif d3b:
        r["SINTONIA_RELEVANT"] = "YES" if d3b == "ENTRA_NA_MICRO" else f"3b:{d3b}"
        r["D_PORQUE"] = f"decisao da 3b: {d3b}"
    else:
        r["SINTONIA_RELEVANT"], r["D_PORQUE"] = "NAO_SEI", "nao medida"
    r["D"] = r["SINTONIA_RELEVANT"] == "YES"
    # D8 (23/09): as 3 de propaganda FICAM, julgadas pagina a pagina; so passa
    # NOTICIA com facto de mercado. Sem esse facto provado, nao passa D.
    if sid in MARCA:
        f8 = str((rot or {}).get("D8_FACTO_DE_MERCADO", "NAO_SEI"))
        r["D8"] = f8
        r["D"] = r["D"] and f8.startswith("YES")
    # E — depois da D8 a marca deixa de cortar aqui (fica como anotacao)
    r["E"] = True
    # o primeiro degrau que falha
    r["PARA_EM"] = next((k for k in "ABCDE" if not r[k]), "PASSA")
    return r


def passa(l: dict) -> bool:
    return all(l[k] for k in "ABCDE")


def desbloqueios(linhas: list[dict], D: dict) -> list[dict]:
    """Cada desbloqueio aplicado EM MEMORIA, sem baixar regua nenhuma: so
    remove um bloqueio que tem dono e decisao conhecidos. Mede-se o ganho
    marginal (sozinho) e o acumulado (por ordem de rendimento)."""
    prop = json.loads((RAIZ / "curadoria/PROPOSTA-RECEITAS-V1.json").read_text(encoding="utf-8"))
    novo_lp = {l["SOURCE_ID"]: p["DEPOIS"] for l in prop["FONTES"] for p in l["PROPOSTAS"]
               if p["CAMPO"] == "ACQUISITION.LINK_PATTERN"}

    def u1(l):   # aplicar a PROPOSTA-RECEITAS-V1 (6-PREP-d, com prova)
        if not l["C"] and l["SOURCE_ID"] in novo_lp and l["MATERIAS_LIDAS"] and \
                all(re.match(novo_lp[l["SOURCE_ID"]], m) for m in l["MATERIAS_LIDAS"]):
            l["C"] = True

    def u2(l):   # aplicar o onboarding das rotas provadas pela M3 (tabela do coletor)
        if not l["B"] and "M3, por aplicar" in l["B_PORQUE"] and MC.receita_web(l["UNIVERSO"]):
            l["B"] = True

    v2 = RAIZ / "curadoria/PROPOSTA-RECEITAS-V2.json"
    novo_v2 = {l["SOURCE_ID"]: p["DEPOIS"] for l in (json.loads(v2.read_text(encoding="utf-8"))["FONTES"]
               if v2.exists() else []) for p in l["PROPOSTAS"] if p["CAMPO"] == "ACQUISITION.LINK_PATTERN"}

    def u4(l):   # contrato novo na tabela do coletor (sem prova M3: exige canario) + receita V2 se houver
        if not l["B"] and l["B_PORQUE"].startswith("NEEDS_CONTRACT") and "M3" not in l["B_PORQUE"]                 and MC.receita_web(l["UNIVERSO"]):
            l["B"] = True
            if not l["C"] and l["SOURCE_ID"] in novo_v2 and l["MATERIAS_LIDAS"] and                     all(re.match(novo_v2[l["SOURCE_ID"]], m) for m in l["MATERIAS_LIDAS"]):
                l["C"] = True

    acoes = [("APLICAR_PROPOSTA_RECEITAS_V1", "Curator/rotas, depois da M5", u1),
             ("ONBOARDAR_CONTRATO_NOVO_COM_CANARIO_E_RECEITA_V2", "Curator + coordenador (canario novo)", u4),
             ("APLICAR_ONBOARDING_M3", "coordenador (onboardar_rotas_provadas.py --aplicar), depois da M5", u2)]
    base = {l["SOURCE_ID"] for l in linhas if passa(l)}
    out = []
    for nome, dono, f in acoes:
        cop = [dict(l) for l in linhas]
        for l in cop:
            f(l)
        ganho = sorted({l["SOURCE_ID"] for l in cop if passa(l)} - base)
        out.append({"DESBLOQUEIO": nome, "DONO": dono, "GANHO_SOZINHO": len(ganho), "FONTES": ganho})
    out.sort(key=lambda x: -x["GANHO_SOZINHO"])
    cop, acum = [dict(l) for l in linhas], set(base)
    for o in out:
        f = next(a[2] for a in acoes if a[0] == o["DESBLOQUEIO"])
        for l in cop:
            f(l)
        acum |= {l["SOURCE_ID"] for l in cop if passa(l)}
        o["ACUMULADO"] = len(acum)
        o["ACUMULADO_FONTES"] = sorted(acum)
    return out


def main(argv=None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    snap = Path(next(a.split("=", 1)[1] for a in argv if a.startswith("--snap=")))
    op = {k: next((Path(a.split("=", 1)[1]) for a in argv if a.startswith(f"--{k}=")), None)
          for k in ("livro", "tabela")}
    D = carregar(snap, **op)
    linhas = [avaliar(s, D) for s in D["universo"]]
    funil, vivos = {}, linhas
    for k in "ABCDE":
        vivos = [l for l in vivos if l[k]]
        funil[k] = len(vivos)
    so = {k: sum(1 for l in linhas if l[k]) for k in "ABCDE"}
    out = {"DATASET": "FUNIL-COORTE-MICRO-V1", "UNIVERSO": len(linhas), "FUNIL_EM_CADEIA": funil,
           "CADA_DEGRAU_SOZINHO": so, "PARA_EM": dict(Counter(l["PARA_EM"] for l in linhas)),
           "PASSAM_TUDO": [l["SOURCE_ID"] for l in linhas if l["PARA_EM"] == "PASSA"],
           "DESBLOQUEIOS": desbloqueios(linhas, D),
           "FONTES": linhas}
    saida = next((Path(a.split("=", 1)[1]) for a in argv if a.startswith("--saida=")), SAIDA)
    if "--escrever" in argv:
        saida.write_text(json.dumps(out, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(json.dumps({k: v for k, v in out.items() if k != "FONTES"}, ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
