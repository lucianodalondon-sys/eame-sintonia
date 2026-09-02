# LACUNAS CONHECIDAS — o que este pacote não tem, e por quê

**Atualizado em 2026-09-02, depois da varredura noturna.** Duas lacunas fecharam, uma
mudou de natureza e uma nova apareceu.

Cada lacuna traz o **estado** e o **motivo**. Estado importa: `SEM PORTA` é diferente de
`RENDEU ZERO`, e `BLOQUEADO POR IP` é diferente de `NÃO EXISTE`.

---

## ✅ 1 · FECHADA — a fenologia corrente

**Antes:** *"sinais de estádio fenológico lidos para setembro de 2026: ZERO. É a maior
lacuna do pacote."*

**Agora:** **73 boletins de 6 regiões, todas alcançadas**, com data de 26/08 a
**01/09/2026** — o mais recente é de ontem.

| região | boletins | mais recente |
|---|---:|---|
| Puglia | 24 | 26/08/2026 |
| Emilia-Romagna (6 unidades territoriais) | 13 | **01/09/2026** |
| Lombardia | 12 | 28/08/2026 |
| Toscana + Friuli-Venezia Giulia | 12 | 27/08/2026 |
| Piemonte | 6 | 28/08/2026 |
| Marche + Umbria | 6 | 26/08/2026 |

⚠️ **O que NÃO mudou:** continua sendo **cobertura, não censo**. São 6 regiões de 20, e
nenhuma delas fala pelo país. E parte das culturas foi **inferida das avversità citadas**,
não declarada pelo boletim — isso vai marcado item a item em `CROP_STATE`.

---

## ✅ 2 · FECHADA — a rota ISMEA/ISTAT, com veredito definitivo

A pergunta era: *a fonte está fora do ar, ou é o nosso IP?* Agora há prova.

O IP de saída é **179.172.231.127** — Vivo residencial, São Paulo. Testando as mesmas URLs
a partir de nós em outros países:

| | Milão | Berlim | Helsinque | Miami | Canadá | **aqui** |
|---|---|---|---|---|---|---|
| `www.ismea.it` | 301 ✅ | 301 ✅ | 301 ✅ | 301 ✅ | 404 ❌ | **404 ❌** |

> Corpo literal do bloqueio: *"You have been blocked … 179.172.231.127 **GEO_IP_BLOCK**
> © Barracuda Networks, Inc."*

E a ISTAT é ainda mais específica: `esploradati.istat.it` responde **302 de outro IP
brasileiro** e dá timeout de TCP em 9 de 9 tentativas **desta linha**. Não é bloqueio de
país — é esta rota.

**Veredito:** o Market Pulse italiano **não pode** ter camada ISMEA/ISTAT nativa daqui.
**Pode** ter substituto via **Eurostat**, que responde e cobre produção vegetal nacional,
produção por região NUTS-2 (Veneto = ITH3) e venda de defensivos — todos com atualização
em 2026. Não é o mesmo produto, e isso vai dito.

⚠️ **Armadilha registrada:** no Internet Archive, snapshots da ISMEA de 2026 com HTTP 200
e 1.199–1.409 bytes compartilham o mesmo digest e contêm `captcha`. **O arquivo capturou a
página de bloqueio, não o conteúdo.** Quem contar esses como "página recuperada" está
contando bloqueio como dado.

---

## 🆕 3 · NOVA — nem toda voz de campo é voz de lavoura

A coleta noturna triplicou os relatos em primeira pessoa. A leitura ingênua seria
"triplicamos a voz do campo italiano". Lendo um a um, a maioria fala de **roseira,
limoeiro e aveleira de quintal**.

| plateia do canal | falas italianas |
|---|---:|
| `PROFESSIONAL_FIELD_AUDIENCE` | **24** |
| `HOBBY_GARDEN_AUDIENCE` | **32** |
| `NOT_KNOWN` | 2 |

> **Relato em primeira pessoa sobre um vaso não é voz de lavoura.**

