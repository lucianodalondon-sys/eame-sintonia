"""IA-CUR: a proposta do agente para IT-T1-006 (ARSAC Calabria, JANELA D29) pelas PORTAS da casa,
numa copia so para ela (sem segundo escritor na copia das voltas).
1. BUILD_CONTRACT importa a linha da tabela do coletor (porta CUR);
2. a proposta (INDEX_URL + LINK_PATTERN lidos pelo agente nas paginas vivas, sha256) entra por
   reparar_contrato.aplicar (a porta de contratos D10 da R1: so muda a ACQUISITION, valida, rebenta
   se tocar noutro campo);
3. VALIDATE_ROUTE -> CANARY pelo worker, e a regua dos quatro passos decide. O agente nao promove."""
import json, os, sys
RAIZ = sys.argv[1]
os.chdir(RAIZ); sys.path.insert(0, RAIZ + "/curadoria")
import worker as W, fila as F, lifecycle as LC, reparar_contrato as RC   # noqa: E402

SID = "IT-T1-006"
PAG = {json.loads(l)["CASO"]: json.loads(l) for l in open("C:/cur/ia/PAGINAS.jsonl", encoding="utf-8")
       if json.loads(l).get("SHA256")}
home, bol = PAG["IT-T1-006-b"], PAG["IT-T1-006"]

r, det = W.etapa_build_contract(SID, None)
print("1 BUILD_CONTRACT (importa do coletor):", r, det.get("ORIGEM"), det.get("PORQUE", ""))
linha = W._linha_do_coletor(SID)
if r != "OK":
    # A importacao foi RECUSADA pelo validador: o LINK_PATTERN da tabela do coletor casa com a
    # propria INDEX_URL (a entrada e um boletim). O contrato base nasce do MOLDE da casa sobre a
    # pagina inicial (validado), e a ACQUISITION do coletor fica guardada como ANTERIOR na prova.
    import escrever_contratos as EC, validar_contratos as VC
    base = EC.contrato_html({"SOURCE_ID": SID, "NOME": linha.get("NAME") or SID,
                             "TERRITORY": linha.get("TERRITORY"), "URL": "https://arsac.calabria.it/"}, {})
    base["ROUTE_PROVENANCE"] = {"ORIGEM": "MOLDE_DA_CASA (IA-CUR)", "INTEGRADO_EM": W.agora(),
                                "PORQUE": "a linha do coletor foi recusada pelo validador (padrao casa a entrada)"}
    base["SOURCE_CONTRACT_VERSION"] = EC.VERSAO
    base["SOURCE_CONTRACT_HASH"] = EC.hash_do_contrato(base)
    assert not VC.validar([base])[1], VC.validar([base])[1]
    d0 = json.load(open(W.CONTRATOS, encoding="utf-8"))
    d0["FONTES"].append(base)
    W._gravar_atomico(W.CONTRATOS, d0)
    print("1b contrato base pelo molde da casa: validado")
con = {c["SOURCE_ID"]: c for c in json.load(open(W.CONTRATOS, encoding="utf-8"))["FONTES"]}
proposta = {
    "DESFECHO": "PADRAO_NOVO",
    "INDEX_URL": "https://arsac.calabria.it/",
    "LINK_PATTERN": r"^https?://arsac\.calabria\.it/(?:[a-z0-9]+-)*bollettino-(?:agrometeorologico-e-fitosanitario|difesa-fitosanitaria)-[a-z0-9-]*valido-fino-a[a-z0-9-]*/?$",
    "COMO": "agente IA-CUR (OPUS claude-opus-5-5 via Orca): a pagina inicial lista 5 boletins da mesma familia "
            "(agrometeorologico e fitosanitario agrumi/olivo/vite/kiwi; limone difesa fitosanitaria)",
    "ENTRADA": {"URL": home["URL"], "SHA256": home["SHA256"], "HTTP": home["HTTP"], "EGRESSO": home["EGRESSO"]},
    "ALVOS_NA_LISTAGEM": 5,
    "ITEM_LIDO": {"URL": bol["URL"], "SHA256": bol["SHA256"], "HTTP": bol["HTTP"]},
    "ACQUISITION_ANTERIOR": (W._linha_do_coletor(SID) or {}).get("ACQUISITION"),
    "PAGINAS_LIDAS": [{"URL": x["URL"], "SHA256": x["SHA256"]} for x in (home, bol)],
}
novo = RC.aplicar(con[SID], proposta)
novo["REPARO_DE_CONTRATO"]["ORIGEM_DA_PROPOSTA"] = "IA-CUR (agente Orca, sem API)"
d = json.load(open(W.CONTRATOS, encoding="utf-8"))
d["FONTES"] = [novo if c["SOURCE_ID"] == SID else c for c in d["FONTES"]]
W._gravar_atomico(W.CONTRATOS, d)
print("2 porta D10 (reparar_contrato.aplicar): contrato novo, validado; INDEX", novo["ACQUISITION"]["INDEX_URL"])
for tipo in (F.VALIDATE_ROUTE, F.CANARY):
    t = F.enfileirar(SID, tipo, priority=90, motivo="IA-CUR: proposta do agente, remedir")
    res = W.executar_uma(t, W._contratos())
    print("3", tipo, res["RESULTADO"], (res.get("PORQUE") or "")[:160])
    if res["RESULTADO"] != "OK":
        break
print("ESTADO FINAL", SID, LC.estado_de(SID))
ev = [p for p in json.load(open(W.EVIDENCIA, encoding="utf-8"))["PROVAS"] if p["SOURCE_ID"] == SID][-1]
dados = ev["DADOS"]
print("canario:", json.dumps({k: dados.get(k) for k in ("PASS", "DETAIL_ENUMERATED", "DETAIL_GATE_PASSED")},
                              ensure_ascii=False), json.dumps(dados.get("ITEM_ABERTO"), ensure_ascii=False)[:300])
