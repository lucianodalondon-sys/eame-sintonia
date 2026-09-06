# Plano de substituição: do slot vazio ao objeto real

> **LEITOR — este documento fala dos 90 pares, que NÃO são o leitor canônico da casa.**
> O leitor canônico é `IT-ROTULOS-PARES-V3` (`data/samples/IT-ROTULOS-V1/`), de 2026-09-04:
> `it_rotulo_parser/3.4.0`, portão `IT-ROTULOS-PORTAO-V1 = PASS` contra gabarito de 30
> rótulos lido à mão, **128 rótulos com par** contra os 19 daqui. Os 90 pares de 2026-08-30
> ficam como `LEGACY_READER / HISTORICAL_INPUT`, `CANONICAL_AUTHORITY = NO`.
> `OLDER_SMALLER_READER != CANONICAL_READER`.


**Data:** 2026-09-01
**Nada foi editado no portal.** Este é o plano, não a execução.

---

## 0 · A primeira correção é do diagnóstico, não do portal

A missão pedia para achar "fixtures falsas" e trocá-las por conteúdo real. **Elas quase não existem.**

Lendo o casco (`data/samples/CASCO-EAME/screens/*.txt`, baseline V7), o que há é o oposto de dado falso:
são **slots que declaram a própria vacuidade**, com estas frases já escritas na tela:

- *"Slot preparado — item entra quando a data oficial e o registro afetado estiverem no freeze."*
- *"Nenhum caso conectado nesta versão. Os cartões abaixo são **slots estruturais** — servem para validar
  filtros, estados e navegação, não para leitura de conteúdo."*
- *"Série de sinal — sem dado conectado"*
- *"Ausência de dado não é ausência do fenômeno."*
- *"Bloqueio de acesso não é evidência de ausência."*
- Contadores da watchlist mostrando literalmente **"—"**

Ou seja: **o problema do demo não é mentira, é vazio.** E o vazio está honestamente rotulado. Isso muda o
trabalho: não é "substituir", é **conectar**.

⚠️ Duas coisas o casco tem que precisam mudar de verdade:

1. Está fixado em **"Country Portal · Espanha"** em pelo menos duas telas (`home`, `casos`).
   Para a Itália, isso é troca de país, não de conteúdo.
2. O casco **está fora do Git** (memória do projeto: quem procura o portal no repositório acha o protótipo
   congelado, que é outra coisa) e o `index` pede ~20 arquivos que só existem no zip. Antes de conectar
   dado, é preciso saber em qual artefato se está mexendo.

---

## 1 · Tela por tela: o que entra, de onde vem

### 1.1 Home — "O que merece atenção agora"

