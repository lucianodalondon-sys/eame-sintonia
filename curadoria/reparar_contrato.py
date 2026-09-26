#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""REPARAR O CONTRATO — a fonte ja achada volta a ser trabalho, nao lixo.

    UMA FONTE CUJO CANARIO FALHOU TEM UM DEFEITO COM NOME. O BOT CONSERTA-O.

Medido no livro vivo (23/09/2026, missao R1 REPARO-FONTES-V1): 400 fontes em
CONTRACTED_CANARY_FAILED e 102 em CANARY_PENDING, NENHUMA com tarefa aberta na
fila. 344 das 400 pararam no mesmo defeito — «nenhum dos N enderecos da entrada
casa com o padrao — EMPTY_LIST»: o LINK_PATTERN e o molde WordPress da missao
04, escrito sem ler a pagina (369/375 contratos das falhadas sao esse molde).
A 6-PREP-d mediu o mesmo: 61/121 padroes nao casam NENHUM link da propria
entrada. O bot marcava e parava; ninguem voltava a elas.

Este modulo e o reparo DETERMINISTICO, sem LLM, com o metodo que a casa ja
provou — e so ele:

  · a LISTAGEM e os itens debaixo dela: `provar_listagem.py` (CANDIDATE-FEEDER-V1)
    — seccao de noticias, itens com slug de 2+ hifens ou ano no caminho;
  · a FAMILIA de enderecos com o mesmo esqueleto: `scripts/receitas/
    censo_e_proposta.py` (6-PREP-d) — numero -> \\d+, titulo -> slug, seccao
    constante -> literal; familia >= 2; e o GUARDA `e_generico`, que recusa o
    padrao que case o INDEX_URL, navegacao sintetica, navegacao da entrada ou
    mais de 80 % dos links;
  · os enderecos vistos pelo MESMO leitor do canario (`canario.hrefs_da_entrada`)
    e o item aberto pela MESMA ordem dele (o primeiro, ordenado): propor um
    padrao sobre outra lista de links seria provar outra coisa.

A TRAVA DO DONO (6-PREP-d, trava 3): «nenhum padrao nasce sem uma materia
lida». Aqui a materia e lida pela MAQUINA: o item que o canario vai abrir e
aberto e retratado (`retrato_html`), e so se aceita CONTENT + MATERIA_PROVAVEL
com >= 800 caracteres em paragrafos — o BODY_UTIL da regua dos quatro passos.
⚠️ O juiz e o da casa, com os erros medidos dele (noticia curta com menu grande
sai capa; 5/14 indices saem CONTENT). Por isso o reparo NAO promove: escreve
uma HIPOTESE de rota, e quem decide READY continua a ser o canario seguinte com
a regua dos quatro passos (worker.executar_uma). Reparar != aprovar.

O QUE O REPARO RECUSA (e escreve porque) — nunca «resolve» a martelo:

  ENTRADA_INSTITUCIONAL  a «fonte» e Contatti, Privacy, Whistleblowing, troca de
                         lingua, Amministrazione Trasparente... — o discovery
                         fez de uma pagina de servico uma fonte. Nao ha materia
                         a colher ali; um padrao «achado» nela seria lixo.
  ENTRADA_E_MATERIA      a «fonte» e UMA noticia (slug no fim + corpo de
                         materia). Os links dela sao «leia tambem» de outra
                         fonte: reparar daria a mesma colheita em dobro.
  SEM_FAMILIA_DE_ITENS   a entrada (e a seccao, se houver) nao lista 2+ itens
                         com o mesmo esqueleto.
  ITEM_NAO_E_MATERIA     havia familia, mas o item que o canario abriria nao
                         tem corpo de materia.
  FAMILIA_ESTATICA       ha familias, mas nenhuma tem cara de fluxo de
                         publicacoes (paginas fixas: servicos, uffici, tributi).
  DUPLICADA              o padrao achado ja e de outra fonte (READY ou
                         reparada): o mesmo documento nao tem dois donos.
  ENTRADA_HTTP_<n>       a entrada respondeu 404/410/... — a fonte mudou de casa.

Transporte, 429/503 e robots ilegivel sao RETRY (NAO SEI != morta). 401/403 e
AUTH; Disallow lido e ROBOTS — BLOCK, como no resto do worker.

