# TOPOLOGIA DA COLETA — o pente-fino, cartão a cartão e aresta a aresta

```
MISSAO      C-TOPOLOGY-1
BRANCH      claude/collection-topology-census-v1
BASE        collection b4310443  ·  system-map ffa9fb9b (lente read-only)
DATA        2026-09-09
VEREDITO    C-TOPOLOGY-1 = PASS
```

> **Todo número aqui é reproduzível.** O comando está ao lado. Um número sem
> comando não entrou.
>
> ```bash
> python3 system-map/scripts/censo_da_topologia.py
> python3 system-map/scripts/validate_system_map.py
> ```

---

## 1 · O QUE O UTILIZADOR VIA, E O QUE ERA

O Luciano abriu o mapa e viu sete coisas. Nenhuma era o que parecia.

| o que se via | o que era |
|---|---|
| cards sem ligação | **26 órfãos falsos por vista** — os vizinhos viviam noutra lente. No grafo inteiro, zero órfãos. |
| mais de um SINTONIA SCRAP | **quatro papéis distintos** com nomes que só divergiam no FIM do rótulo — e um quinto que estava no disco e não no mapa |
| cards fora da ordem do fluxo | a ordem era **alfabética por id**, e as zonas pela ordem de declaração. A ADMISSÃO aparecia **antes** do dono do RAW |
| cards atravessando etapas | a **Z-GUARDA** — onde vivem os donos do RAW e do DERIVED — estava na família «A ESPERA» |
| ligados directamente à Intelligence | 150 arestas, e **zero levam dado**. 78 são provas que MEDEM a coleta |
| edges difíceis de explicar | as **seis únicas** arestas `UNKNOWN` do mapa eram a esteira inteira |
| peças de função pouco clara | 24 sem chamador de runtime, das quais **9 são CLI documentado** e **3 ninguém corre** |

---

## 2 · OS NÚMEROS

```
CARTOES_AUDITADOS            104 de 104        (100%)
ARESTAS_AUDITADAS            532 de 532        (100%)

F-COLETA                      49  ->  64
F-ESPERA                      13  ->   1       (a Z-GUARDA saiu; o READY entrou)

SEM_LIGACAO verdadeiros                2       dois armazéns, terminais legítimos
ORFAOS_FALSOS_POR_VISTA               26
SEM_LIGACAO_INEXPLICADOS               0

DUPLICATE_LABELS                       0
COLISOES_DE_PREFIXO                    7       a maior: «A prova de...» ×7, toda em Z-PROVA

DIRECT_INTELLIGENCE_EDGES            150
  PROOF 78 · READ 38 · CODE 14 · RULE 12 · CONTROL 8
  DATA                                 0       nenhum dado salta a porta
UNEXPLAINED_DIRECT_EDGES               0

ENTRYPOINTS                           52
ALCANCADOS_POR_UMA_CORRIDA            60
SEM_CHAMADOR_DE_RUNTIME               24  (9 CLI documentado)
NINGUEM_CORRE                          3

NEW_FAILURES                           0
PRODUCTION_MUTATION                    0
```

---

## 3 · A ESTEIRA, DA ESQUERDA PARA A DIREITA

Derivada das `ETAPAS` canónicas — `medidas/rastro_da_coleta.ETAPAS` e
`leis/telemetria.ETAPAS_DA_COLETA` concordam palavra por palavra.

```
BIBLIA → ENTRADA → PEDIDO → ORQUESTRADOR → CANDIDATAS → FONTES
       → EXECUCAO → VEICULOS → FERRAMENTAS → ACOES
       → GUARDA (RAW · DERIVED) → ADMISSAO → ESPERA (READY)
       ────────────────────────────────────────────────────────
       apoio:  REGRAS · REGUAS · MEDIDAS · PROVA
```

| etapa | dono | ficheiro |
|---|---|---|
| REQUEST | `C-PEDIDO` | `pedido/pedido.py` |
| ROUTE | `C-ORQUESTRADOR` | `orquestrador/orquestrador.py` |
| ACQUISITION | `C-SCRAP-SOCIAL` e irmãos | `coleta/social_*.py` |
| RAW | `C-DONO-DA-ESCRITA` | `guarda/preservar_coleta.py` |
| DERIVED | `C-DONO-DO-DERIVADO` | `guarda/preservar_derivado.py` |
| STRUCTURED | **5 escritores, nenhum dono único** | gap `STRUCTURED_SEM_DONO_LIGADO` |
| ADMISSION | `C-ADMISSAO` | `admissao/admissao.py` |
| READY | `C-READY` | `admissao.pronto_para_inteligencia()` |
| INTELLIGENCE | **nenhum consumidor** | gap `READY_SEM_CONSUMIDOR` |

---

## 4 · SINTONIA SCRAP — o dossiê

Cinco peças, cinco papéis. Nenhuma é duplicata.

| cartão | papel | ficheiros |
|---|---|---|
| `C-SINTONIA-SCRAP` | despacho de **aquisição** (24 fases) | `.github/workflows/sintonia-scrap.yml` |
| `C-SCRAP-ROTA` | despacho de **rota e sessão** (`auth_mode`) | `.github/workflows/scrap-social.yml` |
| `C-SCRAP-SOCIAL` | **executor** | `coleta/social_*.py`, `youtube_oficial.py` |
| `C-SCRAP-GUARDA` | **guarda** de credencial e sessão | `guarda/social_guarda.py`, `social_sessao.py` |
| `C-SCRAP-LEIS` | **regras** — a taxonomia da falha | `leis/falhas.py`, `fundacao_da_coleta.py`, `social_matriz.py` |

`C-SCRAP-ROTA` **não existia no mapa**: o validador só exige dono para
ficheiros de código, e um `.yml` passava. Eram dois botões no repositório e um
no mapa.

### Onde o SCRAP entra na coleta — e onde ele não entra

```
SCRAP → conteudo · conteudo_visto_em · comentario     (escreve)
SCRAP → raw_asset                                      NÃO ESCREVE
```

