#!/usr/bin/env python3
"""
A PORTA DA BIBLIOTECA DE ANUNCIOS — Chrome com janela, porta 9224, perfil proprio.

A licao ja estava paga. Em 30/08/2026 a coleta do catalogo ADAMA mediu que
`curl` e `chrome --headless=new` levam o MESMO 403, e que so o Chrome com
janela grafica le a pagina. A fronteira nao e "navegador vs. requests" — e
"janela vs. tudo o mais".

A Biblioteca de Anuncios da Meta repete o padrao, medido aqui em 30/08/2026:

    curl com User-Agent de Chrome ......... HTTP 403, 481 bytes
    graph.facebook.com/ads_archive ........ HTTP 500, OAuthException code 1
    Chrome com janela (CDP 9224) .......... 1.990.149 bytes, 27 cartoes lidos

ISOLAMENTO — DUAS COISAS DIFERENTES
------------------------------------
Tambem em 30/08/2026, duas sessoes escolheram sozinhas o mesmo perfil de Chrome
e a mesma porta 9222, e acabaram dividindo UMA janela: quem navegava mexia na
aba da outra missao. A lei que ficou:

    SEPARATE_GIT_WORKTREE != SEPARATE_BROWSER_SESSION

Por isso esta missao tem porta 9224 e perfil `~/.sintonia-browser/meta/` —
FR ficou com 9222, IT com 9223.

O QUE ESTE ARQUIVO FAZ E O QUE NAO FAZ
---------------------------------------
FAZ: abre aba, espera, rola para carregar mais, le o DOM RENDERIZADO da pagina
publica e devolve os cartoes.

NAO FAZ: nao le token de sessao da pagina, nao chama endpoint interno, nao usa
cookie de conta, nao faz login, nao resolve captcha. Le o que a pagina publica
mostra a qualquer pessoa sem login — a barra da Biblioteca continua exibindo
"Log in", e e assim que tem de continuar.

    LEITURA_DO_QUE_A_PAGINA_MOSTRA != BYPASS

LINGUA
------
Toda URL leva `locale=en_US`. Nao e preferencia: sem isso o rotulo do cartao
sai na lingua do perfil do Chrome (a primeira leitura veio em portugues,
"Identificacao da biblioteca"), e o parser passaria a depender de que lingua o
navegador resolveu falar naquele dia. `locale` NAO altera o pais dos anuncios —
o pais e `country=`, e sao coisas separadas.

    UI_LANGUAGE != AD_COUNTRY
"""
import json
import os
import re
import sys
import time
import urllib.parse
import urllib.request

PORTA = 9224
PERFIL = os.path.expanduser(r'~\.sintonia-browser\meta\chrome-profile')
CDP_DIR = os.path.expanduser(r'~\.sintonia-browser')
if CDP_DIR not in sys.path:
    sys.path.insert(0, CDP_DIR)

BASE = 'https://www.facebook.com/ads/library/'

# Estados de porta. Sao nomes de RESULTADO, nao de causa: "nao respondeu" nao
# vira "site fora do ar" sem medida que sustente isso.
PORTA_ABERTA = 'PORTA_ABERTA'
PORTA_SEM_JANELA = 'PORTA_SEM_JANELA'
PORTA_NAO_RESPONDEU = 'PORTA_NAO_RESPONDEU'


def _cdp():
    import cdp  # noqa: E402  — fica fora do Git, so stdlib
    return cdp


def navegador_vivo(porta=PORTA):
    """Ha Chrome com janela escutando nesta porta? Devolve (estado, versao)."""
    try:
        with urllib.request.urlopen('http://127.0.0.1:%d/json/version' % porta,
                                    timeout=5) as r:
            v = json.load(r)
        return PORTA_ABERTA, v.get('Browser')
    except Exception as e:
        return PORTA_NAO_RESPONDEU, str(e)[:120]


def url_biblioteca(**params):
    """Monta URL da Biblioteca com `locale=en_US` sempre, e sem inventar campo."""
    p = dict(params)
    p.setdefault('locale', 'en_US')
    return BASE + '?' + urllib.parse.urlencode(p)


def abrir(url, espera=14, porta=PORTA):
    req = urllib.request.Request(
        'http://127.0.0.1:%d/json/new?%s' % (porta, urllib.parse.quote(url, safe='')),
        method='PUT')
    alvo = json.load(urllib.request.urlopen(req, timeout=20))
    time.sleep(espera)
    return alvo


def fechar(alvo, porta=PORTA):
    try:
        urllib.request.urlopen(
            'http://127.0.0.1:%d/json/close/%s' % (porta, alvo['id']), timeout=10).read()
    except Exception:
        pass


def js(alvo, expressao, timeout=90):
    return _cdp().avaliar(alvo['webSocketDebuggerUrl'], expressao, timeout=timeout)


def js_json(alvo, expressao, timeout=90):
    bruto = js(alvo, expressao, timeout=timeout)
    try:
        return json.loads(bruto)
    except Exception:
        return {'_nao_json': str(bruto)[:400]}


