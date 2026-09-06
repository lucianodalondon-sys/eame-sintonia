#!/usr/bin/env python3
"""
pares_reconstruir.py — remonta a LISTA DE PARES DE USO fora de sintonia/canonical.

## O problema, dito sem rodeio

Toda a esteira de uso desta ferramenta lia
`sintonia/canonical @ bdb57cf — data/samples/IT-ROTULOS-V1/IT-ROTULOS-PARES-V3.json`,
um arquivo que **nao esta neste repositorio e nao esta acessivel a esta sessao**.
Sem ele, `empacotar.py`, `exclusao.py` e `payload.py` nao rodam, e um conserto
que nao pode ser reconstruido nao e um conserto: e uma afirmacao.

## O que este script faz — e o que ele NAO faz

Ele **nao le rotulo** e **nao inventa par nenhum**. Ele remonta a lista a partir
de dois artefatos que ESTAO versionados aqui e que sao, os dois, derivados do
proprio arquivo original:

  * `v1/dados/EXCLUSAO.json` -> `VERDICT_KEY_TRIPLE`, que grava, POR POSICAO,
    a chave `reg#i` -> `[CROP, TARGET]` dos **2928** pares originais. E a
    ordem completa, retirados inclusive.
  * `v1/dados/CASCO-PAYLOAD.json` -> `products[].uses`, que carrega, na mesma
    ordem, os **2926** pares publicados com `crop_raw`, `target_raw`, `page` e
    `route`. Os 2 que faltam sao os retirados por R-10, e a ficha deles esta em
    `EXCLUSAO.json -> RETIRADOS`.

O casamento e conferido par a par: se o `[CROP, TARGET]` de uma posicao nao
bater, o script **para**. Nao ha remendo por aproximacao.

## O que se perde, e esta escrito que se perde

O arquivo original trazia `CROP_Y` e `TARGET_Y` — a coordenada de cada nome na
pagina. Isso **nao sobreviveu** ao payload e nao ha como deduzi-lo daqui. Os
pares reconstruidos saem com `CROP_Y = NOT_PRESERVED` e `TARGET_Y = NOT_PRESERVED`,
com o nome proprio, e quem precisa da coordenada a **remede no PDF**
(`v1/inteligencia/par_validar.py` faz exatamente isso). Um campo perdido que
volta como `null` seria pior do que perdido: seria falso.

## A prova de que a reconstrucao serve

Nao e este script que decide se ele acertou. Quem decide sao dois portes:

    python3 v1/coleta/exclusao.py --pares <saida>   # tem de reproduzir o VERDICT inteiro
    python3 v1/casco/payload.py   --pares <saida>   # tem de reproduzir os `uses` inteiros

`v1/fonte/pares_conferir.py` roda os dois e compara campo a campo.

  uso:  python3 v1/fonte/pares_reconstruir.py
"""
import argparse, json, os, sys
from collections import defaultdict


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--exclusao", default="v1/dados/EXCLUSAO.json")
    ap.add_argument("--payload", default="v1/dados/CASCO-PAYLOAD.json")
    ap.add_argument("--pacote", default="v1/dados/COLLECTION-PACKAGE.json")
    ap.add_argument("--out", default="v1/dados/IT-ROTULOS-PARES-RECONSTRUIDO.json")
    a = ap.parse_args()

    exc = json.load(open(a.exclusao, encoding="utf-8"))
    pay = json.load(open(a.payload, encoding="utf-8"))
    pkg = json.load(open(a.pacote, encoding="utf-8"))
    nome = {i["REGISTRATION_ID"]: i["PRODUCT_NAME_RAW"] for i in pkg["ITEMS"]}

    trio = exc["VERDICT_KEY_TRIPLE"]
    veredito = exc["VERDICT"]
    # ficha dos retirados, que nao viajaram no payload
    ret = {}
    for r in exc["RETIRADOS"]:
        ret.setdefault(r["REGISTRATION_ID"], []).append(r)

    # os usos publicados, na ordem em que o payload os guardou
    usos = {p["reg"]: list(p.get("uses") or []) for p in pay["products"]}
    fila = {reg: iter(us) for reg, us in usos.items()}

    # as chaves reg#i, em ordem de registro e de posicao — a MESMA ordem que
    # exclusao.py usou para grava-las (sorted(por_reg), depois enumerate)
    por_reg = defaultdict(list)
    for chave in trio:
        reg, i = chave.split("#")
        por_reg[reg].append(int(i))
    for reg in por_reg:
        por_reg[reg].sort()

    pares, n_ret, n_pub = [], 0, 0
    for reg in sorted(por_reg):
        pend = list(ret.get(reg, []))
        for i in por_reg[reg]:
            crop, alvo = trio[f"{reg}#{i}"]
            est = veredito.get(f"{reg}#{i}")
            if est == "CROP_ONLY_INSIDE_EXCLUSION":
                # retirado por R-10: nao viajou no payload. A ficha do retirado
                # traz CROP_AS_WRITTEN e ROUTE; TARGET_AS_WRITTEN e PAGE nao
                # foram preservados por ninguem, e saem com o nome proprio.
                f = next((x for x in pend if [x["CROP"], x["TARGET"]] == [crop, alvo]), None)
                if f is None:
                    sys.exit(f"  {reg}#{i} diz CROP_ONLY_INSIDE_EXCLUSION e nao ha ficha "
                             f"de retirada para {crop} x {alvo} em EXCLUSAO.json")
                pend.remove(f)
                pares.append({
                    "REGISTRATION_ID": reg, "PRODUCT": nome.get(reg, "NOT_KNOWN"),
                    "CROP": crop, "TARGET": alvo,
                    "CROP_AS_WRITTEN": f.get("CROP_AS_WRITTEN"),
                    "TARGET_AS_WRITTEN": "NOT_PRESERVED",
                    "PAGE": None, "ROUTE": f.get("ROUTE"),
                    "CROP_Y": "NOT_PRESERVED", "TARGET_Y": "NOT_PRESERVED",
                    "RECONSTRUCTED_FROM": "EXCLUSAO.RETIRADOS",
                })
                n_ret += 1
                continue
            u = next(fila.get(reg, iter(())), None)
            if u is None:
                sys.exit(f"  {reg}#{i} ({crop} x {alvo}) nao tem uso correspondente no payload: "
                         f"a lista de usos deste registro acabou antes das chaves")
            if [u["crop"], u["target"]] != [crop, alvo]:
                sys.exit(f"  desalinhamento em {reg}#{i}: EXCLUSAO diz {[crop, alvo]} e o "
                         f"payload traz {[u['crop'], u['target']]}. A reconstrucao PARA: "
                         f"remendar por aproximacao faria o veredito cair no par errado.")
            pares.append({
                "REGISTRATION_ID": reg, "PRODUCT": nome.get(reg, "NOT_KNOWN"),
                "CROP": crop, "TARGET": alvo,
                "CROP_AS_WRITTEN": u.get("crop_raw"),
                "TARGET_AS_WRITTEN": u.get("target_raw"),
                "PAGE": None if u.get("page") == "NOT_PRESERVED" else u.get("page"),
                "ROUTE": u.get("route"),
                "CROP_Y": "NOT_PRESERVED", "TARGET_Y": "NOT_PRESERVED",
                "RECONSTRUCTED_FROM": "CASCO-PAYLOAD.uses",
            })
            n_pub += 1

    # nenhum uso publicado pode ter sobrado: sobra e desalinhamento silencioso
    for reg, it in fila.items():
        sobra = list(it)
        if sobra:
            sys.exit(f"  sobraram {len(sobra)} uso(s) em {reg} sem chave correspondente")

    saida = {
        "DATASET": "IT-ROTULOS-PARES-RECONSTRUIDO",
        "O_QUE_ISTO_E": ("a lista de pares de uso remontada a partir de EXCLUSAO.json e "
                         "CASCO-PAYLOAD.json, para que a esteira rode sem sintonia/canonical"),
        "O_QUE_ISTO_NAO_E": ("nao e uma leitura nova de rotulo: nenhum par foi criado, "
                             "removido ou reordenado aqui"),
        "SUBSTITUI": "sintonia/canonical @ bdb57cf — data/samples/IT-ROTULOS-V1/IT-ROTULOS-PARES-V3.json",
        "NOT_PRESERVED_FIELDS": ["CROP_Y", "TARGET_Y",
                                 "TARGET_AS_WRITTEN dos pares retirados por R-10"],
        "PAIRS_FROM_PAYLOAD": n_pub,
        "PAIRS_FROM_EXCLUSION_WITHDRAWALS": n_ret,
        "PAIRS": pares,
    }
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    json.dump(saida, open(a.out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"  {len(pares)} pares reconstruidos ({n_pub} do payload, {n_ret} de retirada) "
          f"-> {a.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
