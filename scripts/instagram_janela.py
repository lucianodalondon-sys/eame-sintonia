#!/usr/bin/env python3
"""
INSTAGRAM PELA JANELA — tudo o que a rota pública entrega antes de gastar um centavo.

    py scripts/instagram_janela.py perfis     # bio, seguidores, denominador, a grade
    py scripts/instagram_janela.py objetos    # data, legenda inteira, curtidas, vídeo
    py scripts/instagram_janela.py tudo       # os dois, na ordem

A ORDEM É LEI, E ELA VEM DA MISSÃO 14
---------------------------------------
    LOTE CONGELADO → PERFIL → OBJETO → (só então) ROTA PAGA

Este arquivo NÃO decide quem entra: ele obedece a
`data/samples/COMPETITOR-PUBLIC-COMM/PUBLIC-COMM-FIRST-BATCH-EAME.json` e só toca conta
com `PLATFORM = INSTAGRAM`. Se a régua de identidade estiver errada, o conserto é lá, de
graça, e esta coleta roda de novo sobre a lista nova.

O QUE FOI MEDIDO NESTA MÁQUINA EM 2026-09-02, E QUE JUSTIFICA O ARQUIVO INTEIRO
--------------------------------------------------------------------------------
Chrome com janela, DESLOGADO, contra `@basf_agroes` e `@bayer_italia`:

    página do PERFIL     bio, nome, seguidores, seguindo, link externo, destaques,
                         e EXATAMENTE 12 itens da grade. Rolar não traz o 13º:
                         aparece "Mostrar mais posts de <conta>" e o muro fecha.
    página do POST       a DATA ABSOLUTA, em <time datetime="2026-08-31T18:03:31.000Z">,
                         e a etiqueta og:description com curtidas, nº de comentários,
                         data por extenso e a legenda.
    rota de EMBED        a legenda INTEIRA (720 caracteres, sem o "... mais"), curtidas,
                         nº de comentários, seguidores, o denominador de posts da conta,
                         e — em reel — visualizações (3.763), duração (58,068 s) e a URL
                         do MP4. Tudo dentro de um `contextJSON` embutido no HTML.

O que NENHUMA das três dá: **o texto dos comentários**. Esse continua sendo o único
motivo real de pagar.

    O EMBED É PÚBLICO POR DESENHO. É a moldura que o Instagram publica para que qualquer
    pessoa cole um post num blog. Ler o que ela devolve não é arrombar porta.

O DENOMINADOR É O ACHADO MAIS BARATO DESTE ARQUIVO
----------------------------------------------------
A rota do embed diz quantos posts a conta tem no total ("1.973 posts"). Sem esse número,
"12 itens coletados" é indistinguível de "a conta tem 12 posts" e de "a coleta quebrou".
Com ele, `12 de 1.973` é uma frase honesta — e é o que impede a Missão 14 de ler
cobertura de coleta como cobertura de mercado.

    12 DE 1.973 É SUB-COLETA DECLARADA. "12" SOZINHO É UM NÚMERO QUE MENTE.

TRÊS ROTAS, TRÊS NÚMEROS DE COMENTÁRIO — E NENHUM É "O" NÚMERO
----------------------------------------------------------------
No MESMO post, medido no mesmo minuto: o embed disse 2, a página do post disse 2, e a
etiqueta og:description disse 4. É a mesma família da armadilha que a Biblioteca de
Anúncios já pregou nesta casa. Então este arquivo **grava os três, cada um com o nome da
rota que o produziu**, e nunca escolhe um para chamar de verdade. Quem for comparar
engajamento depois precisa comparar rota com a MESMA rota.

O QUE ESTE ARQUIVO NÃO FAZ
----------------------------
Não faz login, não lê cookie, não resolve CAPTCHA, não passa credencial, não desliga
sandbox. Não classifica assunto, não mede convergência, não declara nada sobre o
mercado. Ele lê, preserva o HTML cru e grava o normalizado — a classificação roda depois,
de graça, sobre o artefato.
"""
import json
import os
import re
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import cdp                       # noqa: E402  — o navegador, em biblioteca padrão
import proveniencia as pv        # noqa: E402

SAMPLES = os.path.join(ROOT, 'data', 'samples')
LOTE = os.path.join(SAMPLES, 'COMPETITOR-PUBLIC-COMM', 'PUBLIC-COMM-FIRST-BATCH-EAME.json')
SAIDA = os.path.join(SAMPLES, 'INSTAGRAM-JANELA')
PROVAS = os.path.join(SAIDA, 'provas')
BRUTO = os.path.join(SAIDA, 'html-bruto')

MISSION = '14-COMUNICACAO-PUBLICA-DO-CONCORRENTE'
RUNNER = os.environ.get('RUNNER_NAME') or 'NOT_KNOWN'
NAO_SEI = 'NOT_KNOWN'

# Porta e perfil PRÓPRIOS. A memória desta casa registra duas sessões escolhendo sozinhas
# o mesmo perfil e a mesma porta 9222, e acabando com um Chrome só, com abas das duas
# missões dentro — quem mandava `navigate` mexia na janela do outro.
#
#     SEPARATE_GIT_WORKTREE ≠ SEPARATE_BROWSER_SESSION.
PORTA = int(os.environ.get('IG_PORTA') or 9226)
PERFIL = os.path.join(os.path.expanduser('~'), '.sintonia-browser', 'ig', 'chrome-profile')

# Pausa entre páginas. Não é superstição: é a diferença entre ler uma fonte pública no
# ritmo de uma pessoa e martelar o servidor de alguém. Nesta máquina, ~35 carregamentos
# deslogados numa hora não encontraram bloqueio nenhum — mas isso mede UMA hora, não
# mede o limite, e o limite não é nosso para descobrir na marra.
PAUSA = float(os.environ.get('IG_PAUSA') or 4.0)


