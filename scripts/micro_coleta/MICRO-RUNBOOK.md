# MICRO_RUNBOOK — a micro-coleta real, passo a passo

Para o coordenador. Cada passo tem **o comando**, **o que conferir** e **quando abortar**.
Tudo corre na árvore da produção (a linha instalada), em PowerShell ou Git Bash, a partir
da raiz do repositório. Nenhum passo apaga dados; o único que desfaz é o R (rollback),
e só com o dump do passo 3.

A coorte **não é uma lista**: é o que o portão (`collection_gate.elegiveis`) diz no
instante, menos o que não tem capacidade técnica (contrato, receita web, rota). A
relevância não barra a fonte (D2 + D8): decide-se por item, na Admission (REROUTE).

---

## 0. Pré-condições (todas verdes, ou não se começa)

| # | o quê | como conferir | abortar se |
|---|---|---|---|
| 0.1 | a produção é a linha com a A2 (`micro-pronta-v1` ou quem a suceder) | `git log -1 --oneline` na árvore do serviço | outra linha |
| 0.2 | ensaio offline verde nesta linha | `py scripts/micro_coleta/ensaio_offline.py --duas-passagens` → C4..C9 PASS, 2.ª passagem REFETCH 0 e FALSE_CHANGED 0 | qualquer um ≠ 0, ou C6/C8 FAIL |
| 0.3 | testes do instrumento | `py -m unittest tests.test_micro_coleta_instrumento tests.test_ensaio_offline_micro` | qualquer falha |
| 0.4 | a Sala real está de pé | `py -c "import sys; sys.path.insert(0,'scripts/micro_coleta'); import micro_coleta as M; print(M.sql('select count(*) from sala_de_espera'))"` | erro de ligação (depois de reiniciar o PC, correr `~\sintonia-sala-italia\ligar_sala.cmd`) |
| 0.5 | egresso IT | `curl -s https://ipinfo.io/country` → `IT` | outro país ou vazio: ligar a VPN IT |
| 0.6 | custo 0 USD | no plano (passo 2), todas as PRONTAS são `italia-recorrente` (gratuito) | alguma rota paga |

## 1. Parar a escrita concorrente

O rollback (R) exige a base **sem ligações**, e o livro do coletor não deve mudar por
outra mão durante a micro.
- Serviço do curator: criar `PARAR.flag` na pasta `curadoria` da árvore do serviço e
  esperar o supervisor dizer `PARA_FLAG`.
- Coletor agendado: confirmar que nenhum job de coleta está marcado para a próxima hora.
- **Abortar se** o supervisor não parar.

## 2. O plano (sem rede, sem banco)

```
py scripts/micro_coleta/micro_coleta.py plano > %TEMP%\micro-plano.json
```

Conferir:
- `COORTE` = `PORTAO (collection_gate.elegiveis)`;
- `PRONTAS` ≥ 1, e cada BLOQUEADA com `FALTA`;
- `FORA_DO_PORTAO` com MOTIVO/PORQUE;
- `G1_FORA_DO_PORTAO` lido.

No ensaio da A2: 19 elegíveis → **8 PRONTAS** (IT-T10-018, -021, -022, IT-T7-017, -021,
-033, -042, -043); 11 bloqueadas por capacidade (9 sem contrato, 4 sem receita web,
2 rota); do G1, só a IT-T7-041 fica fora (canário do contrato falhou).

**Abortar se** o plano sair com `FILTRO_AUSENTE` (código 3): um filtro declarado não se lê.

## 3. Backup da Sala, IMEDIATAMENTE antes

```
%USERPROFILE%\sintonia-sala-italia\backup_sala.cmd
```

É o mesmo que `pg_dump -Fc -Z 6 --no-owner --no-privileges -f <ficheiro> <DSN>`, e o
script confere que o índice do dump lista `sala_de_espera`. **Anotar o nome do ficheiro**:
é o único caminho de volta.

Prova (opcional, recomendada): `py scripts/micro_coleta/provar_backup_da_sala.py`. Faz o
mesmo dump, restaura-o num Postgres descartável e compara o md5 das 5 tabelas com a Sala
real. Na A2, em 23/09: dump de 2,17 MB, Sala real 61 / raw 1405 / storage 1097 /
derived 908 / runs 389, e a cópia restaurada **idêntica**.

Registar **SALA_BEFORE**:
```
py -c "import sys; sys.path.insert(0,'scripts/micro_coleta'); import micro_coleta as M; print(M.sql('select count(*) from sala_de_espera'))"
```

**Abortar se** `BACKUP=FAIL`, ou se o índice do dump não tiver `sala_de_espera`.

## 4. As quatro variáveis da Sala

```
set SINTONIA_SALA_BACKEND=POSTGRES
set SINTONIA_SALA_DSN=<conteudo de %USERPROFILE%\sintonia-sala-italia\SALA_DSN.txt>
set SINTONIA_COLLECTION_DSN=<a mesma DSN>
set SINTONIA_PSQL_EXE=%USERPROFILE%\orca\pgtmp\pgsql\bin\psql.exe
set BANCO_DESCARTAVEL_URL=
```

