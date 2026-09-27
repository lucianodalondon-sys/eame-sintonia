"""Mutacao REFERENCIA-MANUTENCAO (D116 + D117, dono, 27/09).

Cada mutante planta UM defeito no codigo desta missao; o teste nomeado tem de ficar
VERMELHO; o ficheiro volta ao original (sha256 conferido). Os tres que o dono nomeou:
sobrescrever a edicao antiga, inventar cultura, pular a revogacao — e os da cadencia e
do frescor, que sao a outra metade da missao.

uso: python3 provas/mutacao_referencia_manutencao.py      (numa copia/worktree limpa)
"""
import hashlib
import os
import subprocess
import sys
from pathlib import Path

R = Path(__file__).resolve().parents[1]
DIFF = R / "coleta" / "it" / "edicoes_do_registro.py"
FRE = R / "leis" / "frescor_da_referencia.py"
CAD = R / "regras" / "cadencia_da_referencia.mjs"
RUN = R / "coleta" / "italy_recurrent_collect.mjs"
T_DIFF = [sys.executable, "tests/test_edicoes_do_registro.py"]
T_FRE = [sys.executable, "tests/test_frescor_da_referencia.py"]
T_CAD = ["node", "regras/cadencia_da_referencia_test.mjs"]

MUTANTES = [
    # ── os tres do dono ────────────────────────────────────────────────────
    ("S1 sobrescrever: o diff guardado passa a ser reescrito", DIFF,
     "        fd = os.open(caminho, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o644)\n",
     "        fd = os.open(caminho, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o644)\n", T_DIFF),
    ("S2 sobrescrever: a biblioteca guarda uma edicao por FONTE (a nova apaga a antiga)", DIFF,
     "        e = ed.setdefault(doc, {", "        e = ed.setdefault(SOURCE_ID, {", T_DIFF),
    ("C1 inventar cultura: o nome do produto volta a 1.a linha do texto", DIFF,
     '             "%s nel campo %s tra le edizioni %s e %s.\\n"',
     '             "%s nel campo %s tra le edizioni %s e %s. " + m["PRODUTO"] + "\\n"', T_DIFF),
    ("C2 inventar cultura: CULTURA_ALVO lida do nome do produto", DIFF,
     '        "CULTURA_ALVO": CULTURA_ALVO,\n',
     '        "CULTURA_ALVO": ("vite" if "VITE" in ((linha_nova or {}).get("denominazione_prodotto") or "") else CULTURA_ALVO),\n',
     T_DIFF),
    ("R1 pular a revogacao: stato_amministrativo deixa de ser comparado", DIFF,
     "            if antes == depois:\n                continue\n",
     "            if antes == depois or campo == \"stato_amministrativo\":\n                continue\n", T_DIFF),
    ("R2 revogacao datada pela EDICAO e nao pelo decreto", DIFF,
     '        for c in ("data_decreto_revoca", "data_decorrenza_revoca"):\n            d = data_iso(linha_nova.get(c))\n',
     '        for c in ("data_decreto_revoca", "data_decorrenza_revoca"):\n            d = "2026-09-21"\n', T_DIFF),
    ("R3 sair do ficheiro vira revogacao", DIFF,
     '            mud.append(_mudanca(num, CHAVE, num, None, "REGISTRATION_LEFT_THE_LIST", a, b, la,\n                                "UNRESOLVED",',
     '            mud.append(_mudanca(num, "stato_amministrativo", "Autorizzato", "Revocato", "STATUS_CHANGE", a, b, la,\n                                "CONFIRMED",',
     T_DIFF),
    # ── frescor ────────────────────────────────────────────────────────────
    ("F1 frescor contado desde a EDICAO", FRE,
     "    dias = (h - ck).days\n", "    dias = (h - (ed or ck)).days\n", T_FRE),
    ("F2 limiar de 14 dias vira «mais de 14»", FRE,
     "    if dias >= DIAS_PODE_ESTAR_DESATUALIZADO:\n", "    if dias > DIAS_PODE_ESTAR_DESATUALIZADO:\n", T_FRE),
    ("F3 FAILED conta como checagem", FRE,
     "        if o.get(\"HEALTH_STATE\") != SAUDAVEL:\n            continue\n", "", T_FRE),
    ("F4 sem checagem vira EM_DIA", FRE,
     "        return dict(base, DIAS_DESDE_A_CHECAGEM=NAO_SEI, ESTADO_FRESCOR=ESTADO_NAO_SEI,",
     "        return dict(base, DIAS_DESDE_A_CHECAGEM=NAO_SEI, ESTADO_FRESCOR=EM_DIA,", T_FRE),
    # ── cadencia ───────────────────────────────────────────────────────────
    ("K1 sem retentativa na quarta/quinta", CAD,
     "  const ehRetentativa = retentar.some(", "  const ehRetentativa = false && retentar.some(", T_CAD),
    ("K2 o alerta morre fora da janela", CAD,
     "  return { DEVIDA: false, TENTATIVA: null, ALERTA: alerta,\n           PORQUE: `fora da janela",
     "  return { DEVIDA: false, TENTATIVA: null, ALERTA: null,\n           PORQUE: `fora da janela", T_CAD),
    ("K3 a rotacao ignora o teto do dominio", CAD,
     "  const cabe = Math.max(0, Math.min(cad.MAX_POR_DIA, teto - jaGastos - reservaRobots));",
     "  const cabe = cad.MAX_POR_DIA;", T_CAD),
    ("K4 sem leitura de checagem, a cadencia adivinha e colhe", CAD,
     "    if (checagens == null) { foraDaCadencia[id] =",
     "    if (checagens == null) { aColher.push(id); continue; foraDaCadencia[id] =", T_CAD),
    ("K5 o corredor deixa de aplicar a cadencia", RUN,
     "      aColher = cad.aColher;\n", "", T_CAD),
]


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


env = dict(os.environ, PYTHONUTF8="1", PYTHONDONTWRITEBYTECODE="1",
           HTTPS_PROXY="http://127.0.0.1:9", HTTP_PROXY="http://127.0.0.1:9")
mortos, vivos = 0, []
for nome, f, de, para, teste in MUTANTES:
    orig = f.read_bytes()
    h = sha(f)
    txt = orig.decode("utf-8")
    if txt.count(de) != 1:
        print("✗ %s: trecho a mutar aparece %d vezes — mutante invalido" % (nome, txt.count(de)))
        vivos.append(nome)
        continue
    f.write_bytes(txt.replace(de, para).encode("utf-8"))
    try:
        r = subprocess.run(teste, cwd=R, capture_output=True, text=True, encoding="utf-8", env=env, timeout=600)
    finally:
        f.write_bytes(orig)
    assert sha(f) == h, "o ficheiro nao voltou ao original: %s" % f
    if r.returncode != 0:
        mortos += 1
        print("✓ MORTO  %s  (%s)" % (nome, " ".join(teste[-1:])))
    else:
        vivos.append(nome)
        print("✗ VIVO   %s  — nenhum teste reprovou" % nome)
print("\nMUTANTES %d · MORTOS %d · VIVOS %d%s" % (len(MUTANTES), mortos, len(vivos),
                                              (" -> " + "; ".join(vivos)) if vivos else ""))
sys.exit(1 if vivos else 0)
