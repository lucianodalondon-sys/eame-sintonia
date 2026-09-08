# HANDOFF — BÍBLIA DA ENTREGA EAME

```
BIBLE_STATUS            DRAFT
IMPLEMENTATION          0
PRODUCTION_TOUCHED      0
MERGES                  0
DEPLOY                  0
DDL / DB WRITES         0
STORAGE / API PAGA      0
APIFY                   0

BRANCH                  research/delivery-bible-v1
HEAD_INICIAL            9d06d94be9758fea4a3147f9d5f156b96fcbeada
HEAD_FINAL              (o commit deste handoff)
BASE                    claude/integration-acervo-portal-v1 @ 9d06d94
PORTAL MEDIDO           claude/visible-intelligence-v1 @ a4fb6d8 · 2026-09-07 21:11 UTC
```

---

## §1 · OS ARTEFACTOS

| # | ficheiro | o que é |
|---|---|---|
| 1 | `docs/biblia/BIBLIA-DA-ENTREGA-EAME.md` | a Constituição (§1–§14) + o Registo (§15–§19) + a governança (§20–§23) + cinco testes de sobrevivência (§24–§28) |
| 2 | `docs/biblia/INVENTARIO-DAS-SUPERFICIES-ATUAIS.md` | as 13 superfícies medidas, ficha a ficha, com os três tempos |
| 3 | `docs/biblia/MATRIZ-INTELIGENCIA-PRODUTO-ENTREGA.md` | a matriz, a reavaliação das recusas antigas, o grafo M:N, a matriz de risco |
| 4 | `docs/biblia/REGISTRO-DE-PRODUTOS-E-FERRAMENTAS-DRAFT.md` | 11 produtos · 6 projeções · ciclo de vida · o Gate superfície a superfície · as 9 mudanças registadas retroativamente |
| 5 | `docs/biblia/CASOS-ADVERSARIAIS-DA-ENTREGA.md` | 28 cicatrizes reais, com data, prova e estado da guarda |
| 6 | `docs/biblia/PESQUISA-COMPARATIVA-SISTEMAS-DE-INTELIGENCIA-E-DELIVERY.md` | 15 sistemas · 13 com documentação primária · o que entra e o que fica de fora |
| 7 | `docs/biblia/HANDOFF-DA-BIBLIA-DA-ENTREGA.md` | este ficheiro |
| **8** | `docs/biblia/ADJUDICACAO-DO-BENCHMARK-V0.2.md` | **V0.2** · 19 princípios + 16 pulos + 12 recomendações, julgados um a um com `ACCEPT/REFINE/MERGE/REJECT` |
| **9** | `docs/biblia/GRAFO-M-N-DA-ENTREGA-V0.2.md` | **V0.2** · as 15 arestas, com autoridade, promoção, evidência exigida e comportamento em `UNKNOWN` |

**`REUSE FIRST` aplicado:** nada foi duplicado. O `PORTAL-CAPABILITY-INVENTORY.md`, o
`DIARIO-DE-DECISOES.md`, o `CONTRATO-DE-DESIGN-SINTONIA.md`, o
`ARQUITETURA-DE-PRODUTO-ATUAL.md` e os contratos em `data/samples/` continuam a ser os
donos do que dizem. A Bíblia **cita e liga**, não copia.

---

## §2 · AS RESPOSTAS DO FECHO ORIGINAL

**A · HEAD inicial e final.**
Inicial `9d06d94`. Final: o commit deste handoff em `research/delivery-bible-v1`.
Árvore limpa no início. `claude/integration-acervo-portal-v1` **não foi alterada**.

**B · Quantas superfícies reais existem hoje?**
**13.** Doze no menu, uma fora dele (`Signal Archive`, com rota, vista e três caminhos de
acesso). Mais 15 vistas de detalhe e legadas em `CAPABILITY_OF`, e 59 colecções no modelo.

**C · Quais?**
Opportunity Radar 17 · Portfolio 173 · Future Radar 44 · Label Intelligence 166 ·
Crop Windows 29 · Market Pulse 157 · Field Voices 79 · Competitor Watch 577 ·
Scientific Intelligence 88 · Archive 1114 · Source Register 194 ·
Field Sales Channel 18 (DEMO) · **+ Signal Archive 3, fora do menu**.

**D · Quantas têm decision question explícita?**
**4 de 13** — S-01 (§MT2) · S-03 (contrato de dado) · S-04 (escrita no payload) ·
S-11 (parcial, nível 2). Mais uma parcial: S-09 (CAP-017, que **não cobre a Itália**).

**E · Quantas têm Product Contract explícito?**
**1 completo** (S-04 Label Intelligence) · **2 parciais** (S-01, S-03) · **10 sem**.

**F · Quantas nasceram principalmente de dataset/capacidade?**
**6 de 13**: Market Pulse · Field Voices · Scientific Intelligence · Archive ·
Source Register · Crop Windows.
Nasceram de pergunta: **3** (S-01, S-03, S-04). De fixture: **1** (S-12).
Indeterminado: **3**.

**G · Que conflitos portal × arquitetura foram encontrados?**
**Oito**, todos registados sem escolher lado — C-01 a C-08 no Registo §8.
Os dois mais caros: **C-05** (duas linhagens vivas de portal; nada declara qual é o
publicado) e **C-06** (Linha A × Linha B sobre o que é uma oportunidade;
`surface-contract.mjs` está **3/8** desde `a4508ef`, e é idêntico no DEMO_HEAD intocado,
portanto não é regressão).

**H · Quais parecem candidatas a permanecer ferramentas?**
`Opportunity Radar` (confiança **A**) e `Label Intelligence` (confiança **A**).
`Future Radar` como exploratória (**A**), com caminho para canónica se os 13 campos
obrigatórios do cartão passarem a viajar.

**I · Quais parecem supporting views?**
`Signal Archive` (**A**) · `Crop Windows` como componente temporal (**M**) ·
`Market Pulse` como contexto (**M-A**) · `Source Register` como `EVIDENCE_EXPLORER`
(**A**, e é uma classe nova) · `Archive` como investigação ou admin (**M-A** que não é
ferramenta, **B** em qual das duas) · `Competitor Watch` como camada transversal com
vista de investigação (**M-A**).

**J · Quais precisam de medição antes de decidir?**
**Sete**: Portfolio · Crop Windows · Market Pulse · Field Voices ·
Scientific Intelligence · Archive · Source Register.
Três delas ficam **sem recomendação** — Portfolio, Field Voices e Scientific
Intelligence. `TELEMETRY_EXISTS = NO` é a causa comum.

**K · A Bíblia fossiliza MT1/MT2/MT3?**
**NÃO.** MT1/MT2/MT3 estão nomeados em §1 na lista explícita do que **não é**
constitucional. E o §28 testa nove mudanças reais de produto: a Constituição não proibiria
nenhuma e obrigaria a registar as nove.

