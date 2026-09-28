# -*- coding: utf-8 -*-
"""CANÁRIO 1149 — re-derivar UM RAW numa cópia, pela estrada canónica (D131/D132).

    py -m unittest tests.test_canario_1149_rederivar

A trava (sem banco): o runner recusa o vivo — porta 5432/54330, porta implícita, morada remota,
banco fora das listas — ANTES de abrir ligação.

A estrada (Postgres descartável, binários de ~/orca/pgtmp, migrations pela cadeia canónica —
o mesmo `Base` do ensaio da 033; sem os binários, SALTA e diz porquê): a cópia é semeada com o
RAW 2272 REAL (`tests/fixtures/canario_1149/RAW-2272.html`, sha256 f2158520…), um derivado
antigo achatado (a `limpar()` do vivo, cópia literal em `provas/derivacao_estrutura/`) e a linha
da Sala pousada pelo dono. Então:

    · sem marca de cópia                  -> recusa, nada escrito
    · sem --aplicar                       -> nenhuma tabela muda (contagem E md5)
    · --aplicar                           -> derivado v4, pai = RAW 2272; PUBLISHED_AT 2026-06-22;
                                             T5 SIM; a Sala FUNDE por documento (0 linhas novas,
                                             versão 036 = IGUAL) e o recibo diz DONO NAO DEFINIDO
    · --aplicar outra vez                 -> REUSED, nada novo em derived_artifact
    · RAW sem identidade provada com linha -> PARA antes de `pousar` (não duplica)
"""
import hashlib
import importlib.util
import json
import os
import shutil
import socket
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

#: `provas/derivacao_estrutura/replay_acervo.py` arma o socket NO IMPORT (e o desenho dele: o
#: replay e o antes x depois da admissao correm sem rede). O banco descartavel deste teste precisa
#: de uma porta livre — o socket real volta depois de carregar os modulos.
_SOCKET_REAL = socket.socket
RAIZ = Path(__file__).resolve().parents[1]
for p in ("", "provas/canario_1149", "provas/derivacao_estrutura"):
    sys.path.insert(0, str(RAIZ / p))
import _gavetas                          # noqa: E402,F401

_spec = importlib.util.spec_from_file_location(
    "rederivar_um_raw", RAIZ / "provas" / "canario_1149" / "rederivar_um_raw.py")
R = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(R)

_spec = importlib.util.spec_from_file_location(
    "ensaio_offline", RAIZ / "scripts" / "micro_coleta" / "ensaio_offline.py")
E = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(E)

FIXTURE = RAIZ / "tests" / "fixtures" / "canario_1149" / "RAW-2272.html"
SHA = "f2158520f2362956756e31864406962e68ce6632206a4ce56e078e826a953d01"
CAMINHO_RAW = "XX/it-t5-111/OBSERVATION/f2158520f2362956-xylella.html"
TEM_PG = (E.PG_BIN / ("initdb.exe" if os.name == "nt" else "initdb")).exists() \
    and shutil.which("bash") and not (hasattr(os, "geteuid") and os.geteuid() == 0)


class ATravaSemBanco(unittest.TestCase):
    """Nenhuma destas moradas chega a abrir ligação."""

    def test_o_vivo_e_recusado_pela_morada(self):
        for dsn in ("postgresql://postgres@127.0.0.1:5432/sala_italia",
                    "postgresql://postgres@127.0.0.1:54330/sala_italia",
                    "postgresql://postgres@127.0.0.1/sala_italia",
                    "postgresql://postgres@db.x.supabase.co:54391/sala_italia",
                    "postgresql://postgres@127.0.0.1:54391/postgres",
                    "postgresql://postgres@127.0.0.1:54391/sala_italia?host=db.x.supabase.co",
                    "postgresql://postgres@127.0.0.1:54391/sala_italia?dbname=producao"):
            self.assertTrue(R.porque_nao_e_copia(dsn), dsn)

    def test_a_copia_do_coordenador_passa_a_morada(self):
        self.assertEqual(R.porque_nao_e_copia(
            "postgresql://postgres@127.0.0.1:54391/sala_italia"), "")
        self.assertEqual(R.porque_nao_e_copia(
            "postgresql://postgres@localhost:54329/descartavel"), "")

    def test_mutacao_apontado_ao_vivo_recusa_sem_ligar(self):
        """O runner apontado ao DSN «vivo» sai com 2 e o psql nunca é chamado."""
        pasta = tempfile.mkdtemp(prefix="c1149-trava-")
        try:
            with mock.patch("coleta_checkpoint.Banco.executa",
                            side_effect=AssertionError("ligou ao banco")):
                for dsn in ("postgresql://postgres@127.0.0.1:54330/sala_italia",
                            "postgresql://postgres@127.0.0.1:5432/sala_italia"):
                    self.assertEqual(R.main(["--dsn", dsn, "--raw-id", "2272",
                                             "--armazem", pasta, "--saida", pasta,
                                             "--aplicar"]), 2)
            self.assertEqual(os.listdir(pasta), [])
        finally:
            shutil.rmtree(pasta, ignore_errors=True)

    def test_o_armazem_da_copia_nao_pode_morar_no_original(self):
        pasta = tempfile.mkdtemp(prefix="c1149-trava-")
        try:
            with mock.patch("coleta_checkpoint.Banco.executa",
                            side_effect=AssertionError("ligou ao banco")):
                self.assertEqual(R.main(
                    ["--dsn", "postgresql://postgres@127.0.0.1:54391/sala_italia",
                     "--raw-id", "2272", "--armazem", pasta, "--saida", pasta + "-saida",
                     "--armazem-da-copia", os.path.join(pasta, "XX"), "--aplicar"]), 2)
        finally:
            shutil.rmtree(pasta, ignore_errors=True)
            shutil.rmtree(pasta + "-saida", ignore_errors=True)


