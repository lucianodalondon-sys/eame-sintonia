# -*- coding: utf-8 -*-
"""As cinco cicatrizes que o leitor italiano não pode reabrir.

Este ficheiro existe por regressões MEDIDAS, não por simetria. O PASSO 03 trouxe
`scripts/fato_local.py` do piloto italiano, e a versão de lá reabria quatro falsos
positivos fundadores e perdia um foco confirmado em silêncio. Os casos abaixo são
os que a revisão adversarial reproduziu, verbatim.

AS LEIS (decisão de coordenação do PASSO 03):

    EVENTO                != FATO
    LOCAL_DA_FONTE        != LOCAL_DO_FATO
    SEDE                  != LOCAL_DO_FATO
    RISK_WORD             != PHYTOSANITARY_RISK
    GENERIC_PRESENCE      != DISEASE_PRESENCE

E uma que não é sobre falso positivo, mas sobre silêncio:

    RECUSAR é um resultado. DESAPARECER não é.
"""
import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'scripts'))
import fato_local as fl        # noqa: E402
import lugar_do_fato as L      # noqa: E402


def le(texto):
    ok, nao = fl.localizacoes_do_fato(texto)
    return ([(a['FACT_LOCATION'], a['TYPE_OF_EVIDENCE']) for a in ok],
            {r['PLACE'] for r in nao})


class EventoNaoEFato(unittest.TestCase):
    """A cicatriz fundadora: um congresso não é um foco de doença."""

    def test_congresso_com_verbo_depois_do_toponimo(self):
        """A âncora positiva vinha DEPOIS e ganhava por distância."""
        ok, nao = le('Il convegno internazionale organizzato a Bologna ha rilevato sintomi')
        self.assertEqual([], ok, 'o congresso voltou a virar observação de campo')
        self.assertIn('Bologna', nao, 'recusar é um resultado — Bologna tem de aparecer')

    def test_duas_oracoes_cada_lugar_com_a_sua_ancora(self):
        """A trava não pode ser tão larga que mate o lugar legítimo da segunda oração."""
        ok, nao = le('Convegno a Bologna e fusariosi constatata a Grosseto.')
        self.assertEqual([('Grosseto', 'CONFIRMED_FOCUS')], ok)
        self.assertIn('Bologna', nao)


class SedeNaoELocalDoFato(unittest.TestCase):

    def test_sede_legal_com_observacao_na_oracao_seguinte(self):
        ok, nao = le("La sede legale dell'azienda si trova a Bologna, "
                     'dove sono stati osservati sintomi')
        self.assertEqual([], ok, 'a sede da empresa voltou a virar lugar do fato')
        self.assertIn('Bologna', nao)


class RiskWordNaoERiscoFitossanitario(unittest.TestCase):
    """`rischio` sozinho não prova risco agronómico."""

    REAL = ('Prezzi in picchiata per il grano duro di Capitanata. Quotazioni al '
            'ribasso che mettono a rischio le aziende agricole della Provincia di Foggia.')

    def test_noticia_de_preco_nao_vira_afirmacao_fitossanitaria(self):
        """Texto REAL, já versionado em data/samples/SENSOR-PILOT/VIDEOS-A.json."""
        ok, _ = le(self.REAL)
        self.assertEqual([], ok, 'uma notícia de preço voltou a produzir MODELLED_RISK')

    def test_o_artigo_nao_e_sujeito_de_risco(self):
        for t in ('mette a rischio le colture della provincia di Foggia',
                  'a rischio la produzione nella provincia di Foggia'):
            with self.subTest(t=t):
                ok, _ = le(t)
                self.assertNotIn('MODELLED_RISK', [e for _, e in ok],
                                 'âncora ancorada num artigo')

    def test_o_risco_modelado_de_verdade_continua_a_existir(self):
        """A classe não foi removida — foi qualificada."""
        ok, _ = le('Rischio attacchi septoriosi nella provincia di Perugia')
        self.assertEqual([('Perugia', 'MODELLED_RISK')], ok)


class PresencaGenericaNaoEPresencaDeDoenca(unittest.TestCase):

    def test_presenca_de_empresas_nao_e_sintoma_visto(self):
        ok, _ = le('La presenza di aziende agricole in Toscana e significativa')
        self.assertEqual([], ok, 'presença de EMPRESAS voltou a contar como observação')

    def test_presenca_de_tecnicos_nao_e_sintoma_visto(self):
        ok, _ = le('Il progetto prevede la presenza di tecnici in Lombardia')
        self.assertEqual([], ok)

    def test_presenca_media_de_patogeno_continua_a_contar(self):
        """O caso real que justificava a âncora não se perdeu."""
        ok, _ = le('Presenza media di Septoriosi nel frumento in Umbria')
        self.assertEqual([('Umbria', 'FIELD_OBSERVATION')], ok)