**L · Qual é a essência que não muda?**
As leis de **fronteira** (`INTELLIGENCE ≠ CASCO`), **evidência**, **autoridade**
(documento nomeado e datado, ou `UNKNOWN`), **rastreabilidade**, **versionamento**,
**admissão** e **desconhecimento** (`UNKNOWN` continua `UNKNOWN`).
**O número de ferramentas não é essência. O critério de admissão é.**

**M · Como nasce uma nova ferramenta?**
Pelo `TOOL ADMISSION GATE` (§8), 16 perguntas. Três resultados possíveis:
`ADMITTED_AS_CANONICAL_TOOL`, `ADMITTED_AS_EXPLORATORY`, `NOT_ADMITTED_YET` — **que não é
rejeição**: é uma pergunta em aberto, com dono e data. Testado em §24 com
`RESISTANCE INTELLIGENCE`: **0 linhas de Constituição alteradas**.

**N · Como uma ferramenta muda de papel?**
Muda-se `SURFACE_CLASS` no Registo Vivo, com `FROM_STATE` · `TO_STATE` · `EVIDENCE` ·
`WHY`. Testado nas duas direções com Field Voices (§25). **A Constituição não quebra em
nenhuma delas.**

**O · Como duas ferramentas podem ser fundidas?**
Estado `MERGED` (§9), com histórico preservado e razão escrita. **Já aconteceu**:
`casa.html` → vista `radarfuturo`. O código não foi apagado; o dono do dado não mudou.
O que faltou foi o registo — e é o que o Registo Vivo passa a exigir.

**P · Qual é o contrato INTELLIGENCE → DELIVERY?**
```
INTELLIGENCE PRODUCT (§5, envelope selado, versionado, com FORBIDDEN_CLAIMS)
        ↓ atravessa
DELIVERY ELIGIBILITY GATE (§4, lei com dono, classes, e o recusado que NÃO desaparece)
        ↓ materializa-se em
DELIVERY PROJECTION (§6, descartável, regenerável, IS_SOURCE_OF_TRUTH = false)
        ↓ é lida por
PRODUCT SURFACE (§7, sob Product Contract)
```

**Q · O que são os «potes», tecnicamente?**
`DELIVERY_PROJECTION` — uma **materialized view** sobre Intelligence Products, com
contrato de produto por cima. O nome foi escolhido por eliminação, não por estética:
`READ MODEL` importaria a expectativa de um *write model* que não existe;
`MATERIALIZED VIEW` é termo de base de dados sem noção de contrato.
**Seis já existem** — `PORTAL_MODEL_V21`, `MEETING_SNAPSHOT`, `RELEVANCE_VERDICT`,
`CASA_LEDGER`, `LABEL_PAYLOAD`, `DISPLAY_LAYER` — todos com gerador e portão, e nenhum se
chama pote.

**R · Eles são source of truth?**
**NÃO.** É lei constitucional (§6, P-01…P-04) e a formulação vem citada do padrão:
*«completely disposable because it can be entirely rebuilt from the source data stores …
never updated directly by an application.»*
E com uma exigência a mais que o padrão não tem: **a regeneração é PROVADA, byte a byte,
por portão.** `site_v21_ingest.py` já o faz.

**S · Um mesmo Intelligence Product pode alimentar várias ferramentas?**
**SIM**, e é constitucional (M:N, §6). Medido: `LABEL_AUTHORISED_USE` alimenta
`Label Intelligence`, `Opportunity Radar` (o elo do rótulo), `Portfolio` (`STRENGTH`) e o
`Ask` (B11, B35, e as recusas B10 e B28). **Quatro superfícies, um produto, zero
recálculos.**

**T · O casco pode calcular novo judgment?**
**NÃO.** `L-11 · UI ≠ INTELLIGENCE ENGINE`.
O casco pode ordenar, filtrar, paginar, traduzir por dicionário declarado, agrupar por
campo existente, esconder por permissão, e dizer que não sabe.
Já implementado: *«este ficheiro transporta o veredito para o browser, que nunca o
recalcula.»*

**U · O Ask pode contornar os Product Contracts?**
**NÃO.** §11.2: herda os `FORBIDDEN_CLAIMS` de cada produto que cita e a **menor**
confiança; não vê o que uma superfície não veria (mesma permissão, mesmo país, mesmo
`AS_OF`); e uma recusa só cai **por fonte nova**, nunca por régua mais frouxa.
O teste de regressão já existe: as 10 recusas do benchmark.

**V · Como funciona o frescor?**
Composto, nunca um carimbo. Seis relógios (`FACT_TIME`, `PUBLISHED_AT`, `OBSERVED_AT`,
`COLLECTED_AT`, `DERIVED_AT`, `PRODUCT_AT`) mais `PUBLISHED_TO_UI_AT` e `AS_OF`, que não é
um relógio mas uma pergunta — respondida pela regra de seleção em 4 passos, já escrita em
`CAPTURE-VS-REGISTRATION-CONTRACT-V1`. Nove leis, F-01 a F-09.
**Modelo de referência medido: `LABEL_PAYLOAD`, com seis relógios separados.**

**W · Como funciona a supersessão?**
Cinco verbos que afirmam coisas diferentes sobre a versão anterior: `SUPERSEDES` ·
`CORRECTS` · `RETRACTS` · `INVALIDATES` · `REFUTES`.
`WHY_CHANGED` é obrigatório e não-vazio. Uma afirmação retratada é **corrigida no lugar
onde estava**, com data e motivo — não apagada.
E `V-02`: quando a **lei** muda e o **dado** não, o `WHY_CHANGED` nomeia a régua, não a
fonte. Medido: `13 → 17` sobre os mesmos 43 casos.

**X · Como a decisão/feedback volta ao sistema?**
§15. Engagement (`SEEN`, `OPENED`, `INVESTIGATED`, `DISMISSED`) e decision value
(`VALIDATED`, `ACTIONED`, `DECISION`, `OUTCOME`, `FEEDBACK`) **nunca se somam nem
aparecem no mesmo número**. `T-03`: feedback volta como **facto novo**, com fonte e data,
nunca como juízo. `T-04`: a telemetria não reordena a Home sem lei declarada — um ranking
que aprende com cliques converge para o que é clicável, não para o que é decisivo.
**Estado medido: `TELEMETRY_EXISTS = NO`.**

**Y · Market Development foi tratado explicitamente?**
**SIM.** §16 e §17. `MD` é o decisor central e o único que aparece nas cinco áreas de
informação. A régua de seis passos que já existe é adotada como contrato de saída mínimo
para qualquer produto dirigido a MD. E o **teste dos quatro públicos** foi aplicado a dois
produtos reais, com a lei que dele sai:
**a parte comum é o produto; a parte que difere é o pote.**
É essa frase que impede uma ferramenta por departamento.

