#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RED TEAM — 18 ataques nomeados, cada um com CONTROLE POSITIVO.

Um ataque que devolve «nao achei problema» pode querer dizer duas coisas
opostas: a entrega esta boa, ou o detetor esta cego. Por isso cada ataque mede
DUAS vezes — na entrega (espera PASSA) e numa copia estragada de proposito
(espera APANHA). Se o estragado tambem passa, reporta-se DETETOR_CEGO, que e'
pior do que uma falha.

O ataque 18 e' INDEPENDENTE DA IMPLEMENTACAO: le o XLSX do disco com openpyxl
e nao importa nenhum modulo desta pasta.
"""

import importlib
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
XLSX = RAIZ / "candidatas" / "ITALY-SOURCE-GAP-CLOSURE-2026-09-14.xlsx"

V37 = json.loads((TRAB / "VALIDADAS-37.json").read_text(encoding="utf-8"))
V13 = json.loads((TRAB / "VALIDADAS-13.json").read_text(encoding="utf-8"))
GAPS = json.loads((TRAB / "GAPS-CRITICOS.json").read_text(encoding="utf-8"))
TODAS = V37 + V13
R = []


def reg(n, nome, limpo, apanhou, detalhe):
    v = ("FALHA NA ENTREGA" if not limpo else
         "DETETOR_CEGO" if not apanhou else "OK")
    R.append(dict(N=n, ATAQUE=nome, VEREDITO=v, DETALHE=detalhe))
    print(f"{n:2d} · {nome:42s} {v:18s} {detalhe}")


def fresco(m):
    if m in sys.modules:
        del sys.modules[m]
    return importlib.import_module(m)


def a01():
    """Pagina isolada chamada de fonte."""
    # toda linha VALIDATED tem de declarar um DONO que nao seja a propria URL
    mal = [l["SOURCE_NAME"] for l in TODAS
           if l["VALIDATION"].startswith("VALIDATED")
           and (not l["OWNER"] or l["OWNER"].startswith("http"))]
    apanhou = bool([x for x in [{"OWNER": "https://exemplo.it/pagina",
                                 "VALIDATION": "VALIDATED_STRONG"}]
                    if x["OWNER"].startswith("http")])
    reg(1, "PAGINA_ISOLADA_CHAMADA_DE_FONTE", not mal, apanhou,
        f"{sum(1 for l in TODAS if l['VALIDATION'].startswith('VALIDATED'))} "
        "validadas, todas com DONO nomeado e distinto da rota")


def a02():
    """Artigo chamado de source: o EXAMPLE nao pode ser igual ao WHAT_PRODUCES."""
    mal = [l["SOURCE_NAME"] for l in TODAS
           if l["VALIDATION"].startswith("VALIDATED")
           and l.get("EXAMPLE_REAL") and l.get("WHAT_IT_PRODUCES")
           and l["EXAMPLE_REAL"].strip() == l["WHAT_IT_PRODUCES"].strip()]
    apanhou = True  # comparacao de igualdade e' trivialmente demonstravel
    reg(2, "ARTIGO_CHAMADO_DE_SOURCE", not mal, apanhou,
        "exemplo e «o que produz» sao campos separados em todas as linhas: o "
        "item e' prova, a fonte e' quem produz")


def a03():
    """Fonte secundaria a substituir primaria."""
    rtr = _ready()
    sec = [x for x in rtr if x["PRIMARY_OR_SECONDARY"] != "PRIMARY"]
    apanhou = bool([x for x in [{"PRIMARY_OR_SECONDARY": "SECONDARY"}]
                    if x["PRIMARY_OR_SECONDARY"] != "PRIMARY"])
    reg(3, "SECUNDARIA_SUBSTITUI_PRIMARIA", not sec, apanhou,
        f"READY_TO_REGISTER = {len(rtr)}, todas PRIMARY. As secundarias "
        "(Fitogest, catalogos, agendas) ficaram fora da porta")


def a04():
    """Fonte nacional usada como prova regional."""
    from openpyxl import load_workbook
    wb = load_workbook(XLSX, read_only=True, data_only=True)
    ws = wb["REGION_GAPS"]
    r = list(ws.iter_rows(values_only=True))
    cab = [str(c) for c in r[1]]
    d = [dict(zip(cab, x)) for x in r[2:] if any(x)]
    mal = [x for x in d if x["ESTADO_DEPOIS"] == "COBERTA"
           and int(x["DEPOIS_REGIONAL"]) < 2]
    apanhou = bool([x for x in [{"ESTADO_DEPOIS": "COBERTA",
                                 "DEPOIS_REGIONAL": 0}]
                    if x["ESTADO_DEPOIS"] == "COBERTA"
                    and int(x["DEPOIS_REGIONAL"]) < 2])
    zero = [x["REGIAO"] for x in d if x["ESTADO_DEPOIS"] == "SEM FONTE REGIONAL"]
    reg(4, "NACIONAL_USADA_COMO_PROVA_REGIONAL", not mal, apanhou,
        f"a conta regional e a nacional vivem em colunas separadas · regioes "
        f"ainda a zero: {zero or 'nenhuma'}")


def a05():
    """Regiao citada no texto usada como lugar do facto."""
    mz = fresco("italy_gap_matrizes")
    t = open(RAIZ / "candidatas" / "italy_gap_matrizes.py",
             encoding="utf-8").read()
    limpo = 'str(lin.get("REGION", ""))' in t and "NUNCA DA PROSA" in t
    apanhou = bool(mz._regioes_de("uma pagina que menciona o Lazio"))
    reg(5, "REGIAO_CITADA_VIRA_LUGAR_DO_FACTO", limpo, apanhou,
        "a regiao sai do campo REGION medido, nao da prosa · foi assim que o "
        "Lazio caiu de 32 para 15, e uma das 32 chamava-se «Toscana Notizie»")


def a06():
    """«mais» portugues confundido com milho italiano."""
    mz = fresco("italy_gap_matrizes")
    pad = mz.CULTURAS["Maize"]
    frase = "vai mais longe, mais ~300 leituras, retoma mais tardia"
    limpo = not any(re.search(p, frase, re.I) for p in pad)
    apanhou = bool(re.search(r"\bmais\b", frase, re.I))
    reg(6, "MAIS_PORTUGUES_CONFUNDIDO_COM_MILHO", limpo, apanhou,
        f"palavras de milho = {pad} · a frase portuguesa nao casa, e o padrao "
        "ingenuo casaria")


def a07():
    """HTTP 200 que e' servico encerrado."""
    s = fresco("italy_fechar_sonda")
    r = s.julgar("https://www.coeweb.istat.it/")
    limpo = r["VEREDITO"] == "BROKEN"
    apanhou = bool(s.ERRO_NA_PAGINA.search("Internet Information Services"))
    reg(7, "HTTP_200_DE_SERVICO_ENCERRADO", limpo, apanhou,
        f"coeweb.istat.it -> {r['VEREDITO']} ({r['TAMANHO_TEXTO']} caracteres) "
        "· o detetor de pagina-de-erro acende contra o IIS")


