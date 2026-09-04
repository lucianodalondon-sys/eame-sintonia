# ENTREGA DA MADRUGADA · 2026-09-04

```
MEETING_PORTAL_READY        YES
MEETING_FREEZE              YES
FREEZE_TIME                 2026-09-04T03:22:28Z
MEETING_HEAD                014b929   (claude/meeting-intelligence-integration)
DEPLOY_URL                  https://sintonia-eame-preview.vercel.app/portale
INTELLIGENCE_HEAD_USED      b3935bd   (claude/opportunity-commercial-priority-v1)
SNAPSHOT_BUILD_ID           V21-358954754db5ea2f
MEETING_CUTOFF              2026-09-04T00:52:54Z
VISUAL_BASE                 a14b9e1   (ancestral de 014b929 — casca preservada)
```

---

## O QUE MOSTRAR NA REUNIÃO

Cinco casos, escolhidos porque cada um demonstra uma coisa diferente que a
máquina sabe fazer — e todos foram abertos num browser real, nas duas línguas,
em desktop e telemóvel.

### 1 · Botrite × videira × Emilia-Romagna — `OPP_5F31A63F844D`
`ACT_NOW` · `SALES_READY` · `PUBLISHABLE` · janela de pré-colheita aberta agora

**A demonstração inteira num cartão.** O único caso onde tudo fecha: a fonte
declara a regra, o estádio está no mesmo documento, a janela está aberta hoje, há
produto de catálogo ligado, e a leitura pode sair publicada. É por aqui que se
começa.

### 2 · Botrite × videira × Toscana — `OPP_F8106D5E1767`
`ACT_NOW` · janela fenológica · **um elo, não a cadeia**

Serve para mostrar honestidade: sustenta `ACT_NOW`, mas a frase da fonte
(«maggior suscettibilità») prova **um** elo só. O portal diz isso, em vez de
fingir a cadeia completa. Mostrar logo a seguir ao caso 1 — o contraste é o
argumento.

### 3 · Carpocapsa × macieira × Veneto — `OPP_75C37DED9160`
`VALIDATE_NOW` · `RULE_DELEGATED_TO_FARM` · **dois produtos, nenhum coroado**

O caso mais rico. Três coisas ao mesmo tempo:
- o estádio da praga **acabou** e a recomendação **continua** — e a tela não
  confunde as duas;
- a regra existe mas **delega a decisão à observação no campo**, dito em
  linguagem humana;
- tem dois produtos e o motor **não** declara principal, então nenhum é coroado.
  É a resposta visível à contradição que existia antes.

### 4 · Escafoideo × videira × Toscana — `OPP_D11664591168`
`WATCH` · `RULE_ADMINISTRATIVE_ONLY` · **obrigação, não janela**

O único caso do acervo com regra administrativa. Sem tipo de janela — e isso é a
demonstração, não um vazio: obrigação de norma não é janela agronômica. Mostra
que a máquina distingue as duas.

### 5 · Tignoletta × videira × Umbria — `OPP_169BD86DB324`
`WATCH` · **a fonte diz que não é preciso intervir**

A inteligência que esfria, por quatro campos ao mesmo tempo:
`NEED_DIRECTION = NO_ACTION_RECOMMENDED` · `ACTION_RECOMMENDATION_STATE =
NOT_NEEDED_DECLARED` · `PEST_STAGE_STATE = STAGE_DECLINING` ·
`WHY_COMMERCIAL = NEED_CLOSED`.

**Fechar com este.** Um sistema que só diz «venda» não é inteligência comercial;
é um folheto. Este caso prova que a máquina sabe dizer «agora não».

### 6 · O acervo inteiro, como pano de fundo
`43 casos · ACT_NOW 2 · VALIDATE_NOW 3 · WATCH 22 · TO_VALIDATE 9 · FUTURE_PREPARATION 7`
`PUBLISHABLE 5 · VALIDATION_REQUIRED 38`

Os números defendem-se sozinhos: **2 acionáveis em 43**. A régua é apertada de
propósito, e é isso que torna os dois acionáveis dignos de confiança.

---

## LIMITAÇÕES CONHECIDAS — dizer antes que perguntem

**1 · Não há evidência que contradiz.**
`WEAKENS 0 · CONTRADICTS 0 · CLOSES 0` nos 43. O motor não emite papel de
evidência negativo neste snapshot. Não prometer «evidência que contradiz»; a
inteligência negativa existe e está no caso 5, noutros campos.

**2 · O ecrã de demonstração continua contraditório.**
O gate mede `real 0 · legacy 14 / 43 / 48`. A superfície canônica está limpa; os
21 casos de apresentação mantêm as contradições antigas de produto principal e de
janela. Estão separados e **não contaminam nenhum número dos 43**.
**Apresentar apenas o Radar Canônico.** É uma tela a não abrir.

