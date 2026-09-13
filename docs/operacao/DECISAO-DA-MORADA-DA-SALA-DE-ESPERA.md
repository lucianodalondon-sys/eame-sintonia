# A MORADA DA SALA DE ESPERA — DECISÃO MEDIDA

```
MISSAO            C-GREADY-02
MEDIDO_EM         2026-09-13
LINHA_FUNCIONAL   claude/raw-observation-identity-3jbwco @ 247fbf25
TRABALHO          claude/funny-hypatia-y7ho5s
BANCO             PostgreSQL 16.13 descartavel · 127.0.0.1:5433/descartavel
LIVE_READS        0
LIVE_WRITES       0
```

---

## ⚠️ ANTES DE TUDO: A PERGUNTA DESTA MISSÃO JÁ TINHA RESPOSTA

A missão pede para **decidir** onde vive a Sala de Espera. Medido na linha
funcional, a decisão **já existe, é de gente, e está implementada**:

```
docs/decisoes/ADR-SALA-DE-ESPERA-V1.md
  Data      2026-09-12   (um dia antes desta missão)
  Estado    IMPLEMENTADO
  Missão    C-CLOSE-READY-WITH-CANONICAL-WAITING-ROOM-V1
  Decidido por: gente
```

Por isso esta missão **não escolhe**. Ela **audita**, de fora, com bancada
própria, e diz se a escolha aguenta. Escrever aqui um segundo veredito de
arquitetura criaria dois donos para a mesma decisão — que é exatamente o pecado
que a decisão auditada evita.

```
UMA DECISAO JA TOMADA NAO SE RE-TOMA EM SILENCIO.
AUDITA-SE, E DIZ-SE SE AGUENTA.
```

---

## P · VEREDITO

```
FILE_WAITING_ROOM_WINS
```

E com uma qualificação que importa mais do que o veredito:

```
ESTE VEREDITO CONFIRMA O ADR-SALA-DE-ESPERA-V1. NAO O SUBSTITUI.
O DONO DA DECISAO CONTINUA A SER O ADR.
```

A OPÇÃO B **não perdeu por ser inferior**. Ela passou a bateria inteira contra
PostgreSQL real. Perdeu por três razões medidas, e a terceira é decisiva:

1. **Não compra a integridade que se compra um banco para ter.** A chave
   estrangeira para o RAW é impossível com os 11 campos da `COL-LAW-043`:
   `ITEM_ID` é `decisao.item` — texto natural — e não `raw_asset.id`. Para ter
   FK é preciso um **12.º campo**, e é esse campo que a lei proíbe.
2. **Não é mais segura por omissão.** Escrita do modo natural
   (`on conflict do nothing`), a OPÇÃO B **engoliu em silêncio** uma corrida com
   história divergente. A OPÇÃO A levanta `ConflitoDeCorrida` e nomeia o
   ficheiro. Medido, e não suposto.
3. **A OPÇÃO A já está construída e a OPÇÃO B seria uma SEGUNDA morada.** É o
   risco central que a própria missão nomeia.

---

## A · GIT MEDIDO

| | |
|---|---|
| linha funcional | `claude/raw-observation-identity-3jbwco` @ `247fbf25` |
| ramo de trabalho | `claude/funny-hypatia-y7ho5s` |
| refs remotas | 209 |
| migrations na árvore | 30 |

### `tmp/know-how-ready-address-20260913` — §2 da missão

⚠️ **A minha primeira medição estava errada, e a correção muda a razão, não o
resultado.** Eu tinha registado «0 commits únicos» sem dizer contra o quê.
Medido corretamente, contra três bases diferentes:

| base | commits únicos do `tmp/` |
|---|---|
| `origin/main` | **271** |
| `origin/claude/raw-observation-identity-3jbwco` | **127** |
| `origin/claude/sintonia-eame-know-how-v1` | **0** |

O tip `39e685fc` **está contido** em `origin/claude/sintonia-eame-know-how-v1`,
que está 1 commit à frente. O trabalho não se perde.

```
UNIQUE_COMMITS = 0   (contra a linha que carrega o trabalho)
APAGAR         = SEGURO
APAGADO        = NAO — HTTP 403
```

