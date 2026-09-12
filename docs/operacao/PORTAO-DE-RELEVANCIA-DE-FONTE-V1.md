# PORTÃO DE RELEVÂNCIA DE FONTE — V1

```
MISSAO                       SR-01
CONTRATO                     RELEVANCIA_DA_FONTE/v1
DONO DA LEI                  leis/relevancia_da_fonte.py
ONDE ESTE RELATORIO VIVE     docs/operacao/  (a casa que esta arvore ja usa para
                             portões e censos — nenhuma árvore nova foi criada)
```

> **Por que não `docs/source-relevance/`.** A missão sugeria esse caminho «MAS: se
> já existir diretório/artefato canônico equivalente, USAR O EXISTENTE». Existe:
> `docs/operacao/` já guarda `GATE-DE-ACEITACAO-TEMATICA-V1.md`,
> `BASELINE-ADMISSION-T3-V1.md`, `CENSO-DA-COLETA.md` e
> `COLLECTION-V1-CLOSE-GATES.md`. Uma árvore nova só por arrumação estética
> criaria um segundo sítio onde procurar a mesma espécie de documento.

---

## A · BRANCH, BASE E HEAD

```
BRANCH DE TRABALHO   claude/magical-ptolemy-bonfgd
BASE                 origin/claude/prove-canonical-e2e-from-request-v1
                     0b49ae7368fec5a85c97bdeba76cf6231f186dec  ·  2026-09-12T15:51:57Z
```

### A escolha da base, e por que não foi `origin/main`

A sessão começou com a árvore em `origin/main` (`df165da9`). Medido:

| medição | resultado |
|---|---|
| `origin/main` é ancestral da linha da Collection? | **não** |
| divergência `main` ↔ `source-relevance-study-v1` | main +1, a outra **+216** |
| divergência `main` ↔ `prove-canonical-e2e-from-request-v1` | main +1, a outra **+248** |
| merge-base comum | `56fdb8ca` · 2026-09-07 |

E, decisivo, o que **não existe** em `origin/main`:

```
provas/gate_de_aceitacao_tematica.py        ausente em main · presente na linha da Collection
tests/test_gate_de_aceitacao_tematica.py    ausente em main
provas/mutacao_do_gate.py                   ausente em main
BIBLIA-CANONICA-DA-COLETA.md                ausente em main
coleta/social_rotas.py                      ausente em main
admissao/sala_de_espera.py                  ausente em main
```

Construir sobre `main` obrigaria a **recriar do zero** peças que a missão mandou
reutilizar («reutilizá-las em vez de criar concorrentes»). O ramo de trabalho foi
portanto criado a partir da linha funcional da Collection, sem merge, sem rebase
destrutivo e sem force-push — o ramo não existia no remoto, e não havia trabalho
local para perder.

`claude/dazzling-cerf-27a7v2` é mais recente (2026-09-12T15:55:43) mas é uma
**missão paralela do System Map** (toca `system-map/`, `AGENTS.md`,
`italia-portale/client/system-map/`). Não é a linha da Collection e não foi tocada.

### ⚠️ O nome do ramo `claude/source-relevance-study-v1` engana

Apesar do nome, esse ramo **não estuda relevância de fonte**. O que ele produziu
foi medido, ficheiro a ficheiro:

```
provas/gate_de_aceitacao_tematica.py     gate de ITEM (T3), não de fonte
provas/amostragem_neutra_t3.py           amostragem de DOCUMENTOS
provas/fechar_ground_truth_t3.py         gabarito de DOCUMENTOS
data/derivados/BASELINE-ADMISSION-T3-V1.json   baseline da porta de ADMISSÃO
```

Ele é ancestral desta base, logo todo o seu trabalho já está nesta árvore, e
**nada dele foi duplicado.**

---

## B · A BASELINE MEDIDA — O QUE HAVIA ANTES

### As 77 fontes do cadastro único

`system-map/data/sources.generated.json` (23 do atlas europeu + 54 do master
italiano). Quantas declaram cada coisa, contando «NÃO SEI» como ausência:

| campo | tem | de |
|---|---|---|
| `SOURCE_ID` | 77 | 77 |
| território / propósito declarado | 77 | 77 |
| `access_method` | 26 | 77 |
| `EVIDENCE` | 23 | 77 |
| `REAL_EXAMPLE` | 22 | 77 |
| `VERDICT` (≠ NÃO SEI) | 21 | 77 |
| `ADAMA_USE_CASE` | 17 | 77 |
| automation feasibility | 16 | 77 |
| legal / access risk | 16 | 77 |
| collection feasibility | 15 | 77 |
| contrato operacional | 5 | 77 |
| **decisão explícita e auditável de relevância** | **0** | **77** |

