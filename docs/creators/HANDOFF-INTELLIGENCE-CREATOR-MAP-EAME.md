# HANDOFF · MAPA DE CREATORS EAME → RODADA DE INTELIGÊNCIA

**Data:** 2026-08-30 · **Missão 14** · **Autocontido**: quem ler isto não precisa da conversa.

---

## 0 · LEITURA RÁPIDA — o estado, em nove linhas

| | |
|---|---|
| **CAPABILITY STATUS** | **`FROZEN_WAITING_FOR_INTELLIGENCE`** |
| **WHAT IT CAN ANSWER TODAY** | *"Para esta cultura, neste país e região, quem o Marketing já consegue avaliar — e o que ainda não sabemos sobre essa pessoa?"* |
| **WHERE IT CAN ANSWER TODAY** | ES × Almería × hortícolas · ES × Andalucía × olivo · FR × Centre-Val de Loire × cereais · IT × Veneto × milho · **18 combinações `COUNTRY\|CROP`** |
| **WHERE IT CANNOT ANSWER TODAY** | **IT × vide** (`CAPABILITY_COVERAGE_GAP`) · qualquer país fora de ES/IT/FR · qualquer cultura fora das 18 |
| **PERSON_CREATOR_ACTIVATION_READY** | **8** |
| **FARM_BUSINESS_PARTNER_READY** | **2** |
| **`CREATORS_READY`** | **`PROHIBITED_METRIC`** — pessoa ≠ empresa |
| **WHAT CHANGES OVER TIME** | **atividade** (dias) → é o campo que expira primeiro. Cultura (semanas). Identidade (raro, mas invalida tudo). Marca (nunca se apaga). Seguidores (contínuo, **não muda decisão**) |
| **REVALIDATION RULE** | **`NOT_YET_DEFINED`** — nenhuma validade arbitrária foi atribuída |

### A pergunta, e a que ela NÃO é

> **WHO COULD MARKETING EVALUATE / CALL?**
> **NÃO:** *who should Marketing hire?*

### A lei que precisa viajar com os dados

> **`PERSON_CREATOR` e `FARM_BUSINESS` nunca se somam sob o nome de creators.**
> Uma `FARM_BUSINESS` pode ser altamente útil para Marketing, campo, evento ou conteúdo —
> e continua **fora** da contagem de creators-pessoa. São relações comerciais diferentes,
> com outro contrato, outro interlocutor e outro preço.

### A fronteira com a CONVERGÊNCIA

O Creator Map pode acrescentar a um caso `ACTIVATION_ROUTE_AVAILABLE` ou
`RELEVANT_PUBLIC_VOICE_AVAILABLE` **quando provado**.

**Não confirma** `FIELD_PROBLEM` · `INCIDENCE` · `MARKET_OPPORTUNITY` · `PRODUCT_FIT`.
É uma camada de **AUDIÊNCIA / ATIVAÇÃO / VOZ PÚBLICA** — um creator prova que existe *voz*
para aquela cultura naquele lugar, e nada além disso.

### HOW TO JOIN

| frente | chave / gancho |
|---|---|
| **META** | `PERSON_ID` · `ENTITY_ID` · `BRAND` · `OBSERVED_AT` → `CREATOR_APPEARANCE_OBSERVED`. `PAID_CREATOR_RELATION` **só com prova adicional** |
| **COMPETITION** | `BRAND` × `RELATION_TYPE` — 4 casos de concorrente já mapeados |
| **RADAR / CASES** | `COUNTRY` × `CROP` → `CREATOR-CAPABILITY-EAME.json` |
| **FIELD** | creators com conteúdo de campo → `FIELD_VOICE` (não iniciado) |
| **EXPERTS** | `SENSOR_ROLE_LINK` — ponteiro, nunca fusão |
| **TIME** | `AS_OF_DATE` em toda métrica de atividade |

---

## 1 · O QUE ESTA CAPACIDADE PROVOU

**Pergunta de negócio que ela responde:**

> *"Se Marketing ou Market Development quiser agir para esta cultura, neste país e região,
> quem já tem relevância real junto àquele público — e o que ainda não sabemos sobre essa
> pessoa?"*

