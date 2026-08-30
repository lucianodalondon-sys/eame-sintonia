#!/usr/bin/env python3
"""Testes da camada italiana. Codificam as LEIS, não só o comportamento."""
import datetime
import json
import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'scripts'))
import italia                      # noqa: E402
import italia_rotulo_parse as rp   # noqa: E402
import italia_colture as ic        # noqa: E402
import italia_istat as ii2         # noqa: E402
import italia_cobertura_campo      # noqa: E402,F401
import italia_vies_de_painel       # noqa: E402,F401
import italia_trigo_duro           # noqa: E402,F401
import italia_camada_op            # noqa: E402,F401
import italia_tabela_dose as td    # noqa: E402

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


class TestCid2Bytes(unittest.TestCase):
    """O CID de 2 bytes deslocado — o que destrancou os decretos regionais.

    Enganou por um bom tempo porque o terminal desenha `\\x00` como espaco: o texto
    PARECIA separado por espacos e o corretor de espacos nao casava nada.
    """

    def test_decodifica_par_nul_mais_deslocamento(self):
        bruto = 'OGGETTO' + ''.join('\x00' + chr(ord(c) - 29)
                                    for c in 'Misure di lotta')
        novo, mudou = rp._decodificar_cid2(bruto)
        self.assertTrue(mudou)
        self.assertIn('Misure di lotta', novo)

    def test_apostrofo_e_mapeado_antes_do_deslocamento(self):
        """0xB6 e o glifo do apostrofo: somar 29 antes o transformaria em 'O-acento'."""
        bruto = ''.join('\x00' + c for c in [chr(ord('l') - 29), '\xb6',
                                             chr(ord('a') - 29), chr(ord('n') - 29),
                                             chr(ord('n') - 29), chr(ord('o') - 29)])
        novo, _ = rp._decodificar_cid2(bruto)
        self.assertIn("l'anno", novo)

    def test_texto_sem_nul_fica_intacto(self):
        t = 'Misure di lotta obbligatoria'
        self.assertEqual(rp._decodificar_cid2(t), (t, False))

    def test_decodificacao_implausivel_e_recusada(self):
        """Decodificar e conferir: lixo decodificado preserva o bruto."""
        bruto = '\x00\xf0\x00\xf1\x00\xf2\x00\xf3'
        novo, mudou = rp._decodificar_cid2(bruto)
        self.assertFalse(mudou)


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


class TestNutsVintage(unittest.TestCase):
    """A armadilha silenciosa: ISTAT publica em NUTS 2006, Eurostat em NUTS 2021."""

    def test_veneto_e_emilia_sao_remapeados(self):
        self.assertEqual(ii2.canonico('ITD3'), 'ITH3')   # Veneto
        self.assertEqual(ii2.canonico('ITD5'), 'ITH5')   # Emilia-Romagna
        self.assertEqual(ii2.canonico('ITE1'), 'ITI1')   # Toscana

    def test_codigo_ja_corrente_passa_direto(self):
        self.assertEqual(ii2.canonico('ITC4'), 'ITC4')   # Lombardia nao mudou

    def test_todo_destino_e_regiao_conhecida(self):
        """Um mapeamento que aponta para fora da tabela apagaria a regiao de novo."""
        for destino in ii2.NUTS2006_PARA_2021.values():
            self.assertIn(destino, ii2.REGIOES)

    def test_o_mapa_cobre_o_nordeste_e_o_centro(self):
        """Sao ITD* e ITE* que somem: exatamente Veneto e Emilia-Romagna."""
        origens = set(ii2.NUTS2006_PARA_2021)
        self.assertTrue(all(o.startswith(('ITD', 'ITE')) for o in origens))
        self.assertEqual(len(origens), 9)


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


