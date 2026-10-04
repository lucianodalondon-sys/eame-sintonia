# RELATÓRIO — MISSÃO 6-PREP-d · AS RECEITAS DAS FONTES

Branch `receitas-fontes-v1`, a partir de `82d31091`. Motor: `claude-opus-5-5`.

```
PROPOSTA — NÃO APLICADA. Aplicação depois da unificação (M5), pelo coordenador, com o dono.
italy_contracts_curator.json · admissao/ · retrato_html.py · limiares · fila · livros = INTOCADOS
COLLECTION NÃO CORREU · NADA NA SALA · DB_WRITES = 0
```

---

## 0 — DE ONDE VEM CADA NÚMERO

* **Livro vivo lido por cópia**: `source-curator-service-v1` @ `9a82197c`,
  copiado às 02:51Z para `%TEMP%\curator-snap-20260923T025125Z\`
  (`italy_contracts_curator.json` sha256 `03eaba59…`,
  `LIFECYCLE-LEDGER-V1.json` `c3888c0b…`). O vivo nunca foi lido directamente.
* **As 45.** O `ABASTECIMENTO-PROOF-V1.json` da 2b guarda só a **contagem**
  (`EMPTY_LIST_padrao_do_contrato_nao_casa: 45`), não a lista. Isolei-as no livro
  vivo pela janela da prova (00:23:20Z–01:02Z): transições para
  `CONTRACTED_CANARY_FAILED` com a razão «nenhum dos N endereços da entrada
  casa…». **Deu exactamente 45.** No livro inteiro há **203** fontes paradas
  pelo mesmo motivo — as 45 são as que caíram nele dentro da revivificação.
* ⚠️ **Não existe estado `CONTRATO_INVALIDO`** no livro vivo; o nome do briefing
  corresponde a este motivo. Não o adivinhei: medi-o e bateu 45/45.

---

## 1 — CENSO

```
COORTE = 121 fontes (dedup)  =  14 micro  ∪  45 EMPTY_LIST  ∪  85 do gabarito
         (sobreposições: 9 micro∩gabarito, 14 das 45 ∩ gabarito)
```

Páginas lidas: as 146 do gabarito da 6-PREP-c e mais **32 páginas novas de 21
sites** (as fontes sem página), com veredito meu, humano-proposto
(`scripts/receitas/ROTULOS-PAGINAS-RECEITAS-V1.json`).

### DEFEITOS por tipo (várias por fonte; `scripts/receitas/censo_e_proposta.py`)

| defeito | 121 | micro (14) | as 45 | gabarito (85) |
|---|---|---|---|---|
| **PADRAO_NAO_CASA_NADA** — não casa nenhum link da própria página de entrada | **61** | 0 | **26** | 49 |
| **PADRAO_NAO_CASA_MATERIA** — não casa a matéria confirmada | **31** | 5 | 9 | 24 |
| **INDEX_APONTA_MATERIA** | 3 | 0 | 0 | 3 |
| **PADRAO_GENERICO** — casa navegação da entrada | 2 | 1 | 0 | 2 |
| SEM_CONTRATO no livro vivo | 3 | 1 | 0 | 3 |
| NAO_SEI_SEM_PAGINA | 16 | 2 | 14 | 0 |
| SEM_DEFEITO_MEDIDO | 27 | 5 | 5 | 21 |

Leituras:

* O **EMPTY_LIST do bot reproduz-se sem rede** em 26 das 45: o padrão não casa
  nada na página de entrada que eu li. 14 das 45 ficam sem página (domínio
  partilhado com outra fonte — o teto de 3 pedidos por site não deixa abrir
  cada `INDEX_URL`).
* ⚠️ **5 das 45 não mostram defeito** na página que eu li. O bot leu a entrada
  noutra hora; o que ele viu e o que eu vi podem ser páginas diferentes. Não
  resolvo a divergência: declaro-a.
* Os 2 PADRAO_GENERICO: `IT-T10-018` casa `…/news/category/ecommerce-e-delivery`;
  `IT-T7-047` casa `…/news/settore-comunicazione-contatti/`.
* SEM_CONTRATO: `IT-T5-041`, `IT-T9-015`, `IT-T9-019` — as duas T9 têm contrato
  na minha linha e não no livro vivo.

---

## 2 — AS PROPOSTAS (`curadoria/PROPOSTA-RECEITAS-V1.json`)

**Regra escrita** (no topo do script): um padrão novo só nasce de uma **matéria
confirmada** da fonte + a **página de entrada** dela; o esqueleto da morada
(número → `\d+`, título → slug, secção constante → literal, **número nunca
literal**) tem de ter **família ≥ 2** na entrada; tem de **casar todas** as
matérias confirmadas; e passa pelo **guarda** (`e_generico`), que recusa quem
case o `INDEX_URL`, navegação sintética (`/`, `/contatti`, `/chi-siamo`,
`/category/…`, `/page/2`…), navegação da própria entrada, uma capa conhecida,
ou mais de 80 % dos links da entrada. Só se propõe onde há defeito medido.

```
PROPOSTAS    = 16 fontes · 14 LINK_PATTERN + 2 INDEX_URL — todas com prova
SEM_PROPOSTA = 105, e porquê:
               43 sem matéria lida da fonte (NÃO SEI)
               27 sem defeito medido — não se mexe no que funciona
               16 sem página nenhuma
                7 padrão derivado recusado pelo guarda (casava navegação/índice)
                6 família < 2 na entrada
                3 esqueleto não reproduzível (o padrão derivado não casava a própria matéria)
                3 sem contrato
