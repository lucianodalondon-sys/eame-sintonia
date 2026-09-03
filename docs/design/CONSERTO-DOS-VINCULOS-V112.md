# O conserto dos dois vínculos — Commercial Priority V1.1.2

```
VEREDITO: READY — os dois bloqueios fechados por prova executável
BASE AUDITADA: e0a813d (VEREDITO = NOT_READY)
BUILD_ID DEPOIS: V21-5c847ef25e17f680
```

Esta rodada não procurou número melhor. Procurou o número verdadeiro depois que
o vínculo parasse de mentir. O que saiu foi **SALES_READY 4 → 5** — e o quinto
não nasceu de portão afrouxado: nasceu de uma vírgula alheia deixar de apagar
uma recomendação que o boletim de Siena escreveu por extenso.

    NÃO SE CONSERTA UM VÍNCULO PARA MELHORAR O NÚMERO.
    CONSERTA-SE PARA SABER QUAL É O NÚMERO.

---

## 1 · HEAD, branch, commits

| | |
|---|---|
| branch | `claude/opportunity-commercial-priority-v1` |
| commit auditado | `e0a813d` — *a revisão encontra dois defeitos que destroem oportunidade, e não integra* |
| commit desta rodada | este |
| `BUILD_ID` antes | `V21-d52e73904a1d9966` |
| `BUILD_ID` depois | `V21-5c847ef25e17f680` |
| cadeia | `bash scripts/v21_cadeia.sh` → `EXIT=0` |
| contratos | geografia 0 violações · procedência 0 violações · língua 0 campos só em português |

**O que NÃO foi tocado, e isso é a metade mais importante do relatório:**

```
$ git diff --stat scripts/v21_comercial.py
(vazio)
```

A régua comercial — os portões de `COMMERCIAL_PRIORITY`, a regra de
`EXTERNAL_MATERIAL_READY`, os seis bloqueios de saída — **não recebeu uma linha
de alteração**. Nenhum limiar mudou. O que mudou foi a evidência que chega até
ela.

    SE O NÚMERO SOBE E A RÉGUA NÃO FOI TOCADA, QUEM MUDOU FOI O FATO.

---

## 2 · Os dois defeitos, reproduzidos ANTES do conserto

A testemunha é executável e mora em `scripts/v21_defeitos_do_vinculo.py`. Ela lê
o pacote construído e conta ocorrências. Rodada sobre `e0a813d`:

```
DEFEITO 1 · JANELA HERDADA POR COINCIDENCIA DE CULTURA
ocorrencias: 37
  OPP_1A9962A3A2BC  CROP_GRAPEVINE x ISSUE_BOTRYTIS em REGION_EMILIA_ROMAGNA
      carrega IT-WIN-001 — que declara ['CROP_GRAPEVINE'] x ['ISSUE_SCAPHOIDEUS']
      em ['REGION_VENETO']  (diverge em: alvo, regiao)
  … 36 outras

DEFEITO 2 · DIRECAO REPARTIDA ENTRE OS ALVOS DA MESMA ORACAO
ocorrencias: 3
  IT-PHEN-041 · ACTION_SUSPENDED atribuido a ISSUE_BOTRYTIS
      · trecho nomeia SCAPHOIDEUS, BOTRYTIS, POWDERY_MILDEW
  IT-PHEN-041 · ACTION_SUSPENDED atribuido a ISSUE_POWDERY_MILDEW  (idem)
  IT-PHEN-041 · ACTION_SUSPENDED atribuido a ISSUE_SCAPHOIDEUS     (idem)
```

O defeito 2 foi medido **contra o código de `e0a813d` de fato**, extraído com
`git show e0a813d:scripts/v21_necessidade.py` e importado num caminho separado —
não contra uma lembrança do que ele fazia. A mesma testemunha, sobre o código de
hoje, imprime `0` nas duas listas.

**Onde cada eixo era descartado — a linha exata:**

