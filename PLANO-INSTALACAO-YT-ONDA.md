# PLANO (SÓ PAPEL) — YT-ONDA: os 11 canais YouTube, depois da entrega D36 do engenheiro do Scrap

Pedido: coordenação de 25/09 (D36). **Nada instalado. Nada corrido na rede para isto.**
Entrega do engenheiro: `origin/yt-metadados-v1` @ **8c4dfc1e** (blocos A, B, B2, C e D36(a)).
A `regua_social.py` não existe na produção: ela entra com `social-onda2-v1`. Por isso a ordem é
**LI-ONDA (social-onda2-v1) primeiro, YT-ONDA (yt-metadados-v1) por cima.**
Produção medida: bot @ **7b769819** (FILA-ÚNICA instalada; candidatas 932 → 1199).

## 1 · A junção yt-metadados-v1 por cima de social-onda2-v1 (calculada, não feita)
`git merge-tree --write-tree social-onda2-v1 origin/yt-metadados-v1` → conflitos de CÓDIGO = **0**.
Só conflitam as geradas do mapa (12 json + 1 doc), refeitas pela cadeia. A `curadoria/regua_social.py` foi mexida
pelos dois lados e juntou sozinha: a junção tem a `FASES_EQUIVALENTES` (D36) **e** a `fase_do_contrato` + `--vivo`.
Contra a produção 7b769819, a yt-metadados-v1 também junta sem conflito de código.

Testes na árvore juntada (`C:/ens-yt`): **211 corridos, 210 OK, 1 FAIL** — e o FAIL é informação, não defeito:
```
curadoria.test_soc2_curator_youtube.test_o_scrap_declara_a_rota_hoje
   esperava CLASSE = OFFICIAL_API_FREE (API, playlistItems.list); a matriz diz hoje PUBLIC_NATIVE
   (ROTA = youtube:pagina-publica-do-canal — a lista SEM chave do bloco B)
```
**Ajuste que a junção leva** (1 linha, no teste da SOC2):
`self.assertEqual(DECLARADO["CLASSE"], "PUBLIC_NATIVE")`, e o comentário diz que a fase `canal-youtube`
passou a listar pela página pública (bloco B, robots conferido), sem chave.
Mutação na árvore juntada: D36 **9/9** mortos · D37 **6/6** mortos.

⚠️ **Efeito colateral medido:** o contrato guarda `ROTA_DECLARADA_PELO_SCRAP`. Os contratos escritos antes da junção
(`youtube-data-api-v3:playlistItems.list`) passam a ser recusados no VALIDATE_ROUTE («o Scrap declara hoje a rota
youtube:pagina-publica-do-canal e o contrato foi escrito para …»). **Na produção há 0 contratos `SCRAP_FASE`**
(medido no livro do Curator e na tabela onboarded), portanto nada que corre hoje parte. Os contratos dos ensaios
são refeitos pelo worker depois da junção, com a rota nova.

## 2 · O registo dos 11 canais pela porta canónica — DEPOIS da FILA-ÚNICA (já instalada)
Ensaio em cópia fiel da produção (`C:/ens-li2`, 7b769819 + os 14 livros), **sem rede** (proxy fechado),
com o worker filtrado às tarefas do YouTube (`curadoria/ensaio_so_linkedin.py --tipo YOUTUBE`):
```
semear_qualify_social --tipo YOUTUBE     64 QUALIFY novas (canal conhecido + site oficial aponta para ele)
ensaiar_qualify_youtube --reabrir        21 QUALIFY reabertas (bloqueadas com a frase antiga «YouTube exige channel_id…»)
worker (so YouTube, sem rede)            QUALIFY 71 OK + 15 BLOCK · BUILD_CONTRACT 11 · VALIDATE_ROUTE 11
numeros novos                            11, todos CANARY_PENDING (os outros 60 canais ja eram fonte)
comparados com o ensaio de 24/09         9 iguais · 2 TROCADOS entre si: IT-T5-165 <-> IT-T5-166
```
**O número depende da ORDEM da fila.** No ensaio de 24/09, LinkedIn e YouTube foram qualificados juntos. Aqui, o
LinkedIn veio primeiro e as 21 reabertas antes das novas. Consequência:
- os alvos do canário do YouTube **leem-se do livro da produção depois do QUALIFY**, nunca da lista do ensaio;
- a prova D36 do engenheiro (IT-T9-029, IT-T5-165, IT-T3-025) não pode ser reaproveitada por número: para
  `IT-T5-165` o canal mudou (UCXUG… → UCJ8R…). A régua D36 apanharia a troca (compara o CHANNEL_ID do contrato
  com o do item) — daria FALHA, não um READY errado.

## 3 · WRITESET
| passo | escreve | quando | livros do vivo |
|---|---|---|---|
| junção (código) | 26 ficheiros do yt-metadados (coleta/adaptador_youtube, ferramentas/youtube_transcrever, leis/social_matriz, curadoria/regua_social, testes, provas, docs, mapa) + a linha do teste SOC2 | bot parado | 0 |
| `semear_qualify_social.py --tipo YOUTUBE --aplicar --vivo` | `LIFECYCLE-QUEUE` (+64) | bot parado | 1 |
| `ensaiar_qualify_youtube.py --reabrir` | `LIFECYCLE-QUEUE` (21 BLOCKED → PENDING) | bot parado | 1 |
| worker (depois de relançar) | `SOURCE-ID-ALLOCATION` (+11), `italy_contracts_curator.json` (+11), `LIFECYCLE-*` | o bot | os de sempre |
| canário (orquestrador, banco descartável) | nada no vivo (corre numa cópia com os livros do vivo) | com rede | 0 |
| `regua_social.py --aplicar --vivo` | `LIFECYCLE-LEDGER/-EVIDENCE` | bot parado | 2 |

## 4 · Os passos (coordenador), depois da LI-ONDA instalada
1. Junção `yt-metadados-v1` sobre a linha que já tem `social-onda2-v1` + o ajuste de 1 linha + a cadeia do mapa (PASS). Instalar como na LI-ONDA.
2. Bot parado: `semear_qualify_social.py --tipo YOUTUBE --aplicar --vivo` e `ensaiar_qualify_youtube.py --reabrir`. Relançar.
3. Esperar o worker IDLE. Ler os 11 números **do livro vivo** (FAMILY YOUTUBE, CANARY_PENDING).
4. **Canário (rede, pelo portão de consenso):** por canal, `canal-youtube` (a lista pela página pública, 1 visita a
   youtube.com) e depois `audio-youtube` de 1 vídeo (yt-dlp, som público, D17.4), banco descartável.
   **≤ 5 visitas a youtube.com por noite** → 11 canais × 2 = 22 visitas = **5 noites** (lotes de 2 canais),
   salvo decisão do coordenador sobre como contar as visitas.
5. Bot parado: `regua_social.py --aplicar --vivo` (D36: o áudio vale pela fase `canal-youtube` só com as 4 provas no item).
6. Portão e `plano_onda_social.py` (só plano).

**Previsão honesta:** o engenheiro mediu 3 canais com o bloco A: RAW 1 em cada, e os 3 READY pela D36 na cópia dele.
O nosso canário de 24/09 (sem bloco A): 11/11 RAW, 11/11 transcrição, 4 na Sala. Com as duas coisas, o esperado é
**até 11 prontas**. O número real só sai do canário da produção. Por vídeo: 1 som, 1 transcrição (GPU); Sala
conforme a Admissão (4/11 no canário).
