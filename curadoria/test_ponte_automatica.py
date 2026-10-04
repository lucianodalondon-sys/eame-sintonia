#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""O OBSERVADOR DA PONTE, ATACADO — cada lei com o teste que a tenta partir.

    RT-P1  meia-gravacao passa por livro inteiro   -> recusa, nao devolve meio
    RT-P2  livro igual volta a atravessar          -> NO_OP, zero escritas
    RT-P3  tick sem novidade escreve no diario     -> diario nao cresce
    RT-P4  falha a ler derruba o ciclo             -> conta, nao levanta
    RT-P5  falha fica engolida                     -> ULTIMO_ERRO e SAUDE visiveis
    RT-P6  o observador escreve na lane do bot     -> nunca; so le
    RT-P7  o corte logico nao e o que foi lido     -> sha do livro lido

Tudo em pasta descartavel. A lane REAL do bot nunca e tocada, e o livro
canonico real tambem nao.
"""
from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
import lifecycle as LC              # noqa: E402
import ponte_automatica as PA       # noqa: E402
import ready_split as RS            # noqa: E402
import reconciliar_livros as R      # noqa: E402


def _livro(*transicoes):
    return {"DATASET": "LIFECYCLE-LEDGER-V1", "CONTRATO": LC.CONTRATO,
            "LEI": "t", "TRANSICOES": list(transicoes)}


def _linha(sid, para, quando, de=None, ref=None):
    return {"SOURCE_ID": sid, "PREVIOUS_STATE": de, "NEW_STATE": para,
            "REASON": "prova", "EVIDENCE_REF": ref, "OBSERVED_AT": quando,
            "OWNER": LC.OWNER_CURATOR, "VERSION": LC.CONTRATO}


class ABancada(unittest.TestCase):
    """Uma lane do bot de mentira, e o estado do observador a parte."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        d = Path(self.tmp.name)
        self.lane = d / "lane-do-bot"
        (self.lane / "curadoria").mkdir(parents=True)
        self.livro_do_bot = self.lane / "curadoria" / "LIFECYCLE-LEDGER-V1.json"
        self._escrever(_livro(_linha("IT-T9-900", LC.CANARY_PENDING, "2026-09-22T10:00:00+00:00")))

        self._antes = (PA.ESTADO, PA.DIARIO, LC.LIVRO, R.SAIDA, R.EVIDENCIA_A,
                       RS.EVIDENCIA, RS.CONTRATOS)
        self._contratos_a = R.CONTRATOS_A
        PA.ESTADO = d / "STATE.json"
        PA.DIARIO = d / "LOG.ndjson"
        LC.LIVRO = d / "LEDGER.json"
        R.SAIDA = d / "RECONCILIACAO.json"
        R.EVIDENCIA_A = RS.EVIDENCIA = d / "EVIDENCE.json"
        RS.CONTRATOS = d / "CONTRATOS.json"
        R.EVIDENCIA_A.write_text(json.dumps({"DATASET": "LIFECYCLE-EVIDENCE-V1",
                                             "PROVAS": []}), encoding="utf-8")
        LC.LIVRO.write_text(json.dumps(_livro()), encoding="utf-8")
        self.addCleanup(self._repor)

    def _repor(self):
        (PA.ESTADO, PA.DIARIO, LC.LIVRO, R.SAIDA, R.EVIDENCIA_A,
         RS.EVIDENCIA, RS.CONTRATOS) = self._antes

    def _escrever(self, doc):
        self.livro_do_bot.write_text(json.dumps(doc, ensure_ascii=False), encoding="utf-8")

    def _linhas_do_diario(self):
        if not PA.DIARIO.exists():
            return []
        return [l for l in PA.DIARIO.read_text(encoding="utf-8").splitlines() if l.strip()]