```

### Os 14 LINK_PATTERN, cada um com a sua prova

Em **todos**: matérias confirmadas casadas **→ 1/1**, capas conhecidas casadas
**→ 0**.

| SOURCE_ID | matéria antes→depois | links da entrada casados antes→depois | padrão novo (cauda) |
|---|---|---|---|
| IT-T10-018 myfruit (GENÉRICO) | 1/1 → 1/1 | 40 → 34 /82 | `myfruit.it/news/<slug>` (deixa de casar `/news/category/…`) |
| IT-T10-022 Zootecnica | 0/1 → 1/1 | 12 → 75 /128 | `/featured/<slug>` |
| IT-T12-024 Regione Veneto | 0/1 → 1/1 | 3 → 6 /50 | `/web/agricoltura-e-foreste/dettaglio-news?articleId=<n>` |
| IT-T12-039 Bandi Lombardia | 0/1 → 1/1 | 0 → 3 /34 | `/servizi/servizio/comunicazioni/dettaglio/<slug>` |
| IT-T12-057 Generazione Lombardia | 0/1 → 1/1 | 10 → 4 /54 | `/announcements/announcements/view?id=<n>` |
| IT-T12-074 Open Innovation | 0/1 → 1/1 | 7 → 3 /83 | `/it/collaborations/collaboration-proposals/view?id=<n>` |
| IT-T12-117 Calabria Energia | 0/1 → 1/1 | 0 → 2 /24 | `/<n>/<n>/<n>/<slug>` |
| IT-T2-038 Meteotrentino | 0/1 → 1/1 | 7 → 8 /64 | `/previsioni/<slug>` |
| IT-T2-050 Arpa Campania | 0/1 → 1/1 | 0 → 4 /67 | `/-/<slug>?redirect=…` |
| IT-T5-052 Bulletin of Insectology | 0/1 → 1/1 | 0 → 17 /29 | `/article/<n>` |
| IT-T5-053 Phytopathologia Medit. | 0/1 → 1/1 | 0 → 14 /51 | `/index.php/pm/article/view/<n>` |
| IT-T7-047 CIA (GENÉRICO) | 0/1 → 1/1 | 18 → 3 /74 | `/multimedia/video/<n>` |
| IT-T8-016 Protezione Civile Calabria | 0/1 → 1/1 | 0 → 30 /58 | `/?p=<n>` |
| IT-T9-018 FreshPlaza | 0/1 → 1/1 | 0 → 122 /211 | `/article/<n>/<slug>` |

### Os 2 INDEX_URL, provados por página buscada

Regra: a candidata foi **buscada** (`scripts/receitas/provar_indices.py`,
egresso IT, robots, 2 pedidos) e tem **≥ 10 links** com o esqueleto de uma
matéria confirmada do mesmo site.

| SOURCE_ID | antes (é matéria) | depois | prova |
|---|---|---|---|
| IT-T2-039 | `arpae.it/it/notizie/copy_of_monitoraggio-pollini…` | `https://www.arpae.it/it/notizie` | «Notizie — Arpae», 33 notícias filhas |
| IT-T12-044 | `calabriaeuropa…/calabriambiente-la-nuova-app…` | `https://calabriaeuropa.regione.calabria.it/news` | «News», 23 links com forma de notícia |
| IT-T11-010 | `…/fiera/fiera-2026` | **NÃO SEI** | «Eventi» só tem 3 links com forma de notícia (< 10) |

---

## 3 — O EFEITO, MEDIDO SEM APLICAR (`scripts/receitas/medir_efeito.py`)

Receitas antes = cópia do livro vivo; depois = as mesmas + a proposta, **em
memória**.

```
GABARITO (37 matérias · 109 capas)            ANTES      DEPOIS
matérias casadas pelo padrão da sua fonte     11/37  →  21/37
capas casadas por engano                       0/109 →   0/109
```

O detector com as receitas novas:

| juiz | capa atravessa | matéria → capa | matéria → pessoa |
|---|---|---|---|
| ACTUAL (não lê receita) | 63/109 → 63/109 | 6/37 → 6/37 | 8/37 → 8/37 |
| V1 — índice exacto = capa | 20/109 → 20/109 | **9/37 → 7/37** | 6/37 → 7/37 |
| «morada antes do formato» (rejeitada na 6-PREP-c) | 4/109 → 4/109 | 25/37 → **15/37** | 3/37 → 9/37 |

⚠️ Com os contratos do **livro vivo**, os «antes» da V1 e da morada diferem dos
da 6-PREP-c (13 e 0 capas a atravessar), que usou os contratos da **minha**
linha. Mesma página, receita diferente — são dois livros. A leitura não muda:
**mesmo com as receitas corrigidas, a «morada antes do formato» barra 15/37
matérias. Continua a não se aplicar.**

