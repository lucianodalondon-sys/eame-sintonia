#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ONBOARDAR ROTAS PROVADAS — a capacidade que faltava entre o Curator e o coletor.

    ELEGIVEL SEM CONTRATO NAO E UMA DECISAO QUE FALTA. E UMA PONTE QUE FALTA.

MEDIDO (ROTAS-ELEGIVEIS-V1, 2026-09-22). O coletor so colhe quem tem contrato
em `regras/italy_contracts.mjs`, e as fontes do Curator so la entram por uma
linha em `regras/italy_contracts_onboarded.json`. Essa tabela foi escrita UMA
vez (INTEGRACAO-04A, 18 linhas, 2026-09-20). Toda a fonte que o portao aprovou
DEPOIS — com rota declarada pelo Curator e tudo — ficou em
`ELIGIBLE_WITHOUT_CONTRACT`. Nao por decisao: por nao haver caminho.

Este ficheiro e esse caminho, e so esse. Uma linha entra na tabela quando as
TRES coisas sao verdade ao mesmo tempo, no instante da corrida:

    1. o portao (`collection_gate.avaliar`) diz ELIGIBLE, no livro desta arvore
    2. a fonte nao tem contrato no coletor (o dono e `italy_contracts.mjs`)
    3. o canario real (`medidas/canario_rotas_elegiveis.py`) deu ROUTE_PROVEN
       sobre o MESMO contrato que vai ser escrito — a impressao digital
       (`sha_do_contrato`) da prova e igual a do contrato de agora — ha no
       maximo PROVA_MAX_IDADE, e nenhuma outra fonte provou a rota pelo mesmo
       documento (duas fichas, uma fonte: nao se contrata a segunda — e
       decisao de identidade, nao de rota)

A aquisicao escrita e a do Curator, byte a byte. Nada se inventa aqui.

    POR OMISSAO SO MOSTRA. `--aplicar` escreve a tabela.

QUEM O CHAMA (PONTE-ONBOARD, 25/09/2026): o supervisor do bot, a cada volta,
por `onboardar_se_mudou()` (ver `curadoria/supervisor.py`, `_loop`). Medido no
MICRO-PRONTO: este ficheiro nao era chamado por servico nenhum, e em 24 h
entraram 0 fontes na tabela com 27 ELIGIBLE a espera.

O que NAO faz: nao promove, nao mexe no livro, na fila, no portao nem na
rede, e nao declara RECOLLECTION (quem nao mediu nao declara).
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from datetime import datetime, timedelta, timezone
from urllib.parse import urlparse

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "curadoria"))
import collection_gate as G      # noqa: E402
import sha_do_contrato as SHA    # noqa: E402

TABELA = RAIZ / "regras" / "italy_contracts_onboarded.json"
CANARIO = RAIZ / "curadoria" / "ROTAS-ELEGIVEIS-V1.json"
CURATOR = RAIZ / "curadoria" / "italy_contracts_curator.json"

# Uma prova de rota vale 7 dias — a mesma regra da coorte da Big Collection
# (G3: «canario com prova <= 7 dias»). Mais velha, a fonte fica; nao se adivinha.
PROVA_MAX_IDADE = timedelta(days=7)


def ids_com_contrato_no_coletor() -> set[str]:
    r = subprocess.run(
        ["node", "-e", 'import("./regras/italy_contracts.mjs").then(m=>'
         'console.log(JSON.stringify(Object.keys(m.CONTRACTS))))'],
        cwd=RAIZ, capture_output=True, text=True, timeout=120)
    if r.returncode:
        raise RuntimeError("o dono dos contratos nao carregou: " + r.stderr[-300:])
    return set(json.loads(r.stdout))


def _json(p: Path) -> dict:
    return json.loads(p.read_text(encoding="utf-8"))


def _site(url) -> str:
    h = urlparse(url or "").hostname or ""
    return h[4:] if h.startswith("www.") else h


def _quando(texto) -> datetime | None:
    try:
        t = datetime.fromisoformat(str(texto).replace("Z", "+00:00"))
    except (TypeError, ValueError):
        return None
    return t if t.tzinfo else t.replace(tzinfo=timezone.utc)


