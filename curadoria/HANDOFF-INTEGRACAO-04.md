# HANDOFF DE INTEGRAÇÃO — SOURCE CURATOR MISSÃO 04

```
DE            SOURCE CURATOR · claude/bot-de-fontes-v2-plano
PARA          COORDINATOR   · claude/contract-provenance-cutover-v1
DATA          2026-09-20
BASE_HEAD     959ae46a   (esta branch nasceu daqui)
TRUNK         claude/it-trunk-v1 @ 606974c3
COORD_HEAD    4055e543 no início da missão (23 commits à frente)
```

---

## 1 · O QUE ESTA BRANCH ENTREGA

> ### ⚠️ CORRIGIDO PELO GATE 04A — LEIA ISTO PRIMEIRO
>
> A primeira versão deste handoff declarava **68 fontes READY**, das quais 50 do
> YouTube. **Está errado, e a correcção está aplicada abaixo.**
>
> As 50 do YouTube chegavam à rede por `youtube.com/feeds/videos.xml`, e essa
> rota está em `Disallow` no `robots.txt` — lido ao vivo, linha 12. Os canários
> passaram (50/50, XML real com videoId e data) porque a rota **responde**.
> Responder não é ser permitida.
>
> ```
> READY declarado na missão 04     68
> READY depois do gate de rota     18     ← todas HTML
> reclassificadas                  50     CONTRACT_READY_ROUTE_BLOCKED
> ```
>
> **Nada foi apagado.** SOURCE_ID, fichas do Atlas, caracterização, contratos e
> registos de canário continuam de pé. O que caiu foi só a afirmação «pronta
> para coleta» — a única que não estava provada.

**18 fontes italianas prontas para coleta**, cada uma com SOURCE_ID do Atlas,
contrato executável, canário corrido contra a rede real **e rota conferida
contra o `robots.txt` vivo**.

```
READY_FOR_COLLECTION        18     ← todas LOTE-HTML-ARTIGO
CONTRACT_READY_ROUTE_BLOCKED 50     ← YouTube · ROBOTS_DISALLOWED_ROUTE
CONTRACTED_CANARY_FAILED      9     ← EMPTY_LIST honesto, voltam à amostragem
CONTRACTS_CREATED            77     CONTRACTS_VALID 77 · INVALID 0
CANARY_ATTEMPTED             77     PASS 68 · FAIL 9
ROBOTS_GATE_EXECUTED         77     ALLOWED 27 · DISALLOWED 50 · UNKNOWN 0
SOURCES_CREATED (Atlas)      84     fichas novas
ENDPOINTS_ADDED               0
```

---

## 1A · O ERRO DE ROTA, POR EXTENSO

**O repositório já tinha dito isto, e eu não li.**

```
coleta/scrap_http.py:31
  «E o portao ja REPROVOU rota que funcionava: o feeds/videos.xml do YouTube
   devolveu 15 videos italianos com descricao inteira nesta maquina, e esta
   em Disallow. Ele nao entrou. E para isso que o portao serve — se ele so
   aprovasse, nao seria portao.»

coleta/adaptador_youtube.py:756
  nota='playlistItems.list; o feeds/videos.xml foi reprovado pelo portao'
```

Os meus 50 contratos citavam `youtube.channel.discovery` como capacidade
reutilizada. Essa capacidade usa `playlistItems.list` — a **API oficial com
chave**. Nunca usa o feed. Escrevi o nome certo por cima da rota errada.

> **Citar uma capacidade não é usá-la.** O contrato dizia
> `youtube.channel.discovery` e o código fazia `urlopen()` directo no caminho
> proibido, **sem passar pelo portão `permitido()`**.

### Sobre a rota alternativa sugerida na missão

A missão 04A supunha que `/channel/<id>/videos` + `LOCAL_YTDLP` fosse a rota
provada. **Medido: não é.**

```
/channel/<id>/videos       não aparece em nenhum ficheiro do repo
LOCAL_YTDLP                existe, mas é de Instagram Reels
                           (77 menções a instagram, 1 a youtube)
yt-dlp no YouTube          passa por /youtubei/ e /get_video — ambos Disallow
                           e BLOCKED de facto ("Sign in to confirm…")
```

