# EMENDA EXP-D78 — EXCEÇÃO EXPERIMENTAL DA INTELLIGENCE (PROPOSTA)

```text
EMENDA_ID        = EXP-D78
REVISAO          = R2 (26/09 ~02:40) — 3 correções obrigatórias do bot Luciano
                   (auditoria-madrugada/bot-luciano-resp-emenda.txt): ver secção 0.
                   A R1 é o commit 7724687d; nada dela foi apagado sem aviso.
ALVO             = BIBLIA-DE-ENGENHARIA-DA-INTELLIGENCE.md V0.3 (CANONICAL)  →  V0.4 se aprovada
ESTADO           = PROPOSTA — NÃO APLICADA. A Bíblia V0.3 continua a ser a lei até o dono aprovar.
ORIGEM           = D78 do dono real (25/09 23:16, DECISOES-DONO-2026-09-23.md)
REDIGIDA_POR     = sintonia-intelligence-owner, a pedido do coordenador (ordem 25/09 23:40)
RAMO             = int-sala-exp-v1 (a partir do vivo ce28040c) — NÃO é a linha canónica
APROVA           = o dono real. Entra na linha canónica só pelo caminho normal (Control Plane).
```

> Esta emenda **não** relaxa lei nenhuma. Ela cria um modo novo, estreito e com
> prazo de validade, para a Intelligence **se testar a si própria** sobre material
> real, e continua a proibir tudo o que a secção 28 proíbe.
>
> ```text
> EXCEÇÃO EXPERIMENTAL  !=  TRAVA ABERTA
> ACHAR DEFEITOS        !=  PRODUZIR INTELLIGENCE PARA CLIENTE
> ```

---

## 0 · O QUE A R2 MUDOU (as três correções obrigatórias)

| # | correção pedida | onde ficou |
|---|---|---|
| C-a | a FASE 1 só corre com D1–D4 e D6–D10 **corrigidos e testados** | 32-A.0 (pré-condições) e secção 3 |
| C-b | provar `transaction_read_only = on` **na transação real** (`SHOW transaction_read_only` dentro da transação de leitura), não só `default_transaction_read_only`; D9 corrigido **no dono (Collection)** é pré-requisito | 32-A.2(1) |
| C-c | fotografia antes/depois = contagens **+ impressões determinísticas dos registos** (hash ordenado por chave de cada tabela) | 32-A.2(2) |
| + | a linha da trava cita o **commit/blob imutável** da emenda aprovada | 1.1 |

---

## 1 · O CONFLITO QUE A EMENDA RESOLVE (medido, não presumido)

| autoridade | o que diz | medido em `ce28040c` |
|---|---|---|
| Bíblia V0.3, cabeçalho | `IMPLEMENTATION_AUTHORIZED = SOMENTE_A_PRIMEIRA_MISSAO_DA_SECAO_32_E_SUJEITA_AOS_GATES_UPSTREAM` | igual |
| Bíblia V0.3, §32 | a missão «continua a não poder correr» pelos gates a montante, «que não são desta Bíblia para abrir» | igual |
| `docs/operacao/TRAVA-DA-INTELIGENCIA.json` (dono: Collection) | `COLLECTION_FOUNDATION_CLOSED = NAO` · critérios cumpridos C, D, F, K, L · faltam A, B, E, G, H, I, J, M, N | 5/14 |
| `system-map/data/estradas-it.generated.json` (último toque `677b7f62`, 25/09 17:58) | `COLLECTION_FOUNDATION_CLOSED = false` · `ROUTE_CLASSES_ARCHITECTURE_CLOSED = []` · `ROUTE_CLASSES_REQUIRED_TOTAL = UNKNOWN` | igual |
| `leis/fundacao_da_coleta.py` | `AREAS_CONGELADAS` inclui `SIGNALS`; `PERMITIDO_LER = INTELLIGENCE_READ_ALLOWED` | igual |
| D78 (dono real) | «se já tem material com data ela já pode começar a trabalhar, achar seus erros, entender o que precisa fazer» | decisão escrita |

**Conclusão:** a D78 pede uma coisa que a letra da Bíblia hoje não permite. A
Bíblia manda que isso vire emenda, não interpretação. Esta é a emenda.

### ⚠️ 1.1 · A emenda sozinha NÃO chega — segundo conflito, de owner

A trava **não é desta Bíblia**: o dono dela é a Collection
(`leis/fundacao_da_coleta.py` → `TRAVA-DA-INTELIGENCIA.json`). A Bíblia da
Intelligence pode dizer o que **ela** se permite; não pode abrir o portão de
quem vem antes (V0.3: «AUTORIZAR A OBRA != DESTRANCAR O PORTÃO DE QUEM VEM ANTES»).

