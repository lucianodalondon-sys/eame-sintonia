# RELATÓRIO SOC-TEMPO-E-LUGAR (D61/D62/D63) — 25/09

Ramo `social-tempo-v1`, a partir de `origin/social-onda2-v1` @ 7570ef61. O ramo da nuvem `nuvem-social-integrado-v1`
continua sem a junção social (290e7349). Por cima: os 5 commits de código do `yt-metadados-v1` (blocos A, B, B2, C
e D36), por cherry-pick. Só conflitaram as geradas do mapa, refeitas pela cadeia. **Rede FECHADA** o tempo todo.
Nada no vivo nem na Sala real.

⚠️ **Correção ao texto da missão:** `coleta/adaptador_linkedin.py:1786` é o **LUGAR** (`source_location=None`), não a
data. A **data** do LinkedIn já chegava à Sala: medido nas Salas descartáveis de 24/09, 2 de 2 itens com `published_at`.

## 1 · LinkedIn
- **Data de publicação:** existe, servida sem login. Vem do JSON-LD `VideoObject.datePublished` da página pública do
  POST (`coleta/adaptador_linkedin.py::video_do_post`). No bruto real de 24/09
  (`data/samples/SOCIAL-IT/raw-free/LINKEDIN/post-7490681050906439680__…txt`): `2026-08-05T08:12:12.630Z`, até ao segundo.
  **Agora o objeto leva ainda:** `PUBLISHED_AT_SOURCE` (a base: «PLATAFORMA — LinkedIn, pagina publica do post,
  JSON_LD_VideoObject.datePublished») e `PUBLISHED_AT_PRECISION` (`precisao_da_publicacao`: SECOND / MINUTE / DAY /
  NAO DECLARADA — a mesma régua do YouTube, sem arredondar para cima).
- **Lugar da organização:** o coletor não o lê da página. Vem do **site oficial que prova a conta**
  (`leis/lugar_da_organizacao.py`, novo), por esta ordem:
  (1) sede no cadastro-mestre (`owners[].PROVINCE` do dono com o mesmo site) → PROVINCE;
  (2) `COUNTRY` da ficha do site no Atlas → COUNTRY;
  (3) NÃO SEI, com o porquê.
  **Nunca** o `REGION` do Atlas (é cobertura ou lugar dos factos), nunca o `COUNTRY_SCOPE` nem o egresso (é onde NÓS
  pedimos), nunca o nome. O robô de fontes grava-o no contrato social (`BUILD_CONTRACT`), e o Scrap lê-o do contrato
  quando a observação não o traz (`coleta/scrap_colheita.py::unidade`, como já faz com a regra do DOCUMENT_ID).
  **Cobertura medida nas 48 contas (37 LinkedIn + 11 YouTube):** PROVINCE 3 (YouTube: crea.gov.it → Roma,
  arpae.it → Bologna, regione.sicilia.it → Palermo) · COUNTRY «ITALY» 34 (30 LinkedIn + 4 YouTube) ·
  NÃO SEI 11 (7 LinkedIn + 4 YouTube), com o porquê.
  **ESPERA REDE:** a morada que a própria página da empresa no LinkedIn serve (se o JSON-LD `Organization.address`
  vier sem login) não está medida. Não há página de empresa guardada no repositório e a rede está fechada.
- **FACT_TIME / FACT_LOCATION:** só do texto do post, pelo extrator da LUGAR-FATO (`lugar-fato-v1`,
  `leis/fato_do_texto.py::campos_do_fato(texto, publication_time, publication_time_basis)`). **D63:** ele só conta
  «ieri» / «la scorsa settimana» a partir de uma publicação PROVADA — data ISO **e** base. É exatamente o par que
  agora chega à porta (`published_at` + `published_at_basis`, e a precisão).

## 2 · YouTube
- **Data de publicação:** o `yt-dlp` devolve `timestamp`/`upload_date`, e o bloco A do engenheiro (`coleta/adaptador_youtube.py:771`,
  `ferramentas/youtube_transcrever.declarado_em`) já a punha no objeto, com `PUBLISHED_AT_PRECISION` (SECOND/DAY) e
  `PUBLISHED_AT_SOURCE`. **Agora atravessa com a base**: `scrap_colheita` traduz `PUBLISHED_AT_SOURCE` →
  `PUBLISHED_AT_BASIS`, e o `ingresso` → `published_at_basis`.
- **Lugar do canal:** o mesmo caminho do LinkedIn — o site oficial que aponta para o canal (D21). **ESPERA REDE:** o
  país que a página «about» do canal declara não está medido.

