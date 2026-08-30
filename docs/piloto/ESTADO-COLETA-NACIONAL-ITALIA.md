# ESTADO DA COLETA NACIONAL — ITÁLIA

`COUNTRY = IT` · **2026-08-30** · branch `claude/sintonia-italy-pilot-b1l401`

> Resposta honesta às seis perguntas de prontidão. Uma camada só está `READY` quando o
> **universo** foi construído, o critério de seleção é escrito, e a primeira amostra foi
> **validada** — não quando ela tem itens dentro.

---

## PRONTIDÃO

| | Estado | Por quê |
|---|---|---|
| `ITALY_SOURCE_UNIVERSE_READY` | **SIM** | 20 fontes sondadas em 3 dimensões · 16 GREEN · matriz de 8 regiões |
| `ITALY_PRODUCT_INTELLIGENCE_READY` | **SIM (regulatório)** · **NÃO (comercial)** | 163/163 rótulos, 49 usos autorizados, 90 pares cultura×alvo · site 403 |
| `ITALY_RESEARCHER_UNIVERSE_READY` | **PARCIAL** | 1 de 5 recortes construído; os outros 4 estrangulados, não vazios |
| `ITALY_TECHNICAL_NETWORK_READY` | **PARCIAL** | 8 nós institucionais com `ROLE_EVIDENCE`; pessoas individuais não iniciadas |
| `ITALY_CREATOR_UNIVERSE_READY` | **NÃO — e provavelmente não existe** | rota reprovada (6,7 %); a substituta devolveu **zero creators** e uma camada técnica |
| `ITALY_PUBLIC_VOICE_READY` | **NÃO, com método definido** | a voz sobre o issue é **organizacional**, não pessoal — muda o alvo, não o motor |

`ITALY_PILOT_INTELLIGENCE_READY` = **SIM** · `ITALY_DEMO_CONTENT_READY` = **SIM** ·
`READY_TO_DESIGN_ITALY_PORTAL` = **NÃO — e parar antes dele é a instrução**

---

## O QUE ESTA RODADA ACRESCENTOU

**1 · A ligação cultura ↔ alvo, que faltava.** A tabela de doses do rótulo é recuperável
quando se recorta a **tabela** em vez do documento: 49 linhas de uso autorizado, 13 com
dose, **90 pares cultura × alvo**. Isso muda a classe do dado de `CROP_TERM_PRESENT`
(amplo, sem ligação) para `AUTHORIZED_USE_ROW` (estreito, com ligação).

**2 · O verificador teve de ser externo.** Construí-lo dos próprios rótulos falhou: as
duas ordens de captura vazam vernáculo italiano, porque nome comum tem a **mesma forma**
de um binômio. O `eppo-dictionary.json` da Espanha resolveu — e o custo está declarado:
`Scaphoideus` não está nele, então o número é **piso, não teto**.

**3 · O gate de creators reprovou a rota óbvia.** 60 vídeos, 4 canais, **6,7 %** de
relevância; dois canais parados (2015, 11/2025); Edagricole e Agri Italia testam
**tratores**. A rota inversa devolveu, em duas buscas, o Consorzio de Piacenza, a FMach, a
*Giornata del Mais* do CREA e conteúdo técnico de dois concorrentes.

**4 · O bloqueio é da classe.** `adama.com`, `syngenta.it`, `bayer` e `omnitrattore` →
403; `basf` e `corteva` → 200. Não é a ADAMA que nos bloqueia: é a camada de afirmação do
fabricante que é inacessível de datacenter — e isso vale para Espanha e França.

**5 · O trigo duro não tem sinal nenhum.** Primeira cultura da Itália (1.177,4 mil ha) e
**0,0 %** de cobertura de campo nas regiões medidas. Não aparecia porque nenhum caso foi
construído sobre ele.

