# -*- coding: utf-8 -*-
"""PROVAS DO DONO DA ESCRITA DO DERIVADO — `do nothing` não é idempotência.

O QUE ESTES TESTES GUARDAM
--------------------------
A `migration 022` já recusa a segunda linha com a mesma identidade. Isso não
chega, e a diferença é toda:

    o BANCO recusa a linha repetida.
    o WRITER tem de saber POR QUE ela foi recusada.

Se ele ler o silêncio do `on conflict do nothing` como «já lá estava, tudo
igual», uma derivação que passou a produzir **outro resultado** entra como
`REUSED` — e o sistema fica calado exatamente no dia em que devia gritar.

    IDEMPOTÊNCIA É REENCONTRO + COMPARAÇÃO + PROVA DE IGUALDADE.

O caso adversarial central está em `ODriftGrita`: a mesma receita, e o texto
saiu diferente. A resposta certa é `DERIVATION_DRIFT`. Nunca `REUSED`, nunca um
`UPDATE`, nunca apagar o antigo.

Tudo aqui corre contra um banco real e descartável, em memória, que morre no
fim de cada teste. Nada toca produção.
"""
import json
import os
import sys
import unittest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)

from guarda.memoria_descartavel import MemoriaDescartavel  # noqa: E402
from guarda.preservar_coleta import ArmazemDeMentira, sha256  # noqa: E402
from guarda.preservar_derivado import (  # noqa: E402
    DERIVATION_DRIFT, INSERTED, METADATA_NOT_RECONCILED, RAW_PARENT_NOT_FOUND,
    REUSED, REUSED_AFTER_RACE, STORAGE_CONFLICT, STORAGE_MISSING,
    caminho_do_derivado, hash_dos_parametros, id_da_receita,
    parametros_canonicos, preservar_derivado)

TEXTO_A = b"o texto extraido A"
TEXTO_B = b"o texto extraido B, diferente"
RELOGIO = lambda: "2026-09-08T02:00:00Z"          # noqa: E731
CAPTURED_AT = "2026-09-08T00:00:00Z"


class Base(unittest.TestCase):
    def setUp(self):
        self.banco = MemoriaDescartavel()
        self.armazem = ArmazemDeMentira()
        self.addCleanup(self.banco.fechar)
        self.pai = self.criar_raw("IT-W-1", "IT/x/DOCUMENT/pai.pdf", "a" * 64)

    def criar_raw(self, run_id, caminho, sha, pais="IT"):
        self.banco.aplicar(
            "insert into public.collection_run (run_id, platform, started_at, "
            "rule_version, source_country) values ('%s','t','%s','1','%s') "
            "on conflict (run_id) do nothing;"
            % (run_id, CAPTURED_AT, pais))
        # 025: SAO DUAS ESPECIES. Uma observacao que se diz preservada tem de
        # dizer QUAL copia preservou, e a trava do banco recusa se ela nao
        # disser. A fixture escreve as duas, como a producao passou a escrever.
        self.banco.aplicar(
            "insert into public.storage_object (storage_path, media_type, "
            "bytes, sha256) values ('%s','application/pdf',100,'%s') "
            "on conflict (storage_path) do nothing;" % (caminho, sha))
        self.banco.aplicar(
            "insert into public.raw_asset (run_id, storage_path, media_type, "
            "bytes, sha256, captured_at, storage_object_id) "
            "select '%s','%s','application/pdf',100,'%s','%s', o.id "
            "from public.storage_object o where o.storage_path = '%s';"
            % (run_id, caminho, sha, CAPTURED_AT, caminho))
        return int(self.banco.con.execute(
            "select id from raw_asset where storage_path = ?",
            (caminho,)).fetchone()[0])

    def pedido(self, **extra):
        p = {"raw_asset_id": self.pai, "country": "IT",
             "kind": "TEXT_EXTRACTION", "producer": "texto-de-pdf",
             "producer_version": "1", "parameters": None,
             "serie_posicao": None, "media_type": "text/plain"}
        p.update(extra)
        return p

    def escrever(self, dados=TEXTO_A, **extra):
        return preservar_derivado(self.pedido(**extra), dados, self.armazem,
                                  self.banco, relogio=RELOGIO)


