#!/usr/bin/env python3
"""
A FALA DO VÍDEO CHEGA POR OUTRA PORTA? — mede rota alternativa, não contorna rota fechada.

    py provas/rotas_de_fala_do_youtube.py rotas      # abre as rotas candidatas e mede
    py provas/rotas_de_fala_do_youtube.py oficial    # o que a rota oficial do YouTube diz hoje
    py provas/rotas_de_fala_do_youtube.py censo      # regrava o censo com o que foi medido
    py provas/rotas_de_fala_do_youtube.py tudo

O QUE ESTE ARQUIVO NÃO É
==========================
Não baixa vídeo. Não separa áudio. Não pede legenda ao YouTube. Não faz login, não
manda cookie de conta, não resolve CAPTCHA, não usa `yt-dlp` nem equivalente.

A pergunta que ele responde é OUTRA:

    A FALA DAQUELE VÍDEO EXISTE, ESCRITA OU EM MÍDIA, NO SITE DE QUEM PUBLICOU?

Quem publica um vídeo técnico quase nunca publica só o vídeo. Publica o artigo, o
boletim, a apresentação, os atti do convegno, o replay do webinar. Esse material é
do publicador, está no domínio dele, e a rota para ele é a rota normal da web — a
mesma que o SINTONIA já usa para rótulo, bollettino e nota de serviço fitossanitário.

    O ATIVO PROCURADO É A FALA, NÃO OS BYTES SERVIDOS POR youtube.com.

POR QUE A ROTA OFICIAL DO YOUTUBE NÃO RESOLVE (medido, não lembrado)
======================================================================
Developer Policies do YouTube, lidas ao vivo:

    III.E.1.a   «download, import, backup, cache, or store copies of YouTube
                 audiovisual content without YouTube's prior written approval»
    III.I.7     «separate, isolate, or modify the audio or video components of
                 any YouTube audiovisual content»
    III.I.14    «use any technology other than YouTube API Services to access
                 or retrieve API Data»

E `captions.download` exige «permission to edit the video» — permissão do DONO do
vídeo, não uma chave de API mais cara. Para canal de terceiro não há rota oficial
de legenda. Isso não se conserta com dinheiro; conserta-se com autorização.

    "AUDIO-ONLY" NÃO É UMA VERSÃO MAIS LEVE DO PEDIDO. É O CASO QUE A III.I.7 DESCREVE.

O QUE CADA ESTADO SIGNIFICA
=============================
    ALTERNATIVE_OFFICIAL_SOURCE_FOUND   achei, no domínio do publicador, material
                                        que carrega a mesma fala (artigo, boletim,
                                        atti, replay, apresentação)
    TRANSCRIPT_OFFICIAL_AVAILABLE       o publicador entrega texto integral da fala
    MEDIA_OFFICIAL_AVAILABLE            o publicador entrega a mídia fora do YouTube
    OWNER_AUTHORIZATION_REQUIRED        existe a quem pedir, e o pedido é de gente
    BLOCKED_BY_POLICY                   cláusula nomeada fecha a porta
    BLOCKED_BY_ACCESS                   o servidor fecha (403/429/paywall duro)
    UNKNOWN                             NÃO SEI — e continua NÃO SEI

Nenhum estado é escrito por este arquivo a partir de opinião: cada um carrega o
`EVIDENCE` com URL, HTTP, bytes e o pedaço de texto que o sustenta.
"""
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(HERE)
SAIDA = os.path.join(RAIZ, "data", "samples", "YOUTUBE-ACQUISITION")

UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36"
)