| Slot atual | Objeto real que entra | Fonte |
|---|---|---|
| `REGULATORY DEADLINE` · Agir agora (0–30 dias) | **8 registros já vencidos + 7 vencendo em 7 dias** (de 163), com número e data | `IT-T4-001` |
| `INVESTIGATE` · Verificar agora | **os 7 registros citados no site fora do registro medido** (`CLAIM_OUTSIDE_MEASURED_REGISTRY`) — discrepância aberta, com o *n* declarado | censo do catálogo |
| `GEOGRAPHIC PRIORITY` · Preparar (30–90) | **monitoramento de flavescência aberto até fim de setembro**, ordenado por área de vite (Veneto 17,2% · Lombardia 3,1%) | Bollettino Veneto n.19 + ISTAT |
| `ACTIVATION QUESTION` · Planejar (90–180) | **semeadura de cereais de outono (set–nov)** e a pergunta do herbicida: *Lolium*/*Avena* resistentes, intervenção única entre accestimento e levata | site ADAMA + GIRE |
| `CHANGE DETECTED` · Ciclo longo | **extensão art. 51 do SONAVIO® a sedano e finocchio** — mudança real posterior ao nosso freeze | site ADAMA, lido 01/09/2026 |
| `Estado da fundação` | 8 de 20 regiões com fonte medida · 163/163 rótulos parseados · Meta congelada em 31/08/2026 · Supabase `NOT_ACCESSIBLE` | este inventário |

### 1.2 Radar do Futuro

| Slot atual | Objeto real |
|---|---|
| `DISEASE CONTROL` — "sem dado conectado" | **FR-1**: piretroides de eficácia inferior indo à mesa técnica nacional (Emilia-Romagna, 26/02/2026) |
| `WEED CONTROL` — "sem dado conectado" | **FR-4**: *Amaranthus tuberculatus* e *A. palmeri* ALS-resistentes no norte; e as infestantes de nova difusão ligadas ao corte de terbutilazina |
| `PEST CONTROL` — "sem dado conectado" | **FR-2/FR-3**: Nebbiolo manifestando flavescência; obrigação estendida a hobbistas e vinhedos abandonados |
| `CROP ENHANCEMENT` — "sem dado conectado" | ⚠️ **manter vazio.** Não temos sinal italiano de bioestímulo/nutrição. Budge® e Exelgrow® são registros de outra natureza, não fitossanitários |
| Contadores "—" | temas em watchlist **8** · sinais científicos **763 materiais / 88 com fato na Itália** · observações de campo **7 boletins** — todos com denominador ao lado |

### 1.3 Radar / Casos de convergência

Os 5 candidatos de `ITALY-OPPORTUNITY-CANDIDATES-REAL.md` entram como cards, **com o rótulo do próprio
acervo**: `REGIONAL CONVERGENCE WORTH INVESTIGATING`, nunca "opportunity".

Mapeamento direto para os estados que a tela já tem:

| Caso | Linha ADAMA | Estado | Janela |
|---|---|---|---|
| OC-1 Vite × flavescência | Pest Control | **Caso confirmado** | Encerrada (aplicação) + Aberta (monitoramento) |
| OC-2 Soja/milho × Amaranthus ALS | **Weed Control** | **Parcial** — perna GIRE não lida na fonte | Próximo ciclo |
| OC-3 Cereais × Lolium/Avena | **Weed Control** | Em observação | Aberta (semeadura) |
| OC-4 Milho × micotoxina | Disease Control | Em formação | Aberta (colheita) |
| OC-5 Vencimentos do portfólio | transversal | **Caso confirmado** | Aberta |

Note que **dois dos cinco são Weed Control**. É a correção do desequilíbrio, e ela vem do dado.

### 1.4 Acervo

O casco tem "tudo o que foi coletado, com proveniência e data". Objetos reais disponíveis, sem duplicar:

- **414 anúncios Meta** (texto, mídia, data, link, país alcançado)
- **147 vídeos + 265 comentários + 5 transcrições** italianos
- **163 registros + 163 rótulos** com link do PDF do Ministero
- **51 páginas de produto + 141 documentos** do catálogo
- **7 boletins** em texto integral
- **763 materiais científicos**, 88 com fato na Itália

### 1.5 Fontes

Estado por fonte, já medido: **16 GREEN, 3 BLOCKED, 1 NOT_REACHED** entre as 20 sondadas. Acrescentar as
falhas de hoje, que são informação e não vergonha:

| Fonte | Estado hoje |
|---|---|
| `regione.veneto.it` | **BLOQUEIO POR IP** — a página ecoa o IP de saída |
| `gire.ipsp.cnr.it` | **certificado expirado** |
| `adama.com/.../crop-protection?f[0]=…` | **WAF** (`bm-verify`) mesmo com janela gráfica |
| `agricoltura.regione.emilia-romagna.it/fitosanitario/bollettini` | 404 no caminho tentado |
| `difesafitosanitaria.ersa.fvg.it/.../bollettini` | 404 nos dois caminhos tentados |

### 1.6 Calendário agronômico

Entram as janelas de `ITALY-CROP-WINDOWS-REAL-EVIDENCE.md`, **com as cinco camadas separadas**
(esperada · observada · relatada por pessoa · de rótulo · obrigatória). A tela precisa de cinco trilhas
distintas, não de uma barra só.

---

## 2 · O que continua precisando ser simulado

| Camada | Por quê | O que exibir no lugar |
|---|---|---|
| Notificação, workflow, mensagem de Field Sales, geração de Action Brief | é a camada operacional; ninguém tem esse dado | simular à vontade — **é o ambiente, não o mundo** |
| Estoque, venda, pedido, margem, share, prontidão comercial | **exige dado interno da ADAMA, que este projeto não terá** | nunca simular. Deixar o campo como `NÃO SEI` visível |
| Instagram italiano · Facebook orgânico · X/Twitter · TikTok · podcast | não existem, em nenhuma branch | **não colocar o ícone na tela** |
| Sensor humano no LinkedIn Itália | medido e reprovado: `HUMAN_SENSOR_ADDS_NOTHING_IN_THIS_PANEL` | mostrar como **capacidade testada e negativa** — é mais forte que fingir |
| `CROP ENHANCEMENT` no radar | sem sinal italiano | manter "sem dado conectado" |
| Janela de aplicação lida no rótulo | a coluna de época não foi extraída dos 163 PDFs | usar a janela do site (`MANUFACTURER_CLAIM`) e rotular assim |

---

## 3 · Ordem de trabalho sugerida

1. **Decidir qual artefato é o portal** e trazê-lo para um lugar versionado. Sem isso, tudo abaixo é
   trabalho perdido.
2. **Trocar o país** de Espanha para Itália nas telas fixadas.
3. **Commitar o `SENSOR-PILOT` e o CSV do Ministero.** Hoje o melhor material humano italiano e a base
   regulatória inteira existem só nesta pasta local. É o risco mais barato de eliminar.
4. **Conectar a camada regulatória** (163 produtos, 90 pares, calendário de vencimentos). É a mais sólida
   e a que menos exige julgamento.
5. **Conectar os 414 anúncios Meta**, com a lei `alcançou ≠ foi dirigido` visível na tela.
6. **Conectar os 5 candidatos** com o rótulo correto.
7. **Reouvir o vídeo do convegno** antes de qualquer citação em italiano.
8. **Abrir a linha-guia GIRE na fonte** antes de publicar o caso OC-2.

---

## 4 · Frase que resume o plano

O demo não precisa parecer cheio. Precisa que **cada coisa cheia seja verdadeira e cada coisa vazia diga
por que está vazia** — que é, aliás, exatamente o que o casco já faz.
