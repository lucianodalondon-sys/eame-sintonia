# PAPEL ARQUITETURAL DAS FERRAMENTAS — V1

```
MISSAO     C-INT-AGRO-BENCH-01
ESPECIE    CLASSIFICACAO ARQUITETURAL — NAO REDESENHA UI, NAO MEXE NO PORTAL
MEDIDO_EM  2026-09-13
```

> **Nenhuma decisão de design, UI ou visual é tomada aqui.** Esta missão não
> toca em casco, portal, componentes, ícones ou layout. Classifica **função
> arquitetural**, que é outra coisa.

---

## 0 · ANTES DA TABELA: O ENUNCIADO LISTA 12, E EXISTEM 11

Medido em `docs/operacao/CENSO-CARDS-SENSORES-V1.md` (instrumento próprio da
casa):

```
CARDS_TOTAL                          = 11
ALIMENTADO_POR_REAL                  = 1     (windows · Finestre Colturali)
MISTURA_REAL_E_FIXTURE               = 6
SEM_FONTE_DECLARADA                  = 4
```

```
windows · meeting · market · competitors · science · portfolio · archive ·
future · voices · sources · field
```

**`LABEL INTELLIGENCE` não é um card.** O enunciado nomeia-a como ferramenta
actual, e ela não existe no portal. Existe **o material** dela — 
`research/adama-italy-product-intelligence-deep/LABEL-USES.json`, 
`FUNGICIDE/HERBICIDE/INSECTICIDE-LABEL-USES.json`, `LABEL-MANIFEST.json` — e
existe a tabela `registro_uso`. O que não existe é a ferramenta.

```
MATERIAL != FERRAMENTA. E UM CARD QUE NAO EXISTE NAO TEM PAPEL ARQUITETURAL:
TEM UMA DECISAO POR TOMAR.
```

---

## 1 · A CLASSIFICAÇÃO

Vocabulário do enunciado. Uma ferramenta **pode** ter mais de um papel — e cada
papel extra tem de ser justificado, porque um card com dois papéis é um card que
esconde uma fronteira.

### `windows` · **Finestre Colturali**
```
PAPEL PRIMARIO    CONTEXT LAYER
PAPEL SECUNDARIO  TRUTH LAYER — candidato, e ainda nao merecido
PORQUE            A janela e o unico eixo que torna qualquer achado agricola
                  ACIONAVEL (INT-LAW-104). Hoje ela e calendario agronomico;
                  para ser TRUTH LAYER precisa de ser a interseccao das quatro
                  janelas (fenologia ∩ infeccao ∩ rotulo ∩ preparacao).
ESTADO            o UNICO card ALIMENTADO_POR_REAL
NAO E             um sensor. Nao observa nada.
```

### `meeting` · **Radar delle Opportunità**
```
PAPEL PRIMARIO    ANALYTIC PRODUCT
PAPEL SECUNDARIO  DELIVERY PROJECTION
PORQUE            E o unico card que PROMOVE — e promocao e producao analitica,
                  nao apresentacao.
⚠️ O RISCO         E tambem o card com mais superficie para falsificar nivel.
                  Uma oportunidade de NIVEL A apresentada com a linguagem do
                  NIVEL D e o pior defeito possivel desta casa.
EXIGE             que o NIVEL (A·B·C·D) seja parte do objecto, nao do texto.
```

### `market` · **Polso di Mercato**
```
PAPEL PRIMARIO    CONTEXT LAYER
PORQUE            preco, area, producao e comercio sao contexto por defeito.
                  So viram MARKET FINDING com
                  CHANGE + MATERIALITY + CONTEXT + DECISION_AFFECTED
                  + ATTRIBUTION_LIMIT.
NAO E             ANALYTIC PRODUCT. Um dashboard macro nao vira intelligence
                  por estar num card.
MEDIDO            o censo ja apanhou aqui um `else` que inventava a prova que
                  faltava: «UM `else` NO FIM DE UMA ESCADA DE PROVA INVENTA A
                  PROVA QUE FALTA.»
```

