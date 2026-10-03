# -*- coding: utf-8 -*-
"""RED TEAM DA MATRIZ DE DEMANDA DE DADOS — ITÁLIA.

    MISSAO  C-INT-DATA-DEMAND-IT-01

Vinte ataques. Cada um tenta fazer o estudo dizer uma coisa que a matéria-prima
não sustenta. Um ataque que passa é um defeito no estudo, não no ataque.

    python3 -m unittest tests.test_a_demanda_de_dados_da_italia -v
"""
from __future__ import annotations

import csv
import io
import json
import sys
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
if str(RAIZ / "provas") not in sys.path:
    sys.path.insert(0, str(RAIZ / "provas"))

import demanda_de_dados_da_italia as D  # noqa: E402

PESQUISA = RAIZ / "research" / "intelligence"
MATRIZ_JSON = PESQUISA / "DATA-DEMAND-MATRIX-ITALY.json"
MATRIZ_MD = PESQUISA / "DATA-DEMAND-MATRIX-ITALY.md"
FLUXO_MD = PESQUISA / "INTELLIGENCE-DATA-FLOW-ITALY.md"
GAPS_CSV = PESQUISA / "COLLECTION-GAPS-FOR-INTELLIGENCE-ITALY.csv"


def matriz() -> dict:
    return json.loads(MATRIZ_JSON.read_text(encoding="utf-8"))


def medida() -> dict:
    return D.medir()


class OEstudoExiste(unittest.TestCase):
    def test_os_quatro_artefactos_estao_no_sitio(self):
        for p in (MATRIZ_JSON, MATRIZ_MD, FLUXO_MD, GAPS_CSV):
            self.assertTrue(p.exists(), f"{p} nao existe")

    def test_o_medidor_nao_escreve_nada(self):
        """LER NAO E ESCREVER. Um medidor que escreve deixa de poder ser corrido
        contra producao."""
        fonte = (RAIZ / "provas" / "demanda_de_dados_da_italia.py").read_text(encoding="utf-8")
        for proibido in ("write_text(", "open(", ".mkdir(", "os.replace", "shutil"):
            self.assertNotIn(proibido, fonte,
                             f"o medidor contem «{proibido}» — ele nao pode escrever")


class RT01_VolumeSemChave(unittest.TestCase):
    def test_uma_familia_grande_sem_chave_nao_e_dada_como_util(self):
        """MUITA QUANTIDADE E NENHUMA JOIN KEY. `competitors` tem 577 linhas e
        zero problema. O estudo tem de a marcar NOT_POSSIBLE, nao «rica»."""
        m = medida()
        self.assertEqual(m["FAMILIAS"]["competitors"]["ISSUE_IDS"], 0)
        for c in m["CRUZAMENTOS"]:
            if c["A"] == "competitors" or c["B"] == "competitors":
                self.assertEqual(c["CROSSING_STATE"], "NOT_POSSIBLE",
                                 f"{c['CROSSING_ID']} nao devia ser possivel")


class RT02_MesmoDatasetDuasFontes(unittest.TestCase):
    def test_o_dominio_nao_e_a_fonte(self):
        """MESMO DATASET CONTADO COMO DUAS FONTES — e o seu contrario: muitas
        origens contadas como uma. A identidade do V2.1 e o DOMINIO."""
        H = D.pacote_v21()
        conta = {}
        for linhas in H["collections"].values():
            if not isinstance(linhas, list):
                continue
            for r in linhas:
                for s in (r.get("SOURCE_IDS") or []):
                    conta[str(s)] = conta.get(str(s), 0) + 1
        maiores = sorted(conta.values(), reverse=True)[:2]
        total = sum(conta.values())
        self.assertGreater(sum(maiores) / total, 0.5,
                           "se isto deixar de ser verdade, o gap GAP-IT-010 mudou")
        self.assertIn("GAP-IT-010", [g["COLLECTION_GAP_ID"] for g in matriz()["COLLECTION_GAPS"]])


