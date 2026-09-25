"""D61/D62/D69 — mutacao das regras novas de data e lugar do boletim. Cada mutante numa COPIA da arvore (sem
data/, portal, mapa, .git), sem .pyc (PYTHONDONTWRITEBYTECODE); a copia SEM mutacao tem de ficar VERDE primeiro.
Cada mutante corre as provas que o apanham: o teste do motor, os testes do Curator e — para o coletor — a
prova local do coletor de verdade (servidor 127.0.0.1, rede de fora fechada). O mutante tem de ser MORTO.
uso: py provas/boletins_data_local/mutacao_d61.py"""
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
MOTOR = ["node", "regras/boletim_data_local_test.mjs"]
CURADOR = [sys.executable, "-m", "unittest", "test_boletim_data_local", "test_receita_identidade"]
COLETOR = ["node", "provas/boletins_data_local/boletim_pdf_local.mjs"]
M, C, P, V, K = "regras/motor_de_rota.mjs", "curadoria/canario.py", "curadoria/reparar_contrato.py", "curadoria/validar_contratos.py", "coleta/italy_pilot_collect.mjs"
MUTANTES = [
    ("motor: D69 deixa a validade entrar no FACT_TIME", M,
     'if (campo === "FACT_TIME" && spec.FACT_TIME != null && !(Array.isArray(base) ? base : [base]).every((b) => String(b).startsWith(FACT_TIME_LIGADO))) {',
     'if (false) {', [MOTOR]),
    ("motor: aceita qualquer texto como data", M,
     "  if (!/^\\d{4}-\\d{2}-\\d{2}$/.test(iso)) return false;", "  return true;", [MOTOR]),
    ("motor: intervalo ao contrario passa", M,
     "    else if (partes.length === 2 && partes[0] > partes[1]) invalido = `«${valor}» começa depois de acabar`;", "", [MOTOR]),
    ("motor: captura ausente nao da NAO SEI", M, "  if (faltam.length) {", "  if (false) {", [MOTOR]),
    ("motor: data a ler captura obrigatoria passa (D62)", M, "      if (caps[m[1]].REQUIRED !== false) {", "      if (false) {", [MOTOR]),
    ("motor: o FACT_TIME nao diz onde ficou o periodo (D69)", M,
     "    if (saida.FACT_TIME === NAO_SEI && saida.BULLETIN_PERIOD !== NAO_SEI) {", "    if (false) {", [MOTOR]),
    ("motor: MES_IT aceita qualquer mes", M,
     'MES_IT: (v) => { const i = MESES_IT.indexOf(String(v).toLowerCase()); return i < 0 ? null : String(i + 1).padStart(2, "0"); },',
     'MES_IT: (v) => "01",', [MOTOR]),
    ("motor: so a 1.a forma de cada campo", M, "  for (const [k, molde] of moldes.entries()) {",
     "  for (const [k, molde] of moldes.slice(0, 1).entries()) {", [MOTOR]),
    ("porta: PDF sem .pdf sem o porque passa", P, "            if not (isinstance(sem_ext, str) and sem_ext.strip()):",
     "            if False:", [CURADOR]),
    ("validador: sem FACT_TIME nem base passa", V,
     '    if "FACT_TIME" not in idt and not str(idt.get("FACT_TIME_BASIS") or "").strip():', "    if False:", [CURADOR]),
    ("canario: boletim HTML nao pergunta ao motor", C, "    if declara_data_e_lugar(c):", "    if False:", [CURADOR]),
    ("coletor: sem leitor PDF_TEXT", K, "      PDF_TEXT: () => textoDePdf(buf, STORE),", "", [COLETOR]),
    ("coletor: data e lugar nao vao para a ficha", K, "        ...(ident.PUBLISHED_AT_BASIS ? {", "        ...(false ? {", [COLETOR]),
    # DA-13 · o texto do link do indice (BASE INDICE)
    ("DA-13 motor: LINK_TEXT sempre vazio", M,
     '    if (de === "LINK_TEXT") return String(alvo.textoDaLigacao || "");', '    if (de === "LINK_TEXT") return "";', [MOTOR, CURADOR]),
    ("DA-13 motor: os alvos nao levam o texto do link", M,
     'for (const a of as) a.textoDaLigacao = textos.get(a.url) ?? "";', "for (const a of as) void a;", [COLETOR]),
    ("DA-13 motor: a base por forma e ignorada", M,
     "  const baseDe = (k) => (Array.isArray(baseDeclarada) ? baseDeclarada[k] : baseDeclarada);",
     "  const baseDe = (k) => (Array.isArray(baseDeclarada) ? baseDeclarada[0] : baseDeclarada);", [MOTOR]),
    ("DA-13 canario: nao passa o link ao motor", C,
     'textos_das_ligacoes(b, aq["INDEX_URL"], aq.get("STRIP_SUFFIX")).get(alvo, ""))', '"")', [CURADOR]),
]
FORA = {".git", "data", "italia-portale", "system-map", "build", "docs", "node_modules"}


def copia():
    tmp = Path(tempfile.mkdtemp(prefix="mut_d61_"))
    for d in RAIZ.iterdir():
        if d.name in FORA:
            continue
        if d.is_dir():
            shutil.copytree(d, tmp / d.name, ignore=shutil.ignore_patterns("__pycache__", "node_modules"))
        else:
            shutil.copy2(d, tmp / d.name)
    return tmp


def correr(tmp, cmds):
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1", NODE_DISABLE_COMPILE_CACHE="1")
    saidas = []
    for cmd in cmds:
        cwd = tmp / "curadoria" if cmd is CURADOR else tmp
        r = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, encoding="utf-8", errors="replace", env=env, timeout=900)
        saidas.append((r.returncode, (r.stdout + r.stderr)[-1500:]))
    return saidas


tmp = copia()
try:
    base = correr(tmp, [MOTOR, CURADOR, COLETOR])
finally:
    shutil.rmtree(tmp, ignore_errors=True)
if any(rc for rc, _ in base):
    for rc, out in base:
        print(rc, out[-600:])
    sys.exit("a copia sem mutacao nao passa: a medicao nao vale")
print("BASE VERDE (motor, curador, coletor)")
mortos = 0
for nome, f, de, para, cmds in MUTANTES:
    tmp = copia()
    try:
        alvo = tmp / f
        s = alvo.read_text(encoding="utf-8")
        assert s.count(de) == 1, (nome, s.count(de))
        alvo.write_text(s.replace(de, para), encoding="utf-8", newline="\n")
        res = correr(tmp, cmds)
        erros = sorted({e for _, out in res for e in re.findall(r"(ModuleNotFoundError|SyntaxError|ReferenceError)", out)})
        morto = any(rc for rc, _ in res) and not erros
        mortos += morto
        print("MORTO " if morto else "VIVO  ", nome, "|", " / ".join(out.strip().splitlines()[-1][:80] if out.strip() else "" for _, out in res), erros)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
print("MUTACAO_D61 · mortos=%d de %d" % (mortos, len(MUTANTES)))
sys.exit(0 if mortos == len(MUTANTES) else 1)