A rota permitida e documentada é **`playlistItems.list`** (1 unidade de quota),
hoje em `CREDENTIAL_MISSING`. `docs/operacao/PROXIMA-MISSAO-YOUTUBE.md` diz-o
com todas as letras: *«A vigilância barata permitida é `playlistItems.list`
sobre a playlist de uploads — 1 unidade por chamada, não zero.»*

**Não contornei nada:** sem cookie, sem login, sem API key, sem excepção por
SOURCE_ID. As 50 ficam bloqueadas até haver credencial ou decisão de política.

---

## 2 · FICHEIROS ALTERADOS

### Tocado (1 ficheiro partilhado)

```
docs/fontes/ATLAS-DE-FONTES-EAME.md     +2956 linhas, 84 fichas novas
```

**Só acrescenta.** Nenhuma linha existente foi alterada ou removida — as fichas
entram num bloco novo no fim (`## ONDA SOURCE CURATOR — 2026-09-20`).

> **CONFLICT_RISK_WITH_COORDINATOR = BAIXO.** Medido: o COORDINATOR não tocou
> neste ficheiro em nenhum dos 23 commits. Se tiver tocado entretanto, o
> conflito é de fim-de-ficheiro e resolve-se mantendo ambos os blocos.

### Novo (área própria da curadoria, zero risco)

```
curadoria/italy_contracts_curator.json    77 contratos executáveis
curadoria/READY-FOR-COLLECTION-V1.json    o veredito, fonte a fonte
curadoria/SOURCE-ID-ALLOCATION-V1.json    que número foi dado a quem, e porquê
curadoria/CANDIDATE-TO-SOURCE-MATCH-V1.json
curadoria/CONTRACT-VALIDATION-V1.json
curadoria/CANARY-LOTE-YOUTUBE-FEED.json   50/50
curadoria/CANARY-LOTE-HTML-ARTIGO.json    18/27
curadoria/{emparelhar_com_atlas,atribuir_source_id,escrever_contratos,
           validar_contratos,canario,escrever_no_atlas,veredito_ready}.py
```

### NÃO tocado (proibido, e verificado)

```
regras/italy_contracts.mjs              regras/italy_contracts_onboarded.json
regras/italy_pilot_collect.mjs          regras/motor_de_rota.mjs
coleta/*                                 candidatas/FONTES-CANDIDATAS.json
system-map/data/*.generated.json         Admission · Sala · Intelligence
```

**COLISÃO MEDIDA COM OS 78 FICHEIROS DO COORDINATOR: NENHUMA.**

---

## 3 · COMO SE IMPORTA

`italy_contracts_curator.json` tem a **mesma forma** de
`italy_contracts_onboarded.json`. Do lado do dono, uma linha:

```js
const TABELA_CURATOR = JSON.parse(
  readFileSync(new URL("../curadoria/italy_contracts_curator.json", import.meta.url), "utf8"));
```

O dono do contrato continua a ser `regras/italy_contracts.mjs`. Esta tabela é
**configuração, não uma segunda autoridade**.

### Duas famílias, dois moldes já existentes

```
LOTE-YOUTUBE-FEED   50   molde de IT-T8-001 · APPLICATION_ROUTE
                         sobre youtube.channel.discovery / video.metadata
LOTE-HTML-ARTIGO    27   molde de contratoGenerico() · HTML_LINK_DISCOVERY
```

> **Porque não se estendeu `contratoGenerico()` para XML.** Medido:
> `ASSINATURA_POR_TIPO = { PDF, HTML }` — XML rebenta. Acrescentar `XML:"<?xml"`
> teria dois problemas: o ficheiro é seu e está em movimento; e um feed de
> YouTube **não é um documento que se baixa, é uma listagem** — tratá-lo como
> documento poria o índice no RAW em vez do vídeo.

---

## 4 · A IDENTIDADE, QUE É O QUE MAIS IMPORTA

