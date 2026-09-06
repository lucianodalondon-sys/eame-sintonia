#!/usr/bin/env python3
"""LEITOR CANÔNICO DE RÓTULOS — o mais novo e portado vence o mais velho e menor.

O defeito que este arquivo torna impossível de repetir: um enxerto trouxe um artefato de
**30/08/2026** com **90 pares** cultura × alvo e ele foi apresentado como estado da arte,
ao lado de um leitor de **04/09/2026** que já tinha passado portão com gabarito lido à mão.

    OLDER_SMALLER_READER != CANONICAL_READER
    NEW_MERGE_CANNOT_DOWNGRADE_GATED_READING

**A primeira versão deste arquivo contava e nada mais.** Sete mutações passavam por ele:
trocar as doze linhas não cobertas por lixo mantendo o comprimento, esvaziar a lista de
campos exclusivos, falsificar o método, apagar o portão do repositório. Aqui cada afirmação
é RECOMPUTADA a partir dos dois conjuntos, e o portão é ABERTO em vez de citado.
"""
import datetime
import glob
import json
import os
import re
import sys
import unicodedata
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'scripts'))

LEGADO = os.path.join(ROOT, 'data', 'samples', 'IT-T4-001',
                      'ITALY-ADAMA-REGULATORY-INTELLIGENCE.json')
CANONICO = os.path.join(ROOT, 'data', 'samples', 'IT-ROTULOS-V1', 'IT-ROTULOS-PARES-V3.json')
PORTAO = os.path.join(ROOT, 'data', 'samples', 'IT-ROTULOS-V1', 'IT-ROTULOS-PORTAO-V1.json')
PILOTO = os.path.join(ROOT, 'docs', 'piloto', 'SINTONIA-ITALIA-PILOTO.md')

TEM_OS_DOIS = os.path.exists(LEGADO) and os.path.exists(CANONICO)


def _j(p):
    with open(p, encoding='utf-8') as f:
        return json.load(f)


def _up(v):
    return ''.join(c for c in unicodedata.normalize('NFD', str(v or ''))
                   if unicodedata.category(c) != 'Mn').upper().strip()


