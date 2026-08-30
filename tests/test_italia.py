#!/usr/bin/env python3
"""Testes da camada italiana. Codificam as LEIS, não só o comportamento."""
import datetime
import json
import os
import re
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
import italia_antecipacao          # noqa: E402,F401
import italia_voz_humana           # noqa: E402,F401
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

    def test_a_pergunta_foi_resolvida_ao_contrario_do_padrao(self):
        """O NAO SEI da manha estava certo, e a resposta veio invertida.

        De manha o padrao era convincente: 13 herbicidas, 1 tratamento de semente,
        ZERO foliares. Publicar "a ADAMA tem lacuna na maior cultura da Italia" teria
        sido coerente com tudo que estava medido — e falso. O rotulo diz, na tabela de
        usos autorizados, "Frumento tenero e duro". Este teste guarda a licao, nao so
        o numero: um padrao forte nos dados nao autoriza fechar pergunta aberta.
        """
        d = json.load(open(DURO, encoding='utf-8'))
        q = d['THE_QUESTION_THAT_WAS_OPEN']
        self.assertIn('RESOLVIDA', q['STATE'])
        self.assertIn('PADRÃO FORTE', q['LAW'])
        self.assertIn('CONTRÁRIO', q['WHAT_THIS_TEACHES'])
        texto = json.dumps(d, ensure_ascii=False).lower()
        for proibido in ('market share', 'quota di mercato', 'revenue', 'roi realized'):
            self.assertNotIn(proibido, texto)

    def test_a_convergencia_fecha_nos_tres_eixos(self):
        """CULTURA x PROBLEMA x MOMENTO, com a janela vindo dos DOIS lados."""
        d = json.load(open(DURO, encoding='utf-8'))
        c = d['THE_CONVERGENCE']
        self.assertEqual(['CROP', 'ISSUE', 'TIMING'], c['AXES_THAT_MATCH'])
        self.assertEqual('CROP_IN_AUTHORIZED_USE_TABLE', c['EVIDENCE_CLASS'])
        self.assertIn('fine fioritura', c['TIMING_FROM_LABEL_IT'])
        self.assertIn('fioritura', c['TIMING_FROM_FIELD_IT'])
        self.assertIn('Frumento tenero e duro', c['CROP'])

    def test_o_defeito_do_extrator_fica_registrado_com_o_impacto(self):
        """Corrigir sem registrar o tamanho do erro apaga a licao."""
        d = json.load(open(DURO, encoding='utf-8'))
        m = d['MY_OWN_DEFECT_THAT_THIS_CORRECTS']
        self.assertIn('11 dos 25', m['MEASURED_IMPACT'])
        self.assertIn('79%', m['MEASURED_IMPACT'])
        self.assertTrue(m['GUARDED_BY'])

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



