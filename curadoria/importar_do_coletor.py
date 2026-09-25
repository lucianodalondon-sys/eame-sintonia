#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""IMPORTAR DO COLETOR — o Curator aprende o contrato que o coletor JA executa.

    O CONTRATO QUE O ROBO USA E UM SO. O CURATOR NAO PODE PROVAR OUTRO.

MEDIDO (LEGACY-99, 25/09/2026, copia fiel do vivo 7cdb7ea4):
  * 32 das 99 READY_LEGACY nao tinham contrato no Curator (so no coletor): o
    caminho canonico parava em VALIDATE_ROUTE «sem contrato» (worker.py) e o reparo
    em SEM_IDENTIDADE — nunca voltavam;
  * 41 YouTube tinham no Curator a rota `feeds/videos.xml` (robots do YouTube a
    proibe), enquanto o coletor ja usa a pagina publica do canal
    (CUSTOM_ADAPTER CANAL_PUBLICO_YOUTUBE_V1) — o Curator provava um contrato que
    ninguem executa.

O QUE FAZ: para uma READY_LEGACY cuja linha DECLARATIVA existe na tabela do coletor
(`regras/italy_contracts_onboarded.json`), escreve no Curator a aquisicao dessa linha,
byte a byte, e manda a fonte ao caminho canonico (`ready_split.remedir`):
CANARY_PENDING + VALIDATE_ROUTE, com as reguas de hoje. NUNCA READY por importacao.

A PROVENIENCIA FICA SEPARADA DA AQUISICAO HISTORICA — a condicao que faltava em
`docs/operacao/OUT-OF-FLOW-LEGACY-DECISION-V1.md` («o contrato de hoje nao separa
proveniencia da importacao atual da aquisicao historica. Sem essa separacao
escrita, nao autorizo»):
  PROVENIENCIA_DO_CONTRATO  de onde veio ESTE contrato hoje (tabela, linha, sha256)
  AQUISICAO_HISTORICA       o que se sabe da aquisicao antiga — e o que NAO se sabe

Fica de fora, dito com o nome:
  SO_CASE              a fonte so existe como `case` no coletor (nao ha linha a importar)
  CANARIO_NAO_PROVA    a estrategia da linha nao e HTML_LINK_DISCOVERY nem o canal
                       YouTube (ex.: STATIC_ENDPOINT PDF): o canario do Curator nao a
                       prova e a regua dos 4 passos so aceita HTML — importar so a
                       faria falhar

Uso: py curadoria/importar_do_coletor.py                 (so mostra)
     py curadoria/importar_do_coletor.py --aplicar --ids=IT-..,IT-..
