#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MEDE A MÁQUINA — as quatro verdades da COL-LAW-102, uma a uma.

    python3 system-map/v2/scripts/medir_maquina.py

    lê     : system-map/v2/model/maquina.model.json   (declarado por gente)
    escreve: system-map/v2/data/maquina.medida.json   (medido, nunca escrito à mão)

AS QUATRO VERDADES, E POR QUE NÃO SE FUNDEM (COL-LAW-102)
----------------------------------------------------------
    BIBLE     a Bíblia exige que exista           → docs/biblia/leis.json
    DECLARED  o contrato diz que pode existir     → a frase citada está lá?
    CODE      há implementação que permite        → os ficheiros existem?
    OBSERVED  uma execução real provou            → a medição diz o quê?

Um verde único por cima esconderia três factos diferentes. Um conceito que a
Bíblia exige e o repositório não implementa continua a aparecer — é essa a razão
de existir da dimensão BIBLE.

ARTEFATO QUE EXISTE NÃO É ARTEFATO QUE PROVA
---------------------------------------------
Esta é a lição mais cara da tentativa anterior. Ela marcou uma aresta como
OBSERVED porque o ficheiro de evidência existia — e o ficheiro era a ENTRADA do
motor, não a saída. O ficheiro existia; não provava nada sobre aquela aresta.

Por isso aqui a observação não aponta para um ficheiro: aponta para um CAMINHO
DENTRO do ficheiro e diz o valor que espera.

    artefato  system-map/data/pedido.observado.json
    caminho   ESTRADA.RAW.OBSERVED
    espera    true

Se o caminho não existir, o valor não bater, ou o ficheiro não abrir, o conceito
NÃO é observado — e o motivo fica escrito. Nenhuma promoção por proximidade.

ARTEFATO GERADO PELO MAPA NÃO É AUTORIDADE (COL-LAW-047)
---------------------------------------------------------
Um ficheiro que o próprio sistema do mapa produz pode provar «o scanner viu
isto». Nunca pode provar «isto é a arquitetura». O medidor marca cada autoridade
que caia nesse caso, e o validador reprova.
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
V2 = RAIZ / "system-map" / "v2"
MODELO = V2 / "model" / "maquina.model.json"
LEIS = RAIZ / "docs" / "biblia" / "leis.json"
SAIDA = V2 / "data" / "maquina.medida.json"

# Ficheiros que o PRÓPRIO sistema do mapa produz. Servem de medição; nunca de
# autoridade. A lista é de prefixos porque é assim que eles nascem.
GERADO_PELO_MAPA = (
    "system-map/data/",
    "system-map/v2/data/",
    "italia-portale/client/system-map/",
    "regras/LEIA-ANTES-DE-COLETAR.md",
    "docs/fontes/INDICE-DE-FONTES.md",
)


def gerado_pelo_mapa(rel: str) -> bool:
    return bool(rel) and rel.startswith(GERADO_PELO_MAPA)


def _espec(padrao: str) -> tuple:
    """Quao especifico e um padrao. Gaveta inteira perde para ficheiro nomeado."""
    gaveta = padrao.endswith("/**")
    curinga = padrao.count("*") + padrao.count("?")
    concreto = len(padrao.replace("*", "").replace("?", ""))
    return (0 if gaveta else 1, 0 if curinga else 1, concreto)


def git(*args: str) -> str:
    return subprocess.run(["git", "-C", str(RAIZ), *args], capture_output=True,
                          text=True, encoding="utf-8", errors="replace").stdout.rstrip("\n")


def norm(s: str) -> str:
    """Acento, marcação e espaço fora. A FRASE continua a ser exigida."""
    s = unicodedata.normalize("NFKD", s)
    s = "".join(c for c in s if not unicodedata.combining(c))
    s = re.sub(r"[*_`>#|·]", "", s)
    return re.sub(r"\s+", " ", s).strip().lower()


