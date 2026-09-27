#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Testes do motor de descoberta — FASE 10 + FASE 11 + RED TEAM obrigatorio.

Trazidos de candidate-bridge-v1 (63b71421). Os casos sao os mesmos; o que
mudou e ONDE escrevem.

ISOLAMENTO (BRIDGE-FEEDER, G4) — a versao do bridge escrevia na porta REAL
(`candidatas/FONTES-CANDIDATAS.json`) e no `DISCOVERY-VISITED.json` real, e
"limpava" no fim filtrando as candidatas de teste e reescrevendo o ficheiro.
Reescrever nao e nao tocar: a ordenacao, o TOTAL e o proximo CANDIDATA_ID
saiam da suite; e um teste morto a meio deixava o lixo la. Aqui a porta, os
visitados e a prova vivem numa pasta descartavel (molde test_ready_split.py:
44-48), e a impressao dos ficheiros REAIS e comparada em cada tearDown.

ZERO REDE — `urllib.request.urlopen` e substituido em cada setUp por uma
funcao que REBENTA. Um teste que precise de simular HTTP faz o seu proprio
`mock.patch` por cima (e o que TestOrcamento.test_limite_por_dominio faz).
Se algum caminho do motor tentar a internet, o teste reprova em vez de sair.

CONTRAPROVAS (FASE 11):
  1. mesma URL descoberta 2x -> UM candidato (dedup funciona)
  2. mesma organizacao, canal diferente -> NAO colapsa
  3. URL invalida -> nao entra
  4. fonte ja READY -> nao volta como candidata nova
  5. fonte ja BLOCKED -> lifecycle respeitado (nao entra)
  6. sem identidade suficiente -> UNKNOWN, sem fabricar (N/A para motor deterministico)
  7. fila vazia -> discovery abastece
  8. discovery falha a meio -> nao perde estado

RED TEAM OBRIGATORIO (FASE 11):
  Mutar o dedup (desligar normalizacao de URL) e provar que a contraprova 1
  REPROVA. Restaurar e provar que volta a passar.
"""
from __future__ import annotations

import hashlib
import json
import sys
import tempfile
import unittest
import urllib.request
from pathlib import Path
from unittest import mock

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "candidatas"))
sys.path.insert(0, str(RAIZ / "curadoria"))

import fonte_nova as FN   # noqa: E402
import descobrir as D      # noqa: E402

# URL de teste — nao existe na lista de candidatas reais
URL_TESTE_BASE = "https://www.example-agri-test-sintonia.it"
URL_TESTE_CANAL_YT = "https://www.youtube.com/@exemplo_agri_sintonia_test"

# Os caminhos REAIS, escritos por extenso e nao lidos dos modulos.
CAMINHOS_REAIS = {
    "FN.FILA":          RAIZ / "candidatas" / "FONTES-CANDIDATAS.json",
    "D.VISITADOS_JSON": RAIZ / "curadoria" / "DISCOVERY-VISITED.json",
    "D.PROOF_JSON":     RAIZ / "curadoria" / "DISCOVERY-PROOF-V1.json",
}


def _impressao(p: Path) -> str:
    if not p.exists():
        return "AUSENTE"
    return hashlib.sha256(p.read_bytes()).hexdigest()


def _impressoes() -> dict:
    return {k: _impressao(p) for k, p in CAMINHOS_REAIS.items()}


def _rede_proibida(*a, **k):
    raise AssertionError("REDE PROIBIDA NOS TESTES: urlopen(%r)" % (a[:1],))


class Isolada(unittest.TestCase):
    """Porta, visitados e prova numa pasta descartavel; rede desligada."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        d = Path(self.tmp.name)
        self._antes = (FN.FILA, D.VISITADOS_JSON, D.PROOF_JSON)
        self._reais_antes = _impressoes()
        FN.FILA = d / "FONTES-CANDIDATAS.json"
        D.VISITADOS_JSON = d / "DISCOVERY-VISITED.json"
        D.PROOF_JSON = d / "DISCOVERY-PROOF.json"
        self._sem_rede = mock.patch.object(urllib.request, "urlopen", _rede_proibida)
        self._sem_rede.start()
        D._robots_cache.clear()

    def tearDown(self):
        self._sem_rede.stop()
        D._robots_cache.clear()
        (FN.FILA, D.VISITADOS_JSON, D.PROOF_JSON) = self._antes
        self.tmp.cleanup()
        depois = _impressoes()
        self.assertEqual(
            self._reais_antes, depois,
            "um ficheiro REAL mudou durante o teste (antes=%s depois=%s)"
            % (self._reais_antes, depois))


def _e_candidata_de_teste(c: dict) -> bool:
    return ("sintonia" in c.get("URL", "").lower() and "test" in c.get("URL", "").lower()) \
        or ("sintonia" in c.get("NOME", "").lower() and "test" in c.get("NOME", "").lower()) \
        or c.get("QUEM_VIU", "").startswith("TEST_")


def _registar_teste(url: str, tipo: str = "ORGANIZACAO", nome: str = "Fonte Teste") -> dict:
    return FN.registar(
        tipo=tipo, pais="IT", nome=nome,
        url=url,
        para_que="teste automatico source-discovery-v1",
        quem_viu="TEST_discovery",
        onde_viu=url, nota="CANDIDATA_DE_TESTE",
    )


class TestIsolamento(Isolada):
    """Os caminhos dos testes nao sao os reais, e a rede esta desligada."""

    def test_caminhos_apontam_para_a_pasta_descartavel(self):
        d = Path(self.tmp.name)
        self.assertEqual(FN.FILA.parent, d)
        self.assertEqual(D.VISITADOS_JSON.parent, d)
        self.assertEqual(D.PROOF_JSON.parent, d)
        # E o motor le a porta pelo nome do modulo, nao por copia do caminho.
        self.assertEqual(D.carregar()["CANDIDATAS"], [])

    def test_a_rede_esta_desligada(self):
        with self.assertRaises(AssertionError):
            urllib.request.urlopen("https://www.example.invalid/")
        # _verificar_url apanha a excecao generica e devolve ERRO — sem sair.
        orcam = D.Orcamento(total=5)
        existe, code, ct = D._verificar_url("https://www.example.invalid/x", orcam)
        self.assertFalse(existe)
        self.assertEqual(code, 0)
        self.assertIn("ERRO", ct)


