# A trilha universal e o contrato de inteligência comercial

```
UNIVERSAL_INTELLIGENCE_READY = PARTIAL

AUTOMATIC_NEW_INGEST     = YES
UNIVERSAL_GATE           = YES
UNIVERSAL_TRAIL_COVERAGE = PARTIAL   ← a razão do PARTIAL
BACKFILL                 = YES
```

O veredito é **PARTIAL** e a causa está localizada, medida e contada: das dez
famílias da porta real de coleta, **duas nunca entram no pacote**, e uma delas
— `HERBICIDE_CURRENT_CONTEXT`, **16 registros reais** — não é papel de trabalho:
são janelas correntes de aplicação declaradas pelo serviço fitossanitário
regional. É a causa medida de `WHY_NOW = ACT_NOW` ser **impossível** em todo o
pacote hoje.

Antes desta missão isso não estava errado no papel: estava **invisível**.

    UM REGISTRO QUE ENTRA PELA PORTA E NÃO SAI EM LUGAR NENHUM NÃO FOI
    RECUSADO: ELE DESAPARECEU. E DESAPARECER É PIOR QUE SER RECUSADO.

---

## 1 · branch e HEAD

| | |
|---|---|
| branch de trabalho | `claude/trilha-universal-inteligencia-a5rx9d` |
| base canônica da inteligência | `claude/opportunity-commercial-priority-v1` · `0ddf52d` |
| BUILD_ID de partida | `V21-5c847ef25e17f680` · 43 oportunidades · 6.882 no mestre |
| BUILD_ID de chegada | `V21-45dc1a181224bbf7` · 43 oportunidades · 6.882 no mestre |

⚠️ **A branch designada estava na linhagem errada.** Ela apontava para
`claude/sintonia-eame-repo-setup-xccfob` — a linha de *setup* do repositório,
com 53 scripts e nenhum motor de oportunidades. A cadeia V2.1, o Opportunity
Engine e o Commercial Priority vivem na outra linhagem. A branch foi
re-baseada em `0ddf52d` **sem perder commit nenhum**: ela não tinha commit
próprio, era um ponteiro para o HEAD de outra branch.

    DESENVOLVER INTELIGÊNCIA NA BRANCH QUE NÃO TEM A INTELIGÊNCIA É COMEÇAR
    CRIANDO O SEGUNDO DONO.

Duas linhagens divergem de `84f0375` e continuam divergentes — não foram
mescladas aqui:

- `claude/opportunity-commercial-priority-v1` — a **inteligência** (esta);
- `claude/site-v21-ingest-recovery` — o **portal** (`italia-portale/`, 93
  auditorias contra 41). Não foi tocada.

---

## 2 · a trilha real encontrada

Existe **uma** cadeia obrigatória, e ela tem um arquivo: `scripts/v21_cadeia.sh`.
Nada no repositório chama o motor de oportunidades fora dela — `grep -rn
v21_oportunidades.py` devolve **um** chamador executável.

```
PORTA D1  build/ITALY-REALITY-HANDOFF-V2/CANONICAL-INTELLIGENCE.json  (10 famílias)
PORTA D2  research/italy-lastmile/NEW-REAL-SOURCES.json
PORTA D3  data/samples/IT-LASTMILE/ · IT-ISTAT-COLTIVAZIONI/ · IT-V2/
PORTA D4  research/adama-italy-product-intelligence-deep/
PORTA D5  build/ITALY-REALITY-HANDOFF-V2/PREVIOUS-HANDOFF/01-DESIGN-READY/
   ↓
1   v21_ingest{,_b,_c}.py     identidade · proveniência · normalização · classificação
2   v21_crossings.py          cruzamentos
3   v21_vozes_reconciliar.py  §13
4   v21_carimbar_origem.py    origem, sem default silencioso
5   v21_fontes_*.py           fontes rechaveadas e cadastradas
5b  v21_procedencia_religar   procedência
5c  v21_contrato_do_pacote    rota
5d  v21_dominio_da_alegacao   domínio da alegação
5e  v21_oportunidades.py      régua da missão · janela · portfólio · Opportunity Engine
                              + v21_necessidade (direção) + v21_comercial (Commercial Priority)
6   v21_traducao_trava.py     tradução
6b  v21_dominio_da_alegacao   pós-tradução
6c  v21_catraca.py       ←NOVO  a catraca: estados de publicação
6d  v21_briefing.py      ←NOVO  o contrato de inteligência comercial
7   v21_fechar.py             fechamento
8   v21_aceitacao.py          aceitação  ←AGORA É PORTÃO
9   contratos de geografia e procedência
```

**Nenhum segundo dono foi criado.** Cada decisão continua com quem já a tinha, e
os dois arquivos novos declaram o dono ao lado de cada valor derivado:

| decisão | dono | inalterado |
|---|---|---|
| direção da necessidade | `v21_necessidade.direcao()` | sim |
| janela e chave de janela | `v21_oportunidades.janela()` · `janela_vale()` | sim |
| portões A–H e red team | `v21_oportunidades.portoes()` · `red_team()` | sim |
| Commercial Priority | `v21_comercial.prioridade()` | sim |
| saída externa | `v21_comercial.externo()` | sim |
| catálogo × registro | `v21_comercial.casar()` | sim |

---

## 3 · AUTOMATIC_NEW_INGEST = **YES** · testemunha executável

`python3 scripts/v21_testemunha_universal.py` → **EXIT 0**

