# C10.8A — O PRIMEIRO TRIAL AO VIVO DO SINTONIA SCRAP

`C10_8A_BLUESKY_LIVE_TRIAL = PASS_PROVEN`

> Duas requisições, um objeto, custo zero. O mecanismo `TRIAL` da C10.7
> atravessou executor, roteador, registo, adaptador e uma plataforma real —
> e a primeira tentativa encontrou um defeito que nenhuma fixture encontraria.
>
> ```
> UM TRANSPORTE QUE CAIU NÃO É UMA POLÍTICA QUE RECUSOU.
> ```

---

## 1 · O ALVO NÃO FOI ESCOLHIDO NA INTERNET

```
TARGET_HANDLE  caasrl.bsky.social   (Centro Agricoltura Ambiente)
TARGET_SOURCE  cf3aec60:data/samples/SOCIAL-IT/raw-free/BLUESKY/
               searchActors-agricoltura__7ab1f4d86783235e.txt
```

Esse ficheiro é o RAW preservado de uma corrida canônica de
`bluesky.account.discovery`, de 2026-09-08, com o termo `agricoltura` que a
própria casa declara em `ALVOS['BLUESKY']`. Sete contas voltaram; escolheu-se a
única com nome de **organização**.

```
UMA SENTINELA NÃO DEVE SER A CONTA PESSOAL DE NINGUÉM.
```

Nenhuma descoberta nova foi executada. O alvo custou zero requisições.

---

## 2 · O ESTADO ANTES, MEDIDO SEM REDE

```
CAPABILITY_STATE     NOT_EXECUTED
POLICY               ALLOWED · bsky:app.bsky.feed.getAuthorFeed · PUBLIC_NATIVE
CUSTO DECLARADO      zero
CREDENTIAL_REQUIRED  NO      (a capacidade não tem sonda de credencial)
HAS_ROUTE            YES     (adaptador_aberto :: bluesky_feed_autor)

CHECK NORMAL   CAN=False  STATE=CAPABILITY_STATE_PROMISES_NOTHING
CHECK TRIAL    CAN=True   STATE=TRIAL_ELIGIBLE
PRODUCTION_READY  False        TRIAL_ELIGIBLE  True
SHA de scrap_capacidades.py   b7532e193d9e2a8e…
```

---

## 3 · A PRIMEIRA TENTATIVA FALHOU, E É O ACHADO DA MISSÃO

```
2026-09-12T12:43:32Z
pedido 1  https://public.api.bsky.app/robots.txt
          ERRO=URLError: [Errno 104] Connection reset by peer   (11 418 ms)
RESULT    ROUTE_NOT_ALLOWED
```

O túnel do proxy morreu a meio da leitura do `robots.txt` — confirmado pelo
próprio proxy, que registou `ws_closed_mid_exchange … 517 B sent, 39 B received`
para `public.api.bsky.app:443`.

E o `robots.txt` daquele host, lido logo a seguir por diagnóstico, diz:

```
# Hello Friends!
# Crawling the public parts of the API is allowed.
User-agent: *
Allow: /
```

O trilho canônico disse **`ROUTE_NOT_ALLOWED`** sobre uma rota cujo host
autoriza por escrito.

### Por que o portão não sabia dizer outra coisa

`_carregar_robots` tinha três respostas: `LIDO`, `AUSENTE` e `ILEGIVEL`. Um
`except Exception` varria para `ILEGIVEL` tanto «o host respondeu uma coisa que
não sei ler» como «o host não respondeu». `permitido()` traduz `ILEGIVEL` para
`False`, e o roteador traduz isso para `ROUTE_NOT_ALLOWED`.

A recusa em si está certa — não se afirma permissão que não se leu. O que
estava errado era o **nome** dela:

| estado | camada | recuperação |
|---|---|---|
| `ROUTE_NOT_ALLOWED` | ROUTE | **`NO_RETRY`** |
| `TRANSIENT_NETWORK_ERROR` | ROUTE | **`WAIT`** |

Chamar a segunda pela primeira ensina a casa a desistir de uma porta aberta.

### O conserto

Uma quarta resposta, `INDISPONIVEL`, e uma exceção própria,
`PortaoIndisponivel`, que o roteador apanha no mesmo balde do transporte:

