# CENSO ADAMA ESPAÑA — entrega

`captured_at = 2026-08-30` · branch `claude/adama-es-commercial-intelligence-rqgy44`

---

## O achado que decide a missão

O catálogo público da ADAMA España **não foi lido nesta rodada**, e o motivo é
mensurável, reprodutível e não é ausência de fonte.

```
python3 scripts/adama_es_portao.py
```

| rota | HTTP | estado |
|---|---|---|
| `/spain/es/` | 403 | EDGE_BOT_DENIED |
| `/spain/es/products/crop-protection/downloads` | 403 | EDGE_BOT_DENIED |
| `/spain/es/products` | 403 | EDGE_BOT_DENIED |
| `/robots.txt` | 403 | EDGE_BOT_DENIED |
| `/sitemap.xml` | 403 | EDGE_BOT_DENIED |

`ALCANCE = CLIENTE_NEGADO_NO_HOST_INTEIRO` · `ADAMA_ES_COLLECTION_READY = NO`

**Três coisas que este 403 não é.** Não é política de egresso desta sessão: o CONNECT
completa e o proxy não registra recusa. Não é rota inexistente: `/robots.txt` é servido a
qualquer cliente por convenção, e ele também é negado — o recusado é o **cliente**. E não
é catálogo vazio: a ADAMA continua publicando; este IP é que não é atendido.

Quem nega é a borda da própria ADAMA: `server-timing: ak_p` (Akamai Bot Manager) e o corpo
`Access Denied / Reference #`. O IP de saída (`160.79.106.135`, depois `.137` — mesmo
bloco de datacenter) é o sujeito da negação. Não existe host alternativo: das nove
variantes testadas (`adama.es`, `assets.adama.com`, `cdn.adama.com`, …) só
`www.adama.com` resolve. `web.archive.org` está barrado no relé desta sessão.

Isto **reproduz** o que a MISSÃO 09 já havia registrado (`adama.com/spain: 403`) e
**contradiz** a investigação externa de 29/08 que acessou o site normalmente — de outra
rede. As duas observações são compatíveis: a diferença é o cliente, não a data.

Consequência aplicada em todo artefato desta entrega:

> `CURRENT_CATALOG_TOTAL = NOT_COLLECTED`. Nunca `0`, nunca o `55` do relato externo,
> nunca o `58` do snapshot antigo. **Falha de acesso não é ausência.**

---

## O que foi medido ao vivo

O MAPA responde. A metade regulatória do censo foi executada de verdade.

**A tabela de ids que faltava.** `ES-ROTA-DO-PAR-CROP-ISSUE` provou que o ROPF cruza
`idCultivo × idPlaga` no servidor, e parou aí: sem os ids, a rota era descrita, não
executável. Eles estão publicados em texto aberto nos `<option>` de
`/regfiweb/Productos/Index` — **448 cultivos e 708 pragas**, exatamente o vocabulário que
o `ES-ADAMA-PORTFOLIO-ROPF` já dizia usar. Agora com chave.

→ `data/samples/ES-MAPA-VOCABULARIO-IDS.json`

**Teste de ouro, reproduzido sem consultar o artefato antigo:**

| par | registros | ADAMA |
|---|---|---|
| TRIGO × SEPTORIOSIS DEL TRIGO | 95 | 6 |
| TRIGO × ROYA AMARILLA | 42 | 5 |
| CEBADA × SEPTORIOSIS DEL TRIGO | 25 | **0** |
| OLIVO × REPILO DEL OLIVO | 180 | 2 |

Bate com o registrado pela sessão principal. O filtro discrimina — não devolve tudo.

**Milho (seção 22), metade regulatória.** 22 produtos ADAMA com registro vigente em milho;
**20 pares CROP × ISSUE confirmados um a um pelo servidor**. O varrido foi limitado aos
agentes que as próprias fichas ADAMA declaram: 708 × 4 = 2.832 perguntas para achar 20
seria descortesia com a fonte, não rigor.

→ `data/samples/ADAMA-ES-MAIZE-REGULATORY-MAP.json`

Isto **não** é o mapa público que a seção 22 pede. Registro não é comunicação: dose
comunicada, janela declarada, tecnologia própria e posicionamento vivem no site.
O artefato diz isso em campo próprio (`MAIZE_PUBLIC_POSITIONING = NOT_COLLECTED`) em vez
de deixar o leitor supor.

---

## O que foi construído e está pronto para rodar

O coletor não depende de ter visto a página: lê **estrutura**, não seletor adivinhado.

`scripts/adama_es.py`

- **par só nasce de LINHA de tabela**, com âncora reproduzível (seção, tabela, linha,
  texto). Lista solta vira `CROP_RELATION` com `PAIR_DERIVABLE: false`. Cruzar
  `[culturas] × [issues]` seria produto cartesiano — o mesmo atalho que o
  `ES-ADAMA-PORTFOLIO-ROPF` já havia recusado;
- **nove tipos de documento**, nenhum chamado "bula"; SDS classificado antes de LABEL
  porque *"ficha de datos de seguridad"* contém *"ficha"*;
- **desduplicação por SHA256** — o mesmo PDF em duas URLs é um documento com duas URLs;
- **quatro classes de claim**, e nenhuma nasce `REGULATORY_FACT`: um enunciado com número
  de registro sai como `MANUFACTURER_REGULATORY_STATEMENT` até o MAPA confirmar;
