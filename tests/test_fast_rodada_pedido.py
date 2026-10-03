# -*- coding: utf-8 -*-
"""MODO PEDIDO da rodada FAST (`--pedido`): a captura que responde a UM EVIDENCE_REQUEST.

O que se prova aqui, sem banco e sem LLM:
 - o pedido e conferido (CASE_ID, EVIDENCE_REQUEST_ID, RAW nomeado) -- e recusado quando falta
   qualquer um deles, porque uma captura sem pedido nao pode ser incorporada pelo `fast_casos`;
 - a rodada fica ESCOPADA aos RAW que o pedido nomeia (nada de "mais novo primeiro");
 - um RAW que nao existe recusa a rodada inteira (referencia quebrada nao chega a nascer);
 - o `PEDIDO.json` e carimbado DENTRO da pasta da rodada, que e o elo exigido na incorporacao;
 - a rodada pedida NAO usa `candidatos()` (a selecao do ciclo das 2 h).
"""
import importlib.util
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)

spec = importlib.util.spec_from_file_location("rodada_fast_pedido", os.path.join(RAIZ, "motor", "fast_auto", "rodada_fast.py"))
RF = importlib.util.module_from_spec(spec)
spec.loader.exec_module(RF)


def _escrever(tmp, obj):
    p = os.path.join(tmp, "PEDIDO.json")
    Path(p).write_text(json.dumps(obj), encoding="utf-8")
    return p


def _pedido(**kw):
    d = {"CASE_ID": "CASE-001", "EVIDENCE_REQUEST_ID": "ER-CASE-001-FONTE_OFICIAL", "RAW_ASSET_IDS": [7, 3],
         "SOURCE_CONTRACT_ID": "SC-CASE-001-0001", "SOURCE_ID": "S-A"}
    d.update(kw)
    return d


class PedidoConferido(unittest.TestCase):
    def test_pedido_completo_passa_e_conserva_o_que_veio(self):
        with tempfile.TemporaryDirectory() as t:
            d = _pedido(escopo="mais", pergunta_it="Quali valori?")
            self.assertEqual(RF.ler_pedido(_escrever(t, d))["RAW_ASSET_IDS"], [7, 3])

    def test_ficheiro_inexistente_recusa(self):
        with tempfile.TemporaryDirectory() as t:
            with self.assertRaises(RF.PedidoInvalido):
                RF.ler_pedido(os.path.join(t, "nao-existe.json"))

    def test_sem_case_id_ou_mal_formado_recusa(self):
        with tempfile.TemporaryDirectory() as t:
            for valor in (None, "", "001", "CASO-001", "CASE-1"):
                with self.assertRaises(RF.PedidoInvalido):
                    RF.ler_pedido(_escrever(t, _pedido(CASE_ID=valor)))

    def test_sem_evidence_request_id_recusa(self):
        with tempfile.TemporaryDirectory() as t:
            for valor in (None, "", "FONTE_OFICIAL", "ER-"):
                with self.assertRaises(RF.PedidoInvalido):
                    RF.ler_pedido(_escrever(t, _pedido(EVIDENCE_REQUEST_ID=valor)))

    def test_raw_ausente_vazio_repetido_ou_nao_inteiro_recusa(self):
        with tempfile.TemporaryDirectory() as t:
            for valor in (None, [], [7, 7], ["7"], [0], [-3], [1.5]):
                with self.assertRaises(RF.PedidoInvalido):
                    RF.ler_pedido(_escrever(t, _pedido(RAW_ASSET_IDS=valor)))

    def test_ficheiro_ilegivel_recusa(self):
        with tempfile.TemporaryDirectory() as t:
            p = os.path.join(t, "PEDIDO.json")
            Path(p).write_text("{nao e json", encoding="utf-8")
            with self.assertRaises(RF.PedidoInvalido):
                RF.ler_pedido(p)


