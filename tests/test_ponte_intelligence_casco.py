#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""A PONTE INTELLIGENCE -> CASCO, ATACADA — nuvem-int-casco-ponte-v1.

    python3 -m unittest tests.test_ponte_intelligence_casco -v

⚠️ DADO SINTETICO DECLARADO. A corrida `corrida_sintetica()` abaixo e
inventada para o teste, e diz-o tres vezes: `SINTETICA: true`, todo id comeca
por `SINT-`, e ela vive so neste ficheiro. Nenhum valor dela entra no portal
nem em livro nenhum. Dado real da Sala NAO existe na nuvem; o unico dado real
aqui e a coorte versionada (research/intelligence/COORTE-DA-SALA-2026-09-14.json),
que passa pela corrida verdadeira e bloqueia em G0 — e a ponte da zero cartoes,
que e a resposta certa.
"""
import copy
import json
import sys
import tempfile
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
for p in (RAIZ, RAIZ / "pacote", RAIZ / "motor", RAIZ / "provas"):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

import ponte_intelligence_casco as P                          # noqa: E402
import corrida_da_inteligencia as CI                          # noqa: E402

NAO_SEI = P.NAO_SEI


def _prova(n):
    return {"ITEM_ID": f"SINT-ITEM-{n}", "RAW_OBSERVATION_ID": f"SINT-RAW-{n}",
            "SOURCE_ID": f"SINT-SRC-{n}", "DOCUMENT_ID": f"SINT-DOC-{n}"}


def corrida_sintetica():
    """UMA corrida sintetica declarada: tres itens passaram G0, um bloqueou."""
    linhagem = [dict(ITEM_ID=f"SINT-ITEM-{n}", RAW_OBSERVATION_ID=f"SINT-RAW-{n}",
                     SOURCE_ID=f"SINT-SRC-{n}", G0="PASSOU") for n in (1, 2, 3)]
    linhagem.append(dict(ITEM_ID="SINT-ITEM-9", RAW_OBSERVATION_ID=NAO_SEI,
                         SOURCE_ID="SINT-SRC-9", G0="BLOQUEADO_EM_G0"))
    return {
        "SCHEMA": "CORRIDA_DA_INTELLIGENCE/v2-SINTETICA",
        "SINTETICA": True,
        "INTELLIGENCE_RUN_ID": "SINT-IR-0001",
        "RESULT_STATE": "DONE",
        "LINEAGE": linhagem,
        "SIGNALS": [],
        "REQUIREMENTS": [{"REQUIREMENT_ID": "SINT-REQ-1",
                          "MISSING_FACT_OR_KEY": ["RAW_OBSERVATION_ID"]}],
        "GAPS": [{"FERRAMENTA": "voices", "GAP": "SINT: SPEAKER_ROLE sem prova de papel"},
                 {"GAP": "SINT: lacuna sem ferramenta"}],
        "ITENS_POR_FERRAMENTA": {
            "meeting": [{
                "SIGNAL_ID": "SINT-SG-1", "ESTADO": "EXPERIMENTAL_CANDIDATE",
                "CHAVES": {"CROP_ID": "SINT-vite", "ISSUE_ID": "SINT-peronospora",
                           "REGION_ID": "SINT-veneto", "TIME_WINDOW": NAO_SEI,
                           "ADAMA_PRODUCT_ID": "SINT-PROD-1",
                           "AUTHORIZATION_EVIDENCE_ID": "SINT-DOC-1",
                           "SCORE_INVENTADO": 99},
                "PROVA": [_prova(1)],
                "PORQUE": "SINT: boletim cita pressao na regiao"}],
            "windows": [{
                "SIGNAL_ID": "SINT-SG-2", "ESTADO": "EXPERIMENTAL_CANDIDATE",
                "CHAVES": {"CROP_ID": "SINT-vite", "REGION_ID": "SINT-veneto"},
                "PROVA": [_prova(2)]}],
            "voices": [{
                "SIGNAL_ID": "SINT-SG-3", "ESTADO": "EXPERIMENTAL_CANDIDATE",
                "CHAVES": {"SPEAKER_ID": "SINT-SPK-1", "SPEAKER_ROLE": "",
                           "FACT_TIME": None},
                "PROVA": [_prova(3)]}],
        },
    }


def todos_os_cartoes(payload):
    return [c for e in payload["FERRAMENTAS"].values() for c in e["CARTOES"]]


def motivos(payload):
    return {(r["FERRAMENTA"], r["SIGNAL_ID"], r["MOTIVO"]) for r in payload["RECUSADOS"]}


class A_CorridaSinteticaAtravessa(unittest.TestCase):

    def setUp(self):
        self.pl = P.adaptar(corrida_sintetica())

    def test_A1_doze_ferramentas_e_tres_cartoes(self):
        self.assertEqual(set(self.pl["FERRAMENTAS"]), set(P.FERRAMENTAS))
        self.assertEqual(len(P.FERRAMENTAS), 12)
        self.assertEqual({c["SIGNAL_ID"] for c in todos_os_cartoes(self.pl)},
                         {"SINT-SG-1", "SINT-SG-2", "SINT-SG-3"})
        self.assertEqual(self.pl["FERRAMENTAS"]["meeting"]["ESTADO"], "COM_CARTOES_EXPERIMENTAIS")
        self.assertEqual(self.pl["FERRAMENTAS"]["market"]["ESTADO"], "SEM_CARTOES_NESTA_CORRIDA")
        self.assertEqual(self.pl["FERRAMENTAS"]["archive"]["ESTADO"], "SEM_CONTRATO_D84")

    def test_A2_a_marca_esta_nos_tres_niveis(self):
        self.assertEqual(self.pl["MARCA"], "EXPERIMENTAL · NAO_PARA_CLIENTE")
        self.assertIs(self.pl["NAO_PARA_CLIENTE"], True)
        for e in self.pl["FERRAMENTAS"].values():
            self.assertEqual(e["MARCA"], P.MARCA)
            self.assertIs(e["NAO_PARA_CLIENTE"], True)
        for c in todos_os_cartoes(self.pl):
            self.assertEqual(c["MARCA"], P.MARCA)
            self.assertIs(c["NAO_PARA_CLIENTE"], True)
            self.assertEqual(c["ESTADO"], "EXPERIMENTAL_CANDIDATE")

    def test_A3_cada_cartao_leva_a_prova_ate_ao_documento(self):
        for c in todos_os_cartoes(self.pl):
            self.assertTrue(c["PROVA"])
            for p in c["PROVA"]:
                for k in ("ITEM_ID", "RAW_OBSERVATION_ID", "SOURCE_ID", "DOCUMENT_ID"):
                    self.assertTrue(p[k].startswith("SINT-"), (c["SIGNAL_ID"], k))
                self.assertEqual(p["INTELLIGENCE_RUN_ID"], "SINT-IR-0001")

    def test_A4_nao_sei_fica_escrito_por_extenso(self):
        voz = self.pl["FERRAMENTAS"]["voices"]["CARTOES"][0]
        self.assertEqual(voz["CHAVES"]["SPEAKER_ROLE"], NAO_SEI)   # veio ""
        self.assertEqual(voz["CHAVES"]["FACT_TIME"], NAO_SEI)      # veio None
        self.assertIn("FACT_LOCATION", voz["CHAVES_NAO_SEI"])      # nao veio
        self.assertEqual(voz["INCERTEZA"], NAO_SEI)
        radar = self.pl["FERRAMENTAS"]["meeting"]["CARTOES"][0]
        self.assertEqual(radar["CHAVES"]["TIME_WINDOW"], NAO_SEI)

    def test_A5_a_ponte_nao_cria_valor_nenhum(self):
        """INT-LAW-023: todo valor desenhado e do sinal, ou NAO SEI."""
        entrada = corrida_sintetica()["ITENS_POR_FERRAMENTA"]
        for f, sinais in entrada.items():
            dado = sinais[0]["CHAVES"]
            cartao = self.pl["FERRAMENTAS"][f]["CARTOES"][0]
            for k, v in cartao["CHAVES"].items():
                self.assertTrue(v == NAO_SEI or v == dado.get(k), (f, k, v))
            self.assertEqual(set(cartao["CHAVES"]), set(P.FERRAMENTAS[f]["CHAVES"]))

    def test_A6_chave_fora_do_contrato_nao_entra_nas_chaves_mas_viaja_com_valor(self):
        """Ajuste DECLARADO: defeito P4 (bot da Intelligence, 26/09) — o valor ia-se."""
        radar = self.pl["FERRAMENTAS"]["meeting"]["CARTOES"][0]
        self.assertNotIn("SCORE_INVENTADO", radar["CHAVES"])
        self.assertEqual(radar["FORA_DO_CONTRATO"], {"SCORE_INVENTADO": 99})

    def test_A7_lacunas_verbatim_e_no_sitio_certo(self):
        self.assertEqual(len(self.pl["FERRAMENTAS"]["voices"]["LACUNAS"]), 1)
        sem = self.pl["LACUNAS_SEM_FERRAMENTA"]
        self.assertEqual({g.get("REQUIREMENT_ID") or g.get("GAP") for g in sem},
                         {"SINT-REQ-1", "SINT: lacuna sem ferramenta"})

    def test_A8_a_origem_sintetica_viaja_ate_ao_cartao(self):
        self.assertIs(self.pl["ORIGEM"]["CORRIDA_SINTETICA"], True)
        for c in todos_os_cartoes(self.pl):
            self.assertIs(c["CORRIDA_SINTETICA"], True)
        sem_flag = corrida_sintetica()
        del sem_flag["SINTETICA"]
        self.assertEqual(P.adaptar(sem_flag)["ORIGEM"]["CORRIDA_SINTETICA"], NAO_SEI)

    def test_A9_o_numero_e_da_corrida_nao_do_mundo(self):
        u = self.pl["FERRAMENTAS"]["market"]["UNIVERSO"]
        self.assertEqual(u["CARTOES"], 0)
        self.assertEqual(u["INTELLIGENCE_RUN_ID"], "SINT-IR-0001")
        self.assertIn("nao prova ausencia", u["LEITURA"])


class B_OQueARecusa(unittest.TestCase):

    def _com(self, ferramenta, sinal, mexer=None):
        c = corrida_sintetica()
        c["ITENS_POR_FERRAMENTA"] = {ferramenta: [sinal]}
        if mexer:
            mexer(c)
        return P.adaptar(c)

    def _sinal(self, **kw):
        s = {"SIGNAL_ID": "SINT-SG-X", "ESTADO": "EXPERIMENTAL_CANDIDATE",
             "CHAVES": {}, "PROVA": [_prova(1)]}
        s.update(kw)
        return s

    def test_B1_sinal_sem_prova_e_recusado(self):
        for prova in (None, [], "x"):
            s = self._sinal(PROVA=prova)
            if prova is None:
                del s["PROVA"]
            pl = self._com("windows", s)
            self.assertEqual(todos_os_cartoes(pl), [])
            self.assertIn(("windows", "SINT-SG-X", "SEM_PROVA"), motivos(pl))

    def test_B2_prova_que_nao_chega_ao_documento_e_recusada(self):
        p = _prova(1)
        p["DOCUMENT_ID"] = "NAO SEI — nao lido"
        pl = self._com("windows", self._sinal(PROVA=[p]))
        self.assertEqual(todos_os_cartoes(pl), [])
        self.assertIn(("windows", "SINT-SG-X", "PROVA_INCOMPLETA"), motivos(pl))

    def test_B3_prova_fora_da_corrida_ou_contraditoria_e_recusada(self):
        pl = self._com("windows", self._sinal(PROVA=[_prova(7)]))
        self.assertIn(("windows", "SINT-SG-X", "PROVA_FORA_DA_CORRIDA"), motivos(pl))
        p = _prova(1)
        p["SOURCE_ID"] = "SINT-SRC-OUTRA"
        pl = self._com("windows", self._sinal(PROVA=[p]))
        self.assertIn(("windows", "SINT-SG-X", "PROVA_CONTRADIZ_A_CORRIDA"), motivos(pl))

    def test_B4_item_bloqueado_em_g0_nao_prova_nada(self):
        p = {"ITEM_ID": "SINT-ITEM-9", "RAW_OBSERVATION_ID": "SINT-RAW-9",
             "SOURCE_ID": "SINT-SRC-9", "DOCUMENT_ID": "SINT-DOC-9"}
        pl = self._com("windows", self._sinal(PROVA=[p]))
        self.assertIn(("windows", "SINT-SG-X", "ITEM_BLOQUEADO_EM_G0"), motivos(pl))

    def test_B5_so_experimental_candidate_atravessa_e_nada_se_promove(self):
        for estado in ("SINAL", "FINDING", "OPPORTUNITY", None):
            pl = self._com("meeting", self._sinal(ESTADO=estado))
            self.assertEqual(todos_os_cartoes(pl), [], estado)
            self.assertIn(("meeting", "SINT-SG-X", "ESTADO_NAO_TRANSPORTAVEL"), motivos(pl))

    def test_B6_ferramenta_sem_contrato_ou_desconhecida(self):
        pl = self._com("archive", self._sinal())
        self.assertIn(("archive", "SINT-SG-X", "FERRAMENTA_SEM_CONTRATO_D84"), motivos(pl))
        pl = self._com("inventada", self._sinal())
        self.assertIn(("inventada", "SINT-SG-X", "FERRAMENTA_DESCONHECIDA"), motivos(pl))

    def test_B7_duplicado_contribui_uma_vez(self):
        c = corrida_sintetica()
        c["ITENS_POR_FERRAMENTA"] = {"windows": [self._sinal(), self._sinal()]}
        pl = P.adaptar(c)
        self.assertEqual(len(todos_os_cartoes(pl)), 1)
        self.assertIn(("windows", "SINT-SG-X", "DUPLICADO_NA_FERRAMENTA"), motivos(pl))

    def test_B8_corrida_que_falhou_nao_da_cartao(self):
        for estado in ("ERROR", "NOT_RUN", "RUNNING", None):
            c = corrida_sintetica()
            c["RESULT_STATE"] = estado
            pl = P.adaptar(c)
            self.assertEqual(todos_os_cartoes(pl), [], estado)
            self.assertTrue(pl["FERRAMENTAS"]["meeting"]["ESTADO"].startswith("CORRIDA_"))

    def test_B9_corrida_sem_identidade_nao_se_adapta(self):
        c = corrida_sintetica()
        c["INTELLIGENCE_RUN_ID"] = NAO_SEI
        with self.assertRaises(P.LeiViolada):
            P.adaptar(c)

    def test_B10_sinal_do_livro_de_hoje_nao_ganha_ferramenta(self):
        c = corrida_sintetica()
        c["SIGNALS"] = [{"SIGNAL_ID": "SINT-SG-V1", "ESTADO": "SINAL"}]
        pl = P.adaptar(c)
        self.assertIn((NAO_SEI, "SINT-SG-V1", "SINAL_SEM_FERRAMENTA"), motivos(pl))


class C_AConferenciaReprova(unittest.TestCase):
    """O portao de saida le o payload como o portal o leria."""

    def setUp(self):
        self.pl = P.adaptar(corrida_sintetica())
        self.assertEqual(P.conferir_payload(self.pl), [])

    def test_C1_marca_removida_do_cartao_reprova(self):
        for mexer in (lambda c: c.pop("MARCA"),
                      lambda c: c.__setitem__("MARCA", "EXPERIMENTAL"),
                      lambda c: c.__setitem__("NAO_PARA_CLIENTE", False)):
            pl = copy.deepcopy(self.pl)
            mexer(pl["FERRAMENTAS"]["windows"]["CARTOES"][0])
            self.assertTrue(P.conferir_payload(pl))

    def test_C2_marca_removida_do_payload_ou_da_ferramenta_reprova(self):
        pl = copy.deepcopy(self.pl)
        del pl["MARCA"]
        self.assertTrue(P.conferir_payload(pl))
        pl = copy.deepcopy(self.pl)
        del pl["FERRAMENTAS"]["market"]["MARCA"]
        self.assertTrue(P.conferir_payload(pl))

    def test_C3_prova_arrancada_reprova(self):
        pl = copy.deepcopy(self.pl)
        pl["FERRAMENTAS"]["voices"]["CARTOES"][0]["PROVA"] = []
        self.assertTrue(P.conferir_payload(pl))
        pl = copy.deepcopy(self.pl)
        pl["FERRAMENTAS"]["voices"]["CARTOES"][0]["PROVA"][0]["DOCUMENT_ID"] = ""
        self.assertTrue(P.conferir_payload(pl))

    def test_C4_nao_sei_escondido_reprova(self):
        for escondido in ("", None):
            pl = copy.deepcopy(self.pl)
            pl["FERRAMENTAS"]["voices"]["CARTOES"][0]["CHAVES"]["FACT_TIME"] = escondido
            self.assertTrue(P.conferir_payload(pl))

    def test_C5_ferramenta_a_menos_ou_cartao_sem_contrato_reprova(self):
        pl = copy.deepcopy(self.pl)
        del pl["FERRAMENTAS"]["sources"]
        self.assertTrue(P.conferir_payload(pl))
        pl = copy.deepcopy(self.pl)
        pl["FERRAMENTAS"]["archive"]["CARTOES"] = [pl["FERRAMENTAS"]["windows"]["CARTOES"][0]]
        self.assertTrue(P.conferir_payload(pl))


class D_ACorridaRealDaSala(unittest.TestCase):
    """A coorte real versionada, pela corrida verdadeira, e depois pela ponte."""

    def test_D1_coorte_real_bloqueia_em_g0_e_da_zero_cartoes_com_lacunas(self):
        coorte = json.loads((RAIZ / "research" / "intelligence"
                             / "COORTE-DA-SALA-2026-09-14.json").read_text(encoding="utf-8"))
        livro = CI.correr("a ponte tem o que desenhar?", coorte["ITENS"])
        pl = P.adaptar(livro)
        self.assertEqual(todos_os_cartoes(pl), [])
        self.assertEqual(pl["ORIGEM"]["CORRIDA_SINTETICA"], NAO_SEI)
        self.assertEqual(len(pl["LACUNAS_SEM_FERRAMENTA"]), len(livro["REQUIREMENTS"]))
        self.assertTrue(livro["REQUIREMENTS"])
        self.assertEqual(P.conferir_payload(pl), [])


class E_ASaida(unittest.TestCase):

    def test_E1_nao_escreve_dentro_do_portal(self):
        destino = RAIZ / "italia-portale" / "client" / "ponte.js"
        self.assertFalse(P.destino_permitido(destino))
        with tempfile.TemporaryDirectory() as d:
            entrada = Path(d) / "corrida.json"
            entrada.write_text(json.dumps(corrida_sintetica()), encoding="utf-8")
            self.assertEqual(P.main([str(entrada), str(destino)]), 3)
            self.assertFalse(destino.exists())
            saida = Path(d) / "ponte.js"
            self.assertEqual(P.main([str(entrada), str(saida)]), 0)
            texto = saida.read_text(encoding="utf-8")
            self.assertTrue(texto.startswith("/* GERADO"))
            self.assertIn("window.SINTONIA_PONTE_EXPERIMENTAL = ", texto)
            self.assertIn(P.MARCA, texto)


class F_APaginaLocal(unittest.TestCase):
    """A pagina local desenha a marca, a prova e o NAO SEI — e nao executa dado."""

    def setUp(self):
        c = corrida_sintetica()
        c["ITENS_POR_FERRAMENTA"]["windows"][0]["PORQUE"] = "<script>alert(1)</script>"
        self.pl = P.adaptar(c)
        self.html = P.como_html(self.pl, css_href="styles.css")

    def test_F1_faixa_no_topo_e_marca_em_cada_cartao(self):
        corpo = self.html.split("<body>", 1)[1]
        self.assertTrue(corpo.startswith(f'<div class="faixa" data-marca="1">{P.MARCA}'))
        self.assertEqual(self.html.count('<span class="marca" data-marca="1">'),
                         len(todos_os_cartoes(self.pl)))

    def test_F2_prova_e_nao_sei_a_vista(self):
        self.assertIn("DOCUMENT_ID SINT-DOC-3", self.html)
        self.assertIn(f'<span class="naosei">{NAO_SEI}</span>', self.html)

    def test_F3_texto_da_corrida_e_escapado(self):
        self.assertNotIn("<script>alert(1)</script>", self.html)
        self.assertIn("&lt;script&gt;", self.html)

    def test_F4_css_e_o_extrato_adama_ligado(self):
        self.assertTrue(P.CSS_ADAMA.exists())
        self.assertIn(P.CSS_ADAMA.resolve().as_uri(), P.como_html(self.pl))


class G_OCascoNoArEALinhagemReal(unittest.TestCase):
    """O que o bot da Intelligence achou ao correr a ponte na R2 real (26/09)."""

    def test_G1_as_doze_sao_as_vistas_que_o_casco_no_ar_abre(self):
        """Ajuste DECLARADO: a v1 lia o inventario antigo (casa/field); a fonte
        e a lista AMMESSE de VIEW_FROM_HASH() em portale.html."""
        import re
        html = (RAIZ / "italia-portale" / "client" / "portale.html").read_text(encoding="utf-8")
        m = re.search(r"const AMMESSE = \[([^\]]*)\]", html)
        self.assertIsNotNone(m)
        ammesse = set(re.findall(r"'([a-z]+)'", m.group(1)))
        self.assertEqual(ammesse, set(P.FERRAMENTAS))

    def test_G2_etichette_leva_o_contrato_t4_e_radarfuturo_nao_tem_contrato(self):
        c = corrida_sintetica()
        s = {"SIGNAL_ID": "SINT-SG-L", "ESTADO": "EXPERIMENTAL_CANDIDATE",
             "CHAVES": {"PRODUCT_ID": "SINT-PROD-1"}, "PROVA": [_prova(1)]}
        c["ITENS_POR_FERRAMENTA"] = {"etichette": [s], "radarfuturo": [dict(s)]}
        pl = P.adaptar(c)
        self.assertEqual([x["SIGNAL_ID"] for x in pl["FERRAMENTAS"]["etichette"]["CARTOES"]], ["SINT-SG-L"])
        self.assertIn(("radarfuturo", "SINT-SG-L", "FERRAMENTA_SEM_CONTRATO_D84"), motivos(pl))

    def _duas_corridas_upstream(self, ordem, prova_extra=None):
        """O mesmo ITEM_ID em duas corridas upstream: uma PASSOU, a outra nao."""
        c = corrida_sintetica()
        boa = dict(ITEM_ID="SINT-ITEM-5", RAW_OBSERVATION_ID="SINT-RAW-5", SOURCE_ID="SINT-SRC-5",
                   CORRIDA_UPSTREAM="SINT-UP-A", G0="PASSOU")
        ma = dict(boa, CORRIDA_UPSTREAM="SINT-UP-B", G0="BLOQUEADO_EM_G0")
        c["LINEAGE"] += [boa, ma] if ordem else [ma, boa]
        p = _prova(5)
        p.update(prova_extra or {})
        c["ITENS_POR_FERRAMENTA"] = {"windows": [{"SIGNAL_ID": "SINT-SG-5",
                                                  "ESTADO": "EXPERIMENTAL_CANDIDATE",
                                                  "CHAVES": {}, "PROVA": [p]}]}
        return P.adaptar(c)

    def test_G3_a_resposta_nao_depende_da_ordem_da_linhagem(self):
        """Defeito P1: com o indice um-para-um o veredito trocava com a ordem."""
        a, b = self._duas_corridas_upstream(True), self._duas_corridas_upstream(False)
        self.assertEqual(motivos(a), motivos(b))
        self.assertIn(("windows", "SINT-SG-5", "PROVA_AMBIGUA"), motivos(a))
        self.assertEqual(todos_os_cartoes(a), [])

    def test_G4_a_corrida_upstream_na_prova_desfaz_a_ambiguidade(self):
        for ordem in (True, False):
            boa = self._duas_corridas_upstream(ordem, {"CORRIDA_UPSTREAM": "SINT-UP-A"})
            self.assertEqual([x["SIGNAL_ID"] for x in todos_os_cartoes(boa)], ["SINT-SG-5"])
            self.assertEqual(todos_os_cartoes(boa)[0]["PROVA"][0]["CORRIDA_UPSTREAM"], "SINT-UP-A")
            ma = self._duas_corridas_upstream(ordem, {"CORRIDA_UPSTREAM": "SINT-UP-B"})
            self.assertIn(("windows", "SINT-SG-5", "ITEM_BLOQUEADO_EM_G0"), motivos(ma))

    def test_G5_a_pagina_mostra_o_fora_do_contrato_com_valor(self):
        html = P.como_html(P.adaptar(corrida_sintetica()), css_href="styles.css")
        self.assertIn("fuori contratto D84", html)
        self.assertIn("<th>SCORE_INVENTADO</th><td>99</td>", html)


if __name__ == "__main__":
    unittest.main()
