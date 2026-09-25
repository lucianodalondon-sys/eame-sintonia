#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PROVAS DE QUE O NOME DA BRANCH NAO DECIDE O P1 (D50 · missao MAPA-RAMO)

    UM PORTAO QUE MUDA DE VEREDITO COM O NOME DO CHECKOUT
    NAO MEDE A ARVORE: MEDE QUEM A ABRIU.

Medido antes do conserto: `NODES[245].facts[0]` do `state.generated.json` era
`branch <nome>` — `integra-onda2-v1` no commitado, `HEAD` num checkout
destacado, `servico-20260923-0923` no vivo. O MESMO COMMIT passava numa branch e
reprovava noutra em `P1_SEM_DRIFT`.

Estas provas:

  1 · geram o mapa com um nome, commitam, e validam O MESMO COMMIT com tres
      nomes de branch diferentes e em HEAD destacado — P1 tem de passar nos
      quatro, e a arquitetura regerada (sem PROVENANCE) tem de ser byte a byte
      a mesma nos quatro;
  2 · provam que o nome continua MEDIDO — em PROVENANCE.BRANCH, que e onde o
      validador ja nao olha — e que nao vaza para mais nenhum sitio;
  3 · provam que o validador CONTINUA A MORDER: uma fonte mexida sem regerar
      reprova P1 (a mutacao que o conserto nao pode ter desligado);
  4 · provam que a tela e o gerador dizem o mesmo ponteiro.

