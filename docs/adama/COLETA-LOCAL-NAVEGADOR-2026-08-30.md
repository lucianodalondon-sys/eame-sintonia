# Coleta ADAMA España pelo navegador local — 2026-08-30

Captura das páginas: **2026-08-30T03:19:24Z**
Captura dos documentos: **2026-08-30T03:35Z–04:05Z**
Branch: `claude/adama-es-local-browser`

---

## 1 · O que estava travado, e o que destravou

A borda da ADAMA (Akamai) recusa cliente HTTP que não seja navegador. Isso já era
conhecido do datacenter. O que esta execução mediu de novo é que **não é questão de
IP**: rodando na máquina do usuário, na rede doméstica dele, o `curl` **continua**
levando 403.

```
curl -A "Mozilla/5.0 ... Chrome/139" https://www.adama.com/spain/es/nuestras-soluciones
→ HTTP 403, 143 bytes
```

O navegador da mesma máquina abre a mesma URL normalmente. Então o navegador virou o
cliente HTTP: ele busca (`fetch` de mesma origem, com a autorização que a Akamai já deu
à aba), empacota em JSON e grava em disco. O Python continua fazendo tudo o mais —
parser, vocabulário, anti-cartesiano, crosswalk, testes.

Isso **não é cache**. Cada página no pacote carrega o status HTTP real e a hora da
captura, e `buscar()` devolve falha para o que não veio 200.

### Rotas que NÃO funcionaram, e por quê

| tentativa | resultado |
|---|---|
| `curl` da rede doméstica | 403 em todas as rotas, inclusive `robots.txt` |
| ponte HTTP local (`fetch` da página → `127.0.0.1`) | `ERR_BLOCKED_BY_CLIENT` — o sandbox do navegador não deixa a página falar com a rede local. Não insisti: é a intenção do sandbox. |
| Chrome do usuário via extensão | extensão não pareada com o app; quatro tentativas, `list_connected_browsers` sempre vazio |
| `/spain/es/products/crop-protection/downloads` | devolve só o desafio da Akamai (≈3 KB, meta refresh), do datacenter **e** do navegador local |

### A URL do briefing estava errada

O briefing aponta `/spain/es/products/crop-protection/...`. Essa família **não existe**
como página aberta neste site. O catálogo vivo é:

```
https://www.adama.com/spain/es/nuestras-soluciones?items_per_page=All
```

`items_per_page=All` é parâmetro do próprio Drupal da ADAMA e derruba a paginação de
24 em 24. Sem ele, três páginas; com ele, a lista inteira numa carga só.

---

## 2 · Censo

| | |
|---|---|
| `CURRENT_CATALOG_TOTAL` | **56** |
| `CURRENT_CATALOG_ENUMERATED` | 56 |
| `ENUMERATION_COMPLETE` | YES |
| duplicatas | 0 |
| páginas com falha | 0 |

Por categoria — e as duas contagens batem, o que é a checagem que importa: a contagem
de âncoras no catálogo e a categoria derivada da URL de cada ficha dão o mesmo número.

| categoria | catálogo | fichas |
|---|---|---|
| Control de Malas Hierbas | 31 | 31 |
| Control de Enfermedades | 16 | 16 |
| Control de Plagas | 8 | 8 |
| Mejora de Cultivos | 1 | 1 |

### O que NÃO entrou no censo

- **o relato externo de 55.** Não é observação desta coleta.
- **o snapshot antigo de 58.** Página cacheada não fecha denominador atual.
- **`Descargar documentos`.** O catálogo linka essa página e a regex antiga a contava
  como produto — inflava o denominador em 1. Ela existe, é linkada, e não abre.

O delta contra o relato externo de 55 é **+1 herbicida** (30 → 31). As outras três
categorias são idênticas. Não afirmo qual produto entrou: comparar contra um relato de
terceiro que não tem lista nominal não sustenta essa afirmação.

---

## 3 · Documentos

| | |
|---|---|
| descobertos | 147 |
| baixados | **138** |
| falhos | 9 |
| bytes | 295.911.775 |
| sha256 distintos | 138 (nenhum conteúdo repetido) |
| todos com magic `%PDF` e mime `application/pdf` | sim |

Por tipo: 55 rótulo comercial · 55 FDS · 23 folheto/díptico · 9 ficha de registro ·
5 outro documento técnico.

