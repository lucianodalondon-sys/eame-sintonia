#!/usr/bin/env python3
"""REROUTE-D56 · a LEITURA dos novos SIM — cada um lido pelo trecho, e marcado.

O replay (`replay_reroute_d56.py`) corre aqui com TODAS as reguas a promover (`REROUTE_PROMOVE` =
todos os universos com regua, SO dentro deste processo): e a amostra que foi lida ANTES de a regra 4
(so promove quem tem regua medida) existir, e e ela que a justifica.

    ROTULO     VERDADEIRO · FALSO · DISCUTIVEL
    QUEM LEU   o modelo (Claude), pelo trecho + titulo/URL. VALIDADO_POR_HUMANO = NAO.

Precisao ESTRITA conta DISCUTIVEL como falso; LARGA conta como verdadeiro. As duas saem.

    py provas/reroute_d56/leitura_novos_sim.py   -> LEITURA-NOVOS-SIM-D56.json
"""
from __future__ import annotations

import collections
import json
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
import replay_reroute_d56 as R  # noqa: E402

adm = R.adm
SAIDA = AQUI / "LEITURA-NOVOS-SIM-D56.json"
V, F, D = "VERDADEIRO", "FALSO", "DISCUTIVEL"

# chave = sha256[:12] do bruto | universo. Porque, em uma linha.
LEITURA = {
    "042a1c27d12a|T5": (D, "estudo de consumidores sobre rotulos compostaveis (Composting Consortium): e estudo, "
                           "mas de embalagem, nao de ciencia agronomica"),
    "0be2d204c98a|T1": (V, "boletim agrometeo ARPAV: «Fenologia: inolizione – inizio invaiatura», mosca da oliveira"),
    "0be2d204c98a|T2": (V, "boletim agrometeo ARPAV: previsao, temperatura, evapotranspiracao + fenologia"),
    "0c2723e66201|T1": (V, "boletim fitossanitario de Salerno: soglia di intervento, infestazione, citrinos"),
    "0c2723e66201|T2": (V, "boletim fitossanitario de Salerno: dados agrometeo + defesa integrada"),
    "0c2723e66201|T3": (V, "boletim fitossanitario de Salerno: pragas, armadilhas, afideos"),
    "0c2723e66201|T4": (V, "deroga temporanea + «etichetta del formulato commerciale autorizzato», D.Lgs 150/2012"),
    "1ae8fd198f05|T2": (V, "pera Conference: temperatura, seca, rega, geada na floracao — clima com ligacao a cultura"),
    "1ae8fd198f05|T5": (D, "so o intertitulo «Sperimentazione e ricerca» num artigo de comercio"),
    "1dcf9b087958|T4": (F, "premio de cantina: «riconosciuto dal Ministero» + «ogni singola etichetta» (marca)"),
    "3d3c1bc0e963|T1": (V, "boletim agrometeo ARPAV (zona 9): fenologia da oliveira"),
    "3d3c1bc0e963|T2": (V, "boletim agrometeo ARPAV (zona 9): previsao e evapotranspiracao"),
    "59da05274359|T1": (V, "boletim da mosca da oliveira APOL: soglia di intervento, trattamento fitosanitario"),
    "59da05274359|T2": (V, "boletim APOL: perturbacao e chuva que favorecem a mosca"),
    "59da05274359|T3": (V, "boletim APOL: armadilhas, insecto, adversidades"),
    "611ccec87e65|T5": (F, "consorcio do balsamico num dia de analise de alimentos: evento, nao ciencia agronomica"),
    "8a76f4ffef3f|T5": (F, "programa escolar: «Ministero dell'Istruzione, dell'Università e della Ricerca» (nome)"),
    "8c13500d4350|T1": (V, "boletim agrometeo ARPAV (zona 16): fenologia da oliveira"),
    "8c13500d4350|T2": (V, "boletim agrometeo ARPAV (zona 16): anticiclone, temperatura"),
    "995614babca7|T5": (F, "certificacoes/PPWR: «convegno», «rivista», «articolo» de uma revista de comercio"),
    "9d41e259ea98|T5": (D, "estudo da ETI sobre compras de banana no retalho: estudo de mercado, nao agronomico"),
    "a4399fac5c1f|T4": (F, "premio de cantina (outra versao da pagina): Ministero + etichetta de marca"),
    "ac2312c3c186|T5": (V, "Chianti Classico: projeto de investigacao vitivinicola de 16 anos, publicacao dos resultados"),
    "b218369bd0ce|T5": (F, "consorcio do balsamico num dia de analise de alimentos (outra versao)"),
    "def7e3219a46|T4": (F, "DdL Coltiva Italia: rotulagem do vinagre e politica (T12), nao registo fitossanitario"),
    "e612807928b5|T1": (V, "notiziario agrometeo Puglia: situazione fenologica, soglia di infestazione"),
    "e612807928b5|T2": (V, "notiziario agrometeo Puglia: saccatura, nuvolosidade, onda de calor"),
    "e612807928b5|T3": (V, "notiziario agrometeo Puglia: capturas, oziorrinco, peronospora"),
    "e612807928b5|T4": (F, "notiziario: «dosi di etichetta», dados do Ministero, «autorizzazione scritta» (copyright)"),
    "f88c89d73d6a|T1": (V, "boletim agrometeo ARPAV (zona 1): fenologia da oliveira"),
    "f88c89d73d6a|T2": (V, "boletim agrometeo ARPAV (zona 1): anticiclone, temperatura"),
    "fc54e7375f78|T4": (F, "DdL Coltiva Italia (outra versao): rotulagem do vinagre, politica"),
    # so no acervo inteiro (hipotese)
    "03aadc9a2d0f|T2": (V, "pera Conference (outra versao): clima com ligacao a cultura"),
    "03aadc9a2d0f|T5": (D, "pera Conference (outra versao): so o intertitulo «Sperimentazione e ricerca»"),
    "0704ca5347f2|T5": (F, "certificacoes/PPWR (outra versao): revista de comercio"),
    "0c2723e66201|T5": (F, "boletim de Salerno: «Pubblicazione di orientamento», «Articolo 12 del decreto»"),
    "2e488a8232ba|T2": (V, "Terre Etruria: temperaturas, rega, humidade do solo + mosca da oliveira"),
    "2e488a8232ba|T7": (V, "Terre Etruria: monitorizacao pelo Servico Agronomico da cooperativa (o trecho leva menu)"),
    "aee361a99812|T5": (F, "consorcio do balsamico num dia de analise de alimentos (outra versao)"),
    "dc0b2b288d37|T4": (F, "DdL Coltiva Italia (outra versao): politica"),
}


