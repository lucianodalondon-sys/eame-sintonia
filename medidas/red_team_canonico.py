#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""O RED TEAM DA MICRO-COLHEITA CANONICA — cada mutante tem de MORRER.

    py medidas/red_team_canonico.py

    UMA PROVA QUE NAO REPROVA QUANDO O CODIGO PASSA A MENTIR
    NAO E UMA PROVA. E UM COMENTARIO QUE CORRE.

COMO FUNCIONA, E PORQUE ASSIM
-----------------------------
Cada ataque escreve no ficheiro uma versao ERRADA da regra, confirma que o
mutante ENTROU MESMO (`git diff` tem de acusar diferenca — uma substituicao
que nao casou deixa a arvore limpa, e o ataque passaria por «morto» sem
nunca ter existido), corre a prova que devia mata-lo, e repoe o ficheiro.

    MUTANTE QUE NAO ENTROU NAO E MUTANTE MORTO.

O ficheiro e sempre reposto — no fim, com sucesso ou sem ele.

ZERO REDE
---------
Nenhum ataque aqui chama o coletor a serio. Medido nesta casa em 2026-09-21:
uma mutacao de red team desligou o portao e a funcao foi a fonte, colhendo
tres vezes o boletim da APOL com RUN_ID de teste. As provas que este ficheiro
corre usam lancador injectado ou nao tocam em transporte nenhum.

