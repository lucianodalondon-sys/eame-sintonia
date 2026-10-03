# -*- coding: utf-8 -*-
"""QUATRO-CHAVES-V2 — a Sala lê e escreve cada coluna PELO NOME.

AVISO da INSTALAÇÃO-2 (25/09): a leitura do backend Postgres era POSICIONAL
(`c[18]`, `c[19]`, `c[20]`, `c[21]`, e a nuvem acrescentava `c[22]`), e a escrita
eram duas listas paralelas — nomes num sítio, valores noutro. Juntar duas
linhas que acrescentam colunas obrigava a renumerar, e um índice errado NÃO dá
erro: lê ou grava a coluna vizinha em silêncio.

Estes testes não precisam de banco: substituem `_consultar`/`_executar` e
conferem que cada campo volta da SUA coluna e que cada valor vai para a SUA.
EXCEÇÃO (D90, INTEGRA-NOITE lote 3): `AEscritaEPeloNomeNoLivroDeMigracoesReal` liga um Postgres
descartável (PESADO: só com a LOCK-PESADO) para perguntar ao livro de migrações real pela 036.
"""
import json
import os
import re
import sys
import unittest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path[:0] = [os.path.join(RAIZ, "admissao"), RAIZ]

import sala_de_espera as S  # noqa: E402

# campo do READY -> coluna da Sala (o que `ler()` tem de respeitar)
CAMPO_DA_COLUNA = {
    "item_id": "ITEM_ID", "universo": "UNIVERSO", "texto": "TEXTO",
    "source_id": "SOURCE_ID", "source_location": "SOURCE_LOCATION",
    "fact_location": "FACT_LOCATION", "fact_time": "FACT_TIME",
    "captured_at": "CAPTURED_AT", "admitido_por": "ADMITIDO_POR",
    "estagio": "ESTAGIO", "fact_time_basis": "FACT_TIME_BASIS",
    "fact_location_basis": "FACT_LOCATION_BASIS", "published_at": "PUBLISHED_AT",
    "observed_at": "OBSERVED_AT",
    "source_declared_evidence_class": "SOURCE_DECLARED_EVIDENCE_CLASS",
    "published_at_basis": "PUBLISHED_AT_BASIS",
    "source_location_basis": "SOURCE_LOCATION_BASIS",
}
JSONS = {"fato": "FATO", "completude_tempo_lugar": "COMPLETUDE_TEMPO_LUGAR",
         "tempo_lugar_evidencia": "TEMPO_LUGAR_EVIDENCIA",
         "janela_declarada": "JANELA_DECLARADA"}


def _pg():
    b = S._Postgres.__new__(S._Postgres)      # sem ligar a banco nenhum
    return b


class ALeituraEPeloNome(unittest.TestCase):

    def _linha(self):
        vals = []
        for c in S.COLUNAS_LIDAS:
            if c == "ordem":
                vals.append("0")
            elif c == "raw_observation_id":
                vals.append("77")
            elif c in JSONS:
                vals.append(json.dumps({"MARCA": c}))
            else:
                vals.append("MARCA-" + c)
        return vals

    def test_cada_campo_volta_da_sua_coluna(self):
        b = _pg()
        pedido = {}

        def consultar(sql):
            pedido["sql"] = sql
            return [b.SEP.join(self._linha())]
        b._consultar = consultar
        item = b.ler("RUN-X")["ITENS"][0]
        for coluna, campo in CAMPO_DA_COLUNA.items():
            self.assertEqual(item[campo], "MARCA-" + coluna, campo)
        for coluna, campo in JSONS.items():
            self.assertEqual(item[campo], {"MARCA": coluna}, campo)
        self.assertEqual(item["RAW_OBSERVATION_ID"], 77)
        self.assertEqual(item["CORRIDA"], "RUN-X")
        # o select nasce da MESMA lista que a leitura usa
        self.assertIn("select " + ", ".join(S.COLUNAS_LIDAS) + " ", pedido["sql"])

    def test_numero_de_valores_errado_rebenta(self):
        b = _pg()
        b._consultar = lambda sql: [b.SEP.join(self._linha()[:-1])]
        with self.assertRaises(S.SalaIndisponivel):
            b.ler("RUN-X")

    def test_nenhuma_leitura_posicional_em_ler(self):
        import inspect
        codigo = re.sub(r"#.*", "", inspect.getsource(S._Postgres.ler))
        self.assertIsNone(re.search(r"c\[\d+\]", codigo))