class OSnapshotEInteiroOuNaoE(ABancada):

    def test_rt_p1_meia_gravacao_nao_passa_por_livro_inteiro(self):
        """JSON truncado a meio NAO devolve meio livro: recusa e diz porque."""
        self.livro_do_bot.write_text('{"DATASET": "LIFECYCLE-LEDGER-V1", "TRANSI',
                                     encoding="utf-8")
        with self.assertRaises(PA.LeituraInstavel):
            PA.snapshot_do_bot(self.lane)

    def test_rt_p1b_ficheiro_que_muda_entre_leituras_e_recusado(self):
        """O caso real: o bot grava ENTRE as duas leituras. A segunda leitura
        difere da primeira, e um livro apanhado a meio nao pode atravessar."""
        original = PA._ler_inteiro
        estado = {"n": 0}

        def a_mudar(caminho, tentativas=1):
            estado["n"] += 1
            raise PA.LeituraInstavel("os bytes mudaram entre as duas leituras")

        PA._ler_inteiro = a_mudar
        self.addCleanup(lambda: setattr(PA, "_ler_inteiro", original))
        with self.assertRaises(PA.LeituraInstavel):
            PA.snapshot_do_bot(self.lane)
        self.assertGreaterEqual(estado["n"], 1)

    def test_rt_p7_o_corte_logico_e_o_sha_do_que_foi_lido(self):
        import hashlib
        snap = PA.snapshot_do_bot(self.lane)
        esperado = hashlib.sha256(self.livro_do_bot.read_bytes()).hexdigest()
        self.assertEqual(snap["SHA256"], esperado)
        self.assertEqual(snap["TRANSICOES"], 1)


class SemDecisaoNovaNadaAcontece(ABancada):

    def test_rt_p2_e_p3_livro_igual_e_noop_sem_escrever_no_diario(self):
        """A LEI C. O supervisor do bot grava um REALIMENTACAO identico de 15
        em 15 s (~5.760/dia). Este observador, sem novidade, NAO escreve."""
        primeira = PA.uma_volta(lane=self.lane)
        self.assertEqual(primeira["ACCAO"], "ATRAVESSOU")
        linhas_depois_da_primeira = len(self._linhas_do_diario())
        antes_livro = LC.LIVRO.read_bytes()

        for _ in range(5):
            r = PA.uma_volta(lane=self.lane)
            self.assertEqual(r["ACCAO"], "NO_OP", r)

        # nem o livro canonico nem o diario cresceram
        self.assertEqual(LC.LIVRO.read_bytes(), antes_livro)
        self.assertEqual(len(self._linhas_do_diario()), linhas_depois_da_primeira)
        e = PA.estado_lido()
        self.assertEqual(e["NOOPS"], 5)
        self.assertEqual(e["TRAVESSIAS"], 1)
        self.assertEqual(e["VOLTAS"], 6)

    def test_rt_p8_livro_diferente_sem_noticia_nao_conta_como_travessia(self):
        """LIVRO DIFERENTE != NOTICIA NOVA.

        Visto ao vivo: depois de se limpar o residuo de uma prova, o livro do
        bot ficou com outro `sha256` — mas SEM decisao nova nenhuma. A volta
        atravessa (o sha mudou) e nao acrescenta uma linha.

        Somar isso a `TRAVESSIAS` daria um contador que sobrestima, e alguem
        leria «3 travessias» onde houve 2. Conta-se a parte, e o diario
        continua calado: nao ha noticia para dar.
        """
        PA.uma_volta(lane=self.lane)                      # a primeira, essa e real
        linhas = len(self._linhas_do_diario())
        travessias = PA.estado_lido()["TRAVESSIAS"]

        # o livro muda de bytes (outra ordem de chaves) sem ganhar decisao
        doc = json.loads(self.livro_do_bot.read_text(encoding="utf-8"))
        doc["LEI"] = doc["LEI"] + " "                     # um byte a mais, zero decisoes
        self._escrever(doc)

        r = PA.uma_volta(lane=self.lane)
        self.assertEqual(r["ACCAO"], "ATRAVESSOU_SEM_NOVIDADE", r)
        self.assertEqual(r["LIVRO_CANONICO"]["APENDIDAS"], 0)
        e = PA.estado_lido()
        self.assertEqual(e["TRAVESSIAS"], travessias, "contou uma travessia que nao houve")
        self.assertEqual(e["LIVRO_NOVO_SEM_NOTICIA"], 1)
        self.assertEqual(len(self._linhas_do_diario()), linhas, "gritou sem noticia")

    def test_decisao_nova_do_bot_volta_a_atravessar(self):
        PA.uma_volta(lane=self.lane)
        self._escrever(_livro(
            _linha("IT-T9-900", LC.CANARY_PENDING, "2026-09-22T10:00:00+00:00"),
            _linha("IT-T9-901", LC.CANARY_PENDING, "2026-09-22T11:00:00+00:00")))
        r = PA.uma_volta(lane=self.lane)
        self.assertEqual(r["ACCAO"], "ATRAVESSOU", r)
        self.assertGreater(r["LIVRO_CANONICO"]["APENDIDAS"], 0)


