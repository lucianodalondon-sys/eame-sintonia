# -*- coding: utf-8 -*-
"""O RUNTIME OBEDECE AO ENVELOPE, E NÃO AO CHEIRO DO DADO.

Doze ataques contra `orquestrador.o_envelope()` / `a_colheita()`. Todos montam
um retorno com cara de colheita e verificam que ele **não** atravessa.

    ANTES:  253 pseudo-itens atravessavam, e o sistema nao sabia.
    DEPOIS: a especie vem DECLARADA, e so `COLHEITA` passa.

Nenhuma trava aqui aceita nome de ficheiro, nome de pasta, extensão, «a
primeira lista do JSON» ou «a lista mais cheia» como argumento. Se alguma
aceitasse, ela estaria a reconstruir a heurística que a lei veio fechar.
"""
import json
import os
import shutil
import sys
import tempfile
import unittest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)
import _gavetas  # noqa: E402,F401
import orquestrador as orq  # noqa: E402
import retorno_da_coleta as rdc  # noqa: E402


class Bancada(unittest.TestCase):
    """Cada ataque monta o seu retorno dentro da árvore e apaga-o a seguir."""

    def setUp(self):
        self.dir = tempfile.mkdtemp(prefix=".ataque-505-", dir=os.path.join(RAIZ, "data"))
        self.addCleanup(shutil.rmtree, self.dir, True)
        self.rel = os.path.relpath(self.dir, RAIZ).replace(os.sep, "/")

    def escrever(self, nome, corpo):
        caminho = os.path.join(self.dir, nome)
        with open(caminho, "w", encoding="utf-8") as f:
            json.dump(corpo, f, ensure_ascii=False)
        return "%s/%s" % (self.rel, nome)

    def executor(self, **kw):
        base = {"id": "ataque", "roda": ["coleta/ataque.py"], "larga_em": [self.rel]}
        base.update(kw)
        return base

    def passa(self, e):
        itens, _ = orq.a_colheita(e, "RUN-ATAQUE")
        return itens


