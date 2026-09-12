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
import io
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


# ⚠️ UMA GUARDA ESCRITA DENTRO DO `assertIn` NAO TEM QUEM A CONFIRA.
#
# MEDIDO: enfraquecer a agulha (`assertIn("x", s + "x")`) nao partia nada — o
# mutante sobrevivia. A regra escrita a direito dentro da asercao so sabe
# responder sobre o ficheiro real, e um SIM sozinho nao distingue uma guarda
# que morde de uma que ja nao morde.
#
# Isolada, a regra responde a DUAS perguntas: SIM ao ficheiro real, e NAO a um
# exemplo escrito a mao. Enfraquece-la passa a partir a segunda.
def _fixture_fala_pelo_tradutor(texto):
    """A regra do `G-E2E-01`, isolada para poder ser ela propria conferida."""
    return ("_ing.para_o_dono_do_raw(ficha, {})" in texto
            and "'SOURCE_SLUG': 'IT-T2-002'" not in texto)


# Dois exemplos sinteticos: um que a regra tem de aceitar, e um que ela tem de
# recusar. Sao curtos de proposito — nao sao o ficheiro, sao a regra.
_EXEMPLO_BOM = """
        ficha = _art.raw_do_disco(caminho, RAIZ, SOURCE_ID='IT-T2-002')
        art = _ing.para_o_dono_do_raw(ficha, {})
"""
_EXEMPLO_A_MAO = """
        art = {'SOURCE_SLUG': 'IT-T2-002', 'SHA256': sha256(dados),
               'BYTES': len(dados), 'MEDIA_TYPE': 'application/pdf'}
"""


class OFixtureFalaPeloTradutorDaProducao(unittest.TestCase):
    """O defeito `G-E2E-01`, guardado para nao voltar."""

    def test_o_fixture_nao_escreve_a_ficha_do_armazem_a_mao(self):
        self.assertTrue(_fixture_fala_pelo_tradutor(_fonte(PROVA_E2E)),
                        "a prova voltou a imitar a lingua do armazem")

    def test_e_a_regra_RECUSA_a_ficha_escrita_a_mao(self):
        """⚠️ SO O NAO PROVA QUE A GUARDA MORDE. O SIM sozinho nao prova."""
        self.assertFalse(_fixture_fala_pelo_tradutor(_EXEMPLO_A_MAO),
                         "a regra aceita um dicionario escrito a mao:"
                         " ela deixou de morder")
        self.assertFalse(
            _fixture_fala_pelo_tradutor(_EXEMPLO_A_MAO + _EXEMPLO_BOM),
            "chamar o tradutor nao apaga o dicionario a mao ao lado")

    def test_e_ACEITA_a_ficha_que_vem_do_dono(self):
        self.assertTrue(_fixture_fala_pelo_tradutor(_EXEMPLO_BOM),
                        "a regra recusa a forma correta: ela morde a mais")

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

    def test_o_gap_do_raw_fechou_e_nao_voltou_a_ser_declarado(self):
        """⚠️ ESTE TESTE MUDOU DE LADO, E ISSO E O NORMAL.

        Ate C-MAKE-RAW-OBSERVABLE-V1 ele exigia que `RAW_FORWARD_NAO_EMITE`
        CONTINUASSE declarado — «o gap do RAW desapareceu sem missao que o
        fechasse». A missao veio, e o gap fechou.

            UM TESTE QUE SO ESTA CERTO ENQUANTO NADA AVANCA
            E UM TESTE QUE MEDE O PRIMEIRO DIA.

        Agora ele exige o contrario: quem o re-declarar tem de o fazer com uma
        medicao, e nao por copia de um texto velho.
        """
        from coleta import derivacao_forward as df
        nomes = {g[0] for g in df.GAPS}
        self.assertNotIn("RAW_FORWARD_NAO_EMITE", nomes,
                         "o gap do RAW voltou a ser declarado depois de"
                         " `provas/o_raw_fala.py` o provar fechado")


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


# ⚠️ A PROVA DE VALOR NAO VIVE AQUI — E ELA NAO PODE SALTAR.
#
# Havia aqui uma prova que lia `raw_asset` e comparava a fonte aterrada com o
# canario. Ela SALTAVA em todas as corridas: a `tearDownClass` de
# `tests/test_m2_rota_forward.py` limpa o banco ao sair, entao este modulo
# encontrava a tabela vazia e chamava `skipTest`. Um SKIP verde parece um PASS
# no sumario, e nao e um: SKIP != PASS.
#
# A prova mudou-se para onde as linhas existem — `M2_TravessiaUnica`, no
# ficheiro acima, que corre a travessia e pergunta ao banco ANTES de limpar.
# Aqui fica so a guarda de que ela continua la: um dono, e uma sentinela que
# nao o deixa desaparecer em silencio.


class AProvaDEVALORCONTINUANOSITIOCERTO(unittest.TestCase):
    """Quem apagar a leitura do banco tem de o fazer com esta a gritar."""

    ALVO = os.path.join(RAIZ, "tests", "test_m2_rota_forward.py")

    def _corpo_da_prova_de_valor(self):
        import ast
        arv = ast.parse(io.open(self.ALVO, encoding="utf-8").read())
        for no in ast.walk(arv):
            if not isinstance(no, ast.FunctionDef):
                continue
            if not no.name.startswith("test_"):
                continue
            texto = ast.dump(no)
            if "public.raw_asset" in texto and "CANARIO" in texto:
                return no
        return None

    def test_alguem_le_o_raw_asset_e_compara_com_o_canario(self):
        no = self._corpo_da_prova_de_valor()
        self.assertIsNotNone(
            no, "nenhuma prova le `public.raw_asset` e compara com o CANARIO:"
                " sobrou so guarda de texto, e defeito que da outro VALOR"
                " passa por ela")

    def test_e_ela_nao_salta_quando_a_tabela_esta_vazia(self):
        """SKIP != PASS. Uma prova que se auto-salta nao prova nada."""
        import ast
        no = self._corpo_da_prova_de_valor()
        self.assertIsNotNone(no, "nao ha prova de valor para conferir")
        for dentro in ast.walk(no):
            if isinstance(dentro, ast.Call) and getattr(
                    dentro.func, "attr", None) == "skipTest":
                self.fail("a prova de valor chama skipTest: ela volta a"
                          " saltar em silencio")


if __name__ == "__main__":
    unittest.main()
