# ACERVO-PARA-SALA · porque 1.158 documentos guardados não estão na Sala, e quantos podem entrar sem ir à internet

Ramo `acervo-para-sala-v1`, a partir do vivo `83de0ccd` e rebaseado sobre o vivo `69b0e23f` (lote 1 da INTEGRA). **Só leitura e sem rede**:
- a Sala real foi lida por `SELECT` com `default_transaction_read_only=on`;
- o livro de decisões e os livros do coletor foram lidos, não escritos;
- RAW, derivados, Sala e armazém **não foram tocados**;
- os ficheiros lidos ficam em `C:/Users/London1/acervo-para-sala/`, com o sha256 de cada um em
  `scripts/acervo_para_sala/ENTRADAS.sha256`.

## 1. De onde se sabe cada coisa

| pergunta | fonte |
|---|---|
| o que existe | `raw_asset` 1.562 linhas = **1.246 conteúdos** (sha256 distintos); `derived_artifact` 1.063 |
| o que está na Sala | `sala_de_espera_atual`: 94 linhas (88 conteúdos) → **1.158 fora** |
| o que a Admissão disse, e quando | `data/samples/LIVRO-DE-DECISOES.json` do vivo (sha256 `a02db40c…`): 1.400 decisões, **454 sobre derivados** (311 derivados distintos) |
| até onde cada corrida chegou | `etapa_da_corrida`: etapa RAW em 450 corridas, DERIVED em 432, **ADMISSION em só 6** |
| se há bytes e texto | a previsão do ACERVO-TEMPO-LUGAR (sha256 conferido em 31 pastas) |
| se a observação está no livro | `observations.ndjson` do vivo e de ~160 pastas de trabalho |

O classificador é `scripts/acervo_para_sala/classificar_fora_da_sala.py`. O resultado item a item (motivo, fonte,
classe, corrida, decisão) está em `scripts/acervo_para_sala/MOTIVOS-FORA-DA-SALA-V1.json`.

## 2. Porque estão fora: um motivo por documento

A ordem é esta, e vale o primeiro que se aplica: sem bytes → sem texto → a Admissão respondeu → nunca foi
perguntado.

| motivo | quantos | dos quais YouTube |
|---|---|---|
| **NUNCA PERGUNTADO**: há texto, e nenhuma decisão no livro. A corrida parou no DERIVADO: das **218 corridas** deles, **todas** têm etapa RAW e DERIVED, e **nenhuma** tem ADMISSION | **709** | 612 |
| **SEM TEXTO**: não há derivado de texto, e a porta não tem o que ler | 166 | 125 |
| · JSON (125 da API do YouTube + 26 outros) | 151 | 125 |
| · HTML cuja extração não deu texto | 13 | — |
| · CSV · PDF | 1 · 1 | — |
| **A ADMISSÃO DISSE NAO** | 138 | 0 |
| · «não pertence ao universo» | 123 | |
| · «não é matéria» (capa, contatos…) | 15 | |
| **A ADMISSÃO DISSE NAO_SEI** | 111 | 0 |
| · «pertence ao universo?» sem sinais bastantes | 101 | |
| · «é matéria?» sem prova | 10 | |
| **A ADMISSÃO DISSE NAO_SE_APLICA** (universo sem régua) | 11 | 0 |
| **SEM BYTES** em lado nenhum (sha256 não bate em nenhuma das 31 pastas) | 23 | 0 |
| **total** | **1.158** | **737** |

**Marcas à parte** (não são motivo, e um documento pode ter várias):
- **DUPLICADO_DE_URL: 205.** O mesmo endereço tem mais de um conteúdo, porque a página mudou entre corridas.
- **1** tem o mesmo endereço de um documento que já está na Sala.
- **SIM fora da Sala: 0.** Nenhum documento com SIM ficou de fora; não há desvio.

**Por classe T** (a do SOURCE_ID):

| classe | nunca perguntado | NAO | NAO_SEI | NAO_SE_APLICA | sem texto | sem bytes |
|---|---|---|---|---|---|---|
| T1 | 20 | | | | 7 | 7 |
| T2 | 85 | 19 | 19 | 2 | 4 | 4 |
| T3 | 12 | | | | 6 | 4 |
| T4 | | | | | 1 | |
| T5 | 50 | 1 | 2 | | 109 | 2 |
| T7 | 245 | 96 | 47 | | 28 | 1 |
| T8 | 47 | | | | 2 | 1 |
| T9 | 50 | 1 | 1 | | | |
| T10 | 45 | 18 | 42 | | 9 | 4 |
| T11 | 31 | | | | | |
| T12 | 124 | 3 | | 9 | | |

