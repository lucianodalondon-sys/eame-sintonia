#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MEDE A MAQUINA — e recusa toda afirmacao que nao se confirme no repositorio.

    python3 system-map/v2/scripts/scan_machine.py

    le      : system-map/v2/model/machine.model.json   (declarado por gente)
    escreve : system-map/v2/data/machine.measured.json (medido, nunca escrito a mao)

O QUE ESTE FICHEIRO FAZ, E O QUE ELE RECUSA FAZER
--------------------------------------------------
Ele NAO decide o que a maquina e. Isso esta nas autoridades — AGENTS.md, os
contratos, o censo da coleta — e o modelo aponta para elas. O que ele faz e
conferir, uma por uma, se as afirmacoes do modelo sobrevivem ao repositorio:

    a autoridade citada existe, e a frase citada esta mesmo la?
    os ficheiros declarados existem?
    o artefato que provaria a execucao existe?
    a linha de codigo que prova a ligacao existe, e em que linha?

Cada resposta e um FACTO com um sitio onde se conferir. Onde a resposta e nao,
o conceito nao e promovido: fica a dizer o que lhe falta.

    AUSENCIA DE PROVA NAO E PROVA DE AUSENCIA — E TAMBEM NAO E PROVA DE PRESENCA.

POR QUE A COMPARACAO IGNORA ACENTO E ASTERISCO
-----------------------------------------------
As autoridades sao prosa em portugues, escritas com acento e com marcacao de
markdown. Uma ancora citada como «capital parado» nao encontraria
«**capital parado**», e o modelo cairia em UNKNOWN por causa de dois asteriscos
— um falso negativo e um falso negativo aqui custa caro: ensina a desconfiar do
portao em vez de desconfiar do facto.

Por isso a comparacao normaliza acento, marcacao e espaco. Ela continua a exigir
a FRASE: nao ha comparacao por palavra solta nem por semelhanca.

