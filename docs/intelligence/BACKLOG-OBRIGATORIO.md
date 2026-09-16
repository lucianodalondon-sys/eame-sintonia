# BACKLOG OBRIGATÓRIO — MOTOR INTELLIGENCE V2

> Dívida e ações obrigatórias **antes** de `MOTOR_V2_READY = YES`.
>
> Contrato de requisitos: [`MOTOR-INTELLIGENCE-V2-REQUIREMENTS.md`](./MOTOR-INTELLIGENCE-V2-REQUIREMENTS.md)

---

## REGRAS DO BACKLOG

### Status permitidos

```
OPEN
IN_PROGRESS
BLOCKING
DONE
DEFERRED_COM_MOTIVO
NOT_APPLICABLE
```

`DEFERRED_COM_MOTIVO` **precisa** declarar:

- `MOTIVO`
- `RISCO`
- `CONDIÇÃO_DE_RETOMADA`

Adiamento sem os três campos não é adiamento — é omissão.

### Campos de cada item

| Campo | Uso |
|---|---|
| `ID` | identificador estável `INTEL-V2-NNN`, nunca reciclado |
| `STATUS` | estado de trabalho (lista acima) |
| `BLOCKING_PRODUCTION` | se impede `MOTOR_V2_READY = YES` |
| `REQUISITO` | seção correspondente no documento de requisitos |
| `GATE` | gate/medida que fecha o item |

### Gate de revisão

Antes de `MOTOR_V2_READY = YES`:

```
BACKLOG_REVIEWED = YES
```

Qualquer item com `STATUS = BLOCKING`, ou **item não classificado**,
impede `YES`.

### Estado atual

```
BACKLOG_ITEMS_TOTAL = 22
BLOCKING_PRODUCTION_SIM = 19
BACKLOG_REVIEWED = NÃO
MOTOR_V2_READY = NÃO
```

---

## ITENS

### INTEL-V2-001 — Opportunity: cruzamento global do acervo

- **STATUS:** BLOCKING
- **BLOCKING_PRODUCTION:** SIM
- **REQUISITO:** seção 1
- **GATE:** `CROSS_INTELLIGENCE_GATE = PASS`

Opportunity não pode nascer de arquétipo mínimo nem de seleção precoce de
produto. Toda família aplicável ao par `PAÍS × CULTURA × ALVO × REGIÃO × TEMPO`
precisa terminar em `MATCH` / `CROP_ONLY` / `NOT_FOUND` / `UNKNOWN` /
`MATERIAL_EXISTENTE_NAO_UTILIZAVEL`. Existência de coleção não conta como
consulta.

---

### INTEL-V2-002 — Portfólio ADAMA completo por Opportunity

- **STATUS:** BLOCKING
- **BLOCKING_PRODUCTION:** SIM
- **REQUISITO:** seção 2
- **GATE:** `OPPORTUNITY_PORTFOLIO_COMPLETENESS = PASS`

Consultar todos os produtos ADAMA da cultura no país e classificar cada um em
`LIGADO_A_OPORTUNIDADE` / `NAO_LIGADO` / `NAO_SEI`. A conta
`PRODUTOS_ENCONTRADOS = LIGADOS + NAO_LIGADOS + NAO_SEI` precisa fechar.
Nenhuma exclusão silenciosa. Produto para cultura não implica produto para alvo.

---

### INTEL-V2-003 — Corrigir 656 relações produto × cultura do catálogo

- **STATUS:** BLOCKING
- **BLOCKING_PRODUCTION:** SIM
- **REQUISITO:** seções 2 e 18
- **GATE:** relações revisadas com origem declarada; nenhuma relação derivada só de texto

656 relações produto × cultura do catálogo precisam de correção. Enquanto não
corrigidas, a completude de portfólio da seção 2 herda o erro do catálogo.

---

### INTEL-V2-004 — Normalização VITE / Vite da vino / VINE

- **STATUS:** BLOCKING
- **BLOCKING_PRODUCTION:** SIM
- **REQUISITO:** seções 3.1 e 18
- **GATE:** `FULL_BACKFILL = NO` até normalização provada

Normalizar `VITE` / `Vite da vino` / `VINE` sem usar semelhança textual como
prova, e tratar `Vite da tavola` separadamente quando a equivalência exigir
prova adicional. Caso medido: `VITE_DA_VINO_TOTAL_PRODUCTS = 71`, exigível
apenas quando as casas de dados necessárias estiverem ingeridas.

