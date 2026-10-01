"""T9 SOCIAL-CATALOGO-AUTORIZADO · o ataque: cada regra nova da porta social desligada, uma de cada vez, numa COPIA.

    py provas/t9_social/mutacao_porta_social.py [--ref=HEAD]

O metodo e o de `provas/coleta_continua_mutacao.py`: a copia sai de `git archive <ref>` (o repositorio nao e
tocado); cada mutante troca UM trecho exacto; um trecho que nao apareca exactamente uma vez falha ALTO
(MUTANTE_SEM_ALVO — nunca conta como morto). Diferenca: uma so copia, e o ficheiro e reposto byte a byte depois de
cada mutante (a arvore tem ~350 MiB); sem .pyc (PYTHONDONTWRITEBYTECODE e __pycache__ apagado antes de cada corrida:
um mutante do mesmo tamanho nao pode correr o bytecode do original). MORTO = `tests.test_porta_social_t9` sai com
codigo != 0. Resultado em `provas/t9_social/PORTA-SOCIAL-MUTACAO.json`.
"""
import io
import json
import os
import re
import shutil
import subprocess
import sys
import tarfile
import tempfile

RAIZ = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PORTA = "curadoria/plano_onda_social.py"
LINHA = "ferramentas/big_collection/coleta_continua.py"
TESTE = "tests.test_porta_social_t9"
MUTANTES = [
    ("T01_STRATEGY_DESCONHECIDA_SEM_NOME", PORTA, "        if st not in VC.STRATEGIES:\n", "        if False:\n"),
    ("T02_DECISAO_DE_OUTRA_PLATAFORMA_ACEITE", PORTA, "    if d not in pede:\n", "    if False:\n"),
    ("T03_SEM_AUTORIZACAO_ACEITE", PORTA, "    if not d:\n        return [(\"SEM_RASTRO_DE_AUTORIZACAO\"",
     "    if not d:\n        return []\n    if False:\n        return [(\"SEM_RASTRO_DE_AUTORIZACAO\""),
    ("T04_CANAL_YOUTUBE_DENTRO_DO_AMBITO", PORTA, "    elif fase not in FASES_DO_AMBITO and not m:\n", "    elif False:\n"),
    ("T05_PLATAFORMA_FORA_DO_AMBITO_ACEITE", PORTA,
     "    if plat not in AMBITO:\n        m.append((\"FORA_DO_AMBITO_AUTORIZADO\", \"plataforma",
     "    if plat not in AMBITO and False:\n        m.append((\"FORA_DO_AMBITO_AUTORIZADO\", \"plataforma"),
    ("T06_LISTAGEM_DO_INSTAGRAM_SEM_NOME", PORTA, "        if not ok:\n            m.append((\"LISTAGEM_NAO_AUTORIZADA\"",
     "        if False:\n            m.append((\"LISTAGEM_NAO_AUTORIZADA\""),
    ("T07_ROTA_DO_SCRAP_NAO_CONFERIDA", PORTA, "    ok, porque = RSS.conferir(aq)\n", "    ok, porque = True, \"\"\n"),
    ("T08_ROUTE_POLICY_STATUS_IGNORADO", PORTA, "    if pol and pol != \"ALLOWED\":\n", "    if False:\n"),
    ("T09_FEED_SEM_POLITICA_ACEITE", PORTA, "    if not c.get(\"ROUTE_POLICY_STATUS\"):\n", "    if False:\n"),
    ("T10_ROTA_DO_FEED_NAO_CONFERIDA", PORTA, "    ok, porque = VC.route_resolved(c)\n", "    ok, porque = True, \"\"\n"),
    ("T11_FEED_FORA_DE_READY_ACEITE", PORTA, "    if e != \"READY_FOR_COLLECTION\":\n", "    if False:\n"),
    ("T12_FEED_PELA_PALAVRA_SCRAP_FASE", PORTA, "        elif st == FEED:\n", "        elif False:\n"),
    ("T13_RECUSA_SOME_EM_SILENCIO", PORTA, "            aceites.append(s)\n            continue\n",
     "            aceites.append(s)\n        continue\n"),
    ("T14_MOTIVO_NAO_E_O_DA_PRECEDENCIA", PORTA, "\"MOTIVO\": m[0][0], \"PORQUE\": m[0][1],",
     "\"MOTIVO\": m[-1][0], \"PORQUE\": m[-1][1],"),
    ("T15_LINHA_LE_A_PALAVRA", LINHA, "    sociais = tri[\"ACEITES\"]\n",
     "    sociais = sorted(s for s, c in contratos.items()\n"
     "                     if (c.get(\"ACQUISITION\") or {}).get(\"STRATEGY\") == \"SCRAP_FASE\")\n"),
    ("T16_PORTA_NAO_VAI_AO_CICLO", LINHA, "        if \"PORTA_SOCIAL\" in f:", "        if False:"),
    ("T17_SEM_CATALOGO_SEM_OS_MOTIVOS", LINHA,
     "\", \".join(\"%s=%d\" % (k, len(v)) for k, v in sorted(por_motivo.items())) or \"nenhuma\",",
     "\"nenhuma\","),
    ("T18_ESTADO_LIDO_DE_OUTRA_RAIZ", LINHA, "            f = raiz / \"curadoria\" / \"LIFECYCLE-LEDGER-V1.json\"",
     "            f = RAIZ / \"curadoria\" / \"LIFECYCLE-LEDGER-V1.json\""),
]