```python
# scripts/v21_oportunidades.py, em e0a813d
win_crop = _ix(cs['CROP-WINDOWS'], 'CROP_IDS')      # ← só a cultura vira chave
…
janela(win_crop.get(crop, []) + apoios)             # ← alvo e região perdidos
'ACTIONABILITY': 2 if win_crop.get(crop) else 1     # ← e pontuam por isso

# scripts/v21_necessidade.py, em e0a813d
est, _padrao = direcao(oracao)
for c in crops:
    for i in issues:                                # ← uma direção, N alvos
        _pinar(achados, sinal, campo, metodo, c, i, est, oracao)
```

O registro `IT-WIN-001` declara os três eixos — `CROP_IDS`, `ISSUE_IDS`,
`REGION_IDS`. Dois eram jogados fora no momento de indexar. Não era falta de
dado: era descarte de dado declarado.

---

## 3 · A chave usada para JANELA depois do conserto

`OP.janela_vale(janela, cultura, alvo, geografia)` — a janela vale para a
combinação **se e somente se ela mesma a declarar**:

| eixo | regra |
|---|---|
| cultura | `CROP_IDS` tem de conter a cultura do caso. Sempre exigido. |
| alvo | `ISSUE_IDS` não vazio → tem de conter o alvo do caso. |
| alvo | `ISSUE_IDS` vazio **com `ISSUE` escrito em prosa** → não vale para ninguém. |
| alvo | `ISSUE_IDS` vazio e sem prosa → o eixo não foi declarado, e não restringe. |
| região | `REGION_IDS` não vazio → tem de conter a geografia do caso. |
| região | `REGION_IDS` vazio → janela nacional; o nacional contém a região. |

Duas leis, e a segunda é a que evita trocar um erro por outro:

> **COINCIDIR NA CULTURA NÃO É SER A MESMA JANELA.**
> **EIXO SEM IDENTIDADE NÃO É EIXO AUSENTE — É «NÃO SEI».**

`IT-WIN-006` é o caso que obriga a segunda: declara «Cocciniglie farinose
(Planococcus spp.)» em prosa e tem `ISSUE_IDS: []`, porque cochonilha farinhenta
não tem identificador no léxico. Tratar essa lista vazia como curinga daria a
janela das cochonilhas à botrite. Lista vazia ali é alvo que existe e não se
sabe nomear.

E `T21b` fixa o outro lado: o que a evidência **não** declarou não vira exigência
inventada. Uma janela sem região continua alcançando a região — senão o conserto
viraria um portão novo, fechado por precaução em vez de por fato.

---

## 4 · A regra usada para NEED_DIRECTION depois do conserto

```python
if est not in (NEUTRAL_MENTION, UNKNOWN):
    if len(issues) > 1:
        amb, est = MULTIPLE_TARGETS_IN_CLAUSE, UNKNOWN
    elif len(crops) > 1:
        amb, est = MULTIPLE_CROPS_IN_CLAUSE, UNKNOWN
```

> **UMA PALAVRA DE DIREÇÃO NUMA ORAÇÃO COM VÁRIOS ALVOS NÃO DIZ A QUAL DELES SE
> REFERE. ENTÃO NÃO SE SABE — E «NÃO SEI» É A RESPOSTA.**

Quatro decisões dentro dessa regra, e cada uma tem uma razão medida:

**a) O par sobrevive; só a direção morre.** A fonte escreveu cultura e alvo na
mesma oração — isso é observação e continua valendo. O que não existe é a
direção individual. Destruir o par seria trocar um erro de atribuição por uma
perda de observação.

**b) `NEUTRAL_MENTION` e `UNKNOWN` não disparam a regra.** Não há direção sendo
repartida quando não há direção. Aplicar a regra ali seria mexer em três orações
que não têm defeito — e correção que muda o que não estava errado é ruído.

**c) A oração que não nomeia alvo nenhum continua valendo para todos os pares do
documento.** `IT-PHEN-022` diz «durante a floração VIGORA A PROIBIÇÃO de
intervenção fitoiátrica com inseticidas, para tutela das abelhas». A proibição é
da **prática**, sobre a cultura inteira. Não é uma direção de um alvo repartida
entre vários: é uma direção que nunca foi de um alvo só. `T24` fixa isso, e é o
teste que impede o conserto de abrir a porta da piralide e da diabrótica na
Lombardia.

