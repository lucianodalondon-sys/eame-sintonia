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
    # e com legenda, o pedido e SO o da legenda — nunca o do post
    a2 = dict(a, CAPTION_URL="https://dms.licdn.com/x.srt")
    srt = "1\n00:00:01,000 --> 00:00:02,000\nciao a tutti\n"
    c2 = OL.colher_alvo("LINKEDIN", a2, leitor(srt))
    assert c2["PEDIDOS"] == 1, \
        "1 pedido = SO a legenda; %s quer dizer que o post individual tambem foi pedido" % c2["PEDIDOS"]
    assert json.loads(c2["BYTES"].decode("utf-8"))["TEXTO_ORIGEM"] == "LEGENDA_NATIVA_LINKEDIN"


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
        # IT-T3-045 (AMAP Marche) e nao a IT-T5-185: a ENEA esta SUSPENSA PELO DONO (D130) e
        # entrou na lista WEB por erro do Curator, corrigido em 2026-09-30. Um SOURCE_ID suspenso
        # num molde de teste nao coleta nada, mas e semente: alguem copia a linha para uma lista
        # a valer. O molde nao guarda fonte que o dono mandou parar.
        "WEB": [{"SOURCE_ID": "IT-T3-045", "URL": "https://www.amap.marche.it/"}],
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
    # `None` saiu daqui de proposito: depois da D156 um SOURCE_ID sem territorio LEVANTA em vez de
    # cair num T9 inventado — ver `test_armadilha_run_id_nao_inventa_territorio`.
    for sid in ("IT-T8-004", "IT-T9-026"):
        r = OL.run_id(sid)
        assert PT.RE_RUN_ID.fullmatch(r), r


# ══════════════════════════════════════════════════════════════════════════════
# D156 · O UNIVERSO VEM DO PEDIDO — e o teste falha se ele vier da fonte
# ══════════════════════════════════════════════════════════════════════════════
def test_armadilha_o_universo_nunca_vem_do_source_id_nem_do_territorio():
    """⚠️ A LEI QUE EU JA VIOLEI UMA VEZ NESTA MISSAO (`admissao/admissao.py`, pergunta do universo):

        «o universo vem do PEDIDO — nunca da fonte, do territorio dela, da plataforma nem do conteudo»

    Eu derivava o universo do TERRITORIO do Curator, e com isso um item recebia a regua de T8 sem que
    ninguem tivesse perguntado nada sobre T8. Este teste falha se isso voltar."""
    t = _Temp()
    try:
        f = Path(t.pasta) / "c.json"
        f.write_text(json.dumps({"YOUTUBE": [
            {"SOURCE_ID": "IT-T8-004", "URL": "https://www.youtube.com/channel/%s" % CANAL,
             "NATIVE_ID": CANAL, "TERRITORIO": "T8"}]}), encoding="utf-8")
        c = FM.candidatas_por_linha(f)["YOUTUBE"][0]
        assert c["TERRITORIO"] == "T8", "o territorio e um facto do Curator e viaja"
        assert c["UNIVERSOS_DO_PEDIDO"] == [], \
            "o universo veio da fonte: nem o SOURCE_ID nem o TERRITORIO podem declara-lo"
    finally:
        t.fechar()


def test_o_universo_declarado_no_pedido_viaja_com_a_origem():
    t = _Temp()
    try:
        f = Path(t.pasta) / "c.json"
        f.write_text(json.dumps({"YOUTUBE": [
            {"SOURCE_ID": "IT-T8-004", "URL": "https://www.youtube.com/channel/%s" % CANAL,
             "NATIVE_ID": CANAL, "TERRITORIO": "T8",
             "UNIVERSOS_DO_PEDIDO": [{"UNIVERSO": "T8", "ORIGEM": "PEDIDO-X do coordenador, 29/09"},
                                     {"UNIVERSO": "T3", "ORIGEM": "PEDIDO-X do coordenador, 29/09"},
                                     {"UNIVERSO": "T5"}]}]}), encoding="utf-8")
        u = FM.candidatas_por_linha(f)["YOUTUBE"][0]["UNIVERSOS_DO_PEDIDO"]
        assert [x["UNIVERSO"] for x in u] == ["T8", "T3"], "o mesmo item leva DUAS perguntas"
        assert all(x["ORIGEM"] for x in u)
        assert "T5" not in [x["UNIVERSO"] for x in u], "declaracao sem origem nao e rastreavel: nao entra"
    finally:
        t.fechar()


