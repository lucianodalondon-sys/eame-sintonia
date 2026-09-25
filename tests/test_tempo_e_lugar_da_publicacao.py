#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""D61 — QUANDO A FONTE PUBLICOU, E ONDE ELA ESTÁ. E nada sobre o facto.

    PUBLICATION_TIME != FACT_TIME != OBSERVATION_TIME != COLLECTION_TIME
    SOURCE_LOCATION  != FACT_LOCATION

Medido na Sala real a 25/09: `published_at` e `source_location` em `NAO SEI`
em 78/78. Este ficheiro prova as duas réguas que faltavam, sem Sala e sem rede:

    coleta/executor_texto_de_html.py::tempo_de_publicacao   HTML -> {VALOR, BASE}
    regras/contratos_de_fonte.py::lugar_da_fonte           SOURCE_ID -> {VALOR, BASE}

Os HTML reais vêm do armazém italiano versionado nesta árvore
(`data/collection-store/italy/`). Só se LÊEM.
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import unittest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if RAIZ not in sys.path:
    sys.path.insert(0, RAIZ)

import _gavetas  # noqa: E402,F401
from coleta import executor_texto_de_html as ex  # noqa: E402
from leis import artefato as art  # noqa: E402
from regras import contratos_de_fonte as cdf  # noqa: E402

NAO_SEI = art.NAO_SEI
ARMAZEM = os.path.join(RAIZ, "data", "collection-store", "italy")

#: HTML reais, um por forma de data medida no armazém.
REAL_JSON_LD = ("IT-T10-022/IT-T10-022_URL_news_bob-buresh-2026-psa-poultry-"
                "industry-award/v1_47fb3e8825be/bob-buresh-2026-psa-poultry-"
                "industry-award.html")
REAL_META = ("IT-T10-018/IT-T10-018_URL_news_annamaria-medici-in-ortofrutta-"
             "vince-il-valore-percepito/v1_451255119590/annamaria-medici-in-"
             "ortofrutta-vince-il-valore-percepito.html")
REAL_SO_BARRA_LATERAL = ("IT-T7-021/IT-T7-021_URL_news_imprese_sversamento-nel-"
                         "naviglio-grande-riprende-la-navigazione/v1_d44208dc767f/"
                         "sversamento-nel-naviglio-grande-riprende-la-navigazione.html")
REAL_META_E_TIME_EM_PROSA = ("IT-T7-042/IT-T7-042_URL_news-blog_a-sostegno-della-"
                             "filiera-del-vino-italiano/v1_6296ba29a21e/a-sostegno-"
                             "della-filiera-del-vino-italiano.html")

#: Nenhuma saída destas réguas pode ter chave de facto.
CHAVES_DO_FACTO = {"FACT_TIME", "fact_time", "FACT_LOCATION", "fact_location",
                   "FACT_TIME_BASIS", "FACT_LOCATION_BASIS"}


def _real(caminho):
    with open(os.path.join(ARMAZEM, caminho), "rb") as fh:
        return fh.read()


def _pagina(cabeca="", corpo=""):
    return ("<!doctype html><html><head>%s</head><body>%s<p>texto</p></body>"
            "</html>" % (cabeca, corpo)).encode("utf-8")


def _ld(obj):
    return '<script type="application/ld+json">%s</script>' % json.dumps(obj)


class OsHtmlReaisDasFontesItalianas(unittest.TestCase):

    def test_json_ld_datePublished_vence_quando_existe(self):
        r = ex.tempo_de_publicacao(_real(REAL_JSON_LD))
        self.assertEqual("2026-08-11T12:30:19+00:00", r["VALOR"])
        self.assertEqual(ex.BASE_JSON_LD, r["BASE"])
        self.assertEqual("INSTANTE", r["PRECISAO"])

    def test_meta_article_published_time_quando_nao_ha_json_ld(self):
        r = ex.tempo_de_publicacao(_real(REAL_META))
        self.assertEqual("2026-07-11T04:00:00+00:00", r["VALOR"])
        self.assertEqual(ex.BASE_META, r["BASE"])

    def test_time_da_barra_lateral_nao_da_data_ao_artigo(self):
        """IT-T7-021: seis `<time datetime>` diferentes, todos de «últimos posts».

        Ficar com o primeiro daria ao artigo a data de outro. NAO SEI, e o
        porquê diz AMBIGUO.
        """
        r = ex.tempo_de_publicacao(_real(REAL_SO_BARRA_LATERAL))
        self.assertEqual(NAO_SEI, r["VALOR"])
        self.assertEqual(NAO_SEI, r["BASE"])
        self.assertIn("AMBIGUO", r["PORQUE"])

    def test_time_em_prosa_nao_e_lido_e_o_meta_responde(self):
        r = ex.tempo_de_publicacao(_real(REAL_META_E_TIME_EM_PROSA))
        self.assertEqual("2026-07-14T15:25:13+00:00", r["VALOR"])
        self.assertEqual(ex.BASE_META, r["BASE"])


