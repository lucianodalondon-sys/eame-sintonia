# ADR — A SALA DE ESPERA V1 FICA NO SISTEMA DE FICHEIROS

**Data:** 2026-09-12 · **Estado:** IMPLEMENTADO
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
| `READY` tem contrato de 11 campos | `COL-LAW-043` · `BIBLIA-CANONICA-DA-COLETA.md` |
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
