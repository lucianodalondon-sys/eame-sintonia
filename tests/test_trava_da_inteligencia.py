# -*- coding: utf-8 -*-
"""A TRAVA DA INTELIGÊNCIA — a ordem antes da pressa.

    COLLECTION_FOUNDATION_CLOSED != SIM
    →
    INTELLIGENCE_IMPLEMENTATION_BLOCKED

⚠️ O QUE ESTA TRAVA PROVAVA ANTES, E ESTAVA ERRADO
--------------------------------------------------
A primeira versão procurava **pastas com certos nomes** — `inteligencia`,
`opportunity`, `scoring`. Não encontrava nenhuma. E daí eu escrevi, no contrato e
no mapa:

    «zero áreas de inteligência implementadas neste repositório»

**A frase era maior do que a prova.** Não havia *pasta* com esses nomes. Havia
dezenas de artefatos espalhados por outras gavetas: `motor/v21_oportunidades.py`,
`regras/sensor_coleta.py`, e as telas do portal. E `tests/test_radar_futuro.py`
fala de `PROMOTED_TO_RADAR` e `WATCHLIST_PRIORITY` há muito tempo.

*(A contagem exacta não se escreve aqui de propósito: ela vive no contrato, que é
medido. Um número em prosa envelhece sem ninguém dar por isso.)*

Procurar num sítio, não achar, e concluir que não existe em sítio nenhum — é o
mesmo erro de sempre, com outra roupa.

O QUE ESTA VERSÃO PROVA
-----------------------
Não se prova que a inteligência **não existe**. Prova-se que

    A INTELIGÊNCIA QUE JÁ EXISTIA NO MOMENTO DO CONGELAMENTO
    NÃO AVANÇOU.

Duas coisas, e só estas duas:

  1. os artefatos congelados têm o mesmo `GIT_BLOB_SHA` que tinham no
     `FROZEN_AT_HEAD` — **nenhum deles mudou**;
  2. não apareceu artefato **novo** de espécie `IMPLEMENTATION`, `CONTRACT` ou
     `PORTAL_UI`.

E ESPÉCIE NÃO É `grep`
----------------------
Um ficheiro de coleta que menciona «signal» num comentário não é inteligência.
Congelar tudo o que contém a palavra impediria consertar a coleta — e uma trava
que morde o trabalho certo é desligada na primeira semana.
"""
import json
import os
import subprocess
import unittest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONTRATO = os.path.join(RAIZ, "docs", "operacao", "TRAVA-DA-INTELIGENCIA.json")
ESTRADAS = os.path.join(RAIZ, "system-map", "data", "estradas-it.generated.json")
CENSO = os.path.join(RAIZ, "system-map", "data", "congelamento.generated.json")


def _json(caminho):
    with open(caminho, encoding="utf-8") as f:
        return json.load(f)


def _blob_do_git(rel):
    """⚠️ QUEM MEDE É O GIT, NÃO EU.

    Não é `sha256` do ficheiro neste disco: aqui tem CRLF, e o Git guarda LF —
    já publiquei um sha errado por medir do lado errado dessa conversão. E não é
    do último *commit*: o manifesto também é commitado, e a medida andaria atrás
    do próprio rabo.

    `git hash-object` mede a árvore de trabalho **de agora**, passando pelos
    mesmos filtros que o Git aplicaria ao guardar."""
    if not os.path.exists(os.path.join(RAIZ, rel)):
        return None
    r = subprocess.run(["git", "hash-object", "--", rel], cwd=RAIZ,
                       capture_output=True, text=True)
    return r.stdout.strip() if r.returncode == 0 else None


