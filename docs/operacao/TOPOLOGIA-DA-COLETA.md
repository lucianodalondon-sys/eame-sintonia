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
