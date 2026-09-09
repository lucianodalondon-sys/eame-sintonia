# STORIES sem Apify — a pesquisa e a decisão

Medido em **2026-09-09**. Uma página, não uma tese.

## A tabela

| candidato | licença | senha? | cookie exportado? | stealth/proxy/CAPTCHA | marca visto? | expiração nativa | requisições | veredito |
|---|---|---|---|---|---|---|---|---|
| **Instaloader 4.15.3** | MIT | não | não (lê o navegador no disco) | nenhum | **não** (documentado e confirmado no código) | `expiring_utc` | **1 por lote de 50** | **ESCOLHIDO** |
| gallery-dl 1.32.11 | GPLv2-only | não (upstream removeu) | não (lê o navegador no disco) | nenhum | não | `expires` | 1 por conta | fallback, só como processo |
| instagrapi 2.18.19 | MIT | **sim** | — | **emulação de Pixel 8 Pro, proxy, reCAPTCHA e selfie numa classe base** | `story_seen()` existe | **perde** | — | **RECUSADO** |
| CDP no navegador local | nossa | não | não | nenhum | **abrir Story conta visualização** | — | muitas | saúde de sessão e descoberta de ID |
| Graph API oficial | — | — | — | — | — | — | — | só a própria conta, nunca terceiro |

## O que decidiu, e não foi preço

`get_stories(userids=[...])` aceita **ID numérico** e pula a resolução de username.
Uma chamada GraphQL para até 50 contas, contra uma busca de perfil por conta. O
endpoint de perfil é justamente o ponto quente de HTTP 429 relatado em 2026.

```
CACHE O ID UMA VEZ. NUNCA MAIS RESOLVA USERNAME.
```

O instagrapi foi recusado por desenho, não por configuração: senha obrigatória,
dispositivo emulado, proxy embutido e resolução de CAPTCHA numa classe base. Não
existe subconjunto dele que obedeça às regras desta casa.

## A medição que mudou a lei de mídia

Nenhuma das três bibliotecas expõe o texto escrito na tela do Story. O motivo é da
plataforma: ali a palavra é **pixel queimado na imagem**. OCR está fora por decisão.

```
NO STORY, TEXTO DE TELA NÃO É TEXTO. É IMAGEM.
```

Portanto o caminho do **áudio deixa de ser exceção e passa a ser o normal**. A porta
de texto continua no código porque quando abre é a rota mais barata — mas planejar
como se ela fosse a comum seria planejar errado.

## Riscos registrados, não escondidos

- O `query_hash` de Story do Instaloader é o **último consumidor do mecanismo legado**
  e não é tocado desde 2024, enquanto perfil e post migraram para `doc_id` em 2026.
- gallery-dl tem quebra **aberta desde 2026-09-04** (#9731), falhando mesmo com cookie.
- **Toda** rota de Story exige sessão autenticada. Não existe rota anônima, nem para
  conta pública. A conta usada carrega risco de suspensão, seja qual for a ferramenta.

## Técnica e política são respostas separadas

```
TECHNICAL_STATUS = rota escolhida por medição; NÃO executada ao vivo
POLICY_STATUS    = REQUIRES_AUTHORIZATION
```

A Meta declara que coleta automatizada não autorizada pode violar os Termos, inclusive
autenticado. Não há permissão expressa provada. Isso não é motivo para parar a
engenharia, e também não é motivo para escrever `POLICY_ALLOWED = YES`.

## Por que não houve prova viva

O runner local (`eame-sintonia-local-2`, o PC do Luciano) estava **offline**: a corrida
do canário ficou na fila desde 03:30 UTC sem ser recolhida.

```
RUNNER_UNAVAILABLE != CREDENTIAL_MISSING != ROTA IMPOSSÍVEL
```

Sem esse PC não há Chrome autenticado, e sem ele nenhuma das rotas próprias pode ser
provada. Este ambiente também não tem `ffmpeg` nem `faster-whisper`.
