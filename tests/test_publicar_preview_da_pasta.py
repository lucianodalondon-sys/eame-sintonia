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
sys.path.insert(0, str(RAIZ / "tests"))
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
    man = json.dumps({"INTELLIGENCE_RUN_ID": "IR-SINT-TESTE", "RESULT_STATE": "DONE", "POTES": potes}).encode()
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


def montar_entrega_l2(d: Path, estado="DONE") -> Path:
    """A entrega do disparador L2 (provas/l2/PARA-O-CASCO.md, ramo claude/l2-disparador-v1): UM pote."""
    p = d / "PARA-O-CASCO"
    p.mkdir(parents=True)
    pote = FIX.read_bytes()
    (p / "POTE.json").write_bytes(pote)
    man = json.dumps({"INTELLIGENCE_RUN_ID": "IR-SINT-L2", "RESULT_STATE": estado, "CORRIDA_SINTETICA": True,
                      "POTE": {"ARQUIVO": "POTE.json", "SHA256_ARQUIVO": _sha(pote),
                               "CONTRATO": "POTE_INTELLIGENCE_CASCO/v2"}, "VALIDAR_POTE_V2": "PASSA"}).encode()
    (p / "MANIFESTO.json").write_bytes(man)
    (p / G.SOMAS).write_bytes(f"{_sha(pote)} *POTE.json\n{_sha(man)} *MANIFESTO.json\n".encode())
    return p


class G4_AEntregaDaL2(unittest.TestCase):
    """Aviso do coordenador 28/09: a Intelligence entrega SO em curadoria/esteira/intelligence/PARA-O-CASCO/."""
    def setUp(self):
        self.d = Path(tempfile.mkdtemp(prefix="teste-gatilho-"))

    def tearDown(self):
        shutil.rmtree(self.d, ignore_errors=True)

    def chamar(self, argv, entrega):
        with mock.patch.dict(sys.modules), mock.patch.object(G, "ENTREGA", entrega):
            falso = mock.MagicMock()
            falso.main.return_value = 0
            sys.modules["publicar_portal_sozinho"] = falso
            rc = G.main(argv)
        return rc, falso

    def test_o_default_e_a_entrega(self):
        self.assertEqual(G.ENTREGA.relative_to(G.RAIZ).as_posix(), "curadoria/esteira/intelligence/PARA-O-CASCO")

    def test_entrega_l2_completa_publica_a_copia_congelada(self):
        p = montar_entrega_l2(self.d)
        c = G.conferir_pasta(p)
        self.assertTrue(c["COMPLETA"], c["MOTIVOS"])
        rc, falso = self.chamar(["--modo", "preview"], p)
        self.assertEqual(rc, 0)
        args = falso.main.call_args[0][0]
        enviado = Path(args[args.index("--pote") + 1])
        self.assertEqual(enviado.name, "POTE.json")
        self.assertNotEqual(enviado.parent.resolve(), p.resolve(), "o publicador le a copia congelada, nao a pasta viva")

    def test_entrega_a_meio_da_troca_nao_chama(self):
        rc, falso = self.chamar(["--modo", "preview"], self.d / "PARA-O-CASCO")   # entre os dois os.replace
        self.assertEqual(rc, G.SEM_PASTA)
        falso.main.assert_not_called()

    def test_result_state_ruim_nao_chama(self):
        p = montar_entrega_l2(self.d, estado="FAILED")
        self.assertIn("RESULT_STATE", " ".join(G.conferir_pasta(p)["MOTIVOS"]))
        rc, falso = self.chamar(["--modo", "preview"], p)
        self.assertEqual(rc, G.SEM_PASTA)
        falso.main.assert_not_called()

    def test_pote_trocado_depois_da_conferencia_nao_vai(self):
        p = montar_entrega_l2(self.d)
        c = G.conferir_pasta(p)
        self.assertTrue(c["COMPLETA"])
        (p / "POTE.json").write_bytes(FIX.read_bytes() + b" ")   # a Intelligence trocou a pasta no meio
        self.assertIsNone(G.congelar_pote(c, self.d / "gelo"))
        # e sem troca, a copia congelada e aceite
        self.assertIsNotNone(G.congelar_pote(G.conferir_pasta(montar_entrega_l2(self.d / "b")), self.d / "gelo2"))


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



# ── G5 · a RODADA (D156): o que a tarefa agendada corre a cada 10 min ──────────
import entrega_de_teste as ET  # noqa: E402  (tests/entrega_de_teste.py — a entrega pela forma canonica)

VAZIO = RAIZ / "tests" / "fixtures" / "pote" / "POTE-SINTETICO-VAZIO.json"


