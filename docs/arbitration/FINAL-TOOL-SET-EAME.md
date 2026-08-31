# FINAL TOOL SET — SINTONIA EAME V8

**Data:** 2026-08-31 · decisão fechada · **não implementado**

---

## O CONJUNTO

```
PRIMARY   Visão Geral / Atenção   ·  Radar de Atenção  ·  Object Detail
          Camada EAME             ·  Relatórios

SUPPORT   Acervo                  ·  Fontes

ADMIN     Sistema                 ·  Config
```

**Nove superfícies.** O V7 tinha doze itens de navegação; três foram absorvidos e nenhuma
função se perdeu.

---

## 1 · PRIMARY

### VISÃO GERAL / ATENÇÃO

**Pergunta:** *o que merece atenção agora?*
Mostra **prioritariamente `ATTENTION_READY`**. Pode mostrar `ATTENTION_CANDIDATE_TEST`
**com rótulo explícito de teste**. Nunca mostra `VALID_EVIDENCE_NOT_ATTENTION_READY` como
se fosse atenção.

> **Se a fila estiver vazia, diz que está vazia.** Fila vazia é resultado, não falha de
> interface. Hoje, com o refresh corrigido: `ATTENTION_READY = 0`.

Mantém: estado da fundação por país · estado da coleta · porta da camada EAME.

### RADAR DE ATENÇÃO

**Evolução do `Radar/Casos` do V7 — nome novo, identidade preservada.** Abriga os **quatro
tipos de objeto**, não quatro dashboards.

**Absorve o Radar do Futuro como estado/view:**

```
FORMING          o objeto está se formando; falta evidência
WATCH            evidência válida, sem gatilho ainda
NEEDS_EVIDENCE   o bloqueador exato está nomeado
FUTURE           relevante para ciclo futuro
```

**Filtros que continuam do V7:** linha ADAMA · país. **Filtro novo obrigatório:**
`OBJECT_TYPE` — sem ele o usuário não distingue um vencimento de um caso de campo.

### OBJECT DETAIL — **composição modular por tipo**

Fortalecido, e é aqui que mora a decisão mais fina do V8.

| tipo | blocos |
|---|---|
| **PHENOMENON_CASE** | Campo · Ciência · Competição · Portfólio local · Pessoas · **Tempo** · Ação · Unknowns · Evidência |
| **REGULATORY_DEADLINE** | Registro · Titular · Prazo · Ação · Evidência |
| **COMPETITOR_IDENTITY_CHAIN** | Marca · Registro local · Atividade paga observada · Evidência |
| **LONGITUDINAL_FIELD_PRESSURE** | Série · Baseline · Coorte · Backtest · Evidência |

> **Um `REGULATORY_DEADLINE` não finge ter camada de Ciência.** Blocos ausentes **não
> aparecem vazios**: o tipo simplesmente não os tem, e isso é `NOT_APPLICABLE`.

**Absorve `Análises`:** a leitura estruturada (`FACT` / `INTERPRETATION` / `ACTION`) vive
dentro do objeto, com proveniência preservada. Não é mais uma tela onde se escolhe um
"modelo de leitura" solto.

**Absorve `Janelas da Cultura`** como bloco de tempo — ver `FINAL-CADENCE-MODEL-EAME.md`.

### CAMADA EAME

Inalterada na função: comparação, convergência e coordenação entre mercados. A matriz de
comparabilidade continua a peça central.

**Muda uma coisa:** passa a comparar **objetos**, não só casos — e a matriz ganha uma
dimensão implícita, `OBJECT_TYPE`, porque nem todo tipo existe nos três países.

### RELATÓRIOS

Inalterado: snapshot · freeze · dossiê, com data de versão e rastro de evidência.

---

## 2 · SUPPORT

### ACERVO

Inalterado na função. Contrato de 13 colunas, `sha_verified`, abrir original, ver
proveniência.

### FONTES — **`STRENGTHEN`**

A única superfície de suporte que muda, e por causa de uma medição nova. Passa a separar
cinco coisas que hoje se confundem numa só:

```
SOURCE_STATUS              viva · bloqueada · com ressalva · não coletada ainda
LATEST_SOURCE_PUBLICATION  a data da última publicação da fonte
LATEST_CAPTURE             a data da última leitura nossa
OBSERVATION_AGE            idade do documento
PIPELINE_LATENCY           atraso do nosso pipeline
```

> ⚠️ **`OBSERVATION_AGE ≠ PIPELINE_LATENCY`.** A medição atual não separa as duas: houve
> **captura única**, então os dois números são idênticos por construção. Uma tela que
> chamasse idade de documento de "atraso do pipeline" estaria mentindo. Os campos existem
> **separados desde já** para que a segunda captura tenha onde cair.

---

## 3 · ADMIN

**Sistema** (biblioteca visual) e **Config** — inalterados.

---

## 4 · ABSORVIDOS — e o que aconteceu com cada função

| superfície V7 | função | onde vive agora |
|---|---|---|
| **Radar do Futuro** | *onde a evidência se acumula* | estado/view do Radar (`FORMING`/`WATCH`/`NEEDS_EVIDENCE`/`FUTURE`) |
| **Janelas da Cultura** | *ainda dá tempo?* | bloco de tempo no Object Detail, com os sete relógios separados |
| **Análises** | *o que dá para afirmar, e até onde* | leitura dentro do Object Detail, com proveniência |

```
RADAR_FUTURE_STANDALONE = NO      CULTURE_WINDOWS_STANDALONE = NO
ANALYSES_STANDALONE = NO          CREATOR_MAP_STANDALONE_V8 = NO
```

**Por que absorver e não matar.** Cada uma respondia uma pergunta real; nenhuma tinha dado
suficiente para sustentar uma superfície própria. `Janelas da Cultura` é o caso mais claro:
era a segunda tela mais elaborada do V7 e a mais vazia — **fenologia existe em 3 de 22
itens, e só do momento da observação**. Uma tela de tempo bonita e vazia é o convite mais
direto que este produto tem para alguém preencher com estimativa.

---

## 5 · CREATOR MAP — fora da navegação, dentro do produto

```
CREATOR_MAP_STANDALONE_V8 = NO        STATE = TEST_AS_CAPABILITY
```

Disponível de forma **contextual e buscável**: a partir de um objeto de atenção, ou por
busca `cultura + região`.

**A promoção a ferramenta depende de uso real**, e o uso será instrumentado:

```
ENTRY_PATH = FROM_ATTENTION_OBJECT       ou       FROM_CROP_REGION_SEARCH
```

Se o Marketing chegar quase sempre pela segunda porta, é ferramenta. Se chegar pela
primeira, é camada. **A decisão fica com o dado de uso, não com a estética** — e é a única
decisão de produto deste conjunto que foi deliberadamente adiada com um teste desenhado.

---

## 6 · O QUE NÃO SE CONSTRÓI

```
META_DASHBOARD
dashboard regulatório
Radar Regulatório / Radar Meta / Radar Foresight / Radar Campo como quatro superfícies
audit dashboard de "o que falta provar"
ranking de especialista
qualquer score agregado
```

Seis proibições, cada uma com prova que reprova quem as apagar.