**Z · Que sistemas externos ensinaram algo útil?**
Quinze estudados, treze com documentação primária. Os cinco que mais transferiram:

1. **Materialized View** — deu a definição literal do que é um pote e as suas quatro leis;
2. **ICD 203** — deu o léxico fechado de likelihood e a proibição de o misturar com
   confiança;
3. **OpenCTI** — deu a lei da menor confiança;
4. **Palantir Foundry** — confirmou industrialmente que um objeto tem muitas vistas por
   fluxo de trabalho, e que aplicações falam com a ontologia, nunca com a origem;
5. **Anti-Corruption Layer** — nomeou o que o `DISPLAY-LAYER-V1` já fazia melhor do que a
   fonte descreve.

**AA · Que padrões externos NÃO servem ao SINTONIA?**
O **risk score 0–99** do Recorded Future (o repositório já decidiu, com motivo escrito,
que um número único esconde qual camada sustenta o tema) · a **previsão de evolução** do
Dataminr (o backtest mediu 1 safra no melhor caso, zero em dois de três) · o **command
model** e o nome «read model» do CQRS (o casco não escreve) · o **event store e o replay**
do Event Sourcing (fontes oficiais não se re-executam; o ROPF sobrescreve o seu próprio
passado) · **STIX e Admiralty** do OpenCTI (não há com quem trocar, e a régua de 9
dimensões é mais auditável que uma letra) · **Actions** do Foundry (`EXTERNAL-ONLY`) ·
**«no hallucinations»** da AlphaSense (é uma afirmação que nenhum portão prova).

**AB · Que pulos do gato foram descobertos?**
Quinze, em §30. Os cinco que mudam arquitetura:

- **PG-08** — uma inteligência alimenta muitas ferramentas, e **isso não a rebaixa**.
  `IS_INPUT_TO_ANOTHER_TOOL` não é critério; `HAS_OWN_DECISION_QUESTION` é.
- **PG-11** — `SURFACE_EXISTS`, `SURFACE_ROUTABLE`, `SURFACE_LISTED` e `SURFACE_REACHABLE`
  são quatro estados independentes.
- **PG-12** — o funil precisa de contador em cada degrau. `2154 → … → 65`.
- **PG-13** — o termo da busca não é o achado. 87/88 `QUERY_*`, 37/88 `PROVED_*`.
- **PG-15** — uma página que nenhuma rota alcança é uma página que nenhum portão lê.

**AC · Que anti-padrões foram formalizados?**
Dezanove (§19). Dois são novos e saíram da medição: **AP-17 `SEARCH TERM READ AS FINDING`**
e **AP-19 `VALUE EXISTS AND VISIBLE = NO`**.

**AD · Que perguntas continuam `UNKNOWN`?**
Catorze (§29). As três mais caras: **U-01** (qual das duas linhagens é o produto),
**U-02** (quem gerou as 29 janelas — gerador e insumo ausentes de 979 commits) e
**U-14** (sem telemetria, nenhuma superfície pode entrar em `PILOT`).
Acrescenta-se **U-12**, que a missão pressupunha resolvida: **a Bíblia da Coleta e a
Bíblia da Inteligência não existem neste repositório** (`grep -ril biblia` devolve 0
ficheiros). O System Map do §18 refere duas peças ainda por escrever.

**AE · A Bíblia está:** `DRAFT`.

**AF · Implementação feita:** `0`.

**AG · Produção tocada:** `0`.

**AH · Branch pushada:** `research/delivery-bible-v1`, sem merge.

**AI · Qual será o próximo ponto de reconciliação?**
Depois de a **Collection Foundation** fechar e de a **Bíblia da Inteligência** ganhar
arquitetura completa, reconciliar `COLLECTION → INTELLIGENCE → DELIVERY` **antes** de
implementar a ponte e o casco final.
**Com uma pré-condição descoberta nesta pesquisa:** as duas Bíblias a montante ainda não
existem como ficheiros. A reconciliação a três não pode ser marcada antes de elas
existirem.

---

## §3 · AS RESPOSTAS DA CORREÇÃO DE ROTA

**1 · Quantas superfícies `CURRENT` foram realmente medidas?**
**13** — as 12 do menu e a 13ª fora dele. Medidas montando o modelo num contexto Node e
lendo `ITALY_APP_MODEL.counts`, não lendo um ecrã.

**2 · A lista visual reportada de 12 bateu com o código?**
**SIM — 12 de 12 contadores, exatamente, e na mesma ordem.**
Mas **não neste HEAD**: bateu em `claude/visible-intelligence-v1 @ a4fb6d8`.
Nesta branch, `Label Intelligence` aparece **0 vezes** em `portale.html`.
**A divergência era de branch, não de número.**

**3 · Que divergências?**
Quatro de arquitetura, além dos oito conflitos:

- **D-1** · `#field` não está em `AMMESSE`: o item de menu abre por clique e um refresh
  cai em `#meeting`. A voz continua desenhada. Intenção e código discordam.
- **D-2** · `Signal Archive` (3) tem rota, vista e três caminhos, e **não tem voz de
  menu** — deliberado e documentado. Logo há **13 superfícies, não 12**.
- **D-3** · 12 vozes de menu para **59 colecções** no modelo (20%).
- **D-4** · 27 ids de vista em `CAPABILITY_OF` para 12 capacidades — 15 são detalhes e
  legados, e **4 legados renderizam com `legacyCaseId` a resolver 0 de 43**.

**4 · Qual é a diferença entre `TOOL` e `SURFACE`?**
Uma `SURFACE` é qualquer coisa que se renderiza. Uma `TOOL` é uma `SURFACE` que **tem uma
decision question própria** e um Product Contract.
Toda tool é uma surface; a recíproca é falsa. E há mais três estados que não se confundem
com nenhum dos dois: `SURFACE_ROUTABLE`, `SURFACE_LISTED`, `SURFACE_REACHABLE` (PG-11).

**5 · Quais das 12 têm decision question comprovada?**
**4**: S-01 · S-03 · S-04 · S-11 (parcial). Mais S-09 parcial, cuja capacidade
não cobre a Itália.

**6 · Quais têm Product Contract?**
**1 completo** — `Label Intelligence`. **2 parciais** — `Opportunity Radar` (tem lei de
elegibilidade e contrato de saída, não tem contrato de ferramenta) e `Future Radar` (tem o
melhor contrato de **dado** do repositório, que se recusa a definir UI).

**7 · Quais continuam `UNKNOWN` arquiteturalmente?**
**Sete**: Portfolio · Crop Windows · Field Voices · Scientific Intelligence · Archive ·
Signal Archive · Field Sales Channel. Três delas ficam **sem recomendação**, e isso é o
resultado correto: sem telemetria, ninguém tem prova para decidir.

