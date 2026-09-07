#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
A PORTA DE ENTRADA DE FONTE NOVA

    O ACERVO DE FONTES E CAPITAL PARADO. CONSULTA-SE ANTES DE COLETAR.

E capital parado que precisa de porta: fonte nova aparece a toda a hora — no meio
de uma coleta, num rodape de PDF, numa conversa. Sem porta, ela morre no
histórico do terminal de quem a viu.

Mas porta nao e porta escancarada. Este repositorio tem uma lei antiga sobre isto,
escrita no proprio atlas:

    "Uma linha so existe aqui depois que alguem abriu a fonte, olhou o que ela
     entrega e guardou evidencia disso."

Entao a porta e uma FILA, nao o atlas. O que entra aqui e CANDIDATA. Vira fonte
quando alguem a abre e prova. E o mesmo principio do resto da casa: registar que
existe uma pista e barato e honesto; afirmar que ela e uma fonte, sem olhar, e
como dizer que se sabe uma coisa que nao se sabe.

A ESCADA — quatro degraus, e o mapa mostra quantas fontes estao em cada um
--------------------------------------------------------------------------
    1 · CANDIDATA   alguem viu que existe. Aqui, neste ficheiro.
                       ↓ alguem abre, olha, e guarda um exemplo real
    2 · REGISTADA   tem ficha no ATLAS-DE-FONTES-EAME.md · verdict GREEN
                       ↓ alguem escreve COMO se busca e o que fazer se quebrar
    3 · CONTRATADA  tem contrato em CONTRATOS-DAS-FONTES-EAME.md
                       ↓
    4 · AUTOMATICA  a maquina vai la sozinha, sem ninguem por perto

Subir degrau exige trabalho de gente. Este script so cuida do degrau 1 — e
recusa-se a fingir os outros tres.

COMO SE USA
-----------
A mao:

    py candidatas/fonte_nova.py \\
        --tipo BASE_OFICIAL --pais ES --nome "Registro de X" \\
        --url https://... --para-que "responder BQ3 em Espanha" \\
        --quem-viu luciano --onde-viu "rodape do PDF do MAPA"

De dentro de uma coleta que tropecou numa fonte nova:

    from fonte_nova import registar
    registar(tipo="ORGANIZACAO", pais="IT", nome="Consorzio X",
             url=..., para_que=..., quem_viu="instagram_coleta.py",
             onde_viu="bio da conta @...")

