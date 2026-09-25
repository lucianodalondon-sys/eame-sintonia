# TEMPO-E-LUGAR · relatório (D61 · D62 · D63) · ramo `tempo-lugar-v1`

> **ATUALIZAÇÃO (25/09, tarde) — ler primeiro.** As propostas B e C deste relatório viraram
> a migração única **033** (D68), e o `tempo-lugar-v1` passou a apontar para o mesmo commit do
> `migracao-sala-v1`. Juntou-se, por merge, a LUGAR-FATO até a D70 (`4d4ca5fc`) e a nuvem
> tempo-publicacao (`007cccf5`); a DA-9 (duas fontes da publicação, ordem fixa, conflito
> marcado) está ligada. **Os números atuais e o roteiro estão em `MIGRACAO-SALA.md`**: nas 78,
> numa cópia da Sala real, publicação **36**, lugar da fonte **5**, data do facto **18**,
> lugar do facto **12**. ⚠️ **Instalar só DEPOIS da 033** — sem ela, o 1.º `pousar` falha alto.
> Os números abaixo são os da primeira medição (encanamento sem migração) e ficam como histórico.

Base: `df0865e6` (produção). Rede fechada. **O vivo e a Sala real não foram tocados**: a Sala foi
lida só com `default_transaction_read_only=on`. Todo o ensaio correu num Postgres **descartável**
(banco `descartavel`, porta aleatória, desligado e apagado no fim).

```
FACT_TIME != PUBLICATION_TIME != OBSERVATION_TIME != COLLECTION_TIME
SOURCE_LOCATION != FACT_LOCATION          cada valor com a sua BASE
```

## 1. A informação existe? (as 78 da Sala real, 25/09 ~09:25)

A Sala tinha os quatro campos em `NAO SEI` nas 78 linhas. O medidor é
`provas/tempo_e_lugar_medir.py`: ele lê os bytes guardados com o sha256 conferido (77 de 78; o
N37 da ARIF não tem bytes em lado nenhum) e os contratos de cada fonte.

| campo | têm prova | de onde |
|---|---|---|
| PUBLISHED_AT | **37 / 78** | 24 `article:published_time` · 6 JSON-LD `datePublished` · 2 `<time>` · 5 boletins T3 pela data impressa (livro `SOURCE_DATE_ISO`). O APOL (IT-T3-010) conta aqui, mas o contrato declara essa data como VALIDADE, então pelo código novo são **36** |
| SOURCE_LOCATION | **5 / 78** | só os contratos T3 (Napoli, Lecce, Bari). ⚠️ O `REGION` do Atlas é o que a AMOSTRA viu, não a sede — não serve |
| FACT_LOCATION | 1 / 78 com âncora de acontecimento | 74 só **mencionam** lugar, e menção ≠ facto |
| FACT_TIME | ~15 / 78 candidatas | ver §5 (leitura à mão) |

## 2. Onde se perdia (ficheiro:linha na base `df0865e6`)

Ninguém escrevia a constante `NAO SEI`. O valor **não era passado** de uma etapa para a outra:

1. `regras/italy_contracts.mjs:624,637`: a rota HTML genérica não lê data nenhuma, e `SOURCE_LOCATION_RULE: "NAO SEI"`.
2. `coleta/italy_executor.py:114-126,176`: a tradução só levava 4 campos; o motivo do `UNKNOWN` era jogado fora.
3. `coleta/ingresso.py:1017-1021`: `raw_asset` não tem coluna de tempo ou lugar, e o dono do RAW só leva `CAPTURED_AT`.
4. `coleta/ingresso.py:760-771`: a unidade da derivação não levava.
5. `orquestrador/orquestrador.py:497-510`: a estruturação não levava.
6. `orquestrador/orquestrador.py:572-577`: o item da porta nascia sem os campos.
7. `admissao/admissao.py:1893-1918`: escreve `NAO SEI` por falta. A Sala (`sala_de_espera.py:660-666`) grava tal e qual.

## 3. O conserto (A) — no dono único, sem migração · PRONTO PARA INSTALAR

