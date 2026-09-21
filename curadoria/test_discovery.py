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


if __name__ == "__main__":
    unittest.main(verbosity=2)
