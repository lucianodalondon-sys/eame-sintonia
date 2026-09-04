# RESOLVER A PORTA, SEM ENTRAR — fontes e papéis das 221 entidades italianas

**Data:** 2026-09-04 · **HEAD antes:** `252a7b0` · **Branch:** `claude/human-agricultural-sensors-8fv0fw`

```
NEW_DISCOVERY_OF_ENTITIES                   = NO
NEW_CHANNEL_DISCOVERY_FOR_EXISTING_ENTITIES = YES
CONTENT_COLLECTION = NO · PORTAL_TOUCHED = NO · BRAZIL_TOUCHED = NO
```

Código: `scripts/sensor_resolver_fontes_it.py` (`orcid` · `sites` · `aplicar` · `orfas` · `medir`)
Artefatos: [`SOURCE-RESOLUTION.json`](../../data/samples/IT-HUMAN-SENSORS/SOURCE-RESOLUTION.json) ·
[`RESOLUTION-METRICS.json`](../../data/samples/IT-HUMAN-SENSORS/RESOLUTION-METRICS.json) ·
[`FICHAS-RESOLUCAO.json`](../../data/samples/IT-HUMAN-SENSORS/FICHAS-RESOLUCAO.json)

---

## 1 · POR QUE O ORCID FOI A PRIMEIRA ROTA — e não uma busca

`researcher-urls` é o campo onde **a própria pessoa** declara os seus endereços. Não é
inferência, não é busca por nome, não é semelhança textual: é **declaração do titular** — o
degrau mais forte da escada de procedência (`declaracao > perfil > link_no_site > busca`).

E `employments` traz três campos **estruturados**: `role-title`, `organization` e
`address.country`. É exatamente o que a Rota B exigia e o que a prosa livre nunca deu.

| medido | valor |
|---|---:|
| entidades com ORCID declarado | 134 |
| com `researcher-urls` preenchido | **32** |
| URLs declaradas | **53** |
| com `employments` preenchido | **107** |
| falhas de leitura | **0** |

---

## 2 · ⚠️ A ARMADILHA QUE ESTA ROTA CRIOU — e os três guardas

A resolução de entidade é por **claim**. Um pesquisador que declara o site do **empregador**
faria a união silenciosa **engolir a pessoa dentro da instituição**.

E o caso não é hipotético — ele estava nos dados:

> **Marco Lapris** e **Michela Errico** declaram **as mesmas duas URLs**:
> `dipartimenti.unicatt.it/diana-home` e `scuoledidottorato.unicatt.it/agrisystem-home`.
> Sem guarda, as duas pessoas virariam **uma entidade**.

| guarda | o que faz | acionado |
|---|---|---:|
| **1 · raiz de domínio não é claim** | URL sem caminho é o endereço do empregador, não da pessoa. Entra como FONTE, não participa da resolução | **4** |
| **2 · dois ORCID nunca viram uma entidade** | união recusada e conflito registrado | 0 conflitos |
| **3 · endereço partilhado não é identidade** | URL declarada por ≥2 pesquisadores distintos é página institucional compartilhada | **4** |

`ENTIDADES_COM_DOIS_ORCID = nenhuma` · `NEW_ENTITIES = 0`.

---

## 3 · ROTA A — o que as portas realmente são

```
NEW_SOURCES_LINKED_WITH_PROOF = 53
   MONITORABLE_CHANNEL         =  3
   IDENTITY_SOURCE             = 50
```

**Por plataforma declarada:** institucional 30 · ResearchGate 13 · Scholar 7 · LinkedIn 2 ·
Twitter 1.

> ### A distinção da Rota C não é formalidade — ela é o resultado
>
> **50 das 53 portas novas provam identidade e não publicam conteúdo novo.** Uma página
> `unibo.it/sitoweb/...` ou um perfil ResearchGate diz **quem a pessoa é**; não é uma
> superfície onde conteúdo novo apareça de forma monitorável.
>
> `researchgate` e `scholar` ficaram como `IDENTITY_SOURCE` por decisão declarada: publicam
> obra nova, mas são **espelho da produção científica que o Europe PMC já cobre** — contá-los
> como canal novo seria contar a mesma testemunha duas vezes.

```
RESEARCHERS_STILL_ZERO_SOURCE         135 → 103
RESEARCHERS_WITH_1PLUS_SOURCE                32
RESEARCHERS_WITH_MONITORABLE_CHANNEL          3
RESEARCHERS_WITH_IDENTITY_SOURCE_ONLY        29
```

