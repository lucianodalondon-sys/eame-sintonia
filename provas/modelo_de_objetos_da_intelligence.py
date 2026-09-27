#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""O MODELO DE OBJETOS DA INTELLIGENCE — o instrumento que le a declaracao.

    MISSAO   C-INT-OBJECT-MODEL-01
    ESPECIE  LEITOR E JUIZ DE UM CONTRATO DECLARADO. NAO E RUNTIME.
    ESTADO   DEFINED. IMPLEMENTED = NO. OBSERVED = NO.

    python3 provas/modelo_de_objetos_da_intelligence.py     # confere a coerencia
    python3 -m unittest tests.test_modelo_de_objetos_da_intelligence -v

O QUE ESTE FICHEIRO E
---------------------
A porta de leitura de `docs/intelligence/INTELLIGENCE-OBJECT-MODEL-V1.json`, e
o juiz da coerencia interna dele. Ele NAO decide nada: espécie de objeto,
transicao permitida e portao de promocao sao decisoes humanas escritas no JSON.

    O JSON DIZ O QUE E LEI. ESTE FICHEIRO DIZ SE ESSA LEI SE SUSTENTA.

A PROPRIEDADE QUE INTERESSA — MUNDO FECHADO
--------------------------------------------
`pode_transitar` devolve `FORBIDDEN` para tudo o que nao esteja EXPLICITAMENTE
declarado permitido. A lista de proibicoes existe para nomear os ataques
conhecidos e dar-lhes razao escrita; ela NAO e a defesa.

    SE A DEFESA FOSSE A LISTA DE PROIBICOES, BASTAVA INVENTAR UM CAMINHO
    QUE NINGUEM HOUVESSE PENSADO EM PROIBIR.

Por isso `SIGNAL -> OPPORTUNITY` e proibido duas vezes: por nao estar na lista
das permitidas, e por estar na das proibidas com a razao ao lado. A primeira e
o portao; a segunda e a memoria.

O QUE ESTE FICHEIRO NAO E
-------------------------
    NAO executa nada.            NAO le a Sala de Espera.
    NAO persiste nada.           NAO importa Collection nem Portal.
    NAO e o INTELLIGENCE_RUN.    Esse continua bloqueado a montante.
