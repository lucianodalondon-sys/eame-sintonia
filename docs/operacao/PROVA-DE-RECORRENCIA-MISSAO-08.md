# PROVA DE RECORRÊNCIA — a base congelada consegue ser atualizada?

```
PILOT_INFORMATION_BASE = FROZEN (v1, 1e3f5bb) — não reavaliado nesta missão
PILOT_UPDATEABILITY    = PROVED, com uma dependência declarada
TESTES_REAIS           = 91
PROTOTYPE_FROZEN       = SIM
```

**Data:** 2026-08-29 · **MISSÃO 08**

A MISSÃO 07 provou a matéria-prima. Esta responde a outra pergunta:

> *Se as fontes mudarem amanhã, o Sintonia atualiza a inteligência sem redescobrir
> manualmente como cada fonte funciona?*

---

## 1 · COLD START — 4 de 4 cadeias reconstruídas

Executadas do zero, sem usar intermediário processado de nenhuma missão anterior.
`scripts/chain.py`.

| cadeia | resultado | saúde | passos AUTO | MANUAIS | JULGAMENTO | cobertura | bate com o congelado? |
|---|---|---|---|---|---|---|---|
| `fr-prothioconazole` | OK | HEALTHY | 5 | **0** | 2 | 14.060/14.062 = 100% | **sim** — 77 autorizados, ADAMA 3, Bayer 32 |
| `es-identidade` | OK | HEALTHY | 4 | **0** | 0 | 2/2 = 100% | **sim** — ES-01717 com as sete entidades |
| `it-prothioconazole` | OK | HEALTHY | 4 | **0** | 2 | 17.695/17.695 = 100% | **sim, com ressalva** — ver `FREEZE_V1_FINDING` |
| `raif-repilo` | OK | HEALTHY | 4 | **0** | 1 | — | **sim — 12 de 12 células** do CASE-013 |

**Total: 17 passos automáticos, 0 manuais, 5 de julgamento humano.**

O RAIF era o único passo manual quando a missão começou: a URL que o CKAN devolve aponta
para um host inalcançável, e a troca por `www.juntadeandalucia.es` estava em **prosa no
atlas** — conhecimento que ninguém novo teria. Agora está em `raif_download()`.
Automatizá-lo revelou uma segunda coisa que a prosa não dizia: **o ZIP usa Deflate64**, que
o `zipfile` da biblioteca padrão não descomprime. Enquanto o download era manual, ninguém
tropeçava nisso.

### Os cinco passos de julgamento humano — onde eles estão

| cadeia | julgamento | por que não é automatizável |
|---|---|---|
| FR | excluir 1.078 linhas `MFSC` do denominador | fertilizante não tem substância ativa. É uma decisão de **escopo**, e agora é declarada |
| FR · IT | agrupar razão social em **grupo empresarial** | **não há fonte pública de relação corporativa.** Por isso toda cadeia devolve **também** a contagem por entidade legal, que não depende de dicionário |
| IT | aceitar `SECLEVEL=1` no TLS | o host recusa o contexto padrão do Python. Cifra mais antiga, **verificação de certificado mantida** — e o rebaixamento é registrado, nunca silencioso |
| RAIF | escolher o campo `1702` (repilo **visível**) e não o `1703` (incubado) | são a mesma doença em estados diferentes. A escolha muda o número e é agronômica, não técnica |

**O objetivo nunca foi zerar o julgamento humano — era saber onde ele está.** Prova de que
importa: acrescentar `BARCLAY` e `ROTAM` ao dicionário de grupos move 4 produtos franceses
do balde `OUTROS` **sem mudar um único fato**.

---

## 2 · `FREEZE_V1_FINDING` — o critério italiano

**Achado:** a MISSÃO 02 publicou *"85 autorizações em vigor na Itália com protioconazol"*
sem declarar quais estados administrativos contam. A leitura literal dá **83**.

| estado administrativo | n |
|---|---|
| Autorizzato (5 variantes: zonale, art. 10, reconhecimento mútuo, simples, art. 34) | **83** |
| Ri-registrato | 2 |
| Revocato | 3 |
| Scaduto | 1 |

`83` conta só o que contém "Autorizzato"; `85` inclui `Ri-registrato`, cuja autorização foi
**substituída por outra**.