### `competitors` · **Concorrenza**
```
PAPEL PRIMARIO    EVIDENCE SOURCE
PAPEL SECUNDARIO  SENSOR, na camada de comunicacao
PORQUE            SAO DUAS COISAS, e a casa ja o sabe: a camada REGULATORIA e
                  `CROSSING PROVED`; a camada de COMUNICACAO e `CONCEPT`.
                  Registo e autoridade. Comunicacao e alegacao.
EXIGE             que as duas camadas nunca partilhem a mesma contagem.
                  IT-T9-008: COMPANY_CLAIM != REGULATORY_FACT
```

### `science` · **Intelligence Scientifica**
```
PAPEL PRIMARIO    EVIDENCE SOURCE
PAPEL SECUNDARIO  VALIDATION WORKSPACE — candidato
PORQUE            E onde a independencia se mede, e medir independencia e
                  trabalho de validacao, nao de apresentacao.
BLOQUEADO POR     sem DOI/trial_id/afiliacao a atravessar a fronteira, ela nao
                  consegue distinguir tres papers de um ensaio.
```

### `portfolio` · **Portafoglio**
```
PAPEL PRIMARIO    TRUTH LAYER  (para o portfolio REGISTADO, e so para esse)
PORQUE            registo e facto de autoridade, com versao na chave
⚠️ A FRONTEIRA     REGISTERED != COMMERCIAL != AGRONOMIC RESPONSE != PIPELINE.
                  Sao quatro, e so a primeira e publica. O schema ja o trava:
                  `current_commercial_availability DEFAULT 'NAO_SEI'`.
NAO E             um catalogo de vendas.
```

### `archive` · **Archivio**
```
PAPEL PRIMARIO    GOVERNANCE / PROVENANCE
PORQUE            e a navegacao vertical ate a prova (INT-LAW-234). Sem ela,
                  toda a cadeia acaba num numero sem pai.
NAO E             um produto analitico. Nao conclui nada, e nao deve.
```

### `future` · **Archivio segnali**
```
PAPEL PRIMARIO    SENSOR
PAPEL SECUNDARIO  ANALYTIC PRODUCT — SO depois de um rastreio existir
⚠️ O DEFEITO       Hoje mistura duas especies que nao se misturam:
                    FACTO PRESENTE SOBRE O FUTURO   (caducidade de registo —
                                                     solido, datado, do regulador)
                    SINAL FRACO                     (algo que pode vir a ser)
                  A EFSA separa-os: a newsletter e sinal; a pest categorisation
                  e outra coisa. E 392 -> 27 diz o que acontece a quem nao separa.
ESTADO            SEM_FONTE_DECLARADA
```

### `voices` · **Voci dal Campo**
```
PAPEL PRIMARIO    SENSOR
PORQUE            e a unica superficie que pode trazer observacao humana de
                  campo — que os benchmarks todos consideram input de primeira
                  classe (Plantwise, Cropwise, xarvio)
⚠️ E O LIMITE      VOZ DE CAMPO NAO E INCIDENCIA. Sem metodo e sem denominador,
                  uma voz e NIVEL 1 da regua de doenca, e nunca mais do que isso.
                  E a propria CABI mede que ate em clinicas formais «os dados
                  sao muitas vezes incompletos».
ESTADO            SEM_FONTE_DECLARADA · o catalogo historico ja o tinha como
                  `CONCEPT — sem fonte de dado`
```

### `sources` · **Registro delle fonti**
```
PAPEL PRIMARIO    GOVERNANCE / PROVENANCE
PORQUE            COL-LAW-208: o Source Registry e a memoria da coleta
⚠️ O QUE FALTA     e onde a ESPECIE DA EVIDENCIA por fonte deveria estar
                  visivel. Ela existe (13 contratos), e nao aparece.
ESTADO            SEM_FONTE_DECLARADA — e e o card que MENOS podia estar assim
```

### `field` · **Rete Commerciale di Campo**
```
PAPEL PRIMARIO    FEEDBACK LOOP
PORQUE            e o unico sitio onde `FOLLOWED` e `ACTIONED` poderiam ser
                  medidos sem fabricar causalidade
⚠️ E O AVISO       e tambem a unica superficie que toca dado comercial. Ligar
                  CRM aqui sem contrato de acesso e proveniencia e o erro que o
                  §25 do enunciado proibe.
ESTADO            SEM_FONTE_DECLARADA
```

