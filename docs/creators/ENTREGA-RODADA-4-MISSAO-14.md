# MISSÃO 14 · RODADA 4 — CROP FIT FECHADO E ENTIDADE CORRIGIDA · ENTREGA A–T

**Data:** 2026-08-30 · **Suíte:** 70 provas na missão · **novas falhas: 0**

> **A rodada em duas linhas.** O gargalo era `MISSING_CROP_PROOF`; foi atacado por
> conteúdo e caiu de 15 para 13, com **9 `ACTIVATION_READY`** e a França a entrar no mapa.
> E o resultado mais importante não foi um número: foi **descobrir que a minha primeira
> medição de cultura estava errada** e refazê-la.

---

## A · `@biocampojoyma` — a correção semântica

O dado estava certo; a **contagem** estava errada. A conta foi corretamente medida como
empresa e mesmo assim entrou numa frase minha como *"três produtores reais"*.

Novo campo `ACTIVATION_ENTITY_TYPE`, de lista fechada: `PERSON_CREATOR` · `FARM_BUSINESS`
· `FARMER_FAMILY_ACCOUNT` · `MEDIA_ACCOUNT` · `ORGANIZATION` · `OTHER`.

`@biocampojoyma` = **`FARM_BUSINESS`**. Não conta em `FARMER_CREATORS_PROVED` nem em
`PERSON_CREATORS_ACTIVATION_READY`. **Não se perdeu a conta** — passou para a lista
paralela de parceiros. Regressão travada:
`test_biocampojoyma_continua_empresa` e `test_as_duas_listas_nao_se_misturam`.

## B · OS 15 `MISSING_CROP_PROOF` — testados um a um

| resultado | n |
|---|---|
| `PROVED` | **2** |
| `PARTIAL` (menção única) | 6 |
| `NOT_PROVED` | 7 |

**E aqui está o achado da rodada.** A primeira execução devolveu **8 `PROVED`**. Ao ler o
resultado com desconfiança, seis eram **falsos positivos meus**:

```
'riz'  (arroz, FR)  casava dentro de nariz, matriz, Beatriz, horizonte
'mais' (milho, IT)  casava com o "mais" PORTUGUÊS de @ironfarmer_rc, de Évora
'serra' (estufa, IT) casava com serra de montanha
'papa'  (batata)     casava com papa / papá
'riso'  (arroz, IT)  casava com riso / sorriso
```

Era exatamente o erro que o meu próprio código **citava** do `speaker_universo`: consulta
frouxa não traz mais do mesmo, traz **outra população com cara de sucesso**. Corrigido para
casamento por **palavra inteira**, e os termos curtos ambíguos foram **removidos**, não
"melhorados" — um termo que precisa de contexto para não errar não é termo, é palpite.
**8 → 2.**

Segunda lei nova: **quem fala de uma cultura não necessariamente a produz.** Para audiência
de consumidor, mencionar tomate dez vezes prova **assunto**, não lavoura. Sai como
`CROP_TOPIC_ONLY`. Foi o que reclassificou `@urrapetito`, `@nitofrutasyverduras`,
`@lahortetadebussy` e `@laderasdelnaranco`.

E a régua **apertou**, não afrouxou: `PARTIAL` deixou de contar como `CROP_FIT_PROVED`,
porque *"falar uma vez da cultura"* está na lista fechada do que não prova. Isso **reduziu**
`ACTIVATION_READY` de 15 para 8 antes de voltar a 9 por prova legítima.

## C · ACTIVATION_READY — antes e depois

**6 → 9.** E a composição mudou de natureza, não só de tamanho.

## D · `PERSON_CREATORS_READY` = 7

| país | região | cultura | creator |
|---|---|---|---|
| **IT** | Limena, Padova | MILHO, alfafa, soja, forragem | **Davide Gomiero** `@gomierofarm` |
| **FR** | Loiret | TRIGO, colza, cevada, milho, semente de cebola | **Gilles Van Kempen** |
| **ES** | Almería | PIMENTO, hortícolas protegidas | **Germán Fernández** `@germanagrolife` |
| **ES** | Níjar, Almería | TOMATE | **AgroSamanta** `@agrosamanta_` |
| **ES** | — | OLIVO, alfarroba, hortaliças | **Marc** `@huerto_ecologico.marc` |
| **ES** | — | OLIVO, VIDE | **Fco. Fernández Barroso** `@chicurri_agro` |
| **ES** | — | VIDE | **Oliverio Rodríguez** `@oliverio_rodfer` |

## E · `FARM_BUSINESS_PARTNERS_READY` = 2

`@biocampojoyma` (Bio Campojoyma, Níjar — pimento e tomate) e `@terruzapistachos`
(Benamaurel, Granada — pistacho). **Outra relação comercial, outro contrato, outro
interlocutor.**

