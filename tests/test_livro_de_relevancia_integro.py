#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""O LIVRO DE RELEVÂNCIA NÃO PODE GANHAR CÓPIAS SOZINHO.

Esta guarda nasceu de um defeito real, e o defeito foi meu.

    `leis/relevancia_da_fonte.py::registar()` ESCREVE NO DISCO.

O nome não diz isso. Parece — e eu li como — «carregar as decisões para a
memória para poder consultá-las». É o contrário: ela faz *append* ao ficheiro
do livro e devolve o tamanho do livro **depois** de escrever.

Chamei-a três vezes em scripts de medição, para "carregar" o livro antes de
consultar o portão. Cada chamada acrescentou ao disco as 7 decisões que ela
tinha acabado de ler. Resultado medido: `7 → 28`, cada avaliação exactamente
4 vezes (1 original + 3 releituras).

    LER != CARREGAR != REGISTAR.
    UMA FUNÇÃO QUE ESCREVE NÃO PODE CHAMAR-SE COMO UMA QUE LÊ —
    e enquanto se chamar assim, é a guarda que tem de apanhar o engano.

O sinal esteve à vista e passou: `registar()` devolveu `14` quando o livro
tinha 7 linhas. Eu li o número e segui em frente. **O owner do projeto é que
apanhou o defeito, depois de eu ter empurrado o commit.**

    UM NÚMERO QUE NÃO BATE É UM DEFEITO A PEDIR LICENÇA PARA ENTRAR.

E a razão de 324 testes terem passado por cima disto sem piscar:

    NENHUM TESTE OLHAVA PARA O LIVRO.

