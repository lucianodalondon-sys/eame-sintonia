#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""O ENSAIO COMPLETO do PORTAL-PUBLICA-SOZINHO (D126) — sem publicar de verdade.

    python3 provas/portal_publica_sozinho/ensaio.py <pasta-de-trabalho> <saida.json>

Corre o publicador REAL (montagem por git worktree, as conferencias de verdade, o navegador de verdade) contra o
ANFITRIAO LOCAL do ensaio (deployments + alias em 127.0.0.1). Nada sai da maquina; nenhum --prod na nuvem.

⚠️ DADO SINTETICO DECLARADO: os potes sao os de tests/fixtures/pote/ (todo id SINT-).

CENARIOS
  A  pote novo e valido                      -> PUBLICADO, com antes/depois
  B  o mesmo pote outra vez                  -> NADA_A_PUBLICAR
  C  segundo pote                            -> PUBLICADO, e o primeiro vira POTE-ANTERIOR (com SHA)
  D  pote sem bula (D123)                    -> BLOQUEADO no C0, nada vai ao ar
  E  a pagina no ar SEM a contagem           -> REVERTIDO sozinho, volta provada, ALERTA
  F  a volta que NAO roda                    -> ALERTA_CRITICO
  G  producao pelo anfitriao de ensaio       -> BLOQUEADO

A e o unico que corre C1+C2+C3 por inteiro (C3 = os 73 portoes + o System Map: ~10 min). C, E e F reusam as
linhas de C1/C2/C3 que A mediu NO MESMO COMMIT, e dizem-no no registo (NOTA). O resto e real em todos.
"""
import copy
import json
import shutil
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ / "portoes"))
sys.path.insert(0, str(RAIZ))
import _gavetas  # noqa: E402,F401
import publicar_portal_sozinho as P  # noqa: E402

FIX = RAIZ / "tests" / "fixtures" / "pote"
STUB = (RAIZ / "italia-portale" / "client" / "sintonia-pote-publicado.js").read_text(encoding="utf-8")


class ComCodigoJaConferido(P.Publicador):
    linhas_do_codigo = None

    def conferir_codigo(self, copia):
        return [dict(l, NOTA=((l.get("NOTA") + " · ") if l.get("NOTA") else "") +
                     "medido no cenario A, mesmo commit") for l in self.linhas_do_codigo]


class ImplantaSemOPote(P.EnsaioLocal):
    """O defeito: o deploy leva o lugar vazio em vez do envelope — a pagina no ar sem a contagem."""
    def implantar(self, copia, prod):
        novo = super().implantar(copia, prod)
        (self.pasta / "deployments" / novo["ID"] / "sintonia-pote-publicado.js").write_text(STUB, encoding="utf-8")
        return novo


class NaoVolta(ImplantaSemOPote):
    """O defeito: o rollback diz que rodou e nao mexe em nada."""
    def voltar(self, anterior):
        return True


def main():
    trab, saida = Path(sys.argv[1]), Path(sys.argv[2])
    if trab.exists():
        shutil.rmtree(trab)
    reg = trab / "PUBLICACOES"
    contrato = P.carregar_contrato()
    pote = P.ler_pote(FIX / "POTE-SINTETICO-PUBLICA-SOZINHO.json")
    pote2 = copy.deepcopy(pote)
    pote2["CORTE"] = "2026-09-28T06:00:00+00:00"
    sem_bula = P.ler_pote(FIX / "POTE-SINTETICO.json")
    res = {}

    def registo(r):
        return json.loads(sorted(r.rglob("REGISTO.json"), key=lambda p: p.stat().st_mtime)[-1].read_text(encoding="utf-8"))

    def cenario(nome, esperado, imp, pub_cls, p, modo="ensaio", r=None):
        r = r or reg
        pub = pub_cls(contrato, imp, r, modo)
        rc = pub.publicar(p, origem=nome)
        R = registo(r)
        R["_ALERTAS_DESTE_REGISTO"] = [json.loads(a) for a in (r / "ALERTAS.jsonl").read_text(encoding="utf-8").splitlines()] \
            if (r / "ALERTAS.jsonl").exists() else []
        res[nome] = {"ESPERADO": esperado, "RC": rc, "ESTADO": R["ESTADO"], "REGISTO": R,
                     "OK": R["ESTADO"] == esperado}
        print(f"\n### {nome}: {R['ESTADO']} (esperado {esperado}) rc={rc}\n")
        return R

    cliente = RAIZ / "italia-portale" / "client"
    host = P.EnsaioLocal(trab / "host")
    host.semear(cliente)
    try:
        A = cenario("A_POTE_NOVO", "PUBLICADO", host, P.Publicador, pote)
        ComCodigoJaConferido.linhas_do_codigo = [l for l in A["CONFERENCIAS"] if l["ID"].startswith(("C1_BUILD_GATE", "C2_", "C3_"))]
        cenario("B_O_MESMO_POTE", "NADA_A_PUBLICAR", host, P.Publicador, pote)
        cenario("C_SEGUNDO_POTE", "PUBLICADO", host, ComCodigoJaConferido, pote2)
        cenario("D_POTE_SEM_BULA", "BLOQUEADO", host, P.Publicador, sem_bula)
    finally:
        host.fechar()
    for nome, cls, esperado in (("E_PAGINA_NO_AR_SEM_CONTAGEM", ImplantaSemOPote, "REVERTIDO"),
                                ("F_VOLTA_QUE_NAO_RODA", NaoVolta, "ALERTA_CRITICO")):
        h = cls(trab / ("host-" + nome))
        h.semear(cliente)
        try:
            cenario(nome, esperado, h, ComCodigoJaConferido, pote, r=trab / ("PUBLICACOES-" + nome))
        finally:
            h.fechar()
    h = P.EnsaioLocal(trab / "host-G")
    h.semear(cliente)
    try:
        cenario("G_PRODUCAO_PELO_ENSAIO", "BLOQUEADO", h, P.Publicador, pote, modo="producao", r=trab / "PUBLICACOES-G")
    finally:
        h.fechar()

    alertas = (reg / "ALERTAS.jsonl").read_text(encoding="utf-8").splitlines() if (reg / "ALERTAS.jsonl").exists() else []
    out = {"HEAD": P.correr(["git", "rev-parse", "HEAD"], RAIZ)[1].strip().splitlines()[0],
           "CENARIOS": {k: {kk: vv for kk, vv in v.items() if kk != "REGISTO"} for k, v in res.items()},
           "ALERTAS": [json.loads(a) for a in alertas],
           "REGISTOS": {k: v["REGISTO"] for k, v in res.items()},
           "ULTIMA_PUBLICACAO": json.loads((reg / "ULTIMA-PUBLICACAO.json").read_text(encoding="utf-8"))
           if (reg / "ULTIMA-PUBLICACAO.json").exists() else None}
    saida.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    ok = all(v["OK"] for v in res.values())
    print("\nENSAIO:", "TODOS OS CENARIOS COMO ESPERADO" if ok else "CENARIO FORA DO ESPERADO",
          {k: v["ESTADO"] for k, v in res.items()})
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