class AFalhaNaoDerrubaENaoSeEngole(ABancada):

    def test_rt_p4_e_p5_falha_conta_se_e_fica_visivel(self):
        """NUNCA levanta (derrubava o ciclo) e NUNCA fica calada (era o
        DISCOVERY_HOOK_ERRO outra vez: 3054 ocorrencias, uma mensagem)."""
        self.livro_do_bot.unlink()
        for i in (1, 2, 3):
            r = PA.uma_volta(lane=self.lane)          # nao levanta
            self.assertEqual(r["ACCAO"], "FALHA")
            self.assertEqual(r["FALHAS_CONSECUTIVAS"], i)
        e = PA.estado_lido()
        self.assertEqual(e["SAUDE"], "DEGRADADO")
        self.assertTrue(e["ULTIMO_ERRO"])
        self.assertTrue(e["ULTIMO_ERRO_EM"])
        # a falha FICOU ESCRITA, uma linha por ocorrencia
        falhas = [json.loads(l) for l in self._linhas_do_diario()]
        self.assertEqual(sum(1 for f in falhas
                             if f["EVENTO"] == "FALHA_A_LER_O_LIVRO_DO_BOT"), 3)

    def test_recuperar_e_dito_e_o_contador_volta_a_zero(self):
        self.livro_do_bot.unlink()
        PA.uma_volta(lane=self.lane)
        self.assertEqual(PA.estado_lido()["FALHAS_CONSECUTIVAS"], 1)
        self._escrever(_livro(_linha("IT-T9-900", LC.CANARY_PENDING,
                                     "2026-09-22T10:00:00+00:00")))
        PA.uma_volta(lane=self.lane)
        e = PA.estado_lido()
        self.assertEqual(e["FALHAS_CONSECUTIVAS"], 0)
        self.assertEqual(e["SAUDE"], "SAUDAVEL")
        eventos = [json.loads(l)["EVENTO"] for l in self._linhas_do_diario()]
        self.assertIn("RECUPEROU", eventos)


class VivoNaoEOMesmoQueATrabalhar(ABancada):
    """RT-P9 — o irmao do lock orfao, do nosso lado.

    O supervisor do bot enganou toda a gente porque o lock afirmava um dono e
    ninguem perguntava ao relogio. O perigo simetrico e o processo que EXISTE
    e deixou de dar voltas: o PID responde, o estado diz SAUDAVEL, e o
    ficheiro esta parado no tempo.
    """

    def test_rt_p9_parado_no_tempo_e_detectado(self):
        from datetime import datetime, timedelta, timezone
        PA.uma_volta(lane=self.lane)
        s = PA.saude()
        self.assertTrue(s["A_TRABALHAR"], s)
        self.assertEqual(s["VIVACIDADE"], "A_TRABALHAR")

        # o mesmo estado, olhado MUITO mais tarde: o processo pode estar vivo
        futuro = datetime.now(timezone.utc) + timedelta(seconds=PA.INTERVALO_S * 10)
        s2 = PA.saude(agora_utc=futuro)
        self.assertFalse(s2["A_TRABALHAR"], s2)
        self.assertEqual(s2["VIVACIDADE"], "PARADO_NO_TEMPO")
        self.assertIn("pode estar vivo e nao estar a trabalhar", s2["PORQUE"])

    def test_rt_p9b_sem_nenhuma_volta_nao_se_finge_saudavel(self):
        s = PA.saude()
        self.assertEqual(s["VIVACIDADE"], "NUNCA_DEU_UMA_VOLTA")
        self.assertFalse(s["A_TRABALHAR"])


