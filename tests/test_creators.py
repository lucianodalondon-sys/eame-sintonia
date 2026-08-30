#!/usr/bin/env python3
"""
Provas das SEIS LEIS do mapa de creators.

Não testam "o módulo importa". Testam que os erros que o briefing proíbe são
*impossíveis de cometer em silêncio* — cada teste abaixo corresponde a uma
confusão que custaria uma recomendação errada ao Marketing da ADAMA.

    python3 -m unittest discover -s tests -v
"""
import json, glob, os, sys, unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'scripts'))
import creators as cr                                        # noqa: E402

BASE = cr.BASE


def _base(nome):
    return cr.carregar(nome)


class TestContrato(unittest.TestCase):
    """Campo que some é indistinguível de campo que nunca existiu."""

    def test_registro_vazio_tem_todos_os_campos(self):
        r = cr.registro_vazio()
        self.assertEqual(sorted(r), sorted(cr.CAMPOS_CREATOR))
        self.assertTrue(all(v == cr.NAO_SEI for v in r.values()))

    def test_nenhum_campo_do_contrato_se_repete(self):
        self.assertEqual(len(cr.CAMPOS_CREATOR), len(set(cr.CAMPOS_CREATOR)))
        self.assertEqual(len(cr.CAMPOS_COLABORACAO), len(set(cr.CAMPOS_COLABORACAO)))

    def test_papel_de_sensor_e_ponteiro_nunca_campo_fundido(self):
        """EARLY SIGNAL e CREATOR MAP não podem virar uma ficha só."""
        self.assertIn('SENSOR_ROLE_LINK', cr.CAMPOS_CREATOR)
        for proibido in ('SENSOR_SCORE', 'AUTHORITY_SCORE', 'INFLUENCE_SCORE', 'RANK'):
            self.assertNotIn(proibido, cr.CAMPOS_CREATOR,
                             '%s fundiria os dois papéis ou criaria nota de pessoa' % proibido)


class TestLei1HandleNaoSeInfere(unittest.TestCase):
    """NAME != HANDLE != PROFILE. Medido: /company/adama/ é uma imobiliária romena."""

    def test_handle_sem_fonte_e_recusado(self):
        r = cr.registro_vazio()
        r['NAME'] = 'Fulano de Tal'
        r['INSTAGRAM'] = '@fulano'
        faltas = cr.checar(r)
        self.assertTrue(any('HANDLE_SEM_FONTE' in f for f in faltas), faltas)

    def test_handle_com_fonte_passa(self):
        r = cr.registro_vazio()
        r['NAME'] = 'Fulano de Tal'
        r['INSTAGRAM'] = '@fulano'
        r['SOURCE_URL'] = 'https://exemplo.example/artigo'
        self.assertFalse([f for f in cr.checar(r) if 'HANDLE_SEM_FONTE' in f])

    def test_registro_sem_nome_e_recusado(self):
        self.assertTrue(any('NAME_AUSENTE' in f for f in cr.checar(cr.registro_vazio())))


class TestLei2CulturaSeProva(unittest.TestCase):
    """"É agro" não prova "é olivar"."""

    def test_crop_proved_exige_evidencia(self):
        r = cr.registro_vazio(); r['NAME'] = 'X'
        r['CROP_STATE'] = 'PROVED'; r['CROPS'] = ['OLIVE']
        self.assertTrue(any('CROP_PROVED_SEM_EVIDENCIA' in f for f in cr.checar(r)))

    def test_crop_proved_exige_cultura_declarada(self):
        r = cr.registro_vazio(); r['NAME'] = 'X'
        r['CROP_STATE'] = 'PROVED'; r['CROP_EVIDENCE'] = 'vídeo de colheita'
        self.assertTrue(any('CROP_PROVED_SEM_CULTURA' in f for f in cr.checar(r)))


class TestLei3CreatorNaoEProdutor(unittest.TestCase):
    def test_actual_farmer_proved_exige_evidencia(self):
        r = cr.registro_vazio(); r['NAME'] = 'X'; r['ACTUAL_FARMER'] = 'PROVED'
        self.assertTrue(any('FARMER_PROVED_SEM_EVIDENCIA' in f for f in cr.checar(r)))

    def test_actual_farmer_e_campo_proprio(self):
        self.assertIn('ACTUAL_FARMER', cr.CAMPOS_CREATOR)
        self.assertIn('ACTUAL_FARMER_EVIDENCE', cr.CAMPOS_CREATOR)