class FocoConfirmadoNaoDesaparece(unittest.TestCase):
    """Saltar a primeira oração como se fosse cabeçalho apagava o facto."""

    def test_primeira_oracao_que_relata_nao_e_cabecalho(self):
        ok, _ = le('Constatata fusariosi nella provincia di Grosseto. '
                   'Il tempo resta variabile')
        self.assertEqual([('Grosseto', 'CONFIRMED_FOCUS')], ok,
                         'o foco confirmado desapareceu — e sem sequer entrar nas recusas')

    def test_com_regiao_no_comeco_tambem(self):
        ok, _ = le('Regione Toscana: constatata fusariosi a Grosseto. '
                   'Il grano tenero resta esente')
        self.assertIn('Grosseto', [p for p, _ in ok])

    def test_cabecalho_inerte_continua_a_ser_cabecalho(self):
        """A trava não pode desligar o escopo de documento onde ele é legítimo."""
        ok, _ = le('Provincia di Grosseto - Bollettino Frumento del 2026-04-23. '
                   'Constatata fusariosi nelle aziende monitorate.')
        self.assertTrue(ok, 'o escopo de documento deixou de funcionar')


class OLeitorNaoInventaEspecieQueONucleoNaoConhece(unittest.TestCase):
    """MODELLED_RISK existe no leitor e não no núcleo — e não pode vazar."""

    def test_o_leitor_nao_promove_risco_modelado_a_ocorrencia_observada(self):
        conta = fl.ocorrencia_nao_e_incidencia(['MODELLED_RISK'])
        self.assertEqual(0, conta.get('OBSERVED_OCCURRENCES', 0),
                         'risco modelado passou a contar como ocorrência observada')

    def test_o_nucleo_nao_conhece_a_especie_e_isso_esta_declarado(self):
        self.assertNotIn('MODELLED_RISK', set(L.TIPOS_DE_EVIDENCIA))


if __name__ == '__main__':
    unittest.main()


# ---------------------------------------------------------------------------
# SEGUNDA RODADA — o que a revisão adversarial do PASSO 03 encontrou.
#
# As quatro correções da DECISÃO 1 passaram os 90 testes da ref e os 14 desta
# casa, e mesmo assim seis famílias de falso positivo continuavam vivas no corpus
# REAL. Cinco vieram com a ref; uma foi minha. Ficam aqui com o contraexemplo
# reproduzido, porque teste que só cobre o que eu lembrei de olhar não é rede.
# ---------------------------------------------------------------------------

CORPUS_TXT = [
    'data/samples/IT-ROTULOS-V1/testo/009790.txt',
    'data/samples/IT-ROTULOS-V1/testo/011794.txt',
    'data/samples/IT-ROTULOS-V1/testo/013905.txt',
    'data/samples/IT-ROTULOS-V1/testo/013807.txt',
    'data/samples/IT-ROTULOS-V1/testo/015315.txt',
]