_spec = importlib.util.spec_from_file_location(
    "admissao_antes_depois", RAIZ / "provas" / "canario_1149" / "admissao_antes_depois.py")
AD = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(AD)
socket.socket = _SOCKET_REAL


class OEfeitoNaAdmissao(unittest.TestCase):
    """`admissao_antes_depois.py`: a porta julga o texto antigo e o novo, no universo do contrato."""

    def setUp(self):
        self.armazem = Path(tempfile.mkdtemp(prefix="c1149-adm-"))
        self.addCleanup(shutil.rmtree, str(self.armazem), True)

    def _pagina(self, nome, dados):
        p = self.armazem / "XX" / "it-t5-111" / "OBSERVATION" / nome
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(dados)

    def test_o_raw_2272_nao_muda_de_decisao_em_T5(self):
        self._pagina("f2158520f2362956-xylella.html", FIXTURE.read_bytes())
        r = AD.medir(str(self.armazem))
        self.assertEqual((r["RESUMO"]["JULGADAS"], r["RESUMO"]["MUDARAM"]), (1, 0))
        p = r["POR_PAGINA"][0]
        self.assertEqual((p["SOURCE_ID"], p["UNIVERSO"]), ("IT-T5-111", "T5"))
        self.assertEqual((p["ANTES"]["RESULTADO"], p["DEPOIS"]["RESULTADO"]), ("SIM", "SIM"))
        self.assertIn("tesi", p["DEPOIS"]["PALAVRAS"])      # o DEFEITO A continua: «at-tesi»

    def test_mutacao_termo_que_atravessa_um_bloco_e_apanhado(self):
        """«prova di campo» partido por <li>: a limpar/1 juntava-o, a limpar/3 nao. SIM -> NAO_SEI."""
        self._pagina("0000-mutante.html", "<html><body><p>Una ricerca sul grano.</p><ul>"
                     "<li>prova</li><li>di campo</li></ul></body></html>".encode("utf-8"))
        r = AD.medir(str(self.armazem))
        self.assertEqual(r["RESUMO"]["SIM_PARA_OUTRA"], 1)
        s = r["SIM_PARA_OUTRA"][0]
        self.assertTrue(s["ANTES"].startswith("SIM") and "prova di campo" in s["ANTES"])
        self.assertTrue(s["DEPOIS"].startswith("NAO_SEI"))

    def test_pagina_sem_contrato_nao_e_julgada(self):
        p = self.armazem / "XX" / "cand-9999" / "OBSERVATION" / "x.html"
        p.parent.mkdir(parents=True)
        p.write_bytes(b"<p>ricerca e universita</p>")
        r = AD.medir(str(self.armazem))
        self.assertEqual((r["RESUMO"]["JULGADAS"], r["RESUMO"]["NAO_JULGADAS"]), (0, 1))


@unittest.skipUnless(TEM_PG, "sem Postgres portatil (~/orca/pgtmp), sem bash, ou a correr como "
                             "root (o postgres recusa): a prova da estrada nao correu")
