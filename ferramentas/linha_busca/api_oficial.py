# -*- coding: utf-8 -*-
"""LINHA-BUSCA · 3) as APIs OFICIAIS de busca — o pedido, a quota, o diagnostico e a tesoura da chave.

BUSCA-NO-ACTIONS (27/09). A busca por API corre no GitHub Actions (runner sem VPN: a API nao precisa de saida
italiana); as PAGINAS continuam a ser colhidas nesta maquina, com VPN IT, pelo `--colher`.

  pedir(url, cabecalhos)        UM pedido urllib. Sem robots: D91 — «so APIs publicas oficiais documentadas seguem
                                os proprios termos». Sem o teto de 5/dominio das PAGINAS: quem manda e a QUOTA.
  QUOTA_DIA                     o teto declarado por motor (Custom Search JSON API: 100 consultas/dia gratis).
  diagnosticar_cse()            o passo 0: UMA chamada que diz se a API esta ligada no projeto, se a chave a pode
                                usar e se ha CX — sem nunca escrever a chave.
  redigir(texto)                a tesoura: a chave (e o CX) saem de qualquer texto antes de ele ser gravado.

A CHAVE. E a `YOUTUBE_DATA_API_KEY` (resposta do dono, 27/09 11:28: o mesmo projeto Google Cloud). Entra so pelo
ambiente (`SINTONIA_GOOGLE_CSE_KEY`), vai no endereco do pedido (`key=`, a forma que o motor ja usava) e NUNCA
sai deste processo: todo o texto de erro passa por `redigir`. O Actions tambem esconde os segredos no log.
"""
from __future__ import annotations

import json
import os
import re
import urllib.error
import urllib.parse
import urllib.request

ENV_CHAVE, ENV_CX = "SINTONIA_GOOGLE_CSE_KEY", "SINTONIA_GOOGLE_CSE_CX"
SEGREDOS = (ENV_CHAVE, ENV_CX, "SINTONIA_BRAVE_KEY")
ENDERECO_CSE = "https://www.googleapis.com/customsearch/v1"
QUOTA_DIA = {"GOOGLE_CSE": 100}
TIMEOUT = 30
_RE_KEY = re.compile(r"(?i)(key|cx)=[^&\s\"']+")


def redigir(texto, env=None) -> str:
    """O texto sem a chave nem o CX (pelo valor e pela forma `key=`/`cx=`)."""
    env = os.environ if env is None else env
    t = str(texto or "")
    for n in SEGREDOS:
        v = env.get(n)
        if v and len(v) >= 4:
            t = t.replace(v, "***")
    return _RE_KEY.sub(lambda m: m.group(1) + "=***", t)


def pedir(url: str, cabecalhos: dict | None = None, timeout: float = TIMEOUT) -> tuple[int, bytes, str]:
    """→ (http, corpo, erro). O corpo do erro volta tambem: e nele que o Google diz o porque."""
    req = urllib.request.Request(url, headers=dict(cabecalhos or {}, Accept="application/json"))
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, r.read(2_000_000), ""
    except urllib.error.HTTPError as e:
        return e.code, (e.read(2_000_000) if e.fp else b""), "HTTP %d" % e.code
    except Exception as e:                                               # noqa: BLE001
        return 0, b"", redigir("%s: %s" % (type(e).__name__, e))


# ── o passo 0 ───────────────────────────────────────────────────────────────────────────────────
def _erro_do_google(corpo: bytes) -> dict:
    """Os campos que o Google poe no erro: status, reason(s) de errors[] e de details[] (ErrorInfo), mensagem."""
    try:
        e = (json.loads(corpo or b"{}") or {}).get("error") or {}
    except ValueError:
        return {"MENSAGEM": corpo[:300].decode("utf-8", "replace"), "RAZOES": [], "STATUS": None}
    razoes = [x.get("reason") for x in (e.get("errors") or []) if x.get("reason")]
    razoes += [x.get("reason") for x in (e.get("details") or []) if isinstance(x, dict) and x.get("reason")]
    return {"STATUS": e.get("status"), "RAZOES": razoes, "MENSAGEM": e.get("message") or ""}


