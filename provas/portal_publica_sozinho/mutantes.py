#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Mutacao do PORTAL-PUBLICA-SOZINHO (D126): o publicador, o leitor do casco e o portale.html.

    python3 provas/portal_publica_sozinho/mutantes.py [saida.json]

Cada mutante e plantado numa COPIA da arvore (git worktree do HEAD, numa pasta temporaria fora do
repositorio), e la corre tests/test_publicar_portal_sozinho.py. O repositorio nao e tocado.

MORTO = algum teste caiu por causa dele. VIVO = defeito que os testes deixam passar (reprova esta prova,
codigo 1). NAO_APLICOU = o texto-alvo nao existe uma vez so (tambem reprova: mutante que nao se planta
nao prova nada).

Os quatro defeitos que a missao nomeia estao aqui (pote invalido, gate falhado, pagina no ar sem contagem,
rollback que nao roda) — e tambem como TESTES de comportamento em P3 (implantadores com o defeito).
"""
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
PUB = "portoes/publicar_portal_sozinho.py"
LEITOR = "italia-portale/client/sintonia-pote-casco.js"
PORTAL = "italia-portale/client/portale.html"

M = [
    # ── o pote (C0) ──────────────────────────────────────────────────────────
    ("M01 pote invalido: o validador v2 e ignorado", PUB,
     'L.append(linha("C0_POTE_V2_FORMA_E_LEI", not v,', 'L.append(linha("C0_POTE_V2_FORMA_E_LEI", True,'),
    ("M02 prova sem DOCUMENT_ID aceite", PUB,
     'for c in ("ITEM_ID", "RAW_OBSERVATION_ID", "SOURCE_ID", "DOCUMENT_ID"):', 'for c in ("ITEM_ID",):'),
    ("M03 D123 desligada", PUB, 'if o.get("ESPECIE") == "OPORTUNIDADE":', 'if False:'),
    ("M04 D123 esquece a bula", PUB,
     '(("ADAMA_PRODUCT_ID", "produto"), ("AUTHORIZATION_EVIDENCE_ID", "bula"))', '(("ADAMA_PRODUCT_ID", "produto"),)'),
    ("M05 D122 aceita evento sem data", PUB,
     r're.match(r"^\d{4}-(0[1-9]|1[0-2])(-\d{2})?\b", ft)', 're.match(r".*", str(ft))'),
    ("M06 dado cru: chave proibida aceite", PUB, 'if str(kk).upper() in proibidas:', 'if False:'),
    ("M07 dado cru: texto longo aceite", PUB, 'len(x) > limite:', 'len(x) > limite * 1000:'),
    ("M08 demo vai a producao", PUB,
     'L.append(linha("C0_NADA_DA_DEMO", not achados,', 'L.append(linha("C0_NADA_DA_DEMO", True,'),
    ("M09 promocao sem o dono", PUB, 'L.append(linha("C0_PROMOCAO", aprovada,', 'L.append(linha("C0_PROMOCAO", True,'),
    ("M10 aprovacao sem nome vale", PUB, ' and _sabido(prom.get("APROVADA_POR"))', ''),
    ("M11 o sha do pote depende da ordem", PUB, 'json.dumps(pote, sort_keys=True,', 'json.dumps(pote, sort_keys=False,'),
    # ── as telas (C5/C6) ─────────────────────────────────────────────────────
    ("M12 pagina sem a contagem: contagem ignorada", PUB, 'if t in esp and m.get("POTE_OBJETOS") != esp[t]:', 'if False:'),
    ("M13 tela sem o pote aceite", PUB, 'if not m.get("POTE_NA_TELA"):', 'if False:'),
    ("M14 SHA servido ignorado", PUB, 'if env.get("POTE_SHA256") != sha:', 'if False:'),
    ("M15 D122: legado visivel ignorado", PUB, '            if m.get(c) != 0:', '            if False:'),
    ("M16 D122: detector vazio vale zero", PUB,
     'if t in contrato["TELAS"]["DO_POTE"] and not m.get("LEGADO_43_UNIVERSO"):', 'if False:'),
    ("M17 D122: barra com o numero antigo", PUB, 'if v in esp and str(n) != str(esp[v]):', 'if False:'),
    ("M18 medicao incompleta autoriza", PUB, 'if not contagens or not contagens.get("MEDICAO_COMPLETA"):', 'if False:'),
    ("M19 envelope no ar incoerente aceite", PUB,
     'if not isinstance(pote, dict) or sha_do_pote(pote) != env.get("POTE_SHA256"):', 'if False:'),
    # ── o release (C3) ───────────────────────────────────────────────────────
    ("M20 gate falhado: vermelho novo do release aceite", PUB, 'if chegou and ids and not novos:', 'if chegou and ids:'),
    ("M21 release que nao chegou ao fim aceite", PUB, 'if chegou and ids and not novos:', 'if ids and not novos:'),
    ("M22 release ilegivel nao reprova", PUB,
     '    if rc != 0:\n        return None, f"nao consegui ler', '    if False:\n        return None, f"nao consegui ler'),
    ("M23 instalar o browser vira conferencia", PUB,
     'if "run" in st and st.get("name") not in fora:', 'if "run" in st:'),
    ("M24 comando que falha passa", PUB, '    if rc == 0:\n        return linha(ident, True,', '    if True:\n        return linha(ident, True,'),
    # ── a decisao ────────────────────────────────────────────────────────────
    ("M25 gate do pote falhado e ainda assim publica", PUB,
     '        if _falhou(L0):\n            return fim("BLOQUEADO", BLOQUEADO)', '        if False:\n            return fim("BLOQUEADO", BLOQUEADO)'),
    ("M26 gate do codigo falhado e ainda assim publica", PUB,
     '            if _falhou(Lc):\n                return fim("BLOQUEADO", BLOQUEADO)', '            if False:\n                return fim("BLOQUEADO", BLOQUEADO)'),
    ("M27 republica o que ja esta no ar", PUB, 'if sha_antes == sha and self.modo != "preview":', 'if False:'),
    ("M28 producao pelo anfitriao de ensaio", PUB, 'if self.modo == "producao" and not self.imp.publica_de_verdade:', 'if False:'),
    ("M29 rollback que nao roda: nunca se chama a volta", PUB, 'voltou = self.imp.voltar(anterior)', 'voltou = True'),
    ("M30 rollback provado so pelo SHA", PUB,
     'provada = (bool(voltou) and depois.get("ID") == anterior.get("ID") and', 'provada = (bool(voltou) and'),
    ("M31 reverteu sem ALERTA", PUB,
     '_alerta(self.registro, {"QUANDO": R["INICIO"], "TIPO": "REVERTIDO" if provada',
     '(lambda *a: None)(self.registro, {"QUANDO": R["INICIO"], "TIPO": "REVERTIDO" if provada'),
    ("M32 deriva no ar sem ALERTA", PUB, 'if ultima and ultima.get("POTE_SHA256") != sha_antes:', 'if False:'),
    ("M33 o revertido vira a ULTIMA publicacao", PUB,
     '            if not _falhou(L6):\n                if self.modo != "preview":',
     '            if True:\n                if self.modo != "preview":'),
    # ── o casco ──────────────────────────────────────────────────────────────
    ("M34 o casco ignora o pote publicado", LEITOR,
     "if (!window.SINTONIA_POTE && !window.SINTONIA_POTE_PEDIDO && PUB && typeof PUB === 'object' && PUB.POTE) {",
     "if (false) {"),
    ("M35 o publicado atropela o ?pote=local", LEITOR, "!window.SINTONIA_POTE_PEDIDO && PUB &&", "PUB &&"),
    ("M36 pote que reprova devolve a barra ao legado", LEITOR,
     "if (!p || conferir(p).length) return NAO_SEI;", "if (!p || conferir(p).length) return null;"),
    ("M37 field volta a mostrar a demo", LEITOR, "    if (!k) k = soOPorque(p, view);\n", ""),
    ("M38 a barra conta o pote na sala", LEITOR, "    if (FERRAMENTAS.indexOf(ROTA[view] || view) < 0) return null;\n", ""),
    ("M39 a barra volta ao numero antigo", PORTAL,
     "count: poteConta(n[0], n[2]), go: () => n[0] === 'competitors'", "count: n[2], go: () => n[0] === 'competitors'"),
    ("M40 field fora da precedencia", PORTAL, "'isSources', 'isField'];", "'isSources'];"),
    ("M41 o portal nao carrega o pote publicado", PORTAL, '<script src="sintonia-pote-publicado.js"></script>\n', ''),
    ("M42 o registo entra no Git", ".gitignore", "PUBLICACOES/\n", ""),
    ("M43 D122: a caixa «oggi» do legado aceite", PUB, 'and m.get("OGGI_LEGADO") is not False:', 'and False:'),
    ("M44 a caixa «oggi» fica com o pote", PORTAL,
     "oggiDoLegado: !(typeof window !== 'undefined' && window.SINTONIA_POTE_PEDIDO === true),", "oggiDoLegado: true,"),
]


def git(args, cwd=RAIZ):
    return subprocess.run(["git"] + args, cwd=str(cwd), capture_output=True, text=True)


def main():
    saida = Path(sys.argv[1]) if len(sys.argv) > 1 else None
    tmp = Path(tempfile.mkdtemp(prefix="mutantes-publica-"))
    copia = tmp / "arvore"
    r = git(["worktree", "add", "--detach", str(copia), "HEAD"])
    if r.returncode:
        print(r.stderr)
        return 2
    res = []
    try:
        base = subprocess.run([sys.executable, "-m", "unittest", "tests.test_publicar_portal_sozinho"], cwd=copia,
                              capture_output=True, text=True, timeout=900)
        if base.returncode:
            print("a bateria nao esta verde SEM mutante — nada se mede:\n" + base.stderr[-1500:])
            return 2
        for nome, f, velho, novo in M:
            alvo = copia / f
            txt = alvo.read_text(encoding="utf-8")
            if txt.count(velho) != 1:
                res.append({"MUTANTE": nome, "ESTADO": "NAO_APLICOU", "OCORRENCIAS": txt.count(velho)})
                print(f"  NAO_APLICOU  {nome}  ({txt.count(velho)} ocorrencias)")
                continue
            alvo.write_text(txt.replace(velho, novo), encoding="utf-8")
            try:
                p = subprocess.run([sys.executable, "-m", "unittest", "tests.test_publicar_portal_sozinho"], cwd=copia,
                                   capture_output=True, text=True, timeout=900)
                morto = p.returncode != 0
                quem = sorted({l.split(" ")[1] for l in p.stderr.splitlines() if l.startswith(("FAIL:", "ERROR:"))})
            except subprocess.TimeoutExpired:
                morto, quem = True, ["<TIMEOUT>"]
            finally:
                alvo.write_text(txt, encoding="utf-8")
            res.append({"MUTANTE": nome, "ESTADO": "MORTO" if morto else "VIVO", "APANHADO_POR": quem[:6]})
            print(f"  {'MORTO' if morto else 'VIVO '}  {nome}  <- {', '.join(quem[:3])}")
    finally:
        git(["worktree", "remove", "--force", str(copia)])
        shutil.rmtree(tmp, ignore_errors=True)
        git(["worktree", "prune"])
    mortos = sum(1 for x in res if x["ESTADO"] == "MORTO")
    print(f"\nMUTACAO PORTAL-PUBLICA-SOZINHO: {mortos}/{len(M)} mortos")
    if saida:
        saida.write_text(json.dumps({"HEAD": git(["rev-parse", "HEAD"]).stdout.strip(), "MORTOS": mortos,
                                     "TOTAL": len(M), "MUTANTES": res}, ensure_ascii=False, indent=1), encoding="utf-8")
    return 0 if mortos == len(M) else 1


if __name__ == "__main__":
    sys.exit(main())
