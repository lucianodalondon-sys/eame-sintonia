"""D32 (7): a 1.a EXECUCAO da bancada — 30 casos da FILA-PRECISA-DE-IA, como canario.

O robo buscou as paginas (C:/cur/bancada/buscar_lote.py: portao de egresso IT, robots, 2 s por
anfitriao; indice PAGINAS.jsonl com sha256). O agente (claude-opus-5-5, pela assinatura, nesta
sessao) leu os bytes e respondeu. As respostas entram SO pelas portas, em COPIAS:
  territorio / relevancia -> DECISOES-SEMANTICAS (linha revista; a anterior em ANTERIOR)
  receita                 -> PROPOSTAS-DE-RECEITA (proposta com prova, ou SEM_RECEITA com prova)
Depois a fila e refeita com as copias: quantos casos sairam.
uso: py provas/ia_cur/bancada_execucao_1.py <FILA.json> <PAGINAS.jsonl> <DECISOES copia> <PROPOSTAS copia> <saida.json>"""
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ / "curadoria"))
import bancada_ia as BIA   # noqa: E402

FILA, PAGINAS, DEC, PROP, SAIDA = map(Path, sys.argv[1:6])
for p in (DEC, PROP):
    assert "source-curator-service" not in str(p).replace("\\", "/"), "so em copia"
AGORA = datetime.now(timezone.utc).isoformat()
POR = "agente IA (claude-opus-5-5, assinatura) — bancada D32 (7), execucao 1"
V = "C:/Users/London1/orca/workspaces/eame-sintonia/source-curator-service-v1/"
CAND = {x["CANDIDATA_ID"]: x for x in json.load(open(V + "candidatas/FONTES-CANDIDATAS.json", encoding="utf-8"))["CANDIDATAS"]}
PAG = {}
for l in PAGINAS.read_text(encoding="utf-8").splitlines():
    p = json.loads(l)
    if p.get("SHA256"):
        assert hashlib.sha256(Path(p["BYTES_EM"]).read_bytes()).hexdigest() == p["SHA256"], p["URL"]
        PAG.setdefault(p["CASO"].replace("-item", ""), []).append(
            {"PAPEL": "ITEM" if p["CASO"].endswith("-item") else "ENTRADA", "URL": p["URL"],
             "SHA256": p["SHA256"], "BYTES_EM": p["BYTES_EM"]})

# ── as respostas do agente (o que li nos bytes) ─────────────────────────────
RECEITA = {
    "IT-T12-013": "a entrada e o hub tematico Agricoltura da Regione Piemonte (retrato NAVIGATION/CAPA); as familias "
                  "sao paginas de tema (/web/temi/agricoltura/<seccao>/<pagina>), nao publicacoes; a listagem de "
                  "noticias nao esta nesta pagina",
    "IT-T7-041": "ha familia /news/<titulo>/ (7 itens), mas o 1.o item (o que o canario abre) tem 590 caracteres "
                 "em paragrafo e o retrato chama-lhe CAPA: a regua reprova; a lista mistura avisos curtos",
    "IT-T10-024": "pagina de servico da Nomisma (consultoria agroalimentar): as familias sao catalogo de servicos "
                  "(/soluzioni/consulenza/..., /progetti/...), nao publicacoes",
    "IT-T10-032": "pagina de servico da Nomisma (mercado farmaceutico) — o mesmo catalogo de servicos; e fora do agro",
    "IT-T10-033": "pagina de servico da Nomisma (mercado retail) — o mesmo catalogo de servicos",
    "IT-T2-108": "ha familia /notizie/snpa/<titulo>/ (8 itens) e o 1.o item E materia (3969 caracteres em paragrafo, "
                 "polen/Pollnet), mas o retrato chama-lhe CAPA pelos muitos links do menu: o gate reprovaria de novo. "
                 "Achado para o retrato, nao receita",
}
for n in range(81, 90):
    RECEITA["IT-T2-0%d" % n] = ("a pagina E o boletim (rota fixa, actualizada no mesmo endereco): a estrategia certa e "
                                "STATIC_ENDPOINT, que a porta de receita (INDEX + LINK_PATTERN) nao cobre; e sao 9 "
                                "fontes do mesmo site (irmas) — decisao do dono")
