#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""O UNIVERSO VEM DO PEDIDO — e nunca do alvo.

Nasceu do canário final do YouTube, que parou antes de adquirir. Um pedido com

    alvo = T8   ·   universo = T5   (decisão humana, explícita)

chegava à porta a perguntar **T8**, porque `orquestrador.py` passava `p.alvo`
como universo. `T8` não tem régua escrita — só `T3 T4 T5 T7 T9` têm — e a
Admissão responderia `NAO_SE_APLICA` com toda a educação a um texto que nunca
seria julgado contra `T5`.

    ALVO = PARA QUE SERVE a coleta · audiência, missão, finalidade.
    UNIVERSO = QUE PERGUNTA a porta faz ao conteúdo.
    ALVO != UNIVERSO.

Funcionou durante meses por COINCIDÊNCIA: as corridas usavam alvos (`T3`, `T4`,
`T9`) cujos nomes por acaso existem também como universos.

    COINCIDIR POR HÁBITO NÃO É ESTAR LIGADO.

⚠️ NENHUMA PROVA AQUI ADQUIRE NADA. O vídeo `PGdMQyExeis` continua virgem, e
esta suite não sabe que ele existe.
"""
import json
import os
import socket
import sys
import unittest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for gaveta in ('orquestrador', 'pedido', 'coleta', 'leis', 'admissao'):
    sys.path.insert(0, os.path.join(RAIZ, gaveta))
sys.path.insert(0, RAIZ)

import orquestrador as O                    # noqa: E402
import rota_forward_documento as RF         # noqa: E402
import admissao as A                        # noqa: E402
from pedido import Pedido                   # noqa: E402


class _SemRede:
    def __enter__(self):
        self.chamadas = []
        self._orig = socket.socket.connect

        def espiao(_s, endereco, *a, **k):
            self.chamadas.append(endereco)
            raise AssertionError('A PROVA ABRIU A REDE: %r' % (endereco,))

        socket.socket.connect = espiao
        return self

    def __exit__(self, *e):
        socket.socket.connect = self._orig
        return False


class OCasoQueDeuOrigemAEstaMissao(unittest.TestCase):
    """CASO A — alvo e universo diferentes, que é o caso normal."""

    def test_1_alvo_T8_universo_T5_chega_como_T5(self):
        p = Pedido(alvo='T8', filtros={'universo': 'T5'})
        self.assertEqual('T5', O.universo_do_pedido(p))

    def test_2_e_sobretudo_NAO_chega_como_T8(self):
        """A prova que falharia com o defeito antigo."""
        p = Pedido(alvo='T8', filtros={'universo': 'T5'})
        self.assertNotEqual('T8', O.universo_do_pedido(p),
                            'o alvo voltou a preencher o universo')

    def test_3_o_alvo_nao_e_consultado_de_todo(self):
        """Mesmo universo, alvos diferentes → mesma resposta."""
        a = O.universo_do_pedido(Pedido(alvo='T8', filtros={'universo': 'T5'}))
        b = O.universo_do_pedido(Pedido(alvo='T2', filtros={'universo': 'T5'}))
        c = O.universo_do_pedido(Pedido(alvo='T9', filtros={'universo': 'T5'}))
        self.assertEqual({'T5'}, {a, b, c})


class ACompatibilidadeHistorica(unittest.TestCase):
    """CASO B — quando coincidem, continua a funcionar."""

    def test_4_alvo_T3_universo_T3(self):
        p = Pedido(alvo='T3', filtros={'universo': 'T3'})
        self.assertEqual('T3', O.universo_do_pedido(p))

    def test_5_os_alvos_historicos_continuam_a_servir(self):
        for t in ('T3', 'T4', 'T9'):
            p = Pedido(alvo=t, filtros={'universo': t})
            self.assertEqual(t, O.universo_do_pedido(p))


class OUniversoAusenteFalhaFechado(unittest.TestCase):
    """CASO C — e NÃO cai para o alvo."""

    def test_6_sem_universo_levanta(self):
        with self.assertRaises(RF.UniversoNaoDeclarado):
            O.universo_do_pedido(Pedido(alvo='T8', filtros={}))

    def test_7_filtros_None_tambem_levanta(self):
        p = Pedido(alvo='T8', filtros={})
        p.filtros = None
        with self.assertRaises(RF.UniversoNaoDeclarado):
            O.universo_do_pedido(p)

    def test_8_as_confissoes_de_ausencia_tambem_levantam(self):
        for vazio in ('', '   ', 'NAO SEI'):
            with self.assertRaises(RF.UniversoNaoDeclarado):
                O.universo_do_pedido(Pedido(alvo='T8',
                                            filtros={'universo': vazio}))

    def test_9_NAO_existe_fallback_para_o_alvo(self):
        """A pergunta directa: ausente devolve T8 alguma vez?"""
        try:
            v = O.universo_do_pedido(Pedido(alvo='T8', filtros={}))
        except RF.UniversoNaoDeclarado:
            return                      # o comportamento certo
        self.fail('devolveu %r em vez de recusar — fallback para o alvo' % v)

    def test_10_a_recusa_e_do_dono_canonico_e_nao_uma_segunda_lei(self):
        """`UniversoNaoDeclarado` já existia; não se criou outra exceção."""
        import inspect
        src = inspect.getsource(O.universo_do_pedido)
        self.assertIn('universo_declarado', src)
        self.assertNotIn('class ', src, 'exceção nova para a mesma pergunta')


class OUniversoSemReguaEDecisaoDaAdmissao(unittest.TestCase):
    """CASO D — o roteador transporta; quem julga a validade é a porta."""

    def test_11_o_roteador_transporta_o_que_foi_declarado(self):
        p = Pedido(alvo='T8', filtros={'universo': 'T8'})
        self.assertEqual('T8', O.universo_do_pedido(p),
                         'o roteador não é o dono da validade do universo')

    def test_12_a_admissao_e_que_responde_por_universo_sem_regua(self):
        self.assertNotIn('T8', A.PERGUNTAS_DO_UNIVERSO)
        d = A.decidir({'id': 'x', 'texto': 'prova di campo su pomodoro',
                       'source_id': 'IT-T8-001'}, 'T8')
        self.assertIn(d.resultado, ('NAO_SEI', 'NAO_SE_APLICA'),
                      'universo sem régua não pode virar universo válido')

    def test_13_o_roteador_nao_traduz_alvo_em_universo(self):
        """Nenhum alias T8→T5 escondido."""
        import inspect
        src = inspect.getsource(O.universo_do_pedido)
        for proibido in ("'T3'", "'T5'", "'T8'", 'ALIAS', 'MAPA_DE_UNIVERSO'):
            self.assertNotIn(proibido, src,
                             'o roteador não pode conhecer universos pelo nome')


class OUniversoSobreviveAoCaminhoTodo(unittest.TestCase):
    """Não basta viver em memória."""

    def test_14_sobrevive_a_serializacao(self):
        p = Pedido(alvo='T8', filtros={'universo': 'T5', 'fonte': 'IT-T8-001'})
        j = p.para_json()
        self.assertEqual('T5', j['filtros']['universo'])

    def test_15_sobrevive_ao_round_trip_json(self):
        p = Pedido(alvo='T8', filtros={'universo': 'T5'})
        voltou = Pedido(**json.loads(json.dumps(p.para_json())))
        self.assertEqual('T5', O.universo_do_pedido(voltou))

    def test_16_o_alvo_tambem_sobrevive_e_continua_diferente(self):
        p = Pedido(alvo='T8', filtros={'universo': 'T5'})
        voltou = Pedido(**json.loads(json.dumps(p.para_json())))
        self.assertEqual('T8', voltou.alvo)
        self.assertEqual('T5', O.universo_do_pedido(voltou))
        self.assertNotEqual(voltou.alvo, O.universo_do_pedido(voltou))

    def test_17_reprocessamento_preserva_o_universo_sem_rede(self):
        """Um item já adquirido, rejulgado com universo declarado."""
        with _SemRede() as r:
            p = Pedido(alvo='T8', filtros={'universo': 'T5',
                                           'fonte': 'IT-T8-001',
                                           'colheita-da-corrida': 'RUN-ANTIGA'})
            voltou = Pedido(**json.loads(json.dumps(p.para_json())))
            u = O.universo_do_pedido(voltou)
        self.assertEqual('T5', u)
        self.assertEqual([], r.chamadas, 'REPROCESS_NETWORK_CALLS tem de ser 0')


class ASentinelaContraORegresso(unittest.TestCase):
    """A prova que fica de guarda depois de esta missão acabar.

    ⚠️ ELA LÊ CÓDIGO, E NÃO TEXTO — e isso foi aprendido aqui mesmo.

    A primeira versão procurava `pela_porta(julgar, p.alvo` no ficheiro inteiro
    e ficou VERMELHA com a correção já aplicada: a frase aparecia dentro do
    comentário que *documenta* o defeito antigo. O comentário é o registo de
    por que a linha mudou; apagá-lo para o teste passar seria apagar a memória
    da casa para agradar a uma sentinela mal escrita.

        UMA SENTINELA QUE LÊ COMENTÁRIOS ACUSA A CICATRIZ, E NÃO A FERIDA.

    É a mesma família do ataque que media a palavra «cookie» numa docstring que
    proibia cookies. Mede-se o que CORRE.
    """

    @staticmethod
    def _so_codigo(src):
        """O ficheiro sem comentários e sem docstrings, LINHAS PRESERVADAS.

        Junta-se pelos tokens? Não: `tokenize` devolve cada token separado, e
        `pela_porta(julgar, p.alvo, ...)` viria partido em quinze pedaços — a
        sentinela ficaria cega ao próprio defeito (medido).

        Então apagam-se os comentários NO SÍTIO, mantendo a linha inteira.
        """
        import io
        import tokenize
        linhas = src.splitlines()
        try:
            toks = list(tokenize.generate_tokens(io.StringIO(src).readline))
        except (tokenize.TokenError, IndentationError):
            return '\n'.join(l for l in linhas
                             if not l.strip().startswith('#'))
        apagar = []
        for tok in toks:
            if tok.type == tokenize.COMMENT:
                apagar.append((tok.start, tok.end))
            elif (tok.type == tokenize.STRING
                  and tok.line.strip().startswith(('"""', "'''", 'r"""', "r'''"))):
                apagar.append((tok.start, tok.end))
        for (l0, c0), (l1, c1) in reversed(apagar):
            if l0 == l1:
                linha = linhas[l0 - 1]
                linhas[l0 - 1] = linha[:c0] + linha[c1:]
            else:
                linhas[l0 - 1] = linhas[l0 - 1][:c0]
                for i in range(l0, min(l1, len(linhas))):
                    linhas[i] = ''
        return '\n'.join(linhas)

    def test_18_o_orquestrador_nao_passa_p_alvo_a_pela_porta(self):
        import inspect
        codigo = self._so_codigo(inspect.getsource(O))
        self.assertNotIn('pela_porta(julgar, p.alvo', codigo,
                         'o defeito voltou: o alvo a fazer de universo')

    def test_19_a_unica_chamada_de_producao_usa_universo_do_pedido(self):
        import inspect
        import re
        codigo = self._so_codigo(inspect.getsource(O))
        chamadas = [m.group(0) for m in
                    re.finditer(r'pela_porta\((?!itens)[^)]*\)', codigo)]
        self.assertTrue(chamadas, 'ninguém chama a porta?')
        for c in chamadas:
            self.assertNotIn('p.alvo', c, 'chamada com o alvo: %s' % c)

    def test_19b_a_sentinela_apanha_mesmo_o_defeito(self):
        """Mutação: se o código voltar a usar `p.alvo`, isto tem de morder."""
        mutante = 'def f(p):\n    return pela_porta(julgar, p.alvo, run)\n'
        codigo = self._so_codigo(mutante)
        self.assertIn('p.alvo', codigo,
                      'a sentinela ficou cega: não vê o defeito nem no código')

    def test_19c_e_NAO_morde_um_comentario_que_o_descreve(self):
        """A contraprova: a cicatriz documentada não pode reprovar."""
        cicatriz = '# aqui estava pela_porta(julgar, p.alvo, run)\nx = 1\n'
        codigo = self._so_codigo(cicatriz)
        self.assertNotIn('p.alvo', codigo)

    def test_20_nenhum_outro_call_site_usa_o_alvo_como_universo(self):
        """O censo, fixado por teste: 4 call sites, e só um mudou."""
        import re
        achados = []
        for gaveta in ('orquestrador', 'coleta'):
            base = os.path.join(RAIZ, gaveta)
            for raiz, _d, fs in os.walk(base):
                if '__pycache__' in raiz:
                    continue
                for f in fs:
                    if not f.endswith('.py'):
                        continue
                    texto = open(os.path.join(raiz, f), encoding='utf-8',
                                 errors='replace').read()
                    # código, sem comentários
                    codigo = '\n'.join(l for l in texto.splitlines()
                                       if not l.strip().startswith('#'))
                    if re.search(r'(decidir|admitir|pela_porta)\([^)]*p\.alvo',
                                 codigo):
                        achados.append(os.path.join(gaveta, f))
        self.assertEqual([], achados,
                         'estes ainda usam o alvo como universo: %s' % achados)


if __name__ == '__main__':
    unittest.main(verbosity=2)