class TestElisaoDeCabeca(unittest.TestCase):
    """A classe de erro que "frumento tenero e duro" revelou, medida e fechada.

    A hipotese de partida — "coordenacao quebra o extrator" — era larga demais. Em
    "mais e sorgo" cada palavra e substantivo de cultura completo e casa sozinha. O que
    quebra e a ELISAO DE CABECA: cultura de substantivo + modificador em que o
    substantivo e omitido na segunda ocorrencia. No vocabulario indexado isso so existe
    no trigo — e custou 12 de 26 rotulos de grano duro (46,2%).
    """

    ELIDIDAS = ('Coltura Frumento tenero e duro (invernale e primaverile)',
                'Grano tenero e duro', 'FRUMENTO TENERO e DURO',
                'frumento duro e tenero', 'grano tenero ed duro',
                'per il frumento tenero, duro, orzo, segale, avena',
                'frumento duro, tenero')

    def test_elisao_registra_as_duas_culturas_em_qualquer_separador(self):
        """Virgula, "e" e "ed". A varredura achou virgula DEPOIS da primeira correcao."""
        for t in self.ELIDIDAS:
            c = rp.culturas(t)
            with self.subTest(texto=t):
                self.assertEqual('CROP_TERM_PRESENT',
                                 c.get('DURUM_WHEAT', {}).get('STATE'))
                self.assertEqual('CROP_TERM_PRESENT',
                                 c.get('COMMON_WHEAT', {}).get('STATE'))

    def test_elisao_por_virgula_e_um_caso_real_e_nao_hipotetico(self):
        """PRESSING 500: "per il frumento tenero, duro, orzo, segale, avena".

        Se so o " e " tivesse sido consertado, 11 casos passariam e este ficaria de pe.
        """
        c = rp.culturas('erbicida selettivo per il frumento tenero, duro, orzo, '
                        'segale, avena')
        self.assertEqual('CROP_TERM_PRESENT', c.get('DURUM_WHEAT', {}).get('STATE'))
        self.assertEqual('CROP_TERM_PRESENT', c.get('BARLEY', {}).get('STATE'))

    def test_nao_inventa_a_cultura_ausente(self):
        """Consertar a elisao nao pode passar a alucinar o modificador que falta."""
        for t, ausente in (('impiego solo su frumento tenero', 'DURUM_WHEAT'),
                           ('impiego su frumento duro', 'COMMON_WHEAT'),
                           ('grano tenero, orzo e segale', 'DURUM_WHEAT'),
                           ('trattamento duro e prolungato del terreno', 'DURUM_WHEAT')):
            with self.subTest(texto=t):
                self.assertIsNone(rp.culturas(t).get(ausente, {}).get('STATE'))

    def test_coordenacao_de_substantivos_plenos_nunca_perdeu_nada(self):
        """A parte da hipotese que a medicao DERRUBOU. Fica no teste para nao voltar."""
        for t, esperadas in (('mais e sorgo', ('MAIZE', 'SORGHUM')),
                             ('patata, erba medica', ('POTATO', 'ALFALFA')),
                             ('girasole, soia, barbabietola',
                              ('SUNFLOWER', 'SOYBEAN', 'SUGARBEET')),
                             ('vite, del pomodoro', ('GRAPEVINE', 'TOMATO'))):
            c = rp.culturas(t)
            for crop in esperadas:
                with self.subTest(texto=t, crop=crop):
                    self.assertEqual('CROP_TERM_PRESENT', c.get(crop, {}).get('STATE'))

    # ------------------------------------------------------------------ MUTACAO
    def test_mutacao_o_teste_reprova_o_extrator_antigo(self):
        """Prova que o teste acima MEDE alguma coisa.

        Um teste de regressao que passaria tambem com o codigo defeituoso nao protege
        nada. Aqui o padrao antigo e reinstalado de proposito e a deteccao TEM de cair.
        """
        orig = rp.CROP_TERMS['DURUM_WHEAT']
        try:
            rp.CROP_TERMS['DURUM_WHEAT'] = [r'grano\s+duro', r'frumento\s+duro']
            for t in ('frumento tenero e duro', 'frumento tenero, duro, orzo'):
                with self.subTest(mutacao='sem elisao', texto=t):
                    self.assertIsNone(rp.culturas(t).get('DURUM_WHEAT', {}).get('STATE'),
                                      'o extrator antigo NAO podia achar isto; se acha, '
                                      'o teste nao esta medindo a correcao')
        finally:
            rp.CROP_TERMS['DURUM_WHEAT'] = orig

    def test_mutacao_separador_so_com_e_deixa_a_virgula_passar(self):
        """A segunda mutacao: a correcao PARCIAL, que foi de fato o meu primeiro erro."""
        orig = rp.CROP_TERMS['DURUM_WHEAT']
        try:
            rp.CROP_TERMS['DURUM_WHEAT'] = [
                r'grano\s+duro', r'frumento\s+duro',
                r'(?:grano|frumento)\s+tenero\s+e\s+duro']
            self.assertEqual('CROP_TERM_PRESENT',
                             rp.culturas('frumento tenero e duro')
                             .get('DURUM_WHEAT', {}).get('STATE'),
                             'a correcao parcial resolvia o " e "')
            self.assertIsNone(rp.culturas('frumento tenero, duro, orzo')
                              .get('DURUM_WHEAT', {}).get('STATE'),
                              'e deixava a virgula de pe — que e o PRESSING 500')
        finally:
            rp.CROP_TERMS['DURUM_WHEAT'] = orig


VARREDURA = os.path.join(ROOT, 'data', 'samples', 'IT-T4-001', 'IT-COORDINATION-SWEEP.json')