TERRITORIO = {   # CAND -> (CATEGORIA, MOTIVO)
    "CAND-0814": ("PAGINA_DE_OUTRA_FONTE", "pagina «Info e contatti / Come raggiungere il Tecnopolo» do DAMA Tecnopolo "
                                           "(Bologna); o nome da candidata e uma morada de rodape"),
    "CAND-0841": ("PAGINA_DE_OUTRA_FONTE", "um decreto (D.lgs 33/2013, transparencia) no Normattiva; ligacao de "
                                           "rodape «amministrazione trasparente»"),
    "CAND-0842": ("PAGINA_DE_OUTRA_FONTE", "um decreto (D.lgs 97/2016, transparencia/anticorrupcao) no Normattiva; "
                                           "ligacao de rodape"),
    "CAND-0843": ("PAGINA_DE_OUTRA_FONTE", "um decreto (D.lgs 36/2006, reutilizacao de dados publicos) no Normattiva; "
                                           "ligacao de rodape"),
    "CAND-0856": ("PAGINA_DE_OUTRA_FONTE", "um decreto de 2001 (Lavori Pubblici, estabelecimentos de risco) na Gazzetta "
                                           "Ufficiale"),
    "CAND-0857": ("PROVA_INSUFICIENTE", "ENTECA (isprambiente): a pagina e casca de aplicacao JavaScript — sem texto "
                                        "legivel nos bytes; NAO SEI o que publica"),
    "CAND-0858": ("PAGINA_DE_OUTRA_FONTE", "uma pagina de linhas-guia (classificacao de residuos) do SNPA, que ja e "
                                           "fonte (IT-T2-108)"),
    "CAND-0861": ("PROVA_INSUFICIENTE", "RENTRI — registo nacional de rastreabilidade de residuos (portal de servico). "
                                        "D2: UNIVERSE_MATCH NAO SEI; SINTONIA_RELEVANT NAO SEI (as explorações agricolas "
                                        "registam residuos perigosos, ex.: embalagens de fitofarmacos — nao provado nos bytes)"),
    "CAND-0864": ("NAO_E_FONTE", "web agency de Bologna (Smart.it); a candidata e o link «CREDITS» de um rodape"),
    "CAND-0906": ("PAGINA_DE_OUTRA_FONTE", "um documento do Garante Privacy (informativa de dados); ligacao de rodape"),
}
D2 = {   # CAND -> (UNIVERSE_MATCH, SINTONIA_RELEVANT, CATEGORIA, MOTIVO)
    "CAND-0057": ("NO", "NAO SEI", "PROVA_INSUFICIENTE",
                  "jornalismo alimentar do consumidor; nenhuma gaveta T1..T12 encaixa (UNIVERSE_MATCH NO). Os 2 itens "
                  "lidos (Rapporto Coop; dioxido de titanio) nao servem ao Sintonia; o site pode cobrir residuos de "
                  "fitofarmacos, nao provado nos bytes (SINTONIA_RELEVANT NAO SEI)"),
    "CAND-0257": ("NAO SEI", "NAO SEI", "IDENTIDADE_TROCADA",
                  "a pergunta dupla so se faz depois de trocar a URL (sherwood.it -> rivistasherwood.it, porta das "
                  "candidatas); com a URL errada responder seria julgar a Radio Sherwood"),
    "CAND-0554": ("NO", "NO", "NAO_E_FONTE",
                  "loja/blog de produtos de cooperativas: prazos de validade e receitas; nenhuma gaveta e nada para o "
                  "Sintonia (3 paginas lidas)"),
    "CAND-0581": ("NO", "NO", "NAO_E_FONTE",
                  "maquinas de JARDINAGEM (Comagarden, FederUnacoma): fora da agricultura; os comunicados sao os da "
                  "base partilhada da FederUnacoma, que a Assomao (IT-T10-046, READY) ja colhe (D32 1)"),
    "CAND-0583": ("NO", "NO", "NAO_E_FONTE",
                  "programa de energia de biomassa de 2010 (objetivos + estudos em PDF): bioenergia, historico, sem "
                  "publicacao corrente"),
}

dec = json.loads(DEC.read_text(encoding="utf-8"))
linhas, feitas = dec["DECISOES"], []


def gravar_decisao(cand, categoria, motivo, provas, d2=None):
    novo = {"CANDIDATA_ID": cand, "NOME": CAND[cand]["NOME"], "URL": CAND[cand]["URL"], "TERRITORIO": "NAO SEI",
            "CATEGORIA": categoria, "MOTIVO": motivo, "DECIDIDO_POR": POR, "DECIDIDO_EM": AGORA,
            "PROVAS_LIDAS": provas}
    if d2:
        novo["D2"] = d2
    for i, x in enumerate(linhas):
        if x["CANDIDATA_ID"] == cand:
            novo["ANTERIOR"] = {k: x.get(k) for k in ("TERRITORIO", "CATEGORIA", "MOTIVO", "DECIDIDO_POR", "DECIDIDO_EM")}
            linhas[i] = novo
            return "REVISTA"
    linhas.append(novo)
    return "NOVA"