class RT03_RegistoNaoEVenda(unittest.TestCase):
    def test_nenhuma_superficie_promete_venda(self):
        """REGISTO CONFUNDIDO COM VENDA. INT-LAW-067."""
        proibidas = ("venda", "quota", "receita", "procura", "market share",
                     "disponibilidade comercial")
        for s in matriz()["SUPERFICIES"]:
            texto = " ".join(s["NAO_PODE_DECIDIR"]).lower()
            saida = (s["ANALYTIC_OUTPUT_REQUIRED"] + " " + s["BUSINESS_QUESTION"]).lower()
            for p in proibidas:
                self.assertNotIn(p, saida,
                                 f"{s['TOOL']} promete «{p}» na saida")
            if s["TOOL"] in ("PORTFOLIO", "OPPORTUNITY RADAR", "MARKET PULSE",
                             "COMPETITOR WATCH"):
                self.assertTrue(any(p in texto for p in proibidas),
                                f"{s['TOOL']} nao declara a fronteira comercial")


class RT04_PublicacaoNaoEFacto(unittest.TestCase):
    def test_o_estudo_separa_tempo_de_publicacao_de_tempo_do_facto(self):
        """PUBLICACAO CONFUNDIDA COM FATO."""
        gaps = {g["COLLECTION_GAP_ID"]: g for g in matriz()["COLLECTION_GAPS"]}
        self.assertIn("PUBLISHED_AT", gaps["GAP-IT-007"]["MISSING_TIME"])
        self.assertIn("PUBLICATION_TIME", gaps["GAP-IT-002"]["MISSING_TIME"])


class RT05_LocalDaFonteNaoELocalDoFacto(unittest.TestCase):
    def test_regiao_do_pais_nao_conta_como_regiao(self):
        """SOURCE LOCATION CONFUNDIDA COM FACT LOCATION. `REGION_IDS` a 100 %
        em `competitors` e GEO_ITALY — um pais nao distingue Puglia de Veneto."""
        H = D.pacote_v21()
        comp = H["collections"]["competitors"]
        com_regiao = sum(1 for r in comp
                         if any(str(x).startswith("REGION_") for x in (r.get("REGION_IDS") or [])))
        self.assertEqual(len(comp), 577)
        self.assertLess(com_regiao, 10)
        self.assertEqual(medida()["FAMILIAS"]["competitors"]["REGION_SUBNACIONAL"], com_regiao)

    def test_a_afiliacao_nao_promove_a_regiao_do_estudo(self):
        self.assertEqual(medida()["FAMILIAS"]["science"]["REGION_SUBNACIONAL"], 0)


class RT06_CienciaSemCulturaOuProblema(unittest.TestCase):
    def test_ciencia_sem_problema_nao_cruza(self):
        """CIENCIA SEM CULTURA/PROBLEMA."""
        m = medida()
        self.assertEqual(m["FAMILIAS"]["science"]["ISSUE_IDS"], 0)
        por_id = {c["CROSSING_ID"]: c for c in m["CRUZAMENTOS"]}
        for x in ("X-FIELD-x-SCIENCE", "X-CIENCIA-x-PORTFOLIO"):
            self.assertEqual(por_id[x]["CROSSING_STATE"], "NOT_POSSIBLE")


class RT07_VozSemLocalNemData(unittest.TestCase):
    def test_voz_sem_quando_e_sem_onde_nao_vira_sinal(self):
        """FIELD VOICE SEM LOCAL/DATA."""
        m = medida()
        v = m["FAMILIAS"]["voices"]
        self.assertEqual(v["ISSUE_IDS"], 0)
        self.assertLess(v["REFERENCE_DATE"], v["N"] / 2)
        por_id = {c["CROSSING_ID"]: c for c in m["CRUZAMENTOS"]}
        self.assertEqual(por_id["X-VOZ-x-CAMPO"]["CROSSING_STATE"], "NOT_POSSIBLE")

    def test_as_seventeen_vozes_do_pacote_antigo_nao_sabem_quando(self):
        d = D._carrega("italy-ingested.js", "window.ITALY_INGEST")
        vozes = d["VOICES"]
        self.assertEqual(len(vozes), 17)
        self.assertEqual(sum(D.sabe(r, "DATE") for r in vozes), 0)
        self.assertEqual(sum(D.sabe(r, "REGION") for r in vozes), 0)


