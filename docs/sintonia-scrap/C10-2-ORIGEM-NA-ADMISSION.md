# C10.2 · O QUE «ORIGEM» SIGNIFICA NA ADMISSION

```
MEDIDO_EM         = 2026-09-11
C10_2_ORIGIN_GATE = PASS
CONTRACT_DECISION = B · ORIGIN_ACCEPTS_TRACEABLE_URL
```

> Evidência de missão. Não é Bíblia, não é MASTER, não substitui contrato.

---

## A · A PERGUNTA, E COMO ELA FOI RESPONDIDA

A C10.1 deixou em aberto: `_tem_origem()` aceita `source_id or fonte or url`.
Isso é violação da lei `SOURCE_ID != SOURCE_URL`, ou o portão nunca foi de
identidade?

**Não foi escolhido por preferência.** Três leituras independentes do contrato
dizem o mesmo, e a terceira fecha o assunto.

1. **O motivo que o próprio portão escreve quando falha:** *«um item sem origem
   não se consegue **conferir depois**»*. Conferibilidade é procedência.
2. **A companhia em que ele vive.** `perguntas_do_estagio` chama ao conjunto
   *«Prontidão DOCUMENTAL: dá para ler, sabe de onde veio, sabe de que original
   nasceu»* — três perguntas de prontidão, nenhuma de identidade.
3. **A prova que decide:** `pronto_para_inteligencia` monta o `SOURCE_ID` de
   saída a partir de `source_id` **ou** `fonte` — e **deixa `url` de fora**.

O terceiro ponto é o que não admite duas leituras:

```
SE O PORTÃO FOSSE DE IDENTIDADE, A SAÍDA PARTILHARIA A CADEIA DELE.
NÃO PARTILHA. LOGO NÃO É.
```

```
ORIGIN_GATE   = PROCEDÊNCIA CONFERÍVEL
IDENTITY_GATE = outra pergunta, e vive noutro sítio
```

E há um quarto sinal, mais fraco mas na mesma direção: `admissao/admissao.py` é
**byte a byte idêntico** na linha madura de identidade (`71de3214`, medido —
mudou desde a referência `d43126e3`). Quem endureceu identidade olhou para esta
porta e deixou-a como estava.

---

## B · O QUE ESTAVA ERRADO — QUATRO DEFEITOS, NENHUM DELES O FALLBACK

O fallback para URL é legítimo sob o contrato B. O que estava errado era outra
coisa, e a matriz executada mostrou-o.

### D1 · uma confissão passava por origem

```
source_id = "NAO SEI"  →  SIM, com evidência «NAO SEI»
```

`item.get("source_id") or …` mede se o valor é *truthy*, não se ele responde. E
`"NAO SEI"` é truthy.

### D2 · e o pior caso não precisava de endereço nenhum

```
source_id = "NAO SEI",  SEM url  →  SIM
```

Um item sem endereço nenhum dizia que a origem estava declarada. **Não havia
nada para conferir depois** — que é exatamente o que esta pergunta existe para
garantir. O portão contradizia o motivo que ele próprio escreve.

```
UMA CONFISSÃO NÃO É UMA ORIGEM.
«Não sei de onde veio» é a resposta NAO_SEI a esta pergunta, não o valor dela.
```

### D3 · a confissão ofuscava o endereço que respondia

No caso 5 havia uma URL perfeitamente boa. O `or` parava na confissão e a URL
nunca chegava ao livro de decisões. O defeito não só deixava passar o que não
devia: **apagava a única prova que existia**.

### D4 · o portão media a grafia, não a origem

`coleta/ingresso.DO_COLETOR` declara `SOURCE_ID` e `SOURCE_URL` em
**maiúsculas**. O portão lia só minúsculas.

```
{'SOURCE_ID': 'IG-0042'}   →  NAO_SEI
{'source_id': 'IG-0042'}   →  SIM
```

Um item que declarava a origem **pela grafia do contrato da casa** levava
`NAO_SEI`. Isso é falso negativo, e a regra 3 do próprio módulo condena-o:
*«empurrar o NAO_SEI para o NÃO faz a coleta encolher sozinha, sem ninguém ter
decidido isso»*.

### E um quinto, medido e NÃO corrigido

`_tem_pai` guarda contra `"NAO_SEI"` (com sublinhado) e **não** contra
`"NAO SEI"` (com espaço) — que é justamente a grafia que `leis/artefato.py`
escreve. Mesmo defeito de família, portão vizinho.

