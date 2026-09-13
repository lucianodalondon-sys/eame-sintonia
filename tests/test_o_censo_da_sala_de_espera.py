#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""AS GUARDAS DO CENSO — um censo que devolve sempre zero não é um censo.

A fotografia vive em `provas/o_censo_da_sala_de_espera.py`, e ela mediu uma
sala VAZIA. Um zero medido e um zero por avaria são indistinguíveis no
relatório — e é por isso que estas guardas existem.

    ZERO MEDIDO E ZERO POR AVARIA SÃO O MESMO NÚMERO.
    SÓ O INSTRUMENTO OS SEPARA.

Cada caso enche uma sala DESCARTÁVEL e exige que o contador se mexa. A morada
de produção nunca é tocada: `espera.MORADA` é redirigida no `setUp` e reposta
no fim, exactamente como as outras provas desta casa já fazem.
"""
import io
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for p in (RAIZ, os.path.join(RAIZ, "provas")):
    if p not in sys.path:
        sys.path.insert(0, p)
import _gavetas                                # noqa: E402,F401
import sala_de_espera as espera                # noqa: E402
import o_censo_da_sala_de_espera as censo      # noqa: E402

CENSO = os.path.join(RAIZ, "provas", "o_censo_da_sala_de_espera.py")


class Bancada(unittest.TestCase):
    """Uma sala descartável por caso. A morada de produção não se toca."""

    def setUp(self):
        self.sala = tempfile.mkdtemp(prefix="censo-")
        self.addCleanup(shutil.rmtree, self.sala, True)
        self._morada = espera.MORADA
        espera.MORADA = self.sala
        self.addCleanup(setattr, espera, "MORADA", self._morada)
        self.campos = censo._campos_do_contrato()

    def unidade(self, **troca):
        u = {"ESTADO": "PRONTO_PARA_INTELIGENCIA", "ITEM_ID": "i1",
             "UNIVERSO": "T7", "TEXTO": "texto", "SOURCE_ID": "IT-T7-001",
             "SOURCE_LOCATION": "IT", "FACT_LOCATION": "IT",
             "FACT_TIME": "2026-05-02", "CAPTURED_AT": "2026-05-02T10:00:00Z",
             "CORRIDA": "RUN-A", "ADMITIDO_POR": "pertence ao universo v1"}
        u.update(troca)
        return u

    def pousar(self, run_id, itens):
        caminho = os.path.join(self.sala, "%s.json" % run_id)
        with io.open(caminho, "w", encoding="utf-8") as fh:
            json.dump({"RUN_ID": run_id, "ITENS": itens}, fh)

    def medir(self):
        sala, itens = censo.a_sala(self.campos)
        return sala, itens, censo.por_item(itens)


class OInstrumentoConta(Bancada):

    def test_sala_vazia_da_zero_e_a_morada_nao_e_criada(self):
        shutil.rmtree(self.sala, True)
        sala, itens, _ = self.medir()
        self.assertFalse(sala["MORADA_EXISTE"])
        self.assertEqual(0, sala["TOTAL_WAITING_ROOM_RECORDS"])
        self.assertEqual(0, sala["TOTAL_UNIQUE_READY_ITEMS"])
        self.assertFalse(os.path.isdir(self.sala),
                         "medir NAO pode criar a morada que foi medir")

    def test_registo_nao_e_item_e_os_dois_sao_contados_a_parte(self):
        """⚠️ UM FICHEIRO DE CORRIDA COM 3 UNIDADES É 1 REGISTO E 3 ITENS."""
        self.pousar("RUN-A", [self.unidade(), self.unidade(ITEM_ID="i2"),
                              self.unidade(ITEM_ID="i3")])
        sala, _itens, _p = self.medir()
        self.assertEqual(1, sala["TOTAL_WAITING_ROOM_RECORDS"])
        self.assertEqual(3, sala["TOTAL_UNIQUE_READY_ITEMS"])

    def test_ficheiro_ilegivel_nao_vira_zero_silencioso(self):
        with io.open(os.path.join(self.sala, "RUN-X.json"), "w",
                     encoding="utf-8") as fh:
            fh.write("{ isto nao e json")
        sala, _i, _p = self.medir()
        self.assertEqual(1, len(sala["FICHEIROS_ILEGIVEIS"]))
        self.assertEqual(0, sala["TOTAL_WAITING_ROOM_RECORDS"],
                         "ilegivel NAO conta como registo bom")


class AAusenciaNaoEPromovida(Bancada):

    def test_sentinela_conta_como_UNKNOWN_e_nunca_como_valor(self):
        """⚠️ `NAO SEI` NÃO É UM SOURCE_ID. É a casa a dizer que não sabe."""
        self.pousar("RUN-A", [self.unidade(SOURCE_ID="NAO SEI"),
                              self.unidade(ITEM_ID="i2",
                                           FACT_TIME="NÃO SEI"),
                              self.unidade(ITEM_ID="i3",
                                           FACT_LOCATION="UNKNOWN")])
        _s, _i, p = self.medir()
        self.assertEqual(1, p["IDENTIDADE"]["SOURCE_ID_UNKNOWN"])
        self.assertEqual(1, p["TEMPO"]["FACT_TIME_UNKNOWN"])
        self.assertEqual(1, p["GEOGRAFIA"]["FACT_LOCATION_UNKNOWN"])

    def test_source_location_nao_escorrega_para_fact_location(self):
        self.pousar("RUN-A", [self.unidade(SOURCE_LOCATION="IT",
                                           FACT_LOCATION="NAO SEI")])
        _s, _i, p = self.medir()
        self.assertEqual(1, p["GEOGRAFIA"]["SOURCE_LOCATION_KNOWN"])
        self.assertEqual(0, p["GEOGRAFIA"]["FACT_LOCATION_KNOWN"],
                         "saber a fonte NAO e saber o lugar do facto")


class ALinhagemNaoSeArredonda(Bancada):

    def test_corrida_diferente_da_do_ficheiro_quebra_a_ligacao(self):
        """⚠️ UM ITEM QUE NOMEIA OUTRA CORRIDA NÃO TEM LINHAGEM: TEM CONTRADIÇÃO."""
        self.pousar("RUN-A", [self.unidade(CORRIDA="OUTRA")])
        _s, _i, p = self.medir()
        self.assertEqual(1, p["QUEBRA_POR_ESTAGIO"]["MISSING_RUN_LINK"])
        self.assertEqual(0, p["LINHAGEM"]["LINEAGE_PARTIAL"])

    def test_LINEAGE_FULL_nunca_sai_de_um_item_sozinho(self):
        """RAW e STORAGE não viajam no contrato — e isso não vira PASS."""
        self.pousar("RUN-A", [self.unidade()])
        _s, _i, p = self.medir()
        self.assertEqual(0, p["LINHAGEM"]["LINEAGE_FULL"])
        self.assertEqual(1, p["LINHAGEM"]["LINEAGE_PARTIAL"])
        self.assertEqual(1, p["QUEBRA_POR_ESTAGIO"]["MISSING_RAW_LINK"])
        self.assertEqual(1, p["QUEBRA_POR_ESTAGIO"]["MISSING_STORAGE_LINK"])


class AOrigemSaiDaFormaNaoDaData(Bancada):

    def test_forma_de_hoje_com_ligacoes_e_canonico_atual(self):
        self.pousar("RUN-A", [self.unidade()])
        _s, _i, p = self.medir()
        self.assertEqual(1, p["ORIGEM"]["CURRENT_CANONICAL_PROVEN"])
        self.assertEqual(0, p["ORIGEM"]["LEGACY_PROVEN"])

    def test_forma_de_outra_era_com_ligacoes_e_legado(self):
        """⚠️ O WRITER ANTIGO DEIXA MARCA NA FORMA — nunca no mtime."""
        antigo = self.unidade(ITEM_ID="L1")
        antigo["CAMPO_DE_OUTRA_ERA"] = "x"
        self.pousar("RUN-A", [antigo])
        _s, _i, p = self.medir()
        self.assertEqual(1, p["ORIGEM"]["LEGACY_PROVEN"])
        self.assertEqual(0, p["ORIGEM"]["CURRENT_CANONICAL_PROVEN"])

    def test_ficheiro_novo_com_item_sem_ligacoes_nao_vira_atual(self):
        self.pousar("RUN-A", [{"ESTADO": "PRONTO_PARA_INTELIGENCIA",
                               "ITEM_ID": "i9"}])
        _s, _i, p = self.medir()
        self.assertEqual(1, p["ORIGEM"]["UNKNOWN_ORIGIN"])
        self.assertEqual(1, p["CONTRATO"]["READY_CONTRACT_INVALID"])


class ADuplicacaoNaoEUmaSoPergunta(Bancada):

    def test_READY_ID_duplicado_e_visto_pelo_par_CORRIDA_ITEM_ID(self):
        self.pousar("RUN-A", [self.unidade(), self.unidade()])
        _s, itens, _p = self.medir()
        d = censo.as_duplicacoes(itens)
        self.assertEqual(1, d["READY_ID_DUPLICATES"])

    def test_observacao_e_semantica_ficam_NAO_SEI_e_nao_zero(self):
        """⚠️ NÃO MEDIDO ≠ ZERO. Um zero aqui seria uma prova que não houve."""
        self.pousar("RUN-A", [self.unidade()])
        _s, itens, _p = self.medir()
        d = censo.as_duplicacoes(itens)
        self.assertEqual("NO", d["OBSERVATION_ID_MEDIDO"])
        self.assertEqual("NAO SEI", d["POSSIBLE_SEMANTIC_DUPLICATES"])


class OCensoEReprodutivelESoLe(unittest.TestCase):

    def test_duas_corridas_dao_o_MESMO_relatorio_byte_a_byte(self):
        saida = os.path.join(RAIZ, censo.SAIDA)
        um = subprocess.run([sys.executable, CENSO], cwd=RAIZ,
                            capture_output=True)
        self.assertEqual(0, um.returncode, um.stderr.decode()[-800:])
        with io.open(saida, encoding="utf-8") as fh:
            primeiro = fh.read()
        dois = subprocess.run([sys.executable, CENSO], cwd=RAIZ,
                              capture_output=True)
        self.assertEqual(0, dois.returncode, dois.stderr.decode()[-800:])
        with io.open(saida, encoding="utf-8") as fh:
            segundo = fh.read()
        self.assertEqual(primeiro, segundo,
                         "o relatorio NAO pode mudar entre duas corridas: "
                         "nenhum timestamp de geracao entra nele")

    def test_o_censo_nao_escreve_fora_do_proprio_relatorio(self):
        """Correr o censo não pode sujar a árvore — nem criar a sala medida."""
        antes = subprocess.run(["git", "status", "--porcelain"], cwd=RAIZ,
                               capture_output=True).stdout.decode()
        subprocess.run([sys.executable, CENSO], cwd=RAIZ, capture_output=True)
        depois = subprocess.run(["git", "status", "--porcelain"], cwd=RAIZ,
                                capture_output=True).stdout.decode()
        mexidos = {l[3:] for l in depois.splitlines()} - \
                  {l[3:] for l in antes.splitlines()}
        self.assertEqual(set(), mexidos - {censo.SAIDA},
                         "o censo so pode escrever o proprio relatorio")


if __name__ == "__main__":
    unittest.main(verbosity=2)
