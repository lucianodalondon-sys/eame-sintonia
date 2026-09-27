# -*- coding: utf-8 -*-
"""LINHA-BUSCA (D93) · assunto-primeiro sem rede: consultas, motores, portao D93, candidata, Admission normal."""
import hashlib
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "coleta"))
import linha_busca as LB            # noqa: E402
import collection_gate as CG        # noqa: E402

CQ, MO = LB.CQ, LB.MO


def _sem_rede(*a, **k):
    raise AssertionError("o teste tentou sair a rede")


# GUARDA DE REDE (memoria: um mutante que desliga a recusa sai a rede de verdade). Nada neste modulo
# chega ao portao IT nem ao transporte real.
LB.portao_it = _sem_rede
LB.transporte_real = _sem_rede
FX = RAIZ / "ferramentas" / "linha_busca" / "fixtures" / "teste"
PROV = {"ESPECIE": "ACHADO_POR_BUSCA", "CONSULTA": "bollettino vite peronospora", "MOTOR": "DDG_HTML",
        "POSICAO": 1, "INSTANTE": "2026-09-27T09:00:00+00:00"}


class PortaoD93(unittest.TestCase):
    def test_candidata_com_proveniencia_inteira_entra(self):
        v = CG.avaliar_achado_por_busca(PROV, "CANDIDATA")
        self.assertTrue(v["COLLECTION_ELIGIBLE"])
        self.assertEqual(CG.ACHADO_POR_BUSCA_D93, v["MOTIVO"])
        self.assertEqual("CANDIDATA", v["FONTE_ESTADO_NO_MOMENTO"])

    def test_sem_posicao_ou_sem_especie_nao_ha_excecao(self):
        for falta in ("POSICAO", "MOTOR", "INSTANTE", "CONSULTA", "ESPECIE"):
            p = dict(PROV)
            p.pop(falta)
            with self.subTest(falta=falta):
                v = CG.avaliar_achado_por_busca(p, "CANDIDATA")
                self.assertFalse(v["COLLECTION_ELIGIBLE"])
                self.assertEqual(CG.PROVENIENCIA_INCOMPLETA, v["MOTIVO"])

    def test_fonte_ja_recusada_nao_entra_pela_busca(self):
        for e in ("RECUSADA", "POLICY_BLOCK"):
            self.assertEqual(CG.FONTE_RECUSADA, CG.avaliar_achado_por_busca(PROV, e)["MOTIVO"])

    def test_a_regra_da_coleta_recorrente_nao_mudou(self):
        v = CG.avaliar("CAND-9999", livro={"TRANSICOES": []})
        self.assertFalse(v["COLLECTION_ELIGIBLE"])


class Consultas(unittest.TestCase):
    def test_nacional_primeiro_sem_repetir(self):
        qs = CQ.prioridade(CQ.gerar(9, 2026, familias_r3=["T1", "T8"]))
        self.assertEqual("bollettino fitosanitario vite peronospora settembre 2026", qs[0]["CONSULTA"])
        self.assertIsNone(qs[0]["REGIAO"])
        self.assertEqual(len(qs), len({q["CONSULTA"] for q in qs}))
        self.assertTrue(any(q["UNIVERSO"] == "T8" and q["ORIGEM"].startswith("R3") for q in qs))
        for q in qs:
            self.assertIn(q["UNIVERSO"], ("T1", "T3", "T8"))
            self.assertTrue(q["FERRAMENTA"])

    def test_familias_da_r3_so_as_nunca_amostradas(self):
        with tempfile.TemporaryDirectory() as d:
            f = Path(d) / "r3.json"
            f.write_text(json.dumps({"LACUNAS": [{"TIPO": "FAMILIA_NUNCA_AMOSTRADA", "T": "T1"},
                                                 {"TIPO": "DATA_SEM_ANO", "T": "T2"},
                                                 {"TIPO": "FAMILIA_NUNCA_AMOSTRADA", "T": "T8"}]}), encoding="utf-8")
            self.assertEqual(["T1", "T8"], CQ.familias_da_r3(f))


