# -*- coding: utf-8 -*-
"""PROVAS DO DONO CANÔNICO DA ESCRITA — o par byte+memória não se separa.

O QUE ESTES TESTES GUARDAM
--------------------------
A garantia **para a frente** do G-42. A Itália mostrou o que acontece quando os
dois passos não são de ninguém: 195 objetos guardados e zero linhas a
reclamá-los. Estes testes existem para que uma coleta NOVA não consiga repetir
isso em silêncio.

    ARMAZÉM CHEIO + LIVRO EM BRANCO  →  a corrida NÃO pode dizer COMPLETE.

Nada aqui toca produção. O armazém é um dicionário, a memória é uma função que
o teste manda falhar quando quer, e não há banco nenhum — o que é justamente o
que permite provar os casos difíceis: envio passa e memória falha, o processo
morre a meio, o retry.
"""
import json
import os
import sys
import unittest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)

from guarda.preservar_coleta import (  # noqa: E402
    ArmazemDeMentira, UPLOAD_PENDING_METADATA, PRESERVED_AND_REGISTERED,
    caminho_do_objeto, planear, preservar, sha256)

CORRIDA = {
    "RUN_ID": "IT-TESTE-0001", "PLATFORM": "local", "ACTOR": "teste",
    "ACTOR_VERSION": "1", "SOURCE_COUNTRY": "IT", "MISSION": "prova",
    "STARTED_AT": "2026-09-08T00:00:00Z", "RULE_VERSION": "1",
    "CAPTURE_METHOD": "HTTP_GET",
}

BYTES_A = b"o conteudo A"
BYTES_B = b"o conteudo B"


def _art(nome, dados, nativo, usado_por=None, url=None):
    return {
        "COUNTRY": "IT", "SOURCE_SLUG": "fonte-de-teste",
        "ARTIFACT_KIND": "DOCUMENT", "NAME": nome,
        "SOURCE_NATIVE_ID": nativo, "SHA256": sha256(dados),
        "BYTES": len(dados), "MEDIA_TYPE": "application/pdf",
        "CAPTURED_AT": "2026-09-08T00:00:00Z",
        "SOURCE_URL": url or "https://exemplo.it/%s" % nativo,
        "USED_BY": usado_por,
    }


def _bytes_de(obj):
    return {sha256(BYTES_A): BYTES_A, sha256(BYTES_B): BYTES_B}[obj["SHA256"]]


def _correr(artefatos, armazem=None, memoria="ok"):
    armazem = armazem or ArmazemDeMentira()
    escritas = []

    def escrever(sql):
        if memoria == "falha":
            raise IOError("o banco recusou")
        escritas.append(sql)

    r = preservar(CORRIDA, artefatos, armazem, _bytes_de,
                  escrever_memoria=None if memoria == "nenhuma" else escrever)
    return r, armazem, escritas


class OCaminhoFeliz(unittest.TestCase):
    """A a E — a cadeia inteira, e COMPLETE só no fim."""

    def setUp(self):
        self.r, self.armazem, self.escritas = _correr(
            [_art("a.pdf", BYTES_A, "11"), _art("b.pdf", BYTES_B, "22")])

    def test_A_a_corrida_existe_antes_de_qualquer_byte(self):
        """Não há corrida genérica. Sem `run_id`, nada é preservado."""
        with self.assertRaises(ValueError):
            preservar({"RUN_ID": ""}, [], ArmazemDeMentira(), _bytes_de)

    def test_B_o_envio_passa(self):
        self.assertEqual(self.r["ENVIO"]["NOVOS"], 2)
        self.assertEqual(self.r["ENVIO"]["FALHADOS"], [])

    def test_C_a_memoria_passa_e_so_com_o_que_foi_conferido(self):
        self.assertTrue(self.r["MEMORIA"]["ESCRITA"])
        self.assertEqual(self.escritas[0].count("insert into public.raw_asset"), 2)

    def test_D_a_reconciliacao_bate_entre_especies_comparaveis(self):
        rec = self.r["RECONCILIACAO"]
        self.assertEqual(rec["OBJETOS_ESPERADOS"], rec["OBJETOS_CONFERIDOS"])
        self.assertEqual(rec["OBJETOS_CONFERIDOS"], rec["LINHAS_DE_MEMORIA"])

    def test_E_complete_so_no_fim_e_com_todas_as_condicoes(self):
        self.assertEqual(self.r["RUN_STATE"], "COMPLETE")
        self.assertEqual(self.r["COMPLETION_BASIS"]["FALTOU"], [])
        self.assertTrue(all(self.r["COMPLETION_BASIS"]["CONDICOES"].values()))
        self.assertEqual(self.r["PENDENCIA"], PRESERVED_AND_REGISTERED)


