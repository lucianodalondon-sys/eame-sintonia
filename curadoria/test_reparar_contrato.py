# -*- coding: utf-8 -*-
"""R1 · REPARO-FONTES-V1 — o reparo de contratos, o alimentador e a regra
«reparo antes de discovery». Sem rede: um site falso em memoria. Sem escrita
fora de pastas temporarias.
"""
import copy
import json
import sys
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest import mock

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
import fila as F                  # noqa: E402
import gatilho_discovery as GD    # noqa: E402
import lifecycle as LC            # noqa: E402
import reparar_contrato as RC     # noqa: E402
import worker as W                # noqa: E402

AGORA = datetime(2026, 9, 30, 12, 0, tzinfo=timezone.utc)
MOLDE = ("^https?://(www\\.)?exemplo\\.it/(?:[^?#]*/)?(?:news|notizie)[^?#]*/"
         "(?:[a-z0-9]+(?:-[a-z0-9]+){2,}|\\d{4}[^?#]*)/?(?:[?#].*)?$")
CORPO = "<p>" + ("parola " * 200) + "</p>"          # 1200 caracteres em paragrafo


def _html(links, corpo=""):
    return ("<html><body><nav>%s</nav><main>%s</main></body></html>"
            % ("".join('<a href="%s">x</a>' % l for l in list(links) + NAV), corpo)).encode()


NOTICIAS = ["/articoli/%d/il-titolo-di-una-notizia-numero-%d" % (100 + i, i) for i in range(6)]
# links de servico que toda home tem: sem eles a familia seria > 80 % da pagina
# e o guarda da 6-PREP-d (e_generico) recusa-a — como deve.
NAV = ["/contatti", "/chi-siamo", "/privacy", "/area-riservata", "/servizi", "/bandi"]
MENU = ["/web/centro-di-uno", "/web/centro-di-due", "/web/centro-di-tre",
        "/web/centro-di-quattro", "/web/centro-di-cinque"]


def _contrato(sid="IT-T7-900", index="https://www.exemplo.it/", padrao=MOLDE):
    return {"SOURCE_ID": sid, "OWNER": "Exemplo", "NAME": "Exemplo", "TERRITORY": "T7",
            "BATCH_ID": "LOTE-HTML-ARTIGO", "OUTPUT_TYPE": "HTML",
            "CANONICAL_ENTRY_URL": index,
            "ACQUISITION": {"STRATEGY": "HTML_LINK_DISCOVERY", "MATCH": "URL", "INDEX_URL": index,
                            "LINK_PATTERN": padrao, "MAX_TARGETS": 1},
            "IDENTITY": {"STRATEGY": "CONTENT_CAPTURE",
                         "CAPTURES": {"doc": {"FROM": "URL", "PATTERN": "^https?://[^/]+/?(.*?)/?$"}},
                         "DOCUMENT_ID": sid + ":URL:{doc.1}", "FACT_TIME": "UNKNOWN"},
            "IDENTITY_KEYS": ["url_path"], "IDENTITY_KIND": "URL_PATH",
            "ROUTE_TYPE": "DISCOVERED_ROUTE", "FAIL_CLOSED_RULE": "sem endereco = FAILED",
            "NEGATIVE_CONTROL": {"esperado": "EMPTY_LIST -> FAILED"},
            "EXPECTED_FAILURES": ["entrada sem endereco que case = EMPTY_LIST = FAILED"],
            "SOURCE_CONTRACT_VERSION": "SOURCE-CURATOR-CONTRACTS-V1", "SOURCE_CONTRACT_HASH": "x"}


class Site:
    """{url: (status, bytes)} + redireccionamentos. Conta os pedidos."""

    def __init__(self, paginas, redir=None):
        self.p, self.redir, self.pedidos = paginas, redir or {}, []

    def buscar(self, url):
        self.pedidos.append(url)
        destino = self.redir.get(url, url)
        st, b = self.p.get(destino, (404, b""))
        return st, b, "" if st == 200 else "HTTP %s" % st, destino


class _RP:
    def __init__(self, proibe=()):
        self.proibe = proibe


def _robots(proibe=()):
    return lambda host: (_RP(proibe), "robots vivo de %s" % host)


def _permitido(url, rp):
    return not any(p in url for p in rp.proibe)


