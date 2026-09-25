"""O instrumento da micro-coleta, provado SEM REDE.

Toda chamada a programa externo (curl, node, psql, orquestrador) passa por
`subprocess.run` do modulo — e aqui ele e trocado por um que rebenta. Um
teste que tentasse ir a rede ou ao banco falhava em vez de ir.

Nao se fixam contagens do livro (e um servico vivo): afirmam-se leis.
"""
import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

RAIZ = Path(__file__).resolve().parents[1]
_spec = importlib.util.spec_from_file_location(
    "micro_coleta", RAIZ / "scripts" / "micro_coleta" / "micro_coleta.py")
MC = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(MC)

AMBIENTE_OK = {"SINTONIA_COLLECTION_DSN": "x", "SINTONIA_SALA_DSN": "x",
               "SINTONIA_SALA_BACKEND": "POSTGRES", "SINTONIA_PSQL_EXE": "x",
               "SINTONIA_ARMAZEM_RAIZ": "x"}


# A coorte vem do PORTAO, no instante (A2). Os dados de fixture cobrem-na toda.
IDS = MC.coorte_do_portao(MC.GATE._contexto())[0]


def ler_fixture(entra=("IT-T10-018", "IT-T7-043"), rotas=None, sem_decisao=(),
                ausente=None):
    """Um `git show` falso: a forma REAL dos ficheiros da M3 e da 3b, sem git.
    `ausente` = caminho que finge nao existir; `sem_decisao` = fontes que o
    JSON da 3b mediu e o relatorio nao decide."""
    rotas = rotas or {}
    dados = {
        "curadoria/ROTAS-ELEGIVEIS-V1.json": json.dumps({"LINHAS": [
            {"SOURCE_ID": s, "VEREDITO": rotas.get(s, "ROUTE_PROVEN")} for s in IDS]}),
        "curadoria/RELEVANCIA-ELEGIVEIS-V1.json": json.dumps({"FONTES": [
            {"SOURCE_ID": s, "AMOSTRAS": [{"DECIDIR": {"RESULTADO": "NAO_SEI"}}]} for s in IDS]}),
        "RELATORIO-RELEVANCIA-ELEGIVEIS.md": "\n".join(
            ["| SOURCE_ID | U | amostras | SIM | classe | coorte | porque |", "|---|---|---|---|---|---|---|"]
            + [f"| {s} nome | T | x | y | z | **{'ENTRA_NA_MICRO' if s in entra else 'FICA_FORA'}** | w |"
               for s in IDS if s not in sem_decisao]),
    }

    def ler(ref, caminho):
        if caminho == ausente or caminho not in dados:
            raise MC.FiltroAusente(f"{ref}:{caminho}: nao existe")
        return dados[caminho], "fixture"
    return ler


def _proibido(*a, **k):
    raise AssertionError(f"programa externo chamado num teste sem rede: {a[:1]}")


class _Lancador:
    def __init__(self):
        self.comandos = []

    def __call__(self, cmd):
        self.comandos.append(cmd)
        sid = next(a.split("=", 1)[1] for a in cmd if a.startswith("fonte="))
        return {"CODIGO": 0, "SAIDA": f"CORRIDA SUCCESS · RUN-FIXTURE-{sid}"}