**Os 9 falhos são links podres da ADAMA**, não ausência de documento: a ficha aponta
para PDFs do MAPA em URLs que hoje devolvem 404 (`mapa.gob.es`, `mapama.gob.es` e
`magrama.gob.es` — dois desses domínios nem resolvem mais). Isso está registrado como
`DOWNLOAD_STATE=FAILED` com o código, nunca como zero.

### Onde os PDFs estão

**No disco local**, em `data/raw/ES/adama-website/documentos/` — que é `.gitignore`.
Não há credencial do Supabase nesta máquina, e a seção 14 proíbe procurar segredo.
Para o Git foi o manifesto: `data/samples/ADAMA-ES-DOCUMENTOS-MANIFEST.csv`, com
`SHA256`, `BYTES`, `MEDIA_TYPE`, `URL`, `SOURCE_PAGE` e `STORAGE_KEY` de cada um.

> **Pendência para quem tiver a credencial:** subir os 138 arquivos para
> `raw/ES/adama-website/<PRODUCT_ID>/<sha16>-<filename>` e carimbar o `STORAGE_KEY` no
> manifesto. Os arquivos estão íntegros e conferíveis pelo hash.

---

## 4 · Inteligência extraída

| estrutura | linhas |
|---|---|
| PRODUCTS | 56 |
| DOCUMENTS | 147 |
| CROP_RELATIONS | 717 (594 declaradas + 123 só citadas) |
| ISSUE_RELATIONS | 184 |
| CROP_ISSUE_RELATIONS | **5** |
| CROP_DOSE_RELATIONS | 26 |
| APPLICATION_WINDOWS | 3 |
| ACTIVE_INGREDIENTS | 78 |
| MODES_OF_ACTION | 22 (HRAC/FRAC/IRAC) |
| CLAIMS | 35 (29 técnicos · 5 declarações regulatórias · 1 comercial) |
| TECHNOLOGIES | 1 |
| PRODUCT_RELATIONS | 1 |
| VIDEOS | 3 (YouTube) |
| RELATED_CONTENT | 0 |

### Por que só 5 pares cultivo × problema

Porque a ADAMA España **quase não publica tabela cultivo × problema em HTML**. Das 56
fichas, 14 têm tabela, e o formato dominante é `CULTIVO × DOSIS` — sem coluna de agente.
Cruzar o cultivo dessa tabela com os agentes citados noutro ponto da página seria
produto cartesiano, e a seção 8 proíbe. Então essas linhas saem numa estrutura própria,
`CROP_DOSE_RELATIONS`, com `PAIR_DERIVABLE=false` e o motivo escrito em cada linha.

**Onde o par provavelmente está:** dentro dos 55 rótulos comerciais em PDF, que já estão
baixados. Ler PDF não estava nesta missão.

### Tecnologia e relação entre produtos: 1 cada, e o motivo de serem tão poucas

A única marca de tecnologia que a ADAMA marca com ® nas fichas é **FullPage®**, na do
POSTSCRIPT 80 ("híbridos de arroz FullPage®"). **Asorbital®** aparece na home, mas em
nenhuma das 56 fichas de produto.

A ficha do ANIBAL cita **HERBOLEX®**, que é outro produto do catálogo — isso é relação
entre produtos publicada pela ADAMA. O tipo fica como `MENTIONED_ON_PAGE` e não como
"complemento" ou "programa": a página cita a marca sem dizer qual é a relação, e nomear
o tipo seria inferir.

A separação entre os dois só é possível depois de ler o catálogo inteiro — é o que diz
se o nome marcado é produto ou plataforma.

### RELATED_CONTENT é 0 por ausência da fonte

Varri as 56 fichas: a única ocorrência de "relacionad*" é **"Documentos relacionados"**.
O site não publica conteúdo associado (artigo, webinar, field day, campanha) na página
de produto. Zero aqui é medida, não falha — e a seção 21 proíbe inferir relação só
porque dois produtos compartilham molécula.

---

## 5 · Crosswalk MAPA

| estado | antes | depois |
|---|---|---|
| MATCHED_EXACT | 20 | **41** |
| MATCHED_WITH_EVIDENCE | 14 | 2 |
| AMBIGUOUS | 7 | **1** |
| ADAMA_SITE_ONLY | 15 | 12 |
| ROPF_ONLY | 55 | 52 |

O salto não é do portfólio: é da leitura. A ADAMA escreve o registro de três formas
(`ES-01603`, `25186`, `24.887`) e o parser conhecia só a primeira — 30 das 56 fichas
saíam sem registro tendo o número publicado na página.

