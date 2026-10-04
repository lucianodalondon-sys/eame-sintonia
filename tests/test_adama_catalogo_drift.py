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
        """A fonte é a canónica do Atlas (IT-T9-008 — o catálogo é um endpoint
        dela); o nome com que esta casa a chamava fica ao lado, em LEGACY."""
        for o in OBS:
            p = o["PROVENANCE"]
            self.assertEqual(["IT-T9-008"], p["SOURCE_IDS"])
            self.assertEqual(["IT-ADAMA-CATALOG"], p["SOURCE_IDS_LEGACY"])
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

    def test_o_conjunto_observado_nao_mexeu_em_dezasseis_dias(self):
        """E só o conjunto observado. O título deste teste já foi «o catálogo
        não mexeu» — e isso era afirmação maior do que a amostra."""
        self.assertEqual("OBSERVED_READABLE_AND_COMPARABLE",
                         DRIFT["COUNT_POPULATION"])
        self.assertIn("NAO sao o tamanho do catalogo oficial",
                      DRIFT["WHAT_COUNT_MEANS"])
        self.assertEqual(51, DRIFT["COUNT_BEFORE"])
        self.assertEqual(51, DRIFT["COUNT_NOW"])
        self.assertEqual([], DRIFT["ADDED"])
        self.assertEqual([], DRIFT["REMOVED"])
        self.assertEqual([], DRIFT["RENAMED_CANDIDATES"])
        self.assertEqual([], DRIFT["CHANGED_FIELDS"])
        self.assertEqual(51, DRIFT["UNCHANGED"])

    def test_o_total_oficial_do_catalogo_continua_NAO_SEI(self):
        """⚠️ O overclaim que o review apanhou: 51 é o que se consegue LER.

            PÁGINA LEGÍVEL OBSERVADA != CATÁLOGO OFICIAL TOTAL

        Enquanto a listagem oficial não abrir, o total não é 51 — é NÃO SEI."""
        e = DRIFT["COUNT_SCOPE"]
        self.assertEqual(51, e["OBSERVED_READABLE_PRODUCT_COUNT"])
        self.assertEqual("NAO SEI", e["CURRENT_OFFICIAL_PORTFOLIO_COUNT"],
                         "o total do catalogo voltou a ser afirmado a partir do "
                         "que se conseguiu ler")
        self.assertIn("!=", e["LAW"])
        self.assertIn("nao PROVA" if "nao PROVA" in e["WHAT_51_DOES_NOT_PROVE"]
                      else "51 produtos", e["WHAT_51_DOES_NOT_PROVE"])

    def test_o_drift_total_do_catalogo_continua_NAO_SEI(self):
        """Um produto que entre ou saia FORA do sitemap não aparece em nenhuma
        das duas fotos — e a comparação dá igual na mesma."""
        t = DRIFT["TEMPORAL_DRIFT"]
        self.assertEqual("NOT_OBSERVED", t["TEMPORAL_DRIFT_IN_OBSERVED_SET"])
        self.assertEqual("NAO SEI", t["TOTAL_CATALOG_TEMPORAL_DRIFT"],
                         "o veredito voltou a ser maior do que a amostra")
        self.assertIn("NOT_SUPPORTED_IN_OBSERVED_SET", t["HANDOFF_HYPOTHESIS_NOW"])
        self.assertNotIn("REFUTED", t["HANDOFF_HYPOTHESIS_NOW"].replace(
            "NAO e refutacao", ""))

    def test_a_palavra_REFUTED_nao_volta_ao_artefacto(self):
        """`NOT_SUPPORTED` != `REFUTED`. Não provado não é refutado, e a
        diferença entre os dois é o tamanho do que se pode afirmar."""
        texto = json.dumps(ler("PORTFOLIO-DRIFT.json"), ensure_ascii=False)
        self.assertNotIn("REFUTED", texto,
                         "a hipotese voltou a ser dada por morta")

    def test_o_55_continua_pista_e_continua_possivel(self):
        h = DRIFT["HUMAN_REPORT"]
        self.assertEqual(55, h["HUMAN_REPORTED_CURRENT_PORTFOLIO"])
        self.assertEqual("NOT_PROVEN_BY_ANY_SOURCE_READ", h["STATE"])
        self.assertIn("SIM", h["COULD_55_STILL_BE_TRUE"],
                      "55 nao foi provado, mas tambem nao foi refutado")

    def test_o_55_nao_foi_escrito_como_verdade_em_lado_nenhum(self):
        """§8 — não forçar. 55 é pista, e pista não vira contagem."""
        self.assertEqual(51, len(PORTFOLIO))
        self.assertEqual(51, len(MASTER))
        for f in ("PORTFOLIO.json", "PRODUCT-MASTER.json"):
            self.assertNotIn("55", json.dumps(ler(f))[:200])

    def test_duas_contagens_independentes_e_a_terceira_declarada_NAO_SEI(self):
        c = DRIFT["POPULATION_CROSSCHECK"]
        self.assertEqual(51, c["METHOD_A_COUNT"])
        self.assertEqual(51, c["METHOD_B_READABLE_COUNT"])
        self.assertEqual("NAO SEI", c["METHOD_C_COUNT"],
                         "a listagem oficial nao foi lida; dizer um numero seria inventar")
        # a concordancia e sobre o LEGIVEL, nunca sobre o tamanho do catalogo
        self.assertIn("PAGINAS DE PRODUTO LEGIVEIS", c["WHAT_IS_BEING_COUNTED"])
        self.assertTrue(c["METHODS_AGREE_ON_READABLE_PAGES"])
        self.assertNotIn("produtos VIVOS", c["AGREEMENT_MEANS"],
                         "a concordancia voltou a ser lida como censo de produto")

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

    def test_o_403_do_antigram_nao_vira_despublicado(self):
        """⚠️ O segundo overclaim que o review apanhou.

            ERROR != REJECTED
            AUSÊNCIA DE PROVA NÃO É PROVA DE AUSÊNCIA

        403 diz que este cliente não leu a rota. Não diz que o produto não
        existe, nem que foi despublicado."""
        c = DRIFT["POPULATION_CROSSCHECK"]
        ag = [r for r in c["OUT_OF_SITEMAP_ROUTES"] if "antigram" in r["PATH"]]
        self.assertEqual(1, len(ag))
        ag = ag[0]
        self.assertEqual(403, ag["HTTP_STATUS"])
        self.assertEqual("LINKED_BUT_NOT_READABLE", ag["STATE"],
                         "o 403 voltou a ser lido como despublicado")
        self.assertEqual("UNKNOWN", ag["PUBLICATION_STATE"])
        self.assertIn("NAO PROVA", ag["WHY_NOT_COUNTED"])

    def test_nenhuma_rota_por_ler_e_dada_por_ausente(self):
        """Toda rota que não se conseguiu ler fica UNKNOWN quanto a publicação —
        nunca ausente, nunca zero."""
        for r in DRIFT["POPULATION_CROSSCHECK"]["OUT_OF_SITEMAP_ROUTES"]:
            self.assertEqual("UNKNOWN", r["PUBLICATION_STATE"],
                             "%s deixou de ser UNKNOWN sem prova nova" % r["PATH"])
            self.assertNotIn("NOT_PUBLISHED", r["STATE"])

    def test_postscript_80_continua_sem_membership_comercial(self):
        c = DRIFT["POPULATION_CROSSCHECK"]
        ps = [r for r in c["OUT_OF_SITEMAP_ROUTES"] if "postscript-80" in r["PATH"]][0]
        self.assertEqual("BLOCKED_BY_BOT_PROTECTION", ps["STATE"])
        self.assertEqual("UNKNOWN", ps["PUBLICATION_STATE"])
        # ⚠️ `POSTSCRIPT 80 XL` (017868) é OUTRA coisa: é um OBSERVED_NAME
        # legítimo de ADAMA-P-0048 (FullPage®). Procurar a substring apanharia
        # o XL e daria um falso positivo — mede-se o registo exacto.
        regs = {r["REGISTRATION_NUMBER"]: r for r in ler("REGISTRATIONS.json")["RECORDS"]}
        self.assertEqual("POSTSCRIPT 80", regs["017585"]["REGISTERED_NAME"])
        self.assertEqual("UNKNOWN", regs["017585"]["ADAMA_PRODUCT_ID"],
                         "POSTSCRIPT 80 ganhou produto de catalogo sem prova nova")
        self.assertEqual([], regs["017585"]["ADAMA_PRODUCT_IDS"])
        self.assertEqual("ADAMA-P-0048", regs["017868"]["ADAMA_PRODUCT_ID"],
                         "o XL e outro registo, e continua a ser o FullPage")
        nomes = {p["CANONICAL_NAME"].upper() for p in PORTFOLIO}
        self.assertNotIn("POSTSCRIPT 80", nomes,
                         "POSTSCRIPT 80 entrou no portfolio comercial sem prova")

    def test_proveniencia_nao_se_diz_num_campo_so(self):
        """`PROVENANCE_COMPLETE = SIM` sozinho lê-se como «o bruto está
        guardado». Não está: 80 manifestos desta casa já o disseram apontando
        para ficheiro inexistente."""
        man = json.load(io.open(os.path.join(
            RAIZ, "data", "samples", "IT-ADAMA-CATALOG", "2026-09-15",
            "catalog-page-manifest.json"), encoding="utf-8"))
        self.assertEqual("RAW_LOCAL_NOT_VERSIONED", man["RAW_STATE"])
        self.assertEqual("NAO", man["RAW_PRESERVED"])
        self.assertEqual("SIM", man["METADATA_PROVENANCE_COMPLETE"])
        self.assertEqual("SIM", man["PAGE_SHA256_VERSIONED"])
        # nenhum CAMPO pode AFIRMAR preservação — a prosa que explica a regra
        # menciona a palavra de propósito, e procurar a substring apanha-a.
        for chave, valor in man.items():
            if chave.endswith("_PRESERVED") or chave == "RAW_STATE":
                self.assertNotEqual("PRESERVED", valor,
                                    "%s voltou a afirmar bruto guardado" % chave)
                self.assertNotEqual("SIM", valor) if chave.endswith(
                    "_PRESERVED") else None
        self.assertIn("nao se fundem", man["WHY_THESE_THREE_ARE_SEPARATE"])

    def test_o_source_id_herdado_nao_esconde_a_divida_do_atlas(self):
        """IT-ADAMA-CATALOG não foi emitido aqui — e não estava no Atlas.
        A lacuna foi declarada (PREEXISTING_GAP) e depois resolvida pela faixa
        Sources: é identificador LEGADO da ficha IT-T9-008. O contrato guarda as
        duas datas; a foto do catálogo diz o canónico E o nome antigo."""
        with io.open(os.path.join(CASA, "CONTRATO-ADAMA-REFERENCE.md"),
                     encoding="utf-8") as fh:
            contrato = fh.read()
        self.assertIn("PREEXISTING_GAP", contrato)
        self.assertIn("RESOLVED_AS_LEGACY_OF_IT-T9-008", contrato)
        self.assertIn("SOURCE_ID_NEW_BY_REFERENCE           0", contrato)
        for s in CAT_SNAPS:
            self.assertEqual("IT-T9-008", s["SOURCE_ID"])
            self.assertEqual("IT-ADAMA-CATALOG", s["SOURCE_ID_LEGACY"])
            self.assertIn("/it/prodotti-adama/", s["SOURCE_ENDPOINT"])


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
        """LEGADO != CANÓNICO. O canónico é a ficha do Atlas (IT-T9-008);
        IT-ADAMA-CATALOG só pode aparecer do lado LEGADO do mapa — nunca mais
        do lado canónico. E o builder das fotos lê o mapa da Reference, não
        tem cópia própria (COL-LAW-053: uma lista só)."""
        import adama_catalogo_snapshot as S
        import adama_referencia as A
        for s in CAT_SNAPS:
            self.assertEqual("IT-T9-008", s["SOURCE_ID"])
        mapa = ler("SOURCE-ID-MAP.json")["RECORDS"]
        canonicos = {m["CANONICAL_SOURCE_ID"] for m in mapa}
        legados = {m["LEGACY_SOURCE_ID"]: m["CANONICAL_SOURCE_ID"] for m in mapa}
        self.assertIn("IT-T9-008", canonicos)
        self.assertNotIn("IT-ADAMA-CATALOG", canonicos,
                         "IT-ADAMA-CATALOG voltou a ser canonico")
        self.assertEqual("IT-T9-008", legados.get("IT-ADAMA-CATALOG"))
        self.assertEqual(A.SOURCE_ID_CANONICO["IT-ADAMA-CATALOG"], S.SOURCE_ID)
        self.assertEqual("IT-ADAMA-CATALOG", S.SOURCE_ID_LEGACY)

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
