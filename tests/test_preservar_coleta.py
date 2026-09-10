# -*- coding: utf-8 -*-
"""PROVAS DO PLANO E DO ARMAZÉM — antes de o banco entrar na história.

A DIVISÃO ENTRE ESTE FICHEIRO E O DO BANCO
------------------------------------------
    aqui                       o plano e os bytes: quantos objetos deviam
                               existir, o envio, a conferência do hash, e as
                               proibições do dono da escrita. Sem banco.

    test_..._no_banco.py       a reconciliação contra um banco de verdade:
                               quantas linhas ficaram lá, o conflito que o
                               `do nothing` engoliria, e o fecho da corrida.

Esta versão perdeu os testes de «memória escrita» de propósito. Eles davam
`COMPLETE` com um simulacro que nunca gravava nada — provavam a lógica e
mascaravam a pergunta que interessa. Foram para o ficheiro do banco, onde a
resposta vem de um `SELECT`.

O QUE FICOU AQUI, E POR QUÊ
---------------------------
As espécies. Foi a medição dos 195 objetos italianos que as separou, e é aqui
que elas ficam guardadas: dois produtos que usam o mesmo documento na mesma URL
não exigem dois bytes; o mesmo byte publicado em duas URLs exige dois objetos.
Nenhuma dessas duas frases precisa de banco para ser verdadeira.
"""
import json
import os
import sys
import unittest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)

from guarda.preservar_coleta import (  # noqa: E402
    UPLOAD_PENDING_METADATA, ArmazemDeMentira, caminho_do_objeto, planear,
    preservar, relatorio, sha256)

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
        # 026: a observacao diz DE QUEM e DE QUE ela e. Sem SOURCE_ID real o
        # dono do RAW recusa — e nao ha estado de identidade para inventar.
        "SOURCE_ID": "IT-T2-002", "DOCUMENT_ID": "ARPAV:Z07:%s" % nativo,
        "ARTIFACT_KIND": "DOCUMENT", "NAME": nome,
        "SOURCE_NATIVE_ID": nativo, "SHA256": sha256(dados),
        "BYTES": len(dados), "MEDIA_TYPE": "application/pdf",
        "CAPTURED_AT": "2026-09-08T00:00:00Z",
        "SOURCE_URL": url or "https://exemplo.it/%s" % nativo,
        "USED_BY": usado_por,
    }


def _bytes_de(obj):
    return {sha256(BYTES_A): BYTES_A, sha256(BYTES_B): BYTES_B}[obj["SHA256"]]


def _correr(artefatos, armazem=None):
    """Sem banco, de propósito. É a metade da história que este ficheiro cobre."""
    armazem = armazem or ArmazemDeMentira()
    return preservar(CORRIDA, artefatos, armazem, _bytes_de), armazem


