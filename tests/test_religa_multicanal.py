# -*- coding: utf-8 -*-
"""RELIGA-MULTICANAL (D155, 29/09/2026) — as partes NOVAS, medidas.

Zero rede. Cada teste aqui guarda uma frase que a missao paga caro se for quebrada; o nome do teste diz
qual. Os que guardam uma ARMADILHA JA PAGA levam o prefixo `test_armadilha_`.
"""
from __future__ import annotations

import json
import os
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
for p in (RAIZ, RAIZ / "coleta", RAIZ / "ferramentas" / "big_collection"):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

import rotas_multicanal as RM                                      # noqa: E402
import fontes_multicanal as FM                                     # noqa: E402

CANAL = "UCrCabYjtyqdzu1zXo95o7Jw"
OUTRO = "UCEgJbey3UogPJPmdlBEAjKQ"


def leitor(html="", status=200, erro=None):
    """Um transporte de mentira que conta o que lhe pediram. A rota NUNCA abre ligacao propria."""
    chamadas = []

    def buscar(url, aceitar=None):
        chamadas.append(url)
        if erro:
            return {"STATUS": None, "BYTES": None, "ERRO": erro, "QUEM_DISSE_NAO": "PLATAFORMA"}
        return {"STATUS": status, "BYTES": html.encode("utf-8"), "ERRO": None, "CONTENT_TYPE": "text/html"}
    buscar.chamadas = chamadas
    return buscar


class _Temp:
    """Pasta temporaria + ambiente restaurado. O que a suite escreve, a suite apaga."""

    def __init__(self):
        self.pasta = Path(tempfile.mkdtemp(prefix="religa-"))
        self._env = dict(os.environ)

    def livro(self):
        f = self.pasta / "LIVRO.ndjson"
        f.write_text("", encoding="utf-8")
        os.environ["SINTONIA_CORTESIA_LIVRO"] = str(f)
        os.environ.pop("SINTONIA_TETO_24H", None)
        return f

    def sem_livro(self):
        os.environ.pop("SINTONIA_CORTESIA_LIVRO", None)
        os.environ.pop("SINTONIA_TETO_24H", None)

    def fechar(self):
        os.environ.clear()
        os.environ.update(self._env)
        shutil.rmtree(self.pasta, ignore_errors=True)


def pagina_yt(canal, ids):
    return ('<link rel="canonical" href="https://www.youtube.com/channel/%s">'
            '{"channelId":"%s",' % (canal, canal)) + "".join('"videoId":"%s",' % i for i in ids) + "}"


# ══════════════════════════════════════════════════════════════════════════════
# YOUTUBE — a rota publica do canal
# ══════════════════════════════════════════════════════════════════════════════
def test_youtube_le_os_videos_da_pagina_publica_do_canal():
    b = leitor(pagina_yt(CANAL, ["aaaaaaaaaaa", "bbbbbbbbbbb"]))
    r = RM.youtube_videos_do_canal(channel_id=CANAL, buscar=b)
    assert [a["URL"] for a in r["ALVOS"]] == ["https://www.youtube.com/watch?v=aaaaaaaaaaa",
                                              "https://www.youtube.com/watch?v=bbbbbbbbbbb"]
    assert b.chamadas == ["https://www.youtube.com/channel/%s/videos" % CANAL]


def test_armadilha_youtube_nunca_pede_o_feed_que_o_robots_barra():
    """`/feeds/videos.xml` esta ROUTE_NOT_ALLOWED por robots. O molde nao o alcanca nem por engano."""
    b = leitor(pagina_yt(CANAL, ["aaaaaaaaaaa"]))
    RM.youtube_videos_do_canal(channel_id=CANAL, buscar=b)
    for u in b.chamadas:
        assert "/feeds/videos.xml" not in u