**Três.** De 135 pesquisadores, três têm hoje um canal onde se possa escutar algo novo.
Não é falha da rota: é o que o ORCID italiano declara.

---

## 4 · ROTA B — papel por campo estruturado

```
PROVED_FIELD_ROLES   0 → 3        ROLE_PROVED_TOTAL   = 114
ROLE_PROBABLE_TOTAL  = 2          ROLE_NAO_PROVADO    = 42
MULTI_ROLE_ENTITIES  = 58
```

| papel | provado |
|---|---:|
| TECHNICIAN | **3** |
| AGRONOMIST | 0 |
| PRODUCER | 0 |
| CONSULTANT | 0 |
| cooperativa · serviço fitossanitário (org) | 2 |

### O que o ORCID dá — e o que ele não dá

`employments.role-title` provou **114 papéis**, mas quase todos são **acadêmicos**:
`pesquisador` 60 · `professor` 31 · `estudante` 7 · `tecnico` 3.

> **ORCID declara cargo acadêmico, não papel de campo.** Um `Ricercatore` é pesquisador
> provado; ele não é agrônomo, técnico de campo nem produtor por isso. A rota fecha o buraco
> científico e **não** fecha o buraco de campo.

Títulos italianos do organograma foram mapeados a partir dos dados vistos — `ricercator`
(Ricercatori/Ricercatore/a tempo determinato), `docent` (Docenti di ruolo Ia e IIa fascia),
`fellow`, `phd`. E **`Director`, `Collaboratori` e `Group Leader` ficaram deliberadamente
sem mapa**: são posição hierárquica, não papel agrícola. Mapeá-los seria inventar papel a
partir de organograma.

### Os sites — a rota que quase não rendeu, e isso é informação

23 entidades com papel não provado têm site próprio declarado. Foram lidas **21**; apenas
**4** trazem um título profissional em posição estruturada:

| entidade | papel | campo | força |
|---|---|---|---|
| Consorzio Agrario del Nordest | cooperativa | `title` | **PROVADO** |
| Terre dell'Etruria | cooperativa | `title` | **PROVADO** |
| Dario Cortese | consultor | `og:description` | PROBABLE |
| Plant Nutrition Alchemy | agronomo | `og:description` | PROBABLE |

> **`og:description` não vira PROVADO.** É campo estruturado, mas o **conteúdo** dele é
> livre. O contrato espelhado admite grau intermediário (`enderecos.confianca` brasileiro:
> alta · media · duvidosa), e promover isso a PROVADO por conveniência seria repetir
> exatamente o erro que esta camada já cometeu uma vez.

**O corpo do texto nunca entrou.** `ROLE_FROM_FREE_PROSE = 0`.

---

## 5 · AS 92 ÓRFÃS

```
UNRESOLVED_BEFORE = 92 · RESOLVED_WITH_PROOF = 1 · UNRESOLVED_AFTER = 91
```

| fonte | entidade | prova |
|---|---|---|
| `IT-S-000190` L'Informatore Agrario | `IT-E-000179` | o próprio canal **declara** `informatoreagrario.it` na aba About — endereço que já é claim da entidade |

**Uma.** As outras 91 não declaram nenhum endereço que seja claim de entidade existente, e
**não foram fundidas por nome**. A dívida continua visível, e essa é a entrega correta.

---

## 6 · PAÍS

`employments.organization.address.country` é campo estruturado: **IT 198** declarações ·
US 4 · DE 4 · SE 3 · ES 3 · GB 2 · FR 2 · EG 1. Entidades com país provado por esse campo
recebem `PAIS_ESTADO = PROVADO_POR_ORCID_EMPLOYMENT`.

`COUNTRY_INFERRED_FROM_LANGUAGE = 0`. Domínio `.it` sozinho não foi usado como prova.

---

## 7 · MÉTRICAS

| | antes | depois |
|---|---:|---:|
| ENTITIES | 221 | **221** |
| SOURCES | 281 | **334** |
| RESEARCHERS_ZERO_SOURCE | 135 | **103** |
| PROVED_FIELD_ROLES | 0 | **3** |
| UNRESOLVED | 92 | **91** |

`ENTITIES_WITH_1PLUS_SOURCE` 118 · `ENTITIES_WITH_2PLUS_SOURCES` 45 ·
`ENTITIES_WITH_ZERO_SOURCE` 103 · `IDENTITY_ONLY_SOURCES` 154

**Canais públicos:** YouTube 45 · Instagram 15 · LinkedIn 9 · TikTok 3 ·
outros recorrentes 17 — **89 monitoráveis**.