### As respostas às nove perguntas do censo

**C · Quantas fontes têm decisão EXPLÍCITA e AUDITÁVEL de relevância?** **Zero.**
Não havia livro, não havia enum, não havia dono. Um único ficheiro em toda a
árvore pronunciava as palavras `SOURCE_RELEVANCE`, e era para avisar que ela
**não** é relevância de documento: `provas/candidatos_tematicos.py:74`.

**D · Quantas têm algo que PARECE relevância e mistura eixos?** As 21 com
`VERDICT ≠ NÃO SEI`. O próprio atlas define os seus vereditos assim:

| verdict | o que o atlas escreve | eixos que isso mistura |
|---|---|---|
| `GREEN` | «verificada, **acessível**, **útil**, com exemplo real capturado» | acesso · utilidade · evidência |
| `YELLOW` | «fonte real e **relevante**, mas com atrito: acesso difícil, licença dúbia, granularidade fraca, frequência ruim ou automação incerta» | **relevância** · acesso · licença · qualidade · frequência · automação |
| `RED` | «descartada por motivo concreto — não serve, **não é acessível**, ou o uso é **proibido**» | relevância · acesso · legalidade |
| `NÃO SEI` | «não foi possível verificar» | medição ausente |

**E · Quantas podiam disparar coleta sem qualquer decisão de relevância?** **54 de
77** — todas as que caem num território com executor declarado (T2, T3, T4, T7, T9).

**F · Quantas podiam correr rota paga com relevância não avaliada?** **8** — as
oito fontes de T9. As oito têm `verdict = NÃO SEI` **e** `access_method = NÃO SEI`,
e o executor de T9 declara `custo: "pago quando passa pela rota Apify"`.

**G · As fontes novas passam por CANDIDATA → EM_ANALISE → PROMOVIDA/RECUSADA?**
Os quatro estados estão **escritos** em `candidatas/FONTES-CANDIDATAS.json`, e
**nenhum código transiciona entre eles**. A fila tinha 0 candidatas.

**H · Algum caminho cria/usa fonte pulando a fila?** Sim, e de uma maneira que
ninguém tinha visto: **a própria porta escrevia num ficheiro que ninguém lia.**

```
candidatas/fonte_nova.py:63   FILA = data/samples/FONTES-CANDIDATAS.json   ← não existe
COL-LAW-053 · AGENTS.md
scan_sources.py · INDICE-DE-FONTES.md        candidatas/FONTES-CANDIDATAS.json   ← a real
```

    UMA FILA COM DUAS MORADAS É DUAS FILAS,
    E A QUE NINGUÉM LÊ NÃO É UMA FILA: É UMA GAVETA.

Toda candidata registada por aquela porta aterrava fora do alcance do mapa, do
censo e da lei — e `candidates: 0` no System Map não conseguia distinguir «ninguém
registou nenhuma» de «registaram e foram para outro sítio». **Corrigido nesta
missão**, com prova em `tests/test_relevancia_da_fonte.py::test_a_fila_escreve_onde_a_lei_e_o_mapa_leem`.

**I · O `GREEN/YELLOW/RED/NÃO SEI` do atlas é relevância, saúde, acessibilidade ou
mistura?** **Mistura**, e a prova que fecha o assunto está na tabela do próprio
atlas, acima: `YELLOW` **declara a fonte relevante** e mesmo assim não é verde —
porque o amarelo está a falar de acesso, licença e automação. Logo o verde não
está a medir relevância.

---

## C · O DONO ATUAL DE CADA CONCEITO — MEDIDO, NÃO SUPOSTO

| conceito | dono | está no caminho real? |
|---|---|---|
| `ITEM_RELEVANCE` / admissão | `admissao/admissao.py` | **sim** |
| avaliação do *mecanismo* de relevância de item | `provas/gate_de_aceitacao_tematica.py` | só avaliação |
| relevância de **caso** (oportunidade ADAMA) | `leis/adama_relevance.py` | camada de inteligência |
| `SOURCE_HEALTH` | `medidas/source_health.py` · COL-LAW-028 | parcial |
| medidas e ciclo de vida da fonte (contrato) | `leis/aprender_com_a_fonte.py` | **não** — contrato |
| `COLLECTION_PRIORITY` | `leis/politica_da_coleta.py` | **não** — `MODE: SHADOW_ONLY` |
| acesso / rota | `pedido/receitas.py::_sabe_o_caminho` · `coleta/social_rotas.py::permitido` | sim |
| fila de candidatas | `candidatas/fonte_nova.py` | sim (e escrevia no sítio errado) |
| **`SOURCE_RELEVANCE`** | **NINGUÉM** | **não existia** |

