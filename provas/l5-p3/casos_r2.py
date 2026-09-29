# -*- coding: utf-8 -*-
"""L5-P3 · VOLTA 2 · um caso MEU por causa apontada (D150). Pela interface.

    py -3.12 provas/l5-p3/casos_r2.py

Estes casos sao meus, escritos a partir das causas GENERICAS que o coordenador
mandou. Nao reconstroem o gabarito: nenhum vem do golden set, que nao foi aberto.
Cada um prova UMA das oito causas, com o que passa a sair e porque.
"""
import os
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)

from interface import extrair_proposto, extrair_atual   # noqa: E402

BASE = "JSON-LD datePublished"


def caso(nome, causa, texto, alvo_trecho, espera, pub=None, basis=BASE, contrato=None, campo="FACT_TIME"):
    entrada = {"TEXTO": texto, "PUBLISHED_AT_DA_SALA": pub,
               "PUBLISHED_AT_BASIS_DA_SALA": basis if pub else None,
               "CAPTURED_AT": "2026-09-29T02:00:00Z"}
    if contrato:
        entrada["CONTRATO_DA_FONTE"] = contrato
    p = texto.find(alvo_trecho)
    alvo = {"TRECHO": alvo_trecho, "OFFSET": p, "FIM": p + len(alvo_trecho)}
    r = extrair_proposto(entrada, alvo)
    saiu = r[campo]["VALOR"]
    ok = saiu == espera
    print("%-4s C%s %-34s %s=%-28s %s" % ("OK" if ok else "FALHA", causa, nome, campo, saiu,
                                          "" if ok else "(esperado %s)" % espera))
    if not ok:
        print("       porque: %s" % str(r[campo].get("PORQUE"))[:150])
    return ok, r