Onze fixtures, **uma por família**, injetadas nas portas **reais** e versionadas.
Nenhum script especial: a cadeia real, do começo ao fim.

```
BASELINE          V21-45dc1a181224bbf7 · 43 oportunidades · 43 fichas
COM AS FIXTURES   V21-...              · 4 oportunidades mudaram
RESTAURADO        V21-45dc1a181224bbf7 · IGUAL — sem resíduo
```

| família (origem) | entrou | catraca deu estado | mexeu em oportunidade |
|---|---|---|---|
| `CURRENT_FIELD_SIGNALS` · boletim/PDF | SIM | SIM | `OPP_5F31A63F844D` · sinais 9→10 |
| `MARKET_OBSERVATIONS` · API/mercado | SIM | SIM | — |
| `CROP_ECONOMIC_WEIGHT` · estatística | SIM | SIM | `OPP_576D71D702F0` · 2→3 linhas |
| `AGROMET_CONDITIONS` · clima | SIM | SIM | — |
| `REGULATORY_FUTURE` · regulatório | SIM | SIM | — |
| `COMPETITOR_PUBLIC_SIGNALS` · concorrente | SIM | SIM | `OPP_BCD174C535AC` · 42→43 peças |
| `PUBLIC_VOICES` · produtor/vídeo/áudio | SIM | SIM | — |
| `FUTURE_EVENTS` · evento | SIM | SIM | — |
| `COMMERCIAL_CATALOG` | **NÃO** | — | — |
| `HERBICIDE_CURRENT_CONTEXT` | **NÃO** | — | — |
| D2 · fonte nova | SIM | — | — |

**Quatro origens diferentes chegaram a quatro oportunidades diferentes**, uma
delas `PUBLISHABLE`, sem intervenção humana entre a coleta e a régua comercial.

⚠️ **Entrar no acervo e alterar uma oportunidade são duas coisas.** A missão
permite a primeira sem inteligência e proíbe a segunda. Uma fixture que entra e
não muda oportunidade nenhuma **confirma** a catraca; não a reprova.

### O defeito que a testemunha achou na própria medição

A primeira versão comparava `EVIDENCE_IDS` e disse que o boletim de botrite
«não mudou oportunidade nenhuma». Tinha mudado: o motor grava `sin[:8]` — a
lista de apoios é **cortada em oito** — e o nono sinal entra na contagem sem
entrar na citação.

    MEDIR PELO CAMPO TRUNCADO É MEDIR O TRUNCAMENTO, NÃO O FATO.

---

## 4 · UNIVERSAL_GATE = **YES** · e o que isso quer dizer exatamente

São **duas perguntas**, e respondê-las com um número só é o erro de sempre:

| pergunta | resposta |
|---|---|
| **UNIVERSAL_GATE** — algo altera uma oportunidade publicável sem passar pela inteligência? | **NÃO** (medido) |
| **UNIVERSAL_TRAIL_COVERAGE** — toda origem da porta chega até a inteligência? | **PARTIAL** |

O portão não vaza. A trilha não cobre tudo. As duas coisas são verdade.

---

## 5 · BACKFILL = **YES**

`v21_ingest.py` começa com `shutil.rmtree(OUT)`: a cadeia **apaga a saída e
refaz o acervo inteiro** a cada execução. Não existe caminho incremental — e por
isso não existe acervo velho com régua velha.

    NÃO HÁ BACKFILL PORQUE NÃO HÁ INCREMENTAL.
    A CADEIA NÃO ATUALIZA O PACOTE: ELA O REFAZ.

**A prova desta missão é melhor que a da anterior**, porque desta vez havia uma
régua nova para aplicar: as **43** oportunidades preexistentes receberam
`PUBLICATION_STATE` e ficha de briefing **na mesma execução**, sem recoletar
nada, sem duplicar registro bruto e sem apagar evidência. A testemunha mede isso
(`sem PUBLICATION_STATE: 0 · sem ficha: 0`).

E os dois caminhos — dado novo e reprocessamento — são **o mesmo caminho**: um
comando, uma ordem, os mesmos donos.

---

## 6 · Pontos de bypass encontrados

### B1 · a aceitação media violação e devolvia zero — **CORRIGIDO**

`v21_aceitacao.py` contava violações de portão de QA, contagens divergentes,
cruzamento apoiado em registro inseguro, fonte citada sem cadastro — e
terminava com `return 0`, **sempre**. A cadeia roda com `set -euo pipefail`:
quem falha para tudo. Este passo nunca falhava.

    ETAPA OBRIGATÓRIA QUE NÃO PODE REPROVAR NÃO É ETAPA: É RELATÓRIO.

Agora **11 contadores** — todos já chamados de violação pelo próprio relatório,
todos já medindo zero — reprovam a cadeia. A trava nasce verde de propósito:
trava que nasce vermelha ensina a ignorar trava.

### B2 · `classificar || true` + `medir || true` + commit — **CORRIGIDO**

`.github/workflows/comunicacao-publica.yml`, passo 4, era literalmente o padrão
que a missão manda eliminar.

    `|| true` NÃO TORNA O PASSO OPCIONAL. TORNA A FALHA INVISÍVEL.

A distinção que faltava é entre **coletar** e **concluir**. O bruto continua
sendo preservado e commitado — jogar coleta paga fora é irreversível — mas a
falha agora grava `INTELIGENCIA-FALHOU.json` com `ESTADO: VALIDATION_REQUIRED`,
e o job termina **vermelho**, num passo posterior ao push, para que a falha não
custe o dado.

