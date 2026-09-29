# -*- coding: utf-8 -*-
"""LINHA-BUSCA · 4) o PEDIDO do workflow `linha-busca-google.yml` e o RESUMO da corrida. Sem rede, sem segredo.

    python3 ferramentas/linha_busca/pedido_actions.py            >> $GITHUB_OUTPUT   (le o pedido, escreve as saidas)
    python3 ferramentas/linha_busca/pedido_actions.py --resumo=saida >> $GITHUB_STEP_SUMMARY

O pedido vem do ficheiro PEDIDO-BUSCA-GOOGLE.json ao lado (o workflow dispara por PUSH no proprio ramo). Nao passa
segredo nenhum: a chave e sempre o secret YOUTUBE_DATA_API_KEY, escrito FIXO no workflow (coordenacao 12:20 — um
`secrets[...]` pelo nome faria o GitHub entregar TODOS os secrets do repositorio ao runner).
"""
from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
PEDIDO = AQUI / "PEDIDO-BUSCA-GOOGLE.json"
RE_CX = re.compile(r"^[A-Za-z0-9:_-]{1,64}$")
N_MAX = 100


class PedidoInvalido(ValueError):
    pass


def ler_pedido(ficheiro: Path = PEDIDO) -> dict:
    """O pedido do ficheiro (o workflow dispara por PUSH no proprio ramo: nao ha inputs). So o que nao e segredo."""
    bruto = json.loads(Path(ficheiro).read_text(encoding="utf-8"))
    out = {}
    try:
        n = int(str(bruto.get("N", "4")).strip())
    except ValueError:
        raise PedidoInvalido("N nao e numero: %r" % bruto.get("N")) from None
    if not 1 <= n <= N_MAX:
        raise PedidoInvalido("N=%d fora de 1..%d (quota gratis da Custom Search JSON API)" % (n, N_MAX))
    out["N"] = n
    for k, omissao in (("SO_DIAGNOSTICO", True), ("COMENTARIOS", True)):
        v = bruto.get(k, omissao)
        out[k] = v if isinstance(v, bool) else str(v).strip().lower() != "false"
    # O CX e o ID PUBLICO do mecanismo de pesquisa (nao e senha: sem a chave nao serve). Hoje nao existe (medido
    # pela coordenacao 12:20: nao ha secret de CX). Se o dono o criar, entra aqui — e so nesta forma.
    cx = str(bruto.get("CX") or "").strip()
    if cx and not RE_CX.match(cx):
        raise PedidoInvalido("CX com forma inesperada: so letras, algarismos, «:», «_» e «-» (ate 64)")
    out["CX"] = cx
    return out


def saidas(p: dict) -> str:
    return "\n".join(["n=%d" % p["N"], "so_diagnostico=%s" % ("true" if p["SO_DIAGNOSTICO"] else "false"),
                      "comentarios=%s" % ("true" if p["COMENTARIOS"] else "false"), "cx=%s" % p["CX"]]) + "\n"


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
                    ("BUSCA_POSSIVEL", "a busca pode correr?"), ("HTTP", "resposta do Google (HTTP)"),
                    ("ESCOPO_INDICIO", "a web inteira ou so alguns sites? (indicio)")):
        linhas.append("| %s | %s |" % (nome, API.redigir(x.get(k))))
    linhas += ["", "**Porque:** %s" % API.redigir(x.get("PORQUE")), "", "**O que o dono tem de fazer:**"]
    linhas += ["%d. %s" % (i, API.redigir(p)) for i, p in enumerate(x.get("O_QUE_O_DONO_FAZ") or [], 1)]
    c = Path(pasta) / "COMENTARIOS-PILOTO-D106.json"
    if c.exists():
        y = json.loads(c.read_text(encoding="utf-8"))
        linhas += ["", "## Piloto de comentarios (D106)", "",
                   "%d chamadas de %d · HTTP 200 em %d · %d threads · videos com comentario: %s" % (
                       y.get("CHAMADAS", 0), y.get("TETO_CHAMADAS", 0), y.get("COM_200", 0), y.get("ITENS_TOTAL", 0),
                       ", ".join(y.get("VIDEOS_COM_COMENTARIO") or []) or "nenhum")]
        if y.get("PAROU"):
            linhas.append("**Parou:** %s" % API.redigir(y["PAROU"]))
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
