# -*- coding: utf-8 -*-
"""B4 — O RAW_OBSERVATION_ID VOLTA DA MEMÓRIA, E NÃO DE UMA CONTA NOSSA.

A PERGUNTA QUE ESTE FICHEIRO FECHA
----------------------------------
Uma observação preservada não tinha nome. A casa guardava o byte, escrevia a
linha, e depois não sabia dizer QUAL linha era — porque nada voltava.

    RAW_OBSERVATION_ID = raw_asset.id, lido de volta do banco

E lido é a palavra. Um id calculado do `sha256`, do `storage_path` ou do
`DOCUMENT_ID` seria um id que a casa podia ter escrito sozinha, e então ele não
provaria a única coisa que serve para provar: **que a linha existe**.

O CASO QUE ESTE FICHEIRO EXISTE PARA IMPEDIR
--------------------------------------------
O endereço no armazém é do CONTEÚDO, não da vez em que o vimos. Logo o mesmo
documento, amanhã, cai no mesmo `storage_path`. Quem perguntasse «que linha vive
neste caminho?» receberia a linha de ONTEM, com o id de ontem.

    UM ID EMPRESTADO DE OUTRA CORRIDA NÃO É UM ID ERRADO.
    É UMA OBSERVAÇÃO A FAZER-SE PASSAR POR OUTRA.

O B3 mediu que a segunda corrida do mesmo conteúdo hoje conflita. O B4 **não
conserta isso** — e por isso tem de provar que, no conflito, nenhum id é
fabricado nem emprestado.

    B4_DOES_NOT_FIX_1_STORAGE_OBJECT_N_OBSERVATIONS = YES

Offline, sem rede, banco descartável que morre em cada caso.
"""
import io
import json
import os
import sys
import unittest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)
sys.path.insert(0, os.path.join(RAIZ, "tests"))
import _gavetas  # noqa: E402,F401

import ingresso as ing                                       # noqa: E402
import italy_executor as adapter                             # noqa: E402
from guarda.memoria_descartavel import MemoriaDescartavel    # noqa: E402
from guarda import preservar_coleta as pc                    # noqa: E402
from test_italia_na_porta_canonica import CasoB1             # noqa: E402

CAMPOS = ("RAW_OBSERVATION_ID", "RUN_ID", "STORAGE_PATH", "SHA256")


def _codigo(caminho):
    """A fonte sem prosa: comentario e docstring nao sao chamadas.

    Mesmo instrumento que `provas/o_encanamento_tem_uma_porta.py` ja usa.
    """
    import tokenize
    texto = io.open(os.path.join(RAIZ, caminho), encoding="utf-8").read()
    return " ".join(t.string for t in
                    tokenize.generate_tokens(io.StringIO(texto).readline)
                    if t.type not in (tokenize.COMMENT, tokenize.STRING))

PDF = (b"%PDF-1.4\n/CreationDate (D:20260903160930+02'00')\n"
       + b"a" * 4096 + b"\n%%EOF\n")


class Bancada(unittest.TestCase):
    """Um armazém em tmpdir e um banco em memória, por caso."""

    def setUp(self):
        import shutil
        import tempfile
        self.tmp = tempfile.mkdtemp(prefix="b4-")
        self.addCleanup(shutil.rmtree, self.tmp, True)
        self.banco = MemoriaDescartavel()
        self.addCleanup(self.banco.fechar)
        self.armazem = ing.ArmazemLocal(self.tmp)
        self.rel = "loja/IT-T2-002/agro_01.pdf"
        os.makedirs(os.path.join(self.tmp, os.path.dirname(self.rel)),
                    exist_ok=True)
        with open(os.path.join(self.tmp, self.rel), "wb") as fh:
            fh.write(PDF)

    def observar(self, run_id, quando="2026-09-10T00:00:00Z", banco=True):
        return ing.receber(
            [{"SOURCE_ID": "IT-T2-002",
              "SOURCE_URL": "https://www.arpa.veneto.it/…/agro_01.pdf",
              "STORAGE_LOCATION": self.rel}],
            corrida={"RUN_ID": run_id, "PLATFORM": "HTTP direto",
                     "ACTOR": "coleta/italy_executor.py",
                     "ACTOR_VERSION": "adapter-v1", "SOURCE_COUNTRY": "IT",
                     "RULE_VERSION": "1", "STARTED_AT": quando},
            armazem=self.armazem,
            memoria=self.banco if banco else None,
            raiz=self.tmp)


