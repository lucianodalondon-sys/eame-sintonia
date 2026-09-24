# -*- coding: utf-8 -*-
"""REND · a tabela «vale a pena correr agora?» por fonte.

Junta, SEM rede e SEM escrever em livro nenhum:
  medidas/entrada-*.json     o que cada pagina de entrada anuncia hoje (medir_entrada.mjs)
  medidas/sala-por-fonte.json o historico da fonte na Sala (RAW, DERIVED, SIM)
  medidas/gate-vivo.json      as 37 do portao (collection_gate.py --json no vivo)
  COORTE-BIG-COLLECTION-V1    quem esta na coorte da 1.a onda (18) e porque as outras 19 nao
  R1-REENSAIO (ramo reparo-fontes-v2) as 46 READY que a R1 traria

O veredito e uma SUGESTAO. Quem decide a agenda e o Curator/Collection.

Uso: py ferramentas/rendimento/tabela.py --r1 <R1-REENSAIO-ANTES-DEPOIS-fca4f2b6.json>
"""
import json
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
M = AQUI / "medidas"
# As reguas da Admissao que existem no codigo instalado (admissao.PERGUNTAS_DO_UNIVERSO, fca4f2b6).
COM_REGUA = {"T3", "T4", "T5", "T7", "T9", "T10"}


def ler(p):
    return json.loads(Path(p).read_text(encoding="utf-8"))


def linhas_de(*nomes):
    """A ultima medicao de cada fonte vence (os passos 2/3 sao as adiadas pelo teto)."""
    out = {}
    for n in nomes:
        for l in ler(M / n)["LINHAS"]:
            if l["SOURCE_ID"] in out and not str(l.get("ESTADO", "")).startswith("MEDIDA") \
                    and str(out[l["SOURCE_ID"]].get("ESTADO", "")).startswith("MEDIDA"):
                continue
            out[l["SOURCE_ID"]] = l
    return out


def veredito(l, u, no_coletor):
    e = str(l.get("ESTADO", ""))
    if u not in COM_REGUA:
        return "NAO", "sem regua de Admissao para %s: mesmo materia nova sai NAO_SEI, nunca SIM" % u, "PARADA ate haver regua"
    if not no_coletor:
        return "NAO", "sem contrato na tabela do coletor: o coletor recusa a fonte", "PARADA ate o contrato chegar ao coletor"
    if e.startswith("ADIADA_POR_CORTESIA"):
        return "NAO", "a porta de entrada nao se deixou pedir: " + e.split(":", 1)[1], "PARADA (robots/acesso)"
    if e == "INDICE_SEM_ALVO":
        return "NAO", "a entrada nao anuncia nenhum endereco que case com o padrao do contrato", "PARADA ate reparar o padrao"
    if not e.startswith("MEDIDA"):
        return "NAO", "entrada falhou: " + e, "PARADA"
    if l.get("UMA_CORRIDA_TRARIA", 0) > 0:
        return "SIM", "%d materia(s) nova(s) dentro da janela do contrato" % l["UMA_CORRIDA_TRARIA"], "DIARIA"
    if l.get("NOVAS_PARA_O_COLETOR", 0) > 0:
        return ("NAO", "%d nova(s) anunciada(s), mas FORA da janela: o contrato so olha as primeiras %s e essas ja estao no livro"
                % (l["NOVAS_PARA_O_COLETOR"], l.get("MAX_TARGETS")), "SEMANAL ate rever a janela (MAX_TARGETS)")
    return "NAO", "nada novo: tudo o que a entrada anuncia ja esta no livro", "SEMANAL"


