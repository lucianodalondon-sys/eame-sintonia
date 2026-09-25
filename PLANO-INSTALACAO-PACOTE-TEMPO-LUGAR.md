# PACOTE-TEMPO-LUGAR · plano de instalação (numerado) + ensaio integrado

Ramo `pacote-tempo-lugar-v1`, a partir do vivo `origin/servico-20260923-0923` @ `b607c9af`.
**NÃO instalado.** Nada tocou a Sala real: o ensaio correu numa CÓPIA dela (dump só-leitura da
MIGRACAO-SALA) dentro de um Postgres DESCARTÁVEL.

```
MIGRAÇÃO 033 PRIMEIRO  ->  CÓDIGO DEPOIS          (instalar)
CÓDIGO PRIMEIRO        ->  DESFAZER 033 DEPOIS    (voltar)
```
O código do pacote escreve 4 colunas novas (`published_at_basis`, `source_location_basis`,
`completude_tempo_lugar`, `tempo_lugar_evidencia`). Contra uma Sala SEM a 033, o primeiro `pousar`
FALHA ALTO (não perde dado, mas pára a corrida). Por isso nunca nessa ordem.

## O que o pacote junta

| peça | ramo @ SHA | o que traz |
|---|---|---|
| vivo | `origin/servico-20260923-0923` @ `b607c9af` | base (MAPA-RAMO já instalado) |
| 1 mapa-ramo | `nuvem-mapa-ramo-v1` @ `59e8f0e4` | o nome do ramo sai do mapa (já no vivo) |
| 2 FECHAR-ONDA2-B | `fechar-onda2-b` @ `35e73ff9` | RETORNO.json não diz SUCCESS na falha; pasta sem `?` e sem colisão |
| 3 TEMPO-E-LUGAR + MIGRACAO-SALA | `tempo-lugar-v1` = `migracao-sala-v1` @ `b1ddd23d` | encanamento do tempo/lugar até à Sala; **033 única**; `reprocessar_tempo_lugar.py`; DA-9 |
| 4 LUGAR-FATO | `lugar-fato-v1` @ `5cad75a6` | extrator `fact_location`/`fact_time` do texto (D62/D63/D64/D69/D70) — único dono do FACT_TIME do texto (DA-6) |
| 5 tempo-publicação | `nuvem-tempo-publicacao-v1` @ `007cccf5` | `PUBLICATION_TIME` (ordem fixa DA-9: contrato 1.º, página 2.º) e `SOURCE_LOCATION` pelo contrato |
| social-tempo | `social-tempo-v1` @ `ee4eab92` | data e local de LinkedIn/YouTube com base |

**Fica FORA (e porquê):**
- **4 chaves** (`nuvem-quatro-chaves-sala-v1` @ `023727e9`): o código lê/escreve `janela_declarada`
  (a coluna já está na 033 única). Entra junto da migração quando o coordenador mandar; a 033 dela
  deixa de existir.
- **boletins** (`boletins-data-local-v1` @ `626e5813`, contém `t2-boletins-v1`): conflito de código
  em 5 ficheiros do robô — duas listas de réguas (`REGUAS_QUE_ADMITEM` social × `REGUAS_CORRENTES`
  página=boletim). À espera de uma lista única combinada pelos donos.
- A 033 da retenção YouTube passa a **034** (não está neste pacote).

## Ensaio integrado (medido 25/09 sob LOCK-PESADO; versão final 16:19–16:39, pacote `6ddcdd6d`)

Provas com texto da Sala ficam FORA do Git: `C:/Users/London1/auditoria-madrugada/pacote-tempo-lugar/`
(sha256 em `SHA256SUMS.txt` dessa pasta; os principais abaixo).

**A · 033 + reprocessamento numa CÓPIA da Sala real** (`provas/migracao_033_ensaio_copia.py`,
dump só-leitura `sala-real-copia.dump` sha256 `179b7633…d0b20`, árvore do pacote):

| passo | resultado |
|---|---|
| cadeia `migrations` | 31 × `HASH=MATCH`, `MIGRATION_033=PASS` |
| reprocesso 1 → 2 | 2.ª passagem `INSERIDAS: 0` (idempotente) |
| linhas originais da Sala | **iguais** (a correção vai só para `sala_de_espera_revisao`) |
| **saem de NÃO SEI (78 linhas)** | **publicação 36 · local da fonte 5 · data do fato 18 (2 calculadas) · local do fato 13** |
| linhas com revisão | 78 |
| DESFAZER | esquema igual ao da cópia, byte a byte; 033 volta a subir (PASS) |

`ensaio-033-pacote.json` sha256 `43cd5e9a6c04a01b2fcb61a25fa35016543c5a35ac804b12cb82bcc172c7e1ba` (1.ª versão, antes do conserto da LUGAR-FATO 5cad75a6: `ensaio-033-pacote-v1.json` `30c5e81b…`, 36/5/18/12)

**B · teste da 033 em Postgres descartável:** `tests.test_migracao_033_sala` 15/15.