class RT08_ConcorrenciaSemIndependencia(unittest.TestCase):
    def test_as_duas_camadas_da_concorrencia_nao_partilham_contagem(self):
        """CONCORRENCIA SEM INDEPENDENCIA. COMPANY_CLAIM != REGULATORY_FACT."""
        s = [x for x in matriz()["SUPERFICIES"] if x["TOOL"] == "COMPETITOR WATCH"][0]
        self.assertIn("REGULATORY_FACT", s["ANALYTIC_OUTPUT_REQUIRED"])
        self.assertIn("COMPANY_CLAIM", s["ANALYTIC_OUTPUT_REQUIRED"])
        self.assertTrue(any("somar" in n for n in s["NAO_PODE_DECIDIR"]))
        self.assertIn("Zero registos de concorrente", s["O_QUE_FALTA"])


class RT09_MesmaNoticiaEmCincoSites(unittest.TestCase):
    def test_o_estudo_nao_conta_noticia_como_origem_independente(self):
        """NOTICIA REPETIDA EM CINCO SITES. Sem SAME_ORIGIN, convergencia e
        aritmetica de duplicados."""
        texto = MATRIZ_MD.read_text(encoding="utf-8")
        self.assertIn("SAME_ORIGIN", texto)
        self.assertIn("ARITMETICA DE DUPLICADOS", texto.upper())
        g = {x["COLLECTION_GAP_ID"]: x for x in matriz()["COLLECTION_GAPS"]}["GAP-IT-007"]
        self.assertIn("trial_id", g["MISSING_FIELDS"])


class RT10_NomeParecidoUneErrado(unittest.TestCase):
    def test_o_medidor_nao_casa_por_semelhanca(self):
        """PRODUTO COM NOME PARECIDO UNIDO AO ERRADO. O medidor cruza por
        interseccao de IDs, nunca por texto."""
        fonte = (RAIZ / "provas" / "demanda_de_dados_da_italia.py").read_text(encoding="utf-8")
        for proibido in ("difflib", "SequenceMatcher", "startswith(nome", "fuzz", "levensh"):
            self.assertNotIn(proibido, fonte)
        self.assertIn("va & vb", fonte, "o cruzamento tem de ser interseccao de conjuntos")


class RT11_LabelSemVersaoNemData(unittest.TestCase):
    def test_o_gap_do_rotulo_exige_versao_e_data_na_chave(self):
        """LABEL SEM VERSAO/DATA."""
        g = {x["COLLECTION_GAP_ID"]: x for x in matriz()["COLLECTION_GAPS"]}["GAP-IT-003"]
        self.assertIn("versao", g["MISSING_TIME"].lower())


class RT12_DuzentasFontesNumaFamilia(unittest.TestCase):
    def test_a_seccao_das_proximas_fontes_recusa_concentracao(self):
        """200 FONTES CONCENTRADAS NUMA UNICA FAMILIA."""
        texto = MATRIZ_MD.read_text(encoding="utf-8")
        self.assertIn("0 fontes novas", texto,
                      "o estudo tem de dizer onde fonte nova NAO resolve")
        self.assertIn("NÃO DÁ PARA DETERMINAR AINDA", texto)

    def test_o_estudo_condiciona_fonte_nova_a_normalizacao(self):
        texto = MATRIZ_MD.read_text(encoding="utf-8").upper()
        self.assertIn("200 FONTES NOVAS SAO 200 DOCUMENTOS QUE NAO CRUZAM", texto)


