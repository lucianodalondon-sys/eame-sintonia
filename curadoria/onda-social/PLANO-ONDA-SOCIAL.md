# PLANO DA ONDA SOCIAL NO VIVO (só papel) — ONDA-SOCIAL-PREP, 25/09

Leitura do vivo (bot @ **df0865e6**) **só leitura**, rede FECHADA. Nada instalado, nada corrido.
Estado conta a conta: `curadoria/onda-social/ESTADO-VIVO.json`.

## 1 · O estado de hoje (livro vivo)
| grupo | contas | SOURCE_ID hoje | tarefa no robô hoje |
|---|---|---|---|
| LinkedIn (organizações, identidade provada) | 37 | **nenhuma** | nenhuma — a ponte marca LinkedIn POLICY_BLOCK e nunca enfileira (D15) |
| YouTube (os 9 que ganharam número no ensaio de 7cdb7ea4) | 9 | **nenhuma** | 7 QUALIFY BLOCKED com a frase antiga «YouTube exige channel_id…» · 2 sem tarefa |
| YouTube (os outros 2 dos 11 canais: CAND-0221, CAND-0300) | 2 | nenhuma | BLOCKED; depois da T1 o site não dá UM território (D21) → decisão semântica |

**O que falta a cada uma, pela ordem:** instalar a junção social (d7e31802 + 8c4dfc1e) → semear/reabrir o QUALIFY
com o robô parado → o robô cunha o número (**não é o do ensaio**: a produção já mudou duas vezes a numeração) →
canário pelo orquestrador → `regua_social --vivo` → portão.

## 2 · Quem corre a onda — medido no código da produção
- **`ferramentas/big_collection/onda_web.py` NÃO serve a onda social.** Chama `micro_coleta.correr`, que monta o
  pedido do executor WEB (`italia-recorrente`) sem fase. Uma fonte social nem passa o plano dele (SEM_RECEITA_WEB).
- **O executor social que existe é `orquestrador` → `scrap-colheita`** (com o `promover_o_scrap` do ramo social,
  para qualquer território). Não há um condutor de onda social; hoje a corrida é UMA chamada ao orquestrador por conta,
  com o Pedido montado em processo (a frase da linha de comando polui o alvo — IT-T5-163 virou T1).
  Comando exato de uma conta (o `SID` e o `slug` saem do livro vivo depois do QUALIFY):
  ```
  py -c "import sys; sys.path[:0]=['.','orquestrador']; import _gavetas; import orquestrador as O; from pedido import Pedido;
  p=Pedido(alvo='<Tn>', filtros={'fase':'video-linkedin','fonte':'<SID>','pagina':'https://www.linkedin.com/company/<slug>/',
  'teto':'1','pais':'IT','universo':'<Tn>'}); r=O.correr(p); print(r['STATUS'], r['RUN_ID'])"
  ```
  YouTube: o mesmo, com `fase=canal-youtube` + `canal_id=<UC…>` (lista, página pública) e depois `fase=audio-youtube` +
  `video=<id>` de 1 vídeo da lista.

## 3 · ⚠️ D38 na onda social: hoje NÃO há trava nem prova — ESPERA ENGENHEIRO DO SCRAP
Medido em df0865e6:
1. **O teto por domínio é do transporte WEB.** `SINTONIA_TETO_ONDA` / `SINTONIA_TETO_POR_HOST` só são lidos por
   `coleta/italy_pilot_collect.mjs`. O Scrap (Python) não lê nenhum dos dois.
2. **O `orcamento_de_rede` do Scrap existe, mas conta o TOTAL e não é ligado.** `scrap_executor._com_teto_de_rede`:
   sem `teto_de_rede=`, «nada muda». O `scrap_colheita` nunca o passa.
3. **O YouTube áudio foge à porta do Scrap:** o `yt-dlp` faz os pedidos dele (página, player, stream em pedaços em
   `googlevideo.com`) fora de `scrap_http`. Quantos pedidos um áudio gasta: **NÃO SEI** (não medido).
