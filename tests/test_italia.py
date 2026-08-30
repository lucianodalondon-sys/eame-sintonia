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
import italia_istat as ii2         # noqa: E402
import italia_cobertura_campo      # noqa: E402,F401
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

    def test_as_cinco_estao_presentes(self):
        """Apagar uma regressao nao pode ser a forma de fazer a suite passar."""
        for nome in ('SYMPTOM_WINDOW != APPLICATION_WINDOW',
                     'READ_FAILURE != NO_LABEL',
                     'AFFILIATION != STUDY_GEOGRAPHY',
                     'REGISTRATION != COMMERCIAL_CATALOG',
                     'GENERIC_TARGET != SPECIFIC_TARGET'):
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