---

## 2 · O QUE A CLASSIFICAÇÃO REVELA

```
SENSOR                    3   future · voices · competitors(comunicacao)
EVIDENCE SOURCE           2   competitors(registo) · science
CONTEXT LAYER             2   windows · market
TRUTH LAYER               1   portfolio (so o registado)
ANALYTIC PRODUCT          1   meeting
VALIDATION WORKSPACE      0   (science e candidato)
GOVERNANCE / PROVENANCE   2   archive · sources
DELIVERY PROJECTION       1   meeting (secundario)
FEEDBACK LOOP             1   field
```

```
UM PRODUTO ANALITICO. ZERO ESPACOS DE VALIDACAO.
```

> **Esta é a forma de um sistema de entrega, não de uma máquina de produção
> analítica.** Dez superfícies que mostram, uma que conclui, nenhuma onde
> alguém valide antes de concluir. E a Bíblia candidata da Intelligence já
> escreveu o alvo contrário: *«uma máquina de produção analítica auditável»*.

---

## 3 · `DECISION INBOX` E `VALIDATION QUEUE` (`§33`)

O enunciado manda benchmarkar as duas hipóteses da pesquisa anterior e **não**
assumi-las como ferramentas.

### `VALIDATION QUEUE`

```
VEREDITO   NECESSARIA. E NAO E UMA FERRAMENTA.
ESPECIE    CAPABILITY + WORKFLOW, com estado proprio no objecto analitico.
```

**Prova externa, em quatro sistemas independentes:**

- EFSA: **selecção manual** por peritos é uma etapa nomeada do processo, entre o
  MedISys e o PeMoScoring. Não é uma tela: é um estado.
- Plantwise/POMS: harmonização e validação por **equipas dedicadas**, entre o
  formulário do plant doctor e a base.
- Crop Ontology: **curador nomeado pela comunidade** por cultura, que decide o
  que entra no trait dictionary.
- *Front. Plant Sci.* 2026: supervisão **em escalões** — e um escalão é uma fila
  com critério de entrada.

**Consequência:** o estado `PENDING_VALIDATION` pertence ao objecto analítico
(`INT-LAW-039`: a identidade e o estado da Opportunity independem da UI). Uma
fila é a **projecção** desse estado. Construir a tela antes do estado seria
inverter a ordem.

### `DECISION INBOX`

```
VEREDITO   NAO SE JUSTIFICA HOJE. DESCARTAR COMO FERRAMENTA.
ESPECIE    DELIVERY VIEW — e nem sequer a mais urgente.
```

**Porquê:** nenhum dos sistemas estudados tem uma «caixa de decisões». Têm:

- um **produto periódico** com o que mudou (newsletter EFSA, boletim MARS,
  Market Monitor AMIS);
- **alertas por objecto**, ligados à janela (xarvio spray timer, Cropwise
  tasks).

Ambos são projecções de estado, não um repositório novo. E a literatura de 2026
avisa exactamente contra a forma «caixa»: a métrica que mata um sistema de
alerta é a **carga de alertas falsos**, e uma caixa de entrada é a estrutura que
mais convida a enchê-la.

```
UMA CAIXA DE DECISOES SEM UM RASTREIO QUE SAIBA DESCARTAR
E UMA MAQUINA DE PRODUZIR RUIDO COM AR DE AGENDA.
```

**O que fica no lugar das duas:** o estado no objecto (`SCREENED` ·
`PENDING_VALIDATION` · `VALIDATED` · `DISMISSED`, com motivo e versão da regra) e
a janela (`HAS_WINDOW`). Quem precisar de uma lista, projecta-a.

---

## 4 · A RECOMENDAÇÃO ARQUITETURAL, EM UMA FRASE

```
NENHUMA FERRAMENTA NOVA.
UM ESTADO NOVO NO OBJECTO ANALITICO, E UM RASTREIO QUE SAIBA DIZER NAO.
```

E, antes das duas, a coisa que as sustenta e que não está aqui: a matéria-prima
atravessar a fronteira. Está no
[`../../docs/operacao/COLLECTION-P0-CHANGE-REQUEST.md`](../../docs/operacao/COLLECTION-P0-CHANGE-REQUEST.md).