**Classificação: NOVA VERSÃO FUTURA, não correção obrigatória.**

- Nenhum dos dois números é factualmente falso — o que faltava era o **critério**.
- O claim que importa não muda: **ADAMA continua com 5 produtos**, e os cinco são
  estritamente `Autorizzato` nos dois critérios.
- `chain.py` passou a devolver **os dois**, com o critério escrito. Publicar um deles
  sozinho é que não é defensável.

**Nenhum outro número congelado divergiu.** FR (77 / ADAMA 3 / Bayer 32), ES (ES-01717
inteiro) e RAIF (12 de 12 células) reproduziram exatamente.

---

## 3 · A DIVERGÊNCIA ESPANHOLA — resolvida

A MISSÃO 07 registrou `1.998/1.086` (grade) contra `1.993/1.091` (export) como divergência
não resolvida. **Tem regra:**

```
IdEstado=1 ("VIGENTE") == Estado == 'Vigente'
                          OR (Estado == 'Cancelado' AND fechaLimiteVenta >= hoje)
```

Os cinco: **`16192` · `25454` · `ES-00195` · `ES-01106` · `ES-01107`** — cancelados dentro
do **prazo legal de escoamento**.

| registro | produto | titular | caducidade | limite de venda |
|---|---|---|---|---|
| `25454` | AMPLIGO | SYNGENTA ESPAÑA, S.A. | 30-06-2026 | 30-09-2026 |
| `ES-00195` | ERADICOAT | CERTIS BELCHIM B.V. | 28-08-2027 | 03-09-2026 |
| `ES-01106` | INTREPID | CORTEVA AGRISCIENCE SPAIN, S.L.U. | 18-04-2026 | 30-09-2026 |
| `16192` | OVIPRON | FORMULADORES AGROQUÍMICOS EXTREMEÑOS | 31-03-2027 | 03-09-2026 |
| `ES-01107` | RUNNER | CORTEVA AGRISCIENCE SPAIN, S.L.U. | 18-04-2026 | 30-09-2026 |

**Como foram encontrados:** pedindo ao **export** o mesmo filtro da grade. Ele honra
`IdEstado` **e** devolve o campo `Estado` de cada linha — 1.998 linhas das quais 5 dizem
`Cancelado`. Uma requisição, em vez de 400 telas de grade.

**Verificação por igualdade de conjunto, não de contagem:** esses 5 são exatamente os 5
cancelados com `fechaLimiteVenta` futura em todo o registro. Nem um a mais, nem um a menos.

| número | responde |
|---|---|
| **1.998** | *quantos produtos ainda podem ser legalmente comercializados hoje* |
| **1.993** | *quantas autorizações estão em vigor hoje* |

**Os dois estão certos.** Publicar um sem dizer qual pergunta ele responde é que é erro.
E **1.998 tem data de validade**: cai sozinho em 03 e 30/09/2026, com a fonte no ar.

> **Total igual nunca prova estado igual.** As duas leituras concordam em 3.084 e discordam
> na classificação de 5. É a testemunha de por que a comparação tem de ser de **conteúdo
> por identidade**, nunca de contagem. Virou teste
> (`test_mesmo_total_nao_e_mesma_classificacao`).

---

## 4 · DEGRADAÇÃO DE FONTE — 11 formas de apodrecer, 11 falham fechado

`tests/test_operacao.py::TestDegradacaoDeFonte`, contra `scripts/source_health.py`.

| o que acontece | resultado | perigoso? |
|---|---|---|
| campo obrigatório desaparece | `FAILED` | não |
| chave de identidade desaparece | `FAILED` | não |
| **ordem das colunas muda** | `HEALTHY` — a leitura é por **nome**, nunca por posição | não |
| JSON ganha campo | `DEGRADED` — usável, e o contrato mudou | não |
| endpoint devolve HTML no lugar de JSON | `FAILED` | não |
| **lista vazia** | `FAILED` — nunca "zero resultados" | não |
| **HTTP 200 com página de erro** | `FAILED` — status bom, corpo lixo | não |
| id duplicado | `DEGRADED` | não |
| identidade vazia | `FAILED` | não |
| volume fora de ±10% | `DEGRADED` — nunca passa por saudável | não |
| **fonte caiu** | `SOURCE_FAILED` ≠ `NO_NEW_VERSION` ≠ zero | não |

