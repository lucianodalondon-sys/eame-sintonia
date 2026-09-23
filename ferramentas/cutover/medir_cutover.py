"""Medidores do CUTOVER (missao X1) — so leitura; nada e escrito em lado nenhum.

    py ferramentas/cutover/medir_cutover.py pre   --viva <pasta viva> --final <ref do FINAL_HEAD>
    py ferramentas/cutover/medir_cutover.py livros --pasta <worktree unificada> --corte <dir do corte>
    py ferramentas/cutover/medir_cutover.py pos   --viva <pasta viva>

Cada verificacao devolve OK / PARAR (ou LEVAR_NO_5B), e o PORQUE. Sai com 2 se houver PARAR. Nasceram do ensaio geral (X1): cada
uma apanha um defeito que o ensaio encontrou num SWITCH_PLAN seguido a letra.

pre     A1 HEAD vivo ancestral do FINAL_HEAD (senao a troca tira codigo de producao)
        A2 candidatas e SOURCE-ID-ALLOCATION: quantas existem SO na pasta viva
           (o `git checkout -- .` do passo de troca deita-as fora se ninguem as levar)
        A3 os ficheiros sujos da viva que sao CODIGO, nao livros
livros  B1 o corte continua integro (sha256 do CORTE.json) — o pacote G1 NAO pode
           escrever la dentro, senao a reconciliacao recusa o corte
        B2 candidatas e alocacao da linha >= as do corte (A2 resolvido)
        B3 a marca CONTRATO_UNICO (D10) esta no livro que o bot vai correr
        B4 as 7 da D10 em CANARY_PENDING SEM tarefa aberta (ninguem as volta a medir);
           e, informativo, todas as paradas sem tarefa (440 antes / 517 depois, no ensaio)
        B5 portao: elegiveis e RETIRADA_POR_DECISAO recusadas
pos     C1 um so worker lancado de cada vez (pelo diario), saida limpa rc 0
        C2 servico RUNNING ou IDLE; PID_CHECK_NAO_SEI vazio (supervisor.py --estado)
"""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

D10 = ("IT-T10-018", "IT-T10-022", "IT-T5-049", "IT-T7-017", "IT-T7-033", "IT-T7-042", "IT-T7-043")
ABERTAS = ("PENDING", "WAITING_RETRY", "IN_PROGRESS")


def _j(p: Path):
    return json.loads(Path(p).read_text(encoding="utf-8"))


def _git(cwd, *a) -> subprocess.CompletedProcess:
    return subprocess.run(["git", *a], cwd=str(cwd), capture_output=True, text=True,
                          encoding="utf-8", errors="replace")


def so_de_um_lado(a: list, b: list, chave: str) -> dict:
    """Quantos ids existem so em a, so em b (listas de dicts com `chave`)."""
    ia, ib = {x[chave] for x in a}, {x[chave] for x in b}
    return {"SO_NO_PRIMEIRO": len(ia - ib), "SO_NO_SEGUNDO": len(ib - ia),
            "PRIMEIRO": len(ia), "SEGUNDO": len(ib)}


def presas_sem_tarefa(transicoes: list, tarefas: list, fontes=None) -> list[str]:
    """Fontes cujo ULTIMO estado e CANARY_PENDING e que nao tem tarefa aberta."""
    ult = {}
    for t in transicoes:
        ult[t["SOURCE_ID"]] = t["NEW_STATE"]
    com_tarefa = {t["SOURCE_ID"] for t in tarefas if t["STATUS"] in ABERTAS}
    alvo = fontes if fontes is not None else ult.keys()
    return sorted(s for s in alvo if ult.get(s) == "CANARY_PENDING" and s not in com_tarefa)


def _v(ok: bool, porque: str, falha: str = "PARAR") -> dict:
    return {"VEREDITO": "OK" if ok else falha, "PORQUE": porque}


NAO_FINAIS = ("CANARY_PENDING", "CONTRACTED_CANARY_FAILED", "CONTRACT_PENDING", "DEGRADED",
              "REPAIRING", "RETRY_AFTER")