---

## D · ONDE ESTAVA O PRIMEIRO BYPASS

```
FIRST_PRE_SPEND_RELEVANCE_GATE = NONE
```

O caminho canónico, rastreado com `--so-plano` (custo real = 0):

```
Pedido                 pedido/pedido.py         valida alvo, acionamento, escopo
  ↓
SOURCE LOOKUP + PLANO  pedido/receitas.py       filtra fontes por território,
                       ::resolver               país e tema · mede o ACESSO
  ↓
ROTA + EXECUÇÃO        orquestrador/            e = plano.executores[0]
                       orquestrador.py::correr  subprocess.run(executor)
```

O único requisito para correr era `bool(plano.executores)` — isto é, **existir uma
linha no dicionário `EXECUTORES` daquele território**. As fontes filtradas nem
entravam na decisão: `da_para_correr` nunca as olhava.

Os três rastreios que a missão pediu, todos sem gastar:

| fonte | território | rota | o que acontecia antes |
|---|---|---|---|
| `IT-T2-002` (gratuita, conhecida) | T2 | HTTP direto · gratuito | corria — e aparecia na lista «NÃO SEI como se chega» do próprio plano |
| as 8 de T9 (potencialmente pagas) | T9 | YouTube/Instagram/LinkedIn/Facebook · **pago via Apify** | o plano dizia «quem vai correr: comunicacao-publica» com `verdict = NÃO SEI` nas oito |
| `IT-T5-001` (não avaliada, sem executor) | T5 | — | parava por **falta de caminho**, nunca por falta de avaliação |

O terceiro caso é o que mostra o defeito com mais clareza: o sistema já sabia
dizer «não sei COMO chegar lá». Nunca soube dizer «não sei SE vale a pena».

---

## E · O MODELO FINAL

### A decisão é do par, e o eixo é o da casa

```
SOURCE_RELEVANCE  ∈  (SOURCE_ID, PROPOSITO)      — nunca da fonte sozinha
```

O `PROPOSITO` é o território que o atlas e o pedido **já** usam (T1..T13). Não se
inventou taxonomia. As cinco palavras do resultado vêm do dono delas,
`admissao/admissao.py::RESULTADOS` (COL-LAW-038), importadas — não copiadas — e há
teste que reprova se as duas listas divergirem.

| estado | significa |
|---|---|
| `SIM` | provou que serve para este propósito |
| `NAO` | olhou-se, e provou que **não** serve para este propósito |
| `NAO_SEI` | avaliou-se e não deu para concluir |
| `NAO_SE_APLICA` | a pergunta não faz sentido para este par |
| `ERRO` | não foi possível avaliar — **não é uma rejeição** |
| `NAO_AVALIADA` | ninguém olhou. **Não é um resultado**, e por isso não está em `RESULTADOS` |

    NAO_AVALIADA ≠ NAO_SEI ≠ ERRO ≠ NAO
    Uma só delas é um julgamento. As outras três são confissões.

### O portão, e o que ele guarda

```
SIM            -> AUTORIZA
NAO            -> BARRA            (inclusive na rota de graça)
NAO_SE_APLICA  -> BARRA
NAO_SEI        -> EXIGE_AVALIACAO
ERRO           -> EXIGE_AVALIACAO
NAO_AVALIADA   -> EXIGE_AVALIACAO
```

**Três vereditos, não um booleano.** Um booleano obrigaria «não sei» a escolher um
lado, e o lado que ele escolheria seria sempre o «não».

E o portão guarda o **gasto**, não a observação — é a COL-LAW-018 («o portão grátis
vem antes do gasto») aplicada um andar acima. Três formas de gastar fecham a porta
quando a relevância não é `SIM`:

```
ROTA_PAGA           custo do executor ≠ "gratuito"   (e «NÃO SEI» conta como paga)
COLETA_RECORRENTE   acionamento = AGENDADO
COLETA_TOTAL        escopo = TOTAL
```

