#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""G0 POR AFIRMACAO (DIRETIVA-G0-POR-AFIRMACAO) — a unidade CLAIM ao lado da unidade ITEM. Sem rede, sem banco.

    python3 -m unittest tests.test_g0_da_afirmacao -v

O caso e SINTETICO e construido por regra: UM item cujo documento nao tem tempo unico (o G0 do item bloqueia) e
DUAS afirmacoes dele, cada uma com a sua data e o seu lugar escritos no proprio trecho. Nenhum trecho, id ou data
da R9 aparece aqui. O artefato tem a forma AFIRMACOES_DA_SALA/v1 do produtor (ramo produtor-afirmacoes-v1).
"""
import copy
import hashlib
import json
import sys
import unittest
from datetime import date
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
import _gavetas  # noqa: E402,F401

import motor_das_capacidades as M                # noqa: E402
import g0_da_afirmacao as G0A                    # noqa: E402
import gatilho_da_inteligencia as GI             # noqa: E402

HOJE = date(2026, 9, 28)
EXPORT_R7 = RAIZ / "tests" / "dados" / "int-r7" / "SINTETICO-R7-SALA-EXPORT.json"
#: o que a saida e o pote SEM afirmacoes sao hoje (medido antes da mudanca, 29/09): nao podem mudar
SAIDA_SEM_AFIRMACOES_SHA = "297e313a0f653170254715e3f683c0ce36ef4f9746029415689ddbf7c7f797c0"
POTE_SEM_AFIRMACOES_SHA = "cd1c724b01ca780f772d5ca3fea128db92733c4885131ae1007dc929a6a332f0"
TEXTO = ("NOTIZIARIO SINTETICO DI PROVA\n"
         "Il 3 settembre 2026 una grandinata ha colpito i vigneti a Bari.\n"
         "Il 10 settembre 2026 piogge intense si sono registrate a Lecce.\n"
         "Il bollettino e valido fino al 30 settembre 2026 in tutta la regione.\n")


def _h(o) -> str:
    return hashlib.sha256(json.dumps(o, ensure_ascii=False, sort_keys=True).encode()).hexdigest()


def _span(frase: str) -> tuple:
    a = TEXTO.index(frase)
    return a, a + len(frase)


def _afirmacao(linha: dict, frase: str, data_txt: str, valor: str, lugar: str, **mudar) -> dict:
    """Uma afirmacao na forma AFIRMACAO/v1 do produtor, tirada do TEXTO por regra (offsets calculados)."""
    a, b = _span(frase)
    ba = TEXTO.index(data_txt, a)
    la = TEXTO.index(lugar, a)
    trecho = TEXTO[a:b]
    af = {
        "CONTRATO": "AFIRMACAO/v1",
        "CLAIM_ID": "AF-SINT-" + hashlib.sha256(trecho.encode()).hexdigest()[:12],
        "ITEM_ID": linha["item_id"], "RAW_OBSERVATION_ID": linha["raw_observation_id"],
        "RAW_SHA256": linha["raw_sha256"], "SOURCE_ID": linha["source_id"],
        "PRODUTOR_VERSAO": {"CONTRATO": "AFIRMACAO/v1", "SINTETICO": True},
        "EVIDENCE_SPAN": {"INICIO": a, "FIM": b, "TRECHO": trecho, "SHA256": hashlib.sha256(trecho.encode()).hexdigest()},
        "TRECHO_SHA256": hashlib.sha256(trecho.encode()).hexdigest(),
        "CLAIM_KIND": {"VALOR": "ALERTA_EVENTO"},
        "FACT_TIME": {"VALOR": valor, "FACT_TIME_BASIS": {"TRECHO": data_txt, "INICIO": ba, "FIM": ba + len(data_txt)},
                      "FACT_TIME_PRECISION": "DATE_EXACT"},
        "FACT_TIME_ROLE": {"PAPEL": "ACONTECIMENTO", "ORIGEM": "LITERAL",
                           "BASIS": {"TRECHO": data_txt, "INICIO": ba, "FIM": ba + len(data_txt)}},
        "VALIDITY": {"VALOR": "NAO SEI"}, "MARKET_PERIOD": {"VALOR": "NAO SEI"}, "ACT_TIME": {"VALOR": "NAO SEI"},
        "FACT_LOCATION": {"VALOR": lugar, "LOCATION_SOURCE": "TEXT", "PRECISAO": "CITY", "TRECHO": lugar,
                          "INICIO": la},
        "ENTIDADES": [{"TIPO": "CULTURA", "NOME_ORIGINAL": "NAO SEI", "ENTITY_SOURCE": "UNKNOWN"}],
        "PUBLISHED_AT": {"VALOR": "2026-09-16"},
        # §5-C · a contagem do produtor: cada frase do TEXTO tem um tempo e um lugar
        "TEMPOS_NO_TRECHO": 1, "LUGARES_NO_TRECHO": 1,
    }
    for k, v in mudar.items():
        af[k] = v
    return af


class _Caso(unittest.TestCase):
    def setUp(self):
        self.exp = json.loads(EXPORT_R7.read_text(encoding="utf-8"))
        # UM item: o texto sintetico, sem tempo unico do documento (o G0 do ITEM bloqueia)
        l = self.exp["LINHAS"][0]
        l.update(texto=TEXTO, fact_time=None, fact_time_basis=None,
                 raw_sha256=hashlib.sha256(b"raw-sintetico").hexdigest(), raw_storage_path="XX/sint/raw.bin")
        for x in self.exp["LINHAS"][1:]:
            x["raw_sha256"] = hashlib.sha256(("raw-%s" % x["raw_observation_id"]).encode()).hexdigest()
        self.linha = l
        self.af1 = _afirmacao(l, "Il 3 settembre 2026 una grandinata ha colpito i vigneti a Bari.",
                              "3 settembre 2026", "2026-09-03", "Bari")
        self.af2 = _afirmacao(l, "Il 10 settembre 2026 piogge intense si sono registrate a Lecce.",
                              "10 settembre 2026", "2026-09-10", "Lecce")

    def artefato(self, *afs):
        l = self.linha
        return {"CONTRATO": "AFIRMACOES_DA_SALA/v1", "ENTRADA": {"SHA256": "SINTETICO"},
                "ITENS": [{"PROVENIENCIA": {"ITEM_ID": l["item_id"], "RUN_ID": l["run_id"]},
                           "AFIRMACOES": list(afs), "REPROVADAS": []}]}

    def correr(self, *afs, com=True):
        entrada = M.entrada_do_export(self.exp)
        return M.rodar(entrada, HOJE, "TESTE", afirmacoes=self.artefato(*afs) if com else None)

    def entrada_de(self, saida, claim):
        return next(e for e in saida["LINEAGE"] if e.get("CLAIM_ID") == claim)

    def do_item(self, saida):
        return next(e for e in saida["LINEAGE"]
                    if "CLAIM_ID" not in e and e["ITEM_ID"] == self.linha["item_id"])

    def archive(self, saida):
        return saida["ITENS_POR_FERRAMENTA"].get("archive") or []


class TestUmItemDuasAfirmacoes(_Caso):
    def test_cada_afirmacao_sai_com_o_seu_tempo_e_o_g0_do_item_continua_bloqueado(self):
        s = self.correr(self.af1, self.af2)
        self.assertEqual(self.do_item(s)["G0"], "BLOQUEADO_EM_G0")
        for af, ft in ((self.af1, "2026-09-03"), (self.af2, "2026-09-10")):
            e = self.entrada_de(s, af["CLAIM_ID"])
            self.assertEqual((e["G0_DA_AFIRMACAO"], e["FACT_TIME"], e["G0_DO_ITEM"]),
                             ("PASSOU", ft, "BLOQUEADO_EM_G0"))
        objs = {o["PROVA"][0]["CLAIM_ID"]: o for o in self.archive(s)}
        self.assertEqual(objs[self.af1["CLAIM_ID"]]["CHAVES"]["FACT_TIME"], "2026-09-03")
        self.assertEqual(objs[self.af2["CLAIM_ID"]]["CHAVES"]["FACT_TIME"], "2026-09-10")
        self.assertEqual(objs[self.af1["CLAIM_ID"]]["CHAVES"]["FACT_LOCATION"], "Bari")
        self.assertEqual(objs[self.af2["CLAIM_ID"]]["CHAVES"]["LOCATION_SOURCE"], "TEXT")

    def test_o_pote_admite_as_duas_pelo_g0_delas_e_passa_no_fiscal(self):
        pote, _ = GI.montar_o_pote(self.correr(self.af1, self.af2))
        self.assertEqual(GI.VP.validar(pote), [])
        arq = pote["COMPARTIMENTOS"]["archive"]["OBJETOS"]
        self.assertEqual(sorted(p["CLAIM_ID"] for o in arq for p in o["PROVA"]),
                         sorted([self.af1["CLAIM_ID"], self.af2["CLAIM_ID"]]))
        for o in arq:
            self.assertEqual(o["ESPECIE"], "SINAL")
            self.assertEqual(o["PROVA"][0]["G0_DE"], "AFIRMACAO")
            self.assertEqual(o["PROVA"][0]["ADMITIDA_POR"], "G0_PASSOU")
            self.assertEqual(o["PROVA"][0]["RAW_SHA256"], self.linha["raw_sha256"])

    def test_region_id_fica_nao_sei_e_nao_e_cunhado_do_lugar(self):
        for o in self.archive(self.correr(self.af1, self.af2)):
            self.assertEqual(o["CHAVES"]["REGION_ID"], "NAO SEI")
            self.assertNotEqual(o["CHAVES"]["FACT_LOCATION"], "NAO SEI")

    def test_fact_time_do_objeto_e_o_da_afirmacao_nunca_a_publicacao(self):
        for o in self.archive(self.correr(self.af1, self.af2)):
            self.assertNotEqual(o["CHAVES"]["FACT_TIME"], "2026-09-16")
            self.assertEqual(o["PROVA"][0]["FACT_TIME"], o["CHAVES"]["FACT_TIME"])

    def test_o_g0_da_afirmacao_usa_o_tempo_dela_e_nao_o_do_item(self):
        # o item nao tem tempo: se o portao lesse o FACT_TIME do item, as duas bloqueavam
        passou, falta = G0A.portao_g0_da_afirmacao(self.af1, dict(M.entrada_do_export(self.exp)["ITENS"][0]["READY"]),
                                                   TEXTO)
        self.assertTrue(passou, falta)


class TestSemAfirmacoesNadaMuda(_Caso):
    def test_a_saida_e_o_pote_sem_afirmacoes_sao_os_de_antes(self):
        exp = json.loads(EXPORT_R7.read_text(encoding="utf-8"))
        s = GI.correr_o_motor(exp, HOJE, "BASE")
        self.assertEqual(_h({k: v for k, v in s.items() if k != "CORRIDA"}), SAIDA_SEM_AFIRMACOES_SHA)
        self.assertEqual(_h(GI.montar_o_pote(s)[0]), POTE_SEM_AFIRMACOES_SHA)
        self.assertNotIn("archive", s["ITENS_POR_FERRAMENTA"])
        self.assertFalse(any("CLAIM_ID" in e for e in s["LINEAGE"]))
        for k in ("SINAIS_DAS_AFIRMACOES", "AFIRMACOES_RECUSADAS", "INTAKE_DAS_AFIRMACOES"):
            self.assertNotIn(k, s["CORRIDA"])

    def test_com_afirmacoes_a_identidade_da_corrida_muda(self):
        self.assertNotEqual(self.correr(self.af1, com=False)["INTELLIGENCE_RUN_ID"],
                            self.correr(self.af1)["INTELLIGENCE_RUN_ID"])


class TestRecusaEBloqueio(_Caso):
    def recusada(self, af):
        s = self.correr(af)
        self.assertFalse(any(e.get("CLAIM_ID") == af.get("CLAIM_ID") for e in s["LINEAGE"] if "CLAIM_ID" in e))
        self.assertEqual(self.archive(s), [])
        return " ".join(m for r in s["CORRIDA"]["AFIRMACOES_RECUSADAS"] for m in r["MOTIVOS"])

    def test_raw_sha256_diferente_do_item_e_recusada(self):
        self.assertIn("RAW_SHA256", self.recusada(dict(self.af1, RAW_SHA256="0" * 64)))

    def test_trecho_que_nao_bate_com_o_texto_e_recusada(self):
        span = dict(self.af1["EVIDENCE_SPAN"], TRECHO=self.af1["EVIDENCE_SPAN"]["TRECHO"].replace("Bari", "Roma"))
        self.assertIn("EVIDENCE_SPAN", self.recusada(dict(self.af1, EVIDENCE_SPAN=span)))

    def test_sem_claim_id_e_recusada(self):
        af = dict(self.af1)
        del af["CLAIM_ID"]
        self.assertIn("SEM_CLAIM_ID", self.recusada(af))

    def test_o_produtor_que_decide_liberacao_e_recusado(self):
        self.assertIn("PRODUTOR_DECIDIU_LIBERACAO", self.recusada(dict(self.af1, LIBERACAO="LIBERADO_PARA_CLIENTE")))

    def test_papel_que_nao_e_acontecimento_com_fact_time_bloqueia(self):
        af = dict(self.af1, FACT_TIME_ROLE=dict(self.af1["FACT_TIME_ROLE"], PAPEL="VALIDADE"))
        s = self.correr(af)
        e = self.entrada_de(s, af["CLAIM_ID"])
        self.assertEqual(e["G0_DA_AFIRMACAO"], "BLOQUEADO_EM_G0")
        self.assertIn("FACT_TIME:PAPEL_VALIDADE_NAO_E_FACTO", e["G0_FALTA"])
        self.assertEqual(self.archive(s), [])

    def test_literal_com_basis_fora_do_trecho_bloqueia(self):
        fora = TEXTO.index("30 settembre 2026")            # uma data REAL do texto, mas noutra frase
        basis = {"TRECHO": "30 settembre 2026", "INICIO": fora, "FIM": fora + len("30 settembre 2026")}
        af = dict(self.af1, FACT_TIME=dict(self.af1["FACT_TIME"], FACT_TIME_BASIS=basis),
                  FACT_TIME_ROLE=dict(self.af1["FACT_TIME_ROLE"], BASIS=basis))
        e = self.entrada_de(self.correr(af), af["CLAIM_ID"])
        self.assertIn("FACT_TIME:LITERAL_COM_BASIS_FORA_DO_TRECHO", e["G0_FALTA"])

    def test_relativo_d63_passa_mas_nunca_serve_act_now(self):
        af = dict(self.af1, FACT_TIME_ROLE=dict(self.af1["FACT_TIME_ROLE"], ORIGEM="RELATIVO_D63"))
        s = self.correr(af)
        e = self.entrada_de(s, af["CLAIM_ID"])
        self.assertEqual(e["G0_DA_AFIRMACAO"], "PASSOU")
        self.assertEqual(e["USOS_BLOQUEADOS"].get("ACT_NOW"), "RELATIVO_D63")
        self.assertNotIn("ACT_NOW", e["USOS_DISPONIVEIS"])

    def test_a_mesma_afirmacao_duas_vezes_conta_uma(self):
        dup = dict(self.af1, CLAIM_ID=self.af1["CLAIM_ID"] + "-B")
        s = self.correr(self.af1, dup)
        self.assertEqual(len(self.archive(s)), 1)
        self.assertEqual(self.entrada_de(s, dup["CLAIM_ID"])["DUPLICATA_DE"], self.af1["CLAIM_ID"])
        self.assertEqual(s["CORRIDA"]["INTAKE_DAS_AFIRMACOES"]["DUPLICADAS"], 1)

    def test_data_futura_em_relacao_a_captura_bloqueia(self):
        af = dict(self.af1, FACT_TIME=dict(self.af1["FACT_TIME"], VALOR="2026-12-03"))
        e = self.entrada_de(self.correr(af), af["CLAIM_ID"])
        self.assertIn("FACT_TIME:FUTURO_EM_RELACAO_A_CAPTURA", e["G0_FALTA"])


class TestConcorrentesBLK1(_Caso):
    """§5-C (BLK-1): mais de 1 tempo ou lugar no trecho e o valor nao e NAO SEI -> o G0 da afirmacao recusa.
    O G0 le a CONTAGEM que o produtor declara; nao le o texto para isto."""
    EUROPA = "La specie e stata rilevata in Europa per la prima volta nel 2004 e in Italia nel 2012, in Emilia Romagna."

    def _europa(self, **mudar):
        # a forma que o produtor 129a025 devolveu para CLAIM ...330ce9da: FACT_TIME 2004 + Italia (facto falso)
        t, ba, la = self.EUROPA, self.EUROPA.index("2004"), self.EUROPA.index("Italia")
        af = {"CLAIM_ID": "AF-SINT-EUROPA", "CLAIM_KIND": {"VALOR": "ALERTA_EVENTO"},
              "EVIDENCE_SPAN": {"INICIO": 0, "FIM": len(t), "TRECHO": t},
              "FACT_TIME": {"VALOR": "2004", "FACT_TIME_BASIS": {"TRECHO": "2004", "INICIO": ba, "FIM": ba + 4}},
              "FACT_TIME_ROLE": {"PAPEL": "ACONTECIMENTO", "ORIGEM": "LITERAL"},
              "FACT_LOCATION": {"VALOR": "Italia", "LOCATION_SOURCE": "TEXT", "INICIO": la},
              "TEMPOS_NO_TRECHO": 2, "LUGARES_NO_TRECHO": 3}
        af.update(mudar)
        return G0A.portao_g0_da_afirmacao(af, {"CAPTURED_AT": "2026-09-20T10:00:00Z"}, t)

    def test_europa_2004_italia_2012_emilia_romagna_cai_no_g0(self):
        passou, falta = self._europa()
        self.assertFalse(passou)
        self.assertIn("TEMPOS_CONCORRENTES:TEMPOS_NO_TRECHO=2", falta)
        self.assertIn("LUGARES_CONCORRENTES:LUGARES_NO_TRECHO=3", falta)

    def test_controle_a_mesma_afirmacao_com_um_tempo_e_um_lugar_passa(self):
        # a recusa acima vem SO da contagem: com 1 e 1 o resto do G0 passa
        self.assertEqual(self._europa(TEMPOS_NO_TRECHO=1, LUGARES_NO_TRECHO=1), (True, []))

    def test_so_os_tempos_concorrentes_ja_recusam(self):
        passou, falta = self._europa(LUGARES_NO_TRECHO=1)
        self.assertEqual((passou, falta), (False, ["TEMPOS_CONCORRENTES:TEMPOS_NO_TRECHO=2"]))

    def test_so_os_lugares_concorrentes_ja_recusam(self):
        passou, falta = self._europa(TEMPOS_NO_TRECHO=1)
        self.assertEqual((passou, falta), (False, ["LUGARES_CONCORRENTES:LUGARES_NO_TRECHO=3"]))

    def test_concorrentes_com_o_valor_ja_em_nao_sei_nao_sao_motivo(self):
        # o produtor fez o que o §5-C manda (valor NAO SEI): nao ha valor de outro facto para recusar
        _, falta = self._europa(TEMPOS_NO_TRECHO=1, FACT_LOCATION={"VALOR": "NAO SEI"})
        self.assertNotIn("LUGARES_CONCORRENTES:LUGARES_NO_TRECHO=3", falta)

    def test_contagem_ausente_ou_nao_inteira_recusa(self):
        for mudar in ({"TEMPOS_NO_TRECHO": None}, {"TEMPOS_NO_TRECHO": "1"}, {"TEMPOS_NO_TRECHO": True},
                      {"TEMPOS_NO_TRECHO": -1}):
            passou, falta = self._europa(LUGARES_NO_TRECHO=1, **mudar)
            self.assertEqual((passou, falta), (False, ["PRODUTOR_SEM_CONTAGEM_DE_CONCORRENTES:TEMPOS_NO_TRECHO"]),
                             mudar)
        af = dict(self.af1)
        del af["LUGARES_NO_TRECHO"]
        e = self.entrada_de(self.correr(af), af["CLAIM_ID"])
        self.assertEqual(e["G0_DA_AFIRMACAO"], "BLOQUEADO_EM_G0")
        self.assertIn("PRODUTOR_SEM_CONTAGEM_DE_CONCORRENTES:LUGARES_NO_TRECHO", e["G0_FALTA"])

    def test_a_contagem_em_bloco_do_produtor_tambem_vale(self):
        self.assertEqual(self._europa(TEMPOS_NO_TRECHO={"VALOR": 1}, LUGARES_NO_TRECHO={"VALOR": 1}), (True, []))
        self.assertFalse(self._europa(TEMPOS_NO_TRECHO={"VALOR": 2}, LUGARES_NO_TRECHO=1)[0])

    def test_contagem_zero_com_lugar_presente_e_incoerente(self):
        # PROD-3: «ferrarese» -> FACT_LOCATION Ferrara, mas o contador dava 0. Zero ao lado de um valor e contradicao.
        passou, falta = self._europa(TEMPOS_NO_TRECHO=1, LUGARES_NO_TRECHO=0)
        self.assertEqual((passou, falta), (False, ["CONTAGEM_INCOERENTE:LUGARES_NO_TRECHO=0_COM_FACT_LOCATION"]))

    def test_contagem_zero_com_tempo_literal_presente_e_incoerente(self):
        passou, falta = self._europa(TEMPOS_NO_TRECHO=0, LUGARES_NO_TRECHO=1)
        self.assertEqual((passou, falta), (False, ["CONTAGEM_INCOERENTE:TEMPOS_NO_TRECHO=0_COM_FACT_TIME"]))

    def test_contagem_zero_com_o_valor_em_nao_sei_e_coerente(self):
        _, falta = self._europa(TEMPOS_NO_TRECHO=1, LUGARES_NO_TRECHO=0, FACT_LOCATION={"VALOR": "NAO SEI"})
        self.assertFalse([m for m in falta if m.startswith("CONTAGEM_INCOERENTE")])

    def test_tempo_do_cabecalho_conta_zero_no_trecho_com_razao(self):
        # CABECALHO_D147 compoe o tempo FORA do trecho (o caso derived:7 ARIF, TEMPOS 0 / LUGARES 1): nao e incoerente
        for origem in ("CABECALHO_D147", "RELATIVA_ANCORADA_D149", "RELATIVO_D63"):
            _, falta = self._europa(TEMPOS_NO_TRECHO=0, LUGARES_NO_TRECHO=1,
                                    FACT_TIME_ROLE={"PAPEL": "ACONTECIMENTO", "ORIGEM": origem})
            self.assertFalse([m for m in falta if m.startswith("CONTAGEM_INCOERENTE")], origem)

    def test_lugar_com_contagem_zero_e_incoerente_qualquer_que_seja_a_origem_do_tempo(self):
        # a excecao da origem e SO do tempo: o lugar emitido conta sempre (PROD-3)
        _, falta = self._europa(TEMPOS_NO_TRECHO=0, LUGARES_NO_TRECHO=0,
                                FACT_TIME_ROLE={"PAPEL": "ACONTECIMENTO", "ORIGEM": "CABECALHO_D147"})
        self.assertIn("CONTAGEM_INCOERENTE:LUGARES_NO_TRECHO=0_COM_FACT_LOCATION", falta)

    def test_pela_corrida_a_afirmacao_com_tempos_concorrentes_nao_chega_ao_archive(self):
        af = dict(self.af1, TEMPOS_NO_TRECHO=2)
        s = self.correr(af)
        e = self.entrada_de(s, af["CLAIM_ID"])
        self.assertEqual(e["G0_DA_AFIRMACAO"], "BLOQUEADO_EM_G0")
        self.assertIn("TEMPOS_CONCORRENTES:TEMPOS_NO_TRECHO=2", e["G0_FALTA"])
        self.assertEqual(self.archive(s), [])


class TestAdmissaoNoPote(_Caso):
    def test_prova_de_afirmacao_nao_e_admitida_pelo_g0_do_item_nem_o_inverso(self):
        s = self.correr(self.af1)
        claim = self.af1["CLAIM_ID"]
        # a afirmacao passa e o item nao: o pote admite a da afirmacao ...
        pote, _ = GI.montar_o_pote(copy.deepcopy(s))
        self.assertTrue(pote["COMPARTIMENTOS"]["archive"]["OBJETOS"])
        # ... e a mesma prova SEM CLAIM_ID (que diria ser do item, bloqueado) e recusada
        s2 = copy.deepcopy(s)
        for o in s2["ITENS_POR_FERRAMENTA"]["archive"]:
            for p in o["PROVA"]:
                p.pop("CLAIM_ID")
        pote2, _ = GI.montar_o_pote(s2)
        self.assertEqual(pote2["COMPARTIMENTOS"]["archive"]["OBJETOS"], [])
        self.assertTrue(any(r.get("MOTIVO") == "ITEM_BLOQUEADO_EM_G0" for r in pote2["RECUSADOS"]))
        # ... e uma afirmacao BLOQUEADA nao passa por o item passar (o inverso)
        s3 = copy.deepcopy(s)
        e = next(x for x in s3["LINEAGE"] if x.get("CLAIM_ID") == claim)
        e.update(G0_DA_AFIRMACAO="BLOQUEADO_EM_G0", G0="BLOQUEADO_EM_G0", G0_DO_ITEM="PASSOU")
        pote3, _ = GI.montar_o_pote(s3)
        self.assertEqual(pote3["COMPARTIMENTOS"]["archive"]["OBJETOS"], [])

    def test_o_motor_confere_a_prova_da_afirmacao_pela_entrada_dela(self):
        s = self.correr(self.af1)
        self.assertEqual(M.conferir_saida(s), [])
        e = next(x for x in s["LINEAGE"] if x.get("CLAIM_ID") == self.af1["CLAIM_ID"])
        e["G0_DA_AFIRMACAO"] = "BLOQUEADO_EM_G0"
        self.assertTrue(any("nao admitida no G0 dela" in v for v in M.conferir_saida(s)))


class TestAntiOverfit(unittest.TestCase):
    PROIBIDOS = ("derived:11", "AF-", "SG-a5d48c8c", "2026-09-07", "Nociglia", "Otranto", "scarto climatico",
                 "TRECHO_DA_AFIRMACAO")
    #: o que JA estava na producao 852ec0f0b antes desta tarefa (comentarios de outros donos), medido a 29/09:
    #: nao e codigo desta tarefa e nao se toca aqui; o teste so garante que nao cresce.
    JA_NA_PRODUCAO = {"2026-09-07": 1, "scarto climatico": 1}
    DESTA_TAREFA = ("motor/g0_da_afirmacao.py", "motor/motor_das_capacidades.py", "pacote/pote_intelligence_casco.py",
                    "pacote/ponte_intelligence_casco.py", "admissao/gatilho_da_inteligencia.py")

    def test_nenhum_id_trecho_ou_data_da_r9_no_codigo_desta_tarefa(self):
        for f in self.DESTA_TAREFA:
            texto = (RAIZ / f).read_text(encoding="utf-8", errors="replace")
            for p in self.PROIBIDOS:
                self.assertNotIn(p, texto, "%s em %s" % (p, f))

    def test_no_codigo_de_producao_so_o_que_ja_la_estava(self):
        for p in self.PROIBIDOS:
            n = sum(f.read_text(encoding="utf-8", errors="replace").count(p)
                    for pasta in ("motor", "pacote", "admissao", "leis") for f in (RAIZ / pasta).rglob("*.py"))
            self.assertEqual(n, self.JA_NA_PRODUCAO.get(p, 0), p)


if __name__ == "__main__":
    unittest.main()