_INFERIR = RC.inferir


def inferir(contrato, site, outros=None, proibe=()):
    RC._ROBOTS.clear()
    return _INFERIR(contrato, outros=outros or {}, buscar=site.buscar,
                      robots_de=_robots(proibe), permitido=_permitido, pausa=0)


B = "https://www.exemplo.it"


class Inferir(unittest.TestCase):
    def test_familia_de_noticias_na_home_vira_padrao_e_casa_o_que_o_canario_abre(self):
        site = Site({B + "/": (200, _html(NOTICIAS + ["/contatti", "/chi-siamo"])),
                     B + NOTICIAS[0]: (200, _html(["/contatti"], CORPO))})
        p = inferir(_contrato(), site)
        self.assertEqual("PADRAO_NOVO", p["DESFECHO"], p.get("PORQUE"))
        import re
        rx = re.compile(p["LINK_PATTERN"])
        self.assertTrue(all(rx.match(B + n) for n in NOTICIAS))
        self.assertFalse(rx.match(B + "/"))
        self.assertFalse(rx.match(B + "/contatti"))
        self.assertEqual(B + NOTICIAS[0], p["ITEM_LIDO"]["URL"])   # o 1.o ordenado = o do canario
        self.assertLessEqual(p["PEDIDOS"], RC.MAX_PEDIDOS)

    def test_pagina_de_servico_e_recusada_sem_um_so_pedido(self):
        for u in ("/contatti1", "/whistleblowing", "/c/portal/update_language?languageId=en_US",
                  "/amministrazione-trasparente"):
            site = Site({})
            p = inferir(_contrato(index=B + u), site)
            self.assertEqual(("RECUSA", "ENTRADA_INSTITUCIONAL"), (p["DESFECHO"], p["MOTIVO"]), u)
            self.assertEqual([], site.pedidos)

    def test_entrada_que_e_uma_noticia_nao_e_fonte(self):
        idx = B + "/-/il-crea-protagonista-della-notte-europea"
        site = Site({idx: (200, _html(NOTICIAS, CORPO))})
        p = inferir(_contrato(index=idx), site)
        self.assertEqual(("RECUSA", "ENTRADA_E_MATERIA"), (p["DESFECHO"], p["MOTIVO"]))

    def test_listagem_com_corpo_nao_e_confundida_com_noticia(self):
        idx = B + "/notizie"                     # ultimo segmento literal: listagem
        site = Site({idx: (200, _html(NOTICIAS, CORPO)),
                     B + NOTICIAS[0]: (200, _html([], CORPO))})
        self.assertEqual("PADRAO_NOVO", inferir(_contrato(index=idx), site)["DESFECHO"])

    def test_menu_repetido_no_item_salta_para_a_familia_seguinte(self):
        menu = [m.replace("/web/", "/eventi/") for m in MENU]   # tem vocabulario: passa o FLUXO
        pags = {B + "/": (200, _html(menu + menu + menu + NOTICIAS[:4]))}
        for m in menu:
            pags[B + m] = (200, _html(menu, CORPO))      # home de centro: corpo grande + o menu
        pags[B + NOTICIAS[0]] = (200, _html(menu, CORPO))
        p = inferir(_contrato(), Site(pags))
        self.assertEqual("PADRAO_NOVO", p["DESFECHO"], p.get("PORQUE"))
        self.assertIn("articoli", p["LINK_PATTERN"])
        self.assertTrue(any("FAMILIA_E_MENU" in t["VEREDITO"] for t in p["TENTADOS"]))

    def test_so_paginas_fixas_e_familia_estatica_sem_abrir_item(self):
        fixas = ["/regione/uffici-e-organizzazione", "/regione/brand-e-immagine",
                 "/regione/area-personale-tributi", "/regione/bollo-auto-regionale"]
        site = Site({B + "/": (200, _html(fixas)), B + fixas[0]: (200, _html([], CORPO))})
        p = inferir(_contrato(), site)
        self.assertEqual(("RECUSA", "FAMILIA_ESTATICA"), (p["DESFECHO"], p["MOTIVO"]))
        self.assertEqual([B + "/"], site.pedidos)

    def test_paginas_fixas_na_home_descem_a_seccao_de_noticias(self):
        fixas = ["/regione/uffici-e-organizzazione", "/regione/brand-e-immagine",
                 "/regione/area-personale-tributi", "/news/"]
        site = Site({B + "/": (200, _html(fixas)), B + "/news/": (200, _html(NOTICIAS)),
                     B + NOTICIAS[0]: (200, _html([], CORPO))})
        p = inferir(_contrato(), site)
        self.assertEqual("PADRAO_NOVO", p["DESFECHO"], p.get("PORQUE"))
        self.assertEqual(B + "/news/", p["INDEX_URL"])

    def test_seccao_vem_sempre_com_vocabulario_de_publicacao(self):
        # Por isso o filtro FLUXO no ramo da seccao nunca recusa: `_seccoes` so devolve
        # caminhos com vocabulario de noticia, e `fluxo` le o caminho da listagem.
        # (mutante equivalente declarado no relatorio R1.)
        import provar_listagem as PL
        for s in PL._seccoes([B + "/news/", B + "/comunicati-stampa/", B + "/regione/uffici"]):
            self.assertIsNotNone(RC.fluxo(s, "", [B + "/regione/uffici-e-organizzazione"]))

    def test_fluxo_pelos_tres_sinais(self):
        self.assertIsNone(RC.fluxo(B + "/", "", [B + "/regione/area-personale-tributi"] * 2))
        self.assertIn("vocabulario", RC.fluxo(B + "/comunicati/", "", [B + "/x/a-b-c"]))
        self.assertIn("numero", RC.fluxo(B + "/", "", [B + "/x/2026/a-b"]))
        self.assertIn("query", RC.fluxo(B + "/", "", [B + "/dettaglio?articleId=123"]))
        self.assertIn("titulos", RC.fluxo(B + "/", "", [B + "/x/uno-due-tre-quattro-cinque-sei"] * 3))
        self.assertIsNone(RC.fluxo(B + "/", "", [B + "/x/uno-due-tre-quattro-cinque"] * 3))

    def test_menu_com_titulos_longos_nao_e_menu(self):
        # o widget «ultimas noticias» repete-se em cada artigo, mas os nomes sao titulos
        self.assertIsNone(RC.e_menu([B + n for n in NOTICIAS], {B + n for n in NOTICIAS}))
        self.assertIsNotNone(RC.e_menu([B + m for m in MENU], {B + m for m in MENU}))

    def test_item_sem_corpo_de_materia_recusa(self):
        site = Site({B + "/": (200, _html(NOTICIAS)),
                     B + NOTICIAS[0]: (200, _html(NOTICIAS * 3, "<p>curto</p>"))})
        p = inferir(_contrato(), site)
        self.assertEqual(("RECUSA", "ITEM_NAO_E_MATERIA"), (p["DESFECHO"], p["MOTIVO"]))

    def test_sem_familia_desce_a_seccao_de_noticias(self):
        site = Site({B + "/": (200, _html(["/news/", "/contatti"])),
                     B + "/news/": (200, _html(NOTICIAS)),
                     B + NOTICIAS[0]: (200, _html([], CORPO))})
        p = inferir(_contrato(), site)
        self.assertEqual("PADRAO_NOVO", p["DESFECHO"], p.get("PORQUE"))
        self.assertEqual(B + "/news/", p["INDEX_URL"])

    def test_sem_familia_nem_seccao_e_nao_sei(self):
        site = Site({B + "/": (200, _html(["/contatti", "/a"]))})
        p = inferir(_contrato(), site)
        self.assertEqual(("RECUSA", "SEM_FAMILIA_DE_ITENS"), (p["DESFECHO"], p["MOTIVO"]))

    def test_redireccionamento_muda_a_entrada_para_o_destino(self):
        novo = "https://lombardia.exemplo.it/"
        site = Site({novo: (200, _html([novo.rstrip("/") + n for n in NOTICIAS])),
                     novo.rstrip("/") + NOTICIAS[0]: (200, _html([], CORPO))},
                    redir={B + "/": novo})
        p = inferir(_contrato(), site)
        self.assertEqual("PADRAO_NOVO", p["DESFECHO"], p.get("PORQUE"))
        self.assertEqual(novo, p["INDEX_URL"])
        self.assertIn("lombardia", p["LINK_PATTERN"])

    def test_duplicada_quando_o_documento_ja_tem_dono(self):
        site = Site({B + "/": (200, _html(NOTICIAS)), B + NOTICIAS[0]: (200, _html([], CORPO))})
        p1 = inferir(_contrato(), site)
        dono = _contrato("IT-T7-800", padrao=p1["LINK_PATTERN"])
        p2 = inferir(_contrato(), Site(site.p), outros={"IT-T7-800": dono})
        self.assertEqual(("RECUSA", "DUPLICADA"), (p2["DESFECHO"], p2["MOTIVO"]))

    def test_respostas_da_entrada(self):
        casos = {403: ("BLOCK", "AUTH"), 401: ("BLOCK", "AUTH"), 429: ("RETRY", None),
                 503: ("RETRY", None), 0: ("RETRY", None), 404: ("RECUSA", None)}
        for st, (desfecho, classe) in casos.items():
            p = inferir(_contrato(), Site({B + "/": (st, b"")}))
            self.assertEqual(desfecho, p["DESFECHO"], st)
            if classe:
                self.assertEqual(classe, p["CLASSE"])

    def test_robots_proibe_e_block_sem_pedido(self):
        site = Site({B + "/": (200, _html(NOTICIAS))})
        p = inferir(_contrato(), site, proibe=("exemplo.it/",))
        self.assertEqual(("BLOCK", "ROBOTS"), (p["DESFECHO"], p["CLASSE"]))
        self.assertEqual([], site.pedidos)

    def test_familia_que_e_quase_a_pagina_toda_e_generica(self):
        muitas = ["/articoli/%d/il-titolo-di-una-notizia-numero-%d" % (100 + i, i) for i in range(30)]
        site = Site({B + "/": (200, _html(muitas)), B + muitas[0]: (200, _html([], CORPO))})
        p = inferir(_contrato(), site)                  # 30 de 36 links: > 80 % -> guarda recusa
        self.assertEqual(("RECUSA", "SEM_FAMILIA_DE_ITENS"), (p["DESFECHO"], p["MOTIVO"]))

    def test_um_so_item_nao_e_familia(self):
        site = Site({B + "/": (200, _html(NOTICIAS[:1])), B + NOTICIAS[0]: (200, _html([], CORPO))})
        p = inferir(_contrato(), site)
        self.assertEqual(("RECUSA", "SEM_FAMILIA_DE_ITENS"), (p["DESFECHO"], p["MOTIVO"]))

    def test_robots_do_destino_manda_depois_do_redireccionamento(self):
        novo = "https://proibido.exemplo.it/"
        site = Site({novo: (200, _html([novo.rstrip("/") + n for n in NOTICIAS]))},
                    redir={B + "/": novo})
        p = inferir(_contrato(), site, proibe=("proibido.exemplo.it",))
        self.assertEqual(("BLOCK", "ROBOTS"), (p["DESFECHO"], p["CLASSE"]))
        self.assertEqual(1, len(site.pedidos))

    def test_item_proibido_pelo_robots_nao_se_abre(self):
        site = Site({B + "/": (200, _html(NOTICIAS)), B + NOTICIAS[0]: (200, _html([], CORPO))})
        p = inferir(_contrato(), site, proibe=("/articoli/",))
        self.assertEqual("RECUSA", p["DESFECHO"])
        self.assertEqual([B + "/"], site.pedidos)
        self.assertIn("robots", p["TENTADOS"][0]["VEREDITO"])

    def test_teto_de_pedidos_com_muitas_familias(self):
        fams = ["/sez%s/%d/titolo-lungo-di-una-cosa-%d" % (s, i, i) for s in "abcdef" for i in range(2)]
        pags = {B + "/": (200, _html(fams))}
        for f in fams:
            pags[B + f] = (200, _html([], "<p>curto</p>"))
        site = Site(pags)
        with mock.patch.object(RC, "MAX_FAMILIAS_TENTADAS", 10):
            p = inferir(_contrato(), site)
        self.assertEqual("RECUSA", p["DESFECHO"])
        self.assertEqual(RC.MAX_PEDIDOS, len(site.pedidos))

    def test_teto_de_pedidos(self):
        pags = {B + "/": (200, _html(MENU + MENU + NOTICIAS[:3] + ["/eventi/%d/evento-numero-%d-bello" % (i, i)
                                                                   for i in range(3)]))}
        for m in MENU:
            pags[B + m] = (200, _html(MENU, CORPO))
        site = Site(pags)
        p = inferir(_contrato(), site)
        self.assertLessEqual(len(site.pedidos), RC.MAX_PEDIDOS)
        self.assertLessEqual(p["PEDIDOS"], RC.MAX_PEDIDOS)