## F · FRANÇA — Forge e Van Kempen

**Gilles Van Kempen: `ACTIVATION_READY`.** Canal `@gillesvk` — 30 vídeos lidos, último em
**2026-08-29**, **4 vídeos/30d e 10/90d**. Os títulos confirmam a cultura por conteúdo:
*"Préparation des terres pour les semis de maïs 2026"*, *"On récolte les oignons"*.
**É o primeiro `ACTIVATION_READY` francês.**

**David Forge: continua `PROMISING`**, com pendência exata `MISSING_RECENT_ACTIVITY` — e por
um motivo que vale registar: eu havia **inferido** o canal como `youtube.com/@DavidForge`.
A fonte mostrou que ele se chama **"La Chaîne Agricole"**. O canal não foi medido porque
**a URL exata ainda não foi confirmada**, e inferir endereço de canal é o mesmo erro que
inferir handle de pessoa.

## G · HUBS OFICIAIS RESOLVIDOS

Fase gratuita antes de qualquer raspagem. 9 hubs testados:

| hub | conta | estado |
|---|---|---|
| Premios AgroInfluye | `@agroinfluye` | **RESOLVED** · descoberta liberada |
| Fieragricola | `@fieragricolavr` | **RESOLVED** · liberada |
| SIVAL Angers | `@sivalangers` | **RESOLVED** · liberada |
| EIMA International | `@eima_international` | **RESOLVED** · liberada |
| **Enovitis in Campo** | `@enovitis_` | **MENCIONADA, NÃO RESOLVIDA** |
| SITEVI | — | não resolvida · **BLOQUEADA** |
| Espoirs / Blacks Moutons | site sim, conta não | **BLOQUEADA** |
| Innov-Agri · FederUnacoma/AGIA-CIA | — | não testadas |

**O caso Enovitis merece ser lido inteiro**, porque é o portão a funcionar como devia: a
conta estava bloqueada por falta de fonte; a conta oficial da **Fieragricola mencionou
`@enovitis_` nas próprias legendas** — uma porta provada abriu a outra, sem adivinhação.
**Mas a raspagem de `@enovitis_` não devolveu perfil.** A menção deu um **candidato de
handle**; a resolução não o confirmou. Continua bloqueada.

## H · RENDIMENTO ITALIANO

`@fieragricolavr` **13** menções · `@eima_international` **4**. Mas o que elas mencionam é o
achado:

> **Prémios mencionam PESSOAS. Feiras mencionam EMPRESAS.**
> A Fieragricola menciona `@veronafierespa` (a operadora), `@pasimat`, `@cet.electronics`,
> `@agrobit_srl`. O AgroInfluye menciona 23 creators.

Da EIMA saiu **um** creator conhecido — `@the_roman_farmer`. **Rendimento de creators por
feira: baixo.** Isso responde à pergunta do §8 sem precisar de mais gasto: o Enovitis é um
hub técnico excelente e, pelo padrão medido nas feiras irmãs, **provavelmente um hub de
creators fraco**.

## I · RENDIMENTO FRANCÊS

**`@sivalangers`: ZERO pessoas** em 12 publicações. Conta pequena (1.316 seguidores) e
comunicação institucional. **Demote como fonte de descoberta de creators.**

## J · WONDERLAND AGENCY — veredito

`CREATOR_INTERMEDIARY_HUB`, **identidade PROVADA**: sociedade registada em Itteville
(SIREN 821377579), site oficial, fundadora **Émilie Vivier-Houvet** com LinkedIn e filiação
à AJCAM. A fonte declara que ela **gere parcerias de influenciadores agrícolas** e propõe
farmer-influencers a salões como o SITEVI.

**Lista de talentos agrícolas: `NOT_RECOVERED`.** E o aviso fica no registo: a agência
declara acompanhar PME em transformação digital **em geral** — não assumir que todo talento
dela é agrícola.

## K · AGROINFLUYE — recuperados

`RECOVERED = 23` de 66 · `NOT_RECOVERED = 43`. Sem avanço nesta rodada: a rota lê ~12
publicações por execução e a prioridade foi o `CROP_PROOF`, como pedido.

## L · CREATORS ITALIANOS COM CROP FIT

**1** — Davide Gomiero (`PROVED`, classe D: registo societário + imprensa declarando milho,
alfafa e soja). Leonardo Leggieri segue `PROMISING`.

Correção de modelo: o `PARTIAL` do Gomiero significava *"o milho está provado, o trigo e o
arroz da seed não"* — e isso **não é** o `PARTIAL` de "evidência fraca". Passou a `PROVED`
para as culturas provadas, com `CROPS_REJECTED_FROM_SEED = [WHEAT, RICE]` preservado.
Provar uma cultura e refutar outra são resultados distintos.

## M · CREATORS FRANCESES COM CROP FIT