class RiskWordEUmaClasseAberta(unittest.TestCase):
    """A lista de palavras-de-parada nunca fecha; a de sujeitos de risco fecha."""

    FUNCIONAIS = ('non', 'nel', 'nella', 'negli', 'nei', 'alcuni', 'alcune',
                  'questa', 'questo', 'tale', 'tali', 'ogni', 'molti', 'molte',
                  'molto', 'poco', 'anche', 'come', 'su', 'sul', 'sulla', 'con',
                  'da', 'dal', 'dalla', 'ai', 'al', 'alla', 'alle', 'agli',
                  'oltre', 'durante', 'entro', 'verso', 'tra', 'fra', 'piu',
                  'tutta', 'tutte', 'tutti', 'ancora', 'gia', 'sempre', 'solo',
                  "l'", "un'", "dell'", "all'", "nell'", "sull'")

    def test_nenhum_funcional_transforma_rischio_em_risco_fitossanitario(self):
        for w in self.FUNCIONAIS:
            frase = 'Il crollo dei prezzi mette a rischio %s aziende agricole di Cuneo' % w
            with self.subTest(palavra=w):
                ok, _ = fl.localizacoes_do_fato(frase)
                self.assertEqual([], [a['TYPE_OF_EVIDENCE'] for a in ok],
                                 '"rischio %s" ancorou risco fitossanitário' % w)

    def test_a_negacao_depois_da_ancora_nao_vira_afirmacao(self):
        """`rischio non e elevato` dizia o OPOSTO do texto, sobre Foggia."""
        ok, _ = fl.localizacoes_do_fato(
            'Al momento il rischio non e elevato nella provincia di Foggia')
        self.assertEqual([], ok)

    def test_a_noticia_de_preco_real_continua_recusada(self):
        for frase in (
                'Quotazioni al ribasso che mettono a rischio molte aziende agricole '
                'della Provincia di Foggia',
                "Prezzi in picchiata che mettono a rischio l'intera filiera "
                'cerealicola della Provincia di Foggia'):
            with self.subTest(frase=frase[:40]):
                self.assertEqual([], fl.localizacoes_do_fato(frase)[0])

    def test_o_risco_agronomico_de_verdade_continua_a_ancorar(self):
        for frase, ancora in (
                ('Il modello segnala rischio di infezione da peronospora nella '
                 'provincia di Perugia', 'rischio di infezione'),
                ('Rischio attacchi di septoriosi nella provincia di Perugia',
                 'rischio attacchi'),
                ('Elevato rischio di micotossine nel Comune di Parrano',
                 'rischio di micotossine')):
            with self.subTest(frase=frase[:40]):
                ok, _ = fl.localizacoes_do_fato(frase)
                self.assertEqual(1, len(ok), frase)
                self.assertEqual(fl.MODELLED_RISK, ok[0]['TYPE_OF_EVIDENCE'])
                self.assertEqual(ancora, ok[0]['FACT_LOCATION_ANCHOR'])


class PresencaDeQueEQuePesa(unittest.TestCase):
    """Cair fora o `di` inteiro trocou um falso positivo por 299 falsos negativos."""

    def test_presenca_de_praga_volta_a_ser_observacao(self):
        for objeto in ('adulti', 'larve', 'uova', 'infestanti', 'malerbe',
                       'psilla', 'scafoideo', 'antonomo', 'catture', 'sintomi'):
            frase = 'Si riscontra presenza di %s nella provincia di Ancona' % objeto
            with self.subTest(objeto=objeto):
                ok, _ = fl.localizacoes_do_fato(frase)
                self.assertEqual(1, len(ok), 'presenza di %s deixou de ancorar' % objeto)
                self.assertEqual(fl.FIELD_OBSERVATION, ok[0]['TYPE_OF_EVIDENCE'])

    def test_presenca_de_gente_continua_fora(self):
        for objeto in ('aziende agricole', 'tecnici', 'operatori', 'personale',
                       'pubblico'):
            with self.subTest(objeto=objeto):
                self.assertEqual([], fl.localizacoes_do_fato(
                    'Presenza di %s nella provincia di Ancona' % objeto)[0])


class OAssuntoDoEventoNaoEOFato(unittest.TestCase):
    """A ordem normal do italiano põe a doença DENTRO do título do congresso."""

    def test_o_congresso_sobre_a_doenca_nao_e_foco_da_doenca(self):
        for frase in (
                'Il convegno nazionale sui sintomi della septoriosi si terra a Bologna',
                'Il workshop sulla fusariosi constatata nei cereali si e svolto a Bologna',
                'Fiera dedicata alle infezioni fungine del frumento a Verona',
                'Il convegno sulla flavescenza dorata con focolai in vigneto si terra a Verona',
                "La sede legale dell'azienda che ha segnalato i sintomi si trova a Bologna"):
            with self.subTest(frase=frase[:44]):
                self.assertEqual([], fl.localizacoes_do_fato(frase)[0], frase)

    def test_a_cicatriz_fundadora_continua_curada_do_outro_lado(self):
        """A trava não pode matar o caso que a fez existir."""
        for frase in ('Convegno a Bologna e fusariosi constatata a Grosseto',
                      'Convegno a Bologna sulla difesa integrata. '
                      'Fusariosi constatata a Grosseto'):
            with self.subTest(frase=frase[:44]):
                ok, _ = fl.localizacoes_do_fato(frase)
                self.assertEqual([('Grosseto', fl.CONFIRMED_FOCUS)],
                                 [(a['FACT_LOCATION'], a['TYPE_OF_EVIDENCE']) for a in ok])


