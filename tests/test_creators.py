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
        self.assertEqual(v['FR']['ESTADO'], cr.AUSENTE_NO_CORPUS)

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
        self.assertEqual(v['ES']['ESTADO'], cr.AUSENTE_NO_CORPUS)

    def test_mencao_organica_nao_conta_como_prova(self):
        colabs = [{'COUNTRY': 'IT', 'BRAND': 'Syngenta', 'BRAND_KIND': 'CROP_PROTECTION_COMPANY',
                   'PRODUCT_CATEGORY': 'CROP_PROTECTION', 'MESSAGE_KIND': 'PRODUCT_PROMOTION',
                   'RELATIONSHIP_STATE': 'ORGANIC_MENTION'}]
        self.assertEqual(cr.veredito_crop_protection(colabs, paises=('IT',))['IT']['ESTADO'],
                         cr.AUSENTE_NO_CORPUS)


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
        self.assertNotEqual(e, 'ACTIVATION_READY')
        self.assertTrue(any('IDENTITY_PROVED=FALTA' in p for p in porques))

    def test_cultura_nao_provada_nao_chega_a_activation_ready(self):
        r = self._base_ok()
        r['CROP_STATE'] = 'NOT_PROVED'; r['CROP_EVIDENCE'] = cr.NAO_SEI; r['CROPS'] = cr.NAO_SEI
        e, _ = cr.relevancia(r)
        self.assertNotEqual(e, 'ACTIVATION_READY')

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


class TestCarregarConheceOsArtefatos(unittest.TestCase):
    """Uma chave de artefato desconhecida fez uma fase PAGA rodar com zero itens.

    Falhou fechado — não produziu dado errado — mas gastou uma execução para
    descobrir. Este teste existe para que o próximo artefato novo não repita.
    """

    def test_seed_e_lida_por_carregar(self):
        if not os.path.exists(os.path.join(BASE, 'SEED-IT-CANDIDATES.json')):
            self.skipTest('seed ainda não gravada')
        self.assertTrue(cr.carregar('SEED-IT-CANDIDATES.json'),
                        'carregar() devolveu vazio para a seed — chave do artefato '
                        'não está na lista de carregar()')

    def test_toda_lista_de_artefato_tem_chave_conhecida(self):
        import glob
        for caminho in glob.glob(os.path.join(BASE, '*.json')):
            with open(caminho, encoding='utf-8') as f:
                d = json.load(f)
            if not isinstance(d, dict):
                continue
            listas = [k for k, v in d.items() if isinstance(v, list) and v
                      and isinstance(v[0], dict) and len(v) > 2]
            if not listas:
                continue
            nome = os.path.basename(caminho)
            self.assertTrue(cr.carregar(nome),
                            '%s tem lista %s que carregar() não alcança' % (nome, listas))