**d) A assimetria é de propósito.** `UNKNOWN` não está em `NECESSIDADE_POSITIVA`:
não vende, nunca. Uma oração ambígua **não pode criar permissão comercial** — no
máximo deixa de destruir uma que outra oração, sozinha e clara, já sustentava.
`T24b` fixa isso.

O motivo viaja no pacote: `NEED_AMBIGUITY_CODES` e `NEED_AMBIGUITY`. Um `UNKNOWN`
mudo parece «não havia texto»; e o que houve foi texto demais para um alvo só.

---

## 5 · Testes adicionados

Dez, em `tests/test_prioridade_comercial.py`. Todos falharam antes do conserto —
nenhum passa por sorte.

| teste | o que fixa | antes |
|---|---|---|
| `T19` | a janela de um alvo não serve a outro alvo | FALHA |
| `T20` | a janela de uma região não atravessa a fronteira, nem vira nacional | FALHA |
| `T21` | alvo declarado em prosa sem ID não é curinga | FALHA |
| `T21b` | eixo realmente ausente não restringe — o conserto não vira portão | FALHA |
| `T21c` | **no pacote**: nenhum caso carrega janela que o contradiga | FALHA |
| `T22` | oração com vários alvos não distribui direção; o par sobrevive | FALHA |
| `T23` | a oração separada continua decidindo — Siena não foi apagada | FALHA |
| `T24` | a proibição da prática, sem alvo nomeado, continua valendo | FALHA |
| `T24b` | ambiguidade nunca vende | FALHA |
| `T24c` | **no pacote**: direção afirmada nasce de trecho com um alvo só | FALHA |

Mais a testemunha executável `scripts/v21_defeitos_do_vinculo.py`, que sai com
código 1 enquanto houver ocorrência e 0 quando não houver.

Suíte da camada comercial: **52 de 52 verdes**.

---

## 6 · Regressão sobre os 43 casos já classificados

`scripts/v21_regressao_do_vinculo.py` compara o pacote de `e0a813d`, guardado em
`data/samples/AUDITORIA-SOMBRA/V112-ANTES-DO-CONSERTO.json`, com o que a cadeia
reconstruiu. O par é feito por `arquétipo|cultura|alvo|região` — **não por ID**,
porque a data de janela entra no identificador e consertar o vínculo muda o
hash. Casar por ID diria «43 saíram, 43 entraram», que é verdade sobre o hash e
mentira sobre o caso.

```
CASOS   antes 43 · depois 43 · mesmos 43 · so antes 0 · so depois 0
CASOS QUE MUDARAM: 16 de 43   (todos de videira)
```

**Nenhum caso nasceu. Nenhum caso morreu.** Os 43 são os mesmos 43.

| | antes | depois |
|---|---|---|
| `OPPORTUNITY_CONFIRMED` | 21 | **33** |
| `OPPORTUNITY_CANDIDATE` | 22 | **10** |
| pares cultura × alvo observados | 12 | **12** (o mesmo conjunto) |
| casos com 2 famílias externas | 7 | **4** |
| casos com janela ligada | 16 | **0** |

Os 12 casos de videira que estavam `CANDIDATE` viraram `CONFIRMED` porque os
dois portões que os derrubavam eram consequência direta da janela estrangeira:

- `A_GEOGRAFIA · apoios em geografias que nao se contem` — o apoio em geografia
  incompatível **era a janela do Veneto** num caso da Umbria;
- `F_PROCEDENCIA · apoio sem origem recuperavel: IT-WIN-001, IT-WIN-002` — os
  dois apoios sem procedência **eram as mesmas janelas**.

Tirado o apoio que não era do caso, o portão não tinha mais o que apontar. O
portão não foi afrouxado: **ficou sem réu**.