def test_armadilha_youtube_identidade_divergente_falha_fechado():
    """⚠️ A fechadura que nunca tranca: aceitar alvos de um canal e carimba-los com o SOURCE_ID de outro
    e PIOR do que nao colher. Zero alvos, nao «os alvos que vieram»."""
    b = leitor(pagina_yt(OUTRO, ["aaaaaaaaaaa", "bbbbbbbbbbb"]))
    r = RM.youtube_videos_do_canal(channel_id=CANAL, buscar=b)
    assert "ALVOS" not in r
    assert "IDENTITY_MISMATCH" in r["ERRO"]


def test_armadilha_youtube_pagina_sem_canonico_nao_passa_por_omissao():
    """⚠️ Mutante M03: `bate = ... or canonical is None` — uma pagina SEM `<link rel=canonical>` passava a
    aprovar qualquer canal. A ausencia de uma prova nao e prova: sem canonico E sem o canal declarado, a
    identidade NAO foi conferida, e falha fechado."""
    sem_canonico = '{"channelId":"%s","videoId":"aaaaaaaaaaa"}' % OUTRO
    r = RM.youtube_videos_do_canal(channel_id=CANAL, buscar=leitor(sem_canonico))
    assert "ALVOS" not in r and "IDENTITY_MISMATCH" in r["ERRO"]
    # E nem sequer uma pagina vazia de identidade abre a porta.
    r2 = RM.youtube_videos_do_canal(channel_id=CANAL, buscar=leitor('{"videoId":"aaaaaaaaaaa"}'))
    assert "ALVOS" not in r2 and "IDENTITY_MISMATCH" in r2["ERRO"]


def test_youtube_channel_id_malformado_e_recusado_antes_da_rede():
    b = leitor(pagina_yt(CANAL, ["aaaaaaaaaaa"]))
    for mau in (None, "", "agronotizie", "UC-curto", 7):
        r = RM.youtube_videos_do_canal(channel_id=mau, buscar=b)
        assert "CHANNEL_ID_INVALIDO" in r["ERRO"]
    assert b.chamadas == [], "tocou a rede com contrato invalido"


def test_youtube_200_sem_videoid_e_erro_e_nao_lista_vazia_silenciosa():
    r = RM.youtube_videos_do_canal(channel_id=CANAL, buscar=leitor(pagina_yt(CANAL, [])))
    assert "ALVOS" not in r and "nao trouxe videoId" in r["ERRO"]


def test_youtube_status_diferente_de_200_falha_fechado():
    r = RM.youtube_videos_do_canal(channel_id=CANAL, buscar=leitor("", status=404))
    assert "ALVOS" not in r and "nao respondeu 200" in r["ERRO"]


def test_youtube_max_alvos_corta_e_duplicados_nao_contam_duas_vezes():
    b = leitor(pagina_yt(CANAL, ["aaaaaaaaaaa", "aaaaaaaaaaa", "bbbbbbbbbbb", "ccccccccccc"]))
    r = RM.youtube_videos_do_canal(channel_id=CANAL, buscar=b, max_alvos=2)
    assert len(r["ALVOS"]) == 2 and len({a["URL"] for a in r["ALVOS"]}) == 2


def test_youtube_sem_transporte_recusa_e_nao_inventa_um():
    r = RM.youtube_videos_do_canal(channel_id=CANAL, buscar=None)
    assert "SEM_TRANSPORTE" in r["ERRO"]


def _pagina_video(**kw):
    d = {"videoDetails": {"videoId": "x", "title": kw.get("title", "Peronospora della vite"),
                          "lengthSeconds": "60"},
         "shortDescription": kw.get("desc", "Difesa del vigneto, fungicidi e peronospora."),
         "author": "Terra e Vita", "publishDate": "2026-09-01", "keywords": ["vite", "peronospora"]}
    return json.dumps(d, separators=kw.get("sep", (",", ":")))