class Aplicar(unittest.TestCase):
    def _proposta(self):
        site = Site({B + "/": (200, _html(NOTICIAS)), B + NOTICIAS[0]: (200, _html([], CORPO))})
        return inferir(_contrato(), site)

    def test_muda_so_a_acquisition_e_guarda_a_anterior(self):
        c = _contrato()
        novo = RC.aplicar(c, self._proposta(), quando="2026-09-30T12:00:00+00:00")
        mexidos = {k for k in set(c) | set(novo) if c.get(k) != novo.get(k)}
        self.assertTrue(mexidos <= RC.CAMPOS_QUE_O_REPARO_MUDA, mexidos)
        self.assertEqual(MOLDE, novo["REPARO_DE_CONTRATO"]["ACQUISITION_ANTERIOR"]["LINK_PATTERN"])
        self.assertTrue(novo["REPARO_DE_CONTRATO"]["PRECISA_DE_REMEDIR"])
        self.assertEqual("2026-09-30T12:00:00+00:00", novo["ROUTE_PROVENANCE"]["INTEGRADO_EM"])
        self.assertNotEqual(c["SOURCE_CONTRACT_HASH"], novo["SOURCE_CONTRACT_HASH"])
        self.assertEqual(c["SOURCE_ID"], novo["SOURCE_ID"])

    def test_recusa_o_que_nao_e_padrao_novo(self):
        with self.assertRaises(RC.ReparoInvalido):
            RC.aplicar(_contrato(), {"DESFECHO": "RECUSA"})

    def test_o_validador_da_casa_manda(self):
        p = dict(self._proposta(), LINK_PATTERN=".*")          # casa a propria entrada
        with self.assertRaises(RC.ReparoInvalido):
            RC.aplicar(_contrato(), p)

    def test_segundo_reparo_guarda_historico(self):
        c1 = RC.aplicar(_contrato(), self._proposta())
        c2 = RC.aplicar(c1, self._proposta())
        self.assertEqual(1, len(c2["REPARO_DE_CONTRATO"]["HISTORICO"]))


