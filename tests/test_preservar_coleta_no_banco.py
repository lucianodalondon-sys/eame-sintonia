# -*- coding: utf-8 -*-
"""PROVAS CONTRA UM BANCO DE VERDADE — SQL aceite não é linha gravada.

O QUE MUDA EM RELAÇÃO AOS TESTES COM SIMULACRO
----------------------------------------------
`tests/test_preservar_coleta.py` prova a **lógica** com um dicionário. Bom, e
insuficiente: um dicionário não tem `unique`, não tem `on conflict do nothing`,
e não sabe gravar menos linhas do que lhe pediram sem se queixar.

Estes testes correm contra um banco real e descartável, e é ele que responde
às três perguntas que o simulacro não conseguia:

    quantas linhas o banco REALMENTE gravou?      → SELECT
    `do nothing` pode esconder divergência?       → não, porque se lê antes
    o Python e o banco dizem a mesma coisa?       → só se `concluida` lá também

⚠️ **O banco é SQLite, e isso fica dito.** As travas que importam são as
mesmas — `storage_path UNIQUE`, `sha256` não único, `run_id NOT NULL` com
chave estrangeira — mas SQLite não é Postgres. A mesma bateria corre contra
Postgres 16 real no workflow `banco-descartavel.yml`. Enquanto só esta correr,
o estado honesto é `DB_TESTED (SQLITE)`.

E nada aqui toca produção: cada teste cria o seu banco em memória e deita-o
fora no fim.
"""
import os
import sys
import unittest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)

from guarda.memoria_descartavel import MemoriaDescartavel  # noqa: E402
from guarda.preservar_coleta import (  # noqa: E402
    METADATA_CONFLICT, PRESERVED_AND_REGISTERED, RUN_ID_CONFLICT,
    RUN_NOT_CLOSED_IN_DB, UPLOAD_PENDING_METADATA, ArmazemDeMentira,
    caminho_do_objeto, preservar, sha256)

CORRIDA = {
    "RUN_ID": "IT-BANCO-0001", "PLATFORM": "local", "ACTOR": "teste",
    "ACTOR_VERSION": "1", "SOURCE_COUNTRY": "IT", "MISSION": "prova",
    "STARTED_AT": "2026-09-08T00:00:00Z", "RULE_VERSION": "1",
    "CAPTURE_METHOD": "HTTP_GET",
}
FIM = "2026-09-08T00:05:00Z"

A, B = b"o conteudo A", b"o conteudo B"


def _art(nome, dados, nativo, url=None):
    return {
        "COUNTRY": "IT", "SOURCE_SLUG": "fonte-de-teste",
        "ARTIFACT_KIND": "DOCUMENT", "NAME": nome, "SOURCE_NATIVE_ID": nativo,
        "SHA256": sha256(dados), "BYTES": len(dados),
        "MEDIA_TYPE": "application/pdf", "CAPTURED_AT": "2026-09-08T00:00:00Z",
        "SOURCE_URL": url or "https://exemplo.it/%s" % nativo,
    }


def _bytes_de(obj):
    return {sha256(A): A, sha256(B): B}[obj["SHA256"]]


class CasoBase(unittest.TestCase):
    def setUp(self):
        self.banco = MemoriaDescartavel()
        self.armazem = ArmazemDeMentira()
        self.addCleanup(self.banco.fechar)

    def correr(self, artefatos, run=None, banco=True):
        return preservar(run or CORRIDA, artefatos, self.armazem, _bytes_de,
                         memoria=self.banco if banco else None, terminou_em=FIM)