RE_ESCOLHA = re.compile(r"^([^\[]+)\[([^=\]]+)=([^\]]*)\]$")


def caminho_em(obj, caminho: str):
    """Segue `A.B.C` dentro de um JSON. Devolve (achou, valor).

    Um passo tambem pode escolher um elemento de uma LISTA pelo valor de um
    campo: `FERRAMENTAS[vista=windows].de_onde_vem`. Sem isto, uma observacao
    sobre UMA ferramenta teria de apontar para a lista inteira — e a lista
    inteira nao prova nada sobre a ferramenta que o cartao mostra. Escolher
    por posicao (`[3]`) seria pior: a posicao muda quando o portal muda, e a
    prova passaria a apontar para outra tela sem ninguem dar por isso.
    """
    cur = obj
    for parte in caminho.split("."):
        m = RE_ESCOLHA.match(parte)
        if m:
            lista, campo, valor = m.group(1), m.group(2), m.group(3)
            if not isinstance(cur, dict) or lista not in cur:
                return False, None
            seq = cur[lista]
            if not isinstance(seq, list):
                return False, None
            achado = [x for x in seq
                      if isinstance(x, dict) and str(x.get(campo)) == valor]
            if len(achado) != 1:
                # zero nao existe; mais do que um nao distingue. Nos dois casos
                # a prova nao aponta para nada em concreto.
                return False, None
            cur = achado[0]
            continue
        if isinstance(cur, dict) and parte in cur:
            cur = cur[parte]
        else:
            return False, None
    return True, cur


def bate(valor, espera) -> bool:
    """O valor medido satisfaz o que a declaração espera?"""
    if isinstance(espera, bool):
        return valor is espera
    if isinstance(espera, str):
        if espera.startswith(">"):
            try:
                return float(valor) > float(espera[1:])
            except (TypeError, ValueError):
                return False
        if espera == "nao-vazio":
            return bool(valor)
        if espera.startswith("contem:"):
            alvo = espera[7:].split(">")
            if not isinstance(valor, list):
                return False
            return any(list(x) == alvo for x in valor if isinstance(x, (list, tuple)))
        return str(valor) == espera
    return valor == espera