class OCaminhoNormal(Base):
    """1, 2, 11 e 28 — o básico, e a imutabilidade do pai."""

    def test_1_pai_existe_entao_INSERTED(self):
        r = self.escrever()
        self.assertEqual(r["ESTADO"], INSERTED)
        self.assertEqual(self.banco.contar("derived_artifact"), 1)

    def test_2_e_3_pai_ausente_e_recusado_ANTES_do_armazem(self):
        """A recusa acontece antes de qualquer byte ser guardado. Subir bytes
        para um pai que não existe seria sujar o armazém por nada."""
        r = self.escrever(raw_asset_id=999999)
        self.assertEqual(r["ESTADO"], RAW_PARENT_NOT_FOUND)
        self.assertFalse(r["BYTES_GUARDADOS"])
        self.assertEqual(len(self.armazem.objetos), 0)
        self.assertEqual(self.banco.contar("derived_artifact"), 0)

    def test_3_o_sha_do_pai_e_LIDO_nao_aceite_do_chamador(self):
        """Era assim que se conseguia declarar `raw_asset_id` = A com
        `parent_sha256` = B. O chamador nem tem por onde tentar: se mandar o
        campo, ele é ignorado — quem manda é a linha do banco."""
        r = self.escrever(parent_sha256="f" * 64)
        linha = r["LINHA_ESCRITA"]
        self.assertEqual(linha["parent_sha256"], "a" * 64)

    def test_11_primeiro_write_e_INSERTED_com_o_caminho_derivado_da_receita(self):
        r = self.escrever()
        self.assertTrue(r["STORAGE_PATH"].startswith(
            "IT/derivados/TEXT_EXTRACTION/texto-de-pdf-1-"))
        self.assertTrue(r["STORAGE_PATH"].endswith(".txt"))
        self.assertTrue(r["NOVO_UPLOAD"])

    def test_28_o_bruto_fica_imutavel(self):
        antes = dict(self.banco.raw_por_id(self.pai))
        self.escrever()
        self.assertEqual(antes, dict(self.banco.raw_por_id(self.pai)))


class OPaisEDoPaiNaoDoChamador(Base):
    """O chamador não decide onde o byte derivado vai morar."""

    def test_o_chamador_nao_leva_um_bruto_italiano_para_ES(self):
        """Um `country="ES"` no pedido de um bruto italiano poria o artefato a
        morar no sítio errado, e ninguém reparava. O país vem do pai — do
        `source_country` da corrida que o trouxe."""
        r = self.escrever(country="ES")
        self.assertTrue(r["STORAGE_PATH"].startswith("IT/"),
                        "o caminho seguiu o chamador: %s" % r["STORAGE_PATH"])

    def test_pai_sem_pais_provado_fica_NAO_SEI(self):
        """Onde o pai não prova, não se infere."""
        sem = self.criar_raw("IT-SEM-PAIS", "IT/z/DOCUMENT/sem.pdf", "b" * 64,
                             pais="NAO_SEI")
        r = self.escrever(raw_asset_id=sem)
        self.assertTrue(r["STORAGE_PATH"].startswith("NAO_SEI/"))