class OCasoQueACriouAItalia(unittest.TestCase):
    """F a H — envio passa, memória falha. O caso medido nos 195 objetos."""

    def setUp(self):
        self.r, self.armazem, _ = _correr(
            [_art("a.pdf", BYTES_A, "11")], memoria="falha")

    def test_F_o_byte_fica_guardado(self):
        """RAW não se apaga como compensação. Ele é a evidência que sobrou."""
        self.assertEqual(len(self.armazem.objetos), 1)
        self.assertEqual(self.r["BYTE_APAGADO_COMO_COMPENSACAO"][:3], "NAO")

    def test_G_a_corrida_NAO_fica_complete(self):
        """A resposta não pode ser «a corrida continua COMPLETE». É esta linha
        que impede o estado italiano de se repetir em silêncio."""
        self.assertEqual(self.r["RUN_STATE"], "PARTIAL")
        self.assertIn("memoria_escrita", self.r["COMPLETION_BASIS"]["FALTOU"])
        self.assertEqual(self.r["PENDENCIA"], UPLOAD_PENDING_METADATA)

    def test_H_o_retry_nao_sobe_o_byte_outra_vez(self):
        """Repetir só a etapa em falta. O objeto já está lá: `existe()` decide,
        e não se gasta banda para obter exatamente o mesmo estado."""
        envios_antes = self.armazem.envios
        r2, _, escritas = _correr([_art("a.pdf", BYTES_A, "11")],
                                  armazem=self.armazem, memoria="ok")
        self.assertEqual(self.armazem.envios, envios_antes)
        self.assertEqual(r2["ENVIO"]["NOVOS"], 0)
        self.assertEqual(r2["ENVIO"]["REAPROVEITADOS"], 1)
        self.assertEqual(r2["RUN_STATE"], "COMPLETE")
        self.assertEqual(escritas[0].count("insert into public.raw_asset"), 1)


class AsEspeciesNoArmazem(unittest.TestCase):
    """I a K — o que a medição dos 195 provou, virado em regra."""

    def test_I_mesmo_sha_em_dois_caminhos_continua_permitido(self):
        """O caso `227779…`: o MESMO PDF publicado em duas URLs da ADAMA.

        São dois factos sobre o mundo — as duas páginas publicaram — e um
        conteúdo só. Dois objetos, e nenhuma trava os impede.
        """
        p = planear([_art("x.pdf", BYTES_A, "731"),
                     _art("y.pdf", BYTES_A, "6321")])
        self.assertEqual(p["CONTEUDOS_UNICOS"], 1)
        self.assertEqual(p["OBJETOS_PLANEADOS"], 2)
        self.assertEqual(p["RELACOES_SEM_BYTE_NOVO"], 0)

    def test_J_dois_produtos_no_mesmo_documento_nao_exigem_dois_objetos(self):
        """O caso `ef688…` e `308764…`: dois produtos, a MESMA URL.

        A relação produto↔documento é lógica. Duplicar o byte para a
        representar seria gastar armazém para escrever uma linha de tabela.
        """
        p = planear([_art("z.pdf", BYTES_A, "6026", usado_por="P-45"),
                     _art("z.pdf", BYTES_A, "6026", usado_por="P-47")])
        self.assertEqual(p["REGISTOS_DE_ENTRADA"], 2)
        self.assertEqual(p["CONTEUDOS_UNICOS"], 1)
        self.assertEqual(p["OBJETOS_PLANEADOS"], 1)
        self.assertEqual(p["RELACOES_SEM_BYTE_NOVO"], 1)
        self.assertEqual(p["OBJETOS"][0]["USADO_POR"], ["P-45", "P-47"])

    def test_K_caminho_repetido_e_idempotente_nao_duplicado(self):
        a = _art("z.pdf", BYTES_A, "6026")
        r, armazem, escritas = _correr([a, dict(a)])
        self.assertEqual(len(armazem.objetos), 1)
        self.assertEqual(escritas[0].count("insert into public.raw_asset"), 1)
        self.assertIn("on conflict (storage_path) do nothing", escritas[0])


