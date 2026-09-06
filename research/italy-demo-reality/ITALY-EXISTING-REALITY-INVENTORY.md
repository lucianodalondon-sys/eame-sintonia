# Inventário do que o Sintonia JÁ tinha, antes desta pesquisa — Itália

> **LEITOR — este documento fala dos 90 pares, que NÃO são o leitor canônico da casa.**
> O leitor canônico é `IT-ROTULOS-PARES-V3` (`data/samples/IT-ROTULOS-V1/`), de 2026-09-04:
> `it_rotulo_parser/3.4.0`, portão `IT-ROTULOS-PORTAO-V1 = PASS` contra gabarito de 30
> rótulos lido à mão, **128 rótulos com par** contra os 19 daqui. Os 90 pares de 2026-08-30
> ficam como `LEGACY_READER / HISTORICAL_INPUT`, `CANONICAL_AUTHORITY = NO`.
> `OLDER_SMALLER_READER != CANONICAL_READER`.


**Data da varredura:** 2026-09-01
**Escopo:** todas as 19 branches remotas do repositório `lucianodalondon-sys/eame-sintonia`, mais os arquivos
não versionados da árvore de trabalho local.
**Método:** união dos 439 arquivos distintos sob `data/` em todas as branches (versão de maior tamanho de
cada caminho), materializada em pasta de leitura fora do controle de versão. Nenhuma branch trocada,
nenhum merge, nenhuma coleta paga, nenhuma escrita em `data/`.
**Contagens:** medidas registro por registro, nunca estimadas. O JSON irmão
(`ITALY-EXISTING-REALITY-INVENTORY.json`) traz o detalhe por corte.

---

## 0 · Banco de dados / Supabase

**NOT ACCESSIBLE IN THIS SESSION.**

O projeto tem uma camada Supabase real: 16 migrações (`supabase/migrations/001` a `016`), importações
(`ADAMA-ES-CATALOGO-2026-08-30.sql`, 1,08 MB), consultas, ensaios e 11 artefatos de contrato em
`data/supabase/`. As credenciais (`SUPABASE_URL`, `SUPABASE_SECRET_KEY`, `SUPABASE_DB_URL`) existem
**apenas como GitHub Actions secrets** — foram lidas em `.github/workflows/supabase-conexao.yml`.
Nenhuma variável de ambiente correspondente existe nesta sessão e não há arquivo `.env` local.

Consequência honesta: **não sei** o que está publicado no Supabase hoje. Tudo que este inventário conta
vem de arquivos do repositório. Existe uma rota de leitura possível (disparar o workflow
`supabase-conexao.yml` pelo GitHub Actions), que **não foi executada** por ser uma ação, não uma leitura.

---

## 1 · Quadro de contagens

| Camada | Existente (EAME) | Relevante para Itália | Estado |
|---|---:|---:|---|
| Meta Ads — concorrentes | **1.340** cartões | **414** | canônico, congelado |
| Meta Ads — ADAMA própria | 7 | **5** | canônico, já limpo de páginas homônimas |
| Meta Ads — eventos | 1.421 | — | `BASELINE_ONLY` |
| Meta — páginas de anunciante | 23 | 12 | `page_id` provado |
| Vídeos YouTube | 726 | **147** | 431 do piloto de sensores + 254 ES + 41 corpus |
| Transcrições | 15 (300.008 caracteres) | **5** | legenda pública |
| Comentários | 1.190 | **265** | 601 comentaristas únicos no piloto |
| Creators mapeados | 37 | 25 | Itália: identidade e cultura majoritariamente **não provadas** |
| Posts Instagram orgânicos | 399 | **0** | todo o corpus é de creators ES/FR |
| Facebook orgânico | **0** | **0** | não existe |
| Twitter / X | **0** | **0** | não existe |
| Registros LinkedIn | 372 | **0** | painel italiano medido e reprovado |
| Podcasts | **0** | **0** | não existe como objeto próprio |
| Pesquisadores | 37 | **25** | 25 italianos com ORCID, 22 ativos desde 2024 |
| Registros científicos | 763 | 88 com `COUNTRY_OF_FACT=IT` | 582 passam nas duas portas |
| Produtos ADAMA | — | **163** vigentes | + 51 páginas no catálogo público |
| Relações de rótulo (cultura × alvo) | — | **90** pares distintos | 49 linhas de uso autorizado |
| Boletins de campo (texto integral) | — | **7** | LaMMA, ERSA FVG, Collio, Marche ×2, Umbria, AgroNotizie |
| Notícias de imprensa técnica | — | **1** | AgroNotizie 13/02/2026 |
| Eventos regulatórios de concorrente | 21.336 | — | marca + registro, **não** feiras |
| Feiras / eventos de setor | **0** | **0** | não existia |
| Candidatos a oportunidade | 3 | **3** | rotulados "convergência que merece investigação" |
| Temas de Radar do Futuro | 2 | **2** | `PROMOTED_TO_RADAR = 0` |
| Regiões italianas com fonte medida | — | **8 de 20** | |
| Fontes italianas sondadas | — | **20** | 16 verdes, 3 bloqueadas, 1 não alcançada |