# ────────────────────────────────────────────────────────── o que se lê de cada página
# JS em string CRUA (r"""), sempre. Sem o `r`, o `\n` de uma regex vira quebra de linha
# de verdade e o Chrome responde `SyntaxError: Invalid regular expression: missing /` —
# custou uma execução para descobrir.
JS_PERFIL = r"""
(() => {
  const t = document.body.innerText || '';
  const um = (re) => { const m = t.match(re); return m ? m[1].trim() : null; };
  const links = [...document.querySelectorAll('a[href*="/p/"], a[href*="/reel/"]')]
      .map(a => a.getAttribute('href')).filter(Boolean);
  const codigos = [...new Set(links.map(h => {
      const m = h.match(/\/(p|reel)\/([A-Za-z0-9_-]+)/);
      return m ? m[1] + ':' + m[2] : null;
  }).filter(Boolean))];
  const meta = (p) => { const e = document.querySelector('meta[property="' + p + '"]');
                        return e ? e.content : null; };
  return {
    TITULO: document.title || null,
    OG_DESCRIPTION: meta('og:description'),
    SEGUIDORES_TEXTO: um(/([\d.,]+\s*(?:mil|K|M|k|m)?)\s*\n?\s*seguidores/i)
                   || um(/([\d.,]+\s*(?:mil|K|M|k|m)?)\s*\n?\s*followers/i),
    SEGUINDO_TEXTO:   um(/([\d.,]+)\s*\n?\s*seguindo/i)
                   || um(/([\d.,]+)\s*\n?\s*following/i),
    LINK_EXTERNO: (() => {
        const a = [...document.querySelectorAll('a[href]')]
            .map(x => x.getAttribute('href'))
            .find(h => h && /^https?:/.test(h) && !/instagram\.com|facebook\.com/.test(h));
        return a || null; })(),
    TEXTO_VISIVEL: t.slice(0, 1500),
    CODIGOS_NA_GRADE: codigos,
    ITENS_NA_GRADE: codigos.length,
    // DESTAQUES: o CONTEÚDO fica atrás do muro de login (medido: "Cadastre-se para ver
    // mais destaques"), mas a LISTA é pública — e ela é sinal por si só. Post some no
    // meio de 1.974; destaque é o que a marca escolheu deixar guardado para sempre.
    // Um destaque novo aparecendo é notícia; o nome dele diz a prioridade.
    DESTAQUES: [...document.querySelectorAll('a[href*="/stories/highlights/"]')]
        .map(a => (a.getAttribute('href').match(/highlights\/(\d+)/) || [])[1])
        .filter(Boolean),
    MURO_DE_LOGIN: /Mostrar mais posts|Show more posts|Ver más publicaciones|Altri post/i.test(t),
    PAGINA_NAO_ENCONTRADA: /Esta página não está disponível|Sorry, this page isn't available|Página no disponible/i.test(t)
  };
})()
"""

# ── COMENTÁRIO: o seletor saiu de MEDIÇÃO do DOM, não de palpite ────────────────
# A primeira versão procurou `<li>` e colheu ZERO em 6 posts. Inspecionando a árvore de
# verdade: comentário é um `<div>` que contém EXATAMENTE UM `<time>` e cuja árvore de
# texto tem a palavra "Responder". O bloco da legenda do post também tem um `<time>` —
# mas NÃO tem "Responder", e é assim que os dois se separam sem depender de classe
# (a Meta troca as classes a cada publicação).
#
# MEDIDO em 7 posts das 5 contas do lote, deslogado: 18 de 31 comentários declarados
# saíram COM TEXTO — 58%. Em post de 1 comentário, 100%; no de 12, metade.
#
#     A FATIA CRESCE QUANDO SE LÊ CEDO. Post novo tem poucos comentários, e ler todo
#     dia durante os 7 primeiros dias acumula o que uma leitura só não pega.
#
# E o que NÃO se colhe fica declarado: `COMMENTS_DECLARED` contra `COMMENTS_COLLECTED`
# é a única forma de "8 comentários" não ser lido como a audiência inteira.
JS_COMENTARIOS = r"""
(() => {
  const RESP = /(^|\n)\s*(Responder|Reply|Rispondi|Répondre|Responder a)\s*(\n|$)/;
  const achados = [];
  document.querySelectorAll('time').forEach(tm => {
    let p = tm.parentElement, bloco = null;
    for (let k = 0; k < 7 && p; k++) {
      const t = p.innerText || '';
      if (RESP.test(t) && p.querySelectorAll('time').length === 1) { bloco = p; break; }
      p = p.parentElement;
    }
    if (!bloco) return;
    const linhas = (bloco.innerText || '').split('\n').map(x => x.trim()).filter(Boolean);
    if (!linhas.length) return;
    const autor = linhas[0];
    const rel = (tm.innerText || '').trim();
    const corpo = linhas.filter(x =>
        x !== autor && x !== rel &&
        !/^(Responder|Reply|Rispondi|Répondre|Ver tradução|See translation|Editado|Curtir|Like)$/i.test(x) &&
        !/^\d+\s*(curtida|curtidas|like|likes|mi piace)$/i.test(x));
    if (!corpo.length) return;
    const mCurt = ((bloco.innerText || '').match(/(\d+)\s*(curtida|like|mi piace)/i) || [])[1];
    achados.push({
      AUTOR: autor,
      TEMPO_RELATIVO: rel,
      // A tag <time> do comentário costuma NÃO ter `datetime`. Quando não tiver, o
      // tempo é RELATIVO ("19 h") e converter em data inventaria precisão que a fonte
      // não deu. Fica o relativo, e o campo de data sai NOT_KNOWN.
      TEMPO_ABSOLUTO: tm.getAttribute('datetime') || null,
      TEXTO: corpo.join(' ').slice(0, 2000),
      CURTIDAS: mCurt ? parseInt(mCurt, 10) : null
    });
  });
  const visto = new Set(), unicos = [];
  for (const c of achados) {
    const k = c.AUTOR + '|' + c.TEXTO.slice(0, 60);
    if (visto.has(k)) continue;
    visto.add(k); unicos.push(c);
  }
  return { N: unicos.length, COMENTARIOS: unicos };
})()
"""