class AOrdemEANormalizacao(unittest.TestCase):

    def test_a_ordem_e_json_ld_meta_time_indice(self):
        self.assertEqual((ex.BASE_JSON_LD, ex.BASE_META, ex.BASE_TIME,
                          ex.BASE_INDICE), ex.ORDEM_DA_PUBLICACAO)
        tudo = _pagina(
            _ld({"@type": "NewsArticle", "datePublished": "2026-01-01T10:00:00Z"})
            + '<meta property="article:published_time" content="2026-02-02T10:00:00Z">',
            '<time datetime="2026-03-03T10:00:00Z">3</time>')
        r = ex.tempo_de_publicacao(tudo, data_no_indice="2026-04-04")
        self.assertEqual(("2026-01-01T10:00:00+00:00", ex.BASE_JSON_LD),
                         (r["VALOR"], r["BASE"]))
        sem_ld = _pagina(
            '<meta content="2026-02-02T10:00:00Z" property="article:published_time">',
            '<time datetime="2026-03-03T10:00:00Z">3</time>')
        self.assertEqual(ex.BASE_META, ex.tempo_de_publicacao(sem_ld)["BASE"])
        so_time = _pagina(corpo='<time datetime="2026-03-03T10:00:00+0100">3</time>')
        r = ex.tempo_de_publicacao(so_time, data_no_indice="2026-04-04")
        self.assertEqual(("2026-03-03T10:00:00+01:00", ex.BASE_TIME),
                         (r["VALOR"], r["BASE"]))
        so_indice = _pagina()
        r = ex.tempo_de_publicacao(so_indice, data_no_indice="2026-04-04")
        self.assertEqual(("2026-04-04", ex.BASE_INDICE, "DIA"),
                         (r["VALOR"], r["BASE"], r["PRECISAO"]))

    def test_nada_na_pagina_e_NAO_SEI_com_o_que_cada_nivel_viu(self):
        r = ex.tempo_de_publicacao(_pagina())
        self.assertEqual(NAO_SEI, r["VALOR"])
        for base in ex.ORDEM_DA_PUBLICACAO:
            self.assertIn(base, r["PORQUE"])

    def test_meta_por_name_tambem_conta(self):
        p = _pagina('<meta name="article:published_time" content="2026-05-05T08:00:00+02:00">')
        self.assertEqual("2026-05-05T08:00:00+02:00",
                         ex.tempo_de_publicacao(p)["VALOR"])

    def test_json_ld_dentro_de_graph(self):
        p = _pagina(_ld({"@graph": [{"@type": "WebPage"},
                                    {"@type": "Article",
                                     "datePublished": "2026-06-06T06:06:06+00:00"}]}))
        self.assertEqual("2026-06-06T06:06:06+00:00",
                         ex.tempo_de_publicacao(p)["VALOR"])

    def test_json_ld_partido_nao_apaga_o_resto(self):
        p = _pagina('<script type="application/ld+json">{nao e json</script>'
                    '<meta property="article:published_time" content="2026-07-07T07:07:07Z">')
        r = ex.tempo_de_publicacao(p)
        self.assertEqual((ex.BASE_META, "2026-07-07T07:07:07+00:00"),
                         (r["BASE"], r["VALOR"]))

    def test_json_ld_que_se_contradiz_cala_se_e_passa_ao_seguinte(self):
        p = _pagina(_ld([{"datePublished": "2026-01-01T00:00:00Z"},
                         {"datePublished": "2025-12-01T00:00:00Z"}])
                    + '<meta property="article:published_time" content="2026-01-01T00:00:00Z">')
        r = ex.tempo_de_publicacao(p)
        self.assertEqual(ex.BASE_META, r["BASE"])
        self.assertIn("AMBIGUO", r["PORQUE"])

    def test_o_mesmo_instante_em_dois_fusos_nao_e_ambiguo(self):
        p = _pagina(corpo='<time datetime="2026-08-11T12:30:19+00:00">a</time>'
                          '<time datetime="2026-08-11T14:30:19+02:00">b</time>')
        r = ex.tempo_de_publicacao(p)
        self.assertEqual(ex.BASE_TIME, r["BASE"])
        self.assertEqual("2026-08-11T12:30:19+00:00", r["VALOR"])

    def test_normalizacao_iso_8601(self):
        casos = {
            "2026-08-11T12:30:19Z": ("2026-08-11T12:30:19+00:00", "INSTANTE"),
            "2026-08-11T12:30:19.123+0200": ("2026-08-11T12:30:19+02:00", "INSTANTE"),
            "2026-08-11T12:30+01:00": ("2026-08-11T12:30:00+01:00", "INSTANTE"),
            "2026-08-11": ("2026-08-11", "DIA"),
            # hora sem fuso nao e instante: fica o dia, e nao se inventa o Z
            "2026-08-11T12:30:19": ("2026-08-11", "DIA"),
        }
        for bruto, esperado in casos.items():
            self.assertEqual(esperado, ex.normalizar_instante(bruto), bruto)
        for lixo in ("14 luglio 2026", "", None, "2026-02-30", "2026-08-11T25:00:00Z"):
            self.assertIsNone(ex.normalizar_instante(lixo)[0], lixo)


