# RELATÓRIO — DUAS PORTAS V1

**Missão:** fechar os dois bloqueios nomeados pela `LAST-MILE`.
**Base:** `last-mile-v1` @ `f36b2c8d` · **branch:** `duas-portas-v1`
**Modelo:** `ACTUAL_LLM_MODEL = claude-opus-5` (Opus 5) · **rede:** zero, instrumentada.

```
CANONICAL_COLLECTION_PROVEN = YES     os dois bloqueios desta missão, fechados e provados
COORTE_COMPLETA_ATRAVESSA   = NO      11 de 85 param ANTES das duas portas, num
                                      TERCEIRO bloqueio, de outro dono — §9
```

---

## 0 · A BASE, MEDIDA ANTES DE TUDO

```
BASELINE_CURADORIA = 279 OK (skipped=1, 16,0 s)
```

A suíte corre numa **cópia isolada** da árvore, com a fila esvaziada. Não é
zelo: `curadoria/test_supervisor.py` lança um `ciclo_continuo.py` **real** como
subprocesso, que lê os ficheiros da lane em disco — um `F.FILA` remendado no
processo-pai não o protege — e, desde que a etapa `QUALIFY` existe, ele bate à
rede de sítios italianos. Numa missão com `NETWORK_REQUESTS = 0` obrigatório,
correr a suíte na lane seria furar a própria regra.

Estado do acervo antes de qualquer escrita (Postgres `127.0.0.1:54330/sala_italia`):

```
collection_run 376 · raw_asset 1159 · storage_object 1023
derived_artifact 758 · documento_estruturado 754 · sala_de_espera 46
participacao_na_derivacao 785 · etapa_da_corrida 735
```

Cópia de segurança antes da primeira escrita:
`sintonia-sala-italia/backups/pre-duasportas-20260921-193429.dump` (1,8 MB).

---

## 1 · BLOQUEIO A — A ROTA DO HTML

### A1 · A rota, provada antes de ser ligada

```
HTML_INPUT_OWNER          guarda/preservar_coleta.py::preservar()
                          escreve `raw_asset` com media_type = text/html
                          (87/87 na LAST-MILE; 85/85 nesta)
TEXT_EXTRACTOR            coleta/texto_fonte.py::limpar(dados, ctype)
OUTPUT_ARTIFACT_TYPE      derived_artifact · kind = TEXT_EXTRACTION
                          media_type = text/plain
OUTPUT_OWNER              guarda/preservar_derivado.py::preservar_derivado()
ADMISSION_EXPECTED_INPUT  item com `texto` (string) e `artifact_type` em
                          ("RAW","DERIVED") → estágio DOCUMENTO
                          (admissao/admissao.py::estagio)
```

**A classificação `MISSING_ROUTE` confirmou-se em runtime, e não por leitura:**

```
antes:   ingresso.executor_para("text/html")  ->  None
depois:  ingresso.executor_para("text/html")  ->  executor_texto_de_html
```

E `coleta/texto_fonte.py::limpar` tinha **zero chamadores no código de
produção** — o único era `medidas/porque_a_sala_nao_recebeu.py`, que mede e não
colhe.

> **CAPABILITY EXISTS != EDGE EXISTS.**

O vocabulário da casa já tinha reservado o nome antes de existir quem o usasse:
`supabase/migrations/022_o_derivado_ganha_casa.sql` escreve, à frente do valor,
`'TEXT_EXTRACTION',   -- pdftotext, html->texto`.

### A2 · A menor ligação possível

| ficheiro | o que mudou |
|---|---|
| `coleta/executor_texto_de_html.py` | **novo.** Segue a forma do de PDF e do de mídia: `EXECUTOR_ID`, `CAPACIDADE`, `derivar_um(raw_asset_id, ..., armazem, memoria, relogio, contexto_da_passagem)`. **Importa** `limpar()`; não a duplica. |
| `coleta/ingresso.py` | o nome entra em `_DONOS_DA_DERIVACAO`. **Uma linha.** |
| `coleta/derivacao_forward.py` | os motivos novos ganham destino, e a `TEXT_UNIT` que o produtor promete passa a viajar (era deitada fora pelo transportador). |
| `guarda/memoria_descartavel.py` | a tabela da migration `029` faltava no banco de teste. |

**Declarar não é ligar.** A ficha `CAPACIDADE` podia existir um ano sem que nada
mudasse — foi exactamente o que aconteceu ao `SUPPORTS` do executor de PDF, e o
próprio ficheiro escreveu o preço. O que liga é o nome na lista de donos.

**PDF, áudio e vídeo intactos:**