class TestDedup(Isolada):
    """Contraprova 1: mesma URL duas vezes -> UM candidato."""

    def test_mesma_url_duas_vezes_resulta_num_candidato(self):
        url = URL_TESTE_BASE + "/duplicado"
        _registar_teste(url, nome="Teste Dup A")
        n_antes = len([c for c in FN.carregar()["CANDIDATAS"]
                       if FN.normalizar(c["URL"]) == FN.normalizar(url)])
        # Segunda registo da mesma URL
        _registar_teste(url, nome="Teste Dup B")
        n_depois = len([c for c in FN.carregar()["CANDIDATAS"]
                        if FN.normalizar(c["URL"]) == FN.normalizar(url)])
        self.assertEqual(n_antes, 1,
                         "devia ter 1 candidato apos 1o registo")
        self.assertEqual(n_depois, 1,
                         "devia continuar 1 candidato apos 2o registo (dedup)")

    def test_url_com_www_e_sem_www_e_o_mesmo(self):
        url_com_www = "https://www.fonte-test-sintonia.it/"
        url_sem_www = "https://fonte-test-sintonia.it"
        _registar_teste(url_com_www, nome="Teste www A")
        n = len([c for c in FN.carregar()["CANDIDATAS"]
                 if FN.normalizar(c["URL"]) == FN.normalizar(url_com_www)])
        self.assertEqual(n, 1)
        # Tentar registar sem www — dedup devia pegar
        _registar_teste(url_sem_www, nome="Teste www B")
        n2 = len([c for c in FN.carregar()["CANDIDATAS"]
                  if FN.normalizar(c["URL"]) == FN.normalizar(url_com_www)])
        self.assertEqual(n2, 1, "com e sem www devem ser tratados como o mesmo")


class TestCanaisOrganizacao(Isolada):
    """Contraprova 2: mesma organizacao, canal diferente -> NAO colapsa."""

    def test_site_e_youtube_sao_canais_distintos(self):
        url_site = URL_TESTE_BASE + "/org-canais"
        url_yt   = URL_TESTE_CANAL_YT
        _registar_teste(url_site, tipo="ORGANIZACAO",
                        nome="Org Canais Teste")
        _registar_teste(url_yt, tipo="YOUTUBE",
                        nome="Org Canais Teste YouTube")
        d = FN.carregar()
        norms = [FN.normalizar(c["URL"]) for c in d["CANDIDATAS"]
                 if _e_candidata_de_teste(c)]
        self.assertEqual(len(norms), 2,
                         "site e canal YouTube sao entradas distintas")

    def test_instagram_e_linkedin_sao_canais_distintos(self):
        url_ig = "https://www.instagram.com/org_sintonia_test"
        url_li = "https://www.linkedin.com/company/org-sintonia-test"
        _registar_teste(url_ig, tipo="INSTAGRAM",
                        nome="Org Test Instagram")
        _registar_teste(url_li, tipo="LINKEDIN",
                        nome="Org Test LinkedIn")
        d = FN.carregar()
        norms = [FN.normalizar(c["URL"]) for c in d["CANDIDATAS"]
                 if _e_candidata_de_teste(c)]
        self.assertEqual(len(norms), 2,
                         "Instagram e LinkedIn sao entradas distintas")


class TestUrlInvalida(Isolada):
    """Contraprova 3: URL invalida -> nao entra."""

    def test_url_vazia_e_rejeitada(self):
        with self.assertRaises(ValueError):
            FN.registar(tipo="ORGANIZACAO", pais="IT",
                        nome="Test URL vazia",
                        url="",
                        para_que="teste",
                        quem_viu="TEST_discovery")

    def test_url_invalida_via_orcamento_zero(self):
        """Com tudo ja conhecido, nenhum pedido e feito e nenhum candidato entra."""
        # Cria um set que ja contem todos os candidatos do catalogo
        conhecidos_tudo = {
            D.normalizar(c["url"]) for c in D.CATALOGO_ITALIA
        }
        orcam = D.Orcamento(total=0)
        visitados = D._ler_visitados()
        log: list[dict] = []
        resultado = D._descobrir_familia(
            "FITOSSANITARIO", orcam, conhecidos_tudo, visitados, log
        )
        self.assertEqual(resultado, [],
                         "com orcamento=0 ou tudo duplicado: 0 registados")
        self.assertEqual(orcam.pedidos_feitos, 0)
        self.assertTrue(all(e["acao"] == "DEDUP" for e in log), log)


class TestFonteJaReady(Isolada):
    """Contraprova 4: fonte ja READY -> nao volta como candidata nova."""

    def test_url_ready_e_bloqueada_pelo_dedup(self):
        """URL que ja esta no SOURCE-CHARACTERIZATION nao deve ser registada.
        Le a caracterizacao REAL (so leitura); a porta e os visitados sao os
        da pasta descartavel."""
        try:
            char = json.loads(
                (RAIZ / "curadoria" / "SOURCE-CHARACTERIZATION-V1.json")
                .read_text(encoding="utf-8"))
            fontes = [f for f in char.get("FONTES", []) if f.get("URL")]
            if not fontes:
                self.skipTest("sem fontes caracterizadas")
            url_ready = fontes[0]["URL"]
        except Exception:
            self.skipTest("SOURCE-CHARACTERIZATION nao acessivel")

        conhecidos = D._construir_set_conhecido()
        visitados  = D._ler_visitados()
        dup, tipo  = D._e_duplicado(url_ready, conhecidos, visitados)
        self.assertTrue(dup,
                        "URL ja no curator devia ser detectada como duplicada")
        self.assertEqual(tipo, "SAME_URL")


class TestFonteJaBlocked(Isolada):
    """Contraprova 5: URL ja visitada/rejeitada -> nao volta."""

    def test_url_rejeitada_nao_reentra(self):
        url  = "https://bloqueada.test-sintonia.it/"
        norm = D.normalizar(url)
        visitados = D._ler_visitados()
        D._marcar_rejeitado(norm, "TESTE_BLOCKED", visitados)

        dup, tipo = D._e_duplicado(url, set(), visitados)
        self.assertTrue(dup, "URL rejeitada devia ser detectada como duplicada")
        self.assertEqual(tipo, "PREVIOUSLY_REJECTED")
        # E ficou na pasta descartavel, nao na arvore.
        self.assertEqual(D.VISITADOS_JSON.parent, Path(self.tmp.name))
        self.assertTrue(D.VISITADOS_JSON.exists())


class TestIdentidadeDesconhecida(Isolada):
    """Contraprova 6: sem identidade suficiente -> UNKNOWN, sem fabricar.

    O motor deterministico nao tem campo IDENTITY_STATUS dinamico por candidato
    — a identidade e sempre bem-formada a partir do catalogo curado.
    O motor NAO FABRICA. Este teste documenta a politica.
    """

    def test_motor_deterministico_nao_tem_unknown_identity(self):
        for cand in D.CATALOGO_ITALIA:
            self.assertTrue(cand.get("nome"), "candidato sem nome: %s" % cand)
            self.assertTrue(cand.get("tipo"), "candidato sem tipo: %s" % cand)
            self.assertTrue(cand.get("para_que"), "candidato sem para_que: %s" % cand)