- **vocabulário só de fonte oficial** (ROPF + EPPO, ambos já no repo);
- **forma curta ambígua não é resolvida por palpite**: `repilo` encabeça 2 rótulos
  oficiais, `mildiu` mais de 20 → saem como `AMBIGUOUS` com os candidatos nomeados. Onde
  a forma curta casa exatamente um rótulo mas encabeça outros (`OÍDIO`), o par é emitido
  e **marcado** `HEAD_TERM_ALSO_AMBIGUOUS` — a relação vale, a espécie não está resolvida.

`tests/test_adama_es.py` — **28 testes adversariais**, um por erro que a seção 26 nomeia.
Passam. Nenhum teste existente do repo regrediu.

`.github/workflows/adama-es-censo.yml` — a mesma rota de outro IP. Se a borda atender o
runner, o censo roda inteiro sem mudar uma linha. Se negar, duas negações de IPs distintos
são evidência mais forte do que uma.

---

## Entrega (seção 33)

**A · CENSO** — `CATALOG_TIMESTAMP` 2026-08-30 · `CURRENT_CATALOG_TOTAL` **NOT_COLLECTED**
· `CURRENT_CATALOG_ENUMERATED` NOT_COLLECTED · `ENUMERATION_COMPLETE` **NO**

**B · PÁGINAS** — encontradas / parseadas / falhas: NOT_COLLECTED (acesso negado antes da
enumeração)

**C · DOCUMENTOS** — todos NOT_COLLECTED. Descobrir documento exige a página.

**D · STORAGE** — `STORAGE_OBJECTS = 0`, `ORPHANS = 0`. Nada foi baixado, logo nada a
preservar. Nenhum PDF entrou no Git.

**E · INTELIGÊNCIA** — todas as contagens de site NOT_COLLECTED. Estruturas existem e
estão vazias **com motivo**, não com zero.

**F · MAPA** — `ROPF_ACTIVE_REFERENCE = 96` · `MATCHED = 0` · `AMBIGUOUS = 0` ·
`ADAMA_SITE_ONLY = 0` · `ROPF_ONLY = NOT_TESTABLE_WITHOUT_CATALOG` (**não 96**)

> `ROPF_ONLY` afirma "está no MAPA e **não** está no catálogo". Isso exige ter lido o
> catálogo. Sem leitura, os 96 estão em `NOT_TESTABLE_WITHOUT_CATALOG` — ignorância
> medida, não achado. E `96 − 55` continua sem sentido: unidades diferentes (seção 23).

**G · MILHO** — `MAIZE_PRODUCTS = 22` · `MAIZE_CROP_ISSUE_RELATIONS = 20` (regulatórios,
confirmados) · `MAIZE_PUBLIC_POSITIONING` / `MAIZE_TECHNOLOGIES` = NOT_COLLECTED

**H · QUALIDADE** — `STALE_CACHE_EXCLUDED = SIM` (55 e 58 recusados) · duplicados,
cartesianos, erros de tipo e de classificação: `0` sobre o que foi processado, com 28
testes a impedir a reintrodução.

**I · GIT** — branch `claude/adama-es-commercial-intelligence-rqgy44`, partindo do HEAD
remoto mais recente de `claude/sintonia-eame-collection-es`. Sem merge. Sem PDF.

**J · ESTADO**

```
ADAMA_ES_PUBLIC_CATALOG_COMPLETE      = NO
ADAMA_ES_PUBLIC_DOCUMENTS_COMPLETE    = NO
ADAMA_ES_PRODUCT_INTELLIGENCE_COMPLETE= NO (metade regulatoria: SIM)
SAFE_FOR_MAIN_SESSION_TO_CONSUME      = YES
```

Seguro porque nenhuma estrutura afirma o que não foi medido.

**BLOCKERS** — um só: `www.adama.com` nega este IP na borda (Akamai). Três saídas, em
ordem de custo: rodar o workflow (outro IP); rodar o coletor de uma rede que a ADAMA
atenda; ou pedir acesso à ADAMA. Nenhuma exige mudar o coletor.

---

## Verificação manual (seção 26)

Cinco produtos conferidos **um a um contra a ficha viva do MAPA**, não contra o artefato
do repo — registro e formulado batem em 5/5:

| produto | papel | registro | formulado |
|---|---|---|---|
| ACCRESTO | herbicida cereal | 19549 | CLODINAFOP-PROPARGIL 24% [EC] |
| AVASTEL | fungicida | ES-01818 | FLUXAPYROXAD 7,5% + PROTIOCONAZOL 15% [EC] |
| KENDO | inseticida | 24942 | LAMBDA CIHALOTRIN 10% [CS] |
| NICOPERTS | herbicida, milho | 24887 | NICOSULFURON 4% [SC] |
| COSAYR | inseticida, milho | ES-01942 | CLORANTRANILIPROL 20% [SC] |

A seção 26 pede também um *crop enhancement*. O ROPF vigente da ADAMA não expõe essa
categoria — ela é uma categoria do **catálogo comercial** (`Mejora de Cultivos`, 1 entrada
segundo o relato externo), não do registro. Verificá-la exige o site. Registrado como
pendência, não como ausência.

---

## Das 21 perguntas da seção 29

Respondidas com evidência: **5, 14, 18 (metade), 19 e 21** — pelo lado regulatório.

As demais (documentos, doses comunicadas, janelas BBCH declaradas, tecnologias próprias,
claims, complementaridade, programas de cultura, sinais de lançamento) dependem do
catálogo. A máquina que as responde está escrita e testada; falta o acesso.

**Não foi feito** (fora de escopo por desenho): França, Itália, pesquisadores, social,
Apify, RAIF, matriz nacional, portal, UI, migration, merge.