class TestTabelaDeDose(unittest.TestCase):
    """A tabela e onde a autorizacao por cultura mora. Fora dela, nao."""

    LEX = {'Cercospora', 'Diabrotica', 'Peronospora', 'Erysiphe'}

    def test_alvo_com_genero_fora_do_verificador_nao_entra(self):
        """`Trisulfuron metile` e substancia ativa; `Portare quindi` e verbo."""
        t = ('Coltura Patogeno Dose Barbabietola da zucchero Trisulfuron metile '
             'Portare quindi 0,5 l/ha')
        self.assertEqual([], td.linhas_de_uso(t, self.LEX))

    def test_alvo_verificado_entra_com_a_cultura(self):
        t = ('Coltura Patogeno Dose Barbabietola da zucchero '
             'Cercosporiosi (Cercospora beticola) 0,75 l/ha')
        r = td.linhas_de_uso(t, self.LEX)
        self.assertEqual(1, len(r))
        self.assertEqual('SUGARBEET', r[0]['CROP'])
        self.assertIn('Cercospora beticola', r[0]['TARGETS'])
        self.assertEqual('CROP_TARGET_DOSE', r[0]['ROW_STATE'])

    def test_preposicao_italiana_nao_e_epiteto(self):
        """`Peronospora` esta no EPPO, mas "Peronospora della vite" nao e binomio."""
        t = 'Coltura Patogeno Dose Vite Peronospora della vite 1 l/ha'
        r = td.linhas_de_uso(t, self.LEX)
        self.assertEqual([], [x for x in r if any('della' in a for a in x['TARGETS'])])

    def test_sem_cabecalho_de_tabela_nao_ha_linha(self):
        """O mesmo texto FORA da tabela nao pode virar uso autorizado."""
        t = 'In caso di fallimento della coltura, mais Diabrotica virgifera 1 l/ha'
        self.assertEqual([], td.linhas_de_uso(t, self.LEX))

    def test_dedupe_e_estrutural(self):
        t = ('Coltura Patogeno Dose Mais Diabrotica virgifera 1 l/ha '
             'Mais Diabrotica virgifera 1 l/ha')
        r = td.linhas_de_uso(t, self.LEX)
        self.assertEqual(1, len(r))

    def test_lexico_e_externo_e_nao_auto_derivado(self):
        """Se o verificador voltar a sair dos proprios rotulos, o vernaculo volta."""
        self.assertIn('eppo-dictionary', td.EPPO_DICT)


