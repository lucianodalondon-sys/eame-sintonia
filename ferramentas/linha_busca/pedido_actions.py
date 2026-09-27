# -*- coding: utf-8 -*-
"""LINHA-BUSCA · 4) o PEDIDO do workflow `linha-busca-google.yml` e o RESUMO da corrida. Sem rede, sem segredo.

    python3 ferramentas/linha_busca/pedido_actions.py            >> $GITHUB_OUTPUT   (le o pedido, escreve as saidas)
    python3 ferramentas/linha_busca/pedido_actions.py --resumo=saida >> $GITHUB_STEP_SUMMARY

O pedido vem dos inputs do `workflow_dispatch` (ambiente EVENTO=workflow_dispatch, IN_*) ou, num push, do ficheiro
PEDIDO-BUSCA-GOOGLE.json ao lado. Aqui so passam NOMES de secret — nunca o valor — e cada nome e conferido: so
maiusculas, algarismos e `_` (o nome vai parar a uma expressao `secrets[...]`; texto livre ali seria uma porta).
"""
from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
PEDIDO = AQUI / "PEDIDO-BUSCA-GOOGLE.json"
RE_NOME = re.compile(r"^[A-Z][A-Z0-9_]{0,99}$")
N_MAX = 100


class PedidoInvalido(ValueError):
    pass


def ler_pedido(env=None, ficheiro: Path = PEDIDO) -> dict:
    env = os.environ if env is None else env
    if env.get("EVENTO") == "workflow_dispatch":
        bruto = {"SEGREDO_DA_CHAVE": env.get("IN_CHAVE"), "SEGREDO_DO_CX": env.get("IN_CX"),
                 "N": env.get("IN_N"), "SO_DIAGNOSTICO": env.get("IN_SO_DIAG")}
    else:
        bruto = json.loads(Path(ficheiro).read_text(encoding="utf-8"))
    out = {}
    for k in ("SEGREDO_DA_CHAVE", "SEGREDO_DO_CX"):
        v = str(bruto.get(k) or "").strip()
        if not RE_NOME.match(v) or v.startswith("GITHUB_"):
            raise PedidoInvalido("%s invalido: %r (so MAIUSCULAS, algarismos e _; nunca GITHUB_*)" % (k, v))
        out[k] = v
    try:
        n = int(str(bruto.get("N", "4")).strip())
    except ValueError:
        raise PedidoInvalido("N nao e numero: %r" % bruto.get("N")) from None
    if not 1 <= n <= N_MAX:
        raise PedidoInvalido("N=%d fora de 1..%d (quota gratis da Custom Search JSON API)" % (n, N_MAX))
    out["N"] = n
    so = bruto.get("SO_DIAGNOSTICO", True)
    out["SO_DIAGNOSTICO"] = so if isinstance(so, bool) else str(so).strip().lower() != "false"
    return out


def saidas(p: dict) -> str:
    return "\n".join(["segredo_da_chave=%s" % p["SEGREDO_DA_CHAVE"], "segredo_do_cx=%s" % p["SEGREDO_DO_CX"],
                      "n=%d" % p["N"], "so_diagnostico=%s" % ("true" if p["SO_DIAGNOSTICO"] else "false")]) + "\n"


def resumo(pasta: Path) -> str:
    sys.path.insert(0, str(AQUI))
    import api_oficial as API                                          # noqa: PLC0415
    linhas = ["## LINHA-BUSCA · busca do Google pela API oficial", ""]
    d = Path(pasta) / "DIAGNOSTICO.json"
    if not d.exists():
        return "\n".join(linhas + ["**Sem DIAGNOSTICO.json** — o passo 2 nao chegou a correr.", ""])
    x = json.loads(d.read_text(encoding="utf-8"))
    linhas += ["| pergunta | resposta |", "|---|---|"]
    for k, nome in (("API_ATIVA", "a Custom Search JSON API esta ativa no projeto?"),
                    ("CHAVE_PODE_USAR_A_API", "a chave pode usa-la?"), ("CX", "o CX"),
                    ("BUSCA_POSSIVEL", "a busca pode correr?"), ("HTTP", "resposta do Google (HTTP)")):
        linhas.append("| %s | %s |" % (nome, API.redigir(x.get(k))))
    linhas += ["", "**Porque:** %s" % API.redigir(x.get("PORQUE")), "", "**O que o dono tem de fazer:**"]
    linhas += ["%d. %s" % (i, API.redigir(p)) for i, p in enumerate(x.get("O_QUE_O_DONO_FAZ") or [], 1)]
    r = Path(pasta) / "RESULTADOS.json"
    if r.exists():
        rs = json.loads(r.read_text(encoding="utf-8"))
        linhas += ["", "**Busca:** %d resultados, %d erros, %d consultas." % (
            sum(1 for y in rs if y.get("URL")), sum(1 for y in rs if y.get("ERRO")),
            len({y.get("CONSULTA_ID") for y in rs}))]
    return "\n".join(linhas) + "\n"


def main(argv=None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    a = dict(x[2:].split("=", 1) for x in argv if x.startswith("--") and "=" in x)
    if "resumo" in a:
        sys.stdout.write(resumo(Path(a["resumo"])))
        return 0
    try:
        sys.stdout.write(saidas(ler_pedido()))
    except PedidoInvalido as e:
        print("PEDIDO_INVALIDO: %s" % e, file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
