#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ATAQUES AO PORTAO DE ADMISSAO DA COLLECTION.

O portao tem uma frase:

    COLLECTION_ELIGIBLE = READY_CURRENT AND NOT HUMAN_REVIEW_REQUIRED
                          AND NOT bloqueada

Estes testes tentam fazer a frase mentir por oito caminhos diferentes, e
tentam tambem fazer o PROPRIO PORTAO deixar de ser um portao — trocando a
regra por uma lista de IDs autorizados, ou abrindo um caminho paralelo que
arranca coleta sem passar por aqui.

    UM PORTAO QUE NUNCA RECUSA NAO E UM PORTAO.
    UM PORTAO COM UMA PORTA DAS TRASEIRAS TAMBEM NAO.

Os testes que mexem em estado usam livro e fila descartaveis (molde:
test_ready_split.py:44-48). Os que leem o livro REAL so leem — e afirmam
PROPRIEDADES derivadas da regra, nunca identidades escritas a mao: um teste
que lista os IDs esperados e a mesma lista fixa que esta missao veio proibir.
"""
from __future__ import annotations

import ast
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "curadoria"))

import collection_gate as CG      # noqa: E402
import fila as F                  # noqa: E402
import interface_collection as IC  # noqa: E402
import lifecycle as LC            # noqa: E402
import ready_split as RS          # noqa: E402

VELHA = "IT-T9-901"      # promovida pela regua antiga
NOVA = "IT-T9-902"       # promovida com os quatro passos
SECCAO = "IT-T9-903"     # quatro passos, mas o item aberto parece uma seccao

INDEX = "https://ex.it/news/"
ITEM = "https://ex.it/news/mosca-olivo-calo-termico-2026/"
ITEM_SECCAO = "https://ex.it/news/lavora-con-noi"


def _prova_completa(ref: str, url: str = ITEM) -> dict:
    """A evidencia de uma promocao pela regua de hoje: os quatro passos."""
    return {"EVIDENCE_REF": ref, "DADOS": {
        "PASS": True, "DETAIL_ENUMERATED": 9, "DETAIL_GATE_PASSED": True,
        "ITEM_ABERTO": {"URL": url, "HTTP": 200, "HTML_KIND": "CONTENT",
                        "CAPA_OU_MATERIA": RS.MATERIA,
                        "PARAGRAPH_CHARACTERS": 1800}}}


def _prova_antiga(ref: str) -> dict:
    """A regua antiga: «a rota resolveu e trouxe HTML». Sem item, sem corpo."""
    return {"EVIDENCE_REF": ref, "DADOS": {"PASS": True, "ALVO": INDEX}}


class NoLivroDescartavel(unittest.TestCase):
    """Livro, fila, evidencia e contratos numa pasta que morre no fim."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        d = Path(self.tmp.name)
        self._antes = (LC.LIVRO, F.FILA, RS.EVIDENCIA, RS.CONTRATOS, IC.CONTRATOS,
                       IC.CARACT)
        LC.LIVRO = d / "LEDGER.json"
        F.FILA = d / "QUEUE.json"
        RS.EVIDENCIA = d / "EVIDENCE.json"
        RS.CONTRATOS = IC.CONTRATOS = d / "contracts.json"
        IC.CARACT = d / "nao-existe.json"
        self.provas = [_prova_antiga("EV-VELHA"), _prova_completa("EV-NOVA"),
                       _prova_completa("EV-SECCAO", ITEM_SECCAO)]
        RS.EVIDENCIA.write_text(json.dumps({"PROVAS": self.provas}), encoding="utf-8")
        RS.CONTRATOS.write_text(json.dumps({"FONTES": [
            {"SOURCE_ID": s, "TERRITORY": "T9",
             "SOURCE_CONTRACT_HASH": "hash-" + s[-3:],
             "ACQUISITION": {"INDEX_URL": INDEX, "STRATEGY": "HTTP",
                             "ROUTE_TYPE": "LISTAGEM"}}
            for s in (VELHA, NOVA, SECCAO)]}), encoding="utf-8")
        self._promover(VELHA, "EV-VELHA")
        self._promover(NOVA, "EV-NOVA")
        self._promover(SECCAO, "EV-SECCAO")

    def tearDown(self):
        (LC.LIVRO, F.FILA, RS.EVIDENCIA, RS.CONTRATOS, IC.CONTRATOS,
         IC.CARACT) = self._antes
        self.tmp.cleanup()

    def _promover(self, sid: str, ref: str):
        LC.registar(sid, LC.CANARY_PENDING, "prova")
        LC.registar(sid, LC.READY_FOR_COLLECTION, "canario", evidence_ref=ref)

    def _bloquear(self, sid: str, estado: str):
        LC.registar(sid, estado, "bloqueio de teste")