E o `OPPORTUNITY_SCORE` caiu em todos eles — 11→10 em dez casos, 12→11 em dois —
porque `ACTIONABILITY` valia 2 por existir uma janela que não era daquele caso.

    A CORREÇÃO TIROU PONTO DE QUEM SUBIU DE ESTADO.
    ISSO É O CONTRÁRIO DE MAQUIAR NÚMERO.

---

## 7 · SALES_READY — antes e depois

```
antes  4      depois 5
```

| caso | antes | depois |
|---|---|---|
| macieira × carpocapsa · Veneto | SALES_READY | SALES_READY |
| milho × piralide · Friuli-Venezia Giulia | SALES_READY | SALES_READY |
| videira × botrite · Emilia-Romagna | SALES_READY | SALES_READY |
| videira × traça-da-uva · Emilia-Romagna | SALES_READY | SALES_READY |
| **videira × botrite · Toscana** | TO_VALIDATE | **SALES_READY** |

Os cinco, um por um, têm: portões fechados, red team limpo, produto do catálogo
comercial com rótulo ministerial no par exato, geografia que se sustenta, frase
da fonte que nomeia o próprio par, e sinal com menos de 30 dias.

```
OPP_5F31A63F844D  videira × botrite · Emilia-Romagna   BANJO
OPP_3C8C3960CC66  videira × traça  · Emilia-Romagna    Lamdex® Extra
OPP_75C37DED9160  macieira × carpocapsa · Veneto       Lamdex® Extra, MAVRIK SMART
OPP_9C600748BB1B  milho × piralide · Friuli            Lamdex® Extra
OPP_F8106D5E1767  videira × botrite · Toscana          BANJO
```

**Nenhum dos quatro antigos foi rebaixado, e nenhum outro caso subiu.** A
promoção é uma só, e tem nome, fonte e frase.

---

## 8 · EXTERNAL_MATERIAL_READY — antes e depois

```
antes   YES 2 · VALIDATION_REQUIRED 2 · NO 39
depois  YES 5 · VALIDATION_REQUIRED 0 · NO 38
```

Os três que passaram a `YES`, com o motivo factual de cada um:

| caso | antes | por quê |
|---|---|---|
| videira × botrite · Emilia-Romagna | VALIDATION_REQUIRED | os dois bloqueios eram `EVIDENCE_GATE_OPEN` e `WINDOW_IS_ADMINISTRATIVE` — **os dois causados pela janela do Veneto**. Sem ela, não há portão aberto nem data de ato exibida como janela. |
| videira × traça-da-uva · Emilia-Romagna | VALIDATION_REQUIRED | idêntico. |
| videira × botrite · Toscana | NO (`NOT_SALES_READY`) | passou a `SALES_READY` (§7) e não tem pendência. |

⚠️ **A regra de saída externa não foi tocada.** Os seis bloqueios continuam os
mesmos seis, com o mesmo texto. `WINDOW_IS_ADMINISTRATIVE` desapareceu desses
casos porque `WINDOW_KIND` deixou de ser `PREPARATION` — e deixou de ser porque
a janela administrativa que estava lá **era de outra região e de outro alvo**.

    O BLOQUEIO NÃO FOI REMOVIDO. O FATO QUE O DISPARAVA É QUE ERA FALSO.

---

## 9 · VALIDATION_REQUIRED — antes e depois

```
antes 2 · depois 0
```

Os dois eram os mesmos dois casos de Emilia-Romagna da tabela acima. Zero hoje
**não** significa que a coluna virou decorativa: `T14`, `T15`, `T16` e `T17`
continuam provando que portão aberto, data de ato, catálogo que não declara a
cultura e recomendação sem frase da fonte cada um produz `VALIDATION_REQUIRED`.
A coluna funciona; hoje não há caso que a acione.

---

## 10 · Cada oportunidade que mudou, com evidência

**Os dois casos que mudaram de direção — `ANTES → EVIDÊNCIA → REGRA → DEPOIS`:**

### videira × botrite · Toscana