JS_POST = r"""
(() => {
  const t = document.body.innerText || '';
  const meta = (p) => { const e = document.querySelector('meta[property="' + p + '"]');
                        return e ? e.content : null; };
  const tags = [...document.querySelectorAll('time')].map(x => ({
      datetime: x.getAttribute('datetime'), title: x.getAttribute('title'),
      texto: x.innerText }));
  const og = meta('og:description') || '';
  const mL = og.match(/([\d.,]+)\s*likes?/i);
  const mC = og.match(/([\d.,]+)\s*comments?/i);
  return {
    TIME_TAGS: tags,
    OG_DESCRIPTION: og || null,
    OG_LIKES: mL ? mL[1] : null,
    OG_COMENTARIOS: mC ? mC[1] : null,
    TEXTO_COMENTARIOS_VISIVEL: (t.match(/Ver todos os ([\d.,]+) coment/i)
                             || t.match(/View all ([\d.,]+) comment/i) || [])[1] || null,
    MURO_DE_LOGIN: /Não perca nenhum post|Sign up to see|Cadastre-se no Instagram/i.test(t),
    PAGINA_NAO_ENCONTRADA: /não está disponível|isn't available|no disponible/i.test(t)
  };
})()
"""

# O `contextJSON` do embed é uma STRING de JSON dentro do HTML, com as aspas escapadas.
#
# DUAS COISAS QUE A PRIMEIRA VERSÃO ERRAVA, medidas contra os 60 embeds já guardados em
# `data/samples/INSTAGRAM-JANELA/html-bruto/` — leitura de disco, custo zero:
#
# 1. `contextJSON` NEM SEMPRE TEM VALOR. Em 12 dos 60 o HTML diz, literalmente,
#    `"contextJSON":null`. A versão antiga achava a PALAVRA, não reparava no `null`, ia
#    procurar a próxima `{` da página, encontrava um objeto vizinho qualquer, parseava
#    esse objeto estranho e gravava "achei". É a caixa de bolinhas chacoalhada: fui buscar
#    a bolinha numa caixa e trouxe a de outra.
#
#        PARSER QUE ACHA OUTRA COISA É PIOR QUE PARSER QUE NÃO ACHA NADA.
#
# 2. O DESESCAPE CRU QUEBRAVA O JSON. Trocar toda `\"` por `"` troca também as aspas que
#    estão DENTRO do texto de um valor — a string fecha antes da hora e o JSON morre no
#    meio. Aconteceu em 1 dos 60 (`DctSE_5ii6D`, erro na posição 10054).
#
# O conserto é deixar o PRÓPRIO parser desescapar, uma camada por vez. Medido nos mesmos
# 60 arquivos: 47/60 antes, 48/60 depois, zero perdas, e os 12 `null` passam a ter estado
# próprio em vez de virarem "o post não tem legenda".
JS_EMBED = r"""
(() => {
  const h = document.documentElement.outerHTML;
  const t = document.body.innerText || '';
  const mPosts = t.match(/([\d.,]+)\s*posts?/i);
  const base = { POSTS_DA_CONTA_TEXTO: mPosts ? mPosts[1] : null };

  const m = h.match(/contextJSON(\\*)"\s*:\s*/);
  if (!m) return Object.assign({ ACHOU_CONTEXTJSON: false,
                                 MOTIVO: 'a palavra contextJSON nao aparece no HTML',
                                 TEXTO_VISIVEL: t.slice(0, 1200) }, base);

  const p = m.index + m[0].length;
  if (h.slice(p, p + 4) === 'null')
    return Object.assign({ ACHOU_CONTEXTJSON: false, CONTEXTJSON_NULL: true,
                           MOTIVO: 'o HTML traz "contextJSON":null — a caixa existe e '
                                 + 'esta vazia. Nao e o post que nao tem dado; e esta '
                                 + 'variante do embed que nao carrega o bloco.' }, base);

  // Quantas camadas de escape esta pagina usa. O embed vem com o JSON dentro de uma
  // string JS, entao as aspas chegam escapadas uma ou duas vezes conforme o deploy.
  const niveis = m[1].length;
  const abre = '\\'.repeat(niveis) + '"';
  if (h.slice(p, p + abre.length) !== abre)
    return Object.assign({ ACHOU_CONTEXTJSON: false,
                           MOTIVO: 'o valor de contextJSON nao e uma string' }, base);

  // Andar respeitando o escape: `\"` no meio do texto NAO fecha a string.
  let k = p + abre.length, fim = -1;
  while (k < h.length) {
    if (h[k] === '\\') { k += 2; continue; }
    if (h[k] === '"') { fim = k; break; }
    k++;
  }
  if (fim < 0) return Object.assign({ ACHOU_CONTEXTJSON: false,
                                      MOTIVO: 'a string de contextJSON nao fecha' }, base);

  let o = null, erro = null;
  try {
    let s = h.slice(p + abre.length, fim);
    for (let n = 0; n < Math.max(1, niveis); n++) s = JSON.parse('"' + s + '"');
    o = JSON.parse(s);
  } catch (e) { erro = String(e).slice(0, 200); }

  const mm = o && o.gql_data && o.gql_data.shortcode_media;
  if (!mm) return Object.assign({ ACHOU_CONTEXTJSON: true, PARSE_ERRO: erro,
                                  TEM_GQL: h.indexOf('shortcode_media') >= 0 }, base);
  const md = mm;
  const cap = (((md.edge_media_to_caption || {}).edges || [])[0] || {}).node;
  const dono = md.owner || {};
  return {
    ACHOU_CONTEXTJSON: true,
    TIPO: md.__typename || null,
    ID_NUMERICO: md.id || null,
    SHORTCODE: md.shortcode || null,
    E_VIDEO: !!md.is_video,
    PRODUCT_TYPE: md.product_type || null,
    LEGENDA: cap ? cap.text : null,
    CURTIDAS: (md.edge_media_preview_like || md.edge_liked_by || {}).count,
    COMENTARIOS: (md.edge_media_to_comment || {}).count,
    VIDEO_VIEWS: md.video_view_count == null ? null : md.video_view_count,
    VIDEO_DURACAO_S: md.video_duration == null ? null : md.video_duration,
    VIDEO_URL: md.video_url || null,
    IMAGEM_URL: md.display_url || null,
    CARROSSEL_ITENS: ((md.edge_sidecar_to_children || {}).edges || []).length,
    TEXTO_ALTERNATIVO: md.accessibility_caption || null,
    AUDIO: (md.clips_music_attribution_info || {}).song_name || null,
    COAUTORES: (md.coauthor_producers || []).map(c => c.username),
    DONO_USERNAME: dono.username || null,
    DONO_ID: dono.id || null,
    DONO_SEGUIDORES: (dono.edge_followed_by || {}).count,
    DONO_VERIFICADO: dono.is_verified == null ? null : dono.is_verified,
    POSTS_DA_CONTA_TEXTO: mPosts ? mPosts[1] : null,
    TAKEN_AT: md.taken_at_timestamp == null ? null : md.taken_at_timestamp
  };
})()
"""