class AsLinhasSaoContadasNoBanco(CasoBase):
    """A a C — o número observado vem de um SELECT."""

    def test_A_dois_objetos_esperados(self):
        r = self.correr([_art("a.pdf", A, "11"), _art("b.pdf", B, "22")])
        self.assertEqual(r["RECONCILIACAO"]["OBJETOS_ESPERADOS"], 2)
        self.assertEqual(r["RECONCILIACAO"]["OBJETOS_CONFERIDOS"], 2)

    def test_B_o_select_confirma_duas_linhas_reais(self):
        """A prova que faltava: o banco é interrogado, não acreditado."""
        r = self.correr([_art("a.pdf", A, "11"), _art("b.pdf", B, "22")])
        self.assertEqual(r["RECONCILIACAO"]["LINHAS_OBSERVADAS_NO_BANCO"], 2)
        self.assertEqual(self.banco.contar("raw_asset"), 2)
        self.assertIn("SELECT", r["MEMORIA"]["COMO_FOI_MEDIDO"])

    def test_C_a_corrida_termina_concluida_no_proprio_banco(self):
        r = self.correr([_art("a.pdf", A, "11")])
        self.assertEqual(r["RUN_STATE"], "COMPLETE")
        self.assertEqual(self.banco.corrida(CORRIDA["RUN_ID"])["status"],
                         "concluida")
        self.assertEqual(self.banco.corrida(CORRIDA["RUN_ID"])["finished_at"], FIM)
        self.assertTrue(r["AS_DUAS_CASAS_CONCORDAM"])
        self.assertEqual(r["PENDENCIA"], PRESERVED_AND_REGISTERED)


class ORetryNaoDuplica(CasoBase):
    """D e E — repetir é reencontrar, e reencontrar tem nome."""

    def test_D_retry_identico_nao_cria_duplicata(self):
        arts = [_art("a.pdf", A, "11"), _art("b.pdf", B, "22")]
        self.correr(arts)
        envios = self.armazem.envios
        r2 = self.correr(arts)
        self.assertEqual(self.banco.contar("raw_asset"), 2)
        self.assertEqual(self.banco.contar("collection_run"), 1)
        self.assertEqual(self.armazem.envios, envios, "byte subiu outra vez")
        self.assertEqual(r2["RUN_STATE"], "COMPLETE")

    def test_E_caminho_existente_com_a_mesma_linha_e_REUSED(self):
        """Reencontro legítimo diz-se `REUSED`, e não se confunde com «gravei»."""
        art = [_art("a.pdf", A, "11")]
        self.correr(art)
        r2 = self.correr(art)
        self.assertEqual(r2["JA_EXISTIA_NO_BANCO"]["REUSED_METADATA"], 1)
        self.assertEqual(r2["JA_EXISTIA_NO_BANCO"]["CONFLITOS_DE_OBJETO"], [])


class OConflitoNaoEEngolido(CasoBase):
    """F, G e J — `do nothing` deixa de ser esconderijo."""

    def test_F_mesmo_caminho_com_outro_sha_e_CONFLICT(self):
        """Duas verdades no mesmo endereço. O SQL passaria calado; aqui não.

        A linha existente é LIDA e comparada antes de qualquer escrita, e a
        corrida não fecha.
        """
        art = _art("a.pdf", A, "11")
        self.correr([art])
        impostor = dict(art, SHA256=sha256(B), BYTES=len(B))
        # o caminho tem o sha no nome; forca-se o MESMO caminho de proposito
        impostor["SHA256"] = art["SHA256"]
        caminho = caminho_do_objeto(impostor)
        self.assertEqual(caminho, caminho_do_objeto(art))
        # e agora muda-se so o conteudo declarado, mantendo o endereco
        self.banco.con.execute(
            "update raw_asset set sha256 = ? where storage_path = ?",
            (sha256(B), caminho))
        r = self.correr([art])
        self.assertEqual(r["PENDENCIA"], METADATA_CONFLICT)
        self.assertEqual(r["RUN_STATE"], "PARTIAL")
        self.assertIn("sem_conflito_de_metadata", r["COMPLETION_BASIS"]["FALTOU"])
        divergencias = r["JA_EXISTIA_NO_BANCO"]["CONFLITOS_DE_OBJETO"][0]
        self.assertEqual(divergencias["DIVERGENCIAS"][0]["CAMPO"], "sha256")

    def test_G_mesmo_caminho_com_outra_corrida_e_CONFLICT(self):
        """Byte reclamado por duas corridas não se resolve por antiguidade."""
        art = _art("a.pdf", A, "11")
        self.correr([art])
        outra = dict(CORRIDA, RUN_ID="IT-BANCO-0002")
        r = self.correr([art], run=outra)
        self.assertEqual(r["PENDENCIA"], METADATA_CONFLICT)
        self.assertEqual(r["RUN_STATE"], "PARTIAL")

    def test_J_mesmo_run_id_com_outra_identidade_e_RUN_ID_CONFLICT(self):
        """A configuração da corrida é congelada (COL-LAW-211). Se ela mudar,
        não é a mesma execução — e duas execuções não partilham um nome."""
        self.correr([_art("a.pdf", A, "11")])
        disfarcada = dict(CORRIDA, ACTOR_VERSION="2")
        r = self.correr([_art("b.pdf", B, "22")], run=disfarcada)
        self.assertEqual(r["PENDENCIA"], RUN_ID_CONFLICT)
        self.assertEqual(r["RUN_STATE"], "PARTIAL")
        self.assertIn("sem_conflito_de_corrida", r["COMPLETION_BASIS"]["FALTOU"])
        campos = {d["CAMPO"] for d in
                  r["JA_EXISTIA_NO_BANCO"]["CONFLITO_DE_CORRIDA"]["DIVERGENCIAS"]}
        self.assertIn("actor_version", campos)