Medido: `coleta/social_persistencia.py` escreve as três tabelas de conteúdo e
**não** escreve `raw_asset`. Os únicos escritores de `raw_asset` são
`guarda/preservar_coleta.py`, `guarda/catalogo_importar.py` e
`guarda/memoria_descartavel.py`, e o SCRAP não chama nenhum.

O próprio código já dizia, em `coleta/social_scrap.py:668`: *«PILOT_PROOF, não
OPERATIONAL_STORAGE. O dono forward do G-42 (Storage + raw_asset) NÃO recebeu
estes bytes.»*

O que faltava era um **nome que uma máquina lesse**: `SCRAP_RAW_NAO_RECEBIDO`,
agora em `coleta/social_envelope.py`, guardado por três casos em
`tests/test_politica_da_coleta.py`.

> **A rota social não atravessa RAW.** Ligá-la é decisão de arquitetura — muda
> o que se preserva, quanto custa e o que passa a ser reproduzível. Esta missão
> nomeia; não decide.

---

## 5 · A FRONTEIRA COM A INTELLIGENCE

**150 arestas atravessam. Zero levam dado.**

```
PROOF     78     provas que MEDEM a coleta
READ      38
CODE      14     imports
RULE      12     leis consultadas
CONTROL    8
DATA       0
```

136 das 150 vão para **Z-PROVA**. O que parecia «a coleta a falar com a
inteligência» é, quase todo, **a coleta a ser medida** — porque o território
das provas está na família da inteligência.

As três que o mapa mostrava como DATA eram falsas, e todas pela mesma causa:
a regra que promove a ligação de uma ferramenta de PREPARO a DATA disparava
sem olhar para o outro topo, e apanhava um censo que LÊ o `.py` da ferramenta
e uma lei que ela CONSULTA.

> **UMA PROVA QUE ME MEDE NÃO ESTÁ NO MEU CAMINHO.**
> **UMA REGRA QUE EU CONSULTO NÃO VIAJA COMIGO.**

Guardado por `T5b_nenhum_dado_salta_a_porta_para_a_inteligencia`, com uma
lista `TRAVESSIAS_AUTORIZADAS` vazia. Ele não exige zero para sempre: exige
que, se um dado passar a atravessar, alguém venha declarar a lei que o
autoriza. Mutação de red team (`RAW → Inteligência` sem contrato): reprova.

---

## 6 · O QUE CONTINUA ABERTO

| gap | estado | de quem é |
|---|---|---|
| `READY_SEM_CONSUMIDOR` | aberto, visível no cartão `C-READY` | arquitetura / Intelligence |
| `SCRAP_RAW_NAO_RECEBIDO` | aberto, nomeado | decisão de arquitetura |
| `STRUCTURED_SEM_DONO_LIGADO` | aberto | herdado do C-FINAL |
| `RAW_FORWARD_NAO_EMITE` | aberto | herdado |
| `ADMISSION_SEM_DONO_LIGADO` | aberto | herdado |
| `CHANNEL_IDENTITY_NOT_RESOLVED` | aberto | **decisão humana**: `IT-OWN-003` ou `IT-OWN-ARPAV` |
| `TELEMETRY_FAILURE_SEM_POLITICA` | aberto | herdado |
| rehome `regras/sensor_coleta.py` → `coleta/` | registado | mudança de código, não de mapa |

**Uma prova do mapa continua vermelha, e a reprovação é dela:**
`regua_que_carimba_nao_e_regua_que_mede` usa «tem seta para uma zona de acção»
para separar carimbar de medir. Nos quatro casos testados as setas são
`IMPORTS`, e a dependência vai ao contrário do desenho. Não foi afrouxada.

---

## 7 · PARA A LINHA DO SYSTEM MAP

1. **Z-PROVA (33 cartões) e Z-REGUAS (11) estão em `F-INTELIGENCIA`.** São
   provas e regras que servem a COLETA. Dar-lhes faixa própria é decisão de
   representação, e a representação é vossa. É a causa de 90 das 150 arestas
   que atravessam a fronteira.
2. **26 cartões são órfãos falsos por vista.** A correcção é alinhar as vistas
   de quem já fala entre si, não criar ligações.
3. Sete colisões de prefixo, a maior «A prova de...» ×7.

### A integração, medida

A vossa linha andou durante esta missão: `ffa9fb9b → 6ad45b9a`. Comparado
cartão a cartão e território a território, **não há colisão**:

```
a vossa linha acrescentou   C-CI-RELEASE                        1 cartão
                            territórios alterados               NENHUM

esta linha acrescentou      C-PROVA-FRONTEIRA · C-PROVA-DEDUPE
                            C-CENSO-TOPOLOGIA · C-SCRAP-ROTA
                            C-SENSOR-COLETA                     5 cartões
                            Z-GUARDA  F-ESPERA -> F-COLETA
                            Z-ESPERA  (nova)

IDs em colisão              NENHUM
territórios em colisão      NENHUM
```

O conflito textual no JSON é provável; o semântico não existe. Os
`.generated.json` **não se resolvem à mão** — regeneram-se, e agora com os
doze censos, não com os seis de antes.

---

## 8 · O QUE NÃO FOI TOCADO

```
INTELLIGENCE_FUNCIONAL     NAO
PORTAL                     NAO
SECURITY                   NAO
VERCEL_PRODUCTION          NAO
SUPABASE_PRODUCTION        NAO
```

---

# APÊNDICE · SEGUNDA PASSAGEM — a prova, lida uma a uma

O corpo deste relatório fechou a contagem: 100% dos cartões e 100% das arestas.
Contar não é conferir. Esta segunda passagem foi ler, **uma a uma**, o que cada
aresta dá como prova — e a pergunta foi sempre a mesma:

> **a linha citada diz mesmo o que a aresta afirma?**

Sete vezes a resposta foi não, e as sete estão consertadas com prova nova e
teste que morde. Nenhuma delas foi encontrada olhando para o desenho: todas
saíram de abrir o ficheiro na linha indicada e ler.

## A · O ARTEFACTO SEM AUTOR

