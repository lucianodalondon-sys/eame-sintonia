# Preservação e integração da coleta local ADAMA España — M12

Relatório de execução da missão de **preservar e integrar**. Não houve coleta nova.

| | |
|---|---|
| Branch | `claude/adama-es-local-browser` |
| HEAD de entrada | `a40e163` |
| Commits desta missão | 7 |
| Merge | **não feito** |

---

## 1 · Pré-voo — o que foi medido antes de mexer em qualquer coisa

```
BRANCH          = claude/adama-es-local-browser
HEAD_LOCAL      = a40e163   (idêntico ao remoto)
WORKTREE        = limpo
RAW_DIR_EXISTS  = YES
PDF_COUNT_LOCAL = 138
PDF_BYTES_LOCAL = 295.911.775
HASH_CHECK      = 138/138 recalculados e conferidos · 56/56 páginas conferidas
MANIFEST_ROWS   = 147  (138 DOWNLOADED + 9 FAILED)
TESTS           = 41/41 + 9 suítes OK
```

O pré-voo achou **duas divergências**, e as duas eram minhas:

**1. Números velhos em dois documentos.** O crosswalk real era 41/3/0/12 e os documentos
diziam 41/2/1/12. O brief desta missão herdou o número errado. Corrigido na seção 6.

**2. O artefato não era byte-reproduzível.** Reconstruído a partir dos mesmos bytes, ele
diferia em duas células — o texto do erro dos 9 links mortos gravava o *milissegundo* do
timeout do `curl`. A duração não é evidência de nada ali: aqueles domínios não resolvem
mais. Corrigido; duas rodadas seguidas agora produzem arquivos idênticos.

---

## 2 · Supabase — NÃO MEDIDO, e isso é o resultado

| | |
|---|---|
| `SUPABASE_AUTH_AVAILABLE` | **NO** |
| `SUPABASE_PROJECT_CONFIRMED` | **NOT_MEASURED** |
| `MIGRATIONS_APPLIED` | **NOT_MEASURED** |
| `TABLES` | **NOT_MEASURED** |
| `RAW_BUCKET_EXISTS` / `RAW_BUCKET_PRIVATE` | **NOT_MEASURED** |

Nenhuma variável de ambiente (`SUPABASE_URL`, `SUPABASE_SECRET_KEY`, `SUPABASE_DB_URL`),
sem CLI do Supabase, sem `psql`. A missão proíbe procurar segredo, então não procurei.

**Não li o comentário "NÃO EXECUTADA" dentro das migrations e chamei isso de medição.**
Um comentário diz o que alguém escreveu, não o que o banco tem.

---

## 3 · Preservação — plano fechado, envio bloqueado

| | |
|---|---|
| `RAW_ASSETS_EXPECTED` | **196** (138 PDFs + 56 páginas + 2 pacotes de captura) |
| `BYTES_LOCAIS` | 304.482.907 |
| `PROBLEMAS_ANTES_DE_ENVIAR` | **0** — hash de cada arquivo recalculado, nada diverge |
| `UPLOADED` / `VERIFIED` / `FAILED` | **0 / 0 / 0** — nada foi enviado |
| `HASH_MISMATCH` / `ORPHANS` | 0 / 0 |

Os 2 pacotes de captura entram porque sem eles o censo não se reproduz.

### A convenção é reusada, não inventada

Bucket único `raw`, país no path — a mesma do `supabase-storage.yml`. A chave dos
documentos é a que o parser **já emitia**:

```
ES/adama-website/<PRODUCT_ID>/<sha16>-<filename>
```

É **endereçada por conteúdo**: o sha16 está no nome. Duas capturas do mesmo arquivo caem
no mesmo lugar; arquivo diferente cai em outro. Sobrescrita silenciosa de conteúdo
diferente deixa de ser possível pelo formato da chave.

> `PATH != IDENTITY`. A identidade é `run_id + sha256 + metadata`, e mora em `raw_asset`.

### Cinco estados, e a distinção que importa

`PENDING` · `UPLOADED` · `ALREADY_PRESENT_VERIFIED` · `VERIFIED` · `FAILED_WITH_REASON`

**`UPLOADED` não é preservado.** HTTP 200 diz que o servidor aceitou, não que os bytes
certos chegaram. `preserved=true` só depois de baixar o objeto de volta e reconferir o
sha256. Se os bytes de volta não baterem, o uploader **para e reporta** em vez de
sobrescrever.

### Os 9 links falhos

Continuam como `DOCUMENT_REFERENCE` com `DOWNLOAD_STATE=FAILED`, código HTTP e motivo.
**Não entram no plano de preservação** — não há bytes para preservar — e o schema tem um
CHECK que impede um `FAILED` apontar para `raw_asset`. Há teste para isso.

---

## 4 · Postgres — 15 tabelas, e as leis viradas em CHECK

Migration **`010_catalogo_publico_fabricante.sql`**. Não executada.