class TestCorrecaoSemantica(unittest.TestCase):
    """§0 — ausência observada num corpus não é ausência no mercado.

    A primeira redação desta missão publicou "a faixa está vazia nos três
    países". Isso extrapolava: o corpus medido é pequeno e enviesado pelas
    fontes que alcançamos. O estado passou a carregar o próprio escopo.
    """

    def test_o_estado_nomeia_o_corpus(self):
        self.assertEqual(cr.AUSENTE_NO_CORPUS, 'NOT_OBSERVED_IN_MEASURED_CORPUS')
        self.assertIn('CORPUS', cr.AUSENTE_NO_CORPUS)

    def test_o_veredito_viaja_com_a_ressalva(self):
        v = cr.veredito_crop_protection([], paises=('IT',))
        self.assertIn('ESTE_ESTADO_NAO_SIGNIFICA', v['IT'])
        junto = ' '.join(v['IT']['ESTE_ESTADO_NAO_SIGNIFICA']).lower()
        for proibido in ('ninguém faz', 'white space', 'oportunidade comercial'):
            self.assertIn(proibido, junto)

    def test_o_veredito_declara_o_corpus_medido(self):
        v = cr.veredito_crop_protection([], paises=('IT',))
        self.assertIn('CORPUS_MEDIDO', v['IT'])

    def test_nenhum_artefato_AFIRMA_a_frase_extrapolada(self):
        """A frase que causou a correção não pode voltar como AFIRMAÇÃO.

        O teste é por linha e não por documento, e aceita a frase quando ela
        aparece sendo NEGADA — é assim que a própria correção fica escrita sem
        se autoproibir. Banir a palavra em vez da afirmação tornaria impossível
        documentar o erro, que é justamente o que não queremos perder.
        """
        import glob
        proibidas = ('faixa está vazia', 'faixa vazia', 'white space',
                     'espaço livre', 'ninguém faz', 'vazia nos três países')
        # Marcas de que a linha NEGA a frase em vez de afirmá-la.
        nega = ('≠', 'não ', 'nao ', 'não\u00a0', 'nunca', 'extrapol',
                'correção', 'correcao', 'proibid', 'errado', 'não é', '!=')
        achados = []
        for caminho in glob.glob(os.path.join(ROOT, 'docs', 'creators', '*.md')):
            for n, linha in enumerate(open(caminho, encoding='utf-8'), 1):
                baixa = linha.lower()
                if any(f in baixa for f in proibidas) and not any(x in baixa for x in nega):
                    achados.append('%s:%d %s' % (os.path.basename(caminho), n,
                                                 linha.strip()[:70]))
        self.assertFalse(achados, 'frase extrapolada AFIRMADA: %s' % achados)

class TestTipoDeRelacaoNaoEEscada(unittest.TestCase):
    """§11 — os cinco tipos NÃO são equivalentes e NÃO são degraus."""

    def test_e_conjunto_sem_ordem(self):
        self.assertIsInstance(cr.TIPOS_DE_RELACAO, frozenset)
        self.assertFalse(hasattr(cr.TIPOS_DE_RELACAO, 'index'),
                         'um tipo de relação com índice viraria escada, e '
                         '"patrocinou uma categoria" viraria "ativa produto"')

    def test_os_cinco_existem_e_sao_distintos(self):
        for t in ('BRAND_ECOSYSTEM_SPONSORSHIP', 'BRAND_EVENT_COLLABORATION',
                  'BRAND_COLLABORATION_PROVED', 'PAID_PARTNERSHIP_PROVED',
                  'PRODUCT_ACTIVATION_PROVED'):
            self.assertIn(t, cr.TIPOS_DE_RELACAO)

    def test_forca_e_tipo_sao_campos_diferentes(self):
        self.assertIn('BRAND_RELATIONSHIP_STATE', cr.CAMPOS_CREATOR)
        self.assertIn('BRAND_RELATION_TYPE', cr.CAMPOS_CREATOR)


class TestSeisProvasDeAtivacao(unittest.TestCase):
    """§10 — marca e seguidores NÃO são requisito de ACTIVATION_READY."""

    def _pronto(self):
        r = cr.registro_vazio()
        r.update({'CREATOR_ID': 'A-1', 'NAME': 'X', 'IDENTITY_STATE': 'PROVED',
                  'COUNTRY': 'ES', 'CROP_STATE': 'PROVED', 'CROPS': ['OLIVE'],
                  'CROP_EVIDENCE': 'vídeo de poda', 'OLIVE_GROWING_RELEVANCE': 'PROVED',
                  'CREATOR_TYPE': 'FARMER_CREATOR', 'ACTIVITY_STATE': 'ACTIVE_RECENT',
                  'INSTAGRAM': '@x', 'SOURCE_URL': 'https://e.example'})
        return r

    def test_pronto_sem_nenhuma_marca_no_historico(self):
        r = self._pronto()
        self.assertEqual(r['BRAND_RELATIONSHIP_STATE'], cr.NAO_SEI)
        self.assertEqual(cr.relevancia(r)[0], 'ACTIVATION_READY')

    def test_pronto_sem_nenhum_seguidor_declarado(self):
        r = self._pronto()
        self.assertEqual(r['FOLLOWERS_BY_PLATFORM'], cr.NAO_SEI)
        self.assertEqual(cr.relevancia(r)[0], 'ACTIVATION_READY')

    def test_sem_atividade_recente_nao_esta_pronto(self):
        r = self._pronto(); r['ACTIVITY_STATE'] = 'NOT_MEASURED'
        self.assertNotEqual(cr.relevancia(r)[0], 'ACTIVATION_READY')

    def test_as_seis_provas_sao_reportadas_uma_a_uma(self):
        p = cr.provas_de_ativacao(self._pronto())
        for prova in cr.PROVAS_DE_ATIVACAO:
            self.assertIn(prova, p)

    def test_marca_e_seguidores_nao_sao_prova(self):
        junto = ' '.join(cr.PROVAS_DE_ATIVACAO)
        self.assertNotIn('BRAND', junto)
        self.assertNotIn('FOLLOWER', junto)


