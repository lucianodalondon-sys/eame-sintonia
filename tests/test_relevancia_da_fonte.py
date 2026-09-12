#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""AS PROVAS DO PORTAO DE RELEVANCIA DE FONTE.

Cada teste aqui e uma propriedade que, se cair, deixa passar um gasto que
ninguem autorizou — ou transforma uma confissao num veredito.

    UMA DECISAO QUE A PORTA NAO CONHECE NAO E UMA DECISAO.

Por isso metade destes testes nao fala com a lei: fala com o CAMINHO REAL,
`pedido -> receitas.resolver -> orquestrador.correr`. Uma lei com testes verdes
e nenhum chamador e um documento com sintaxe de Python.
"""
import os
import sys
import unittest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)
import _gavetas  # noqa: E402,F401

import relevancia_da_fonte as rel      # noqa: E402
import admissao as adm                 # noqa: E402
import receitas                        # noqa: E402
import orquestrador as orq             # noqa: E402
from pedido import Pedido              # noqa: E402


def decisao(source_id, proposito, resultado, **kw):
    kw.setdefault('motivo', 'medido nesta prova')
    kw.setdefault('metodo', 'PROVA_BARATA_ACERVO')
    if resultado in rel.RESULTADOS_QUE_AFIRMAM:
        kw.setdefault('evidencia', {'file': 'data/samples/x.json', 'line': 1})
    return rel.Decisao(source_id=source_id, proposito=proposito,
                       resultado=resultado, **kw).para_livro()


class OEixoSemanticoEODaCasa(unittest.TestCase):
    """As cinco palavras nao se reinventam aqui (COL-LAW-038)."""

    def test_as_cinco_palavras_vem_do_dono_delas(self):
        self.assertEqual(adm.RESULTADOS, rel.RESULTADOS,
                         'o eixo semantico divergiu do dono, admissao/admissao.py. '
                         'Duas listas com as mesmas palavras sao duas verdades.')

    def test_nao_avaliada_nao_e_um_resultado(self):
        """Ninguem olhou != olhou-se e nao se concluiu."""
        self.assertNotIn(rel.NAO_AVALIADA, rel.RESULTADOS)


class AsQuatroAusenciasNaoSaoAMesmaCoisa(unittest.TestCase):
    """2 · UNKNOWN nao vira NOT_RELEVANT. 3 · ERROR nao vira NOT_RELEVANT."""

    def test_nao_sei_nao_vira_nao(self):
        livro = [decisao('IT-T3-002', 'T3', rel.NAO_SEI)]
        v = rel.portao('IT-T3-002', 'T3', livro, custo='gratuito')
        self.assertEqual(rel.EXIGE_AVALIACAO, v['VEREDITO'])
        self.assertNotEqual(rel.BARRA, v['VEREDITO'])
        self.assertEqual(rel.NAO_SEI, v['ESTADO_DA_RELEVANCIA'])

    def test_erro_nao_vira_nao(self):
        livro = [decisao('IT-T3-002', 'T3', rel.ERRO)]
        v = rel.portao('IT-T3-002', 'T3', livro, custo='gratuito')
        self.assertEqual(rel.EXIGE_AVALIACAO, v['VEREDITO'])
        self.assertNotEqual(rel.BARRA, v['VEREDITO'])

    def test_nao_avaliada_nao_vira_nao(self):
        v = rel.portao('IT-T3-002', 'T3', [], custo='gratuito')
        self.assertEqual(rel.EXIGE_AVALIACAO, v['VEREDITO'])
        self.assertEqual(rel.NAO_AVALIADA, v['ESTADO_DA_RELEVANCIA'])

    def test_as_tres_ausencias_continuam_distinguiveis_no_veredito(self):
        """Mesmo veredito, estados diferentes: nao se achatam."""
        estados = []
        for r in (rel.NAO_SEI, rel.ERRO):
            livro = [decisao('IT-T3-002', 'T3', r)]
            estados.append(rel.portao('IT-T3-002', 'T3', livro,
                                      custo='gratuito')['ESTADO_DA_RELEVANCIA'])
        estados.append(rel.portao('IT-T3-002', 'T3', [],
                                  custo='gratuito')['ESTADO_DA_RELEVANCIA'])
        self.assertEqual(3, len(set(estados)), 'as tres ausencias colapsaram')

    def test_um_nao_explicito_barra_mesmo_de_graca(self):
        """4 · ACCESS_BLOCKED nao vira NOT_RELEVANT — e o NAO real barra."""
        livro = [decisao('IT-T3-002', 'T3', rel.NAO)]
        v = rel.portao('IT-T3-002', 'T3', livro, custo='gratuito')
        self.assertEqual(rel.BARRA, v['VEREDITO'])


class OsEixosNaoSePreenchemUnsAosOutros(unittest.TestCase):
    """5 · saude. 6 · custo zero. 7 · custo alto."""

    def test_a_lei_nao_le_saude_nem_acesso_nem_ficha(self):
        """O unico ingrediente do estado e o livro.

        Se `estado()` aceitasse saude ou a ficha da fonte, a primeira pressa
        escrevia `if health == HEALTHY: return SIM`.
        """
        import inspect
        params = set(inspect.signature(rel.estado).parameters)
        self.assertEqual({'source_id', 'proposito', 'livro'}, params,
                         'estado() ganhou um ingrediente que nao e o livro')

    def test_custo_zero_nao_torna_relevante(self):
        v = rel.portao('IT-T3-002', 'T3', [], custo='gratuito')
        self.assertNotEqual(rel.AUTORIZA, v['VEREDITO'])
        self.assertEqual(rel.NAO_AVALIADA, v['ESTADO_DA_RELEVANCIA'])

    def test_custo_alto_nao_torna_irrelevante(self):
        livro = [decisao('IT-T9-002', 'T9', rel.SIM)]
        v = rel.portao('IT-T9-002', 'T9', livro,
                       custo='pago quando passa pela rota Apify')
        self.assertEqual(rel.AUTORIZA, v['VEREDITO'])
        self.assertIn(rel.GASTO_DINHEIRO, v['FORMAS_DE_GASTO_ABERTAS'])

    def test_relevante_com_rota_bloqueada_continua_relevante(self):
        """E · RELEVANT + ACCESS BLOCKED sao dois campos, nao um."""
        livro = [decisao('IT-T9-008', 'T9', rel.SIM)]
        v = rel.portao('IT-T9-008', 'T9', livro, custo='gratuito')
        self.assertEqual(rel.AUTORIZA, v['VEREDITO'])
        # O acesso continua a ser respondido por quem e dono dele.
        self.assertFalse(receitas._sabe_o_caminho({'access_method': 'NÃO SEI'}))

    def test_nao_saber_o_custo_nao_e_custar_zero(self):
        for custo in (None, 'NAO SEI', 'NÃO SEI', '', 'talvez gratuito', 0):
            with self.subTest(custo=custo):
                self.assertFalse(rel.custo_e_gratuito(custo))
        self.assertTrue(rel.custo_e_gratuito('gratuito'))


class ARelevanciaEDoParNaoDaFonte(unittest.TestCase):
    """8 · relevancia de um universo nao vaza para outro."""

    def test_sim_em_t3_nao_autoriza_t9(self):
        livro = [decisao('IT-T3-002', 'T3', rel.SIM)]
        self.assertEqual(rel.AUTORIZA,
                         rel.portao('IT-T3-002', 'T3', livro,
                                    custo='gratuito')['VEREDITO'])
        self.assertEqual(rel.EXIGE_AVALIACAO,
                         rel.portao('IT-T3-002', 'T9', livro,
                                    custo='gratuito')['VEREDITO'])

    def test_nao_em_t9_nao_condena_t3(self):
        livro = [decisao('IT-T3-002', 'T9', rel.NAO)]
        self.assertEqual(rel.BARRA,
                         rel.portao('IT-T3-002', 'T9', livro,
                                    custo='gratuito')['VEREDITO'])
        self.assertEqual(rel.EXIGE_AVALIACAO,
                         rel.portao('IT-T3-002', 'T3', livro,
                                    custo='gratuito')['VEREDITO'])

    def test_a_mesma_fonte_carrega_dois_vereditos_independentes(self):
        livro = [decisao('IT-T3-002', 'T3', rel.SIM),
                 decisao('IT-T3-002', 'T9', rel.NAO)]
        self.assertEqual(rel.AUTORIZA, rel.portao('IT-T3-002', 'T3', livro,
                                                  custo='gratuito')['VEREDITO'])
        self.assertEqual(rel.BARRA, rel.portao('IT-T3-002', 'T9', livro,
                                               custo='gratuito')['VEREDITO'])

    def test_a_decisao_de_uma_fonte_nao_fala_pelas_outras_do_territorio(self):
        """A CHAVE E O PAR, E A FONTE E METADE DELA.

        ⚠️ ESTE TESTE NASCEU DE UM MUTANTE VIVO. A suite provava que o
        PROPOSITO fazia parte da chave, e nunca provava que a FONTE tambem —
        de modo que tirar `SOURCE_ID` do filtro passava despercebido, e a
        decisao de uma fonte respondia pelas outras dezasseis de T3.
        """
        livro = [decisao('IT-T3-002', 'T3', rel.SIM)]
        self.assertEqual(rel.AUTORIZA, rel.portao('IT-T3-002', 'T3', livro,
                                                  custo='gratuito')['VEREDITO'])
        outra = rel.portao('IT-T3-008', 'T3', livro, custo='gratuito')
        self.assertEqual(rel.NAO_AVALIADA, outra['ESTADO_DA_RELEVANCIA'])
        self.assertEqual(rel.EXIGE_AVALIACAO, outra['VEREDITO'])

    def test_um_nao_numa_fonte_nao_condena_as_vizinhas(self):
        livro = [decisao('IT-T3-002', 'T3', rel.NAO)]
        self.assertEqual(rel.BARRA, rel.portao('IT-T3-002', 'T3', livro,
                                               custo='gratuito')['VEREDITO'])
        self.assertNotEqual(rel.BARRA, rel.portao('IT-T3-008', 'T3', livro,
                                                  custo='gratuito')['VEREDITO'])

    def test_decisao_sem_proposito_e_recusada(self):
        with self.assertRaises(rel.DecisaoInvalida):
            rel.Decisao(source_id='IT-T3-002', proposito='', resultado=rel.SIM,
                        motivo='x', metodo='y', evidencia={'a': 1})


class OItemNaoFalaPelaFonte(unittest.TestCase):
    """9 · um item negativo nao condena. 10 · um positivo nao promove."""

    def test_a_lei_da_fonte_nao_importa_a_lei_do_item(self):
        """Duas perguntas, dois livros, duas chaves.

        `admissao` decide o par (ITEM, universo); esta lei decide o par
        (FONTE, proposito). Elas partilham o EIXO e nada mais — livros
        diferentes, e nenhuma consegue escrever no da outra.
        """
        self.assertNotEqual(str(adm.LIVRO), os.path.join(RAIZ, rel.LIVRO))

    def test_o_livro_de_itens_nao_move_o_portao_da_fonte(self):
        """Mil decisoes de item, e o portao da fonte nao se mexe."""
        antes = rel.portao('IT-T3-002', 'T3', [], custo='gratuito')
        # decisoes de ITEM, na lingua da porta de admissao, no livro da fonte:
        livro_errado = [{'item': 'x', 'universo': 'T3', 'resultado': rel.SIM}]
        depois = rel.portao('IT-T3-002', 'T3', livro_errado, custo='gratuito')
        self.assertEqual(antes['VEREDITO'], depois['VEREDITO'])
        self.assertEqual(rel.NAO_AVALIADA, depois['ESTADO_DA_RELEVANCIA'])

    def test_uma_decisao_de_fonte_exige_source_id_e_proposito(self):
        """Uma linha de item nunca passa por decisao de fonte."""
        with self.assertRaises(rel.DecisaoInvalida):
            rel.registar([{'item': 'x', 'universo': 'T3', 'resultado': 'SIM'}],
                         raiz=RAIZ)


class ADecisaoTemProvaVersaoEHistoria(unittest.TestCase):
    """15 · evidencia. 16 · versao. 17 · a negativa fica."""

    def test_sim_sem_evidencia_e_recusado(self):
        with self.assertRaises(rel.DecisaoInvalida):
            rel.Decisao(source_id='IT-T3-002', proposito='T3',
                        resultado=rel.SIM, motivo='acho', metodo='olhometro')

    def test_nao_sem_evidencia_e_recusado(self):
        with self.assertRaises(rel.DecisaoInvalida):
            rel.Decisao(source_id='IT-T3-002', proposito='T3',
                        resultado=rel.NAO, motivo='acho', metodo='olhometro')

    def test_nao_sei_pode_confessar_sem_prova(self):
        """Exigir prova de quem confessa empurraria toda a gente para o NAO."""
        d = rel.Decisao(source_id='IT-T3-002', proposito='T3',
                        resultado=rel.NAO_SEI, motivo='amostra magra',
                        metodo='PROVA_BARATA_ACERVO')
        self.assertEqual(rel.NAO_SEI, d.resultado)

    def test_toda_decisao_carrega_versao(self):
        d = rel.Decisao(source_id='IT-T3-002', proposito='T3',
                        resultado=rel.NAO_SEI, motivo='x', metodo='y')
        self.assertTrue(d.versao)
        self.assertIn('VERSAO', d.para_livro())

    def test_decisao_sem_versao_e_recusada(self):
        with self.assertRaises(rel.DecisaoInvalida):
            rel.Decisao(source_id='IT-T3-002', proposito='T3',
                        resultado=rel.NAO_SEI, motivo='x', metodo='y',
                        versao='')

    def test_decisao_sem_metodo_e_recusada(self):
        with self.assertRaises(rel.DecisaoInvalida):
            rel.Decisao(source_id='IT-T3-002', proposito='T3',
                        resultado=rel.NAO_SEI, motivo='x', metodo='')

    def test_reavaliar_escreve_por_cima_e_a_negativa_fica(self):
        livro = [decisao('IT-T3-002', 'T3', rel.NAO),
                 decisao('IT-T3-002', 'T3', rel.SIM)]
        e = rel.estado('IT-T3-002', 'T3', livro)
        self.assertEqual(rel.SIM, e['ESTADO'])
        self.assertEqual(2, e['HISTORICO'], 'a decisao antiga desapareceu')

    def test_nao_existe_funcao_de_apagar_no_dono_da_lei(self):
        proibidas = [n for n in dir(rel)
                     if any(p in n.lower() for p in ('apagar', 'remover',
                                                     'delete', 'limpar'))]
        self.assertEqual([], proibidas,
                         'apareceu uma porta para apagar decisao: %s' % proibidas)

    def test_o_portao_carimba_a_versao_da_regra(self):
        v = rel.portao('IT-T3-002', 'T3', [], custo='gratuito')
        self.assertEqual(rel.VERSAO_DO_PORTAO, v['VERSAO_DO_PORTAO'])


class AFonteNaoNasceDeUmaURL(unittest.TestCase):
    """12 · a fila nao fabrica SOURCE_ID. 13 · URL nao vira SOURCE_ID."""

    def test_url_nunca_e_source_id(self):
        for u in ('https://arpa.veneto.it', 'http://x.it/y', 'www.istat.it',
                  '//istat.it', 'data/samples/IT-T3-002/x.pdf'):
            with self.subTest(url=u):
                with self.assertRaises(rel.SourceIdInvalido):
                    rel.conferir_source_id(u)

    def test_source_id_vazio_e_recusado(self):
        for s in (None, '', '   ', 42):
            with self.subTest(s=s):
                with self.assertRaises(rel.SourceIdInvalido):
                    rel.conferir_source_id(s)

    def test_a_fila_de_candidatas_nao_preenche_source_id(self):
        import fonte_nova
        fonte = open(os.path.join(RAIZ, 'candidatas', 'fonte_nova.py'),
                     encoding='utf-8').read()
        self.assertIn('"SOURCE_ID": None', fonte,
                      'a fila passou a nascer com SOURCE_ID: uma candidata '
                      'viraria fonte sem ninguem a ter aberto')
        self.assertTrue(hasattr(fonte_nova, 'registar'))

    def test_a_prova_barata_recusa_fonte_fora_do_cadastro(self):
        import prova_barata
        with self.assertRaises(prova_barata.ProvaRecusada):
            prova_barata.observar('IT-T99-999', 'T3')

    def test_a_fila_escreve_onde_a_lei_e_o_mapa_leem(self):
        """UMA FILA COM DUAS MORADAS E DUAS FILAS.

        Medido antes desta missao: `fonte_nova.py` escrevia em
        `data/samples/FONTES-CANDIDATAS.json` — ficheiro que nem existe — e a
        COL-LAW-053, o AGENTS.md, o scanner do mapa e o indice de fontes
        apontavam todos para `candidatas/`. O degrau 1 da escada estava
        invisivel, e `candidates: 0` no mapa nao distinguia «ninguem registou»
        de «registaram noutro sitio».
        """
        import fonte_nova
        escrita = os.path.relpath(str(fonte_nova.FILA), RAIZ).replace(os.sep, '/')
        scanner = open(os.path.join(RAIZ, 'system-map', 'scripts',
                                    'scan_sources.py'), encoding='utf-8').read()
        biblia = open(os.path.join(RAIZ, 'BIBLIA-CANONICA-DA-COLETA.md'),
                      encoding='utf-8').read()
        self.assertIn('FILA = "%s"' % escrita, scanner,
                      'a porta escreve em %s e o mapa le noutro sitio' % escrita)
        self.assertIn(escrita, biblia,
                      'a porta escreve em %s e a COL-LAW-053 nomeia outro'
                      % escrita)
        self.assertTrue(os.path.isfile(str(fonte_nova.FILA)),
                        'a fila declarada nao existe em disco')


class ODeclaradoNaoEOObservado(unittest.TestCase):
    """O territorio escrito na ficha nao e uma avaliacao."""

    def test_o_territorio_da_ficha_nao_promove_a_fonte(self):
        """`IT-T3-002` diz T3 no proprio nome. Isso nao e uma decisao."""
        v = rel.portao('IT-T3-002', 'T3', [], custo='gratuito')
        self.assertEqual(rel.NAO_AVALIADA, v['ESTADO_DA_RELEVANCIA'])

    def test_o_verdict_do_atlas_nao_e_portado(self):
        import censo_de_relevancia_das_fontes as censo
        self.assertFalse(censo.PORTAR_DO_ATLAS)
        self.assertEqual(0, censo.medir()['PORTADAS_DO_ATLAS'])

    def test_o_atlas_declara_yellow_como_relevante(self):
        """A prova de que GREEN nao quer dizer «relevante».

        Se o amarelo — que o atlas define como «fonte real e RELEVANTE, mas com
        atrito» — nao e verde, entao o verde nao esta a medir relevancia.
        """
        atlas = open(os.path.join(RAIZ, 'docs', 'fontes',
                                  'ATLAS-DE-FONTES-EAME.md'),
                     encoding='utf-8').read()
        i = atlas.find('**YELLOW**')
        self.assertGreater(i, 0, 'o atlas deixou de definir YELLOW')
        linha = atlas[i:i + 240]
        self.assertIn('relevante', linha.lower(),
                      'YELLOW deixou de declarar a fonte relevante; a base da '
                      'recusa em portar GREEN mudou e tem de ser remedida')


class ONaoENaoEOErroEErro(unittest.TestCase):
    """18 · rejeicao de fonte != erro de acesso."""

    def test_barra_e_exige_avaliacao_sao_vereditos_diferentes(self):
        self.assertNotEqual(rel.BARRA, rel.EXIGE_AVALIACAO)
        self.assertEqual(3, len(set(rel.VEREDITOS)))

    def test_o_erro_de_avaliacao_nunca_produz_barra(self):
        for r in (rel.ERRO, rel.NAO_SEI):
            with self.subTest(resultado=r):
                livro = [decisao('IT-T3-002', 'T3', r)]
                self.assertNotEqual(
                    rel.BARRA,
                    rel.portao('IT-T3-002', 'T3', livro,
                               custo='gratuito')['VEREDITO'])

    def test_a_sonda_que_nao_consegue_olhar_levanta_erro_e_nao_um_nao(self):
        import prova_barata
        with self.assertRaises(prova_barata.ProvaRecusada) as c:
            prova_barata.sondar('IT-T3-002', 'T3', custo_da_rota='gratuito')
        self.assertIn('ERRO', str(c.exception))


class ARotaPagaNaoCorreSemPortao(unittest.TestCase):
    """11 · rota paga nao executa sem gate. 19 · promocao != coleta."""

    def test_rota_paga_com_relevancia_ausente_bloqueia(self):
        v = rel.portao('IT-T9-002', 'T9', [],
                       custo='pago quando passa pela rota Apify')
        self.assertTrue(v['BLOQUEIA_A_CORRIDA'])
        self.assertFalse(v['PODE_GASTAR'])

    def test_rota_paga_com_relevancia_provada_passa(self):
        livro = [decisao('IT-T9-002', 'T9', rel.SIM)]
        v = rel.portao('IT-T9-002', 'T9', livro,
                       custo='pago quando passa pela rota Apify')
        self.assertFalse(v['BLOQUEIA_A_CORRIDA'])

    def test_coleta_recorrente_sobre_fonte_nao_avaliada_bloqueia(self):
        v = rel.portao('IT-T2-002', 'T2', [], custo='gratuito',
                       acionamento='AGENDADO')
        self.assertTrue(v['BLOQUEIA_A_CORRIDA'])
        self.assertIn(rel.GASTO_RECORRENTE, v['FORMAS_DE_GASTO_ABERTAS'])

    def test_coleta_total_sobre_fonte_nao_avaliada_bloqueia(self):
        v = rel.portao('IT-T2-002', 'T2', [], custo='gratuito', escopo='TOTAL')
        self.assertTrue(v['BLOQUEIA_A_CORRIDA'])
        self.assertIn(rel.GASTO_VOLUME, v['FORMAS_DE_GASTO_ABERTAS'])

    def test_observacao_barata_continua_possivel_sem_avaliacao(self):
        """O portao guarda o gasto, nao a observacao (COL-LAW-018)."""
        v = rel.portao('IT-T2-002', 'T2', [], custo='gratuito',
                       acionamento='MANUAL', escopo='PONTUAL')
        self.assertFalse(v['BLOQUEIA_A_CORRIDA'])
        self.assertTrue(v['PODE_OBSERVAR_BARATO'])

    def test_um_nao_explicito_fecha_ate_a_observacao_barata(self):
        livro = [decisao('IT-T2-002', 'T2', rel.NAO)]
        v = rel.portao('IT-T2-002', 'T2', livro, custo='gratuito',
                       acionamento='MANUAL', escopo='PONTUAL')
        self.assertFalse(v['PODE_OBSERVAR_BARATO'])

    def test_promover_nao_dispara_coleta(self):
        """19 · escrever SIM no livro nao corre nada."""
        livro = [decisao('IT-T9-002', 'T9', rel.SIM)]
        v = rel.portao('IT-T9-002', 'T9', livro, custo='gratuito')
        self.assertEqual(rel.AUTORIZA, v['VEREDITO'])
        # o veredito autoriza; nao executa, nao escolhe rota, nao nomeia executor
        self.assertNotIn('EXECUTOR', v)
        self.assertNotIn('ROTA', v)


class AProvaBarataNaoViraColeta(unittest.TestCase):
    """O probe tem teto, nao paga e nao decide."""

    def test_a_prova_nunca_decide(self):
        import prova_barata
        o = prova_barata.observar('IT-T3-002', 'T3')
        self.assertEqual('NAO_TOMADA', o['DECISAO'])
        self.assertNotIn(o['DECISAO'], rel.RESULTADOS)

    def test_o_teto_e_respeitado(self):
        import prova_barata
        o = prova_barata.observar('IT-T3-002', 'T3', teto=1)
        self.assertLessEqual(len(o['UNIDADES_OLHADAS']), 1)
        self.assertEqual(1, o['TETO_DE_UNIDADES'])

    def test_o_denominador_vai_junto(self):
        import prova_barata
        o = prova_barata.observar('IT-T3-002', 'T3', teto=1)
        self.assertIn('UNIDADES_NO_ACERVO', o)
        self.assertGreaterEqual(o['UNIDADES_NO_ACERVO'],
                                len(o['UNIDADES_OLHADAS']))

    def test_a_prova_barata_nao_gasta(self):
        import prova_barata
        self.assertTrue(prova_barata.PROVA_BARATA_NUNCA_PAGA)
        o = prova_barata.observar('IT-T3-002', 'T3')
        self.assertEqual(0, o['CUSTO_USD'])
        self.assertFalse(o['REDE_USADA'])

    def test_a_sonda_recusa_rota_paga_e_rota_de_custo_desconhecido(self):
        """E RECUSA PELO MOTIVO DO DINHEIRO, nao por acaso.

        ⚠️ ESTE TESTE NASCEU DE UM MUTANTE VIVO. A versao anterior so exigia
        que `sondar` levantasse — e ela levanta sempre, porque o transporte
        canonico nao vive nesta arvore. Tirar a trava do dinheiro nao mudava
        nada visivel, e o mutante sobrevivia.

            DUAS RECUSAS DIFERENTES QUE PRODUZEM A MESMA EXCEPCAO
            SAO UMA TRAVA E UM ACASO COM O MESMO ASPECTO.
        """
        import prova_barata
        for custo in ('pago quando passa pela rota Apify', 'NAO SEI', None):
            with self.subTest(custo=custo):
                with self.assertRaises(prova_barata.ProvaRecusada) as c:
                    prova_barata.sondar('IT-T3-002', 'T3',
                                        custo_da_rota=custo)
                self.assertIn('ROTA PAGA', str(c.exception),
                              'recusou, mas nao por causa do dinheiro')
                self.assertIn('autorizacao humana', str(c.exception))

    def test_a_recusa_por_dinheiro_e_a_recusa_por_transporte_sao_distintas(self):
        import prova_barata
        with self.assertRaises(prova_barata.ProvaRecusada) as pago:
            prova_barata.sondar('IT-T3-002', 'T3', custo_da_rota='NAO SEI')
        with self.assertRaises(prova_barata.ProvaRecusada) as gratis:
            prova_barata.sondar('IT-T3-002', 'T3', custo_da_rota='gratuito')
        self.assertNotEqual(str(pago.exception), str(gratis.exception))
        self.assertIn('ROTA PAGA', str(pago.exception))
        self.assertIn('SONDA NAO DISPONIVEL', str(gratis.exception))

    def test_nada_no_acervo_nao_e_fonte_que_nao_serve(self):
        import prova_barata
        o = prova_barata.observar('IT-T5-001', 'T5')
        self.assertNotIn(o['O_QUE_DEU'], rel.RESULTADOS)
        self.assertEqual('NAO_TOMADA', o['DECISAO'])


class OLivroNaoSeApagaSozinho(unittest.TestCase):
    """Livro ilegivel != livro vazio."""

    def test_livro_ilegivel_levanta_em_vez_de_devolver_vazio(self):
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            caminho = os.path.join(d, rel.LIVRO)
            os.makedirs(os.path.dirname(caminho), exist_ok=True)
            open(caminho, 'w', encoding='utf-8').write('{isto nao e json')
            with self.assertRaises(rel.LivroIlegivel):
                rel.ler_livro(d)

    def test_livro_que_nao_existe_e_livro_vazio(self):
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            self.assertEqual([], rel.ler_livro(d))

    def test_registar_junta_e_nunca_reescreve(self):
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            rel.registar([decisao('IT-T3-002', 'T3', rel.NAO)], raiz=d)
            rel.registar([decisao('IT-T3-002', 'T3', rel.SIM)], raiz=d)
            livro = rel.ler_livro(d)
            self.assertEqual(2, len(livro))
            self.assertEqual(rel.NAO, livro[0]['RESULTADO'])


class OPortaoEstaNoCaminhoReal(unittest.TestCase):
    """1 · fonte nao promovida nao entra em coleta normal, no caminho de verdade.

    ⚠️ SEM ESTA CLASSE, TUDO O QUE ESTA ACIMA E UM DOCUMENTO. O teste tem de
    atravessar `Pedido -> receitas.resolver -> orquestrador.correr`.
    """

    def setUp(self):
        self._ler = receitas.rel.ler_livro

    def tearDown(self):
        receitas.rel.ler_livro = self._ler

    def _com_livro(self, livro):
        receitas.rel.ler_livro = lambda *a, **k: livro

    def test_o_plano_traz_o_veredito(self):
        self._com_livro([])
        plano = receitas.resolver(Pedido(alvo='T9'))
        self.assertTrue(plano.relevancia, 'o plano nao consulta o portao')
        self.assertEqual(rel.EXIGE_AVALIACAO, plano.relevancia['VEREDITO'])

    def test_a_rota_paga_e_barrada_no_orquestrador(self):
        self._com_livro([])
        recibo = orq.correr(Pedido(alvo='T9'))
        self.assertEqual('BARRADO_NA_RELEVANCIA', recibo['STATUS'])
        self.assertEqual(0, recibo['COST_USD'])
        self.assertEqual('NAO_CORREU', recibo['ESTADO_DOS_ITENS'])

    def test_barrado_nao_e_erro_nem_falta_de_caminho(self):
        self._com_livro([])
        recibo = orq.correr(Pedido(alvo='T9'))
        self.assertNotEqual('FAILED', recibo['STATUS'])
        self.assertNotEqual('SEM_CAMINHO', recibo['STATUS'])

    def test_a_rota_paga_passa_quando_a_fonte_foi_provada(self):
        """A · fonte relevante passa para o proximo portao.

        T9 nao nomeia fonte, logo nem um SIM a autoriza — e esse e o ponto:
        nao se autoriza gasto sobre uma fonte que o plano nao nomeia.
        """
        self._com_livro([decisao('IT-T9-002', 'T9', rel.SIM)])
        plano = receitas.resolver(Pedido(alvo='T9'))
        self.assertIsNone(plano.relevancia['SOURCE_ID'])
        self.assertTrue(plano.bloqueia_a_corrida)

    def test_a_rota_gratuita_nomeada_passa_com_sim_e_e_barrada_com_nao(self):
        """T2 nomeia IT-T2-002: aqui a decisao decide mesmo."""
        self._com_livro([decisao('IT-T2-002', 'T2', rel.SIM)])
        p = receitas.resolver(Pedido(alvo='T2'))
        self.assertEqual('IT-T2-002', p.relevancia['SOURCE_ID'])
        self.assertEqual(rel.AUTORIZA, p.relevancia['VEREDITO'])

        self._com_livro([decisao('IT-T2-002', 'T2', rel.NAO)])
        p = receitas.resolver(Pedido(alvo='T2'))
        self.assertEqual(rel.BARRA, p.relevancia['VEREDITO'])

    def test_agendado_sobre_fonte_nao_avaliada_nao_corre(self):
        self._com_livro([])
        recibo = orq.correr(Pedido(alvo='T2', acionamento='AGENDADO'))
        self.assertEqual('BARRADO_NA_RELEVANCIA', recibo['STATUS'])

    def test_total_sobre_fonte_nao_avaliada_nao_corre(self):
        self._com_livro([])
        recibo = orq.correr(Pedido(alvo='T2', escopo='TOTAL'))
        self.assertEqual('BARRADO_NA_RELEVANCIA', recibo['STATUS'])

    def test_o_recibo_guarda_o_estado_mesmo_quando_passa(self):
        """Sem isto, nao ha como perguntar sob que relevancia cada corrida correu."""
        self._com_livro([])
        recibo = orq.correr(Pedido(alvo='T2'), seco=True)
        self.assertIn('RELEVANCIA_DA_FONTE', recibo)
        self.assertEqual(rel.NAO_AVALIADA,
                         recibo['RELEVANCIA_DA_FONTE']['ESTADO_DA_RELEVANCIA'])

    def test_da_para_correr_continua_a_responder_so_pelo_caminho(self):
        """`SEM_CAMINHO` e `BARRADO` sao duas respostas, nao uma."""
        self._com_livro([])
        plano = receitas.resolver(Pedido(alvo='T9'))
        self.assertTrue(plano.da_para_correr)
        self.assertTrue(plano.bloqueia_a_corrida)


class NaoHaScoreNemBooleanoUniversal(unittest.TestCase):
    """21 · um score medio compensaria uma falha grave."""

    def test_a_lei_recusa_score(self):
        for proibido in ('SOURCE_SCORE', 'RANKING_UNICO', 'NOTA_DE_0_A_100'):
            self.assertIn(proibido, rel.NAO_CRIAR)

    def test_nao_ha_campo_numerico_de_relevancia_no_veredito(self):
        v = rel.portao('IT-T3-002', 'T3', [], custo='gratuito')
        numericos = [k for k, x in v.items()
                     if isinstance(x, (int, float)) and not isinstance(x, bool)]
        self.assertEqual(['HISTORICO'], numericos,
                         'apareceu um numero no veredito: %s' % numericos)

    def test_o_ficheiro_da_lei_nao_tem_score(self):
        fonte = open(os.path.join(RAIZ, 'leis', 'relevancia_da_fonte.py'),
                     encoding='utf-8').read().lower()
        self.assertNotIn('def score', fonte)
        self.assertNotIn('relevance_score', fonte)


class OCensoMedeEDeclara(unittest.TestCase):
    """20 · a regressao das fontes atuais continua limpa."""

    def test_o_censo_conta_todas_as_fontes_do_cadastro(self):
        import censo_de_relevancia_das_fontes as censo
        c = censo.medir()
        self.assertEqual(c['TOTAIS']['FONTES_NO_CADASTRO'], len(c['FONTES']))
        self.assertGreater(c['TOTAIS']['FONTES_NO_CADASTRO'], 0)

    def test_o_censo_separa_quem_gasta_de_quem_so_coleta(self):
        import censo_de_relevancia_das_fontes as censo
        t = censo.medir()['TOTAIS']
        self.assertLessEqual(t['PODEM_GASTAR_DINHEIRO'],
                             t['PODEM_DISPARAR_COLETA'])

    def test_nenhuma_fonte_que_gasta_escapa_ao_portao_sem_decisao(self):
        import censo_de_relevancia_das_fontes as censo
        c = censo.medir()
        escapou = [l for l in c['FONTES']
                   if l['PODE_GASTAR_DINHEIRO']
                   and l['RELEVANCIA_PRESENTE'] == 'NAO'
                   and l['VEREDITO_DO_PORTAO'] == rel.AUTORIZA]
        self.assertEqual([], escapou,
                         'fonte que gasta dinheiro passou o portao sem decisao')


if __name__ == '__main__':
    unittest.main(verbosity=2)
