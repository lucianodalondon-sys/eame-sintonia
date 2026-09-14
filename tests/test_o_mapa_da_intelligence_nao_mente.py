#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""O SYSTEM MAP DA INTELLIGENCE, ATACADO — C-INT-SYSTEM-MAP-AUDIT-01.

    python3 -m unittest tests.test_o_mapa_da_intelligence_nao_mente -v

    SYSTEM MAP OBSERVA A MAQUINA. SYSTEM MAP NAO DEFINE A ARQUITETURA.

O que estas provas guardam: que a faixa da Intelligence no mapa nao promete mais
do que o modelo de objetos declara, e que nenhuma etapa, ferramenta, dominio ou
ecra ganha um conceito por aparecer numa caixa.

O que elas NAO provam: que a Intelligence funciona.

    INTELLIGENCE_RUNTIME_IMPLEMENTED = NO.

A medicao que originou esta faixa: antes desta missao, F-INTELIGENCIA tinha DOIS
territorios contra os catorze da Coleta, oito cartoes de codigo do motor V2.1 e
ZERO cartoes da lei que manda neles. A Biblia da Intelligence nao tinha cartao
nenhum. O mapa dizia, sem o escrever, que a V2.1 ERA a Intelligence.
"""
import fnmatch
import json
import subprocess
import sys
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))


def carregar(caminho):
    return json.loads((RAIZ / caminho).read_text(encoding="utf-8"))


D = carregar("system-map/data/architecture.declared.json")
S = carregar("system-map/data/state.generated.json")
M = carregar("docs/intelligence/INTELLIGENCE-OBJECT-MODEL-V1.json")
R = carregar("controle/AUTORIDADES-CANONICAS.json")

TERR = {t["id"]: t for t in D["TERRITORIES"]}
CARTOES = {c["id"]: c for c in D["COMPONENTS"]}
NOS = {n["id"]: n for n in S["NODES"]}
DA_INTELIGENCIA = [c for c in D["COMPONENTS"]
                   if TERR[c["territory"]]["family"] == "F-INTELIGENCIA"]


def dono_do_ficheiro(caminho):
    """Que cartao reivindica este caminho. Usa o mapa GERADO, que ja expandiu
    os padroes — comparar padroes a mao seria uma segunda implementacao."""
    for n in S["NODES"]:
        if caminho in n.get("files", []):
            return n
    return None


def familia(cartao):
    return TERR[cartao["territory"]]["family"] if cartao["territory"] in TERR else None


def reivindica(cartao, caminho):
    """Este cartao DECLARADO reivindica este caminho concreto?

    ⚠️ CONTRA O DECLARADO, E NAO CONTRA O GERADO. Ja esteve ao contrario, e a
    mutacao que re-fundia o Achado com a Oportunidade passava despercebida: a
    prova lia a saida do gerador, que so muda quando alguem regenera. Uma prova
    que mede a saida nao ve a decisao a ser tomada na fonte.

        A DECISAO VIVE NO DECLARADO. E AI QUE SE MEDE.
    """
    for padrao in cartao.get("exclude", []):
        if fnmatch.fnmatch(caminho, padrao):
            return False
    for padrao in cartao["files"]:
        if (padrao == caminho or fnmatch.fnmatch(caminho, padrao)
                or (padrao.endswith("/") and caminho.startswith(padrao))):
            return True
    return False


def objetos_do_cartao(cid):
    """Os objetos do modelo cujo MORA_EM aponta para um ficheiro deste cartao."""
    cartao = CARTOES.get(cid)
    if not cartao:
        return []
    achados = []
    for nome, o in M["OBJETOS"].items():
        for pedaco in o["MORA_EM"].replace(" · ", "|").split("|"):
            if reivindica(cartao, pedaco.split("::")[0].strip()):
                achados.append(nome)
                break
    return achados


def texto_da_faixa():
    return " ".join(json.dumps(c, ensure_ascii=False) for c in DA_INTELIGENCIA) + \
        " " + " ".join(json.dumps(t, ensure_ascii=False)
                       for t in D["TERRITORIES"]
                       if t.get("family") == "F-INTELIGENCIA")


# ══════════════════════════════════════════════════════════════════════════════
class A_AFaixaDaIntelligenceNoMapa(unittest.TestCase):
    """O censo, virado prova: o que a auditoria mediu tem de continuar verdade."""

    def test_A1_a_lei_da_intelligence_tem_cartao(self):
        """O achado central desta missao: ate aqui, nao tinha."""
        biblia = dono_do_ficheiro("BIBLIA-DE-ENGENHARIA-DA-INTELLIGENCE.md")
        self.assertIsNotNone(biblia, "a Biblia da Intelligence sem cartao nenhum")
        self.assertEqual(biblia["family"], "F-INTELIGENCIA")

    def test_A2_a_constituicao_e_um_territorio_proprio(self):
        z = TERR.get("Z-INT-LEI")
        self.assertIsNotNone(z)
        self.assertEqual(z["family"], "F-INTELIGENCIA")

    def test_A3_cada_cartao_da_lei_e_uma_autoridade_REGISTADA(self):
        """A regra que impede a constituicao de virar um caixote.

        Um cartao aqui so existe se houver uma autoridade registada da
        INTELIGENCIA cujo CANONICAL_PATH ele reivindique. Sem isto, qualquer
        documento entrava na lei por parecer importante.
        """
        registadas = {a["CANONICAL_PATH"]: a for a in R["AUTHORITIES"]
                      if a["DOMAIN"] == "INTELIGENCIA"}
        for c in D["COMPONENTS"]:
            if c["territory"] != "Z-INT-LEI":
                continue
            with self.subTest(cartao=c["id"]):
                donas = [registadas[f] for f in c["files"] if f in registadas]
                self.assertEqual(len(donas), 1,
                                 f"{c['id']} nao reivindica exatamente uma "
                                 f"autoridade registada: {c['files']}")

    def test_A4_o_motor_V21_nao_e_a_intelligence_inteira(self):
        """RT26. Enquanto Z-MOTOR era o unico territorio com cartoes, era."""
        zonas = {t["id"] for t in D["TERRITORIES"] if t.get("family") == "F-INTELIGENCIA"}
        com_cartoes = {c["territory"] for c in DA_INTELIGENCIA}
        self.assertIn("Z-INT-LEI", com_cartoes)
        self.assertGreater(len(com_cartoes), 1, zonas)
        self.assertNotEqual(TERR["Z-MOTOR"]["name"], "MOTOR — CADEIA V2.1",
                            "o nome dizia que a V2.1 era a Intelligence")

    def test_A5_nenhum_cartao_carrega_objetos_de_donos_diferentes(self):
        """RT27 · um cartao com dois donos e um cartao que esconde uma fronteira."""
        for c in DA_INTELIGENCIA:
            objs = objetos_do_cartao(c["id"])
            donos = {M["OBJETOS"][o]["OWNER"] for o in objs}
            with self.subTest(cartao=c["id"], objetos=objs):
                self.assertLessEqual(len(donos), 1,
                                     f"{c['id']} carrega {objs} com donos {donos}")

    def test_A6_os_cartoes_sobrecarregados_foram_partidos(self):
        """Cada um destes carregava mais de um objeto do modelo."""
        for cid, esperado in (("C-V21-OPORTUNIDADE", ["OPPORTUNITY"]),
                              ("C-V21-CRUZAMENTO", ["CROSSING"]),
                              ("C-INT-ACHADO", ["FINDING / ANALYTIC_JUDGMENT"]),
                              ("C-INT-CONVERGENCIA", ["CONVERGENCE"]),
                              ("C-INT-DOMINIO-ALEGACAO", ["CLAIM_DOMAIN_JUDGMENT"])):
            with self.subTest(cartao=cid):
                self.assertEqual(sorted(objetos_do_cartao(cid)), sorted(esperado))


# ══════════════════════════════════════════════════════════════════════════════
class RT_OsTrintaAtaquesAoMapa(unittest.TestCase):
    """§54 · RT01–RT30 contra a REPRESENTACAO, e nao contra o modelo."""

    # ── o que o mapa nao pode prometer ──────────────────────────────────────
    def test_RT01_DEFINED_ONLY_aparece_como_OBSERVED(self):
        """Um objeto que a arbitragem mede como so-definido nao tem modulo —
        logo nenhum cartao o pode reivindicar, e o mapa nao o pode pintar."""
        for nome, o in M["OBJETOS"].items():
            if o["CURRENT_IMPLEMENTATION"] != "DEFINED_ONLY":
                continue
            if o["MORA_EM"] in ("NAO_EXISTE_AINDA", "NAO_EXISTE_EM_LADO_NENHUM"):
                with self.subTest(objeto=nome):
                    self.assertIsNone(dono_do_ficheiro(o["MORA_EM"]))

    def test_RT02_IMPLEMENTED_aparece_como_fluxo_executado(self):
        """O verde do mapa diz «alguem manda correr isto», nunca «o fluxo da
        Intelligence aconteceu». A razao tem de continuar a dize-lo."""
        for c in DA_INTELIGENCIA:
            n = NOS.get(c["id"])
            if n and n["status"] == "PROVEN":
                with self.subTest(cartao=c["id"]):
                    self.assertTrue(n["status_reason"].strip(),
                                    "verde sem razao escrita")
                    for mentira in ("fluxo observado", "intelligence corre",
                                    "runtime implementado"):
                        self.assertNotIn(mentira, n["status_reason"].lower())

    def test_RT03_e_RT04_transicao_proibida_nao_vira_seta_DECLARADA(self):
        """As setas tecnicas sao MEDIDAS (imports) e o mapa pode desenha-las.
        As DECLARADAS sao promessas — e uma promessa nao pode desenhar o que a
        Biblia proibe."""
        cartao_do_objeto = {}
        for c in DA_INTELIGENCIA:
            for o in objetos_do_cartao(c["id"]):
                cartao_do_objeto[o] = c["id"]
        declaradas = {(e["from"], e["to"])
                      for e in D["EXPECTED_EDGES"] + D["BUSINESS_EDGES"]}
        for t in M["TRANSICOES_PROIBIDAS"]:
            a, b = cartao_do_objeto.get(t["FROM"]), cartao_do_objeto.get(t["TO"])
            if a and b:
                with self.subTest(transicao=f"{t['FROM']}->{t['TO']}"):
                    self.assertNotIn((a, b), declaradas)

    # ── quem e dono de que ──────────────────────────────────────────────────
    def test_RT05_READY_ITEM_aparece_owned_by_Intelligence(self):
        o = M["OBJETOS"]["SOURCE_FACT / READY_ITEM"]
        self.assertEqual(o["OWNER"], "COLLECTION")
        n = dono_do_ficheiro("admissao/sala_de_espera.py")
        self.assertIsNotNone(n)
        self.assertNotEqual(n["family"], "F-INTELIGENCIA")

    def test_RT06_o_GAP_da_Collection_aparece_owned_by_Intelligence(self):
        o = M["OBJETOS"]["GAP / SATISFACTION / DECISION / ROTA"]
        self.assertEqual(o["OWNER"], "COLLECTION")
        n = dono_do_ficheiro("leis/gestao_da_coleta.py")
        self.assertIsNotNone(n)
        self.assertNotEqual(n["family"], "F-INTELIGENCIA")

    def test_RT07_e_RT08_o_requisito_escolhe_collector_ou_rota(self):
        nunca = " ".join(M["OBJETOS"]["INTELLIGENCE_REQUIREMENT"]["NUNCA_E"]).upper()
        for palavra in ("ROTA", "COLETOR", "EXECUTOR", "URL"):
            self.assertIn(palavra, nunca)
        self.assertNotIn("COLETOR", texto_da_faixa().upper().replace("COLETORES", ""))

    def test_RT09_Portal_aparece_como_owner(self):
        """Nenhum cartao de ENTREGA reivindica o modulo de um objeto da
        Intelligence. TOCAR != POSSUIR — e a familia do mapa nao move o dono."""
        for nome, o in M["OBJETOS"].items():
            if o["OWNER"] != "INTELLIGENCE":
                continue
            for pedaco in o["MORA_EM"].replace(" · ", "|").split("|"):
                caminho = pedaco.split("::")[0].strip()
                n = dono_do_ficheiro(caminho)
                if n:
                    with self.subTest(objeto=nome, ficheiro=caminho):
                        self.assertNotEqual(n["family"], "F-ENTREGA")

    def test_RT10_uma_ferramenta_aparece_como_motor(self):
        nomes = " ".join(c["name"].upper() for c in DA_INTELIGENCIA)
        for tool in ("FUTURE RADAR", "VALIDATION QUEUE", "LABEL INTELLIGENCE"):
            self.assertNotIn(tool, nomes)

    def test_RT11_um_dominio_aparece_como_etapa(self):
        """DOMAIN != STAGE. Os oito dominios usam a mesma espinha e nenhum e
        um territorio nem um cartao da faixa."""
        nomes = {c["name"].upper() for c in DA_INTELIGENCIA}
        zonas = {t["name"].upper() for t in D["TERRITORIES"]
                 if t.get("family") == "F-INTELIGENCIA"}
        for d in M["DOMINIOS_ITALIA"]:
            with self.subTest(dominio=d):
                self.assertNotIn(d, nomes)
                self.assertNotIn(d, zonas)

    # ── as especies que nao podem virar caixa ───────────────────────────────
    def test_RT12_SCREENING_aparece_como_entidade(self):
        self.assertEqual(M["OBJETOS"]["SCREENING"]["ESPECIE"], "TRANSITION")
        self.assertNotIn("SCREENING", {c["id"].upper() for c in DA_INTELIGENCIA})

    def test_RT13_VALIDATION_QUEUE_reaparece_como_entidade(self):
        self.assertEqual(M["ALIASES"]["VALIDATION_QUEUE"]["CLASSE"], "DIFFERENT_CONCEPT")
        self.assertNotIn("VALIDATION_QUEUE", texto_da_faixa().upper())

    def test_RT14_ATTENTION_ITEM_reaparece_como_conceito(self):
        self.assertEqual(M["OBJETOS"]["ATTENTION_ITEM"]["ESPECIE"], "NOT_A_CONCEPT")
        self.assertNotIn("ATTENTION_ITEM", texto_da_faixa().upper())

    def test_RT15_FUTURE_SIGNAL_aparece_como_previsao(self):
        o = M["OBJETOS"]["FUTURE_SIGNAL"]
        self.assertEqual(o["ESPECIE"], "PROJECTION")
        self.assertIn("uma previsao certa do futuro", o["NUNCA_E"])
        # O vocabulario de sete valores que o Portal inventou nao entra no mapa.
        for inventado in ("GAINING ATTENTION", "TIMING APPROACHING", "WATCH CLOSELY"):
            self.assertNotIn(inventado, texto_da_faixa().upper())

    def test_RT16_RECOMMENDATION_aparece_como_Finding(self):
        self.assertEqual(M["OBJETOS"]["ANALYTIC_RECOMMENDATION"]["ESPECIE"], "OUTPUT")
        self.assertEqual(M["OBJETOS"]["FINDING / ANALYTIC_JUDGMENT"]["ESPECIE"], "ENTITY")

    def test_RT17_SUPPORT_aparece_como_estacao(self):
        self.assertEqual(M["OBJETOS"]["SUPPORT"]["ESPECIE"], "RELATION")
        self.assertNotIn("SUPPORT", {c["id"].split("-")[-1] for c in DA_INTELIGENCIA})

    def test_RT18_CONTRADICTION_e_um_boolean_perdido(self):
        o = M["OBJETOS"]["CONTRADICTION"]
        self.assertIn("um campo booleano", o["NUNCA_E"])
        self.assertIn("RUN_ID em que foi detetada", o["ENTRADA_MINIMA"])

    def test_RT19_DEPENDENCY_aparece_como_fonte_independente(self):
        self.assertIn("uma contagem de fontes",
                      M["OBJETOS"]["DEPENDENCY / INDEPENDENCE"]["NUNCA_E"])
        self.assertIn("INDEPENDENTES", CARTOES["C-INT-CONVERGENCIA"]["name"].upper())

    def test_RT20_REVERSAL_aparece_como_entidade_nova(self):
        self.assertEqual(M["OBJETOS"]["REVERSAL / DEMOTED_BY"]["ESPECIE"], "TRANSITION")
        self.assertNotIn("REVERSAL", {c["id"].upper() for c in DA_INTELIGENCIA})

    def test_RT21_o_achado_antigo_desaparece_depois_da_reversao(self):
        self.assertIn("apaga o estado anterior", M["REVERSAO"]["NUNCA_FAZ"])

    def test_RT22_e_RT23_RELEVANCE_ou_PRIORITY_nu_reaparece(self):
        for nu in ("RELEVANCE", "PRIORITY"):
            with self.subTest(nome=nu):
                self.assertEqual(M["ALIASES"][nu]["CANONICO"],
                                 "RETIRED_AS_OVERLOADED_NAME")
                for c in DA_INTELIGENCIA:
                    self.assertNotEqual(c["name"].upper().strip(), nu)

    def test_RT24_COLLECTION_GAP_reaparece_como_um_conceito_unico(self):
        self.assertEqual(M["ALIASES"]["COLLECTION_GAP"]["CLASSE"], "DIFFERENT_CONCEPT")
        self.assertIn("INTELLIGENCE_REQUIREMENT", M["OBJETOS"])
        self.assertIn("GAP / SATISFACTION / DECISION / ROTA", M["OBJETOS"])

    def test_RT25_CANDIDATE_FINDING_reaparece(self):
        self.assertEqual(M["ALIASES"]["CANDIDATE_FINDING"]["CANONICO"],
                         "ANALYTIC_HYPOTHESIS")
        self.assertNotIn("CANDIDATE_FINDING", texto_da_faixa().upper())

    def test_RT26_MOTOR_V21_parece_ser_toda_a_Intelligence(self):
        lei = [c for c in DA_INTELIGENCIA if c["territory"] == "Z-INT-LEI"]
        self.assertGreaterEqual(len(lei), 4, "a constituicao tem de estar la")
        self.assertIn("V2.1", TERR["Z-MOTOR"]["why"],
                      "a zona tem de dizer que e a maquina de HOJE, nao a lei")

    # ── o que o proprio validador do mapa ja guarda ─────────────────────────
    # ⚠️ ESTES QUATRO JA FORAM UM SUBPROCESSO, E ISSO ESTAVA ERRADO.
    #
    # A primeira versao corria `validate_system_map.py` inteiro aqui dentro. Ele
    # passava — e fazia esta prova, e as VIZINHAS, oscilar em suite cheia:
    # `test_portao` reprovava numa corrida e passava na seguinte, sem nada mudar.
    # Um teste que lanca um processo pesado que toca o repositorio deixa de ser
    # uma medicao e passa a ser um evento.
    #
    #     UM TESTE QUE CORRE UM PORTAO INTEIRO NAO MEDE: INTERFERE.
    #
    # O portao continua a correr — na cadeia canonica e no CI, que e o sitio
    # dele. Aqui medem-se as PROPRIEDADES, sobre o artefacto ja gerado.

    def test_RT27_dois_donos_para_o_mesmo_ficheiro(self):
        """⚠️ A REGRA E A DO MAPA, E NAO UMA MINHA MAIS DURA.

        A primeira versao percorria TODOS os nos gerados e exigia um dono por
        ficheiro. Reprovou `portale.html` — porque as pecas GERADAS sao lentes
        sobre a mesma arvore, e a mesma pagina aparece legitimamente em varias.
        O mapa ja mede isto onde deve, sobre os componentes DECLARADOS, e
        publica o resultado em `OWNERSHIP_CONFLICTS`.

            INVENTAR UMA REGRA MAIS DURA QUE A LEI NAO E RIGOR: E RUIDO.
        """
        self.assertEqual(S["OWNERSHIP_CONFLICTS"], [])
        # E a parte que E desta missao: dentro da faixa, sem sobreposicao.
        visto = {}
        for c in DA_INTELIGENCIA:
            for f in c["files"]:
                with self.subTest(ficheiro=f):
                    self.assertNotIn(f, visto,
                                     f"{f}: {visto.get(f)} e {c['id']}")
                visto[f] = c["id"]

    def test_RT28_um_ficheiro_que_existe_fabrica_uma_aresta(self):
        """Uma aresta tecnica e MEDIDA: tem de trazer a prova com ela."""
        sem_prova = [f"{e['from']}->{e['to']}" for e in S["EDGES"]
                     if e.get("kind") == "technical" and not e.get("evidence")]
        self.assertEqual(sem_prova, [])

    def test_RT29_uma_aresta_declarada_aparece_observada(self):
        """DECLARED EDGE != OBSERVED EDGE — e as duas costuras com a Coleta
        sao precisamente declaradas, e tem de continuar a ⚪."""
        verdes = [f"{e['from']}->{e['to']}" for e in S["EDGES"]
                  if e.get("kind") == "expected" and e["status"] != "UNKNOWN"]
        self.assertEqual(verdes, [])
        costuras = {(e["from"], e["to"]) for e in S["EDGES"]
                    if e.get("kind") == "expected"}
        self.assertIn(("C-SALA-DE-ESPERA", "C-INT-ESPINHA"), costuras)
        self.assertIn(("C-INT-ESPINHA", "C-GESTAO-DA-COLETA"), costuras)

    def test_RT30_o_gerado_foi_editado_a_mao(self):
        """A deriva quem a mede e a cadeia canonica (`P1_SEM_DRIFT`), que
        regenera e compara. Aqui guarda-se o que ela nao ve: que o gerado
        continua a declarar a arvore de onde veio."""
        prov = S["PROVENANCE"]
        self.assertEqual(len(prov["SOURCE_TREE_FINGERPRINT"]), 64)
        self.assertTrue(prov["HEAD"])
        for c in D["COMPONENTS"]:
            with self.subTest(cartao=c["id"]):
                self.assertNotIn("generated", " ".join(c["files"]).lower())


# ══════════════════════════════════════════════════════════════════════════════
class N_OQueOMapaNaoDeveDesenhar(unittest.TestCase):
    """§46 · 100% REPRESENTADO SEMANTICAMENTE, e nao 25 CAIXAS."""

    def test_N1_nem_todo_objeto_vira_cartao_e_isso_e_deliberado(self):
        com_cartao = set()
        for c in DA_INTELIGENCIA:
            com_cartao.update(objetos_do_cartao(c["id"]))
        self.assertLess(len(com_cartao), len(M["OBJETOS"]),
                        "25 caixas seria o mapa a DEFINIR arquitetura")
        # E os que viram cartao sao exatamente os que tem codigo nesta arvore.
        for o in com_cartao:
            with self.subTest(objeto=o):
                self.assertIn(M["OBJETOS"][o]["CURRENT_IMPLEMENTATION"],
                              ("IMPLEMENTED", "DISPERSO"))

    def test_N2_o_mapa_aponta_para_o_contrato_em_vez_de_o_copiar(self):
        """Dominios e ferramentas vivem no modelo, que E um cartao. Copia-los
        para caixas criava uma segunda arquitetura — e duas divergem."""
        modelo = CARTOES["C-INT-MODELO"]
        self.assertEqual(modelo["files"],
                         ["docs/intelligence/INTELLIGENCE-OBJECT-MODEL-V1.json"])
        self.assertEqual(len(M["DOMINIOS_ITALIA"]), 8)
        self.assertEqual(len(M["FERRAMENTAS"]), 8)

    def test_N3_o_mapa_nao_inventa_runtime(self):
        for nome in ("INTELLIGENCE_RUN", "INTELLIGENCE_REQUEST"):
            with self.subTest(objeto=nome):
                self.assertEqual(M["OBJETOS"][nome]["CURRENT_IMPLEMENTATION"],
                                 "DEFINED_ONLY")
                self.assertEqual(M["OBJETOS"][nome]["MORA_EM"], "NAO_EXISTE_AINDA")


if __name__ == "__main__":
    unittest.main(verbosity=2)