class Medidor:
    def __init__(self) -> None:
        self.tracked = [f for f in git("ls-files").splitlines() if f]
        self.set_tracked = set(self.tracked)
        self._txt: dict[str, str] = {}
        self._json: dict[str, object] = {}
        self.leis = {}
        if LEIS.is_file():
            for l in json.loads(LEIS.read_text(encoding="utf-8")).get("LAWS", []):
                self.leis[l["id"]] = l

    def texto(self, rel: str) -> str:
        if rel not in self._txt:
            p = RAIZ / rel
            try:
                self._txt[rel] = p.read_text(encoding="utf-8", errors="replace")
            except OSError:
                self._txt[rel] = ""
        return self._txt[rel]

    def json_de(self, rel: str):
        if rel not in self._json:
            try:
                self._json[rel] = json.loads(self.texto(rel))
            except (ValueError, TypeError):
                self._json[rel] = None
        return self._json[rel]

    # ── BIBLE ───────────────────────────────────────────────────────────────
    def biblia(self, ids: list[str]) -> dict:
        """O que a Bíblia EXIGE. Vem da Bíblia, nunca do mapa."""
        achadas, perdidas = [], []
        for i in ids or []:
            (achadas if i in self.leis else perdidas).append(i)
        return {
            "leis": [{"id": i, "nome": self.leis[i]["nome"],
                      "law_status": self.leis[i].get("law_status"),
                      "italia": self.leis[i].get("italia")} for i in achadas],
            "leis_inexistentes": perdidas,
            "exigido": bool(achadas),
        }

    # ── DECLARED ────────────────────────────────────────────────────────────
    def declarado(self, ref: dict | None) -> dict:
        if not ref:
            return {"estado": "SEM_DECLARACAO", "file": None, "anchor": None,
                    "gerado_pelo_mapa": False}
        f, a = ref.get("file"), ref.get("anchor", "")
        ger = gerado_pelo_mapa(f or "")
        if f not in self.set_tracked and not (RAIZ / f).is_file():
            return {"estado": "FICHEIRO_AUSENTE", "file": f, "anchor": a, "gerado_pelo_mapa": ger}
        if norm(a) and norm(a) in norm(self.texto(f)):
            return {"estado": "CONFIRMADA", "file": f, "anchor": a, "gerado_pelo_mapa": ger}
        return {"estado": "FRASE_NAO_ENCONTRADA", "file": f, "anchor": a, "gerado_pelo_mapa": ger}

    # ── O CASCO JA FOI MEDIDO. NAO SE MEDE OUTRA VEZ, LE-SE ─────────────────
    CASCO = "system-map/data/casco.generated.json"

    RE_CAPACIDADE = re.compile(r"static\s+CAPABILITY_OF\s*=\s*\{([^}]*)\}")
    RE_PAR = re.compile(r"(\w+)\s*:\s*'(\w*)'")
    PORTALE = "italia-portale/client/portale.html"

    def telas_por_ferramenta(self) -> dict:
        """Quantas TELAS do portal pertencem a cada ferramenta — medido.

        Responde «analise pronta ou ferramenta exploratoria?» sem ninguem ter
        de opinar: uma ferramenta com UMA tela entrega uma leitura fechada;
        uma com VARIAS deixa entrar e navegar (lista, detalhe, perfil, evento).
        A tabela e a mesma que o proprio portal usa para saber em que
        capacidade esta — `CAPABILITY_OF` — por isso nao ha aqui um segundo
        criterio a divergir do primeiro.
        """
        if getattr(self, "_telas", None) is not None:
            return self._telas
        fora: dict[str, list] = {}
        texto = self.texto(self.PORTALE)
        m = self.RE_CAPACIDADE.search(texto)
        if m:
            linha = texto[:m.start()].count("\n") + 1
            for tela, cap in self.RE_PAR.findall(m.group(1)):
                if cap:
                    fora.setdefault(cap, []).append(tela)
            self._linha_capacidade = linha
        self._telas = fora
        return fora

    def ferramenta(self, vista: str | None) -> dict | None:
        """O que a maquina ja mediu sobre UMA ferramenta do portal.

        Nada aqui e escrito a mao. `scan_casco.py` le `portale.html` e os
        contratos de bloco e escreve o que encontrou; este metodo so vai buscar
        a linha que corresponde a esta vista. Se a vista nao existir no censo,
        devolve `None` — e o cartao dira que nao sabe, em vez de inventar.

        A prova de que isto nao e um laco: `casco.generated.json` mede o PORTAL
        (`italia-portale/client/portale.html`), nao mede o mapa. E observacao
        sobre a maquina, como `provas-de-execucao.json` — nunca autoridade
        sobre o que a arquitetura deve ser. Por isso entra em `observado`, e
        nunca em `declarado`.
        """
        if not vista:
            return None
        d = self.json_de(self.CASCO)
        if not isinstance(d, dict):
            return None
        achado = [f for f in (d.get("FERRAMENTAS") or [])
                  if isinstance(f, dict) and f.get("vista") == vista]
        if len(achado) != 1:
            return None
        f = achado[0]
        camadas = {}
        for nome, c in (f.get("camadas") or {}).items():
            if isinstance(c, dict):
                camadas[nome] = {"tipo": c.get("tipo"), "o_que_e": c.get("o_que_e"),
                                 "prova": c.get("prova")}
        telas = self.telas_por_ferramenta().get(vista, [])
        return {
            "vista": f.get("vista"),
            "nome": f.get("nome"),
            "telas": sorted(telas),
            "modo": ("EXPLORATORIA" if len(telas) > 1
                     else "ANALISE_PRONTA" if len(telas) == 1 else None),
            "prova_das_telas": ({"file": self.PORTALE,
                                 "line": getattr(self, "_linha_capacidade", None),
                                 "simbolo": "static CAPABILITY_OF"} if telas else None),
            "de_onde_vem": f.get("de_onde_vem"),
            "leitura": f.get("leitura"),
            "confianca": f.get("confianca") or None,
            "recebe": f.get("o_que_alimenta") or None,
            "mostra": f.get("resumo") or None,
            "camadas": camadas,
            "contratos": list(f.get("ficheiros") or []),
            "tecido_comum": list(f.get("tecido_comum") or []),
            "blocos": list(f.get("blocos") or []),
            "registos_citados": list(f.get("registos_citados") or []),
            "riscos": list(f.get("riscos") or []),
            "perguntas_abertas": list(f.get("perguntas_abertas") or []),
            "confissoes": list(f.get("confissoes") or []),
            "prova_do_nome": f.get("prova_do_nome"),
        }

    # ── CODE ────────────────────────────────────────────────────────────────
    def codigo(self, padroes: list[str]) -> dict:
        """Devolve os ficheiros E o padrao que apanhou cada um.

        O padrao importa porque UM FICHEIRO TEM UM DONO: quando uma peca apanha
        a gaveta inteira (`coleta/**`) e outra nomeia um ficheiro la dentro, a
        que nomeia e a dona. Sem saber qual padrao apanhou o que, essa decisao
        teria de ser escrita a mao dezenove vezes — e uma excecao escrita a mao
        e uma excecao que envelhece calada.
        """
        achados, vazios, por_padrao = set(), [], {}
        for p in padroes or []:
            if p.endswith("/**"):
                base = p[:-3].rstrip("/") + "/"
                hit = [f for f in self.tracked if f.startswith(base)]
            elif "*" in p or "?" in p:
                hit = [f for f in self.tracked if fnmatch.fnmatch(f, p)]
            else:
                hit = [f for f in self.tracked
                       if f == p or f.startswith(p.rstrip("/") + "/")]
            if hit:
                achados.update(hit)
                for f in hit:
                    # o padrao MAIS ESPECIFICO fica registado para cada ficheiro
                    if f not in por_padrao or _espec(p) > _espec(por_padrao[f]):
                        por_padrao[f] = p
            else:
                vazios.append(p)
        return {"ficheiros": sorted(achados), "padroes_vazios": vazios,
                "declarou": bool(padroes), "por_padrao": por_padrao}

    # ── CODE que vive DENTRO de um ficheiro de outro dono ───────────────────
    def codigo_em(self, refs: list) -> list:
        """CONCEITO NAO E IMPLEMENTACAO FISICA (COL-LAW-315).

        `READY` e um contrato de 12 campos implementado por
        `admissao.pronto_para_inteligencia()` — uma funcao DENTRO de um ficheiro
        cujo dono e a porta de admissao. Se o conceito reivindicasse o ficheiro
        para provar que tem codigo, roubava o ficheiro ao dono certo; se nao
        declarasse nada, o mapa diria «nao implementado» sobre codigo que existe.

        Por isso aponta-se o SIMBOLO, e nao o ficheiro: prova a implementacao sem
        mexer na propriedade.
        """
        out = []
        for r in refs or []:
            f, sim = r.get("file"), r.get("simbolo", "")
            if not (RAIZ / f).is_file():
                out.append({"file": f, "simbolo": sim, "estado": "FICHEIRO_AUSENTE"}); continue
            achou = None
            for i, linha in enumerate(self.texto(f).splitlines(), 1):
                if sim in linha:
                    achou = {"line": i, "snippet": linha.strip()[:150]}; break
            out.append({"file": f, "simbolo": sim,
                        "estado": "ENCONTRADO" if achou else "NAO_ENCONTRADO", **(achou or {})})
        return out

    # ── OBSERVED — com relevância ───────────────────────────────────────────
    def observado(self, obs: list) -> list:
        out = []
        for o in obs or []:
            rel, cam, esp = o["artefato"], o.get("caminho"), o.get("espera")
            reg = {"artefato": rel, "caminho": cam, "espera": esp,
                   "prova": o.get("prova", ""), "gerado_pelo_mapa": gerado_pelo_mapa(rel)}
            if not (RAIZ / rel).is_file():
                out.append({**reg, "estado": "ARTEFATO_AUSENTE", "valor": None}); continue
            d = self.json_de(rel)
            if d is None:
                out.append({**reg, "estado": "ARTEFATO_ILEGIVEL", "valor": None}); continue
            achou, valor = caminho_em(d, cam)
            if not achou:
                out.append({**reg, "estado": "CAMINHO_AUSENTE", "valor": None}); continue
            v = valor if not isinstance(valor, (list, dict)) else f"<{type(valor).__name__}:{len(valor)}>"
            out.append({**reg, "valor": v,
                        "estado": "CONFIRMA" if bate(valor, esp) else "NAO_CONFIRMA"})
        return out

    # ── prova de código para uma aresta ─────────────────────────────────────
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