class OsOitoAtaques(NoLivroDescartavel):
    """A tabela G-RT da missao, ataque a ataque."""

    def test_1_READY_LEGACY_nao_entra(self):
        v = CG.avaliar(VELHA)
        self.assertEqual(LC.READY_FOR_COLLECTION, v["STATE"],
                         "a fonte nem sequer esta READY — o ataque nao chegou a acontecer")
        self.assertEqual(RS.REGUA_LEGACY, v["READY_RULE"])
        self.assertFalse(v["COLLECTION_ELIGIBLE"])
        self.assertEqual(CG.READY_LEGACY, v["MOTIVO"])
        self.assertNotIn(VELHA, [r["SOURCE_ID"] for r in IC.ready_sources()])

    def test_2_POLICY_BLOCK_nao_entra(self):
        self._bloquear(NOVA, LC.POLICY_BLOCK)
        v = CG.avaliar(NOVA)
        self.assertFalse(v["COLLECTION_ELIGIBLE"])
        self.assertEqual(CG.ESTADO_NAO_READY, v["MOTIVO"])
        self.assertIn(LC.POLICY_BLOCK, v["PORQUE"])

    def test_3_CAPABILITY_BLOCK_nao_entra(self):
        self._bloquear(NOVA, LC.CAPABILITY_BLOCK)
        self.assertFalse(CG.eligible_for_collection(NOVA))
        self.assertEqual([], IC.ready_sources() and
                         [r for r in IC.ready_sources() if r["SOURCE_ID"] == NOVA])

    def test_4_UNKNOWN_nao_entra(self):
        self._bloquear(NOVA, LC.UNKNOWN)
        self.assertFalse(CG.eligible_for_collection(NOVA))

    def test_4b_DEGRADED_e_RETRY_nao_entram(self):
        for estado in (LC.DEGRADED, LC.RETRY_AFTER):
            with self.subTest(estado=estado):
                self._bloquear(NOVA, estado)
                self.assertFalse(CG.eligible_for_collection(NOVA))
        # e uma fonte que nunca foi promovida tambem nao entra
        LC.registar("IT-T9-904", LC.CANARY_PENDING, "nunca chegou a READY")
        self.assertFalse(CG.eligible_for_collection("IT-T9-904"))

    def test_5_fonte_com_revisao_humana_nao_entra(self):
        v = CG.avaliar(SECCAO)
        self.assertEqual(RS.REGUA_CURRENT, v["READY_RULE"],
                         "esta fonte tem os quatro passos — o ataque so vale assim")
        self.assertTrue(v["HUMAN_REVIEW_REQUIRED"])
        self.assertFalse(v["COLLECTION_ELIGIBLE"])
        self.assertEqual(CG.HUMAN_REVIEW_REQUIRED, v["MOTIVO"])
        self.assertNotIn(SECCAO, [r["SOURCE_ID"] for r in IC.ready_sources()])

    def test_6_uma_promocao_sem_corpo_util_nao_vira_READY_CURRENT(self):
        """CONTROLO NEGATIVO DA REGUA.

        Se alguem «arranjar» o reconciliador ou a regua para devolver
        READY_CURRENT a toda a gente, este teste cai: a VELHA tem evidencia
        sem item e sem corpo, e nao pode ser CURRENT de maneira nenhuma.
        Tambem cai o inverso — uma regua que nunca diz CURRENT deixa NOVA de
        fora e o portao passa a recusar tudo, que e outra forma de mentir.
        """
        self.assertEqual(RS.REGUA_LEGACY, CG.avaliar(VELHA)["READY_RULE"])
        self.assertEqual(RS.REGUA_CURRENT, CG.avaliar(NOVA)["READY_RULE"])
        elegiveis = CG.elegiveis()
        self.assertEqual([NOVA], elegiveis,
                         "o portao deixou de distinguir as duas reguas")

    def test_7_o_portao_recusa_e_diz_sempre_porque(self):
        inv = CG.inventario()
        self.assertEqual(3, len(inv))
        recusadas = [l for l in inv if not l["COLLECTION_ELIGIBLE"]]
        self.assertEqual(2, len(recusadas))
        for l in recusadas:
            self.assertTrue(l["MOTIVO"] and l["PORQUE"],
                            "recusa sem motivo escrito e igual a nao medir: %s" % l)

    def test_8_o_painel_nao_chama_READY_LEGACY_de_pronta(self):
        m = IC.metricas_operacionais()
        self.assertEqual(3, m["READY"])
        self.assertEqual(1, m["READY_LEGACY"])
        self.assertEqual(2, m["READY_CURRENT"])
        self.assertEqual(1, m["HUMAN_REVIEW_REQUIRED"])
        self.assertEqual(1, m["COLLECTION_ELIGIBLE"])
        self.assertLess(m["COLLECTION_ELIGIBLE"], m["READY"],
                        "READY e COLLECTION_ELIGIBLE colaram-se num numero so")

    def test_9_o_lote_entregue_a_Collection_nao_leva_legacy(self):
        entregues = {r["SOURCE_ID"] for r in IC.ready_sources()}
        self.assertEqual({NOVA}, entregues)
        self.assertTrue(all(r["READY_RULE"] == RS.REGUA_CURRENT
                            for r in IC.ready_sources()))