---

## 2 · Onde cada coisa mora (mapa de branches)

O acervo está **espalhado**. Nenhuma branch tem tudo. Os datasets italianos e de Meta vivem em branches
diferentes da atual:

| Conjunto | Branch com a versão mais completa |
|---|---|
| `data/samples/IT-*` (casos, catálogo, fontes, origens, T1, T3, T4, T5) | `claude/adama-it-local-catalog`, `claude/sintonia-italy-pilot-b1l401` |
| `data/samples/META-EAME/*` (1.340 anúncios) | `claude/eame-meta-competitor` |
| `data/samples/CREATOR-MAP-EAME/*` e `CREATOR-CONTENT-CORPUS-EAME/*` | `claude/eame-agro-creators-map-77c4ld` |
| `data/samples/COMPETITOR-*` (foresight, eventos, crosswalk) | `claude/eame-competitor-foresight` |
| `data/samples/SENSOR-PILOT/*` (440 vídeos, 991 comentários, 15 transcrições) | **apenas na árvore local, sem commit** |
| `data/raw/IT/PROD_FTS_6_20260824.csv` (registro do Ministero, 4,6 MB) | **apenas na árvore local**, `data/raw` é ignorado pelo Git |

⚠️ **Risco operacional:** o piloto de sensores (o material humano mais rico que temos da Itália) e o CSV
do Ministero **não estão no Git**. Se esta pasta de trabalho for perdida ou a branch trocar, esse material
some. Isso não é uma opinião: `git status` mostra `data/samples/SENSOR-PILOT/` como não rastreado.

---

## 3 · Camada por camada — o que existe de verdade

### 3.1 Meta Ads — a camada mais forte do acervo para a Itália

414 cartões de anúncio que **alcançaram a Itália**, de 6 concorrentes, em 12 páginas distintas.

- **Por empresa:** BASF 127 · FMC 98 · Corteva 79 · Bayer 69 · Syngenta 30 · UPL 11
- **Por ano de início:** 2026 → 273 · 2025 → 125 · 2024 → 10 · antes → 6
- **Estado:** 27 ativos, 385 inativos, 2 não sabidos
- **Mídia:** 234 imagem, 180 vídeo
- **Produtos provados no texto:** Exirel (36), Arc (26), Spectrum (13), Cyazypyr (13), Efficon (12),
  Dagonis (10), Enervin (9), Coragen (8), EliteSea (7), Belanty (6), F500 (6), Revysol (5), Tanaris (5),
  MAXIA (5) e mais 22 nomes
- **Culturas citadas no texto:** Zea mays 67 · Vitis vinifera 42 · cereali 24 · Olea europaea 24 ·
  Citrus 15 · Solanum lycopersicum 12 · Helianthus annuus 9 · frutta 8 · ortaggi 5 · Malus domestica 5 ·
  Beta vulgaris 4 · Oryza sativa 3 · Prunus persica 2 · Triticum aestivum 1