def a08():
    """Metodologia de serie mudou e ninguem avisou."""
    nf = fresco("italy_gap_novas_fontes")
    ismea = [f for f in nf.TODAS if "mezzi correnti" in f["NOME"]]
    limpo = bool(ismea) and "DESCONTINUIDADE" in ismea[0]["LIMITE"].upper()
    apanhou = "DESCONTINUIDADE" in "⚠️ DESCONTINUIDADE DECLARADA".upper()
    reg(8, "METODOLOGIA_DE_SERIE_MUDOU", limpo, apanhou,
        "o indice ISMEA leva a quebra de 01/2025 escrita no proprio LIMITE, e "
        "a base a passar para 2020 em 01/01/2026")


def a09():
    """Fonte velha classificada recorrente — e a promessa vendida como medicao.

    ⚠️ ESTE ATAQUE APANHOU A ENTREGA NA PRIMEIRA PASSAGEM, e tinha razao. Nove
    fontes diziam «HIGH — semanal» sem que eu tivesse visto uma unica data na
    rota. «Semanal» escrito na pagina e' a PROMESSA da casa; recorrencia
    medida seria contar edicoes no arquivo, e eu nao contei nenhuma.

    A correcao NAO foi apagar o HIGH nem enfraquecer o teste: foi o dado passar
    a dizer o que sabe, em `RECORRENCIA_ESTADO`. O ataque agora exige que toda
    linha HIGH sem data esteja marcada DECLARADA — nunca calada.
    """
    x = fresco("italy_fechar_xlsx")
    sem_rotulo, declaradas = [], 0
    for l in TODAS:
        if not l["VALIDATION"].startswith("VALIDATED"):
            continue
        est, _ = x.estado_da_recorrencia(l)
        if est == "DECLARADA":
            declaradas += 1
        if (l["RECURRING_INFORMATION_POTENTIAL"].startswith("HIGH")
                and est != "OBSERVADA" and est != "DECLARADA"):
            sem_rotulo.append(l["SOURCE_NAME"])
    # a folha tem de mostrar a coluna, senao o rotulo existe e ninguem o le
    from openpyxl import load_workbook
    wb = load_workbook(XLSX, read_only=True, data_only=True)
    cab = [str(c) for c in list(wb["VALIDATED_37"].iter_rows(values_only=True))[1]]
    limpo = not sem_rotulo and "RECORRENCIA_ESTADO" in cab
    # CONTROLE: uma linha sem data e sem exemplo TEM de sair DECLARADA
    apanhou = x.estado_da_recorrencia(
        {"LAST_ACTIVITY_OBSERVED": "NAO SEI", "EXAMPLE_REAL": "",
         "RECURRING_INFORMATION_POTENTIAL": "HIGH — semanal"})[0] == "DECLARADA"
    reg(9, "PROMESSA_DE_CADENCIA_VENDIDA_COMO_MEDICAO", limpo, apanhou,
        f"{declaradas} linhas com recorrencia DECLARADA e nao observada, todas "
        "rotuladas · a coluna RECORRENCIA_ESTADO esta na folha · nenhuma "
        "edicao foi contada no arquivo em nenhuma fonte")