class NenhumaListaDecideAAdmissao(unittest.TestCase):
    """G-RT ataque 8: alguem troca a regra por `ALLOWED_IDS = [...]`.

    Uma lista fixa parece o portao — e no dia seguinte e um carimbo velho.
    Este teste le o TEXTO dos ficheiros que decidem a admissao e reprova se
    encontrar um SOURCE_ID literal onde devia estar uma regra.
    """

    DECIDEM_A_ADMISSAO = ["curadoria/collection_gate.py",
                          "curadoria/interface_collection.py"]
    UM_SOURCE_ID = re.compile(r"^IT-T\d+-\d+$")
    NOME_DE_LISTA_AUTORIZADA = re.compile(
        r"^(ALLOWED_IDS|FONTES_AUTORIZADAS|WHITELIST|IDS_PERMITIDOS)$")

    @staticmethod
    def _defeitos(texto: str) -> list[str]:
        """Le o CODIGO, nao o texto. Comentario e docstring podem — e devem —
        citar `ALLOWED_IDS = [...]` para explicar o defeito que se proibiu; uma
        regex crua sobre o ficheiro confundia a explicacao com a reincidencia.
        A arvore sintactica separa os dois."""
        arvore = ast.parse(texto)
        docstrings = set()
        for no in ast.walk(arvore):
            if isinstance(no, (ast.Module, ast.ClassDef, ast.FunctionDef,
                               ast.AsyncFunctionDef)):
                corpo = getattr(no, "body", None)
                if (corpo and isinstance(corpo[0], ast.Expr)
                        and isinstance(corpo[0].value, ast.Constant)
                        and isinstance(corpo[0].value.value, str)):
                    docstrings.add(id(corpo[0].value))
        achados = []
        for no in ast.walk(arvore):
            if (isinstance(no, ast.Constant) and isinstance(no.value, str)
                    and id(no) not in docstrings
                    and NenhumaListaDecideAAdmissao.UM_SOURCE_ID.match(no.value)):
                achados.append("SOURCE_ID literal no codigo: %s" % no.value)
            if isinstance(no, ast.Name) and \
                    NenhumaListaDecideAAdmissao.NOME_DE_LISTA_AUTORIZADA.match(no.id):
                achados.append("lista de autorizados: %s" % no.id)
        return achados

    def test_nenhuma_lista_nem_SOURCE_ID_decide_a_admissao(self):
        achados = []
        for rel in self.DECIDEM_A_ADMISSAO:
            for d in self._defeitos((RAIZ / rel).read_text(encoding="utf-8")):
                achados.append("%s: %s" % (rel, d))
        self.assertEqual([], achados, (
            "as fontes elegiveis tem de RESULTAR da regra, nunca de uma lista "
            "escrita a mao: %s" % achados))

    def test_a_propria_regra_apanha_o_defeito(self):
        """CONTROLO POSITIVO: sem isto, uma regra que nunca acusa da verde."""
        falso = ("\"\"\"Aqui explica-se que ALLOWED_IDS = ['IT-T7-017'] e "
                 "proibido.\"\"\"\nALLOWED_IDS = ['IT-T7-017', 'IT-T7-033']\n")
        d = self._defeitos(falso)
        self.assertTrue(any("lista de autorizados" in x for x in d), d)
        self.assertTrue(any("SOURCE_ID literal" in x for x in d), d)

    def test_a_regra_nao_acusa_a_explicacao(self):
        """CONTROLO NEGATIVO: um ficheiro que so EXPLICA o defeito passa."""
        so_explica = ("\"\"\"PROIBIDO ALLOWED_IDS = ['IT-T7-017'].\"\"\"\n"
                      "def f(sid):\n    return sid\n")
        self.assertEqual([], self._defeitos(so_explica))