class TestCoberturaDeCampo(unittest.TestCase):
    """A inversao entre onde o sinal esta e onde a cultura esta."""

    @classmethod
    def setUpClass(cls):
        import italia_cobertura_campo as cc
        cls.cc = cc
        cls.linhas = cc.linhas()

    def test_nao_medido_nunca_conta_como_ausencia(self):
        """NOT_MEASURED e NOT_OBTAINED ficam fora da conta: senao viram zero."""
        d = self.cc.inversao(self.linhas, 'Milho gr\u00e3o')
        self.assertNotIn('Piemonte', d['REGIONS_NOT_PUBLISHING'])
        self.assertNotIn('Piemonte', d['REGIONS_PUBLISHING'])

    def test_toda_linha_declara_a_rota_tentada_ou_e_nao_medida(self):
        for l in self.linhas:
            if l['BULLETINS_2026_MEASURED'] is not None:
                self.assertTrue(l['ROUTE_TRIED'], l['REGION'])

    def test_existe_e_nao_lido_fica_fora_dos_dois_lados(self):
        """Boletim que EXISTE e nao foi lido nao conta como cobertura nem como ausencia.

        O Veneto nao publica milho pela rota do servico fitossanitario, mas a AVISP
        publica um boletim de colture erbacee com edicoes de piralide. Conta-lo como
        "sem sinal" repetiria, com outro nome, o erro do FVG.
        """
        d = self.cc.inversao(self.linhas, 'Milho gr\u00e3o')
        self.assertIn('Veneto', d['REGIONS_BULLETIN_EXISTS_NOT_READ'])
        self.assertNotIn('Veneto', d['REGIONS_NOT_PUBLISHING'])
        self.assertNotIn('Veneto', d['REGIONS_PUBLISHING'])
        self.assertGreater(d['PCT_NATIONAL_EXISTS_NOT_READ'], 0)

    def test_edicao_lida_nao_promove_a_regiao_a_coberta(self):
        """Ler edicoes da serie nao vira cobertura enquanto nao houver indice.

        Duas edicoes da serie da AVISP foram lidas pelo endpoint de download por ID
        (micotossine nel mais; nottue). Isso prova que a serie existe e trata de milho.
        NAO diz quantas edicoes de 2026 existem. Sem denominador nao ha cobertura, e a
        linha tem de continuar fora dos dois lados. Este teste existe porque a tentacao
        de promover o Veneto justamente por eu ter finalmente lido algo e a forma local
        de COBERTURA ALTA != COBERTURA CORRETA.
        """
        veneto = [l for l in self.linhas
                  if l['REGION'] == 'Veneto' and l['CROP'] == 'Milho grão'][0]
        self.assertTrue(veneto.get('EDITIONS_READ'), 'as edicoes lidas devem ficar no registro')
        self.assertIsNone(veneto['BULLETINS_2026_MEASURED'],
                          'edicao lida nao e serie medida: o denominador continua ausente')
        d = self.cc.inversao(self.linhas, 'Milho grão')
        self.assertNotIn('Veneto', d['REGIONS_PUBLISHING'])

    def test_testemunho_de_leitura_confessa_que_o_bruto_nao_foi_preservado(self):
        """Resumo de PDF lido em sessao nao e evidencia: tem de se declarar NOT_PRESERVED.

        Os dois PDFs da AVISP foram lidos e nunca gravados em data/raw. Se a linha
        carrega o conteudo sem confessar o estado do bruto, ela passa a parecer
        evidencia re-verificavel — e nao e.
        """
        veneto = [l for l in self.linhas
                  if l['REGION'] == 'Veneto' and l['CROP'] == 'Milho grão'][0]
        self.assertEqual('NOT_PRESERVED', veneto.get('RAW_EVIDENCE_STATE'))
        self.assertTrue(veneto.get('RAW_EVIDENCE_CONFESSION'))

    def test_a_inversao_e_detectada(self):
        for cultura in ('Oliveira', 'Milho gr\u00e3o'):
            self.assertTrue(self.cc.inversao(self.linhas, cultura)['INVERTED'], cultura)

    def test_inversao_falsa_nao_e_reportada(self):
        """Se quem publica for a maior regiao, INVERTED tem de dar False."""
        fake = [
            {'CROP': 'X', 'REGION': 'Grande', 'PCT_NATIONAL': 50.0, 'BULLETINS_2026_MEASURED': 5,
             'ROUTE_TRIED': 'r'},
            {'CROP': 'X', 'REGION': 'Pequena', 'PCT_NATIONAL': 2.0, 'BULLETINS_2026_MEASURED': 0,
             'ROUTE_TRIED': 'r'}]
        self.assertFalse(self.cc.inversao(fake, 'X')['INVERTED'])



PAINEL = os.path.join(ROOT, 'data', 'samples', 'IT-FONTES', 'ITALY-PANEL-BIAS.json')
DURO = os.path.join(ROOT, 'data', 'samples', 'IT-T3-LOTTA',
                    'IT-trigo-duro-sinal-x-portfolio.json')


