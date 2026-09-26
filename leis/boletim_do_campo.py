#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""O BOLETIM DO CAMPO — cultura, praga/doenca e fase lidas no texto de um boletim (T3 fitossanitario,
T2 agrometeo), cada uma com o TRECHO que a prova. EXTRATOR-EVENTO-V2 (D84, 26/09).

    ler_boletim(texto) -> {"SECOES": [...], "CULTURAS": [...], "PROBLEMAS": [...], "FASES": [...]}

POR QUE EXISTE. A ferramenta n.o 1 do casco (FINESTRE COLTURALI) precisa de cultura + problema + fase +
periodo no MESMO registo. Nos 94 itens da Sala, cultura e fase estavam NAO SEI em 94/94 — e o texto dos
boletins TEM as tres: «COLTURA … ACTINIDIA … Stadio fenologico … Ingrossamento frutto … CIMICE ASIATICA
(Halyomorpha halys); Non Presente» (IT-T3-002, Salerno). A porta so lia a cultura no titulo e na frase do
lugar (`admissao._cultura_fora_da_regua`), e a fase so pela regua T1.

O QUE ELE FAZ, E O QUE NAO FAZ
  · Um boletim fala de VARIAS culturas. Ler o texto inteiro como uma lista juntaria a praga do olivo com a
    fase da vite. Por isso parte-se o texto em SECOES, uma por cultura, pela linha que NOMEIA a cultura
    (cabecalho curto: «OLIVO», «Vite da vino», «COLTURA … ACTINIDIA»), e cada praga e fase fica na secao
    onde esta escrita. Texto antes da primeira cultura fica numa secao SEM cultura — nunca emprestada.
  · PRAGA MARCADA COMO AUSENTE NAO E OCORRENCIA. «Non presente», «assente», «nessuna segnalazione»,
    «non rilevat…» junto ao nome: ESTADO = AUSENTE. Sem marca: ESTADO = CITADA (o boletim fala dela; a
    frase nao diz se foi observada). So «presente», «rilevat…», «catture», «infestazion…», «sintomi» dao
    ESTADO = PRESENTE.
  · Nao normaliza (nao e EPPO nem BBCH): a FORMA e a do texto, em minusculas.
  · Nao le datas: o periodo do boletim e do leitor do facto (`leis/fato_do_texto.py`, DA-6).
