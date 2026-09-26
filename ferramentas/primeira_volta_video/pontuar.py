# -*- coding: utf-8 -*-
"""PRIMEIRA-VOLTA-VIDEO · que canais tem MAIS chance de render para Voci dal Campo / Intelligence Scientifica.

So com o que JA esta guardado (VIDEOS-GUARDADOS.json): titulo e descricao que cada video declara.
Nada se infere alem das palavras: e um indicio de rendimento, nao uma prova (a prova e a
transcricao, depois da volta).

Por video, sinais (listas abaixo, todas a vista):
  CULTURA   o video nomeia uma cultura
  PROBLEMA  nomeia uma praga/doenca/infestante ou «difesa»
  REGIAO    nomeia uma regiao/zona italiana
  VOZ       ha sinal de pessoa com papel tecnico (agronomo, ricercatore, prof., dott., intervista, ...)
  CURTO     dura <= 540 s (o baixador do freio filtra acima disto: SINTONIA_YT_DURACAO_MAX_S)
  LEGENDA_IT tem faixa de legenda em italiano (automatica ou nao)
  RECENTE   publicado nos 12 meses antes de 2026-09-20 (a data da pagina guardada)
Um video «util» = CULTURA + PROBLEMA + VOZ. Ordem dos canais: uteis recentes e curtos, depois
uteis, depois CULTURA+PROBLEMA, depois recencia. A ordem e mostrada com os numeros, nunca so o lugar.

    py ferramentas/primeira_volta_video/pontuar.py --universo=UNIVERSO-59.json --videos=VIDEOS-GUARDADOS.json --saida=PONTUACAO.json
"""
import json
import re
import sys
import unicodedata
from collections import defaultdict
from pathlib import Path

# ⚠️ «pero», «melo», «riso», «vite», «pesco» so como palavra inteira: sem o \b do fim casavam
# «peronospora»/«però», «melone», «risorse», «vitello» (medido na 2.a lista, 26/09).
CULTURAS = r"""vite\b|viti\b|vigneto|vigneti|viticol|uva\b|olivo|olivi|oliveto|olivicol|melo\b|meli\b|meleto|meleti|mele\b|
pero\b|peri\b|pereto|pereti|pericol|pomacee|pesco\b|pesche\b|pescheto|drupacee|
ciliegi|albicocc|susin|actinidia|kiwi|agrumi|limone|arancio|nocciol|noce|castagn|mandorl|frument|grano|cereal|orzo|oliv|
mais\b|riso\b|risi\b|risaia|risicol|soia|girasole|colza|barbabietol|pomodor|patat|orticol|ortaggi|ortofrutt|frutticol|insalat|lattuga|carciof|zucchin|melanzan|peperon|
fragol|piccoli frutti|mirtill|lampone|melone|cocomero|cavol|cipoll|aglio|legumi|foraggi|erba medica|prato|luppolo|tabacco|canapa|zafferano"""
PROBLEMAS = r"""peronospora|oidio|botrite|muffa grigia|flavescenza|legno nero|fitoplasm|mal dell.esca|esca della vite|cimice|
popillia|xylella|mosca dell|mosca olearia|bactrocera|ticchiolatura|carpocapsa|tignola|tignoletta|drosophila|suzukii|
afid|pidocch|cocciniglia|ragnetto|acar|tripid|nematod|elateridi|diabrotica|piralide|fusari|septoria|ruggine|brusone|
alternaria|marciume|batteriosi|virosi|virus|maculatura|cancro|colpo di fuoco|erwinia|psilla|fillossera|infestant|malerbe|
patogen|parassit|insett[io] dannos|difesa|fitosanitar|lotta integrata|difesa integrata|lotta biologica|
biocontroll|insetti utili|antagonist"""
REGIONI = r"""piemonte|valle d.aosta|lombardia|trentino|alto adige|sudtirol|veneto|friuli|liguria|emilia|romagna|toscana|umbria|
marche|lazio|abruzzo|molise|campania|puglia|basilicata|calabria|sicilia|sardegna|franciacorta|langhe|roero|monferrato|
chianti|montalcino|valpolicella|prosecco|conegliano|valdobbiadene|maremma|salento|pianura padana|val di non|valtellina|
oltrepo|irpinia|cilento|etna|capitanata|polesine|lomellina|vercelli|novara"""
VOZ = r"""agronom|dottore agronomo|dott\.|dr\.|prof\.|professor|ricercat|docente|tecnic[oai]|esperto|esperta|entomolog|
fitopatolog|patolog|intervista|ci spiega|spiega|parla|webinar|convegno|seminario|universit|crea|cnr|istituto"""


def _rx(s):
    # so as quebras de linha saem; os espacos DENTRO dos termos ficam («mosca delle olive»)
    return re.compile(r"\b(?:%s)" % s.replace("\n", ""), re.I)


RX = {"CULTURA": _rx(CULTURAS), "PROBLEMA": _rx(PROBLEMAS), "REGIAO": _rx(REGIONI), "VOZ": _rx(VOZ)}
DURACAO_MAX_S = 540
DESDE = "2025-09-20"


def _txt(v):
    t = "%s\n%s" % (v.get("TITULO") or "", v.get("DESCRICAO") or "")
    return unicodedata.normalize("NFC", t)


