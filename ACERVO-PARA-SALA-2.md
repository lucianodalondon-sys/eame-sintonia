# ACERVO-PARA-SALA-2 — atacar os dois maiores buracos, sem rede

Ramo `acervo-para-sala-2-v1`, a partir do vivo `69b0e23f` (com os commits de `acervo-para-sala-v1` por cima,
fast-forward). **NÃO instalado.** Sem rede; Sala real e RAW **não tocados** (Sala só em leitura: um `pg_dump`
com `default_transaction_read_only`). O ensaio correu com o `LOCK-PESADO` (11:58:41 → 13:27:42), num Postgres
descartável, desligado no fim.

## EM PALAVRAS SIMPLES

**O número que o dono pediu: 12 itens novos entrariam na Sala hoje** (no ensaio, 88 → 100). Destes 12:

- **5** têm a data em que foram publicados;
- **0** têm a data do fato;
- **0** têm o lugar do fato;
- **cultura: 0 pela estrada instalada hoje.** O código que escreve a cultura (D84) ainda não foi instalado; em
  todas as 94 linhas da Sala real a cultura está "NÃO SEI". **Se o D84 for instalado, 4 dos 12** teriam cultura:
  oliveira, nos 4 boletins de clima da ARPAV (IT-T2-002).

Antes eram 4 itens. Três coisas mudaram:

1. **O erro era meu.** Na missão anterior eu disse que 178 corridas eram recusadas por "envelope sem fonte". Era
   defeito do **meu** ensaio: ele misturava o livro de corridas dentro do livro de observações, como pôr as notas
   fiscais dentro do caderno de receitas. Corrigido. Agora **323 de 387 corridas chegam à porta** (antes, 66).
2. **T1 (cultura) e T11 (evento) ganharam executor**: uma linha, o mesmo coletor que já as tinha colhido. As 45
   corridas chegam à porta. Resultado: **0 SIM** (T11: 30 vídeos barrados pela porta "capa"; T1: 16 NÃO, 6 NÃO SEI).
3. **As 13 páginas "sem texto" dão texto** com o leitor de hoje. Só nunca tinham sido lidas. Resultado:
   **2 SIM** (estão nos 12), 6 NÃO, 5 NÃO SEI.

**Os 612 vídeos do YouTube: 0 entram, e o motivo não é o texto.** Eu ensinei o leitor a pegar a descrição que o
autor escreveu, que já estava guardada dentro da página: 495 das 612 páginas têm descrição com 40 letras ou mais.
Mas os 612 são barrados **antes** do texto ser lido, por uma porta que pergunta "isto é uma matéria ou uma capa?"
(capa = a primeira página de um jornal, só com links). O detector olha só os parágrafos visíveis da página. No
vídeo, o texto mora num script, e o detector vê só 209 letras. Resultado: "capa" nas 612.

Essa porta é do Curator, e mudá-la é decisão do coordenador. Medi as duas saídas mínimas **sem mudar nada**:

| opção | o que muda | passam a porta | SIM na régua |
|---|---|---|---|
| hoje | nada | 0 de 612 | 0 |
| **A** | o detector conta a descrição do vídeo como parágrafo | 74 | **2** |
| **B** | página `watch?v=` é UM vídeo, nunca uma lista: a pergunta capa/matéria não se aplica | 612 | **5** |

Mesmo na opção B só entram 5, porque:
- **193 vídeos** são de universos **sem régua escrita**: T12 política (118), T8 agricultor (45), T11 evento (30);
- **cerca de 290** caem em "não achei nada do assunto". Um canal de consórcio de vinho fala de degustação, não
  das palavras de "cooperativa".

**Transcrições guardadas: 0 dos 612.** Procurei em 2.246 arquivos, em todas as pastas. Transcrever exige baixar o
áudio, ou seja, rede. Fica para outra missão.

**Para aplicar os 12 de verdade, há um passo antes**:
- **16 das 18 corridas** que dão os 12 itens **não estão no livro do vivo**; só existem em pastas de outras sessões.
- Aplicando hoje, só entrariam **5 dos 12**.
- Fiz a ferramenta `trazer_livro.py`: ela traz essas linhas e os arquivos, conferindo a impressão digital (sha256)
  de cada um. **Sem `--aplicar` só conta.**
- Testei numa cópia: trouxe 25 + 16 linhas e 10 arquivos, e na segunda vez não fez nada.

**O que continua sem saída** (não é defeito escondido, é falta de peça):
- o PDF escaneado da IARA Aosta (IT-T5-007) é uma foto de papel e precisa de leitura de imagem (OCR), que não está
  instalada nesta máquina;
- a planilha CSV de 4,6 MB do Ministério da Saúde (IT-T4-001) não tem leitor na estrada (defeito já conhecido);
- **63 corridas** não têm nenhuma linha em livro nenhum (balcão vazio);
- **1 corrida** quebra no defeito já anotado em `coleta/ingresso.py:913` (`CONTENT_TYPE` duas vezes).