respostas = []
for cand, (cat, mot) in TERRITORIO.items():
    modo = gravar_decisao(cand, cat, mot, PAG[cand])
    respostas.append({"CASO": cand, "PERGUNTA": "TERRITORIO", "RESPOSTA": cat, "PORTA": "DECISOES-SEMANTICAS",
                      "LINHA": modo, "PROVAS": len(PAG[cand])})
for cand, (um, sr, cat, mot) in D2.items():
    ant = next(x for x in linhas if x["CANDIDATA_ID"] == cand)
    modo = gravar_decisao(cand, cat, mot, ant.get("PROVAS_LIDAS") or [],
                          d2={"UNIVERSE_MATCH": um, "SINTONIA_RELEVANT": sr,
                              "ACTION": "REROUTE" if (um == "NO" and sr == "YES") else None})
    respostas.append({"CASO": cand, "PERGUNTA": "RELEVANCIA_D2", "RESPOSTA": "%s/%s" % (um, sr), "CATEGORIA": cat,
                      "PORTA": "DECISOES-SEMANTICAS", "LINHA": modo, "PROVAS": len(ant.get("PROVAS_LIDAS") or [])})
assert len({x["CANDIDATA_ID"] for x in linhas}) == len(linhas), "duas linhas para a mesma candidata"
DEC.write_text(json.dumps(dec, ensure_ascii=False, indent=1), encoding="utf-8")

for sid, porque in RECEITA.items():
    BIA.responder_sem_receita({"SOURCE_ID": sid, "PORQUE": porque, "PROPOSTO_EM": AGORA, "PROPOSTO_POR": POR,
                               "PAGINAS_LIDAS": PAG[sid]}, PROP)
    respostas.append({"CASO": sid, "PERGUNTA": "RECEITA", "RESPOSTA": "SEM_RECEITA", "PORTA": "PROPOSTAS-DE-RECEITA",
                      "PROVAS": len(PAG[sid])})

fila = json.loads(FILA.read_text(encoding="utf-8"))
lote = [c["CASO"] for c in fila["CASOS"][:BIA.LOTE_CANARIO]]
assert sorted(lote) == sorted(r["CASO"] for r in respostas), set(lote) ^ {r["CASO"] for r in respostas}

# a fila depois, com as portas copiadas
L = json.load(open(V + "curadoria/LIFECYCLE-LEDGER-V1.json", encoding="utf-8"))["TRANSICOES"]
E = {p["EVIDENCE_REF"]: p.get("OBSERVED_AT") for p in
     json.load(open(V + "curadoria/LIFECYCLE-EVIDENCE-V1.json", encoding="utf-8"))["PROVAS"]}
C = {c["SOURCE_ID"]: c for c in json.load(open(V + "curadoria/italy_contracts_curator.json", encoding="utf-8"))["FONTES"]}
import janela_de_cultura as JC   # noqa: E402
depois = BIA.construir(transicoes=L, decisoes=linhas, propostas=json.loads(PROP.read_text(encoding="utf-8"))["PROPOSTAS"],
                       contratos=C, janela=JC.e_janela, provas_em=E)
out = {"EXECUCAO": 1, "LOTE": len(lote), "FEITA_EM": AGORA, "POR": POR, "ONDE": "COPIAS — nada instalado",
       "FILA_ANTES": {k: fila[k] for k in ("TOTAL", "POR_PERGUNTA")},
       "FILA_DEPOIS": {k: depois[k] for k in ("TOTAL", "POR_PERGUNTA")},
       "SAIRAM_DA_FILA": sorted(set(lote) - {c["CASO"] for c in depois["CASOS"]}),
       "CONTINUAM": sorted(set(lote) & {c["CASO"] for c in depois["CASOS"]}),
       "RESPOSTAS": respostas,
       "COPIAS": {str(DEC): hashlib.sha256(DEC.read_bytes()).hexdigest(),
                  str(PROP): hashlib.sha256(PROP.read_bytes()).hexdigest(),
                  str(PAGINAS): hashlib.sha256(PAGINAS.read_bytes()).hexdigest()}}
SAIDA.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
print(json.dumps({k: out[k] for k in ("FILA_ANTES", "FILA_DEPOIS", "CONTINUAM")}, ensure_ascii=False))
print("sairam:", len(out["SAIRAM_DA_FILA"]))
