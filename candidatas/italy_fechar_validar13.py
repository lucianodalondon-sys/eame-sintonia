#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
VALIDAR AS 13 DA SEGUNDA VAGA — e a SEGUNDA PROVA das criticas.

Mesma disciplina das 37: abrir a rota, oito estados, exemplo real obrigatorio
para STRONG e USEFUL. Nada entra por ter sido bem descrito.

A SEGUNDA PROVA E' POR OUTRO CAMINHO, senao nao e' segunda
----------------------------------------------------------
Confirmar uma fonte abrindo a MESMA rota outra vez nao prova nada — prova que
o cache funciona. Aqui a segunda prova de cada fonte CRITICAL usa uma rota
DIFERENTE do mesmo dono (o dominio raiz, ou o indice da serie), e compara se
a casa se declara a mesma.

    CONFIRMED  a segunda rota abre e confirma dono e assunto
    DIVERGED   a segunda rota contradiz a primeira
    UNKNOWN    nao consegui a segunda rota

DIVERGED nao vai para READY_TO_REGISTER, por muitos pontos que tenha.
"""

import json
import re
import sys
from collections import Counter
from pathlib import Path
from urllib.parse import urlparse

RAIZ = Path(__file__).resolve().parents[1]
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "candidatas"))
TRAB = Path("C:/Users/London1/AppData/Local/Temp/sintonia-fechar")

from italy_fechar_sonda import julgar, correr_controles          # noqa: E402
from italy_fechar_descoberta import TODAS_NOVAS                  # noqa: E402

# palavra que a segunda rota TEM de conter para confirmar o dono
ASSINATURA = {
 "SAL — Servizio Agrometeorologico Lucano, e os bollettini do SeDI": r"alsia",
 "Avvisi fitosanitari per viticoltori e per frutticoltori": r"valle d'aosta|vall[eé]e|regione autonoma",
 "Dati di maturazione dell'uva e scelta della data di vendemmia": r"institut agricole|iar\b",
 "Bollettini colture estensive / seminativi": r"veneto",
 "Bollettini interprovinciali di produzione integrata e biologica": r"emilia-romagna|emilia romagna",
 "Bollettini di difesa integrata — colture erbacee (mais e soia)": r"ersa|friuli",
 "Bollettino Mais": r"lombardia",
 "Bollettino Colture Erbacee": r"veneto agricoltura|veneto",
 "Bollettini fitosanitari — Unita territoriali di monitoraggio (UTM)": r"campania",
 "Bollettini di produzione integrata — pomodoro da industria": r"fitosanitario|consorzio",
 "Bollettino seminativi biologici": r"aiab|biolog",
 "Bollettini AgroAmbiente e Disciplinare di Produzione Integrata": r"abruzzo",
 "IrriNet e FERTIRRINET": r"irri",
}


def segunda_rota(url):
    """Outra rota do MESMO dono: a raiz do dominio."""
    p = urlparse(url)
    return f"{p.scheme}://{p.netloc}/"


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    if correr_controles():
        sys.exit("!! controles da sonda falharam")
    print()

    linhas = []
    for f in TODAS_NOVAS:
        r = julgar(f["URL"])
        base = r["VEREDITO"]
        tem_ex = bool(f.get("EXEMPLO_REAL"))
        critica = f["GAP_FECHA"].startswith("CRITICAL")

        if base in ("BROKEN", "BLOCKED", "UNKNOWN", "WRONG_SOURCE"):
            ver, porque = base, r["PORQUE"]
        elif not tem_ex:
            ver, porque = "VALIDATED_BUT_SECONDARY", "sem exemplo real declarado"
        elif f["CLASSE"] == "A" and f["RECORRENCIA"].startswith("HIGH"):
            ver = "VALIDATED_STRONG"
            porque = (f"abre ({r['TAMANHO_TEXTO']} caracteres, "
                      f"{r.get('N_SINAIS', 0)} palavras do assunto), exemplo "
                      "real datado, recorrencia HIGH, PRIMARY")
        else:
            ver = "VALIDATED_USEFUL"
            porque = f"abre e serve. {r['PORQUE']}"

        # ── SEGUNDA PROVA: obrigatoria nas CRITICAL ──
        prova2, prova2_porque = "", ""
        if critica or ver == "VALIDATED_STRONG":
            u2 = segunda_rota(f["URL"])
            r2 = julgar(u2)
            assin = ASSINATURA.get(f["NOME"], "")
            if r2["VEREDITO"] in ("BROKEN", "UNKNOWN"):
                prova2 = "UNKNOWN"
                prova2_porque = (f"a segunda rota ({u2}) nao abriu: "
                                 f"{r2['VEREDITO']}. Nao confirma nem desmente.")
            else:
                cache = TRAB / "paginas"
                chave = re.sub(r"[^a-z0-9]+", "_", u2.lower())[:120] + ".json"
                txt = ""
                if (cache / chave).exists():
                    txt = json.loads((cache / chave).read_text(
                        encoding="utf-8"))["texto"]
                if assin and re.search(assin, txt, re.I):
                    prova2 = "CONFIRMED"
                    prova2_porque = (f"segunda rota independente ({u2}) abre e "
                                     f"a casa declara-se «{assin}» no texto.")
                else:
                    prova2 = "DIVERGED" if assin else "UNKNOWN"
                    prova2_porque = (f"segunda rota ({u2}) abre mas NAO achei a "
                                     f"assinatura do dono («{assin}»). "
                                     "Nao promovo sem confirmar o dono.")

        linhas.append({
            "SOURCE_NAME": f["NOME"], "OWNER": f["DONO"],
            "URL_DECLARED": f["URL"], "URL_FINAL": r["URL_FINAL"],
            "URL_CANONICAL": r["URL_FINAL"],
            "REDIRECIONOU": r["REDIRECIONOU"], "HTTP": r["HTTP"],
            "TAMANHO_TEXTO": r["TAMANHO_TEXTO"],
            "SOURCE_TYPE": f["CLASSE"], "COUNTRY": "IT",
            "REGION_SCOPE": f["AMBITO"], "TERRITORIES": " ".join(f["TERR"]),
            "CULTURAS_QUE_NOMEIA": " · ".join(f["CULTURAS_QUE_NOMEIA"]) or "—",
            "WHAT_IT_PRODUCES": f["PRODUZ"],
            "WHICH_RAW_NEED_IT_FEEDS": " || ".join(f["ALIMENTA"]),
            "WHICH_TOOL_IT_SUPPORTS": " · ".join(
                sorted({a.split(" · ")[0] for a in f["ALIMENTA"]})),
            "EXAMPLE_REAL": f["EXEMPLO_REAL"],
            "EXAMPLE_URL": r["URL_FINAL"],
            "LAST_ACTIVITY_OBSERVED": r.get("DATAS_NA_PAGINA", "") or "NAO SEI",
            "RECURRING_INFORMATION_POTENTIAL": f["RECORRENCIA"],
            "PRIMARY_OR_SECONDARY": f["PRIMARIA"],
            "GAP_CLOSURE_VALUE": f["GAP_FECHA"].split(" — ")[0],
            "GAP_FECHA_QUAL": f["GAP_FECHA"],
            "VALIDATION": ver, "VALIDATION_PORQUE": porque,
            "SEGUNDA_PROVA": prova2 or "NAO_EXIGIDA",
            "SEGUNDA_PROVA_PORQUE": prova2_porque,
            "EVIDENCE": f["EVIDENCIA"], "LIMITE": f["LIMITE"],
            "VALIDATED_AT": "2026-09-14 (sonda urllib, UA de navegador)"})

    (TRAB / "VALIDADAS-13.json").write_text(
        json.dumps(linhas, ensure_ascii=False, indent=1), encoding="utf-8")

    print("VALIDACAO DA SEGUNDA VAGA (13)")
    print("=" * 96)
    for l in sorted(linhas, key=lambda x: x["VALIDATION"]):
        print(f"  {l['VALIDATION']:24s} {l['SEGUNDA_PROVA']:12s} "
              f"HTTP{str(l['HTTP']):>4s} {str(l['TAMANHO_TEXTO']):>7s}c  "
              f"{l['SOURCE_NAME'][:44]}")
    print("=" * 96)
    print("  validacao:", dict(Counter(l["VALIDATION"] for l in linhas)))
    print("  2a prova :", dict(Counter(l["SEGUNDA_PROVA"] for l in linhas)))
    print(f"gravado: {TRAB / 'VALIDADAS-13.json'}")


if __name__ == "__main__":
    main()