class TestQuatroPapeis(unittest.TestCase):
    """§14 — quatro papéis, quatro campos, nenhum herdando do outro."""

    def test_os_quatro_campos_existem(self):
        for c in ('ACTIVATION_CREATOR', 'TECHNICAL_SENSOR_CANDIDATE',
                  'FIELD_VOICE_SOURCE', 'FARMER_CREATOR_ROLE'):
            self.assertIn(c, cr.CAMPOS_CREATOR)

    def test_creator_nao_vira_sensor_por_omissao(self):
        r = cr.registro_vazio()
        r.update({'NAME': 'X', 'ACTIVATION_CREATOR': 'YES'})
        self.assertEqual(r['TECHNICAL_SENSOR_CANDIDATE'], cr.NAO_SEI,
                         'marcar creator não pode preencher o papel de sensor')


class TestFitParaAdama(unittest.TestCase):
    """A função sumiu numa reescrita e nada acusou — porque nada a testava.

    O sintoma apareceu só quando outro script a chamou, três commits depois.
    Estes testes existem para que a próxima remoção acidental falhe aqui.
    """

    def _reg(self, **kw):
        r = cr.registro_vazio()
        r.update({'NAME': 'X', 'CREATOR_TYPE': 'FARMER_CREATOR',
                  'CROP_STATE': 'PROVED', 'AUDIENCE_TYPE': 'NOT_KNOWN'})
        r.update(kw)
        return r

    def test_a_funcao_existe_e_devolve_par(self):
        fit, porque = cr.fit_para_adama(self._reg())
        self.assertIn(fit, cr.FIT_ADAMA)
        self.assertTrue(porque)

    def test_audiencia_de_consumidor_nunca_e_fit_alto(self):
        for aud in ('WINE_CONSUMERS', 'FOOD_CONSUMERS', 'GENERAL_PUBLIC'):
            fit, _ = cr.fit_para_adama(self._reg(AUDIENCE_TYPE=aud))
            self.assertEqual(fit, 'LOW', 'audiência %s não pode dar fit alto' % aud)

    def test_midia_de_vinho_nunca_e_fit_alto(self):
        fit, _ = cr.fit_para_adama(self._reg(CREATOR_TYPE='WINE_MEDIA_CREATOR'))
        self.assertEqual(fit, 'LOW')

    def test_cultura_refutada_derruba_o_fit(self):
        fit, _ = cr.fit_para_adama(self._reg(CROP_STATE='WRONG_ASSIGNMENT'))
        self.assertEqual(fit, 'LOW')

    def test_campo_com_cultura_e_audiencia_provadas_e_alto(self):
        fit, _ = cr.fit_para_adama(self._reg(AUDIENCE_TYPE='FARMERS'))
        self.assertEqual(fit, 'HIGH')


class TestFuncoesPublicasNaoSomem(unittest.TestCase):
    """Guarda de superfície: uma reescrita não pode apagar a API em silêncio."""

    def test_a_superficie_publica_esta_inteira(self):
        for nome in ('registro_vazio', 'checar', 'promover_marca', 'relevancia',
                     'provas_de_ativacao', 'fit_para_adama',
                     'pendencias_de_compliance', 'veredito_crop_protection',
                     'cobertura', 'carregar'):
            self.assertTrue(callable(getattr(cr, nome, None)),
                            '%s sumiu de creators.py' % nome)