class OsParametrosTemUmDono(unittest.TestCase):
    """4, 5, 6 — a serialização canónica, provada."""

    def test_4_sem_parametros_e_o_hash_da_cadeia_vazia(self):
        vazio = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
        self.assertEqual(parametros_canonicos(None), b"")
        self.assertEqual(hash_dos_parametros(None), vazio)

    def test_5_a_ordem_das_chaves_nao_muda_o_hash(self):
        """`{"a":1,"b":2}` e `{"b":2,"a":1}` são os MESMOS parâmetros. Se a
        ordem contasse, o mesmo pedido daria duas derivações diferentes."""
        self.assertEqual(hash_dos_parametros({"a": 1, "b": 2}),
                         hash_dos_parametros({"b": 2, "a": 1}))

    def test_5b_acentos_listas_booleanos_e_nulos_sao_deterministicos(self):
        p1 = {"lingua": "città", "paginas": [1, 2, 3], "ocr": False, "x": None}
        p2 = {"x": None, "ocr": False, "paginas": [1, 2, 3], "lingua": "città"}
        self.assertEqual(hash_dos_parametros(p1), hash_dos_parametros(p2))
        # e o acento viaja como acento, nao como escape
        self.assertIn("città".encode("utf-8"), parametros_canonicos(p1))

    def test_5c_a_formatacao_nao_entra_na_conta(self):
        """Espaços e indentação não são parâmetros. A forma canónica não os tem."""
        self.assertNotIn(b" ", parametros_canonicos({"a": 1, "b": 2}))

    def test_6_parametros_diferentes_dao_hashes_diferentes(self):
        self.assertNotEqual(hash_dos_parametros({"a": 1}),
                            hash_dos_parametros({"a": 2}))
        self.assertNotEqual(hash_dos_parametros(None), hash_dos_parametros({}))

    def test_o_hash_e_calculado_num_sitio_so(self):
        """Duas implementações da mesma regra são duas verdades livres para
        divergir. Nenhum outro ficheiro pode recalcular isto."""
        for pasta in ("guarda", "coleta"):
            for nome in os.listdir(os.path.join(RAIZ, pasta)):
                if not nome.endswith(".py") or nome == "preservar_derivado.py":
                    continue
                with open(os.path.join(RAIZ, pasta, nome), encoding="utf-8") as f:
                    fonte = f.read()
                self.assertNotIn("parameters_hash =", fonte,
                                 "%s/%s recalcula o hash dos parametros" % (pasta, nome))


class OEnderecoCarregaAReceitaInteira(unittest.TestCase):
    """Os oito casos do caminho — e o que o defeito antigo colapsava.

    O caminho antigo era `PAIS/derivados/TIPO/<pai16>-<produtor>-<versao>` e
    **não incluía o `parameters_hash`**. O mesmo PDF a 150 e a 300 dpi são duas
    derivações que a `022` distingue — e disputavam o MESMO endereço.

        SE A IDENTIDADE DO BANCO DIZ QUE SÃO DUAS DERIVAÇÕES,
        O ENDEREÇO TEM DE PERMITIR QUE AS DUAS EXISTAM.
    """

    def ident(self, **extra):
        d = {"parent_sha256": "a" * 64, "kind": "TEXT_EXTRACTION",
             "producer": "texto-de-pdf", "producer_version": "1",
             "parameters_hash": hash_dos_parametros(None),
             "serie_posicao": None}
        d.update(extra)
        return d

    def caminho(self, **extra):
        return caminho_do_derivado(self.ident(**extra), "text/plain", "IT")

    def test_p1_mesma_identidade_mesmo_caminho(self):
        self.assertEqual(self.caminho(), self.caminho())

    def test_p2_parameters_diferentes_dao_caminhos_diferentes(self):
        """O CASO QUE ESTAVA QUEBRADO. 150 dpi e 300 dpi já não colidem."""
        a = self.caminho(parameters_hash=hash_dos_parametros({"dpi": 150}))
        b = self.caminho(parameters_hash=hash_dos_parametros({"dpi": 300}))
        self.assertNotEqual(a, b)

    def test_p3_producer_version_diferente_da_caminho_diferente(self):
        self.assertNotEqual(self.caminho(), self.caminho(producer_version="2"))

    def test_p4_kind_diferente_da_caminho_diferente(self):
        self.assertNotEqual(self.caminho(), self.caminho(kind="OCR"))

    def test_p5_serie_posicao_diferente_da_caminho_diferente(self):
        self.assertNotEqual(self.caminho(serie_posicao=0),
                            self.caminho(serie_posicao=1))

    def test_p6_pai_diferente_da_caminho_diferente(self):
        self.assertNotEqual(self.caminho(), self.caminho(parent_sha256="c" * 64))

    def test_p7_o_discriminante_e_o_hash_INTEIRO_da_receita(self):
        """Não um prefixo de 16 caracteres a fazer de identidade."""
        caminho = self.caminho()
        self.assertIn(id_da_receita(self.ident()), caminho)
        self.assertEqual(len(id_da_receita(self.ident())), 64)
        # e o pai NAO entra em prefixo curto solto
        self.assertNotIn("a" * 16 + "-", caminho)

    def test_p8_o_sha_do_FILHO_nao_entra_no_caminho(self):
        """Se entrasse, o `DERIVATION_DRIFT` ganharia um endereço novo e
        deixaria de ser drift — passaria a ser dois artefatos calados."""
        import inspect
        from guarda import preservar_derivado as pd
        fonte = inspect.getsource(pd.caminho_do_derivado)
        self.assertNotIn("sha_filho", fonte)
        self.assertEqual(len(inspect.signature(pd.caminho_do_derivado).parameters), 3)