@mock.patch.object(MC.subprocess, "run", _proibido)
class TestCorrerNaoVaiARedeSemTudoCerto(unittest.TestCase):

    def test_sem_autorizacao_nao_lanca(self):
        l = _Lancador()
        r = MC.correr(lancar=l, egresso=lambda: {"PAIS": "IT"}, ambiente=AMBIENTE_OK)
        self.assertFalse(r["CORREU"])
        self.assertEqual(l.comandos, [])

    def test_sem_as_variaveis_da_sala_nao_lanca(self):
        l = _Lancador()
        r = MC.correr(autorizado=True, lancar=l, egresso=lambda: {"PAIS": "IT"}, ambiente={})
        self.assertFalse(r["CORREU"])
        # 5 desde a BC4 (24/09/2026): SINTONIA_ARMAZEM_RAIZ — sem ela os bytes da Sala
        # real caiam em <arvore>/XX/ (residuo que a suite apaga)
        self.assertEqual(len(r["FALTA"]), 5)
        self.assertIn("SINTONIA_ARMAZEM_RAIZ", r["FALTA"])
        self.assertEqual(l.comandos, [])

    def test_sala_em_ficheiro_ou_banco_descartavel_recusa(self):
        for extra in ({"SINTONIA_SALA_BACKEND": "FICHEIRO"}, {"BANCO_DESCARTAVEL_URL": "x"}):
            l = _Lancador()
            r = MC.correr(autorizado=True, lancar=l, egresso=lambda: {"PAIS": "IT"},
                          ambiente={**AMBIENTE_OK, **extra})
            self.assertFalse(r["CORREU"], extra)
            self.assertEqual(l.comandos, [])

    def test_egresso_brasil_nao_lanca_nenhuma(self):
        l = _Lancador()
        r = MC.correr(autorizado=True, lancar=l, egresso=lambda: {"PAIS": "BR"},
                      ambiente=AMBIENTE_OK, consulta=_proibido, ler=ler_fixture())
        self.assertEqual(l.comandos, [])
        for c in r["CORRIDAS"]:
            self.assertFalse(c["CORREU"])

    def test_egresso_it_lanca_so_as_prontas_e_pela_porta_canonica(self):
        l = _Lancador()
        p = MC.plano(ler=ler_fixture())
        prontas = {x["SOURCE_ID"] for x in p["LINHAS"] if x["ESTADO"] == "PRONTA"}
        r = MC.correr(autorizado=True, lancar=l, egresso=lambda: {"PAIS": "IT"},
                      ambiente=AMBIENTE_OK, consulta=lambda q: [], ler=ler_fixture())
        lancadas = {next(a.split("=", 1)[1] for a in c if a.startswith("fonte="))
                    for c in l.comandos}
        self.assertEqual(lancadas, prontas)
        for c in l.comandos:
            self.assertEqual(c[1], "orquestrador/orquestrador.py")
            self.assertIn("--filtro", c)
            self.assertTrue(any(a.startswith("universo=") for a in c))
        for c in r["CORRIDAS"]:
            if c["CORREU"]:
                self.assertEqual(c["GATE_NO_INSTANTE"], "ELIGIBLE")
                self.assertEqual(c["EGRESSO_ANTES"]["PAIS"], "IT")
                self.assertEqual(c["EGRESSO_DEPOIS"]["PAIS"], "IT")


