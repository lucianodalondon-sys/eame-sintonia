#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""PORQUE E QUE O BOT PAROU — a fila dele, lida de fora, sem lhe tocar.

    UMA PONTE LIGADA A UMA TORNEIRA FECHADA NAO TRAZ NADA,
    E FICA VERDE A DIZER QUE ESTA TUDO BEM.

A ponte (`reconciliar_livros.py`) responde «o que e que o bot descobriu?».
Este ficheiro responde a outra pergunta, que a ponte nunca faz: **porque e que
ele deixou de descobrir?** Sem ela, um bot parado e um bot sem trabalho leem-se
exactamente da mesma maneira — o livro nao cresce nos dois casos.

Medido em 2026-09-22: a fila tinha 1057 tarefas e **ZERO pendentes**. O bot nao
estava preso: tinha acabado o trabalho. Mas 149 tarefas nao deram fruto, e e ai
que esta o que interessa.

⚠️ O ACHADO. 62 das 69 tarefas FAILED morreram com o mesmo motivo — «teto de 5
tentativas: robots nao pode ser lido». A doutrina do bot esta CERTA (robots
ilegivel e UNKNOWN, nao proibicao), mas o efeito pratico e que a fonte bate no
teto e fica FAILED **para sempre**: ninguem volta a olhar para ela.

Sondadas as 62 uma a uma (so o `robots.txt`, que e publico e minusculo):
**42 leem-se agora**. As outras 20 falham por 403 de muro anti-robot, ligacao
cancelada, SSL ou robots inexistente — e nenhuma dessas e prova de fonte morta.

    FALHA DE LIGACAO NAO E FONTE MORTA.
    UM TETO DE TENTATIVAS TRANSFORMA UMA INTERMITENCIA EM SENTENCA.

`www.meteotrentino.it` prova-o sozinho: respondeu HTTP 200 numa sonda e
cancelou a ligacao na seguinte, com minutos de diferenca.

