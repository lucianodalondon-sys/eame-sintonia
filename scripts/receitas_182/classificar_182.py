# -*- coding: utf-8 -*-
"""RECEITAS-182 · passo 1: a FORMA real de cada fonte parada, sem rede.

    py scripts/receitas_182/classificar_182.py

Le EXTRACAO-182-V1.json (a ultima prova que o robo guardou: motivo da recusa, retrato da
entrada, bytes e endereco lidos, e o item tentado quando o motivo o traz). O robo NAO guardou
as paginas: a forma decide-se por regras declaradas abaixo, na ordem, a primeira que casa.
Quando a prova nao chega para a certeza, a classe diz PROVAVEL.

Escreve CLASSIFICACAO-182-V1.json (uma linha por fonte, com a regra que a classificou).
"""
import json
import re
from collections import Counter
from pathlib import Path
from urllib.parse import urlparse

AQUI = Path(__file__).resolve().parent
PUBLICACAO = re.compile(r"(news|notizi|comunicat|stampa|eventi|blog|articol|avvis|pubblicazion|newsletter|"
                        r"in-evidenza|rassegna|category/news)", re.I)
BOLETIM = re.compile(r"(bollettin|bollfenolog|monit_siccita|mappe-settimanali|previsioni-agrometeo)", re.I)
ANEXO = re.compile(r"(allegato\.aspx|\.pdf$|/download|bacheca)", re.I)
CMS_ORDEM = re.compile(r"(ordine[a-z-]*\.conaf\.it|federazione[a-z]*\.conaf\.it|agronomi[a-z]*\.it|"
                       r"agronomiforestali)", re.I)


def forma(f: dict) -> tuple[str, str]:
    p = f.get("PROVA") or {}
    m = p.get("MOTIVO") or (f.get("REASON") or "").split(":")[0]
    r = p.get("ENTRADA_RETRATO") or {}
    entrada = p.get("ENTRADA") or ((f.get("ACQUISITION") or {}).get("INDEX_URL")) or ""
    lidos = p.get("PAGINAS_LIDAS") or [{}]
    b = lidos[0].get("BYTES") or 0
    porque = p.get("PORQUE") or f.get("REASON") or ""
    host = urlparse(entrada).netloc.lower()
    if m == "REVISAO_PENDENTE":
        return "PASSOU_A_REGUA_ESPERA_LEITURA", "motivo REVISAO_PENDENTE: o reparo passou a regua; falta uma pessoa ler o item"
    if m == "ENTRADA_NAO_E_HTML":
        if b < 2000:
            return "JS_OU_VAZIA", "entrada nao-HTML com %d bytes" % b
        return "NAO_HTML_A_CONFIRMAR", ("entrada com %d bytes que o reparo diz nao comecar por '<' — "
                                        "PROVAVEL: BOM + quebra de linha antes do HTML (nao se ve sem os bytes)" % b)
    if b and b < 3000 and (r.get("LINKS") or 0) <= 10:
        return "JS_OU_VAZIA", "entrada com %d bytes e %s ligacoes: a pagina desenha-se no navegador" % (b, r.get("LINKS"))
    if ANEXO.search(porque) or ANEXO.search(entrada):
        return "LISTA_DE_ANEXOS_PDF", "o item/entrada e anexo (allegato/pdf/bacheca)"
    if BOLETIM.search(entrada):
        return "PAGINA_BOLETIM", "a entrada e a pagina de um boletim/mapa (%s)" % BOLETIM.search(entrada).group(0)
    if m == "ENTRADA_E_MATERIA":
        return "PAGINA_UNICA", "a entrada e ela propria um texto (%d em paragrafos): nao lista nada" % (r.get("PARAGRAPH_CHARACTERS") or 0)
    if CMS_ORDEM.search(host):
        return "SITE_DE_ORDEM_PROFISSIONAL", ("ordem/federacao de agronomos (%s): paginas fixas e avisos curtos — "
                                              "motivo %s" % (host, m))
    # daqui para baixo: a entrada TEM cara de lista de publicacoes?
    lista = bool(PUBLICACAO.search(urlparse(entrada).path))
    if m == "ITEM_NAO_E_MATERIA":
        corpo = [int(x) for x in re.findall(r"(\d+) em paragrafos", porque)]
        if any(c >= 800 for c in corpo):
            return "LISTA_CERTA_JUIZ_DIZ_CAPA", ("um item tentado tem %d letras em paragrafos e o juiz disse capa/nao sei "
                                                 "(menu grande) — regua, nao molde" % max(corpo))
        if "FAMILIA_E_MENU" in porque and lista:
            return "LISTA_MOLDE_ESCOLHEU_MENU", "a entrada e lista de publicacoes e o reparo gastou tentativas no menu do site"
        if "DUPLICADA" in porque:
            return "DUPLICADA_DE_OUTRA_FONTE", "o item achado ja e de outra fonte"
        if "FAMILIA_E_MENU" in porque:
            return "MENU_INSTITUCIONAL", "so familias de menu numa pagina que nao e lista"
        return "ITEM_CURTO_OU_NAO_ABRIU", "o item tentado nao tem corpo (ou deu erro)"
    if m == "SEM_FAMILIA_DE_ITENS":
        if lista or "seccao" in porque:
            return "LISTA_MOLDE_NAO_ACHOU", ("a entrada%s e lista de publicacoes e o reparo nao achou 2+ itens "
                                            "com o mesmo esqueleto" % (" (ou a seccao)" if not lista else ""))
        return "MENU_INSTITUCIONAL", "pagina sem familia de itens e sem cara de lista"
    if m == "FAMILIA_ESTATICA":
        return "MENU_INSTITUCIONAL", "so ha familias de paginas fixas"
    return "OUTRA", m


def main():
    d = json.loads((AQUI / "EXTRACAO-182-V1.json").read_text(encoding="utf-8"))
    linhas = []
    for f in d["FONTES"]:
        c, porque = forma(f)
        p = f.get("PROVA") or {}
        linhas.append({"SOURCE_ID": f["SOURCE_ID"], "FORMA": c, "REGRA": porque,
                       "MOTIVO_DO_ROBO": p.get("MOTIVO") or (f.get("REASON") or "").split(":")[0],
                       "ENTRADA": p.get("ENTRADA") or (f.get("ACQUISITION") or {}).get("INDEX_URL"),
                       "HOST": urlparse(p.get("ENTRADA") or (f.get("ACQUISITION") or {}).get("INDEX_URL") or "").netloc})
    cont = Counter(x["FORMA"] for x in linhas)
    out = {"DATASET": "CLASSIFICACAO-182-V1", "ORIGEM": "EXTRACAO-182-V1.json (vivo %s)" % d["VIVO_HEAD"],
           "TOTAL": len(linhas), "POR_FORMA": dict(cont.most_common()), "FONTES": linhas}
    (AQUI / "CLASSIFICACAO-182-V1.json").write_text(json.dumps(out, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    for k, v in cont.most_common():
        print("%4d  %s" % (v, k))
    print("total", len(linhas))


if __name__ == "__main__":
    main()
