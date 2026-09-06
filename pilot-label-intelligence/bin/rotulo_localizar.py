#!/usr/bin/env python3
"""
rotulo_localizar.py — do numero de registro ate o PDF oficial da etichetta.

Resolve o passo que faltava para sair do universo ADAMA: dado um numero de
registro qualquer do registro italiano, descobrir a URL do rotulo oficial e a
data em que essa etichetta entrou em vigor.

A rota, medida nesta sessao:

  1. GET  /fitosanitariws_new/FitosanitariServlet          -> abre sessao (JSESSIONID)
  2. POST mesmo endpoint, corpo MINIMO:
         ACTION=cercaProdotti&FROM=0&TO=49&PROVENIENZA=RICERCA&NUMERO_REGISTRAZIONE=<n>
     O numero vai SEM zeros a esquerda. Com "015275" o servlet responde erro;
     com "15275" responde a ficha. Mandar os campos vazios do formulario
     tambem faz o servlet errar — por isso o corpo minimo.
  3. a ficha traz  EtichettaServlet?id=NNNNN  e o texto "Etichetta del DD/MM/AAAA"
  4. GET dessa URL -> PDF

Cliente: wget. O host manda um cabecalho Public-Key-Pins truncado sem CRLF e o
curl 8 aborta com "Header without colon"; o wget tolera. E manda cadeia TLS
incompleta, resolvida por recon/it-chain-fix.pem. Nada de verify=False.

O servlet e INTERMITENTE. Medido: a mesma consulta, no mesmo minuto, alterna
entre a ficha certa e uma pagina generica "Si e' verificato un errore". Nao e o
numero de registro e nao e o numero de buscas por sessao — foi testado com o
mesmo registro nas duas condicoes. Por isso a busca tenta de novo com SESSAO
NOVA e espera crescente. Uma falha depois das tentativas vira SEARCH_REJECTED,
que e estado de COLETA e nunca "produto sem rotulo".

Um detalhe que custa caro: no POST as cookies sao apenas CARREGADAS. Reescrever
o pote com --save-cookies no meio da sequencia derruba a sessao — medido, e o
erro aparece exatamente como o erro generico acima.
"""
import argparse, subprocess as _sp, json, os, re, subprocess, sys, tempfile, time

HOST = "https://www.fitosanitari.salute.gov.it/fitosanitariws_new"
SERVLET = f"{HOST}/FitosanitariServlet"
UA = ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/126.0 Safari/537.36")
RE_ETI = re.compile(r"EtichettaServlet\?id=(\d+)")
RE_DATA = re.compile(r"Etichetta\s*(?:del)?\s*(\d{2}/\d{2}/\d{4})", re.I)


def _wget(url, ca, cookies, post=None, out=None, save_cookies=False):
    cmd = ["wget", f"--ca-certificate={ca}", "-U", UA, "-q", "--timeout=90", "--tries=2"]
    if os.path.exists(cookies):
        cmd += [f"--load-cookies={cookies}"]
    if save_cookies:
        cmd += ["--keep-session-cookies", f"--save-cookies={cookies}"]
    if post is not None:
        cmd += [f"--post-data={post}", f"--header=Referer: {SERVLET}"]
    cmd += ["-O", out or "-", url]
    r = subprocess.run(cmd, capture_output=True)
    return r.returncode


def abrir_sessao(ca, cookies):
    return _wget(SERVLET, ca, cookies, out=os.devnull, save_cookies=True)


def localizar(reg, ca, cookies, sleep=1.5, tentativas=4):
    """Devolve {LABEL_URL, LABEL_EFFECTIVE_AT} ou um estado de falha.

    Tenta de novo com sessao nova porque o servlet erra de forma intermitente.
    """
    ultimo = {"STATE": "SEARCH_REJECTED"}
    for t in range(1, tentativas + 1):
        abrir_sessao(ca, cookies)
        time.sleep(sleep)
        r = _uma_busca(reg, ca, cookies, sleep)
        if r["STATE"] in ("FOUND", "NO_LABEL_LINK"):
            r["ATTEMPTS"] = t
            return r
        ultimo = r
        time.sleep(sleep * 2 * t)
    ultimo["ATTEMPTS"] = tentativas
    ultimo.setdefault("NOTE", "")
    ultimo["NOTE"] += (" | estado de COLETA apos %d tentativas com sessao nova; "
                       "nao afirma ausencia de rotulo" % tentativas)
    return ultimo


def _uma_busca(reg, ca, cookies, sleep):
    n = str(reg).lstrip("0") or "0"          # o servlet recusa zeros a esquerda
    corpo = f"ACTION=cercaProdotti&FROM=0&TO=49&PROVENIENZA=RICERCA&NUMERO_REGISTRAZIONE={n}"
    with tempfile.NamedTemporaryFile(suffix=".html", delete=False) as t:
        tmp = t.name
    try:
        rc = _wget(SERVLET, ca, cookies, post=corpo, out=tmp)
        time.sleep(sleep)
        if rc != 0:
            return {"STATE": "SEARCH_FAILED", "RC": rc}
        h = open(tmp, encoding="latin-1", errors="replace").read()
        if "verificato un errore" in h:
            return {"STATE": "SEARCH_REJECTED",
                    "NOTE": "o servlet devolveu erro generico para esta consulta"}
        m = RE_ETI.search(h)
        if not m:
            return {"STATE": "NO_LABEL_LINK",
                    "NOTE": "ficha encontrada, sem link de etichetta — nao e ausencia regulatoria"}
        d = RE_DATA.search(re.sub(r"<[^>]+>", " ", h))
        eff = "NOT_PRESENT"
        if d:
            dd, mm, yy = d.group(1).split("/")
            eff = f"{yy}-{mm}-{dd}"
        return {"STATE": "FOUND",
                "LABEL_URL": f"{HOST}/EtichettaServlet?id={m.group(1)}",
                "LABEL_DOCUMENT_ID": m.group(1),
                "LABEL_EFFECTIVE_AT": eff}
    finally:
        os.unlink(tmp)



def _garantir_cadeia(ca):
    """Monta it-chain-fix.pem se ele nao existir. So a intermediaria e versionada."""
    if os.path.exists(ca):
        return ca
    sh = os.path.join(os.path.dirname(os.path.abspath(__file__)), "chain.sh")
    subprocess.run([sh], check=True, capture_output=True)
    return ca

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("registros", nargs="+")
    ap.add_argument("--ca", default="pilot-label-intelligence/recon/it-chain-fix.pem")
    ap.add_argument("--json", default=None)
    a = ap.parse_args()
    _garantir_cadeia(a.ca)
    with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as t:
        ck = t.name
    os.unlink(ck)
    out = []
    for r in a.registros:
        res = localizar(r, a.ca, ck)
        res["REGISTRATION_ID"] = r
        out.append(res)
        print(f'  {r}  {res["STATE"]:<16} t={res.get("ATTEMPTS","?")}  '
              f'{res.get("LABEL_URL","")}  {res.get("LABEL_EFFECTIVE_AT","")}', file=sys.stderr)
    if a.json:
        json.dump(out, open(a.json, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    return 0


if __name__ == "__main__":
    sys.exit(main())