---

### INTEL-V2-005 — Reconstruir Radar Futuro com cruzamento do acervo

- **STATUS:** BLOCKING
- **BLOCKING_PRODUCTION:** SIM
- **REQUISITO:** seção 5
- **GATE:** `FUTURE_RADAR_CROSS_INTELLIGENCE_GATE = PASS`

Estado medido: `FUTURE_RADAR_INPUT_FAMILIES = 0 de 26`,
`FUTURE_RADAR_CROSS_INTELLIGENCE_GATE = FAIL`. Reconstrução obrigatória com os
estados `FATO_FUTURO_CONFIRMADO` / `SINAL_PARA_PREPARACAO` /
`HIPOTESE_MONITORAR` / `NAO_SEI`. Data futura não é oportunidade; forecast não
é fato; subtração entre datas não prova ação.

---

### INTEL-V2-006 — Separar métricas de convergência

- **STATUS:** BLOCKING
- **BLOCKING_PRODUCTION:** SIM
- **REQUISITO:** seção 4
- **GATE:** nenhuma Opportunity soma validação estrutural como fonte independente

Expor `EXTERNAL_SIGNAL_COUNT`, `INDEPENDENT_SOURCE_COUNT`,
`STRUCTURAL_VALIDATION_COUNT` e `INTELLIGENCE_FAMILY_COUNT` separadamente.
1 fonte de campo + 3 validações estruturais não é "4 fontes independentes".

---

### INTEL-V2-007 — Histórico append-only e órfãos declarados

- **STATUS:** BLOCKING
- **BLOCKING_PRODUCTION:** SIM
- **REQUISITO:** seção 7
- **GATE:** `UNEXPLAINED_ORPHANS = 0`

Correções de identidade, vínculo e estado acrescentam eventos e não reescrevem
o passado. `HISTORICAL_STATE` e `ACTIVE_STATE` reconstrutíveis. Órfão sem prova
vira `RECOVERY_STATE = ORPHANED / UNRECOVERABLE` — nunca dono provável por
inferência.

---

### INTEL-V2-008 — Gates precisam saber falhar

- **STATUS:** BLOCKING
- **BLOCKING_PRODUCTION:** SIM
- **REQUISITO:** seção 17
- **GATE:** suíte adversarial verde em todos os cenários negativos

Testar todo gate crítico contra: input vazio, arquivo ausente, universo
divergente, claim inexistente, claim duplicado, órfão tratado como provado,
estado contraditório, fingerprint divergente. Gate que dá `PASS` sobre entrada
vazia é inválido.

---

### INTEL-V2-009 — Dono canônico do CAPABILITY MAP

- **STATUS:** BLOCKING
- **BLOCKING_PRODUCTION:** SIM
- **REQUISITO:** seção 16
- **GATE:** `ROUTES_TO_MISSING_CLAIMS = 0` e zero reconstrução no portal

A relação `CAPABILITY -> CASE / CLAIM / EVIDENCE` tem um único dono na camada
de inteligência/prova. O portal apenas renderiza e não pode reconstruir a
relação.

---

### INTEL-V2-010 — ZERO não é ausência

- **STATUS:** BLOCKING
- **BLOCKING_PRODUCTION:** SIM
- **REQUISITO:** seção 15
- **GATE:** nenhum `ZERO` publicado sem estado discriminado

Distinguir `ZERO_PROVED`, `NOT_FOUND_IN_SCANNED_UNIVERSE`,
`UNIVERSE_INCOMPLETE`, `NOT_QUERIED`, `MATERIAL_NOT_USABLE`, `UNKNOWN`.
"Não apareceu no que eu li" não significa "não existe".

---

### INTEL-V2-011 — Canonizar identidade global de CLAIM

- **STATUS:** BLOCKING
- **BLOCKING_PRODUCTION:** SIM
- **REQUISITO:** seção 6
- **GATE:** `CLAIM_ID_COLLISIONS = 0` (input vazio nunca gera `PASS`)

Identidade globalmente única, determinística, reproduzível, rastreável e
diferente quando o conteúdo factual for diferente. Proibido `CLAIM_ID` baseado
em posição em lista, contador local ou ordem de processamento.

---