class QuandoOProcessoMorre(unittest.TestCase):
    """L a N — as duas mortes, e a recuperação."""

    def test_L_morte_depois_do_envio(self):
        """Morrer entre o envio e a memória deixa byte sem linha — e o
        manifesto NUNCA chega a ser escrito com COMPLETE, porque o fecho é o
        último passo. A pasta remota cheia não vale como «acabou»."""
        r, armazem, _ = _correr([_art("a.pdf", BYTES_A, "11")], memoria="nenhuma")
        self.assertEqual(len(armazem.objetos), 1)
        self.assertEqual(r["RUN_STATE"], "PARTIAL")
        self.assertEqual(r["PENDENCIA"], UPLOAD_PENDING_METADATA)

    def test_M_morte_a_meio_do_envio(self):
        """O segundo objeto rebenta. O primeiro fica guardado, a conta não bate
        e a corrida diz PARTIAL — não FAILED silencioso nem COMPLETE otimista."""
        armazem = ArmazemDeMentira()
        arts = [_art("a.pdf", BYTES_A, "11"), _art("b.pdf", BYTES_B, "22")]
        armazem.falhar_a_partir_de = caminho_do_objeto(arts[1])
        r, _, _ = _correr(arts, armazem=armazem)
        self.assertEqual(len(armazem.objetos), 1)
        self.assertEqual(r["RUN_STATE"], "PARTIAL")
        self.assertIn("nenhum_envio_falhado", r["COMPLETION_BASIS"]["FALTOU"])
        self.assertIn("bytes_no_armazem", r["COMPLETION_BASIS"]["FALTOU"])

    def test_N_a_recuperacao_e_correr_outra_vez(self):
        """Nada de comando especial: a mesma chamada, e ela faz só o que falta."""
        armazem = ArmazemDeMentira()
        arts = [_art("a.pdf", BYTES_A, "11"), _art("b.pdf", BYTES_B, "22")]
        armazem.falhar_a_partir_de = caminho_do_objeto(arts[1])
        _correr(arts, armazem=armazem)
        armazem.falhar_a_partir_de = None
        r2, _, escritas = _correr(arts, armazem=armazem)
        self.assertEqual(r2["ENVIO"]["NOVOS"], 1)
        self.assertEqual(r2["ENVIO"]["REAPROVEITADOS"], 1)
        self.assertEqual(r2["RUN_STATE"], "COMPLETE")
        self.assertEqual(escritas[0].count("insert into public.raw_asset"), 2)


class OQueEsteDonoNuncaFaz(unittest.TestCase):
    """As proibições, escritas como teste."""

    def test_nao_fala_com_o_banco(self):
        """Segue o padrão da casa: gera SQL auditável, e a mão que o leva ao
        banco é injetada. Este ficheiro não abre ligação nenhuma."""
        fonte = open(os.path.join(RAIZ, "guarda", "preservar_coleta.py"),
                     encoding="utf-8").read().lower()
        for proibido in ("psycopg", "import requests", "urlopen", "create_client",
                         "subprocess", "socket"):
            self.assertNotIn(proibido, fonte)

    def test_nao_conhece_run_generica(self):
        """Nenhum nome de corrida de mentira mora aqui."""
        fonte = open(os.path.join(RAIZ, "guarda", "preservar_coleta.py"),
                     encoding="utf-8").read()
        for inventada in ('"LEGACY', '"UNKNOWN-RUN', '"BACKFILL', '"MIGRATION-RUN'):
            self.assertNotIn(inventada, fonte)

    def test_nao_sabe_apagar_do_armazem(self):
        """A porta do armazém tem três métodos, e nenhum é «remover»."""
        from guarda import preservar_coleta as pc
        metodos = [m for m in dir(pc.Armazem) if not m.startswith("_")]
        self.assertEqual(sorted(metodos), ["enviar", "existe", "ler"])

    def test_a_apostrofe_italiana_nao_parte_o_sql(self):
        """`dell'olivo` e `l'annata` são a classe de erro que um gerador comete
        e que transforma o resto do ficheiro em lixo — está escrito em
        `guarda/sql_conferir.py`, que é o portão desta casa. O SQL gerado aqui
        passa nesse portão, apóstrofes incluídas."""
        a = _art("bollettino dell'olivo.pdf", BYTES_A, "9")
        a["SOURCE_URL"] = "https://exemplo.it/l'annata"
        r, _, escritas = _correr([a])
        self.assertEqual(r["RUN_STATE"], "COMPLETE")
        self.assertIn("dell''olivo", escritas[0])
        self.assertIn("l''annata", escritas[0])
        # numero par de aspas simples em cada statement = nenhuma aberta
        for linha in escritas[0].splitlines():
            if linha.startswith("insert"):
                self.assertEqual(linha.count("'") % 2, 0)

    def test_o_relatorio_nao_carrega_o_sql(self):
        r, _, _ = _correr([_art("a.pdf", BYTES_A, "11")])
        from guarda.preservar_coleta import relatorio
        self.assertNotIn("insert into", relatorio(r))
        json.loads(relatorio(r))


if __name__ == "__main__":
    unittest.main(verbosity=2)