```
application/pdf        -> texto-de-pdf           (inalterado)
video/mp4              -> transcricao-de-midia   (inalterado)
text/csv · text/plain  -> None                   (a rota do IT-T4-001 não foi roubada)
```

`ACEITA_FAMILIAS` fica **vazia** de propósito: a família `text` apanharia
`text/csv` e `text/plain`, que esta casa não sabe abrir.

### A3 · O canário, com bytes reais e sem rede

`provas/a_rota_do_html_atravessa.py` · `IT-T5-049` · `raw_asset 1118` · 38 117 bytes.
Banco descartável (SQLite), armazém em memória, **a Sala nem é tocada**. E o
canário **não chama o executor pelo nome**: chama o runner e deixa a escolha
acontecer.

> Um canário que escolhe o executor não prova a rota: prova a ferramenta, que
> nunca esteve em causa.

```
HTML_RAW                   ✅ 38 117 bytes · sha 70ae4c4a6eed… · media_type text/html
ROUTE_CHOICE               ✅ texto-de-html   (pdf e mídia continuam nos donos deles)
TEXT_OUTPUT                ✅ PORTA=PASSED · kind=TEXT_EXTRACTION · media_type=text/plain
NONEMPTY_TEXT              ✅ 3 370 caracteres · 2 831 sem brancos
PROVENANCE_PRESERVED       ✅ pai por id == pai por sha · producer=texto-de-html
                              PAGE_TEXT · ORIGINAL · EXTRACTED_FROM_DOCUMENT
                              TOOL=coleta/texto_fonte.py::limpar · LANGUAGE=UNKNOWN
                              1 linha em derived_artifact · 1 participação escrita
ADMISSION_RECEIVES_OUTPUT  ✅ com texto  → regra «pertence ao universo» (SIM)
                              sem texto  → regra «legivel»   (era o que acontecia antes)
```

A receita foi lida **de volta do banco**, e não do recibo em memória: um recibo
que concorda consigo próprio não prova persistência nenhuma.

```
HTML_ROUTE_PROVEN = YES
```

---

## 2 · BLOQUEIO B — A RÉGUA DE T10

### B1 · O contrato, descoberto e não inventado

Medido em `medidas/o_contrato_do_universo.py`, sobre os universos que **já**
existiam:

```
CRITÉRIOS UNIVERSAIS   legivel · origem · linhagem · identidade
                       dono: admissao.perguntas_do_estagio(DOCUMENTO)
                       os mesmos para T3, T4, T5, T7, T9 e T10

CRITÉRIO ESPECÍFICO    «pertence ao universo»
                       dono: admissao.PERGUNTAS_DO_UNIVERSO[universo]
                       régua: SINAIS_MINIMOS = 2 termos DISTINTOS
```

```
T10_REQUIRED_FIELDS    texto · title · nome · topics · crops · resumo
                       (nenhum é obrigatório sozinho: o que a régua exige é
                        que ALGUM deles traga texto)
                       + os quatro portões universais acima
T10_AVAILABLE_FIELDS   texto
T10_MISSING_FIELDS     title · nome · topics · crops · resumo
```

Os cinco em falta **não se preenchem**. A rota documental entrega `texto`, e
isso chega para a pergunta.

> ⚠️ **Uma correcção à medição de entrada.** O briefing dizia que `_do_universo`
> devolvia `NAO_SEI` para T10. Devolvia `NAO_SE_APLICA` — «não há regra escrita
> do que conta como «T10». Sem regra, esta porta não inventa uma.» A raiz é a
> mesma e a conclusão não muda; o vocabulário fica certo.

### B2 · A régua mais estreita possível

17 termos, tirados dos **dois donos** que já declaram o que T10 é — o escopo do
Atlas (`docs/fontes/ATLAS-DE-FONTES-EAME.md`) e os `APELIDOS` de
`leis/territorios.py` — e **não** do corpus.

```
sem língua  commodity
it          prezzo · prezzi · quotazion · listino · importazion ·
            esportazion · rincar · borsa merci · domanda e offerta
pt          precos · cotacao · cotacoes · importacao · importacoes ·
            exportacao · exportacoes
```

**Onze candidatos caíram por medição nos 85 documentos reais.** Não por gosto:

| termo | porque saiu | casava em |
|---|---|---|
| `dazi` | vive dentro de **re·DAZI·one** — a redacção, que assina todas as páginas | 32/85 |
| `preco` | vive dentro de **s·PRECO** (desperdício) e **PRECO·ce** | 4/85 |
| `mercato` | **menu do site** («Trend e mercati») | 40/85 |
| `mercati` | menu do site | 34/85 |
| `ingrosso` | **nuvem de etiquetas** («ingrosso 872») | 30/85 |
| `grossist` | menu de distribuição | 31/85 |
| `export` | bloco «potrebbe interessarti anche» — texto de **outro** artigo | 35/85 |
| `commercio` · `comercio` | 2 de 3 usos eram nome de órgão: «camera di commercio», «ministero del commercio» | 8/85 |
| `industria` | nome de um **sector**, não um movimento de mercado | 7/85 |
| `atacado` | em português é também o particípio de «atacar» — e «cultivo atacado por pragas» é T3 | — |

