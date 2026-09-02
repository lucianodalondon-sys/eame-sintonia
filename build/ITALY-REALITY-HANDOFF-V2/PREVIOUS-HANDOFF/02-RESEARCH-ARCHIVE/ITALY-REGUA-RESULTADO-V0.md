# O que a régua devolveu — coleta nova + filtragem herdada do Brasil

**Data:** 2026-09-02
**Contrato:** [`docs/regras/REGUA-ITALIA-FITOSSANITARIA.md`](../../docs/regras/REGUA-ITALIA-FITOSSANITARIA.md)
**Pai:** `portal-sintonia/REGUA-MISSAO-5-FITOSSANITARIO.md` (Brasil, 23/08/2026)
**Artefato:** `data/samples/IT-REGUA/IT-PARES-CULTURA-ALVO-V0.json`

---

## 1 · A coleta nova

Chave Apify descartável, orçamento US$ 5, ciclo fechando em 03/09. **Estado final: ENCERRADA.**

| Lote | Recortes | Vídeos | Transcrições | Comentários |
|---|---|---:|---:|---:|
| **C** | IT-MAIZE-WEED · IT-CEREAL-WEED · IT-SOYBEAN-AMARANTHUS | 177 | 9 | 335 |
| **D** | IT-SUGARBEET-WEED · IT-RICE-WEED · IT-APPLE-DISEASE · IT-VINE-WEED | 252 | 3 | 686 |

Acervo antes → depois: **431 → 603 vídeos** · **15 → 24 transcrições** ·
**991 → 1.326 comentários** · **601 → 777 autores distintos** · **6 → 9 recortes**.

Sobreposição com o que já existia: **6 vídeos em 429**. O universo é novo de verdade —
**232 canais distintos** nos dois lotes.

### 1.1 ⚠️ O custo que eu anunciei errado

Eu te disse US$ 0,62 e depois US$ 0,90. **O custo real foi US$ 5,044.**

O motivo é uma armadilha da plataforma: o coletor lê `usageTotalUsd` no instante em que a
execução termina, e nesse momento a Apify **ainda não fechou a conta** — o campo vem `0`.
As buscas de vídeo, que eu anunciei como "grátis", custaram **US$ 2,77**.

```
CUSTO LIDO CEDO DEMAIS NÃO É CUSTO ZERO.
```