### B3 · duas famílias somem na porta — **DECLARADO, NÃO CONSERTADO**

26 registros reais entram por `CANONICAL-INTELLIGENCE.json` e não existem em
coleção nenhuma. Sem erro, sem quarentena, sem estado.

| família | n | o que é | veredito |
|---|---:|---|---|
| `COMMERCIAL_CATALOG` | 10 | meta-registros **sobre** a coleta: censo do catálogo, defeito de método, divergência catálogo × registro | papel de trabalho — os produtos entram por outra porta e são os 51 de `PRODUCTS-COMMERCIAL.json` |
| `HERBICIDE_CURRENT_CONTEXT` | 16 | **janelas correntes de aplicação** por província, com ativos permitidos e derrogações de calendário | **ABERTO** — é material de campo |

Ingerir a segunda exige coleção, normalização e dono próprios. Fazê-lo de
passagem aqui criaria um segundo dono para a janela — exatamente o que a missão
proíbe. O que esta rodada fez é o mínimo honesto: **declarar, contar, e tornar
FATAL qualquer buraco novo**.

### B4 · quatro boletins reais chegam ao motor mudos — **VISÍVEL, NÃO CONSERTADO**

Herdado e já documentado em `V112-AUTOMACAO-DA-INGESTAO.md` (ABERTO 1):
`IT-CAN-71D68FCB7D`, `IT-CAN-6EFC8DC91A`, `IT-CAN-EB63AEC4AA`,
`IT-CAN-49BA29FF51` têm a leitura só em `RESEARCH.o_que`, e
`promover_research` é tudo-ou-nada. Agora carregam
`RELATION_EXTRACTION = UNKNOWN` com o código do motivo, e o teste `U6` quebra se
voltarem a sumir em silêncio. O comportamento **não** mudou; o silêncio, sim.

### B5 · dois erros meus que a medição pegou antes de virarem lei

A primeira versão do portão de aceitação pôs `LINGUA.AINDA_SO_EM_PORTUGUES` na
lista fatal. A testemunha universal mostrou o efeito imediatamente: um boletim
novo qualquer traz leitura nossa em português ainda sem irmã em italiano, e a
**cadeia inteira parava** — 7.000 registros sem fechar por causa de uma frase
por traduzir.

    LACUNA DE TRADUÇÃO NÃO É FALHA DE INTELIGÊNCIA.
    UMA TRAVA QUE IMPEDE A INGESTÃO NORMAL NÃO PROTEGE: ELA PARA.

A consequência passou a ser **do registro**, na catraca, etapa `LOCALIZATION`,
estado `UNKNOWN`. O contador continua no relatório de aceitação.

E o segundo, do mesmo tipo: a catraca nasceu no passo **5f**, *antes* da
tradução — e mediu **5.638** registros como incompletos por causa de uma
tradução que a própria cadeia ia aplicar três linhas adiante.

    MEDIR UMA ETAPA ANTES DE ELA RODAR NÃO MEDE O PACOTE: MEDE A ORDEM.

Movida para **6c**, depois da tradução e antes do fechamento, o número certo é
**42**. Os testes `U27` e `U28` fixam a ordem e o número, para que o erro não
possa voltar em silêncio.

---

## 7 · A CATRACA · `scripts/v21_catraca.py`

    DADO BRUTO NÃO É PUBLICÁVEL.
    A CATRACA SÓ SEGURA. NUNCA EMPURRA.

Não é um segundo motor: não pontua, não classifica, não descobre.
`PUBLICATION_STATE` **nasce** de `EXTERNAL_MATERIAL_READY` — decisão de
`v21_comercial.externo()` — e a catraca só pode **rebaixá-lo**. O teste `U1`
compara permissividade como inteiro e quebra se algum dia ela promover alguém.

### As seis etapas obrigatórias, por registro

| etapa | pergunta |
|---|---|
| `IDENTITY_PROVENANCE` | tem identidade e origem declarada? |
| `NORMALIZATION` | os eixos canônicos existem? |
| `CLASSIFICATION` | tem `QA_STATUS` e `CLIENT_SAFE` booleano? |
| `MISSION_RULER` | a régua de QA não o rejeitou? |
| `RELATION_EXTRACTION` | o extrator de pares teve texto para ler? |
| `LOCALIZATION` | a leitura chega na língua de quem vai ler? |

Estados: `PASSED` · `UNKNOWN` · `FAILED` · `NOT_APPLICABLE`.
**`UNKNOWN` é o estado que esta camada existe para tornar visível.**

`AXES_MISSING` é `UNKNOWN`, **não** `FAILED`: medido, as 26 coleções de material
trazem os três eixos em 100% dos registros, e um eixo ausente prova que a
normalização não deixou marca — não que ela reprovou. Chamar isso de falha
promoveria um NÃO SEI a acusação.

### Medido hoje

```
porta       10 famílias · COMMERCIAL_CATALOG 0/10 · HERBICIDE_CURRENT_CONTEXT 0/16
material    7.023 registros · PASSED 6.981 · INCOMPLETE 42 · QUARANTINED 0
            NO_TEXT_FOR_PAIR_EXTRACTION 40 · AXES_MISSING 2 · SENTINEL 2
oportunidades  PUBLISHABLE 5 · VALIDATION_REQUIRED 38 · UNKNOWN 0 · QUARANTINED 0
trilha         COMPLETE 43
VIOLACOES      0
```

