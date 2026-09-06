#!/usr/bin/env python3
"""
Provas do parser contra o contrato REAL, com fixture sanitizada e sem token.

O schema saiu dos 8 runs PAGOS recuperados. O defeito que estas provas fecham foi
um so: a URL do perfil vive em `basic_info.profile_url`, e o parser antigo
procurava `profileUrl` no topo. Um nivel de aninhamento virou 8 NOT_FOUND.
"""
import json
import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'scripts'))
import linkedin_schema as ls  # noqa: E402

FIX = os.path.join(ROOT, 'tests', 'fixtures', 'linkedin_profile_v1.json')


def carregar():
    with open(FIX, encoding='utf-8') as f:
        return json.load(f)


class TestSchemaReal(unittest.TestCase):

    def test_A_perfil_real_e_reconhecido(self):
        p = ls.extrair_perfil(carregar())
        self.assertEqual(ls.SCHEMA_V1, p['SCHEMA'])
        self.assertEqual('https://www.linkedin.com/in/exemplo', p['PROFILE_URL'])
        self.assertEqual('exemplo123', p['PUBLIC_IDENTIFIER'])

    def test_B_campo_aninhado_e_reconhecido(self):
        """A licao inteira: a URL esta em basic_info, nao no topo."""
        d = carregar()
        self.assertNotIn('profileUrl', d, 'o Actor NUNCA devolveu isso no topo')
        self.assertNotIn('profile_url', d, 'nem no topo com underscore')
        self.assertIn('profile_url', d['basic_info'])
        p = ls.extrair_perfil(d)
        self.assertEqual('Citta, Italia', p['LOCATION'])
        self.assertEqual('IT', p['COUNTRY_CODE'])

    def test_C_schema_desconhecido_continua_desconhecido(self):
        """UNKNOWN_SCHEMA nunca pode virar NOT_FOUND."""
        p = ls.extrair_perfil({'profileUrl': 'https://x', 'name': 'y'})
        self.assertEqual(ls.UNKNOWN_SCHEMA, p['SCHEMA'])
        self.assertIsNone(p['PROFILE_URL'])
        self.assertIn('NÃO significa que o perfil não exista', p['WHY'])

    def test_D_item_de_erro_nao_vira_perfil(self):
        p = ls.extrair_perfil({'error': 'quota', 'errorMessage': 'x'})
        self.assertEqual(ls.ERROR_ITEM, p['SCHEMA'])
        self.assertIsNone(p['PROFILE_URL'])

    def test_E_parser_miss_nao_vira_not_found(self):
        """A lei central desta rodada."""
        for item in ({'algo': 1}, [], None, 'texto', {'basic_info': 'nao dict'}):
            with self.subTest(item=repr(item)[:30]):
                p = ls.extrair_perfil(item)
                self.assertIn(p['SCHEMA'], (ls.UNKNOWN_SCHEMA, ls.ERROR_ITEM))
                self.assertNotIn('NOT_FOUND', json.dumps(p, ensure_ascii=False))

    def test_G_fixture_nao_tem_token_nem_pessoa_real(self):
        t = open(FIX, encoding='utf-8').read()
        self.assertNotIn('apify_api_', t)
        self.assertIn('SINTETICO', t)
        for nome in ('Locatelli', 'Pecchioni', 'Biagetti', 'Cavina'):
            self.assertNotIn(nome, t, 'fixture nao carrega pessoa real')

    def test_H_identidade_da_execucao_sobrevive(self):
        p = ls.extrair_perfil(carregar())
        self.assertTrue(p['URN'].startswith('urn:li:'))
        self.assertEqual('exemplo123', ls.identidade_do_item(carregar()))

    def test_I_reprocessar_a_mesma_resposta_nao_duplica(self):
        d = carregar()
        self.assertEqual(ls.identidade_do_item(d), ls.identidade_do_item(carregar()))

    def test_J_identidade_nao_depende_do_token(self):
        """Trocar de chave nao pode mudar a identidade do conteudo."""
        d1, d2 = carregar(), carregar()
        d2['_COLETADO_COM_POOL_POSITION'] = 3
        self.assertEqual(ls.identidade_do_item(d1), ls.identidade_do_item(d2))

    # ------------------------------------------------------- SEARCH_HIT != PERSON
    def test_busca_devolve_alguem_e_isso_nao_e_a_pessoa(self):
        """O Actor sempre devolve UM perfil para uma consulta. Pode ser outro."""
        p = ls.extrair_perfil(carregar())
        est, _ = ls.conferir_identidade(p, 'Nome Cognome')
        self.assertEqual('IDENTITY_CONFIRMED', est)
        est, motivo = ls.conferir_identidade(p, 'Sabrina Locatelli')
        self.assertEqual(ls.IDENTITY_UNVERIFIED, est)
        self.assertIn('não contém', motivo)

    def test_identidade_nao_avaliavel_em_schema_desconhecido(self):
        p = ls.extrair_perfil({'x': 1})
        est, _ = ls.conferir_identidade(p, 'Qualquer Nome')
        self.assertEqual(ls.UNKNOWN_SCHEMA, est)

    # ------------------------------------------------------------------ MUTACAO
    def test_mutacao_remover_o_mapping_correto_reprova(self):
        """Prova que o teste mede o conserto, e nao passaria de graca.

        Reinstala o parser ANTIGO — que procurava a URL no topo — e exige que ele
        falhe sobre a MESMA fixture que o parser novo le.
        """
        d = carregar()
        antigo = (d.get('profileUrl') or d.get('url') or d.get('publicIdentifier'))
        self.assertIsNone(antigo,
                          'o parser antigo NAO podia achar a URL; se acha, o teste '
                          'nao esta medindo a correcao')
        novo = ls.extrair_perfil(d)['PROFILE_URL']
        self.assertIsNotNone(novo, 'o parser novo acha')

    def test_mutacao_aceitar_qualquer_dict_como_perfil_reprova(self):
        """Se detectar_schema virasse permissivo, item de erro viraria perfil."""
        erro = {'error': 'x'}
        self.assertNotEqual(ls.SCHEMA_V1, ls.detectar_schema(erro))
        permissivo = bool(isinstance(erro, dict))
        self.assertTrue(permissivo, 'um detector ingenuo aceitaria — por isso nao e ingenuo')


if __name__ == '__main__':
    unittest.main(verbosity=2)