class TestViesDePainel(unittest.TestCase):
    """Um numero de cobertura nao significa nada sem saber de quantas regioes ele vem.

    Nasceu de uma linha minha que estava certa em aritmetica e errada em sentido:
    "trigo duro - 0,0% de cobertura". O trigo duro e a maior cultura da Italia, e
    76,8% da area que entrou como MEDIDA era uma regiao so, a Puglia, justamente a
    que parou de redigir fitopatologia em 2018.
    """

    @classmethod
    def setUpClass(cls):
        import italia_vies_de_painel as vp
        cls.vp = vp
        a = vp.areas()
        med, painel = vp.medidas_por_cultura()
        cls.linhas = {c: vp.avaliar(c, a[c][0], a[c][1], med[c], painel)
                      for c in med if c in a}

    def test_dependencia_de_uma_regiao_derruba_o_veredito(self):
        """Cobertura apoiada numa regiao so e amostra de tamanho um, nao cobertura."""
        for crop in ('DURUM_WHEAT', 'OLIVE'):
            v = self.linhas[crop]
            with self.subTest(crop=crop):
                self.assertGreaterEqual(v['SINGLE_REGION_DEPENDENCE_PCT'],
                                        self.vp.LIMIAR_DEPENDENCIA_PCT)
                self.assertEqual('UNMEASURED_NOT_ZERO', v['VERDICT'],
                                 'dependencia alta tem de derrubar o veredito mesmo '
                                 'com painel aparentemente grande')

    def test_nunca_perguntada_nao_se_confunde_com_rota_falhada(self):
        """NOT_ASKED != NOT_FOUND. Colapsar os dois e o erro que este arquivo denuncia.

        A Sicilia tem FIELD_STATE = NOT_MEASURED: nunca foi interrogada para trigo duro.
        O Piemonte tem NOT_OBTAINED: foi interrogado e a bacheca em JavaScript nao
        respondeu. Sao trabalhos diferentes e nao podem cair no mesmo balde.
        """
        d = self.linhas['DURUM_WHEAT']
        self.assertIn('Sicilia', [x['REGION'] for x in d['LARGEST_REGIONS_NEVER_ASKED']])
        self.assertNotIn('Sicilia',
                         [x['REGION'] for x in d['REGIONS_ASKED_ROUTE_DID_NOT_ANSWER']])
        m = self.linhas['MAIZE']
        self.assertIn('Piemonte',
                      [x['REGION'] for x in m['REGIONS_ASKED_ROUTE_DID_NOT_ANSWER']])
        self.assertNotIn('Piemonte',
                         [x['REGION'] for x in m['LARGEST_REGIONS_NEVER_ASKED']])

    def test_estar_no_painel_nao_e_ter_sido_perguntado(self):
        """A Sicilia e linha da matriz e mesmo assim conta como nunca perguntada."""
        _, painel = self.vp.medidas_por_cultura()
        self.assertIn('Sicilia', painel, 'a Sicilia e linha da matriz')
        self.assertEqual('NOT_MEASURED', painel['Sicilia'])

    def test_regiao_que_nao_planta_a_cultura_nao_testemunha(self):
        """O FVG entrou como 'medido sem sinal' para trigo duro com 0,0 mil ha.

        Nao distorce a aritmetica (area zero soma zero dos dois lados), mas aparece
        como se tivesse sido interrogado e tivesse respondido 'nao'. E erro de
        categoria, e tem de ficar nomeado como peso morto.
        """
        d = self.linhas['DURUM_WHEAT']
        mortas = [x['REGION'] for x in d['DEAD_WEIGHT_IN_PANEL']]
        self.assertIn('Friuli-Venezia Giulia', mortas)
        self.assertLess(d['PCT_NATIONAL_EFFECTIVELY_INTERROGATED'],
                        d['PCT_NATIONAL_COUNTED_AS_MEASURED'],
                        'a area efetivamente interrogada tem de ser menor que a contada')

    def test_o_tipo_de_lacuna_separa_engenharia_de_painel(self):
        """Dizer QUE trabalho fecha a lacuna, nao so que ela existe.

        No milho as regioes certas ja foram interrogadas e a rota e que falha: e
        engenharia de coleta. No trigo duro nenhuma engenharia resolve, porque as
        regioes grandes nunca foram perguntadas.
        """
        self.assertEqual('ROUTE_ENGINEERING', self.linhas['MAIZE']['GAP_TYPE'])
        self.assertEqual('PANEL_EXPANSION', self.linhas['DURUM_WHEAT']['GAP_TYPE'])

    def test_o_zero_do_trigo_duro_nunca_e_publicado_como_ausencia(self):
        """A linha que originou o arquivo nao pode voltar a ser lida como ausencia."""
        d = self.linhas['DURUM_WHEAT']
        self.assertEqual('UNMEASURED_NOT_ZERO', d['VERDICT'])
        self.assertGreater(d['PCT_NATIONAL_NEVER_ASKED'], 50.0,
                           'mais de metade do trigo duro italiano nunca foi perguntado')