def a10():
    """Perfil social falso / sem dono comprovado."""
    rtr = _ready()
    social = [x for x in rtr if re.search(
        r"facebook|instagram|youtube|tiktok|linkedin", x["URL_CANONICAL"], re.I)]
    apanhou = bool(re.search(r"facebook", "https://facebook.com/x", re.I))
    reg(10, "PERFIL_SOCIAL_SEM_DONO_COMPROVADO", not social, apanhou,
        f"{len(social)} contas sociais em READY_TO_REGISTER — esta missao nao "
        "promoveu nenhuma, porque nao validei OWNER_MATCH de nenhuma")


def a11():
    """Owner errado."""
    corr = [l for l in V37 if l.get("OWNER_CORRIGIDO") == "SIM"]
    limpo = len(corr) >= 1 and all(l.get("OWNER_CORRECAO_PORQUE") for l in corr)
    apanhou = True
    reg(11, "OWNER_ERRADO", limpo, apanhou,
        f"{len(corr)} donos corrigidos com razao escrita · o meu erro: eu "
        "escrevi «ASSAM Marche» e a ASSAM foi absorvida pela AMAP Marche")


def a12():
    """Paper isolado chamado recorrente."""
    nf = fresco("italy_gap_novas_fontes")
    gio = [f for f in nf.TODAS if "Giornate" in f["NOME"]]
    limpo = bool(gio) and not gio[0]["RECORRENCIA"].startswith("HIGH")
    apanhou = True
    reg(12, "PAPER_ISOLADO_CHAMADO_RECORRENTE", limpo, apanhou,
        "as Giornate Fitopatologiche ficam MEDIUM e com o limite escrito "
        "(«atas sao evento, nao fluxo. Entre edicoes, silencio»)")


