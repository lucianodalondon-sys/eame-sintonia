# -*- coding: utf-8 -*-
"""CANAIS-41 · separa o que a regua pode escrever no livro do que e defeito NOSSO.

    py ferramentas/canais41/para_aplicar.py --regua REGUA.json --corridas CORRIDAS.json \
        --saida CORRIDAS-A-APLICAR.json

`regua_social.py --aplicar` escreve TODAS as linhas que recebe: READY promove, FALHA vai a
CONTRACTED_CANARY_FAILED. Uma FALHA que nasce do nosso lado (sem chave, teto nosso, banco
sem RAW, envelope trocado, Atlas) nao e da fonte — escreve-la condenava uma fonte boa por
defeito nosso (UM TIMEOUT NAO E UM DISALLOW). Este filtro deixa passar so:
  READY                       -> promove
  FALHA com causa na FONTE    -> CONTRACTED_CANARY_FAILED, com o porque
e guarda o resto (ZERO e FALHA nossa) para voltar a medir, com o motivo.
"""
import json
import sys
from pathlib import Path

# o texto do `PORQUE` da regua (curadoria/regua_social.py) que aponta para o NOSSO lado
NOSSO = ("CREDENTIAL", "BUDGET_EXHAUSTED", "RATE_LIMITED", "QUOTA", "linhas RAW no banco",
         "o envelope e de", "o Atlas nao conhece", "RESULT=None", "RESULT=ERROR", "RESULT=PARTIAL",
         "sem autorizacao do dono escrita", "OWNER_AUTHORIZED", "PLATFORM_POLICY_STATUS")


def classe(linha: dict) -> str:
    v, p = linha["VEREDITO"], linha.get("PORQUE") or ""
    if v == "READY":
        return "APLICAR"
    if v == "ZERO":
        return "REMEDIR_DEPOIS"
    if any(k in p for k in NOSSO):
        return "DEFEITO_NOSSO"
    return "APLICAR"


def main(argv) -> int:
    arg = dict(a[2:].split("=", 1) for a in argv[1:] if a.startswith("--") and "=" in a)
    regua = json.loads(Path(arg["regua"]).read_text(encoding="utf-8"))["LINHAS"]
    corridas = json.loads(Path(arg["corridas"]).read_text(encoding="utf-8"))
    por_run = {(x["SOURCE_ID"], x["RUN_ID"]): k for k, x in corridas.items()}
    aplicar, fora = {}, []
    for l in regua:
        c = classe(l)
        k = por_run.get((l["SOURCE_ID"], l["RUN_ID"]))
        if c == "APLICAR" and k:
            aplicar[k] = corridas[k]
        else:
            fora.append({"SOURCE_ID": l["SOURCE_ID"], "RUN_ID": l["RUN_ID"], "CLASSE": c,
                         "VEREDITO": l["VEREDITO"], "PORQUE": l.get("PORQUE")})
    Path(arg["saida"]).write_text(json.dumps(aplicar, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    Path(arg["saida"]).with_suffix(".fora.json").write_text(
        json.dumps(fora, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print("APLICAR=%d FORA=%d (%s)" % (len(aplicar), len(fora),
                                        ", ".join(sorted({f["CLASSE"] for f in fora})) or "-"))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