### As oito travas

`NEW_ENTITY_FROM_CHANNEL` · `ROLE_LOST_BY_WEIGHT` · `ROLE_FROM_FREE_PROSE` ·
`ORGANIZATION_AS_PERSON_ROLE` · `PORTAL_AS_AGRONOMIST` · `NAME_OR_ORG_AS_OPERATIONAL_ID` ·
`FOLLOWERS_AS_AUTHORITY` · `COUNTRY_INFERRED_FROM_LANGUAGE` — **todas em 0, todas medidas.**

---

## 8 · AMOSTRA — e uma correção de escopo

A missão pedia 5 + 5 + 5. Entrego **12**, não 15, e o motivo é o achado:

| grupo | pedidos | entregues |
|---|---:|---:|
| pesquisadores com canal monitorável | 5 | **2** |
| papel de campo agora provado | 5 | 5 |
| casos difíceis / NÃO SEI | 5 | 5 |

**Só existem 3 pesquisadores com canal monitorável, e dois deles têm papel de pesquisador
provado.** Preencher os cinco exigiria afrouxar "monitorável" ou "provado" — o oposto do que
esta missão é.

**Riccardo Baroncelli** (`IT-E-000068`) é o caso que a missão inteira procurava: pesquisador
e professor **provados** por `role-title`, identidade em `unibo.it/sitoweb/riccardo.baroncelli`,
e canal monitorável no Twitter declarado por ele mesmo no ORCID. País provado por employment.

---

## PORTÃO

```
SOURCE_RESOLUTION_READY         = SIM
SOCIAL_CONTENT_COLLECTION_READY = SIM
```

**`SOURCE_RESOLUTION_READY = SIM`** — a máquina de resolver porta funciona e está provada:
53 fontes ligadas com prova de titularidade, 0 entidades novas, três guardas acionados 8
vezes, e a fusão Lapris/Errico evitada. A **cobertura** é parcial (103 pesquisadores seguem
sem porta), mas isso é lacuna de rota, não defeito de mecanismo.

**`SOCIAL_CONTENT_COLLECTION_READY = SIM`** — as seis condições declaradas estão satisfeitas:

| # | condição | estado |
|---|---|---|
| 1 | conteúdo anexa a `SOURCE_ID` existente | **SIM** — 334 fontes com id |
| 2 | cada `SOURCE_ID` aponta para entidade **ou** carrega dívida explícita | **SIM** — 243 ligadas + 91 `UNRESOLVED` nomeadas |
| 3 | coletar canal novo não cria entidade | **SIM** — `NEW_ENTITY_FROM_CHANNEL = 0`, ledger + 3 guardas |
| 4 | papel não depende do conteúdo | **SIM** — `ROLE_FROM_FREE_PROSE = 0` |
| 5 | autoridade não depende de followers | **SIM** — `FOLLOWERS_AS_AUTHORITY = 0` |
| 6 | universo declarado e mensurável | **SIM** — abaixo |

### COLLECTION_UNIVERSE — proposto, **não executado**

**89 canais monitoráveis, 44 entidades alcançadas.**

| família | canais | por plataforma |
|---|---:|---|
| **SEM_PAPEL_PROVADO** | **79** | youtube 41 · facebook 14 · instagram 13 · linkedin 8 · tiktok 3 |
| MERCADO (cooperativa/OP) | 6 | youtube 2 · facebook 2 · instagram 2 |
| TÉCNICO | 2 | youtube 2 |
| CIÊNCIA | 2 | twitter 1 · linkedin 1 |

Fora do universo: **154 fontes só-identidade** (não publicam) e **91 `UNRESOLVED`** (sem
entidade — coletá-las criaria conteúdo órfão).

> ⚠️ **Duas ressalvas que o `SIM` não apaga.**
>
> **79 dos 89 canais pertencem a entidades sem papel provado.** A coleta é
> arquiteturalmente segura — o conteúdo não vai criar nem alterar papel — mas o que voltar
> será atribuível a uma entidade cujo papel agrícola continua `NÃO SEI`. Isso é aceitável
> para medir *o que se fala*; não sustenta ainda *quem é o sensor*.
>
> **Não existe chave de coleta.** `APIFY_TOKEN` continua ausente. Isso não é uma das seis
> condições, e por isso não derruba o `SIM` — mas bloqueia a execução, e não deve ser
> descoberto na hora de rodar.

**Parado aqui. Nenhuma coleta iniciada. PR não aberto.**
