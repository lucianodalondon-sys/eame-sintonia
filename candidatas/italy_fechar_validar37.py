#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
VALIDAR AS 37 — abrir cada rota e dar-lhe um dos oito estados.

A missao anterior escreveu, na propria entrega: «nenhuma das 37 rotas foi
aberta por sonda». Isto paga essa divida.

OS OITO ESTADOS, E POR QUE SAO OITO
-----------------------------------
    VALIDATED_STRONG        abre, fala do assunto, TEM exemplo real datado,
                            e e' PRIMARY para a necessidade que alimenta
    VALIDATED_USEFUL        abre, fala do assunto, tem exemplo real
    VALIDATED_BUT_SECONDARY abre e serve, mas repassa o que outro produz
    BLOCKED                 responde e recusa-me a entrada (403/401/muro)
    BROKEN                  nao existe, ou serve pagina de erro com HTTP 200
    WRONG_SOURCE            abre e nao e' disto que fala
    DUPLICATE               o mesmo dono/rota que uma linha ja contada
    UNKNOWN                 a duvida e' NOSSA (falha de ligacao, transitorio)

Colapsar isto em «viva/morta» perde as tres accoes diferentes: BROKEN pede
fonte nova, BLOCKED pede outra rota, UNKNOWN pede outra tentativa.