As credenciais desta sessão **não permitem apagar ramos**. Fica para quem tenha
permissão. Não é bloqueio da arquitetura, como a missão já previa.

```
UM NUMERO SEM A BASE CONTRA A QUAL FOI MEDIDO NAO E UM NUMERO.
```

---

## B · `G-READY-01` — READY NÃO É PRODUZIDO POR NENHUMA ROTA

```
ESTADO = FECHADO
```

Fechou em `C-CLOSE-READY-WITH-CANONICAL-WAITING-ROOM-V1`. Provado agora, por
mim, com travessia real:

```
RAW -> DERIVED -> STRUCTURED -> ADMISSION -> READY    (a MESMA corrida)
```

`provas/a_unidade_pousa_na_espera.py` · caso `E7` · **PASS**

E o achado histórico que a casa deixou escrito, e que vale repetir:

> enquanto `G-READY-01` esteve aberto ficou CRITICAL/BLOCKER **apesar** de
> existir um CLI que produzia READY à mão. **UM CLI NÃO É UMA ROTA** — e só
> fechou quando uma ROTA produziu READY.

---

## C · `G-READY-02` — A SALA DE ESPERA NÃO TEM ARMAZENAMENTO

```
ESTADO = FECHADO, E FECHADO POR «TEM MORADA», NAO POR «TEM ARMAZEM»
```

A distinção é do próprio texto que se recusou a fechá-lo antes, e continua
verdadeira. A sala tem morada, dono, escrita atómica e travas. Não tem tabela.

### ⚠️ Uma contradição aparente, e ela não é contradição

Duas medições coexistem no mesmo commit e parecem discordar:

| ficheiro | diz |
|---|---|
| `provas/a_sala_de_espera_nao_tem_morada.py` | a sala **não** tem morada |
| `admissao/sala_de_espera.py` | a morada **é** `data/samples/PRONTO-PARA-INTELIGENCIA/<RUN_ID>.json` |

Lido o teste que a guarda — `test_nenhuma_migration_deu_MORADA_a_sala_de_espera`,
com `proibidas = ("waiting_room", "sala_de_espera", "ready", ...)` — a primeira
fala de **morada no banco**. Não de morada nenhuma.

```
«NAO TEM MORADA» ALI QUER DIZER «NAO TEM TABELA».
O FICHEIRO SEMPRE FOI MORADA.
```

**E essa medição está hoje desatualizada**, num ponto concreto: o caso `S5`
(«a morada declarada TEM escritor e ele está completo») **FALHA agora**, porque
procura a escrita dentro de `orquestrador/orquestrador.py` — e ela mudou de casa
para `admissao/sala_de_espera.py`. A medição não mente sobre o mundo; ela ficou a
apontar para a casa antiga.

---

## D · O CONTRATO READY, HOJE

```
COL-LAW-043 · 11 campos fixos · UM construtor
```

`admissao.pronto_para_inteligencia(item, decisao) -> dict`

```
ESTADO · ITEM_ID · UNIVERSO · TEXTO · SOURCE_ID · SOURCE_LOCATION
FACT_LOCATION · FACT_TIME · CAPTURED_AT · CORRIDA · ADMITIDO_POR
```

**Um construtor, e não dois.** A minha primeira contagem disse «2×» e estava
errada: a segunda ocorrência de `def pronto_para_inteligencia` é uma **string
literal** dentro de `system-map/scripts/generate_system_map.py:1060`, usada como
ponteiro de prova para o mapa. Não é uma definição.

```
UM GREP QUE CONTA DEFINICOES TEM DE SABER DISTINGUIR
UMA DEFINICAO DE UMA CITACAO DELA.
```

---

## E · A MORADA EM FICHEIRO, HOJE

```
data/samples/PRONTO-PARA-INTELIGENCIA/<RUN_ID>.json
DONO       admissao/sala_de_espera.py  ·  def pousar(run_id, unidades)
CHAMADORES coleta/rota_forward_documento.py · orquestrador/orquestrador.py
A PASTA    NAO EXISTE na árvore
```

E a última linha **não** é um defeito:

```
DESTINO VAZIO != DESTINO SEM DONO.
```

A pasta não existe porque nenhuma corrida preservada produziu aceites. `CAN DO ≠
DID DO`, e aqui o `CAN DO` está provado por travessia real.