class PublicacaoNaoViraFacto(unittest.TestCase):
    """A mutação da D61: `published_at` usado como `fact_time` tem de reprovar."""

    def _todas_as_saidas(self):
        paginas = [_real(REAL_JSON_LD), _real(REAL_META),
                   _real(REAL_SO_BARRA_LATERAL), _pagina()]
        for p in paginas:
            r = ex.tempo_de_publicacao(p)
            yield r
            yield ex.publicacao_para_o_contrato(r)

    def test_nenhuma_saida_tem_chave_de_facto(self):
        for saida in self._todas_as_saidas():
            self.assertFalse(CHAVES_DO_FACTO & set(saida), saida)

    def test_so_atravessa_afirmacao_e_o_porque_vai_na_base(self):
        com = ex.publicacao_para_o_contrato(ex.tempo_de_publicacao(_real(REAL_META)))
        self.assertEqual({"PUBLISHED_AT": "2026-07-11T04:00:00+00:00",
                          "PUBLISHED_AT_BASIS": ex.BASE_META}, com)
        sem = ex.publicacao_para_o_contrato(
            ex.tempo_de_publicacao(_real(REAL_SO_BARRA_LATERAL)))
        self.assertNotIn("PUBLISHED_AT", sem)
        self.assertTrue(sem["PUBLISHED_AT_BASIS"].startswith("NAO SEI — "))

    def test_o_artefato_com_a_publicacao_fica_de_pe_e_o_facto_fica_NAO_SEI(self):
        """Posta no contrato comum, a publicação não mexe no tempo do facto —
        e a lei de `leis/artefato.py::conferir` reprova quem a copiar para lá."""
        pub = ex.publicacao_para_o_contrato(ex.tempo_de_publicacao(_real(REAL_JSON_LD)))
        a = art.Artefato(ARTIFACT_ID="x", ARTIFACT_TYPE=art.RAW,
                         STORAGE_LOCATION="x.html", SHA256="0" * 64,
                         PUBLISHED_AT=pub["PUBLISHED_AT"])
        self.assertEqual(NAO_SEI, a.FACT_TIME)
        self.assertEqual([], art.conferir(a))
        a.FACT_TIME = a.PUBLISHED_AT               # o defeito, plantado
        self.assertTrue(any("PUBLISHED_AT" in q for q in art.conferir(a)))


def _node():
    return shutil.which("node") is not None