class AEscritaEPeloNome(unittest.TestCase):

    def _unidade(self):
        u = {c: "MARCA-" + c for c in S.CAMPOS_READY}
        u["RAW_OBSERVATION_ID"] = 5
        for campo in ("FATO", "COMPLETUDE_TEMPO_LUGAR", "TEMPO_LUGAR_EVIDENCIA",
                      "JANELA_DECLARADA"):
            u[campo] = "J-" + campo
        return u

    def _script(self):
        b = _pg()
        visto = {}

        def executar(script):
            visto["s"] = script
            return 0, "%s:1:0" % S.POUSOU, ""
        b._executar = executar
        # DEDUP-DOC (036): o `pousar` pergunta primeiro ao banco se o caderno de versoes existe.
        # Aqui nao ha banco: responde-se «036 nao aplicada» (DA-20, 2 — o lote 3 funciona sem a 036).
        # O que este teste mede — cada valor na SUA coluna, as 3 listas iguais — nao muda. D90: a MESMA
        # conferencia corre com a pergunta respondida pelo livro de migracoes REAL em
        # `AEscritaEPeloNomeNoLivroDeMigracoesReal` (Postgres descartavel sem a 036).
        b._consultar = lambda sql: ["f"]
        b.pousar("RUN-Y", [self._unidade()])
        return visto["s"]

    def test_cada_valor_vai_para_a_sua_coluna(self):
        s = self._script()
        m = re.search(r"insert into _entrada\s*\(([^)]*)\)\s*values\s*\((.*?)\);", s, re.S)
        self.assertTrue(m, "nao achei o insert em _entrada")
        nomes = [n.strip() for n in m.group(1).split(",")]
        valores = [v.strip() for v in re.split(r",\s(?=(?:[^']*'[^']*')*[^']*$)", m.group(2))]
        self.assertEqual(nomes, list(S.COLUNAS_ESCRITAS))
        self.assertEqual(len(valores), len(nomes))
        par = dict(zip(nomes, valores))
        self.assertEqual(par["run_id"], "'RUN-Y'")
        self.assertEqual(par["raw_observation_id"], "5")
        self.assertEqual(par["published_at_basis"], "'MARCA-PUBLISHED_AT_BASIS'")
        self.assertEqual(par["source_location_basis"], "'MARCA-SOURCE_LOCATION_BASIS'")
        self.assertEqual(par["janela_declarada"], "'\"J-JANELA_DECLARADA\"'")
        self.assertEqual(par["tempo_lugar_evidencia"], "'\"J-TEMPO_LUGAR_EVIDENCIA\"'")
        self.assertEqual(par["fato"], "'\"J-FATO\"'")

    def test_as_tres_listas_de_colunas_sao_a_mesma(self):
        s = self._script()
        lista = ", ".join(S.COLUNAS_ESCRITAS)
        self.assertEqual(s.count(lista), 3)   # _entrada, insert na Sala, select

    def test_as_colunas_lidas_existem_nas_escritas_ou_sao_da_sala(self):
        self.assertLessEqual(set(S.COLUNAS_LIDAS) - {"ordem"}, set(S.COLUNAS_ESCRITAS))
        self.assertIn("janela_declarada", S.COLUNAS_LIDAS)
        self.assertIn("janela_declarada", S.COLUNAS_ESCRITAS)


class SemA036OPousarContinuaAPousar(unittest.TestCase):
    """DA-20 (3): a 036 nao entra no lote 3 (vai pela MIGRACOES-EM-SERIE, DA-19) — o lote 3 tem de
    funcionar com ela AUSENTE. Sem o caderno de versoes o `pousar` escreve como antes, nao fala da
    tabela que nao existe, e diz no relato porque nao ha versoes."""

    def _pousar(self, tem_036):
        b = _pg()
        visto = {"perguntas": []}

        def consultar(sql):
            visto["perguntas"].append(sql)
            return ["t" if tem_036 else "f"] if "to_regclass" in sql else []

        def executar(script):
            visto["s"] = script
            return 0, "%s:1:0" % S.POUSOU, ""
        b._consultar, b._executar = consultar, executar
        u = AEscritaEPeloNome._unidade(AEscritaEPeloNome())
        visto["estado"] = b.pousar("RUN-SEM-036", [u])
        visto["relato"] = b.ultimas_versoes
        return visto

    def test_sem_a_036_pousa_e_nao_toca_na_tabela_que_nao_existe(self):
        v = self._pousar(tem_036=False)
        self.assertEqual(v["estado"], S.POUSOU)
        self.assertIn("insert into public.sala_de_espera", v["s"])
        self.assertNotIn("sala_de_espera_versao", v["s"])
        self.assertEqual(len(v["perguntas"]), 1)                 # so a pergunta «a 036 existe?»
        self.assertIn("036 nao aplicada", v["relato"][0]["MOTIVO"])

    def test_contraprova_com_a_036_o_pousar_procura_o_documento(self):
        v = self._pousar(tem_036=True)
        self.assertEqual(v["estado"], S.POUSOU)
        self.assertGreater(len(v["perguntas"]), 1)              # pergunta pelo documento, unidade a unidade