def test_youtube_metadados_saem_da_pagina_publica_do_video():
    """O oembed so traz titulo e autor; com isso a Admission nao consegue julgar o universo (medido no
    canario: «so uma palavra de T7 aparece»). A pagina /watch traz a descricao, e o robots aprova-a."""
    b = leitor(_pagina_video())
    r = RM.youtube_metadados_do_video(url="https://www.youtube.com/watch?v=x", buscar=b)
    assert r["REGISTO"]["DESCRIPTION"].startswith("Difesa del vigneto")
    assert r["REGISTO"]["PUBLISHED_AT"] == "2026-09-01"
    assert r["MEDIA_TYPE"] == "application/json", "guarda-se o REGISTO, nao a pagina"
    assert b.chamadas == ["https://www.youtube.com/watch?v=x"]


def test_youtube_metadados_leem_json_minificado_e_formatado():
    """O YouTube serve minificado. Um molde que so casasse com essa forma partiria em silencio no dia em
    que a pagina viesse formatada — e o sintoma soaria a problema da fonte."""
    for sep in ((",", ":"), (", ", ": ")):
        r = RM.youtube_metadados_do_video(url="https://www.youtube.com/watch?v=x",
                                          buscar=leitor(_pagina_video(sep=sep)))
        assert r["REGISTO"]["TITLE"] == "Peronospora della vite"


def test_youtube_metadados_nao_cortam_aspas_dentro_do_texto():
    """Cortar no primeiro `"` perderia metade de qualquer descricao que cite alguem."""
    r = RM.youtube_metadados_do_video(url="https://www.youtube.com/watch?v=x",
                                      buscar=leitor(_pagina_video(title='a "difesa" integrata')))
    assert r["REGISTO"]["TITLE"] == 'a "difesa" integrata'


def test_youtube_video_sem_titulo_nem_descricao_e_erro_com_nome():
    r = RM.youtube_metadados_do_video(url="https://www.youtube.com/watch?v=x", buscar=leitor("{}"))
    assert "REGISTO" not in r and "nao declarou titulo nem descricao" in r["ERRO"]


# ══════════════════════════════════════════════════════════════════════════════
# INSTAGRAM — Reel por URL directa (D22) e listagem /embed/ (provada 23/09)
# ══════════════════════════════════════════════════════════════════════════════
def test_instagram_lista_reels_pela_pagina_embed_da_conta():
    b = leitor('<a href="/reel/ABC12/">x</a><a href="/reel/DEF34/">y</a>')
    r = RM.instagram_reels_da_conta(handle="bayer_italia", buscar=b)
    assert [a["NATIVE_ID"] for a in r["ALVOS"]] == ["ABC12", "DEF34"]
    assert b.chamadas == ["https://www.instagram.com/bayer_italia/embed/"]
    assert r["ROTA"] == "embed_publico"


def test_armadilha_instagram_zero_reels_e_zero_legitimo_e_nao_erro():
    """Uma conta sem Reel na pagina de embed devolve LISTA VAZIA, nao falha. Transformar zero em erro
    faria o canario parecer partido onde a fonte so nao tem video."""
    r = RM.instagram_reels_da_conta(handle="conta_sem_reel", buscar=leitor("<html>nada</html>"))
    assert r["ALVOS"] == [] and "ERRO" not in r


def test_instagram_so_aceita_url_de_reel_a_conta_nao_e_alvo_directo():
    """D22 abre o REEL por URL directa; a CONTA continua POLICY_BLOCK (D19)."""
    r = RM.instagram_reel(url="https://www.instagram.com/syngentaitalia/", buscar=leitor("x"))
    assert "URL_NAO_E_REEL" in r["ERRO"]


def test_instagram_reel_por_url_directa_colhe():
    b = leitor("<html>reel</html>")
    r = RM.instagram_reel(url="https://www.instagram.com/reel/C-FanW_CYMz/", buscar=b)
    assert r["NATIVE_ID"] == "C-FanW_CYMz" and r["BYTES"] == b"<html>reel</html>"