Tudo corre num clone descartavel, com o trabalho por commitar desta arvore
copiado para dentro — uma prova que suja a arvore de quem a corre muda aquilo
que mede, e uma prova que so ve o ultimo commit nao prova o que esta no disco.
"""

import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ / "system-map" / "scripts"))
import generate_system_map as GEN  # noqa: E402

GERADOS = ("system-map/data/architecture.generated.json",
           "system-map/data/sources.generated.json",
           "system-map/data/state.generated.json",
           "italia-portale/client/system-map/state.generated.json")
NOMES = ("ramo-alfa", "servico-20260923-0923", "claude/um-nome-com-barra")

falhas: list[str] = []


def prova(id_: str, ok: bool, detalhe: str = ""):
    print(f"  {'PASS' if ok else 'FAIL':4s}  {id_:58s}{'' if ok else '  ' + detalhe}")
    if not ok:
        falhas.append(f"{id_}: {detalhe}")


def correr(cmd, cwd):
    return subprocess.run(cmd, cwd=str(cwd), capture_output=True, text=True,
                          encoding="utf-8", errors="replace")


def git(cwd, *a):
    r = correr(["git", "-c", "user.name=prova", "-c", "user.email=prova@local",
                *a], cwd)
    if r.returncode != 0:
        raise SystemExit(f"git {' '.join(a)} falhou: {r.stderr[-300:]}")
    return r.stdout


def clone_com_o_disco() -> Path:
    """Clone do HEAD + o que esta por commitar nesta arvore, commitado la."""
    d = Path(tempfile.mkdtemp(prefix="ramo-")) / "r"
    git(RAIZ, "clone", "-q", "--no-hardlinks", "--shared", str(RAIZ), str(d))
    for ln in git(RAIZ, "status", "--porcelain", "--untracked-files=all").splitlines():
        rel = ln[3:].split(" -> ")[-1].strip('"')
        src, dst = RAIZ / rel, d / rel
        if src.is_file():
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)
        elif dst.exists():
            dst.unlink()
    git(d, "add", "-A")
    git(d, "commit", "-q", "--allow-empty", "-m", "prova: a arvore do disco")
    return d


def sem_proveniencia(raiz: Path) -> dict:
    fora = {}
    for rel in GERADOS:
        dados = json.loads((raiz / rel).read_text(encoding="utf-8"))
        dados.pop("PROVENANCE", None)
        fora[rel] = json.dumps(dados, ensure_ascii=False, sort_keys=True)
    return fora


def validar(raiz: Path) -> tuple[bool, str]:
    r = correr([sys.executable, "system-map/scripts/validate_system_map.py"], raiz)
    saida = r.stdout + r.stderr
    p1 = re.search(r"^\s*(PASS|FAIL)\s+P1_SEM_DRIFT\b", saida, re.M)
    return (p1 is not None and p1.group(1) == "PASS"), saida


# ── 0 · o gerador e a tela dizem o mesmo ponteiro ───────────────────────────
mapa_js = (RAIZ / "system-map" / "app" / "map.js").read_text(encoding="utf-8")
prova("a_tela_conhece_o_ponteiro_do_gerador",
      f"const FACTO_DO_RAMO = '{GEN.FACTO_DO_RAMO}';" in mapa_js,
      "map.js nao declara o mesmo FACTO_DO_RAMO que generate_system_map.py")

# ── 1 · gerar uma vez, com um nome, e commitar ──────────────────────────────
r = clone_com_o_disco()
git(r, "checkout", "-q", "-b", "ramo-que-gerou")
x = correr([sys.executable, "system-map/scripts/correr_a_cadeia.py", "REGERAR"], r)
if x.returncode != 0:
    prova("a_cadeia_regera_no_clone", False, x.stderr[-300:])
    raise SystemExit(1)
git(r, "add", "-A")
git(r, "commit", "-q", "--allow-empty", "-m", "prova: mapa gerado em ramo-que-gerou")
commit = git(r, "rev-parse", "HEAD").strip()
estado = json.loads((r / GERADOS[2]).read_text(encoding="utf-8"))
consumidor = next(n for n in estado["NODES"] if n["id"] == "lineage_consumer")
prova("o_cartao_aponta_em_vez_de_carregar_o_nome",
      consumidor["facts"] == [GEN.FACTO_DO_RAMO], str(consumidor["facts"]))

# ── 2 · o MESMO commit, validado com tres nomes e em HEAD destacado ─────────
arquiteturas = {}
for nome in NOMES + (None,):
    git(r, "checkout", "-q", "--detach", commit) if nome is None else \
        git(r, "checkout", "-q", "-B", nome, commit)
    rotulo = nome or "HEAD-destacado"
    passou, saida = validar(r)
    detalhe = "\n".join(l for l in saida.splitlines()
                        if "P1_" in l or "primeira diferenca" in l or ".NODES[" in l)
    prova(f"p1_passa_com_o_checkout[{rotulo}]", passou, detalhe[:500])
    arquiteturas[rotulo] = sem_proveniencia(r)
    medido = json.loads((r / GERADOS[2]).read_text(encoding="utf-8"))["PROVENANCE"]
    esperado = "HEAD" if nome is None else nome
    prova(f"o_nome_continua_medido_em_PROVENANCE[{rotulo}]",
          medido.get("BRANCH") == esperado, f"BRANCH={medido.get('BRANCH')}")
    if nome is not None:
        vazou = [rel for rel, t in arquiteturas[rotulo].items() if nome in t]
        prova(f"o_nome_nao_vaza_para_fora_de_PROVENANCE[{rotulo}]", not vazou,
              ", ".join(vazou))
    git(r, "checkout", "-q", "--", ".")

base = arquiteturas[NOMES[0]]
for rotulo, a in arquiteturas.items():
    difere = [rel for rel in GERADOS if a[rel] != base[rel]]
    prova(f"a_arquitetura_e_a_mesma[{NOMES[0]}=={rotulo}]", not difere,
          ", ".join(difere))

# ── 3 · o validador continua a morder um drift REAL ─────────────────────────
# Mexe-se numa fonte rastreada e commita-se SEM regerar. E o caso que o P1
# existe para apanhar; se o conserto o tivesse desligado, isto passava.
git(r, "checkout", "-q", "-B", NOMES[0], commit)
alvo = r / "_gavetas.py"
alvo.write_text(alvo.read_text(encoding="utf-8") + "\n# mutacao: drift real\n",
                encoding="utf-8")
git(r, "commit", "-q", "-am", "prova: fonte mexida sem regerar")
passou, saida = validar(r)
prova("p1_reprova_uma_fonte_mexida_sem_regerar", not passou,
      "o validador deixou passar uma fonte mexida sem mapa regerado")
prova("o_drift_real_e_nomeado_pelo_ficheiro", "_gavetas.py" in saida or ".sha" in saida,
      "a reprovacao nao diz onde")

shutil.rmtree(r.parent, ignore_errors=True)
print()
if falhas:
    print(f"RAMO_NAO_ENTRA_NO_MAPA=FAIL · {len(falhas)} prova(s)")
    sys.exit(1)
print("RAMO_NAO_ENTRA_NO_MAPA=PASS")