def ler_diagnostico(http: int, corpo: bytes, erro: str, *, com_cx: bool) -> dict:
    """A resposta da UMA chamada → o que ela prova. Cada campo: SIM / NAO / NAO_SEI, e o porque."""
    d = {"HTTP": http, "CX_PASSADO": com_cx, "API_ATIVA": "NAO_SEI", "CHAVE_PODE_USAR_A_API": "NAO_SEI",
         "CX": "PASSADO" if com_cx else "AUSENTE", "BUSCA_POSSIVEL": "NAO"}
    if http == 200:
        j = json.loads(corpo or b"{}")
        itens = j.get("items") or []
        dominios = sorted({urllib.parse.urlsplit(i.get("link", "")).hostname or "" for i in itens} - {""})
        d.update(API_ATIVA="SIM", CHAVE_PODE_USAR_A_API="SIM", CX="VALIDO", BUSCA_POSSIVEL="SIM",
                 RESULTADOS=len(itens), DOMINIOS_DOS_RESULTADOS=dominios,
                 TOTAL_ESTIMADO=(j.get("searchInformation") or {}).get("totalResults"),
                 PORQUE="a API respondeu 200 com o CX dado",
                 # INDICIO, nao prova: um mecanismo limitado a uma lista de sites so devolve esses sites. A
                 # pergunta «pesquisa a web inteira?» responde-se no painel do mecanismo, nao aqui.
                 ESCOPO_INDICIO=("MUITOS_SITES: %d dominios em %d resultados — parece a web inteira ou uma lista "
                                 "grande (NAO e prova)" % (len(dominios), len(itens)) if len(dominios) >= 5 else
                                 "POUCOS_SITES: %d dominio(s) em %d resultados — o mecanismo parece limitado a uma "
                                 "lista de sites (NAO e prova)" % (len(dominios), len(itens))))
        return d
    if http == 0:
        d["PORQUE"] = "a chamada nao chegou ao Google (%s) — nada se prova" % redigir(erro)
        return d
    g = _erro_do_google(corpo)
    razoes = {r.upper() for r in g["RAZOES"]}
    msg = redigir(g["MENSAGEM"])
    d.update(ERRO_STATUS=g["STATUS"], ERRO_RAZOES=sorted(g["RAZOES"]), ERRO_MENSAGEM=msg[:400])
    m = msg.lower()
    if razoes & {"SERVICE_DISABLED", "ACCESSNOTCONFIGURED"} or "has not been used in project" in m \
            or "it is disabled" in m:
        d.update(API_ATIVA="NAO", PORQUE="a Custom Search JSON API nao esta ativada neste projeto do Google Cloud")
    elif razoes & {"API_KEY_SERVICE_BLOCKED"} or "are blocked" in m:
        d.update(API_ATIVA="NAO_SEI", CHAVE_PODE_USAR_A_API="NAO",
                 PORQUE="a chave tem restricao de API: so pode chamar outras APIs (ex.: so a YouTube Data API)")
    elif razoes & {"API_KEY_INVALID", "KEYINVALID"} or "api key not valid" in m:
        d.update(CHAVE_PODE_USAR_A_API="NAO", PORQUE="a chave nao e valida (o Google nao a reconhece)")
    elif razoes & {"API_KEY_HTTP_REFERRER_BLOCKED", "API_KEY_IP_ADDRESS_BLOCKED", "API_KEY_ANDROID_APP_BLOCKED",
                   "API_KEY_IOS_APP_BLOCKED"}:
        d.update(CHAVE_PODE_USAR_A_API="NAO",
                 PORQUE="a chave tem restricao de aplicacao (site/IP/app) que barra este runner")
    elif "does not have the access to custom search json api" in m:
        d.update(API_ATIVA="SIM", CHAVE_PODE_USAR_A_API="NAO",
                 PORQUE="o projeto nao tem acesso a Custom Search JSON API (o Google fechou-a a clientes novos?)")
    elif http == 429 or razoes & {"RATELIMITEXCEEDED", "DAILYLIMITEXCEEDED", "RATE_LIMIT_EXCEEDED"} \
            or g["STATUS"] == "RESOURCE_EXHAUSTED":
        d.update(API_ATIVA="SIM", CHAVE_PODE_USAR_A_API="SIM", PORQUE="quota esgotada (a API esta ligada)")
    elif http == 400 and (g["STATUS"] == "INVALID_ARGUMENT" or razoes & {"INVALID", "BADREQUEST"}):
        # A porta do Google (ligada? chave pode?) vem ANTES da validacao dos parametros: um 400 de argumento
        # quer dizer que a API esta ligada e a chave pode — o que faltou foi o pedido.
        d.update(API_ATIVA="SIM", CHAVE_PODE_USAR_A_API="SIM",
                 CX="OBRIGATORIO_E_AUSENTE" if not com_cx else "INVALIDO",
                 PORQUE=("sem CX o Google recusa o pedido: o CX e OBRIGATORIO (medido)" if not com_cx
                         else "o CX dado nao e valido para esta chave"))
    else:
        d["PORQUE"] = "resposta que este diagnostico nao conhece — ver ERRO_*"
    return d


