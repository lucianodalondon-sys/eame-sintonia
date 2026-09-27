# MOTOR INTELLIGENCE V2 — REQUISITOS CANÔNICOS

> Documento canônico de requisitos futuros do Motor Intelligence V2.
>
> Este arquivo existe porque decisões estruturais estavam vivendo apenas em
> conversas e em relatórios de missão. Relatório de missão descreve o que
> aconteceu numa rodada. Este documento declara a **lei** que vale para as
> próximas rodadas.
>
> Regra de uso: nenhum item aqui pode ser silenciosamente contornado por
> implementação. Se a implementação não consegue cumprir, o caminho é abrir
> item em `BACKLOG-OBRIGATORIO.md` — não relaxar o requisito.

---

## 0. ESTATUTO DO DOCUMENTO

**O que este documento é:**

- contrato de requisitos do Motor Intelligence V2;
- fonte de verdade sobre gates, estados e proibições;
- base contra a qual `MOTOR_V2_READY` é julgado.

**O que este documento NÃO é:**

- relatório de execução;
- inventário de dados;
- documentação de portal;
- promessa de que algo já está implementado.

**Princípio geral que atravessa todas as seções:**

O motor pode dizer `UNKNOWN`. O motor não pode transformar `UNKNOWN` em fato
para destravar produção. Um estado desconhecido declarado é um resultado
válido; um estado desconhecido disfarçado de `PASS` é defeito.

---

## 1. OPPORTUNITY — CRUZAMENTO GLOBAL DO ACERVO

**Requisito obrigatório.**

Uma Opportunity **não pode nascer** apenas de um arquétipo mínimo, nem de uma
seleção precoce de produto.

Para cada Opportunity, o motor deve consultar **todas as famílias de
inteligência relevantes disponíveis** para a mesma combinação factual,
conforme aplicável:

- `PAÍS`
- `CULTURA`
- `ALVO / PROBLEMA`
- `REGIÃO`
- `TEMPO`

### 1.1 Famílias a consultar (quando existirem)

- sinais de campo / boletins
- portfólio ADAMA
- rótulos ministeriais / regulatório
- concorrência
- ciência
- resistência / modo de ação
- mercado / economia
- clima
- fenologia / janelas
- eventos
- notícias
- pesquisadores
- técnicos
- creators / vozes públicas
- vídeos
- transcrições
- histórico
- geografia
- regulatório futuro
- eventos futuros
- sinais futuros
- relações / crossings
- qualquer outra família presente no acervo

### 1.2 Estado obrigatório por família

Cada família consultada deve terminar **explicitamente** em um destes estados:

| Estado | Significado |
|---|---|
| `MATCH` | a família respondeu à combinação factual pedida |
| `CROP_ONLY` | há resposta para a cultura, mas não para o par cultura × alvo |
| `NOT_FOUND` | consultada, nada encontrado no universo lido |
| `UNKNOWN` | não foi possível determinar |
| `MATERIAL_EXISTENTE_NAO_UTILIZAVEL` | há material, mas o conteúdo não é utilizável como prova |

### 1.3 Proibição

**Nunca** considerar uma família como consultada apenas porque a coleção
existe. Existência de coleção não é consulta. Consulta é a produção de um dos
estados acima, registrada e rastreável.

### 1.4 Gate

```
CROSS_INTELLIGENCE_GATE = PASS / FAIL
```

`FAIL` quando qualquer família aplicável não terminar em estado explícito.

---

## 2. PORTFÓLIO ADAMA COMPLETO POR OPPORTUNITY

Para toda Opportunity:

1. identificar `PAÍS` + `CULTURA`;
2. consultar **TODOS** os produtos ADAMA conhecidos para essa cultura no país;
3. para cada produto, classificar:

| Classificação | Significado |
|---|---|
| `LIGADO_A_OPORTUNIDADE` | ligação provada com o caso |
| `NAO_LIGADO` | ausência de ligação estabelecida |
| `NAO_SEI` | não há base para decidir |

4. **nenhuma exclusão pode ser silenciosa**;
5. produto para cultura **NÃO** implica produto para alvo;
6. catálogo/rótulo **não contam** como fonte de campo independente;
7. **não chamar produto de "solução"** sem prova do par cultura × alvo.

### 2.1 Contabilidade obrigatória

A conta precisa fechar:

```
PRODUTOS_ENCONTRADOS = LIGADOS + NAO_LIGADOS + NAO_SEI
```

Se a soma não fecha, houve exclusão silenciosa.

### 2.2 Gate