```
parent_artifact_id = "NAO_SEI"  →  NAO_SEI   (apanhado)
parent_artifact_id = "NAO SEI"  →  SIM       (passa)
```

**Fica registado e não foi tocado.** A missão perguntou pelo portão de origem, e
mudar o resultado de um portão que ela não mediu alteraria decisões de caminhos
que ninguém conferiu. E que `_tem_pai` já tente guardar é a melhor prova de que
a omissão em `_tem_origem` era descuido, não desenho.

---

## C · A MATRIZ, ANTES E DEPOIS

Executada sobre a função real, não sobre o texto dela.

| caso | antes | depois |
|---|---|---|
| `source_id` provado + url | SIM · «IG-0042» | SIM · **SOURCE_ID** |
| `source_id` provado sem url | SIM | SIM · **SOURCE_ID** |
| sem `source_id` + url | SIM · «…/reel/…» | SIM · **SOURCE_URL** |
| sem nada | NAO_SEI | NAO_SEI |
| **`source_id` = NAO SEI + url** | **SIM · «NAO SEI»** | **SIM · SOURCE_URL, com o URL** |
| **`source_id` = NAO SEI, sem url** | **SIM · «NAO SEI»** | **NAO_SEI** |
| `fonte` = identidade | SIM | SIM · **SOURCE_ID** |
| `post_id` só | NAO_SEI | NAO_SEI |
| `storage_path` só | NAO_SEI | NAO_SEI |
| **`SOURCE_ID` maiúsculo** | **NAO_SEI** | **SIM · SOURCE_ID** |
| **`SOURCE_URL` maiúsculo** | **NAO_SEI** | **SIM · SOURCE_URL** |
| `UNKNOWN` + `SOURCE_URL` | SIM · «UNKNOWN» | SIM · **SOURCE_URL** |

### O que a mudança acrescenta ao livro de decisões

A evidência passa a dizer **de que espécie** foi a origem, e **por que campo**
ela veio:

```
{"origem": "IG-0042",   "origem_especie": "SOURCE_ID",  "origem_campo": "source_id"}
{"origem": "https://…", "origem_especie": "SOURCE_URL", "origem_campo": "url"}
```

Antes dizia só `origem`, e a leitura natural de «origem» é identidade. Quem
lesse o livro não conseguia distinguir as duas.

E o motivo escrito no caso do endereço di-lo em claro: *«a fonte canônica
continua por identificar, e isto NÃO é `IDENTITY_STATE`»*.

---

## D · O CASO REAL DO REEL DA C10.1

`SOURCE_ID = NAO SEI`, `SOURCE_URL` válida. O que o fluxo real faz:

| variante | origem, antes | origem, depois |
|---|---|---|
| o Reel como a C10.1 o entrega | SIM · «NAO SEI» | SIM · **o URL**, marcado `SOURCE_URL` |
| o mesmo, **sem URL nenhuma** | **SIM · «NAO SEI»** | **NAO_SEI** |
| com `SOURCE_ID` canônico, um dia | SIM | SIM · `SOURCE_ID` |

Nos três casos a decisão final ficou `NAO_SEI` — mas **pela pergunta temática**,
não pela origem. Os dois estados são diferentes e agora distinguem-se:

```
ORIGIN_GATE_PASSED  !=  ADMISSION_PASSED  !=  READY
```

E atravessar a origem pelo endereço **não** torna a identidade provada: a trava
da Collection continua a devolver `IDENTITY_STATE = None` para o mesmo item. Há
teste para isso.

---

## E · O QUE A SOLUÇÃO NÃO FAZ

Nenhum caminho, direto ou indireto, escreve `source_id = url`. O portão apenas
**lê**; `pronto_para_inteligencia` continua a montar o `SOURCE_ID` de saída sem
`url`, e há um teste que reprova se isso mudar. `POST_ID`, `SHA256` e
`storage_path` continuam a não ser origem.

### Um limite medido, e declarado

Se um produtor puser um URL **dentro** de `source_id`, o portão reporta
`ESPECIE = SOURCE_ID` — porque o campo é de identidade. Ele reporta o campo com
fidelidade; não adivinha o valor.

Cheirar o valor à procura de forma de URL seria heurística, e rejeitaria um id
legítimo que por acaso pareça um URI. **O sítio certo para impedir isso é o
produtor** — e foi exatamente o que a C10.1 fechou no único produtor que o
fazia.