# ══════════════════════════════════════════════════════════════════════════════
# LINKEDIN — a distincao que ja enganou uma vez
# ══════════════════════════════════════════════════════════════════════════════
def test_armadilha_linkedin_video_descoberto_nunca_conta_como_video_coletado():
    """⚠️ FETCH_VIDEO_BYTES = PROVED quer dizer «o URL do MP4 e DESCOBRIVEL», e NAO «os bytes foram
    baixados». Esta leitura ja enganou o relatorio uma vez."""
    import onda_linha as OL
    a = {"URL_DO_POST": "https://www.linkedin.com/posts/x", "NATIVE_ID": "7123456789012345678",
         "URL_MP4_DESCOBERTA": "https://dms.licdn.com/x.mp4", "VIDEO_BYTES_ACQUIRED": False}
    c = OL.colher_alvo("LINKEDIN", a, leitor("x"))
    guardado = json.loads(c["BYTES"].decode("utf-8"))
    assert guardado["VIDEO_BYTES_ACQUIRED"] is False
    assert guardado["URL_MP4_DESCOBERTA"].endswith(".mp4")
    assert "ROUTE_NOT_ALLOWED" in guardado["FETCH_POST"]
    assert c["PEDIDOS"] == 0, "FETCH_POST esta ROUTE_NOT_ALLOWED: nao se pede o post individual"


def test_linkedin_le_o_mp4_do_data_sources_que_a_pagina_serviu():
    """O endereco do MP4 vem do `data-sources` que a propria pagina publicou — nao se constroi."""
    c = {"VIDEO_RENDICOES": [{"URL": "https://dms.licdn.com/a.mp4", "largura": 720}]}
    assert RM._mp4_do_cartao(c) == "https://dms.licdn.com/a.mp4"
    assert RM._mp4_do_cartao({"VIDEO_RENDICOES": []}) is None


def test_linkedin_cartao_sem_identidade_do_post_nao_vira_item_vazio():
    """Sem endereco NEM activity id nao ha post a que atar a observacao."""
    import onda_linha as OL
    c = OL.colher_alvo("LINKEDIN", {"URL_DO_POST": None, "NATIVE_ID": None}, leitor("x"))
    assert "CARTAO_SEM_IDENTIDADE_DO_POST" in c["ERRO"]


# ══════════════════════════════════════════════════════════════════════════════
# A ALIMENTACAO — opcao (a)
# ══════════════════════════════════════════════════════════════════════════════
def escrever_lista(pasta):
    f = Path(pasta) / "curator.json"
    f.write_text(json.dumps({
        "YOUTUBE": [{"SOURCE_ID": "IT-T8-004", "URL": "https://www.youtube.com/channel/%s" % CANAL,
                     "NATIVE_ID": CANAL, "NOME": "x"},
                    {"SOURCE_ID": "IT-T9-999", "URL": "https://www.youtube.com/@sem_id", "NATIVE_ID": None}],
        "YOUTUBE_FORA": [{"SOURCE_ID": "NAO_EXISTE", "URL": "https://www.youtube.com/@adamaitalia7114",
                          "NATIVE_ID": "UCzzzzzzzzzzzzzzzzzzzzzz"}],
        "INSTAGRAM": [{"SOURCE_ID": "COMPETITOR-PUBLIC-COMM/CONTAS-V1#BAYER|IT|INSTAGRAM",
                       "URL": "https://www.instagram.com/bayer_italia", "HANDLE": "bayer_italia",
                       "REELS_JA_NO_REPOSITORIO": ["https://www.instagram.com/reel/DcNkh7LCW4u/"]}],
        "LINKEDIN": [{"SOURCE_ID": "IT-T9-026", "URL": "https://www.linkedin.com/company/x/",
                      "NATIVE_ID": "x"}],
        "WEB": [{"SOURCE_ID": "IT-T5-185", "URL": "https://sostenibilita.enea.it/"}],
        "BUSCA": [{"CONSULTA_ID": "Q0001", "CONSULTA": "bollettino vite", "UNIVERSO": "T3"}],
        "CIENCIA": [{"SOURCE_ID": "EU-T5-001", "CONSULTA_OPENALEX": "(grapevine)"}],
        "DIVERGENCIAS_FORA_DO_CANARIO": [{"ID": "IT-T9-021", "O_QUE": "didacta"}],
    }, ensure_ascii=False), encoding="utf-8")
    return f