Com rota gratuita, acionamento manual e escopo pontual, `EXIGE_AVALIACAO` deixa
passar — **e fica escrito no recibo**. É a prova barata, não coleta normal.

### Onde ele vive, e por que aí

```
leis/relevancia_da_fonte.py     A LEI       vocabulário, contrato da decisão,
                                            o livro, e a função `portao()`
pedido/receitas.py::resolver    PERGUNTA    é aqui que o pedido vira fonte + executor
orquestrador/.py::correr        OBEDECE     é quem gasta, e é quem recusa
```

Um dono da regra, um sítio que pergunta, um sítio que obedece. A regra **não está
copiada** em nenhum dos dois chamadores.

A recusa tem estado próprio — `STATUS: BARRADO_NA_RELEVANCIA`, `exit 3` —, e
**não** é `FAILED` nem `SEM_CAMINHO`: uma decisão desta casa não é uma corrida que
rebentou nem um caminho que falta.

### A prova barata — a saída do impasse

`candidatas/prova_barata.py`. O portão recusa gasto sobre fonte não avaliada, e
avaliar exige olhar; sem uma forma barata de olhar, o portão seria uma porta
trancada com a chave do lado de dentro.

```
DEGRAU 0 · ACERVO     o que esta casa JÁ guardou desta fonte.
                      Zero rede, zero dinheiro. TETO = 3 unidades.
DEGRAU 1 · SONDA      uma ida ao mundo, com teto, rota gratuita e uma só passagem.
```

    PROVA_BARATA_NUNCA_PAGA = True

⚠️ **E a prova não decide. Observa.** O campo `DECISAO` sai sempre `NAO_TOMADA`, e
`'NAO_TOMADA'` não pertence a `RESULTADOS` — por construção, a observação não pode
ser lida como veredito. Transformar «a amostra que consegui apanhar» em «o que a
fonte é» faria a primeira amostra magra condenar a fonte com ar de medição.

O degrau 1 **recusa-se a correr nesta árvore** e diz porquê: o executor canónico do
SINTONIA SCRAP não vive nesta linha, e chamar um adapter diretamente criaria um
segundo caminho de coleta (COL-LAW-011). Isso é `ERRO` de avaliação, e o teste
exige que a mensagem o diga — nunca uma fonte que não serve.

---

## F · O CENSO DAS FONTES ATUAIS

`py provas/censo_de_relevancia_das_fontes.py` · derivado, nada escrito à mão.

```
FONTES_NO_CADASTRO                 77
COM_DECISAO_DE_RELEVANCIA           0
SEM_DECISAO_DE_RELEVANCIA          77
PODEM_DISPARAR_COLETA              54
PODEM_GASTAR_DINHEIRO               8
COLETAM_SEM_AVALIACAO              54
GASTAM_SEM_AVALIACAO                8
BARRADAS_PELO_PORTAO_NO_DINHEIRO    8
DECISOES_NO_LIVRO                   0

por buraco    PODE_COLETAR_DE_GRACA_SEM_AVALIACAO  46
              SEM_EXECUTOR_E_SEM_AVALIACAO         23
              PODE_GASTAR_SEM_AVALIACAO             8
por veredito  EXIGE_AVALIACAO                      77
```

### G · Quantas estão protegidas

**As 8 que podiam gastar dinheiro.** Todas barradas, e o barramento está no caminho
real — provado por `orq.correr()` e pela linha de comando (`exit 3`).

**As 54 que podiam disparar coleta** deixaram de poder fazê-lo de forma recorrente
(`AGENDADO`) ou total (`TOTAL`) sem avaliação.

### H · Quantas ainda podem gastar sem avaliação

```
ROTA PAGA            0   de 8
COLETA RECORRENTE    0
COLETA TOTAL         0
```

**Mas 46 ainda podem ser observadas de graça, à mão e pontualmente, sem decisão de
relevância** — e isso é deliberado, não um buraco escondido: é a prova barata, e
cada corrida escreve `RELEVANCIA_DA_FONTE` no recibo com o estado sob o qual
aconteceu. O que deixou de existir é a coleta *cara*, *recorrente* ou *massiva*
sobre fonte que ninguém abriu.

### Por que NENHUMA decisão foi portada do atlas

```
PORTADAS_DO_ATLAS = 0
```