`UNKNOWN` e `QUARANTINED` medem zero **no dado de hoje**, não por serem estados
mortos: `U4` exercita os dois pela função, com material inventado, para que a
regra esteja provada mesmo onde o pacote não a exercita.

### O que faz a cadeia parar

```
V1  uma oportunidade PUBLISHABLE citando material QUARANTINED
V2  um registro sem QA_STATUS — a classificação nunca rodou nele
V3  uma oportunidade citando evidência que não existe no pacote
V4  a catraca promovendo alguém (defeito nosso, não do dado)
V5  uma família da porta que some sem declaração
```

---

## 8 · O contrato do payload comercial · `scripts/v21_briefing.py`

    SE O CONSUMIDOR TEM DE LER EVIDÊNCIA BRUTA PARA INVENTAR A OPORTUNIDADE,
    A INTELIGÊNCIA NÃO ENTREGOU A OPORTUNIDADE: ENTREGOU A LIÇÃO DE CASA.

`DESIGN-INGEST/OPPORTUNITY-BRIEFINGS.json` · uma ficha por oportunidade, **43**.

```
ID · OPPORTUNITY_ID · PUBLICATION_STATE
WHAT_IS_HAPPENING          cultura · alvo · região · escopo · data · idade ·
                           direção + evidência + método · trecho da fonte ·
                           nº de apoios · famílias · nº de publicadores · SUMMARY
WHY_THIS_IS_A_COMMERCIAL_OPPORTUNITY
                           COMMERCIAL_REASON_STATE · CHAIN (5 elos) ·
                           MISSING_LINKS · REASON_CODES · OWNER
WHY_NOW + WHY_NOW_CODES + WHY_NOW_LAW
WINDOW                     STATE · KIND · FIELD · START · END · DAYS_REMAINING ·
                           COMMERCIAL_WINDOW · COMMERCIAL_WINDOW_FROM · OWNER
PORTFOLIO_MATCHES[]        (abaixo)   PORTFOLIO_MATCH_COUNT · CROP_LEVEL_ONLY_COUNT
PRIMARY_MATCH + PRIMARY_MATCH_RULE + PRIMARY_MATCH_LAW
SALES_REASON               STATE · TEMPLATE_CODE · SLOTS · SLOT_LABELS ·
                           SLOT_EVIDENCE_IDS
WHAT_IS_MISSING[]          códigos
ACTION_MAP[]               (abaixo)
EVIDENCES[]                (abaixo)
BRIEFING_DOES_NOT_PROVE
```

**Nenhum registro carrega prosa.** Todo campo é código, ID ou número; as frases
vivem em `PHRASES`, no cabeçalho, uma vez por código, em **PT/IT/EN**. O briefing
curto é um `TEMPLATE_CODE` com `SLOTS`, e **cada slot carrega a evidência que o
sustenta**.

    O CÓDIGO É DADO. A FRASE É TEXTO. E CADA PEDAÇO DA FRASE TEM DONO.

`scripts/v21_ler_briefing.py` renderiza a ficha em prosa a partir dos códigos,
porque um contrato que só a máquina lê não foi revisado por ninguém.

---

## 9 · A regra de `WHY_THIS_IS_A_COMMERCIAL_OPPORTUNITY`

Cinco elos, e `PROVEN` só quando **os cinco** fecham:

```
PROBLEM          alvo agronômico declarado          + evidência
AGRONOMIC_NEED   NEED_DIRECTION = POSITIVE_PRESSURE + trecho da fonte + método
MOMENT           janela de APLICAÇÃO, ou recência do sinal (≤120 dias, o
                 limiar do portão C do motor — reusado, não inventado)
ADAMA_PORTFOLIO  ≥1 produto com par de rótulo verificado E no catálogo público
POSSIBLE_ACTION  WHY_NOW ≠ UNKNOWN e ≠ CLOSED
```

Faltando um: `COMMERCIAL_REASON = UNKNOWN`, com `MISSING_LINKS` nomeando qual.

    NUNCA ESCREVER UMA FRASE COMERCIAL PORQUE UM PRODUTO E UMA DOENÇA
    APARECERAM NO MESMO CONJUNTO.

Medido: **PROVEN 5 · UNKNOWN 38**. Os 5 são exatamente os 5 `SALES_READY`.

---

## 10 · A regra de `WHY_NOW`

```
1  NEED_DIRECTION fechada                          → CLOSED
2  SALES_READY  e  janela de APLICAÇÃO declarada e aberta  → ACT_NOW
3  SALES_READY  e  janela UNKNOWN                  → VALIDATE_NOW
4  SALES_READY  e  janela declarada, não agora     → PREPARE
5  SALES_PREPARE                                   → PREPARE
6  COMMERCIAL_WATCH                                → WATCH
7  STRATEGIC + STATUS=FUTURE_PREPARATION           → FUTURE
8  qualquer outro                                  → UNKNOWN
```

    SE A JANELA É UNKNOWN, ACT_NOW NÃO PODE NASCER POR DEFAULT.

`WHY_NOW` é **estritamente mais conservador** que `COMMERCIAL_WINDOW` e nunca
mais permissivo. `COMMERCIAL_WINDOW` aceita a data do documento — e está certo,
porque essa data responde «o sinal é de hoje?». Mas «hoje há sinal» não é «hoje
é a hora de aplicar», e nada foi afrouxado para separá-los: **o limiar da régua
comercial não foi tocado.**

Medido: `ACT_NOW` **0** · `VALIDATE_NOW` 5 · `PREPARE` 0 · `WATCH` 14 ·
`FUTURE` 7 · `CLOSED` 7 · `UNKNOWN` 10.