**C · replay das 78 pela estrada inteira** (livro → executor → entrada → derivação → estruturação →
porta → Sala descartável), produção `b607c9af` × pacote `6ddcdd6d`:

| campo | produção | pacote |
|---|---:|---:|
| reproduzidos | 77 | 77 (a obs 9 não tem bytes guardados) |
| publicação | 0 | 35 |
| local da fonte | 0 | 4 |
| data do fato | 0 | 18 |
| local do fato | 0 | 13 |
| sem READY (descartados) | 0 | **0** |
| linhas na Sala descartável | 48 | 48 |

D62 cumprido: **nenhum item descartado por falta de dado** (mesmas 48 admitidas, 0 sem READY).
A 1.ª medida (pacote `f95df7e8`, antes da MIGRACAO-SALA) deu 3/4/18/12 — igual 3 vezes seguidas.

**D · leitura de 15 à mão** (`amostra-15-indices.json`: 5 com local do fato, 1 data calculada,
4 com data do fato, 3 com publicação, 2 tudo NÃO SEI; bases e trechos lidos):

| # | fonte | veredito |
|---|---|---|
| 1 | IT-T3-008 | **INCOERENTE** — local do fato «Puglia» vem de «scarto climatico registrato nella settimana scorsa» (lida como OCORRÊNCIA), mas a data da MESMA frase fica NÃO SEI («não fala de um acontecimento»), com a publicação provada (edição 16/09) |
| 2 | IT-T5-010 | certo — «campagna 2010», Ferrara (facto antigo, bem datado) |
| 3, 5 | IT-T5-015 | certo — workshop 12–13 nov 2026, Napoli |
| 4, 10 | IT-T5-033 | certo mas fraco — 29 set 2026; local só «Italy» (país) |
| 6 | IT-T10-018 | certo — «oggi 23 settembre 2026» (dia escrito, D64); local «Firenze» ficou de fora |
| 7 | IT-T3-010 | duvidoso — data do fato «luglio» é CONSELHO («eseguire la diagnosi… in luglio e agosto»), sem ano; publicação NÃO SEI certa (14/09 é validade) |
| 8, 9 | IT-T5-030 | data certa (8 out 2026); local «Università di Teramo» ficou de fora; e o item NÃO é agro (cibersegurança) |
| 11, 13 | IT-T3-002 | certo — edição 16/09; fato NÃO SEI |
| 12 | IT-T3-008 | certo — «scorso anno» só comparação, sem conta |
| 14, 15 | IT-T5-009 / IT-T5-011 | certo — nada na página, NÃO SEI |

**Re-leitura depois do conserto da LUGAR-FATO (`5cad75a6`, feito a partir desta amostra):** #1 data do fato 2026-09-07/2026-09-13 (RELATIVA_A_PUBLICACAO: «settimana scorsa» contada da edição de qua 16/09) — CERTO; #7 «luglio» (conselho) → NÃO SEI — CERTO; #6 local Firenze (mercado, «punti vendita») — CERTO; #8/#9 local Teramo (seminário) — CERTO; #4/#10 «Italy» → NÃO SEI (sem acontecimento ligado) — mais prudente; #2 «Ferrara ; Italia» → «Ferrara» (o país não dizia mais nada). Fora da amostra só 1 mudança (idx69, o mesmo corte do país). A incoerência e a dúvida da 1.ª leitura estão resolvidas.