# ─────────────────────────────────────────────────────────────────────── utilitários
def contas():
    """As contas de Instagram do LOTE CONGELADO. Este arquivo obedece, não escolhe."""
    if not os.path.exists(LOTE):
        raise SystemExit(
            'sem lote congelado em %s.\n'
            'A coleta não improvisa a lista: ela obedece a uma lista datada.' % LOTE)
    with open(LOTE, encoding='utf-8') as f:
        d = json.load(f)
    return [c for c in d['ACCOUNTS'] if c.get('PLATFORM') == 'INSTAGRAM']


def agora():
    import datetime
    return datetime.datetime.utcnow().replace(microsecond=0).isoformat() + 'Z'


def hoje():
    import datetime
    return datetime.date.today().isoformat()


def _gravar(nome, corpo):
    os.makedirs(SAIDA, exist_ok=True)
    with open(os.path.join(SAIDA, nome), 'w', encoding='utf-8') as f:
        json.dump(corpo, f, ensure_ascii=False, indent=1)
    return 'data/samples/INSTAGRAM-JANELA/' + nome


def _ler(nome):
    p = os.path.join(SAIDA, nome)
    if not os.path.exists(p):
        return None
    with open(p, encoding='utf-8') as f:
        return json.load(f)


def _guardar_html(nome, html):
    """O HTML cru, ANTES de normalizar. Mesma lei da rota paga, aplicada à rota grátis.

    Sem isto, um erro de leitor obrigaria a abrir a página de novo — e a página de
    amanhã não é a de hoje. O bruto é o que torna a normalização refazível de graça.
    """
    import gzip
    os.makedirs(BRUTO, exist_ok=True)
    caminho = os.path.join(BRUTO, nome + '.html.gz')
    with gzip.open(caminho, 'wt', encoding='utf-8', compresslevel=9) as f:
        f.write(html or '')
    return 'data/samples/INSTAGRAM-JANELA/html-bruto/' + nome + '.html.gz'


def _slug(s):
    return re.sub(r'[^A-Za-z0-9_.-]', '-', str(s or ''))[:60]


def _numero(texto):
    """"18,7 mil" → 18700. Devolve `(valor, COMO)` — e `NOT_KNOWN` quando não der.

    Por que devolve o COMO junto: "18,7 mil" é um número ARREDONDADO pela própria tela.
    O valor exato (18.737) só aparece na rota de embed. Tratar os dois como o mesmo
    número faria uma variação de arredondamento virar "a conta perdeu seguidores".

        NÚMERO ARREDONDADO PELA FONTE ≠ NÚMERO MEDIDO.
    """
    if not texto:
        return NAO_SEI, 'a fonte não mostrou'
    t = str(texto).strip().lower().replace(' ', ' ')
    m = re.match(r'^([\d.,]+)\s*(mil|k|m|mi)?$', t)
    if not m:
        return NAO_SEI, 'formato não reconhecido: %r' % texto[:30]
    corpo, sufixo = m.group(1), m.group(2)
    # pt-BR e es usam ponto para milhar e vírgula para decimal.
    if ',' in corpo and '.' in corpo:
        corpo = corpo.replace('.', '').replace(',', '.')
    elif ',' in corpo:
        corpo = corpo.replace(',', '.') if len(corpo.split(',')[-1]) < 3 else corpo.replace(',', '')
    elif corpo.count('.') == 1 and len(corpo.split('.')[-1]) == 3:
        corpo = corpo.replace('.', '')                 # 2.751 é dois mil, não 2,751
    try:
        v = float(corpo)
    except ValueError:
        return NAO_SEI, 'não virou número: %r' % texto[:30]
    fator = {'mil': 1000, 'k': 1000, 'm': 1_000_000, 'mi': 1_000_000}.get(sufixo, 1)
    exato = fator == 1 and '.' not in corpo
    return int(v * fator), ('valor exato da tela' if exato
                            else 'ARREDONDADO pela própria tela ("%s")' % texto)


_SAIDA_DE_REDE = {}


def saida_de_rede():
    """De que país esta leitura saiu. Medido uma vez por execução, e gravado no artefato.

    POR QUE ISTO ENTROU NA PROVENIÊNCIA, em 2026-09-02
    ----------------------------------------------------
    A coleta desta casa passou a sair por VPN na Itália. O Instagram serve conteúdo,
    idioma e — principalmente — **exigência de consentimento de cookie** conforme o país
    de onde o pedido chega. Um IP europeu pode receber um banner de GDPR que o brasileiro
    não recebe, e esse banner é desenhado ANTES da página.

    Ler o banner e contar zero post seria `SOURCE_FAILURE` disfarçado de conta vazia —
    a mesma lei de sempre, quebrada por uma mudança de rota de REDE que ninguém anotou.

    E há a armadilha de comparação, que a Biblioteca de Anúncios já pregou aqui: duas
    coletas com saídas de rede diferentes NÃO são comparáveis sem que isso seja dito.

        MUDAR A ROTA DE REDE ENTRE DUAS MEDIÇÕES É MUDAR O MÉTODO.

    A leitura usa um serviço público, sem credencial. Se falhar, sai `NOT_KNOWN` — nunca
    um país adivinhado.
    """
    if _SAIDA_DE_REDE:
        return _SAIDA_DE_REDE
    import urllib.request
    try:
        with urllib.request.urlopen('https://ipinfo.io/json', timeout=15) as r:
            d = json.loads(r.read().decode('utf-8', 'replace'))
        _SAIDA_DE_REDE.update({
            'NETWORK_EXIT_COUNTRY': d.get('country') or NAO_SEI,
            'NETWORK_EXIT_REGION': d.get('region') or NAO_SEI,
            'NETWORK_EXIT_ORG': (d.get('org') or NAO_SEI)[:60],
            'NETWORK_EXIT_HOW': 'ipinfo.io — serviço público, sem credencial',
        })
    except Exception as e:                                    # noqa: BLE001
        _SAIDA_DE_REDE.update({
            'NETWORK_EXIT_COUNTRY': NAO_SEI, 'NETWORK_EXIT_REGION': NAO_SEI,
            'NETWORK_EXIT_ORG': NAO_SEI,
            'NETWORK_EXIT_HOW': 'não medido: %s' % type(e).__name__})
    # O IP em si NÃO é gravado: país e operadora bastam para julgar comparabilidade, e
    # endereço é dado que não precisa entrar em artefato para nada.
    return _SAIDA_DE_REDE