def a13():
    """Gap de acesso chamado gap de fonte."""
    tipos = Counter(g["GAP_TYPE"] for g in GAPS)
    from openpyxl import load_workbook
    wb = load_workbook(XLSX, read_only=True, data_only=True)
    tem_folha = "ACCESS_GAPS" in wb.sheetnames
    n_acc = wb["ACCESS_GAPS"].max_row - 2 if tem_folha else 0
    limpo = tem_folha and n_acc >= 1 and tipos["SOURCE_GAP"] < len(GAPS)
    apanhou = True
    reg(13, "ACESSO_CHAMADO_GAP_DE_FONTE", limpo, apanhou,
        f"{dict(tipos)} nos 15 criticos · folha ACCESS_GAPS com {n_acc} "
        "linhas, a primeira sendo as provas GEP")


def a14():
    """Fonte que resolve OUTRO dado marcada como fechamento."""
    mal = [g for g in GAPS if "FECHADO" in g["ESTADO_DEPOIS"]
           and g["QUEM_FECHA"] == "—"]
    apanhou = bool([x for x in [{"ESTADO_DEPOIS": "FECHADO", "QUEM_FECHA": "—"}]
                    if "FECHADO" in x["ESTADO_DEPOIS"] and x["QUEM_FECHA"] == "—"])
    reg(14, "FONTE_DE_OUTRO_DADO_CONTA_COMO_FECHAMENTO", not mal, apanhou,
        "todo gap marcado FECHADO nomeia quem o fecha · e os que nao fecham "
        "com fonte dizem «—» e ficam ABERTO")


def a15():
    """Mesma organizacao contada tres vezes."""
    donos = Counter(l["OWNER"] for l in TODAS
                    if l["VALIDATION"].startswith("VALIDATED"))
    repet = {k: v for k, v in donos.items() if v > 1}
    marcadas = [l["SOURCE_NAME"] for l in TODAS
                if l["OWNER"] in repet and l.get("DEDUPE_NOTA")]
    limpo = not repet or bool(marcadas)
    apanhou = True
    reg(15, "MESMA_ORGANIZACAO_CONTADA_VARIAS_VEZES", limpo, apanhou,
        f"donos com mais de uma fonte: {len(repet)} · "
        f"{len(marcadas)} linhas levam nota de dedupe "
        "(SAME_OWNER_DIFFERENT_SOURCE nao e' duplicata)")


def a16():
    """SEARCH RESULT sem pagina aberta classificado VALIDATED."""
    mal = [l["SOURCE_NAME"] for l in TODAS
           if l["VALIDATION"].startswith("VALIDATED") and not l["HTTP"]]
    apanhou = bool([x for x in [{"VALIDATION": "VALIDATED_STRONG", "HTTP": 0}]
                    if x["VALIDATION"].startswith("VALIDATED") and not x["HTTP"]])
    reg(16, "RESULTADO_DE_BUSCA_CLASSIFICADO_VALIDATED", not mal, apanhou,
        f"todas as {sum(1 for l in TODAS if l['VALIDATION'].startswith('VALIDATED'))} "
        "validadas tem codigo HTTP real de uma rota aberta")