ESTE FICHEIRO NAO CONSERTA NADA. Nao escreve na fila do bot, nao re-enfileira,
nao toca na worktree dele — o supervisor esta vivo. Mede, classifica e diz. A
decisao de re-enfileirar e de quem manda, e e outra missao.
"""
from __future__ import annotations

import collections
import json
import subprocess
import sys
import urllib.request
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "curadoria"))

import reconciliar_livros as R  # noqa: E402

SAIDA = RAIZ / "curadoria" / "DIAGNOSTICO-FILA-DO-BOT-V1.json"
UA = "Mozilla/5.0 (compatible; SintoniaBot/1.0)"
MOTIVO_ROBOTS = "robots nao pode ser lido"


def _do_bot(ref: str, caminho: str):
    r = subprocess.run(["git", "show", "%s:%s" % (ref, caminho)], cwd=str(RAIZ),
                       capture_output=True, text=True, encoding="utf-8", timeout=120)
    return json.loads(r.stdout) if r.returncode == 0 and r.stdout else None


def classificar(erro: Exception) -> str:
    s = str(erro)
    if "getaddrinfo" in s:
        return "DNS_NAO_RESOLVE"
    if "10054" in s or "10053" in s:
        return "LIGACAO_CANCELADA"
    if "SSL" in s:
        return "SSL"
    if "403" in s:
        return "MURO_ANTI_ROBOT_403"
    if "404" in s:
        return "ROBOTS_INEXISTENTE_404"
    if "timed out" in s or "timeout" in s.lower():
        return "TIMEOUT"
    return "OUTRO"


def sondar_robots(host: str, timeout: int = 20) -> tuple[str, str]:
    """So o robots.txt. Publico, minusculo, feito para ser lido por maquinas.
    ISTO NAO E COLETA: nao se le uma unica pagina de conteudo."""
    try:
        req = urllib.request.Request("https://%s/robots.txt" % host,
                                     headers={"User-Agent": UA})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            resp.read()
        return "LEGIVEL", "HTTP %s" % resp.status
    except Exception as e:  # noqa: BLE001 — a classificacao e o produto
        return classificar(e), ("%s: %s" % (type(e).__name__, e))[:120]


def medir(*, sondar: bool = True, ref: str | None = None) -> dict:
    ref = ref or R.ref_do_bot()
    fila = _do_bot(ref, "curadoria/LIFECYCLE-QUEUE-V1.json")
    if fila is None:
        raise SystemExit("fila do bot ilegivel por git show %s" % ref)
    tarefas = fila.get("TAREFAS", [])
    contratos = _do_bot(ref, "curadoria/italy_contracts_curator.json") or {}
    mp = {c["SOURCE_ID"]: c for c in contratos.get("FONTES", [])}

    por_status = collections.Counter(t["STATUS"] for t in tarefas)
    pendentes = [t for t in tarefas
                 if t["STATUS"] in ("PENDING", "PENDENTE", "QUEUED", "READY")]

    falhas = collections.Counter()
    for t in tarefas:
        if t["STATUS"] in ("FAILED", "BLOCKED"):
            falhas["%s | %s" % (t["STATUS"], str(t.get("LAST_ERROR"))[:70])] += 1

    presas = [t for t in tarefas
              if t["STATUS"] == "FAILED" and MOTIVO_ROBOTS in str(t.get("LAST_ERROR"))]
    por_host: dict = collections.defaultdict(list)
    sem_contrato = []
    for t in presas:
        c = mp.get(t["SOURCE_ID"]) or {}
        url = ((c.get("ACQUISITION") or {}).get("INDEX_URL")
               or c.get("CANONICAL_ENTRY_URL") or "")
        if url.startswith("http"):
            por_host[url.split("/")[2]].append(t["SOURCE_ID"])
        else:
            sem_contrato.append(t["SOURCE_ID"])

    sonda: dict = {}
    if sondar:
        for host in sorted(por_host):
            classe, detalhe = sondar_robots(host)
            sonda[host] = {"CLASSE": classe, "DETALHE": detalhe,
                           "SOURCE_IDS": sorted(por_host[host])}

    por_classe_host = collections.Counter(v["CLASSE"] for v in sonda.values())
    por_classe_fonte: collections.Counter = collections.Counter()
    for h, v in sonda.items():
        por_classe_fonte[v["CLASSE"]] += len(v["SOURCE_IDS"])

    return {
        "DATASET": "DIAGNOSTICO-FILA-DO-BOT-V1",
        "LEI": ("um bot parado e um bot sem trabalho leem-se da mesma maneira no "
                "livro; so a fila os distingue. Falha de ligacao nao e fonte morta."),
        "GERADO_EM": R.agora(),
        "BOT": {"BRANCH": R.BRANCH_C, "HEAD": ref,
                "LEITURA": "git show — copia congelada; o supervisor esta vivo e nao foi tocado"},
        "FILA": {
            "TAREFAS": len(tarefas),
            "POR_STATUS": dict(por_status),
            "PENDENTES": len(pendentes),
            "PORQUE_PAROU": ("fila esgotada — 0 pendentes; nao esta preso"
                             if not pendentes else
                             "%d tarefas pendentes: o bot tem trabalho por fazer" % len(pendentes)),
        },
        "MOTIVOS_DE_FALHA": dict(falhas.most_common(12)),
        "PRESAS_POR_ROBOTS_ILEGIVEL": {
            "FONTES": len(presas),
            "HOSTS": len(por_host),
            "SEM_CONTRATO_NESTA_LEITURA": sem_contrato,
            "SONDA_FEITA": sondar,
            "POR_CLASSE_HOSTS": dict(por_classe_host),
            "POR_CLASSE_FONTES": dict(por_classe_fonte),
            "LEGIVEIS_AGORA": por_classe_fonte.get("LEGIVEL", 0),
            "NOTA": ("«legivel agora» NAO quer dizer «pronta»: quer dizer que o motivo "
                     "pelo qual parou ja nao se verifica, e que merece ser olhada outra "
                     "vez. Nenhuma das classes medidas e prova de fonte morta."),
            "HOSTS_SONDADOS": sonda,
        },
        "NAO_FEITO": ("re-enfileirar, corrigir a fila ou tocar na worktree do bot. "
                      "Isto mede e diz; decidir e de quem manda."),
    }


def main(argv=None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    d = medir(sondar="--sem-rede" not in argv)
    if "--escrever" in argv:
        SAIDA.write_text(json.dumps(d, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
        print("escrito: %s" % SAIDA.relative_to(RAIZ))
    f = d["FILA"]
    print("BOT_HEAD            %s" % d["BOT"]["HEAD"])
    print("TAREFAS             %d  %s" % (f["TAREFAS"], json.dumps(f["POR_STATUS"])))
    print("PENDENTES           %d — %s" % (f["PENDENTES"], f["PORQUE_PAROU"]))
    p = d["PRESAS_POR_ROBOTS_ILEGIVEL"]
    print("PRESAS_POR_ROBOTS   %d fontes em %d hosts" % (p["FONTES"], p["HOSTS"]))
    if p["SONDA_FEITA"]:
        print("  por classe (fontes): %s" % json.dumps(p["POR_CLASSE_FONTES"], ensure_ascii=False))
        print("  LEGIVEIS_AGORA      %d de %d" % (p["LEGIVEIS_AGORA"], p["FONTES"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