def paradas_sem_tarefa(transicoes: list, tarefas: list) -> dict:
    """Informativo: estados nao finais sem tarefa aberta, por estado. Medido no ensaio:
    440 no bot vivo antes da troca, 517 na linha unida — o problema geral de quem
    re-mede o que falhou, anterior ao cutover (so as 7 da D10 sao do cutover)."""
    from collections import Counter
    ult = {}
    for t in transicoes:
        ult[t["SOURCE_ID"]] = t["NEW_STATE"]
    ab = {t["SOURCE_ID"] for t in tarefas if t["STATUS"] in ABERTAS}
    return dict(Counter(e for s, e in ult.items() if s not in ab and e in NAO_FINAIS))


# ── pre ───────────────────────────────────────────────────────────────────────
def pre(viva: Path, final: str) -> dict:
    h = _git(viva, "rev-parse", "HEAD").stdout.strip()
    anc = _git(viva, "merge-base", "--is-ancestor", h, final).returncode == 0
    out = {"HEAD_VIVO": h[:8], "A1_ANCESTRAL": _v(anc, "HEAD vivo %s %s ancestral de %s"
                                                  % (h[:8], "e" if anc else "NAO e", final))}
    for rel, k, ch in (("candidatas/FONTES-CANDIDATAS.json", "CANDIDATAS", "CANDIDATA_ID"),
                       ("curadoria/SOURCE-ID-ALLOCATION-V1.json", "NOVAS", "SOURCE_ID")):
        linha = json.loads(_git(viva, "show", "%s:%s" % (final, rel)).stdout or '{"%s": []}' % k)[k]
        c = so_de_um_lado(_j(viva / rel)[k], linha, ch)
        out["A2_" + rel.split("/")[-1]] = dict(c, **_v(c["SO_NO_PRIMEIRO"] == 0,
            "%d so na viva: tem de ser levado para a linha antes da troca (passo 5b)"
            % c["SO_NO_PRIMEIRO"] if c["SO_NO_PRIMEIRO"] else "nada so na viva",
            falha="LEVAR_NO_5B"))
    sujos = [l[3:] for l in _git(viva, "status", "--short").stdout.splitlines()]
    codigo = [s for s in sujos if s.endswith((".py", ".mjs", ".js"))]
    diff = {s: bool(_git(viva, "diff", "--ignore-cr-at-eol", "--quiet", "--", s).returncode) for s in codigo}
    out["A3_SUJOS"] = {"TOTAL": len(sujos), "CODIGO": codigo,
                       "CODIGO_COM_CONTEUDO_DIFERENTE": [s for s, d in diff.items() if d],
                       **_v(not any(diff.values()), "codigo sujo so com fim de linha" if codigo else "sem codigo sujo")}
    return out


# ── livros ────────────────────────────────────────────────────────────────────
def livros_corte_integro(corte: Path) -> dict:
    man = _j(corte / "CORTE.json")
    shas = man.get("SHA256") or {k: v.get("SHA256") for k, v in (man.get("FICHEIROS") or {}).items() if v}
    mal = [n for n, s in shas.items() if (corte / n).exists()
           and hashlib.sha256((corte / n).read_bytes()).hexdigest() != s]
    return _v(not mal, "alterados depois do corte: %s" % mal if mal else "sha256 confere")


