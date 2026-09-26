# ACERVO-PARA-SALA · porque 1.158 documentos guardados não estão na Sala, e quantos podem entrar sem ir à internet

Ramo `acervo-para-sala-v1`, a partir do vivo `83de0ccd`. **Só leitura e sem rede**:
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

**Quantos DESSES a porta aceita de verdade** só o ensaio diz (secção 4).

## 4. O ensaio (Postgres descartável)

ENSAIO_AQUI

## 5. Roteiro de reprocesso para o coordenador

Pré-requisito: a decisão sobre o livro (secção 3). Sem ela, só os 260 do livro vivo.

1. **Preflight e backup.**
   - `preflight_sala.cmd` → PASS;
   - `backup_sala.cmd` → um `.dump` novo, com o sha256 anotado.
2. **Robô parado.** Criar `PARAR.flag` no vivo e confirmar que o supervisor e o observador pararam: 0 processos
   do coletor.
3. **Rede fechada**, como no ensaio (`HTTP(S)_PROXY=http://127.0.0.1:9`). Reprocessar não é colher.
4. **Por corrida**, na árvore do vivo (`source-curator-service-v1`), com `SINTONIA_SALA_BACKEND=POSTGRES`,
   `SINTONIA_SALA_DSN` e `SINTONIA_COLLECTION_DSN` da Sala real, e `SINTONIA_ARMAZEM_RAIZ` do armazém real:

   ```
   py -B -c "from coleta import italy_executor as ix; ix.colher('<RUN_ID>')"
   py -B orquestrador/orquestrador.py <apelido do universo> --so-a-porta --colheita-da-corrida=<RUN_ID> ^
       --filtro fonte=<SOURCE_ID> --filtro universo=<Tn>
   ```

   - A lista de `<RUN_ID>, <SOURCE_ID>, <Tn>` é a do ensaio (`PASSAGENS`).
   - O apelido é: T1 cultura · T2 clima · T3 praga · T5 ciencia · T7 cooperativa · T8 agricultor ·
     T9 concorrente · T10 mercado · T11 evento · T12 politica.
5. **Validação** (SELECT, só leitura):
   - `select count(*) from sala_de_espera` = antes + as novas do ensaio;
   - as linhas antigas iguais byte a byte (md5, como na verificação da 033);
   - `etapa_da_corrida` com ADMISSION nas corridas reprocessadas;
   - cada linha nova com SIM no livro de decisões (0 bypass).
6. **Outra vez as 5 primeiras corridas** → Sala +0 (idempotência).
7. **Religar**: tirar `PARAR.flag`.
8. **Desfazer**: restaurar o `.dump` do passo 1 (`pg_restore` sobre uma base recriada, com o serviço parado,
   como em `ensaio_offline.Base.restaurar`). A Sala só acrescenta, e as linhas novas são a única diferença.

## 6. Evidência

- `scripts/acervo_para_sala/classificar_fora_da_sala.py` · `MOTIVOS-FORA-DA-SALA-V1.json` · `ENTRADAS.sha256`.
- `provas/acervo_para_sala_ensaio.py`: o ensaio (secção 4).
