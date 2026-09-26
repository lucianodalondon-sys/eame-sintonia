# -*- coding: utf-8 -*-
"""FALA-DOS-VIDEOS · o que ja ha de fala guardada nos 737 videos, e quanto custa transcrever os 50 mais promissores.

Sem rede. Le VIDEOS-GUARDADOS.json (as 612 paginas /watch) e as contagens da Sala feitas a parte
(so leitura, no relatorio). Escolhe ate `--n` videos (omissao 50) nos canais TECNICOS, com teto por
canal, e calcula o custo de cada um:

  PEDIDOS (freio D38/D41, um video por onda; youtube.com e googlevideo.com no MESMO balde):
    youtube.com     3 (pagina, player, API interna) — medido pela bancada do freio (servidor local, yt-dlp real)
    googlevideo.com ceil(MB / 50) com --http-chunk-size 50M; MB = duracao x BITRATE_KBPS / 8 / 1000
    CABE            3 + fatias <= 5 (teto por dominio na onda). Nao cabe = nao se corre com o freio de hoje.
  GPU (faster-whisper «small», GTX 1080): duracao / 34.07 — medido a 14/09 sobre 460,9 s de audio real
    (CPU: / 4.84). ⚠️ o texto da GPU nao e igual ao da CPU (4 de 6 pecas diferiam); qual esta certo: NAO MEDIDO.

⚠️ BITRATE_KBPS e uma HIPOTESE (128 kbit/s, o m4a 140 do YouTube; o opus 251 anda por 130-160).
O tamanho real so se sabe no pedido. Por isso cada video leva tambem o pior caso (160 kbit/s).

    py ferramentas/primeira_volta_video/fala_dos_videos.py --videos=VIDEOS-GUARDADOS.json --saida=FALA-50.json [--n=50] [--por-canal=10]
"""
import json
import math
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
import pontuar as P   # noqa: E402

# Os canais tecnicos (a missao: CRPV, CONAF, Condifesa, consorzi, universidades; + extensao regional e
# imprensa tecnica). CNR fica de fora: fechado pela coordenacao (10:13). Os 9 canais de pesquisa
# (IT-T5-042..050, IT-T7-016/018) so tem registos de falha 429 na Sala: sem titulo, sem duracao.
TECNICOS = {
    "IT-T5-040": "CRPV (centro de pesquisa)", "IT-T7-026": "CONAF (ordem dos agronomos)",
    "IT-T8-006": "L'Informatore Agrario (entrevistas Condifesa/universidades)", "IT-T8-004": "Terra e Vita (imprensa tecnica)",
    "IT-T12-008": "ASSAM/AMAP Marche (extensao regional)", "IT-T12-007": "ARSAC Calabria (extensao regional)",
    "IT-T12-011": "Pianeta PSR (Rete Rurale/CREA)", "IT-T7-035": "Accademia dei Georgofili",
    "IT-T5-038": "UNINA Agraria (universidade)", "IT-T9-014": "Conserve Italia (cooperativa, tecnicos)",
    "IT-T9-016": "Consorzi Agrari d'Italia (rede tecnica)", "IT-T7-023": "ANBI (consorzi di bonifica)",
    "IT-T7-020": "Consorzio di Bonifica Est Ticino Villoresi", "IT-T7-039": "Consorzio di Bonifica Piave",
    "IT-T7-034": "Consorzio Brunello (annata agronomica)", "IT-T7-032": "Consorzio Chianti Classico",
    "IT-T7-015": "Consorzio Vini d'Abruzzo", "IT-T7-036": "Consorzio Prosecco DOC", "IT-T7-037": "Consorzio Valpolicella",
    "IT-T12-012": "Regione Piemonte", "IT-T12-014": "Regione Toscana", "IT-T12-010": "Regione Molise",
    "IT-T12-016": "Regione Valle d'Aosta", "IT-T9-017": "Koppert (tecnicos; concorrente T9)",
}
FORMATO_LONGO = re.compile(r"webinar|convegno|seminario|incontro tecnico|giornata tecnica|corso|lezione|workshop", re.I)
NAO_TECNICO = re.compile(r"visita virtuale|mostra|voucher|ferroviar|scuola|festival|premio|spot\b|trailer|auguri|natale|"
                         r"concerto|inaugurazione|cerimonia|tg\b|highlights|promo\b|stati generali|corso di laurea|"
                         r"laurea magistrale|femminicidio|comunita del mare|comunità del mare|biennale|cinema|"
                         r"portrait|free online course|eccellenza autentica|grandi emozioni|ricavi, costi", re.I)
