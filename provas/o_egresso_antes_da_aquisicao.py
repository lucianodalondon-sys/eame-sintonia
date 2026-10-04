#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""O EGRESSO MEDE-SE ANTES DE ADQUIRIR — e UNKNOWN fecha a porta.

    python3 provas/o_egresso_antes_da_aquisicao.py

O QUE ESTA PROVA EXISTE PARA FECHAR
-----------------------------------
O `C-ITALIA-FIRST-REAL-COLLECTION-CANARY-V1` mediu o segundo blocker:

    o unico medidor de egresso desta casa vivia DENTRO de
    `coleta/instagram_janela.py` — ou seja, dentro de uma rota de aquisicao.

Exigir `EGRESS_COUNTRY_CODE = IT` *antes* de adquirir era, por construcao,
impossivel: para saber por onde se saia era preciso ja estar a sair.

    UM PREFLIGHT QUE SO CORRE DEPOIS DE COMECAR NAO E UM PREFLIGHT.

O QUE ELA MEDE
--------------
    A. o dono      o egresso pertence ao AMBIENTE, e nao a fonte nenhuma
    B. a norma     `it`, ` IT `, `IT` sao o mesmo pais; o resto e UNKNOWN
    C. o portao    qualquer coisa que nao seja o pais exigido BLOQUEIA
    D. a ordem     o workflow chama o preflight ANTES da aquisicao
    E. o segredo   o IP publico nao entra em lado nenhum
    F. o limite    VPN_LOCATION != SOURCE_LOCATION != FACT_LOCATION
    G. red team    10 ataques ao portao, e nenhum sobrevive

⚠️ E ELA NAO LIGA VPN NENHUMA
------------------------------
Todos os casos sao deterministicos: o corpo do checker e INJETADO. Uma prova
que so passa com a VPN ligada nao se repete, e o que nao se repete nao e prova.

