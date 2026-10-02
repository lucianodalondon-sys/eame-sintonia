"""Casco: publica /fast no ENDERECO DE TESTE depois de cada rodada FAST-AUTO.

Chamado por FAST-AUTO/POS_RODADA_PUBLICAR.cmd <RUN_ID>, que o rodada_fast.py da Intelligence
dispara so DEPOIS de gravar ULTIMA.txt. Nao toca no portal oficial (release/canonical), nem no
ramo, nem na pasta da Intelligence (so le). Falha fechada: rc!=0 e nada publicado.

Passos: (1) confere que ULTIMA.txt aponta para o RUN_ID recebido; (2) regera
client/sintonia-fast.local.js pelo gerar_fast_local.py (que confere SHA256SUMS);
(3) confere que o pacote gerado diz ULTIMA=<RUN_ID>; (4) monta pasta temporaria so com
fast.html + sintonia-fast.local.js + tokens/fontes ADAMA; (5) vercel deploy (preview);
(6) alias fixo; (7) prova no ar: /sintonia-fast.local.js contem o RUN_ID.
"""
import json, os, re, shutil, subprocess, sys, tempfile, time, urllib.request

CASCO = r"C:/g/casco"
CLIENT = os.path.join(CASCO, "italia-portale", "client")
GERADOR = os.path.join(CASCO, "italia-portale", "audit", "casco", "gerar_fast_local.py")
IE = r"C:/Users/London1/sintonia-sala-italia/intelligence-experimental"
ULTIMA = os.path.join(IE, "FAST-AUTO", "ULTIMA.txt")
ESTADO = r"C:/Users/London1/sintonia-casco-preview/fast"
ALIAS = "sintonia-fast-teste.vercel.app"
SCOPE = "london-creative"
PROJETO = "sintonia-eame-preview"


def log(msg):
    os.makedirs(ESTADO, exist_ok=True)
    linha = time.strftime("%Y-%m-%dT%H:%M:%S ") + msg
    print(linha, flush=True)
    with open(os.path.join(ESTADO, "PUBLICACOES.log"), "a", encoding="utf-8") as f:
        f.write(linha + "\n")


def run(cmd, cwd=None, timeout=900):
    r = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, encoding="utf-8",
                       errors="replace", timeout=timeout, shell=isinstance(cmd, str))
    return r.returncode, r.stdout, r.stderr


def main():
    if len(sys.argv) < 2 or not re.fullmatch(r"[A-Za-z0-9_.-]+", sys.argv[1]) or ".." in sys.argv[1]:
        log("RECUSADO run_id invalido %r" % sys.argv[1:])
        return 2
    run_id = sys.argv[1]
    os.makedirs(ESTADO, exist_ok=True)
    ponteiro = open(ULTIMA, encoding="utf-8").read().strip()
    if ponteiro != "RUN_ID=" + run_id:
        log("RECUSADO %s: ULTIMA.txt diz %r" % (run_id, ponteiro))
        return 3

    rc, out, err = run([sys.executable, GERADOR, IE])
    if rc != 0:
        log("RECUSADO %s: gerador rc=%s %s" % (run_id, rc, (out + err).strip()[-300:]))
        return 4
    js = open(os.path.join(CLIENT, "sintonia-fast.local.js"), encoding="utf-8").read()
    if run_id not in js:
        log("RECUSADO %s: pacote gerado nao contem o RUN_ID" % run_id)
        return 5

    tmp = tempfile.mkdtemp(prefix="fast-pub-")
    try:
        dst = os.path.join(tmp, "site")
        os.makedirs(dst)
        shutil.copy(os.path.join(CLIENT, "fast.html"), os.path.join(dst, "fast.html"))
        shutil.copy(os.path.join(CLIENT, "fast.html"), os.path.join(dst, "index.html"))
        shutil.copy(os.path.join(CLIENT, "sintonia-fast.local.js"), os.path.join(dst, "sintonia-fast.local.js"))
        ds = os.path.join(CLIENT, "_ds", "adama-brandwell")
        for sub in ("tokens", os.path.join("assets", "fonts")):
            if os.path.isdir(os.path.join(ds, sub)):
                shutil.copytree(os.path.join(ds, sub), os.path.join(dst, "_ds", "adama-brandwell", sub))
        json.dump({"outputDirectory": "site", "cleanUrls": True,
                   "headers": [{"source": "/(.*)", "headers": [
                       {"key": "Cache-Control", "value": "public, max-age=0, must-revalidate"},
                       {"key": "X-Robots-Tag", "value": "noindex"}]}]},
                  open(os.path.join(tmp, "vercel.json"), "w"))
        json.dump({"name": "sintonia-fast-teste", "private": True,
                   "scripts": {"build": "echo fast-estatico"}},
                  open(os.path.join(tmp, "package.json"), "w"))
        rc, out, err = run("vercel link --yes --project %s --scope %s" % (PROJETO, SCOPE), cwd=tmp)
        if rc != 0:
            log("FALHA %s: vercel link rc=%s %s" % (run_id, rc, err.strip()[-300:]))
            return 6
        rc, out, err = run("vercel deploy --yes --scope %s" % SCOPE, cwd=tmp, timeout=1200)
        urls = re.findall(r"https://[a-z0-9-]+\.vercel\.app", out + err)
        if rc != 0 or not urls:
            log("FALHA %s: vercel deploy rc=%s %s" % (run_id, rc, (out + err).strip()[-300:]))
            return 7
        url = urls[-1]
        rc, out, err = run("vercel alias set %s %s --scope %s" % (url, ALIAS, SCOPE), cwd=tmp)
        alias_ok = rc == 0
        if not alias_ok:
            log("AVISO %s: alias falhou rc=%s %s" % (run_id, rc, (out + err).strip()[-200:]))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    alvo = ("https://" + ALIAS) if alias_ok else url
    prova = "NAO_CONFERIDO"
    for _ in range(6):
        try:
            corpo = urllib.request.urlopen(alvo + "/sintonia-fast.local.js?t=%d" % time.time(), timeout=30).read().decode("utf-8", "replace")
            prova = "RUN_ID_NO_AR" if run_id in corpo else "RUN_ID_AUSENTE_NO_AR"
            if prova == "RUN_ID_NO_AR":
                break
        except Exception as e:
            prova = "ERRO %r" % e
        time.sleep(10)
    json.dump({"RUN_ID": run_id, "URL": alvo + "/fast", "DEPLOY": url, "PROVA": prova,
               "PUBLICADO_EM": time.strftime("%Y-%m-%dT%H:%M:%S")},
              open(os.path.join(ESTADO, "ULTIMA-PUBLICACAO.json"), "w", encoding="utf-8"), indent=1)
    log("PUBLICADO %s URL=%s/fast DEPLOY=%s PROVA=%s" % (run_id, alvo, url, prova))
    return 0 if prova == "RUN_ID_NO_AR" else 8


if __name__ == "__main__":
    sys.exit(main())