---

## F · OPÇÃO A (FICHEIRO) — PROVAS

`provas/a_unidade_pousa_na_espera.py`, contra PostgreSQL 16 descartável, 29
migrations e bytes reais de um PDF italiano preservado (`SA-02-09.pdf`):

```
POUSA_NA_ESPERA=PASS · 26/26
```

| família | casos | o que prova |
|---|---|---|
| travessia | `E0`–`E11` | as 5 etapas na mesma corrida; 11 campos; linhagem READY→RAW |
| retry | `R1` `R2` | mesmo conteúdo → `REUSED`, e os bytes não mexem |
| conflito | `C1` `C2` | outra história → `RUN_ID_CONFLICT`, anterior intacto |
| atomicidade | `A1` `A2` | `mkstemp` + `fsync` + `os.replace`; zero temporários |
| crash | `X1` | crash antes da troca deixa o anterior válido |
| concorrência | `K1` `K2` | duas mãos na mesma corrida: uma escreve, a outra ouve «ocupada» |
| negativos | `N`×5 | `NAO` · `NAO_SEI` · `NAO_SE_APLICA` · `ERRO` não produzem nada |

⚠️ **As duas primeiras corridas desta prova falharam, e por nada de
arquitetura.** Faltava `pdftotext` na máquina — sem ele a cadeia para em
`DERIVED`, e os 24 casos a jusante caem como dominó. A segunda falhou porque o
banco descartável já tinha migrations aplicadas de uma corrida anterior.

```
UMA PROVA VERMELHA POR FALTA DE FERRAMENTA
DIZ ALGO SOBRE A MAQUINA, E NADA SOBRE O CODIGO.
```

Foi exatamente esse o erro que quase cometi: ler «FALHA» e escrever «a Sala de
Espera não funciona».

---

## G · OPÇÃO B (POSTGRESQL) — PROVAS

`provas/a_sala_de_espera_em_postgres.py` — **a mesma bateria, os mesmos nomes**,
num schema `ensaio_espera` que nasce e morre dentro da execução.

```
ESPERA_EM_POSTGRES=PASS · 21/21
```

```
UMA OPCAO QUE NUNCA CORREU NAO PERDE NEM GANHA. ELA NAO FOI MEDIDA.
```

A tabela do ensaio tem **os 11 campos e nem um a mais**, de propósito: para
mostrar o que a OPÇÃO B consegue **sem** violar a `COL-LAW-043`.

### O que a OPÇÃO B ganha

| | |
|---|---|
| `B_D1` | unicidade é do **banco** (`unique (corrida, item_id, universo)`), não do processo |
| `B_A1` | o lote publica inteiro ou não publica — a `check` recusou e a linha boa **não** entrou sozinha |
| `B_K1` | a segunda mão **bloqueou 2.4s** à espera do commit da primeira, em vez de ser recusada |
| `D3` | responde a `where universo = ...` — no ficheiro isso é um glob e abrir tudo |

### O que a OPÇÃO B **não** ganha

| | |
|---|---|
| `B_D2` | **nenhuma chave estrangeira para o RAW.** `ITEM_ID` é texto natural. Sem 12.º campo não há FK — e o 12.º campo é o que a lei proíbe |
| `B_C1` | `on conflict do nothing` **engoliu a divergência em silêncio**: 0 linhas, 0 exceção |
| `D1` | e `do update ... where` também devolve 0 linhas. Para **gritar**, o banco tem de LER-E-COMPARAR antes — exatamente o que o ficheiro já faz |
| `D2` | a unicidade é por **corrida**: o mesmo item em duas corridas entra duas vezes. O banco **não** resolve o duplicado entre corridas — e o ficheiro também não (`D2b`). **EMPATE** |

```
COMPRA-SE UM BANCO PELA INTEGRIDADE REFERENCIAL.
AQUI ELA NAO ESTA A VENDA: O CONTRATO NAO TEM A CHAVE.
```

---

## H · REFERÊNCIA EXTERNA

O padrão da OPÇÃO A é o **outbox/staging em ficheiro com publicação atómica**:
escrever num temporário na mesma filesystem, `fsync`, e `rename` — que o POSIX
garante atómico. É o que fazem os `maildir`, o `git` para refs e objetos, e
qualquer escritor de configuração que não queira deixar meio ficheiro.