| peça | o que faz |
|---|---|
| `coleta/italy_executor.py::tempo_e_lugar` | **o dono do que a observação prova.** `PUBLISHED_AT` só com base: vem do coletor, ou é `SOURCE_DATE_ISO` **só** se o contrato declara `DOCUMENT_DATE_KIND=EDICAO`. O `UNKNOWN — …` vira `FACT_TIME_BASIS`. `SOURCE_LOCATION` vem de `contratos_de_fonte.lugar_declarado_pela_fonte`. `FACT_LOCATION` só vem do coletor com base. Texto como «por ponto — …» não é instante |
| `regras/italy_contracts.mjs` + `contratos_de_fonte.data_do_documento_e_publicacao` | `DOCUMENT_DATE_KIND`: IT-T3-002 e IT-T3-008 = `EDICAO`; IT-T3-010 = `VALIDADE` (não é publicação) |
| `coleta/ingresso.py` | `TEMPO_E_LUGAR` (a lista do recado, **um dono**) · `tempo_e_lugar_por_observacao` (liga pela alça, sem sha nem posição; passagens que discordam → ausente) · a unidade da derivação leva o recado · `PARA_A_PORTA` traduz `PUBLISHED_AT_BASIS`/`SOURCE_LOCATION_BASIS` · as bases do facto vão às `NOTES` da ficha |
| `coleta/derivacao_forward.py`, `orquestrador.pela_estruturacao` | passam o recado sem tocar |
| `orquestrador.item_documental_para_a_porta` + `_fato_do_texto` | põe o recado no item, só pelo tradutor único. **Liga o extrator da LUGAR-FATO** (`leis/fato_do_texto.py`, commit `44f91b51`, autoria preservada): ele só preenche o que o livro não provou, **não recebe a sede**, e conta a data relativa a partir de `PUBLISHED_AT` com base, **nunca** de `COLLECTED_AT` (D63). Sem resposta de nenhum dos dois, as duas bases ficam |
| `admissao._tem_quando` (**D62**) | um FATO sem data nenhuma deixa de ser barrado: a falta registra-se (`NAO SEI`) e a porta segue. Três testes que fixavam a regra revogada foram atualizados (`test_red_team_estrada` K/K2, `test_estagio_atravessa_a_fronteira` 3/4/sem_estágio) |
| `admissao.completude_tempo_lugar` (**D62**) | por item: `PUBLICACAO · LOCAL_DA_FONTE · DATA_DO_FATO · LOCAL_DO_FATO`, cada um `PROVADA` / `CALCULADA` (relativa, D63) / `NAO SEI`, e `PROVADAS: n` |

**Testes:** `tests/test_tempo_e_lugar_atravessa.py`, 34 verdes. Mais os 12 da LUGAR-FATO, verdes.
**Mutação:** `tests/mutacao_tempo_e_lugar.py`, **13 de 13 pegas** (o arquivo volta idêntico depois de cada uma):
M1 publicação→fact_time · M2 sede→fact_location · M3/M4 o tradutor troca os dois · M5 validade vira publicação ·
M6/M7 uma paragem larga o recado · M8 prosa vira instante · M9 extrator desligado · M10 sede empurrada no extrator ·
**M11 a relativa contada a partir da COLHEITA (D63)** · **M12 a falta de data volta a barrar (D62)** · M13 a completude esconde o CALCULADA.
**Vizinhos:** 16 suítes + os 2 testes Node do contrato, na árvore nova e na base: as mesmas falhas
antigas nas duas (`test_lingua_da_porta` 1F, `test_col_e7` 1F, `test_estagio_atravessa` 1E,
`italy_contract_test.mjs` 348/77), e nenhuma nova.

## 4. Antes / depois — a estrada REAL num Postgres descartável

`provas/tempo_e_lugar_replay.py` usa as mesmas peças e a mesma ordem de `orquestrador.correr`:
livro → `traduzir` → `pela_entrada` → `pela_derivacao` → `pela_estruturacao` → `item_documental_para_a_porta` → `pela_porta`.
Os bytes são os guardados, com o sha256 conferido. Corri **duas vezes**: com a árvore de base e com a nova.

