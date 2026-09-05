# Vídeo, transcrição e comentário — o que existe de verdade

**Data:** 2026-09-01
**Fonte principal:** `data/samples/SENSOR-PILOT/` — piloto de sensores técnicos de 2026-08-30,
dois runners locais, 49 execuções Apify, custo declarado **USD 1,85**.
⚠️ **Este material não está no Git.** Existe só na árvore de trabalho local.

---

## 1 · O total, e o que sobra depois da peneira

| Medida | EAME | Itália |
|---|---:|---:|
| Vídeos coletados | 440 (9 duplicados interceptados → **431**) | **147** |
| Comentários | **991** (601 comentaristas únicos) | **265** |
| Transcrições | **15** (300.008 caracteres) | **5** |
| Canais com identidade resolvida | 44 candidatos: 7 PROVED · 12 PLAUSIBLE · 25 NOT_PROVED | — |

Classificação dos 431 vídeos: ruído 220 · texto insuficiente 129 · promoção de evento 48 ·
**interpretação técnica 13** · marketing 11 · **comunicação de pesquisa 8** · **observação de campo 2**

Classificação dos 991 comentários: opinião 571 · ruído 203 · pergunta 196 · **resposta técnica 13** ·
**relato de campo em primeira pessoa 6** · marketing 2

**A peneira é brutal e isso é honesto:** de 431 vídeos, 23 são tecnicamente relevantes.
De 991 comentários, 6 são relato de campo. Quem prometer "milhares de vozes do campo" está mentindo.

---

## 2 · Os 147 vídeos italianos

Dois recortes: `IT-DURUM_WHEAT-FUSARIUM` (73) e `IT-VINE-FLAVESCENCE` (74).

| Tipo de conteúdo | Vídeos IT |
|---|---:|
| NOISE | 81 |
| NOT_ENOUGH_TEXT | 41 |
| EVENT_PROMOTION | 12 |
| **TECHNICAL_INTERPRETATION** | **7** |
| MARKETING | 5 |
| **RESEARCH_COMMUNICATION** | **1** |

**56 dos 147 têm `COUNTRY_OF_FACT = IT`** provado pelo conteúdo, não pela consulta.

### 2.1 Assimetria que decide o demo

O recorte da **vite × flavescência** rendeu material italiano real e recente.
O recorte do **trigo duro × Fusarium** não: os poucos vídeos com transcrição são de canais
internacionais em inglês (*RealAgriculture*, *OGRAIN — Organic Grain Research*, *CATECP*,
*azeri teacher*). Os italianos que sobraram são telejornal local sobre apreensão de grão e
convegni de 2011–2017.

Consequência: **a camada Voci dal Campo italiana é viticultura.** Cereal é lacuna medida.

---

## 3 · As 5 transcrições italianas

| Recorte | Canal | Título | Caracteres |
|---|---|---|---:|
| `IT-VINE-FLAVESCENCE` | **Coldiretti Emilia Romagna** | CONTRASTO ALLA FLAVESCENZA DORATA DELLA VITE A CHE PUNTO SIAMO — 26/02/2026 | **97.710** |
| `IT-DURUM_WHEAT-FUSARIUM` | RealAgriculture | Timing fungicide to fight fusarium \| Wheat School | 8.459 |
| `IT-DURUM_WHEAT-FUSARIUM` | azeri teacher | Microbial Inoculants for Biocontrol of Fusarium in Durum Wheat | 7.358 |
| `IT-DURUM_WHEAT-FUSARIUM` | OGRAIN | Fusarium Head Blight Management and Harvesting in Organic Wheat | 6.237 |
| `IT-DURUM_WHEAT-FUSARIUM` | CATECP | Green Control of Wheat Fusarium Head Blight | 4.145 |

**Só uma é italiana.** As outras quatro entraram pelo recorte italiano mas o fato delas é de outro lugar —
e o dataset marca isso corretamente com `COUNTRY_OF_FACT`.

⚠️ **Todas as 15 transcrições vieram com legenda em inglês.** O campo `TRANSCRIPT_LANGUAGE` está
preenchido como "NÃO SEI" e o texto é tradução automática. Para o convegno italiano isso significa que
nomes e termos técnicos estão corrompidos e **não servem para citação literal**.