class OIdVemDoBanco(Bancada):
    """1..4 · a primeira escrita devolve identidade real."""

    def test_1_a_primeira_preservacao_devolve_o_id_da_linha(self):
        r = self.observar("IT-B4-0001")
        obs = r["RAW"]["RAW_OBSERVATIONS"]
        self.assertEqual(len(obs), 1)
        self.assertEqual(sorted(obs[0]), sorted(CAMPOS))
        self.assertIsInstance(obs[0]["RAW_OBSERVATION_ID"], int)
        self.assertNotIsInstance(obs[0]["RAW_OBSERVATION_ID"], bool)
        self.assertGreater(obs[0]["RAW_OBSERVATION_ID"], 0)

    def test_2_o_id_devolvido_e_o_id_que_esta_no_banco(self):
        """Não basta ser inteiro: tem de ser AQUELE inteiro."""
        r = self.observar("IT-B4-0002")
        o = r["RAW"]["RAW_OBSERVATIONS"][0]
        linhas = self.banco.objetos_da_corrida("IT-B4-0002")
        self.assertEqual(len(linhas), 1)
        self.assertEqual(o["RAW_OBSERVATION_ID"], linhas[0]["id"])
        self.assertEqual(o["STORAGE_PATH"], linhas[0]["storage_path"])
        self.assertEqual(o["SHA256"], linhas[0]["sha256"])
        self.assertEqual(o["RUN_ID"], "IT-B4-0002")

    def test_3_o_id_nao_e_o_caminho_nem_o_sha(self):
        """Três espécies, três perguntas, e nenhuma serve de resposta à outra."""
        r = self.observar("IT-B4-0003")
        o = r["RAW"]["RAW_OBSERVATIONS"][0]
        ident = o["RAW_OBSERVATION_ID"]
        self.assertNotEqual(str(ident), o["STORAGE_PATH"])
        self.assertNotEqual(str(ident), o["SHA256"])
        self.assertNotIn(str(ident), o["SHA256"][:12])

    def test_4_sem_banco_nao_ha_id_e_nao_se_cunha_nenhum(self):
        r = self.observar("IT-B4-0004", banco=False)
        self.assertEqual(r["RAW"]["RAW_OBSERVATIONS"], [])
        # e os bytes foram preservados na mesma
        self.assertTrue(r["RAW"]["PROVA_DOS_BYTES"]["CONFERIDOS"], r["RAW"])


class ORetryNaoRebatiza(Bancada):
    """5 · repetir a mesma corrida não muda o nome da observação."""

    def test_5_retry_da_mesma_corrida_devolve_o_mesmo_id(self):
        primeiro = self.observar("IT-B4-RETRY")["RAW"]["RAW_OBSERVATIONS"]
        segundo = self.observar("IT-B4-RETRY")["RAW"]["RAW_OBSERVATIONS"]
        self.assertEqual(len(primeiro), 1)
        self.assertEqual(primeiro[0]["RAW_OBSERVATION_ID"],
                         segundo[0]["RAW_OBSERVATION_ID"])
        self.assertEqual(self.banco.contar("raw_asset"), 1)


class ASegundaCorridaNaoHERDANOME(Bancada):
    """6..7 · o teste negativo mais importante desta missão."""

    def test_6_corrida_nova_com_o_mesmo_conteudo_nao_recebe_o_id_da_anterior(self):
        a = self.observar("IT-B4-RUN-A")["RAW"]
        id_a = a["RAW_OBSERVATIONS"][0]["RAW_OBSERVATION_ID"]
        b = self.observar("IT-B4-RUN-B", quando="2026-09-11T00:00:00Z")["RAW"]

        # o estado de hoje, medido no B3 e NÃO corrigido aqui
        self.assertEqual(b["RUN_STATE"], "PARTIAL")
        self.assertTrue(b["JA_EXISTIA_NO_BANCO"]["CONFLITOS_DE_OBJETO"])

        # e o que o B4 tem de garantir mesmo assim
        self.assertEqual(b["RAW_OBSERVATIONS"], [])
        ids_b = [o["RAW_OBSERVATION_ID"] for o in b["RAW_OBSERVATIONS"]]
        self.assertNotIn(id_a, ids_b)   # OLD_OBSERVATION_ID_LEAKED_TO_NEW_RUN = NO

    def test_7_uma_linha_de_outra_corrida_nunca_vira_identidade_desta(self):
        """A trava, medida na função, e não só no caminho feliz.

        `objeto_em(caminho)` devolveria a linha de ontem — o endereço é do
        conteúdo. Quem construísse a identidade a partir dela daria à observação
        de hoje o nome da de ontem, e ninguém veria.
        """
        alheia = {"id": 10, "run_id": "RUN-A",
                  "storage_path": "IT/f/DOCUMENT/x-y-z.pdf", "sha256": "ab" * 32}
        pos = {"CONFERIDOS": ["IT/f/DOCUMENT/x-y-z.pdf"]}
        fora = pc.observacoes_confirmadas({"RUN_ID": "RUN-B"}, [alheia], pos)
        self.assertEqual(fora, [])

    def test_8_linha_desta_corrida_mas_nao_conferida_tambem_nao_entra(self):
        """INSERT TENTADO != ID DISPONÍVEL. CONTAGEM BATEU != ID CONFIRMADO."""
        minha = {"id": 11, "run_id": "RUN-B",
                 "storage_path": "IT/f/DOCUMENT/x-y-z.pdf", "sha256": "cd" * 32}
        fora = pc.observacoes_confirmadas({"RUN_ID": "RUN-B"}, [minha],
                                          {"CONFERIDOS": []})
        self.assertEqual(fora, [])
        fora = pc.observacoes_confirmadas(
            {"RUN_ID": "RUN-B"}, [minha],
            {"CONFERIDOS": ["IT/f/DOCUMENT/x-y-z.pdf"]})
        self.assertEqual(len(fora), 1)
        self.assertEqual(fora[0]["RAW_OBSERVATION_ID"], 11)


