#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""VOCI DAL CAMPO — o contrato do item Voce, provado com os transcritos que JA estao no repositorio.

    py -m unittest tests.test_voce_dal_campo

Duas especies de caso, e o nome da classe diz qual e:
  · Fixture*   transcritos REAIS versionados (data/samples/ES-T8-001, SENSOR-PILOT, REEL-TRANSCRICOES).
               Nenhum dado da Sala: a nuvem nao os tem (ordem da missao).
  · Sintetico* textos ESCRITOS AQUI para isolar uma lei. Marcados SOURCE_ID = 'SINTETICO' — nunca
               entram numa contagem nem num card.
Sem rede, sem banco, sem ficheiros escritos.
"""
import os
import sys
import unittest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(RAIZ, 'motor'))
import voce_dal_campo as vc  # noqa: E402
import matriz_recorte as MR  # noqa: E402

NS = vc.NAO_SEI
_DOCS = None


def docs():
    global _DOCS
    if _DOCS is None:
        _DOCS = {d['EXTERNAL_ID']: d for d in vc.documentos_do_repo(RAIZ)}
    return _DOCS


def vozes(ext):
    d = docs()[ext]
    return d, vc.extrair(d)


def sintetico(texto, published_at='2025-05-03', channel='Canale di prova', **kw):
    d = vc.documento(texto, source_id='SINTETICO', external_id='SINT', published_at=published_at, channel=channel,
                     **kw)
    return d, vc.extrair(d)


def a_frase(r, pedaco):
    return [v for v in r['VOZES'] if pedaco in v['QUOTE_ORIGINAL']]


class FixtureTodoOCorpus(unittest.TestCase):
    """As leis que valem para CADA voz extraida dos 47 transcritos versionados."""

    @classmethod
    def setUpClass(cls):
        cls.pares = [(d, v) for d in docs().values() for v in vc.extrair(d)['VOZES']]

    def test_ha_corpus_e_ha_vozes(self):
        # entrada vazia nao prova nada (INT-LAW-113): se os fixtures sumirem, isto reprova em vez de passar
        self.assertGreaterEqual(len(docs()), 40)
        self.assertGreater(len(self.pares), 100)

    def test_toda_voz_cumpre_o_contrato(self):
        falhas = [(v['VOICE_ID'], vc.validar_voce(v, d)) for d, v in self.pares if vc.validar_voce(v, d)]
        self.assertEqual(falhas, [])

    def test_citacao_e_o_texto_exacto_na_posicao(self):
        for d, v in self.pares:
            self.assertEqual(d['TEXT'][v['QUOTE_POS_START']:v['QUOTE_POS_END']], v['QUOTE_ORIGINAL'])

    def test_publicacao_nunca_vira_tempo_do_facto(self):
        for d, v in self.pares:
            if v['FACT_TIME'] != NS:
                self.assertNotEqual(v['FACT_TIME'], v['PUBLISHED_AT'])
                self.assertIn(v['FACT_TIME_BASIS'].split(' ')[0],
                              ('ESCRITO_NA_FRASE_DA_CITACAO', 'leis/fato_local.tempo_do_fato'))

    def test_quem_publica_nunca_e_o_falante(self):
        for d, v in self.pares:
            if v['SPEAKER_ID'] != NS:
                self.assertNotEqual(v['SPEAKER_NAME'], v['PUBLISHER'])

    def test_voice_id_estavel_entre_corridas(self):
        d = docs()['QXwvQiufKxg']
        self.assertEqual([v['VOICE_ID'] for v in vc.extrair(d)['VOZES']],
                         [v['VOICE_ID'] for v in vc.extrair(d)['VOZES']])

    def test_voz_sem_metodo_nao_e_incidencia(self):
        for d, v in self.pares:
            self.assertIn('NAO E INCIDENCIA', v['WHAT_IT_DOES_NOT_PROVE'])

    def test_vocabulario_de_cultura_e_problema_tem_um_dono(self):
        # INT-LAW-000: as chaves sao as de motor/matriz_recorte.py, e nenhuma outra
        self.assertEqual(set(vc._PADROES_CULTURA), set(MR.CROPS))
        self.assertEqual(set(vc._PADROES_PROBLEMA), set(MR.ISSUES))
        for d, v in self.pares:
            self.assertIn(v['CROP'], set(MR.CROPS) | {NS})
            self.assertIn(v['ISSUE'], set(MR.ISSUES) | {NS})


class FixtureAgricultoraDeHautFrance(unittest.TestCase):
    """QXwvQiufKxg · «Ellisabeth, a farmer in the Aras area of Haut-France» — o lugar dela NAO e o do facto."""

    def setUp(self):
        self.d, self.r = vozes('QXwvQiufKxg')

    def test_papel_agricultor_e_t8_com_trecho(self):
        f = [x for x in self.r['FALANTES'] if x['SPEAKER_NAME'] == 'Ellisabeth']
        self.assertEqual(len(f), 1)
        self.assertEqual(f[0]['ROLE'], vc.AGRICULTOR)
        self.assertEqual(f[0]['UNIVERSO_DO_PAPEL'], 'T8')
        self.assertIn('a farmer', f[0]['ROLE_EVIDENCE'][0]['TRECHO'])

    def test_relato_de_2024_tem_tempo_e_nao_tem_lugar(self):
        v = a_frase(self.r, 'In 2024, we encountered difficulties with the septoria')[0]
        self.assertEqual(v['SPEAKER_NAME'], 'Ellisabeth')
        self.assertEqual(v['STATEMENT_KIND'], vc.RELATO)
        self.assertEqual(v['ISSUE'], 'SEPTORIA')
        self.assertEqual(v['FACT_TIME'], 'in 2024')
        self.assertIn('Haut-France', v['SPEAKER_PLACE'])
        self.assertEqual(v['FACT_LOCATION'], NS)          # lugar da pessoa != lugar do facto

    def test_titulo_frances_legenda_inglesa_e_suspeita_e_nao_carimbo(self):
        # C6: quem infere pode suspeitar, nao pode carimbar. A especie e de regras/proveniencia.py.
        for v in self.r['VOZES']:
            self.assertEqual(v['QUOTE_TRANSLATION_SUSPECT'], vc.SUSPEITA_SIM)
            self.assertEqual(v['TEXT_KIND'], vc.PV.NAO_SEI)
            self.assertEqual(v['QUOTE_IS_SPEAKERS_WORDS'], 'NAO_PROVADO')


class FixturePesquisadorDeWisconsin(unittest.TestCase):
    """EsdOflKtFIU · Damon Smith, pathologist at the University of Wisconsin — identidade != expertise."""

    def setUp(self):
        self.d, self.r = vozes('EsdOflKtFIU')

    def test_papel_organizacao_e_tipo(self):
        f = [x for x in self.r['FALANTES'] if x['SPEAKER_NAME'] == 'Damon Smith'][0]
        self.assertEqual(f['ROLE'], vc.INVESTIGADOR)
        self.assertEqual(f['ORGANIZATION'], 'University of Wisconsin Madison')
        self.assertEqual(f['ORGANIZATION_KIND'], 'UNIVERSIDADE_PESQUISA')
        self.assertEqual(f['UNIVERSO_DO_PAPEL'], 'NAO_T8')

    def test_lugar_da_cena_do_relato_e_nao_da_universidade(self):
        v = a_frase(self.r, 'field of soft red winter wheat that actually has fusarium')[0]
        self.assertEqual((v['CROP'], v['ISSUE']), ('CEREAL', 'FUSARIUM'))
        self.assertIn('Arlington Prairie', v['FACT_LOCATION'])
        self.assertNotIn('University', v['FACT_LOCATION'])
        self.assertTrue(v['FACT_LOCATION_BASIS'].startswith('CENA_DO_RELATO'))
        self.assertEqual(v['FACT_TIME'], NS)             # «today» nao se converte

    def test_papel_declarado_nao_prova_expertise_no_tema(self):
        v = a_frase(self.r, 'field of soft red winter wheat')[0]
        self.assertEqual(v['EXPERTISE_TEMATICA'], 'NAO_PROVADA')


class FixtureApresentadoPorOutro(unittest.TestCase):
    """VZGepvBdkoI · a apresentadora apresenta «Rory Cranston, technical product lead with Bayer»."""

    def setUp(self):
        self.d, self.r = vozes('VZGepvBdkoI')

    def test_papel_e_empresa_do_convidado(self):
        f = [x for x in self.r['FALANTES'] if x['SPEAKER_NAME'] == 'Rory Cranston'][0]
        self.assertEqual(f['ROLE'], vc.TECNICO)
        self.assertEqual(f['ROLE_STATE'], vc.TERCEIRO)
        self.assertEqual((f['ORGANIZATION'], f['ORGANIZATION_KIND']), ('Bayer', 'EMPRESA'))

    def test_apresentado_por_outro_nao_passa_a_ser_quem_fala(self):
        rory = [x['SPEAKER_ID'] for x in self.r['FALANTES'] if x['SPEAKER_NAME'] == 'Rory Cranston'][0]
        self.assertNotIn(rory, {v['SPEAKER_ID'] for v in self.r['VOZES']})

    def test_troca_de_voz_marcada_desliga_a_atribuicao(self):
        for v in a_frase(self.r, '>>'):
            self.assertEqual(v['SPEAKER_ID'], NS)


class FixtureSemFalanteEInstituicao(unittest.TestCase):

    def test_sem_apresentacao_nao_ha_speaker(self):
        d, r = vozes('rqII-vRZZTY')
        self.assertTrue(r['VOZES'])
        for v in r['VOZES']:
            self.assertEqual((v['SPEAKER_ID'], v['ROLE']), (NS, NS))

    def test_reel_da_syngenta_e_voz_da_instituicao_com_audio_original(self):
        d, r = vozes('C-FanW_CYMz')
        self.assertTrue(r['VOZES'])
        for v in r['VOZES']:
            self.assertEqual(v['SPEAKER_KIND'], vc.INSTITUICAO)
            self.assertEqual(v['PUBLISHER_KIND'], 'EMPRESA')
            self.assertEqual(v['SPEAKER_ID'], NS)
            self.assertEqual((v['TEXT_KIND'], v['TEXT_KIND_BASIS']), (vc.PV.ASR_LOCAL, vc.PV.PRODUCED_BY_LOCAL_ASR))
            self.assertEqual(v['QUOTE_IS_SPEAKERS_WORDS'], 'SIM')
            self.assertIsInstance(v['QUOTE_T_S'], (int, float))    # o segundo do audio, dos segmentos

    def test_canal_que_pede_inscricao_e_criador(self):
        d, r = vozes('kFHEEmcqdc0')
        self.assertTrue(r['VOZES'])
        self.assertEqual({v['PUBLISHER_KIND'] for v in r['VOZES']}, {'CRIADOR_DE_CONTEUDO'})


class FixtureLegendaSemPontuacao(unittest.TestCase):
    """ES-T8-001 · legenda espanhola sem ponto final: palestra inteira era UMA frase."""

    def test_citacao_e_pedaco_curto_marcado(self):
        d, r = vozes('HdI2-O6pM0E')
        self.assertTrue(r['VOZES'])
        for v in r['VOZES']:
            self.assertEqual(v['QUOTE_BOUNDARY'], vc.PEDACO)
            self.assertLessEqual(len(v['QUOTE_ORIGINAL'].split()), vc.PALAVRAS_POR_PEDACO)
            # o nosso ficheiro chama ao campo TRANSCRIPT_ORIGINAL; a rota nao declarou a lingua. Rotulo != especie.
            self.assertTrue(v['DATASET_FIELD_LABEL'].startswith('TRANSCRIPT_ORIGINAL'))
            self.assertEqual(v['TEXT_KIND'], vc.PV.NAO_SEI)
            self.assertEqual(v['QUOTE_IS_SPEAKERS_WORDS'], 'NAO_PROVADO')

    def test_palavra_de_ligacao_com_virgula_nao_vira_pessoa(self):
        # medido na 1.a corrida: «Bueno, …», «Entonces, …», «However, …» saiam como 187 falantes falsos
        nomes = {f['SPEAKER_NAME'] for d in docs().values() for f in vc.extrair(d)['FALANTES']}
        for falso in ('Bueno', 'Entonces', 'Mejor', 'However', 'Therefore', 'Yeah', 'Finally'):
            self.assertNotIn(falso, nomes)

    def test_maiuscula_aleatoria_nao_vira_lugar(self):
        for ext in ('nyIrd9Ihl_c', 'HdI2-O6pM0E', 'dgG6DbcRQP0', 'TQH1rUR8ZQ4'):
            d, r = vozes(ext)
            for v in r['VOZES']:
                for lugar in ('Viña', 'Dios', 'Ho', 'Bueno'):
                    self.assertNotIn(lugar, v['FACT_LOCATION'].split(' ; '))


class SinteticoItaliano(unittest.TestCase):
    """SINTETICO — o leitor italiano de lugar e tempo e o de leis/fato_local.py."""

    def test_agronomo_com_consorzio_e_relato_em_ravenna(self):
        d, r = sintetico("Buongiorno, sono Marco Rossi, agronomo presso il Consorzio Agrario di Bologna. "
                         "Nel mese di maggio abbiamo riscontrato attacchi di peronospora sulla vite a Ravenna.")
        v = r['VOZES'][-1]
        self.assertEqual((v['SPEAKER_NAME'], v['ROLE']), ('Marco Rossi', vc.AGRONOMO))
        self.assertEqual((v['ORGANIZATION'], v['ORGANIZATION_KIND']), ('Consorzio Agrario di Bologna', 'ASSOCIACAO'))
        self.assertEqual((v['CROP'], v['ISSUE']), ('VINE', 'DOWNY_MILDEW'))
        self.assertEqual(v['FACT_LOCATION'], 'Ravenna')                 # e NAO Bologna, a sede
        self.assertEqual(v['FACT_TIME'], 'maggio')
        self.assertTrue(v['FACT_TIME_BASIS'].startswith('leis/fato_local'))
        self.assertEqual(vc.validar_voce(v, d), [])

    def test_viticoltore_em_toscana_quest_anno(self):
        d, r = sintetico("Sono Luca Bianchi, viticoltore in Toscana. Quest'anno abbiamo visto la flavescenza nella vigna.")
        v = r['VOZES'][0]
        self.assertEqual((v['ROLE'], v['UNIVERSO_DO_PAPEL']), (vc.AGRICULTOR, 'T8'))
        self.assertEqual(v['SPEAKER_PLACE'], 'Toscana')
        self.assertEqual(v['FACT_LOCATION'], NS)
        self.assertEqual(v['FACT_TIME'], NS)
        self.assertEqual(v['FACT_TIME_EXPRESSAO'], "quest'anno")

    def test_influenciador_sem_papel_profissional(self):
        d, r = sintetico("Ciao ragazzi, sono Giulio Verdi, benvenuti. La peronospora della vite torna ogni anno. "
                         "Iscrivetevi al mio canale!")
        v = r['VOZES'][0]
        self.assertEqual(v['ROLE'], vc.INFLUENCIADOR)
        self.assertEqual(v['UNIVERSO_DO_PAPEL'], 'NAO_T8')
        self.assertTrue(v['CREATOR_SIGNALS'])

    def test_agronoma_que_tambem_pede_inscricao_continua_agronoma(self):
        d, r = sintetico("Sono Anna Neri, agronoma. La peronospora della vite si combatte presto. "
                         "Iscrivetevi al mio canale!")
        v = r['VOZES'][0]
        self.assertEqual(v['ROLE'], vc.AGRONOMO)
        self.assertTrue(v['CREATOR_SIGNALS'])                 # o sinal fica a vista


class SinteticoIngles(unittest.TestCase):

    def test_data_igual_a_publicacao_nao_e_tempo_do_facto(self):
        d, r = sintetico("My name is John Doe, I'm a farmer. On May 3, 2025 we found septoria in the wheat.",
                         published_at='2025-05-03')
        self.assertEqual(r['VOZES'][0]['FACT_TIME'], NS)

    def test_data_escrita_diferente_da_publicacao_e_tempo_do_facto(self):
        d, r = sintetico("My name is John Doe, I'm a farmer. On May 10, 2024 we found septoria in the wheat.",
                         published_at='2025-05-03')
        v = r['VOZES'][0]
        self.assertEqual((v['FACT_TIME'], v['FACT_TIME_PRECISION']), ('may 10, 2024', 'DATE_EXACT'))
        self.assertEqual((v['ROLE'], v['UNIVERSO_DO_PAPEL']), (vc.AGRICULTOR, 'T8'))

    def test_troca_de_voz_no_inicio_da_citacao(self):
        d, r = sintetico("My name is John Doe, I'm a farmer. >> We found septoria in the wheat.")
        self.assertEqual(r['VOZES'][0]['SPEAKER_ID'], NS)

    def test_frase_curta_de_apresentacao_nao_cola_o_papel_do_seguinte(self):
        d, r = sintetico("I'm Amber Bell. I am here with Rory Cranston, who's the technical lead with Bayer. "
                         "We found septoria in the wheat.")
        amber = [f for f in r['FALANTES'] if f['SPEAKER_NAME'] == 'Amber Bell'][0]
        self.assertEqual((amber['ROLE'], amber['ORGANIZATION']), (NS, NS))
        self.assertEqual(r['VOZES'][0]['SPEAKER_NAME'], 'Amber Bell')

    def test_mesmo_nome_mesmo_speaker_id(self):
        _, r1 = sintetico("My name is John Doe, I'm a farmer. We found septoria in the wheat.")
        _, r2 = sintetico("Hello. My name is John  Doe. The wheat had septoria.")
        self.assertEqual(r1['VOZES'][0]['SPEAKER_ID'], r2['VOZES'][0]['SPEAKER_ID'])

    def test_sem_source_id_fica_nao_sei_e_nao_e_inventado(self):
        d = vc.documento("My name is John Doe, I'm a farmer. We found septoria in the wheat.")
        v = vc.extrair(d)['VOZES'][0]
        self.assertEqual((v['SOURCE_ID'], v['EXTERNAL_ID'], v['PUBLISHED_AT']), (NS, NS, NS))


class SinteticoOValidadorApanha(unittest.TestCase):
    """O contrato tem de REPROVAR cada violacao — um validador que aceita tudo nao prova nada."""

    def setUp(self):
        self.d, r = sintetico("My name is John Doe, I'm a farmer in Kent. On May 10, 2024 we found septoria "
                              "in the wheat.")
        self.v = dict(r['VOZES'][0])
        self.assertEqual(vc.validar_voce(self.v, self.d), [])

    def reprova(self, lei, **mudar):
        v = dict(self.v, **mudar)
        self.assertTrue(any(e.startswith(lei) for e in vc.validar_voce(v, self.d)), (lei, vc.validar_voce(v, self.d)))

    def test_citacao_reescrita(self):
        self.reprova('CITACAO_NAO_E_O_TEXTO', QUOTE_ORIGINAL=self.v['QUOTE_ORIGINAL'].replace('found', 'saw'))

    def test_interpretacao_sem_assinatura(self):
        self.reprova('INTERPRETACAO_SEM_ASSINATURA', INTERPRETACAO={'AUTOR': 'John Doe', 'LEITURA': 'x'})

    def test_publicacao_no_tempo_do_facto(self):
        self.reprova('PUBLICACAO_VIROU_TEMPO_DO_FACTO', FACT_TIME=self.v['PUBLISHED_AT'])

    def test_t8_sem_agricultor(self):
        self.reprova('T8_SO_E_AGRICULTOR', ROLE=vc.TECNICO)

    def test_lugar_da_pessoa_no_lugar_do_facto(self):
        self.reprova('LUGAR_DA_PESSOA_VIROU_LUGAR_DO_FACTO', SPEAKER_PLACE='Kent', FACT_LOCATION='Kent',
                     FACT_LOCATION_EVIDENCE=self.v['QUOTE_ORIGINAL'], FACT_LOCATION_EVIDENCE_POS=self.v['QUOTE_POS_START'])

    def test_lugar_sem_trecho(self):
        self.reprova('LUGAR_DO_FACTO_FORA', FACT_LOCATION='Kent', FACT_LOCATION_EVIDENCE='Kent is nice',
                     FACT_LOCATION_EVIDENCE_POS=0)

    def test_papel_sem_prova(self):
        self.reprova('PAPEL_SEM_PROVA', ROLE=vc.AGRONOMO, UNIVERSO_DO_PAPEL='NAO_T8')

    def test_instituicao_com_speaker(self):
        self.reprova('INSTITUICAO_OU_NINGUEM', SPEAKER_KIND=vc.INSTITUICAO)

    def test_atribuicao_provada(self):
        self.reprova('ATRIBUICAO_PROVADA', ATTRIBUTION_STATE='PROVADA_POR_DIARIZACAO')

    def test_sem_ressalva_de_incidencia(self):
        self.reprova('VOZ_SEM_A_RESSALVA', WHAT_IT_DOES_NOT_PROVE='nada')

    def test_publisher_como_falante(self):
        self.reprova('PUBLISHER_VIROU_FALANTE', SPEAKER_NAME=self.v['PUBLISHER'])

    def test_fala_da_pessoa_sem_especie(self):
        self.reprova('FALA_DA_PESSOA_SEM_ESPECIE', QUOTE_IS_SPEAKERS_WORDS='SIM')

    def test_especie_inventada(self):
        self.reprova('ESPECIE_DO_TEXTO_FORA_DO_DONO', TEXT_KIND='PROVAVEL_TRADUCAO')

    def test_influenciador_com_papel(self):
        self.reprova('INFLUENCIADOR_COM_PAPEL', ROLE=vc.INFLUENCIADOR, UNIVERSO_DO_PAPEL='NAO_T8')


if __name__ == '__main__':
    unittest.main()