class RT13_PortalExigeDadoQueNenhumaLeiExige(unittest.TestCase):
    def test_nenhuma_familia_entra_sem_uma_pergunta_por_tras(self):
        """PORTAL EXIGINDO DADO QUE NENHUMA LEI EXIGE. Toda familia pedida tem
        de aparecer numa superficie que declara a pergunta que a usa."""
        M = matriz()
        pedidas = {f for g in M["COLLECTION_GAPS"] for f in [g["MISSING_DATA_FAMILY"]]}
        self.assertTrue(pedidas)
        for s in M["SUPERFICIES"]:
            self.assertTrue(s["BUSINESS_QUESTION"].strip(),
                            f"{s['TOOL']} sem pergunta — seria QUESTION_NOT_DEFINED")
            self.assertTrue(s["FAMILIAS_NECESSARIAS"])

    def test_nenhum_gap_existe_sem_ferramenta_afetada(self):
        for g in matriz()["COLLECTION_GAPS"]:
            self.assertTrue(g["TOOL_AFFECTED"].strip())
            self.assertTrue(g["QUESTION_BLOCKED"].strip())


class RT14_TelaVirandoProdutoCanonico(unittest.TestCase):
    def test_uma_tela_nao_vira_ferramenta_por_existir(self):
        """FERRAMENTA ATUAL TRATADA AUTOMATICAMENTE COMO PRODUTO CANONICO."""
        M = matriz()
        papeis = {s["TOOL"]: s["CANONICAL_PRODUCT_ROLE"] for s in M["SUPERFICIES"]}
        principais = [t for t, p in papeis.items() if p == "PRIMARY_TOOL"]
        self.assertEqual(len(principais), 1,
                         f"nove telas nao sao nove produtos: {principais}")

    def test_a_superficie_que_nao_existe_esta_declarada_como_inexistente(self):
        s = [x for x in matriz()["SUPERFICIES"] if x["TOOL"] == "LABEL INTELLIGENCE"][0]
        self.assertEqual(s["CURRENT_PORTAL_SURFACE"], "NO")
        self.assertEqual(s["VIEWS_MEDIDAS"], [])
        portal = (RAIZ / "italia-portale" / "client" / "portale.html").read_text(
            encoding="utf-8", errors="replace")
        self.assertNotIn("view === 'label'", portal)


class RT15_UnknownViraMissing(unittest.TestCase):
    def test_nao_sei_e_um_valor_contado_e_nao_uma_ausencia(self):
        """UNKNOWN TRANSFORMADO EM MISSING. Uma familia que diz «nao sei» em 17
        de 17 tem 17 linhas, nao zero."""
        d = D._carrega("italy-ingested.js", "window.ITALY_INGEST")
        vozes = d["VOICES"]
        self.assertEqual(len(vozes), 17)                    # existem
        self.assertEqual(sum(D.sabe(r, "DATE") for r in vozes), 0)   # e nao sabem
        s = [x for x in matriz()["SUPERFICIES"] if x["TOOL"] == "FIELD VOICES"][0]
        self.assertIn("79", s["O_QUE_EXISTE"])              # o estudo conta-as

    def test_um_nao_sei_declarado_nao_vira_gap_fechado(self):
        """Um gap que carrega UNKNOWN_REASON tem de dizer NAO SEI na resposta —
        e nao esconde-lo atras de um «PARCIALMENTE» que responde so a metade."""
        for g in matriz()["COLLECTION_GAPS"]:
            if not g["UNKNOWN_REASON"].strip():
                continue
            self.assertIn("NAO SEI", g["CAN_COLLECTION_CURRENTLY_ACQUIRE_IT"].upper(),
                          f"{g['COLLECTION_GAP_ID']} tem motivo de ignorancia escrito "
                          f"e responde como se soubesse")

    def test_um_gap_que_diz_nao_sei_diz_sempre_porque(self):
        for g in matriz()["COLLECTION_GAPS"]:
            if "NAO SEI" in g["CAN_COLLECTION_CURRENTLY_ACQUIRE_IT"].upper():
                self.assertTrue(g["UNKNOWN_REASON"].strip(),
                                f"{g['COLLECTION_GAP_ID']} diz NAO SEI e nao diz porque")