class OBancoGravaMenosDoQueSePediu(CasoBase):
    """H e I — o caso que derrubava a versão anterior."""

    def test_H_sql_corre_e_grava_a_menos_a_reconciliacao_reprova(self):
        """O SQL é aceite, não lança exceção, e o banco fica com uma linha a
        menos. Se `LINHAS_OBSERVADAS` viesse do número esperado, isto passava
        como sucesso — e era o estado italiano outra vez, em pequeno."""
        self.banco.engolir_inserts_de_objeto = 1
        r = self.correr([_art("a.pdf", A, "11"), _art("b.pdf", B, "22")])
        self.assertTrue(r["MEMORIA"]["APLICADA"], "o SQL correu sem erro")
        self.assertEqual(r["MEMORIA"]["LINHAS_ESPERADAS"], 2)
        self.assertEqual(r["MEMORIA"]["LINHAS_OBSERVADAS"], 1)
        self.assertEqual(self.banco.contar("raw_asset"), 1)
        self.assertEqual(r["RUN_STATE"], "PARTIAL")
        self.assertIn("reconciliacao_observada", r["COMPLETION_BASIS"]["FALTOU"])
        self.assertEqual(r["PENDENCIA"], UPLOAD_PENDING_METADATA)

    def test_H2_e_a_corrida_fica_rodando_no_banco(self):
        """Sem reconciliação não há promoção. O `UPDATE` de fecho nem corre."""
        self.banco.engolir_inserts_de_objeto = 1
        self.correr([_art("a.pdf", A, "11"), _art("b.pdf", B, "22")])
        self.assertEqual(self.banco.corrida(CORRIDA["RUN_ID"])["status"],
                         "rodando")

    def test_I_objetos_gravados_mas_fecho_falha_nao_da_COMPLETE(self):
        """As duas casas têm de dizer a mesma coisa. Se o `UPDATE` de fecho não
        pegar, o manifesto NÃO pode dizer COMPLETE — era o segundo buraco que o
        red team encontrou."""
        original = self.banco.aplicar
        estado = {"n": 0}

        def aplicar_e_recusar_o_fecho(sql):
            estado["n"] += 1
            if "update" in sql:
                raise IOError("o banco recusou o fecho")
            original(sql)

        self.banco.aplicar = aplicar_e_recusar_o_fecho
        r = self.correr([_art("a.pdf", A, "11")])
        self.assertEqual(self.banco.contar("raw_asset"), 1)
        self.assertEqual(r["RECONCILIACAO"]["LINHAS_OBSERVADAS_NO_BANCO"], 1)
        self.assertEqual(r["RUN_STATE"], "PARTIAL")
        self.assertIn("banco_diz_concluida", r["COMPLETION_BASIS"]["FALTOU"])
        self.assertEqual(r["PENDENCIA"], RUN_NOT_CLOSED_IN_DB)
        self.assertFalse(r["AS_DUAS_CASAS_CONCORDAM"])