@mock.patch.object(MC.subprocess, "run", _proibido)
class TestPlano(unittest.TestCase):

    def test_a_coorte_e_o_portao_no_instante_nao_uma_lista(self):
        ctx = MC.GATE._contexto()
        p = MC.plano(ctx=ctx, ler=ler_fixture())
        self.assertEqual(p["COORTE"], "PORTAO (collection_gate.elegiveis)")
        self.assertEqual([l["SOURCE_ID"] for l in p["LINHAS"]], MC.GATE.elegiveis(ctx=ctx))

    def test_cada_ready_fora_do_portao_tem_motivo(self):
        p = MC.plano(ler=ler_fixture())
        dentro = {l["SOURCE_ID"] for l in p["LINHAS"]}
        for x in p["FORA_DO_PORTAO"]:
            self.assertNotIn(x["SOURCE_ID"], dentro)
            self.assertTrue(x["MOTIVO"] and x["PORQUE"], x)

    def test_o_portao_manda_mesmo_contra_a_lista_antiga(self):
        """Uma fonte que o portao recusa nao entra, nem que esteja no ficheiro antigo."""
        ctx = MC.GATE._contexto()
        antigas = {f["SOURCE_ID"] for f in MC.ler_coorte()["PROPOSTAS"]}
        eleg = set(MC.GATE.elegiveis(ctx=ctx))
        p = MC.plano(ctx=ctx, ler=ler_fixture())
        self.assertEqual({l["SOURCE_ID"] for l in p["LINHAS"]} & (antigas - eleg), set())

    def test_pronta_tem_gate_contrato_receita_e_frase(self):
        for l in MC.plano(ler=ler_fixture())["LINHAS"]:
            if l["ESTADO"] == "PRONTA":
                self.assertEqual(l["GATE"], "ELIGIBLE", l["SOURCE_ID"])
                self.assertTrue(l["CONTRATO"] and l["RECEITA_WEB"] and l["FRASE_RESOLVE"])
            else:
                self.assertTrue(l["FALTA"], l["SOURCE_ID"])


    def test_filtro_de_rota_m3_so_bloqueia(self):
        base = {x["SOURCE_ID"]: x["ESTADO"] for x in MC.plano(ler=ler_fixture())["LINHAS"]}
        prontas = [s for s, e in base.items() if e == "PRONTA"]
        self.assertGreaterEqual(len(prontas), 2)
        depois = {x["SOURCE_ID"]: x["ESTADO"] for x in MC.plano(ler=ler_fixture(
            rotas={prontas[0]: "CAPABILITY_BLOCK"}))["LINHAS"]}
        self.assertEqual(depois[prontas[0]], "BLOQUEADA")
        self.assertEqual(depois[prontas[1]], "PRONTA")
        for s, e in base.items():          # nunca promove
            if e == "BLOQUEADA":
                self.assertEqual(depois[s], "BLOQUEADA")

    def test_fica_fora_da_3b_nao_barra_a_fonte(self):
        """D2 + D8 do dono: relevancia decide-se por item na Admission (REROUTE), nao por fonte.
        IT-T10-022 (Zootecnica) e a 3b diz FICA_FORA: continua PRONTA, e a 3b fica ao lado."""
        # ERA `ids=["IT-T10-022"]` escrito a mao. A coorte deste ficheiro vem do
        # PORTAO VIVO (A2, `IDS` acima), e a IT-T10-022 saiu dela na
        # reconciliacao do cutover (345f0e46: READY -> CANARY_PENDING). A
        # pergunta fica a mesma: uma fonte PRONTA da coorte de hoje, com a 3b a
        # dizer FICA_FORA (`entra=()`), continua PRONTA.
        pronta = next(x["SOURCE_ID"] for x in MC.plano(ler=ler_fixture())["LINHAS"]
                      if x["ESTADO"] == "PRONTA")
        p = MC.plano(ids=[pronta], ler=ler_fixture(entra=()))
        self.assertEqual(p["LINHAS"][0]["ESTADO"], "PRONTA", p["LINHAS"][0]["FALTA"])
        self.assertEqual(p["LINHAS"][0]["RELEVANCIA_3b"], "FICA_FORA")

    def test_fonte_que_a_3b_nao_mediu_nao_e_barrada_por_isso(self):
        p = MC.plano(ids=["IT-T10-018", "IT-FORA-999"], ler=ler_fixture())
        self.assertNotIn("RELEVANCIA_NAO_MEDIDA_PELA_3b", p["LINHAS"][1]["FALTA"])
        self.assertEqual(p["LINHAS"][1]["RELEVANCIA_3b"], "NAO_MEDIDA")


@mock.patch.object(MC.subprocess, "run", _proibido)
class TestFiltroAusenteFalhaAlto(unittest.TestCase):
    """FILTRO DECLARADO E AUSENTE = FALHA ALTA. Nunca «sem opiniao»."""

    def test_ficheiro_da_3b_ausente_rebenta_o_plano(self):
        for c in ("curadoria/RELEVANCIA-ELEGIVEIS-V1.json", "RELATORIO-RELEVANCIA-ELEGIVEIS.md",
                  "curadoria/ROTAS-ELEGIVEIS-V1.json"):
            with self.assertRaises(MC.FiltroAusente, msg=c):
                MC.plano(ler=ler_fixture(ausente=c))

    def test_correr_nao_lanca_nada_sem_filtro(self):
        l = _Lancador()
        with self.assertRaises(MC.FiltroAusente):
            MC.correr(autorizado=True, lancar=l, egresso=lambda: {"PAIS": "IT"},
                      ambiente=AMBIENTE_OK, consulta=_proibido,
                      ler=ler_fixture(ausente="curadoria/RELEVANCIA-ELEGIVEIS-V1.json"))
        self.assertEqual(l.comandos, [])

    def test_relatorio_e_dados_da_3b_desencontrados_rebentam(self):
        with self.assertRaises(MC.FiltroAusente):
            # ERA `("IT-T7-043",)`, que saiu da coorte viva (345f0e46): uma
            # fonte fora da coorte nao desencontra nada. Usa-se uma de dentro.
            MC.plano(ler=ler_fixture(sem_decisao=(IDS[0],)))

    def test_forma_inesperada_rebenta(self):
        def ler(ref, c):
            return json.dumps({"LINHAS": []}), "x"
        with self.assertRaises(MC.FiltroAusente):
            MC.plano(ler=ler)

    def test_main_sai_com_3(self):
        with mock.patch.object(MC, "git_show", ler_fixture(ausente="RELATORIO-RELEVANCIA-ELEGIVEIS.md")):
            with mock.patch.object(MC, "plano", lambda: MC.filtros_externos(MC.git_show)):
                self.assertEqual(MC.main(["plano"]), 3)