| 77 reproduzíveis (o N37 não tem bytes) | BASE `df0865e6` | NOVO |
|---|---|---|
| PUBLISHED_AT sai de NAO SEI | 0 | **3** (T3 pela edição; o APOL é validade e fica NAO SEI) |
| SOURCE_LOCATION | 0 | **4** |
| FACT_TIME | 0 | **14** (extrator da LUGAR-FATO) |
| FACT_LOCATION | 0 | **1** (Puglia, N38) |
| FACT_TIME_BASIS / FACT_LOCATION_BASIS | 0 / 0 | **77 / 77** (o porquê, sempre) |
| linhas na Sala descartável | 48 | 48, com 2 / 3 / 12 / 1 preenchidas e bases 48/48 |
| FACT_LOCATION == SOURCE_LOCATION | 0 | **0** |
| FACT_TIME == PUBLISHED_AT | 0 | 1: o N38 com «oggi» (ver §5) |

As 48 linhas, e não 78: a Admissão de hoje admite menos do que admitia quando as 78 pousaram.
Isso é igual nas duas árvores, então não vem deste conserto.

## 5. Leitura à mão — as 15 datas do facto previstas para as 78

**10 certas:** campagna 2010 · 2022 (curso aberto) · 29 settembre 2026 (evento, 2 linhas) ·
stagione 2026 · raccolta 2026 · 2025 (meta dos varejistas) · «oggi 23 settembre 2026» ·
«presentato oggi a Bologna» · maggio (pico de pólen).

**5 erradas (33%):** «luglio» é conselho · «21 settembre» é um exame remarcado · «2025» é ano de
comparação de preço · **N37 e N38: «ex UCEA, *oggi* C.R.E.A.»**, em que «oggi» é *hoje em dia*, e
com a D63 isto vira `FACT_TIME = publicação`. **Defeito novo para a LUGAR-FATO** (o padrão
«ex X, oggi Y»). Os 3 primeiros ela já os tinha declarado.
Lugar do facto: 1 de 1 certo (Puglia).
*A leitura é de uma pessoa só, pelos trechos; pode haver erro de um item.*

## 6. Reprocessamento do acervo (pedido do dono) — previsão, sem rede, só leitura

`provas/tempo_e_lugar_acervo.py`. Acervo na Sala real: **1.474** linhas `raw_asset`, que são
**1.158** arquivos diferentes (937 HTML · 47 PDF · 171 JSON social · 3 mídia/CSV). Com o código
novo, sobre os 984 HTML/PDF:

| | originais | publicação | local da fonte | data do facto (calculadas) | local do facto |
|---|---|---|---|---|---|
| **as 78 linhas da Sala** | 72 arquivos | **36** (4 livro + 32 página*) | **5** | **15** (4) | **1** |
| fora da Sala | 912 | 797* | 9 | 19 (1) | 3 |
| acervo todo | 984 | 831* | 13 | 33 (5) | 4 |

\* A publicação pela página é uma **previsão** feita com o medidor do ponto 1. O extrator oficial
é da nuvem `nuvem-tempo-publicacao-v1`, que **ainda não entregou** (o ramo está sem commits).
Só com este ramo, a publicação das 78 fica em **4** pelo livro, e **3** pela estrada real, porque o N37 não tem bytes para derivar. O livro do coletor existe para os 984;
o texto derivado existe para 813 (191 derivados faltam no armazém).

**Índice (BASE='INDICE'): não dá sem rede.** Das 38 fontes das 78, 31 têm `INDEX_URL` no
contrato, e **só 1 teve a página de índice guardada** (IT-T5-025, 3 vezes, e como se fosse
notícia). O livro não anota a data que aparece ao lado do link. → proposta D.

## 7. PARADO — precisa de decisão (propostas, sem código aplicado)

**B · as duas bases que a Sala não tem onde guardar.** A Sala tem colunas `fact_time_basis` e
`fact_location_basis`, mas não tem `published_at_basis` nem `source_location_basis`. Hoje o
**valor** chega à Sala e a **base** para na porta. Para o T3 e para a sede, a base dá para
reconstruir a partir do `source_id` e do contrato. Para a data de publicação da página (JSON-LD
ou meta tag), a base **não** dá para reconstruir. Por isso: **instalar B antes de ligar o
extrator da nuvem.**

