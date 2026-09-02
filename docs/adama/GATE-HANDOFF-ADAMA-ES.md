# Gate do handoff ADAMA España — o que pode entrar, e o que não pode ainda

`2026-08-30` · rodada de **PORTÃO**. Nenhuma linha importada, nada aplicado no Supabase,
nenhuma migration nova, branch do handoff **não mesclada**.

**Veredito: `HANDOFF_PARTIAL`.**

---

## A · HEAD / branch / push

| | |
|---|---|
| Branch de trabalho | `claude/sintonia-eame-collection-es` |
| HEAD | `2e8e163` · árvore limpa · em dia com o remoto |
| Handoff auditado | `origin/claude/adama-es-local-browser` |
| HEAD do handoff | `0a799f5fae0e3146c3502dcd2002dc5bb2339a9c` (`0a799f5`) |
| Publicado | **sim** — o ref lido é `origin/...`, que só existe porque o remoto o publicou |
| Mesclado | **não**, e é assim que tem de continuar nesta rodada |
| Distância | 20 commits à frente da principal · 41 arquivos |

Havia dois candidatos. `claude/adama-es-commercial-intelligence-rqgy44` é a rodada
anterior (portfólio ROPF, 96 vigentes, fichas oficiais) e já tem seus artefatos na
principal. O handoff da coleta local é o `adama-es-local-browser`, e ele se identifica
sozinho: `docs/adama/ENTREGA-ADAMA-ES-PARA-ABA-PRINCIPAL.md`, com
`SAFE_FOR_MAIN_SESSION_TO_CONSUME = YES` e a data de observação ao vivo
`2026-08-30T03:19:24Z`.

## B · Onde está o handoff

`data/samples/ADAMA-ES-PRODUCT-INTELLIGENCE.json` (822 KB) é o artefato principal.
Ao redor dele: o censo em CSV, o manifesto dos 147 documentos com sha256, os 5 pares
confirmados no MAPA, os recortes por cultura, o vocabulário de ids do ROPF, a migration
do catálogo, o importador determinístico e 64 guardas próprios.

**Os 138 PDFs (296 MB) não estão no Git.** Estão no disco local do usuário. O manifesto
com hash está versionado; manifesto não é backup.

## C · O que ele contém

| estrutura | linhas |
|---|---|
| PRODUCTS | **56** |
| DOCUMENTS | 147 (138 baixados, 9 com link podre da própria ADAMA) |
| CROP_RELATIONS | 711 — **588 declaradas**, 123 apenas citadas |
| ISSUE_RELATIONS | 176 |
| **usos com cultura E alvo na mesma linha** | **5** |
| linhas CULTIVO × DOSE sem alvo | 26 |
| APPLICATION_WINDOWS | 3 |

## D · Quantos têm prova regulatória espanhola

**44 de 56.** Mas as duas bases não são a mesma coisa e o portão não deixa isso sumir:

| base do casamento | nº | o que sustenta |
|---|---|---|
| `REGISTRATION_NUMBER` | **41** | o número da ficha está no ROPF vigente, titular ADAMA |
| `NAME_AND_COMPOSITION` | **3** | nome comercial idêntico + composição compatível |

Os três de nome+composição são CUPROXI FLO, KLARTAN EW e NICOPERTS. É casamento por
nome, e nome não é chave. Eles entram como `LOCAL_REGISTERED`, mas carregando
`MATCH_BASIS` para que ninguém trate os 44 como um bloco homogêneo.

## E · Quantos dependem só do site da ADAMA

**12.** BASTOS · COLTRANE · FADEUS · GARMIL · KAMPAI · KONA · MAVITA 250 EC · MIRADOR ·
ORISOS · ROMIN · TRICUPROXI F · TRINITY PACK.

Estado: `LOCAL_PRESENT_BUT_REGISTRATION_NOT_PROVED`. **Não** `NÃO REGISTRADO`. Eles podem
ter registro cancelado, registro de outro titular, ou grafia que o crosswalk não alcançou.
Ausência no ROPF vigente é `AUSENTE_MEDIDO`, não ausência de registro.

E aqui o schema já trabalha sozinho: `registro_regulatorio.titular` é `NOT NULL` e o site
não publica titular. **Os 12 não conseguem entrar como registro nem se alguém tentar.**
A lei `ADAMA WEBSITE ≠ PROVA REGULATÓRIA` está aplicada por constraint, não por
recomendação.

## F · Quantos estão NOT_KNOWN

