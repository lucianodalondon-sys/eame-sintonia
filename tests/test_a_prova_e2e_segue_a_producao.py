#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""A PROVA DA ESTRADA TEM DE SEGUIR A PRODUCAO, E NAO IMITA-LA.

    PRODUCTION CONTRACT -> TEST FOLLOWS
    e nunca STALE TEST -> PRODUCTION WEAKENED

Duas coisas envelheceram calladas nesta casa e reprovaram estradas que
estavam boas: um dicionario de armazem escrito a mao, e uma lista de
migrations escrita a mao. Os dois eram copias de um contrato, e copia nao e
conferida por ninguem.
"""
import hashlib
import importlib.util
import os
import re
import sys
import unittest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if RAIZ not in sys.path:
    sys.path.insert(0, RAIZ)
import _gavetas  # noqa: E402,F401
from coleta import ingresso as ing  # noqa: E402
from leis import artefato as art  # noqa: E402

PROVA_E2E = os.path.join(RAIZ, "tests", "test_m2_rota_forward.py")
PROVA_ROTA = os.path.join(RAIZ, "provas", "a_rota_m2_atravessa.py")
LOJA = os.path.join(RAIZ, "data", "collection-store", "italy", "IT-T2-002")


def _fonte(caminho):
    with open(caminho, encoding="utf-8") as f:
        return f.read()


def _um_pdf():
    for base, _d, fs in os.walk(LOJA):
        for f in sorted(fs):
            if f.endswith(".pdf"):
                return os.path.join(base, f)
    raise AssertionError("nenhum PDF real no armazem de IT-T2-002")


class OFixtureFalaPeloTradutorDaProducao(unittest.TestCase):
    """O defeito `G-E2E-01`, guardado para nao voltar."""

    def test_o_fixture_nao_escreve_a_ficha_do_armazem_a_mao(self):
        s = _fonte(PROVA_E2E)
        self.assertIn("_ing.para_o_dono_do_raw(ficha, {})", s,
                      "a prova voltou a imitar a lingua do armazem")
        self.assertNotIn("'SOURCE_SLUG': 'IT-T2-002'", s,
                         "voltou o dicionario escrito a mao")

    def test_o_tradutor_carrega_a_fonte_que_o_writer_exige(self):
        """A razao pela qual o fixture antigo reprovava a estrada."""
        f = art.raw_do_disco(_um_pdf(), RAIZ, COUNTRY_SCOPE="IT",
                             SOURCE_ID="IT-T2-002")
        self.assertEqual(ing.para_o_dono_do_raw(f, {})["SOURCE_ID"],
                         "IT-T2-002")

    def test_a_ficha_a_mao_perdia_campos_que_a_producao_entrega(self):
        """MEDIDO: sete campos diferiam, e um deles matava a prova."""
        f = art.raw_do_disco(_um_pdf(), RAIZ, COUNTRY_SCOPE="IT",
                             SOURCE_ID="IT-T2-002")
        prod = ing.para_o_dono_do_raw(f, {})
        a_mao = {"COUNTRY", "SOURCE_SLUG", "ARTIFACT_KIND", "NAME",
                 "SOURCE_NATIVE_ID", "SHA256", "BYTES", "MEDIA_TYPE",
                 "CAPTURED_AT", "SOURCE_URL"}
        em_falta = sorted(set(prod) - a_mao)
        self.assertIn("SOURCE_ID", em_falta,
                      "o campo que derrubava a prova deixou de faltar na "
                      "versao a mao — remedir a deriva")


class ACadeiaDeMigrationsVemDoDisco(unittest.TestCase):
    """A segunda copia que envelheceu, e que ja tinha envelhecido uma vez."""

    def _mod(self):
        spec = importlib.util.spec_from_file_location("rota_t", PROVA_ROTA)
        m = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(m)
        return m

    def test_a_lista_nao_esta_escrita_a_mao(self):
        s = _fonte(PROVA_ROTA)
        self.assertNotIn("'025', '026']", s,
                         "a lista de migrations voltou a ser escrita a mao")
        self.assertIn("_cadeia_de_migrations()", s)

    def test_a_cadeia_inclui_toda_migration_do_disco_menos_a_verificacao(self):
        m = self._mod()
        pasta = os.path.join(RAIZ, "supabase", "migrations")
        no_disco = {f.split("_", 1)[0] for f in os.listdir(pasta)
                    if f.endswith(".sql")}
        self.assertEqual(set(m.MIGRATIONS), no_disco - set(m._SO_VERIFICA),
                         "a cadeia divergiu da pasta")

    def test_a_ultima_migration_do_disco_esta_na_cadeia(self):
        """O defeito concreto: a 027 existia e a prova parava na 026."""
        m = self._mod()
        pasta = os.path.join(RAIZ, "supabase", "migrations")
        ultima = sorted(f.split("_", 1)[0] for f in os.listdir(pasta)
                        if f.endswith(".sql"))[-1]
        self.assertIn(ultima, m.MIGRATIONS,
                      "a prova atravessa um esquema atras da realidade")

    def test_a_verificacao_pos_aplicacao_fica_de_fora_com_motivo(self):
        m = self._mod()
        self.assertEqual(m._SO_VERIFICA, ("008",))
        self.assertIn("VERIFICACAO POS-APLICACAO", _fonte(PROVA_ROTA))


class NadaFabricaAFonte(unittest.TestCase):
    """As negativas: o que NAO pode virar `SOURCE_ID` na ficha do armazem."""

    def _sem_fonte(self):
        return art.raw_do_disco(_um_pdf(), RAIZ, COUNTRY_SCOPE="IT")

    def test_sem_fonte_declarada_a_ficha_confessa_e_nao_inventa(self):
        d = ing.para_o_dono_do_raw(self._sem_fonte(), {})
        self.assertEqual(d["SOURCE_ID"], art.NAO_SEI,
                         "a traducao inventou uma fonte")

    def test_o_sha_nao_vira_fonte(self):
        f = self._sem_fonte()
        d = ing.para_o_dono_do_raw(f, {})
        self.assertNotEqual(d["SOURCE_ID"], f.SHA256)
        self.assertNotIn(f.SHA256[:16], str(d["SOURCE_ID"]))

    def test_o_caminho_nao_vira_fonte(self):
        """O ficheiro VIVE em .../IT-T2-002/... e mesmo assim nao conta."""
        f = self._sem_fonte()
        self.assertIn("IT-T2-002", f.STORAGE_LOCATION)
        d = ing.para_o_dono_do_raw(f, {})
        self.assertEqual(d["SOURCE_ID"], art.NAO_SEI,
                         "o nome do diretorio virou identidade")

    def test_o_slug_nao_e_a_fonte(self):
        """`it-t2-002` e o ENDERECO. `IT-T2-002` e a identidade.

        Os dois viajam em campos diferentes de proposito: o slug nao se
        reconverte em codigo canonico sem adivinhar.
        """
        f = art.raw_do_disco(_um_pdf(), RAIZ, COUNTRY_SCOPE="IT",
                             SOURCE_ID="IT-T2-002")
        d = ing.para_o_dono_do_raw(f, {})
        self.assertEqual(d["SOURCE_SLUG"], "it-t2-002")
        self.assertEqual(d["SOURCE_ID"], "IT-T2-002")
        self.assertNotEqual(d["SOURCE_SLUG"], d["SOURCE_ID"])

    def test_o_document_id_nao_e_inventado(self):
        d = ing.para_o_dono_do_raw(self._sem_fonte(), {})
        self.assertIsNone(d.get("DOCUMENT_ID"),
                          "nasceu um DOCUMENT_ID que a fonte nao provou")


class OEscopoDaProvaEstaDeclarado(unittest.TestCase):
    """O nome diz «rota forward». O relatorio tem de dizer onde ela comeca."""

    def test_a_prova_declara_que_nao_prova_producao_nem_ready(self):
        s = _fonte(PROVA_ROTA)
        self.assertIn("o que NAO prova", s)
        self.assertIn("READY", s)

    def test_a_prova_nao_finge_comecar_no_pedido(self):
        """REQUEST/ORCHESTRATOR/EXECUTOR continuam por observar."""
        s = _fonte(PROVA_ROTA)
        for etapa in ("DERIVED", "STRUCTURED", "ADMISSION"):
            self.assertIn(etapa, s)
        self.assertNotIn("END_TO_END do pedido", s)

    def test_o_gap_do_raw_continua_declarado_e_nao_foi_fechado_de_lado(self):
        """`G-RAW-01` e o blocker seguinte, e nao desta missao."""
        from coleta import derivacao_forward as df
        nomes = {g[0] for g in df.GAPS}
        self.assertIn("RAW_FORWARD_NAO_EMITE", nomes,
                      "o gap do RAW desapareceu sem missao que o fechasse")


class AFonteQueATERRAEACANONICA(unittest.TestCase):
    """QUATRO MUTANTES SOBREVIVERAM AQUI, E OS TRES PRIMEIROS SAO O MESMO.

    Trocar `IT-T2-002` por `it-t2-002`, pelo sha, ou por uma expressao que
    LE O CAMINHO — a travessia completava-se na mesma, porque o escritor
    aceita qualquer texto que nao seja sentinela.

        ATRAVESSAR NAO E ATRAVESSAR COM A IDENTIDADE CERTA.

    E o terceiro nao se apanha por valor nenhum: derivar do caminho da
    EXACTAMENTE a mesma string. Contra ele so vale prova estrutural.
    """

    MODELO = os.path.join(RAIZ, "system-map", "data", "estradas-it.model.json")

    def _canario(self):
        import json
        with open(self.MODELO, encoding="utf-8") as f:
            return json.load(f)["CANARIO"]["SOURCE_ID"]

    def test_o_fixture_declara_a_fonte_do_canario(self):
        """O dono de «qual fonte esta rota prova» e o modelo, nao o fixture."""
        s = _fonte(PROVA_E2E)
        self.assertIn("SOURCE_ID='%s'" % self._canario(), s,
                      "o fixture deixou de declarar a fonte do canario")

    def test_a_fonte_declarada_nao_e_o_slug(self):
        c = self._canario()
        self.assertEqual(c, c.upper(),
                         "o canario esta em minusculas: isso e endereco")
        self.assertNotIn("SOURCE_ID='%s'" % c.lower(), _fonte(PROVA_E2E),
                         "o fixture escreveu o SLUG onde vai a identidade")

    def test_a_fonte_do_fixture_e_um_literal_e_nao_vem_do_caminho(self):
        """ESTRUTURAL, e nao por valor.

        Derivar `IT-T2-002` do caminho produz a MESMA string. Nenhuma
        comparacao de valores apanha isso — so olhar para a forma do codigo.

            QUANDO O DEFEITO DA O VALOR CERTO,
            SO A ESTRUTURA O DENUNCIA.
        """
        import ast
        arv = ast.parse(_fonte(PROVA_E2E))
        achou = False
        for no in ast.walk(arv):
            if not isinstance(no, ast.Call):
                continue
            for kw in no.keywords:
                if kw.arg != "SOURCE_ID":
                    continue
                achou = True
                self.assertIsInstance(
                    kw.value, ast.Constant,
                    "a fonte do fixture e uma EXPRESSAO — se ela le o "
                    "caminho, a prova fabrica a identidade que devia "
                    "declarar")
                self.assertIsInstance(kw.value.value, str)
        self.assertTrue(achou, "nenhuma fonte declarada no fixture")

    def test_a_guarda_da_ficha_a_mao_procura_alguma_coisa(self):
        """Uma guarda com agulha vazia passa sempre.

            UM `assertIn('', x)` E UM TESTE QUE JA NASCEU MORTO.
        """
        s = _fonte(os.path.join(RAIZ, "tests",
                                "test_a_prova_e2e_segue_a_producao.py"))
        # ⚠️ E A VERIFICACAO E ESTRUTURAL, NAO TEXTUAL — a primeira versao
        # usava uma expressao regular e apanhou o EXEMPLO dentro da docstring
        # acima, que cita o padrao mau de proposito.
        #
        #     UM TEXTO NAO DISTINGUE O EXEMPLO DA OCORRENCIA.
        #
        # Esta casa ja aprendeu isto no §60, com um comentario que explicava a
        # ausencia a servir de prova da presenca.
        import ast
        for no in ast.walk(ast.parse(s)):
            if not isinstance(no, ast.Call):
                continue
            alvo = getattr(no.func, "attr", None)
            if alvo not in ("assertIn", "assertNotIn") or not no.args:
                continue
            agulha = no.args[0]
            if isinstance(agulha, ast.Constant) and isinstance(
                    agulha.value, str):
                self.assertTrue(agulha.value.strip(),
                                "ha uma guarda a procurar a string vazia")


DSN = os.environ.get("BANCO_DESCARTAVEL_URL") or ""


@unittest.skipUnless(DSN, "sem PostgreSQL descartavel")
class AFonteCHEGAAOBANCOINTEIRA(unittest.TestCase):
    """A prova que nenhum teste de string faz: ler do banco o que aterrou."""

    def test_o_source_id_no_raw_asset_e_o_do_canario(self):
        import json
        import subprocess
        with open(os.path.join(RAIZ, "system-map", "data",
                               "estradas-it.model.json"), encoding="utf-8") as f:
            canario = json.load(f)["CANARIO"]["SOURCE_ID"]
        r = subprocess.run(
            ["psql", DSN, "-tA", "-c",
             "select distinct source_id from public.raw_asset"],
            capture_output=True, text=True)
        fontes = [x for x in (r.stdout or "").split() if x]
        if not fontes:
            self.skipTest("nenhuma observacao no banco: corra a prova antes")
        self.assertEqual(set(fontes), {canario},
                         "aterrou uma fonte que nao e a do canario: %s"
                         % fontes)


if __name__ == "__main__":
    unittest.main()
