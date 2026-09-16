# MODELO DE PROMOÇÃO DA INTELLIGENCE AGRÍCOLA — V1

```
MISSAO     C-INT-AGRO-BENCH-01
ESPECIE    MODELO CANDIDATO, DERIVADO DE BENCHMARK — NAO IMPLEMENTA NADA
MEDIDO_EM  2026-09-13
```

> O enunciado manda **tentar derrubar** a hipótese SINTONIA, não confirmá-la.
> Isto é o resultado dessa tentativa.

---

## 0 · A HIPÓTESE EM JULGAMENTO

```
OBSERVED SIGNAL -> CORROBORATED -> HYPOTHESIS -> VALIDATED IMPLICATION
                -> ACTIONABLE OPPORTUNITY
```

**Veredito: sobreviveu na forma, falhou na completude.**

A cadeia real da EFSA/JRC/ANSES tem a mesma silhueta, e tem **quatro coisas**
que a hipótese não tem:

| a EFSA tem | a hipótese SINTONIA |
|---|---|
| `IDENTITY CHECK` antes de pontuar | ausente |
| `SCREENING` barato feito **para descartar** (PeMoScoring, 15 critérios, 1 dia) | ausente |
| `EXPERT REVIEW` como etapa nomeada, não como opinião difusa | ausente |
| **reversão** de estado (ISPM 8: *records invalid*, *no longer present*) | ausente |

```
UMA MAQUINA QUE SO SABE SUBIR NAO E UMA MAQUINA DE PROMOCAO.
E UMA CATRACA.
```

---

## 1 · A CADEIA CORRIGIDA

```
        SOURCE FACT / CLAIM        (dono: COLLECTION)
              │
        [G0]  │ IDENTITY CHECK
              ▼
           SIGNAL
              │
        [G1]  │ SCREENING  (barato, feito para DESCARTAR)
              ▼
      SCREENED SIGNAL ─────────────► DISCARDED, com motivo e versão da regra
              │
        [G2]  │ CORROBORATION  (independência ANTES de convergência)
              ▼
     CORROBORATED SIGNAL
              │
        [G3]  │ HYPOTHESIS FORMATION
              ▼
          HYPOTHESIS ◄──────────────── CONTRADICTION pode voltar a pô-la aqui
              │
        [G4]  │ RISK / IMPLICATION CHARACTERISATION
              ▼
           FINDING
              │
      ┌───────┴────────┐
 [G5] │                │ [G6]
      ▼                ▼
  WATCH/FUTURE     OPPORTUNITY  (A · B · C · D — e o nível é parte do objecto)
      │                │
      └────────┬───────┘
               ▼
        RECOMMENDATION        (nunca ACTION — INT-LAW-024)
               │
               ▼
          OUTCOME LOOP ──► pode REVERTER qualquer estado acima
```

---

## 2 · AS TRANSIÇÕES, UMA A UMA

### `G0` · SOURCE FACT → SIGNAL

```
WHO OWNS            Intelligence
REQUIRED INPUTS     claim/facto com identidade propria e linhagem ao RAW
REQUIRED EVIDENCE   a ESPECIE da evidencia declarada pela fonte
                    (OBSERVED_FIELD_SIGNAL · AGROCLIMATIC_SIGNAL ·
                     REGULATORY_AUTHORIZATION · COMPANY_CLAIM · …)
HARD GATES          [1] identidade do sujeito resolvida OU o termo original
                        preservado com MATCH_TYPE = UNRESOLVED
                    [2] especie da evidencia conhecida
                    [3] FACT_TIME != PUBLISHED_AT
HUMAN REVIEW        nao
WHAT CAN BLOCK      especie desconhecida; identidade so por semelhanca textual
WHAT CAN REVERSE    a Collection corrigir o RAW; a normalizacao ser revista
EXTERNO             EFSA faz identity check antes do PeMo; ISPM 8 avalia a
                    fiabilidade do registo antes de o usar
ESTADO HOJE         ⛔ BLOQUEADO — a especie da evidencia nao atravessa a
                    fronteira (medido: ataque F)
```

