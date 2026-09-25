"""D36 · A FASE EQUIVALENTE SÓ VALE COM AS QUATRO PROVAS NO ITEM.

O contrato destes canais pede `canal-youtube`; a corrida que traz o som declara
`audio-youtube`. O dono (bot Luciano, 25/09 02:20) escolheu a opção (a): o contrato
passa a aceitar esse envelope — **mas só** quando o item prova de que canal veio,
quando foi publicado, que o dono autorizou, e a ligação canal→vídeo→áudio inteira.

A opção (b) — o coletor de áudio passar a chamar-se `canal-youtube` — foi RECUSADA:
uma lista de contas não é a observação delas.

Estes testes medem as duas metades da lei:
  · com as quatro provas → o item segue a mesma régua de sempre (e pode ficar READY);
  · sem QUALQUER uma delas → reprova, e o motivo nomeia a prova que falta.

Nenhum teste aqui toca em rede, em disco ou no banco: `julgar()` é pura.
"""
import sys
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
import _gavetas  # noqa: E402,F401 — põe as gavetas do processo no caminho
sys.path.insert(0, str(RAIZ / "curadoria"))
import regua_social as R  # noqa: E402

SID = "IT-T9-029"
CANAL = "UC4A5UdkaIvcbaA7z1mz-YdA"
CONTRATO = {"SOURCE_ID": SID, "NAME": "Cifo Giardinaggio",
            "ACQUISITION": {"STRATEGY": "SCRAP_FASE", "FASE": "canal-youtube",
                            "CAPACIDADE": "youtube.channel.discovery", "CHANNEL_ID": CANAL}}


def item(**mudar) -> dict:
    """Um item com tudo o que o bloco A passou a registar — medido ao vivo em 25/09."""
    ob = {
        "NATIVE_ID": "ehjdygGJJqQ",
        "TITLE": "Come si pota il limone",
        "PUBLISHED_AT": "2026-02-11T15:02:31Z",
        "PUBLISHED_AT_PRECISION": "SECOND",
        "COLLECTED_AT": "2026-09-25T04:59:32+00:00",
        "FACT_TIME": "NAO SEI",
        "CHANNEL_ID": CANAL,
        "CHANNEL_ID_ESTADO": "DECLARADO_PELA_PLATAFORMA",
        "CHANNEL_NAME": "Cifo Giardinaggio",
        "CHANNEL_URL": "https://www.youtube.com/channel/" + CANAL,
        "OWNER_AUTHORIZED": "SIM",
        "PLATFORM_POLICY_STATUS": "DISALLOWED",
        "AUTORIZACAO_DE": "leis/social_matriz.py",
        "AUDIO_BYTES": 2967630,
        "AUDIO_DURATION_S": 92.74,
        "AUDIO_SHA256": "288c88d244087cbe2c08c3c352580f7c1797683d9693f70835a1b52a5be7541",
        "AUDIO_REFERENCE": "data/samples/YOUTUBE-TRANSCRICOES/audio-cache/ehjdygGJJqQ.wav",
        "RAW": {"CHANNEL_ID": CANAL, "CREATOR_NAME": "Cifo Giardinaggio",
                "CREATOR_URL": "https://www.youtube.com/channel/" + CANAL},
    }
    ob.update(mudar)
    return {"OBSERVACAO": ob}


def envelope(itens=None, fase="audio-youtube", **mudar) -> dict:
    e = {"SOURCE_ID_DO_PEDIDO": SID, "FASE": fase, "PLATFORM": "YOUTUBE",
         "COLHEITA": itens if itens is not None else [item()],
         "SUPORTE": [{"ESPECIE": "RUN_RECEIPT", "RESUMO": {"RESULT": "OK"}}]}
    e.update(mudar)
    return e


def veredicto(env, raw=1, contrato=CONTRATO):
    return R.julgar(env, SID, (contrato.get("ACQUISITION") or {}).get("FASE"), raw,
                    slug=None, nome_da_fonte=contrato.get("NAME"), contrato=contrato)


class AComAsQuatroProvas(unittest.TestCase):
    def test_1_o_item_segue_a_regua_e_fica_READY(self):
        """Com as quatro provas, a equivalência vale e o resto da régua decide igual."""
        v, porque = veredicto(envelope())
        self.assertEqual(v, R.READY, porque)

    def test_2_ser_prova_pura_nao_basta_sem_linha_no_banco(self):
        """Visto ≠ guardado: sem linha RAW, READY não existe — a prova não o compra."""
        v, porque = veredicto(envelope(), raw=0)
        self.assertEqual(v, R.FALHA, porque)
        self.assertIn("0 linhas RAW", porque)