def test_cada_linha_recebe_as_suas_candidatas_com_o_campo_linha():
    t = _Temp()
    try:
        c = FM.candidatas_por_linha(escrever_lista(t.pasta))
    finally:
        t.fechar()
    assert FM.resumo(c) == {"BUSCA": 1, "CIENCIA": 1, "INSTAGRAM": 1, "LINKEDIN": 1, "SITES": 1, "YOUTUBE": 1}
    for nome, itens in c.items():
        for x in itens:
            assert x["LINHA"] == nome, "a candidata tem de saber de que linha e"


def test_armadilha_as_listas_fora_do_canario_nao_alimentam_linha_nenhuma():
    """⚠️ `*_FORA` e `DIVERGENCIAS_*` sao o que o Curator EXCLUIU, com motivo escrito. Le-las por engano
    poria no ar uma fonte recusada — o ADAMA sem identidade provada, a Didacta que nao e concorrente."""
    t = _Temp()
    try:
        c = FM.candidatas_por_linha(escrever_lista(t.pasta))
    finally:
        t.fechar()
    todos = json.dumps(c, ensure_ascii=False)
    assert "adamaitalia7114" not in todos
    assert "IT-T9-021" not in todos and "didacta" not in todos


def test_armadilha_source_id_ausente_e_declarado_e_nunca_inventado():
    """⚠️ As contas de dataset nao estao no livro do Curator. Fabricar um SOURCE_ID faria a Sala declarar
    uma procedencia que nao existe, e ninguem depois distinguiria a inventada da real."""
    t = _Temp()
    try:
        c = FM.candidatas_por_linha(escrever_lista(t.pasta))
    finally:
        t.fechar()
    ig = c["INSTAGRAM"][0]
    assert ig["SOURCE_STATUS"] == "NAO_REGISTRADA_PENDENTE_PORTA_CANONICA"
    assert ig["SOURCE_ID"] == "COMPETITOR-PUBLIC-COMM/CONTAS-V1#BAYER|IT|INSTAGRAM"
    assert c["YOUTUBE"][0]["SOURCE_STATUS"] == "REGISTRADA"


def test_youtube_sem_channel_id_nao_entra_porque_a_rota_nao_se_adivinha():
    t = _Temp()
    try:
        c = FM.candidatas_por_linha(escrever_lista(t.pasta))
    finally:
        t.fechar()
    assert [x["SOURCE_ID"] for x in c["YOUTUBE"]] == ["IT-T8-004"]


def test_os_reels_provados_do_curator_viajam_com_a_candidata():
    t = _Temp()
    try:
        c = FM.candidatas_por_linha(escrever_lista(t.pasta))
    finally:
        t.fechar()
    assert c["INSTAGRAM"][0]["ALVO"]["REELS_CONHECIDOS"] == ["https://www.instagram.com/reel/DcNkh7LCW4u/"]


def test_as_pessoas_do_linkedin_so_entram_se_pedidas():
    t = _Temp()
    f = t.pasta / "c.json"
    f.write_text(json.dumps({"LINKEDIN": [{"SOURCE_ID": "A", "URL": "https://www.linkedin.com/company/a/"}],
                             "LINKEDIN_PESSOAS_OPCIONAIS": [
                                 {"SOURCE_ID": "CAND-1177", "URL": "https://www.linkedin.com/in/z"}]}),
                encoding="utf-8")
    try:
        assert len(FM.candidatas_por_linha(f)["LINKEDIN"]) == 1
        assert len(FM.candidatas_por_linha(f, com_pessoas=True)["LINKEDIN"]) == 2
    finally:
        t.fechar()