### `G1` · SIGNAL → SCREENED SIGNAL

**A etapa que faltava, e é a mais barata de todas.**

```
WHO OWNS            Intelligence
REQUIRED INPUTS     criterios declarados, poucos, com resposta rapida
REQUIRED EVIDENCE   a resposta a cada criterio, visivel
HARD GATES          o rastreio tem de conseguir dizer NAO. Um rastreio que
                    nunca descarta nao e um rastreio.
HUMAN REVIEW        nao no calculo; SIM na seleccao do que entra
WHAT CAN BLOCK      criterio sem resposta -> NAO_SEI, nao «media»
WHAT CAN REVERSE    novo dado muda um criterio -> recalcula
EXTERNO             PeMoScoring: 15 criterios em 5 categorias (hospedeiro,
                    entrada, estabelecimento, dispersao, impacto), phi de -1 a
                    +1, resposta «ate um dia apos a primeira recolha»; e quando
                    ha varias opcoes, o perito escolhe «o resultado intermedio
                    mais plausivel, para evitar pressupostos extremos»
⚠️ E O QUE NAO SE COPIA  o phi NAO e o julgamento. E o bilhete de entrada.
                    INT-LAW-093: score nao substitui decomposicao.
```

### `G2` · SIGNAL → CORROBORATED SIGNAL

```
WHO OWNS            Intelligence
REQUIRED INPUTS     >= 2 evidencias
REQUIRED EVIDENCE   O GRAFO DE DEPENDENCIA, antes da contagem
HARD GATES          [1] origens independentes — e «independente» prova-se:
                        mesmo ensaio? mesmo dataset? mesmo grupo? um cita o
                        outro? mesma ONPF?
                    [2] compatibilidade TEMPORAL (mesma janela)
                    [3] compatibilidade GEOGRAFICA (mesma area, mesma escada)
                    [4] compatibilidade SEMANTICA (mesmo organismo, mesma
                        cultura, metodos comensuraveis)
HUMAN REVIEW        nao, se as quatro chaves existirem
WHAT CAN BLOCK      falta de chave de juncao (INT-LAW-091)
WHAT CAN REVERSE    descobrir que as duas fontes tinham a mesma origem
EXTERNO             392 -> 27 na EFSA: a repeticao E o sinal, e a maioria nao
                    repete. E MIAPPE/BrAPI dao as chaves para distinguir
                    replica de fonte nova.
ESTADO HOJE         ⛔ BLOQUEADO — sem metodo, unidade e identidade no READY,
                    a compatibilidade semantica nao e testavel
```

### `G3` · SIGNAL → HYPOTHESIS

```
WHO OWNS            Intelligence (+ agronomo, quando o dominio for tecnico)
REQUIRED INPUTS     sinal corroborado OU um sinal unico de autoridade alta
REQUIRED EVIDENCE   a pergunta a que a hipotese responde (INT-LAW-090)
                    as PREMISSAS, explicitas (INT-LAW-034)
HARD GATES          a hipotese tem de ser FALSIFICAVEL: escreve-se o que a
                    derrubaria
HUMAN REVIEW        recomendavel
WHAT CAN BLOCK      hipotese que nada derruba
WHAT CAN REVERSE    a evidencia contraria aparecer
LEI                 INT-LAW-035: hipotese NAO vira facto por repeticao
```

### `G4` · HYPOTHESIS → FINDING

```
WHO OWNS            Intelligence, com revisao humana obrigatoria em dominio
                    regulatorio, fitossanitario e comercial
REQUIRED INPUTS     hipotese + evidencia + premissas + contraditorio
REQUIRED EVIDENCE   DECISION TRACE auditavel (INT-LAW-038):
                    claims usados · arestas de suporte e contradicao ·
                    premissas · alternativas materiais · regra/prompt
                    versionados · gates e estados
HARD GATES          [1] a evidencia contraria esta ligada, nao omitida
                    [2] o NIVEL esta declarado (disease levels; opportunity A-D)
                    [3] a incerteza esta declarada, e nao e um numero sozinho
HUMAN REVIEW        SIM
WHAT CAN BLOCK      alto impacto + alta incerteza sem alternativas
                    (INT-LAW-124)
WHAT CAN REVERSE    dado novo; regra nova; o registo de origem ser invalidado
EXTERNO             ISPM 8: determinar o estado de uma praga e juizo da
                    autoridade, nao a soma dos registos
```

