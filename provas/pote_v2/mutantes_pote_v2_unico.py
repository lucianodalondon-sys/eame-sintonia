#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Mutacao do POTE-V2-UNICO: o contrato unico (gerador + validador + schema), P7, P8, D112 e o casco.

    python3 provas/pote_v2/mutantes_pote_v2_unico.py

Cada mutante e plantado numa COPIA da arvore minima, numa pasta temporaria fora do repositorio, e la
correm tests/test_pote_v2_unico.py e tests/test_pote_intelligence_casco.py (que corre
tests/test_pote_no_casco.mjs). O repositorio nao e tocado.

MORTO = algum teste caiu por causa dele. VIVO = defeito que os testes deixam passar (reprova esta prova,
codigo 1). NAO_APLICOU = o texto-alvo nao existe uma vez so (tambem reprova: mutante que nao se planta
nao prova nada).
"""
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
POTE = "pacote/pote_intelligence_casco.py"
VALIDADOR = "pacote/validar_pote_v2.py"
SCHEMA = "docs/intelligence/pote-v2/POTE_INTELLIGENCE_CASCO-v2.schema.json"
LEITOR = "italia-portale/client/sintonia-pote-casco.js"
PORTAL = "italia-portale/client/portale.html"
COPIAR = ("tests/test_pote_v2_unico.py", "tests/test_pote_intelligence_casco.py", "tests/test_pote_no_casco.mjs",
          "tests/test_ponte_intelligence_casco.py", "docs/intelligence/pote-v2/CONTRATO-POTE-V2.md",
          "provas/pote_v2/medir_recusas_r6.py",
          "italia-portale/audit/lib/harness.mjs", "italia-portale/client/.gitignore",
          "italia-portale/client/.vercelignore", ".vercelignore", ".gitignore",
          "italia-portale/client/_ds/adama-brandwell/styles.css")

M = [
    # ── o contrato: uma corrida, no topo ──────────────────────────────────────
    ("V1 sem run id no topo: o validador aceita",
     '    if e_ignorancia(pote.get("INTELLIGENCE_RUN_ID")):\n        v.append(',
     '    if False:\n        v.append('),
    ("V2 run id lido de CABECALHO sem declarar a leitura",
     "            leituras.append(f\"{c} lido de CABECALHO", "            (f\"{c} lido de CABECALHO"),
    ("V3 topo e CABECALHO divergentes viram uma corrida so",
     "        if not e_ignorancia(v) and not e_ignorancia(w) and v != w:\n",
     "        if False:\n"),
    # ── a prova: URL e PUBLISHED_AT, ou NAO SEI com a base ───────────────────
    ("V4 prova sem URL / NAO SEI sem base passa no validador",
     "                        if p.get(k) == NAO_SEI and e_ignorancia(p.get(k + \"_BASE\")):\n",
     "                        if False:\n"),
    ("V5 NAO SEI sem porque: a base some",
     "            out[c + \"_BASE\"] = base or (dita if not e_ignorancia(dita) else\n",
     "            out[c + \"_BASE\"] = base or (dita if False else NAO_SEI) or (NAO_SEI if 0 else\n"),
    ("V6 publicacao vira tempo do facto",
     '"COLHIDO_EM": ("COLHIDO_EM",), "FACT_TIME": ("FACT_TIME",)}',
     '"COLHIDO_EM": ("COLHIDO_EM",), "FACT_TIME": ("FACT_TIME", "PUBLICATION_TIME", "PUBLICADO_EM")}'),
    ("V7 o schema deixa de pedir a base da URL",
     '"URL", "URL_BASE",\n', '"URL",\n', SCHEMA),
    # ── P8: sinal solto nunca e mudanca de mercado ───────────────────────────
    ("V8 sinal solto como mudanca: um ponto basta",
     "    if len(pontos) != len(serie) or len(pontos) < 2:\n", "    if len(pontos) != len(serie) or len(pontos) < 1:\n"),
    ("V9 unidades diferentes comparadas",
     "    if len(unidades) != 1:\n", "    if False:\n"),
    ("V10 afirmar mudanca sem serie: aceite",
     "    if _afirma_mudanca(o) and ler_serie(o)[0] != SERIE_MEDIDA:\n", "    if False:\n"),
    ("V11 validador aceita sinal solto dito SERIE_MEDIDA",
     "                elif m[\"LEITURA\"] == SERIE_MEDIDA and ler_serie(", "                elif False and ler_serie("),
    # ── P7: o tempo so para quem o usa ───────────────────────────────────────
    ("V12 recusa por falta de tempo em uso que nao exige tempo",
     "    if not uso_exige_tempo(especie, o or {}):\n", "    if False:\n"),
    ("V13 o Registro volta a depender do tempo",
     "    if especie == RENDIMENTO:\n        return False\n", "    if especie == RENDIMENTO:\n        return True\n"),
    ("V14 todo uso dispensa o tempo",
     "            return False\n    return True\n", "            return False\n    return False\n"),
    ("V15 proveniencia dispensada (so_tempo aceita tudo)",
     "    return bool(falta) and all(f == \"FACT_TIME\" or f.startswith(\"FACT_TIME:\") for f in falta)\n",
     "    return True\n"),
    ("V16 oportunidade pode ser «nao»",
     "_PODEM_SER_HONESTAS = (SINAL, CROSSING, FINDING)", "_PODEM_SER_HONESTAS = (SINAL, CROSSING, FINDING, OPORTUNIDADE)"),
    ("V17 validador aceita item sem tempo num uso temporal",
     "                    elif adm == \"USO_SEM_TEMPO\" and uso_exige_tempo(", "                    elif False and uso_exige_tempo("),
    # ── D112 ─────────────────────────────────────────────────────────────────
    ("V18 lugar da fonte vira lugar do facto",
     "    if not e_ignorancia(ls) and normal(ls) in LOCATION_SOURCE_PROIBIDA:\n        return (",
     "    if False:\n        return ("),
    ("V19 lugar do facto sem LOCATION_SOURCE a vista",
     '    if not e_ignorancia(lugar) and "LOCATION_SOURCE" not in out:\n        out["LOCATION_SOURCE"] = NAO_SEI\n', ""),
    # ── o casco ──────────────────────────────────────────────────────────────
    ("K1 leitor: sinal solto chamado variazione",
     "      : T.solto + ' · ' + txt(m.PORQUE));", "      : T.serie + ' · ' + txt(m.PORQUE));", LEITOR),
    ("K2 leitor aceita um ponto como serie",
     "    if (!s || !s.length || s.length < 2) return false;", "    if (!s || !s.length) return false;", LEITOR),
    ("K3 pote pedido e ausente: o legado volta",
     "      if (!pedido || FERRAMENTAS.indexOf(ROTA[view] || view) < 0) return null;", "      return null;", LEITOR),
    ("K4 leitor aceita URL NAO SEI sem base",
     "            else if (ns(p[c]) && (!p[c + '_BASE'] || ns(p[c + '_BASE']))) v.push(", "            else if (false) v.push(", LEITOR),
    ("K5 leitor aceita item sem tempo num uso temporal",
     "          if (p.ADMITIDA_POR === 'USO_SEM_TEMPO' && o.USO_EXIGE_TEMPO !== false) v.push(", "          if (false) v.push(", LEITOR),
    ("K6 portal: o leitor so e chamado com pote (o «pedido e ausente» cai no legado)",
     "    const pv = P ? P.vm(W.SINTONIA_POTE || null, this.state.view, this.state.lang) : null;",
     "    const pv = (P && W.SINTONIA_POTE) ? P.vm(W.SINTONIA_POTE, this.state.view, this.state.lang) : null;", PORTAL),
]


def correr(pasta: Path) -> subprocess.CompletedProcess:
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1", PYTHONUTF8="1",
               HTTP_PROXY="http://127.0.0.1:9", HTTPS_PROXY="http://127.0.0.1:9")
    return subprocess.run([sys.executable, "-m", "unittest", "tests.test_pote_v2_unico",
                           "tests.test_pote_intelligence_casco"],
                          cwd=pasta, capture_output=True, text=True, encoding="utf-8",
                          errors="replace", env=env, timeout=900)


def main() -> int:
    alvos = {POTE, VALIDADOR, SCHEMA, LEITOR, PORTAL}
    originais = {a: (RAIZ / a).read_text(encoding="utf-8") for a in alvos}
    vivos, nao_aplicou = [], []
    with tempfile.TemporaryDirectory() as d:
        pasta = Path(d)
        pys = subprocess.run(["git", "-C", str(RAIZ), "ls-files", "*.py"], capture_output=True,
                             text=True, encoding="utf-8").stdout.split()
        cliente = [str(p.relative_to(RAIZ)) for p in (RAIZ / "italia-portale" / "client").glob("*.js")]
        fixtures = [str(p.relative_to(RAIZ)) for p in (RAIZ / "tests" / "fixtures" / "pote").glob("*.json")]
        for rel in sorted(set(COPIAR) | set(pys) | set(cliente) | set(fixtures) | alvos):
            if not (RAIZ / rel).is_file():
                continue
            (pasta / rel).parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(RAIZ / rel, pasta / rel)
        subprocess.run(["git", "init", "-q", str(pasta)], check=True)   # o teste J3 pergunta ao git
        base = correr(pasta)
        if base.returncode != 0:
            print("BASE VERMELHA na copia — a prova nao vale:\n" + base.stderr[-3000:])
            return 2
        print("base: verde na copia")
        for nome, a, b, *alvo in M:
            alvo = alvo[0] if alvo else POTE
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
