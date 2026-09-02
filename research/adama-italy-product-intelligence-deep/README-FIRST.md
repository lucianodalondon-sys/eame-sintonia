# README-FIRST — ADAMA ITALY PRODUCT INTELLIGENCE (DEEP)

**Data:** 2026-09-02 · **Branch:** `claude/adama-italia-product-intelligence-deep`
**Não é trabalho de portal.** Nada aqui entra no site. Nenhum card de oportunidade foi criado — isso é do V2.1.

---

## Leia estes três parágrafos antes de qualquer número

**1. O catálogo não foi recoletado.** Os 51 produtos comerciais e as 51 etichette já tinham sido capturados
em 2026-08-30, na máquina local, por navegador com janela. `adama.com` devolve 403 aqui — e a fronteira
medida na captura original não é navegador vs. script: é **janela gráfica vs. tudo o mais**. Headless também
leva 403. Esta missão reconciliou o que existia e coletou só o que faltava.

**2. As 163 autorizações 'vivas' não eram o que a palavra sugeria.** O relatório anterior chamou de
"vivas hoje" o que a fonte marca como **estado administrativo ativo**. São coisas diferentes, e a §3 mediu
a distância. Ver abaixo.

**3. Nenhum par cultura × alvo foi produzido.** Sem etichetta lida não há par defensável, e as etichettas
não são alcançáveis deste ambiente. Zero é o número honesto, não uma falha escondida.

---

## §3 · O conflito das 163 — resolvido

```
163 ORIGINAL "LIVE"      = 163   (estado administrativo ativo na fonte)
FORMALLY UNEXPIRED       = 155   (vencimento >= snapshot da fonte, 2026-08-31)
EXPIRED_BY_DATE          = 8     (vencimento no passado, estado ainda ativo)
GRACE PERIOD CONFIRMED   = 0     (nenhum: o dataset não traz período de smaltimento)
STATE CONFLICT           = 8     (a fonte se contradiz consigo mesma)
UNKNOWN                  = 163   (CURRENTLY_MARKETABLE_STATE, para todas)
```

**O que "live" significava, medido:** significa `stato_amministrativo` ∈ {Autorizzato, Ri-registrato,
Rinnovato}. **Não** significa autorização não vencida, e **não** significa comercializável. As três coisas
agora são campos separados em `PRODUCTS-REGULATORY.json`.

**Os 8 em conflito** — estado ativo, vencimento 15/08/2026, snapshot da fonte 31/08/2026, 16 dias depois:

| Produto | Registro | Vencimento | Estado na fonte |
|---|---|---|---|
| DAUPHIN 45 | 013899 | 15/08/2026 | Ri-registrato |
| CUSTODIA ULTRA | 015232 | 15/08/2026 | Autorizzato |
| BADGER 45% WG | 015629 | 15/08/2026 | Ri-registrato |
| CARSON 45% WG | 015630 | 15/08/2026 | Ri-registrato |
| BLAISE ULTRA | 017358 | 15/08/2026 | Autorizzato |
| ANTERLEX | 017688 | 15/08/2026 | Autorizzato |
| MOXYL MK | 017689 | 15/08/2026 | Autorizzato |
| VANTEX | 017690 | 15/08/2026 | Autorizzato |

Isto **não** é defeito do coletor: o coletor leu certo o que a fonte escreve. É a fonte que carrega estado
ativo em registro vencido. Pode ser reregistro em curso, atraso de atualização ou período de smaltimento —
**nenhuma das três foi provada**, e por isso `CURRENT_INTERPRETATION = STATE_CONFLICT_IN_SOURCE`.

> Sete outros venceram em 31/08/2026, entre o snapshot e hoje. Esses **não** são conflito: na data do dado
> estavam válidos. É defasagem de snapshot, e está classificada como tal.

---

## §4 · Censo comercial — reconfirmado

| Categoria | Impressa na página | Caminho da URL |
|---|---:|---:|
| ERBICIDI | 26 | 27 |
| FUNGICIDI | 14 | 13 |
| INSETTICIDI | 6 | 6 |
| SPECIALI | 5 | 5 |
| **TOTAL** | **51** | **51** |

**Diferença em relação a 51: 0.** O censo bate exatamente: 26 / 14 / 6 / 5.

**A regra "caminho da URL ≠ categoria" não é teoria — tem um caso real:**

- **Folpan® Energy** mora em `/erbicidi/` mas a página escreve **FUNGICIDI** — e folpet é fungicida.

Um pipeline que classificasse pelo caminho da URL erraria este produto. A categoria impressa vence.

---

## §11 · Reconciliação comercial × regulatória

| Classe | Produtos |
|---|---:|
| REGULATORY_ONLY_NOT_FOUND_IN_CURRENT_PUBLIC_CATALOG | 561 |
| COMMERCIAL_AND_REGULATORY_ADAMA_HOLDER | 42 |
| COMMERCIAL_AND_REGULATORY_OTHER_HOLDER | 7 |
| COMMERCIAL_WITH_REGULATORY_MATCH_UNRESOLVED | 2 |