class ATravaExisteEDizOEstado(unittest.TestCase):

    def test_o_contrato_existe_e_declara_a_regra(self):
        c = _json(CONTRATO)
        self.assertIn("INTELLIGENCE_IMPLEMENTATION_BLOCKED", c["REGRA"])
        self.assertIn(c["COLLECTION_FOUNDATION_CLOSED"], ("SIM", "NAO"))

    def test_a_trava_nao_impede_o_que_nao_deve_impedir(self):
        """Uma trava que impedisse consertar um defeito que ameaça dados seria
        pior do que o problema que resolve."""
        c = _json(CONTRATO)
        junto = " ".join(c["O_QUE_A_TRAVA_NAO_IMPEDE"]).lower()
        self.assertIn("ler", junto)
        self.assertIn("defeito", junto)
        self.assertIn("historico", junto)

    def test_o_contrato_nao_diz_mais_que_nao_existe_inteligencia(self):
        """A afirmação antiga era falsa e está corrigida por escrito. Se alguém
        a repuser, este teste reprova."""
        c = _json(CONTRATO)
        e = c["ESTADO_MEDIDO_HOJE"]
        self.assertNotIn("AREAS_DE_INTELIGENCIA_IMPLEMENTADAS", e,
                         "a contagem antiga voltou; ela media pastas, nao "
                         "inteligencia")
        self.assertGreater(e["ARTEFATOS_CONGELADOS"], 0,
                           "congelar zero artefatos e nao congelar nada")
        self.assertIn("PROVA", c["O_QUE_A_TRAVA_PROVA"])


class OManifestoEUmaFotografia(unittest.TestCase):
    """O manifesto é DECLARADO, à mão, no contrato — não gerado.

    Se ele fosse gerado, correr o censo num HEAD novo reescreveria em silêncio a
    linha de base que ele existe para guardar. **O guarda não pode mover a
    própria marca.**"""

    def setUp(self):
        self.c = _json(CONTRATO)
        self.m = self.c["FREEZE_MANIFEST"]

    def test_o_manifesto_diz_em_que_ponto_congelou(self):
        cabeca = self.m["FROZEN_AT_HEAD"]
        self.assertEqual(len(cabeca), 40, "FROZEN_AT_HEAD tem de ser um commit")
        self.assertTrue(all(ch in "0123456789abcdef" for ch in cabeca))

    def test_cada_artefato_congelado_tem_caminho_especie_e_sha(self):
        for a in self.m["FROZEN_INTELLIGENCE_ARTIFACTS"]:
            self.assertIn(a["SPECIES"], self.m["ESPECIES_CONGELADAS"])
            self.assertEqual(len(a["GIT_BLOB_SHA"]), 40, a["PATH"])

    def test_nenhum_caminho_repetido(self):
        caminhos = [a["PATH"] for a in self.m["FROZEN_INTELLIGENCE_ARTIFACTS"]]
        self.assertEqual(len(caminhos), len(set(caminhos)))


class AInteligenciaCongeladaNaoAvancou(unittest.TestCase):
    """O coração da trava. Os dois testes que a fazem morder."""

    def setUp(self):
        self.c = _json(CONTRATO)
        self.m = self.c["FREEZE_MANIFEST"]
        if self.c["COLLECTION_FOUNDATION_CLOSED"] == "SIM":
            self.skipTest("a fundacao fechou; a trava deixa de morder")

    def test_nenhum_artefato_congelado_mudou(self):
        """⚠️ ESTE É O TESTE. Um ficheiro congelado que muda de sha avançou.

        Sumiu também conta: apagar não é congelar."""
        mudaram, sumiram = [], []
        for a in self.m["FROZEN_INTELLIGENCE_ARTIFACTS"]:
            agora = _blob_do_git(a["PATH"])
            if agora is None:
                sumiram.append(a["PATH"])
            elif agora != a["GIT_BLOB_SHA"]:
                mudaram.append("%s\n    congelado=%s\n    agora     =%s"
                               % (a["PATH"], a["GIT_BLOB_SHA"][:16],
                                  agora[:16]))
        self.assertEqual(
            mudaram, [],
            "INTELIGENCIA CONGELADA AVANCOU antes de a coleta fechar:\n  %s"
            % "\n  ".join(mudaram))
        self.assertEqual(
            sumiram, [],
            "artefato congelado desapareceu — apagar nao e congelar:\n  %s"
            % "\n  ".join(sumiram))

    def test_nao_apareceu_inteligencia_nova(self):
        """A outra maneira de violar a trava: não mexer em nada do que existe, e
        escrever um ficheiro novo ao lado."""
        if not os.path.exists(CENSO):
            self.skipTest("censo do congelamento ainda nao foi corrido")
        censo = _json(CENSO)
        antes = {a["PATH"] for a in self.m["FROZEN_INTELLIGENCE_ARTIFACTS"]}
        agora = {a["PATH"] for a in censo["FROZEN_INTELLIGENCE_ARTIFACTS"]}
        novos = sorted(agora - antes)
        self.assertEqual(
            novos, [],
            "INTELIGENCIA NOVA antes de COLLECTION_FOUNDATION_CLOSED:\n  %s"
            % "\n  ".join(novos))

    def test_o_manifesto_e_o_censo_falam_da_mesma_fotografia(self):
        """`FROZEN_AT_HEAD` é a MARCA HISTÓRICA — o ponto em que a fotografia
        foi tirada. Não é o ponto onde se mede: mede-se sempre a árvore de
        trabalho de agora. Mas as duas medições têm de descrever a mesma
        fotografia, senão comparam coisas diferentes."""
        if not os.path.exists(CENSO):
            self.skipTest("censo do congelamento ainda nao foi corrido")
        censo = _json(CENSO)
        self.assertEqual(censo["O_QUE_A_TRAVA_SEGURA"],
                         self.m["ESPECIES_CONGELADAS"],
                         "censo e manifesto congelam especies diferentes")