def _proveniencia(rota, url):
    return dict(saida_de_rede(), **{
        'COLLECTION_METHOD': 'CHROME_HEADED_CDP',
        'COLLECTION_ROUTE': rota,
        'SOURCE_URL': url,
        'LOGGED_IN': 'NO',
        'CAPTURED_AT': agora(),
        'MISSION': MISSION,
        'RUNNER_NAME': RUNNER,
        'COST_USD': 0,
    })


# ═══════════════════════════════════════════════════════════════ FASE 1 · PERFIS
def perfis():
    """Bio, seguidores, denominador e a grade — das 5 contas do lote. Custo: zero."""
    cs = contas()
    print('lote congelado: %d contas de Instagram' % len(cs))
    cdp.subir(PORTA, perfil=PERFIL)
    achados = []
    for c in cs:
        url = c['ACCOUNT_URL']
        handle = c['ACCOUNT_HANDLE']
        print('  %-18s %-8s %s' % (handle, c['COUNTRY'], c['COMPANY']))
        r = dict(_proveniencia('PROFILE_PAGE', url), **{
            'ACCOUNT_HANDLE': handle, 'ACCOUNT_URL': url,
            'COMPANY': c['COMPANY'], 'COUNTRY_SCOPE': c['COUNTRY'],
        })
        try:
            aba, html = cdp.abrir(url, porta=PORTA, espera=6)
        except cdp.Erro as e:
            # Porta fechada é ESTADO da minha ponta, não fato sobre a conta.
            r.update({'DOOR_STATE': cdp.BROWSER_NOT_REACHED,
                      'WHY': str(e)[:200],
                      'READ_FAILURE_IS_NOT_ZERO': (
                          'não consegui falar com o navegador. Isto NÃO é "a conta não '
                          'tem posts" — é a minha ponta que não abriu.')})
            achados.append(r)
            continue
        try:
            d = aba.js(JS_PERFIL) or {}
            r['RAW_HTML_PATH'] = _guardar_html('perfil-' + _slug(handle), html)
            r['HTML_BYTES'] = len(html or '')
            foto, motivo = cdp.png(aba, os.path.join(PROVAS, 'perfil-%s.png' % _slug(handle)))
            r['SCREENSHOT_PATH'] = ('data/samples/INSTAGRAM-JANELA/provas/perfil-%s.png'
                                    % _slug(handle)) if foto else pv.NOT_PRESERVED
            r['SCREENSHOT_STATE'] = motivo

            seg, como_seg = _numero(d.get('SEGUIDORES_TEXTO'))
            sig, como_sig = _numero(d.get('SEGUINDO_TEXTO'))
            r.update({
                'DOOR_STATE': (cdp.NOT_FOUND if d.get('PAGINA_NAO_ENCONTRADA')
                               else cdp.PAGE_RENDERED),
                'PROFILE_TITLE': d.get('TITULO') or NAO_SEI,
                'BIO_TEXT': d.get('TEXTO_VISIVEL') or NAO_SEI,
                'EXTERNAL_LINK': d.get('LINK_EXTERNO') or NAO_SEI,
                'FOLLOWERS': seg, 'FOLLOWERS_PRECISION': como_seg,
                'FOLLOWERS_RAW_TEXT': d.get('SEGUIDORES_TEXTO') or NAO_SEI,
                'FOLLOWING': sig, 'FOLLOWING_PRECISION': como_sig,
                'GRID_ITEMS_VISIBLE': d.get('ITENS_NA_GRADE') or 0,
                'GRID_CODES': d.get('CODIGOS_NA_GRADE') or [],
                'LOGIN_WALL_AFTER_GRID': 'YES' if d.get('MURO_DE_LOGIN') else 'NO',
                # O denominador NÃO vem daqui: a página do perfil deslogada não publica o
                # total de posts. Ele vem da rota de embed, na fase `objetos`.
                'ACCOUNT_POST_COUNT': NAO_SEI,
                'ACCOUNT_POST_COUNT_SOURCE': 'preenchido pela fase `objetos` (rota embed)',
                'COVERAGE_STATEMENT': (
                    'a grade deslogada mostra %d itens e o muro fecha depois. Isto é o '
                    'TETO DA ROTA, não o tamanho da conta.'
                    % (d.get('ITENS_NA_GRADE') or 0)),
            })
        finally:
            aba.fechar()
        achados.append(r)
        time.sleep(PAUSA)

    caminho = _gravar('PERFIS.json', {
        'SOURCE_ID': 'INSTAGRAM-JANELA/PERFIS',
        **saida_de_rede(),
        'source': 'página pública de perfil, lida em Chrome com janela, DESLOGADO',
        'SOURCE_LOCATION': 'Instagram',
        'FACT_LOCATION': 'NOT_KNOWN — o lugar do fato sai do conteúdo, nunca da conta',
        'ORIGINAL_LANGUAGE': 'multi',
        'EVIDENCE_CLASS': 'COMPETITOR_PUBLIC_COMMUNICATION_OBSERVED',
        'CAPTURED_AT': agora(), 'MISSION': MISSION, 'RUNNER_NAME': RUNNER,
        'COLLECTION_METHOD': 'CHROME_HEADED_CDP', 'LOGGED_IN': 'NO',
        'APIFY_RUNS': 0, 'COST_USD': 0,
        'ACCOUNTS_IN_BATCH': len(cs), 'ACCOUNTS_READ': len(achados),
        'LEI': ('12 itens é o TETO DA ROTA DESLOGADA, medido em duas contas. '
                'GRID_ITEMS_VISIBLE ≠ ACCOUNT_POST_COUNT. Porta fechada é DOOR_STATE, '
                'nunca zero.'),
        'ITEMS': achados})
    print('\ngravado: %s · contas lidas=%d · custo=0,00 USD' % (caminho, len(achados)))
    return 0