**`ACT_NOW` = 0 não é um estado morto: é a consequência medida do buraco B3.**
Nenhum registro do pacote declara `WINDOW_KIND = APPLICATION`, porque a família
que carrega janela corrente não entra. Prova `U10` que a camada nunca infla.

---

## 11 · O modelo de `PORTFOLIO_MATCHES`

**Todos** os produtos cujo rótulo nomeia o par cultura × alvo. Não
`PRIMARY_PRODUCT + N_MORE`.

```
PRODUCT_ID · PRODUCT_NAME · REGISTRATION_NUMBER
ACTIVE_SUBSTANCES[]   ID · nome · MOA_STATE · HRAC/IRAC/FRAC · EU_STATE ·
                      EU_EXPIRATION_OF_APPROVAL · evidência
MATCH_STATE           VERIFIED_LABEL_MATCH · PRODUCT_SPECTRUM_ONLY ·
                      CROP_ONLY_MATCH · CROP_MATCH_NO_TARGET_IN_CASE
MATCH_REASON_CODE
CROP_FIT              estado · CROP_ID · CROP_ON_LABEL (palavra da fonte) · evid.
TARGET_FIT            estado · ISSUE_ID · TARGET_ON_LABEL · TARGET_AS_WRITTEN ·
                      LINK_STRENGTH · evidência
REGULATORY_FIT        estado · titular · status · EXPIRY · geografia · evidência
REGIONAL_FIT          NATIONAL_AUTHORIZATION_CONTAINS_REGION | UNKNOWN
WINDOW_FIT            WINDOW_DECLARED | UNKNOWN  (pela chave mínima do motor)
COMMERCIAL_CATALOG    estado · ID · URL · CATALOG_DECLARES_CROP · culturas do site
VALIDATION_STATE      READY_TO_NAME_EXTERNALLY | INTERNAL_READING_ONLY
MARKETABLE_STATE      UNKNOWN sempre
RESTRICTION_CODES[]   EVIDENCE_IDS[]
```

O `MATCH_STATE` sai da **força que o próprio rótulo declara** em `LINK_STRENGTH`
(`LINHA_DA_TABELA`, `BLOCO_DA_CULTURA`, `DECLARACAO_DE_PRODUTO`) — não de leitura
nossa.

**Cobertura de cultura não é cobertura de alvo.** Um produto com videira no
rótulo e sem botrite não entra em `PORTFOLIO_MATCHES` — entra em
`CROP_LEVEL_ONLY_COUNT`. Ele não some; ele não mente.

### A regra do `PRIMARY_MATCH`

Um produto que seja **simultaneamente** (a) par de rótulo verificado, (b) no
catálogo público, (c) com a cultura declarada na própria página, e (d) sem data
de autorização anterior à data de referência do pacote. **Exatamente um**:
`PM_SINGLE_EXTERNALLY_NAMEABLE`. Zero ou mais de um: **`UNKNOWN`**, com a regra
declarada.

    A ORDEM DA LISTA É ALFABÉTICA E NÃO SIGNIFICA ESCOLHA.

Medido: `PM_SINGLE` 5 · `PM_NONE` 35 · `PM_SEVERAL` 3.

### O que a data de autorização faz, e o que ela não faz

**171 dos 463 matches** têm `EXPIRY` anterior à data de referência do pacote. A
doutrina do repositório já estava escrita e não é minha para reescrever:

    EXPIRY != WITHDRAWAL. DATA VENCIDA ENTRA COMO DATA, NUNCA COMO RETIRADA.
    E `CURRENTLY_MARKETABLE` É UNKNOWN SEMPRE.

Então o produto **continua um match válido** — o rótulo diz o que ele cobre, e
isso não mudou. O que a data faz é impedir `READY_TO_NAME_EXTERNALLY`. Efeito
medido: `PM_SINGLE` caiu de 10 para 5. **A camada só rebaixa.**

---

## 12 · O modelo do `ACTION_MAP`

Um registro por departamento; os departamentos vêm do `ACTION_MAP` do motor
(`MARKET_DEVELOPMENT`, `COMMERCIAL`, `MARKETING`, `SCIENCE_TECHNICAL`, `SUPPLY`,
`PORTFOLIO`, `REGULATORY`) — nenhum inventado.

```
DEPARTMENT · ACTION_STATE (ACT_NOW|PREPARE|VALIDATE|WATCH|NO_ACTION|UNKNOWN)
ACTION_CODE · WHY_CODES · EVIDENCE_IDS · DEPENDENCY · NEXT_TRIGGER · MISSING_CODES
```

O estado sai de uma matriz **departamento × WHY_NOW** que diz duas coisas que o
dado sustenta — quem valida vem antes de quem ativa, e material externo vem
depois de validação — e nada além disso.

    NÃO INVENTAR SEQUÊNCIA ORGANIZACIONAL SE O DADO NÃO A SUSTENTA.
    ONDE ELE NÃO SUSTENTA, O ESTADO É UNKNOWN.

Com `WHY_NOW = UNKNOWN` não há matriz: só Market Development recebe
`VALIDATE`, e só quando `WHAT_IS_MISSING` diz o que validar. Os outros ficam
`UNKNOWN` com dependência declarada.

Medido: `WATCH` 49 · `PREPARE` 26 · `NO_ACTION` 20 · `VALIDATE` 20 · `UNKNOWN` 19.

---

## 13 · O papel da evidência, e o resumo curto

