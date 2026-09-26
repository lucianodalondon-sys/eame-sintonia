# ACERVO-TEMPO-LUGAR · o tempo e o lugar do acervo que NÃO está na Sala

Ramo `acervo-tempo-lugar-v1`, a partir do vivo `ce28040c`. **Só leitura e sem rede**:
- a Sala real foi lida por `SELECT` com `default_transaction_read_only=on` e copiada por `pg_dump`, também só
  leitura;
- RAW, derivados, Sala e armazém **não foram tocados**;
- os ficheiros lidos ficam fora do Git, em `C:/Users/London1/reproc-acervo/`, com o sha256 de cada um escrito em
  `scripts/reproc_acervo/ACERVO-TEMPO-LUGAR-V1.json`.

## 1. O que se mediu, e com que código

- **O acervo hoje (26/09, 00h):**
  - 1.562 linhas de `raw_asset`, que são **1.246 conteúdos diferentes**. A mesma página guardada em corridas
    diferentes tem o mesmo sha256.
  - Na Sala: 94 linhas (88 conteúdos).
  - **Fora da Sala: 1.158 conteúdos (1.413 linhas de RAW).**
- **O código é o INSTALADO**, pela mesma estrada da produção (`scripts/reproc_acervo/prever_acervo.py`):
  - `coleta/italy_executor.tempo_e_lugar(obs, bytes_da_pagina)` → data de publicação e lugar da fonte;
  - `orquestrador._fato_do_texto(texto, …)` → data e lugar do fato (LUGAR-FATO).

  Os ficheiros de tempo e lugar são iguais em `e5cd691f` e no vivo de hoje, `ce28040c` (git diff vazio).
- **Os bytes estão espalhados.** A conta procurou em 31 pastas, e **só aceitou um ficheiro se o sha256 batesse** com
  o do banco:
  - 1.058 no armazém da Sala (`sintonia-sala-italia/armazem`);
  - 164 em três árvores de trabalho antigas (`duas-portas-v1`, `lote-76-v1`, `it-trunk-v1`);
  - **24 conteúdos sem bytes** em lado nenhum.
- **A prova de que a conta é a do vivo:** nas 94 linhas que já estão na Sala, a previsão dá **exatamente o que a Sala
  guardou, nos quatro campos — 94 de 94 iguais**.

## 2. Quantos ganham cada campo (fora da Sala)

| campo | conteúdos que saem de NAO SEI | de 1.158 |
|---|---|---|
| **data de publicação** | **241** | 20,8 % |
| lugar da fonte | 11 | 0,9 % |
| **data do fato** | **66** | 5,7 % |
| **lugar do fato** | **79** | 6,8 % |
| data do fato calculada («ieri», «la settimana scorsa»…) | 0 | — |

Para comparar, **dentro** da Sala (88 conteúdos): publicação 44, lugar da fonte 4, data do fato 20, lugar do fato 18.

Porque tão pouco sai de NAO SEI fora da Sala:
- **737 dos 1.158 são YouTube** (612 páginas de vídeo + 125 JSON da API). O texto guardado de uma página de vídeo
  quase nunca diz uma data ou um lugar de facto.
- **172 são JSON** (125 do YouTube) e **não têm texto derivado**: o leitor do facto não tem o que ler.
- 24 não têm bytes; 189 não têm texto derivado.

## 3. ⚠️ O maior ganho possível não é meu: a data de publicação do YouTube

Das 612 páginas de vídeo do YouTube fora da Sala, **603 trazem a data de publicação escrita no HTML**
(`<meta itemprop="datePublished" content="AAAA-MM-DD…">`, e também `uploadDate`). O extrator instalado
(`coleta/executor_texto_de_html.tempo_de_publicacao`) lê JSON-LD, `article:published_time` e `<time>`, **mas não
esta marca**. Com ela, a data de publicação fora da Sala passaria de **241 para cerca de 844** (de 21 % para 73 %).

Pela **DA-6**, o dono do extrator de publicação é a nuvem **tempo-publicacao**. **Não mexi nele**: fica como
proposta para ela. Os 125 JSON do YouTube não têm `publishedAt` dentro e continuam sem data.

## 4. Por fonte (fora da Sala): as 68 fontes com algum ganho

As outras **113** fontes não ganham nenhum campo. Quase todas são páginas de vídeo, JSON ou páginas sem data nem
facto no texto. A tabela das 181 está em `ACERVO-TEMPO-LUGAR-V1.json → POR_FONTE_FORA_DA_SALA`.

