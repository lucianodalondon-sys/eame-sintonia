#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""A PONTE STORAGE -> DERIVED — e as travas que a impedem de mentir.

A medição de valor vive em `provas/o_pedido_atravessa.py`, contra PostgreSQL
real e o executor REAL. Aqui ficam as guardas que não precisam de banco:

    · o armazém responde ONDE está o byte, e `None` quando não sabe;
    · a porta traduz OBSERVAÇÕES CONFIRMADAS em unidades de derivação,
      e nunca ficheiros encontrados no disco;
    · o orquestrador COORDENA e não deriva.

    CONTROL PLANE != DATA PLANE.  (COL-LAW-012)
"""
import ast
import io
import os
import shutil
import sys
import tempfile
import unittest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for p in (RAIZ, os.path.join(RAIZ, "coleta")):
    if p not in sys.path:
        sys.path.insert(0, p)
import _gavetas                      # noqa: E402,F401
import ingresso as ing               # noqa: E402
import derivacao_forward as deriv    # noqa: E402
from guarda.preservar_coleta import (Armazem, ArmazemLocal,  # noqa: E402
                                     ArmazemDeMentira)

ORQ = os.path.join(RAIZ, "orquestrador", "orquestrador.py")


def _fonte(caminho):
    with io.open(caminho, encoding="utf-8") as f:
        return f.read()


def _chamadas(caminho):
    fora = set()
    for no in ast.walk(ast.parse(_fonte(caminho))):
        if isinstance(no, ast.Call):
            n = getattr(no.func, "attr", None) or getattr(no.func, "id", None)
            if n:
                fora.add(n)
    return fora


class OArmazemDizOndeEstaOByte(unittest.TestCase):
    """`caminho_local` é a mesma pergunta do `ler`, feita por quem não pode
    receber bytes — uma ferramenta externa abre o ficheiro ela própria."""

    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.a = ArmazemLocal(self.tmp)

    def test_devolve_o_caminho_do_byte_que_aterrou(self):
        self.a.enviar("XX/f/DOCUMENT/um.pdf", b"%PDF-1.4", "application/pdf")
        onde = self.a.caminho_local("XX/f/DOCUMENT/um.pdf")
        self.assertTrue(onde and os.path.isfile(onde))
        with open(onde, "rb") as f:
            self.assertEqual(f.read(), b"%PDF-1.4")

    def test_endereco_vazio_nao_tem_caminho(self):
        """O byte não aterrou: devolver o caminho seria entregar um endereço
        que não responde, e o executor chamaria ERROR ao que foi invenção
        nossa."""
        self.assertIsNone(self.a.caminho_local("XX/f/DOCUMENT/nunca.pdf"))

    def test_travessia_para_fora_do_armazem_continua_recusada(self):
        """A mesma linha que recusa no `enviar` recusa aqui: um armazém que
        lê fora de si não é um armazém."""
        with self.assertRaises(ValueError):
            self.a.caminho_local("../../etc/passwd")

    def test_um_armazem_que_nao_e_disco_responde_que_nao_sabe(self):
        """`None` é a resposta CERTA de um armazém de objetos remoto. Criar um
        ficheiro temporário para poder devolver uma string seria responder à
        pergunta errada."""
        m = ArmazemDeMentira()
        m.enviar("XX/f/DOCUMENT/um.pdf", b"%PDF", "application/pdf")
        self.assertIsNone(m.caminho_local("XX/f/DOCUMENT/um.pdf"))
        self.assertIsNone(Armazem().caminho_local("seja_o_que_for"))


class APortaTraduzObservacoesENaoFicheiros(unittest.TestCase):
    """A unidade sai da LINHAGEM — `raw_asset.id` e o endereço do objeto dele —
    e nunca de uma varredura do disco.

        PATH != IDENTITY.
    """

    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.a = ArmazemLocal(self.tmp)
        self.a.enviar("XX/f/DOCUMENT/a.pdf", b"%PDF-a", "application/pdf")
        self.a.enviar("XX/f/DOCUMENT/b.pdf", b"%PDF-b", "application/pdf")

    def _recibo(self, *obs):
        return {"RAW_OBSERVATIONS": list(obs)}

    def test_cada_observacao_confirmada_vira_uma_unidade_com_o_id_real(self):
        u, sem = ing.unidades_para_a_derivacao(self._recibo(
            {"RAW_OBSERVATION_ID": 7, "STORAGE_PATH": "XX/f/DOCUMENT/a.pdf"},
            {"RAW_OBSERVATION_ID": 9, "STORAGE_PATH": "XX/f/DOCUMENT/b.pdf"}),
            self.a)
        self.assertEqual(sem, [])
        self.assertEqual([x["RAW_ASSET_ID"] for x in u], [7, 9])
        # o par (observação, bytes) veio inteiro da linhagem
        self.assertTrue(u[0]["PDF"].endswith("a.pdf"))
        self.assertTrue(u[1]["PDF"].endswith("b.pdf"))

    def test_o_id_NAO_e_derivado_do_caminho_nem_da_ordem(self):
        """O id vem da linha que o banco devolveu. Um id que a casa pudesse
        calcular sozinha não provaria que a linha existe."""
        u, _ = ing.unidades_para_a_derivacao(self._recibo(
            {"RAW_OBSERVATION_ID": 42, "STORAGE_PATH": "XX/f/DOCUMENT/b.pdf"}),
            self.a)
        self.assertEqual(u[0]["RAW_ASSET_ID"], 42)
        self.assertNotIn("42", os.path.basename(u[0]["PDF"]))

    def test_sem_bytes_alcancaveis_a_observacao_sai_com_nome(self):
        u, sem = ing.unidades_para_a_derivacao(self._recibo(
            {"RAW_OBSERVATION_ID": 1, "STORAGE_PATH": "XX/f/DOCUMENT/a.pdf"},
            {"RAW_OBSERVATION_ID": 2, "STORAGE_PATH": "XX/f/DOCUMENT/x.pdf"}),
            self.a)
        self.assertEqual([x["RAW_ASSET_ID"] for x in u], [1])
        self.assertEqual(len(sem), 1)
        self.assertEqual(sem[0]["RAW_ASSET_ID"], 2)
        self.assertEqual(sem[0]["PORQUE"], ing.DERIVACAO_SEM_BYTES_LOCAIS)

    def test_sem_recibo_nao_ha_nada_para_derivar(self):
        """Sem banco, `preservar()` não devolve observações. A lista vazia é a
        verdade: não há observação canónica para derivar.

            ACEITE NA PORTA != OBSERVACAO NO BANCO.
        """
        for vazio in (None, {}, {"RAW_OBSERVATIONS": None},
                      {"RAW_OBSERVATIONS": []}):
            u, sem = ing.unidades_para_a_derivacao(vazio, self.a)
            self.assertEqual((u, sem), ([], []))

    def test_a_porta_nao_varre_o_disco(self):
        """Um `glob` aqui emparelharia o primeiro ficheiro da pasta com a
        primeira linha da tabela, e as duas ordens não têm razão nenhuma para
        coincidir."""
        chamadas = _chamadas(os.path.join(RAIZ, "coleta", "ingresso.py"))
        for proibida in ("glob", "iglob", "listdir", "scandir", "walk"):
            self.assertNotIn(proibida, chamadas)


class OOrquestradorCoordenaENaoDeriva(unittest.TestCase):
    """COL-LAW-012. Ele chama o runner; não abre PDF, não escreve derivado,
    não escreve rastro."""

    def test_nao_chama_o_executor_nem_o_dono_da_escrita(self):
        chamadas = _chamadas(ORQ)
        for proibida in ("derivar_um", "extrair", "preservar_derivado",
                         "registrar", "preservar"):
            self.assertNotIn(proibida, chamadas,
                             "o orquestrador passou a fazer o trabalho de "
                             "outro: %s" % proibida)

    def test_chama_o_runner_canonico(self):
        self.assertIn("correr", _chamadas(ORQ))
        self.assertIn("import derivacao_forward as deriv", _fonte(ORQ))

    def test_nao_varre_o_disco_a_procura_de_brutos(self):
        chamadas = _chamadas(ORQ)
        for proibida in ("glob", "iglob", "listdir", "scandir", "walk"):
            self.assertNotIn(proibida, chamadas)

    def test_sem_unidades_o_runner_nao_e_chamado(self):
        """NAO CORREU != CORREU E NAO DEU NADA. Uma chamada vazia poria uma
        passagem DERIVED no rastro a dizer que a etapa correu."""
        sys.path.insert(0, os.path.join(RAIZ, "orquestrador"))
        import orquestrador as orq
        chamado = []
        antes = deriv.correr
        deriv.correr = lambda *a, **k: chamado.append(1)
        try:
            r = orq.pela_derivacao([], run_id="R", armazem=None, memoria=None)
        finally:
            deriv.correr = antes
        self.assertEqual(chamado, [])
        self.assertFalse(r["CHAMADO"])
        self.assertEqual(r["UNIDADES"], 0)

    def test_a_classe_de_rota_nao_e_fabricada(self):
        """Nenhuma peça entre o Pedido e a corrida declara `ROUTE_CLASS_ID`.
        Escrever `RC-1` porque o canário de hoje é RC-1 seria fabricar
        identidade a partir do caso da vez.

            UNKNOWN HONESTO > ID INVENTADO.

        ⚠️ ISTO LIA-SE COM `assertNotIn("RC-1", fonte)` E MORDIA A PROPRIA
        EXPLICAÇÃO: o parágrafo que diz «não escrever RC-1» contém `RC-1`.
        Uma guarda de texto não distingue a regra do exemplo dela.

            LER O FICHEIRO NÃO É LER O CÓDIGO.

        Agora pergunta-se ao AST o que a chamada REALMENTE passa, e qual é o
        valor por omissão — que é onde um `RC-1` teria de aparecer para
        chegar ao banco.
        """
        arvore = ast.parse(_fonte(ORQ))
        chamadas = [n for n in ast.walk(arvore)
                    if isinstance(n, ast.Call)
                    and getattr(n.func, "id", None) == "pela_derivacao"]
        self.assertEqual(len(chamadas), 1, "a ponte é chamada uma vez")
        passados = {k.arg for k in chamadas[0].keywords}
        self.assertNotIn("route_class_id", passados,
                         "o orquestrador passou a declarar uma classe de rota "
                         "que ninguém lhe provou")
        alvo = [n for n in ast.walk(arvore)
                if isinstance(n, ast.FunctionDef)
                and n.name == "pela_derivacao"][0]
        omissoes = dict(zip(
            [a.arg for a in alvo.args.kwonlyargs], alvo.args.kw_defaults))
        rota = omissoes.get("route_class_id")
        self.assertTrue(isinstance(rota, ast.Constant) and rota.value is None,
                        "o valor por omissão da classe de rota deixou de ser "
                        "ausência")


class AChamadaLevaOQueFoiPROVADOENaoOQueEComodo(unittest.TestCase):
    """O que a ponte passa ao runner tem de VIR de onde foi apurado.

    Uma constante escrita à mão no sítio certo passa em todos os testes que
    olham para o VALOR — e continua a ser identidade fabricada.

        UM VALOR CERTO POR ACASO NÃO É UM VALOR PROVADO.
    """

    def _a_chamada(self):
        arvore = ast.parse(_fonte(ORQ))
        c = [n for n in ast.walk(arvore) if isinstance(n, ast.Call)
             and getattr(n.func, "id", None) == "pela_derivacao"]
        self.assertEqual(len(c), 1)
        return {k.arg: k.value for k in c[0].keywords}

    def test_a_fonte_vem_da_porta_e_nao_de_uma_constante(self):
        """`IT-T2-002` escrito aqui daria a resposta certa para o canário de
        hoje e a resposta errada para todas as outras fontes."""
        alvo = self._a_chamada().get("source_id")
        self.assertFalse(isinstance(alvo, ast.Constant),
                         "a fonte passou a ser escrita à mão na chamada")
        self.assertIn("FONTE_PROVADA", ast.dump(alvo))

    def test_a_corrida_vem_do_recibo_daquela_execucao(self):
        alvo = self._a_chamada().get("run_id")
        self.assertFalse(isinstance(alvo, ast.Constant))
        self.assertIn("RUN_ID", ast.dump(alvo))

    def test_o_rastro_e_o_banco_atravessam_a_ponte(self):
        """Sem `banco_do_rastro` a etapa derivaria em silêncio, e sem
        `memoria` não haveria `derived_artifact` nenhum.

            PERSISTIR SEM RASTRO E UMA ETAPA QUE ACONTECEU AS ESCONDIDAS.
        """
        passados = self._a_chamada()
        for campo in ("banco_do_rastro", "memoria", "armazem"):
            self.assertIn(campo, passados, "a ponte deixou de levar %s" % campo)
            self.assertFalse(isinstance(passados[campo], ast.Constant),
                             "%s passou a ser constante" % campo)

    def test_as_unidades_vem_da_lista_da_PORTA(self):
        """`PARA_A_DERIVACAO` são as observações que o BANCO confirmou. Trocar
        por `PARA_A_PORTA` mandaria derivar o que foi aceite no contrato mas
        talvez nunca escrito — e por `itens`, o que a porta RECUSOU."""
        arvore = ast.parse(_fonte(ORQ))
        c = [n for n in ast.walk(arvore) if isinstance(n, ast.Call)
             and getattr(n.func, "id", None) == "pela_derivacao"][0]
        self.assertTrue(c.args, "a ponte deixou de receber as unidades")
        dump = ast.dump(c.args[0])
        self.assertIn("PARA_A_DERIVACAO", dump)
        for errada in ("PARA_A_PORTA", "ACEITES", "COLHEITA"):
            self.assertNotIn(errada, dump)


class SoAObservacaoCONFIRMADAAtravessa(unittest.TestCase):
    """RECUSA NA PORTA -> NAO HA OBSERVACAO -> NAO HA O QUE DERIVAR."""

    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.a = ArmazemLocal(self.tmp)
        self.a.enviar("XX/f/DOCUMENT/bom.pdf", b"%PDF", "application/pdf")
        self.a.enviar("XX/f/DOCUMENT/mau.pdf", b"%PDF", "application/pdf")

    def test_o_recusado_sem_identidade_nao_entra_mesmo_tendo_bytes(self):
        """Os bytes dele estão no armazém — o que falta é a LINHA. Derivar a
        partir de quem o banco não confirmou seria derivar o que talvez não
        exista."""
        u, sem = ing.unidades_para_a_derivacao({
            "RAW_OBSERVATIONS": [{"RAW_OBSERVATION_ID": 1,
                                  "STORAGE_PATH": "XX/f/DOCUMENT/bom.pdf"}],
            "RECUSADOS_SEM_IDENTIDADE": [
                {"STORAGE_PATH": "XX/f/DOCUMENT/mau.pdf"}],
        }, self.a)
        self.assertEqual([x["RAW_ASSET_ID"] for x in u], [1])
        self.assertEqual(sem, [])
        self.assertNotIn("mau.pdf", " ".join(x["PDF"] for x in u))


class ATentativaPerguntaAoDono(unittest.TestCase):
    """Fixá-la em zero fazia a segunda derivação da mesma corrida colidir na
    chave `(run_id, etapa, tentativa)`, e a passagem perdia-se."""

    def test_correr_pergunta_a_proxima_tentativa_quando_nao_lhe_dizem(self):
        import rastro_da_coleta as rastro
        vistas, escritas = [], []
        antes_p, antes_r = rastro.proxima_tentativa, rastro.registrar
        rastro.proxima_tentativa = lambda b, r, e: vistas.append((r, e)) or 3
        rastro.registrar = lambda b, **k: escritas.append(k) or {"ok": 1}
        try:
            deriv.correr([], banco_do_rastro=object(), run_id="RUN-1",
                         armazem=None, memoria=None)
        finally:
            rastro.proxima_tentativa, rastro.registrar = antes_p, antes_r
        self.assertEqual(vistas, [("RUN-1", "DERIVED")])
        self.assertEqual(escritas[0]["tentativa"], 3)

    def test_quem_diz_a_tentativa_manda_e_o_dono_nao_e_perguntado(self):
        import rastro_da_coleta as rastro
        vistas, escritas = [], []
        antes_p, antes_r = rastro.proxima_tentativa, rastro.registrar
        rastro.proxima_tentativa = lambda b, r, e: vistas.append(1) or 9
        rastro.registrar = lambda b, **k: escritas.append(k) or {"ok": 1}
        try:
            deriv.correr([], banco_do_rastro=object(), run_id="RUN-1",
                         armazem=None, memoria=None, tentativa=0)
        finally:
            rastro.proxima_tentativa, rastro.registrar = antes_p, antes_r
        self.assertEqual(vistas, [])
        self.assertEqual(escritas[0]["tentativa"], 0)

    def test_sem_banco_nao_se_pergunta_nada_a_ninguem(self):
        """AUSENCIA DE RASTRO E AUSENCIA. Sem banco não há a quem perguntar."""
        r = deriv.correr([], banco_do_rastro=None, run_id="RUN-1",
                         armazem=None, memoria=None)
        self.assertEqual(r["RASTRO"], "NAO_EMITIDO")
        self.assertEqual(r["ETAPAS_EMITIDAS"], [])


if __name__ == "__main__":
    unittest.main()