class TestLei4MencaoNaoEPatrocinio(unittest.TestCase):
    """A escada só sobe com evidência do degrau."""

    def test_subida_sem_evidencia_e_recusada(self):
        e, motivo = cr.promover_marca('ORGANIC_MENTION', 'PAID_PARTNERSHIP_PROVED',
                                      evidencia=None)
        self.assertEqual(e, 'ORGANIC_MENTION')
        self.assertIn('SUBIDA_RECUSADA', motivo)

    def test_subida_com_evidencia_passa(self):
        e, motivo = cr.promover_marca('ORGANIC_MENTION', 'PAID_PARTNERSHIP_PROVED',
                                      evidencia='post com #ad e URL preservada')
        self.assertEqual(e, 'PAID_PARTNERSHIP_PROVED')

    def test_rebaixar_sempre_permitido(self):
        e, motivo = cr.promover_marca('PAID_PARTNERSHIP_PROVED', 'ORGANIC_MENTION',
                                      evidencia=None)
        self.assertEqual(e, 'ORGANIC_MENTION')

    def test_escada_tem_a_ordem_do_briefing(self):
        self.assertEqual(cr.ESCADA_MARCA.index('ORGANIC_MENTION') + 1,
                         cr.ESCADA_MARCA.index('PRODUCT_USE_OBSERVED'))
        self.assertLess(cr.ESCADA_MARCA.index('BRAND_COLLABORATION_PROVED'),
                        cr.ESCADA_MARCA.index('PAID_PARTNERSHIP_PROVED'))


class TestLei5CategoriaNaoTransfere(unittest.TestCase):
    """Maquinaria não prova defensivo. Empresa de defensivo não é peça de defensivo."""

    def test_maquinaria_nao_prova_crop_protection(self):
        colabs = [{'COUNTRY': 'FR', 'BRAND': 'New Holland', 'BRAND_KIND': 'MACHINERY_COMPANY',
                   'PRODUCT_CATEGORY': 'MACHINERY', 'MESSAGE_KIND': 'PRODUCT_PROMOTION',
                   'RELATIONSHIP_STATE': 'PAID_PARTNERSHIP_PROVED'}]
        v = cr.veredito_crop_protection(colabs, paises=('FR',))
        self.assertEqual(v['FR']['ESTADO'], 'NOT_PROVED')

    def test_empresa_de_defensivo_com_peca_institucional_e_PARTIAL(self):
        colabs = [{'COUNTRY': 'FR', 'BRAND': 'Bayer', 'BRAND_KIND': 'CROP_PROTECTION_COMPANY',
                   'PRODUCT_CATEGORY': 'INSTITUTIONAL_SECTOR', 'MESSAGE_KIND': 'CORPORATE_IMAGE',
                   'RELATIONSHIP_STATE': 'PAID_PARTNERSHIP_PROVED'}]
        v = cr.veredito_crop_protection(colabs, paises=('FR',))
        self.assertEqual(v['FR']['ESTADO'], 'PARTIAL')

    def test_peca_de_produto_fitossanitario_e_PROVED(self):
        colabs = [{'COUNTRY': 'ES', 'BRAND': 'Alguma', 'BRAND_KIND': 'CROP_PROTECTION_COMPANY',
                   'PRODUCT_CATEGORY': 'CROP_PROTECTION', 'MESSAGE_KIND': 'PRODUCT_PROMOTION',
                   'RELATIONSHIP_STATE': 'PAID_PARTNERSHIP_PROVED'}]
        v = cr.veredito_crop_protection(colabs, paises=('ES',))
        self.assertEqual(v['ES']['ESTADO'], 'PROVED')

    def test_nao_testado_nunca_vira_nao_provado(self):
        v = cr.veredito_crop_protection([], paises=('ES', 'IT', 'FR', 'DE'),
                                        testados=('ES', 'IT', 'FR'))
        self.assertEqual(v['DE']['ESTADO'], 'NOT_TESTED')
        self.assertEqual(v['ES']['ESTADO'], 'NOT_PROVED')

    def test_mencao_organica_nao_conta_como_prova(self):
        colabs = [{'COUNTRY': 'IT', 'BRAND': 'Syngenta', 'BRAND_KIND': 'CROP_PROTECTION_COMPANY',
                   'PRODUCT_CATEGORY': 'CROP_PROTECTION', 'MESSAGE_KIND': 'PRODUCT_PROMOTION',
                   'RELATIONSHIP_STATE': 'ORGANIC_MENTION'}]
        self.assertEqual(cr.veredito_crop_protection(colabs, paises=('IT',))['IT']['ESTADO'],
                         'NOT_PROVED')


