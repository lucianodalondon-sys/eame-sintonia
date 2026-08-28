# SOURCE PACKS — SINTONIA EAME

A apresentação promete *"configured public sources, by market and language. No private
conversations."* (DECK-017). Este documento mede o que existe, por camada e por mercado.

**Estados:** `STRONG` · `USABLE` · `WEAK` · `EMPTY` · `BLOCKED`
**Data:** 2026-08-28 · fichas completas em `../fontes/ATLAS-DE-FONTES-EAME.md`

---

## MAPA GERAL

| Pack | FRANCE | SPAIN | ITALY | EUROPE |
|---|---|---|---|---|
| **REGULATION** | **STRONG** | USABLE | **STRONG** | **STRONG** |
| **MOLECULE** | **STRONG** | WEAK | **STRONG** | **STRONG** |
| **SCIENCE** | **STRONG** | **STRONG** | **STRONG** | **STRONG** |
| **WEATHER** | **STRONG** | **STRONG** | **STRONG** | **STRONG** |
| **MARKET** | USABLE | USABLE | USABLE | USABLE |
| **FIELD / TECHNICAL** | WEAK | **STRONG** | WEAK | EMPTY |
| **COMPETITOR** | USABLE (só registro) | WEAK | USABLE (só registro) | EMPTY |
| **DISTRIBUTION** | **USABLE** | EMPTY | EMPTY | EMPTY |
| **ADAMA CONTEXT** | USABLE | USABLE | USABLE | USABLE |

**Dois packs continuam vazios ou fracos em todos os mercados: FIELD (fora da Andaluzia) e
COMPETITOR (comunicação).** São exatamente os que sustentam os claims não provados do deck.
**DISTRIBUTION saiu de EMPTY** na MISSÃO 03: a França tem fonte aberta e boa; Espanha e
Itália continuam sem investigação.

---

## PACK · REGULATION — `STRONG`

| País | Fonte | Acesso | Idioma | Frequência | Histórico | Automação | Licença | Evidência |
|---|---|---|---|---|---|---|---|---|
| EU | EU-T4-001 CELLAR | SPARQL + content negotiation | 24 línguas | contínua | acervo CELEX | ALTA | pública | XHTML integral |
| FR | FR-T4-001 E-Phy | CSV/XML via API data.gouv | FR | **semanal** | estado + datas | ALTA | Licence Ouverte | CSV oficial |
| IT | IT-T4-001 Min. Salute | CSV datado | IT | arquivo datado | desde 1970 | MÉDIA-ALTA | CC BY 4.0 | CSV oficial |
| ES | ES-T4-001 vocabulário · ES-T4-002 excepcionais | XLSX / XLS | ES | não declarada | vigentes | ALTA / MÉDIA | pública | XLSX oficial |
| ES | ES-T4-003 registro de produtos | **só consulta web** | ES | — | — | **NÃO SEI** | — | nenhuma |

**Fortes:** 4 fontes com evidência preservável. **Buraco:** o registro espanhol de produtos.

## PACK · MOLECULE — `STRONG` no que é substância, `EMPTY` no que é origem

| Dimensão | Estado | Fonte |
|---|---|---|
| substância ativa (nome, CAS) | **STRONG** | FR-T4-001, IT-T4-001, EU-T4-001 |
| normalização de substância | **STRONG** — 82% do uso (X-006) | derivado |
| titular do registro | **STRONG** | registros nacionais |
| **manufacturer da substância ativa** | **EMPTY** | — |
| **manufacturer do formulado** | **EMPTY** | — |
| **fonte / origem autorizada** | **EMPTY** | — |
| país de fabricação / de origem | **EMPTY** | — |

> **Lei registrada:** `titulaire` (FR) e `ragione_sociale` (IT) são **titular de registro**,
> não fabricante. Tratar como sinônimos seria erro factual.

