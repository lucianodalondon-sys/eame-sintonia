#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""AS PROVAS DA RECONCILIACAO DO UNIVERSO DO MAPA.

    python3 system-map/tests/test_reconciliacao_do_universo.py

A reconciliacao existe para que os numeros do mapa se encontrem. Uma
reconciliacao que ninguem confere e uma folha de calculo com ar de lei: basta
alguem mexer numa lente para ela passar a descrever um mundo que ja nao existe,
e continuar a parecer certa.

    TEXTO NAO REPROVA NADA. PROVA REPROVA.

O QUE ESTE FICHEIRO CONFERE
---------------------------
    ARITMETICA   incluidos + excluidos == total visual, e nos dois sentidos
    ANTI-DRIFT   o artefato commitado e o que esta arvore produz hoje
    FILTRO       um territorio novo na coleta nao cai de fora em silencio
    ESPECIE      duas populacoes diferentes nao usam o mesmo nome sem relacao
    FRESCURA     um carimbo que nao se consegue verificar diz isso, nao CURRENT
    MUTACAO      mexer na reconciliacao tem de reprovar alguma coisa

    UMA CONTA QUE FECHA POR ACIDENTE FECHA NA MESMA. As provas de mutacao
    existem para separar «fecha» de «fecha porque esta certa».