**6 · O OpenAlex estrangulou o IP inteiro.** Não por volume: por **rajada**. Uma consulta
avulsa passou a devolver 429; 45 s de pausa devolveram 200. O limite é do nosso lado, a
fonte segue GREEN, e consulta dirigida precisa ser **lenta**.

---

## ENTREGA

### A · REPO
`BRANCH` `claude/sintonia-italy-pilot-b1l401` · `TESTS` **329, 0 falhas** · `PUSHED` SIM

### B · SOURCES
`SOURCES_TOTAL` 20 · `GREEN` 16 · `BLOCKED` 3 · `NOT_REACHED` 1 ·
`REGIONS_COVERED` 8 de 20 · `FIELD_SOURCES` 5 regiões + 2 org. de produtores ·
`SCIENCE_SOURCES` OpenAlex · CREA · CNR-ISPA · FMach ·
`VOICE_SOURCES` YouTube RSS (rota aberta, sem alvo validado)

### C · ADAMA REGULATORY
`ACTIVE_REGISTRATIONS` **163** · `OFFICIAL_LABELS` **163/163 (100 %)** ·
`CROP_ISSUE_RELATIONS` **90 pares** · `AUTHORIZED_USE_ROWS` **49** (13 com dose) ·
`MODE_OF_ACTION_RELATIONS` **70** produtos · `APPLICATION_WINDOWS` 2 casos com janela datada

### D · ADAMA COMMERCIAL
`SITE_ACCESS` **BLOCKED (403, WAF de origem, medido 3×)** ·
`CURRENT_CATALOG_TOTAL` **NÃO OBTIDO** · `CATALOG_52_CLAIM` `UNVERIFIED_INPUT` ·
`COMMERCIAL_INTELLIGENCE_STATUS` `NOT_COLLECTED` ·
`LOCAL_BROWSER_HANDOFF_STATUS` **READY_TO_RUN**

### E · RESEARCHERS
`RESEARCHER_UNIVERSE` 25 detalhados · `IDENTITY_CONFIRMED` **25/25 com ORCID** ·
`INSTITUTIONS` 20 · `CROP_ISSUE_REGION_COVERAGE` 1 de 5 recortes ·
`PUBLIC_EXPLANATIONS` 0 — camada seguinte

### F · TECHNICAL NETWORK
`TECHNICAL_PERSONS` 0 · `PUBLIC_SERVICES` **4** regionais + 1 consórcio provincial ·
`REGIONAL_COVERAGE` Vêneto · Lombardia · FVG · Emilia-Romagna ·
`PUBLIC_CONTENT_FOUND` boletins, decretos, *Giornata del Mais* (CREA), portal FMach

### G · FARMERS / CREATORS
`FARMERS` 0 · `FARMER_CREATORS` 0 · `CHANNELS` 4 testados, **0 aceitos** ·
`CONTENT_ITEMS` 60 amostrados · `CREATOR_DISCOVERY_STATUS` **ROUTE_REJECTED (6,7 %)**

### H · COOPERATIVES / MEDIA
`COOPERATIVES` 3 · `PRODUCER_ORGANISATIONS` 1 (Assoproli) · `TECHNICAL_MEDIA` 3 ·
destaque: **Co.Pro.B.** opera DSS de *Cercospora* **citado por boletim oficial**

### I · COMPETITORS
`COMPETITORS_OBSERVED` 4 · `PUBLIC_CLAIMS` 2 conteúdos técnicos **exatamente nos issues
dos casos** (Syngenta: piralide/diabrotica · Bayer: *Scaphoideus*) ·
nada inferido sobre estratégia, vendas ou market share

### J · CASE ENRICHMENT
`VINE_CASE` reforçado — Bayer publica conteúdo técnico no mesmo issue ·
`MAIZE_CASE` reforçado — Syngenta idem, e o CREA faz evento sobre micotoxina ·
`OLIVE_CASE` inalterado · `REGULATORY_CASE` reforçado — 90 pares dão cultura e alvo ao
que vence · `NEW_CASE_CANDIDATES` **trigo duro** (maior cultura, zero sinal)