def main(argv):
    r1p = argv[argv.index("--r1") + 1]
    sala = ler(M / "sala-por-fonte.json")["POR_FONTE"]
    gate = ler(M / "gate-vivo.json")
    coorte = ler(AQUI.parent / "big_collection" / "COORTE-BIG-COLLECTION-V1.json")
    na_coorte = {x["SOURCE_ID"] for x in coorte["COORTE"]}
    fora = {x["SOURCE_ID"]: x["FALTA"] for x in coorte["FORA"]}
    r1 = {x["SOURCE_ID"]: x for x in ler(r1p)["READY_NOVAS"]}
    e37 = linhas_de("entrada-37.json", "entrada-37-passo2.json", "entrada-37-passo3.json")
    # As 46 da R1 medem-se com os contratos REPARADOS, refeitos a partir do ramo
    # reparo-fontes-v2 numa banca (medidas/contratos-r1-reparados.json). A medida
    # com os contratos de antes do reparo (entrada-r1*.json) fica no ramo, so como historia.
    er1 = linhas_de("entrada-r1-reparado.json", "entrada-r1-reparado-passo2.json")
    rev = {x["SOURCE_ID"]: x for x in ler(M / "contratos-r1-reparados.json")["REVISAO"]["FONTES"]}

    jan = {}
    if (M / "janelas.json").exists():
        jan = ler(M / "janelas.json")["POR_FONTE"]
    tabela = []
    for grupo, ids, med in (("PORTAO_37", gate["COLLECTION_ELIGIBLE_IDS"], e37), ("R1_46", list(r1), er1)):
        for s in ids:
            l = med[s]
            u = s.split("-")[1]
            no_coletor = l.get("CONTRATO") == "COLETOR"
            # R1: a falta de contrato no coletor e um bloqueio a mais, nao o veredito —
            # mede-se a entrada como se o contrato do curador ja la estivesse.
            v, porque, cad = veredito(l, u, no_coletor or grupo == "R1_46")
            # o que a entrada promete se os bloqueios caissem (regua e entrada medida)
            potencial = (l.get("UMA_CORRIDA_TRARIA") or 0) if str(l.get("ESTADO", "")).startswith("MEDIDA") else None
            # bloqueio de porta: fora da coorte congelada, ou R1 ainda nao instalada
            if v == "SIM" and grupo == "PORTAO_37" and s not in na_coorte:
                v, porque, cad = "NAO", "a entrada tem novidade, mas a fonte esta fora da coorte: " + ",".join(fora.get(s, ["?"])), "PARADA ate sair o bloqueio"
            sinais = (rev.get(s) or {}).get("SINAIS") or []
            if grupo == "R1_46":
                if v == "SIM":
                    if no_coletor:
                        v, porque, cad = "DEPOIS_DA_R1", "a entrada tem novidade; corre quando a R1 for instalada e a fonte passar o portao", "DIARIA depois da R1"
                    else:
                        v, porque, cad = ("DEPOIS_DA_R1_E_DO_CONTRATO",
                                          "a entrada tem novidade; falta a R1 E o contrato na tabela do coletor (hoje so existe no curador)",
                                          "DIARIA depois da R1 e do contrato")
                if [x for x in sinais if x.startswith("CAMINHO_DE_SERVICO")]:
                    porque += " [SUSPEITA: o item que o canario abriu e pagina de servico — %s; ler antes de correr]" % "; ".join(sinais)
                elif sinais:
                    porque += " [sinal: %s]" % "; ".join(sinais)
            h = sala.get(s, {"RAW": 0, "DERIVED": 0, "SIM": 0, "SIM_ULTIMO": None})
            if grupo == "PORTAO_37":
                onde = "COORTE_1A_ONDA" if s in na_coorte else "FORA_DA_COORTE:" + ",".join(fora.get(s, ["?"]))
            else:
                onde = "R1_NAO_INSTALADA:%s" % r1[s]["CAUSA"]
            tabela.append({
                "SOURCE_ID": s, "GRUPO": grupo, "ONDE": onde, "UNIVERSO": u, "REGUA": u in COM_REGUA,
                "CONTRATO": l.get("CONTRATO"), "ESTADO_DA_ENTRADA": l.get("ESTADO"),
                "ANUNCIA_HOJE": l.get("ANUNCIADAS"), "NOVAS_PARA_O_COLETOR": l.get("NOVAS_PARA_O_COLETOR"),
                "NOVAS_PARA_O_ACERVO": l.get("NOVAS_PARA_O_ACERVO"), "MAX_TARGETS": l.get("MAX_TARGETS"),
                "NOVAS_NA_JANELA": l.get("NOVAS_NA_JANELA"), "UMA_CORRIDA_TRARIA": l.get("UMA_CORRIDA_TRARIA"), "POTENCIAL_SEM_BLOQUEIO": potencial,
                "HIST_RAW": h["RAW"], "HIST_DERIVED": h["DERIVED"], "HIST_SIM": h["SIM"], "HIST_SIM_ULTIMO": h["SIM_ULTIMO"],
                "JANELA_DE_CULTURA": jan.get(s, {}).get("JANELA", "NAO_SEI"),
                "JANELA_FORCA": jan.get(s, {}).get("FORCA"), "JANELA_EXEMPLO_URL": jan.get(s, {}).get("EXEMPLO_URL"),
                "SINAIS_DA_REVISAO_R1": sinais or None, "ITEM_DO_CANARIO_R1": (rev.get(s) or {}).get("ITEM"),
                "VALE_CORRER_AGORA": v, "PORQUE": porque, "CADENCIA_SUGERIDA": cad,
                "INDEX_SHA256": l.get("INDEX_SHA256"), "PEDIDO_EM": l.get("PEDIDO_EM")})

    # D29 (dono): a janela de cultura PESA na ordem. Primeiro o que corre agora,
    # depois o que corre depois da R1; dentro de cada degrau, janela forte >
    # janela fraca > sem prova; depois o que uma corrida traria e o potencial.
    degrau = {"SIM": 0, "DEPOIS_DA_R1": 1, "DEPOIS_DA_R1_E_DO_CONTRATO": 2, "NAO": 3}
    suspeita = lambda x: 1 if "SUSPEITA" in x["PORQUE"] else 0
    peso_j = lambda x: 0 if (x["JANELA_FORCA"] or "").startswith("FORTE") else (1 if x["JANELA_DE_CULTURA"] == "SIM" else (2 if x["JANELA_DE_CULTURA"] == "NAO_SEI" else 3))
    tabela.sort(key=lambda x: (degrau[x["VALE_CORRER_AGORA"]], suspeita(x), peso_j(x), -(x["UMA_CORRIDA_TRARIA"] or 0),
                               -(x["POTENCIAL_SEM_BLOQUEIO"] or 0), -(x["NOVAS_PARA_O_COLETOR"] or 0), x["SOURCE_ID"]))
    for i, x in enumerate(tabela, 1):
        x["ORDEM"] = i

    def conta(g):
        t = [x for x in tabela if x["GRUPO"] == g]
        por = {}
        for x in t:
            chave = x["PORQUE"].split(":")[0].split(" (")[0]
            if x["VALE_CORRER_AGORA"] != "NAO":
                chave = x["VALE_CORRER_AGORA"]
            elif x["PORQUE"].startswith("a entrada tem novidade, mas"):
                chave = "novidade, mas fora da coorte"
            elif chave.startswith("%d" % (x.get("NOVAS_PARA_O_COLETOR") or 0)) or "FORA da janela" in x["PORQUE"]:
                chave = "novas fora da janela"
            por[chave] = por.get(chave, 0) + 1
        return {"FONTES": len(t), "VALE_AGORA": sum(x["VALE_CORRER_AGORA"] == "SIM" for x in t),
                "MATERIAS_NUMA_CORRIDA": sum(x["UMA_CORRIDA_TRARIA"] or 0 for x in t if x["VALE_CORRER_AGORA"] == "SIM"),
                "NOVAS_ANUNCIADAS_COM_REGUA_E_CONTRATO": sum(x["NOVAS_PARA_O_COLETOR"] or 0 for x in t if x["REGUA"] and x["CONTRATO"] == "COLETOR"),
                "POR_MOTIVO": por,
                "JANELA_DE_CULTURA": {k: sum(x["JANELA_DE_CULTURA"] == k for x in t) for k in ("SIM", "NAO", "NAO_SEI")}}

    d = {"DATASET": "REND-TABELA-V1",
         "O_QUE_E": "vale a pena correr agora? por fonte — SUGESTAO; a agenda e do Curator/Collection",
         "REGRA": ("SIM so se: universo com regua de Admissao E contrato no coletor E entrada pedida com cortesia "
                   "E pelo menos 1 materia nunca vista DENTRO da janela do contrato (MAX_TARGETS, teto 3 materias/site/corrida)"),
         "RESUMO": {"PORTAO_37": conta("PORTAO_37"), "R1_46": conta("R1_46")},
         "TABELA": tabela}
    (AQUI / "REND-TABELA-V1.json").write_text(json.dumps(d, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(json.dumps(d["RESUMO"], ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
