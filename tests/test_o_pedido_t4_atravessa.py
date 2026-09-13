#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""AS VINTE MANEIRAS DE FABRICAR UM «T4 ATRAVESSA».

O brief nomeou-as. Cada uma tem aqui uma guarda, e a guarda mede a
PROPRIEDADE — nunca o estado de hoje.

    UMA GUARDA PRESA AO ESTADO DE HOJE REPROVA O PROGRESSO DE AMANHA.
"""
import ast
import importlib.util
import io
import json
import os
import sys
import unittest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if RAIZ not in sys.path:
    sys.path.insert(0, RAIZ)
import _gavetas  # noqa: E402,F401

import admissao as adm  # noqa: E402
import retorno_da_coleta as rdc  # noqa: E402
from receitas import EXECUTORES  # noqa: E402

PROVA = os.path.join(RAIZ, "provas", "o_pedido_t4_atravessa.py")
EXEC_T4 = os.path.join(RAIZ, "coleta", "eu_regulatorio_executor.py")
OBSERVADO = os.path.join(RAIZ, "system-map", "data",
                         "pedido-t4.observado.json")

_spec = importlib.util.spec_from_file_location("prova_t4", PROVA)
P = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(P)


def _fonte(caminho):
    with io.open(caminho, encoding="utf-8") as f:
        return f.read()


def _codigo_sem_prosa(caminho):
    """O ficheiro sem comentarios e sem docstrings — so o que EXECUTA.

    ⚠️ ISTO NASCEU DE UMA GUARDA QUE MORDEU A PROPRIA REGRA.
    `test_nenhum_canal_nem_conteudo_de_plataforma_e_criado` procurava
    `channel_id` no texto do executor — e o executor DIZ, na docstring dele,
    que nao inventa `channel_id`. A frase que explica a regra reprovava a
    regra.

        PROCURAR O TEXTO DA REGRA NAO E MEDIR A REGRA.

    E a terceira vez nesta linha de missoes (§95, §99.5). A correcao ja tem
    nome: AST em vez de texto. `ast.unparse` deita fora os comentarios
    sozinho; as docstrings tiram-se a mao, porque para o interpretador elas
    sao expressoes como as outras.
    """
    arvore = ast.parse(_fonte(caminho))
    for no in ast.walk(arvore):
        corpo = getattr(no, "body", None)
        if not isinstance(corpo, list) or not corpo:
            continue
        if not isinstance(no, (ast.Module, ast.ClassDef, ast.FunctionDef,
                               ast.AsyncFunctionDef)):
            continue
        primeiro = corpo[0]
        if (isinstance(primeiro, ast.Expr)
                and isinstance(primeiro.value, ast.Constant)
                and isinstance(primeiro.value.value, str)):
            corpo.pop(0)
            if not corpo:
                corpo.append(ast.Pass())
    ast.fix_missing_locations(arvore)
    return ast.unparse(arvore)


def _chamadas(caminho):
    nomes = set()
    for no in ast.walk(ast.parse(_fonte(caminho))):
        if isinstance(no, ast.Call):
            f = no.func
            if isinstance(f, ast.Attribute):
                nomes.add(f.attr)
            elif isinstance(f, ast.Name):
                nomes.add(f.id)
    return nomes


def _observado():
    if not os.path.isfile(OBSERVADO):
        return None
    with io.open(OBSERVADO, encoding="utf-8") as f:
        return json.load(f)


# ══════════════════════════════════════════════════════════════════════════
# 1 · A PROVA COMECA NO PEDIDO, E NAO NO MEIO
# ══════════════════════════════════════════════════════════════════════════
class AProvaNaoComecaPeloMeio(unittest.TestCase):

    def test_aperta_o_botao_canonico(self):
        self.assertIn("correr", _chamadas(PROVA),
                      "a prova nao chama orquestrador.correr()")

    def test_e_NAO_chama_o_downstream_a_mao(self):
        """ATAQUE 1 · comecar na Admission. ATAQUE 11 · Admission de outra
        historia. Uma prova que chama a porta a mao mede a porta, e nao a
        estrada que devia leva-la ate la."""
        chamadas = _chamadas(PROVA)
        for proibida in ("admitir", "pronto_para_inteligencia", "pousar",
                         "decidir", "preservar_documento",
                         "preservar_derivado", "derivar_um"):
            self.assertNotIn(proibida, chamadas,
                             "a prova montou a estrada a mao: %s" % proibida)

    def test_e_nao_abre_a_corrida_nem_o_bruto_a_mao(self):
        """ATAQUE 8 · RAW nao preservado, mascarado por uma linha escrita a
        mao."""
        s = _fonte(PROVA).lower()
        self.assertNotIn("insert into public.collection_run", s)
        self.assertNotIn("insert into public.raw_asset", s)
        self.assertNotIn("insert into public.documento_estruturado", s)


# ══════════════════════════════════════════════════════════════════════════
# 2 · FIXTURE NAO E INTERNET  ·  TLS NAO SE DESLIGA
# ══════════════════════════════════════════════════════════════════════════
class SoAInternetProvaAquisicao(unittest.TestCase):

    def test_a_prova_nao_traz_bytes_no_bolso(self):
        """ATAQUE 3 · fixture conta como internet real.

        Um PDF versionado ao lado da prova provaria o parser e chamaria a
        isso aquisicao.

            FIXTURE PROVA PARSER. SO A INTERNET PROVA AQUISICAO.
        """
        codigo = _codigo_sem_prosa(PROVA)
        for pista in (".pdf", "data/samples", "fixture"):
            self.assertNotIn(pista, codigo,
                             "a prova passou a carregar material proprio: %s"
                             % pista)

    def test_o_executor_nao_desliga_a_verificacao_de_TLS(self):
        """ATAQUE 4 · TLS desativado.

        ⚠️ ISTO E UMA GUARDA DE TEXTO DE PROPOSITO, e a excepcao esta medida:
        as formas de desligar TLS em Python sao POUCAS e TEM NOME
        (`_create_unverified_context`, `verify=False`, `CERT_NONE`). Nao e
        uma regra de prosa a ser confundida com o exemplo dela — sao chamadas
        de biblioteca, e cada uma delas desliga mesmo.
        """
        # ⚠️ O PROPRIO FICHEIRO EXPLICA QUE NAO DESLIGA TLS, e por isso a
        # guarda NAO pode ler o texto dele: leria a explicacao e reprovaria.
        # Olha para CHAMADAS e para nos da arvore.
        s = _codigo_sem_prosa(EXEC_T4)
        chamadas = _chamadas(EXEC_T4)
        for proibida in ("_create_unverified_context",
                         "_create_default_https_context"):
            self.assertNotIn(proibida, chamadas,
                             "o executor passou a desligar a verificacao TLS")
        arvore = ast.parse(s)
        for no in ast.walk(arvore):
            if isinstance(no, ast.keyword) and no.arg == "verify":
                v = getattr(no.value, "value", None)
                self.assertNotEqual(
                    False, v, "o executor passou a usar verify=False")
        for no in ast.walk(arvore):
            if isinstance(no, ast.Attribute) and no.attr == "CERT_NONE":
                self.fail("o executor passou a aceitar certificado nenhum")


# ══════════════════════════════════════════════════════════════════════════
# 3 · MANIFEST NAO E COLHEITA
# ══════════════════════════════════════════════════════════════════════════
class SuporteNaoAtravessa(unittest.TestCase):

    def test_o_executor_de_T4_que_corre_declara_ENVELOPE(self):
        """ATAQUE 2 · executor devolve manifest e o teste chama a isso coleta.

        ⚠️ E A GUARDA E SOBRE O PRIMEIRO, e nao sobre «algum». O orquestrador
        corre `plano.executores[0]`: um executor de colheita no fim da lista
        nao colhe nada.
        """
        primeiro = (EXECUTORES.get("T4") or [{}])[0]
        retorno = primeiro.get("retorno") or {}
        self.assertIn("ENVELOPE", retorno,
                      "o primeiro executor de T4 voltou a declarar suporte: "
                      "%s" % list(retorno))

    def test_o_envelope_que_ele_escreve_cumpre_o_contrato(self):
        """Um envelope que quebra o contrato nao entrega nada — e e melhor
        descobri-lo aqui do que numa corrida."""
        caminho = os.path.join(
            RAIZ, (EXECUTORES["T4"][0]["retorno"]["ENVELOPE"]))
        if not os.path.isfile(caminho):
            self.skipTest("o executor ainda nao correu neste HEAD")
        with io.open(caminho, encoding="utf-8") as f:
            env = json.load(f)
        self.assertEqual([], rdc.conferir(env, RAIZ),
                         "o envelope de T4 quebrou o contrato")

    def test_so_COLHEITA_atravessa_e_o_executor_declara_COLHEITA(self):
        self.assertIn("rdc.COLHEITA", _codigo_sem_prosa(EXEC_T4),
                      "o executor deixou de declarar a especie COLHEITA")


# ══════════════════════════════════════════════════════════════════════════
# 4 · IDENTIDADE — o que se prova e o que se fabrica
# ══════════════════════════════════════════════════════════════════════════
class AIdentidadeNaoSeFabrica(unittest.TestCase):

    def test_o_SOURCE_ID_nao_sai_da_URL_nem_do_caminho(self):
        """ATAQUES 5 e 7 · SOURCE_ID fabricado · URL vira identidade."""
        arvore = ast.parse(_fonte(EXEC_T4))
        for no in ast.walk(arvore):
            if not isinstance(no, ast.Assign):
                continue
            alvos = [a.id for a in no.targets if isinstance(a, ast.Name)]
            if "SOURCE_ID" in alvos:
                self.assertIsInstance(
                    no.value, ast.Constant,
                    "SOURCE_ID passou a ser CALCULADO. Ele e o codigo que o "
                    "atlas declara, e nao um valor derivado da rota")

    def test_o_DOCUMENT_ID_e_o_que_a_fonte_declara_como_identidade(self):
        """ATAQUE 6 · DOCUMENT_ID fabricado.

        ⚠️ E ESTA GUARDA NAO DIZ «NUNCA ESCREVER DOCUMENT_ID».
        Dizer isso congelaria a casa no dia em que ela so tinha fontes que
        nao provam identidade. O que ela guarda e a LIGACAO: o valor escrito
        tem de ser o CELEX que veio no pedido, e nao o sha, o caminho ou a URL.
        """
        codigo = _codigo_sem_prosa(EXEC_T4)
        self.assertIn("'DOCUMENT_ID': celex", codigo,
                      "o DOCUMENT_ID deixou de ser o identificador da fonte")
        for atalho in ("sha256", "hexdigest", "SOURCE_URL", "basename"):
            self.assertNotIn("'DOCUMENT_ID': %s" % atalho, codigo,
                             "o DOCUMENT_ID passou a vir de %s" % atalho)

    def test_a_observacao_medida_traz_identidade_PROVADA(self):
        d = _observado()
        if d is None:
            self.skipTest("a prova de T4 ainda nao correu neste HEAD")
        raw = (d.get("ESTRADA") or {}).get("RAW") or {}
        self.assertTrue(raw.get("OBSERVED"), "RAW nao foi observado")
        self.assertIn(d.get("CELEX") or "", str(d))

    def test_nenhum_canal_nem_conteudo_de_plataforma_e_criado(self):
        """A rota de T4 e documental. Um `canal_id` aqui seria identidade
        social inventada para um ato do Jornal Oficial."""
        codigo = _codigo_sem_prosa(EXEC_T4).lower()
        for proibido in ("canal_id", "channel_id", "content_id"):
            self.assertNotIn(proibido, codigo,
                             "a rota documental passou a CRIAR %s — e nao "
                             "apenas a falar dele" % proibido)


# ══════════════════════════════════════════════════════════════════════════
# 5 · A REGRA NAO MUDA PARA O EXAME PASSAR
# ══════════════════════════════════════════════════════════════════════════
class ARegraDeT4NaoFoiTocada(unittest.TestCase):

    # ⚠️ O VOCABULARIO DE T4 COMO ELE ESTAVA ANTES DESTA MISSAO.
    # Nao e um retrato do presente: e o conjunto que a missao encontrou. Se
    # alguem ACRESCENTAR um termo para um caso passar, a guarda apanha-o; se
    # alguem o reescrever por outra razao, tambem — e deve mesmo apanhar, para
    # que a mudanca seja deliberada e nao um efeito secundario.
    ANTES_DESTA_MISSAO = {
        "registro", "ministero", "decreto", "autorizacao", "rotulo", "bula",
        "autorizzazione", "etichetta", "foglietto", "registrazione",
        "gazzetta"}

    def test_o_vocabulario_de_T4_e_o_mesmo_de_antes(self):
        """ATAQUE 12 · regra de T4 alterada so para produzir SIM."""
        self.assertEqual(
            self.ANTES_DESTA_MISSAO,
            set(adm.PERGUNTAS_DO_UNIVERSO.get("T4") or []),
            "o vocabulario de T4 mudou. Se foi de proposito, esta guarda "
            "muda com a decisao escrita ao lado — nunca em silencio")

    def test_a_porta_continua_a_ter_cinco_respostas_distintas(self):
        """ATAQUES 14, 15 · NAO e NAO_SEI a produzirem READY."""
        for a_, b_ in ((adm.SIM, adm.NAO), (adm.NAO, adm.NAO_SEI),
                       (adm.NAO_SEI, adm.NAO_SE_APLICA),
                       (adm.NAO_SE_APLICA, adm.ERRO)):
            self.assertNotEqual(a_, b_)

    def test_so_o_SIM_produz_READY(self):
        d = adm.Decisao(item="x", universo="T4", resultado=adm.NAO,
                        regra="r", motivo="m", evidencia={}, corrida="c")
        with self.assertRaises(ValueError):
            adm.pronto_para_inteligencia({"texto": "t"}, d)


# ══════════════════════════════════════════════════════════════════════════
# 6 · A MESMA HISTORIA, E NAO DUAS SOMADAS
# ══════════════════════════════════════════════════════════════════════════
class DuasMetadesNaoSaoUmaEstrada(unittest.TestCase):

    def test_o_limiar_da_mesma_historia_reprova_duas_corridas(self):
        """ATAQUE 19 · duas rotas somadas como uma.

        ⚠️ `== 1` escrito a direito sobrevive a mutacao num banco com uma
        corrida so. Isolado, ele e conferido pelos DOIS lados.
        """
        self.assertTrue(P.uma_corrida_so(1))
        self.assertFalse(P.uma_corrida_so(2))
        self.assertFalse(P.uma_corrida_so(0))

    def test_o_veredicto_exige_as_ONZE_etapas(self):
        d = _observado()
        if d is None:
            self.skipTest("a prova de T4 ainda nao correu neste HEAD")
        estrada = d.get("ESTRADA") or {}
        observadas = [e for e in P.ESTRADA
                      if (estrada.get(e) or {}).get("OBSERVED")]
        if d.get("CANONICAL_E2E") == "PASS":
            self.assertEqual(len(P.ESTRADA), len(observadas),
                             "o veredicto deu PASS sem as onze etapas")
        else:
            self.assertLess(len(observadas), len(P.ESTRADA))

    def test_o_criterio_do_canario_esta_escrito_na_prova(self):
        """ATAQUE 20 e o irmao dele: escolher o caso depois de ver o
        resultado. O criterio tem de existir no ficheiro, e nao na memoria de
        quem o correu."""
        self.assertTrue(P.PORQUE_ELE_E_T4.strip())
        self.assertIn("real_example", P.PORQUE_ELE_E_T4,
                      "o criterio deixou de dizer de onde veio o caso")


# ══════════════════════════════════════════════════════════════════════════
# 7 · O QUE ESTA EM GIT NAO E O QUE ESTA EM LIVE
# ══════════════════════════════════════════════════════════════════════════
class GitNaoELive(unittest.TestCase):

    def test_a_prova_corre_contra_descartavel_e_diz_isso(self):
        """ATAQUE 20 · migration em Git chamada de LIVE."""
        s = _fonte(PROVA)
        self.assertIn("BANCO_DESCARTAVEL_URL", s)
        self.assertIn("descartavel", s.lower())

    def test_sem_ambiente_a_prova_NAO_diz_PASS(self):
        """`SKIP != PASS` e `NOT_MEASURED != PASS`."""
        s = _fonte(PROVA)
        self.assertIn("PEDIDO_T4_ATRAVESSA=NOT_MEASURED", s)


if __name__ == "__main__":
    unittest.main()