O registo dos derivados — `data/derivados/REGISTO-DE-ARTEFATOS.json`, a saída
do DERIVED — aparecia com **nove leitores e zero autores**. A porta de admissão
dizia `produces: []`, e o cartão dela afirmava por escrito que «este mapa não
viu nada sair desta peça» — sendo ela quem escreve o livro de decisões de 376 KB.

A causa: o censo só via `open(X, 'w')`. Metade da casa escreve com `pathlib`, e
`LIVRO.write_text(...)` não passa por `open()` nenhum. Nove escritas reais eram
invisíveis, incluindo o **manifesto da corrida**, escrito pelo orquestrador.

E havia um segundo defeito por baixo: o censo deixava a **última** atribuição
ganhar, sem olhar a escopo nem a ordem. Sessenta nomes desta árvore estão
ligados a mais de um ficheiro, e isso já fabricava arestas —
`ask_sintonia.py:351` escreve o *benchmark*, e o mapa dizia que era o *teste*.

## B · O DONO TIRADO À SORTE

Com os autores todos à vista, `data/samples/RUN-MANIFEST.json` passou a ter
**três** peças a escrevê-lo, e o mapa elegia dono por ordem alfabética. O dono
mudou sozinho de `C-PROCEDENCIA` para `C-ESTRADA-PDF` sem ninguém ter tocado no
repositório.

```
UM DONO ELEITO POR ORDEM ALFABÉTICA NÃO É UM DONO.
```

Não foi inventado dono nenhum. O estado passa a registar
`ARTEFACT_MULTIPLE_AUTHORS` e o validador di-lo em voz alta. **É observação, não
prova** — não há lei que proíba dois autores. A escolha é de gente, e é a
pergunta 3 do §Q.

## C · QUATRO VEZES A MESMA LIÇÃO — vocabulário lido como rota

Cada uma destas foi medida sobre uma aresta que o mapa publicava como `PROVEN`:

| # | o que a prova era, de facto | quantas |
|---|---|---|
| 1 | uma linha **dentro de um docstring** — e duas delas eram o próprio varredor a ler a sua documentação | 3 |
| 2 | o campo de relatório `'APIFY_RUNS': 0` — um rótulo que regista que **não** houve chamada | 3 |
| 3 | a tabela `HOSTS`, que **reconhece** o domínio de uma URL que o investigador declarou no ORCID | 3 |
| 4 | a linha `{'LINKEDIN': 'NOT_TESTED', 'YOUTUBE': 'NOT_TESTED',` | 3 |

A pior das quatro: `V-LINKEDIN → C-SCRAP-SOCIAL` tinha como prova
`social_scrap.py:135`, uma linha do bloco **adversarial**, cujo comentário diz
«rotas que a matriz declara proibidas […] TÊM que falhar». O mapa desenhava
como travessia exactamente a rota que aquele bloco existe para provar fechada.

E fica registado o que **não** foi consertado, porque não é conserto de código:
mesmo depois das quatro guardas, este detector só consegue provar que o código
**nomeia** o canal. O cartão dizia «N acções chamam este canal, e cada uma tem
ficheiro e linha que o prova». Passa a dizer o que mediu — **rota DECLARADA**.

```
O CÓDIGO NOMEAR UM CANAL NÃO É ALGO TER VINDO POR ELE.
```

## D · A REGRA QUE PARECIA ESCREVER NO LIVRO QUE AUDITA

`RE_ESCRITA` tinha `>` para apanhar `comando > ficheiro`. Em JavaScript, `=>`
casa com isso. Quatro leituras viravam escritas, e uma é a inversão mais
perigosa que este mapa pode publicar:

```
regras/italy_pilot_guards.mjs:9   WRITES  data/collection-ledger/italy/runs.ndjson
  const runs = readFileSync("data/collection-ledger/italy/runs.ndjson", ...)
```

## E · A PROVA QUE APONTAVA PARA UMA LINHA EM BRANCO

A aresta `C-ADMISSAO → C-READY` é a que diz por onde sai o que passou a porta.
A prova dela estava escrita à mão, **com linha fixa e texto redigido por mim**:

```
"line": 391, "snippet": "def pronto_para_inteligencia(item, decisao)"
```

A função mudou para a linha 426. A 391 é hoje uma linha em branco, e nenhum
portão acusou nada — porque a `P5` só exigia que o número **coubesse** no
ficheiro. Entra a `P5_PROVA_TEM_CONTEUDO`, e a linha passa a procurar-se.

## F · OS NÚMEROS DEPOIS DA SEGUNDA PASSAGEM

```
NODES                                148
EDGES                          573 -> 567
FILE_EDGES                    2061 -> 2068
VIAJA_POR                       16 -> 13

artefactos com autor conhecido        72
artefactos com MAIS DE UM autor        2   RUN-MANIFEST · architecture.declared

arestas provadas por prosa       3 -> 0
arestas provadas por linha oca   1 -> 0
WRITES nascidas de `=>`          4 -> 0

TRAVESSIAS_COLETA_PARA_INTELIGENCIA  149
  -> Z-PROVA                         138      provas que servem a coleta
  -> Z-MOTOR                           6      o motor propriamente dito
  -> Z-REGUAS                          5
  das quais levam DADO                 0

SYSTEM_MAP_CHECK                    PASS
TESTES_SYSTEM_MAP           FAIL · 1        regua_que_carimba (herdada)
FAILING                                6    os mesmos seis módulos
NEW_FAILURES                           0
PRODUCTION_MUTATION                    0
```

**O número que responde à queixa que abriu a missão.** «Cartões da coleta
ligados directo à Intelligence» são 149 — e 138 deles vão parar à `Z-PROVA`, a
zona das **provas**, que está arrumada debaixo de `F-INTELIGENCIA` só porque não
há família para ela. Uma prova a ler o que a coleta produziu é o trabalho dela.
**Ao motor chegam seis, e nenhuma leva dado.**

---

# §Q · EM PALAVRAS FÁCEIS — as vinte perguntas

**1 · Quantos cards da Collection existiam?**
**105.** É o universo do censo determinístico: tudo o que a Collection toca —
as acções, as fontes, as regras, as guardas, as medidas, os canais, as provas
que a medem, e os armazéns. O mapa inteiro tem 148 peças; 105 são a Collection.

