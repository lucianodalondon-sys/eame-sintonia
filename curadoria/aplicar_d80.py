#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""D80 (26/09, bot Luciano por delegacao do dono) — a parte (i) pela porta, e as
tarefas que (ii) e (iii) precisam de volta na fila. Com o ROBO PARADO: um so escritor.

    py curadoria/aplicar_d80.py --montar=<BLOQUEADAS-268-V1.json>   # congela a lista (feito no ramo)
    py curadoria/aplicar_d80.py                                      # A SECO: diz o que faria, nao grava
    py curadoria/aplicar_d80.py --aplicar  --recibo=<fora do Git>    # (i) + reabre as QUALIFY
    py curadoria/aplicar_d80.py --reverter --recibo=<fora do Git>    # desfaz (i) + reabre as QUALIFY
    ... [--mae=<host>=<SOURCE_ID>]   # a mae de um site com varias fontes, se o dono a disser

(i)   As 113 da BLOQUEADAS-268 que a leitura propos retirar. Cada uma recusada pela
      PORTA (`fonte_nova.recusar`, decisao «D80(i)»), com motivo proprio, a duplicada
      ligada a fonte canonica (DUPLICADA_DE), nada apagado, reversivel. Duvida -> NAO SEI
      (nao se recusa): «talvez seja a mesma» (IDENTIDADE_DUPLICADA_POSSIVEL) e a
      duplicada cuja mae nao se acha sozinha.
(ii)  O QUALIFY cunha o prefixo canonico (EU-/INT-/<pais>-) e PARA. A ferramenta so
      reabre as QUALIFY barradas por «territorio decidido fora de IT».
(iii) O QUALIFY herda a classe do mesmo site. A ferramenta so reabre as QUALIFY
      barradas por «territorio indeterminado pelo nome».