# ---------------------------------------------------------------------------
# O CENSO — 14 vídeos, todos vindos de SENSOR-PILOT/MEDICAO.json.
# Nenhum SOURCE_ID é inventado aqui: o dataset de origem é o dono do id.
# ---------------------------------------------------------------------------
CENSO = [
    {
        "VIDEO_ID": "EAkcA_2FDN8",
        "CANAL": "Coldiretti Emilia Romagna",
        "PUBLISHER": "Coldiretti Emilia Romagna",
        "IMPORTANCE": "ALTA",
        "WHY_NEEDED": "convegno de 2h03 sobre flavescenza dourada da vite, com o estado da luta obrigatória — o caso IT-VINE-FLAVESCENCE",
        "ROTAS": [
            "https://www.coldiretti.it/",
            "https://agricoltura.regione.emilia-romagna.it/fitosanitario",
        ],
    },
    {
        "VIDEO_ID": "w_D7NYYI3b0",
        "CANAL": "Accademia dei Georgofili",
        "PUBLISHER": "Accademia dei Georgofili",
        "IMPORTANCE": "ALTA",
        "WHY_NEEDED": "Giornata di Studio de 2h37 sobre difesa fitosanitaria em olivicoltura — Xylella, Bactrocera, Prays",
        "ROTAS": [
            "https://www.georgofili.it/contenuti/difesa-fitosanitaria-in-olivicoltura-richiede-approfondimenti-di-conoscenze-o-ha-pi-bisogno-di-trasf/19541",
            "https://www.georgofili.info/contenuti/difesa-fitosanitaria-in-olivicoltura-richiede-approfondimenti-di-conoscenze-o-pi-trasferimenti-di-qu/28558",
        ],
    },
    {
        "VIDEO_ID": "rdDR4xgpQ4k",
        "CANAL": "Chambre d'Agriculture de la Gironde",
        "PUBLISHER": "Chambre d'Agriculture de la Gironde",
        "IMPORTANCE": "ALTA",
        "WHY_NEEDED": "webinar de 1h33 sobre mildiou e black-rot da vinha — estratégias combinadas",
        "ROTAS": [
            "https://www.vinopole.com/nos-publications/",
            "https://www.vinopole.com/wp-content/uploads/2025/12/Bilan-de-campagne-2025-VF.pdf",
            "https://www.vinopole.com/wp-content/uploads/2025/03/fiche-technique-n7-Plan-Mildiou.pdf",
        ],
    },
    {
        "VIDEO_ID": "RisRARQSFAg",
        "CANAL": "AIPO verona",
        "PUBLISHER": "AIPO — Associazione Interregionale Produttori Olivicoli",
        "IMPORTANCE": "ALTA",
        "WHY_NEEDED": "o vídeo LÊ o «Periodico n 18 del 01.05.2026» — boletim fenológico e fitossanitário do olival",
        "ROTAS": [
            "https://www.aipoverona.it/",
            "https://www.aipoverona.it/periodico-olivo-periodico-olivo-",
        ],
    },
    {
        "VIDEO_ID": "zaEk8LE6SOQ",
        "CANAL": "Agronotizie",
        "PUBLISHER": "Image Line — AgroNotizie",
        "IMPORTANCE": "ALTA",
        "WHY_NEEDED": "flavescenza dourada e Scaphoideus titanus; 36.100 visualizações, o mais visto do recorte",
        "ROTAS": ["https://agronotizie.imagelinenetwork.com/difesa-e-diserbo/2024/05/28/flavescenza-dorata-il-vero-nemico-e-la-cicalina-della-vite/84010"],
    },
    {
        "VIDEO_ID": "uIegdnccN9g",
        "CANAL": "Agronotizie",
        "PUBLISHER": "Image Line — AgroNotizie",
        "IMPORTANCE": "ALTA",
        "WHY_NEEDED": "resistência a herbicidas em arrozais lombardos — o caso IT-RICE-WEED",
        "ROTAS": ["https://agronotizie.imagelinenetwork.com/difesa-e-diserbo/2023/03/31/resistenze-agli-erbicidi-nei-giavoni-di-risaia-gli-innovativi-risultati-del-progetto-epiresistenze/78751"],
    },
    {
        "VIDEO_ID": "3mB_D1Nlvbk",
        "CANAL": "Agronotizie",
        "PUBLISHER": "Image Line — AgroNotizie",
        "IMPORTANCE": "MEDIA",
        "WHY_NEEDED": "dessecação da soja com ácido pelargónico — o caso IT-SOYBEAN",
        "ROTAS": ["https://agronotizie.imagelinenetwork.com/difesa-e-diserbo/2022/09/12/disseccamento-della-soia-tutti-i-vantaggi-di-beloukhasupregsup/71819"],
    },
    {
        "VIDEO_ID": "hoppQZ7f_ok",
        "CANAL": "Bayer Crop Science Italia",
        "PUBLISHER": "Bayer CropScience Italia",
        "IMPORTANCE": "MEDIA",
        "WHY_NEEDED": "ensaio de campo de herbicida em milho, com resultados de eficácia e seletividade — concorrente directo",
        "ROTAS": [
            "https://www.cropscience.bayer.it/magazine/articoli/campi-prova/podere-pignatelli",
            "https://www.cropscience.bayer.it/",
        ],
    },
    {
        "VIDEO_ID": "QGE7h4gztQ8",
        "CANAL": "L'Informatore Agrario",
        "PUBLISHER": "L'Informatore Agrario",
        "IMPORTANCE": "ALTA",
        "WHY_NEEDED": "ticchiolatura e oídio da macieira no Veronese, com ensaio de Revysol — o caso IT-APPLE-DISEASE",
        "ROTAS": ["https://www.informatoreagrario.it/", "https://openpub.fmach.it/handle/10449/79717"],
    },
    {
        "VIDEO_ID": "yEQezPE7Wfw",
        "CANAL": "L'Informatore Agrario",
        "PUBLISHER": "L'Informatore Agrario",
        "IMPORTANCE": "MEDIA",
        "WHY_NEEDED": "ticchiolatura da macieira na Emilia-Romagna, ensaio do Consorzio agrario di Ravenna",
        "ROTAS": ["https://www.informatoreagrario.it/"],
    },
    {
        "VIDEO_ID": "yCR90mte0CM",
        "CANAL": "Viticoltura Riccardo Castaldi",
        "PUBLISHER": "Riccardo Castaldi (pessoa singular)",
        "IMPORTANCE": "MEDIA",
        "WHY_NEEDED": "sintomas foliares de flavescenza em 22 castas — observação de campo, não comunicação de marca",
        "ROTAS": ["https://www.youtube.com/@viticolturariccardocastaldi/about"],
    },
    {
        "VIDEO_ID": "ZmmFiPHNl2U",
        "CANAL": "Primoweb",
        "PUBLISHER": "Primoweb",
        "IMPORTANCE": "MEDIA",
        "WHY_NEEDED": "o vídeo LÊ um boletim de fase fenológica e mosca da azeitona — o caso IT-OLIVE-BACTROCERA",
        "ROTAS": ["https://primoweb.it/video-olivo-nuovi-notiziari-aipo-sul-nostro-canale-youtube-68/"],
    },
    {
        "VIDEO_ID": "Svsznb_EB50",
        "CANAL": "UPL Italia",
        "PUBLISHER": "UPL Italia",
        "IMPORTANCE": "BAIXA",
        "WHY_NEEDED": "bioestimulante para soja — comunicação de concorrente, ficha de produto é a mesma fala",
        "ROTAS": ["https://www.uplcorp.com/it/"],
    },
    {
        "VIDEO_ID": "gU5NdowIkO8",
        "CANAL": "FOGLIE WEBTV",
        "PUBLISHER": "FOGLIE.TV",
        "IMPORTANCE": "BAIXA",
        "WHY_NEEDED": "encontro técnico Sipcam sobre peronospora e oídio da vide, 2014 — valor histórico",
        "ROTAS": ["https://foglie.tv/?s=Sipcam"],
    },
]