class OPlanoEOsBytes(unittest.TestCase):
    """O que se pode provar sem banco nenhum."""

    def test_sem_corrida_nao_entra_nada(self):
        """Não há corrida genérica. Sem `run_id`, nada é preservado."""
        with self.assertRaises(ValueError):
            preservar({"RUN_ID": ""}, [], ArmazemDeMentira(), _bytes_de)

    def test_o_envio_passa_e_o_hash_e_conferido(self):
        r, _ = _correr([_art("a.pdf", BYTES_A, "11"),
                        _art("b.pdf", BYTES_B, "22")])
        self.assertEqual(r["ENVIO"]["NOVOS"], 2)
        self.assertEqual(r["ENVIO"]["FALHADOS"], [])
        self.assertEqual(r["PROVA_DOS_BYTES"]["CONFERIDOS"], 2)
        self.assertEqual(r["PROVA_DOS_BYTES"]["DIVERGENTES"], [])

    def test_sem_banco_a_corrida_NUNCA_fica_complete(self):
        """A propriedade mais importante deste ficheiro.

        Bytes perfeitos no armazém e nenhuma linha escrita é EXATAMENTE o
        estado italiano. Ele não pode dar `COMPLETE` — nem sequer quando tudo
        o que este ficheiro sabe medir correu bem.
        """
        r, armazem = _correr([_art("a.pdf", BYTES_A, "11")])
        self.assertEqual(len(armazem.objetos), 1)
        self.assertEqual(r["RUN_STATE"], "PARTIAL")
        self.assertEqual(r["PENDENCIA"], UPLOAD_PENDING_METADATA)
        self.assertIn("reconciliacao_observada", r["COMPLETION_BASIS"]["FALTOU"])
        self.assertIn("banco_diz_concluida", r["COMPLETION_BASIS"]["FALTOU"])

    def test_a_contagem_observada_nao_e_inventada_quando_nao_ha_leitura(self):
        """Sem banco não há número observado — e o campo diz isso, em vez de
        copiar o esperado para o lugar do medido."""
        r, _ = _correr([_art("a.pdf", BYTES_A, "11")])
        self.assertIsNone(r["RECONCILIACAO"]["LINHAS_OBSERVADAS_NO_BANCO"])
        self.assertIn("NAO MEDIDO", r["MEMORIA"]["COMO_FOI_MEDIDO"])

    def test_o_byte_fica_guardado_quando_a_memoria_nao_corre(self):
        """RAW não se apaga como compensação. É a evidência que sobrou."""
        r, armazem = _correr([_art("a.pdf", BYTES_A, "11")])
        self.assertEqual(len(armazem.objetos), 1)
        self.assertEqual(r["BYTE_APAGADO_COMO_COMPENSACAO"][:3], "NAO")

    def test_retry_nao_sobe_o_byte_outra_vez(self):
        _, armazem = _correr([_art("a.pdf", BYTES_A, "11")])
        envios = armazem.envios
        r2, _ = _correr([_art("a.pdf", BYTES_A, "11")], armazem=armazem)
        self.assertEqual(armazem.envios, envios)
        self.assertEqual(r2["ENVIO"]["NOVOS"], 0)
        self.assertEqual(r2["ENVIO"]["REAPROVEITADOS"], 1)

    def test_morte_a_meio_do_envio(self):
        """O segundo objeto rebenta; o primeiro fica guardado e a conta não
        bate. `PARTIAL` — não `FAILED` silencioso nem `COMPLETE` otimista."""
        armazem = ArmazemDeMentira()
        arts = [_art("a.pdf", BYTES_A, "11"), _art("b.pdf", BYTES_B, "22")]
        armazem.falhar_a_partir_de = caminho_do_objeto(arts[1])
        r, _ = _correr(arts, armazem=armazem)
        self.assertEqual(len(armazem.objetos), 1)
        self.assertEqual(r["RUN_STATE"], "PARTIAL")
        self.assertIn("nenhum_envio_falhado", r["COMPLETION_BASIS"]["FALTOU"])
        self.assertIn("bytes_no_armazem", r["COMPLETION_BASIS"]["FALTOU"])