---

## F · UM DONO PARA O VOCABULÁRIO

As seis confissões — `NAO SEI`, `NAO_SEI`, `NÃO SEI`, `NAO_SE_APLICA`,
`UNKNOWN`, `NOT_KNOWN` — têm dono: `guarda/preservar_coleta`, que as descreve
como *«contadas no repositório, não inventadas aqui»*.

A porta **importa** `_identifica` em vez de copiar a lista. Copiar criaria um
segundo dono da mesma pergunta, e dois donos divergem no dia em que aparecer a
sétima palavra. Medido: o import custa 13 ms, só `stdlib` no topo do módulo,
nenhuma ligação a base de dados, nenhum ciclo. Há teste que reprova se uma
segunda cópia nascer.

---

## G · RED TEAM — seis mutações, seis quedas

| # | mutação | resultado |
|---|---|---|
| 1 | volta a cadeia `source_id or fonte or url` | **FAILED** (9 testes) |
| 2 | *truthiness* em vez do dono do vocabulário | **FAILED** (6) |
| 3 | endereço antes de identidade | **FAILED** (7) |
| 4 | `source_id` entra na lista de endereço | **FAILED** (1) |
| 5 | `url` entra no `SOURCE_ID` de saída | **FAILED** (1) |
| 6 | a espécie deixa de ser escrita | **ERRORS** (4) |

A quinta é a que guarda a lei da §9, e está no sítio certo: na fronteira de
saída, que é por onde a identidade sairia.

---

## H · REGRESSÃO

| momento | testes | falhas |
|---|---:|---:|
| baseline, com a porta como estava | 541 | 0 |
| depois, com os 18 novos | 559 | 0 |

Conjunto mais largo — C5 a C8, voz, política e coleta externa — 282 testes, `OK`.
O grupo que inclui `test_fundacao_da_coleta` traz a falha de sempre,
`test_o_portal_nao_ganhou_implementacao`, entulho anterior já contado na C9, na
C10 e na C10.1.

```
NEW_FAILURES     = 0
SYSTEM_MAP_CHECK = PASS
```

O mapa foi regenerado mecanicamente porque o comportamento real do portão
mudou. Precisou de duas passagens, como já é conhecido.

---

## I · O QUE NÃO MUDOU

Instagram audio-only, `yt-dlp`, ASR, GPU, Facebook, LinkedIn, YouTube, X,
portal, classificador temático, Collection LIVE, Supabase. E a capacidade
**continua sem atravessar o portão canônico de rotas**.

A evidência do livro de decisões só **ganhou** chaves; nenhum consumidor fora da
própria porta lê `origem` — medido.

---

## J · RISCO RESTANTE

1. **`_tem_pai` não apanha `"NAO SEI"` com espaço.** Medido, registado, não
   corrigido — fora do escopo desta missão.
2. **`_tem_quando` não guarda sentinela nenhum.** Mesma família, mesmo limite.
3. **Um URL escondido dentro de `source_id`** é reportado como identidade. O
   sítio de impedir isso é o produtor, e a C10.1 fechou o único que o fazia.
4. **Nada garante que um endereço que passou hoje ainda resolva amanhã.** O
   portão pergunta se há endereço, não se ele responde — e as sentinelas de
   Instagram da C10 mostraram que isso muda dentro do mesmo dia.

---

## K · VEREDITO

```
C10_2_ORIGIN_GATE = PASS
CONTRACT_DECISION = B · ORIGIN_ACCEPTS_TRACEABLE_URL
NEW_FAILURES      = 0
SYSTEM_MAP_CHECK  = PASS
KNOW_HOW_DELTA    = NENHUM
BÍBLIA/CONTRATO   = NÃO precisa mudar

PRÓXIMO PASSO MÍNIMO = ligar a capacidade Instagram audio-only
                       ao portão canônico de rotas

HARD STOP.
```

`KNOW_HOW_DELTA = NENHUM` com motivo: a §16 mandava atualizar **se** identidade
e procedência estivessem colapsadas em um gate só. **Não estavam** — a fronteira
de saída já as separava, e foi isso que provou o contrato. O que houve foi um
portão de procedência a aceitar confissões e a ler uma grafia só. Isso é defeito
de implementação de lei existente, não aprendizado novo.
