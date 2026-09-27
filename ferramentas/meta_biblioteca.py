#!/usr/bin/env python3
"""
A PORTA DA BIBLIOTECA DE ANÚNCIOS DA META — com que se viaja, e nada mais.

    python3 ferramentas/meta_biblioteca.py          # há Chrome com janela na porta?

FERRAMENTA, não ação (AGENTS.md: «com QUE se viaja»). Quem vai buscar e guarda é
`coleta/concorrencia_meta.py`. Este ficheiro sabe três coisas: montar o endereço
público da Biblioteca, ler o DOM que a página mostra a qualquer pessoa sem login,
e dizer se a leitura bateu com o número que a PRÓPRIA FONTE declara.

DE ONDE VEM
-----------
Trazido do ramo `claude/eame-meta-competitor` (a2fad2d0, 31/08/2026),
`scripts/meta_navegador.py`. O que mudou na vinda, e só isto:

  · fala com o Chrome por `ferramentas/cdp.py` (a biblioteca da casa), e não por
    um `cdp.py` que vivia fora do Git em `~/.sintonia-browser/`;
  · os extratores de JavaScript, a regra de completude, as datas e o estado do
    cartão vieram iguais — cada um carrega a medição que o fez nascer.

A ROTA, MEDIDA EM 30/08/2026 (META-ROUTE-PROBE-V1, no mesmo ramo)
-------------------------------------------------------------------
    curl com User-Agent de Chrome ......... HTTP 403, 481 bytes
    graph.facebook.com/ads_archive ........ HTTP 500, OAuthException (sem token)
    Chrome com janela (CDP) ............... 1.990.149 bytes, cartões lidos

    META_ROUTE = META_ADS_LIBRARY_UI_CHROME_COM_JANELA

D88: contorno técnico para material PÚBLICO é permitido (navegador real), SEM
login e SEM conta paga. A barra da Biblioteca continua a mostrar «Log in» — e
`cabecalho()` devolve `NAO_LOGADO` quando é assim. Se um dia devolver outra
coisa, quem chama PARA (ver a ação).

    LEITURA_DO_QUE_A_PAGINA_MOSTRA != BYPASS

LÍNGUA ≠ PAÍS
-------------
Toda URL leva `locale=en_US`: sem isso o rótulo do cartão sai na língua do perfil
do Chrome e o parser passa a depender dela. `locale` NÃO altera o país dos
anúncios — o país é `country=`, e a Meta acrescenta `is_targeted_country=false`:
a lista responde «anúncios que ALCANÇARAM o país», não «dirigidos ao país».

    UI_LANGUAGE != AD_COUNTRY        PAIS_ALCANCADO != PAIS_ALVO
"""
import json
import os
import re
import sys
import time
import urllib.parse

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))   # a raiz
import _gavetas  # noqa: E402,F401 — poe as gavetas do processo no caminho

BASE = 'https://www.facebook.com/ads/library/'
ROTA = 'META_ADS_LIBRARY_UI_CHROME_COM_JANELA'
# Porta própria (SEPARATE_GIT_WORKTREE != SEPARATE_BROWSER_SESSION): a mesma que
# a missão de 30/08 usou, longe da 9222 (FR) e da 9223 (IT).
PORTA = int(os.environ.get('META_PORTA') or 9224)
PERFIL = os.path.join(os.path.expanduser('~'), '.sintonia-browser', 'meta',
                      'chrome-profile')

NAO_LOGADO = 'NAO_LOGADO'
LOGIN_INDEFINIDO = 'INDEFINIDO'


def url_biblioteca(**params):
    """Monta URL da Biblioteca com `locale=en_US` sempre, e sem inventar campo."""
    p = dict(params)
    p.setdefault('locale', 'en_US')
    return BASE + '?' + urllib.parse.urlencode(p)


def url_da_pagina(page_id, pais):
    """A visão por PÁGINA num país: todos os anúncios (ativos e inativos)."""
    return url_biblioteca(active_status='all', ad_type='all', country=pais,
                          view_all_page_id=page_id, search_type='page',
                          media_type='all')


# ── completude ───────────────────────────────────────────────────────────────
# A PRIMEIRA REGRA DE COMPLETUDE ESTAVA ERRADA, E O ERRO FOI MEDIDO (30/08/2026)
#     Bayer Crop Science España, ES ... 1.a leitura 189 cartões
#                                       2.a leitura  29 cartões, e AS DUAS
#                                       diziam «completa»
# Com os dois lados marcados completos, o relógio teria anunciado 160 «parou»
# falsos.                               PAROU_DE_CRESCER != CHEGOU_AO_FIM
# A regra usa o denominador que a PRÓPRIA FONTE publica («~230 results»).
COMPLETA_BATE_COM_A_FONTE = 'COMPLETE_MATCHES_SOURCE_COUNT'
AQUEM_DA_FONTE = 'SHORT_OF_SOURCE_COUNT'
FONTE_NAO_DECLARA = 'SOURCE_COUNT_NOT_DECLARED'
# Sem anúncio a página NÃO imprime «~N results», imprime a frase abaixo.
#     ZERO_PROVADO != ZERO_POR_FALTA_DE_LEITURA
ZERO_DECLARADO = 'ZERO_CONFIRMED_BY_SOURCE'
SEM_RESULTADOS_TEXTO = 'No ads match your search criteria'