class OEnderecoDoTitularNaoEOLugarDoFato(unittest.TestCase):
    """SEDE != LOCAL_DO_FATO também quando a palavra `sede` não aparece."""

    def test_o_rodape_do_rotulo_nao_produz_lugar_do_fato(self):
        for rel in CORPUS_TXT:
            caminho = os.path.join(ROOT, rel)
            if not os.path.exists(caminho):
                self.skipTest('%s não versionado' % rel)
            with open(caminho, encoding='utf-8', errors='replace') as f:
                ok, _ = fl.localizacoes_do_fato(f.read())
            with self.subTest(rotulo=rel.split('/')[-1]):
                self.assertEqual(
                    [], [(a['FACT_LOCATION'], a['FACT_LOCATION_ANCHOR']) for a in ok],
                    'endereço do registrante virou lugar do fato')

    def test_observar_as_normas_nao_e_observar_no_campo(self):
        self.assertEqual([], fl.localizacoes_do_fato(
            'ADAMA ITALIA srl - Via Zanica 19 - 24050 Grassobbio, Bergamo. '
            'Osservate le norme precauzionali prescritte')[0])

    def test_marca_registrada_nao_e_ocorrencia_oficial(self):
        self.assertEqual([], fl.localizacoes_do_fato(
            'marchio registrato GOWAN ITALIA S.r.l.')[0])


class NotaDeTempoNaoEOcorrenciaFitossanitaria(unittest.TestCase):
    """Nos dois boletins mais ricos da Itália, o único fato aceite era a chuva."""

    BOLETINS = ('data/samples/IT-T5-SENSORES/marche-amap-an-615-2026-04-22.txt',
                'data/samples/IT-T5-SENSORES/marche-amap-an-616-2026-04-29.txt')

    def test_a_chuva_nao_entra_e_a_observacao_entra(self):
        for rel in self.BOLETINS:
            caminho = os.path.join(ROOT, rel)
            if not os.path.exists(caminho):
                self.skipTest('%s não versionado' % rel)
            with open(caminho, encoding='utf-8', errors='replace') as f:
                ok, _ = fl.localizacoes_do_fato(f.read())
            with self.subTest(boletim=rel.split('/')[-1]):
                self.assertTrue(ok, 'o boletim ficou mudo: trocou-se um erro por outro')
                for a in ok:
                    self.assertNotIn(a['TYPE_OF_EVIDENCE'], (fl.OFFICIAL_OCCURRENCE,),
                                     'nota meteorológica voltou a ser ocorrência')
                    self.assertNotRegex(
                        a['FACT_LOCATION_EVIDENCE'],
                        r'(?i)precipitazioni|temperature|piogg',
                        'o trecho que sustenta o fato é meteorologia')