class NenhumCaminhoParaleloArrancaColeta(unittest.TestCase):
    """G-RT ataque 7: bypass direto da Collection.

    Quem arranca o coletor italiano tem de perguntar ao portao. Os outros
    caminhos ficam DECLARADOS, com o que sao — e um ficheiro NOVO que comece a
    chamar o coletor sem estar declarado reprova aqui, antes de chegar a
    producao.
    """

    COLETORES = ("italy_pilot_collect.mjs", "italy_recurrent_collect.mjs")
    GASTAS = (".py", ".mjs", ".js", ".cmd", ".yml", ".yaml")
    ONDE = ("coleta", "curadoria", "pedido", "orquestrador", "regras",
            "candidatas", "ferramentas", "scripts", "provas", "tests",
            ".github", "motor", "controle", "portoes", "guarda")

    # (caminho relativo) -> (classificacao, exige portao?)
    DECLARADOS = {
        "coleta/italy_recurrent_collect.mjs": ("PRODUCTION_PATH", True),
        "coleta/italy_executor.py": ("PRODUCTION_PATH", True),
        "pedido/receitas.py": ("PRODUCTION_PATH_DECLARA", False),
        "coleta/italy_pilot_collect.mjs": ("MANUAL_TOOL", False),
        "ferramentas/italy-forward-only-live.cmd": ("PRODUCTION_LAUNCHER", False),
        ".github/workflows/sintonia-scrap.yml": ("TEST_ONLY", False),
        "curadoria/test_collection_gate.py": ("TEST_ONLY", False),
        # A2 (micro-pronta-v2): ensaio OFFLINE da micro-coleta. Corre o coletor com
        # TODA a rede desviada para 127.0.0.1 (bytes ja guardados), um Postgres
        # descartavel e uma worktree temporaria — a Sala real nao e tocada.
        # Ferramenta corrida a mao; nao arranca coleta de producao.
        "scripts/micro_coleta/ensaio_offline.py": ("MANUAL_TOOL", False),
        # SOC2: importa `alvosDe` para provar a guarda COLETADO_POR; nao colhe.
        "curadoria/test_soc2_curator_youtube.py": ("TEST_ONLY", False),
    }
    PREFIXOS_DECLARADOS = {
        "regras/": "TEST_ONLY",      # guardas e motor de rota, nao correm coleta
        "provas/": "MANUAL_TOOL",    # provas corridas a mao
        "tests/": "TEST_ONLY",
    }

    def _quem_menciona(self) -> list[str]:
        achados = []
        for pasta in self.ONDE:
            base = RAIZ / pasta
            if not base.exists():
                continue
            for p in base.rglob("*"):
                if p.suffix.lower() not in self.GASTAS or not p.is_file():
                    continue
                try:
                    t = p.read_text(encoding="utf-8", errors="replace")
                except OSError:
                    continue
                if any(c in t for c in self.COLETORES):
                    achados.append(p.relative_to(RAIZ).as_posix())
        return sorted(achados)

    def test_todo_caminho_ate_ao_coletor_esta_declarado(self):
        nao_declarados = [
            c for c in self._quem_menciona()
            if c not in self.DECLARADOS
            and not any(c.startswith(p) for p in self.PREFIXOS_DECLARADOS)]
        self.assertEqual([], nao_declarados, (
            "caminho novo ate ao coletor italiano, sem classificacao. "
            "Classifica-o (PRODUCTION_PATH / MANUAL_TOOL / TEST_ONLY) e, se "
            "for producao, faz-lo perguntar a curadoria/collection_gate.py: %s"
            % nao_declarados))

    def test_os_caminhos_de_producao_perguntam_ao_portao(self):
        sem_portao = []
        for rel, (classe, exige) in self.DECLARADOS.items():
            if not exige:
                continue
            t = (RAIZ / rel).read_text(encoding="utf-8", errors="replace")
            if "collection_gate" not in t:
                sem_portao.append("%s (%s)" % (rel, classe))
        self.assertEqual([], sem_portao, (
            "caminho de producao que arranca coleta sem consultar o portao "
            "de admissao: %s" % sem_portao))

    def test_o_perfil_agendado_nao_nomeia_fonte_nenhuma(self):
        """⚠️ ESTE TESTE MUDOU DE LEI EM 2026-09-22 (cutover, Fase 5).

        A lei velha era «o perfil pode nomear o que quiser; quem decide e o
        portao», e procurava `BLOCKED_BY_CURATOR_INTAKE_GATE` no coletor.
        Enquanto o perfil tinha lista, esse era o estado esperado — as tres
        fontes escritas a mao eram uma SEMANTIC_REVIEW e duas READY_LEGACY, e
        o portao dizia nao as tres.

        A lei nova e mais dura: O PERFIL NAO NOMEIA NADA. A populacao sai do
        portao, e por isso `BLOCKED_BY_CURATOR_INTAKE_GATE` deixou de poder
        acontecer por esta via — nao ha lista para o portao recusar.

            ENQUANTO O PERFIL NOMEAVA FONTES, O MELHOR QUE O PORTAO PODIA
            FAZER ERA DIZER NAO. AGORA ELE DIZ QUEM.
        """
        perfil = (RAIZ / "candidatas" / "italy_profiles.mjs").read_text(
            encoding="utf-8", errors="replace")
        # so o CODIGO: o comentario cita a lista removida para explicar o
        # defeito, e explicacao nao e reincidencia.
        codigo = "\n".join(l for l in perfil.split("\n")
                           if not l.strip().startswith("//"))
        self.assertNotIn("SOURCES", codigo,
                         "a lista fixa de fontes voltou ao perfil")
        self.assertEqual([], re.findall(r"IT-T\d+-\d+", codigo),
                         "um SOURCE_ID voltou ao perfil")
        self.assertIn('POPULACAO: "COLLECTION_GATE"', codigo,
                      "o perfil tem de declarar de onde vem a populacao")

        t = (RAIZ / "coleta" / "italy_recurrent_collect.mjs").read_text(
            encoding="utf-8", errors="replace")
        tc = "\n".join(l for l in t.split("\n")
                       if not l.strip().startswith("//"))
        self.assertIn('"curadoria/collection_gate.py", "--json"', tc)
        self.assertNotIn("--ids=", tc,
                         "o coletor voltou a mandar ids ao portao — assim o "
                         "portao filtra a lista de outra pessoa, nao decide "
                         "a populacao")
        # o portao vem ANTES de cunhar o RUN_ID e de chamar o coletor
        self.assertLess(tc.index("collection_gate.py"), tc.index("executarRodada"),
                        "o portao foi consultado DEPOIS de a coleta comecar")

    def test_o_coletor_agendado_para_mesmo_no_portao(self):
        """⚠️ PROVA DE RUNTIME, E NAO DE TEXTO. FOI PRECISA.

        A versao anterior deste ataque so lia o ficheiro. Uma mutacao que
        trocava `admissao.RECUSADAS.map(...)` por `[]` deixava as duas frases
        procuradas intactas — o mutante SOBREVIVEU e a suite ficou verde com o
        portao desligado. Ler o texto nao prova que o portao morde.

        Corre-se o coletor agendado a serio, com `--so-o-portao` (que para no
        passo 6b, com ou sem veredito favoravel) e `--simulate-vpn IT` (que
        nao vai a rede). ITALY_OPS_ROOT vai para uma pasta descartavel: o lock
        e o log nascem e morrem la.
        """
        if not shutil.which("node"):
            self.skipTest("node nao esta nesta maquina — a prova de runtime "
                          "do coletor agendado nao corre aqui")
        with tempfile.TemporaryDirectory() as d:
            r = subprocess.run(
                ["node", "coleta/italy_recurrent_collect.mjs",
                 "--profile", "forward-only-live", "--so-o-portao",
                 "--simulate-vpn", "IT", "--no-git"],
                cwd=str(RAIZ), capture_output=True, text=True,
                encoding="utf-8", errors="replace", timeout=600,
                env={**os.environ, "ITALY_OPS_ROOT": d})
        self.assertIn("{", r.stdout, "o coletor nao devolveu resumo: %s" % r.stderr[-400:])
        resumo = json.loads(r.stdout[r.stdout.index("{"):])

        # ⚠️ O VALOR ESPERADO NAO SAI DESTE JSON. Comparar `COLLECTION_ELIGIBLE`
        # com `len(COLLECTION_ELIGIBLE_IDS)` do MESMO resumo era comparar a
        # lista consigo propria. O portao e perguntado OUTRA VEZ, por OUTRO
        # caminho — em processo, pela API Python (`CG.elegiveis()`), enquanto o
        # coletor o correu por subprocesso e leu JSON.
        #
        #     DOIS CAMINHOS INDEPENDENTES QUE DAO O MESMO NUMERO
        #     SAO UMA PROVA. UM CAMINHO SO E UM ECO.
        esperados = CG.elegiveis()

        self.assertEqual("COLLECTION_GATE", resumo["COLLECTION_SOURCE_SELECTION"],
                         "a selecao deixou de sair do portao")
        self.assertEqual("GATE_ONLY_NO_COLLECTION", resumo["RUN_STATE"],
                         "o coletor agendado nao parou no portao: %s"
                         % resumo.get("reason"))
        self.assertEqual(0, resumo["SOURCE_ATTEMPTED"],
                         "alguma fonte foi tocada antes do portao dizer sim")
        self.assertEqual(len(esperados), resumo["COLLECTION_ELIGIBLE"],
                         "o coletor viu uma populacao diferente da que o "
                         "portao da: %s vs %s"
                         % (resumo["COLLECTION_ELIGIBLE"], len(esperados)))
        # O PORTAO TEM DE MORDER. Um portao que admite tudo nao e um portao —
        # e este e o ataque que a mutacao `RECUSADAS -> []` faz.
        self.assertTrue(resumo["COLLECTION_REFUSED_TOTAL"],
                        "o portao nao recusou ninguem — nao mordeu")
        self.assertTrue(resumo["COLLECTION_REFUSED_BY_MOTIVE"],
                        "as recusas nao vieram com motivo; uma soma nao diz "
                        "de que lei o nao veio")
        # ELEGIVEL NAO E ALCANCAVEL, e a diferenca fica DITA, nao calada.
        self.assertEqual(
            resumo["ELIGIBLE_WITH_CONTRACT"] + len(resumo["ELIGIBLE_WITHOUT_CONTRACT"]),
            resumo["COLLECTION_ELIGIBLE"],
            "a conta nao fecha: elegivel = com contrato + sem contrato")
        self.assertEqual("HEALTHY", resumo["RUNNER_HEALTH"],
                         "o portao decidir nao e o corredor estar doente")

    def test_o_adapter_do_pedido_recusa_a_fonte_por_omissao_da_receita(self):
        """PROVA DE RUNTIME do segundo caminho de producao, SEM REDE ALCANCAVEL.

        `pedido/receitas.py` nomeia a fonte, e a receita de T3 tem
        `filtros_por_omissao`. A fonte que la esta e medida contra o livro
        AGORA: se nao for admitida, `correr_coletor()` devolve
        BLOQUEADA_PELO_CURATOR e o lancador nem chega a ser chamado.

        ⚠️ PORQUE O LANCADOR E INJECTADO. A primeira versao deste teste chamava
        `correr_coletor()` a serio. Com o portao inteiro isso nunca ia a rede —
        mas as mutacoes do red team desligam o portao de proposito, e nessas
        corridas o teste colheu TRES VEZES o boletim da APOL, com o RUN_ID
        «RUN-TESTE-SEM-REDE» e egresso no Brasil. O espiao abaixo torna isso
        impossivel: se o portao falhar, o teste reprova — nao colhe.
        """
        sys.path.insert(0, str(RAIZ / "coleta"))
        import italy_executor as adapter   # noqa: PLC0415

        receitas = (RAIZ / "pedido" / "receitas.py").read_text(encoding="utf-8")
        m = re.search(r'filtros_por_omissao["\']?\s*:\s*\{\s*["\']fonte["\']\s*:\s*["\'](IT-T\d+-\d+)["\']',
                      receitas)
        self.assertIsNotNone(m, "a receita deixou de ter fonte por omissao — "
                                "este ataque precisa de saber qual e")
        sid = m.group(1)
        veredito = CG.avaliar(sid)
        chamadas = []

        def espiao(comando):
            chamadas.append(comando)
            return {"CODIGO": 0, "ERRO": "", "ESPIAO": True}

        r = adapter.correr_coletor("RUN-DE-TESTE-NUNCA-CORRE", sid,
                                   raiz=str(RAIZ), lancar=espiao)
        if veredito["COLLECTION_ELIGIBLE"]:
            self.assertNotIn("BLOQUEADA_PELO_CURATOR", r)
            self.assertEqual(1, len(chamadas),
                             "admitida e o lancador nao foi chamado")
        else:
            self.assertIn("BLOQUEADA_PELO_CURATOR", r,
                          "o adapter correu o coletor com uma fonte que o "
                          "Curator nao admite: %s" % veredito["PORQUE"])
            self.assertFalse(r["CORREU"])
            self.assertEqual(veredito["MOTIVO"],
                             r["BLOQUEADA_PELO_CURATOR"]["MOTIVO"])
            self.assertEqual([], chamadas,
                             "o coletor foi lancado apesar da recusa")