# ══════════════════════════════════════════════════════════════════════════════
# O ORQUESTRADOR — um coletor, um contador, uma entrada na Sala
# ══════════════════════════════════════════════════════════════════════════════
def test_as_linhas_do_ciclo_cobrem_os_seis_canais_da_campanha():
    import coleta_continua as CC
    nomes = [l["LINHA"] for l in CC.LINHAS]
    for esperado in ("SITES", "BUSCA", "CIENCIA", "YOUTUBE", "INSTAGRAM", "LINKEDIN"):
        assert esperado in nomes
    assert len(nomes) == len(set(nomes)), "linha repetida: o ciclo passaria duas vezes pela mesma"


def test_armadilha_pesquisadores_continua_desligada_e_com_o_motivo_escrito():
    """A missao manda REGISTRAR, nao ligar: o transporte real usa um contador PROPRIO de 5/24 h, fora do
    livro da cortesia. Reapontar sem reconciliar poria DOIS contadores na mesma janela de 24 h."""
    import coleta_continua as CC
    p = next(l for l in CC.LINHAS if l["LINHA"] == "PESQUISADORES")
    assert p["TRANSPORTE"] == "coleta/seguir.py"
    assert not (RAIZ / p["TRANSPORTE"]).exists()
    assert CC.medir_ligacao(p)["LIGADA"] is False


def test_so_as_linhas_nao_web_usam_o_executor_proprio():
    """A SITES nao pode regredir: ela continua a correr pela onda web, com a coorte congelada."""
    import coleta_continua as CC
    por_linha = {l["LINHA"] for l in CC.LINHAS if l.get("EXECUTOR") == "LINHA"}
    assert por_linha == {"YOUTUBE", "INSTAGRAM", "LINKEDIN", "BUSCA", "CIENCIA"}
    assert "SITES" not in por_linha


def test_a_alimentacao_nao_esmaga_a_coorte_congelada_da_sites():
    """A SITES e alimentada pelo PLANO (coorte congelada). A lista do Curator nao a substitui."""
    import coleta_continua as CC
    t = _Temp()
    try:
        lista = escrever_lista(t.pasta)
        cands = {l["LINHA"]: [] for l in CC.LINHAS}
        cands["SITES"] = [{"SOURCE_ID": "DA-COORTE", "LINHA": "SITES"}]
        extra = FM.candidatas_por_linha(lista)
        for nome, l in extra.items():
            if nome == "SITES" and cands.get("SITES"):
                continue
            if nome in cands:
                cands[nome] = l
        assert [x["SOURCE_ID"] for x in cands["SITES"]] == ["DA-COORTE"]
        assert len(cands["YOUTUBE"]) == 1
    finally:
        t.fechar()


# ══════════════════════════════════════════════════════════════════════════════
# A PORTA UNICA DO CONTADOR
# ══════════════════════════════════════════════════════════════════════════════
def test_a_porta_reserva_antes_e_regista_a_resposta_depois():
    import reserva_24h as R24
    t = _Temp()
    try:
        f = t.livro()
        r, res = R24.pedir("https://exemplo.it/a", lambda: (200, {}, b"ok"), run_id="R", linha="TESTE")
        assert r["ESTADO"] == "RESERVADO" and res[2] == b"ok"
        ev = [json.loads(l) for l in f.read_text(encoding="utf-8").splitlines() if l.strip()]
        assert [e["TIPO"] for e in ev] == ["RESERVA", "RESPOSTA"],             "a reserva vem ANTES e a resposta DEPOIS; a ordem e a prova"
    finally:
        t.fechar()


