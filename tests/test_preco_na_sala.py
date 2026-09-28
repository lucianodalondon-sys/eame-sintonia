# -*- coding: utf-8 -*-
"""PROPOSTA 038 · o lugar do preco na Sala — a regra nos dois sitios, e a prova no banco.

Sem banco: o que o escritor recusa, o que ele escreve, e que a regra do Python e a da trava da
proposta sao a MESMA (uma regra que so vive num dos lados nao e uma regra).
Com banco (Postgres descartavel dos binarios de ~/orca/pgtmp): a cadeia canonica sobe, a proposta
aplica-se, o preco entra, a VISTA le-o, e o que nao se pode fazer e recusado.

    py -m unittest tests.test_preco_na_sala
"""
import glob
import importlib.util
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

RAIZ = Path(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
for p in ("", "admissao", "coleta", "orquestrador"):
    sys.path.insert(0, str(RAIZ / p))
import _gavetas                          # noqa: E402,F401
import admissao as adm                   # noqa: E402
import sala_de_espera as espera          # noqa: E402
import preco_na_sala as PS               # noqa: E402

_spec = importlib.util.spec_from_file_location(
    "ensaio_offline", RAIZ / "scripts" / "micro_coleta" / "ensaio_offline.py")
E = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(E)

PROPOSTA = next(iter(glob.glob(str(RAIZ / "supabase" / "migrations" / "038_*.sql"))))
DESFAZER = RAIZ / "supabase" / "desfazer" / "038_desfazer.sql"
SHA = "b" * 64
TEM_PG = (E.PG_BIN / ("initdb.exe" if os.name == "nt" else "initdb")).exists() and shutil.which("bash")


def _preco(**kw):
    """Um preco REAL, dos que a fonte publica: como o EC Agri-food Data Portal («€237,00»)."""
    p = {"INDICADOR": "PRECO", "CULTURA": "Riso", "NIVEL": "PIAZZA", "PRACA": "Bologna",
         "VALOR_TEXTO": "€237,00", "VALOR_NUMERICO": "237.00", "UNIDADE": "€/100kg",
         "PERIODO_INICIO": "2026-09-07", "PERIODO_FIM": "2026-09-13", "CLASSE": "CURRENT",
         "CITACAO": "Riso, Bologna: €237,00 / 100 kg",
         "O_QUE_NAO_PROVA": "preco de piazza nao e preco nacional, e preco nao e lucro",
         "RAW_SHA256": SHA, "DOCUMENT_ID": "DOC-1", "ONDE": "tabela 2, linha 7"}
    p.update(kw)
    return p


def _ready(i, corrida="R1", **kw):
    item = {"id": "derived:%d" % i, "texto": "Bollettino fitosanitario n. %d" % i,
            "source_id": "IT-T3-002", "artifact_type": "DERIVED",
            "parent_sha256": "a" * 64, "raw_asset_id": None,
            "captured_at": "2026-09-18T17:19:15Z"}
    item.update(kw)
    d = adm.Decisao(item=item["id"], universo="T3", resultado=adm.SIM,
                    regra="teste", motivo="teste", corrida=corrida)
    return adm.pronto_para_inteligencia(item, d)


class P1OQueNaoEntra(unittest.TestCase):
    def test_ausencia_nao_gera_linha(self):
        self.assertIsNone(PS.sql_de_registo("R1", [(0, {}), (1, {})]))

    def test_o_valor_nao_sei_nunca_vira_preco(self):
        """Ausencia escreve-se AUSENCIA DE LINHA. Um «NAO SEI» com valor seria um preco inventado."""
        self.assertIn("NAO SEI", PS.motivo_da_recusa(_preco(VALOR_TEXTO="NAO SEI")))
        self.assertIsNone(PS.sql_de_registo("R1", [(0, _preco(VALOR_TEXTO="NAO SEI", VALOR_NUMERICO=None))]))

    def test_piazza_sem_praca_nao_entra(self):
        self.assertIsNone(PS.sql_de_registo("R1", [(0, _preco(NIVEL="PIAZZA", PRACA=None))]))
        self.assertIsNotNone(PS.sql_de_registo("R1", [(0, _preco(NIVEL="NACIONAL", PRACA=None))]))

    def test_indicador_e_classe_e_nivel_sao_listas_fechadas(self):
        for p in (_preco(INDICADOR="PRODUCAO"), _preco(CLASSE="MAYBE"), _preco(NIVEL="ITALIA?")):
            self.assertIsNotNone(PS.motivo_da_recusa(p), p)

    def test_sem_a_prova_dos_bytes_nao_entra(self):
        for mau in ("", "nao-e-sha", "b" * 63, "B" * 64):
            self.assertIsNone(PS.sql_de_registo("R1", [(0, _preco(RAW_SHA256=mau))]), mau)

    def test_periodo_invertido_nao_entra(self):
        self.assertIsNone(PS.sql_de_registo(
            "R1", [(0, _preco(PERIODO_INICIO="2026-09-13", PERIODO_FIM="2026-09-07"))]))

    def test_sem_o_que_nao_prova_nao_entra(self):
        self.assertIsNone(PS.sql_de_registo("R1", [(0, _preco(O_QUE_NAO_PROVA=""))]))


class P2OQueSeEscreve(unittest.TestCase):
    def test_o_literal_sai_byte_a_byte_com_a_virgula_italiana(self):
        sql = PS.sql_de_registo("R1", [(3, _preco())])
        self.assertIn("'€237,00'", sql)
        # o parse vai AO LADO, e nao substitui o literal: converter cedo perde a virgula
        self.assertIn("'237.00'", sql)
        self.assertNotIn("237.0,", sql)

    def test_sem_prova_de_identidade_o_documento_e_nao_sei_nunca_fabricado(self):
        sql = PS.sql_de_registo("R1", [(0, _preco(DOCUMENT_ID=""))])
        self.assertIn('"DOCUMENT_ID": "NAO SEI"', sql)
        self.assertIn('"RAW_SHA256": "%s"' % SHA, sql)
        self.assertIn('"ONDE": "tabela 2, linha 7"', sql)

    def test_aspas_nao_partem_o_sql(self):
        sql = PS.sql_de_registo("R'1", [(0, _preco(CULTURA="Riso'vo", CITACAO="l'ha detto"))])
        self.assertIn("'R''1'", sql)
        self.assertIn("'Riso''vo'", sql)
        self.assertIn("'l''ha detto'", sql)

    def test_a_chave_do_item_e_a_da_sala(self):
        sql = PS.sql_de_registo("R1", [(3, _preco())])
        self.assertIn("('R1', 3,", sql)
        # o `on conflict` cita a chave PELO NOME: com o alvo por colunas, o banco teria de adivinhar
        # por que conjunto se resolve, e a deduplicacao do reprocesso ficava dependente disso
        self.assertIn("on conflict on constraint preco_do_item_uma_vez do nothing", sql)
        self.assertIn("constraint preco_do_item_uma_vez unique nulls not distinct",
                      Path(PROPOSTA).read_text(encoding="utf-8"))


class P3AMesmaRegraNosDoisSitios(unittest.TestCase):
    """A regra do escritor e a trava da tabela TEM de ser a mesma. Se divergirem, a divergencia
    aparece em producao e nao num teste."""

    @classmethod
    def setUpClass(cls):
        cls.sql = PROPOSTA and Path(PROPOSTA).read_text(encoding="utf-8")

    def _lista(self, nome):
        bloco = re.search(r"check \(%s in \(([^)]*)\)\)" % nome, self.sql).group(1)
        return tuple(re.findall(r"'([A-Z_]+)'", bloco))

    def test_as_tres_listas_fechadas_sao_as_mesmas(self):
        self.assertEqual(self._lista("indicador"), PS.INDICADORES)
        self.assertEqual(self._lista("classe"), PS.CLASSES)
        self.assertEqual(self._lista("nivel"), PS.NIVEIS)

    def test_as_colunas_obrigatorias_sao_as_chaves_obrigatorias(self):
        corpo = self.sql.split("create table if not exists public.sala_de_espera_preco (", 1)[1]
        corpo = corpo.split("\n);", 1)[0]
        obrigatorias = set()
        for linha in corpo.splitlines():
            linha = linha.split("--")[0].strip().rstrip(",")
            m = re.match(r"^(\w+)\s+\w+.*not null", linha)
            if m and "default" not in linha:
                obrigatorias.add(m.group(1))
        # as colunas da chave e da prova vivem em `run_id`/`ordem` e no jsonb `prova`
        mapa = {"INDICADOR": "indicador", "CULTURA": "cultura_literal", "NIVEL": "nivel",
                "VALOR_TEXTO": "valor_texto", "UNIDADE": "unidade",
                "PERIODO_INICIO": "periodo_inicio", "PERIODO_FIM": "periodo_fim",
                "CLASSE": "classe", "CITACAO": "citacao_literal",
                "O_QUE_NAO_PROVA": "o_que_nao_prova"}
        self.assertEqual({mapa[c] for c in PS.CHAVES_OBRIGATORIAS if c in mapa},
                         obrigatorias - {"run_id", "ordem", "prova"})
        for chave in ("RAW_SHA256", "ONDE"):
            self.assertIn("prova ? '%s'" % chave, self.sql)

    def test_a_migracao_nao_toca_na_sala_e_esta_nas_migracoes(self):
        codigo = "\n".join(l for l in self.sql.lower().splitlines()
                           if not l.strip().startswith("--"))
        self.assertNotIn("alter table public.sala_de_espera ", codigo)
        self.assertNotRegex(codigo, r"\bdrop\b")
        # PROMOVIDA a migration (o dono aprovou em 28/09): vive em `migrations/`, e nao pode
        # continuar em `propostas/` — uma migration em dois sitios sao duas verdades.
        self.assertEqual([p.name for p in Path(RAIZ, "supabase", "migrations").glob("038_*.sql")],
                         ["038_a_sala_guarda_o_preco.sql"])
        self.assertEqual([p.name for p in Path(RAIZ, "supabase", "propostas").glob("038_*.sql")], [])
        self.assertNotIn("revisao_so_de_campo_revisivel", codigo,
                         "a trava das revisoes da 033 nao se toca")

    def test_a_vista_traz_o_que_a_inteligencia_pediu(self):
        """(run_id, ordem), RAW_SHA256, DOCUMENT_ID, o valor LITERAL e a unidade."""
        vista = self.sql.split("create or replace view public.sala_de_espera_precos as", 1)[1]
        for obrigatorio in ("p.run_id", "p.ordem", "as raw_sha256", "as document_id",
                            "p.valor_texto", "p.unidade"):
            self.assertIn(obrigatorio, vista)


@unittest.skipUnless(TEM_PG, "sem Postgres portatil (~/orca/pgtmp) ou sem bash: a prova nao correu")
class P4NoBancoDescartavel(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.pasta = Path(tempfile.mkdtemp(prefix="proposta-038-"))
        cls.base = E.Base(cls.pasta / "pg")
        assert ":54330/" not in cls.base.url, "isto e a Sala real"
        cls.env = {**os.environ, "PATH": str(E.PG_BIN) + os.pathsep + os.environ.get("PATH", "")}
        r = cls.base.subir(RAIZ, cls.env)
        if r["CODIGO"] != 0:
            cls.base.descer()
            raise unittest.SkipTest("migrations falharam: %s" % r["ERRO"])
        cls._amb = dict(os.environ)
        try:
            os.environ.update({"SINTONIA_SALA_BACKEND": "POSTGRES",
                               "SINTONIA_SALA_DSN": cls.base.url,
                               "SINTONIA_PSQL_EXE": cls.base.exe("psql")})
            cls.sql("insert into collection_run (run_id, platform, started_at, rule_version) "
                    "values ('R1', 'teste', now(), 'teste')")
            espera.pousar("R1", [_ready(1)])
            cls.provas = cls.sql("select count(*) || ' ' || coalesce(md5(string_agg(t::text, '' "
                                 "order by run_id, ordem)), '-') from public.sala_de_espera t").stdout.strip()
            cls.aplicar(PROPOSTA)
        except Exception:
            cls.tearDownClass()
            raise

    @classmethod
    def tearDownClass(cls):
        os.environ.clear()
        os.environ.update(cls._amb)
        cls.base.descer()
        shutil.rmtree(cls.pasta, ignore_errors=True)

    @classmethod
    def sql(cls, comando, falhar=True):
        # ⚠️ O SQL VAI PELA ENTRADA EM UTF-8, NUNCA PELA LINHA DE COMANDO. No Windows a linha de
        # comando chega ao psql noutra codificacao, e o «€» rebentou com
        # «sequencia de bytes e invalida para codificacao UTF8: 0x80» — medido a 28/09, o mesmo
        # tropeco que o ensaio da 037 ja tinha registado. Pela entrada, com o cliente em UTF8
        # declarado, o literal do preco chega byte a byte.
        r = subprocess.run([cls.base.exe("psql"), "-X", "-q", "-A", "-t", "-F", "|",
                            "-v", "ON_ERROR_STOP=1", "-d", cls.base.url, "-f", "-"],
                           input=comando, capture_output=True, text=True, encoding="utf-8",
                           errors="replace", env=dict(os.environ, PGCLIENTENCODING="UTF8"))
        if falhar and r.returncode != 0:
            raise AssertionError(r.stderr)
        return r

    @classmethod
    def aplicar(cls, ficheiro):
        r = subprocess.run([cls.base.exe("psql"), "-X", "-q", "-v", "ON_ERROR_STOP=1",
                            "--single-transaction", "-f", str(ficheiro), cls.base.url],
                           capture_output=True, text=True, encoding="utf-8", errors="replace")
        if r.returncode != 0:
            raise AssertionError(r.stderr[-600:])
        return r

    def test_1_a_cadeia_canonica_subiu_e_a_sala_tem_o_item(self):
        self.assertEqual(self.sql("select count(*) from sala_de_espera where run_id='R1'")
                         .stdout.strip(), "1")

    def test_2_o_preco_entra_e_a_vista_le_o_literal_com_a_prova(self):
        self.assertEqual(PS.registar("R1", [(0, _preco())], dsn=self.base.url,
                                     psql=self.base.exe("psql")), "REGISTADO")
        lido = PS.ler("R1", dsn=self.base.url, psql=self.base.exe("psql"))
        self.assertEqual(len(lido), 1, lido)
        _, indicador, valor, unidade, sha, doc, classe = lido[0]
        self.assertEqual((indicador, valor, unidade, classe), ("PRECO", "€237,00", "€/100kg", "CURRENT"))
        self.assertEqual((sha, doc), (SHA, "DOC-1"), "a prova nao chegou a vista")
        # a linha ORIGINAL da Sala nao mudou com o preco ao lado
        self.assertEqual(self.sql("select count(*) || ' ' || coalesce(md5(string_agg(t::text, '' "
                                  "order by run_id, ordem)), '-') from public.sala_de_espera t")
                         .stdout.strip(), self.provas)

    def test_3_reprocessar_o_mesmo_item_nao_duplica_o_preco(self):
        """O reprocesso e a cadeia do canario: o mesmo item, o mesmo codigo, duas vezes.

        Pauta propria (`Verona`) para a prova nao depender da ordem em que os testes correm.
        """
        pauta = _preco(PRACA="Verona")
        for _ in (1, 2):
            PS.registar("R1", [(0, pauta)], dsn=self.base.url, psql=self.base.exe("psql"))
        n = self.sql("select count(*) from sala_de_espera_preco where praca='Verona'").stdout.strip()
        self.assertEqual(n, "1", "o reprocesso escreveu o preco duas vezes")

    def test_4_a_ausencia_nao_escreve_nada(self):
        self.assertEqual(PS.registar("R1", [(0, _preco(VALOR_TEXTO="NAO SEI", VALOR_NUMERICO=None))],
                                     dsn=self.base.url, psql=self.base.exe("psql")), "NADA_A_REGISTAR")

    def test_5_o_banco_recusa_o_que_o_escritor_recusa(self):
        """Uma regra que so vive no codigo nao e uma regra: a trava tem de a impor tambem."""
        for mau in ("update sala_de_espera_preco set valor_texto='€1,00'",
                    "delete from sala_de_espera_preco",
                    "truncate sala_de_espera_preco"):
            r = self.sql(mau, falhar=False)
            self.assertNotEqual(r.returncode, 0, mau)
            self.assertIn("SALA_PRECO_SO_ACRESCENTA", r.stderr, mau)
        piazza = ("insert into sala_de_espera_preco (run_id, ordem, indicador, cultura_literal, nivel, "
                  "valor_texto, unidade, periodo_inicio, periodo_fim, classe, citacao_literal, "
                  "o_que_nao_prova, prova) values ('R1', 0, 'PRECO', 'Riso', 'PIAZZA', '€1,00', 'kg', "
                  "'2026-09-07', '2026-09-13', 'CURRENT', 'x', 'y', '{\"RAW_SHA256\": \"%s\", \"ONDE\": \"z\"}')"
                  % SHA)
        self.assertIn("praca_obrigatoria_no_nivel_piazza", self.sql(piazza, falhar=False).stderr)
        self.assertIn("preco_nao_se_inventa_o_que_nao_se_leu",
                      self.sql(piazza.replace("'€1,00'", "'NAO SEI'").replace("'PIAZZA'", "'NACIONAL'"),
                               falhar=False).stderr)

    def test_6_preco_de_item_que_nao_esta_na_sala_e_recusado(self):
        """A FK e o que impede um preco orfao: sem item na Sala nao ha a que preco pertencer.

        Prova-se pelo NOME da trava, nao pela mensagem: o servidor desta maquina fala portugues
        («viola restricao de chave estrangeira») e o texto do erro nao e contrato.
        """
        self.assertIn("sala_de_espera_preco_run_id_ordem_fkey", self.sql(
            "insert into sala_de_espera_preco (run_id, ordem, indicador, cultura_literal, nivel, "
            "valor_texto, unidade, periodo_inicio, periodo_fim, classe, citacao_literal, "
            "o_que_nao_prova, prova) values ('R1', 99, 'PRECO', 'Riso', 'NACIONAL', '€1,00', 'kg', "
            "'2026-09-07', '2026-09-13', 'CURRENT', 'x', 'y', '{\"RAW_SHA256\": \"%s\", \"ONDE\": \"z\"}')"
            % SHA, falhar=False).stderr)

    def test_z_desfazer_leva_o_preco_e_deixa_a_sala(self):
        self.aplicar(DESFAZER)
        for obj in ("sala_de_espera_preco", "sala_de_espera_precos"):
            self.assertEqual(self.sql("select to_regclass('public.%s') is null" % obj).stdout.strip(),
                             "t", obj)
        self.assertEqual(self.sql("select count(*) || ' ' || coalesce(md5(string_agg(t::text, '' "
                                  "order by run_id, ordem)), '-') from public.sala_de_espera t")
                         .stdout.strip(), self.provas, "o desfazer tocou na Sala")
        # e a proposta pode voltar a subir
        self.aplicar(PROPOSTA)
        self.assertEqual(self.sql("select count(*) from sala_de_espera_preco").stdout.strip(), "0")


if __name__ == "__main__":
    unittest.main()