class RodadaEscopada(unittest.TestCase):
    def setUp(self):
        self._orig = RF.linhas_banco

    def tearDown(self):
        RF.linhas_banco = self._orig

    def test_escopa_aos_raw_do_pedido_sem_alternar_fonte(self):
        # banco devolve os 2 RAW nomeados (da MESMA fonte), fora de ordem: a rodada pedida
        # usa exatamente esses 2 -- a regra do ciclo (alternar fonte / mais novo primeiro) nao vale aqui.
        RF.linhas_banco = lambda sql: [{"id": 7, "source_id": "S-A", "captured_at": "x"},
                                       {"id": 3, "source_id": "S-A", "captured_at": "x"}]
        self.assertEqual([r["id"] for r in RF.raws_do_pedido(_pedido())], [3, 7])

    def test_raw_fora_do_pedido_recusa_a_rodada(self):
        # contraprova: se vier RAW que o pedido nao nomeia, recusa-se -- a rodada nao se estreita em silencio
        RF.linhas_banco = lambda sql: [{"id": 3, "source_id": "S-A", "captured_at": "x"},
                                       {"id": 7, "source_id": "S-A", "captured_at": "x"},
                                       {"id": 9, "source_id": "S-B", "captured_at": "x"}]
        with self.assertRaises(RF.PedidoInvalido):
            RF.raws_do_pedido(_pedido())

    def test_raw_inexistente_recusa_a_rodada(self):
        RF.linhas_banco = lambda sql: [{"id": 3, "source_id": "S-A", "captured_at": "x"}]
        with self.assertRaises(RF.PedidoInvalido):
            RF.raws_do_pedido(_pedido())

    def test_a_pedido_nao_usa_a_selecao_do_ciclo(self):
        def ciclo(*a, **k):
            raise AssertionError("candidatos() nao pode ser usado numa rodada pedida")

        class _Marcador(Exception):
            pass

        orig_cand, orig_raws, orig = RF.candidatos, RF.raws_do_pedido, RF.RAIZ
        RF.candidatos = ciclo
        RF.raws_do_pedido = lambda ped: (_ for _ in ()).throw(_Marcador())
        try:
            with tempfile.TemporaryDirectory() as t:
                RF.RAIZ, RF.LOG, RF.FEITOS = t, os.path.join(t, "RODADAS.log"), os.path.join(t, "FEITOS.txt")
                argv = sys.argv
                sys.argv = ["rodada_fast.py", "--pedido", _escrever(t, _pedido())]
                try:
                    with self.assertRaises(_Marcador):
                        RF.main()
                finally:
                    sys.argv = argv
        finally:
            RF.candidatos, RF.raws_do_pedido, RF.RAIZ = orig_cand, orig_raws, orig

    def test_pedido_invalido_sai_com_codigo_2_e_nao_cria_rodada(self):
        RF.linhas_banco = self._orig
        with tempfile.TemporaryDirectory() as t:
            antes = set(os.listdir(t))
            orig = RF.RAIZ, RF.LOG, RF.FEITOS
            RF.RAIZ, RF.LOG, RF.FEITOS = t, os.path.join(t, "RODADAS.log"), os.path.join(t, "FEITOS.txt")
            argv = sys.argv
            sys.argv = ["rodada_fast.py", "--pedido", _escrever(t, _pedido(EVIDENCE_REQUEST_ID=None))]
            try:
                with self.assertRaises(SystemExit) as e:
                    RF.main()
            finally:
                sys.argv = argv
                RF.RAIZ, RF.LOG, RF.FEITOS = orig
            self.assertEqual(e.exception.code, 2)
            # nada de rodada criada: so o proprio PEDIDO.json do teste e o log da recusa
            self.assertEqual({x for x in os.listdir(t) if not x.startswith("FAST-")} - antes,
                             {"PEDIDO.json", "RODADAS.log"})


