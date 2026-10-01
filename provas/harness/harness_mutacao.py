"""Harness de mutacao (fora do repo, como o da RESERVA; o sha256 vai na entrega).
uso: python harness_mutacao.py <worktree> <spec.json> <saida.json>
spec = {"NOME":..., "TESTE": [args do pytest], "MUTANTES": [{"MUTANTE","FICHEIRO","ALVO","SUBSTITUTO","FINGE"}]}
Cada mutante: aplica UMA troca (alvo unico), corre o teste, restaura; no fim confere o sha256 de cada ficheiro."""
import hashlib, json, subprocess, sys
from datetime import datetime, timezone
from pathlib import Path

W, SPEC, OUT = Path(sys.argv[1]), json.loads(Path(sys.argv[2]).read_text(encoding="utf-8")), Path(sys.argv[3])
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()


def correr():
    try:
        r = subprocess.run([sys.executable, "-B", "-m", "pytest", *SPEC["TESTE"], "-q", "-x", "-p", "no:cacheprovider"],
                           cwd=W, capture_output=True, text=True, encoding="utf-8", errors="replace",
                           timeout=SPEC.get("TIMEOUT_S", 900))
    except subprocess.TimeoutExpired:
        # o teste nao terminou dentro do limite (o controlo sem mutante e medido ao lado): conta como MORTO por TIMEOUT,
        # e o JSON diz isso — nunca se confunde com uma falha de asserção
        return -9, "TIMEOUT > %ss (controlo sem mutante: ver SEM_MUTANTE.CAUDA)" % SPEC.get("TIMEOUT_S", 900)
    cauda = [l for l in r.stdout.splitlines() if l.strip()][-1:] or [""]
    return r.returncode, cauda[0].strip()


head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=W, capture_output=True, text=True).stdout.strip()
sujo = subprocess.run(["git", "status", "--porcelain"], cwd=W, capture_output=True, text=True).stdout.strip()
fs = sorted({m["FICHEIRO"] for m in SPEC["MUTANTES"]})
antes = {f: sha(W / f) for f in fs}
rc0, cauda0 = correr()
out = {"NOME": SPEC["NOME"], "REF": head, "ARVORE_LIMPA_ANTES": not sujo, "TESTE": SPEC["TESTE"],
       "QUANDO": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
       "SEM_MUTANTE": {"RC": rc0, "ESTADO": "OK" if rc0 == 0 else "VERMELHO", "CAUDA": cauda0}, "MUTANTES": []}
if rc0 == 0:
    for m in SPEC["MUTANTES"]:
        p = W / m["FICHEIRO"]
        orig = p.read_bytes()
        alvo, novo = m["ALVO"].encode("utf-8"), m["SUBSTITUTO"].encode("utf-8")
        if b"\r\n" in orig and alvo not in orig:
            alvo, novo = alvo.replace(b"\n", b"\r\n"), novo.replace(b"\n", b"\r\n")
        n = orig.count(alvo)
        reg = {"MUTANTE": m["MUTANTE"], "FINGE": m["FINGE"], "CODIGO": {"FICHEIRO": m["FICHEIRO"],
               "ALVO": m["ALVO"], "SUBSTITUTO": m["SUBSTITUTO"]}}
        if n != 1:
            reg.update(MORTO=None, ESTADO="ALVO_NAO_UNICO (%d)" % n)
        else:
            try:
                p.write_bytes(orig.replace(alvo, novo))
                rc, cauda = correr()
            finally:
                p.write_bytes(orig)
            reg.update(MORTO=rc != 0, RC=rc, CAUDA=cauda)
        out["MUTANTES"].append(reg)
        print(m["MUTANTE"], reg.get("MORTO"), reg.get("CAUDA", reg.get("ESTADO")), flush=True)
iguais = antes == {f: sha(W / f) for f in fs}
mortos = sum(1 for m in out["MUTANTES"] if m.get("MORTO") is True)
out.update(MORTOS=mortos, TOTAL=len(SPEC["MUTANTES"]), RESTAURADOS_IGUAIS=iguais,
           ESTADO="PASS" if rc0 == 0 and mortos == len(SPEC["MUTANTES"]) and iguais else "FAIL")
OUT.write_text(json.dumps(out, ensure_ascii=False, indent=1) + "\n", encoding="utf-8", newline="\n")
print("MORTOS %d/%d · sem mutante %s · restaurados iguais %s · %s" % (mortos, out["TOTAL"], out["SEM_MUTANTE"]["ESTADO"],
                                                                       iguais, out["ESTADO"]))