class NaoSeEscreveNaLaneDoBot(ABancada):

    def test_rt_p6_a_lane_do_bot_fica_byte_a_byte_igual(self):
        """O observador LE a lane do bot. Se lhe escrevesse, estaria a mexer na
        arvore de um servico a correr — e era outra pessoa a decidir isso."""
        antes = {p: p.read_bytes() for p in (self.lane / "curadoria").rglob("*")
                 if p.is_file()}
        PA.uma_volta(lane=self.lane)
        PA.uma_volta(lane=self.lane)
        depois = {p: p.read_bytes() for p in (self.lane / "curadoria").rglob("*")
                  if p.is_file()}
        self.assertEqual(sorted(map(str, antes)), sorted(map(str, depois)),
                         "o observador criou ou apagou ficheiros na lane do bot")
        for p, b in antes.items():
            self.assertEqual(depois[p], b, "o observador escreveu em %s" % p.name)

    def test_o_codigo_nao_tem_escrita_para_a_lane_do_bot(self):
        """Guarda de texto: nenhuma chamada de escrita sobre a lane do bot."""
        texto = (AQUI / "ponte_automatica.py").read_text(encoding="utf-8")
        for proibido in ("LANE_DO_BOT /", "lane /"):
            for escrita in ("write_text", "write_bytes", "mkdir", "unlink"):
                self.assertNotIn("%s%s" % (proibido, escrita), texto)
        self.assertNotIn("subprocess", texto,
                         "o observador nao corre comandos — so le ficheiros")


class ALaneDizSeNaLinhaDeComando(ABancada):
    """Defeito 6 do ensaio X1: sem --lane, o observador so observava a pasta
    fixa. E a lane nunca pode ser a casa da ponte (o livro seria o mesmo)."""

    def test_lane_da_linha_de_comando_e_a_que_se_le(self):
        import io
        from contextlib import redirect_stdout
        with redirect_stdout(io.StringIO()):
            rc = PA.main(["--servir", "--voltas", "1", "--intervalo", "0",
                          "--lane", str(self.lane)])
        self.assertEqual(rc, 0)
        arranque = json.loads(self._linhas_do_diario()[0])
        self.assertEqual(arranque["LANE_DO_BOT"], str(self.lane))
        import hashlib
        self.assertEqual(PA.estado_lido()["ULTIMO_LIVRO_VISTO"]["SHA256"],
                         hashlib.sha256(self.livro_do_bot.read_bytes()).hexdigest())

    def test_uma_volta_sem_servir_tambem_obedece_a_lane(self):
        import io
        from contextlib import redirect_stdout
        out = io.StringIO()
        with redirect_stdout(out):
            rc = PA.main(["--lane", str(self.lane)])
        self.assertEqual(rc, 0)
        r = json.loads(out.getvalue())
        import hashlib
        self.assertEqual((r["ACCAO"], r["BOT"]["SHA256"]),
                         ("ATRAVESSOU", hashlib.sha256(self.livro_do_bot.read_bytes()).hexdigest()))

    def test_lane_que_e_a_casa_da_ponte_e_recusada_sem_escrever(self):
        import io
        from contextlib import redirect_stdout
        LC.LIVRO = self.livro_do_bot           # a ponte a correr DENTRO da pasta do bot
        antes = self.livro_do_bot.read_bytes()
        out = io.StringIO()
        with redirect_stdout(out):
            rc = PA.main(["--servir", "--voltas", "1", "--intervalo", "0",
                          "--lane", str(self.lane)])
        self.assertEqual(rc, 2)
        r = json.loads(out.getvalue())
        self.assertEqual((r["PORQUE"], r["MESMOS_FICHEIROS"]),
                         ("LANE_E_A_CASA_DA_PONTE", ["LIFECYCLE-LEDGER-V1.json"]))
        self.assertEqual(self.livro_do_bot.read_bytes(), antes)
        self.assertEqual(self._linhas_do_diario(), [])
        self.assertFalse(PA.ESTADO.exists())

    def test_so_as_provas_ou_os_contratos_iguais_tambem_recusam(self):
        R.CONTRATOS_A = self.lane / "curadoria" / "italy_contracts_curator.json"
        try:
            self.assertEqual(PA.lane_separada(self.lane), ["italy_contracts_curator.json"])
        finally:
            R.CONTRATOS_A = self._contratos_a
        self.assertEqual(PA.lane_separada(self.lane), [])


if __name__ == "__main__":
    unittest.main(verbosity=2)
