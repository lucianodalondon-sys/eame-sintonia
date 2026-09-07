#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SINTONIA SYSTEM MAP · SCANNER DO CASCO

    CADA FERRAMENTA DA TELA TEM DE DIZER O QUE ESTA LIGADO NELA HOJE.

O portal tem onze ferramentas — Radar das Oportunidades, Portfolio, Radar Futuro,
Janelas de Cultura, Pulso de Mercado, Vozes do Campo, Concorrencia, Ciencia,
Arquivo, Registo de Fontes, Rede Comercial. Quem as abre ve numeros. O que quase
ninguem consegue ver e DE ONDE VEM CADA NUMERO.

E a diferenca e enorme. Este repositorio ja tem a resposta escrita, e ela e
brutalmente honesta — do contrato do Radar das Oportunidades:

    «Today the Opportunity Radar is 100% legacy fixture (...) Facts on that
     screen come from three different places and only one is real (...) The real
     backing is 3 records in ITALY_INGEST.OPPORTUNITIES.»

Dezassete oportunidades na tela. Tres reais por baixo.

    UM NUMERO NA TELA SEM PROCEDENCIA E UM PALPITE BEM VESTIDO.

Este ficheiro le os contratos de bloco (`italia-portale/audit/blocks/*.spec.json`)
e devolve, por ferramenta: o que ela e, o que a alimenta de verdade, quantos
registos, e de que camada vem cada um.

AS TRES CAMADAS, E PORQUE IMPORTAM
-----------------------------------
    ITALY_INGEST      REAL      veio do motor, com procedencia
    ITALY_CANONICAL   CANONICO  a lei aplicada sobre o real
    ITALY_DEMO        FIXTURE   escrito a mao para a tela nao ficar vazia

Uma tela que mistura as tres sem dizer qual e qual nao esta a informar: esta a
ilustrar. E ilustracao com numero em cima e a forma mais cara de enganar alguem,
porque parece medicao.