"""
import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
MODELO = RAIZ / "docs" / "intelligence" / "INTELLIGENCE-OBJECT-MODEL-V1.json"

# Pontas de transicao que NAO sao objetos, e nao deviam ser. Uma transicao pode
# nomear um estado (`DESCARTADO`), um destino de reversao, ou um sitio para
# onde a Intelligence NAO pode ir (`COLETOR·ROTA·EXECUTOR`). Exigir que fossem
# objetos declarados obrigava a inventar objetos para os nomear — e nomear o
# proibido nao e cria-lo.
ROTULOS_LIVRES = {
    "DESCARTADO", "REJEITADA", "SIGNAL(RASTREADO)", "GESTAO_DA_COLETA",
    "REJEITADO·REBAIXADO·REABERTO·SUBSTITUIDO", "qualquer portao bloqueado",
    "qualquer objeto", "COLETOR·ROTA·EXECUTOR", "NAO SEI", "FALSO", "ZERO",
    "FERRAMENTA·PORTAL", "qualquer conceito novo", "SCORE alto",
    "OPPORTUNITY(A ou B)", "OPPORTUNITY(C ou D)",
    "transicao proibida", "APROVACAO HUMANA", "UNKNOWN vira facto",
    "SAIDA DE LLM", "evidencia de fonte", "ACAO",
    "OPPORTUNITY(A ou B)", "OPPORTUNITY(C ou D)",
}

# Um conceito nunca pode ter como dono um ecra. A palavra muda; o defeito nao.
DONOS_PROIBIDOS = ("PORTAL", "PORTALE", "UI", "DASHBOARD", "SCREEN", "ECRA",
                   "CARD", "COMPONENT", "REACT", "DELIVERY", "TOOL", "FERRAMENTA")

ESPECIES_VALIDAS = ("ENTITY", "RELATION", "STATE", "TRANSITION", "PROJECTION",
                    "OUTPUT", "EXTERNAL_REFERENCE", "NOT_A_CONCEPT")

SENTINELAS = ("NAO_E_CONCEITO", "RETIRED_AS_OVERLOADED_NAME")


def carregar(caminho: Path = MODELO) -> dict:
    return json.loads(caminho.read_text(encoding="utf-8"))


def objetos(m: dict) -> dict:
    return m["OBJETOS"]


def especie(m: dict, nome: str) -> str:
    return m["OBJETOS"][nome]["ESPECIE"]


def owner(m: dict, nome: str) -> str:
    return m["OBJETOS"][nome]["OWNER"]


def canonico(m: dict, nome: str) -> str:
    """O nome canonico de `nome`. Ele proprio quando ja e canonico."""
    if nome in m["OBJETOS"]:
        return nome
    a = m["ALIASES"].get(nome)
    return a["CANONICO"] if a else ""


def pode_transitar(m: dict, de: str, para: str) -> tuple:
    """`(VEREDITO, PORQUE)`. MUNDO FECHADO: o que nao esta permitido e proibido.

    A ordem importa e nao e cosmetica. Uma transicao declarada CONDITIONAL
    aparece nas duas listas — permitida com condicao, proibida sem ela — e
    quem le tem de receber a condicao, nunca o `ALLOWED` seco.
    """
    for t in m["TRANSICOES_PROIBIDAS"]:
        if t["FROM"] == de and t["TO"] == para:
            return t["VEREDITO"], t["PORQUE"]
    for t in m["TRANSICOES_PERMITIDAS"]:
        if t["FROM"] == de and t["TO"] == para:
            return t["VEREDITO"], t["PORQUE"]
    return ("FORBIDDEN",
            "nao existe aresta declarada. O mundo e fechado: o que nao esta "
            "escrito como permitido nao e permitido.")


def incoerencias(m: dict) -> list:
    """Os defeitos INTERNOS do modelo. `[]` quando nenhum.

    Isto nao mede o codigo: mede se a declaracao se sustenta a si propria. Um
    modelo incoerente e pior que nenhum — quem o le acredita nele.
    """
    achados = []
    obj = m["OBJETOS"]

    for nome, o in obj.items():
        if o["ESPECIE"] not in ESPECIES_VALIDAS:
            achados.append(f"{nome}: especie desconhecida {o['ESPECIE']}")
        if not o.get("OWNER"):
            achados.append(f"{nome}: sem dono")
        up = str(o.get("OWNER", "")).upper()
        if any(p in up for p in DONOS_PROIBIDOS):
            achados.append(f"{nome}: dono e um ecra/ferramenta ({o['OWNER']})")
        # UM OBJETO QUE NAO EXISTE NAO TEM ESTADOS NEM SAIDAS.
        if o["ESPECIE"] == "NOT_A_CONCEPT" and (o["ESTADOS"] or o["SAIDA_POSSIVEL"]):
            achados.append(f"{nome}: declarado NOT_A_CONCEPT e tem estados ou saida")
        # UMA TRANSICAO NAO TEM ESTADO PROPRIO, senao e uma entidade disfarcada.
        if o["ESPECIE"] == "TRANSITION" and o["PERSISTIDO"].startswith("SIM —"):
            if "evento" not in o["PERSISTIDO"]:
                achados.append(f"{nome}: transicao com persistencia propria")

    for velho, a in m["ALIASES"].items():
        alvo = a["CANONICO"]
        if alvo in SENTINELAS or alvo in obj:
            continue
        if all(p.strip() in obj for p in alvo.split("+")):
            continue
        achados.append(f"alias {velho} -> {alvo}, que nao e objeto declarado")
        # um alias que aponta para nada devolve o nome ao mundo

    pontas = set(ROTULOS_LIVRES) | set(obj)
    for chave in ("TRANSICOES_PERMITIDAS", "TRANSICOES_PROIBIDAS"):
        for t in m[chave]:
            for lado in ("FROM", "TO"):
                if t[lado] not in pontas:
                    achados.append(f"{chave}: ponta {lado}={t[lado]!r} nao e "
                                   "objeto declarado nem rotulo livre")
            if t["VEREDITO"] not in ("ALLOWED", "FORBIDDEN", "CONDITIONAL"):
                achados.append(f"{chave}: veredito {t['VEREDITO']}")

    # OS NOMES TEM DE SER OS MESMOS QUE A ARBITRAGEM JA FIXOU.
    #
    # Este modelo nasceu com `READY_ITEM` num sitio e `SOURCE_FACT / READY_ITEM`
    # noutro — dois nomes para o mesmo objeto, dentro do ficheiro escrito para
    # eliminar nomes a mais. Quem arbitra nomes e
    # `INTELLIGENCE-CONCEPT-OWNERSHIP-V3.json`; este ficheiro consome-os.
    #
    #     UM MODELO QUE INVENTA UM NOME DEIXA DE MODELAR E PASSA A COMPETIR.
    v3 = RAIZ / "docs" / "intelligence" / "INTELLIGENCE-CONCEPT-OWNERSHIP-V3.json"
    if v3.exists():
        arb = json.loads(v3.read_text(encoding="utf-8"))
        nomes = set(arb["CONCEITOS"])
        apelidos = {a for c in arb["CONCEITOS"].values() for a in c.get("ALIAS", [])}
        for nome in obj:
            if nome in nomes:
                continue
            if nome in apelidos:
                achados.append(f"{nome}: e ALIAS em V3, e aqui esta como objeto "
                               "— o canonico da arbitragem e que manda")
        for nome, o in obj.items():
            if nome in nomes and o["OWNER"] not in ("NAO_APLICAVEL",):
                if arb["CONCEITOS"][nome]["OWNER"] != o["OWNER"]:
                    achados.append(f"{nome}: dono {o['OWNER']} aqui e "
                                   f"{arb['CONCEITOS'][nome]['OWNER']} em V3")
                if arb["CONCEITOS"][nome]["CURRENT_IMPLEMENTATION"] != \
                        o["CURRENT_IMPLEMENTATION"]:
                    achados.append(f"{nome}: implementacao declarada aqui nao e "
                                   "a medida em V3")

    for p in m["PORTOES"]:
        if not p["PROOF_REQUIRED"]:
            achados.append(f"portao {p['GATE']}: sem prova exigida")
        if not p["WHO_MAY_PROMOTE"]:
            achados.append(f"portao {p['GATE']}: sem quem promove")

    for nome, f in m["FERRAMENTAS"].items():
        if not f["NEVER_WRITES"]:
            achados.append(f"ferramenta {nome}: sem NEVER_WRITES")
        escreve = " ".join(f["WRITES"]).upper()
        if escreve and "NADA" not in escreve and "VALIDATION_STATE" not in escreve:
            achados.append(f"ferramenta {nome}: escreve {f['WRITES']} — so "
                           "VALIDATION_STATE pode ser escrito por ferramenta")

    for d, x in m["DOMINIOS_ITALIA"].items():
        if not x["FORBIDDEN_OUTPUT"]:
            achados.append(f"dominio {d}: sem saida proibida declarada")

    return achados


def main() -> int:
    m = carregar()
    maus = incoerencias(m)
    obj = m["OBJETOS"]
    print("=" * 70)
    print("MODELO DE OBJETOS DA INTELLIGENCE")
    print("=" * 70)
    por_especie = {}
    for n, o in obj.items():
        por_especie.setdefault(o["ESPECIE"], []).append(n)
    for esp in ESPECIES_VALIDAS:
        for n in sorted(por_especie.get(esp, [])):
            print(f"  {esp:<20} {n:<32} {obj[n]['OWNER']:<14} "
                  f"{obj[n]['CURRENT_IMPLEMENTATION']}")
    print()
    print(f"  objetos={len(obj)} · aliases={len(m['ALIASES'])} · "
          f"portoes={len(m['PORTOES'])} · permitidas="
          f"{len(m['TRANSICOES_PERMITIDAS'])} · proibidas="
          f"{len(m['TRANSICOES_PROIBIDAS'])} · dominios="
          f"{len(m['DOMINIOS_ITALIA'])} · ferramentas={len(m['FERRAMENTAS'])}")
    print()
    if maus:
        print(f"MODELO_DE_OBJETOS=FAIL · {len(maus)} incoerencia(s)")
        for x in maus[:20]:
            print(f"    · {x}")
        return 1
    print("MODELO_DE_OBJETOS=OK · a declaracao sustenta-se")
    print()
    print("    E UM CONTRATO. NAO E RUNTIME, E NAO PROVA IMPLEMENTACAO.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