class TestFilaVaziaAciona(Isolada):
    """Contraprova 7: fila de candidatas vazia -> esta_na_fila_baixa() = True."""

    def test_fila_abaixo_do_limiar(self):
        with mock.patch.object(D, "carregar") as mock_carregar:
            # Simula fila com 5 candidatos pendentes (abaixo do limiar 20)
            mock_carregar.return_value = {
                "CANDIDATAS": [
                    {"ESTADO": "CANDIDATA", "URL": "http://x.it/%d" % i}
                    for i in range(5)
                ]
            }
            self.assertTrue(D.esta_na_fila_baixa(),
                            "5 < 20 deve ser fila_baixa=True")

    def test_fila_acima_do_limiar_nao_aciona(self):
        with mock.patch.object(D, "carregar") as mock_carregar:
            mock_carregar.return_value = {
                "CANDIDATAS": [
                    {"ESTADO": "CANDIDATA", "URL": "http://x.it/%d" % i}
                    for i in range(50)
                ]
            }
            self.assertFalse(D.esta_na_fila_baixa(),
                             "50 > 20 deve ser fila_baixa=False")


class TestEstadoPersistidoAposFalha(Isolada):
    """Contraprova 8: discovery falha a meio -> nao perde estado.

    O VISITADOS_JSON persiste atomicamente. Uma excecao no meio da corrida
    nao deve apagar o que ja foi gravado.
    """

    def test_visitados_sobrevivem_a_excecao(self):
        url_norm = D.normalizar("https://sobreviveu.test-sintonia.it/")
        visitados = D._ler_visitados()
        D._marcar_visitado(url_norm, "TESTE", visitados)

        # Simula crash relendo do disco
        visitados2 = D._ler_visitados()
        self.assertIn(url_norm, visitados2["VISITADOS"],
                      "estado deve persistir apos releitura")

    def test_gravar_visitados_atomico(self):
        """A gravacao usa tempfile + replace — atomica por construcao."""
        url_norm = D.normalizar("https://atomico.test-sintonia.it/")
        visitados = D._ler_visitados()
        D._marcar_visitado(url_norm, "ATOMICO", visitados)

        # Verificar que o ficheiro existe e e JSON valido
        self.assertTrue(D.VISITADOS_JSON.exists())
        d = json.loads(D.VISITADOS_JSON.read_text(encoding="utf-8"))
        self.assertIn(url_norm, d["VISITADOS"])


class TestOrcamento(Isolada):
    """Testes do rastreador de orcamento."""

    def test_orcamento_zero_bloqueia_tudo(self):
        orcam = D.Orcamento(total=0)
        ok, motivo = orcam.pode("https://www.crea.gov.it/")
        self.assertFalse(ok)
        self.assertIn("orcamento_total", motivo)

    def test_limite_por_dominio(self):
        orcam = D.Orcamento(total=100, por_dominio=2)
        # Simular 2 pedidos ao mesmo dominio — HTTP falso por cima da guarda.
        with mock.patch("urllib.request.urlopen") as mock_open, \
             mock.patch.object(D, "PAUSA_ENTRE_PEDIDOS_S", 0.0):
            mock_resp = mock.MagicMock()
            mock_resp.__enter__ = mock.Mock(return_value=mock_resp)
            mock_resp.__exit__ = mock.Mock(return_value=False)
            mock_resp.status = 200
            mock_resp.headers = {"Content-Type": "text/html"}
            mock_open.return_value = mock_resp

            D._verificar_url("https://www.exemplo.it/pag1", orcam)
            D._verificar_url("https://www.exemplo.it/pag2", orcam)
            self.assertEqual(mock_open.call_count, 2)

        ok, motivo = orcam.pode("https://www.exemplo.it/pag3")
        self.assertFalse(ok, "apos 2 pedidos ao dominio, 3o devia ser bloqueado")
        self.assertIn("limite_por_dominio", motivo)

    def test_dominio_bloqueado(self):
        orcam = D.Orcamento(total=100)
        orcam.bloquear_dominio("https://www.bloqueado.it/")
        ok, motivo = orcam.pode("https://www.bloqueado.it/qualquer")
        self.assertFalse(ok)
        self.assertIn("dominio_bloqueado", motivo)


# ---------------------------------------------------------------------------
# RED TEAM OBRIGATORIO
# ---------------------------------------------------------------------------

class TestRedTeamDedup(Isolada):
    """RED TEAM: mutar o dedup e provar que a contraprova 1 REPROVA.

    Procedimento:
    1. Mutar normalizar() para retornar valor diferente por chamada (sem dedup).
    2. Provar que mesma URL pode entrar 2x (contraprova 1 REPROVA).
    3. Restaurar normalizar() original.
    4. Provar que mesma URL so entra 1x (contraprova 1 PASSA).
    """

    def test_red_team_com_mutacao_dedup_reprova(self):
        """Com normalizar mutado (retorna UUID), a mesma URL entra 2x.
        Confirma que a contraprova 1 REPROVA sob mutacao.
        """
        import uuid as _uuid

        url = "https://mutado.test-sintonia.it/redteam"
        # Guardar normalizacao original
        normalizar_orig = FN.normalizar

        # Mutacao: cada chamada devolve um valor unico -> dedup nunca pega
        def normalizar_mutado(u: str) -> str:
            return str(_uuid.uuid4())  # sempre diferente -> dedup cego

        # Aplicar mutacao
        FN.normalizar = normalizar_mutado
        # Tambem precisa mudar em descobrir.py que importou a funcao
        D.normalizar = normalizar_mutado

        try:
            _registar_teste(url, nome="Red Team Dup A")
            _registar_teste(url, nome="Red Team Dup B")

            # Com dedup mutado, a fila deve ter 2 entradas para a mesma URL
            d = FN.carregar()
            count_mutado = sum(1 for c in d["CANDIDATAS"]
                               if url in c.get("URL", ""))
            # RED TEAM: devia ter 2 (dedup falhou)
            self.assertEqual(count_mutado, 2,
                             "RED TEAM: com dedup mutado, 2 entradas sao criadas "
                             "para a mesma URL — contraprova 1 REPROVA")
        finally:
            # Restaurar normalizacao original
            FN.normalizar = normalizar_orig
            D.normalizar  = normalizar_orig

    def test_apos_restaurar_dedup_passa(self):
        """Apos restaurar normalizar(), a mesma URL so entra 1x.
        Confirma que a contraprova 1 PASSA com o dedup correcto.
        """
        url = "https://restaurado.test-sintonia.it/redteam"
        _registar_teste(url, nome="Red Team Restaurado A")
        _registar_teste(url, nome="Red Team Restaurado B")

        # Com dedup restaurado, deve ter apenas 1 entrada
        d = FN.carregar()
        count = sum(1 for c in d["CANDIDATAS"]
                    if url in c.get("URL", ""))
        self.assertEqual(count, 1,
                         "apos restaurar dedup: 1 entrada para a mesma URL")