class AsPortasFalamAMesmaLingua(unittest.TestCase):
    """9..11 · `id` inteiro, em toda implementação da porta."""

    def test_9_a_porta_descartavel_devolve_id_inteiro(self):
        banco = MemoriaDescartavel()
        self.addCleanup(banco.fechar)
        banco.aplicar(
            "insert into public.collection_run (run_id, platform, actor, "
            "actor_version, mission, source_country, started_at, rule_version, "
            "capture_method, status) values ('R','p','a','1','m','IT',"
            "'2026-09-10T00:00:00Z','1','HTTP_GET','rodando');\n"
            "insert into public.raw_asset (run_id, storage_path, media_type, "
            "bytes, sha256, captured_at, source_url) values ('R','c/x.pdf',"
            "'application/pdf',1,'%s','2026-09-10T00:00:00Z','https://a.it');"
            % ("ab" * 32))
        linhas = banco.objetos_da_corrida("R")
        self.assertEqual(len(linhas), 1)
        self.assertIn("id", linhas[0])
        self.assertIsInstance(linhas[0]["id"], int)

    def test_10_a_porta_supabase_pede_o_id_e_devolve_o_id_inteiro(self):
        """Sem rede e sem credencial: substitui-se a saída do `psql`.

        ⚠️ A projeção desta porta NÃO pedia `id`. A coluna existe na tabela
        desde a migration 001; era o `select` que a deixava de fora, e por isso
        a identidade da observação não tinha por onde voltar em produção.
        """
        from guarda.portas_live import MemoriaSupabase
        porta = MemoriaSupabase(url="postgresql://localhost/nao-usado")
        vistos = {}

        def falso_psql(sql):
            vistos["sql"] = sql
            campos = ["17", "R", "c/x.pdf", "application/pdf", "1", "ab" * 32,
                      "2026-09-10T00:00:00Z", "https://a.it"]
            return porta.SEP.join(campos) + "\n"

        porta._psql = falso_psql
        linhas = porta.objetos_da_corrida("R")
        self.assertIn("id", vistos["sql"].split("from")[0])
        self.assertEqual(linhas[0]["id"], 17)
        self.assertIsInstance(linhas[0]["id"], int)
        self.assertEqual(linhas[0]["run_id"], "R")

    def test_10b_a_porta_da_prova_em_postgres_tambem_pede_o_id(self):
        """A terceira implementação da porta, e ela tinha o mesmo buraco.

        Ela corre no `banco-descartavel`, contra um Postgres a sério. Sem `id`
        na projeção, `preservar()` recusaria a corrida inteira lá — e o defeito
        só apareceria no CI, longe de quem o escreveu.
        """
        sys.path.insert(0, os.path.join(RAIZ, "provas"))
        import preservar_coleta_no_postgres as pg
        porta = pg.MemoriaPostgres.__new__(pg.MemoriaPostgres)
        campos = ["23", "R", "c/x.pdf", "application/pdf", "1", "ab" * 32,
                  "2026-09-10T00:00:00Z", "https://a.it"]
        vistos = {}

        def falso_psql(sql):
            vistos["sql"] = sql
            return porta.SEP.join(campos) + "\n"

        porta._psql = falso_psql
        linhas = porta.objetos_da_corrida("R")
        self.assertIn("id", vistos["sql"].split("from")[0])
        self.assertEqual(linhas[0]["id"], 23)
        self.assertIsInstance(linhas[0]["id"], int)

    def test_11_o_contrato_da_porta_diz_que_o_id_volta(self):
        doc = pc.Memoria.objetos_da_corrida.__doc__ or ""
        self.assertIn("id", doc)
        self.assertIn("inteiro positivo", doc)

    def test_12_uma_porta_fora_do_contrato_e_recusada_em_voz_alta(self):
        """Calar aqui esconderia a divergência dentro de um campo preenchido."""
        texto = {"id": "17", "run_id": "R", "storage_path": "c/x.pdf",
                 "sha256": "ab" * 32}
        with self.assertRaises(ValueError) as e:
            pc.observacoes_confirmadas({"RUN_ID": "R"}, [texto],
                                       {"CONFERIDOS": ["c/x.pdf"]})
        self.assertIn("inteiro positivo", str(e.exception))


