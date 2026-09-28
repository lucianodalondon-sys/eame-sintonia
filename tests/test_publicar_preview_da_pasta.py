#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""O gatilho do preview (correcao do dono 28/09, missao L3, item 3) — atacado.

    python3 -m unittest tests.test_publicar_preview_da_pasta -v

⚠️ DADO SINTETICO DECLARADO: as pastas daqui sao montadas pelo teste (pote = o sintetico de
tests/fixtures/pote/, ids SINT-). Nenhuma pasta real da Intelligence e lida.

Prova que:
  G0  uma pasta COMPLETA (SHA256SUMS confere, lista um MANIFESTO, o manifesto aponta um pote PARA_CLIENTE que
      o SHA256SUMS lista, com o mesmo sha) e escolhida;
  G1  uma pasta a meio (sem SHA256SUMS, SHA256SUMS sem fim de linha, byte trocado depois da soma, ficheiro
      listado e ausente, manifesto fora da soma, pote fora da soma, sha do manifesto errado) NAO e lida, e o
      publicador NAO e chamado;
  G2  so ensaio e preview: producao e recusada antes de tocar no publicador;
  G3  na raiz, a completa mais recente vence, e uma pasta inteira sem pote PARA_CLIENTE diz-se como tal.
"""
import hashlib
import json
import os
import shutil
import sys
import tempfile
import time
import unittest
from pathlib import Path
from unittest import mock

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "portoes"))
sys.path.insert(0, str(RAIZ))
import _gavetas  # noqa: E402,F401

import publicar_preview_da_pasta as G  # noqa: E402

FIX = RAIZ / "tests" / "fixtures" / "pote" / "POTE-SINTETICO-PUBLICA-SOZINHO.json"


def _sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def montar_pasta(d: Path, nome="PARA-O-CASCO-RX", para_cliente=True, somas=True, manifesto_na_soma=True,
                 pote_na_soma=True, sha_manifesto=None, fim_de_linha=True) -> Path:
    """Uma entrega no formato medido da Intelligence (R9): pote(s), MANIFESTO, e o SHA256SUMS por ultimo."""
    p = d / nome
    p.mkdir(parents=True)
    pote = FIX.read_bytes()
    (p / "POTE-RX-PARA_CLIENTE.json").write_bytes(pote)
    (p / "POTE-RX-EXPERIMENTAL.json").write_bytes(pote)
    potes = {"EXPERIMENTAL": {"ARQUIVO": "POTE-RX-EXPERIMENTAL.json", "SHA256_ARQUIVO": _sha(pote)}}
    if para_cliente:
        potes["PARA_CLIENTE"] = {"ARQUIVO": "POTE-RX-PARA_CLIENTE.json",
                                 "SHA256_ARQUIVO": sha_manifesto or _sha(pote), "OBJETOS_LIBERADOS": 2}
    man = json.dumps({"INTELLIGENCE_RUN_ID": "IR-SINT-TESTE", "POTES": potes}).encode()
    (p / "MANIFESTO-RX.json").write_bytes(man)
    if somas:
        linhas = []
        if pote_na_soma:
            linhas.append(f"{_sha(pote)} *POTE-RX-PARA_CLIENTE.json")
        linhas.append(f"{_sha(pote)} *POTE-RX-EXPERIMENTAL.json")
        if manifesto_na_soma:
            linhas.append(f"{_sha(man)} *MANIFESTO-RX.json")
        txt = "\n".join(linhas) + ("\n" if fim_de_linha else "")
        (p / G.SOMAS).write_bytes(txt.encode())
    return p


class G0_Completa(unittest.TestCase):
    def setUp(self):
        self.d = Path(tempfile.mkdtemp(prefix="teste-gatilho-"))

    def tearDown(self):
        shutil.rmtree(self.d, ignore_errors=True)

    def test_pasta_completa_e_lida(self):
        p = montar_pasta(self.d)
        c = G.conferir_pasta(p)
        self.assertTrue(c["COMPLETA"], c["MOTIVOS"])
        self.assertEqual(c["ESTADO"], "COMPLETA")
        self.assertEqual(Path(c["POTE"]).name, "POTE-RX-PARA_CLIENTE.json")
        self.assertEqual(c["INTELLIGENCE_RUN_ID"], "IR-SINT-TESTE")

    def test_crlf_e_espaco_duplo_no_formato_do_sha256sum(self):
        p = montar_pasta(self.d)
        txt = (p / G.SOMAS).read_text(encoding="utf-8").replace(" *", "  ").replace("\n", "\r\n")
        (p / G.SOMAS).write_bytes(txt.encode())
        self.assertTrue(G.conferir_pasta(p)["COMPLETA"])

    def test_chama_o_publicador_com_o_pote_para_cliente_e_o_modo(self):
        p = montar_pasta(self.d)
        with mock.patch.dict(sys.modules):
            falso = mock.MagicMock()
            falso.main.return_value = 0
            sys.modules["publicar_portal_sozinho"] = falso
            rc = G.main(["--pasta", str(p), "--modo", "preview", "--registro", str(self.d / "REG")])
        self.assertEqual(rc, 0)
        args = falso.main.call_args[0][0]
        self.assertEqual(args[args.index("--modo") + 1], "preview")
        self.assertEqual(Path(args[args.index("--pote") + 1]).name, "POTE-RX-PARA_CLIENTE.json")


class G1_Incompleta(unittest.TestCase):
    def setUp(self):
        self.d = Path(tempfile.mkdtemp(prefix="teste-gatilho-"))

    def tearDown(self):
        shutil.rmtree(self.d, ignore_errors=True)

    def incompleta(self, p, pedaco):
        c = G.conferir_pasta(p)
        self.assertFalse(c["COMPLETA"])
        self.assertIsNone(c["POTE"], "pasta incompleta nao entrega pote nenhum")
        self.assertTrue(any(pedaco in m for m in c["MOTIVOS"]), c["MOTIVOS"])
        with mock.patch.dict(sys.modules):
            falso = mock.MagicMock()
            sys.modules["publicar_portal_sozinho"] = falso
            rc = G.main(["--pasta", str(p), "--modo", "preview"])
        self.assertEqual(rc, G.SEM_PASTA)
        falso.main.assert_not_called()

    def test_sem_sha256sums(self):
        self.incompleta(montar_pasta(self.d, somas=False), "sem SHA256SUMS")

    def test_sha256sums_a_meio(self):
        self.incompleta(montar_pasta(self.d, fim_de_linha=False), "fim de linha")

    def test_byte_trocado_depois_da_soma(self):
        p = montar_pasta(self.d)
        (p / "POTE-RX-PARA_CLIENTE.json").write_bytes(FIX.read_bytes() + b" ")
        self.incompleta(p, "sha256 diferente")

    def test_ficheiro_listado_e_ausente(self):
        p = montar_pasta(self.d)
        (p / "POTE-RX-EXPERIMENTAL.json").unlink()
        self.incompleta(p, "listado e ausente")

    def test_manifesto_fora_da_soma(self):
        self.incompleta(montar_pasta(self.d, manifesto_na_soma=False), "MANIFESTO")

    def test_pote_para_cliente_fora_da_soma(self):
        self.incompleta(montar_pasta(self.d, pote_na_soma=False), "nao esta no SHA256SUMS")

    def test_sha_do_manifesto_diferente_do_ficheiro(self):
        self.incompleta(montar_pasta(self.d, sha_manifesto="0" * 64), "SHA256_ARQUIVO")

    def test_linha_mal_formada(self):
        p = montar_pasta(self.d)
        with open(p / G.SOMAS, "ab") as f:
            f.write(b"isto nao e uma soma\n")
        self.incompleta(p, "mal formada")

    def test_pasta_inteira_sem_pote_para_cliente(self):
        p = montar_pasta(self.d, para_cliente=False)
        c = G.conferir_pasta(p)
        self.assertEqual(c["ESTADO"], "SEM_POTE_PARA_CLIENTE")
        self.incompleta(p, "PARA_CLIENTE")


class G2_SoPreview(unittest.TestCase):
    def test_producao_e_recusada_antes_do_publicador(self):
        d = Path(tempfile.mkdtemp(prefix="teste-gatilho-"))
        try:
            p = montar_pasta(d)
            with mock.patch.dict(sys.modules):
                falso = mock.MagicMock()
                sys.modules["publicar_portal_sozinho"] = falso
                rc = G.main(["--pasta", str(p), "--modo", "producao"])
            self.assertEqual(rc, G.USO)
            falso.main.assert_not_called()
            self.assertEqual(G.MODOS_PERMITIDOS, ("ensaio", "preview"))
        finally:
            shutil.rmtree(d, ignore_errors=True)


class G3_ARaiz(unittest.TestCase):
    def test_a_completa_mais_recente_vence_e_a_incompleta_nao_conta(self):
        d = Path(tempfile.mkdtemp(prefix="teste-gatilho-"))
        try:
            velha = montar_pasta(d, "PARA-O-CASCO-R1")
            nova = montar_pasta(d, "PARA-O-CASCO-R2")
            a_meio = montar_pasta(d, "PARA-O-CASCO-R3", fim_de_linha=False)
            t = time.time()
            os.utime(velha / G.SOMAS, (t - 100, t - 100))
            os.utime(nova / G.SOMAS, (t - 50, t - 50))
            os.utime(a_meio / G.SOMAS, (t, t))
            esc, todas = G.escolher(d)
            self.assertEqual(Path(esc["PASTA"]).name, "PARA-O-CASCO-R2")
            self.assertEqual(len(todas), 3)
        finally:
            shutil.rmtree(d, ignore_errors=True)


if __name__ == "__main__":
    unittest.main()
