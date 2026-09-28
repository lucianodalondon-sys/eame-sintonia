# -*- coding: utf-8 -*-
"""FEED-LIGADO · liga FEED_DISCOVERY nas linhas da tabela do coletor, pela porta canonica dos contratos.

    py regras/ligar_feeds.py                                   # SECO: mostra o que mudaria, nao escreve
    py regras/ligar_feeds.py --conferir-feeds=<pasta>          # + le <pasta>/<SOURCE_ID>/CORPO.bin (a medida
                                                               #   com rede) pelo MOTOR VERDADEIRO
    py regras/ligar_feeds.py --aplicar [--tabela=<ficheiro>]   # escreve a tabela (tmp + rename)
    py regras/ligar_feeds.py --desfazer [--tabela=<ficheiro>]  # repoe a ACQUISITION_ANTERIOR de cada linha ligada

ONDE VIVE O CONTRATO EXECUTAVEL (medido nesta arvore, 27/09). O coletor so colhe quem esta em
`CONTRACTS` de `regras/italy_contracts.mjs` (o dono do contrato). As fontes do Curator la entram por UMA
linha em `regras/italy_contracts_onboarded.json`, expandida por `contratoGenerico()`.
`curadoria/italy_contracts_curator.json` NAO e lido pelo coletor: e o livro do Curator, de onde a ponte
(`curadoria/onboardar_rotas_provadas.py`) copia a linha quando o portao e o canario deixam.

    ESTE FICHEIRO SO TROCA A AQUISICAO DE UMA LINHA QUE JA EXISTE. NAO CRIA LINHA.

Criar a linha seria contratar uma fonte sem o portao (ELIGIBLE) e sem o canario da rota — o atalho que a
ponte existe para impedir. Fonte do pacote sem linha na tabela sai com `SEM_LINHA_NA_TABELA` e fica como
esta.

A LINHA LIGADA:
  ACQUISITION = {STRATEGY: FEED_DISCOVERY, FEED_URL: <medido>, INDEX_URL: <o de antes>}
    · o INDEX_URL fica porque a regra V1 da capa (`coleta/retrato_html.mjs`, `admissao/admissao.py`) e o
      plano da onda (`onda_web.py`, dominio por INDEX_URL) o leem. O coletor NAO o pede: o feed substitui
      o indice (robots + feed + ate 3 materias = 5, D38).
    · o LINK_PATTERN antigo NAO passa: era o filtro para achar materias no meio dos href de uma pagina; o
      feed ja so lista publicacoes, e o molde generico (`news|notizie|...`) recusaria a morada de um post
      WordPress (`/2026/09/16/titolo/`) — EMPTY_LIST por construcao. O motor continua a tirar o que nao e
      do proprio site, paginacao e feeds de comentarios.
  FEED_LIGADO = {ACQUISITION_ANTERIOR, FEED_URL, PACOTE, EM} — o caminho de volta (`--desfazer`).

A TABELA E LIVRO VIVO na producao (o supervisor do bot escreve nela a cada volta): este ficheiro NAO e
corrido contra a tabela desta arvore; quem instala e o coordenador, com o comando de FEED-LIGADO.md.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
TABELA = RAIZ / "regras" / "italy_contracts_onboarded.json"
PACOTE = RAIZ / "regras" / "FEED-LIGADO-PACOTE.json"


def _json(p: Path) -> dict:
    return json.loads(Path(p).read_text(encoding="utf-8"))


def aquisicao_ligada(anterior: dict, feed_url: str) -> dict:
    aq = {"STRATEGY": "FEED_DISCOVERY", "FEED_URL": feed_url}
    if anterior.get("INDEX_URL"):
        aq["INDEX_URL"] = anterior["INDEX_URL"]
    return aq


def plano(tabela: dict, pacote: dict) -> list[dict]:
    """Uma decisao por fonte do pacote. Puro: nao le disco nem rede."""
    linhas = {l.get("SOURCE_ID"): l for l in tabela.get("FONTES", [])}
    fora = []
    for sid, p in sorted(pacote["FEEDS"].items()):
        d = {"SOURCE_ID": sid, "FEED_URL": p["FEED_URL"]}
        l = linhas.get(sid)
        aq = (l or {}).get("ACQUISITION") or {}
        if not p.get("LIGAR"):
            d.update(DECISAO="NAO_LIGAR", PORQUE=p.get("PORQUE", "o pacote nao a liga"))
        elif l is None:
            d.update(DECISAO="SEM_LINHA_NA_TABELA",
                     PORQUE="sem contrato executavel no coletor; nao se cria linha aqui — entra pela ponte "
                            "(curadoria/onboardar_rotas_provadas.py: portao ELIGIBLE + canario da rota)")
        elif l.get("ESTADO_CATALOGO") == "RETIRADA_POR_DECISAO":
            d.update(DECISAO="RETIRADA", PORQUE="a linha esta RETIRADA_POR_DECISAO; nao se liga")
        elif str(l.get("OUTPUT_TYPE", "")).upper() != "HTML":
            d.update(DECISAO="NAO_E_HTML", PORQUE=f"OUTPUT_TYPE {l.get('OUTPUT_TYPE')}: o feed so serve a materia HTML")
        elif aq.get("STRATEGY") == "FEED_DISCOVERY" and aq.get("FEED_URL") == p["FEED_URL"]:
            d.update(DECISAO="JA_LIGADA", PORQUE="a linha ja le este feed")
        elif aq.get("STRATEGY") != "HTML_LINK_DISCOVERY":
            d.update(DECISAO="ESTRATEGIA_INESPERADA",
                     PORQUE=f"a linha usa {aq.get('STRATEGY')}; so se troca HTML_LINK_DISCOVERY por feed")
        else:
            d.update(DECISAO="LIGAR", ANTES=aq, DEPOIS=aquisicao_ligada(aq, p["FEED_URL"]))
        fora.append(d)
    return fora


def aplicar(tabela: dict, decisoes: list[dict], pacote_nome: str, em: str) -> int:
    linhas = {l.get("SOURCE_ID"): l for l in tabela.get("FONTES", [])}
    n = 0
    for d in decisoes:
        if d["DECISAO"] != "LIGAR":
            continue
        l = linhas[d["SOURCE_ID"]]
        l["FEED_LIGADO"] = {"ACQUISITION_ANTERIOR": d["ANTES"], "FEED_URL": d["FEED_URL"],
                            "PACOTE": pacote_nome, "EM": em}
        l["ACQUISITION"] = d["DEPOIS"]
        n += 1
    return n


def desfazer(tabela: dict) -> list[str]:
    feitas = []
    for l in tabela.get("FONTES", []):
        f = l.get("FEED_LIGADO")
        if f and (l.get("ACQUISITION") or {}).get("STRATEGY") == "FEED_DISCOVERY":
            l["ACQUISITION"] = f["ACQUISITION_ANTERIOR"]
            del l["FEED_LIGADO"]
            feitas.append(l["SOURCE_ID"])
    return feitas


def escrever(tabela: dict, caminho: Path) -> None:
    # A forma da casa (indent=1, UTF-8 cru, fim de linha no fim): um diff so mostra as linhas mudadas.
    tmp = Path(str(caminho) + ".tmp")
    tmp.write_text(json.dumps(tabela, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    os.replace(tmp, caminho)


def conferir(decisoes: list[dict], pasta: str) -> None:
    """Le os corpos da medida com rede pelo MOTOR VERDADEIRO (itensDoFeed + os filtros do FEED_DISCOVERY) e
    calcula a PREVISAO de documentos por dia, com as datas de publicacao que o proprio feed declara.
    Sem corpo na pasta: NAO SEI para aquela fonte — nunca um numero inventado.

    A conta (por dominio, teto de 5 em 24 h; D40 = 3 materias a pedir):
      referencia   = a hora em que o corpo foi gravado (mtime do CORPO.bin = a hora do pedido)
      C7, S7       = itens publicados nos 7 dias antes da referencia, COM e SEM texto completo no feed
      ANTES/dia    = min(3, (C7 + S7) / 7)      o indice da o mesmo que o feed, e cada materia e 1 pedido
      DEPOIS/dia   = C7 / 7 + min(3, S7 / 7)    o item com corpo nao pede nada; o sem corpo continua no teto
      1.a volta    = C + min(3, S)              o que o feed traz hoje (base; nao e ritmo)
    ⚠️ ANTES e um TECTO do indice: supoe que a pagina de indice anuncia os mesmos itens que o feed."""
    for d in decisoes:
        corpo = Path(pasta) / d["SOURCE_ID"] / "CORPO.bin"
        if not corpo.exists():
            d["CONFERIDO"] = {"ESTADO": "NAO SEI", "PORQUE": f"{corpo} nao existe"}
            continue
        ref = datetime.fromtimestamp(corpo.stat().st_mtime, timezone.utc).isoformat()
        js = ("import('./regras/motor_de_rota.mjs').then(async m=>{const fs=await import('node:fs');"
              "const xml=fs.readFileSync(process.argv[1]);const u=process.argv[2];const ref=Date.parse(process.argv[3]);"
              "const aq={STRATEGY:'FEED_DISCOVERY',FEED_URL:u};const buscar=async()=>({status:200,buf:xml});"
              # a 1.a volta, com o classificador do coletor (tudo NOVO): o que entra sem pedido e o que se pede
              "const a=await m.alvosDoContrato('X',{OUTPUT_TYPE:'HTML',ACQUISITION:aq},{buscar,classificar:()=>'NOVO'});"
              "if(a.erro){console.log(JSON.stringify({ERRO:a.erro}));return}"
              # todos os itens que passam os filtros do motor (sem o corte D40), para o ritmo de publicacao
              "const t=await m.alvosDoContrato('X',{OUTPUT_TYPE:'HTML',ACQUISITION:{...aq,MAX_TARGETS:1e6}},{buscar});"
              "const passa=new Set(t.map(y=>y.url));const it=m.itensDoFeed(xml.toString('utf8'),u).filter(x=>passa.has(x.url));"
              "const d7=x=>x.publicado&&Date.parse(x.publicado)<=ref&&Date.parse(x.publicado)>ref-7*864e5;"
              "const C=it.filter(x=>x.corpo).length,S=it.length-C;"
              "const C7=it.filter(x=>x.corpo&&d7(x)).length,S7=it.filter(x=>!x.corpo&&d7(x)).length;"
              "const r2=n=>Math.round(n*100)/100;"
              "console.log(JSON.stringify({ITENS_NO_FEED:m.itensDoFeed(xml.toString('utf8'),u).length,ITENS_QUE_PASSAM:it.length,"
              "COM_CORPO:C,SEM_CORPO:S,COM_DATA:it.filter(x=>x.publicado).length,"
              "PRIMEIRA_VOLTA:{SEM_PEDIDO_BODY_FROM_FEED:a.D40.CORPO_DO_FEED,A_PEDIR:a.D40.A_PEDIR},"
              "PUBLICADOS_7D:{COM_CORPO:C7,SEM_CORPO:S7},"
              "PREVISAO:{DOC_DIA_ANTES:r2(Math.min(3,(C7+S7)/7)),DOC_DIA_DEPOIS:r2(C7/7+Math.min(3,S7/7)),"
              "DOC_1A_VOLTA_ANTES:Math.min(3,C+S),DOC_1A_VOLTA_DEPOIS:C+Math.min(3,S)}}))})")
        r = subprocess.run(["node", "-e", js, str(corpo), d["FEED_URL"], ref], cwd=RAIZ, capture_output=True,
                           text=True, encoding="utf-8", timeout=120)
        try:
            d["CONFERIDO"] = dict(json.loads(r.stdout.strip().splitlines()[-1]), REFERENCIA=ref)
        except (ValueError, IndexError):
            d["CONFERIDO"] = {"ESTADO": "NAO SEI", "PORQUE": (r.stderr or r.stdout)[-300:]}


def previsao(decisoes: list[dict]) -> dict:
    """A soma so das fontes que ficam ligadas e que se conferiram; as outras contam-se como NAO SEI."""
    ps = [d["CONFERIDO"]["PREVISAO"] for d in decisoes
          if d["DECISAO"] in ("LIGAR", "JA_LIGADA") and "PREVISAO" in d.get("CONFERIDO", {})]
    fora = [d["SOURCE_ID"] for d in decisoes
            if d["DECISAO"] in ("LIGAR", "JA_LIGADA") and "PREVISAO" not in d.get("CONFERIDO", {})]
    soma = {k: round(sum(p[k] for p in ps), 2) for k in ("DOC_DIA_ANTES", "DOC_DIA_DEPOIS",
                                                          "DOC_1A_VOLTA_ANTES", "DOC_1A_VOLTA_DEPOIS")}
    return {"FONTES_CONFERIDAS": len(ps), "NAO_SEI": fora, **soma}


def main(argv=None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    a = dict(x[2:].split("=", 1) for x in argv if x.startswith("--") and "=" in x)
    caminho = Path(a.get("tabela") or TABELA)
    tabela = _json(caminho)
    if "--desfazer" in argv:
        feitas = desfazer(tabela)
        if feitas:
            escrever(tabela, caminho)
        print(json.dumps({"DESFEITAS": feitas, "TABELA": str(caminho)}, ensure_ascii=False, indent=1))
        return 0
    pacote = _json(Path(a.get("pacote") or PACOTE))
    decisoes = plano(tabela, pacote)
    prev = None
    if a.get("conferir-feeds"):
        conferir(decisoes, a["conferir-feeds"])
        prev = previsao(decisoes)
    ligadas = 0
    if "--aplicar" in argv:
        ligadas = aplicar(tabela, decisoes, "regras/FEED-LIGADO-PACOTE.json",
                          datetime.now(timezone.utc).isoformat(timespec="seconds"))
        if ligadas:
            escrever(tabela, caminho)
    resumo = {}
    for d in decisoes:
        resumo[d["DECISAO"]] = resumo.get(d["DECISAO"], 0) + 1
    print(json.dumps({"TABELA": str(caminho), "MODO": "APLICADO" if "--aplicar" in argv else "SECO (nada escrito)",
                      "LIGADAS_AGORA": ligadas, "RESUMO": resumo, **({"PREVISAO": prev} if prev else {}),
                      "DECISOES": decisoes},
                     ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