@unittest.skipUnless(os.path.exists(VARREDURA), 'varredura ainda nao gerada')
class TestVarreduraDeCoordenacao(unittest.TestCase):
    """O raio de alcance medido, e a honestidade do que NAO apareceu."""

    @classmethod
    def setUpClass(cls):
        cls.d = json.load(open(VARREDURA, encoding='utf-8'))

    def test_a_varredura_leu_o_corpus_inteiro(self):
        self.assertEqual(163, self.d['LABELS_READ'])

    def test_o_raio_de_alcance_esta_medido(self):
        self.assertEqual(12, self.d['LABELS_LOST_BY_OLD_PATTERN'])
        self.assertEqual(14, self.d['DURUM_BEFORE_FIX'])
        self.assertEqual(26, self.d['DURUM_AFTER_FIX'])
        self.assertGreater(self.d['UNDERCOUNT_PCT'], 45.0)

    def test_nada_ficou_por_detectar(self):
        self.assertEqual([], self.d['STILL_UNDETECTED'])

    def test_os_dois_separadores_estao_registrados(self):
        self.assertIn(',', self.d['SEPARATORS_FOUND'])
        self.assertIn('e', self.d['SEPARATORS_FOUND'])

    def test_o_que_nao_apareceu_nao_e_declarado_inexistente(self):
        """NAO ENCONTREI NOS FORMATOS MEDIDOS != NAO EXISTE."""
        t = self.d['TESTED_AND_NOT_FOUND']
        self.assertIn('não é "não existe"', t['STATE'])
        formas = ' '.join(i['FORM'] for i in t['ITEMS'])
        self.assertIn('mais dolce', formas)

    def test_a_hipotese_larga_fica_registrada_como_derrubada(self):
        h = self.d['HYPOTHESIS_NARROWED']
        self.assertIn('coordenação', h['STARTED_AS'])
        self.assertIn('elisão de cabeça', h['MEASURED_AS'])



CASO_DURO = os.path.join(ROOT, 'data', 'samples', 'IT-CASOS',
                         'IT-CASE-DURUM-FUSARIUM-001.json')
PAINEL_DURO = os.path.join(ROOT, 'data', 'samples', 'IT-T3-LOTTA',
                           'IT-durum-field-panel.json')