def test_sem_universo_declarado_a_porta_para_e_diz_porque():
    import onda_linha as OL
    d = OL.admitir_pedidos(b"{}", "application/json", "u", "IT-T8-004", [], "sha", "2026-09-29T00:00:00Z", "R")
    assert len(d) == 1 and d[0]["RESULTADO"] == "UNIVERSO_NAO_DECLARADO"
    assert d[0]["READY"] is None
    assert "nao escolhe um" in d[0]["MOTIVO"]


def test_a_regua_t8_e_candidata_e_carimba_cada_decisao():
    """A regua T8 tem recall 10/20 e 3 falsos SIM em 28 negativos. Sem carimbo, daqui a um mes um SIM
    de T8 le-se como um SIM validado."""
    sys.path.insert(0, str(RAIZ / "admissao"))
    import admissao as adm
    assert "T8" in adm.PERGUNTAS_DO_UNIVERSO, "a regua T8 tem de estar portada"
    c = adm.carimbo_da_regua("T8")
    assert c["REGUA_T8"] == "v1" and c["VALIDADO_POR_HUMANO"] == "NAO"
    assert adm.carimbo_da_regua("T7") == {}, "so a regua candidata leva carimbo"
    assert "T8" in adm.TRANSVERSAIS, "T8 e transversal: nao exclui outro universo"


# ══════════════════════════════════════════════════════════════════════════════
# D156 · DUAS CAPTURAS DOS MESMOS BYTES SAO DUAS OBSERVACOES (COL-LAW-204/311)
# ══════════════════════════════════════════════════════════════════════════════
def test_armadilha_duas_urls_com_os_mesmos_bytes_preservam_duas_observacoes():
    """⚠️ Este codigo descartava por sha256 ANTES de preservar, e casava o RAW_OBSERVATION_ID tambem
    pelo sha. Dois enderecos que devolvam o MESMO byte sao duas OBSERVACOES do mundo, e nao uma: um
    canal que republica o mesmo boletim em duas paginas perdia uma das duas, calado.

        O SHA IDENTIFICA O CONTEUDO. NAO IDENTIFICA A OBSERVACAO."""
    import onda_linha as OL
    from guarda import preservar_coleta as PC
    mesmos = b'{"TITLE":"o mesmo byte","DESCRIPTION":"identico"}'
    colhidos = [{"BYTES": mesmos, "URL": "https://x.it/a", "MEDIA_TYPE": "application/json",
                 "ROTA": "r", "_DESCOBERTA": {}},
                {"BYTES": mesmos, "URL": "https://x.it/b", "MEDIA_TYPE": "application/json",
                 "ROTA": "r", "_DESCOBERTA": {}}]
    cand = {"SOURCE_ID": "IT-T9-001", "UNIVERSOS_DO_PEDIDO": []}
    visto = {}

    class _Persistencia:
        raiz_do_armazem = str(RAIZ)
        memoria = object()

    def _preservar(run, artefatos, armazem, bytes_de, memoria=None):
        visto["artefatos"] = artefatos
        # o dono do RAW devolve UM par por artefato, com a alca que o chamador atou
        # a forma REAL do recibo: as alcas viajam em RAW_OBSERVATIONS, com o RUN_ID
        return {"RUN_STATE": "OK", "RAW_OBSERVATIONS": [
            {"RAW_OBSERVATION_ID": 100 + i, "RUN_ID": run["RUN_ID"], "SHA256": a["SHA256"],
             PC.PASSAGENS: [a[PC.PASSAGEM]]}
            for i, a in enumerate(artefatos)]}
    real = PC.preservar
    PC.preservar = _preservar
    try:
        r = OL.para_a_sala("YOUTUBE", cand, colhidos, "IT-T9-2026-09-29-000000-0123456789abcdef",
                           persistencia=_Persistencia(), pousar=False)
    finally:
        PC.preservar = real
    assert len(visto["artefatos"]) == 2, "uma das duas capturas foi deitada fora antes de preservar"
    assert {a["SHA256"] for a in visto["artefatos"]} == {visto["artefatos"][0]["SHA256"]}, \
        "os bytes eram para ser os mesmos"
    assert {a["SOURCE_URL"] for a in visto["artefatos"]} == {"https://x.it/a", "https://x.it/b"}
    ids = [l["RAW_OBSERVATION_ID"] for l in r["RELATO"]]
    assert sorted(ids) == [100, 101], "cada captura tem de receber o SEU id: %s" % ids
    assert len({l["PASSAGEM"] for l in r["RELATO"]}) == 2, "as alcas tem de ser distintas"