**8 · O que é a Label Intelligence, segundo a evidência?**
**É um `INTELLIGENCE PRODUCT` selado a servir uma `DELIVERY_PROJECTION` — e é a única
superfície do portal que já é isso hoje.**
166 produtos, 210 objetos, 54 versões, 22 regras versionadas (`REGRAS.md@5`),
`CONTENT_SHA256` recalculado por portão a cada execução, 7 coberturas contadas
separadamente com a nota «nenhuma implica a seguinte», `PHI_COVERAGE = 0` **por decisão
declarada**, e — o que mais importa — **`FORBIDDEN_CLAIMS` escritos no próprio payload**:
não responde `SCIENTIFIC_INTELLIGENCE`, `DISEASE_INTELLIGENCE`, `OPPORTUNITY` nem
`COMPETITOR_INTELLIGENCE`, **e não pode ser feita responder por junção**. Portão G-01
fechado: nunca envia nada ao campo sozinha.
**Recomendação: `CANONICAL_TOOL` + `DELIVERY_PROJECTION`, em simultâneo. Confiança A.**
O facto de alimentar o Radar não a rebaixa — é PG-08.

**9 · O que é o Future Radar?**
`EXPLORATORY_TOOL` com a **melhor decision question** («o que pode importar depois?») e o
**pior payload**: 44 identificadores, e 12 dos 13 campos obrigatórios do cartão não viajam
no handoff. Só 3 dos 44 têm conteúdo rico, e é conteúdo de sensor.
**44 «fichas» é o que se pode dizer hoje; 44 fichas ricas não existem em lado nenhum deste
repositório.** Caminho para canónica: fazer os campos viajarem. É trabalho a montante.

**10 · O que é o Source Register?**
**`EVIDENCE_EXPLORER`** — e é por causa dele que a classe passa a existir (§10 V-01).
Não é ferramenta (não responde a decisão de negócio), não é admin (é para o cliente), não
é context view (não contextualiza — **prova**). Tem uma pergunta própria de outra
natureza: «de onde vem cada coisa?», **incluindo as fontes bloqueadas, com motivo**.
A proibição da home («contador de fontes») é sobre a **home**, não sobre a superfície.
Foram lidas como a mesma coisa e não são. **Confiança A.** Conflito C-02 aberto.

**11 · O que é o Archive?**
Um índice derivado de 1114 linhas, sem ficha, sem contrato e sem decisão em nenhum
documento do repositório. Não traz facto próprio — o modelo já o sabe e conta-o à parte
(`indexRows`). E existe um quarto acervo, `searchIndex` com 1655 entradas em 17 famílias,
que já indexa tudo o que os outros três dizem arquivar.
**`INVESTIGATION_VIEW` ou `ADMIN/DIAGNOSTIC`** — e a diferença entre as duas é **quem o
abre**, que é a única coisa que não foi medida. **Confiança M-A em «não é ferramenta»,
B em qual das duas.**

**12 · O Field Sales Channel continua corretamente `DEMO`?**
**SIM, e é o melhor exemplo do repositório.** Quatro camadas de honestidade: rótulo no
ecrã · grupo de menu separado · cor distinta (âmbar, não o verde corporativo) ·
`provenance = SYNTHETIC_DEMO` no modelo, contado à parte (`demo: 103`).
**O rótulo está no dado, não só na tela.**
Duas ressalvas: falta-lhe uma data de revisão (`LC-04`), e a rota `#field` não sobrevive a
um refresh.

**13 · A arquitetura antiga MT1/MT2/MT3 continua autoridade atual, histórica, parcial, ou
precisa de decisão?**
**PARCIAL, e precisa de decisão.** Medido, por partes:

| parte | estado |
|---|---|
| MT2 → Opportunity Radar | **ATUAL** — é a única autoridade escrita e funciona |
| MT1 → «REGULATORY & EXPIRY EXPOSURE» | **ATUAL como pergunta, sem superfície.** `REGULATORY_EXPOSURE` existe como produto e vive espalhado dentro do Portfolio. MT1 é hoje uma pergunta sem tela |
| MT3 → PUBLIC ACTIVATION GAP | **HISTÓRICO** — não tem superfície no portal medido |
| «duas ferramentas + uma exploratória» | **HISTÓRICO.** É `CURRENT PRODUCT DECISION` de 29/08, e o portal de 07/09 já não a segue |
| SUPPORTING ENGINE «não no menu» | **PARCIALMENTE REVOGADO por medição.** O critério que usou — ser input de outra ferramenta — não é um critério de classificação (PG-08) |
| as proibições (DO NOT BUILD, o que o design não pode fazer, os claims proibidos) | **ATUAIS E VÁLIDAS.** Nenhuma foi contestada por nenhuma medição desta pesquisa |

> **A parte prescritiva envelheceu. A parte proibitiva não envelheceu nada.**
> É um resultado sobre o tipo de documento: **contratos que dizem «não podes» duram
> mais do que contratos que dizem «serão três».**

**14 · Alguma ferramenta foi recusada só porque um documento antigo não a previa?**
**NÃO. Zero.** Cinco superfícies com `AUTHORITY = NO` foram reavaliadas contra os seis
testes. Resultado: **1 recusa confirmada** (Market Pulse — e é o único caso em que o
contrato antigo e a medição de hoje concordam), **3 que têm de ser reabertas** (Field
Voices, Scientific Intelligence, Source Register) e **1 mal lida** (Competitor Watch: o
contrato proíbe o número único e o ranking, não a superfície).

**15 · A Bíblia permite novas ferramentas?**
**SIM.** Testado em §24 com `RESISTANCE INTELLIGENCE`, escolhida por medição:
`resistance` já existe no modelo com 34 registos e é a única colecção com nome de problema
agronómico **sem superfície nenhuma**. Passa as 16 perguntas. **0 linhas de Constituição
alteradas.**

**16 · Uma nova ferramenta muda a Constituição?**
**NÃO** — salvo se revelar um contraexemplo estrutural real. E `§20` exige exatamente
isso: **sem `COUNTEREXAMPLE` não há emenda.** Opinião, gosto, conveniência de calendário e
«o cliente pediu» não são contraexemplos.

**17 · O que muda normalmente?**
`LIVING PRODUCT REGISTRY` + `PRODUCT CONTRACTS` + `PROJECTIONS`.

---

## §4 · PALAVRAS FÁCEIS PARA O LUCIANO

