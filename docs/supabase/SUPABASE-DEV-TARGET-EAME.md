# RESOLUÇÃO DO ALVO DEV — SINTONIA EAME

**Data:** 2026-08-31 · artefato em `data/supabase/SUPABASE-DEV-TARGET.json`

```
MIGRATION_APPLIED_DEV = NO   REAL_DATA_PUBLISHED = NO   V8_WIRED = NO
DEV_TARGET_CREATED = NO      NADA FOI CRIADO, LIMPO OU APAGADO
```

---

## 0 · DUAS CORREÇÕES, NA ORDEM EM QUE ACONTECERAM

**A primeira foi minha.** Eu declarei `DEV_INSTANCE_AVAILABLE = NO`. A medição estava
certa — não há credencial, CLI, `psql` nem Docker nesta máquina — mas o **rótulo** estava
errado: eu concluí sobre a existência do banco a partir de uma medição do meu acesso.

Passaram a ser três coisas:

| | responde | quem mede |
|---|---|---|
| `SUPABASE_PROJECT_EXISTS` | existe projeto na conta? | acesso autorizado |
| `CLAUDE_LOCAL_SUPABASE_ACCESS` | consigo abrir conexão daqui? | eu |
| `DEV_INSTANCE_AVAILABLE` | existe banco DEV **utilizável**? | o inventário |

**A segunda veio do inventário.** O projeto existe, está saudável — e **não serve como DEV**.

---

## 1 · O INVENTÁRIO, MEDIDO POR ACESSO AUTORIZADO

```
PROJECT_NAME = eame-sintonia    PROJECT_REF = odhdwvugikjdvkapbowe
REGION = eu-west-1              STATUS = ACTIVE_HEALTHY

AUTH_USERS ....................... 0
STORAGE_BUCKETS .................. 1
STORAGE_OBJECTS .................. 732
PUBLIC_VIEWS ..................... 16
PUBLIC_FUNCTIONS ................. 20
PUBLIC_POLICIES .................. 0
PUBLIC_TABLES_WITH_ROWS .......... 19        LINHAS TOTAIS: 1.932
SUPABASE_DEVELOPMENT_BRANCHES .... 0
```

As 19 tabelas com dado, exatas: `catalogo_produto_cultivo` 711 · `raw_asset` 245 ·
`catalogo_termo_ambiguo` 210 · `catalogo_produto_agente` 176 ·
`catalogo_produto_documento` 147 · `catalogo_registro_crosswalk` 108 ·
`registro_regulatorio` 96 · `catalogo_produto_substancia` 73 · `catalogo_produto` 56 ·
`catalogo_produto_claim` 35 · `catalogo_produto_cultivo_dose` 26 ·
`catalogo_produto_modo_acao` 17 · `schema_migracao` 17 ·
`catalogo_produto_cultivo_agente` 5 · `collection_run` 4 ·
`catalogo_produto_janela_aplicacao` 3 · `catalogo_captura` 1 ·
`catalogo_produto_relacao` 1 · `catalogo_produto_tecnologia` 1

**Não fui eu que rodei.** Está registrado como medição externa, e o que **não** veio está
declarado: a lista de schemas, a de tabelas, o histórico de migration e a versão do banco.

---

## 2 · O VEREDITO

```
EXISTING_PROJECT_AVAILABLE   = YES
EXISTING_PROJECT_SAFE_AS_DEV = NO
DEV_INSTANCE_AVAILABLE       = NO
```

Dois bloqueios, ambos medidos:

```
732 objetos em storage — arquivo guardado é dado de alguém
19 tabelas com linha — 1.932 linhas ao todo
```

**`AUTH_USERS = 0` não liberou nada.** Zero usuário é verdade e não muda o veredito: o que
bloqueia é o dado, não o cadastro.

O projeto existente fica **intocado**: não aplicar migration, não limpar, não apagar, não
reutilizar como sandbox.

---

## 3 · O INVENTÁRIO REAL ACHOU UM BUG NO MEU CLASSIFICADOR

Vieram **contagens**, não as listas de schema e tabela. O classificador tinha uma guarda
que respondia primeiro:

> inventário incompleto → `NEEDS_DECISION`

E com isso ele devolveu **"precisa decidir"** para um projeto com **732 arquivos e 1.932
linhas medidos lá dentro**.

A ordem estava errada. **Evidência que bloqueia vence a incompletude:**

> *"Não sei tudo, mas sei que há 732 arquivos"* é **NÃO**, não é "precisa decidir".

Corrigido: os bloqueios são avaliados primeiro; a guarda de completude só vale quando
**nada** bloqueia — que é onde a ausência de informação poderia virar um `YES` indevido. E
quando há bloqueio com inventário parcial, o artefato registra que o veredito **não depende
do que falta**.

---

## 4 · TRÊS ACHADOS QUE NÃO FORAM PEDIDOS

**`PUBLIC_POLICIES = 0` com 19 tabelas contendo dado.** Sem política, o acesso depende de
RLS estar desligada ou de `GRANT`. Num projeto Supabase, tabela sem RLS fica legível pela
chave anônima. **Não é meu projeto e não mexi** — mas é um fato medido que alguém precisa
olhar.