O VEICULO NAO SE ESCREVE A MAO
-------------------------------
Os canais — YouTube, Instagram, LinkedIn, Facebook, HTTP — nascem de procurar o
canal dentro do codigo das acoes, e cada um carrega o ficheiro e a linha onde
aparece. Canal que ninguem chama fica em NAO SEI, e e a verdade.
"""

from __future__ import annotations

import fnmatch
import json
import re
import subprocess
import sys
import unicodedata
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[3]
MODELO = RAIZ / "system-map" / "v2" / "model" / "machine.model.json"
SAIDA = RAIZ / "system-map" / "v2" / "data" / "machine.measured.json"

# Os canais que a casa conhece. A lista e curta e vem da lei: o veiculo responde
# «de ONDE o dado vem». Cada um traz os nomes por que pode aparecer no codigo.
CANAIS = [
    ("V-YOUTUBE",   "YOUTUBE",            ("youtube", "yt-dlp", "youtu.be")),
    ("V-INSTAGRAM", "INSTAGRAM",          ("instagram",)),
    ("V-LINKEDIN",  "LINKEDIN",           ("linkedin",)),
    ("V-FACEBOOK",  "FACEBOOK",           ("facebook", "meta ads")),
    ("V-HTTP",      "PEDIDO HTTP DIRETO", ("urllib.request", "requests.get", "fetch(")),
]
# Onde se procura um canal: nas ACOES da coleta. Procurar na casa toda acharia o
# nome do canal num documento e faria um veiculo nascer de prosa.
ONDE_HA_CANAL = ("coleta/",)


def git(*args: str) -> str:
    return subprocess.run(["git", "-C", str(RAIZ), *args],
                          capture_output=True, text=True,
                          encoding="utf-8", errors="replace").stdout.rstrip("\n")


def norm(s: str) -> str:
    """Acento, marcacao e espaco fora. A frase continua a ser exigida."""
    s = unicodedata.normalize("NFKD", s)
    s = "".join(c for c in s if not unicodedata.combining(c))
    s = re.sub(r"[*_`>#|]", "", s)
    return re.sub(r"\s+", " ", s).strip().lower()


def ler(p: Path) -> str:
    try:
        return p.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""


class Medidor:
    def __init__(self) -> None:
        self.tracked = [f for f in git("ls-files").splitlines() if f]
        self.set_tracked = set(self.tracked)
        self._cache: dict[str, str] = {}

    def texto(self, rel: str) -> str:
        if rel not in self._cache:
            self._cache[rel] = ler(RAIZ / rel)
        return self._cache[rel]

    # ── a autoridade ────────────────────────────────────────────────────────
    def ancora(self, ref: dict | None) -> dict:
        """A autoridade existe, e a frase citada esta mesmo la?"""
        if not ref:
            return {"estado": "SEM_AUTORIDADE", "file": None, "anchor": None}
        f, a = ref.get("file"), ref.get("anchor", "")
        if f not in self.set_tracked and not (RAIZ / f).is_file():
            return {"estado": "FICHEIRO_AUSENTE", "file": f, "anchor": a}
        if norm(a) and norm(a) in norm(self.texto(f)):
            return {"estado": "CONFIRMADA", "file": f, "anchor": a}
        return {"estado": "FRASE_NAO_ENCONTRADA", "file": f, "anchor": a}

    # ── os ficheiros ────────────────────────────────────────────────────────
    def ficheiros(self, padroes: list[str], excluir: list[str] | None = None
                  ) -> tuple[list[str], list[str]]:
        """Devolve (encontrados, padroes que nao acharam nada).

        `excluir` existe porque UM FICHEIRO TEM UM DONO. Uma peca que apanha uma
        gaveta inteira (`italia-portale/audit/**`) atropela a peca vizinha que
        reivindica um ficheiro nomeado la dentro — e dois donos para a mesma linha
        e a avaria que este mapa existe para nao ter. A excecao escreve-se, a vista,
        em vez de se resolver por ordem de leitura.
        """
        achados: set[str] = set()
        vazios: list[str] = []
        for p in padroes or []:
            if p.endswith("/**"):
                base = p[:-3].rstrip("/") + "/"
                hit = [f for f in self.tracked if f.startswith(base)]
            elif "*" in p or "?" in p:
                hit = [f for f in self.tracked if fnmatch.fnmatch(f, p)]
            else:
                hit = [f for f in self.tracked if f == p or f.startswith(p.rstrip("/") + "/")]
            if hit:
                achados.update(hit)
            else:
                vazios.append(p)
        for x in excluir or []:
            if x.endswith("/**"):
                base = x[:-3].rstrip("/") + "/"
                achados -= {f for f in achados if f.startswith(base)}
            elif "*" in x or "?" in x:
                achados -= {f for f in achados if fnmatch.fnmatch(f, x)}
            else:
                achados.discard(x)
        return sorted(achados), vazios

    # ── o artefato que prova a execucao ─────────────────────────────────────
    def artefato(self, rel: str) -> dict:
        p = RAIZ / rel
        if p.is_dir():
            n = sum(1 for _ in p.rglob("*") if _.is_file())
            return {"existe": True, "tipo": "pasta", "itens": n, "path": rel}
        if p.is_file():
            return {"existe": True, "tipo": "ficheiro", "bytes": p.stat().st_size, "path": rel}
        return {"existe": False, "tipo": None, "path": rel}

    # ── o impedimento: um caminho que a maquina EXIGE e que nao existe ──────
    def impedimento(self, imp: dict) -> dict:
        """BLOQUEADO nao se declara: mede-se.

        Um workflow que confere `scripts/x.py` antes de correr, numa arvore onde
        essa pasta ja foi dissolvida, para no primeiro passo. Isso nao e opiniao
        sobre a peca — e um ficheiro que se procura e nao esta la, e qualquer
        pessoa pode conferir com um `ls`.
        """
        faltam = [c for c in imp.get("caminhos", [])
                  if not (RAIZ / c).exists()]
        return {"tipo": imp.get("tipo"), "exigido_por": imp.get("exigido_por"),
                "porque": imp.get("porque"),
                "caminhos": imp.get("caminhos", []), "ausentes": faltam,
                "bloqueia": bool(faltam)}

    # ── a linha de codigo que prova a ligacao ───────────────────────────────
    def linha(self, ref: dict | None) -> dict:
        if not ref:
            return {"estado": "NAO_DECLARADA", "file": None}
        f, needle = ref.get("file"), ref.get("contem", "")
        if not (RAIZ / f).is_file():
            return {"estado": "FICHEIRO_AUSENTE", "file": f, "contem": needle}
        for i, linha in enumerate(self.texto(f).splitlines(), 1):
            if needle in linha:
                return {"estado": "ENCONTRADA", "file": f, "line": i,
                        "snippet": linha.strip()[:160], "contem": needle}
        return {"estado": "NAO_ENCONTRADA", "file": f, "contem": needle}

    # ── os canais, medidos e nao escritos ───────────────────────────────────
    def canais(self) -> list[dict]:
        alvos = [f for f in self.tracked
                 if f.startswith(ONDE_HA_CANAL) and f.endswith((".py", ".mjs", ".js", ".sh"))]
        out = []
        for cid, nome, termos in CANAIS:
            provas = []
            for f in alvos:
                baixo = self.texto(f).lower()
                for t in termos:
                    pos = baixo.find(t)
                    if pos < 0:
                        continue
                    n = baixo.count("\n", 0, pos) + 1
                    provas.append({"file": f, "line": n, "termo": t})
                    break
            out.append({"id": cid, "nome": nome, "termos": list(termos),
                        "provas": provas[:12], "total_provas": len(provas)})
        return out


def main() -> int:
    if not MODELO.is_file():
        print(f"modelo ausente: {MODELO}", file=sys.stderr)
        return 2
    modelo = json.loads(MODELO.read_text(encoding="utf-8"))
    m = Medidor()

    conceitos = []
    for c in modelo["CONCEITOS"]:
        achados, vazios = m.ficheiros(c.get("implementa", []), c.get("excluir"))
        conceitos.append({
            "id": c["id"],
            "autoridade": m.ancora(c.get("authority")),
            "ficheiros": achados,
            "padroes_vazios": vazios,
            "observacoes": [
                {**m.artefato(o["artefato"]), "prova": o["prova"]}
                for o in c.get("observado_por", [])
            ],
            "impedimentos": [m.impedimento(i) for i in c.get("impedimentos", [])],
        })

    ligacoes = []
    for e in modelo["LIGACOES"]:
        ligacoes.append({
            "de": e["de"], "para": e["para"],
            "declarada": m.ancora(e.get("declarada")),
            "implementada": m.linha(e.get("implementada")),
            "observada": ({**m.artefato(e["observada"]["artefato"]),
                           "prova": e["observada"]["prova"]}
                          if e.get("observada") else {"existe": False, "path": None}),
        })

    departamentos = [{"id": d["id"], "autoridade": m.ancora(d.get("authority"))}
                     for d in modelo["DEPARTAMENTOS"]]

    saida = {
        "SCHEMA": "sintonia.system-map-v2.measured/1",
        "PROVENANCE": {
            "REPO": "lucianodalondon-sys/eame-sintonia",
            "BRANCH": git("rev-parse", "--abbrev-ref", "HEAD"),
            "HEAD": git("rev-parse", "HEAD"),
            # A data e a do COMMIT, nunca a do relogio: um relogio dentro do
            # artefato faz o CI acusar drift a cada minuto.
            "GENERATED_AT": git("log", "-1", "--format=%cI"),
        },
        "FILES_TRACKED": len(m.tracked),
        "DEPARTAMENTOS": departamentos,
        "CONCEITOS": conceitos,
        "LIGACOES": ligacoes,
        "CANAIS": m.canais(),
    }
    SAIDA.parent.mkdir(parents=True, exist_ok=True)
    SAIDA.write_text(json.dumps(saida, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"medido: {len(conceitos)} conceitos, {len(ligacoes)} ligacoes, "
          f"{len(m.tracked)} ficheiros seguidos pelo git")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