```
ANTES     NEED_DIRECTION = ACTION_SUSPENDED   ·   COMMERCIAL_PRIORITY = TO_VALIDATE
```

**EVIDÊNCIA.** `IT-PHEN-041` (Firenze) publica o texto de Siena com vírgulas onde
Siena usou ponto e vírgula:

> «Mesmo texto de seções que Siena nesta semana: suspensão da defesa
> antiperonosporica em vinhas com invaiatura completa, suspensão de oídio nas
> variedades próximas da maturação, fim da defesa de black rot, **janela de
> maior suscetibilidade a botrite**, fim da defesa de Scaphoideus titanus.»

A oração inteira vira uma só. O primeiro padrão que casa é `suspensao`. Os três
alvos nomeados recebiam `ACTION_SUSPENDED` — inclusive a botrite, para a qual o
**mesmo texto** diz o contrário. E `IT-PHEN-040` (Siena), com pontuação, diz por
extenso:

> «para botrite, na fase de maior suscetibilidade, possível intervir com
> antibotríticos microbiológicos, bicarbonato de potássio ou terpenos e desfolha
> junto aos cachos;»

**REGRA.** Oração com vários alvos e uma direção → `UNKNOWN` para todos. A
direção passa a vir da oração de Siena, que nomeia um alvo só.

```
DEPOIS    NEED_DIRECTION = POSITIVE_PRESSURE  ·  COMMERCIAL_PRIORITY = SALES_READY
          EXTERNAL_MATERIAL_READY = YES  ·  produto BANJO  ·  sinal de 2026-08-27
```

### videira × Scaphoideus · Toscana

```
ANTES  ACTION_SUSPENDED   →   DEPOIS  WINDOW_CONCLUDED
```

**EVIDÊNCIA.** A mesma oração corrida de `IT-PHEN-041`. Com ela fora,
`IT-PHEN-040` decide sozinha: «defesa de Scaphoideus titanus concluída e retirada
das armadilhas.»

**REGRA.** A mesma. **CONSEQUÊNCIA COMERCIAL: nenhuma** — os dois estados são
restritivos, e o caso continua `TO_VALIDATE` com `NEED_CLOSED`. Trocou-se um
motivo errado por um motivo certo, e a porta continua fechada.

**Os 14 restantes** perderam os três apoios `IT-WIN-001/002/003` e, com eles, os
dois portões e a janela administrativa. Doze são casos regionais de videira que
passaram de `CANDIDATE` a `CONFIRMED` com `SCORE` menor. Quatro são os casos
nacionais de videira (`O2`, `O4`, `O5`, `O6`), que só perderam a janela:

```
DAYS_REMAINING  271 → None      WINDOW_FIELD  PREPARATION_WINDOW → None
STATUS          FUTURE_PREPARATION → ACT_NOW / PREPARE_NOW
```

⚠️ Efeito colateral que precisa ser dito: **três casos nacionais ficaram mais
urgentes** ao perder a janela falsa, porque o `STATUS` passa a sair da idade do
sinal. Nenhum deles mudou de `COMMERCIAL_PRIORITY` nem de
`EXTERNAL_MATERIAL_READY` — continuam `COMMERCIAL_WATCH` / `STRATEGIC_OPPORTUNITY`
e `NO`. E a origem do tempo continua declarada em `COMMERCIAL_WINDOW_FROM =
SIGNAL_DATE`, que é onde se lê que ali não há janela de aplicação nenhuma.

**Nenhuma oportunidade nasceu da correção — a prova em quatro linhas:**

1. 43 casos antes, 43 depois, o mesmo conjunto de identidades;
2. 12 pares observados antes, os **mesmos** 12 depois;
3. `scripts/v21_comercial.py` sem uma linha alterada — nenhum limiar mexeu;
4. `UNKNOWN` em `NEED_DIRECTION`: 26 antes, 26 depois — **nenhum par caiu no
   «não sei»**, e as três direções que se moveram trocaram entre si (9 antes, 9
   depois).