Um artigo sobre **mobilidade sustentável** marcava SEIS sinais de mercado sem
ter uma palavra de mercado no corpo.

> **UMA PALAVRA QUE QUALQUER DOCUMENTO TEM NÃO SEPARA DOCUMENTO NENHUM.**
> **O NOME DE QUEM PUBLICA NÃO É O ASSUNTO DO QUE SE PUBLICA.**

É a mesma família de `fitosanitario` (saiu de T3) e de `prova` dentro de
`approvazione` (saiu de T5), com o mesmo método de medição.

**E nenhuma forma cabe dentro de outra da lista.** `importazione` dentro de
`importazioni` daria **dois** sinais a **uma** palavra, e a régua dos
`SINAIS_MINIMOS` deixava de valer sem ninguém dar por isso. Daí as raízes:
`quotazion`, `importazion`, `esportazion`, `rincar` — a mesma solução que
`fitopatolog` já usa em T3.

### B3 · Os quatro ramos, com valores escritos à mão

`tests/test_a_regra_de_t10.py` — 16 testes:

```
material válido        → SIM        dois termos distintos, e as palavras ficam no livro
material insuficiente  → NAO_SEI    um indício não promove NEM rejeita
material incompatível  → NAO        prova POSITIVA de outro universo
material inválido      → não entra  para em «legivel» ou em «linhagem», antes do universo
sem universo declarado → NAO_SE_APLICA  (UNIVERSO_NAO_DECLARADO)
universo sem régua     → NAO_SE_APLICA  (T1 continua sem régua, e a porta não inventa uma)
```

E a guarda contra a regra proibida: **`T10 → SIM` automático não existe**. Um
texto sem uma palavra de mercado, perguntado a T10, não pode sair `SIM`.

```
T10_ADMISSION_RULE_PROVEN = YES
```

### ⚠️ B4 · A régua de T10 desmascarou um acidente em T7

Enquanto T10 não tinha régua, `_do_universo` saía mais cedo e o ciclo dos
**outros** universos nunca corria para estes itens. Com a régua escrita, ele
passou a correr — e **26 dos 39** documentos de T10 saíram `NAO` com a prova
«fala claramente de T7: **soci**».

Medido, palavra inteira por palavra inteira, nos mesmos 26 documentos:

```
sociale 22 · association 10 · social 9 · sociali 8 ·
societario 2 · associations 2 · societa 1 · society 1
```

> **`soci` NÃO CASOU UMA ÚNICA VEZ COM A PALAVRA `soci`.**

E o estrago era o pior que esta porta consegue fazer: um `NAO`, que é a única
resposta que **fecha** o assunto — e a prova era `associazione`.

`soci` foi removido, **sem substituto inventado**: o conceito de T7 já está
coberto por `cooperativa`, `consorzio`, `agronomi`, `assistenza tecnica`,
`servizio agronomico`, `tecnico di campo` e `divulgazione tecnica`.

**E isto corrige a expectativa herdada.** A `LAST-MILE` estimou «12 SIM». Eram
**4 verdadeiros** (T5) + **8 falsos** (T7, todos sustentados por `soci`).

---

## 3 · MEDIÇÃO A SECO, DEPOIS DAS DUAS PORTAS

`medidas/o_contrato_do_universo.py`, sobre os 85 com o texto que o derivador
produz:

```
SIM 11 · NAO 34 · NAO_SEI 40 · NAO_SE_APLICA 0
  T5   SIM 4
  T7   NAO 21 · NAO_SEI 21
  T10  SIM 7 · NAO 13 · NAO_SEI 19
```

`NAO_SE_APLICA` caiu de **39 para 0**: era a ausência da régua de T10.

**E nenhum dos 34 `NAO` assenta só num acidente de substring** — conferido item
a item: todos têm pelo menos um casamento de **palavra inteira** do vocabulário
de outro universo (`evento`, `prodotto`, `ricerca`, `campagna`, `etichetta`,
`ministero`, `istituto`…). A porta está a julgar, não a tropeçar.

> **Dívida declarada, não corrigida:** três termos pré-existentes de outros
> universos casam por acidente — `lancio` dentro de **bi·lancio**, `revista`
> dentro de **p·revista**, `tesi` dentro de **sin·tesi** e **ipo·tesi**.
> Nenhum deles decide sozinho nesta coorte (0 de 34), e são de T9 e T5, que não
> são os bloqueios desta missão. Ficam nomeados e medidos.

