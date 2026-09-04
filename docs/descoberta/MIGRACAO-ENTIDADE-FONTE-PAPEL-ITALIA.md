# MIGRAÇÃO ESTRUTURAL DA CAMADA ITALIANA — ENTITY · SOURCE · ROLE

**Data:** 2026-09-04 · **HEAD antes:** `c126b3d` · **Branch:** `claude/human-agricultural-sensors-8fv0fw`
**PR:** não aberto · **Descoberta nova:** nenhuma · **Coleta:** nenhuma · **Portal:** intocado

Executado por `scripts/sensor_entidade_it.py`. Artefatos:
[`ENTITIES.json`](../../data/samples/IT-HUMAN-SENSORS/ENTITIES.json) ·
[`SOURCES.json`](../../data/samples/IT-HUMAN-SENSORS/SOURCES.json) ·
[`ID-LEDGER.json`](../../data/samples/IT-HUMAN-SENSORS/ID-LEDGER.json) ·
[`ID-MIGRATION.json`](../../data/samples/IT-HUMAN-SENSORS/ID-MIGRATION.json) ·
[`MIGRATION-VALIDATION.json`](../../data/samples/IT-HUMAN-SENSORS/MIGRATION-VALIDATION.json)

---

## P-014 — decidido

```
ITALY_WRITES_TO_BRAZIL_DB = NO
CONTRACT_MIRRORED         = YES

BRASIL  →  semântica · contrato · leis
ITÁLIA  →  dados · registro · classificadores
```

O Brasil é **referência de contrato**, não infraestrutura compartilhada. Nenhuma camada
federada foi criada. Se um dia Brasil e Itália precisarem reconhecer a mesma entidade,
será uma camada explícita de crosswalk — nunca compartilhamento silencioso de banco.

---

## 1 · IDENTIDADE PERSISTENTE — o `bigserial`, não mais um hash

**O dono real da identidade persistente no Brasil é `fontes.id`**, um `bigserial`
(`supabase-conteudo.sql:11`): chave substituta, **sem nenhuma semântica de negócio**,
protegida por uma trava em AST (`provar-fonte-por-id.py:96,144-167`) que proíbe usar
`nome` como chave de operação.

⚠️ **`entidades.chave` NÃO serve**, apesar do nome: é derivada do menor `external_id` do
grupo, e o próprio arquivo declara que *"muda se o grupo ganhar um id menor"*
(`entidade-fase-1.py:44-47`). Copiar aquilo seria trocar um id instável por outro.

Como aqui não há Postgres, o papel do `bigserial` é feito por um **livro-razão
versionado** — `ID-LEDGER.json` — que é a única fonte de verdade sobre qual id já foi
dado a quem. Ids no formato `IT-E-000001` / `IT-S-000001`, **atribuídos uma vez**.

### Como o id sobrevive a rename e a mudança de instituição

Ele **não é calculado a partir de nada**. A ligação `registro → id` é feita por
**REIVINDICAÇÕES (claims)** — os identificadores observáveis:

```
orcid:0000-0003-…  ·  web:fmach.it  ·  youtube:@fondazionemach  ·  instagram:@…
```

Duas fichas que compartilhem **qualquer** claim são a mesma entidade (union-find sobre
claims). **Nome e organização não são claims** e não participam da resolução — que é a lei
brasileira *"Nome NUNCA é identificador: a casa tem 142 nomes repetidos"*
(`entidades.sql:80`).

| propriedade exigida | como é atendida |
|---|---|
| não depende de nome | nome não é claim |
| não depende de organização atual | organização não é claim |
| sobrevive a rename | o id vive no ledger, não no conteúdo |
| sobrevive a mudança de instituição | claims (ORCID, canal, URL) não mudam com a lotação |
| sobrevive à adição de novos canais | canal novo **acrescenta** claim à mesma entidade |

**`NAME_OR_ORG_USED_AS_OPERATIONAL_ID = 0`** — medido, não afirmado: o ledger só contém
claims com prefixo de plataforma e âncoras `legacy:`.

