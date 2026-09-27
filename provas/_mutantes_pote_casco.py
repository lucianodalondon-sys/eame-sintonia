#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Mutacao do POTE UNICO (POTE-UNICO): o pote v2, o leitor do casco e a precedencia no portal.

    python3 provas/_mutantes_pote_casco.py

Cada mutante e plantado numa COPIA da arvore minima, numa pasta temporaria fora do repositorio, e la
corre tests/test_pote_intelligence_casco.py (que corre tambem tests/test_pote_no_casco.mjs). O
repositorio nao e tocado.

Um mutante MORTO e um teste que falhou por causa dele. Um VIVO e um defeito que os testes deixam passar,
e reprova esta prova (codigo de saida 1). Um que NAO_APLICOU (o texto-alvo nao existe uma vez so)
tambem reprova: mutante que nao se planta nao prova nada.
"""
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
POTE = "pacote/pote_intelligence_casco.py"
LEITOR = "italia-portale/client/sintonia-pote-casco.js"
PORTAL = "italia-portale/client/portale.html"
COPIAR = ("tests/test_pote_intelligence_casco.py", "tests/test_pote_no_casco.mjs",
          "tests/test_ponte_intelligence_casco.py",
          "tests/fixtures/pote/CORRIDA-SINTETICA-POTE.json", "tests/fixtures/pote/POTE-SINTETICO.json",
          "tests/fixtures/pote/POTE-SINTETICO-V2-UNICO.json",   # o .mjs le-o desde o POTE-V2-UNICO
          "italia-portale/audit/lib/harness.mjs", "italia-portale/client/.gitignore",
          "italia-portale/client/.vercelignore", ".vercelignore", ".gitignore",
          "italia-portale/client/_ds/adama-brandwell/styles.css")

M = [
    # ── o pote (Python) ──────────────────────────────────────────────────────
    ("Q1 oportunidade entra no Radar Futuro (especie nao conferida)",
     "    if especie not in admitidas:\n", "    if False:\n"),
    ("Q2 qualquer bloqueio de G0 passa por 'futuro por desenho'",
     '        return e.get("G0") == "BLOQUEADO_EM_G0" and list(e.get("G0_FALTA") or []) == [G0_FUTURO_POR_DESENHO]\n',
     '        return e.get("G0") == "BLOQUEADO_EM_G0"\n'),
    # Ajuste DECLARADO (POTE-V2-UNICO, 27/09): Q3, Q6, Q7 e Q8 miram o mesmo defeito no codigo novo
    # (a admissao passou a depender do USO — P7; a PROVA ganhou a base de URL/PUBLISHED_AT).
    ("Q3 P2/P5 de volta: o futuro bloqueado por desenho nao tem vaga",
     "    if especie == FUTURO:\n        def admite(e):\n", "    if False:\n        def admite(e):\n"),
    ("Q4 conferencia aceita vazio sem porque",
     '                v.append(f"{comp}: vazio sem o PORQUE")\n', "                pass\n"),
    ("Q5 rendimento provado por outra fonte aceite",
     "        if outras:\n", "        if False:\n"),
    ("Q6 P4 de volta: o valor fora do contrato some",
     '        "FORA_DO_CONTRATO": {k: _valor(dadas[k]) for k in sorted(dadas)\n',
     '        "FORA_DO_CONTRATO": {k: NAO_SEI for k in sorted(dadas)\n'),
    ("Q7 FACT_LOCATION vira REGION_ID",
     "    chaves = {k: _valor(dadas.get(k)) for k in contrato}\n    out = {\n",
     '    chaves = {k: _valor(dadas.get(k) or (dadas.get("FACT_LOCATION") if k == "REGION_ID" else None)) for k in contrato}\n    out = {\n'),
    ("Q8 publicacao vira tempo do facto",
     "        out[c] = _valor(v)\n        if c in CAMPOS_COM_BASE:\n",
     '        out[c] = _valor(p.get("PUBLICADO_EM") if c == "FACT_TIME" and e_ignorancia(v) else v)\n        if c in CAMPOS_COM_BASE:\n'),
    ("Q9 objeto sem especie vira OPORTUNIDADE (promocao)",
     '        return SINAL, "CONTRATO_V1"\n', '        return OPORTUNIDADE, "CONTRATO_V1"\n'),
    ("Q10 SOURCE_HEAD inventado quando falta",
     '        "SOURCE_HEAD": _valor(fonte.get("SOURCE_HEAD")),\n',
     '        "SOURCE_HEAD": fonte.get("SOURCE_HEAD") or "HEAD",\n'),
    ("Q11 escreve em qualquer sitio do portal",
     "    return rel.parts == DESTINO_NO_CASCO\n", "    return True\n"),
    ("Q12 payload v1 adulterado entra sem conferencia",
     '    if violacoes:\n        raise LeiViolada("o payload v1 reprova', '    if False:\n        raise LeiViolada("o payload v1 reprova'),
    ("Q13 o future da v1 cai no Radar Futuro",
     'DA_V1 = {"future": "archive",', 'DA_V1 = {"future": "future",'),
    ("Q14 duplicado conta duas vezes",
     "    if _id_do_objeto(o) in vistos:\n", "    if False:\n"),
    ("Q15 lacunas da corrida somem",
     '        "LACUNAS": [g for g in lacunas if nomes.get(g.get("FERRAMENTA"), g.get("FERRAMENTA")) == comp],\n',
     '        "LACUNAS": [],\n'),
    ("Q16 compartimento sem contrato desenha",
     '        if meta["CHAVES"] is None:\n            recusados += [_recusa(comp, o, SEM_CONTRATO) for o in objs]\n',
     '        if False:\n            recusados += [_recusa(comp, o, SEM_CONTRATO) for o in objs]\n'),
    ("Q17 o pote nao traz o CORTE",
     '        "CORTE": _valor(fonte.get("CORTE")),\n', ""),
    # ── o leitor do casco (JavaScript) ───────────────────────────────────────
    ("J1 futuro com a forma da oportunidade",
     "    FATO_PRESENTE_SOBRE_O_FUTURO: { bg: '#00698F', ink: '#FFFFFF', edge: '#00698F', traco: 'dashed' },\n",
     "    FATO_PRESENTE_SOBRE_O_FUTURO: { bg: '#009845', ink: '#FFFFFF', edge: 'rgba(0,152,69,0.55)', traco: 'solid' },\n",
     LEITOR),
    ("J2 o leitor reordena",
     "    var objs = (e.OBJETOS || []).map(", "    var objs = (e.OBJETOS || []).slice().reverse().map(", LEITOR),
    ("J3 NAO SEI sem destaque",
     "color: ns(v) ? '#F5B317' : '#FFFFFF'", "color: '#FFFFFF'", LEITOR),
    ("J4 pote recusado desenha na mesma",
     "    if (falhas.length) {\n", "    if (false) {\n", LEITOR),
    ("J5 o leitor nao olha a marca",
     "    if (p.MARCA !== MARCA || p.NAO_PARA_CLIENTE !== true) v.push(", "    if (false) v.push(", LEITOR),
    ("J6 URL javascript: vira link",
     "  function linkSeguro(u) { return typeof u === 'string' && /^https?:\\/\\//i.test(u); }\n",
     "  function linkSeguro(u) { return typeof u === 'string'; }\n", LEITOR),
    ("J7 o casco escolhe o compartimento pelo nome da vista",
     "      if (e && (e.VISTAS_DO_CASCO || []).indexOf(alvo) >= 0) return DOZE[i];\n",
     "      if (e && (DOZE[i] === alvo || (e.VISTAS_DO_CASCO || []).indexOf(alvo) >= 0)) return DOZE[i];\n", LEITOR),
    ("J8 o carregador pede o pote sem ?pote=local",
     "    if (!window.SINTONIA_POTE && /[?&]pote=local(?:&|$)/.test(window.location.search)) {\n",
     "    if (!window.SINTONIA_POTE) {\n", LEITOR),
    ("J9 o leitor esconde o compartimento vazio",
     "      vazio: objs.length === 0,", "      vazio: false,", LEITOR),
    # ── a precedencia no portal ──────────────────────────────────────────────
    ("H1 sem precedencia: legado e pote na mesma vista",
     "    if (pv) for (const k of Component.FLAGS_DO_LEGADO) v[k] = false;\n", "", PORTAL),
    ("H2 o Radar Futuro esquecido na precedencia",
     "  static FLAGS_DO_LEGADO = ['isMeeting', 'isRadarFuturo', ", "  static FLAGS_DO_LEGADO = ['isMeeting', ", PORTAL),
    ("H3 o bloco do pote sem a faixa EXPERIMENTAL",
     '      <div data-marca="1" style="border-radius:10px;background:#000;color:#fff;padding:9px 14px;font-size:11px;font-weight:700;letter-spacing:0.08em">{{ pote.faixa }}</div>\n',
     "", PORTAL),
]


def correr(pasta: Path) -> subprocess.CompletedProcess:
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1", PYTHONUTF8="1",
               HTTP_PROXY="http://127.0.0.1:9", HTTPS_PROXY="http://127.0.0.1:9")
    return subprocess.run([sys.executable, "-m", "unittest", "tests.test_pote_intelligence_casco"],
                          cwd=pasta, capture_output=True, text=True, encoding="utf-8",
                          errors="replace", env=env, timeout=900)


def main() -> int:
    alvos = {POTE, LEITOR, PORTAL}
    originais = {a: (RAIZ / a).read_text(encoding="utf-8") for a in alvos}
    vivos, nao_aplicou = [], []
    with tempfile.TemporaryDirectory() as d:
        pasta = Path(d)
        pys = subprocess.run(["git", "-C", str(RAIZ), "ls-files", "*.py"], capture_output=True,
                             text=True, encoding="utf-8").stdout.split()
        cliente = [str(p.relative_to(RAIZ)) for p in (RAIZ / "italia-portale" / "client").glob("*.js")]
        for rel in sorted(set(COPIAR) | set(pys) | set(cliente) | alvos):
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