---

## 4 · FASES C–F — O REPROCESSAMENTO REAL

`medidas/duas_portas_reprocessa.py` · seis corridas · `--so-a-porta
--colheita-da-corrida=<RUN_ID>` · persistência **OPERACIONAL**
(`127.0.0.1:54330/sala_italia`).

### O balcão, reconstruído pelo dono

`data/colheita/` está no `.gitignore` e os envelopes da RUN1C já não existiam
em disco. Quem os refez foi o **dono** — `italy_executor.colher(run_id)` —
relendo `data/collection-ledger/italy/observations.ndjson`, que está no Git com
as 85 observações. Nada inventado: `leis/retorno_da_coleta.conferir()` confere
o `sha256` declarado contra os bytes no armazém.

### O que mudou no acervo

| tabela | antes | depois | delta |
|---|---|---|---|
| `collection_run` | 376 | 388 | +12 |
| `raw_asset` | 1159 | 1329 | +170 |
| `storage_object` | 1023 | 1023 | **+0** |
| `derived_artifact` | 758 | **832** | **+74** |
| `documento_estruturado` | 754 | 828 | +74 |
| `participacao_na_derivacao` | 785 | 933 | +148 |
| **`sala_de_espera`** | **46** | **56** | **+10** |
| `etapa_da_corrida` | 735 | 759 | +24 |

```
SALA_BEFORE = 46      SALA_AFTER = 56      SALA_DELTA = +10
```

**`derived_artifact +0` na segunda corrida é uma prova, e não um falhanço.**
Mesma receita, mesmos bytes → `REUSED`. As 74 observações **novas** declararam
participação nos **mesmos** 74 derivados — que é palavra por palavra o que a
migration `029` prometeu: as capturas irmãs deixam de se distinguir por
inferência de `sha256`.

### A admissão

```
ADMISSION_SIM          10
ADMISSION_NAO          28
ADMISSION_NAO_SEI      36
ADMISSION_NAO_SE_APLICA 0
ADMISSION_ERRO          0
                       ──
                       74 julgados   (os outros 11 → §9)
```

As duas corridas deram **exactamente** as mesmas 74 decisões. A porta é
determinística.

### Cada linha nova da Sala, com linhagem inteira

| `SOURCE_ID` | `RUN_ID` | `ARTIFACT_ID` | `RAW_ASSET_ID` | `STORAGE_OBJECT_ID` | `VERDICT` |
|---|---|---|---|---|---|
| IT-T10-018 | XX-T10-…-224321 | `derived:762` | 1261 | 1093 | SIM |
| IT-T10-018 | XX-T10-…-224321 | `derived:764` | 1258 | 1090 | SIM |
| IT-T10-018 | XX-T10-…-224321 | `derived:766` | 1253 | 1085 | SIM |
| IT-T10-018 | XX-T10-…-224321 | `derived:767` | 1260 | 1092 | SIM |
| IT-T10-018 | XX-T10-…-224321 | `derived:768` | 1257 | 1089 | SIM |
| IT-T10-018 | XX-T10-…-224321 | `derived:769` | 1267 | 1099 | SIM |
| IT-T10-018 | XX-T10-…-224321 | `derived:772` | 1263 | 1095 | SIM |
| IT-T5-049 | XX-T5-…-224448 | `derived:794` | 1285 | 1117 | SIM |
| IT-T5-049 | XX-T5-…-224448 | `derived:795` | 1286 | 1118 | SIM |
| IT-T5-049 | XX-T5-…-224448 | `derived:796` | 1284 | 1116 | SIM |

`OBSERVATION_ID` = `raw_asset.id` (a coluna chama-se `raw_observation_id`).
`ADMISSION_ID`: **não existe** como campo. O que a Sala guarda é
`admitido_por = "pertence ao universo v5"` — a regra e a versão dela. A ausência
é declarada, não fabricada.

Todas as dez: `producer = texto-de-html`, `parent_sha256` == o `sha256` do
bruto, `estado_da_fila = WAITING`, `estagio = DOCUMENTO`.

```
RAW_PROVEN                   YES (85 linhas por corrida; 74 confirmadas — §9)
STORAGE_PROVEN               YES (+0 novos, 85 reaproveitados: o mesmo byte, uma cópia)
ADMISSION_PROVEN             YES (74 decisões, quatro vereditos usados)
SALA_CANONICAL_WRITE_PROVEN  YES (+10)
INSERT manual 0 · SQL ad hoc 0 · fixture 0 · bypass 0
```

### Tempo, lugar e cultura — sem fallback