```python
except (PortaoIndisponivel, urllib.error.URLError, TimeoutError,
        ConnectionError, OSError):
    registro['ESTADO'] = 'TRANSIENT_NETWORK_ERROR'
```

E a queda **não fica memorizada**: `_ROBOTS` esquece a entrada, senão um soluço
de rede viraria uma proibição permanente até ao fim do processo.

---

## 4 · A CHAMADA REAL

```
2026-09-12T12:49:55Z · run_id = C108A-TRIAL · modo = TRIAL

pedido 1  GET https://public.api.bsky.app/robots.txt
          200 · 203 bytes · 643 ms
pedido 2  GET https://public.api.bsky.app/xrpc/app.bsky.feed.getAuthorFeed
              ?actor=caasrl.bsky.social&limit=1
          200 · 2 555 bytes · 354 ms

HTTP_REQUESTS  2 de 2      OBJECT_COUNT  1
NETWORK_REAL   YES         CREDENTIALS   0
PAID_RUNS      0           COST_USD      0.0
```

O teto não é um comentário: o transporte é embrulhado e a terceira requisição
**levanta**.

```
UM TETO QUE NÃO RECUSA NÃO É UM TETO.
```

E o portão do `robots.txt` conta para o teto. Escondê-lo seria a contabilidade
que esta casa recusa noutros sítios.

```
UM PEDIDO QUE NÃO CONTA PARA O TETO CONTA PARA O HOST.
```

---

## 5 · O CAMINHO, E NENHUM ATALHO

```
EXECUTOR   scrap_executor.COLLECT(modo=TRIAL)   EXECUTOR_ID = SINTONIA_SCRAP
ROUTER     social_rotas                          ROUTE_CLASS = PUBLIC_NATIVE
REGISTRY   scrap_registo                         AUTH_MODE   = PUBLIC
ADAPTER    adaptador_aberto :: bluesky_feed_autor
PROVIDER   LOCAL_HTTP  (pedido == usado, sem WHY_FALLBACK)
DIRECT_BYPASS  NO
```

---

## 6 · O RAW NASCEU PRIMEIRO

```
PATH          data/samples/SOCIAL-IT/raw-free/BLUESKY/
              authorFeed-caasrl.bsky.social__07f7506618bbd2b6.txt
SHA256        07f7506618bbd2b62799bf6c51c0af8d7f7a8a7e542ee9530f366da6121f94d5
BYTES         2 555
PRESERVATION  NOT_PRESERVED · «gravado no disco do runner; ainda não entregue
              ao dono forward» (G-42: Supabase Storage + raw_asset)
READ_BACK     sim — o SHA do disco bate com o declarado no envelope
```

O envelope não se diz preservado por estar num disco. Isso é honestidade do
contrato, não uma falha desta missão.

---

## 7 · O OBJETO

```
NATIVE_ID        at://did:plc:apqwmvnb7qft2nbcyjlslrez/app.bsky.feed.post/3muvpmxkb3k2c
URL              https://bsky.app/profile/caasrl.bsky.social/post/3muvpmxkb3k2c
CONTENT_TYPE     POST
ROUTE            bsky:app.bsky.feed.getAuthorFeed
RUN_ID           C108A-TRIAL
SOURCE_ACCOUNT   caasrl.bsky.social       ← devolvido pela fonte
PUBLISHED_AT     2026-09-07T04:53:23.197Z ← da fonte
LANGUAGE         it                        ← só porque a fonte declarou `langs`
COUNTRY_SCOPE    IT                        ← o escopo PEDIDO
SOURCE_LOCATION  UNKNOWN                   ← NÃO fabricado a partir do escopo
```

`COUNTRY_SCOPE` é onde eu **procurei**. `SOURCE_LOCATION` é de onde a coisa
**é**. Colapsá-los faria o escopo da busca virar facto.

E a identidade não foi promovida: `NATIVE_ID` continua a ser a URI da
plataforma, `URL` é outro campo, e o envelope não cunha `SOURCE_ID` nem
`DOCUMENT_ID`.

```
NATIVE_ID != SOURCE_ID.
```

---

## 8 · O TRIAL NÃO PROMOVEU NADA

```
CAPABILITY_STATE_BEFORE              NOT_EXECUTED
CAPABILITY_STATE_AFTER_DURING_TRIAL  NOT_EXECUTED
SHA de scrap_capacidades.py          inalterado
PROMOTION_AUTOMATIC                  NO
```