Por fonte, e com a corrida de cada item: `MOTIVOS-FORA-DA-SALA-V1.json → POR_FONTE / ITENS[].RUN_IDS`.

**As corridas que os trouxeram.** Quase todas são `coleta/italy_executor.py`, «HTTP direto», gratuito, com as
missões do Atlas:

| missão | documentos nunca perguntados |
|---|---|
| TECHNICAL NETWORK | 245 |
| POLICY | 124 |
| CLIMATE/WATER/SOIL | 85 |
| SCIENCE | 50 |
| COMPETITORS | 50 |
| FARMERS | 46 |
| MARKET | 45 |
| EVENTS | 31 |
| CROP | 20 |
| PEST | 12 |

A maior parte é de **20/09**, antes de existir a ponte do DERIVADO até à porta.

## 3. Para cada motivo: entra por reprocesso canónico, ou precisa de conserto/decisão?

**Nenhum portão é afrouxado. UNKNOWN não vira facto.** «Reprocesso canónico» quer dizer a MESMA porta:
- `italy_executor.colher(RUN_ID)` refaz o balcão a partir do livro do coletor;
- depois `orquestrador --so-a-porta --colheita-da-corrida=RUN_ID`;
- o dono da Sala só escreve depois de um SIM.

É o método de `medidas/duas_portas_reprocessa.py`.

| motivo | quantos | caminho | porquê |
|---|---|---|---|
| NAO / NAO_SEI / NAO_SE_APLICA | 260 | **REPROCESSO CANÓNICO** (a mesma porta, régua de hoje, versão declarada) | todos têm a observação **no livro do vivo** (260 de 260). **138** foram julgados com a **versão 5** das réguas (18–22/09), 9 com a 7 e 113 com a 9; desde então mudaram T1, T2 e a palavra inteira. **O resultado pode mudar nos dois sentidos**, e isso mede-se, não se presume. |
| NUNCA PERGUNTADO, fora do YouTube | 97 | **REPROCESSO CANÓNICO, depois de uma DECISÃO sobre o livro** | há texto, a porta nunca o viu. Mas a observação de 96 deles **só existe em livros de outras pastas de trabalho** (1 em nenhum). Para a estrada canónica os ler, é preciso **juntar essas linhas ao livro vivo**: isso é escrever no livro do coletor, e a decisão é do coordenador. |
| NUNCA PERGUNTADO, YouTube | 612 | **DECISÃO** (e provavelmente conserto) | o texto guardado de cada página de vídeo é **só o título + o rodapé do YouTube** (~250 letras: «Informazioni Stampa Copyright…»). A porta aceita-o como legível, mas precisa de **2 sinais** do universo, e um título quase nunca os tem → espera-se NAO_SEI. Além disso: a observação só existe em livros de **outras pastas** (612 de 612), e o YouTube tem regras próprias (D20: metadados expiram em 30 dias; SOC3: retenção). A estrada certa para vídeo é a oficial (descrição, transcrição), não a página. |
| SEM TEXTO · JSON | 151 | **CONSERTO** | não há leitor de JSON → texto. Os 125 do YouTube são dados da API sem `publishedAt`. É uma derivação nova, não reprocesso. |
| SEM TEXTO · HTML/PDF/CSV | 15 | **CONSERTO técnico** | a extração falhou; pode refazer-se offline pelo executor canónico, a partir dos bytes que existem. |
| SEM BYTES | 23 | **FICA** | só uma nova coleta os traria (proibida aqui). |

**Resposta curta à pergunta «quantos podem entrar pela porta sem nova coleta»:**
- **candidatos imediatos: 260** (os já julgados; basta a régua de hoje);
- **mais 97** depois de juntar os livros;
- os 612 do YouTube só com decisão;
- 166 + 23 não entram sem conserto ou coleta.

**Quantos DESSES a porta aceita de verdade:** o ensaio mediu **4** (secção 4).

## 4. O ensaio (Postgres descartável)

Feito em 26/09 às 06:00–06:45, sob a LOCK-PESADO. Resultado em `scripts/acervo_para_sala/ENSAIO-REPROCESSO-V2.json`, e as decisões
que a porta escreveu **no livro da cópia** em `DECISOES-DO-ENSAIO-V2.json`.