class OTempoEOsBytesSaoMedidos(Base):
    """7, 8, 9, 10 — o writer mede; o chamador não fornece."""

    def test_7_derived_at_vem_do_relogio_do_writer(self):
        r = self.escrever()
        self.assertEqual(r["LINHA_ESCRITA"]["derived_at"], RELOGIO())

    def test_8_o_chamador_NAO_consegue_passar_o_captured_at_como_derived_at(self):
        """A trava que o banco não pode dar: ele vê um timestamp, não vê de onde
        veio. Aqui o campo nem é lido do pedido."""
        r = self.escrever(derived_at=CAPTURED_AT)
        self.assertNotEqual(r["LINHA_ESCRITA"]["derived_at"], CAPTURED_AT)
        self.assertEqual(r["LINHA_ESCRITA"]["derived_at"], RELOGIO())

    def test_9_e_10_sha_e_bytes_vem_dos_bytes_reais(self):
        """Um `sha256` informado pelo chamador é uma afirmação; medido é um
        facto. Aqui manda-se um valor falso e ele é ignorado."""
        r = self.escrever(sha256="f" * 64, bytes=99999)
        self.assertEqual(r["LINHA_ESCRITA"]["sha256"], sha256(TEXTO_A))
        self.assertEqual(int(r["LINHA_ESCRITA"]["bytes"]), len(TEXTO_A))


class ORetryEReencontro(Base):
    """12, 13, 14, 30 — repetir é reencontrar, e reencontrar é comparar."""

    def test_12_13_14_retry_identico_e_REUSED_sem_upload_e_sem_linha(self):
        self.escrever()
        envios, linhas = self.armazem.envios, self.banco.contar("derived_artifact")
        r = self.escrever()
        self.assertEqual(r["ESTADO"], REUSED)
        self.assertFalse(r["NOVO_UPLOAD"])
        self.assertEqual(self.armazem.envios, envios)
        self.assertEqual(self.banco.contar("derived_artifact"), linhas)

    def test_30_o_writer_nunca_usa_DO_NOTHING_como_prova_de_REUSED(self):
        """O `insert` deste dono não tem `on conflict`, de propósito: ele quer
        o erro para poder ir LER o que lá está."""
        from guarda.preservar_derivado import sql_do_derivado
        sql = sql_do_derivado({"raw_asset_id": 1, "parent_sha256": "a" * 64,
                               "kind": "TEXT_EXTRACTION", "producer": "p",
                               "producer_version": "1",
                               "parameters_hash": "b" * 64, "sha256": "c" * 64,
                               "bytes": 1, "media_type": "text/plain",
                               "storage_path": "x", "derived_at": "t"})
        self.assertNotIn("on conflict", sql.lower())
        # A prosa deste ficheiro FALA de `on conflict do nothing` — ela explica
        # por que ele nao e usado. O que nao pode existir e a coisa: uma linha
        # de codigo que o escreva num SQL.
        with open(os.path.join(RAIZ, "guarda", "preservar_derivado.py"),
                  encoding="utf-8") as f:
            for linha in f:
                nua = linha.strip()
                if nua.startswith("#") or not nua:
                    continue
                if "on conflict" in nua.lower():
                    self.assertNotIn("insert into", nua.lower(),
                                     "ha um insert com on conflict: %s" % nua)