class SemQualquerUmaDasQuatroProvasReprova(unittest.TestCase):
    def test_3_sem_canal_de_origem(self):
        v, porque = veredicto(envelope([item(CHANNEL_ID=None, CHANNEL_URL=None)]))
        self.assertEqual(v, R.FALHA)
        self.assertIn("CANAL_DE_ORIGEM", porque)

    def test_4_sem_data_de_publicacao(self):
        v, porque = veredicto(envelope([item(PUBLISHED_AT=None)]))
        self.assertEqual(v, R.FALHA)
        self.assertIn("DATA_DE_PUBLICACAO", porque)

    def test_5_data_sem_precisao_declarada_tambem_reprova(self):
        """A data vale pela precisão que traz: 'SECOND' é prova, um número solto não."""
        v, porque = veredicto(envelope([item(PUBLISHED_AT_PRECISION=None)]))
        self.assertEqual(v, R.FALHA)
        self.assertIn("sem precisao declarada", porque)

    def test_6_sem_autorizacao_do_dono(self):
        v, porque = veredicto(envelope([item(OWNER_AUTHORIZED="NAO")]))
        self.assertEqual(v, R.FALHA)
        self.assertIn("AUTORIZACAO_DO_DONO", porque)

    def test_7_ligacao_quebrada_canal_de_outro(self):
        outro = item(CHANNEL_ID="UCzzzzzzzzzzzzzzzzzzzzzz")
        v, porque = veredicto(envelope([outro]))
        self.assertEqual(v, R.FALHA)
        self.assertIn("LIGACAO_CANAL_VIDEO_AUDIO", porque)

    def test_8_ligacao_quebrada_sem_o_video(self):
        v, porque = veredicto(envelope([item(NATIVE_ID=None)]))
        self.assertEqual(v, R.FALHA)
        self.assertIn("LIGACAO_CANAL_VIDEO_AUDIO", porque)

    def test_9_ligacao_quebrada_sem_o_audio_adquirido(self):
        v, porque = veredicto(envelope([item(AUDIO_SHA256=None, AUDIO_BYTES=0)]))
        self.assertEqual(v, R.FALHA)
        self.assertIn("LIGACAO_CANAL_VIDEO_AUDIO", porque)

    def test_10_audio_guardado_que_nao_nomeia_o_video(self):
        """O ficheiro do som tem de apontar para o vídeo: é isso que fecha a cadeia."""
        v, porque = veredicto(envelope([item(AUDIO_REFERENCE="audio-cache/outro.wav")]))
        self.assertEqual(v, R.FALHA)
        self.assertIn("nao nomeia o video", porque)

    def test_11_contrato_sem_CHANNEL_ID_nao_prova_a_ligacao(self):
        c = {"SOURCE_ID": SID, "NAME": "Cifo Giardinaggio",
             "ACQUISITION": {"FASE": "canal-youtube"}}
        v, porque = veredicto(envelope(), contrato=c)
        self.assertEqual(v, R.FALHA)
        self.assertIn("o contrato nao declara CHANNEL_ID", porque)


class NaoHaExcecaoGenerica(unittest.TestCase):
    def test_12_par_de_fases_nao_declarado_reprova(self):
        """Só a equivalência declarada passa. Outra fase continua a reprovar como antes."""
        v, porque = veredicto(envelope(fase="comentarios-youtube"))
        self.assertEqual(v, R.FALHA)
        self.assertIn("A_EQUIVALENCIA_NAO_ESTA_DECLARADA", porque)

    def test_13_o_par_invertido_nao_esta_declarado(self):
        """`canal-youtube` a satisfazer um contrato de `audio-youtube` não é a lei."""
        c = {"SOURCE_ID": SID, "NAME": "Cifo Giardinaggio",
             "ACQUISITION": {"FASE": "audio-youtube", "CHANNEL_ID": CANAL}}
        v, porque = veredicto(envelope(fase="canal-youtube"), contrato=c)
        self.assertEqual(v, R.FALHA)
        self.assertIn("A_EQUIVALENCIA_NAO_ESTA_DECLARADA", porque)

    def test_14_envelope_sem_colheita_nao_prova_nada(self):
        v, porque = veredicto(envelope(itens=[]))
        self.assertEqual(v, R.FALHA)
        self.assertIn("COLHEITA_VAZIA", porque)

    def test_15_a_mesma_fase_de_sempre_nao_passa_por_aqui(self):
        """Quando a fase bate, o critério é o de sempre: esta equivalência nem corre."""
        faltam = R.provas_da_equivalencia(envelope(fase="canal-youtube"), "canal-youtube", CONTRATO)
        self.assertEqual(faltam, ["A_EQUIVALENCIA_NAO_ESTA_DECLARADA"])

    def test_16_o_estado_do_item_nao_compra_a_data(self):
        """FACT_TIME continua NAO SEI: a publicação não vira tempo do facto."""
        ob = item()["OBSERVACAO"]
        self.assertEqual(ob["FACT_TIME"], "NAO SEI")
        self.assertNotEqual(ob["PUBLISHED_AT"], ob["COLLECTED_AT"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
