"""C6-REPETIDO — o SIM que a Sala FUNDIU nao e bypass.

Medido na Sala real (28/09, ciclo 26, IT-T5-025): a coleta continua parou em
C6_BYPASS porque derived:1243 (raw 2375) tem SIM no livro e nao esta na Sala.
O raw 2375 e FORWARD_IDENTIFIED com document_key
«IT-T5-025:URL:it/news/progetto-innoflorenerg» — o mesmo dos raw 166 e 299 —
e derived:58 (raw 166) esta na Sala desde 20/09, universo T5. A Sala fundiu
CERTO pela DEDUP-DOC. Aqui o caso e reconstruido e as fronteiras provadas:
outro universo, identidade nao provada e SIM que simplesmente nao pousou
continuam a reprovar.

O banco e falso mas FAZ AS JUNCOES que o SQL do C6 pede (raw por source_id e
document_key, Sala pelo raw, outra corrida) e NAO aplica os filtros de
identidade nem de universo — esses sao do Python, e e o Python que se prova.
Sem rede, sem psql.
"""
import importlib.util
import json
import re
import tempfile
import unittest
from pathlib import Path
from unittest import mock

RAIZ = Path(__file__).resolve().parents[1]
_spec = importlib.util.spec_from_file_location(
    "micro_coleta_c6", RAIZ / "scripts" / "micro_coleta" / "micro_coleta.py")
MC = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(MC)

FI = "FORWARD_IDENTIFIED"
CHAVE = "IT-T5-025:URL:it/news/progetto-innoflorenerg"
RUN_2009 = "IT-T5-025-2026-09-20-101500-aaaaaaaaaaaaaaaa"
RUN_2809 = "IT-T5-025-2026-09-28-110400-bbbbbbbbbbbbbbbb"


def _proibido(*a, **k):
    raise AssertionError(f"programa externo chamado num teste sem rede: {a[:1]}")


class Banco:
    """raw_asset, derived_artifact e sala_de_espera em memoria."""

    def __init__(self):
        # raw id -> (source_id, document_key, identity_state, run_id)
        self.raw = {166: ("IT-T5-025", CHAVE, FI, RUN_2009),
                    299: ("IT-T5-025", CHAVE, FI, "IT-T5-025-2026-09-24-090000-cccccccccccccccc"),
                    2375: ("IT-T5-025", CHAVE, FI, RUN_2809)}
        self.derived = {58: 166, 1243: 2375}                    # derived id -> raw id
        # (item_id, raw_observation_id, source_id, run_id, universo)
        self.sala = [("derived:58", 166, "IT-T5-025", RUN_2009, "T5")]

    def __call__(self, s):
        corridas = re.findall(r"'([^']+)'", s.split("not in (", 1)[1].split(")", 1)[0]) \
            if "not in (" in s else []
        if "from raw_asset r left join" in s:
            return [[str(r), self.raw[r][0], "text/html", f"XX/{r}.html", str(r), str(d), "t",
                     self.raw[r][3], "", ""]
                    for d, r in self.derived.items() if self.raw[r][3] in corridas_do(s)]
        if "count(distinct s.run_id)" in s:
            return []
        if "from derived_artifact d" in s:                 # C6: a fusao pelo DOCUMENTO
            ids = [int(x) for x in re.search(r"d\.id in \(([^)]*)\)", s).group(1).split(",")]
            out = []
            for d in ids:
                re_id = self.derived.get(d)
                if re_id is None:
                    continue
                src, chave, est, _ = self.raw[re_id]
                for rs_id, (s_src, s_chave, s_est, _) in self.raw.items():
                    if (s_src, s_chave) != (src, chave):
                        continue
                    for item, raw_obs, _, run, uni in self.sala:
                        if raw_obs == rs_id and run not in corridas:
                            out.append([f"derived:{d}", str(re_id), est or "", src, chave,
                                        item, run, uni, str(rs_id), s_est or ""])
            return out
        if "select s.item_id, s.universo, s.run_id" in s:   # C6: a fusao pelo ITEM
            itens = re.findall(r"'(derived:\d+)'", s.split("item_id in (", 1)[1].split(")", 1)[0])
            return [[i, u, r] for i, _, _, r, u in self.sala if i in itens and r not in corridas]
        if "from sala_de_espera" in s:                     # as linhas DESTA corrida
            return [[i, str(ro), src, "NAO SEI", "NAO SEI", "t", r, "1"]
                    for i, ro, src, r, u in self.sala if r in corridas_do(s)]
        raise AssertionError(s)


def corridas_do(s):
    return re.findall(r"'([^']+)'", s.split("run_id in (", 1)[1].split(")", 1)[0])


