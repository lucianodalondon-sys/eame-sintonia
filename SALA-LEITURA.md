# SALA-LEITURA — D9 e D10

Missão SALA-LEITURA-D9-D10 · 26/09/2026 · ramo `sala-leitura-v1` a partir do vivo `83de0ccd`.
**NÃO instalado.** Vivo não tocado. Sala real não tocada nesta missão. Sem rede.

## 0 · Em uma linha

D9: quem pedia «só leitura» à Sala era ignorado em silêncio — agora o pedido chega ao banco, e há um modo
leitura que **prova** que a transação é de leitura. D10: `ler_atual()` passa a entregar o item inteiro
(o READY do dono) com as revisões, em vez de meio item.

## 1 · D9 — o só-leitura pedido não chegava ao banco

**Antes** (`admissao/sala_de_espera.py:458-466` em `83de0ccd`):

```python
return dict(os.environ, PGOPTIONS="-c standard_conforming_strings=on")
```

O `PGOPTIONS` de quem chamava era **substituído**. A micro_coleta (`scripts/micro_coleta/micro_coleta.py:356`)
e quem mais pedisse `-c default_transaction_read_only=on` acreditava estar a ler em modo leitura, e a
sessão vinha de escrita.

**Depois:**
1. As opções do chamador são **acrescentadas**: `"<do chamador> -c standard_conforming_strings=on"`.
   A do dono vem por último, porque no `-c` repetido ganha o último — o escape de `_lit()` não pode ser
   desligado por fora (teste `test_o_escape_do_dono_vem_por_ultimo_e_ganha`).
2. **Modo leitura** (`SINTONIA_SALA_SO_LEITURA=1`, ou `_Postgres(url, so_leitura=True)`):
   - cada leitura corre em `begin read only; show transaction_read_only; <pergunta>; commit;` e a
     resposta só é devolvida se o banco disser **`on` na mesma transação**; senão levanta
     `SalaIndisponivel`;
   - cada escrita começa por `set transaction read only;` — **quem recusa é o banco**, não o Python.
   Porquê SQL e não só `PGOPTIONS`: `provas/auditoria_live.sh:326` mediu que o `PGOPTIONS` foi
   **ignorado em silêncio** por um pooler no banco vivo (`READ_ONLY_SESSION=off`). `begin read only`
   atravessa pooler.
3. **Fora do modo leitura e sem `PGOPTIONS` do chamador, a escrita é byte a byte a mesma**
   (`test_fora_do_modo_leitura_a_escrita_nao_muda`; `test_P2_...`). A Admission não muda.

⚠️ **Risco declarado para a instalação:** se o processo do robô (supervisor/observador) tiver um
`PGOPTIONS` de leitura no ambiente, hoje ele é deitado fora e o robô escreve; **depois desta mudança o
robô deixaria de conseguir escrever**. Não encontrei no repositório quem ponha `PGOPTIONS` no ambiente do
robô (`git grep PGOPTIONS`: só a micro_coleta, os medidores e as guardas de banco), mas o ambiente do
processo vivo **não foi medido**. Passo 2 do plano mede-o.

## 2 · D10 — `ler_atual()` entregava meio item

**Antes:** `ler_atual()` devolvia 21 campos próprios, **sem** ESTADO, SOURCE_DECLARED_EVIDENCE_CLASS,
FATO, CORRIDA e ADMITIDO_POR. `ler()` tinha-os, mas sem as revisões. E cada um tinha a **sua** lista de
colunas escrita à mão.

**Depois:**
- Uma só ponte coluna → campo do contrato: `_COLUNA_DO_CAMPO`, `_COLUNAS_DO_READY` (derivado de
  `CAMPOS_READY`, a lista do dono) e `_para_ready()`. **`ler` e `ler_atual` usam as duas a mesma** —
  nenhuma segunda cópia de campos. Um teste (`test_a_ponte_cobre_o_contrato_inteiro`) reprova se o
  contrato ganhar um campo sem coluna.
- `ler_atual()` devolve, por item: os 23 campos de `CAMPOS_READY` **na ordem do dono**, já com as
  revisões aplicadas (pela vista `sala_de_espera_atual`), mais `ORDEM`, `JANELA_DECLARADA`, `REVISOES`
  (o número, como antes — compatível com `tests/test_migracao_033_sala.py`) e **`HISTORICO_DE_REVISOES`**
  (cada revisão: campo, valor, base, extrator, versão, quando, motivo; da mais antiga à mais nova).
- `ler()` continua a devolver o que **pousou** (sem revisões): é com ele que `pousar` separa um retry de
  um conflito (`test_D10d_o_retry_continua_a_ser_retry`).