**2 · Você abriu e entendeu todos eles?**
Sim, e por dois caminhos independentes. O censo determinístico
(`censo_da_topologia.py`) abriu **105 de 105** e, para cada um, respondeu quem o
chama, se alguma corrida o alcança, o que escreve, o que lê e por que está
sozinho quando está. O censo por leitura abriu **90 de 90** cartões e **297 de
297** arestas, um por um, a ler a linha citada. Os dois discordaram em alguns
pontos, e cada discordância foi ao ficheiro decidir. Sete defeitos reais saíram
daí, todos consertados com prova nova.

**3 · Quantos eram realmente duplicados?**
**Nomes duplicados: zero.** Não há dois cartões com o mesmo nome.
**Conceitos duplicados: dois**, e são de natureza diferente:
`C-GESTAO-COLETA` é um cartão-pacote — o próprio texto dele admite «duas
autoridades distintas» sem relação entre si. `C-LUGAR-COLETA` diz que «o motor
importa esta lei para decidir», e nenhum módulo de runtime a importa: o único
`import` está num teste. **Não foram fundidos nem partidos**, porque isso é
desenho, e o desenho é de gente. Ficam nomeados.

**4 · Por que havia mais de um SINTONIA SCRAP?**
Porque **SCRAP não é uma peça, são cinco**, e as cinco estavam a partilhar o
começo do nome. Não era duplicação: era um prefixo comum a esconder cinco
funções diferentes. Hoje cada uma diz o que faz e onde vive:

```
C-SINTONIA-SCRAP   SCRAP aquisicao · o despachador (Instagram, YouTube)   Z-EXECUCAO
C-SCRAP-ROTA       SCRAP rota e sessao · o despachador (auth_mode)        Z-EXECUCAO
C-SCRAP-SOCIAL     Executor do SCRAP · a aquisicao social                 Z-ACOES
C-SCRAP-LEIS       As leis do SCRAP — a taxonomia canonica da falha       Z-REGUAS
C-SCRAP-GUARDA     A guarda de credencial e de sessao do SCRAP            Z-GUARDA
```

**5 · Quantos cards estavam sem ligação, e qual era a razão de cada grupo?**
Pareciam 28. São **dois**, e os dois estão certos assim:

| grupo | quantos | razão |
|---|---|---|
| **falsos órfãos por vista** | 26 | o cartão TEM ligações — mas a peça do outro lado não pertence à vista aberta. É defeito de representação, não de arquitectura. |
| **armazéns** | 2 | `C-ARMAZEM-IT-SEM-LIVRO` e `C-DERIVED-ARTIFACT` são terminais legítimos: sítios onde a coisa fica. Um armazém não tem para onde apontar. |
| **inexplicados** | **0** | — |

**6 · A Collection agora tem uma ordem clara?**
Sim, e a ordem estava lá — só não estava a ser mostrada. Os territórios eram
listados **por ordem alfabética**, o que punha a admissão antes da colheita. Hoje
estão pela ordem da esteira.

**7 · Qual é a sequência real desde a fonte até READY?**

```
DECIDE · CHECK · DISCOVER · FETCH · RAW · DERIVED · STRUCTURED · ADMISSION · READY
```

Não é opinião: é a lista declarada em `medidas/rastro_da_coleta.ETAPAS`, em
`leis/telemetria.ETAPAS_DA_COLETA` e no `enum etapa_da_coleta` da migração 024.
**Três donos, e os três concordam.**

**8 · Quais cards eram só provas, regras ou infraestrutura e estavam misturados
na esteira?**
**45.** Trinta e quatro em `Z-PROVA` e onze em `Z-REGUAS`. Não estão na esteira
por engano de arrumação: estão em `F-INTELIGENCIA` porque **não existe família
para «prova» nem para «regra»**. As famílias são três, e nenhuma delas serve.
É a pergunta 1 do §R.

**9 · Quantas ligações diretas com Intelligence existiam?**
**149.**

**10 · Quantas eram fluxo de dado real?**
**Zero.** Nenhuma das 149 leva dado. Repartidas: 77 são PROVA, 42 são LEITURA,
14 são CÓDIGO, 10 são REGRA, 6 são CONTROLO.

**11 · Alguma estava pulando a Admission/READY de verdade?**
**Nenhuma.** E não é conclusão de vista de olhos: há uma prova que vira o
argumento do avesso — esvazia a lista de travessias autorizadas e exige que
continue a dar zero. Se um dia algum dado saltar a porta, ela reprova.

**12 · Por que cada ligação restante com Intelligence existe?**
Porque **138 das 149 não vão à Intelligence — vão às PROVAS**, que estão
arrumadas debaixo dela. Uma prova que lê o que a coleta produziu está a fazer o
trabalho dela. **Ao motor propriamente dito chegam SEIS**, e as seis são
controlo e leitura, não dado.

```
-> Z-PROVA    138      as provas que medem a coleta
-> Z-MOTOR      6      o motor propriamente dito
-> Z-REGUAS     5      as réguas
```

**13 · READY hoje tem produtor operacional?**
**Sim.** `orquestrador/orquestrador.py` e `provas/testa_coleta_canonica.py`. O
contrato existe, tem dono, e o código devolve exactamente os campos da lei.

**14 · READY hoje tem consumidor operacional?**
**Não.** Zero. O destino declarado
(`data/samples/PRONTO-PARA-INTELIGENCIA/<RUN_ID>.json`) **não existe no disco**.
O gap chama-se `READY_SEM_CONSUMIDOR` e está no cartão:

```
UMA PORTA POR ONDE NINGUÉM PASSA NÃO É UMA PORTA.
```

**15 · Onde exatamente o SINTONIA Scrap entra na Collection?**
Entra em **FETCH**, e não antes. O despachador chama o executor social, o
executor devolve o item, e daí o caminho é o normal. Onde ele **não** entra:
não decide relevância (isso é a porta de admissão) e **não preserva o bruto** —
esse buraco tem nome, `SCRAP_RAW_NAO_RECEBIDO`, e um teste que o mantém
declarado enquanto não for tapado.

