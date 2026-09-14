#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SONDA — abre a rota de verdade. Deixa de ser «descrita por busca».

A missao anterior entregou 37 rotas e declarou, na propria entrega, que
NENHUMA foi aberta. Esta sonda e' o que fecha essa divida.

TRES ARMADILHAS QUE ESTA SONDA TEM DE SOBREVIVER
------------------------------------------------
1 · `CONN_FAIL` PODE SER CULPA NOSSA, NAO DA FONTE.
    A missao paralela `italy-source-qualification-v1` mediu isto na pele: o
    helper de cadeia TLS tinha a porta do proxy fixa em codigo de outra
    sessao. Falhava em silencio, e a falha PARECIA «fonte morta». Cinco
    fontes oficiais — ISMEA, ARPA Puglia, ARPA Sicilia, Regione Abruzzo,
    UNIPI — so' foram recuperadas depois do conserto.
    Regra: falha de ligacao nunca escreve BROKEN. Escreve UNKNOWN, e diz que
    a duvida e' nossa.

2 · HTTP 200 PODE SER UMA PAGINA DE ERRO.
    O ataque 18 daquela missao apanhou a ARPA Sardegna a servir pagina de
    erro do IIS, ja promovida a P1. E a minha propria missao 1 mediu sitios
    vivos com HTTP 200 e menos de 400 caracteres de texto.
    Regra: 200 nao e' prova. Prova e' 200 + texto + sinal do assunto.

3 · BLOCKED NAO E' BROKEN.
    403, 401 e muro de login dizem «nao te deixo entrar», nao «nao existo».
    Confundir os dois apaga fonte viva do acervo. Sao estados diferentes com
    accoes diferentes: BROKEN pede fonte nova, BLOCKED pede outra rota.