class OLivroRealPassaPelaMesmaRegra(unittest.TestCase):
    """F5/F6 — o livro canonico, so lido, medido pela regra e nunca por lista.

    Nao ha aqui um unico SOURCE_ID escrito a mao, de proposito: o que se afirma
    e a PROPRIEDADE de quem passa e de quem nao passa.
    """

    @classmethod
    def setUpClass(cls):
        cls.ctx = CG._contexto()
        cls.inv = CG.inventario(ctx=cls.ctx)
        cls.painel = CG.painel(ctx=cls.ctx)

    def test_toda_elegivel_e_READY_CURRENT_sem_revisao_humana(self):
        for l in self.inv:
            if not l["COLLECTION_ELIGIBLE"]:
                continue
            with self.subTest(sid=l["SOURCE_ID"]):
                self.assertEqual(LC.READY_FOR_COLLECTION, l["STATE"])
                self.assertEqual(RS.REGUA_CURRENT, l["READY_RULE"])
                self.assertIsNone(l["HUMAN_REVIEW_REQUIRED"])

    def test_toda_READY_CURRENT_com_revisao_humana_fica_de_fora(self):
        com_revisao = [l for l in self.inv
                       if l["READY_RULE"] == RS.REGUA_CURRENT
                       and l["HUMAN_REVIEW_REQUIRED"]]
        for l in com_revisao:
            with self.subTest(sid=l["SOURCE_ID"]):
                self.assertFalse(l["COLLECTION_ELIGIBLE"])
                self.assertEqual(CG.HUMAN_REVIEW_REQUIRED, l["MOTIVO"])

    def test_nenhuma_READY_LEGACY_do_livro_real_entra(self):
        vazou = [l["SOURCE_ID"] for l in self.inv
                 if l["READY_RULE"] != RS.REGUA_CURRENT and l["COLLECTION_ELIGIBLE"]]
        self.assertEqual([], vazou)

    def test_os_contadores_fecham_entre_si(self):
        p = self.painel
        self.assertEqual(p["READY_TOTAL"],
                         p["READY_CURRENT_TOTAL"] + p["READY_LEGACY_TOTAL"],
                         "ha READY que nao e LEGACY nem CURRENT e ninguem o disse")
        self.assertLessEqual(p["COLLECTION_ELIGIBLE"], p["READY_CURRENT_TOTAL"])
        self.assertGreater(p["READY_TOTAL"], p["COLLECTION_ELIGIBLE"],
                           "o livro real tem READY a mais para isto ser possivel; "
                           "se passou, o portao deixou de filtrar")

    def test_cada_elegivel_traz_contrato_rota_e_prova_de_detalhe(self):
        """F5, uma a uma — pela regra, nunca por lista."""
        entregues = IC.ready_sources()
        self.assertEqual(self.painel["COLLECTION_ELIGIBLE"], len(entregues))
        contratos = RS._contratos()
        for r in entregues:
            with self.subTest(sid=r["SOURCE_ID"]):
                self.assertTrue(r["COLLECTION_ELIGIBLE"])
                self.assertEqual(RS.REGUA_CURRENT, r["READY_RULE"])
                self.assertIsNone(r["HUMAN_REVIEW_REQUIRED"])
                self.assertNotEqual("NAO SEI", r["CONTRACT_VERSION"])
                self.assertNotEqual("NAO SEI", r["EVIDENCE_REF"])
                # ⚠️ MEDIDO E DECLARADO, NAO CORRIGIDO AQUI: `ROUTE_VERSION`
                # sai «NAO SEI» para TODAS as fontes deste livro. A chave que
                # a interface le e `ACQUISITION.ROUTE_TYPE`, e os contratos
                # desta arvore nao a tem — trazem STRATEGY, MATCH, INDEX_URL,
                # LINK_PATTERN, MAX_TARGETS. Nao e defeito do portao e nao se
                # arranja escondendo: a rota prova-se pelo INDEX_URL, que tem
                # de existir, e o «NAO SEI» fica a vista no relatorio.
                self.assertTrue(
                    (contratos.get(r["SOURCE_ID"]) or {}).get("ACQUISITION", {}).get("INDEX_URL"),
                    "elegivel sem endereco de listagem no contrato")
                passos = RS.passos_da_promocao(
                    RS.ultima_promocao(r["SOURCE_ID"], self.ctx["livro"]),
                    self.ctx["evidencias"].get(r["EVIDENCE_REF"]),
                    contratos.get(r["SOURCE_ID"]))
                self.assertTrue(all(passos["PASSOS"].values()),
                                "elegivel sem os quatro passos: %s" % passos)


if __name__ == "__main__":
    unittest.main(verbosity=2)