```
OPPORTUNITY_PORTFOLIO_COMPLETENESS = PASS / FAIL
```

---

## 3. CASOS-TESTEMUNHA OBRIGATÓRIOS

Casos-testemunha não são exemplos ilustrativos. São **fixtures de regressão**:
o motor precisa continuar acertando neles a cada mudança.

### 3.1 VITE / VITE DA VINO / VINE

O motor precisa tratar explicitamente a normalização entre:

- `VITE`
- `Vite da vino`
- `VINE`

E precisa analisar **separadamente**:

- `Vite da tavola`

quando a equivalência exigir prova adicional.

**Proibição:** não normalizar apenas por semelhança textual.

**Caso medido:**

```
VITE_DA_VINO_TOTAL_PRODUCTS = 71
```

Esse `71` é **união de múltiplas casas de dados**. Só pode ser exigido quando
as casas necessárias estiverem de fato ingeridas. Exigir `71` sobre um universo
parcial produz `FAIL` correto, não meta a ser burlada.

**Regra derivada:** produto disponível para `VITE` **não é automaticamente**
produto indicado para o problema do cartão.

### 3.2 EXELGROW

`EXELGROW` deve poder ser encontrado como produto **candidato/contextual**
quando a cultura e o contexto justificarem.

Mas:

```
agricoltura biologica != controle biológico de doença
```

E `EXELGROW` **não pode** ser afirmado como tratamento de botrite sem prova
factual do par cultura × alvo.

### 3.3 MAIS / MILHO / MAIZE / CORN

Segundo caso-testemunha obrigatório.

**Regra:** volume de publicidade concorrente é sinal de **atenção comercial**,
**NÃO** prova de necessidade agronômica.

**Caso factual:**

```
MAIS × PIRALIDE × FRIULI-VENEZIA GIULIA
```

deve preservar:

- sinal de campo;
- limiar declarado;
- região;
- produtos ADAMA do par;
- `janela = UNKNOWN` se não houver registro factual.

---

## 4. CONVERGÊNCIA NÃO É SÓ CONTAGEM

Métricas obrigatoriamente **separadas**:

```
EXTERNAL_SIGNAL_COUNT
INDEPENDENT_SOURCE_COUNT
STRUCTURAL_VALIDATION_COUNT
INTELLIGENCE_FAMILY_COUNT
```

Catálogo, rótulo e registro ministerial são **validações estruturais**.
Não são três fontes externas independentes.

**Proibição explícita:**

Uma Opportunity com

```
1 fonte de campo + 3 validações estruturais
```

**não pode** ser apresentada como

```
4 fontes independentes
```

---

## 5. RADAR FUTURO

**Requisito obrigatório:** o Radar Futuro deve usar o **mesmo princípio de
consulta global do acervo** definido na seção 1.

Data matemática sozinha **não cria** oportunidade futura.

### 5.1 Estados mínimos

```
FATO_FUTURO_CONFIRMADO
SINAL_PARA_PREPARACAO
HIPOTESE_MONITORAR
NAO_SEI
```

### 5.2 Regras

- data futura **não é** oportunidade;
- janela de cultura **não é** recomendação;
- história **não prova** repetição;
- forecast **não é** fato;
- subtração entre datas **não prova** ação;
- ação futura precisa de **evidência** ou **dependência declarada**.

### 5.3 Estado medido

```
FUTURE_RADAR_INPUT_FAMILIES = 0 de 26
FUTURE_RADAR_CROSS_INTELLIGENCE_GATE = FAIL
```

Esse estado permanece no backlog como **reconstrução obrigatória**. Não é
defeito cosmético: o Radar Futuro atual não consulta o acervo.

---

## 6. IDENTIDADE GLOBAL DE CLAIM

Toda afirmação factual consumida pelo motor precisa ter identidade:

- globalmente única;
- determinística;
- reproduzível;
- rastreável;
- **diferente** quando o conteúdo factual for diferente.

### 6.1 Proibições

É proibido `CLAIM_ID` baseado apenas em:

- posição em lista;
- contador local;
- ordem de processamento.

### 6.2 Gate

```
CLAIM_ID_COLLISIONS = 0
```

**Input vazio nunca pode gerar `PASS`.** Zero colisões sobre zero claims não é
prova de identidade — é prova de que nada foi lido (ver seção 17).

---

## 7. HISTÓRICO APPEND-ONLY

Correções de:

- identidade;
- vínculo;
- estado;

**não reescrevem o passado.**

Devem **acrescentar eventos** e permitir reconstrução de:

```
HISTORICAL_STATE
ACTIVE_STATE
```