class OsDozeAtaques(Bancada):

    # 1 · manifesto com uma lista chamada ITEMS
    def test_1_manifesto_com_lista_items_nao_atravessa(self):
        onde = self.escrever("m.json", {"ITEMS": [{"a": 1}] * 163})
        e = self.executor(retorno={"LEGADO": {onde: rdc.MANIFEST}})
        self.assertEqual(self.passa(e), [])

    # 2 · catálogo com campo texto
    def test_2_catalogo_com_texto_nao_atravessa(self):
        onde = self.escrever("c.json", {"ACCOUNTS": [{"texto": "parece prosa"}]})
        e = self.executor(retorno={"LEGADO": {onde: rdc.CATALOG}})
        self.assertEqual(self.passa(e), [])

    # 3 · lista cheia ao lado de COLHEITA vazia — o contraexemplo histórico
    def test_3_lista_cheia_ao_lado_de_colheita_vazia(self):
        onde = self.escrever("env.json", {
            "RUN_ID": "RUN-ATAQUE", "EXECUTOR_ID": "x", "EXECUTOR_VERSION": "v",
            "ESTADO": rdc.SUCCESS, "COLHEITA": [], "SUPORTE": [], "ERROS": [],
            "CONTAS": [{"ACCOUNT_HANDLE": "@a"}] * 74})
        e = self.executor(retorno={"ENVELOPE": onde})
        self.assertEqual(self.passa(e), [],
                         "a lista cheia ao lado nao pode substituir a COLHEITA vazia")

    # 4 · ficheiro chamado harvest.json que é MANIFEST
    def test_4_o_nome_do_ficheiro_nao_promove_nada(self):
        onde = self.escrever("harvest.json", {"ITEMS": [{"texto": "x"}]})
        e = self.executor(retorno={"LEGADO": {onde: rdc.MANIFEST}})
        self.assertEqual(self.passa(e), [])

    # 5 · COLHEITA declarada sem payload
    def test_5_colheita_sem_payload_nao_atravessa(self):
        onde = self.escrever("env.json", {
            "RUN_ID": "RUN-ATAQUE", "EXECUTOR_ID": "x", "EXECUTOR_VERSION": "v",
            "ESTADO": rdc.SUCCESS, "SUPORTE": [], "ERROS": [],
            "COLHEITA": [{"ESPECIE": rdc.COLHEITA, "SOURCE_ID": "IT-T2-002",
                          "DOCUMENT_ID": "D1"}]})
        e = self.executor(retorno={"ENVELOPE": onde})
        self.assertEqual(self.passa(e), [])

    # 6 · payload AUSENTE — declarado, e não é erro nem item fabricado
    def test_6_payload_ausente_e_estado_e_nao_pseudo_item(self):
        onde = self.escrever("env.json", {
            "RUN_ID": "RUN-ATAQUE", "EXECUTOR_ID": "x", "EXECUTOR_VERSION": "v",
            "ESTADO": rdc.SUCCESS, "SUPORTE": [], "ERROS": [],
            "COLHEITA": [{"ESPECIE": rdc.COLHEITA, "SOURCE_ID": "IT-T2-002",
                          "DOCUMENT_ID": "D1", "texto": "prosa",
                          "PAYLOAD": {"ONDE": "nao/existe.pdf",
                                      "ESTADO": rdc.AUSENTE}}]})
        e = self.executor(retorno={"ENVELOPE": onde})
        # A unidade e legitima: o payload esta AUSENTE e isso esta DECLARADO.
        self.assertEqual(len(self.passa(e)), 1)

    def test_6b_mentir_sobre_o_payload_fecha_o_envelope_inteiro(self):
        onde = self.escrever("env.json", {
            "RUN_ID": "RUN-ATAQUE", "EXECUTOR_ID": "x", "EXECUTOR_VERSION": "v",
            "ESTADO": rdc.SUCCESS, "SUPORTE": [], "ERROS": [],
            "COLHEITA": [{"ESPECIE": rdc.COLHEITA, "SOURCE_ID": "IT-T2-002",
                          "DOCUMENT_ID": "D1",
                          "PAYLOAD": {"ONDE": "nao/existe.pdf",
                                      "ESTADO": rdc.PRESENTE}}]})
        e = self.executor(retorno={"ENVELOPE": onde})
        self.assertEqual(self.passa(e), [])

    # 7 · UNKNOWN
    def test_7_unknown_nunca_atravessa(self):
        onde = self.escrever("u.json", {"L": [{"texto": "x"}]})
        e = self.executor(retorno={"LEGADO": {onde: rdc.ESPECIE_DESCONHECIDA}})
        self.assertEqual(self.passa(e), [])

    # 8 · EMPTY_SUCCESS
    def test_8_zero_colheita_com_sucesso_nao_e_erro(self):
        onde = self.escrever("env.json", {
            "RUN_ID": "RUN-ATAQUE", "EXECUTOR_ID": "x", "EXECUTOR_VERSION": "v",
            "ESTADO": rdc.SUCCESS, "COLHEITA": [], "SUPORTE": [], "ERROS": []})
        e = self.executor(retorno={"ENVELOPE": onde})
        envelope, _ = orq.o_envelope(e, "RUN-ATAQUE")
        self.assertEqual(rdc.conferir(envelope, RAIZ), [])
        self.assertEqual(self.passa(e), [])

    # 9 · ERROR
    def test_9_erro_nao_e_sucesso_vazio(self):
        onde = self.escrever("env.json", {
            "RUN_ID": "RUN-ATAQUE", "EXECUTOR_ID": "x", "EXECUTOR_VERSION": "v",
            "ESTADO": rdc.FAILED, "COLHEITA": [], "SUPORTE": [],
            "ERROS": ["a fonte respondeu 503"]})
        e = self.executor(retorno={"ENVELOPE": onde})
        envelope, _ = orq.o_envelope(e, "RUN-ATAQUE")
        self.assertEqual(envelope["ESTADO"], rdc.FAILED)
        self.assertTrue(envelope["ERROS"])
        self.assertEqual(self.passa(e), [])

    # 10 · suporte e colheita na mesma corrida
    def test_10_suporte_e_colheita_convivem_e_so_uma_passa(self):
        pdf = os.path.join(self.dir, "doc.pdf")
        open(pdf, "w").write("bytes")
        onde = self.escrever("env.json", {
            "RUN_ID": "RUN-ATAQUE", "EXECUTOR_ID": "x", "EXECUTOR_VERSION": "v",
            "ESTADO": rdc.SUCCESS, "ERROS": [],
            "COLHEITA": [{"ESPECIE": rdc.COLHEITA, "SOURCE_ID": "IT-T2-002",
                          "DOCUMENT_ID": "D1", "texto": "prosa",
                          "PAYLOAD": {"ONDE": "%s/doc.pdf" % self.rel,
                                      "ESTADO": rdc.PRESENTE}}],
            "SUPORTE": [{"ESPECIE": rdc.MANIFEST, "ONDE": "m.json"},
                        {"ESPECIE": rdc.RUN_RECEIPT, "ONDE": "r.json"}]})
        e = self.executor(retorno={"ENVELOPE": onde})
        envelope, _ = orq.o_envelope(e, "RUN-ATAQUE")
        self.assertEqual(len(self.passa(e)), 1)
        self.assertEqual(len(envelope["SUPORTE"]), 2)

    # 11 · mesmo conteúdo em duas observações legítimas
    def test_11_mesmo_sha_em_duas_unidades_e_legitimo(self):
        sha = "2e488a8232ba" + "0" * 52
        u = lambda d: {"ESPECIE": rdc.COLHEITA, "SOURCE_ID": "IT-T3-005",
                       "DOCUMENT_ID": d, "SHA256": sha, "texto": "prosa",
                       "PAYLOAD": {"ONDE": "", "ESTADO": rdc.PAYLOAD_NAO_SE_APLICA}}
        onde = self.escrever("env.json", {
            "RUN_ID": "RUN-ATAQUE", "EXECUTOR_ID": "x", "EXECUTOR_VERSION": "v",
            "ESTADO": rdc.SUCCESS, "SUPORTE": [], "ERROS": [],
            "COLHEITA": [u("TERRETRURIA_A"), u("TERRETRURIA_B")]})
        e = self.executor(retorno={"ENVELOPE": onde})
        self.assertEqual(len(self.passa(e)), 2, "SHA256 NAO E IDENTIDADE DOCUMENTAL")

    # 12 · RUN_ID divergente
    def test_12_run_id_divergente_fecha_o_envelope(self):
        onde = self.escrever("env.json", {
            "RUN_ID": "RUN-ATAQUE", "EXECUTOR_ID": "x", "EXECUTOR_VERSION": "v",
            "ESTADO": rdc.SUCCESS, "SUPORTE": [], "ERROS": [],
            "COLHEITA": [{"ESPECIE": rdc.COLHEITA, "SOURCE_ID": "IT-T2-002",
                          "DOCUMENT_ID": "D1", "RUN_ID": "OUTRA-CORRIDA",
                          "texto": "prosa",
                          "PAYLOAD": {"ONDE": "", "ESTADO": rdc.PAYLOAD_NAO_SE_APLICA}}]})
        e = self.executor(retorno={"ENVELOPE": onde})
        self.assertEqual(self.passa(e), [],
                         "saida de outra corrida nao se atribui a esta")