O detalhe do conteúdo do convegno está em
[`ITALY-VOCI-DAL-CAMPO-REAL-SOURCES.md`](ITALY-VOCI-DAL-CAMPO-REAL-SOURCES.md).

---

## 4 · Os 265 comentários italianos

| Tipo de fala | Comentários |
|---|---:|
| OPINION | 159 |
| QUESTION | 61 |
| NOISE | 40 |
| **TECHNICAL_REPLY** | **3** |
| **FIRST_PERSON_FIELD_REPORT** | **2** |

Por recorte: `IT-VINE-FLAVESCENCE` **235** · `IT-DURUM_WHEAT-FUSARIUM` **30**.
Com `COUNTRY_OF_FACT = IT`: **24**.

Os 5 relatos e respostas técnicas estão transcritos, com link e ressalva, no documento de Voci dal Campo.

---

## 5 · Vídeos italianos utilizáveis (os 25 que não são ruído)

Os mais fortes, por relevância agronômica e não por audiência:

| Canal | Título | Data | Views |
|---|---|---|---:|
| Agronotizie | Flavescenza dorata, la lotta alla cicalina della vite | 2024-05-28 | **36.100** |
| Provincia di Asti | Flavescenza dorata della vite | 2010-06-11 | 16.312 |
| Matej vignaiuolo in Oslavia | 6 sintomi per individuare la Flavescenza Dorata nella tua vigna | 2022-08-10 | 8.822 |
| Viticoltura Riccardo Castaldi | Vite. Gestione agronomica del primo anno | 2023-04-21 | 8.458 |
| Matej vignaiuolo in Oslavia | Flavescenza Dorata della vite \| Riconoscimento e strategie di contenimento | 2023-04-15 | 4.728 |
| Matej vignaiuolo in Oslavia | Monitoraggio dello Scafoideo sui polloni della vite | 2023-06-16 | 3.584 |
| Viticoltura Riccardo Castaldi | Vite. Flavescenza dorata: sintomi fogliari su 22 vitigni | 2022-07-02 | 3.475 |
| Coldiretti Emilia Romagna | CONTRASTO ALLA FLAVESCENZA DORATA — 26/02/2026 | 2026-03-10 | 310 |
| Comizio Agrario di Mondovì | Aggiornamenti su flavescenza dorata. Esperienze di difesa sostenibile in vigneto | 2022-11-15 | 401 |
| Confraternita di Valdobbiadene | Indagini recenti sul contenimento della Flavescenza Dorata della Vite | 2024-01-07 | 32 |
| Qdpnews | Flavescenza dorata, convegno di Confagricoltura Treviso a Valdobbiadene | 2021-12-07 | 275 |
| Infowine | Stato dell'arte della ricerca scientifica sulla flavescenza dorata — François-Michel Bernard | 2016-12-16 | 286 |
| Vinophila Wine Expo | Webinar "Emergenza Flavescenza Dorata" | 2022-10-17 | 130 |
| Confagricoltura Siena | Promo convegno "La flavescenza dorata" | 2023-01-20 | 173 |
| Sata S.r.l. | Webinar: le sfide della filiera frumento tenero tra sostenibilità e salubrità | 2020-10-02 | 179 |
| AIPO Verona | Utilizzo dello Spinosad — Spintor Fly | 2021-08-28 | 18.378 |

⚠️ **Só o vídeo da Coldiretti é de 2026.** Os demais são de 2010 a 2024. Material histórico prova
**histórico**, nunca atividade corrente. E `VIEWS` é métrica pública da plataforma, não relevância
agronômica — a ordenação acima é por utilidade, não por audiência.

---

## 6 · Limite declarado do classificador

Do próprio artefato: *"lexical. Polissemia produz falso positivo e nenhum portão automático detecta isso.
Todo item carrega `CONTENT_TYPE_EVIDENCE`; a verificação é humana."*

Antes de qualquer item destes ir para a tela do cliente, alguém precisa abrir o vídeo.