def livros(pasta: Path, corte: Path) -> dict:
    out = {"B1_CORTE_INTEGRO": livros_corte_integro(corte)}
    cur = pasta / "curadoria"
    tr = _j(cur / "LIFECYCLE-LEDGER-V1.json")["TRANSICOES"]
    ta = _j(cur / "LIFECYCLE-QUEUE-V1.json")["TAREFAS"]
    contratos = {c["SOURCE_ID"]: c for c in _j(cur / "italy_contracts_curator.json")["FONTES"]}
    marcadas = [s for s in D10 if (contratos.get(s) or {}).get("CONTRATO_UNICO")]
    out["B3_MARCA_D10_NO_LIVRO_DO_BOT"] = dict(MARCADAS=marcadas, **_v(
        len(marcadas) >= 6, "%d/7 com CONTRATO_UNICO no livro que o bot corre (a B3 prova 6)" % len(marcadas)))
    presas = presas_sem_tarefa(tr, ta, D10)
    out["B4_D10_SEM_TAREFA"] = dict(FONTES=presas, **_v(
        not presas, "%d das 7 da D10 em CANARY_PENDING sem ninguem que as re-meça (passo 7b)"
        % len(presas) if presas else "nenhuma"))
    out["B4_INFO_PARADAS_SEM_TAREFA"] = paradas_sem_tarefa(tr, ta)
    for rel, k, ch in (("candidatas/FONTES-CANDIDATAS.json", "CANDIDATAS", "CANDIDATA_ID"),
                       ("curadoria/SOURCE-ID-ALLOCATION-V1.json", "NOVAS", "SOURCE_ID")):
        f = corte.parent / "servico-extras" / rel.split("/")[-1]
        if not f.exists():
            f = corte / rel.split("/")[-1]
        if f.exists():
            c = so_de_um_lado(_j(f)[k], _j(pasta / rel)[k], ch)
            out["B2_" + rel.split("/")[-1]] = dict(c, **_v(c["SO_NO_PRIMEIRO"] == 0,
                "%d do corte faltam na linha" % c["SO_NO_PRIMEIRO"]))
    sys.path.insert(0, str(cur))
    import collection_gate as CG  # noqa: E402
    el = sorted(CG.elegiveis())
    ret = [s for s, c in contratos.items() if c.get("ESTADO_CATALOGO") == "RETIRADA_POR_DECISAO"]
    recus = [s for s in ret if (CG.avaliar(s) or {}).get("MOTIVO") == "RETIRADA_POR_DECISAO"]
    out["B5_PORTAO"] = {"ELEGIVEIS": len(el), "LISTA": el, "RETIRADAS": len(ret),
                        "RETIRADAS_RECUSADAS": len(recus), **_v(len(recus) == len(ret), "retiradas recusadas %d/%d" % (len(recus), len(ret)))}
    return out


# ── pos ───────────────────────────────────────────────────────────────────────
def pos(viva: Path) -> dict:
    cur = viva / "curadoria"
    ev = [json.loads(l) for l in (cur / "SOURCE-CURATOR-RUN-LOG.ndjson").read_text(encoding="utf-8").splitlines() if l.strip()]
    i = max((k for k, e in enumerate(ev) if e.get("EVENTO") == "SUPERVISOR_ARRANQUE"), default=0)
    ev = ev[i:]
    vivos, sobrepostos = set(), 0
    for e in ev:
        if e.get("EVENTO") == "WORKER_RELANCADO":
            if vivos:
                sobrepostos += 1
            vivos.add(e.get("PID"))
        elif e.get("EVENTO") in ("WORKER_MORTO", "WORKER_SAIU_LIMPO"):
            vivos.discard(e.get("PID"))
    rc = [e.get("RC") for e in ev if e.get("EVENTO") == "WORKER_MORTO"]
    out = {"C1_UM_WORKER": dict(LANCAMENTOS=sum(e.get("EVENTO") == "WORKER_RELANCADO" for e in ev),
                                RC=rc, **_v(sobrepostos == 0 and all(r == 0 for r in rc),
                                           "%d lancamentos sobrepostos; rc %s" % (sobrepostos, rc)))}
    est = subprocess.run([sys.executable, str(cur / "supervisor.py"), "--estado"], cwd=str(viva),
                         capture_output=True, text=True, encoding="utf-8", errors="replace")
    try:
        e = json.loads(est.stdout[est.stdout.index("{"):])
    except ValueError:
        e = {}
    out["C2_ESTADO"] = {k: e.get(k) for k in ("SOURCE_CURATOR_SERVICE", "WORKER_STATE", "HEARTBEAT_AGE_S",
                                              "PID_CHECK_NAO_SEI")}
    out["C2_ESTADO"].update(_v(not e.get("PID_CHECK_NAO_SEI") and e.get("SOURCE_CURATOR_SERVICE") in ("RUNNING", "IDLE"),
                               "servico %s, NAO SEI %s" % (e.get("SOURCE_CURATOR_SERVICE"), e.get("PID_CHECK_NAO_SEI"))))
    return out


def main(argv=None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    modo = argv[0]
    arg = {argv[i][2:]: argv[i + 1] for i in range(1, len(argv) - 1, 2) if argv[i].startswith("--")}
    r = (pre(Path(arg["viva"]), arg["final"]) if modo == "pre" else
         livros(Path(arg["pasta"]), Path(arg["corte"])) if modo == "livros" else
         pos(Path(arg["viva"])))
    print(json.dumps(r, ensure_ascii=False, indent=1))
    return 2 if any(isinstance(v, dict) and v.get("VEREDITO") == "PARAR" for v in r.values()) else 0


if __name__ == "__main__":
    raise SystemExit(main())