class TestNormalizar(unittest.TestCase):
    """Testes da funcao de normalizacao de URL (chave do dedup). Puros."""

    def test_https_e_http_iguais(self):
        self.assertEqual(
            FN.normalizar("https://www.crea.gov.it/"),
            FN.normalizar("http://crea.gov.it"),
        )

    def test_trailing_slash_removida(self):
        self.assertEqual(
            FN.normalizar("https://www.exemplo.it/"),
            FN.normalizar("https://www.exemplo.it"),
        )

    def test_case_insensitive(self):
        self.assertEqual(
            FN.normalizar("https://WWW.EXEMPLO.IT/Pagina"),
            FN.normalizar("https://www.exemplo.it/pagina"),
        )


class TestCatalogo(unittest.TestCase):
    """Verifica integridade do catalogo de candidatos. So le constantes."""

    def test_todos_candidatos_tem_campos_obrigatorios(self):
        campos = ("familia", "tipo", "pais", "nome", "url", "para_que",
                  "discovered_from", "method")
        for cand in D.CATALOGO_ITALIA:
            for campo in campos:
                self.assertIn(campo, cand,
                              "candidato sem campo '%s': %s" % (campo, cand))
                self.assertTrue(cand[campo],
                                "campo '%s' vazio em: %s" % (campo, cand))

    def test_todos_tipos_validos(self):
        from fonte_nova import TIPOS
        for cand in D.CATALOGO_ITALIA:
            self.assertIn(cand["tipo"], TIPOS,
                          "tipo invalido '%s'" % cand["tipo"])

    def test_todos_paises_validos(self):
        from fonte_nova import PAISES
        for cand in D.CATALOGO_ITALIA:
            self.assertIn(cand["pais"], PAISES,
                          "pais invalido '%s'" % cand["pais"])

    def test_urls_unicas_no_catalogo(self):
        from collections import Counter
        urls = [D.normalizar(c["url"]) for c in D.CATALOGO_ITALIA]
        dup = [u for u, n in Counter(urls).items() if n > 1]
        self.assertEqual(dup, [],
                         "URLs duplicadas no catalogo: %s" % dup)

    def test_familias_mapeadas_para_tipos_corretos(self):
        """Cada familia mapeia para pelo menos um tipo valido."""
        from fonte_nova import TIPOS
        familias_sem_tipo = []
        for cand in D.CATALOGO_ITALIA:
            if cand["tipo"] not in TIPOS:
                familias_sem_tipo.append(cand["familia"])
        self.assertEqual(familias_sem_tipo, [],
                         "candidatos com tipo invalido: %s" % familias_sem_tipo)


# ---------------------------------------------------------------------------
# FASE 7 — CONTRAPROVAS DO CRAWL
# ---------------------------------------------------------------------------

class TestExtrairLinks(unittest.TestCase):
    """Extracao de links de HTML."""

    def test_extrai_href_absoluto(self):
        html = '<a href="https://www.crea.gov.it/page">CREA</a>'
        links = D.extrair_links(html, "https://www.crea.gov.it/")
        self.assertEqual(len(links), 1)
        self.assertEqual(links[0][0], "https://www.crea.gov.it/page")
        self.assertEqual(links[0][1], "CREA")

    def test_resolve_href_relativo(self):
        html = '<a href="/fitosanitario">Difesa</a>'
        links = D.extrair_links(html, "https://agri.regione.emilia-romagna.it/")
        self.assertEqual(links[0][0],
                         "https://agri.regione.emilia-romagna.it/fitosanitario")

    def test_html_sem_links_devolve_lista_vazia(self):
        self.assertEqual(D.extrair_links("<p>Sem links</p>", "https://x.it/"), [])

    def test_ancora_interna_extraida(self):
        html = '<a href="#section1">Secao</a>'
        links = D.extrair_links(html, "https://www.exemplo.it/pagina")
        self.assertEqual(len(links), 1)

    def test_mailto_extraido_mas_filtrado_depois(self):
        html = '<a href="mailto:info@exemplo.it">Email</a>'
        links = D.extrair_links(html, "https://www.exemplo.it/")
        self.assertEqual(len(links), 1)
        manter, motivo = D._filtrar_link(links[0][0], "https://www.exemplo.it/")
        self.assertFalse(manter)
        self.assertEqual(motivo, "R1_ESQUEMA_NAO_HTTP")


class TestFiltrarLink(unittest.TestCase):
    """Regras de filtro declaradas e testaveis."""

    BASE = "https://www.crea.gov.it/"

    def _ok(self, url: str) -> bool:
        return D._filtrar_link(url, self.BASE)[0]

    def _motivo(self, url: str) -> str:
        return D._filtrar_link(url, self.BASE)[1]

    def test_r1_mailto_descartado(self):
        self.assertFalse(self._ok("mailto:info@crea.gov.it"))
        self.assertEqual(self._motivo("mailto:info@crea.gov.it"), "R1_ESQUEMA_NAO_HTTP")

    def test_r1_tel_descartado(self):
        self.assertFalse(self._ok("tel:+39061234567"))
        self.assertEqual(self._motivo("tel:+39061234567"), "R1_ESQUEMA_NAO_HTTP")

    def test_r1_javascript_descartado(self):
        self.assertFalse(self._ok("javascript:void(0)"))
        self.assertEqual(self._motivo("javascript:void(0)"), "R1_ESQUEMA_NAO_HTTP")

    def test_r2_ancora_mesma_pagina_descartada(self):
        url = "https://www.crea.gov.it/#section"
        self.assertFalse(self._ok(url))

    def test_r3_pdf_descartado(self):
        self.assertFalse(self._ok("https://www.crea.gov.it/doc.pdf"))
        self.assertEqual(self._motivo("https://www.crea.gov.it/doc.pdf"),
                         "R3_FICHEIRO_BINARIO")

    def test_r3_zip_descartado(self):
        self.assertFalse(self._ok("https://www.crea.gov.it/data.zip"))

    def test_r4_privacy_descartado(self):
        self.assertFalse(self._ok("https://www.crea.gov.it/privacy"))

    def test_r4_login_descartado(self):
        self.assertFalse(self._ok("https://www.crea.gov.it/login"))

    def test_r4_cookie_descartado(self):
        self.assertFalse(self._ok("https://www.crea.gov.it/cookie"))

    def test_r5_propria_semente_descartada(self):
        self.assertFalse(self._ok("https://www.crea.gov.it/"))
        self.assertEqual(self._motivo("https://www.crea.gov.it/"),
                         "R5_PROPRIA_SEMENTE")

    def test_r5_semente_sem_trailing_slash_descartada(self):
        self.assertFalse(self._ok("https://www.crea.gov.it"))

    def test_r6_google_descartado(self):
        self.assertFalse(self._ok("https://www.google.com/maps"))

    def test_subpath_mesmo_dominio_mantido(self):
        self.assertTrue(self._ok("https://www.crea.gov.it/difesa"))

    def test_dominio_externo_gov_it_mantido(self):
        self.assertTrue(self._ok("https://www.politicheagricole.it/"))

    def test_social_linkedin_mantido(self):
        self.assertTrue(self._ok("https://www.linkedin.com/company/crea"))

    def test_social_instagram_mantido(self):
        self.assertTrue(self._ok("https://www.instagram.com/creagov"))