class LinhagemDoContrato(unittest.TestCase):
    """Ordem do dono 02/10: SOURCE_CONTRACT_ID e SOURCE_ID copiados do Source Contract, conferidos, nunca inventados."""

    def setUp(self):
        self._orig = RF.linhas_banco

    def tearDown(self):
        RF.linhas_banco = self._orig

    def test_sem_contrato_ou_sem_source_id_recusa(self):
        with tempfile.TemporaryDirectory() as t:
            for k in ("SOURCE_CONTRACT_ID", "SOURCE_ID"):
                for v in (None, "", "NAO_SEI"):
                    with self.assertRaises(RF.PedidoInvalido, msg="%s=%r" % (k, v)):
                        RF.ler_pedido(_escrever(t, _pedido(**{k: v})))

    def test_raw_de_outra_fonte_recusa(self):
        RF.linhas_banco = lambda sql: [{"id": 3, "source_id": "S-A", "captured_at": "x"},
                                       {"id": 7, "source_id": "S-B", "captured_at": "x"}]
        with self.assertRaises(RF.PedidoInvalido):
            RF.raws_do_pedido(_pedido())

    def contrato(self, t, **kw):
        sc = {"SOURCE_CONTRACT_ID": "SC-CASE-001-0001", "CASE_ID": "CASE-001",
              "EVIDENCE_REQUEST_ID": "ER-CASE-001-FONTE_OFICIAL", "SOURCE_ID": "S-A", "APROVADA_PARA_CAPTURA": "SIM"}
        sc.update(kw)
        return sc

    def test_contraprova_contrato_igual_ao_pedido_passa(self):
        with tempfile.TemporaryDirectory() as t:
            self.assertEqual(RF.conferir_contrato(_pedido(), self.contrato(t))["SOURCE_ID"], "S-A")

    def test_contrato_divergente_ou_nao_aprovado_recusa(self):
        with tempfile.TemporaryDirectory() as t:
            for kw in ({"SOURCE_CONTRACT_ID": "SC-OUTRO"}, {"CASE_ID": "CASE-002"},
                       {"EVIDENCE_REQUEST_ID": "ER-OUTRO"}, {"SOURCE_ID": "S-B"}, {"APROVADA_PARA_CAPTURA": "NAO"}):
                with self.assertRaises(RF.PedidoInvalido, msg=str(kw)):
                    RF.conferir_contrato(_pedido(), self.contrato(t, **kw))

    def test_carimbo_sem_contrato_conferido_diz_nao(self):
        with tempfile.TemporaryDirectory() as t:
            RF.carimbar_pedido(t, _pedido(), "FAST-X")
            p = json.loads(Path(os.path.join(t, "PEDIDO.json")).read_text(encoding="utf-8"))
            self.assertEqual(p["CONTRATO_CONFERIDO"], "NAO")
            self.assertFalse(os.path.exists(os.path.join(t, "SOURCE_CONTRACT.json")))

    def test_carimbo_com_contrato_copia_bytes_commit_e_sha(self):
        import hashlib
        with tempfile.TemporaryDirectory() as t:
            bts = json.dumps(self.contrato(t)).encode("utf-8")
            RF.carimbar_pedido(t, _pedido(), "FAST-X", (self.contrato(t), bts, "a" * 40, "fontes/SC.json"))
            p = json.loads(Path(os.path.join(t, "PEDIDO.json")).read_text(encoding="utf-8"))
            self.assertEqual((p["CONTRATO_CONFERIDO"], p["SOURCE_CONTRACT_COMMIT"], p["SOURCE_CONTRACT_PATH"],
                              p["SOURCE_CONTRACT_SHA256"]), ("SIM", "a" * 40, "fontes/SC.json",
                                                             hashlib.sha256(bts).hexdigest()))
            self.assertEqual(Path(os.path.join(t, "SOURCE_CONTRACT.json")).read_bytes(), bts)


class ContratoPublicadoNoGit(unittest.TestCase):
    """O contrato vem de um commit PUBLICADO (`git show <commit>:<caminho>`), nunca de ficheiro solto."""

    def setUp(self):
        import subprocess as sp
        self.t = tempfile.mkdtemp()
        g = lambda *a, cwd=None: sp.run(["git"] + list(a), cwd=cwd, capture_output=True, text=True, check=True)
        self.g = g
        g("init", "--bare", "-q", os.path.join(self.t, "remoto.git"))
        self.repo = os.path.join(self.t, "repo")
        g("clone", "-q", os.path.join(self.t, "remoto.git"), self.repo)
        for k, v in (("user.email", "t@t"), ("user.name", "t")):
            g("config", k, v, cwd=self.repo)
        os.makedirs(os.path.join(self.repo, "fontes"))
        Path(self.repo, "fontes", "SC.json").write_text(json.dumps({"SOURCE_CONTRACT_ID": "SC-1"}), encoding="utf-8")
        g("add", ".", cwd=self.repo)
        g("commit", "-q", "-m", "sc", cwd=self.repo)
        g("push", "origin", "HEAD:refs/heads/main", cwd=self.repo)
        g("fetch", "origin", cwd=self.repo)
        self.pub = g("rev-parse", "HEAD", cwd=self.repo).stdout.strip()

    def test_contraprova_publicado_le_os_bytes_do_commit(self):
        sc, bts, commit, cam = RF.contrato_publicado(self.pub[:10] + ":fontes/SC.json", self.repo)
        self.assertEqual((sc["SOURCE_CONTRACT_ID"], commit, cam), ("SC-1", self.pub, "fontes/SC.json"))

    def test_commit_nao_publicado_recusa(self):
        Path(self.repo, "fontes", "SC.json").write_text(json.dumps({"SOURCE_CONTRACT_ID": "SC-2"}), encoding="utf-8")
        self.g("commit", "-q", "-am", "local", cwd=self.repo)
        local = self.g("rev-parse", "HEAD", cwd=self.repo).stdout.strip()
        with self.assertRaises(RF.PedidoInvalido):
            RF.contrato_publicado(local + ":fontes/SC.json", self.repo)

    def test_ficheiro_solto_ou_caminho_inexistente_recusa(self):
        for ref in ("C/x/SOURCE_CONTRACT.json", self.pub + ":fontes/OUTRO.json", "0" * 40 + ":fontes/SC.json"):
            with self.assertRaises(RF.PedidoInvalido, msg=ref):
                RF.contrato_publicado(ref, self.repo)


