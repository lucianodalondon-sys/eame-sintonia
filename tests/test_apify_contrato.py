"""
Provas do conferidor de contrato de entrada.

O defeito que estas provas existem para impedir: mandar um campo que o ator não
lê, ele ignorar em silêncio, devolver `SUCCEEDED` com um item bem formado, e o
dinheiro sair. Foi exatamente o que aconteceu com `searchQuery` em um ator de
*profile detail* — oito vezes.

Nenhuma prova aqui toca a rede. Todas usam schema sintético.
"""
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))), 'scripts'))
import apify_contrato as ac  # noqa: E402

# O contrato do ator de busca por nome, como um ator desse tipo o declara.
SCHEMA_BUSCA = {
    'title': 'Linkedin Profile Search By Name',
    'type': 'object',
    'properties': {
        'firstName': {'type': 'string'},
        'lastName': {'type': 'string'},
        'maxItems': {'type': 'integer'},
        'location': {'type': 'string'},
    },
    'required': ['firstName'],
}


class ContratoConfere(unittest.TestCase):

    def test_a_entrada_que_bate_com_o_contrato_e_MATCH(self):
        props, req = ac.campos_do_schema(SCHEMA_BUSCA)
        r = ac.conferir(props, req, {'firstName': 'Pasquale', 'lastName': 'De Vita'})
        self.assertEqual(r['STATE'], ac.CONTRACT_MATCH)
        self.assertEqual(r['UNKNOWN_FIELDS'], [])

    def test_o_defeito_dos_8_runs_seria_pego_aqui(self):
        """searchQuery num ator que so le firstName/lastName: campo inexistente."""
        props, req = ac.campos_do_schema(SCHEMA_BUSCA)
        r = ac.conferir(props, req, {'firstName': 'x', 'searchQuery': 'Pasquale De Vita'})
        self.assertEqual(r['STATE'], ac.CONTRACT_FIELD_UNKNOWN)
        self.assertIn('searchQuery', r['UNKNOWN_FIELDS'])

    def test_campo_obrigatorio_ausente_pesa_mais_que_campo_desconhecido(self):
        """Faltar obrigatorio impede a execucao; campo a mais so e ignorado."""
        props, req = ac.campos_do_schema(SCHEMA_BUSCA)
        r = ac.conferir(props, req, {'searchQuery': 'x'})
        self.assertEqual(r['STATE'], ac.CONTRACT_REQUIRED_MISSING)
        self.assertEqual(r['REQUIRED_MISSING'], ['firstName'])

    def test_schema_vazio_e_NOT_READABLE_e_nunca_MATCH(self):
        """Sem propriedades declaradas nao ha o que conferir.

        Devolver MATCH aqui seria dizer 'o contrato aprova' quando o contrato
        nao foi lido — o mesmo tipo de falso verde que custou os 8 runs.
        """
        for schema in ({}, None, {'properties': None}, {'properties': {}}, 'texto'):
            props, req = ac.campos_do_schema(schema)
            r = ac.conferir(props, req, {'firstName': 'x'})
            self.assertEqual(r['STATE'], ac.CONTRACT_NOT_READABLE, schema)

    def test_required_malformado_nao_derruba_a_leitura(self):
        props, req = ac.campos_do_schema(dict(SCHEMA_BUSCA, required='firstName'))
        self.assertEqual(req, [])
        self.assertTrue(props)

    def test_MATCH_nao_promete_dado_util(self):
        """A lei CONTRACT_MATCH != USEFUL_DATA tem de estar declarada no arquivo.

        Um contrato satisfeito diz que a entrada sera LIDA. Nao diz que a saida
        serve. Quem apagar essa distincao repete o erro por outro caminho.
        """
        self.assertIn('CONTRACT_MATCH ≠ USEFUL_DATA', ac.__doc__)

    def test_a_intencao_declarada_no_plano_bate_com_o_proprio_conferidor(self):
        """O PLANO nao pode conter entrada que o proprio arquivo saberia recusar."""
        for actor, entrada in ac.PLANO:
            self.assertTrue(entrada, actor)
            self.assertTrue(all(isinstance(k, str) for k in entrada), actor)


class NaoAbreExecucao(unittest.TestCase):

    def test_nenhuma_rota_do_arquivo_faz_POST(self):
        """Ler contrato e GET. Um POST aqui abriria run e custaria dinheiro."""
        with open(ac.__file__, encoding='utf-8') as fh:
            fonte = fh.read()
        self.assertNotIn("'-X', 'POST'", fonte)
        self.assertNotIn('/runs?', fonte)


if __name__ == '__main__':
    unittest.main()