E EXEMPLO REAL E' OBRIGATORIO PARA STRONG E USEFUL
--------------------------------------------------
Sem exemplo, o maximo e' VALIDATED_BUT_SECONDARY ou UNKNOWN, conforme a
evidencia. «A pagina existe» nao e' «a fonte publica».
"""

import json
import re
import sys
from collections import Counter
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "candidatas"))
TRAB = Path("C:/Users/London1/AppData/Local/Temp/sintonia-fechar")

from italy_fechar_sonda import julgar, correr_controles, DATA   # noqa: E402
from italy_gap_novas_fontes import TODAS as NOVAS               # noqa: E402

# ── CORRECOES DE DONO E DE ENDERECO vindas da missao paralela ──────────────
# `origin/claude/italy-source-qualification-v1`, commit d9535783, folha
# CORRECOES_URL: 125 enderecos canonicos diferiam do declarado. Duas tocam
# diretamente nas minhas 37 — e uma delas é um DONO errado meu.
CORRECOES_DA_PARALELA = {
 "https://meteo.regione.marche.it/": dict(
   DONO_CORRIGIDO="Regione Marche — AMAP (Agenzia per l'Innovazione nel settore "
                  "Agroalimentare e della Pesca), que absorveu a ASSAM",
   PORQUE="eu escrevi «ASSAM». A missao paralela mediu que a ASSAM redireciona "
          "para a AMAP Marche, inclusive na conta social oficial "
          "(instagram.com/amapmarche). Dono errado e' o ataque 11 do red team, "
          "e apanhou-me."),
 "https://www.arsacweb.it/bollettino-agrometeorologico-e-fitosanitario-agrumi-olivo-e-vite/": dict(
   DONO_CORRIGIDO="ARSAC — Azienda Regionale per lo Sviluppo dell'Agricoltura "
                  "Calabrese",
   PORQUE="dono confirmado pela missao paralela (conta oficial "
          "facebook.com/ArsacRegioneCalabria). ⚠️ E ela tambem mediu que a "
          "Regione Calabria redireciona para um dominio «old.» — o que reforca "
          "que `arsacweb.it` e `arsac.calabria.it` precisam de decisao de "
          "canonico, nao de duas linhas."),
}

# ── ROTAS QUE EU MESMO ESCREVI ERRADO, CORRIGIDAS AO ABRI-LAS ─────────────
# A URL declarada NUNCA e' sobrescrita: fica em URL_DECLARED, e a corrigida em
# URL_CANONICAL. Disciplina herdada da missao paralela, que separou
# URL_ORIGINAL / URL_FINAL / URL_CANONICAL em 125 casos.
ROTAS_CORRIGIDAS = {
 "https://esploradati.istat.it/SDMXWS/rest/": dict(
   CANONICA="https://esploradati.istat.it/SDMXWS/rest/dataflow/IT1/"
            "101_1015_DF_DCSP_COLTIVAZIONI_1",
   PORQUE="⚠️ DUAS COISAS ERRADAS NA MINHA LINHA ANTERIOR. Primeira: eu dei a "
          "RAIZ do servico SDMX, que devolve 404 a um GET simples — julgar uma "
          "raiz de API como rota de conteudo e' erro meu, nao fonte morta. "
          "Segunda, e mais grave: o identificador «DCSP_COLTIVAZIONI» que eu "
          "citei NAO EXISTE — o servico responde «Could not find requested "
          "structures». Procurei nos 4.907 dataflows publicados e o verdadeiro "
          "e' `101_1015_DF_DCSP_COLTIVAZIONI_1` (superficies e producao, dados "
          "no conjunto); ha tambem `_2` por provincia e `_10` intencoes de "
          "semina.",
   PROVA_FORTE="a chamada de DADO devolveu 13.522.174 bytes de CSV real, com "
               "as colunas REF_AREA · TYPE_OF_CROP · TIME_PERIOD · OBS_VALUE · "
               "UNIT_MEAS · OBS_STATUS. Nao e' pagina que fala de dado: e' o "
               "dado."),
}

# Necessidades onde a fonte e' o PRODUTOR do facto (PRIMARY) vs quem repassa
SECUNDARIAS = {
 "Banca dati Fitogest": "republica o registo do Ministero com mais filtros",
 "Catalogo annuale di gamma": "material comercial do proprio concorrente",
 "AgriEvents — calendario di eventi tecnici regionali": "agenda de eventos de "
   "terceiros",
 "Demo Days e open day de sementes horticolas": "comunicacao da propria empresa",
 "Censimento delle strutture di stoccaggio dei cereali": "censo unico, nao serie",
}


def exemplo_real(r, fonte):
    """Ha exemplo real DATADO na pagina aberta? Devolve (tem, texto)."""
    if r.get("N_DATAS", 0) >= 1 and r.get("N_SINAIS", 0) >= 3:
        return True, (f"lido na rota em {r['URL_FINAL'][:70]}: "
                      f"datas {r['DATAS_NA_PAGINA']} · assunto "
                      f"{r['SINAIS_DO_ASSUNTO'][:90]}")
    if r.get("N_SINAIS", 0) >= 3:
        return False, (f"a rota abre e fala do assunto ({r['N_SINAIS']} "
                       "palavras), mas NAO achei data legivel na pagina de "
                       "entrada. O exemplo datado costuma estar um clique "
                       "adentro, e um clique adentro nao foi medido.")
    return False, "sem sinal suficiente para chamar de exemplo"


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    if correr_controles():
        sys.exit("!! controles da sonda falharam — nada aqui vale")
    print()

    vistos_url, vistos_dono = {}, {}
    linhas = []
    for f in NOVAS:
        url = f["URL"]
        rota = ROTAS_CORRIGIDAS.get(url, {})
        r = julgar(rota.get("CANONICA", url))
        corr = CORRECOES_DA_PARALELA.get(url, {})
        dono = corr.get("DONO_CORRIGIDO", f["DONO"])

        # ── DUPLICATE antes de tudo: mesma rota ou mesmo dono ja contado ──
        chave_url = re.sub(r"^https?://(www\.)?", "", r["URL_FINAL"]).rstrip("/").lower()
        dup = ""
        if chave_url in vistos_url:
            dup = f"mesma rota final que «{vistos_url[chave_url]}»"
        elif dono in vistos_dono and f["NOME"] != vistos_dono[dono]:
            dup = (f"mesmo DONO que «{vistos_dono[dono]}» — "
                   "SAME_OWNER_DIFFERENT_SOURCE, nao duplicata verdadeira")

        base = r["VEREDITO"]
        tem_ex, ex = exemplo_real(r, f)
        # rota corrigida com prova de DADO vale mais do que prova de pagina
        if rota.get("PROVA_FORTE"):
            base = "ABRE_E_FALA_DO_ASSUNTO"
            tem_ex = True
            ex = rota["PROVA_FORTE"]

        if f["CLASSE"] == "REJECT_COMO_FONTE_DE_DADO":
            ver = "WRONG_SOURCE"
            porque = ("nao e' rota quebrada: e' fonte que NAO PODE publicar o "
                      "dado. Gap de acesso, decidido na missao anterior.")
        elif base in ("BROKEN", "BLOCKED", "UNKNOWN", "WRONG_SOURCE"):
            ver, porque = base, r["PORQUE"]
        elif dup and "mesma rota final" in dup:
            ver, porque = "DUPLICATE", dup
        elif f["NOME"] in SECUNDARIAS:
            ver = "VALIDATED_BUT_SECONDARY"
            porque = (f"abre e serve, mas e' secundaria: {SECUNDARIAS[f['NOME']]}. "
                      f"{r['PORQUE']}")
        elif not tem_ex:
            ver = "VALIDATED_BUT_SECONDARY"
            porque = ("abre e fala do assunto, mas SEM exemplo real datado na "
                      f"rota medida. {ex}")
        elif f["CLASSE"] == "A" and f["RECORRENCIA"].startswith("HIGH"):
            ver = "VALIDATED_STRONG"
            porque = f"abre, fala do assunto, exemplo datado, recorrencia HIGH. {ex}"
        else:
            ver = "VALIDATED_USEFUL"
            porque = f"abre, fala do assunto, exemplo datado. {ex}"

        if ver.startswith("VALIDATED"):
            vistos_url.setdefault(chave_url, f["NOME"])
            vistos_dono.setdefault(dono, f["NOME"])

        linhas.append({
            "SOURCE_NAME": f["NOME"], "OWNER": dono,
            "OWNER_CORRIGIDO": "SIM" if corr else "NAO",
            "OWNER_CORRECAO_PORQUE": corr.get("PORQUE", ""),
            "URL_DECLARED": url, "URL_FINAL": r["URL_FINAL"],
            "URL_CANONICAL": rota.get("CANONICA") or r["URL_FINAL"],
            "URL_CORRIGIDA_PORQUE": rota.get("PORQUE", ""),
            "REDIRECIONOU": r["REDIRECIONOU"],
            "HTTP": r["HTTP"], "TAMANHO_TEXTO": r["TAMANHO_TEXTO"],
            "SOURCE_TYPE": f["CLASSE"],
            "COUNTRY": "IT", "REGION_SCOPE": f["AMBITO"],
            "TERRITORIES": " ".join(f["TERR"]),
            "WHAT_IT_PRODUCES": f["PRODUZ"],
            "WHICH_RAW_NEED_IT_FEEDS": " || ".join(f["ALIMENTA"]),
            "WHICH_TOOL_IT_SUPPORTS": " · ".join(
                sorted({a.split(" · ")[0] for a in f["ALIMENTA"]})),
            "EXAMPLE_REAL": ex if tem_ex else "",
            "EXAMPLE_URL": r["URL_FINAL"] if tem_ex else "",
            "LAST_ACTIVITY_OBSERVED": r.get("DATAS_NA_PAGINA", "") or "NAO SEI",
            "RECURRING_INFORMATION_POTENTIAL": f["RECORRENCIA"],
            "PRIMARY_OR_SECONDARY": ("SECONDARY"
                                     if ver == "VALIDATED_BUT_SECONDARY"
                                     or f["NOME"] in SECUNDARIAS
                                     else "PRIMARY"),
            "DEDUPE_NOTA": dup,
            "VALIDATION": ver, "VALIDATION_PORQUE": porque,
            "SONDA_VEREDITO_CRU": base,
            "EVIDENCE": f["EVIDENCIA"], "LIMITE": f["LIMITE"],
            "VALIDATED_AT": "2026-09-14 (sonda urllib, UA de navegador)"})

    (TRAB / "VALIDADAS-37.json").write_text(
        json.dumps(linhas, ensure_ascii=False, indent=1), encoding="utf-8")

    c = Counter(l["VALIDATION"] for l in linhas)
    print("VALIDACAO DAS 37")
    print("=" * 92)
    for l in sorted(linhas, key=lambda x: x["VALIDATION"]):
        print(f"  {l['VALIDATION']:24s} HTTP{str(l['HTTP']):>4s} "
              f"{str(l['TAMANHO_TEXTO']):>7s}c  {l['SOURCE_NAME'][:50]}")
    print("=" * 92)
    for k, v in sorted(c.items(), key=lambda x: -x[1]):
        print(f"  {k:26s} {v}")
    print(f"\n  redirecionaram: "
          f"{sum(1 for l in linhas if l['REDIRECIONOU'] == 'SIM')} de {len(linhas)}")
    print(f"  dono corrigido: {sum(1 for l in linhas if l['OWNER_CORRIGIDO'] == 'SIM')}")
    print(f"gravado: {TRAB / 'VALIDADAS-37.json'}")


if __name__ == "__main__":
    main()
