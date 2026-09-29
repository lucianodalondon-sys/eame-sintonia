# PRODUTOR DE AFIRMAÇÕES — a versão mínima da COL-LAW-202 (D158)

> `DOCUMENTO DA SALA  →  AFIRMAÇÕES COM PROVA  →  INTELLIGENCE`, de forma repetível.
> Determinístico, sem LLM, sem rede, sem banco, sem infraestrutura nova.

A [`COL-LAW-202`](BIBLIA-CANONICA-DA-COLETA.md) (`ARTIFACT → CLAIM`) estava
`LAW_STATUS CANONICAL` e `IT ABSENT`: o SINTONIA guardava **documentos** e nunca
**afirmações**. Sem afirmação, tudo o que a Intelligence recebia era o documento inteiro,
com a data e o lugar do documento inteiro — e foi por isso que os dois objetos da corrida
R9 tiveram de ser **escritos à mão** num script. A D158 autorizou a versão **mínima** que
fecha esse buraco, e só ela.

---

## O que é uma afirmação

**UM trecho do texto**, com tudo o que prova que ele é daquele documento e o que a fonte
diz sobre **quando** e **onde**:

| campo | o que é |
|---|---|
| `ASSERTION_ID` | determinístico: `sha256(SOURCE_ID │ RAW_SHA256 │ início │ fim │ trecho)` |
| `TRECHO_LITERAL` | **exatamente** `texto[INICIO:FIM]`. Nunca reescrito, nunca normalizado |
| `TRECHO_SHA256` | o selo do trecho |
| `POSICAO` | `INICIO`, `FIM`, a **secção estrutural** que governa o trecho e a **secção territorial** |
| `CONTEXTO_MINIMO` | só quando o sentido depende dele (entidade ou data herdada de fora do trecho) |
| `FACT_TIME` | valor · `NAO SEI` · `NAO_EXISTE` |
| `FACT_TIME_ROLE` | `PAPEL` · `ORIGEM` · `BASIS` (trecho + offset) · `PRECISAO` · `PORQUE` · `COMPOSICAO` |
| `FACT_LOCATION` | valor ou `NAO SEI`, com `LOCATION_SOURCE` e o trecho que o prova |
| `ENTIDADES` | cultura e praga, cada uma com o seu `ENTITY_SOURCE` (COL-LAW-221) |
| `PROVENIENCIA` | `ITEM_ID`, `RUN_ID`, `SOURCE_ID`, `RAW_OBSERVATION_ID`, `RAW_SHA256`, `RAW_STORAGE_PATH`, `DOCUMENT_ID`, `URL`, `PUBLISHED_AT`, `COLHIDO_EM` |

### O PAPEL da data — e a regra que não tem exceção

```
PAPEIS            ACONTECIMENTO · VALIDADE · PUBLICACAO · PREVISAO
                  PERIODO_DA_EDICAO · ATO · MARKET_PERIOD
PAPEL_QUE_E_FACTO ACONTECIMENTO
```

Um papel que não seja `ACONTECIMENTO` **nunca** sai como `FACT_TIME`. Isso é mecânico, não
é disciplina: a data de publicação, a validade de uma derroga, o período que a edição
cobre e uma previsão têm todos um nome próprio, e ao terem um nome próprio ficam de fora.

### De onde veio o valor

```
LITERAL        escrito dentro do próprio trecho, ou no cabeçalho impresso da secção dele
CABECALHO      composto do cabeçalho da secção, sob as CINCO CONDIÇÕES da D147
RELATIVO_D63   contado pelo leitor vivo a partir de publicação PROVADA
```

---

## O que ele **não** decide

Relevância comercial · oportunidade · ligação ADAMA · recomendação · prioridade ·
**liberação** · produto · significado estratégico. Isso é da Intelligence e dos portões
depois dela (`INT-LAW-030` / `INT-LAW-031` · `COL-LAW-201` / `COL-LAW-202`).
**A Collection não vira Intelligence.**

---

## O que ele reusa — e por isso não há extrator paralelo nenhum

| peça | o que ela já fazia |
|---|---|
| `leis/fato_do_texto.py` | o corpo (`sem_vizinhos`, `corpo`) e **o leitor temporal do vivo** |
| `leis/fato_local.py` | quem lê o italiano: topónimos, âncoras, relativas |
| `leis/boletim_do_campo.py` | `ler_afirmacao(texto, inicio, fim)`: cultura, praga e **lugar** do trecho, cada um com a procedência, e as travas `COL-LAW-221` / `COL-LAW-032` |
| `leis/afirmacao_da_fonte.py` | o vocabulário e as travas da afirmação (D112) |

`ler_afirmacao` existia desde a `BOLETIM-POR-SECAO` e **nunca tinha quem lhe desse o
`inicio/fim`**: até aqui, só o gabarito, escrito à mão. É isso que muda.

### A parte nova, e só ela

1. **As secções estruturais.** Uma secção abre na quebra de página (`\f`) do extrator de
   PDF ou numa **linha de cabeçalho** (curta, sem ponto final, em maiúsculas, com as
   letras dobradas do PDF, ou que seja só o período).
   ⚠️ *Limite declarado:* um cabeçalho em Maiúsculas De Título («Situazione Attuale») não
   abre secção. Preferiu-se falhar de menos a cortar o corpo ao meio.
2. **As frases.** Uma frase acaba em `.`, `!`, `?` ou `;` **seguido de espaço** — a
   condição do espaço é o que separa `46.8 mm` (número) de `32,8 mm.` (fim de frase).
   Mais a **vírgula que emenda duas frases** (o ponto que o compositor perdeu), numa regra
   estreita: vírgula + palavra de classe fechada em maiúscula + palavra em minúscula — a
   minúscula é a guarda que salva «La Spezia» e «Le Marche».