# ══════════════════════════════════════════════════════════════════════════════
# D156 · O TERRITORIO NAO SE INVENTA
# ══════════════════════════════════════════════════════════════════════════════
def test_armadilha_run_id_nao_inventa_territorio():
    """⚠️ Caia num T9 por omissao — e T9 e COMPETITORS, um universo real com dono. Uma corrida de uma
    fonte sem territorio ficava carimbada como sendo de concorrentes, para sempre."""
    import onda_linha as OL
    for sem in (None, "", "CAND-0078", "COMPETITOR-PUBLIC-COMM/CONTAS-V1#BAYER|IT|INSTAGRAM"):
        try:
            r = OL.run_id(sem)
            raise AssertionError("inventou um territorio para %r: %s" % (sem, r))
        except OL.TerritorioNaoDeclarado as ex:
            assert "TERRITORIO_NAO_DECLARADO" in str(ex)
    # declarado: passa, e a prova continua a saber ler
    sys.path.insert(0, str(RAIZ / "provas"))
    import prova_teto_dominio as PT
    assert PT.RE_RUN_ID.fullmatch(OL.run_id("CAND-0078", "T9"))
    # e a AUSENCIA declarada (T0) tambem e legivel pela prova — mas nao e um territorio real
    import territorios as TERR
    assert OL.SEM_TERRITORIO not in TERR.TERRITORIOS, "T0 nao pode colidir com um territorio real"
    r = OL.run_id("CAND-0078", None, aceitar_sem_territorio=True)
    assert PT.RE_RUN_ID.fullmatch(r) and "-T0-" in r
    for real in ("T7", "T8", "T9"):
        assert "-%s-" % real not in r, "a ausencia de territorio nao pode sair carimbada como %s" % real


# ══════════════════════════════════════════════════════════════════════════════
# D157 + LAB · NAO SE RE-PEDE O QUE JA SE COLHEU, E A SALA NAO REPETE O CONTEUDO
# ══════════════════════════════════════════════════════════════════════════════
def _html_de_reel(caption="Difesa del vigneto dalla peronospora in campo", conta="bayer_italia"):
    return ('<html><head>'
            '<meta property="og:title" content="Bayer Italia no Instagram">'
            '<meta property="og:description" content="%s">'
            '</head><body><script>{"owner":{"username":"%s"},'
            '"taken_at_timestamp":1789000000,"caption":"%s"}</script></body></html>'
            % (caption, conta, caption))


def test_o_reel_entra_como_registo_de_metadados_e_nao_como_pagina():
    """Decisao do coordenador (29/09): a unidade do Reel e o REGISTO, como o YouTube ja faz. A pagina
    do Reel e HTML, logo ganhava retrato do detector, e o juiz de capa/materia respondia QUARENTENA a
    uma pergunta que nao se aplica — um Reel nao e materia nem pagina de entrada."""
    import onda_linha as OL
    b = leitor(_html_de_reel())
    c = OL.colher_alvo("INSTAGRAM", {"URL": "https://www.instagram.com/reel/DcNkh7LCW4u/",
                                     "CONTA": "bayer_italia"}, b)
    assert c["MEDIA_TYPE"] == "application/json", "a unidade tem de ser o registo, nao a pagina"
    r = c["REGISTO"]
    assert r["NATIVE_ID"] == "DcNkh7LCW4u"
    assert r["ACCOUNT"] == "bayer_italia"
    assert r["PLATFORM"] == "INSTAGRAM"
    assert "peronospora" in (r["CAPTION"] or "")
    assert r["PUBLISHED_AT"], "a data sai do documento, nunca do nosso relogio"
    assert r["FONTE_SHA256"], "o registo aponta para os bytes de onde saiu"
    assert r["ROBOTS_STATUS"] == "DISALLOW" and r["OWNER_AUTHORIZED"] == "SIM"