class TestLei6SemAuthorityScore(unittest.TestCase):
    """Seguidor alto não promove. Relevância é estado derivado, não nota."""

    def _base_ok(self):
        r = cr.registro_vazio()
        r.update({'CREATOR_ID': 'C-1', 'NAME': 'X', 'IDENTITY_STATE': 'PROVED',
                  'INSTAGRAM': '@x', 'SOURCE_URL': 'https://e.example',
                  'CROP_STATE': 'PROVED', 'CROPS': ['OLIVE'],
                  'CROP_EVIDENCE': 'vídeo de colheita', 'ACTIVITY_STATE': 'ACTIVE_RECENT'})
        return r

    def test_relevancia_e_estado_da_lista_fechada(self):
        e, _ = cr.relevancia(self._base_ok())
        self.assertIn(e, cr.RELEVANCIA)

    def test_seguidores_altos_sem_identidade_nao_promovem(self):
        r = self._base_ok()
        r['IDENTITY_STATE'] = cr.NAO_SEI
        r['FOLLOWERS_BY_PLATFORM'] = {'INSTAGRAM': 900000}
        e, porques = cr.relevancia(r)
        self.assertEqual(e, 'RESEARCH_NEEDED')
        self.assertTrue(any('IDENTIDADE_NAO_PROVADA' in p for p in porques))

    def test_cultura_nao_provada_nao_chega_a_activation_ready(self):
        r = self._base_ok()
        r['CROP_STATE'] = 'NOT_PROVED'; r['CROP_EVIDENCE'] = cr.NAO_SEI; r['CROPS'] = cr.NAO_SEI
        e, _ = cr.relevancia(r)
        self.assertEqual(e, 'PROMISING')

    def test_activation_ready_nao_e_autorizacao_de_campanha(self):
        p = cr.pendencias_de_compliance()
        self.assertEqual(p['BASE_AUTORIZA_CAMPANHA'], 'NO')
        for c in cr.COMPLIANCE_PPP:
            self.assertIn(c, p['CHECAGENS_PENDENTES'])

    def test_conflito_com_concorrente_e_informado_nao_apagado(self):
        r = self._base_ok()
        colabs = [{'CREATOR_ID': 'C-1', 'BRAND': 'Bayer',
                   'RELATIONSHIP_STATE': 'PAID_PARTNERSHIP_PROVED'}]
        e, porques = cr.relevancia(r, colaboracoes=colabs)
        self.assertTrue(any('CONFLITO_CONCORRENTE' in p for p in porques))


class TestBaseGravada(unittest.TestCase):
    """O que estiver gravado precisa passar nos mesmos portões."""

    def test_todo_creator_gravado_passa_no_portao(self):
        regs = _base('CREATORS-ES-IT-FR.json')
        if not regs:
            self.skipTest('base ainda não gravada')
        problemas = []
        for r in regs:
            f = cr.checar(r)
            if f:
                problemas.append('%s: %s' % (r.get('CREATOR_ID'), f))
        self.assertFalse(problemas, '\n'.join(problemas))

    def test_creator_id_e_unico(self):
        regs = _base('CREATORS-ES-IT-FR.json')
        if not regs:
            self.skipTest('base ainda não gravada')
        ids = [r.get('CREATOR_ID') for r in regs]
        self.assertEqual(len(ids), len(set(ids)), 'CREATOR_ID duplicado')

    def test_toda_colaboracao_declara_fonte(self):
        colabs = _base('BRAND-COLLABORATIONS-EU.json')
        if not colabs:
            self.skipTest('base ainda não gravada')
        sem = [c.get('COLLAB_ID') for c in colabs
               if not c.get('SOURCE_URL') or c.get('SOURCE_URL') == cr.NAO_SEI]
        self.assertFalse(sem, 'colaboração sem SOURCE_URL: %s' % sem)

    def test_estado_de_relacao_e_da_escada(self):
        colabs = _base('BRAND-COLLABORATIONS-EU.json')
        if not colabs:
            self.skipTest('base ainda não gravada')
        maus = [(c.get('COLLAB_ID'), c.get('RELATIONSHIP_STATE')) for c in colabs
                if c.get('RELATIONSHIP_STATE') not in cr.ESCADA_MARCA]
        self.assertFalse(maus, 'estado fora da escada: %s' % maus)

    def test_categoria_e_da_lista(self):
        colabs = _base('BRAND-COLLABORATIONS-EU.json')
        if not colabs:
            self.skipTest('base ainda não gravada')
        maus = [(c.get('COLLAB_ID'), c.get('PRODUCT_CATEGORY')) for c in colabs
                if c.get('PRODUCT_CATEGORY') not in cr.CATEGORIAS]
        self.assertFalse(maus, 'categoria fora da lista: %s' % maus)


if __name__ == '__main__':
    unittest.main(verbosity=2)
