#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ESCREVE A PLANILHA E O CSV DA PORTA.

Le `LINHAS.json` (que o italy_deep_workbook.py produziu) e escreve:

    candidatas/ITALY-DEEP-SOURCE-RESEARCH-2026-09-14.xlsx
    candidatas/ITALY-DEEP-SOURCE-IMPORT-READY-2026-09-14.csv

O CSV sai no formato exato de `candidatas/fonte_nova.py` e **nao e executado**.
Ficheiro pronto nao e ingestao feita — e essa distincao e o que impede uma
planilha de virar acervo sem ninguem ter olhado.

As abas de COBERTURA existem para mostrar o buraco, nao para o esconder:
regiao com zero fonte forte aparece com zero, escrito, e com a palavra
GAP ao lado. Preencher regiao com fonte fraca para a tabela ficar bonita e
o erro que esta missao foi mandada nao cometer.
"""

import csv
import html
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

import openpyxl
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter

TRABALHO = Path(sys.argv[1] if len(sys.argv) > 1
                else "C:/Users/London1/AppData/Local/Temp/sintonia-italy-deep")
DESTINO = Path(sys.argv[2]) if len(sys.argv) > 2 else Path(__file__).resolve().parent
HOJE = "2026-09-14"
QUEM_VIU = "claude-code (missao ITALY-DEEP-SOURCE-RESEARCH, 2026-09-14)"

REGIOES_20 = ["ABRUZZO", "BASILICATA", "CALABRIA", "CAMPANIA", "EMILIA-ROMAGNA",
              "FRIULI-VENEZIA GIULIA", "LAZIO", "LIGURIA", "LOMBARDIA", "MARCHE",
              "MOLISE", "PIEMONTE", "PUGLIA", "SARDEGNA", "SICILIA", "TOSCANA",
              "TRENTINO-ALTO ADIGE", "UMBRIA", "VALLE D'AOSTA", "VENETO"]
TS = [f"T{i}" for i in range(1, 13)]
TERRITORIOS = {
    "T1": "CROP & PRODUCTION", "T2": "CLIMATE / WATER / SOIL",
    "T3": "PEST / DISEASE / WEEDS", "T4": "REGULATORY", "T5": "SCIENCE",
    "T6": "RESEARCHERS", "T7": "TECHNICAL NETWORK",
    "T8": "FARMERS & INFLUENCERS", "T9": "COMPETITORS",
    "T10": "MARKET / TRADE / INDUSTRY", "T11": "EVENTS",
    "T12": "POLICY / AGRICULTURAL ENVIRONMENT",
}

COLUNAS = ["RECORD_KIND", "NAME", "OWNER", "PERSON", "ORGANIZATION", "COUNTRY",
           "REGION", "REGION_EVIDENCE", "SCOPE", "SOURCE_TYPE", "PLATFORM",
           "URL_DISCOVERED", "URL_FINAL", "URL_CANONICAL", "URL_STATUS",
           "HTTP_STATUS", "TERRITORIES", "CROPS", "TOPICS",
           "INFORMATION_PROXIMITY", "RECURRING_INFORMATION_POTENTIAL",
           "WHY_USEFUL", "WHAT_CAN_THIS_SOURCE_TELL_SINTONIA", "EXAMPLE_REAL",
           "EVIDENCE", "LAST_ACTIVITY_OBSERVED", "OFFICIALITY", "OWNER_MATCH",
           "NEW_VS_EXISTING", "RELATED_OWNER", "QUALITY_CLASS", "QUALITY_REASON",
           "LIMITATION", "VALIDATED_AT", "DISCOVERED_FROM", "N_DESCOBRIDORES",
           "AGRI_N", "INFO_PROPRIA_N", "SECOND_PROOF", "MANUAL_AUDIT"]

TIPO_PARA_PORTA = {
    "SERVIZIO_FITOSANITARIO": "BASE_OFICIAL", "AGENZIA_REGIONALE": "BASE_OFICIAL",
    "REGIONE": "BASE_OFICIAL", "ESTADO_NACIONAL": "BASE_OFICIAL",
    "CAMARA_COMERCIO": "BASE_OFICIAL",
    "UNIVERSIDADE": "CIENCIA", "CENTRO_PESQUISA": "CIENCIA",
    "SOCIEDADE_CIENTIFICA": "CIENCIA",
    "CONSORZIO_TUTELA": "ORGANIZACAO", "CONSORZIO_BONIFICA": "ORGANIZACAO",
    "COOPERATIVA_OP": "ORGANIZACAO", "ASSOCIACAO_AGRICOLA": "ORGANIZACAO",
    "ORDEM_PROFISSIONAL": "ORGANIZACAO", "EMPRESA_INSUMOS": "ORGANIZACAO",
    "FEIRA_EVENTO": "ORGANIZACAO", "MIDIA_TECNICA": "IMPRENSA",
    "PESSOA": "OUTRO",
}
PLATAFORMA_PARA_PORTA = {
    "INSTAGRAM": "INSTAGRAM", "YOUTUBE": "YOUTUBE", "LINKEDIN": "LINKEDIN",
    "FACEBOOK": "FACEBOOK", "TIKTOK": "OUTRO", "PODCAST": "OUTRO",
    "TELEGRAM": "OUTRO", "BLOG": "OUTRO", "WEB": None,
}

CAB = PatternFill("solid", fgColor="1F3864")
CAB_F = Font(bold=True, color="FFFFFF", size=10)
COR = {"A": "C6EFCE", "B": "DDEBF7", "C": "FFF2CC",
       "HOLD": "FCE4D6", "UNKNOWN": "E7E6E6", "REJECT": "F8CBAD",
       "PEOPLE": "E4DFEC"}


def aba(wb, titulo, cabecalho, linhas, larguras=None):
    ws = wb.create_sheet(titulo[:31])
    ws.append(cabecalho)
    for c in range(1, len(cabecalho) + 1):
        cel = ws.cell(row=1, column=c)
        cel.fill = CAB
        cel.font = CAB_F
        cel.alignment = Alignment(vertical="center", wrap_text=True)
    for ln in linhas:
        ws.append(ln)
    ws.freeze_panes = "A2"
    for i, h in enumerate(cabecalho, 1):
        w = (larguras or {}).get(h, min(52, max(12, len(str(h)) + 4)))
        ws.column_dimensions[get_column_letter(i)].width = w
    if len(cabecalho) > 1:
        ws.auto_filter.ref = ws.dimensions
    return ws


def linha_de(d):
    return [d.get(c, "") for c in COLUNAS]


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    linhas = json.loads((TRABALHO / "LINHAS.json").read_text(encoding="utf-8"))

    # ── auditoria manual e segunda prova ──
    # A chave e o HOST COMPLETO (RELATED_OWNER), nao o URL: o julgamento humano
    # e sobre a fonte, e a mesma fonte pode ter chegado por dois caminhos.
    # Para pessoas e canais, a chave e o NAME.
    for nome, campo in (("AUDIT.json", "MANUAL_AUDIT"),
                        ("SECOND-PROOF.json", "SECOND_PROOF")):
        p = TRABALHO / nome
        if not p.exists():
            print(f"(sem {nome})")
            continue
        marcas = json.loads(p.read_text(encoding="utf-8"))
        tocadas = 0
        for d in linhas:
            # A chave depende do tipo de registo, e isto NAO e detalhe: sem a
            # separacao, um julgamento escrito sobre o SITE de uma organizacao
            # pingava nas linhas das PESSOAS que partilham aquele site — e uma
            # pessoa passava a ter a classe de um endereco. Aconteceu com dois
            # dirigentes do Consorzio Vini Valle d Aosta antes desta correcao.
            if d.get("RECORD_KIND") == "SOURCE":
                chaves = (d.get("RELATED_OWNER", ""), d.get("URL_DISCOVERED", ""))
            else:
                chaves = (d.get("NAME", ""), d.get("PERSON", ""))
            for k in chaves:
                if k and k in marcas:
                    m = marcas[k]
                    d[campo] = (m.get("resultado", "REVISTA_A_MAO")
                                if isinstance(m, dict) else str(m))
                    if isinstance(m, dict):
                        if m.get("classe_final"):
                            d["QUALITY_CLASS"] = m["classe_final"]
                        if m.get("nota"):
                            d["QUALITY_REASON"] = (
                                d.get("QUALITY_REASON", "")
                                + " || LEITURA HUMANA: " + m["nota"])
                        if m.get("terr"):
                            d["TERRITORIES"] = m["terr"]
                        if m.get("regiao"):
                            d["REGION"] = m["regiao"]
                            d["REGION_EVIDENCE"] = ("AFIRMADA NA LEITURA HUMANA — "
                                                    "ver QUALITY_REASON")
                    tocadas += 1
                    break
        print(f"{nome}: {len(marcas)} decisoes, {tocadas} linhas tocadas")

    # as linhas DEPOIS da leitura humana e da segunda prova — e este ficheiro,
    # nao o LINHAS.json cru, e o que o red team tem de atacar.
    (TRABALHO / "LINHAS-FINAL.json").write_text(
        json.dumps(linhas, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")

    por_classe = defaultdict(list)
    for d in linhas:
        por_classe[d["QUALITY_CLASS"]].append(d)
    print("classes DEPOIS da leitura humana:",
          dict(Counter(d["QUALITY_CLASS"] for d in linhas)))

    wb = openpyxl.Workbook()
    wb.remove(wb.active)

    larg = {"NAME": 44, "OWNER": 34, "WHY_USEFUL": 60, "QUALITY_REASON": 60,
            "WHAT_CAN_THIS_SOURCE_TELL_SINTONIA": 54, "EVIDENCE": 58,
            "URL_DISCOVERED": 48, "URL_FINAL": 48, "URL_CANONICAL": 40,
            "REGION_EVIDENCE": 46, "LIMITATION": 40, "TOPICS": 36,
            "DISCOVERED_FROM": 40, "ORGANIZATION": 34, "PERSON": 26}

    # ══ A / B / C ══
    for cls, nome in (("A", "A_EXCELLENT"), ("B", "B_GOOD"), ("C", "C_COMPLEMENTARY")):
        dd = sorted(por_classe.get(cls, []),
                    key=lambda x: (-(x.get("AGRI_N") or 0), x.get("NAME", "")))
        ws = aba(wb, nome, COLUNAS, [linha_de(d) for d in dd], larg)
        for r in range(2, ws.max_row + 1):
            ws.cell(row=r, column=1).fill = PatternFill("solid", fgColor=COR[cls])

    # ══ PEOPLE ══
    pessoas = [d for d in linhas if d["RECORD_KIND"] == "PERSON"]
    cab_p = ["NAME", "INSTITUTION", "CURRENT_AFFILIATION", "REGION", "SPECIALTY",
             "CROPS", "PROBLEMS", "ORCID", "INSTITUTIONAL_PROFILE",
             "RECENT_WORK_EXAMPLE", "TERRITORIES",
             "WHAT_CAN_THIS_SOURCE_TELL_SINTONIA", "EVIDENCE", "LIMITATION",
             "NEW_VS_EXISTING", "VALIDATED_AT",
             "NAO_E_RANKING", "SECOND_PROOF", "MANUAL_AUDIT"]
    lp = []
    for d in pessoas:
        lp.append([d.get("PERSON") or d.get("NAME"), d.get("ORGANIZATION"),
                   d.get("ORGANIZATION"), d.get("REGION"), d.get("WHY_USEFUL"),
                   d.get("CROPS"), d.get("TOPICS"), d.get("_orcid") or "NAO SEI",
                   d.get("URL_DISCOVERED"), d.get("EVIDENCE"),
                   d.get("TERRITORIES"),
                   d.get("WHAT_CAN_THIS_SOURCE_TELL_SINTONIA"),
                   d.get("EVIDENCE"), d.get("LIMITATION"),
                   d.get("NEW_VS_EXISTING"), d.get("VALIDATED_AT"),
                   "relevante para a cultura e o problema escritos nesta linha; "
                   "esta folha NAO e um ranking de pesquisadores de Italia",
                   d.get("SECOND_PROOF", ""), d.get("MANUAL_AUDIT", "")])
    aba(wb, "PEOPLE", cab_p, lp,
        {"NAME": 30, "INSTITUTION": 46, "CURRENT_AFFILIATION": 46, "SPECIALTY": 46,
         "PROBLEMS": 34, "WHAT_CAN_THIS_SOURCE_TELL_SINTONIA": 54, "EVIDENCE": 58,
         "INSTITUTIONAL_PROFILE": 44, "NAO_E_RANKING": 50, "LIMITATION": 40})

    # ══ ORGANIZATIONS ══
    orgs = [d for d in linhas if d["RECORD_KIND"] == "SOURCE"
            and d["QUALITY_CLASS"] in ("A", "B", "C")]
    aba(wb, "ORGANIZATIONS", COLUNAS, [linha_de(d) for d in
                                       sorted(orgs, key=lambda x: (x["QUALITY_CLASS"], x["NAME"]))],
        larg)

    # ══ SOCIAL ══
    soc = [d for d in linhas if d["RECORD_KIND"] == "CHANNEL"]
    cab_s = ["PLATFORM", "NAME", "HANDLE", "PROFILE_URL", "OWNER", "OWNER_MATCH",
             "REGION", "TERRITORIES", "REACH", "FIELD_AUTHORITY",
             "TECHNICAL_AUTHORITY", "COMMERCIAL_INFLUENCE",
             "LAST_ACTIVITY_OBSERVED", "EXAMPLE_POST",
             "WHAT_CAN_THIS_SOURCE_TELL_SINTONIA", "QUALITY_CLASS",
             "QUALITY_REASON", "NEW_VS_EXISTING", "EVIDENCE", "LIMITATION"]
    ls = []
    for d in soc:
        u = d.get("URL_DISCOVERED", "")
        handle = ""
        m = re.search(r"(?:@|/)([A-Za-z0-9_.\-]{2,40})/?$", u)
        if m:
            handle = m.group(1)
        ls.append([d.get("PLATFORM"), d.get("NAME"), handle, u, d.get("OWNER"),
                   d.get("OWNER_MATCH"), d.get("REGION"), d.get("TERRITORIES"),
                   d.get("_reach", ""), d.get("_field", ""), d.get("_tech", ""),
                   d.get("_comm", ""), d.get("LAST_ACTIVITY_OBSERVED"),
                   d.get("EXAMPLE_REAL"),
                   d.get("WHAT_CAN_THIS_SOURCE_TELL_SINTONIA"),
                   d.get("QUALITY_CLASS"), d.get("QUALITY_REASON"),
                   d.get("NEW_VS_EXISTING"), d.get("EVIDENCE"), d.get("LIMITATION")])
    aba(wb, "SOCIAL", cab_s, ls,
        {"NAME": 34, "PROFILE_URL": 46, "OWNER": 46, "REACH": 40,
         "FIELD_AUTHORITY": 40, "TECHNICAL_AUTHORITY": 44,
         "COMMERCIAL_INFLUENCE": 34, "WHAT_CAN_THIS_SOURCE_TELL_SINTONIA": 54,
         "QUALITY_REASON": 60, "EVIDENCE": 50, "LIMITATION": 40})

    # ══ REGION_COVERAGE ══
    cab_r = (["REGION", "RAW_DISCOVERIES_COM_ESTA_REGIAO_NO_TEXTO", "NEW_A",
              "NEW_B", "NEW_C", "HOLD", "PEOPLE", "ORGANIZATIONS", "SOCIAL"]
             + TS + ["GAPS"])
    lr = []
    for reg in REGIOES_20 + ["ITALIA (nacional)", "NAO SEI (regiao nao provada)"]:
        def bate(d):
            r = d.get("REGION", "")
            if reg == "ITALIA (nacional)":
                return r == "ITALIA"
            if reg.startswith("NAO SEI"):
                return r == "NAO SEI"
            return reg in (r or "")
        dd = [d for d in linhas if bate(d)]
        novos = [d for d in dd if d["NEW_VS_EXISTING"] in
                 ("NEW_SOURCE", "NEW_CHANNEL", "NEW_PERSON",
                  "SAME_OWNER_DIFFERENT_SOURCE")]
        na = sum(1 for d in novos if d["QUALITY_CLASS"] == "A")
        nb = sum(1 for d in novos if d["QUALITY_CLASS"] == "B")
        nc = sum(1 for d in novos if d["QUALITY_CLASS"] == "C")
        nh = sum(1 for d in novos if d["QUALITY_CLASS"] == "HOLD")
        npe = sum(1 for d in dd if d["RECORD_KIND"] == "PERSON")
        nor = sum(1 for d in dd if d["RECORD_KIND"] == "SOURCE")
        nso = sum(1 for d in dd if d["RECORD_KIND"] == "CHANNEL")
        tt = []
        for t in TS:
            tt.append(sum(1 for d in novos
                          if t in (d.get("TERRITORIES") or "").split(";")
                          and d["QUALITY_CLASS"] in ("A", "B")))
        faltas = [TS[i] for i, v in enumerate(tt) if v == 0]
        gap = ""
        if reg in REGIOES_20:
            if na + nb == 0:
                gap = ("SOURCE GAP: zero fonte A/B com esta regiao PROVADA no texto. "
                       "Pode ser falta real ou limite da pesquisa — nao foi preenchida "
                       "com fonte fraca.")
            elif faltas:
                gap = "sem A/B em: " + ",".join(faltas)
            else:
                gap = "—"
        lr.append([reg, len(dd), na, nb, nc, nh, npe, nor, nso] + tt + [gap])
    aba(wb, "REGION_COVERAGE", cab_r, lr, {"REGION": 30, "GAPS": 70,
                                           "RAW_DISCOVERIES_COM_ESTA_REGIAO_NO_TEXTO": 20})

    # ══ TERRITORY_COVERAGE ══
    cab_t = ["TERRITORY", "O_QUE_E", "NEW_A", "NEW_B", "NEW_C", "HOLD",
             "TOTAL_NOVOS", "PRIMARY", "NEAR_PRIMARY", "RECORRENCIA_HIGH",
             "REGIOES_COBERTAS_COM_A_OU_B", "GAP"]
    lt = []
    for t in TS:
        dd = [d for d in linhas if t in (d.get("TERRITORIES") or "").split(";")]
        novos = [d for d in dd if d["NEW_VS_EXISTING"] in
                 ("NEW_SOURCE", "NEW_CHANNEL", "NEW_PERSON",
                  "SAME_OWNER_DIFFERENT_SOURCE")]
        na = sum(1 for d in novos if d["QUALITY_CLASS"] == "A")
        nb = sum(1 for d in novos if d["QUALITY_CLASS"] == "B")
        nc = sum(1 for d in novos if d["QUALITY_CLASS"] == "C")
        nh = sum(1 for d in novos if d["QUALITY_CLASS"] == "HOLD")
        pr = sum(1 for d in novos if d["INFORMATION_PROXIMITY"] == "PRIMARY")
        npr = sum(1 for d in novos if d["INFORMATION_PROXIMITY"] == "NEAR_PRIMARY")
        hi = sum(1 for d in novos if d["RECURRING_INFORMATION_POTENTIAL"] == "HIGH")
        regs = {r for d in novos if d["QUALITY_CLASS"] in ("A", "B")
                for r in (d.get("REGION") or "").split(";") if r in REGIOES_20}
        lt.append([t, TERRITORIOS[t], na, nb, nc, nh, len(novos), pr, npr, hi,
                   len(regs),
                   "—" if na + nb >= 3 else
                   f"poucas fontes fortes novas ({na+nb}) — procurar mais"])
    aba(wb, "TERRITORY_COVERAGE", cab_t, lt, {"O_QUE_E": 34, "GAP": 52,
                                              "REGIOES_COBERTAS_COM_A_OU_B": 18})

    # ══ CROP_COVERAGE ══
    conta = Counter()
    conta_ab = Counter()
    for d in linhas:
        for c in (d.get("CROPS") or "").split(";"):
            if not c:
                continue
            conta[c] += 1
            if d["QUALITY_CLASS"] in ("A", "B"):
                conta_ab[c] += 1
    lc = [[c, n, conta_ab.get(c, 0),
           "—" if conta_ab.get(c, 0) >= 3 else "poucas fontes A/B para esta cultura"]
          for c, n in conta.most_common()]
    aba(wb, "CROP_COVERAGE", ["CROP", "LINHAS_COM_ESTA_CULTURA", "A_OU_B", "GAP"],
        lc, {"GAP": 46})

    # ══ OWNER_MAP ══
    donos = defaultdict(list)
    for d in linhas:
        donos[d.get("RELATED_OWNER") or "NAO SEI"].append(d)
    lo = []
    for dono, dd in sorted(donos.items(), key=lambda kv: -len(kv[1])):
        if len(dd) < 2 and dono == "NAO SEI":
            continue
        lo.append([dono, len(dd),
                   ";".join(sorted({x["RECORD_KIND"] for x in dd})),
                   ";".join(sorted({x["QUALITY_CLASS"] for x in dd})),
                   ";".join(sorted({x["NEW_VS_EXISTING"] for x in dd})),
                   " | ".join(sorted({x["NAME"][:40] for x in dd})[:6]),
                   "ATENCAO: mais de uma linha para o mesmo dono — sao canais/rotas "
                   "do MESMO dono, nao organizacoes diferentes" if len(dd) > 1 else "—"])
    aba(wb, "OWNER_MAP", ["OWNER_ROOT", "N_LINHAS", "RECORD_KINDS", "CLASSES",
                          "NEW_VS_EXISTING", "EXEMPLOS", "NOTA_DE_CONTAGEM"], lo,
        {"OWNER_ROOT": 34, "EXEMPLOS": 70, "NOTA_DE_CONTAGEM": 60})

    # ══ REJECTED / HOLD_UNKNOWN ══
    rej = sorted(por_classe.get("REJECT", []), key=lambda x: x.get("NAME", ""))
    aba(wb, "REJECTED", ["NAME", "URL_DISCOVERED", "HTTP_STATUS", "RECORD_KIND",
                         "QUALITY_REASON", "DISCOVERED_FROM", "N_DESCOBRIDORES"],
        [[d.get("NAME"), d.get("URL_DISCOVERED"), d.get("HTTP_STATUS"),
          d.get("RECORD_KIND"), d.get("QUALITY_REASON"), d.get("DISCOVERED_FROM"),
          d.get("N_DESCOBRIDORES")] for d in rej],
        {"NAME": 40, "URL_DISCOVERED": 46, "QUALITY_REASON": 70, "DISCOVERED_FROM": 40})

    hu = sorted(por_classe.get("HOLD", []) + por_classe.get("UNKNOWN", []),
                key=lambda x: (x["QUALITY_CLASS"], x.get("NAME", "")))
    aba(wb, "HOLD_UNKNOWN", COLUNAS, [linha_de(d) for d in hu], larg)

    # ══ SEARCH_LOG ══
    log = json.loads((TRABALHO / "SEARCH-LOG.json").read_text(encoding="utf-8")) \
        if (TRABALHO / "SEARCH-LOG.json").exists() else []
    aba(wb, "SEARCH_LOG", ["RODADA", "FERRAMENTA", "CONSULTA_OU_SEMENTE",
                           "O_QUE_DEVOLVEU", "CUSTO_MEDIDO", "NOTA"],
        [[x.get("rodada"), x.get("ferramenta"), x.get("consulta"),
          x.get("devolveu"), x.get("custo"), x.get("nota")] for x in log],
        {"CONSULTA_OU_SEMENTE": 62, "O_QUE_DEVOLVEU": 46, "NOTA": 46})

    # ══ README ══
    readme = json.loads((TRABALHO / "README-ROWS.json").read_text(encoding="utf-8")) \
        if (TRABALHO / "README-ROWS.json").exists() else []
    ws = aba(wb, "README", ["O QUE ESTA FOLHA DIZ", "EXPLICACAO"], readme,
             {"O QUE ESTA FOLHA DIZ": 44, "EXPLICACAO": 118})
    for r in range(2, ws.max_row + 1):
        ws.cell(row=r, column=2).alignment = Alignment(wrap_text=True, vertical="top")

    # ordem das abas como o pedido pede
    ordem = ["A_EXCELLENT", "B_GOOD", "C_COMPLEMENTARY", "PEOPLE", "ORGANIZATIONS",
             "SOCIAL", "REGION_COVERAGE", "TERRITORY_COVERAGE", "CROP_COVERAGE",
             "OWNER_MAP", "REJECTED", "HOLD_UNKNOWN", "SEARCH_LOG", "README"]
    wb._sheets = [wb[n] for n in ordem if n in wb.sheetnames] + \
                 [s for s in wb._sheets if s.title not in ordem]

    alvo = DESTINO / "ITALY-DEEP-SOURCE-RESEARCH-2026-09-14.xlsx"
    wb.save(alvo)
    print(f"XLSX={alvo}")
    for s in wb.sheetnames:
        print(f"   {s:24s} {wb[s].max_row-1} linhas")

    # ══ CSV import-ready: SO A e B novas, no formato de fonte_nova.py ══
    pron, barradas = [], []
    for d in linhas:
        if d["QUALITY_CLASS"] not in ("A", "B"):
            continue
        if d["NEW_VS_EXISTING"] in ("KNOWN_SOURCE", "TRUE_DUPLICATE",
                                    "SAME_SOURCE_VARIANT_URL"):
            barradas.append((d, "ja existe no acervo (" + d["NEW_VS_EXISTING"] + ")"))
            continue
        if d["RECORD_KIND"] == "PERSON":
            barradas.append((d, "pessoa nao entra pela porta de fonte: "
                                "a porta aceita fonte/canal, e a pessoa precisa de "
                                "perfil institucional proprio como URL"))
            continue
        url = d.get("URL_CANONICAL") or d.get("URL_FINAL") or d.get("URL_DISCOVERED")
        if not url:
            barradas.append((d, "sem endereco utilizavel"))
            continue
        if d.get("URL_STATUS") in ("BROKEN", "UNKNOWN"):
            barradas.append((d, f"endereco em estado {d.get('URL_STATUS')} — "
                                f"nao se manda para a porta o que nao abriu"))
            continue
        host = d.get("RELATED_OWNER") or ""
        plat = d.get("PLATFORM") or "WEB"
        tipo = PLATAFORMA_PARA_PORTA.get(plat)
        if not tipo:
            # Prioridade EXPLICITA, e nao 'o primeiro que bater': o estado vem
            # antes da universidade, e a universidade antes da midia. Sem isto,
            # o ministerio da agricultura entrava na gaveta CIENCIA porque a
            # pagina dele cita universidades.
            todos = (d.get("SOURCE_TYPE_ALL") or d.get("SOURCE_TYPE") or "").split(";")
            # Uma editora que fala de regioes nao e um orgao publico. Se o host
            # NAO e institucional e a pagina tem marca de redacao, a gaveta e
            # IMPRENSA — senao o Edagricole entrava como BASE_OFICIAL.
            institucional = any(
                m in host.lower() for m in
                (".gov.it", "regione.", "provincia.", "camcom", "arpa", "ersa",
                 "assam", "amap.", "arsial", "alsia", "arsac", "arsarp", "laore",
                 "agris", "arif", "avepa", "ersaf", "agrion", "sardegna.it",
                 "salute.gov", "cnr.it", "crea.gov", "istat.it", "europa.eu",
                 "fitosanitario."))
            # ── por que a maquina desistiu de escolher a gaveta ──
            # Tentei tres vezes deduzir o TIPO do texto da pagina e falhei tres
            # vezes, cada uma para um lado: 'servizio fitosanitario' mencionado
            # fazia uma empresa privada virar BASE_OFICIAL; 'notizie' fazia uma
            # agencia publica virar IMPRENSA; 'universita' citada fazia um
            # consorcio de azeite virar CIENCIA.
            #
            # A licao: o texto de uma pagina diz de que ela FALA, nao QUEM ELA E.
            # Por isso agora o TIPO sai de tres coisas, nesta ordem, e nenhuma
            # delas e contagem de palavras do corpo da pagina:
            #   1 · o dominio, quando ele PROVA (um .gov.it e' publico)
            #   2 · a minha leitura humana, quando existe
            #   3 · OUTRO, com a duvida escrita — a porta aceita OUTRO
            #       justamente para isto, e `fonte_nova.py` exige que se
            #       explique em PARA_QUE_SERVE, o que aqui esta feito.
            #
            # Assimetria deliberada: para a REGIAO recusei usar o dominio
            # ('agrisicilia.it' pode ser de Milao); para o TIPO DE DONO o
            # dominio e prova boa. As duas coisas nao sao o mesmo.
            leitura = (d.get("QUALITY_REASON") or "")
            leitura = leitura.split("LEITURA HUMANA:", 1)[-1].lower() \
                if "LEITURA HUMANA:" in leitura else ""
            DA_MINHA_LEITURA = [
                ("BASE_OFICIAL", ["servico fitossanitario", "servizio fitosanitario",
                                  "agencia regional", "organismo pagador",
                                  "ministerio", "borsa merci", "cotacao",
                                  "camera di commercio", "observatorio de mercado",
                                  "dados nacionais", "boletim regional"]),
                ("CIENCIA", ["centro de pesquisa", "centro di ricerca", "sociedade cientifica",
                             "universidade", "departamento", "revista academica",
                             "instituto de pesquisa", "experimentacao", "spin-off",
                             "ensaios de eficacia", "centro de experimentacao",
                             "rede nacional de fenotipagem", "pesquisa aplicada"]),
                ("ORGANIZACAO", ["consorcio", "consorzio", "cooperativa", "organizacao de produtores",
                                 "op ", "associacao", "federacao", "ordem profissional",
                                 "sindicato", "uniao", "camara", "empresa",
                                 "concorrente", "fornecedor", "cluster", "app de gestao",
                                 "plataforma"]),
                ("IMPRENSA", ["revista", "jornal", "midia", "testata", "webzine",
                              "mensario", "periodico", "editora", "redacao",
                              "portal de noticias", "podcast"]),
            ]
            if institucional:
                tipo = "BASE_OFICIAL"
            elif leitura:
                for cand, marcas in DA_MINHA_LEITURA:
                    if any(m in leitura for m in marcas):
                        tipo = cand
                        break
            if not tipo:
                tipo = "OUTRO"
        # O NOME nao pode ser o titulo da pagina: o titulo de uma noticia nao
        # identifica a fonte, e quem importar o CSV fica sem saber quem e.
        # O host COMPLETO identifica sempre; o titulo vem atras, encurtado.
        # html.unescape: '&#039;' e '&agrave;' nao sao nome de fonte nenhuma
        titulo = re.sub(r"\s+", " ", html.unescape(d.get("NAME") or "")).strip()
        if d.get("RECORD_KIND") == "CHANNEL":
            nome = f"{titulo} [{d.get('PLATFORM')}]"
        elif host and host.lower() not in titulo.lower():
            nome = f"{host} — {titulo[:80]}" if titulo else host
        else:
            nome = titulo or host

        para_que = d.get("WHAT_CAN_THIS_SOURCE_TELL_SINTONIA") or ""
        terrs = d.get("TERRITORIES") or ""
        if terrs:
            para_que += f" — alimenta {terrs}"
        if not para_que.strip():
            barradas.append((d, "PARA_QUE_SERVE vazio: a porta recusa, e bem"))
            continue
        onde = d.get("DISCOVERED_FROM") or "grafo de descoberta a partir do acervo"
        nota = (f"CANDIDATA classe {d['QUALITY_CLASS']} em {HOJE}; "
                f"proximidade={d['INFORMATION_PROXIMITY']}; "
                f"recorrencia={d['RECURRING_INFORMATION_POTENTIAL']}; "
                f"regiao={d['REGION']} ({d['REGION_EVIDENCE'][:60]}); "
                f"SOURCE_ID nao atribuido — nasce na porta canonica")
        if tipo == "OUTRO" and plat == "WEB":
            nota += ("; TIPO=OUTRO porque a gaveta NAO foi provada: o dominio nao "
                     "e institucional e ninguem leu esta fonte a mao. O que a "
                     "maquina detetou na pagina foi ["
                     + (d.get("SOURCE_TYPE_ALL") or "nada")
                     + "], e deteccao por palavra diz de que a pagina FALA, nao "
                       "QUEM ELA E. Quem registar escolhe a gaveta")
        pron.append({
            "TIPO": tipo, "PAIS": "IT" if d.get("COUNTRY") == "IT" else "OUTRO",
            "NOME": nome[:120],
            "URL": url,
            "PARA_QUE_SERVE": para_que[:400],
            "QUEM_VIU": QUEM_VIU,
            "ONDE_VIU": str(onde)[:220],
            "NOTA": nota[:400],
        })

    csv_alvo = DESTINO / "ITALY-DEEP-SOURCE-IMPORT-READY-2026-09-14.csv"
    with open(csv_alvo, "w", encoding="utf-8-sig", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=["TIPO", "PAIS", "NOME", "URL",
                                           "PARA_QUE_SERVE", "QUEM_VIU",
                                           "ONDE_VIU", "NOTA"])
        w.writeheader()
        for r in pron:
            w.writerow(r)
    print(f"CSV={csv_alvo}  linhas={len(pron)}  barradas={len(barradas)}")
    razoes = Counter(m for _, m in barradas)
    for m, n in razoes.most_common():
        print(f"    barradas {n:4d}: {m[:90]}")

    (TRABALHO / "IMPORT-BARRADAS.json").write_text(
        json.dumps([{"NAME": d.get("NAME"), "URL": d.get("URL_DISCOVERED"),
                     "MOTIVO": m} for d, m in barradas],
                   ensure_ascii=False, indent=1), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