```sql
-- 033_a_sala_guarda_a_base_da_publicacao_e_da_sede.sql  (proposta, NAO aplicada)
alter table public.sala_de_espera
  add column if not exists published_at_basis    text not null default 'NAO SEI',
  add column if not exists source_location_basis text not null default 'NAO SEI',
  add column if not exists completude_tempo_lugar json not null default '"NAO_SEI"'::json;
```
Código que muda: `admissao.CAMPOS_READY` e `sala_de_espera.CAMPOS_READY` (19 → 22), o
insert/select de `_Postgres.pousar/ler`, e `pronto_para_inteligencia` a escrever
`completude_tempo_lugar(...)`. As linhas antigas ficam com o default.

**C · atualizar as 78 (e o acervo) com histórico. O caminho oficial NÃO existe.**
A Sala só sabe `pousar` (inserir), `ler`, `listar_pendentes` e `retirar`. Pior, medido no código:
reprocessar pela estrada oficial **reaproveita** o texto derivado (mesmo pai, mesmo extrator), o
item volta com o mesmo nome, e `pousar` responde `JA_NA_SALA_POR_OUTRA_CORRIDA`: **não grava
nada**. As 78 continuariam `NAO SEI`. Proposta: uma tabela que só acrescenta,
`sala_de_espera_revisao` (`run_id, ordem, revisao, campo, valor, base, extrator, versao_do_extrator,
reprocessado_em, corrida_de_reprocessamento`), e uma vista `sala_de_espera_atual` com a última
revisão por campo. **O RAW não muda. A linha antiga não muda. Nunca há UPDATE calado.**

**D · a data do índice (coletas futuras).** O coletor abre o `INDEX_URL` e joga a página fora.
Proposta: guardar a página de índice como RAW próprio, com o tipo `INDEX`, e anotar no livro a
data que aparece ao lado de cada link, com `PUBLISHED_AT_BASIS='INDICE'`.

**E · D62 no coletor (risco medido, 0 casos).** `coleta/italy_pilot_collect.mjs:1066-1070`: nos T3
a identidade é montada com a data. Se a data não for lida, o documento é **descartado sem
guardar os bytes** (`IDENTITY_FAILED`). No livro vivo há 85 desses descartes, **todos de páginas
HTML pelo endereço, nenhum por data**. Proposta: guardar os bytes na mesma, como
`FORWARD_IDENTITY_UNPROVEN` (o estado já existe em `raw_asset`). É a lei da identidade, então é
decisão do dono.

## 8. Coordenação — para não haver dois desenhos

- **LUGAR-FATO (`lugar-fato-v1`)**: o extrator dela está ligado aqui, num sítio só
  (`orquestrador._fato_do_texto`). Pedidos para ela: o padrão «ex X, oggi Y» (§5); as formas da
  D63 que ela ainda não conhece («la scorsa settimana», «lunedì scorso»); e a semana passada
  sai como semana ISO (`2026-W37`), que é intervalo e não dia inventado, mas a D63 fala em
  «início–fim». Se o dono quiser `2026-09-07/2026-09-13`, é uma linha lá.
- **nuvem-tempo-publicacao-v1**: o encaixe é o livro. O coletor escreve `PUBLISHED_AT` +
  `PUBLISHED_AT_BASIS` na observação, e `italy_executor.tempo_e_lugar` passa-os tal e qual (teste
  `test_valor_do_coletor_com_base_atravessa_tal_e_qual`). Para o acervo já coletado, o sítio é o
  mesmo, lendo os bytes guardados. **Precisa de B antes.**