### INTEL-V2-012 — Declarar universos esperados e fingerprints

- **STATUS:** BLOCKING
- **BLOCKING_PRODUCTION:** SIM
- **REQUISITO:** seções 10 e 14
- **GATE:** `EXPECTED_UNIVERSE_DECLARED = YES` e `UNIVERSE_COMPLETENESS = PASS` nos universos exigidos

Toda capability que afirma `COMPLETE` / `FULL_SCAN` / `ZERO` / `NOT_FOUND` deve
declarar `WHICH_UNIVERSE`, `UNIVERSE_OWNER`, `INCLUSION_RULE`,
`EXPECTED_EXTENT`, `SCANNED_EXTENT`, `EXPECTED_FINGERPRINT`,
`SCANNED_FINGERPRINT`, `COMPLETENESS_STATE`. Sem `EXPECTED_UNIVERSE`:
`FAIL / UNKNOWN`, nunca `PASS`.

---

### INTEL-V2-013 — Separar EVIDENCE_CLASS / STATE / STRENGTH / REASON

- **STATUS:** BLOCKING
- **BLOCKING_PRODUCTION:** SIM
- **REQUISITO:** seção 8
- **GATE:** `EVIDENCE_STATE_CONTRADICTIONS = 0`

Quatro eixos distintos: natureza, estado factual, força/confiança e explicação
humana. `PROVED` com razão semanticamente `UNKNOWN` deve ser impossível.

---

### INTEL-V2-014 — Separar EVIDENCE_FAMILY / DATASET_FAMILY / SOURCE_FAMILY

- **STATUS:** BLOCKING
- **BLOCKING_PRODUCTION:** SIM
- **REQUISITO:** seção 9
- **GATE:** nenhum `FAMILY_ID` genérico em uso

Natureza da evidência, onde o dado mora e método/origem de coleta são três
campos. Não fundir. Sem essa separação não é possível responder se uma segunda
leitura é uma segunda fonte.

---

### INTEL-V2-015 — Canonizar UNIVERSE_PASSAPORTE por regra

- **STATUS:** BLOCKING
- **BLOCKING_PRODUCTION:** SIM
- **REQUISITO:** seção 11
- **GATE:** `INCLUSION_RULE` declarada e `PASSPORT_READY` derivado dela

`UNIVERSE_PASSAPORTE` é o universo que bloqueia `PASSPORT_READY` e precisa vir
de regra canônica de inclusão. Lista histórica de arquivos não basta. O
passaporte não precisa cobrir todo `data/samples`.

---

### INTEL-V2-016 — Reconciliar 37 chaves / 7.512 registros de UNIVERSE_ACERVO_IT

- **STATUS:** BLOCKING
- **BLOCKING_PRODUCTION:** SIM
- **REQUISITO:** seção 12
- **GATE:** decisão do dono registrada; só então `UNIVERSE_ACERVO_IT_CANONICAL` pode mudar

Dois leitores independentes convergiram em `FILES = 178`,
`RECORDS = 17.612`, `COLLECTIONS = 116`, `UNKNOWN_KEYS = 51`,
`FINGERPRINT = ca4ceca25cd4762ba91f69ba360349cf313f7724ce02e613d274d72d0acf3f91`.
Mesmo assim `UNIVERSE_ACERVO_IT_CANONICAL = NÃO`, porque 37 chaves novas /
7.512 registros ainda exigem decisão do dono. Não converter em `PASS`.

---

### INTEL-V2-017 — Extensão quantitativa de UNIVERSE_EXECUCOES

- **STATUS:** DEFERRED_COM_MOTIVO
- **BLOCKING_PRODUCTION:** NÃO
- **REQUISITO:** seção 13
- **GATE:** nenhum enquanto adiado

- **MOTIVO:** `UNIVERSE_EXECUCOES` é universo de proveniência e hoje declara
  forma/estrutura da execução, não extensão quantitativa completa. Não existe
  contrato de completude a cumprir.
- **RISCO:** se alguma capability passar a afirmar completude de execuções sem
  contrato, o `ZERO` dela será indistinguível de `NOT_QUERIED`.
- **CONDIÇÃO_DE_RETOMADA:** surgir qualquer claim de completude sobre
  execuções. Nesse momento criar `EXPECTED_EXECUTIONS`,
  `EXPECTED_FINGERPRINT` e gate próprio, e reclassificar este item.