class TestCasosOuroDaSeed(unittest.TestCase):
    """§8 — os QUATRO erros que a seed italiana custou, travados contra regressão.

    Cada um prova uma lei diferente, e as três frases que eles sustentam são:

        HANDLE_MATCH  != IDENTITY_MATCH
        ACCOUNT       != PERSON
        DISPLAY_NAME  != LEGAL/PUBLIC IDENTITY

    Estes testes leem a base gravada. Se alguém "arrumar" um registro achando que
    o handle da seed estava certo, o teste cai — que é exatamente o ponto.
    """

    def _ident(self):
        regs = cr.carregar('PRIMARY-IDENTITY-RESOLVED.json')
        if not regs:
            self.skipTest('resolução de identidade ainda não gravada')
        return {r['CREATOR_ID']: r for r in regs}, {r.get('SEED_HANDLE'): r for r in regs}

    # ── caso 1 · o endereço estava errado, a pessoa não
    def test_gomiero_o_handle_da_seed_nao_e_o_real(self):
        _, porseed = self._ident()
        r = porseed.get('@davide_gomiero')
        self.assertIsNotNone(r, 'o caso Gomiero sumiu da base')
        self.assertEqual(r['ORIGIN_ID'], '@gomierofarm')
        self.assertNotEqual(r['ORIGIN_ID'], r['SEED_HANDLE'],
                            'HANDLE_MATCH != IDENTITY_MATCH: o handle da seed não '
                            'pode voltar a ser tratado como o real')
        self.assertEqual(r['SEED_ERROR_CLASS'], 'HANDLE_ERRADO_NA_SEED')

    # ── caso 2 · nome e endereço errados ao mesmo tempo
    def test_leggieri_nome_e_handle_corrigidos(self):
        _, porseed = self._ident()
        r = porseed.get('@evolovers')
        self.assertIsNotNone(r, 'o caso Leggieri sumiu da base')
        self.assertEqual(r['NAME'], 'Leonardo Leggieri',
                         'o nome da seed era "Leggeri" — a grafia corrigida não pode '
                         'regredir')
        self.assertEqual(r['ORIGIN_ID'], '@narduccio_capicchiaro')
        self.assertNotEqual(r['ORIGIN_ID'], '@evolovers.eu',
                            'a conta PESSOAL não é a conta da COMUNIDADE')

    # ── caso 3 · a persona não é a pessoa
    def test_tomy_rohde_e_persona_nao_pessoa(self):
        porid, _ = self._ident()
        r = porid.get('ES-CR-001')
        self.assertIsNotNone(r, 'o caso Tomy Rohde sumiu da base')
        self.assertEqual(r['NAME'], 'Fernando Giraldo',
                         'DISPLAY_NAME != LEGAL/PUBLIC IDENTITY: o NAME precisa ser a '
                         'pessoa, não o alter ego')
        self.assertEqual(r['DISPLAY_NAME'], '@Tomy_Rohde')
        self.assertTrue(any('PERSONA' in str(p).upper() for p in r['WHY_RELEVANT']),
                        'a ficha precisa dizer que o handle é um alter ego — quem '
                        'contrata "Tomy Rohde" contrata Fernando Giraldo')

    # ── caso 4 · a conta é da empresa
    def test_biocampojoyma_e_empresa_nao_pessoa(self):
        porid, _ = self._ident()
        r = porid.get('ES-CR-004')
        self.assertIsNotNone(r, 'o caso Bio Campojoyma sumiu da base')
        self.assertEqual(r['ENTITY_KIND'], 'ORGANIZATION',
                         'ACCOUNT != PERSON: @biocampojoyma é a conta da EMPRESA. '
                         'Marcá-la como PERSON transformaria um acordo B2B com uma '
                         'produtora num contrato de influencer com um produtor.')
        self.assertEqual(r['SEED_ERROR_CLASS'], 'PESSOA_DIFERENTE_DE_EMPRESA')

    # ── a lei geral que os quatro sustentam
    def test_toda_correcao_de_handle_fica_rastreavel(self):
        regs = cr.carregar('PRIMARY-IDENTITY-RESOLVED.json')
        if not regs:
            self.skipTest('base não gravada')
        for r in regs:
            self.assertIn('SEED_HANDLE', r, '%s perdeu o handle de origem' % r['NAME'])
            self.assertIn('SEED_ERROR_CLASS', r,
                          '%s perdeu a classe do erro — sem ela a correção vira '
                          'silenciosa' % r['NAME'])