## 3 · As leis, uma a uma
- **PUBLICATION_TIME != FACT_TIME:** a data de publicação nunca vira data do facto. Mutante «a hora da coleta vira
  publicação» (D63) → MORTO.
- **SOURCE_LOCATION != FACT_LOCATION:** o lugar vem da organização, nunca do texto, nunca do pedido. Mutantes
  «o país do pedido vira lugar da fonte» e «a região de cobertura vira morada» → MORTOS.
- **D62, nunca descartar por falta de dado:** ausência sai NÃO SEI **com o porquê**. Nada é recusado por não ter lugar.
- **Precisão por item:** `PUBLISHED_AT_PRECISION` e `SOURCE_LOCATION_PRECISION` em cada objeto. Uma base sem o valor
  que prova não atravessa (mutante → MORTO).

## 4 · O que chega à SALA, e o que ainda não
- Colunas que já existem e agora recebem: `published_at` (LinkedIn, e YouTube com o bloco A) e `source_location`
  (quando o contrato o declara).
- **A base e a precisão param na PORTA.** O item da Admissão já as tem (`published_at_basis`,
  `published_at_precision`, `source_location_basis`, `source_location_precision`), mas a Sala **não tem colunas**
  para elas: `admissao.py::unidade` (1893-1918) e a migração 032 só conhecem `published_at`/`source_location`.
  **Um dono só para essa migração:** a nuvem `nuvem-tempo-publicacao-v1` (encanamento da PUBLICATION_TIME; ainda
  sem commits). Duas frentes a mexer em `admissao.py` + `sala_de_espera.py` + uma migração cada dariam conflito.
  Os nomes estão fixados aqui, e são os mesmos que o extrator da LUGAR-FATO pede.
- «Quando colhemos» continua em duas colunas conforme a plataforma: `observed_at` (LinkedIn) e `captured_at`
  (YouTube áudio). Dono: a fronteira do ingresso.

## 5 · PEDIDOS_POR_HOST para as corridas do Scrap — PROPOSTA (não feita)
A prova-teto (`provas/prova_teto_dominio.py`) lê, do `data/collection-ledger/italy/runs.ndjson`, uma linha por
corrida com `RUN_ID` e `CORTESIA.PEDIDOS_POR_HOST`. O transporte web escreve-a no fim de cada corrida, também quando
ela rebenta a meio (`coleta/italy_pilot_collect.mjs:1301-1327`, prova `provas/corrida_abortada_local.mjs`). O Scrap
não escreve nada. O mínimo:
1. **Contar** — `coleta/scrap_http.py`: o abridor instalado (`_PortaoEmCadaSalto`, já a única porta de
   `urllib.request.urlopen`) soma 1 por pedido real, por host sem `www.`, incluindo saltos e retentativas, num contador
   do processo. O `orcamento_de_rede` já existe mas conta o TOTAL, e ninguém o liga.
2. **Escrever** — `coleta/scrap_colheita.py::main`, num `finally`: acrescenta ao `runs.ndjson` (o mesmo `LEDGER_DIR`,
   respeitando `ITALY_OPS_ROOT`) `{RUN_ID, STARTED_AT, FINISHED_AT, EXECUTOR: "scrap-colheita", FASE, SOURCE_ID,
   CORTESIA: {PEDIDOS_POR_HOST, TETO_CONTA_POR}, ABORTED?}`.
3. **Não mentir** — na fase `audio-youtube`, o `yt-dlp` faz os pedidos dele fora do `scrap_http`
   (página, player e stream em `googlevideo.com`). Aí a linha leva `PEDIDOS_NAO_CONTADOS: "yt-dlp"` e **não**
   leva `PEDIDOS_POR_HOST`: a prova-teto dá NAO_SEI, que é a verdade, até o `yt-dlp` ser contado (`--print-traffic`
   ou um proxy local que conte).
4. **Travar** (D38) — o mesmo contador, lido contra `SINTONIA_TETO_ONDA` (o livro da onda do transporte web), recusa
   o pedido acima de 5 por domínio registável.
Dono: o engenheiro do Scrap. Prova sugerida: a de `corrida_abortada_local.mjs`, em Python, com um servidor em 127.0.0.1.

## Testes e mutação (rede fechada)
`tests/test_soc_tempo_publicacao_e_lugar.py` (11, com o bruto real do LinkedIn, o cadastro-mestre e o Atlas) ·
`curadoria/test_soc_onda2_social.py` (+2: o contrato guarda o lugar) · `provas/_mutantes_soc_tempo.py` **7/7 mortos** ·
suítes sociais e do YouTube: 147 OK.
