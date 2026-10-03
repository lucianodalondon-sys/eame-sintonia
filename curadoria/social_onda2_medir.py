"""SOC-ONDA2 · PASSO 1 — QUAIS DAS CANDIDATAS SOCIAIS TÊM IDENTIDADE PROVADA.

    py curadoria/social_onda2_medir.py [--json SAIDA]

Só LÊ. Sem rede, sem escrever em livro nenhum. Para cada candidata YouTube,
LinkedIn e Instagram sem SOURCE_ID, responde às perguntas que o QUALIFY vai
fazer, pela ordem em que o QUALIFY as faz:

  1. IDENTIDADE DA PLATAFORMA — o endereço diz QUEM é?
       YouTube   `/channel/UC…` (o channel_id) · `@handle`/`/user/`/`/c/` NÃO
                 (resolver pede a API; um UC escrito na NOTA é pista, não prova)
       LinkedIn  `/company/<slug>` (página de ORGANIZAÇÃO, D23; `/showcase/` o Scrap não lê)
       Instagram `instagram.com/<conta>` (perfil)
  2. LIGAÇÃO OFICIAL (D21 cond. 2 / D24) — o site da própria organização aponta
     para a conta (`ONDE_VIU = declarado no site oficial do dono: …` ou
     `DISCOVERED_FROM … CRAWL_LINK`). Nome parecido não conta.
  3. JÁ TEM DONO? — um canal que a casa já liga a um SOURCE_ID não recebe outro.
  4. TERRITÓRIO — pelo nome (regra do Atlas) e, se o nome não decide, pela
     herança D21 do site (que tem de ter SOURCE_ID e UM só território).
  5. FORA DE FOCO (D26) — veterinária / IZS.
  6. ROTA — que fase do Scrap colheria esta conta, e o que a matriz diz dela.

O resultado é um balde por candidata. PRONTA_PARA_QUALIFY quer dizer: o QUALIFY
tem tudo o que precisa para cunhar um SOURCE_ID sem fabricar nada.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
for _p in ("curadoria", "candidatas", "coleta", "leis", "regras", "pedido", "orquestrador", ""):
    q = str(RAIZ / _p) if _p else str(RAIZ)
    if q not in sys.path:
        sys.path.insert(0, q)

import atribuir_source_id as ASI  # noqa: E402
import rota_do_scrap_social as RSS  # noqa: E402
import rota_do_scrap_youtube as RSY  # noqa: E402

CANDIDATAS = RAIZ / "candidatas" / "FONTES-CANDIDATAS.json"
TIPOS = ("YOUTUBE", "LINKEDIN", "INSTAGRAM")

RE_IG = re.compile(r"instagram\.com/([A-Za-z0-9_.]+)/?(?:[?#]|$)", re.I)
RE_IG_REEL = re.compile(r"instagram\.com/(?:reel|p)/", re.I)
RE_UC_NOTA = re.compile(r"id estavel de plataforma:\s*(UC[A-Za-z0-9_-]{22})")
RE_VET = re.compile(r"veterinar|zooprofilatt|\bIZS\b|sanit[aà] animale", re.I)

# Fase do Scrap que colheria cada plataforma (leitura de coleta/scrap_colheita.FASES).
FASE_POR_TIPO = {"YOUTUBE": "canal-youtube", "LINKEDIN": "video-linkedin",
                 "INSTAGRAM": None}  # só o Reel por URL directa (D22); listar a conta = `janela`


def identidade(f: dict) -> tuple[str | None, str]:
    """→ (id nativo, como) ou (None, porquê não)."""
    tipo, url = f["TIPO"], f.get("URL") or ""
    if tipo == "YOUTUBE":
        uc = RSY.channel_id_da_url(url)
        if uc:
            return uc, "channel_id no endereco"
        uc = RSY.canal_resolvido(f["CANDIDATA_ID"], url)
        if uc:
            return uc, "channel_id resolvido pela API oficial (SOC4, youtube.channel.resolve)"
        m = RE_UC_NOTA.search(f.get("NOTA") or "")
        if m:
            return None, "HANDLE_COM_UC_NA_NOTA:%s" % m.group(1)
        return None, "HANDLE_SEM_UC"
    if tipo == "LINKEDIN":
        slug, porque = RSS.slug_linkedin(url)
        return (slug, "pagina de organizacao (/company/)") if slug else (None, porque)
    if tipo == "INSTAGRAM":
        if RE_IG_REEL.search(url):
            return None, "E_UM_POST_NAO_UMA_CONTA"
        m = RE_IG.search(url)
        return (m.group(1).lower(), "perfil") if m else (None, "URL_INSTAGRAM_ILEGIVEL")
    return None, "TIPO_FORA"


def ja_tem_dono(f: dict, nativo: str | None, tabela, livro, alloc, mjs) -> list[str]:
    if f["TIPO"] == "YOUTUBE" and nativo:
        return RSY.canal_conhecido(nativo, tabela=tabela, livro=livro, alloc=alloc, mjs=mjs)
    if f["TIPO"] == "LINKEDIN" and nativo:
        return RSS.pagina_conhecida(nativo, tabela=tabela, livro=livro, alloc=alloc)
    # IG: a casa guarda a conta pelo URL da ACQUISITION (perfil).
    achados = set()
    if nativo:
        for c in (tabela.get("FONTES") or []) + (livro.get("FONTES") or []):
            s = json.dumps(c.get("ACQUISITION") or {}).lower()
            if nativo in s and ("linkedin" in s or "instagram" in s):
                achados.add(c["SOURCE_ID"])
    return sorted(achados)


def medir() -> list[dict]:
    doc = json.loads(CANDIDATAS.read_text(encoding="utf-8"))
    tabela, livro = RSY._ler(RSY.TABELA), RSY._ler(RSY.LIVRO)
    alloc = RSY._ler(RSY.ALLOCATION)
    mjs = RSY.CONTRATOS_MJS.read_text(encoding="utf-8") if RSY.CONTRATOS_MJS.exists() else ""
    atlas = RSY.ATLAS.read_text(encoding="utf-8") if RSY.ATLAS.exists() else ""
    import scrap_colheita as sc
    import scrap_capacidades as cap
    import social_matriz as mz

    out = []
    for f in doc["CANDIDATAS"]:
        if f.get("TIPO") not in TIPOS or f.get("SOURCE_ID"):
            continue
        nativo, como = identidade(f)
        pagina, ligacao = RSY.ligacao_oficial(f)
        donos = ja_tem_dono(f, nativo, tabela, livro, alloc, mjs)
        terr, porque = ASI.territorio_de({"NOME": f.get("NOME", ""), "URL": f.get("URL", ""),
                                          "CONTENT_VALUE_TYPE": []})
        via = "NOME" if terr != "NAO SEI" else None
        prova_d21 = None
        if terr == "NAO SEI":
            t2, prova_d21 = RSY.heranca_do_site(f, tabela=tabela, livro=livro, atlas_texto=atlas)
            if t2:
                terr, via = t2, "D21"
        fase = FASE_POR_TIPO[f["TIPO"]]
        decisao = None
        if fase:
            linha = sc.FASES[fase]
            decisao = mz.decisao(linha[0], cap.da_matriz(linha[1]) or "").get("DECISAO")
        vet = bool(RE_VET.search("%s %s" % (f.get("NOME", ""), f.get("URL", ""))))

        if vet:
            balde = "FORA_DE_FOCO_D26"
        elif not nativo:
            balde = "SEM_IDENTIDADE:" + como.split(":")[0]
        elif not pagina:
            balde = "SEM_LIGACAO_OFICIAL"
        elif len(donos) > 1:
            balde = "COLISAO_DE_DONO"
        elif donos:
            balde = "JA_E_FONTE"
        elif terr == "NAO SEI":
            balde = "TERRITORIO_NAO_SEI"
        elif not fase:
            balde = "SEM_ROTA_PARA_LISTAR"
        elif decisao != "ALLOWED":
            balde = "ROTA_NAO_PERMITIDA"
        else:
            balde = "PRONTA_PARA_QUALIFY"
        out.append({
            "CANDIDATA_ID": f["CANDIDATA_ID"], "TIPO": f["TIPO"], "ESTADO": f.get("ESTADO"),
            "NOME": f.get("NOME", "")[:90], "URL": f.get("URL"),
            "NATIVO": nativo, "IDENTIDADE": como, "LIGACAO_OFICIAL": ligacao, "SITE": pagina,
            "JA_E_FONTE": donos, "TERRITORIO": terr, "TERRITORIO_VIA": via,
            "D21": prova_d21 if via == "D21" else (prova_d21 or {}).get("PORQUE"),
            "FASE": fase, "MATRIZ": decisao, "BALDE": balde,
        })
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--json")
    a = ap.parse_args()
    linhas = medir()
    print("TOTAL", len(linhas), dict(Counter(l["TIPO"] for l in linhas)))
    for t in TIPOS:
        c = Counter(l["BALDE"] for l in linhas if l["TIPO"] == t)
        print(t, dict(c.most_common()))
    print("TERRITORIO das PRONTAS", dict(Counter((l["TIPO"], l["TERRITORIO"], l["TERRITORIO_VIA"])
                                                for l in linhas if l["BALDE"] == "PRONTA_PARA_QUALIFY")))
    if a.json:
        Path(a.json).write_text(json.dumps({"DATASET": "SOC-ONDA2-IDENTIDADE-V1",
                                            "LINHAS": linhas}, ensure_ascii=False, indent=1),
                                encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