BITRATE_KBPS, BITRATE_PIOR = 128, 160
FATIA_MB, TETO = 50, 5
GPU_X, CPU_X = 34.07, 4.84


def custo(dur_s: int, kbps: int = BITRATE_KBPS) -> dict:
    mb = dur_s * kbps / 8 / 1000
    fatias = max(1, math.ceil(mb / FATIA_MB))
    return {"MB": round(mb, 1), "YOUTUBE_COM": 3, "GOOGLEVIDEO_COM": fatias, "BALDE": 3 + fatias,
            "CABE_NO_TETO": 3 + fatias <= TETO, "GPU_S": round(dur_s / GPU_X, 1), "CPU_S": round(dur_s / CPU_X, 1)}


def promessa(v: dict, s: dict) -> tuple:
    t = "%s %s" % (v.get("TITULO") or "", "" if s["DESCRICAO_PARTILHADA"] else (v.get("DESCRICAO") or ""))
    pontos = 3 * s["PROBLEMA"] + 2 * s["CULTURA"] + 2 * s["VOZ"] + 1 * s["RECENTE"] + 1 * bool(FORMATO_LONGO.search(t))
    return pontos, bool(NAO_TECNICO.search(v.get("TITULO") or ""))


def voltas_do_maestro(xs: list) -> list:
    """O maestro aceita UM video por fonte em cada corrida: a volta k leva o k-esimo video de cada canal."""
    por = defaultdict(list)
    for x in xs:
        por[x["SOURCE_ID"]].append(x)
    k = max((len(v) for v in por.values()), default=0)
    return [[por[s][i] for s in sorted(por) if i < len(por[s])] for i in range(k)]


def comandos(voltas: list) -> str:
    out = ["# FALA-DOS-VIDEOS · uma volta de cada vez, pasta nova para cada; depois do lote 3 e das voltas 1 e 2.",
           "# Antes de cada volta: py superficie/rede.py --portao-de-egresso IT", ""]
    for i, v in enumerate(voltas, 1):
        dmax = max(x["DURACAO_S"] for x in v)
        lim = max(540, int(math.ceil(dmax / 60.0) * 60))
        out.append("# VOLTA F%02d: %d videos, %d s de audio, o maior %d s" % (i, len(v), sum(x["DURACAO_S"] for x in v), dmax))
        out.append("SINTONIA_YT_DURACAO_MAX_S=%d SINTONIA_ASR_DEVICE=GPU py ferramentas/maestro_social/maestro_social.py "
                   "--correr --autorizado-pelo-dono --canario --saida=<pasta F%02d> --fontes=%s --videos=%s" % (
                       lim, i, ",".join(x["SOURCE_ID"] for x in v), ",".join("%s:%s" % (x["SOURCE_ID"], x["VIDEO_ID"]) for x in v)))
        out.append("")
    return "\n".join(out)