**Zero — e isso precisa de explicação, não de comemoração.** Os 56 foram observados ao
vivo no catálogo espanhol, então *presença local* nunca é desconhecida. O que varia é a
prova de registro, e para isso existem os outros dois estados. `NOT_KNOWN` passaria a ser
diferente de zero se um produto entrasse por uma lista de terceiro em vez de observação
própria.

## G · Cobertura por campo do contrato

| campo | cobertura | estado |
|---|---|---|
| COUNTRY · PRODUCT · SOURCE_URL · SOURCE_TYPE · SOURCE_DATE | 56/56 | completo |
| ACTIVE_INGREDIENT | 52/56 | 4 fichas não publicam composição — `AUSENTE_MEDIDO` |
| FORMULATION | 55/56 | |
| CROP | 588 declaradas de 711 | completo **com a distinção declarado/citado** |
| **TARGET / ISSUE** | 176/176 | **contaminado** — ver RT-11 |
| AUTHORIZED_USE | 5 | mínimo: só 5 linhas têm cultura e alvo juntos |
| HOLDER | 0/56 | ausente no handoff; derivável do ROPF |
| REGISTRATION_STATUS | 43/56 | derivável; o handoff traz estado de **catálogo**, não de registro |
| EXPIRY | 43/56 | derivável do ROPF pelo número |
| AUTHORIZATION_DATE | 0/56 | não coletado, nem lá nem cá |
| PHI | 0/5 | o HTML não publica; mora no rótulo em PDF |
| APPLICATION_TIMING_LITERAL | 5/5 | toda linha carrega o texto literal da tabela |
| DOSE · EVIDENCE_LOCATOR | 31/31 | completo, com âncora de seção/tabela/linha |
| **TEMPORAL_RESOLUTION** | 0/31 | **não existe como campo** — ver C-3 |
| LIMITATION / NOT_KNOWN | 56/56 | ausência é escrita, nunca omitida |

## H · Conflitos com o schema atual

| id | gravidade | o quê | resolução |
|---|---|---|---|
| **C-1** | mecânico | duas migrations `010` | renumerar a do catálogo para `013`. As 15 tabelas se chamam `catalogo_*` e **nenhuma** colide com as quatro do calendário — o choque é de número de arquivo |
| **C-2** | nenhuma ação | o catálogo tem janela própria | e deve ter: o que o *fabricante publica* ≠ o que o *rótulo autoriza*. `registro_uso_janela` continua filho de `registro_uso` e único dono do relógio C |
| **C-3** | **bloqueia** | o handoff não tem `temporal_resolution` | a decisão PHENOLOGY_STAGE / APPROXIMATE / NOT_KNOWN é do importador e precisa ser regra escrita, auditável contra `ANCHOR.ROW_TEXT` |
| **C-4** | **bloqueia** | `BBCH 00-00` passa pelo schema e vira `CLOSED` | consertar na origem ou importar como APPROXIMATE |
| **C-5** | atenção | `titular` é NOT NULL e o handoff não tem | vem do ROPF, e precisa ser declarado como propriedade da **consulta** (export filtrado por titular ADAMA), não do registro |
| **C-7** | **bloqueia** | duas capturas do mesmo registro viram dois registros | o importador casa por `(pais, registration_id)` e a view devolve a captura mais recente. **Não é defeito do handoff — é do nosso lado** |
| **C-6** | atenção | importar só o relógio C não acende nenhuma janela | 5 de 5 casos do ensaio respondem `NOT_KNOWN`, porque janela em BBCH só se avalia contra fenologia observada e hoje só o olivar tem série |

`bbch_em_ordem` **não** pega o C-4, e não deve: uma janela de um estádio só (BBCH 65-65)
é legítima. O conserto é na origem, não no banco.

### C-7 — o conflito que o handoff não causou, só revelou

Carregando a camada ADAMA **por cima** do acervo ES que já existe:

| medida | valor |
|---|---|
| linhas em `registro_regulatorio` | 8 |
| registros distintos por `(pais, registration_id)` | **7** |
| duplicados | **1** (ES-00211, o NEPTUNE) |
| janelas do NEPTUNE na view | **3** |

A chave natural é `UNIQUE (pais, registration_id, fonte_versao)`. `registro_regulatorio` é
um **log versionado por captura** — e isso é de propósito, guarda o histórico do que o
registro dizia em cada leitura. Mas `v_product_registered_windows` lê esse log **como se
fosse estado corrente**. Com uma captura só, o defeito era invisível. O handoff da ADAMA é
a segunda leitura do ROPF no mesmo dia (01:01 e 05:01), e ele o revela.