E A SONDA E' TESTADA ANTES DE JULGAR
------------------------------------
Dois controles POSITIVOS (rotas que TEM de abrir) e dois NEGATIVOS (uma sede
encerrada que eu mesmo descobri, e um dominio que nao existe). Se um controle
positivo falhar, a sonda esta quebrada e o resultado inteiro nao vale — e o
programa para em vez de entregar numeros.
"""

import gzip
import html
import io
import json
import re
import socket
import ssl
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "candidatas"))
TRAB = Path("C:/Users/London1/AppData/Local/Temp/sintonia-fechar")
TRAB.mkdir(parents=True, exist_ok=True)
CACHE = TRAB / "paginas"
CACHE.mkdir(exist_ok=True)

# UA de navegador: a memoria do projeto tem dois casos medidos em que o curl
# devolve 0 bytes com HTTP 200 e o WebFetch devolve 403, e o urllib com este
# cabecalho le a mesma pagina.
CAB = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/124.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "it-IT,it;q=0.9,en;q=0.8,de;q=0.7",
    "Accept-Encoding": "gzip, deflate",
}

CTX = ssl.create_default_context()
CTX.check_hostname = False
CTX.verify_mode = ssl.CERT_NONE   # cadeia incompleta e' defeito do servidor,
                                  # nao prova de que a fonte nao publica

# Marcas de pagina de erro servida com HTTP 200
ERRO_NA_PAGINA = re.compile(
    r"internet information services|iis\s*(windows|7|8|10)|"
    r"pagina non trovata|page not found|error 404|errore 404|"
    r"service unavailable|servizio non disponibile|sito in manutenzione|"
    r"site under maintenance|default web site page|it works!|"
    r"apache2? (ubuntu|debian) default", re.I)

# Muro de entrada
MURO = re.compile(r"accedi al (tuo )?account|effettua il login|area riservata|"
                  r"sign in to continue|enter your password|captcha|"
                  r"verifica di non essere un robot", re.I)

# ── SINAL DE QUE A PAGINA FALA DO ASSUNTO ─────────────────────────────────
# ⚠️ A PRIMEIRA VERSAO ERA SO' EM ITALIANO, e isso ja custou caro uma vez.
# Na missao 1, um filtro monolingue recusou duas fontes italianas de primeira
# linha: o Versuchszentrum Laimburg (publica em ALEMAO) e o Italian Journal of
# Agrometeorology (publica em INGLES). Aqui repetiu-se: a EU Pesticides
# Database saiu WRONG_SOURCE por estar em ingles. Detector monolingue nao e'
# conservador — e' cego de um olho.
SINAL = re.compile(
    # italiano
    r"bollettin|fenolog|bbch|fitosanitar|agrometeo|coltur|coltiv|avversit|"
    r"parassit|malatti|difesa integrata|produzione integrata|monitoraggio|"
    r"prezz|quotazion|mercato|superfici|produzione|resa|"
    r"sostanza attiva|principio attivo|etichetta|autorizzaz|registro|"
    r"gradi giorno|clima|stazioni|vendemmia|raccolt|semina"
    # ingles (producao cientifica e bases europeias)
    r"|pesticide|plant protection|active substance|crop|phenolog|harvest|"
    r"yield|pest|disease|residue|authoris|authoriz|maximum residue|"
    r"agrometeorolog|growing degree|bulletin"
    # alemao (Alto Adige) e frances (Valle d'Aosta)
    r"|pflanzenschutz|obstbau|weinbau|versuchszentrum|beratungsring|"
    r"phytosanitaire|viticulture", re.I)

DATA = re.compile(
    r"\b(3[01]|[12]\d|0?\d)[/\-\.](1[0-2]|0?\d)[/\-\.](20(2[0-9]))\b"
    r"|\b20(2[0-9])[/\-](1[0-2]|0?\d)[/\-](3[01]|[12]\d|0?\d)\b"
    r"|\b(3[01]|[12]\d|0?\d)\s+(gennaio|febbraio|marzo|aprile|maggio|giugno|"
    r"luglio|agosto|settembre|ottobre|novembre|dicembre)\s+20(2[0-9])\b", re.I)


def _chave(url):
    return re.sub(r"[^a-z0-9]+", "_", url.lower())[:120]


def existe_no_dns_publico(host):
    """O dominio existe NO MUNDO, mesmo que nao resolva NESTA maquina?

    ⚠️ ISTO SALVOU UMA FONTE VIVA DE SER DECLARADA MORTA. A sonda deu
    `getaddrinfo failed` para `www.arpa.piemonte.it` — em Python E em curl — e
    eu ia escrever BROKEN. O resolvedor publico 8.8.8.8 devolve tres enderecos
    (alias de `vip-lb-1-portali.nivolapiemonte.it`). O dominio esta vivo; o
    DNS desta maquina e' que nao o alcanca.

    E' a mesma familia do que a missao paralela mediu: cinco fontes oficiais
    «mortas» que eram defeito de ferramenta local. A pergunta certa nunca e'
    «falhou?», e' «falhou de que lado?».
    """
    import subprocess
    try:
        r = subprocess.run(["nslookup", host, "8.8.8.8"], capture_output=True,
                           text=True, encoding="utf-8", errors="replace",
                           timeout=25)
        saida = (r.stdout or "") + (r.stderr or "")
    except Exception:                                           # noqa: BLE001
        return None, "nao consegui consultar o resolvedor publico"
    # um IP fora da linha do proprio servidor 8.8.8.8 prova que resolveu
    ips = [ip for ip in re.findall(r"\b\d{1,3}(?:\.\d{1,3}){3}\b", saida)
           if ip != "8.8.8.8"]
    if ips:
        return True, f"resolve no DNS publico: {', '.join(ips[:3])}"
    if re.search(r"non-existent domain|NXDOMAIN|can't find", saida, re.I):
        return False, "o resolvedor publico tambem diz que nao existe (NXDOMAIN)"
    return None, "resposta do resolvedor publico nao foi conclusiva"


def baixar(url, tentativas=2):
    """Devolve (estado, http, url_final, texto, bruto_len). Cacheia em disco."""
    c = CACHE / (_chave(url) + ".json")
    if c.exists():
        d = json.loads(c.read_text(encoding="utf-8"))
        return (d["estado"], d["http"], d["url_final"], d["texto"], d["bytes"])

    ultimo = None
    for n in range(tentativas):
        try:
            req = urllib.request.Request(url, headers=CAB)
            with urllib.request.urlopen(req, timeout=30, context=CTX) as r:
                bruto = r.read()
                if (r.headers.get("Content-Encoding") or "").lower() == "gzip":
                    try:
                        bruto = gzip.decompress(bruto)
                    except OSError:
                        pass
                fin = r.geturl()
                http = r.status
            res = ("OK", http, fin, bruto)
            break
        except urllib.error.HTTPError as e:
            corpo = b""
            try:
                corpo = e.read()
            except Exception:                                   # noqa: BLE001
                pass
            res = ("HTTP_ERRO", e.code, url, corpo)
            break
        except (urllib.error.URLError, socket.timeout, ssl.SSLError,
                ConnectionError, OSError) as e:
            ultimo = f"{type(e).__name__}: {e}"
            # DNS que nao resolve e' da fonte; o resto pode ser nosso
            if "getaddrinfo failed" in str(e) or "Name or service" in str(e):
                res = ("DNS_FALHA", 0, url, b"")
                break
            time.sleep(1.5 * (n + 1))
            res = ("CONN_FAIL", 0, url, b"")
    estado, http, fin, bruto = res
    if estado == "CONN_FAIL":
        fin = url + f"  [{ultimo}]"

    texto = ""
    if bruto:
        for cod in ("utf-8", "latin-1"):
            try:
                texto = bruto.decode(cod, errors="replace")
                break
            except Exception:                                   # noqa: BLE001
                continue
        texto = re.sub(r"(?is)<(script|style|noscript).*?</\1>", " ", texto)
        texto = re.sub(r"(?s)<[^>]+>", " ", texto)
        texto = html.unescape(re.sub(r"\s+", " ", texto)).strip()

    c.write_text(json.dumps({"estado": estado, "http": http, "url_final": fin,
                             "texto": texto[:200000], "bytes": len(bruto)},
                            ensure_ascii=False), encoding="utf-8")
    return estado, http, fin, texto[:200000], len(bruto)


def julgar(url):
    """O veredito de UMA rota, com a razao escrita ao lado."""
    estado, http, fin, texto, nb = baixar(url)
    t = len(texto)
    d = {"URL_ORIGINAL": url, "URL_FINAL": fin.split("  [")[0],
         "HTTP": http, "BYTES": nb, "TAMANHO_TEXTO": t,
         "REDIRECIONOU": "SIM" if fin.split("  [")[0].rstrip("/") !=
                                  url.rstrip("/") else "NAO"}

    if estado == "CONN_FAIL":
        d.update(VEREDITO="UNKNOWN", PORQUE=(
            "falha de ligacao apos 2 tentativas. ⚠️ A DUVIDA E' NOSSA, nao da "
            "fonte: a missao paralela recuperou 5 fontes oficiais que "
            "«pareciam mortas» e eram defeito de ferramenta local. "
            f"Detalhe: {fin.split('  [')[-1].rstrip(']')}"))
        return d
    if estado == "DNS_FALHA":
        # NAO escrever BROKEN sem perguntar ao mundo. Ver `existe_no_dns_publico`.
        host = re.sub(r"^https?://", "", url).split("/")[0]
        existe, nota = existe_no_dns_publico(host)
        if existe is True:
            d.update(VEREDITO="UNKNOWN", PORQUE=(
                f"o DNS DESTA MAQUINA nao resolve «{host}», mas o {nota}. "
                "⚠️ A FONTE ESTA VIVA; o limite e' nosso. Escrever BROKEN aqui "
                "apagaria do acervo uma agencia regional que publica. Pede "
                "outra rota de saida (VPN, outro resolvedor), nao outra fonte."))
        elif existe is False:
            d.update(VEREDITO="BROKEN", PORQUE=f"{nota}. O nome nao existe.")
        else:
            d.update(VEREDITO="UNKNOWN", PORQUE=(
                f"nao resolve aqui e {nota} — fica em duvida declarada."))
        return d
    if estado == "HTTP_ERRO":
        if http in (401, 403, 429):
            d.update(VEREDITO="BLOCKED", PORQUE=(
                f"HTTP {http}. ⚠️ BLOCKED NAO E' BROKEN: o servidor responde e "
                "recusa-me a entrada. A fonte pode estar viva e publicar — "
                "pede outra rota, nao outra fonte."))
        elif http in (404, 410):
            d.update(VEREDITO="BROKEN", PORQUE=f"HTTP {http}: a rota nao existe "
                     "no servidor, que responde normalmente para o resto.")
        else:
            d.update(VEREDITO="UNKNOWN", PORQUE=f"HTTP {http} — nao classifico "
                     "sem olhar; pode ser transitorio do servidor.")
        return d

    # daqui para baixo, HTTP 200
    if ERRO_NA_PAGINA.search(texto[:4000]):
        d.update(VEREDITO="BROKEN", PORQUE=(
            "⚠️ HTTP 200 COM PAGINA DE ERRO DENTRO. Foi assim que a ARPA "
            "Sardegna chegou a P1 na missao paralela, a servir erro do IIS. "
            "Codigo 200 nao e' prova de nada."))
        return d
    if t < 400:
        # ⚠️ TEXTO CURTO TEM DUAS CAUSAS OPOSTAS, e a primeira versao desta
        # sonda juntava-as. Pagina morta tem pouco texto E pouco byte. App de
        # JavaScript tem pouco texto e MUITO byte — e esta viva; a minha sonda
        # e' que nao executa JS. Chamar as duas de BROKEN apaga do acervo dois
        # portais do Estado italiano (`sian.it`, `esploradati.istat.it`).
        # ⚠️ E HA UMA TERCEIRA CAUSA: a pagina de REDIRECIONAMENTO. O
        # `irriframe.it` devolve 970 bytes a dizer «Stai per essere
        # reindirizzato ad altra pagina» — e' um meta-refresh, que o urllib nao
        # segue. Chamei-lhe BROKEN e estava vivo. Placa de «siga em frente» nao
        # e' porta fechada.
        reenvio = re.search(
            r"stai per essere reindirizzat|sarai reindirizzat|"
            r"you (are|will be) redirected|redirecting|"
            r"se non sei reindirizzato|if you are not redirected", texto, re.I)
        erro_da_app = re.search(
            r"an error occurred|errore nel contattare|error contacting|"
            r"impossibile contattare", texto, re.I)
        if reenvio:
            d.update(VEREDITO="UNKNOWN", PORQUE=(
                f"HTTP 200 com {t} caracteres e a pagina diz «{reenvio.group(0)}»: "
                "e' REDIRECIONAMENTO por meta-refresh ou JavaScript, que o "
                "urllib nao segue. ⚠️ A fonte esta viva e o destino nao foi "
                "medido — placa de «siga em frente» nao e' porta fechada."))
        elif erro_da_app:
            d.update(VEREDITO="BROKEN", PORQUE=(
                f"HTTP 200, {nb} bytes, e a propria aplicacao escreve o erro: "
                f"«{erro_da_app.group(0)}». Medido agora — pode ser "
                "transitorio, e por isso a data da medicao viaja com o "
                "veredito."))
        elif nb >= 2500:
            d.update(VEREDITO="UNKNOWN", PORQUE=(
                f"HTTP 200 com {nb} bytes mas so' {t} caracteres de texto: e' "
                "aplicacao de JavaScript, e a minha sonda nao executa JS. ⚠️ A "
                "LIMITACAO E' MINHA, nao da fonte. Precisa de navegador com "
                "janela para ser lida."))
        else:
            d.update(VEREDITO="BROKEN", PORQUE=(
                f"HTTP 200 com {t} caracteres e apenas {nb} bytes. Pouco texto "
                "E pouco byte: sitio vivo no servidor e morto no conteudo — a "
                "regra dos 400 vem da missao 1."))
        return d
    if MURO.search(texto[:6000]) and not SINAL.search(texto[:6000]):
        d.update(VEREDITO="BLOCKED", PORQUE="muro de entrada (login/captcha) "
                 "antes de qualquer conteudo tecnico.")
        return d

    sinais = sorted({m.group(0).lower() for m in SINAL.finditer(texto)})
    datas = [m.group(0) for m in DATA.finditer(texto)]
    d.update(SINAIS_DO_ASSUNTO=" · ".join(sinais[:8]),
             N_SINAIS=len(sinais),
             DATAS_NA_PAGINA=" · ".join(datas[:4]), N_DATAS=len(datas))
    if not sinais:
        d.update(VEREDITO="WRONG_SOURCE", PORQUE=(
            f"abre e tem {t} caracteres, mas nenhuma palavra do assunto "
            "agricola/tecnico. Abre != serve."))
        return d
    d.update(VEREDITO="ABRE_E_FALA_DO_ASSUNTO", PORQUE=(
        f"HTTP 200 · {t} caracteres · {len(sinais)} palavras do assunto · "
        f"{len(datas)} datas legiveis. ⚠️ Isto NAO e' ainda VALIDATED: falta "
        "o exemplo real e a leitura humana."))
    return d


# ─────────────────────────────────────────────────────────────────────────────
# CONTROLES — a sonda e' testada ANTES de julgar qualquer fonte
# ─────────────────────────────────────────────────────────────────────────────
CONTROLES = [
 # positivos: TEM de abrir e falar do assunto
 ("POSITIVO", "https://www.fitosanitari.salute.gov.it/",
  ("ABRE_E_FALA_DO_ASSUNTO",),
  "registo oficial de fitossanitarios. A memoria do projeto diz que abre no "
  "urllib. Se isto falhar, a sonda esta quebrada."),
 ("POSITIVO", "https://www.regione.veneto.it/web/fitosanitario/bollettini-viticoli",
  ("ABRE_E_FALA_DO_ASSUNTO",),
  "boletins viticolos do Veneto, ja no acervo."),
 # negativos: NAO podem sair como rota boa
 ("NEGATIVO", "https://nao-existe-este-dominio-sintonia-2026.it/",
  ("BROKEN",), "dominio inventado: tem de dar BROKEN por DNS."),
 ("NEGATIVO", "https://www.coeweb.istat.it/",
  ("BROKEN", "BLOCKED", "UNKNOWN", "WRONG_SOURCE"),
  "sede encerrada em 30/09/2025 (achado da missao anterior). NAO pode sair "
  "como rota que abre e serve."),
]


def correr_controles():
    print("CONTROLES DA SONDA — antes de julgar qualquer fonte")
    print("-" * 92)
    falhou = []
    for tipo, url, esperado, porque in CONTROLES:
        r = julgar(url)
        ok = r["VEREDITO"] in esperado
        print(f"  {tipo:8s} {r['VEREDITO']:24s} {'OK ' if ok else 'FALHOU'}  "
              f"{url[:52]}")
        if not ok:
            print(f"           esperava {esperado}, deu {r['VEREDITO']}")
            print(f"           {porque}")
            falhou.append((tipo, url, r["VEREDITO"], esperado))
    print("-" * 92)
    return falhou


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    f = correr_controles()
    if f:
        print(f"\n!! {len(f)} CONTROLE(S) FALHARAM. A sonda nao esta provada, "
              "e nenhum veredito dela vale. Parando de proposito.")
        sys.exit(1)
    print("\nSONDA PROVADA: 2 positivos abrem, 2 negativos nao passam.")