| fonte | conteúdos | com texto | data de publicação | lugar da fonte | data do fato | lugar do fato |
|---|---|---|---|---|---|---|
| IT-T7-017 | 74 | 69 | 74 | 0 | 11 | 4 |
| IT-T10-018 | 37 | 35 | 36 | 0 | 8 | 9 |
| IT-T7-042 | 27 | 26 | 27 | 0 | 9 | 17 |
| IT-T10-022 | 23 | 21 | 22 | 0 | 0 | 0 |
| IT-T7-033 | 14 | 14 | 14 | 0 | 5 | 2 |
| IT-T2-034 | 9 | 9 | 9 | 0 | 3 | 3 |
| IT-T9-009 | 4 | 4 | 4 | 0 | 2 | 2 |
| IT-T2-025 | 14 | 14 | 0 | 0 | 0 | 6 |
| IT-T10-021 | 7 | 7 | 0 | 0 | 3 | 2 |
| IT-T2-037 | 4 | 4 | 4 | 0 | 1 | 0 |
| IT-T7-125 | 3 | 3 | 3 | 0 | 0 | 2 |
| IT-T2-051 | 9 | 9 | 0 | 0 | 2 | 2 |
| IT-T2-006 | 4 | 4 | 0 | 0 | 4 | 0 |
| IT-T7-043 | 3 | 3 | 0 | 0 | 2 | 2 |
| IT-T7-019 | 3 | 3 | 3 | 0 | 0 | 1 |
| IT-T7-049 | 3 | 3 | 3 | 0 | 0 | 1 |
| IT-T2-008 | 2 | 2 | 2 | 0 | 0 | 2 |
| IT-T1-021 | 2 | 2 | 0 | 0 | 2 | 2 |
| IT-T10-013 | 2 | 2 | 2 | 0 | 0 | 2 |
| IT-T2-032 | 5 | 5 | 0 | 0 | 2 | 1 |
| IT-T2-145 | 3 | 3 | 3 | 0 | 0 | 0 |
| IT-T12-130 | 3 | 3 | 3 | 0 | 0 | 0 |
| IT-T2-146 | 3 | 3 | 3 | 0 | 0 | 0 |
| IT-T7-103 | 3 | 3 | 3 | 0 | 0 | 0 |
| IT-T7-139 | 3 | 3 | 3 | 0 | 0 | 0 |
| IT-T5-186 | 1 | 1 | 1 | 0 | 1 | 1 |
| IT-T10-017 | 15 | 15 | 0 | 0 | 0 | 2 |
| IT-T12-011 | 15 | 15 | 0 | 0 | 2 | 0 |
| IT-T2-007 | 2 | 2 | 2 | 0 | 0 | 0 |
| IT-T3-014 | 2 | 2 | 2 | 0 | 0 | 0 |
| IT-T3-015 | 2 | 2 | 2 | 0 | 0 | 0 |
| IT-T1-003 | 2 | 2 | 2 | 0 | 0 | 0 |
| IT-T1-013 | 2 | 2 | 2 | 0 | 0 | 0 |
| IT-T1-022 | 2 | 2 | 2 | 0 | 0 | 0 |
| IT-T7-112 | 2 | 2 | 0 | 0 | 1 | 1 |
| IT-T12-117 | 2 | 2 | 2 | 0 | 0 | 0 |
| IT-T2-014 | 1 | 1 | 0 | 0 | 1 | 1 |
| IT-T1-009 | 1 | 1 | 0 | 0 | 1 | 1 |
| IT-T10-012 | 1 | 1 | 0 | 0 | 1 | 1 |
| IT-T11-005 | 1 | 1 | 0 | 0 | 1 | 1 |
| IT-T12-006 | 1 | 1 | 0 | 0 | 1 | 1 |
| IT-T2-026 | 15 | 15 | 0 | 0 | 0 | 1 |
| IT-T8-005 | 15 | 15 | 0 | 0 | 0 | 1 |
| IT-T12-014 | 15 | 15 | 0 | 0 | 0 | 1 |
| IT-T12-016 | 15 | 15 | 0 | 0 | 0 | 1 |
| IT-T7-021 | 5 | 5 | 0 | 0 | 1 | 0 |
| IT-T7-118 | 2 | 2 | 0 | 0 | 0 | 1 |
| IT-T2-010 | 1 | 1 | 1 | 0 | 0 | 0 |
| IT-T2-024 | 1 | 1 | 0 | 0 | 0 | 1 |
| IT-T3-018 | 1 | 1 | 0 | 0 | 1 | 0 |
| IT-T3-019 | 1 | 1 | 1 | 0 | 0 | 0 |
| IT-T1-002 | 1 | 1 | 1 | 0 | 0 | 0 |
| IT-T1-008 | 1 | 1 | 0 | 0 | 0 | 1 |
| IT-T1-010 | 1 | 1 | 0 | 0 | 0 | 1 |
| IT-T1-018 | 1 | 1 | 0 | 0 | 0 | 1 |
| IT-T10-011 | 1 | 1 | 1 | 0 | 0 | 0 |
| IT-T2-030 | 1 | 1 | 1 | 0 | 0 | 0 |
| IT-T7-031 | 1 | 1 | 0 | 0 | 0 | 1 |
| IT-T7-040 | 1 | 1 | 1 | 0 | 0 | 0 |
| IT-T10-020 | 1 | 1 | 0 | 0 | 1 | 0 |
| IT-T12-009 | 1 | 1 | 1 | 0 | 0 | 0 |
| IT-T12-137 | 1 | 1 | 1 | 0 | 0 | 0 |
| IT-T2-002 | 4 | 4 | 0 | 4 | 0 | 0 |
| IT-T2-004 | 3 | 1 | 0 | 3 | 0 | 0 |
| IT-T4-001 | 1 | 0 | 0 | 1 | 0 | 0 |
| IT-T3-005 | 1 | 0 | 0 | 1 | 0 | 0 |
| IT-T3-008 | 1 | 0 | 0 | 1 | 0 | 0 |
| IT-T2-001 | 1 | 1 | 0 | 1 | 0 | 0 |

