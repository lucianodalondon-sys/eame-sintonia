#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""A SALA DURÁVEL — o que se pode provar sem banco nenhum.

    O QUE ESTA BATERIA MEDE, E O QUE ELA NÃO PODE MEDIR

Durabilidade não se prova aqui: prova-se contra Postgres real, em
`provas/a_sala_sobrevive_ao_processo.py`, e o workflow `banco-descartavel.yml`
é que a corre. O que se prova AQUI é tudo o que não precisa de banco — a
escolha do backend, o contrato de entrada, a recusa de cair em silêncio, e o
facto de a API pública ter continuado a ser a mesma.

    UM TESTE QUE PRECISA DE BANCO E NÃO O TEM NÃO É UM TESTE QUE PASSA.
    É UM TESTE QUE NÃO CORREU.
"""
import ast
import io
import os
import shutil
import sys
import tempfile
import unittest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for g in (RAIZ, os.path.join(RAIZ, "admissao")):
    if g not in sys.path:
        sys.path.insert(0, g)

import _gavetas                                            # noqa: E402,F401
import admissao                                            # noqa: E402
import sala_de_espera as espera                            # noqa: E402

DONO = os.path.join(RAIZ, "admissao", "sala_de_espera.py")
MIGRACAO = os.path.join(RAIZ, "supabase", "migrations",
                        "031_a_sala_de_espera_ganha_dono_duravel.sql")


def _fonte(caminho):
    # Com `with`, e não sem: um ficheiro deixado aberto num varrimento de árvore
    # inteira enche o descritor do processo e enche o log de avisos.
    with io.open(caminho, encoding="utf-8") as f:
        return f.read()


class Bancada(unittest.TestCase):
    def setUp(self):
        self.sala = tempfile.mkdtemp(prefix="sala-teste-")
        self.addCleanup(shutil.rmtree, self.sala, ignore_errors=True)
        self._morada = espera.MORADA
        espera.MORADA = self.sala
        self.addCleanup(setattr, espera, "MORADA", self._morada)
        self._amb = dict(os.environ)
        self.addCleanup(lambda: (os.environ.clear(), os.environ.update(self._amb)))
        os.environ.pop("SINTONIA_SALA_BACKEND", None)
        os.environ.pop("SINTONIA_SALA_DSN", None)

    def unidade(self, **extra):
        item = {"id": "i-1", "texto": "Ensaio de campo publicado com DOI",
                "source_id": "IT-T7-001", "fact_time": "2026-05-02"}
        d = admissao.decidir(item, "T5", corrida="R1")
        return dict(admissao.pronto_para_inteligencia(item, d), **extra)


class ABackendNaoSeEscolheSozinho(Bancada):
    """⚠️ UM FALLBACK SILENCIOSO PARA DISCO EFÉMERO É A FALHA ORIGINAL."""

    def test_sem_variavel_o_backend_e_o_NAO_canonico(self):
        e = espera.estado_operacional()
        self.assertEqual("FICHEIRO", e["BACKEND"])
        self.assertFalse(e["CANONICO"])

    def test_e_o_recibo_di_lo_em_vez_de_calar(self):
        r = espera.pousar("R1", [self.unidade()])
        self.assertEqual("FICHEIRO", r["BACKEND"])
        self.assertFalse(r["CANONICO"])

    def test_postgres_sem_dsn_falha_ALTO_e_nao_cai_para_ficheiro(self):
        os.environ["SINTONIA_SALA_BACKEND"] = "POSTGRES"
        with self.assertRaises(espera.SalaIndisponivel):
            espera.pousar("R1", [self.unidade()])
        self.assertFalse(os.path.isfile(os.path.join(self.sala, "R1.json")),
                         "caiu para ficheiro — o fallback que criou o bloqueio")

    def test_backend_desconhecido_nao_vira_ficheiro(self):
        os.environ["SINTONIA_SALA_BACKEND"] = "SQLITE"
        with self.assertRaises(espera.SalaIndisponivel):
            espera.backend()

    def test_exigir_canonica_recusa_o_ficheiro(self):
        with self.assertRaises(espera.SalaIndisponivel):
            espera.exigir_canonica()

    def test_o_ficheiro_admite_que_nao_sabe_dizer_pendente(self):
        """Fingir uma fila num backend sem estado seria medir a mentira."""
        with self.assertRaises(espera.SalaIndisponivel):
            espera.listar_pendentes()
        with self.assertRaises(espera.SalaIndisponivel):
            espera.retirar("R1", "i-1", por="teste")


class OContratoDeEntrada(Bancada):
    """⚠️ UMA SALA QUE ACEITA QUALQUER DICIONÁRIO NÃO GUARDA READY: GUARDA LIXO."""

    def test_os_campos_do_dono_sao_os_campos_da_sala(self):
        """Dois lados a comparar. Se o dono do contrato mudar, isto reprova."""
        self.assertEqual(tuple(self.unidade()), espera.CAMPOS_READY)
        self.assertEqual(19, len(espera.CAMPOS_READY))

    def test_onze_campos_nao_entram(self):
        onze = self.unidade()
        onze.pop("RAW_OBSERVATION_ID")
        with self.assertRaises(ValueError):
            espera.pousar("R1", [onze])

    def test_campo_a_mais_tambem_nao_entra(self):
        with self.assertRaises(ValueError):
            espera.pousar("R1", [self.unidade(ESTADO_DE_STORAGE="x")])

    def test_o_que_nao_esta_pronto_nao_entra(self):
        with self.assertRaises(ValueError):
            espera.pousar("R1", [self.unidade(ESTADO="QUASE")])

    def test_o_que_nem_dicionario_e_nao_entra(self):
        with self.assertRaises(ValueError):
            espera.pousar("R1", ["um texto"])

    def test_lista_vazia_nao_cria_registo_nenhum(self):
        r = espera.pousar("R1", [])
        self.assertIsNone(r["ESTADO"])
        self.assertEqual([], os.listdir(self.sala))


class AImpressaoDaCorrida(Bancada):
    """A chave que distingue retry de conflito, e que não pode mudar sozinha."""

    def test_a_mesma_entrada_da_sempre_a_mesma_impressao(self):
        u = self.unidade()
        self.assertEqual(espera.impressao_da_corrida("R1", [u]),
                         espera.impressao_da_corrida("R1", [u]))

    def test_conteudo_diferente_da_impressao_diferente(self):
        self.assertNotEqual(
            espera.impressao_da_corrida("R1", [self.unidade()]),
            espera.impressao_da_corrida("R1", [self.unidade(TEXTO="outro DOI")]))

    def test_a_ordem_faz_parte_da_impressao(self):
        a, b = self.unidade(ITEM_ID="a"), self.unidade(ITEM_ID="b")
        self.assertNotEqual(espera.impressao_da_corrida("R1", [a, b]),
                            espera.impressao_da_corrida("R1", [b, a]))

    def test_o_corpo_canonico_nao_mudou_ao_mudar_de_backend(self):
        """⚠️ MUDÁ-LO FARIA UMA CORRIDA ANTIGA CONFLITAR CONSIGO PRÓPRIA."""
        self.assertIn('"ITENS": list(unidades)', _fonte(DONO))


class OEscapeDoLiteral(Bancada):
    """⚠️ CONCATENAR TEXTO DE FORA EM SQL SEM ESCAPAR É UMA PORTA DOS FUNDOS."""

    def test_a_plica_dobra(self):
        self.assertEqual("'o''brien'", espera._lit("o'brien"))

    def test_a_barra_invertida_e_um_caractere_e_nao_um_escape(self):
        self.assertEqual("'a\\b'", espera._lit("a\\b"))

    def test_o_nulo_vira_null_e_nao_a_palavra(self):
        self.assertEqual("null", espera._lit(None))

    def test_o_NUL_e_recusado_antes_do_banco(self):
        with self.assertRaises(ValueError):
            espera._lit("a\x00b")

    def test_a_tentativa_de_injecao_fica_dentro_das_plicas(self):
        self.assertEqual("'''; drop table x;--'", espera._lit("'; drop table x;--"))

    def test_o_escape_nao_depende_do_padrao_do_servidor(self):
        """⚠️ UM COMENTÁRIO QUE GARANTE O QUE O CÓDIGO NÃO IMPÕE É UMA PROMESSA.

        Com `standard_conforming_strings` desligado, a barra invertida volta a
        ser escape dentro da plica — e `_lit()`, que só dobra a plica, deixaria
        de bastar. A definição viaja com cada chamada ao `psql`.
        """
        amb = espera._ambiente_psql()
        self.assertIn("standard_conforming_strings=on", amb["PGOPTIONS"])


class ADSNNuncaAparece(Bancada):
    """Um erro do `psql` pode trazer a DSN dentro da mensagem."""

    def test_a_url_sai_omitida(self):
        sujo = 'could not connect to postgresql://u:senha@host:5432/db agora'
        self.assertNotIn("senha", espera._sanitiza(sujo))
        self.assertIn("<URL_OMITIDA>", espera._sanitiza(sujo))


class UmDonoSo(Bancada):
    """⚠️ ONE CONCEPT → ONE OWNER, e a mudança de backend não o duplicou."""

    def test_nao_nasceu_um_segundo_dono_da_sala(self):
        proibidos = ("sala_v2.py", "waiting_room.py", "waiting_room_new.py",
                     "ready_store.py", "sala_de_espera_pg.py",
                     "sala_de_espera_v2.py")
        achados = []
        for base, _dirs, ficheiros in os.walk(RAIZ):
            if any(x in base for x in (".git", "node_modules", "italia-portale")):
                continue
            achados += [f for f in ficheiros if f in proibidos]
        self.assertEqual([], achados)

    def test_os_dois_caminhos_canonicos_continuam_a_falar_com_o_mesmo_dono(self):
        for caminho in (os.path.join(RAIZ, "orquestrador", "orquestrador.py"),
                        os.path.join(RAIZ, "coleta", "rota_forward_documento.py")):
            s = _fonte(caminho)
            self.assertIn("import sala_de_espera as espera", s)
            self.assertIn("espera.pousar(", s)

    def test_nem_o_orquestrador_nem_a_rota_conhecem_o_backend(self):
        """⚠️ OS CONSUMIDORES NÃO PODEM SABER ONDE A SALA GUARDA."""
        for caminho in (os.path.join(RAIZ, "orquestrador", "orquestrador.py"),
                        os.path.join(RAIZ, "coleta", "rota_forward_documento.py")):
            s = _fonte(caminho)
            for proibido in ("sala_de_espera", "psql", "insert into",
                             "SINTONIA_SALA_DSN", "SUPABASE_DB_URL"):
                if proibido == "sala_de_espera":
                    continue
                self.assertNotIn(proibido, s,
                                 "%s passou a conhecer o backend da sala"
                                 % os.path.basename(caminho))

    def test_o_sql_da_sala_so_existe_dentro_do_dono(self):
        agulhas = ("public.sala_de_espera",)
        fora = []
        for base, _dirs, ficheiros in os.walk(RAIZ):
            if any(x in base for x in (".git", "node_modules", "italia-portale",
                                       "supabase", "docs", "system-map",
                                       "provas", "tests", ".tmp", "build")):
                continue
            for f in ficheiros:
                if not f.endswith(".py") or f == "sala_de_espera.py":
                    continue
                s = _fonte(os.path.join(base, f))
                if any(a in s for a in agulhas):
                    fora.append(os.path.relpath(os.path.join(base, f), RAIZ))
        self.assertEqual([], fora, "o SQL da sala escapou do dono")


class ASalaNaoJulga(Bancada):
    """⚠️ COLLECTION TERMINA NA SALA. A SALA NÃO É INTELLIGENCE."""

    def test_nao_ha_vocabulario_de_relevancia_no_dono(self):
        s = _fonte(DONO).upper()
        for palavra in ("KEEP", "DISCARD", "RELEVANCIA", "RELEVANCE", "SCORE"):
            self.assertNotIn('"%s"' % palavra, s)

    def test_nem_na_migration(self):
        s = _fonte(MIGRACAO).lower()
        for coluna in ("keep ", "discard ", "relevancia ", "veredito "):
            self.assertNotIn("  %s" % coluna, s)

    def test_retirar_nao_recebe_veredito(self):
        arv = ast.parse(_fonte(DONO))
        for no in ast.walk(arv):
            if isinstance(no, ast.FunctionDef) and no.name == "retirar":
                nomes = [a.arg for a in no.args.args]
                self.assertEqual(["run_id", "item_id", "por"], nomes)
                return
        self.fail("retirar() desapareceu do dono")

    def test_o_vocabulario_da_fila_e_de_duas_palavras(self):
        self.assertEqual(("WAITING", "CONSUMED"), espera.ESTADOS_DA_FILA)

    def test_retirar_nao_e_apagar(self):
        """A linha fica, com hora e autor. Uma fila que apaga não é auditável."""
        s = _fonte(DONO)
        self.assertNotIn("delete from public.sala_de_espera", s)
        self.assertIn("estado_da_fila = ", s)


class AMigrationDiz(Bancada):
    def test_a_031_existe_e_e_a_proxima(self):
        pasta = os.path.join(RAIZ, "supabase", "migrations")
        numeros = sorted(f[:3] for f in os.listdir(pasta) if f.endswith(".sql"))
        # ⚠️ ERA `assertEqual("031", numeros[-1])`, e isso guardava «a 031 e a
        # ULTIMA migration do repositorio» — uma frase que deixa de ser
        # verdadeira na primeira migration seguinte, escrita por quem for.
        # O que esta prova quer dizer e que a 031 EXISTE e nao foi renumerada.
        self.assertIn("031", numeros)
        self.assertEqual(len(numeros), len(set(numeros)),
                         "duas migrations com o mesmo numero sao UMA")

    def test_a_chave_nao_e_o_ITEM_ID(self):
        """A chave é `(run_id, ordem)`, e continua a ser depois da cura.

        ⚠️ A RAZÃO MUDOU, E A REGRA NÃO. Esta prova dizia «`decidir()` devolve
        `"?"`, logo `ITEM_ID` não é endereço». `C-COL-PRESERVE-FACTS-V1` matou o
        `"?"` — e isso NÃO faz de `ITEM_ID` uma chave. Ele continua a ser o nome
        que a FONTE deu ao item, e duas fontes podem dar o mesmo. A ordem dentro
        da corrida é gerada aqui e é única por construção.

            CURAR UM SINTOMA NÃO PROMOVE O CAMPO A CHAVE.
        """
        s = _fonte(MIGRACAO)
        self.assertIn("primary key (run_id, ordem)", s)
        self.assertNotIn("primary key (run_id, item_id)", s)

    def test_um_item_sem_endereco_NAO_chega_a_sala(self):
        """⚠️ ISTO EXIGIA `ITEM_ID == "?"`, E ERA A LEI AO CONTRÁRIO.

        A prova antiga afirmava que um item sem `id` e sem `url` chegava à Sala
        com `ITEM_ID = '?'` — e a `COL-LAW-034` diz em letra que `"?"` **NÃO
        DEVE** ser usado como identidade. A guarda congelava a violação.

            UMA PROVA QUE DESCREVE O DEFEITO PASSA A DEFENDÊ-LO.

        Agora a porta recusa: `NAO_SEI` por `identidade`, e nada chega à Sala.
        """
        sem_id = {"texto": "Ensaio com DOI", "source_id": "IT-T7-001",
                  "fact_time": "2026-05-02"}
        d = admissao.decidir(sem_id, "T5", corrida="R1")
        self.assertEqual(admissao.NAO_SEI, d.resultado)
        self.assertEqual("identidade", d.regra)
        self.assertNotEqual("?", d.item)
        with self.assertRaises(ValueError):
            admissao.pronto_para_inteligencia(sem_id, d)

    def test_a_linhagem_tem_chave_estrangeira_e_nao_disciplina(self):
        s = _fonte(MIGRACAO)
        self.assertIn("references public.raw_asset(id)", s)
        self.assertIn("references public.collection_run(run_id)", s)

    def test_o_consumo_declara_quem_e_quando(self):
        self.assertIn("consumo_diz_quem_e_quando", _fonte(MIGRACAO))

    def test_a_prova_duravel_corre_no_workflow_do_banco_descartavel(self):
        """MODULE EXISTS != EDGE EXISTS: uma prova que ninguém corre não corre."""
        s = _fonte(os.path.join(RAIZ, ".github", "workflows",
                                "banco-descartavel.yml"))
        self.assertIn("provas/a_sala_sobrevive_ao_processo.py", s)
        self.assertIn("provas/mutacao_da_sala_duravel.py", s)
        self.assertIn("supabase/migrations/031_*.sql", s)


if __name__ == "__main__":
    unittest.main(verbosity=2)
