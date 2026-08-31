# V8 · ESPECIFICAÇÃO DE PRODUTO — SINTONIA EAME

**Data:** 2026-08-31 · **especificação fechada** · `V8_IMPLEMENTATION_STARTED = NO`

> Esta é a especificação. A ordem de implementar virá **separada**.

---

## 0 · O QUE O V8 HERDA E O QUE NÃO HERDA

```
HERDA        identidade visual ADAMA · gramática visual · tokens e componentes
             a hierarquia que ainda faz sentido
             as leis de saída: FACT / INTERPRETATION / ACTION separados
             ausência declarada como ausência

NÃO HERDA    a ontologia de um tipo único de CASE
```

**V7 continua testemunha byte a byte** (`SHA-256 a31ea184…87c6a`). O V8 é versão nova; a
anterior não se destrói.

---

## 1 · NAVEGAÇÃO

```
INTEL       Visão Geral / Atenção     ·  Radar de Atenção
EVIDÊNCIA   Acervo                    ·  Fontes
LEITURA     Relatórios
CAMADA      EAME
ADMIN       Sistema                   ·  Config
```

Fora do rail, alcançáveis: **Object Detail** (a partir do Radar) e a **camada EAME** (pelo
seletor de país).

**Barra superior** inalterada: marca · seletor de país (ES · IT · FR + EAME) · campo de
pergunta · seletor de idioma (5) · perfil.

**A lei de país continua escrita na interface:** *dados de um país nunca aparecem dentro de
outro; cruzamentos só na camada EAME, e apenas nas dimensões declaradas comparáveis.*

---

## 2 · VISÃO GERAL / ATENÇÃO

**Uma pergunta manda:** *o que merece atenção agora?*

```
BLOCO 1   fila de ATTENTION_READY
          se vazia → dizer que está vazia, com o motivo
BLOCO 2   candidatos em teste, com ROTULO EXPLÍCITO
BLOCO 3   estado da fundação por país
BLOCO 4   estado da coleta (última leitura, portões, freeze, mudanças)
BLOCO 5   porta da camada EAME
```

**Proibido na home:** contador de fontes · contador de linhas · "buzz" · score de influência
· qualquer número que não mude uma decisão.

**Novo, e obrigatório:** o card de fila mostra o **`OBJECT_TYPE`**. Sem isso o usuário não
distingue um vencimento de um caso de campo — e essa confusão foi o defeito do V7.

---

## 3 · RADAR DE ATENÇÃO

Evolução do `Radar/Casos`. Abriga os **quatro tipos**.

**Filtros:**

```
OBJECT_TYPE        ← novo e obrigatório
PAÍS               ES · IT · FR
LINHA ADAMA        Disease · Weed · Pest · Crop Enhancement   (só onde aplicável)
ESTADO             FORMING · WATCH · NEEDS_EVIDENCE · FUTURE
                   ATTENTION_CANDIDATE_TEST · ATTENTION_READY · ARCHIVED
JANELA             só onde o tipo tem janela
```

> **`LINHA ADAMA` e `JANELA` não se aplicam a todos os tipos.** Um vencimento não tem linha
> de produto no sentido do card; um `IDENTITY_CHAIN` não tem janela agronômica. O filtro
> **desaparece** para o tipo em que não faz sentido — não fica vazio.

**Absorve o Radar do Futuro** como estados `FORMING` / `WATCH` / `NEEDS_EVIDENCE` / `FUTURE`.

**O card do radar mostra, para todo tipo:** `OBJECT_TYPE` · país · estado de atenção ·
**bloqueador exato** quando não estiver pronto · data da evidência mais recente.

**O bloqueador exato é a novidade que mais serve ao usuário.** Hoje o acervo produz coisas
como *"falta REGION em 3 itens franceses"* e *"falta ISSUE em 10 itens espanhóis"* — e são
filas diferentes que o V7 mostrava como uma só.

---

## 4 · OBJECT DETAIL — composição modular

**O detalhe se adapta ao tipo.** Blocos que o tipo não tem **não aparecem**.

### PHENOMENON_CASE

```
Cabeçalho        país · região · cultura · problema · estado · tipo
Síntese          FACT / INTERPRETATION / ACTION separados
Camadas          Campo · Ciência · Competição · Portfólio local · Pessoas
Tempo            os sete relógios, cada um com seu estado
Cruzamentos      o que liga a outros objetos
Ação             mapa por departamento, com ACTION_TYPE
Unknowns         o que ainda não sabemos
Evidência        gaveta com o original — nunca a tradução
Histórico        mudanças de estado do objeto
```

### REGULATORY_DEADLINE

```
Cabeçalho   país · registro · produto · titular · prazo · estado
Registro    número, titular, status COMO A FONTE DECLARA
Prazo       a data, e o que ela autoriza (REVIEW) e o que não autoriza (ALERT)
Ação        REGULATÓRIO e PORTFÓLIO
Unknowns    se a renovação está em curso — dado interno, que não virá
Evidência   a linha do registro oficial
```