**Os nomes são do domínio SINTONIA:** `catalogo_produto`, `registro_regulatorio`,
`raw_asset`, `collection_run`. Isto não parece um projeto alheio; parece uma implementação
**anterior ou paralela do próprio SINTONIA**. Se for, o dado lá dentro pode ter valor, e a
relação dele com o modelo canônico desta rodada é uma **pergunta em aberto** — não uma
coincidência de nome. Não resolvi por palpite.

**`schema_migracao = 17`.** O projeto tem história de migration própria. É isso que sustenta
a recomendação abaixo.

---

## 5 · O ALVO DEV: DUAS OPÇÕES, UMA RECOMENDAÇÃO, NENHUMA ESCOLHA

`DEV_TARGET_STRATEGY = NEEDS_DECISION` · `DEV_TARGET_CREATED = NO`

### A · Development Branch do projeto existente

**Exige:** plano com branching, projeto ligado a um repositório Git, custo por branch aceito.

**Contra, e é medido:** a branch nasce do pai — e o pai tem **17 migrations aplicadas** e
**19 tabelas com dado**. A migration canônica pousaria sobre um schema que **não está
limpo**, que é exatamente o que o meu próprio classificador marca como *"não pode assumir
banco limpo"*. E o requisito *"não carregar dado de produção automaticamente"* ficaria
dependendo de configuração, em vez de ser garantido pela origem.

**A favor:** nasce ligada ao projeto real e some quando a branch some.

### B · Novo projeto Supabase DEV separado

**A favor, e é medido:** nasce vazio **por construção** — nenhum dado de produção pode vir
junto porque não há de onde vir. Nenhuma história de migration para colidir. E o isolamento
não depende de configuração: depende de ser outro projeto.

**Contra:** mais um projeto para manter, e outro conjunto de chaves para guardar.

### Recomendação: **B**

> **Não é preferência: é o inventário.** 17 migrations e 19 tabelas com linha. Uma branch
> herdaria as duas coisas. Um projeto novo começa vazio porque não há de onde herdar.

**É recomendação. Nada foi criado.**

### O que o ambiente DEV precisa ter

```
não carregar dado de produção automaticamente — nem por cópia, nem por seed
receber SOMENTE migrations
ser explicitamente descartável: apagar e recriar não pode doer
ter PROJECT_REF próprio, diferente de odhdwvugikjdvkapbowe
nome que se leia como DEV sem precisar consultar ninguém
service role NUNCA no frontend: a chave vai para um servidor
ser identificável como DEV pelo próprio REF, não só pelo nome
```

---

## 6 · A OPÇÃO A FOI TENTADA, MEDIDA E REPROVADA

A branch foi criada com `WITH_DATA=false` e medida:

```
DEV_BRANCH = develop        DEV_BRANCH_REF = hvtycqsrdtmxxodwcwph
PARENT_PROJECT_REF = odhdwvugikjdvkapbowe          STATUS = ACTIVE_HEALTHY

PUBLIC_TABLES_WITH_ROWS ... 0        STORAGE_OBJECTS ... 0        AUTH_USERS ... 0
PUBLIC_TABLES ............ 51        PUBLIC_VIEWS .... 16         PUBLIC_FUNCTIONS ... 20
PUBLIC_POLICIES .......... 0         public.schema_migracao EXISTS = YES
```

**`WITH_DATA=false` barrou o dado e não barrou o schema.** A branch chegou sem uma linha
sequer — e com 51 tabelas, 16 views, 20 funções e a tabela de migrations do pai.

```
DEV_BRANCH_DATA_EMPTY ....................... YES
DEV_BRANCH_SCHEMA_CLEAN ..................... NO
DEV_BRANCH_SAFE_FOR_CANONICAL_MIGRATION ..... NO
```

A branch fica **intocada**: não aplicar a migration, não limpar, não dar `DROP` para abrir
espaço, não adaptar a migration ao schema legado. E não tocar no parent.

### E isso achou um segundo bug meu — o mesmo erro, do outro lado

Rodei meu próprio classificador contra esta medição antes de escrever qualquer coisa. Ele
respondeu **`YES`**.

Ele media **dado**: usuário, arquivo, linha. Zero em todos os três. Mas *vazio de dado* não
é *limpo de schema* — são **duas perguntas**, e eu só estava fazendo uma.

> Na rodada passada eu tratei "não sei tudo" como se fosse "está vazio".
> Nesta, tratei "não tem dado" como se fosse "está limpo". É o mesmo erro virado do avesso.

Corrigido. O classificador agora responde as duas separado, e a migration exige as duas:

```
DATA_EMPTY = YES   ·   SCHEMA_CLEAN = NO   →   SAFE_FOR_CANONICAL_MIGRATION = NO
```

`public` estava na minha lista de "schema de sistema" — e está certo, todo Postgres tem um.
Mas **tabela dentro de `public` não vem com o Postgres: alguém criou.** Era por aí que as 51
passavam sem serem vistas.

### O alvo saiu do código