def test_a_pagina_do_reel_continua_preservada_como_observacao():
    """Preservar nao e admitir. A pagina e a prova do que a plataforma serviu, e nao se deita fora
    por o item julgado ser outro — duas capturas, DUAS observacoes (COL-LAW-204/311)."""
    import onda_linha as OL
    c = OL.colher_alvo("INSTAGRAM", {"URL": "https://www.instagram.com/reel/DcNkh7LCW4u/"},
                       leitor(_html_de_reel()))
    fonte = c["_FONTE"]
    assert fonte["MEDIA_TYPE"] == "text/html"
    assert fonte["ADMITIR"] is False
    assert b"<html>" in fonte["BYTES"]
    assert fonte["PEDIDOS"] == 0, "a pagina ja veio no mesmo pedido: nao se pede outra vez"


def test_armadilha_o_registo_do_reel_nao_leva_pela_frente_o_juiz_de_capa():
    """⚠️ O registo passa a ser julgado pelo UNIVERSO, e NAO pela capa. E isto NAO declara que «social
    nao passa pelo juiz»: e o tipo da unidade que mudou, nao a lei da Admission."""
    import onda_linha as OL
    reg = OL.admitir(json.dumps({"PLATFORM": "INSTAGRAM", "CAPTION":
                                 "In campo con l agricoltore: difesa del vigneto, potatura e raccolto. " * 3
                                 }).encode("utf-8"),
                     "application/json", "https://www.instagram.com/reel/X/", "CAND-1", "T8",
                     "sha", "2026-09-29T00:00:00Z", "R")
    assert reg["REGRA"] != "materia", "o juiz de capa foi aplicado a um registo: %s" % reg["MOTIVO"]
    assert "QUARENTENA" not in (reg["MOTIVO"] or "")


def test_armadilha_a_materia_comum_em_html_continua_a_passar_pelo_juiz_de_capa():
    """⚠️ A CONTRAPROVA, e ela e obrigatoria: se o juiz de capa deixasse de correr para HTML, esta
    correccao teria trocado um defeito por outro maior — uma pagina de entrada entraria como materia."""
    import onda_linha as OL
    import executor_texto_de_html as H
    pagina = ("<html><body>" + "<a href='/x'>link</a>" * 80 + "</body></html>").encode("utf-8")
    assert H._retrato(pagina), "o detector tem de olhar para HTML"
    d = OL.admitir(pagina, "text/html", "https://exemplo.it/indice", "IT-T3-001", "T3",
                   "sha", "2026-09-29T00:00:00Z", "R")
    assert d["REGRA"] == "materia", "o juiz de capa deixou de correr sobre HTML: %s" % d["REGRA"]


def test_armadilha_a_d22_abre_o_reel_e_nao_o_dominio():
    """⚠️ `autorizacao_do_dono` limita HOST, nao CAMINHO. Com o host aberto, o perfil e o /embed/ da
    conta passavam pela MESMA porta — e a D22 abre o REEL POR URL DIRECTA; a CONTA continua
    POLICY_BLOCK pela D19.

        AMPLIAR UMA AUTORIZACAO PORQUE ELA ESTAVA PERTO E COMO TRATA-LA COMO PERMISSAO GERAL."""
    ok = "https://www.instagram.com/reel/DcNkh7LCW4u/"
    assert RM.caminho_de_reel_permitido(ok)
    assert RM.caminho_de_reel_permitido(ok.rstrip("/"))
    for recusado in (
            "https://www.instagram.com/bayer_italia/",              # o perfil
            "https://www.instagram.com/bayer_italia/embed/",        # a listagem da conta
            "https://www.instagram.com/reel/DcNkh7LCW4u/embed/",    # o embed DO reel
            "https://www.instagram.com/p/DcNkh7LCW4u/",             # um post que nao e reel
            "https://www.instagram.com/accounts/login/",            # o ecra de login
            "https://www.instagram.com/",
            "https://exemplo.it/reel/DcNkh7LCW4u/"):                # outro host
        assert not RM.caminho_de_reel_permitido(recusado), "a D22 nao abre %s" % recusado