@unittest.skipUnless(os.path.exists(CASO_DURO), 'caso ainda nao gerado')
class TestCasoDurumFusarium(unittest.TestCase):
    """O primeiro caso regional real — e os limites que nao podem ser afrouxados."""

    @classmethod
    def setUpClass(cls):
        cls.c = json.load(open(CASO_DURO, encoding='utf-8'))

    # Os campos que EXISTEM para nomear o que e proibido. Varrer o documento inteiro
    # fazia o teste reprovar a propria declaracao da proibicao — o que e ruido, nao
    # achado. O teste tem de pegar AFIRMACAO, nao o vocabulario da proibicao.
    META = ('FORBIDDEN_LABEL', 'STILL_FORBIDDEN_TO_WRITE')

    def _corpo_de_afirmacoes(self):
        c = {k: v for k, v in self.c.items() if k not in self.META}
        am = json.loads(json.dumps(c['ACTION_MAP'], ensure_ascii=False))
        am['SUPPLY'].pop('WHY', None)      # cita a lista de termos banidos
        c['ACTION_MAP'] = am
        return json.dumps(c, ensure_ascii=False).lower()

    # Banir a PALAVRA e diferente de banir a AFIRMACAO. O caso precisa poder escrever
    # "NAO que ainda exista oportunidade hoje" — que e justamente a frase que limita a
    # promessa. Um teste por palavra-chave crua obrigaria a apagar essa frase, e o
    # documento ficaria mais permissivo, nao menos. Entao o teste olha a POLARIDADE.
    NEGACAO = re.compile(r'(?:n[ãa]o|nunca|jamais|proibid|forbidden|not)\b[^.;]{0,60}$')

    def test_nunca_se_chama_oportunidade_nem_se_eleva_a_pais(self):
        """O rotulo maximo e REGIONAL CONVERGENCE WORTH INVESTIGATING."""
        self.assertIn('WORTH INVESTIGATING', self.c['CASE_LABEL'])
        t = self._corpo_de_afirmacoes()
        achados = 0
        for m in re.finditer(r'opportunity|oportunidade', t):
            achados += 1
            antes = t[max(0, m.start() - 70):m.start()]
            with self.subTest(trecho=t[max(0, m.start() - 70):m.end() + 20]):
                self.assertRegex(antes, self.NEGACAO,
                                 'a palavra so pode aparecer negada; aqui esta afirmada')
        self.assertEqual('Toscana', self.c['REGION'])
        self.assertLess(self.c['REGION_PCT_OF_NATIONAL_CROP'], 5.0)

    def test_a_negacao_da_promessa_esta_de_fato_escrita(self):
        """A excecao de polaridade so vale se a frase limitante existir mesmo."""
        v = self.c['WHAT_THE_PROVED_VERDICT_MEANS']
        self.assertIn('NÃO que ainda exista oportunidade hoje', v)
        self.assertIn('TERIA', v, 'o verbo tem de estar no passado condicional')

    def test_os_campos_meta_realmente_nomeiam_a_proibicao(self):
        """Se os campos sumirem, a excecao acima deixa de ser justificada.

        Excluir um campo da varredura so e honesto enquanto o campo existe PARA
        nomear o que e proibido. Sem este teste, META viraria uma porta de fuga.
        """
        self.assertIn('opportunity', self.c['FORBIDDEN_LABEL'].lower())
        self.assertIn('Toscana', self.c['FORBIDDEN_LABEL'])
        proibidas = ' '.join(self.c['STILL_FORBIDDEN_TO_WRITE']).lower()
        for f in ('italy opportunity', 'national convergence', 'market gap'):
            self.assertIn(f, proibidas)

    def test_a_janela_de_2026_esta_declarada_fechada(self):
        """Janela passada nao e janela aberta — o erro da flavescencia nao volta."""
        b = self.c['CLOCKS']['B_AGRONOMIC_CLOCK']
        self.assertEqual('CLOSED_FOR_2026', b['WINDOW_STATE_AT_AS_OF'])
        self.assertTrue(b['WINDOWS_COINCIDE'])

    def test_o_relogio_comercial_e_not_known_e_a_inferencia_e_proibida(self):
        d = self.c['CLOCKS']['D_COMMERCIAL_CLOCK']
        self.assertEqual('NOT_KNOWN', d['STATE'])
        self.assertIn('NÃO implica', d['FORBIDDEN_INFERENCE'])

    def test_so_entram_produtos_com_durum_provado_no_rotulo(self):
        """E o SEEDRON fica FORA: fusariose de semente nao e fusariose de espiga."""
        nomes = [p['PRODUCT'] for p in self.c['ADAMA_REGULATORY_RESPONSE']]
        self.assertNotIn('SEEDRON', nomes)
        self.assertIn('MAXENTIS', nomes)
        self.assertIn('KOJAMI', nomes)
        for p in self.c['ADAMA_REGULATORY_RESPONSE']:
            self.assertIn('AUTHORIZED_USE_TABLE', p['DURUM_EVIDENCE'])
            self.assertTrue(p['IN_FORCE_AT_CASE_DATE'])

    def test_vencimento_passado_nao_vira_retirada(self):
        """CUSTODIA ULTRA e BLAISE ULTRA venceram 15 dias antes do AS_OF."""
        c = self.c['CLOCKS']['C_REGULATORY_PRODUCT_WINDOW']
        self.assertIn('CUSTODIA ULTRA', c['EXPIRY_DATE_PASSED_AT_AS_OF'])
        self.assertIn('EXPIRY ≠ WITHDRAWAL', c['ANOMALY_NOTE'])

    def test_as_duas_pernas_estao_preservadas_com_hash(self):
        """PRESERVED so vale se o byte puder ser reconferido."""
        p = self.c['PRESERVATION']
        self.assertEqual('PRESERVED', p['FIELD_LEG'])
        self.assertEqual('PRESERVED', p['PRODUCT_LEG'])
        self.assertEqual(64, len(p['FIELD_SHA256']))
        self.assertGreater(p['FIELD_BYTES'], 0)
        self.assertTrue(p['FIELD_SOURCE_URL'].startswith('https://'))
        self.assertEqual('2026-04-23', p['FIELD_SOURCE_DATE'])
        caminho = os.path.join(ROOT, p['FIELD_ARTIFACT'])
        self.assertTrue(os.path.exists(caminho), 'o artefato preservado tem de existir')
        import hashlib
        with open(caminho, 'rb') as fh:
            self.assertEqual(p['FIELD_SHA256'], hashlib.sha256(fh.read()).hexdigest(),
                             'o hash do disco tem de bater com o declarado')

    def test_o_verdito_subiu_e_carrega_os_tres_limites(self):
        """PROVED nao pode viajar sozinho: escopo, janela e comercial vao junto."""
        self.assertEqual('REAL_REGIONAL_CONVERGENCE_PROVED', self.c['VERDICT'])
        v = self.c['VERDICT_MUST_CARRY']
        self.assertEqual('NOT_KNOWN', v['COMMERCIAL_WINDOW'])
        self.assertEqual('TOSCANA / GROSSETO', v['SCOPE'])
        self.assertIn('CLOSED', v['AGRONOMIC_WINDOW_2026'])

    def test_o_escopo_nunca_foi_o_motivo_do_partial(self):
        """Preservar fechou a preservacao. NAO tornou o caso nacional."""
        e = self.c['VERDICT_DECOMPOSED']['SCOPE']
        self.assertIn('REGIONAL', e)
        self.assertIn('57,9', e)
        self.assertIn('NUNCA foi o motivo', e)

    def test_as_frases_proibidas_continuam_proibidas_mesmo_com_proved(self):
        proibidas = self.c['STILL_FORBIDDEN_TO_WRITE']
        for f in ('ITALY OPPORTUNITY', 'NATIONAL CONVERGENCE', 'ADAMA SHOULD ACT',
                  'MARKET GAP', 'SALES OPPORTUNITY'):
            self.assertIn(f, proibidas)
        t = self._corpo_de_afirmacoes()
        for f in ('italy opportunity', 'national convergence', 'adama should act',
                  'market gap'):
            self.assertNotIn(f, t)

    def test_a_preservacao_corrigiu_a_magnitude_do_risco(self):
        """Ler o texto guardado derrubou uma generalizacao minha.

        Eu escrevi "alto risco de fusariosi" para o grano duro. A fonte diz que o risco
        modelado e elevado no TENERO no sul e "in alcune situazioni del duro". Em
        compensacao ela traz SINTOMA OBSERVADO no duro, que e mais forte que modelo.
        """
        obs = ' '.join(o['WHAT'] for o in self.c['OBSERVED'])
        self.assertIn('CORREÇÃO DO PRÓPRIO CASO', obs)
        self.assertIn('IN ALCUNE SITUAZIONI DEL DURO', obs)
        self.assertIn('SINTOMA DE FUSARIOSE OBSERVADO', obs)
        leis = [o.get('LAW') for o in self.c['OBSERVED'] if o.get('LAW')]
        self.assertIn('SINTOMA OBSERVADO ≠ RISCO MODELADO', leis)

    def test_o_mapa_de_acoes_separa_olhar_de_agir(self):
        m = self.c['ACTION_MAP']
        self.assertIn('WHO CAN LOOK NOW ≠ WHO MUST ACT NOW', m['RULE'])
        self.assertFalse(m['COMMERCIAL']['CAN_LOOK_NOW'])
        self.assertEqual('NOT_KNOWN', m['MARKETING']['STATE'])
        self.assertEqual('NO_STATEMENT_POSSIBLE', m['SUPPLY']['STATE'])
        self.assertTrue(m['MARKET_DEVELOPMENT']['CAN_LOOK_NOW'])

    def test_nenhuma_afirmacao_proibida_pela_premissa(self):
        """Sem dado interno: nada de receita, margem, venda, estoque ou ROI."""
        t = self._corpo_de_afirmacoes()
        for proibido in ('revenue', 'margin', 'roi realized', 'market share',
                         'quota di mercato', 'inventory'):
            self.assertNotIn(proibido, t)

    def test_a_proibicao_de_supply_continua_escrita_em_algum_lugar(self):
        """A excecao do teste acima so vale enquanto a proibicao estiver declarada."""
        why = self.c['ACTION_MAP']['SUPPLY']['WHY'].lower()
        self.assertIn('dado interno', why)
        self.assertIn('revenue', why)