É a mesma família do erro que o `apify_pool` já documentava para a cota ("cota esgotada se
apresenta como sucesso"). Corrigido em `scripts/corrigir_custo.py`, que relê o custo real
na plataforma e **preserva o valor errado** em `COST_USD_AT_WRITE_TIME` — apagar o erro
apagaria a prova de que ele existe.

| Artefato | Anunciado | Real |
|---|---:|---:|
| VIDEOS-C | 0,0000 | **1,1920** |
| TRANSCRICOES-C | 0,0000 | 0,0900 |
| COMENTARIOS-C | 0,6220 | 0,6700 |
| VIDEOS-D | 0,0000 | **1,5800** |
| TRANSCRICOES-D | 0,0000 | 0,0300 |
| COMENTARIOS-D | 0,2820 | **1,4820** |
| **TOTAL** | **0,9040** | **5,0440** |

---

## 2 · A régua — o que eu teria errado sozinho

Quatro leis vieram do Brasil e mudaram o resultado:

| Lei herdada | O que eu ia fazer |
|---|---|
| **A unidade é o PAR `cultura × alvo`** | contar vídeos e comentários por tema |
| **Contagem bruta não é sinal de alta — só proporção** | publicar "37 menções" como se fosse crescimento |
| **O PAR é INFERIDO pelo sistema** | tratar a ligação como observada |
| **Comentário é PLATEIA daquele canal, nunca produtor** | dizer "o produtor italiano relatou" |

### 2.1 ⭐ O acréscimo italiano: a quarentena entre línguas

O Brasil precisou resolver `ferrugem` (doença × metal) e `acaro` (lavoura × poeira).
A Itália tem isso **e mais** a colisão entre línguas, porque a mesma busca devolveu
itálico, espanhol, francês e inglês no mesmo saco.

**O que a quarentena barrou, medido:**

| Termo | Colisão | Barrados |
|---|---|---:|
| `vite` | videira × **parafuso** (dentro do italiano) | **124** |
| `mais` | milho × **"mas" francês** | **68** |
| `pero` | pereira × **"porém" espanhol** | **29** |
| `grano` | trigo italiano × grão espanhol | 14 |
| `cicalina` | cigarrinha genérica × Scaphoideus | 4 |
| `riso` | arroz × riso de rir | 2 |

**241 pares falsos não entraram.** Sem essa camada, `VITE × qualquer coisa` teria triplicado
por causa de gente falando de parafuso de trator.

E há uma trava a mais: a **língua é medida** por marcador funcional, nunca herdada do
`CASE_ID` — porque o `CASE_ID` diz de que *consulta* o item veio, não em que língua ele
está. Dos 1.929 documentos lidos, **339 são italianos**; 653 ficaram em `NÃO SEI` (quase
todos comentários curtos demais para medir).

---

## 3 · O resultado

**46 pares `cultura × alvo`**, de 1.929 documentos.

| Nível | Pares | O que significa |
|---|---:|---|
| **3 · SINAL CORROBORADO** | **3** | o par aparece em **duas portas nativas independentes** |
| **1 · MENÇÃO TEMÁTICA** | 8 | o documento trata do par. **Não** é sinal de aumento |
| **NÃO SEI · amostra insuficiente** | 35 | menos de 3 documentos. Par a investigar, não par ruim |

**NÍVEL 2 está `NAO_MEDIDO`, e o motivo é medido:** a coleta italiana tem **uma janela só**.
Sem duas janelas comparáveis não há proporção, e publicar variação seria inventar série.

### 3.1 Por categoria de produto — a régua reproduziu o portfólio sozinha

| Categoria | Pares |
|---|---:|
| **HERBICIDA** | **21** |
| FUNGICIDA | 12 |
| INSETICIDA | 9 |
| ACARICIDA | 2 |
| FITOPLASMA | 2 |

O eixo herbicida produz **mais pares que qualquer outro** — sem que ninguém tenha dito à
régua que 55% do portfólio italiano da ADAMA é herbicida. As duas medições são
independentes e apontam para o mesmo lado.

⚠️ **Mas com uma ressalva que muda a leitura:** os pares de herbicida são **largos e
rasos**. Só dois passam de 2 documentos (`MAIS × SORGHETTA` com 4, `FRUMENTO × LOIETTO` com 3);
os outros 19 têm 1 ou 2. O que é **grande** não é o par nomeado — é o assunto:

| Eixo próprio (nunca ao lado de um organismo) | Documentos | Fontes |
|---|---:|---:|
| **ASSUNTO_DISERBO** | **78** | 28 |
| ASSUNTO_RESISTENZA | 23 | 15 |
| ASSUNTO_MICOTOSSINA | 18 | 16 |

Leitura honesta: **a Itália fala muito de diserbo e pouco de cada erva com nome.**
O sinal está no assunto, não no par. Dizer "MAIS × SORGHETTA é o grande tema italiano de
daninha" seria trocar 4 documentos por 78.

### 3.2 Os três pares corroborados

| Par | Documentos | Fontes | Portas | Camadas |
|---|---:|---:|---:|---|
| **VITE × FLAVESCENZA** | 37 | **19** | 2 | 28 FONTE · 9 PLATEIA |
| **VITE × SCAFOIDEO** | 12 | 8 | 2 | 11 FONTE · 1 PLATEIA |
| **VITE × PERONOSPORA** | 6 | 3 | 2 | — |

Os três são de vite. Isso confirma, por uma terceira rota independente, o que o portfólio
e os decretos já diziam — e confirma também a assimetria: **a voz italiana que temos é de
viticultura.**

---

## 4 · O achado que a coleta nova entregou

### 4.1 ⭐ O GIRE apareceu — falando, com nome e rosto

Na primeira rodada eu declarei uma lacuna: *"o site do GIRE devolveu certificado expirado;
a linha-guia precisa ser aberta antes de virar peça de demo"*. **A coleta de vídeo resolveu
por outra porta.**

| Pessoa | Papel | Onde |
|---|---|---|
| **Maurizio Sattin** | dirigente de pesquisa **CNR-IPSP** e **coordenador do GIRE** | L'Informatore Agrario, 03/05/2022, *"Infestanti resistenti della soia"* — nomeia *Amaranthus hybridus, A. tuberculatus, A. palmeri* (2.823 views) · Giornate Fitopatologiche GF 2020 — nomeia *Lolium, Papaver rhoeas, Echinochloa, Sorghum halepense, Amaranthus* spp., *Eleusine indica* · Agronotizie 24/02/2021, resistência a ACCase e ALS |
| **Donato Loddo** | pesquisador **CNR**, **membro do GIRE** | **Bayer Crop Science Italia**, 12/10/2022, *"La gestione delle malerbe resistenti in cerealicoltura"* — **36.412 views** |

Isto fecha a perna que faltava do candidato **OC-2 (soja/milho × *Amaranthus* ALS-resistente)**:
a autoridade italiana em resistência a herbicida agora tem **pessoa nomeada, vídeo datado e
espécies citadas** — não mais só resumo de busca.

### 4.2 ⭐ E ele aparece no canal do concorrente

O vídeo de maior alcance com um membro do GIRE (36.412 views) é **da Bayer**. E o vídeo da
Agronotizie com o coordenador do GIRE traz, na própria descrição, *"Contenuto promosso da:
Bayer"*.

Ou seja: **o concorrente contrata a autoridade independente para dar credibilidade ao
próprio conteúdo de resistência.** É comportamento de comunicação observável, datável e
citável — e o acervo não tinha nada disso.

⚠️ O que isto **não** prova: nada sobre eficácia de produto, nada sobre o que o pesquisador
pensa da Bayer, e nada sobre a ADAMA.

### 4.3 ⭐ Bayer coordenou canais no mesmo produto e na mesma semana

| Data | Canal | Peça |
|---|---|---|
| **03/03/2026** | YouTube Bayer Italia | *"Adengo Xtra: risultati in campo nel diserbo del mais"* — **140.623 views** |
| **04/03/2026** | Meta Ads (já no acervo) | anúncio do **mesmo Adengo Xtra**, milho |
| 10/03/2026 | YouTube Bayer Italia | *"Diserbo del mais in pre-emergenza con Adengo Xtra"* — 8.053 views |
| 09/04/2026 | YouTube Bayer Italia | *"Diserbo in post-emergenza"* — 7.010 views |

O acervo só tinha o lado pago. Agora tem os dois, e eles batem na data.

### 4.4 ⭐ Agricultores italianos nomeando herbicida e dizendo se funcionou

Foi o que os recortes de daninha entregaram e os de doença nunca tinham entregado:

> *"Ho provato un anno **adengo** in pre emergenza un disastro (era però il 2017 anno tremendo
> per poca pioggia) dal 2018 sempre in post emergenza ma con ottimi risultati."*
> — comentarista em vídeo do canal *Agricoltura Innovativa*