---

## 2 · ENTIDADE ≠ FONTE — os 224 viram 221 + 281

```
ENTITIES_TOTAL          221
SOURCES_TOTAL           281   (LINKED 189 · UNRESOLVED 92)
ENTITY_WITH_1_SOURCE     54
ENTITY_WITH_2PLUS_SOURCES 32
ENTITY_WITH_0_SOURCE    135
```

**224 → 221: três entidades absorveram dois "sensores" cada** — e as três foram descobertas
**por claim declarado**, nunca por semelhança de nome:

| entidade | fundiu | prova do vínculo |
|---|---|---|
| **Fondazione Edmund Mach** | `web:fmach.it` + `youtube:@fondazionemach` | o canal **declara `fmach.it`** na própria aba About |
| **AgroNotizie — Image Line** | `web:agronotizie…` + `youtube:@agronotizietv` | idem |
| **AIPO** | `web:aipoverona.it` + `youtube:@aipoverona7094` | idem |

Isto é o `MESMA_ENTIDADE` brasileiro, com a evidência mais forte da escada
(`como_achou = declarado_no_perfil`).

---

## 3 · PAPEL MULTIVALORADO — e a lei que esta missão tinha violado

```
ROLE_LOST_BY_WEIGHT            = 0
ROLE_REMOVED_BY_DECLARED_RULE  = 10
MULTI_ROLE_ENTITIES            = 11
ROLES_BY_STATE  →  DECLARADO 184 · NAO_PROVADO 46
```

Nenhum papel é sobrescrito. **"Peso maior vence" não existe aqui** — a única remoção
possível é por **regra declarada** (papel de pessoa numa organização), e cada uma é
registrada em `ROLES_REMOVED` com nome, motivo e ficha de origem.

### ⛔ A correção mais dura desta rodada

`MODELO-DE-IDENTIDADE-EAME.md` é literal sobre o que **nunca** decide papel:

> *nome da conta · foto · estilo do texto · idioma · **prosa livre (`about`,
> `description`)** · o assunto de um post*

**A rota de canal italiana lia a descrição do canal e produzia papéis.** É exatamente o
classificador que a casa já mediu e reprovou (`Oleo Revista` → `RESEARCHER` porque
"investigador" aparecia numa notícia citada). O YouTube **não expõe campo estruturado de
papel**. Portanto todo papel vindo dessa rota passou a `NAO_PROVADO`.

> ### O zero que precisa ser lido, não escondido
>
> ```
> RESEARCHERS = 135   COOPERATIVES_OR_ORGS = 43
> AGRONOMISTS = 0     TECHNICIANS = 0     PRODUCERS = 0
> ```
>
> **Não é perda de dado — é a retirada de uma afirmação que nunca teve prova.** Os
> candidatos continuam gravados: `agronomo` 11 · `produtor` 11 ·
> `organizacao_de_pesquisa` 11 · `tecnico` 5 · `consultor` 3 · `cooperativa` 3 ·
> `pesquisador` 2, todos como `NAO_PROVADO`.
>
> Fechar isso exige uma rota com **campo declarado estruturado** — headline de LinkedIn,
> página de equipe institucional, Ordine dei Dottori Agronomi. **Não executada nesta
> rodada.**

`AMBIGUOUS` nunca virou papel verdadeiro. Ausência de prova é `NÃO SEI`, jamais `FALSE`.

---

## 4 · ORGANIZAÇÃO ≠ PESSOA — a ordem, e por que ela tem de ser final

`classificar-fontes.py:396-397` decide `organizacao|pessoa` **antes** do papel, e as duas
listas são **disjuntas**. Copiado — com uma correção que só apareceu ao rodar:

> ⚠️ **A purga tem de ser passe FINAL, depois das fusões.** Rodá-la por registro deixava
> passar o AgroNotizie: a ficha do canal chegava com `KIND` indefinido (o nome do canal
> não tem forma jurídica), ganhava `agronomo`, e só **depois** a fusão por claim revelava
> que a entidade é o veículo. **Kind só é conhecido quando a entidade está inteira.**