A missão autorizava portar «se for barato e determinístico» **e** se se provasse
que `GREEN` quer dizer exatamente «relevante». Foi medido, e não quer — ver a
tabela em **B · D**. Portar `GREEN → SIM` promoveria **17 fontes por convenção de
cor** e deixaria de fora **4** que o atlas declara relevantes (as `YELLOW`).

    UMA COR NÃO É UMA DECISÃO. PINTAR NÃO É AVALIAR.

Há teste que reprova se o atlas deixar de declarar `YELLOW` como relevante — porque
nesse dia a base desta recusa muda, e tem de ser remedida em vez de herdada.

---

## I · TESTES

`tests/test_relevancia_da_fonte.py` — **73 testes, 20 subtestes**, todos verdes.

As vinte propriedades que a missão exigiu, e onde cada uma está provada:

| # | propriedade | classe de teste |
|---|---|---|
| 1 | fonte não promovida não entra em coleta normal | `OPortaoEstaNoCaminhoReal` |
| 2 | `UNKNOWN` não vira `NOT_RELEVANT` | `AsQuatroAusenciasNaoSaoAMesmaCoisa` |
| 3 | `ERROR` não vira `NOT_RELEVANT` | idem |
| 4 | `ACCESS_BLOCKED` não vira `NOT_RELEVANT` | `OsEixosNaoSePreenchemUnsAosOutros` |
| 5 | `SOURCE_HEALTH` não vira `SOURCE_RELEVANCE` | idem (assinatura de `estado()`) |
| 6 | custo zero não vira relevante | idem |
| 7 | custo alto não vira irrelevante | idem |
| 8 | relevância do universo A não vaza para B | `ARelevanciaEDoParNaoDaFonte` |
| 9 | um item negativo não condena a fonte | `OItemNaoFalaPelaFonte` |
| 10 | um item positivo não promove a fonte | idem |
| 11 | rota paga não executa sem portão | `ARotaPagaNaoCorreSemPortao` |
| 12 | fila de candidatas não fabrica `SOURCE_ID` | `AFonteNaoNasceDeUmaURL` |
| 13 | URL não vira `SOURCE_ID` | idem |
| 14 | falta de decisão falha alto no ponto certo | `OPortaoEstaNoCaminhoReal` |
| 15 | decisão tem evidência apontável | `ADecisaoTemProvaVersaoEHistoria` |
| 16 | decisão tem versão | idem |
| 17 | decisão negativa fica preservada | idem |
| 18 | rejeição de fonte ≠ erro de acesso | `ONaoENaoEOErroEErro` |
| 19 | promoção ≠ coleta automática | `ARotaPagaNaoCorreSemPortao` |
| 20 | regressão das fontes atuais limpa | `OCensoMedeEDeclara` |

⚠️ **Metade destes testes não fala com a lei: fala com o caminho real**
(`Pedido → receitas.resolver → orquestrador.correr`). Uma lei com testes verdes e
nenhum chamador é um documento com sintaxe de Python.

---

## J · RED TEAM

`py provas/red_team_da_relevancia_da_fonte.py`

```
ATAQUES = 27   MORTOS = 27   VIVOS = 0
```

Os 25 que a missão nomeou, mais dois que o desenho convidava:

```
RT-26  custo «NAO SEI» passar por gratuito
RT-27  um SIM numa fonte abrir a porta às outras sete do território
```

### O ataque que sobreviveu à primeira volta, e o que ele ensinou

`RT-13` (*keyword miss vira NO*) **sobreviveu** na primeira execução. A causa não
era o portão: era o ataque. Ele procurava a palavra `keyword` no ficheiro da lei —
e encontrava-a, porque a lei escreve `NO KEYWORD MATCH != NOT_RELEVANT` no próprio
texto. **O ataque estava a apanhar a defesa.**

    PROCURAR UMA PALAVRA NUM FICHEIRO NÃO É MEDIR O QUE ELE FAZ.

Reescrito para medir comportamento: a lei não importa `re`, o portão não recebe
texto nenhum por onde comparar, e uma fonte sem uma única palavra em comum com o
propósito continua `NAO_AVALIADA`.

E um ataque que **rebenta** é contado como `ATAQUE_VIVO`, nunca como defesa —
contar exceção como vitória seria a mesma confusão que esta missão existe para
matar.

---

## K · MUTATION

`py provas/mutacao_do_portao_de_relevancia.py`

```
MUTANTES = 20   SURVIVORS = 0
```

