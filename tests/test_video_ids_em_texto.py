# -*- coding: utf-8 -*-
"""A fase `video-youtube` recebe os IDs como TEXTO pelo workflow («--filtro videos='a,b,c'»).

Medido a seco (PEDIDO-API-125, 26/09): sem traducao, `videos.list` iterava o texto e pedia «IDs» de
uma letra — 0 videos e quota gasta. O adaptador traduz a forma: texto -> lista. Sem rede.
"""
import sys
import unittest
from pathlib import Path
from unittest import mock

RAIZ = Path(__file__).resolve().parents[1]
for p in ("coleta", "leis", "ferramentas", ""):
    sys.path.insert(0, str(RAIZ / p) if p else str(RAIZ))
import adaptador_youtube as A   # noqa: E402
import youtube_oficial as yt    # noqa: E402


class IdsEmTexto(unittest.TestCase):
    def correr(self, video_ids):
        recebido = {}

        def falso(*, video_ids, **_):
            recebido["IDS"] = video_ids
            return [], None, {}
        fn = getattr(A.youtube_metadata, "__wrapped__", A.youtube_metadata)
        with mock.patch.object(yt, "metadata", side_effect=falso):
            fn(video_ids=video_ids, run_id="R", country_scope="IT")
        return recebido["IDS"]

    def test_texto_com_virgulas_vira_lista_de_ids(self):
        self.assertEqual(["1SpP29BM1_M", "-k02-HKAQvw"], self.correr("1SpP29BM1_M, -k02-HKAQvw,"))

    def test_lista_fica_como_esta(self):
        self.assertEqual(["1SpP29BM1_M"], self.correr(["1SpP29BM1_M"]))


if __name__ == "__main__":
    unittest.main()