### Os casos que você nomeou — reprocessados, sem descoberta nova

| entidade | KIND | DOMÍNIO | papéis depois |
|---|---|---|---|
| **AgroNotizie — Image Line** | organizacao | AGRO_PROFISSIONAL | `veiculo_tecnico` (DECLARADO) — **`agronomo` removido** |
| **Medical Excellence TV** | organizacao | **NÃO SEI** | `organizacao_de_pesquisa` **NAO_PROVADO** |
| **Archivio Nazionale Cinema Impresa** | organizacao | **NÃO SEI** | `organizacao_de_pesquisa` **NAO_PROVADO** |
| **Orto Da Coltivare** | NÃO SEI | **HOBBY_DECLARADO** | `agronomo` **NAO_PROVADO** |
| **W&A Gardens** | NÃO SEI | **HOBBY_DECLARADO** | `pesquisador` **NAO_PROVADO** |

Mais cinco que a mesma regra pegou e que não estavam na sua lista: `Agralia studio di
agronomia` (−agronomo, −produtor), `Agricolus srl` (−agronomo, −produtor),
`Consorzio Agrario del Nordest` (−tecnico), `Consorzi Agrari d'Italia` (−agronomo),
`Centro Agricoltura Ambiente S.r.l.` (−pesquisador), `ERSAF Lombardia` (−tecnico),
`AIPO` (−produtor).

Dois marcadores foram corrigidos por medição:

- **`campo` saiu** da lista de marcadores agronômicos: casava *"campo da medicina"* e fazia
  o **Medical Excellence TV** virar `AGRO_PROFISSIONAL`. É a lei *casar termo não é casar
  assunto*.
- **Hobby declarado passou a vencer**, mesmo com marcador agronômico junto: *"Vuoi rimanere
  aggiornato sulle ultime novità nel mondo agricolo **hobbistico**"* declara hobby e
  agricultura na mesma frase, e o que decide se é sensor de campo é a primeira.

`ORGANIZATION_CLASSIFIED_AS_PERSON_ROLE = 0` · `PORTAL_CLASSIFIED_AS_AGRONOMIST = 0`.

---

## 5 · AS 33 FONTES SEM ENTIDADE — e as 92 que a dívida virou

Nenhuma entidade foi inventada, nada foi fundido por semelhança de nome, nenhuma web foi
consultada para completar.

As 33 órfãs eram canais cuja identidade de entidade não estava resolvida. Sob o modelo
novo, **um canal com identificador observável já é a fonte de uma entidade** — e a
entidade nasce do claim, não do nome. As que tinham claim ligaram; as que não podiam ser
demonstradas ficaram:

```
ORPHAN_SOURCES = 92     ENTITY_LINK = UNRESOLVED
```

Os 92 são os canais **não promovidos**: 68 com `PAIS = NÃO SEI` e 24 com país estrangeiro
declarado. Eles entram no registro **como fontes visíveis e não qualificadas** — o
objetivo é *tornar a dívida visível, não zerá-la artificialmente*.

---

## 6 · ORCID DEIXA DE SER CATRACA (D-018 aplicado)

```
ORCID_PRESENT                    = 134
ORCID_ABSENT_BUT_IDENTITY_VALID  =  86
```

A estrutura canônica é `ENTITY → IDENTIFIERS [0..N]`, e ORCID é **um dos tipos**, ao lado
de `WEB`, `YOUTUBE`, `INSTAGRAM`, `LINKEDIN`, `FACEBOOK`, `TIKTOK`. Cada identificador
carrega `EVIDENCIA` e `ESTADO`.

**86 entidades são válidas sem ORCID nenhum.** No modelo antigo, sete pesquisadores tinham
sido barrados só por não terem ORCID; a catraca não existe mais.

---

## 7 · PAÍS AUSENTE (D-022 aplicado)

