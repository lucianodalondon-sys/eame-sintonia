# V8 · PREVIEW NA VERCEL — O CASCO SAI DO DISCO E VIRA URL

**Data:** 2026-08-31 · antecede `V8-RECEPTOR-CLOSEOUT.md`, não o substitui

```
NO SUPABASE WIRING · NO REAL DATA · NO PRODUCTION DEPLOY · NO MAIN MERGE
NO DESIGN CHANGE · NO ONTOLOGY CHANGE · NO SECRET
```

---

## 0 · O QUE ESTA RODADA FEZ E O QUE NÃO FEZ

Fez uma coisa só: **deu à testemunha do casco um caminho para virar site**. Nenhum byte
do casco foi alterado. Nenhuma tela foi redesenhada. Nada foi ligado a banco.

---

## 1 · A TESTEMUNHA ESTAVA INCOMPLETA — E ISSO SÓ APARECE NO NAVEGADOR

`casco/canonical/deploy-v8-closeout/` guardava quatro arquivos: o `index` gzipado,
`support.js`, `crop-map.js` e `vercel.json`. Ela fechou o casco e fechou bem.

**Mas o `index.html` do export não é auto-contido.** Ele pede por URL:

```
./support.js                                          ✅ estava
crop-map.js                                           ✅ estava
_ds/adama-brasil-design-system-<uuid>/…  (7 arquivos) ❌ NÃO estava
assets/…                                 (7 arquivos) ❌ NÃO estava
```

São **20 arquivos que faltavam** (5 CSS, 1 JS de bundle, 1 JSON de aderência, 1 readme,
4 fontes, 7 imagens). Servido como estava, o portal abriria **sem fonte, sem cor de token
e sem logo** — e nada no repositório denunciava isso, porque nenhum teste abria o
navegador. A diferença entre "o casco está pronto" e "o casco abre" é exatamente essa.

⚠️ Isso **não invalida** o `CASCO_RECEPTOR_READY = YES`. Aquilo mediu os receptores, e a
medição continua de pé. É outra pergunta, feita pela primeira vez agora.

---

## 2 · DE ONDE VIERAM OS 20 ARQUIVOS — E POR QUE SÃO OS MESMOS

Do mesmo export: `C:\Users\London1\Downloads\Formulário e próximos passos.zip`
(849.114 bytes, `b1256d71708cfaae97b20756c18a67774cf3bdb826bb909404a6222d6f5c925b` — o
arquivo sobrescrito de que fala a seção 0 do CLOSEOUT).

**Não confiei no nome do arquivo. Conferi os bytes.** Os quatro que já estavam
commitados foram medidos contra os do zip:

```
                      TESTEMUNHA NO GIT                    ZIP                  BATE
index.html   372.425  d28f6b58…f4e81328    372.425  d28f6b58…f4e81328    ✅ idêntico
support.js    69.150  8fe7df74…2e28cbe     69.150  8fe7df74…2e28cbe      ✅ idêntico
crop-map.js   10.156  a55c6011…bb1614c8    10.156  a55c6011…bb1614c8     ✅ idêntico
vercel.json       23  b7790313…bf745842        23  b7790313…bf745842     ✅ idêntico
```

Quatro de quatro batem, byte a byte, e o SHA do `index` é o mesmo publicado na seção 9 do
CLOSEOUT. **É o mesmo export.** Por isso os 20 arquivos que faltavam podem ser
adicionados sem abrir uma segunda linhagem: eles vieram da mesma caixa.

Cada um dos 27 ativos tem tamanho e SHA-256 registrados em
`casco/canonical/deploy-v8-closeout/ASSETS-SHA256.json`.

---

## 3 · UMA CÓPIA SÓ DO CASCO — E UMA TRANSFORMAÇÃO SÓ

Não criei pasta `deploy/` na raiz. O casco continua existindo **em um lugar**: gzipado,
como testemunha. O Preview é gerado, não guardado.

```
deploy-index.html.gz  ──gunzip──►  public/index.html        ← única transformação
support.js            ──cópia───►  public/support.js
crop-map.js           ──cópia───►  public/crop-map.js
_ds/ + assets/        ──cópia───►  public/_ds/ + public/assets/
```

O build está em `build-preview.mjs` (Node puro, `zlib` e `crypto` da biblioteca padrão,
**zero dependências**). Ele confere o SHA-256 de **cada byte que escreve** contra a
testemunha. Se um único arquivo divergir, o build falha e a Vercel não publica.
Também reprova se um ativo entrar de carona ou se um do manifesto não sair.

### O gzip não é capricho