def diagnosticar_cse(pedir_=None, env=None) -> dict:
    """UMA chamada. Com CX: uma busca de 10 resultados (1 das 100 consultas do dia). Sem CX: o pedido sem ele — mede se o CX
    e obrigatorio e, de caminho, se a API esta ligada e se a chave pode."""
    env = os.environ if env is None else env
    chave, cx = env.get(ENV_CHAVE), env.get(ENV_CX)
    if not chave:
        return {"HTTP": None, "API_ATIVA": "NAO_SEI", "CHAVE_PODE_USAR_A_API": "NAO_SEI", "CX": "NAO_SEI",
                "BUSCA_POSSIVEL": "NAO", "CHAMADAS": 0,
                "PORQUE": "o segredo da chave nao chegou ao ambiente (%s vazio) — nenhuma chamada saiu" % ENV_CHAVE,
                "O_QUE_O_DONO_FAZ": ["Conferir no GitHub (Settings > Secrets and variables > Actions) se o secret com o "
                                     "nome pedido existe — o workflow nao recebeu nenhuma chave."]}
    # 10 resultados custam o MESMO que 1 (a quota conta consultas): os 10 dizem de quantos sites vem a busca
    q = {"key": chave, "q": "agricoltura", "num": 10}
    if cx:
        q["cx"] = cx
    http, corpo, erro = (pedir_ or pedir)(ENDERECO_CSE + "?" + urllib.parse.urlencode(q))
    d = ler_diagnostico(http, corpo, erro, com_cx=bool(cx))
    d["CHAMADAS"] = 1
    d["O_QUE_O_DONO_FAZ"] = o_que_o_dono_faz(d)
    return d


def o_que_o_dono_faz(d: dict) -> list:
    """Em palavras simples, so o que falta — pela ordem."""
    passos = []
    if d.get("CHAVE_PODE_USAR_A_API") == "NAO" and "restricao de API" in (d.get("PORQUE") or ""):
        passos.append("No Google Cloud, em APIs e servicos > Credenciais, abrir a chave e acrescentar a "
                      "'Custom Search API' a lista de APIs que ela pode chamar (hoje ela so pode outras).")
    if d.get("API_ATIVA") == "NAO":
        passos.append("No Google Cloud, no MESMO projeto da chave, ativar a 'Custom Search API' "
                      "(APIs e servicos > Biblioteca > Custom Search API > Ativar).")
    if d.get("CX") in ("AUSENTE", "OBRIGATORIO_E_AUSENTE", "INVALIDO", "NAO_SEI"):
        passos.append("Em programmablesearchengine.google.com, criar um mecanismo de busca (ou abrir o que ja "
                      "existe), copiar o 'ID do mecanismo de pesquisa' (esse ID e o CX) e grava-lo no GitHub como secret "
                      "GOOGLE_CSE_CX (Settings > Secrets and variables > Actions).")
    if "clientes novos" in (d.get("PORQUE") or ""):
        passos.append("Confirmar com o Google se este projeto ainda pode usar a Custom Search JSON API; se nao, "
                      "a alternativa e outro motor oficial (ex.: Brave Search API) — decisao do dono.")
    if d.get("CHAVE_PODE_USAR_A_API") == "NAO" and "nao e valida" in (d.get("PORQUE") or ""):
        passos.append("Conferir se o secret escolhido tem mesmo a chave do Google (ela nao foi reconhecida).")
    return passos or (["Nada: a busca pode correr."] if d.get("BUSCA_POSSIVEL") == "SIM" else
                      ["NAO SEI: ver o ERRO_* no DIAGNOSTICO.json."])


class ErroDaApi(RuntimeError):
    """Levantada pelo transporte da API; a mensagem ja vem redigida."""


def transporte(pedir_=None):
    """O `buscar(url, cab)` que `linha_busca.buscar_consultas` espera, pela API: → (corpo, meta) ou ErroDaApi."""
    def buscar(url, cabecalhos=None):
        http, corpo, erro = (pedir_ or pedir)(url, cabecalhos)
        if http != 200:
            g = _erro_do_google(corpo)
            raise ErroDaApi(redigir("%s %s %s" % (erro or "HTTP %s" % http, ",".join(g["RAZOES"]), g["MENSAGEM"][:200])))
        return corpo, {"CONTENT_TYPE": "application/json", "STATUS": http, "ROTA": "API_OFICIAL (D91)"}
    return buscar