> *"io **adengo** l'ho usato qualche anno fa ma mi ha creato problemi di tossicità sul mais.
> Ora uso **Merlin Flex** è simile però non mi ha mai creato problemi ed è ugualmente efficace"*
> — idem

> *"ho fatto 2 **epik sl** ma sembra che il principio non sia molto efficace poi ho fatto
> **evure pro** (sembra più efficace) principio attivo **tau fluvalinate**…"*
> — comentarista em vídeo de *Matej vignaiuolo in Oslavia*

⚠️ **EVURE PRO é um dos 6 produtos ADAMA que nomeiam *Scaphoideus titanus* no rótulo.** É a
primeira vez que uma voz pública italiana nomeia um produto ADAMA e diz como ele se comportou.

⛔⛔ **E aqui a régua do Brasil segura a mão, com razão:** isto é **PLATEIA de um canal**, não
produtor identificado. `FALHA DE CONTROLE` **não tem dono** nesta casa, e não se cria detector
novo nesta fase. A frase permitida é *"um comentarista, em vídeo de tal canal, escreveu X"* —
nunca *"o produtor relatou que o produto não funcionou"*.

---

## 5 · Duas réguas discordaram, e isso fica registrado

O classificador de **tipo de conteúdo** (léxico, herdado do piloto) marcou como **`NOISE`**
todos os vídeos do GIRE, incluindo o de Sattin na L'Informatore Agrario e o de Loddo na Bayer.
A régua do **par** marcou os mesmos vídeos como evidência válida de `SOIA × AMARANTO` e
`FRUMENTO × LOIETTO`.

```
CLASSIFICADOR DE TIPO: NOISE
RÉGUA DO PAR:          NÍVEL 1, com cientista nomeado
```

A régua do par está certa aqui. O classificador de tipo tem léxico de **doença em perene**
(`abbiamo osservato`, `primi sintomi`) e nenhum marcador de comunicação técnica de daninha.

**ACHADO REGISTRADO, NÃO CONSERTADO.** Unificar os dois é mexer em régua que já produziu
artefato citado — é decisão dele, não minha. Do mesmo jeito que a régua brasileira registrou
que `vocabulario.py` e `dores.py` divergem em 5 de 12 chaves e não uniu.