def planear(*, ctx: dict | None = None, canario: dict | None = None,
            curator: dict | None = None, com_contrato: set[str] | None = None,
            agora: datetime | None = None) -> dict:
    agora = agora or datetime.now(timezone.utc)
    ctx = ctx if ctx is not None else G._contexto()
    canario = canario if canario is not None else _json(CANARIO)
    curator = curator if curator is not None else {
        c["SOURCE_ID"]: c for c in _json(CURATOR)["FONTES"]}
    com_contrato = com_contrato if com_contrato is not None else ids_com_contrato_no_coletor()
    provas = {l["SOURCE_ID"]: l for l in canario["LINHAS"]}
    # o documento que provou a rota — dois IDs pelo mesmo documento sao uma fonte
    dono_do_doc = {}
    for l in canario["LINHAS"]:
        if l.get("VEREDITO") == "ROUTE_PROVEN":
            dono_do_doc.setdefault(l["CANARIO"]["URL"], l["SOURCE_ID"])
    # ...e contra quem JA tem contrato no coletor: o mesmo site com o mesmo padrao de
    # materias colhe os mesmos documentos (BC2, 23/09: duas paginas de «seleccao de
    # idioma» da ARPAE, com OWNER «Italiano», iam duplicar a fonte ja contratada).
    ja_contratada = {}
    for s in sorted(com_contrato):
        a = (curator.get(s) or {}).get("ACQUISITION") or {}
        if a.get("LINK_PATTERN"):
            ja_contratada.setdefault((_site(a.get("INDEX_URL")), a["LINK_PATTERN"]), s)
    entra, fica = [], []
    for sid in G.elegiveis(ctx=ctx):
        if sid in com_contrato:
            continue
        p, c = provas.get(sid), curator.get(sid)
        porque = None
        if not c:
            porque = "sem contrato do Curator nesta arvore"
        elif not p or p.get("VEREDITO") != "ROUTE_PROVEN":
            porque = "canario nao provou a rota: %s — %s" % (
                (p or {}).get("VEREDITO", "SEM_CANARIO"), (p or {}).get("CAUSA", ""))
        elif not p.get("CONTRATO_SHA256"):
            porque = ("a prova nao diz que contrato provou (sem CONTRATO_SHA256): e de antes "
                      "do PONTE-ONBOARD — refazer o canario")
        elif p["CONTRATO_SHA256"] != SHA.do_contrato(c):
            porque = ("o canario provou OUTRA aquisicao que nao a do contrato actual "
                      "(sha provado %s != actual %s)" % (p["CONTRATO_SHA256"][:12],
                                                        SHA.do_contrato(c)[:12]))
        elif (_quando(p.get("PROVADO_EM") or canario.get("GERADO_EM")) is None
              or agora - _quando(p.get("PROVADO_EM") or canario.get("GERADO_EM")) > PROVA_MAX_IDADE):
            porque = ("prova de rota VELHA ou sem data (%s): vale %d dias — refazer o canario"
                      % (p.get("PROVADO_EM") or canario.get("GERADO_EM"), PROVA_MAX_IDADE.days))
        elif dono_do_doc.get(p["CANARIO"]["URL"]) != sid:
            porque = ("DUPLICADA: a rota chega ao mesmo documento que %s — duas fichas, "
                      "uma fonte; decisao de identidade, nao de rota"
                      % dono_do_doc[p["CANARIO"]["URL"]])
        elif (_site(c["ACQUISITION"].get("INDEX_URL")),
              c["ACQUISITION"].get("LINK_PATTERN")) in ja_contratada:
            porque = ("DUPLICADA de fonte ja contratada: %s — mesmo site e mesmo padrao de "
                      "materias; decisao de identidade, nao de rota"
                      % ja_contratada[(_site(c["ACQUISITION"].get("INDEX_URL")),
                                       c["ACQUISITION"].get("LINK_PATTERN"))])
        if porque:
            fica.append({"SOURCE_ID": sid, "PORQUE": porque})
            continue
        entra.append(linha_da_tabela(c, p, p.get("PROVADO_EM") or canario.get("GERADO_EM", "NAO SEI")))
    return {"ENTRA": entra, "FICA": fica}