## 1 · O defeito do ensaio (o meu)

`provas/acervo_para_sala_ensaio.py` reunia os livros de outras pastas assim: para `observations.ndjson` **e** para
`runs.ndjson`, lia **todos** os padrões de `--livros`. Os recibos de corrida (`runs.ndjson`, sem `SOURCE_ID`)
entravam no livro de observações. `italy_executor.colher` fazia de cada recibo uma unidade, e
`leis/retorno_da_coleta` recusava o envelope inteiro: «COLHEITA[i]: unidade colhida sem SOURCE_ID».

A prova: na v2, `DE_OUTRAS_PASTAS` era **1.146 nos dois livros**. Nenhuma linha de observação destas corridas
está sem `SOURCE_ID` em livro nenhum; o recibo `IT-T10-2026-09-20-112556-…` está em `runs.ndjson`.

Conserto: só o livro **do mesmo nome** (`os.path.basename(padrao) != nome → continue`). Na v3: 1.057 + 253.

Segundo defeito, apanhado a medir a cultura: o `psql()` do ensaio lê em modo texto, e o **CR** dentro do texto da
Sala virava fim de linha. A linha partia-se calada. Agora todas as colunas saem sem TAB/LF/CR.

## 2 · T1 e T11 ganham o coletor de sites

`pedido/receitas.py`: `for _u in ("T1", "T8", "T9", "T11", "T12")`. É o gesto da D48, sem executor novo. Cada
fonte continua a passar pelo portão do Curator; sem `--filtro fonte=` o coletor recusa alto (sem
`filtros_por_omissao`). Teste `T1eT11` + `OResto` atualizado.

## 3 · A descrição do vídeo

- `coleta/texto_fonte.descricao_do_youtube(dados)`: **pergunta** a `coleta/youtube_janela.titulo_e_descricao_do_video`,
  a mesma função do EXTRATOR-EVENTO-V2 (`6971ddb1`), **copiada igual byte a byte**
  (`git diff 6971ddb1 -- coleta/youtube_janela.py` = vazio). Assim os dois ramos juntam-se sem conflito e há um
  dono só. Só o `shortDescription`: não é transcrição, legenda nem comentário.
- `limpar()` acrescenta a descrição **depois** do texto de antes. Página sem `videoDetails` = texto igual ao de antes.
- `executor_texto_de_html.receita(dados)`: a receita do derivado ganha `VIDEO_DESCRIPTION_OWNER` **só** quando a
  descrição entrou. Sem isto, a mesma receita a dar outro texto seria `DERIVATION_DRIFT`; nas outras páginas a
  receita é a de antes e o derivado antigo é `REUSED`.
- Teste `tests/test_descricao_do_youtube.py` (8), com excerto real (IT-T7-015, raw 201, sha256 `cf60e168…`).
- **Hoje isto não põe nenhum vídeo na Sala** (secção 5). Serve às opções A e B, e ao leitor do fato.

## 4 · Os 15 «sem texto»

| | quantos | o que acontece |
|---|---|---|
| HTML | 13 | o extractor de hoje dá texto (1.879 a 32.846 caracteres); nunca tinham sido derivados. Na porta: **2 SIM**, 6 NÃO, 5 NÃO SEI |
| PDF IT-T5-007 | 1 | `Sharp Scanned ImagePDF`, sem camada de texto → precisa de OCR; `tesseract` não existe nesta máquina (instalar = rede) |
| CSV IT-T4-001 | 1 | `text/csv` 4,6 MB, sem executor (MISSING_ROUTE conhecido) |

Os 26 JSON «sem texto» que não são do YouTube são recibos do coletor (560–905 bytes), não documentos.

## 5 · O ensaio (`ENSAIO-REPROCESSO-V3.json`)

Cópia da Sala: `sala-copia-2.dump` (sha256 `62102455…`, 10:49). Árvore: `69b0e23f` + este ramo.

| | v2 (missão anterior) | **v3** |
|---|---|---|
| corridas | 341 | 387 (+ os SEM_TEXTO) |
| passam a porta | 66 | **323** |
| envelope recusado | 178 | **0** |
| sem executor | 50 | **0** |
| balcão vazio | 47 | 63 |
| rebentou (`ingresso.py:913`) | — | 1 (`CANARIO-AQD-P3-…`) |
| Sala nova | +4 | **+12** |
| idempotência (5 corridas outra vez) | +0 | **+0** |

Os 12, por grupo de antes: NÃO 4 (IT-T2-002, boletins ARPAV) · NÃO SEI 3 (IT-T10-022) · novo derivado 3 ·
nunca perguntados 2 (IT-T2-001 ARPAE, IT-T10-015). Por universo: T10 6 · T2 5 · T5 1.

