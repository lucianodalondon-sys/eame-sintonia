#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
C10.2 — O QUE A PORTA CHAMA DE «ORIGEM».

O contrato foi determinado por prova, e nao por preferencia:

    ORIGIN_GATE = PROCEDENCIA CONFERIVEL,  nao identidade canonica.

Tres leituras independentes dizem o mesmo, e a terceira fecha o assunto:

  1. o motivo que o proprio portao escreve — «nao se consegue CONFERIR DEPOIS»;
  2. a companhia dele — «Prontidao DOCUMENTAL: da para ler, sabe de onde veio,
     sabe de que original nasceu»;
  3. `pronto_para_inteligencia` monta o `SOURCE_ID` de saida a partir de
     `source_id` ou `fonte` e DEIXA `url` DE FORA. Se o portao fosse de
     identidade, a saida partilharia a cadeia dele. Nao partilha.

Logo um endereco PODE responder a esta pergunta. O que ele nao pode e virar
identidade.

    UMA URL PROVA UM ENDERECO. UMA URL NAO CRIA SOURCE_ID.
"""
import ast
import io
import os
import sys
import unittest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for p in ('admissao', 'guarda', ''):
    sys.path.insert(0, os.path.join(RAIZ, p) if p else RAIZ)

import admissao as ad            # noqa: E402
import preservar_coleta as pc    # noqa: E402

URL = 'https://www.instagram.com/reel/C-FanW_CYMz/'
ID = 'IG-CANAL-0042'


class OContratoLeSeNoCodigo(unittest.TestCase):
    """A prova que decide entre «identidade» e «procedencia»."""

    def test_a_fronteira_de_saida_nao_deixa_o_endereco_virar_source_id(self):
        # ESTE E O TESTE QUE PROVA O CONTRATO. Se um dia `url` entrar nesta
        # cadeia, o portao passa a ser de identidade e a §9 foi quebrada.
        item = {'id': 'x', 'texto': 'ensaio de campo com DOI', 'url': URL,
                'fact_time': '2026-05-02'}
        d = ad.decidir(item, 'T7', corrida='c10-2')
        if d.resultado != ad.SIM:
            item['texto'] = 'ensaio de campo publicado com DOI e revisao por pares'
            d = ad.decidir(item, 'T7', corrida='c10-2')
        self.assertEqual(d.resultado, ad.SIM, d.motivo)
        saida = ad.pronto_para_inteligencia(item, d)
        self.assertEqual(saida['SOURCE_ID'], 'NAO SEI',
                         'o endereco entrou no SOURCE_ID de saida')
        self.assertNotIn('instagram.com', str(saida['SOURCE_ID']))

    def test_o_portao_vive_entre_as_perguntas_de_prontidao(self):
        rotulos = [r for r, _f in ad.perguntas_do_estagio(ad.DOCUMENTO)]
        self.assertEqual(rotulos, ['legivel', 'origem', 'linhagem'])


class UmaConfissaoNaoEUmaOrigem(unittest.TestCase):
    """O defeito central, e o pior caso dele."""

    def test_nenhuma_das_seis_confissoes_passa_sozinha(self):
        for palavra in sorted(pc.SENTINELAS):
            r, _m, ev = ad._tem_origem({'source_id': palavra})
            self.assertEqual(r, ad.NAO_SEI,
                             '«%s» passou por origem declarada' % palavra)
            self.assertEqual(ev, {})

    def test_o_pior_caso_confissao_sem_endereco_nenhum(self):
        # Antes desta missao isto devolvia SIM com evidencia «NAO SEI»: nao
        # havia NADA para conferir depois, e o portao dizia que havia.
        r, _m, _ev = ad._tem_origem({'source_id': 'NAO SEI'})
        self.assertEqual(r, ad.NAO_SEI)

    def test_a_confissao_nao_ofusca_o_endereco_que_responde(self):
        # A cadeia de `or` parava na confissao e o URL nunca chegava ao livro.
        r, _m, ev = ad._tem_origem({'source_id': 'NAO SEI', 'url': URL})
        self.assertEqual(r, ad.SIM)
        self.assertEqual(ev['origem'], URL)
        self.assertEqual(ev['origem_especie'], 'SOURCE_URL')

    def test_campo_vazio_ou_so_espacos_tambem_nao_e_origem(self):
        for vazio in ('', '   ', None):
            r, _m, _ev = ad._tem_origem({'source_id': vazio})
            self.assertEqual(r, ad.NAO_SEI, repr(vazio))


class AEspecieFicaEscrita(unittest.TestCase):
    """Quem ler o livro tem de distinguir identidade de endereco."""

    def test_identidade_e_endereco_saem_com_nome_diferente(self):
        _r, _m, a = ad._tem_origem({'source_id': ID})
        _r, _m, b = ad._tem_origem({'url': URL})
        self.assertEqual(a['origem_especie'], 'SOURCE_ID')
        self.assertEqual(b['origem_especie'], 'SOURCE_URL')
        self.assertNotEqual(a['origem_especie'], b['origem_especie'])

    def test_a_identidade_ganha_do_endereco_quando_existem_as_duas(self):
        _r, _m, ev = ad._tem_origem({'source_id': ID, 'url': URL})
        self.assertEqual(ev['origem'], ID)
        self.assertEqual(ev['origem_especie'], 'SOURCE_ID')

    def test_o_endereco_nunca_sobe_por_cima_de_uma_identidade_real(self):
        _r, _m, ev = ad._tem_origem({'source_id': ID, 'url': 'https://outro/'})
        self.assertEqual(ev['origem'], ID)

    def test_o_motivo_do_endereco_diz_que_isto_nao_e_identity_state(self):
        _r, motivo, _ev = ad._tem_origem({'url': URL})
        self.assertIn('IDENTITY_STATE', motivo)


class OQueNaoEOrigem(unittest.TestCase):
    """Nem tudo o que identifica um item identifica a origem dele."""

    def test_post_id_sha_e_caminho_nao_sao_origem(self):
        for campo, valor in (('post_id', 'C-FanW_CYMz'),
                             ('sha256', 'a' * 64),
                             ('storage_path', 'data/raw/x.m4a'),
                             ('parent_artifact_id', 'RAW-4fe5e6be5c580c42')):
            r, _m, _ev = ad._tem_origem({campo: valor})
            self.assertEqual(r, ad.NAO_SEI, campo)


class AGrafiaDoContratoDoColetor(unittest.TestCase):
    """O portao media a grafia, e nao a origem."""

    def test_o_portao_ve_a_grafia_que_o_coletor_declara(self):
        # `coleta/ingresso.DO_COLETOR` declara SOURCE_ID e SOURCE_URL em
        # MAIUSCULAS. Antes desta missao o portao so lia minusculas, e um item
        # que declarava a origem pelo contrato da casa levava NAO_SEI.
        r, _m, ev = ad._tem_origem({'SOURCE_ID': ID})
        self.assertEqual(r, ad.SIM)
        self.assertEqual(ev['origem_especie'], 'SOURCE_ID')
        r, _m, ev = ad._tem_origem({'SOURCE_URL': URL})
        self.assertEqual(r, ad.SIM)
        self.assertEqual(ev['origem_especie'], 'SOURCE_URL')

    def test_as_duas_grafias_da_identidade_estao_declaradas(self):
        self.assertIn('SOURCE_ID', ad.IDENTIDADE_DA_FONTE)
        self.assertIn('source_id', ad.IDENTIDADE_DA_FONTE)
        self.assertIn('url', ad.ENDERECO_DA_OBSERVACAO)
        self.assertIn('SOURCE_URL', ad.ENDERECO_DA_OBSERVACAO)

    def test_nenhum_campo_de_endereco_entrou_na_lista_da_identidade(self):
        cruzados = set(ad.IDENTIDADE_DA_FONTE) & set(ad.ENDERECO_DA_OBSERVACAO)
        self.assertEqual(cruzados, set(),
                         'um campo esta nas duas listas: a porta deixou de '
                         'distinguir identidade de endereco')


class OCasoRealDoReel(unittest.TestCase):
    """O Reel da C10.1: SOURCE_ID desconhecido, SOURCE_URL valida."""

    ITEM = {'id': 'C-FanW_CYMz', 'texto': 'Buongiorno appassionati di mais',
            'artifact_type': 'DERIVED',
            'parent_artifact_id': 'RAW-4fe5e6be5c580c42',
            'source_id': 'NAO SEI', 'url': URL}

    def test_passa_a_origem_pelo_endereco_e_diz_que_foi_pelo_endereco(self):
        r, _m, ev = ad._tem_origem(self.ITEM)
        self.assertEqual(r, ad.SIM)
        self.assertEqual(ev['origem_especie'], 'SOURCE_URL')
        self.assertEqual(ev['origem'], URL)

    def test_sem_endereco_o_mesmo_reel_ja_nao_passa(self):
        sem = {k: v for k, v in self.ITEM.items() if k != 'url'}
        r, _m, _ev = ad._tem_origem(sem)
        self.assertEqual(r, ad.NAO_SEI)

    def test_atravessar_a_origem_nao_torna_a_identidade_provada(self):
        # ORIGIN_GATE_PASSED != IDENTITY_STATE PROVEN. Sao dois estados, e a
        # trava da Collection continua a dizer que nao ha fonte.
        r, _m, _ev = ad._tem_origem(self.ITEM)
        self.assertEqual(r, ad.SIM)
        identidade = pc.identidade_da_observacao(
            {'SOURCE_ID': self.ITEM['source_id'], 'DOCUMENT_ID': None})
        self.assertIsNone(identidade['IDENTITY_STATE'])
        self.assertIsNone(identidade['SOURCE_ID'])


class UmDonoParaOVocabulario(unittest.TestCase):
    """As seis confissoes tem dono, e a porta usa-o em vez de o copiar."""

    def test_a_admissao_importa_o_dono_e_nao_repete_a_lista(self):
        with io.open(os.path.join(RAIZ, 'admissao', 'admissao.py'),
                     encoding='utf-8') as fh:
            fonte = fh.read()
        arvore = ast.parse(fonte)
        importa = [n for n in ast.walk(arvore)
                   if isinstance(n, ast.ImportFrom) and n.module == 'preservar_coleta'
                   and any(a.name == '_identifica' for a in n.names)]
        self.assertTrue(importa, 'a porta deixou de usar o dono do vocabulario')
        for n in ast.walk(arvore):
            if isinstance(n, ast.Assign):
                alvos = [t.id for t in n.targets if isinstance(t, ast.Name)]
                self.assertNotIn('SENTINELAS', alvos,
                                 'nasceu uma segunda copia das confissoes')


if __name__ == '__main__':
    unittest.main(verbosity=2)
