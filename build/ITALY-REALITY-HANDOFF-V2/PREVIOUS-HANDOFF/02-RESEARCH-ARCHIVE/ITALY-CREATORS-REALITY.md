# Creators italianos — o que temos, e por que é pouco

**Data:** 2026-09-01
**Regra do acervo:** relevância agronômica vale mais que tamanho de audiência. O próprio dataset proíbe
ordenar por seguidores.

---

## 1 · Os números

25 candidatos italianos em `CREATOR-MAP-EAME/IT-CREATORS-CONSOLIDATED.json`.

| Dimensão | Estado |
|---|---|
| **Handle** | RESOLVED 16 · SEED_HANDLE_LIKELY_WRONG 4 · HANDLE_UNRESOLVED 3 · RESOLVED_MINIMAL_PRESENCE 2 |
| **Cultura** | **PROVED 1** · PARTIAL 3 · NOT_PROVED 3 · WRONG_ASSIGNMENT 3 · NOT_KNOWN 15 |
| **Aderência ao público ADAMA** | MEDIUM 4 · LOW 4 · NOT_KNOWN 17 |

**Uma única cultura provada em 25.** Isso é o número, não uma opinião sobre ele.

No conjunto EAME: 37 fichas, 10 `ACTIVATION_READY`, distribuídas por IT, ES, FR, MX, PT. A lei do
dataset é explícita: a soma **nunca** se chama `CREATORS_READY`, porque mistura pessoa com empresa.

---

## 2 · Quem são, na prática

| Nome | Handle | Cultura alegada | Cultura provada | Fit |
|---|---|---|---|---|
| Leonardo Leggeri | `@evolovers` | OLIVE | **PROVED** | MEDIUM |
| Davide Gomiero | `@davide_gomiero` | WHEAT, RICE | PARTIAL | MEDIUM |
| Maria Pezone | `@maria.pezone` | TOMATO/HORTICULTURA | PARTIAL | MEDIUM |
| Filippo Ballardin | `@filippoballardin` | WHEAT | NOT_PROVED | MEDIUM |
| Francesco Saverio Russo | `@italianwinelover` | GRAPEVINE | PARTIAL | LOW |
| Daniele Cernilli | `@doctor.wine` | GRAPEVINE | **WRONG_ASSIGNMENT** | LOW |
| Luca Gardini | `@thewinekiller` | GRAPEVINE | **WRONG_ASSIGNMENT** | LOW |
| Mirco Colzani | `@mircocolzani_gardendesigner` | FRUIT_ORCHARD | **WRONG_ASSIGNMENT** | LOW |
| Agromoderni | `@agromoderni` | WHEAT, RICE | NOT_PROVED | NOT_KNOWN |
| Yuliya Pyliavska | `@yuliyapyliavska` | MAIZE, RICE | NOT_PROVED | NOT_KNOWN |
| + 15 outros | | GRAPEVINE / OLIVE / MAIZE / TOMATO / FRUIT | NOT_KNOWN | NOT_KNOWN |

O padrão salta: **`@italianwinelover`, `@doctor.wine`, `@thewinekiller`, `@tastevo`, `@ilsommolier`,
`@oiltogether`** — são comunicadores de **vinho e azeite para consumidor**, não técnicos de campo.
Três deles têm atribuição de cultura formalmente **errada**.

Chamar isto de "camada de creators do agro italiano" seria falso. É uma **lista de candidatos de origem
externa (seed), parcialmente validada**, e o próprio artefato registra:
`STATE = CLAIMS_ONLY — nenhum campo verificado` na seed original, com 10 suspeitas de descasamento.

---

## 3 · A voz técnica italiana real não veio desta camada

Veio da busca de vídeo do piloto de sensores:

- **Viticoltura Riccardo Castaldi** — agrônomo/viticultor, conteúdo técnico sobre sintomatologia de
  flavescência em 22 castas, gestão agronômica do primeiro ano. Responde tecnicamente nos comentários.
- **Matej vignaiuolo in Oslavia** — vignaiolo do Collio (Gorizia, FVG), três vídeos sobre reconhecimento
  de flavescência e monitoramento de escafoideo, 3,5k–8,8k views cada.
- **Agronotizie** — canal editorial da Image Line; 36.100 views no vídeo sobre a cicalina da vite.
- **Vito Vitelli Agronomo** — encontrado na pesquisa externa de hoje, **não** está no acervo:
  agrônomo, diretor do Consorzio Vivaisti Lucani, ~15 mil inscritos, 306 vídeos, 62 publicados só em 2024,
  temas de fruticultura, citricultura e olivicultura.

⚠️ Nenhum destes quatro está na camada de creators do Sintonia. Três entraram como *canal de vídeo*
(sem identidade resolvida: dos 44 candidatos de canal, só 7 `PROVED`) e um só apareceu hoje.

---

## 4 · A lacuna que importa

**Não existe creator técnico italiano de milho, cereal ou soja no acervo.** As culturas onde o portfólio
ADAMA italiano é mais forte (herbicida de milho, cereal, soja, arroz, barbabietola) são exatamente as que
não têm voz mapeada.

Uma busca externa de hoje confirmou a assimetria: o segmento seminativi/cerealicolo italiano é coberto por
**canais de entidade e revista técnica** (Agronotizie, Terra e Vita, CREA, consórcios agrários,
Coldiretti regional), **não** por divulgadores individuais — ao contrário de vite e fruticultura, onde há
pessoas com canal próprio.

Isto não é falha da coleta. É uma característica do mercado italiano, e é uma informação em si.

---

## 5 · O que o demo pode dizer

✅ *"O Sintonia mapeou 25 contas italianas candidatas; uma tem cultura provada por conteúdo."*
✅ *"A voz técnica italiana que a coleta encontrou está no YouTube, em canais de viticultura e de
entidade — e o segmento de seminativi é coberto por revista técnica, não por criador individual."*

❌ *"25 creators italianos do agro."* — 15 têm cultura não sabida e 3 têm atribuição errada.
❌ Qualquer ordenação por seguidores.
❌ Qualquer palavra que sugira relação comercial: `ADAMA_COLLABORATION_OBSERVED` é falso em todos.