class QuandoOProcessoMorre(CasoBase):
    """K e L — as duas mortes, contra o banco."""

    def test_K_morte_depois_do_upload(self):
        """Bytes guardados, banco por tocar. A corrida não fecha, e a segunda
        passagem completa-a sem subir byte nenhum outra vez."""
        arts = [_art("a.pdf", A, "11")]
        r1 = self.correr(arts, banco=False)
        self.assertEqual(len(self.armazem.objetos), 1)
        self.assertEqual(r1["RUN_STATE"], "PARTIAL")
        self.assertEqual(self.banco.contar("raw_asset"), 0)

        envios = self.armazem.envios
        r2 = self.correr(arts)
        self.assertEqual(self.armazem.envios, envios)
        self.assertEqual(r2["RUN_STATE"], "COMPLETE")
        self.assertEqual(self.banco.contar("raw_asset"), 1)

    def test_L_morte_depois_do_metadata_e_antes_do_fecho(self):
        """As linhas ficaram, a corrida ficou `rodando`. Correr outra vez fecha
        — e não duplica nada, porque o retry lê antes de escrever."""
        original = self.banco.aplicar

        def recusar_o_fecho(sql):
            if "update" in sql:
                raise IOError("morreu antes de fechar")
            original(sql)

        self.banco.aplicar = recusar_o_fecho
        arts = [_art("a.pdf", A, "11"), _art("b.pdf", B, "22")]
        self.correr(arts)
        self.assertEqual(self.banco.contar("raw_asset"), 2)
        self.assertEqual(self.banco.corrida(CORRIDA["RUN_ID"])["status"],
                         "rodando")

        self.banco.aplicar = original
        r2 = self.correr(arts)
        self.assertEqual(self.banco.contar("raw_asset"), 2, "duplicou")
        self.assertEqual(self.banco.contar("collection_run"), 1)
        self.assertEqual(r2["RUN_STATE"], "COMPLETE")
        self.assertEqual(self.banco.corrida(CORRIDA["RUN_ID"])["status"],
                         "concluida")


class OGoldenPathPODERIAPassarPorAqui(CasoBase):
    """A integração contra fixture — sem correr a estrada de verdade.

    A pergunta desta fase não é «migrámos os 43?». É: **o acervo real caberia
    nesta cadeia?** Responde-se com os conteúdos que o registo de derivados já
    declara, um armazém de mentira e o banco descartável.

    ⚠️ E o número NÃO está escrito no teste. Ele é contado do registo. Fixar
    «43» aqui repetiria o erro de gravar no código algo que só era verdade num
    dia — e o armazém italiano acabou de mostrar por que três contagens
    parecidas podem ser todas diferentes.
    """

    def artefatos_reais(self):
        caminho = os.path.join(RAIZ, "data", "derivados",
                               "REGISTO-DE-ARTEFATOS.json")
        if not os.path.exists(caminho):
            self.skipTest("registo de derivados ausente")
        import json
        with open(caminho, encoding="utf-8") as f:
            d = json.load(f)
        itens = d.get("ARTEFATOS") if isinstance(d, dict) else d
        pais = {}
        for a in itens or []:
            if a.get("PARENT_SHA256"):
                pais.setdefault(a["PARENT_SHA256"], a)
        arts, conteudo = [], {}
        for sha, a in sorted(pais.items()):
            # os bytes reais nao sao lidos: o que se prova aqui e a CADEIA,
            # nao o conteudo. Cada pai vira um artefato com o seu sha declarado.
            dados = ("bytes de %s" % sha).encode()
            conteudo[sha256(dados)] = dados
            arts.append({
                "COUNTRY": "IT", "SOURCE_SLUG": "golden-path",
                "ARTIFACT_KIND": "DOCUMENT",
                "NAME": (a.get("PARENT_ARTIFACT_ID") or sha[:12]) + ".pdf",
                "SOURCE_NATIVE_ID": sha[:8], "SHA256": sha256(dados),
                "BYTES": len(dados), "MEDIA_TYPE": "application/pdf",
                "CAPTURED_AT": "2026-09-08T00:00:00Z",
                "SOURCE_URL": "https://exemplo.it/%s" % sha[:8]})
        return arts, conteudo

    def test_a_cadeia_aguenta_o_acervo_real_e_o_numero_e_contado(self):
        arts, conteudo = self.artefatos_reais()
        self.assertGreater(len(arts), 0, "o registo nao declarou pai nenhum")
        r = preservar(CORRIDA, arts, self.armazem,
                      lambda o: conteudo[o["SHA256"]],
                      memoria=self.banco, terminou_em=FIM)
        n = len(arts)
        self.assertEqual(r["RECONCILIACAO"]["OBJETOS_ESPERADOS"], n)
        self.assertEqual(r["RECONCILIACAO"]["LINHAS_OBSERVADAS_NO_BANCO"], n)
        self.assertEqual(self.banco.contar("raw_asset"), n)
        self.assertEqual(r["RUN_STATE"], "COMPLETE")
        self.assertEqual(self.banco.corrida(CORRIDA["RUN_ID"])["status"],
                         "concluida")

    def test_esta_peca_ainda_nao_tem_caller_real(self):
        """CAN DO ≠ DID DO, e o repositório tem de o admitir.

        Medido: nenhum ficheiro de produção chama `preservar()`. Só testes,
        provas e o adaptador descartável. Enquanto for assim, o mapa não pode
        pintar isto como estrada corrente — e é este teste que segura a
        honestidade se alguém ligar a peça e esquecer de atualizar o estado.
        """
        chamadores = []
        for pasta, _sub, ficheiros in os.walk(RAIZ):
            partes = pasta.replace("\\", "/").split("/")
            if ".git" in partes or "tests" in partes or "provas" in partes:
                continue
            for nome in ficheiros:
                if not nome.endswith((".py", ".mjs")):
                    continue
                caminho = os.path.join(pasta, nome)
                if caminho.endswith(("preservar_coleta.py", "memoria_descartavel.py")):
                    continue
                with open(caminho, encoding="utf-8", errors="ignore") as f:
                    if "preservar_coleta" in f.read():
                        chamadores.append(os.path.relpath(caminho, RAIZ))
        self.assertEqual(
            chamadores, [],
            "a peca ganhou caller real: atualize o estado do G-42 forward de "
            "DB_TESTED para OPERATIONAL e o cartao do mapa junto")