@unittest.skipUnless(TEM_OS_DOIS, 'os dois leitores precisam estar versionados')
class TestOLegadoNaoTemAutoridade(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.legado = _j(LEGADO)
        cls.canon = _j(CANONICO)
        cls.dec = cls.legado['LEITOR_CANONICO_DA_CASA']

    def test_o_legado_se_declara_legado(self):
        self.assertEqual('LEGACY_READER / HISTORICAL_INPUT', self.dec['ESTE_ARTEFACTO'])
        self.assertEqual('NO', self.dec['CANONICAL_AUTHORITY'])

    def test_as_duas_leis_estao_escritas(self):
        self.assertIn('OLDER_SMALLER_READER != CANONICAL_READER', self.dec['LEI'])
        self.assertIn('NEW_MERGE_CANNOT_DOWNGRADE_GATED_READING', self.dec['LEI'])

    def test_a_regua_plana_de_cobertura_morreu_tambem_aqui(self):
        """`LABEL_COVERAGE: 163/163 (100%)` media download e era lido como leitura."""
        cob = self.legado['LABEL_COVERAGE']
        self.assertIsInstance(cob, dict, 'a régua plana voltou como string')
        self.assertTrue(cob.get('DEPRECATED'))

    def test_o_canonico_e_mesmo_o_mais_novo(self):
        d = datetime.date.fromisoformat
        self.assertLess(d(self.legado['CAPTURED_AT']), d(self.canon['CAPTURED_AT']))
        self.assertEqual(d(self.dec['LEITOR_CANONICO']['CAPTURED_AT']),
                         d(self.canon['CAPTURED_AT']))

    def test_o_canonico_e_maior_NA_REGUA_CERTA(self):
        """2.928 contra 90 compara réguas diferentes, e a casa já disse isso.

        `IT-ROTULOS-COBERTURA-V2` escreve: «o conjunto antigo conta o LITERAL do alvo
        e o novo conta CLASSE canônica. Somar os dois seria comparar réguas
        diferentes.» A conclusão sobrevive na régua honesta — rótulos com par —,
        e é essa que este teste usa.
        """
        c = self.dec['COMPARACAO_CAMPO_A_CAMPO']
        canon_rot = len({p['REGISTRATION_ID'] for p in self.canon['PAIRS']})
        legado_rot = len({u['REGISTRATION_ID'] for u in self.legado['AUTHORIZED_USE_ROWS']})
        self.assertEqual(canon_rot, c['ROTULOS_DO_CANONICO'])
        self.assertEqual(legado_rot, c['ROTULOS_DO_LEGADO'])
        self.assertGreater(canon_rot, legado_rot,
                           'na régua de rótulos o canônico não é maior — reabrir a decisão')
        # E na régua de pares (CROP,TARGET), que é a que o legado usa.
        canon_pares = len({(_up(p['CROP']), _up(p['TARGET'])) for p in self.canon['PAIRS']})
        self.assertGreater(canon_pares, self.legado['DISTINCT_CROP_TARGET_PAIRS'])

    def test_o_conjunto_canonico_nao_pode_ser_enchimento(self):
        """2.928 linhas iguais não são 2.928 pares. Diversidade é medida."""
        pares = self.canon['PAIRS']
        self.assertEqual(len(pares), self.canon['SUPPORTED_PAIRS'])
        triplas = {(p['REGISTRATION_ID'], _up(p['CROP']), _up(p['TARGET'])) for p in pares}
        self.assertEqual(len(triplas), len(pares), 'há par duplicado no conjunto canônico')
        self.assertGreaterEqual(len({_up(p['CROP']) for p in pares}), 20)
        self.assertGreaterEqual(len({_up(p['TARGET']) for p in pares}), 20)


@unittest.skipUnless(os.path.exists(PORTAO), 'portão não versionado')
class TestOPortaoEAbertoENaoCitado(unittest.TestCase):
    """`PORTAO = 'IT-ROTULOS-PORTAO-V1 = PASS'` era uma string num dicionário.

    Apagar o artefato do repositório não reprovava nada, e trocar PASS por FAIL
    também não. O portão é a justificação de carga da decisão inteira.
    """

    @classmethod
    def setUpClass(cls):
        cls.p = _j(PORTAO)

    def test_o_portao_passa_e_cada_check_passa(self):
        self.assertEqual('PASS', self.p['RESULT'])
        self.assertTrue(self.p['CHECKS'], 'portão sem checks')
        for nome, c in self.p['CHECKS'].items():
            with self.subTest(check=nome):
                self.assertTrue(c['PASSA'], '%s reprovou' % nome)

    def test_cada_limiar_numerico_e_realmente_satisfeito(self):
        for nome in ('PRECISION', 'RECALL'):
            c = self.p['CHECKS'][nome]
            with self.subTest(check=nome):
                self.assertGreaterEqual(c['VALOR'], c['LIMIAR'])
        for nome in ('EXPECTED_NO_PAIR_VIOLATIONS', 'AMBIGUOUS_PROMOTED_TO_PAIR'):
            c = self.p['CHECKS'][nome]
            with self.subTest(check=nome):
                self.assertLessEqual(c['VALOR'], c['LIMIAR'])

    def test_o_portao_declara_o_que_ele_NAO_mediu(self):
        """Um portão que esconde a própria cobertura não é um portão."""
        self.assertIn('RESSALVA_DE_COBERTURA', self.p,
                      'o portão perdeu a ressalva de cobertura do gabarito')
        self.assertRegex(self.p['RESSALVA_DE_COBERTURA'], r'30 dos 163')
        self.assertIn('QUANDO_FOI_ESCRITO', self.p['PORTAO'],
                      'o portão deixou de dizer quando os limiares foram escritos')


@unittest.skipUnless(TEM_OS_DOIS, 'os dois leitores precisam estar versionados')
class TestOQueOLegadoAINDATem(unittest.TestCase):
    """Sem autoridade não quer dizer sem valor. Mas o que ele tem entra como CANDIDATO."""

    @classmethod
    def setUpClass(cls):
        cls.legado = _j(LEGADO)
        cls.canon = _j(CANONICO)
        cls.dec = cls.legado['LEITOR_CANONICO_DA_CASA']
        cls.so = cls.dec['O_QUE_ESTE_ARTEFACTO_TEM_E_O_CANONICO_NAO']

    def _recomputa(self):
        culturas = {}
        for p in self.canon['PAIRS']:
            culturas.setdefault(p['REGISTRATION_ID'], set()).add(_up(p['CROP']))
        cobertas, nao = set(), set()
        for u in self.legado['AUTHORIZED_USE_ROWS']:
            reg = u['REGISTRATION_ID']
            c = _up(u.get('CROP_TERM_MATCHED') or u.get('CROP'))
            g = culturas.get(reg, set())
            (cobertas if c and (c in g or c.split()[0] in g) else nao).add((reg, c))
        return cobertas, nao

    def test_o_conjunto_nao_coberto_e_recomputado_e_nao_aceito(self):
        """Trocar as linhas por lixo mantendo o comprimento passava antes."""
        _, nao = self._recomputa()
        declarado = {(r['REGISTRATION_ID'], r['CROP_LEGADO'])
                     for r in (self.so['LINHAS_NAO_COBERTAS']
                               + self.so['DEFEITO_CONHECIDO_DO_LEGADO'])}
        self.assertEqual(nao, declarado,
                         'a lista de linhas não cobertas não é a que os dois arquivos dão')

    def test_a_contagem_de_culturas_bate_com_a_recomputacao(self):
        cobertas, nao = self._recomputa()
        c = self.dec['COMPARACAO_CAMPO_A_CAMPO']
        linhas = self.legado['AUTHORIZED_USE_ROWS']
        cob = sum(1 for u in linhas
                  if (u['REGISTRATION_ID'],
                      _up(u.get('CROP_TERM_MATCHED') or u.get('CROP'))) in cobertas)
        self.assertEqual(cob, c['CROP_PRESENTE_NO_CANONICO'])
        self.assertEqual(len(linhas), c['LINHAS_DE_USO_DO_LEGADO'])
        self.assertEqual(len({(u['REGISTRATION_ID'],
                               _up(u.get('CROP_TERM_MATCHED') or u.get('CROP')))
                              for u in linhas}),
                         c['SLOTS_DISTINTOS_CULTURA_x_ROTULO'])

    def test_subsumido_diz_CULTURA_e_nao_finge_dizer_USO(self):
        """«37 de 49» lia-se como usos reproduzidos. Nenhum alvo é reproduzido."""
        c = self.dec['COMPARACAO_CAMPO_A_CAMPO']
        alvos = {}
        for p in self.canon['PAIRS']:
            alvos.setdefault((p['REGISTRATION_ID'], _up(p['CROP'])), set()).add(_up(p['TARGET']))
        triplas = {(u['REGISTRATION_ID'], _up(u.get('CROP_TERM_MATCHED') or u.get('CROP')), _up(t))
                   for u in self.legado['AUTHORIZED_USE_ROWS'] for t in u['TARGETS']}
        rep = sum(1 for reg, cr, t in triplas
                  if t in alvos.get((reg, cr), set())
                  or t in alvos.get((reg, cr.split()[0] if cr else ''), set()))
        self.assertEqual(rep, c['USE_ROWS_COM_ALVO_REPRODUZIDO'])
        self.assertEqual(len(triplas), c['TRIPLAS_REG_CROP_TARGET_DO_LEGADO'])
        self.assertIn('CULTURA', c['O_QUE_SUBSUMIDO_QUER_DIZER'])

    def test_o_defeito_conhecido_do_legado_nao_volta_como_candidato(self):
        """`Riso` saiu de dentro do nome de uma erva daninha, num glifosato."""
        defeito = self.so['DEFEITO_CONHECIDO_DO_LEGADO']
        self.assertEqual({('018270', 'RISO'), ('018271', 'RISO'),
                          ('018277', 'RISO'), ('018279', 'RISO')},
                         {(r['REGISTRATION_ID'], r['CROP_LEGADO']) for r in defeito})
        for r in defeito:
            with self.subTest(reg=r['REGISTRATION_ID']):
                self.assertEqual('KNOWN_DEFECT / DO_NOT_REPROCESS', r['CLASSE'])
        for r in self.so['LINHAS_NAO_COBERTAS']:
            self.assertEqual('CANDIDATE_INPUT_TO_CANONICAL_READER', r['CLASSE'])
        self.assertIn('AUTORIDADE', self.so['NAO_E'])

    def test_os_campos_exclusivos_sao_sete_e_exclusivos_de_verdade(self):
        """Uma lista vazia fazia zero asserções e passava."""
        campos = self.so['CAMPOS_EXCLUSIVOS']
        self.assertEqual(7, len(campos), 'a lista de campos exclusivos mudou de tamanho')
        do_legado = set()
        for r in self.legado['AUTHORIZED_USE_ROWS']:
            do_legado |= set(r)
        do_canon = set()
        for p in self.canon['PAIRS']:
            do_canon |= set(p)
        for campo in campos:
            with self.subTest(campo=campo):
                self.assertIn(campo, do_legado)
                self.assertNotIn(campo, do_canon)

    def test_o_metodo_descreve_o_que_o_codigo_faz(self):
        """Dizia «traduzida EN->IT» e não há tradução nenhuma."""
        metodo = self.dec['COMPARACAO_CAMPO_A_CAMPO']['METODO']
        self.assertIn('CROP_TERM_MATCHED', metodo)
        self.assertNotRegex(metodo, r'(?i)traduzid[ao]\s+EN')


@unittest.skipUnless(TEM_OS_DOIS, 'os dois leitores precisam estar versionados')
class TestScaphoideusENenhumDosDoisResolveOGenero(unittest.TestCase):
    """A afirmação de que o canônico «resolve» a limitação do legado era grande demais.

    O legado diz que o dicionário é espanhol e não cobre `Scaphoideus`. O canônico
    não resolve isso — ele **contorna**, publicando a CLASSE `CICALINE` e deixando
    `TAXONOMIC_STATUS = UNKNOWN` em quase todos os pares. O que existe de verdade é
    a citação literal do rótulo, e ela é anterior aos dois.
    """

    def test_o_canonico_carrega_a_frase_mas_nao_a_especie(self):
        canon = _j(CANONICO)
        alvo_exato = [p for p in canon['PAIRS'] if 'SCAPHOIDEUS' in _up(p['TARGET'])]
        self.assertEqual([], alvo_exato,
                         'o canônico passou a publicar a espécie: reescrever esta prova')
        na_prosa = [p for p in canon['PAIRS']
                    if 'scaphoideus' in json.dumps(p, ensure_ascii=False).lower()]
        self.assertTrue(na_prosa, 'a citação do rótulo sumiu do canônico')
        for p in na_prosa:
            with self.subTest(reg=p['REGISTRATION_ID']):
                self.assertIn('scaphoideus', p['TARGET_AS_WRITTEN'].lower())

    def test_o_legado_declara_a_limitacao_e_ela_continua_de_pe(self):
        legado = _j(LEGADO)
        self.assertIn('Scaphoideus', legado['COVERAGE_IS_A_FLOOR'])


class TestNenhumDocumentoVendeOLeitorVelhoComoEstadoDaArte(unittest.TestCase):
    """Antes, um parágrafo que dizia o OPOSTO passava: os três regexes casavam."""

    LIMPOS = ('build/', 'PREVIOUS-HANDOFF')

    def _docs_que_citam_os_90(self):
        fora = []
        for padrao in ('docs/**/*.md', 'research/**/*.md', '*.md'):
            for c in glob.glob(os.path.join(ROOT, padrao), recursive=True):
                rel = os.path.relpath(c, ROOT)
                if any(x in rel for x in self.LIMPOS):
                    continue
                with open(c, encoding='utf-8', errors='replace') as f:
                    txt = f.read()
                if re.search(r'90\s+pares|DISTINCT_CROP_TARGET_PAIRS', txt):
                    fora.append((rel, txt))
        return fora

    def test_todo_documento_que_cita_os_90_diz_que_eles_nao_sao_o_canonico(self):
        docs = self._docs_que_citam_os_90()
        self.assertTrue(docs, 'nenhum documento cita os 90 pares — a varredura não provou nada')
        for rel, txt in docs:
            with self.subTest(documento=rel):
                self.assertRegex(
                    txt, r'IT-ROTULOS-PARES-V3',
                    'cita os 90 pares sem nomear o leitor canônico')
                self.assertRegex(
                    txt, r'(?i)LEGACY_READER|leitor canónico|leitor canônico',
                    'cita os 90 pares sem dizer que eles não são o estado da arte')

    def test_nenhum_documento_promove_o_leitor_velho_de_volta(self):
        """A ERRATA que inverte a decisão passava por conter as três palavras."""
        for rel, txt in self._docs_que_citam_os_90():
            with self.subTest(documento=rel):
                self.assertNotRegex(
                    txt,
                    r'(?i)IT-ROTULOS-PARES-V3[^.\n]{0,80}(?:RETIRAD|LEGACY_READER|'
                    r'n[aã]o\s+[eé]\s+o\s+leitor)',
                    'um documento declara o leitor canônico como legado')


class TestOGeradorEQuemDizALei(unittest.TestCase):
    """Lei que vive só no arquivo gerado é apagada na próxima execução."""

    @unittest.skipUnless(TEM_OS_DOIS, 'os dois leitores precisam estar versionados')
    def test_o_gerador_reproduz_o_bloco_publicado(self):
        import italia_reg_intelligence as ri
        legado = _j(LEGADO)
        self.assertEqual(legado['LEITOR_CANONICO_DA_CASA'],
                         ri.leitor_canonico(legado['AUTHORIZED_USE_ROWS'],
                                            legado['CROP_TARGET_PAIRS']),
                         'gerador e artefato discordam: a correção some na próxima rodada')

    def test_o_gerador_nao_publica_mais_a_regua_plana(self):
        import italia_reg_intelligence as ri
        self.assertTrue(ri._cobertura_plana_depreciada(163)['DEPRECATED'])

    def test_o_pipeline_de_entrega_tambem_sabe_que_a_camada_e_legado(self):
        """`CANONICAL_AUTHORITY = NO` só valia dentro do ficheiro que o dizia.

        O pipeline que produz o pacote entregue continuava a sourcear o leitor de 90
        pares como autoridade única e a carimbá-lo `REAL_FACT`. Uma demissão que só
        vale dentro do ficheiro demitido não vale.
        """
        caminho = os.path.join(ROOT, 'scripts', 'pacote_normalizar.py')
        if not os.path.exists(caminho):
            self.skipTest('pipeline de entrega ausente')
        with open(caminho, encoding='utf-8') as f:
            fonte = f.read()
        self.assertIn('LEITOR_CANONICO_DA_CASA', fonte,
                      'o pacote entregue não diz que a camada vem do leitor legado')
        self.assertIn('IT-ROTULOS-PARES-V3', fonte)
        self.assertNotRegex(
            fonte, r'E a UNICA classe que liga cultura a alvo',
            'o pacote volta a dizer que os 90 pares são a única classe da casa')

    def test_o_gerador_conhece_o_defeito_conhecido(self):
        import italia_reg_intelligence as ri
        self.assertEqual(4, len(ri.DEFEITO_CONHECIDO_DO_LEGADO))


if __name__ == '__main__':
    unittest.main(verbosity=2)
