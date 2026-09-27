#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Mutacao da RETE-VOCI-DATI: planta defeitos no adaptador e prova que os testes os apanham.

    python3 provas/_mutantes_rete_voci_dati.py

Cada mutante e plantado numa COPIA minima da arvore, numa pasta temporaria fora do repositorio, e
la corre tests/test_rete_voci_dati.py. O repositorio nao e tocado.

MORTO = um teste falhou por causa dele. VIVO = defeito que os testes deixam passar (reprova esta
prova, saida 1). NAO_APLICOU (algum texto-alvo nao existe exactamente uma vez) tambem reprova.
"""
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
ALVO = "pacote/rete_voci_dati.py"
COPIAR = ("tests/test_rete_voci_dati.py", "tests/fixtures/pote/CORRIDA-SINTETICA-POTE.json",
          "data/derivados/RETE-VOCI-DATI/CONTAGEM.json", "docs/fontes/ATLAS-DE-FONTES-EAME.md",
          "curadoria/italy_contracts_curator.json", "candidatas/ITALY-SOURCE-MASTER-V1.json")

#: (nome, [(texto-alvo, substituto), ...])
M = [
    ("R1 G0 ignorado: item bloqueado vira prova",
     [("        if passou:\n            prova = {", "        if True:\n            prova = {")]),
    ("R2 Meta diz «hoje»",
     [('quando = f"observado em {dia_obs[8:10]}/{dia_obs[5:7]}/{dia_obs[:4]}" if dia_obs else NAO_SEI',
       'quando = "ativo hoje" if dia_obs else NAO_SEI')]),
    ("R3 pagina fora do agro (FMC Moto) entra",
     [('    if str(a.get("PAGE_ID")) in PAGINAS_FORA_DO_AGRO:\n', "    if False:\n")]),
    ("R4 serie com um ponto so",
     [("        if len(periodos) < 2 or len(unidades) != 1:\n", "        if len(unidades) != 1:\n")]),
    ("R5 serie mistura unidades",
     [('        grupos.setdefault(p["CHAVE"] + (str(p["UNIDADE"]),), []).append(p)\n',
       '        grupos.setdefault(p["CHAVE"] + ("*",), []).append(p)\n'),
      ("        if len(periodos) < 2 or len(unidades) != 1:\n", "        if len(periodos) < 2:\n")]),
    ("R6 publicacao vira tempo do facto nas vozes",
     [('                       fact_time=r.get("periodo"), base="periodo declarado pelo curador no registo (PUBLIC-VOICES)",',
       '                       fact_time=pub, base="periodo declarado pelo curador no registo (PUBLIC-VOICES)",')]),
    ("R7 data de leitura inventada como publicacao",
     [('    return (NAO_SEI, d) if "lido nesta data" in s else (d, NAO_SEI)\n',
       "    return (d, d) if \"lido nesta data\" in s else (d, NAO_SEI)\n")]),
    ("R8 SOURCE_ID do dataset (a plataforma) em vez do Atlas",
     [('    prova = L.item("competitors", "CONCORRENCIA", a["ID"], source_id=_source_id_do_atlas(L, a.get("URL")),',
       '    prova = L.item("competitors", "CONCORRENCIA", a["ID"], source_id=a.get("SOURCE_ID"),')]),
    ("R9 a pessoa da voz viaja",
     [('            "SPEAKER_ID": NAO_SEI, "SPEAKER_ROLE": _v(r.get("tipo")),',
       '            "SPEAKER_ID": _curto(r.get("o_que"), 80), "SPEAKER_ROLE": _v(r.get("tipo")),')]),
    ("R10 texto do curador sobre agricultor privado viaja",
     [("    if any(p in str(r.get(\"tipo\", \"\")).upper() for p in PAPEL_PRIVADO):\n", "    if False:\n")]),
    ("R11 archive muda a especie",
     [('            }), o["PROVA"], porque=o["PORQUE"], incerteza=o["INCERTEZA"], especie=o["ESPECIE"])',
       '            }), o["PROVA"], porque=o["PORQUE"], incerteza=o["INCERTEZA"], especie="FINDING")')]),
    ("R12 rendimento conta a dobrar",
     [('        e["LIDOS"] += 1\n', '        e["LIDOS"] += 2\n')]),
    ("R13 dominio ambiguo escolhe a primeira ficha",
     [("        if notas and notas[0][0] >= 1 and (len(notas) == 1 or notas[1][0] < notas[0][0]):\n",
       "        if notas:\n")]),
    ("R14 NAO SEI vira vazio",
     [("    return NAO_SEI if e_ignorancia(x) else x\n", '    return "" if e_ignorancia(x) else x\n')]),
    ("R15 portao de saida nao olha «hoje»",
     [('            if "hoje" in _NEGA_HOJE.sub("", texto.lower()):\n', "            if False:\n")]),
    ("R16 portao de saida nao olha contacto",
     [("            if _CONTATO.search(texto):\n", "            if False:\n")]),
    ("R17 juntar aceita LINEAGE repetida",
     [("    if repetidas:\n", "    if False:\n")]),
    ("R18 juntar deixa a extra mandar no cabecalho",
     [('    out = json.loads(json.dumps(corrida))\n',
       '    out = json.loads(json.dumps(corrida))\n    out["INTELLIGENCE_RUN_ID"] = extra["INTELLIGENCE_RUN_ID"]\n')]),
    ("R19 o resumo do artigo viaja",
     [('"TITULO": _curto(m.get("TITLE")) or NAO_SEI, "REVISTA": _v(m.get("VENUE")),',
       '"TITULO": _curto(m.get("TITLE")) or NAO_SEI, "REVISTA": _v(m.get("VENUE")), "ABSTRACT": m.get("ABSTRACT"),')]),
    ("R20 captura desconhecida vira data longe (futuro nunca bloqueia)",
     [('"CAPTURED_AT": _v(colhido) if not e_ignorancia(colhido) else _v(captura_g0)}',
       '"CAPTURED_AT": _v(colhido) if not e_ignorancia(colhido) else "2099-12-31"}')]),
    ("R21 a entrada extra escreve dentro do portal",
     [('        if destino and "italia-portale" in Path(destino).resolve().parts:\n', "        if False:\n")]),
    ("R22 relogio na identidade (deixa de ser deterministica)",
     [('"INTELLIGENCE_RUN_ID": "RVD-" + impressao[:16],',
       '"INTELLIGENCE_RUN_ID": "RVD-" + str(__import__("time").time_ns()),')]),
    ("R23 corpus aceita prova de pessoa fraca",
     [('        fortes = [m for m in ms if m.get("PERSON_PROOF") in PROVA_FORTE_DE_PESSOA and m.get("DOMAIN_STATE") == "IN_DOMAIN"]',
       '        fortes = list(ms)')]),
    ("R24 estado do anuncio sem a data da observacao",
     [('"ESTADO_NA_OBSERVACAO": NAO_SEI if estado == NAO_SEI else f"{estado} ({quando}; nao e o estado de hoje)",',
       '"ESTADO_NA_OBSERVACAO": estado,')]),
]


def correr(pasta: Path) -> subprocess.CompletedProcess:
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1", PYTHONUTF8="1",
               HTTP_PROXY="http://127.0.0.1:9", HTTPS_PROXY="http://127.0.0.1:9")
    return subprocess.run([sys.executable, "-m", "unittest", "tests.test_rete_voci_dati"],
                          cwd=pasta, capture_output=True, text=True, encoding="utf-8",
                          errors="replace", env=env, timeout=1200)


def main() -> int:
    sys.path.insert(0, str(RAIZ / "pacote"))
    import rete_voci_dati as R                               # noqa: E402 — so para saber que ficheiros le
    original = (RAIZ / ALVO).read_text(encoding="utf-8")
    vivos, nao_aplicou = [], []
    with tempfile.TemporaryDirectory() as d:
        pasta = Path(d)
        pys = subprocess.run(["git", "-C", str(RAIZ), "ls-files", "*.py", "*.json"], capture_output=True,
                             text=True, encoding="utf-8").stdout.split()
        pys = [p for p in pys if p.endswith(".py") or p.startswith(("motor/", "leis/", "regras/", "referencia/"))]
        for rel in sorted(set(COPIAR) | set(pys) | set(R.FICHEIROS.values()) | {R.MESTRE_ITALIANO, ALVO}):
            if not (RAIZ / rel).is_file():
                continue
            (pasta / rel).parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(RAIZ / rel, pasta / rel)
        subprocess.run(["git", "init", "-q", str(pasta)], check=True)
        base = correr(pasta)
        if base.returncode != 0:
            print("BASE VERMELHA na copia — a prova nao vale:\n" + base.stderr[-3000:])
            return 2
        print("base: verde na copia")
        for nome, trocas in M:
            texto = original
            falhou = [a for a, _ in trocas if original.count(a) != 1]
            if falhou:
                print(f"{nome}: NAO_APLICOU ({[original.count(a) for a, _ in trocas]} ocorrencias)")
                nao_aplicou.append(nome)
                continue
            for a, b in trocas:
                texto = texto.replace(a, b)
            (pasta / ALVO).write_text(texto, encoding="utf-8")
            r = correr(pasta)
            caidos = sorted(set(re.findall(r"^(?:FAIL|ERROR): (\S+) \(", r.stderr, re.M)))
            estado = "MORTO" if r.returncode != 0 else "VIVO"
            if estado == "VIVO":
                vivos.append(nome)
            print(f"{nome}: {estado} · {len(caidos)} testes caem · {', '.join(caidos[:4])}", flush=True)
            (pasta / ALVO).write_text(original, encoding="utf-8")
    mortos = len(M) - len(vivos) - len(nao_aplicou)
    print(f"\nMUTACAO: {mortos}/{len(M)} mortos · vivos {vivos or 0} · nao aplicados {nao_aplicou or 0}")
    return 0 if not vivos and not nao_aplicou else 1


if __name__ == "__main__":
    sys.exit(main())