**A montagem (tudo cópia; nada do vivo nem da Sala foi escrito):**
- **o código:** o vivo `69b0e23f` (que já traz o leitor-data-yt `4dd00308`) + `conserto-regua-v1 a139caad`, numa pasta local;
- **a Sala:** uma cópia só-leitura tirada às 05:40 (`pg_dump -Fc`, sha256 `687a135e…`), restaurada num Postgres descartável.
  Usei esta e não o backup de 19:33, que é anterior à 3.ª onda: com ele, o que a onda pôs pareceria entrar pelo reprocesso;
- **o livro reunido:** o livro do vivo + 1.146 linhas das mesmas corridas que só existem em livros de outras pastas;
- **os bytes:** no depósito do coletor dentro da árvore (1.136 ficheiros; 118 não existem em lado nenhum) e no armazém (2.260), todos com o
  sha256 conferido.

**As corridas:** as do banco e as do livro onde a impressão digital de cada documento aparece. O mesmo conteúdo foi muitas vezes colhido de
novo por uma corrida mais recente, e é essa que o livro conhece. Total: **341 corridas**, cada uma pela porta canónica, sem rede.

| o que aconteceu | corridas | porquê |
|---|---|---|
| **passaram pela porta** | **66** | a Admissão julgou os documentos |
| envelope recusado: «unidade colhida sem SOURCE_ID» | 178 | o livro antigo (20/09) tem unidades sem a fonte; a porta recusa o envelope inteiro («não se inventa uma fonte») |
| sem executor: «NAO SEI COMO» | 50 | T1 (cultura) e T11 (eventos) não têm executor declarado; a estrada não abre |
| balcão vazio | 47 | a corrida do banco não tem linha em livro nenhum |

**O que a porta respondeu, com as réguas de hoje, aos 260 «julgáveis já»:** **SIM 3** · NAO 117 · NAO_SEI 94 · NAO_SE_APLICA 46.

**O que entrou na Sala do ensaio: 4 linhas** (88 → 92 documentos; 94 → 98 linhas):

| item | fonte | o que é | publicação | data do facto | lugar do facto |
|---|---|---|---|---|---|
| derived:791 | IT-T10-022 | FEFAC e Sindirações assinam um MoU da indústria de ração | 2026-08-09 (JSON-LD) | NAO SEI | NAO SEI |
| derived:793 | IT-T10-022 | A Indonésia olha a China e o Médio Oriente para exportar frango | 2026-07-22 (JSON-LD) | NAO SEI | NAO SEI |
| derived:787 | IT-T10-022 | A produção de aves da UE sobe e o preço do frango desce | 2026-08-18 (JSON-LD) | NAO SEI | NAO SEI |
| (derivado novo) | IT-T10-022 | um 4.º texto extraído de novo no reprocesso | 2026-07-25 (JSON-LD) | NAO SEI | NAO SEI |

Li os três primeiros à mão (o texto guardado): são **matérias de verdade** da revista Zootecnica International (aves e ração), julgadas
SIM em T10 (mercado).

- ⚠️ **Foco:** a decisão de 23/09 tirou veterinária e saúde animal do foco. Aves e ração não são saúde animal, mas também não são lavoura.
  A porta aceita; se é foco, decide o dono. Não se afrouxa nem se aperta a porta aqui.
- ⚠️ **Data e lugar do facto NAO SEI, por defeito MEU (LUGAR-FATO):** o texto destas páginas vem numa linha só, e essa linha tem a
  palavra «Newsletter». O leitor do facto trata a linha inteira como rodapé e diz «o texto não tem corpo». É um conserto no meu
  `leis/fato_do_texto.corpo()`, para depois (não mexi hoje).

**Idempotência:** as 5 primeiras corridas outra vez → Sala **+0** (98 → 98).

**Um defeito real, achado pelo caminho** (`coleta/ingresso.py:913`): quando o ficheiro de uma observação não está onde o livro diz, o
ingresso monta a ficha com `CONTENT_TYPE="application/json"` **e** com o `CONTENT_TYPE` que a observação declarou. Resultado:
`TypeError … got multiple values for keyword argument 'CONTENT_TYPE'`, e a corrida quebra em vez de dizer «ficheiro ausente». No primeiro
ensaio isto partiu 57 corridas. A culpa foi da minha montagem (os bytes estavam fora da árvore), mas no vivo acontece a qualquer corrida
cujo ficheiro falte. Por isso uma corrida ficou fora do lote (abaixo).

## 5. Roteiro EXECUTÁVEL para o vivo — o LOTE dos «julgáveis já» (D82)