```
FACT_TIME_PROVEN       0      FACT_TIME_UNKNOWN       10
FACT_LOCATION_PROVEN   0      FACT_LOCATION_UNKNOWN   10
REGION_*               NOT_APPLICABLE
CROP_*                 NOT_APPLICABLE
```

Nas dez linhas: `fact_time`, `published_at`, `observed_at`, `fact_location`,
`source_location`, `fact_time_basis`, `fact_location_basis` e
`source_declared_evidence_class` são todos `NAO SEI`.

**Que não houve queda, prova-se assim:** `captured_at` **está** preenchido com o
instante real (`2026-09-21T19:26:49.683Z` e companhia) e o `fact_time` continua
`NAO SEI`. Se existisse fallback, seriam iguais. E `published_at` é ele próprio
`NAO SEI` — a igualdade entre duas ausências declaradas não é um fallback.

`REGION_*` e `CROP_*` são `NOT_APPLICABLE` e **não** um buraco novo: nem
`ingresso.FRONTEIRA_TRANSPORTA` nem `admissao.pronto_para_inteligencia`
(COL-LAW-043) têm campo de cultura ou de região, e a tabela `sala_de_espera`
não tem coluna.

### A rede

```
NETWORK_REQUESTS    0
DNS_LOOKUPS_FORA    0
LOOPBACK_CONNECTS   0
SUBPROCESSOS      790    (todos `psql` e `git` — um filho nasce com
                          interpretador limpo e NÃO herda os remendos,
                          por isso são contados e não escondidos)
```

Instrumento: `medidas/corrida_sem_rede.py`, **importado** e não copiado. Uma
segunda cópia dos remendos seria um segundo dono da mesma medição.

---

## 5 · FASE G — RED TEAM

`provas/red_team_duas_portas.py` — 14 ataques. Cada um com:

1. **base medida antes** — os matadores têm de estar verdes. Um teste que já
   falha «mata» qualquer coisa;
2. **`git diff` a provar a mutação** — «apliquei a mutação» é uma afirmação
   minha sobre mim próprio;
3. **matadores em interpretador limpo** (subprocesso);
4. **restauro conferido por `sha256`**.

| # | ataque | `MUTANT_APPLIED` | `MUTANT_KILLED` |
|---|---|---|---|
| M01 | desligar a rota HTML | ✅ | ✅ |
| M02 | `limpar()` devolve vazio e passa | ✅ | ✅ |
| M03 | universo sem régua entra | ✅ | ✅ |
| M04 | régua vira `SIM` automático | ✅ | ✅ |
| M05 | uma palavra promove (`SINAIS_MINIMOS` 2→1) | ✅ | ✅ |
| M06 | proveniência desaparece (texto sem ferramenta) | ✅ | ✅ |
| M07 | RAW salta a admissão | ✅ | ✅ |
| M08 | HTML mau entra como matéria | ✅ | ✅ |
| M09 | `FACT_TIME = PUBLISHED_AT` | ✅ | ✅ |
| M10 | `FACT_LOCATION = SOURCE_LOCATION` | ✅ | ✅ |
| M11 | acesso à rede durante o reprocessamento | ✅ | ✅ |
| M12 | a rota do HTML rouba o PDF | ✅ | ✅ |
| M13 | `soci` volta a T7 | ✅ | ✅ |
| M14 | duas formas da mesma palavra em T10 | ✅ | ✅ |

```
MUTANTES 14 · MUTANT_KILLED 14 · RED_TEAM_SURVIVORS 0 · ÁRVORE LIMPA NO FIM
```

Zero rede: o único ataque que **tenta** sair é o `M11`, e existe para provar que
o instrumento o apanha — a ligação é travada, nunca completada.

### ⚠️ Os dois sobreviventes da primeira passagem, e as duas causas

**`M05` sobreviveu por defeito do instrumento.** A mutação trocava
`SINAIS_MINIMOS = 2` por `= 1`: **mesmo tamanho**, escrita no mesmo segundo do
import anterior. O `.pyc` valida-se por `(mtime em segundos, tamanho)` e nenhum
dos dois mudou — o interpretador novo carregou o ficheiro **antigo** do cache.
O `git diff` provava a mutação e o matador nunca a viu.

> **UM MUTANTE QUE NÃO MUDA O TAMANHO E QUE CABE NO MESMO SEGUNDO É INVISÍVEL
> PARA O IMPORT. ELE «SOBREVIVE» SEM NUNCA TER CORRIDO.**

Corrigido por dentro: o cache do alvo é apagado ao aplicar e ao restaurar, e
`PYTHONDONTWRITEBYTECODE=1` impede cache novo.

