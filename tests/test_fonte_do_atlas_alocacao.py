#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""SOC-ONDA2 — o registo de alocação do Curator é o terceiro emissor da população de SOURCE_ID."""
import json
import os
import sys
import tempfile
import unittest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(RAIZ, "leis"))

import fonte_do_atlas as fa  # noqa: E402

ATLAS_MIN = "# atlas\n\n## REGISTRO DE FONTES\n\n```\nSOURCE_ID:   IT-T2-001\n```\n"


class OTerceiroEmissor(unittest.TestCase):
    def _raiz(self, novas):
        t = tempfile.mkdtemp(prefix="pop-")
        os.makedirs(os.path.join(t, "docs", "fontes"))
        os.makedirs(os.path.join(t, "curadoria"))
        with open(os.path.join(t, fa.ATLAS), "w", encoding="utf-8") as f:
            f.write(ATLAS_MIN)
        if novas is not None:
            with open(os.path.join(t, fa.ALOCACAO), "w", encoding="utf-8") as f:
                json.dump({"NOVAS": novas}, f)
        return t

    def test_numero_cunhado_pelo_qualify_e_conhecido(self):
        t = self._raiz([{"SOURCE_ID": "IT-T9-024"}, {"SOURCE_ID": "IT-T2-132"}])
        self.assertTrue(fa.conhece("IT-T9-024", raiz=t))
        self.assertTrue(fa.conhece("IT-T2-001", raiz=t), "o Atlas continua a responder")

    def test_numero_que_ninguem_cunhou_continua_desconhecido(self):
        t = self._raiz([{"SOURCE_ID": "IT-T9-024"}])
        self.assertFalse(fa.conhece("IT-T9-025", raiz=t))
        self.assertFalse(fa.conhece("IT-T99-999", raiz=t))

    def test_linha_mal_formada_nao_entra(self):
        t = self._raiz([{"SOURCE_ID": "CAND-0101"}, {"SOURCE_ID": "IT-T9-0x"}, {}])
        self.assertEqual(fa._da_alocacao(t), set())

    def test_sem_registo_de_alocacao_e_so_o_atlas(self):
        t = self._raiz(None)
        self.assertEqual(fa.populacao(t, recarregar=True), {"IT-T2-001"})


if __name__ == "__main__":
    unittest.main(verbosity=2)
