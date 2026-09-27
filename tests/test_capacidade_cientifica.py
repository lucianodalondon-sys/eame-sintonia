#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""CAP-SCI minima — forca, aplicabilidade, independencia, especies e ligacao.

    python3 -m unittest tests.test_capacidade_cientifica -v

⚠️ FIXTURE SINTETICA. `tests/dados/cap-sci/SINTETICO-ESTUDOS-CAP-SCI.json` e
marcada `SINTETICO: true`: nenhum estudo existe, DOI 10.0000/* e ORCID/ROR SINT-*
sao ficticios. O registo T6 real NAO esta nesta arvore; o que se prova aqui sao
as REGRAS, nao os numeros da Sala.

A referencia ADAMA usada nas ligacoes e a REAL (`referencia/adama`, so leitura):
as quatro ligacoes parciais da pre-medicao T6 (folpet, metalaxil-M, cimoxanil,
fosetyl-Al em vite x peronospora) tem de sair com os mesmos produtos.
"""
import copy
import json
import sys
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
for g in ("", "motor", "provas"):
    if str(RAIZ / g) not in sys.path:
        sys.path.insert(0, str(RAIZ / g))

import capacidade_cientifica as SCI            # noqa: E402
import corrida_da_inteligencia as CI           # noqa: E402

FIXTURE = RAIZ / "tests" / "dados" / "cap-sci" / "SINTETICO-ESTUDOS-CAP-SCI.json"
DADO = json.loads(FIXTURE.read_text(encoding="utf-8"))
REF = SCI.carregar_referencia()


def itens():
    return copy.deepcopy(DADO["ITENS"])


def rodar(xs=None, ref=REF):
    xs = itens() if xs is None else xs
    livro = CI.correr("CAP-SCI teste", xs,
                      universo={"CORTE": "SINTETICO", "ITENS_NO_CORTE": len(xs)})
    return SCI.julgar(livro, xs, ref)


SAIDA = rodar()
POR_ID = {e["ITEM_ID"]: e for e in SAIDA["ESTUDOS"]}
LIG = {x["ITEM_ID"]: x for x in SAIDA["LIGACOES"]}


def um(n):
    return next(i for i in itens() if i["ITEM_ID"] == "SINT-T6-%02d" % n)


class AFixtureESintetica(unittest.TestCase):
    def test_marcada_e_itens_sao_READY_completos(self):
        self.assertIs(DADO["SINTETICO"], True)
        self.assertIn("SINTETICA", DADO["AVISO"])
        for i in DADO["ITENS"]:
            self.assertTrue(i["ITEM_ID"].startswith("SINT-"))
            self.assertEqual(sorted(i), sorted(SCI.CAMPOS_DO_READY))


class NuncaLerIdentidadeDeForaDoREADY(unittest.TestCase):
    def test_campo_fora_do_contrato_e_recusado_e_nao_ignorado(self):
        xs = itens()
        xs[0]["DOI"] = "10.9999/de-fora"
        livro = CI.correr("t", xs)
        with self.assertRaisesRegex(SCI.LeiViolada, "IDENTIDADE_DE_FORA_DO_READY"):
            SCI.julgar(livro, xs, REF)

    def test_item_que_nao_esta_PRONTO_e_recusado(self):
        xs = itens()
        xs[0]["ESTADO"] = "EM_TRIAGEM"
        with self.assertRaisesRegex(SCI.LeiViolada, "nao esta READY"):
            SCI.julgar(CI.correr("t", xs), xs, REF)

    def test_itens_diferentes_dos_da_corrida_sao_recusados(self):
        xs = itens()
        livro = CI.correr("t", xs[:-1])
        with self.assertRaisesRegex(SCI.LeiViolada, "nao sao os que a corrida"):
            SCI.julgar(livro, xs, REF)

    def test_o_texto_nao_e_lido(self):
        # SINT-T6-10: o TEXTO diz folpet, Padova, 2022, n=30. Nada disso vale.
        e = POR_ID["SINT-T6-10"]
        self.assertEqual(e["MOLECULA"], SCI.NAO_SEI)
        self.assertEqual(e["N"], 6)
        self.assertEqual(e["PERIODO_DO_ESTUDO"]["ESTADO"], "NAO_SEI")
        self.assertNotIn("SINT-T6-10", LIG)

    def test_item_sem_proveniencia_fica_FORA_com_motivo(self):
        self.assertEqual(SAIDA["FORA"], [{"ITEM_ID": "SINT-T6-12", "PORQUE": "SEM_PROVENIENCIA"}])
        self.assertEqual(SAIDA["UNIVERSO"]["ITENS"], len(DADO["ITENS"]))


class LocalEPeriodoSoQuandoProvados(unittest.TestCase):
    def test_afiliacao_nao_vira_local_do_estudo(self):
        e = POR_ID["SINT-T6-10"]
        self.assertEqual(e["LOCAL_DO_ESTUDO"]["VALOR"], SCI.NAO_SEI)
        self.assertNotIn("Padova", json.dumps(e["LOCAL_DO_ESTUDO"]))

    def test_nenhuma_chave_de_afiliacao_vira_local(self):
        for chave in SCI.NAO_SAO_LOCAL_DO_ESTUDO:
            i = um(2)
            i["FATO"][chave] = "Verona, Italia"
            self.assertEqual(SCI.julgar_estudo(i)["LOCAL_DO_ESTUDO"]["VALOR"], SCI.NAO_SEI, chave)

    def test_source_location_nao_vira_local_do_estudo(self):
        self.assertEqual(um(2)["SOURCE_LOCATION"], "Italia")
        self.assertEqual(POR_ID["SINT-T6-02"]["LOCAL_DO_ESTUDO"]["ESTADO"], "NAO_SEI")

    def test_publicacao_nao_vira_periodo(self):
        e = POR_ID["SINT-T6-02"]
        self.assertEqual(e["PERIODO_DO_ESTUDO"]["VALOR"], SCI.NAO_SEI)
        self.assertTrue(e["PERIODO_DO_ESTUDO"]["PUBLICATION_TIME_NAO_E_PERIODO"])

    def test_local_e_periodo_com_base_sao_provados(self):
        e = POR_ID["SINT-T6-01"]
        self.assertEqual(e["LOCAL_DO_ESTUDO"], {"VALOR": "Veneto", "ESTADO": "PROVADO",
                                                 "BASE": um(1)["FACT_LOCATION_BASIS"]})
        self.assertEqual(e["PERIODO_DO_ESTUDO"]["ESTADO"], "PROVADO")
        self.assertEqual(e["APLICABILIDADE"]["ESTADO"], "COMPLETA")

    def test_local_sem_base_nao_ancora(self):
        i = um(1)
        i["FACT_LOCATION_BASIS"] = "NAO SEI"
        self.assertEqual(SCI.local_do_estudo(i)["ESTADO"], "NAO_SEI")


class Forca(unittest.TestCase):
    def test_forca_e_decomposta(self):
        f = POR_ID["SINT-T6-01"]["FORCA"]
        self.assertEqual((f["NIVEL"], f["DESENHO"], f["N"]),
                         ("FORTE", "ENSAIO_DE_CAMPO_RANDOMIZADO", 12))
        self.assertTrue(f["PORQUE"])

    def test_estudo_pequeno_e_indicativo(self):
        f = POR_ID["SINT-T6-03"]["FORCA"]
        self.assertEqual(f["NIVEL"], "INDICATIVA")
        self.assertTrue(f["ESTUDO_PEQUENO"])

    def test_sem_metodo_forca_e_NAO_SEI_e_nao_fraca(self):
        self.assertEqual(SCI.forca(SCI.NAO_SEI, 50)["NIVEL"], SCI.NAO_SEI)

    def test_metodo_fora_do_vocabulario_e_NAO_SEI(self):
        self.assertEqual(SCI._metodo({"method": "parece um ensaio"})[0], SCI.NAO_SEI)

    def test_sem_n_nao_passa_de_fraca(self):
        self.assertEqual(SCI.forca("ENSAIO_DE_CAMPO_RANDOMIZADO", SCI.NAO_SEI)["NIVEL"], "FRACA")

    def test_revisao_nao_e_evidencia_primaria(self):
        e = POR_ID["SINT-T6-13"]
        self.assertEqual(e["FORCA"]["NIVEL"], "NAO_APLICAVEL")
        self.assertFalse([r for r in SAIDA["REPLICACAO"] if "SINT-T6-13" in r["ESTUDOS"]])


class EstudoPequenoNuncaViraOProdutoNaoFunciona(unittest.TestCase):
    def test_pequeno_e_negativo_e_so_indicio(self):
        self.assertEqual(POR_ID["SINT-T6-03"]["LEITURA"], "INDICIO_A_CONFIRMAR")

    def test_negativo_forte_diz_nestas_condicoes(self):
        self.assertEqual(POR_ID["SINT-T6-04"]["LEITURA"],
                         "NAO_DEMONSTROU_EFEITO_NESTAS_CONDICOES")

    def test_nenhuma_leitura_proibida_no_livro(self):
        texto = json.dumps(SAIDA, ensure_ascii=False).upper()
        for p in SCI.LEITURAS_PROIBIDAS:
            self.assertNotIn(p, texto)
        self.assertTrue(set(POR_ID[k]["LEITURA"] for k in POR_ID) <= set(SCI.LEITURAS))

    def test_a_trava_rebenta_se_alguem_escrever_a_leitura_proibida(self):
        with self.assertRaises(SCI.LeiViolada):
            SCI._vigiar_leituras_proibidas({"X": "o_produto_nao_funciona"})

    def test_estudo_nao_e_resultado_do_produto(self):
        self.assertIn("RESULTADO_DO_PRODUTO", POR_ID["SINT-T6-01"]["NAO_E"])
        self.assertIn("NAO diz que o estudo testou o produto", LIG["SINT-T6-01"]["NAO_PROVA"])


class Especies(unittest.TestCase):
    def test_model_rule_e_especie_propria_e_nao_liga_a_produto(self):
        self.assertEqual(SAIDA["REGRAS_DE_MODELO"], ["SINT-T6-07"])
        self.assertEqual(POR_ID["SINT-T6-07"]["LEITURA"], "REGRA_DE_MODELO_DECLARADA")
        self.assertNotIn("SINT-T6-07", LIG)
        self.assertFalse([r for r in SAIDA["REPLICACAO"] if "SINT-T6-07" in r["ESTUDOS"]])

    def test_resistencia_e_especie_propria_com_local_e_periodo(self):
        self.assertEqual(SAIDA["RESISTENCIAS"], ["SINT-T6-08"])
        self.assertEqual(POR_ID["SINT-T6-08"]["LEITURA"],
                         "RESISTENCIA_OBSERVADA_NESTE_LOCAL_E_PERIODO")

    def test_resistencia_sem_local_nao_se_generaliza(self):
        i = um(8)
        i["FACT_LOCATION"] = "NAO SEI"
        self.assertEqual(SCI.julgar_estudo(i)["LEITURA"],
                         "RESISTENCIA_OBSERVADA_LOCAL_OU_PERIODO_NAO_PROVADO")

    def test_especie_nao_declarada_e_NAO_SEI_mesmo_com_texto_sugestivo(self):
        i = um(8)
        del i["FATO"]["evidence_species"]
        i["TEXTO"] = "resistance resistenza RESISTANCE"
        self.assertEqual(SCI.julgar_estudo(i)["ESPECIE"], SCI.NAO_SEI)

    def test_conflito_no_fato_fica_conflito(self):
        e = POR_ID["SINT-T6-15"]
        self.assertEqual(e["CULTURA"], SCI.NAO_SEI)
        self.assertIn("CONFLITO", e["PORQUE_NAO_SEI"]["CULTURA"])
        self.assertEqual(e["LEITURA"], "SEM_LEITURA_TEMA_NAO_PROVADO")


class Independencia(unittest.TestCase):
    PAR = "VITE x PERONOSPORA"

    def test_mesmo_ensaio_e_mesmo_autor_sao_um_grupo(self):
        grupos = SAIDA["INDEPENDENCIA"][self.PAR]["GRUPOS"]
        self.assertIn(["SINT-T6-01", "SINT-T6-02", "SINT-T6-05"], grupos)

    def test_mesmo_dataset_e_um_grupo(self):
        self.assertIn(["SINT-T6-04", "SINT-T6-06"], SAIDA["INDEPENDENCIA"][self.PAR]["GRUPOS"])

    def test_tres_papers_dois_do_mesmo_ensaio_contam_dois_grupos(self):
        r = next(x for x in SAIDA["REPLICACAO"]
                 if x["MOLECULA"] == "FOLPET" and x["DIRECAO"] == "+")
        self.assertEqual(r["ESTUDOS"], ["SINT-T6-01", "SINT-T6-05", "SINT-T6-16"])
        self.assertEqual(r["GRUPOS_COM_CHAVE"], 2)
        self.assertEqual(r["REPLICACAO"], "REPLICADO_EM_GRUPOS_DISTINTOS_TETO")

    def test_sem_chave_nao_conta_como_independente(self):
        ind = SAIDA["INDEPENDENCIA"][self.PAR]
        self.assertIn("SINT-T6-11", ind["SEM_CHAVE_DE_INDEPENDENCIA"])
        self.assertIn("NAO SEI", ind["INDEPENDENCIA"])
        r = next(x for x in SAIDA["REPLICACAO"]
                 if x["MOLECULA"] == "FOLPET" and x["DIRECAO"] == "-")
        self.assertEqual(r["REPLICACAO"], "NAO_SEI")

    def test_um_grupo_com_chave_mais_um_sem_chave_nao_e_replicacao(self):
        # (mutante M09) o estudo sem chave nao pode virar o segundo grupo
        xs = itens()
        novo = copy.deepcopy(next(i for i in xs if i["ITEM_ID"] == "SINT-T6-11"))
        novo.update(ITEM_ID="SINT-T6-17", RAW_OBSERVATION_ID="SINT-RAW-17")
        novo["FATO"].update(doi="10.0000/sint.17", molecule="cimoxanil")
        xs.append(novo)
        r = next(x for x in rodar(xs)["REPLICACAO"] if x["MOLECULA"] == "CIMOXANIL")
        self.assertEqual((r["GRUPOS_COM_CHAVE"], r["ESTUDOS_SEM_CHAVE"]), (1, 1))
        self.assertEqual(r["REPLICACAO"], "NAO_SEI")

    def test_contradicao_e_declarada(self):
        r = next(x for x in SAIDA["REPLICACAO"]
                 if x["MOLECULA"] == "FOLPET" and x["DIRECAO"] == "+")
        self.assertEqual(r["CONTRADICAO_COM"], ["-"])

    def test_replicacao_ausente_e_declarada(self):
        r = next(x for x in SAIDA["REPLICACAO"] if x["MOLECULA"] == "CIMOXANIL")
        self.assertEqual(r["REPLICACAO"], "NAO_REPLICADO")
        self.assertTrue(r["REPLICACAO_AUSENTE_DECLARADA"])

    def test_mesmo_doi_e_mesma_obra(self):
        xs = itens()
        xs[2]["FATO"]["doi"] = xs[0]["FATO"]["doi"]
        s = rodar(xs)
        self.assertEqual(s["INDEPENDENCIA"][self.PAR]["OBRAS"],
                         SAIDA["INDEPENDENCIA"][self.PAR]["OBRAS"] - 1)


class LigacaoAoProdutoADAMA(unittest.TestCase):
    def _nomes(self, iid):
        return sorted(p["NOME_NO_ROTULO"] for m in LIG[iid]["POR_MOLECULA"]
                      for p in m["PRODUTOS"])

    def test_as_quatro_parciais_do_miildio(self):
        self.assertEqual(LIG["SINT-T6-02"]["ESTADO"], "PARTIAL")
        self.assertEqual(self._nomes("SINT-T6-02"), ["FOLPAN GOLD", "SESTO GOLD"])
        self.assertEqual(self._nomes("SINT-T6-03"),
                         ["ANTERLEX", "BADGER 45% WG", "CARSON 45% WG", "DAUPHIN 45",
                          "MOXYL MK", "VANTEX"])
        self.assertEqual(self._nomes("SINT-T6-04"), ["MOMENTUM PFNPE"])
        self.assertEqual(self._nomes("SINT-T6-05"), ["FOLPAN GOLD", "SESTO GOLD"])
        self.assertEqual(LIG["SINT-T6-05"]["POR_MOLECULA"][0]["FALTA"], ["LOCAL", "PERIODO"])

    def test_candidata_so_com_local_e_periodo(self):
        self.assertEqual(LIG["SINT-T6-01"]["ESTADO"], "CANDIDATE")

    def test_sem_molecula_nao_liga(self):
        self.assertNotIn("SINT-T6-10", LIG)
        e = SCI.ligar_ao_produto(POR_ID["SINT-T6-10"], REF)
        self.assertEqual((e["ESTADO"], e["FALTA"], e["PRODUTOS"]),
                         ("NOT_POSSIBLE", ["MOLECULA"], []))

    def test_regra_de_modelo_com_molecula_nao_liga(self):
        # (mutante M15) a regra de modelo nomeia a molecula e continua sem ligacao
        xs = itens()
        next(i for i in xs if i["ITEM_ID"] == "SINT-T6-07")["FATO"]["molecule"] = "folpet"
        self.assertNotIn("SINT-T6-07", {x["ITEM_ID"] for x in rodar(xs)["LIGACOES"]})

    def test_metalaxyl_nao_e_metalaxyl_M(self):
        # a resistencia a METALAXYL nao herda os rotulos do METALAXYL-M
        self.assertNotIn("SINT-T6-08", LIG)
        e = SCI.ligar_ao_produto(POR_ID["SINT-T6-08"], REF)
        self.assertEqual(e["ESTADO"], "UNKNOWN_REFERENCIA")

    def test_referencia_incompleta_nao_vira_ADAMA_nao_tem(self):
        e = SCI.ligar_ao_produto(POR_ID["SINT-T6-14"], REF)
        self.assertEqual(e["ESTADO"], "UNKNOWN_REFERENCIA")
        self.assertIn("referencia incompleta", e["POR_MOLECULA"][0]["PORQUE"])

    def test_molecula_da_ADAMA_sem_rotulo_no_tema(self):
        self.assertEqual(SCI.ligar_ao_produto(POR_ID["SINT-T6-09"], REF)["ESTADO"],
                         "RELACAO_SEM_ROTULO")

    def test_referencia_ilegivel_e_NAO_SEI(self):
        s = rodar(ref=SCI.carregar_referencia(RAIZ / "nao-existe"))
        self.assertEqual(s["LIGACOES"], [])
        self.assertEqual(s["REFERENCIA"]["ESTADO"], SCI.NAO_SEI)

    def test_rotulo_nao_ativo_nao_liga(self):
        ref = copy.deepcopy(REF)
        for r in ref["REGISTRATIONS"]:
            r["ADMIN_ACTIVE"] = False
        e = SCI.ligar_ao_produto(POR_ID["SINT-T6-01"], ref)
        self.assertEqual(e["ESTADO"], "RELACAO_SEM_ROTULO")

    def test_semelhanca_nao_e_equivalencia(self):
        e = copy.deepcopy(POR_ID["SINT-T6-01"])
        e["CULTURA"] = "vite da tavola"
        self.assertEqual(SCI.ligar_ao_produto(e, REF)["ESTADO"], "RELACAO_SEM_ROTULO")


class NaoProduzJulgamentoDeMais(unittest.TestCase):
    def test_sem_finding_nem_opportunity(self):
        self.assertEqual(SAIDA["NAO_PRODUZ"],
                         ["FINDING", "OPPORTUNITY", "INCIDENCIA_DE_CAMPO", "SCORE_UNICO"])
        self.assertNotIn("FINDINGS", SAIDA)
        self.assertNotIn("OPPORTUNITIES", SAIDA)

    def test_so_le_corrida_fechada(self):
        with self.assertRaises(SCI.LeiViolada):
            SCI.julgar({"RESULT_STATE": "ERROR"}, [], REF)

    def test_livro_leva_a_corrida_e_a_impressao_da_referencia(self):
        self.assertTrue(SAIDA["INTELLIGENCE_RUN_ID"].startswith("IR-"))
        self.assertEqual(SAIDA["RULESET_DA_CORRIDA"], "G0/v4")
        self.assertEqual(len(SAIDA["REFERENCIA"]["SHA256"]), 4)


if __name__ == "__main__":
    unittest.main()