A ESCRITA (`aplicar`) e a porta de contratos deste reparo, com a forma da D10
(`scripts/desbloqueio/aplicar_desbloqueio.contrato_unico`): muda SO a
ACQUISITION (INDEX_URL e LINK_PATTERN), guarda a anterior, escreve a prova e
PRECISA_DE_REMEDIR, recalcula o hash, passa o validador da casa
(`validar_contratos.validar`) e rebenta se tocar noutro campo. Nunca a mao.
"""
from __future__ import annotations

import copy
import importlib.util
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import parse_qsl, urlparse

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "curadoria"))

import canario as CAN            # noqa: E402  (buscar + hrefs_da_entrada: o leitor do canario)
import gate_de_rota as GATE      # noqa: E402
import provar_listagem as PL     # noqa: E402  (listagem -> itens: o metodo da CANDIDATE-FEEDER-V1)
import retrato_html as RH        # noqa: E402

_spec = importlib.util.spec_from_file_location(
    "censo_e_proposta", RAIZ / "scripts" / "receitas" / "censo_e_proposta.py")
RC = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(RC)     # esqueleto/padrao_de/e_generico: o metodo da 6-PREP-d

METODO = "REPARO-DE-CONTRATO/v1"
MISSAO = "REPARO-FONTES-V1"

# WHY 4: o teto da casa para uma fonte (provar_listagem.MAX_PEDIDOS_POR_FONTE).
# Entrada + no maximo 1 seccao + no maximo 2 itens. O robots.txt nao conta aqui
# (lido uma vez por anfitriao e guardado neste processo).
MAX_PEDIDOS = 4
# WHY 2 s: o canario e o provar_listagem usam 0,8-1 s entre pedidos a FONTES
# diferentes; aqui varias fontes partilham o anfitriao (42 no crea.gov.it), e o
# canario vem logo a seguir. 2 s por anfitriao e o dobro, e nao adormece a fila:
# so espera quem acabou de bater no MESMO anfitriao.
PAUSA_POR_ANFITRIAO_S = 2.0
# WHY 3 familias: o teto de pedidos (MAX_PEDIDOS) corta antes quando houve seccao. Alem da 3.a ficam
# na prova como vistas e nao tentadas (medido: no crea a 1.a e a 2.a eram menu).
MAX_FAMILIAS_TENTADAS = 3
# WHY 800: o BODY_UTIL da regua (ready_split.passos_da_promocao) — o mesmo
# numero, lido do dono (retrato_html.PARAGRAFO_MINIMO).
CORPO_MINIMO = RH.PARAGRAFO_MINIMO

# Paginas de servico: o nome diz o que sao. Casa no CAMINHO da entrada.
_INSTITUCIONAL = re.compile(
    r"(?:contatt|contact|whistleblow|privacy|cookie|update_language|languageId=|"
    r"amministrazione-trasparente|accesso-civico|note-legali|mappa-del-sito|sitemap|"
    r"chi-siamo|/organi(?:/|$)|link-utili|login|/search|cerca\b|carta-europea|"
    r"piano-triennale|riferimenti-normativi|lavora-con-noi|dove-siamo|accessibilita|"
    r"direzione-generale|conosci-il|/home1?/?$|/contatti)", re.I)
_BINARIO = re.compile(r"\.(?:pdf|jpe?g|png|gif|svg|webp|zip|docx?|xlsx?|pptx?|mp[34]|xml|rss|ics)$",
                      re.I)

_ROBOTS: dict = {}
_ULTIMO_PEDIDO: dict = {}


def agora() -> str:
    return datetime.now(timezone.utc).isoformat()


def _host(u: str) -> str:
    return urlparse(u).netloc.lower().removeprefix("www.")


def entrada_institucional(url: str) -> str | None:
    """A entrada e uma pagina de servico? Devolve o pedaco que o diz, ou None."""
    u = urlparse(url)
    m = _INSTITUCIONAL.search((u.path or "/") + ("?" + u.query if u.query else ""))
    return m.group(0) if m else None


def _e_materia(ret: dict) -> bool:
    return (ret.get("HTML_KIND") == "CONTENT"
            and ret.get("CAPA_OU_MATERIA") == "MATERIA_PROVAVEL"
            and (ret.get("PARAGRAPH_CHARACTERS") or 0) >= CORPO_MINIMO)


def entrada_e_materia(url: str, ret: dict) -> bool:
    """A entrada e UMA noticia: o ultimo segmento tem cara de item (slug ou numero)
    E o corpo e de materia. Uma das duas sozinha nao chega (medido: 5/14 indices
    saem CONTENT; e /news/2024/ tem numero e e listagem)."""
    _, segs, _ = RC.esqueleto(url)
    return bool(segs) and segs[-1] in ("SLUG", "NUM") and _e_materia(ret)


def familias(hrefs: set[str], listagem: str) -> list[dict]:
    """Os padroes possiveis numa pagina, do mais povoado para o menos. Sem rede.

    [{"PADRAO", "MEMBROS", "COMO"}]. So o anfitriao da listagem conta; binarios
    e navegacao nao sao itens; tudo passa pelo GUARDA da 6-PREP-d.
    """
    host = _host(listagem)
    mesmos = sorted(h for h in hrefs if _host(h) == host)
    uteis = [h for h in mesmos if not _BINARIO.search(urlparse(h).path)
             and h.rstrip("/") != listagem.rstrip("/")]
    vistos, out = set(), []

    def _junta(padrao: str, como: str):
        if padrao in vistos:
            return
        vistos.add(padrao)
        try:
            rx = re.compile(padrao)
        except re.error:
            return
        membros = [h for h in uteis if rx.match(h)]
        if len(membros) < 2:                                  # MINIMO_DE_LIGACOES
            return
        if RC.e_generico(padrao, listagem, mesmos, []) is not None:
            return
        if rx.match(listagem.rstrip("/")) or rx.match(listagem):
            return                                            # a porta do validador
        out.append({"PADRAO": padrao, "MEMBROS": len(membros), "COMO": como,
                    "EXEMPLOS": membros[:3], "FLUXO": fluxo(listagem, padrao, membros)})

    # 1) a listagem e os itens debaixo dela (provar_listagem)
    if (urlparse(listagem).path or "/").strip("/"):
        itens = PL._itens_sob(listagem, [h.split("?")[0] for h in uteis])
        if len(itens) >= 2:
            _junta(PL._padrao(listagem), "LISTAGEM_E_ITENS_SOB_ELA (provar_listagem)")

    # 2) familias por esqueleto (receitas 6-PREP-d)
    grupos: dict = {}
    for h in uteis:
        if RC.NAVEGACAO.search(h):
            continue
        e = RC.esqueleto(h)
        _, segs, q = e
        item = (segs and segs[-1] in ("SLUG", "NUM")) or any(t == "NUM" for _, t in q)
        if item:
            grupos.setdefault(e, []).append(h)
    for e, membros in grupos.items():
        if len(membros) >= 2:
            _junta(RC.padrao_de(e, membros[0], membros[1:]), "FAMILIA_POR_ESQUELETO (receitas 6-PREP-d)")

    out.sort(key=lambda x: (-x["MEMBROS"], x["COMO"], x["PADRAO"]))
    return out


# ── FLUXO DE PUBLICACOES, NAO PAGINAS FIXAS ─────────────────────────────────
# Medido na 1.a medicao em copia (23/09, 4 bancas): 42 fontes chegaram a READY
# pelo reparo, e pelo menos 12 tinham como «documento» uma pagina FIXA do site —
# «accesso-civico», «1010000-ufficio-gabinetto», «area-personale-tributi»,
# «brand-e-immagine-coordinata», «LAssociazione/Area-Studi». O juiz da casa
# (retrato_html) mede texto e ligacoes: uma pagina institucional longa e
# MATERIA para ele, e a regua dos quatro passos passa-a. Colher isso na Big
# Collection seria guardar a repartição como noticia.
#
# Uma fonte de materias publica: a familia tem de ter CARA DE FLUXO, por UM de:
#   · vocabulario de publicacao no caminho da listagem ou dos itens — a lista da
#     casa, `provar_listagem._SECCAO_LARGA` (news, notizie, comunicati, stampa,
#     eventi, blog, bollettini, avvisi, pubblicazioni, articoli...);
#   · um marcador que so as publicacoes tem: segmento numerico, ano no caminho
#     (`provar_listagem._ITEM_ANO`) ou id numerico na query;
#   · titulo longo: mediana >= FLUXO_PALAVRAS palavras no ultimo segmento.
#     WHY 6: nas 42 medidas, as paginas fixas tinham 2-5 palavras
#     («area-personale-tributi», «brand-e-immagine-coordinata»); as noticias
#     6-20. ⚠️ Custo medido na mesma amostra: 2 fontes boas saem (issuu
#     /docs/<titulo-de-5-palavras>, e uma noticia da ARPAL com 5), e ~5 paginas
#     fixas de titulo longo continuam a passar. Heuristica declarada, nao juiz.
FLUXO_PALAVRAS = 6


def fluxo(listagem: str, padrao: str, membros: list[str]) -> str | None:
    """Porque esta familia parece um fluxo de publicacoes — ou None (pagina fixa)."""
    caminhos = [urlparse(listagem).path] + [urlparse(m).path for m in membros]
    for c in caminhos:
        m = PL._SECCAO_LARGA.search(c)
        if m:
            return "vocabulario de publicacao: %s" % m.group(0)
    for u in membros:
        pu = urlparse(u)
        if re.search(r"(?:^|/)\d+(?:/|$)", pu.path) or PL._ITEM_ANO.search(pu.path):
            return "numero ou ano no caminho: %s" % pu.path[:60]
        if any(v.isdigit() for _, v in parse_qsl(pu.query)):
            return "id numerico na query: %s" % pu.query[:40]
    pal = sorted(_palavras(m) for m in membros) or [0]
    if pal[len(pal) // 2] >= FLUXO_PALAVRAS:
        return "titulos longos (mediana %d palavras)" % pal[len(pal) // 2]
    return None


class _Leitor:
    """Os pedidos de UM reparo: robots da casa, teto, pausa por anfitriao."""

    def __init__(self, buscar, robots_de, permitido, pausa: float):
        self.buscar, self.robots_de, self.permitido = buscar, robots_de, permitido
        self.pausa, self.pedidos, self.vistos = pausa, 0, []
        self.destino = ""

    def robots(self, url: str) -> tuple[str, str]:
        """('OK'|'RETRY'|'ROBOTS', porque)."""
        h = urlparse(url).netloc
        if h not in _ROBOTS:
            try:
                _ROBOTS[h] = self.robots_de(h)
            except Exception as e:                            # noqa: BLE001
                return "RETRY", "robots.txt ilegivel: %s" % type(e).__name__
        rp, origem = _ROBOTS[h]
        if "inacessivel" in origem:
            _ROBOTS.pop(h, None)                              # NAO SEI: tentar noutra volta
            return "RETRY", "robots nao pode ser lido — UNKNOWN, nao proibicao"
        if not self.permitido(url, rp):
            return "ROBOTS", "o endereco casa com Disallow no robots vivo"
        return "OK", origem[:100]

    def get(self, url: str):
        if self.pedidos >= MAX_PEDIDOS:
            return None, b"", "teto de %d pedidos" % MAX_PEDIDOS
        h = _host(url)
        falta = self.pausa - (time.time() - _ULTIMO_PEDIDO.get(h, 0))
        if falta > 0:
            time.sleep(falta)
        self.pedidos += 1
        r = self.buscar(url)
        st, b, err = r[:3]
        destino = r[3] if len(r) > 3 and r[3] else url
        _ULTIMO_PEDIDO[h] = time.time()
        self.vistos.append({"URL": url, "HTTP": st, "BYTES": len(b or b""),
                            **({"DESTINO": destino} if destino != url else {})})
        self.destino = destino
        return st, b, err


def buscar_com_destino(url: str) -> tuple[int, bytes, str, str]:
    """`canario.buscar` (mesmo UA, timeout, TLS e teto de 4 MB) + o endereco final
    depois dos redireccionamentos, que o canario nao devolve."""
    import urllib.error
    import urllib.request
    req = urllib.request.Request(CAN.url_segura(url), headers={        # acento no link (BLOQUEADAS-268)
        "User-Agent": CAN.CAP.UA, "Accept": "*/*", "Accept-Language": "it-IT,it;q=0.9"})
    try:
        with urllib.request.urlopen(req, timeout=CAN.TIMEOUT, context=CAN.CTX) as r:
            return r.status, r.read(4_000_000), "", r.geturl()
    except urllib.error.HTTPError as e:
        return e.code, b"", "HTTP %d" % e.code, url
    except Exception as e:                                    # noqa: BLE001
        return 0, b"", "%s: %s" % (type(e).__name__, str(e)[:90]), url


def _resposta_http(st, err) -> dict | None:
    """Traduz uma entrada que nao abriu. None = abriu."""
    if st == 200:
        return None
    if st in (401, 403):
        return {"DESFECHO": "BLOCK", "CLASSE": "AUTH",
                "PORQUE": "HTTP %s na entrada: a fonte respondeu que nao a esta identidade" % st}
    if st in (0, None, 429, 500, 502, 503, 504):
        return {"DESFECHO": "RETRY", "PORQUE": "entrada sem resposta util (%s) — NAO SEI, nao morta"
                % (err or st)}
    return {"DESFECHO": "RECUSA", "MOTIVO": "ENTRADA_HTTP_%s" % st,
            "PORQUE": "a entrada respondeu HTTP %s: a fonte mudou de casa ou saiu do ar" % st}


def inferir(contrato: dict, *, outros: dict | None = None, buscar=None, robots_de=None,
            permitido=None, pausa: float = PAUSA_POR_ANFITRIAO_S) -> dict:
    """UMA fonte. Devolve {"DESFECHO": PADRAO_NOVO|RECUSA|RETRY|BLOCK, ...}. Nunca escreve.

    `outros` = {SOURCE_ID: contrato} das fontes cujo documento ja tem dono (READY
    ou ja reparadas), para a guarda DUPLICADA. Rede injectavel (testes sem rede).
    """
    L = _Leitor(buscar or buscar_com_destino, robots_de or GATE.robots_de,
                permitido or GATE.permitido, pausa)
    aq = contrato.get("ACQUISITION") or {}
    entrada = aq.get("INDEX_URL") or contrato.get("CANONICAL_ENTRY_URL") or ""
    base = {"METODO": METODO, "ENTRADA": entrada, "ACQUISITION_ANTERIOR": copy.deepcopy(aq)}

    def fim(d: dict) -> dict:
        return dict(base, **d, PEDIDOS=L.pedidos, PAGINAS_LIDAS=L.vistos)

    if aq.get("STRATEGY") not in (None, "HTML_LINK_DISCOVERY"):
        return fim({"DESFECHO": "RECUSA", "MOTIVO": "ESTRATEGIA_SEM_REPARO",
                    "PORQUE": "o reparo so conhece HTML_LINK_DISCOVERY, nao %s" % aq.get("STRATEGY")})
    if not entrada.startswith("http"):
        return fim({"DESFECHO": "RECUSA", "MOTIVO": "SEM_ENTRADA",
                    "PORQUE": "contrato sem INDEX_URL nem CANONICAL_ENTRY_URL"})
    inst = entrada_institucional(entrada)
    if inst:
        return fim({"DESFECHO": "RECUSA", "MOTIVO": "ENTRADA_INSTITUCIONAL",
                    "PORQUE": "a entrada e uma pagina de servico (%s), nao uma fonte de materias"
                              % inst})

    r, porque = L.robots(entrada)
    if r != "OK":
        return fim({"DESFECHO": "RETRY" if r == "RETRY" else "BLOCK", "CLASSE": r,
                    "PORQUE": porque})
    st, b, err = L.get(entrada)
    mau = _resposta_http(st, err)
    if mau:
        return fim(mau)
    if not b or b.lstrip().removeprefix(b"\xef\xbb\xbf")[:1] != b"<":
        return fim({"DESFECHO": "RECUSA", "MOTIVO": "ENTRADA_NAO_E_HTML",
                    "PORQUE": "a entrada abriu e nao e HTML"})
    ret_e = RH.retrato_do_html(b)
    base["ENTRADA_RETRATO"] = {k: ret_e[k] for k in ("HTML_KIND", "CAPA_OU_MATERIA", "LINKS",
                                                      "PARAGRAPH_CHARACTERS", "TEXT_SHA256")}
    if entrada_e_materia(entrada, ret_e):
        return fim({"DESFECHO": "RECUSA", "MOTIVO": "ENTRADA_E_MATERIA",
                    "PORQUE": ("a entrada e UMA noticia (item no fim do caminho, %d caracteres em "
                               "paragrafos): nao e uma fonte, e os links dela sao de outra"
                               % ret_e["PARAGRAPH_CHARACTERS"])})

    # ⚠️ A ENTRADA PODE TER MUDADO DE CASA (medido: confagricolturalombardia.it
    # responde de lombardia.confagricoltura.it). Os links sao do anfitriao de
    # DESTINO; julga-los pelo antigo dava «sem familia» a uma pagina cheia de
    # noticias. O contrato reparado passa a apontar para o destino.
    if _host(L.destino) != _host(entrada):
        base["ENTRADA_REDIRECCIONADA_PARA"] = L.destino
        entrada = L.destino
        r, porque = L.robots(entrada)                         # o robots e o do destino
        if r != "OK":
            return fim({"DESFECHO": "RETRY" if r == "RETRY" else "BLOCK", "CLASSE": r,
                        "PORQUE": "destino %s: %s" % (entrada, porque)})
    listagem, hrefs = entrada, CAN.hrefs_da_entrada(b, entrada)
    todas = familias(hrefs, listagem)
    cands = [c for c in todas if c["FLUXO"]]
    estaticas = [c for c in todas if not c["FLUXO"]]
    seccao_tentada = None
    if not cands:
        # a entrada nao lista itens: descer a seccao de noticias (provar_listagem)
        internos = PL._links_internos(b.decode("utf-8", "replace"), entrada)
        for s in PL._seccoes(internos)[:1]:
            if s.rstrip("/") == entrada.rstrip("/") or entrada_institucional(s):
                continue
            seccao_tentada = s
            r, porque = L.robots(s)
            if r != "OK":
                break
            st2, b2, err2 = L.get(s)
            if st2 != 200 or not b2:
                break
            listagem, hrefs = s, CAN.hrefs_da_entrada(b2, s)
            todas = familias(hrefs, listagem)
            cands = [c for c in todas if c["FLUXO"]]
            estaticas += [c for c in todas if not c["FLUXO"]]
    base["SECCAO_TENTADA"] = seccao_tentada
    base["FAMILIAS_VISTAS"] = cands[:5]
    base["FAMILIAS_ESTATICAS"] = estaticas[:5]
    if not cands and estaticas:
        return fim({"DESFECHO": "RECUSA", "MOTIVO": "FAMILIA_ESTATICA",
                    "PORQUE": ("so ha familias de paginas fixas (%s...): nenhuma tem cara de fluxo "
                               "de publicacoes" % estaticas[0]["EXEMPLOS"][0][:70])})
    if not cands:
        return fim({"DESFECHO": "RECUSA", "MOTIVO": "SEM_FAMILIA_DE_ITENS",
                    "PORQUE": ("nem a entrada%s lista 2+ itens com o mesmo esqueleto"
                               % (" nem a seccao %s" % seccao_tentada if seccao_tentada else ""))})

    tentados = []
    for cand in cands[:MAX_FAMILIAS_TENTADAS]:
        rx = re.compile(cand["PADRAO"])
        # ⚠️ O MESMO ITEM QUE O CANARIO VAI ABRIR: todos os hrefs, ordenados, o 1.o.
        alvos = [h for h in sorted(hrefs) if rx.match(h)]
        alvo = alvos[0]
        dono = _dono(alvo, cand["PADRAO"], outros or {}, contrato.get("SOURCE_ID"))
        if dono:
            tentados.append(dict(cand, ALVO=alvo, VEREDITO="DUPLICADA de %s" % dono))
            continue
        r, porque = L.robots(alvo)
        if r != "OK":
            tentados.append(dict(cand, ALVO=alvo, VEREDITO="robots: %s" % porque))
            continue
        st3, b3, err3 = L.get(alvo)
        if st3 != 200 or not b3:
            tentados.append(dict(cand, ALVO=alvo, VEREDITO="item nao abriu: %s" % (err3 or st3)))
            continue
        ret = RH.retrato_do_html(b3)
        item = {"URL": alvo, "HTTP": st3, "BYTES": len(b3),
                **{k: ret[k] for k in ("HTML_KIND", "CAPA_OU_MATERIA", "LINKS",
                                       "NON_WHITESPACE_CHARACTERS", "PARAGRAPH_CHARACTERS",
                                       "TEXT_SHA256")}}
        menu = e_menu(alvos, CAN.hrefs_da_entrada(b3, alvo))
        if menu:
            tentados.append(dict(cand, ALVO=alvo, ITEM=item, VEREDITO=menu))
            continue
        if not _e_materia(ret):
            tentados.append(dict(cand, ALVO=alvo, ITEM=item,
                                 VEREDITO="%s/%s, %d em paragrafos (< %d ou nao e materia)"
                                 % (ret["HTML_KIND"], ret["CAPA_OU_MATERIA"],
                                    ret["PARAGRAPH_CHARACTERS"], CORPO_MINIMO)))
            continue
        tentados.append(dict(cand, ALVO=alvo, ITEM=item, VEREDITO="MATERIA"))
        return fim({"DESFECHO": "PADRAO_NOVO", "INDEX_URL": listagem,
                    "LINK_PATTERN": cand["PADRAO"], "COMO": cand["COMO"],
                    "ALVOS_NA_LISTAGEM": len(alvos), "ITEM_LIDO": item, "TENTADOS": tentados,
                    "PORQUE": ("%s: %d itens na listagem, o 1.o (o do canario) e materia "
                               "com %d caracteres em paragrafos"
                               % (cand["COMO"].split(" ")[0], len(alvos),
                                  ret["PARAGRAPH_CHARACTERS"]))})
    so_dup = all(t["VEREDITO"].startswith("DUPLICADA") for t in tentados)
    return fim({"DESFECHO": "RECUSA",
                "MOTIVO": "DUPLICADA" if so_dup else "ITEM_NAO_E_MATERIA",
                "TENTADOS": tentados,
                "PORQUE": ("; ".join("%s -> %s" % (t["ALVO"][:70], t["VEREDITO"][:60])
                                     for t in tentados))[:300]})


# WHY 0,8 e 4: medido no 1.o ensaio (crea.gov.it, 23/09): a familia mais povoada
# da home era `/web/<centro>` — as 12 paginas dos centros de investigacao, que
# estao no MENU de todas as paginas; o item aberto (a home de um centro) tinha
# 3874 caracteres em paragrafos e o juiz disse MATERIA. Uma lista de noticias
# muda de pagina para pagina; um menu repete-se inteiro. 80 % da familia
# repetida no item = menu. Com menos de 4 membros nao se decide (NAO SEI: fica o
# juiz).
#
# ⚠️ Mas o widget «ultimas noticias» do WordPress tambem se repete em cada
# artigo. O que separa os dois e o NOME: um menu nomeia seccoes
# («difesa-e-certificazione», 3 palavras), uma noticia tem titulo
# («il-crea-protagonista-della-notte-europea-...», 10+). So e menu se, alem de
# repetido, a mediana das palavras do ultimo segmento for < 5.
MENU_FRACCAO = 0.8
MENU_MINIMO = 4
MENU_PALAVRAS_MAX = 5


def _palavras(u: str) -> int:
    ult = [s for s in urlparse(u).path.split("/") if s]
    return len(re.split(r"[-_]+", ult[-1])) if ult else 0


def e_menu(membros: list[str], hrefs_do_item: set[str]) -> str | None:
    """A familia repete-se quase inteira dentro do item, com nomes curtos? Navegacao."""
    if len(membros) < MENU_MINIMO:
        return None
    pal = sorted(_palavras(m) for m in membros)
    if pal[len(pal) // 2] >= MENU_PALAVRAS_MAX:
        return None
    norm = {h.rstrip("/") for h in hrefs_do_item}
    dentro = sum(1 for m in membros if m.rstrip("/") in norm)
    if dentro / len(membros) >= MENU_FRACCAO:
        return ("FAMILIA_E_MENU: %d dos %d enderecos da familia repetem-se dentro do item "
                "— navegacao do site, nao lista de materias" % (dentro, len(membros)))
    return None


def _dono(alvo: str, padrao: str, outros: dict, eu: str | None) -> str | None:
    """Outra fonte ja colhe este documento (ou tem este mesmo padrao)?"""
    for sid, c in sorted(outros.items()):
        if sid == eu:
            continue
        aq = (c or {}).get("ACQUISITION") or {}
        p = aq.get("LINK_PATTERN")
        if not p:
            continue
        if p == padrao:
            return sid
        if _host(aq.get("INDEX_URL") or "") != _host(alvo):
            continue
        try:
            if re.match(p, alvo):
                return sid
        except re.error:
            continue
    return None


# ── A PORTA DE CONTRATOS DO REPARO ──────────────────────────────────────────
CAMPOS_QUE_O_REPARO_MUDA = frozenset({"ACQUISITION", "REPARO_DE_CONTRATO", "ROUTE_PROVENANCE",
                                      "SOURCE_CONTRACT_HASH"})


class ReparoInvalido(Exception):
    pass


def aplicar(contrato: dict, proposta: dict, *, quando: str | None = None) -> dict:
    """O contrato depois do reparo. Puro: nao escreve em disco. Rebenta se a
    proposta nao for PADRAO_NOVO, se o validador da casa reprovar, ou se algum
    campo alem de CAMPOS_QUE_O_REPARO_MUDA mudar."""
    import escrever_contratos as EC      # noqa: PLC0415
    import validar_contratos as VC       # noqa: PLC0415
    if proposta.get("DESFECHO") != "PADRAO_NOVO":
        raise ReparoInvalido("so se aplica PADRAO_NOVO, nao %s" % proposta.get("DESFECHO"))
    quando = quando or agora()
    antes = copy.deepcopy(contrato)
    novo = copy.deepcopy(contrato)
    aq = dict(novo.get("ACQUISITION") or {}, STRATEGY="HTML_LINK_DISCOVERY",
              INDEX_URL=proposta["INDEX_URL"], LINK_PATTERN=proposta["LINK_PATTERN"])
    aq.setdefault("MATCH", "URL")
    aq.setdefault("MAX_TARGETS", 1)
    novo["ACQUISITION"] = aq
    anteriores = list((contrato.get("REPARO_DE_CONTRATO") or {}).get("HISTORICO") or [])
    if contrato.get("REPARO_DE_CONTRATO"):
        anteriores.append({k: v for k, v in contrato["REPARO_DE_CONTRATO"].items() if k != "HISTORICO"})
    novo["REPARO_DE_CONTRATO"] = {
        "DECISAO": "R1", "MISSAO": MISSAO, "METODO": METODO, "APLICADO_EM": quando,
        "COMO": proposta.get("COMO"),
        "ACQUISITION_ANTERIOR": proposta.get("ACQUISITION_ANTERIOR") or antes.get("ACQUISITION"),
        "PROVA": {"ENTRADA": proposta.get("ENTRADA"), "ENTRADA_RETRATO": proposta.get("ENTRADA_RETRATO"),
                  "SECCAO_TENTADA": proposta.get("SECCAO_TENTADA"),
                  "ALVOS_NA_LISTAGEM": proposta.get("ALVOS_NA_LISTAGEM"),
                  "ITEM_LIDO": proposta.get("ITEM_LIDO"), "PAGINAS_LIDAS": proposta.get("PAGINAS_LIDAS")},
        "PRECISA_DE_REMEDIR": True,
        "NOTA": ("hipotese de rota: o canario seguinte, com a regua dos quatro passos, e que "
                 "decide READY; o reparo nunca promove"),
        **({"HISTORICO": anteriores} if anteriores else {}),
    }
    novo["ROUTE_PROVENANCE"] = {
        "MISSAO": MISSAO, "FERRAMENTA": "curadoria/reparar_contrato.py", "INTEGRADO_EM": quando,
        "PROVADO_EM": quando, "LISTAGEM": proposta["INDEX_URL"],
        **({"ANTERIOR": contrato["ROUTE_PROVENANCE"]} if contrato.get("ROUTE_PROVENANCE") else {}),
    }
    novo.pop("SOURCE_CONTRACT_HASH", None)
    novo["SOURCE_CONTRACT_HASH"] = EC.hash_do_contrato(novo)
    mexidos = {k for k in set(antes) | set(novo) if antes.get(k) != novo.get(k)}
    fora = mexidos - CAMPOS_QUE_O_REPARO_MUDA
    if fora:
        raise ReparoInvalido("o reparo mexeu em campos que nao sao dele: %s" % sorted(fora))
    if antes.get("SOURCE_ID") != novo.get("SOURCE_ID"):
        raise ReparoInvalido("SOURCE_ID mudou")
    _, falhas = VC.validar([novo])
    if falhas:
        raise ReparoInvalido("contrato reparado reprovado: %s" % str(falhas[0])[:200])
    return novo