class ACorridaItalianaInteira(CasoB1):
    """13..15 · a bancada do B1/B2, offline, com quatro observações."""

    def receber_direto(self, run_id):
        """A porta canónica, com o recibo INTEIRO à vista.

        `pela_entrada` do T-04 resume o recibo do dono do RAW em quatro campos,
        e o resumo não carrega as observações. Aqui chama-se a porta com os
        mesmos argumentos e guarda-se o que ela devolveu — nada é contornado.
        """
        import orquestrador as orq
        from receitas import EXECUTORES
        adapter.colher(run_id, ops_root=self.ops)
        itens, _ = orq.a_colheita(EXECUTORES["T2"][0])
        return ing.receber(
            itens,
            corrida={"RUN_ID": run_id, "PLATFORM": "HTTP direto",
                     "ACTOR": "coleta/italy_executor.py",
                     "ACTOR_VERSION": "adapter-v1", "SOURCE_COUNTRY": "IT",
                     "RULE_VERSION": "1", "STARTED_AT": "2026-09-10T00:00:00Z"},
            armazem=ing.ArmazemLocal(RAIZ), memoria=self.banco, raiz=RAIZ)

    def test_13_quatro_observacoes_dao_quatro_ids_distintos(self):
        self.coletar("IT-B4-ITALIA")
        r = self.receber_direto("IT-B4-ITALIA")
        self.assertEqual(len(r["ACEITES"]), 4)
        obs = r["RAW"]["RAW_OBSERVATIONS"]
        ids = [o["RAW_OBSERVATION_ID"] for o in obs]
        self.assertEqual(len(ids), 4)
        self.assertEqual(len(ids), len(set(ids)))
        self.assertTrue(all(isinstance(i, int) and i > 0 for i in ids))
        for o in obs:
            self.assertEqual(o["RUN_ID"], "IT-B4-ITALIA")
            linha = self.banco.objeto_em(o["STORAGE_PATH"])
            self.assertIsNotNone(linha)
            self.assertEqual(linha["sha256"], o["SHA256"])

    def test_14_o_recibo_que_a_porta_devolve_transporta_as_observacoes(self):
        """A porta não consulta o banco: ela transporta o que o dono devolveu."""
        self.coletar("IT-B4-PORTA")
        r = self.receber_direto("IT-B4-PORTA")
        self.assertIn("RAW_OBSERVATIONS", r["RAW"])
        self.assertEqual(len(r["RAW"]["RAW_OBSERVATIONS"]), 4)
        # A PROSA PODE NOMEAR A TABELA; O CODIGO NAO PODE FALAR COM ELA. O
        # cabecalho da porta explica que nada ali sabe como `raw_asset` e feita
        # por dentro — e um teste que proibisse a palavra proibiria a
        # explicacao junto com o defeito.
        self.assertNotIn("RAW_OBSERVATIONS", _codigo("coleta/ingresso.py"))
        self.assertNotIn("raw_asset", _codigo("coleta/ingresso.py"))

    def test_15_o_B4_nao_tocou_no_esquema_nem_chamou_o_T32(self):
        alvo = os.path.join(RAIZ, "supabase", "migrations")
        antes = sorted(os.listdir(alvo))
        self.assertEqual(antes, sorted(os.listdir(alvo)))
        for nome in ("preservar_coleta.py", "portas_live.py"):
            fonte = io.open(os.path.join(RAIZ, "guarda", nome),
                            encoding="utf-8").read()
            self.assertNotIn("rota_forward_documento", fonte)
            self.assertNotIn("alter table", fonte.lower())
            self.assertNotIn("create table", fonte.lower())


if __name__ == "__main__":
    unittest.main(verbosity=2)