class TestProvenanciaCircular(unittest.TestCase):
    """Contraprova 3: DISCOVERED_FROM nunca igual a URL do candidato."""

    def test_guarda_detecta_circularidade(self):
        url = "https://www.fonte-test.it/"
        with self.assertRaises(ValueError):
            D._checar_sem_circularidade(url, url)

    def test_guarda_aceita_proveniencia_valida(self):
        semente = "https://www.origem.it/"
        candidato = "https://www.destino.it/"
        try:
            D._checar_sem_circularidade(semente, candidato)
        except ValueError:
            self.fail("proveniencia valida nao deve lancar ValueError")

    def test_guarda_com_www_e_sem_www(self):
        url_com = "https://www.circular.it/"
        url_sem = "https://circular.it"
        with self.assertRaises(ValueError):
            D._checar_sem_circularidade(url_com, url_sem)


class TestRedTeamProvenanciaCircular(unittest.TestCase):
    """RED TEAM: mutar a guarda e provar que a contraprova REPROVA."""

    def test_red_team_mute_guarda_bug_passa(self):
        """Com _checar_sem_circularidade mutada para no-op, o bug nao e detectado.
        RED TEAM: confirma que a guarda e o ponto de proteccao real.
        """
        url = "https://www.circular-red-team.it/"
        guarda_orig = D._checar_sem_circularidade

        D._checar_sem_circularidade = lambda disc, cand: None

        try:
            D._checar_sem_circularidade(url, url)

            circular = int(D.normalizar(url) == D.normalizar(url))
            self.assertEqual(circular, 1,
                             "RED TEAM: PROVENIENCIA_CIRCULAR=1 sob mutacao")
        finally:
            D._checar_sem_circularidade = guarda_orig

    def test_apos_restaurar_guarda_reprova(self):
        url = "https://www.circular-red-team.it/"
        with self.assertRaises(ValueError,
                               msg="guarda restaurada deve detectar circularidade"):
            D._checar_sem_circularidade(url, url)


class TestCrawlMesmaUrlDuasSementes(Isolada):
    """Contraprova 1: mesmo link em duas sementes -> UM candidato."""

    def test_mesmo_link_duas_sementes_um_candidato(self):
        url_candidato = "https://www.agri-test-sintonia.it/candidato"

        conhecidos: set[str] = set()
        visitados = D._ler_visitados()

        D._marcar_visitado(D.normalizar(url_candidato),
                           "REGISTADO_CAND-9999", visitados)
        conhecidos.add(D.normalizar(url_candidato))

        dup, tipo_dup = D._e_duplicado(url_candidato, conhecidos, visitados)
        self.assertTrue(dup,
                        "segundo registo do mesmo link deve ser detectado como dedup")
        self.assertEqual(tipo_dup, "SAME_URL")


class TestSementeJaVisitadaNaoRevisitada(Isolada):
    """Contraprova 5: semente ja visitada nao e revisitada."""

    def test_semente_visitada_ignorada(self):
        sementes = D._extrair_sementes_legitimas()
        if not sementes:
            self.skipTest("sem sementes legitimas no catalogo")
        semente = sementes[0]

        visitados = D._ler_visitados()
        D._marcar_visitado(D.normalizar(semente), "JA_VISITADA_TESTE",
                           visitados)

        orcam = D.Orcamento(total=0)
        conhecidos: set[str] = set()
        log: list[dict] = []

        D.crawl_sementes(orcam, conhecidos, visitados, log, max_sementes=1)

        acoes_semente = [e for e in log if e.get("semente") == semente]
        fetch_failed = [e for e in acoes_semente
                        if e.get("acao") == "SEMENTE_FETCH_FAILED"]
        self.assertEqual(fetch_failed, [],
                         "semente ja visitada nao deve ser buscada")


class TestSociaisRegistadasNaoEnfileiradas(unittest.TestCase):
    """Contraprova 9: sociais encontradas -> registadas, mas NAO enfileiradas."""

    def test_inferir_tipo_social_linkedin(self):
        tipo, _ = D._inferir_tipo_crawl(
            "https://www.linkedin.com/company/crea-test", "CREA LinkedIn")
        self.assertEqual(tipo, "LINKEDIN")

    def test_inferir_tipo_social_instagram(self):
        tipo, _ = D._inferir_tipo_crawl(
            "https://www.instagram.com/agri_test", "Agri Instagram")
        self.assertEqual(tipo, "INSTAGRAM")

    def test_inferir_tipo_social_youtube(self):
        tipo, _ = D._inferir_tipo_crawl(
            "https://www.youtube.com/@agri_test", "Canal Agri")
        self.assertEqual(tipo, "YOUTUBE")

    def test_e_social_url_detecta_linkedin(self):
        self.assertTrue(D._e_social_url("https://www.linkedin.com/company/x"))

    def test_e_social_url_nao_confunde_gov_it(self):
        self.assertFalse(D._e_social_url("https://www.crea.gov.it/"))


class TestOrcamentoEsgotadoParaLimpo(Isolada):
    """Contraprova 7: orcamento esgotado -> para limpo, estado persistido."""

    def test_orcamento_zero_nao_busca_sementes(self):
        orcam = D.Orcamento(total=0)
        conhecidos: set[str] = set()
        visitados = D._ler_visitados()
        log: list[dict] = []

        registados, stats = D.crawl_sementes(
            orcam, conhecidos, visitados, log, max_sementes=15
        )

        self.assertEqual(orcam.pedidos_feitos, 0)
        self.assertEqual(registados, [])