O padrão da OPÇÃO B é a **transactional outbox**, e ele existe para um problema
que aqui não há: publicar para fora **na mesma transação** em que se muda estado
de negócio. A Sala de Espera não muda estado de negócio nenhum — ela pousa um
artefacto imutável no fim da estrada.

```
UM PADRAO RESOLVE UM PROBLEMA. ADOTA-LO SEM O PROBLEMA
E COMPRAR A CONTA SEM O JANTAR.
```

---

## I · A IDENTIDADE DA UNIDADE NA SALA

```
CHAVE NATURAL = (CORRIDA, ITEM_ID, UNIVERSO)
SURROGATE     = NAO EXISTE, e nao e preciso
```

A unidade **não** carrega `RAW_OBSERVATION_ID`. Isso é deliberado: `READY` é o
contrato que a Inteligência recebe, e ela não deve saber qual raspador trouxe o
dado. Um surrogate do RAW dentro do READY seria uma morada física dentro dos 11
campos — o §5 da missão proíbe, e a `COL-LAW-043` também.

---

## J · RELAÇÃO COM A DECISÃO DE ADMISSÃO

```
Decisao  item · universo · resultado · regra · motivo
         evidencia · versao · corrida · quando
```

Nove campos, **zero surrogate**, e o dono escreve num livro JSON
(`data/samples/LIVRO-DE-DECISOES.json`), não no banco.

Consequência para a OPÇÃO B: uma tabela READY **não teria a que se ligar**. Ou
se liga à admissão por chave natural, ou a ADMISSION ganha armazenamento — e
isso é `G-ADM-01`, dívida de **outro** portão. Adotar B arrastaria um portão que
não é este.

---

## K · CRASH E RETRY

| ataque | OPÇÃO A | OPÇÃO B |
|---|---|---|
| crash a meio da escrita | `X1` **PASS** — o parcial fica no temporário; o canónico lê-se inteiro | `B_X1` **PASS** — transação morta não deixa linha |
| retry com o mesmo conteúdo | `R1`/`R2` **PASS** — `REUSED`, bytes intactos | `B_R1`/`B_R2` **PASS** — `do nothing` absorve |
| a mesma corrida com **outra** história | `C1` **PASS · GRITA** | `B_C1` **PASS · CALA-SE** |

A última linha é a que decide, e é comportamento medido, não preferência.

---

## L · CONCORRÊNCIA

```
OPCAO A   trava por CORRIDA (flock não-bloqueante)
          duas mãos na mesma corrida -> a segunda ouve «ocupada» e RECUSA
          duas corridas diferentes -> não se tocam  (RT10 medido)

OPCAO B   sem trava explícita
          duas mãos na mesma corrida -> a segunda BLOQUEIA 2.4s e depois
          resolve pela unicidade no commit
```

São duas filosofias legítimas: **recusar** (A) versus **esperar** (B). Para uma
sala onde uma corrida escreve uma vez, recusar alto é mais fácil de auditar do
que esperar em silêncio.

⚠️ **E a OPÇÃO A tem aqui a sua pior aresta, dita na cara:** se um processo
morrer com a trava presa, o ficheiro `.lock` fica, e a escrita seguinte **falha
para sempre** até alguém apagar à mão. Está escrito no próprio código, e é uma
escolha declarada — «um estado preso e auditável é melhor do que uma limpeza
automática que não sabe se o outro lado ainda corre». O `RT11` mede-o: falha
alto e nomeia o ficheiro. **Não** é um defeito escondido; é uma dívida conhecida.

---

## M · SEGURANÇA