class PublicadorFalso:
    """Anota cada chamada; devolve o rc que o teste mandar e um REGISTO minimo."""
    def __init__(self, rcs=(0,)):
        self.chamadas, self.rcs = [], list(rcs)

    def __call__(self, pote, modo, registro, entrega, estado):
        rc = self.rcs.pop(0) if self.rcs else 0
        self.chamadas.append({"POTE": Path(pote), "SHA": hashlib.sha256(Path(pote).read_bytes()).hexdigest(),
                              "MODO": modo, "ENTREGA": entrega})
        reg = {"ESTADO": "PUBLICADO" if rc == 0 else "BLOQUEADO", "FIM": "2026-09-29T00:00:00",
               "IMPLANTADO": {"ID": "dpl_falso%d" % len(self.chamadas), "URL": "https://falso.vercel.app"},
               "CONFERENCIAS": [] if rc == 0 else [{"ID": "C0_POTE_V2_FORMA_E_LEI", "PASS": False}]}
        return rc, reg


class G5_ARodada(unittest.TestCase):
    def setUp(self):
        self.d = Path(tempfile.mkdtemp(prefix="teste-rodada-"))
        self.entrega = self.d / "esteira" / "PARA-O-CASCO"
        self.estado = self.d / "estado"

    def tearDown(self):
        shutil.rmtree(self.d, ignore_errors=True)

    def rodar(self, pub, modo="preview"):
        return G.rodada(self.entrega, self.estado, modo, publicar=pub)

    def linhas(self):
        return [json.loads(l) for l in (self.estado / "RODADAS.ndjson").read_text(encoding="utf-8").splitlines()]

    def test_pote_novo_valido_publica_sozinho_e_depois_igual(self):
        ET.entregar(self.entrega, FIX.read_bytes(), "demo")
        pub = PublicadorFalso()
        r = self.rodar(pub)
        self.assertEqual(r["DECISAO"], "PUBLICADA")
        self.assertEqual(pub.chamadas[0]["MODO"], "preview")
        self.assertIsNone(pub.chamadas[0]["ENTREGA"], "entrega aceite nao leva recusa")
        self.assertEqual(pub.chamadas[0]["SHA"], _sha(FIX.read_bytes()))
        self.assertTrue(r["T0"] and r["T1"] and r["DEPLOYMENT"]["ID"])
        self.assertEqual(self.rodar(pub)["DECISAO"], "IGUAL")
        self.assertEqual(len(pub.chamadas), 1, "MANIFESTO/SHA256SUMS iguais: nada acontece")
        self.assertEqual([l["DECISAO"] for l in self.linhas()], ["PUBLICADA", "IGUAL"])

    def _bom_e_depois(self, caso):
        ET.entregar(self.entrega, FIX.read_bytes(), "demo")
        pub = PublicadorFalso()
        self.rodar(pub)
        ET.entregar(self.entrega, VAZIO.read_bytes(), caso)
        r = self.rodar(pub)
        return r, pub

    def test_b1_sha_errado_mantem_o_ultimo_bom_e_diz_o_motivo(self):
        r, pub = self._bom_e_depois("sha")
        self.assertEqual(r["DECISAO"], "RECUSADA_DITA")
        ch = pub.chamadas[-1]
        self.assertEqual(ch["SHA"], _sha(FIX.read_bytes()), "o pote que volta ao ar e o ULTIMO BOM")
        self.assertEqual(ch["ENTREGA"]["ESTADO"], "RECUSADA")
        self.assertIn("sha256 diferente", " ".join(ch["ENTREGA"]["MOTIVOS"]))

    def test_b1_ficheiro_em_falta(self):
        for caso, pedaco in (("falta-pote", "listado e ausente"), ("falta-manifesto", "MANIFESTO")):
            with self.subTest(caso=caso):
                shutil.rmtree(self.d, ignore_errors=True)
                r, pub = self._bom_e_depois(caso)
                self.assertEqual(r["DECISAO"], "RECUSADA_DITA")
                self.assertEqual(pub.chamadas[-1]["SHA"], _sha(FIX.read_bytes()))
                self.assertIn(pedaco, " ".join(pub.chamadas[-1]["ENTREGA"]["MOTIVOS"]))

    def test_b1_result_state_nao_final(self):
        r, pub = self._bom_e_depois("estado")
        self.assertEqual(r["DECISAO"], "RECUSADA_DITA")
        self.assertEqual(pub.chamadas[-1]["SHA"], _sha(FIX.read_bytes()))
        self.assertIn("RESULT_STATE", " ".join(pub.chamadas[-1]["ENTREGA"]["MOTIVOS"]))

    def test_recusada_sem_ultimo_bom_nao_publica(self):
        ET.entregar(self.entrega, FIX.read_bytes(), "sha")
        pub = PublicadorFalso()
        self.assertEqual(self.rodar(pub)["DECISAO"], "RECUSADA_SEM_ULTIMO_BOM")
        self.assertEqual(pub.chamadas, [])

    def test_c1_pote_vazio_e_legitimo(self):
        ET.entregar(self.entrega, VAZIO.read_bytes(), "vazio")
        pub = PublicadorFalso()
        self.assertEqual(self.rodar(pub)["DECISAO"], "PUBLICADA")
        self.assertEqual(pub.chamadas[0]["SHA"], _sha(VAZIO.read_bytes()))

    def test_publicador_que_reprova_vira_recusa_com_o_motivo(self):
        ET.entregar(self.entrega, FIX.read_bytes(), "demo")
        pub = PublicadorFalso([0, 1, 0])
        self.rodar(pub)
        ET.entregar(self.entrega, VAZIO.read_bytes(), "vazio")
        r = self.rodar(pub)
        self.assertEqual(r["DECISAO"], "RECUSADA_DITA")
        self.assertEqual(pub.chamadas[-1]["SHA"], _sha(FIX.read_bytes()))
        self.assertIn("C0_POTE_V2_FORMA_E_LEI", " ".join(pub.chamadas[-1]["ENTREGA"]["MOTIVOS"]))

    def test_falha_do_transporte_tenta_de_novo_e_nao_gira_para_sempre(self):
        ET.entregar(self.entrega, FIX.read_bytes(), "demo")
        pub = PublicadorFalso([0, 1, 1])
        self.rodar(pub)
        ET.entregar(self.entrega, FIX.read_bytes(), "sha")
        self.assertEqual(self.rodar(pub)["DECISAO"], "RECUSADA_NAO_DITA")
        self.assertEqual(self.rodar(pub)["DECISAO"], "RECUSADA_NAO_DITA")
        self.assertEqual(self.rodar(pub)["DECISAO"], "IGUAL", "duas tentativas e desiste daquela assinatura")

    def test_parar_desliga(self):
        ET.entregar(self.entrega, FIX.read_bytes(), "demo")
        self.estado.mkdir(parents=True)
        (self.estado / "PARAR").write_text("", encoding="utf-8")
        pub = PublicadorFalso()
        self.assertEqual(self.rodar(pub)["DECISAO"], "PARADO")
        self.assertEqual(pub.chamadas, [])
        (self.estado / "PARAR").unlink()
        self.assertEqual(self.rodar(pub)["DECISAO"], "PUBLICADA")

    def test_trava_de_instancia_unica(self):
        ET.entregar(self.entrega, FIX.read_bytes(), "demo")
        self.estado.mkdir(parents=True)
        (self.estado / "TRAVA.lock").write_text("123", encoding="utf-8")
        pub = PublicadorFalso()
        self.assertEqual(self.rodar(pub)["DECISAO"], "OCUPADO")
        self.assertEqual(pub.chamadas, [])
        velho = time.time() - G.TRAVA_VELHA_S - 10
        os.utime(self.estado / "TRAVA.lock", (velho, velho))
        r = self.rodar(pub)
        self.assertEqual(r["DECISAO"], "PUBLICADA")
        self.assertIn("TRAVA_VELHA_REMOVIDA_S", r)
        self.assertFalse((self.estado / "TRAVA.lock").exists(), "a rodada solta a trava")

    def test_entrega_ausente_nao_faz_nada(self):
        pub = PublicadorFalso()
        self.assertEqual(self.rodar(pub)["DECISAO"], "AUSENTE")
        self.assertEqual(pub.chamadas, [])

    def test_producao_recusada_na_rodada(self):
        ET.entregar(self.entrega, FIX.read_bytes(), "demo")
        pub = PublicadorFalso()
        self.assertEqual(self.rodar(pub, "producao")["DECISAO"], "RECUSADO_DESTINO")
        self.assertEqual(pub.chamadas, [])
        self.assertEqual(G.main(["--rodada", "--estado", str(self.estado), "--pasta", str(self.entrega),
                                 "--modo", "producao"]), G.USO)

    def test_a_entrega_de_teste_troca_a_pasta_inteira(self):
        ET.entregar(self.entrega, FIX.read_bytes(), "demo")
        ET.entregar(self.entrega, VAZIO.read_bytes(), "vazio")
        irmaos = [x.name for x in self.entrega.parent.iterdir() if x.is_dir()]
        self.assertEqual(irmaos, ["PARA-O-CASCO"], "nada de meia pasta ao lado depois da troca")
        self.assertTrue(G.conferir_pasta(self.entrega)["COMPLETA"])


if __name__ == "__main__":
    unittest.main()