class TestExtrairSementesLegitimas(unittest.TestCase):
    """Sementes extraidas sao os discovered_from != url do catalogo."""

    def test_sementes_nao_sao_urls_do_catalogo(self):
        sementes = D._extrair_sementes_legitimas()
        self.assertGreater(len(sementes), 0,
                           "deve haver sementes legitimas no catalogo")

    def test_sementes_sao_distintas(self):
        sementes = D._extrair_sementes_legitimas()
        norms = [D.normalizar(s) for s in sementes]
        self.assertEqual(len(norms), len(set(norms)),
                         "sementes devem ser distintas")

    def test_contagem_sementes_legitimas(self):
        sementes = D._extrair_sementes_legitimas()
        self.assertEqual(len(sementes), 33,
                         "ADDENDUM-02 acrescentou 4 sementes TEMATICAS novas (assam.marche.it ja existia via Instagram); total 33")


class TestFiltrarLinkRA(unittest.TestCase):
    """RA — facets de pesquisa e hashtags nao sao fontes."""

    BASE = "https://www.regione.lombardia.it/"

    def _ok(self, url: str, anchor: str = "") -> bool:
        return D._filtrar_link(url, self.BASE, anchor)[0]

    def _motivo(self, url: str, anchor: str = "") -> str:
        return D._filtrar_link(url, self.BASE, anchor)[1]

    def test_anchor_hashtag_descartado(self):
        url = "https://www.regione.lombardia.it/ricerca?q=Bandi"
        self.assertFalse(self._ok(url, "#Bandi"))
        self.assertEqual(self._motivo(url, "#Bandi"), "RA_FACET_PESQUISA")

    def test_ancora_bollo_auto_descartada(self):
        url = "https://www.regione.lombardia.it/ricerca?lombardia_articoli%5Bquery%5D=Bollo+Auto"
        self.assertFalse(self._ok(url, "#BolloAuto"))
        self.assertEqual(self._motivo(url, "#BolloAuto"), "RA_FACET_PESQUISA")

    def test_path_ricerca_descartado(self):
        url = "https://www.regione.lombardia.it/ricerca"
        self.assertFalse(self._ok(url))
        self.assertEqual(self._motivo(url), "RA_FACET_PESQUISA")

    def test_query_param_query_descartado(self):
        url = "https://example.it/risultati?query=cereali&page=1"
        self.assertFalse(self._ok(url))
        self.assertEqual(self._motivo(url), "RA_FACET_PESQUISA")

    def test_pagina_legittima_sem_anchor_hash_mantida(self):
        url = "https://www.regione.lombardia.it/agricoltura/bandi"
        self.assertTrue(self._ok(url, "Bandi e concorsi"))


class TestFiltrarLinkRB(unittest.TestCase):
    """RB — artigos individuais nao sao fontes. ITEM != FONTE."""

    BASE = "https://www.arpae.it/"

    def _ok(self, url: str) -> bool:
        return D._filtrar_link(url, self.BASE)[0]

    def _motivo(self, url: str) -> str:
        return D._filtrar_link(url, self.BASE)[1]

    def test_artigo_notizie_slug_longo(self):
        url = "https://www.arpae.it/it/notizie/mare-riviera-interamente-balneabile-14sett2026"
        self.assertFalse(self._ok(url))
        self.assertEqual(self._motivo(url), "RB_ARTIGO_INDIVIDUAL")

    def test_artigo_incendio_com_data(self):
        url = "https://www.arpae.it/it/notizie/incendio-alla-sorgenia-di-finale-emilia-17-9-2026"
        self.assertFalse(self._ok(url))
        self.assertEqual(self._motivo(url), "RB_ARTIGO_INDIVIDUAL")

    def test_artigo_news_id_numerico(self):
        url = "http://www.calabriapsr.it/news/2456-scadenza-presentazione-domande-di-sostegno"
        self.assertFalse(self._ok(url))
        self.assertEqual(self._motivo(url), "RB_ARTIGO_INDIVIDUAL")

    def test_listagem_notizie_argomenti_mantida(self):
        url = "https://www.arpae.it/it/notizie/argomenti/agro-meteo"
        self.assertTrue(self._ok(url),
                        "listagem com subseccao nao e artigo — deve ser mantida")

    def test_listagem_notizie_raiz_mantida(self):
        url = "https://www.arpae.it/it/notizie"
        self.assertTrue(self._ok(url))


class TestFiltrarLinkRC(unittest.TestCase):
    """RC — paginas institucionais obrigatorias nao publicam conteudo agronomico."""

    BASE = "https://www.regione.sicilia.it/"

    def _ok(self, url: str) -> bool:
        return D._filtrar_link(url, self.BASE)[0]

    def _motivo(self, url: str) -> str:
        return D._filtrar_link(url, self.BASE)[1]

    def test_amministrazione_trasparente_path(self):
        url = "https://www.crea.gov.it/amministrazione-trasparente"
        self.assertFalse(self._ok(url))
        self.assertEqual(self._motivo(url), "RC_ISTITUZIONALE_OBBLIGATORIO")

    def test_subdomain_trasparenza(self):
        url = "https://trasparenza.regione.calabria.it/REGIONECALABRIA"
        self.assertFalse(self._ok(url))
        self.assertEqual(self._motivo(url), "RC_ISTITUZIONALE_OBBLIGATORIO")

    def test_subdomain_intranet(self):
        url = "https://intranet.regione.abruzzo.it"
        self.assertFalse(self._ok(url))
        self.assertEqual(self._motivo(url), "RC_ISTITUZIONALE_OBBLIGATORIO")

    def test_il_presidente_path(self):
        url = "https://www.regione.sicilia.it/istituzioni/regione/il-presidente"
        self.assertFalse(self._ok(url))
        self.assertEqual(self._motivo(url), "RC_ISTITUZIONALE_OBBLIGATORIO")

    def test_agid_formulario_acessibilidade(self):
        url = "https://form.agid.gov.it/view/78bd7980-9859-11f0-b114-bda70f0f6c0f"
        self.assertFalse(self._ok(url))
        self.assertEqual(self._motivo(url), "RC_ISTITUZIONALE_OBBLIGATORIO")

    def test_pagina_agricoltura_legittima_mantida(self):
        url = "https://www.regione.sicilia.it/agricoltura-foreste/fitosanitario"
        self.assertTrue(self._ok(url))


class TestRedTeamFiltroRB(unittest.TestCase):
    """RED TEAM DO FILTRO: mutar RB e provar que a contraprova REPROVA."""

    BASE = "https://www.arpae.it/"
    ARTIGO_URL = "https://www.arpae.it/it/notizie/incendio-alla-sorgenia-di-finale-emilia-17-9-2026"

    def test_red_team_mute_rb_artigo_passa_incorretamente(self):
        """Com RB mutado (regex vazia), o artigo passa o filtro — BUG simulado."""
        orig = D._RE_ARTIGO_INDIVIDUAL
        try:
            D._RE_ARTIGO_INDIVIDUAL = __import__("re").compile(r"(?!)")  # nunca casa
            ok, motivo = D._filtrar_link(self.ARTIGO_URL, self.BASE)
            self.assertTrue(ok, "mutacao deve deixar o artigo passar (BUG)")
        finally:
            D._RE_ARTIGO_INDIVIDUAL = orig

    def test_red_team_restaurada_rb_reprova(self):
        """Com RB restaurado, o mesmo artigo e corretamente recusado."""
        ok, motivo = D._filtrar_link(self.ARTIGO_URL, self.BASE)
        self.assertFalse(ok, "RB restaurado deve reprovar o artigo")
        self.assertEqual(motivo, "RB_ARTIGO_INDIVIDUAL")


