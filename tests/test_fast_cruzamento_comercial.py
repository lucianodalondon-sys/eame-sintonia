# -*- coding: utf-8 -*-
"""O que o programa confere no cruzamento comercial FAST (sem LLM).

O raciocinio e do modelo; aqui so se prova que o programa:
 - recusa ids inventados (FACT/SIGNAL/USE/FENOLOGIA) e classe fora das quatro;
 - escreve ORIGEM por script (documento != SOURCE_ID != dominio);
 - poe o aviso de frescor sempre que um USE_ID e citado;
 - mede «verificar», OPORTUNIDADE com NAO_SEI e cruzamento de um so documento.
"""
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from motor import fast_cruzamento_comercial as FC  # noqa: E402

FATOS = {
    "d:1#F1": {"FACT_ID": "d:1#F1", "DOCUMENT_ID": "d:1", "SOURCE_ID": "S-A", "URL": "https://www.a.it/x",
               "quando": "24/09/2026", "evidencias": {"fato": "trecho um"}},
    "d:1#F2": {"FACT_ID": "d:1#F2", "DOCUMENT_ID": "d:1", "SOURCE_ID": "S-A", "URL": "https://www.a.it/x",
               "evidencias": {"fato": "trecho dois"}},
    "d:2#F1": {"FACT_ID": "d:2#F1", "DOCUMENT_ID": "d:2", "SOURCE_ID": "S-B", "URL": "https://a.it/y",
               "evidencias": {"fato": "trecho tres"}},
}
SINAIS = [{"SIGNAL_ID": "S01"}, {"SIGNAL_ID": "S02"}]
REF = {"USE_IDS": {"U1"}, "FRESCOR": "PODE_ESTAR_DESATUALIZADO",
       "CARIMBO": {"EDICAO_REGISTRO": "E1", "ULTIMA_CHECAGEM_OK": "2026-09-07", "DIAS_SEM_CHECAGEM": 25}}
FEN = {"IDS": {"IT-PHEN-001"}}


def _campos(valor="x", **ids):
    return {k: dict({"valor": valor}, **ids) for k in FC.CAMPOS}


def _obj(**kw):
    o = {"ID": "C01", "CLASSE": "LEAD", "CAMPOS": _campos(), "FACT_IDs": ["d:1#F1"], "SINAIS_CRUZADOS": []}
    o.update(kw)
    return o


def conf(*objs):
    from datetime import date
    return FC.conferir({"objetos": list(objs)}, FATOS, SINAIS, REF, FEN, hoje=date(2026, 10, 2))


class TestConferencia(unittest.TestCase):
    def test_ids_inventados_sao_rejeitados(self):
        for o, motivo in [
            (_obj(FACT_IDs=["d:9#F1"]), "FACT_ID_INEXISTENTE"),
            (_obj(SINAIS_CRUZADOS=[{"SIGNAL_ID": "S99", "ACRESCENTOU": "x"}]), "SIGNAL_ID_INEXISTENTE"),
            (_obj(CAMPOS=_campos(USE_IDs=["U-INVENTADO"])), "USE_ID_INEXISTENTE"),
            (_obj(CAMPOS=_campos(FENOLOGIA_IDs=["IT-PHEN-999"])), "FENOLOGIA_ID_INEXISTENTE"),
            (_obj(CLASSE="OPORTUNIDADE_TALVEZ"), "CLASSE_INVALIDA"),
            (_obj(FACT_IDs=[]), "SEM_FACT_ID"),
        ]:
            ok, rej = conf(o)
            self.assertEqual(ok, [], motivo)
            self.assertTrue(any(p.startswith(motivo) for p in rej[0]["PROBLEMAS"]), (motivo, rej))

    def test_contraprova_ids_reais_passam(self):
        ok, rej = conf(_obj(CAMPOS=_campos(USE_IDs=["U1"], FENOLOGIA_IDs=["IT-PHEN-001"]),
                            SINAIS_CRUZADOS=[{"SIGNAL_ID": "S01", "ACRESCENTOU": "a"}]))
        self.assertEqual(rej, [])
        self.assertEqual(len(ok), 1)

    def test_origem_separa_documento_source_e_dominio(self):
        ok, _ = conf(_obj(FACT_IDs=["d:1#F1", "d:2#F1"]))
        org = ok[0]["ORIGEM"]
        self.assertEqual(org["N_DOCUMENTOS"], 2)
        self.assertEqual(org["N_SOURCE_IDS"], 2)
        self.assertEqual(org["N_DOMINIOS"], 1)  # www.a.it == a.it: mesma origem editorial
        self.assertTrue(org["FONTES_INDEPENDENTES"].startswith("1"))

    def test_aviso_de_frescor_quando_ha_use_id(self):
        ok, _ = conf(_obj(CAMPOS=_campos(USE_IDs=["U1"])))
        self.assertEqual(ok[0]["AVISO_DE_FRESCOR_DA_BULA"]["ESTADO_FRESCOR"], "PODE_ESTAR_DESATUALIZADO")
        ok, _ = conf(_obj())
        self.assertNotIn("AVISO_DE_FRESCOR_DA_BULA", ok[0])

    def test_medidas_do_done(self):
        ok, _ = conf(_obj(ID="V", CAMPOS=_campos(valor="verificar o portfolio")))
        self.assertIn("verificar", ok[0]["CONFERENCIA"]["PALAVRAS_VERIFICAR"])
        ok, _ = conf(_obj(CLASSE="OPORTUNIDADE", CAMPOS=_campos(valor="NAO_SEI — dado nao encontrado")))
        self.assertTrue(ok[0]["CONFERENCIA"]["OPORTUNIDADE_COM_NAO_SEI"])
        ok, _ = conf(_obj(FACT_IDs=["d:1#F1", "d:1#F2"],
                          SINAIS_CRUZADOS=[{"SIGNAL_ID": "S01", "ACRESCENTOU": "a"},
                                           {"SIGNAL_ID": "S02", "ACRESCENTOU": ""}]))
        c = ok[0]["CONFERENCIA"]
        self.assertTrue(c["CRUZAMENTO_DE_UM_SO_DOCUMENTO"])
        self.assertEqual(c["SINAIS_SEM_ACRESCIMO"], ["S02"])

    def test_contraprova_limpa(self):
        # LAB 02/10: uma OPORTUNIDADE limpa tem o POR_QUE_AGORA provado por facto do ano corrente, sem inferencia
        campos = _campos()
        campos["POR_QUE_AGORA"] = {"valor": "x", "FACT_IDs": ["d:1#F1"]}
        ok, _ = conf(_obj(CLASSE="OPORTUNIDADE", FACT_IDs=["d:1#F1", "d:2#F1"], CAMPOS=campos,
                          SINAIS_CRUZADOS=[{"SIGNAL_ID": "S01", "ACRESCENTOU": "a"},
                                           {"SIGNAL_ID": "S02", "ACRESCENTOU": "b"}]))
        c = ok[0]["CONFERENCIA"]
        self.assertEqual(c["PALAVRAS_VERIFICAR"], [])
        self.assertFalse(c["OPORTUNIDADE_COM_NAO_SEI"])
        self.assertFalse(c["CRUZAMENTO_DE_UM_SO_DOCUMENTO"])


if __name__ == "__main__":
    unittest.main()