class TestTrigoDuro(unittest.TestCase):
    """A maior cultura da Italia: o sinal existe, o portfolio nomeado nao responde a ele."""

    @classmethod
    def setUpClass(cls):
        import italia_trigo_duro as tdu
        cls.tdu = tdu

    def test_substancia_decide_a_classe_antes_do_alvo_extraido(self):
        """AUSENCIA DE EXTRACAO NAO E AUSENCIA DE CLASSE.

        TOPIK 80 EC, VIP 80 EC e CELIO 80 EC sao clodinafop — herbicidas inequivocos —
        e o parser nao tirou alvo daqueles PDFs. Classificar pelo genero botanico do
        alvo os jogava em OUTRO, e 13 herbicidas viravam 10 mais 3 desconhecidos.
        """
        p = {'ACTIVE_SUBSTANCE': 'CLODINAFOP|CLOQUINTOCET MEXYL', 'ISSUES_FROM_SOURCE': []}
        self.assertEqual('HERBICIDA', self.tdu.classificar(p))

    def test_tratamento_de_semente_nao_e_fungicida_foliar(self):
        """SEEDRON tem tebuconazole E fludioxonil. A fusariose dele e a da SEMENTE.

        Deixa-lo cair em FUNGICIDA_FOLIAR faria parecer que existe resposta foliar de
        espiga nomeada para grano duro. Nao existe.
        """
        p = {'ACTIVE_SUBSTANCE': 'FLUDIOXONIL|TEBUCONAZOLE', 'ISSUES_FROM_SOURCE': []}
        self.assertEqual('TRATAMENTO_SEMENTE', self.tdu.classificar(p))

    def test_foliar_de_cereal_e_reconhecido(self):
        p = {'ACTIVE_SUBSTANCE': 'AZOXYSTROBIN|PROTHIOCONAZOLE', 'ISSUES_FROM_SOURCE': []}
        self.assertEqual('FUNGICIDA_FOLIAR', self.tdu.classificar(p))

    def test_a_pergunta_aberta_continua_aberta(self):
        """O artefato NAO pode afirmar lacuna: depende de "frumento" cobrir grano duro.

        Se cobre, nao ha lacuna nenhuma e o desencontro e artefato de redacao de rotulo.
        Nao e extraivel do texto do rotulo, entao o estado tem de continuar NAO SEI.
        CROP_TERM != AUTHORIZED_CROP.
        """
        d = json.load(open(DURO, encoding='utf-8'))
        self.assertEqual('NÃO SEI', d['THE_OPEN_QUESTION']['STATE'])
        self.assertEqual('CROP_TERM ≠ AUTHORIZED_CROP', d['THE_OPEN_QUESTION']['LAW'])
        texto = json.dumps(d, ensure_ascii=False).lower()
        for proibido in ('market share', 'quota di mercato', 'revenue', 'roi realized'):
            self.assertNotIn(proibido, texto)

    def test_a_pagina_rolante_nao_vira_serie_contada(self):
        """Mesma lei do Veneto, por motivo diferente: la faltava conteudo, aqui indice."""
        d = json.load(open(DURO, encoding='utf-8'))
        self.assertEqual('ROLLING_CURRENT_ISSUE', d['FIELD_SIGNAL']['PAGE_KIND'])
        self.assertNotIn('BULLETINS_2026_COUNT', d['FIELD_SIGNAL'])

    def test_o_sinal_de_campo_de_trigo_duro_deixou_de_ser_zero(self):
        """Duas provincias da Toscana nomeiam grano duro separado do tenero."""
        d = json.load(open(DURO, encoding='utf-8'))
        com = [x for x in d['FIELD_SIGNAL']['PROVINCES_PROBED']
               if x['DURUM_NAMED_SEPARATELY']]
        self.assertGreaterEqual(len(com), 2)
        self.assertIn('Fusariosi', d['FIELD_SIGNAL']['DISEASES_NAMED'])

    def test_a_toscana_nao_e_apresentada_como_o_pais(self):
        """3,7% da area. Puglia, Sicilia e Basilicata continuam sem sonda."""
        d = json.load(open(DURO, encoding='utf-8'))
        junto = ' '.join(d['WHAT_THIS_DOES_NOT_PROVE'])
        for r in ('Puglia', 'Sicília', 'Basilicata'):
            self.assertIn(r, junto)