- **Problemas citados:** insetti 37 · infestanti 26 · malattie 23 · Plasmopara viticola 16 ·
  parassiti 12 · funghi 6 · Fusarium 5 · Amaranthus 4 · Erysiphe necator 3 · Botrytis cinerea 3 ·
  Phyllosticta ampelicida 2 · Diaporthe neoviticola 2 · Ceratitis capitata 2 · Zymoseptoria tritici 1

ADAMA própria: 5 cartões que alcançaram a Itália, produtos **Cazado** (3) e **Gilboa** (2), todos inativos,
últimos de 2026.

**Lei permanente, escrita no próprio dataset:** `AD_REACHED_COUNTRY ≠ AD_TARGETED_COUNTRY`. A fonte diz
que o anúncio foi visto na Itália; **não** diz que foi dirigido à Itália. Também não publica gasto,
impressão nem público. Qualquer frase sobre investimento, share ou sucesso de campanha é invenção.

### 3.2 Vídeo, transcrição e comentário — o piloto de sensores

Coleta de 2026-08-30, 6 recortes país × cultura × problema, custo declarado de USD 1,85.

- **147 vídeos italianos** — 73 no recorte `IT-DURUM_WHEAT-FUSARIUM`, 74 em `IT-VINE-FLAVESCENCE`
- Classificação: 81 ruído, 41 sem texto suficiente, 12 promoção de evento,
  **7 interpretação técnica**, 5 marketing, **1 comunicação de pesquisa**
- 56 dos 147 têm `COUNTRY_OF_FACT = IT` provado pelo conteúdo
- **265 comentários italianos** — 159 opinião, 61 pergunta, 40 ruído,
  **3 resposta técnica**, **2 relato de campo em primeira pessoa**
- 24 comentários com `COUNTRY_OF_FACT = IT`
- **5 transcrições** de recortes italianos; a maior tem **97.710 caracteres**

A transcrição grande é a mais valiosa do acervo inteiro: **"CONTRASTO ALLA FLAVESCENZA DORATA DELLA VITE
A CHE PUNTO SIAMO"**, canal Coldiretti Emilia Romagna, convegno de 26/02/2026, publicado 10/03/2026,
310 visualizações. Detalhe em `ITALY-VIDEO-TRANSCRIPT-REALITY.md`.

⚠️ **Ressalva que muda o uso:** a legenda dessas transcrições veio em **inglês**, tradução automática do
áudio italiano. Nomes próprios chegam corrompidos ("Stefano Buon Compagni" = Stefano Boncompagni,
"Luca Casuli" = Luca Casoli). Serve para **saber que o assunto foi tratado e por quem**; **não** serve
para citação literal em italiano sem reouvir o vídeo.

### 3.3 Creators italianos — a camada mais fraca

25 candidatos italianos. Estado real:

- Handle: 16 resolvidos, 4 provavelmente errados na seed, 3 não resolvidos, 2 com presença mínima
- Cultura: **1 provada** (Leonardo Leggeri, `@evolovers`, olivo), 3 parciais, 3 atribuições erradas,
  3 não provadas, 15 não sabidas
- Aderência ao público ADAMA: 4 média, 4 baixa, 17 não sabida

O perfil dominante é **comunicador de vinho e comida** (`@italianwinelover`, `@doctor.wine`,
`@thewinekiller`, `@tastevo`, `@ilsommolier`), não técnico de campo. Chamar isso de "camada de creators
italianos do agro" seria falso.

A voz técnica italiana real que o acervo achou **não veio da camada de creators** — veio da busca de vídeo:
canais como *Viticoltura Riccardo Castaldi*, *Matej vignaiuolo in Oslavia*, *Agronotizie* e
*Coldiretti Emilia Romagna*.

### 3.4 Regulatório e portfólio ADAMA Itália — a fundação mais sólida

Fonte: Ministero della Salute, banca dati `PROD_FTS_6_20260824`, licença CC BY 4.0,
SHA-256 `8fe401895592c41e...`, 4.594.315 bytes.