Onze papéis, com os negativos em primeira classe:

```
SUPPORTS_SIGNAL · SUPPORTS_DIRECTION · SUPPORTS_WINDOW · SUPPORTS_PRODUCT_MATCH
SUPPORTS_REGIONAL_CONTEXT · SUPPORTS_COMMERCIAL_ACTION
WEAKENS · CONTRADICTS · CLOSES · BACKGROUND_ONLY · UNKNOWN
```

Medido: `SUPPORTS_PRODUCT_MATCH` 265 · `BACKGROUND_ONLY` 258 ·
`SUPPORTS_REGIONAL_CONTEXT` 62 · `SUPPORTS_SIGNAL` 18 · `SUPPORTS_DIRECTION` 10 ·
**`WEAKENS` 8 · `CLOSES` 7**.

A evidência negativa continua podendo esfriar oportunidade, e é o próprio
`v21_necessidade.pares_observados()` — o dono da direção — que decide se um sinal
`WEAKENS` ou `CONTRADICTS` dentro daquele caso.

Cada evidência ganha, **sem perder nada do original** (`SOURCE_IDS`,
`SOURCE_URLS`, `REFERENCE_DATE`, `PROVENANCE` e o ponteiro para o registro
completo viajam junto):

```
INTELLIGENCE_HEADLINE_SLOTS   {TARGET, REGION}
INTELLIGENCE_SUMMARY_CODE     IE_PRESSURE_OBSERVED · IE_SOURCE_RECOMMENDS ·
                              IE_SOURCE_STOPS · IE_SOURCE_MONITORS ·
                              IE_LABEL_PAIR · IE_LABEL_SPECTRUM ·
                              IE_WINDOW_DECLARED · IE_REGIONAL_CONTEXT ·
                              IE_BACKGROUND · IE_UNKNOWN
COMMERCIAL_IMPLICATION_CODE   CI_SUPPORTS_SALE · CI_ENABLES_PRODUCT_CLAIM ·
                              CI_COOLS_OPPORTUNITY · CI_NO_IMPLICATION · UNKNOWN
DEPARTMENT_ACTION
```

    NÃO RESUMIR «COMERCIALMENTE» O QUE A FONTE NÃO PERMITE CONCLUIR.

`SUPPORTS_SIGNAL` → `COMMERCIAL_IMPLICATION = UNKNOWN`, sempre: presença não é
recomendação. Prova `U20`.

---

## 14 · A TESTEMUNHA · Botrytis × Grapevine × Emilia-Romagna

`python3 scripts/v21_ler_briefing.py OPP_5F31A63F844D` — reconstruída do acervo,
nunca do texto do portal.

```
OPP_5F31A63F844D · PUBLICATION_STATE = PUBLISHABLE
```

| campo | valor |
|---|---|
| cultura · alvo · região | `CROP_GRAPEVINE` · `ISSUE_BOTRYTIS` · `REGION_EMILIA_ROMAGNA` |
| escopo | `PROVINCIAL` |
| data / idade do sinal | 2026-09-01 · **1 dia** |
| direção | `POSITIVE_PRESSURE` · `IT-PHEN-001` · `PAIR_IN_SAME_CLAUSE` |
| a frase da fonte | «*Vite/botrite: intervir em pre-colheita com Fenhexamid (max 2) ou alternativas biologicas.*» |
| evidência | 14 apoios · 2 famílias · 4 publicadores |
| `COMMERCIAL_REASON_STATE` | **PROVEN** — os cinco elos fecham |
| `WHY_NOW` | **`VALIDATE_NOW`** · `WN_NO_APPLICATION_WINDOW` |
| janela | `STATE=UNKNOWN` · `KIND=None` · `COMMERCIAL_WINDOW=ACT_NOW` (de `SIGNAL_DATE`) |
| `PORTFOLIO_MATCHES` | **3** no par · 22 só na cultura |
| `PRIMARY_MATCH` | `IT-PRD-053` (**BANJO**) · `PM_SINGLE_EXTERNALLY_NAMEABLE` |
| `WHAT_IS_MISSING` | `WINDOW` · `MAGNITUDE` |

### Os três produtos

| produto | reg. | substância | catálogo | declara VITE | validação |
|---|---|---|---|---|---|
| **BANJO** | 013905 | FLUAZINAM · FRAC 29 · UE aprovado até 2027-11-30 | **sim** | **sim** | `READY_TO_NAME_EXTERNALLY` |
| AGHARTA | 017432 | FLUAZINAM · FRAC 29 | não | — | `INTERNAL_READING_ONLY` |
| EMBRACE | 015315 | FLUAZINAM · FRAC 29 | não | — | `INTERNAL_READING_ONLY` |

Os três dizem «*muffa grigia*» / «*Botrytis cinerea*» no bloco da cultura VITE
(`BLOCO_DA_CULTURA`), com evidência `IT-LBL-979/981`, `IT-LBL-1437/1439`,
`IT-LBL-1626/1628`. **Os três são o mesmo ativo** — a oferta ADAMA para botrite
em videira, neste pacote, é fluazinam em três marcas.

### O mapa de ação

| departamento | estado | ação | dependência | gatilho |
|---|---|---|---|---|
| MARKET DEVELOPMENT | **VALIDATE** | confirmar a janela regional de aplicação e a recomendação antes de qualquer ativação | — | uma janela de aplicação declarada |
| COMMERCIAL | **PREPARE** | não ativar a força de vendas até a validação de Desenvolvimento de Mercado | MARKET_DEVELOPMENT | idem |
| SCIENCE / TECHNICAL | **VALIDATE** | conferir a leitura agronômica contra a fonte original | — | o próximo boletim regional |