**16 · Ainda existe alguma ferramenta duplicada ou morta?**
Duplicada, não. **Parada, sim, e são duas:** `ferramentas/apify_contrato.py` e
`ferramentas/apify_recuperar.py`. As duas são CLI de mão, nenhum workflow as
corre, nenhum módulo as importa, e **as saídas que declaram nunca existiram**:

```
data/samples/IT-CASOS/IT-APIFY-CONTRATO.json      não existe
data/samples/IT-CASOS/IT-LINKEDIN-RECOVERY.json   não existe
```

Não foram apagadas: as duas estão amarradas a leis da Bíblia (`COL-LAW-018/019`,
`CEN-071`), e apagar código que uma lei nomeia é decisão de gente. É a
pergunta 4 do §R.

**17 · Ainda existe algum card que você não sabe explicar?**
**Não.** Os 105 têm «o que faz» e «por que está aqui», e os que estão sozinhos
têm razão nomeada. `SEM_LIGACAO_INEXPLICADOS = 0`.

**18 · Ainda existe alguma edge que você não sabe explicar?**
**Não.** Todas as 567 arestas do mapa sabem dizer o que transportam. Eram duas
as que não sabiam — e a causa era misturar dois eixos: por serem «declaradas e
ainda não provadas», ficavam também sem categoria. **«Está provada?» e «o que é
que viaja?» são duas perguntas.** As duas continuam cinzentas; passaram a saber
dizer o que levariam.

**19 · O que continua vermelho porque realmente falta arquitetura, dado ou
decisão humana?**

| o que | falta o quê |
|---|---|
| `READY_SEM_CONSUMIDOR` | **arquitectura**: quem, do lado da Intelligence, lê a saída |
| `IT-T2-002` — `IT-OWN-003` ou `IT-OWN-ARPAV` | **decisão humana**, uma escolha entre duas |
| `SCRAP_RAW_NAO_RECEBIDO` | **arquitectura**: onde o bruto do SCRAP é preservado |
| 10 de 20 manifestos de corrida sem campos do contrato | **dívida de dado histórico** |
| `RUN-MANIFEST.json` com três autores | **decisão humana**: de quem é |
| `Z-PROVA` e `Z-REGUAS` sem família própria | **decisão de representação** |
| `regua_que_carimba_nao_e_regua_que_mede` | a pergunta não é decidível a partir do grafo; documentada, **não afrouxada** |

**20 · Ao abrir o System Map agora, Luciano consegue entender a Collection da
esquerda para a direita?**
Sim, com uma ressalva que é honesto dizer. A ordem está certa, os órfãos falsos
desapareceram, cada cartão diz o que é e cada linha diz porquê. **A ressalva:**
a faixa da direita mistura o motor com as provas. Enquanto `Z-PROVA` e
`Z-REGUAS` viverem em `F-INTELIGENCIA`, a leitura «a coleta está toda ligada à
Intelligence» continua a impor-se aos olhos — e são 138 de 149 travessias a
alimentar essa impressão. **Isso não se conserta medindo melhor. Conserta-se
decidindo**, e a decisão é sua.

---

# §R · AS QUATRO PERGUNTAS QUE FICAM PARA GENTE

1. **`Z-PROVA` (34) e `Z-REGUAS` (11) merecem faixa própria?** Hoje o
   vocabulário de famílias tem três valores e nenhum serve para «prova» ou
   «regra». É a causa de 143 das 149 travessias.
2. **De quem é `data/samples/RUN-MANIFEST.json`?** Três peças escrevem-no:
   `C-ORQUESTRADOR`, `C-ESTRADA-PDF` e `C-PROCEDENCIA`. O mapa elege por ordem
   alfabética, e isso muda sozinho quando alguém renomeia uma peça.
3. **`C-GESTAO-COLETA` parte-se em duas? `C-LUGAR-COLETA` fica?** O primeiro
   junta duas autoridades sem relação. O segundo diz que o motor o importa, e
   nenhum módulo de runtime o importa.
4. **`apify_contrato.py` e `apify_recuperar.py` ficam ou saem?** Estão parados,
   nunca produziram nada, e duas leis da Bíblia nomeiam-nos.

---

# APÊNDICE II · C-TOPOLOGY-2 — as quatro decisões, executadas

O §R deste relatório terminava com quatro perguntas para gente. As quatro foram
respondidas, e este apêndice regista o que a resposta mudou no repositório —
não no desenho.

## 1 · GOVERNANÇA — a família que faltava

`Z-PROVA` (34 cartões) e `Z-REGUAS` (11) viviam em `F-INTELIGENCIA` por não
haver sítio para elas. Nasce **`F-GOVERNANCA`**, uma família transversal (uma, e
não duas), e as duas zonas mudam de casa.

```
PROVA ≠ INTELIGÊNCIA.   REGRA ≠ INTELIGÊNCIA.
E NENHUMA DAS DUAS É ETAPA OPERACIONAL.
```

**Nenhuma aresta foi tocada.** As relações são exactamente as mesmas; o que mudou
foi a arrumação. E o número que a queixa original media desabou:

```
COLLECTION → INTELLIGENCE     149  ->    6
COLLECTION → GOVERNANCE         –  ->  143
das que atravessam, levam DADO           0
```

As **seis** que sobram são explicáveis uma a uma, e cada uma tem linha de código:

| aresta | categoria | prova |
|---|---|---|
| `C-ADAMA-IT → C-V21-INGEST` | READ | `motor/v21_ingest.py:266` |
| `C-CI-PERSIST → C-CADEIA-V21` | CONTROL | `supabase-migrate.yml:92` |
| `C-FONTES-EU → C-V21-INGEST` | CODE | `motor/normalize_agro.py:29` |
| `C-PALAVRAS → C-V21-CRUZAMENTO` | RULE | `motor/pacote_convergencia.py:101` |
| `C-ROTULOS → C-V21-CRUZAMENTO` | READ | `motor/pacote_convergencia.py:40` |
| `C-SUPABASE → C-CADEIA-V21` | READ | `motor/cadeia_canonica.sh:151` |