`_ds_bundle.js` **também** teve de ser guardado como `.gz`. O antivírus deste ambiente
removeu o `.js` do disco depois da escrita — o mesmo comportamento que já obrigou o
`index.html` a virar `.gz` na rodada anterior. Aconteceu de novo, no meio desta rodada,
e o próprio build pegou (`ativos do manifesto que nao sairam`). O ambiente de build da
Vercel é Linux e não tem esse problema; o `.gz` existe para atravessar **este** disco.

---

## 4 · O BUILD LOCAL RODOU

```
$ npm run build
OK  index.html + support.js + crop-map.js + 27 ativos  ->  public/
OK  index.html sha256 = d28f6b5876e2fa28720eb555a8b99a275e56c229ed0ac5c4b07edf89f4e81328

30 arquivos em public/
```

`LOCAL_BUILD_PASS = YES`

---

## 5 · O PORTAL FOI ABERTO DE VERDADE, EM NAVEGADOR

Servido estático em `localhost:8788`, **sem fallback de SPA** — de propósito, para
imitar a Vercel e não mascarar 404.

```
200  /
200  /support.js
200  /crop-map.js
200  /assets/Adama_H_white.png
200  /assets/a-shape-full.svg
200  /_ds/…/_ds_bundle.js
200  /_ds/…/assets/fonts/BrownLL-Regular.otf
```

**Nenhum 404 em nenhuma requisição da página.** E o que o navegador confirmou por dentro:

```
customElements.get('crop-map')  →  registrado
document.fonts.size             →  20 fontes carregadas
<img> naturalWidth              →  2052 e 1000 (imagens decodificadas, não quebradas)
<crop-map> svg path             →  179 caminhos desenhados
```

Três telas percorridas — Visão Geral, Radar de Atenção e EAME. O mapa da camada EAME
desenha Espanha, França e Itália com geometria real.

### Refresh direto não quebra

O pacote **não usa `pushState`, `replaceState`, `popstate` nem `location.pathname`** —
verificado por varredura nos três arquivos. A navegação entre as nove telas é estado em
memória, não URL. Toda visita e todo F5 caem em `/`, que é `index.html`.
**Não é preciso regra de rewrite**, e nenhuma foi adicionada.

Consequência a registrar: `/radar`, `/eame` etc. **não existem como URL** e devolvem 404
na Vercel. Isso é o comportamento correto do casco de hoje, não um defeito do deploy.

---

## 6 · DOIS ERROS DE CONSOLE — E DE QUEM SÃO

O Preview registra, a cada carga, dois erros:

```
Uncaught SyntaxError: Unexpected token '<'   (x2)
```

Não os deixei sem dono. Fiz o A/B:

```
casco empacotado (SINTONIA-EAME-V8-FINAL.html), servido inteiro ......  0 erros
export de deploy, como está ..........................................  2 erros
export de deploy, cópia descartável sem <script src="_ds/…_ds_bundle.js">  0 erros
```

**São do `_ds_bundle.js` — o bundle do design system da ADAMA que veio no export.** Não
são do casco, não são do `support.js` e não são do build.

São **não fatais**: com eles presentes, as fontes carregam, os tokens aplicam, as imagens
decodificam, o mapa desenha e as três telas navegam. A cópia sem o script foi um
diagnóstico descartável em `C:\temp\diag`, **jamais commitada** — o export vai íntegro
para o Preview, com o script no lugar.

Fica registrado para quem cuidar do design system. Não bloqueia o Preview.

---

## 7 · DEPENDÊNCIA DE REDE QUE O EXPORT TEM E O EMPACOTADO NÃO TINHA

Diferente do casco empacotado (que traz React embutido), **o export busca em CDN, em
tempo de execução**:

```
unpkg.com/react@18.3.1/umd/react.production.min.js
unpkg.com/react-dom@18.3.1/umd/react-dom.production.min.js
unpkg.com/d3@7.9.0/dist/d3.min.js
unpkg.com/topojson-client@3.1.0/dist/topojson-client.min.js
cdn.jsdelivr.net/npm/world-atlas@2.0.2/countries-110m.json
```

Todos responderam 200 no teste. **Mas isso significa que o Preview não abre sem internet
aberta para `unpkg.com` e `cdn.jsdelivr.net`** — se a rede de quem for revisar bloquear
esses domínios, a página fica em branco. Não é problema do deploy; é uma propriedade do
export, e precisa estar escrita antes de alguém abrir o link e concluir que "quebrou".

---

## 8 · SEGREDO: NENHUM, AGORA E DEPOIS

Varredura nos três arquivos servidos, procurando
`service_role`, `SUPABASE_*`, `sk-…`, `apify_api_…`, `ghp_…`, JWT (`eyJhbGciOi…`):