class TestCamadaOP(unittest.TestCase):
    """SOURCE_LAYER != SIGNAL_ABSENCE — o erro de painel um nivel acima.

    Medir a camada estatal e concluir "nao ha sinal" e o erro do trigo duro repetido
    com outro eixo: la eu perguntei as regioes erradas, aqui a INSTITUICAO errada
    dentro da regiao certa.
    """

    @classmethod
    def setUpClass(cls):
        import italia_camada_op as op
        cls.fs = {f['ORG']: f for f in op.fontes()}

    def test_conteudo_nao_lido_nao_vira_cobertura(self):
        """A APOL prova EXISTENCIA por indice de busca; o conteudo devolve 503."""
        apol = self.fs['APOL']
        self.assertEqual('EXISTS_ROUTE_NOT_READABLE', apol['STATE'])
        self.assertTrue(apol['EXISTENCE_EVIDENCE'])
        self.assertTrue(apol['ROUTE_FAILURE_IS_NOT_ABSENCE'])

    def test_arquivo_legivel_e_medicao_mesmo_estando_velho(self):
        """Assoproli Bari respondeu: 10/06/2024 e MEDIDO, nao e falha de rota."""
        a = self.fs['Assoproli Bari']
        self.assertEqual('ARCHIVE_READ_BUT_STALE', a['STATE'])
        self.assertEqual('10/06/2024', a['MOST_RECENT'])

    def test_a_correcao_da_puglia_nao_derruba_a_inversao(self):
        """A inversao sobrevive como comparacao entre SERVICOS REGIONAIS.

        O que morre e a leitura "na Puglia nao ha sinal de olivo". Se este teste
        cair, alguem transformou a correcao em retratacao — e ela nao e.
        """
        import italia_camada_op as op
        d = json.load(open(os.path.join(ROOT, 'data', 'samples', 'IT-FONTES',
                                        'ITALY-OP-FIELD-LAYER.json'), encoding='utf-8'))
        c = d['CORRECTION_TO_MY_OWN_FINDING']
        self.assertIn('inversão', c['WHAT_SURVIVES'])
        self.assertIn('não foi lido', c['WHAT_THIS_STILL_DOES_NOT_LICENSE'])
        import italia_cobertura_campo as cc
        inv = cc.inversao(cc.linhas(), 'Oliveira')
        self.assertTrue(inv['INVERTED'], 'a inversao entre servicos regionais continua')
        self.assertIn('Puglia', inv['REGIONS_NOT_PUBLISHING'])

    def test_a_fonte_que_declara_o_proprio_limite_fica_marcada(self):
        """O boletim da Assoprol diz que ainda NAO amostrou infestacao ativa.

        Separar o que mediu do que ainda nao mediu e sinal de qualidade da fonte, e
        perder essa marca faria a leitura parecer mais completa do que e.
        """
        a = self.fs['Assoprol Umbria']
        self.assertEqual('CONTENT_READ', a['STATE'])
        self.assertTrue(a['DECLARES_OWN_LIMIT'])
        self.assertIn('non sono ancora stati effettuati', a['DECLARED_LIMIT_IT'])
        self.assertEqual('71-75', a['BBCH'])

    def test_a_ausencia_da_puglia_e_estabilizada_nao_transitoria(self):
        """A ARIF e hoje a EDITORA e mesmo assim nao redige fitopatologia."""
        arif = self.fs['ARIF Puglia']
        self.assertEqual('PUBLISHES_BUT_NO_PHYTOPATHOLOGY', arif['STATE'])
        self.assertIn('ausência estabilizada', arif['SHARPENED_2026_08_30'])



class TestColetorFalhaSuave(unittest.TestCase):
    """SOURCE FAILURE != ZERO aplicada ao proprio coletor.

    Medido em 30/08/2026: o 429 do OpenAlex escapava de montar() e matava o processo,
    de modo que os recortes ja coletados NAQUELA execucao iam junto. Pior que perder
    trabalho: um recorte que sumiu do artefato e indistinguivel de um recorte que
    devolveu zero pesquisadores.
    """

    def test_estrangulamento_marca_o_recorte_e_nao_derruba_a_coleta(self):
        import urllib.error
        import italia_pesquisadores as ip

        chamadas = []

        def percorrer_falso(q, teto=400):
            chamadas.append(q)
            if len(chamadas) == 1:
                raise urllib.error.HTTPError('u', 429, 'Too Many Requests', {}, None)
            return [], 0

        orig_perc, orig_sleep = ip.percorrer, ip.time.sleep
        ip.percorrer, ip.time.sleep = percorrer_falso, lambda *_: None
        try:
            _, escopos = ip.montar(teto=1)
        finally:
            ip.percorrer, ip.time.sleep = orig_perc, orig_sleep

        self.assertEqual(len(ip.ESCOPOS), len(escopos),
                         'todo recorte tem de aparecer, inclusive o que falhou')
        estrang = [v for v in escopos.values() if v.get('STATE') == 'THROTTLED_NOT_EMPTY']
        self.assertEqual(1, len(estrang))
        self.assertEqual(429, estrang[0]['HTTP'])
        self.assertIsNone(estrang[0]['AUTHORS_WITH_IT_AFFILIATION'],
                          'recorte estrangulado nao pode declarar contagem — nem zero')
        self.assertIn('SOURCE FAILURE', estrang[0]['WHY_NOT_ZERO'])
        self.assertGreater(len(chamadas), 1,
                           'a coleta tem de continuar depois do recorte que falhou')