**2** — Van Kempen (`ACTIVATION_READY`) e Forge (`PROMISING`).

## N · CREATORS ESPANHÓIS COM CROP FIT

**7** — cinco pessoas e duas empresas.

## O · SHORTLIST 1 · ES × ALMERÍA × HORTÍCOLAS ✅

**Agora corretamente separada:**

**Pessoas creators (2):**
| creator | cultura provada | atividade | contato público |
|---|---|---|---|
| `@germanagrolife` | PIMENTO, hortícolas protegidas | ativo · 32.912 | podcast próprio |
| `@agrosamanta_` (Níjar) | TOMATE | ativo · 28.694 | **e-mail publicado pela própria** |

**Parceiro de negócio (1):** `@biocampojoyma` — Bio Campojoyma, Níjar, ~15 M kg de pimento
bio/ano.

## P · SHORTLIST 2 · FR × GRANDES CULTURAS ✅

**Gilles Van Kempen** — `ACTIVATION_READY`, trigo/colza/cevada/milho/semente de cebola,
4 vídeos/30d. **David Forge** — `PROMISING`, falta a URL do canal *La Chaîne Agricole*.

## Q · SHORTLIST 3 · IT × VITE — **`NOT_READY`**

E a causa é exata, não vaga:

1. **Zero creators italianos com `GRAPEVINE` provado.** Os candidatos de vide da seed eram
   mídia de vinho (`WRONG_ASSIGNMENT`).
2. **A porta natural continua fechada** — `@enovitis_` foi mencionada mas não resolveu.
3. **As feiras italianas rendem empresas, não creators** (13 e 4 menções, quase todas
   empresas).

**Não foi fabricada shortlist.** O único italiano pronto é de milho, não de vide.

## R · RELAÇÕES COM MARCAS

Sem mudança de estado. `BRAND_ECOSYSTEM_SPONSORSHIP` ≠ `PRODUCT_ACTIVATION_PROVED`
preservado — **incluindo o caso Seipasa × Tomatito, cujo vencedor é comércio de fruta e
verdura**. O dado não foi corrigido para caber na tese.
`PRODUCT_ACTIVATION_PROVED`: nenhum caso.

## S · APIFY

| métrica | valor |
|---|---|
| execuções no manifesto da missão | **6** |
| custo desta rodada | **≈ US$ 0,156** (crop-proof 0,034 · França 0,116 · hubs 0,005) |
| custo acumulado | ≈ US$ 0,29 |
| perfis/vídeos lidos | 15 perfis + 30 vídeos + 4 hubs |

**Nota de gasto:** a medição francesa custou **US$ 0,116** — três vezes toda a extração de
hubs — para medir **um** canal. O ator de YouTube é caro por unidade; vale para fechar um
candidato, não para varrer.

## T · LACUNAS REAIS

1. **`MISSING_CROP_PROOF` ainda em 13** dos 16 `PROMISING`. Caiu pouco porque a régua
   apertou ao mesmo tempo — e isso é correto.
2. **IT × VITE sem base.** Precisa da conta do Enovitis ou de outra porta de viticultura.
3. **43 dos 66 nomeados do AgroInfluye** por recuperar.
4. **David Forge** a uma URL de distância.
5. **Feiras rendem empresas** — a estratégia italiana precisa mudar de porta, não de esforço.
6. **`FIELD_CONTENT_RATE` continua não calculado.** N = 12 posts por perfil. Registados
   `N_CONTENT_ITEMS_REVIEWED` e `CONTENT_TYPES_OBSERVED`, sem virar taxa. **Proposta ao
   árbitro, feita antes de ver resultado: N ≥ 30 conteúdos por perfil para publicar taxa.**
7. **Mapa de pecuária** com 3 creators à espera.
8. **Só Instagram e um canal de YouTube.** TikTok e LinkedIn por usar.

---

## LEIS NOVAS DESTA RODADA

| # | lei | prova |
|---|---|---|
| 13 | `ACCOUNT_OF_FARM_COMPANY ≠ PERSON_CREATOR` | 4 testes, 2 listas separadas |
| 14 | só as quatro classes A–D provam cultura | `CROP_PROOF_TYPE` validado no portão |
| 15 | `PARTIAL` (menção única) **não** é `CROP_FIT_PROVED` | teste dedicado |
| 16 | casar cultura por **palavra inteira**, nunca substring | 3 testes de falso positivo |
| 17 | quem **fala** da cultura não necessariamente a **produz** | `CROP_TOPIC_ONLY` |
| 18 | hub sem conta provada **não** se raspa | `HUB_DISCOVERY = BLOCKED` |

**70 provas na missão · `FULL_SUITE_NEW_FAILURES = 0`, medido por diferença de conjuntos.**

**Casco não alterado. Sem ranking. Sem score único. Sem expansão de países.**
