#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""D126 · PORTAL-PUBLICA-SOZINHO — o publicador, atacado.

    python3 -m unittest tests.test_publicar_portal_sozinho -v

⚠️ DADO SINTETICO DECLARADO: os potes daqui sao os de tests/fixtures/pote/ (todo id SINT-, SINTETICA = true).
O que se chama «pote real» num teste e o sintetico com os ids renomeados — continua inventado.

Prova que:
  P0  o pote: forma+lei v2, D122 (evento so com data), D123 (caso -> produto -> bula), nenhum objeto sem
      prova, nada de dado cru, nada da demo, e a promocao de um pote EXPERIMENTAL so com o dono;
  P1  as telas (D151/D152, dono 29/09): o pote INTEIRO so na tela de debug; as telas de cliente sem a camada
      tecnica (casco original); Radar e Radar Futuro com a linha LIVE = a contagem do pote; nenhum caso antigo
      fora do SNAPSHOT; a barra conta o LIVE; o SHA servido e o do pote; casa (legado fora do casco, correcao do dono 28/09) tem de acabar na
      porta /accesso, sem os 43/44 — senao BLOQUEIA; o redirect vem do vercel.json, e o servidor local o cumpre;
  P2  o portao do release e LIDO do workflow (nao copiado) e so o vermelho herdado e declarado passa;
  P3  o caminho inteiro, com o anfitriao local do ensaio: publica, nao publica o que reprova, nao
      republica o que ja esta no ar, VOLTA sozinho quando a pagina no ar nao tem a contagem, e grita
      ALERTA_CRITICO quando a volta nao roda;
  P4  o casco le o pote publicado (o lugar no Git e null), o local vence, e a barra conta o pote;
  P5  o pote e o registo ficam fora do Git e do deploy.