4. **A prova-teto não vê corridas sociais.** `provas/prova_teto_dominio.py` lê `CORTESIA.PEDIDOS_POR_HOST` do livro
   de corridas do coletor web. O envelope e o RUN-MANIFEST de uma corrida do Scrap não registam pedidos por host
   (conferido num envelope real de 24/09). Para a onda social, a prova daria **NAO_SEI (código 2)**.

**O que falta, para o dono do Scrap:** (a) contar os pedidos por DOMÍNIO registável no mesmo livro da onda
(`SINTONIA_TETO_ONDA`) e recusar acima de 5; (b) escrever `PEDIDOS_POR_HOST` no recibo da corrida; (c) fazer o `yt-dlp`
passar pelo mesmo contador (ou medir e limitar os pedidos dele). **Sem (a)+(b), a onda social não corre**:
o lote pequeno limitaria os pedidos, mas ninguém o provaria depois.

## 4 · A onda, por noites (quando o §3 estiver fechado e a junção instalada)
**Cada noite, a mesma sequência:** portão de egresso de consenso (`superficie/rede.py --portao-de-egresso IT`) = PASS
→ **backup da Sala** (`pg_dump -Fc` da `SINTONIA_COLLECTION_DSN`, como na BC2) → **robô parado** (`PARAR.flag`; a corrida
escreve `data/samples/RUN-MANIFEST.json` e o LIVRO na árvore do robô: dois escritores não) → o lote → egresso de novo
→ **prova-teto** (com o §3 (b) feito) → relançar o robô → `regua_social --vivo` (robô parado) só para o canário.

| noite | lote (por slug / canal; o SID lê-se no livro vivo) | pedidos previstos por domínio |
|---|---|---|
| LI-1 | gruppocaviro · certisbelchim-italia | linkedin.com 2 · licdn.com ≤ 4 (teto 1: MP4 + legenda) |
| LI-2 | arpa-valle-d-aosta · cia-agricoltori-italiani | idem |
| LI-3 | consorzio-tutela-grana-padano · ispra_2 | idem |
| LI-4 | italmopa · macfrut-fiera | idem |
| LI-5 | dipartimento-di-scienze-agrarie-ambientali | linkedin.com 1 · licdn.com ≤ 2 |
| LI-6… | as outras 28 contas (ZERO/FALHA em 24/09), 2 por noite | idem |
| YT-1…YT-9 | 1 canal por noite (os 9 números novos) | youtube.com 1 (lista) + o áudio: **NÃO SEI** (yt-dlp, §3.3) |

O primeiro lote de cada plataforma é o **canário**: decide o READY pela régua. Os seguintes são a onda.
**Previsão (24/09, com os números de então):** LinkedIn ≈ 9 vídeos com teto 1 nas 9 contas boas, 7 com legenda,
2 na Sala. YouTube: 1 som + 1 transcrição por canal, e cerca de 4 em 11 na Sala.

## 5 · A junção da nuvem (item 1 da missão)
`origin/nuvem-social-integrado-v1` @ **290e7349** (medido): **ainda não tem** d7e31802, 8c4dfc1e nem df0865e6.
Aponta para a INTEGRA-ONDA2 (coorte da 2.ª onda congelada). **Nada a verificar ainda.** Quando tiver, a verificação é:
clone limpo → `git checkout -B nuvem-social-integrado-v1` → os 3 SHAs dentro → conflitos (só as geradas) →
bateria antes/depois pelo nome (a mesma de `curadoria/social-final/`) → `test_d37_campos_de_politica` +
`provas/_mutantes_d37.py` (8/8) → `test_d36_envelope_equivalente` + `provas/_mutantes_d36_equivalencia.py` (9/9) →
cadeia do mapa VALIDAR.