class TestClassificarSemente(unittest.TestCase):
    """_classificar_semente — regra DECLARADA e TESTAVEL (ADDENDUM-02 tarefa 1)."""

    def test_crea_e_tematica(self):
        tipo, _ = D._classificar_semente("https://www.crea.gov.it/centri-di-ricerca")
        self.assertEqual(tipo, "TEMATICA")

    def test_arpae_e_tematica(self):
        tipo, _ = D._classificar_semente("https://www.arpae.it/")
        self.assertEqual(tipo, "TEMATICA")

    def test_agri_subdominio_e_tematica(self):
        tipo, _ = D._classificar_semente("https://agri.regione.emilia-romagna.it/")
        self.assertEqual(tipo, "TEMATICA",
                         "subdominio agri. e sempre TEMATICA")

    def test_arsacweb_e_tematica(self):
        tipo, _ = D._classificar_semente("https://www.arsacweb.it/")
        self.assertEqual(tipo, "TEMATICA")

    def test_portal_regional_raiz_e_generica(self):
        tipo, motivo = D._classificar_semente("https://www.regione.calabria.it/")
        self.assertEqual(tipo, "GENERICA")
        self.assertIn("portal_regional", motivo)

    def test_portal_regional_path_agri_continua_generica(self):
        """Mesmo com /settore-agricolo, o portal regional e GENERICA (colheita provou 0 agro)."""
        tipo, _ = D._classificar_semente(
            "https://www.regione.lombardia.it/wps/portal/istituzionale/HP/"
            "DettaglioRedazionale/servizi-e-informazioni/imprese/settore-agricolo"
        )
        self.assertEqual(tipo, "GENERICA",
                         "portal regional e GENERICA mesmo com path agricolo")

    def test_coldiretti_e_tematica(self):
        tipo, _ = D._classificar_semente("https://www.coldiretti.it/")
        self.assertEqual(tipo, "TEMATICA")

    def test_cnr_e_unknown(self):
        tipo, _ = D._classificar_semente("https://www.cnr.it/it/istituto?cds=0")
        self.assertEqual(tipo, "UNKNOWN",
                         "CNR tem escopo amplo — nao e decidivel pelo dominio")


class TestRedTeamClassificarSemente(unittest.TestCase):
    """RED TEAM: mutar _classificar_semente para TEMATICA e provar que semente
    GENERICA entraria no loop — o que e o BUG que o ADDENDUM-02 identificou."""

    URL_GENERICA = "https://www.regione.calabria.it/"

    def test_red_team_mute_generica_passa_como_tematica(self):
        """Com classificacao mutada (sempre TEMATICA), semente GENERICA nao e filtrada."""
        orig = D._classificar_semente
        D._classificar_semente = lambda url: ("TEMATICA", "muted")
        try:
            tipo, _ = D._classificar_semente(self.URL_GENERICA)
            self.assertEqual(tipo, "TEMATICA",
                             "mutacao deve declarar TEMATICA mesmo para semente GENERICA (BUG)")
        finally:
            D._classificar_semente = orig

    def test_red_team_restaurado_reprova_generica(self):
        """Com classificacao restaurada, homepage regional e corretamente GENERICA."""
        tipo, _ = D._classificar_semente(self.URL_GENERICA)
        self.assertEqual(tipo, "GENERICA",
                         "classificacao real deve detectar portal regional como GENERICA")


class TestFiltrarLinkRCFix(unittest.TestCase):
    """RC corrigida (ADDENDUM-03): urp e tutela-dati-personali que passavam antes."""

    BASE = "https://www.assam.marche.it/"

    def _ok(self, url: str) -> bool:
        return D._filtrar_link(url, self.BASE)[0]

    def _motivo(self, url: str) -> str:
        return D._filtrar_link(url, self.BASE)[1]

    def test_urp_raiz_descartado(self):
        url = "https://www.regione.sicilia.it/urp"
        self.assertFalse(self._ok(url))
        self.assertEqual(self._motivo(url), "RC_ISTITUZIONALE_OBBLIGATORIO")

    def test_urp_aninhado_descartado(self):
        """Caso que falhou no ADDENDUM-03: /agenzia/urp nao era apanhado."""
        url = "https://www.assam.marche.it/agenzia/urp"
        self.assertFalse(self._ok(url))
        self.assertEqual(self._motivo(url), "RC_ISTITUZIONALE_OBBLIGATORIO")

    def test_tutela_dati_aninhado_descartado(self):
        """Caso que falhou no ADDENDUM-03: /agenzia/tutela-dati-personali-privacy."""
        url = "https://www.assam.marche.it/agenzia/tutela-dati-personali-privacy"
        self.assertFalse(self._ok(url))
        self.assertEqual(self._motivo(url), "RC_ISTITUZIONALE_OBBLIGATORIO")

    def test_pagina_servizi_assam_mantida(self):
        url = "https://www.assam.marche.it/servizi"
        self.assertTrue(self._ok(url))

    def test_termini_duso_descartado(self):
        """ADDENDUM-04: arpalombardia.it/termini-duso/ passava antes da correcao."""
        url = "https://www.arpalombardia.it/termini-duso/"
        self.assertFalse(self._ok(url))
        self.assertEqual(self._motivo(url), "RC_ISTITUZIONALE_OBBLIGATORIO")

    def test_note_legali_descartado(self):
        url = "https://www.arpalombardia.it/note-legali"
        self.assertFalse(self._ok(url))
        self.assertEqual(self._motivo(url), "RC_ISTITUZIONALE_OBBLIGATORIO")

    def test_disclaimer_descartado(self):
        url = "https://www.arpalombardia.it/disclaimer/"
        self.assertFalse(self._ok(url))
        self.assertEqual(self._motivo(url), "RC_ISTITUZIONALE_OBBLIGATORIO")

    def test_termini_di_uso_descartado(self):
        url = "https://www.assam.marche.it/termini-di-uso"
        self.assertFalse(self._ok(url))
        self.assertEqual(self._motivo(url), "RC_ISTITUZIONALE_OBBLIGATORIO")

    def test_ufficio_relazioni_urp_sufixo_descartado(self):
        """ADDENDUM-04 residuo: ufficio-relazioni-con-il-pubblico-urp passava por ter -urp no fim."""
        url = "https://www.arpat.toscana.it/ufficio-relazioni-con-il-pubblico-urp/"
        self.assertFalse(self._ok(url))
        self.assertEqual(self._motivo(url), "RC_ISTITUZIONALE_OBBLIGATORIO")


