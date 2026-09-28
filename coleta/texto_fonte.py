#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TEXTO LIMPO DE UMA FONTE PÚBLICA — ajudante de leitura, sem chave e sem custo.

    python3 coleta/texto_fonte.py eu 32026R1826          # ato da UE, texto integral EN
    python3 coleta/texto_fonte.py gire Lolium            # ficha de espécie do GIRE
    python3 coleta/texto_fonte.py url <endereco>         # qualquer HTML/PDF público

POR QUE ISTO EXISTE
--------------------
Os atos da UE chegam como XHTML de 30-300 KB com marcação de diagramação, e a ficha do
GIRE chega com menu, CSS e contador de visitas em volta do conteúdo. Ler tag a tag gasta
contexto e esconde a frase que decide. Este arquivo devolve só o texto.

    ⛔ ELE NÃO INTERPRETA NADA. Devolve texto. A leitura é de quem chamou.
"""
import html
import io
import re
import sys
import urllib.request

UA = ('Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 '
      '(KHTML, like Gecko) Chrome/126.0 Safari/537.36')
CELLAR = 'https://publications.europa.eu/resource/celex/%s'
GIRE = 'http://gire.mlib.cnr.it/index.php?sel=schedeSpecie/%s'


def _bruto(url, accept=None):
    req = urllib.request.Request(url, headers={
        'User-Agent': UA,
        'Accept': accept or 'text/html,application/xhtml+xml,*/*',
        'Accept-Language': 'eng',
    })
    with urllib.request.urlopen(req, timeout=120) as r:
        return r.read(), (r.headers.get('Content-Type') or '')


def _pdf(dados):
    """PDF sem dependência externa: extrai os literais de texto dos fluxos."""
    try:
        import zlib
    except ImportError:
        return '[PDF: zlib indisponível]'
    saida = []
    for m in re.finditer(rb'stream\r?\n(.*?)endstream', dados, re.S):
        bloco = m.group(1)
        try:
            bloco = zlib.decompress(bloco)
        except Exception:                                        # noqa: BLE001
            continue
        for t in re.findall(rb'\((?:\\.|[^\\()])*\)', bloco):
            s = t[1:-1]
            s = re.sub(rb'\\([()\\])', rb'\1', s)
            try:
                saida.append(s.decode('latin-1'))
            except Exception:                                    # noqa: BLE001
                pass
    txt = ' '.join(saida)
    return re.sub(r'\s+', ' ', txt).strip() or '[PDF sem texto extraível — pode ser imagem]'


# ── A ESTRUTURA DE BLOCO SOBREVIVE À LIMPEZA (DERIVACAO-ESTRUTURA, 28/09) ────
# Até aqui TODA etiqueta virava espaço. Medido no RAW 2272 (CREA, derived:1149):
# 186 `</div>`, 28 `<p>`, 9 `<h2>` — e o texto derivado saía com UMA linha de
# 8 988 caracteres, menu, data, título e corpo colados. Quem lê por linha a
# jusante (`leis/fato_do_texto.py::corpo`) ficava cego: corpo = 0 caracteres.
#
# Uma etiqueta de BLOCO significa «aqui acaba uma linha»; passa a dar `\n`. As
# outras (inline: `a`, `span`, `b`, `em`…) continuam a dar espaço, como antes.
# Sem biblioteca nova e sem segundo extrator: é a mesma `limpar()`.
#
#     O HTML JÁ DIZ ONDE ACABA A LINHA. APAGAR ISSO NÃO É LIMPAR, É ACHATAR.
BLOCOS = ('p', 'div', 'li', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'br', 'tr',
          'td', 'th', 'section', 'article', 'header', 'footer', 'nav', 'aside',
          'blockquote', 'pre', 'ul', 'ol', 'table', 'dd', 'dt', 'figure',
          'figcaption', 'main', 'form', 'hr')
_RE_BLOCO = re.compile(r'</?(?:%s)\b' % '|'.join(BLOCOS), re.I)

# ── UMA ETIQUETA NÃO ATRAVESSA OUTRO «<» (DERIVACAO-ESTRUTURA-V2, 28/09) ──────
# A régua 2 fazia DUAS passagens: primeiro o bloco virava `\n`, depois o resto
# `<[^>]+>` virava espaço. Medido no balsâmico (IT-T7-042, 30 páginas na árvore,
# 14 no armazém): `…ES</a></</div></div>…`. A 1.ª passagem trocava `</div>` por
# `\n` e o «</» órfão ficava sem o seu «>»; a 2.ª engolia dali até o PRÓXIMO «>»
# — 328 caracteres, atravessando linhas, título e subtítulo do artigo.
#
# Agora é UMA passagem: cada etiqueta é `<…>` SEM outro «<» dentro, começada
# por letra, `/`, `!` ou `?` (como no leitor do navegador), e decide-se
# ali mesmo se é bloco (`\n`) ou inline (espaço). Não há passagem anterior que
# abra buraco, então uma etiqueta também não atravessa quebra de linha criada
# por bloco. Exceção medida: dentro de `<!--` o «<» não abre etiqueta (é
# conteúdo do comentário), e o comentário acaba no primeiro «>», como sempre
# acabou — tratá-lo inteiro até `-->` apagaria texto que a `limpar()` sempre mostrou
# (71/216 páginas da árvore), e isso é outra mudança.
#
# O «<» de marcação que sobra sem «>» (`</`, `<!--`, `<!`, `<?`) vira espaço até
# o próximo branco; um «<» diante de espaço ou algarismo é texto e fica.
#
#     UMA ETIQUETA QUE ENGOLE OUTRA NÃO É ETIQUETA, É BURACO.
_RE_ETIQUETA = re.compile(r'<!--[^>]*>|<[A-Za-z/!?][^<>]*>')
_RE_ORFAO = re.compile(r'<[/!?][^\s<>]*')


def _etiqueta(m):
    return '\n' if _RE_BLOCO.match(m.group(0)) else ' '

#: A RÉGUA DE EXTRAÇÃO, com nome. Entra na receita do derivado
#: (`executor_texto_de_html.receita`) junto com a impressão da SONDA abaixo.
#:
#: ⚠️ O ALGORITMO TEM DE ESTAR NA IDENTIDADE DO DERIVADO. Antes desta mudança a
#: receita dizia só QUEM extrai (`TEXT_OWNER`), nunca COMO: mudar `limpar()`
#: mudava o texto e deixava a receita igual — o derivado achatado e o
#: estruturado do mesmo RAW ficariam os dois `texto-de-html` "2".
REGUA = ('limpar/3 (uma passagem: etiqueta sem outro < dentro; bloco -> quebra de '
         'linha; < de marcacao orfao -> espaco)')

#: Um HTML pequeno e FIXO que exercita tudo o que `limpar()` decide: cada
#: etiqueta de bloco, inline, script/style, comentário, entidades, `&nbsp;`,
#: maiúsculas, atributos, espaços e linhas vazias. O sha256 do que `limpar()`
#: devolve para ela é a impressão da régua: qualquer mudança de COMPORTAMENTO
#: move-a (e reprova `tests/test_a_receita_tem_versao.py` até a versão subir);
#: mexer num comentário, não.
#:
#:     ⛔ NÃO SE EDITA ESTA SONDA SEM SUBIR `EXECUTOR_VERSION`.
SONDA = (
    b'<!doctype html><html><head><title>Sonda &amp; r\xc3\xa9gua</title>'
    b'<style>.x{color:red}</style><script>var a = "<p>nao</p>";</script></head>'
    b'<BODY class="b"><!-- comentario --><header>Cabe<b>\xc3\xa7a</b>lho</header>'
    b'<nav><ul><li><a href="/a">Um</a></li><li>Dois</li></ul></nav><main><article>'
    b'<h1>T1</h1><h2>T2</h2><h3>T3</h3><h4>T4</h4><h5>T5</h5><h6>T6</h6>'
    b'<div class="content-metadata"><div class="content-category">CAT</div>'
    b'&nbsp;<span>-</span>&nbsp;<div class="content-date"> 22 giu 2026 </div></div>'
    b'<section><p>Primeira   frase\t com  <em>\xc3\xaanfase</em> e <strong>for\xc3\xa7a</strong>.</p>'
    b'<P ALIGN="x">Segunda<br>quebra<br/>outra<BR />fim</p></section>'
    b'<blockquote>cita</blockquote><pre>pre   formatado</pre><hr>'
    b'<table><tr><th>h1</th><th>h2</th></tr><tr><td>c1</td><td>c2</td></tr></table>'
    b'<ol><li>um</li></ol><dl><dt>termo</dt><dd>def</dd></dl>'
    b'<figure>img<figcaption>legenda</figcaption></figure><form>campo</form>'
    b'<aside>lado</aside></article></main>\n\n\n<footer>&copy; rodap&eacute; &lt;x&gt;'
    b'</footer><param name="p"><thead>th</thead><pa>x</pa>'
    # régua 3: o «</» órfão do balsâmico, um comentário com bloco dentro, um «<»
    # que é texto, um `<!` e um `<?` sem fecho, e o «<» órfão antes de um inline
    b'<ul><li><a href="/es">ES</a></</div></div>\r\n<div class="t">TITOLO</div>'
    b'<h2>sottotitolo</h2><!-- <div class="x"> -->dopo<p>se a < 5 e b >= 2</p>'
    b'<p>x <!doctype y <? z</p><p>resto </<b>grassetto</b></p></BODY></html>'
)


def limpar(dados, ctype=''):
    if 'pdf' in ctype.lower() or dados[:5] == b'%PDF-':
        return _pdf(dados)
    t = dados.decode('utf-8', errors='replace')
    t = re.sub(r'<(script|style)\b.*?</\1>', ' ', t, flags=re.S | re.I)
    t = _RE_ETIQUETA.sub(_etiqueta, t)
    t = _RE_ORFAO.sub(' ', t)
    t = html.unescape(t)
    t = re.sub(r'[ \t\xa0]+', ' ', t)
    t = re.sub(r'\n\s*\n+', '\n', t)
    return '\n'.join(l.strip() for l in t.split('\n') if l.strip())


def impressao_da_regua():
    """sha256 do que `limpar()` devolve para a `SONDA`. Comportamento, não código."""
    import hashlib
    return hashlib.sha256(limpar(SONDA, 'text/html').encode('utf-8')).hexdigest()


def main():
    if len(sys.argv) < 3:
        print(__doc__); return 2
    modo, alvo = sys.argv[1], sys.argv[2]
    url = {'eu': CELLAR % alvo, 'gire': GIRE % alvo}.get(modo, alvo)
    try:
        dados, ctype = _bruto(url)
    except Exception as e:                                       # noqa: BLE001
        print('FALHA_DE_REDE %s: %s' % (type(e).__name__, str(e)[:200])); return 1
    txt = limpar(dados, ctype)
    print('FONTE: %s' % url)
    print('BYTES_BRUTOS: %d · CARACTERES_LIMPOS: %d' % (len(dados), len(txt)))
    print('-' * 70)
    sys.stdout.write(txt)
    return 0


if __name__ == '__main__':
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except Exception:                                            # noqa: BLE001
        pass
    sys.exit(main())