class AsEspeciesNoArmazem(unittest.TestCase):
    """O que a medição dos 195 objetos italianos provou, virado em regra."""

    def test_mesmo_sha_em_dois_caminhos_continua_permitido(self):
        """O caso `227779…`: o MESMO PDF publicado em duas URLs da ADAMA.

        São dois factos sobre o mundo — as duas páginas publicaram — e um
        conteúdo só. Dois objetos, e nada os impede.
        """
        p = planear([_art("x.pdf", BYTES_A, "731"),
                     _art("y.pdf", BYTES_A, "6321")])
        self.assertEqual(p["CONTEUDOS_UNICOS"], 1)
        self.assertEqual(p["OBJETOS_PLANEADOS"], 2)
        self.assertEqual(p["RELACOES_SEM_BYTE_NOVO"], 0)

    def test_dois_produtos_no_mesmo_documento_nao_exigem_dois_objetos(self):
        """Os casos `ef688…` e `308764…`: dois produtos, a MESMA URL.

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

    def test_caminho_repetido_nao_sobe_duas_vezes(self):
        a = _art("z.pdf", BYTES_A, "6026")
        _, armazem = _correr([a, dict(a)])
        self.assertEqual(len(armazem.objetos), 1)
        self.assertEqual(armazem.envios, 1)

    def test_a_cardinalidade_nao_esta_escrita_no_codigo(self):
        """Nem 43, nem 141, nem 139. O plano é calculado do que entrar — fixar
        um número na arquitetura repetiria o erro de escrever no código algo
        que só era verdade num dia."""
        for quantos in (0, 1, 7):
            p = planear([_art("f%d.pdf" % i, BYTES_A, str(i))
                         for i in range(quantos)])
            self.assertEqual(p["OBJETOS_PLANEADOS"], quantos)


class OQueEsteDonoNuncaFaz(unittest.TestCase):
    """As proibições, escritas como teste."""

    def test_nao_fala_com_o_banco(self):
        """Gera SQL auditável, e a mão que o aplica é injetada. Este ficheiro
        não abre ligação nenhuma."""
        fonte = open(os.path.join(RAIZ, "guarda", "preservar_coleta.py"),
                     encoding="utf-8").read().lower()
        for proibido in ("psycopg", "import requests", "urlopen",
                         "create_client", "subprocess", "sqlite3"):
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

    def test_a_porta_do_banco_sabe_ler(self):
        """E a porta do banco tem de saber LER — sem leitura não há
        reconciliação, e sem reconciliação `COMPLETE` é opinião."""
        from guarda import preservar_coleta as pc
        metodos = sorted(m for m in dir(pc.Memoria) if not m.startswith("_"))
        self.assertEqual(metodos,
                         ["aplicar", "corrida", "objeto_em", "objetos_da_corrida"])

    def test_so_o_sql_de_fecho_promove_a_corrida(self):
        """`concluida` não aparece no SQL de escrita: a corrida abre `rodando`
        e só é promovida depois da reconciliação ter sido lida."""
        from guarda.preservar_coleta import sql_da_memoria, sql_de_fecho
        p = planear([_art("a.pdf", BYTES_A, "11")])
        escrita = sql_da_memoria(CORRIDA, [p["OBJETOS"][0]["STORAGE_PATH"]], p)
        # so as linhas EXECUTAVEIS contam: o comentario do ficheiro explica o
        # fecho, e explicar nao e executar
        executavel = "\n".join(x for x in escrita.splitlines()
                               if not x.strip().startswith("--"))
        self.assertIn("'rodando'", executavel)
        self.assertNotIn("concluida", executavel)
        fecho = sql_de_fecho("R", "2026-09-08T00:05:00Z", 1)
        self.assertIn("status = 'concluida'", fecho)
        self.assertIn("finished_at", fecho)
        # a trava do `where`: fechar duas vezes nao muda nada, e nao ressuscita
        # uma corrida que outro processo ja marcou de outra maneira
        self.assertIn("and status = 'rodando'", fecho)

    def test_a_apostrofe_italiana_nao_parte_o_sql(self):
        """`dell'olivo` e `l'annata` são a classe de erro que um gerador comete
        e que transforma o resto do ficheiro em lixo — está escrito em
        `guarda/sql_conferir.py`, o portão desta casa."""
        from guarda.preservar_coleta import sql_da_memoria
        a = _art("bollettino dell'olivo.pdf", BYTES_A, "9")
        a["SOURCE_URL"] = "https://exemplo.it/l'annata"
        p = planear([a])
        sql = sql_da_memoria(CORRIDA, [p["OBJETOS"][0]["STORAGE_PATH"]], p)
        self.assertIn("dell''olivo", sql)
        self.assertIn("l''annata", sql)
        for linha in sql.splitlines():
            if linha.startswith("insert"):
                self.assertEqual(linha.count("'") % 2, 0)

    def test_o_relatorio_nao_carrega_o_sql(self):
        r, _ = _correr([_art("a.pdf", BYTES_A, "11")])
        self.assertNotIn("insert into", relatorio(r))
        json.loads(relatorio(r))


if __name__ == "__main__":
    unittest.main(verbosity=2)