class Motores(unittest.TestCase):
    def test_ddg_bing_google(self):
        ddg = MO.ddg_resultados((FX / "serp-ddg-SINTETICA.html").read_bytes())
        self.assertEqual(["https://www.fitosanitario.re.it/bollettino/", "https://assoprol.it/mosca"], ddg)
        bing = MO.bing_resultados((FX / "serp-bing-SINTETICA.html").read_bytes())
        self.assertEqual(["https://www.arsacweb.it/bollettino/", "https://nocciolare.it/cimice"], bing)
        g = MO.google_resultados((FX / "serp-google-SINTETICA.html").read_bytes())
        self.assertEqual(["https://www.regione.veneto.it/web/fitosanitario", "https://www.olivicoltori.net/"], g)

    def test_api_sem_chave_nao_pede(self):
        import os
        if not os.environ.get("SINTONIA_GOOGLE_CSE_KEY"):
            self.assertEqual("", MO.google_cse_pedido("x"))
        if not os.environ.get("SINTONIA_BRAVE_KEY"):
            self.assertEqual("", MO.brave_pedido("x"))


class Colher(unittest.TestCase):
    """O ensaio inteiro sobre a fixture de teste (paginas sinteticas marcadas)."""

    @classmethod
    def setUpClass(cls):
        cls.d = Path(tempfile.mkdtemp())
        cls.fila = cls.d / "fila.json"
        cls.fila.write_text(json.dumps({"DATASET": "t", "LEI": "t", "ESTADOS": {}, "CANDIDATAS": [
            {"CANDIDATA_ID": "CAND-0001", "TIPO": "ORGANIZACAO", "PAIS": "IT", "NOME": "r",
             "URL": "https://www.recusada.example.it/", "ESTADO": "RECUSADA", "SOURCE_ID": None,
             "MOTIVO_DA_RECUSA": "fora do foco"}]}), encoding="utf-8")
        idx = json.loads((FX / "PAGINAS.json").read_text(encoding="utf-8"))

        def falso(url, cab=None):
            p = idx[url]
            if p.get("ERRO"):
                raise type(p["ERRO"], (Exception,), {})(p["PORQUE"])
            return (FX / p["FICHEIRO"]).read_bytes(), {"CONTENT_TYPE": p["CONTENT_TYPE"]}
        cls.res = json.loads((FX / "RESULTADOS.json").read_text(encoding="utf-8"))
        cls.doc = LB.colher(cls.res, cls.fila, cls.d / "saida", falso, corrida="TESTE-LINHA-BUSCA")
        cls.por = {}
        for x in cls.doc["ITENS"]:                     # a 1.a vez que cada endereco apareceu (o duplicado vem depois)
            cls.por.setdefault(x["URL"], x)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.d, ignore_errors=True)

    def test_estados(self):
        e = {u: x["ESTADO"] for u, x in self.por.items()}
        self.assertEqual("ADMITIDA", self.por["https://www.servizio-vite.example.it/bollettino-21"]["ESTADO"])
        self.assertEqual("ADMISSION_NAO", self.por["https://www.servizio-vite.example.it/bollettini/"]["ESTADO"])
        self.assertEqual("ROBOTS_OU_ROTA_NAO_PERMITIDA", self.por["https://www.proibido.example.it/bollettino"]["ESTADO"])
        self.assertEqual("TETO_DO_DOMINIO", self.por["https://www.cheio.example.it/bollettino"]["ESTADO"])
        self.assertEqual("PORTAO_RECUSOU", self.por["https://www.recusada.example.it/pagina"]["ESTADO"], e)

    def test_a_candidata_entra_pela_porta_e_e_a_identidade_do_item(self):
        q = {c["CANDIDATA_ID"]: c for c in json.loads(self.fila.read_text(encoding="utf-8"))["CANDIDATAS"]}
        x = self.por["https://www.servizio-vite.example.it/bollettino-21"]
        c = q[x["CANDIDATA_ID"]]
        self.assertEqual("https://www.servizio-vite.example.it/", c["URL"])
        self.assertEqual("CANDIDATA", c["ESTADO"])
        self.assertIn("DDG_HTML posicao 1", c["ONDE_VIU"])
        self.assertEqual(x["CANDIDATA_ID"], x["SOURCE_ID"])
        # a capa do mesmo site nao cria segunda candidata
        self.assertEqual(x["CANDIDATA_ID"], self.por["https://www.servizio-vite.example.it/bollettini/"]["CANDIDATA_ID"])

    def test_ready_leva_a_fonte_candidata_e_cumpre_o_contrato_da_sala(self):
        import sala_de_espera as SE
        x = self.por["https://www.servizio-vite.example.it/bollettino-21"]
        r = x["READY"]
        self.assertEqual(x["CANDIDATA_ID"], r["SOURCE_ID"])
        self.assertEqual("T3", r["UNIVERSO"])
        SE._conferir_unidades([r])                     # o mesmo cheque que o pousar faz
        self.assertNotEqual("NAO SEI", r["FACT_TIME"])

    def test_o_raw_leva_a_proveniencia_inteira(self):
        raws = [json.loads(l) for l in (self.d / "saida" / "RAW-LINHA-BUSCA.jsonl").read_text(encoding="utf-8").splitlines()]
        self.assertEqual(2, len(raws))                 # so as duas paginas que sairam de facto
        for r in raws:
            p = r["PROVENIENCIA"]
            self.assertEqual("ACHADO_POR_BUSCA", p["ESPECIE"])
            for k in ("CONSULTA", "MOTOR", "POSICAO", "INSTANTE", "FONTE_ESTADO_NO_MOMENTO"):
                self.assertTrue(str(p[k]).strip(), k)
            self.assertTrue((self.d / "saida" / r["STORAGE_PATH"]).exists())

    def test_fonte_recusada_depois_marca_e_nao_apaga(self):
        d = json.loads(self.fila.read_text(encoding="utf-8"))
        x = self.por["https://www.servizio-vite.example.it/bollettino-21"]
        for c in d["CANDIDATAS"]:
            if c["CANDIDATA_ID"] == x["CANDIDATA_ID"]:
                c["ESTADO"] = "RECUSADA"
        f2 = self.d / "fila-depois.json"
        f2.write_text(json.dumps(d), encoding="utf-8")
        antes = (self.d / "saida" / "LIVRO-LINHA-BUSCA.jsonl").read_text(encoding="utf-8")
        m = LB.marcar(self.d / "saida", f2)
        self.assertEqual(2, len(m))                   # a materia e a capa do mesmo site foram colhidas
        depois = (self.d / "saida" / "LIVRO-LINHA-BUSCA.jsonl").read_text(encoding="utf-8")
        self.assertTrue(depois.startswith(antes))     # so acrescenta
        self.assertEqual([], LB.marcar(self.d / "saida", f2))   # nao marca duas vezes


    # ── D94-b (08:58) ──────────────────────────────────────────────────────
    def test_perfil_nao_e_item_e_nao_vira_candidata(self):
        for u in ("https://www.linkedin.com/in/silvia-toffolatti", "https://x.com/SLToffolatti"):
            self.assertEqual("PERFIL_NAO_E_ITEM", self.por[u]["ESTADO"])
            self.assertNotIn("CANDIDATA_ID", self.por[u])
        urls = [c["URL"] for c in json.loads(self.fila.read_text(encoding="utf-8"))["CANDIDATAS"]]
        self.assertFalse([u for u in urls if "linkedin.com" in u or "x.com" in u])
        pistas = (self.d / "saida" / "PISTAS-DE-CONTA.jsonl").read_text(encoding="utf-8")
        self.assertIn("silvia-toffolatti", pistas)

    def test_post_de_linkedin_vai_para_o_scrap(self):
        u = [x for x in self.por if "/posts/" in x][0]
        self.assertEqual("POST_SOCIAL_PARA_O_SCRAP", self.por[u]["ESTADO"])
        self.assertIn("/posts/", (self.d / "saida" / "POSTS-PARA-O-SCRAP.jsonl").read_text(encoding="utf-8"))

    def test_muro_de_login_nao_se_guarda_nem_conta(self):
        self.assertEqual("PAGINA_DE_LOGIN", self.por["https://www.login.example.it/pagina"]["ESTADO"])

    def test_so_conta_itens_unicos(self):
        # o mesmo boletim achado por 2 resultados: um pedido, um item
        self.assertEqual(1, self.doc["ADMITIDAS"])
        self.assertEqual(1, self.doc["ITENS_UNICOS_ADMITIDOS"])
        self.assertEqual(1, self.doc["ESTADOS"]["DUPLICADO_NA_CORRIDA"])