# ── rolagem ──────────────────────────────────────────────────────────────────
# A Biblioteca carrega por rolagem infinita. Rolar N vezes NAO garante ter tudo:
# devolve quantos cartoes havia antes e depois, para que quem le saiba se a
# lista PAROU de crescer (COMPLETA_OBSERVADA) ou se ainda crescia quando parei
# (TRUNCADA_POR_LIMITE). Chamar isso de "todos os anuncios" sem essa distincao
# seria transformar limite meu em fato do mundo.
COMPLETA_OBSERVADA = 'COMPLETA_OBSERVADA'
TRUNCADA_POR_LIMITE = 'TRUNCADA_POR_LIMITE'

_CONTA = r'''(()=>{return String((document.body.innerText.match(/Library ID:/g)||[]).length)})()'''


def rolar_ate_parar(alvo, max_rolagens=40, pausa=2.2):
    antes = int(js(alvo, _CONTA) or 0)
    estavel = 0
    n = 0
    for n in range(1, max_rolagens + 1):
        js(alvo, 'window.scrollTo(0, document.body.scrollHeight); "ok"')
        time.sleep(pausa)
        agora = int(js(alvo, _CONTA) or 0)
        if agora == antes:
            estavel += 1
            if estavel >= 3:
                return {'cartoes': agora, 'rolagens': n,
                        'completude': COMPLETA_OBSERVADA}
        else:
            estavel = 0
        antes = agora
    return {'cartoes': antes, 'rolagens': n, 'completude': TRUNCADA_POR_LIMITE}


# ── leitura do cartao ────────────────────────────────────────────────────────
# O cartao e o MAIOR no que contem exatamente UM "Library ID:" e nao esta dentro
# de outro no assim. Achar a fronteira por contagem, e nao por nome de classe,
# e o que faz o parser sobreviver ao React da Meta, que reescreve as classes.
_CARTOES = r'''(()=>{
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
   const links = [...n.querySelectorAll('a[href]')].map(a=>a.href);
   const rotulos = [...n.querySelectorAll('[aria-label]')].map(e=>e.getAttribute('aria-label')).filter(Boolean);
   const imgs = [...n.querySelectorAll('img')].map(i=>i.src).filter(s=>/scontent|fbcdn/.test(s));
   saida.push({
     library_id: id,
     texto: t,
     links: links.slice(0,20),
     rotulos: [...new Set(rotulos)].slice(0,25),
     n_img: n.querySelectorAll('img').length,
     n_video: n.querySelectorAll('video').length,
     img_amostra: imgs.slice(0,2)
   });
 }
 return JSON.stringify({total: saida.length, cartoes: saida});
})()'''


def cartoes(alvo):
    return js_json(alvo, _CARTOES, timeout=120)


_CABECALHO = r'''(()=>{
 const t = document.body.innerText || '';
 const m = t.match(/~?([\d.,]+)\s+result/i);
 return JSON.stringify({
   url: location.href,
   titulo: document.title,
   bytes: document.documentElement.outerHTML.length,
   resultados_declarados: m ? m[1] : null,
   logado: !/\bLog in\b/.test(t) ? 'INDEFINIDO' : 'NAO_LOGADO'
 });
})()'''


def cabecalho(alvo):
    return js_json(alvo, _CABECALHO, timeout=60)


# ── datas do cartao ──────────────────────────────────────────────────────────
# Dois formatos observados em 30/08/2026, com `locale=en_US`:
#     "Started running on Jul 15, 2026"      -> so inicio, anuncio em veiculacao
#     "Jul 29, 2025 - Mar 8, 2026"           -> inicio e fim
# Um terceiro formato que eu nao conheca deve virar None, e nao um palpite.
_MES = {m: i + 1 for i, m in enumerate(
    ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
     'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'])}
_DATA = r'([A-Z][a-z]{2})\s+(\d{1,2}),\s+(\d{4})'


def _iso(mes, dia, ano):
    if mes not in _MES:
        return None
    return '%s-%02d-%02d' % (ano, _MES[mes], int(dia))


def datas_do_texto(texto):
    faixa = re.search(_DATA + r'\s*[-–]\s*' + _DATA, texto)
    if faixa:
        a = _iso(faixa.group(1), faixa.group(2), faixa.group(3))
        b = _iso(faixa.group(4), faixa.group(5), faixa.group(6))
        return a, b
    inicio = re.search(r'Started running on\s+' + _DATA, texto)
    if inicio:
        return _iso(inicio.group(1), inicio.group(2), inicio.group(3)), None
    solta = re.search(_DATA, texto)
    if solta:
        return _iso(solta.group(1), solta.group(2), solta.group(3)), None
    return None, None


ATIVO = 'ACTIVE'
INATIVO = 'INACTIVE'
STATUS_NAO_LIDO = 'NOT_KNOWN'


def status_do_texto(texto):
    cabeca = texto[:200]
    if re.search(r'\bActive\b', cabeca):
        return ATIVO
    if re.search(r'\bInactive\b', cabeca):
        return INATIVO
    return STATUS_NAO_LIDO


if __name__ == '__main__':
    estado, versao = navegador_vivo()
    print(json.dumps({'porta': PORTA, 'estado': estado, 'navegador': versao,
                      'perfil': PERFIL}, ensure_ascii=False, indent=2))