class OQueSeCapturaTemDeParecerUmNome(unittest.TestCase):
    """FACT_LOCATION é chave de junção. Um timbre de cinco linhas ali é lixo."""

    def test_nenhum_lugar_do_corpus_carrega_lixo_de_captura(self):
        import glob
        vistos = 0
        for caminho in sorted(glob.glob(os.path.join(ROOT, 'data', 'samples',
                                                     '**', '*.txt'), recursive=True)):
            with open(caminho, encoding='utf-8', errors='replace') as f:
                texto = f.read()
            for a in fl.localizacoes_do_fato(texto)[0]:
                vistos += 1
                nome = a['FACT_LOCATION']
                with self.subTest(arquivo=os.path.basename(caminho), lugar=nome[:30]):
                    self.assertNotIn('\n', nome, 'o nome atravessou uma quebra de linha')
                    self.assertFalse(any(c.isdigit() for c in nome),
                                     'o nome carrega um número de protocolo')
                    self.assertNotRegex(nome, r'  +', 'o nome atravessou uma coluna de tabela')
                    self.assertLessEqual(len(nome), 60, 'o nome é um parágrafo')
                    # Literal escrito AQUI, não lido de `fl.PALAVRAS_ADMINISTRATIVAS`.
                    # Percorrer a constante da implementação torna a asserção vácua no
                    # instante em que alguém esvazia a lista: ciclo vazio, zero asserções,
                    # suíte verde. `TESTE QUE LÊ A PRÓPRIA REGRA NÃO TESTA A REGRA`.
                    for adm in ('presidenza', 'giunta', 'regionale', 'coordinamento',
                                'servizio', 'direzione', 'assessorato', 'dipartimento',
                                'settore', 'ufficio', 'bollettino', 'notiziario',
                                'comunicato', 'agenzia'):
                        self.assertNotIn(adm, fl._sem_acento(nome).lower().split(),
                                         'o nome é um pedaço de timbre')
        self.assertGreater(vistos, 0, 'nenhum lugar foi lido — o teste não provou nada')

    LUGARES_MEDIDOS = {
        'Alessandria', 'Ancona', 'Bari', 'Bologna', 'Branca di Gubbio', 'Catania',
        'Cremona', 'Emilia-Romagna', 'Ferrara', 'Friuli-Venezia Giulia', 'Italia',
        'Lagosanto', 'Lodi', 'Milano', 'Molise', 'Parrano', 'Piemonte', 'Ravenna',
        'Rovigo', 'Udine', 'Veneto', 'Venezia', 'Vicenza', 'Verona',
    }

    def test_o_conjunto_de_lugares_do_corpus_esta_pregado(self):
        """Olhar só para a FORMA do nome deixa passar o lixo de forma nova.

        Uma mutação que esvaziasse `CABECALHOS_DE_COLUNA` devolvia `Maturazione` — um
        cabeçalho de coluna — como lugar do fato, e nenhuma das 1.386 provas do
        repositório reprovava: o nome não tem quebra de linha, nem dígito, nem espaço
        duplo, e cabe em 60 caracteres. Aqui o conjunto inteiro está pregado, e mudar
        uma regra passa a exigir declarar o que ela mudou.
        """
        import glob
        lugares = set()
        for caminho in sorted(glob.glob(os.path.join(ROOT, 'data', 'samples',
                                                     '**', '*.txt'), recursive=True)):
            with open(caminho, encoding='utf-8', errors='replace') as f:
                for a in fl.localizacoes_do_fato(f.read())[0]:
                    lugares.add(a['FACT_LOCATION'])
        self.assertEqual(self.LUGARES_MEDIDOS, lugares,
                         'o conjunto de lugares que o corpus produz mudou — se a mudança '
                         'é intencional, actualize LUGARES_MEDIDOS e diga porquê')

    def test_limpa_nome_recusa_o_que_nao_e_nome(self):
        """`_limpa_nome` não tinha um único teste directo. Estes são literais."""
        self.assertIsNone(fl._limpa_nome('Maturazione  Si'),
                          'cabeçalho de coluna voltou a ser aceite como nome')
        self.assertIsNone(fl._limpa_nome('Coltura'))
        self.assertIsNone(fl._limpa_nome('SERVIZIO FITOSANITARIO'))
        self.assertEqual('Molise', fl._limpa_nome(
            'MOLISE\n\n     PRESIDENZA DELLA GIUNTA REGIONALE'))
        self.assertEqual('Piemonte', fl._limpa_nome('PIEMONTE BU12'))

    def test_limpa_nome_preserva_nome_legitimo(self):
        for nome in ('Reggio Emilia', 'La Spezia', 'Branca di Gubbio',
                     'Friuli-Venezia Giulia'):
            with self.subTest(nome=nome):
                self.assertEqual(nome, fl._limpa_nome(nome),
                                 'a limpeza destruiu um nome de lugar legítimo')

    def test_a_grafia_canonica_da_casa_e_sem_acento_e_isso_e_convencao(self):
        """`Forlì-Cesena` sai `Forli-Cesena`, e está certo: as 100 entradas do
        gazetteer são sem acento. FACT_LOCATION é chave de junção, e a chave é a do
        gazetteer — não a ortografia do documento de origem."""
        acentuadas = [n for n, _ in fl.GAZETTEER
                      if any(c in n for c in 'àèéìòùÀÈÉÌÒÙ')]
        self.assertEqual([], acentuadas,
                         'o gazetteer ganhou entrada acentuada — a convenção mudou e '
                         '_limpa_nome passa a devolver duas grafias para o mesmo lugar')
        self.assertEqual('Forli-Cesena', fl._limpa_nome('Forlì-Cesena'))

    def test_o_titulo_do_boletim_nao_e_um_relato(self):
        for titulo in ('Provincia di Grosseto - Bollettino Segnalazioni Fitosanitarie '
                       'del 23 aprile 2026. Il tempo resta variabile',
                       'Regione Toscana - Bollettino Rischio Fitosanitario n. 7. '
                       'Il tempo resta variabile'):
            with self.subTest(titulo=titulo[:44]):
                self.assertEqual([], fl.localizacoes_do_fato(titulo)[0])

    def test_o_cabecalho_que_RELATA_continua_a_valer(self):
        """A trava do título não pode reabrir o buraco que a DECISÃO 1 fechou."""
        ok, _ = fl.localizacoes_do_fato(
            'Constatata fusariosi nella provincia di Grosseto. Il tempo resta variabile')
        self.assertEqual([('Grosseto', fl.CONFIRMED_FOCUS)],
                         [(a['FACT_LOCATION'], a['TYPE_OF_EVIDENCE']) for a in ok])