Enquanto adiado: não bloquear `PASSPORT_READY` por quantidade de execuções.

---

### INTEL-V2-018 — Proibir data/samples como universo semântico implícito

- **STATUS:** BLOCKING
- **BLOCKING_PRODUCTION:** SIM
- **REQUISITO:** seção 10
- **GATE:** nenhum universo derivado de caminho físico

Universo é definido pela pergunta que responde, não por pasta. `data/samples` é
diretório físico e não pode virar automaticamente universo canônico.

---

### INTEL-V2-019 — Integrar vídeos/transcrições só quando o conteúdo for utilizável

- **STATUS:** DEFERRED_COM_MOTIVO
- **BLOCKING_PRODUCTION:** NÃO
- **REQUISITO:** seções 1 e 15
- **GATE:** enquanto adiado, estas famílias reportam `MATERIAL_EXISTENTE_NAO_UTILIZAVEL`

- **MOTIVO:** existe material de vídeo/transcrição no acervo cujo conteúdo
  ainda não é utilizável como prova factual. Ingerir agora produziria volume
  sem evidência.
- **RISCO:** contagem de famílias consultadas subir sem que a evidência suba —
  exatamente o erro que a seção 4 proíbe.
- **CONDIÇÃO_DE_RETOMADA:** conteúdo utilizável verificado (transcrição
  legível, atribuível e datada). Só então essas famílias podem produzir
  `MATCH` no cruzamento da seção 1.

Enquanto adiado, o estado precisa aparecer explicitamente — família não
utilizável não é família ausente.

---

### INTEL-V2-020 — Certificação independente da ferramenta de pressão de doença

- **STATUS:** OPEN
- **BLOCKING_PRODUCTION:** NÃO
- **REQUISITO:** seção 19
- **GATE:** `DISEASE_PRESSURE_TOOL = NOT_YET` até certificação independente

Unidade factual `REGIÃO × CULTURA × PROBLEMA × DATA`, com tempo como parte da
identidade do sinal. `DISEASE_PRESSURE_SIGNAL != COMMERCIAL_OPPORTUNITY`: para
virar Opportunity, outra camada precisa provar produto ADAMA, cultura, alvo,
região, tempo/janela e os demais gates comerciais. Não bloqueia produção
porque a ferramenta permanece fora do caminho de decisão enquanto `NOT_YET`.

---

### INTEL-V2-021 — Mapa de ações restrito a cinco áreas canônicas

- **STATUS:** BLOCKING
- **BLOCKING_PRODUCTION:** SIM
- **REQUISITO:** seção 20
- **GATE:** nenhuma recomendação emitida sem prova ou regra correspondente

Somente `MARKETING`, `COMMERCIAL / SALES`, `MARKET DEVELOPMENT`,
`TECHNICAL / SCIENCE`, `SUPPLY`. Ausência de evidência não gera recomendação —
gera dependência declarada, investigação ou `UNKNOWN`.

---

### INTEL-V2-022 — Casos-testemunha como fixtures de regressão

- **STATUS:** BLOCKING
- **BLOCKING_PRODUCTION:** SIM
- **REQUISITO:** seção 3
- **GATE:** os três casos verdes a cada mudança de motor

Três casos obrigatórios:

1. **VITE / Vite da vino / VINE** — normalização provada, `Vite da tavola`
   separado, `VITE_DA_VINO_TOTAL_PRODUCTS = 71` exigível só sobre as casas
   ingeridas, e produto disponível para `VITE` nunca tratado como indicado
   para o problema do cartão.
2. **EXELGROW** — encontrável como candidato/contextual, mas
   `agricoltura biologica != controle biológico de doença`, e nunca afirmado
   como tratamento de botrite sem prova factual.
3. **MAIS × PIRALIDE × FRIULI-VENEZIA GIULIA** — preserva sinal de campo,
   limiar declarado, região, produtos ADAMA do par e `janela = UNKNOWN` se não
   houver registro factual. Volume de publicidade concorrente é atenção
   comercial, não necessidade agronômica.

---

## FECHAMENTO

```
MOTOR_V2_READY = NÃO
BACKLOG_REVIEWED = NÃO
```

`UNKNOWN` crítico continua visível. Nenhum item deste backlog pode ser fechado
convertendo `UNKNOWN` em fato.