| | |
|---|---|
| `RT05` | `RUN_ID` com `../`, `/`, `\` ou `.` inicial é **recusado** — não se escreve fora da morada |
| `RT14` | symlink na morada: `os.replace` substitui o **link**, e o ficheiro de fora fica intacto |
| `RT15` | nenhum ficheiro escreve na morada sem passar pelo dono |
| OPÇÃO B | herdaria RLS e papéis do Supabase — vantagem real, e **não usada hoje**, porque não há consumidor |

---

## N · RED TEAM — 16 ATAQUES

`provas/red_team_da_sala_de_espera.py`

```
RED_TEAM_ESPERA=TUDO_DEFENDIDO · 16/16
```

| | ataque | |
|---|---|---|
| RT01 | criar uma SEGUNDA morada para o mesmo READY | DEFENDIDO |
| RT02 | meter `STORAGE_PATH` nos 11 campos «só para facilitar» | DEFENDIDO |
| RT03 | declarar um segundo construtor de READY | DEFENDIDO |
| RT04 | fabricar READY a partir de uma decisão que não foi SIM | DEFENDIDO |
| RT05 | escrever fora da morada com um `RUN_ID` `../` | DEFENDIDO |
| RT06 | criar uma espera fantasma com zero unidades | DEFENDIDO |
| RT07 | a mesma corrida contar outra história, em silêncio | DEFENDIDO |
| RT08 | o retry duplicar a unidade | DEFENDIDO |
| RT09 | deixar temporários `.espera-*` na sala | DEFENDIDO |
| RT10 | a trava de uma corrida bloquear as outras | DEFENDIDO |
| RT11 | uma trava presa ser limpa em silêncio | DEFENDIDO |
| RT12 | um crash a meio deixar o canónico truncado | DEFENDIDO |
| RT13 | uma migration dar tabela à espera sem ninguém decidir | DEFENDIDO |
| RT14 | um symlink redirigir a escrita para fora | DEFENDIDO |
| RT15 | escrever na morada sem passar pelo dono | DEFENDIDO |
| RT16 | o consumidor ler meia corrida a meio da escrita | DEFENDIDO |

### ⚠️ O RT15 acusou duas provas, e **eu** estava errado

A primeira versão perguntava «este ficheiro **nomeia** a morada?» e acusou
`provas/a_fronteira_da_coleta.py` e `provas/mutacao_do_fluxo_canonico.py`. Lidos:
o primeiro faz `os.path.isdir(destino)` para **medir** se a pasta existe; o
segundo carrega a morada dentro de uma string de **mutação** que aplica a uma
cópia da árvore num temporário, e repõe.

```
NOMEAR UMA MORADA NAO E ESCREVER NELA.
```

É a mesma família do ataque que o censo do Control Plane cometeu contra si
próprio: uma busca que casa com a **menção** quando a pergunta era sobre o
**comportamento**. O detetor foi corrigido para só acusar quem leva um caminho
derivado da morada a uma chamada de escrita — e não para escrever em prosa que
o resultado era falso positivo.

```
8 ficheiros NOMEIAM a morada; os que lhe ESCREVEM sem o dono: nenhum.
```

---

## O · MATRIZ DE DECISÃO

`A` = ficheiro · `B` = PostgreSQL · `=` = empate medido

| # | critério | A | B | medido em |
|---|---|:--:|:--:|---|
| 1 | escrita atómica | ✅ | ✅ | `A1` · `B_A1` |
| 2 | crash a meio não corrompe | ✅ | ✅ | `X1` · `B_X1` |
| 3 | retry idempotente | ✅ | ✅ | `R1` · `B_R1` |
| 4 | conflito de corrida **audível** | ✅ | ❌ | `C1` grita · `B_C1` cala-se |
| 5 | concorrência na mesma corrida | ✅ | ✅ | `K1` recusa · `B_K1` espera |
| 6 | corridas diferentes não se serializam | ✅ | ✅ | `RT10` |
| 7 | unicidade garantida pelo motor | ❌ | ✅ | `B_D1` |
| 8 | FK para o RAW | ❌ | ❌ | `B_D2` — o contrato não tem a chave |
| 9 | duplicado entre corridas | = | = | `D2` · `D2b` |
| 10 | consulta por campo | ❌ | ✅ | `D3` |
| 11 | leitura parcial / paginação | ❌ | ✅ | `D7` |
| 12 | escrita de 5000 unidades | 0.05s | 0.11s | `D4` |
| 13 | leitura da corrida inteira | 0.012s | 0.035s | `D5` |
| 14 | migrations necessárias | **0** | 1 | `RT13` |
| 15 | moradas para o mesmo conceito | **1** | **2** | `RT01` |

**Critério 15 é o que decide.** Os critérios 7, 10 e 11 são reais e ficam por
ganhar — mas nenhum tem consumidor hoje que os peça.

```
UMA VANTAGEM SEM CONSUMIDOR E UMA CONTA A PAGAR ANTES DO JANTAR.
```

---

## Q · DELTA DE BÍBLIA E CONTRATO

```
COL-LAW-043   INALTERADA — 11 campos, um construtor
COL-LAW-044   INALTERADA — lista `data/samples` E Supabase como armazenamento
ADR-SALA-DE-ESPERA-V1   INALTERADO — este relatório confirma-o, não o substitui
```

**Nada muda.** E isso é o resultado, não a falta dele.

---

## R · DELTA DO SYSTEM MAP

```
MAPA=OK · pecas=138 (🟢96 🟡34 🔴4 ⚪4) · ligacoes=373
SYSTEM_MAP_CHECK=PASS · 18/18
```

⚠️ **E aqui um achado sobre o próprio validador**, encontrado por acidente: o
scanner do mapa lê ficheiros **rastreados pelo git**. Enquanto as duas provas
novas estavam por commitar, `P9_CODIGO_DECLARADO` passava — e não passava *por
elas estarem declaradas*, mas por **não as ver**.

```
UM PORTAO QUE NAO VE O FICHEIRO NOVO
APROVA-O SEM O LER.
```

O mapa foi regerado **depois** do commit, e é essa corrida que vale.

---

## S · DELTA DE KNOW-HOW

Ver `handoff/KNOW-HOW-DELTA-MORADA-DA-SALA-DE-ESPERA.md`.

---

## T · O QUE **NÃO** MUDOU

```
admissao/admissao.py              INTACTO
admissao/sala_de_espera.py        INTACTO
coleta/rota_forward_documento.py  INTACTO
orquestrador/orquestrador.py      INTACTO
supabase/migrations/              INTACTO — 30 ficheiros, zero novos
docs/decisoes/ADR-SALA-DE-ESPERA-V1.md   INTACTO
```

Nenhuma tabela criada. Nenhuma migration. Nenhum campo acrescentado ao READY.
Nenhuma alteração à Admission. Nenhuma Intelligence ligada. Zero LIVE.

O único código escrito nesta missão são **duas bancadas de medição**, e elas
não entram no caminho do dado.

---

## U · O QUE FICA EM NÃO SEI

```
NAO_SEI  quantas unidades uma corrida real de producao produz.
         5000 foi um numero que eu escolhi, e nao um numero medido no mundo.
         Se uma corrida real fizer 5 milhoes, o criterio 13 muda de lado.