## PACK · SCIENCE — `STRONG`
EU-T5-001 OpenAlex: REST sem chave, autoria + afiliação + país + DOI + ano, décadas de
histórico, cobertura dos três países. **Limite estrutural:** `authorships.countries` é
**afiliação**, não local do experimento — SOURCE_LOCATION ≠ FACT_LOCATION.
**Atenção GDPR:** são pessoas identificadas (P-008).

## PACK · WEATHER — `STRONG`
EU-T2-001 NASA POWER (diário, sem chave, sem cota observada) + EU-T2-002 GISCO (pontos
NUTS 2). **Limite:** o valor é de **um ponto**, não média regional — aproximação declarada.
EU-T2-003 Open-Meteo ficou `BLOCKED` neste ambiente (cota por IP).

## PACK · MARKET — `USABLE`

| Variável | Estado | Fonte |
|---|---|---|
| área de cultura por NUTS 2 | **STRONG** (25 anos) | EU-T1-001 |
| rendimento por país | **STRONG** | EU-T1-002 |
| rendimento por região | **EMPTY** — medido, não existe | — |
| preço de cereal por praça | **STRONG** (semanal, 39 praças) | EU-T10-001 |
| importação / exportação | **BLOCKED / WEAK** | FAOSTAT 401; Eurostat mal consultado |
| eventos de mercado | **EMPTY** | — |
| presença competitiva | **STRONG** via registro | X-005 |

## PACK · FIELD / TECHNICAL — `STRONG` só na Andaluzia

| País | Fonte | Estado | O que entrega |
|---|---|---|---|
| ES | ES-T3-001 RAIF | **STRONG** | incidência **em %**, por **parcela**, semanal, 2006–2026, 10 culturas |
| FR | FR-T3-001 BSV | **WEAK** | texto de especialista, semanal, regional — **PDF descentralizado, sem API** |
| IT | IT-T3-001 bollettini | **WEAK** | idem, e verificado em **1 de 20 regiões** |
| EU | — | **EMPTY** | — |

> A assimetria é estrutural: a Andaluzia publica **número**, a França e a Itália publicam
> **julgamento**. Não são comparáveis, e nenhuma tela pode sugerir que sejam.

## PACK · COMPETITOR — `USABLE` no registro, `WEAK/EMPTY` na comunicação

| Dimensão | Estado | Motivo medido |
|---|---|---|
| presença regulatória por cultura × alvo | **USABLE→STRONG** (FR, IT) | X-005 COMPROVADO |
| comunicação institucional | **BLOCKED** | syngenta.fr 403 · basf 502 · corteva.it 404 |
| patentes e marcas | **EMPTY — não investigado** | — |
| atividade técnica e eventos | **WEAK** | EIMA e Vinitech alcançáveis; sem formato estruturado |
| anúncios, campanhas, claims | **EMPTY — não investigado** | — |
| atenção do campo | **EMPTY** | dimensão distinta de comunicação da empresa |

## PACK · DISTRIBUTION — `USABLE` na França, `EMPTY` na Espanha e na Itália

| País | Fonte | Estado | O que entrega |
|---|---|---|---|
| FR | FR-T13-001 base SIRENE aberta | **USABLE** | **4.646** empresas em atacado de grãos e **4.251** em atacado de produtos químicos, com comuna, faixa de efetivo e SIREN. As grandes cooperativas aparecem nominalmente: OCEALIA, SOUFFLET, VIVESCIA, AXEREAL, NATUP, ARTERRIS, OXYANE, CAVAC |
| ES | — | **EMPTY** | não investigado |
| IT | — | **EMPTY** | não investigado |

> Dá **a rede**, não o **fluxo**. Volume, catálogo, mudanças de catálogo e acordos
> continuam sem fonte. Afirmar volume a partir daqui seria inventar.

## PACK · ADAMA CONTEXT — `USABLE`
Registro oficial (presença registrada, os três países) + imprensa agrícola 2025–2026
(sinal público). `adama.com` devolveu **403** em duas rotas de saída distintas.
**INTERNAL PRIORITY continua NÃO SEI.** Ver `../adama/RADAR-ADAMA-EAME.md`.