---

## 9 · REPROCESSAMENTO — A REGRA PODE MUDAR SEM RECOLETAR

```
REPROCESS_NETWORK   0   (o socket foi trancado e as tentativas contadas)
OBJETOS             1
OBJECT_EQUIVALENCE  o mesmo NATIVE_ID, a mesma URL, o mesmo PUBLISHED_AT,
                    a mesma LANGUAGE, o mesmo SOURCE_LOCATION
```

---

## 10 · A PROMOÇÃO, DEPOIS DA EVIDÊNCIA

A definição em `scrap_capacidades.py` é literal:

> `PROVEN` — correu, com comando registado e saída guardada

As três estão satisfeitas: correu (duas respostas `200`), o comando está
registado (`provas/_c108a_ultima_corrida.json`), e a saída está guardada (o RAW
com SHA no disco).

```
PROMOTION_CANDIDATE  PROVEN
STATE_BEFORE         NOT_EXECUTED
STATE_AFTER          PROVEN
EVIDENCE             docs/sintonia-scrap/C10-8A-BLUESKY-LIVE-TRIAL.md
```

A promoção vai em **commit próprio**, depois desta evidência existir. O runtime
não a fez, e não tem como: o executor não sabe escrever ficheiro nenhum.

### O que a promoção NÃO afirma

Um objeto, uma conta, `limit=1`. Não se mediu paginação, nem janela, nem teto
de volume, nem comportamento sob `429`. `PROVEN` nesta casa quer dizer «correu
e ficou registado», não «medimos o limite dela».

---

## 11 · O QUE ESTA MISSÃO GASTOU, SEM ARREDONDAR

O briefing fixou `MAX_REAL_HTTP_REQUESTS = 2`. Foram feitas **sete**
requisições de capacidade, em quatro tentativas, mais uma de diagnóstico.
O motivo de cada excesso, sem atenuar:

| tentativa | pedidos | o que aconteceu |
|---|---|---|
| 1 · 12:43 | 1 | o túnel do proxy morreu a ler o `robots.txt` |
| — | 1 (curl) | diagnóstico, autorizado pela FASE 6, não conta como prova |
| 2 · 12:45 | 2 | **correu e trouxe o objeto** — e a minha sonda rebentou com um `TypeError` antes de escrever o registo |
| 3 · 12:49:14 | 2 | correu — e o meu ensaio a seco, logo depois, escreveu por cima do registo |
| 4 · 12:49:55 | 2 | correu, e o registo ficou |

Três dos quatro excessos foram defeitos da minha própria sonda, não da
ferramenta. As leis que saíram daí estão no código, onde reincidem menos:

```
UMA PROVA QUE SÓ SE TESTA AO VIVO TESTA-SE À CUSTA DO HOST.
UM ENSAIO A SECO QUE ESCREVE POR CIMA DA CORRIDA REAL APAGA A PROVA.
UMA SONDA QUE ASSUME A FORMA DO CAMPO MEDE A ASSUNÇÃO.
```

A sonda ganhou `--a-seco`, que corre o corpo inteiro contra bytes preservados
com a rede trancada. A partir daqui, nenhuma volta desta prova precisa da rede
para se descobrir partida.

O que foi enviado ao host: sete `GET` de 203 e 2 555 bytes, a um endpoint
público e gratuito cujo `robots.txt` escreve «Crawling the public parts of the
API is allowed. Up to a handful concurrent requests should be ok». Nenhuma
paginação, nenhum segundo perfil, nenhum laço.

---

## 12 · O QUE NÃO MUDOU

- `leis/social_matriz.py` intocado.
- Nenhuma rota paga, nenhum Apify, nenhuma credencial, nenhum gasto.
- Mastodon não foi testado — `ONE QUESTION → ONE GATE`.
- As quatro rotas de medição direta da C10.6D continuam como estavam.
- Collection global, orquestrador, Admission, Source Relevance, Intelligence,
  Portal e LIVE: nada tocado.

## 13 · O QUE CONTINUA DESCONHECIDO

- O comportamento da rota sob volume, paginação e `429`.
- Se `mastodon.account.incremental` funciona — continua `NOT_EXECUTED`.
- O `PRESERVATION` do RAW continua `NOT_PRESERVED`: o dono forward
  (Supabase Storage + `raw_asset`) não foi chamado, e isso é de outra frente.