Cada mutante altera o **ficheiro real** do dono, corre a suíte **real**, exige que
ela **reprove**, restaura e confere o `sha256`. Uma âncora que não é única conta
como **sobrevivente**, nunca como mutante morto — contar isso como defesa seria
fabricar contagem.

### Os dois mutantes que sobreviveram à primeira volta

Foram buracos reais na suíte, e os dois foram tapados com testes novos:

| mutante | o que a suíte não defendia |
|---|---|
| «a fonte deixa de ser parte da chave» | a suíte provava que o `PROPOSITO` fazia parte da chave e **nunca** que o `SOURCE_ID` também. Tirar a fonte do filtro passava despercebido, e a decisão de uma fonte respondia pelas outras dezasseis de T3. |
| «a sonda aceita rota paga» | `sondar()` levanta sempre (o transporte canónico não vive nesta árvore), por isso tirar a trava do dinheiro não mudava nada visível. **Duas recusas diferentes que produzem a mesma exceção são uma trava e um acaso com o mesmo aspeto.** |

---

## L · REGRESSÃO

```
BASE                    origin/claude/prove-canonical-e2e-from-request-v1 @ 0b49ae73
COMANDO                 python3 -m pytest tests -q
                        (--ignore de test_alvo_estruturado_resolvido.py e
                         test_comunicacao.py: são scripts com SystemExit ao nível
                         do módulo, e matam a COLEÇÃO do pytest, não um teste)
```

| medição | falhas | passes | subtestes |
|---|---|---|---|
| ANTES · árvore limpa, sem este código | **22** | 2427 | 12550 |
| DEPOIS · mesma árvore limpa, com este código | **22** | 2500 | 12685 |

```
NEW_FAILURES      = 0
FALHAS QUE SUMIRAM = 0
```

Os dois conjuntos de falhas são **idênticos linha a linha**. A única diferença em
todo o `diff` é o *valor* dentro de um subteste que já estava vermelho
(`TEST_COUNT_CURRENT` passou de 2.524 para 2.597, porque a suíte cresceu) — o mesmo
teste, a falhar pelo mesmo motivo.

E as provas do mapa, corridas como o `AGENTS.md` manda:

```
SYSTEM_MAP_CHECK   = PASS   (21/21 regras)
TESTES_SYSTEM_MAP  = PASS
```

⚠️ **As três medições têm de correr em série.** Correr a suíte e as provas do mapa
ao mesmo tempo fez `scanner_e_deterministico` reprovar uma vez: `tests/` também
invoca scripts do mapa, e as duas corridas disputavam
`architecture.generated.json`. Em série, passa. Foi engano da medição, não do
código, e fica escrito porque quem repetir isto vai tropeçar no mesmo sítio.

### ⚠️ A suíte não é idempotente, e isso custou uma medição falsa

Numa das corridas, a suíte completa **executou uma coleta italiana real** e deixou
na árvore quatro pastas novas em `data/collection-store/italy/IT-T2-002/` e quatro
ficheiros rastreados modificados (`observations.ndjson`, `runs.ndjson`,
`LIVRO-DE-DECISOES.json`, `estradas-it.generated.json`). Na corrida **seguinte**,
seis testes sem relação nenhuma com esta missão reprovaram por causa desses dados.

A primeira leitura — «28 falhas, logo 6 regressões» — estava errada, e foi
descartada pela medição correta: árvore restaurada, código removido, suíte corrida
→ **22**. Árvore restaurada, código reposto, suíte corrida → **22**.

    UMA SUÍTE QUE ESCREVE NA ÁRVORE MEDE A CORRIDA ANTERIOR, NÃO O CÓDIGO.

Isto **não foi causado por esta missão** e **não foi corrigido por ela** — fica
nomeado em **N · O QUE CONTINUA DESCONHECIDO**.

### Falhas pré-existentes

```
tests/es/test_adama_es_gate.py            1
tests/test_canonico.py                    1   (conta a suíte e exige o número no doc)
tests/test_evidence.py                    2 + 3 subtestes
tests/test_fundacao_da_coleta.py          1
tests/test_handoff.py                     2
tests/test_metricas.py                    1 + 4 subtestes
tests/test_operacao.py                    1
tests/test_proveniencia.py                5
tests/test_trava_da_inteligencia.py       1
```

`test_canonico` e `test_metricas` contam a suíte e exigem que um documento declare
o total. Já falhavam antes; acrescentar testes muda o número que elas comparam, mas
**não** muda o facto de já estarem vermelhas.