O QUE ESTE FICHEIRO NAO ESCONDE
-------------------------------
Ha ataques que NAO se podem matar hoje, porque a regra que eles violam ainda
nao existe nesta casa. Esses aparecem como `SEM_GUARDA`, com o nome do que
falta, e NAO como sucesso. Um red team que so lista o que ja estava guardado
mede o guarda, nao o perigo.
"""
from __future__ import annotations

import io
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent


def agora() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def _correr(cmd, timeout=900):
    return subprocess.run(cmd, cwd=str(RAIZ), capture_output=True, text=True,
                          encoding="utf-8", errors="replace", timeout=timeout,
                          env={**__import__("os").environ,
                               "PYTHONUTF8": "1", "PYTHONIOENCODING": "utf-8"})


def _sujo(rel: str) -> bool:
    """`git diff --quiet` acusa diferenca? Se nao, o mutante NAO entrou."""
    return _correr(["git", "diff", "--quiet", "--", rel]).returncode != 0


# ── AS PROVAS QUE DEVEM MATAR ──────────────────────────────────────────────
PY_UNIT = lambda pasta, padrao: [sys.executable, "-m", "unittest", "discover",
                                 "-s", pasta, "-t", pasta, "-p", padrao]
NODE = lambda f: ["node", f]


def prova_falhou(cmd) -> tuple[bool, str]:
    r = _correr(cmd)
    saida = (r.stdout + r.stderr)
    # unittest devolve !=0 quando reprova; os ficheiros .mjs desta casa
    # imprimem «FALHOU n» e saem com 1.
    return r.returncode != 0, saida[-400:].strip()


# ── OS ATAQUES ─────────────────────────────────────────────────────────────
# `de` tem de existir LITERALMENTE no ficheiro; se nao existir, o ataque
# reporta-se como NAO_APLICADO e isso NAO e um mutante morto.
ATAQUES = [
    {
        "nome": "READY_LEGACY entra na Collection",
        "lei": "READY_LEGACY != READY_CURRENT — 77 fontes promovidas pela regua antiga",
        "ficheiro": "curadoria/collection_gate.py",
        "de": "    if regua not in RS.REGUAS_QUE_ADMITEM:",
        "para": "    if False:",
        "prova": PY_UNIT("curadoria", "test_collection_gate.py"),
    },
    {
        "nome": "HUMAN_REVIEW_REQUIRED entra na Collection",
        "lei": "uma fonte marcada para olho humano nao entra por omissao",
        "ficheiro": "curadoria/collection_gate.py",
        "de": "if revisao:",
        "para": "if False:",
        "prova": PY_UNIT("curadoria", "test_collection_gate.py"),
    },
    {
        "nome": "FACT_TIME cai para SOURCE_DATE quando nao ha tempo do facto",
        "lei": "FACT_TIME != PUBLISHED_AT — UNKNOWN continua UNKNOWN",
        "ficheiro": "regras/motor_de_rota.mjs",
        "de": 'const FACT_TIME = spec.FACT_TIME || "UNKNOWN";',
        "para": 'const FACT_TIME = spec.FACT_TIME || spec.SOURCE_DATE || "UNKNOWN";',
        "prova": NODE("regras/motor_de_rota_test.mjs"),
    },
    {
        "nome": "a propria pagina de entrada e aceite como materia",
        "lei": "a homepage nao e um documento seu — FAIL_CLOSED, nunca a entrada",
        "ficheiro": "regras/motor_de_rota.mjs",
        "de": 'if (u.replace(/\\/+$/, "") === entradaNorm) continue;',
        "para": "",
        "prova": NODE("regras/motor_de_rota_test.mjs"),
    },
    {
        "nome": "paginacao e feeds entram como documentos",
        "lei": "uma lista de artigos nao e um artigo",
        "ficheiro": "regras/motor_de_rota.mjs",
        "de": "if (ATIVOS_ESTATICOS.test(u) || PAGINACAO.test(u) || FEED.test(u)) continue;",
        "para": "",
        "prova": NODE("regras/motor_de_rota_test.mjs"),
    },
    {
        "nome": "MATCH desconhecido passa calado na conferencia",
        "lei": "aceitar um campo sem o implementar da verde na conferencia e acusa a fonte na corrida",
        "ficheiro": "regras/motor_de_rota.mjs",
        "de": 'if (aq.MATCH !== undefined && !["HTML", "URL"].includes(aq.MATCH)) {',
        "para": "if (false) {",
        "prova": NODE("regras/motor_de_rota_test.mjs"),
    },
    {
        "nome": "IDENTITY.STRATEGY desconhecida passa calada",
        "lei": "`null` nao diz porque — um vocabulario fora da lista reprova com o nome dele",
        "ficheiro": "regras/motor_de_rota.mjs",
        "de": "if (!ESTRATEGIAS_DE_IDENTIDADE.includes(spec.STRATEGY)) {",
        "para": "if (false) {",
        "prova": NODE("regras/motor_de_rota_test.mjs"),
    },
    {
        "nome": "identidade a meio em vez de identidade vazia",
        "lei": "um DOCUMENT_ID com buraco e pior que nenhum",
        "ficheiro": "regras/motor_de_rota.mjs",
        # ⚠️ `\r\n`: `regras/motor_de_rota.mjs` esta em CRLF (457 linhas, zero
        # LF soltos). Uma ancora com `\n` nao casa, e o ataque sai
        # NAO_APLICADO — que e exactamente o que aconteceu na 1.a corrida
        # deste red team, e nao e um mutante morto.
        "de": "    } else {\r\n      return vazio;\r\n    }",
        "para": '    } else {\r\n      grupos[nome] = ["", ""];\r\n    }',
        "prova": NODE("regras/motor_de_rota_test.mjs"),
    },
    {
        "nome": "«nao consegui ler o robots» vira «o site proibiu»",
        "lei": "ROBOTS_GATE_FAIL != ROBOTS_DISALLOW — e uma acusacao ao site",
        "ficheiro": "medidas/corrida_canonica.py",
        "de": '        return {"ROBOTS_RESULT": "ROBOTS_GATE_FAIL", "PORQUE": str(ex),',
        "para": '        return {"ROBOTS_RESULT": "ROBOTS_DISALLOW", "PORQUE": str(ex),',
        "prova": PY_UNIT("medidas", "test_corrida_canonica.py"),
    },
    {
        "nome": "«robots ilegivel» vira «o site proibiu»",
        "lei": "ROBOTS_UNREADABLE != ROBOTS_DISALLOW",
        "ficheiro": "medidas/corrida_canonica.py",
        "de": '    ilegivel = "ilegível" in motivo or "ilegivel" in motivo',
        "para": "    ilegivel = False",
        "prova": PY_UNIT("medidas", "test_corrida_canonica.py"),
    },
    {
        "nome": "robots ilegivel deixa ir na mesma",
        "lei": "nao saber se se pode e motivo para parar, nunca para prosseguir",
        "ficheiro": "medidas/corrida_canonica.py",
        "de": '"LIDO_EM": quando, "PODE_IR": False,\n            "LEI": "nao consegui LER != o site proibiu"}',
        "para": '"LIDO_EM": quando, "PODE_IR": True,\n            "LEI": "nao consegui LER != o site proibiu"}',
        "prova": PY_UNIT("medidas", "test_corrida_canonica.py"),
    },
    {
        "nome": "fonte sem contrato vai a rede na mesma",
        "lei": "o portao aprovar nao quer dizer que se sabe o caminho",
        "ficheiro": "medidas/corrida_canonica.py",
        "de": '        if not c.get("PERCORRIVEL"):',
        "para": "        if False:",
        "prova": PY_UNIT("medidas", "test_corrida_canonica.py"),
    },
    {
        "nome": "o relatorio inventa um HTTP 200 que ninguem mediu",
        "lei": "campo que o livro nao tem sai AUSENTE, nunca preenchido para agradar",
        "ficheiro": "medidas/corrida_canonica.py",
        "de": '"HTTP_STATUS": o.get("HTTP_STATUS", "AUSENTE_NO_LIVRO — o livro guarda o RESULTADO, nao o codigo"),',
        "para": '"HTTP_STATUS": o.get("HTTP_STATUS", 200),',
        "prova": PY_UNIT("medidas", "test_corrida_canonica.py"),
    },
    {
        "nome": "o instrumento passa a ter a sua lista de IDs autorizados",
        "lei": "PROIBIDO ALLOWED_IDS — as elegiveis RESULTAM da regra",
        "ficheiro": "medidas/corrida_canonica.py",
        "de": "    elegiveis = CG.elegiveis()",
        "para": '    elegiveis = ["IT-T7-042", "IT-T7-043"]',
        "prova": PY_UNIT("medidas", "test_corrida_canonica.py"),
    },
    {
        "nome": "o veredito do robots vem em cache de outra corrida",
        "lei": "entre a RUN1 e a RUN3 o bloqueio ja mudou de fonte nesta casa",
        "ficheiro": "medidas/corrida_canonica.py",
        "de": "    HTTP._ROBOTS.clear()",
        "para": "    pass",
        "prova": PY_UNIT("medidas", "test_corrida_canonica.py"),
    },
    {
        "nome": "o coletor corre sem passar pelo portao de admissao",
        "lei": "NOMEAR NAO E ADMITIR — bypass directo da admissao",
        "ficheiro": "coleta/italy_executor.py",
        "de": '        if not a["ADMITIDA"]:',
        "para": "        if False:",
        "prova": PY_UNIT("curadoria", "test_collection_gate.py"),
    },
]

# ── OS ATAQUES QUE HOJE NAO TEM GUARDA, E DIZEM-NO ─────────────────────────
# Nao se inventa aqui a guarda que falta: inventa-la no ficheiro do red team
# era escrever a prova e o codigo no mesmo sitio, e as duas passariam sempre.
SEM_GUARDA = [
    {
        "nome": "a segunda RUN regrava o armazem inteiro sem o documento ter mudado",
        "lei": "nova observacao PODE nascer sem duplicar armazenamento",
        "medido": ("RUN2 sobre os mesmos 85 documentos: 83 objectos NOVOS no "
                   "armazem, 7,86 MB. As linhas diferentes sao 374 em 86.441 "
                   "(0,43%) e TODAS sao rasto de maquina — o carimbo "
                   "`article:modified_time` traz A HORA DA NOSSA VISITA, mais "
                   "tokens CSRF e ids de DOM por render. Zero texto editorial."),
        "falta": ("ninguem compara o documento SEM o rasto volatil antes de "
                  "gravar. `DOCUMENT_CHANGED_IN_PLACE` esta a ser disparado "
                  "pela nossa propria pegada."),
    },
    {
        "nome": "o hash serve de identidade da VERSAO do documento",
        "lei": "HASH E BYTE_ID, NAO IDENTIDADE",
        "medido": ("DOCUMENT_VERSION_ID == 'v1_' + RAW_SHA256[:12] em 85 de 85 "
                   "observacoes da RUN1C, conferido aritmeticamente. E "
                   "RAW_OBSERVATION_ID nao existe: 0 de 360 linhas do livro."),
        "falta": ("defeito PRE-EXISTENTE e comum as duas linhas. A missao mandou "
                  "medir e nomear, e NAO refactorizar. Nao se escreve aqui uma "
                  "guarda para um defeito que se decidiu nao corrigir: isso "
                  "deixava o trunk vermelho de proposito."),
    },
    {
        "nome": "SOURCE_LOCATION preenche FACT_LOCATION por fallback",
        "lei": "a sede da fonte nao e o sitio onde a coisa aconteceu",
        "medido": ("os 174 contratos onboarded declaram FACT_LOCATION_RULE = "
                   "'UNKNOWN por padrao — so preencher se o proprio documento "
                   "declarar; NUNCA inferir'. Nenhuma etapa desta missao chegou "
                   "a preencher FACT_LOCATION: a cadeia parou antes do DERIVED."),
        "falta": ("a regra existe em prosa no contrato e NAO ha codigo que a "
                  "execute nesta linha — nao ha o que mutar."),
    },
]


def main() -> int:
    relatorio = {"INSTRUMENTO": "medidas/red_team_canonico.py", "QUANDO": agora(),
                 "ATAQUES": [], "SEM_GUARDA": SEM_GUARDA}
    print("ATAQUE                                                    MUTANTE   PROVA")
    print("-" * 92)
    mortos = sobreviventes = nao_aplicados = 0

    for a in ATAQUES:
        rel = a["ficheiro"]
        alvo = RAIZ / rel
        original = io.open(alvo, encoding="utf-8", newline="").read()
        linha = {"NOME": a["nome"], "LEI": a["lei"], "FICHEIRO": rel}
        try:
            if a["de"] not in original:
                linha["RESULTADO"] = "NAO_APLICADO"
                linha["PORQUE"] = "o texto a mutar nao existe no ficheiro"
                nao_aplicados += 1
            else:
                io.open(alvo, "w", encoding="utf-8", newline="").write(
                    original.replace(a["de"], a["para"], 1))
                entrou = _sujo(rel)
                linha["MUTANTE_ENTROU"] = entrou
                if not entrou:
                    linha["RESULTADO"] = "NAO_APLICADO"
                    linha["PORQUE"] = "git diff nao acusou diferenca"
                    nao_aplicados += 1
                else:
                    morreu, cauda = prova_falhou(a["prova"])
                    linha["RESULTADO"] = "MORTO" if morreu else "SOBREVIVEU"
                    linha["PROVA"] = " ".join(a["prova"][-2:])
                    linha["SAIDA"] = cauda if not morreu else ""
                    mortos += morreu
                    sobreviventes += not morreu
        finally:
            io.open(alvo, "w", encoding="utf-8", newline="").write(original)
            if _sujo(rel):
                linha["AVISO"] = "O FICHEIRO NAO VOLTOU AO ESTADO ORIGINAL"
        relatorio["ATAQUES"].append(linha)
        print("%-56s %-9s %s" % (a["nome"][:56],
                                 "entrou" if linha.get("MUTANTE_ENTROU") else "-",
                                 linha["RESULTADO"]))

    relatorio["MORTOS"] = mortos
    relatorio["SOBREVIVENTES"] = sobreviventes
    relatorio["NAO_APLICADOS"] = nao_aplicados
    relatorio["RED_TEAM_PROVEN"] = (sobreviventes == 0 and nao_aplicados == 0)

    print("-" * 92)
    print("MORTOS %d · SOBREVIVERAM %d · NAO APLICADOS %d" % (mortos, sobreviventes, nao_aplicados))
    print("")
    print("SEM GUARDA HOJE (e isto NAO e sucesso):")
    for s in SEM_GUARDA:
        print("  · %s" % s["nome"])

    destino = RAIZ / "medidas" / "RED-TEAM-CANONICO-V1.json"
    with io.open(destino, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(relatorio, fh, ensure_ascii=False, indent=1)
        fh.write("\n")
    print("\nrelatorio: %s" % destino)
    return 0 if sobreviventes == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