CASOS = os.path.join(ROOT, 'data', 'samples', 'IT-CASOS', 'ITALY-HERO-CASES-V1.json')


@unittest.skipUnless(os.path.exists(CASOS), 'pacote de casos ainda nao gerado')
class TestRegressoesDeConfiancaFalsa(unittest.TestCase):
    """As cinco confusoes que ja custaram medicao nesta branch.

    Uma regressao que so vive num script nao protege nada: quem editar um artefato
    nao roda o script. Aqui elas passam a reprovar a suite.
    """

    @classmethod
    def setUpClass(cls):
        import ask_sintonia_italia as ask
        cls.regs = {n: (ok, w) for n, ok, w in ask.regressoes()}

    def test_todas_as_regressoes_passam(self):
        falhas = [n for n, (ok, _) in self.regs.items() if not ok]
        self.assertEqual([], falhas, 'regressoes de confianca falsa quebradas: %s' % falhas)

    def test_as_nove_estao_presentes(self):
        """Apagar uma regressao nao pode ser a forma de fazer a suite passar.

        As quatro ultimas nasceram em 30/08/2026, quando eu corrigi tres achados meus
        no mesmo dia: o "0,0% de trigo duro" que media um jornal descontinuado, o
        "frumento" que nao decide grano duro, e a Puglia calada que nao estava calada.
        Elas entram aqui pelo mesmo motivo das cinco primeiras — para que a forma de
        fazer a suite passar nunca seja apagar a licao.
        """
        for nome in ('SYMPTOM_WINDOW != APPLICATION_WINDOW',
                     'READ_FAILURE != NO_LABEL',
                     'AFFILIATION != STUDY_GEOGRAPHY',
                     'REGISTRATION != COMMERCIAL_CATALOG',
                     'GENERIC_TARGET != SPECIFIC_TARGET',
                     'PANEL_MEASURED != COUNTRY_MEASURED',
                     'NOT_ASKED != NOT_FOUND != DOES_NOT_EXIST',
                     'CROP_TERM != AUTHORIZED_CROP',
                     'SOURCE_LAYER != SIGNAL_ABSENCE'):
            self.assertIn(nome, self.regs)

    def test_ask_declara_estado_em_toda_pergunta(self):
        import ask_sintonia_italia as ask
        ask.RESPOSTAS.clear()
        ask.perguntas()
        self.assertGreaterEqual(len(ask.RESPOSTAS), 10)
        validos = {ask.ANSWERABLE, ask.PARTIAL, ask.REFUSE}
        for a in ask.RESPOSTAS:
            self.assertIn(a['STATE'], validos, a['QUESTION'])
            for campo in ('SOURCE', 'WHAT_IS_FACT', 'WHAT_IS_UNKNOWN'):
                self.assertTrue(a[campo], '%s sem %s' % (a['QUESTION'], campo))

    def test_o_ask_recusa_de_verdade(self):
        """Um Ask que responde tudo nao esta medindo nada: a recusa e o ativo."""
        import ask_sintonia_italia as ask
        ask.RESPOSTAS.clear()
        ask.perguntas()
        recusas = [a for a in ask.RESPOSTAS if a['STATE'] == ask.REFUSE]
        self.assertGreaterEqual(len(recusas), 3)


if __name__ == '__main__':
    unittest.main()