96 registros vigentes no ROPF e 56 entradas no catálogo **contam unidades diferentes**.
Um produto pode ter vários registros; um registro pode não ter exposição comercial. A
diferença só vira achado depois do crosswalk, nunca por subtração.

---

## 6 · Visões por cultura

| arquivo | linhas |
|---|---|
| `ADAMA-ES-MAIZE-PUBLIC-PORTFOLIO-MAP.json` | 15 produtos (12 `MAÍZ` + 3 `MAÍZ DULCE`) |
| `ADAMA-ES-OLIVE-PUBLIC-PORTFOLIO-MAP.json` | 8 produtos |
| `ADAMA-ES-WINTER_CEREALS-PUBLIC-PORTFOLIO-MAP.json` | 15 produtos (trigo 14, cevada 14, centeio 8, triticale 6) |
| `ADAMA-ES-PORTFOLIO-POR-CULTIVO.json` | 132 cultivos |
| `ADAMA-ES-PORTFOLIO-POR-ISSUE.json` | 67 problemas |

**Regra de entrada:** o produto só entra se a ficha **declara** o cultivo no bloco
"Cultivos". Cultivo apenas citado no corpo do texto fica listado à parte, em
`PRODUTOS_QUE_SO_CITAM_SEM_DECLARAR`, e nunca somado. No milho isso separa 15
declarados de 20 que só mencionam.

---

## 7 · Defeitos do coletor que só a coleta ao vivo revelou

Sete, todos meus, todos com guarda de teste novo agora:

1. **Rota do catálogo inexistente** — apontava para `/products/crop-protection/downloads`.
2. **Categoria vinda do menu** — o menu lista as quatro categorias em toda página, e o
   parser varria os links em ordem de DOM: as 56 fichas saíam como fungicida.
3. **Documento sem extensão na URL** — a ADAMA serve por `/media/<id>/download`, com o
   nome do arquivo no atributo `title`. Zero documentos eram vistos em 56 fichas.
4. **Dose descartada** — linha `CULTIVO × DOSE` era jogada fora por falta de agente.
5. **Unidade da dose no cabeçalho** — a célula traz só `2,5`; a unidade está em
   `DOSIS (L/Ha)`, uma linha acima. E a ADAMA parte uma tabela lógica em vários
   `<table>`, só o primeiro com cabeçalho (7 doses → 26 com a herança).
6. **Concentração em g/l** — a regex só conhecia `%`. COLTRANE saía sem nenhum
   ingrediente ativo tendo `Dicamba 120 g/l + Mesotriona 50 g/l` escrito na página.
7. **Registro em três grafias** — descrito na seção 5.

E um erro meu de correção: ao limpar o título vazado do bloco "Cultivos" eu descartava
todo texto que fosse nome de seção — mas "Trigo" também titula outro bloco na ficha do
AVASTEL, e o trigo real ia junto. Agora descarta exatamente um item do fim.

---

## 8 · Verificação

- **Guardas:** 36 no `test_adama_es.py`, 0 falha. Eram 28; os 8 novos guardam
  exatamente os defeitos acima.
- **Demais suítes:** 149 testes (`portao` 40, `operacao` 37, `coleta_externa` 29,
  `pipeline` 18, `evidence` 16, `canonico` 9), todas OK.
- **Verificação manual 5/5** (§24), ficha viva contra saída do parser: KAMPAI
  (herbicida), AVASTEL (fungicida), COSAYR (inseticida), BREVIS (mejora de cultivos),
  COLTRANE (milho). Duas discrepâncias encontradas nessa conferência viraram os
  defeitos 6 e 7.

---

## 9 · O que esta coleta NÃO prova

Estoque · venda · distribuição · market share · receita · prioridade interna da ADAMA.

Presença em catálogo público é presença em catálogo público. `CURRENT_COMMERCIAL_
AVAILABILITY` é `NAO_SEI` para os 56, e continua sendo.

---

## 10 · Como reproduzir

```bash
python3 scripts/adama_intelligence.py --build 2026-08-30T03:19:24Z > data/samples/ADAMA-ES-PRODUCT-INTELLIGENCE.json
python3 scripts/adama_intelligence.py --manifest 2026-08-30T03:19:24Z > data/samples/ADAMA-ES-CENSO-MANIFEST.csv
python3 scripts/adama_es_visoes.py --build
python3 tests/test_adama_es.py
```

Exige os pacotes de captura em `data/raw/ES/adama-website/` (não versionados). Sem
eles, o portão devolve `SEM_CAPTURA` e o censo devolve `NOT_COLLECTED` — nunca 0.