## 3 · Testes — `tests/test_sala_leitura_d9_d10.py`

| grupo | teste | prova |
|---|---|---|
| sem banco | as_opcoes_do_chamador_sao_acrescentadas | D9: o pedido do chamador sobrevive |
| sem banco | o_escape_do_dono_vem_por_ultimo_e_ganha | `standard_conforming_strings=off` de fora não vence |
| sem banco | sem_pgoptions_do_chamador_fica_so_o_do_dono | igual a antes |
| sem banco | modo_leitura_sem_confirmacao_do_banco_levanta | banco diz `off` → nada é devolvido |
| sem banco | modo_leitura_embrulha_a_pergunta_em_begin_read_only | a prova vem antes da pergunta |
| sem banco | fora_do_modo_leitura_a_escrita_nao_muda | o script de escrita é o mesmo |
| sem banco | a_ponte_cobre_o_contrato_inteiro | D10: nenhum campo do dono sem coluna |
| **NEGATIVO** | N1 PGOPTIONS só-leitura do chamador | `pousar` **recusado pelo banco** (`read-only`), 0 linhas novas — **antes pousava** |
| **NEGATIVO** | N2 modo leitura recusa `pousar` | recusado pelo banco, 0 linhas novas |
| **NEGATIVO** | N3 modo leitura recusa `rever` | recusado, 0 revisões novas |
| banco | P1 modo leitura lê e prova `on` | `ler` e `ler_atual` funcionam em modo leitura |
| banco | P2 fora do modo leitura pousa | a escrita da Admission continua |
| banco | D10a/b/c/d | READY inteiro na ordem; igual a `ler` sem revisão; revisão + histórico; retry continua retry |

Mutantes: S1 volta a deitar fora o PGOPTIONS · S2 tira `set transaction read only` da escrita ·
S3 deixa de conferir o `on` · S4 `ler_atual` perde o histórico.

### 3.1 · Resultados

- **Sem banco: 7/7 OK** (corrido 26/09 ~02:20, trabalho leve).
- `tests/test_a_sala_de_espera_nao_tem_morada.py`: **2 falhas, as mesmas na base `83de0ccd`** sem a
  minha mudança (`test_a_morada_em_SQL_e_exactamente_UMA_e_declarada`,
  `test_os_dezanove_campos_estao_la_e_na_ordem`) — herdadas, não desta missão.
- `tests/test_psql_argv.py`: 6/6 OK.
- Com banco (N1–N3, P1–P2, D10a–d), regressões 033/idempotente e mutantes S1–S4:
  PENDENTE_RESULTADOS_BANCO

## 4 · Juntar com o `dedup-doc-v1` (os dois mexem em `admissao/sala_de_espera.py`)

Mexem em sítios diferentes: DEDUP-DOC só no `insert` de `pousar` (e num comentário); SALA-LEITURA em
`_ambiente_psql`, `_Postgres.__init__`, `_consultar`, `_executar`, `ler`, `ler_atual` e um bloco novo
antes de `class _Postgres`. `git merge-tree --write-tree sala-leitura-v1 origin/dedup-doc-v1` →
**sem conflito** (medido, 26/09 02:21). Ordem sugerida: instalar os dois juntos, ou qualquer um primeiro —
um `git merge` do segundo sobre o primeiro basta.

## 5 · Plano de instalação (NÃO executado — só o coordenador instala)

1. LOCK-PESADO + ≥ 5 GB. Robô, supervisor e observador parados.
2. **Medir o ambiente do robô:** `PGOPTIONS` e `SINTONIA_SALA_SO_LEITURA` no processo vivo (e no script
   que o arranca). Se algum pedir leitura, **não instalar** até decidir (com esta mudança, o pedido passa
   a valer e a escrita pararia).
3. Backup do código (`/c/inst/<data>-sala-leitura`). A Sala não precisa de backup: **sem migration**.
4. No vivo (`83de0ccd` ou o que estiver): `git merge --ff-only origin/sala-leitura-v1` (ou merge normal se
   o DEDUP-DOC já entrou).
5. Correr no SHA instalado: `tests/test_sala_leitura_d9_d10.py`, `tests/test_migracao_033_sala.py`,
   `tests/test_sala_idempotente_por_documento.py`, `tests/test_psql_argv.py`.
6. Prova na Sala real, **só leitura**: `SINTONIA_SALA_SO_LEITURA=1` e `ler_atual(<um run_id>)` → itens com
   23 campos + histórico; a contagem da Sala igual antes e depois.
7. Religar. **Desfazer:** `git revert` do commit; nada no banco.
