# YOUTUBE — A FALA ENTRA POR ONDE?

**Missão:** descobrir e provar a melhor rota **autorizada** para o conteúdo falado
dos vídeos estratégicos entrar na Collection.
**Medido em:** 2026-09-14. **Custo:** US$ 0,00. **Execuções pagas:** 0.

Esta missão **termina na aquisição**. Não cria RUN, não cria RAW, não cria sala,
não toca na Collection e não começa Inteligência.

---

## A frase que esta missão veio refutar

> «A API do YouTube não baixa vídeo, logo o conteúdo é impossível.»

É falsa, e a razão é simples: **o ativo procurado é a fala, não os bytes servidos
por youtube.com**. Quem publica um vídeo técnico quase nunca publica só o vídeo.
Publica o artigo, o boletim, os atti do convegno, o PDF do webinar. Esse material
é do próprio publicador, mora no domínio dele, e a rota até ele é a rota normal da
web — a mesma que o SINTONIA já usa para rótulo e bollettino.

**Dos 14 vídeos estratégicos medidos, 6 já têm essa outra porta aberta hoje.**

---

## A · GIT

| | |
|---|---|
| REPO | `lucianodalondon-sys/eame-sintonia` |
| REMOTE | `https://github.com/lucianodalondon-sys/eame-sintonia.git` |
| BRANCH | `claude/youtube-acquisition-authorized-7e2e67` |
| HEAD | `f437ff1140fa97484ca9695b341fbe9ca0a9f050` |
| WORKTREE | `C:\eame-sintonia\.claude\worktrees\youtube-acquisition-authorized-7e2e67` |
| ÁRVORE | limpa no início (o `git status` do arranque era um retrato velho) |
| `git fetch --all --prune` | correu, sem alteração |

**Branches YouTube no remoto (5):** `sintonia-scrap-youtube-official-c2` ·
`sintonia-scrap-youtube-cutover-c3` · `sintonia-scrap-youtube-transcript-c5` ·
`whisper-youtube-integration-tkulwy` · `retomada-coleta-video-convegni-vz50er`.

**Branches Collection concorrentes (26 no remoto).** Nenhuma foi tocada. A que está
a construir o executor de mídia — `claude/collection-preserve-facts-2139eb` — tem
worktree próprio e ficou intacta.

### ⚠️ Esta branch está 485 commits atrás da branch YouTube irmã

`claude/youtube-italia-caption-audio-8b460b` (worktree vizinho, local, não empurrada)
está **9 atrás / 485 à frente** desta. São 743 ficheiros de diferença. Ela carrega a
entrega anterior sobre legenda e áudio (`docs/sintonia-scrap/C4G-…`,
`provas/a_legenda_e_o_audio_do_youtube.py`, `tests/test_youtube_oficial.py`), que
**não existem aqui**. Por isso esta missão releu a política ao vivo em vez de a
herdar: o documento não estava nesta prateleira.

---

## B · O UNIVERSO MEDIDO

O acervo já tem o material. Ele veio do piloto de sensores, em
`data/samples/SENSOR-PILOT/MEDICAO.json` (SOURCE_ID `SENSOR-PILOT/MEDICAO`):

```
1.071   vídeos colhidos
  567   NOISE
  356   NOT_ENOUGH_TEXT
   65   EVENT_PROMOTION
   47   MARKETING
   23   TECHNICAL_INTERPRETATION   ┐
   11   RESEARCH_COMMUNICATION     ├─ 36 itens: o material tecnicamente relevante
    2   FIELD_OBSERVATION          ┘
   28   com transcrição já guardada (444.810 caracteres)
```

**Destes 36, escolheram-se 14** — os de maior valor e os que cobrem os recortes
italianos vivos (`IT-VINE-FLAVESCENCE`, `IT-APPLE-DISEASE`, `IT-RICE-WEED`,
`IT-OLIVE-BACTROCERA`, `IT-MAIZE-WEED`, `IT-SOYBEAN`).