class ODriftGrita(Base):
    """15, 16, 17 — O CASO ADVERSARIAL CENTRAL."""

    def test_15_e_16_a_mesma_receita_com_outro_resultado_e_DRIFT(self):
        """Primeira execução produziu AAAA. A segunda, por um defeito de versão
        ou de ambiente, produz BBBB — e a identidade continua igual.

        O sistema tem de GRITAR. Nunca `REUSED`, nunca `UPDATE`, nunca apagar.
        """
        self.escrever(TEXTO_A)
        r = self.escrever(TEXTO_B)
        self.assertEqual(r["ESTADO"], DERIVATION_DRIFT)
        campos = {d["CAMPO"] for d in r["DIVERGENCIAS"]}
        self.assertIn("sha256", campos)
        self.assertIn("bytes", campos)

    def test_15b_o_antigo_NAO_e_apagado_nem_sobrescrito(self):
        primeiro = self.escrever(TEXTO_A)["LINHA_ESCRITA"]
        self.escrever(TEXTO_B)
        agora = self.banco.con.execute(
            "select * from derived_artifact").fetchall()
        self.assertEqual(len(agora), 1)
        self.assertEqual(dict(agora[0])["sha256"], primeiro["sha256"])

    def test_16b_e_nenhum_byte_novo_sobe_no_drift(self):
        self.escrever(TEXTO_A)
        envios = self.armazem.envios
        r = self.escrever(TEXTO_B)
        self.assertEqual(self.armazem.envios, envios)
        self.assertFalse(r["BYTES_GUARDADOS"])

    def test_17_media_type_diferente_tambem_e_DRIFT(self):
        """`media_type` é resultado, não receita: se mudou, a derivação não é a
        mesma coisa que estava lá."""
        self.escrever(TEXTO_A)
        r = self.escrever(TEXTO_A, media_type="application/json")
        # o caminho muda com a extensao, mas a identidade da receita e a mesma
        self.assertEqual(r["ESTADO"], DERIVATION_DRIFT)
        self.assertIn("media_type", {d["CAMPO"] for d in r["DIVERGENCIAS"]})


class ASegundaCapturaDoMesmoConteudo(Base):
    """18, 19, 20 — o grão CONTEÚDO POR RECEITA, do lado do writer."""

    def test_18_19_20_outra_captura_mesmos_bytes_e_REUSED(self):
        """Duas capturas do mesmo conteúdo, a mesma receita: UMA derivação.

        A testemunha **não se troca** — trocá-la reescreveria a história por
        nada — e a segunda captura continua inteira em `raw_asset`.
        """
        self.escrever()
        gemeo = self.criar_raw("IT-W-2", "IT/y/DOCUMENT/copia-2.pdf", "a" * 64)
        r = self.escrever(raw_asset_id=gemeo)

        self.assertEqual(r["ESTADO"], REUSED)
        self.assertEqual(self.banco.contar("derived_artifact"), 1)
        # 20 · a testemunha ficou a apontar para a PRIMEIRA copia
        self.assertEqual(int(r["TESTEMUNHA_NO_BANCO"]), self.pai)
        self.assertEqual(r["TESTEMUNHA_DESTA_CHAMADA"], gemeo)
        self.assertEqual(int(self.banco.con.execute(
            "select raw_asset_id from derived_artifact").fetchone()[0]), self.pai)
        # 19 · e as duas capturas continuam inteiras
        self.assertEqual(self.banco.con.execute(
            "select count(*) from raw_asset where sha256 = ?",
            ("a" * 64,)).fetchone()[0], 2)


class ACorrida(Base):
    """21 e 22 — violação de unicidade não é sucesso automático."""

    def _outro_escritor_entra(self, dados):
        """Insere a mesma identidade entre a nossa leitura e o nosso insert."""
        original = self.banco.aplicar
        estado = {"feito": False}

        def intruso(sql):
            if not estado["feito"] and "insert into public.derived_artifact" in sql:
                estado["feito"] = True
                self.banco.aplicar = original
                preservar_derivado(self.pedido(), dados, ArmazemDeMentira(),
                                   self.banco, relogio=RELOGIO)
                self.banco.aplicar = intruso
            original(sql)

        self.banco.aplicar = intruso
        try:
            return self.escrever(TEXTO_A)
        finally:
            self.banco.aplicar = original

    def test_21_race_com_o_mesmo_resultado_e_REUSED_AFTER_RACE(self):
        r = self._outro_escritor_entra(TEXTO_A)
        self.assertEqual(r["ESTADO"], REUSED_AFTER_RACE)
        self.assertEqual(self.banco.contar("derived_artifact"), 1)
        self.assertIn("comparado", r["PORQUE"])

    def test_22_race_com_resultado_diferente_e_DRIFT(self):
        r = self._outro_escritor_entra(TEXTO_B)
        self.assertEqual(r["ESTADO"], DERIVATION_DRIFT)
        self.assertEqual(self.banco.contar("derived_artifact"), 1)