---

## M · SYSTEM MAP

A arquitetura mudou: há um dono novo e arestas novas. A cadeia foi **lida** de
`system-map/scripts/CADEIA-DO-MAPA.json` naquele HEAD — **7 passos de `REGERAR`
e 1 de `VALIDAR`**, não um número suposto — e corrida na ordem declarada.

```
SYSTEM_MAP_CHECK = PASS   ·   21/21 regras
MAPA=OK · peças=166 · ligações=711 · cobertura=748/1516 ficheiros
```

### As duas peças novas

| id | território | kind | ficheiro |
|---|---|---|---|
| `C-RELEVANCIA-FONTE` | `Z-REGUAS` | `gate` | `leis/relevancia_da_fonte.py` |
| `C-PROVA-BARATA` | `Z-CANDIDATAS` | `engine` | `candidatas/prova_barata.py` |

Declaradas em `system-map/data/architecture.declared.json` — o ficheiro **declarado**,
que é onde o que o código não sabe de si mesmo se escreve. Nenhum JSON **gerado** foi
tocado à mão; os oito ficheiros `*.generated.json` desta árvore são todos saída da
cadeia.

### As arestas, e nenhuma foi desenhada à mão

Todas derivadas de `import` real e todas `status: PROVEN`:

```
C-RELEVANCIA-FONTE  ->  C-RECEITAS       IMPORTS   o plano pergunta ao portão
C-ADMISSAO          ->  C-RELEVANCIA-FONTE IMPORTS o eixo semântico vem do dono dele
C-RELEVANCIA-FONTE  ->  C-PROVA-BARATA   IMPORTS   a sonda obedece à lei
C-RELEVANCIA-FONTE  ->  C-PROVA-COLETA   IMPORTS   censo · red team · mutação
```

Não há aresta `C-RELEVANCIA-FONTE → C-ORQUESTRADOR`, e isso está certo: o
orquestrador **não importa a lei**. Ele lê `plano.relevancia`, que o planeador já
preencheu. Um dono da regra, um sítio que pergunta, um sítio que obedece.

### O que o mapa passou a conseguir distinguir

```
SOURCE CANDIDATE     C-PORTA-FONTE        Z-CANDIDATAS
PROVA BARATA         C-PROVA-BARATA       Z-CANDIDATAS
SOURCE REGISTERED    o atlas + sources.generated.json
RELEVANCE DECISION   C-RELEVANCIA-FONTE   (o livro)
COLLECTION GATE      C-RELEVANCIA-FONTE   (o portão que lê o livro)
COLLECTION           C-ORQUESTRADOR + executores
```

⚠️ As duas peças nascem **`PENDING` (🟡), não verdes**. `P6_VERDE_TEM_PROVA` exige
mais do que o ficheiro existir, e fabricar-lhes um verde seria exatamente o defeito
que esta missão foi construída para impedir, uma camada acima.

### O passo que faltava, e que o validador apanhou

A primeira volta da cadeia correu com os ficheiros **por rastrear**, e o mapa não os
viu: `scan_repo.py` mede do **índice do git**, não do disco. A segunda volta, já com
`git add`, contou 1516 ficheiros em vez de 1507 — e o validador **reprovou**, com
razão:

```
P9_CODIGO_DECLARADO: 5 ficheiro(s) de codigo que o mapa nao conhece
CODIGO NOVO SEM PECA NO MAPA E ARQUITETURA INVISIVEL.
```

Foi por isso que as duas peças acima foram declaradas. **O validador fez o trabalho
dele**, e isso fica registado aqui em vez de desaparecer atrás de um PASS final.

---

## N · O QUE CONTINUA DESCONHECIDO

1. **A sonda de rede nunca correu.** O degrau 1 da prova barata recusa-se a correr
   nesta árvore porque o executor canónico do SCRAP vive noutra linha. Não se sabe
   o que ela devolveria — e essa ignorância está escrita no código, não escondida.

2. **As 46 fontes de rota gratuita continuam observáveis sem decisão.** É
   deliberado (é a prova barata), mas nunca foi medido quanto volume uma dessas
   observações traz na prática.

3. **A suíte pode executar uma coleta real.** Não foi isolado qual teste o faz nem
   sob que condição — só que acontece, que muta ficheiros rastreados, e que faz
   seis testes alheios reprovarem na corrida seguinte.