3. **`leis/tempo_da_afirmacao.py` — a INTERFACE do leitor temporal.** O leitor do vivo fica
   atrás dela, para o componente tipado da L5 (`leis_proposta/tempo_tipado.py`, congelado)
   poder entrar no lugar dele sem mexer em quem pergunta. Ela acrescenta o **papel** da
   data, o **período impresso num cabeçalho** em duas formas que o vivo não lê (a numérica
   `Dal dd-mm-aaaa al dd-mm-aaaa`, e a de **letras dobradas** que o PDF produz no negrito),
   e a **composição** da D147/D149/D153.

---

## As leis que governam isto

| | |
|---|---|
| `COL-LAW-202` | `ARTIFACT → CLAIM`: o claim guarda `EVIDENCE_SPAN`, `FACT_TIME`, `FACT_LOCATION`, `PROVENANCE` |
| `COL-LAW-203` | a procedência chega até ao valor — aqui, até ao `RAW_SHA256` do banco |
| `COL-LAW-221` | de onde veio o **nome** da entidade (`ENTITY_SOURCE`) |
| `COL-LAW-032` | de onde veio o **lugar** (`LOCATION_SOURCE`) |
| `D63` | relativa («la settimana scorsa») só com publicação **provada**, e a conta é a do vivo |
| `D147` | o período do cabeçalho só governa a afirmação com as **cinco condições** cumpridas; o período que a **edição** cobre não é validade nem facto |
| `D149` | uma relativa de semana ancora-se no **período impresso** do próprio boletim, quando ele existe |
| `D153` | compor só com evidência de que o cabeçalho governa a afirmação, sem concorrente, com **os dois trechos** e a origem registados. Na dúvida, `NÃO SEI` |

### As cinco condições da D147, em código

`leis/tempo_da_afirmacao.py::_compor_do_cabecalho` verifica, uma a uma:

1. há **um** período no cabeçalho da secção — não dois;
2. o período está na **mesma secção** que a afirmação, e **antes** dela;
3. o próprio trecho **não escreve outro tempo** (não há concorrente para a mesma afirmação);
4. o papel do período é `ACONTECIMENTO` **e** o trecho fala de alguma coisa que aconteceu —
   conselho, frase institucional e futuro não herdam a data de uma secção passada;
5. **os dois trechos** e a **origem** ficam registados em `COMPOSICAO`.

Faltando uma, `NAO SEI` — com o porquê escrito.

---

## Onde as afirmações moram

**Nenhuma infraestrutura nova.** `admissao/produtor_de_afirmacoes.py` lê uma cópia
**só-leitura** da Sala e escreve **um artefato JSON** ao lado dela:

```bash
py admissao/produtor_de_afirmacoes.py <SALA_ATUAL.json> <AFIRMACOES.json> [--item <ITEM_ID>]
```

Não abre banco, não cria tabela nem migration, não escreve na Sala. Cada afirmação é
**conferida contra o texto de onde saiu** antes de ser escrita; a que não passa fica em
`REPROVADAS`, com o motivo.

---

## A conferência — o programa prova o trecho de origem

`conferir_afirmacao(af, texto, raw_sha256=…)` devolve as violações. Reprovam:

- `TRECHO_LITERAL` diferente de `texto[INICIO:FIM]` (o documento mudou, ou a âncora está errada);
- `TRECHO_SHA256` que não bate;
- `RAW_SHA256` diferente do documento — **documento alterado**;
- `ASSERTION_ID` que não é o hash desta afirmação;
- offset fora do texto, ou trecho fora da secção declarada;
- `PAPEL` fora do vocabulário;
- `FACT_TIME` **com valor** e papel que não é `ACONTECIMENTO`;
- `BASIS` ou `CONTEXTO_MINIMO` que não estão no texto onde dizem estar;
- `LOCATION_SOURCE` / `ENTITY_SOURCE` fora da lei dona deles.

---

## As provas

| | |
|---|---|
| `tests/test_o_produtor_de_afirmacoes.py` | 40 testes. Textos **sintéticos**, um por regra. Inclui os negativos obrigatórios e o grep que reprova se um ID, um trecho ou uma data da corrida R9 entrar numa **regra** de produção |
| `provas/d158/r9_pelo_caminho_canonico.py` | a mesma Sala da R9, pelo caminho oficial: produtor → motor → gerador → fiscal, e a comparação com os dois objetos que a mão escreveu |
| `provas/d158/mutar_o_produtor.py` | um mutante por garantia, numa cópia por `git archive` |

O resultado medido está em
[`ENTREGA-PRODUTOR-AFIRMACOES.md`](https://example.invalid/fora-do-git) (fora do Git, em
`C:/Users/London1/auditoria-madrugada/`).

---

## O que fica por fazer, e de quem é

| | |
|---|---|
| **o MOTOR ler afirmações** | `motor/motor_das_capacidades.py` continua a ler o documento inteiro. Ligar o motor às afirmações é da **Intelligence** — a Collection produz o claim, não decide o que ele significa |
| **a liberação por objeto** | `LIBERACAO_AUTOMATICA = NOT_IMPLEMENTED`, `BLOCKED_BY = CONTRATO_V2.2_NAO_VERSIONADO` (o C8 é uma decisão do dono escrita como frase). Registado pela D-GER-3 |
| **os comuni no gazetteer** | `leis/fato_local.cobertura()` mede `MUNICIPALITIES = 0` — sem a lista oficial do ISTAT, um comune que não seja capoluogo é invisível. Isso limita a precisão do `FACT_LOCATION`, e está declarado lá |
| **tornar a COL-LAW-202 `CURRENT`** | é decisão da Bíblia da Coleta, não desta missão |