`preparar_aplicacao()` tinha o REF do **parent** escrito dentro dele como alvo. Era um alvo
errado esperando a hora de ser usado. Agora quem aplica informa o REF, e o portão **recusa**
os dois já medidos:

```
odhdwvugikjdvkapbowe   parent: 732 objetos em storage, 19 tabelas com dado
hvtycqsrdtmxxodwcwph   branch develop: 51 tabelas herdadas e public.schema_migracao
```

---

## 7 · A BATERIA DE VALIDAÇÃO EXISTE, ESCRITA PARA RODAR SOZINHA

Não há banco limpo e não há credencial aqui. Em vez de descrever o que *deveria* ser testado,
o teste está escrito em SQL: `supabase/validation/0002_dev_validation.sql`, gerado por
`scripts/supabase_dev_validation.py`.

**44 verificações — e as 27 que valem são as negativas.** Contar tabela prova que o `CREATE`
correu; só a **linha recusada** prova que a lei pega. Cada negativa tenta inserir algo
proibido e marca `PASS` **quando o banco recusa**:

```
prazo de expiração declarado como retirada          média sem o n
prazo autorizando decisão de negócio                localidade em texto carregando ponto
perna dependente sem dizer de quem depende          perna independente apontando para outra
publicação sem a sombra aprovada                    proveniência misturando GitHub e Supabase
língua fora do vocabulário · língua igual a `—`     portfólio local marcado como evidência
expertise provada sem evidência                     voz de pessoa identificada antes do GDPR
… e mais 15
```

As 17 positivas contam e derivam: 57 tabelas, 13 views, 5 funções, 27 vocabulários, RLS nas
57, isolamento nos três países, um objeto com cinco idiomas e o original preservado,
proveniência que chega no commit `d7b2894…` do H2, e `allowed_countries()` devolvendo vazio
por padrão — porta fechada até alguém abrir.

**Tudo dentro de uma transação que termina em `ROLLBACK`.** O banco sai como entrou.

**Ordem:** inventário → migration → validação. O inventário roda **primeiro**, no DEV novo —
foi ele que reprovou o parent e teria reprovado a branch.

---

## 8 · SAÍDA

```
EXISTING_SUPABASE_PROJECT    = eame-sintonia · odhdwvugikjdvkapbowe · eu-west-1 · ACTIVE_HEALTHY
EXISTING_PROJECT_AVAILABLE   = YES
EXISTING_PROJECT_SAFE_AS_DEV = NO

EXISTING_STORAGE_OBJECTS = 732
PUBLIC_TABLES_WITH_ROWS  = 19        (1.932 linhas)
PUBLIC_VIEWS = 16   PUBLIC_FUNCTIONS = 20   PUBLIC_POLICIES = 0   AUTH_USERS = 0

DEV_BRANCH_REF = hvtycqsrdtmxxodwcwph
DEV_BRANCH_DATA_EMPTY = YES   DEV_BRANCH_SCHEMA_CLEAN = NO
DEV_BRANCH_SAFE_FOR_CANONICAL_MIGRATION = NO

CLAUDE_LOCAL_SUPABASE_ACCESS = NO
DEV_INSTANCE_AVAILABLE       = NO

DEV_TARGET_STRATEGY = NEW_PROJECT      (a opção A foi tentada e medida)
DEV_TARGET_CREATED  = NO
DEV_PROJECT_REF     = (aguardando REF limpo)

MIGRATION_APPLIED_DEV = NO      REAL_DATA_PUBLISHED = NO
DEV_VALIDATION_SUITE = 44 verificações escritas · NOT_EXECUTED

READY_TO_APPLY_MIGRATION_DEV = NO
READY_FOR_FIRST_SHADOW_LOAD  = NO
```

### Preservado

```
H2_FIXED_COMMIT = YES    H2_COMMIT_SHA = d7b289425c5e436f3ce68e367b8706e11910f43b
MIGRATION_REVIEW = PASS  VIEWS_IMPLEMENTED = 13   RPCS_IMPLEMENTED = 4
PUBLISHER_DRY_RUN = PASS PUBLISHER_IDEMPOTENCY_TEST = PASS
SHADOW_VALIDATOR_READY = YES
FIRST_SHADOW_LOAD_EXECUTED = NO   V8_WIRED = NO   PRODUCTION_DEPLOY = NO
```

### Incompletudes herdadas, ainda abertas

```
H3 sem artefato resolvido — quatro candidatos, nenhum com 36 de nada
manifesto de rótulos de H2 com três versões — nenhuma escolhida
```

Continuam **exatamente** como registradas. Não escondidas, não resolvidas por palpite.

### `EXACT_BLOCKERS`

```
1  NEW CLEAN DEV PROJECT REQUIRED
   é o bloqueador exato. Os dois alvos existentes foram medidos e reprovados:
   o parent por dado, a branch por schema. O portão recusa os dois pelo REF.

2  quem aplica é quem tem a credencial
   o portão recusa enquanto CLAUDE_LOCAL_SUPABASE_ACCESS for NO

3  pergunta aberta: o que é o dado do projeto existente?
   os nomes são do domínio SINTONIA. Se for implementação anterior, a relação
   dele com o modelo canônico precisa de resposta — de alguém, não de palpite
```