class OArmazemNaoSeSobrescreve(Base):
    """23, 24, 25, 26 — os bytes e a memória, e nenhum apaga o outro."""

    def _caminho(self, **extra):
        from guarda.preservar_derivado import hash_dos_parametros as _h
        ident = {"parent_sha256": "a" * 64, "kind": "TEXT_EXTRACTION",
                 "producer": "texto-de-pdf", "producer_version": "1",
                 "parameters_hash": _h(None), "serie_posicao": None}
        ident.update(extra)
        return caminho_do_derivado(ident, "text/plain", "IT")

    def test_23_objeto_ja_existente_com_os_mesmos_bytes_e_reutilizado(self):
        caminho = self._caminho()
        self.armazem.enviar(caminho, TEXTO_A, "text/plain")
        envios = self.armazem.envios
        r = self.escrever()
        self.assertEqual(r["ESTADO"], INSERTED)
        self.assertEqual(self.armazem.envios, envios, "subiu por cima do igual")

    def test_24_objeto_ja_existente_com_bytes_diferentes_e_STORAGE_CONFLICT(self):
        """Não se apaga evidência para «tentar de novo»."""
        caminho = self._caminho()
        self.armazem.enviar(caminho, b"outra coisa qualquer", "text/plain")
        r = self.escrever()
        self.assertEqual(r["ESTADO"], STORAGE_CONFLICT)
        self.assertEqual(self.armazem.ler(caminho), b"outra coisa qualquer")
        self.assertEqual(self.banco.contar("derived_artifact"), 0)

    def test_25_armazem_grava_e_banco_falha_NAO_apaga_os_bytes(self):
        """A lei do G-42, aplicada ao derivado."""
        original = self.banco.aplicar

        def recusar(sql):
            if "insert into public.derived_artifact" in sql:
                raise IOError("o banco recusou")
            original(sql)

        self.banco.aplicar = recusar
        r = self.escrever()
        self.assertEqual(r["ESTADO"], METADATA_NOT_RECONCILED)
        self.assertEqual(len(self.armazem.objetos), 1)
        self.assertEqual(r["BYTE_APAGADO_COMO_COMPENSACAO"], "NAO")
        self.assertEqual(self.banco.contar("derived_artifact"), 0)

    def test_26_linha_existe_mas_o_byte_sumiu_NAO_e_REUSED(self):
        """ASSERÇÃO ANTIGA: este teste exigia `REUSED`, e chamava a isso «limite
        conhecido». Estava a **canonizar uma falha** — um teste que exige o
        comportamento errado impede quem o vem consertar, e ainda dá ao defeito
        um ar de decisão.

            UMA LINHA NO BANCO NÃO É PROVA DE QUE O BYTE AINDA EXISTE.

        Agora o `REUSED` só sai depois de o artefato ser encontrado no armazém e
        o seu hash ser conferido. Sem byte, `STORAGE_MISSING`.
        """
        self.escrever()
        self.armazem.objetos.clear()
        r = self.escrever()
        self.assertEqual(r["ESTADO"], STORAGE_MISSING)
        self.assertFalse(r["BYTES_CONFERIDOS_NO_ARMAZEM"])
        self.assertIn("NAO se reenvia", r["O_QUE_NAO_SE_FAZ"])

    def test_26b_com_o_byte_la_o_REUSED_diz_que_o_conferiu(self):
        self.escrever()
        r = self.escrever()
        self.assertEqual(r["ESTADO"], REUSED)
        self.assertTrue(r["BYTES_CONFERIDOS_NO_ARMAZEM"])

    def test_26c_byte_trocado_debaixo_da_ficha_e_STORAGE_CONFLICT(self):
        """O artefato continua lá, mas já não é o mesmo. Pior do que sumir:
        parece saudável."""
        r1 = self.escrever()
        self.armazem.objetos[r1["STORAGE_PATH"]] = (b"outra coisa", "text/plain")
        r = self.escrever()
        self.assertEqual(r["ESTADO"], STORAGE_CONFLICT)
        self.assertNotEqual(r["SHA_NO_ARMAZEM"], r["SHA_NA_LINHA"])