O portal veria o mesmo NEPTUNE três vezes no mesmo caso, com estados de janela diferentes
e nenhuma indicação de que são a mesma autorização vista duas vezes.

**A lei nova que este ensaio nomeia: `CAPTURE != REGISTRATION`.** Duas leituras do ROPF no
mesmo dia são um registro, não dois.

Não consertado nesta rodada, de propósito: é rodada de portão, e mexer no motor enquanto
se testa o handoff contra ele invalidaria o teste. O conserto é na camada de **consulta**,
não no dado — a view devolve a captura mais recente por `(pais, registration_id)` e expõe
quantas existem. Mudar a chave da tabela jogaria fora o histórico.

## I · Os cinco casos contra o motor

Banco descartável com 001–012, `supabase/ensaios/ADAMA-ES-ENSAIO-CINCO-CASOS.sql`,
`as_of 2026-08-30`. **Nenhuma linha no banco canônico.**

| caso | o que exerce | produto | estado | escopo | some ao perguntar por alvo? |
|---|---|---|---|---|---|
| **A** | cultura + alvo + janela explícita | POSTSCRIPT 80 · arroz | NOT_KNOWN | ISSUE_LEVEL | não |
| **B** | nível cultura, sem alvo | ORDAGO CAPS · amendoeira | NOT_KNOWN | **CROP_LEVEL** | **não** |
| **C** | validade vencida | NEPTUNE · olivo | NOT_KNOWN | ISSUE_LEVEL | não |
| **D** | temporalidade aproximada | TRINITY · cevada | NOT_KNOWN | ISSUE_LEVEL | não |
| **E** | dado ausente | TRINITY · centeio | NOT_KNOWN | ISSUE_LEVEL | não |

**O schema representa os cinco sem perda e sem inferir nada.** O texto literal da fonte
viaja em todos. O caso C mostra `registration_state = "Vigente"` (a palavra do MAPA) ao
lado de `registration_expiry_state = EXPIRY_DATE_PASSED` — a data vencida é dita, a
retirada não é inferida.

Os cinco respondem `NOT_KNOWN` e isso é a resposta **certa**: nenhuma dessas culturas tem
fenologia observada. É o conflito C-6, medido.

### O dano do `BBCH 00-00`, demonstrado

Com cevada observada em BBCH 05, na mesma consulta:

| janela | estado |
|---|---|
| como a fonte diz — `desde BBCH 00 hasta BBCH 07` | **ACTIVE** |
| como o handoff entrega — `BBCH_FROM=00 BBCH_TO=00` | **CLOSED** |

Importar verbatim transformaria uma janela de pré-emergência aberta em fechada. É
exatamente o `UNKNOWN → CLOSED` que o contrato inteiro existe para impedir, chegando
por outra porta: uma faixa numérica errada.

## J · Red team — 11 hipóteses, 8 derrubadas, 3 defeitos

| id | hipótese | resultado |
|---|---|---|
| RT-1 | o site foi tratado como prova regulatória | **derrubada** — 5 de 918 linhas são `REGULATORY_FACT`, e as 5 têm id de cultivo, id de plaga, titular e estado do MAPA |
| RT-2 | produto de outro país vazou para ES | **derrubada** — as 56 URLs estão em `adama.com/spain/es/` |
| RT-3 | ausência virou "não existe" | **derrubada** |
| RT-4 | alvo ausente fez produto de nível cultura sumir | **derrubada** — as 26 linhas ficam, com `PAIR_DERIVABLE=false` e o motivo escrito |
| RT-5 | validade vencida virou retirada | **derrubada** |
| **RT-6** | aproximado virou faixa numérica exata | **DEFEITO** — 2 de 3 janelas com `BBCH 00-00` |
| RT-7 | desconhecido virou fechado | **derrubada** — o artefato não guarda estado de janela nenhum |
| RT-8 | frescor foi persistido | **derrubada** — nem nome de campo nem valor |
| RT-9 | o catálogo virou segundo dono da janela | **derrubada** — 15 tabelas `catalogo_*`, janela própria, não escreve em `registro_uso_janela` |
| **RT-10** | a mesma evidência em dois lugares com semântica diferente | **DEFEITO** — CUPROXI FLO é `19232` em `PRODUCTS` e `ES-00979` em `REGULATORY_CROSSWALK`, sob o mesmo nome de campo |
| **RT-11** | a distinção DECLARADO ≠ CITADO foi aplicada a alvo | **DEFEITO** — não foi |