Havia duas casas e nenhuma servia: `registro_regulatorio` guarda o que o Estado
autorizou; `disponibilidade_comercial` guarda se está sendo vendido. O que o **fabricante
publica** não era de ninguém.

> `PUBLIC CATALOG PRESENCE != REGULATORY FACT != COMMERCIAL AVAILABILITY`

As tabelas: `catalogo_captura` · `catalogo_produto` · `_documento` · `_cultivo` ·
`_agente` · `catalogo_termo_ambiguo` · `_cultivo_agente` · `_cultivo_dose` ·
`_janela_aplicacao` · `_substancia` · `_modo_acao` · `_claim` · `_tecnologia` ·
`_relacao` · `catalogo_registro_crosswalk`. RLS em todas, como na 006.

### Onde cada lei virou trava

| lei | como o banco a impõe |
|---|---|
| sem cartesiano | a âncora (tabela, linha, texto) é `NOT NULL` no par. Relação inventada de duas listas não tem linha de origem para declarar — **não entra** |
| dose ≠ par | tabela separada, **sem coluna de agente**, e `par_derivavel` com `CHECK = false` |
| declarado ≠ citado | `origem_declaracao` `NOT NULL` com dois valores. Colapso impossível |
| fato regulatório | só existe com `confirmacao_mapa = CONFIRMED`, e confirmado **exige os ids da consulta**. "O MAPA confirmou" sem os ids é frase |
| link falho | `FAILED` não pode apontar `raw_asset` e exige código + motivo |
| código de MOA | `CHECK` de forma: `^[A-Z0-9]{1,4}(/[A-Z0-9]{1,4})?$`. "FRAC Grupo" não entra |
| match exato | exige número de registro. Nome comercial sozinho não fecha |
| crosswalk | é **relação**, não coluna. Fundir as entidades autorizaria `96 − 56` |
| substância | `texto_publicado` e `nome_normalizado` convivem; normalizar exige declarar a regra |
| disponibilidade | `catalogo_produto` **não tem** essa coluna. Se tivesse, alguém preencheria SIM por estar no catálogo |
| baseline | `capturado_em` e `importado_em` separados, com CHECK de ordem, e `e_baseline` |

---

## 5 · Importador — SQL auditável, não processo opaco

`supabase/importacoes/ADAMA-ES-CATALOGO-2026-08-30.sql` — **1.814 comandos, 949 KB.**
Não aplicado.

| tabela | linhas |
|---|---|
| produtos | 56 |
| documentos | 147 |
| cultivos | 711 (588 declarados + 123 citados) |
| agentes | 176 |
| termos ambíguos | 210 |
| pares cultivo × agente | 5 |
| cultivo × dose | 26 |
| janelas de aplicação | 3 |
| substâncias | 73 |
| modos de ação | 17 |
| claims | 35 |
| tecnologia / relação | 1 / 1 |
| crosswalk | 108 (56 do catálogo + 52 ROPF-only) |
| **raw_asset** | **0** |

**`raw_asset = 0` é a resposta certa, não um buraco.** Documento só aponta para bytes
preservados depois de `VERIFIED` no Storage. Preencher o ponteiro agora seria dizer que o
byte está preservado quando está numa máquina só.

Gera SQL em vez de falar direto com o banco de propósito: o SQL entra no Git, alguém lê
antes de rodar, e o mesmo arquivo pode ser aplicado por qualquer via. Importador que só
existe como processo não deixa rastro do que fez.

Idempotência: todo `INSERT` tem `ON CONFLICT DO NOTHING` sobre chave **natural**; a
captura é única por `(pais, fabricante, fonte_versao)`. Não há `update`, `delete` nem
`upsert`. Fonte nova entra como **captura nova, ao lado** — histórico não se reescreve.

---

## 6 · O defeito que a preparação do banco revelou

Preparando as linhas, **quatro chaves naturais colidiram**. Se eu tivesse importado assim,
o `ON CONFLICT` teria derrubado as duplicatas em silêncio e o round-trip diria 711 no
banco contra 717 no Git, sem ninguém saber por quê.

A causa é notação da fonte. O MAPA escreve rótulo composto — `"BATATA, BONIATO"` — e a
vírgula separa nome comum de nome comum. O parser já gerava dois apelidos para o **mesmo**
rótulo oficial, o que está certo e é o que faz a página casar dizendo qualquer uma das
palavras. Faltava: quando a página diz **as duas**, o mesmo rótulo casava duas vezes.

| | inflado | verdadeiro |
|---|---|---|
| CROP_RELATIONS | 717 (594+123) | **711 (588+123)** |
| ISSUE_RELATIONS | 184 | **176** |
| MODES_OF_ACTION | 19 | **17** |
| AMBIGUOUS_TERMS | 212 | **210** |

Nenhum apelido se perde: viram `MATCHED_AS_ALL` na própria relação. O crosswalk não muda:
**41 + 3 + 0 + 12 = 56**.

---

## 7 · Round-trip

**20 testes.** 18 passam agora; 2 **pulam declarando o que falta** — não passam por
omissão.