def test_armadilha_sem_livro_nao_se_pede_a_linha_falha_fechada():
    """Um contador ausente nao e um contador vazio: sem livro partilhado NAO se pede."""
    import reserva_24h as R24
    t = _Temp()
    try:
        t.sem_livro()
        tocou = []

        def fazer():
            tocou.append(1)
            return 200, {}, b""
        r, res = R24.pedir("https://exemplo.it/a", fazer, run_id="R", linha="TESTE")
        assert res is None and r["ESTADO"] == "FAIL" and tocou == []
    finally:
        t.fechar()


def test_a_falha_do_pedido_tambem_vai_ao_livro():
    """Um pedido reservado que nao teve resposta fecha o «um de cada vez» na mesma — senao o dominio
    ficava preso ate ao LEASE."""
    import reserva_24h as R24
    t = _Temp()
    try:
        f = t.livro()

        def rebenta():
            raise TimeoutError("timed out")
        try:
            R24.pedir("https://exemplo.it/a", rebenta, run_id="R", linha="TESTE")
            raise AssertionError("a excecao tem de SUBIR: quem pediu precisa de saber que falhou")
        except TimeoutError:
            pass
        ev = [json.loads(l) for l in f.read_text(encoding="utf-8").splitlines() if l.strip()]
        resp = [e for e in ev if e["TIPO"] == "RESPOSTA"]
        assert resp and "TIMEOUT" in resp[0]["MARCAS"]
    finally:
        t.fechar()


def test_armadilha_duas_rotas_no_mesmo_dominio_nao_partilham_o_orcamento():
    """⚠️ Custom Search (100/dia publicado) e YouTube Data (10.000) vivem ambas em googleapis.com.
    Contadas juntas, 10.000 pedidos de busca cabiam num orcamento que o Google cobra depois das 100."""
    import cortesia_adaptativa as CA
    cse = CA.dominio_do_pedido("www.googleapis.com", "https://www.googleapis.com/customsearch/v1?q=x")
    yt = CA.dominio_do_pedido("www.googleapis.com", "https://www.googleapis.com/youtube/v3/channels?id=x")
    busca_yt = CA.dominio_do_pedido("www.googleapis.com", "https://www.googleapis.com/youtube/v3/search?q=x")
    assert cse == "googleapis.com/customsearch"
    assert yt == "googleapis.com/youtube"
    assert busca_yt == "googleapis.com/youtube/search"
    assert len({cse, yt, busca_yt}) == 3
    # Sem URL paga-se o dominio inteiro, que e sempre o mais apertado.
    assert CA.dominio_do_pedido("www.googleapis.com") == "googleapis.com"


def test_a_porta_e_o_abridor_global_nao_reservam_duas_vezes_o_mesmo_pedido():
    """⚠️ Dois caminhos para o mesmo livro: `reserva_24h.pedir` e o abridor do `scrap_http` (via
    `teto_da_onda`). Sem esta trava o MESMO pedido gastava DOIS lugares do orcamento."""
    import reserva_24h as R24
    import teto_da_onda as T
    t = _Temp()
    try:
        t.livro()
        visto = {}

        def fazer():
            visto["dentro"] = R24.dentro_da_porta("exemplo.it", "https://exemplo.it/a")
            visto["teto"] = T.reservar("exemplo.it", url="https://exemplo.it/a", quem="scrap_http")
            return 200, {}, b"ok"
        R24.pedir("https://exemplo.it/a", fazer, run_id="R", linha="TESTE")
        assert visto["dentro"] is True
        assert visto["teto"] == "exemplo.it", "o teto devolveu o orcamento sem reservar de novo"
        assert R24.dentro_da_porta("exemplo.it", "https://exemplo.it/a") is False, "a porta ficou aberta"
    finally:
        t.fechar()


