# -*- coding: utf-8 -*-
"""Rodada automatica FAST com o cruzamento comercial ligado (sem LLM, sem banco).

 - selecao: alterna SOURCE_ID e limita por fonte (defeito medido: 20/20 RAW de uma vinicola);
 - o cruzamento comercial le a rodada automatica (FACTS_FAST/SIGNALS_FAST) so com fatos aceitos e
   campos cujo trecho foi achado no RAW;
 - passo3 nao decide oportunidade (substituido, nao em paralelo).
"""
import importlib.util
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)
from motor import fast_cruzamento_comercial as FC  # noqa: E402

spec = importlib.util.spec_from_file_location("rodada_fast", os.path.join(RAIZ, "motor", "fast_auto", "rodada_fast.py"))
RF = importlib.util.module_from_spec(spec)
spec.loader.exec_module(RF)


class Selecao(unittest.TestCase):
    def test_uma_fonte_nao_ocupa_a_rodada(self):
        novos = [{"id": 100 - i, "source_id": "VINICOLA"} for i in range(20)] + \
                [{"id": 50, "source_id": "B"}, {"id": 49, "source_id": "C"}]
        out = RF.alternar_fontes(novos, 20, 2)
        self.assertEqual([r["source_id"] for r in out].count("VINICOLA"), 2)
        self.assertEqual({r["source_id"] for r in out}, {"VINICOLA", "B", "C"})
        self.assertEqual(len(out), 4)  # o resto espera a proxima rodada

    def test_alterna_mais_novo_primeiro_e_respeita_max(self):
        novos = [{"id": 9, "source_id": "A"}, {"id": 8, "source_id": "A"}, {"id": 7, "source_id": "B"},
                 {"id": 6, "source_id": "C"}, {"id": 5, "source_id": "B"}]
        self.assertEqual([r["id"] for r in RF.alternar_fontes(novos, 20, 2)], [9, 7, 6, 8, 5])
        self.assertEqual([r["id"] for r in RF.alternar_fontes(novos, 2, 2)], [9, 7])

    def test_contraprova_sem_limite_passa_tudo(self):
        novos = [{"id": i, "source_id": "A"} for i in range(5)]
        self.assertEqual(len(RF.alternar_fontes(novos, 20, 99)), 5)


def _campo(v, ok=True):
    return {"VALOR": v, "TRECHO": "trecho de " + v,
            "VERIFICACAO": "TRECHO_ENCONTRADO_NO_RAW" if ok else "REJEITADO_TRECHO_NAO_EXISTE_NO_RAW"}


class LeituraDaRodadaAutomatica(unittest.TestCase):
    def setUp(self):
        self.d = Path(tempfile.mkdtemp())
        base = {"DOCUMENT_ID": "RAW-1", "SOURCE_ID": "S-A", "URL": "https://a.it/x", "TIPO": "PRAGA_DOENCA"}
        nao = {"VALOR": "NAO_SEI", "TRECHO": None, "VERIFICACAO": "NAO_SEI"}
        fatos = [
            dict(base, FACT_ID="F-RAW-1-01", ESTADO="ACEITO_COM_CAMPOS_REJEITADOS", O_QUE=_campo("peronospora"),
                 ONDE=_campo("Veneto"), QUANDO=nao, CULTURA=_campo("vite"), PRAGA_DOENCA=_campo("inventada", False),
                 PRODUTO_OU_EMPRESA=nao, NUMERO=nao),
            dict(base, FACT_ID="F-RAW-1-02", ESTADO="REJEITADO", O_QUE=_campo("x", False), ONDE=nao, QUANDO=nao,
                 CULTURA=nao, PRAGA_DOENCA=nao, PRODUTO_OU_EMPRESA=nao, NUMERO=nao),
        ]
        (self.d / "FACTS_FAST.json").write_text(json.dumps({"FATOS": fatos}), encoding="utf-8")
        (self.d / "SIGNALS_FAST.json").write_text(json.dumps({"SINAIS": [
            {"SIGNAL_ID": "S-01", "TITULO": "t", "O_QUE_ACONTECEU": "d", "FACT_IDS": ["F-RAW-1-01"],
             "VALIDACAO": "OK_FATOS_EXISTEM"},
            {"SIGNAL_ID": "S-02", "FACT_IDS": ["F-X"], "VALIDACAO": "REJEITADO_FACT_ID_INEXISTENTE:F-X"}]}),
            encoding="utf-8")
        (self.d / "OPPORTUNITIES_FAST.json").write_text(json.dumps({"OPORTUNIDADES": []}), encoding="utf-8")

    def test_le_so_aceitos_e_campos_verificados(self):
        fatos, sinais, opps = FC.ler_remessa(self.d)
        self.assertEqual(list(fatos), ["F-RAW-1-01"])
        f = fatos["F-RAW-1-01"]
        self.assertEqual(f["cultura"], "vite")
        self.assertEqual(f["problema"], "NAO_SEI")  # trecho nao achado no RAW nao chega ao Opus
        self.assertEqual(f["quando"], "NAO_SEI")
        self.assertEqual(f["evidencias"]["fato"], "trecho de peronospora")
        self.assertEqual([s["SIGNAL_ID"] for s in sinais], ["S-01"])
        self.assertEqual(opps, [])
        self.assertEqual(FC.entradas(self.d), FC.ENTRADA_FAST_AUTO)

    def test_prompt_monta_sem_candidatas(self):
        fatos, sinais, opps = FC.ler_remessa(self.d)
        linha = FC.linha_fato(fatos["F-RAW-1-01"])
        self.assertIn("cultura=vite", linha)
        self.assertIn("problema=NAO_SEI", linha)


class Passo3NaoDecideOportunidade(unittest.TestCase):
    def test_passo3_so_sinais(self):
        p = open(os.path.join(RAIZ, "motor", "fast_auto", "passo3_cruzar.py"), encoding="utf-8").read()
        self.assertIn("NAO produza oportunidades", p)
        self.assertIn("OPORTUNIDADES=[]", p)
        self.assertNotIn('"OPORTUNIDADES":[{', p)


def _ler_sinais():
    p = open(os.path.join(RAIZ, "motor", "fast_auto", "passo3_cruzar.py"), encoding="utf-8").read()
    ns = {"json": json, "re": __import__("re")}
    exec(p[p.index("def ler_sinais"):p.index("# defeito medido (FAST-20261002T030919)")], ns)
    return ns["ler_sinais"]


class Passo3LeSaidaMalFechada(unittest.TestCase):
    def test_lista_completa_sem_chave_final(self):
        # forma medida nas 2 tentativas reais: termina em "}]" sem o "}" do objeto
        r = _ler_sinais()('{"SINAIS":[{"SIGNAL_ID":"S-01","FACT_IDS":["F1"]},{"SIGNAL_ID":"S-02","FACT_IDS":[]}]')
        self.assertEqual([s["SIGNAL_ID"] for s in r["SINAIS"]], ["S-01", "S-02"])
        self.assertTrue(r["LEITURA"].startswith("SO_A_LISTA_SINAIS"))

    def test_objeto_inteiro_continua_igual(self):
        self.assertEqual(_ler_sinais()('ok {"SINAIS":[{"SIGNAL_ID":"S-01"}]} fim'), {"SINAIS": [{"SIGNAL_ID": "S-01"}]})

    def test_lista_cortada_no_meio_continua_erro(self):
        with self.assertRaises(ValueError):
            _ler_sinais()('{"SINAIS":[{"SIGNAL_ID":"S-01","FACT_IDS":["F1"')


if __name__ == "__main__":
    unittest.main()
