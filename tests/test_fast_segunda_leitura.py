# -*- coding: utf-8 -*-
"""RUN-AUTO-001 (ordem do dono 03/10): SEGUNDA LEITURA automatica (passo2b_verificar.aplicar) — sem LLM (custo 0).
SUPORTADO segue; PARCIAL segue so como CLAIM/INTERPRETACAO; NAO_SUPORTADO e sem veredicto = REJEITADO;
campo nao sustentado vira NAO_SEI no cruzamento."""
import copy
import importlib.util
import sys
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("passo2b", RAIZ / "motor" / "fast_auto" / "passo2b_verificar.py")
P = importlib.util.module_from_spec(spec)
spec.loader.exec_module(P)  # main() so corre com __name__ == "__main__"
sys.path.insert(0, str(RAIZ))
from motor import fast_cruzamento_comercial as FC  # noqa: E402

OK = "TRECHO_ENCONTRADO_NO_RAW"


def fato(i, nat="FATO"):
    return {"FACT_ID": "F-%d" % i, "DOCUMENT_ID": "D1", "SOURCE_ID": "S1", "URL": "https://a.it/x", "ESTADO": "ACEITO", "NATUREZA_DA_AFIRMACAO": nat,
            "O_QUE": {"VALOR": "afirmacao %d" % i, "TRECHO": "trecho %d" % i, "VERIFICACAO": OK},
            "ONDE": {"VALOR": "Lombardia", "TRECHO": "in Lombardia", "VERIFICACAO": OK},
            "QUANDO": {"VALOR": "NAO_SEI", "TRECHO": None, "VERIFICACAO": "NAO_SEI"}}


class SegundaLeitura(unittest.TestCase):
    def test_tres_vereditos(self):
        fs = [fato(1), fato(2), fato(3)]
        cont, estranhos = P.aplicar(fs, [
            {"FACT_ID": "F-1", "VEREDICTO": "SUPORTADO", "NATUREZA": "FATO"},
            {"FACT_ID": "F-2", "VEREDICTO": "PARCIAL", "NATUREZA": "FATO", "MOTIVO": "a fonte so afirma"},
            {"FACT_ID": "F-3", "VEREDICTO": "NAO_SUPORTADO", "MOTIVO": "o texto nao diz"}])
        self.assertEqual((cont["SUPORTADO"], cont["PARCIAL"], cont["NAO_SUPORTADO"]), (1, 1, 1))
        self.assertEqual([f["ESTADO"] for f in fs], ["ACEITO", "ACEITO", "REJEITADO"])
        self.assertEqual(fs[0]["NATUREZA_DA_AFIRMACAO"], "FATO")
        self.assertEqual(fs[1]["NATUREZA_DA_AFIRMACAO"], "CLAIM_DA_FONTE")  # PARCIAL nunca segue como FATO
        self.assertEqual(estranhos, [])

    def test_sem_veredicto_e_rejeitado(self):
        fs = [fato(1), fato(2)]
        cont, _ = P.aplicar(fs, [{"FACT_ID": "F-1", "VEREDICTO": "SUPORTADO"}])
        self.assertEqual(fs[1]["ESTADO"], "REJEITADO")
        self.assertEqual(cont["NAO_VERIFICADO"], 1)
        fs = [fato(1)]
        P.aplicar(fs, None)  # chamada caiu
        self.assertEqual(fs[0]["ESTADO"], "REJEITADO")
        fs = [fato(1)]
        P.aplicar(fs, [{"FACT_ID": "F-1", "VEREDICTO": "TALVEZ"}])  # fora da lista fechada
        self.assertEqual(fs[0]["ESTADO"], "REJEITADO")

    def test_id_inventado_pelo_verificador_nao_conta(self):
        fs = [fato(1)]
        cont, estranhos = P.aplicar(fs, [{"FACT_ID": "F-99", "VEREDICTO": "SUPORTADO"}])
        self.assertEqual(estranhos, ["F-99"])
        self.assertEqual(fs[0]["ESTADO"], "REJEITADO")

    def test_campo_nao_sustentado_vira_nao_sei_no_cruzamento(self):
        fs = [fato(1)]
        P.aplicar(fs, [{"FACT_ID": "F-1", "VEREDICTO": "SUPORTADO", "CAMPOS_NAO_SUSTENTADOS": ["ONDE", "O_QUE"]}])
        self.assertEqual(fs[0]["ONDE"]["VERIFICACAO"], P.REJ_CAMPO)
        self.assertEqual(fs[0]["O_QUE"]["VERIFICACAO"], OK)  # O_QUE nao e campo: o veredicto e que decide
        import json, tempfile
        with tempfile.TemporaryDirectory() as d:
            Path(d, "FACTS_FAST.json").write_text(json.dumps({"FATOS": fs}), encoding="utf-8")
            Path(d, "SIGNALS_FAST.json").write_text(json.dumps({"SINAIS": []}), encoding="utf-8")
            fatos, _, _ = FC.ler_fast_auto(Path(d))
        self.assertEqual(fatos["F-1"]["onde"], "NAO_SEI")
        self.assertEqual(fatos["F-1"]["verificacao"], "SUPORTADO")

    def test_rejeitado_pelo_passo2_nao_e_reverificado(self):
        f = fato(1); f["ESTADO"] = "REJEITADO"
        cont, _ = P.aplicar([f], [{"FACT_ID": "F-1", "VEREDICTO": "SUPORTADO"}])
        self.assertEqual(f["ESTADO"], "REJEITADO")
        self.assertEqual(sum(cont.values()), 0)

    def test_verificador_mais_fraco_vence(self):
        fs = [fato(1)]
        P.aplicar(fs, [{"FACT_ID": "F-1", "VEREDICTO": "SUPORTADO", "NATUREZA": "CLAIM_DA_FONTE"}])
        self.assertEqual(fs[0]["NATUREZA_DA_AFIRMACAO"], "CLAIM_DA_FONTE")

    def test_verificador_nao_tem_ferramentas(self):
        src = (RAIZ / "motor" / "fast_auto" / "passo2b_verificar.py").read_text(encoding="utf-8")
        self.assertIn('"--tools", ""', src)
        self.assertIn('"--strict-mcp-config"', src)

    def test_ciclo_chama_a_segunda_leitura_antes_do_passo3(self):
        src = (RAIZ / "motor" / "fast_auto" / "rodada_fast.py").read_text(encoding="utf-8")
        self.assertIn('PASSOS = ["passo1_selecionar.py", "passo2_fatos.py", "passo2b_verificar.py", "passo3_cruzar.py"]',
                      src)


if __name__ == "__main__":
    unittest.main()