4. **Quem escreve a primeira decisão, e com que autoridade.** O livro nasce vazio.
   A missão construiu a porta e a forma de olhar; **não** avaliou nenhuma fonte —
   avaliar 77 fontes é trabalho de gente, e fabricar 77 `SIM` para o censo ficar
   bonito seria exatamente o defeito que o portão existe para impedir.

5. **`NAO_SE_APLICA` nunca foi exercido sobre um par real.** Está no eixo, está
   testado, e nenhuma fonte real o recebeu ainda.

---

## O · VEREDITO

```
SR_01_SOURCE_RELEVANCE_GATE = PARTIAL
```

O portão existe, é canónico, está no caminho real antes do gasto, distingue as
quatro ausências, é contextual por propósito, não tem score, não mistura eixos,
sobreviveu a 27 ataques e a 20 mutantes, e não gastou um cêntimo.

```
PAID_REAL_RUNS = 0
REAL_COST      = 0
REDE_USADA_PELA_SONDA = 0
```

**E mesmo assim não é PASS**, porque o critério da missão é «nenhum bypass
relevante sobreviveu» — e sobreviveu um, que não se mede em adjetivos:

### O GAP, NOMEADO COM NÚMEROS

```
ENTRYPOINTS DE COLETA COM `__main__` QUE VÃO À REDE   40
DESTES, QUE TOCAM APIFY                               32
DESTES, QUE CONSULTAM O PORTÃO DE RELEVÂNCIA           0
WORKFLOWS QUE CORREM COLETA PAGA SEM O ORQUESTRADOR    4 de 5
```

O portão está no caminho **canónico** — `pedido → receitas.resolver →
orquestrador.correr` — e esse caminho está fechado, provado pela função, pela
linha de comando (`exit 3`) e por 27 ataques. Mas o caminho canónico **não é o
único caminho até ao dinheiro**.

`coleta/comunicacao_coleta.py` tem `__main__` próprio, importa `apify_pool` e
corre com `python3 coleta/comunicacao_coleta.py posts <plataforma>`. Dos cinco
workflows que alcançam rota paga, só `comunicacao-publica.yml` passa pelo
orquestrador; `scrap-social.yml` chama `coleta/social_scrap.py` e
`guarda/social_guarda.py` diretamente, e `sintonia-scrap.yml` chama sete scripts
pelo nome.

    UM PORTÃO NA PORTA DA FRENTE NÃO FECHA TRINTA E DUAS PORTAS DAS TRASEIRAS.

### Por que isto NÃO foi fechado nesta missão

1. **Não é um buraco que esta missão abriu, e fechá-lo não é trabalho de
   relevância.** Quem chama um coletor à mão salta também a admissão, a
   procedência, o `RUN-MANIFEST` e o ingresso — a arquitetura inteira, não só
   este portão. A COL-LAW-011 já proíbe o segundo orquestrador; o que falta é
   **enforcement**, e enforcement dos 32 entrypoints é uma missão própria.

2. **Pô-lo dentro de cada coletor seria copiar a lei 32 vezes**, que é o defeito
   que este ficheiro passa a página inteira a evitar. Uma lei em trinta e dois
   sítios diverge no terceiro commit.

3. **Fazê-lo às escondidas seria pior do que não o fazer.** A missão mandou
   nomear precisamente o que ainda permite gasto sem portão. Está nomeado, com
   contagem e com o comando que o reproduz:

   ```
   py provas/censo_de_relevancia_das_fontes.py     # o censo das fontes
   grep -l "apify" coleta/*.py | xargs grep -L "relevancia_da_fonte"
   ```

### O que É verdade, e continua a ser

```
NO CAMINHO CANONICO
  rota paga sobre fonte não avaliada        0   (eram 8)
  coleta recorrente sobre fonte não avaliada 0
  coleta total sobre fonte não avaliada      0

FORA DELE
  32 entrypoints que tocam Apify continuam a poder correr à mão
```

E o segundo gap, este por desenho: 46 fontes de rota gratuita continuam
observáveis à mão e pontualmente sem decisão de relevância, com o estado escrito
em cada recibo, e sem poderem escalar para coleta recorrente, total ou paga.

### Próximo passo mínimo — declarado, NÃO iniciado

Fazer os 32 entrypoints pagos passarem pelo orquestrador, ou dar-lhes um portão
comum no dono da chave (`apify_pool`), que é por onde **todos** eles têm de
passar para gastar. É o único sítio onde uma trava se escreve uma vez e vale para
os trinta e dois.