**O que está provado, com evidência preservada:**

1. **O mercado europeu de creators agrícolas existe e é comprado.** ES, IT e FR, com
   monetização declarada pelos próprios creators e infraestrutura de intermediação
   (AGROLAND em Espanha, Wonderland Agency em França).
2. **Empresas de proteção de cultivo já usam creators** — BASF, Seipasa, Syngenta (ES) e
   Bayer (FR). Quatro casos, todos com fonte.
3. **Descoberta por hub funciona, e rende muito mais que lista pronta.** 12 publicações da
   conta de um prémio → 23 pessoas, 17 válidas. Uma lista externa de 25 handles → 0 válidas.
4. **Identity-first não é preferência, é necessidade.** Sete classes distintas de erro
   medidas, cada uma travada como teste de regressão.
5. **Seguidores não ordenam utilidade.** Dois perfis somam 5,2 milhões e declaram audiência
   urbana ou de comida.
6. **Prova de cultura muda o resultado.** A correção do matcher levou 8 `PROVED` a 2.
7. **Pessoa e empresa não se somam.** 8 pessoas + 2 contas de empresa, nunca uma soma só.

## 2 · O QUE ELA **NÃO** PROVOU

- **`PRODUCT_ACTIVATION_PROVED` = nenhum caso** nos três países. Isto é
  `NOT_OBSERVED_IN_MEASURED_CORPUS`, e o corpus é pequeno: pesquisa aberta + Instagram +
  um canal de YouTube. **Não é "ninguém faz" nem white space de mercado.**
- **`ADAMA_CREATOR_COLLABORATION` = `NOT_OBSERVED`** em ES/IT/FR. Busca feita, não é prova
  de ausência.
- **Nenhuma audiência foi medida.** `FACING` é o lado do balcão observado, não a composição
  real dos seguidores.
- **Nenhuma taxa de conteúdo foi publicada.** N = 12 por perfil; proposta de N ≥ 30 aguarda
  arbitragem.
- **39 de 43 hubs não foram abertos.**

## 3 · ONDE ELA JÁ RESPONDE, E ONDE NÃO

| recorte | resposta |
|---|---|
| **ES × Almería × hortícolas** | **READY** — 2 pessoas + 1 empresa |
| **ES × Andalucía × olivo** | **READY** — 2 pessoas |
| **FR × Centre-Val de Loire × cereais** | **READY** — 2 pessoas |
| **IT × Veneto × milho** | **READY** — 1 pessoa |
| **IT × vide** | **NOT_READY** — causa medida, ver §5 |

`CREATOR-CAPABILITY-EAME.json` responde por `COUNTRY|CROP` para **18 combinações**, e
distingue `NOT_READY` (procurámos, não há) de `NOT_ASKED` (não procurámos).

## 4 · OS MELHORES EXEMPLOS PARA MOSTRAR

**O que a ferramenta acerta:** `@agrosamanta_` — agricultora em Níjar, tomate provado por
conteúdo recorrente, ativa (10 posts/30d), **e-mail profissional publicado por ela própria**.
Descoberta por menção na conta de um prémio, não por lista.

**O que a ferramenta impede:** `@lajoya.agro` tem **2,6 milhões de seguidores**, usa
`#agroinfluencer` — e declara na própria bio que explica campo *"para gente de Ciudad"*.
Qualquer ordenação por seguidores o poria em primeiro lugar numa ativação dirigida a quem
aplica defensivo. A régua devolve-o como `LOW`.

**O erro mais caro que ela apanhou:** `@davide_gomiero`, o handle da lista externa, está
**errado**. O real é `@gomierofarm`, com 457 mil seguidores e uma exploração de ~400 ha.
Sem o portão de identidade, o melhor candidato italiano teria desaparecido por erro de
endereço — e a lista continuaria a parecer correta.

## 5 · IT × VITE — a causa exata do `NOT_READY`

1. Zero creators **pessoa** italianos com viticultura provada.
2. Os candidatos de vide da lista externa eram **mídia de vinho** — crítico, sommelier,
   blogger — e saíram como `WRONG_ASSIGNMENT`.