A arrumação mudou também no desenho: a moldura de uma família é o rectângulo que
envolve as zonas dela, e as zonas estavam intercaladas — a caixa da COLETA
engolia a da GOVERNANÇA. Cada família passa a ocupar um bloco contíguo, e a
**governança fica no fim, fora da esteira**. A espinha da vista principal
lê-se da esquerda para a direita e **acaba no READY**.

**Design.** O endereço do ADAMA Design System devolve `HTTP 403` nesta sessão:
`ADAMA_DESIGN_SYSTEM_CONSULTA = NAO_ALCANCADA`. Não foi inventada cor — foi
reutilizado `--color-secondary-purple` do extracto versionado, com moldura mais
fina e borda tracejada para se ler como apoio.
`ADAMA_DESIGN_SYSTEM_MATCH = TOKEN_OFICIAL_REUTILIZADO`.

## 2 · O MANIFESTO — um dono, e a arquitectura a convergir com ele

Três peças escreviam `data/samples/RUN-MANIFEST.json`. **Dono canónico:
`C-PROCEDENCIA`**, porque o manifesto é o registo de procedência da execução.

```
EXECUTAR A CORRIDA NÃO É SER A AUTORIDADE SOBRE A PROCEDÊNCIA DELA.
```

O que o sorteio custava está medido no próprio ficheiro: das 20 corridas, **10**
sem `DATASET_ID`/`SOURCE_VERSION`/`RAW_EVIDENCE_PATH`/`RAW_EVIDENCE_STATE`, e
**3** com `STATUS: OK`, palavra que a lei não aceita. As treze saíram das duas
peças que apendiam o recibo à mão, sem passar pelo contrato.

Nasce a **menor interface possível dentro do dono que já existia** —
`regras/proveniencia.py::acrescentar` — e não um `manifest_writer_v2.py` ao
lado. As outras duas deixam de ter sequer o **caminho** do ficheiro: uma
constante órfã é uma porta destrancada.

```
escritores do RUN-MANIFEST   3  ->  1
```

## 3A · O CARTÃO-PACOTE PARTIDO

`C-GESTAO-COLETA` juntava «duas autoridades distintas». Os chamadores provam que
são duas coisas, e os nomes vieram da função real:

| cartão | o que é | chamadores |
|---|---|---|
| `C-POLITICA-COLETA` | o que colher, quando, e se já temos | 1, e é um teste |
| `C-DIAGNOSTICO` | onde o fluxo parou e quem tem de agir — 17 códigos | runtime, provas e testes |

O cartão antigo **não ficou como alias**: desapareceu, e com ele a colisão de
nome com `C-GESTAO-DA-COLETA`.

## 3B · A LEI QUE FINGIA SER MOTOR

`C-LUGAR-COLETA` dizia «o motor importa esta lei para decidir». Medido: uma linha
de `import` em toda a árvore para cada ficheiro, e as duas em
`tests/test_lugar_do_fato.py`.

A frase não era falha do cartão: era da **regra que a escrevia**. Corrigida,
aparecem **cinco** leis nesta condição, e não uma —
`C-IDENTIDADE`, `C-LUGAR-COLETA`, `C-POLITICA-COLETA`, `C-REGRA-COLETA`,
`C-SAUDE-FONTE`. Todas ficam `DECLARED_RULE_NOT_ENFORCED`, e **nenhuma aresta foi
criada para as fazer parecer usadas**.

A lei continua válida e por isso não foi apagada: mudou de sítio, e os **dois
ficheiros mudaram de gaveta com ela** (`medidas/` → `leis/`), porque o mapa exige
que a prateleira e o mapa contem a mesma história. Nove ficheiros apontavam para
o caminho antigo; os nove foram actualizados.

## 4 · AS DUAS FERRAMENTAS MORTAS

```
ferramentas/apify_contrato.py    importadores 0 · workflows 0 · saída nunca existiu
ferramentas/apify_recuperar.py   importadores 0 · workflows 0 · saída nunca existiu
```

As duas saíram, **sem stub**. Isto **não é «remover Apify do SINTONIA»**:
`apify_pool.py` continua, e os dois workflows que o correm continuam.

A lei não morre com o ficheiro. `COL-LAW-019` nomeava `apify_contrato.py`, e o
que ela exige — ler o contrato do ator **de graça** antes de gastar — continua
canónico. O dono vivo desse conceito já existia: `ferramentas/contrato_ator.py`,
importado em runtime pela esteira. **A ferramenta morta era o duplicado.**

```
UMA LEI NÃO DEPENDE DE UM NOME DE FICHEIRO. DEPENDE DO QUE ELA EXIGE.
```

## 5 · «MEDE» E «CARIMBA» — decidido pela função real

A prova `regua_que_carimba_nao_e_regua_que_mede` estava vermelha desde a missão
anterior, e de propósito: a pergunta dela era indecidível.

```
UM IMPORT NÃO É UM CARIMBO.
E A SETA DO IMPORT APONTA PARA O LADO CONTRÁRIO DA DEPENDÊNCIA.
```

O sinal que decide não está em quem me importa: está no que eu **produzo** e em
**quem o consome**.

| papel | como se mede | quantos |
|---|---|---|
| `STAMPS` | escreve artefacto que uma peça **da esteira** lê | 3 |
| `MEASURES` | lê artefacto; o que escreve só é lido por prova, censo, motor ou ninguém | 15 |
| `DECLARES` | não lê nem escreve artefacto: enuncia vocabulário | 11 |
| `NÃO SEI` | escreve e não há como dizer quem lê | **0** |

Cada peça carrega a frase que o prova. **Não se classifica por nome:** `medidas/`
e `regras/` são gavetas, e uma gaveta não é uma função.

**Família e papel são eixos diferentes**, e há prova disso: quem carimba vive em
duas famílias. Se um dia o papel passar a sair da família, essa prova cai.

## 6 · O RED TEAM — seis ataques, seis reprovações

Nenhuma destas guardas foi suposta: cada uma foi atacada e vista a morder.