Uma nota sobre RT-3: a primeira versão dele acusou o handoff de dizer "não existe", e o
acerto era a frase `"falha de download NÃO é documento inexistente"` — o campo que
**enuncia** a proibição. É a quarta vez neste projeto que uma lista de termos proibidos
dispara na própria proibição. A busca agora percorre campo a campo e ignora os campos cujo
**nome** os marca como regra ou motivo. RT-5, RT-7 e RT-8 tinham o mesmo defeito latente e
foram corrigidos juntos; o RT-8 só ganhou dentes de verdade quando passou a procurar
também no **nome** do campo, que é onde um frescor gravado apareceria.

### RT-11, o achado que mais importa

`ISSUE_RELATIONS` **não tem o campo `DECLARATION_SOURCE`** que `CROP_RELATIONS` tem. A
distinção que o próprio handoff chama de "a que mais importa" foi aplicada a cultivo e
não a alvo.

O resultado é medível: **25 produtos que não são herbicida carregam o alvo
`MALAS HIERBAS`** — um por produto não-herbicida, incluindo o NEPTUNE, o CUPROXI FLO e o
BREVIS (regulador de crescimento). O inverso nunca acontece: nenhum herbicida ganhou um
alvo de doença. Essa assimetria é a assinatura de **menu do site**, não de conteúdo de
ficha — o mesmo defeito nº 2 que o handoff já corrigiu para categoria, sobrevivendo em
outra estrutura.

Importado, isso afirmaria que um fungicida cúprico controla ervas daninhas, e a
`v_product_line_semantics` o classificaria como `WEED_CONTROL`.

### O red team foi testado por mutação

Dez mutações, cada uma quebrando uma coisa numa cópia em memória. **Todas pegaram.**

| mutação | hipótese que reprovou |
|---|---|
| o site vira prova regulatória | RT-1 |
| uma página passa a ser francesa | RT-2 |
| um estado passa a dizer `NAO_REGISTRADO` | RT-3 |
| linha sem alvo declara par derivável | RT-4 |
| um estado passa a dizer `RETIRADO DO MERCADO` | RT-5 |
| a janela ganha um `CLOSED` gravado | RT-7 |
| o produto ganha `AGE_DAYS` persistido | RT-8 |
| o catálogo passa a escrever em `registro_uso_janela` | RT-9 |
| os dois números de registro divergem sempre | RT-10 |
| consertar `BBCH 00-00` para `00-07` | RT-6 volta a passar |
| remover as 25 ervas dos não-herbicidas | RT-11 volta a passar |

## K · ES-CASE-001 — **ABERTA**

| | |
|---|---|
| janelas do NEPTUNE no handoff | **0** |
| pares olivo × repilo do NEPTUNE | **0** |
| citações da palavra "floração" | 9 |
| citações que **servem** como evidência | **0** |

As 9 estão todas em `AMBIGUOUS_TERMS` e são rótulos oficiais de **uso** — *"Inhibición
floración"*, *"Aclareo floración"*. Nenhuma tem data, nenhuma fala de olival, nenhuma
está ligada ao NEPTUNE.

O handoff **não** traz o que fecharia a divergência. Ela continua `ABERTA`:
humano `CLOSED`, motor `NOT_KNOWN`.

**O que fecharia:** a data ou o estádio BBCH de floração do olival numa fonte datada,
guardada como `OBSERVED_CAMPAIGN`. O candidato mais provável está localizado e tem hash:
`L30037I_06_NEPTUNE_COMPLETA (SPECIMEN).pdf`, 657.461 bytes,
sha256 `d04e306e13ddd5ad71b72c5dc2a608971b2af7dd5257c422fd4f7a6e88cc2d63` — baixado, no
disco do usuário, **fora do Git**.

### Este portão quase fechou a divergência sozinho

A primeira versão da verificação procurava a palavra "floración" no artefato, achava 18
ocorrências e devolvia `RESOLVE = true`, `ESTADO = FECHADA`. Todas as 18 eram vocabulário
não resolvido.

A regra agora exige as três coisas juntas — falar de olival, carregar data ou BBCH, e não
estar em `AMBIGUOUS_TERMS` — e o padrão é `ABERTA` até prova em contrário. Fica registrado
porque foi a missão que proibiu resolver por conveniência, e a primeira tentativa
resolveu.

## L · Veredito — `HANDOFF_PARTIAL`

A coleta é sólida e a proveniência é exemplar: quatro níveis de verdade linha a linha,
âncora de tabela em toda relação, ausência sempre escrita, e 8 das 11 hipóteses do red
team caíram. Mas três defeitos ficam no dado de origem e três conflitos bloqueiam
estruturas específicas.