### Os 7 do catálogo ADAMA cuja autorização italiana é de outra empresa

| Produto no catálogo | Nome no registro | Titular da autorização | Registro |
|---|---|---|---|
| Mirador® SC | MIRADOR SC | SYNGENTA CROP PROTECTION AG | 015111 |
| Mavita® 250 EC | MAVITA 250 EC | SYNGENTA CROP PROTECTION AG | 015293 |
| Zakeo® 250 SC | ZAKEO 250 SC | SYNGENTA CROP PROTECTION AG | 017099 |
| Timeline® Trio | TIMELINE TRIO | SYNGENTA CROP PROTECTION AG | 014935 |
| Clematis® | CLEMATIS | ALBAUGH TKI D.O.O | 017746 |
| Parleaf | PARLEAF | MICROCIDE LTD | 017807 |
| Powerfilm® | COCTEL GOLD | LAINCO S.A. | 017052 |

> **O que isto prova:** o produto está no catálogo público da ADAMA Itália, e a autorização italiana está
> no nome de outra empresa. **O que isto não prova:** licença, distribuição, co-marketing, propriedade ou
> qualquer contrato. Isso é `UNKNOWN` e continua `UNKNOWN` até uma fonte pública dizer.

> Repare em **Powerfilm®**: no registro ele se chama **COCTEL GOLD**, da LAINCO S.A. Nome comercial e nome
> regulatório divergem — por isso o mapa de identidade guarda os dois, nunca um só.

---

## §5 · Os cinco SPECIALI — não foram forçados no universo fitossanitário

| Produto | Registro publicado | Regime | Titular |
|---|---|---|---|
| Brevis® | 16084 | PHYTOSANITARY_REGISTER_IT_T4_001 | ADAMA ITALIA S.R.L. |
| Exelgrow® | 0023801/18 | NOT_THE_PHYTOSANITARY_REGISTER | — |
| Parleaf | 17807 | PHYTOSANITARY_REGISTER_IT_T4_001 | MICROCIDE LTD |
| Budge® | 0037584/22 | NOT_THE_PHYTOSANITARY_REGISTER | — |
| Powerfilm® | 17052 | PHYTOSANITARY_REGISTER_IT_T4_001 | LAINCO S.A. |

**Três são fitossanitários** e existem no registro do Ministero. **Dois não são**: Exelgrow® e Budge®
publicam números no formato `0023801/18` e `0037584/22`, que não existem entre as 17.695 linhas do registro
fitossanitário, e declaram composição em *carbonio organico* e *azoto organico* — linguagem de fertilizante,
não de sostanza attiva. **Qual registro exatamente permanece `UNKNOWN`**: o formato e a composição provam o
que eles **não** são; não provam em qual registro eles **estão**.

---

## §20 · QA — taxa de erro medida

```
QA_SAMPLE_SIZE = 36
QA_PASS = 35
QA_CORRECTED = 0
QA_REJECTED = 0
QA_UNREVIEWED = 1
MEASURED_ERROR_RATE = 0.0
```

Taxa de erro zero só vale se o detector reprova alguma coisa. Foi provado por **injeção de defeito**:
4 defeitos plantados, 3 caíram dentro da amostra sorteada,
e os 3 foram reprovados — recall 1.0 sobre o que a amostra alcançou.
O quarto (troca de categoria) não foi sorteado: amostragem, não cegueira. O arquivo foi restaurado depois.

---

## O que este pacote NÃO entrega

| Camada | Estado | Bloqueio exato |
|---|---|---|
| Conteúdo das etichette | `REAL_GAP` | PDF fora do Git e em bucket sem credencial aqui; `adama.com` = 403 |
| Cultura × alvo × dose × BBCH × carência | `REAL_GAP` | depende do conteúdo da etichetta |
| Cobertura por cultura e por alvo | `REAL_GAP` | idem |
| Código FRAC | `REAL_GAP` | PDF oficial baixado; extração perde dígitos (`M 04` → `M 0`) |
| Futuro regulatório EU | `REAL_GAP` | EU Pesticides Database: 307 → `sorry.ec.europa.eu` |
| Licença/distribuição dos 7 de outro titular | `UNKNOWN` | nenhuma fonte pública lida prova contrato |
| Se o produto é vendido hoje | `UNKNOWN` | nenhuma fonte pública prova comercialização |

**Registros sintéticos: 0.** Nenhum número deste pacote foi inventado, arredondado para cima ou inferido
de categoria de produto. Cada um sai de `research/adama-italy-product-intelligence-deep/*.json` e é
refeito com `scripts/adama_it_intelligence.py` + `scripts/adama_it_qa.py`.
