# A CASA DO DERIVADO — a única tabela que sobreviveu à medição

**Censo, desenho e prova** · 2026-09-08 · ramo `claude/italia-biblia-integracao-v1`

> **Nada foi aplicado em produção.** 0 migrations aplicadas, 0 escritas, 0 uploads, 0 deletes,
> 0 backfill, 0 corridas retrocriadas. A `022` foi aplicada e provada num **Postgres 16 que
> morre no fim do job**.

---

## A · O CENSO VEIO PRIMEIRO

Quatro missões apontaram para `derived_artifact`. Isso não autoriza desenhá-la de cabeça —
**desenhar primeiro e medir depois é medir o buraco pelo tamanho da tampa já comprada.**

Medido em [`censo_das_derivacoes.py`](../../system-map/scripts/censo_das_derivacoes.py):

```
7 produtores medidos      e só 3 são de espécie DERIVED_ARTIFACT
2 ferramentas de derivação    texto-de-pdf · whisper
2 tipos reais hoje            texto simples · transcrição
```

### A armadilha: chamar tudo de derivado

| o quê | espécie | por quê |
|---|---|---|
| `executor_texto_de_pdf.py` → TXT | **`DERIVED_ARTIFACT`** | **nós** produzimos, de bytes que guardámos |
| `youtube_transcrever.py` → texto | **`DERIVED_ARTIFACT`** | Whisper local, com **modelo escolhível** |
| `instagram_transcrever.py` → texto | **`DERIVED_ARTIFACT`** | idem |
| legenda que o YouTube entregou | `RAW_CAPTURE` | ⚠️ **veio com a coleta.** Nós não a produzimos |
| `italy_extract_fields.mjs` → campos | `STRUCTURED_RECORD` | extrai campos, não um artefato com bytes |
| `admissao.py` → decisão | `CLAIM_OU_JUIZO` | julga. COL-LAW-502: julgar um texto não é derivá-lo |
| `pdf_text.py` | `BIBLIOTECA` | não escreve artefato nenhum |

> **Meter uma legenda do YouTube em `derived_artifact` diria que nós a produzimos.** Diria
> mal, e a partir daí a linhagem mentiria para toda a gente.

### E o vocabulário já existia

`leis/artefato.py` já distingue `RAW` de `DERIVED`, com `PARENT_ARTIFACT_ID`,
`PARENT_SHA256`, `DERIVATION_TYPE`, `EXECUTOR_ID/VERSION`, `PIPELINE_VERSION` — **os 9 campos
conferidos, todos presentes**. A tabela **traduz** esse contrato; não inventa outro. Duas
gramáticas para a mesma coisa dariam mais uma tradução a poder mentir.

---

## B · O GRÃO, EM UMA FRASE

> ## Uma linha representa **UM artefato que nós produzimos, a partir de UM conteúdo bruto, por UMA ferramenta numa VERSÃO, com UNS parâmetros, numa POSIÇÃO da série.**

Testada contra os oito casos que a quebrariam:

| caso | resultado |
|---|---|
| PDF → TXT | 1 linha |
| o mesmo PDF → OCR | outro `kind` → outra linha |
| o mesmo PDF → thumbnail | outro `kind` → outra linha |
| **o mesmo PDF → 10 frames** | mesmo tudo, e **dez artefatos** ⚠️ |
| áudio → transcrição | 1 linha |
| o mesmo RAW por **duas versões** | duas linhas, ambas legítimas |
| retry idêntico | mesma chave, mesmos bytes → **REUSED** |
| os mesmos bytes por rotas diferentes | `producer` diferente → duas linhas, **um só** `sha256` |

**O caso dos frames é o que quebra qualquer chave ingénua.** Mesmo pai, mesmo tipo, mesma
ferramenta, mesma versão, mesmos parâmetros — e dez artefatos distintos. Por isso existe
`serie_posicao`: `NULL` quando a derivação produz um só, `0..N` quando produz vários. **É o
único campo que existe por causa de um caso que ainda não temos** — e existe porque sem ele a
chave é falsa no dia em que ele aparecer.

---

## C · A IDENTIDADE — e por que o `sha256` sozinho não serve

```
(parent_sha256, kind, producer, producer_version, parameters_hash, serie_posicao)
```

> **`SHA256` IDENTIFICA BYTES. NÃO IDENTIFICA LINHAGEM.**
> Duas rotas diferentes podem chegar aos mesmos bytes — e são duas derivações, não uma.
> Provado no Postgres: `I_mesmo_sha_do_filho_com_pais_diferentes_coexiste`.

**E o `sha256` do filho NÃO entra na chave, de propósito.** Se entrasse, a mesma régua com
resultado diferente viraria duas linhas caladas. Ficando de fora, ela dá **conflito** — que é
o que um resultado que mudou merece.

### A versão da ferramenta não é enfeite

**`whisper` não basta.** O modelo `base` e o `small` sobre o mesmo áudio dão textos
diferentes, e **os dois são legítimos** — está escrito em
`ferramentas/youtube_transcrever.py`, não é hipótese. Sem a versão na identidade, a segunda
passagem apagaria a primeira em silêncio.

Versão histórica que não se consegue provar entra como `UNKNOWN`. **Não se adivinha a versão
do `pdftotext` que produziu os 43 legados.**

---

## D · O QUE FICOU DE FORA, E POR QUÊ

