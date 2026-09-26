# VIDEO-SEGUNDA-LISTA — 10 vídeos ≤ 900 s com pessoa identificada, no formato do maestro

Ramo `primeira-volta-video-v1` (continua a PRIMEIRA-VOLTA-VIDEO). Fonte da lista: `VOZES-AGRONOMOS`
(`origin/vozes-agronomos-v1` @ e9a6990a: 22 pessoas com nome + 8 séries), cruzada com as 612 páginas
`/watch` guardadas (`VIDEOS-GUARDADOS.json`). **Sem rede. SEM MAPA.**

## Em palavras simples

- Pedido: 10 vídeos de até 900 s, cada um com **agrónomo/técnico identificado + cultura + problema**.
- **No que está guardado, só 4 vídeos cumprem as três coisas** (pessoa com papel técnico, cultura e
  problema escritos no próprio título/descrição), e **3 deles já estão na 1.ª lista** (ASSAM, CONAF,
  Brunello). **Só 1 é novo:** Luca Fagioli, técnico do Consorzio Agrario di Ravenna, sobre a cimice
  asiatica nos pereti (Conserve Italia, 216 s).
- Por isso a 2.ª lista tem **10 vídeos em três níveis**, e cada linha diz o que lhe falta:
  - **A (1):** as três coisas provadas pelo texto do vídeo;
  - **B (7):** pessoa com nome + cultura; o problema falta ou é só do evento;
  - **C (2):** pessoa com nome e papel técnico/académico; cultura e problema NÃO SEI.
- ⚠️ **Corrijo a 1.ª lista.** Eu disse «L'Informatore Agrario: 6 de 15 vídeos úteis». Não é verdade:
  - as 5 entrevistas «Vite in Campo» **partilham a mesma descrição** do evento, que diz «falou-se
    **também** da peronospora» — o tema delas é a **poda**;
  - no vídeo n.º 1 da 1.ª lista (Pachioli) não há descrição; o «problema» veio da palavra
    «Fitopatologo», que é o **papel** da pessoa, não o assunto;
  - e a lista de palavras tinha falsos positivos («pero» casava «peronospora», «riso» casava
    «risorse»).
  Corrigido e testado: agora **nenhum canal passa de 2 vídeos úteis**, e o L'Informatore Agrario tem
  **0**. A escolha dos 10 da 1.ª volta não muda (continua a melhor que há), mas **o «1 forte» já não é
  forte**: é um agrónomo fitopatólogo a falar de oliveto, com o problema por provar na transcrição.
- A VOZES-AGRONOMOS diz «separar o áudio é proibido (III.I.7)». A D17.4 do dono autoriza a rota
  `audio-youtube` (OWNER_AUTHORIZED=SIM, a política da plataforma fica escrita), e a 1.ª volta foi
  aceite assim: segui o mesmo caminho. Fica dito para o dono ver as duas leituras lado a lado.

## A lista (`VOLTA-2.tsv`)

| Volta | Nível | Fonte | Vídeo | s | Pessoa · papel | Cultura · problema |
|---|---|---|---|---|---|---|
| 2A | **A** | IT-T9-014 Conserve Italia | `pCtl0kpM1xM` Difesa contro la cimice asiatica: consigli utili | 216 | Luca Fagioli · tecnico Consorzio Agrario di Ravenna | pero (pereti) · cimice asiatica |
| 2A | B | IT-T8-006 L'Informatore Agrario | `CjtZ_U1KOMs` Vite in Campo — Valerio Nadal (Condifesa) | 104 | Valerio Nadal · Condifesa | vite · só do evento (peronospora) |
| 2A | C | IT-T8-004 Terra e Vita | `HfTvWjFwsvQ` AGRILAB 2026, intervista a Bruno Basso | 136 | Bruno Basso · prof., Michigan State Univ. | NÃO SEI · NÃO SEI |
| 2A | C | IT-T9-016 Consorzi Agrari d'Italia | `QmeVN7SNnMU` Matteo Gnocato — Rete tecnica CAI | 62 | Matteo Gnocato · rede técnica CAI | NÃO SEI · NÃO SEI |
| 2B | B | IT-T8-006 | `Pw-dHhFWFeY` Vite in Campo — Silvia Toffolati (Università di Milano) | 78 | Silvia Toffolati · Univ. Milano | vite · só do evento |
| 2B | B | IT-T9-014 | `AQ5u5u-_Jjg` Campagna drupacee 2026: il punto di Pietro Baroncini | 160 | Pietro Baroncini · técnico (descrição) | drupacee · nenhum (balanço da campanha) |
| 2C | B | IT-T8-006 | `pgQCP00r8eg` Oliveto Smart — Giulia Zuecco (Docente Univ. Padova) | 216 | Giulia Zuecco · docente UniPD | olivo · NÃO SEI |
| 2D | B | IT-T8-006 | `oSg9I8_tkvI` Vite in Campo — Riccardo Castaldi (Terremerse) | 115 | Riccardo Castaldi · papel NÃO SEI | vite · só do evento |
| 2E | B | IT-T8-006 | `IXF-wG0-iQ4` Vite in Campo — Gabriele Posenato (Cadis 1898) | 72 | Gabriele Posenato · papel NÃO SEI | vite · só do evento |
| 2F | B | IT-T8-006 | `OUOpZ0mSfR8` Oliveto Smart — Enzo Gambin, direttore Aipo | 123 | Enzo Gambin · dirigente (não técnico) | olivo · NÃO SEI |