class CarimboFonte(unittest.TestCase):
    def test_carimbo_leva_contrato_e_fonte(self):
        with tempfile.TemporaryDirectory() as t:
            RF.carimbar_pedido(t, _pedido(), "FAST-X")
            p = json.loads(Path(os.path.join(t, "PEDIDO.json")).read_text(encoding="utf-8"))
            self.assertEqual((p["SOURCE_CONTRACT_ID"], p["SOURCE_ID"]), ("SC-CASE-001-0001", "S-A"))


class Carimbo(unittest.TestCase):
    def test_carimba_o_pedido_dentro_da_pasta_da_rodada(self):
        with tempfile.TemporaryDirectory() as t:
            RF.carimbar_pedido(t, _pedido(), "FAST-20261002T210000")
            p = json.loads(Path(os.path.join(t, "PEDIDO.json")).read_text(encoding="utf-8"))
            # o que o `fast_casos` confere na incorporacao:
            self.assertEqual(p["CASE_ID"], "CASE-001")
            self.assertEqual(p["EVIDENCE_REQUEST_ID"], "ER-CASE-001-FONTE_OFICIAL")
            self.assertEqual(p["RAW_ASSET_IDS"], [7, 3])
            # + a identidade da rodada que o serviu
            self.assertEqual(p["RUN_ID"], "FAST-20261002T210000")
            self.assertTrue(p["RODADA_PEDIDA"])


class LeituraDoBanco(unittest.TestCase):
    def test_o_dsn_do_ficheiro_chega_ao_psql(self):
        """Contraprova de uma quase-falha medida: sem o dsn como argumento, o psql cai em
        `localhost:5432` e recusa em portugues -- e a rodada morre sem explicacao."""
        class _R:
            returncode = 0
            stdout = 'on\n{"id":1,"source_id":"S","captured_at":"x"}\n'
            stderr = ""

        orig_base, orig_run = RF.BASE, RF.subprocess.run
        chamadas = []

        def falso(argv, **kw):
            chamadas.append(argv)
            return _R()

        RF.BASE = tempfile.mkdtemp()
        dsn = "postgresql://u:p@host:5432/db"
        Path(os.path.join(RF.BASE, "SALA_DSN.txt")).write_text(dsn, encoding="utf-8")
        RF.subprocess.run = falso
        try:
            self.assertEqual(RF.linhas_banco("select 1"), [{"id": 1, "source_id": "S", "captured_at": "x"}])
            self.assertIn(dsn, chamadas[0])
        finally:
            RF.BASE, RF.subprocess.run = orig_base, orig_run

    def test_sem_read_only_confere_e_diz_por_que(self):
        class _R:
            returncode = 2
            stdout = ""
            stderr = "psql: erro: a conexao com o servidor falhou"

        orig_base, orig_run = RF.BASE, RF.subprocess.run
        RF.BASE = tempfile.mkdtemp()
        Path(os.path.join(RF.BASE, "SALA_DSN.txt")).write_text("postgresql://x", encoding="utf-8")
        RF.subprocess.run = lambda argv, **kw: _R()
        try:
            with self.assertRaises(AssertionError) as e:
                RF.linhas_banco("select 1")
            self.assertIn("conexao com o servidor falhou", str(e.exception))
        finally:
            RF.BASE, RF.subprocess.run = orig_base, orig_run


if __name__ == "__main__":
    unittest.main()