```
COUNTRY_ITALY_PROVED_BY_SELF_DECLARATION =  40   ← o canal declara "Italia"
COUNTRY_ITALY_PROVED_BY_ROUTE            = 181   ← AFF:"Italy" no EPMC, ou órgão público IT
COUNTRY_FOREIGN_PROVED                   =  24
COUNTRY_UNKNOWN                          =  68
```

Os 68 deixaram de significar `NOT_ITALY` e passaram a `COUNTRY = NÃO SEI`. **Isso não os
qualifica** como sensores italianos — apenas remove uma negativa que nunca foi medida.
Nenhuma coleta nova foi iniciada sobre eles.

⚠️ Os dois graus de prova **não se somam sem dizer o nome**: auto-declaração e garantia de
rota são evidências de naturezas diferentes, e ficam em campos separados.

---

## 8 · ALCANCE ≠ AUTORIDADE — quatro eixos, nunca uma média

```
SCIENTIFIC_AUTHORITY · TECHNICAL_AUTHORITY · FIELD_PROXIMITY · PUBLIC_REACH
FOLLOWERS_USED_AS_AUTHORITY = 0
```

`PUBLIC_REACH` guarda o número declarado e **não é lido por nenhuma regra**. É a única
trava brasileira plenamente válida, agora escrita em vez de acidental:

> *"média entre 'alcança 334 mil pessoas' e 'fala de manejo 1,8% do tempo' não significa
> nada"* — `gerar-dados.py:708-721`

---

## 9 · VALIDAÇÃO — as seis travas

| trava | resultado |
|---|---|
| `ROLE_LOST_BY_WEIGHT == 0` | **PASSA** |
| `ORGANIZATION_CLASSIFIED_AS_PERSON_ROLE == 0` | **PASSA** |
| `PORTAL_CLASSIFIED_AS_AGRONOMIST == 0` | **PASSA** |
| `NAME_OR_ORG_USED_AS_OPERATIONAL_ID == 0` | **PASSA** |
| `FOLLOWERS_USED_AS_AUTHORITY == 0` | **PASSA** |
| `ID_MIGRATION_LOSS == 0` | **PASSA** |

`OLD_SENSOR_IDS = 224` → `NEW_ENTITIES = 221`, com `ID-MIGRATION.json` guardando o mapa
`OLD_SENSOR_ID → NEW_ENTITY_ID` de **todos os 224**. Nada desapareceu em silêncio.

---

## VEREDITO

```
SAME_ARCHITECTURE_AS_BRASIL            = SIM
READY_FOR_SOCIAL_ENRICHMENT_COLLECTION = NÃO
```

**`SAME_ARCHITECTURE = SIM`.** As quatro incompatibilidades foram fechadas: id persistente
por claim, entidade separada de fonte, papel multivalorado com prova por papel, e órfãs
com estado explícito. O contrato brasileiro está espelhado — com registro próprio, sem
escrever no banco do Brasil.

**`READY_FOR_SOCIAL_ENRICHMENT_COLLECTION = NÃO`**, e agora por uma razão diferente e
melhor. A trava que você definiu é: *"só pode abrir quando for possível escolher uma
ENTITY e adicionar canais a ela sem criar nova entidade por plataforma, perder papel,
depender de ORCID, confundir ausência de país com exclusão, chamar organização de pessoa,
ou usar alcance como autoridade"*.

**Essas seis condições agora estão satisfeitas** — as seis travas passam. O que falta é
outra coisa:

| falta | medida |
|---|---|
| **135 entidades têm ZERO fontes** | são os pesquisadores; não há onde bater |
| **Zero papéis de campo PROVADOS** | agrônomo, técnico e produtor = 0 provados; existem só como candidatos |
| **Nenhuma chave de coleta** | `APIFY_TOKEN` ausente — o SINTONIA SCRAP não roda |

Abrir coleta social agora atingiria **40 entidades com presença pública** e deixaria 135
intocadas. E o enriquecimento mais valioso — ligar pesquisador a canal — **não tem
insumo**: nenhum dos 135 tem canal conhecido.