class TestPendenciasSaoAcionaveis(unittest.TestCase):
    """§11 — PROMISING precisa dizer QUAL requisito falta."""

    def test_cada_prova_tem_um_codigo_de_pendencia(self):
        for prova in cr.PROVAS_DE_ATIVACAO:
            self.assertIn(prova, cr.MOTIVO_PENDENTE,
                          '%s não tem código MISSING_* — o Marketing veria '
                          '"PROMISING" sem saber o que buscar' % prova)

    def test_promising_carrega_o_motivo(self):
        r = cr.registro_vazio()
        r.update({'NAME': 'X', 'IDENTITY_STATE': 'PROVED', 'COUNTRY': 'ES',
                  'CREATOR_TYPE': 'FARMER_CREATOR', 'INSTAGRAM': '@x',
                  'SOURCE_URL': 'https://e.example'})
        estado, porques = cr.relevancia(r)
        self.assertEqual(estado, 'PROMISING')
        junto = ' '.join(porques)
        self.assertIn('MISSING_CROP_PROOF', junto)
        self.assertIn('MISSING_RECENT_ACTIVITY', junto)

    def test_regiao_e_contato_ausentes_aparecem(self):
        pend = cr.pendencias(cr.registro_vazio())
        self.assertIn(cr.MISSING_REGIAO, pend)
        self.assertIn(cr.MISSING_CONTATO, pend)


class TestContaDeEmpresaNaoEPessoa(unittest.TestCase):
    """§0 — `ACCOUNT_OF_FARM_COMPANY != PERSON_CREATOR`.

    Nasceu de um erro de CONTAGEM, não de dado: `@biocampojoyma` estava
    corretamente medido como conta de empresa e mesmo assim entrou numa frase
    como "três produtores reais". O dado estava certo; a soma, errada.
    """

    def test_o_campo_existe_e_e_de_lista_fechada(self):
        self.assertIn('ACTIVATION_ENTITY_TYPE', cr.CAMPOS_CREATOR)
        for v in ('PERSON_CREATOR', 'FARM_BUSINESS', 'FARMER_FAMILY_ACCOUNT',
                  'MEDIA_ACCOUNT', 'ORGANIZATION'):
            self.assertIn(v, cr.ENTIDADES_DE_ATIVACAO)

    def test_conta_de_empresa_nao_e_pessoa_creator(self):
        r = cr.registro_vazio()
        r['ACTIVATION_ENTITY_TYPE'] = 'FARM_BUSINESS'
        self.assertFalse(cr.e_pessoa_creator(r))
        r['ACTIVATION_ENTITY_TYPE'] = 'PERSON_CREATOR'
        self.assertTrue(cr.e_pessoa_creator(r))

    def test_biocampojoyma_continua_empresa(self):
        regs = cr.carregar('PRIMARY-IDENTITY-RESOLVED.json')
        if not regs:
            self.skipTest('base não gravada')
        r = {x['CREATOR_ID']: x for x in regs}.get('ES-CR-004')
        self.assertIsNotNone(r)
        self.assertEqual(r['ACTIVATION_ENTITY_TYPE'], 'FARM_BUSINESS',
                         'a conta da Bio Campojoyma não pode voltar a ser contada '
                         'como creator-pessoa')

    def test_as_duas_listas_nao_se_misturam(self):
        import json as _j
        caminho = os.path.join(BASE, 'WHO-COULD-MARKETING-CALL.json')
        if not os.path.exists(caminho):
            self.skipTest('fichas não geradas')
        with open(caminho, encoding='utf-8') as f:
            d = _j.load(f)
        pessoas = {x['HANDLE'] for x in d.get('PERSON_CREATORS_ACTIVATION_READY', [])}
        negocios = {x['HANDLE'] for x in d.get('FARM_BUSINESS_PARTNERS_READY', [])}
        self.assertFalse(pessoas & negocios,
                         'um handle não pode estar nas duas listas: são relações '
                         'comerciais diferentes')