**`M12` sobreviveu por código redundante que escondia uma trava inexistente.**
Pôr `application/pdf` na ficha do executor de HTML não fazia nada reclamar:
`executor_para` percorre a lista por ordem e o de PDF está primeiro. Mas
`coleta/ingresso.py` já tinha escrito, por extenso, que **«a ordem NÃO é
prioridade»** e que sobreposição de espécies é «uma decisão a **escrever**, não
a herdar de quem foi importado primeiro». A lei estava escrita e não tinha quem
a fizesse morder. Passa a ter: dois testes novos, com a tabela de donos escrita
à mão.

---

## 6 · UM DEFEITO MEU, APANHADO PELOS MEUS PRÓPRIOS TESTES

A guarda dos bytes escrevia `"os bytes comecam por %PDF- …" % media_type` — e
`%P` não é um especificador de formato. A guarda **rebentava** com
`ValueError: unsupported format character 'P'` em vez de recusar.

> Uma guarda que rebenta em vez de recusar deixa de ser guarda.

Corrigido (`%%PDF-`) e coberto por
`tests/test_a_rota_do_html.py::OsBytesQueNaoSaoHtmlNaoEntramAqui`.

---

## 7 · REGRESSÃO

Medida nas **duas** bases e comparada **por nome** — a base desta máquina já
chega vermelha, e comparar totais mentiria nos dois sentidos.

```
curadoria/   BASELINE 279 OK    DEPOIS 279 OK    NEW_FAILURES 0
tests/       grupo de 55 módulos que importam admissao · ingresso ·
             derivacao_forward · memoria_descartavel · preservar_derivado
             ANTES 44 vermelhos   DEPOIS 44   os MESMOS nomes
             NEW_FAILURES 0
```

### Três sentinelas dispararam, e isso é o trabalho delas

Cada uma exige, por escrito, que quem muda a lista actualize o número **e**
escreva porquê. As três foram actualizadas com a razão medida ao lado:

```
tests/test_c4g_a_especie_do_video.py   «a porta conhece pdf E midia e nada mais»
tests/test_a_regra_de_t2.py            a lista de universos e as contagens
tests/test_amostragem_neutra_t3.py     a lista de universos
tests/test_ui_revisao_t3_ptbr.py       a lista de universos
tests/test_pacote_de_revisao_t3.py     a lista de universos
```

O que todas protegem continua inteiro: **`T2` NÃO ganhou régua.**

---

## 8 · SYSTEM MAP

```
SYSTEM_MAP_CHECK = PASS
```

Três peças novas declaradas em `system-map/data/architecture.declared.json`:

```
C-EXECUTOR-TEXTO-HTML     Z-ACOES    engine   coleta/executor_texto_de_html.py
C-DUAS-PORTAS-MEDIDORES   Z-MEDIDAS  scanner  medidas/ (2 medidores + 2 JSON)
C-PROVA-ROTA-DO-HTML      Z-PROVA    proof    provas/ (3 provas + 1 JSON)
```

A casa já tinha o padrão — uma peça por executor — e o de HTML segue-o.
Escrito por **inserção literal no fim do array**: 64 linhas acrescentadas,
**zero** apagadas. A missão anterior mediu o preço de reserializar (2 404
inserções / 2 354 remoções de diff fantasma) e a lição fica aplicada.

A `OBSERVACAO` que sobra é pré-existente: `architecture.declared.json` tem dois
autores e o dono foi eleito por ordem alfabética. Continua por decidir por
gente.

---

## 9 · ⚠️ O TERCEIRO BLOQUEIO — 11 DE 85, POR UM ZERO

**Não é um dos dois desta missão, e não foi tocado. Fica nomeado e medido.**

Das 85 observações, **74** chegaram à derivação. As outras **11** perdem-se
antes, e a telemetria diz exactamente onde:

```
RAW      PARTIAL   input 30 · output 28 · unknown 2   (e assim nas seis)
DERIVED  PASS      recebeu 74, entregou 74
```

O mecanismo, medido:

```
as 74 confirmadas   captured_at rende 26 caracteres   2026-09-21 19:26:49.683+00
as 11 perdidas      rende 25 ou 24                    2026-09-21 19:27:45.1+00
```

`guarda/preservar_coleta.py::observacoes_confirmadas` só aceita a linha que
passou na **conferência campo a campo depois de escrever**, e essa conferência
compara `captured_at` como **texto**. O livro escreve `…28.790Z`; o Postgres
devolve `…28.79+00`, com o zero final comido. As cadeias diferem, a observação
não é confirmada, nunca se torna unidade de derivação — e a etapa `DERIVED`
nem chega a saber que ela existiu.

