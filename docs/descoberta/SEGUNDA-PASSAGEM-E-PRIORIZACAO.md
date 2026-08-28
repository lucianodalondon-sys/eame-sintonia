# SEGUNDA PASSAGEM E PRIORIZAÇÃO — MISSÃO EAME 02

Feita depois de percorrer T1–T12 nos quatro recortes, conforme §21 e §22 da missão.
Não é resumo: é releitura do que foi medido, para decidir onde aprofundar.

**Data:** 2026-08-28

---

## A · Quais famílias ficaram pobres

| Território | Situação | Motivo medido |
|---|---|---|
| **T8 · FARMERS & INFLUENCERS** | **a mais pobre** | Todas as APIs exigem credencial (YouTube 403, Meta 400, TikTok 404). O RSS do YouTube funciona sem chave, mas exige o `channel_id` — o gargalo é **descoberta**, não coleta. FIELD, TECHNICAL e COMMERCIAL AUTHORITY ficaram **sem nenhuma fonte identificada**. |
| **T9 · camada de comunicação** | pobre | 403/502/404 nos três sites testados. Superar exigiria varredura proibida pela §16. |
| **T11 · EVENTS** | pobre em formato | Informação real e verificável, mas sem API nem formato estruturado. Manutenção alta, valor relativo baixo. |
| **T7 · TECHNICAL NETWORK** | pouco investigado | Só alcançado indiretamente, pelas instituições que aparecem em T5 e T3. Não teve investigação própria. **É a maior lacuna de esforço, não de dado.** |

## B · Quais fontes se mostraram extraordinariamente ricas

1. **ES-T3-001 · RAIF Andalucía** — a mais rica da missão. Incidência **medida em percentual**,
   por **parcela com coordenadas**, semanal, 2006–2026, 10 culturas, CC BY 4.0.
   Nenhuma outra fonte chega perto dessa granularidade.
2. **FR-T4-001 · ANSES E-Phy** — 15.140 produtos e 18.558 usos autorizados com **cultura × alvo**,
   dose, BBCH e ZNT. É a única fonte que liga empresa, produto, cultura e problema num só lugar.
3. **EU-T4-001 · CELLAR** — documento primário, identificável, datado, em 24 línguas.
   E serviu **duas famílias** (T4 e T12) com o mesmo conector.
4. **EU-T5-001 · OpenAlex** — responde perguntas de pessoas que nenhuma outra fonte responde.

## C · Quais culturas aparecem repetidamente

| Cultura | Camadas em que aparece |
|---|---|
| **Trigo** (TRZAX) | T1 (área NUTS 2 e rendimento), T2 (clima), T4 (registro), T5 (pesquisa), T10 (preço) — **5 camadas** |
| **Vid** (VITVI) | T3 (RAIF, medição), T4 (registro FR), T5 (pesquisadores IT), T2 (clima) — **4 camadas** |
| Cevada, milho, beterraba | T1, T4, T10 |

## D · Quais regiões têm dados particularmente bons

- **Andaluzia (ES)** — a única com medição fitossanitária por parcela. Huelva, Córdoba e Cádiz
  têm série semanal de doença.
- **Castilla y León (ES41)** — maior área de trigo dos três países (771,8 mil ha) com clima
  e rendimento nacional associados.
- **Cinturão do trigo francês** — FRB0, FRE2, FRF2, FRI3, com área NUTS 2 desde 2000.

## E · Quais problemas agronômicos aparecem em múltiplas camadas

**O míldio da videira (*Plasmopara viticola*, EPPO PLASVI) é o problema que atravessa mais
camadas de toda a missão** — e por isso virou a fatia vertical aprofundada nesta passagem:

| Camada | O que se sabe hoje sobre PLASVI |
|---|---|
| **T3 · medição** | Andaluzia 2026: Huelva **26,4%**, Córdoba 6,4%, Cádiz ≈0% de cepas afetadas |
| **T4 · registro FR** | **168 usos autorizados** em Vigne × Mildiou(s). ADAMA é a **empresa nomeada com mais usos: 17**, à frente de Nufarm (11), Ascenza (10), Bayer (8), UPL (7), Syngenta (5), Corteva (3), BASF (2) |
| **T4 · portfólio ADAMA** | 6 produtos nesse combate: FOLPAN 80 WDG, FOLPAN SC, EPYLOG FLASH, EXTASE GOLD, LASVEGAS, **PANDERO GOLD** |
| **T4 · UE** | PANDERO GOLD depende de metalaxil-M, substância tratada pelo CELEX 32026R1353 (15/06/2026) — ver CASE-001 |
| **T5 · ciência** | Itália: Toffolatti (17 trabalhos, Milano), Perazzolli (12, Edmund Mach), Maddalena (11), Rossi (10, Cattolica) |
| **T2 · clima** | medível por província e por janela — mas **não explica** a diferença observada (CASE-008) |