- **nuvem-quatro-chaves-sala-v1 / quatro-chaves-v1** (cultura, região, fase, janela na
  Admission/Sala): o comum é (1) **uma migração só** para as colunas novas da Sala, B + as dela,
  com o mesmo número 033, e não duas; (2) o mesmo transporte: um dicionário por unidade que
  atravessa derivação e estruturação, e um tradutor só (`ingresso.para_a_porta`); (3) **a região
  dela é do FACTO, nunca a sede** — a mesma lei `SOURCE_LOCATION != FACT_LOCATION`, e ela pode
  ler `FACT_LOCATION` daqui em vez de medir de novo; (4) a mesma regra da D62, em que falta de
  dado não barra.

## 9. Provas fora do Git (caminho + sha256)

Pasta: `C:/Users/London1/auditoria-madrugada/tempo-lugar/`

```
c84e35f731d4963cdc435cb684262f8129ded5516a9f4c43b7e8c0b8114a4999  sala78.json            (dump só-leitura das 78, com texto)
8436cee66df9eb5b08dbf2812b1c587f2627083a919daa302fd6bebe27886ac4  raw-todos.json         (raw_asset, só-leitura)
acd7d7876ef719b340a453ba46c11d54eeab8de2bf96432b2065f759f3b136fb  derivados-todos.json
221914a2777673647e3d8420ebc6267d9cf2ca8cadd0f4e761be8473916da9a0  livro-vivo-copia.ndjson (cópia do livro do vivo)
87b58831e8a6f6e4475926f53d996237cda6fb65d736b7f4290dc39dec1df2c4  contratos-sl.json
5805fed5f049e5fb7c1ebe63181d21f773d07a6e36e23a1bb7a51f209d2aa3de  index-urls.json
458bce921fed8f13c8f1029a2260ba19a550f359ba11eea143364f72e235c938  medida-antes.json      (ponto 1)
538541290fa0d2d50dc927417fbbf13fc4448693ddaa126333e53d457bf47c6e  replay-base.json       (§4 base)
ecb63af93768f3fb175886536eef3a85e0935503a6c6259072a9bfc63eb22366  replay-novo.json       (§4 novo)
6dd3a5ee476a13100a70871a927b61e5cf4872b7905f37407b205b7c7092d3f9  acervo-previsao.json   (§6)
```

## EM PALAVRAS SIMPLES

- **O que estava errado:** a data e o lugar se perdiam no caminho, como um recado passado de mão
  em mão que ninguém repete. Não era falta de informação em todos os casos. Em parte, ela existia
  e ninguém passava adiante.
- **O que eu consertei:** agora cada etapa repassa o recado até a porta da Sala, e cada valor vai
  com a sua "etiqueta de origem" (a base). A data de publicação nunca vira data do fato. O
  endereço de quem publica nunca vira lugar do fato. Tem 13 "sabotagens de propósito" no código,
  e os testes pegaram as 13.
- **Quanto melhora, nas 78 notícias da Sala:** com o que está pronto neste ramo, medido passando
  pela estrada de verdade num banco de teste: a data de publicação de **3**, o lugar de quem
  publica de **4**, a data do fato de **14** e o lugar do fato de **1**. (Uma notícia, a N37, não
  tem o arquivo original guardado; contando o caderno do robô, seriam 4, 5, 15 e 1.) Das 15
  datas do fato, li uma a uma: 10 certas e 5 erradas. Quando chegar o leitor de data das
  páginas (de outra equipe), a data de publicação passa para **36 de 78**.
- **O que o dono pediu e já está feito:** item sem data **não é mais barrado**. Cada item agora
  pode dizer "de quatro coisas, sei estas". E "ieri" vira data, contada a partir da publicação,
  nunca a partir do dia em que o robô baixou a página.
- **O que parou e precisa de você:** (B) a Sala não tem gaveta para a etiqueta de origem de duas
  das datas; é preciso criar duas gavetas novas no banco (migração). (C) Não existe um jeito
  oficial de corrigir uma notícia que já está na Sala guardando o histórico. Proponho um
  "caderno de correções" que só acrescenta páginas e nunca apaga a antiga. Sem ele, reprocessar
  as 78 não muda nada na Sala.
- **O que foi perdido ou quebrou:** nada. Não escrevi na Sala, não mexi no robô que está
  rodando, e todo o ensaio foi feito num banco de teste que desliguei e apaguei no fim.
