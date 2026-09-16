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
        # 51 e o CONJUNTO OBSERVADO (paginas legiveis), nao o total oficial —
        # esse e NAO SEI. Ver test_o_51_e_o_que_se_leu_nao_o_que_o_catalogo_tem.
        self.assertEqual(len(MASTER), 51,
                         "o MASTER preserva os 51 produtos observados no catalogo; "
                         "ficaram %d" % len(MASTER))
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


def ler_raiz(*partes):
    with io.open(os.path.join(RAIZ, *partes), encoding="utf-8") as fh:
        return json.load(fh)


def _source_ids_do_atlas():
    """Os SOURCE_ID que TÊM ficha no Atlas — a única lista que pode ser canónica."""
    atlas = os.path.join(RAIZ, "docs", "fontes", "ATLAS-DE-FONTES-EAME.md")
    with io.open(atlas, encoding="utf-8") as fh:
        linhas = fh.read().splitlines()
    ids = set()
    for l in linhas:
        if l.startswith("SOURCE_ID:"):
            ids.add(l.split(":", 1)[1].strip())
    return ids


class LegadoNaoECanonico(unittest.TestCase):
    """P a U — a fonte do catálogo é a ficha do Atlas; o nome antigo não morre.

    Decidido em 2026-09-16 (know-how §127; ficha IT-T9-008): o catálogo
    comercial é outro ENDPOINT da fonte IT-T9-008, não uma segunda fonte.
    `IT-ADAMA-CATALOG` passa a identificador LEGADO. Estas provas impedem as
    duas regressões simétricas: o legado voltar a canónico, e o legado sumir.
    """

    LEGADO = "IT-ADAMA-CATALOG"
    CANONICO = "IT-T9-008"

    def test_P_nenhum_canonico_do_mapa_e_IT_ADAMA_CATALOG(self):
        canonicos = {m["CANONICAL_SOURCE_ID"] for m in MAPA_FONTE}
        self.assertNotIn(self.LEGADO, canonicos,
                         "IT-ADAMA-CATALOG voltou a ser CANONICAL_SOURCE_ID")
        self.assertIn(self.CANONICO, canonicos)

    def test_Q_todo_canonico_tem_ficha_no_atlas(self):
        """SOURCE_ID não se fabrica: canónico é o que o Atlas tem como ficha."""
        no_atlas = _source_ids_do_atlas()
        self.assertTrue(no_atlas, "o Atlas nao devolveu nenhum SOURCE_ID")
        for m in MAPA_FONTE:
            self.assertIn(m["CANONICAL_SOURCE_ID"], no_atlas,
                          "%s e canonico no mapa mas nao tem ficha no Atlas"
                          % m["CANONICAL_SOURCE_ID"])
        self.assertNotIn(self.LEGADO, no_atlas,
                         "IT-ADAMA-CATALOG ganhou ficha propria — isso e uma "
                         "SEGUNDA fonte para o mesmo publicador")

    def test_R_o_builder_nao_inventa_source_id(self):
        import adama_referencia as A
        no_atlas = _source_ids_do_atlas()
        for k, v in A.SOURCE_ID_CANONICO.items():
            self.assertIn(v, no_atlas, "%s -> %s: canonico sem ficha" % (k, v))
        self.assertEqual(self.CANONICO, A.SOURCE_ID_CANONICO[self.LEGADO])
        self.assertEqual(self.CANONICO, A.SOURCE_ID_CANONICO["SRC_ADAMA_COM"])

    def test_S_o_legado_continua_encontravel(self):
        """Apagar o nome antigo partiria a linhagem: 51 paginas e 141
        documentos foram produzidos sob IT-ADAMA-CATALOG e continuam a
        responder «como me chamava quando fui produzido?»."""
        legados = {m["LEGACY_SOURCE_ID"]: m["CANONICAL_SOURCE_ID"] for m in MAPA_FONTE}
        self.assertEqual(self.CANONICO, legados.get(self.LEGADO))
        self.assertEqual(self.CANONICO, legados.get("SRC_ADAMA_COM"))
        com_legado = lambda col: sum(  # noqa: E731
            1 for r in col if self.LEGADO in r["PROVENANCE"].get("SOURCE_IDS_LEGACY", []))
        self.assertEqual(51, com_legado(PORTFOLIO))
        self.assertEqual(51, com_legado(MASTER))
        self.assertEqual(141, com_legado(DOCS))
        for col in (PORTFOLIO, MASTER, DOCS, REGISTOS, USOS):
            for r in col:
                self.assertNotIn(self.LEGADO, r["PROVENANCE"]["SOURCE_IDS"],
                                 "legado a ser usado como canonico")

    def test_T_regenerar_nao_desfaz_o_mapa(self):
        """O ataque: corrigir o JSON à mão e o builder desfazer na regeneração.
        O mapa commitado tem de ser o que o builder produz."""
        import adama_referencia as A
        gerado = A.montar(escrever=False)["SOURCE-ID-MAP.json"]["RECORDS"]
        self.assertEqual(MAPA_FONTE, gerado)

    def test_V_o_dono_da_fonte_adama_tem_um_id_so_e_o_antigo_nao_morre(self):
        """IT-OWN-040 e IT-OWN-ADAMA-IT eram dois ids para o mesmo dono da
        mesma fonte IT-T9-008. Reconciliados em 2026-09-16 pela cadeia de
        autoridade da casa (a ficha do Atlas decide). Os quatro sitios que
        declaram o dono de IT-T9-008 tem de dizer o MESMO id, e o antigo tem
        de continuar encontravel como OWNER_ID_LEGACY."""
        import re
        CANON, LEGADO = "IT-OWN-040", "IT-OWN-ADAMA-IT"
        atlas = os.path.join(RAIZ, "docs", "fontes", "ATLAS-DE-FONTES-EAME.md")
        with io.open(atlas, encoding="utf-8") as fh:
            texto = fh.read()
        i = texto.index("SOURCE_ID:                    IT-T9-008")
        ficha = texto[i:i + 4000]
        m = re.search(r"SOURCE_OWNER:\s+.*?\((IT-OWN-[A-Z0-9-]+)\)", ficha)
        self.assertEqual(CANON, m.group(1), "a ficha do Atlas mudou de dono")
        self.assertIn("OWNER_ID_LEGACY: " + LEGADO, ficha)
        master = ler_raiz("candidatas", "ITALY-SOURCE-MASTER-V1.json")
        fonte = next(s for s in master["sources"] if s["SOURCE_ID"] == "IT-T9-008")
        dono = next(o for o in master["owners"] if o["OWNER_ID"] == CANON)
        self.assertEqual(CANON, fonte["OWNER_ID"])
        self.assertIn(LEGADO, dono["OWNER_ID_LEGACY"])
        self.assertFalse(any(o["OWNER_ID"] == LEGADO for o in master["owners"]),
                         "o legado virou registo proprio — segundo dono canonico")
        man = ler_raiz("data", "samples", "IT-SOURCE-SAMPLES", "IT-T9-008", "MANIFEST.json")
        self.assertEqual(CANON, man["OWNER_ID"])
        self.assertEqual(LEGADO, man["OWNER_ID_LEGACY"])
        self.assertEqual("9f56e17877efe44f086c65efb9e4910f138b8273a0eaedc70842ac697f1218c6",
                         man["FILES"][0]["SHA256"], "a amostra mudou de bytes")
        with io.open(os.path.join(RAIZ, "regras", "italy_contracts.mjs"),
                     encoding="utf-8") as fh:
            mjs = fh.read()
        j = mjs.index('"IT-T9-008": {')
        bloco = mjs[j:j + 900]
        self.assertIn('OWNER_ID: "%s"' % CANON, bloco)
        self.assertIn('OWNER_ID_LEGACY: "%s"' % LEGADO, bloco)
        self.assertNotIn('OWNER_ID: "%s"' % LEGADO, bloco)

    def test_U_o_51_e_o_que_se_leu_nao_o_que_o_catalogo_tem(self):
        """51 = OBSERVED_READABLE; total oficial = NAO SEI. As duas coisas
        têm de continuar separadas em todo o lado onde esta casa fala."""
        cat = registos("CATALOG-SNAPSHOTS.json")
        self.assertTrue(cat)
        for s in cat:
            self.assertEqual("NAO SEI", s["TOTAL_OFFICIAL_CATALOG"])
            self.assertEqual(51, s["OBSERVED_READABLE_PRODUCT_PAGES"])
        self.assertEqual(51, len(MASTER))
        with io.open(os.path.join(CASA, "CONTRATO-ADAMA-REFERENCE.md"),
                     encoding="utf-8") as fh:
            contrato = fh.read().lower()
        for frase in ("catalogo tem 51", "catálogo tem 51", "catalogo = 51",
                      "catálogo de 51 produtos", "catalogo de 51 produtos"):
            self.assertNotIn(frase, contrato,
                             "o contrato voltou a afirmar o total do catalogo: «%s»" % frase)


if __name__ == "__main__":
    unittest.main(verbosity=2)