class TestProvaDeCulturaNaoAfrouxa(unittest.TestCase):
    """§2 — o que a régua recusa a aceitar como prova."""

    def test_menção_unica_nao_prova(self):
        r = cr.registro_vazio()
        r.update({'NAME': 'X', 'IDENTITY_STATE': 'PROVED', 'COUNTRY': 'ES',
                  'CREATOR_TYPE': 'FARMER_CREATOR', 'ACTIVITY_STATE': 'ACTIVE_RECENT',
                  'INSTAGRAM': '@x', 'SOURCE_URL': 'https://e.example',
                  'CROP_STATE': 'PARTIAL'})
        self.assertFalse(cr.provas_de_ativacao(r)['CROP_FIT_PROVED'],
                         'PARTIAL é menção única — "falar uma vez da cultura" está '
                         'na lista fechada do que NÃO prova')
        self.assertNotEqual(cr.relevancia(r)[0], 'ACTIVATION_READY')

    def test_as_quatro_classes_de_prova_existem(self):
        for c in ('A_OWN_CROP_DECLARED', 'B_RECURRING_PROFESSIONAL_WORK',
                  'C_RECURRING_FIELD_CONTENT', 'D_FARM_PRODUCTION_PROVED'):
            self.assertIn(c, cr.CLASSES_DE_PROVA_DE_CULTURA)

    def test_a_lista_do_que_nao_prova_esta_escrita(self):
        junto = ' '.join(cr.NAO_PROVA_CULTURA)
        for x in ('hashtag', 'evento', 'repost', 'uma vez', 'prêmio'):
            self.assertIn(x, junto)

    def test_classe_de_prova_invalida_e_recusada(self):
        r = cr.registro_vazio()
        r.update({'NAME': 'X', 'CROP_PROOF_TYPE': 'E_INVENTADA'})
        self.assertTrue(any('CROP_PROOF_TYPE_INVALIDO' in f for f in cr.checar(r)))


class TestMatcherDeCulturaNaoCasaSubstring(unittest.TestCase):
    """A primeira versão casava por substring e produziu falsos positivos.

    Medidos ao ler o resultado com desconfiança: 'riz' dentro de nariz/matriz,
    'mais' (português, de um perfil de Évora) lido como milho italiano. O
    resultado da rodada caiu de 8 PROVED para 2 depois da correção — seis dos
    oito eram falsos.
    """

    def _matcher(self):
        import importlib.util
        caminho = os.path.join(ROOT, 'scripts', 'creator_coleta.py')
        spec = importlib.util.spec_from_file_location('_cc', caminho)
        mod = importlib.util.module_from_spec(spec)
        try:
            spec.loader.exec_module(mod)
        except SystemExit:
            pass
        except Exception:                                    # noqa: BLE001
            self.skipTest('creator_coleta não importável neste ambiente')
        return mod._cultura_no_texto

    def test_nariz_e_matriz_nao_sao_arroz(self):
        f = self._matcher()
        self.assertEqual({}, f('tenho o nariz frio e a matriz cheia'))

    def test_mais_portugues_nao_e_milho(self):
        f = self._matcher()
        self.assertEqual({}, f('quero mais novidades para o campo'))

    def test_termos_reais_continuam_casando(self):
        f = self._matcher()
        self.assertIn('MAIZE', f('sembrando maiz esta semana'))
        self.assertIn('RICE', f('la cosecha de arroz'))
        self.assertIn('OLIVE', f('hoy en el olivar'))