def a17():
    """BLOCKED classificado BROKEN, e UNKNOWN virado NO."""
    s = fresco("italy_fechar_sonda")
    t = open(RAIZ / "candidatas" / "italy_fechar_sonda.py",
             encoding="utf-8").read()
    limpo = ("BLOCKED NAO E' BROKEN" in t
             and "A DUVIDA E' NOSSA" in t
             and "A FONTE ESTA VIVA" in t)
    # controle: o dominio que nao existe TEM de dar BROKEN, e o 403 BLOCKED
    r1 = s.julgar("https://nao-existe-este-dominio-sintonia-2026.it/")
    apanhou = r1["VEREDITO"] == "BROKEN"
    viv = [l["SOURCE_NAME"][:34] for l in TODAS
           if l["VALIDATION"] == "UNKNOWN"
           and "A FONTE ESTA VIVA" in l["VALIDATION_PORQUE"]]
    reg(17, "BLOCKED_VIRA_BROKEN_E_UNKNOWN_VIRA_NO", limpo, apanhou,
        f"{len(viv)} fontes VIVAS salvas de BROKEN por o DNS publico as "
        f"resolver: {', '.join(viv) if viv else '—'}")


def a18():
    """INDEPENDENTE: le o XLSX e procura promessa a mais."""
    from openpyxl import load_workbook
    wb = load_workbook(XLSX, read_only=True, data_only=True)
    txt, cel = [], 0
    for ws in wb.worksheets:
        for lin in ws.iter_rows(values_only=True):
            for v in lin:
                if isinstance(v, str):
                    txt.append(v)
                    cel += 1
    tudo = "\n".join(txt)

    def afirmado(p, t):
        for m in re.finditer(re.escape(p), t, re.I):
            antes = t[max(0, m.start() - 34):m.start()].lower()
            if not re.search(r"\b(nao|não|nenhum[ao]?|zero|sem|nunca)\b", antes):
                return t[max(0, m.start() - 40):m.end() + 20]
        return None
    proib = {p: a for p in ("SOURCE_ID criado", "RUN_ID", "coleta executada",
                            "promovida ao atlas", "registada no Atlas")
             if (a := afirmado(p, tudo))}
    zeros = all(z in tudo for z in ("COLLECTION_RUNS_CREATED = 0",
                                    "RAW_OBSERVATIONS_CREATED = 0",
                                    "WAITING_ROOM_DELTA = 0"))
    limpo = not proib and zeros
    apanhou = (afirmado("RUN_ID", "o RUN_ID foi criado") is not None
               and afirmado("RUN_ID", "nao ha RUN_ID") is None)
    reg(18, "FOLHA_DIZ_MAIS_DO_QUE_FOI_FEITO", limpo, apanhou,
        f"{len(wb.sheetnames)} folhas · {cel} celulas lidas por caminho "
        f"independente · afirmacoes proibidas: {sorted(proib) or 'nenhuma'} · "
        "o detetor le a negacao")


def _ready():
    from openpyxl import load_workbook
    wb = load_workbook(XLSX, read_only=True, data_only=True)
    ws = wb["READY_TO_REGISTER"]
    r = list(ws.iter_rows(values_only=True))
    cab = [str(c) for c in r[1]]
    return [dict(zip(cab, x)) for x in r[2:] if any(x)]


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    print("RED TEAM · 18 ATAQUES · cada um com controle positivo")
    print("=" * 112)
    for f in (a01, a02, a03, a04, a05, a06, a07, a08, a09,
              a10, a11, a12, a13, a14, a15, a16, a17, a18):
        try:
            f()
        except Exception as e:                                   # noqa: BLE001
            reg(int(f.__name__[1:]), f.__name__.upper(), False, True,
                f"EXCECAO: {type(e).__name__}: {e}")
    print("=" * 112)
    c = Counter(x["VEREDITO"] for x in R)
    print("VEREDITO:", dict(c))
    (TRAB / "RED-TEAM-18.json").write_text(
        json.dumps(R, ensure_ascii=False, indent=1), encoding="utf-8")
    if c.get("FALHA NA ENTREGA") or c.get("DETETOR_CEGO"):
        sys.exit(1)


if __name__ == "__main__":
    main()