class AsTravasDoEsquemaSaoReais(CasoBase):
    """O banco descartável tem de reproduzir as travas que interessam."""

    def test_run_id_e_obrigatorio_e_tem_chave_estrangeira(self):
        """A trava que NÃO se relaxa para caber o legado italiano."""
        import sqlite3
        with self.assertRaises(sqlite3.IntegrityError):
            self.banco.con.execute(
                "insert into raw_asset (run_id, storage_path, media_type, "
                "bytes, sha256, captured_at) values "
                "('CORRIDA-QUE-NAO-EXISTE','x','application/pdf',1,'a','t')")

    def test_storage_path_e_unico_e_sha256_nao_e(self):
        """O mesmo conteúdo em dois endereços continua a caber — foi o que os
        195 objetos italianos provaram."""
        self.correr([_art("x.pdf", A, "731"), _art("y.pdf", A, "6321")])
        self.assertEqual(self.banco.contar("raw_asset"), 2)
        linhas = self.banco.objetos_da_corrida(CORRIDA["RUN_ID"])
        self.assertEqual(len({x["sha256"] for x in linhas}), 1)
        self.assertEqual(len({x["storage_path"] for x in linhas}), 2)

    def test_o_banco_e_descartavel_e_nao_conhece_producao(self):
        # A prosa deste ficheiro FALA de producao — ela explica que nao lhe
        # toca. O que nao pode existir e MAO: um import de rede, ou uma
        # credencial lida do ambiente.
        fonte = open(os.path.join(RAIZ, "guarda", "memoria_descartavel.py"),
                     encoding="utf-8").read()
        for linha in fonte.splitlines():
            if linha.startswith(("import ", "from ")):
                self.assertNotIn("requests", linha)
                self.assertNotIn("urllib", linha)
                self.assertNotIn("psycopg", linha)
                self.assertNotIn("socket", linha)
        for proibido in ("os.environ", "getenv", "SUPABASE_URL ="):
            self.assertNotIn(proibido, fonte)
        # e o unico motor que ele conhece e o descartavel
        self.assertIn("import sqlite3", fonte)


if __name__ == "__main__":
    unittest.main(verbosity=2)