Funcao PURA: sem rede, sem banco, sem ficheiros.
"""
from __future__ import annotations

import re
import unicodedata

# ── os vocabularios (declarados; medidos nos 5 T3 + 1 T2 da Sala e nos boletins do acervo) ─────────────
# A cultura: o vocabulario da regua T1 (`admissao.CULTURA_OBRIGATORIA["T1"]`, copiado por nome para esta
# funcao continuar pura) + as culturas que os boletins da Campania e da Puglia nomeiam e que a regua nao tem.
CULTURAS = (
    "vite", "vigneto", "uva da tavola", "uva da vino", "olivo", "oliveto", "melo", "pero", "pesco",
    "nettarina", "ciliegio", "actinidia", "kiwi", "albicocco", "susino", "castagno", "nocciolo", "noce",
    "mandorlo", "fico", "agrumi", "arancio", "limone", "mandarino", "clementine", "fragola", "frumento",
    "grano duro", "grano tenero", "orzo", "mais", "girasole", "soia", "barbabietola", "pomodoro", "patata",
    "carciofo", "melanzana", "peperone", "zucchina", "cetriolo", "lattuga", "cavolfiore", "cavolo",
    "finocchio", "cipolla", "aglio", "fagiolo", "fagiolino", "pisello", "cece", "tabacco", "melone",
    "anguria", "cocomero", "asparago", "sedano", "spinacio", "rucola", "mirtillo", "lampone", "mora",
)
# a forma plural / a outra forma que o texto usa, apontando para a forma do vocabulario
FORMAS = {"viti": "vite", "vigneti": "vigneto", "olive": "olivo", "ulivo": "olivo", "ulivi": "olivo",
          "olivi": "olivo", "oliveti": "oliveto", "mele": "melo", "pere": "pero", "pesche": "pesco",
          "nettarine": "nettarina", "ciliegie": "ciliegio", "albicocche": "albicocco", "susine": "susino",
          "castagne": "castagno", "nocciole": "nocciolo", "noci": "noce", "mandorle": "mandorlo",
          "fragole": "fragola", "pomodori": "pomodoro", "patate": "patata", "carciofi": "carciofo",
          "melanzane": "melanzana", "peperoni": "peperone", "zucchine": "zucchina", "cetrioli": "cetriolo",
          "cavoli": "cavolo", "finocchi": "finocchio", "cipolle": "cipolla", "fagioli": "fagiolo",
          "fagiolini": "fagiolino", "piselli": "pisello", "ceci": "cece", "meloni": "melone",
          "asparagi": "asparago", "mirtilli": "mirtillo", "lamponi": "lampone", "agrume": "agrumi"}

# Pragas e doencas: a lista T3 da regua (`admissao._do_universo["T3"]`: peronospora, oidio, botrite,
# ticchiolatura) + os nomes comuns que os boletins medidos escrevem. Raizes, palavra inteira a esquerda.
PROBLEMAS = (
    r"peronospor[ae]", r"oidio", r"mal\s+bianco", r"botrite", r"muffa\s+grigia", r"ticchiolatura",
    r"cimice\s+asiatica", r"cimic[ei]", r"halyomorpha\s+halys", r"mosca\s+dell['’\s]*oliv[ao]",
    r"mosca\s+della\s+frutta", r"mosca\s+mediterranea", r"ceratitis\s+capitata", r"bactrocera\s+oleae",
    r"tignol[ae](?:tta)?(?:\s+(?:della\s+vite|dell['’\s]*olivo|orientale))?", r"lobesia(?:\s+botrana)?",
    r"carpocapsa", r"cydia(?:\s+\w+)?", r"cocciniglia", r"afid[ei]", r"pidocch\w*", r"ragnetto\s+rosso",
    r"tripid[ei]", r"psill[ae]", r"flavescenza\s+dorata", r"mal\s+secco", r"occhio\s+di\s+pavone",
    r"lebbra", r"monilia", r"corineo", r"bolla", r"cercospor\w*", r"septoria", r"ruggin[ei]", r"fusari\w*",
    r"alternari\w*", r"batterios[ie]", r"xylella(?:\s+fastidiosa)?", r"drosophila\s+suzukii",
    r"popillia\s+japonica", r"dorifora", r"elateridi", r"nottu[ae]", r"piralide", r"diabrotica",
    r"escoriosi", r"black\s*rot", r"marciume\s+(?!(?:del|della|dei|delle|degli|di|da))\w+", r"virosi", r"virus", r"nematod[ie]",
)
# Fases / estadios, como os boletins os escrevem (o vocabulario T1 da regua + os medidos nos boletins).
FASES = (
    r"ripresa\s+vegetativa", r"riposo\s+vegetativo", r"gemm[ae]\s+(?:gonfi[ae]|cotonos[ae]|ferm[ae])",
    r"germogliamento", r"germogli\s+di\s+\d+", r"foglie\s+distese", r"prefioritura", r"inizio\s+fioritura",
    r"piena\s+fioritura", r"fine\s+fioritura", r"fioritura", r"mignolatura", r"allegagione",
    r"accrescimento\s+(?:frutti|frutto|acini|drupe)", r"ingrossamento\s+(?:frutti|frutto|acini|drupe)",
    r"chiusura\s+(?:del\s+)?grappolo", r"pre-?chiusura\s+grappolo", r"invaiatura", r"indurimento\s+(?:del\s+)?nocciolo",
    r"inolizione", r"maturazione", r"pre-?raccolta", r"raccolta", r"vendemmia", r"post-?raccolta",
    r"caduta\s+(?:delle\s+)?foglie", r"semina", r"emergenza", r"levata", r"spigatura", r"trapianto",
    r"bbch\s*\d{1,2}(?:\s*[-–]\s*\d{1,2})?",
)
_AUSENTE = re.compile(r"(?:non\s+presente|non\s+present[ei]|assent[ei]|nessun[ao]?\s+segnalazion[ei]|"
                      r"non\s+rilevat[oaie]|non\s+segnalat[oaie]|nulla|nessun[ao]?\s+(?:cattur[ae]|sintom[oi]))",
                      re.I)
_PRESENTE = re.compile(r"(?:(?<!non\s)present[ei]|(?<!non\s)rilevat[oaie]|(?<!non\s)segnalat[oaie]|cattur[ae]|"
                       r"infestazion[ei]|sintomi|focola[io]|attacch[io])", re.I)
JANELA_DO_ESTADO = 60          # letras depois do nome da praga onde se le «Non presente»

# a linha que NOMEIA uma cultura e abre a secao dela: curta, e a cultura e o essencial dela
PALAVRAS_DO_CABECALHO = 6


def _dobrar(s: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFKD", str(s or "")) if not unicodedata.combining(c)).lower()


_RE_CULTURA = re.compile(r"(?<![a-z])(%s)(?![a-z])" % "|".join(
    sorted([re.escape(c) for c in CULTURAS] + [re.escape(f) for f in FORMAS], key=len, reverse=True)))
_RE_PROBLEMA = re.compile(r"(?<![a-z])(?:%s)(?![a-z])" % "|".join(PROBLEMAS))
_RE_FASE = re.compile(r"(?<![a-z])(?:%s)(?![a-z])" % "|".join(FASES))


def _forma(c: str) -> str:
    c = re.sub(r"\s+", " ", c.strip())
    return FORMAS.get(c, c)


def _trecho(linha: str, ini: int, fim: int, n: int = 90) -> str:
    return re.sub(r"\s+", " ", linha[max(0, ini - n):fim + n]).strip()


def _cabecalho_de_cultura(linha: str) -> str | None:
    """A cultura que esta linha NOMEIA como cabecalho de secao, ou None."""
    d = _dobrar(linha).strip(" •·-–:;")
    palavras = re.findall(r"[a-z']+", d)
    if not palavras or len(palavras) > PALAVRAS_DO_CABECALHO:
        return None
    m = _RE_CULTURA.search(d)
    if not m:
        return None
    # «COLTURA … ACTINIDIA», «OLIVO», «Vite da vino», «Pomodoro in serra»: a cultura e o essencial da linha
    return _forma(m.group(1))


def ler_boletim(texto: str) -> dict:
    linhas = [l for l in str(texto or "").splitlines()]
    secoes = [{"CULTURA": None, "LINHA": 0, "PROBLEMAS": [], "FASES": []}]
    for n, linha in enumerate(linhas):
        c = _cabecalho_de_cultura(linha)
        if c:
            if secoes[-1]["CULTURA"] == c:
                continue                     # a mesma cultura outra vez (IT-T3-010: «OLIVO» dez vezes): a mesma secao
            secoes.append({"CULTURA": c, "LINHA": n + 1, "TRECHO_DA_CULTURA": linha.strip()[:120],
                           "PROBLEMAS": [], "FASES": []})
            continue
        d = _dobrar(linha)
        s = secoes[-1]
        for m in _RE_PROBLEMA.finditer(d):
            nome = re.sub(r"\s+", " ", m.group(0))
            depois = d[m.end():m.end() + JANELA_DO_ESTADO] + " " + " ".join(
                _dobrar(x) for x in linhas[n + 1:n + 3])[:JANELA_DO_ESTADO]
            estado = ("AUSENTE" if _AUSENTE.search(depois.split(".")[0][:JANELA_DO_ESTADO])
                      else "PRESENTE" if _PRESENTE.search(d) else "CITADA")
            if not any(p["NOME"] == nome and p["ESTADO"] == estado for p in s["PROBLEMAS"]):
                s["PROBLEMAS"].append({"NOME": nome, "ESTADO": estado,
                                       "TRECHO": _trecho(linha, m.start(), m.end())})
        for m in _RE_FASE.finditer(d):
            nome = re.sub(r"\s+", " ", m.group(0))
            if not any(f["NOME"] == nome for f in s["FASES"]):
                s["FASES"].append({"NOME": nome, "TRECHO": _trecho(linha, m.start(), m.end())})
    secoes = [s for s in secoes if s["CULTURA"] or s["PROBLEMAS"] or s["FASES"]]

    def _unicos(chave, campo):
        vistos = []
        for s in secoes:
            for x in s[chave]:
                if x[campo] not in vistos:
                    vistos.append(x[campo])
        return vistos
    return {"SECOES": secoes,
            "CULTURAS": [s["CULTURA"] for s in secoes if s["CULTURA"]],
            "PROBLEMAS": _unicos("PROBLEMAS", "NOME"),
            "PROBLEMAS_NAO_AUSENTES": sorted({p["NOME"] for s in secoes for p in s["PROBLEMAS"]
                                             if p["ESTADO"] != "AUSENTE"}),
            "FASES": _unicos("FASES", "NOME"),
            "LEI": ("praga «non presente» e AUSENTE, nunca ocorrencia; cada praga e fase fica na secao da "
                    "cultura onde esta escrita; texto antes da 1.a cultura nao herda cultura")}
