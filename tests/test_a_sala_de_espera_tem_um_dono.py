#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""AS GUARDAS DA SALA DE ESPERA — um dono, uma morada, e nenhuma mão solta.

A prova de valor vive em `provas/a_unidade_pousa_na_espera.py`, contra
PostgreSQL e filesystem reais. Aqui ficam as guardas que não precisam de banco
— e a que impede o writer de voltar para o control plane.
"""
import ast
import io
import json
import os
import shutil
import sys
import tempfile
import unittest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for p in (RAIZ, os.path.join(RAIZ, "coleta")):
    if p not in sys.path:
        sys.path.insert(0, p)
import _gavetas                       # noqa: E402,F401
import admissao                       # noqa: E402
import sala_de_espera as espera       # noqa: E402
import telemetria as tel              # noqa: E402

ORQ = os.path.join(RAIZ, "orquestrador", "orquestrador.py")
ROTA = os.path.join(RAIZ, "coleta", "rota_forward_documento.py")
DONO = os.path.join(RAIZ, "admissao", "sala_de_espera.py")
ADR = os.path.join(RAIZ, "docs", "decisoes", "ADR-SALA-DE-ESPERA-V1.md")


def _fonte(caminho):
    return io.open(caminho, encoding="utf-8").read()


class Bancada(unittest.TestCase):
    """Uma sala descartável por caso. A morada de produção não se toca."""

    def setUp(self):
        self.sala = tempfile.mkdtemp(prefix="sala-")
        self.addCleanup(shutil.rmtree, self.sala, True)
        self._morada = espera.MORADA
        espera.MORADA = self.sala
        self.addCleanup(setattr, espera, "MORADA", self._morada)

    def unidade(self, **extra):
        return dict({"ESTADO": "PRONTO_PARA_INTELIGENCIA", "ITEM_ID": "i-1",
                     "UNIVERSO": "T3", "TEXTO": "t", "SOURCE_ID": "IT-T3-002",
                     "SOURCE_LOCATION": "NAO SEI", "FACT_LOCATION": "NAO SEI",
                     "FACT_TIME": "NAO SEI", "CAPTURED_AT": "NAO SEI",
                     "CORRIDA": "R1", "ADMITIDO_POR": "regra v1"}, **extra)


class UMDonoEUmaMorada(unittest.TestCase):
    """⚠️ COL-LAW-012: O ORQUESTRADOR CONTROLA, NÃO TRANSPORTA DADO.

    A escrita vivia dentro do orquestrador. Enquanto a única escrita estivesse
    no control plane, a rota forward não tinha como pousar a unidade sem
    escrever uma SEGUNDA — e duas escritas da mesma espera são duas verdades à
    espera de divergir.
    """

    def _escreve_a_morada(self, caminho):
        """Quem monta o caminho da sala E escreve, lido por AST."""
        arv = ast.parse(_fonte(caminho))
        for no in ast.walk(arv):
            if not isinstance(no, ast.Call):
                continue
            alvo = getattr(no.func, "attr", None)
            if alvo in ("write_text", "mkstemp") or (
                    alvo == "open" and "PRONTO-PARA-INTELIGENCIA" in _fonte(caminho)):
                return True
        return False

    def test_o_orquestrador_ja_nao_escreve_a_sala(self):
        s = _fonte(ORQ)
        self.assertNotIn("PRONTO-PARA-INTELIGENCIA", s,
                         "o caminho da sala voltou para o control plane")
        self.assertFalse(self._escreve_a_morada(ORQ),
                         "o orquestrador voltou a escrever a sala")

    def test_e_a_rota_forward_tambem_nao(self):
        s = _fonte(ROTA)
        self.assertNotIn("PRONTO-PARA-INTELIGENCIA", s,
                         "nasceu um segundo writer na rota forward")
        self.assertNotIn(".write_text(", s)

    def test_os_dois_chamam_o_MESMO_dono(self):
        for caminho in (ORQ, ROTA):
            with self.subTest(ficheiro=os.path.basename(caminho)):
                self.assertIn("sala_de_espera", _fonte(caminho))
                self.assertIn("espera.pousar(", _fonte(caminho))

    def test_a_morada_tem_UM_dono_em_todo_o_runtime(self):
        donos = []
        for pasta in ("admissao", "coleta", "guarda", "orquestrador",
                      "medidas", "regras", "motor"):
            base = os.path.join(RAIZ, pasta)
            if not os.path.isdir(base):
                continue
            for raiz_, _d, fs in os.walk(base):
                if "__pycache__" in raiz_:
                    continue
                for f in sorted(fs):
                    if not f.endswith(".py"):
                        continue
                    if "PRONTO-PARA-INTELIGENCIA" in _fonte(
                            os.path.join(raiz_, f)):
                        donos.append(os.path.relpath(
                            os.path.join(raiz_, f), RAIZ))
        self.assertEqual(["admissao/sala_de_espera.py"], donos,
                         "a morada e nomeada em mais do que um sitio: %s"
                         % donos)


class OContratoNaoMudou(unittest.TestCase):
    """READY continua os 11 campos, e nem um a mais para facilitar storage."""

    CAMPOS = ("ESTADO", "ITEM_ID", "UNIVERSO", "TEXTO", "SOURCE_ID",
              "SOURCE_LOCATION", "FACT_LOCATION", "FACT_TIME",
              "CAPTURED_AT", "CORRIDA", "ADMITIDO_POR")

    def test_o_dono_do_contrato_devolve_os_onze(self):
        item = {"id": "c-1", "texto": "Ensaio de campo com DOI",
                "source_id": "IT-T7-001", "fact_time": "2026-05-02"}
        d = admissao.decidir(item, "T7", corrida="guarda")
        self.assertEqual(self.CAMPOS,
                         tuple(admissao.pronto_para_inteligencia(item, d)))

    def test_o_dono_da_sala_nao_acrescenta_campos_tecnicos(self):
        """O payload entregue à Intelligence é o da lei, e mais nada."""
        s = _fonte(DONO)
        arv = ast.parse(s)
        for no in ast.walk(arv):
            if isinstance(no, ast.Dict):
                chaves = {k.value for k in no.keys
                          if isinstance(k, ast.Constant)
                          and isinstance(k.value, str)}
                self.assertNotIn("ESTADO_DE_STORAGE", chaves)
        self.assertIn('"ITENS": list(unidades)', s,
                      "a sala passou a mexer no conteudo das unidades")


class OQueUmFicheiroExige(Bancada):
    """Atomicidade, idempotência e conflito — provados no filesystem real."""

    def test_pousar_escreve_e_devolve_PASSED(self):
        r = espera.pousar("R1", [self.unidade()])
        self.assertEqual(tel.DESTINOS_DO_ITEM[0], r["ESTADO"])
        self.assertTrue(os.path.isfile(espera.caminho_da_corrida("R1")))

    def test_o_mesmo_conteudo_outra_vez_diz_REUSED_e_nao_duplica(self):
        u = [self.unidade()]
        espera.pousar("R1", u)
        antes = _fonte(espera.caminho_da_corrida("R1"))
        r = espera.pousar("R1", u)
        self.assertEqual(tel.DESTINOS_DO_ITEM[5], r["ESTADO"])
        self.assertEqual(antes, _fonte(espera.caminho_da_corrida("R1")))

    def test_outra_historia_na_mesma_corrida_e_conflito_e_nao_overwrite(self):
        espera.pousar("R1", [self.unidade()])
        antes = _fonte(espera.caminho_da_corrida("R1"))
        with self.assertRaises(espera.ConflitoDeCorrida):
            espera.pousar("R1", [self.unidade(TEXTO="outra")])
        self.assertEqual(antes, _fonte(espera.caminho_da_corrida("R1")),
                         "o ficheiro anterior foi mexido")

    def test_zero_unidades_nao_cria_ficheiro(self):
        """Um ficheiro com `ITENS: []` diria que a corrida chegou. Nao chegou."""
        r = espera.pousar("R1", [])
        self.assertIsNone(r["ESTADO"])
        self.assertFalse(os.path.isfile(espera.caminho_da_corrida("R1")))

    def test_o_ficheiro_publicado_e_sempre_JSON_inteiro(self):
        espera.pousar("R1", [self.unidade()])
        d = json.loads(_fonte(espera.caminho_da_corrida("R1")))
        self.assertEqual("R1", d["RUN_ID"])
        self.assertEqual(1, len(d["ITENS"]))

    def test_nao_ficam_temporarios_na_sala(self):
        espera.pousar("R1", [self.unidade()])
        self.assertEqual([], [f for f in os.listdir(self.sala)
                              if f.startswith(".espera-")])

    def test_a_corrida_nao_pode_carregar_caminho(self):
        """`../` no RUN_ID escreveria fora da morada."""
        for mau in ("../fora", "a/b", ".oculto", "", "   "):
            with self.subTest(run_id=mau):
                with self.assertRaises(ValueError):
                    espera.caminho_da_corrida(mau)


class OVocabularioEOQueJaExistia(unittest.TestCase):
    """Não se inventou estado novo para dizer «pousou» e «já lá estava»."""

    def test_os_estados_vem_de_telemetria(self):
        self.assertEqual(tel.DESTINOS_DO_ITEM[0], espera.POUSOU)
        self.assertEqual(tel.DESTINOS_DO_ITEM[5], espera.JA_ESTAVA)

    def test_o_nome_do_conflito_vem_do_dono_dele(self):
        from preservar_coleta import RUN_ID_CONFLICT
        self.assertEqual(RUN_ID_CONFLICT, espera.RUN_ID_CONFLICT)

    def test_a_etapa_READY_ja_estava_no_vocabulario(self):
        self.assertIn("READY", tel.ETAPAS_DA_COLETA)


class ADecisaoEstaVersionada(unittest.TestCase):
    """Uma decisão de arquitetura que não está escrita volta como discussão."""

    def test_o_ADR_existe_e_declara_o_backend(self):
        s = _fonte(ADR)
        self.assertIn("WAITING_ROOM_V1_BACKEND        FILESYSTEM", s)
        self.assertIn("BACKEND_CHANGE_ALLOWED_LATER   YES", s)

    def test_e_nao_declara_o_PostgreSQL_aposentado(self):
        s = _fonte(ADR)
        self.assertIn("NOT_REQUIRED_NOW", s)


if __name__ == "__main__":
    unittest.main()