A lista final por fonte (o que o robo fez com cada uma) sai do ENSAIO, nao daqui.
"""
from __future__ import annotations

import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "curadoria"))
sys.path.insert(0, str(RAIZ / "candidatas"))

import fila as F                      # noqa: E402
import fonte_nova as FN               # noqa: E402
import linkedin_pelo_site as LPS      # noqa: E402
import rota_do_scrap_youtube as RSY   # noqa: E402
import decisao_semantica as DS        # noqa: E402

LISTA = RAIZ / "curadoria" / "D80-LISTA-V1.json"
ALLOCATION = RAIZ / "curadoria" / "SOURCE-ID-ALLOCATION-V1.json"
DECISAO = "D80(i)"
REABRIR = ["territorio decidido fora de IT", "territorio indeterminado pelo nome"]
REABRIR_AO_REVERTER = ["RECUSADA pela porta de entrada"]

# Leitura a mao de 25/09 (BLOQUEADAS-268, `MAO_MESMO_SITE`): a casa do site ja e esta fonte.
MAE_LIDA_A_MAO = {"CAND-0720": "IT-T8-033", "CAND-0942": "IT-T2-149", "CAND-1023": "IT-T8-061",
                  "CAND-1025": "IT-T8-062", "CAND-1047": "IT-T8-065", "CAND-1050": "IT-T8-064",
                  "CAND-1052": "IT-T8-067", "CAND-1060": "IT-T1-022"}
DUVIDA = {"IDENTIDADE_DUPLICADA_POSSIVEL"}
RE_ID = re.compile(r"\b(?:[A-Z]{2,3}-T\d+-\d{3}|CAND-\d{4})\b")


def _ler(p: Path) -> dict:
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else {}


def _norm(u: str) -> str:
    return FN.normalizar(u)


def _fontes_do_host(host: str, tabela: dict, livro: dict, atlas: str) -> dict:
    """{SOURCE_ID: URL de entrada} das fontes da casa neste host (tabela, livro, Atlas)."""
    por_sid = RSY._territorios_do_host(host, tabela, livro, atlas)
    entradas = {}
    for doc in (tabela, livro):
        for c in doc.get("FONTES") or []:
            if c["SOURCE_ID"] in por_sid:
                entradas.setdefault(c["SOURCE_ID"], (c.get("ACQUISITION") or {}).get("INDEX_URL")
                                    or c.get("CANONICAL_ENTRY_URL") or "")
    return {s: entradas.get(s, "") for s in por_sid}


def _raiz(url: str) -> bool:
    u = urlparse(url if "://" in url else "https://" + url)
    return u.path.strip("/").lower() in RSY.RAIZES_DE_SITE and not u.query


def mae(cand: str, url: str, nomeados: list[str], casa: tuple, alloc: dict,
        maes_do_dono: dict) -> tuple[str | None, str]:
    """(fonte canonica, como se achou) ou (None, porque fica NAO SEI). Mais forte primeiro."""
    tabela, livro, atlas = casa
    host = LPS.host(url)
    do_host = _fontes_do_host(host, tabela, livro, atlas)
    iguais = sorted(s for s, e in do_host.items() if e and _norm(e) == _norm(url))
    if len(iguais) == 1:
        return iguais[0], "o mesmo endereco ja e a entrada de %s" % iguais[0]
    sid_da_cand = {n["CANDIDATE_ID"]: n["SOURCE_ID"] for n in alloc.get("NOVAS", [])}
    nomeados = [sid_da_cand.get(n, n) for n in nomeados]
    no_host = [n for n in dict.fromkeys(nomeados) if n in do_host]
    if len(no_host) == 1:
        return no_host[0], "nomeada na leitura e do mesmo site %s" % host
    if cand in MAE_LIDA_A_MAO and MAE_LIDA_A_MAO[cand] in do_host:
        return MAE_LIDA_A_MAO[cand], "leitura a mao de 25/09: a casa do site %s ja e a fonte" % host
    if host in maes_do_dono:
        return maes_do_dono[host], "mae do site %s dita pelo dono (--mae)" % host
    raizes = sorted(s for s, e in do_host.items() if e and _raiz(e))
    if len(raizes) == 1:
        return raizes[0], "a fonte de %s cuja entrada e a raiz do site" % host
    if len(do_host) == 1:
        return next(iter(do_host)), "a unica fonte da casa no site %s" % host
    cands = [n for n in dict.fromkeys(nomeados) if n.startswith("CAND-")]
    if len(cands) == 1 and not do_host:
        return cands[0], "nomeada na leitura (candidata da organizacao, ainda sem numero)"
    if do_host:
        return None, "o site %s tem %d fontes (%s) e nenhuma e a mae provada" % (
            host, len(do_host), ", ".join(sorted(do_host)))
    return None, "a fonte canonica nao se acha sem adivinhar"


def montar(bloqueadas: Path) -> dict:
    bl = _ler(bloqueadas)
    ds = {d["CANDIDATA_ID"]: d for d in DS._ler()}
    fichas = {c["CANDIDATA_ID"]: c for c in FN.carregar()["CANDIDATAS"]}
    casa = (_ler(RSY.TABELA), _ler(RSY.LIVRO),
            RSY.ATLAS.read_text(encoding="utf-8") if RSY.ATLAS.exists() else "")
    alloc = _ler(ALLOCATION)
    vistas, linhas = set(), []
    for l in bl["LINHAS"]:
        grupo = l.get("LEITURA_A_MAO") if l.get("LEITURA_A_MAO") == "DUPLICADA_DA_ORGANIZACAO" else (
            l["PROPOSTA"] if l["PROPOSTA"] in ("PROPOR_RECUSA", "DUPLICADA_DE") else None)
        if not grupo or l["ID"] in vistas:
            continue
        vistas.add(l["ID"])
        cand, f, d = l["ID"], fichas.get(l["ID"]) or {}, ds.get(l["ID"]) or {}
        leitura = d.get("MOTIVO") or ""
        categoria = l.get("DECISAO_SEMANTICA") or ""
        base = {"CANDIDATA_ID": cand, "NOME": f.get("NOME") or l.get("NOME"), "URL": f.get("URL") or l.get("URL"),
                "ESTADO_NA_MONTAGEM": f.get("ESTADO"), "PROPOSTA_BLOQUEADAS_268": l["PROPOSTA"],
                "CATEGORIA_DA_LEITURA": categoria or None,
                "LEITURA": ("%s — %s %s" % (leitura, d.get("DECIDIDO_POR", ""), (d.get("DECIDIDO_EM") or "")[:10])
                            if leitura else l["PORQUE"])}
        if categoria in DUVIDA:
            linhas.append({**base, "ACAO": "NAO_SEI", "DUPLICADA_DE": None,
                           "PORQUE": "duvida de identidade (%s): %s — nao se recusa" % (categoria, leitura[:160])})
            continue
        if grupo == "PROPOR_RECUSA":
            regra = re.match(r"regra (\S+) casa", l["PORQUE"])
            motivo = "D80(i) %s: %s" % (categoria or (regra.group(1) if regra else "RECUSA"),
                                        leitura or ("%s («%s»)" % (l["PORQUE"], base["NOME"])))
            if regra and leitura:
                motivo += " · regra %s casa no nome/URL" % regra.group(1)
            linhas.append({**base, "ACAO": "RECUSAR", "DUPLICADA_DE": None, "MOTIVO": motivo[:400]})
            continue
        sid, como = mae(cand, base["URL"] or "", RE_ID.findall(leitura), casa, alloc, {})
        if not sid:
            linhas.append({**base, "ACAO": "NAO_SEI", "DUPLICADA_DE": None,
                           "PORQUE": "duplicada sem mae provada: %s" % como})
            continue
        tipo = "DUPLICADA_DA_ORGANIZACAO" if grupo == "DUPLICADA_DA_ORGANIZACAO" else (categoria or "DUPLICADA")
        linhas.append({**base, "ACAO": "RECUSAR", "DUPLICADA_DE": sid, "COMO_SE_ACHOU_A_MAE": como,
                       "MOTIVO": ("D80(i) %s de %s: %s" % (tipo, sid, leitura or como))[:400]})
    conta = {}
    for x in linhas:
        conta[x["ACAO"]] = conta.get(x["ACAO"], 0) + 1
    return {"DATASET": "D80-LISTA-V1", "DECISAO": "D80 (26/09, bot Luciano por delegacao do dono)",
            "DE": str(bloqueadas), "MONTADA_EM": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "N": len(linhas), "POR_ACAO": conta, "LINHAS": linhas}


def conferir(lista: dict, maes_do_dono: dict) -> list[dict]:
    """Cada linha contra a ficha de AGORA. Nada se recusa se a ficha mudou desde a montagem."""
    fichas = {c["CANDIDATA_ID"]: c for c in FN.carregar()["CANDIDATAS"]}
    casa = (_ler(RSY.TABELA), _ler(RSY.LIVRO),
            RSY.ATLAS.read_text(encoding="utf-8") if RSY.ATLAS.exists() else "")
    alloc = _ler(ALLOCATION)
    out = []
    for l in lista["LINHAS"]:
        f = fichas.get(l["CANDIDATA_ID"])
        x = dict(l)
        if l["ACAO"] == "NAO_SEI" and l.get("PORQUE", "").startswith("duplicada sem mae") and maes_do_dono:
            sid, como = mae(l["CANDIDATA_ID"], l["URL"] or "", [], casa, alloc, maes_do_dono)
            if sid:
                x.update(ACAO="RECUSAR", DUPLICADA_DE=sid, COMO_SE_ACHOU_A_MAE=como,
                         MOTIVO=("D80(i) %s de %s: %s" % (l.get("CATEGORIA_DA_LEITURA") or "DUPLICADA", sid,
                                                          l.get("LEITURA") or como))[:400])
        if not f:
            x["AGORA"] = "SEM_FICHA"
        elif _norm(f["URL"]) != _norm(l["URL"] or ""):
            x["AGORA"] = "URL_MUDOU"
        elif f["ESTADO"] == "RECUSADA" and f.get("RECUSADA_POR") == DECISAO:
            x["AGORA"] = "JA_RECUSADA_PELA_D80"
        elif f["ESTADO"] == "RECUSADA":
            x["AGORA"] = "JA_RECUSADA_ANTES"
        elif f["ESTADO"] != l["ESTADO_NA_MONTAGEM"]:
            x["AGORA"] = "ESTADO_MUDOU:%s" % f["ESTADO"]
        else:
            x["AGORA"] = "PRONTA"
        out.append(x)
    return out


def _tarefas(assinaturas: list[str]) -> list[dict]:
    return [t for t in F._ler()["TAREFAS"]
            if t["STATUS"] == F.BLOCKED and t["TASK_TYPE"] == F.QUALIFY
            and any(a in (t.get("LAST_ERROR") or "") for a in assinaturas)]


def main(argv=None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    a = {}
    for x in argv:
        k, _, v = x.lstrip("-").partition("=")
        a.setdefault(k, []).append(v)
    if "montar" in a:
        lista = montar(Path(a["montar"][0]))
        LISTA.write_text(json.dumps(lista, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
        print(json.dumps({"LISTA": str(LISTA), "N": lista["N"], "POR_ACAO": lista["POR_ACAO"]}, ensure_ascii=False))
        return 0
    maes = {}
    for m in a.get("mae", []):
        host, _, sid = m.partition("=")
        casa = (_ler(RSY.TABELA), _ler(RSY.LIVRO), RSY.ATLAS.read_text(encoding="utf-8"))
        if sid not in _fontes_do_host(host, *casa):
            print("RECUSADO: --mae=%s — %s nao e fonte do site %s" % (m, sid, host), file=sys.stderr)
            return 2
        maes[host] = sid
    linhas = conferir(_ler(LISTA), maes)
    recibo = {"DECISAO": DECISAO, "QUANDO": datetime.now(timezone.utc).isoformat(timespec="seconds"),
              "RAIZ": str(RAIZ), "MAES_DO_DONO": maes}
    if "reverter" in a:
        feitas = []
        for l in linhas:
            if l["AGORA"] == "JA_RECUSADA_PELA_D80" and FN.reverter_recusa(l["URL"], DECISAO):
                feitas.append(l["CANDIDATA_ID"])
        reabertas = F.recuperar_bloqueadas_por_defeito(REABRIR_AO_REVERTER, {F.QUALIFY})
        recibo.update(MODO="REVERTER", REVERTIDAS=feitas, QUALIFY_REABERTAS=len(reabertas),
                      NOTA="numeros ja cunhados (ii)/(iii) NAO se apagam: nunca reciclar")
    else:
        prontas = [l for l in linhas if l["ACAO"] == "RECUSAR" and l["AGORA"] == "PRONTA"]
        recibo.update(MODO="APLICAR" if "aplicar" in a else "A_SECO",
                      POR_AGORA={k: sum(1 for l in linhas if l["AGORA"] == k) for k in
                                 sorted({l["AGORA"] for l in linhas})},
                      A_RECUSAR=len(prontas),
                      FICAM_NAO_SEI=[{"CANDIDATA_ID": l["CANDIDATA_ID"], "PORQUE": l.get("PORQUE")}
                                     for l in linhas if l["ACAO"] == "NAO_SEI"],
                      QUALIFY_A_REABRIR={s: len(_tarefas([s])) for s in REABRIR})
        if "aplicar" in a:
            feitas = []
            for l in prontas:
                c = FN.recusar(l["URL"], l["MOTIVO"], duplicada_de=l.get("DUPLICADA_DE"), decisao=DECISAO)
                if c and c.get("RECUSADA_POR") == DECISAO:
                    feitas.append({"CANDIDATA_ID": l["CANDIDATA_ID"], "DUPLICADA_DE": l.get("DUPLICADA_DE")})
            reabertas = F.recuperar_bloqueadas_por_defeito(REABRIR, {F.QUALIFY})
            recibo.update(RECUSADAS=feitas, QUALIFY_REABERTAS=len(reabertas))
        recibo["LINHAS"] = linhas
    texto = json.dumps(recibo, ensure_ascii=False, indent=1)
    if a.get("recibo"):
        Path(a["recibo"][0]).write_text(texto + "\n", encoding="utf-8")
    resumo = {k: v for k, v in recibo.items() if k not in ("LINHAS",)}
    print(json.dumps(resumo, ensure_ascii=False, indent=1)[:6000])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