**Sem camada de Campo, Ciência ou Pessoas.** Não é omissão: é `NOT_APPLICABLE`.

### COMPETITOR_IDENTITY_CHAIN

```
Cabeçalho          competidor · país · produto normalizado · estado
Marca              escritório, data de depósito, status
Registro local     número, titular, grupo
Atividade paga     anúncios observados — com os sete "não pode afirmar" visíveis
Concordância       META == MARCA == REGISTRO, e o portão URBOLE
Evidência          as três pontas
```

### LONGITUDINAL_FIELD_PRESSURE

```
Cabeçalho   país · região · cultura · problema · estado
Série       leituras por safra, sempre com o n
Baseline    o tipo de baseline e seu limite
Coorte      controle de amostragem
Backtest    disparos, falsos positivos e a conclusão honesta
Evidência   o artefato da fonte
```

**Absorve `Análises`:** a leitura estruturada vive aqui, com proveniência.

---

## 5 · O BLOCO DE TEMPO

Substitui `Janelas da Cultura` como superfície. Sete campos que **nunca se fundem**:

```
OBSERVATION_TIME · STAGE_AT_OBSERVATION · CURRENT_CROP_STAGE · LABEL_USE_STAGE
APPLICATION_WINDOW · REGULATORY_DEADLINE · FUTURE_SEASON_WINDOW
```

**Resolução declarada** — herdada do V7 e mantida:
`DATA EXATA · SEMANA · MÊS · FASE FENOLÓGICA · ESTAÇÃO · NÃO CONHECIDA (sem barra)`.

> **A interface nunca desenha precisão que o dado não tem.** E não projeta a janela de uma
> safra sobre a seguinte.

---

## 6 · CAPABILITIES CONTEXTUAIS

**Creator** — sem navegação própria. Acessível a partir do objeto ou por busca
`cultura + região`. Instrumentar `ENTRY_PATH`.
`PERSON_CREATOR ≠ FARM_BUSINESS`; a soma nunca se chama `CREATORS_READY`.

**Expert** — dentro do `PHENOMENON_CASE`, bloco Pessoas.
**Portão obrigatório `ISSUE_EXPERTISE_PROVED` antes de apresentar alguém como especialista
do problema.** Lista **sem ordem**. GDPR antes de qualquer exposição.

**Unknown** — estado transversal em todo objeto. Nunca superfície.

---

## 7 · MULTILÍNGUE E ÍCONES

```
ATTENTION_OBJECT_ID = LANGUAGE_NEUTRAL
contrato 1443f643 preservado integralmente
UI por dicionário i18n — nunca IA em runtime para menu, botão, filtro ou estado
conteúdo com proveniência de tradução e VER ORIGINAL sempre presente

DISEASE_ID → OFFICIAL_ADAMA_DISEASE_ICON_ID
DISEASE_ICON_CROSSWALK = NOT_MEASURED — medir no design system durante o desenho
não criar substituto genérico
```

---

## 8 · DEFINITION OF DONE DO V8

```
NAVIGATION_WORKS ..................... todas as superfícies abrem
OBJECT_TYPE_VISIBLE .................. o tipo aparece em toda lista e todo detalhe
MODULAR_DETAIL ....................... blocos ausentes NÃO aparecem vazios
COUNTRY_ISOLATION .................... nenhuma evidência atravessa país
EVIDENCE_OPENABLE .................... toda afirmação abre no original
ATTENTION_GATE_ENFORCED .............. os cinco requisitos, em código
EMPTY_QUEUE_HONEST ................... fila vazia se mostra vazia
NO_FABRICATED_WINDOW ................. nenhuma janela sem fonte
NO_SCORE ............................. nenhum score agregado
GUARDS_IN_CODE ....................... os guards do mapa de mangueiras, com teste
MULTILINGUAL_RESPECTED ............... um objeto, várias representações
```

---

## 9 · O QUE O V8 NÃO CONSTRÓI

```
META_DASHBOARD · dashboard regulatório · audit dashboard
quatro radares separados · ranking de especialista · score agregado
navegação primária de Creator
```

---

## 10 · BLOQUEADORES PARA A IMPLEMENTAÇÃO

Nenhum impede começar; todos precisam estar escritos na tela quando o dado faltar:

```
1  cultura × alvo ausente nos 3 registros nacionais
2  24 dos 163 rótulos italianos ausentes do disco
3  corpo completo dos documentos territoriais NÃO preservado (só 3.000 caracteres)
4  captura única: nenhum OBJECT_SPECIFIC_TRIGGER pode disparar hoje
5  corpus científico só espanhol — expertise IT e FR fica NOT_READY
6  conteúdo das 22 contas de concorrente NOT_STARTED
7  DISEASE_ICON_CROSSWALK NOT_MEASURED
8  REGULATORY_DEADLINE só existe para a Itália neste acervo
```

**O item 4 é o mais importante:** com `ATTENTION_READY = 0`, o V8 nasce com a fila vazia.
**Isso é aceitável e previsto** — a fila vazia se mostra vazia, com o motivo. O que não é
aceitável é preenchê-la para a tela não ficar pobre.