"""
from __future__ import annotations

import copy
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "curadoria"))
import sha_do_contrato as SHA   # noqa: E402

TABELA = RAIZ / "regras" / "italy_contracts_onboarded.json"
CURATOR = RAIZ / "curadoria" / "italy_contracts_curator.json"
YOUTUBE_CANAL = "CANAL_PUBLICO_YOUTUBE_V1"
MISSAO = "LEGACY-99 v2 (A/B), 25/09/2026"


class ImportacaoInvalida(ValueError):
    pass


def _agora() -> str:
    return datetime.now(timezone.utc).isoformat()


def o_canario_prova(aq: dict) -> bool:
    return (aq.get("STRATEGY") == "HTML_LINK_DISCOVERY" and bool(aq.get("INDEX_URL"))) or \
           (aq.get("STRATEGY") == "CUSTOM_ADAPTER" and aq.get("ADAPTER_ID") == YOUTUBE_CANAL
            and bool(aq.get("CHANNEL_ID")))


def identidades_do_coletor(ids: list[str]) -> dict:
    """A IDENTITY que o coletor gera ao expandir a linha (`regras/italy_contracts.mjs`,
    `contratoGenerico`): o dono do contrato, lido por Node, nunca reescrito aqui.

    ⚠️ MEDIDO no ensaio da LEGACY-99 v2 (25/09): a linha da tabela nao traz IDENTITY; o
    coletor gera-a. Importada so a linha, 14 das 21 HTML rebentaram no canario do
    Curator com «KeyError: 'IDENTITY'»."""
    import subprocess
    r = subprocess.run(["node", "-e", 'import("./regras/italy_contracts.mjs").then(m=>{const o={};'
                        'for(const s of JSON.parse(process.argv[1])){const c=m.CONTRACTS[s];'
                        'if(c&&c.IDENTITY)o[s]=c.IDENTITY}console.log(JSON.stringify(o))})', json.dumps(ids)],
                       cwd=RAIZ, capture_output=True, text=True, timeout=120)
    if r.returncode:
        raise ImportacaoInvalida("o dono dos contratos do coletor nao carregou: " + r.stderr[-200:])
    return json.loads(r.stdout)


def contrato_importado(linha: dict, atual: dict | None, promocao: dict | None, quando: str,
                       identidade: dict | None = None) -> dict:
    """O contrato do Curator depois da importacao. Puro: nao escreve.

    `linha` e a linha da tabela do coletor; `atual` o contrato do Curator se existir
    (YouTube: mantem-se tudo o que nao e rota); `promocao` a ultima promocao do livro."""
    aq = linha.get("ACQUISITION") or {}
    if not o_canario_prova(aq):
        raise ImportacaoInvalida("%s: estrategia %s — o canario do Curator nao a prova"
                                 % (linha.get("SOURCE_ID"), aq.get("STRATEGY")))
    novo = copy.deepcopy(atual) if atual else {}
    for k in ("SOURCE_ID", "OWNER", "NAME", "TERRITORY", "BATCH_ID", "OUTPUT_TYPE", "CANONICAL_ENTRY_URL",
              "SOURCE_NATIVE_ID", "SOURCE_NATIVE_ID_KIND"):
        if k in linha:
            novo[k] = copy.deepcopy(linha[k])
    novo["ACQUISITION"] = copy.deepcopy(aq)
    # D53: o canal YouTube entra na forma VIDEO, com saida VIDEO explicita. O coletor
    # transporta a pagina (OUTPUT_TYPE HTML na tabela); o Curator declara o que prova.
    # A diferenca fica escrita na proveniencia, e a guarda de impressao compara a rota.
    video = aq.get("STRATEGY") == "CUSTOM_ADAPTER" and aq.get("ADAPTER_ID") == YOUTUBE_CANAL
    if video:
        novo["FORMA"], novo["OUTPUT_TYPE"] = "VIDEO", "VIDEO"
    # a identidade: a da linha, senao a que o Curator ja tinha (YouTube: por video), senao
    # a que o coletor gera. Sem nenhuma, o canario nao da nome ao documento: nao se importa.
    ident = linha.get("IDENTITY") or (atual or {}).get("IDENTITY") or identidade
    if not ident or not ident.get("DOCUMENT_ID"):
        raise ImportacaoInvalida("%s: sem IDENTITY (nem na linha, nem no Curator, nem gerada pelo coletor)"
                                 % linha.get("SOURCE_ID"))
    novo["IDENTITY"] = copy.deepcopy(ident)
    anterior = (atual or {}).get("ACQUISITION")
    novo["PROVENIENCIA_DO_CONTRATO"] = {
        "ORIGEM": "IMPORTADO_DO_COLETOR",
        "IMPORTADO_EM": quando,
        "TABELA": "regras/italy_contracts_onboarded.json",
        "SHA256_DA_LINHA": SHA.do_contrato(linha),
        "POR": MISSAO,
        "ACQUISITION_ANTERIOR_NO_CURATOR": anterior,
        "OUTPUT_TYPE_NO_COLETOR": linha.get("OUTPUT_TYPE"),
        "NOTA": ("contrato de HOJE, igual ao que o coletor executa; nao promove: a fonte vai "
                 "ao canario com as reguas atuais (ready_split.remedir)"),
    }
    novo["AQUISICAO_HISTORICA"] = {
        "PROVADA": False,
        "PROMOVIDA_PELA_REGUA_ANTIGA_EM": (promocao or {}).get("OBSERVED_AT"),
        "EVIDENCE_REF_DA_PROMOCAO": (promocao or {}).get("EVIDENCE_REF"),
        "NOTA": ("CONTENT_PROVES_PUBLISHER != ACQUISITION_PROVENANCE_PROVEN: importar o "
                 "contrato hoje nao prova como, quando nem por quem foram adquiridos os "
                 "documentos antigos desta fonte"),
    }
    # a marca de contrato novo que o gatilho ja sabe ler (gatilho_discovery.candidatas_a_revalidar)
    novo["CONTRATO_UNICO"] = {"APLICADO_EM": quando, "ORIGEM": "tabela do coletor",
                              "SHA256": SHA.do_contrato(novo)}
    comparavel = dict(novo, OUTPUT_TYPE=linha.get("OUTPUT_TYPE")) if video else novo
    if SHA.do_contrato(comparavel) != SHA.do_contrato(linha):
        raise ImportacaoInvalida("%s: o contrato importado nao e o da linha" % linha.get("SOURCE_ID"))
    return novo


def planear(*, ctx: dict | None = None, tabela: dict | None = None) -> dict:
    """{"IMPORTA": [...], "FICA": [...]} para as READY_LEGACY. Sem rede e sem escrever."""
    import collection_gate as CG   # noqa: E402
    import ready_split as RS       # noqa: E402
    ctx = ctx if ctx is not None else CG._contexto()
    tabela = tabela if tabela is not None else {
        l["SOURCE_ID"]: l for l in json.loads(TABELA.read_text(encoding="utf-8"))["FONTES"]}
    importa, fica = [], []
    for sid in sorted(s for s, e in _estados(ctx).items() if e == "READY_FOR_COLLECTION"):
        if CG.avaliar(sid, **ctx).get("MOTIVO") != CG.READY_LEGACY:
            continue
        atual = ctx["contratos"].get(sid)
        aq_atual = (atual or {}).get("ACQUISITION") or {}
        precisa = (not atual) or aq_atual.get("STRATEGY") == "YOUTUBE_CHANNEL_FEED"
        if not precisa:
            continue
        linha = tabela.get(sid)
        if not linha:
            fica.append({"SOURCE_ID": sid, "PORQUE": "SO_CASE: o coletor tem esta fonte so como `case` — "
                                                    "nao ha linha declarativa a importar"})
            continue
        if not o_canario_prova(linha.get("ACQUISITION") or {}):
            fica.append({"SOURCE_ID": sid, "PORQUE": "CANARIO_NAO_PROVA: %s/%s — nem o canario nem a "
                         "regua dos 4 passos sabem prova-la" % ((linha.get("ACQUISITION") or {}).get("STRATEGY"),
                                                                linha.get("OUTPUT_TYPE"))})
            continue
        importa.append({"SOURCE_ID": sid, "CASO": "YOUTUBE_FEED_PARA_CANAL" if atual else "SEM_CONTRATO_NO_CURATOR",
                        "PROMOCAO": RS.ultima_promocao(sid, ctx["livro"])})
    return {"IMPORTA": importa, "FICA": fica}


def _estados(ctx: dict) -> dict:
    est = {}
    for t in ctx["livro"]["TRANSICOES"]:
        est[t["SOURCE_ID"]] = t["NEW_STATE"]
    return est


def aplicar(ids: list[str], *, quando: str | None = None, remedir_fn=None, identidades_fn=None) -> dict:
    """Escreve os contratos importados (escrita atomica) e manda as fontes ao canario."""
    quando = quando or _agora()
    plano = planear()
    por = {p["SOURCE_ID"]: p for p in plano["IMPORTA"]}
    fora = [s for s in ids if s not in por]
    if fora:
        raise ImportacaoInvalida("fora do plano (nao sao READY_LEGACY importaveis): %s" % ", ".join(fora))
    tabela = {l["SOURCE_ID"]: l for l in json.loads(TABELA.read_text(encoding="utf-8"))["FONTES"]}
    d = json.loads(CURATOR.read_text(encoding="utf-8"))
    tem = {c["SOURCE_ID"] for c in d["FONTES"] if c.get("IDENTITY")}
    faltam = [s for s in ids if not tabela[s].get("IDENTITY") and s not in tem]
    geradas = (identidades_fn or identidades_do_coletor)(faltam) if faltam else {}
    idx = {c["SOURCE_ID"]: i for i, c in enumerate(d["FONTES"])}
    for s in ids:
        atual = d["FONTES"][idx[s]] if s in idx else None
        novo = contrato_importado(tabela[s], atual, por[s]["PROMOCAO"], quando, identidade=geradas.get(s))
        if s in idx:
            d["FONTES"][idx[s]] = novo
        else:
            d["FONTES"].append(novo)
    tmp = CURATOR.with_name(CURATOR.name + ".tmp")
    tmp.write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")
    tmp.replace(CURATOR)
    if remedir_fn is None:
        import ready_split as RS   # noqa: E402
        remedir_fn = lambda x: RS.remedir(x, motivo=(  # noqa: E731
            "contrato importado do coletor (%s): medir pelas reguas atuais — importar nunca promove" % MISSAO))
    feitas = remedir_fn(ids)
    return {"IMPORTADAS": ids, "REMEDIDAS": sum(1 for f in feitas if f.get("FEITO"))}


def main(argv=None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    plano = planear()
    for p in plano["IMPORTA"]:
        print("IMPORTA  %-11s  %s" % (p["SOURCE_ID"], p["CASO"]))
    for f in plano["FICA"]:
        print("FICA     %-11s  %s" % (f["SOURCE_ID"], f["PORQUE"][:110]))
    print("IMPORTA=%d FICA=%d" % (len(plano["IMPORTA"]), len(plano["FICA"])))
    if "--aplicar" in argv:
        ids = next((a.split("=", 1)[1].split(",") for a in argv if a.startswith("--ids=")), None)
        if not ids:
            print("--aplicar exige --ids=... (lote pequeno, D38: uma fonte por dominio por corrida)")
            return 2
        print(json.dumps(aplicar([i for i in ids if i]), ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