O censo completo, com todos os campos pedidos, está em
[`data/samples/YOUTUBE-ACQUISITION/CENSO-AQUISICAO-YOUTUBE-V1.json`](../../data/samples/YOUTUBE-ACQUISITION/CENSO-AQUISICAO-YOUTUBE-V1.json).

**Nenhum `SOURCE_ID` foi fabricado.** O censo é derivado e não reivindica id próprio:
o dono do id do material continua a ser `SENSOR-PILOT/MEDICAO`.

---

## C · A ROTA OFICIAL DO YOUTUBE — lida ao vivo, não lembrada

Fonte: `developers.google.com/youtube/terms/developer-policies`,
**Last Updated 2026-09-14 UTC** (o mesmo dia da leitura).

```
III.E.1.a   «download, import, backup, cache, or store copies of YouTube
             audiovisual content without YouTube's prior written approval»
III.I.7     «separate, isolate, or modify the audio or video components of
             any YouTube audiovisual content»
III.I.8     «promote separately the audio or video components ...»
III.I.14    «use any technology other than YouTube API Services to access or
             retrieve API Data, including to access any portion of any
             YouTube audiovisual content»
```

A política **não mudou**. Bate palavra por palavra com o que já estava medido.

### A legenda: o bloqueio é de permissão, não de preço

`captions.download`, doc lida hoje:

| | |
|---|---|
| scopes | `youtube.force-ssl` · `youtubepartner` |
| exigência | *«This method is requires the user to have permission to edit the video»* |
| leitura | a chave da porta é do **dono do vídeo** |

Para canal de terceiro **não existe rota oficial de legenda**. Comprar uma chave de
API mais cara não abre esta porta — ela abre com um «sim» de quem publicou.

### O `robots.txt`, lido hoje

HTTP 200, 792 bytes. Proíbe `/api/` (que cobre o `/api/timedtext`, a baseUrl real da
legenda), `/youtubei/`, `/get_video`, `/get_video_info`, `/timedtext_video`.
**Não** proíbe `/watch` nem as páginas de canal — por isso a janela pública de
metadata continua válida.

### Três bloqueios distintos, e levantar um não abre a estrada

```
POLÍTICA     as cláusulas acima            -> conserta-se com AUTORIZAÇÃO
CREDENCIAL   YOUTUBE_DATA_API_KEY          -> JÁ RESOLVIDO (ver abaixo)
IDENTIDADE   canal sem identidade provada  -> missão de fonte, decisão de gente
```

### ✅ A chave existe — e a minha primeira leitura estava errada

No meio desta missão escrevi que a credencial estava ausente. **Estava a olhar só
para esta máquina.** `gh secret list` mostra:

```
YOUTUBE_DATA_API_KEY    2026-09-08T14:18:34Z
```

A chave é **secret do repositório** desde 8 de setembro, e quem a usa é a fase
`youtube` do `.github/workflows/scrap-social.yml`. Não está no ambiente local **de
propósito**: essa fase corre no runner hospedado, porque este IP de datacenter já
foi medido como barrado pelo player do YouTube.

Isto não muda o veredicto sobre a fala — a chave abre busca, metadata e comentários,
**nunca** legenda de canal de terceiro. Mas muda quem tem de fazer o quê: ninguém
precisa de comprar chave nenhuma.

`search`, `videos`, `channels` e `commentThreads` **não foram testados nesta
missão**, por escolha de não gastar quota alheia. Ausência de teste não é prova de
bloqueio — é NÃO SEI, e fica escrito como NÃO SEI.

### O que já estava medido noutra branch, e que esta missão não repete

`origin/claude/sintonia-scrap-youtube-official-c2` (e c3, c5) carrega
`docs/operacao/PROXIMA-MISSAO-YOUTUBE.md` com a matriz de **seis capacidades contra
cinco rotas** e o custo em unidades de quota. Dois números de lá:

- **96% do gasto Apify histórico foi YouTube** — US$ 12,33 de US$ 12,81;
- desses, **US$ 12,20 têm rota oficial permitida** (busca, metadata, comentários) e
  **US$ 0,13 — a legenda — não têm**.

E a frase que abre exactamente o buraco por onde esta missão entrou:

> «Ou se obtém permissão escrita, ou a transcrição de terceiro continua sendo a
> única célula onde a Apify tem argumento.»

**Há uma terceira saída, e é a deste relatório:** o texto no site de quem publicou.

---

## D · AS ROTAS ALTERNATIVAS, POR PUBLICADOR

### 🟢 Abertas hoje, sem pedir nada a ninguém (6)

| vídeo | publicador | a outra porta | prova |
|---|---|---|---|
| `zaEk8LE6SOQ` | AgroNotizie | [artigo completo sobre flavescenza](https://agronotizie.imagelinenetwork.com/difesa-e-diserbo/2024/05/28/flavescenza-dorata-il-vero-nemico-e-la-cicalina-della-vite/84010) | 200 · 3.464 palavras · **nomeia os mesmos dois interlocutores do vídeo** (Beccari ×6, Balestrazzi ×1) |
| `uIegdnccN9g` | AgroNotizie | [artigo Epiresistenze](https://agronotizie.imagelinenetwork.com/difesa-e-diserbo/2023/03/31/resistenze-agli-erbicidi-nei-giavoni-di-risaia-gli-innovativi-risultati-del-progetto-epiresistenze/78751) | 200 · 200.381 b |
| `3mB_D1Nlvbk` | AgroNotizie | [artigo Beloukha/soja](https://agronotizie.imagelinenetwork.com/difesa-e-diserbo/2022/09/12/disseccamento-della-soia-tutti-i-vantaggi-di-beloukhasupregsup/71819) | 200 · 184.724 b |
| `hoppQZ7f_ok` | Bayer IT | [Prova in campo con Adengo Xtra](https://www.cropscience.bayer.it/magazine/articoli/campi-prova/podere-pignatelli) | traz **mais** que o vídeo: desenho do ensaio, 7 teses com substâncias activas, dose (0,44 L/ha), datas, citação do técnico palavra por palavra |
| `w_D7NYYI3b0` | Accademia dei Georgofili | [resenha assinada por Bruno Bagnoli](https://www.georgofili.info/contenuti/difesa-fitosanitaria-in-olivicoltura-richiede-approfondimenti-di-conoscenze-o-pi-trasferimenti-di-qu/28558) + página do evento + arquivo de *Atti* | 200 · 2.012 palavras · assinada e datada |
| `rdDR4xgpQ4k` | Chambre d'Agriculture de la Gironde (consórcio PARSADA) | [Bilan de campagne 2025](https://www.vinopole.com/wp-content/uploads/2025/12/Bilan-de-campagne-2025-VF.pdf) + [fiche Plan Mildiou](https://www.vinopole.com/wp-content/uploads/2025/03/fiche-technique-n7-Plan-Mildiou.pdf) | 200 · 10,3 MB e 747 KB · **`%PDF-` verificado byte a byte**, não pela extensão |

**Quatro destas seis portas estão escritas pelo próprio publicador na descrição do
vídeo** («Leggi l'articolo completo», «Scopri di più su»). Ninguém contornou nada:
seguiu-se o link que o autor pôs lá.

### 🟡 Existe o texto, e existe a quem pedir (5)

| vídeo | publicador | onde está a fala escrita | a chave |
|---|---|---|---|
| `RisRARQSFAg` | AIPO Verona | «PERIODICO OLIVO 2026», na Área Reservada | quota de sócio / pedido institucional |
| `ZmmFiPHNl2U` | Primoweb / AIPO / Televeneto | o mesmo boletim da AIPO | **três donos possíveis** na cadeia |
| `QGE7h4gztQ8` | L'Informatore Agrario | candidato: artigo n.41/2022, pp.59-63 | assinatura ou compra avulsa |
| `yEQezPE7Wfw` | L'Informatore Agrario | não localizado | assinatura ou compra avulsa |
| `yCR90mte0CM` | Riccardo Castaldi | não há site próprio | **um «sim» dele abriria a rota OFICIAL** — é o dono do vídeo |

**Nenhum pedido foi enviado.** A missão identificou a quem se pediria; pedir é
decisão de gente.

O caso da AIPO merece registo: **ela publica o boletim de graça em vídeo no YouTube
e fecha o PDF aos sócios.** É por isso que o vídeo tem valor — ele é a versão
pública de um documento reservado.

### ⚪ NÃO SEI (3)

| vídeo | o que aconteceu |
|---|---|
| `EAkcA_2FDN8` (Coldiretti ER) | `coldiretti.it` cai (000) no `curl` **e** no navegador; `emiliaromagna.coldiretti.it` nem resolve em DNS. Pista, não prova: o [portal fitossanitário da Região Emilia-Romagna](https://agricoltura.regione.emilia-romagna.it/fitosanitario) abre (200, 946 KB) e é o dono do plano trienal que o convegno discute |
| `Svsznb_EB50` (UPL) | o site corporativo abre; o caminho do catálogo foi adivinhado e deu 404 |
| `gU5NdowIkO8` (FOGLIE.TV) | arquivo aberto e pesquisável, mas o item de 2014 não apareceu |

---

## E · CANÁRIOS

Coisas que, se mudarem, invalidam este relatório:

1. **`provas/rotas_de_fala_do_youtube.py`** — reabre as 14 rotas e regrava a medição.
   Falha no dia em que uma porta hoje aberta fechar, e vice-versa.
2. **`Last Updated` das Developer Policies** — hoje `2026-09-14`. Se mudar, reler.
3. **Frase `permission to edit the video`** em `captions.download` — se sair da doc,
   a rota oficial de legenda mudou.
4. **`Disallow: /api/` no `robots.txt`** — se sair, o `/api/timedtext` deixou de estar
   coberto e a leitura muda.

---

## F · BLOQUEIOS REAIS

### O que é bloqueio de política (não se conserta com dinheiro nem com código)

| o que foi testado | regra que bloqueia | rota alternativa que resta |
|---|---|---|
| baixar os bytes do vídeo | III.E.1.a | mídia no site do publicador, ou autorização escrita |
| tirar só o áudio para transcrever | **III.I.7** — a cláusula nomeia o áudio | a mesma |
| raspar o `/api/timedtext` | III.I.14 + `Disallow: /api/` | nenhuma automática; pedir ao dono |
| `captions.download` em canal de terceiro | «permission to edit the video» | pedir ao dono do canal |

> **«audio-only» não é uma versão mais leve do pedido. É o caso que a III.I.7 descreve.**
> A intuição «preciso de menos, logo posso mais» reaparece em toda missão de fala, e
> está errada todas as vezes.

### O que NÃO é bloqueio, e parece

Esta máquina saiu por **IP de datacenter em Palermo/IT** (`149.22.91.179`,
AS212238 Datacamp) — a VPN italiana está ligada, mas por gama de datacenter.

```
urllib / curl                    navegador gráfico, MESMO IP, MESMO dia
─────────────────────────        ─────────────────────────────────────
informatoreagrario.it  403       abriu, título «Homepage - L'Informatore Agrario»
cropscience.bayer.it   403       abriu, artigo inteiro do ensaio de campo
primoweb.it            403       abriu, artigo lido
```

**403 de um cliente ≠ página fechada para todos.** É a mesma lição que o
`youtube_janela.py` já tinha registado com o HTTP 429. Quem tomar estes 403 por
«fonte morta» apaga três rotas boas do mapa.

O caso da Coldiretti é diferente e **por isso fica em NÃO SEI**: fecha nos dois.

---

## G · AS AUTORIZAÇÕES QUE SERIAM NECESSÁRIAS

Nenhuma foi pedida. Por ordem de retorno:

1. **AIPO Verona** — inscrição/quota associativa. Abre o `Periodico Olivo` semanal
   inteiro, que é fonte **recorrente** e não um item só. Resolve 2 dos 14.
2. **Riccardo Castaldi** — autorização escrita do autor. É o único caso do censo em
   que a rota **oficial** do YouTube se abriria: sendo dono, ele pode dar a permissão
   que o `captions.download` exige.
3. **L'Informatore Agrario** — assinatura ou compra de artigo avulso. Resolve 2.
4. **Accademia dei Georgofili** — só para os *Atti* impressos; a resenha já é aberta.

---

## H · O QUE PODE ENTRAR AGORA NA COLLECTION

**Seis documentos, todos por HTTP normal, custo zero, sem pedir nada:**

```
3 artigos AgroNotizie       (flavescenza · epiresistenze · Beloukha)
1 artigo Bayer IT           (ensaio de campo Adengo Xtra)
1 resenha Georgofili        (giornata di studio em olivicoltura)
2 PDFs Vinopôle/PARSADA     (mildiou e black-rot)
```

O handoff é o canónico, e o YouTube **não** cria caminho paralelo:

```
SOURCE → ORCHESTRATOR → COLLECTION → RAW → executor de mídia → ...
```

### ⚠️ A etiqueta importa, e é aqui que se erra

Estes seis são **ARTIGO / BOLETIM / SÍNTESE TÉCNICA**. Não são transcrição.

```
TEXT_KIND     = ARTICLE  (ou BULLETIN / TECHNICAL_SYNTHESIS)
TEXT_RELATION = ORIGINAL          ← original DELE, não do vídeo
```

Carregam o mesmo assunto; **não carregam as mesmas palavras ditas**. Chamar artigo
de transcrição seria inventar uma equivalência que ninguém mediu. Por isso
`N_TRANSCRIPT_FOUND = 0`, e é para ficar zero.

E há um par que precisa de ressalva explícita: o PDF do Vinopôle é o balanço da
**campanha 2025**; o vídeo é o webinar de **abril de 2026**. Mesmo projeto, mesmo
assunto, **objeto diferente**.

---

## I · O QUE CONTINUA SEM ROTA

- **8 dos 14** não têm, hoje, documento aberto que entre sozinho: 5 dependem de
  autorização, 3 estão em NÃO SEI.
- **Os 22 vídeos técnicos restantes** dos 36 não foram tocados.
- **Os 1.035 vídeos não técnicos** do piloto continuam fora desta pergunta.
- **A conta YouTube da Syngenta Italia** (`Syngentaitaly`), do lote congelado
  `PUBLIC-COMM-FIRST-BATCH-EAME`, não foi medida.
- **A Data API**, por ausência de chave.

---

## J · RISCO

### 🔴 O risco que esta missão descobriu e não veio procurar

**As 28 transcrições que já estão no acervo — 444.810 caracteres — vieram todas do
ator `streamers~youtube-scraper` da Apify.**

```python
Counter({'streamers~youtube-scraper': 28})
```

São dois problemas diferentes, e não se substituem:

1. **Rota.** Um raspador de terceiro é, textualmente, *«technology other than
   YouTube API Services»* — a III.I.14. O material está no acervo; a rota por que
   entrou é a que a política nomeia.
2. **Espécie.** O que esse ator devolve é **legenda automática**, não transcrição
   oficial. Se alguma dessas 28 estiver gravada como `TEXT_KIND = TRANSCRIPT` e
   `TEXT_RELATION = ORIGINAL`, o acervo está a afirmar uma coisa que não mediu.

Entre as 28 está a do convegno da Coldiretti (97.710 caracteres) e a do webinar da
Gironde (85.931) — dois dos itens mais valiosos deste censo. **Estar no acervo não é
o mesmo que ter entrado por rota defensável.**

Isto **não** é uma proposta de apagar nada. É um facto que precisa de ficar visível
antes de alguém construir uma entrega em cima dele.

### Riscos menores

- **Rota alternativa não é o mesmo objeto.** Artigo e fala coincidem no assunto, não
  no texto. Trocar um pelo outro em silêncio é o erro que o contrato de design proíbe.
- **Medição de um IP só.** Tudo aqui foi medido de Palermo, por datacenter. Outra
  rede dá outro resultado — sobretudo para a Coldiretti.
- **Link de terceiro envelhece.** Quatro rotas vieram de `bit.ly` na descrição do
  vídeo. Encurtador morre; os URLs finais ficaram guardados no censo.

---

## K · KNOW_HOW_DELTA

```
§ A FALA NÃO É O FICHEIRO
  O ativo é o conteúdo falado, não os bytes de youtube.com. A pergunta certa não é
  «a API baixa vídeo?» — é «esta fala existe escrita no site de quem a disse?».
  Medido: 6 de 14 vídeos estratégicos têm essa outra porta ABERTA hoje, custo zero,
  e 4 delas estão escritas pelo próprio autor na descrição do vídeo.

§ O PUBLICADOR COSTUMA ENTREGAR A PORTA DE GRAÇA
  «Leggi l'articolo completo», «Scopri di più su». Ler a descrição do vídeo antes de
  discutir política de acesso poupa a discussão inteira.

§ 403 DE UM CLIENTE NÃO É PÁGINA FECHADA
  Do MESMO IP e no MESMO dia, o urllib apanhou 403 em informatoreagrario.it,
  cropscience.bayer.it e primoweb.it, e o navegador gráfico abriu os três. É
  impressão digital de cliente, não conteúdo fechado. Mesma lição do HTTP 429 do
  youtube_janela.py. Quem confundir apaga três fontes boas.

§ VERIFICAR O %PDF-, NUNCA A EXTENSÃO
  Os dois PDFs do Vinopôle foram conferidos byte a byte. O Plone já devolveu casca
  de HTML com nome .pdf nesta casa.

§ ARTIGO NÃO É TRANSCRIÇÃO
  Mesmo assunto ≠ mesmas palavras ditas. N_TRANSCRIPT_FOUND = 0 e fica zero.
  TEXT_KIND = ARTICLE, TEXT_RELATION = ORIGINAL (original dele, não do vídeo).

§ O QUE JÁ ESTÁ NO ACERVO TAMBÉM TEM ROTA
  444.810 caracteres de transcrição entraram por raspador de terceiro (a III.I.14) e
  são legenda automática, não transcrição oficial. Auditar o que entrou é tão
  necessário quanto autorizar o que ainda vai entrar.
```

## L · VEREDICTO

```
YOUTUBE_ACQUISITION = PARTIAL
```

**PASS** seria toda a amostra com rota resolvida. **FAIL** seria nenhuma.
Seis das catorze abrem hoje, sem autorização e sem custo; cinco esperam uma decisão
de gente; três continuam NÃO SEI. E a pergunta que a missão veio responder tem
resposta medida: **sim, o conteúdo falado do YouTube pode entrar no SINTONIA por
rota legítima — só que quase nunca pelo YouTube.**

## M · NEXT_MINIMUM_STEP

> **Um só:** abrir as 28 transcrições já guardadas em `SENSOR-PILOT` e registar, para
> cada uma, `TEXT_KIND` e `TEXT_RELATION` verdadeiros — legenda automática de
> raspador de terceiro, não transcrição oficial.

Vem antes de qualquer coleta nova porque é a única coisa que já está a afirmar algo
errado dentro do acervo. Enquanto não for feito, toda entrega construída em cima
dessas 444.810 letras herda a afirmação.

---

## Como reproduzir

```bash
py provas/rotas_de_fala_do_youtube.py tudo
```

Reabre as rotas oficiais e as 14 alternativas e regrava
`data/samples/YOUTUBE-ACQUISITION/MEDICAO-ROTAS.json`. Não baixa vídeo, não separa
áudio, não pede legenda, não faz login, não resolve CAPTCHA.