def test_armadilha_a_porta_nao_tapa_um_salto_para_outro_dominio():
    """⚠️ Mutante M30: `dentro_da_porta` a devolver True para QUALQUER dominio. Um redireccionamento para
    outro dominio passaria a nao reservar nada — o orcamento do segundo dominio nunca seria gasto, e um
    salto tornava-se uma porta lateral silenciosa.

        A PORTA COBRE O PEDIDO QUE ELA RESERVOU, E SO ESSE."""
    import reserva_24h as R24
    t = _Temp()
    try:
        t.livro()
        visto = {}

        def fazer():
            visto["mesmo"] = R24.dentro_da_porta("exemplo.it", "https://exemplo.it/a")
            visto["outro"] = R24.dentro_da_porta("outro-sitio.it", "https://outro-sitio.it/b")
            return 200, {}, b"ok"
        R24.pedir("https://exemplo.it/a", fazer, run_id="R", linha="TESTE")
        assert visto["mesmo"] is True
        assert visto["outro"] is False, "um salto para outro dominio ficou coberto sem ter reservado"
    finally:
        t.fechar()


class _Resposta:
    status = 200
    headers = {}

    def read(self):
        return b'{"ok": 1}'

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False


def test_ciencia_reserva_no_unico_ponto_onde_toca_a_rede():
    """A lacuna medida: `corpus_pesquisador._get` chegava a rede por urlopen CRU, sem reservar."""
    import corpus_pesquisador as CP
    t = _Temp()
    real = CP.urllib.request.urlopen
    try:
        f = t.livro()
        CP.urllib.request.urlopen = lambda *a, **k: _Resposta()
        d, erro = CP._get("https://api.openalex.org/works?x=1")
        assert erro is None and d == {"ok": 1}
        ev = [json.loads(l) for l in f.read_text(encoding="utf-8").splitlines() if l.strip()]
        assert [e["TIPO"] for e in ev] == ["RESERVA", "RESPOSTA"]
        assert ev[0]["DOMINIO"] == "openalex.org"
    finally:
        CP.urllib.request.urlopen = real
        t.fechar()


def test_ciencia_sem_reserva_nao_pede_e_diz_que_foi_o_contador():
    """«CONTADOR_24H» e a nossa politica, nao «a fonte nao respondeu». Trocar os dois nomes faz um
    orcamento esgotado parecer uma fonte morta."""
    import corpus_pesquisador as CP
    t = _Temp()
    real = CP.urllib.request.urlopen
    try:
        t.sem_livro()
        tocou = []
        CP.urllib.request.urlopen = lambda *a, **k: tocou.append(1)
        d, erro = CP._get("https://api.openalex.org/works")
        assert d is None and erro.startswith("CONTADOR_24H") and tocou == []
    finally:
        CP.urllib.request.urlopen = real
        t.fechar()


# ══════════════════════════════════════════════════════════════════════════════
# O RUN_ID — a PROVA-TETO tem de conseguir le-lo
# ══════════════════════════════════════════════════════════════════════════════
def test_o_run_id_da_linha_e_legivel_pela_prova_teto():
    """Um formato proprio ficaria INVISIVEL para a prova independente — e uma corrida que a prova nao ve
    e uma corrida que ninguem confere."""
    import onda_linha as OL
    sys.path.insert(0, str(RAIZ / "provas"))
    import prova_teto_dominio as PT
    for sid in ("IT-T8-004", "IT-T9-026", None):
        r = OL.run_id(sid)
        assert PT.RE_RUN_ID.fullmatch(r), r


# ══════════════════════════════════════════════════════════════════════════════
# As funcoes soltas acima correm pelo unittest: uma classe que as recolhe pelo nome.
# A bateria da casa (`_bateria_por_nome.py`) le `unittest`, nao `pytest`.
# ══════════════════════════════════════════════════════════════════════════════
def _montar():
    corpo = {}
    for nome, fn in sorted(globals().items()):
        if nome.startswith("test_") and callable(fn):
            corpo[nome] = (lambda f: lambda self: f())(fn)
            corpo[nome].__doc__ = fn.__doc__
    return type("ReligaMulticanal", (unittest.TestCase,), corpo)


ReligaMulticanal = _montar()

if __name__ == "__main__":
    unittest.main()