Nenhuma outra diferença entre os dois grupos: todas `FORWARD_IDENTIFIED`, sem
`sha256` repetido, com os bytes no armazém e com texto extraível.

**E custa uma decisão:** uma das 11 (`IT-T5-049`,
`avvisi-esami-e-prove-itinere.html`, 5 830 caracteres) daria `SIM`. É por isso
que a medição a seco diz **11 SIM** e a corrida real deu **10**.

```
Dono: guarda/preservar_coleta.py::observacoes_confirmadas
Custo medido: 11 de 85 (12,9 %) · 1 SIM perdido
Conserto provável: comparar INSTANTES, não textos
```

### ⚠️ E um segundo achado da fase C–F: a Sala corre em `FICHEIRO` por omissão

A **primeira** corrida desta missão atravessou a estrada inteira — `DERIVED
+74`, `STRUCTURED +74`, `ADMISSION` com **10 SIM** — e a Sala ficou em 46.
Nada tinha falhado: `admissao/sala_de_espera.py::backend()` cai em `FICHEIRO`
por omissão, que ele próprio declara `CANONICO: False` («o ficheiro vive no
workspace do runner: não sobrevive ao job»). Os dez pousaram num disco efémero.

> **UMA CORRIDA QUE DIZ `SUCCESS` COM A SALA NO BACKEND ERRADO NÃO ESCREVEU NA
> SALA — E NÃO SE QUEIXOU.**

O dono já tinha a resposta pronta (`estado_operacional()`) e o portão
(`exigir_canonica()`); faltava alguém **perguntar** antes de gastar a corrida.
O corredor passa a perguntar e a recusar sem `SINTONIA_SALA_BACKEND=POSTGRES`.
A Sala-sombra do backend de ficheiro foi apagada.

**Preço declarado:** a primeira corrida deixou 6 `collection_run` e 85
`raw_asset` no acervo sem nada a jusante. `storage_object +0` — nenhum byte
duplicado. Fica dito em vez de ficar calado.

---

## 10 · VEREDICTO

| critério | estado |
|---|---|
| `HTML_ROUTE_PROVEN` | ✅ YES |
| `T10_ADMISSION_RULE_PROVEN` | ✅ YES |
| `RAW_PROVEN` | ✅ YES |
| `STORAGE_PROVEN` | ✅ YES |
| `ADMISSION_PROVEN` | ✅ YES |
| `SALA_CANONICAL_WRITE_PROVEN` | ✅ YES — `SALA_DELTA = +10` |
| `NETWORK_REQUESTS` | ✅ 0 |
| `RED_TEAM_SURVIVORS` | ✅ 0 (14/14 mortos) |
| `NEW_FAILURES` | ✅ 0 (contra 279, e contra 44 em `tests/`) |
| `SYSTEM_MAP_CHECK` | ✅ PASS |
| árvore limpa · `LOCAL == REMOTE` | ✅ |

```
CANONICAL_COLLECTION_PROVEN = YES
```

**E a ressalva, que vale tanto como o veredicto:** a estrada está aberta e
provada, mas **nem tudo a percorre**. 11 das 85 param num terceiro bloqueio,
noutro dono, por um zero final numa comparação de texto (§9). Abrir a porta não
é o mesmo que toda a gente passar por ela.

---

## EM PALAVRAS SIMPLES

**O que estava parado, e porquê.**

Imagine uma fábrica com uma esteira. No fim da esteira há uma porta, e atrás da
porta há uma sala onde os documentos ficam à espera de serem lidos. Tinham
chegado 85 páginas de sítios italianos. Nenhuma passou a porta. Duas coisas
faltavam, e as duas eram pequenas.

**A primeira: a máquina de ler já existia, e ninguém a tinha ligado à tomada.**

Uma página de internet chega cheia de coisa que não é texto — código, menus,
botões. Alguém, meses atrás, escreveu nesta casa uma peça que tira tudo isso e
deixa só as palavras. A peça estava lá, funcionava, e **nenhuma parte da
fábrica a chamava**. Era como ter uma máquina de café na cozinha, em bom
estado, sem ficha na tomada — e o pessoal a dizer que não havia café.

Eu não construí máquina nova. Liguei a que já lá estava: escrevi o adaptador
(uma peça pequena, no formato das outras duas que já existiam — a do PDF e a do
vídeo) e pus o nome dela na lista de quem a fábrica chama. **Uma linha.** Das
85 páginas, 74 passaram a virar texto.

**A segunda: a porta não tinha régua para um dos assuntos.**