class _Pasta(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        d = Path(self.tmp.name)
        self._antes = (LC.LIVRO, F.FILA, W.EVIDENCIA, W.CONTRATOS, W.ALLOCATION, GD.CONTRATOS,
                       GD.CANDIDATAS)
        LC.LIVRO = d / "LEDGER.json"
        F.FILA = d / "QUEUE.json"
        W.EVIDENCIA = d / "EVIDENCE.json"
        W.CONTRATOS = GD.CONTRATOS = d / "contratos.json"
        W.ALLOCATION = d / "alloc.json"
        GD.CANDIDATAS = d / "cand.json"
        GD.CANDIDATAS.write_text(json.dumps({"CANDIDATAS": []}), encoding="utf-8")
        W.ALLOCATION.write_text(json.dumps({"NOVAS": []}), encoding="utf-8")

    def tearDown(self):
        (LC.LIVRO, F.FILA, W.EVIDENCIA, W.CONTRATOS, W.ALLOCATION, GD.CONTRATOS,
         GD.CANDIDATAS) = self._antes
        self.tmp.cleanup()

    def _contratos(self, *cs):
        W.CONTRATOS.write_text(json.dumps({"FONTES": list(cs)}), encoding="utf-8")

    def _estado(self, sid, e):
        LC.registar(sid, e, "preparo do teste", evidence_ref="EV-TESTE")


class EtapaDoWorker(_Pasta):
    def test_padrao_novo_reescreve_o_contrato_e_enfileira_a_validacao(self):
        c = _contrato()
        self._contratos(c)
        self._estado(c["SOURCE_ID"], LC.CONTRACTED_CANARY_FAILED)
        site = Site({B + "/": (200, _html(NOTICIAS)), B + NOTICIAS[0]: (200, _html([], CORPO))})
        prop = inferir(c, site)
        t = F.enfileirar(c["SOURCE_ID"], F.REPAIR_CONTRACT, priority=50)
        with mock.patch.object(RC, "inferir", return_value=prop):
            r = W.executar_uma(F.proxima(), W._contratos())
        self.assertEqual("OK", r["RESULTADO"])
        livro = json.loads(W.CONTRATOS.read_text(encoding="utf-8"))["FONTES"]
        self.assertEqual(prop["LINK_PATTERN"], livro[0]["ACQUISITION"]["LINK_PATTERN"])
        self.assertEqual(LC.CANARY_PENDING, LC.estado_de(c["SOURCE_ID"]))
        abertas = [x for x in F._ler()["TAREFAS"] if x["STATUS"] == F.PENDING]
        self.assertEqual([F.VALIDATE_ROUTE], [x["TASK_TYPE"] for x in abertas])
        self.assertNotIn(LC.READY_FOR_COLLECTION,
                         [x["NEW_STATE"] for x in LC._ler_bruto()["TRANSICOES"]])
        self.assertEqual(t["TASK_ID"], r["TASK_ID"])

    def test_recusa_fica_canary_failed_com_o_motivo_no_livro(self):
        c = _contrato()
        self._contratos(c)
        self._estado(c["SOURCE_ID"], LC.CONTRACTED_CANARY_FAILED)
        F.enfileirar(c["SOURCE_ID"], F.REPAIR_CONTRACT, priority=50)
        rec = {"DESFECHO": "RECUSA", "MOTIVO": "ENTRADA_E_MATERIA", "PORQUE": "e uma noticia"}
        with mock.patch.object(RC, "inferir", return_value=rec):
            r = W.executar_uma(F.proxima(), W._contratos())
        self.assertEqual("FAIL", r["RESULTADO"])
        ult = LC._ler_bruto()["TRANSICOES"][-1]
        self.assertEqual(LC.CONTRACTED_CANARY_FAILED, ult["NEW_STATE"])
        self.assertIn("REPARO_RECUSADO: ENTRADA_E_MATERIA", ult["REASON"])
        self.assertEqual(c["ACQUISITION"],
                         json.loads(W.CONTRATOS.read_text(encoding="utf-8"))["FONTES"][0]["ACQUISITION"])

    def test_sem_contrato_parte_do_molde_da_alocacao(self):
        sid = "IT-T2-900"
        W.ALLOCATION.write_text(json.dumps({"NOVAS": [
            {"SOURCE_ID": sid, "CANDIDATE_ID": "CAND-9999", "TERRITORY": "T2", "NOME": "Arpa Exemplo",
             "URL": B + "/", "FAMILY": "HTML_SITE"}]}), encoding="utf-8")
        self._contratos()
        self._estado(sid, LC.CONTRACTED_CANARY_FAILED)
        F.enfileirar(sid, F.REPAIR_CONTRACT, priority=50)
        visto = {}

        def _inf(c, **kw):
            visto["c"] = c
            return inferir(c, Site({B + "/": (200, _html(NOTICIAS)),
                                    B + NOTICIAS[0]: (200, _html([], CORPO))}))
        with mock.patch.object(RC, "inferir", side_effect=_inf):
            r = W.executar_uma(F.proxima(), W._contratos())
        self.assertEqual("OK", r["RESULTADO"], r)
        self.assertEqual(sid, visto["c"]["SOURCE_ID"])
        self.assertEqual([sid], [c["SOURCE_ID"] for c in
                                 json.loads(W.CONTRATOS.read_text(encoding="utf-8"))["FONTES"]])


class Alimentador(_Pasta):
    def _cands(self, **kw):
        return {(c["SOURCE_ID"], c["TASK_TYPE"])
                for c in GD.candidatas_a_reparar(AGORA, **kw)}

    def test_quem_entra_e_quem_nao(self):
        html, yt = _contrato("IT-T7-001"), _contrato("IT-T8-001")
        yt["ACQUISITION"] = {"STRATEGY": "SCRAP_FASE"}
        pend = _contrato("IT-T7-002")
        self._contratos(html, yt, pend)
        for sid, e in (("IT-T7-001", LC.CONTRACTED_CANARY_FAILED),
                       ("IT-T8-001", LC.CONTRACTED_CANARY_FAILED),
                       ("IT-T7-002", LC.CANARY_PENDING),
                       ("IT-T7-003", LC.CANARY_PENDING),          # sem contrato
                       ("IT-T7-004", LC.CANARY_PENDING), ("IT-T7-004", LC.READY_FOR_COLLECTION),
                       ("CAND-0001", LC.CONTRACTED_CANARY_FAILED)):
            self._estado(sid, e)
        self.assertEqual({("IT-T7-001", F.REPAIR_CONTRACT), ("IT-T7-002", F.VALIDATE_ROUTE),
                          ("IT-T7-003", F.REPAIR_CONTRACT)}, self._cands())

    def test_um_reparo_por_fonte_salvo_morte_por_transporte(self):
        self._contratos(_contrato("IT-T7-001"))
        self._estado("IT-T7-001", LC.CONTRACTED_CANARY_FAILED)
        base = {"SOURCE_ID": "IT-T7-001", "TASK_TYPE": F.REPAIR_CONTRACT, "TASK_ID": "T1"}
        velho = (AGORA - timedelta(days=2)).isoformat()
        novo = (AGORA - timedelta(hours=1)).isoformat()
        for status, quando, entra in ((F.DONE, velho, False), (F.BLOCKED, velho, False),
                                      (F.FAILED, novo, False), (F.FAILED, velho, True),
                                      (F.PENDING, velho, False)):
            t = dict(base, STATUS=status, UPDATED_AT=quando)
            self.assertEqual(entra, bool(self._cands(tarefas=[t])), (status, quando))

    def test_fonte_com_tarefa_aberta_nao_entra(self):
        self._contratos(_contrato("IT-T7-001"))
        self._estado("IT-T7-001", LC.CONTRACTED_CANARY_FAILED)
        t = {"SOURCE_ID": "IT-T7-001", "TASK_TYPE": F.CANARY, "TASK_ID": "T1",
             "STATUS": F.WAITING_RETRY, "UPDATED_AT": AGORA.isoformat()}
        self.assertEqual(set(), self._cands(tarefas=[t]))

    def test_pendente_recente_nao_volta(self):
        self._contratos(_contrato("IT-T7-002"))
        self._estado("IT-T7-002", LC.CANARY_PENDING)
        t = {"SOURCE_ID": "IT-T7-002", "TASK_TYPE": F.CANARY, "TASK_ID": "T1", "STATUS": F.DONE,
             "UPDATED_AT": (AGORA - timedelta(hours=2)).isoformat()}
        self.assertEqual(set(), self._cands(tarefas=[t]))
        t["UPDATED_AT"] = (AGORA - timedelta(days=2)).isoformat()
        self.assertEqual({("IT-T7-002", F.VALIDATE_ROUTE)}, self._cands(tarefas=[t]))

    def test_reparar_encalhadas_enfileira_com_teto(self):
        cs = [_contrato("IT-T7-%03d" % i) for i in range(GD.REPARAR_POR_VOLTA + 5)]
        self._contratos(*cs)
        for c in cs:
            self._estado(c["SOURCE_ID"], LC.CONTRACTED_CANARY_FAILED)
        with mock.patch.object(GD, "requalificar_se_a_prova_mudou", return_value=[]):
            r = GD.reparar_encalhadas(AGORA)
        self.assertEqual(GD.REPARAR_POR_VOLTA, len(r["ENFILEIRADAS"]))
        self.assertEqual(5, r["RESTAM"])
        self.assertEqual(GD.REPARAR_POR_VOLTA,
                         sum(1 for t in F._ler()["TAREFAS"] if t["TASK_TYPE"] == F.REPAIR_CONTRACT))
        with mock.patch.object(GD, "requalificar_se_a_prova_mudou", return_value=[]):
            r2 = GD.reparar_encalhadas(AGORA)                       # abertas nao se repetem
        self.assertEqual(5, len(r2["ENFILEIRADAS"]))

    def test_youtube_barrado_nao_e_reaberto_sem_a_rota_do_scrap(self):
        self._contratos()
        F.FILA.write_text(json.dumps({"PROXIMO_ID": 3, "TAREFAS": [
            {"TASK_ID": "T1", "SOURCE_ID": "CAND-0001", "TASK_TYPE": F.QUALIFY, "PRIORITY": 30,
             "STATUS": F.BLOCKED, "ATTEMPTS": 0, "NEXT_ATTEMPT_AT": None, "MOTIVO": "",
             "LAST_ERROR": "YouTube exige channel_id e molde de video (conteudo real)",
             "CREATED_AT": "x", "UPDATED_AT": "x"},
            {"TASK_ID": "T2", "SOURCE_ID": "CAND-0002", "TASK_TYPE": F.QUALIFY, "PRIORITY": 30,
             "STATUS": F.BLOCKED, "ATTEMPTS": 0, "NEXT_ATTEMPT_AT": None, "MOTIVO": "",
             "LAST_ERROR": "LINKEDIN: coleta automatizada proibida pelos TOS",
             "CREATED_AT": "x", "UPDATED_AT": "x"}]}), encoding="utf-8")
        with mock.patch.object(GD, "requalificar_se_a_prova_mudou", return_value=[]):
            r = GD.reparar_encalhadas(AGORA)
        self.assertEqual(0, r["QUALIFY_REQUALIFICADAS"])
        st = {t["TASK_ID"]: t["STATUS"] for t in F._ler()["TAREFAS"]}
        self.assertEqual({"T1": F.BLOCKED, "T2": F.BLOCKED}, st)     # sem eco: o worker barra-a outra vez

    def test_sem_territorio_so_volta_com_prova_nova(self):
        self._contratos()
        F.FILA.write_text(json.dumps({"PROXIMO_ID": 3, "TAREFAS": [
            {"TASK_ID": "T%d" % i, "SOURCE_ID": cid, "TASK_TYPE": F.QUALIFY, "PRIORITY": 30,
             "STATUS": F.BLOCKED, "ATTEMPTS": 0, "NEXT_ATTEMPT_AT": None, "MOTIVO": "",
             "LAST_ERROR": GD.ASSINATURA_SEM_TERRITORIO + " (x)", "CREATED_AT": "x", "UPDATED_AT": "x"}
            for i, cid in ((1, "CAND-0001"), (2, "CAND-0002"))]}), encoding="utf-8")
        fichas = {"CANDIDATAS": [{"CANDIDATA_ID": "CAND-0001", "NOME": "ARPA Exemplo", "URL": B},
                                 {"CANDIDATA_ID": "CAND-0002", "NOME": "open.spotify.com",
                                  "URL": "https://open.spotify.com/show/x"}]}
        import decisao_semantica as DS
        sys.path.insert(0, str(AQUI.parent / "candidatas"))
        import fonte_nova as FN
        with mock.patch.object(FN, "carregar", return_value=fichas), \
                mock.patch.object(DS, "decisao_para", return_value=(None, "")):
            feitas = GD.requalificar_se_a_prova_mudou(AGORA)
        self.assertEqual(["T1"], feitas)
        st = {t["TASK_ID"]: t["STATUS"] for t in F._ler()["TAREFAS"]}
        self.assertEqual({"T1": F.PENDING, "T2": F.BLOCKED}, st)


class ReparoAntesDeDiscovery(_Pasta):
    def test_com_reparo_elegivel_nao_ha_discovery(self):
        self._contratos(_contrato("IT-T7-001"))
        self._estado("IT-T7-001", LC.CONTRACTED_CANARY_FAILED)
        chamadas = []
        with mock.patch.object(GD, "requalificar_se_a_prova_mudou", return_value=[]), \
                mock.patch.object(F, "elegiveis", return_value=[]):
            m = GD.talvez_alimentar({}, feeder_fn=lambda: {}, descobrir_fn=lambda: chamadas.append(1),
                                    agora=AGORA)
        self.assertEqual("REPARO_ANTES_DE_DISCOVERY", m["DECISAO"])
        self.assertEqual([], chamadas)
        self.assertGreater(m["REPARO_PENDENTE"], 0)

    def test_sem_reparo_a_discovery_volta(self):
        self._contratos()
        chamadas = []
        with mock.patch.object(GD, "requalificar_se_a_prova_mudou", return_value=[]):
            m = GD.talvez_alimentar({}, feeder_fn=lambda: {},
                                    descobrir_fn=lambda: chamadas.append(1) or {}, agora=AGORA)
        self.assertEqual("DISCOVERY_ACCIONADA", m["DECISAO"])
        self.assertEqual([1], chamadas)


if __name__ == "__main__":
    unittest.main()