class APosLeituraConfereCampos(Base):
    """27 e 29 — contar não é conferir; e apagar o pai continua recusado."""

    def test_27_contagem_certa_com_campo_errado_reprova(self):
        """A linha entra, mas com outro `producer`. A contagem bate; a
        conferência campo a campo não."""
        original = self.banco.aplicar

        def adulterar(sql):
            original(sql.replace("'texto-de-pdf'", "'outra-ferramenta'"))

        self.banco.aplicar = adulterar
        r = self.escrever()
        self.assertEqual(r["ESTADO"], METADATA_NOT_RECONCILED)
        self.assertEqual(self.banco.contar("derived_artifact"), 1)

    def test_27b_o_caminho_feliz_confere_todos_os_campos(self):
        r = self.escrever()
        self.assertEqual(r["CAMPOS_CONFERIDOS"], 13)

    def test_29_apagar_o_bruto_com_derivado_e_recusado(self):
        import sqlite3
        self.escrever()
        with self.assertRaises(sqlite3.IntegrityError):
            self.banco.con.execute("delete from raw_asset where id = ?",
                                   (self.pai,))


class ONaoRegresso(unittest.TestCase):
    """As travas anti-deriva: um dono só, e ninguém a escrever por fora."""

    def test_o_executor_pdf_nao_escreve_na_tabela(self):
        with open(os.path.join(RAIZ, "coleta", "executor_texto_de_pdf.py"),
                  encoding="utf-8") as f:
            fonte = f.read()
        self.assertNotIn("derived_artifact", fonte)
        self.assertNotIn("insert into", fonte.lower())

    def test_nao_ha_writer_paralelo(self):
        proibidos = ("writer_v2", "derived_db", "derived_store",
                     "derived_repository", "derivation_run")
        for pasta in ("guarda", "coleta"):
            for nome in os.listdir(os.path.join(RAIZ, pasta)):
                for p in proibidos:
                    self.assertNotIn(p, nome)

    def test_o_writer_nao_fala_com_o_banco_nem_com_a_rede(self):
        with open(os.path.join(RAIZ, "guarda", "preservar_derivado.py"),
                  encoding="utf-8") as f:
            fonte = f.read().lower()
        for proibido in ("psycopg", "import requests", "urlopen", "sqlite3",
                         "create_client", "subprocess"):
            self.assertNotIn(proibido, fonte)

    def test_o_legado_nao_foi_tocado(self):
        """Os 43 históricos continuam onde estavam, e nenhum foi migrado."""
        registo = os.path.join(RAIZ, "data", "derivados",
                               "REGISTO-DE-ARTEFATOS.json")
        self.assertTrue(os.path.exists(registo))
        with open(registo, encoding="utf-8") as f:
            d = json.load(f)
        itens = d.get("ARTEFATOS") if isinstance(d, dict) else d
        self.assertGreater(len([a for a in itens if a.get("PARENT_SHA256")]), 0)


