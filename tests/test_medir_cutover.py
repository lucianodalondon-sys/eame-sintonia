"""X1 — os medidores do cutover decidem o que dizem decidir (dados sinteticos)."""
from __future__ import annotations

import hashlib
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
_s = importlib.util.spec_from_file_location("medir_cutover", RAIZ / "ferramentas" / "cutover" / "medir_cutover.py")
M = importlib.util.module_from_spec(_s)
_s.loader.exec_module(M)
_p = importlib.util.spec_from_file_location("passos_do_cutover", RAIZ / "ferramentas" / "cutover" / "passos_do_cutover.py")
P = importlib.util.module_from_spec(_p)
_p.loader.exec_module(P)


def _t(sid, estado):
    return {"SOURCE_ID": sid, "NEW_STATE": estado}


class TestMedidores(unittest.TestCase):
    def test_so_de_um_lado_conta_o_que_a_troca_deitaria_fora(self):
        viva = [{"ID": i} for i in range(10)]
        linha = [{"ID": i} for i in range(6)]
        c = M.so_de_um_lado(viva, linha, "ID")
        self.assertEqual((c["SO_NO_PRIMEIRO"], c["SO_NO_SEGUNDO"]), (4, 0))

    def test_presa_e_so_quem_esta_em_canary_pending_sem_tarefa_aberta(self):
        tr = [_t("A", "READY_FOR_COLLECTION"), _t("A", "CANARY_PENDING"),
              _t("B", "CANARY_PENDING"), _t("C", "CANARY_PENDING"), _t("D", "READY_FOR_COLLECTION")]
        ta = [{"SOURCE_ID": "B", "STATUS": "WAITING_RETRY"}, {"SOURCE_ID": "C", "STATUS": "DONE"}]
        self.assertEqual(M.presas_sem_tarefa(tr, ta), ["A", "C"])
        self.assertEqual(M.presas_sem_tarefa(tr, ta, ("A", "D")), ["A"])

    def test_paradas_contam_por_estado_e_ignoram_finais(self):
        tr = [_t("A", "CONTRACTED_CANARY_FAILED"), _t("B", "READY_FOR_COLLECTION"), _t("C", "DEGRADED")]
        self.assertEqual(M.paradas_sem_tarefa(tr, []), {"CONTRACTED_CANARY_FAILED": 1, "DEGRADED": 1})

    def test_corte_alterado_depois_de_congelado_manda_parar(self):
        with tempfile.TemporaryDirectory() as d:
            corte = Path(d) / "corte"
            corte.mkdir()
            f = corte / "italy_contracts_curator.json"
            f.write_text('{"FONTES": []}', encoding="utf-8")
            (corte / "CORTE.json").write_text(json.dumps(
                {"SHA256": {f.name: hashlib.sha256(f.read_bytes()).hexdigest()}}), encoding="utf-8")
            self.assertEqual(M.livros_corte_integro(corte)["VEREDITO"], "OK")
            f.write_text('{"FONTES": [{"SOURCE_ID": "X"}]}', encoding="utf-8")   # o pacote escreveu la
            self.assertEqual(M.livros_corte_integro(corte)["VEREDITO"], "PARAR")

    def test_levar_no_5b_nao_manda_parar_mas_nao_e_ok(self):
        r = {"A2": M._v(False, "x", falha="LEVAR_NO_5B")}
        self.assertEqual(r["A2"]["VEREDITO"], "LEVAR_NO_5B")