def ler():
    antes = adm.REROUTE_PROMOVE
    adm.REROUTE_PROMOVE = frozenset(adm.PERGUNTAS_DO_UNIVERSO)
    try:
        _r, novos, hnovos = R.replay()
    finally:
        adm.REROUTE_PROMOVE = antes
    vistos, linhas = set(), []
    for origem, lista in (("LIVRO", novos), ("ACERVO_INTEIRO", hnovos)):
        for n in lista:
            k = "%s|%s" % (n["SHA256"][:12], n["UNIVERSO"])
            if k in vistos:
                continue
            vistos.add(k)
            rot, porque = LEITURA.get(k, ("NAO_LIDO", "NAO SEI — fora da leitura"))
            linhas.append({"CHAVE": k, "AMOSTRA": origem, "SOURCE_ID": n["SOURCE_ID"],
                           "URL_OU_FICHEIRO": n["URL_OU_FICHEIRO"], "UNIVERSO": n["UNIVERSO"],
                           "PALAVRAS": n["PALAVRAS"], "TRECHO": (n["TRECHOS"] or [{}])[0].get("trecho"),
                           "ROTULO": rot, "PORQUE": porque,
                           "PROMOVE_HOJE": n["UNIVERSO"] in adm.REROUTE_PROMOVE})
    por_u = collections.defaultdict(collections.Counter)
    for l in linhas:
        por_u[l["UNIVERSO"]][l["ROTULO"]] += 1

    def precisao(sel):
        c = collections.Counter(l["ROTULO"] for l in sel)
        n = c[V] + c[F] + c[D]
        return {"N": n, V: c[V], F: c[F], D: c[D],
                "ESTRITA": round(c[V] / n, 3) if n else "NAO SEI",
                "LARGA": round((c[V] + c[D]) / n, 3) if n else "NAO SEI"}
    livro = [l for l in linhas if l["AMOSTRA"] == "LIVRO"]
    return {"DATASET": "LEITURA-NOVOS-SIM-D56-V1", "QUEM_LEU": "modelo (Claude)",
            "VALIDADO_POR_HUMANO": "NAO",
            "O_QUE_FOI_LIDO": ("os novos SIM do replay com TODAS as reguas a promover (antes da regra 4); "
                               "cada um pelo trecho do corpo e pelo titulo/URL"),
            "LIDOS": sum(1 for l in linhas if l["ROTULO"] != "NAO_LIDO"),
            "NAO_LIDOS": sum(1 for l in linhas if l["ROTULO"] == "NAO_LIDO"),
            "PRECISAO_LIVRO_TODAS_AS_REGUAS": precisao(livro),
            "PRECISAO_LIVRO_SO_O_QUE_PROMOVE_HOJE": precisao([l for l in livro if l["PROMOVE_HOJE"]]),
            "PRECISAO_TUDO_O_QUE_PROMOVE_HOJE": precisao([l for l in linhas if l["PROMOVE_HOJE"]]),
            "POR_UNIVERSO": {u: dict(c) for u, c in sorted(por_u.items(), key=lambda x: adm._ordem_no_atlas(x[0]))},
            "LINHAS": linhas}


def main():
    r = ler()
    SAIDA.write_text(json.dumps(r, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(json.dumps({k: r[k] for k in r if k != "LINHAS"}, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