**Substâncias mais registradas contra míldio da videira na França:** fosfonatos de potássio (37),
**folpet (33 + 14 grafados "folpel" = 47)**, fosetil de alumínio (23), cobre (16), cimoxanil (11).

> **Achado de qualidade de dado:** o mesmo registro francês grafa a mesma substância como
> **"folpet"** e **"folpel"**. Quem contar sem normalizar subestima a molécula em 30%.
> É exatamente o tipo de erro silencioso que uma tela bonita esconde.

## F · Quais pessoas aparecem repetidamente

- **Christophe Délye** (INRAE Agroécologie) — 9 trabalhos em resistência a herbicidas na França,
  com mais três coautores do mesmo laboratório. Um único laboratório domina o tema no país.
- **Silvia Laura Toffolatti** (Università di Milano) — 17 trabalhos em míldio da videira na Itália.
- **Michele Perazzolli** (Fondazione Edmund Mach) — 12 trabalhos, **e** a instituição publica os
  boletins técnicos do Trentino. Único elo medido entre T5 e T3/T7.

## G · Quais cruzamentos estão perto de fechar

| Cruzamento | Falta o quê | Esforço |
|---|---|---|
| **X-006** (UE → nacional) | segunda chave: nome normalizado da substância, além do CAS. Hoje cobre 3 de 6 atos e 621 de 1.338 substâncias. | baixo |
| **X-007** (FR ↔ EPPO) | dicionário FR(cultura,alvo) → EPPO, **com taxa de acerto medida**. O lado espanhol já está pronto. | médio |
| **X-011** (evento × empresa × pessoa) | casar nome de empresa entre catálogo e registro. Chave suja. | médio, valor baixo |

## H · Quais ferramentas ganharam evidência suficiente

Ver a classificação em TIERS abaixo.

---

# PRIORIZAÇÃO (§22)

## TIER A · DEMONSTRÁVEL AGORA
*Dados reais + evidência preservada + exemplo real. Poderia ir a uma tela amanhã.*

| Ferramenta / capacidade | Evidência |
|---|---|
| **PEST & DISEASE RADAR** (Andaluzia) | CASE-007 · CAP-014/015/016 |
| **REGULATORY WATCH** (UE → França) | CASE-001/002 · CAP-001/006 |
| **COMPETITIVE RADAR** — camada regulatória | X-005 · fatia PLASVI |
| **REGISTRATION EXPIRY RADAR** (Itália) | CASE-003 · CAP-007 |
| **UNMET NEED RADAR** (Espanha) | CASE-004 · CAP-009 |
| **CROP PULSE** (área NUTS 2, 25 anos) | CAP-010/011 |
| **EXPERT NETWORK / SCIENCE RADAR** | CASE-009/010 · CAP-017/018 |
| **CLIMATE EXPOSURE** (não "impact") | CASE-005/006 · CAP-012/013 |
| Vigilância da **política agrícola comum** | CAP-020 |
| Preço semanal de cereal por praça | CAP-019 |

## TIER B · CONSTRUÍVEL
*Os dados existem; a integração não está completa.*

- **PORTFOLIO OPPORTUNITY** — a base está provada; a varredura de lacunas não foi rodada.
- **EPPO NORMALIZER** — dicionário pronto do lado espanhol, mapeamento francês por construir (X-007).
- **COUNTRY PULSE** — todas as fontes provadas, falta a montagem e a declaração de granularidades.
- **X-006 em escala** — falta a segunda chave de substância.

## TIER C · PLAUSÍVEL
*Há indício suficiente para pesquisar mais.*

- **PEST & DISEASE RADAR fora da Andaluzia** — França e Itália têm boletins reais, em PDF.
- **EVENT RADAR** — informação real, formato ruim (X-011).
- **T7 · rede técnica** — pouco investigada, não bloqueada. Provável ganho rápido.

## TIER D · CONCEPT ONLY
*Ainda não demonstrado. Não pode aparecer como capacidade pronta.*

- **FIELD VOICES / influenciadores** — nenhuma fonte obtida (P-009).
- **COMPETITIVE RADAR — camada de comunicação** — X-003 NÃO COMPÕE.
- **Visão EAME unificada de registro** — X-008 NÃO COMPÕE; as três fontes nacionais não cobrem os mesmos campos.
- **Qualquer leitura causal de clima sobre doença** — X-009 NÃO COMPÕE. Ver CASE-008.
