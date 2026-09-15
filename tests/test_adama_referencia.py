#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PROVAS DA CASA CANÔNICA DA REFERÊNCIA ADAMA

    UMA REFERÊNCIA QUE O CONSUMIDOR TEM DE ESCOLHER NÃO É UMA REFERÊNCIA:
    É UM PAR DE OPINIÕES.

A casa tinha duas referências da ADAMA construídas no mesmo dia, que não se
conheciam, e quem as consumia escolhia sozinho. Estes testes existem para que a
união não desfaça nada do que cada uma sabia, e para que a identidade que nasceu
aqui não se mexa nunca mais.

Corre como os outros testes desta casa:  py tests/test_adama_referencia.py
"""
import io
import json
import os
import sys
import unittest
from collections import Counter, defaultdict

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CASA = os.path.join(RAIZ, "referencia", "adama")
sys.path.insert(0, os.path.join(RAIZ, "fontes"))

UNKNOWN = "UNKNOWN"


def ler(nome):
    with io.open(os.path.join(CASA, nome), encoding="utf-8") as fh:
        return json.load(fh)


def registos(nome):
    return ler(nome)["RECORDS"]


MASTER = ler("PRODUCT-MASTER.json")["PRODUCTS"]
PORTFOLIO = registos("PORTFOLIO.json")
REGISTOS = registos("REGISTRATIONS.json")
DOCS = registos("LABEL-DOCUMENTS.json")
USOS = registos("AUTHORIZED-USES.json")
DOSES = registos("DOSES.json")
SNAPS = registos("SNAPSHOTS.json")
MAPA_FONTE = registos("SOURCE-ID-MAP.json")


class AIdentidadeNaoSeMexe(unittest.TestCase):
    """A · B · C — o RG do produto é do produto, e não da corrida que o leu."""

    def test_A_regenerar_nao_muda_nenhum_adama_product_id(self):
        """Regenerar é a operação mais comum que existe. Se ela mexer no ID,
        tudo o que apontou para o ID de ontem passa a apontar para outra coisa,
        e ninguém é avisado."""
        import adama_referencia as A
        antes = {p["ADAMA_PRODUCT_ID"]: p["CANONICAL_NAME"] for p in MASTER}
        depois = {p["ADAMA_PRODUCT_ID"]: p["CANONICAL_NAME"]
                  for p in A.montar(escrever=False)["PRODUCT-MASTER.json"]["PRODUCTS"]}
        self.assertEqual(antes, depois,
                         "regenerar mudou a identidade de algum produto")

    def test_A2_o_selo_prende_o_id_a_ancora(self):
        """⚠️ ESTE TESTE NASCEU DE UM ATAQUE QUE SOBREVIVEU.

        O red team rodou os IDs entre os produtos e a prova de cima passou —
        porque ela regenera A PARTIR DO PRÓPRIO FICHEIRO, portanto lê a rotação
        e reproduz. O selo é a testemunha independente: assina o par
        ID↔primeira âncora na emissão, e trocar um sem o outro deixa de fechar.
        """
        import adama_referencia as A
        for p in MASTER:
            self.assertTrue(p.get("IDENTITY_SEAL"),
                            "%s sem selo de identidade" % p["ADAMA_PRODUCT_ID"])
            esperado = A._selo(p["ADAMA_PRODUCT_ID"], sorted(p["IDENTITY_ANCHORS"])[0])
            self.assertEqual(esperado, p["IDENTITY_SEAL"],
                             "o selo de %s nao fecha com a ancora — o ID mudou de dono"
                             % p["ADAMA_PRODUCT_ID"])
        selos = [p["IDENTITY_SEAL"] for p in MASTER]
        self.assertEqual(len(selos), len(set(selos)), "dois produtos com o mesmo selo")

    def test_B_produto_antigo_nao_e_renumerado_por_produto_novo(self):
        """O ataque real: chega um produto novo, o construtor reordena, e os
        antigos andam uma casa. Aqui simula-se o registo com um produto a
        menos — os que sobram TÊM de manter o número."""
        import adama_referencia as A
        guardado = list(A.carregar_master.__doc__ or "")  # noqa: F841
        original = A.carregar_master
        recorte = {"DATASET": "ADAMA-PRODUCT-MASTER",
                   "PRODUCTS": [dict(p) for p in MASTER[:-1]],
                   "NEXT_SERIAL": max(int(p["ADAMA_PRODUCT_ID"].rsplit("-", 1)[1])
                                      for p in MASTER) + 1}
        A.carregar_master = lambda: recorte
        try:
            novo = A.montar(escrever=False)["PRODUCT-MASTER.json"]["PRODUCTS"]
        finally:
            A.carregar_master = original
        por_ancora = {tuple(sorted(p["IDENTITY_ANCHORS"])): p["ADAMA_PRODUCT_ID"]
                      for p in novo}
        for p in MASTER[:-1]:
            k = tuple(sorted(p["IDENTITY_ANCHORS"]))
            self.assertEqual(p["ADAMA_PRODUCT_ID"], por_ancora.get(k),
                             "%s foi renumerado" % p["ADAMA_PRODUCT_ID"])

    def test_C_nome_diferente_nao_cria_produto_novo_sozinho(self):
        """`APYZAR WG` e `APYZA® WG` são o mesmo produto. Se a grafia corrompida
        criasse a sua própria entrada, a casa passaria a ter um produto
        fantasma — e ele pareceria real."""
        corrompidos = [n for p in MASTER for n in p["OBSERVED_NAMES"]
                       if n["NAME_STATE"] == "SIMBOLO_REGISTADO_LIDO_COMO_LETRA_R"]
        self.assertTrue(corrompidos, "nenhuma grafia corrompida foi mapeada — "
                                     "ou o defeito sumiu, ou o teste deixou de medir")
        canon = {p["CANONICAL_NAME"] for p in MASTER}
        for n in corrompidos:
            self.assertNotIn(n["OBSERVED_NAME"], canon,
                             "%s virou produto proprio" % n["OBSERVED_NAME"])
            self.assertIn(n["MAPS_TO_CANONICAL"], canon)

    def test_D_mesmo_nome_nao_funde_produtos_distintos(self):
        """Uma chave generosa demais é pior do que o defeito que cura. Dois
        produtos de catálogo partilham a autorização `017995` e continuam
        sendo dois."""
        ids = [p["ADAMA_PRODUCT_ID"] for p in MASTER]
        self.assertEqual(len(ids), len(set(ids)), "ADAMA_PRODUCT_ID duplicado")
        self.assertEqual(len(MASTER), 51,
                         "o catalogo tem 51 produtos; ficaram %d" % len(MASTER))
        partilham = [r for r in REGISTOS if len(r["ADAMA_PRODUCT_IDS"]) > 1]
        self.assertTrue(partilham, "017995 partilhava dois produtos e deixou de partilhar")
        for r in partilham:
            self.assertEqual(r["ADAMA_PRODUCT_ID"], "MULTIPLE",
                             "registo partilhado tem de dizer MULTIPLE, nao escolher um")

    def test_E_numero_de_registo_nunca_e_usado_como_product_id(self):
        """`REGISTRATION_NUMBER` é o `SOURCE_NATIVE_ID` da COL-LAW-206. Usá-lo
        como identidade nossa faria a identidade mudar quando o Ministero
        mudasse a dele."""
        for p in MASTER:
            pid = p["ADAMA_PRODUCT_ID"]
            self.assertTrue(pid.startswith("ADAMA-P-"), pid)
            self.assertFalse(any(ch.isdigit() and pid.endswith(r["REGISTRATION_NUMBER"])
                                 for r in REGISTOS for ch in [pid[-1]]),
                             "%s termina num numero de registo" % pid)
        for p in PORTFOLIO:
            if p["REGISTRATION_NUMBER"] != UNKNOWN:
                self.assertNotIn(p["REGISTRATION_NUMBER"], p["ADAMA_PRODUCT_ID"])

    def test_pais_nao_esta_dentro_da_identidade(self):
        """`IT-PRODUCT-0045` parecia identidade e era o numero da linha do
        registo italiano. Levar isso para Espanha obrigaria a renumerar tudo."""
        for p in MASTER:
            self.assertNotIn("IT", p["ADAMA_PRODUCT_ID"].replace("ADAMA-P-", ""))
            self.assertEqual(["IT"], p["COUNTRY_SCOPE"])


class NadaSePerdeuNaUniao(unittest.TestCase):
    """F a L — a união somou. Cada número aqui é um que já existia antes."""

    def test_F_os_tres_snapshots_continuam_acessiveis(self):
        ids = {s["SNAPSHOT_ID"] for s in SNAPS}
        self.assertEqual({"PROD_FTS_6_20260824", "PROD_FTS_6_20260831",
                          "PROD_FTS_6_20260907"}, ids)
        for s in SNAPS:
            self.assertTrue(os.path.exists(os.path.join(RAIZ, s["PROVING_ARTIFACT"])),
                            "o artefacto que prova %s desapareceu" % s["SNAPSHOT_ID"])

    def test_G_o_snapshot_corrente_e_um_so(self):
        atuais = [s for s in SNAPS if s.get("CURRENT")]
        self.assertEqual(1, len(atuais), "mais de uma foto diz ser a actual")
        self.assertEqual("PROD_FTS_6_20260831", atuais[0]["SNAPSHOT_ID"])

    def test_H_os_2030_usos_continuam_presentes(self):
        self.assertEqual(2030, len(USOS))
        # e o alvo escrito no papel não foi trocado pelo alvo mapeado
        escritos = sum(1 for u in USOS if u["TARGET_AS_WRITTEN"] != "NAO SEI")
        self.assertEqual(2030, escritos,
                         "o alvo como o rotulo escreveu perdeu-se em %d casos"
                         % (2030 - escritos))

    def test_I_a_ligacao_uso_registo_continua_sem_orfaos(self):
        """102 de 102, zero órfãos. Era a única ligação sem furos antes da
        união, e tem de continuar a ser."""
        nums = {r["REGISTRATION_NUMBER"] for r in REGISTOS}
        dos_usos = {u["REGISTRATION_NUMBER"] for u in USOS}
        self.assertEqual(102, len(dos_usos))
        self.assertEqual(set(), dos_usos - nums, "uso autorizado sem registo")

    def test_J_nenhum_dos_51_produtos_desapareceu(self):
        self.assertEqual(51, len(PORTFOLIO))
        self.assertEqual({p["ADAMA_PRODUCT_ID"] for p in MASTER},
                         {p["ADAMA_PRODUCT_ID"] for p in PORTFOLIO})
        ligados = [p for p in PORTFOLIO if p["REGISTRATION_NUMBER"] != UNKNOWN]
        self.assertEqual(49, len(ligados),
                         "a ligacao portfolio->registo era 49/51 e ficou %d/51"
                         % len(ligados))

    def test_K_as_560_autorizacoes_sem_catalogo_continuam(self):
        """Elas não são lixo: são o registo italiano a dizer que a ADAMA tem
        muito mais autorização do que o catálogo mostra."""
        self.assertEqual(602, len(REGISTOS))
        sem = [r for r in REGISTOS if r["ADAMA_PRODUCT_ID"] == UNKNOWN]
        self.assertEqual(560, len(sem))
        titulares = {r["HOLDER"] for r in REGISTOS if r["HOLDER"] != "NAO SEI"}
        self.assertGreaterEqual(len(titulares), 5,
                                "as cinco entidades legais ADAMA foram fundidas")

    def test_L_os_141_documentos_mantem_sha256_e_proveniencia(self):
        self.assertEqual(141, len(DOCS))
        for d in DOCS:
            self.assertTrue(d["SHA256"], "documento sem sha256: %s" % d["DOCUMENT_ID"])
            self.assertTrue(d["CAPTURED_AT"])
            self.assertTrue(d["PROVENANCE"]["PROVING_ARTIFACT"])
        self.assertEqual(51, sum(1 for d in DOCS if d["DOCUMENT_TYPE"] == "ETICHETTA"))


class OQueEraArmadilhaDeixouDeSer(unittest.TestCase):
    """M · N · O — três defeitos medidos, e a prova de que saíram."""

    def test_M_data_de_observacao_nao_e_data_de_vencimento(self):
        """No V2.1 os dois eram o MESMO valor em 163 de 163, com vencimentos
        até 2040. Quem lesse «data de referência» concluía que o dado estava
        fresco por catorze anos."""
        iguais = [r for r in REGISTOS
                  if r["OBSERVED_AT"] == r["EXPIRY_DATE"] != "NAO SEI"]
        self.assertEqual([], iguais[:5],
                         "%d registos voltaram a ter observacao == vencimento"
                         % len(iguais))
        for r in REGISTOS:
            self.assertEqual("2026-08-31", r["OBSERVED_AT"],
                             "a data de observacao tem de vir do snapshot")
        futuro = [r for r in REGISTOS if r["EXPIRY_DATE"] > "2030"]
        self.assertTrue(futuro, "nenhum vencimento distante — o campo perdeu o valor antigo")

    def test_N_o_source_id_fala_a_lingua_do_atlas(self):
        """`SRC_FITOSANITARI_SALUTE_GOV_IT` e `IT-T4-001` eram a mesma fonte com
        dois nomes. O antigo não se apaga: fica ligado."""
        legado = {m["LEGACY_SOURCE_ID"] for m in MAPA_FONTE}
        self.assertIn("SRC_FITOSANITARI_SALUTE_GOV_IT", legado)
        canon = set()
        for colecao in (PORTFOLIO, REGISTOS, USOS, DOCS):
            for r in colecao:
                canon |= set(r["PROVENANCE"]["SOURCE_IDS"])
        self.assertTrue(canon, "nenhuma linha declara fonte")
        for s in canon:
            self.assertFalse(s.startswith("SRC_"),
                             "%s e vocabulario legado a ser usado como canonico" % s)
        atlas = os.path.join(RAIZ, "docs", "fontes", "ATLAS-DE-FONTES-EAME.md")
        with io.open(atlas, encoding="utf-8") as fh:
            texto = fh.read()
        self.assertIn("IT-T4-001", texto,
                      "o SOURCE_ID canonico nao existe no Atlas")

    def test_O_a_identidade_nao_precisa_do_portal_para_ficar_certa(self):
        """Os quinze que `italia-portale/audit/product-identity.mjs` teve de
        reparar têm de chegar ao registo por esta casa, sem passar pelo site."""
        import adama_referencia as A
        QUINZE = ["Avastel", "Diode", "Folpan® Energy", "Highcard", "Lamdex® Extra",
                  "Maganic", "NICOGAN V.O.", "Schermo® 0.5 G", "Sonavio", "Stavento",
                  "TAIFUN MK CL PFNPE", "APYZA® WG", "COSAYR® 200 SC",
                  "GOLTIX® TOP", "NIMROD® 250 EW"]
        por_chave = {A.chave(p["CANONICAL_NAME"]): p for p in PORTFOLIO}
        perdidos = []
        for nome in QUINZE:
            p = por_chave.get(A.chave(nome))
            if p is None or p["REGISTRATION_NUMBER"] == UNKNOWN:
                perdidos.append(nome)
        self.assertEqual([], perdidos,
                         "sem o Portal, estes nao encontram o registo: %s" % perdidos)

    def test_a_dose_sem_prova_nao_entra_como_verdade(self):
        """142 dos 163 rótulos não deram tabela. Eles ficam na lista, com o
        estado — `PARSER_FAILURE != REGULATORY_ABSENCE`."""
        self.assertEqual(163, len(DOSES))
        com = [d for d in DOSES if d["ROW_COUNT"]]
        self.assertEqual(21, len(com))
        self.assertEqual(839, sum(d["ROW_COUNT"] for d in DOSES))
        for d in DOSES:
            self.assertTrue(d["PARSE_STATE"])
            if not d["ROW_COUNT"]:
                self.assertNotEqual("USE_TABLE_READ", d["PARSE_STATE"])
        for d in com:
            for linha in d["ROWS"]:
                self.assertTrue(linha.get("SOURCE_QUOTE"),
                                "dose sem citacao do papel")

    def test_o_consumidor_nao_escolhe_entre_deep_e_v21(self):
        """O contrato tem de nomear UM ficheiro por conceito."""
        with io.open(os.path.join(CASA, "CONTRATO-ADAMA-REFERENCE.md"),
                     encoding="utf-8") as fh:
            contrato = fh.read()
        for conceito in ("PRODUCT MASTER", "PORTFOLIO", "REGISTRATIONS",
                         "LABEL DOCUMENTS", "AUTHORIZED USES", "ACTIVE INGREDIENTS"):
            self.assertIn(conceito, contrato, "o contrato nao nomeia %s" % conceito)
        for f in ("PRODUCT-MASTER.json", "PORTFOLIO.json", "REGISTRATIONS.json",
                  "LABEL-DOCUMENTS.json", "AUTHORIZED-USES.json",
                  "ACTIVE-INGREDIENTS.json", "DOSES.json", "SNAPSHOTS.json"):
            self.assertTrue(os.path.isfile(os.path.join(CASA, f)), f)

    def test_nao_vacuidade(self):
        """Uma suite que mede coleções vazias passa sempre. Esta recusa-se."""
        for nome, col in (("MASTER", MASTER), ("PORTFOLIO", PORTFOLIO),
                          ("REGISTOS", REGISTOS), ("DOCS", DOCS),
                          ("USOS", USOS), ("DOSES", DOSES), ("SNAPS", SNAPS)):
            self.assertTrue(col, "%s esta vazio — o teste nao mediu nada" % nome)


if __name__ == "__main__":
    unittest.main(verbosity=2)