`SOURCE_ID` veio do Atlas, nunca da URL. A sequência continua do maior número
existente **em cada território**, contando o Atlas **e** o seu
`onboarded.json` — nunca recicla.

```
T5  SCIENCE            18        T12 POLICY/ENV        11
T7  TECHNICAL NETWORK  29        T10 MARKET             6
T9  COMPETITORS         7        T2  CLIMATE            6
T8  FARMERS/MEDIA       5        T11 EVENTS             2
```

**Zero colisão** com os 105 SOURCE_IDs do seu `onboarded.json` e com as 185
fichas do seu Atlas.

### O emparelhamento que quase correu mal

O primeiro emparelhador comparava URLs literalmente e devolveu
**«0 de 98 já existem»** — um zero limpo, redondo e falso. O controlo positivo
apanhou-o:

```
Atlas   IT-T8-001   youtube.com/@agronotizietv
fila    CAND-0187   youtube.com/@AgroNotizie      ← A MESMA FONTE
```

Sem esse controlo, teria criado 98 identidades novas, uma delas duplicando
`IT-T8-001`. **CAND-0187 não recebeu número novo**: reconhece-se como
`IT-T8-001`.

> **Um zero suspeito merece um controlo positivo antes de virar número.**

### Canal e site são duas fontes

15 organizações aparecem duas vezes (canal + site). A primeira leitura foi
«tenho 30 números para 15 fontes». **Não é** — `COL-LAW-034` diz o contrário,
com o seu próprio caso: `IT-T8-001` é o canal AgroNotizie, `IT-T1-021` é o site,
«continua a ser outra fonte». O campo `MESMA_ORGANIZACAO` guarda o parentesco
sem fundir as identidades.

---

## 5 · O QUE FICOU DE FORA, E DE QUEM É

```
50  ROBOTS_DISALLOWED_ROUTE    rota do feed barrada (SCRAP ENGINEER / política)
 9  CONTRACTED_CANARY_FAILED   EMPTY_LIST — voltam à amostragem (Curator)
 7  ramo de índice             pequena adaptação de rota (Curator)
13  sem território             evidência não decidiu T1–T12 (Curator)
14  Facebook                   CAPABILITY_BLOCK (SCRAP ENGINEER)
 1  Valagro/Syngenta           SEMANTIC_REVIEW_REQUIRED (humano)
11  NEEDS_MORE_SAMPLING        (Curator)
69  LinkedIn 44 + Instagram 25 POLICY — zero pedidos de rede
```

Nenhum destes é uma recusa. **Nenhuma fonte foi rejeitada nesta missão.**

---

## 6 · SYSTEM MAP

`system-map/data/sources.generated.json` **não foi commitado** — foi corrido
uma vez para provar que o scanner canónico lê as fichas novas:

```
213 → 297 fontes    IT 244 · ES 34 · EU 13 · FR 6
GREEN 175 · YELLOW 85 · PARCIAL 27 · NÃO SEI 10
IT-T7-015, IT-T5-037, IT-T12-007, IT-T8-008 → todos PRESENTES com campos lidos
```

> **REGENERAÇÃO NECESSÁRIA DO SEU LADO**, depois de integrar o Atlas. Não a
> commitei para não colidir com os derivados que está a gerar.

---

## 7 · O QUE ISTO NÃO É

```
FONTE PRONTA != FONTE COLETADA
```

Nenhuma destas 68 foi coletada. Não corri Big Collection, não criei RUN, não
escrevi RAW, não toquei em Admission nem na Sala. A próxima coleta é sua.

---

## 8 · TESTES

```
test_capturador       22      test_correr_lote        6
test_caracterizador   29      validar_contratos        8
──────────────────────────────────────────────────────────
TOTAL                 65      NEW_FAILURES = 0
RED TEAM missão 04    21 PASS · 0 FAIL
RED TEAM gate 04A     17 PASS · 0 FAIL  (inclui controlo independente:
                      feeds/videos.xml barrado · /channel/<id>/videos não)
```