**A próxima rodada que muda o veredito é uma só:** a rota de **campo declarado
estruturado** (headline de LinkedIn, página de equipe institucional, `researcher-urls` do
ORCID). Ela fecha ao mesmo tempo os dois buracos — dá fonte às 135 entidades e dá prova
estruturada aos papéis de campo. **Não foi executada nesta rodada.**

---

## ANEXO · P-013 FECHADO — e os três números nunca brigaram

Auditoria forense somente-leitura no Brasil (HEAD `38e4b8d`, `git status` vazio ao fim).

```
P013_REAL_COVERAGE       = NÃO SEI   (veredito firme, não abstenção)
P013_DENOMINATOR         = não existe um
P013_CONTRACT_OPERATIONAL = PARCIAL
```

**`NÃO SEI` é firme porque foi provado por ausência de instrumento**, não por preguiça: o
grep exaustivo de `entidade_id` em todo o repositório mostra que a **única** ocorrência de
`entidade_id is not null` é a cláusula `WHERE` de um índice parcial. **Não existe
`count(entidade_id)` em lugar nenhum.**

### Os três números medem três coisas diferentes — e nenhum é cobertura

| número | o que é de verdade | prova |
|---|---|---|
| **47 / 95** | **contador de ESCRITA de uma rodada** (10/08, 11h18): 47 entidades criadas, 95 fontes ligadas *naquela execução* | a rodada seguinte (15/08) imprimiu **4 / 56** — o número **desceu**. Censo não desce; contador de rodada sim |
| **57** | `count(*)` da tabela **`entidades`** — outra grandeza. Entidade que **existe** ≠ entidade **referenciada** | e a citação de 23/08 é **literal hardcoded** em `matriz-do-rendimento.py:305`; o programa **nunca lê** a tabela |
| **3.275 / 3.299** | 🔴 **é `fontes.external_id`**, com o rótulo trocado | a medição original diz literalmente *"identidade **(external)** 3.275 de 3.298"*; e a seção que carimba "medido" se declara não-construída em `PLANO-location-resolver.md:665` |

**Prova aritmética de impossibilidade do 3.275:** 3.275 fichas apontando para no máximo 57
entidades daria média de ~57 fichas por entidade. Os grupos reais têm 2 a 3 fichas.

### As duas perguntas laterais

- **`enderecos` (3.627 linhas): FIO CORTADO confirmado.** Nenhum escritor vivo, nenhum
  consumidor externo (só o próprio escritor se relendo), nenhum `schedule` no workflow, e
  3.627 medido **idêntico** com cinco dias de intervalo. Tabela viva não fica parada.
- **`papel_da_fonte`: CONTRATO NÃO IMPLANTADO**, não tabela abandonada — nunca recebeu uma
  linha. Nasceu no **mesmo `alter table`** que `entidade_id`, com a semântica escrita como
  comentário no banco. Estado declarado: `⚠️ ESQUEMA_SEM_USO · ⛔ SEM SEGUNDA DECLARAÇÃO`.

### A lição, e ela já está aplicada na Itália

> **Toda coluna de contrato nasce com a sua consulta de cobertura no mesmo commit do DDL.**
> **Todo número publicado carrega: coluna medida · denominador declarado · data/execução.**

O Brasil criou `entidade_id`, criou até o índice parcial — e nunca escreveu o `count`.
Havia intenção; faltou o instrumento. `MIGRATION-VALIDATION.json` **é** esse censo para a
Itália, e declara os seus denominadores. E a saída de `migrar` fica separada como
**contador de escrita**, que não preenche tabela de cobertura.

Corolário herdado: **herdar tabela sem herdar consumidor é importar esquema morto.** A
Itália não espelhou `enderecos` nem `papel_da_fonte` — espelhou a semântica de canal dentro
de `SOURCES.json`, que tem leitor.

> ⚠️ E a consequência para a decisão P-014 é direta: se a Itália tivesse calibrado
> expectativa por *"99,3% já ligadas"*, dimensionaria o resolvedor de entidade para um
> problema que não existe. **Espelhar o contrato, nunca o número.**