def linha_da_tabela(c: dict, p: dict, quando: str) -> dict:
    k = p["CANARIO"]
    return {
        "SOURCE_ID": c["SOURCE_ID"], "OWNER": c.get("OWNER"), "NAME": c.get("NAME"),
        "TERRITORY": c.get("TERRITORY"), "BATCH_ID": c.get("BATCH_ID"),
        "OUTPUT_TYPE": c.get("OUTPUT_TYPE"), "ACQUISITION": c["ACQUISITION"],
        "EVIDENCE": "curadoria/ROTAS-ELEGIVEIS-V1.json",
        "SONDAGEM": {
            "SONDADO_EM": quando[:10],
            "REGRA": "medidas/canario_rotas_elegiveis.py: robots pela casa, INDEX_URL, "
                     "links pelo motor do coletor, alvo aberto e retratado, gate CAPA != MATERIA",
            "ENTRADA_STATUS": p.get("INDEX_HTTP"), "DOCUMENTO": k["URL"],
            "DOCUMENTO_ASSINATURA": "HTML", "DOCUMENTO_BYTES": k["BYTES"],
            "ALVOS_DESCOBERTOS": p.get("LINKS_DE_DETALHE"),
            "HTML_KIND": k["HTML_KIND"], "PARAGRAPH_CHARACTERS": k["PARAGRAPH_CHARACTERS"],
            "CONTRATO_SHA256": p.get("CONTRATO_SHA256"), "PROVADO_EM": p.get("PROVADO_EM"),
        },
        "ONBOARDED_BY": "ROTAS-ELEGIVEIS-V1 (canario de rota %s) — curadoria/onboardar_rotas_provadas.py"
                        % quando[:10],
    }


def aplicar(entra: list[dict]) -> int:
    t = _json(TABELA)
    ja = {f["SOURCE_ID"] for f in t["FONTES"]}
    novas = [l for l in entra if l["SOURCE_ID"] not in ja]
    if not novas:
        return 0
    t["FONTES"].extend(novas)
    # escrita atomica: o coletor pode estar a ler a tabela nesse instante
    tmp = TABELA.with_name(TABELA.name + ".tmp")
    tmp.write_text(json.dumps(t, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    tmp.replace(TABELA)
    return len(novas)


# ── O GANCHO DO SUPERVISOR ───────────────────────────────────────────────────
# Porque o supervisor e nao a ponte nem o alimentador:
#   * a tabela que o coletor le vive na lane do BOT (a Big Collection corre com
#     cwd = arvore do bot: ferramentas/big_collection/bc5_big_collection.py);
#   * a ponte (ponte_automatica.py) por desenho so LE a lane do bot;
#   * o alimentador (gatilho_discovery.talvez_alimentar) sai logo com QUEUE_OK
#     quando a fila tem trabalho — no vivo tinha 3457 tarefas: nunca correria.
# Sem rede: so le a prova que o canario deixou. Barato, mas nao a cada volta:
# corre quando a prova muda de bytes, ou de ONBOARD_INTERVALO em ONBOARD_INTERVALO
# (o portao muda sem a prova mudar: uma fonte provada pode ficar ELIGIBLE depois).
ONBOARD_INTERVALO = timedelta(minutes=10)


def onboardar_se_mudou(estado: dict, *, agora: datetime | None = None,
                       planear_fn=None, aplicar_fn=None) -> dict:
    """Uma volta do onboarding. Devolve o que fez (para o diario do supervisor);
    guarda em `estado` a impressao da prova e a hora, para nao repetir sem motivo."""
    import hashlib
    agora = agora or datetime.now(timezone.utc)
    sha = hashlib.sha256(CANARIO.read_bytes()).hexdigest() if CANARIO.exists() else None
    ultima = _quando(estado.get("ONBOARD_ULTIMA_EM"))
    if sha == estado.get("ONBOARD_PROVA_SHA") and ultima and agora - ultima < ONBOARD_INTERVALO:
        return {"ACCAO": "NADA_MUDOU"}
    estado["ONBOARD_PROVA_SHA"], estado["ONBOARD_ULTIMA_EM"] = sha, agora.isoformat()
    if sha is None:
        return {"ACCAO": "SEM_PROVA", "PORQUE": "%s nao existe" % CANARIO.name}
    plano = (planear_fn or planear)(agora=agora)
    escritas = (aplicar_fn or aplicar)(plano["ENTRA"]) if plano["ENTRA"] else 0
    return {"ACCAO": "ONBOARDOU" if escritas else "NINGUEM_ENTROU",
            "ESCRITAS": escritas, "ENTRA": [l["SOURCE_ID"] for l in plano["ENTRA"]],
            "FICA": len(plano["FICA"]), "PROVA_SHA": sha}


def main(argv=None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    plano = planear()
    for l in plano["ENTRA"]:
        print("ENTRA  %s  %s" % (l["SOURCE_ID"], l["ACQUISITION"]["INDEX_URL"]))
    for l in plano["FICA"]:
        print("FICA   %s  %s" % (l["SOURCE_ID"], l["PORQUE"][:140]))
    print("ENTRA=%d FICA=%d" % (len(plano["ENTRA"]), len(plano["FICA"])))
    if "--aplicar" in argv:
        print("escritas na tabela: %d" % aplicar(plano["ENTRA"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