**Zero produzem número errado.** O caso mais perigoso — *fonte falha vira zero* — tem teste
próprio, porque é o que transforma "não consegui ver" em "não há nada".

A cobertura provou-se no primeiro uso real: a cadeia FR **falhou fechada** com 92,9%, e o
motivo era **escopo**, não degradação. A exclusão de MFSC passou a ser declarada. Um
pipeline sem piso teria publicado 92,9% de cobertura sem ninguém perceber.

---

## 5 · REGRESSÃO DO LEITOR ANTIGO

O erro que transformou **1.786** linhas em **1.737** veio inteiramente do parser — provado
porque o `dc_web.pdf` de hoje é **byte a byte idêntico** ao da MISSÃO 06.

O leitor antigo não foi preservado como código, então não se reproduz o bug linha a linha.
**Protege-se o invariante que ele violava:** nenhuma linha desaparece em silêncio.

| prova | o que garante |
|---|---|
| `test_a_coluna_notas_e_removida_antes_do_corte` | a regra que corrigiu o bug continua ligada |
| `test_sem_remover_notas_os_pedacos_aparecem_como_nao_interpretados` | com a regra **desligada** (`strip_notes=False`), os fragmentos aparecem contados como `UNRESOLVED`. **Visível é o oposto de silencioso** |
| `test_nada_desaparece_no_pdf_real` | 1.786 linhas, **0 pedaços não interpretados**, e a distribuição soma o total |

---

## 6 · VERSIONAMENTO — quais fontes permitem história real

| fonte | histórico nativo | versão vem de | estado hoje |
|---|---|---|---|
| **EU-T4-001** (CELLAR) | **SIM** — o CELEX é imutável | o próprio ato | histórico completo |
| **ES-T3-001** (RAIF) | **SIM** — 20 anos no mesmo pacote | `generated` do XML | histórico completo |
| **IT-T4-001** | **PARCIAL** — traz revogação, motivo e datas | **o nome do arquivo** | histórico nativo |
| **FR-T4-001** | **NÃO** — forward-only | `last_update` da API | só o que arquivarmos |
| **ES-T4-005** | **NÃO, e pior** — sobrescreve o trâmite | `Fecha` do export | **BASELINE_ESTABLISHED** |
| **ES-T4-004** | **NÃO** | data no cabeçalho do PDF | **duas versões arquivadas** |

**Demonstração ao vivo dos estados de versão.** O ZIP do RAIF trazia
`last-modified: 26/08/2026`, mais novo que o snapshot de `24/08`. Um verificador ingênuo
diria "versão nova". O hash do conteúdo é **idêntico** →
`NEW_VERSION_IDENTICAL`, e nenhum evento é emitido. Os cinco estados
(`BASELINE_ESTABLISHED`, `NO_NEW_VERSION`, `NEW_VERSION_IDENTICAL`,
`NEW_VERSION_CHANGED`, `SOURCE_FAILED`) têm teste que prova que nenhum colapsa no outro.

---

## 7 · CHANGE EVENTS — o que é operacionalmente detectável

Régua completa em `../regras/REGUA-DE-CHANGE-EVENT-EAME.md` §6.

| operacional hoje | `NOT ENOUGH VERSIONS` |
|---|---|
| `REFERENCE_NAME_CHANGE` (5 confirmados, verificação reprova 50% dos brutos) | `STATUS_CHANGE` |
| `NEW_COMMON_DENOMINATION` (156, não verificados um a um) | `HOLDER_CHANGE` |
| `REMOVED_COMMON_DENOMINATION` (30, idem) | `COMPOSITION_CHANGE` |
| `NEW_REGISTRATION` (83) | `DATE_CHANGE` |
| `REGISTRATION_LEFT_THE_LIST` (38) | `MANUFACTURER_CHANGE` |

**Os cinco da direita não faltam por método — faltam por tempo.** Existe **uma** versão
arquivada do export do ROPF. A segunda os destrava sem uma linha de código nova. E enquanto
houver uma só, a resposta a *"mudou o titular?"* é **`NOT ENOUGH VERSIONS`**, nunca
`NO_CHANGE`.

