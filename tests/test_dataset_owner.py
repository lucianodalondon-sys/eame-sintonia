#!/usr/bin/env python3
"""
PROVA EXECUTÁVEL DO ISOLAMENTO ENTRE DONOS DE DATASET.

Este arquivo existe porque a primeira medição do isolamento PASSOU sem provar nada:
`EARLY_SIGNAL_EAME = 12`, `CREATOR_MAP_EAME = 0`, "isolado". Com um lado vazio, qualquer
implementação passa — inclusive uma que não separe nada.

    É a mesma lição que o portão de dedupe já pagou nesta casa: `DUPLICATE_COUNT = 0` é
    verdade e POR ISSO MESMO não prova nada. Um dedupe que não faz nada passaria igual.

Então aqui o isolamento é **exercido** com os dois lados cheios, em diretório temporário,
e cada teste tenta QUEBRAR a propriedade em vez de confirmá-la:

  · carregar um dono devolve execução do outro?
  · dois escritores simultâneos perdem um ao outro?
  · o mesmo RUN_ID em dois donos passa despercebido?
  · missão não registrada vira dono errado, ou derruba a coleta?
  · o índice global derivado mistura donos ao contar?
"""
import json
import os
import shutil
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, 'scripts'))
import proveniencia as pv  # noqa: E402


def run(rid, mission, **extra):
    base = dict(PLATFORM='X', ACTOR='a', COUNTRY='ES', MISSION=mission, QUERY='q',
                ITEM_COUNT_RAW=1, STATUS='SUCCESS', RAW_EVIDENCE_STATE='NOT_APPLICABLE',
                EVIDENCE_PATH='e', SOURCE_VERSION='v')
    base.update(extra)
    return pv.novo_run(rid, **base)