def main() -> int:
    if not MODELO.is_file():
        print(f"modelo ausente: {MODELO}", file=sys.stderr)
        return 2
    m = Medidor()
    if not m.leis:
        print("AVISO: docs/biblia/leis.json nao foi lido — a dimensao BIBLE fica vazia",
              file=sys.stderr)
    modelo = json.loads(MODELO.read_text(encoding="utf-8"))

    conceitos = []
    for c in modelo["CONCEITOS"]:
        conceitos.append({
            "id": c["id"],
            "biblia": m.biblia(c.get("leis", [])),
            "declarado": m.declarado(c.get("declarado_por")),
            "codigo": m.codigo(c.get("codigo", [])),
            "codigo_em": m.codigo_em(c.get("codigo_em", [])),
            "observado": m.observado(c.get("observado_por", [])),
            "ferramenta": m.ferramenta(c.get("ferramenta_do_casco")),
        })

    ligacoes = []
    for e in modelo["LIGACOES"]:
        ligacoes.append({
            "de": e["de"], "para": e["para"],
            "declarada": m.declarado(e.get("declarada")),
            "codigo": m.linha(e.get("codigo")),
            "observada": (m.observado([e["observada"]])[0] if e.get("observada")
                          else {"estado": "SEM_OBSERVACAO", "artefato": None,
                                "gerado_pelo_mapa": False}),
        })

    departamentos = [{"id": d["id"], "declarado": m.declarado(d.get("declarado_por"))}
                     for d in modelo["DEPARTAMENTOS"]]

    saida = {
        "SCHEMA": "sintonia.system-map-v2.medida/2",
        "PROVENANCE": {
            "REPO": "lucianodalondon-sys/eame-sintonia",
            "BRANCH": git("rev-parse", "--abbrev-ref", "HEAD"),
            "HEAD": git("rev-parse", "HEAD"),
            # A data é a do COMMIT, nunca do relógio: um relógio dentro do
            # artefato faz o portão acusar drift a cada minuto.
            "GENERATED_AT": git("log", "-1", "--format=%cI"),
        },
        "BIBLIA": {"ficheiro": "docs/biblia/leis.json", "leis_conhecidas": len(m.leis)},
        "FILES_TRACKED": len(m.tracked),
        "DEPARTAMENTOS": departamentos,
        "CONCEITOS": conceitos,
        "LIGACOES": ligacoes,
    }
    SAIDA.parent.mkdir(parents=True, exist_ok=True)
    SAIDA.write_text(json.dumps(saida, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"medido · {len(conceitos)} conceitos · {len(ligacoes)} ligacoes · "
          f"{len(m.leis)} leis da Biblia · {len(m.tracked)} ficheiros")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