### `G5` · FINDING → WATCH / FUTURE

```
WHO OWNS            Intelligence
REQUIRED INPUTS     achado + HORIZONTE + condicao de revisao
HARD GATES          [1] o horizonte e explicito
                    [2] existe um GATILHO — o que faria isto voltar a mesa
                    [3] FUTURE_DATE != FUTURE INTELLIGENCE: uma caducidade e
                        um facto presente, e vive noutra prateleira
WHAT CAN REVERSE    o gatilho disparar; o horizonte passar sem nada acontecer
EXTERNO             a newsletter mensal da EFSA E este estado: publicada,
                    datada, revisitavel — e a maioria dos itens morre la
```

### `G6` · FINDING → OPPORTUNITY

**A transição mais perigosa, e por isso a que tem mais portões.**

```
WHO OWNS            Intelligence propoe; MARKET DEVELOPMENT valida
REQUIRED INPUTS     achado + janela + portfolio + dono da decisao
REQUIRED EVIDENCE   a tupla de uso de PPP que sustenta a resposta
HARD GATES          [1] O NIVEL (A · B · C · D) esta declarado E provado
                    [2] a JANELA existe e e compativel:
                        fenologia ∩ janela de infeccao ∩ janela de aplicacao do
                        rotulo ∩ janela de preparacao comercial
                    [3] para nivel B: o uso autorizado cobre
                        (cultura, alvo, pais) — nao basta o produto existir
                    [4] para nivel C ou D: dado interno ADAMA, com contrato
HUMAN REVIEW        OBRIGATORIA
WHAT CAN BLOCK      registo caducado; janela fechada; nivel nao provado
WHAT CAN REVERSE    revogacao; alteracao de rotulo; a janela passar
LEI                 INT-LAW-144: produto para cultura != produto para alvo
                    INT-LAW-145: estrutura nao inventa pressao de campo
ESTADO HOJE         ⛔ BLOQUEADO acima do nivel A — a tupla de uso de PPP nao
                    existe como objecto nesta casa
```

---

## 3 · O QUE PODE FAZER ANDAR PARA TRÁS

O benchmark obriga esta secção, e ela não existia.

| reversão | quem a dispara | exemplo agro |
|---|---|---|
| `RECORD_INVALIDATED` | a autoridade | ISPM 8: *«pest records invalid»* — o registo era falso |
| `NO_LONGER_PRESENT` | a autoridade | praga erradicada; a área volta a *pest free* |
| `NORMALIZATION_REVISED` | nós | a EPPO reclassifica; o nosso `MATCH_TYPE` muda |
| `SOURCE_RETRACTED` | a fonte | boletim corrigido; paper retratado |
| `DEPENDENCY_DISCOVERED` | nós | as «duas fontes» eram a mesma ONPF |
| `AUTHORIZATION_CHANGED` | o regulador | o uso deixou de existir → a oportunidade morre |
| `WINDOW_CLOSED` | o tempo | a janela passou → deixa de ser accionável, e **não** deixa de ser verdade |

```
UM OBJECTO QUE NAO SABE DESPROMOVER-SE ACUMULA MENTIRAS
NA VELOCIDADE A QUE O MUNDO MUDA.
E NO AGRO O MUNDO MUDA TODAS AS CAMPANHAS.
```

---

## 4 · HUMAN-IN-THE-LOOP — E A AUTONOMIA NÃO É BINÁRIA

O enunciado pede cinco graus. O benchmark dá-os, e a literatura de 2026 dá o
critério de escalão:

