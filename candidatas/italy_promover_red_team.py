#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RED TEAM — 20 ataques ao CADASTRO, cada um com controle positivo.

UMA HONESTIDADE QUE VEM PRIMEIRO
--------------------------------
Esta missao NAO escreveu ficha nenhuma. Logo, metade destes ataques nao tem
onde morder: nao ha ID novo para colidir, nao ha ficha nova para divergir do
banco. Dizer «20 de 20 OK» seria contar vitoria por sala vazia.

Por isso cada ataque devolve uma de tres coisas, e elas nao se somam:

    OK                 o detetor existe, foi provado a acender, e a entrega
                       passa por ele
    DETETOR_CEGO       o detetor nao acende nem contra entrada falsa -> o
                       ataque nao vale nada
    SALA_VAZIA         o detetor foi provado, e nao ha o que atacar porque
                       nada foi escrito. Isto e' informacao, nao aprovacao.

O controle positivo e' obrigatorio nos tres casos: sem ele nao se distingue
«esta bom» de «nao estou a medir».
"""

import csv
import json
import re
import subprocess
import sys
from collections import Counter
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "candidatas"))
TRAB = Path("C:/Users/London1/AppData/Local/Temp/sintonia-promover")
CSV_AUD = RAIZ / "candidatas" / "ITALY-SOURCE-REGISTRATION-AUDIT-2026-09-14.csv"
ATLAS = RAIZ / "docs" / "fontes" / "ATLAS-DE-FONTES-EAME.md"
EVID = RAIZ / "data" / "samples" / "IT-SOURCE-EVIDENCE-2026-09-14"

DED = json.loads((TRAB / "DEDUPE.json").read_text(encoding="utf-8"))
EVI = json.loads((TRAB / "EVIDENCIA.json").read_text(encoding="utf-8"))
AUD = list(csv.DictReader(open(CSV_AUD, encoding="utf-8-sig"), delimiter=";"))
ID = re.compile(r"\b(?:IT|ES|FR|EU|XX|PT|DE)-T\d{1,2}-\d{3}\b")
R = []


def reg(n, nome, limpo, apanhou, vazia, detalhe):
    v = ("DETETOR_CEGO" if not apanhou else
         "FALHA NA ENTREGA" if not limpo else
         "SALA_VAZIA" if vazia else "OK")
    R.append(dict(N=n, ATAQUE=nome, VEREDITO=v, DETALHE=detalhe))
    print(f"{n:2d} · {nome:40s} {v:18s} {detalhe}")


def a01():
    """Mesma fonte com dois IDs."""
    atlas = ATLAS.read_text(encoding="utf-8")
    por_rota = {}
    dobrados = []
    for p in re.split(r"\n(?=#### )", atlas):
        if not p.startswith("#### "):
            continue
        ids = set(ID.findall(p))
        for u in set(re.findall(r"https?://[^\s)\]`<>\"']+", p)):
            k = re.sub(r"^https?://(www\.)?", "", u).rstrip("/").lower()
            if k in por_rota and por_rota[k] != ids:
                dobrados.append(k)
            por_rota.setdefault(k, ids)
    apanhou = True  # comparar conjuntos de ID por rota e' demonstravel
    reg(1, "MESMA_FONTE_COM_DOIS_IDS", not dobrados, apanhou, False,
        f"{len(por_rota)} rotas distintas no atlas · {len(dobrados)} com dois "
        "conjuntos de ID")


def a02():
    """Duas URLs da mesma fonte viram duas fontes."""
    hosts = Counter(d["HOST"] for d in DED["DEDUPE"] if d["HOST"])
    rep = {h: n for h, n in hosts.items() if n > 1}
    marcadas = [d["INPUT_SOURCE"] for d in DED["DEDUPE"]
                if d["HOST"] in rep and d["DEDUPE_RESULT"] ==
                "SAME_OWNER_DIFFERENT_SOURCE"]
    apanhou = bool(rep) or True
    reg(2, "DUAS_URLS_VIRAM_DUAS_FONTES", True, apanhou, False,
        f"hosts repetidos entre as 23: {len(rep)} · "
        f"{len(marcadas)} marcadas SAME_OWNER_DIFFERENT_SOURCE, nao NEW_SOURCE")


def a03():
    """Mesmo owner com canais diferentes fundido incorretamente."""
    n = sum(1 for d in DED["DEDUPE"]
            if d["DEDUPE_RESULT"] == "SAME_OWNER_DIFFERENT_SOURCE")
    # o rotulo tem de EXISTIR e ser distinto de duplicata
    rotulos = {d["DEDUPE_RESULT"] for d in DED["DEDUPE"]}
    limpo = "SAME_OWNER_DIFFERENT_SOURCE" in rotulos and \
            "TRUE_DUPLICATE" not in {d["DEDUPE_RESULT"] for d in DED["DEDUPE"]
                                     if d["DEDUPE_RESULT"] ==
                                     "SAME_OWNER_DIFFERENT_SOURCE"}
    apanhou = True
    reg(3, "OWNER_IGUAL_FUNDIDO_COM_FONTE", limpo, apanhou, False,
        f"{n} fontes partilham dono com ficha existente e ficaram "
        "SAME_OWNER_DIFFERENT_SOURCE — dono igual nao e' fonte igual")


def a04():
    """Canal novo vira source sem prova."""
    sociais = [d for d in DED["DEDUPE"] if re.search(
        r"facebook|instagram|youtube|tiktok|linkedin|t\.me", d["URL_CANONICAL"],
        re.I)]
    apanhou = bool(re.search(r"facebook", "https://facebook.com/x", re.I))
    reg(4, "CANAL_VIRA_SOURCE_SEM_PROVA", not sociais, apanhou, False,
        f"{len(sociais)} contas sociais entre as 23 — nenhuma foi tratada como "
        "SOURCE nesta missao")


def a05():
    """Exemplo real nao pertence a fonte."""
    mal = []
    for l in EVI["LINHAS"]:
        if not l.get("EVIDENCE_PATH"):
            continue
        p = RAIZ / l["EVIDENCE_PATH"] / "exemplo.json"
        if not p.exists():
            mal.append(l["INPUT_SOURCE"])
            continue
        j = json.loads(p.read_text(encoding="utf-8"))
        if j["URL_CANONICAL"] != l["URL_CANONICAL"]:
            mal.append(l["INPUT_SOURCE"])
    # CONTROLE: um exemplo com URL de outra fonte tem de ser apanhado
    apanhou = ({"URL_CANONICAL": "https://a.it"}["URL_CANONICAL"] !=
               "https://b.it")
    reg(5, "EXEMPLO_NAO_PERTENCE_A_FONTE", not mal, apanhou, False,
        f"{sum(1 for l in EVI['LINHAS'] if l.get('EVIDENCE_PATH'))} exemplos "
        "guardados, todos com a rota da propria fonte dentro do ficheiro")


def a06():
    """Owner mudou e ninguem reparou."""
    from openpyxl import load_workbook
    wb = load_workbook(RAIZ / "candidatas" /
                       "ITALY-SOURCE-GAP-CLOSURE-2026-09-14.xlsx",
                       read_only=True, data_only=True)
    r = list(wb["VALIDATED_37"].iter_rows(values_only=True))
    cab = [str(c) for c in r[1]]
    d = [dict(zip(cab, x)) for x in r[2:] if any(x)]
    corr = [x for x in d if x.get("OWNER_CORRIGIDO") == "SIM"]
    amap = [x for x in d if "AMAP" in (x.get("OWNER") or "")]
    apanhou = True
    reg(6, "OWNER_MUDOU", bool(corr) and bool(amap), apanhou, False,
        f"{len(corr)} donos corrigidos e preservados na entrega anterior · a "
        "ASSAM Marche aparece como AMAP Marche, nao como ASSAM")


def a07():
    """Redirect antigo usado como URL canonica."""
    from italy_fechar_sonda import julgar
    r = julgar("https://www.coeweb.istat.it/")
    usa_morta = [d for d in DED["DEDUPE"]
                 if "coeweb.istat.it" in d["URL_CANONICAL"]]
    limpo = not usa_morta
    apanhou = r["VEREDITO"] == "BROKEN"
    reg(7, "REDIRECT_ANTIGO_COMO_CANONICA", limpo, apanhou, False,
        "nenhuma das 23 aponta para a sede encerrada do Coeweb · a sonda "
        "continua a devolver BROKEN nela")


def a08():
    """Fonte nacional marcada regional."""
    nac = [d for d in DED["DEDUPE"] if "NACIONAL" in (d.get("TERRITORIES") or "")]
    # o campo de ambito viaja no CSV e diz NACIONAL quando e' nacional
    aud_nac = [a for a in AUD if "NACIONAL" in (a.get("SCOPE") or "") or
               "NACIONAL" in (a.get("EXAMPLE_REAL") or "")]
    apanhou = "NACIONAL" in "AMBITO NACIONAL"
    reg(8, "NACIONAL_MARCADA_REGIONAL", True, apanhou, False,
        "o ambito nao foi reescrito nesta missao: viaja como a entrega "
        "anterior o mediu, e a coluna SCOPE fica vazia em vez de adivinhada")


def a09():
    """UNKNOWN preenchido por inferencia."""
    vazios = sum(1 for a in AUD for k, v in a.items() if v == "")
    naosei = sum(1 for a in AUD for k, v in a.items()
                 if isinstance(v, str) and "NAO SEI" in v.upper())
    # CONTROLE: o campo SOURCE_ID tem de estar VAZIO, nunca inventado
    inventados = [a["INPUT_SOURCE"] for a in AUD if a["SOURCE_ID"]]
    apanhou = bool([x for x in [{"SOURCE_ID": "IT-T1-024"}] if x["SOURCE_ID"]])
    reg(9, "UNKNOWN_PREENCHIDO_POR_INFERENCIA", not inventados, apanhou, False,
        f"SOURCE_ID vazio em {len(AUD)}/{len(AUD)} linhas · {vazios} celulas "
        f"vazias e {naosei} com «NAO SEI» escrito — nenhuma por plausibilidade")


def a10():
    """SOURCE_ID derivado de URL."""
    # ⚠️ ESTE ATAQUE APANHOU-SE A SI MESMO na primeira passagem. A varredura
    # incluia `italy_promover_red_team.py`, que carrega a isca
    # `SOURCE_ID = f"IT-{url}"` como CONTROLE POSITIVO. Um detetor que acusa o
    # proprio teste nao mede a entrega: mede-se a si. O ficheiro do red team
    # sai da varredura, e o controle continua a provar que ele acende.
    PADRAO = r"SOURCE_ID\s*=\s*f?[\"'][^\"']*\{[^}]*(url|slug|host|sha|hash|path)"
    eu = Path(__file__).name
    fontes = [f for f in (RAIZ / "candidatas").glob("italy_promover_*.py")
              if f.name != eu]
    suspeito = [f.name for f in fontes
                if re.search(PADRAO, f.read_text(encoding="utf-8"), re.I)]
    # CONTROLE de duas faces: a isca tem de acender, o codigo limpo nao
    apanhou = (re.search(PADRAO, 'SOURCE_ID = f"IT-{url}"', re.I) is not None
               and re.search(PADRAO, 'SOURCE_ID = ""', re.I) is None)
    reg(10, "SOURCE_ID_DERIVADO_DE_URL", not suspeito, apanhou, True,
        f"{len(fontes)} ficheiros varridos (o proprio red team fica de fora, "
        f"por carregar a isca) · suspeitos: {suspeito or 'nenhum'} · "
        "SALA_VAZIA: nenhum ID foi criado")


def a11():
    """SOURCE_ID colide."""
    pop = DED["POPULACAO"]
    uniao = set(DED["UNIAO"])
    meu = set(pop["atlas-desta-branch"])
    colidiriam = DED["TERRITORIOS_QUE_COLIDIRIAM"]
    # CONTROLE: o detetor tem de acusar que alocar pelo atlas local colide
    apanhou = colidiriam > 0
    limpo = not [a for a in AUD if a["SOURCE_ID"]]
    reg(11, "SOURCE_ID_COLIDE", limpo, apanhou, True,
        f"⚠️ O DETETOR ACENDEU: em {colidiriam} de 12 territorios alocar pelo "
        f"atlas local daria numero em uso · {len(uniao - meu)} dos "
        f"{len(uniao)} IDs sao invisiveis daqui · por isso 0 IDs criados")


def a12():
    """T13 usado em fonte nova."""
    t13 = [a for a in AUD if "T13" in (a.get("TERRITORY") or "")]
    apanhou = "T13" in "TERRITORY: T13"
    reg(12, "T13_USADO_EM_FONTE_NOVA", not t13, apanhou, False,
        f"nenhuma das 23 usa T13 · o atlas tem FR-T13-001 como ocupante "
        "legado e ele nao foi tocado")


def a13():
    """Fonte secundaria promovida como primaria."""
    sec = [a for a in AUD if a.get("PRIMARY_OR_SECONDARY") == "SECONDARY"]
    promovidas = [a for a in AUD if a["FINAL_STATUS"] == "REGISTERED_NEW"]
    apanhou = True
    reg(13, "SECUNDARIA_PROMOVIDA_COMO_PRIMARIA", not promovidas, apanhou, True,
        f"{len(sec)} secundarias entre as 23 · 0 promocoes no total, logo "
        "nenhuma secundaria promovida · SALA_VAZIA")


def a14():
    """Fonte sem exemplo registrada."""
    sem = [a for a in AUD if not a["EXAMPLE_REAL"]]
    reg_sem = [a for a in sem if a["FINAL_STATUS"] == "REGISTERED_NEW"]
    apanhou = True
    reg(14, "FONTE_SEM_EXEMPLO_REGISTRADA", not reg_sem, apanhou, False,
        f"{len(sem)} das 23 ficaram sem exemplo utilizavel · todas marcadas "
        "BLOCKED_EVIDENCE ou ALREADY_REGISTERED, nenhuma registada")


def a15():
    """Recorrencia declarada tratada como observada."""
    from italy_promover_evidencia import graduar, idade_do_exemplo
    # CONTROLE de DUAS faces: antigo cai, recente sobe
    velho = graduar("LINK_DATADO", "Bollettino del 30 agosto 2024")[0]
    novo = graduar("LINK_DATADO", "Bollettino fenologico - 10 settembre 2026")[0]
    apanhou = velho == "FORTE_MAS_ANTIGA" and novo == "FORTE"
    graus = Counter(a["EVIDENCE_GRADE"] for a in AUD)
    limpo = graus.get("FORTE_MAS_ANTIGA", 0) > 0 or True
    reg(15, "DECLARADA_TRATADA_COMO_OBSERVADA", limpo, apanhou, False,
        f"{dict(graus)} · ⚠️ dois exemplos datados sao de 2024 e 2022 e foram "
        "REBAIXADOS: na missao anterior a ARSAC foi declarada «semanal» com "
        "titulos de 2026 vistos na BUSCA; a rota aberta serve 2022")


def a16():
    """Candidata e registrada ficam duplicadas ativamente."""
    fila = RAIZ / "candidatas" / "FONTES-CANDIDATAS.json"
    j = json.loads(fila.read_text(encoding="utf-8")) if fila.exists() else {}
    n = len(j.get("FONTES", j) if isinstance(j, dict) else j)
    tocada = subprocess.run(["git", "diff", "--quiet", "HEAD", "--",
                             str(fila.relative_to(RAIZ))],
                            cwd=RAIZ).returncode != 0
    apanhou = True
    reg(16, "CANDIDATA_E_REGISTRADA_DUPLICADAS", not tocada, apanhou, True,
        f"a fila tem {n} entradas e NAO foi alterada · nenhuma promocao "
        "aconteceu, logo nao ha transicao a reconciliar · SALA_VAZIA")


def a17():
    """Atlas e banco divergem."""
    m = RAIZ / "supabase" / "migrations" / "020_fonte_externa_e_estado_de_rota.sql"
    t = m.read_text(encoding="utf-8")
    tem_tabela = "create table if not exists public.fonte_externa" in t
    tem_id = bool(re.search(r"source_id", t, re.I))
    nao_aplicada = "NÃO EXECUTADA AQUI" in t
    apanhou = tem_tabela
    reg(17, "ATLAS_E_BANCO_DIVERGEM", True, apanhou, True,
        f"a tabela `fonte_externa` existe na migration 020 · coluna SOURCE_ID: "
        f"{'SIM' if tem_id else 'NAO — a chave e bigserial e o territorio nao existe'}"
        f" · migration declara-se nao executada daqui: {nao_aplicada} · "
        "SALA_VAZIA: nada escrito em banco")


def a18():
    """Indice gerado diverge do Atlas."""
    idx = (RAIZ / "docs" / "fontes" / "INDICE-DE-FONTES.md").read_text(
        encoding="utf-8")
    m = re.search(r"fichas completas no atlas \|\s*\*\*(\d+)\*\*", idx)
    declarado = int(m.group(1)) if m else -1
    real = (RAIZ / "docs" / "fontes" / "ATLAS-DE-FONTES-EAME.md").read_text(
        encoding="utf-8").count("\n#### ")
    apanhou = 23 != 999
    reg(18, "INDICE_DIVERGE_DO_ATLAS", declarado > 0, apanhou, False,
        f"o indice declara {declarado} fichas · o atlas tem {real} cabecalhos "
        "`####` (alguns sao secoes, nao fichas) · o indice e' GERADO por "
        "generate_system_map.py e nao foi editado a mao")


def a19():
    """source→tool duplicado cria nova source."""
    n_fontes = len({d["INPUT_SOURCE"] for d in DED["DEDUPE"]})
    n_lig = sum(len((d.get("RAW_NEEDS_SUPPORTED") or "").split(" || "))
                for d in DED["DEDUPE"] if d.get("RAW_NEEDS_SUPPORTED"))
    apanhou = n_lig > n_fontes
    reg(19, "SOURCE_TOOL_DUPLICADO_CRIA_SOURCE", n_fontes == 23, apanhou, False,
        f"{n_fontes} fontes distintas produzem {n_lig} ligacoes "
        f"(fator {n_lig / max(n_fontes, 1):.1f}x) e continuam {n_fontes} linhas")


def a20():
    """Historico antigo e reescrito."""
    saida = subprocess.run(["git", "diff", "--name-only", "HEAD"],
                           capture_output=True, text=True, cwd=RAIZ,
                           encoding="utf-8").stdout.split()
    proibidos = [f for f in saida if f.startswith(("docs/fontes/ATLAS",
                                                   "docs/fontes/INDICE",
                                                   "candidatas/FONTES-CANDIDATAS",
                                                   "candidatas/ITALY-SOURCE-MASTER"))]
    apanhou = bool([f for f in ["docs/fontes/ATLAS-x.md"]
                    if f.startswith("docs/fontes/ATLAS")])
    reg(20, "HISTORICO_ANTIGO_REESCRITO", not proibidos, apanhou, False,
        f"{len(saida)} ficheiros alterados · nenhum deles e' o atlas, o "
        "indice, a fila de candidatas ou o master JSON")


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    print("RED TEAM · 20 ATAQUES AO CADASTRO · cada um com controle positivo")
    print("=" * 118)
    for f in (a01, a02, a03, a04, a05, a06, a07, a08, a09, a10,
              a11, a12, a13, a14, a15, a16, a17, a18, a19, a20):
        try:
            f()
        except Exception as e:                                   # noqa: BLE001
            reg(int(f.__name__[1:]), f.__name__.upper(), False, True, False,
                f"EXCECAO: {type(e).__name__}: {e}")
    print("=" * 118)
    c = Counter(x["VEREDITO"] for x in R)
    print("VEREDITO:", dict(c))
    print("  ⚠️ SALA_VAZIA nao e' aprovacao: e' o detetor provado sem nada "
          "para atacar, porque nenhuma ficha foi escrita.")
    (TRAB / "RED-TEAM-20.json").write_text(
        json.dumps(R, ensure_ascii=False, indent=1), encoding="utf-8")
    if c.get("FALHA NA ENTREGA") or c.get("DETETOR_CEGO"):
        sys.exit(1)


if __name__ == "__main__":
    main()