| pediram-me para considerar | veredito |
|---|---|
| `parent_derived_artifact_id` (derivado de derivado) | **NÃO** — zero casos reais medidos. Acrescentar depois é aditivo e barato; acrescentar agora é especular |
| `derivation_run` (entidade própria) | **NÃO** — não houve prova. E esticar `collection_run` para significar algo que não é coleta seria pior do que não ter nada. Ficou um `derivation_batch` de texto: **rótulo para agrupar, não entidade, sem chave estrangeira** |
| coluna de `status` com erros | **NÃO** — a tabela guarda **só o que existe**. Uma derivação que falhou não tem bytes; ela vive no manifesto da corrida. Guardar linhas de erro aqui faria a tabela dos artefatos contar coisas que não são artefatos |
| corpo do texto dentro do Postgres | **NÃO** — bytes no Storage, memória no banco. Provado: `K_o_banco_nao_guarda_o_corpo_do_derivado` |
| segunda tabela qualquer | **NÃO** — uma bastou |

---

## E · O LEGADO — 43 derivados sem pai canónico

```
derivados existentes           43
linhas de raw_asset IT          0
ligáveis honestamente           0
```

**Nenhum dos 43 pode apontar para um `raw_asset`, porque não há nenhum.** A corrida que
teria trazido aqueles PDFs é `RUN_NOT_PROVABLE`.

> ### LEGADO SEM PAI CANÓNICO CONTINUA LEGADO SEM PAI CANÓNICO.
> A tentação óbvia desta missão era inventar as linhas de `raw_asset` que faltam, para a
> chave estrangeira ficar bonita. **Não se fabrica história para embelezar um diagrama.**

Classe: **`LEGACY_DERIVATION_WITHOUT_CANONICAL_RAW_PARENT`**. Fica classificado, não
remendado. **A migration é FORWARD** — abre a casa para o que vier, não repinta o que passou.

E `raw_asset_id` é **`NOT NULL`** justamente por isso: derivado sem bruto canónico não entra.
Que os 43 de hoje não caibam **é o desenho a funcionar**.

---

## F · AS TRAVAS, E O QUE CADA UMA IMPEDE

| trava | impede |
|---|---|
| `raw_asset_id NOT NULL` + FK | derivado órfão, sem bruto que o justifique |
| **`ON DELETE RESTRICT`** | apagar um bruto com filhos e **levar a linhagem junto, em silêncio** |
| `unique (parent_sha256, kind, producer, producer_version, parameters_hash, serie_posicao)` | a mesma derivação virar duas linhas — e o resultado que mudou passar calado |
| `storage_path UNIQUE` | dois objetos no mesmo endereço |
| `sha256 ~ '^[0-9a-f]{64}$'` | um hash que não é um hash |
| `kind` em lista fechada | um tipo inventado a entrar sem decisão |
| `producer_version NOT NULL` | duas versões da ferramenta a apagarem-se |
| `bytes >= 0` · `derived_at NOT NULL` | artefato sem tamanho ou sem data |

**`nulls not distinct` na chave** é obrigatório: `serie_posicao` é nulável, e no Postgres dois
nulos são *diferentes*. Sem isso a trava destrancava sozinha justamente para as linhas de
derivação simples — que são a maioria.

---

## G · PROVADO EM POSTGRES 16 DE VERDADE

**`banco-descartavel`, execução `34237653804` = SUCCESS.** Lido, não presumido.

```
POSTGRES16_FOUNDATION_SCHEMA_TESTED = PASS · 19 casos    (a garantia forward)
DERIVED_ARTIFACT_DB_TESTED          = PASS · 17 casos    (a casa do derivado)
a tranca recusou 4 de 4 endereços que não são descartáveis
```

Escopo: **`FOUNDATION_MAIS_022`** — só a `001` e a `022`. As `002`–`021` não entram: a `022`
não precisa delas, e aplicá-las só para dizer «o esquema inteiro» seria pagar por uma frase
maior do que a medição. **Não houve `MIGRATION_CHAIN_DRIFT` a contornar** — a `022` assenta
na `001` sem mais nada.

### Um caso que passou a dar FAIL antes de dar PASS — e ainda bem

O caso **B** (`sem raw, a FK recusa`) reprovou na primeira execução. O banco **recusou** o
insert — mas pela trava de **unicidade**, não pela chave estrangeira: eu tinha dado ao órfão a
mesma identidade do caso A, e a unicidade mordeu primeiro.

> **Recusar não é recusar pelo motivo certo.** Se eu tivesse aceitado «qualquer erro serve
> como prova», o teste passava e não provava nada. Corrigido dando ao órfão uma identidade
> própria; agora o erro que volta é literalmente `violates foreign key constraint`.

---

## H · O ESTADO, MARCADO UM A UM

```
DESIGNED       ✅  migration 022 escrita, com o grão e a identidade medidos
IMPLEMENTED    ✅  SQL completo, com travas e comentários
DB_TESTED      ✅  Postgres 16 descartável · 17/17 · run 34237653804
LIVE_APPLIED   ❌  NÃO. Nenhuma migration aplicada em produção
OBSERVED       ❌  NÃO. Nenhuma linha real escreveu-se em lado nenhum
```

**O primeiro produtor deve ser o Golden Path para a frente** — nova corrida, novo `raw_asset`,
novo derivado. **Nunca o legado retroativo.**

## I · O QUE FALTA PARA LIGAR O GOLDEN PATH

1. Aplicar a `022` em produção — **missão própria, com autorização explícita**.
2. Uma corrida italiana real a passar pelo dono da escrita (`guarda/preservar_coleta.py`),
   criando `collection_run` + `raw_asset` de verdade.
3. Só então o derivado tem pai, e a chave estrangeira tem em que assentar.

**Por esta ordem, e nenhum passo antes do anterior.**