A unica medicao real que esta prova faz e read-only e nao adquire nada: pergunta
ao checker publico por onde SAI esta sessao, e o resultado e o que for. Se esta
sessao nao for o runner italiano, o resultado correto e dize-lo — nunca declarar
IT por conveniencia.
"""
import io
import json
import os
import re
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for g in (RAIZ, os.path.join(RAIZ, "superficie")):
    if g not in sys.path:
        sys.path.insert(0, g)

import _gavetas                                            # noqa: E402,F401
import rede                                                # noqa: E402

def _ler(caminho):
    with io.open(caminho, encoding="utf-8") as f:
        return f.read()


CASOS = []


def caso(nome, obtido, esperado):
    CASOS.append((obtido == esperado, nome, obtido, esperado))


def main():
    # ── A · O DONO ─────────────────────────────────────────────────────
    # Procurado antes de criado: o dono do AMBIENTE ja existia.
    caso("o dono do egresso e o portao de rede, e nao um ficheiro novo",
         hasattr(rede, "portao_de_egresso") and hasattr(rede, "egresso"), True)
    novos = [f for f in os.listdir(RAIZ)
             if f.lower().startswith(("egress", "egresso"))]
    caso("nao nasceu um segundo dono do egresso na raiz", novos, [])
    # E o medidor NAO pode viver dentro de uma rota de aquisicao.
    fonte_rede = _ler(os.path.join(RAIZ, "superficie", "rede.py"))
    caso("o dono do egresso nao importa nenhum coletor",
         [l for l in fonte_rede.splitlines()
          if re.match(r"\s*(import|from)\s+(coleta|instagram|youtube|bluesky)",
                      l)], [])
    # ⚠️ E NAO NASCEU UM COMPOSITOR. Houve um `motor/preflight_da_coleta.py`
    # nesta missao, e foi deitado fora: cada dono responde por si, e a ORDEM
    # mora no workflow, que e o unico sitio onde ela e observavel.
    caso("nao ha um terceiro ficheiro a encadear os dois portoes",
         os.path.isfile(os.path.join(RAIZ, "motor", "preflight_da_coleta.py")),
         False)

    # ── B e C · A NORMA E O PORTAO ─────────────────────────────────────
    tabela = [
        ("IT maiusculo",          '{"country":"IT"}',            "IT",      "PASS"),
        ("it minusculo",          '{"country":"it"}',            "IT",      "PASS"),
        ("com espacos",           '{"country":"  IT  "}',        "IT",      "PASS"),
        ("ataque 1 · FR",         '{"country":"FR"}',            "FR",      "BLOCKED"),
        ("ataque 2 · US",         '{"country":"US"}',            "US",      "BLOCKED"),
        ("ataque 3 · timeout",    None,                          "UNKNOWN", "BLOCKED"),
        ("ataque 4 · HTTP 500",   "<html>500 Internal</html>",   "UNKNOWN", "BLOCKED"),
        ("ataque 5 · JSON partido", '{"country":',               "UNKNOWN", "BLOCKED"),
        ("ataque 6 · sem country", '{"ip":"1.2.3.4","city":"X"}', "UNKNOWN", "BLOCKED"),
        ("ataque 7 · country nao-texto", '{"country":42}',       "UNKNOWN", "BLOCKED"),
        ("ataque 8 · so espacos", '{"country":"   "}',           "UNKNOWN", "BLOCKED"),
        ("ataque 9 · tres letras", '{"country":"ITA"}',          "UNKNOWN", "BLOCKED"),
        ("ataque 10 · corpo vazio", "",                          "UNKNOWN", "BLOCKED"),
        ("lista em vez de objeto", '[{"country":"IT"}]',         "UNKNOWN", "BLOCKED"),
        ("nulo no campo",         '{"country":null}',            "UNKNOWN", "BLOCKED"),
    ]
    for nome, bruto, pais, portao in tabela:
        v = rede.portao_de_egresso("IT", bruto=bruto)
        caso("%s -> %s / %s" % (nome, pais, portao),
             (v["EGRESS_COUNTRY_CODE"], v["EGRESS_GATE"]), (pais, portao))

    caso("ACQUISITION_STARTED_ON_NON_IT = 0",
         len([1 for n, b, p, g in tabela
              if p not in ("IT", "UNKNOWN")
              and rede.portao_de_egresso("IT", bruto=b)["EGRESS_GATE"] == "PASS"]), 0)
    caso("ACQUISITION_STARTED_ON_UNKNOWN = 0",
         len([1 for n, b, p, g in tabela
              if p == "UNKNOWN"
              and rede.portao_de_egresso("IT", bruto=b)["EGRESS_GATE"] == "PASS"]), 0)

    # ⚠️ E A COSTURA NAO PODE SER AMBIGUA. A primeira versao usava `None` para
    # dizer «nao me deram corpo, vai medir» — e `None` e TAMBEM o que o checker
    # devolve quando nao respondeu. A prova do timeout foi a rede a serio e
    # voltou com um pais verdadeiro: um caso de red team passou por acidente.
    #
    #     DOIS SIGNIFICADOS NO MESMO VALOR E COMO SE LE O ERRADO.
    caso("o `None` injetado quer dizer «nao respondeu», e nao «vai medir»",
         rede.egresso(bruto=None)["EGRESS_COUNTRY_CODE"], "UNKNOWN")

    # ── D · A ORDEM NO WORKFLOW ────────────────────────────────────────
    # MODULE EXISTS != EDGE EXISTS. Um portao que existe e nao e chamado antes
    # da aquisicao nao protege nada.
    with io.open(os.path.join(RAIZ, ".github", "workflows",
                              "sintonia-scrap.yml"), encoding="utf-8") as f:
        yml = f.read()
    pos_sala = yml.find("sala_de_espera.py --portao")
    pos_egresso = yml.find("rede.py --portao-de-egresso")
    pos_orq = yml.find("orquestrador/orquestrador.py")
    caso("o workflow canonico chama o portao da sala", pos_sala >= 0, True)
    caso("e o portao do egresso", pos_egresso >= 0, True)
    caso("a sala vem primeiro: nao custa rede, e e a que invalida tudo",
         pos_sala < pos_egresso, True)
    caso("e os dois vem ANTES do orquestrador que adquire",
         pos_sala >= 0 and pos_orq >= 0 and max(pos_sala, pos_egresso) < pos_orq,
         True)
    # E o passo tem de PARAR o job. Um passo que imprime BLOCKED e devolve zero
    # deixa a aquisicao seguinte arrancar.
    # ⚠️ E O AMBIENTE APROVADO TEM DE SER O AMBIENTE DA AQUISICAO.
    # A primeira versao deste passo declarava `SINTONIA_SALA_BACKEND` SO dentro
    # do proprio preflight. O portao passava — e o passo seguinte, o que adquire,
    # corria sem a variavel e escrevia o READY no ficheiro efemero.
    #
    #     UM PORTAO QUE MEDE UM AMBIENTE E DEIXA PASSAR PARA OUTRO
    #     NAO MEDIU NADA.
    import yaml
    d = yaml.safe_load(yml)
    job = d["jobs"]["coleta"]
    caso("o backend canonico e declarado no NIVEL DO JOB, e nao so no preflight",
         (job.get("env") or {}).get("SINTONIA_SALA_BACKEND"), "POSTGRES")
    passos = [st for st in job["steps"]
              if str(st.get("name", "")).startswith(("5b", "5c"))]
    caso("os dois portoes existem e nenhum tem ambiente proprio",
         len(passos) == 2 and not any(st.get("env") for st in passos), True)

    caso("e o preflight sai com codigo (o `--portao-de-egresso` tambem)",
         "sys.exit(0 if v['EGRESS_GATE'] == 'PASS' else 1)"
         in _ler(os.path.join(RAIZ, "superficie", "rede.py")), True)

    # ── E · O SEGREDO ──────────────────────────────────────────────────
    v = rede.portao_de_egresso("IT", bruto='{"country":"IT","ip":"203.0.113.7",'
                                           '"city":"Milano","org":"AS1 X"}')
    texto = json.dumps(v, ensure_ascii=False)
    caso("o IP publico nao entra no resultado", "203.0.113.7" in texto, False)
    caso("nem a cidade, nem a organizacao",
         ("Milano" in texto) or ("AS1 X" in texto), False)
    caso("o que fica e o pais, o momento e o checker",
         sorted(k for k in v if k.startswith("EGRESS") or k in
                ("CHECKED_AT", "CHECKER")),
         ["CHECKED_AT", "CHECKER", "EGRESS_COUNTRY_CODE", "EGRESS_GATE",
          "EGRESS_REQUIRED"])

    # ── F · O LIMITE ───────────────────────────────────────────────────
    caso("o resultado declara o que NAO prova",
         "VPN_LOCATION != SOURCE_LOCATION" in v["O_QUE_ISTO_NAO_PROVA"], True)
    caso("e nada aqui se chama SOURCE_LOCATION ou FACT_LOCATION",
         [k for k in v if k in ("SOURCE_LOCATION", "FACT_LOCATION")], [])

    # ── A MEDICAO REAL, READ-ONLY ──────────────────────────────────────
    real = rede.egresso()
    print()
    print("REAL_RUNNER_EGRESS=%s" % real["EGRESS_COUNTRY_CODE"])
    print("  (esta sessao. NAO e o runner italiano a menos que diga IT, e "
          "declarar IT sem medir seria fabricar ambiente.)")

    reprovados = [c for c in CASOS if not c[0]]
    print()
    for ok, nome, obtido, esperado in CASOS:
        print("  %-5s %s" % ("ok" if ok else "FALHA", nome))
        if not ok:
            print("          esperado: %r" % (esperado,))
            print("          obtido:   %r" % (obtido,))
    print()
    print("=" * 66)
    ataques = len([c for c in CASOS if "ataque" in c[1]])
    print("CASOS=%d · PASS=%d · FAIL=%d"
          % (len(CASOS), len(CASOS) - len(reprovados), len(reprovados)))
    print("RED_TEAM_ATTACKS=%d · RED_TEAM_SURVIVORS=%d"
          % (ataques, len([c for c in reprovados if "ataque" in c[1]])))
    print("EGRESSO_ANTES_DA_AQUISICAO=%s" % ("PASS" if not reprovados else "FAIL"))
    print("=" * 66)
    return 1 if reprovados else 0


if __name__ == "__main__":
    raise SystemExit(main())
