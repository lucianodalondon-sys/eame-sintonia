# BENCHMARK PROFUNDO DE INTELLIGENCE PARA AGRONEGÓCIO — V1

```
MISSAO        C-INT-AGRO-BENCH-01
ESPECIE       RESEARCH + ENGINEERING AUDIT
MEDIDO_EM     2026-09-13
RAMO          claude/epic-archimedes-ryo0ms
BASE          claude/raw-observation-identity-3jbwco @ f888776d
```

> **ISTO NÃO É ARQUITETURA, NÃO É CONTRATO E NÃO GOVERNA NADA.**
> É evidência de auditoria e de benchmark, produzida num commit. As leis
> continuam na [`BIBLIA-CANONICA-DA-COLETA.md`](../../BIBLIA-CANONICA-DA-COLETA.md)
> e na Bíblia candidata de Engenharia da Intelligence. Esta missão **não
> implementa** Intelligence, **não altera** Collection, **não toca** no Portal.

Existe em paralelo uma pesquisa independente feita pelo ChatGPT. Este documento
**não** tentou adivinhá-la nem reproduzi-la. Ele é a segunda investigação.

---

## 0 · O GIT, MEDIDO ANTES DE QUALQUER DECISÃO

Nada aqui foi herdado do enunciado nem da conversa. Tudo foi lido da árvore.

| facto | valor medido |
|---|---|
| `REPO` | `github.com/lucianodalondon-sys/eame-sintonia` |
| `CURRENT_BRANCH` (à chegada) | `claude/epic-archimedes-ryo0ms` @ `f437ff11` (= `origin/main`) |
| `REMOTE_HEAD` de `main` | `f437ff11` · 2026-09-12 18:49 |
| `WORKTREE` (à chegada) | limpa |
| `FUNCTIONAL_REFERENCE` | **`origin/claude/raw-observation-identity-3jbwco` @ `f888776d`** · 2026-09-13 22:53 |
| `COLLECTION_BIBLE_HEAD` | `BIBLIA-CANONICA-DA-COLETA.md` @ `f888776d` · 2 889 linhas · V1.4 |
| `INTELLIGENCE_BIBLE_BRANCH/HEAD` | `origin/research/intelligence-bible-engineering-v1` @ `7ae1b510` · `BIBLIA-DE-ENGENHARIA-DA-INTELLIGENCE.md` · 1 335 linhas · V0.2 · `CANONICAL = NO` |
| `KNOW_HOW_BRANCH/HEAD` | `origin/claude/sintonia-eame-know-how-v1` @ `7b5e50cf` · `SINTONIA-EAME-KNOW-HOW.md` |
| `SYSTEM_MAP_REFERENCE` | cadeia canónica corrida nesta árvore: `MAPA=OK · pecas=182 · SYSTEM_MAP_CHECK=PASS` |

### ⚠️ A PRIMEIRA MEDIÇÃO É UM ACHADO, E NÃO ESTAVA NO ENUNCIADO

> ## `main` NÃO É A LINHA FUNCIONAL DESTA CASA.