| ataque | o que reprovou |
|---|---|
| `Z-PROVA` volta para `F-INTELIGENCIA` | `prova_e_regua_vivem_na_governanca` · `nenhuma_zona_de_prova_ou_regua_ficou_na_inteligencia` · `a_coleta_nao_conversa_com_o_motor_as_centenas` |
| outro componente volta a escrever o `RUN-MANIFEST` | `CANONICAL_OWNER_VIOLATIONS = MULTIPLE_CANONICAL_WRITERS` · `nenhum_dono_canonico_contornado` · `so_a_proveniencia_escreve_o_manifesto` · `P8_DONO_CANONICO` |
| uma régua `MEASURES` passa a escrever estado que a esteira lê | `regua_que_carimba_nao_e_regua_que_mede` |
| a lei volta a exigir o caminho da ferramenta morta | `B9_FICHEIROS_CITADOS` · `BIBLIA_CHECK=FAIL` |
| aresta `DATA` do RAW direto para a Intelligence | `T5b_nenhum_dado_salta_a_porta_para_a_inteligencia` · `nenhum_dado_atravessa_para_a_inteligencia_depois_do_rehome` |
| `'APIFY_RUNS': 0` tenta gerar rota | as três guardas continuam a recusar: rede, tabela de hosts e `NOT_TESTED` |

## 7 · A ENTREGA

```
GIT
  A. BRANCH                        claude/collection-topology-census-v1
  B. INITIAL_HEAD                  53390ddd
  C. FINAL_HEAD                    (o desta entrega)
  D. COMMITS                       5
  E. PUSHED                        SIM

GOVERNANÇA
  F. F_GOVERNANCA_CREATED          SIM · transversal
  G. Z_PROVA_MOVED                 SIM
  H. Z_REGUAS_MOVED                SIM
  I. COLLECTION_INTELLIGENCE_EDGES_BEFORE   149
  J. COLLECTION_INTELLIGENCE_EDGES_AFTER      6
  K. COLLECTION_GOVERNANCE_EDGES_AFTER      143

MANIFESTO
  L. RUN_MANIFEST_OWNER            C-PROCEDENCIA
  M. RUN_MANIFEST_WRITERS_BEFORE   3  (C-ORQUESTRADOR · C-ESTRADA-PDF · C-PROCEDENCIA)
  N. RUN_MANIFEST_WRITERS_AFTER    1  (regras/proveniencia.py)
  O. DIRECT_UNAUTHORIZED_MANIFEST_WRITERS   0

GESTÃO
  P. C_GESTAO_COLETA_SPLIT         SIM
  Q. RESULTING_COMPONENTS          C-POLITICA-COLETA · C-DIAGNOSTICO
  R. OLD_CARD_REMAINING            NÃO

LUGAR
  S. C_LUGAR_COLETA_RUNTIME_CARD   NÃO
  T. RULE_RETAINED                 SIM — Z-REGUAS, F-GOVERNANCA, ficheiros em leis/
  U. RULE_ENFORCED                 NÃO — DECLARED_RULE_NOT_ENFORCED

APIFY
  V. APIFY_CONTRATO_REMOVED        SIM
  W. APIFY_RECUPERAR_REMOVED       SIM
  X. ACTIVE_REFERENCES_TO_REMOVED_TOOLS     0

SEMÂNTICA DO MAPA
  Y. RULE_ROLE_MODEL               STAMPS · MEASURES · DECLARES · NÃO SEI
                                   29 réguas · 3 · 15 · 11 · 0
  Z. MEASURE_VS_STAMP_TEST         PASS  (por correcção semântica, não por afrouxamento)

ARESTAS
  AA. EDGES_TOTAL                  567
  AB. EDGES_WITH_CATEGORY          567
  AC. UNKNOWN_EDGES                0
  AD. COLLECTION_INTELLIGENCE_DATA_EDGES    0

SCRAP
  AE. SCRAP_RAW_NAO_RECEBIDO       ABERTO

READY
  AF. READY_PRODUCTION_CONSUMERS   0
  AG. READY_SEM_CONSUMIDOR         ABERTO

STRUCTURED
  AH. STRUCTURED_OWNER             sem dono ligado
  AI. STRUCTURED_GAP               ABERTO

TESTES
  AJ. BASE_FAIL                    6   (BASE_PASS 63, de 69 módulos)
  AK. FINAL_FAIL                   6   (os mesmos seis)
  AL. NEW_FAILURES                 0
  AM. SYSTEM_MAP_CHECK             PASS
      TESTES_SYSTEM_MAP            PASS  (era FAIL · 1)
      BIBLIA_CHECK                 PASS
      PRODUCTION_MUTATION          0
```

**VEREDITO: `C-TOPOLOGY-2 = PASS`**

```
F_GOVERNANCA          = PROVED
RUN_MANIFEST_OWNER    = UNIQUE
C_GESTAO_COLETA       = SPLIT
C_LUGAR_COLETA        = NO LONGER FALSE RUNTIME COMPONENT
DEAD_APIFY_TOOLS      = REMOVED
MEASURE_VS_STAMP      = SEMANTICALLY DECIDABLE
UNKNOWN_EDGES         = 0
UNEXPLAINED_INTELLIGENCE_EDGES = 0
NEW_FAILURES          = 0
```

**A Collection continua `PARTIAL`, e isso não é falha desta missão.** Os gaps
reais continuam gaps: `READY_SEM_CONSUMIDOR`, `SCRAP_RAW_NAO_RECEBIDO`,
`STRUCTURED_SEM_DONO_LIGADO`, a dívida histórica de 10 manifestos e a escolha
`IT-OWN-003` × `IT-OWN-ARPAV`. Nenhum foi fechado por decreto.

---

# §Q2 · EM PALAVRAS FÁCEIS — as catorze perguntas

**1 · Por que parecia que a Collection tinha 149 ligações com a Intelligence?**
Porque a prateleira das **provas** e a das **réguas** estavam guardadas dentro da
Intelligence. Uma prova que mede a coleta tinha de ser desenhada a atravessar a
fronteira — e são 143 dessas. O número era verdadeiro; a leitura era falsa.

**2 · Quantas sobraram depois de separar a Governança?**
**Seis.** E as seis estão na tabela do §1, cada uma com ficheiro e linha.

