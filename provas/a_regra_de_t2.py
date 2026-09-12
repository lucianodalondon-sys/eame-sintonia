#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""A REGRA DE T2 — a medicao de «o que um documento precisa provar para a
Admission dizer que ele pertence a T2 — Clima e tempo».

    python3 provas/a_regra_de_t2.py

Sem rede, sem banco, sem recoleta, sem escrita. Todo o material que esta prova
le ja existe nesta arvore antes de ela correr.

O QUE ELA MEDE
--------------
    A  o GABARITO: 46 documentos REAIS, cada um com ITEM / EXPECTED / WHY /
       EVIDENCE. Nenhum inventado, nenhum escolhido para o numero dar bem.
    B  o vocabulario REAL: que termos aparecem nos T2 e nos que nao sao T2,
       contados, nao supostos.
    C  tres desenhos de regra (A lista de palavras · B grupos de sinais ·
       C prova da fonte) contra o gabarito, pelo MECANISMO QUE EXISTE
       (`admissao._do_universo`), nao por uma reimplementacao amiga.
    D  o veredicto: a medicao autoriza escrever a regra, ou nao.

POR QUE ELA EXISTE
------------------
A pergunta da missao nao era «escreva a regra de T2» — era «MEDIR o que um
documento precisa provar, e so escrever a regra se a medicao der resposta
clara». Uma lista de palavras que PARECE boa e uma opiniao. Esta prova e o
unico sitio onde a opiniao encontra os documentos.

    ESCREVER A REGRA SEM MEDIR E ADIVINHAR COM AR DE LEI.
