# MATRIZ DE PROVA — SINTONIA EAME

**A verdade principal do projeto.** De um lado, o que a apresentação prometeu à ADAMA.
Do outro, o que já está provado com dado real.

**Data:** 2026-08-28 · Claims em `CONTRATO-DE-PROVA-DA-APRESENTACAO.md` ·
Fontes em `../fontes/ATLAS-DE-FONTES-EAME.md`

---

## O PLACAR

| Estado | Claims | Quais |
|---|---|---|
| **PROVED** | **8** | DECK-001, 002, 003, 010, 014, 017*, 024, 025, 030 |
| **PARTIAL** | **13** | DECK-004, 005, 006, 007, 008, 012, 013, 015, 018, 019, 020, 021, 023, 028 |
| **UNPROVED** | **6** | DECK-009, 011, 022, 026, 027, 029 |
| **NOT TESTABLE YET** | **1** | DECK-016 |

\* DECK-017 é PROVED como princípio e PARTIAL como cobertura.

**Leitura em uma frase:** o eixo **REGULATÓRIO–MOLÉCULA–PORTFÓLIO está provado**; o eixo
**CAMPO–COMUNICAÇÃO–TENDÊNCIA não está**, e a razão é sempre a mesma — **falta linha de base
histórica e falta coleta de conversa pública**.

---

## A MATRIZ

| DECK | Claim | Status | FR | ES | IT | EU | Source pack | Normalização | Cruzamento | Caso real | Alinh. ADAMA | Falta | Próximo teste |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| **001** | REGULATION | **PROVED** | ✅ | ⚠️ | ✅ | ✅ | REGULATION | X-006 ✅ | X-004, X-006 | CASE-001, 011 | HIGH | dump aberto ES | consulta MAPA (P-011) |
| **002** | SCIENCE | **PROVED** | ✅ | ✅ | ✅ | ✅ | SCIENCE | X-010 ⚠️ | X-002 | CASE-009, 010 | HIGH | régua de autoridade | — |
| **003** | WEATHER (contexto) | **PROVED** | ✅ | ✅ | ✅ | ✅ | WEATHER | — | X-001 ⚠️ | CASE-005, 006 | MEDIUM | nada p/ contexto | — |
| **004** | MARKET | **PARTIAL** | ⚠️ | ⚠️ | ⚠️ | ⚠️ | MARKET | — | — | — | MEDIUM | comércio exterior, eventos | Eurostat Comext bem consultado |
| **005** | COMPETITOR | **PARTIAL** | ✅ reg. | ❌ | ✅ reg. | — | COMPETITOR | DECK-015 ❌ | X-005 ✅ / X-003 ❌ | CASE-011 | HIGH | comunicação | packs de comunicação |
| **006** | MOLECULE | **PARTIAL** | ✅ | ⚠️ | ✅ | ✅ | MOLECULE | X-006 ✅ | X-006 | CASE-011 | HIGH | **manufacturer, origem** | fontes de origem autorizada |
| **007** | FIELD | **PARTIAL** | ⚠️ PDF | ✅ RAIF | ⚠️ PDF | — | FIELD | X-007 ⚠️ | — | CASE-007, 012 | HIGH | FR/IT processável | — |
| **008** | DISTRIBUTION | **PARTIAL** | ✅ rede | ❌ | ❌ | ❌ | DISTRIBUTION | — | — | FR-T13-001 | NÃO SEI | ES, IT, e o fluxo | registro de empresas ES/IT |
| **009** | "discussion **rises**" | **UNPROVED** | ❌ | ❌ | ❌ | — | FIELD | — | — | — | HIGH | **linha de base** | régua temporal |
| **010** | "regulatory status changes" | **PROVED** | ✅ | ⚠️ | ✅ | ✅ | REGULATION | X-006 ✅ | X-006 | **CASE-011** | HIGH | — | — |
| **011** | "competitor **increases**" | **UNPROVED** | ❌ | ❌ | ❌ | — | COMPETITOR | — | X-003 ❌ | — | HIGH | coleta + base | régua temporal |
| **012** | new registration/manuf./origin | **PARTIAL** | ⚠️ | ❌ | ⚠️ | — | MOLECULE | X-006 ✅ | — | — | HIGH | versionamento semanal | arquivar versões |
| **013** | SAME ISSUE | **PARTIAL** | ⚠️ 23,5% | ✅ | ❌ | — | FIELD | **X-007 medido: 23,5% do uso** | X-007 | CASE-007 | HIGH | 76,5% do uso francês | resolver cultura-grupo |
| **014** | SAME MOLECULE | **PROVED** | ✅ | ✅ | ✅ | ✅ | MOLECULE | **X-006 ✅ 82% uso** | X-006 | **CASE-011** | HIGH | cobre e enxofre | — |
| **015** | SAME COMPETITOR | **PARTIAL** | ✅ | ❌ | ✅ | — | COMPETITOR | **falta** | X-005 | CASE-011 | HIGH | normalizar titular→grupo | normalizador de entidade |
| **016** | SIMILAR MOVEMENT | **NOT TESTABLE** | ❌ | ⚠️ | ❌ | — | FIELD | — | — | — | HIGH | série em ≥2 países | — |
| **017** | fontes públicas configuradas | **PROVED**\* | ✅ | ✅ | ✅ | ✅ | todos | — | — | 31 SOURCE_IDs | — | 4 packs vazios | — |
| **018** | WHO/WHAT/WHERE/WHEN | **PARTIAL** | ⚠️ | ✅ | ⚠️ | ✅ | — | — | — | — | — | WHO em clima; WHERE em ciência | — |
| **019** | idioma local normalizado | **PARTIAL** | ⚠️ | ✅ | ⚠️ | ✅ | — | X-006 ✅ X-007 ⚠️ | — | CAP-002 | — | X-007 | fechar X-007 |
| **020** | CROP×ISSUE×SCIENCE×MOLECULE×COMPETITOR×PORTFOLIO | **PARTIAL — 5/6** | ✅ | ⚠️ | ⚠️ | ✅ | — | X-006 ✅ | X-006 + X-002 | **CASE-011** | HIGH | elo ISSUE automático | fechar X-007 |
| **021** | DISTRIBUTION (camada) | **PARTIAL** | ✅ rede | ❌ | ❌ | ❌ | DISTRIBUTION | — | — | FR-T13-001 | NÃO SEI | volume, catálogo, acordos | fontes de catálogo |
| **022** | régua de "increasing" | **UNPROVED** | ❌ | ❌ | ❌ | ❌ | — | — | — | — | HIGH | a régua | `REGUA-DE-ALERTA-EAME.md` |
| **023** | DELIVER (6 saídas) | **PARTIAL** | — | — | — | — | — | — | — | — | — | ALERT sem régua | contratos textuais |
| **024** | toda resposta leva à evidência | **PROVED** | ✅ | ✅ | ✅ | ✅ | — | — | — | 14 amostras | — | campo FACT/INTERP/ACTION | aplicar a partir do CASE-013 |
| **025** | "we don't know yet" | **PROVED** | ✅ | ✅ | ✅ | ✅ | — | — | — | 14 NÃO SEI, 5 hipóteses caídas | — | — | — |
| **026** | 3 fontes independentes | **UNPROVED** | — | — | — | — | — | — | — | — | — | régua criada, não aplicada | aplicar a um caso |
| **027** | CONFIDENCE | **UNPROVED** | — | — | — | — | — | — | — | — | — | idem | idem |
| **028** | MARKETING OPPORTUNITY | **UNPROVED** | — | — | — | — | — | — | — | — | HIGH | 2 dos 4 lados fracos | fechar COMPETITOR e FIELD |
| **029** | SUPPLY WATCH | **UNPROVED** | ❌ | ❌ | ❌ | ❌ | MOLECULE | — | — | — | NÃO SEI | tudo | fontes de origem |
| **030** | pilot focado | **PROVED** | ✅ | ✅ | ✅ | — | — | — | — | — | — | — | — |