# Rotas oficiais do YouTube que este arquivo mede sem precisar de chave nem de conta.
ROTAS_OFICIAIS = [
    ("robots.txt", "https://www.youtube.com/robots.txt"),
    ("developer-policies", "https://developers.google.com/youtube/terms/developer-policies"),
    ("captions.download (doc)", "https://developers.google.com/youtube/v3/docs/captions/download"),
]


def abrir(url, timeout=25):
    """GET simples. Devolve sempre um dicionário — erro também é medição."""
    pedido = urllib.request.Request(url, headers={
        "User-Agent": UA,
        "Accept-Language": "it-IT,it;q=0.9,en;q=0.6",
    })
    inicio = time.time()
    try:
        with urllib.request.urlopen(pedido, timeout=timeout) as r:
            corpo = r.read()
            return {
                "URL_PEDIDA": url,
                "URL_FINAL": r.geturl(),
                "HTTP": r.status,
                "CONTENT_TYPE": r.headers.get("Content-Type", "?"),
                "BYTES": len(corpo),
                "MS": int((time.time() - inicio) * 1000),
                "TEXTO": corpo.decode("utf-8", "replace"),
            }
    except urllib.error.HTTPError as e:
        corpo = b""
        try:
            corpo = e.read()
        except Exception:
            pass
        return {
            "URL_PEDIDA": url, "URL_FINAL": url, "HTTP": e.code,
            "CONTENT_TYPE": e.headers.get("Content-Type", "?") if e.headers else "?",
            "BYTES": len(corpo), "MS": int((time.time() - inicio) * 1000),
            "TEXTO": corpo.decode("utf-8", "replace"), "ERRO": f"HTTPError {e.code}",
        }
    except Exception as e:
        return {
            "URL_PEDIDA": url, "URL_FINAL": url, "HTTP": 0, "CONTENT_TYPE": "?",
            "BYTES": 0, "MS": int((time.time() - inicio) * 1000), "TEXTO": "",
            "ERRO": f"{type(e).__name__}: {e}",
        }