class ODestraveExigeTudoENaoUmaCoisaSo(unittest.TestCase):
    """⚠️ AQUI ESTAVA A BRECHA MAIOR.

    A versão antiga aceitava `SIM` desde que `ESTRADAS.FECHADAS > 0`. Uma
    estrada fechada de sete destrancaria as sete."""

    def test_a_condicao_de_destrave_exige_os_catorze_criterios(self):
        c = _json(CONTRATO)
        junto = " ".join(c["CONDICAO_DE_DESTRAVE"]["TODAS_ESTAS_AO_MESMO_TEMPO"])
        self.assertIn("A..N", junto)
        self.assertIn("UNKNOWN", junto)
        self.assertIn("BLOCKED", junto)

    def test_fechadas_maior_que_zero_nao_basta(self):
        """Se um dia alguém puser SIM, tem de haver isto tudo por trás.

        ⚠️ Nenhuma destas condições é decorativa. Cada uma bloqueia uma maneira
        diferente de dizer «fechado» sem estar."""
        c = _json(CONTRATO)
        if c["COLLECTION_FOUNDATION_CLOSED"] != "SIM":
            self.assertEqual(c["COLLECTION_FOUNDATION_CLOSED"], "NAO")
            return

        # 1 · nenhum critério pendente
        self.assertEqual(c["QUAIS_FALTAM"], [],
                         "diz FECHADO com criterios pendentes")
        self.assertEqual(c["QUANTOS_CRITERIOS_JA_CUMPRIDOS"],
                         len(c["CRITERIOS_PARA_FECHAR"]))

        e = _json(ESTRADAS)

        # 2 · saber quantas estradas o sistema precisa
        self.assertNotEqual(
            e["ROUTE_CLASSES_REQUIRED_TOTAL"], "UNKNOWN",
            "diz FECHADO sem saber quantas estradas sao precisas")

        # 3 · nenhuma fonte sem caminho provado.
        # ⚠️ CANDIDATE NÃO CONTA. Uma pista no catálogo é uma frase, não uma
        # cadeia percorrida — e são justamente as pistas que fariam a fundação
        # parecer fechada sem ninguém ter ido lá.
        f = e["FONTES_IT"]
        self.assertEqual(
            f["SOURCES_ROUTE_UNKNOWN"], 0,
            "diz FECHADO com fontes de rota desconhecida")
        self.assertEqual(
            f["SOURCES_WITH_ONLY_CANDIDATE_ROUTE"], 0,
            "diz FECHADO com fontes que so tem pista, e pista nao e rota")
        self.assertEqual(
            f["SOURCES_WITH_PROVEN_ROUTE"] + f["SOURCES_BLOCKED"], f["TOTAL"],
            "ha fontes que nao estao nem provadas nem bloqueadas com razao")

        # 4 · toda estrada necessária com arquitetura fechada.
        # BLOCKED e DEBT nao saem da conta sozinhos: precisam de razao escrita.
        for r in e["ROUTE_CLASSES"]:
            rid = r["ROUTE_CLASS_ID"]
            if r.get("ARCHITECTURE_CLOSED"):
                continue
            razao = r.get("BLOCKED_REASON") or r.get("DEBT_REASON")
            self.assertTrue(
                razao,
                "diz FECHADO com a estrada %s aberta e sem razao escrita" % rid)

    def test_bloquear_nao_e_atalho_para_fechar(self):
        c = _json(CONTRATO)
        self.assertIn("decisao", c["CONDICAO_DE_DESTRAVE"]["BLOCKED_NAO_E_ATALHO"])

    def test_a_lei_e_o_contrato_nao_podem_discordar(self):
        """⚠️ DOIS SÍTIOS A DECLARAR O MESMO FACTO É DERIVA À ESPERA.

        `leis/fundacao_da_coleta.py` declara `COLLECTION_FOUNDATION_CLOSED` em
        Python; este contrato declara-o em JSON. Se um disser `SIM` e o outro
        `NAO`, alguém destrancou metade da casa.

        Eles não são a mesma coisa e é bom que não sejam: a lei diz que **áreas**
        estão proibidas — é política, por nome. O manifesto congela os
        **artefatos** que existem — é medição, por `sha`. A política diz o que
        não se pode começar; a medição prova que o que já existia não andou.
        Mas sobre *se a fundação fechou*, só pode haver uma resposta."""
        import sys
        sys.path.insert(0, RAIZ)
        import _gavetas  # noqa: F401
        import fundacao_da_coleta as lei
        c = _json(CONTRATO)
        na_lei = "SIM" if lei.COLLECTION_FOUNDATION_CLOSED else "NAO"
        self.assertEqual(
            c["COLLECTION_FOUNDATION_CLOSED"], na_lei,
            "o contrato diz %s e leis/fundacao_da_coleta.py diz %s"
            % (c["COLLECTION_FOUNDATION_CLOSED"], na_lei))

    def test_as_areas_da_lei_estao_cobertas_pelas_marcas_do_censo(self):
        """A lei nomeia 6 áreas proibidas. O censo procura marcas no código. Se
        uma área da lei não tiver marca que a denuncie, ela está proibida no
        papel e invisível na medição."""
        import sys
        sys.path.insert(0, RAIZ)
        import _gavetas  # noqa: F401
        import fundacao_da_coleta as lei
        sys.path.insert(0, os.path.join(RAIZ, "system-map", "scripts"))
        import censo_do_congelamento as censo
        def raiz(p):
            return p.upper().rstrip("S").split("_")[0]
        marcas = [raiz(m) for m in censo.TODAS]
        sem_marca = [a for a in lei.AREAS_CONGELADAS
                     if not any(raiz(a) == m or raiz(a) in m or m in raiz(a)
                                for m in marcas)]
        self.assertEqual(
            sem_marca, [],
            "areas proibidas pela lei que o censo nao procura: %s" % sem_marca)


class OsCriteriosSaoContados(unittest.TestCase):

    def test_os_criterios_somam(self):
        """Cumpridos mais pendentes têm de dar o total. Um critério que
        desaparece da conta é um critério que ninguém vai fechar."""
        c = _json(CONTRATO)
        total = len(c["CRITERIOS_PARA_FECHAR"])
        self.assertEqual(len(c["QUAIS_JA_CUMPRIDOS"]) + len(c["QUAIS_FALTAM"]),
                         total)
        self.assertEqual(c["QUANTOS_CRITERIOS_JA_CUMPRIDOS"],
                         len(c["QUAIS_JA_CUMPRIDOS"]))

    def test_nenhum_criterio_e_dado_por_cumprido_sem_estar_na_lista(self):
        c = _json(CONTRATO)
        chaves = set(c["CRITERIOS_PARA_FECHAR"])
        self.assertTrue(set(c["QUAIS_JA_CUMPRIDOS"]) <= chaves)
        self.assertTrue(set(c["QUAIS_FALTAM"]) <= chaves)
        self.assertEqual(set(c["QUAIS_JA_CUMPRIDOS"]) & set(c["QUAIS_FALTAM"]),
                         set())


if __name__ == "__main__":
    unittest.main(verbosity=2)