### As 14 da micro

```
RECEITA PROVADA (casa matéria confirmada e nenhuma capa)   3/14 → 6/14
                ganhas: IT-T10-022, IT-T12-057, IT-T12-074
MICRO_PRONTAS_SE_APLICADA                                  1/14 → 1/14
```

**Nenhuma fonte fica pronta a mais.** As 3 ganhas estão todas `FICA_FORA` na
relevância da 3b (inglês; portal de juventude; open innovation). O que prende
a micro não é a receita: é a relevância e as receitas de coleta T12/T9.

---

## 4 — CONTROLO: PADRÃO GENÉRICO RECUSADO

`tests/test_receitas_proposta.py` — **9 provas, verdes**, sem rede:

* `.*` e `^https?://host/.*$` recusados; padrão que casa o índice, a navegação
  ou uma capa conhecida recusado; padrão que não compila recusado; padrão
  estreito aceite;
* cada padrão publicado na proposta passa o guarda, casa as suas matérias e
  zero capas; o ficheiro diz «NÃO APLICADA».

Mutantes (cada um tem de pôr uma prova a vermelho):

```
o guarda aceita tudo           → 4 vermelhos
número vira literal no padrão  → 1 vermelho
GENERICO_RECUSADO = YES
```

---

## 5 — REDE

```
EGRESS = IT em 24/24 idas desta missão (149.22.91.172 Palermo): 21 sites + 3 índices candidatos
         0 BR · máx. 3 pedidos por site · robots da casa
         paragens: 7 sem link com forma de matéria · 1 robots nega · 1 URL com caracteres de controlo
bytes    ~/receitas-paginas/ (fora do Git, da Sala e do armazém), sha256 no MANIFESTO
```

---

## 6 — LIMITES, DECLARADOS

* Cada prova de padrão assenta em **1 matéria confirmada** por fonte e na
  família da página de entrada (≥ 2). É prova mínima; os `EXEMPLOS_DEPOIS` de
  cada proposta estão no ficheiro para quem quiser ler mais.
* 105 de 121 fontes ficam sem proposta. É a regra a funcionar, não a falhar:
  nenhum padrão nasce sem uma matéria lida (trava 3 do dono).
* Várias T12 medidas são portais regionais **fora do tema** (impostos,
  turismo, bibliotecas, PNRR). Aí o defeito é a **fonte**, não a receita:
  corrigir o padrão faria uma rota certa para o sítio errado. Registo, não
  corrijo (decisão D5 do dono).
* Vereditos de página humano-propostos por mim; precisam de visto.

---

## ENTREGA

```
COORTE            = 121 (dedup: 14 micro ∪ 45 EMPTY_LIST ∪ 85 gabarito)
DEFEITOS          = NAO_CASA_NADA 61 · NAO_CASA_MATERIA 31 · INDEX_APONTA_MATERIA 3 ·
                    GENERICO 2 · SEM_CONTRATO 3 · SEM_PAGINA 16 · SEM_DEFEITO 27
PROPOSTAS         = 16 com prova (14 LINK_PATTERN · 2 INDEX_URL)
SEM_PROPOSTA      = 105 (43 sem matéria lida · 27 sem defeito · 16 sem página · 7 guarda ·
                    6 família < 2 · 3 esqueleto · 3 sem contrato)
EFEITO_GABARITO   = matérias casadas 11/37 → 21/37 · capas casadas por engano 0/109 → 0/109
MICRO_PRONTAS_SE_APLICADA = 1/14 (receitas provadas 3 → 6; as 3 ganhas estão FICA_FORA na 3b)
GENERICO_RECUSADO = YES (9 provas; mutantes «guarda aceita tudo» e «número literal» mortos)
EGRESS            = IT 24/24
```

---

## EM PALAVRAS SIMPLES

Cada fonte tem uma **receita**: onde fica a página de entrada, e como é o
endereço de uma notícia. O coletor usa a receita para saber o que apanhar.

Fui ver as receitas de 121 fontes. Em **61**, a receita não reconhece **nenhum**
link da própria página de entrada — é como mandar alguém buscar "caixas
azuis" num armazém onde todas as caixas são verdes. Volta de mãos vazias, e o
sistema anota "lista vazia". Isso explica as 45 fontes que o robô reviveu e
que voltaram a parar.

Porquê? A maioria das receitas foi escrita **em série, pelo mesmo molde**, sem
nunca olhar para o site.

Escrevi **16 receitas novas**, e cada uma só nasceu depois de eu ler uma
notícia verdadeira daquele site. Com elas, o número de notícias que a receita
reconhece no meu gabarito sobe de **11 para 21 (em 37)**, e o número de páginas
vazias que ela deixa passar fica em **zero**. Para as outras 105, não inventei:
ficaram "não sei".

Mas atenção: **isto não põe mais nenhuma fonte pronta para a micro-coleta.**
As 3 que ganham receita estão fora pelo tema. A porta certa para uma casa
onde não há nada que nos interesse continua a não servir.

Nada foi aplicado. É proposta, com prova, para depois da unificação.