Por isso a aprovação precisa de **duas assinaturas escritas do dono real**, ou de
uma que nomeie as duas:

1. esta emenda (lado Intelligence), **na versão imutável aprovada**;
2. uma linha no contrato da trava (lado Collection, pelo dono dela) acrescentando
   a `O_QUE_A_TRAVA_NAO_IMPEDE`:

   ```text
   «execução EXPERIMENTAL só-leitura da Intelligence, nos termos da
    EMENDA EXP-D78 aprovada: commit <SHA-DO-COMMIT-APROVADO>,
    blob docs/intelligence/EMENDA-EXP-D78-EXCECAO-EXPERIMENTAL.md = <GIT_BLOB_SHA>»
   ```

   — **sem** mudar `COLLECTION_FOUNDATION_CLOSED`, que continua `NAO`. Citar o
   commit **e** o blob (o nome que o Git dá ao conteúdo) impede que uma edição
   posterior da emenda herde a assinatura: texto novo = blob novo = assinatura
   que não bate.

Sem a 2, a FASE 1 continua bloqueada. Não sou eu que a escrevo: não sou o dono
da trava.

---

## 2 · O TEXTO PROPOSTO — nova secção «32-A», a inserir depois da §32

### 32-A. EXCEÇÃO EXPERIMENTAL EXP-D78

**Pergunta:** a máquina de Intelligence que já existe aguenta material real
admitido? Onde ela quebra, lê mal ou fabrica? O que ela precisa da Collection?

**Objetivo único:** achar **defeitos da Intelligence** e escrever **pedidos
para a Collection**. Não é objetivo produzir sinal, achado ou oportunidade.

#### 32-A.0 · Pré-condições — TODAS, antes de qualquer leitura da Sala (C-a)

```text
P1  as duas assinaturas escritas do dono (1.1), citando commit + blob desta emenda;
P2  D1–D4, D6–D8 (lado Intelligence) corrigidos, com teste negativo, contraprova
    e mutação apanhada, e INTEGRADOS na linha de onde a FASE 1 corre;
P3  D9 e D10 (lado Collection) corrigidos PELO DONO da Sala, integrados primeiro;
    depois a Intelligence é re-provada contra essa fronteira nova;
P4  a prova de só-leitura na transação real (32-A.2(1)) e a fotografia com
    impressões (32-A.2(2)) existem como código testado, não como promessa.
Falta uma → NOT_RUN. Nenhuma é dispensável por urgência.
```

#### 32-A.1 · Entrada (INT-LAW-010, INT-LAW-100)

```text
ENTRADA   = só itens ADMITIDOS/READY da Sala de Espera canónica (PostgreSQL),
            estado_da_fila = WAITING, lidos pelo dono da Sala
            (admissao/sala_de_espera.py) — ler_atual() / ler().
ELEGÍVEL  = item com DATA DO FATO válida:
              FACT_TIME       != vazio, != NAO SEI*, != UNKNOWN*
              FACT_TIME_BASIS != vazio, != NAO SEI*, sem UNKNOWN
PUBLICAÇÃO NUNCA SUBSTITUI DATA DO FATO para tornar um item elegível.
Itens só com PUBLISHED_AT entram na FASE 2 apenas como MEDIÇÃO
(«quantos têm só publicação»), nunca como item ancorado no tempo.
ENTRADA B = referencia/adama/ — ler e citar, nunca escrever.
```

#### 32-A.2 · Travas técnicas obrigatórias (não são promessa: são verificadas)

1. **Só-leitura provado NA TRANSAÇÃO REAL (C-b).** Pedir não é provar, e provar
   a configuração por omissão também não é provar a transação:

   ```text
   BEGIN READ ONLY;                        -- a leitura abre-se assim, sempre
   SHOW transaction_read_only;             -- tem de devolver «on», DENTRO dela
   ... todas as leituras da corrida, nesta mesma transação ...
   COMMIT;
   ```

   `SHOW default_transaction_read_only` sozinho **não conta**: diz o valor por
   omissão da sessão, não o da transação onde a leitura aconteceu. Qualquer
   `SHOW transaction_read_only` ≠ `on` → aborta, `INVALID`, nada é lido.
   ⚠️ Medido: o dono da Sala (`_ambiente_psql()`) **sobrescreve** `PGOPTIONS`;
   o só-leitura de quem chama não chega ao banco (D9). **O conserto é do dono
   (Collection) e é pré-requisito (32-A.0 P3)** — a R1 admitia contorná-lo em
   processo pela Intelligence; a R2 retira essa via: a Intelligence não remenda
   o leitor de outro owner.
