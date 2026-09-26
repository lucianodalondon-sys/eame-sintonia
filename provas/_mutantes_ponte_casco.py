#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Mutacao da PONTE INTELLIGENCE -> CASCO (nuvem-int-casco-ponte-v1).

    py provas/_mutantes_ponte_casco.py

Cada mutante e plantado numa COPIA da arvore minima, numa pasta temporaria fora
do repositorio, e la corre tests/test_ponte_intelligence_casco.py. O repositorio
nao e tocado — nem git checkout, nem reposicao: a copia morre com a pasta.

Um mutante MORTO e um teste que falhou por causa dele. Um VIVO e um defeito que
os testes deixam passar, e reprova esta prova (codigo de saida 1).
"""
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
ALVO = "pacote/ponte_intelligence_casco.py"
ALVO_ESQ = "pacote/esqueleto_scientifica.py"
COPIAR = ("_gavetas.py", ALVO, ALVO_ESQ, "tests/test_esqueleto_scientifica.py", "motor/corrida_da_inteligencia.py",
          "provas/espinha_da_intelligence.py", "admissao/sala_de_espera.py",
          "research/intelligence/COORTE-DA-SALA-2026-09-14.json",
          "tests/test_ponte_intelligence_casco.py",
          "italia-portale/client/_ds/adama-brandwell/styles.css",
          "italia-portale/client/portale.html")

M = [
    ("M1 sinal sem prova atravessa",
     "                falha = conferir_prova(s, linhagem)\n",
     "                falha = None\n"),
    ("M2 cartao sai sem a marca",
     '        "MARCA": MARCA,\n        "NAO_PARA_CLIENTE": True,\n        "FERRAMENTA": ferramenta,\n',
     '        "NAO_PARA_CLIENTE": True,\n        "FERRAMENTA": ferramenta,\n'),
    ("M3 conferencia nao olha a marca do cartao",
     '            if c.get("MARCA") != MARCA or c.get("NAO_PARA_CLIENTE") is not True:\n',
     '            if False:\n'),
    ("M4 NAO SEI vira vazio",
     "    return NAO_SEI if e_ignorancia(v) else v\n",
     '    return "" if e_ignorancia(v) else v\n'),
    ("M5 qualquer estado atravessa (promocao)",
     '                if s.get("ESTADO") != ESTADO_TRANSPORTAVEL:\n',
     '                if False:\n'),
    ("M6 prova fora da corrida aceite",
     "        if not todas:\n            return \"PROVA_FORA_DA_CORRIDA\"",
     "        if not todas:\n            continue\n            return \"PROVA_FORA_DA_CORRIDA\""),
    ("M7 G0 ignorado",
     '        if g0 == ["PASSOU"]:\n',
     '        if True:\n'),
    ("M8 DOCUMENT_ID nao exigido",
     'CAMPOS_DA_PROVA = ("ITEM_ID", "RAW_OBSERVATION_ID", "SOURCE_ID", "DOCUMENT_ID")',
     'CAMPOS_DA_PROVA = ("ITEM_ID", "RAW_OBSERVATION_ID", "SOURCE_ID")'),
    ("M9 corrida que falhou da cartao",
     "        elif estado in CORRIDA_SEM_SAIDA or estado == NAO_SEI:\n",
     "        elif False:\n"),
    ("M10 duplicado conta duas vezes",
     '                if s["SIGNAL_ID"] in vistos:\n',
     '                if False:\n'),
    ("M11 a ponte completa chave que falta",
     "    chaves = {k: _valor(dadas.get(k)) for k in chaves_contrato}\n",
     '    chaves = {k: _valor(dadas.get(k) or dadas.get("CROP_ID")) for k in chaves_contrato}\n'),
    ("M12 escreve dentro do portal",
     '    return not (rel.parts and rel.parts[0] == "italia-portale")\n',
     "    return True\n"),
    ("M13 conferencia aceita NAO SEI escondido",
     "                    if e_ignorancia(val) and val != NAO_SEI:\n",
     "                    if False:\n"),
    ("M14 conferencia aceita cartao sem prova",
     "            if not isinstance(prova, list) or not prova:\n                v.append(f\"{f}/{sid}: cartao sem prova\")",
     "            if False:\n                v.append(f\"{f}/{sid}: cartao sem prova\")"),
    ("M15 lacunas da corrida somem",
     '    for r in corrida.get("REQUIREMENTS") or []:\n',
     "    for r in []:\n"),
    ("M16 ferramenta sem contrato desenha",
     '        if meta["CHAVES"] is None:\n            for s in sinais:\n',
     '        if meta["CHAVES"] is None and False:\n            for s in sinais:\n'),
    ("M17 pagina sem a faixa EXPERIMENTAL",
     "        f'<div class=\"faixa\" data-marca=\"1\">{E(MARCA)} — anteprima locale, non per il cliente, non pubblicata</div>',\n",
     ""),
    ("M18 pagina nao escapa o texto da corrida",
     "    from html import escape as E\n",
     "    E = lambda s: s  # noqa: E731\n"),
    ("M19 P1 de volta: linhagem um-para-um (a ultima ganha)",
     '            out.setdefault(str(e["ITEM_ID"]), []).append(e)\n',
     '            out[str(e["ITEM_ID"])] = [e]\n'),
    ("M20 P4 de volta: o valor fora do contrato some",
     "        \"FORA_DO_CONTRATO\": {k: _valor(dadas[k]) for k in sorted(dadas)\n",
     "        \"FORA_DO_CONTRATO\": {k: NAO_SEI for k in sorted(dadas)\n"),
    ("M21 CORRIDA_UPSTREAM da prova ignorada",
     '        if not e_ignorancia(p.get("CORRIDA_UPSTREAM")):\n',
     '        if False:\n'),
    ("M22 ambiguidade resolvida a favor do PASSOU",
     '        if "PASSOU" in g0:\n            return ("PROVA_AMBIGUA"',
     '        if "PASSOU" in g0:\n            continue\n            return ("PROVA_AMBIGUA"'),
    # O esqueleto de Intelligence Scientifica (ordem da coordenacao 26/09 17:35)
    ("E1 tema tirado da cultura",
     '        pares = u.get("NA_CONSULTA_E_NO_TEXTO") or []\n',
     '        pares = u.get("NA_CONSULTA_E_NO_TEXTO") or _valores(u.get("CULTURA"))\n', ALVO_ESQ),
    ("E2 SO_NOME passa a ligar",
     'LIGADOS = ("MUR_E_OBRAS", "VARIOS_IDS")',
     'LIGADOS = ("MUR_E_OBRAS", "VARIOS_IDS", "SO_NOME")', ALVO_ESQ),
    ("E3 tema sem a marca",
     '            "MARCA": MARCA, "NAO_PARA_CLIENTE": True, "TEMA": t,\n',
     '            "NAO_PARA_CLIENTE": True, "TEMA": t,\n', ALVO_ESQ),
    ("E4 NAO SEI vira vazio",
     '    return NAO_SEI if e_ignorancia(x) else x\n',
     '    return "" if e_ignorancia(x) else x\n', ALVO_ESQ),
    ("E5 publicacao vira periodo do estudo",
     '        "PERIODO_DO_ESTUDO": _valores(u.get("PERIODO_DO_ESTUDO")) or NAO_SEI,\n',
     '        "PERIODO_DO_ESTUDO": _valores(u.get("PERIODO_DO_ESTUDO")) or _v(u.get("PUBLICADO_EM")),\n', ALVO_ESQ),
    ("E6 independencia sem a base",
     '(dict(pm, BASE=(origens or {}).get("PRE_MEDICAO_BASE", NAO_SEI))',
     '(dict(pm)', ALVO_ESQ),
    ("E7 pagina do esqueleto sem a faixa",
     "         f'<div class=\"faixa\" data-marca=\"1\">{E(MARCA)} — PRE_SALA, non è Intelligence · anteprima locale, non pubblicata</div>',\n",
     "", ALVO_ESQ),
    ("E8 conferencia aceita pessoa nao ligada",
     '            if p.get("ESTADO_NA_LISTA_MESTRA") not in LIGADOS:\n',
     '            if False:\n', ALVO_ESQ),
    ("E9 VARIOS_IDS perde o segundo id",
     '            ids = set(p.get("OPENALEX_IDS") or [])\n',
     '            ids = set((p.get("OPENALEX_IDS") or [])[:1])\n', ALVO_ESQ),
]


def correr(pasta: Path) -> subprocess.CompletedProcess:
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1", PYTHONUTF8="1",
               HTTP_PROXY="http://127.0.0.1:9", HTTPS_PROXY="http://127.0.0.1:9")
    return subprocess.run([sys.executable, "-m", "unittest", "tests.test_ponte_intelligence_casco",
                           "tests.test_esqueleto_scientifica"],
                          cwd=pasta, capture_output=True, text=True, encoding="utf-8",
                          errors="replace", env=env, timeout=300)


def main() -> int:
    originais = {a: (RAIZ / a).read_text(encoding="utf-8") for a in (ALVO, ALVO_ESQ)}
    vivos, nao_aplicou = [], []
    with tempfile.TemporaryDirectory() as d:
        pasta = Path(d)
        # Todo .py versionado vai junto: a espinha le admissao/ e o que ela
        # importa, e essa cadeia muda com cada lote (medido no 278cd489).
        pys = subprocess.run(["git", "-C", str(RAIZ), "ls-files", "*.py"], capture_output=True,
                             text=True, encoding="utf-8").stdout.split()
        for rel in sorted(set(COPIAR) | set(pys)):
            if not (RAIZ / rel).is_file():
                continue
            (pasta / rel).parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(RAIZ / rel, pasta / rel)
        base = correr(pasta)
        if base.returncode != 0:
            print("BASE VERMELHA na copia — a prova nao vale:\n" + base.stderr[-2000:])
            return 2
        print("base: verde na copia")
        for nome, a, b, *alvo in M:
            alvo = alvo[0] if alvo else ALVO
            original = originais[alvo]
            if original.count(a) != 1:
                print(f"{nome}: NAO_APLICOU ({original.count(a)} ocorrencias)")
                nao_aplicou.append(nome)
                continue
            (pasta / alvo).write_text(original.replace(a, b), encoding="utf-8")
            r = correr(pasta)
            caidos = sorted(set(re.findall(r"^(?:FAIL|ERROR): (\S+) \(", r.stderr, re.M)))
            estado = "MORTO" if r.returncode != 0 else "VIVO"
            if estado == "VIVO":
                vivos.append(nome)
            print(f"{nome}: {estado} · {len(caidos)} testes caem · {', '.join(caidos[:4])}")
            (pasta / alvo).write_text(original, encoding="utf-8")
    mortos = len(M) - len(vivos) - len(nao_aplicou)
    print(f"\nMUTACAO: {mortos}/{len(M)} mortos · vivos {vivos or 0} · nao aplicados {nao_aplicou or 0}")
    return 0 if not vivos and not nao_aplicou else 1


if __name__ == "__main__":
    sys.exit(main())