class TestFiltroRealPorGit(unittest.TestCase):
    """Le as branches reais por `git show` (so git local, sem rede).
    A mutacao pedida: RENOMEAR o ficheiro tem de reprovar."""

    def setUp(self):
        r = MC.subprocess.run(["git", "rev-parse", "--verify", "-q", MC.FILTROS[1]["REF"]],
                              cwd=MC.RAIZ, capture_output=True)
        if r.returncode != 0:
            self.skipTest("branch da 3b nao existe neste clone — correr `git fetch`")

    def test_le_o_ficheiro_real_da_3b(self):
        r = MC.ler_relevancia()
        self.assertIn(MC.ENTRA_3B, r["POR_FONTE"].values())
        self.assertEqual(set(r["POR_FONTE"]), set(r["AMOSTRAS"]))

    def test_renomear_o_ficheiro_reprova(self):
        f = dict(MC.FILTROS[1], DADOS="curadoria/RELEVANCIA-POR-FONTE-V1.json")
        with mock.patch.object(MC, "FILTROS", [MC.FILTROS[0], f, MC.FILTROS[2]]):
            with self.assertRaises(MC.FiltroAusente):
                MC.ler_relevancia()


@mock.patch.object(MC.subprocess, "run", _proibido)
class TestBancoSoLeitura(unittest.TestCase):

    def test_escrita_recusada_antes_do_psql(self):
        for q in ("delete from sala_de_espera", "update raw_asset set id=1",
                  "insert into x values (1)", "select 1; drop table raw_asset",
                  "with x as (select 1) delete from raw_asset; select 1"):
            with self.assertRaises(MC.EscritaRecusada, msg=q):
                MC.sql(q)