def test_a_rota_do_reel_cita_a_decisao_escrita_do_dono():
    """A autorizacao tem de dizer QUEM decidiu e ONDE esta escrito — uma excepcao sem nome de quem a
    autorizou e um bypass com outro nome, e e o proprio `scrap_http` que o diz."""
    assert RM.DECISAO_DO_DONO_IG == "D22"
    for pedaco in ("D22", "DECISOES-DONO-2026-09-23.md", "OWNER_AUTHORIZED=SIM",
                   "PLATFORM_POLICY_STATUS=DISALLOWED"):
        assert pedaco in RM.AUTORIZACAO_ESCRITA_IG, pedaco


def test_o_rasto_do_reel_nao_esconde_que_o_robots_barra():
    """O que se mede fica no rasto e NAO se apaga: o robots barra, e isso e um facto que viaja."""
    b = leitor("<html>reel</html>")
    r = RM.instagram_reel(url="https://www.instagram.com/reel/DcNkh7LCW4u/", buscar=b)
    assert r["ROBOTS_STATUS"] == "DISALLOW"
    assert r["PLATFORM_POLICY_STATUS"] == "DISALLOWED"
    assert r["OWNER_AUTHORIZED"] == "SIM"
    assert r["DECISAO_DO_DONO"] == "D22"
    assert b.chamadas == ["https://www.instagram.com/reel/DcNkh7LCW4u/"], \
        "pediu um caminho que a D22 nao abre: %s" % b.chamadas


def test_armadilha_um_redirect_para_outro_caminho_e_recusa():
    """⚠️ Um 302 para o perfil ou para um ecra de login e do MESMO host — a autorizacao por host
    deixava-o passar. Um redireccionamento nao e uma autorizacao nova.

        PEDIR UM ENDERECO NAO E CHEGAR A ELE."""
    def buscar_que_redirige(url, aceitar=None):
        return {"STATUS": 200, "BYTES": b"<html>login</html>", "ERRO": None,
                "URL_FINAL": "https://www.instagram.com/accounts/login/"}
    r = RM.instagram_reel(url="https://www.instagram.com/reel/DcNkh7LCW4u/", buscar=buscar_que_redirige)
    assert "BYTES" not in r
    assert "REDIRECT_FORA_DA_D22" in r["ERRO"]
    assert r["ROBOTS_STATUS"] == "DISALLOW", "o rasto viaja mesmo na recusa"


def test_o_embed_do_reel_e_montado_para_fora_mesmo_que_venha_na_url():
    """Quem passar `/reel/<code>/embed/` recebe o REEL, nao o embed: o alvo e MONTADO do codigo."""
    b = leitor("<html>reel</html>")
    RM.instagram_reel(url="https://www.instagram.com/reel/DcNkh7LCW4u/embed/", buscar=b)
    assert b.chamadas == ["https://www.instagram.com/reel/DcNkh7LCW4u/"]


def test_a_conta_sem_reel_provado_nao_manda_listar_a_conta():
    """SO_URL_DIRETA_SEM_LISTAGEM: sem Reel provado pelo Curator, a linha para — e NAO vai pedir a
    pagina da conta para descobrir algum."""
    import onda_linha as OL
    b = leitor("<a href='/reel/XXXXX/'>x</a>")
    cand = {"SOURCE_ID": "CAND-0078", "ALVO": {"HANDLE": "granapadano", "REELS_CONHECIDOS": []}}
    r = OL.alvos_da_fonte("INSTAGRAM", cand, b)
    assert "SEM_REEL_CONHECIDO" in r["ERRO"]
    assert b.chamadas == [], "foi listar a conta: %s" % b.chamadas


def test_a_linha_instagram_so_usa_os_reels_provados_pelo_curator():
    import onda_linha as OL
    b = leitor("<html>x</html>")
    cand = {"SOURCE_ID": "COMPETITOR-X", "ALVO": {
        "HANDLE": "bayer_italia",
        "REELS_CONHECIDOS": ["https://www.instagram.com/reel/DcNkh7LCW4u/",
                             "https://www.instagram.com/reel/DZ9ygDrCwzu/"]}}
    r = OL.alvos_da_fonte("INSTAGRAM", cand, b)
    assert [a["URL"] for a in r["ALVOS"]] == cand["ALVO"]["REELS_CONHECIDOS"]
    assert r["PEDIDOS"] == 0, "a descoberta nao gasta pedido: os Reels ja eram conhecidos"
    assert r["ROTA_LISTAGEM"] == "NAO_PEDIDA (D19)"
    assert b.chamadas == []


