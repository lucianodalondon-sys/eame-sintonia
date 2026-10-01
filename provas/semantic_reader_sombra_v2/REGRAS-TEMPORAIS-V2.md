# REGRAS TEMPORAIS DO SEMANTIC READER V2 (SOMBRA) — CONGELADAS ANTES DA 1ª RODADA
EXPERIMENTAL / NAO_PARA_CLIENTE · base c5db5eedd · decisão do dono 01/10 (V1 = baseline reprovado)

O defeito que a V2 corrige: a V1 achava UMA data escrita e preenchia FACT_TIME. A V2 primeiro
LISTA todas as datas escritas (por código), depois CLASSIFICA o papel de cada uma, e só um
candidato com papel FACT_TIME_OBSERVADO que também passe nos vetos do código pode alimentar FACT_TIME.

## 1. Quem faz o quê
- CÓDIGO (determinístico): encontra os candidatos no texto, mede POSICAO, TRECHO_LITERAL, VALOR
  normalizado, TEXTO_SHA256. O modelo nunca escreve trecho nem valor: só escolhe um papel por ID.
- MODELO (mecanismo, não fonte): devolve um TIPO por candidato + qual ID (se algum) é o tempo do fato.
- CÓDIGO (vetos duros, vencem o modelo): ver §3.
- ESTABILIDADE: 5 votos independentes por item; só sai FACT_TIME se ≥4/5 votos escolhem o MESMO
  VALOR e esse valor passou nos vetos. Senão NAO SEI (MOTIVO=SEM_MAIORIA_ESTAVEL). O trecho entregue é o
  candidato mais votado com esse valor (empate → primeira posição no texto), e o TIPO final dele (maioria ≥4/5)
  tem de ser FACT_TIME_OBSERVADO. Mesma entrada + mesma versão → mesmo resultado.

## 2. Tipos (vocabulário fechado)
- FACT_TIME_OBSERVADO — quando o fato principal foi observado, medido, cotado, aconteceu, ou a data
  "ao dia" de um estado declarado ("situazione al…", "rilevazione del…", "nel periodo dal … la coltura si
  trova…", "campagna 2025 conclusa"), terminando até a publicação.
- FORECAST_TIME — período/dia de previsão ou tendência (meteo, "tendenza", "previsioni", "attese").
- PUBLICATION_TIME — data de publicação/atualização/byline da página.
- VALIDITY_TIME — validade de norma, deroga, recomendação, prazo, scadenza.
- EDITION_PERIOD — número/data/período que rotula a EDIÇÃO de um periódico ("N.13 del 03/07/2026",
  "Settimanale N.37 · 09-15 settembre 2026", "Bollettino n. 4 del 3 marzo 2026"), salvo se o texto
  liga explicitamente esse período às observações.
- HISTORICAL_REFERENCE — passado citado como contexto (lei, decreto, recorde anterior, fundação, outro
  artigo, barra lateral, rodapé, copyright).
- COMPARATIVE_PERIOD — anos/semanas usados como termo de comparação ("settimane 33-41 del 2024, 2025 e 2026",
  "rispetto al 2025").
- NAO_SEI — papel não determinável.

## 3. Vetos do código (independentes do modelo)
- V-MULTIANO: candidato com ≥2 anos distintos (exceto safra "2025/26") → COMPARATIVE_PERIOD, inelegível.
- V-NORMA: na mesma oração (até 60 caracteres antes, cortados no último fim de linha, ")", ". " ou ";") há decreto/legge/legislativo/delibera/regolamento/
  direttiva/DD/DRD/DM/BURC/Gazzetta/circolare/determina → HISTORICAL_REFERENCE, inelegível.
- V-FUTURO: INICIO do candidato > data de referência (publicação; se a publicação é NAO SEI, a captura)
  → inelegível como observado ("período futuro em relação à publicação não vira observação passada").
  Um período que CONTÉM a referência (começou antes, termina depois) é período corrente, não futuro:
  continua elegível, com a marca TERMINA_DEPOIS_DA_REFERENCIA; se o modelo o chama FORECAST_TIME, cai.
- V-SEM-ANO: datas sem ano escrito NÃO são candidatos (não inferir data ausente; nenhum ano é emprestado
  de outra parte do texto).
- V-PUBLICACAO: a publicação (metadado) nunca é FACT_TIME, e um candidato que o modelo rotula
  PUBLICATION_TIME ou EDITION_PERIOD nunca alimenta FACT_TIME.
- Ambiguidade real (sem maioria ≥4/5, ou maioria em NAO_SEI) = NAO SEI.

## 4. Formato de cada candidato
VALOR (ISO: AAAA-MM-DD, AAAA-MM-DD/AAAA-MM-DD, AAAA-Www, AAAA-MM, AAAA, AAAA/AAAA) · TIPO · TRECHO_LITERAL
(fatia exata do texto) · POSICAO [início, fim] · TEXTO_SHA256.

## 5. Previsão registrada antes da rodada (para ninguém ajustar a régua depois)
- L30-21 (controle): o "valor certo" congelado no lote é "09 - 15 settembre 2026", que é o cabeçalho da
  edição de um boletim publicado em 09/09 cujo conteúdo é previsão até 15/09. Pela regra do dono
  (previsão/período futuro não vira observação), a V2 NÃO pode devolvê-lo. A régua congelada vai contar
  REGRESSAO aqui. Não ajusto o código para escapar disso: é conflito entre o lote e a regra, decisão do dono.
  Pela mesma lógica que o próprio lote usa no controle L30-22 (semana de dados observados "Dal 07-09 al
  13-09"), o observado de L30-21 seria "Dal 31-08-2026 al 06-09-2026" — o lote é internamente inconsistente aqui.
- L30-08 e L30-10 (alvos): os períodos escritos começam antes e terminam depois da publicação/captura →
  elegíveis só com TERMINA_DEPOIS_DA_REFERENCIA e se o modelo não os chamar previsão/edição.
- Datas de edição de boletim (L30-09, 14, 16, 19 e semelhantes) só passam se o modelo, em maioria estável,
  as ligar a observação; por regra elas são EDITION_PERIOD.