class RawCanonico(unittest.TestCase):
    """11:20: a Sala recusou (run_id_fkey). O repouso preserva pelo dono do RAW e so pousa com o id real."""

    @classmethod
    def setUpClass(cls):
        import linha_busca_raw as LR
        cls.LR = LR
        cls.d = Path(tempfile.mkdtemp())
        fila = cls.d / "fila.json"
        fila.write_text(json.dumps({"DATASET": "t", "LEI": "t", "ESTADOS": {}, "CANDIDATAS": []}), encoding="utf-8")
        idx = json.loads((FX / "PAGINAS.json").read_text(encoding="utf-8"))

        def falso(url, cab=None):
            p = idx[url]
            if p.get("ERRO"):
                raise type(p["ERRO"], (Exception,), {})(p["PORQUE"])
            return (FX / p["FICHEIRO"]).read_bytes(), {"CONTENT_TYPE": p["CONTENT_TYPE"]}
        res = json.loads((FX / "RESULTADOS.json").read_text(encoding="utf-8"))
        cls.saida = cls.d / "LOTE-T"
        LB.colher(res, fila, cls.saida, falso, corrida="TESTE-COLHER")

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.d, ignore_errors=True)

    def _fakes(self, confirmar=True):
        visto = {}

        class P:
            memoria = object()
            ESTADO = "DESCARTAVEL"

        def preservar(run, artefatos, bytes_de):
            visto["RUN"], visto["ARTEFATOS"] = run, artefatos
            for a in artefatos:
                self.assertEqual(a["SHA256"], hashlib.sha256(bytes_de(a)).hexdigest())
            obs = [{"RUN_ID": run["RUN_ID"], "SHA256": a["SHA256"], "RAW_OBSERVATION_ID": 900 + i}
                   for i, a in enumerate(artefatos)] if confirmar else []
            return {"RUN_STATE": "COMPLETE" if confirmar else "PARTIAL", "RAW_OBSERVATIONS": obs,
                    "MEMORIA": {"APLICADA": confirmar}, "FECHO_NO_BANCO": {"STATUS_NO_BANCO": "concluida"}}

        def pousar_fn(corrida, prontos):
            visto["POUSAR"] = (corrida, prontos)
            return {"POUSADAS": len(prontos)}
        return P(), preservar, pousar_fn, visto

    def test_sem_memoria_recusa(self):
        class Sem:
            memoria = None
            ESTADO = "AUSENTE"
        with self.assertRaises(SystemExit):
            self.LR.repousar([self.saida], persistencia=Sem(), preservar=lambda *a: {}, pousar=True)

    def test_preserva_e_pousa_com_o_id_real_na_mesma_corrida(self):
        P, pres, pou, visto = self._fakes()
        doc = self.LR.repousar([self.saida], corrida="LB-RAW-T", pousar=True, persistencia=P,
                               preservar=pres, pousar_fn=pou)
        self.assertEqual(1, doc["PAGINAS_ADMITIDAS_LIDAS"])          # so a pagina ADMITIDA, uma vez
        self.assertEqual(1, doc["PRONTOS_COM_RAW"])
        run = visto["RUN"]
        self.assertEqual("coleta/linha_busca.py", run["ACTOR"])
        self.assertEqual("LB-RAW-T", run["RUN_ID"])
        a = visto["ARTEFATOS"][0]
        self.assertTrue(a["SOURCE_ID"].startswith("CAND-"))
        self.assertIsNone(a["DOCUMENT_ID"])                         # nao se inventa identidade documental
        corrida, prontos = visto["POUSAR"]
        self.assertEqual("LB-RAW-T", corrida)                       # a corrida que nasceu em collection_run
        self.assertEqual(900, prontos[0]["RAW_OBSERVATION_ID"])
        import sala_de_espera as SE
        SE._conferir_unidades(prontos)

    def test_sem_observacao_confirmada_nao_pousa(self):
        P, pres, pou, visto = self._fakes(confirmar=False)
        doc = self.LR.repousar([self.saida], corrida="LB-RAW-T2", pousar=True, persistencia=P,
                               preservar=pres, pousar_fn=pou)
        self.assertEqual(0, doc["PRONTOS_COM_RAW"])
        self.assertNotIn("POUSAR", visto)
        self.assertEqual("SEM_RAW_CANONICO", doc["PAGINAS"][0]["ESTADO"])

    def test_byte_adulterado_nao_entra(self):
        raw = json.loads((self.saida / "RAW-LINHA-BUSCA.jsonl").read_text(encoding="utf-8").splitlines()[0])
        copia = self.d / "LOTE-ADULTERADO"
        shutil.copytree(self.saida, copia)
        (copia / raw["STORAGE_PATH"]).write_bytes(b"outro conteudo")
        self.assertEqual([], [p for p in self.LR.paginas_admitidas([copia]) if p["RAW"]["SHA256"] == raw["SHA256"]])


class Rede(unittest.TestCase):
    def test_sem_autorizado_nao_sai(self):
        with tempfile.TemporaryDirectory() as d:
            self.assertEqual(2, LB.main(["x", "--colher", "--resultados=x", "--fila=x", "--saida=%s" % d]))


if __name__ == "__main__":
    unittest.main()