**1 · O portal de hoje foi realmente estudado?**
Sim, e de duas maneiras. Primeiro medi o código desta branch — e o que o senhor descreveu
**não estava lá**. Não desisti nem inventei: procurei nas 62 branches do repositório até
encontrar a que corresponde ao que o senhor está a ver. Depois carreguei os ficheiros do
portal num motor JavaScript e li os números **do próprio programa**, em vez de acreditar
num ecrã. **Os doze números batem, um a um, e pela mesma ordem.** O senhor viu bem; a
lista antiga é que era de outro dia.

**2 · Alguma ferramenta atual foi descartada só porque o contrato antigo não gostava dela?**
**Não. Nenhuma.** Peguei nas cinco que um documento antigo tinha recusado e voltei a
julgá-las com os factos de hoje. Só uma continua recusada — o Market Pulse — e não é por
teimosia: é o único caso em que o documento antigo e a medição de hoje dizem a mesma
coisa. Três têm de ser reabertas. E uma tinha sido **mal lida**: o contrato da
concorrência não proíbe a tela; proíbe o **número grande** ao lado do nome.

**3 · Alguma tela atual virou automaticamente ferramenta?**
**Não.** Fiz o contrário: quatro têm pergunta própria comprovada, uma tem contrato
completo, e sete continuam **por classificar** — porque não há prova para as classificar.
Escrever «é isto» sem prova seria o defeito que este repositório existe para não cometer.

**4 · A Bíblia permite ferramentas novas?**
**Sim.** E provei-o em vez de o afirmar: inventei uma — *Resistance Intelligence* — passei-a
pelas dezasseis perguntas de admissão, e **não foi preciso mudar uma linha da
Constituição**. Escolhi-a por medição, não por gosto: os dados dela já estão no sistema,
34 registos, sem tela nenhuma.

**5 · O número de ferramentas é fixo?**
**Não.** Está escrito, com todas as letras, na lista do que **não** é constituição:
«MT1/MT2/MT3», «duas ferramentas principais», «o SINTONIA tem doze superfícies».
Podem ser doze, vinte ou seis.

**6 · O que é fixo?**
As leis de fronteira (a inteligência não sabe desenhar; o casco não sabe julgar), a
evidência, a autoridade, a rastreabilidade, o versionamento, a admissão — e o direito de
dizer **NÃO SEI**.

**7 · Se amanhã surgir uma ferramenta ótima, o que acontece?**
Entra pelo portão de admissão. Se responder às dezasseis perguntas, é canónica. Se
responder com alguns *não sei* declarados, é exploratória — e o ecrã di-lo. Se ainda não
responder, fica com o nome «ainda não admitida», **que não é uma recusa**: é uma pergunta
em aberto, com dono e com data.

**8 · Precisamos de reescrever a Bíblia inteira?**
**Não.** Testei nove mudanças **reais** que aconteceram no portal em 48 horas. A
Constituição não proibiria nenhuma delas. Obrigaria a **registar** as nove — e apanharia
uma como defeito, que é uma entrada de menu que não sobrevive a um recarregamento da
página.

**9 · O que muda?**
O Registo Vivo e os contratos de cada ferramenta. É o ficheiro que se mexe todas as
semanas, e mexer nele **não é** mexer na Constituição.

**10 · A essência continua?**
Sim. E há uma coisa que o senhor deve saber, porque é o melhor resultado desta pesquisa:
**a prática do repositório já ultrapassou a doutrina.** A ferramenta mais nova — a Label
Intelligence, de anteontem — nasceu com selo criptográfico, vinte e duas regras
versionadas, sete coberturas contadas em separado e a frase «uso autorizado não é
oportunidade comercial» escrita dentro do próprio dado. Nenhum documento lhe exigia isso.
**A Bíblia não teve de inventar o padrão: teve de o nomear e de o pedir às outras onze.**

E há uma coisa que falta, e é uma só: **ninguém sabe quem usa cada tela, nem para quê.**
Sete das treze decisões ficaram sem recomendação por causa disso. Não é falta de dados —
é falta de saber o que as pessoas fazem com eles. É a dívida número um da entrega, e é a
única coisa desta lista que exige construir, e não escrever.

---

## §5 · O QUE FICA POR FAZER

Do `REGISTO §9`, por custo de não fazer:

```
 1  PUBLICATION_MANIFEST por build         resolve C-05         baixo
 2  IS_SOURCE_OF_TRUTH = false nas 6       lei que se lê        trivial
 3  DROPPED_FIELDS nas 4 que não o têm     AD-21, o funil       médio
 4  responder às perguntas 13–16 do Gate   decisões escritas    baixo
 5  LC-04: datas de revisão                inventário           trivial
 6  registar RV-002, RV-006, RV-007        AD-05                trivial
 7  TELEMETRIA DE DECISÃO                  desbloqueia 7        ALTO — é o único
                                           recomendações e             item de engenharia
                                           todos os PILOT
 8  achar o gerador das 29 janelas         U-02                 desconhecido
 9  reconciliar 166 × 173                  C-08                 médio
10  FORBIDDEN_CLAIMS para os 6 produtos    C-01 do contrato     baixo
    que não os têm
```

**Nove das dez são escrita, não código.**

---

## §6 · DECLARAÇÃO FINAL

```
BIBLE_STATUS ................ DRAFT
IMPLEMENTATION .............. 0
PRODUCTION_TOUCHED .......... 0
MERGES ...................... 0
DEPLOY ...................... 0
DDL · DB WRITES · STORAGE ... 0
API PAGA · APIFY ............ 0

PORTAL ALTERADO ............. NÃO
HTML · CSS · JS ............. NÃO
COLETA · INTELIGÊNCIA ....... NÃO
OPPORTUNITY · FIELD VOICES .. NÃO
SCORING · SINAIS ............ NÃO

BRANCHES OPERACIONAIS ....... intocadas
BRANCH DESTA MISSÃO ......... research/delivery-bible-v1
```

> **A BÍBLIA DA ENTREGA NÃO É UMA LISTA DAS FERRAMENTAS DE HOJE.**
> É a constituição que permite ao SINTONIA criar, testar, promover, mudar, fundir e
> aposentar ferramentas sem perder evidência, autoridade, rastreabilidade, história,
> `UNKNOWN` — e sem perder a separação entre **INTELIGÊNCIA** e **CASCO**.
>
> O portal de 08/09 entrou aqui como **evidência, cicatriz e primeiro caso real**.
> **Não como limite.**

---

# PARTE V0.2 · SÍNTESE COM O BENCHMARK

```
BIBLE_STATUS       DRAFT · V0.2      SUPERSEDES V0.1 (não a apaga)
IMPLEMENTATION     0      PRODUCTION 0      MERGES 0      DEPLOY 0
BENCHMARK_INPUT    research/product-tools-benchmark-v1 @ 6ef8e70
ARTEFACTOS NOVOS   ADJUDICACAO-DO-BENCHMARK-V0.2.md · GRAFO-M-N-DA-ENTREGA-V0.2.md
ARTEFACTOS EDITADOS BIBLIA (PARTE V) · INVENTARIO (adenda A) · REGISTO (adenda R0.2)
```