2. **Fotografia antes/depois com IMPRESSÕES (C-c).** Contagens iguais não
   detetam um valor alterado, nem uma linha trocada por outra. Por cada tabela
   (`sala_de_espera`, `sala_de_espera_revisao`, `raw_asset`, `storage_object`,
   `derived_artifact`, `collection_run`):

   ```text
   CONTAGEM   = count(*)
   IMPRESSAO  = sha256 da concatenação, ORDENADA PELA CHAVE PRIMÁRIA da tabela,
                de uma representação canónica de cada linha inteira
                (ex.: md5(row_to_json(t)::text) por linha, ordenado por chave,
                 agregado com string_agg ... order by <chave>)
   ```

   Antes = depois nas duas grandezas, em todas as tabelas, ou o resultado é
   `INVALID`. A chave de ordenação de cada tabela é declarada por escrito antes
   de correr (vem do schema do dono, não é escolhida pela Intelligence).
3. **Zero chamadas a coletor, zero rede.**
4. **Saída fora do Git**, em
   `C:/Users/London1/sintonia-sala-italia/intelligence-experimental/<RUN_ID>/`,
   marcada `EXPERIMENTAL / NAO_PARA_CLIENTE` em cada ficheiro.
5. **Motor existente, sem motor novo**: `motor/corrida_da_inteligencia.py`
   (e, na FASE 2, a lógica do piloto `origin/claude/int-pilot-sala-v1`).
6. Todo `SIGNAL` emitido é `EXPERIMENTAL_CANDIDATE`: não é persistido em canal
   canónico, não é consumido por Tool, Casco ou Portal. (Isto é o que torna a
   exceção compatível com `AREAS_CONGELADAS ∋ SIGNALS`: nada liga sinais ao sistema.)

#### 32-A.3 · Sequência (cada fase termina em HARD STOP)

```text
FASE 1 = a própria §32: 1 item real elegível (regra escrita ANTES de ver a Sala)
         → 1 INTELLIGENCE_RUN identificado → lineage provada
         → sem coleta direta → sem julgamento fabricado → HARD STOP + relatório.
FASE 2 = só depois de o coordenador aceitar a FASE 1:
         lote = TODOS os elegíveis de 32-A.1 (número medido na hora, não presumido),
         mesma corrida identificada, mesmas travas → 5 perguntas + lista de defeitos
         + pedidos à Collection → HARD STOP.
```

#### 32-A.4 · O que continua proibido (a secção 28 fica INTACTA)

Tudo da §28, e mais, dentro desta exceção:

- escrever na Sala, na Admission, no READY, nas fontes, na Collection ou no Portal;
- pontuar, recomendar, publicar ou mostrar a cliente;
- promover `SIGNAL → FINDING → OPPORTUNITY` (máximo: candidato experimental);
- correlação virar causa; preencher `UNKNOWN`; relaxar gate;
- diagnóstico agronómico sem família T3;
- instalar código no vivo; alterar o motor durante a corrida;
- chamar coletor — gaps saem como `COLLECTION_GAP` escritos e vão pela
  Collection canónica (INT-LAW-020), sem escolher rota, fonte ou coletor.

#### 32-A.5 · O que sai (e o que conta como sucesso)

- livro do `INTELLIGENCE_RUN` (identidade, versões efetivas, entradas, estado);
- lista de **defeitos da Intelligence** com prova (item, campo, esperado, obtido);
- lista de **pedidos à Collection** (fonte/classe/campo que falta);
- respostas às 5 perguntas, onde `NO_DEFENSIBLE_ACTION_YET`, `UNKNOWN` e
  `NOT_POSSIBLE` são respostas válidas (INT-LAW-012).

Sucesso **não** é ter sinais. Sucesso é a corrida existir, ser reproduzível,
ter lineage e **recusar-se a fabricar**.

#### 32-A.6 · Validade

A exceção **caduca** quando acontecer o primeiro destes:
(a) `COLLECTION_FOUNDATION_CLOSED = SIM` pelo seu dono — aí vale a §32 normal;
(b) revogação escrita do dono; (c) a FASE 2 fechar — nova fase exige nova decisão.

---

## 3 · DEFEITOS JÁ PROVADOS SEM ABRIR O BANCO (motivam as travas acima)

Prova: `provas_offline.py` na pasta experimental — chama as funções reais do
repositório, sem banco e sem rede. Suíte do motor em `ce28040c`:
`test_espinha_da_intelligence.py` + `test_a_primeira_corrida_da_inteligencia.py`
= **78 passed, 31 subtests** — e todos os defeitos abaixo passam despercebidos a ela.