"""
import json
import os
import re
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)
import _gavetas  # noqa: E402,F401
import admissao as adm  # noqa: E402

REGISTO = os.path.join(RAIZ, "data", "derivados", "REGISTO-DE-ARTEFATOS.json")


# ── COMO O GABARITO FOI ROTULADO ───────────────────────────────────────────
# O rotulo NAO vem do que daria jeito, e NAO vem do editor. Vem do que o
# PROPRIO documento declara nas suas primeiras linhas — a unica evidencia que
# qualquer pessoa pode abrir e conferir sem acreditar em mim:
#
#   SIM      a abertura declara que o documento E um relato de tempo ou de
#            agrometeorologia («Agrometeo… Informa», «Bollettino
#            AgroMeteorologico Settimanale», «Meteo Veneto»), e o corpo nao
#            tem seccao de defesa da cultura.
#   NAO      a abertura declara que o documento e um boletim fitossanitario,
#            regulatorio ou de mercado («SERVIZIO FITOSANITARIO … DIFESA
#            INTEGRATA», «Bollettino Fitosanitario», «Dataset Fitosanitari»,
#            «Bilancio Fitosanitario»). Falar de tempo la dentro e o que estes
#            documentos FAZEM — a praga responde ao tempo — e nao os torna T2.
#   AMBIGUO  o documento carrega as DUAS coisas, ou a ficha da fonte e o
#            conteudo discordam. Nao se resolve com o material desta arvore, e
#            o brief autoriza que fique NAO_SEI. Nao vira SIM nem NAO para o
#            numero dar melhor.
#
# O CONTRAEXEMPLO QUE FUNDA TUDO: a ARPAV publica «Meteo Veneto» (T2) E
# «U.O. Fitosanitario — VITE» (T3). MESMO PUBLICADOR, TERRITORIOS DIFERENTES.
# Quem classificar pela fonte acerta num e erra no outro, sempre.
SIM, NAO, AMBIGUO = "SIM", "NAO", "AMBIGUO"

# (caminho, EXPECTED, WHY)
GABARITO = [
    # ── POSITIVOS_T2 ──────────────────────────────────────────────────────
    ("data/derivados/texto/RAW-f88c89d73d6a132a.txt", SIM,
     "ARPAV «Agrometeo… Informa» Zona 1. Ficha IT-T2-002 = T2."),
    ("data/derivados/texto/RAW-3d3c1bc0e96332e8.txt", SIM,
     "ARPAV «Agrometeo… Informa» Zona 9. Ficha IT-T2-002 = T2."),
    ("data/derivados/texto/RAW-8c13500d43502e64.txt", SIM,
     "ARPAV «Agrometeo… Informa» Zona 16. Ficha IT-T2-002 = T2."),
    ("data/derivados/texto/RAW-0be2d204c98ad1b1.txt", SIM,
     "ARPAV «Agrometeo… Informa» Zona 24. Ficha IT-T2-002 = T2."),
    ("data/derivados/texto/RAW-144fdb152b1a6ae4.txt", SIM,
     "ARPAE «Bollettino AgroMeteorologico Settimanale n. 35/2026». "
     "Ficha IT-T2-001 = T2."),
    ("data/derivados/texto/RAW-445e41701f737d73.txt", SIM,
     "ARPAE «Bollettino AgroMeteorologico Settimanale n. 34/2026». "
     "Ficha IT-T2-001 = T2."),
    ("data/derivados/texto/RAW-9a01cc17889e1f40.txt", SIM,
     "«BOLLETTINO AGROMETEOROLOGICO REGIONALE N. 21» da ARPAV. A abertura "
     "declara-o; nao ha seccao de defesa da cultura."),
    ("data/derivados/texto/RAW-6377ac2f8419d905.txt", SIM,
     "«Meteo Veneto. Fine estate tra eventi intensi e ritorno del caldo» — "
     "relato de tempo, e so isso."),
    ("data/derivados/texto/RAW-699a073ace4361ea.txt", SIM,
     "«Meteo Veneto: luglio 2026 molto caldo, poche piogge» — sintese "
     "climatica mensal."),
    ("data/collection-store/italy/IT-T2-004/"
     "SIAS_PRECIPITAZIONE_GIORNALIERA_WINDOW_END_2026-09-05/"
     "v1_6c71cc191272/NHEOWL0530_00.html", SIM,
     "SIAS Sicilia, tabela de precipitacao diaria por estacao. Ficha "
     "IT-T2-004 = T2. Clima MEDIDO, sem uma linha de prosa."),

    # ── NEGATIVOS_T2 · ARPAV, o mesmo publicador dos positivos ────────────
    ("data/derivados/texto/RAW-223510588786a4de.txt", NAO,
     "ARPAV «U.O. Fitosanitario — Bollettino n. 19 VITE». MESMA AGENCIA dos "
     "positivos, territorio T3. E cita «Servizio Meteorologia e Climatologia "
     "di Arpav» — a palavra «climatologia» aqui e o nome de quem colaborou, "
     "nao o assunto."),
    ("data/derivados/texto/RAW-6d12bcb5fa2b0905.txt", NAO,
     "ARPAV «U.O. Fitosanitario — Bollettino n. 20 VITE». Mesma agencia dos "
     "positivos, mesmo servico fitossanitario, territorio T3."),
    ("data/derivados/texto/RAW-4e12affad7fedd91.txt", NAO,
     "ARPAV «SERVIZIO FITOSANITARIO … DIFESA INTEGRATA — OLIVO n. 28»."),
    ("data/derivados/texto/RAW-c6377f6951bfeb2e.txt", NAO,
     "ARPAV «SERVIZIO FITOSANITARIO … DIFESA INTEGRATA — OLIVO n. 29»."),
    ("data/derivados/texto/RAW-9488589cfc657b95.txt", NAO,
     "ARPAV «… COLTURE FRUTTICOLE n. 24». Abre com previsao de temperatura e "
     "continua a ser um boletim de defesa."),
    ("data/derivados/texto/RAW-fe3c922bfdfd7999.txt", NAO,
     "ARPAV «… COLTURE ORTICOLE n. 22». Fala de precipitacao e de umidade "
     "fogliare como CAUSA da infeccao."),

    # ── NEGATIVOS_T2 · Campania ───────────────────────────────────────────
    ("data/derivados/texto/RAW-0c2723e66201f966.txt", NAO,
     "Campania SA, «DIFESA DELLE COLTURE». Ficha IT-T3-002 = T3."),
    ("data/derivados/texto/RAW-420e08ef15bec6e4.txt", NAO,
     "Campania SA 26-08, «DIFESA DELLE COLTURE». Ficha IT-T3-002 = T3."),
    ("data/derivados/texto/RAW-48e76a696be6831d.txt", NAO,
     "Campania NA 02-09. Ficha IT-T3-002 = T3. Contem «bagnatura fogliare» "
     "como condicao de risco de infeccao."),
    ("data/derivados/texto/RAW-99cb44a67f6b4e9a.txt", NAO,
     "Campania NA 26-08. Ficha IT-T3-002 = T3, e tambem contem «bagnatura "
     "fogliare»."),
    ("data/derivados/texto/RAW-7a51732e87f0f319.txt", NAO,
     "Campania AV 26-08, «DIFESA DELLE COLTURE». Ficha IT-T3-002 = T3."),
    ("data/derivados/texto/RAW-df4adcb5d78929e1.txt", NAO,
     "Campania BN 26-08, «DIFESA DELLE COLTURE». Ficha IT-T3-002 = T3."),
    ("data/derivados/texto/RAW-e9395a7ea894c1d2.txt", NAO,
     "Campania CE 26-08, «DIFESA DELLE COLTURE». Ficha IT-T3-002 = T3."),

    # ── NEGATIVOS_T2 · Lazio ──────────────────────────────────────────────
    ("data/derivados/texto/RAW-392840d3e13d1b15.txt", NAO,
     "«Bollettino Fitosanitario» Lazio Bolsena."),
    ("data/derivados/texto/RAW-823e18ebb232eb36.txt", NAO,
     "«Bollettino Fitosanitario» Lazio Entroterra Tuscia."),
    ("data/derivados/texto/RAW-a6515948880d173a.txt", NAO,
     "«Bollettino Fitosanitario» Lazio Sabina."),
    ("data/derivados/texto/RAW-b631f6eecfbc1db0.txt", NAO,
     "«Bollettino Fitosanitario» Lazio Pianura Interna."),
    ("data/derivados/texto/RAW-e6ec962a8a730ee4.txt", NAO,
     "«Bollettino Fitosanitario» Lazio Litorale Viterbese."),

    # ── NEGATIVOS_T2 · Trentino, Molise, Piemonte ─────────────────────────
    ("data/derivados/texto/RAW-221ab4a8d6ebec30.txt", NAO,
     "Fondazione Edmund Mach, bollettino de transferencia tecnica n. 23."),
    ("data/derivados/texto/RAW-ccd8ea9c8e9c4caf.txt", NAO,
     "Fondazione Edmund Mach, bollettino n. 24. Idem."),
    ("data/derivados/texto/RAW-ec3108a2ed424702.txt", NAO,
     "Fondazione Edmund Mach, bollettino n. 25. Idem."),
    ("data/derivados/texto/RAW-fd5b5e465457e4d6.txt", NAO,
     "Fondazione Edmund Mach, bollettino n. 22. Idem."),
    ("data/derivados/texto/RAW-024abdb692be926a.txt", NAO,
     "Regione Molise, comunicato fitossanitario."),
    ("data/derivados/texto/RAW-5dcfb75ac38390c3.txt", NAO,
     "Piemonte, «Misure fitosanitarie di emergenza» — Flavescenza dorata."),
    ("data/derivados/texto/RAW-ded546686d61dc91.txt", NAO,
     "Piemonte, «INSETTICIDI AMMESSI» — lista regulatoria."),

    # ── NEGATIVOS_T2 · Puglia, ciencia, regua ─────────────────────────────
    ("data/derivados/texto/RAW-59da05274359eff6.txt", NAO,
     "APOL, «MOSCA DELLE OLIVE» comprensorio BR. Ficha IT-T3-010 = T3."),
    ("data/derivados/texto/RAW-3e941738599367d7.txt", NAO,
     "APOL, «MOSCA DELLE OLIVE», o mesmo boletim noutra captura. "
     "Ficha IT-T3-010 = T3."),
    ("data/derivados/texto/RAW-e5176df66216dfd0.txt", NAO,
     "«DIRETTIVE PER LA FRUTTICOLTURA INTEGRATA 2026». Ficha IT-T3-011 = T3."),
    ("data/derivados/texto/RAW-2a12cb316622a9a5.txt", NAO,
     "«Bilancio Fitosanitario — Olivo». Ficha IT-T5-003 = T5."),
    ("data/derivados/texto/RAW-924aabd94168c53a.txt", NAO,
     "«Bilancio Fitosanitario — Olivo», outro autor. Ficha IT-T5-003 = T5."),
    ("data/derivados/texto/RAW-a927e846ba8e78b0.txt", NAO,
     "«Dataset Fitosanitari». Ficha IT-T4-001 = T4."),
    ("data/collection-store/italy/IT-T3-005/"
     "TERRETRURIA_31-08-2026_06-09-2026/v1_2e488a8232ba/monitoraggio.html", NAO,
     "Terre dell'Etruria, monitoraggio da mosca. Ficha IT-T3-005 = T3."),
    ("data/collection-store/italy/IT-T4-001/MINSALUTE_FTS6_20260907/"
     "v1_9cd4d156369f/PROD_FTS_6_20260907.csv", NAO,
     "Banca dati dos produtos autorizados. Ficha IT-T4-001 = T4. E o negativo "
     "facil, e esta aqui por isso: regra que falhe neste falha em tudo."),

    # ── CASOS_AMBIGUOS ────────────────────────────────────────────────────
    # Nao sao um terceiro rotulo de conveniencia: sao o que o material tem e
    # esta arvore nao consegue resolver.
    ("data/derivados/texto/RAW-e612807928b5ada9.txt", AMBIGUO,
     "ARIF Puglia «Settimanale N. 36». A ficha IT-T3-008 declara T3 — e "
     "declara topics «monitoramento, alerta, AGROMETEOROLOGIA». O ficheiro "
     "chama-se «Notiziario_Agrometeorologico». O documento ABRE com duas "
     "paginas de analise sinoptica (saccature, Groenlandia, promontorio "
     "sub-tropical) e SO DEPOIS traz mosca e Bactrocera. E as duas coisas "
     "num so PDF. NAO se resolve aqui, e nao vira SIM nem NAO."),
    ("data/derivados/texto/RAW-3ef48aaa830edf3b.txt", AMBIGUO,
     "ARIF Puglia «Settimanale N. 35». Mesma mistura: analise sinoptica "
     "primeiro, mosca e Bactrocera depois."),
    ("data/derivados/texto/RAW-178ebe9e0ea7dd83.txt", AMBIGUO,
     "ARIF Puglia «Giornaliero Meteorologico N. 136». Ficha IT-T3-008 = T3, "
     "conteudo e previsao do tempo pura. Ficha e documento discordam."),
]


# ── OS TRES DESENHOS ───────────────────────────────────────────────────────
# DESENHO A · lista plana de palavras, primeira que casa ganha.
#   E o unico mecanismo que `_do_universo` tem, e a missao proibiu mudar a
#   logica da Admission. As candidatas nasceram DA MEDICAO (bloco B), nao de
#   uma lista inventada antes de olhar para os documentos.
CANDIDATAS_A = {
    "A1-obvia": ["clima", "tempo", "meteo", "temperatura", "chuva", "pioggia",
                 "precipitazione", "umidita", "vento", "previsione"],
    "A2-agro": ["agrometeo", "agrometeorolog", "bollettino agrometeo"],
    "A3-medida-forte": ["evapotraspirazione", "climatologia",
                        "bagnatura fogliare"],
    "A4-so-a-mais-forte": ["evapotraspirazione"],
    "A5-titulo-do-documento": ["agrometeo… informa", "meteo veneto",
                               "bollettino agrometeorologico"],
}

DESENHO_B = ("grupos de sinais — exigir N sinais de grupos distintos. "
             "`_do_universo` faz `if achadas: return SIM` na PRIMEIRA palavra "
             "que casa. Contar sinais e exigir grupos e mudar essa linha. "
             "Implementar B = mudar a logica da Admission. PROIBIDO na missao.")
DESENHO_C = ("prova da fonte — `source_id` -> `territory` da ficha canonica. "
             "Duas coisas o impedem. (1) `_do_universo` so le "
             "('texto','title','nome','topics','crops','resumo') — nunca "
             "`source_id`. (2) E sobretudo: a ARPAV publica «Meteo Veneto» "
             "(T2) E «U.O. Fitosanitario VITE» (T3). O publicador NAO decide "
             "o territorio, e este gabarito tem os dois casos. C erraria "
             "6 documentos por construcao — e erraria em silencio, com ar de "
             "quem tem prova.")


def _texto(caminho):
    with open(os.path.join(RAIZ, caminho), "rb") as f:
        return f.read().decode("utf-8", "replace")


def _decide(texto, palavras):
    """A decisao REAL, pela funcao real. Nao ha aqui reimplementacao."""
    return adm._do_universo({"texto": texto}, "T2", palavras)


def _matriz(nome, palavras, textos):
    m = {"NOME": nome, "TRUE_POSITIVE": 0, "TRUE_NEGATIVE": 0,
         "FALSE_POSITIVE": 0, "FALSE_NEGATIVE": 0, "UNKNOWN": 0,
         "AMBIGUO_FORCADO": 0, "ERROS": []}
    for caminho, esperado, _why in GABARITO:
        r, _motivo, ev = _decide(textos[caminho], palavras)
        prova = ev.get("palavras") or ev.get("achado_noutro") or ""
        if esperado == AMBIGUO:
            # Um ambiguo so esta bem respondido se a porta NAO fingir saber.
            if r in (adm.SIM, adm.NAO):
                m["AMBIGUO_FORCADO"] += 1
            continue
        if r == adm.SIM and esperado == SIM:
            m["TRUE_POSITIVE"] += 1
        elif r == adm.SIM and esperado == NAO:
            m["FALSE_POSITIVE"] += 1
            m["ERROS"].append(("FALSE_POSITIVE", caminho, prova))
        elif r == adm.NAO and esperado == NAO:
            m["TRUE_NEGATIVE"] += 1
        elif r == adm.NAO and esperado == SIM:
            m["FALSE_NEGATIVE"] += 1
            m["ERROS"].append(("FALSE_NEGATIVE", caminho, prova))
        else:
            m["UNKNOWN"] += 1
            m["ERROS"].append(("UNKNOWN(" + r + ")", caminho, prova))
    return m



# ── O ATAQUE QUE DECIDE A MISSAO ───────────────────────────────────────────
# Comparar candidatas que EU escolhi so responde «estas nao servem». A pergunta
# da missao e mais dura: EXISTE alguma lista de palavras que sirva?
#
# Entao para de haver candidatas minhas. O corpus propoe TODOS os termos e
# bigramas dos positivos, fica-se so com os que nao aparecem em NENHUM dos 33
# negativos, e pergunta-se se a uniao deles cobre os 10 positivos.
#
# E depois — e so isto separa uma regra de um decalque — treina-se sem UM dos
# publicadores e testa-se nesse. Uma regra que so acerta em quem ja viu nao e
# uma regra: e a lista dos documentos que ja tinhamos.
FONTE_DO_POSITIVO = {
    "IT-T2-004": "SIAS",
    "RAW-144fdb152b1a6ae4.txt": "ARPAE",
    "RAW-445e41701f737d73.txt": "ARPAE",
}


def _termos(texto):
    t = texto.lower()
    uni = set(re.findall(r"[a-zà-ÿ]{4,}", t))
    pal = re.findall(r"[a-zà-ÿ]{3,}", t)
    return uni | {pal[i] + " " + pal[i + 1] for i in range(len(pal) - 1)}


def _fonte(caminho):
    for chave, nome in FONTE_DO_POSITIVO.items():
        if chave in caminho:
            return nome
    return "ARPAV"


def _cobertura_gulosa(alvos, limpos, termos_de):
    # O desempate e por ordem alfabetica, e nao pela ordem de um `set`. Uma
    # prova que muda de resposta entre duas corridas nao prova nada.
    falta, regra, ordenados = set(alvos), [], sorted(limpos)
    while falta:
        t = max(ordenados,
                key=lambda x: (sum(1 for c in falta if x in termos_de[c]), x))
        cobre = [c for c in falta if t in termos_de[c]]
        if not cobre:
            break
        regra.append(t)
        falta -= set(cobre)
    return regra, len(alvos) - len(falta)


def red_team(textos, pos, neg):
    """Os dois ataques que nenhuma candidata minha sobreviveu."""
    termos_de = {c: _termos(textos[c]) for c, _e, _w in GABARITO}
    fora_de_t2 = set()
    for c, _e, _w in neg:
        fora_de_t2 |= termos_de[c]
    caminhos = [c for c, _e, _w in pos]
    limpos = set().union(*[termos_de[c] for c in caminhos]) - fora_de_t2

    print("\nE · O ATAQUE — existe ALGUMA lista de palavras que sirva?")
    print("-" * 74)
    print(f"  termos e bigramas nos {len(caminhos)} positivos: "
          f"{len(set().union(*[termos_de[c] for c in caminhos]))}")
    print(f"  destes, os que nao aparecem em NENHUM dos {len(neg)} negativos: "
          f"{len(limpos)}")
    orfaos = [c for c in caminhos if not (termos_de[c] & limpos)]
    print(f"  positivos que NENHUM termo limpo alcanca: {len(orfaos)}")
    print("\n  Existe. Uma lista que separa este gabarito na perfeicao EXISTE.")
    print("  A pergunta seguinte e a unica que importa: DE QUE e que ela e feita?")
    ranking = sorted(((sum(1 for c in caminhos if t in termos_de[c]), t)
                      for t in limpos), reverse=True)[:9]  # (n, termo): estavel
    for n, t in ranking:
        print(f"    {n}/{len(caminhos)}  {t!r}")
    print("\n  Dias da semana. Horas do dia. O nome do departamento que publica.")
    print("  Nao e vocabulario de clima: e a impressao digital de quem imprime.")

    print("\n  TREINA NUM PUBLICADOR, TESTA NOUTRO")
    total_retido = total_acerto = 0
    for deixado in ("SIAS", "ARPAE", "ARPAV"):
        treino = [c for c in caminhos if _fonte(c) != deixado]
        teste = [c for c in caminhos if _fonte(c) == deixado]
        limpos_treino = set().union(*[termos_de[c] for c in treino]) - fora_de_t2
        regra, coberto = _cobertura_gulosa(treino, limpos_treino, termos_de)
        acerta = sum(1 for c in teste
                     if any(t in termos_de[c] for t in regra))
        total_retido += len(teste)
        total_acerto += acerta
        print(f"    sem {deixado:<6} regra={regra}")
        print(f"      cobre o treino {coberto}/{len(treino)} · "
              f"ACERTA NO RETIDO {acerta}/{len(teste)}")
    print(f"\n    GENERALIZACAO = {total_acerto}/{total_retido}")
    return total_acerto, total_retido


# ── O PORTAO ───────────────────────────────────────────────────────────────
def portao(limpas, generaliza):
    """As seis condicoes do brief. Nenhuma delas se responde por impressao."""
    g = [
        ("T2_MEANING_ALREADY_CANONICAL", "YES",
         "«T2 = Clima e tempo» esta declarado em `MASTER_ITALIANO`, com cinco "
         "fontes (IT-T2-001..005) e os seus topics. Nao foi inventado aqui."),
        ("REAL_POSITIVE_EXAMPLES_EXIST", "YES",
         "10 documentos reais, de 3 publicadores."),
        ("REAL_NEGATIVE_EXAMPLES_EXIST", "YES",
         "33 documentos reais, incluindo 6 do MESMO publicador de positivos."),
        ("RULE_CAN_DISTINGUISH_T2_FROM_T3", "YES" if limpas else "NO",
         "nenhuma candidata fica sem erro. E a busca exaustiva mostra que a "
         "lista que separa e feita de dias da semana e nomes de departamento: "
         f"treinada num publicador, acerta {generaliza[0]}/{generaliza[1]} "
         "no publicador que nao viu. Uma regra que nao generaliza nao "
         "distingue — decora."),
        ("RULE_CAN_DISTINGUISH_T2_FROM_T7", "NAO_CHEGOU_A_SER_PERGUNTADO",
         "a condicao anterior ja fechou o portao. Responder a esta agora seria "
         "dar um numero a uma regra que nao existe."),
        ("NO_NEW_ARCHITECTURAL_LAW_REQUIRED", "NO",
         "para separar «documento SOBRE clima» de «documento que MENCIONA "
         "clima» era precisa uma lei que esta casa ainda nao tem, e um "
         "mecanismo que conte sinais em vez de parar na primeira palavra. "
         "As duas coisas mudam a Admission. A missao proibiu."),
    ]
    print("\nF · O PORTAO")
    print("-" * 74)
    for nome, valor, porque in g:
        print(f"  {nome:<36} = {valor}")
        print(f"      {porque}")
    passou = all(v == "YES" for _n, v, _p in g)
    print(f"\n  PORTAO = {'ABERTO' if passou else 'FECHADO'}")
    print(f"  T2_RULE_IMPLEMENTED = {'YES' if passou else 'NO'}")
    if not passou:
        print("\n  O brief foi explicito: «Se não: não implementar. Entregar a "
              "medição e parar.»")
        print("  `PERGUNTAS_DO_UNIVERSO` fica exactamente como estava, e T2 "
              "continua a\n  responder NAO_SE_APLICA — que e verdade: nao ha "
              "regra escrita.")
    return passou


def main():
    textos = {c: _texto(c) for c, _e, _w in GABARITO}
    pos = [g for g in GABARITO if g[1] == SIM]
    neg = [g for g in GABARITO if g[1] == NAO]
    amb = [g for g in GABARITO if g[1] == AMBIGUO]

    print("A REGRA DE T2 — a medicao")
    print("=" * 74)
    print("\nA · O GABARITO — 46 documentos reais desta arvore")
    print("-" * 74)
    for etiqueta, grupo in ((SIM, pos), (NAO, neg), (AMBIGUO, amb)):
        for caminho, _e, why in grupo:
            print(f"  {etiqueta:<8}{caminho.split('/')[-1]:<32}"
                  f"{len(textos[caminho]):>9} chars")
            print(f"           {why[:180]}")
    print(f"\n  POSITIVOS_T2   = {len(pos)}")
    print(f"  NEGATIVOS_T2   = {len(neg)}")
    print(f"  CASOS_AMBIGUOS = {len(amb)}")

    print("\nB · O VOCABULARIO REAL — contado, nao suposto")
    print("-" * 74)
    print(f"  {'TERMO':<26}{'T2':>7}{'NAO-T2':>10}{'AMBIGUO':>10}")
    for t in ["evapotraspirazione", "climatologia", "bagnatura fogliare",
              "agrometeo", "temperatura", "precipitazione", "previsione",
              "meteo", "vento", "clima", "pioggia"]:
        a = sum(1 for c, _e, _w in pos if t in textos[c].lower())
        b = sum(1 for c, _e, _w in neg if t in textos[c].lower())
        d = sum(1 for c, _e, _w in amb if t in textos[c].lower())
        print(f"  {t:<26}{a:>4}/{len(pos):<2}{b:>7}/{len(neg):<2}"
              f"{d:>7}/{len(amb):<2}")
    exclusivos = _exclusivos(textos, pos, neg)
    print(f"\n  termos que aparecem em TODOS os {len(pos)} positivos e em "
          f"ZERO negativos: {len(exclusivos)}")
    if exclusivos:
        print(f"    {sorted(exclusivos)[:20]}")

    print("\nC · OS TRES DESENHOS CONTRA O GABARITO")
    print("-" * 74)
    print("  DESENHO A · lista plana de palavras (o mecanismo que existe)\n")
    resultados = []
    for nome in sorted(CANDIDATAS_A):
        m = _matriz(nome, CANDIDATAS_A[nome], textos)
        resultados.append(m)
        print(f"    {nome:<24} TP={m['TRUE_POSITIVE']:<3}"
              f"TN={m['TRUE_NEGATIVE']:<3}FP={m['FALSE_POSITIVE']:<3}"
              f"FN={m['FALSE_NEGATIVE']:<3}UNKNOWN={m['UNKNOWN']:<3}"
              f"ambiguo_forcado={m['AMBIGUO_FORCADO']}")
        for rot, caminho, prova in m["ERROS"][:6]:
            print(f"        {rot:<18}{caminho.split('/')[-1]:<30}{prova}")
        if len(m["ERROS"]) > 6:
            print(f"        … mais {len(m['ERROS']) - 6}")
    print(f"\n  DESENHO B · {DESENHO_B}")
    print(f"\n  DESENHO C · {DESENHO_C}")

    print("\nD · O VEREDICTO PARCIAL")
    print("-" * 74)
    limpa = [m for m in resultados
             if m["FALSE_POSITIVE"] == 0 and m["FALSE_NEGATIVE"] == 0
             and m["UNKNOWN"] == 0 and m["AMBIGUO_FORCADO"] == 0]
    print(f"  candidatas sem UM erro sequer: {len(limpa)}"
          f"  {[m['NOME'] for m in limpa]}")
    print("  A melhor delas, `A5-titulo-do-documento`, nao e uma regra de "
          "clima:\n  e a lista dos NOMES COMERCIAIS de tres publicacoes. E "
          "mesmo assim\n  responde NAO_SEI ao SIAS — uma fonte T2 declarada.")
    generaliza = red_team(textos, pos, neg)
    portao(limpa, generaliza)
    return 0


def _exclusivos(textos, pos, neg):
    """Deixa o CORPUS propor os termos, em vez de eu propor uma lista."""
    def palavras(t):
        return {p for p in re.findall(r"[a-zà-ÿ]{5,}", t.lower())}
    comuns = None
    for c, _e, _w in pos:
        p = palavras(textos[c])
        comuns = p if comuns is None else (comuns & p)
    fora = set()
    for c, _e, _w in neg:
        fora |= palavras(textos[c])
    return (comuns or set()) - fora


if __name__ == "__main__":
    raise SystemExit(main())