O mais caro deles, o **C-7, não é defeito do handoff** — é do nosso próprio lado, e só
apareceu porque o handoff é a segunda captura do mesmo registro. Sem esta rodada de
portão, ele teria aparecido na tela do cliente.

### Pode entrar agora

| estrutura | destino |
|---|---|
| PRODUCTS (56) | `catalogo_produto` |
| CROP_RELATIONS declaradas (588) | `catalogo_produto_cultivo` |
| DOCUMENTS (147) | `catalogo_produto_documento`, com `raw_asset_id` NULL até o byte estar preservado |
| CROP_ISSUE_RELATIONS (5) | `registro_uso` + `registro_uso_janela`, com a ressalva C-4 na do TRINITY |
| REGULATORY_CROSSWALK (108) | `catalogo_registro_crosswalk` |

### Não pode entrar ainda

| estrutura | bloqueio | o que destrava |
|---|---|---|
| qualquer registro que já exista no acervo | C-7 | importador casando por `(pais, registration_id)` e view devolvendo a captura mais recente |
| ISSUE_RELATIONS (176) | RT-11 | reprocessar com a mesma regra de `CROP_RELATIONS` e marcar cada linha DECLARADO ou CITADO |
| APPLICATION_WINDOWS (2 de 3) | RT-6 · C-4 | corrigir `BBCH_TO` na origem, ou importar como APPROXIMATE com o texto inteiro |
| `REGISTRATION_ID` de PRODUCTS | RT-10 | renomear no artefato: `..._PUBLICADO_NO_SITE` e `..._NO_ROPF`. Importar sempre o segundo |

## M · Procedimento de importação — escrito, **não executado**

1. Renumerar `010_catalogo_publico_fabricante.sql` para `013`. Não tocar no conteúdo.
2. Aplicar a `013` pelo workflow `supabase-migrate`, com a `008` por último e estendida
   para conferir as 15 tabelas `catalogo_*`.
3. **Preservar os 138 PDFs primeiro** (`scripts/storage_preservar.py --enviar`). Só depois
   de `VERIFIED` um documento pode apontar `raw_asset_id`.
4. Aplicar `supabase/importacoes/ADAMA-ES-CATALOGO-2026-08-30.sql` (idempotente) para as
   estruturas liberadas.
5. Relógio C: importar as 5 `CROP_ISSUE_RELATIONS` casando **sempre pelo número do ROPF**,
   nunca por nome comercial. Regra de resolução temporal escrita e auditável contra
   `ANCHOR.ROW_TEXT`: `PHENOLOGY_STAGE` só quando os dois BBCH aparecem no texto ancorado;
   caso contrário `APPROXIMATE` com a frase inteira.
6. `titular` vem do ROPF, declarado como propriedade da consulta.
7. `fecha_caducidad` vem do ROPF pelo número. `EXPIRY ≠ WITHDRAWAL` continua valendo.
8. **Antes de qualquer coisa do relógio C: resolver C-7.** Enquanto a view devolver todas
   as capturas, importar registro que já existe duplica produto na tela.
9. Rodar `supabase/tests/regressoes_calendario.sql` e o ensaio contra o banco carregado.
   Nenhuma das 45 afirmações pode cair — hoje, com as duas camadas juntas, a nº 12 cai.
10. Só então ISSUE_RELATIONS e APPLICATION_WINDOWS, depois de RT-11 e RT-6 resolvidos
    **na origem**.

## N · Testes e mutações

| prova | resultado |
|---|---|
| `tests/test_adama_es_gate.py` | **35 testes**, OK |
| suíte completa | **494 testes**, OK |
| mutações do red team | **10 de 10 pegaram** |
| ensaio dos cinco casos, Postgres 16 descartável | 5 de 5 representados sem perda |
| dano do `BBCH 00-00`, medido | `ACTIVE` vira `CLOSED` |
| `regressoes_calendario.sql`, banco só com a fixture ES | 45/45 |
| `regressoes_calendario.sql`, com as duas camadas juntas | **para no nº 12** — e a parada é o achado C-7 |
| artefato do portão reproduzível | mesmo md5 em execuções repetidas |

O workflow `adama-es-gate` roda tudo isso num Postgres descartável, sem segredo, e
**falha** se uma mutação deixar de pegar ou se o artefato versionado divergir da medição.

## O que esta rodada não fez

Não importou nenhuma linha no banco canônico · não aplicou nada no Supabase · não criou
migration nova · não mesclou a branch do handoff · não resolveu ES-CASE-001 · não leu os
138 PDFs · não abriu França nem Itália · não fez coleta.