| elo | estado |
|---|---|
| Git ↔ linhas normalizadas | **PASS** — 56 produtos, 4 categorias, 12 estruturas inteiras |
| disco ↔ manifesto | **PASS** — 138 arquivos, hash recalculado, 0 divergência |
| manifesto ↔ plano | **PASS** — 0 órfão dos dois lados |
| SQL ↔ idempotência | **PASS** — sem update/delete/upsert; ON CONFLICT em toda chave natural |
| SQL ↔ segredo | **PASS** — nada que pareça credencial no arquivo versionado |
| disco ↔ Storage | **PENDENTE** — falta `SUPABASE_URL` + `SUPABASE_SECRET_KEY` |
| Git ↔ Postgres | **PENDENTE** — falta `SUPABASE_DB_URL` + `psql` |

Cinco leis viradas em teste: milho declarado não soma com citado (15 + 20 nunca vira 35) ·
dose nunca ganha coluna de agente · todo par carrega âncora · confirmação do MAPA
atravessa com os ids que a produziram · `"NÃO SEI"` vira `NULL` (guardar a string faria
`where ... is null` mentir).

Um defeito **do teste**, achado por ele mesmo: eu fatiava o SQL no primeiro `;`, e há `;`
dentro de literal (`application/pdf; length=127023`). O corte caía antes do `ON CONFLICT`
e o teste acusou quatro tabelas inocentes.

### As 14 perguntas (§24)

Escritas como SQL em `supabase/consultas/ADAMA-ES-CATALOGO-14-PERGUNTAS.sql`, com a
resposta **esperada** em comentário, calculada das mesmas linhas que o importador vai
inserir. **Esperado não é medido**, e o arquivo diz isso na primeira linha.

Pergunta 14 — `CURRENT_COMMERCIAL_AVAILABILITY` — continua `NAO_SEI` para os 56, e não
por convenção: **por construção**, porque a coluna não existe naquela tabela.

---

## 8 · Entrega

**A · REPO** — branch `claude/adama-es-local-browser` · 7 commits · pushed · 385 testes,
13 suítes, 0 falha (2 pulam por falta de credencial, declarando o motivo).

**B · PRÉ-VOO** — 138 PDFs · 295.911.775 bytes · 138/138 hashes conferem · 147 linhas de
manifesto.

**C · SUPABASE** — `AUTH_AVAILABLE = NO`. Tudo o mais: `NOT_MEASURED`.

**D · STORAGE** — 196 esperados · 0 enviados · 0 verificados · 0 falhos · 0 órfãos.

**E · POSTGRES** — migration 010 escrita, 15 tabelas, não executada. 1.814 comandos
gerados, não aplicados.

**F · CROSSWALK** — 41 exatos + 3 com evidência + 0 ambíguos + 12 só-site = **56**.
Partição fecha. ROPF-only: 52.

**G · PROVENIÊNCIA** — `RUN_ID = ES-M12-IMPORT-CATALOGO-ADAMA-2026-08-30-a` ·
`CAPTURED_AT = 2026-08-30T03:19:24Z` · `IMPORTED_AT = now()` na aplicação ·
`SOURCE_VERSION` = a hora da captura · `RAW_ASSETS_LINKED = 0`.

**H · CONSISTÊNCIA DOCUMENTAL** — relatório de execução carimbado com o que mudou e por
quê; entrega canônica corrigida; **0 número velho restante**.

**I · PRONTIDÃO**

| | |
|---|---|
| `ADAMA_ES_PUBLIC_CATALOG_COMPLETE` | **YES** |
| `ADAMA_ES_RAW_PRESERVED` | **NO** — bloqueado por credencial |
| `ADAMA_ES_DOCUMENTS_PRESERVED` | **NO** — bloqueado por credencial |
| `ADAMA_ES_POSTGRES_INTEGRATED` | **NO** — bloqueado por credencial |
| `SAFE_FOR_MAIN_TO_MERGE` | **YES** — nada aplicado remotamente, tudo reversível |
| `READY_TO_PARSE_55_LABELS` | **NO** — a missão manda fechar preservação antes |

**BLOCKER — um só:** não há autenticação Supabase nesta máquina.

```bash
export SUPABASE_URL=... SUPABASE_SECRET_KEY=... && python3 scripts/storage_preservar.py --enviar
```

**NEXT_SMALLEST_STEP:** esse comando. Ele sobe os 196 assets, baixa cada um de volta,
reconfere o sha256 e escreve o relatório. Depois dele, o import tem `raw_asset` para
apontar e os dois testes pendentes viram verdes.

---

## 9 · O que continua verdade, e o que não

Não mudou nada no que a coleta afirma: **56 produtos · 138 documentos · 5 pares
confirmados no registro oficial**. O que mudou foi a leitura das relações, que estava
inflada, e a infraestrutura ao redor, que não existia.

E continua valendo o que a coleta **não** prova: estoque · venda · distribuição · market
share · receita · prioridade interna da ADAMA.

⚠️ **Os 296 MB ainda existem numa máquina só.** Manifesto com sha256 não é backup.