# ═══════════════════════════════════════════════════════════════ FASE 2 · OBJETOS
def objetos(limite_por_conta=None):
    """Cada item da grade: data, legenda inteira, curtidas, vídeo. Custo: zero."""
    fonte = _ler('PERFIS.json')
    if not fonte:
        print('SEM PERFIS — rode `py scripts/instagram_janela.py perfis` antes')
        return 1
    cdp.subir(PORTA, perfil=PERFIL)
    achados, denominadores = [], {}
    for p in fonte['ITEMS']:
        codigos = p.get('GRID_CODES') or []
        if limite_por_conta:
            codigos = codigos[:int(limite_por_conta)]
        handle = p['ACCOUNT_HANDLE']
        print('  %-18s %d objetos' % (handle, len(codigos)))
        for cod in codigos:
            tipo, _, shortcode = cod.partition(':')
            r = _objeto(handle, p, tipo, shortcode)
            achados.append(r)
            if r.get('ACCOUNT_POST_COUNT') not in (None, NAO_SEI):
                denominadores[handle] = r['ACCOUNT_POST_COUNT']
            time.sleep(PAUSA)

    # O denominador descoberto no embed volta para o artefato de perfis: sem ele,
    # "12 coletados" não tem contra o que ser lido.
    if denominadores:
        for p in fonte['ITEMS']:
            n = denominadores.get(p['ACCOUNT_HANDLE'])
            if n:
                p['ACCOUNT_POST_COUNT'] = n
                p['ACCOUNT_POST_COUNT_SOURCE'] = 'rota EMBED, lida na fase `objetos`'
                p['COVERAGE_STATEMENT'] = (
                    '%d de %d posts da conta — SUB-COLETA DECLARADA, e é o teto da rota '
                    'deslogada, não uma escolha.' % (p.get('GRID_ITEMS_VISIBLE') or 0, n))
        fonte['DENOMINATOR_BACKFILLED_AT'] = agora()
        _gravar('PERFIS.json', fonte)

    com_data = sum(1 for a in achados if a.get('PUBLISHED_AT') not in (None, NAO_SEI))
    com_legenda = sum(1 for a in achados if a.get('CAPTION') not in (None, NAO_SEI))
    videos = sum(1 for a in achados if a.get('IS_VIDEO') == 'YES')
    caminho = _gravar('OBJETOS.json', {
        'SOURCE_ID': 'INSTAGRAM-JANELA/OBJETOS',
        **saida_de_rede(),
        'source': ('página pública do post + rota de embed pública, em Chrome com janela, '
                   'DESLOGADO'),
        'SOURCE_LOCATION': 'Instagram',
        'FACT_LOCATION': 'NOT_KNOWN — sai do conteúdo, nunca da conta que publicou',
        'ORIGINAL_LANGUAGE': 'multi',
        'EVIDENCE_CLASS': 'COMPETITOR_PUBLIC_COMMUNICATION_OBSERVED',
        'CAPTURED_AT': agora(), 'MISSION': MISSION, 'RUNNER_NAME': RUNNER,
        'COLLECTION_METHOD': 'CHROME_HEADED_CDP', 'LOGGED_IN': 'NO',
        'APIFY_RUNS': 0, 'COST_USD': 0,
        'ITEM_COUNT': len(achados),
        'WITH_ABSOLUTE_DATE': com_data,
        'WITH_FULL_CAPTION': com_legenda,
        'VIDEOS': videos,
        'LEI_DOS_TRES_NUMEROS': (
            'COMMENT_COUNT_EMBED, COMMENT_COUNT_POST_PAGE e COMMENT_COUNT_OG são TRÊS '
            'medições de rotas diferentes e divergem no mesmo post (medido: 2, 2 e 4). '
            'Nenhuma é "o" número. Comparação de engajamento só vale rota contra a MESMA '
            'rota.'),
        'O_QUE_NENHUMA_ROTA_GRATIS_DA': (
            'o TEXTO dos comentários. As três rotas dão a CONTAGEM; nenhuma dá o texto. '
            'Esse é o único motivo real de acionar rota paga.'),
        'ITEMS': achados})
    print('\ngravado: %s' % caminho)
    print('  objetos=%d · com data absoluta=%d · com legenda inteira=%d · vídeos=%d'
          % (len(achados), com_data, com_legenda, videos))
    print('  custo=0,00 USD')
    return 0


def _resgatar_do_og(r):
    """Quando o embed não trouxe o bloco de dados, a etiqueta og: resgata — ROTULADA.

    A `og:description` da página do post tem a forma:

        205 likes, 12 comments - bayer_italia no June 12, 2025: "Oggi è un giorno..."

    Ela salva o objeto de virar uma linha de NOT_KNOWN. Mas ela **trunca a legenda** com
    reticências, e por isso o resgate NUNCA se disfarça de leitura inteira: o campo
    `CAPTION_SOURCE` diz de onde veio e se pode estar cortada. Um corpus que não distingue
    legenda inteira de legenda cortada mede tamanho de texto errado.
    """
    og = r.get('OG_DESCRIPTION')
    if not og or og == NAO_SEI:
        r.setdefault('CAPTION', NAO_SEI)
        r.setdefault('CAPTION_SOURCE', 'nenhuma rota trouxe legenda')
        return r
    m = re.search(r':\s*"(.*)"\s*\.?\s*$', str(og), re.S)
    legenda = m.group(1).strip() if m else None
    truncada = bool(legenda and legenda.endswith(('...', '…')))
    if legenda:
        r['CAPTION'] = legenda
        r['CAPTION_CHARS'] = len(legenda)
        r['CAPTION_SOURCE'] = ('og:description da página do post — %s'
                               % ('PODE ESTAR TRUNCADA (termina em reticências)'
                                  if truncada else 'sem sinal de corte'))
        r['CAPTION_IS_COMPLETE'] = 'NO' if truncada else 'NOT_KNOWN'
    else:
        r.setdefault('CAPTION', NAO_SEI)
        r['CAPTION_SOURCE'] = 'og:description existe mas não tem legenda entre aspas'
    # Curtidas e comentários também: melhor um número com rota declarada que um NOT_KNOWN.
    if r.get('LIKE_COUNT_EMBED', NAO_SEI) == NAO_SEI and r.get('LIKE_COUNT_OG') != NAO_SEI:
        r['LIKE_COUNT_RESOLVED'] = _numero(r.get('LIKE_COUNT_OG'))[0]
        r['LIKE_COUNT_RESOLVED_ROUTE'] = 'OG_DESCRIPTION'
    if (r.get('COMMENT_COUNT_EMBED', NAO_SEI) == NAO_SEI
            and r.get('COMMENT_COUNT_OG') != NAO_SEI):
        r['COMMENT_COUNT_RESOLVED'] = _numero(r.get('COMMENT_COUNT_OG'))[0]
        r['COMMENT_COUNT_RESOLVED_ROUTE'] = 'OG_DESCRIPTION'
    return r