Duas vezes a mesma fonte nao cria duas linhas: a chave e o URL normalizado.
"""

import argparse
import json
import re
import sys
from datetime import date
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
FILA = RAIZ / "data" / "samples" / "FONTES-CANDIDATAS.json"

# Os tipos sao os que esta casa ja usa, nao uma taxonomia nova. Inventar uma
# gaveta nova para cada fonte que chega e como nao ter gaveta nenhuma.
TIPOS = {
    "BASE_OFICIAL": "Registro publico, dado aberto, base regulatoria ou estatistica.",
    "ORGANIZACAO": "Instituto, associacao, consorcio, universidade, cooperativa.",
    "CIENCIA": "Artigo, ensaio, repositorio bibliografico, congresso.",
    "INSTAGRAM": "Conta publica no Instagram.",
    "LINKEDIN": "Pagina publica no LinkedIn.",
    "YOUTUBE": "Canal publico no YouTube.",
    "FACEBOOK": "Pagina publica no Facebook.",
    "IMPRENSA": "Veiculo de imprensa, boletim, newsletter setorial.",
    "OUTRO": "Nao encaixa em nenhuma das anteriores. Explique em PARA_QUE.",
}
PAISES = {"EU", "FR", "ES", "IT", "PT", "DE", "PL", "OUTRO"}


def normalizar(url: str) -> str:
    """A chave da fila. Sem isto, a mesma fonte entra tres vezes com tres grafias."""
    u = (url or "").strip().lower()
    u = re.sub(r"^https?://", "", u)
    u = re.sub(r"^www\.", "", u)
    return u.rstrip("/")


def carregar() -> dict:
    if FILA.exists():
        return json.loads(FILA.read_text(encoding="utf-8"))
    return {
        "DATASET": "SINTONIA-FONTES-CANDIDATAS-V1",
        "LEI": ("Isto e uma FILA, nao o atlas. O que esta aqui e uma pista de que "
                "existe uma fonte. Vira fonte quando alguem a abrir, olhar o que ela "
                "entrega e guardar evidencia — e nesse momento ganha ficha no "
                "docs/fontes/ATLAS-DE-FONTES-EAME.md. Nada aqui e afirmado como fonte."),
        "ESTADOS": {
            "CANDIDATA": "alguem viu que existe. Ninguem abriu ainda.",
            "EM_ANALISE": "alguem esta a olhar agora.",
            "PROMOVIDA": "virou ficha no atlas. O campo SOURCE_ID diz qual.",
            "RECUSADA": "olhou-se e nao serve. O motivo fica escrito, e a linha fica.",
        },
        "CANDIDATAS": [],
    }


def registar(tipo: str, pais: str, nome: str, url: str, para_que: str,
             quem_viu: str, onde_viu: str = "", nota: str = "") -> dict:
    """Poe uma pista na fila. Devolve a linha criada (ou a que ja existia)."""
    if tipo not in TIPOS:
        raise ValueError(f"tipo desconhecido: {tipo}. Use um de: {', '.join(TIPOS)}")
    if pais not in PAISES:
        raise ValueError(f"pais desconhecido: {pais}. Use um de: {', '.join(sorted(PAISES))}")
    for campo, valor in (("nome", nome), ("url", url),
                         ("para_que", para_que), ("quem_viu", quem_viu)):
        if not (valor or "").strip():
            # PARA_QUE e obrigatorio de proposito. Fonte sem uso declarado vira
            # entulho: daqui a seis meses ninguem sabe por que ela foi anotada, e
            # a fila deixa de ser um acervo para ser uma gaveta de papeis soltos.
            raise ValueError(f"campo obrigatorio vazio: {campo}")

    d = carregar()
    chave = normalizar(url)
    for c in d["CANDIDATAS"]:
        if normalizar(c["URL"]) == chave:
            c.setdefault("VISTA_TAMBEM_POR", [])
            marca = {"quem": quem_viu, "onde": onde_viu, "quando": date.today().isoformat()}
            if marca not in c["VISTA_TAMBEM_POR"]:
                c["VISTA_TAMBEM_POR"].append(marca)
                gravar(d)
            return c

    linha = {
        "CANDIDATA_ID": f"CAND-{len(d['CANDIDATAS']) + 1:04d}",
        "TIPO": tipo, "TIPO_SIGNIFICA": TIPOS[tipo],
        "PAIS": pais, "NOME": nome.strip(), "URL": url.strip(),
        "PARA_QUE_SERVE": para_que.strip(),
        "QUEM_VIU": quem_viu.strip(), "ONDE_VIU": onde_viu.strip(),
        "QUANDO": date.today().isoformat(),
        "NOTA": nota.strip(),
        "ESTADO": "CANDIDATA",
        "SOURCE_ID": None,          # preenchido so quando virar ficha no atlas
        "MOTIVO_DA_RECUSA": None,
    }
    d["CANDIDATAS"].append(linha)
    gravar(d)
    return linha


def gravar(d: dict) -> None:
    FILA.parent.mkdir(parents=True, exist_ok=True)
    d["CANDIDATAS"].sort(key=lambda c: (c["TIPO"], c["PAIS"], c["NOME"]))
    d["TOTAL"] = len(d["CANDIDATAS"])
    FILA.write_text(json.dumps(d, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def listar() -> int:
    d = carregar()
    if not d["CANDIDATAS"]:
        print("FILA=VAZIA · nenhuma fonte candidata registada")
        return 0
    por_tipo: dict[str, list] = {}
    for c in d["CANDIDATAS"]:
        por_tipo.setdefault(c["TIPO"], []).append(c)
    for tipo in sorted(por_tipo):
        linhas = por_tipo[tipo]
        print(f"\n{tipo} · {len(linhas)}  — {TIPOS.get(tipo, '')}")
        for c in linhas:
            print(f"  [{c['ESTADO']:10s}] {c['CANDIDATA_ID']} {c['PAIS']} · {c['NOME'][:52]}")
            print(f"               para que: {c['PARA_QUE_SERVE'][:80]}")
    print(f"\nTOTAL={len(d['CANDIDATAS'])} · "
          + " · ".join(f"{e}={sum(1 for c in d['CANDIDATAS'] if c['ESTADO'] == e)}"
                       for e in ("CANDIDATA", "EM_ANALISE", "PROMOVIDA", "RECUSADA")))
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Regista uma fonte candidata na fila de entrada.",
        epilog="Isto NAO cria fonte. Cria pista. Fonte nasce no atlas, com evidencia.")
    ap.add_argument("--listar", action="store_true", help="mostra a fila por tipo")
    ap.add_argument("--tipos", action="store_true", help="mostra os tipos aceites")
    ap.add_argument("--tipo"), ap.add_argument("--pais"), ap.add_argument("--nome")
    ap.add_argument("--url"), ap.add_argument("--para-que", dest="para_que")
    ap.add_argument("--quem-viu", dest="quem_viu")
    ap.add_argument("--onde-viu", dest="onde_viu", default="")
    ap.add_argument("--nota", default="")
    a = ap.parse_args()

    if a.tipos:
        for t, o_que in TIPOS.items():
            print(f"  {t:14s} {o_que}")
        return 0
    if a.listar or not a.tipo:
        return listar()

    try:
        linha = registar(a.tipo, a.pais, a.nome, a.url, a.para_que,
                         a.quem_viu, a.onde_viu, a.nota)
    except ValueError as e:
        print(f"RECUSADO: {e}", file=sys.stderr)
        return 1
    print(f"NA_FILA={linha['CANDIDATA_ID']} · {linha['TIPO']} · {linha['NOME']}")
    print(f"  estado: {linha['ESTADO']} — ninguem abriu esta fonte ainda.")
    print(f"  proximo degrau: abrir, olhar o que entrega, guardar um exemplo real,")
    print(f"                  e escrever a ficha em docs/fontes/ATLAS-DE-FONTES-EAME.md")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