class TestIsolamentoEntreDonos(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self._frag, self._man = pv.FRAGMENTOS, pv.MANIFESTO
        pv.FRAGMENTOS = os.path.join(self.tmp, 'runs')
        pv.MANIFESTO = os.path.join(self.tmp, 'RUN-MANIFEST.json')

    def tearDown(self):
        pv.FRAGMENTOS, pv.MANIFESTO = self._frag, self._man
        shutil.rmtree(self.tmp, ignore_errors=True)

    # ── os dois lados CHEIOS, que é o que a primeira medição não tinha ──────────
    def _povoar(self):
        for i in range(3):
            pv.gravar_fragmento(run('ES-%d' % i, '13-PILOTO-SENSORES-TECNICOS'))
        for i in range(4):
            pv.gravar_fragmento(run('CM-%d' % i, '14-MAPA-DE-CREATORS-EAME'))

    def test_carregar_um_dono_nunca_devolve_execucao_do_outro(self):
        self._povoar()
        early = pv.carregar_fragmentos('EARLY_SIGNAL_EAME')
        creator = pv.carregar_fragmentos('CREATOR_MAP_EAME')
        self.assertEqual(len(early), 3)
        self.assertEqual(len(creator), 4)
        self.assertFalse(set(early) & set(creator),
                         'um RUN_ID apareceu nos dois donos')
        for r in early.values():
            self.assertEqual(r['DATASET_OWNER'], 'EARLY_SIGNAL_EAME')
        for r in creator.values():
            self.assertEqual(r['DATASET_OWNER'], 'CREATOR_MAP_EAME')

    def test_isolamento_com_os_dois_lados_cheios(self):
        self._povoar()
        iso = pv.isolamento('EARLY_SIGNAL_EAME', 'CREATOR_MAP_EAME')
        self.assertTrue(iso['ISOLATED'])
        # E o teste que a medição vazia não fazia: os DOIS lados têm execução.
        self.assertGreater(iso['RUNS_A'], 0)
        self.assertGreater(iso['RUNS_B'], 0)

    def test_escritas_simultaneas_nao_se_perdem(self):
        """O defeito original, reproduzido: dois escritores, um arquivo cada."""
        import threading
        erros = []

        def escreve(pref, mission, n):
            try:
                for i in range(n):
                    pv.gravar_fragmento(run('%s-%d' % (pref, i), mission))
            except Exception as e:                            # noqa: BLE001
                erros.append(e)

        t1 = threading.Thread(target=escreve,
                              args=('ES', '13-PILOTO-SENSORES-TECNICOS', 25))
        t2 = threading.Thread(target=escreve,
                              args=('CM', '14-MAPA-DE-CREATORS-EAME', 25))
        t1.start(); t2.start(); t1.join(); t2.join()
        self.assertEqual(erros, [], 'escrita concorrente levantou exceção')
        # NENHUM dos 50 pode faltar. Era exatamente isto que o arquivo global perdia.
        self.assertEqual(len(pv.carregar_fragmentos('EARLY_SIGNAL_EAME')), 25)
        self.assertEqual(len(pv.carregar_fragmentos('CREATOR_MAP_EAME')), 25)

    def test_mesmo_run_id_em_dois_donos_e_detectado(self):
        """A mesma execução não pode ter dois proprietários — e isso tem de ser VISTO."""
        pv.gravar_fragmento(run('COLIDE', '13-PILOTO-SENSORES-TECNICOS'))
        pv.gravar_fragmento(run('COLIDE', '14-MAPA-DE-CREATORS-EAME'))
        iso = pv.isolamento('EARLY_SIGNAL_EAME', 'CREATOR_MAP_EAME')
        self.assertEqual(iso['SHARED_RUN_IDS'], ['COLIDE'])
        self.assertFalse(iso['ISOLATED'],
                         'RUN_ID em dois donos passou como isolado')

    def test_missao_nao_registrada_nao_derruba_a_coleta(self):
        """Metadado faltando não pode custar dado pago."""
        r = run('NOVA-1', '99-MISSAO-QUE-NAO-EXISTE')
        self.assertEqual(r['DATASET_OWNER'], pv.UNDECLARED_OWNER)
        caminho = pv.gravar_fragmento(r)       # grava, não levanta
        self.assertIn(pv.UNDECLARED_OWNER, caminho)
        self.assertIn(pv.UNDECLARED_OWNER, pv.donos_presentes())

    def test_pasta_manda_sobre_campo(self):
        """Editar o campo à mão não move a execução de dataset."""
        pv.gravar_fragmento(run('ES-X', '13-PILOTO-SENSORES-TECNICOS'))
        alvo = os.path.join(pv.FRAGMENTOS, 'EARLY_SIGNAL_EAME', 'ES-X.json')
        with open(alvo, encoding='utf-8') as f:
            d = json.load(f)
        d['DATASET_OWNER'] = 'CREATOR_MAP_EAME'               # mentira no campo
        with open(alvo, 'w', encoding='utf-8') as f:
            json.dump(d, f)
        lido = pv.carregar_fragmentos('EARLY_SIGNAL_EAME')['ES-X']
        self.assertEqual(lido['DATASET_OWNER'], 'EARLY_SIGNAL_EAME',
                         'o campo editado sobrepôs a pasta')
        self.assertEqual(pv.carregar_fragmentos('CREATOR_MAP_EAME'), {})

    def test_indice_global_e_derivado_e_conta_por_dono(self):
        self._povoar()
        corpo = pv.reconciliar('2026-08-30')
        self.assertEqual(corpo['RUNS_BY_OWNER'],
                         {'CREATOR_MAP_EAME': 4, 'EARLY_SIGNAL_EAME': 3})
        self.assertEqual(len(corpo['RUNS']), 7)
        # E o filtro por dono no global funciona, que é o que impede contar misturado.
        self.assertEqual(len(pv.carregar('EARLY_SIGNAL_EAME')), 3)
        self.assertEqual(len(pv.carregar('CREATOR_MAP_EAME')), 4)

    def test_fragmento_ilegivel_nao_contamina_os_outros(self):
        self._povoar()
        ruim = os.path.join(pv.FRAGMENTOS, 'EARLY_SIGNAL_EAME', 'QUEBRADO.json')
        with open(ruim, 'w', encoding='utf-8') as f:
            f.write('{ isto nao e json')
        self.assertEqual(len(pv.carregar_fragmentos('EARLY_SIGNAL_EAME')), 3)


class TestContratoDoDono(unittest.TestCase):
    def test_toda_missao_conhecida_tem_dono(self):
        self.assertEqual(pv.dono_da_missao('13-PILOTO-SENSORES-TECNICOS'),
                         'EARLY_SIGNAL_EAME')
        self.assertEqual(pv.dono_da_missao('14-MAPA-DE-CREATORS-EAME'),
                         'CREATOR_MAP_EAME')
        self.assertEqual(pv.dono_da_missao('10A-ES'), 'VOICE_ES')

    def test_dono_e_campo_obrigatorio_do_contrato(self):
        self.assertIn('DATASET_OWNER', pv.CAMPOS_RUN)

    def test_nenhuma_missao_pertence_a_dois_donos(self):
        vistas = []
        for missoes in pv.DONOS.values():
            vistas.extend(missoes)
        self.assertEqual(len(vistas), len(set(vistas)),
                         'uma missão aparece em mais de um dono')


if __name__ == '__main__':
    unittest.main()