def titulo(html):
    m = re.search(r"<title[^>]*>(.*?)</title>", html, re.S | re.I)
    return re.sub(r"\s+", " ", m.group(1)).strip()[:160] if m else "NÃO SEI"


def texto_visivel(html):
    """Aproximação grosseira; serve para procurar palavra, não para preservar."""
    s = re.sub(r"(?is)<(script|style|noscript)[^>]*>.*?</\1>", " ", html)
    s = re.sub(r"(?s)<[^>]+>", " ", s)
    return re.sub(r"\s+", " ", s)


def medir_rotas():
    resultados = []
    for item in CENSO:
        medidas = []
        for url in item["ROTAS"]:
            r = abrir(url)
            html = r.pop("TEXTO", "")
            r["TITULO"] = titulo(html) if "html" in r.get("CONTENT_TYPE", "").lower() else "—"
            visivel = texto_visivel(html)
            r["PALAVRAS_VISIVEIS"] = len(visivel.split())
            r["AMOSTRA"] = visivel[:400]
            medidas.append(r)
            time.sleep(1.0)
        resultados.append({
            "VIDEO_ID": item["VIDEO_ID"],
            "CANAL": item["CANAL"],
            "PUBLISHER": item["PUBLISHER"],
            "MEDIDAS": medidas,
        })
        print(f"{item['VIDEO_ID']}  {item['PUBLISHER'][:38]:38}  " +
              "  ".join(f"{m['HTTP']}/{m['BYTES']}b" for m in medidas))
    return resultados


def medir_oficial():
    linhas = []
    for nome, url in ROTAS_OFICIAIS:
        r = abrir(url)
        html = r.pop("TEXTO", "")
        achados = {}
        for chave, agulha in [
            ("III.E.1.a", "download, import, backup, cache, or store copies"),
            ("III.I.7", "separate, isolate, or modify the audio or video components"),
            ("III.I.14", "use any technology other than YouTube API Services"),
            ("permission to edit", "permission to edit the video"),
            ("Disallow /api/", "Disallow: /api/"),
            ("Disallow /youtubei/", "Disallow: /youtubei/"),
            ("Disallow /get_video", "Disallow: /get_video"),
        ]:
            if agulha.lower() in html.lower():
                achados[chave] = "PRESENTE"
        r["CLAUSULAS_ENCONTRADAS"] = achados
        r["NOME"] = nome
        linhas.append(r)
        print(f"{nome:26} HTTP {r['HTTP']:3}  {r['BYTES']:7}b  {sorted(achados)}")
        time.sleep(1.0)
    return linhas


def main():
    modo = sys.argv[1] if len(sys.argv) > 1 else "tudo"
    os.makedirs(SAIDA, exist_ok=True)
    pacote = {
        "SOURCE_ID": "NÃO SEI — medição derivada; o dono do id é SENSOR-PILOT/MEDICAO",
        "DERIVADO_DE": "data/samples/SENSOR-PILOT/MEDICAO.json",
        "EVIDENCE_CLASS": "DERIVED_MEASUREMENT",
        "MEDIDO_EM": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "APIFY_RUNS": 0,
        "COST_USD": 0,
        "O_QUE_NAO_FOI_FEITO": [
            "nenhum byte de vídeo do YouTube foi baixado",
            "nenhum áudio foi separado de vídeo nenhum",
            "nenhuma legenda foi pedida ao YouTube",
            "nenhum login, cookie de conta ou CAPTCHA",
        ],
    }
    if modo in ("oficial", "tudo"):
        print("== ROTA OFICIAL DO YOUTUBE, LIDA AO VIVO ==")
        pacote["ROTA_OFICIAL"] = medir_oficial()
    if modo in ("rotas", "tudo", "censo"):
        print("== ROTAS ALTERNATIVAS, POR PUBLICADOR ==")
        pacote["ROTAS_ALTERNATIVAS"] = medir_rotas()
    destino = os.path.join(SAIDA, "MEDICAO-ROTAS.json")
    with open(destino, "w", encoding="utf-8") as f:
        json.dump(pacote, f, ensure_ascii=False, indent=1)
    print(f"\ngravado: {os.path.relpath(destino, RAIZ)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