class RT16_MissingViraZero(unittest.TestCase):
    def test_familia_inexistente_e_dita_inexistente_e_nao_zero_silencioso(self):
        """MISSING TRANSFORMADO EM ZERO."""
        fluxo = FLUXO_MD.read_text(encoding="utf-8")
        self.assertIn("A FAMÍLIA NÃO EXISTE", fluxo)
        texto = MATRIZ_MD.read_text(encoding="utf-8")
        self.assertIn("Registar como `NÃO SEI`, não como zero", texto)


class RT17_JanelaEsperadaComoObservacao(unittest.TestCase):
    def test_nenhuma_janela_canonica_tem_fonte_e_o_estudo_di_lo(self):
        """JANELA AGRONOMICA TRATADA COMO OBSERVACAO REAL."""
        t = (RAIZ / "italia-portale" / "client" / "italy-canonical-windows.js").read_text(
            encoding="utf-8")
        W = json.loads(t[t.index("window.ITALY_CANONICAL = ")
                         + len("window.ITALY_CANONICAL = "):t.rindex("}") + 1])
        janelas = W["windows"]
        self.assertEqual(len(janelas), 29)
        self.assertEqual(sum(1 for w in janelas if w.get("CROP_STAGE_SOURCE")), 0)
        self.assertEqual(sum(1 for w in janelas if w.get("SOURCE_IDS")), 0)
        self.assertEqual(sum(1 for w in janelas if w.get("PRODUCT_MATCHES")), 0)
        self.assertEqual(sum(1 for w in janelas
                             if str(w.get("PROVENANCE")) == "CONFIRMED"), 0)
        texto = MATRIZ_MD.read_text(encoding="utf-8").upper()
        self.assertIn("JANELA ESPERADA NÃO É OBSERVAÇÃO", texto)


class RT18_FixtureContadoComoDado(unittest.TestCase):
    def test_o_medidor_le_o_pacote_e_nunca_o_ficheiro_de_demonstracao(self):
        """FIXTURE/DEMO CONTADO COMO DADO."""
        fonte = (RAIZ / "provas" / "demanda_de_dados_da_italia.py").read_text(encoding="utf-8")
        self.assertNotIn("italy-demo-data", fonte)
        self.assertNotIn("D.CASES", fonte)
        self.assertIn("italy-v21.js", fonte)

    def test_a_oportunidade_real_e_tres_e_o_estudo_nao_diz_vinte_e_nove(self):
        m = medida()
        self.assertEqual(m["FAMILIAS"]["opportunities"]["N"], 3)
        s = [x for x in matriz()["SUPERFICIES"] if x["TOOL"] == "OPPORTUNITY RADAR"][0]
        self.assertIn("3 OPPORTUNITIES", s["O_QUE_EXISTE"])


class RT19_MesmoConteudoAlimentaConvergenciaDuasVezes(unittest.TestCase):
    def test_o_recorte_nao_e_contado_como_coleccao_independente(self):
        """MESMO CONTEUDO ALIMENTANDO CONVERGENCIA DUAS VEZES. `futureEvents` e
        um RECORTE de `events` — o proprio pacote avisa."""
        H = D.pacote_v21()
        self.assertIn("RECORTE", H["DOUBLE_COUNT_WARNING"].upper())
        ids_e = {r["ID"] for r in H["collections"]["events"]}
        ids_f = {r["ID"] for r in H["collections"]["futureEvents"]}
        self.assertTrue(ids_f & ids_e, "se deixarem de se sobrepor, o aviso mudou")
        for c in medida()["CRUZAMENTOS"]:
            self.assertNotIn("futureEvents", (c["A"], c["B"]),
                             "um recorte nao entra num cruzamento como ponta propria")


