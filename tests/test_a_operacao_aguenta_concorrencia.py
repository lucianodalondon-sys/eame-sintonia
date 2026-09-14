#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""AS GUARDAS DAS QUATRO CORRECOES DA MADRUGADA.

Todas nasceram de um defeito MEDIDO, e cada uma guarda a PROPRIEDADE — nunca
o estado de hoje.

    UMA GUARDA PRESA AO ESTADO DE HOJE REPROVA O PROGRESSO DE AMANHA.
"""
import ast
import io
import json
import os
import sys
import threading
import unittest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if RAIZ not in sys.path:
    sys.path.insert(0, RAIZ)
import _gavetas  # noqa: E402,F401

import admissao as adm                                      # noqa: E402
import retorno_da_coleta as rdc                             # noqa: E402
from pedido import Pedido                                   # noqa: E402
from receitas import EXECUTORES                             # noqa: E402


def _fonte(rel):
    with io.open(os.path.join(RAIZ, rel), encoding="utf-8") as f:
        return f.read()


def _codigo_sem_prosa(rel):
    """O ficheiro sem comentarios e sem docstrings — so o que EXECUTA.

    A prosa destes ficheiros EXPLICA os defeitos que eles corrigiram, e uma
    guarda de texto leria a explicacao e reprovaria a cura.

        PROCURAR O TEXTO DA REGRA NAO E MEDIR A REGRA.
    """
    arvore = ast.parse(_fonte(rel))
    for no in ast.walk(arvore):
        corpo = getattr(no, "body", None)
        if not isinstance(corpo, list) or not corpo:
            continue
        if not isinstance(no, (ast.Module, ast.ClassDef, ast.FunctionDef,
                               ast.AsyncFunctionDef)):
            continue
        p = corpo[0]
        if (isinstance(p, ast.Expr) and isinstance(p.value, ast.Constant)
                and isinstance(p.value.value, str)):
            corpo.pop(0)
            if not corpo:
                corpo.append(ast.Pass())
    ast.fix_missing_locations(arvore)
    return ast.unparse(arvore)


# ══════════════════════════════════════════════════════════════════════════
# 1 · O ENVELOPE E DA CORRIDA
# ══════════════════════════════════════════════════════════════════════════
class OEnvelopeEDaCorrida(unittest.TestCase):

    def test_o_endereco_muda_com_a_corrida(self):
        a = rdc.endereco_do_envelope("data/x/RETORNO.json", "CORRIDA-A")
        b = rdc.endereco_do_envelope("data/x/RETORNO.json", "CORRIDA-B")
        self.assertNotEqual(a, b, "duas corridas partilham o mesmo endereco")
        self.assertTrue(a.endswith(".json"), "a extensao perdeu-se: %s" % a)
        self.assertIn("CORRIDA-A", a)

    def test_sem_corrida_devolve_o_padrao_e_nao_inventa(self):
        """Quem pergunta sem corrida quer saber onde o executor costuma
        escrever. Inventar um endereco daria um caminho que ninguem escreve,
        e a recusa deixaria de se distinguir do erro."""
        p = "data/x/RETORNO.json"
        for vazio in ("", None, "   "):
            self.assertEqual(p, rdc.endereco_do_envelope(p, vazio))

    def test_o_run_id_e_saneado_para_caber_num_caminho(self):
        """⚠️ A CORRIDA E UM SEGMENTO, E NAO PODE TRAZER SEPARADORES.
        Um `run_id` com `/` dentro criaria pastas que ninguem pediu — e, pior,
        um `..` sairia da pasta da colheita.
        """
        fora = rdc.endereco_do_envelope("d/R.json", "a/b\\c:d e")
        segmento = fora[len("d/"):-len("/R.json")]
        self.assertNotIn("/", segmento, "a corrida trouxe separadores: %s"
                         % segmento)
        self.assertNotIn("\\", segmento)
        self.assertNotIn("..", segmento)
        self.assertTrue(fora.endswith("/R.json"),
                        "o nome do ficheiro mudou: %s" % fora)

    def test_TODOS_os_executores_com_ENVELOPE_escrevem_pela_regra(self):
        """⚠️ NAO SE NOMEIA UM EXECUTOR: a propriedade e do contrato.

        Corrigir so o que me lembrei de testar deixaria a propriedade meia
        verdadeira — e meia verdadeira e pior do que falsa, porque passa a
        depender de qual executor correu.
        """
        for universo, lista in EXECUTORES.items():
            for e in lista:
                if not (e.get("retorno") or {}).get("ENVELOPE"):
                    continue
                rel = e["roda"][0]
                if not rel.endswith(".py"):
                    continue
                codigo = _codigo_sem_prosa(rel)
                self.assertIn("endereco_do_envelope", codigo,
                              "%s/%s escreve o envelope sem passar pela regra"
                              % (universo, e["id"]))

    def test_o_orquestrador_pergunta_a_lei_pelo_endereco(self):
        codigo = _codigo_sem_prosa("orquestrador/orquestrador.py")
        self.assertIn("endereco_do_envelope", codigo,
                      "o orquestrador voltou a ler o caminho como literal")

    def test_um_envelope_de_OUTRA_corrida_e_RECUSADO(self):
        """A segunda tranca: o endereco separa, e o conteudo confirma.

        Uma tranca de endereco protege do acidente; uma de CONTEUDO protege
        tambem do engano — um ficheiro deixado a mao, um restauro de backup,
        um padrao sem sufixo.
        """
        import orquestrador as orq
        e = {"id": "x", "roda": ["coleta/eu_regulatorio_executor.py"],
             "retorno": {"ENVELOPE": "data/colheita/_prova/RETORNO.json"}}
        alvo = os.path.join(
            RAIZ, rdc.endereco_do_envelope(e["retorno"]["ENVELOPE"], "DONA"))
        os.makedirs(os.path.dirname(alvo), exist_ok=True)
        with io.open(alvo, "w", encoding="utf-8") as fh:
            json.dump({"RUN_ID": "OUTRA", "EXECUTOR_ID": "x",
                       "EXECUTOR_VERSION": "v", "ESTADO": rdc.SUCCESS,
                       "COLHEITA": [], "SUPORTE": [], "ERROS": []}, fh)
        try:
            env, notas = orq.o_envelope(e, "DONA")
            self.assertNotEqual("OUTRA", env.get("RUN_ID"),
                                "o envelope de outra corrida foi aceite")
            self.assertIn("OUTRA", notas,
                          "a recusa nao diz de quem era o envelope")
        finally:
            os.unlink(alvo)


# ══════════════════════════════════════════════════════════════════════════
# 2 · A CORRIDA TEM NOME PROPRIO
# ══════════════════════════════════════════════════════════════════════════
class ACorridaTemNomeProprio(unittest.TestCase):

    def test_duas_corridas_do_mesmo_segundo_sao_DUAS(self):
        """⚠️ MEDIDO: cinco corridas concorrentes nasceram no mesmo segundo,
        receberam o mesmo nome, e quatro rebentaram na chave unica.

            DUAS COLETAS NO MESMO SEGUNDO NAO SAO A MESMA COLETA.
        """
        import orquestrador as orq
        p = Pedido(alvo="T4", filtros={"pais": "IT"})
        # ⚠️ A AMOSTRA TEM DE SER GRANDE PARA A COLISAO TER HIPOTESE.
        # Com 500 nomes e tres bytes de sufixo, a probabilidade de colisao
        # era ~0,7% — o teste passaria quase sempre e falharia de vez em
        # quando, que e o pior comportamento possivel numa guarda.
        #
        #     UM TESTE QUE SO APANHA O DEFEITO AS VEZES
        #     ENSINA A DESCONFIAR DO TESTE, E NAO DO CODIGO.
        quantos = 20000
        nomes = {orq.novo_run_id(p) for _ in range(quantos)}
        self.assertEqual(quantos, len(nomes),
                         "o nome da corrida repetiu-se em %d seguidas"
                         % quantos)

    def test_e_em_fios_concorrentes_tambem(self):
        import orquestrador as orq
        p = Pedido(alvo="T4", filtros={"pais": "IT"})
        nomes, trava = [], threading.Lock()

        def gera():
            meu = [orq.novo_run_id(p) for _ in range(400)]
            with trava:
                nomes.extend(meu)

        fios = [threading.Thread(target=gera) for _ in range(8)]
        for f in fios:
            f.start()
        for f in fios:
            f.join()
        self.assertEqual(len(nomes), len(set(nomes)),
                         "nomes repetidos com 8 fios em paralelo")

    def test_o_nome_continua_a_dizer_pais_alvo_e_quando(self):
        """O sufixo e DESEMPATE, e nao substitui o que o nome ja dizia. Uma
        pessoa le estes nomes."""
        import orquestrador as orq
        nome = orq.novo_run_id(Pedido(alvo="T4", filtros={"pais": "IT"}))
        self.assertTrue(nome.startswith("IT-T4-"),
                        "o nome deixou de dizer pais e alvo: %s" % nome)


# ══════════════════════════════════════════════════════════════════════════
# 3 · O LIVRO DE DECISOES NAO SE PERDE A DUAS MAOS
# ══════════════════════════════════════════════════════════════════════════
class OLivroAguentaDuasMaos(unittest.TestCase):

    def setUp(self):
        import pathlib
        import tempfile
        self._antes = adm.LIVRO
        adm.LIVRO = (pathlib.Path(tempfile.mkdtemp(prefix="livro-t-"))
                     / "LIVRO-DE-DECISOES.json")

    def tearDown(self):
        adm.LIVRO = self._antes

    def _decisao(self, i):
        return adm.Decisao(item="i%d" % i, universo="T4", resultado=adm.SIM,
                           regra="r", motivo="m", evidencia={},
                           corrida="c%d" % i)

    def test_nenhuma_decisao_se_perde_com_muitos_escritores(self):
        """⚠️ MEDIDO: com cinco corridas concorrentes, uma morreu com
        `LivroIlegivel`. E a falha silenciosa e pior: as duas leem 100, cada
        uma junta 1, a ultima escreve 101 — e a decisao da outra desapareceu.

            LER, JUNTAR E ESCREVER SEM TRAVA NAO E ACRESCENTAR:
            E ESCREVER POR CIMA DE QUEM ESTAVA A ACRESCENTAR.
        """
        erros = []

        def escreve(i):
            try:
                adm.escrever([self._decisao(i)])
            except Exception as ex:                          # noqa: BLE001
                erros.append("%s: %s" % (type(ex).__name__, str(ex)[:120]))

        fios = [threading.Thread(target=escreve, args=(i,)) for i in range(24)]
        for f in fios:
            f.start()
        for f in fios:
            f.join()
        self.assertEqual([], erros, "escritas concorrentes falharam: %s"
                         % erros[:3])
        with io.open(str(adm.LIVRO), encoding="utf-8") as fh:
            livro = json.load(fh)
        self.assertEqual(24, len(livro["DECISOES"]),
                         "decisoes perdidas: ficaram %d de 24"
                         % len(livro["DECISOES"]))

    def test_a_escrita_e_atomica_e_nao_deixa_o_livro_a_meio(self):
        codigo = _codigo_sem_prosa("admissao/admissao.py")
        self.assertIn("os.replace", codigo,
                      "o livro voltou a ser escrito sem troca atomica")
        self.assertNotIn("LIVRO.write_text", codigo,
                         "o livro voltou ao write_text directo")

    def test_um_livro_ilegivel_continua_a_ser_RECUSADO(self):
        """A trava nova nao pode ter afrouxado a antiga: um livro que nao se
        le nao e um livro vazio."""
        adm.LIVRO.parent.mkdir(parents=True, exist_ok=True)
        adm.LIVRO.write_text("{isto nao e json", encoding="utf-8")
        with self.assertRaises(adm.LivroIlegivel):
            adm.escrever([self._decisao(1)])
        self.assertEqual("{isto nao e json",
                         adm.LIVRO.read_text(encoding="utf-8"),
                         "o livro ilegivel foi apagado em vez de recusado")


# ══════════════════════════════════════════════════════════════════════════
# 4 · OS BYTES NAO SE LEEM A MEIO DE SEREM ESCRITOS
# ══════════════════════════════════════════════════════════════════════════
class OsBytesChegamInteiros(unittest.TestCase):

    def test_o_executor_troca_o_ficheiro_de_forma_atomica(self):
        """⚠️ MEDIDO: duas em vinte corridas concorrentes perderam o item
        porque leram o PDF a meio de outra corrida o escrever.

            UM FICHEIRO A MEIO DE SER ESCRITO NAO E UM FICHEIRO VAZIO:
            E UM FICHEIRO QUE MENTE DURANTE UNS MILISSEGUNDOS.
        """
        codigo = _codigo_sem_prosa("coleta/eu_regulatorio_executor.py")
        self.assertIn("os.replace", codigo,
                      "o executor voltou a escrever o PDF por cima")

    def test_e_nao_reescreve_o_que_ja_estava_la(self):
        codigo = _codigo_sem_prosa("coleta/eu_regulatorio_executor.py")
        self.assertIn("DO_ARQUIVO", codigo,
                      "o executor deixou de distinguir a origem dos bytes")

    def test_um_ficheiro_truncado_NAO_conta_como_documento(self):
        import importlib.util as u
        sp = u.spec_from_file_location(
            "ex_t4", os.path.join(RAIZ, "coleta",
                                  "eu_regulatorio_executor.py"))
        m = u.module_from_spec(sp)
        sp.loader.exec_module(m)
        pasta = os.path.join(RAIZ, m.ARMAZEM)
        os.makedirs(pasta, exist_ok=True)
        alvo = os.path.join(pasta, "PROVA-TRUNCADO-IT.pdf")
        with io.open(alvo, "wb") as fh:
            fh.write(b"nao sou um pdf")
        try:
            self.assertIsNone(m._bytes_que_ja_temos("PROVA-TRUNCADO"),
                              "um ficheiro truncado passou por documento")
        finally:
            os.unlink(alvo)


# ══════════════════════════════════════════════════════════════════════════
# 5 · A FONTE QUE TRAVA NAO E A FONTE QUE NAO TEM NADA
# ══════════════════════════════════════════════════════════════════════════
class OTravaoNaoEVazio(unittest.TestCase):

    def test_os_estados_da_ida_a_fonte_sao_distintos(self):
        import importlib.util as u
        sp = u.spec_from_file_location(
            "ex_t4b", os.path.join(RAIZ, "coleta",
                                   "eu_regulatorio_executor.py"))
        m = u.module_from_spec(sp)
        sp.loader.exec_module(m)
        estados = {m.OK, m.VAZIO, m.FONTE_INDISPONIVEL, m.NAO_E_PDF,
                   m.DO_ARQUIVO}
        self.assertEqual(5, len(estados),
                         "dois estados da ida a fonte colaram-se: %s"
                         % estados)
        self.assertIn(202, m.TRAVOU, "o 202 deixou de contar como travao")

    def test_o_executor_e_CORTES_com_a_fonte(self):
        """Um coletor sem cortesia nao perde um documento: perde a fonte.
        Medido — dez idas em duas horas e o EUR-Lex passou a travar tudo."""
        import importlib.util as u
        sp = u.spec_from_file_location(
            "ex_t4c", os.path.join(RAIZ, "coleta",
                                   "eu_regulatorio_executor.py"))
        m = u.module_from_spec(sp)
        sp.loader.exec_module(m)
        self.assertGreater(m.PAUSA_ENTRE_IDAS, 0)
        self.assertGreater(m.TENTATIVAS, 1)
        self.assertGreater(m.ESPERA_INICIAL, 0)


if __name__ == "__main__":
    unittest.main()