Todos ≤ 900 s (o maior tem 216 s: nenhum precisa de mexer no limite de 540 s), todos com legenda
italiana na página guardada, **1 282 s ≈ 21 min** de áudio.

**Porque há 6 voltas e não 1:** o maestro aceita **um vídeo por fonte** em cada corrida
(`--videos` é um dicionário por SOURCE_ID) e 6 dos 10 vídeos são do mesmo canal (IT-T8-006). Cada
volta tem cada fonte uma só vez.

**Ficaram de fora (≤ 900 s não há):** as séries técnicas CRPV (3 347 s), Georgofili (2 598 s), Rete
Rurale (5 175 s), ANBI (7 580 s); CNR-ISAFOM (Angelo Basile: CNR fechado pela coordenação; vídeo de
2015); Simon Pierce (sem vídeo guardado); Koppert (cultura + problema, mas ninguém com nome);
os outros técnicos da CAI (nome e cargo, mas nem cultura nem problema no texto).

## Os comandos (depois do lote 3 e da 1.ª volta; uma volta de cada vez, pasta nova para cada)

```bash
py superficie/rede.py --portao-de-egresso IT
SINTONIA_ASR_DEVICE=GPU py ferramentas/maestro_social/maestro_social.py --correr --autorizado-pelo-dono --canario --saida=<pasta 2A> \
   --fontes=IT-T9-014,IT-T8-006,IT-T8-004,IT-T9-016 \
   --videos=IT-T9-014:pCtl0kpM1xM,IT-T8-006:CjtZ_U1KOMs,IT-T8-004:HfTvWjFwsvQ,IT-T9-016:QmeVN7SNnMU
# 2B
   --fontes=IT-T8-006,IT-T9-014 --videos=IT-T8-006:Pw-dHhFWFeY,IT-T9-014:AQ5u5u-_Jjg
# 2C · 2D · 2E · 2F (uma fonte cada)
   --fontes=IT-T8-006 --videos=IT-T8-006:pgQCP00r8eg
   --fontes=IT-T8-006 --videos=IT-T8-006:oSg9I8_tkvI
   --fontes=IT-T8-006 --videos=IT-T8-006:IXF-wG0-iQ4
   --fontes=IT-T8-006 --videos=IT-T8-006:OUOpZ0mSfR8
```

**Plano a seco da 2A** (`MAESTRO-SOCIAL-PLANO-VOLTA-2A.json`, cópia deste ramo com os livros do vivo):
4 ondas, `{"youtube.com": 4}` cada, `TODAS_CABEM: true`. As outras voltas são uma ou duas destas ondas.
Pedidos na 2.ª lista inteira: **40** ao balde do YouTube (30 `youtube.com` + 10 `googlevideo.com`), **0**
à API. D20 não se aplica (rota de áudio, não da API).

Sugestão de ordem, se o dono quiser menos voltas: correr só **2A + 2B** (6 vídeos: o A, dois B com
papel técnico/académico, os dois C) e deixar as 4 voltas de um vídeo só para depois de ver o que a
transcrição das primeiras dá.

## O que isto não prova

- Que as pessoas dizem cultura + problema: o nível B e C é exactamente o que só a transcrição diz.
- O papel de quase todos: só o título/descrição o diz (a VOZES-AGRONOMOS tem o plano de 19 pedidos
  para o provar nas páginas das instituições).