class RT20_GapChamandoCollector(unittest.TestCase):
    def test_nenhum_gap_escolhe_rota_de_coleta(self):
        """GAP GERANDO CHAMADA DIRETA DE COLLECTOR. INT-LAW-151: a Intelligence
        pede prova, nao escolhe rota."""
        with io.open(GAPS_CSV, encoding="utf-8") as f:
            linhas = list(csv.DictReader(f))
        self.assertEqual(len(linhas), 10)
        for g in linhas:
            todo = " ".join(g.values()).lower()
            for proibido in ("collector", "scraper", "requests.get", "curl ",
                             "crawl", "endpoint a chamar"):
                self.assertNotIn(proibido, todo,
                                 f"{g['COLLECTION_GAP_ID']} escolhe rota: «{proibido}»")

    def test_o_estudo_nao_importa_nada_da_coleta(self):
        fonte = (RAIZ / "provas" / "demanda_de_dados_da_italia.py").read_text(encoding="utf-8")
        import ast
        arvore = ast.parse(fonte)
        for no in ast.walk(arvore):
            nomes = []
            if isinstance(no, ast.Import):
                nomes = [a.name for a in no.names]
            elif isinstance(no, ast.ImportFrom):
                nomes = [no.module or ""]
            for n in nomes:
                self.assertFalse(n.startswith(("coleta", "admissao", "orquestrador",
                                               "motor", "fontes")),
                                 f"o estudo importa «{n}» — estudo nao coleta")


class M1_ValorPartilhadoNaoELinhaQueAtravessa(unittest.TestCase):
    """Apanhada por mutacao: apagar a guarda de zero linhas nao mudava teste
    nenhum, porque nenhum cruzamento REAL cai hoje nesse caso. Um teste que so
    observa a arvore de hoje nao mede a lei — mede a fotografia."""

    def test_valores_em_comum_sem_uma_linha_completa_e_NOT_POSSIBLE(self):
        a = [{"CROP_IDS": ["CROP_OLIVE"], "ISSUE_IDS": []},
             {"CROP_IDS": [], "ISSUE_IDS": ["ISSUE_OLIVE_FLY"]}]
        b = [{"CROP_IDS": ["CROP_OLIVE"], "ISSUE_IDS": ["ISSUE_OLIVE_FLY"]}]
        veredito = D.julga(
            dict(ID="X-SINTETICO", PERGUNTA="—", A="a", B="b",
                 CHAVES=("CROP_IDS", "ISSUE_IDS")), {"a": a, "b": b})
        # As duas pontas partilham AS DUAS chaves...
        self.assertEqual(veredito["INTERSECCAO"], {"CROP_IDS": 1, "ISSUE_IDS": 1})
        # ...e mesmo assim nenhuma linha de `a` carrega as duas ao mesmo tempo.
        self.assertEqual(veredito["LINHAS_QUE_ATRAVESSAM"]["a"], 0)
        self.assertEqual(veredito["CROSSING_STATE"], "NOT_POSSIBLE")
        self.assertTrue(any("nenhuma linha" in x for x in veredito["BLOQUEIO"]))

    def test_quando_ha_linhas_completas_o_cruzamento_deixa_de_ser_impossivel(self):
        a = [{"CROP_IDS": ["CROP_OLIVE"], "ISSUE_IDS": ["ISSUE_OLIVE_FLY"]}]
        b = [{"CROP_IDS": ["CROP_OLIVE"], "ISSUE_IDS": ["ISSUE_OLIVE_FLY"]}]
        veredito = D.julga(
            dict(ID="X-SINTETICO", PERGUNTA="—", A="a", B="b",
                 CHAVES=("CROP_IDS", "ISSUE_IDS")), {"a": a, "b": b})
        self.assertEqual(veredito["CROSSING_STATE"], "PARTIAL")