### K · QUALITY
`IDENTITY_ERRORS` 0 · `ROLE_ERRORS` 0 (todo papel com `ROLE_EVIDENCE`) ·
`GEOGRAPHY_ERRORS` 0 (`FACT_REGION` nunca derivado de afiliação) ·
`READ_FAILURE_AS_ZERO_ERRORS` **0 — e 3 evitados** (Piemonte, bollettini de Piacenza,
recortes estrangulados) · `FOLLOWER_AUTHORITY_ERRORS` 0 (seguidor não é campo) ·
`DUPLICATES` tratadas por chave estrutural

### L · COST
`APIFY_USED` **NÃO** (nenhuma credencial no ambiente) · `APIFY_COST` **US$ 0,00** ·
`OTHER_PAID_COST` **US$ 0,00**

### BLOCKERS
1. `adama.com` e sites do setor → 403 de datacenter. **Handoff residencial pronto.**
2. OpenAlex estrangula rajada → 4 recortes de pesquisador pendentes.
3. Sem credencial Supabase → `STORAGE_PENDING`.
4. Piemonte e Piacenza com bollettini em JS → `NOT_OBTAINED`.
5. Trigo duro sem nenhuma fonte de campo medida.

### O SEGUNDO TESTE DA ROTA DE VOZ — executado, e mudou a pergunta

O `NEXT_SMALLEST_STEP` anterior era rodar a rota substituta **uma vez**, para
`flavescenza dorata`. Foi rodado. Resultado:

```
CREATORS ENCONTRADOS          0
CANAIS DE YOUTUBE             0
```

E o que apareceu no lugar:

- serviços regionais (Piemonte, Campania) e o Serviço Fitossanitário Nacional;
- **técnicos de cooperativa** — `Terre dell'Etruria` publica *bollettini agronomici per
  vite* assinados pelo próprio serviço técnico, com orientação de monitoramento de
  flavescência para Livorno e Grosseto (e a observação de que o fitoplasma **ainda não
  chegou** — sinal de ausência vigiada, que também é sinal);
- **estúdio agronômico privado com autor nomeado** — `Agralia` (Brescia),
  *Massimiliano Perazzoli*, com bollettini agrometeo próprios de viticoltura e olivicoltura;
- conteúdo técnico de empresa (Bayer, SLM Italia);
- imprensa técnica cobrindo **encontro de campo entre as fileiras** (Canelli, Piemonte).

> **A voz pública técnica italiana sobre este problema é ORGANIZACIONAL, não pessoal.**
> Não há camada de creator para coletar; há uma camada de **técnico** dentro de
> cooperativas e estúdios agronômicos. Isso é um achado **sobre o país**, não uma falha de
> coleta — e explica por que buscar "influenciadores agrícolas italianos" devolvia canais
> de trator.

**Consequência de método:** a camada de voz italiana deve ser construída **por
organização com técnico nomeado**, não por perfil social. O motor de voz do Brasil
continua reusável — **muda o alvo, não o método.**

### NEXT_SMALLEST_STEP
**Repetir o teste de voz para um segundo `CROP × ISSUE`** — *piralide/diabrotica em
milho* — e ver se o padrão se confirma. Se a voz também for organizacional ali, a Itália
tem uma regra de país e não uma coincidência de issue, e a camada de voz pode ser
desenhada com alvo certo desde o início: cooperativas com serviço técnico, estúdios
agronômicos e consórcios provinciais — não perfis sociais.

Uma busca decide, de novo. Os cinco `NEXT_SMALLEST_STEP` desta branch foram **executados,
não recomendados**, e cada um mudou uma conclusão: o caso vencedor, a região do caso, o
horizonte de ação, a existência do sinal de milho e agora a natureza da própria camada de
voz.
