# -*- coding: utf-8 -*-
"""ORDENS-63 v2 · gera curadoria/DECISAO-D52-RETIRAR-V1.json — as 62 SOURCE_ID que a D52 retira, cada
uma com a SUA prova guardada pelo robo. Sem rede; so leitura do vivo.

    py scripts/ordens_63/gerar_d52.py <EXTRACAO-182-V1.json> <CLASSIFICACAO-182-V1.json>

Le tambem o LIFECYCLE-LEDGER do vivo (so leitura) para a referencia da prova de cada uma.
As duas entradas sao as da RECEITAS-182 (`receitas-182-v1 @ 41d8751e`): a extracao traz, de cada fonte,
a ultima prova do robo (LIFECYCLE-EVIDENCE: motivo, entrada, retrato, paginas lidas); a classificacao
diz quais sao SITE_DE_ORDEM_PROFISSIONAL. Palermo (IT-T7-226) fica de fora: D52 manda-a ficar activa.
"""
import hashlib
import json
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parents[1]
FICA_ACTIVA = {"IT-T7-226"}

ext_p, cla_p = Path(sys.argv[1]), Path(sys.argv[2])
ext = json.loads(ext_p.read_text(encoding="utf-8"))
cla = json.loads(cla_p.read_text(encoding="utf-8"))
prova = {f["SOURCE_ID"]: f for f in ext["FONTES"]}
VIVO = Path(r"C:/Users/London1/orca/workspaces/eame-sintonia/source-curator-service-v1")
ult = {}
for t in json.loads((VIVO / "curadoria" / "LIFECYCLE-LEDGER-V1.json").read_text(encoding="utf-8"))["TRANSICOES"]:
    ult[t.get("SOURCE_ID")] = t
fontes = []
for x in cla["FONTES"]:
    if x["FORMA"] != "SITE_DE_ORDEM_PROFISSIONAL" or x["SOURCE_ID"] in FICA_ACTIVA:
        continue
    f = prova[x["SOURCE_ID"]]
    p = f.get("PROVA") or {}
    fontes.append({
        "SOURCE_ID": x["SOURCE_ID"], "ENTRADA": x["ENTRADA"], "HOST": x["HOST"],
        "PORQUE": "so avisos institucionais de ordem profissional (sem noticia agronomica datada com corpo): %s"
                  % (p.get("PORQUE") or f.get("REASON") or "")[:220],
        "PROVA": {"EVIDENCE_REF": (ult.get(x["SOURCE_ID"]) or {}).get("EVIDENCE_REF"),
                  "ESTADO_NO_VIVO": (ult.get(x["SOURCE_ID"]) or {}).get("NEW_STATE"),
                  "ETAPA": f.get("ETAPA"), "OBSERVADO_EM": f.get("OBSERVED_AT"),
                  "MOTIVO_DO_ROBO": p.get("MOTIVO") or (f.get("REASON") or "").split(":")[0],
                  "ENTRADA_RETRATO": p.get("ENTRADA_RETRATO"), "PAGINAS_LIDAS": p.get("PAGINAS_LIDAS")},
    })
out = {
    "DATASET": "DECISAO-D52-RETIRAR-V1",
    "DECISAO": "D52",
    "DECIDIDO_POR": "bot Luciano (25/09), sobre ORDENS-63 (ordens-63-v1 @ 7648c995)",
    "O_QUE": "RETIRADA_POR_DECISAO (a marca de catalogo da D9), POR SOURCE_ID; nunca o dominio conaf.it inteiro; "
             "nada apagado; reversivel (curadoria/retirar_por_decisao.py --reverter)",
    "VOLTA": "pelo circuito normal do Curator se a fonte passar a publicar conteudo agronomico",
    "D2": "noticias uteis ja preservadas seguem a D2 — medido: 0 observacoes destas 62 no livro de coleta",
    "PROVA_GERAL": {"AMOSTRA_DE_REDE": "scripts/ordens_63/MEDIDA-ORDENS-V1.json (feed de ordinelivorno: 10 posts em 9 meses, 0-169 letras)",
                    "EXTRACAO": {"FICHEIRO": "scripts/receitas_182/EXTRACAO-182-V1.json @ receitas-182-v1",
                                 "SHA256": hashlib.sha256(ext_p.read_bytes()).hexdigest(),
                                 "LIVROS_DO_VIVO": ext.get("LIDO_SHA256"), "VIVO_HEAD": ext.get("VIVO_HEAD")}},
    "FICA_ACTIVA": sorted(FICA_ACTIVA),
    "TOTAL": len(fontes),
    "FONTES": fontes,
}
(RAIZ / "curadoria" / "DECISAO-D52-RETIRAR-V1.json").write_text(
    json.dumps(out, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
print(len(fontes))
