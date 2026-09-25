#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""CANARIO DAS ROTAS ELEGIVEIS — a fonte aprovada pelo portao, a casa sabe la chegar?

    ELEGIVEL NAO E ALCANCAVEL. SAO DUAS PERGUNTAS.

O portao (`curadoria/collection_gate.py`) diz QUEM pode ser colhido. O coletor
(`coleta/italy_recurrent_collect.mjs`) so colhe quem tem contrato em
`regras/italy_contracts.mjs`. As aprovadas sem contrato ficam em
`ELIGIBLE_WITHOUT_CONTRACT`. Este instrumento pega na rota que o Curator
DECLAROU para cada uma (`curadoria/italy_contracts_curator.json` EM DISCO por omissao, ou no ref de Git
se lhe indicar) e prova-a contra a rede, SEM inventar nenhuma:

    1. robots.txt pelo leitor unico da casa (gate_de_rota) — proibido nao se bate
    2. GET ao INDEX_URL declarado
    3. links de detalhe pelo MESMO motor do coletor (`ligacoesDoIndice`, Node)
    4. GET ao primeiro alvo; retrato + gate CAPA != MATERIA (retrato_html)
    5. CONTROLO NEGATIVO: o proprio INDEX_URL passado pelo mesmo gate — uma
       listagem/homepage NAO pode passar como materia

    ROUTE_PROVEN      alvo aberto, HTML_KIND=CONTENT, gate calado
    CAPABILITY_BLOCK  a rota declarada nao chega a materia (lista vazia, alvo
                      e capa, alvo sem corpo) — falta capacidade do nosso lado
    POLICY_BLOCK      robots proibe, ou a fonte responde 401/403 (nao se contorna)
    UNKNOWN           transporte/DNS deste egresso, robots ilegivel