# Os dois estados que a fonte fecha: só eles autorizam afirmar ausência.
ESTADOS_FECHADOS_PELA_FONTE = (COMPLETA_BATE_COM_A_FONTE, ZERO_DECLARADO)

# CARTÃO NÃO É ANÚNCIO — Syngenta global, ES, 30/08/2026: ~15 declarados, 13
# cartões, dois deles «2 ads use this creative and text» -> 11 + 4 = 15. Exato.
# 0,95 é tolerância ao «~» da fonte, não arredondamento.
TOLERANCIA = 0.95


def _numero(declarado):
    if not declarado:
        return None
    try:
        return int(str(declarado).replace(',', '').replace('.', '').strip())
    except ValueError:
        return None


def anuncios_em(cartoes):
    """Soma os anúncios que os cartões representam. Cartão sem grupo vale 1."""
    return sum(int(c.get('ads_neste_cartao') or 1) for c in (cartoes or []))


def completude(lidos, declarado, sem_resultados=False):
    """`lidos` é contagem de ANÚNCIOS (ver anuncios_em), não de cartões."""
    n = _numero(declarado)
    if sem_resultados and lidos == 0:
        return {'state': ZERO_DECLARADO, 'read': 0, 'source_count': 0,
                'ratio': None,
                'nota': 'a fonte escreveu "%s". Zero PROVADO, nao zero por '
                        'falta de leitura.' % SEM_RESULTADOS_TEXTO}
    if n is None:
        return {'state': FONTE_NAO_DECLARA, 'read': lidos,
                'source_count': None, 'ratio': None,
                'nota': 'a pagina nao publicou "~N results". Sem denominador da '
                        'fonte, nao da para afirmar completude.'}
    razao = round(lidos / n, 3) if n else None
    return {'state': COMPLETA_BATE_COM_A_FONTE if (n and lidos >= TOLERANCIA * n)
            else AQUEM_DA_FONTE,
            'read': lidos, 'source_count': n, 'ratio': razao,
            'nota': 'li %d de ~%d que a fonte declara' % (lidos, n)}


# ── datas e estado do cartão ─────────────────────────────────────────────────
# Dois formatos observados em 30/08/2026, com `locale=en_US`:
#     "Started running on Jul 15, 2026"      -> só início, em veiculação
#     "Jul 29, 2025 - Mar 8, 2026"           -> início e fim
# Formato desconhecido vira None, e não um palpite.
_MES = {m: i + 1 for i, m in enumerate(
    ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
     'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'])}
_DATA = r'([A-Z][a-z]{2})\s+(\d{1,2}),\s+(\d{4})'


def _iso(mes, dia, ano):
    if mes not in _MES:
        return None
    return '%s-%02d-%02d' % (ano, _MES[mes], int(dia))


def datas_do_texto(texto):
    faixa = re.search(_DATA + r'\s*[-–]\s*' + _DATA, texto or '')
    if faixa:
        return (_iso(faixa.group(1), faixa.group(2), faixa.group(3)),
                _iso(faixa.group(4), faixa.group(5), faixa.group(6)))
    inicio = re.search(r'Started running on\s+' + _DATA, texto or '')
    if inicio:
        return _iso(inicio.group(1), inicio.group(2), inicio.group(3)), None
    return None, None


ATIVO = 'ACTIVE'
INATIVO = 'INACTIVE'
STATUS_NAO_LIDO = 'NOT_KNOWN'


def status_do_texto(texto):
    cabeca = (texto or '')[:200]
    if re.search(r'\bActive\b', cabeca):
        return ATIVO
    if re.search(r'\bInactive\b', cabeca):
        return INATIVO
    return STATUS_NAO_LIDO


# ── o que o JavaScript lê da página ──────────────────────────────────────────
# conta ANÚNCIOS, não cartões: o cartão que declara «N ads use this creative and
# text» vale N.
JS_CONTA = r'''(()=>{
 const t = document.body.innerText || '';
 const cartoes = (t.match(/Library ID:/g)||[]).length;
 const grupos = [...t.matchAll(/(\d+)\s+ads?\s+use\s+this\s+creative\s+and\s+text/gi)];
 const extra = grupos.reduce((a,m)=>a + (parseInt(m[1],10)-1), 0);
 return String(cartoes + extra);
})()'''