⚠️ Sem `SINTONIA_SALA_BACKEND=POSTGRES`, a Sala cai calada num FICHEIRO. O `correr` recusa
arrancar sem as quatro, e com `BANCO_DESCARTAVEL_URL` definido.

## 5. A corrida (a única porta para a rede)

```
py scripts/micro_coleta/micro_coleta.py correr --autorizado-pelo-dono --saida=%TEMP%\micro-coleta-real
```

O que ela faz:
1. refaz o plano (o portão no instante);
2. para cada PRONTA: mede o egresso **antes**, regista o veredito do portão **no instante**,
   lança o orquestrador pela porta canónica e mede o egresso **depois**;
3. no fim chama o `relatorio` sobre os RUN_ID que nasceram.

**Abortar (Ctrl+C e ir a R) se:**
- o egresso sair de IT no meio (a fonte seguinte não arranca; parar de vez);
- qualquer corrida demorar mais de 30 minutos;
- aparecer `ModosEmConflito`, `SalaIndisponivel` ou `persistencia: FICHEIRO` na saída;
- o número de pedidos por fonte passar de 3 × MAX_TARGETS (90).

## 6. Ler o resultado

Os ficheiros ficam em `%TEMP%\micro-coleta-real\`: `RELATORIO-PASSAGEM.json`, `.md`,
`CLASSES.tsv` e `CAPAS-A-CONFIRMAR.tsv`.

| campo do mandato | onde está |
|---|---|
| SOURCES_ATTEMPTED | saída do `correr`: `CORRIDAS` com `CORREU=true` |
| SOURCES_SUCCESS | `CONTAGENS.COLETOR.SOURCES_SUCCESS` (saúde do coletor, não o código de saída) |
| DETAIL_DOCUMENTS | `CONTAGENS.COLETOR.DETAIL_DOCUMENTS` |
| LISTINGS_REJECTED | **MISSING_ROUTE** no código; o juiz de capa (C2) aponta depois |
| RAW_CREATED | `CONTAGENS.RAW_CREATED` (só documentos); `TENTATIVAS_FALHADAS` à parte, com motivo |
| DERIVED_CREATED | `CRITERIOS.C4.COM_DERIVADO` |
| ADMISSION_SIM / NAO / NAO_SEI | `CRITERIOS.C7.POR_FONTE` (somar) |
| SALA_BEFORE / AFTER / DELTA | passo 3 e passo 7; `C4.SALA_LINHAS` = linhas da corrida |
| UNNECESSARY_REFETCHES | `CONTAGENS.COLETOR.UNNECESSARY_REFETCHES` |
| FALSE_DOCUMENT_CHANGED | **MISSING_ROUTE** no código; medido no ensaio (2.ª passagem) |
| PROVENANCE_FAILURES | `C4`: documentos sem cadeia completa (tentativas falhadas já não contam) |
| NETWORK_REQUESTS | `CONTAGENS.COLETOR.NETWORK_REQUESTS` (+ 2 ipinfo por fonte do instrumento) |
| PAID_USD | 0, declarado pela receita (`italia-recorrente`) |

Critérios: **C6 (zero bypass) e C8 (0 SIM errado no gabarito do dono) têm de passar.**
C2 PENDENTE_HUMANO significa que uma pessoa lê o `CAPAS-A-CONFIRMAR.tsv`.

## 7. Depois

- Registar SALA_AFTER (mesmo comando do passo 3).
- Retirar o `PARAR.flag` do serviço.
- Guardar `%TEMP%\micro-coleta-real\` fora do TEMP, junto com o nome do dump.

## R. Rollback (só se for preciso desfazer)

Com o serviço **parado** e ninguém ligado à `sala_italia`:

```
set PG=%USERPROFILE%\orca\pgtmp\pgsql\bin
set ADMIN=postgresql://<utilizador>@127.0.0.1:54330/postgres
"%PG%\dropdb.exe"   --if-exists --maintenance-db=%ADMIN% sala_italia
"%PG%\createdb.exe" --maintenance-db=%ADMIN% sala_italia
"%PG%\pg_restore.exe" --no-owner --no-privileges -d "%SINTONIA_SALA_DSN%" <ficheiro do passo 3>
```

Conferir: a contagem de `sala_de_espera` = SALA_BEFORE, e a mesma fotografia que o
`provar_backup_da_sala.py` mostra.

⚠️ **Nunca** `pg_restore` por cima da base existente: ele «ignora» centenas de erros, sai
com código 1 e **não desfaz nada** (medido no ensaio da A1). O `dropdb` e o `createdb` usam
`--maintenance-db`, não `-d`.

O armazém de bytes (`%USERPROFILE%\sintonia-sala-italia\armazem`) e o livro do coletor
(`data/collection-ledger/italy/*.ndjson`) não são desfeitos pelo rollback do banco: os bytes
novos ficam órfãos. Nenhum armazém desta casa apaga; isso fica registado, não apagado.