### 7.1 Órfãos

Órfão sem prova:

```
RECOVERY_STATE = ORPHANED / UNRECOVERABLE
```

**Nunca escolher dono provável por inferência.** Um órfão declarado é
recuperável depois; um órfão adotado pelo dono errado contamina a cadeia.

---

## 8. ESTADO DA EVIDÊNCIA

Separar obrigatoriamente quatro eixos:

| Campo | Significado |
|---|---|
| `EVIDENCE_CLASS` | natureza |
| `EVIDENCE_STATE` | estado factual |
| `EVIDENCE_STRENGTH` | força / confiança |
| `EVIDENCE_REASON` | explicação humana |

### 8.1 Invariante

```
PROVED + razão semanticamente UNKNOWN  =>  IMPOSSÍVEL
```

Se o estado é `PROVED`, a razão precisa dizer **o que** prova. Uma razão vazia,
genérica ou semanticamente desconhecida sob estado `PROVED` é contradição de
estado e deve falhar o gate.

---

## 9. FAMÍLIAS — NÃO EXISTE `FAMILY_ID` GENÉRICO

Separar três conceitos que hoje colidem num campo só:

| Campo | Significado |
|---|---|
| `EVIDENCE_FAMILY` | natureza da evidência |
| `DATASET_FAMILY` | onde o dado mora |
| `SOURCE_FAMILY` | método / origem de coleta |

**Não fundir os três.** Um `FAMILY_ID` genérico destrói a capacidade de
responder "isto é uma segunda fonte ou é o mesmo dado lido de outro lugar?".

---

## 10. UNIVERSOS SEMÂNTICOS

**Decisão canônica:**

> Universo é definido pela **pergunta que responde**.
> Universo **NÃO** é uma pasta.

Manter distintos:

```
UNIVERSE_PASSAPORTE
UNIVERSE_ACERVO_IT
UNIVERSE_EXECUCOES
```

`data/samples` é **diretório físico** e **NÃO** deve virar automaticamente
universo canônico.

---

## 11. `UNIVERSE_PASSAPORTE`

`UNIVERSE_PASSAPORTE` é o universo que bloqueia:

```
PASSPORT_READY
```

Requisitos:

- precisa ser derivado de **regra canônica de inclusão**;
- lista histórica de arquivos **não basta**;
- o passaporte **NÃO** precisa cobrir todo `data/samples`.

Enquanto a regra de inclusão não existir, o universo é declarado por
enumeração herdada — e isso é dívida registrada, não estado aceitável.

---

## 12. `UNIVERSE_ACERVO_IT`

### 12.1 Achado registrado

Três contagens anteriores foram **reproduzidas**:

| Leitura | FILES | RECORDS | COLLECTIONS |
|---|---|---|---|
| A | 141 | 9.438 | 0 |
| B | 101 | 8.770 | 35 |
| C | 164 | 29.694 | 82 |

Causas provadas incluíram:

- `WRONG_PATH`
- `STALE_OWNER`
- `COLLECTION_FILTER`
- `DUPLICATE_COUNT`
- `GENERATED_FILE_INCLUDED`
- `BUG` latente

### 12.2 Convergência posterior

Dois leitores independentes convergiram em:

```
FILES         = 178
RECORDS       = 17.612
COLLECTIONS   = 116
UNKNOWN_KEYS  = 51

FINGERPRINT = ca4ceca25cd4762ba91f69ba360349cf313f7724ce02e613d274d72d0acf3f91
```

### 12.3 Estado canônico

```
UNIVERSE_ACERVO_IT_CANONICAL = NÃO
```

**Motivo:** 37 chaves novas / 7.512 registros ainda exigem decisão do dono.

**Proibição:** não transformar esse estado em `PASS`. Convergência entre dois
leitores prova que a leitura é reprodutível — não prova que o universo está
decidido.

---

## 13. `UNIVERSE_EXECUCOES`

É universo de **proveniência**.

Hoje declara **forma/estrutura** da execução, não extensão quantitativa
completa.

**Regra atual:** não bloquear `PASSPORT_READY` por quantidade enquanto esse
contrato não existir.

**Regra futura:** se houver claim de completude de execuções, criar:

```
EXPECTED_EXECUTIONS
EXPECTED_FINGERPRINT
```

e gate próprio.

---

## 14. COMPLETUDE EXIGE UNIVERSO DECLARADO

Toda capability que afirma:

```
COMPLETE
FULL_SCAN
ZERO
NOT_FOUND
```

deve declarar:

```
WHICH_UNIVERSE
UNIVERSE_OWNER
INCLUSION_RULE
EXPECTED_EXTENT
SCANNED_EXTENT
EXPECTED_FINGERPRINT
SCANNED_FINGERPRINT
COMPLETENESS_STATE
```

Se `EXPECTED_UNIVERSE` não existir:

```
UNIVERSE_COMPLETENESS = FAIL / UNKNOWN
```

**Nunca `PASS`.**

---

## 15. ZERO NÃO É AUSÊNCIA

Distinguir obrigatoriamente:

| Estado | Significado |
|---|---|
| `ZERO_PROVED` | provado que não existe no universo declarado |
| `NOT_FOUND_IN_SCANNED_UNIVERSE` | não apareceu no que foi lido |
| `UNIVERSE_INCOMPLETE` | o universo lido não é o universo esperado |
| `NOT_QUERIED` | não foi consultado |
| `MATERIAL_NOT_USABLE` | há material, mas não é utilizável |
| `UNKNOWN` | indeterminado |

> "não apareceu no que eu li"
>
> **não significa**
>
> "não existe".

---

## 16. CAPABILITY MAP

A relação:

```
CAPABILITY -> CASE / CLAIM / EVIDENCE
```

tem **um único dono canônico**, na camada de inteligência/prova.

- o portal apenas **renderiza**;
- o portal **não pode reconstruir** essa relação.

Toda reconstrução no portal é uma segunda verdade e diverge da primeira.

---

## 17. GATES PRECISAM SABER FALHAR

Todo gate crítico precisa ser testado contra:

- input vazio
- arquivo ausente
- universo divergente
- claim inexistente
- claim duplicado
- órfão tratado como provado
- estado contraditório
- fingerprint divergente

**Regra:** gate que dá `PASS` sobre entrada vazia é **inválido**.

Um gate que nunca falhou não está provado — está não testado.

---

## 18. NORMALIZAÇÃO ANTES DE BACKFILL

**Nenhum backfill em massa** enquanto identidades equivalentes puderem
divergir.

Casos-testemunha:

```
VITE
VINE
Vite da vino
["VINE"]
```

Estado:

```
FULL_BACKFILL = NO
```

enquanto a normalização não estiver provada. Backfill sobre identidade não
normalizada multiplica o erro em vez de corrigi-lo.

---

## 19. PRESSÃO DE DOENÇA — FERRAMENTA FUTURA

**Requisito experimental do Motor V2.**

Unidade factual:

```
REGIÃO × CULTURA × PROBLEMA × DATA
```

**Tempo faz parte da identidade do sinal.**

### 19.1 Separação obrigatória

```
DISEASE_PRESSURE_SIGNAL != COMMERCIAL_OPPORTUNITY
```

### 19.2 Para virar Opportunity

Outra camada precisa provar:

- produto ADAMA;
- cultura;
- alvo;
- região;
- tempo / janela;
- demais gates comerciais.

### 19.3 Estado atual

```
DISEASE_PRESSURE_TOOL = NOT_YET
```

até certificação independente.

---

## 20. MAPA DE AÇÕES

Somente **cinco áreas canônicas**:

```
MARKETING
COMMERCIAL / SALES
MARKET DEVELOPMENT
TECHNICAL / SCIENCE
SUPPLY
```

### 20.1 Regra

**Ausência de evidência não gera recomendação.**

Pode gerar:

- dependência declarada;
- investigação;
- `UNKNOWN`.

Ação futura apenas com prova ou regra correspondente.

---

## 21. GATE FINAL DO MOTOR V2

Antes de:

```
MOTOR_V2_READY = YES
```

exigir **pelo menos**:

```
CLAIM_ID_COLLISIONS             = 0
ROUTES_TO_MISSING_CLAIMS        = 0
UNEXPLAINED_ORPHANS             = 0
EVIDENCE_STATE_CONTRADICTIONS   = 0
EXPECTED_UNIVERSE_DECLARED      = YES
UNIVERSE_COMPLETENESS           = PASS nos universos exigidos
OPPORTUNITY_PORTFOLIO_COMPLETENESS = PASS
CROSS_INTELLIGENCE_GATE         = PASS
BACKLOG_REVIEWED                = YES
```

### 21.1 Regra final

`UNKNOWN` crítico continua **visível**.

**Nunca converter `UNKNOWN` em fato para liberar produção.**

---

## REFERÊNCIA CRUZADA

Dívida e ações obrigatórias antes de `MOTOR_V2_READY`:
[`BACKLOG-OBRIGATORIO.md`](./BACKLOG-OBRIGATORIO.md)