class TestRelatorioComFixture(unittest.TestCase):

    def setUp(self):
        self.t = Path(tempfile.mkdtemp())
        (self.t / "XX").mkdir()
        (self.t / "XX" / "materia.html").write_bytes(
            b"<html><body><p>" + b"Il prezzo delle pere e salito. " * 60 + b"</p></body></html>")
        (self.t / "XX" / "capa.html").write_bytes(
            b"<html><body>" + b"".join(b'<a href="/n%d">n</a>' % i for i in range(200))
            + b"</body></html>")
        (self.t / "XX" / "en.txt").write_text("the price of the pears and of the apples is up for the market " * 5, encoding="utf-8")
        (self.t / "XX" / "it.txt").write_text("il prezzo delle pere e di che per con gli nel " * 5, encoding="utf-8")
        self.duplicados = []
        self.livro = self.t / "livro.json"
        self.livro.write_text(json.dumps({"DECISOES": [
            {"item": "derived:10", "resultado": "SIM", "corrida": "R1"},
            {"item": "derived:11", "resultado": "NAO", "corrida": "R1"}]}), encoding="utf-8")

    def _consulta(self, sala_item="derived:10", cadeia="1"):
        def q(s):
            if "from raw_asset r left join" in s:
                return [["1", "IT-X-1", "text/html", "XX/materia.html", "7", "10", "t", "R1",
                         "https://www.myfruit.it/news/dai-mercati-pomodori-sempre-alle-stelle", "XX/en.txt"],
                        ["2", "IT-X-1", "text/html", "XX/capa.html", "8", "11", "t", "R1", "", "XX/it.txt"]]
            if "count(distinct s.run_id)" in s:
                return self.duplicados
            if "from sala_de_espera" in s:
                return [[sala_item, "1", "IT-X-1", "NAO SEI", "NAO SEI", "t", "R1", cadeia]]
            raise AssertionError(s)
        return q

    def test_tentativa_falhada_nao_e_raw_nem_quebra_a_proveniencia(self):
        """A1: 30 linhas para 1 documento e 29 «falhas de proveniencia» falsas. Nunca mais."""
        (self.t / "XX" / "falha.json").write_text(json.dumps(
            {"HEALTH_STATE": "FAILED", "SHA256": "", "OBSERVATION_RESULT": "TRANSPORT_OR_EMPTY",
             "motivo": "status 404", "SOURCE_URL": "https://x.it/n9"}), encoding="utf-8")
        base = self._consulta()

        def q(s):
            linhas = base(s)
            if "from raw_asset r left join" in s:
                linhas = linhas + [["3", "IT-X-1", "application/json", "XX/falha.json", "9", "",
                                    "t", "R1", "https://x.it/n9", ""]]
            return linhas
        r = MC.relatorio(["R1"], consulta=q, livro=self.livro, armazem=self.t)
        self.assertEqual(r["CONTAGENS"]["RAW_LINHAS"], 3)
        self.assertEqual(r["CONTAGENS"]["RAW_CREATED"], 2)
        self.assertEqual(r["CONTAGENS"]["TENTATIVAS_FALHADAS"], 1)
        self.assertEqual(r["CONTAGENS"]["TENTATIVAS"][0]["MOTIVO"], "status 404")
        c4 = r["CRITERIOS"]["C4_PROVENIENCIA_COMPLETA"]
        self.assertEqual(c4["OBSERVACOES"], 2)
        self.assertEqual(c4["TENTATIVAS_FALHADAS_A_PARTE"], 1)
        self.assertNotIn("SEM_DERIVADO", r["CRITERIOS"]["C7_PROPORCAO_POR_FONTE_E_CLASSE"]["POR_FONTE"]["IT-X-1"])

    def test_contadores_do_coletor_vem_do_runs_ndjson_pelo_run_id(self):
        led = self.t / "led"
        led.mkdir()
        linhas = [
            {"RUN_ID": "R1", "contadores": {"HEALTHY": 0, "FAILED": 1, "DETAIL_NEW": 3,
                                            "DETAIL_REQUESTS": 3, "INDEX_REQUESTS": 1,
                                            "UNNECESSARY_REFETCHES": 0}},
            {"RUN_ID": "OUTRA", "contadores": {"HEALTHY": 9}}]
        (led / "runs.ndjson").write_text("".join(json.dumps(x) + "\n" for x in linhas),
                                         encoding="utf-8")
        r = MC.relatorio(["R1"], consulta=self._consulta(), livro=self.livro, armazem=self.t, ledger=led)
        c = r["CONTAGENS"]["COLETOR"]
        self.assertEqual((c["SOURCES_SUCCESS"], c["SOURCES_FAILED"]), (0, 1))
        self.assertEqual(c["DETAIL_DOCUMENTS"], 3)
        self.assertEqual(c["NETWORK_REQUESTS"], 4)
        self.assertEqual(c["RUNS_SEM_LEDGER"], [])

    def test_item_que_ja_estava_na_sala_por_outra_corrida_e_contado(self):
        self.duplicados = [["derived:10", "1"]]
        r = MC.relatorio(["R1"], consulta=self._consulta(), livro=self.livro, armazem=self.t)
        self.assertEqual(r["CONTAGENS"]["SALA_ITENS_JA_NA_SALA_POR_OUTRA_CORRIDA"], 1)
        self.assertEqual(r["CONTAGENS"]["SALA_DUPLICADOS_EXEMPLOS"], ["derived:10"])

    def test_sem_duplicados_conta_zero(self):
        r = MC.relatorio(["R1"], consulta=self._consulta(), livro=self.livro, armazem=self.t)
        self.assertEqual(r["CONTAGENS"]["SALA_ITENS_JA_NA_SALA_POR_OUTRA_CORRIDA"], 0)

    def test_json_de_verdade_continua_documento(self):
        (self.t / "XX" / "api.json").write_text(json.dumps({"dados": [1, 2]}), encoding="utf-8")
        self.assertIsNone(MC.e_tentativa_falhada(self.t, "XX/api.json", "application/json"))

    def test_mede_os_criterios(self):
        corr = [{"SOURCE_ID": "IT-X-1", "CORREU": True, "GATE_NO_INSTANTE": "ELIGIBLE",
                 "EGRESSO_ANTES": {"PAIS": "IT"}, "EGRESSO_DEPOIS": {"PAIS": "IT"}}]
        r = MC.relatorio(["R1"], corridas=corr, consulta=self._consulta(),
                         livro=self.livro, armazem=self.t, saida=self.t / "out")
        C = r["CRITERIOS"]
        self.assertTrue(C["C1_EGRESSO_IT_POR_CORRIDA"]["PASSA"])
        self.assertEqual(C["C2_MATERIA_NAO_CAPA"]["ESTADO"], "PENDENTE_HUMANO")
        self.assertEqual(C["C2_MATERIA_NAO_CAPA"]["CAPAS_DO_JUIZ"], ["2"])
        self.assertTrue(C["C3_PONTE_EM_RUNTIME"]["PASSA"])
        self.assertTrue(C["C4_PROVENIENCIA_COMPLETA"]["PASSA"])
        self.assertEqual(C["C5_FACT_TIME_LOCATION"]["FACT_TIME_UNKNOWN"], 1)
        self.assertTrue(C["C6_ZERO_BYPASS"]["PASSA"])
        self.assertEqual(C["C7_PROPORCAO_POR_FONTE_E_CLASSE"]["POR_FONTE"],
                         {"IT-X-1": {"SIM": 1, "NAO": 1}})
        self.assertIn("2\tIT-X-1", (self.t / "out" / "CAPAS-A-CONFIRMAR.tsv").read_text(encoding="utf-8"))

    def test_duas_perguntas_e_idioma_contados_a_parte(self):
        livro = self.t / "livro2.json"
        livro.write_text(json.dumps({"DECISOES": [
            {"item": "derived:10", "resultado": "NAO_SEI", "corrida": "R1", "evidencia": {}},
            {"item": "derived:11", "resultado": "NAO", "corrida": "R1"}]}), encoding="utf-8")
        r = MC.relatorio(["R1"], consulta=self._consulta(sala_item="derived:99"),
                         livro=livro, armazem=self.t)
        c8, c9 = r["CRITERIOS"]["C8_DUAS_PERGUNTAS"], r["CRITERIOS"]["C9_IDIOMA_NAO_DA_NAO_SEI"]
        self.assertEqual([x["N"] for x in c8["ITENS_DO_GABARITO"]], [1])   # casado por URL
        self.assertEqual(c8["RELEVANTE_AO_SINTONIA_FORA_DA_SALA"], [1])
        self.assertEqual(c8["SIM_ERRADO"], 0)
        self.assertEqual(c9["IDIOMAS"], {"en": 1, "it": 1})
        self.assertEqual(c9["CONTADOS"], 1)                                # ingles + NAO_SEI sem sinal
        self.assertFalse(c9["PASSA"])

    def test_sim_errado_reprova_c8(self):
        livro = self.t / "livro3.json"
        livro.write_text(json.dumps({"DECISOES": [{"item": "derived:10", "resultado": "SIM", "corrida": "R1"}]}))
        with mock.patch.object(MC, "GABARITO", self.t / "g.json"):
            (self.t / "g.json").write_text(json.dumps({"ITENS": [{"N": 3, "DOCUMENTO":
                "https://www.myfruit.it/news/dai-mercati-pomodori-sempre-alle-stelle", "ESPERADO": "NAO",
                "UNIVERSE_MATCH": "NO", "SINTONIA_RELEVANT": "NO", "ACTION": "NAO_ENTRA"}]}))
            r = MC.relatorio(["R1"], consulta=self._consulta(), livro=livro, armazem=self.t)
        self.assertEqual(r["CRITERIOS"]["C8_DUAS_PERGUNTAS"]["SIM_ERRADO"], 1)
        self.assertFalse(r["CRITERIOS"]["C8_DUAS_PERGUNTAS"]["PASSA"])

    def test_bypass_e_cadeia_partida_reprovam(self):
        r = MC.relatorio(["R1"], consulta=self._consulta(sala_item="derived:11", cadeia="0"),
                         livro=self.livro, armazem=self.t)
        C = r["CRITERIOS"]
        self.assertFalse(C["C6_ZERO_BYPASS"]["PASSA"])      # NAO na Sala
        self.assertFalse(C["C4_PROVENIENCIA_COMPLETA"]["PASSA"])
        self.assertFalse(C["C1_EGRESSO_IT_POR_CORRIDA"]["PASSA"])  # sem medicao = FAIL
        self.assertFalse(C["C3_PONTE_EM_RUNTIME"]["PASSA"])

    def test_bytes_em_falta_reprovam(self):
        (self.t / "XX" / "capa.html").unlink()
        r = MC.relatorio(["R1"], consulta=self._consulta(), livro=self.livro, armazem=self.t)
        self.assertEqual(r["CRITERIOS"]["C2_MATERIA_NAO_CAPA"]["ESTADO"], "FAIL")

    def test_controlo_negativo_do_juiz(self):
        self.assertTrue(MC.controlo_negativo_de_capa()["PASSA"])

    def test_run_id_com_aspas_recusado(self):
        with self.assertRaises(ValueError):
            MC.relatorio(["R1' or '1'='1"], consulta=_proibido, livro=self.livro)


if __name__ == "__main__":
    unittest.main()