- **163 produtos vigentes** do grupo ADAMA (vínculo por sede administrativa declarada)
- **163 de 163 rótulos autorizados baixados e parseados — 0 falhas (100%)**
- Categoria regulatória: **diserbante 77** · fungicida 46 · insetticida 16 ·
  diserbante-antidoto agronomico 13 · insetticida-acaricida 4 · aficida 3 ·
  molluschicida 1 · insetticida-diserbante 1 · diradante 1 · coadiuvante 1
- 49 linhas de uso autorizado, 13 com dose · **90 pares cultura × alvo distintos**

> ### ⚠️ CORREÇÃO DE 2026-09-02 — o número de cobertura estava perigoso
>
> A auditoria de integridade do par (lei portada do `pares-da-bula.py` brasileiro) mediu
> o que este inventário não tinha medido:
>
> | medida | valor |
> |---|---|
> | produtos com **ao menos 1** linha de uso lida | **19 de 163 — 11,7%** |
> | produtos com **ZERO** linha de uso | **144 de 163 — 88,3%** |
> | dos 144: têm cultura E alvo no rótulo, **sem ligação entre os dois** | 82 |
> | das 49 linhas: **não cumprem a definição da própria classe** (a classe exige dose; só 13 têm) | **36 — 73,5%** |
>
> **`LABEL_COVERAGE: 163/163 (100%)` é o número mais perigoso do arquivo.** Ele conta
> rótulo **baixado**, não uso **lido**. Ao lado dos 11,7%, ele engana.
>
> E a distância que importa, por cultura — `menciona` contra `tem linha de uso`:
> **GRAPEVINE 61 → 1**. Sessenta produtos citam videira no rótulo e um só tem a ligação lida.
>
> **A frase que o sistema tem direito de dizer sobre os 144:** *"nesta leitura do rótulo,
> não encontramos linha ligando cultura e alvo. Isso é o que a nossa coleta leu — não é o
> que o registro contém. Não sei."*
>
> **A frase que ele NÃO tem direito de dizer:** ~~"a ADAMA não tem produto para X em Y"~~.
> É o erro do Nimitz EC — 3 culturas no catálogo, 19 no registro. **Afirmar que o cliente
> não tem produto para um alvo quando ele tem é o pior erro possível deste sistema.**
>
> E um achado de método: **o verificador de gênero de um rótulo italiano é o dicionário
> EPPO espanhol.** Gêneros só italianos passam sem conferência — `Scaphoideus` não está nele.
>
> Detalhe completo em [ITALY-AUDITORIA-DO-PAR.md](ITALY-AUDITORIA-DO-PAR.md).
- Produtos por termo de cultura no rótulo: GRAPEVINE 61 · WHEAT_GENERIC 61 · TOMATO 57 ·
  SUGARBEET 48 · APPLE 48 · BARLEY 46 · POTATO 45 · MAIZE 36 · SOYBEAN 33 · SUNFLOWER 32 ·
  ALFALFA 25 · TRITICALE 25 · COMMON_WHEAT 24 · RICE 15 · DURUM_WHEAT 14 · OLIVE 12 · SORGHUM 9
- Grupos de mecanismo declarados: HRAC 1(A) 20 · HRAC B 8 · HRAC G 7 · HRAC 3(K1) 7 · IRAC 3 6 ·
  FRAC 8 5 · FRAC 3 4 · HRAC 2 4 · e mais 13 grupos
- Vencimentos: 8 já passados · 7 em 7 dias · 71 em 6 meses · 0 sem data

Catálogo público (`adama.com/italia/it`, censo de 2026-08-30): **51 páginas de produto**,
141 documentos (51 fichas de segurança, 51 etiquetas, 23 brochuras, 13 comunicações, 2 extensões de uso,
1 leaflet). 41 produtos do catálogo cruzam com registro medido; 123 registros vigentes **não** aparecem
no catálogo público.

### 3.5 Ciência e pesquisadores italianos

- **25 pesquisadores italianos** com ORCID, 22 ativos desde 2024, do corte MAIZE_MYCOTOXIN
  (208 obras percorridas, 452 autores com afiliação italiana)
- Instituições líderes: Università Cattolica del Sacro Cuore 193 · Institute of Sciences of Food
  Production (CNR) 115 · CNR 88 · University of Milan 67 · University of Turin 67 · Parma 43 · Udine 28