import importlib.util  # noqa: E402
import shutil  # noqa: E402
import subprocess  # noqa: E402
import tempfile  # noqa: E402
from pathlib import Path  # noqa: E402

_spec = importlib.util.spec_from_file_location(
    "ensaio_offline", os.path.join(RAIZ, "scripts", "micro_coleta", "ensaio_offline.py"))
E = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(E)
TEM_PG = (E.PG_BIN / ("initdb.exe" if os.name == "nt" else "initdb")).exists() and shutil.which("bash")
A036 = "036_a_sala_guarda_as_versoes_do_documento.sql"


@unittest.skipUnless(TEM_PG, "sem Postgres portatil (~/orca/pgtmp) ou sem bash: a prova nao correu")
class AEscritaEPeloNomeNoLivroDeMigracoesReal(AEscritaEPeloNome):
    """D90 (bot Luciano, 26/09 19:50): os 2 testes da escrita por nome nao podem so RESPONDER «036 nao
    aplicada» — perguntam ao esquema e ao livro de migracoes REAIS e provam que o codigo funciona com a
    036 AUSENTE (DA-20 3: a 036 vai pela MIGRACOES-EM-SERIE, DA-19).

    Postgres descartavel com as migrations pela cadeia canonica (`motor/cadeia_canonica.sh`) a partir de
    uma arvore com TODAS as migrations do ramo menos a 036 — o `schema_migracao` e o que a cadeia escreveu.
    Os testes herdados (`test_cada_valor_vai_para_a_sua_coluna`, `test_as_tres_listas_de_colunas_sao_a_mesma`)
    correm aqui com a pergunta «a 036 existe?» respondida pelo BANCO."""

    @classmethod
    def setUpClass(cls):
        cls.pasta = Path(tempfile.mkdtemp(prefix="sala-sem-036-"))
        arvore = cls.pasta / "arvore"
        (arvore / "motor").mkdir(parents=True)
        (arvore / "supabase" / "migrations").mkdir(parents=True)
        shutil.copy2(os.path.join(RAIZ, "motor", "cadeia_canonica.sh"), arvore / "motor")
        cls.fora = []
        for f in sorted(Path(RAIZ, "supabase", "migrations").glob("*.sql")):
            if f.name == A036:
                cls.fora.append(f.name)
                continue
            shutil.copy2(f, arvore / "supabase" / "migrations")
        cls.base = E.Base(cls.pasta / "pg")
        env = {**os.environ, "PATH": str(E.PG_BIN) + os.pathsep + os.environ.get("PATH", "")}
        r = cls.base.subir(arvore, env)
        if r["CODIGO"] != 0:
            cls.base.descer()
            shutil.rmtree(cls.pasta, ignore_errors=True)
            raise unittest.SkipTest("migrations falharam: %s" % r["ERRO"])
        cls._amb = dict(os.environ)
        try:
            os.environ.update({"SINTONIA_SALA_BACKEND": "POSTGRES", "SINTONIA_SALA_DSN": cls.base.url,
                               "SINTONIA_PSQL_EXE": cls.base.exe("psql")})
            cls.sql("insert into collection_run (run_id, platform, started_at, rule_version) values "
                    "('SEM036-A', 'teste', now(), 'teste'), ('SEM036-B', 'teste', now(), 'teste')")
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
        r = subprocess.run([cls.base.exe("psql"), "-X", "-At", "-v", "ON_ERROR_STOP=1",
                            "-c", comando, cls.base.url], capture_output=True, text=True, check=True)
        return r.stdout.strip()

    def _script(self):
        """Como o pai, mas a pergunta ao banco vai ao BANCO: so a escrita e apanhada (o insert leva um
        RAW_OBSERVATION_ID de marca, que nao existe em raw_asset)."""
        b = S._Postgres(self.base.url)
        visto = {"perguntas": []}
        consultar_real = b._consultar

        def consultar(sql):
            visto["perguntas"].append(sql)
            return consultar_real(sql)

        def executar(script):
            visto["s"] = script
            return 0, "%s:1:0" % S.POUSOU, ""
        b._consultar, b._executar = consultar, executar
        b.pousar("RUN-Y", [self._unidade()])
        self.visto = dict(visto, relato=b.ultimas_versoes)
        return visto["s"]

    def test_o_livro_de_migracoes_real_nao_tem_a_036(self):
        self.assertEqual(self.fora, [A036])                       # a 036 do ramo ficou mesmo de fora
        self.assertEqual(self.sql("select count(*) from public.schema_migracao where versao = '036'"), "0")
        self.assertEqual(self.sql("select count(*) from public.schema_migracao where versao = '033'"), "1")
        self.assertEqual(self.sql("select to_regclass('public.sala_de_espera_versao') is null"), "t")

    def test_o_banco_responde_que_a_036_nao_esta_e_o_pousar_nao_a_toca(self):
        s = self._script()
        self.assertEqual(len(self.visto["perguntas"]), 1)         # so «a 036 existe?», e o banco disse nao
        self.assertIn("036 nao aplicada", self.visto["relato"][0]["MOTIVO"])
        self.assertNotIn("sala_de_espera_versao", s)

    def test_pousar_de_verdade_sem_a_036(self):
        """Ponta a ponta, sem nada substituido: um bruto real, o READY da porta, `pousar` pelo modulo."""
        import admissao as A
        raw = int(self.sql(
            "insert into raw_asset (run_id, storage_path, media_type, bytes, sha256, captured_at, preserved, "
            "not_preserved_reason, source_id, document_key, document_key_basis, identity_state) values "
            "('SEM036-B', 'teste/sem036', 'text/html', 1, '%s', now(), false, 'teste sem copia', 'IT-T5-025', "
            "'IT-T5-025:URL:sem036', 'SOURCE_DOCUMENT_ID', 'FORWARD_IDENTIFIED') returning id" % ("c" * 64)
        ).splitlines()[0])
        item = {"id": "derived:sem036", "texto": "Ensaio de campo publicado com DOI sem036",
                "source_id": "IT-T5-025", "fact_time": "2026-05-02"}
        u = A.pronto_para_inteligencia(item, A.decidir(item, "T5", corrida="R"))
        u = dict(u, ITEM_ID="derived:sem036", UNIVERSO="T5", RAW_OBSERVATION_ID=raw, SOURCE_ID="IT-T5-025")
        r = S.pousar("SEM036-B", [u])
        self.assertEqual(r["INSERIDAS"], 1)
        self.assertIn("036 nao aplicada", r["VERSOES"][0]["MOTIVO"])
        self.assertEqual(self.sql("select count(*) from sala_de_espera where item_id = 'derived:sem036'"), "1")
        self.assertEqual(self.sql("select to_regclass('public.sala_de_espera_versao') is null"), "t")