Resumo da 1.ª leitura: 0 valores inventados; 1 incoerência (#1) e 1 duvidoso (#7) para a LUGAR-FATO; 3 locais que
ficaram por apanhar (conservador). Duplicados (#3/#5, #4/#10, #8/#9, #11/#13) são o mesmo documento
em corridas diferentes: saem iguais.

**E · testes (rede fechada) na árvore do pacote:** linhagem_do_ready 13/13, artefato_tempo_do_fato 14/14,
corrida_abortada 1/1, fato_do_texto 44/44, tempo_e_lugar_atravessa 43/43, tempo_e_lugar_da_publicacao 42/42,
red_team_estrada 18/18, retorno_nao_diz_success_na_falha 7/7, nome_da_pasta_windows 1/1,
soc2_curator_youtube 29/29, migracao_033_sala 15/15.
Herdados da produção (iguais em `b607c9af`): `test_estagio_atravessa_a_fronteira` 1 ERROR
(UniversoNaoDeclarado), `test_lingua_da_porta` 1 FAIL (barra do Windows), `test_collection_gate` 1 FAIL
(`onda_web.py` e `buscar_indices_d40.py` sem classificação).

## Plano de instalação (numerado)

Git Bash, nesta máquina. Nada corre sem LOCK-PESADO livre e ≥5 GB. `P` = cópia do ramo
`pacote-tempo-lugar-v1` no SHA entregue. Variáveis `S`, `VIVA`, `PATH`, `PGPASSFILE`,
`SINTONIA_SALA_DSN`, `SINTONIA_PSQL_EXE` exatamente como em `MIGRACAO-SALA.md` §3 (a DSN nunca é escrita
em log, relatório ou commit).

1. **O ficheiro certo.** `sha256sum $P/supabase/migrations/033_*.sql` = `b980c76e6b164d93fc7d293d7e7399aa0b6faa575bdbfb2ea03468095458a938`. Outro → PARAR.
2. **Preflight** (`MIGRACAO-SALA.md` passo 1) → `PREFLIGHT=PASS`. Outro → PARAR.
3. **Backup da Sala** (passo 2): `backup_sala.cmd` → `BACKUP=PASS`; anotar `B=` + `sha256sum "$B"`.
   Recomendado: `py scripts/micro_coleta/provar_backup_da_sala.py`.
4. **Parar o robô** (passo 3; `CUTOVER-RUNBOOK.md` passo 1). A consulta de processos não pode devolver
   `supervisor|worker|ponte_automatica`.
5. **Fotografia antes** (passo 4): linhas da Sala; `max(versao)` = `032`. Anotar também o vivo:
   `git -C $VIVA rev-parse HEAD` (esperado `b607c9af…`) e o carimbo do mapa.
6. **Migração 033 (UP)** pela cadeia canónica (passo 5), a partir de `$P`: 31 `HASH=MATCH` + `MIGRATION_033=PASS`.
   `MIGRATION_APLICADA_MUDOU` ou `FAIL` → PARAR (nada fica meio aplicado).
7. **SELECTs de validação** (passo 6): 5 colunas, 3 tabelas/vista, 2 gatilhos, `033|b980c76e…`,
   `count(sala_de_espera_atual)` = passo 5.
8. **Instalar o código** no vivo: `git -C $VIVA fetch origin pacote-tempo-lugar-v1` e
   `git -C $VIVA merge --ff-only <SHA entregue>` (o pacote parte de `b607c9af`: tem de ser fast-forward;
   se não for, PARAR — o vivo andou). Depois, na árvore do vivo, rede fechada:
   `py -m unittest tests.test_tempo_e_lugar_atravessa tests.test_fato_do_texto tests.test_retorno_nao_diz_success_na_falha tests.test_migracao_033_sala`
   → todos OK. Mapa: `py system-map/scripts/correr_a_cadeia.py VALIDAR` → `SYSTEM_MAP_CHECK=PASS`, carimbo IGUAL.
9. **Reprocessar o acervo — primeiro SEM escrever** (passo 7, a partir do vivo já no SHA):
   esperado com as 78: `SAEM_DE_NAO_SEI` 36 / 5 / 18 / 12. Mais linhas na Sala → números sobem (anotar).
10. **Reprocessar — ESCREVER as revisões** (passo 8): 1.ª `INSERIDAS` ≈ 455; 2.ª **`INSERIDAS: 0`** (senão PARAR).
    A linha original não muda: cada valor novo entra como revisão com base, versão do extrator e data.
11. **Validação por SELECT** (passo 9): contagem pela vista `sala_de_espera_atual` = passo 10;
    `select count(*) from sala_de_espera` = passo 5 (nenhuma linha nova, nenhuma apagada).
12. **Religar o robô** (passo 10; `CUTOVER-RUNBOOK.md` passos 8/10). Vigiar a 1.ª corrida real:
    o `pousar` escreve as colunas novas sem erro e `RETORNO.json` só diz SUCCESS quando o coletor
    não falhou.

### Desfazer

- **U1 · só o código** (a 033 fica, o código velho funciona com ela pelos defaults — provado pela
  MIGRACAO-SALA): robô parado; `git -C $VIVA reset --keep b607c9af` (depois de guardar `git status`,
  `git diff` e um stash com nome — regra da máquina); religar.
- **U2 · código e 033** (SEMPRE o código primeiro): U1, e depois `MIGRACAO-SALA.md` D1
  (`supabase/desfazer/033_desfazer.sql`, `--single-transaction`) → `schema_migracao` sem 033; as
  revisões apagam-se, as linhas da Sala ficam.
- **U3 · tudo pelo backup** do passo 3 (`MIGRACAO-SALA.md` D2: `dropdb`/`createdb`/`pg_restore "$B"`,
  preflight PASS).

## EM PALAVRAS SIMPLES

- É uma caixa com seis trabalhos já juntos: data e lugar das notícias até à Sala, o extrator do texto,
  a data de publicação, datas do LinkedIn/YouTube, o conserto do «SUCCESS» falso e o do nome da pasta.
- Primeiro a Sala ganha **gavetas novas** (só acrescenta), depois entra o código, depois arruma-se o
  que já foi colhido — sem apagar nada: cada correção fica escrita num caderno à parte.
- Numa cópia da Sala: das 78 notícias, 36 passam a ter data de publicação, 5 o lugar de quem publica,
  18 a data do fato e 13 o lugar do fato. Nenhuma foi deitada fora por falta de dado.
- Li 15 à mão: nada inventado. A LUGAR-FATO corrigiu a incoerência e a dúvida que achei; reli e estão certas.
