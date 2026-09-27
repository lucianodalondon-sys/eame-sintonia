# ADR — A SALA DE ESPERA

**Data:** 2026-09-12 · **Estado:** V1 SUPERADA PELA EMENDA DE 2026-09-13

> ## ⚠️ LEIA A EMENDA ANTES DO CORPO
>
> O corpo abaixo é a decisão **V1**, de 2026-09-12, e continua aqui inteiro
> porque foi tomada, foi correcta para o que se sabia, e apagá-la esconderia
> como se chegou à seguinte. **Ela já não descreve o backend de hoje.**
>
> O que mudou está na [**EMENDA · 2026-09-13**](#emenda--2026-09-13--a-sala-ganha-dono-duravel),
> no fim deste ficheiro. Esta ADR não foi substituída por uma `V2`: ela é o
> ficheiro da decisão, e uma decisão que muda continua a ser a mesma decisão
> com mais um capítulo.
>
> ```
> WAITING_ROOM_CANONICAL_BACKEND   POSTGRES   (desde 2026-09-13)
> WAITING_ROOM_V1_BACKEND          FILESYSTEM (histórico, não canónico)
> ```
**Missão:** `C-CLOSE-READY-WITH-CANONICAL-WAITING-ROOM-V1`
**Decidido por:** gente. A medição que abriu a pergunta está em
`provas/a_sala_de_espera_nao_tem_morada.py`, e o know-how em `§74`.

---

## 1 · O QUÊ

A unidade `READY` da rota forward pousa na morada que já existia:

```
data/samples/PRONTO-PARA-INTELIGENCIA/<RUN_ID>.json
```

**Não** se cria tabela para READY. **Não** se cria migration para a Sala de
Espera. **Não** se persiste a decisão de admissão em PostgreSQL.

---

## 2 · POR QUÊ

Um conceito já tinha uma morada funcional. `orquestrador/orquestrador.py`
decidia, chamava o dono do READY por cada `SIM` e gravava o ficheiro da
corrida — completo, a correr, e nunca medido como tal. A pasta não existia
porque nenhuma corrida daquele caminho produzira aceites.

> **DESTINO VAZIO ≠ DESTINO SEM DONO.**

Criar uma tabela ao lado teria criado uma **segunda verdade** sobre a mesma
espera, e obrigado a retirar a primeira — mexendo num caminho que não era o
dos dois blockers.

E não há necessidade **medida** que exija banco: zero consumidores, uma
unidade por corrida, nenhum requisito de consulta declarado.

---

## 3 · PROVA

| O quê | Onde |
|---|---|
| `READY` tem contrato de 12 campos (eram 11 quando isto se escreveu; `RAW_OBSERVATION_ID` entrou em `C-READY-LINEAGE-BEFORE-SCALE-V1`) | `COL-LAW-043` · `BIBLIA-CANONICA-DA-COLETA.md` |
| `READY` tem **um** construtor | `admissao.pronto_para_inteligencia()` |
| Armazenamento ≠ estado lógico | `COL-LAW-044` — lista `data/samples` **e** Supabase |
| O orquestrador já gravava a morada | `provas/a_sala_de_espera_nao_tem_morada.py::S5` |
| A unidade pousa, na mesma corrida | `provas/a_unidade_pousa_na_espera.py` |

---

## 4 · CONSEQUÊNCIA

**O writer saiu do control plane.** `COL-LAW-012` separa os dois planos, e a
escrita vivia dentro do orquestrador. Enquanto a única escrita estivesse lá, a
rota forward não tinha como pousar a unidade sem escrever uma **segunda**.

O dono passou a ser `admissao/sala_de_espera.py`, e os dois caminhos —
orquestrador e rota forward — chamam-no.

> **ONE CONCEPT → ONE OWNER.**

**E o ficheiro ganhou as travas que um ficheiro exige:** escrita atómica por
troca (`os.replace` depois de `fsync`), retry idempotente (`REUSED`), conflito
explícito quando a mesma corrida traz outra história (`RUN_ID_CONFLICT`), e uma
trava por corrida contra duas mãos simultâneas.

> **UMA `RUN_ID` NÃO PODE CONTAR DUAS HISTÓRIAS.**

---

## 5 · O QUE ESTA DECISÃO NÃO FECHA PARA SEMPRE

```
WAITING_ROOM_V1_BACKEND        FILESYSTEM
WAITING_ROOM_LOGICAL_STATE     READY
BACKEND_CHANGE_ALLOWED_LATER   YES
BACKEND_CHANGE_REQUIRES        PROVA DE NECESSIDADE
                               + MIGRAÇÃO CANÓNICA
                               + UM ÚNICO OWNER
```

PostgreSQL **não** está aposentado: está `NOT_REQUIRED_NOW`. Volume,
concorrência, consulta ou consumo de Intelligence que provem necessidade
reabrem a pergunta — e a `COL-LAW-044` garante que trocar o meio **não**
redefine o estado. `READY` continua `READY`.

Porque o dono é um só, a troca de backend é uma mudança dentro de
`admissao/sala_de_espera.py`, e não uma reescrita de quem o chama.


---

<a id="emenda--2026-09-13--a-sala-ganha-dono-duravel"></a>

# EMENDA · 2026-09-13 — A SALA GANHA DONO DURÁVEL

**Missão:** `C-SALA-PERSISTENTE-E-PREFLIGHT-REAL-V1`
**Estado:** IMPLEMENTADO EM DESCARTÁVEL · **NÃO APLICADO NO LIVE**

---

## 1 · A DECISÃO ANTERIOR ERA SUFICIENTE — PARA A PERGUNTA QUE TINHA

A V1 escolheu o sistema de ficheiros, e a escolha estava certa contra o que se
sabia em 2026-09-12: zero consumidores, uma unidade por corrida, nenhuma
consulta declarada, e uma morada que já existia. Ela até escreveu a porta de
saída:

```
BACKEND_CHANGE_ALLOWED_LATER   YES
BACKEND_CHANGE_REQUIRES        PROVA DE NECESSIDADE
```

## 2 · O FACTO REAL NOVO

A prova chegou na primeira tentativa de coleta real italiana,
`C-ITALIA-FIRST-REAL-COLLECTION-CANARY-V1`, que parou antes de adquirir um
único byte. A pergunta que ninguém tinha feito era esta:

> quando o runner acabar, onde é que o READY fica?

E a resposta, medida contra o repositório inteiro e não suposta:

```
git log --all -- 'data/samples/PRONTO-PARA-INTELIGENCIA'   ->   vazio
```

Nunca, em ramo nenhum, um ficheiro da Sala foi versionado. Nenhum workflow lhe
faz `git add` — o `sintonia-scrap.yml` até **recusa** qualquer caminho fora de
`INSTAGRAM|YOUTUBE|SCRAP`. Nenhum `upload-artifact` o apanha. Não há dono em
banco. E o `actions/checkout` seguinte limpa o que não está versionado.

```
MODULE EXISTS != FILE WRITTEN ON RUNNER != PERSISTED AFTER RUN.
PROVA DENTRO DO PROCESSO != DURABILIDADE OPERACIONAL.
```

A V1 escolheu o **meio** e nunca respondeu à **sobrevivência**. Não é
contradição dela: é uma pergunta que ela não fez, e que só aparece quando se
tenta coletar a sério.

## 3 · A DECISÃO NOVA

```
WAITING_ROOM_CANONICAL_BACKEND        POSTGRES · public.sala_de_espera
WAITING_ROOM_CANONICAL_OWNER          admissao/sala_de_espera.py  (o MESMO)
WAITING_ROOM_CANONICAL_IDENTITY       (run_id, ordem)
WAITING_ROOM_CANONICAL_WRITE          pousar(run_id, unidades)
WAITING_ROOM_CANONICAL_READ           ler(run_id) · listar_pendentes(limite)
WAITING_ROOM_CANONICAL_ACK            retirar(run_id, item_id, por)
                                      WAITING -> CONSUMED, sem apagar
WAITING_ROOM_CANONICAL_CONFLICT_RULE  mesma corrida com outra impressão ->
                                      RUN_ID_CONFLICT, e não se escreve nada
WAITING_ROOM_CANONICAL_RETRY_RULE     mesma corrida com a mesma impressão ->
                                      REUSED, sem duplicar
WAITING_ROOM_CANONICAL_CRASH_RULE     uma transação, ou nada. Um processo morto
                                      a meio não deixa meio READY visível
WAITING_ROOM_CANONICAL_CONCURRENCY    pg_advisory_xact_lock por CORRIDA, que
                                      morre com a transação
```

### 3.1 · Por que Postgres, e não as outras

Medido, e não preferido:

| opção | porquê não |
|---|---|
| filesystem local | morre com o job. É o defeito que abriu esta emenda. |
| Git | `P-011 · GIT NÃO É BANCO OPERACIONAL`. Um commit por execução faz do histórico a memória da fila. A casa já tinha recusado isto por escrito. |
| artefato do Actions | retenção de 30 dias, declarada no próprio workflow: `WORKFLOW ARTIFACT != CANONICAL FORWARD STORAGE`. |
| Supabase Storage | guarda **bytes**. A Sala não tem bytes — tem uma fila com estado, unicidade e transição. Um bucket não tem `unique`, não tem transação e não sabe recusar a segunda escrita divergente. |
| PostgreSQL + Storage | o segundo membro não tem trabalho: o READY carrega um **ponteiro** (`RAW_OBSERVATION_ID`), e os bytes já têm dono em `raw_asset` → `storage_object`. |

```
A MENOR IDENTIDADE QUE FECHA A ESTRADA É A CERTA.
```

### 3.2 · O dono não mudou, e é isso que torna a troca barata

A V1 tinha escrito: *«porque o dono é um só, a troca de backend é uma mudança
dentro de `admissao/sala_de_espera.py`, e não uma reescrita de quem o chama.»*
Foi exactamente o que aconteceu. O orquestrador e a rota forward continuam a
chamar `espera.pousar()` e continuam a não saber onde a sala guarda.

E o padrão dos dois backends por trás de um dono não é invenção desta missão:
é o de `guarda/preservar_coleta.py` + `guarda/memoria_descartavel.py`, que já
cá estava.

### 3.3 · Dois backends, uma só verdade — e a diferença está declarada

```
POSTGRES   CANÓNICO
FICHEIRO   NÃO CANÓNICO — a V1, preservada, para prova offline
```

Um por processo, e o recibo diz sempre qual foi (`CANONICO`). O que **não**
acontece é a queda silenciosa de um para o outro: pedir `POSTGRES` sem DSN
levanta `SalaIndisponivel` e **não** escreve em disco.

```
UM FALLBACK SILENCIOSO PARA DISCO EFÉMERO
É A MESMA FALHA COM OUTRO NOME.
```

E quem manda no caminho operacional é `exigir_canonica()`, chamado pelo
preflight ANTES da aquisição.

## 4 · O QUE ESTA EMENDA **NÃO** DECIDE

**Não decide relevância.** `CONSUMED` quer dizer «saiu da fila», e mais nada.
Não há coluna de veredito, `retirar()` não recebe nenhum, e há prova que
reprova se aparecer.

```
COLLECTION TERMINA NA SALA. A SALA NÃO JULGA.
```

`KEEP`/`TEMP`/`DISCARD` continuam a ser da Intelligence, e a Intelligence
continua a ser outra missão. O que esta emenda garante é que o modelo **não
força** uma fila eterna: a transição mínima existe, é auditável, e não apaga.

## 5 · O ACHADO QUE QUASE PASSOU DESPERCEBIDO

A chave da fila ia ser `(run_id, item_id)`. Medi-la matou-a:

```python
ITEM_ID = str(item.get("id") or item.get("url") or "?")
```

`"?"` é alcançável. Dois itens admitidos sem `id` e sem `url` na mesma corrida
trazem **ambos** `ITEM_ID = "?"` — e uma chave primária ali deitaria um deles
fora.

```
ITEM_ID NÃO É IDENTIDADE GARANTIDA DENTRO DA CORRIDA.
```

A chave é `(run_id, ordem)`. `item_id` continua guardado e indexado; o que ele
não é, aqui, é endereço — e `retirar()` por um `ITEM_ID` ambíguo é **recusado**
com nome (`ItemAmbiguo`) em vez de escolher um à sorte.

## 6 · PROVA

| o quê | onde |
|---|---|
| a migration aplica pela cadeia canónica | `supabase/migrations/031_a_sala_de_espera_ganha_dono_duravel.sql` |
| durabilidade, crash, concorrência, linhagem, retirada | `provas/a_sala_sobrevive_ao_processo.py` — 67 casos, 30 ataques, 0 sobreviventes |
| as leis mordem | `provas/mutacao_da_sala_duravel.py` — 17 mutantes, 17 mortos |
| o que não precisa de banco | `tests/test_sala_duravel.py` |
| e corre no CI | `.github/workflows/banco-descartavel.yml` passos `2b5`–`2b7` |

## 7 · O QUE CONTINUA EM ABERTO

```
LIVE_MIGRATION_APPLIED   NO
```

Esta emenda está provada em **descartável**. A aplicação no LIVE é uma decisão
explícita e separada, e o pacote dela está em
`docs/operacao/C-SALA-PERSISTENTE-E-PREFLIGHT-REAL-V1.md`.
