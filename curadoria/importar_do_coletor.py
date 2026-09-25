#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""IMPORTAR DO COLETOR — o Curator aprende o contrato que o coletor JA executa.

    O CONTRATO QUE O ROBO USA E UM SO. O CURATOR NAO PODE PROVAR OUTRO.

MEDIDO (LEGACY-99, 25/09/2026, copia fiel do vivo 7cdb7ea4):
  * 32 das 99 READY_LEGACY nao tinham contrato no Curator (so no coletor): o
    caminho canonico parava em VALIDATE_ROUTE «sem contrato» (worker.py) e o reparo
    em SEM_IDENTIDADE — nunca voltavam;
  * 41 YouTube tinham no Curator a rota `feeds/videos.xml` (robots do YouTube a
    proibe). ⚠️ ESTAS NAO SE IMPORTAM DAQUI: a linha do coletor aponta-as para
    `CANAL_PUBLICO_YOUTUBE_V1`, um adapter JS que nao existe nesta arvore, e a rota
    YouTube tem UM dono — a fase `canal-youtube` do Scrap (SOC2, D17.4), nomeada por
    `rota_do_scrap_youtube.py` e julgada por `regua_social.py`.

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
  CANARIO_NAO_PROVA    a estrategia da linha nao e HTML_LINK_DISCOVERY (ex.:
                       STATIC_ENDPOINT PDF): o canario do Curator nao a prova e a
                       regua dos 4 passos so aceita HTML — importar so a faria falhar
  ROTA_DO_SCRAP        canal YouTube: a rota e do Scrap, nao da tabela do coletor

B · O CANAL YOUTUBE VAI PARA A ROTA DO SCRAP (UM SO DONO):
  `--pelo-scrap --ids=` nao escreve rota nenhuma com a mao dele: chama o BLOCO 4 do
  desbloqueio (`scripts/desbloqueio/aplicar_desbloqueio.rota_do_scrap`), que ja e a
  peca que troca o feed pela fase `canal-youtube` do Scrap — com as provas dele
  (canal do livro = da tabela = SOURCE_NATIVE_ID, IDENTITY_MATCH=YES, um so dono do
  canal, o Scrap declara HOJE a rota e a matriz diz ALLOWED) e as invariantes dele.
  So as fontes pedidas mudam; depois vao ao `remedir` (CANARY_PENDING +
  VALIDATE_ROUTE, que para em CANARY_PENDING: o canario e uma colheita do Scrap,
  julgada por `regua_social.py`). Nunca READY daqui.

Uso: py curadoria/importar_do_coletor.py                 (so mostra)
     py curadoria/importar_do_coletor.py --aplicar --ids=IT-..,IT-..
     py curadoria/importar_do_coletor.py --pelo-scrap --ids=IT-..   (B: canal YouTube)
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
MISSAO = "LEGACY-99 v4 (A), 25/09/2026"
MISSAO_B = "LEGACY-99 v4 (B), 25/09/2026"
LEDGER = RAIZ / "curadoria" / "DESBLOQUEIO-LEDGER-V1.jsonl"   # o mesmo do bloco 4
YOUTUBE = ("YOUTUBE_CHANNEL_FEED", "SCRAP_FASE")


class ImportacaoInvalida(ValueError):
    pass


def _agora() -> str:
    return datetime.now(timezone.utc).isoformat()


def o_canario_prova(aq: dict) -> bool:
    """So HTML. O canal YouTube nao e provado pelo canario do Curator: e uma colheita
    do Scrap (worker.etapa_canary devolve BLOCK DO_SCRAP)."""
    return aq.get("STRATEGY") == "HTML_LINK_DISCOVERY" and bool(aq.get("INDEX_URL"))