Legenda: ✅ provado · ⚠️ parcial · ❌ ausente · — não se aplica

---

## O QUE PROMETEMOS × O QUE JÁ PROVAMOS

### Provado e demonstrável amanhã
1. **Mudança regulatória europeia ligada ao produto nacional e ao portfólio ADAMA** —
   com identificador, data e texto integral em quatro línguas (DECK-001, 010, 014).
2. **A mesma molécula atravessando os três mercados** — com cobertura medida de 82% do uso
   (DECK-014).
3. **Ciência dirigida a um problema específico** — com a armadilha da consulta larga medida
   e evitada (DECK-002).
4. **Contexto climático regional com série histórica** — e a recusa explícita da causalidade
   (DECK-003 + CASE-008).
5. **A disciplina de evidência** — toda resposta leva à fonte, e "não sabemos ainda" é
   comportamento, não desculpa (DECK-024, 025).

### Prometido e ainda não provado — e o motivo é sempre o mesmo
6. **"rises" / "increases"** (DECK-009, 011, 016, 022) — não temos **linha de base
   histórica** de conversa pública nem coleta comparável. É o buraco mais caro do deck.
7. **Comunicação do concorrente** (DECK-005 parcial, 011) — 403/502/404 nos três sites
   testados; superar exigiria varredura que a própria disciplina do projeto proíbe.
8. **Manufacturer e origem autorizada** (DECK-006, 012, 029) — **nunca investigado**, e o
   registro nacional **não** contém: `titulaire` é titular de AMM, não fabricante.
9. **Distribuição** (DECK-008, 021) — **saiu de zero na MISSÃO 03**: a França tem 4.646
   atacadistas de grãos e 4.251 de produtos químicos em fonte aberta, com as grandes
   cooperativas nominalmente. Mas é **a rede, não o fluxo** — volume, catálogo e acordos
   continuam sem fonte, e Espanha e Itália não foram investigadas.
10. **Réguas de alerta, confiança e independência** (DECK-026, 027) — escritas nesta missão,
    ainda **não aplicadas** a um caso.

---

## OS QUATRO GAPS QUE DECIDEM O RESTO

| # | Gap | Bloqueia | Custo estimado | Prioridade |
|---|---|---|---|---|
| **G1** | **Linha de base histórica** de qualquer camada de conversa | DECK-009, 011, 016, 022, 028 | alto — exige começar a arquivar **hoje** | **máxima** |
| **G2** | **Manufacturer / origem autorizada** | DECK-006, 012, 029 | desconhecido — nunca investigado | alta |
| **G3** | **Normalização FR→EPPO** (X-007) | DECK-013, 019, 020 | **medido: resolve 23,5% do uso; 46% do vocabulário francês é grupo por construção e não tem espécie** | alta |
| **G4** | **Normalização de titular → grupo** | DECK-015 | baixo | média |

> **G1 tem uma propriedade que os outros não têm: ele não se resolve pesquisando melhor.**
> Linha de base é tempo. Toda semana que passa sem arquivar é uma semana que não volta.
> A recomendação operacional imediata é **começar a arquivar as versões semanais** do E-Phy,
> do CSV italiano, do RAIF e dos boletins — mesmo antes de decidir o produto.