## 5. Vinte lidos à mão (fora da Sala)

Escolhidos de forma fixa (pela ordem do sha256): 7 com data do fato, 7 com lugar do fato, 6 com data de publicação.
**A leitura é minha, pelos trechos e pelo HTML; pode ter erro de um ou dois.**

**Resultado: 15 certos, 2 meio certos, 3 errados.**

| nº | campo | fonte | valor | veredito | porquê |
|---|---|---|---|---|---|
| 1 | data do fato | IT-T2-037 | 2025 | certo | resultados do monitoramento das águas da Toscana **em 2025** |
| 2 | data do fato | IT-T7-033 | 17 febbraio | certo | abertura do evento Chianti Classico (o texto não diz o ano) |
| 3 | data do fato | IT-T7-042 | 7-9 ottobre 2026 | certo | congresso MS Food Day |
| 4 | data do fato | IT-T7-042 | 27 settembre 2026 | certo | Acetaie Aperte |
| 5 | data do fato | IT-T1-021 | 24-27 settembre 2026 | certo | Salone del Gusto, Turim |
| 6 | data do fato | IT-T7-017 | annata 2022 | **errado** | é a **safra** do vinho lançado num jantar, não a data do facto |
| 7 | data do fato | IT-T2-006 | 21 settembre | certo | o incêndio «la sera dello scorso 21 settembre» |
| 8 | lugar do fato | IT-T2-014 | Molise | **errado** | «Bollettino Ufficiale della Regione Molise» é onde a lei foi **publicada** (a âncora «bollettino» do leitor italiano) |
| 9 | lugar do fato | IT-T10-017 | Bergamo | certo | morangos no **mercado** de Bergamo |
| 10 | lugar do fato | IT-T7-042 | Modena | meio | vem de «Aceto Balsamico **di Modena**» (nome do produto); o evento é mesmo em Modena |
| 11 | lugar do fato | IT-T2-034 | Pesaro ; Marche | certo | convegno em Pesaro |
| 12 | lugar do fato | IT-T7-017 | Milano | certo | DEGU-STAZIONI em Milão |
| 13 | lugar do fato | IT-T9-009 | Piacenza | certo | Piacenza Expo |
| 14 | lugar do fato | IT-T7-042 | Modena | meio | o mesmo caso do 10 |
| 15 | publicação | IT-T2-037 | 2026-09-17 | certo | JSON-LD = data visível na página |
| 16 | publicação | IT-T2-145 | 2026-09-23 | certo | «Data di pubblicazione: 23 settembre 2026» |
| 17 | publicação | IT-T3-014 | 2022-08-09 | **errado** | a página é o **login** («Account area riservata»): a data existe, mas não é notícia |
| 18 | publicação | IT-T7-042 | 2026-06-25 | certo | = «25 giugno 2026» visível |
| 19 | publicação | IT-T2-008 | 2026-09-15 | certo | página do evento ARPAT |
| 20 | publicação | IT-T7-033 | 2025-07-17 | certo | JSON-LD = article:published_time |