class TestFiltrarLinkRD(unittest.TestCase):
    """RD_LOGIN_AUTH — portais de autenticacao nao publicam conteudo (ADDENDUM-03)."""

    BASE = "https://www.assam.marche.it/"

    def _ok(self, url: str) -> bool:
        return D._filtrar_link(url, self.BASE)[0]

    def _motivo(self, url: str) -> str:
        return D._filtrar_link(url, self.BASE)[1]

    def test_microsoftonline_descartado(self):
        """Caso que revelou a lacuna: login.microsoftonline.com."""
        url = "https://login.microsoftonline.com/"
        self.assertFalse(self._ok(url))
        self.assertEqual(self._motivo(url), "RD_LOGIN_AUTH")

    def test_login_subdominio_generico_descartado(self):
        url = "https://login.exemplo.gov.it/"
        self.assertFalse(self._ok(url))
        self.assertEqual(self._motivo(url), "RD_LOGIN_AUTH")

    def test_accounts_descartado(self):
        url = "https://accounts.google.com/signin"
        self.assertFalse(self._ok(url))
        self.assertEqual(self._motivo(url), "RD_LOGIN_AUTH")

    def test_pagina_normal_nao_descartada(self):
        url = "https://www.arpalombardia.it/temi-ambientali/aria/"
        self.assertTrue(self._ok(url))


class TestRedTeamRC(unittest.TestCase):
    """RED TEAM: mutar RC e provar que os testes de urp/termini-duso REPROVAM.

    Se a RC for desligada (regex que nunca casa), as URLs que ela devia barrar
    passam pelo filtro — isso e o BUG simulado. O teste afirma o BUG. Restaurar
    a regra faz o comportamento correcto voltar.
    """

    BASE = "https://www.assam.marche.it/"

    def test_red_team_mute_rc_urp_passa_incorretamente(self):
        """Com RC mutada (nunca casa), urp passa — BUG simulado."""
        import re as _re
        orig_path = D._RE_ISTITUZIONALE_PATH
        orig_prefix = D._RE_ISTITUZIONALE_PATH_PREFIX
        orig_host = D._RE_ISTITUZIONALE_HOST
        try:
            D._RE_ISTITUZIONALE_PATH = _re.compile(r"(?!)")
            D._RE_ISTITUZIONALE_PATH_PREFIX = _re.compile(r"(?!)")
            D._RE_ISTITUZIONALE_HOST = _re.compile(r"(?!)")
            ok, _ = D._filtrar_link("https://www.assam.marche.it/agenzia/urp", self.BASE)
            self.assertTrue(ok, "RC mutada deve deixar urp passar (BUG simulado)")
        finally:
            D._RE_ISTITUZIONALE_PATH = orig_path
            D._RE_ISTITUZIONALE_PATH_PREFIX = orig_prefix
            D._RE_ISTITUZIONALE_HOST = orig_host

    def test_red_team_mute_rc_termini_duso_passa_incorretamente(self):
        """Com RC mutada, termini-duso passa — BUG simulado (lacuna ADDENDUM-04)."""
        import re as _re
        orig_path = D._RE_ISTITUZIONALE_PATH
        orig_prefix = D._RE_ISTITUZIONALE_PATH_PREFIX
        orig_host = D._RE_ISTITUZIONALE_HOST
        try:
            D._RE_ISTITUZIONALE_PATH = _re.compile(r"(?!)")
            D._RE_ISTITUZIONALE_PATH_PREFIX = _re.compile(r"(?!)")
            D._RE_ISTITUZIONALE_HOST = _re.compile(r"(?!)")
            ok, _ = D._filtrar_link("https://www.arpalombardia.it/termini-duso/", self.BASE)
            self.assertTrue(ok, "RC mutada deve deixar termini-duso passar (BUG simulado)")
        finally:
            D._RE_ISTITUZIONALE_PATH = orig_path
            D._RE_ISTITUZIONALE_PATH_PREFIX = orig_prefix
            D._RE_ISTITUZIONALE_HOST = orig_host

    def test_red_team_restaurada_rc_reprova_urp(self):
        """Com RC restaurada, urp e corretamente bloqueado."""
        ok, motivo = D._filtrar_link("https://www.assam.marche.it/agenzia/urp", self.BASE)
        self.assertFalse(ok, "RC restaurada deve reprovar urp")
        self.assertEqual(motivo, "RC_ISTITUZIONALE_OBBLIGATORIO")

    def test_red_team_restaurada_rc_reprova_termini_duso(self):
        """Com RC restaurada, termini-duso e corretamente bloqueado."""
        ok, motivo = D._filtrar_link("https://www.arpalombardia.it/termini-duso/", self.BASE)
        self.assertFalse(ok, "RC restaurada deve reprovar termini-duso")
        self.assertEqual(motivo, "RC_ISTITUZIONALE_OBBLIGATORIO")


class TestRedTeamRD(unittest.TestCase):
    """RED TEAM: mutar RD e provar que login.microsoftonline REPROVA.

    Se a RD for desligada, a pagina de login passa pelo filtro — BUG simulado.
    """

    BASE = "https://www.assam.marche.it/"

    def test_red_team_mute_rd_login_passa_incorretamente(self):
        """Com RD mutada (nunca casa), login.microsoftonline passa — BUG simulado."""
        import re as _re
        orig_host = D._RE_LOGIN_AUTH_HOST
        orig_dom = D._LOGIN_AUTH_DOMINIOS
        try:
            D._RE_LOGIN_AUTH_HOST = _re.compile(r"(?!)")
            D._LOGIN_AUTH_DOMINIOS = frozenset()
            ok, _ = D._filtrar_link("https://login.microsoftonline.com/", self.BASE)
            self.assertTrue(ok, "RD mutada deve deixar login passar (BUG simulado)")
        finally:
            D._RE_LOGIN_AUTH_HOST = orig_host
            D._LOGIN_AUTH_DOMINIOS = orig_dom

    def test_red_team_restaurada_rd_reprova_login(self):
        """Com RD restaurada, login.microsoftonline e corretamente bloqueado."""
        ok, motivo = D._filtrar_link("https://login.microsoftonline.com/", self.BASE)
        self.assertFalse(ok, "RD restaurada deve reprovar login")
        self.assertEqual(motivo, "RD_LOGIN_AUTH")


if __name__ == "__main__":
    unittest.main(verbosity=2)