def copia(ref, destino):
    tar = subprocess.run(["git", "-C", RAIZ, "archive", "--format=tar", ref], capture_output=True, check=True).stdout
    with tarfile.open(fileobj=io.BytesIO(tar)) as t:
        t.extractall(destino)


def sem_pyc(pasta):
    for d in ("curadoria", os.path.join("ferramentas", "big_collection"), "tests"):
        shutil.rmtree(os.path.join(pasta, d, "__pycache__"), ignore_errors=True)


def correr(pasta):
    sem_pyc(pasta)
    env = dict(os.environ, PYTHONUTF8="1", PYTHONDONTWRITEBYTECODE="1",
               HTTPS_PROXY="http://127.0.0.1:9", HTTP_PROXY="http://127.0.0.1:9")
    r = subprocess.run([sys.executable, "-m", "unittest", TESTE], cwd=pasta, env=env, capture_output=True,
                       text=True, encoding="utf-8", errors="replace", timeout=600)
    m = re.search(r"Ran (\d+) test", r.stderr)
    return r.returncode, int(m.group(1)) if m else None, r.stderr[-600:]


def main():
    ref = next((a.split("=", 1)[1] for a in sys.argv[1:] if a.startswith("--ref=")), "HEAD")
    base = tempfile.mkdtemp(prefix="porta-social-mutacao-")
    out = {"REF": subprocess.run(["git", "-C", RAIZ, "rev-parse", "--short", ref], capture_output=True,
                                 text=True).stdout.strip(), "TESTE": TESTE, "MUTANTES": []}
    try:
        limpa = os.path.join(base, "limpa")
        copia(ref, limpa)
        cod, n, cauda = correr(limpa)
        out["SEM_MUTANTE"] = {"CODIGO": cod, "TESTES": n}
        if cod != 0:
            raise SystemExit("a copia limpa nao passa — o ataque nao tem base:\n" + cauda)
        for nome, alvo, de, para in MUTANTES:
            f = os.path.join(limpa, alvo)
            with open(f, "rb") as h:
                original = h.read()
            s = original.decode("utf-8")
            s2 = s.replace("\r\n", "\n")
            if s2.count(de) != 1:
                raise SystemExit("MUTANTE_SEM_ALVO %s: o trecho aparece %d vezes em %s" % (nome, s2.count(de), alvo))
            s2 = s2.replace(de, para)
            with open(f, "wb") as h:
                h.write((s2.replace("\n", "\r\n") if "\r\n" in s else s2).encode("utf-8"))
            try:
                cod, n, cauda = correr(limpa)
            finally:
                with open(f, "wb") as h:
                    h.write(original)
            morto = cod != 0
            out["MUTANTES"].append({"MUTANTE": nome, "ALVO": alvo, "MORTO": morto, "CODIGO": cod, "TESTES": n,
                                    "CAUDA": None if morto else cauda})
            print(nome, "MORTO" if morto else "SOBREVIVEU", flush=True)
        cod, n, cauda = correr(limpa)                                  # a copia reposta volta a passar
        out["DEPOIS_DO_ATAQUE"] = {"CODIGO": cod, "TESTES": n}
        if cod != 0:
            raise SystemExit("a copia nao voltou ao original depois do ataque:\n" + cauda)
    finally:
        shutil.rmtree(base, ignore_errors=True)
    out["MORTOS"] = sum(1 for m in out["MUTANTES"] if m["MORTO"])
    out["TOTAL"] = len(out["MUTANTES"])
    with open(os.path.join(RAIZ, "provas", "t9_social", "PORTA-SOCIAL-MUTACAO.json"), "w", encoding="utf-8",
              newline="\n") as h:
        json.dump(out, h, ensure_ascii=False, indent=1)
        h.write("\n")
    print("PORTA_SOCIAL_MUTACAO · mortos=%d de %d" % (out["MORTOS"], out["TOTAL"]))
    return 0 if out["MORTOS"] == out["TOTAL"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