```
NENHUMA OCORRÊNCIA
```

Também não há caminho de Windows (`C:\…`), nem `file:///`, nem `localhost:` fixo.

```
NO_FRONTEND_SECRET = PASS       REQUIRED_ENV_VARS_NOW = nenhuma
```

### Variáveis de ambiente — documentadas para depois, NÃO configuradas agora

| variável | quando | onde pode aparecer | risco |
|---|---|---|---|
| `NEXT_PUBLIC_SUPABASE_URL` (ou `VITE_`/`PUBLIC_`) | só no wiring | frontend | público por natureza; ainda assim, só depois da RLS pronta |
| `SUPABASE_ANON_KEY` | só no wiring | frontend | público **por desenho**, e só seguro se a RLS estiver implementada — hoje ela está **desenhada, não implementada** |
| `SUPABASE_SERVICE_ROLE_KEY` | só no backend | **NUNCA no frontend** | ignora toda a RLS |

> ⛔ **`SUPABASE_SERVICE_ROLE_KEY` não pode ir ao frontend, agora nem depois.** Ele passa
> por cima de toda política de linha. Em Preview da Vercel, qualquer variável com prefixo
> público é embutida no JavaScript entregue ao navegador — ou seja, fica legível para
> quem abrir o link. Chave de serviço só em ambiente de servidor, e só quando houver
> servidor.

Nesta rodada **nenhuma variável foi criada**. O Preview sobe com o painel de env vazio.

---

## 9 · CONFIGURAÇÃO DA VERCEL

```
VERCEL_PROJECT_EXPECTED = sintonia-eame-preview
GIT_BRANCH              = claude/eame-final-product-arbitration   (Preview, nunca Production)

ROOT_DIRECTORY   = casco/canonical/deploy-v8-closeout
BUILD_COMMAND    = npm run build
OUTPUT_DIRECTORY = public
INSTALL_COMMAND  = (padrão; não há dependências)
FRAMEWORK_PRESET = Other
NODE_VERSION     = 22.x

REQUIRED_ENV_VARS_NOW   = nenhuma
REQUIRED_ENV_VARS_LATER = NEXT_PUBLIC_SUPABASE_URL · SUPABASE_ANON_KEY (frontend, só após RLS)
                          SUPABASE_SERVICE_ROLE_KEY (backend apenas — NUNCA frontend)
```

`vercel.json` **não foi tocado** — continua com os 23 bytes e o SHA da testemunha
(`{"cleanUrls": true}`). Por isso `BUILD_COMMAND` e `OUTPUT_DIRECTORY` vão no painel da
Vercel, e não no arquivo: mexer nele quebraria a prova de integridade do export por uma
conveniência de configuração.

⚠️ Deixe **desligado** "Include source files outside of the Root Directory". Todo o
necessário está dentro de `deploy-v8-closeout/`.

---

## 10 · SAÍDA

```
VERCEL_PREVIEW_READY = YES
LOCAL_BUILD_PASS     = YES

CASCO_RECEPTOR_READY  = YES     (inalterado — medido em V8-RECEPTOR-CLOSEOUT.md)
DESIGN_PATCH_REQUIRED = NO
SEGUNDA_COPIA_DO_CASCO = NO

SUPABASE_CONNECTED = NO
REAL_DATA_WIRED    = NO
PRODUCTION_DEPLOY  = NO
MAIN_MERGED        = NO

INDEX_ABRE            = YES
SUPPORT_JS_CARREGA    = YES
CROP_MAP_JS_CARREGA    = YES
ASSETS_CARREGAM       = YES   (27/27)
REFRESH_DIRETO_QUEBRA = NO
PATH_LOCAL_WINDOWS    = NENHUM
NO_FRONTEND_SECRET    = PASS

CASCO_SHA_MATCH = YES
SHA256_INDEX    = d28f6b5876e2fa28720eb555a8b99a275e56c229ed0ac5c4b07edf89f4e81328
```

### `EXACT_BLOCKERS`

```
nenhum para o Preview.
```

### O que NÃO é bloqueador, mas precisa estar escrito

```
1  _ds_bundle.js lança 2 SyntaxError por carga — do design system, não do casco,
   não fatal (seção 6)

2  o export depende de unpkg.com e cdn.jsdelivr.net em tempo de execução; rede que
   bloqueie esses domínios mostra página em branco (seção 7)

3  /radar, /eame etc. devolvem 404 — o casco não usa URL para navegar (seção 5)

4  os cinco itens da seção 10 do CLOSEOUT continuam abertos, e todos são do wiring,
   não do Preview
```
