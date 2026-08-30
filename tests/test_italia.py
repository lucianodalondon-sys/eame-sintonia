#!/usr/bin/env python3
"""Testes da camada italiana. Codificam as LEIS, não só o comportamento."""
import datetime
import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'scripts'))
import italia                      # noqa: E402
import italia_rotulo_parse as rp   # noqa: E402
import italia_colture as ic        # noqa: E402

CSV = os.path.join(ROOT, 'data', 'raw', 'IT', 'PROD_FTS_6_20260824.csv')


def _linha(**kw):
    base = {'num_registrazione': '000001', 'denominazione_prodotto': 'X',
            'ragione_sociale': '', 'indirizzo_sede_amministrativa': '',
            'stato_amministrativo': 'Autorizzato', 'sostanze_attive': '-',
            'data_scadenza_autorizzazione': '-'}
    base.update(kw)
    return base


class TestIdentidadeTitular(unittest.TestCase):
    """A regra que custou o número errado: string de nome NÃO é entidade."""

    def test_entidade_italiana_por_nome_exato(self):
        e, ev = italia.classificar_titular(_linha(ragione_sociale='ADAMA ITALIA S.R.L.'))
        self.assertEqual(e, 'ADAMA_IT_LEGAL_ENTITY')
        self.assertIn('ragione_sociale', ev)

    def test_nucleo_exige_sede_declarada_nao_o_nome(self):
        e, ev = italia.classificar_titular(_linha(
            ragione_sociale='ADAMA AGAN LTD',
            indirizzo_sede_amministrativa='C/O ADAMA ITALIA S.R.L. - VIA ZANICA, 19'))
        self.assertEqual(e, 'ADAMA_GROUP_IT_CORE')
        self.assertIn('sede_amministrativa', ev)

    def test_nome_parecido_sem_sede_nao_entra_no_nucleo(self):
        """MAGAN ITALIA lembra Makhteshim-Agan. Semelhança não é evidência."""
        e, _ = italia.classificar_titular(_linha(
            ragione_sociale='MAGAN ITALIA S.R.L.',
            indirizzo_sede_amministrativa='VIA G. FALCONE, 13'))
        self.assertEqual(e, 'ADAMA_IT_ADJACENT')

    def test_terceiro_nao_vira_adama_por_endereco_parcial(self):
        """Só a via, sem a razão social na sede, não basta."""
        e, _ = italia.classificar_titular(_linha(
            ragione_sociale='OUTRA S.P.A.', indirizzo_sede_amministrativa='VIA ZANICA, 21'))
        self.assertEqual(e, 'OUTRO')


class TestVigencia(unittest.TestCase):
    def test_data_ausente_nao_e_data_passada(self):
        """'-' é NÃO SEI. Tratar ausência como vencido inventaria vencimentos."""
        self.assertIsNone(italia._data('-'))
        self.assertIsNone(italia._data(''))
        self.assertEqual(italia._data('31/07/2027'), datetime.date(2027, 7, 31))

    def test_substancias_ausentes_nao_contam(self):
        self.assertEqual(italia.substancias('-'), [])
        self.assertEqual(italia.substancias('A|B'), ['A', 'B'])
        self.assertEqual(italia.substancias('A|-'), ['A'])

    def test_sem_data_nao_entra_em_vencimento(self):
        rows = [_linha(ragione_sociale='ADAMA ITALIA S.R.L.',
                       data_scadenza_autorizzazione='-')]
        d = italia.inventario_adama(rows, datetime.date(2026, 8, 30))['ADAMA_IT_LEGAL_ENTITY']
        self.assertEqual(d['ACTIVE'], 1)
        self.assertEqual(d['ACTIVE_WITHOUT_EXPIRY_DATE'], 1)
        self.assertEqual(d['EXPIRING_6M'], 0)


class TestRotulo(unittest.TestCase):
    """Alvo vem da FORMA do nome científico, nunca de lista de pragas na cabeça."""

    def test_toponimo_de_fabrica_nao_e_alvo(self):
        t = 'Stabilimento di produzione: ADAMA Makhteshim Ltd - Beer Sheva (Israele)'
        self.assertEqual(rp.alvos(t), [])

    def test_binomio_real_e_alvo(self):
        t = 'Oidio (Erysiphe spp.); Septoria (Septoria tritici)'
        got = {a['SCIENTIFIC_NAME'] for a in rp.alvos(t)}
        self.assertIn('Erysiphe spp.', got)
        self.assertIn('Septoria tritici', got)

    def test_ordem_invertida_tambem_e_alvo(self):
        """`Ostrinia nubilialis (piralide)` — a etichetta usa as DUAS ordens.

        COSAYR 200 SC, o registro de milho mais novo do portfolio, lista os alvos
        so nesta ordem. Com so a ordem vernaculo->binomio, aquele rotulo devolvia
        ZERO alvos, e o vazio parecia ausencia quando era cegueira do parser.
        """
        got = {a['SCIENTIFIC_NAME']: a['ISSUE_VERNACULAR_IT']
               for a in rp.alvos('Ostrinia nubilialis (piralide), Sesamia spp. (sesamia)')}
        self.assertEqual(got.get('Ostrinia nubilialis'), 'piralide')
        self.assertIn('Sesamia spp.', got)

    def test_ordem_invertida_nao_inventa_alvo(self):
        """Parenteses com texto qualquer nao vira alvo so por vir depois de duas palavras."""
        self.assertEqual(rp.alvos('Distribuito da Syngenta Italia (Milano)'), [])

    def test_secao_nao_vira_alvo(self):
        self.assertEqual(rp.alvos('Composizione (Azoxystrobin puro)'), [])

    def test_cultura_e_presenca_de_termo_nao_autorizacao(self):
        c = rp.culturas('Mais: diserbo di post-emergenza')
        self.assertEqual(c['MAIZE']['STATE'], 'CROP_TERM_PRESENT')