**Riscos de falso positivo, medidos e escritos:** `MANUFACTURER_CHANGE` é ALTO porque
`fabricante` é rótulo abreviado (`ADAMA Agri Sol`) e `fabrica` é razão social — comparar
campos trocados inventa mudança. `STATUS_CHANGE` é ALTO porque ler o **filtro** em vez do
**campo** inventaria 5 eventos por versão.

---

## 8 · REPRODUTIBILIDADE DOS HERO CASES

| | CASE-013 | CASE-014 | CASE-015 | CASE-008 |
|---|---|---|---|---|
| **SOURCE_DEPENDENCIES** | ES-T3-001 | FR-T4-001 · IT-T4-001 · EU-T4-001 | ES-T4-004 (2 versões) · ES-T4-005 | ES-T3-001 · EU-T2-001 |
| **REPRODUCIBLE_FROM_RAW?** | **SIM** | **SIM** (perna FR e IT em cadeia; a leitura de datas ainda não) | **SIM** | **PARCIAL** — o cruzamento clima×doença não está em cadeia |
| **AUTOMATIC / PARTIAL / MANUAL** | **AUTOMATIC** | **PARTIAL** | **AUTOMATIC** | **PARTIAL** |
| **NUMBER_OF_MANUAL_STEPS** | **0** | 0 na coleta; a comparação de datas é análise avulsa | **0** | 0 na coleta; o cruzamento é avulso |
| **FRAGILE_SOURCE?** | não — CKAN aberto, 20 anos de história | não | **SIM** — `ES-T4-005` é rota de aplicação | não |
| **FAILURE_MODE** | zero leituras levanta; "sem doença" nunca sai de "sem dado" | perna cai com `SOURCE FAILED`; **não** recalcular o total | rota 404 → o `CORE CLAIM` sobrevive como **histórico** (vive do `dc_web.pdf`, que é `/dam/`) | idem CASE-013 |
| **FRESHNESS_REQUIREMENT** | semanal na safra | semanal | semanal | nenhuma — é um caso histórico fechado |

**A divisão do CASE-015 feita na MISSÃO 07 paga aqui:** o `CORE CLAIM` não depende do
`regfiweb`; o `ADAMA-SPECIFIC CLAIM` depende. Se a rota cair, o hero vira histórico em vez
de morrer.

---

## 9 · CROSS-MARKET — chaves de recorrência

Para que uma reexecução futura consiga dizer o que mudou em vez de reemitir um total:

```
canonical molecule key    nome da substância normalizado (X-006) + CAS quando houver
national registration key FR: numero AMM · ES: numRegistro · IT: num_registrazione
ADAMA entity key          a ENTIDADE LEGAL (ADAMA FRANCE SAS · ADAMA Agriculture España
                          S.A. · a razão social italiana). NUNCA o grupo — o grupo é
                          dicionário nosso
country                   FR · ES · IT
source version            FR: last_update · ES: Fecha do export · IT: data no nome do
                          arquivo
```

A saída de uma reexecução tem de ser **por perna**:

```
FR changed · ES unchanged · IT source failed
```

e **nunca** `"protioconazol tem X produtos"` — um total agregado esconde qual perna falhou
e transforma uma fonte caída em queda de mercado.

---

## 10 · FRESHNESS DO ASK SINTONIA

O benchmark media verdade e recusa. Ganhou a terceira dimensão
(`scripts/ask_sintonia.py::FRESHNESS`):

| | n |
|---|---|
| `CURRENT` — depende da versão de hoje | **19** |
| `STRUCTURAL` — é sobre a regra, não sobre um valor | **14** |
| `HISTORICAL` — aponta para versão arquivada, **não envelhece** | **2** |
| exigem frescor (`SIM`) | 16 |
| não exigem (`NÃO`) | 13 |
| dependem | 6 |

**A recusa também envelhece.** Quatro recusas (`B08`, `B17`, `B19`, `B33`) deixam de ser
corretas quando a fonte abrir — foi exatamente o que aconteceu com `B03` e `B24` na
MISSÃO 07, quando a rota espanhola apareceu.

E a distinção que vira lei: *"quem é o titular?"* e *"quem era o titular na versão
arquivada?"* **não são a mesma pergunta**. A primeira é `CURRENT` e pode ficar velha; a
segunda é `HISTORICAL` e não fica.