SAIDA: system-map/data/casco.generated.json
"""

import json
import re
import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
SAIDA = RAIZ / "system-map" / "data" / "casco.generated.json"
BLOCOS = "italia-portale/audit/blocks"
CLIENTE = "italia-portale/client"

# As camadas de dado que o casco carrega, e o que cada uma significa.
CAMADAS = {
    "ITALY_INGEST": ("REAL", "veio do motor, com procedencia"),
    "ITALY_CANONICAL": ("CANONICO", "a lei aplicada sobre o real"),
    "ITALY_LABEL_VERDICTS": ("CANONICO", "veredito de rotulo, medido"),
    "ITALY_REAL_INTELLIGENCE": ("REAL", "inteligencia derivada do real"),
    "ITALY_MARKET_PULSE": ("REAL", "observacoes de mercado"),
    "ITALY_SCIENCE_BUSINESS": ("REAL", "ciencia ligada ao negocio"),
    "ITALY_CATALOG": ("REAL", "catalogo de produto"),
    "ITALY_BRIEFS": ("CANONICO", "briefings montados"),
    "MEETING_INTELLIGENCE": ("CANONICO", "camada da reuniao"),
    "ITALY_DEMO": ("FIXTURE", "escrito a mao para a tela nao ficar vazia"),
}

RE_REGISTOS = re.compile(r"(\d[\d.,]*)\s*(?:records?|registos?)", re.I)

# O FICHEIRO DE FIXTURE tem nome, e o contrato cita-o pelo nome — nao pela camada.
# Sem isto, o Radar das Oportunidades saia classificado como REAL, quando o seu
# proprio contrato abre com «Today the Opportunity Radar is 100% legacy fixture».
# Contar so os nomes de camada e ler metade da frase.
RE_FIXTURE_FICHEIRO = re.compile(r"italy-demo-data\.js|ITALY_DEMO", re.I)

# E o contrato as vezes diz, com todas as letras, que aquilo nao e real. Quando
# diz, e ELE que manda — nao a minha contagem de nomes.
CONFISSOES = (
    (re.compile(r"100%\s+legacy\s+fixture", re.I), "o contrato diz: 100% legacy fixture"),
    (re.compile(r"hand-authored|authored (?:or generated )?inside", re.I),
     "o contrato diz: escrito a mao"),
    (re.compile(r"seeded PRNG|is literally built from", re.I),
     "o contrato diz: gerado por sorteio, nao medido"),
    (re.compile(r"only one is real", re.I), "o contrato diz: so uma parte e real"),
)
RE_GLOBAL = re.compile(r"\b(ITALY_[A-Z_]+|MEETING_[A-Z_]+)\b")


# ── QUEM DECIDE QUAIS SAO AS FERRAMENTAS ────────────────────────────────────
# Nao sou eu, e nao e o nome do contrato. E o MENU DO PORTAL. A primeira versao
# deste ficheiro montava um cartao por «dominio» de contrato e saiam nomes que
# ninguem reconhece — «NAV COUNTERS + DATA STATE / PROVENANCE PANEL», «Helper
# relationships, visual tokens». Isso nao e uma ferramenta: e uma gaveta do
# codigo. Quem abre o portal ve «Radar delle Opportunita», e e esse o nome que
# tem de estar no cartao.
PORTALE = "italia-portale/client/portale.html"
I18N = "italia-portale/client/italy-i18n.js"

# a linha do menu: ['radar', T.navRadar, navN('cases')]
RE_MENU = re.compile(
    r"\[\s*'(\w+)'\s*,\s*(?:T\.(\w+)|mtL\(\s*'(\w+)'\s*\))\s*,")
RE_ROTULO = re.compile(r"^\s*(nav[A-Za-z]+)\s*:\s*'((?:[^'\\]|\\.)*)'", re.M)

# O rotulo do «Radar delle Opportunita» nao vive no i18n normal, vive na tabela
# da reuniao, e la cada chave e um par [italiano, ingles].
ROTULOS_REUNIAO = "italia-portale/client/meeting-labels.js"
RE_ROTULO_PAR = re.compile(
    r"^\s*(nav[A-Za-z]+)\s*:\s*\[\s*'((?:[^'\\]|\\.)*)'", re.M)

# ── QUE CONTRATO DESCREVE QUE FERRAMENTA ────────────────────────────────────
# Isto tambem nao e palpite meu: o portal ja tem a tabela feita, em
# `CAPABILITY_OF`, que diz a que ferramenta pertence cada tela. A ficha do
# produto pertence ao Portafoglio, a ficha do caso pertence ao Radar. Leio essa
# tabela em vez de a reescrever — reescrever seria criar uma segunda verdade.
RE_CAPACIDADE = re.compile(r"static\s+CAPABILITY_OF\s*=\s*\{([^}]*)\}")
RE_PAR = re.compile(r"(\w+)\s*:\s*'(\w*)'")

# A rota 'radar' e a rota 'meeting' desenham a MESMA tela — o proprio portal
# diz isso numa linha (`isMeeting: s.view === 'meeting' || s.view === 'radar'`),
# e so 'meeting' aparece no menu. Sem esta ponte, o contrato do Radar ficava
# orfao. E a unica ponte que este ficheiro faz, e tem linha que a prova.
CAPACIDADE_DOBRADA = {"radar": "meeting"}

# Tres contratos tem nome de ficheiro que nao e nome de tela. Isto SIM e leitura
# minha, nao medicao — fica aqui em cima, curta, para se poder discordar:
#     calendar   -> windows      o calendario e a mesma tela das Finestre
#     competitor -> competitors  singular no ficheiro, plural na tela
#     voci       -> voices       o ficheiro esta em italiano, a tela em ingles
LEITURA_MINHA = {"calendar": "windows", "competitor": "competitors",
                 "voci": "voices"}

# E quatro contratos nao sao ferramenta nenhuma — sao o casco a volta: o
# cabecalho, o menu, os ajudantes e a busca do topo. Nao ganham cartao.
NAO_E_FERRAMENTA = {"head", "helpers", "nav", "search"}


def capacidade_das_telas() -> dict:
    """A tabela do portal: cada tela pertence a que ferramenta. Medida."""
    m = RE_CAPACIDADE.search(texto(PORTALE))
    if not m:
        return {}
    fora = {}
    for tela, cap in RE_PAR.findall(m.group(1)):
        if cap:
            fora[tela] = CAPACIDADE_DOBRADA.get(cap, cap)
    return fora


def o_menu() -> list:
    """As ferramentas, na ordem e com o nome que o portal mostra. Medido.

    O ficheiro de rotulos traz o italiano PRIMEIRO e o ingles depois. Quem abre
    o portal ve o italiano, e e esse que vai para o cartao — por isso guardo a
    primeira vez que cada chave aparece, nunca a ultima.
    """
    linhas = texto(PORTALE).splitlines()
    rotulos: dict[str, str] = {}
    for chave, valor in (RE_ROTULO.findall(texto(I18N))
                         + RE_ROTULO_PAR.findall(texto(ROTULOS_REUNIAO))):
        rotulos.setdefault(chave, valor)

    fora, vistos = [], set()
    for i, l in enumerate(linhas, 1):
        m = RE_MENU.search(l)
        if not m:
            continue
        vista, chave = m.group(1), (m.group(2) or m.group(3) or "")
        if not chave.startswith("nav") or vista in vistos:
            continue
        vistos.add(vista)
        fora.append({
            "vista": vista,
            "nome": rotulos.get(chave, chave),
            "chave_do_rotulo": chave,
            "prova_do_nome": {"file": PORTALE, "line": i, "snippet": l.strip()[:150]},
        })
    return fora


def texto(rel: str) -> str:
    p = RAIZ / rel
    try:
        return p.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""


def ferramentas() -> list:
    """UMA ENTRADA POR FERRAMENTA DO MENU — com o nome que o portal mostra.

    A versao anterior agrupava por «dominio» do contrato e saiam cartoes chamados
    «NAV COUNTERS + DATA STATE / PROVENANCE PANEL». Isso e o nome de uma gaveta do
    codigo, nao de uma ferramenta: ninguem abre o portal e ve isso escrito.

    Agora e ao contrario. Primeiro pergunta-se ao MENU quais sao as ferramentas —
    sao onze, e chamam-se «Radar delle Opportunita», «Portafoglio», «Archivio».
    Depois cada contrato de bloco vai para a ferramenta a que pertence, usando a
    tabela que o proprio portal ja mantem. Uma ferramenta pode ter varios
    contratos (o Radar tem dois: o caso e o brief) e pode nao ter nenhum — e
    quando nao tem, o cartao diz NAO SEI, que e a resposta honesta.
    """
    menu = o_menu()
    if not menu:
        return []
    capacidade = capacidade_das_telas()
    por_ferramenta = {f["vista"]: dict(f, blocos=[], o_que_alimenta="", resumo="",
                                       confianca="", camadas={}, registos=[],
                                       riscos=[], perguntas_abertas=[],
                                       ficheiros=[], confissoes=[])
                      for f in menu}

    d = RAIZ / BLOCOS
    if not d.is_dir():
        return list(por_ferramenta.values())

    for p in sorted(d.glob("*.spec.json")):
        raiz_do_nome = p.name.replace(".spec.json", "")
        if raiz_do_nome in NAO_E_FERRAMENTA:
            continue
        tela = LEITURA_MINHA.get(raiz_do_nome, raiz_do_nome)
        vista = capacidade.get(tela)
        if vista not in por_ferramenta:
            continue
        try:
            bruto = json.loads(p.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue
        e = (bruto[0] if isinstance(bruto, list) and bruto else bruto) or {}
        if not isinstance(e, dict):
            continue
        dominio = str(e.get("domain") or p.stem).strip()
        real = str(e.get("realSource") or "")
        resumo = str(e.get("summary") or "")

        # de que camadas ela bebe, e quantos registos de cada
        camadas: dict[str, dict] = {}
        junto = real + " " + resumo
        # ONDE, EXATAMENTE, o contrato nomeia cada camada. Uma seta no mapa sem
        # ficheiro e linha por baixo e um desenho bonito, nao uma medicao.
        linhas = p.read_text(encoding="utf-8", errors="replace").splitlines()

        def onde(agulha: str) -> dict:
            for i, l in enumerate(linhas, 1):
                if agulha.lower() in l.lower():
                    return {"file": f"{BLOCOS}/{p.name}", "line": i,
                            "snippet": l.strip()[:150]}
            return {"file": f"{BLOCOS}/{p.name}", "line": 1, "snippet": agulha}
        if RE_FIXTURE_FICHEIRO.search(junto):
            camadas["italy-demo-data.js"] = {
                "tipo": "FIXTURE",
                "o_que_e": "escrito a mao para a tela nao ficar vazia",
                "prova": onde("italy-demo")}
        for g in sorted(set(RE_GLOBAL.findall(junto))):
            tipo, o_que = CAMADAS.get(g, ("NAO SEI", "camada nao classificada"))
            camadas[g] = {"tipo": tipo, "o_que_e": o_que, "prova": onde(g)}

        alvo = por_ferramenta[vista]
        # Varios contratos podem cair na mesma ferramenta. Empilha-se tudo:
        # duas descricoes de duas partes da mesma tela continuam a ser a mesma
        # tela, e quem olha o cartao quer as duas.
        alvo["o_que_alimenta"] = ((alvo["o_que_alimenta"] + " · " + real).strip(" ·")
                                  if real else alvo["o_que_alimenta"])
        alvo["resumo"] = ((alvo["resumo"] + " · " + resumo).strip(" ·")
                          if resumo else alvo["resumo"])
        alvo["confianca"] = alvo["confianca"] or e.get("confidence", "")
        alvo["dominios_do_contrato"] = sorted(
            set(alvo.get("dominios_do_contrato", []) + ([dominio] if dominio else [])))
        for campo, chave in (("riscos", "risks"),
                             ("perguntas_abertas", "openQuestions")):
            v = e.get(chave)
            if isinstance(v, list):
                alvo[campo] += v
        for rx, frase in CONFISSOES:
            if rx.search(junto) and frase not in alvo["confissoes"]:
                alvo["confissoes"].append(frase)
        alvo["blocos"].append(p.stem.replace(".spec", ""))
        alvo["ficheiros"].append(f"{BLOCOS}/{p.name}")
        alvo["camadas"].update(camadas)
        for n in RE_REGISTOS.findall(real):
            try:
                alvo["registos"].append(int(n.replace(".", "").replace(",", "")))
            except ValueError:
                pass

    for f in por_ferramenta.values():
        tipos = {c["tipo"] for c in f["camadas"].values()}
        if f["confissoes"]:
            tipos.add("FIXTURE")
        # A leitura que interessa: esta ferramenta esta a mostrar dado REAL, ou
        # esta a ilustrar? Misturar sem dizer qual e qual e o pior dos tres casos,
        # porque parece medicao.
        if not tipos:
            f["de_onde_vem"] = "NAO SEI"
            f["leitura"] = (
                "Nao da para dizer de onde vem o que esta nesta tela. "
                + ("Esta ferramenta nao tem contrato de bloco nenhum escrito."
                   if not f["ficheiros"] else
                   "O contrato existe, mas nao nomeia camada de dado nenhuma."))
        elif tipos == {"FIXTURE"}:
            f["de_onde_vem"] = "SO FIXTURE"
            f["leitura"] = ("Tudo o que esta aqui foi escrito a mao para a tela nao "
                            "ficar vazia. Nao ha dado real por baixo.")
        elif "FIXTURE" in tipos:
            f["de_onde_vem"] = "MISTURA"
            f["leitura"] = ("Mistura dado real com dado escrito a mao. Quem olha nao "
                            "consegue dizer qual e qual — e a tela nao avisa.")
        else:
            f["de_onde_vem"] = "REAL"
            f["leitura"] = "Tudo o que esta aqui vem de dado com procedencia."
        f["registos_citados"] = sorted(set(f["registos"]), reverse=True)[:6]
        f.pop("registos", None)
        f["blocos"] = sorted(set(f["blocos"]))
        f["ficheiros"] = sorted(set(f["ficheiros"]))
        f["riscos"] = f["riscos"][:12]
        f["perguntas_abertas"] = f["perguntas_abertas"][:12]

    # A ordem e a do menu, nao a alfabetica: e assim que a pessoa as ve.
    return list(por_ferramenta.values())


def camadas_no_cliente() -> dict:
    """Que ficheiro do cliente publica cada camada — medido, nao suposto."""
    fora: dict[str, list] = {}
    d = RAIZ / CLIENTE
    if not d.is_dir():
        return {}
    for p in sorted(d.glob("*.js")):
        if "vendor" in str(p):
            continue
        t = p.read_text(encoding="utf-8", errors="replace")[:400000]
        for g in sorted(set(RE_GLOBAL.findall(t))):
            if re.search(rf"window\.{g}\s*=|const {g}\s*=|var {g}\s*=", t):
                fora.setdefault(g, []).append(f"{CLIENTE}/{p.name}")
    return dict(sorted(fora.items()))


def main() -> int:
    fs = ferramentas()
    if not fs:
        print("CASCO=VAZIO · nao encontrei contratos de bloco", file=sys.stderr)
        return 0

    publica = camadas_no_cliente()
    head = subprocess.run(["git", "-C", str(RAIZ), "rev-parse", "HEAD"],
                          capture_output=True, text=True).stdout.strip()

    conta: dict[str, int] = {}
    for f in fs:
        conta[f["de_onde_vem"]] = conta.get(f["de_onde_vem"], 0) + 1

    dados = {
        "SCHEMA": "sintonia.system-map.casco/1",
        "PROVENANCE": {"HEAD": head, "BLOCOS": BLOCOS, "CLIENTE": CLIENTE},
        "FERRAMENTAS": fs,
        "CAMADAS_PUBLICADAS": publica,
        "COUNTS": {
            "ferramentas": len(fs),
            "por_origem": dict(sorted(conta.items())),
            "camadas_publicadas": len(publica),
        },
    }
    SAIDA.write_text(json.dumps(dados, ensure_ascii=False, indent=2) + "\n",
                     encoding="utf-8")
    c = dados["COUNTS"]
    print(f"CASCO=OK · {c['ferramentas']} ferramentas · "
          + " · ".join(f"{k} {v}" for k, v in c["por_origem"].items())
          + f" · {c['camadas_publicadas']} camadas publicadas pelo cliente")
    for f in fs:
        print(f"    {f['de_onde_vem']:11s} {f['nome'][:40]:42s}"
              f"{len(f['blocos'])} contrato(s) · {len(f['camadas'])} camada(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