def main(argv) -> int:
    arg = dict(a[2:].split("=", 1) for a in argv[1:] if a.startswith("--") and "=" in a)
    n, por_canal = int(arg.get("n", 50)), int(arg.get("por-canal", 10))
    vids = [v for v in json.loads(Path(arg["videos"]).read_text(encoding="utf-8"))["VIDEOS"] if v.get("ESTADO") == "LIDO"]
    part = P.partilhadas_por_canal(vids)
    cands = []
    for v in vids:
        if v["SOURCE_ID"] not in TECNICOS or not v.get("DURACAO_S"):
            continue
        s = P.sinais(v, descricao_partilhada=(v["SOURCE_ID"], P._chave_desc(v)) in part)
        pts, fora = promessa(v, s)
        longo = bool(FORMATO_LONGO.search("%s %s" % (v.get("TITULO") or "", v.get("DESCRICAO") or "")))
        # entra: problema; ou cultura + (voz OU formato de palestra). Cultura sozinha e promocao, nao fala tecnica.
        if fora or not (s["PROBLEMA"] or (s["CULTURA"] and (s["VOZ"] or longo))):
            continue
        c = custo(int(v["DURACAO_S"]))
        cands.append({"SOURCE_ID": v["SOURCE_ID"], "CANAL": TECNICOS[v["SOURCE_ID"]], "VIDEO_ID": v["VIDEO_ID"],
                      "TITULO": v["TITULO"], "PUBLICADO": (v.get("PUBLICADO") or "")[:10], "DURACAO_S": int(v["DURACAO_S"]),
                      "LEGENDA_IT": s["LEGENDA_IT"], "PONTOS": pts,
                      "SINAIS": {k: s[k] for k in ("CULTURA", "PROBLEMA", "VOZ", "REGIAO", "RECENTE", "DESCRICAO_PARTILHADA")},
                      "TERMOS": s["TERMOS"], "CUSTO": c, "CUSTO_PIOR_160KBPS": custo(int(v["DURACAO_S"]), BITRATE_PIOR)})
    cands.sort(key=lambda x: (x["PONTOS"], x["CUSTO"]["CABE_NO_TETO"], x["PUBLICADO"]), reverse=True)
    escolhidos, conta = [], Counter()
    for x in cands:
        if len(escolhidos) >= n:
            break
        if conta[x["SOURCE_ID"]] >= por_canal:
            continue
        conta[x["SOURCE_ID"]] += 1
        escolhidos.append(x)
    # os que ja vao nas voltas 1 e 2 (VOLTA-1.tsv, VOLTA-2.tsv ao lado): contam nos 50, nao se pedem outra vez
    ja = {}
    for nome in ("VOLTA-1.tsv", "VOLTA-2.tsv"):
        f = AQUI / nome
        if f.exists():
            linhas = f.read_text(encoding="utf-8").splitlines()
            i = linhas[0].split("\t").index("VIDEO_ID")
            ja.update({l.split("\t")[i]: nome[:-4] for l in linhas[1:] if l.strip()})
    for x in escolhidos:
        x["JA_EM"] = ja.get(x["VIDEO_ID"])
    cabe = [x for x in escolhidos if x["CUSTO"]["CABE_NO_TETO"] and not x["JA_EM"]]
    tot = lambda xs, k: sum(x["CUSTO"][k] for x in xs)   # noqa: E731
    resumo = {
        "CANDIDATOS": len(cands), "ESCOLHIDOS": len(escolhidos), "POR_CANAL": dict(conta),
        "JA_NAS_VOLTAS_1_2": sum(1 for x in escolhidos if x["JA_EM"]),
        "A_PEDIR_NA_FALA": len(cabe),
        "NAO_CABEM_128": sum(1 for x in escolhidos if not x["CUSTO"]["CABE_NO_TETO"]),
        "NAO_CABEM_160": sum(1 for x in escolhidos if not x["CUSTO_PIOR_160KBPS"]["CABE_NO_TETO"]),
        "AUDIO_S": sum(x["DURACAO_S"] for x in escolhidos), "AUDIO_S_OS_QUE_CABEM": sum(x["DURACAO_S"] for x in cabe),
        "PEDIDOS_YOUTUBE_COM_OS_QUE_CABEM": tot(cabe, "YOUTUBE_COM"), "PEDIDOS_GOOGLEVIDEO_OS_QUE_CABEM": tot(cabe, "GOOGLEVIDEO_COM"),
        "GPU_S_OS_QUE_CABEM": round(tot(cabe, "GPU_S"), 1), "CPU_S_OS_QUE_CABEM": round(tot(cabe, "CPU_S"), 1),
        "DURACAO_MAX_S_OS_QUE_CABEM": max((x["DURACAO_S"] for x in cabe), default=0),
        "VOLTAS_MINIMAS": max(conta.values()) if conta else 0,
    }
    voltas = voltas_do_maestro(cabe)
    resumo["VOLTAS"] = len(voltas)
    Path(arg["saida"]).with_name("VOLTAS-FALA.txt").write_text(comandos(voltas), encoding="utf-8")
    Path(arg["saida"]).write_text(json.dumps({"DATASET": "FALA-DOS-VIDEOS-50", "BITRATE_KBPS_HIPOTESE": BITRATE_KBPS,
                                              "GPU_X_MEDIDO_14_09": GPU_X, "RESUMO": resumo, "VIDEOS": escolhidos},
                                             ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(json.dumps(resumo, ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