---

## 11 · RED TEAM — tentando provar "congelada mas não operacional"

| ataque | resultado |
|---|---|
| **"há dependência manual escondida"** | **derrubado.** 0 passos manuais nas 4 cadeias. O último caiu nesta missão |
| **"o julgamento humano está disfarçado de dado"** | **procede em parte, e está declarado.** 5 passos de julgamento, cada um nomeado. O agrupamento empresarial é o mais consequente — por isso a contagem por entidade legal sai junto |
| **"endpoint frágil"** | **PROCEDE.** `ES-T4-005` é rota de aplicação sem compromisso de estabilidade e **sem fallback equivalente**. É a dependência declarada do veredito |
| **"parser silencioso"** | **derrubado.** 0 pedaços não interpretados no PDF canônico; cobertura é saída obrigatória; piso levanta |
| **"ausência de versão"** | **procede para 5 tipos de evento**, e está rotulado `NOT ENOUGH VERSIONS`, não `NO_CHANGE` |
| **"falso NO_CHANGE"** | **derrubado.** 5 estados distintos, com teste. O RAIF acabou de exercitar `NEW_VERSION_IDENTICAL` com dado real |
| **"current e historical confundidos"** | **derrubado.** `FACT_KIND` no benchmark, o trâmite do ROPF documentado como sobrescrito, e o próprio `TESTES_REAIS` da v1 separado do corrente |
| **"nome virando identidade"** | **derrubado.** Chave é sempre o registro. Testes: nome único hoje ≠ chave estável; `SORATEL` × `SORATEL MAX`; `AVASTEL` em três países com composições diferentes |
| **"falha de fonte virando zero"** | **derrubado.** Lista vazia é `FAILED`; `SOURCE_FAILED` ≠ `NO_NEW_VERSION`; cobertura zero levanta |
| **"cobertura silenciosa"** | **derrubado.** `TOTAL/RESOLVED/AMBIGUOUS/UNRESOLVED/COVERAGE` obrigatórios, e `AMBIGUOUS` não colapsa em nenhum dos outros dois |

**Dois ataques sobreviveram**, e nenhum é sobre a informação: são sobre a **rota espanhola**
e sobre a **falta de uma segunda versão do export**. O segundo se resolve sozinho com o
tempo, desde que o arquivamento esteja ligado.

---

## 12 · VEREDITO

```
PILOT_INFORMATION_BASE = FROZEN            (v1, 1e3f5bb — não reavaliado)
PILOT_UPDATEABILITY    = PROVED, com uma dependência declarada
```

**PROVED** porque: 4 de 4 cadeias reconstruídas do zero reproduzem os fatos congelados;
0 passos manuais; 11 formas de degradação falham fechado e nenhuma produz número errado;
os estados de versão não colapsam; a divergência que estava em aberto tem regra verificada
por igualdade de conjunto; e a cobertura é saída obrigatória com piso que interrompe.

**A dependência declarada:** `ES-T4-005` não tem fallback equivalente
(`FALHA-DE-FONTE-ESPANHA.md`). Se a rota cair, a Espanha vira **histórico datado** — o
`CORE CLAIM` do CASE-015 sobrevive, o `ADAMA-SPECIFIC CLAIM` para de envelhecer, e o
cross-market vira 2/3 + 1 congelado. **Isso não impede operar; impede prometer.**

**Não é SLA.** *"Verificar semanalmente"* não é *"garantimos atualização semanal"*.
`PRODUCT SLA` continua sendo decisão futura — ver `CONTRATO-DE-ATUALIZACAO-DO-PILOTO.md`.

---

## 13 · MENOR PRÓXIMO PASSO

**Podemos ir ao Claude Design.** A base está congelada e agora se sabe mantê-la.

Nenhum erro obriga v2: o único `FREEZE_V1_FINDING` (o critério italiano) é de **forma**,
não de valor, e o número que o piloto usa — ADAMA com 5 produtos — é o mesmo nos dois
critérios.

O menor passo que aumenta mais a confiança **não é uma missão**: é **arquivar a segunda
versão do export do ROPF e do `dc_web.pdf`**. Uma coleta semanal, sem código novo,
destrava cinco tipos de change event e tira a Espanha de `BASELINE_ESTABLISHED`.