def _objeto(handle, perfil, tipo, shortcode):
    """Um objeto lido por DUAS rotas: a página do post (data) e o embed (o resto)."""
    url_post = 'https://www.instagram.com/%s/%s/' % ('reel' if tipo == 'reel' else 'p',
                                                     shortcode)
    url_embed = 'https://www.instagram.com/p/%s/embed/captioned/' % shortcode
    r = dict(_proveniencia('POST_PAGE + EMBED', url_post), **{
        'OBJECT_ID': shortcode,
        'SHORTCODE': shortcode,
        'OBJECT_KIND_FROM_GRID': tipo.upper(),
        'ACCOUNT_HANDLE': handle,
        'ACCOUNT_URL': perfil.get('ACCOUNT_URL'),
        'COMPANY': perfil.get('COMPANY'),
        'COUNTRY_SCOPE': perfil.get('COUNTRY_SCOPE'),
        'EMBED_URL': url_embed,
        # O lugar do fato NUNCA sai do país da conta nem do idioma do texto.
        'COUNTRY_OF_FACT': 'NOT_KNOWN',
        'REGION_OF_FACT': 'NOT_KNOWN',
        # O assunto NÃO é lido aqui. A Missão 14 tem conta corporativa que publica fora
        # do agro (medido: @bayer_italia é a conta guarda-chuva e fala de saúde), e um
        # corpus que não marca isso faz "a Bayer publicou X vezes" virar número falso.
        'SUBJECT_DOMAIN': 'NOT_CLASSIFIED',
        'SUBJECT_DOMAIN_HOW': 'classificação roda depois, de graça, sobre este artefato',
    })

    # ── rota 1: página do post. É a ÚNICA das três que dá a data absoluta.
    try:
        aba, html = cdp.abrir(url_post, porta=PORTA, espera=5)
        try:
            d = aba.js(JS_POST) or {}
            r['RAW_HTML_POST_PATH'] = _guardar_html('post-' + _slug(shortcode), html)
            tags = d.get('TIME_TAGS') or []
            dt = next((t.get('datetime') for t in tags if t.get('datetime')), None)
            r.update({
                'PUBLISHED_AT': dt or NAO_SEI,
                'PUBLISHED_AT_SOURCE': ('<time datetime> da página do post'
                                        if dt else 'a página não trouxe <time>'),
                'PUBLISHED_AT_HUMAN': next((t.get('title') for t in tags if t.get('title')),
                                           NAO_SEI),
                'OG_DESCRIPTION': d.get('OG_DESCRIPTION') or NAO_SEI,
                'LIKE_COUNT_OG': d.get('OG_LIKES') or NAO_SEI,
                'COMMENT_COUNT_OG': d.get('OG_COMENTARIOS') or NAO_SEI,
                'COMMENT_COUNT_POST_PAGE': d.get('TEXTO_COMENTARIOS_VISIVEL') or NAO_SEI,
                'POST_PAGE_STATE': (cdp.NOT_FOUND if d.get('PAGINA_NAO_ENCONTRADA')
                                    else cdp.PAGE_RENDERED),
            })
        finally:
            aba.fechar()
    except cdp.Erro as e:
        r.update({'POST_PAGE_STATE': cdp.NAVIGATION_FAILED,
                  'PUBLISHED_AT': NAO_SEI,
                  'WHY_POST_PAGE': str(e)[:200]})

    time.sleep(PAUSA / 2)

    # ── rota 2: embed. Legenda INTEIRA, curtidas, vídeo, e o denominador da conta.
    try:
        aba, html = cdp.abrir(url_embed, porta=PORTA, espera=4)
        try:
            e = aba.js(JS_EMBED) or {}
            r['RAW_HTML_EMBED_PATH'] = _guardar_html('embed-' + _slug(shortcode), html)
            if not e.get('ACHOU_CONTEXTJSON') or not e.get('TIPO'):
                # MEDIDO em 2026-09-02: para alguns posts o Instagram serve um embed
                # ENXUTO — o `contextJSON` está lá, mas sem o bloco `shortcode_media`.
                # Três dos dez objetos do teste caíram aqui (@bayer_italia DKzXiwvIVx_ e
                # dois de @syngentaitalia).
                #
                # A primeira versão deste arquivo marcava esses três como PAGE_RENDERED e
                # preenchia legenda, curtidas e comentários com NOT_KNOWN. Isso se lê como
                # "o post não tem legenda" — e os três TÊM: a etiqueta og:description da
                # página do post traz legenda, curtidas e nº de comentários.
                #
                #     PARSER SEM DADO ≠ FONTE SEM DADO.
                #
                # É o mesmo defeito de classe que a lei SOURCE_FAILURE != ZERO existe para
                # impedir, cometido de dentro para fora. Agora o estado diz o que houve, e
                # a outra rota resgata o conteúdo — rotulada como tal.
                # Três estados diferentes, e cada um pede uma conduta diferente de quem
                # lê o artefato depois. Juntar os três num "não veio" apagaria a única
                # informação útil: DE QUE JEITO não veio.
                estado = ('EMBED_CONTEXTJSON_NULL' if e.get('CONTEXTJSON_NULL')
                          else 'EMBED_PARSE_FAILED' if e.get('PARSE_ERRO')
                          else 'EMBED_WITHOUT_GQL_DATA' if e.get('ACHOU_CONTEXTJSON')
                          else 'EMBED_WITHOUT_CONTEXTJSON')
                r.update({
                    'EMBED_STATE': estado,
                    'WHY_EMBED': str(e.get('PARSE_ERRO') or e.get('MOTIVO')
                                     or e.get('ERRO')
                                     or 'o embed montou sem o bloco shortcode_media')[:250],
                    'ACCOUNT_POST_COUNT': _numero(e.get('POSTS_DA_CONTA_TEXTO'))[0],
                })
                _resgatar_do_og(r)
            else:
                posts_conta, _como = _numero(e.get('POSTS_DA_CONTA_TEXTO'))
                r.update({
                    'EMBED_STATE': cdp.PAGE_RENDERED,
                    'MEDIA_TYPE': e.get('TIPO') or NAO_SEI,
                    'PRODUCT_TYPE': e.get('PRODUCT_TYPE') or NAO_SEI,
                    'IS_VIDEO': 'YES' if e.get('E_VIDEO') else 'NO',
                    'EXTERNAL_ID': e.get('ID_NUMERICO') or NAO_SEI,
                    'CAPTION': e.get('LEGENDA') if e.get('LEGENDA') else NAO_SEI,
                    'CAPTION_CHARS': len(e.get('LEGENDA') or ''),
                    # A rota de embed entrega a legenda INTEIRA — sem o "... mais" que a
                    # página do post mostra e sem as reticências da og:description.
                    'CAPTION_SOURCE': 'contextJSON da rota de embed — legenda inteira',
                    'CAPTION_IS_COMPLETE': 'YES' if e.get('LEGENDA') else 'NOT_KNOWN',
                    'LIKE_COUNT_EMBED': (e.get('CURTIDAS') if e.get('CURTIDAS') is not None
                                         else NAO_SEI),
                    'COMMENT_COUNT_EMBED': (e.get('COMENTARIOS')
                                            if e.get('COMENTARIOS') is not None else NAO_SEI),
                    'VIDEO_VIEW_COUNT': (e.get('VIDEO_VIEWS')
                                         if e.get('VIDEO_VIEWS') is not None else NAO_SEI),
                    'VIDEO_DURATION_S': (e.get('VIDEO_DURACAO_S')
                                         if e.get('VIDEO_DURACAO_S') is not None else NAO_SEI),
                    # A URL do MP4 é assinada e EXPIRA. Guardar como se fosse endereço
                    # permanente faria o artefato apontar para o nada em algumas horas.
                    'VIDEO_URL_TEMPORARY': e.get('VIDEO_URL') or NAO_SEI,
                    'VIDEO_URL_WARNING': ('URL assinada pela CDN da Meta: EXPIRA em horas. '
                                          'Serve para baixar agora, não para citar depois.'),
                    'IMAGE_URL_TEMPORARY': e.get('IMAGEM_URL') or NAO_SEI,
                    'CAROUSEL_ITEMS': e.get('CARROSSEL_ITENS') or 0,
                    'ALT_TEXT': e.get('TEXTO_ALTERNATIVO') or NAO_SEI,
                    'AUDIO_NAME': e.get('AUDIO') or NAO_SEI,
                    'COAUTHORS': e.get('COAUTORES') or [],
                    'OWNER_NUMERIC_ID': e.get('DONO_ID') or NAO_SEI,
                    'OWNER_FOLLOWERS_EXACT': (e.get('DONO_SEGUIDORES')
                                              if e.get('DONO_SEGUIDORES') is not None
                                              else NAO_SEI),
                    'OWNER_VERIFIED': (e.get('DONO_VERIFICADO')
                                       if e.get('DONO_VERIFICADO') is not None else NAO_SEI),
                    'ACCOUNT_POST_COUNT': posts_conta,
                    # Medido: o embed NÃO traz taken_at_timestamp. É por isso que a
                    # página do post continua sendo lida — ela é a dona da data.
                    'EMBED_HAS_TIMESTAMP': 'YES' if e.get('TAKEN_AT') else 'NO',
                })
        finally:
            aba.fechar()
    except cdp.Erro as ex:
        r.update({'EMBED_STATE': cdp.NAVIGATION_FAILED, 'WHY_EMBED': str(ex)[:200]})

    # As contagens de comentário, lado a lado e com o nome da rota. A divergência entre
    # elas é DADO, não defeito — e some se alguém escolher uma.
    #
    # MEDIDO: das três rotas que eu esperava, só DUAS publicam número. A página do post
    # mostra "Carregar mais comentários", SEM o total — o rótulo "Ver todos os N
    # comentários" que eu tinha visto uma vez não é o que ela renderiza de forma estável.
    # Deixar o campo vazio faria parecer que a rota foi lida e deu zero.
    if r.get('COMMENT_COUNT_POST_PAGE') in (None, NAO_SEI):
        r['COMMENT_COUNT_POST_PAGE'] = NAO_SEI
        r['COMMENT_COUNT_POST_PAGE_WHY'] = (
            'a página do post não publica o total de forma estável: renderiza '
            '"Carregar mais comentários", sem número. NÃO é zero — é rota que não conta.')
    numeros = {}
    for rota, v in (('EMBED', r.get('COMMENT_COUNT_EMBED')),
                    ('POST_PAGE', r.get('COMMENT_COUNT_POST_PAGE')),
                    ('OG_DESCRIPTION', r.get('COMMENT_COUNT_OG'))):
        if v not in (None, NAO_SEI):
            numeros[rota] = _numero(v)[0] if isinstance(v, str) else v
    r['COMMENT_COUNT_BY_ROUTE'] = numeros
    r['COMMENT_COUNT_ROUTES_AGREE'] = (
        'YES' if len(set(numeros.values())) <= 1 else
        'NO — %s. Comparação de engajamento só vale rota contra a MESMA rota.' % numeros)
    r['COMMENT_TEXT'] = None
    r['COMMENT_TEXT_STATE'] = 'NOT_AVAILABLE_ON_FREE_ROUTE'
    return r


if __name__ == '__main__':
    cmd = sys.argv[1] if len(sys.argv) > 1 else 'perfis'
    lim = sys.argv[2] if len(sys.argv) > 2 else None
    if cmd == 'perfis':
        raise SystemExit(perfis())
    if cmd == 'objetos':
        raise SystemExit(objetos(lim))
    if cmd == 'tudo':
        raise SystemExit(perfis() or objetos(lim))
    print('uso: instagram_janela.py {perfis|objetos|tudo} [limite_por_conta]')
    raise SystemExit(2)