class OLugarDaFontePeloContrato(unittest.TestCase):

    def _exige_node(self):
        if not cdf.declarados():
            self.skipTest("DEPENDENCIA AUSENTE: node — sem ele o contrato "
                          "(regras/italy_contracts.mjs) nao se le")

    def test_contrato_com_sede_declarada(self):
        self._exige_node()
        r = cdf.lugar_da_fonte("IT-T3-002")
        self.assertEqual(("Napoli", cdf.BASE_CONTRATO), (r["VALOR"], r["BASE"]))
        self.assertEqual("Napoli (sede da Regiao) — fixo", r["ORIGINAL"])
        self.assertEqual({"SOURCE_LOCATION": "Napoli",
                          "SOURCE_LOCATION_BASIS": cdf.BASE_CONTRATO},
                         cdf.lugar_para_o_contrato(r))

    def test_contrato_que_nao_declara_e_NAO_SEI_com_o_porque_certo(self):
        self._exige_node()
        r = cdf.lugar_da_fonte("IT-T10-018")
        self.assertEqual((NAO_SEI, NAO_SEI), (r["VALOR"], r["BASE"]))
        self.assertIn("nao declara", r["PORQUE"])
        self.assertNotIn("GAZETTEER", r["PORQUE"])
        sai = cdf.lugar_para_o_contrato(r)
        self.assertNotIn("SOURCE_LOCATION", sai)
        self.assertTrue(sai["SOURCE_LOCATION_BASIS"].startswith("NAO SEI — "))

    def test_lugar_fora_do_gazetteer_nao_se_adivinha(self):
        self._exige_node()
        r = cdf.lugar_da_fonte("IT-T3-011")          # «Terlano (BZ)»
        self.assertEqual(NAO_SEI, r["VALOR"])
        self.assertEqual("Terlano (BZ)", r["ORIGINAL"])

    def test_o_REGION_do_atlas_nunca_vira_lugar_da_fonte(self):
        """IT-T7-017: sede em Reggio Emilia, o Atlas diz LAZIO (a amostra)."""
        self._exige_node()
        r = cdf.lugar_da_fonte("IT-T7-017")
        self.assertEqual(NAO_SEI, r["VALOR"])
        self.assertNotIn("LAZIO", json.dumps(r).upper())

    def test_sem_node_a_resposta_e_NAO_SEI_e_nunca_um_valor(self):
        """A outra realidade: node ausente. Aceita-se NAO SEI, nunca um valor."""
        r = cdf.lugar_da_fonte("IT-T3-002")
        self.assertIn(r["VALOR"], ("Napoli", NAO_SEI))
        if r["VALOR"] == NAO_SEI:
            self.assertEqual(NAO_SEI, r["BASE"])

    def test_nenhuma_saida_tem_chave_de_facto(self):
        """A mutação da D61: `source_location` copiado para `fact_location` reprova."""
        for sid in ("IT-T3-002", "IT-T10-018", "IT-T3-011", "IT-T7-017"):
            r = cdf.lugar_da_fonte(sid)
            for saida in (r, cdf.lugar_para_o_contrato(r)):
                self.assertFalse(CHAVES_DO_FACTO & set(saida), (sid, saida))

    def test_a_linha_onboarded_pode_declarar_a_sede_e_o_padrao_continua_NAO_SEI(self):
        if not _node():
            self.skipTest("DEPENDENCIA AUSENTE: node")
        guiao = (
            "const m = await import(%s);\n"
            "const base = {SOURCE_ID: 'IT-T99-001', OUTPUT_TYPE: 'HTML',"
            " ACQUISITION: {STRATEGY: 'STATIC_ENDPOINT', URL: 'https://x.it/a'}};\n"
            "const a = m.contratoGenerico(base);\n"
            "const b = m.contratoGenerico({...base, SOURCE_LOCATION_RULE: 'Bari (sede)'});\n"
            "process.stdout.write(JSON.stringify([a.SOURCE_LOCATION_RULE,"
            " b.SOURCE_LOCATION_RULE, b.FACT_LOCATION_RULE]));\n"
            % json.dumps(__import__("pathlib").Path(
                os.path.join(RAIZ, "regras", "italy_contracts.mjs")).as_uri()))
        r = subprocess.run(["node", "--input-type=module", "-e", guiao],
                           capture_output=True, text=True, encoding="utf-8",
                           cwd=RAIZ, timeout=60)
        self.assertEqual(0, r.returncode, r.stderr[-400:])
        sem, com, facto = json.loads(r.stdout)
        self.assertEqual("NAO SEI", sem)
        self.assertEqual("Bari (sede)", com)
        # declarar a sede NAO mexe na regra do lugar do facto
        self.assertTrue(facto.startswith("UNKNOWN"))


if __name__ == "__main__":
    unittest.main()
