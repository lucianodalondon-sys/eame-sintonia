#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""A LEGENDA E O AUDIO DO YOUTUBE — a pergunta que sobrou depois do video.

    python3 provas/a_legenda_e_o_audio_do_youtube.py

A PERGUNTA QUE ESTA PROVA RESPONDE
-----------------------------------
A C4F mediu que adquirir VIDEO do YouTube e `ROUTE_NOT_ALLOWED`. Ficou de pe
uma hipotese razoavel, e ela merecia medicao propria:

    para transcrever, talvez esta casa nao precise dos bytes do video.
    Talvez baste a LEGENDA publica. Ou, faltando ela, SO O AUDIO.

Se fossem a mesma coisa, a resposta ja estaria dada. NAO SAO:

    FETCH_VIDEO_METADATA  !=  FETCH_PUBLIC_CAPTION
    FETCH_PUBLIC_CAPTION  !=  FETCH_AUDIO_STREAM
    FETCH_AUDIO_STREAM    !=  FETCH_VIDEO_STREAM

Quatro capacidades, quatro autorizacoes possiveis. Trata-las como uma so —
`FETCH_VIDEO` — foi exactamente o erro que esta prova existe para nao repetir.

O QUE ELA MEDE, E O QUE ELA RECUSA MEDIR
-----------------------------------------
MEDE, na hora, nesta maquina:

    o `robots.txt` VIVO do hospedeiro, sobre os caminhos REAIS que cada uma
    das rotas usaria — nao sobre o caminho que a casa imagina que usaria;

    o que `leis/social_matriz.py` DECLARA para cada rota de legenda;

    se existe, na matriz, qualquer capacidade de AUDIO — e o silencio dela
    nao e lido como permissao;

    se o `yt-dlp` esta instalado nesta arvore.

RECUSA medir por tentativa: nenhuma requisicao e feita a um endereco de
conteudo. O unico ficheiro que esta prova busca e o `robots.txt`, que e o
ficheiro que todo agente tem direito de ler, e e a pergunta «posso?» feita a
quem responde.

    UMA PROVA QUE PRECISA DE VIOLAR A POLITICA PARA MEDIR A POLITICA
    NAO ESTA A MEDIR NADA: ESTA A DECIDIR.

⚠️ O QUE ESTA PROVA NAO FAZ, E POR ESCOLHA
-------------------------------------------
Nao instala `yt-dlp`, nao adquire legenda, nao adquire audio, e nao escreve o
adaptador que faria qualquer das duas. Com tres autoridades a dizer nao, isso
seria contornar — e contornar em silencio e pior do que contornar, porque a
proxima missao herda a rota sem herdar a decisao.

    ROTA QUE FUNCIONA NAO E ROTA PERMITIDA.