class M2_IgnoranciaComExplicacaoContinuaIgnorancia(unittest.TestCase):
    """Apanhada por mutacao: `sabe()` reconhecia «NAO SEI» exacto e tambem
    «NAO SEI — porque», e so a primeira forma aparecia no caminho medido. A
    segunda ficava sem prova — e uma linha sem prova cai sem ninguem dar por ela.

        UM CAMPO QUE EXPLICA PORQUE NAO SABE CONTINUA A NAO SABER.
    """

    def test_a_forma_com_explicacao_nao_conta_como_conhecimento(self):
        self.assertFalse(D.sabe({"x": "NAO SEI"}, "x"))
        self.assertFalse(D.sabe({"x": "NAO SEI — a coluna nao foi extraida"}, "x"))
        self.assertFalse(D.sabe({"x": "nao sei — em minusculas"}, "x"))
        self.assertTrue(D.sabe({"x": "2026-09-01"}, "x"))

    def test_e_ha_dado_real_nesta_arvore_com_essa_forma(self):
        """Se isto deixar de existir, o teste acima passa a ser teorico — e o
        teste tem de dizer que passou a ser."""
        d = D._carrega("italy-ingested.js", "window.ITALY_INGEST")
        ligacoes = d["LINKS"]
        self.assertEqual(len(ligacoes), 219)
        com_epoca = sum(D.sabe(r, "timing") for r in ligacoes)
        self.assertEqual(com_epoca, 0,
                         "219 linhas de uso, e a epoca de aplicacao e ignorancia "
                         "explicada em todas")
        janelas = d["CROP_WINDOWS"]
        self.assertEqual(sum(D.sabe(r, "OBSERVED_STAGE") for r in janelas), 2)


class OQueOEstudoAfirma(unittest.TestCase):
    """As contagens que o documento imprime têm de ser as que o medidor mede.
    Um número escrito à mão envelhece em silêncio."""

    def test_o_veredito_bate_com_a_medicao(self):
        M, m = matriz(), medida()
        estados = [c["CROSSING_STATE"] for c in m["CRUZAMENTOS"]]
        v = M["VEREDITO"]
        self.assertEqual(v["CRUZAMENTOS_POSSIVEIS"], estados.count("POSSIBLE"))
        self.assertEqual(v["CRUZAMENTOS_PARCIAIS"], estados.count("PARTIAL"))
        self.assertEqual(v["CRUZAMENTOS_IMPOSSIVEIS"], estados.count("NOT_POSSIBLE"))

    def test_todos_os_impossiveis_sao_bloqueados_pela_mesma_chave(self):
        impossiveis = [c for c in medida()["CRUZAMENTOS"]
                       if c["CROSSING_STATE"] == "NOT_POSSIBLE"]
        self.assertTrue(impossiveis)
        for c in impossiveis:
            self.assertTrue(any("ISSUE_IDS" in b for b in c["BLOQUEIO"]),
                            f"{c['CROSSING_ID']} falha por outra chave: {c['BLOQUEIO']}")

    def test_o_vocabulario_de_problema_e_muito_menor_que_o_texto_livre(self):
        v = medida()["VOCABULARIO_DE_PROBLEMA"]
        self.assertLess(v["ISSUE_IDS_DISTINTOS"], v["NOMES_CITADOS_EM_TEXTO_LIVRE"] / 4)

    def test_cada_superficie_aponta_para_um_gap_que_existe(self):
        M = matriz()
        conhecidos = {g["COLLECTION_GAP_ID"] for g in M["COLLECTION_GAPS"]}
        for s in M["SUPERFICIES"]:
            self.assertIn(s["GAP_PRINCIPAL"], conhecidos, s["TOOL"])

    def test_cada_cruzamento_citado_por_uma_superficie_foi_medido(self):
        M, m = matriz(), medida()
        medidos = {c["CROSSING_ID"] for c in m["CRUZAMENTOS"]}
        for s in M["SUPERFICIES"]:
            for x in s["CROSSINGS_NECESSARIOS"]:
                self.assertIn(x, medidos, f"{s['TOOL']} cita {x}, que ninguem mediu")

    def test_o_estudo_declara_a_quem_obedece(self):
        M = matriz()
        self.assertTrue(M["NAO_CRIA"])
        for caminho in M["SUBORDINADO_A"]:
            self.assertTrue((RAIZ / caminho).exists(), f"{caminho} nao existe")


if __name__ == "__main__":
    unittest.main()
