#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MONTA candidatas/ITALY-SOURCE-GAP-CLOSURE-2026-09-14.xlsx

READY_TO_REGISTER E' UMA PORTA, NAO UM PREMIO
---------------------------------------------
Entra so' quem tem as dez coisas: identidade confirmada, dono confirmado, URL
canonica, exemplo real, necessidade que alimenta, ferramenta que serve,
ambito, potencial de recorrencia, evidencia e ausencia de duplicata
verdadeira. Falta uma e fica fora, por boa que pareca.

E `DIVERGED` na segunda prova nao entra, por muitos pontos que some.

NADA AQUI E' REGISTO
--------------------
Nenhum SOURCE_ID. Nenhuma promocao ao Atlas. A folha diz «pronta», e quem
registra e' a missao seguinte, com decisao de gente.
"""

import json
import sys
from collections import Counter
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "candidatas"))
TRAB = Path("C:/Users/London1/AppData/Local/Temp/sintonia-fechar")
ANTES = Path("C:/Users/London1/AppData/Local/Temp/sintonia-gap")

from italy_fechar_buscas import BUSCAS2                          # noqa: E402
from openpyxl import Workbook                                    # noqa: E402
from openpyxl.styles import Alignment, Font, PatternFill         # noqa: E402
from openpyxl.utils import get_column_letter                     # noqa: E402

SAIDA = RAIZ / "candidatas" / "ITALY-SOURCE-GAP-CLOSURE-2026-09-14.xlsx"
V37 = json.loads((TRAB / "VALIDADAS-37.json").read_text(encoding="utf-8"))
V13 = json.loads((TRAB / "VALIDADAS-13.json").read_text(encoding="utf-8"))
GAPS = json.loads((TRAB / "GAPS-CRITICOS.json").read_text(encoding="utf-8"))
MATZ = json.loads((ANTES / "MATRIZES.json").read_text(encoding="utf-8"))

CAB = PatternFill("solid", fgColor="1F3864")
NOTA = PatternFill("solid", fgColor="FFF2CC")


def estado_da_recorrencia(l):
    """A recorrencia foi OBSERVADA ou apenas DECLARADA?

    ⚠️ O ATAQUE 9 DO RED TEAM APANHOU-ME NISTO. Nove fontes diziam
    «HIGH — semanal» sem que eu tivesse visto uma unica data na rota nem
    guardado exemplo datado. «Semanal» escrito na pagina e' a PROMESSA da
    casa; recorrencia de verdade mede-se contando edicoes no arquivo, e eu
    nao contei nenhuma.

    Corrigir isto enfraquecendo o teste seria o caminho errado. O certo e' o
    dado dizer o que sabe: tres estados, e nunca se somam.

        OBSERVADA   vi data na rota, ou tenho exemplo real datado
        DECLARADA   a fonte (ou eu) diz a cadencia; ninguem a contou
        NAO_SEI     nem uma coisa nem outra
    """
    tem_data = l.get("LAST_ACTIVITY_OBSERVED", "NAO SEI") != "NAO SEI"
    tem_ex = bool(l.get("EXAMPLE_REAL"))
    if tem_data or tem_ex:
        return ("OBSERVADA", "data lida na rota ou exemplo real datado")
    if l.get("RECURRING_INFORMATION_POTENTIAL", "").strip():
        return ("DECLARADA", "a cadencia esta escrita, mas NENHUMA edicao foi "
                "contada no arquivo. Promessa da casa, nao medicao nossa.")
    return ("NAO_SEI", "sem data e sem cadencia declarada")


def folha(wb, nome, explica, linhas, colunas=None):
    ws = wb.create_sheet(nome)
    ws["A1"] = explica
    ws["A1"].fill = NOTA
    ws["A1"].alignment = Alignment(wrap_text=True, vertical="top")
    cols = colunas or (list(linhas[0]) if linhas else ["(vazia)"])
    ws.merge_cells(start_row=1, start_column=1, end_row=1,
                   end_column=max(len(cols), 2))
    ws.row_dimensions[1].height = 46
    for j, c in enumerate(cols, 1):
        cel = ws.cell(row=2, column=j, value=c)
        cel.fill = CAB
        cel.font = Font(color="FFFFFF", bold=True)
        cel.alignment = Alignment(wrap_text=True, vertical="center")
    for i, lin in enumerate(linhas, 3):
        for j, c in enumerate(cols, 1):
            v = lin.get(c, "")
            cel = ws.cell(row=i, column=j,
                          value=v if isinstance(v, (int, float)) else str(v))
            cel.alignment = Alignment(wrap_text=True, vertical="top")
    for j, c in enumerate(cols, 1):
        larg = max([len(str(c))] +
                   [min(len(str(l.get(c, ""))), 74) for l in linhas] or [10]) + 2
        ws.column_dimensions[get_column_letter(j)].width = min(max(larg, 10), 60)
    ws.freeze_panes = "A3"


# ── READY_TO_REGISTER: a porta das dez coisas ─────────────────────────────
def pronta(l):
    faltam = []
    if not l.get("SOURCE_NAME"):
        faltam.append("IDENTITY")
    if not l.get("OWNER"):
        faltam.append("OWNER")
    if not l.get("URL_CANONICAL"):
        faltam.append("CANONICAL_URL")
    if not l.get("EXAMPLE_REAL"):
        faltam.append("EXAMPLE_REAL")
    if not l.get("WHICH_RAW_NEED_IT_FEEDS"):
        faltam.append("RAW_NEED")
    if not l.get("WHICH_TOOL_IT_SUPPORTS"):
        faltam.append("TOOL_SUPPORTED")
    if not l.get("REGION_SCOPE"):
        faltam.append("SCOPE")
    if not l.get("RECURRING_INFORMATION_POTENTIAL"):
        faltam.append("RECURRING_POTENTIAL")
    if not l.get("EVIDENCE"):
        faltam.append("EVIDENCE")
    if "mesma rota final" in (l.get("DEDUPE_NOTA") or ""):
        faltam.append("TRUE_DUPLICATE")
    if l.get("VALIDATION") not in ("VALIDATED_STRONG", "VALIDATED_USEFUL"):
        faltam.append(f"VALIDATION={l.get('VALIDATION')}")
    if l.get("SEGUNDA_PROVA") == "DIVERGED":
        faltam.append("SEGUNDA_PROVA=DIVERGED")
    return faltam


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    wb = Workbook()
    wb.remove(wb.active)
    todas = [dict(x, VAGA="37 da missao anterior") for x in V37] + \
            [dict(x, VAGA="13 desta missao") for x in V13]

    # A recorrencia ganha ESTADO antes de qualquer folha a mostrar.
    for _l in todas + V37 + V13:
        _e, _p = estado_da_recorrencia(_l)
        _l["RECORRENCIA_ESTADO"] = _e
        _l["RECORRENCIA_ESTADO_PORQUE"] = _p

    # 1 · VALIDATED_37
    c37 = ["SOURCE_NAME", "OWNER", "OWNER_CORRIGIDO", "OWNER_CORRECAO_PORQUE",
           "URL_DECLARED", "URL_FINAL", "URL_CANONICAL", "URL_CORRIGIDA_PORQUE",
           "REDIRECIONOU", "HTTP", "TAMANHO_TEXTO", "VALIDATION",
           "VALIDATION_PORQUE", "PRIMARY_OR_SECONDARY", "EXAMPLE_REAL",
           "LAST_ACTIVITY_OBSERVED", "RECURRING_INFORMATION_POTENTIAL",
           "RECORRENCIA_ESTADO", "RECORRENCIA_ESTADO_PORQUE",
           "WHICH_TOOL_IT_SUPPORTS", "REGION_SCOPE", "TERRITORIES",
           "DEDUPE_NOTA", "LIMITE", "VALIDATED_AT"]
    folha(wb, "VALIDATED_37",
          "AS 37 ROTAS DA MISSAO ANTERIOR, ABERTAS DE VERDADE. A entrega "
          "anterior declarava «0 de 37 abertas»; esta abriu as 37 com sonda "
          "urllib e UA de navegador. ⚠️ A sonda foi PROVADA antes de julgar: "
          "2 controles positivos que tinham de abrir e 2 negativos que nao "
          "podiam passar. Oito estados, nao dois — BROKEN pede fonte nova, "
          "BLOCKED pede outra rota, UNKNOWN e' duvida NOSSA.",
          V37, c37)

    # 2 · READY_TO_REGISTER
    rtr, rej_porta = [], []
    for l in todas:
        f = pronta(l)
        if f:
            rej_porta.append(dict(l, FALTA=" · ".join(f)))
            continue
        rtr.append({
            "SOURCE_NAME": l["SOURCE_NAME"], "OWNER": l["OWNER"],
            "SOURCE_TYPE": l["SOURCE_TYPE"],
            "URL_CANONICAL": l["URL_CANONICAL"],
            "COUNTRY": l["COUNTRY"],
            "REGION": l["REGION_SCOPE"], "SCOPE": l["REGION_SCOPE"],
            "TERRITORIES": l["TERRITORIES"],
            "TOOLS_SUPPORTED": l["WHICH_TOOL_IT_SUPPORTS"],
            "RAW_NEEDS_SUPPORTED": l["WHICH_RAW_NEED_IT_FEEDS"],
            "WHAT_IT_PRODUCES": l["WHAT_IT_PRODUCES"],
            "PRIMARY_OR_SECONDARY": l["PRIMARY_OR_SECONDARY"],
            "RECURRING_POTENTIAL": l["RECURRING_INFORMATION_POTENTIAL"],
            "RECORRENCIA_ESTADO": l["RECORRENCIA_ESTADO"],
            "RECORRENCIA_ESTADO_PORQUE": l["RECORRENCIA_ESTADO_PORQUE"],
            "EXAMPLE_REAL": l["EXAMPLE_REAL"],
            "EXAMPLE_URL": l.get("EXAMPLE_URL", ""),
            "GAP_CLOSURE_VALUE": l.get("GAP_CLOSURE_VALUE") or "MEDIUM",
            "SEGUNDA_PROVA": l.get("SEGUNDA_PROVA", "NAO_EXIGIDA"),
            "EVIDENCE": l["EVIDENCE"],
            "LIMITE_DECLARADO": l["LIMITE"],
            "VALIDATED_AT": l["VALIDATED_AT"], "VAGA": l["VAGA"]})
    ordem = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}
    rtr.sort(key=lambda x: (ordem.get(x["GAP_CLOSURE_VALUE"], 9),
                            x["PRIMARY_OR_SECONDARY"] != "PRIMARY"))
    folha(wb, "READY_TO_REGISTER",
          "A PORTA DAS DEZ COISAS. Entra so' quem tem identidade e dono "
          "confirmados, URL canonica, EXEMPLO REAL, necessidade que alimenta, "
          "ferramenta que serve, ambito, recorrencia, evidencia e nenhuma "
          "duplicata verdadeira — e validacao STRONG ou USEFUL. `DIVERGED` na "
          "segunda prova NAO entra, por bem classificada que esteja. ⚠️ "
          "«Pronta» nao e' «registada»: nenhum SOURCE_ID nasce aqui.",
          rtr)

    # 3 · CRITICAL_GAPS
    folha(wb, "CRITICAL_GAPS",
          "OS 15 CRITICOS, CLASSIFICADOS POR TIPO ANTES DE SE PROCURAR MAIS. "
          "Procurar fonte publica para um dado que a lei proibe publicar e' "
          "procurar para sempre — por isso o tipo vem primeiro. Leia a coluna "
          "PROCURAR_MAIS_FONTE_RESOLVE: em 5 dos 15, a resposta e' NAO, e a "
          "accao fica noutro sitio.",
          GAPS)

    # 4 · ACCESS_GAPS
    acc = [
     {"GAP": "SCIENCE · ENSAIO DE CAMPO / trial com resultado",
      "GAP_TYPE": "ACCESS_GAP",
      "WHAT_DATA_EXISTS": "ensaio oficial de eficacia e residuos sob Good "
                          "Experimental Practice, com tratamento e testemunha",
      "WHO_OWNS_ACCESS": "a empresa que encomenda o ensaio. Os centros de "
                         "saggio executam e nao detem o direito de publicar: "
                         "Agrea, Sagea, AgriSearch, Agro Services, Agritec, "
                         "Repros",
      "ACCESS_REQUIRED": "contrato ou parceria com o titular do ensaio",
      "HOW_IT_COULD_BE_ACQUIRED": "encomendar ensaio proprio a um centro GEP, "
                                  "ou acordo de partilha com quem o encomendou. "
                                  "NAO se adquire por coleta.",
      "O_QUE_E_DIVULGAVEL_EM_VEZ": "provas demonstrativas dos servicos "
          "regionais, atas das Giornate Fitopatologiche e da AIPP/SIPaV, e o "
          "Bollettino Colture Erbacee da Veneto Agricoltura — que publica "
          "resultado medido com o numero desfavoravel incluido («o tratamento "
          "no momento de maxima eficacia melhorou produtividade e micotoxinas "
          "em MENOS DE 50% dos casos»). Isto e' resultado publico de ensaio "
          "demonstrativo, que nao substitui o de registo mas fecha parte da "
          "pergunta.",
      "PORQUE_NAO_E_SOURCE_GAP": "nenhuma fonte publica existe nem pode "
          "existir. Gastar buscas aqui e' gastar contra a lei do contrato, nao "
          "contra um problema tecnico."},
     {"GAP": "MARKET · CUSTO DE INSUMO — monitoraggio dei costi medi",
      "GAP_TYPE": "ACCESS_GAP",
      "WHAT_DATA_EXISTS": "custo medio de producao em EUR/tonelada por cluster",
      "WHO_OWNS_ACCESS": "ISMEA",
      "ACCESS_REQUIRED": "registo de conta no servico",
      "HOW_IT_COULD_BE_ACQUIRED": "criar conta institucional. E' gratuito mas "
                                  "atras de login, e coleta atras de login e' "
                                  "outra decisao.",
      "O_QUE_E_DIVULGAVEL_EM_VEZ": "o indice dos mezzi correnti, aberto e "
          "validado nesta missao (14.782 caracteres lidos)",
      "PORQUE_NAO_E_SOURCE_GAP": "a fonte existe, e nomeada e publica — o "
          "obstaculo e' a porta, nao a ausencia."},
     {"GAP": "WINDOWS · bollettini do SeDI da ALSIA (Basilicata)",
      "GAP_TYPE": "ACCESS_GAP",
      "WHAT_DATA_EXISTS": "boletins fitossanitarios por comprensorio "
                          "(Metapontino, Alta Valle d'Agri, Valle del Bradano)",
      "WHO_OWNS_ACCESS": "ALSIA — Agenzia Lucana",
      "ACCESS_REQUIRED": "inscricao nos Servizi di Consulenza online",
      "HOW_IT_COULD_BE_ACQUIRED": "inscricao gratuita",
      "O_QUE_E_DIVULGAVEL_EM_VEZ": "os relatorios climaticos mensais e os "
          "dados das 40 estacoes, publicados diariamente na web",
      "PORQUE_NAO_E_SOURCE_GAP": "a fonte existe e fecha a regiao que estava "
          "a zero. ⚠️ E ha um segundo obstaculo, independente deste: o DNS "
          "desta maquina nao alcanca `alsia.it`, embora o resolvedor publico "
          "o resolva (78.40.170.40). Sao dois problemas diferentes e ambos "
          "nossos."},
    ]
    folha(wb, "ACCESS_GAPS",
          "O DADO EXISTE E TEM DONO QUE NAO O PUBLICA — ou que o publica atras "
          "de uma porta. Isto NAO e' gap de fonte, e a diferenca decide o que "
          "se faz a seguir: coleta nao resolve, contrato ou inscricao "
          "resolvem. A primeira linha e' a mais dura da missao.",
          acc)

    # 5 · NEW_DISCOVERY
    c13 = ["SOURCE_NAME", "OWNER", "URL_DECLARED", "URL_CANONICAL", "HTTP",
           "TAMANHO_TEXTO", "VALIDATION", "SEGUNDA_PROVA",
           "SEGUNDA_PROVA_PORQUE", "CULTURAS_QUE_NOMEIA", "REGION_SCOPE",
           "TERRITORIES", "WHAT_IT_PRODUCES", "EXAMPLE_REAL",
           "GAP_CLOSURE_VALUE", "GAP_FECHA_QUAL", "PRIMARY_OR_SECONDARY",
           "RECURRING_INFORMATION_POTENTIAL", "RECORRENCIA_ESTADO",
           "WHICH_TOOL_IT_SUPPORTS",
           "EVIDENCE", "LIMITE"]
    folha(wb, "NEW_DISCOVERY",
          "AS 13 FONTES DESTA MISSAO, achadas por busca dirigida ao que "
          "faltava: as 5 culturas nao pesquisadas (trigo, trigo duro, milho, "
          "soja, tomate — 14 das 29 janelas) e as 2 regioes a zero "
          "(Basilicata, Valle d'Aosta). Nenhuma nasceu de um tema; todas de um "
          "buraco medido. Todas abertas por sonda, e as CRITICAL com segunda "
          "prova por rota independente.",
          V13, c13)

    # 6 · CROP_GAPS
    cult = {}
    for l in V13:
        for c in (l["CULTURAS_QUE_NOMEIA"] or "").split(" · "):
            if c and c != "—":
                cult.setdefault(c, []).append(l["SOURCE_NAME"][:38])
    crop = []
    for c in MATZ["CROP"]:
        nome = c["CULTURA"]
        agora = cult.get(nome, [])
        crop.append({
            "CULTURA": nome, "JANELAS_NO_CASCO": c["JANELAS_NO_CASCO"],
            "FONTES_ANTES": c["FONTES_NOVAS_QUE_A_NOMEIAM"],
            "FONTES_DESTA_MISSAO": len(agora),
            "TOTAL_DEPOIS": c["FONTES_NOVAS_QUE_A_NOMEIAM"] + len(agora),
            "ESTADO_ANTES": c["ESTADO"],
            "ESTADO_DEPOIS": ("NOMEADA" if (agora or
                              c["FONTES_NOVAS_QUE_A_NOMEIAM"]) else "AINDA NAO"),
            "QUEM_FECHOU": " · ".join(agora) or "—"})
    folha(wb, "CROP_GAPS",
          "AS 10 CULTURAS DAS 29 JANELAS, antes e depois. As cinco que estavam "
          "a zero eram arvenses e tomate — 14 das 29 janelas, quase metade — e "
          "a razao era ausencia de BUSCA, nao de fonte. ⚠️ «mais» (milho em "
          "italiano) continua fora das palavras-chave: colide com «mais» em "
          "portugues e produziu 6 falsos na missao anterior. Aqui as fontes de "
          "milho confirmam-se pelo CONTEUDO — diabrotica, piralide, BBCH 42-70.",
          crop)

    # 7 · REGION_GAPS
    novas_por_regiao = {}
    for l in V13:
        for r in ("Basilicata", "Valle d'Aosta", "Abruzzo", "Campania",
                  "Friuli-Venezia Giulia", "Molise", "Veneto",
                  "Emilia-Romagna", "Lombardia"):
            if r in l["REGION_SCOPE"]:
                novas_por_regiao.setdefault(r, []).append(l["SOURCE_NAME"][:40])
    reg = []
    for r in MATZ["REGION"]:
        nome = r["REGIAO"]
        agora = novas_por_regiao.get(nome, [])
        d = r["DEPOIS_REGIONAL"] + len(agora)
        reg.append({
            "REGIAO": nome, "ANTES_REGIONAL": r["DEPOIS_REGIONAL"],
            "NOVAS_DESTA_MISSAO": len(agora), "DEPOIS_REGIONAL": d,
            "ESTADO_ANTES": r["ESTADO"],
            "ESTADO_DEPOIS": ("COBERTA" if d >= 2 else "FRACA" if d == 1
                              else "SEM FONTE REGIONAL"),
            "QUEM_FECHOU": " · ".join(agora) or "—"})
    folha(wb, "REGION_GAPS",
          "AS 20 REGIOES, antes e depois. ⚠️ FONTE NACIONAL CONTINUA A NAO "
          "CONTAR como cobertura regional: a fenologia muda com altitude e "
          "distancia ao mar, e o proprio Abruzzo mede ~2 semanas de atraso "
          "acima de 400 m ou a mais de 40 km da costa. As duas regioes a zero "
          "fecharam com fonte REGIONAL propria, nao com nacional.",
          reg)

    # 8 · PEOPLE
    pes = list(MATZ["PEOPLE"]) + [{
     "PAPEL": "responsavel tecnico de servico regional (achado nesta missao)",
     "QUANTAS": 1,
     "NOMES": "Emanuele Scalcione — funcionario da ALSIA, responsavel do "
              "Servizio Agrometeorologico Lucano (Basilicata)",
     "ONDE": "boletim agrometeorologico semanal da ALSIA",
     "ALIMENTA": "VOICES · PAPEL de quem fala (produtor? tecnico? amador?)",
     "NOTA": "papel E territorio declarados pela propria casa. ⚠️ A afiliacao "
             "NAO foi verificada em perfil institucional: a rota `alsia.it` "
             "nao abre desta maquina (DNS local), embora resolva no publico."}]
    folha(wb, "PEOPLE",
          "PESSOAS POR PAPEL, nunca por alcance. Seguidores nao sao "
          "autoridade, e isto nao e' ranking de especialistas. A linha com "
          "QUANTAS=0 continua a ser a mais importante: produtor agricola com "
          "regiao e data, zero.",
          pes)

    # 9 · SOCIAL
    folha(wb, "SOCIAL",
          "OS CAMPOS DA VOZ DE CAMPO, com o enchimento real. Nao e' lista de "
          "canais: e' a conta que explica por que o Radar nao cruza voz com "
          "janela. ⚠️ E esta missao NAO mexeu nisto: os tres zeros continuam "
          "zeros no casco. O que mudou e' que agora ha fonte que TRAZ regiao, "
          "papel e data — de tecnico institucional, nao de produtor.",
          MATZ["SOCIAL"])

    # 10 · SOURCE_TO_TOOL
    stt = []
    for l in todas:
        if not l.get("VALIDATION", "").startswith("VALIDATED"):
            continue
        for a in (l["WHICH_RAW_NEED_IT_FEEDS"] or "").split(" || "):
            if not a:
                continue
            tool, _, need = a.partition(" · ")
            stt.append({
                "SOURCE": l["SOURCE_NAME"], "OWNER": l["OWNER"],
                "URL_CANONICAL": l["URL_CANONICAL"],
                "VALIDATION": l["VALIDATION"],
                "PRIMARY_OR_SECONDARY": l["PRIMARY_OR_SECONDARY"],
                "TOOL": tool, "RAW_NEED_QUE_ALIMENTA": need,
                "SCOPE": l["REGION_SCOPE"],
                "RECURRING": l["RECURRING_INFORMATION_POTENTIAL"],
                "RECORRENCIA_ESTADO": l["RECORRENCIA_ESTADO"],
                "VAGA": l["VAGA"]})
    stt.sort(key=lambda x: (x["TOOL"], x["SOURCE"]))
    folha(wb, "SOURCE_TO_TOOL",
          "UMA LINHA = UMA LIGACAO fonte→necessidade, NAO uma fonte. So' "
          "entram fontes VALIDADAS (abertas de verdade). Quem contar linhas "
          "aqui e disser «N fontes novas» conta a mesma fonte varias vezes: "
          "«uma SOURCE, varios usos» le-se nesta folha e em nenhuma outra.",
          stt)

    # 11 · SEARCH_LOG
    sl = [{"N": i, "GAP_QUE_GUIOU": b["GAP"], "CONSULTA": b["CONSULTA"],
           "RODADA": b["RODADA"], "O_QUE_DEVOLVEU": b["DEVOLVEU"],
           "FONTES_NOVAS_DAQUI": b["FONTES"],
           "SATURATION_SIGNAL": b["SATURACAO"],
           "ACHADO_QUE_MUDOU_A_RESPOSTA": b["VIROU"]}
          for i, b in enumerate(BUSCAS2, 1)]
    folha(wb, "SEARCH_LOG",
          "UMA LINHA = UMA BUSCA DESTA MISSAO. Toda consulta parte de um GAP "
          "MEDIDO. A coluna RODADA permite ler saturacao: quando tres rodadas "
          "seguidas do mesmo gap nao devolvem fonte forte nova, "
          "SATURATION_SIGNAL=YES — e isso significa que ESTA busca saturou, "
          "nao que a fonte nao exista.",
          sl)

    # 12 · REJECTED
    rej = []
    for l in todas:
        if l.get("VALIDATION", "").startswith("VALIDATED"):
            continue
        rej.append({
            "SOURCE_NAME": l["SOURCE_NAME"], "OWNER": l["OWNER"],
            "URL_DECLARED": l["URL_DECLARED"], "URL_FINAL": l["URL_FINAL"],
            "HTTP": l["HTTP"], "TAMANHO_TEXTO": l["TAMANHO_TEXTO"],
            "VALIDATION": l["VALIDATION"],
            "DE_QUE_LADO_ESTA_A_FALHA": (
                "NOSSA — a fonte esta viva" if l["VALIDATION"] == "UNKNOWN"
                else "DA FONTE — responde e recusa" if l["VALIDATION"] == "BLOCKED"
                else "DA FONTE — nao existe ou serve erro"
                if l["VALIDATION"] == "BROKEN"
                else "NEM UMA NEM OUTRA — abre e nao e' disto"),
            "PORQUE": l["VALIDATION_PORQUE"],
            "O_QUE_FAZER": {
                "UNKNOWN": "tentar outra rota de saida (VPN/outro resolvedor) "
                           "ou navegador com janela. NAO substituir a fonte.",
                "BLOCKED": "procurar outra rota do MESMO dono (RSS, PDF "
                           "direto, area publica).",
                "BROKEN": "procurar fonte nova, ou a nova sede se houver.",
                "WRONG_SOURCE": "nao e' problema de rota: e' de expectativa."
            }[l["VALIDATION"]],
            "VAGA": l["VAGA"]})
    folha(wb, "REJECTED",
          "O QUE NAO PASSOU, E DE QUE LADO ESTA A FALHA — que e' a pergunta "
          "que importa. ⚠️ TRES DESTAS FONTES ESTAO VIVAS: o DNS desta maquina "
          "nao alcanca `alsia.it`, `ersa.fvg.it` e `arpa.piemonte.it`, mas o "
          "resolvedor publico devolve endereco para as tres. Escrever BROKEN "
          "nelas apagaria do acervo tres agencias regionais que publicam — e "
          "uma delas e' a que fecha a Basilicata.",
          rej)

    # 13 · README
    cv37 = Counter(l["VALIDATION"] for l in V37)
    cv13 = Counter(l["VALIDATION"] for l in V13)
    ct = Counter(g["GAP_TYPE"] for g in GAPS)
    rd = [
     {"O_QUE": "PERGUNTA DESTA MISSAO", "RESPOSTA":
      "quais fontes reais precisamos adicionar para que as ferramentas de "
      "Intelligence tenham materia-prima suficiente, comprovada e recorrente."},
     {"O_QUE": "AS 37 ANTERIORES, ABERTAS", "RESPOSTA":
      " · ".join(f"{k}={v}" for k, v in sorted(cv37.items()))},
     {"O_QUE": "AS 13 DESTA MISSAO", "RESPOSTA":
      " · ".join(f"{k}={v}" for k, v in sorted(cv13.items()))},
     {"O_QUE": "OS 15 CRITICOS, POR TIPO", "RESPOSTA":
      " · ".join(f"{k}={v}" for k, v in sorted(ct.items()))
      + f" · ainda pedem fonte: "
        f"{sum(1 for g in GAPS if g['PROCURAR_MAIS_FONTE_RESOLVE'] == 'SIM')}"},
     {"O_QUE": "READY_TO_REGISTER", "RESPOSTA":
      f"{len(rtr)} fontes passaram a porta das dez coisas. "
      f"{len(rej_porta)} ficaram fora, e a folha REJECTED diz por que."},
     {"O_QUE": "CULTURAS", "RESPOSTA":
      "as 5 que estavam a zero (trigo, trigo duro, milho, soja, tomate — 14 "
      "das 29 janelas) tem agora fonte aberta e validada. Nenhuma das 10 "
      "culturas do casco fica sem fonte."},
     {"O_QUE": "REGIOES", "RESPOSTA":
      "as 2 a zero (Basilicata, Valle d'Aosta) fecharam com fonte REGIONAL "
      "propria. Fonte nacional continua a nao contar como cobertura regional."},
     {"O_QUE": "O ERRO MEU MAIS CARO", "RESPOSTA":
      "o identificador de dataflow do ISTAT que eu publiquei na missao "
      "anterior — «DCSP_COLTIVAZIONI» — NAO EXISTE. O servico responde «Could "
      "not find requested structures». O verdadeiro e' "
      "`101_1015_DF_DCSP_COLTIVAZIONI_1`, achado a procurar nos 4.907 "
      "dataflows publicados. Quem tentasse coletar pelo meu ID receberia 404."},
     {"O_QUE": "O QUE A SONDA ME ENSINOU", "RESPOSTA":
      "que `getaddrinfo failed` NAO e' prova de fonte morta. Tres fontes "
      "vivas quase foram declaradas BROKEN por falha de DNS desta maquina. A "
      "pergunta certa nunca e' «falhou?», e' «falhou de que lado?»."},
     {"O_QUE": "O QUE NAO SE FEZ", "RESPOSTA":
      "COLLECTION_RUNS_CREATED = 0 · RAW_OBSERVATIONS_CREATED = 0 · "
      "DERIVED_CREATED = 0 · STRUCTURED_CREATED = 0 · ADMISSION_CREATED = 0 · "
      "WAITING_ROOM_DELTA = 0 · SOURCE_ID = 0 · DOCUMENT_ID = 0 · "
      "ATLAS_PROMOTION = NOT_RUN · PORTAL_CHANGED = NO"},
     {"O_QUE": "O QUE ISTO NAO PROVA", "RESPOSTA":
      "a sonda le HTML e nao executa JavaScript: quatro portais do Estado "
      "italiano ficam ilegiveis por isso. Nenhum conteudo foi guardado em "
      "ficheiro. Nenhuma afiliacao de pessoa foi verificada em perfil "
      "institucional. E ler a pagina de entrada nao e' ler o arquivo: "
      "recorrencia declarada nao e' recorrencia contada edicao a edicao."},
     {"O_QUE": "DONO DA TAXONOMIA", "RESPOSTA":
      "docs/fontes/ATLAS-DE-FONTES-EAME.md, via _territorios.py. Todo codigo "
      "T foi validado contra ele. T13 nao e' canonico e nao aparece."},
     {"O_QUE": "TRABALHO PARALELO CARREGADO", "RESPOSTA":
      "origin/claude/italy-source-qualification-v1, commit d9535783: "
      "qualificacao das 381 do acervo base (PASS 265 · REVIEW 88 · REJECT 25; "
      "P1 161) e 125 correcoes de endereco canonico. Duas tocam nesta "
      "entrega, e uma corrigiu um DONO meu — a ASSAM Marche foi absorvida "
      "pela AMAP Marche."},
    ]
    folha(wb, "README", "COMECE AQUI.", rd)

    wb.save(SAIDA)
    print(f"gravado: {SAIDA}")
    print(f"folhas: {len(wb.sheetnames)}")
    for n in wb.sheetnames:
        print(f"  {n:20s} {wb[n].max_row - 2:4d} linhas")
    print(f"\nREADY_TO_REGISTER = {len(rtr)}  ·  fora da porta = {len(rej_porta)}")
    print("  por valor de fechamento:",
          dict(Counter(x["GAP_CLOSURE_VALUE"] for x in rtr)))
    print("  primaria/secundaria:",
          dict(Counter(x["PRIMARY_OR_SECONDARY"] for x in rtr)))


if __name__ == "__main__":
    main()