---

## 6 · A segunda rodada, sem chave nenhuma — US$ 0,00

Depois que a chave esgotou, quatro rotas gratuitas ainda estavam abertas. Três delas
fecharam lacunas que eu mesmo tinha declarado.

### 6.1 ⭐ O bloqueio do OpenAlex era do ambiente, não da fonte

`ITALY-RESEARCHER-UNIVERSE.json` deixou quatro cortes como `NOT_COLLECTED` por HTTP 429, e
o diagnóstico registrado dizia *"oito horas depois da rajada original o IP deste ambiente
continua recusado"*.

**Medido em 02/09/2026 deste ambiente: HTTP 200 na primeira tentativa, e a contagem bate
exatamente com a declarada (135).** O limite era do **IP de saída daquele ambiente** — não
da fonte, não da consulta, não do volume.

⚠️ `NOT_COLLECTED` estava certo como **estado**. O que muda é o diagnóstico da **causa** —
e isso importa porque "esperar mais" nunca ia resolver.

| Recorte | Obras | Autores IT | Com ORCID | Ativos desde 2024 |
|---|---:|---:|---:|---:|
| **VINE_FLAVESCENCE** | 135 | **334** | 213 | 195 |
| DURUM_FUSARIUM | 70 | 235 | 195 | 92 |
| OLIVE_BACTROCERA | 71 | 223 | 188 | 106 |
| MAIZE_BORER_DIABROTICA | 27 | 62 | 50 | 17 |
| ⭐ **WEED_HERBICIDE_RESISTANCE** (novo) | 17 | 22 | 17 | 11 |

O quinto corte é acréscimo meu: a ciência italiana do acervo era toda de doença, e 55% do
portfólio é herbicida.

**E ele corroborou o vídeo por rota independente:** `Maurizio Sattin` (CNR-IPSP), que os
vídeos mostraram como coordenador do GIRE, aparece com 4 obras — ao lado de
**Laura Scarabel** (6) e **Silvia Panozzo** (5), do mesmo instituto.

Na flavescência, o mesmo aconteceu: **Domenico Bosco** (Univ. Torino, 19 obras) é o nome
que já tinha aparecido falando no convegno da Coldiretti Emilia-Romagna. E
**Elisa Angelini** e **Luisa Filippin** (CREA, 20 obras cada, última atividade **30/07/2026**)
são gente do CREA-VE — um dos *referenti scientifici* que o próprio decreto do Vêneto cita
para definir as janelas de tratamento.

Artefato: `data/samples/IT-CIENCIA/IT-CIENCIA-UNIVERSO-V1.json`

### 6.2 ⭐ O campo italiano de agora — 95 dias mais fresco

O acervo de campo parava em **15/05/2026**. O Consorzio Fitosanitario di Modena publica
semanalmente e está em **n.27 de 18/08/2026**, com notícias de setembro.

**Dois sinais correntes, com mecânica técnica declarada:**

**Cocciniglie farinose na vite — em aumento.** A fonte explica por quê: gerações
exponenciais (300-400 descendentes por fêmea), esgotamento do efeito dos inseticidas
anteriores, cobertura cerosa, e o inseto se enfiando no cacho onde o produto não chega —
*"anche le molecole dotate di sistemia non riescono a traslocare su un frutto che sta
maturando"*. E dias ensolarados mais medo de granizo freiam a desfolha que descobriria os
cachos.

⚠️ **Convergência real, mas de TEMA e não de janela:** a Emilia-Romagna deu deroga art.51
para **EFFICON** (dimpropyridaz) contra *Planococcus ficus*, válida de 01/03 a **28/06/2026**
— já fechada quando o aumento aparece. E **EFFICON tem 12 anúncios Meta que alcançaram a
Itália** no dataset congelado. Dizer que os três se alinham na janela inverteria o
calendário.

**Mosca delle olive — aumento de capturas** em todo o comprensório olivícola, "in linea con
quanto rilevato in Emilia-Romagna". ⛔ Captura em armadilha **não é dano no fruto**.

Artefato: `data/samples/IT-CAMPO-ATUAL/IT-SINAIS-CAMPO-SETEMBRO-2026.json`

### 6.3 ⭐ O GIRE abriu — era porta errada, não fonte morta

`https://gire.ipsp.cnr.it` recusa: certificado expirado. **`http://gire.mlib.cnr.it` abre** —
mesmo conteúdo, host espelho.