## 6 · D61 — a DATA e o LOCAL dos vídeos chegam ao item da Sala? (medido, 25/09)
Lido nos envelopes reais de 24/09 e **nas Salas descartáveis desses canários** (religadas sem rede, só leitura, e desligadas):

| campo na Sala | LinkedIn (2 itens na Sala) | YouTube áudio, código da produção (4 itens na Sala) |
|---|---|---|
| `published_at` (quando o vídeo foi publicado) | **CHEGA** (2026-09-19T09:38:04Z · 2026-09-10T14:10:28Z) | **NAO SEI** |
| `source_location` (onde está a organização) | **NAO SEI** | **NAO SEI** |
| canal / conta | pelo `source_id` (o número É a página); o CREATOR_URL fica no bruto | pelo `source_id` (o número É o canal); o CHANNEL_ID só com o bloco A do yt-metadados |
| quando colhemos | `observed_at` preenchido, `captured_at` NAO SEI | `captured_at` preenchido, `observed_at` NAO SEI |

**Onde se perde (ficheiro:linha):**
1. **Data do vídeo no YouTube** — `coleta/adaptador_youtube.py:635` (`youtube_audio_publico`, produção df0865e6) não
   emite `PUBLISHED_AT`. **Consertado no yt-metadados-v1** (`8c4dfc1e`, `coleta/adaptador_youtube.py:771`, `timestamp`/
   `upload_date` do yt-dlp). Daí em diante o caminho existe: `coleta/scrap_colheita.py:421` (sobe para o topo) →
   `coleta/ingresso.py:318` (`published_at`) → `admissao/admissao.py:1917` → coluna `published_at`.
   **Provado pelo código, NÃO medido numa Sala** (a prova do engenheiro teve SALA 0). Medir no 1.º lote YouTube.
2. **Local da organização, nas duas plataformas** — o coletor escreve «não sei»:
   `coleta/adaptador_linkedin.py:1786` (produção; `:1818` no social-onda2-v1) → `source_location=None`;
   e o `coleta/adaptador_youtube.py` do yt-metadados não tem o campo.
   **E não há quem o complete:** `coleta/scrap_colheita.py:512-514` lê do contrato só o DOCUMENT_ID
   (`cf.document_id_declarado`). `regras/contratos_de_fonte.py:183` (`lugar_declarado_pela_fonte`, que confere o lugar
   contra o gazetteer) existe, mas nenhum passo da coleta a chama (só um print e uma prova). Mesmo chamada, lê
   `regras/italy_contracts.mjs`, onde os contratos sociais do Curator **não estão** — o mesmo buraco do DOCUMENT_ID_RULE.
   **Conserto proposto (dono: engenheiro do Scrap + CUR-PRONTA):** (a) a unidade do Scrap pede ao contrato também
   `SOURCE_LOCATION` (a função existe, falta a chamada); (b) o contrato social declara `SOURCE_LOCATION_RULE`, e a
   ponte livro do Curator → tabela do coletor leva-o. **Não se preenche no coletor a partir do país do egresso nem
   do `COUNTRY_SCOPE`:** isso seria o lugar do nosso pedido, não o da organização (VPN_LOCATION != SOURCE_LOCATION).
3. **Duas colunas para «quando colhemos»** — `coleta/scrap_colheita.py:422` traduz `COLLECTED_AT` → `OBSERVED_AT`, e
   `coleta/ingresso.py` traduz `COLLECTED_AT` → `captured_at`. O LinkedIn cai numa, o áudio do YouTube na outra.
   Não se perde o valor; perde-se a comparação entre plataformas. Dono: o dono da fronteira (ingresso).

**Portanto: com a junção social + yt-metadados, a DATA de publicação chega nas duas plataformas (LinkedIn medido;
YouTube pelo código). O LOCAL da organização NÃO chega em nenhuma.** A onda social fica em espera (D61) até este
§6.2 estar consertado e medido numa Sala descartável.
