#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""AS 24 DISTINCOES QUE A BIBLIA NAO PODE DEIXAR DE FAZER.

    py tests/test_biblia.py

O QUE ESTE FICHEIRO TESTA — E O QUE ELE NAO TESTA
--------------------------------------------------
Ele testa a CONSTITUICAO, nao o runtime. Cada teste pergunta uma coisa so:

    a Biblia continua declarando esta distincao, com forca normativa?

Nao pergunta se a Italia ja cumpre — isso e a matriz de conformidade, e ela
mede outra coisa de proposito (LAW_STATUS != IMPLEMENTATION_STATUS).

    UMA LEI QUE SOME DE UM DOCUMENTO NAO DA ERRO EM TESTE NENHUM.

E por isso que este ficheiro existe. Ja aconteceu nesta casa: ao trazer um
ficheiro de outra branch veio junto um `PORTOES-DE-COLETA-10B.md` 54 linhas
mais curto, apagando o registo inteiro de uma verificacao adversarial. O
`git diff --stat` mostrou; se ninguem tivesse olhado, a prova teria sumido.
Documentacao apagada nao reprova nada — a nao ser que alguem a meca.

AS DISTINCOES SAO PARES, E O TESTE PROCURA OS DOIS LADOS
--------------------------------------------------------
Procurar so a palavra `FACT_TIME` acharia qualquer paragrafo que a mencione.
O teste exige a LEI (o id) e a SEPARACAO (os dois termos, ou a frase que os
separa) — senao um teste verde sobre uma lei apagada seria pior que nenhum.
"""
from __future__ import annotations

import os
import re
import sys
import unittest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)
import _gavetas  # noqa: E402,F401 — poe as gavetas do processo no caminho

BIBLIA = os.path.join(RAIZ, 'BIBLIA-CANONICA-DA-COLETA.md')
CONFORMIDADE = os.path.join(RAIZ, 'docs', 'biblia', 'CONFORMIDADE-ITALIA.md')
EMENDA = os.path.join(RAIZ, 'docs', 'biblia', 'EMENDA-V1-1.md')


def ler(p: str) -> str:
    with open(p, encoding='utf-8') as f:
        return f.read()


def corpo_da_lei(texto: str, law_id: str) -> str:
    """O bloco de UMA lei, do cabecalho dela ate o proximo cabecalho.

    Recortar a lei importa: sem isto, um termo escrito noutra parte da Biblia
    faria o teste passar sobre uma lei que ficou vazia.
    """
    m = re.search(r'^## %s · .+?$' % re.escape(law_id), texto, re.M)
    if not m:
        return ''
    resto = texto[m.end():]
    prox = re.search(r'^## COL-LAW-\d{3} · ', resto, re.M)
    return resto[:prox.start()] if prox else resto


class Distincoes(unittest.TestCase):
    """Cada teste e uma frase que o SINTONIA pagou para aprender."""

    @classmethod
    def setUpClass(cls):
        cls.t = ler(BIBLIA)
        cls.conf = ler(CONFORMIDADE)
        cls.emenda = ler(EMENDA)

    # ── ajudas ───────────────────────────────────────────────────────────
    def lei(self, law_id: str) -> str:
        c = corpo_da_lei(self.t, law_id)
        self.assertTrue(c, f'{law_id} desapareceu da Biblia')
        return c

    def separa(self, law_id: str, a: str, b: str, msg: str = ''):
        """A lei tem de nomear OS DOIS lados da distincao."""
        c = self.lei(law_id)
        for termo in (a, b):
            self.assertIn(termo, c,
                          f'{law_id} deixou de nomear «{termo}». {msg}')

    def manda(self, law_id: str):
        """Lei sem palavra normativa e conselho, nao lei."""
        c = self.lei(law_id)
        self.assertTrue(re.search(r'\*\*(DEVE|NÃO DEVE|NÃO DEVEM|DEVEM|PODE|PODEM)\*\*|'
                                  r'\b(DEVE|NÃO DEVE|NÃO DEVEM|DEVEM)\b', c),
                        f'{law_id} nao tem palavra normativa: virou prosa')
        return c

    # ── T1 · T2 — o artefato nao carrega o fato por omissao ──────────────
    def test_T1_artifact_nao_exige_fact_time(self):
        c = self.manda('COL-LAW-201')
        self.assertIn('FACT_TIME', c)
        self.assertRegex(
            c, r'NÃO DEVE ser exigido que todo RAW tenha `FACT_TIME`',
            'a dispensa explicita sumiu: sem ela volta a pressao de pendurar '
            'o tempo do fato no documento')

    def test_T2_artifact_nao_exige_fact_location(self):
        c = self.lei('COL-LAW-201')
        self.assertIn('FACT_LOCATION', c)
        self.assertIn('`UNKNOWN` é válido', c)

    # ── T3 · T4 — os dois pares que mais custaram ────────────────────────
    def test_T3_published_at_nao_e_fact_time(self):
        self.assertIn('`FACT_TIME = PUBLISHED_AT` É PROIBIDO',
                      self.lei('COL-LAW-031'))
        self.separa('COL-LAW-201', 'PUBLISHED_AT', 'FACT_TIME')

    def test_T4_source_location_nao_e_fact_location(self):
        self.assertIn('SOURCE_LOCATION ≠ FACT_LOCATION', self.lei('COL-LAW-032'))

    # ── T5 · T6 — a fonte, o endpoint e as identidades ───────────────────
    def test_T5_source_nao_e_endpoint(self):
        c = self.manda('COL-LAW-205')
        self.separa('COL-LAW-205', 'SOURCE', 'ENDPOINT')
        self.assertIn('NÃO CRIA', c, 'trocar o meio de acesso nao cria fonte nova')

    def test_T6_tres_identidades_de_fonte(self):
        c = self.lei('COL-LAW-206')
        for termo in ('SOURCE_NATIVE_ID', 'SINTONIA_STABLE_ID', 'CANONICAL_URL'):
            self.assertIn(termo, c)
        self.assertIn('NÃO DEVE', c)

    # ── T7 — as tres capacidades ─────────────────────────────────────────
    def test_T7_discover_fetch_derive(self):
        c = self.lei('COL-LAW-207')
        for cap in ('DISCOVER', 'FETCH', 'DERIVE'):
            self.assertIn(cap, c)
        self.assertIn('só uma', c, 'um executor pode implementar uma capacidade so')

    # ── T8 · T9 — o fim da corrida ───────────────────────────────────────
    def test_T8_ficheiro_na_pasta_nao_prova_corrida_terminada(self):
        c = self.lei('COL-LAW-210')
        self.assertIn('A EXISTÊNCIA DE FICHEIROS NUMA PASTA NÃO PROVA', c)

    def test_T9_complete_depende_do_fechamento(self):
        c = self.manda('COL-LAW-210')
        for e in ('RUNNING', 'PARTIAL', 'FAILED', 'COMPLETE'):
            self.assertIn(e, c)
        self.assertIn('MANIFEST COMPLETE POR ÚLTIMO', c)

    # ── T10 · T11 — a corrida lembra como foi feita ──────────────────────
    def test_T10_plan_version_e_config_hash(self):
        c = self.lei('COL-LAW-211')
        self.assertIn('PLAN_VERSION', c)
        self.assertIn('CONFIG_HASH', c)

    def test_T11_watermark_nao_e_run_finished_at(self):
        self.assertIn('`WATERMARK` NÃO É `RUN_FINISHED_AT`', self.lei('COL-LAW-212'))

    # ── T12 · T13 — o incremental ────────────────────────────────────────
    def test_T12_incremental_nao_e_so_create(self):
        c = self.lei('COL-LAW-213')
        for verbo in ('CREATE', 'UPDATE', 'DELETE', 'MERGE'):
            self.assertIn(verbo, c)

    def test_T13_ausencia_nao_prova_delete(self):
        c = self.lei('COL-LAW-213')
        self.assertIn('NÃO APARECEU NESTA CORRIDA» NÃO PROVA `DELETE`', c)

    # ── T14 — o zero ─────────────────────────────────────────────────────
    def test_T14_zero_tem_tres_palavras(self):
        c = self.lei('COL-LAW-214')
        for z in ('EXPECTED_ZERO', 'UNEXPECTED_ZERO', 'UNKNOWN_ZERO'):
            self.assertIn(z, c)

    # ── T15 · T16 — os tres eixos de confianca ───────────────────────────
    def test_T15_health_nao_e_reliability(self):
        self.separa('COL-LAW-216', 'SOURCE_HEALTH', 'SOURCE_RELIABILITY')

    def test_T16_reliability_nao_e_claim_confidence(self):
        c = self.lei('COL-LAW-216')
        self.assertIn('CLAIM_CONFIDENCE', c)
        self.assertIn('nenhum preenche o outro', self.t)

    # ── T17 · T18 — o que o mapa pode afirmar ────────────────────────────
    def test_T17_observed_exige_run(self):
        c = self.lei('COL-LAW-112')
        self.assertIn('OBSERVED', c)
        self.assertIn('RUN', c)
        self.assertIn('tem de apontar para um RUN', c)

    def test_T18_can_do_nao_vira_did_do(self):
        c = self.lei('COL-LAW-102')
        self.assertIn('CAN USE APIFY = YES', c)
        self.assertIn('NÃO** significa', c)

    # ── T19 · T20 — a historia sobrevive a normalizacao e ao dedupe ──────
    def test_T19_normalizacao_preserva_o_original(self):
        c = self.manda('COL-LAW-203')
        self.assertIn('NORMALIZAÇÃO NÃO DESTRÓI O VALOR ORIGINAL', c)
        self.assertIn('ORIGINAL_VALUE', c)

    def test_T20_dedupe_nao_destroi_source_record(self):
        c = self.manda('COL-LAW-204')
        self.assertIn('SOURCE RECORD  ≠  CANONICAL ENTITY', c)
        self.assertIn('NÃO DEVE** sobrescrever', c)

    # ── T21 — o reparo nao apaga o erro ──────────────────────────────────
    def test_T21_repair_run_nao_reescreve_a_original(self):
        c = self.manda('COL-LAW-209')
        self.assertIn('PARENT_RUN_ID', c)
        self.assertIn('O erro histórico não se apaga', c)

    # ── T22 · T23 · T24 — o mapa ─────────────────────────────────────────
    def test_T22_current_nao_se_confunde_com_target(self):
        c = self.manda('COL-LAW-050')
        # a quebra de linha do Markdown cai no meio da frase; o teste mede a
        # frase, nao a largura da coluna em que ela foi escrita.
        self.assertRegex(c, r'NÃO DEVE\*\* afirmar que ela\s+já existe')
        # e a Biblia marca como TARGET o que ainda nao existe
        self.assertIn('`TARGET`, nunca `CURRENT`', self.lei('COL-LAW-202'))

    def test_T23_system_map_continua_derivado(self):
        c = self.lei('COL-LAW-111')
        self.assertIn('saída**, nunca fonte primária', c)
        self.assertIn('NÃO DEVE** passar a ser dona', c)

    def test_T24_paridade_do_mapa_e_condicao_de_pronto(self):
        c = self.lei('COL-LAW-110')
        self.assertIn('SYSTEM MAP PARITY PASS', c)
        self.assertIn('BIBLE COMPLIANCE KNOWN', c)


class Infraestrutura(Distincoes):
    """As 21 distincoes da emenda V1.2 — GitHub, Supabase e a referencia.

    Herda de `Distincoes` so pelas ajudas (`lei`, `separa`, `manda`): a
    diferenca entre uma lei viva e um paragrafo e sempre a mesma pergunta.
    """

    # ── I1 · I2 — cada casa com o seu papel ──────────────────────────────
    def test_I1_github_e_engenharia_nao_banco(self):
        self.assertIn('QUAL ENGENHARIA ESTAVA VALENDO?', self.lei('COL-LAW-302'))
        c = self.manda('COL-LAW-303')
        self.assertIn('RUN STATE', c)
        self.assertIn('NÃO DEVEM** viver em Git', c)

    def test_I2_supabase_e_infra_nao_autoridade(self):
        c = self.lei('COL-LAW-301')
        self.assertIn('INFRASTRUCTURE  ≠  SEMANTIC AUTHORITY', c)
        self.assertIn('O QUE ACONTECEU, E COMO ESTÁ AGORA?', self.lei('COL-LAW-304'))

    # ── I3 · I4 — a tabela nao decide, e ninguem escreve por conhece-la ──
    def test_I3_estar_numa_tabela_nao_e_canonico(self):
        c = self.lei('COL-LAW-301')
        self.assertIn('TABLE           ≠  CANONICAL TRUTH', c)
        self.assertIn('SUPABASE STORES. SUPABASE DOES NOT JUDGE', self.lei('COL-LAW-305'))

    def test_I4_escrita_canonica_atravessa_o_dono(self):
        c = self.manda('COL-LAW-306')
        self.assertIn('ADMISSÃO / DONO', c)
        self.assertIn('DONO DA REFERÊNCIA', c)

    # ── I5 a I8 — a corrida e a engenharia que a produziu ────────────────
    def test_I5_commit_nao_e_corrida_observada(self):
        c = self.lei('COL-LAW-307')
        self.assertIn('`GIT COMMIT` NÃO É `OBSERVED RUN`', c)
        self.assertIn('NÃO DEVE** ser reconstruída com o código de hoje', c)

    def test_I6_I7_I8_a_corrida_preserva_as_versoes(self):
        c = self.lei('COL-LAW-307')
        for campo in ('GIT_COMMIT', 'BIBLE_VERSION', 'PIPELINE_VERSION',
                      'EXECUTOR_VERSION', 'CONFIG_HASH', 'PLAN_VERSION'):
            self.assertIn(campo, c, f'{campo} saiu do contrato da corrida')

    # ── I9 · I10 — o YAML e o relogio ────────────────────────────────────
    def test_I9_action_nao_e_orquestrador(self):
        c = self.manda('COL-LAW-309')
        self.assertIn('YAML NÃO É UM SEGUNDO ORQUESTRADOR', c)
        self.assertIn('COL-LAW-011', c, 'a lei tem de apontar para o dono da orquestracao')

    def test_I10_agenda_nao_e_politica(self):
        c = self.lei('COL-LAW-310')
        self.assertIn('SCHEDULE  ≠  COLLECTION POLICY', c)
        for modo in ('PONTUAL', 'INCREMENTAL', 'TOTAL'):
            self.assertIn(modo, c)

    # ── I11 · I12 — a migration ──────────────────────────────────────────
    def test_I11_migration_e_versionada(self):
        c = self.manda('COL-LAW-308')
        self.assertIn('migration versionada em Git', c)

    def test_I12_ficheiro_de_migration_nao_prova_estado_aplicado(self):
        c = self.lei('COL-LAW-308')
        self.assertIn('NÃO prova que ela foi aplicada', c)
        self.assertIn('INFRASTRUCTURE_DRIFT', c)
        self.assertIn('NÃO É**\n`WORLD UNKNOWN`', c.replace('\r', ''))

    # ── I13 — bytes e metadata ───────────────────────────────────────────
    def test_I13_bytes_nao_sao_metadata(self):
        c = self.manda('COL-LAW-311')
        self.assertIn('O CAMINHO É ENDEREÇO, NUNCA IDENTIDADE', c)
        self.assertIn('SHA256', c)
        self.assertIn('NÃO decreta onde os bytes ficam', c)

    # ── I14 a I16 — a referencia ─────────────────────────────────────────
    def test_I14_referencia_nao_e_configuracao(self):
        c = self.lei('COL-LAW-401')
        self.assertIn('REFERENCE DATA', c)
        self.assertIn('sem deploy', c)
        self.assertIn('commit versionado', c)

    def test_I15_conferir_nao_e_mudar(self):
        c = self.lei('COL-LAW-404')
        self.assertIn('`LAST_CHECKED` ≠ `LAST_CHANGED`', c)
        self.assertIn('NEXT_DUE', c)

    def test_I16_a_referencia_tem_validade_temporal(self):
        c = self.manda('COL-LAW-405')
        self.assertIn('VALID_FROM', c)
        self.assertIn('VALID_TO', c)
        self.assertIn('REFERENCE AS OF FACT_TIME', c)

    # ── I17 — portabilidade sem abstracao prematura ──────────────────────
    def test_I17_conceito_nao_e_tabela_fisica(self):
        c = self.lei('COL-LAW-315')
        self.assertIn('conceitos **do SINTONIA**', c)
        self.assertIn('NÃO AUTORIZA ABSTRAÇÃO PREMATURA', c)

    # ── I18 — segredo ────────────────────────────────────────────────────
    def test_I18_segredo_nao_entra_no_estado_do_mapa(self):
        c = self.manda('COL-LAW-312')
        self.assertIn('estado do System Map', c)
        self.assertIn('Nunca o valor', c)

    # ── I19 · I20 — o mapa ───────────────────────────────────────────────
    def test_I19_infra_e_infra_no_mapa(self):
        c = self.lei('COL-LAW-316')
        self.assertIn('nunca como fonte de', c)
        self.assertIn('A arquitetura governa o visual', c)

    def test_I20_current_nao_recebe_aresta_inventada(self):
        """A V1.2 nao pode desenhar como CURRENT o que ela mesma mediu como ABSENT."""
        self.assertIn('NÃO EXISTE hoje', self.lei('COL-LAW-401')[:0] or self.t
                      [self.t.index('PARTE XIX'):self.t.index('COL-LAW-401')])
        self.assertIn('não** o desenha como `CURRENT`',
                      self.t[self.t.index('PARTE XIX'):self.t.index('COL-LAW-401')])

    # ── I21 — deploy ─────────────────────────────────────────────────────
    def test_I21_deploy_nao_decide_verdade_do_dado(self):
        c = self.lei('COL-LAW-314')
        for x in ('CODE DEPLOYMENT', 'DATA STATE', 'REFERENCE VERSION', 'RUN STATE'):
            self.assertIn(x, c)


class Integridade(unittest.TestCase):
    """A emenda tem de bater com o corpo da Biblia."""

    @classmethod
    def setUpClass(cls):
        cls.t = ler(BIBLIA)
        cls.emenda = ler(EMENDA)
        cls.emenda2 = ler(os.path.join(RAIZ, 'docs', 'biblia', 'EMENDA-V1-2.md'))
        cls.conf = ler(CONFORMIDADE)
        cls.censo_infra = ler(os.path.join(RAIZ, 'docs', 'biblia',
                                           'CENSO-DA-INFRAESTRUTURA.md'))

    def test_versao_bate_com_o_historico(self):
        # ⚠️ ISTO JA FOI UM LITERAL CRAVADO (`V1.3`), e um literal cravado
        # convida a ser editado para o teste ficar verde — que e exactamente o
        # contrario do que a COL-LAW-069 quer. Agora a versao declarada e
        # COMPARADA com a ultima linha do historico constitucional: subir a
        # versao sem registar a emenda passa a ser impossivel, e registar a
        # emenda sem subir a versao tambem.
        historico = re.findall(r'^\| \*\*(V[\d.]+)\*\* \|', self.t, re.M)
        self.assertTrue(historico, 'o historico constitucional desapareceu')
        declarada = re.search(r'VERSION\s+(V[\d.]+)', self.t).group(1)
        self.assertEqual(declarada, historico[-1],
                         'a VERSION declarada nao e a ultima emenda registada')
        for v in ('V1', 'V1.1', 'V1.2', 'V1.3'):
            self.assertIn(v, historico, f'{v} sumiu do historico constitucional')

    def test_a_lei_da_infra_nasceu_de_medicao(self):
        """Lei de infraestrutura escrita sem censo e opiniao com cara de lei."""
        self.assertIn('ZERO', self.censo_infra)
        self.assertIn('caminhos de escrita medidos', self.censo_infra)
        self.assertIn('CENSO-DA-INFRAESTRUTURA.md', self.t)

    def test_toda_lei_da_v1_2_existe_na_biblia(self):
        na_biblia = set(re.findall(r'^## (COL-LAW-\d{3}) · ', self.t, re.M))
        citadas = set(re.findall(r'`(COL-LAW-[34]\d{2})`', self.emenda2))
        self.assertTrue(citadas, 'a emenda V1.2 deixou de citar leis')
        self.assertEqual(set(), citadas - na_biblia,
                         'a emenda V1.2 cita lei que a Biblia nao tem')

    def test_toda_lei_da_emenda_existe_na_biblia(self):
        na_biblia = set(re.findall(r'^## (COL-LAW-\d{3}) · ', self.t, re.M))
        na_emenda = set(re.findall(r'`(COL-LAW-[12]\d{2})`', self.emenda))
        self.assertTrue(na_emenda, 'a emenda deixou de citar leis')
        self.assertEqual(set(), na_emenda - na_biblia,
                         'a emenda cita lei que a Biblia nao tem')

    def test_nenhuma_lei_da_v1_foi_apagada(self):
        """A V1 congelou 48 leis. Emenda que apaga lei antiga nao e emenda."""
        na_biblia = set(re.findall(r'^## (COL-LAW-\d{3}) · ', self.t, re.M))
        v1 = {x for x in na_biblia if int(x[-3:]) < 100}
        self.assertEqual(48, len(v1),
                         f'a V1 tinha 48 leis e agora ha {len(v1)}: '
                         'alguma foi apagada ou renumerada')

    def test_not_applicable_nao_conta_como_divida(self):
        """Lei que nao se aplica nao e falha — e o placar tem de dizer isso."""
        self.assertIn('NOT_APPLICABLE', self.conf)
        self.assertIn('não é `ABSENT`', self.conf)


if __name__ == '__main__':
    r = unittest.main(exit=False, verbosity=1).result
    ok = r.wasSuccessful()
    print('\nTESTES_BIBLIA=%s · %d testes' % ('PASS' if ok else 'FAIL', r.testsRun))
    raise SystemExit(0 if ok else 1)