**3 · O smoke ao vivo não foi dirigido daqui.**
Os bytes servidos são idênticos aos locais (sha256 nos quatro ficheiros críticos)
e os 23 recursos devolvem 200. Mas o Chromium deste contentor não atravessa o
relay do proxy, então os 24 percursos verdes correram sobre os bytes locais
idênticos, não sobre o domínio público. **Clicar uma vez em cada um dos cinco
casos antes da reunião fecha esta lacuna em um minuto.**

**4 · O exame encolheu no merge.**
De 20 para 14 testemunhas. Saíram `PRIMARY_MATCH_SINGLE_OWNER`,
`NO_PRIMARY_WHEN_UNKNOWN`, `WINDOW_SINGLE_OWNER`,
`WINDOW_DEFINED_OPEN_SEPARATED` e `DEMO_AND_CANONICAL_SEPARATED`. Verifiquei
essas propriedades por fora e **seguram** — mas quem tocar nisto depois da
reunião não será avisado pelo repositório. Dívida a pagar depois.

**5 · Quatro portões antigos continuam vermelhos.**
`B3 · H3 · W2 · DS1` — vermelhos **também na base congelada `a14b9e1`**, sob
condição idêntica (mesmo tree, mesmo pacote). Não são desta integração. `O1`, que
também falhava, ficou verde.

---

## GATES FINAIS

| | |
|---|---|
| `meeting-gate.mjs` | 14/14 |
| `meeting-browser.mjs` | 24/24 percursos · 1440 e 390 · IT e EN |
| `browser.mjs` | 7/7 |
| `run.mjs` | 67/71 (base: 66/71) |
| `ADAPTER_BOUNDARY` | `PASS_DECLARED_SCHEMA_ADAPTATION` · IT e EN |
| `DECISION_FIELDS_CHANGED_BY_FRONTEND` | **0** |
| `CANONICAL_CASES_RENDERED` | **43** · alheios 0 · IT e EN |
| `CLIENT_PRIMARY_MATCH_NULL` | **26 / 26** |
| Cadeia canônica | reprodutível — `BUILD_ID` idêntico ao reconstruir de `b3935bd` |
| `PROVENANCE-CONTRACT` | 7169 registros · 0 violações |

---

## MISSÕES DA MADRUGADA

**Iniciadas:** 6 sessões vivas às 01:21Z — quatro na integração do portal, uma na
coleta de vídeo/convegni, e esta aba.

**Terminadas e integradas:** as **quatro** sessões do portal convergiram para uma
só branch por fast-forward e dois merges, sem force-push e sem perder trabalho.
`b3935bd` (inteligência canônica), `41a3b9e` (trilha universal), `e7c154c`
(auditoria do radar) e `a14b9e1` (base visual) já eram ancestrais.

**Adiadas — `DEFERRED_AFTER_MEETING`:**

| missão | HEAD | o que terminou | impacto esperado no backfill |
|---|---|---|---|
| coleta de fontes Itália | `34e4ce8` | acervo de fontes 43 → 87; rota de áudio com 84,6% de sinal | fontes novas entram por trilha universal; pode acrescentar evidência a casos existentes, não novos casos |
| coleta vídeo/convegni | `80ff4db`+ | snapshot V2 com 117 objetos e 3,6 M de caracteres de fala | maior potencial de delta — fala científica nomeia molécula; exige ingestão canônica antes de qualquer leitura |
| candidata paralela | `8c316e2` | implementação alternativa do portal | absorvida no merge `e927cb9`; nada por integrar |

**`NEW_DATA_AFTER_CUTOFF = SIM`, e nenhum entrou.** Tudo o que fechou depois de
`2026-09-04T00:52:54Z` ficou fora, por não ter passado trilha universal, backfill
e delta medido. Nada se perdeu.

---

## VEREDITO

```
OVERNIGHT_ORCHESTRATION      = PASS

ALL_MISSIONS_CHECKED         = YES
CLOSED_RELEVANT_WORK_REVIEWED= YES
CANONICAL_PIPELINE_RESPECTED = YES
MEETING_PORTAL_STABLE        = YES
POST_FREEZE_WORK_DEFERRED    = YES
DUPLICATE_WORK_CREATED       = NO
PARTIAL_DATA_INTEGRATED      = NO

NEW_COLLECTION_STARTED       = NO
THRESHOLDS_CHANGED           = NO
SECOND_ENGINE_CREATED        = NO
VISUAL_REDESIGN              = NO
RAW_EVIDENCE_CHANGED         = NO
FORCE_PUSH                   = NO
```

O risco que dominou a noite — quatro sessões a construir a mesma integração —
**não se materializou**: convergiram sozinhas, e esta aba nunca precisou de
arbitrar. O que ela fez foi medir, e três vezes o que salvou o relatório foi
desconfiar do instrumento antes do objeto.
