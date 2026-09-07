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


def texto(rel: str) -> str:
    p = RAIZ / rel
    try:
        return p.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""


def ferramentas() -> list:
    """Uma entrada por contrato de bloco, agrupada pelo dominio que ele declara."""
    por_dominio: dict[str, dict] = {}
    d = RAIZ / BLOCOS
    if not d.is_dir():
        return []

    for p in sorted(d.glob("*.spec.json")):
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

        alvo = por_dominio.setdefault(dominio, {
            "dominio": dominio,
            "blocos": [],
            "o_que_alimenta": real,
            "resumo": resumo,
            "confianca": e.get("confidence", ""),
            "camadas": {},
            "registos": [],
            "riscos": e.get("risks") if isinstance(e.get("risks"), list) else [],
            "perguntas_abertas": (e.get("openQuestions")
                                  if isinstance(e.get("openQuestions"), list) else []),
            "ficheiros": [],
            "confissoes": [],
        })
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

    for f in por_dominio.values():
        tipos = {c["tipo"] for c in f["camadas"].values()}
        if f["confissoes"]:
            tipos.add("FIXTURE")
        # A leitura que interessa: esta ferramenta esta a mostrar dado REAL, ou
        # esta a ilustrar? Misturar sem dizer qual e qual e o pior dos tres casos,
        # porque parece medicao.
        if not tipos:
            f["de_onde_vem"] = "NAO SEI"
            f["leitura"] = ("Nao da para dizer de onde vem o que esta na tela: o "
                            "contrato deste bloco nao nomeia camada nenhuma.")
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

    return sorted(por_dominio.values(), key=lambda x: x["dominio"])


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
        print(f"    {f['de_onde_vem']:11s} {f['dominio'][:62]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