**O que entra (medido no ensaio): 4 documentos na Sala, todos T10, todos com data de publicação, 0 com data do facto, 0 com lugar do
facto.** Nenhum portão é afrouxado: é a mesma porta.

As **64 corridas** do lote estão em `scripts/acervo_para_sala/LOTE-260-CORRIDAS.json`. São as 66 que passaram pela porta no ensaio,
**todas com as observações no livro do próprio vivo** (324 ficheiros conferidos pelo sha256 na árvore do vivo), menos duas:
- `XX-T3-2026-09-18-171838…` (ARPAV): faltam-lhe 4 ficheiros no depósito do vivo, e cairia no defeito do `CONTENT_TYPE`;
- `OPS_forward-only-live_…`: o RUN_ID não traz classe T.

Nenhuma das duas traz nenhum dos 4.

Os 97 «nunca perguntados» ficam para depois: dependem de juntar os livros e de consertar o livro antigo (secção 3).

**Passos (na máquina do vivo, janela `cmd`):**

1. **Preflight e backup**
   ```
   %USERPROFILE%\sintonia-sala-italia\preflight_sala.cmd
   %USERPROFILE%\sintonia-sala-italia\backup_sala.cmd
   ```
   Anotar o nome do `.dump` novo e o sha256 dele.
2. **Robô parado:** criar `PARAR.flag` na raiz do vivo (`…\source-curator-service-v1\PARAR.flag`) e confirmar que o supervisor e o
   coletor pararam (0 processos do coletor).
3. **Conferir sem correr** (não escreve nada):
   ```
   cd %USERPROFILE%\orca\workspaces\eame-sintonia\source-curator-service-v1
   py -B <ramo acervo-para-sala-v1>\scripts\acervo_para_sala\reprocessar_lote.py --arvore . --lista <ramo>\scripts\acervo_para_sala\LOTE-260-CORRIDAS.json
   ```
   Tem de dizer 64 corridas e **nenhum** «NAO PRONTO». Conferido por mim às 06:50 contra o vivo real: só faltava o `PARAR.flag`.
4. **Correr:** o mesmo comando com `--aplicar --saida RECIBO-LOTE-ACERVO.json`.
   - O script fecha a rede no processo filho, usa `SINTONIA_SALA_BACKEND=POSTGRES`, a DSN de `SALA_DSN.txt` e o armazém de
     `~/sintonia-sala-italia/armazem`.
   - Para cada corrida chama `italy_executor.colher` + `orquestrador --so-a-porta`.
   - No ensaio levou cerca de 35 minutos (as 341 corridas); o lote de 64 deve levar menos.
5. **Validação** (só leitura):
   ```
   select count(*) from sala_de_espera;          -- antes + 4
   select item_id, source_id, published_at, fact_time, fact_location
     from sala_de_espera_atual where source_id = 'IT-T10-022' order by pousado_em desc limit 6;
   ```
   Conferir também:
   - no `RECIBO-LOTE-ACERVO.json`, nenhuma corrida com `EXIT` ≠ 0;
   - no `data/samples/LIVRO-DE-DECISOES.json`, as decisões novas com SIM = as linhas novas da Sala (0 desvios);
   - as linhas antigas da Sala iguais (md5, como na verificação da 033).
6. **Outra vez as 5 primeiras corridas** (a mesma lista cortada) → Sala **+0**.
7. **Religar:** apagar `PARAR.flag`.
8. **Desfazer, se preciso:** restaurar o `.dump` do passo 1 com o serviço parado (dropdb/createdb/pg_restore, como em
   `scripts/micro_coleta/ensaio_offline.py::Base.restaurar`). A Sala só acrescenta; as 4 linhas e as decisões novas são a única diferença.
   O `LIVRO-DE-DECISOES.json` e o `RUN-MANIFEST.json` do vivo ganham linhas novas: guardar uma cópia dos dois antes do passo 4.

## 6. Evidência

- `scripts/acervo_para_sala/classificar_fora_da_sala.py` · `MOTIVOS-FORA-DA-SALA-V1.json` · `ENTRADAS.sha256`.
- `provas/acervo_para_sala_ensaio.py` · `ENSAIO-REPROCESSO-V2.json` · `DECISOES-DO-ENSAIO-V2.json`: o ensaio (secção 4).
- `scripts/acervo_para_sala/reprocessar_lote.py` · `LOTE-260-CORRIDAS.json`: o roteiro executável (secção 5).