"""
import copy
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "portoes"))
sys.path.insert(0, str(RAIZ))
import _gavetas  # noqa: E402,F401

import publicar_portal_sozinho as P  # noqa: E402
import pote_intelligence_casco as PIC  # noqa: E402 — o dono do contrato (K2: os eixos so ele os carimba)

FIX = RAIZ / "tests" / "fixtures" / "pote"
POTE_ENSAIO = json.loads((FIX / "POTE-SINTETICO-PUBLICA-SOZINHO.json").read_text(encoding="utf-8"))
POTE_SEM_BULA = json.loads((FIX / "POTE-SINTETICO.json").read_text(encoding="utf-8"))
CONTRATO = P.carregar_contrato()


def ids(linhas, falhas=True):
    return [l["ID"] for l in linhas if (not l["PASS"]) == falhas]


def pote_nao_sintetico():
    """O sintetico com outro nome — para provar o caminho de producao. Continua inventado."""
    txt = json.dumps(POTE_ENSAIO, ensure_ascii=False).replace("SINT-", "RUN-")
    p = json.loads(txt)
    p["CORRIDA_SINTETICA"] = False
    return p


def contrato_aprovado():
    c = copy.deepcopy(CONTRATO)
    c["REGRA_DE_PROMOCAO"].update(ESTADO="APROVADA_PELO_DONO", APROVADA_POR="teste", APROVADA_EM="2026-09-28")
    return c


class ArmazemDeProva:
    """Os bytes do arquivo original, em memoria. So `ler` — a unica pergunta que o publicador faz."""
    def __init__(self, bytes_por_lugar):
        self.b = dict(bytes_por_lugar)

    def ler(self, caminho):
        if caminho not in self.b:
            raise FileNotFoundError(caminho)
        return self.b[caminho]


def pote_liberado():
    """O pote nao sintetico com as tres coisas da liberacao: cada objeto LIBERADO_PARA_CLIENTE, cada prova com
    o sha e o endereco do RAW. Devolve (pote, armazem com os bytes, veredito do LAB para este pote)."""
    p = pote_nao_sintetico()
    reg = CONTRATO["REGRA_DE_PROMOCAO"]
    campo, valor = reg["LIBERACAO_POR_OBJETO"]["CAMPO"], reg["LIBERACAO_POR_OBJETO"]["VALOR_QUE_LIBERA"]
    sha_c, lugar_c = reg["RAW_NO_ARMAZEM"]["CAMPOS_DA_PROVA"]
    bytes_ = {}
    for _, o in P._objetos(p):
        o[campo] = valor
        for pr in o["PROVA"]:
            lugar = f"raw/{pr['RAW_OBSERVATION_ID']}.html"
            bytes_.setdefault(lugar, f"<html>{pr['RAW_OBSERVATION_ID']}</html>".encode("utf-8"))
            pr[sha_c], pr[lugar_c] = P.hashlib.sha256(bytes_[lugar]).hexdigest(), lugar
    # K2 · EIXOS/v1 (01/10): um objeto LIBERADO num pote sem eixos e a contradicao que o LAB reprovou (e97ce8b0) e o
    # fiscal agora recusa. Os eixos sao carimbados pelo DONO (aplicar_eixos), que so copia a LIBERACAO dada acima.
    p = PIC.aplicar_eixos(p)
    ver = {"POTE_SHA256": P.sha_do_pote(p), "VEREDITO": "APROVADO", "PREVIEW": "preview-de-prova",
           "CRITERIO": "21556c27b1ca8ba99f1f11a31e917a4b11a0e867962e9def952de384a13bb9f5", "QUANDO": "2026-09-28"}
    return p, ArmazemDeProva(bytes_), ver


LIBERACAO = ["C0_LIBERADO_PARA_CLIENTE", "C0_VEREDITO_DO_LAB", "C0_RAW_CONFERIDO_NO_ARMAZEM"]


def contagens_boas(pote, sha, contrato=CONTRATO):
    """O CONTAGENS.json que o fotografo escreveria para um portal que obedece."""
    esp = P.contagem_esperada(pote, contrato)
    TL = contrato["TELAS"]
    vivas = [v for v in TL["LIVE"]["TELAS"] if v != "inicio"]
    # a barra: o LIVE nas vozes vivas; nas outras, o numero do casco original (aqui um qualquer)
    nav = {v: (str(esp[v]) if v in vivas else "7") for v in esp if v != "inicio"}
    nav.update(painel="", sala="")
    total = sum(len(e.get("OBJETOS") or []) for e in pote["COMPARTIMENTOS"].values())
    T = {}
    for t in TL["DO_POTE"]:
        viva = t in TL["LIVE"]["TELAS"]
        antigos = 17 if t in ("inicio", "meeting") else (44 if t == "radarfuturo" else 0)
        T[t] = {"HTTP": 200, "POTE_NA_TELA": False, "POTE_OBJETOS": 0, "POTE_RECUSADO": False, "MARCA": False,
                "LEGADO_CARTOES": antigos, "LEGADO_43_UNIVERSO": 43,
                "LEGADO_43_VISIVEIS": antigos if t in ("inicio", "meeting") else 0, "LEGADO_44_UNIVERSO": 44,
                "LEGADO_44_VISIVEIS": antigos if t == "radarfuturo" else 0,
                "LEGADO_43_FORA": 0, "LEGADO_44_FORA": 0, "LEGADO_CARTOES_FORA": 0,
                "LIVE_N": str(esp[t]) if viva else None, "SNAPSHOT_TITULO": viva,
                "OGGI_LEGADO": False, "NAV": dict(nav), "ENVELOPE": {"POTE_SHA256": sha, "TEM_POTE": True},
                "ENTREGA_RECUSADA_NA_TELA": False}
    T[TL["DEBUG"]["TELA"]] = {"HTTP": 200, "POTE_NA_TELA": True, "MARCA": True, "POTE_RECUSADO": False,
                              "POTE_OBJETOS": total, "ENVELOPE": {"POTE_SHA256": sha, "TEM_POTE": True},
                              "ENTREGA_RECUSADA_NA_TELA": False}
    T["accesso"] = {"HTTP": 200, "LEGADO_CARTOES": 0, "LEGADO_43_VISIVEIS": 0, "LEGADO_44_VISIVEIS": 0, "LEGADO_43_UNIVERSO": 43,
                    "LEGADO_43_FORA": 0, "LEGADO_44_FORA": 0, "LEGADO_CARTOES_FORA": 0, "ENTREGA_RECUSADA_NA_TELA": False}
    T["casa"] = {"HTTP": 200, "URL_FINAL": "http://127.0.0.1:1/accesso", "LEGADO_43_VISIVEIS": 0, "LEGADO_44_VISIVEIS": 0}
    return {"MEDICAO_COMPLETA": True, "TELAS": T}


# ── P0 · o pote ──────────────────────────────────────────────────────────────
class P0_OPote(unittest.TestCase):
    def test_o_pote_do_ensaio_passa_em_ensaio_com_as_notas(self):
        L = P.conferir_pote(POTE_ENSAIO, CONTRATO, "ensaio")
        self.assertEqual(ids(L), [], L)
        notas = " ".join(l.get("NOTA") or "" for l in L)
        self.assertIn("SINTETICO", notas)
        self.assertIn("APROVADA_PELO_DONO", notas)

    def test_sintetico_nunca_vai_a_producao(self):
        L = P.conferir_pote(POTE_ENSAIO, contrato_aprovado(), "producao")
        self.assertIn("C0_NADA_DA_DEMO", ids(L))

    def test_a_regra_esta_aprovada_pelo_dono_com_as_seis_condicoes(self):
        prom = CONTRATO["REGRA_DE_PROMOCAO"]
        self.assertEqual(prom["ESTADO"], "APROVADA_PELO_DONO")
        self.assertEqual(prom["APROVADA_EM"], "2026-09-28")
        self.assertEqual([c["N"] for c in prom["AS_SEIS_CONDICOES"]], [1, 2, 3, 4, 5, 6])
        self.assertIn("NAO_PARA_CLIENTE", prom["TEXTO_DO_DONO"])
        conf = {c["ID"] for c in CONTRATO["CONFERENCIAS"]}
        self.assertTrue(set(LIBERACAO) <= conf, "as tres conferencias da liberacao estao escritas na lei")

    def test_experimental_nao_liberado_e_recusado_em_producao_mesmo_com_o_sim_do_dono(self):
        # O CASO QUE O DONO PROIBIU: pote EXPERIMENTAL · NAO_PARA_CLIENTE, regra aprovada, corrida real.
        L = P.conferir_pote(pote_nao_sintetico(), CONTRATO, "producao")
        self.assertEqual(ids(L), LIBERACAO, L)

    def test_liberado_com_lab_e_raw_conferido_passa_em_producao(self):
        p, arm, ver = pote_liberado()
        self.assertEqual(ids(P.conferir_pote(p, CONTRATO, "producao", ver, arm)), [])

    def test_sem_o_sim_do_dono_nem_o_liberado_passa(self):
        p, arm, ver = pote_liberado()
        c = copy.deepcopy(CONTRATO)
        c["REGRA_DE_PROMOCAO"]["ESTADO"] = "AGUARDA_DONO"
        self.assertEqual(ids(P.conferir_pote(p, c, "producao", ver, arm)), ["C0_PROMOCAO"])

    def test_aprovacao_sem_nome_nem_data_nao_vale(self):
        p, arm, ver = pote_liberado()
        c = contrato_aprovado()
        c["REGRA_DE_PROMOCAO"]["APROVADA_POR"] = None
        self.assertIn("C0_PROMOCAO", ids(P.conferir_pote(p, c, "producao", ver, arm)))

    def test_um_objeto_nao_liberado_recusa_o_pote_inteiro(self):
        p, arm, ver = pote_liberado()
        o = next(o for _, o in P._objetos(p))
        o["LIBERACAO"] = "NAO_PARA_CLIENTE"
        p = PIC.aplicar_eixos(p)                          # K2: o eixo 1 do objeto segue a LIBERACAO nova (o dono)
        ver["POTE_SHA256"] = P.sha_do_pote(p)
        self.assertEqual(ids(P.conferir_pote(p, CONTRATO, "producao", ver, arm)), ["C0_LIBERADO_PARA_CLIENTE"])

    def test_a_marca_do_pote_nao_libera_os_objetos(self):
        p = pote_nao_sintetico()
        p["MARCA"], p["LIBERACAO"] = "LIBERADO_PARA_CLIENTE", "LIBERADO_PARA_CLIENTE"
        self.assertIn("C0_LIBERADO_PARA_CLIENTE", ids(P.conferir_pote(p, CONTRATO, "producao")))

    def test_veredito_do_lab_ausente_de_outro_pote_ou_reprovado(self):
        p, arm, ver = pote_liberado()
        self.assertEqual(ids(P.conferir_pote(p, CONTRATO, "producao", None, arm)), ["C0_VEREDITO_DO_LAB"])
        outro = dict(ver, POTE_SHA256="0" * 64)
        self.assertEqual(ids(P.conferir_pote(p, CONTRATO, "producao", outro, arm)), ["C0_VEREDITO_DO_LAB"])
        reprovado = dict(ver, VEREDITO="REPROVADO")
        self.assertEqual(ids(P.conferir_pote(p, CONTRATO, "producao", reprovado, arm)), ["C0_VEREDITO_DO_LAB"])
        sem_criterio = dict(ver, CRITERIO="NAO SEI")
        self.assertEqual(ids(P.conferir_pote(p, CONTRATO, "producao", sem_criterio, arm)), ["C0_VEREDITO_DO_LAB"])
        criterio_que_nao_e_sha = dict(ver, CRITERIO="criterio-v2")
        self.assertEqual(ids(P.conferir_pote(p, CONTRATO, "producao", criterio_que_nao_e_sha, arm)),
                         ["C0_VEREDITO_DO_LAB"])

    def test_raw_que_nao_bate_no_armazem(self):
        p, arm, ver = pote_liberado()
        lugar = next(iter(arm.b))
        arm.b[lugar] = b"outro byte"                       # o arquivo mudou no armazem
        self.assertEqual(ids(P.conferir_pote(p, CONTRATO, "producao", ver, arm)), ["C0_RAW_CONFERIDO_NO_ARMAZEM"])
        del arm.b[lugar]                                   # o arquivo sumiu
        self.assertEqual(ids(P.conferir_pote(p, CONTRATO, "producao", ver, arm)), ["C0_RAW_CONFERIDO_NO_ARMAZEM"])

    def test_prova_sem_sha_do_raw(self):
        p, arm, ver = pote_liberado()
        next(o for _, o in P._objetos(p))["PROVA"][0]["RAW_SHA256"] = "NAO SEI"
        ver["POTE_SHA256"] = P.sha_do_pote(p)
        self.assertEqual(ids(P.conferir_pote(p, CONTRATO, "producao", ver, arm)), ["C0_RAW_CONFERIDO_NO_ARMAZEM"])

    def test_producao_sem_armazem_declarado_bloqueia(self):
        p, _, ver = pote_liberado()
        antes = P.os.environ.pop("SINTONIA_ARMAZEM_RAIZ", None)
        try:
            L = P.conferir_pote(p, CONTRATO, "producao", ver, None)
        finally:
            if antes is not None:
                P.os.environ["SINTONIA_ARMAZEM_RAIZ"] = antes
        self.assertEqual(ids(L), ["C0_RAW_CONFERIDO_NO_ARMAZEM"])

    def test_em_preview_a_liberacao_so_avisa(self):
        # o LAB precisa do preview para dar o veredito: em preview as tres viram NOTA, nao bloqueiam
        L = P.conferir_pote(pote_nao_sintetico(), CONTRATO, "preview")
        self.assertEqual(ids(L), [])
        self.assertEqual(sorted(l["ID"] for l in L if l.get("NOTA") and "em producao ESTA" in l["NOTA"]),
                         sorted(LIBERACAO))

    def test_d123_oportunidade_sem_bula(self):
        L = P.conferir_pote(POTE_SEM_BULA, CONTRATO, "ensaio")
        self.assertIn("C0_D123_CASO_PRODUTO_BULA", ids(L))

    def test_d123_oportunidade_sem_produto(self):
        p = copy.deepcopy(POTE_ENSAIO)
        for o in p["COMPARTIMENTOS"]["meeting"]["OBJETOS"]:
            if o["ESPECIE"] == "OPORTUNIDADE":
                o["CHAVES"]["ADAMA_PRODUCT_ID"] = "NAO SEI"
        self.assertIn("C0_D123_CASO_PRODUTO_BULA", ids(P.conferir_pote(p, CONTRATO, "ensaio")))

    def test_d122_evento_sem_data(self):
        p = copy.deepcopy(POTE_ENSAIO)
        p["COMPARTIMENTOS"]["future"]["OBJETOS"][0]["CHAVES"]["FACT_TIME"] = "NAO SEI"
        self.assertIn("C0_D122_EVENTO_SO_COM_DATA", ids(P.conferir_pote(p, CONTRATO, "ensaio")))
        p["COMPARTIMENTOS"]["future"]["OBJETOS"][0]["CHAVES"]["FACT_TIME"] = "primavera"
        self.assertIn("C0_D122_EVENTO_SO_COM_DATA", ids(P.conferir_pote(p, CONTRATO, "ensaio")))

    def test_objeto_sem_prova_ate_ao_documento(self):
        p = copy.deepcopy(POTE_ENSAIO)
        p["COMPARTIMENTOS"]["windows"]["OBJETOS"][0]["PROVA"][0]["DOCUMENT_ID"] = "NAO SEI"
        self.assertIn("C0_NENHUM_OBJETO_SEM_PROVA", ids(P.conferir_pote(p, CONTRATO, "ensaio")))
        p["COMPARTIMENTOS"]["windows"]["OBJETOS"][0]["PROVA"] = []
        self.assertIn("C0_NENHUM_OBJETO_SEM_PROVA", ids(P.conferir_pote(p, CONTRATO, "ensaio")))

    def test_dado_cru_chave_e_texto_longo(self):
        p = copy.deepcopy(POTE_ENSAIO)
        p["COMPARTIMENTOS"]["windows"]["OBJETOS"][0]["FORA_DO_CONTRATO"] = {"RAW_TEXT": "o documento inteiro"}
        self.assertIn("C0_NADA_DE_DADO_CRU", ids(P.conferir_pote(p, CONTRATO, "ensaio")))
        p = copy.deepcopy(POTE_ENSAIO)
        p["COMPARTIMENTOS"]["windows"]["OBJETOS"][0]["PORQUE"] = "x" * 4001
        self.assertIn("C0_NADA_DE_DADO_CRU", ids(P.conferir_pote(p, CONTRATO, "ensaio")))

    def test_pote_que_o_validador_v2_reprova(self):
        p = copy.deepcopy(POTE_ENSAIO)
        p["SCHEMA"] = "POTE_INTELLIGENCE_CASCO/v1"
        self.assertIn("C0_POTE_V2_FORMA_E_LEI", ids(P.conferir_pote(p, CONTRATO, "ensaio")))

    def test_o_sha_e_do_conteudo_e_nao_da_ordem(self):
        a = P.sha_do_pote(POTE_ENSAIO)
        b = P.sha_do_pote(dict(reversed(list(POTE_ENSAIO.items()))))
        self.assertEqual(a, b)
        p = copy.deepcopy(POTE_ENSAIO)
        p["CORTE"] = "outro"
        self.assertNotEqual(a, P.sha_do_pote(p))

    def test_o_envelope_se_le_de_volta_e_o_lugar_vazio_nao(self):
        sha = P.sha_do_pote(POTE_ENSAIO)
        js = P.js_do_envelope(P.envelope(POTE_ENSAIO, sha, CONTRATO, "ensaio", "abc"))
        env = P.ler_envelope_js(js)
        self.assertEqual(env["POTE_SHA256"], sha)
        self.assertEqual(P.sha_do_pote(env["POTE"]), sha)
        stub = (RAIZ / "italia-portale" / "client" / "sintonia-pote-publicado.js").read_text(encoding="utf-8")
        self.assertIsNone(P.ler_envelope_js(stub))


# ── P1 · as telas ────────────────────────────────────────────────────────────
class P1_AsTelas(unittest.TestCase):
    def setUp(self):
        self.sha = P.sha_do_pote(POTE_ENSAIO)
        self.C = contagens_boas(POTE_ENSAIO, self.sha)

    def conf(self):
        return P.conferir_telas(self.C, POTE_ENSAIO, self.sha, CONTRATO, "C5")

    def test_a_contagem_esperada_vem_do_pote(self):
        esp = P.contagem_esperada(POTE_ENSAIO, CONTRATO)
        self.assertEqual(esp["meeting"], 2)
        self.assertEqual(esp["radarfuturo"], 1)
        self.assertEqual(esp["future"], 2, "a rota #future le o compartimento archive")
        self.assertEqual(esp["etichette"], esp["portfolio"])
        self.assertEqual(esp["field"], 0)
        self.assertEqual(set(CONTRATO["TELAS"]["DO_POTE"]) - set(esp), set())

    def test_portal_que_obedece_passa_e_a_casa_redireciona(self):
        L = self.conf()
        self.assertEqual(ids(L), [])
        self.assertIn("C5_REDIRECIONADA_CASA", ids(L, falhas=False))
        self.assertEqual(CONTRATO["TELAS"]["FORA_DAS_ROTAS"], {}, "a casa saiu de «so dita» para redirecionada")

    def test_casa_que_ainda_abre_bloqueia(self):
        """Correcao do dono 28/09: pagina demo acessivel por URL publica nao pode ficar. So avisar ja nao chega."""
        self.C["TELAS"]["casa"] = {"HTTP": 200, "URL_FINAL": "http://127.0.0.1:1/casa",
                                   "LEGADO_43_VISIVEIS": 43, "LEGADO_44_VISIVEIS": 44}
        self.assertIn("C5_REDIRECIONADA_CASA", ids(self.conf()))

    def test_casa_redirecionada_para_outro_sitio_bloqueia(self):
        self.C["TELAS"]["casa"]["URL_FINAL"] = "http://127.0.0.1:1/portale"
        self.assertIn("C5_REDIRECIONADA_CASA", ids(self.conf()))

    def test_casa_nao_medida_bloqueia(self):
        del self.C["TELAS"]["casa"]
        self.assertIn("C5_REDIRECIONADA_CASA", ids(self.conf()))

    def test_o_fotografo_visita_toda_tela_que_uma_conferencia_le(self):
        """Medido no preview de 28/09 18:45: a casa saiu de FORA_DAS_ROTAS e o fotografo deixou de a visitar —
        a conferencia reprovou por «nao medido». Uma tela conferida tem de estar na lista do fotografo."""
        telas = P.telas_a_fotografar(CONTRATO)
        for t in list(CONTRATO["TELAS"].get("REDIRECIONADAS") or {}) + list(CONTRATO["TELAS"]["FORA_DAS_ROTAS"]):
            self.assertIn(t, telas)
        self.assertIn("casa", telas)
        self.assertEqual(len(telas), len(set(telas)))

    def test_o_vercel_json_redireciona_a_casa_para_a_porta(self):
        """A regra que a Vercel aplica e a que o contrato espera — um so destino, lido dos dois lados."""
        r = {x["source"]: x["destination"] for x in P.redirecionamentos(RAIZ / "vercel.json")}
        para = CONTRATO["TELAS"]["REDIRECIONADAS"]["casa"]["PARA"]
        self.assertEqual(r.get("/casa"), para)
        self.assertEqual(r.get("/casa.html"), para)
        self.assertTrue((RAIZ / "italia-portale" / "client" / "casa.html").exists(),
                        "o ficheiro fica no Git: redirecionar nao e apagar")

    def test_o_servidor_local_cumpre_o_redirect_antes_do_ficheiro(self):
        import urllib.request as U
        d = Path(tempfile.mkdtemp(prefix="teste-redirect-"))
        try:
            (d / "casa.html").write_text("CASA-LEGADA", encoding="utf-8")
            (d / "accesso.html").write_text("PORTA", encoding="utf-8")
            (d / "vercel.json").write_text(json.dumps({"redirects": [
                {"source": "/casa", "destination": "/accesso", "permanent": False},
                {"source": "/casa.html", "destination": "/accesso", "permanent": False}]}), encoding="utf-8")
            srv = P.Servidor(lambda: d, lambda: P.redirecionamentos(d / "vercel.json"))
            try:
                for caminho in ("/casa", "/casa.html"):
                    with U.urlopen(srv.url + caminho, timeout=10) as r:
                        self.assertEqual(r.read().decode(), "PORTA", caminho)
                        self.assertTrue(r.geturl().endswith("/accesso"), r.geturl())
                sem = P.Servidor(lambda: d)   # sem regras: o ficheiro e servido (o antes)
                try:
                    with U.urlopen(sem.url + "/casa", timeout=10) as r:
                        self.assertEqual(r.read().decode(), "CASA-LEGADA")
                finally:
                    sem.fechar()
            finally:
                srv.fechar()
        finally:
            shutil.rmtree(d, ignore_errors=True)

    def test_debug_sem_o_pote_inteiro(self):
        d = CONTRATO["TELAS"]["DEBUG"]["TELA"]
        self.C["TELAS"][d]["POTE_OBJETOS"] -= 1
        self.assertIn("C5_DEBUG_TEM_O_POTE_INTEIRO", ids(self.conf()))
        self.C = contagens_boas(POTE_ENSAIO, self.sha)
        self.C["TELAS"][d]["MARCA"] = False
        self.assertIn("C5_DEBUG_TEM_O_POTE_INTEIRO", ids(self.conf()))
        self.C = contagens_boas(POTE_ENSAIO, self.sha)
        del self.C["TELAS"][d]
        self.assertIn("C5_DEBUG_TEM_O_POTE_INTEIRO", ids(self.conf()))

    def test_pote_recusado_no_debug(self):
        self.C["TELAS"][CONTRATO["TELAS"]["DEBUG"]["TELA"]]["POTE_RECUSADO"] = True
        self.assertIn("C5_DEBUG_TEM_O_POTE_INTEIRO", ids(self.conf()))

    def test_tela_com_erro_de_pintura_reprova(self):
        """D156: medido 29/09 12:36 — #future abriu com renderVals() e o modelo null. A segunda tentativa decide;
        se ela tambem falha, reprova."""
        self.C["TELAS"]["future"]["ERRO_DE_PINTURA"] = True
        self.assertIn("C5_CLIENTE_SEM_CAMADA_TECNICA", ids(self.conf()))

    def test_camada_tecnica_na_tela_do_cliente(self):
        """D152: a faixa EXPERIMENTAL e o pote so no debug. Na tela do cliente, reprova."""
        self.C["TELAS"]["windows"].update(POTE_NA_TELA=True, MARCA=True, POTE_OBJETOS=2)
        self.assertIn("C5_CLIENTE_SEM_CAMADA_TECNICA", ids(self.conf()))
        self.C = contagens_boas(POTE_ENSAIO, self.sha)
        del self.C["TELAS"]["market"]["MARCA"]
        self.assertIn("C5_CLIENTE_SEM_CAMADA_TECNICA", ids(self.conf()), "nao medida nao e ausente")

    def test_sha_servido_nao_e_o_do_pote(self):
        self.C["TELAS"]["windows"]["ENVELOPE"]["POTE_SHA256"] = "0" * 64
        self.assertIn("C5_CLIENTE_SEM_CAMADA_TECNICA", ids(self.conf()))

    def test_live_com_numero_que_nao_e_o_do_pote(self):
        self.C["TELAS"]["meeting"]["LIVE_N"] = "17"
        self.assertIn("C5_LIVE_CONTA_O_POTE", ids(self.conf()))
        self.C = contagens_boas(POTE_ENSAIO, self.sha)
        self.C["TELAS"]["radarfuturo"]["LIVE_N"] = None
        self.assertIn("C5_LIVE_CONTA_O_POTE", ids(self.conf()))

    def test_live_numa_tela_que_nao_o_tem(self):
        self.C["TELAS"]["windows"]["LIVE_N"] = "2"
        self.assertIn("C5_LIVE_CONTA_O_POTE", ids(self.conf()))

    def test_snapshot_sem_rotulo(self):
        self.C["TELAS"]["meeting"]["SNAPSHOT_TITULO"] = False
        self.assertIn("C5_LIVE_CONTA_O_POTE", ids(self.conf()))

    def test_d152_caso_antigo_fora_do_snapshot(self):
        self.C["TELAS"]["radarfuturo"]["LEGADO_44_FORA"] = 44
        self.assertIn("C5_D152_NADA_MISTURADO", ids(self.conf()))
        self.C = contagens_boas(POTE_ENSAIO, self.sha)
        self.C["TELAS"]["accesso"]["LEGADO_CARTOES_FORA"] = 3
        self.assertIn("C5_D152_NADA_MISTURADO", ids(self.conf()))
        self.C = contagens_boas(POTE_ENSAIO, self.sha)
        del self.C["TELAS"]["meeting"]["LEGADO_43_FORA"]
        self.assertIn("C5_D152_NADA_MISTURADO", ids(self.conf()), "nao medido nao e zero")

    def test_d152_antigos_dentro_do_snapshot_passam(self):
        """Os 17 e os 44 continuam visiveis — dentro do SNAPSHOT. Nao apagar historico real."""
        self.assertEqual(self.C["TELAS"]["meeting"]["LEGADO_43_VISIVEIS"], 17)
        self.assertEqual(ids(self.conf()), [])

    def test_a_caixa_oggi_do_legado(self):
        self.C["TELAS"]["windows"]["OGGI_LEGADO"] = True
        self.assertIn("C5_D152_NADA_MISTURADO", ids(self.conf()))
        self.C = contagens_boas(POTE_ENSAIO, self.sha)
        del self.C["TELAS"]["windows"]["OGGI_LEGADO"]
        self.assertIn("C5_D152_NADA_MISTURADO", ids(self.conf()), "nao medida nao e escondida")

    def test_detector_que_nao_mediu_nao_vale_zero(self):
        self.C["TELAS"]["meeting"]["LEGADO_43_UNIVERSO"] = 0
        self.assertIn("C5_D152_NADA_MISTURADO", ids(self.conf()))

    def test_a_barra_do_radar_com_o_numero_antigo(self):
        self.C["TELAS"]["meeting"]["NAV"]["radarfuturo"] = "44"
        self.assertIn("C5_BARRA_CONTA_O_LIVE", ids(self.conf()))
        self.C = contagens_boas(POTE_ENSAIO, self.sha)
        self.C["TELAS"]["meeting"]["NAV"]["windows"] = "29"
        self.assertNotIn("C5_BARRA_CONTA_O_LIVE", ids(self.conf()), "as outras vozes contam como o casco original")

    def test_d156_recusa_dita_no_debug_e_so_la(self):
        """B3: com a entrega RECUSADA o debug diz o motivo; tela de cliente nenhuma o diz."""
        ent = {"ESTADO": "RECUSADA", "QUANDO": "2026-09-29T10:00:00Z", "MOTIVOS": ["POTE.json: sha256 diferente"]}
        d = CONTRATO["TELAS"]["DEBUG"]["TELA"]
        self.C["TELAS"][d]["ENTREGA_RECUSADA_NA_TELA"] = True
        L = P.conferir_telas(self.C, POTE_ENSAIO, self.sha, CONTRATO, "C5", ent)
        self.assertNotIn("C5_ENTREGA_DITA_SO_NO_DEBUG", ids(L))
        self.C["TELAS"]["meeting"]["ENTREGA_RECUSADA_NA_TELA"] = True
        self.assertIn("C5_ENTREGA_DITA_SO_NO_DEBUG", ids(P.conferir_telas(self.C, POTE_ENSAIO, self.sha, CONTRATO, "C5", ent)))

    def test_d156_recusa_que_o_debug_nao_diz(self):
        ent = {"ESTADO": "RECUSADA", "QUANDO": "x", "MOTIVOS": ["y"]}
        self.assertIn("C5_ENTREGA_DITA_SO_NO_DEBUG", ids(P.conferir_telas(self.C, POTE_ENSAIO, self.sha, CONTRATO, "C5", ent)))

    def test_d156_recusa_na_tela_sem_recusa_nenhuma(self):
        self.C["TELAS"][CONTRATO["TELAS"]["DEBUG"]["TELA"]]["ENTREGA_RECUSADA_NA_TELA"] = True
        self.assertIn("C5_ENTREGA_DITA_SO_NO_DEBUG", ids(self.conf()))

    def test_d156_o_envelope_leva_a_entrega(self):
        ent = {"ESTADO": "RECUSADA", "QUANDO": "x", "MOTIVOS": ["y"]}
        self.assertEqual(P.envelope(POTE_ENSAIO, self.sha, CONTRATO, "preview", "0" * 40, ent)["ENTREGA"], ent)
        self.assertNotIn("ENTREGA", P.envelope(POTE_ENSAIO, self.sha, CONTRATO, "preview", "0" * 40))

    def test_d156_pote_demo_nao_se_diz_aprovado_pelo_dono(self):
        """Item 5 do LAB: um pote de teste no ar nao leva a aprovacao D126 do dono como se fosse dele."""
        self.assertIs(POTE_ENSAIO.get("CORRIDA_SINTETICA"), True)
        prom = P.envelope(POTE_ENSAIO, self.sha, CONTRATO, "preview", "0" * 40)["PROMOCAO"]
        self.assertEqual(prom["ESTADO"], "DEMO_SEM_APROVACAO_DO_DONO")
        self.assertIsNone(prom["APROVADA_POR"])
        self.assertNotIn("APROVADA_PELO_DONO", json.dumps(prom))
        self.assertNotIn("PUBLICACAO: SIM", json.dumps(prom))
        self.assertTrue(prom["TEXTO"].startswith("DEMO"))

    def test_d156_cada_sinal_de_nao_cliente_sozinho_tira_a_aprovacao(self):
        """Red team do bot (30/09): CORRIDA_SINTETICA, NAO_PARA_CLIENTE, MARCA ou SOURCE_HEAD SINT-, CADA UM SOZINHO,
        e o envelope nunca diz APROVADA_PELO_DONO nem cita a D126 como aprovacao deste pote."""
        limpo = dict(POTE_ENSAIO, CORRIDA_SINTETICA=False, NAO_PARA_CLIENTE=False, MARCA="LIBERADO_PARA_CLIENTE",
                     SOURCE_HEAD="a5db06c4a094d569a329f7a3a135c17fdb130efb")
        casos = {"CORRIDA_SINTETICA": {"CORRIDA_SINTETICA": True},
                 "NAO_PARA_CLIENTE": {"NAO_PARA_CLIENTE": True},
                 "MARCA EXPERIMENTAL": {"MARCA": "EXPERIMENTAL"},
                 "MARCA NAO_PARA_CLIENTE": {"MARCA": "nao_para_cliente"},
                 "MARCA completa": {"MARCA": "EXPERIMENTAL · NAO_PARA_CLIENTE"},
                 "SOURCE_HEAD SINT-": {"SOURCE_HEAD": "SINT-0000"},
                 "SOURCE_HEAD dict SINT-": {"SOURCE_HEAD": {"MOTOR": "SINT-0000"}}}
        for nome, mexe in casos.items():
            for sem_campo in (False, True):
                with self.subTest(nome, limpo_sem_campos=sem_campo):
                    base = dict(limpo)
                    if sem_campo:     # o sinal sozinho, com os outros campos AUSENTES (nao so false)
                        for k in ("CORRIDA_SINTETICA", "NAO_PARA_CLIENTE", "MARCA", "SOURCE_HEAD"):
                            base.pop(k, None)
                    prom = P.envelope(dict(base, **mexe), self.sha, CONTRATO, "preview", "0" * 40)["PROMOCAO"]
                    self.assertNotIn("APROVADA_PELO_DONO", json.dumps(prom))
                    self.assertNotIn("PUBLICACAO: SIM", json.dumps(prom))
                    self.assertIsNone(prom["APROVADA_POR"])
                    self.assertIn("sem aprovacao do dono para este pote", prom["TEXTO"])
        # sem nenhum sinal, a regra geral continua dita (e so ai)
        self.assertEqual(P.envelope(limpo, self.sha, CONTRATO, "preview", "0" * 40)["PROMOCAO"]["ESTADO"],
                         CONTRATO["REGRA_DE_PROMOCAO"]["ESTADO"])
        self.assertEqual(P.sinais_de_nao_cliente(limpo), [])

    def test_d156_o_pote_real_r9_tambem_nao_se_diz_aprovado(self):
        """O R9 real e EXPERIMENTAL · NAO_PARA_CLIENTE com CORRIDA_SINTETICA false: nao e DEMO, e nao e aprovado."""
        r9 = dict(POTE_ENSAIO, CORRIDA_SINTETICA=False, SOURCE_HEAD={"MOTOR": "a5db06c4"})
        prom = P.envelope(r9, self.sha, CONTRATO, "preview", "0" * 40)["PROMOCAO"]
        self.assertEqual(prom["ESTADO"], "NAO_PARA_CLIENTE_SEM_APROVACAO_DO_DONO")
        self.assertFalse(prom["TEXTO"].startswith("DEMO"))

    def test_medicao_incompleta_nao_autoriza(self):
        self.C["MEDICAO_COMPLETA"] = False
        self.assertIn("C5_MEDIDO", ids(self.conf()))
        self.assertTrue(ids(P.conferir_telas(None, POTE_ENSAIO, self.sha, CONTRATO, "C6")))

    def test_tela_que_faltou(self):
        del self.C["TELAS"]["science"]
        self.assertIn("C5_CLIENTE_SEM_CAMADA_TECNICA", ids(self.conf()))


# ── P2 · o portao do release ─────────────────────────────────────────────────
class P2_OPortaoDoRelease(unittest.TestCase):
    def test_lido_do_workflow_e_nao_copiado(self):
        cmds, erro = P.comandos_do_release(CONTRATO)
        if erro and "nao consegui ler" in erro:
            self.fail("origin/release/canonical nao esta nesta arvore: git fetch origin release/canonical — " + erro)
        self.assertIsNone(erro)
        txt = [c for _, _, c in cmds]
        self.assertIn("node italia-portale/audit/build-gate.mjs", txt)
        self.assertIn("node italia-portale/audit/run.mjs", txt)
        self.assertIn("python3 system-map/scripts/correr_a_cadeia.py VALIDAR", txt)
        self.assertFalse([c for c in txt if "playwright" in c], "instalar o browser e ferramenta, nao conferencia")

    def test_release_ilegivel_reprova(self):
        c = copy.deepcopy(CONTRATO)
        c["RELEASE_REF"] = "refs/heads/nao-existe-de-todo"
        cmds, erro = P.comandos_do_release(c)
        self.assertIsNone(cmds)
        self.assertIn("nao consegui ler", erro)

    def _run(self, saida, rc):
        with tempfile.TemporaryDirectory() as d:
            (Path(d) / "italia-portale" / "audit").mkdir(parents=True)
            (Path(d) / "italia-portale" / "audit" / "run.mjs").write_text(
                f"console.log({json.dumps(saida)}); process.exit({rc});\n", encoding="utf-8")
            return P.conferir_comando("C3", "node italia-portale/audit/run.mjs", d, CONTRATO, 60)

    def test_so_o_vermelho_herdado_e_declarado_passa(self):
        l = self._run("  \x1b[31mFAIL\x1b[0m  N1    Nav counts\n  72/73 passing  1 failing", 1)
        self.assertTrue(l["PASS"], l)
        self.assertIn("INHERITED", l["NOTA"])

    def test_vermelho_novo_reprova(self):
        l = self._run("  FAIL  N1    x\n  FAIL  B2    y\n  71/73 passing", 1)
        self.assertFalse(l["PASS"])
        self.assertIn("B2", " ".join(l["DETALHE"]))

    def test_corrida_que_nao_chegou_ao_fim_reprova(self):
        self.assertFalse(self._run("  FAIL  N1    x\nTypeError: boom", 1)["PASS"])

    def test_comando_que_falha_reprova(self):
        l = P.conferir_comando("C1", [sys.executable, "-c", "import sys; sys.exit(3)"], RAIZ, CONTRATO, 60)
        self.assertFalse(l["PASS"])


# ── P3 · o caminho inteiro, com o anfitriao local ────────────────────────────
STUB = (RAIZ / "italia-portale" / "client" / "sintonia-pote-publicado.js").read_text(encoding="utf-8")


def cliente_minimo(d: Path):
    (d / "italia-portale" / "client").mkdir(parents=True, exist_ok=True)
    (d / "italia-portale" / "client" / "index.html").write_text("<!doctype html><title>x</title>", encoding="utf-8")
    (d / "italia-portale" / "client" / "sintonia-pote-publicado.js").write_text(STUB, encoding="utf-8")
    return d / "italia-portale" / "client"


class PublicadorDeProva(P.Publicador):
    """O caminho real, com as pecas que tocam o mundo trocadas: a arvore e um cliente minimo, as conferencias
    do codigo dizem o que o teste mandar, e o navegador e o CONTAGENS que o teste der — mas o SHA no ar e
    medido de verdade, por HTTP, no anfitriao local."""
    codigo_passa = True
    contagens_no_ar = "boas"   # "boas" | "sem_contagem"
    montados = 0

    def montar(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="teste-montagem-"))
        cliente_minimo(self.tmp / "arvore")
        (self.tmp / "ferramentas").mkdir()
        PublicadorDeProva.montados += 1
        return self.tmp / "arvore", self.tmp / "ferramentas", "0" * 40

    def desmontar(self):
        shutil.rmtree(self.tmp, ignore_errors=True) if self.tmp else None

    def conferir_codigo(self, copia):
        return [P.linha("C1_BUILD_GATE", self.codigo_passa, ["prova"])]

    def construir(self, copia):
        return P.linha("C1_BUILD_COM_O_POTE", True, ["prova"])

    def conferir_montagem(self, copia, ferr, pote, sha, pasta):
        return P.conferir_telas(contagens_boas(pote, sha, self.c), pote, sha, self.c, "C5_MONTAGEM"), None

    def conferir_no_ar(self, url, ferr, pote, sha, pasta):
        st, s = P.sha_no_ar(url)
        L = [P.linha("C6_NO_AR_SHA", s == sha, [f"HTTP {st} SHA {s}"])]
        cont = contagens_boas(pote, sha, self.c)
        if self.contagens_no_ar == "sem_contagem" or s != sha:
            for t in cont["TELAS"].values():
                t.update(POTE_NA_TELA=False, POTE_OBJETOS=0, ENVELOPE=None, LIVE_N=None)
        return L + P.conferir_telas(cont, pote, sha, self.c, "C6_NO_AR"), None


class EnsaioQueImplantaSemOPote(P.EnsaioLocal):
    """O defeito «a pagina no ar sem contagem»: o deploy leva o lugar vazio em vez do envelope."""
    def implantar(self, copia, prod):
        novo = super().implantar(copia, prod)
        (self.pasta / "deployments" / novo["ID"] / "sintonia-pote-publicado.js").write_text(STUB, encoding="utf-8")
        return novo


class EnsaioQueNaoVolta(EnsaioQueImplantaSemOPote):
    """O defeito «o rollback que nao roda»: diz que voltou e nao mexe no alias."""
    def voltar(self, anterior):
        return True


class P3_OCaminhoInteiro(unittest.TestCase):
    def setUp(self):
        self.d = Path(tempfile.mkdtemp(prefix="teste-publica-"))
        self.reg = self.d / "PUBLICACOES"
        self.imps = []

    def tearDown(self):
        for i in self.imps:
            i.fechar()
        shutil.rmtree(self.d, ignore_errors=True)

    def anfitriao(self, cls=P.EnsaioLocal):
        imp = cls(self.d / "host")
        imp.semear(cliente_minimo(self.d / "semente"))
        self.imps.append(imp)
        return imp

    def publicar(self, imp, pote=POTE_ENSAIO, modo="ensaio", contrato=CONTRATO, **kw):
        pub = PublicadorDeProva(contrato, imp, self.reg, modo, espera_no_ar=1)
        for k, v in kw.items():
            setattr(pub, k, v)
        return pub.publicar(pote, origem="teste")

    def registos(self):
        return [json.loads(p.read_text(encoding="utf-8")) for p in sorted(self.reg.rglob("REGISTO.json"))]

    def alertas(self):
        f = self.reg / "ALERTAS.jsonl"
        return [json.loads(l) for l in f.read_text(encoding="utf-8").splitlines()] if f.exists() else []

    def test_publica_e_guarda_o_antes_o_depois_e_o_sha(self):
        imp = self.anfitriao()
        antes = imp.atual()["ID"]
        self.assertEqual(self.publicar(imp), P.PUBLICADO)
        sha = P.sha_do_pote(POTE_ENSAIO)
        self.assertEqual(P.sha_no_ar(imp.url_no_ar()), (200, sha))
        u = json.loads((self.reg / "ULTIMA-PUBLICACAO.json").read_text(encoding="utf-8"))
        self.assertEqual(u["POTE_SHA256"], sha)
        self.assertTrue(Path(u["POTE_JS"]).exists())
        R = self.registos()[-1]
        self.assertEqual(R["ESTADO"], "PUBLICADO")
        self.assertEqual(R["ANTERIOR"]["DEPLOYMENT"]["ID"], antes)
        self.assertIsNone(R["ANTERIOR"]["POTE_SHA256_NO_AR"], "antes estava no ar o lugar vazio")

    def test_o_registo_guarda_o_sha_do_ficheiro_de_veredito(self):
        imp = self.anfitriao()
        _, _, ver = pote_liberado()
        arq = {"ARQUIVO": "lab/vereditos/VEREDITO-x.json", "SHA256": "a" * 64}
        self.publicar(imp, veredito_lab=ver, veredito_arquivo=arq)
        v = self.registos()[-1]["VEREDITO_DO_LAB"]
        self.assertEqual((v["ARQUIVO"], v["SHA256"], v["CRITERIO"]), (arq["ARQUIVO"], arq["SHA256"], ver["CRITERIO"]))

    def test_o_segundo_pote_guarda_o_primeiro_como_anterior(self):
        imp = self.anfitriao()
        self.assertEqual(self.publicar(imp), P.PUBLICADO)
        p2 = copy.deepcopy(POTE_ENSAIO)
        p2["CORTE"] = "2026-09-28T10:00:00Z"
        self.assertEqual(self.publicar(imp, pote=p2), P.PUBLICADO)
        R = self.registos()[-1]
        self.assertEqual(R["POTE_ANTERIOR"]["POTE_SHA256"], P.sha_do_pote(POTE_ENSAIO))
        self.assertEqual(R["POTE_ANTERIOR"]["FICHEIRO"], "POTE-ANTERIOR.js")

    def test_o_mesmo_pote_no_ar_nao_se_republica(self):
        imp = self.anfitriao()
        self.publicar(imp)
        n = PublicadorDeProva.montados
        self.assertEqual(self.publicar(imp), P.PUBLICADO)
        self.assertEqual(self.registos()[-1]["ESTADO"], "NADA_A_PUBLICAR")
        self.assertEqual(PublicadorDeProva.montados, n, "nada se montou")

    def test_pote_invalido_nao_vai_ao_ar(self):
        imp = self.anfitriao()
        antes = imp.atual()["ID"]
        p = copy.deepcopy(POTE_ENSAIO)
        p["COMPARTIMENTOS"]["windows"]["OBJETOS"][0]["PROVA"] = []
        self.assertEqual(self.publicar(imp, pote=p), P.BLOQUEADO)
        self.assertEqual(imp.atual()["ID"], antes)
        self.assertEqual(P.sha_no_ar(imp.url_no_ar())[1], None)

    def test_conferencia_do_codigo_falhada_nao_vai_ao_ar(self):
        imp = self.anfitriao()
        antes = imp.atual()["ID"]
        self.assertEqual(self.publicar(imp, codigo_passa=False), P.BLOQUEADO)
        self.assertEqual(imp.atual()["ID"], antes)
        self.assertEqual(self.registos()[-1]["ESTADO"], "BLOQUEADO")

    def test_pagina_no_ar_sem_contagem_volta_sozinha_e_avisa(self):
        imp = self.anfitriao(EnsaioQueImplantaSemOPote)
        antes = imp.atual()["ID"]
        self.assertEqual(self.publicar(imp), P.REVERTIDO)
        self.assertEqual(imp.atual()["ID"], antes, "o alias voltou para o anterior")
        R = self.registos()[-1]
        self.assertTrue(R["VOLTA"]["PROVADA"])
        self.assertEqual([a["TIPO"] for a in self.alertas()], ["REVERTIDO"])
        self.assertFalse((self.reg / "ULTIMA-PUBLICACAO.json").exists(), "o que foi revertido nao e a ultima")

    def test_rollback_que_nao_roda_e_alerta_critico(self):
        imp = self.anfitriao(EnsaioQueNaoVolta)
        self.assertEqual(self.publicar(imp), P.CRITICO)
        self.assertEqual([a["TIPO"] for a in self.alertas()], ["ALERTA_CRITICO"])
        self.assertFalse(self.registos()[-1]["VOLTA"]["PROVADA"])

    def test_producao_nunca_pelo_anfitriao_de_ensaio(self):
        # tudo o resto em ordem (corrida real, promocao aprovada): so a regra do modo pode barrar
        imp = self.anfitriao()
        antes = imp.atual()["ID"]
        self.assertEqual(self.publicar(imp, pote=pote_nao_sintetico(), modo="producao", contrato=contrato_aprovado()),
                         P.BLOQUEADO)
        self.assertEqual(imp.atual()["ID"], antes)
        self.assertEqual([l["ID"] for l in self.registos()[-1]["CONFERENCIAS"] if not l["PASS"]], ["MODO"])

    def test_envelope_no_ar_cujo_sha_nao_e_o_do_pote_nao_conta(self):
        imp = self.anfitriao()
        p = copy.deepcopy(POTE_ENSAIO)
        p["CORTE"] = "outro"
        env = P.envelope(p, P.sha_do_pote(POTE_ENSAIO), CONTRATO, "ensaio", "x")   # SHA de outro pote
        (self.d / "host" / "deployments" / imp.atual()["ID"] / "sintonia-pote-publicado.js").write_text(
            P.js_do_envelope(env), encoding="utf-8")
        self.assertEqual(P.sha_no_ar(imp.url_no_ar()), (200, "ENVELOPE_INCOERENTE"))

    def test_deriva_no_ar_e_alertada(self):
        imp = self.anfitriao()
        self.publicar(imp)
        (self.d / "host" / "deployments" / imp.atual()["ID"] / "sintonia-pote-publicado.js").write_text(STUB, encoding="utf-8")
        self.assertEqual(self.publicar(imp), P.PUBLICADO, "o pote volta a subir")
        self.assertIn("DERIVA", [a["TIPO"] for a in self.alertas()])


# ── P4 · o casco ─────────────────────────────────────────────────────────────
NODE_CASCO = r"""
const fs = require('fs'), vm = require('vm'), path = require('path');
const CL = path.join(process.argv[1], 'italia-portale', 'client');
const LEITOR = fs.readFileSync(path.join(CL, 'sintonia-pote-casco.js'), 'utf8');
const STUB = fs.readFileSync(path.join(CL, 'sintonia-pote-publicado.js'), 'utf8');
const POTE = JSON.parse(fs.readFileSync(process.argv[2], 'utf8'));
function janela(search, publicado) {
  const w = { location: { search }, document: { escrito: [], write(s) { this.escrito.push(s); } } };
  w.window = w; w.document = w.document; vm.createContext(w);
  vm.runInContext(STUB, w);
  if (publicado !== undefined) w.SINTONIA_POTE_PUBLICADO = publicado;
  vm.runInContext(LEITOR, w);
  return w;
}
const out = {};
let w = janela('', undefined);
out.stub = { pote: w.SINTONIA_POTE, pedido: w.SINTONIA_POTE_PEDIDO, escrito: w.document.escrito.length,
  conta: w.SINTONIA_POTE_CASCO.contagemDaVista(w.SINTONIA_POTE, 'meeting'),
  vm: w.SINTONIA_POTE_CASCO.vm(w.SINTONIA_POTE, 'field', 'it') };