## §7 · AS 33 RESPOSTAS

**1 · O baseline 12/12 foi reproduzido em `a4fb6d8`?**
**SIM.** `BASELINE_12_OF_12_REPRODUCED = YES`. Não foi releitura: foi um segundo
carregamento, com *script* novo, que avalia **as mesmas expressões que `portale.html`
usa** para desenhar cada voz — incluindo `MEETING_SURFACE.build()`, que a primeira
medição não tinha corrido. Registado como **`MEASURED_VISUAL_BASELINE_2026-09-08`**,
**não** como `CANONICAL CURRENT HEAD`.
*E as duas medições anteriores estavam ambas certas:* o benchmark mediu a partir de
`main@df165da9` e escreveu «não reproduzível **nas linhas inspecionadas**», que é a forma
correta. Daí a lei `L-EPI-05`.

**2 · Qual é a fotografia medida?**
`a4fb6d81681094925ccfd1638bc7386cbec6f4d4` · `claude/visible-intelligence-v1` ·
2026-09-07 21:11:51 UTC. Doze vozes de menu, mais `Signal Archive` fora dele = **13
superfícies navegáveis**, 27 ids de vista, 59 colecções. Tabela completa em
`INVENTARIO §A.2`.

**3 · Que recomendações do benchmark entraram na Constituição?**
Oito leis (`L-18`…`L-25`) e quinze artigos (`§32`…`§46`): os três registos
epistemológicos, o modelo temporal com dono por campo, `Opportunity` como interseção, o
contrato de card 3s/30s/3min, o Evidence Drawer, a Home como fila, o alerta por transição,
os briefs por papel, a superfície de ação, a métrica de valor em três níveis, oito
anti-padrões, o grafo M:N e o System Map ampliado.
Dos 19 princípios: **10 `ACCEPT`, 4 `REFINE`, 5 `MERGE`**.

**4 · Quais entraram apenas no Registo Vivo?**
As doze reclassificações de superfície (`R0.2 §R2.1`), as cinco entradas `RV-010`…`RV-014`,
os dez contratos de produto que passam a ser exigíveis, o `WORKFLOW_CANDIDATE WC-01`, e o
princípio 15 («produtos são respostas»), que é uma decisão sobre **uma** superfície e não
uma lei de fronteira.

**5 · Quais foram rejeitadas?**
Quatro, com motivo escrito em `ADJUDICACAO §5`:
`R-01` «a cadeia linear é uma ilusão» **na forma absoluta** — revogaria a lei fundadora do
README sem contraexemplo; aceite como distinção: **linear na origem, M:N no consumo**.
`R-02` `Brief Hub` como ferramenta — falha a pergunta 1 do Gate.
`R-03` `Evidence Portal` — seria o quinto acervo.
`R-04` `Score Center` e portais por departamento — contrariam `L-19` e `L-16`.

**6 · A Home virou o quê?**
**`DECISION / ATTENTION INBOX`** — uma fila por estado de ação no tempo, filtrada por
papel, geografia, cultura e itens seguidos (§38). Entra como **hipótese forte**
(`OWNER_INTENT` + `BENCHMARK_EVIDENCE`), não como `PROVEN_VALUE`.

**7 · Quem calcula a sua prioridade?**
**Não é a Home.** `H-06` endurece a trava: a `DELIVERY_ELIGIBILITY` (§4) decide **o quê**
entra, o estado de ação no tempo (§34) decide **onde** entra, e a régua de desempate
declarada decide a ordem dentro do estado. Os três vivem na Inteligência.
`HOME PROJECTION ≠ INTELLIGENCE ENGINE`.

**8 · O Opportunity passou a organizar-se por que modelo temporal?**
Por **estado de ação no tempo**: `AGIR AGORA → PREPARAR AGORA → PRÓXIMA JANELA →
MONITORAR/VALIDAR`, com desempate por factores **visíveis e separados** — tempo restante,
consequência de perder a janela, prontidão da resposta ADAMA, frescura da evidência,
responsabilidade geográfica.
**A arquitetura é `ACCEPT`; os nomes são `NOT_CANONICAL`** e exigem validação com
utilizadores ADAMA (`U-15`).
**E o achado:** a partição por estado de ação **já existe no motor** —
`ACT_NOW 2 · VALIDATE_NOW 4 · FUTURE_PREPARATION 7 · WATCH 21 · TO_VALIDATE 9` — **e não
é a que a barra conta** (`OPPORTUNITA 17`). É o conflito `C-06`, agora com números dos
dois lados.

**9 · Quem é dono de `TIME_TO_ACT`?**
A **Inteligência**. E hoje **o campo não existe**: `WINDOW_OPEN_NOW = UNKNOWN` em
**41 de 43**, `WINDOW_DEFINED = NO` em **27 de 43**.
`DEPENDENCY_ON_INTELLIGENCE_BIBLE = OPEN`.

**10 · Quem é dono de `TIME_TO_PREPARE`?**
A **Inteligência**, e depende de `COMMERCIAL_LEAD_TIME`, que **não existe em lado nenhum
e não tem dono** (`U-17`). É a consequência direta de `L-18`: a janela comercial abre
antes da agronómica, e ninguém mediu quanto antes.

**11 · O que ainda depende da Bíblia da Inteligência?**
Sete arestas do grafo (`GRAFO §5`) e dez campos de juízo:
`TIME_TO_ACT` · `TIME_TO_PREPARE` · `WINDOW_STATE` · `ADAMA RESPONSE` · `WHAT TO DO` ·
`EVIDENCE MATURITY` · `SCIENCE MATURITY` · o que conta como
`CURRENT_FIELD_CONFIRMATION` · o que é um evento «material» de concorrente · quando é que
feedback de campo passa a evidência.
**Mais o objecto `CLAIM`, que não existe** — e sem ele o Evidence Drawer não tem a que se
ligar.

**12 · O Portfolio passou a ser definido como quê?**
**`OPERATIONAL RESPONSE MEMORY`** (`RV-010`), com a pergunta declarada pelo dono e o campo
novo `WHERE IS THIS PRODUCT RELEVANT IN SINTONIA NOW?` — **como projeção, nunca como
verdade nova**. `PRODUCT ON CROP ≠ COMMERCIAL SOLUTION`.
Ressalva mantida: é `OWNER_INTENT`, não `OBSERVED_USAGE`. A medição de uso continua exigida.

**13 · Crop Windows como quê?**
**Papel `FOUNDATIONAL_LAYER` — o `SHARED AGRONOMIC CLOCK` — e estado `DEGRADED`, ao mesmo
tempo** (`RV-012`). O benchmark tem razão no papel: `§34` depende dela inteiro. A medição
tem razão no estado: `PROVED 0`, `SOURCE_IDS` vazio 29/29, gerador ausente de 979 commits.
**Elevar o papel de uma superfície não repara o seu dado.**