- Cortes **não construídos** por estrangulamento do OpenAlex (HTTP 429):
  VINE_FLAVESCENCE (135 obras), MAIZE_BORER_DIABROTICA (30), OLIVE_BACTROCERA (70), DURUM_FUSARIUM (78).
  Estado é `NOT_COLLECTED`, **não** "sem pesquisadores"
- Corpus profundo EAME: 12 identidades provadas, 763 materiais achados, 582 servindo de evidência,
  88 com `COUNTRY_OF_FACT = IT`

### 3.6 Campo e regiões

8 das 20 regiões italianas têm fonte de campo medida. Boletins com texto integral preservado:

| Fonte | Documento | Data |
|---|---|---|
| Consorzio LaMMA (Toscana / CNR) | bollettino fitosanitario Grosseto | 2026-04-23 |
| ERSA FVG | Difesa integrata colture erbacee, frumento-orzo n.07 | 2026-04-20 |
| Consorzio Collio (Enol. Dario Maurigh) | Bollettino difesa integrata vite n.06 | 2026-05-15 |
| AMAP Marche — Ancona | Notiziario produzione integrata n.615 | 2026-04-22 |
| AMAP Marche — Ancona | Notiziario produzione integrata n.616 | 2026-04-29 |
| Servizio Fitosanitario Umbria | Bollettino cereali n.04 | 2026 |
| AgroNotizie (Image Line) | "Mais e micotossine, un 2025 da dimenticare" | 2026-02-13 |

**Viés declarado e medido:** as três maiores regiões de milho (Veneto, Lombardia, Piemonte — 71,6% da
área) não têm boletim de milho medido. A cobertura de fonte não segue a área da cultura.

---

## 4 · O que NÃO existe (dito sem rodeio)

| Camada | Estado | Por quê importa |
|---|---|---|
| Twitter / X | **inexistente** | nenhuma coleta em nenhuma branch. Se a tela do demo mostrar X, é ficção |
| Facebook orgânico | **inexistente** | tudo que temos de Facebook é Meta Ads Library (publicidade paga) |
| Instagram italiano | **inexistente** | 399 posts orgânicos, todos de creators ES/FR |
| LinkedIn italiano | **medido e reprovado** | veredito próprio: `HUMAN_SENSOR_ADDS_NOTHING_IN_THIS_PANEL` |
| Podcast | **inexistente** como objeto | há webinars e convegni dentro do acervo de vídeo |
| Feiras e eventos de setor | **inexistente** antes desta pesquisa | os 21.336 "eventos" são regulatórios e de marca |
| Janela de aplicação de rótulo | **não extraída** | a coluna de época do PDF não foi reconstruída |
| Dados internos ADAMA | **fora do projeto** | estoque, venda, margem, prontidão — nunca teremos |

---

## 5 · Regras semânticas que o acervo já carrega e que não podem ser afrouxadas

1. `AD_REACHED_COUNTRY ≠ AD_TARGETED_COUNTRY`
2. `COMENTÁRIO ≠ AGRICULTOR` · `PERGUNTA ≠ RELATO DE CAMPO` · `PRIMEIRA PESSOA ≠ FATO AGRONÔMICO`
3. `CROP_TERM_PRESENT ≠ AUTHORIZED_ON_CROP`
4. `EXPIRY ≠ WITHDRAWAL` — re-registro é rotina; estado de renovação é NÃO SEI
5. `NOT_OBTAINED ≠ DOES_NOT_EXIST` — cobertura é sempre um piso
6. `HANDLE RESOLVIDO ≠ CULTURA PROVADA`
7. `FONTE HTTP 200 ≠ FONTE VIVA`
8. Menção de creator é **menção de creator**, não tendência de mercado
9. `PROMOTED_TO_RADAR = 0` na Itália — os dois temas são candidatos, não sinais promovidos

---

## 6 · Arquivos-fonte deste inventário

Contagens completas, com detalhamento por corte, empresa, cultura, problema e estado, em
[`ITALY-EXISTING-REALITY-INVENTORY.json`](ITALY-EXISTING-REALITY-INVENTORY.json).