"""

import json
import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
SCRIPTS = RAIZ / "system-map" / "scripts"
ARTEFATO = RAIZ / "data" / "derivados" / "SYSTEM-MAP-UNIVERSE-RECONCILIATION-V1.json"

sys.path.insert(0, str(SCRIPTS))
from pente_fino_da_coleta import ZONAS as PENTE_ZONAS      # noqa: E402
from censo_da_topologia import LADO_DA_COLETA              # noqa: E402
import reconciliacao_do_universo as RECONCILIACAO          # noqa: E402

FALHAS = []


def prova(nome, ok, porque=""):
    print(("  PASS  " if ok else "  FAIL  ") + nome + (("\n        " + porque) if not ok and porque else ""))
    if not ok:
        FALHAS.append(nome)


def regerar() -> dict:
    """O que o gerador produz AGORA — medido, nao escrito.

    ⚠️ A PRIMEIRA VERSAO DISTO CORRIA O SCRIPT E DEPOIS REPUNHA O FICHEIRO.
    Funcionava, e criava um SEGUNDO AUTOR do artefato: o validador passou a
    dizer «escrito por C-MAPA-TESTES, C-RECONCILIACAO-UNIVERSO · dono eleito
    por ordem alfabetica».

        UM DONO ELEITO POR ORDEM ALFABETICA NAO E UM DONO.

    A prova nao precisa de escrever para comparar. `medir()` devolve o mesmo
    conteudo sem tocar no disco, e o artefato fica com um dono so. O ida e
    volta por JSON e de proposito: `medir()` devolve tuplos onde o ficheiro
    guarda listas, e comparar as duas formas daria diferenca onde nao ha.
    """
    return json.loads(json.dumps(RECONCILIACAO.medir(com_topologia=True),
                                 ensure_ascii=False))


print("AS PROVAS DA RECONCILIACAO DO UNIVERSO DO MAPA")
print("=" * 70)

prova("o_artefato_existe", ARTEFATO.exists(),
      "corra: py system-map/scripts/reconciliacao_do_universo.py")
if not ARTEFATO.exists():
    raise SystemExit(1)

COMMITADO = json.loads(ARTEFATO.read_text(encoding="utf-8"))
S = json.loads((RAIZ / "system-map" / "data" / "state.generated.json")
               .read_text(encoding="utf-8"))
PENTE = json.loads((RAIZ / "system-map" / "data" / "pente-fino.generated.json")
                   .read_text(encoding="utf-8"))

# ── 1 · ARITMETICA ───────────────────────────────────────────────────────────
# O objectivo NAO e «todas as lentes dao o mesmo numero». E «todos os numeros
# conseguem ser reconciliados»: o que sai de uma lente tem de aparecer na lista
# de excluidos da outra, com motivo, e a soma tem de bater exactamente.
A = COMMITADO["ARITMETICA"]
prova("aritmetica_incluidos_mais_excluidos_da_o_total",
      A["VISUAL_TOTAL"] == A["PENTE_FINE_INCLUDED"] + A["PENTE_FINE_EXCLUDED"],
      f"{A['VISUAL_TOTAL']} != {A['PENTE_FINE_INCLUDED']} + {A['PENTE_FINE_EXCLUDED']}")

cartoes = COMMITADO["CARTOES"]
prova("visual_count_bate_com_os_membros_listados",
      A["VISUAL_TOTAL"] == len(cartoes),
      f"conta {A['VISUAL_TOTAL']}, lista {len(cartoes)}")
prova("pente_count_bate_com_os_membros_listados",
      A["PENTE_FINE_INCLUDED"] == sum(1 for c in cartoes if c["IN_PENTE_FINE"]))
prova("o_pente_fino_bate_consigo_proprio",
      PENTE["RESUMO"]["pecas_da_coleta"] == len(PENTE["PECAS"]))

# UM CARTAO CONTADO DUAS VEZES FECHA A CONTA E MENTE NA MESMA.
ids = [c["CARD_ID"] for c in cartoes]
prova("nenhum_cartao_contado_duas_vezes", len(ids) == len(set(ids)),
      f"repetidos: {sorted({i for i in ids if ids.count(i) > 1})}")

# ── 2 · A CONTA FECHA NOS DOIS SENTIDOS ──────────────────────────────────────
# Um membro do pente fino fora do universo visual seria um cartao auditado que
# a tela nao desenha — e um cartao que ninguem ve e um cartao que ninguem audita.
prova("nenhum_membro_do_pente_fica_fora_da_vista",
      not A["MEMBROS_DO_PENTE_FORA_DA_VISTA"],
      f"{A['MEMBROS_DO_PENTE_FORA_DA_VISTA']}")

# ── 3 · NENHUM EXCLUIDO SEM RAZAO ────────────────────────────────────────────
sem_razao = [c["CARD_ID"] for c in cartoes
             if not c["IN_PENTE_FINE"]
             and not (c.get("WHY_EXCLUDED") or {}).get("EXCLUSION_REASON")]
prova("nenhum_cartao_excluido_sem_razao", not sem_razao, f"{sem_razao}")

sem_dono = [c["CARD_ID"] for c in cartoes
            if not c["IN_PENTE_FINE"]
            and not (c.get("WHY_EXCLUDED") or {}).get("EXCLUSION_OWNER")]
prova("toda_exclusao_tem_dono", not sem_dono, f"{sem_dono}")

sem_intencao = [c["CARD_ID"] for c in cartoes
                if not c["IN_PENTE_FINE"]
                and (c.get("WHY_EXCLUDED") or {}).get("EXCLUSION_INTENTIONAL")
                not in ("YES", "NO", "UNKNOWN")]
prova("toda_exclusao_diz_se_foi_decidida", not sem_intencao, f"{sem_intencao}")

# ── 4 · TODO UNIVERSO PUBLICADO DECLARA-SE ───────────────────────────────────
# Uma contagem sem UNIVERSE_DEFINITION e um numero a flutuar: quem o le
# preenche o universo com o que imagina, e imagina diferente de quem o escreveu.
OBRIGATORIO = ("UNIVERSE_DEFINITION", "OWNER", "COUNT",
               "INCLUSION_RULE", "EXCLUSION_RULE", "MEASURED_HEAD")
for nome, u in COMMITADO["UNIVERSOS"].items():
    faltam = [k for k in OBRIGATORIO if k not in u]
    prova(f"universo_declarado[{nome}]", not faltam, f"faltam: {faltam}")
    if "MEMBERS" in u:
        prova(f"universo_conta_os_membros_que_lista[{nome}]",
              u["COUNT"] == len(u["MEMBERS"]),
              f"COUNT={u['COUNT']} MEMBERS={len(u['MEMBERS'])}")

for lente in COMMITADO["LENTES"]:
    faltam = [k for k in ("LENS_ID", "PARENT_UNIVERSE", "MEMBER_COUNT",
                          "INCLUSION_RULE", "EXCLUSION_RULE", "WHO_COMPUTES",
                          "FROM_WHICH_FILE", "FROM_WHICH_FIELD", "FROM_WHICH_HEAD")
              if k not in lente]
    prova(f"lente_declarada[{lente.get('LENS_ID')}]", not faltam, f"faltam: {faltam}")
    prova(f"lente_aponta_para_universo_real[{lente.get('LENS_ID')}]",
          lente["PARENT_UNIVERSE"] in COMMITADO["UNIVERSOS"],
          f"{lente['PARENT_UNIVERSE']} nao e um universo declarado")

# ── 5 · O CONTADOR DA TELA TEM DONO, E NAO E UM NUMERO ESCRITO A MAO ─────────
fam = {f["id"]: f for f in S["FAMILIES"]}
lente_tela = next(x for x in COMMITADO["LENTES"] if x["LENS_ID"] == "FRONTEND_FAMILY_COUNTER")
prova("o_contador_da_tela_nao_e_hardcoded", lente_tela["HARDCODED"] is False)
prova("o_contador_da_tela_vem_do_estado_gerado",
      sum(fam[f]["count"] for f in LADO_DA_COLETA if f in fam) == A["VISUAL_TOTAL"],
      "FAMILIES[].count nao soma o universo visual")
MAPJS = (RAIZ / "system-map" / "app" / "map.js").read_text(encoding="utf-8")
prova("a_tela_le_o_campo_que_a_reconciliacao_nomeia",
      "${f.count} peças" in MAPJS,
      "map.js deixou de mostrar f.count — a lente aponta para um campo que "
      "ja nao e o que a tela le")

# ── 6 · ANTI-DRIFT: O ARTEFATO COMMITADO E O DESTA ARVORE ───────────────────
# Sem isto, o pente fino podia mudar de populacao e a reconciliacao continuar a
# publicar a populacao anterior — exactamente o defeito que ela veio fechar.
AGORA = regerar()


def sem_carimbo(d):
    """O conteudo, sem as chaves que carregam um SHA de commit.

    A lista NAO esta escrita aqui: vem do proprio artefato
    (`CARIMBOS_NAO_COMPARAVEIS`), para nao existirem duas listas. Uma
    segunda lista divergiria no dia em que alguem acrescentasse um carimbo
    de um lado so — e a prova passaria a ignorar conteudo a serio, ou a
    reprovar por uma diferenca que nao e conteudo nenhum.
    """
    chaves = set(d.get("CARIMBOS_NAO_COMPARAVEIS") or [])

    def limpar(o):
        if isinstance(o, dict):
            return {k: limpar(v) for k, v in o.items() if k not in chaves}
        if isinstance(o, list):
            return [limpar(v) for v in o]
        return o

    d = json.loads(json.dumps(d))
    d.pop("PROVENANCE", None)
    return json.dumps(limpar(d), ensure_ascii=False, sort_keys=True)


prova("o_artefato_declara_os_proprios_carimbos",
      bool(COMMITADO.get("CARIMBOS_NAO_COMPARAVEIS")),
      "sem esta lista, a prova anti-drift nao sabe o que e carimbo e o que e "
      "conteudo — e passaria a reprovar a cada commit, por nada")

prova("a_reconciliacao_commitada_e_a_desta_arvore",
      sem_carimbo(COMMITADO) == sem_carimbo(AGORA),
      "regerar mudou a reconciliacao. Conserto: "
      "py system-map/scripts/reconciliacao_do_universo.py && git add data/derivados")

# A TELA PUBLICA UM NUMERO E A RECONCILIACAO CONHECE OUTRO — o caso que a
# missao pediu para apanhar: frontend diz 62, reconciliacao conhece 61 ou 63.
prova("a_tela_e_a_reconciliacao_conhecem_o_MESMO_numero",
      AGORA["ARITMETICA"]["VISUAL_TOTAL"]
      == sum(fam[f]["count"] for f in LADO_DA_COLETA if f in fam),
      f"tela={sum(fam[f]['count'] for f in LADO_DA_COLETA if f in fam)} "
      f"reconciliacao={AGORA['ARITMETICA']['VISUAL_TOTAL']}")
prova("o_pente_fino_e_a_reconciliacao_conhecem_o_MESMO_numero",
      AGORA["ARITMETICA"]["PENTE_FINE_INCLUDED"] == PENTE["RESUMO"]["pecas_da_coleta"],
      f"pente={PENTE['RESUMO']['pecas_da_coleta']} "
      f"reconciliacao={AGORA['ARITMETICA']['PENTE_FINE_INCLUDED']}")

# ── 7 · O ATAQUE AO FILTRO ESTATICO ──────────────────────────────────────────
# O pente fino filtra por uma TUPLA FIXA de territorios. Um territorio novo na
# coleta entra no mapa e sai da auditoria sem que nada reclame — expandir o
# sistema passa a encolher a medicao. Esta prova nao alarga o filtro: obriga a
# reconciliacao a NOMEAR o territorio desconhecido em vez de o engolir.
territorios_da_coleta = {t["id"] for t in S["TERRITORIES"]
                         if t.get("family") in LADO_DA_COLETA}
desconhecidos = sorted(territorios_da_coleta - set(PENTE_ZONAS))
nomeados = set()
for c in cartoes:
    w = c.get("WHY_EXCLUDED") or {}
    if w:
        nomeados.add(c["TERRITORY"])
prova("todo_territorio_da_coleta_fora_do_pente_esta_nomeado",
      all(t in nomeados for t in desconhecidos),
      f"territorios fora do pente e sem ficha: "
      f"{[t for t in desconhecidos if t not in nomeados]}")

orfaos = [c["CARD_ID"] for c in cartoes
          if not c["IN_PENTE_FINE"]
          and (c.get("WHY_EXCLUDED") or {}).get("EXCLUSION_REASON")
          == "TERRITORIO_FORA_DA_TUPLA_SEM_MOTIVO_ESCRITO"]
prova("nenhum_territorio_novo_caiu_fora_em_silencio", not orfaos,
      f"cartoes em territorio que a tupla ZONAS nao conhece: {orfaos}. "
      f"Ou eles pertencem ao pente fino (e a tupla esta estreita), ou a "
      f"exclusao precisa de uma regra semantica escrita — nao de um silencio.")

# O CASO QUE PARECE ESTE E NAO E: o territorio ESTA na tupla e o cartao nao
# esta no pente fino. Descoberto por ataque — injectar um cartao em `Z-ACOES`
# e o pente fino nao o viu; correr a cadeia outra vez, sem mexer em mais nada,
# e ele apareceu (48 -> 49). A cadeia le `state.generated.json` no passo 5 e
# escreve-o no passo 7.
#
#     DIAGNOSTICAR A DOENCA ERRADA COM CONFIANCA MANDA A PROXIMA PESSOA
#     ALARGAR UM FILTRO QUE NAO TEM DEFEITO NENHUM.
atrasados = [c["CARD_ID"] for c in cartoes
             if not c["IN_PENTE_FINE"]
             and (c.get("WHY_EXCLUDED") or {}).get("EXCLUSION_REASON")
             == "PENTE_FINO_MEDIU_OUTRO_CONJUNTO_DE_NOS"]
prova("o_pente_fino_mediu_o_mesmo_conjunto_de_nos_que_a_tela", not atrasados,
      f"cartoes cujo territorio ESTA na tupla e que o pente fino nao viu: "
      f"{atrasados}. Isto nao e filtro estreito: e ordem da cadeia. Conserto "
      f"imediato: correr REGERAR outra vez. Conserto real: o pente fino nao "
      f"pode ler o estado antes de o gerador o escrever.")

# ── 8 · A MESMA PALAVRA NAO PODE SER DUAS ESPECIES SEM RELACAO ──────────────
especies = {e["NAME"]: e for e in COMMITADO["CARD_SPECIES"]}
prova("as_especies_de_card_estao_todas_declaradas",
      {"ARCHITECTURE_NODE", "SYSTEM_MAP_VISUAL_CARD", "COLLECTION_INTERNAL_PIECE",
       "PORTAL_TOOL_CARD", "VISUAL_ONLY_BLOCK"} <= set(especies),
      f"declaradas: {sorted(especies)}")
for nome, e in especies.items():
    prova(f"especie_tem_dono_e_fonte[{nome}]",
          bool(e.get("OWNER")) and bool(e.get("SOURCE")) and bool(e.get("DEFINITION")))
prova("card_do_portal_nao_se_confunde_com_card_da_coleta",
      especies["PORTAL_TOOL_CARD"]["INTERSECCAO_COM_A_COLETA"] == 0)
prova("a_identidade_do_card_do_portal_esta_provada_e_nao_assumida",
      especies["PORTAL_TOOL_CARD"]["PROVA_DE_IDENTIDADE"] == "NOMES_IGUAIS",
      "os 11 cards do casco deixaram de bater, por nome, com os 11 nos de Z-TELAS")

# ── 9 · FRESCURA: NAO SEI NAO PODE PARECER CURRENT ──────────────────────────
# Um carimbo de SHA de commit nunca pode ser verificado: o ficheiro commitado
# nao nomeia o commit que o contem. Dizer CURRENT a partir dele seria inventar.
for f in COMMITADO["FRESCURA"]["ARTEFATOS"]:
    prova(f"frescura_tem_veredito_conhecido[{f['ARTEFATO']}]",
          f["ESTADO"] in ("CURRENT", "STALE", "UNVERIFIABLE"),
          f"{f['ESTADO']}")
    if f["IMPRESSAO_CARIMBADA"] == "NAO SEI":
        prova(f"carimbo_sem_impressao_nunca_diz_CURRENT[{f['ARTEFATO']}]",
              f["ESTADO"] == "UNVERIFIABLE",
              "artefato sem SOURCE_TREE_FINGERPRINT nao pode ser dado por actual")

# ── 10 · MUTACAO: MEXER NA RECONCILIACAO TEM DE REPROVAR ────────────────────
# SURVIVORS = 0. Cada mutante abaixo e uma maneira conhecida de a reconciliacao
# parecer certa estando errada; se um deles sobreviver, a prova de cima nao
# estava a medir o que dizia medir.
def mutar(nome, transformar, esperado):
    d = json.loads(json.dumps(COMMITADO))
    transformar(d)
    quebrou = []
    a = d["ARITMETICA"]
    cs = d["CARTOES"]
    if a["VISUAL_TOTAL"] != a["PENTE_FINE_INCLUDED"] + a["PENTE_FINE_EXCLUDED"]:
        quebrou.append("soma")
    if a["VISUAL_TOTAL"] != len(cs):
        quebrou.append("membros")
    if a["PENTE_FINE_INCLUDED"] != sum(1 for c in cs if c["IN_PENTE_FINE"]):
        quebrou.append("incluidos")
    i = [c["CARD_ID"] for c in cs]
    if len(i) != len(set(i)):
        quebrou.append("repetido")
    if [c["CARD_ID"] for c in cs
        if not c["IN_PENTE_FINE"] and not (c.get("WHY_EXCLUDED") or {}).get("EXCLUSION_REASON")]:
        quebrou.append("exclusao sem razao")
    if [c for c in cs if c["TERRITORY"] not in
            {t["id"] for t in S["TERRITORIES"]}]:
        quebrou.append("territorio inexistente")
    if [c for c in cs if c["FAMILY"] not in LADO_DA_COLETA]:
        quebrou.append("familia fora do universo")
    for f in d["FRESCURA"]["ARTEFATOS"]:
        if f["IMPRESSAO_CARIMBADA"] == "NAO SEI" and f["ESTADO"] != "UNVERIFIABLE":
            quebrou.append("stale dado por actual")
    prova(f"mutante_morre[{nome}]", bool(quebrou) is esperado,
          f"esperado quebrar={esperado}, quebrou={quebrou}")


def sem_um(d):
    d["CARTOES"].pop()


def duplicar_um(d):
    d["CARTOES"].append(json.loads(json.dumps(d["CARTOES"][0])))
    d["ARITMETICA"]["VISUAL_TOTAL"] += 1
    if d["CARTOES"][0]["IN_PENTE_FINE"]:
        d["ARITMETICA"]["PENTE_FINE_INCLUDED"] += 1
    else:
        d["ARITMETICA"]["PENTE_FINE_EXCLUDED"] += 1


def trocar_familia(d):
    d["CARTOES"][0]["FAMILY"] = "F-INTELIGENCIA"


def trocar_territorio(d):
    d["CARTOES"][0]["TERRITORY"] = "Z-INVENTADA"


def apagar_razao(d):
    for c in d["CARTOES"]:
        if not c["IN_PENTE_FINE"]:
            c["WHY_EXCLUDED"] = {}
            return
    raise AssertionError("nenhum excluido para mutar")


def forjar_stale_como_actual(d):
    for f in d["FRESCURA"]["ARTEFATOS"]:
        if f["IMPRESSAO_CARIMBADA"] == "NAO SEI":
            f["ESTADO"] = "CURRENT"
            return
    raise AssertionError("nenhum carimbo nao verificavel para mutar")


def mudar_o_total_mantendo_membros(d):
    d["ARITMETICA"]["VISUAL_TOTAL"] -= 1


mutar("remover_um_cartao", sem_um, True)
mutar("duplicar_um_cartao", duplicar_um, True)
mutar("trocar_a_familia_de_um_cartao", trocar_familia, True)
mutar("trocar_o_territorio_de_um_cartao", trocar_territorio, True)
mutar("apagar_a_razao_de_uma_exclusao", apagar_razao, True)
mutar("dar_stale_por_actual", forjar_stale_como_actual, True)
mutar("mudar_o_total_mantendo_os_membros", mudar_o_total_mantendo_membros, True)
mutar("nao_mexer_em_nada", lambda d: None, False)

print()
print("=" * 70)
if FALHAS:
    print(f"RECONCILIACAO=FAIL · {len(FALHAS)} prova(s) reprovada(s)")
    for f in FALHAS:
        print("  ·", f)
    raise SystemExit(1)
print("RECONCILIACAO=PASS · os universos do mapa reconciliam-se")
