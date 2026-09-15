#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PROVAS DA SEGUNDA FOTOGRAFIA DO CATÁLOGO ADAMA ITÁLIA

    51 MEDIDO vs 55 INFORMADO. A resposta não era escolher um dos dois.

O handoff registou a hipótese: *«o snapshot do catálogo é de 30/08, a informação
humana é de 15/09; quinze dias chegam para um portfólio mexer»*. Estes testes
guardam o que a medição fez com essa hipótese — e guardam, sobretudo, o que
continua a ser `NÃO SEI`.

    UMA SUITE QUE MEDE COLEÇÃO VAZIA PASSA SEMPRE. Esta recusa-se.

Corre como os outros testes desta casa:  py tests/test_adama_catalogo_drift.py
"""
import io
import json
import os
import sys
import unittest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CASA = os.path.join(RAIZ, "referencia", "adama")
sys.path.insert(0, os.path.join(RAIZ, "fontes"))


def ler(nome):
    with io.open(os.path.join(CASA, nome), encoding="utf-8") as fh:
        return json.load(fh)


MASTER = ler("PRODUCT-MASTER.json")["PRODUCTS"]
PORTFOLIO = ler("PORTFOLIO.json")["RECORDS"]
SNAPS_REG = ler("SNAPSHOTS.json")["RECORDS"]
CAT = ler("CATALOG-SNAPSHOTS.json")
CAT_SNAPS = CAT["RECORDS"]
OBS = ler("PORTFOLIO-OBSERVATIONS.json")["RECORDS"]
DRIFT = ler("PORTFOLIO-DRIFT.json")

ANTES = "CAT_ADAMA_IT_20260830"
AGORA = "CAT_ADAMA_IT_20260915"


class ANaoVacuidade(unittest.TestCase):
    """Antes de medir seja o que for, provar que há o que medir."""

    def test_nenhuma_colecao_medida_esta_vazia(self):
        for nome, col in (("PRODUCT-MASTER", MASTER), ("PORTFOLIO", PORTFOLIO),
                          ("CATALOG-SNAPSHOTS", CAT_SNAPS),
                          ("PORTFOLIO-OBSERVATIONS", OBS)):
            self.assertTrue(len(col) > 0, "%s esta vazio — o teste mediria nada" % nome)
        self.assertEqual(51, len(MASTER))
        self.assertEqual(51, len(PORTFOLIO))
        self.assertEqual(102, len(OBS), "2 fotos x 51 produtos")


class OIDNaoSeMexeu(unittest.TestCase):
    """§6 — a foto nova não tem licença para tocar na identidade."""

    def test_nenhum_id_foi_renumerado(self):
        esperados = ["ADAMA-P-%04d" % n for n in range(1, 52)]
        self.assertEqual(esperados,
                         sorted(p["ADAMA_PRODUCT_ID"] for p in MASTER))
        self.assertEqual(0, DRIFT["ADAMA_PRODUCT_IDS_CHANGED"])

    def test_o_selo_de_identidade_continua_a_fechar(self):
        """A testemunha independente: assina ID↔primeira âncora na emissão."""
        import adama_referencia as A
        for p in MASTER:
            esperado = A._selo(p["ADAMA_PRODUCT_ID"], sorted(p["IDENTITY_ANCHORS"])[0])
            self.assertEqual(esperado, p["IDENTITY_SEAL"],
                             "o selo de %s deixou de fechar" % p["ADAMA_PRODUCT_ID"])
        selos = [p["IDENTITY_SEAL"] for p in MASTER]
        self.assertEqual(len(selos), len(set(selos)))

    def test_o_serial_nao_recuou_nem_reciclou(self):
        self.assertEqual(52, ler("PRODUCT-MASTER.json")["NEXT_SERIAL"],
                         "o proximo numero de serie mexeu sem produto novo")

    def test_o_casamento_e_por_ancora_nunca_por_nome(self):
        self.assertIn("IDENTITY_ANCHORS", DRIFT["IDENTITY_MATCH_METHOD"])
        self.assertEqual(0, len(DRIFT["UNMATCHED_PAGES_NOW"]),
                         "pagina observada sem dono viraria palpite de identidade")


class NenhumaFotoViraLixo(unittest.TestCase):
    """§4 · §6 — a foto anterior não se apaga, e a nova não a substitui."""

    def test_as_tres_fotos_regulatorias_continuam_intactas(self):
        ids = {s["SNAPSHOT_ID"] for s in SNAPS_REG}
        self.assertEqual({"PROD_FTS_6_20260824", "PROD_FTS_6_20260831",
                          "PROD_FTS_6_20260907"}, ids,
                         "a foto do catalogo invadiu o registo do Ministero")

    def test_a_foto_anterior_do_catalogo_continua_declarada(self):
        ids = [s["SNAPSHOT_ID"] for s in CAT_SNAPS]
        self.assertIn(ANTES, ids, "a foto de 30/08 desapareceu")
        self.assertIn(AGORA, ids)

    def test_o_artefacto_que_prova_cada_foto_existe_no_disco(self):
        for s in CAT_SNAPS:
            for campo in ("PROVING_ARTIFACT", "PROVING_ARTIFACT_ENUMERATION"):
                art = s.get(campo)
                if not art:
                    continue
                self.assertTrue(os.path.exists(os.path.join(RAIZ, art)),
                                "o artefacto que prova %s desapareceu: %s"
                                % (s["SNAPSHOT_ID"], art))

    def test_ha_exactamente_uma_foto_corrente_do_catalogo(self):
        atuais = [s for s in CAT_SNAPS if s.get("CURRENT")]
        self.assertEqual(1, len(atuais), "mais de uma foto do catalogo diz ser actual")
        self.assertEqual(AGORA, atuais[0]["SNAPSHOT_ID"])
        self.assertEqual(AGORA, CAT["CURRENT_SNAPSHOT"])

    def test_current_nao_e_historical(self):
        """A pergunta «como está hoje?» e «como estava?» não podem dar o mesmo
        objecto. Cada observação está presa à sua foto, e as duas coexistem."""
        for sid in (ANTES, AGORA):
            desta = [o for o in OBS if o["SNAPSHOT_ID"] == sid]
            self.assertEqual(51, len(desta),
                             "a foto %s nao observou os 51 produtos" % sid)
        ids_por_foto = {sid: {o["OBSERVATION_ID"] for o in OBS
                              if o["SNAPSHOT_ID"] == sid}
                        for sid in (ANTES, AGORA)}
        self.assertEqual(set(), ids_por_foto[ANTES] & ids_por_foto[AGORA],
                         "duas fotos partilham OBSERVATION_ID — colapsaram numa so")


class AProvenienciaEstaInteira(unittest.TestCase):
    """§4 — SOURCE_ID · SOURCE_URL · OBSERVED_AT · COLLECTED_AT · SHA256."""

    def test_cada_observacao_diz_de_onde_veio(self):
        for o in OBS:
            p = o["PROVENANCE"]
            self.assertEqual(["IT-ADAMA-CATALOG"], p["SOURCE_IDS"])
            self.assertTrue(p["SOURCE_URL"], "%s sem endereco" % o["OBSERVATION_ID"])
            self.assertTrue(p["SNAPSHOT_ID"])
            self.assertTrue(os.path.exists(os.path.join(RAIZ, p["PROVING_ARTIFACT"])),
                            "%s aponta para artefacto que nao existe"
                            % o["OBSERVATION_ID"])

    def test_a_foto_nova_traz_hash_de_cada_pagina(self):
        agora = [o for o in OBS if o["SNAPSHOT_ID"] == AGORA]
        sem_hash = [o["OBSERVATION_ID"] for o in agora
                    if o["MEMBERSHIP_STATE"].startswith("PRESENT")
                    and not o.get("PAGE_SHA256")]
        self.assertEqual([], sem_hash, "observacao presente sem sha256 da pagina")
        hashes = [o["PAGE_SHA256"] for o in agora if o.get("PAGE_SHA256")]
        self.assertEqual(51, len(hashes))
        self.assertEqual(51, len(set(hashes)),
                         "duas paginas com o mesmo sha256 — captura repetida")
        for h in hashes:
            self.assertEqual(64, len(h))

    def test_observed_at_e_collected_at_sao_campos_distintos(self):
        nova = [s for s in CAT_SNAPS if s["SNAPSHOT_ID"] == AGORA][0]
        self.assertEqual("2026-09-15", nova["OBSERVED_AT"])
        self.assertTrue(nova["COLLECTED_AT"].startswith("2026-09-15T"))
        self.assertNotEqual(nova["OBSERVED_AT"], nova["COLLECTED_AT"])

    def test_o_bruto_nao_se_declara_guardado_quando_nao_esta(self):
        """80 manifestos desta casa já disseram PRESERVED apontando para
        ficheiro que não existia. `data/raw/` é ignorado pelo Git: o que vive
        lá é LOCAL, e diz-se LOCAL."""
        nova = [s for s in CAT_SNAPS if s["SNAPSHOT_ID"] == AGORA][0]
        self.assertEqual("RAW_LOCAL_NOT_VERSIONED", nova["RAW_STATE"])
        self.assertNotIn("PRESERVED", json.dumps(nova))


class OQueMudouEOQueNaoSeSabe(unittest.TestCase):
    """§5 · §8 — o diff, e o tamanho honesto do NÃO SEI."""

    def test_o_diff_e_entre_duas_fotos_do_mesmo_catalogo(self):
        self.assertEqual(ANTES, DRIFT["SNAPSHOT_BEFORE"])
        self.assertEqual(AGORA, DRIFT["SNAPSHOT_NOW"])
        self.assertEqual(16, DRIFT["DAYS_BETWEEN"])

    def test_o_catalogo_nao_mexeu_em_dezasseis_dias(self):
        self.assertEqual(51, DRIFT["COUNT_BEFORE"])
        self.assertEqual(51, DRIFT["COUNT_NOW"])
        self.assertEqual([], DRIFT["ADDED"])
        self.assertEqual([], DRIFT["REMOVED"])
        self.assertEqual([], DRIFT["RENAMED_CANDIDATES"])
        self.assertEqual([], DRIFT["CHANGED_FIELDS"])
        self.assertEqual(51, DRIFT["UNCHANGED"])

    def test_a_hipotese_do_drift_temporal_foi_refutada_e_nao_esquecida(self):
        h = DRIFT["HUMAN_REPORT"]
        self.assertEqual(55, h["HUMAN_REPORTED_CURRENT_PORTFOLIO"])
        self.assertEqual("NOT_PROVEN_BY_ANY_SOURCE_READ", h["STATE"])
        self.assertEqual("REFUTED", h["TEMPORAL_DRIFT_HYPOTHESIS"])

    def test_o_55_nao_foi_escrito_como_verdade_em_lado_nenhum(self):
        """§8 — não forçar. 55 é pista, e pista não vira contagem."""
        self.assertEqual(51, len(PORTFOLIO))
        self.assertEqual(51, len(MASTER))
        for f in ("PORTFOLIO.json", "PRODUCT-MASTER.json"):
            self.assertNotIn("55", json.dumps(ler(f))[:200])

    def test_duas_contagens_independentes_e_a_terceira_declarada_NAO_SEI(self):
        c = DRIFT["POPULATION_CROSSCHECK"]
        self.assertEqual(51, c["METHOD_A_COUNT"])
        self.assertEqual(51, c["METHOD_B_LIVE_COUNT"])
        self.assertEqual("NAO SEI", c["METHOD_C_COUNT"],
                         "a listagem oficial nao foi lida; dizer um numero seria inventar")

    def test_a_rota_que_nao_se_le_fica_nomeada_e_nao_arredondada(self):
        """POSTSCRIPT 80 não é «nada». É autorização ADAMA viva cuja página de
        catálogo o Akamai barra. O NÃO SEI tem nome e número de registo."""
        c = DRIFT["POPULATION_CROSSCHECK"]
        rotas = {r["PATH"]: r for r in c["OUT_OF_SITEMAP_ROUTES"]}
        self.assertTrue(rotas, "a varredura nao declarou nenhuma rota extra")
        ps = [r for r in rotas.values() if "postscript-80" in r["PATH"]]
        self.assertEqual(1, len(ps))
        ps = ps[0]
        self.assertEqual("BLOCKED_BY_BOT_PROTECTION", ps["STATE"])
        regs = ps["REGISTRY_LOOKUP"]["MATCHED_REGISTRATIONS"]
        self.assertEqual(1, len(regs))
        self.assertEqual("017585", regs[0]["REGISTRATION_NUMBER"])
        self.assertTrue(regs[0]["ADMIN_ACTIVE"])
        self.assertEqual("POSTSCRIPT 80", regs[0]["REGISTERED_NAME"])
        self.assertEqual("UNKNOWN", regs[0]["ADAMA_PRODUCT_ID"],
                         "esta autorizacao nao tem produto de catalogo — e esse e "
                         "exactamente o motivo de ela nao entrar na contagem")
        self.assertIn("REGULATORY_PRODUCT != CATALOG_PRODUCT",
                      ps["REGISTRY_LOOKUP"]["WHAT_IT_DOES_NOT_PROVE"],
                      "achar o nome no registo nao pode virar prova de catalogo")
        self.assertGreaterEqual(len(ps["LINKED_FROM"]), 3,
                                "a rota e citada por paginas vivas; isso e o que a "
                                "torna um NAO SEI e nao um nada")

    def test_deteccao_de_robo_declarada_como_limite_nao_como_ausencia(self):
        nova = [s for s in CAT_SNAPS if s["SNAPSHOT_ID"] == AGORA][0]
        self.assertIn("NAO SE CONTORNA", nova["COLLECTION_METHOD"])


class AAusenciaNaoDestroi(unittest.TestCase):
    """§6 — produto fora do catálogo é membership, nunca apagamento."""

    def test_o_vocabulario_de_membership_existe_antes_de_ser_preciso(self):
        estados = {o["MEMBERSHIP_STATE"] for o in OBS}
        self.assertEqual({"PRESENT_IN_CATALOG_SNAPSHOT"}, estados,
                         "hoje ninguem esta ausente; o estado de ausencia continua "
                         "definido no contrato para quando estiver")
        ficheiro = ler("PORTFOLIO-OBSERVATIONS.json")
        vocab = ficheiro["MEMBERSHIP_STATES"]
        self.assertIn("ABSENT_FROM_CATALOG_SNAPSHOT", vocab,
                      "o estado de ausencia so nasceria no dia em que fosse preciso")
        self.assertTrue(ficheiro["VOCABULARY_IS_CLOSED"])
        self.assertEqual(set(vocab), estados | {"ABSENT_FROM_CATALOG_SNAPSHOT"},
                         "ha estado usado fora do vocabulario, ou vocabulario a mais")
        self.assertIn("NAO significa descontinuado",
                      vocab["ABSENT_FROM_CATALOG_SNAPSHOT"])

    def test_produto_ausente_sairia_da_foto_e_nao_do_master(self):
        """Simula a saída: o contrato do diff tem de marcar o Product Master
        como preservado, não como reduzido."""
        import adama_catalogo_snapshot as S
        antes = [{"CANONICAL_URL": S.ancora_de_url(p),
                  "OBSERVED_NAME": None, "CATEGORY_DISPLAY": None, "NODE_ID": None}
                 for p in MASTER]
        agora = antes[:-1]          # um produto deixou de aparecer no catalogo
        d = S.medir_drift(MASTER, PORTFOLIO, antes, agora)
        self.assertEqual(1, len(d["REMOVED"]))
        self.assertEqual("ABSENT_FROM_CATALOG_SNAPSHOT",
                         d["REMOVED"][0]["MEMBERSHIP_STATE"])
        self.assertEqual("PRESERVED_NEVER_DELETED",
                         d["REMOVED"][0]["PRODUCT_MASTER_STATE"])
        self.assertEqual(51, len(MASTER), "a simulacao mexeu no Product Master real")

    def test_rename_so_sai_como_candidato_e_com_ancora_igual(self):
        import adama_catalogo_snapshot as S
        antes = [{"CANONICAL_URL": S.ancora_de_url(p), "OBSERVED_NAME": "NOME VELHO",
                  "CATEGORY_DISPLAY": None, "NODE_ID": None} for p in MASTER]
        agora = [dict(x, OBSERVED_NAME="NOME NOVO") for x in antes]
        d = S.medir_drift(MASTER, PORTFOLIO, antes, agora)
        self.assertEqual(51, len(d["RENAMED_CANDIDATES"]))
        for r in d["RENAMED_CANDIDATES"]:
            self.assertEqual("RENAMED_CANDIDATE", r["STATE"])
            self.assertIn("IDENTITY_ANCHOR", r["IDENTITY_EVIDENCE"])
        self.assertEqual([], d["ADDED"])
        self.assertEqual([], d["REMOVED"],
                         "mudar o nome fez o produto parecer que saiu e voltou")


class ACasaContinuaDonaDoDado(unittest.TestCase):
    """§7 · §9 — não se construiu motor, e o Portal não foi tocado."""

    def test_a_fonte_do_catalogo_fala_a_lingua_do_atlas(self):
        for s in CAT_SNAPS:
            self.assertEqual("IT-ADAMA-CATALOG", s["SOURCE_ID"])
        mapa = ler("SOURCE-ID-MAP.json")["RECORDS"]
        canonicos = {m["CANONICAL_SOURCE_ID"] for m in mapa}
        self.assertIn("IT-ADAMA-CATALOG", canonicos)

    def test_a_foto_do_catalogo_nao_se_funde_com_a_do_ministero(self):
        """CATALOG_PRODUCT != REGULATORY_PRODUCT. Fundir as duas faria o
        portfolio parecer observado num dia em que ninguém olhou para ele."""
        reg = {s["SNAPSHOT_ID"] for s in SNAPS_REG}
        cat = {s["SNAPSHOT_ID"] for s in CAT_SNAPS}
        self.assertEqual(set(), reg & cat)
        anterior = [s for s in CAT_SNAPS if s["SNAPSHOT_ID"] == ANTES][0]
        self.assertEqual("PROD_FTS_6_20260831",
                         anterior["REGULATORY_SNAPSHOT_ID_INHERITED"],
                         "o valor herdado errado foi apagado em vez de declarado")

    def test_nenhum_motor_de_mudanca_foi_construido(self):
        proibidos = ("IMPACT_GRAPH", "REGULATORY_RADAR", "LABEL_INTELLIGENCE",
                     "CHANGE_ENGINE", "EVENT_BUS")
        texto = json.dumps(DRIFT).upper()
        for p in proibidos:
            self.assertNotIn(p.replace("_", ""), texto.replace("_", ""),
                             "o diff comecou a virar motor de eventos: %s" % p)

    def test_o_portal_nao_foi_corrigido_por_esta_missao(self):
        """A verdade conserta-se na Reference, nunca na camada que apresenta."""
        alvo = os.path.join(RAIZ, "referencia", "adama")
        escritos = {"CATALOG-SNAPSHOTS.json", "PORTFOLIO-OBSERVATIONS.json",
                    "PORTFOLIO-DRIFT.json"}
        for nome in escritos:
            self.assertTrue(os.path.exists(os.path.join(alvo, nome)),
                            "%s devia ter nascido em referencia/adama/" % nome)


if __name__ == "__main__":
    unittest.main(verbosity=2)