"""
import io
import json
import os
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)
import _gavetas                                    # noqa: E402,F401

SAIDA = os.path.join(RAIZ, "system-map", "data",
                     "youtube-legenda-audio.generated.json")

#: O canario. E um video do piloto italiano REAL — `YOUTUBE-PILOTO-IT.json`,
#: canal `@agronotizietv`, resolvido pela Data API oficial. Ele entra aqui
#: para que os caminhos testados sejam os caminhos verdadeiros, e NAO um
#: `VIDEO_ID` inventado que faria o `robots.txt` responder sobre nada.
#:
#: ⚠️ ELE NAO TEM `SOURCE_ID`. O proprio piloto escreve `KNOWN_SOURCE =
#: NENHUMA — ONE_SHOT nao consulta memoria`. Fabricar um a partir do handle,
#: da URL ou do `CHANNEL_ID` seria inventar identidade, e `COL-LAW-206` diz
#: que a URL nao e uma das tres. Fica `NAO SEI`, declarado.
CANARIO_VIDEO_ID = "MCnd9c2pzd8"
CANARIO_CANAL_ID = "UCUs2Mg7jvUTRt7_MSOFYM5Q"
CANARIO_SOURCE_ID = "NAO SEI"

#: Os caminhos REAIS de cada rota. O nome da rota nao basta: a C5 mostrou que
#: a matriz desta casa citava `/timedtext_video` como prova, quando a `baseUrl`
#: que sai de `captionTracks` aponta para `/api/timedtext` — outro caminho,
#: outro `Disallow`, e o veredito so estava certo por sorte.
#:
#:     UMA CITACAO ERRADA CAI NO DIA EM QUE ALGUEM A CONFERE.
CAMINHOS = (
    ("CAPTION_TIMEDTEXT", "FETCH_PUBLIC_CAPTION",
     "https://www.youtube.com/api/timedtext?v=%s&lang=it" % CANARIO_VIDEO_ID,
     "a `baseUrl` real de `captionTracks` — a legenda publica, se houver"),
    ("CAPTION_PAGINA_WATCH", "FETCH_PUBLIC_CAPTION",
     "https://www.youtube.com/watch?v=%s" % CANARIO_VIDEO_ID,
     "a pagina de onde se leria `ytInitialPlayerResponse.captionTracks`"),
    ("AUDIO_PLAYER_INTERNO", "FETCH_AUDIO_STREAM",
     "https://www.youtube.com/youtubei/v1/player",
     "por onde o `yt-dlp` pede os formatos, audio-only inclusive"),
    ("AUDIO_GET_VIDEO", "FETCH_AUDIO_STREAM",
     "https://www.youtube.com/get_video?video_id=%s" % CANARIO_VIDEO_ID,
     "o endereco historico do fluxo de midia"),
    ("METADATA_OEMBED", "FETCH_VIDEO_METADATA",
     "https://www.youtube.com/oembed?url=https://www.youtube.com/watch?v=%s"
     % CANARIO_VIDEO_ID,
     "o controlo POSITIVO: a unica rota livre PROVED, e traz so o nome"),
)

#: As clausulas que decidem, buscadas na fonte viva. Elas nao sao medidas por
#: codigo — sao CITACOES, e por isso carregam a data em que foram lidas, que e
#: a unica coisa que as impede de virar folclore.
#:
#: ⚠️ A III.I.7 e a que muda esta missao. Ela nao fala de «baixar video»:
#: fala de SEPARAR O AUDIO. E separar o audio era, literalmente, o plano B.
CLAUSULAS = (
    ("III.I.7", "separate, isolate, or modify the audio or video components "
                "of any YouTube audiovisual content",
     "FETCH_AUDIO_STREAM", "2026-09-14"),
    ("III.E.1.a", "download, import, backup, cache, or store copies of "
                  "YouTube audiovisual content without YouTube's prior "
                  "written approval",
     "PRESERVAR OS BYTES", "2026-09-14"),
    ("III.I.14", "use any technology other than YouTube API Services to "
                 "access or retrieve API Data, including to access any "
                 "portion of any YouTube audiovisual content",
     "yt-dlp COMO ADAPTADOR", "2026-09-14"),
)
FONTE_DAS_CLAUSULAS = ("https://developers.google.com/youtube/terms/"
                       "developer-policies")

FALHAS, PASSOU = [], []
achados = {}


def T(nome, condicao, detalhe=""):
    (PASSOU if condicao else FALHAS).append(nome)
    print("  %s  %s%s" % ("ok  " if condicao else "FALHA", nome,
                          ("" if condicao else "\n        " + detalhe)))


def _mede(nome, valor, porque):
    achados[nome] = {"VALOR": valor, "PORQUE": porque}
    print("  %-30s = %-22s %s" % (nome, valor, porque[:60]))
    return valor


print("A LEGENDA E O AUDIO DO YOUTUBE")
print()

# ── 1 · O PORTAO VIVO, SOBRE OS CAMINHOS REAIS ────────────────────────────
# `permitido()` busca o `robots.txt` do hospedeiro com o `User-Agent` REAL
# desta coleta. Uma resposta — qualquer resposta, recusa inclusive — prova
# que a rede chegou la.
#
#     RECUSA E POLITICA. AUSENCIA DE RESPOSTA E REDE. NAO SAO A MESMA COISA,
#     E CONSERTAM-SE EM SITIOS DIFERENTES.
print("  O PORTAO, LIDO AGORA")
import scrap_http as http                                      # noqa: E402

portao, vivos = {}, 0
for nome, capacidade, url, porque in CAMINHOS:
    try:
        ok, motivo = http.permitido(url)
    except Exception as e:                                     # noqa: BLE001
        portao[nome] = {"CAPACIDADE": capacidade, "VEREDITO": "NOT_MEASURED",
                        "PORQUE": "o transporte caiu antes da resposta (%s) — "
                                  "isto NAO e uma recusa do hospedeiro"
                                  % type(e).__name__, "URL": url}
        _mede(nome, "NOT_MEASURED", portao[nome]["PORQUE"])
        continue
    vivos += 1
    portao[nome] = {"CAPACIDADE": capacidade,
                    "VEREDITO": "ROBOTS_ALLOWS" if ok else "ROBOTS_DISALLOWS",
                    "PORQUE": motivo, "URL": url, "O_QUE_E": porque}
    _mede(nome, portao[nome]["VEREDITO"], motivo)

T("o portao respondeu sobre todos os caminhos — a medicao e de rede viva",
  vivos == len(CAMINHOS),
  "so %d de %d caminhos obtiveram resposta do robots.txt" % (vivos, len(CAMINHOS)))

# O controlo NEGATIVO. Um portao que so aprova nao e portao; um que so recusa
# tambem nao mede nada. Os dois lados tem de aparecer na mesma corrida.
barrados = [n for n, d in portao.items() if d["VEREDITO"] == "ROBOTS_DISALLOWS"]
permitidos = [n for n, d in portao.items() if d["VEREDITO"] == "ROBOTS_ALLOWS"]
T("o portao discrimina — barrou uns e deixou passar outros",
  bool(barrados) and bool(permitidos),
  "barrados=%s permitidos=%s" % (barrados, permitidos))

# ── 2 · A LEGENDA, PELA POLITICA DE ROTA ──────────────────────────────────
print()
print("  A LEGENDA")
import social_matriz as mz                                     # noqa: E402

legenda = mz.MATRIZ["YOUTUBE"]["FETCH_TRANSCRIPT"]
livres_permitidas = [r for r in legenda
                     if r["CLASSE"] != "APIFY" and r["PERMITIDA"] == "SIM"]
for r in legenda:
    _mede("CAPTION_%s" % r["ROTA"].split(":")[-1].upper().replace(".", "_"),
          r["ESTADO"], r["NOTA"][:60])

# ⚠️ OS ESTADOS NAO SE COLAPSAM, E O §7 DO BRIEFING PEDIU-OS SEPARADOS.
# `REQUIRES_OWNER_PERMISSION` e `CAPTION_NOT_AVAILABLE` sao coisas opostas:
# o primeiro diz que a legenda PODE existir e a porta e de outra pessoa.
#
#     ERRO DE ACESSO TRADUZIDO PARA «NAO EXISTE» APAGA A DIFERENCA ENTRE
#     UM VIDEO SEM LEGENDA E UM VIDEO CUJA LEGENDA NAO ME DEIXAM LER.
estado_da_legenda = ("CAPTION_NOT_ACCESSIBLE" if not livres_permitidas
                     else "CAPTION_ROUTE_AVAILABLE_NOT_EXERCISED")
_mede("CAPTION_STATUS", estado_da_legenda,
      "nenhuma rota livre de legenda esta PERMITIDA=SIM para canal de terceiro"
      if not livres_permitidas else
      "ha rota livre permitida: %s" % [r["ROTA"] for r in livres_permitidas])
_mede("CAPTION_KIND", "UNKNOWN",
      "sem ler a faixa nao se sabe se a legenda e MANUAL ou AUTOMATIC — e "
      "`captions.list`, que responderia, pede OAuth e nao traz o texto")
_mede("CAPTION_LANGUAGE", "UNKNOWN",
      "idem: a lingua da faixa so se sabe lendo a ficha da faixa")

T("nenhuma rota livre de legenda se declara permitida para terceiro",
  not livres_permitidas,
  "apareceu rota livre PERMITIDA=SIM: %s — actualize esta prova e o relatorio"
  % [r["ROTA"] for r in livres_permitidas])

# ── 3 · O AUDIO — E O SILENCIO DA MATRIZ ──────────────────────────────────
print()
print("  O AUDIO")
capacidades = [c for c in mz.MATRIZ["YOUTUBE"] if not c.startswith("_")]
de_audio = [c for c in capacidades if "AUDIO" in c.upper()]
_mede("AUDIO_CAPABILITY_DECLARADA", "NO" if not de_audio else ",".join(de_audio),
      "as %d capacidades do YouTube na matriz sao %s — nenhuma de bytes de "
      "audio" % (len(capacidades), capacidades))

# ⚠️ E O SILENCIO NAO E A RESPOSTA. `social_matriz` escreve-o por extenso:
# «O SILENCIO DA MATRIZ NAO PROIBE, E TAMBEM NAO AUTORIZA.» Quem fecha esta
# porta nao e a ausencia de linha — sao as clausulas abaixo, que existem e
# nomeiam o audio directamente.
_mede("AUDIO_STATUS", "ROUTE_NOT_ALLOWED",
      "nao e o silencio da matriz que fecha: e a III.I.7, que nomeia "
      "«separate, isolate ... the audio components» por extenso")

for numero, texto, sobre_o_que, lido_em in CLAUSULAS:
    _mede("POLICY_%s" % numero.replace(".", "_"), "PROIBE",
          "%s — sobre %s (lido em %s)" % (texto[:44], sobre_o_que, lido_em))

T("a clausula que nomeia o audio esta registada com data de leitura",
  all(len(c[3]) == 10 for c in CLAUSULAS),
  "uma clausula sem data de leitura e folclore, nao evidencia")

# ── 4 · A FERRAMENTA — O QUE NAO ESTA INSTALADO NAO SE USA POR ENGANO ────
print()
print("  A FERRAMENTA")
try:
    import yt_dlp                                              # noqa: E402,F401
    tem_ytdlp = True
    versao = getattr(getattr(yt_dlp, "version", None), "__version__", "?")
except Exception:                                              # noqa: BLE001
    tem_ytdlp, versao = False, "nao instalado"
_mede("YT_DLP_PRESENTE", "YES" if tem_ytdlp else "NO",
      "versao %s — e ele passa por `/youtubei/`, que o portao acima barrou"
      % versao)

# ⚠️ NAO E UM TESTE DE QUALIDADE. Ter `yt-dlp` instalado nao seria um defeito,
# e nao o ter nao e uma protecao: a decisao e da politica, nao do `pip`. Isto
# mede-se porque uma ferramenta ausente explica por que NENHUMA tentativa
# aconteceu — e sem o campo, a proxima missao pergunta outra vez.
#
#     A POLITICA DECIDE. O `pip` SO REGISTA.

# ── 5 · O VEREDITO, DERIVADO E NAO AFIRMADO ──────────────────────────────
print()
print("  O VEREDITO")
caption_fechada = not livres_permitidas
audio_fechado = not de_audio
_mede("ACQUISITION_POLICY_VERDICT",
      "BLOCKED_NEEDS_AUTHORIZATION" if (caption_fechada and audio_fechado)
      else "PARTIAL",
      "legenda e audio fechados pelas MESMAS autoridades que fecharam o video"
      " — e a III.I.7 fecha o audio com nome proprio")
_mede("POLICY_DECISION_REQUIRED", "YES" if (caption_fechada and audio_fechado)
      else "NO",
      "abrir qualquer das duas rotas depende de permissao escrita do YouTube,"
      " e essa decisao e de gente, nao de codigo")
_mede("FULL_VIDEO_FETCHED", "NO", "nada foi adquirido nesta corrida")
_mede("AUDIO_BYTES", "0", "nenhum byte de midia foi pedido nem recebido")
_mede("CAPTION_BYTES", "0", "nenhuma legenda foi pedida nem recebida")

T("o veredito fecha as duas rotas, e nao so a do video",
  caption_fechada and audio_fechado,
  "uma das duas abriu: caption_fechada=%s audio_fechado=%s"
  % (caption_fechada, audio_fechado))

estado = {
    "O_QUE_ISTO_E": ("Se LEGENDA publica e AUDIO-ONLY do YouTube sao rotas "
                     "permitidas a esta casa — medido, nao herdado do "
                     "veredito do video."),
    "COMO_REFAZER": "python3 provas/a_legenda_e_o_audio_do_youtube.py",
    "A_LEI": ("CAPTION != TRANSCRIPT · AUDIO_ONLY != VIDEO · "
              "METADATA != MEDIA BYTES · ROTA QUE FUNCIONA != ROTA PERMITIDA"),
    "O_CANARIO": {
        "SOURCE_ID": CANARIO_SOURCE_ID,
        "PLATFORM_VIDEO_ID": CANARIO_VIDEO_ID,
        "CHANNEL_ID": CANARIO_CANAL_ID,
        "PROVENANCE": "data/samples/SOCIAL-IT/YOUTUBE-PILOTO-IT.json",
        "PORQUE_SEM_SOURCE_ID": (
            "o piloto declara `KNOWN_SOURCE = NENHUMA`. Derivar um SOURCE_ID "
            "do handle, da URL ou do CHANNEL_ID seria fabricar identidade."),
    },
    "O_PORTAO": portao,
    "AS_CLAUSULAS": [{"SECAO": n, "TEXTO": t, "FECHA": s, "FETCHED_AT": d,
                      "FONTE": FONTE_DAS_CLAUSULAS}
                     for n, t, s, d in CLAUSULAS],
    "MEDIDO": achados,
    "O_QUE_ABRIRIA_ESTA_PORTA": (
        "permissao escrita previa do YouTube, ou a autorizacao do dono de "
        "cada video para `captions.download`. Nenhuma das duas se resolve "
        "escrevendo codigo, e por isso esta missao parou aqui em vez de "
        "instalar `yt-dlp`."),
}
os.makedirs(os.path.dirname(SAIDA), exist_ok=True)
with io.open(SAIDA, "w", encoding="utf-8") as f:
    json.dump(estado, f, ensure_ascii=False, indent=1)
    f.write("\n")

print()
print("  gravado: %s" % os.path.relpath(SAIDA, RAIZ))
print()
print("LEGENDA_E_AUDIO = %s · %d passaram · %d falharam"
      % ("MEDIDO" if not FALHAS else "FALHOU", len(PASSOU), len(FALHAS)))
raise SystemExit(1 if FALHAS else 0)