Dois dos três erros já têm nome e dono:
- o nº 8 é a âncora «bollettino» do leitor italiano, que também pega «Bollettino **Ufficiale**» (o diário oficial);
- o nº 17 é uma página que não é notícia: o juiz de capa/matéria devia tê-la barrado antes.

## 6. Onde isto fica: a proposta de migração 034 (decisão do coordenador/dono)

**O problema.** A 033 dá casa ao tempo e ao lugar das linhas **da Sala** (revisões). Para o acervo fora da Sala não há
linha para rever, e **o RAW nunca se altera**.

**A casa que já existe.** `derived_artifact` é o filho de um RAW, com:
- pai declarado e conferido pela chave estrangeira;
- produtor, versão do produtor, parâmetros e sha256 dos bytes;
- idempotência: `derivacao_e_unica_por_regua` não deixa a mesma régua produzir o mesmo filho duas vezes.

**O que falta é uma palavra.** O tipo (`kind`) do derivado é um vocabulário **fechado** de 7 palavras
(TEXT_EXTRACTION, OCR, TRANSCRIPTION, TRANSLATION, THUMBNAIL, FRAME, TABLE_EXTRACTION). Nenhuma é «tempo e lugar»,
e usar outra seria mentir sobre a espécie do filho.

**A proposta** (`supabase/migrations/034_o_acervo_guarda_tempo_e_lugar_como_derivado.sql`):
- o vocabulário ganha **`TEMPO_LUGAR`**;
- o filho seria um JSON com os quatro campos do contrato comum (`PUBLISHED_AT`, `SOURCE_LOCATION`, `FACT_TIME`,
  `FACT_LOCATION`), **cada um com a sua base**, mais a evidência do leitor e a proveniência (a observação do livro e
  o texto usados);
- `producer_version` = sha256 do código que o produziu; `parameters_hash` = sha256 das entradas (sha do RAW, do texto
  derivado e da observação);
- **UNKNOWN não funde nem vira facto**: NAO SEI fica NAO SEI com o porquê;
- nenhuma linha existente muda; só o vocabulário cresce. Tecnicamente é «DROP + ADD» da mesma restrição, numa
  transação, porque o Postgres não alarga um CHECK no lugar.

**O desfazer** (`supabase/desfazer/034_desfazer.sql`) repõe o vocabulário antigo e **recusa-se** se já houver algum
derivado TEMPO_LUGAR: apagá-los seria perder evidência. Nesse caso, o caminho é o backup.

**⚠️ Número.** A «lápide da retenção» (`033_a_lapide_da_retencao.sql`) está em **6 ramos** (canais-pessoas-v1,
pessoas-agro-v1, reparo-fontes-v1, retencao-youtube-v1, youtube-canario-v1, youtube-pronto-v1) e **não** entrou no
vivo. Quando entrar, precisa de outro número, e vai colidir com esta 034. **Quem decide a ordem é o coordenador.**

**O que NÃO fiz:** o escritor dos derivados TEMPO_LUGAR. Só depois de o dono decidir a 034. Seria uma chamada ao dono
da escrita dos derivados (`guarda/preservar_derivado.py`) com a saída de `prever_acervo.prever()`.

### 6.1 O ensaio da 034 em Postgres descartável

ENSAIO_034_AQUI

## 7. Plano (se a 034 for aprovada)

1. Coordenador: escolher o número (034 ou outro), por causa da lápide da retenção.
2. `backup_sala.cmd` → aplicar a migração pela cadeia → os SELECTs de validação do ensaio.
3. Escritor TEMPO_LUGAR (missão nova): para cada RAW com bytes, um filho TEMPO_LUGAR pela porta dos derivados.
   Correr duas vezes deve inserir 0 na segunda.
4. Antes do escritor, se o dono quiser o ganho grande: a leitura de `itemprop="datePublished"` pela nuvem
   tempo-publicacao (secção 3).
5. Desfazer: `034_desfazer.sql` (recusa se houver filhos); senão, restauro do backup.

## 8. Evidência

- `scripts/reproc_acervo/prever_acervo.py`: a previsão, só leitura.
- `scripts/reproc_acervo/ACERVO-TEMPO-LUGAR-V1.json`: contas, por fonte, conferência 94/94, os 20 lidos e os 1.246
  itens com trechos curtos.
- Fora do Git: `C:/Users/London1/reproc-acervo/` (raw.json, derivados.json, sala.json, sala-copia.dump), com o
  sha256 no JSON acima.
- `provas/migracao_034_ensaio_copia.py`: o ensaio.