class TestPassosDoCutover(unittest.TestCase):
    def test_5b_candidata_da_linha_que_a_viva_nao_tem_fica_fora(self):
        linha = {"CANDIDATAS": [{"CANDIDATA_ID": "C1", "ESTADO": "POLICY_BLOCK"}, {"CANDIDATA_ID": "C9"}]}
        viva = {"CANDIDATAS": [{"CANDIDATA_ID": "C1", "ESTADO": "RECUSADA"}, {"CANDIDATA_ID": "C2"}]}
        self.assertEqual(P.candidatas_fora_da_viva(linha, viva), ["C9"])
        self.assertEqual(P.candidatas_fora_da_viva({"CANDIDATAS": linha["CANDIDATAS"][:1]}, viva), [])

    def test_5b_para_se_a_alocacao_da_linha_nao_esta_na_viva(self):
        self.assertEqual(P.alocacao_contida({"NOVAS": [{"SOURCE_ID": "A", "T": 1}]},
                                            {"NOVAS": [{"SOURCE_ID": "A", "T": 1}, {"SOURCE_ID": "B"}]}), [])
        self.assertEqual(P.alocacao_contida({"NOVAS": [{"SOURCE_ID": "A", "T": 1}, {"SOURCE_ID": "Z"}]},
                                            {"NOVAS": [{"SOURCE_ID": "A", "T": 2}]}), ["A", "Z"])

    def test_5b_so_copia_a_viva_se_ela_contem_a_linha(self):
        with tempfile.TemporaryDirectory() as d:
            raiz = Path(d); (raiz / "candidatas").mkdir(); (raiz / "curadoria").mkdir(); ex = raiz / "ex"; ex.mkdir()
            cand = raiz / "candidatas" / "FONTES-CANDIDATAS.json"
            aloc = raiz / "curadoria" / "SOURCE-ID-ALLOCATION-V1.json"
            cand.write_text(json.dumps({"CANDIDATAS": [{"CANDIDATA_ID": "C1"}]}), encoding="utf-8")
            aloc.write_text(json.dumps({"NOVAS": []}), encoding="utf-8")
            (ex / "FONTES-CANDIDATAS.json").write_text(json.dumps({"CANDIDATAS": [{"CANDIDATA_ID": "C1"}, {"CANDIDATA_ID": "C2"}]}), encoding="utf-8")
            (ex / "SOURCE-ID-ALLOCATION-V1.json").write_text(json.dumps({"NOVAS": [{"SOURCE_ID": "B"}]}), encoding="utf-8")
            r = P.passo_5b(raiz, ex, escrever=False)
            self.assertEqual((r["VEREDITO"], r["ESCRITO"]), ("OK", 0))
            self.assertNotIn("C2", cand.read_text(encoding="utf-8"))
            r = P.passo_5b(raiz, ex, escrever=True)
            self.assertEqual(r["ESCRITO"], 2)
            self.assertEqual(cand.read_bytes(), (ex / "FONTES-CANDIDATAS.json").read_bytes())
            self.assertIn("B", aloc.read_text(encoding="utf-8"))
            # a linha tem um SOURCE_ID que a viva nao tem -> nada se grava
            aloc.write_text(json.dumps({"NOVAS": [{"SOURCE_ID": "Z"}]}), encoding="utf-8")
            cand.write_text(json.dumps({"CANDIDATAS": [{"CANDIDATA_ID": "C1"}]}), encoding="utf-8")
            r = P.passo_5b(raiz, ex, escrever=True)
            self.assertEqual((r["VEREDITO"], r["ESCRITO"]), ("PARAR", 0))
            self.assertIn("Z", aloc.read_text(encoding="utf-8"))
            self.assertNotIn("C2", cand.read_text(encoding="utf-8"))

    def test_5c_so_leva_a_marca_onde_a_aquisicao_e_igual(self):
        aq = {"STRATEGY": "HTML_LINK_DISCOVERY", "INDEX_URL": "https://x/n"}
        unido = [{"SOURCE_ID": "A", "ACQUISITION": aq}, {"SOURCE_ID": "B", "ACQUISITION": aq},
                 {"SOURCE_ID": "C", "ACQUISITION": aq, "CONTRATO_UNICO": {"V": 1}}]
        bot = [{"SOURCE_ID": "A", "ACQUISITION": dict(aq), "CONTRATO_UNICO": {"V": 2}},
               {"SOURCE_ID": "B", "ACQUISITION": {**aq, "INDEX_URL": "https://x/"}, "CONTRATO_UNICO": {"V": 2}},
               {"SOURCE_ID": "C", "ACQUISITION": aq, "CONTRATO_UNICO": {"V": 2}}]
        self.assertEqual(P.marcas_a_levar(unido, bot), ["A"])

    def test_5c_escreve_e_a_segunda_corrida_nao_muda_nada(self):
        aq = {"STRATEGY": "S"}
        with tempfile.TemporaryDirectory() as d:
            raiz = Path(d); (raiz / "curadoria").mkdir()
            livro = raiz / "curadoria" / "italy_contracts_curator.json"
            livro.write_text(json.dumps({"FONTES": [{"SOURCE_ID": "A", "ACQUISITION": aq}]}), encoding="utf-8")
            bot = raiz / "bot.json"
            bot.write_text(json.dumps({"FONTES": [{"SOURCE_ID": "A", "ACQUISITION": aq,
                                                   "CONTRATO_UNICO": {"PRECISA_DE_REMEDIR": True}}]}), encoding="utf-8")
            self.assertEqual(P.passo_5c(raiz, bot, escrever=False)["ESCRITO"], 0)
            self.assertNotIn("CONTRATO_UNICO", livro.read_text(encoding="utf-8"))
            self.assertEqual(P.passo_5c(raiz, bot, escrever=True)["ESCRITO"], 1)
            self.assertIn("PRECISA_DE_REMEDIR", livro.read_text(encoding="utf-8"))
            self.assertEqual(P.passo_5c(raiz, bot, escrever=True)["LEVADAS"], [])

    def test_7b_apanha_toda_a_d10_presa_marcada_ou_nao(self):
        # IT-T5-049 nao tem marca CONTRATO_UNICO e ficou presa na mesma (ensaio 3)
        with tempfile.TemporaryDirectory() as d:
            raiz = Path(d); cur = raiz / "curadoria"; cur.mkdir()
            tr = [_t("IT-T5-049", "READY_FOR_COLLECTION"), _t("IT-T5-049", "CANARY_PENDING"),
                  _t("IT-T7-017", "CANARY_PENDING"), _t("IT-T7-033", "CANARY_PENDING"),
                  _t("IT-T9-001", "CANARY_PENDING")]
            ta = [{"SOURCE_ID": "IT-T7-033", "STATUS": "PENDING"}]
            (cur / "LIFECYCLE-LEDGER-V1.json").write_text(json.dumps({"TRANSICOES": tr}), encoding="utf-8")
            (cur / "LIFECYCLE-QUEUE-V1.json").write_text(json.dumps({"TAREFAS": ta}), encoding="utf-8")
            r = P.passo_7b(raiz, escrever=False)
            self.assertEqual(r["PRESAS"], ["IT-T5-049", "IT-T7-017"])
            self.assertEqual(r["ENFILEIRADAS"], [])


if __name__ == "__main__":
    unittest.main()