@unittest.skipUnless(os.path.exists(PAINEL_DURO), 'painel ainda nao gerado')
class TestPainelDoTrigoDuro(unittest.TestCase):
    """Abrir a rota nao e ler o sinal — tres regioes novas, cobertura inalterada."""

    @classmethod
    def setUpClass(cls):
        cls.d = json.load(open(PAINEL_DURO, encoding='utf-8'))

    def test_sondar_nao_move_cobertura_sem_ler_boletim(self):
        self.assertFalse(self.d['COVERAGE_MOVED'])
        self.assertEqual(3.7, self.d['PCT_NATIONAL_NOW_COVERED'])
        self.assertGreater(self.d['PCT_NATIONAL_PROBED_THIS_ROUND'], 35.0)

    def test_cada_regiao_declara_orgao_rota_e_estado(self):
        for r in self.d['REGIONS']:
            with self.subTest(regiao=r['REGION']):
                self.assertTrue(r['BODY'])
                self.assertTrue(r['ROUTES_TRIED'])
                self.assertTrue(r['EVIDENCE_STATE'])
                self.assertTrue(r['RAW_EVIDENCE_STATE'])

    def test_falha_de_rota_nunca_e_ausencia_de_sinal(self):
        sic = [r for r in self.d['REGIONS'] if r['REGION'] == 'Sicilia'][0]
        self.assertEqual('BULLETIN_NOT_FOUND_ON_MEASURED_ROUTES', sic['FIELD_SIGNAL_STATE'])
        self.assertIn('NORMA TÉCNICA ≠ SINAL DE CAMPO', sic['LAW'])
        sias = [x for x in sic['ROUTES_TRIED'] if x['HTTP'] == 503][0]
        self.assertEqual(2, sias['ATTEMPTS'], 'duas tentativas, e para')

    def test_conteudo_atras_de_cadastro_nao_e_bloqueio_nem_ausencia(self):
        bas = [r for r in self.d['REGIONS'] if r['REGION'] == 'Basilicata'][0]
        self.assertEqual('GATED_BY_FREE_REGISTRATION', bas['EVIDENCE_STATE'])
        self.assertIn('GATED ≠ BLOCKED ≠ ABSENT', bas['LAW'])
        self.assertIn('ação para fora', bas['WHY_I_DID_NOT_OPEN_IT'])