def test_armadilha_o_motor_de_busca_e_o_do_vivo_e_nao_um_nome_inventado():
    """⚠️ Eu tinha escrito «DUCKDUCKGO_HTML» por omissao; o dicionario do vivo chama-lhe `DDG_HTML`.
    As 5 consultas do canario morreram todas com KeyError, e o erro so apareceu na rede real."""
    sys.path.insert(0, str(RAIZ))
    import _gavetas  # noqa: F401
    import motores as MO
    import onda_linha as OL
    import re as _re
    fonte = open(RAIZ / "ferramentas" / "big_collection" / "onda_linha.py", encoding="utf-8").read()
    m = _re.search(r'SINTONIA_BUSCA_MOTOR"\) or "([A-Z_]+)"', fonte)
    assert m, "nao encontrei o motor por omissao"
    assert m.group(1) in MO.MOTORES,         "o motor por omissao (%s) nao existe no vivo; existem: %s" % (m.group(1), sorted(MO.MOTORES))
    # e um motor desconhecido tem de dizer QUAIS existem, em vez de rebentar com KeyError
    import os as _os
    _os.environ["SINTONIA_BUSCA_MOTOR"] = "NAO_EXISTE_ESTE"
    try:
        r = OL.alvos_da_fonte("BUSCA", {"SOURCE_ID": "Q1", "ALVO": {"CONSULTA": "x"}}, leitor("x"))
        assert "MOTOR_DESCONHECIDO" in r["ERRO"] and "DDG_HTML" in r["ERRO"]
    finally:
        _os.environ.pop("SINTONIA_BUSCA_MOTOR", None)


def test_a_sala_fica_com_a_variante_rica_do_mesmo_documento():
    """As 7 variantes que o LAB contou NAO sao duplicados: sao o oEmbed (so titulo) e a pagina /watch
    (com a descricao) do MESMO video. Apagar uma delas perderia informacao real; a Sala fica com a que
    ve mais, e as outras continuam preservadas no RAW."""
    import onda_linha as OL
    pobre = {"ITEM_ID": "doc-1", "TEXTO": "Peronospora"}
    rica = {"ITEM_ID": "doc-1", "TEXTO": "Peronospora della vite: difesa, fungicidi e strategia " * 4}
    assert OL._riqueza(rica) > OL._riqueza(pobre)


def test_o_alvo_ja_colhido_na_janela_nao_e_pedido_outra_vez():
    """31 dos 45 RAW do canario (69%) eram o MESMO video regravado ate 6x. O desperdicio nao e o
    ficheiro a mais: e o PEDIDO a mais, que gasta orcamento que uma fonte nova nao vai ter."""
    import onda_linha as OL
    t = _Temp()
    try:
        base = Path(t.pasta)
        OL.anotar_visto(base, "YOUTUBE", "https://www.youtube.com/watch?v=aaaaaaaaaaa", "RUN-1")
        v = OL.ler_vistos(base)
        assert v[("YOUTUBE", "https://www.youtube.com/watch?v=aaaaaaaaaaa")]["RUN_ID"] == "RUN-1"
        assert ("YOUTUBE", "https://www.youtube.com/watch?v=outro") not in v
        assert ("LINKEDIN", "https://www.youtube.com/watch?v=aaaaaaaaaaa") not in v, \
            "o livro e por LINHA e por alvo"
        # fora da janela deixa de contar
        assert OL.ler_vistos(base, janela_s=1, agora=__import__("time").time() + 10) == {}
    finally:
        t.fechar()


def test_um_livro_de_vistos_estragado_nao_apaga_a_memoria():
    """Uma linha ilegivel nao pode fazer o coletor esquecer tudo o que ja colheu — seria voltar a
    pedir o mundo inteiro por causa de um byte."""
    import onda_linha as OL
    t = _Temp()
    try:
        base = Path(t.pasta)
        OL.anotar_visto(base, "YOUTUBE", "https://x/1", "RUN-1")
        with open(base / OL.VISTOS_F, "a", encoding="utf-8") as f:
            f.write("{isto nao e json\n")
        OL.anotar_visto(base, "YOUTUBE", "https://x/2", "RUN-2")
        v = OL.ler_vistos(base)
        assert len(v) == 2
    finally:
        t.fechar()


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