A distinção é do **canal**, não do comentário, e é uma **lista declarada** — canal fora da
lista sai `NÃO SEI`, jamais "profissional por omissão". As duas classes **não se somam**.

---

## ⚠️ 4 · Cobertura de rótulo — continua aberta, e é a mais cara

- **19 de 163 produtos (11,7%)** têm ao menos uma linha de uso lida
- **144 (88,3%)** têm zero — desses, **82 têm cultura E alvo no rótulo, sem ligação lida**
- **36 das 49 linhas (73,5%)** não cumprem a definição da própria classe (que exige dose)
- **GRAPEVINE: 61 produtos mencionam, 1 tem linha de uso** — distância de 60

E um achado de método: **o verificador de gênero de um rótulo italiano é o dicionário EPPO
espanhol.** Gêneros só italianos passam sem conferência — `Scaphoideus` não está nele.

⚠️ **Os 163 PDFs de rótulo não estão neste disco.** Foram baixados em 30/08 em outra
máquina. A rota está documentada e é gratuita: `POST cercaProdotti → EtichettaServlet?id=`.
**Esta é a próxima coleta de maior retorno.**

---

## 🚪 5 · Portas de escuta social que nunca abrimos

| porta | estado |
|---|---|
| Instagram italiano | 🚪 **SEM PORTA** — 399 posts orgânicos no acervo, todos de creators ES/FR |
| Facebook orgânico | 🚪 **SEM PORTA** — todo Facebook que temos é Meta Ads Library (pago) |
| X / Twitter | 🚪 **SEM PORTA** |
| TikTok | 🚪 **SEM PORTA** |
| Podcast | 🚪 **SEM PORTA** como objeto próprio |
| LinkedIn italiano | ⚠️ **MEDIDO E REPROVADO** — `HUMAN_SENSOR_ADDS_NOTHING_IN_THIS_PANEL` |

⛔ **`SEM PORTA` ≠ `RENDEU ZERO`.** Um relatório que diga "0 menções no Instagram" está
mentindo: nunca abrimos a porta.

---

## ⚠️ 6 · Integridade do par cultura × alvo

Sete alvos gravados são **gêneros que também nomeiam cultura**: `Avena sp`,
`Sorghum halepense`, `Raphanus sp`, `Sinapis sp`, `Lolium sp`, `Chenopodium sp`,
`Amaranthus sp`. Um produto com zero linha traz `Daucus carota` — o binômio da cenoura.

**Estado:** suspeita de colisão registrada, **não** veredito de erro. Mesma classe do caso
brasileiro «Nabo-bravo × *Gossypium hirsutum*», onde o apelido batia exato.

---

## ⚠️ 7 · Séries de preço que morreram

A praça que para de cotar **mantém a última cotação no índice**. Exemplo real: azeite em
Salerno, €630, de **setembro de 2015**. Todo preço no pacote traz `SERIES_STATE`.

Vinho: a série de preço por praça da UE para a Itália está **parada desde julho de 2025**.

---

## ⛔ 8 · O que exige dado interno da ADAMA

```
sell-in · sell-out · CRM · pedidos · pipeline · estoque de distribuidor
estoque de armazém · preço realizado · venda por região · margem · share
```

**Estado:** `INTERNAL_DATA_REQUIRED`. Na tela: **«dado interno não conectado»** — nunca
zero, nunca valor sintético.

---

## ⚠️ 9 · Nível 2 do sinal continua bloqueado

O nível 2 exige **proporção entre duas janelas comparáveis**, e a coleta italiana tem
**uma janela só**. Publicar variação seria inventar série. `NAO_MEDIDO`.

---

## 📋 10 · O que ficou a um passo

- os **mapas nacionais do GIRE** — o índice foi lido; os mapas em si, parcialmente
- **os PDFs de rótulo** — a rota existe e é grátis (ver §4)
- o **catálogo ADAMA 2026 em PDF** — o WAF recusa `curl`, só abre em janela gráfica
- **16 das 29 páginas «ADAMA in campo»**
- a **Regione Veneto** — bloqueia IP estrangeiro, como a ISMEA