O livro é dado, não código. Não tem import, não tem chamada, não aparece em
cobertura. A suíte inteira podia ficar verde com o livro a quadruplicar em
cada corrida — e ficou. Por isso a guarda vive aqui, e olha para o FICHEIRO.
"""
import json
import os
import unittest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LIVRO = os.path.join(RAIZ, 'data', 'samples',
                     'LIVRO-DE-RELEVANCIA-DE-FONTE.json')


def _livro():
    with open(LIVRO, encoding='utf-8') as fh:
        return json.load(fh)


def _chave(decisao):
    """A linha inteira, normalizada — para comparar byte a byte."""
    return json.dumps(decisao, sort_keys=True, ensure_ascii=False)


def _par(decisao):
    """O par (FONTE, PROPÓSITO): a unidade de que a lei fala."""
    return (decisao.get('SOURCE_ID'), decisao.get('PROPOSITO'))


class OLivroNaoGanhaCopiasSozinho(unittest.TestCase):

    def test_nenhuma_linha_byte_identica_repetida(self):
        """A guarda central: duas linhas IGUAIS são sempre um acidente.

        Uma reavaliação legítima muda `AVALIADO_EM`, `VERSAO` ou `RESULTADO` —
        e por isso NÃO é byte-idêntica. Só uma releitura acidental produz a
        mesma linha duas vezes.
        """
        decisoes = _livro()['DECISOES']
        vistas, repetidas = set(), []
        for d in decisoes:
            k = _chave(d)
            if k in vistas:
                repetidas.append(_par(d))
            vistas.add(k)
        self.assertEqual(
            [], repetidas,
            'LINHAS BYTE-IDENTICAS NO LIVRO: %s.\n'
            'Isto nao e reavaliacao — reavaliar muda a data e a versao.\n'
            'A causa provavel e `registar()` ter sido chamada para LER: ela '
            'escreve no disco e devolve o tamanho DEPOIS de escrever.' % repetidas)

    def test_total_declarado_bate_com_as_linhas(self):
        """`TOTAL` é uma afirmação sobre o ficheiro. Tem de ser verdadeira."""
        d = _livro()
        self.assertEqual(
            len(d['DECISOES']), d.get('TOTAL'),
            'TOTAL=%s mas ha %s linhas. Um contador que mente esconde '
            'exactamente o defeito que esta suite existe para apanhar.'
            % (d.get('TOTAL'), len(d['DECISOES'])))

    def test_cada_par_aparece_uma_vez_por_avaliacao(self):
        """Duas linhas do mesmo par têm de ser avaliações DIFERENTES.

        A lei do livro permite — e protege — reavaliar. O que ela não permite
        é a mesma avaliação existir duas vezes: aí já não se sabe se houve
        uma decisão ou duas.
        """
        por_par = {}
        for d in _livro()['DECISOES']:
            por_par.setdefault(_par(d), []).append(d)
        for par, linhas in por_par.items():
            assinaturas = {(l.get('AVALIADO_EM'), l.get('VERSAO')) for l in linhas}
            self.assertEqual(
                len(linhas), len(assinaturas),
                'o par %s tem %d linhas mas so %d avaliacoes distintas '
                '(data+versao). Copia, nao historia.'
                % (par, len(linhas), len(assinaturas)))

    def test_toda_decisao_tem_os_campos_do_contrato(self):
        """Sem os campos, o portão canónico recusa a linha."""
        import sys
        sys.path.insert(0, os.path.join(RAIZ, 'leis'))
        sys.path.insert(0, RAIZ)
        import relevancia_da_fonte as R
        for d in _livro()['DECISOES']:
            faltam = [c for c in R.CAMPOS_DA_DECISAO if c not in d]
            self.assertEqual([], faltam,
                             'decisao %s sem os campos: %s' % (_par(d), faltam))

    def test_o_livro_e_o_que_o_dono_da_lei_aceita(self):
        """Prova de ponta: o portão canónico lê este ficheiro e responde.

        ⚠️ Repare que esta prova NÃO chama `registar()`. Ela passa as linhas
        directamente a `portao()`, que é a função que só lê. Chamar
        `registar()` aqui faria o teste ESCREVER no livro de cada vez que
        corresse — e um teste que corrompe o dado que valida é pior que teste
        nenhum.
        """
        import sys
        sys.path.insert(0, os.path.join(RAIZ, 'leis'))
        sys.path.insert(0, RAIZ)
        import relevancia_da_fonte as R
        decisoes = _livro()['DECISOES']
        for d in decisoes:
            v = R.portao(d['SOURCE_ID'], d['PROPOSITO'], decisoes,
                         custo='gratuito')
            self.assertEqual(
                d['RESULTADO'], v['ESTADO_DA_RELEVANCIA'],
                'o portao le %s para %s, mas o livro diz %s'
                % (v['ESTADO_DA_RELEVANCIA'], _par(d), d['RESULTADO']))


class RegistarEscreveEIssoTemDeEstarDito(unittest.TestCase):
    """A segunda metade da correcção: tornar o engano difícil de repetir.

    Não se renomeou `registar()` — ela é chamada noutros sítios e renomear
    era mexer em mais do que este defeito pede. O que se faz é FIXAR por
    teste que ela escreve, para que ninguém volte a lê-la como leitura.
    """

    def test_a_funcao_que_so_le_chama_se_ler_livro(self):
        import sys
        sys.path.insert(0, os.path.join(RAIZ, 'leis'))
        sys.path.insert(0, RAIZ)
        import relevancia_da_fonte as R
        self.assertTrue(hasattr(R, 'ler_livro'),
                        'quem quer LER tem de ter uma funcao de leitura')

    def test_registar_esta_documentada_como_escrita(self):
        import sys
        sys.path.insert(0, os.path.join(RAIZ, 'leis'))
        sys.path.insert(0, RAIZ)
        import relevancia_da_fonte as R
        doc = (R.registar.__doc__ or '').upper()
        self.assertTrue(
            any(p in doc for p in ('JUNTA', 'ESCREV', 'APPEND', 'GRAVA')),
            'o docstring de `registar()` tem de dizer que ela ESCREVE — '
            'foi lê-la como leitura que quadruplicou o livro.')

    def test_registar_num_livro_de_brincar_realmente_escreve(self):
        """Prova executável de que ela escreve — em pasta descartável."""
        import sys, tempfile, shutil
        sys.path.insert(0, os.path.join(RAIZ, 'leis'))
        sys.path.insert(0, RAIZ)
        import relevancia_da_fonte as R
        tmp = tempfile.mkdtemp(prefix='livro-de-brincar-')
        try:
            linha = dict(_livro()['DECISOES'][0])
            antes = R.ler_livro(tmp)
            R.registar([linha], raiz=tmp)
            depois = R.ler_livro(tmp)
            self.assertEqual(len(antes) + 1, len(depois),
                             '`registar()` ESCREVE: e esse o ponto.')
        finally:
            shutil.rmtree(tmp, ignore_errors=True)


if __name__ == '__main__':
    unittest.main(verbosity=2)