class OModoForwardDoExecutor(Base):
    """A ponte antiga não tinha pai. Esta tem — e prova-o de ponta a ponta.

    ⚠️ A PRIMEIRA VERSÃO DESTA PONTE PASSAVA A RECEITA E OS BYTES, E NÃO O
    `raw_asset_id`. O dono ficava sem saber qual linha de `raw_asset` era o pai
    daquele PDF, e o teste só verificava «o callback foi chamado» — o que não
    prova nada. Foi removida, e no lugar entrou `derivar_um()`.

    Aqui corre o dono REAL, contra um banco real e um armazém de teste.
    """

    def setUp(self):
        super().setUp()

    def _pdf_de_fixture(self, n=0):
        """Um PDF DE VERDADE, dos que a casa já tem.

        Construir um PDF mínimo à mão daria um teste que prova que eu sei
        montar bytes de PDF — não que a cadeia funciona. Os documentos reais
        estão aqui, o `pdftotext` abre-os, e é isso que interessa provar.
        """
        import glob
        raiz = os.path.join(RAIZ, "data", "samples", "IT-SOURCE-SAMPLES")
        achados = sorted(glob.glob(os.path.join(raiz, "*", "*.pdf")))
        if len(achados) <= n:
            self.skipTest("nao ha PDF de amostra suficiente")
        return achados[n]

    def test_ponta_a_ponta_o_filho_aponta_o_pai_certo(self):
        """raw_asset X → executor → dono → derived_artifact.raw_asset_id = X"""
        import coleta.executor_texto_de_pdf as ex
        if not ex.ha_ferramenta():
            self.skipTest("pdftotext ausente nesta maquina")
        pdf = self._pdf_de_fixture()
        r = ex.derivar_um(self.pai, pdf, self.armazem, self.banco,
                          relogio=RELOGIO)
        self.assertEqual(r["ESTADO"], INSERTED, r.get("PORQUE"))
        linha = r["LINHA_ESCRITA"]
        self.assertEqual(int(linha["raw_asset_id"]), self.pai)
        self.assertEqual(linha["parent_sha256"], "a" * 64)
        self.assertEqual(linha["producer"], ex.EXECUTOR_ID)
        # o byte do filho esta mesmo no armazem, e bate
        self.assertIn(linha["storage_path"], self.armazem.objetos)
        self.assertEqual(sha256(self.armazem.ler(linha["storage_path"])),
                         linha["sha256"])

    def test_dois_brutos_ficam_ligados_aos_filhos_certos(self):
        """Nenhum caminho global pode trocar os pais."""
        import coleta.executor_texto_de_pdf as ex
        if not ex.ha_ferramenta():
            self.skipTest("pdftotext ausente nesta maquina")
        outro = self.criar_raw("IT-W-3", "IT/x/DOCUMENT/pai-b.pdf", "b" * 64)
        ra = ex.derivar_um(self.pai, self._pdf_de_fixture(0),
                           self.armazem, self.banco, relogio=RELOGIO)
        rb = ex.derivar_um(outro, self._pdf_de_fixture(1),
                           self.armazem, self.banco, relogio=RELOGIO)
        self.assertEqual(ra["ESTADO"], INSERTED, ra.get("PORQUE"))
        self.assertEqual(rb["ESTADO"], INSERTED, rb.get("PORQUE"))
        self.assertEqual(int(ra["LINHA_ESCRITA"]["raw_asset_id"]), self.pai)
        self.assertEqual(int(rb["LINHA_ESCRITA"]["raw_asset_id"]), outro)
        self.assertEqual(ra["LINHA_ESCRITA"]["parent_sha256"], "a" * 64)
        self.assertEqual(rb["LINHA_ESCRITA"]["parent_sha256"], "b" * 64)

    def test_o_executor_nao_calcula_nada_que_e_do_dono(self):
        """O que ele entrega é a receita. Nem o `sha256` do pai viaja."""
        import ast
        import inspect

        import coleta.executor_texto_de_pdf as ex
        # SO O CORPO EXECUTAVEL. A docstring desta funcao NOMEIA os campos que
        # ela nao calcula — e procurar a palavra na prosa reprovaria justamente
        # o texto que explica a regra. Ja me enganei assim tres vezes; desta
        # vez a docstring sai antes da comparacao.
        arvore = ast.parse(inspect.getsource(ex.derivar_um).lstrip())
        corpo = arvore.body[0].body
        if (isinstance(corpo[0], ast.Expr)
                and isinstance(corpo[0].value, ast.Constant)):
            corpo = corpo[1:]
        fonte = " ".join(ast.unparse(x) for x in corpo)
        for do_dono in ("parent_sha256", "parameters_hash", "derived_at",
                        "storage_path"):
            self.assertNotIn(do_dono, fonte,
                             "o executor calcula %s, que e do dono" % do_dono)
        for da_receita in ("kind", "producer", "producer_version",
                           "parameters", "serie_posicao", "media_type"):
            self.assertIn(da_receita, fonte)

    def test_o_legado_continua_sem_o_dono(self):
        """`correr()` é o modo legado, e não conhece o writer. Os 43 históricos
        não têm `raw_asset` canónico, e não se lhes inventa um."""
        import inspect

        import coleta.executor_texto_de_pdf as ex
        fonte = inspect.getsource(ex.correr)
        self.assertNotIn("preservar_derivado", fonte)
        self.assertNotIn("entregar_ao_dono", fonte)
        self.assertNotIn("raw_asset", fonte)


if __name__ == "__main__":
    unittest.main(verbosity=2)