**E nenhuma oportunidade verdadeira foi destruída:** `T24` prova que a proibição
da prática sobrevive (`TREATMENT_PROHIBITED` continua 2), `T21b` prova que eixo
ausente não vira exigência, e nenhum caso perdeu `SALES_READY`.

---

## 11 · DURUM WHEAT

```
DURUM_WHEAT = COLLECTION_REQUIRED   (inalterado)
```

Nada foi mapeado. `CROP_DURUM_WHEAT` continua sendo uma entrada do léxico sem
caso no motor — zero oportunidades declaram essa cultura. Trigo duro **não** foi
transformado em trigo, e não será sem coleta nova. Esta rodada não coletou nada:
ela mexeu em vínculo, não em fonte.

O que falta continua sendo o que a revisão anterior descreveu: um boletim ou uma
tabela de rótulo que declare `frumento duro` explicitamente, com origem
recuperável, para que a distinção deixe de ser uma palavra num alias e passe a
ser um fato com endereço.

---

## 12 · Falhas ainda abertas

**Na suíte:** 715 testes descobertos · 710 executados · 14 pulados · **6 falhas ·
2 erros**. São exatamente os mesmos 8 de `e0a813d`, todos anteriores a esta linha
de missões e classificados um a um em `REVISAO-COMMERCIAL-PRIORITY-V11.md` §7:
procedência de amostras antigas (`IT-ARPAV`, `IT-LASTMILE`, `IT-V2`,
`COMPETITOR-PUBLIC-COMM`, `PIEMONTE-FD`), um artefato ausente deste clone e uma
migration do Supabase ES. **Nenhum toca a camada comercial.**

**No motor, e isto é achado novo desta rodada:**

> **Depois do conserto, NENHUM caso tem janela.**

Não é defeito do conserto — é o retrato da coleta. As sete janelas do acervo
cobrem videira × Scaphoideus em cinco regiões (Veneto, Lombardia, Piemonte,
Trentino, Emilia-Romagna), videira em Modena com alvo sem identificador, e
oliveira × mosca em Modena. Os sinais de campo que formaram par estão em Toscana,
Umbria, Emilia-Romagna, Friuli e Veneto. **A interseção nos três eixos é vazia.**

Consequência honesta: o tempo comercial de **todos** os casos hoje vem de
`SIGNAL_DATE`, não de janela de aplicação — e isso está declarado, caso a caso,
em `COMMERCIAL_WINDOW_FROM`. O ramo positivo da regra de janela está provado por
teste (`T19` afirma o caso que vale, `T21b` a janela nacional), **não por um caso
real**. Fechar isso é coleta: uma janela de aplicação para um par que já tem
sinal — por exemplo videira × botrite na Emilia-Romagna ou na Toscana.

---

## 13 · Confirmação explícita

```
merge          = NÃO
publicação     = NÃO
portal / casco = NÃO TOCADO
```

Nada foi integrado. A interface não foi redesenhada. O trabalho está no branch
`claude/opportunity-commercial-priority-v1` e para aqui.

---

## Veredito

```
VEREDITO = READY

JANELA          = PASS   (T19, T20, T21, T21b, T21c + testemunha executável)
NEED_DIRECTION  = PASS   (T22, T23, T24, T24b, T24c + testemunha executável)

SALES_READY                = 4 → 5
EXTERNAL_MATERIAL_READY    = 2 → 5
VALIDATION_REQUIRED        = 2 → 0
CASOS                      = 43 → 43   (o mesmo conjunto)
PARES OBSERVADOS           = 12 → 12   (o mesmo conjunto)
RÉGUA COMERCIAL            = não tocada
DURUM_WHEAT                = COLLECTION_REQUIRED

ABERTO: nenhum caso tem janela de aplicação — a interseção cultura × alvo ×
        região entre o acervo de janelas e os sinais de campo é vazia. É coleta,
        não motor.
```

`READY` aqui significa exatamente o que a missão pediu: os dois bloqueios estão
fechados por prova que se executa, não por inspeção visual. Não significa que o
acervo esteja completo — o §12 diz onde ele não está.