NAO_SEI  como a Inteligencia vai QUERER ler a sala. Nao ha consumidor, e
         por isso os criterios 10 e 11 nao tem peso hoje. O primeiro
         consumidor real pode reabrir a pergunta, e a COL-LAW-044 garante
         que trocar o meio nao redefine READY.

NAO_SEI  o custo de operar a trava presa (RT11) em producao. Nunca aconteceu,
         porque a rota nunca correu em producao.

NAO_SEI  se `provas/a_sala_de_espera_nao_tem_morada.py` deve ser corrigida ou
         aposentada. O caso S5 aponta para a casa antiga do escritor. Nao lhe
         toquei: nao e minha, e uma medicao desatualizada que se corrige de
         fora perde o historico de por que existiu.
```

---

## V · O PRÓXIMO PASSO MÍNIMO

```
UM: consertar o caso S5 de `provas/a_sala_de_espera_nao_tem_morada.py`,
    que ainda procura o escritor dentro do orquestrador.
    NAO E ARQUITETURA. E uma medicao a apontar para a casa antiga.
```

E o passo seguinte, que **não** é desta missão: a Sala de Espera não tem
consumidor. A Inteligência ainda não a lê. Enquanto isso for verdade, todos os
argumentos a favor de PostgreSQL continuam sem peso — e no dia em que houver
consumidor, a troca é **dentro** de `admissao/sala_de_espera.py`, porque o dono
é um só.

```
O DONO UNICO E O QUE TORNA A DECISAO REVERSIVEL.
FOI ESSA A PARTE CARA, E ELA JA ESTA PAGA.
```