**14 · Label como quê?**
**`TRUTH_LAYER` + `CANONICAL_TOOL` + `DELIVERY_PROJECTION`, as três em simultâneo**
(`RV-011`, `ADJUDICACAO §4`). Foi a única divergência real entre benchmark e medição, e
resolveu-se por `PG-08`: **ser input de outra ferramenta não rebaixa ninguém.**
Prioridade: `WHAT CHANGED SINCE LAST LABEL` + objectos impactados — com a trava de §34.2:
o casco não calcula o impacto se ele exigir juízo.

**15 · Market Pulse como quê?**
`CONTEXT_VIEW` **com uma porta de promoção** (`RV-013`, `C-CARD-06`): um item só é *pulse*
se responder `SO WHAT` · `WHO CARES` · `WHICH DECISION MAY CHANGE`. Se a porta fechar para
a maioria dos 157, a superfície não é má — é contexto, que é o que a medição já dizia.

**16 · Field Voices como quê?**
Direção declarada: **`CURATED FIELD NEWSWIRE / SENSOR`** (`RV-014`). Continua `CANDIDATE`.
Os três bloqueadores medidos mantêm-se e **nenhum é de formato**: baseline, denominador
(79 de quantos?) e GDPR. `FIELD VOICE ≠ FIELD INCIDENCE`.

**17 · Science como quê?**
**`SCIENCE CALLS` que podem mudar decisão; os papers passam a camada de evidência
subjacente** (`C-CARD-05`). Convergem benchmark e medição. Bloqueadores: `CAP-017` não
cobre a Itália, **39/88 `OFF_CASE`**, GDPR `P-008`.

**18 · Future como quê?**
**Portfólio de hipóteses observadas, com horizonte, *triggers*, o que fortalece, o que
enfraquece e evidência contrária. NUNCA `PREDICTION THEATER`** (`C-CARD-04`).
Já é a lei do `RADAR-DO-FUTURO-CONTRACT-V1`. O que falta continua a montante:
**12 dos 13 campos obrigatórios do cartão não viajam**.

**19 · Competitor mudou muito?**
**Não.** `KEEP + IMPROVE` nas duas pesquisas. Reforçar taxonomia, *cross-links* e
evidência; separar `REGISTERED RESPONSE` · `ADVERTISEMENT` · `PUBLIC COMMUNICATION` ·
`TECHNICAL ACTIVITY` · `LAUNCH` · `EVENT` · `PRODUCT CHANGE`; **nenhum score universal**.
O que continua a violar o contrato é o **`577` no menu** — o número único que o contrato
proíbe pelo nome.

**20 · Como funcionam os briefs por papel?**
`ONE INTELLIGENCE PRODUCT → N DELIVERY PROJECTIONS` (§40). Nove papéis reconhecidos —
os sete de §16 mais **RTV** e **Supply**. Cada brief muda língua, título, ordem, ênfase,
detalhe, contexto, comprimento e **ação recomendada, dentro do que o Product Contract
autoriza** (`C-BRIEF-01`).

**21 · O que é imutável entre briefs?**
`FACTS · EVIDENCE · SOURCE/PROVENANCE · FACT_TIME · OBSERVED_TIME · SOURCE_LOCATION ·
FACT_LOCATION · LIMITATIONS · CONFIDENCE/EVIDENCE STATE · UNKNOWN · CONTRADICTION ·
LABEL TRUTH · PRODUCT_ID + VERSION + AS_OF`.
> **Uma projeção não pode transformar uma incerteza técnica numa certeza comercial.**
E para o RTV, duas travas próprias: a secção **`NÃO PROMETA`** é obrigatória e não-vazia;
e as perguntas sugeridas **nunca induzem a resposta que validaria a hipótese**.

**22 · Móvel é produto?**
**SIM.** `L-24` · `MOBILE IS DELIVERY, NOT A SMALLER DESKTOP`. O *share brief* móvel é uma
`DELIVERY_PROJECTION` de primeira classe: ID estável, versão, `AS_OF`, projeção por papel,
*deep-link* de evidência e ligação à verdade corrente.

**23 · O PDF continua importante?**
**SIM — e deixa de ser o canal único.** É um **derivado congelado**: *snapshot*, offline,
impressão, anexo de auditoria, apresentação. `PDF ≠ DATABASE DUMP`.
Medido: existe hoje **um único** `[data-download-pdf]` no portal, e vive numa vista
**legada** cuja ponte resolve **0 de 43**.

**24 · A Validation Queue virou ferramenta?**
**NÃO. `WORKFLOW_CANDIDATE`** (`WC-01`). Não passou o Gate — falha as perguntas 2 e 13.
A pergunta é boa e a matéria-prima está medida (`VALIDATION_REQUIRED 37 de 43`,
`TO_VALIDATE 9`, `WATCH 21`). **O que falta é o *workflow* real da ADAMA** (`U-20`).
Construir a fila antes de saber como eles já validam seria desenhar o processo em vez de
o servir.

**25 · Que novos Product Contracts serão precisos?**
**Dez** (`R0.2 §R2.3`): `HOME_QUEUE` · `CARD_CONTRACT` ×3 · `EVIDENCE_DRAWER` ·
`ROLE_BRIEF` ×9 · `SHARE_BRIEF` · `PDF_SNAPSHOT` · `ACTION` · `ALERT` · `TEMPORAL` ·
`LABEL_CHANGE_PROPAGATION`.
**Nenhum exige engenharia nova para ser escrito. Três não podem ser fechados sem a Bíblia
da Inteligência.**

**26 · Que arestas M:N precisam de autoridade da Bíblia da Inteligência?**
Sete: `E-03` (Crop Window → Opportunity) · `E-05` (Portfolio → Opportunity) ·
`E-06` (Science → Future) · `E-07` (Future → Opportunity) · `E-09` (Competitor → *) ·
`E-15` (Action → Intelligence) · e **todas**, para o objecto `CLAIM`.
**`E-03` é a lacuna estrutural:** é a única aresta que **pode promover** e **não tem porta
nomeada** — e é exatamente a que o modelo temporal exige.

**27 · Que princípios foram aceites?**
Dez `ACCEPT`: 2, 3, 5, 11, 13, 14, 16, 17, 19 — e o 15, que fica no Registo.
Cinco `MERGE` (1, 6, 8, 10, 12): **já eram lei aqui antes de o benchmark existir.**