def sinais(v: dict, descricao_partilhada: bool = False) -> dict:
    """`descricao_partilhada`: a mesma descricao aparece em >= 3 videos do canal (a do EVENTO).
    Ai o que ela diz nao e desta pessoa: conta so o titulo (medido: as 5 entrevistas «Vite in
    Campo» partilham «si e parlato anche della peronospora» e sao sobre poda)."""
    t = (v.get("TITULO") or "") if descricao_partilhada else _txt(v)
    t = unicodedata.normalize("NFC", t)
    s = {k: bool(rx.search(t)) for k, rx in RX.items()}
    s["DESCRICAO_PARTILHADA"] = descricao_partilhada
    s["TERMOS"] = {k: sorted({m.group(0).lower() for m in rx.finditer(t)})[:6] for k, rx in RX.items()}
    d = v.get("DURACAO_S")
    s["CURTO"] = d is not None and int(d) <= DURACAO_MAX_S
    s["LEGENDA_IT"] = any((f.get("LINGUA") or "").startswith("it") for f in v.get("LEGENDAS") or [])
    s["RECENTE"] = (v.get("PUBLICADO") or "")[:10] >= DESDE
    s["UTIL"] = s["CULTURA"] and s["PROBLEMA"] and s["VOZ"]
    return s


def _chave_desc(v: dict) -> str:
    return " ".join((v.get("DESCRICAO") or "").split())[:400]


def partilhadas_por_canal(vids: list, minimo: int = 3) -> set:
    """{(SOURCE_ID, descricao)} das descricoes (nao vazias) repetidas em >= `minimo` videos do canal."""
    from collections import Counter
    c = Counter((v["SOURCE_ID"], _chave_desc(v)) for v in vids if v.get("ESTADO") == "LIDO" and _chave_desc(v))
    return {k for k, n in c.items() if n >= minimo}


def main(argv) -> int:
    arg = dict(a[2:].split("=", 1) for a in argv[1:] if a.startswith("--") and "=" in a)
    u = json.loads(Path(arg["universo"]).read_text(encoding="utf-8"))["FONTES"]
    vids = json.loads(Path(arg["videos"]).read_text(encoding="utf-8"))["VIDEOS"]
    por = defaultdict(list)
    partilhadas = partilhadas_por_canal(vids)
    for v in vids:
        if v.get("ESTADO") == "LIDO":
            p = (v["SOURCE_ID"], _chave_desc(v)) in partilhadas
            por[v["SOURCE_ID"]].append(dict(v, SINAIS=sinais(v, descricao_partilhada=p)))
    linhas = []
    for f in u:
        vs = por.get(f["SOURCE_ID"], [])
        c = lambda *ks: sum(1 for v in vs if all(v["SINAIS"][k] for k in ks))   # noqa: E731
        util = [v for v in vs if v["SINAIS"]["UTIL"]]
        linhas.append(dict(f, MEDIDO=bool(vs), VIDEOS=len(vs), CULTURA=c("CULTURA"), PROBLEMA=c("PROBLEMA"),
                           CULTURA_E_PROBLEMA=c("CULTURA", "PROBLEMA"), VOZ=c("VOZ"), UTIL=len(util),
                           UTIL_RECENTE_CURTO=c("UTIL", "RECENTE", "CURTO"), UTIL_E_REGIAO=c("UTIL", "REGIAO"),
                           CURTOS=c("CURTO"), LEGENDA_IT=c("LEGENDA_IT"), RECENTES=c("RECENTE"),
                           ULTIMO_VIDEO=max((v.get("PUBLICADO") or "")[:10] for v in vs) if vs else None,
                           EXEMPLOS=[{"VIDEO_ID": v["VIDEO_ID"], "TITULO": v["TITULO"], "PUBLICADO": (v.get("PUBLICADO") or "")[:10],
                                      "DURACAO_S": v.get("DURACAO_S"), "LEGENDA_IT": v["SINAIS"]["LEGENDA_IT"],
                                      "TERMOS": v["SINAIS"]["TERMOS"]}
                                     for v in sorted(util, key=lambda v: v.get("PUBLICADO") or "", reverse=True)[:5]]))
    chave = lambda l: (l["UTIL_RECENTE_CURTO"], l["UTIL"], l["CULTURA_E_PROBLEMA"], l["ULTIMO_VIDEO"] or "")  # noqa: E731
    medidas = sorted([l for l in linhas if l["MEDIDO"]], key=chave, reverse=True)
    for i, l in enumerate(medidas, 1):
        l["ORDEM"] = i
    nao = [l for l in linhas if not l["MEDIDO"]]
    Path(arg["saida"]).write_text(json.dumps({"DATASET": "PRIMEIRA-VOLTA-VIDEO-PONTUACAO", "DESDE": DESDE,
                                              "DURACAO_MAX_S": DURACAO_MAX_S, "MEDIDAS": medidas, "NAO_MEDIDAS": nao},
                                             ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print("%-3s %-10s %3s %3s %3s %3s %3s %3s %3s %3s %-10s %s" % ("#", "SID", "vid", "C+P", "voz", "UTL", "URC", "cur", "leg", "rec", "ultimo", "nome"))
    for l in medidas:
        print("%-3d %-10s %3d %3d %3d %3d %3d %3d %3d %3d %-10s %s" % (
            l["ORDEM"], l["SOURCE_ID"], l["VIDEOS"], l["CULTURA_E_PROBLEMA"], l["VOZ"], l["UTIL"],
            l["UTIL_RECENTE_CURTO"], l["CURTOS"], l["LEGENDA_IT"], l["RECENTES"], l["ULTIMO_VIDEO"], l["NOME"][:40]))
    print("NAO MEDIDAS (nada guardado):", len(nao))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