```
FONTE INALCANÇÁVEL POR UMA PORTA NÃO É FONTE INALCANÇÁVEL.
```

O que estava atrás dela: **22 espécies com resistência a herbicida CONFIRMADA na Itália**,
cada uma com ficha e, para muitas, mapa nacional por cultura e mecanismo.

| Espécie | Cultura do mapa | Mecanismo |
|---|---|---|
| *Lolium* spp. | frumento · medica · **arbóreas** | ACCasi · ALS · **EPSP** |
| *Avena sterilis* | frumento | ACCasi · ALS |
| *Echinochloa crus-galli* | mais · **riso** | ALS · **ACCasi + ALS + propanile** |
| *Conyza canadensis* | **arbóreas** | **EPSP** |
| *Papaver rhoeas* | frumento | ALS · 2,4-D |
| *Oryza sativa* (riso crodo) | riso | ALS |
| *Amaranthus retroflexus* | dicot. estive | ALS |
| *Sorghum halepense* | dicot. estive | ACCasi |
| *Cyperus difformis* · *Schoenoplectus* · *Alisma* | riso | ALS |
| *Phalaris paradoxa* · *Sinapis arvensis* | frumento | ACCasi · ALS |

E a declaração mais recente, de **junho de 2025**:

> *"Il GIRE conferma la presenza di popolazioni di **riso crodo** e di **giavoni resistenti
> a tutti gli inibitori dell'ACCasi** utilizzati in riso."* — Il Risicoltore LXVII (6)

Artefato: `data/samples/IT-CIENCIA/IT-GIRE-RESISTENCIA-V1.json`

### 6.4 ⭐ E o cruzamento que merece um humano abrir

O evento **da própria ADAMA** em Fossano (CN), 26/05/2026, apresentou o **Edaptis®** —
descrito no site como *"graminicida de pós-emergência de amplo espectro para cereais…
**gestão das resistências** graças à combinação de **dois mecanismos de ação diferentes**"*.

No registro do Ministero, `EDAPTIS` = **mesosulfuron-methyl (ALS) + pinoxaden (ACCase)** +
mefenpyr-diethyl (protetor).

O GIRE lista *Lolium* spp. e *Avena sterilis* em frumento como resistentes a **ACCasi E ALS**.

⚠️ **Como isto NÃO pode ser lido:** mistura de dois mecanismos é estratégia antirresistência
padrão e legítima; resistência confirmada em algum lugar **não** é resistência em todo lugar;
e nada aqui mede eficácia de produto nenhum. `FALHA DE CONTROLE` continua **sem dono**.

✅ **Como isto PODE ser lido:** *«a autoridade nacional publica resistência confirmada aos
dois mecanismos que o produto combina, nas duas espécies que o produto tem como alvo
principal em cereal»*. Isso é contexto para um técnico da ADAMA abrir — que é exatamente a
decisão que esta régua serve.

Mesmo cruzamento, mesma cautela, em mais três casos:

| Espécie e mecanismo resistente | Onde toca o portfólio ADAMA IT |
|---|---|
| *Conyza canadensis* — EPSP em arbóreas | 11 registros com glifosato; TAIFUN MK CL posicionado para frutícolas, vite e olivo |
| *Echinochloa* — ALS em arroz | FullPage e Max-Ace são baseados em imazamox, que é ALS |
| *Amaranthus* — ALS | BIFENOX (7 registros: SONAVIO, VALLEY, FOX, FOXPRO, BIFENIX, ANTARKTIS) é HRAC 14/E — **mecanismo diferente** do que tem resistência confirmada |

### 6.5 A flavescência agora tem 5 regiões, não 2

O acervo tinha Lombardia e Vêneto. As rotas gratuitas acrescentaram, cada uma com seu ato:

| Região | Ato | Data |
|---|---|---|
| Lombardia | Comunicato Giunta n. 39 | 25/05/2026 |
| Vêneto | DDR n. 13645 | 14/05/2026 |
| ⭐ Piemonte | Determinazione Dirigenziale n. 280 | 16/03/2026 |
| ⭐ Trentino | Bollettino speciale Flavescenza n. 1 | 29/05/2026 |
| ⭐ Emilia-Romagna | Determinazione 9818/2026 | 2026 |

⚠️ Os três novos estão `CITADO_EM_FONTE_SECUNDARIA` — os atos não foram abertos. Isso é
estado, não prova.

---

## 7 · ⭐ A camada que não existia: aprovação europeia da substância ativa