> *«sinais de baixo risco permanecem automatizados, alertas de risco médio
> desencadeiam recolha adicional de dados, e cenários de alta consequência
> escalam para peritos»* — e o desenho separa explicitamente **output do
> modelo** de **gatilho da acção**.

| grau | onde é aceitável, no agro | onde **não** é |
|---|---|---|
| `AI CAN SUMMARIZE` | sempre, com a fonte ao lado | — |
| `AI CAN DERIVE` | normalizar termo, ligar EPPO, calcular janela | decidir que a normalização ambígua é uma só |
| `AI CAN RECOMMEND` | propor hipótese, propor crossing, propor rastreio | recomendar aplicação de produto |
| `AI CAN PROMOTE` | `G0`, `G1`, `G2` — se os portões forem duros | `G4`, `G6` |
| `AI CAN ACT` | **em nada**, nesta V1 | tudo |

E os donos humanos, por domínio:

```
AGRONOMO              G3, G4 em doenca/praga; a regua de nivel
PERITO REGULATORIO    G4 e G6 em rotulo e autorizacao
MARKET DEVELOPMENT    G6 acima do nivel A
VALIDACAO DE CAMPO    o loop de outcome, e so ele fecha
```

**E a lei que impede o abuso do carimbo humano** já existe
(`INT-LAW-172`), e o benchmark confirma-a: a EFSA usa perito para **escolher
entre opções plausíveis**, não para transformar ausência de dado em dado.

```
HUMAN APPROVAL NAO TRANSFORMA BASE FRACA EM FACTO.
UM PERITO A CARIMBAR UM NIVEL 1 NAO PRODUZ UM NIVEL 4.
```

---

## 5 · O LOOP DE RESULTADO, SEM FABRICAR CAUSALIDADE

Quatro estados, e a distância entre eles é a honestidade do sistema:

```
FOLLOWED              alguem abriu, leu, guardou           MEDIVEL HOJE
ACTIONED              alguem declarou ter agido            MEDIVEL, se se perguntar
OUTCOME OBSERVED      houve observacao de campo depois     EXIGE dado de campo
OUTCOME ATTRIBUTABLE  o resultado deve-se a isto           EXIGE DESENHO EXPERIMENTAL
```

O que a literatura acrescenta, e que é mais útil do que «funcionou»:

```
LEAD TIME             o aviso chegou antes de a janela fechar?
CALIBRACAO            a confianca declarada bate com a realidade?
CARGA DE FALSOS       quantos alertas falsos por alerta util?
AVISOS FALHADOS       quantos surtos reais nao foram avisados?
```

```
ESTES QUATRO MEDEM-SE SEM DADO DE CAMPO, E SO O TERCEIRO E O QUARTO
EXIGEM ALGUEM A DIZER O QUE ACONTECEU.
COMECAR PELOS DOIS PRIMEIROS E O CAMINHO BARATO E HONESTO.
```

E a proibição:

```
INT-LAW-213: o resultado posterior NAO reescreve o julgamento passado.
Um achado que estava certo com a evidencia de Maio continua a ter estado certo
em Maio, mesmo que Junho o desminta. Reescreve-lo apaga a unica serie que
permitiria calibrar.
```

---

## 6 · VEREDITO

```
PROMOTION_MODEL_READY = NO
```

Não porque o modelo esteja errado — sobreviveu ao ataque e ficou mais completo —
mas porque **três dos sete portões estão bloqueados na matéria-prima**:

```
G0  bloqueado   a especie da evidencia nao atravessa a fronteira
G2  bloqueado   sem metodo/unidade/identidade, a compatibilidade semantica
                nao e testavel
G6  bloqueado   a tupla de uso de PPP nao existe como objecto
```

E porque **nenhuma das sete reversões tem hoje onde ser escrita**.

```
UM MODELO DE PROMOCAO SO FICA PRONTO QUANDO OS SEUS PORTOES CONSEGUEM
RECUSAR — E UM PORTAO QUE NAO RECEBE O DADO NAO RECUSA: DEIXA PASSAR.
```