# O cartão é o MAIOR nó que contém exatamente UM «Library ID:» e não está dentro
# de outro assim. Fronteira por contagem, e não por classe: o React da Meta
# reescreve as classes.
JS_CARTOES = r'''(()=>{
 const conta = t => ((t||'').match(/Library ID:\s*\d{6,}/g)||[]).length;
 const nos = [...document.querySelectorAll('div')].filter(d => conta(d.innerText)===1);
 const set = new Set(nos);
 const cartoes = nos.filter(n=>{let p=n.parentElement;while(p){if(set.has(p))return false;p=p.parentElement}return true});
 const vistos = new Set();
 const saida = [];
 for (const n of cartoes){
   const t = n.innerText || '';
   const m = t.match(/Library ID:\s*(\d{6,})/);
   if (!m) continue;
   const id = m[1];
   if (vistos.has(id)) continue;
   vistos.add(id);
   const rotulos = [...n.querySelectorAll('[aria-label]')].map(e=>e.getAttribute('aria-label')).filter(Boolean);
   const links = [...n.querySelectorAll('a[href]')].map(a=>a.href);
   const g = t.match(/(\d+)\s+ads?\s+use\s+this\s+creative\s+and\s+text/i);
   saida.push({
     library_id: id,
     ads_neste_cartao: g ? parseInt(g[1], 10) : 1,
     texto: t,
     links: links.slice(0,20),
     rotulos: [...new Set(rotulos)].slice(0,25),
     n_img: n.querySelectorAll('img').length,
     n_video: n.querySelectorAll('video').length
   });
 }
 return JSON.stringify({total: saida.length, cartoes: saida});
})()'''

JS_CABECALHO = r'''(()=>{
 const t = document.body.innerText || '';
 const m = t.match(/~?([\d.,]+)\s+result/i);
 return JSON.stringify({
   url: location.href,
   titulo: document.title,
   bytes: document.documentElement.outerHTML.length,
   resultados_declarados: m ? m[1] : null,
   sem_resultados: /No ads match your search criteria/i.test(t),
   logado: !/\bLog in\b/.test(t) ? 'INDEFINIDO' : 'NAO_LOGADO'
 });
})()'''


def _json(bruto):
    try:
        return json.loads(bruto)
    except (TypeError, ValueError):
        return {'_nao_json': str(bruto)[:400]}


def ler_pagina(url, *, porta=PORTA, espera=15, max_rolagens=60, pausa=2.2,
               paciencia=8, cdp=None):
    """UMA visita a UMA página da Biblioteca. → dict com o bruto e o que se leu.

    Rola até a lista parar de crescer `paciencia` vezes seguidas (DOIS sinais
    para parar, não um: alcançar o total declarado não é ter visto todos os
    criativos — UPL Corp France, 30/08: 47 cartões com a conta fechada, 87 sem o
    corte). `cdp` é injetável para teste; por omissão é `ferramentas/cdp.py`.
    """
    if cdp is None:
        import cdp as _cdp  # noqa: E402 — ferramentas/cdp.py
        cdp = _cdp
    aba, _html = cdp.abrir(url, porta=porta, espera=espera, timeout=120)
    try:
        cab = _json(aba.js(JS_CABECALHO))
        antes = int(aba.js(JS_CONTA) or 0)
        parado, n = 0, 0
        for n in range(1, max_rolagens + 1):
            aba.js('window.scrollTo(0, document.body.scrollHeight); "ok"')
            time.sleep(pausa)
            agora = int(aba.js(JS_CONTA) or 0)
            parado = parado + 1 if agora == antes else 0
            antes = agora
            if parado >= paciencia:
                break
        cart = _json(aba.js(JS_CARTOES, timeout_ms=120000))
        url_final = (cab or {}).get('url')
    finally:
        aba.fechar()
    return {'cabecalho': cab, 'cartoes': cart.get('cartoes', []),
            'rolagens': n, 'parou_sem_crescer': parado >= paciencia,
            'url_final': url_final}


def navegador_vivo(porta=PORTA):
    """Há Chrome com janela escutando nesta porta? → (estado, detalhe)."""
    import cdp  # noqa: E402
    try:
        return 'PORTA_ABERTA', len(cdp.abas(porta, timeout=5))
    except cdp.Erro as e:
        return (e.estado or 'PORTA_NAO_RESPONDEU'), str(e)[:160]


if __name__ == '__main__':
    estado, det = navegador_vivo()
    print(json.dumps({'porta': PORTA, 'estado': estado, 'detalhe': det,
                      'perfil': PERFIL, 'rota': ROTA}, ensure_ascii=False, indent=2))