def e_youtube(atual: dict | None, linha: dict | None) -> bool:
    """O canal YouTube, pelo contrato do Curator OU pela linha do coletor."""
    aq = (atual or {}).get("ACQUISITION") or {}
    la = (linha or {}).get("ACQUISITION") or {}
    return (aq.get("STRATEGY") in YOUTUBE or aq.get("PLATFORM") == "YOUTUBE"
            or "youtube" in json.dumps(la).lower())


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

    `linha` e a linha da tabela do coletor; `atual` o contrato do Curator se existir;
    `promocao` a ultima promocao do livro."""
    aq = linha.get("ACQUISITION") or {}
    if e_youtube(atual, linha):
        raise ImportacaoInvalida("%s: canal YouTube — a rota e do Scrap (rota_do_scrap_youtube), "
                                 "nao se importa da tabela do coletor" % linha.get("SOURCE_ID"))
    if not o_canario_prova(aq):
        raise ImportacaoInvalida("%s: estrategia %s — o canario do Curator nao a prova"
                                 % (linha.get("SOURCE_ID"), aq.get("STRATEGY")))
    novo = copy.deepcopy(atual) if atual else {}
    for k in ("SOURCE_ID", "OWNER", "NAME", "TERRITORY", "BATCH_ID", "OUTPUT_TYPE", "CANONICAL_ENTRY_URL",
              "SOURCE_NATIVE_ID", "SOURCE_NATIVE_ID_KIND"):
        if k in linha:
            novo[k] = copy.deepcopy(linha[k])
    novo["ACQUISITION"] = copy.deepcopy(aq)
    # a identidade: a da linha, senao a que o Curator ja tinha, senao a que o coletor
    # gera. Sem nenhuma, o canario nao da nome ao documento: nao se importa.
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
    if SHA.do_contrato(novo) != SHA.do_contrato(linha):
        raise ImportacaoInvalida("%s: o contrato importado nao e o da linha" % linha.get("SOURCE_ID"))
    return novo


def planear(*, ctx: dict | None = None, tabela: dict | None = None) -> dict:
    """{"IMPORTA": [...], "PELO_SCRAP": [...], "FICA": [...]} para as READY_LEGACY.
    Sem rede e sem escrever."""
    import collection_gate as CG   # noqa: E402
    import ready_split as RS       # noqa: E402
    ctx = ctx if ctx is not None else CG._contexto()
    tabela = tabela if tabela is not None else {
        l["SOURCE_ID"]: l for l in json.loads(TABELA.read_text(encoding="utf-8"))["FONTES"]}
    importa, scrap, fica = [], [], []
    for sid in sorted(s for s, e in _estados(ctx).items() if e == "READY_FOR_COLLECTION"):
        if CG.avaliar(sid, **ctx).get("MOTIVO") != CG.READY_LEGACY:
            continue
        atual = ctx["contratos"].get(sid)
        linha = tabela.get(sid)
        if e_youtube(atual, linha):
            if not atual:
                fica.append({"SOURCE_ID": sid, "PORQUE": "ROTA_DO_SCRAP: canal YouTube sem contrato no "
                             "Curator — o bloco 4 so troca a rota de um contrato que ja existe"})
            else:
                scrap.append({"SOURCE_ID": sid, "PORQUE": "ROTA_DO_SCRAP: canal YouTube — a rota tem "
                              "dono proprio (rota_do_scrap_youtube, fase canal-youtube); vai pelo bloco 4",
                              "STRATEGY_HOJE": ((atual.get("ACQUISITION") or {}).get("STRATEGY"))})
            continue
        if atual:
            continue
        if not linha:
            fica.append({"SOURCE_ID": sid, "PORQUE": "SO_CASE: o coletor tem esta fonte so como `case` — "
                                                    "nao ha linha declarativa a importar"})
            continue
        if not o_canario_prova(linha.get("ACQUISITION") or {}):
            fica.append({"SOURCE_ID": sid, "PORQUE": "CANARIO_NAO_PROVA: %s/%s — nem o canario nem a "
                         "regua dos 4 passos sabem prova-la" % ((linha.get("ACQUISITION") or {}).get("STRATEGY"),
                                                                linha.get("OUTPUT_TYPE"))})
            continue
        importa.append({"SOURCE_ID": sid, "CASO": "SEM_CONTRATO_NO_CURATOR",
                        "PROMOCAO": RS.ultima_promocao(sid, ctx["livro"])})
    return {"IMPORTA": importa, "PELO_SCRAP": scrap, "FICA": fica}


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


def _bloco4():
    """O dono da troca feed -> Scrap. Importado, nunca copiado."""
    import importlib.util
    p = RAIZ / "scripts" / "desbloqueio" / "aplicar_desbloqueio.py"
    spec = importlib.util.spec_from_file_location("aplicar_desbloqueio", p)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def pelo_scrap(ids: list[str], *, remedir_fn=None, declarado: dict | None = None, bloco4=None) -> dict:
    """B · as fontes pedidas passam para a rota do Scrap pelo bloco 4, e vao ao remedir.

    Tudo ou nada: se o bloco 4 saltar uma das pedidas (com o porque dele), nada se
    escreve. O bloco corre sobre os livros INTEIROS (a colisao de canal ve a casa
    toda), mas so as linhas das fontes pedidas passam para o disco."""
    AD = bloco4 or _bloco4()
    plano = planear()
    por = {p["SOURCE_ID"] for p in plano["PELO_SCRAP"]}
    fora = [s for s in ids if s not in por]
    if fora:
        raise ImportacaoInvalida("fora do plano (nao sao canais YouTube READY_LEGACY com contrato): %s"
                                 % ", ".join(fora))
    livro = json.loads(CURATOR.read_text(encoding="utf-8"))
    tabela = json.loads(TABELA.read_text(encoding="utf-8"))
    novo_livro = {c["SOURCE_ID"]: copy.deepcopy(c) for c in livro["FONTES"]}
    tab_antes = {l["SOURCE_ID"]: l for l in tabela["FONTES"]}
    nova_tabela = copy.deepcopy(tab_antes)
    acoes, autorizadas = AD.rota_do_scrap(novo_livro, nova_tabela, tab_antes, declarado)
    pedidas = set(ids)
    saltou = {a["SOURCE_ID"]: a["PORQUE"] for a in acoes if a["ACAO"] == "SALTA" and a["SOURCE_ID"] in pedidas}
    if saltou or not pedidas <= autorizadas:
        raise ImportacaoInvalida("o bloco 4 nao autoriza: %s" % ("; ".join(
            "%s: %s" % kv for kv in sorted(saltou.items())) or sorted(pedidas - autorizadas)))
    livro_d = dict(livro, FONTES=[novo_livro[c["SOURCE_ID"]] if c["SOURCE_ID"] in pedidas else c
                                  for c in livro["FONTES"]])
    tabela_d = dict(tabela, FONTES=[nova_tabela[l["SOURCE_ID"]] if l["SOURCE_ID"] in pedidas else l
                                    for l in tabela["FONTES"]])
    AD.invariantes(livro, livro_d, tabela, tabela_d, autorizadas_scrap=frozenset(pedidas))
    minhas = [a for a in acoes if a["SOURCE_ID"] in pedidas and a["ACAO"] == "APLICA"]
    for dest, d in ((CURATOR, livro_d), (TABELA, tabela_d)):
        tmp = dest.with_name(dest.name + ".tmp")
        tmp.write_text(json.dumps(d, ensure_ascii=False, indent=1) + ("\n" if dest == TABELA else ""),
                       encoding="utf-8")
        tmp.replace(dest)
    if minhas:
        with LEDGER.open("a", encoding="utf-8") as f:
            for a in minhas:
                f.write(json.dumps({"MISSAO": MISSAO_B, "AT": _agora(), **{k: a.get(k) for k in (
                    "LIVRO", "SOURCE_ID", "CAMPO", "ANTES", "DEPOIS", "ORIGEM", "PROVA", "DECISAO")}},
                    ensure_ascii=False) + "\n")
    if remedir_fn is None:
        import ready_split as RS   # noqa: E402
        remedir_fn = lambda x: RS.remedir(x, motivo=(  # noqa: E731
            "canal YouTube na rota do Scrap (%s, bloco 4): o canario e uma colheita do Scrap, "
            "julgada pela regua social — nunca READY daqui" % MISSAO_B))
    feitas = remedir_fn(ids)
    return {"PELO_SCRAP": ids, "ACOES": [(a["LIVRO"], a["SOURCE_ID"], a["ACAO"]) for a in acoes
                                         if a["SOURCE_ID"] in pedidas],
            "REMEDIDAS": sum(1 for f in feitas if f.get("FEITO"))}


def main(argv=None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    plano = planear()
    for p in plano["IMPORTA"]:
        print("IMPORTA  %-11s  %s" % (p["SOURCE_ID"], p["CASO"]))
    for p in plano["PELO_SCRAP"]:
        print("SCRAP    %-11s  %s" % (p["SOURCE_ID"], p["STRATEGY_HOJE"]))
    for f in plano["FICA"]:
        print("FICA     %-11s  %s" % (f["SOURCE_ID"], f["PORQUE"][:110]))
    print("IMPORTA=%d PELO_SCRAP=%d FICA=%d" % (len(plano["IMPORTA"]), len(plano["PELO_SCRAP"]),
                                                len(plano["FICA"])))
    if "--aplicar" in argv or "--pelo-scrap" in argv:
        ids = next((a.split("=", 1)[1].split(",") for a in argv if a.startswith("--ids=")), None)
        if not ids:
            print("--aplicar/--pelo-scrap exigem --ids=... (lote pequeno, D38: uma fonte por dominio por corrida)")
            return 2
        fn = pelo_scrap if "--pelo-scrap" in argv else aplicar
        print(json.dumps(fn([i for i in ids if i]), ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