Decisões por conteúdo (`DECISOES-DO-ENSAIO-3.json`, 1.292):

| grupo de antes | SIM | NÃO | NÃO SEI | NÃO SE APLICA |
|---|---|---|---|---|
| YouTube (612) | 0 | **612** (porta capa) | 0 | 0 |
| já julgados (ADMISSAO) | 7 | 120 | 95 | 73 |
| nunca perguntados (outros) | 3 | 59 | 28 | 6 |
| sem texto (13 HTML) | 2 | 6 | 5 | 0 |

(«SIM» por conteúdo inclui os que já estavam na cópia com outro `item_id`; a medida da Sala é a de cima.)

## 6 · A cultura (`provas/acervo_para_sala_cultura.py`)

A estrada do vivo não escreve as quatro chaves. O medidor importa o D84 (`extratores-v2-juntos` `efb78e60`) de uma
**cópia**, aplica-o ao mesmo texto que o ensaio pousou, e não escreve em lado nenhum.

- **Conferência na Sala real (94 linhas):** o D84 aceitaria 92, com cultura em 45; nos universos T2+T3 dá **6**, o
  número que o relatório do D84 dá («Sala T3/T2 cultura 1→6»).
- **Nos 12:** o D84 aceita os 12, com cultura em **4** (`olive`, `drupe`: IT-T2-002) e data do fato em 0.

## 7 · Para o coordenador aplicar (nada foi aplicado)

1. Backup da Sala (`backup_sala.cmd`).
2. `py scripts/acervo_para_sala/trazer_livro.py --arvore <vivo> --lista scripts/acervo_para_sala/LOTE-12-ITENS.json --dados <pasta com raw.json> --livros "<globs>" --raizes "<raízes>"`
   mostra o plano (medido hoje no vivo: 25 + 16 linhas, 25 bytes em 10 ficheiros, 0 conflitos, 0 não achados).
   Com `--aplicar --recibo <out>`: só acrescenta e nunca escreve por cima (`open(..., "xb")`).
3. `py scripts/acervo_para_sala/reprocessar_lote.py --arvore <vivo> --lista scripts/acervo_para_sala/LOTE-12-ITENS.json [--aplicar]`
   → Sala +12 esperado (+5 se o passo 2 não for feito).

O código deste ramo (descrição, T1/T11) **não é necessário para estes 12**. Estes 12 saem do vivo tal como está,
com o livro completo.

**Decisões que são do coordenador / dono:**
- **Porta capa para vídeos:** opção A, B ou nenhuma (`OPCOES-CAPA-VIDEO.json`).
- **Régua para T8, T11 e T12:** sem ela, 193 vídeos ficam em «não se aplica» em qualquer opção.
- **OCR:** instalar um leitor de imagem (exige rede), para o PDF escaneado.

## 8 · Provas

| | resultado |
|---|---|
| `tests/test_descricao_do_youtube.py` (novo) | 8/8 |
| `tests/test_receita_web_t8_t9_t12.py` (+ T1eT11) | 11/11 |
| mutação (`medidas-2/mutar.py.txt`) | **6/6 mortos por falha de asserção** (sem o acrescento · descrição antes · receita sempre · receita nunca · T1/T11 fora · título no lugar da descrição) |
| regressão: 26 ficheiros de teste (html/texto/deriv/ingresso/youtube/receita/pedido), vivo × ramo | 645 × 654 testes; **os mesmos 12 vermelhos pelo nome** (herdados) |
| `test_proveniencia` 5 falhas, `test_estagio_atravessa_a_fronteira` 1 erro | iguais em `a75588e8` (herdados) |

Entradas fora do Git com sha256: `scripts/acervo_para_sala/ENTRADAS-2.sha256`. Medidas e saídas:
`scripts/acervo_para_sala/medidas-2/`.

## 9 · O que isto NÃO prova

- As opções A/B foram medidas com a régua **sem** a porta inteira (sem banco). O ensaio é que conta o que entra;
  A/B é previsão.
- O LOCK-PESADO estava com 0 bytes desde 11:40:14, sem Postgres descartável ligado. Renomeei-o para
  `LOCK-PESADO-orfa-0bytes-1140.txt`, **não o apaguei**, e deixei uma nota. Outra missão (NUVEM-CONCORRENZA)
  pegou o lock a seguir; esperei a vez.
- A Sala real tem 94 linhas e **88 itens distintos** (medido: `count(*)=94`, `count(distinct item_id)=88`); o
  ensaio mede contra os 88. Nenhum dos 12 `item_id` está na Sala real (SELECT só-leitura).
- `derived:1084`, `derived:1751` e `derived:1753` nasceram na cópia (o maior `derived_artifact.id` real é 1063):
  na aplicação real o número será outro. O conteúdo é o mesmo (a mesma receita sobre o mesmo sha256).