def main():
    resultados = []

    # C1 · o ato de OUTRA afirmacao nao e o ato desta. Uma lei antiga citada de passagem
    # no fim do documento nao pode datar a afirmacao do campo.
    T1 = ("Nei rilievi di campo sono state riscontrate infezioni sui frutteti della zona. "
          "Ai sensi del decreto legislativo 14 agosto 2012, n. 150, l'uso sostenibile dei "
          "prodotti fitosanitari e disciplinato dalle norme tecniche regionali.")
    resultados.append(caso("ato de outra afirmacao", 1, T1,
                           "Nei rilievi di campo sono state riscontrate infezioni sui frutteti della zona",
                           "NAO_EXISTE", campo="ACT_TIME")[0])
    # e o ato REFERIDO pela afirmacao continua a sair
    T2 = ("Con Determinazione n. 9818 del 20/05/2026 sono state fissate le prescrizioni. "
          "Nei vigneti a conduzione integrata, secondo la Determinazione n. 9818, sono stati "
          "osservati attacchi diffusi.")
    resultados.append(caso("ato referido pela afirmacao", 1, T2,
                           "secondo la Determinazione n. 9818, sono stati osservati attacchi diffusi",
                           "2026-05-20", campo="ACT_TIME")[0])

    # C2 · ano do cabecalho inequivoco da MESMA edicao, precisao DIA, com composicao
    T3 = ("Bollettino fitosanitario n. 17/2026 del 04.05.2026\nVITICOLTURA\n"
          "Nei monitoraggi eseguiti giovedi 30 aprile il Servizio fitosanitario cantonale ha "
          "rilevato infezioni nei vigneti della zona collinare.")
    ok, r = caso("ano do cabecalho -> DIA", 2, T3,
                 "Nei monitoraggi eseguiti giovedi 30 aprile", "2026-04-30")
    resultados.append(ok and r["FACT_TIME"]["ORIGEM"] == "CABECALHO"
                      and r["FACT_TIME"]["PRECISAO"] == "DIA"
                      and bool(r["FACT_TIME"].get("ANO_BASIS"))
                      and bool(r["FACT_TIME"].get("PROCEDENCIA_DO_ANO")))
    print("       ORIGEM=%s PRECISAO=%s ANO_BASIS=%s" % (
        r["FACT_TIME"]["ORIGEM"], r["FACT_TIME"]["PRECISAO"],
        (r["FACT_TIME"].get("ANO_BASIS") or {}).get("EXPRESSAO")))
    # ano concorrente no cabecalho -> NAO SEI no ano (nunca chutar)
    T4 = ("Bollettino n. 5 del 2026 · archivio storico 2025\nVITICOLTURA\n"
          "Nei monitoraggi eseguiti giovedi 30 aprile sono state rilevate infezioni nei vigneti.")
    resultados.append(caso("ano concorrente -> sem ano", 2, T4,
                           "Nei monitoraggi eseguiti giovedi 30 aprile", "SEM_ANO-04-30")[0])

    # C3 · ano economico atribuido ao facto = FACT_TIME com precisao ANO (D147 item 3)
    T5 = ("La campagna olivicola ha chiuso il 2025 con una produzione dimezzata dalla siccita "
          "osservata nei campi della provincia.")
    ok, r = caso("ano economico -> FACT ANO", 3, T5,
                 "ha chiuso il 2025 con una produzione dimezzata dalla siccita", "2025", pub="2026-03-01")
    resultados.append(ok and r["FACT_TIME"]["PRECISAO"] == "ANO")
    # o ano historico de OUTRO facto continua barrado
    T6 = "La Xylella fastidiosa e stata rilevata per la prima volta in Europa nel 2004, in Puglia."
    resultados.append(caso("ano historico de outro facto", 3, T6,
                           "rilevata per la prima volta in Europa nel 2004", "NAO_SEI",
                           pub="2026-09-01")[0])

    # C4 · a relativa ancorada na publicacao nao rebenta mais a interface
    T7 = "Ieri la grandinata ha colpito i vigneti della zona collinare della provincia."
    ok, r = caso("relativa D63 sem rebentar", 4, T7, T7, "2026-09-25", pub="2026-09-26")
    resultados.append(ok and isinstance(r["FACT_TIME"].get("ANO_BASIS"), dict))

    # C5 · cabecalho com as letras dobradas pelo PDF
    T8 = ("BBOOLLLLEETTTTIINNOO nn.. 2200//22002266\nSSIITTUUAAZZIIOONNEE\n"
          "Nei rilievi del 18 maggio sono state riscontrate infezioni nei frutteti della provincia.")
    resultados.append(caso("cabecalho dobrado pelo PDF", 5, T8,
                           "Nei rilievi del 18 maggio sono state riscontrate infezioni", "2026-05-18")[0])

    # C6 · PUBLICATION_TIME pelo metadado da entrada
    T9 = "Nei frutteti della zona sono state riscontrate infezioni diffuse sulle cultivar tardive."
    ok, r = caso("publicacao pelo metadado", 6, T9, T9, "2026-09-20",
                 pub="2026-09-20", campo="PUBLICATION_TIME")
    resultados.append(ok and r["PUBLICATION_TIME"]["ORIGEM"] == "METADADO_DA_ENTRADA")
    # e NUNCA no facto
    resultados.append(r["FACT_TIME"]["VALOR"] == "NAO_SEI")
    print("       FACT com metadado de publicacao = %s (tem de ser NAO_SEI)" % r["FACT_TIME"]["VALOR"])

    # C7 · conhecimento sem acontecimento -> FACT_TIME = NAO_EXISTE
    T10 = ("La Bactrocera oleae e un dittero le cui larve si nutrono della polpa delle olive; "
           "il ciclo si completa in tre settimane.")
    resultados.append(caso("ficha tecnica -> NAO_EXISTE", 7, T10,
                           "La Bactrocera oleae e un dittero le cui larve si nutrono della polpa delle olive",
                           "NAO_EXISTE")[0])

    # C8 · o contrato da fonte chega a logica
    T11 = ("MOSCA DELLE OLIVE 14/09/2026 - 20/09/2026 COMPRENSORIO BR\n"
           "Nei rilievi di campo la infestazione risulta bassa sulle cultivar da olio.")
    ok, r = caso("contrato VALIDADE", 8, T11, "MOSCA DELLE OLIVE 14/09/2026 - 20/09/2026",
                 "2026-09-14/2026-09-20", contrato="VALIDADE", campo="VALIDITY_TIME")
    resultados.append(ok)
    ok2, r2 = caso("contrato EDICAO", 8, T11, "MOSCA DELLE OLIVE 14/09/2026 - 20/09/2026",
                   "2026-09-14/2026-09-20", contrato="EDIZIONE", campo="PERIODO_DA_EDICAO")
    resultados.append(ok2 and r2["VALIDITY_TIME"]["VALOR"] in ("NAO_EXISTE", "NAO_SEI"))
    print("       com EDICAO, VALIDITY = %s (nunca o periodo da edicao)" % r2["VALIDITY_TIME"]["VALOR"])

    # C9 · relativa de semana ancorada no periodo IMPRESSO do mesmo boletim (D63/D149)
    T12 = ("BOLLETTINO settimana 39 dal 22/09/2026 al 29/09/2026\n"
           "Questa settimana sono stati osservati attacchi di peronospora nei vigneti della zona.")
    ok, r = caso("semana relativa pela edicao", 9, T12,
                 "Questa settimana sono stati osservati attacchi di peronospora",
                 "2026-09-22/2026-09-29")
    resultados.append(ok and bool(r["FACT_TIME"].get("COMPOSICAO")))
    print("       composicao: %s" % str((r["FACT_TIME"].get("COMPOSICAO") or {}).get("CONTA")))

    print("\nCASOS_R2 %d/%d" % (sum(1 for x in resultados if x), len(resultados)))
    return 0 if all(resultados) else 1


if __name__ == "__main__":
    raise SystemExit(main())