`origin/main` e a linha da Collection **divergiram a 2026-09-07** (`56fdb8ca`,
«Merge pull request #1»). Desde então:

```
origin/main                              +9 commits   1 294 ficheiros
claude/raw-observation-identity-3jbwco  +453 commits  1 866 ficheiros
```

E os 9 commits de `main` são: 2 registos de workflow do GitHub, e 7 com as
mensagens `temp` · `placeholder` · `remove accidental temporary file` ·
`remove accidental draft file` · três `ops:` de um one-shot. **`main` não
carrega a `BIBLIA-CANONICA-DA-COLETA.md`. Não carrega o know-how canónico.**

Isto importa para esta missão por uma razão prática:

```
A BIBLIA DA INTELLIGENCE NASCEU EM main.        (research/intelligence-bible-engineering-v1)
O CENSO DA INTELLIGENCE NASCEU EM main.         (claude/funny-hypatia-y7ho5s)
O BENCHMARK DE PRODUTO NASCEU EM main.          (research/product-tools-benchmark-v1)
A COLLECTION QUE ELES DESCREVEM VIVE NA OUTRA LINHA.
```

O próprio `CENSO-ATUAL-DA-INTELLIGENCE.md` mediu isto e escolheu a mesma
referência funcional que esta missão mediu independentemente
(`raw-observation-identity-3jbwco`), e escreveu a frase que fecha o assunto:

> «UM NUMERO DE PECAS SEM A LINHA EM QUE FOI MEDIDO NAO E UM NUMERO.»

**Esta missão nasceu da referência funcional**, e não de `main`. Os documentos
da outra linha foram lidos por `git show`, sem merge e sem alteração.

### A branch desta missão

O enunciado pede `research/agro-intelligence-benchmark-v1`. A missão recebeu,
por instrução operacional vinculativa, a branch `claude/epic-archimedes-ryo0ms`.
Ela **não era** a linha funcional (estava em `main`, sem a Bíblia), e foi
recriada a partir de `f888776d` — que é exactamente o que o enunciado exige
(«a branch deve nascer da referência funcional»). Nenhuma branch funcional foi
alterada.

---

## 1 · O MÉTODO, E A LEI DE PROVA

O enunciado proíbe começar pela UI, pelos motores existentes e pela vontade de
copiar uma empresa. A ordem seguida foi a que ele manda:

```
O QUE SISTEMAS MADUROS PRECISAM DE SABER
  → COMO REPRESENTAM ISSO
    → QUE MATERIA-PRIMA PRECISAM DE RECEBER
      → COMO EVITAM CONCLUSOES FALSAS
        → COMO PROMOVEM EVIDENCIA A DECISAO
          → O QUE DISSO E TRANSFERIVEL
            → O QUE A COLLECTION ATUAL ENTREGA
              → O QUE FALTA
```

E a lei de prova do enunciado foi aplicada linha a linha:

```
VENDOR CLAIM        !=  PROVEN EFFECTIVENESS
PRODUCT CAPABILITY  !=  SCIENTIFIC EVIDENCE  !=  OUR INFERENCE
```

Cada afirmação neste benchmark carrega uma dessas três etiquetas. Uma página de
fornecedor prova **o que o produto declara fazer** — nunca que funciona melhor
do que tudo.

### O que ficou por provar, e diz-se

| fonte | estado |
|---|---|
| EFSA EN-9788 (guidelines 2025), texto integral | `NAO_LIDO` — Wiley devolveu HTTP 403; usado o **resumo oficial da própria EFSA**, que já carrega as definições dos três parâmetros |
| RiPEST / RiBESS+ (manual), texto integral | `NAO_LIDO` — PDF não extraível nesta máquina |
| JRC MARS, metodologia detalhada (grelha, WOFOST, NUTS) | `PARCIAL` — ScienceDirect 403; usada a página institucional do JRC |
| AMIS, páginas técnicas | `PARCIAL` — o sítio devolveu só o título; usado o material institucional indexado |
| CABI Compendium, ficha técnica | `NAO_LIDO` — HTTP 403 |
| Cropwise / xarvio / FieldView / JD Ops | `VENDOR_CLAIM` apenas, por construção — é o que estas fontes podem provar |

**NÃO SE INVENTOU O QUE NÃO SE LEU.** Onde a leitura falhou, está escrito.

---

## 2 · O QUE FOI PESQUISADO

### A · Agronomic / Digital farm DSS
Syngenta **Cropwise Protector** (+ app de scouting) · BASF **xarvio FIELD
MANAGER** · Bayer **Climate FieldView** · **CropX** · **OneSoil** · **John Deere
Operations Center**.

### B · Agronomic data / R&D intelligence
**Agmatix / Axiom / GUARDS** · **MIAPPE** v1.1 · **BrAPI** · **Crop Ontology**.

### C · Plant health / pest intelligence
**EFSA** Plant Health · EFSA **pest surveillance** (guidelines estatísticas) ·
EFSA **Horizon Scanning** + **PeMoScoring** · **EPPO Global Database** · **EPPO
Reporting Service** · **ISPM 8** (IPPC) · **CABI Compendium** ·
**Plantwise / PlantwisePlus / POMS**.

### D · Regulatory / label / crop protection
**EU Pesticides Database** · **Ministero della Salute — Banca dati dei prodotti
fitosanitari** · **EPPO PP 1/248 (3)** (classificação harmonizada de usos de
PPP) · **Homologa / Lexagri** como exemplo comercial de harmonização.

### E · Agricultural markets
**JRC MARS Bulletin** · **EU Market Observatories** · **FAO AMIS**.

### F · Agribusiness commercial intelligence
**DTN Farm Intelligence / Ag Hub / FarmMarket data**.

### G · Ontologia / interoperabilidade
**EPPO Codes** · **AGROVOC** · **Crop Ontology** · **BBCH** · **MIAPPE** ·
**BrAPI** · **AgGateway ADAPT** · **ISO 11783 / ISOXML** · GeoJSON · **NUTS**.

### H · Literatura e política independentes
Revisão sobre avaliação de sistemas de alerta de saúde vegetal (*Frontiers in
Plant Science*, 2026) · literatura sobre modelos e previsão de doenças de
plantas · literatura sobre grafos de conhecimento e interoperabilidade agrícola
(AgroPortal, ontologia EPPO em OWL) · **EU Code of Conduct on agricultural data
sharing by contractual agreement** (COPA-COGECA e co-signatários).

As URLs estão no
[`AGRO-INTELLIGENCE-BENCHMARK-MATRIX-V1.md`](AGRO-INTELLIGENCE-BENCHMARK-MATRIX-V1.md),
por sistema.

---

## 3 · AS CONVERGÊNCIAS FORTES DO AGRO

São sete. Cada uma aparece em famílias **independentes** — regulador,
instituição científica e produto comercial — e nenhuma é uma opinião desta casa.

### C1 · A UNIDADE DE OBSERVAÇÃO NÃO É UM NÚMERO: É `TRAIT × METHOD × SCALE`

> Crop Ontology: *«uma variável fenotípica é a combinação de um trait, um método
> e uma escala»*; *«um trait pode ser medido por variáveis diferentes, conforme
> o método ou a escala»*.
>
> MIAPPE 1.1: *«uma variável observada descreve como a medição foi feita»*,
> associada *«ao método e à unidade de medida»*.

E o mesmo desenho aparece num **produto comercial**, com outro vocabulário:
Cropwise Protector separa **o que** está a ser observado (fenómenos: pragas,
doenças, pressão de infestantes) de **como** está a ser observado
(características: contagem por planta, percentagem de infestação, níveis de
pressão).

```
UM VALOR SEM METODO E SEM ESCALA NAO E COMPARAVEL COM OUTRO VALOR.
E DOIS VALORES NAO COMPARAVEIS SOMADOS NAO SAO UM NUMERO MAIOR:
SAO UM NUMERO FALSO.
```

`CONFIDENCE = ALTA` · três famílias independentes (ontologia científica, padrão
de metadados, produto comercial).

### C2 · ZERO NÃO EXISTE SEM DENOMINADOR, MÉTODO E PREVALÊNCIA DE DESENHO

A vigilância fitossanitária séria **não** declara ausência por não ter achado.
A EFSA, no resumo oficial das suas guidelines de inquéritos estatisticamente
sólidos, define três parâmetros e nenhum é opcional:

> *«(i) os objectivos do inquérito definem-se como atingir um certo nível de
> confiança de detectar uma dada prevalência da praga (**design prevalence**)…;
> (ii) a **população-alvo** é descrita pela sua estrutura e dimensão, incluindo
> os factores de risco; e (iii) a **sensibilidade do método** define-se como a
> combinação da eficácia da amostragem e da sensibilidade de diagnóstico para
> cada unidade de inspecção.»*

E a ISPM 8 (IPPC), revista em 2021, dá o vocabulário da **ausência**, que não é
uma palavra só:

```
ABSENT   pest not recorded · pest free area · pest records invalid
         pest no longer present · pest eradicated
PRESENT  (com qualificadores) not widely distributed · at low prevalence
         under official control · transient (not expected to establish)
```

```
«NAO ENCONTREI» E UMA MEDICAO DO OLHAR.
«NAO EXISTE» E UMA MEDICAO DO MUNDO.
SAO PERGUNTAS DIFERENTES, E SO A SEGUNDA PRECISA DE DENOMINADOR.
```

`CONFIDENCE = MUITO ALTA` · regulador europeu + padrão internacional (IPPC).

### C3 · O CÓDIGO É ESTÁVEL; O NOME MUDA — E O CÓDIGO SOZINHO NÃO CHEGA

EPPO: *«quando, por razões taxonómicas, um nome científico muda, o código EPPO
permanece o mesmo»*. Mais de 98 500 espécies, e **625 entidades não-taxonómicas**
(grupos de culturas, tratamentos). Códigos sob licença de dados aberta.

Isto é a resposta certa ao problema da identidade — **e tem um limite medido
nesta casa**, na secção 5.

`CONFIDENCE = MUITO ALTA` para a estabilidade. `CONFIDENCE = MUITO ALTA` para o
limite (medição interna executável).

### C4 · BASE DE DADOS NORMALIZADA ≠ AUTORIDADE LEGAL

A **EU Pesticides Database**, a base regulatória mais citada da Europa, diz de
si própria:

> *«This database is made available solely for the purpose of information.
> **It has no legal value.**»*
> *«The official information … are published in the Official Journal of the
> European Union.»*
> *«any questions related to specific authorisations should be addressed
> directly to the relevant Member State competent authority.»*

O regulador europeu escreve, na primeira pessoa, a lei que o SINTONIA precisa:

```
O FACTO REGULATORIO E O ATO OFICIAL.
A BASE DE DADOS E UMA COPIA COMODA DELE.
GUARDAR A COPIA E PERDER O ATO E FICAR SEM O FACTO.
```

Em Itália, o ato é o **decreto de autorização** e a **etichetta autorizzata**,
na Banca dati do Ministero della Salute — que dá número de registo, data do
decreto, substância activa, estado administrativo (autorizado · revogado ·
caducado · suspenso) e a última etiqueta autorizada.

`CONFIDENCE = MUITO ALTA` · declaração explícita da própria fonte.

### C5 · SINAL NÃO É ACHADO, E A ATRIÇÃO É ENORME E MEDIDA

A EFSA faz horizon scanning de saúde vegetal desde 2017 com JRC e ANSES. A
cadeia real, medida na literatura revista por pares:

```
MONITORIZAR   MedISys / EIOS — 3 221 fontes cientificas e de media, diariamente
SELECIONAR    revisao MANUAL por peritos, por relevancia para gestores de risco
RASTREAR      PeMoScoring — 15 criterios em 5 categorias (hospedeiro, entrada,
              estabelecimento, dispersao, impacto) -> phi liquido de -1 a +1
COMUNICAR     newsletter mensal no EFSA Journal
DEPOIS        pest categorisation -> avaliacao de risco -> PAFF -> gestor decide
```

E o número que fecha a discussão:

> **392 pragas novas foram identificadas entre 2017 e 2024. Apenas 27 foram
> mencionadas outra vez em artigos subsequentes.**

```
~7% DOS SINAIS SOBREVIVERAM A PROPRIA REPETICAO.
UM SISTEMA QUE PROMOVESSE SINAL A ACHADO PRODUZIRIA
93% DE INTELLIGENCE FALSA — COM APARENCIA IMPECAVEL.
```

E a própria EFSA declara o que o rastreio **não** decide: ele desencadeia
avaliação, não decisão regulatória.

`CONFIDENCE = MUITO ALTA` · regulador + literatura revista por pares.

### C6 · OBSERVADO, FAVORÁVEL, MODELADO E CONFIRMADO SÃO QUATRO COISAS

Nenhum sistema maduro as mistura, e os produtos comerciais dizem-no com as suas
próprias palavras. O xarvio FIELD MANAGER declara usar *«um índice para
identificar e prever o risco de eventos de infecção na época»* e mostrar
*«a favorabilidade meteorológica para o desenvolvimento da doença»* — e aceita
que o utilizador *«inclua as suas observações para melhorar os modelos»*. Ou
seja: **a observação humana entra como input do modelo, não como output dele.**

```
DOENCA OBSERVADA         alguem viu, com metodo e denominador
CONDICOES FAVORAVEIS     o tempo permitiria
RISCO MODELADO           um modelo calculou uma probabilidade
INCIDENCIA CONFIRMADA    diagnostico, com metodo declarado
```

`CONFIDENCE = ALTA` · declaração de produto + literatura.

### C7 · ACERTAR NA DETECÇÃO NÃO É ACERTAR NO AVISO

A revisão de 2026 em *Frontiers in Plant Science* é explícita:

> *«A avaliação centrada em exactidão comprime erros operacionais distintos:
> uma infecção precoce falhada, um alerta falso, um alerta tardio e um valor de
> confiança mal calibrado têm consequências agronómicas diferentes.»*

E propõe os indicadores que interessam a quem decide: **lead time · calibração ·
carga de alertas falsos · taxa de avisos falhados · conclusão da resposta ·
supressão da doença · valor económico · aprendizagem após a acção no campo**.
Separa explicitamente **output do modelo** de **gatilho da acção**, e defende
supervisão **em escalões**: sinal de baixo risco automático, risco médio
desencadeia recolha adicional, alta consequência escala para perito.

`CONFIDENCE = ALTA` · literatura revista por pares.

---

## 4 · O QUE DERRUBOU HIPÓTESES NOSSAS

### D1 · A hipótese da sequência SINTONIA sobreviveu — mas incompleta

Hipótese em teste:

```
OBSERVED SIGNAL -> CORROBORATED -> HYPOTHESIS -> VALIDATED IMPLICATION -> ACTIONABLE OPPORTUNITY
```

O benchmark **não a derrubou**: a cadeia EFSA/CABI tem a mesma forma. Mas ela
**não tem três coisas que os sistemas maduros têm**, e sem elas a sequência é
uma narrativa, não uma máquina:

| falta | quem a tem | o que é |
|---|---|---|
| `IDENTITY CHECK` **antes** do rastreio | EFSA/EPPO | confirmar de que organismo se fala antes de pontuar risco |
| `SCREENING` **explícito e barato** | PeMoScoring | 15 critérios, resposta em 1 dia, feito para **descartar** |
| `REVERSÃO` | ISPM 8 | *«pest records invalid»* · *«pest no longer present»* — o estado **anda para trás** |

A terceira é a mais dura, porque a sequência escrita só sabe subir.

```
UMA MAQUINA DE PROMOCAO QUE NAO SABE DESPROMOVER
NAO E UMA MAQUINA: E UMA CATRACA.
```

### D2 · «Documento» não é a unidade de conhecimento agrícola — e nós já sabíamos

A `COL-LAW-201` já diz `COLLECTION ARTIFACT ≠ CLAIM ≠ FACT`, e a `COL-LAW-202`
já desenha `ARTIFACT ──evidence_for──► CLAIM`. O benchmark confirma-o de fora,
e **acrescenta que no agro as espécies são mais do que duas**:

```
DOCUMENT              o PDF, o post, a pagina             evidencia
SOURCE CLAIM          o que a fonte AFIRMA                evidencia interpretada
FIELD OBSERVATION     alguem olhou, com metodo            MIAPPE / Cropwise / Plantwise
MEASUREMENT           trait x method x scale              Crop Ontology
PEST RECORD           a unidade da ISPM 8                 IPPC
REGULATORY FACT       o ato oficial + a etiqueta          Gazzetta / Ministero
PPP USE               crop x object x target x dest x loc x treatment   EPPO PP1/248
SCIENTIFIC RESULT     o resultado, nao o paper            MIAPPE
MODEL OUTPUT          a saida de um modelo                xarvio / MARS
SIGNAL                o que o radar apanhou               EFSA HS
HYPOTHESIS / FINDING  o julgamento                        analista
```

**A `PPP USE` é a descoberta que mais muda o desenho.** A EPPO PP 1/248 (3) diz
que *«um uso de produto fitofarmacêutico deve ser descrito por uma combinação de
elementos e dos seus códigos EPPO associados»* — cultura/grupo, objecto tratado,
alvo, destino da cultura, local de uso, tratamento. Não é um par
`(produto, cultura)`. É uma **tupla de seis**, e cada membro tem código.

```
UM ROTULO NAO AUTORIZA UM PRODUTO NUMA CULTURA.
AUTORIZA UM *USO* — E O USO TEM SEIS EIXOS.
```

### D3 · «Ontologia» no agro não é uma, e escolher uma só seria um erro

O enunciado já avisava («não escolher um único vocabulário universal por
conveniência»), e o benchmark prova porquê: os vocabulários **não cobrem as
mesmas perguntas**.

| pergunta | quem responde | quem **não** responde |
|---|---|---|
| que organismo é este? | EPPO code | AGROVOC (é tesauro, não registo taxonómico) |
| que medição é esta? | Crop Ontology (trait×method×scale) | EPPO |
| em que fase está a cultura? | BBCH | EPPO · AGROVOC |
| que estudo é este e é comparável? | MIAPPE · BrAPI | EPPO · BBCH |
| que uso de PPP é este? | EPPO PP1/248 | Crop Ontology · AGROVOC |
| como se chama isto em italiano? | AGROVOC (45 línguas, SKOS) · EPPO (nomes comuns) | Crop Ontology |
| onde, administrativamente? | NUTS | todos os outros |
| que operação de campo foi feita? | ADAPT / ISO 11783 | todos os outros |

A literatura de 2024-2025 diz o mesmo: *«muitos vocabulários e ontologias
representam dados agronómicos, mas estão espalhados em formatos diferentes,
tamanhos diferentes, estruturas diferentes, de domínios sobrepostos»* — e é por
isso que existe o AgroPortal, que é um **hub de alinhamento**, não um
vocabulário substituto.

### D4 · A passagem de oportunidade agronómica a oportunidade comercial **não** é pública

Foi a resposta mais limpa de todo o benchmark, e vem do único sistema que
declara fazê-lo. A DTN Farm Intelligence descreve os inputs de que precisa para
dizer «venda aqui»:

```
ligacao CAMPO -> OPERADOR DA TERRA
cultura, area (acreage), produtividades, INPUTS USADOS
integracao com CRM e ERP
perfis de 95%+ dos agricultores dos EUA (dado proprietario)
segmentacao por potencial de compra, wallet share, territorio, churn
```

Nada disto é público. Nada disto é derivável de registo regulatório, boletim
fitossanitário, paper ou preço de mercado.

```
DADO PUBLICO EXTERNO PROVA AGRONOMIA E REGULACAO.
NAO PROVA CARTEIRA, NAO PROVA CLIENTE, NAO PROVA VENDA.
```

E a Homologa/Lexagri prova o contrário pela positiva: mesmo a **harmonização
regulatória** à escala global (33 milhões de entradas, 350 000 produtos, 90+
países, com dados de GAP — culturas, pragas, doses, métodos, momento de
aplicação) é feita *«a partir de fontes públicas **e privadas**»* e com *«uma
rede de parceiros locais»*. Harmonizar rótulo à escala não é raspar sítios: é
uma operação com pessoas.

### D5 · O mesmo facto agrícola muda de decisão por causa de uma palavra — medido aqui

Não é uma hipótese externa. É o resultado do **ATAQUE E** desta missão, corrido
contra o código real (`provas/auditoria_agro_fronteira.py`):

```
"Sintomo di peronospora al 12,5% delle foglie..."     -> porta: SIM
"Peronospora osservata al 12,5% delle foglie..."      -> porta: NAO_SEI
MESMO FATO · MESMO EPPO (PLASVI) · MESMA CULTURA · MESMO VALOR
```

O léxico de universo é uma lista plana de palavras em PT/IT. O próprio código
escreve, em comentário, o diagnóstico correcto:

> *«a arquitetura certa e CONCEITO -> TERMO LOCAL (um `WHEAT_SEPTORIA` com as
> suas formas em IT/ES/FR/EN), e ela NAO existe aqui.»*

`PERONOSPORA` — a doença mais importante da vinha europeia — não está no léxico
do universo T3. **Está no dicionário agro canónico desta casa, com código EPPO
`PLASVI` verificado contra a EPPO Global Database.** As duas peças existem e não
se falam.

---

## 5 · ONTOLOGIA E IDENTIDADE — E O LIMITE, MEDIDO NESTA CASA

O detalhe está em
[`AGRO-IDENTITY-AND-ONTOLOGY-MAP-V1.md`](AGRO-IDENTITY-AND-ONTOLOGY-MAP-V1.md).
Aqui fica o que derruba o mito.

**Ataque testado:** *«EPPO sozinho resolve toda a identidade agrícola.»*

**Prova interna, executável, já existente nesta árvore.** O
`motor/normalize_agro.py` constrói uma ponte `nome comum francês → código EPPO`
com um desenho defensável — *o dicionário espanhol **propõe**, a EPPO Global
Database **verifica*** — e o resultado está gravado em
`data/samples/X-007-canonical-agro-dictionary.json`, sobre o corpo real dos usos
autorizados franceses (E-Phy, `FR-T4-001`):

| | pares `(cultura, alvo)` | usos autorizados |
|---|---|---|
| corpo total | **1 181** | **14 931** |
| `CONTEXTUAL` (resolvido pelo contexto da cultura) | 76 | 2 078 |
| `GROUP_SCOPED` (grupo delimitado pela cultura → **vários** códigos) | 29 | 1 431 |
| `GROUP` (o termo francês designa um **grupo**, não uma espécie) | 683 | 6 927 |
| `AMBIGUOUS` | 131 | 2 111 |
| `UNRESOLVED` | 262 | 2 384 |
| **resolvido** | **105 (8,9 %)** | **3 509 (23,5 %)** |
| resolvido, excluindo termos de grupo franceses | 21,1 % | 43,8 % |

```
O CODIGO EPPO RESOLVE 23,5% DOS USOS AUTORIZADOS FRANCESES.
E MESMO DEPOIS DE TIRAR OS TERMOS QUE SAO GRUPO POR CONSTRUCAO,
MAIS DE METADE CONTINUA POR RESOLVER.
```

E a razão não é um defeito do EPPO. É que **o rótulo fala a língua do agricultor
e o registo fala a língua do regulador**, e nenhuma delas é a língua da
taxonomia:

- `Vigne × Mildiou(s)` → `VITVI × PLASVI` — resolve, e a prova é o nome francês
  da própria EPPO: *«mildiou de la vigne»*.
- `Blé × Rouille(s)` → `TRZAX × [PUCCRT, PUCCST]` — **dois** códigos. «Rouille»
  não é uma espécie; é duas.
- `Cerisier × Moniliose(s) et pourriture grise` → **dois** patógenos num único
  termo de rótulo.
- 40 dos 105 registos resolvidos têm `EPPO_CROP` e `CANONICAL_CROP = null` —
  o código existe ao nível de **género/agregado**, não de espécie.

**Corolário arquitetural, e é uma lei candidata:**

```
A RELACAO TERMO-DE-ROTULO -> ENTIDADE E 1:N, E NAO 1:1.
UM SISTEMA QUE FORCE 1:1 OU MENTE, OU DEITA FORA 76,5% DOS USOS.
```

E por isso o `MATCH_TYPE` (`CONTEXTUAL` · `GROUP_SCOPED` · `AMBIGUOUS` ·
`GROUP` · `UNRESOLVED`) **é informação de primeira classe**: é o registo de
*como* a identidade foi decidida. Deitá-lo fora torna o erro de normalização
permanente e invisível — que é exactamente o que a `COL-LAW-203` já proíbe.

---

## 6 · TEMPO, GEOGRAFIA E FENOLOGIA

Detalhe na matriz. O que o benchmark obriga a escrever:

### Uma data de calendário **não** é suficiente

```
CALENDAR DATE        !=  OBSERVED PHENOLOGY
MODELLED PHENOLOGY   !=  OBSERVED PHENOLOGY
PUBLICATION_TIME     !=  FACT_TIME
```

O BBCH existe precisamente porque «15 de Maio» não diz se a vinha está em
floração. É um código decimal de dois dígitos (00–99), dez estágios principais
(0–9), aplicável a mono e dicotiledóneas — a escala que permite comparar
«mesmo estádio» entre anos, variedades e latitudes. O xarvio declara usar
**estádio de crescimento** como input do modelo e como eixo do alerta; o
Cropwise Protector regista **estádio fenológico** como campo de scouting.

E há um tempo que só o agro tem, e que nenhum dos nossos quatro tempos cobre:

```
JANELA AGRONOMICA          quando a aplicacao ainda faz efeito
JANELA DE PREPARACAO       quando a decisao comercial ainda e possivel
PRAZO REGULATORIO          quando a autorizacao caduca / o periodo de escoamento fecha
HORIZONTE DE PREVISAO      ate quando o modelo vale
```

A Bíblia candidata da Intelligence já tem `INT-LAW-104 — ACT_NOW exige janela
compatível`. O benchmark diz de onde vem a janela: **da fenologia e do rótulo, não
do calendário.**

### A geografia tem duas escadas, não uma

A `COL-LAW-032` já tem a escada administrativa
(`PAIS → REGIAO → PROVINCIA → MUNICIPIO → LOCALIDADE → COORDENADA`) e já proíbe
`SOURCE_LOCATION → FACT_LOCATION`. O benchmark acrescenta a segunda escada, que
é a da **evidência**, e ela não é comparável com a primeira:

```
ADMINISTRATIVA   NUTS0 / NUTS1 / NUTS2 / NUTS3 / comune
EPIDEMIOLOGICA   populacao-alvo -> unidade epidemiologica -> unidade de inspecao
MODELO           celula de grelha (MARS: grelha meteorologica agregada a NUTS)
OPERACIONAL      talhao / field boundary (ADAPT, FieldView, JD Ops)
```

E a regra que o JRC MARS obriga a escrever: o seu produto é uma previsão
**regional** construída sobre grelha meteorológica e modelo de crescimento, com
juízo de analista por cima. Não é um facto de talhão.

```
MODELO REGIONAL NAO DESCE A TALHAO.
E OBSERVACAO DE TALHAO NAO SOBE A REGIAO SEM DENOMINADOR.
```

---

## 7 · O QUE **NÃO** DEVE SER TRANSFERIDO PARA O SINTONIA

O benchmark encontrou coisas boas que seriam erradas aqui. Ficam escritas para
que ninguém as traga por entusiasmo:

| não trazer | porquê |
|---|---|
| **Score único de risco** (estilo PeMo phi) como número de decisão | o phi da EFSA é um **rastreio para descartar**, com 15 critérios visíveis por trás. Um score sem decomposição viola `INT-LAW-093` |
| **Modelos de doença de talhão** (xarvio/Cropwise) | exigem limite de campo, variedade, data de sementeira, meteorologia local, histórico. O SINTONIA não os tem e não os deve fingir |
| **Ontologia própria do SINTONIA** | há AgroPortal, EPPO, AGROVOC, Crop Ontology. Criar a 12.ª é criar a 12.ª |
| **Grafo como tecnologia** | `GRAPH MODEL ≠ GRAPH DATABASE`. Esta missão não escolhe banco |
| **Dado de exploração agrícola sem contrato** | o EU Code of Conduct põe o originador do dado no centro e reconhece-lhe o direito a beneficiar do seu uso. Ligar dado de agricultor sem contrato é um problema jurídico, não técnico |
| **A plataforma** (Agmatix, Homologa, DTN) | a casa já tem a lei: *«ROUBAMOS AS LEIS. NÃO TROUXEMOS AS PLATAFORMAS.»* |

---

## 8 · O QUE ISTO OBRIGA A DECIDIR — E NÃO DECIDE AQUI

Os documentos irmãos desta missão:

| documento | responde |
|---|---|
| [`AGRO-INTELLIGENCE-BENCHMARK-MATRIX-V1.md`](AGRO-INTELLIGENCE-BENCHMARK-MATRIX-V1.md) | os 20 eixos do §7, sistema a sistema |
| [`AGRO-IDENTITY-AND-ONTOLOGY-MAP-V1.md`](AGRO-IDENTITY-AND-ONTOLOGY-MAP-V1.md) | como identificar cada conceito agrícola |
| [`AGRO-INTELLIGENCE-INPUT-REQUIREMENTS-V1.md`](AGRO-INTELLIGENCE-INPUT-REQUIREMENTS-V1.md) | o contrato de matéria-prima, por capacidade |
| [`DISEASE-INTELLIGENCE-LEVELS-V1.md`](DISEASE-INTELLIGENCE-LEVELS-V1.md) | a régua de doença, e até onde chegamos |
| [`COLLECTION-READINESS-FOR-AGRO-INTELLIGENCE-V1.md`](COLLECTION-READINESS-FOR-AGRO-INTELLIGENCE-V1.md) | o que a Collection actual entrega |
| [`AGRO-INTELLIGENCE-PROMOTION-MODEL-V1.md`](AGRO-INTELLIGENCE-PROMOTION-MODEL-V1.md) | as transições, os portões e o que reverte |
| [`AGRO-CROSSING-GRAPH-V1.md`](AGRO-CROSSING-GRAPH-V1.md) | que relações são necessárias, e porquê |
| [`AGRO-INTELLIGENCE-TOOL-ROLES-V1.md`](AGRO-INTELLIGENCE-TOOL-ROLES-V1.md) | o papel arquitetural das 12 ferramentas |
| [`RED-TEAM-AGRO-INTELLIGENCE-BENCHMARK-V1.md`](RED-TEAM-AGRO-INTELLIGENCE-BENCHMARK-V1.md) | os 20 ataques, e quais sobreviveram |
| [`../../docs/operacao/COLLECTION-P0-CHANGE-REQUEST.md`](../../docs/operacao/COLLECTION-P0-CHANGE-REQUEST.md) | o gap P0, para o dono da Collection |

---

## 9 · VEREDITOS

```
AGRO_INTELLIGENCE_ARCHITECTURE_READY     = NO
COLLECTION_READY_FOR_AGRO_INTELLIGENCE   = PARTIAL
P0_COLLECTION_CHANGE_REQUIRED            = YES
ONTOLOGY_DIRECTION_READY                 = YES
PROMOTION_MODEL_READY                    = NO
OPPORTUNITY_CONTRACT_READY               = NO

DISEASE_INTELLIGENCE_MAX_DEFENSIBLE_LEVEL =
  NIVEL 2 — «CONDICOES FAVORAVEIS E SINAL RELATADO, COM LUGAR E TEMPO DA FONTE».
  Nao ha denominador, nao ha metodo de diagnostico, nao ha populacao-alvo, e
  nao ha modelo proprio. NIVEL 3 (risco modelado) e NIVEL 4 (incidencia
  confirmada) exigem materia-prima que nenhuma fonte publica actual entrega
  a esta casa.

PUBLIC_DATA_COMMERCIAL_LIMIT =
  DADO PUBLICO EXTERNO PROVA, NO MAXIMO, *OPORTUNIDADE AGRONOMICA* E
  *OPORTUNIDADE DE PORTFOLIO REGISTADO*. NAO PROVA PORTFOLIO COMERCIAL,
  NAO PROVA OPORTUNIDADE DE VENDA, NAO PROVA PREVISAO DE PROCURA.
  A fronteira e a identidade do agricultor e a ligacao CAMPO->OPERADOR, e ela
  e privada por construcao.
```

O porquê de cada `NO` está em
[§40 do `COLLECTION-READINESS-FOR-AGRO-INTELLIGENCE-V1.md`](COLLECTION-READINESS-FOR-AGRO-INTELLIGENCE-V1.md).

---

## 10 · DESCONHECIDOS DECLARADOS

```
NAO_SEI  o texto integral das guidelines EFSA EN-9788 (403)
NAO_SEI  a metodologia detalhada do JRC MARS (grelha, WOFOST, agregacao NUTS)
NAO_SEI  a ficha tecnica do CABI Compendium (403)
NAO_SEI  se a EPPO GD publica versao datada consultavel por API sem token
NAO_SEI  a cobertura real de BBCH nas fontes italianas ja coletadas
NAO_SEI  que contratos de dado a ADAMA ja tem, e com quem
NAO_SEI  se existe uma fonte publica EAME que declare denominador de vigilancia
```

Nenhum destes foi preenchido por inferência.