3. A porta natural, **Enovitis in Campo**, teve a conta oficial **provada** (`@enovitis_`,
   site `enovitisincampo.it`) e rendeu **zero pessoas** em 12 publicações.
4. O padrão é consistente e medido: **prémios mencionam pessoas, feiras mencionam empresas.**

**Falta uma porta italiana de PESSOAS em viticultura.** Não é falta de esforço — é falta de
porta, e abrir mais feiras não resolve.

## 6 · COMO CRUZA COM AS OUTRAS FRENTES

| frente | cruzamento possível | estado |
|---|---|---|
| **META** | se um anúncio mostrar uma destas pessoas → `CREATOR_APPEARANCE_OBSERVED`. `PAID_CREATOR_RELATION` só com prova adicional | **chaves prontas**, não antecipado |
| **COMPETITION** | 4 casos de concorrente × creator já mapeados, com tipo de relação distinto | pronto |
| **RADAR / CASES** | `COUNTRY × CROP × ISSUE` → "há alguém para ativação aqui?" | **artefato pronto** |
| **EXPERTS / EARLY SIGNAL** | `SENSOR_ROLE_LINK` é ponteiro; uma pessoa pode ter os dois papéis sem os fundir | ponteiro pronto, nenhum ligado |
| **FIELD** | creators com conteúdo de campo podem alimentar `FIELD_VOICE` | não iniciado |
| **TIME** | `AS_OF_DATE` em toda métrica de atividade | pronto |

**Chaves de junção:** `PERSON_ID` · `ENTITY_ID` · `BRAND` · `COUNTRY` · `CROP` · `OBSERVED_AT`.

## 7 · O QUE MUDA COM QUE FREQUÊNCIA

| dado | ritmo | consequência |
|---|---|---|
| **atividade** (último post, 30/90d) | **dias** | é o campo que expira primeiro; `ACTIVATION_READY` sem remedição envelhece |
| conteúdo / prova de cultura | semanas | uma cultura provada raramente se torna falsa |
| identidade, handle | raro | mas quando muda, invalida tudo o resto |
| relação com marca | por descoberta | nunca se apaga: histórico é histórico |
| seguidores | contínuo | **descritivo**; não muda decisão |

> A consequência operacional: **`ACTIVATION_READY` tem prazo de validade.** Um recorte medido
> há três meses precisa de remedição de atividade antes de ir para uma reunião.

## 8 · VALOR POSSÍVEL, POR ÁREA

- **Marketing** — responde *quem avaliar* por país × cultura, com rota de contacto pública e
  conflito com concorrente à vista. **Não recomenda contratação.**
- **Market Development** — mostra onde existe voz de campo organizada e onde não existe;
  a ausência é informação de mercado.
- **Comercial** — as contas de exploração (`FARM_BUSINESS`) são candidatos a caso de estudo,
  visita de campo e parceria técnica — outra relação, não influencer.
- **Técnico** — os hubs técnicos mapeados (CREA, Fondazione Mach, AGROINNOVA, Enovitis)
  continuam válidos como fonte de especialista, mesmo tendo rendido zero creators.

## 9 · O QUE A PRÓXIMA RODADA DEVE DECIDIR — E QUE ESTA MISSÃO NÃO DECIDE

**A superfície no portal não foi decidida aqui**, por instrução: aba própria, ferramenta,
camada dentro de casos ou painel de Marketing é decisão da Rodada de Inteligência com o red
team externo.

O que esta missão entrega para essa decisão: **capacidade provada, dados, contrato,
exemplos, e as lacunas nomeadas**.

---

**Artefatos:** `CREATOR-CAPABILITY-EAME.json` (consulta) · `DECISION-FICHES.json` (fichas) ·
`WHO-COULD-MARKETING-CALL.json` (mapa) · `HUB-YIELD.json` · `HUB-OFFICIAL-IDENTITY.json` ·
`CROP-PROOF.json` · `BRAND-COLLABORATIONS-EU.json` · `MARKET-EVIDENCE-EU.json`.

**Contrato executável:** `scripts/creators.py` · **90 provas** em `tests/test_creators.py`.

**Custo Apify acumulado da missão: ≈ US$ 0,29.**