**28 · Quais foram modificados?**
Quatro `REFINE`: **nº 4** (localização é sempre primeira classe, não só «quando muda a
ação»: `SOURCE_LOCATION ≠ FACT_LOCATION` sempre) · **nº 7** (a prova dobra-se, **a lacuna
não**) · **nº 9** (a proibição é sobre a **ordem**, não sobre imprimir o número) ·
**nº 18** (três níveis de valor, e o terceiro publica-se como `UNKNOWN`).

**29 · Quais foram recusados?**
Zero entre os 19 princípios e os 16 pulos. **Quatro entre as propostas concretas** —
`R-01`…`R-04`. A rejeição concentra-se onde o benchmark desce ao concreto e a medição
local sabe mais.

**30 · Que `UNKNOWN` continuam abertos?**
Os catorze de `§29` mais **dez novos** (`U-15`…`U-24`). Os três mais caros:
**`U-16`** (a correspondência entre os 5 estados da Linha A e os 4 propostos — não medida,
e fazê-la à mão seria inventar semântica) · **`U-17`** (`COMMERCIAL_LEAD_TIME` não tem
dono) · **`U-24`** (`DEPENDENCY_ON_INTELLIGENCE_BIBLE = OPEN` em dez campos de juízo).
E `U-12` continua: **as Bíblias da Coleta e da Inteligência não existem como ficheiros.**

**31 · Implementação?** `0`.
**32 · Produção?** `0`.
**33 · Merge?** `0`.

---

## §8 · EM PALAVRAS FÁCEIS — o que mudou no desenho mental de cada ferramenta

**Antes de tudo, uma coisa que o senhor deve saber, porque foi a maior surpresa da
medição.** Aquilo que o *benchmark* recomendou como a grande mudança — organizar as
oportunidades por **quando é preciso agir**, e não por uma nota — **já está calculado
dentro do motor**. Ele já separa os 43 casos em *agir agora* (2), *validar agora* (4),
*preparar* (7), *observar* (21) e *por validar* (9). E o motor até traz uma frase a
dizer que o portal **não pode recalcular** nada disso.

**Só que a barra do portal não conta isso. Conta outro número, de outra lei.**
Duas leis, o mesmo pacote, os mesmos 43 casos, ninguém as reconciliou. Essa é hoje a
decisão mais cara que está à sua espera — e não é técnica: é escolher qual das duas manda.

**E há uma segunda coisa, que é o travão honesto.** Para dizer «isto tem de ser feito nos
próximos nove dias» é preciso saber quando a janela abre e fecha. Medido: **em 41 dos 43
casos o sistema não sabe se a janela está aberta**, e 27 nem sequer têm janela. A
arquitetura está pronta; o relógio que a alimenta não está. Isso não é motivo para
desistir da ideia — é o trabalho seguinte, e tem nome: dar proveniência às janelas.

Agora, ferramenta a ferramenta:

**Opportunity Radar.** Deixa de ser uma lista de coisas interessantes e passa a ser uma
fila por tempo: *o que tem de ser feito agora, o que tem de ser preparado agora, o que
vem na próxima janela, o que só se observa*. Para o **gerente comercial**, é a diferença
entre uma lista e um plano de semana. E para o **RTV**, é a diferença entre saber que há
um problema e saber quando tem de estar na revenda.

**A janela comercial abre antes da janela agronómica.** É o salto mais útil para venda e
para *supply*: a aplicação pode ser daqui a seis semanas, mas a preparação começa hoje.
O sistema passa a ter **dois relógios diferentes** onde antes tinha um só.

**Portfolio.** Deixa de responder «que produtos temos?» e passa a responder «**o que a
ADAMA consegue fazer para este problema, nesta cultura, neste país, agora — dentro do que
o rótulo autoriza**». Para o RTV isso é ouro: é a resposta que ele pode defender à frente
do cliente sem prometer o que não pode.

**Label Intelligence.** Passa a ser a **trava de verdade**: nada pode ser afirmado sobre
um produto que o rótulo não sustente. E ganha a evolução que vale mais: **o que mudou
desde o último rótulo, e o que isso afeta**. Para Regulatory e para Technical, é a
diferença entre ler PDFs e ser avisado.

**Crop Windows.** Passa a ser o **relógio partilhado** do sistema inteiro — é ele que dá
o tempo às oportunidades. Mas fica escrito, sem enfeite, que hoje **nenhuma das 29
janelas tem fonte**. Elevar a importância dela não conserta o dado dela.

**Market Pulse.** Passa a ter uma porta: um item só entra se conseguir dizer **quem
precisa de olhar e que decisão pode mudar**. Se não conseguir, é contexto — e contexto é
útil, só não é manchete.

**Field Voices.** Passa a ser um **noticiário curado do campo**, com origem, data e
diversidade de fontes. E fica gravada a linha que nunca se atravessa: **o que o campo
fala não é o que está a acontecer**. Para Marketing e Market Development, é um sensor
precioso — desde que nunca vire estatística.

**Scientific Intelligence.** A conclusão sobe, os *papers* descem. Em vez de uma lista de
estudos, uma frase que diz **o que a ciência sustenta, quão madura é, e o que a ADAMA
poderia fazer com isso** — com a evidência contrária ao lado, sempre.

**Future Radar.** Continua a dizer o que estamos a observar e **o que teria de acontecer**
para passar a importar. Nunca prevê. E fica dito que hoje ele carrega 44 identificadores e
não 44 fichas: **doze dos treze campos que o cartão precisa não chegam a viajar**.

**Competitor Watch.** Muda pouco, e é bom sinal. O que muda é o `577` no menu — esse
número junta quatro coisas de naturezas diferentes e o próprio contrato proíbe-o.

**Archive e Source Register.** Continuam essenciais e deixam de disputar o mesmo espaço
mental que o Radar. Um é para investigar, o outro é para provar. Para **Leadership** isso
importa: a primeira tela deixa de ter contadores e passa a ter decisões.

**A Home.** Deixa de ser um sítio onde se escolhe uma ferramenta e passa a ser o sítio que
responde: *«estas merecem a sua atenção agora — nestas age, nestas prepara, estas só
observa.»* Com uma trava dura: **a Home não decide nada**. Ela mostra o que a inteligência
já decidiu.

**E os briefs.** A mesma verdade, contada de nove maneiras — RTV, gerente, marketing,
market development, técnico, *supply*, regulatório, direção e controlo. Muda a linguagem,
a ordem e a próxima ação. **Não muda um facto, uma limitação nem um «não sabemos».**
Um brief de vendas que apague a limitação técnica é a doença que este contrato existe
para impedir.

**Uma última, e é a que protege tudo o resto.** Nunca vamos dizer que o SINTONIA causou
uma venda. Inteligência, ação, execução comercial e venda são quatro etapas com donos
diferentes. Podemos, mais tarde e com base, medir a associação. **Inventar a causa seria
destruir a única coisa que faz este sistema valer: poder ser verificado.**