class AEstradaNaCopia(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.pasta = Path(tempfile.mkdtemp(prefix="c1149-"))
        cls.base = E.Base(cls.pasta / "pg")
        assert ":54330/" not in cls.base.url, "isto e a Sala real"
        cls.env = {**os.environ, "PATH": str(E.PG_BIN) + os.pathsep + os.environ.get("PATH", "")}
        r = cls.base.subir(RAIZ, cls.env)
        if r["CODIGO"] != 0:
            cls.base.descer()
            raise unittest.SkipTest("migrations falharam: %s" % r["ERRO"])
        cls._amb = dict(os.environ)
        try:
            os.environ["SINTONIA_PSQL_EXE"] = cls.base.exe("psql")
            cls.armazem = cls.pasta / "armazem-original"
            (cls.armazem / CAMINHO_RAW).parent.mkdir(parents=True)
            shutil.copyfile(FIXTURE, cls.armazem / CAMINHO_RAW)
            cls.semear()
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
    def sql(cls, comando):
        r = subprocess.run([cls.base.exe("psql"), "-X", "-q", "-A", "-t", "-v", "ON_ERROR_STOP=1",
                            "-f", "-", cls.base.url], input=comando, capture_output=True,
                           text=True, encoding="utf-8")
        assert r.returncode == 0, r.stderr
        return r.stdout.strip()

    @classmethod
    def semear(cls, raw_id=2272, caminho=CAMINHO_RAW, identidade="FORWARD_IDENTIFIED",
               corrida="IT-T5-2026-09-28-112058-aacf19302d12b1b0", marca=True):
        """O estado da cópia: o RAW real, o derivado antigo achatado, a linha da Sala."""
        import replay_acervo as RA
        if marca:
            cls.sql("create table public._copia_descartavel (marcada_em timestamptz not null "
                    "default now(), origem text not null); insert into public._copia_descartavel "
                    "(origem) values ('teste: Postgres descartavel do unittest');")
        dados = FIXTURE.read_bytes()
        cls.sql("insert into collection_run (run_id, platform, started_at, rule_version, "
                "source_country) values ('%s', 'HTTP', now(), 'v1', 'IT') "
                "on conflict (run_id) do nothing;" % corrida)
        cls.sql("insert into storage_object (storage_path, media_type, bytes, sha256) values "
                "('%s', 'text/html', %d, '%s');" % (caminho, len(dados), SHA))
        cls.sql("insert into raw_asset (id, run_id, storage_path, storage_object_id, media_type, "
                "bytes, sha256, captured_at, source_url, source_id, document_key, "
                "document_key_basis, identity_state, preserved) select %d, '%s', '%s', o.id, "
                "'text/html', %d, '%s', '2026-09-28T11:20:58Z', "
                "'https://www.crea.gov.it/-/xylella-fastidiosa', 'IT-T5-111', %s, %s, '%s', true "
                "from storage_object o where o.storage_path = '%s';"
                % (raw_id, corrida, caminho, len(dados), SHA,
                   "'IT-T5-111:URL:-/xylella-fastidiosa'" if identidade == "FORWARD_IDENTIFIED"
                   else "null", "'SOURCE_DOCUMENT_ID'" if identidade == "FORWARD_IDENTIFIED"
                   else "null", identidade, caminho))
        # o derivado ANTIGO: a limpar() do vivo (achatada), receita «texto-de-html 2»
        antigo = RA.limpar_antes(dados, "text/html")
        sha_a = hashlib.sha256(antigo.encode("utf-8")).hexdigest()
        onde = "DERIVED/IT/antigo-%d.txt" % raw_id
        (cls.armazem / onde).parent.mkdir(parents=True, exist_ok=True)
        (cls.armazem / onde).write_bytes(antigo.encode("utf-8"))
        der = int(cls.sql(
            "insert into derived_artifact (raw_asset_id, parent_sha256, kind, producer, "
            "producer_version, pipeline_version, parameters_hash, sha256, bytes, media_type, "
            "storage_path, derived_at) values (%d, '%s', 'TEXT_EXTRACTION', 'texto-de-html', "
            "'2', '1', '%s', '%s', %d, 'text/plain', '%s', now()) returning id;"
            % (raw_id, SHA, "b" * 64 if raw_id == 2272 else "c" * 64, sha_a,
               len(antigo.encode("utf-8")), onde)).split("\n")[0])
        # a linha da Sala, pousada pelo DONO, com o item da rota documental
        import admissao as adm
        import orquestrador as ORQ
        import sala_de_espera as espera
        os.environ.update({"SINTONIA_SALA_BACKEND": "POSTGRES", "SINTONIA_SALA_DSN": cls.base.url})
        est = {"SOURCE_ID": "IT-T5-111", "TEXTO": antigo, "DERIVED_ARTIFACT_ID": der,
               "RAW_ASSET_ID": raw_id, "PARENT_SHA256": SHA,
               "CAPTURED_AT": "2026-09-28T11:20:58Z", "TEMPO_E_LUGAR": {}}
        item = ORQ.item_documental_para_a_porta(est, source_id="IT-T5-111")
        d = adm.decidir(item, "T5", corrida=corrida)
        assert d.resultado == adm.SIM, d.motivo
        assert espera.pousar(corrida, [adm.pronto_para_inteligencia(item, d)])["ESTADO"] \
            == espera.POUSOU
        return der

    def impressao(self):
        """md5 de cada tabela (linhas ordenadas): contagem igual nao e conteudo igual."""
        return {t: self.sql("select count(*)::text || ':' || md5(coalesce(string_agg(x::text, "
                            "'|' order by x::text), '')) from public.%s x" % t)
                for t in R.TABELAS}

    def correr(self, *extra, raw_id=2272):
        saida = tempfile.mkdtemp(prefix="saida-", dir=str(self.pasta))
        codigo = R.main(["--dsn", self.base.url, "--raw-id", str(raw_id), "--armazem",
                         str(self.armazem), "--saida", saida,
                         "--armazem-da-copia", str(self.pasta / "armazem-da-copia")] + list(extra))
        nome = [f for f in os.listdir(saida) if f.startswith("REDERIVAR-")]
        recibo = json.loads(Path(saida, nome[0]).read_text(encoding="utf-8")) if nome else None
        return codigo, recibo, saida

    def test_1_sem_marca_de_copia_recusa(self):
        self.sql("alter table public._copia_descartavel rename to _sem_marca;")
        try:
            antes = self.impressao()
            codigo, recibo, _ = self.correr("--aplicar")
            self.assertEqual((codigo, recibo), (2, None))
            self.assertEqual(self.impressao(), antes)
        finally:
            self.sql("alter table public._sem_marca rename to _copia_descartavel;")

    def test_1b_marca_de_copia_vazia_recusa(self):
        self.sql("create table public._marca_guardada as select * from public._copia_descartavel; "
                 "delete from public._copia_descartavel;")
        try:
            antes = self.impressao()
            codigo, recibo, _ = self.correr("--aplicar")
            self.assertEqual((codigo, recibo), (2, None))
            self.assertEqual(self.impressao(), antes)
        finally:
            self.sql("insert into public._copia_descartavel select * from public._marca_guardada; "
                     "drop table public._marca_guardada;")

    def test_2_sem_aplicar_nao_escreve_nada(self):
        antes = self.impressao()
        original = sorted(str(p) for p in self.armazem.rglob("*"))
        codigo, recibo, saida = self.correr()
        self.assertEqual(codigo, 0)
        self.assertEqual(self.impressao(), antes)
        self.assertEqual(sorted(str(p) for p in self.armazem.rglob("*")), original)
        self.assertFalse(os.path.exists(self.pasta / "armazem-da-copia"))
        self.assertTrue(recibo["ESTADO"].startswith("SO_PREVISAO"))
        self.assertEqual(recibo["DERIVACAO_PREVISTA"]["producer_version"], "4")
        self.assertIn("NAO_EXISTE", recibo["DERIVACAO_PREVISTA"]["NA_COPIA"])
        self.assertEqual(recibo["SALA_PREVISTA"]["VERSAO_036"]["ESTADO"], "IGUAL")
        self.assertEqual(recibo["COMPARACAO"]["DECISAO_ANTIGO"]["RESULTADO"], "SIM")

    def test_3_aplicar_deriva_v4_e_a_sala_funde_por_documento(self):
        linhas_sala = self.sql("select count(*) from sala_de_espera")
        original = sorted(str(p) for p in self.armazem.rglob("*"))
        codigo, r, saida = self.correr("--aplicar")
        self.assertEqual(codigo, 0, r and r.get("ESTADO"))
        self.assertEqual(r["ESTADO"], "APLICADO_NA_COPIA")
        # o derivado novo: versao 4, pai = RAW 2272, sha do texto que ficou guardado
        dn = r["DERIVADO_NOVO"]
        self.assertEqual((dn["PORTA"], dn["PRODUCER_VERSION"], str(dn["PAI_RAW_ASSET_ID"]),
                          dn["PARENT_SHA256"]), ("PASSED", "4", "2272", SHA))
        guardado = Path(self.pasta, "armazem-da-copia", dn["STORAGE_PATH"]).read_bytes()
        self.assertEqual(hashlib.sha256(guardado).hexdigest(), dn["SHA256"])
        self.assertGreater(r["TEXTO_DERIVADO"]["LINHAS"], 40)
        self.assertEqual(len(r["TEXTO_DERIVADO"]["PRIMEIRAS_40_LINHAS"]), 40)
        # a publicacao, pelo leitor da pagina (content-date), precisao DIA
        f = r["CAMPOS_DO_FATO"]
        self.assertEqual((f["PUBLISHED_AT"], f["PUBLISHED_AT_PRECISION"]), ("2026-06-22", "DIA"))
        self.assertIn("content-date", f["PUBLISHED_AT_BASIS"])
        self.assertNotEqual(f["FACT_TIME"], "2026-06-22")    # publicacao nao vira fact time
        # a porta: T5, com as palavras e a regua
        self.assertEqual((r["ADMISSAO"]["UNIVERSO"], r["ADMISSAO"]["RESULTADO"]), ("T5", "SIM"))
        self.assertTrue(r["ADMISSAO"]["PALAVRAS"])
        self.assertIn("ricerca", r["ADMISSAO"]["A_REGUA"]["PERGUNTAS_DO_UNIVERSO"])
        # a Sala: FUNDIU por documento — nenhuma linha nova, nenhuma versao nova
        s = r["SALA"]
        self.assertEqual(s["RECIBO"]["ESTADO"], "REUSED")
        self.assertEqual(s["RECIBO"]["INSERIDAS"], 0)
        self.assertTrue(s["VEREDITO"].startswith("FUNDIDO_POR_DOCUMENTO"))
        self.assertEqual([v["ESTADO"] for v in s["RECIBO"]["VERSOES"]], ["IGUAL"])
        self.assertIn("bytes do RAW iguais", s["RECIBO"]["VERSOES"][0]["MOTIVO"])
        self.assertEqual(s["DONO_DO_CAMINHO_PARA_TEXTO_NOVO"], "NAO DEFINIDO")
        self.assertEqual(self.sql("select count(*) from sala_de_espera"), linhas_sala)
        # o que se escreveu: uma corrida marcada, um derivado, um documento estruturado
        self.assertEqual((r["ESCREVEU"]["collection_run"], r["ESCREVEU"]["derived_artifact"],
                          r["ESCREVEU"]["sala_de_espera"], r["ESCREVEU"]["raw_asset"]),
                         (1, 1, 0, 0))
        self.assertEqual(self.sql("select mission || '|' || status from collection_run "
                                  "where run_id = '%s'" % r["CORRIDA"]["RUN_ID"]),
                         "REPROCESSO_CANARIO_1149|concluida")
        # o armazem original so foi LIDO
        self.assertEqual(sorted(str(p) for p in self.armazem.rglob("*")), original)

    def test_4_aplicar_outra_vez_reaproveita(self):
        derivados = self.sql("select count(*) from derived_artifact")
        codigo, r, _ = self.correr("--aplicar")
        self.assertEqual(codigo, 0, r and r.get("ESTADO"))
        self.assertEqual(r["DERIVADO_NOVO"]["PORTA"], "REUSED")
        self.assertEqual(self.sql("select count(*) from derived_artifact"), derivados)
        self.assertEqual(r["ESCREVEU"]["sala_de_espera"], 0)

    def test_5_raw_sem_identidade_provada_para_antes_de_duplicar(self):
        """Mutação: sem FORWARD_IDENTIFIED a DEDUP-DOC não funde, e `pousar` gravaria uma 2.ª
        linha do MESMO bruto. O runner PARA antes de a chamar."""
        caminho = CAMINHO_RAW.replace("xylella", "xylella-sem-identidade")
        shutil.copyfile(FIXTURE, self.armazem / caminho)
        self.semear(raw_id=2273, caminho=caminho, identidade="FORWARD_IDENTITY_UNPROVEN",
                    corrida="IT-T5-2026-09-28-SEM-IDENTIDADE", marca=False)
        linhas = self.sql("select count(*) from sala_de_espera")
        codigo, r, _ = self.correr("--aplicar", raw_id=2273)
        self.assertEqual(codigo, 3)
        self.assertTrue(r["ESTADO"].startswith("PARADO"))
        self.assertEqual(r.get("SALA", {}).get("ESTADO"), "NAO_CHAMADA", r["ESTADO"])
        self.assertEqual(r["SALA"]["DONO_DO_CAMINHO"], "NAO DEFINIDO")
        self.assertEqual(self.sql("select count(*) from sala_de_espera"), linhas)
        self.assertEqual(self.sql("select status from collection_run where run_id = '%s'"
                                  % r["CORRIDA"]["RUN_ID"]), "parcial")


if __name__ == "__main__":
    unittest.main(verbosity=2)