A porta pergunta sempre a mesma coisa: «este documento é do assunto que me
pediram?». Para fazer essa pergunta, ela precisa de uma lista de palavras —
uma régua. Havia régua para cinco assuntos (pragas, regulamentação, ciência,
rede técnica, concorrentes). **Faltava a do assunto «mercado»** — preços,
importações, exportações, movimentos de comércio. Trinta e nove documentos eram
desse assunto, e a porta respondia, com toda a educação: *«não há regra escrita
do que conta como mercado. Sem regra, eu não invento uma.»* A porta estava
certa. Ninguém tinha escrito a pergunta.

Escrevi a régua. E aqui foi onde o trabalho ficou interessante, porque a
primeira versão dela estava **errada e parecia boa**.

**A armadilha do menu do site.** Peguei nas palavras óbvias de mercado —
«mercado», «preço», «atacado», «exportação» — e fui medir nos 85 documentos.
Quarenta deles tinham a palavra «mercado». Fui ver **onde**. Estava no **menu de
navegação do site**, que aparece em todas as páginas, incluindo numa notícia
sobre transporte sustentável que não falava de mercado nenhum. O nome da secção
do jornal não é o assunto da notícia.

Pior ainda: a palavra italiana para «taxas de importação» é *dazi*. Ela aparecia
em 32 dos 85 documentos. Fui ver onde: dentro de *re**dazi**one* — que quer
dizer «redacção», e está no rodapé de qualquer jornal italiano. A régua não
estava a medir nada. Só não se via.

Atirei fora onze palavras por esse motivo, uma a uma, com a medição escrita ao
lado de cada uma. Ficaram dezassete, todas conferidas no texto real.

**E aí a régua nova apanhou um erro antigo.** Assim que a régua de mercado
começou a funcionar, o sistema passou a comparar os documentos com **todos** os
assuntos ao mesmo tempo — e vinte e seis documentos foram recusados com a
justificação «isto é claramente rede técnica, fala de *soci*» (sócios de
cooperativa). Fui verificar. A palavra *soci* nunca aparecia nesses documentos.
O que aparecia era *so**ci**ale*, *so**ci**al*, *as**soci**ation* — e o
computador, que procura pedaços de palavra, achava que tinha encontrado
«sócios» dentro de «social». **Vinte e seis documentos recusados por uma
palavra que não estava lá.** Tirei-a.

**Quantas notícias entraram mesmo.**

Dez. A sala tinha 46 documentos; ficou com 56.

E é importante dizer porque não foram as 85, porque a diferença é toda:

- **74** viraram texto e foram à porta.
- Dessas 74, a porta disse **SIM a 10**, **NÃO a 28** e **«não sei» a 36**.
- As outras **11** nem chegaram à porta — e isso é um **terceiro** problema, que
  não era o meu, e que deixo medido e com nome: quando a hora de chegada do
  documento acaba em zero (`19:27:45.**790**`), a base de dados devolve-a sem
  esse zero (`19:27:45.79`), o sistema compara os dois como se fossem palavras,
  vê que são diferentes e descarta a observação. Uma dessas onze era um `SIM`.

**Dez não é pouco e não é muito — é o número verdadeiro.** A porta não é um
carimbo: ela lê, e recusa o que não é do assunto. Vinte e oito documentos foram
recusados *com prova* — falavam de outra coisa, e isso está escrito no livro de
decisões, documento a documento. Trinta e seis ficaram em «não sei», que é a
resposta honesta para «o meu vocabulário não chegou a este item» e que manda
alguém ir ver. Se eu quisesse um número bonito, bastava afrouxar a régua — e era
exactamente assim que os 8 falsos «sim» do assunto «rede técnica» tinham
aparecido antes.

**Uma coisa que ficou vazia de propósito.** Nenhum dos dez documentos diz
**quando** o facto aconteceu nem **onde**. Eu tinha ali à mão a data em que a
nossa máquina descarregou a página, e podia ter posto essa data no campo do
«quando aconteceu» — ficava tudo preenchido e bonito. Não pus. São coisas
diferentes: a hora em que eu recebi o jornal não é a hora em que a notícia
aconteceu. O campo fica a dizer **«não sei»**, que é a verdade, e quem ler
daqui a três meses sabe que continua por descobrir.

**Como sei que nada disto é conversa.** Depois de tudo funcionar, quebrei-o de
propósito catorze vezes — desliguei a máquina de ler, fiz a régua dizer «sim» a
tudo, apaguei a origem dos textos, mandei o sistema ir à internet no meio do
trabalho — e em cada uma das catorze um teste gritou. Duas das primeiras vezes
não gritou, e as duas razões valeram a pena: uma foi a minha própria ferramenta
de ataque que estava a enganar-se (o Python tinha guardado uma cópia velha do
ficheiro e nem chegou a ver a avaria), e a outra era uma regra que a casa tinha
escrita no papel e que ninguém fazia cumprir. As duas ficaram fechadas.