w = janela('', { CONTRATO: 'SINTONIA_POTE_PUBLICADO/1', POTE });
const C = w.SINTONIA_POTE_CASCO;
out.pub = { run: (w.SINTONIA_POTE || {}).INTELLIGENCE_RUN_ID, pedido: w.SINTONIA_POTE_PEDIDO,
  conta: Object.fromEntries(['meeting', 'radarfuturo', 'future', 'etichette', 'field', 'sala', 'painel', 'radar']
    .map((v) => [v, C.contagemDaVista(w.SINTONIA_POTE, v)])),
  field: (() => { const x = C.vm(w.SINTONIA_POTE, 'field', 'it'); return x && { comp: x.comp.codigo, vazio: x.vazio, titulo: x.vazioTitulo }; })() };
const ruim = JSON.parse(JSON.stringify(POTE)); ruim.SCHEMA = 'x';
w = janela('', { POTE: ruim });
out.ruim = { conta: w.SINTONIA_POTE_CASCO.contagemDaVista(w.SINTONIA_POTE, 'meeting') };
w = janela('?pote=local', { POTE });
out.local = { pote: w.SINTONIA_POTE, pedido: w.SINTONIA_POTE_PEDIDO, escrito: w.document.escrito.join('') };
w = janela('', { POTE: null });
out.semPote = { pote: w.SINTONIA_POTE, pedido: w.SINTONIA_POTE_PEDIDO };
console.log(JSON.stringify(out));
"""


class P4_OCasco(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        r = subprocess.run(["node", "-e", NODE_CASCO, str(RAIZ), str(FIX / "POTE-SINTETICO-PUBLICA-SOZINHO.json")],
                           capture_output=True, text=True, timeout=120)
        if r.returncode != 0:
            raise AssertionError("node nao correu o leitor do casco: " + r.stderr[-800:])
        cls.o = json.loads(r.stdout)

    def test_o_lugar_no_git_e_null_e_nada_muda(self):
        s = self.o["stub"]
        self.assertIsNone(s["pote"])
        self.assertFalse(s["pedido"])
        self.assertEqual(s["escrito"], 0)
        self.assertIsNone(s["conta"], "sem pote, o contador e o de sempre")
        self.assertIsNone(s["vm"])
        stub = (RAIZ / "italia-portale" / "client" / "sintonia-pote-publicado.js").read_text(encoding="utf-8")
        self.assertIn("window.SINTONIA_POTE_PUBLICADO = window.SINTONIA_POTE_PUBLICADO || null;", stub)
        self.assertNotIn("INTELLIGENCE_RUN_ID\":", stub)

    def test_o_pote_publicado_e_lido_e_pedido(self):
        p = self.o["pub"]
        self.assertEqual(p["run"], "SINT-IR-PUBLICA-0001")
        self.assertTrue(p["pedido"])

    def test_a_barra_conta_o_pote(self):
        c = self.o["pub"]["conta"]
        esp = P.contagem_esperada(POTE_ENSAIO, CONTRATO)
        for v in ("meeting", "radarfuturo"):
            self.assertEqual(c[v], esp[v], v)
        self.assertEqual(c["radar"], esp["meeting"])
        for v in ("future", "etichette", "field"):
            self.assertIsNone(c[v], f"D152: {v} conta como o casco original")
        self.assertIsNone(c["sala"])
        self.assertIsNone(c["painel"])

    def test_field_mostra_o_porque_do_pote_e_nao_a_demo(self):
        f = self.o["pub"]["field"]
        self.assertEqual(f["comp"], "field")
        self.assertTrue(f["vazio"])
        self.assertIn("CASCO_SEM_CONTRATO_DE_INTELLIGENCE", f["titulo"])

    def test_pote_publicado_que_reprova_e_nao_sei_na_barra(self):
        self.assertEqual(self.o["ruim"]["conta"], "NAO SEI")

    def test_o_local_vence(self):
        l = self.o["local"]
        self.assertIsNone(l["pote"], "o local ainda nao chegou; o publicado nao o substitui")
        self.assertTrue(l["pedido"])
        self.assertIn("sintonia-pote.js", l["escrito"])

    def test_envelope_sem_pote_nao_pede(self):
        self.assertIsNone(self.o["semPote"]["pote"])
        self.assertFalse(self.o["semPote"]["pedido"])

    def test_o_portal_carrega_o_lugar_antes_do_leitor(self):
        html = (RAIZ / "italia-portale" / "client" / "portale.html").read_text(encoding="utf-8")
        a = html.find('<script src="sintonia-pote-publicado.js"></script>')
        b = html.find('<script src="sintonia-pote-casco.js"></script>')
        self.assertTrue(0 < a < b)
        self.assertIn("'isField'];", html, "a rota field tambem cede ao pote")
        self.assertEqual(html.count("count: poteConta("), 3)
        self.assertEqual(html.count('data-nav-view="{{ n.view }}"'), 3)
        self.assertIn('<sc-if value="{{ oggiDoLegado }}"', html)
        self.assertIn("oggiDoLegado: !(typeof window !== 'undefined' && window.SINTONIA_POTE_PEDIDO === true),", html)


# ── P5 · fora do Git e do deploy ─────────────────────────────────────────────
class P5_ForaDoGit(unittest.TestCase):
    def test_o_registo_nunca_entra_no_git_nem_sobe(self):
        self.assertIn("PUBLICACOES/", (RAIZ / ".gitignore").read_text(encoding="utf-8").splitlines())
        self.assertIn("/PUBLICACOES", (RAIZ / ".vercelignore").read_text(encoding="utf-8").splitlines())

    def test_o_pote_local_continua_fora(self):
        self.assertIn("/italia-portale/client/sintonia-pote.js",
                      (RAIZ / ".vercelignore").read_text(encoding="utf-8").splitlines())

    def test_o_contrato_diz_a_autoridade_e_a_regra(self):
        self.assertIn("release/canonical", " ".join(CONTRATO["AUTORIDADE_DE_DEPLOY"]["MEDIDO"]))
        self.assertIn("--prebuilt", CONTRATO["AUTORIDADE_DE_DEPLOY"]["COMANDOS_VERCEL"]["IMPLANTAR"])
        self.assertEqual(set(CONTRATO["VERMELHOS_HERDADOS_DO_RELEASE"]) - {"PORQUE"}, {"N1"})


if __name__ == "__main__":
    unittest.main()