**3 · Alguma delas leva dado?**
**Nenhuma.** Três são leitura, uma é código, uma é regra, uma é controlo. E há
uma prova que tenta o contrário: mete um atalho `DATA` do RAW para o motor e
exige que ela reprove. Reprova.

**4 · Quem é agora o dono único do manifesto da corrida?**
**`C-PROCEDENCIA`** — `regras/proveniencia.py`. É a única peça que escreve o
ficheiro, e há três guardas a medir isso, não a repeti-lo.

**5 · Por que os outros dois deixaram de ser donos?**
Porque correr não é ter autoridade. O orquestrador inicia a corrida e a estrada
do PDF conhece os detalhes da dela — os dois continuam a trazer tudo o que
sabem. **Escrever** é do dono da lei. E não é teoria: enquanto escreveram por
fora, dez das vinte corridas ficaram sem quatro campos do contrato e três
gravaram uma palavra que a lei não aceita.

**6 · Em que dois componentes o `C-GESTAO-COLETA` virou?**
`C-POLITICA-COLETA` (o que colher, quando, e se já temos) e `C-DIAGNOSTICO` (onde
o fluxo parou e quem tem de agir). Os nomes vieram da função, não de «parte 1» e
«parte 2». O cartão antigo não ficou.

**7 · O que aconteceu com o `C-LUGAR-COLETA`?**
Saiu da esteira. A lei é válida e ficou; a frase «o motor importa esta lei para
decidir» é que era falsa. Está em `F-GOVERNANCA`, marcada
`DECLARED_RULE_NOT_ENFORCED`, e os ficheiros mudaram de `medidas/` para `leis/`,
que é onde as leis vivem. **Aplicá-la quando o dado entra continua por decidir.**

**8 · As duas ferramentas Apify mortas saíram?**
Saíram, e sem deixar ficheiro vazio no lugar. Zero referências activas.

**9 · Alguma função real foi perdida?**
**Não.** `apify_contrato.py` era o duplicado de `ferramentas/contrato_ator.py`,
que está vivo e é importado pela esteira em runtime — é ele que a lei aponta
agora. `apify_recuperar.py` nunca produziu a saída que declarava. E
`apify_pool.py`, a rota paga a sério, não foi tocado.

**10 · A regra «mede vs carimba» agora é decidida por quê?**
Pelo que a peça **produz** e por **quem consome** o que ela produz. Carimba quem
escreve algo que uma peça da esteira lê — isso entra no caminho do item. Mede
quem olha e dá nota. Antes a pergunta era «tem uma seta a apontar para uma zona
de acção?», e essa seta era um `import`, que aponta ao contrário da dependência.

**11 · O mapa agora distingue dependência de código de fluxo de dados?**
Sim, e são categorias diferentes em cada aresta: `CODE` é um import, `DATA` é
artefacto a viajar. Das 567 arestas, **567 sabem dizer o que transportam** e
nenhuma ficou `UNKNOWN`. Das seis que atravessam para a Intelligence, uma é
`CODE` e **nenhuma** é `DATA`.

**12 · Ainda existe algum card operacional cuja função não sabemos?**
**Não.** Os 105 cartões da Collection têm «o que faz» e «por que está aqui», os
dois que estão sozinhos são armazéns (terminais legítimos), e
`SEM_LIGACAO_INEXPLICADOS = 0`.

**13 · Ainda existe alguma edge cuja razão não sabemos?**
**Não.** `UNKNOWN_EDGES = 0`.

**14 · Quais gaps reais da Collection continuam?**

| gap | falta o quê |
|---|---|
| `READY_SEM_CONSUMIDOR` | **arquitectura** — quem, do lado da Intelligence, lê a saída. Produtores há dois; consumidores, zero |
| `SCRAP_RAW_NAO_RECEBIDO` | **arquitectura** — onde o bruto do SCRAP é preservado |
| `STRUCTURED_SEM_DONO_LIGADO` | **arquitectura** — o STRUCTURED continua sem dono ligado |
| 10 de 20 manifestos históricos incompletos | **dívida de dado** — a causa está fechada, a história fica |
| `IT-T2-002`: `IT-OWN-003` ou `IT-OWN-ARPAV` | **decisão humana**, uma escolha entre duas |
| 5 leis `DECLARED_RULE_NOT_ENFORCED` | **decisão** — aplicar, ou assumir que são só doutrina |
| 3 peças em `Z-REGRAS` que não carimbam | **arrumação** — `C-IT-CONTRATOS`, `C-PALAVRAS` e `C-SENSOR-COLETA` (este é um coletor a viver em `regras/`; o rehome continua registado) |

---

## 8 · A LINHA PARALELA — o que existe, e o que NÃO foi integrado

`git fetch --all --prune` no fecho encontrou duas linhas que se mexeram:

| ramo | tocou o System Map? | integrado? |
|---|---|---|
| `claude/sintonia-scrap-stories-no-apify-v1` | não | — |
| `claude/security-s2-client-server-boundary-v1` | **sim, 26 ficheiros** | **não** |

A linha de Security partiu de `1c99a48b` — a base de **antes** destas duas
missões — e mexeu no `architecture.declared.json`, no `map.js`, no `map.css` e
no `index.html`. Ela ainda tem **22 zonas, 122 peças e `Z-PROVA` em
`F-INTELIGENCIA`**.

**Não foi integrada, e é de propósito:** Security Foundation está fora do
escopo desta missão, e puxar o trabalho dela para cá seria decidir por ela. O
que fica registado, para quem fizer a junção:

- os `.generated.json` **não se resolvem à mão**: correm-se
  `scan_repo.py` e `generate_system_map.py` e o conflito desaparece;
- o que precisa de olhos é o `architecture.declared.json` — lá a família de
  `Z-PROVA` ainda é `F-INTELIGENCIA`, e aqui é `F-GOVERNANCA`. **A semântica
  desta missão é a mais nova**, e as guardas que a seguram estão no §6;
- `map.css` e `index.html` mudaram dos dois lados por razões diferentes: aqui,
  a cor e a moldura da governança.
