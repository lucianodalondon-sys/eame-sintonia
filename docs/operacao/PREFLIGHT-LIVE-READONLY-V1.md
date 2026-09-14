# PREFLIGHT LIVE — RETRATO SOMENTE LEITURA

```
MISSAO            C-LIVE-PREFLIGHT-READONLY-V1
MEDIDO_EM         2026-09-13T12:04Z
MEDIDO_NO_COMMIT  2e093c60  (ramo claude/live-preflight-readonly-v1)
HEAD_FUNCIONAL    e16fdd1b
MEDIDO_POR        provas/auditoria_live.sh, seccao H · corrida 30
LIVE_WRITES       0
```

> ## ⚠️ ISTO É UM RETRATO, E NÃO UMA FONTE DE VERDADE
>
> A fonte de verdade sobre migrations é **o livro-razão do banco** mais
> `supabase/migrations/`. Este ficheiro é o que se viu **num instante**, e
> envelhece a partir do segundo em que foi escrito.
>
> Quem precisar do estado de hoje **corre a auditoria**, não lê isto.
> Um documento que se deixe consultar como se fosse o banco vira o segundo
> dono de uma verdade que já tem dono — e dois donos divergem.

---

## 1 · O PORTÃO

```
READ_ONLY_SESSION   on      (begin read only, confirmado pelo servidor)
READ_ONLY_PROVEN    YES
```

A sessão é fechada com `begin read only` e a resposta é **conferida** antes
de qualquer pergunta. Isto não é cerimónia: na corrida 29 o mecanismo
anterior (`PGOPTIONS`) foi silenciosamente ignorado pelo endpoint vivo e
devolveu `off`. O preflight recusou-se a correr, como devia.

```
PEDIR NAO E OBTER.
```

## 2 · O LIVRO-RAZÃO

```
LIVE_SCHEMA_LEDGER_EXISTS   YES
LEDGER_ROWS                 26
LEDGER_DUPLICATES            0
LEDGER_INVALID_RESULTS       0
LEDGER_MISSING_SHA           0
EXTRA_IN_LIVE                nenhuma
```

`LEDGER_VERSIONS` = `001`–`007`, `009`–`027` (a `008` **confere**, não cria,
e por isso nunca entra na cadeia nem no livro).

**Drift de SHA:** nenhum. Cada versão do livro foi comparada byte a byte com
o ficheiro do repositório — `SHA_MISMATCH = {}`.

## 3 · O QUE FALTA APLICAR

```
PENDING_IN_LIVE   028 · 029 · 030
```

## 4 · AS TABELAS DA COLLECTION

| tabela | existe | linhas |
|---|---|---|
| `collection_run` | SIM | 11 |
| `raw_asset` | SIM | 252 |
| `storage_object` | SIM | 252 |
| `derived_artifact` | SIM | 1 |
| `etapa_da_corrida` | SIM | 0 |
| `participacao_na_derivacao` | **NÃO** | — |
| `documento_estruturado` | **NÃO** | — |
| `schema_migracao` | SIM | 26 |

Estrutura e contagem. **Nenhuma linha de corpus foi lida.**

## 5 · AS TRAVAS

Todas as travas das oito tabelas acima estão **validadas** (`convalidated =
true`). Duas travas do banco não estão, e **nenhuma delas é da Collection**:

```
crop_calendar.calendario_geografia_e_do_pais
issue_window.janela_issue_geografia_e_do_pais
```

Uma trava por convalidar existe no catálogo e não foi conferida contra as
linhas que já lá estavam: parece uma trava e não garante o passado. Ficam
declaradas; não são objecto desta missão.

## 6 · A `029` E A `030`, PELAS DUAS PERGUNTAS

```
MIGRATION_029_IN_LEDGER = NO    PARTICIPACAO_NA_DERIVACAO_EXISTS = NO
MIGRATION_030_IN_LEDGER = NO    DOCUMENTO_ESTRUTURADO_EXISTS     = NO
```

São perguntas diferentes, e a diferença entre elas seria o achado:

```
REGISTADA SEM TABELA  = o livro mente sobre o que correu
TABELA SEM REGISTO    = o aplicador vai tropecar nela
```

Aqui as duas respostas **coincidem** nos dois casos — o livro e o schema
contam a mesma história. Não há conflito.

## 7 · BACKUP E RESTORE

```
LIVE_BACKUP_STATUS    NOT_MEASURED
LIVE_RESTORE_STATUS   NOT_PROVEN
```

Não é a mesma coisa, e a diferença é deliberada:

- **`NOT_MEASURED`** — a configuração de backup do projeto não foi medida.
  Esta sessão não tem `SUPABASE_ACCESS_TOKEN` nem ref do projeto, e a
  auditoria fala com o banco por `psql`, não com a API de gestão. Não medi;
  não digo.
- **`NOT_PROVEN`** — um restore ensaiado deixa registo. Procurei em `docs/`,
  `.github/`, `motor/` e `provas/`: **não existe nenhum**. Prova é artefacto
  positivo, e a ausência dele é ausência de prova.

```
BACKUP EXISTE != RESTORE PROVADO.
«O SUPABASE TEM BACKUP» NAO E UMA MEDICAO.
```

## 8 · VEREDITO

```
PREFLIGHT_MISSION     = PASS
LIVE_READY_FOR_APPLY  = NO
BLOCKER               = RESTORE_NOT_PROVEN
```

O estado do LIVE é **conhecido e coerente**: livro-razão íntegro, zero
drift, zero versões órfãs, schema a bater com o livro, e as três pendentes
identificadas. Do lado do banco não há nada a impedir um apply.

O que falta não é do banco: é a **capacidade de voltar atrás**. Enquanto
`RESTORE` não estiver provado, `LIVE_READY_FOR_APPLY` é `NO` — e um `NO`
medido é um resultado, não uma falha desta missão.

**A aplicação pertence a outra missão, e exige autorização explícita.**
