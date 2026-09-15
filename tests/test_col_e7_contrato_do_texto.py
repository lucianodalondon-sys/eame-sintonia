#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
COL-E7-01 — O CONTRATO DO TEXTO NA COLLECTION, ATACADO.

    Cada teste aqui e um ATAQUE que tem de morrer, ou uma MUTACAO que tem de
    ser apanhada. Nenhum deles mede «o codigo corre»: medem «a especie
    sobrevive a travessia, e o caminho errado nao existe».

        UM CONTRATO QUE SO PASSA QUANDO O CHAMADOR SE PORTA BEM
        NAO E UM CONTRATO: E UMA CONVENCAO.
"""
import os
import re
import sys
import tempfile
import unittest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)
import _gavetas                                              # noqa: E402,F401

import admissao as adm                                       # noqa: E402
import ingresso as ing                                       # noqa: E402
import proveniencia as pv                                    # noqa: E402
import social_envelope as env                                # noqa: E402


def unidade(**kw):
    base = dict(texto='um texto', kind=pv.AUTHOR_TEXT,
                kind_basis=pv.DECLARED_BY_ROUTE, relation=pv.ORIGINAL,
                unit_id='TU-1', derivation_method=pv.LIDO_DO_CAMPO)
    base.update(kw)
    return pv.unidade_de_texto(**base)


class OsDoisEixosNaoColapsam(unittest.TestCase):
    """ATAQUES 1 e 2 — legenda tratada como transcricao, e o contrario."""

    def test_caption_e_transcript_sao_valores_diferentes(self):
        self.assertIn(pv.NATIVE_CAPTION, pv.TEXT_KINDS)
        self.assertIn(pv.TRANSCRIPT, pv.TEXT_KINDS)
        self.assertNotEqual(pv.NATIVE_CAPTION, pv.TRANSCRIPT)

    def test_author_text_nao_se_escreve_CAPTION(self):
        # A colisao medida: `comunicacao_coleta` chama `CAPTION` ao texto do
        # autor e a C6 chama `NATIVE_CAPTION_*` a faixa de legenda. Um token
        # com dois donos e o ataque ja escrito no dicionario.
        self.assertNotIn('CAPTION', pv.TEXT_KINDS)
        self.assertIn(pv.AUTHOR_TEXT, pv.TEXT_KINDS)

    def test_a_legenda_nao_chega_a_porta_como_transcricao(self):
        u = unidade(kind=pv.NATIVE_CAPTION, language='it')
        item = ing.para_a_porta({'SOURCE_ID': 'S', pv.CAMPO_DAS_UNIDADES: [u]})
        self.assertEqual(pv.NATIVE_CAPTION, item['texto_especie'])

    def test_a_transcricao_nao_chega_a_porta_como_legenda(self):
        u = unidade(kind=pv.TRANSCRIPT, derivation_method=pv.ASR_DO_PROVEDOR,
                    tool='apify:actor')
        item = ing.para_a_porta({'SOURCE_ID': 'S', pv.CAMPO_DAS_UNIDADES: [u]})
        self.assertEqual(pv.TRANSCRIPT, item['texto_especie'])

    def test_traduzir_nao_muda_a_especie(self):
        # ATAQUE: uma traducao que se declara de outra especie que o original
        # seria o caminho por onde um transcript vira caption sem decisao.
        o = unidade(unit_id='TU-1', kind=pv.NATIVE_CAPTION, language='it')
        t = unidade(unit_id='TU-2', kind=pv.TRANSCRIPT, relation=pv.TRANSLATED,
                    translated_from='TU-1', language='en',
                    derivation_method=pv.TRADUCAO_DO_PROVEDOR, tool='x')
        mal = pv.conferir_unidades_de_texto([o, t])
        self.assertTrue(any('nunca a ESPECIE' in m for m in mal), mal)


class OAsrNaoEDeNinguem(unittest.TestCase):
    """ATAQUE 3 — o ASR tratado como texto do autor."""

    def test_asr_e_author_text_sao_valores_diferentes(self):
        self.assertNotEqual(pv.ASR, pv.AUTHOR_TEXT)

    def test_asr_sem_ferramenta_declarada_e_recusado(self):
        # Um texto de maquina sem maquina declarada nao se confere nem se repete.
        u = unidade(kind=pv.ASR, derivation_method=pv.ASR_DA_CASA, tool=None)
        mal = pv.conferir_unidade_de_texto(u)
        self.assertTrue(any('ferramenta' in m for m in mal), mal)

    def test_asr_com_ferramenta_declarada_passa(self):
        u = unidade(kind=pv.ASR, derivation_method=pv.ASR_DA_CASA,
                    tool='whisper', model='large-v3')
        self.assertEqual([], pv.conferir_unidade_de_texto(u))


class ATraducaoNaoSeFazPassarPorOriginal(unittest.TestCase):
    """ATAQUES 4 e 5 — traducao tratada como original, e original substituido."""

    def test_traducao_sem_apontar_o_original_e_recusada(self):
        u = unidade(relation=pv.TRANSLATED, translated_from=None)
        mal = pv.conferir_unidade_de_texto(u)
        self.assertTrue(any('TRANSLATED_FROM' in m for m in mal), mal)

    def test_quem_nao_e_traducao_nao_aponta_para_original(self):
        u = unidade(relation=pv.ORIGINAL, translated_from='TU-9')
        mal = pv.conferir_unidade_de_texto(u)
        self.assertTrue(any('contradicao' in m for m in mal), mal)

    def test_traducao_para_a_mesma_lingua_e_recusada(self):
        o = unidade(unit_id='TU-1', language='it')
        t = unidade(unit_id='TU-2', relation=pv.TRANSLATED, translated_from='TU-1',
                    language='it', derivation_method=pv.TRADUCAO_DO_PROVEDOR,
                    tool='x')
        mal = pv.conferir_unidades_de_texto([o, t])
        self.assertTrue(any('MESMA lingua' in m for m in mal), mal)

    def test_traducao_de_traducao_e_recusada(self):
        a = unidade(unit_id='TU-1', language='it')
        b = unidade(unit_id='TU-2', relation=pv.TRANSLATED, translated_from='TU-1',
                    language='en', derivation_method=pv.TRADUCAO_DO_PROVEDOR, tool='x')
        c = unidade(unit_id='TU-3', relation=pv.TRANSLATED, translated_from='TU-2',
                    language='fr', derivation_method=pv.TRADUCAO_DO_PROVEDOR, tool='x')
        mal = pv.conferir_unidades_de_texto([a, b, c])
        self.assertTrue(any('outra traducao' in m for m in mal), mal)

    def test_o_original_ganha_a_traducao_mesmo_vindo_depois(self):
        # ATAQUE 5 e 15 juntos: a traducao PRIMEIRO na lista.
        o = unidade(unit_id='TU-1', texto='convegno sulla ricerca', language='it')
        t = unidade(unit_id='TU-2', texto='conference on research',
                    relation=pv.TRANSLATED, translated_from='TU-1', language='en',
                    derivation_method=pv.TRADUCAO_DO_PROVEDOR, tool='x')
        item = ing.para_a_porta({'SOURCE_ID': 'S', pv.CAMPO_DAS_UNIDADES: [t, o]})
        self.assertEqual('it', item['texto_lingua'])
        self.assertEqual(pv.ORIGINAL, item['texto_relacao'])
        self.assertEqual('TU-1', item['texto_unidade'])

    def test_serve_para_original_recusa_traducao(self):
        self.assertFalse(pv.serve_para_original((pv.NATIVE_CAPTION, pv.TRANSLATED)))
        self.assertTrue(pv.serve_para_original((pv.NATIVE_CAPTION, pv.ORIGINAL)))


class ALinguaNaoSeAdivinha(unittest.TestCase):
    """ATAQUE 6 — texto sem lingua a receber lingua inferida."""

    def test_texto_sem_lingua_declarada_fica_UNKNOWN(self):
        u = unidade(language=None, texto='questo è chiaramente italiano')
        self.assertEqual(pv.TEXTO_DESCONHECIDO, u['LANGUAGE'])

    def test_a_lingua_da_publicacao_nao_desce_para_a_unidade(self):
        # `language=` e da PUBLICACAO; `text_language=` e do TEXTO. Sem o
        # segundo, a unidade fica UNKNOWN — nunca herda o primeiro.
        e = env.envelope(platform='BLUESKY', native_id='x', url='u',
                         content_type='POST', route='r', executor='e',
                         run_id='R', country_scope='IT', language='it',
                         text='ciao', text_kind=pv.AUTHOR_TEXT,
                         text_kind_basis=pv.DECLARED_BY_ROUTE,
                         text_relation=pv.ORIGINAL)
        self.assertEqual('it', e['LANGUAGE'])
        self.assertEqual(pv.TEXTO_DESCONHECIDO,
                         e[pv.CAMPO_DAS_UNIDADES][0]['LANGUAGE'])

    def test_nenhuma_base_da_especie_e_inferencia(self):
        # A lei da C6, e ela vale tambem para a base nova.
        for b in pv.BASES_DA_ESPECIE:
            self.assertNotIn('INFER', b.upper())

    def test_base_com_inferencia_e_recusada(self):
        # Recusada por NAO ESTAR NA LISTA, que e onde a lei vive. Nao ha guarda
        # especial para a palavra `INFER`: uma segunda guarda para um valor que
        # a lista ja barra seria codigo morto a fingir de lei.
        u = unidade(kind_basis='INFERRED_FROM_TEXT')
        mal = pv.conferir_unidade_de_texto(u)
        self.assertTrue(any('TEXT_KIND_BASIS fora do vocabulario' in m
                            for m in mal), mal)


class ODesconhecidoNaoSobeDeCategoria(unittest.TestCase):
    """ATAQUE 7 — `TEXT_KIND=UNKNOWN` promovido a legenda."""

    def test_envelope_legado_so_com_TEXT_nasce_UNKNOWN(self):
        u = pv.unidades_do_envelope({'TEXT': 'un testo', 'LANGUAGE': 'it',
                                     'URL': 'u'})[0]
        self.assertEqual(pv.TEXTO_DESCONHECIDO, u['TEXT_KIND'])
        self.assertEqual(pv.NOT_DECLARED, u['TEXT_KIND_BASIS'])
        self.assertEqual(pv.TEXTO_DESCONHECIDO, u['TEXT_RELATION'])

    def test_o_legado_nao_herda_a_lingua_da_publicacao(self):
        u = pv.unidades_do_envelope({'TEXT': 'un testo', 'LANGUAGE': 'it'})[0]
        self.assertEqual(pv.TEXTO_DESCONHECIDO, u['LANGUAGE'])

    def test_UNKNOWN_com_testemunha_declarada_e_recusado(self):
        u = unidade(kind=pv.TEXTO_DESCONHECIDO, kind_basis=pv.DECLARED_BY_PROVIDER)
        mal = pv.conferir_unidade_de_texto(u)
        self.assertTrue(any('so e desconhecida se ninguem a declarou' in m
                            for m in mal), mal)

    def test_UNKNOWN_atravessa_a_porta_ainda_UNKNOWN(self):
        u = pv.unidades_do_envelope({'TEXT': 'un testo', 'URL': 'u'})[0]
        item = ing.para_a_porta({'SOURCE_ID': 'S', pv.CAMPO_DAS_UNIDADES: [u]})
        self.assertEqual(pv.TEXTO_DESCONHECIDO, item['texto_especie'])

    def test_UNKNOWN_nao_sustenta_afirmacao_sobre_o_original(self):
        self.assertFalse(pv.serve_para_original(
            (pv.TEXTO_DESCONHECIDO, pv.ORIGINAL)))

    def test_especie_conhecida_ganha_a_UNKNOWN_na_escolha(self):
        d = unidade(unit_id='TU-1', kind=pv.TEXTO_DESCONHECIDO,
                    kind_basis=pv.NOT_DECLARED, relation=pv.TEXTO_DESCONHECIDO,
                    derivation_method=pv.TEXTO_DESCONHECIDO, texto='desconhecido')
        a = unidade(unit_id='TU-2', texto='do autor')
        escolhida, _ = pv.escolher_para_leitura([d, a])
        self.assertEqual('TU-2', escolhida['TEXT_UNIT_ID'])


class ALinhagemNaoSeApaga(unittest.TestCase):
    """ATAQUES 8, 9 e 10 — linhagem removida, observacao perdida, SHA como id."""

    def test_unidade_sem_LINEAGE_e_recusada(self):
        u = unidade()
        del u['LINEAGE']
        mal = pv.conferir_unidade_de_texto(u)
        self.assertTrue(any('LINEAGE' in m for m in mal), mal)

    def test_LINEAGE_sem_RAW_OBSERVATION_ID_e_recusada(self):
        u = unidade()
        del u['LINEAGE']['RAW_OBSERVATION_ID']
        mal = pv.conferir_unidade_de_texto(u)
        self.assertTrue(any('RAW_OBSERVATION_ID' in m for m in mal), mal)

    def test_RAW_OBSERVATION_ID_declarado_atravessa_ate_a_porta(self):
        u = unidade(raw_observation_id=4242)
        item = ing.para_a_porta({'SOURCE_ID': 'S', pv.CAMPO_DAS_UNIDADES: [u]})
        viajou = item[pv.CAMPO_DAS_UNIDADES][0]['LINEAGE']['RAW_OBSERVATION_ID']
        self.assertEqual(4242, viajou)

    def test_ausencia_de_observacao_diz_se_e_nao_se_cala(self):
        u = unidade(raw_observation_id=None)
        self.assertEqual(pv.TEXTO_DESCONHECIDO,
                         u['LINEAGE']['RAW_OBSERVATION_ID'])

    def test_TEXT_UNIT_ID_com_cara_de_sha_e_recusado(self):
        u = unidade(unit_id='a3f5e9d1c7b20486')
        mal = pv.conferir_unidade_de_texto(u)
        self.assertTrue(any('hash' in m for m in mal), mal)

    def test_TEXT_UNIT_ID_ausente_e_recusado(self):
        u = unidade(unit_id=None)
        mal = pv.conferir_unidade_de_texto(u)
        self.assertTrue(any('TEXT_UNIT_ID' in m for m in mal), mal)

    def test_moradas_repetidas_sao_recusadas(self):
        a, b = unidade(unit_id='TU-1'), unidade(unit_id='TU-1')
        mal = pv.conferir_unidades_de_texto([a, b])
        self.assertTrue(any('repetido' in m for m in mal), mal)

    def test_traducao_que_aponta_para_fora_da_observacao_e_recusada(self):
        t = unidade(relation=pv.TRANSLATED, translated_from='TU-99',
                    language='en', derivation_method=pv.TRADUCAO_DO_PROVEDOR,
                    tool='x')
        mal = pv.conferir_unidades_de_texto([t])
        self.assertTrue(any('nao esta nesta observacao' in m for m in mal), mal)


class OCaminhoAntigoNaoContornaOContrato(unittest.TestCase):
    """ATAQUES 11 e 12 — o `texto` legado a ignorar o contrato novo."""

    def test_texto_a_mao_que_contradiz_as_unidades_e_recusado(self):
        u = unidade(texto='o que a regra escolheu')
        with self.assertRaises(ing.TextoEmConflito):
            ing.para_a_porta({'SOURCE_ID': 'S', 'texto': 'outro texto qualquer',
                              pv.CAMPO_DAS_UNIDADES: [u]})

    def test_texto_a_mao_que_concorda_passa(self):
        u = unidade(texto='o mesmo texto')
        item = ing.para_a_porta({'SOURCE_ID': 'S', 'texto': 'o mesmo texto',
                                 pv.CAMPO_DAS_UNIDADES: [u]})
        self.assertEqual('o mesmo texto', item['texto'])

    def test_a_admissao_le_o_texto_que_a_regra_escolheu(self):
        o = unidade(unit_id='TU-1', texto='convegno sulla ricerca in campo',
                    language='it')
        t = unidade(unit_id='TU-2', texto='conference on field research',
                    relation=pv.TRANSLATED, translated_from='TU-1',
                    language='en', derivation_method=pv.TRADUCAO_DO_PROVEDOR,
                    tool='x')
        item = ing.para_a_porta({'SOURCE_ID': 'S', 'SOURCE_URL': 'u',
                                 pv.CAMPO_DAS_UNIDADES: [t, o]})
        item.update({'id': 'x', 'fact_time': '2026-01-01'})
        d = adm.decidir(item, 'T5', corrida='R')
        # Com o ORIGINAL italiano casa o lexico italiano. Com a traducao
        # inglesa nao casaria — e o veredito seria outro, sem ninguem ver.
        self.assertEqual('SIM', d.resultado)

    def test_o_contrato_e_conferido_na_porta_e_a_unidade_ma_e_recusada(self):
        banco = tempfile.mkdtemp(prefix='col-e7-teste-')
        mau = unidade(kind='INVENTADO')
        r = ing.receber(
            [{'SOURCE_ID': 'S', 'SOURCE_URL': 'u',
              pv.CAMPO_DAS_UNIDADES: [mau]}],
            corrida={'RUN_ID': 'R', 'STARTED_AT': '2026-09-13T00:00:00Z'},
            armazem=ing.ArmazemLocal(banco), memoria=None, raiz=banco)
        self.assertEqual(0, len(r['ACEITES']))
        self.assertEqual(ing.CONTRATO_QUEBRADO, r['RECUSAS'][0]['PORQUE'])


class UmConceitoUmDono(unittest.TestCase):
    """ATAQUE 13 — dois mappers independentes para o mesmo conceito."""

    def test_so_um_ficheiro_declara_o_vocabulario_da_especie(self):
        donos = []
        for pasta, _, ficheiros in os.walk(RAIZ):
            if any(p in pasta for p in ('/.git', 'node_modules', '/tests',
                                        '/docs', '/build')):
                continue
            for f in ficheiros:
                if not f.endswith('.py'):
                    continue
                caminho = os.path.join(pasta, f)
                with open(caminho, encoding='utf-8', errors='replace') as fh:
                    if re.search(r'^TEXT_KINDS\s*=', fh.read(), re.M):
                        donos.append(os.path.relpath(caminho, RAIZ))
        self.assertEqual(['regras/proveniencia.py'], sorted(donos),
                         'duas listas para o mesmo vocabulario divergem no dia '
                         'em que alguem acrescentar uma especie a uma delas')

    def test_a_porta_nao_redeclara_a_regra_da_escolha(self):
        with open(os.path.join(RAIZ, 'coleta', 'ingresso.py'),
                  encoding='utf-8') as fh:
            fonte = fh.read()
        self.assertNotIn('ORDEM_DA_ESPECIE =', fonte)
        self.assertIn('pv.texto_para_quem_julga', fonte)

    def test_a_escolha_aplica_se_uma_vez_so(self):
        with open(os.path.join(RAIZ, 'coleta', 'ingresso.py'),
                  encoding='utf-8') as fh:
            fonte = fh.read()
        self.assertEqual(1, fonte.count('pv.texto_para_quem_julga('))


class AAusenciaNaoViraVazio(unittest.TestCase):
    """ATAQUE 14 — ausencia de texto a virar string vazia e a ser admitida."""

    def test_sem_unidades_nao_ha_campo_texto(self):
        item = ing.para_a_porta({'SOURCE_ID': 'S',
                                 pv.CAMPO_DAS_UNIDADES: []})
        self.assertNotIn('texto', item)

    def test_unidades_sem_texto_nao_dao_campo_texto(self):
        u = unidade(texto='   ')
        item = ing.para_a_porta({'SOURCE_ID': 'S', pv.CAMPO_DAS_UNIDADES: [u]})
        self.assertNotIn('texto', item)

    def test_os_dois_silencios_tem_nomes_diferentes(self):
        self.assertEqual((None, pv.SEM_UNIDADES), pv.escolher_para_leitura([]))
        vazia = unidade(texto='')
        self.assertEqual((None, pv.SEM_TEXTO_LEGIVEL),
                         pv.escolher_para_leitura([vazia]))

    def test_a_porta_responde_NAO_SEI_a_uma_observacao_sem_texto(self):
        item = ing.para_a_porta({'SOURCE_ID': 'S', 'SOURCE_URL': 'u',
                                 pv.CAMPO_DAS_UNIDADES: []})
        item.update({'id': 'x', 'fact_time': '2026-01-01'})
        d = adm.decidir(item, 'T5', corrida='R')
        self.assertEqual('NAO_SEI', d.resultado)


class AEscolhaTemRegraEscrita(unittest.TestCase):
    """ATAQUE 15 — a lista a escolher «o primeiro» sem regra canonica."""

    def test_a_escolha_diz_porque_escolheu(self):
        item = ing.para_a_porta({'SOURCE_ID': 'S',
                                 pv.CAMPO_DAS_UNIDADES: [unidade()]})
        self.assertIn('ordem canonica', item['texto_escolha_porque'])

    def test_a_ordem_nao_depende_da_ordem_da_lista(self):
        a = unidade(unit_id='TU-1', kind=pv.PAGE_TEXT, texto='pagina',
                    derivation_method=pv.RASPADO_DA_PAGINA)
        b = unidade(unit_id='TU-2', kind=pv.AUTHOR_TEXT, texto='autor')
        for lista in ([a, b], [b, a]):
            escolhida, _ = pv.escolher_para_leitura(lista)
            self.assertEqual('TU-2', escolhida['TEXT_UNIT_ID'])

    def test_a_ordem_da_especie_cobre_todo_o_vocabulario(self):
        # Uma ordem incompleta manda o valor que falta para o fim em silencio.
        self.assertEqual(sorted(pv.TEXT_KINDS), sorted(pv.ORDEM_DA_ESPECIE))
        self.assertEqual(sorted(pv.TEXT_RELATIONS), sorted(pv.ORDEM_DA_RELACAO))

    def test_o_desempate_e_a_morada_declarada_e_nao_o_acaso(self):
        a = unidade(unit_id='TU-1', texto='primeiro')
        b = unidade(unit_id='TU-2', texto='segundo')
        escolhida, _ = pv.escolher_para_leitura([a, b])
        self.assertEqual('TU-1', escolhida['TEXT_UNIT_ID'])


class OsNomesDaC6ContinuamAResolver(unittest.TestCase):
    """MIGRACAO — mudou de forma, nao de significado."""

    def test_as_quatro_especies_da_c6_existem(self):
        self.assertEqual(
            ('NATIVE_CAPTION_ORIGINAL', 'NATIVE_CAPTION_TRANSLATED',
             'ASR_LOCAL', pv.NAO_SEI), pv.ESPECIES_DO_TEXTO)

    def test_cada_nome_composto_decompoe_se_no_par_que_sempre_foi(self):
        self.assertEqual((pv.NATIVE_CAPTION, pv.ORIGINAL),
                         pv.ESPECIE_COMPOSTA[pv.NATIVE_CAPTION_ORIGINAL])
        self.assertEqual((pv.NATIVE_CAPTION, pv.TRANSLATED),
                         pv.ESPECIE_COMPOSTA[pv.NATIVE_CAPTION_TRANSLATED])
        self.assertEqual((pv.ASR, pv.ORIGINAL),
                         pv.ESPECIE_COMPOSTA[pv.ASR_LOCAL])

    def test_serve_para_original_responde_o_mesmo_nas_duas_formas(self):
        for nome, par in pv.ESPECIE_COMPOSTA.items():
            self.assertEqual(pv.serve_para_original(nome),
                             pv.serve_para_original(par), nome)

    def test_especie_declarada_continua_a_ler_o_provedor(self):
        self.assertEqual((pv.NATIVE_CAPTION_ORIGINAL, pv.DECLARED_BY_PROVIDER),
                         pv.especie_declarada({'trackKind': 'asr'}))
        self.assertEqual((pv.NATIVE_CAPTION_TRANSLATED, pv.DECLARED_BY_PROVIDER),
                         pv.especie_declarada({'isTranslated': True}))
        self.assertEqual((pv.NAO_SEI, pv.NOT_DECLARED),
                         pv.especie_declarada({}))

    def test_o_ASR_traduzido_passa_a_ter_nome(self):
        # A razao inteira de haver dois eixos: com quatro nomes num eixo so,
        # este texto nao tinha nome nenhum.
        u = unidade(kind=pv.ASR, relation=pv.TRANSLATED, translated_from='TU-0',
                    language='en', derivation_method=pv.TRADUCAO_DA_CASA,
                    tool='whisper', unit_id='TU-1')
        self.assertEqual([], pv.conferir_unidade_de_texto(u))
        self.assertFalse(pv.serve_para_original((pv.ASR, pv.TRANSLATED)))


class OsProdutoresDeclaramAEspecie(unittest.TestCase):
    """O contrato nao fica por preencher — os produtores reais usam-no."""

    def test_o_texto_do_autor_no_bluesky_declara_se(self):
        e = env.envelope(platform='BLUESKY', native_id='x', url='u',
                         content_type='POST', route='r', executor='e',
                         run_id='R', country_scope='IT', text='ciao',
                         text_kind=pv.AUTHOR_TEXT,
                         text_kind_basis=pv.DECLARED_BY_ROUTE,
                         text_relation=pv.ORIGINAL, text_language='it',
                         text_derivation=pv.LIDO_DO_CAMPO)
        u = e[pv.CAMPO_DAS_UNIDADES][0]
        self.assertEqual(pv.AUTHOR_TEXT, u['TEXT_KIND'])
        self.assertEqual([], pv.conferir_unidades_de_texto([u]))

    def test_quem_nao_declara_produz_envelope_valido_e_UNKNOWN(self):
        # O defeito nao se apaga: passa a ver-se.
        e = env.envelope(platform='X', native_id='x', url='u',
                         content_type='POST', route='r', executor='e',
                         run_id='R', country_scope='IT', text='algo')
        self.assertEqual(pv.TEXTO_DESCONHECIDO,
                         e[pv.CAMPO_DAS_UNIDADES][0]['TEXT_KIND'])

    def test_envelope_sem_texto_nao_inventa_unidade(self):
        e = env.envelope(platform='X', native_id='x', url='u',
                         content_type='POST', route='r', executor='e',
                         run_id='R', country_scope='IT')
        self.assertEqual([], e[pv.CAMPO_DAS_UNIDADES])

    def test_as_duas_maneiras_de_declarar_nao_se_misturam(self):
        with self.assertRaises(ValueError):
            env.envelope(platform='X', native_id='x', url='u',
                         content_type='POST', route='r', executor='e',
                         run_id='R', country_scope='IT', text='a',
                         text_kind=pv.AUTHOR_TEXT,
                         text_units=[unidade()])

    def test_o_TEXT_antigo_continua_onde_estava(self):
        e = env.envelope(platform='X', native_id='x', url='u',
                         content_type='POST', route='r', executor='e',
                         run_id='R', country_scope='IT', text='ciao',
                         text_kind=pv.AUTHOR_TEXT,
                         text_kind_basis=pv.DECLARED_BY_ROUTE)
        self.assertEqual('ciao', e['TEXT'])


class ARotaDocumentalTambemTemEspecie(unittest.TestCase):
    """O produtor que a Collection ja tinha nao fica de fora do contrato."""

    def test_o_texto_de_pdf_nao_e_texto_de_autor(self):
        import orquestrador as orq
        item = orq.item_documental_para_a_porta(
            {'DERIVED_ARTIFACT_ID': 7, 'TEXTO': 'bollettino agrometeorologico',
             'RAW_ASSET_ID': 99, 'PARENT_SHA256': 'abc'}, source_id='IT-T7-001')
        self.assertEqual(pv.DOCUMENT_TEXT, item['texto_especie'])
        self.assertEqual('bollettino agrometeorologico', item['texto'])

    def test_a_linhagem_do_documento_leva_a_observacao_de_origem(self):
        import orquestrador as orq
        item = orq.item_documental_para_a_porta(
            {'DERIVED_ARTIFACT_ID': 7, 'TEXTO': 'texto', 'RAW_ASSET_ID': 99,
             'PARENT_SHA256': 'abc'}, source_id='IT-T7-001')
        lin = item[pv.CAMPO_DAS_UNIDADES][0]['LINEAGE']
        self.assertEqual(99, lin['RAW_OBSERVATION_ID'])
        self.assertEqual(pv.EXTRAIDO_DO_DOCUMENTO, lin['DERIVATION_METHOD'])
        self.assertNotEqual(pv.TEXTO_DESCONHECIDO, lin['TOOL'])


class AsMutacoesMorrem(unittest.TestCase):
    """§14 — mutar o contrato tem de ser apanhado, ou o contrato nao mede nada."""

    def test_mutar_TEXT_KIND_e_apanhado(self):
        for mau in ('CAPTION', 'caption', 'AUTHOR', '', None, 'UNKNOWN_KIND'):
            u = unidade(kind=mau)
            self.assertTrue(pv.conferir_unidade_de_texto(u),
                            'TEXT_KIND=%r passou' % mau)

    def test_mutar_TEXT_RELATION_e_apanhado(self):
        for mau in ('ORIGINAL_TEXT', 'original', 'TRANSLATION', '', None):
            u = unidade(relation=mau)
            self.assertTrue(pv.conferir_unidade_de_texto(u),
                            'TEXT_RELATION=%r passou' % mau)

    def test_mutar_a_base_e_apanhado(self):
        for mau in ('DECLARED', 'GUESSED', 'INFERRED_FROM_TEXT', '', None):
            u = unidade(kind_basis=mau)
            self.assertTrue(pv.conferir_unidade_de_texto(u),
                            'base=%r passou' % mau)

    def test_mutar_o_metodo_de_derivacao_e_apanhado(self):
        for mau in ('READ', 'OCR', '', None):
            u = unidade(derivation_method=mau)
            self.assertTrue(pv.conferir_unidade_de_texto(u),
                            'metodo=%r passou' % mau)

    def test_mutar_a_ordem_da_escolha_muda_o_que_a_porta_le(self):
        # Se trocar a ordem NAO mudasse nada, a ordem nao estaria a decidir —
        # e entao a regra seria decorativa.
        o = unidade(unit_id='TU-1', texto='original', language='it')
        t = unidade(unit_id='TU-2', texto='traducao', relation=pv.TRANSLATED,
                    translated_from='TU-1', language='en',
                    derivation_method=pv.TRADUCAO_DO_PROVEDOR, tool='x')
        real = pv.ORDEM_DA_RELACAO
        try:
            pv.ORDEM_DA_RELACAO = (pv.TRANSLATED, pv.ORIGINAL,
                                   pv.TEXTO_DESCONHECIDO)
            escolhida, _ = pv.escolher_para_leitura([o, t])
            self.assertEqual('TU-2', escolhida['TEXT_UNIT_ID'])
        finally:
            pv.ORDEM_DA_RELACAO = real
        escolhida, _ = pv.escolher_para_leitura([o, t])
        self.assertEqual('TU-1', escolhida['TEXT_UNIT_ID'])

    def test_mutar_o_UNKNOWN_para_um_valor_do_vocabulario_e_apanhado(self):
        # A promocao silenciosa, escrita como mutacao.
        u = pv.unidades_do_envelope({'TEXT': 'x', 'URL': 'u'})[0]
        u['TEXT_KIND'] = pv.AUTHOR_TEXT
        mal = pv.conferir_unidade_de_texto(u)
        self.assertTrue(any('nao tem quem a declare' in m for m in mal),
                        'promover UNKNOWN a AUTHOR_TEXT passou sem base')


if __name__ == '__main__':
    unittest.main(verbosity=2)
