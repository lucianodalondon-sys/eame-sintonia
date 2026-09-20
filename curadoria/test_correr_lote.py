#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Testes do executor de lotes — sobretudo da regra de ENDPOINT.

    DEDUPLICAR PELO ANFITRIAO FUNDE TODA A PLATAFORMA NUM SO DONO.

Este ficheiro existe por causa de um defeito real, apanhado ao vivo: as 60
candidatas YouTube casavam `youtube.com` contra `IT-T8-001` e saiam TODAS como
«endpoint da mesma fonte». Sessenta organizacoes italianas distintas a serem
declaradas o mesmo canal.

E o mesmo erro que em 14/09 fundiu tres paginas LinkedIn de tres donos
diferentes, por todas redirigirem para `/login`.
"""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "curadoria"))
import correr_lote as L  # noqa: E402
import capturador as C   # noqa: E402


class TesteChaveSocial(unittest.TestCase):
    def test_identidade_e_anfitriao_mais_handle(self):
        self.assertEqual(L.chave_social("https://www.youtube.com/@agronotizietv"),
                         ("youtube.com", "agronotizietv"))
        self.assertEqual(L.chave_social("https://it.linkedin.com/company/image-line"),
                         ("it.linkedin.com", "image-line"))

    def test_dois_canais_da_mesma_plataforma_nao_colidem(self):
        # ⚠️ O TESTE QUE APANHA A REGRESSAO. Se voltar a comparar por anfitriao,
        # estas duas chaves passam a ser iguais e 60 fontes fundem-se numa.
        a = L.chave_social("https://www.youtube.com/@arpalazio")
        b = L.chave_social("https://www.youtube.com/@arpalombardia")
        self.assertNotEqual(a, b)
        self.assertEqual(a[0], b[0], "mesmo anfitriao — e por isso que o handle importa")

    def test_site_normal_nao_tem_chave_social(self):
        self.assertIsNone(L.chave_social("https://www.arpa.puglia.it/"))

    def test_mesmo_handle_em_enderecos_diferentes_e_a_mesma_fonte(self):
        self.assertEqual(L.chave_social("https://youtube.com/@x"),
                         L.chave_social("https://www.youtube.com/@X"))


class TesteClassificar(unittest.TestCase):
    """As regras de decisao. O ponto central: «nao li» nunca vira «nao serve»."""

    def _f(self, **kw):
        base = {"CAPTURE_RESULT": "FAILED", "CAPTURE_FAILURE_CLASS": None,
                "EVIDENCE": "e", "REAL_EXAMPLE_URL": "NAO SEI",
                "REAL_EXAMPLE_BYTES": None, "REAL_EXAMPLE_SHA256": "NAO SEI",
                "REAL_EXAMPLE_MEDIA_TYPE": "NAO SEI", "ROUTE_FAMILY": "NAO SEI",
                "REAL_EXAMPLE_PUBLISHED_AT": "NAO SEI", "HTTP_STATUS": None,
                "ITEMS_OBSERVED_IN_INDEX": 0}
        base.update(kw)
        return base

    def test_nenhuma_falha_de_leitura_produz_REJECT(self):
        for classe in ("HTTP_ERROR", "TIMEOUT", "DNS_OR_CONN", "TLS",
                       "WALL", "NO_ITEM_FOUND", "EMPTY_BODY"):
            d = L.classificar(self._f(CAPTURE_FAILURE_CLASS=classe), None)
            self.assertNotEqual(d["PROPOSED_STATE"], "REJECT",
                                "«nao consegui ler» virou «nao serve» em %s" % classe)

    def test_transporte_e_UNKNOWN_e_nao_BLOCK(self):
        # nao se chegou la deste egresso != a fonte esta bloqueada
        for classe in ("DNS_OR_CONN", "TLS", "TIMEOUT"):
            d = L.classificar(self._f(CAPTURE_FAILURE_CLASS=classe), None)
            self.assertEqual(d["PROPOSED_STATE"], "UNKNOWN", classe)

    def test_muro_e_BLOCK_por_CAPABILITY(self):
        d = L.classificar(self._f(CAPTURE_FAILURE_CLASS="WALL"), None)
        self.assertEqual(d["PROPOSED_STATE"], "BLOCK")
        self.assertEqual(d["BLOCK_KIND"], "CAPABILITY")

    def test_policy_e_BLOCK_por_POLICY(self):
        d = L.classificar(self._f(CAPTURE_FAILURE_CLASS="POLICY"), None)
        self.assertEqual(d["PROPOSED_STATE"], "BLOCK")
        self.assertEqual(d["BLOCK_KIND"], "POLICY")

    def test_promote_exige_sha_de_64(self):
        bom = self._f(CAPTURE_RESULT="CAPTURED", REAL_EXAMPLE_URL="https://a.it/x.pdf",
                      REAL_EXAMPLE_BYTES=1234, REAL_EXAMPLE_SHA256="a" * 64)
        self.assertEqual(L.classificar(bom, None)["PROPOSED_STATE"], "PROMOTE")
        mau = dict(bom, REAL_EXAMPLE_SHA256="curto")
        self.assertEqual(L.classificar(mau, None)["PROPOSED_STATE"], "NEEDS_REVIEW")

    def test_endpoint_vence_tudo_e_nao_cria_fonte(self):
        # COL-LAW-205: mesmo com captura perfeita, se e endpoint de fonte
        # existente, NAO se propoe fonte nova.
        bom = self._f(CAPTURE_RESULT="CAPTURED", REAL_EXAMPLE_URL="https://a.it/x.pdf",
                      REAL_EXAMPLE_BYTES=1, REAL_EXAMPLE_SHA256="a" * 64)
        d = L.classificar(bom, "IT-T1-008")
        self.assertEqual(d["PROPOSED_STATE"], "ENDPOINT_OF_EXISTING_SOURCE")
        self.assertEqual(d["MATCHED_SOURCE_ID"], "IT-T1-008")
        self.assertEqual(d["RELATION"], "ENDPOINT_OF")


class TesteCobertura(unittest.TestCase):
    def test_cobertura_vem_do_tipo_declarado_e_nao_de_opiniao(self):
        self.assertEqual(L.COBERTURA_POR_TIPO["BASE_OFICIAL"], "regulatory / official-data")
        self.assertEqual(L.COBERTURA_POR_TIPO["CIENCIA"], "science")
        # um tipo desconhecido nao ganha rotulo inventado
        self.assertEqual(L.COBERTURA_POR_TIPO.get("INEXISTENTE", "NAO SEI"), "NAO SEI")


if __name__ == "__main__":
    unittest.main(verbosity=2)