ANTEC = os.path.join(ROOT, 'data', 'samples', 'IT-CASOS',
                     'IT-CASE-DURUM-FUSARIUM-001-antecipacao.json')


@unittest.skipUnless(os.path.exists(ANTEC), 'auditoria de antecipacao ainda nao gerada')
class TestFutureEvidenceCannotClosePastCase(unittest.TestCase):
    """FUTURE_EVIDENCE_CANNOT_CLOSE_PAST_CASE.

    Um caso datado so prova ANTECIPACAO se fechar com o que existia no dia. Se qualquer
    peca publicada depois for necessaria para justificar o alerta, o que se mostra e
    retrospectiva bem escrita — outra coisa, e vale muito menos.
    """

    @classmethod
    def setUpClass(cls):
        import italia_antecipacao as ant
        cls.ant = ant
        cls.d = json.load(open(ANTEC, encoding='utf-8'))

    def test_nenhuma_evidencia_posterior_sustenta_o_alerta(self):
        ok, viol = self.ant.auditar(self.ant.evidencias())
        self.assertTrue(ok, 'evidencia posterior marcada como SUSTAINS_ALERT: %s' % viol)
        self.assertTrue(self.d['AUDIT_PASSES'])
        self.assertEqual([], self.d['VIOLATIONS'])

    def test_toda_peca_do_alerta_tem_data_anterior_ou_igual(self):
        import datetime
        caso = datetime.date.fromisoformat(self.d['CASE_DATE'])
        for e in self.d['AVAILABLE_BY_CASE_DATE']:
            with self.subTest(item=e['ITEM']):
                self.assertLessEqual(datetime.date.fromisoformat(e['SOURCE_DATE']), caso)

    def test_as_pecas_posteriores_existem_e_sao_context_only(self):
        """Se a lista de posteriores esvaziar, o teste deixa de medir alguma coisa."""
        depois = self.d['AVAILABLE_ONLY_LATER']
        self.assertGreaterEqual(len(depois), 3)
        for e in depois:
            with self.subTest(item=e['ITEM']):
                self.assertEqual('CONTEXT_ONLY', e['ROLE'])

    def test_a_data_usada_e_a_vigencia_do_documento_nao_a_do_download(self):
        """Os PDFs sao de agosto; o rotulo italiano e modificavel sob art.7 DPR 55/2012.

        Uma copia de agosto pode carregar modificacao de junho, entao a data que conta e
        a vigencia declarada DENTRO do documento.
        """
        rot = [e for e in self.d['AVAILABLE_BY_CASE_DATE']
               if e.get('IN_DOCUMENT_VALIDITY_IT')]
        self.assertEqual(5, len(rot), 'os cinco rotulos declaram vigencia propria')
        self.assertIn('art. 7', self.d['THE_SUBTLETY_THAT_ALMOST_SLIPPED'])

    def test_limitacao_do_observador_nao_e_limitacao_da_evidencia(self):
        """A correcao do extrator e de agosto, mas o rotulo ja dizia em marco."""
        t = self.d['OBSERVER_LIMITATION_IS_NOT_EVIDENCE_LIMITATION']
        self.assertIn('OBSERVADOR', t)
        self.assertIn('saber ler', t)

    # ------------------------------------------------------------------ MUTACAO
    def test_mutacao_promover_uma_peca_posterior_reprova(self):
        """Prova que a auditoria MEDE. Sem isto ela poderia passar por vacuidade."""
        evs = [dict(e) for e in self.ant.evidencias()]
        alvo = [e for e in evs if e['SOURCE_DATE'] == '2026-08-24'][0]
        alvo['ROLE'] = self.ant.SUSTAINS
        ok, viol = self.ant.auditar(evs)
        self.assertFalse(ok, 'promover o instantaneo de agosto TEM de reprovar')
        self.assertEqual(1, len(viol))
        self.assertIn('2026-08-24', viol[0]['SOURCE_DATE'])

    def test_mutacao_adiantar_a_data_do_caso_reprova(self):
        """Se o caso fosse de marco, o proprio boletim de 23/04 seria evidencia futura."""
        import datetime
        ok, viol = self.ant.auditar(self.ant.evidencias(),
                                    case_date=datetime.date(2026, 3, 1))
        self.assertFalse(ok)
        itens = [v['ITEM'] for v in viol]
        self.assertIn('Bollettino LaMMA Grosseto — frumento', itens)