class TestContextoDeRotacao(unittest.TestCase):
    """A armadilha que quase publicou 4 herbicidas de beterraba como produtos de milho."""

    def test_clausula_de_sucessao_nao_e_uso(self):
        t = ('AVVERTENZE AGRONOMICHE: In caso di fallimento della coltura: barbabietola '
             'da zucchero puo essere seminata senza attesa; patate e mais possono essere '
             'seminate in seguito ad aratura profonda.')
        c = rp.culturas(t)
        self.assertEqual(c['MAIZE']['STATE'], 'ROTATION_CONTEXT_ONLY')
        self.assertEqual(c['MAIZE']['MENTIONS_USE_CONTEXT'], 0)

    def test_uso_real_continua_sendo_uso(self):
        t = 'Diserbo di post-emergenza del mais: dose 1,5 l/ha.'
        self.assertEqual(rp.culturas(t)['MAIZE']['STATE'], 'CROP_TERM_PRESENT')

    def test_uso_vence_rotacao_quando_ha_os_dois(self):
        t = ('Erbicida per il mais. Dose 1 l/ha. In caso di fallimento della coltura '
             'il mais puo essere seminato dopo 30 giorni.')
        c = rp.culturas(t)
        self.assertEqual(c['MAIZE']['STATE'], 'CROP_TERM_PRESENT')
        self.assertGreaterEqual(c['MAIZE']['MENTIONS_ROTATION_CONTEXT'], 1)


class TestModoDeAcao(unittest.TestCase):
    """O extrator anterior reportava 55% e estava errado. Estes casos sao os reais."""

    def test_codigo_antes_do_esquema(self):
        self.assertEqual(rp.modo_de_acao("Meccanismo d'azione gruppo B (HRAC)"),
                         {'HRAC': ['B']})

    def test_varios_grupos_numa_so_declaracao(self):
        t = "Meccanismi d'azione: gruppo 2 (B), gruppo 27 (F2), gruppo 4 (O) (HRAC)"
        self.assertEqual(rp.modo_de_acao(t), {'HRAC': ['2 (B)', '27 (F2)', '4 (O)']})

    def test_codigo_depois_do_esquema(self):
        t = "MECCANISMO D'AZIONE (HRAC): GRUPPO 5 (C1) E GRUPPO 27 (F2)"
        self.assertEqual(rp.modo_de_acao(t), {'HRAC': ['27 (F2)', '5 (C1)']})

    def test_inicial_do_produto_nao_vira_grupo(self):
        """`TAIFUN MK CL` virava HRAC 'T'. Sem token `gruppo`, nao ha grupo."""
        self.assertEqual(rp.modo_de_acao('(HRAC) TAIFUN MK CL Registrazione n. 1'), {})

    def test_sem_declaracao_devolve_vazio(self):
        self.assertEqual(rp.modo_de_acao('Fungicida per cereali. Dose 1 l/ha.'), {})


class TestColturaHierarquia(unittest.TestCase):
    def test_prova_detecta_nao_aditividade(self):
        """A prova tem de REPROVAR quando pai ≠ soma dos filhos."""
        v = {'C1100': 100.0, 'C1110': 10.0, 'C1120': 20.0}
        r = [x for x in ic.provar_hierarquia(v) if x['PARENT'] == 'C1100'][0]
        self.assertEqual(r['STATE'], 'NOT_ADDITIVE')

    def test_prova_aceita_aditividade(self):
        v = {'C1100': 30.0, 'C1110': 10.0, 'C1120': 20.0}
        r = [x for x in ic.provar_hierarquia(v) if x['PARENT'] == 'C1100'][0]
        self.assertEqual(r['STATE'], 'PROVED')

    def test_commodity_nao_contem_agregado_conhecido(self):
        """C1100 é pai de dois filhos que ESTÃO na lista: não pode estar também."""
        self.assertNotIn('C1100', ic.COMMODITY)
        self.assertIn('C1110', ic.COMMODITY)
        self.assertIn('C1120', ic.COMMODITY)


@unittest.skipUnless(os.path.exists(CSV), 'dataset bruto não versionado')
class TestContraFonteReal(unittest.TestCase):
    def test_censo_reproduz(self):
        c = italia.censo_nacional(italia.carregar(CSV))
        self.assertEqual(c['TOTAL_PRODUCTS'], 17695)
        self.assertEqual(c['CURRENT_AUTHORIZED'], 3712)

    def test_numero_antigo_era_do_grupo_nao_da_entidade(self):
        inv = italia.inventario_adama(italia.carregar(CSV), datetime.date(2026, 8, 30))
        self.assertEqual(inv['ADAMA_GROUP_IT_CORE']['ACTIVE_WITH_FUTURE_EXPIRY'], 155)
        self.assertEqual(inv['ADAMA_IT_LEGAL_ENTITY']['ACTIVE_WITH_FUTURE_EXPIRY'], 77)

    def test_adjacentes_nao_tem_vigente(self):
        """A ambiguidade de MAGAN/MAKHTESHIM HOLLAND é IMATERIAL hoje — e provado."""
        inv = italia.inventario_adama(italia.carregar(CSV), datetime.date(2026, 8, 30))
        self.assertEqual(inv['ADAMA_IT_ADJACENT']['ACTIVE'], 0)


if __name__ == '__main__':
    unittest.main()