@mock.patch.object(MC.subprocess, "run", _proibido)
class TestC6Repetido(unittest.TestCase):

    def setUp(self):
        self.t = Path(tempfile.mkdtemp())
        (self.t / "XX").mkdir()
        (self.t / "XX" / "2375.html").write_bytes(
            b"<html><body><p>" + b"Il progetto Innoflorenerg continua. " * 60 + b"</p></body></html>")
        self.banco = Banco()
        self.livro = self.t / "livro.json"
        self.decisoes = [{"item": "derived:1243", "universo": "T5", "resultado": "SIM",
                          "corrida": RUN_2809}]

    def _c6(self, run=RUN_2809):
        self.livro.write_text(json.dumps({"DECISOES": self.decisoes}), encoding="utf-8")
        r = MC.relatorio([run], consulta=self.banco, livro=self.livro, armazem=self.t)
        return r, r["CRITERIOS"]["C6_ZERO_BYPASS"]

    # ── o caso real ───────────────────────────────────────────────────────
    def test_caso_real_58_1243_mesmo_documento_passa(self):
        r, c6 = self._c6()
        self.assertTrue(c6["PASSA"], c6)
        self.assertEqual(c6["SIM_FORA_DA_SALA"], [])
        self.assertEqual(c6["FUNDIDO_POR_DOCUMENTO"], ["derived:1243->derived:58"])
        self.assertEqual(c6["FUNDIDO_POR_ITEM"], [])
        p = c6["PROVA_DA_FUSAO"]["derived:1243"]
        self.assertEqual((p["SALA_ITEM"], p["SALA_RUN_ID"], p["UNIVERSO"], p["RAW"], p["SALA_RAW"],
                          p["SOURCE_ID"], p["DOCUMENT_KEY"]),
                         ("derived:58", RUN_2009, "T5", "2375", "166", "IT-T5-025", CHAVE))

    def test_a_contagem_ja_na_sala_passa_a_ver_a_fusao_por_documento(self):
        r, _ = self._c6()
        self.assertEqual(r["CONTAGENS"]["SALA_ITENS_JA_NA_SALA_POR_OUTRA_CORRIDA"], 1)
        self.assertEqual(r["CONTAGENS"]["SALA_JA_NA_SALA_PARCELAS"],
                         {"POUSOU_NAS_DUAS_CORRIDAS": 0, "FUNDIDO_POR_ITEM": 0, "FUNDIDO_POR_DOCUMENTO": 1})
        self.assertEqual(r["CONTAGENS"]["SALA_DUPLICADOS_EXEMPLOS"], ["derived:1243"])

    # ── as fronteiras: tudo isto continua a reprovar ─────────────────────
    def test_mesmo_documento_outro_universo_reprova(self):
        self.decisoes[0]["universo"] = "T7"
        _, c6 = self._c6()
        self.assertFalse(c6["PASSA"])
        self.assertEqual(c6["SIM_FORA_DA_SALA"], ["derived:1243"])
        self.assertEqual(c6["FUNDIDO_POR_DOCUMENTO"], [])
        self.assertTrue(c6["SIM_FORA_DA_SALA_PORQUE"]["derived:1243"].startswith("MESMO_DOCUMENTO_OUTRO_UNIVERSO"))

    def test_decisao_sem_universo_nao_funde(self):
        del self.decisoes[0]["universo"]
        _, c6 = self._c6()
        self.assertFalse(c6["PASSA"])
        self.assertEqual(c6["SIM_FORA_DA_SALA"], ["derived:1243"])

    def test_raw_do_item_sem_identidade_provada_reprova(self):
        """NAO SEI qual documento NUNCA funde — reprova como hoje."""
        src, chave, _, run = self.banco.raw[2375]
        self.banco.raw[2375] = (src, chave, "FORWARD_IDENTITY_UNPROVEN", run)
        _, c6 = self._c6()
        self.assertFalse(c6["PASSA"])
        self.assertEqual(c6["SIM_FORA_DA_SALA"], ["derived:1243"])
        self.assertIn("IDENTIDADE_NAO_PROVADA", c6["SIM_FORA_DA_SALA_PORQUE"]["derived:1243"])

    def test_raw_do_item_com_identidade_nula_reprova(self):
        src, chave, _, run = self.banco.raw[2375]
        self.banco.raw[2375] = (src, chave, None, run)
        _, c6 = self._c6()
        self.assertFalse(c6["PASSA"])
        self.assertIn("identity_state=NULL", c6["SIM_FORA_DA_SALA_PORQUE"]["derived:1243"])

    def test_raw_da_linha_da_sala_sem_identidade_provada_reprova(self):
        src, chave, _, run = self.banco.raw[166]
        self.banco.raw[166] = (src, chave, "FORWARD_IDENTITY_UNPROVEN", run)
        _, c6 = self._c6()
        self.assertFalse(c6["PASSA"])
        self.assertIn("LINHA_DA_SALA_SEM_IDENTIDADE_PROVADA",
                      c6["SIM_FORA_DA_SALA_PORQUE"]["derived:1243"])

    def test_sim_que_simplesmente_nao_pousou_reprova(self):
        src, _, est, run = self.banco.raw[2375]
        self.banco.raw[2375] = (src, "IT-T5-025:URL:it/news/outra-noticia", est, run)
        _, c6 = self._c6()
        self.assertFalse(c6["PASSA"])
        self.assertEqual(c6["SIM_FORA_DA_SALA"], ["derived:1243"])
        self.assertEqual(c6["SIM_FORA_DA_SALA_PORQUE"], {"derived:1243": "NAO_POUSOU"})
        self.assertEqual((c6["FUNDIDO_POR_DOCUMENTO"], c6["FUNDIDO_POR_ITEM"]), ([], []))

    def test_mesmo_documento_so_na_mesma_corrida_nao_e_fusao_de_outra_corrida(self):
        """A linha com o mesmo documento e desta corrida mas NAO e o item: nao conta."""
        self.banco.sala = [("derived:58", 166, "IT-T5-025", RUN_2809, "T5")]
        self.decisoes.append({"item": "derived:58", "universo": "T5", "resultado": "SIM",
                              "corrida": RUN_2809})
        _, c6 = self._c6()
        self.assertFalse(c6["PASSA"])
        self.assertEqual(c6["SIM_FORA_DA_SALA"], ["derived:1243"])

    def test_sala_sem_sim_no_livro_continua_a_reprovar_mesmo_com_fusao(self):
        self.banco.sala.append(("derived:77", 2375, "IT-T5-025", RUN_2809, "T5"))
        self.decisoes.append({"item": "derived:77", "universo": "T5", "resultado": "NAO",
                              "corrida": RUN_2809})
        _, c6 = self._c6()
        self.assertFalse(c6["PASSA"])
        self.assertEqual(c6["SALA_SEM_SIM_NO_LIVRO"], ["derived:77"])
        self.assertEqual(c6["FUNDIDO_POR_DOCUMENTO"], ["derived:1243->derived:58"])

    # ── a fusao pelo ITEM ────────────────────────────────────────────────
    def test_fundido_por_item_noutra_corrida_passa(self):
        self.banco.raw[2375] = ("IT-T5-025", CHAVE, "FORWARD_IDENTITY_UNPROVEN", RUN_2809)
        self.banco.sala.append(("derived:1243", 9999, "IT-T5-025", RUN_2009, "T5"))
        r, c6 = self._c6()
        self.assertTrue(c6["PASSA"], c6)
        self.assertEqual(c6["FUNDIDO_POR_ITEM"], ["derived:1243->derived:1243"])
        self.assertEqual(c6["PROVA_DA_FUSAO"]["derived:1243"]["SALA_RUN_ID"], RUN_2009)
        self.assertEqual(r["CONTAGENS"]["SALA_JA_NA_SALA_PARCELAS"]["FUNDIDO_POR_ITEM"], 1)

    def test_mesmo_item_outro_universo_reprova(self):
        self.banco.raw[2375] = ("IT-T5-025", CHAVE, "FORWARD_IDENTITY_UNPROVEN", RUN_2809)
        self.banco.sala.append(("derived:1243", 9999, "IT-T5-025", RUN_2009, "T7"))
        _, c6 = self._c6()
        self.assertFalse(c6["PASSA"])
        self.assertEqual(c6["SIM_FORA_DA_SALA"], ["derived:1243"])

    # ── o que o C6 pergunta ao banco ─────────────────────────────────────
    def test_so_select_e_o_run_id_passa_pela_forma(self):
        vistas = []

        def q(s):
            vistas.append(s)
            return self.banco(s)
        self.livro.write_text(json.dumps({"DECISOES": self.decisoes}), encoding="utf-8")
        MC.relatorio([RUN_2809], consulta=q, livro=self.livro, armazem=self.t)
        novas = [s for s in vistas if "from derived_artifact d" in s
                 or "select s.item_id, s.universo, s.run_id" in s]
        self.assertEqual(len(novas), 2)
        for s in novas:
            self.assertRegex(s, r"^\s*select\b")
            self.assertNotIn(";", s)
        with self.assertRaises(ValueError):
            MC.fusoes_na_sala(["derived:1"], {}, ["R' or '1'='1"], consulta=_proibido)

    def test_sem_sim_fora_nao_pergunta_nada_a_mais(self):
        self.assertEqual(MC.fusoes_na_sala([], {}, ["R1"], consulta=_proibido),
                         {"POR_ITEM": {}, "POR_DOCUMENTO": {}, "NAO_FUNDIDO_PORQUE": {}})


if __name__ == "__main__":
    unittest.main()