| ID | peça | esperado (autoridade) | obtido |
|---|---|---|---|
| D1 | `portao_g0` | `FACT_TIME = "UNKNOWN"` bloqueia (INT-LAW-112) | **passa** — `e_ignorancia` só conhece `NAO SEI`; na tabela `sala_de_espera` (contagem agregada lida às ~23:2x, ANTES da ordem de paragem) 12 linhas têm `fact_time_basis` a começar por «o coletor declarou: «UNKNOWN…» |
| D2 | `portao_g0` | valor sem base provada não ancora (INT-LAW-062) | `FACT_TIME="2025"` com base `NAO SEI` **passa** |
| D3 | `portao_g0` | data sem ano não é âncora (INT-LAW-100) | `"21-23 ottobre"` **passa** |
| D4 | `portao_g0` | evento futuro ≠ facto ocorrido (§28: FUTURE DATE ≠ FORECAST ≠ FACT) | `"20-22 aprile 2027"` **passa** e vira SINAL |
| D5 | `portao_g0` | PUBLISHED_AT não vira FACT_TIME | **correto** (contraprova positiva: bloqueia) |
| D6 | `correr` → SIGNAL | sinal carrega a base de tempo/lugar | copia `FACT_LOCATION` **sem** `FACT_LOCATION_BASIS` nem precisão |
| D7 | motor | carimbo = Bíblia efetiva (INT-LAW-052) | `BIBLE_VERSION = "V0.2 CANONICAL"`; a lei é V0.3 |
| D8 | `espinha` vs dono da Sala | uma cópia do contrato que acompanha o dono | espinha 19 campos, dono 23; faltam `PUBLISHED_AT_BASIS`, `SOURCE_LOCATION_BASIS`, `COMPLETUDE_TEMPO_LUGAR`, `TEMPO_LUGAR_EVIDENCIA` — e o teste **fixa 19**, por isso não avisa |
| D9 | `sala_de_espera._ambiente_psql` (owner: Collection) | só-leitura pedido pelo chamador chega ao banco | `PGOPTIONS` **sobrescrito** → `-c standard_conforming_strings=on` |
| D10 | `ler_atual()` (owner: Collection) | a vista para a Intelligence entrega o READY inteiro | não devolve `ESTADO`, `SOURCE_DECLARED_EVIDENCE_CLASS`, `FATO`, `CORRIDA`, `ADMITIDO_POR`; `ler()` devolve estes mas **sem** as revisões |

D1–D4 fazem a §32, corrida hoje, **produzir SINAL a partir de datas que não
ancoram o facto**. Por isso 32-A.2(6) marca todo sinal como candidato
experimental.

### 3.1 · Estado dos consertos (R2)

| ID | owner | estado | onde |
|---|---|---|---|
| D1–D4, D6–D8 | Intelligence | **CORRIGIDO EM RAMO, com teste negativo + contraprova + mutação apanhada; NÃO integrado, NÃO instalado** | ramo `int-consertos-v1` (a partir do vivo `83de0ccd`) — commit citado no relatório da missão INT-CONSERTOS-EXP |
| D9, D10 | Collection | **POR FAZER pelo dono** (bancada DEDUP-DOC, ramo `sala-leitura-v1`) | pré-requisito P3 |

Enquanto uma linha desta tabela não estiver integrada, 32-A.0 dá `NOT_RUN`.

---

## 4 · RED TEAM DA PRÓPRIA EMENDA

| ataque | onde morre |
|---|---|
| «experimental» usado para alimentar o Casco | 32-A.2(4)(6) + 32-A.4: nada sai do diretório experimental; Casco só lê artefato marcado e **não** pode mostrar a cliente |
| publicação usada para tornar item elegível | 32-A.1: elegibilidade exige FACT_TIME **e** base |
| «só leitura» só declarado | 32-A.2(1): `SHOW transaction_read_only` **dentro** da transação de leitura; D9 prova que o pedido do chamador não bastava |
| «só leitura» provado na sessão e não na transação | 32-A.2(1): `default_transaction_read_only` não conta |
| conteúdo alterado com contagem igual | 32-A.2(2): impressão por linha, ordenada por chave |
| assinatura da trava herdada por uma emenda editada depois | 1.1: a linha cita commit **e** blob |
| FASE 1 a correr com o G0 antigo (D1–D4) | 32-A.0 P2 |
| FASE 1 esticada para lote | 32-A.3: HARD STOP entre fases |
| exceção que nunca caduca | 32-A.6 |
| emenda da Intelligence a abrir o portão da Collection | 1.1: exige a linha do dono da trava |
| gate a passar com entrada vazia (§28) | nenhum elegível → `NOT_RUN`, não PASS |

## 5 · COLISÕES VERIFICADAS

- §28: nenhuma linha removida ou atenuada.
- §32: continua a ser a primeira missão; a FASE 1 **é** a §32.
- Collection Bible / TRAVA: não alteradas por esta emenda; dependência declarada em 1.1.
- Concept ownership: nenhum conceito novo com owner novo; `EXPERIMENTAL_CANDIDATE`
  é um estado de um `SIGNAL` já existente, não um objeto novo.