### As 14 evidências, por papel

`SUPPORTS_DIRECTION` **1** · **`WEAKENS` 7** · `SUPPORTS_PRODUCT_MATCH` 6.

⚠️ **Sete dos oito boletins que sustentam este caso não mandam intervir.** Só
`IT-PHEN-001` traz a oração que recomenda; os outros sete citam botrite em
contexto de observação, e o papel deles é `WEAKENS` — com
`COMMERCIAL_IMPLICATION = CI_COOLS_OPPORTUNITY`. O caso continua `SALES_READY`
pela régua comercial, que não conta famílias no escuro, e a fragilidade viaja
escrita ao lado em vez de sumir na contagem de «14 apoios».

    OITO APOIOS NÃO SÃO OITO RECOMENDAÇÕES.
    UM CONTADOR DE EVIDÊNCIA QUE NÃO DIZ O PAPEL DE CADA UMA ENGANA PELO TAMANHO.

### As dez respostas

1. **Por que há oportunidade comercial?** Há, e é `PROVEN`. O serviço
   fitossanitário da Emilia-Romagna escreveu, em documento datado de 2026-09-01,
   que se deve intervir contra botrite em videira em pré-colheita; existe rótulo
   ministerial ADAMA que nomeia o par videira × botrite; e um dos produtos está
   no catálogo público com a cultura declarada.
2. **O que exatamente podemos vender?** **BANJO** (reg. 013905). AGHARTA e
   EMBRACE cobrem o mesmo par com o mesmo ativo, e **não estão no catálogo
   público** — são leitura interna, não material externo.
3. **Por que esses produtos cabem?** Porque o rótulo ministerial nomeia
   `VITE` e «*muffa grigia / Botrytis cinerea*» **no mesmo bloco de cultura**, com
   os IDs de evidência acima. Não é inferência: é o documento que os une.
4. **É realmente ACT NOW?** **NÃO.** `WHY_NOW = VALIDATE_NOW`. O sinal é de
   ontem e a direção manda intervir, mas **não existe janela de aplicação
   declarada** para videira × botrite × Emilia-Romagna no pacote.
   `COMMERCIAL_WINDOW = ACT_NOW` vem de `SIGNAL_DATE`, e data de documento não é
   janela de pulverização.
5. **Qual informação ainda falta?** `WINDOW` — a janela regional de aplicação.
   `MAGNITUDE` — área, incidência, severidade: o boletim observa, não faz censo.
6. **Quem deve agir agora?** **Market Development**, e só. Validar a janela.
7. **O que o Comercial deveria receber?** Um aviso de espera, não uma ordem:
   *não ativar a força de vendas até a validação de Market Development*, com a
   dependência e o gatilho declarados.
8. **O que Desenvolvimento de Mercado deveria receber?** O par, a região, a
   frase original do boletim, a data, os três produtos com o estado de cada um, e
   a pergunta exata: existe janela regional de aplicação declarada para este par?
9. **Qual texto curto deveria chegar como briefing?**
   > **botrite em vite · emilia-romagna**
   > pressão observada — a janela regional ainda precisa de validação. O
   > portfólio ADAMA tem 3 soluções com uso compatível no par.
   >
   > **AÇÃO:** Market Development → validar janela.
10. **Quais afirmações NÃO podem ser feitas?** Que há janela aberta agora. Que a
    doença está incidente em área conhecida. Que o produtor vai tratar. Que há
    demanda, sell-in, pedido, estoque ou pipeline. Que AGHARTA ou EMBRACE podem
    ser nomeados em material externo. Que a leitura é do serviço fitossanitário:
    a leitura é nossa, `CLIENT_SAFE = false`, e o método viaja ao lado.

---

## 15 · Outros casos, para provar que o contrato não é do Botrytis

| caso | tipo | `WHY_NOW` | `COMMERCIAL_REASON` | o que o contrato mostrou |
|---|---|---|---|---|
| `OPP_9C600748BB1B` milho × piralide · FVG | Pest Control | `VALIDATE_NOW` | `PROVEN` | **5** produtos, todos lambda-cialotrina IRAC 3; `PRIMARY_MATCH = UNKNOWN` porque os cinco têm data de autorização 2026-08-31, dois dias antes da referência |
| `OPP_81C053E9DCD3` milho × piralide · Lombardia | fechado por evidência | **`CLOSED`** | `UNKNOWN` | `TREATMENT_PROHIBITED` — «*durante a floração VIGORA A PROIBIÇÃO*». Comercial `NO_ACTION`, gatilho `TR_NONE`. Mesmo par, outra região, resposta oposta |
| `OPP_E138ECDFD7D2` videira × peronospora · E-R | Disease Control | `CLOSED` | `UNKNOWN` | `WINDOW_CONCLUDED`; elos `AGRONOMIC_NEED` e `POSSIBLE_ACTION` faltando |
| `OPP_EE1E2A3869EE` oliveira · mercado | Market Moment / gap | `UNKNOWN` | `UNKNOWN` | **os cinco elos UNKNOWN**, `SALES_REASON = UNKNOWN`, régua comercial `LABEL_WITHOUT_CATALOG`. Um match de cultura sem alvo, fora do catálogo |
| `OPP_75C37DED9160` maçã × carpocapsa · Veneto | Disease/Pest | `VALIDATE_NOW` | `PROVEN` | continua `PUBLISHABLE`; o caso testemunha do V1.1 sobreviveu |