VOZ = os.path.join(ROOT, 'data', 'samples', 'IT-CASOS', 'IT-HUMAN-SENSOR-PILOT.json')


@unittest.skipUnless(os.path.exists(VOZ), 'piloto de voz humana ainda nao gerado')
class TestCamadaDeSensoresHumanos(unittest.TestCase):
    """PESSOAS FUNCIONAM COMO SENSORES? Medido, e o "nao" tem forma."""

    @classmethod
    def setUpClass(cls):
        import italia_voz_humana as vh
        cls.vh = vh
        cls.d = json.load(open(VOZ, encoding='utf-8'))

    def test_porta_fechada_nunca_vira_ausencia_de_sinal(self):
        """LinkedIn e Instagram devolvem 200 com muro de login. HTTP 200 != FONTE VIVA."""
        for p in ('LINKEDIN', 'INSTAGRAM'):
            est = self.d['PLATFORM_STATE'][p]
            with self.subTest(plataforma=p):
                self.assertEqual(200, est['HTTP'])
                self.assertIn('ACCESS_FAILURE', est['STATE'])
                self.assertIn('ACCESS_FAILURE ≠ NO_SIGNAL', est['LAW'])

    def test_o_verdito_e_in_sample_e_nao_not_exists(self):
        """Com 2 de 3 portas fechadas, so cabe dizer o que NAO foi observado."""
        self.assertEqual('HUMAN_SENSOR_LAYER_NOT_PROVED_IN_SAMPLE', self.d['VERDICT'])
        self.assertIn('NOT_PROVED_IN_SAMPLE e não NOT_EXISTS', self.d['VERDICT_WHY'])

    def test_classes_sem_sinal_dizem_nao_observado_e_nao_inexistente(self):
        for k in ('FIRST_RESEARCHER_SIGNAL', 'FIRST_TECHNICAL_SIGNAL',
                  'FIRST_CREATOR_SIGNAL'):
            with self.subTest(classe=k):
                self.assertEqual('NOT_OBSERVED_IN_MEASURED_SAMPLE',
                                 self.d['CLOCK_BY_CLASS'][k]['STATE'])
                self.assertIsNone(self.d['CLOCK_BY_CLASS'][k]['DATE'])

    def test_data_aproximada_nunca_coloca_nada_antes_do_caso(self):
        """"6 mesi fa" nao e 2026-02-xx. Aproximacao nao fecha afirmacao temporal.

        O webinar da Adama provavelmente e anterior a 23/04. "Provavelmente" e
        exatamente o que esta proibido de virar BEFORE_CASE.
        """
        aprox = [p for p in self.d['PROFILES']
                 if p.get('DATE_STATE') == 'NOT_DATED_PRECISELY']
        self.assertGreaterEqual(len(aprox), 2)
        for p in aprox:
            with self.subTest(quem=p['NAME']):
                self.assertNotEqual('BEFORE_CASE', p.get('RELATIVE_TO_CASE'))

    def test_o_unico_sinal_anterior_esta_qualificado(self):
        """Corteva veio 25 dias antes — de outra doenca, sem regiao, e e comercial."""
        c = [x for x in self.d['CONTENTS_READ']
             if x.get('RELATIVE_TO_CASE') == 'BEFORE_CASE']
        self.assertEqual(1, len(c))
        self.assertEqual(25, c[0]['DAYS_BEFORE_CASE'])
        self.assertEqual('Septoria', c[0]['ISSUE'])
        self.assertIn('não é o issue do caso', c[0]['DOES_NOT_ADD'])
        inst = self.d['CLOCK_BY_CLASS']['FIRST_INSTITUTIONAL_SIGNAL']
        self.assertEqual('BEFORE_CASE', inst['STATE'])

    def test_o_artigo_de_2024_fica_fora_da_janela(self):
        """CLASSE CERTA != JANELA CERTA. Encaixaria na narrativa e seria falso."""
        b = [x for x in self.d['CONTENTS_READ'] if 'Biagetti' in x['PERSON_OR_ORGANIZATION']][0]
        self.assertEqual('2024-04-20', b['PUBLISHED_AT'])
        self.assertEqual('OUT_OF_WINDOW', b['RELATIVE_TO_CASE'])
        self.assertIn('seria falso', b['WHY_EXCLUDED'])

    def test_concorrente_entra_so_como_contexto(self):
        """A Corteva aparece porque calhou, nao porque foi coletada como concorrente."""
        cor = [p for p in self.d['PROFILES'] if p['NAME'] == 'Corteva Agriscience'][0]
        self.assertTrue(cor['COMPETITOR_CONTEXT_ONLY'])
        t = json.dumps(self.d, ensure_ascii=False).lower()
        for proibido in ('competitor portfolio', 'meta ads', 'ads library'):
            self.assertNotIn(proibido, t)

    def test_nenhum_token_vazou_para_o_artefato(self):
        """Nunca gravar credencial. Vale para o artefato e para o script."""
        import re as _re
        alvo = json.dumps(self.d, ensure_ascii=False)
        fonte = open(os.path.join(ROOT, 'scripts', 'italia_voz_humana.py'),
                     encoding='utf-8').read()
        pad = _re.compile(r'apify_api_[A-Za-z0-9]{10,}')
        for nome, txt in (('artefato', alvo), ('script', fonte)):
            with self.subTest(onde=nome):
                self.assertIsNone(pad.search(txt))
        self.assertFalse(self.d['APIFY']['TOKEN_1_USED'])
        self.assertEqual(0, self.d['APIFY']['TOTAL_ACTOR_RUNS'])

    def test_a_amostra_respeitou_os_tetos(self):
        c = self.d['COUNTS']
        self.assertLessEqual(c['PROFILES_OR_ENTITIES'], c['LIMIT_PROFILES'])
        self.assertLessEqual(c['YOUTUBE_ITEMS_SCREENED'], c['LIMIT_CONTENTS'])
        self.assertIn('não fechar pergunta', c['STOPPED_EARLY_BECAUSE'])

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

    def test_as_dezoito_estao_presentes(self):
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
                     'SOURCE_LAYER != SIGNAL_ABSENCE',
                     'STRONG_PATTERN != PERMISSION_TO_CLOSE',
                     'AUTHORIZATION != OPPORTUNITY',
                     'ONE_REGION != COUNTRY',
                     'ROUTE_OPENED != SIGNAL_READ',
                     'PAST_WINDOW != OPEN_WINDOW',
                     'FUTURE_EVIDENCE_CANNOT_CLOSE_PAST_CASE',
                     'OBSERVED_SYMPTOM != MODELLED_RISK',
                     'ACCESS_FAILURE != NO_SIGNAL',
                     'APPROXIMATE_DATE != DATED_EVIDENCE'):
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
