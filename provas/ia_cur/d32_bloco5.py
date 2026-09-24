"""D32 (5): as 5 recusas do piloto NAO foram aceites — sem provas e a misturar irrelevancia com
identidade errada. Revisao das 5 linhas NUMA COPIA de DECISOES-SEMANTICAS-V1.json (revisa a linha,
com a anterior em ANTERIOR; duas linhas para a mesma candidata seriam conflito).

  CAND-0257 Sherwood        -> IDENTIDADE_TROCADA, agora com prova (3 paginas da Radio/Festival
                               Sherwood) e a URL certa proposta (rivistasherwood.it, capa n.284)
  as outras 4               -> NAO SEI ate a pergunta dupla da D2: UNIVERSE_MATCH e SINTONIA_RELEVANT
                               ficam NAO SEI; categoria PROVA_INSUFICIENTE (nao trava semente:
                               falta de resposta nao e prova de lixo)

As paginas sao as que a S2 guardou (bytes fora do Git, caminho + sha256 em cada prova).
uso: py provas/ia_cur/d32_bloco5.py <DECISOES copia.json> <pasta dos bytes> <saida.json>"""
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

COPIA, BYTES, SAIDA = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])
assert "source-curator-service" not in str(COPIA).replace("\\", "/"), "so em copia"
AGORA = datetime.now(timezone.utc).isoformat()
POR = "bot Luciano por delegacao (D32 5), preparado pelo agente IA-CUR (claude-opus-5-5)"
PAPEIS = ("INSTITUCIONAL", "CONTEUDO", "CONTEUDO")
URLS = json.loads((BYTES / "agentes.json").read_text(encoding="utf-8"))
# a recusa do piloto (so existiu na copia do piloto; nunca foi instalada) — NAO aceite pela D32
PILOTO = {x["CANDIDATA_ID"]: {k: x.get(k) for k in ("CATEGORIA", "MOTIVO", "DECIDIDO_EM")}
          for x in json.loads((Path(__file__).parent / "DECISOES-IA-CUR-V1.json")
                              .read_text(encoding="utf-8"))["DECISOES"]}

# o que as paginas mostram (factos lidos nos bytes, para quem fizer a pergunta dupla)
FACTOS = {
    "CAND-0057": "redacao de jornalismo alimentar do consumidor: Rapporto Coop 2025; dioxido de titanio (aditivo/farmacos)",
    "CAND-0554": "loja/blog de produtos de cooperativas: prazos de validade; receitas de couve",
    "CAND-0581": "associacao FederUnacoma de construtores de maquinas de jardinagem: dados de mercado; comunicados",
    "CAND-0583": "programa ministerial de energia de biomassa (FederUnacoma): objetivos; estudos em PDF",
}
PERGUNTA = ("D2: UNIVERSE_MATCH (serve a gaveta declarada?) e SINTONIA_RELEVANT (serve ao Sintonia em "
            "qualquer gaveta?) sao perguntas separadas; a recusa anterior respondeu as duas com uma so")


def provas(cand):
    out = []
    for i, (url, papel) in enumerate(zip(URLS[cand], PAPEIS)):
        p = BYTES / "provas" / cand / ("%d_%s.bin" % (i, papel))
        b = p.read_bytes()
        out.append({"PAPEL": papel, "URL": url, "SHA256": hashlib.sha256(b).hexdigest(),
                    "BYTES": len(b), "BYTES_EM": str(p)})
    return out


d = json.loads(COPIA.read_text(encoding="utf-8"))
linhas = d["DECISOES"]
mudadas = []
for i, x in enumerate(linhas):
    cand = x["CANDIDATA_ID"]
    if cand not in FACTOS and cand != "CAND-0257":
        continue
    anterior = {k: x.get(k) for k in ("TERRITORIO", "CATEGORIA", "MOTIVO", "DECIDIDO_POR", "DECIDIDO_EM")}
    novo = {"CANDIDATA_ID": cand, "NOME": x["NOME"], "URL": x["URL"], "TERRITORIO": "NAO SEI",
            "DECIDIDO_POR": POR, "DECIDIDO_EM": AGORA, "PROVAS_LIDAS": provas(cand), "ANTERIOR": anterior,
            "RECUSA_DO_PILOTO_NAO_ACEITE": PILOTO.get(cand)}
    if cand == "CAND-0257":
        sher = BYTES.parent / "sherwood" / "www.rivistasherwood.it.bin"
        novo.update(CATEGORIA="IDENTIDADE_TROCADA",
                    MOTIVO=("as 3 paginas de sherwood.it sao da Radio/Festival Sherwood (Padova), nao da "
                            "revista florestal; volta com a URL certa: https://www.rivistasherwood.it/ "
                            "(capa «Sherwood - Foreste ed Alberi Oggi» n.284, Compagnia delle Foreste)"),
                    URL_CERTA_PROPOSTA={"URL": "https://www.rivistasherwood.it/",
                                        "SHA256": hashlib.sha256(sher.read_bytes()).hexdigest(),
                                        "BYTES_EM": str(sher), "LIDO_EM": "2026-09-24, egresso IT, robots permite"},
                    D2={"UNIVERSE_MATCH": "NAO SEI", "SINTONIA_RELEVANT": "NAO SEI",
                        "NOTA": "a relevancia da revista florestal pergunta-se DEPOIS de a URL ser trocada"})
    else:
        novo.update(CATEGORIA="PROVA_INSUFICIENTE",
                    MOTIVO=("NAO SEI ate a pergunta dupla da D2. O que as paginas mostram: %s. A recusa "
                            "do piloto (%s) misturava gaveta e relevancia." % (FACTOS[cand], (PILOTO.get(cand) or {}).get("CATEGORIA"))),
                    D2={"UNIVERSE_MATCH": "NAO SEI", "SINTONIA_RELEVANT": "NAO SEI", "PERGUNTA": PERGUNTA})
    linhas[i] = novo
    mudadas.append({"CANDIDATA_ID": cand, "ANTES_NO_VIVO": anterior["CATEGORIA"],
                    "PILOTO_PROPUNHA": (PILOTO.get(cand) or {}).get("CATEGORIA"), "DEPOIS": novo["CATEGORIA"],
                    "PROVAS": len(novo["PROVAS_LIDAS"])})
assert len(mudadas) == 5, mudadas
assert all(sum(1 for x in linhas if x["CANDIDATA_ID"] == m["CANDIDATA_ID"]) == 1 for m in mudadas)
COPIA.write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")
SAIDA.write_text(json.dumps({"ONDE": "COPIA — nada instalado", "COPIA": str(COPIA),
                             "COPIA_SHA256": hashlib.sha256(COPIA.read_bytes()).hexdigest(),
                             "MUDADAS": mudadas,
                             "LINHAS": [x for x in linhas if x["CANDIDATA_ID"] in {m["CANDIDATA_ID"] for m in mudadas}]},
                            ensure_ascii=False, indent=1), encoding="utf-8")
for m in mudadas:
    print(m)