---

## 16 · Regressões

| | baseline `0ddf52d` | depois |
|---|---:|---:|
| testes descobertos | 720 | **748** (+28) |
| falhas | 7 | **6** |
| erros | 1 | **1** |
| pulados | 16 | 16 |

**Nenhuma regressão nova.** As 6 falhas e o 1 erro são os mesmos do baseline:

| falha | classificação |
|---|---|
| `test_source_e_fact_location_quando_declarados` (×3) | **preexistente** · procedência de amostras antigas em `data/samples/` |
| `test_toda_amostra_declara_data_de_captura` | **preexistente** · idem |
| `test_toda_amostra_declara_origem` | **preexistente** · idem |
| `test_a_unica_migration_nova_tem_incompatibilidade_provada` | **preexistente** · gate de import ES |
| `ERROR: test_comunicacao` | **preexistente** · o módulo é script e faz `SystemExit(1)` na descoberta |

Uma falha do baseline **sumiu**: `test_branch_vivo_nao_e_alvo_congelado`. Não foi
consertada por mim — ela depende do estado git do checkout, e falha em worktree
com `HEAD` destacado. Passa na árvore de trabalho normal, antes e depois.

Números de sentinela (`TEST_COUNT_CURRENT` 720 → 748) atualizados com a
ferramenta que o próprio teste manda rodar (`scripts/metricas_canonicas.py --sync`), mais o prompt de bootstrap e o
handoff, cujos números o `test_handoff` cobra.

### O que a regressão prova, item a item

- **os casos existentes não sumiram** — 43 antes, 43 depois; `U21` prova uma
  ficha por oportunidade, nem uma a mais;
- **nenhuma oportunidade nasceu da camada textual** — o motor não foi tocado;
  `BY_ARCHETYPE`, `BY_STATUS` e `BY_COMMERCIAL_PRIORITY` são idênticos;
- **nenhum produto foi promovido para preencher tela** — `U17` exige par de
  rótulo declarado pela fonte em todo match; e a regra da data de autorização
  **derrubou** `PM_SINGLE` de 10 para 5;
- **`ACT_NOW` não aumentou por copy** — `WHY_NOW = ACT_NOW` é **0**, contra 16
  `STATUS = ACT_NOW` do motor. `U10` fixa a desigualdade;
- **`UNKNOWN` continua `UNKNOWN`** — 38 fichas com `COMMERCIAL_REASON = UNKNOWN`
  e `MISSING_LINKS` nomeados; `U22`;
- **evidência negativa continua enfraquecendo** — `WEAKENS` 8, `CLOSES` 7;
  `U18`–`U19`.

---

## 17 · Falhas ainda abertas

| # | o que | estado |
|---|---|---|
| A1 | `HERBICIDE_CURRENT_CONTEXT` · 16 registros reais de janela corrente não entram no pacote. É a causa medida de `ACT_NOW = 0` | **ABERTO** · declarado, contado, pinado em `U8` |
| A2 | `promover_research` é tudo-ou-nada: 4 boletins reais chegam ao motor mudos | **ABERTO** · herdado; agora visível (`U6`) |
| A3 | `v21_crossings.py` ainda indexa janela por cultura só | **ABERTO** · herdado, não alterado |
| A4 | `sin[:8]` — o motor corta a lista de apoios em oito; o nono conta e não é citado | **ABERTO** · achado nesta rodada, não alterado |
| A5 | 171 de 463 matches com data de autorização anterior à referência | **MEDIDO** · vira restrição, nunca «retirada» |
| A6 | `PM_SEVERAL_EQUALLY_DEFENSIBLE` em 3 casos | **por decidir** · `PRIMARY_MATCH = UNKNOWN` é a resposta honesta hoje |
| A7 | 6 falhas + 1 erro preexistentes na suíte | **ABERTO** · anteriores a esta missão |

---

## 18 · Confirmação explícita

```
PORTAL          = NÃO TOCADO   (italia-portale/ intacto — 0 arquivos no diff)
DESIGN          = NÃO TOCADO   (nenhum .css, .html ou BrandWell no diff)
VERCEL          = NÃO TOCADO
PRODUÇÃO        = NÃO TOCADA   (nenhuma publicação, nenhum deploy, nenhum merge)
THRESHOLDS      = NÃO ALTERADOS (score, portões, janela, prioridade comercial)
SEGUNDO MOTOR   = NÃO CRIADO   (v21_oportunidades.py e v21_comercial.py intactos)
EVIDÊNCIA BRUTA = NÃO APAGADA  (as camadas novas só acrescentam campo)
UNKNOWN         = CONTINUA UNKNOWN
```

Arquivos tocados:

```
NOVOS      scripts/v21_catraca.py
           scripts/v21_briefing.py
           scripts/v21_ler_briefing.py
           scripts/v21_testemunha_universal.py
           tests/test_trilha_universal.py
           data/samples/AUDITORIA-SOMBRA/TRILHA-UNIVERSAL-TESTEMUNHA.json
           docs/design/TRILHA-UNIVERSAL-E-CONTRATO-COMERCIAL.md

ALTERADOS  scripts/v21_cadeia.sh                      (dois passos novos)
           scripts/v21_aceitacao.py                   (virou portão)
           .github/workflows/comunicacao-publica.yml  (fim do `|| true`)
           PROMPT-... · HANDOFF-... · docs/*          (só marcadores de métrica)
```