Cadencia: 1 s entre pedidos, no maximo 4 pedidos por fonte (robots, indice,
ate 2 alvos). Nao escreve no livro, na fila, no armazem nem na Sala. Nao promove.
"""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "curadoria"))
import canario as CAN            # noqa: E402
import gate_de_rota as GATE      # noqa: E402
import retrato_html as RH        # noqa: E402
import sha_do_contrato as SHA    # noqa: E402

SAIDA = RAIZ / "curadoria" / "ROTAS-ELEGIVEIS-V1.json"
PAUSA_S = 1.0
MAX_ALVOS = 2

_NODE_LIGACOES = r"""
import { readFileSync } from "node:fs";
import { pathToFileURL } from "node:url";
const [motor, html, aq] = process.argv.slice(2);
const m = await import(pathToFileURL(motor).href);
const a = JSON.parse(readFileSync(aq, "utf8"));
console.log(JSON.stringify(m.ligacoesDoIndice(readFileSync(html).toString("latin1"), a)));
"""


def ligacoes_pelo_motor(html: bytes, aq: dict) -> list[str]:
    """Os links que o COLETOR veria — o motor verdadeiro, nao uma copia."""
    with tempfile.TemporaryDirectory() as d:
        h, a, s = Path(d, "i.html"), Path(d, "aq.json"), Path(d, "l.mjs")
        h.write_bytes(html)
        a.write_text(json.dumps(aq), encoding="utf-8")
        s.write_text(_NODE_LIGACOES, encoding="utf-8")
        r = subprocess.run(["node", str(s), str(RAIZ / "regras" / "motor_de_rota.mjs"),
                            str(h), str(a)], capture_output=True, text=True, timeout=60)
        if r.returncode:
            raise RuntimeError(r.stderr[-300:])
        return json.loads(r.stdout)


def _veredito_http(status: int, erro: str) -> tuple[str, str]:
    if status in (401, 403):
        return "POLICY_BLOCK", "a fonte respondeu HTTP %d — nao se contorna" % status
    if status == 0:
        return "UNKNOWN", "transporte deste egresso: %s" % erro
    return "CAPABILITY_BLOCK", "HTTP %d na rota declarada" % status


def provar(sid: str, contrato: dict) -> dict:
    aq = contrato.get("ACQUISITION") or {}
    lin = {"SOURCE_ID": sid, "OWNER": contrato.get("OWNER"),
           "TIPO": ("LISTAGEM_DE_NOTICIAS" if aq.get("STRATEGY") == "HTML_LINK_DISCOVERY"
                    else aq.get("STRATEGY")),
           "INDEX_URL": aq.get("INDEX_URL"), "LINK_PATTERN": aq.get("LINK_PATTERN"),
           "MAX_TARGETS": aq.get("MAX_TARGETS"), "PEDIDOS": 0}
    if aq.get("STRATEGY") != "HTML_LINK_DISCOVERY":
        lin.update(VEREDITO="UNKNOWN", CAUSA="estrategia %s fora do ambito deste canario"
                   % aq.get("STRATEGY"))
        return lin
    idx = aq["INDEX_URL"]
    rp, txt = GATE.robots_de(urlparse(idx).hostname)
    lin["PEDIDOS"] += 1
    lin["ROBOTS"] = txt[:160] if not txt.lstrip().lower().startswith(("user", "#", "sitemap")) else "lido"
    if "inacessivel" in txt:
        lin.update(VEREDITO="UNKNOWN", CAUSA="robots ilegivel deste egresso: " + txt[:120])
        return lin
    if not GATE.permitido(idx, rp):
        lin.update(VEREDITO="POLICY_BLOCK", CAUSA="robots proibe o INDEX_URL")
        return lin
    time.sleep(PAUSA_S)
    st, corpo, err = CAN.buscar(idx)
    lin["PEDIDOS"] += 1
    lin["INDEX_HTTP"] = st
    if st != 200:
        v, c = _veredito_http(st, err)
        lin.update(VEREDITO=v, CAUSA="indice: " + c)
        return lin
    # CONTROLO NEGATIVO: a propria listagem pelo gate. Tem de NAO passar.
    ri = RH.retrato_do_html(corpo)
    lin["NEGATIVE_CONTROL"] = {
        "URL": idx, "HTML_KIND": ri["HTML_KIND"], "LINKS": ri["LINKS"],
        "NON_WHITESPACE_CHARACTERS": ri["NON_WHITESPACE_CHARACTERS"],
        "PASSARIA_COMO_MATERIA": ri["HTML_KIND"] == "CONTENT",
    }
    links = ligacoes_pelo_motor(corpo, aq)
    lin["LINKS_DE_DETALHE"] = len(links)
    lin["AMOSTRA_LINKS"] = links[:5]
    if not links:
        lin.update(VEREDITO="CAPABILITY_BLOCK",
                   CAUSA="EMPTY_LIST: o INDEX_URL declarado nao anuncia nenhum endereco "
                         "que case com LINK_PATTERN (pelo motor do coletor)")
        return lin
    # Ate DOIS alvos: um item magro (pagina de inscricao, evento sem texto)
    # nao condena a rota, e um so verde nao se estica ao resto. Cada alvo
    # aberto fica escrito, com o veredito dele.
    lin["CANARIOS"] = []
    for alvo in links[:MAX_ALVOS]:
        if not GATE.permitido(alvo, rp):
            lin["CANARIOS"].append({"URL": alvo, "VEREDITO": "POLICY_BLOCK",
                                    "CAUSA": "robots proibe o alvo"})
            continue
        time.sleep(PAUSA_S)
        st, corpo, err = CAN.buscar(alvo)
        lin["PEDIDOS"] += 1
        c = {"URL": alvo, "HTTP": st, "BYTES": len(corpo)}
        lin["CANARIOS"].append(c)
        if st != 200:
            c["VEREDITO"], c["CAUSA"] = _veredito_http(st, err)
            continue
        r = RH.retrato_do_html(corpo)
        c.update({k: r[k] for k in ("HTML_KIND", "CAPA_OU_MATERIA", "LINKS",
                                    "NON_WHITESPACE_CHARACTERS",
                                    "PARAGRAPH_CHARACTERS", "TEXT_SHA256")})
        gate = RH.gate_capa_nao_e_materia(contrato, r, url=alvo, regua_a_mandar=CAN._regua_manda(sid))  # V1A
        if gate:
            c["VEREDITO"], c["CAUSA"] = "CAPABILITY_BLOCK", gate
        elif r["HTML_KIND"] != "CONTENT":
            c["VEREDITO"], c["CAUSA"] = ("CAPABILITY_BLOCK",
                                         "alvo sem corpo util: HTML_KIND=%s" % r["HTML_KIND"])
        else:
            c["VEREDITO"], c["CAUSA"] = "ROUTE_PROVEN", "materia com corpo"
            break
    bons = [c for c in lin["CANARIOS"] if c["VEREDITO"] == "ROUTE_PROVEN"]
    if bons:
        c = bons[0]
        lin["CANARIO"] = c
        lin.update(VEREDITO="ROUTE_PROVEN",
                   CAUSA="indice -> %d links pelo motor -> %s com %d caracteres em "
                         "paragrafos (%d alvo(s) aberto(s))"
                         % (len(links), c["URL"], c["PARAGRAPH_CHARACTERS"],
                            len(lin["CANARIOS"])))
    else:
        # o veredito da fonte e o do ULTIMO alvo: politica vence capacidade
        vs = [c["VEREDITO"] for c in lin["CANARIOS"]]
        v = ("POLICY_BLOCK" if "POLICY_BLOCK" in vs else
             "UNKNOWN" if "UNKNOWN" in vs else "CAPABILITY_BLOCK")
        lin.update(VEREDITO=v, CAUSA="; ".join("%s: %s" % (c["URL"], c["CAUSA"])
                                              for c in lin["CANARIOS"]))
    return lin


# ── O CONTRATO QUE SE PROVA E O DO LIVRO VIVO, EM DISCO ─────────────────────
# ⚠️ MEDIDO (MICRO-PRONTO, 25/09/2026): isto lia `git show HEAD:...` sempre. O bot
# escreve no DISCO e nao commita — no vivo HEAD tinha 574 fontes e o disco 762, e
# 14 das 17 fontes a onboardar tinham no HEAD outra aquisicao (ou nenhuma). A
# prova dizia ROUTE_PROVEN sobre um contrato que nao era o que ia para o coletor.
#
#     O CONTRATO PROVADO TEM DE SER O CONTRATO QUE O ROBO VAI USAR.
#
# Por omissao le-se o ficheiro em disco (o mesmo que `onboardar_rotas_provadas`
# le). Um ref de Git so se usa quando pedido por extenso (`ID@<ref>`), e a linha
# diz de onde veio. Em qualquer caso a prova leva a impressao digital do que
# provou (`sha_do_contrato`): quem onboarda compara-a com o contrato de agora.
DISCO = "DISCO"
CONTRATOS_EM_DISCO = RAIZ / "curadoria" / "italy_contracts_curator.json"


def _contratos_de(ref: str) -> dict:
    if ref == DISCO:
        d = json.loads(CONTRATOS_EM_DISCO.read_text(encoding="utf-8"))
    else:
        r = subprocess.run(["git", "show", "%s:curadoria/italy_contracts_curator.json" % ref],
                           capture_output=True, cwd=RAIZ)
        if r.returncode:
            raise RuntimeError("git show %s falhou: %s" % (ref, r.stderr[-200:]))
        d = json.loads(r.stdout)
    return {c["SOURCE_ID"]: c for c in d["FONTES"]}


def _de_onde(ref: str) -> str:
    return ("disco:curadoria/italy_contracts_curator.json" if ref == DISCO
            else "%s:curadoria/italy_contracts_curator.json" % ref)


def juntar(antigas: list[dict], novas: list[dict]) -> list[dict]:
    """Uma linha por fonte: a prova nova substitui a antiga da MESMA fonte, e as
    outras ficam. `--escrever` sozinho reescrevia o ficheiro — correr em rondas
    (uma fonte por dominio por ronda, D38) apagava a ronda anterior."""
    por = {l["SOURCE_ID"]: l for l in antigas}
    for l in novas:
        por[l["SOURCE_ID"]] = l
    return list(por.values())


def main(argv=None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    pedidos = []           # "ID@ref"
    for a in argv:
        if a.startswith("--fontes="):
            pedidos = [x for x in a.split("=", 1)[1].split(",") if x]
    livros, linhas = {}, []
    for p in pedidos:
        sid, _, ref = p.partition("@")
        ref = ref or DISCO
        if ref not in livros:
            livros[ref] = _contratos_de(ref)
        c = livros[ref].get(sid)
        if not c:
            linhas.append({"SOURCE_ID": sid, "VEREDITO": "UNKNOWN",
                           "CAUSA": "sem contrato do Curator em %s" % _de_onde(ref)})
            continue
        l = provar(sid, c)
        l["CONTRATO_LIDO_DE"] = _de_onde(ref)
        l["CONTRATO_SHA256"] = SHA.do_contrato(c)
        l["PROVADO_EM"] = datetime.now(timezone.utc).isoformat()
        linhas.append(l)
        print("%-11s %-17s %s" % (sid, l["VEREDITO"], l["CAUSA"][:110]), flush=True)
        time.sleep(PAUSA_S)
    d = {"DATASET": "ROTAS-ELEGIVEIS-V1",
         "GERADO_EM": datetime.now(timezone.utc).isoformat(),
         "INSTRUMENTO": "medidas/canario_rotas_elegiveis.py",
         "LEI": "rota sem canario real nao e rota; 403 e robots sao resposta, nao se contornam",
         "LINHAS": linhas}
    if "--juntar" in argv and SAIDA.exists():
        d["LINHAS"] = juntar(json.loads(SAIDA.read_text(encoding="utf-8")).get("LINHAS", []), linhas)
    if "--escrever" in argv or "--juntar" in argv:
        SAIDA.write_text(json.dumps(d, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