class OSilencioTemNome(Bancada):
    """Um retorno que ninguém declarou não é um retorno vazio."""

    def test_sem_declaracao_nada_atravessa(self):
        self.escrever("qualquer.json", {"L": [{"texto": "x"}] * 99})
        e = self.executor()          # sem `retorno`
        self.assertEqual(self.passa(e), [])

    def test_sem_declaracao_o_recibo_diz_porque(self):
        e = self.executor()
        envelope, _ = orq.o_envelope(e, "RUN-ATAQUE")
        self.assertTrue(envelope.get("RETORNO_NAO_DECLARADO"))
        self.assertIn("nao declara", envelope.get("PORQUE_ZERO_COLHEITA") or "")

    def test_o_legado_nao_pode_declarar_colheita(self):
        onde = self.escrever("c.json", {"L": [{"texto": "x"}]})
        e = self.executor(retorno={"LEGADO": {onde: rdc.COLHEITA}})
        envelope, _ = orq.o_envelope(e, "RUN-ATAQUE")
        self.assertEqual(self.passa(e), [])
        self.assertTrue(any("so pode declarar suporte" in m
                            for m in envelope["ERROS"]), envelope["ERROS"])


class ANenhumaHeuristicaSobrou(unittest.TestCase):
    """A trava que impede a heurística de voltar por distracção.

    ⚠️ A PRIMEIRA VERSAO DESTA TRAVA PROCURAVA TEXTO NO FICHEIRO, e acusava o
    proprio docstring que CITA a heuristica antiga para explicar o conserto.

        PROCURAR TEXTO NUM FICHEIRO DE CODIGO APANHA A EXPLICACAO,
        E UMA EXPLICACAO HONESTA CITA O QUE FOI CONSERTADO.

    Agora percorre-se a árvore sintáctica: só código que corre conta. Comentário
    e docstring ficam de fora, que é onde a história deve poder viver.
    """

    @classmethod
    def setUpClass(cls):
        import ast
        caminho = os.path.join(RAIZ, "orquestrador", "orquestrador.py")
        with open(caminho, encoding="utf-8") as f:
            cls.fonte = f.read()
        arvore = ast.parse(cls.fonte)
        # fora todos os docstrings, para sobrar so o que executa
        for no in ast.walk(arvore):
            if isinstance(no, (ast.Module, ast.FunctionDef, ast.AsyncFunctionDef,
                               ast.ClassDef)) and ast.get_docstring(no):
                no.body = no.body[1:]
        cls.codigo = ast.unparse(arvore)

    def test_o_orquestrador_nao_decide_por_forma_do_json(self):
        for proibido in ("isinstance(v, list)", "isinstance(x[0], dict)",
                         "isinstance(d, list)"):
            self.assertNotIn(
                proibido, self.codigo,
                "a heuristica de forma voltou ao codigo do orquestrador: %s"
                % proibido)

    def test_o_orquestrador_nao_varre_pastas_a_procura_de_json(self):
        for proibido in ("glob('*.json')", 'glob("*.json")'):
            self.assertNotIn(
                proibido, self.codigo,
                "o orquestrador voltou a varrer a pasta: %s" % proibido)

    def test_a_lei_esta_importada_e_nao_copiada(self):
        self.assertIn("import retorno_da_coleta as rdc", self.codigo)
        for nome in ("MANIFEST", "CATALOG", "RUN_RECEIPT", "PLAN"):
            self.assertNotIn(
                "%s = '" % nome, self.codigo,
                "a especie %s foi redefinida no orquestrador" % nome)

    def test_quem_classifica_e_a_lei(self):
        """A decisão final tem de sair de `so_o_que_entra`, e de mais nada."""
        self.assertIn("rdc.so_o_que_entra(envelope)", self.codigo)
        self.assertIn("rdc.conferir(envelope", self.codigo)


if __name__ == "__main__":
    unittest.main()
