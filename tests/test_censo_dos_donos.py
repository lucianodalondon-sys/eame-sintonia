#!/usr/bin/env python3
"""O CENSO DOS DONOS — medir antes de nomear dono novo.

    REUSE FIRST.

Antes de a observabilidade escrever uma linha de telemetria, a pergunta e:
quem JA responde por cada conceito? Esta casa ja errou ao contrario — desenhou
primeiro, mediu depois, e o buraco ficou do tamanho da tampa ja comprada.

O QUE ESTE FICHEIRO GUARDA
--------------------------
Que o censo continue a MEDIR e nao a RECOMENDAR, e que nao publique buracos
que sao artefato da propria medida.
"""
import json
import os
import unittest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DONOS = os.path.join(RAIZ, 'system-map', 'data', 'donos.generated.json')


def _json(p):
    with open(p, encoding='utf-8') as f:
        return json.load(f)


class OCensoMedeENaoRecomenda(unittest.TestCase):

    def setUp(self):
        self.d = _json(DONOS)

    def test_diz_por_escrito_que_nao_propoe_schema(self):
        """Um censo que ja recomenda deixou de medir."""
        junto = self.d['O_QUE_NAO_E'].lower()
        self.assertIn('schema', junto)
        self.assertIn('tabela', junto)

    def test_todo_conceito_diz_como_foi_medido(self):
        for c in self.d['DETALHE']:
            self.assertTrue(c['COMO_FOI_MEDIDO'], c['CONCEITO'])

    def test_o_vocabulario_de_estado_e_fechado(self):
        vale = {'UM_DONO', 'DONO_DUPLICADO', 'SEM_DONO_MAS_LIDO',
                'DONO_E_INSTRUMENTO', 'UNKNOWN'}
        for c in self.d['DETALHE']:
            self.assertIn(c['ESTADO'], vale, c['CONCEITO'])


class NaoPublicarBuracoQueEArtefatoDaMedida(unittest.TestCase):
    """⚠️ O censo exclui `system-map/`, `provas/` e `tests/` porque citam tudo
    por oficio. Mas ha conceitos cujo dono legitimo mora la — o modelo de
    estradas e o proprio System Map.

    Dizer `UNKNOWN` sobre eles seria inventar um buraco que so existe porque eu
    tapei os olhos."""

    def setUp(self):
        self.d = _json(DONOS)

    def test_unknown_nao_e_dado_a_quem_tem_dono_instrumento(self):
        for c in self.d['DETALHE']:
            if c['ESTADO'] == 'UNKNOWN':
                self.assertEqual(
                    c['INSTRUMENTOS_QUE_CITAM'], 0,
                    '%s foi dado por UNKNOWN e ha %d instrumentos a escreve-lo'
                    % (c['CONCEITO'], c['INSTRUMENTOS_QUE_CITAM']))

    def test_dono_instrumento_diz_que_nao_e_buraco(self):
        for c in self.d['DETALHE']:
            if c['ESTADO'] == 'DONO_E_INSTRUMENTO':
                self.assertIn('NAO e um buraco', c['NOTA'])


class ODonoDuplicadoEOAchadoQueImporta(unittest.TestCase):
    """Onde dois ficheiros escrevem o mesmo conceito, a telemetria pode divergir
    sem ninguem dar por isso. Nao e erro por si — pode ser dono canonico mais
    legado — mas tem de estar a vista, com os nomes."""

    def setUp(self):
        self.d = _json(DONOS)

    def test_duplicado_lista_todos_os_que_escrevem(self):
        for c in self.d['DETALHE']:
            if c['ESTADO'] == 'DONO_DUPLICADO':
                self.assertGreater(len(c['ESCREVEM']), 1, c['CONCEITO'])

    def test_um_dono_e_exatamente_um(self):
        for c in self.d['DETALHE']:
            if c['ESTADO'] == 'UM_DONO':
                self.assertEqual(len(c['ESCREVEM']), 1, c['CONCEITO'])

    def test_as_leis_estao_escritas(self):
        junto = ' '.join(self.d['LEIS'])
        self.assertIn('OWNER EXISTS != OWNER CONNECTED', junto)
        self.assertIn('ESCREVER != LER', junto)


if __name__ == '__main__':
    unittest.main(verbosity=2)