class OsPendentesSaoPeloNome(unittest.TestCase):
    """`listar_pendentes` lia `c[0]`, `c[1]`, `c[2]` (QUATRO-CHAVES-MEDIR, 26/09)."""

    def _listar(self, linha):
        b = _pg()
        pedido = {}

        def consultar(sql):
            pedido["sql"] = sql
            return [b.SEP.join(linha)]
        b._consultar = consultar
        return b.listar_pendentes(), pedido["sql"]

    def test_cada_chave_volta_da_sua_coluna(self):
        vals = {"run_id": "RUN-P", "ordem": "7", "item_id": "derived:p-1"}
        fora, sql = self._listar([vals[c] for c, _ in S.COLUNAS_PENDENTES])
        self.assertEqual(fora, [{"RUN_ID": "RUN-P", "ORDEM": 7, "ITEM_ID": "derived:p-1"}])
        self.assertIn("select " + ", ".join(c for c, _ in S.COLUNAS_PENDENTES) + " from", sql)

    def test_numero_de_valores_errado_rebenta(self):
        b = _pg()
        b._consultar = lambda sql: [b.SEP.join(["RUN-P", "7"])]
        with self.assertRaises(S.SalaIndisponivel):
            b.listar_pendentes()

    def test_nenhuma_leitura_posicional_em_listar_pendentes(self):
        import inspect
        codigo = re.sub(r"#.*", "", inspect.getsource(S._Postgres.listar_pendentes))
        self.assertIsNone(re.search(r"\w\[\d+\]", codigo))


if __name__ == "__main__":
    unittest.main()