Todo o regulatório italiano do acervo é de **registro nacional do produto** — `EXPIRY`
2027, 2034, 2040. Mas **nenhum registro nacional sobrevive à aprovação europeia da
substância** que ele contém. São duas camadas, e o acervo só tinha uma.

Rota: CELLAR / SPARQL do Publications Office, **pública, sem chave** — a mesma que
`EU-T4-001` já tinha provado. 89 atos de 2024–2026 cruzados contra as **53 substâncias
ativas** do registro ADAMA Itália.

**31 das 53 têm ato europeu na janela.** Duas delas são de **junho e julho de 2026**.

### 7.1 O que isso muda no caso principal

O acervo dizia, sobre os 6 produtos ADAMA que nomeiam *Scaphoideus titanus* no rótulo
(KLARTAN 20 EW, KLARTAN SMART, TAU AL 240 EW, MAVRIK EW, MAVRIK SMART, EVURE PRO):

> *"EXPIRY 2027-01-31. EXPIRY ≠ WITHDRAWAL: re-registro é rotina e RENEWAL_STATUS = NÃO SEI."*

**A aprovação europeia do tau-fluvalinate expira na MESMA data: 31 de janeiro de 2027.**

Li o ato inteiro — Reg. (EU) 2024/1206, de 29/04/2024:

- tau-fluvalinate está na **Parte A** do Anexo do Reg. 540/2011 (substância antiga, da
  Diretiva 91/414)
- a aprovação **já tinha sido estendida** antes, até 31/08/2024, pelo Reg. 2020/2007
- o pedido e o dossiê de renovação foram apresentados
- e o ato registra, literalmente: *"the risk assessment pursuant to Article 11 of
  Implementing Regulation (EU) No 844/2012 **has not yet been finalised** by the respective
  rapporteur Member States"* — com tau-fluvalinate nomeado nessa lista
- Anexo, linha 328: nova data **31 January 2027**

**Checagem de ato mais novo:** consulta SPARQL dirigida a todos os atos cujo título contém
"fluvalinate", **sem filtro de ano** — 10 atos, e o mais recente é este, de abril de 2024.
Nenhuma renovação, não-renovação ou nova extensão até 02/09/2026.

**A ressalva do acervo muda de sentido.** *"Re-registro é rotina"* vale para registro
nacional sob aprovação europeia estável. Aqui a data nacional **é** a fronteira europeia, e
a decisão europeia está aberta com avaliação de risco não finalizada.

⛔ **Proibido dizer:** "o produto vai sair do mercado" · "a ADAMA vai perder o registro" ·
"a substância será proibida" · "há risco de desabastecimento".

✅ **Permitido dizer:** *"a aprovação europeia do tau-fluvalinate expira em 31/01/2027, foi
estendida por ato de 2024 que registra avaliação de risco não finalizada, e nenhum ato
posterior nomeando a substância foi publicado até 02/09/2026."*

O mesmo vale, com a mesma data, para o **bupirimate** — 5 produtos ADAMA na Itália, entre
eles o NIMROD.

⚠️ **Limite do método:** o casamento é sobre o **título** do ato. Ato que decida sobre a
substância sem nomeá-la no título não seria achado; conclusão da EFSA e voto de comitê não
são atos e não estão no EUR-Lex. As outras 30 substâncias saem como `ACT_FOUND_NOT_READ` —
título casado **não é** ato lido.

Artefato: `data/samples/IT-REGUA/IT-ADAMA-EU-ACTIVE-SUBSTANCE-V1.json`

---

## 8 · O que continua NÃO SEI

```
⛔ NÍVEL 2                uma janela só; sem série não há proporção
⛔ LOCAL DO FATO          145 de 603 vídeos nomeiam lugar; comentário quase nunca
⛔ TEMPO DO FATO          comentário devolve tempo RELATIVO, não data
⛔ FALHA DE CONTROLE      não há dono, e não se cria detector nesta fase
⛔ RESISTÊNCIA            proibido declarar sem base oficial
⛔ SEVERIDADE             nenhum dono mede intensidade
⛔ QUEM FALA no comentário  pseudonimizado
⛔ RECALL DOS ALVOS       ⭐ a lista italiana é NOVA e nunca foi medida contra o que o
                          acervo realmente nomeia. Recall baixo provaria que ESTA lista
                          não alcança — não que a Itália não fala do assunto
🚪 SEM PORTA              instagram · facebook orgânico · x · tiktok · podcast · linkedin
                          PORTA AUSENTE NÃO É RENDEU ZERO
```
