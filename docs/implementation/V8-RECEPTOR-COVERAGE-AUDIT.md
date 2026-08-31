# V8 · AUDITORIA DE COBERTURA DE RECEPTORES — SINTONIA EAME

> ⚠️ **ESTE DOCUMENTO MEDE O `index (10)` — o casco ANTES do patch de recepção.**
> A medição corrente está em
> [V8-RECEPTOR-REAUDIT-INDEX11.md](V8-RECEPTOR-REAUDIT-INDEX11.md).
> Ele fica no repositório porque é a prova do "antes": sem ele, não há como
> mostrar que o patch mudou alguma coisa.

**Data:** 2026-08-31 · artefatos executáveis em `data/implementation/`

```
REAL_DATA_WIRED = NO      COLLECTION_EXECUTED = NO      INTELLIGENCE_CHANGED = NO
CASCO_V7_MODIFIED = NO    CASCO_V8_MODIFIED = NO        V8_IMPLEMENTATION_STARTED = NO
```

> **O que esta rodada fez:** escreveu o contrato de recepção das nove mangueiras e mediu o
> casco contra ele. **O que não fez:** ligar dado, coletar, mudar inteligência ou desenhar.

---

## 0 · O CASCO QUE FOI AUDITADO

O casco V8 **não veio anexado** à mensagem. Localizei em `Downloads` por data e tamanho e
confirmei pela lista de telas.

```
arquivo ......... index (10).html · 2026-08-31 02:19 · 1.451.775 bytes
sha-256 ......... 8905fcb5dac7d8854ad661f60ba83d7f029ca3bd7cbf44ac925c3efce1d3eaf5
index (9).html .. MESMO SHA-256 — um arquivo baixado duas vezes, não duas versões
telas ........... home · radar · obj · acervo · fontes · relatorios · eame · lib · config
```

**É o V8:** `casos`, `caso`, `futuro`, `calendario` e `analises` sumiram; `radar` e `obj`
entraram. É exatamente a arbitragem — três superfícies absorvidas e Object Detail modular.

O casco vivia **só na pasta Downloads**. Copiei para
`casco/canonical/SINTONIA-EAME-V8-RECEPTOR-CANDIDATE.html`, byte a byte, e há teste que
confere tamanho e SHA-256. Sem isso, esta auditoria seria uma opinião sobre um arquivo que
ninguém mais consegue abrir. **O V7 continua testemunha** — não foi tocado.

---

## 1 · O VEREDITO EM UMA LINHA

**O casco acerta a lei e erra o campo.**

Os cinco componentes novos — convergência, timeline, mapa de culturas, mapa de ações,
gaveta de evidência — dizem a coisa certa na tela. Nenhum tem onde receber o dado que
diria. Um rótulo não é um campo: `PROVENIÊNCIA: "hash / commit — slot"` é uma frase, e o
adapter não tem onde escrever o commit.

**Nenhum redesenho é pedido.** O que falta é campo, não pixel.

---

## 2 · AS NOVE MANGUEIRAS

| # | receptor | contrato | casco | o que falta |
|---|---|---|---|---|
| **H1** | TERRITORIAL_OBSERVATION | ✅ completo | **PARCIAL** | `meta[]` é array de rótulos: não há onde escrever CROP |
| **H2** | REGISTRATION_DEADLINE | ✅ completo | **PARCIAL** | composição modular certa, sem campo para o número do registro |
| **H3** | COMPETITOR_IDENTITY_CHAIN | ✅ completo | **PARCIAL** | os três elos existem; falta o campo de concordância titular·país |
| **H4** | OBSERVED_PAID_ACTIVITY | ✅ completo | **PARCIAL** | uma linha sem `EVIDENCE_ID` — a gaveta não abre o anúncio |
| **H5** | FIELD_PRESSURE_SERIES | ✅ completo | **PARCIAL** | `fieldStats` só sabe dizer que não sabe; não recebe `READINGS[]` |
| **H6** | CREATOR_ENTITY | ✅ completo | **PARCIAL** | separação pessoa/negócio preservada; `ENTRY_PATH` não existe |
| **H7** | SCIENTIFIC_PERSON | ✅ completo | **PARCIAL** | o portão é **frase**, não campo — e a lista mora no Radar |
| **H8** | COMPANY_LOCAL_ACCOUNT | ✅ completo | **AUSENTE** | nenhuma chave. As 22 contas resolvidas não têm para onde ir |
| **H9** | TEXT_CONTENT | ✅ completo | **AUSENTE COMO RECEPTOR** | `UI_LANGUAGE` funciona; as outras quatro línguas não existem |

```
CONTRATO DECLARADO ................ 9 / 9
CASCO IMPLEMENTA .................. 0 / 9
```

**Os dois números são diferentes e não se trocam um pelo outro.** Escrever o contrato é o
produto desta rodada; ter o receptor é o produto da próxima.

---

## 3 · OS TRÊS SUBRECEPTORES QUE NÃO PODEM SUMIR

Estes são os que desaparecem quando alguém "resolve" roteando para a mangueira parecida.

### `SCIENCE_PUBLICATION_EVIDENCE` — **AUSENTE**

`SCIENTIFIC_PERSON ≠ SCIENTIFIC_PUBLICATION`. **H7 não é a resposta automática para
"Ciência".** Uma pessoa não é um trabalho.

No casco existe a palavra *Ciência* como camada com estado (`EM COLETA`) e como dimensão do
caso. É um chip. **Não existe onde entregar uma publicação** — título, data, veículo,
autores, revisão por pares.

> Se este subreceptor não for criado, alguém liga H7 aqui e o portal passa a dizer que há
> ciência por trás de um caso **porque encontrou um pesquisador**.

### `LOCAL_ADAMA_PORTFOLIO_CONTEXT` — **AUSENTE**

`REGISTRATION_DEADLINE ≠ LOCAL_ADAMA_PORTFOLIO_CONTEXT`. **H2 não é a resposta automática
para "Portfólio".** H2 carrega o prazo de **um** registro — de **qualquer** titular,
inclusive de concorrente. *"A ADAMA tem resposta registrada para este alvo neste país?"* é
outra pergunta, com outra fonte e outro dono.

No casco: `Portfólio local ADAMA` é um chip (`NÃO PROVADO`) e uma frase de ação. A pergunta
está na tela; a resposta não tem onde chegar.

> Se este subreceptor não for criado, alguém liga H2 aqui e o portal passa a dizer que a
> ADAMA tem produto **porque um registro qualquer tem prazo**.

### `FIELD_VOICE_OBSERVED` — **AUSENTE**

`voices[]` tem a **entidade** — e a separação `PERSON CREATOR` / `FARM BUSINESS` está
visível na interface, com nota GDPR. Isso é o mais difícil e está certo.

Falta a **observação**: o que a pessoa disse, quando, sobre que cultura e região, no idioma
original. **Nome não é sinal.**

---

## 4 · OS CINCO COMPONENTES JÁ DESENHADOS

| componente | semântica | campos | pior lacuna |
|---|---|---|---|
| **CONVERGENCE** | ✅ certa | 0 de 5 ids | `DEPENDENCY_RELATION` não existe |
| **OBJECT_TIMELINE** | ✅ certa | 3 de 8 | sem `EVENT_AT` em ISO, sem `STATE_BEFORE`/`AFTER` |
| **CROP_INTELLIGENCE_MAP** | ✅ certa | 0 de 8 por ponto | é coroplética de país; não recebe objeto num lugar |
| **ACTION_MAP** | ✅ certa | 3 de 6 | `EVIDENCE_BASIS` — nada impede ação sem evidência |
| **EVIDENCE_DRAWER** | ✅ certa | 7 rótulos fixos | é **global**: abre igual venha de que objeto vier |

### 4.1 · A pior lacuna do produto inteiro: `DEPENDENCY_RELATION`

A convergência acerta a lei. Diz que single signal é legítimo. Separa alinhamento
contextual. Deriva a contagem de famílias em vez de digitá-la. Tudo certo.

**E não tem campo para dizer que duas pernas dependem uma da outra.**

As duas dependências medidas do produto ficam invisíveis:

```
H3 → H4    DERIVATION_DEPENDENCY    a perna Meta da cadeia É o anúncio da Meta
H5 → H1    SOURCE_DEPENDENCY        o RAIF é publicador dos dois lados
```

Sem esse campo, duas pernas que são **a mesma evidência vista de outro ângulo** vão
renderizar como `MULTI SIGNAL`. **Foi exatamente esse o erro que o refresh encontrou:**
cinco das seis convergências da V1 eram a mesma evidência.

### 4.2 · A gaveta não rastreia mangueira nenhuma

`EVIDENCE_DRAWER_TRACES_ALL_HOSES = NO`. Três bloqueios, todos medidos:

**1 · É global, não por objeto.** `openDrawer` e `o.evidence` fazem a mesma coisa:

```js
openDrawer: () => this.set({ drawerOpen: true })
```

Nenhum id é passado. `drawerClaim` e `drawerFields` são chaves de topo. A gaveta abre com o
mesmo conteúdo sempre.

**2 · Proveniência é uma string.** Um campo de texto com `"hash / commit — slot"`. Sem
discriminador de backend, sem repositório/caminho/commit, sem schema/tabela/chave/snapshot.

**3 · O multilíngue não está ligado.** Os rótulos `TRECHO ORIGINAL` e `IDIOMA DA FONTE` não
têm valor ligado; o corpo é um parágrafo estático de política. E os botões **"Ver original"
e "Mostrar tradução" não têm handler** — nenhum `sc-camel-on-click`. São botões desenhados,
com cursor de clique e sem ação.

> É a mesma classe de defeito do *ranking de recorrência* do V7: parece vivo e não está
> ligado. Há teste que reprova se a gaveta ganhar handler novo sem a medição ser refeita.

---

## 5 · O ENVELOPE: UM RECEPTOR, DOIS BACKENDS

**Não existe "receptor GitHub" e "receptor Supabase".** Existe **um** receptor canônico. O
adapter decide de onde veio; a UI renderiza igual.

```
SOURCE_BACKEND = GITHUB    → REPOSITORY · PATH · COMMIT_SHA · HASH · SOURCE_ID · AS_OF_DATE
SOURCE_BACKEND = SUPABASE  → SCHEMA · TABLE_OR_VIEW · PRIMARY_KEY · SNAPSHOT_ID
                             CAPTURED_AT · SOURCE_ID · AS_OF_DATE
```

**Leitura no GitHub é sempre por commit fixo.** Uma branch se move e responde diferente a
cada hora sem ninguém ter mudado nada.

**Segurança:** `SERVICE_ROLE_KEY`, secret e token **nunca** no frontend. O casco recebe
entidade canônica já resolvida; credencial não atravessa receptor. Há teste que varre os
bytes do casco — hoje ele não carrega nenhum segredo.

### Os oito estados de carga

```
UNWIRED · LOADING · READY · EMPTY_VALID · NOT_STARTED · NOT_AVAILABLE · BLOCKED · ERROR_FAIL_CLOSED
```

**Estado de transporte nunca vira dado.** Lista vazia por falta de ligação e lista vazia por
resultado legítimo **não podem renderizar igual**. Erro de rede nunca vira *"não há
evidência"*.

**O casco hoje tem dois estados, não oito:** `hasObjects`/`noObjects`,
`hasChanges`/`noChanges`, `hasKnown`/`noKnown`, `objHasHistory`/`objNoHistory`. Cheio ou
vazio. É por isso que H8 não consegue existir: `NOT_STARTED` não tem como ser dito.

---

## 6 · ÓRFÃS

```
SAÍDAS INVENTARIADAS ............................. 35
ORPHAN_CANONICAL_INTELLIGENCE_OUTPUTS ............  0
SAÍDAS CUJO RECEPTOR ESTÁ AUSENTE NO CASCO ....... 10
RECEPTORES AUSENTES ..............................  6
```

**Dez saídas apontam para seis receptores.** São unidades diferentes e nunca se somam —
várias saídas dividem o mesmo receptor faltante. É a mesma disciplina de `ROW ≠ ENTITY`.

Nenhuma saída canônica ficou sem destino declarado. As cinco classificadas como
`NOT_CANONICAL` são sobre o **processo** — benchmark, auditoria de coleta, manifesto de
execução, contrato de escopo — e cada uma diz o motivo.

> Reclassificar algo inconveniente como não canônico para chegar a zero seria fraude de
> auditoria. Os números acima são derivados por `scripts/v8_receptor_audit.py`; nenhum foi
> digitado, e há teste que confere.

Os seis receptores ausentes: **H8**, **H9**, `SCIENCE_PUBLICATION`, `LOCAL_ADAMA_PORTFOLIO`,
`FIELD_VOICE_OBSERVED` e `DEPENDENCY_RELATION` na convergência.

---

## 7 · DOIS DESVIOS DE SUPERFÍCIE

**`experts` renderiza no Radar.** A arbitragem coloca a camada Pessoas dentro do
`PHENOMENON_CASE`. No Radar a lista aparece **fora de qualquer objeto** — e um portão por
objeto não tem onde ser exercido. `ISSUE_EXPERTISE_PROVED` não pode bloquear nada se não há
objeto ao qual a expertise se refira.

**`objHistory` e `timeline` são duas listas para a mesma coisa.** `objHistory` está vazia e
`timeline` está preenchida. É pergunta de design, não bloqueio de receptor — anotada, não
cobrada.

---

## 8 · O QUE ESTÁ CERTO E NÃO DEVE SER MEXIDO

Vale registrar, porque a próxima rodada vai mexer no arquivo:

- **Composição modular por tipo.** Um vencimento regulatório não finge ter camada de
  Ciência. `NOT_APPLICABLE` não aparece como lacuna.
- **`PERSON_CREATOR ≠ FARM_BUSINESS`** visível na interface, sem número somado.
- **Vazio temporal como evento** na timeline, com trilho tracejado.
- **`mapHoles`** — o mapa declara que não tem geometria, que nenhum objeto tem coordenada
  provada, e que não pode dizer onde não olhamos. Nada pintado por estimativa.
- **Localidade da fonte ≠ localidade do fato**, com a explicação dentro da própria gaveta.
- **Single signal legítimo** e alinhamento contextual que não soma.
- **`SEM AÇÃO DEFENSÁVEL AINDA`** para as três áreas comerciais, e acento verde só em
  Market Development.
- **Latência de pipeline: `NÃO MEDIDA`** — sem instrumentação não existe zero.

---

## 9 · PROVAS

`tests/test_v8_receptors.py` — **49 provas**, dentro das
<!--M:TEST_COUNT_CURRENT-->786<!--/M--> da suíte, 0 falhas.

Duas coisas diferentes, que nunca se misturam:

1. **O contrato está completo?** Cada receptor declara os onze campos, os guards, os estados
   de carga, os dois backends e a falha fechada. Isto passa hoje.
2. **A medição é honesta?** Cada afirmação `CASCO_MEASURED` é conferida contra os bytes. Se
   alguém escrever que H8 existe, o teste abre o arquivo e reprova. Se apagar um bloqueador
   para o relatório ficar bonito, reprova.

**O que os testes não fazem: aprovar o casco.**

### Um erro meu que os testes pegaram

Escrevi uma prova que procurava os oito estados de carga como substring no markup. Ela
reprovou: `READY` casa dentro de `ATTENTION READY`, que é estado de **atenção**, não de
transporte. Confundir menção com uso — o mesmo erro que já cometi com a palavra *apify*.
Corrigido para procurar só os nomes que não colidem, com o motivo escrito no teste.

E escrevi outra que fatiava a tela `radar` pela primeira ocorrência de `at.radar` — que é o
**botão do menu**, não a tela. Corrigido em `fatiar_por_tela()`, com a armadilha documentada.

---

## 10 · SAÍDA

```
HOSES_TOTAL ........................... 9
HOSES_WITH_COMPLETE_RECEIVER .......... 0     (contrato declarado: 9/9)

H1 .................................... PARTIAL
H2 .................................... PARTIAL
H3 .................................... PARTIAL
H4 .................................... PARTIAL
H5 .................................... PARTIAL
H6 .................................... PARTIAL
H7 .................................... PARTIAL
H8 .................................... ABSENT
H9 .................................... ABSENT_AS_RECEPTOR

SCIENCE_PUBLICATION_ROUTE ............. ABSENT — e NÃO deve ser roteada para H7
LOCAL_ADAMA_PORTFOLIO_ROUTE ........... ABSENT — e NÃO deve ser roteada para H2
FIELD_VOICE_ROUTE ..................... ABSENT — entidade existe, observação não

GITHUB_PROVENANCE_CONTRACT ............ DECLARED / NOT_IMPLEMENTED_IN_CASCO
SUPABASE_PROVENANCE_CONTRACT .......... DECLARED / NOT_IMPLEMENTED_IN_CASCO

CONVERGENCE_COMPONENT_RECEPTOR ........ PARTIAL — falta DEPENDENCY_RELATION
TIMELINE_COMPONENT_RECEPTOR ........... PARTIAL — 3 de 8 campos
CROP_MAP_COMPONENT_RECEPTOR ........... PARTIAL — resolução de país apenas
ACTION_MAP_COMPONENT_RECEPTOR ......... PARTIAL — falta EVIDENCE_BASIS
EVIDENCE_DRAWER_RECEPTOR .............. PARTIAL — global, não rastreia H1–H9

ORPHAN_CANONICAL_INTELLIGENCE_OUTPUTS . 0
OUTPUTS_WITH_ABSENT_RECEPTOR .......... 10  (em 6 receptores — unidades distintas)

DESIGN_PATCH_REQUIRED ................. YES
CASCO_RECEPTOR_READY .................. NO
READY_TO_WIRE_REAL_DATA ............... NO
```

### `EXACT_BLOCKERS`

```
1  envelope de carga ausente: 8 estados exigidos, 2 disponíveis (cheio / vazio)
2  envelope de proveniência ausente: PROVENIÊNCIA é uma string, não um registro
3  gaveta global: openDrawer não recebe id — nenhuma mangueira é rastreável
4  H8 sem receptor: NOT_STARTED não tem como ser dito
5  H9 sem receptor de conteúdo: sem SOURCE_LANGUAGE, ORIGINAL_TEXT, TRANSLATION_PROVENANCE
6  botões "Ver original" e "Mostrar tradução" sem handler
7  SCIENCE_PUBLICATION sem receptor — só um chip chamado Ciência
8  LOCAL_ADAMA_PORTFOLIO sem receptor — só um chip e uma frase
9  FIELD_VOICE_OBSERVED sem receptor — entidade sem observação
10 DEPENDENCY_RELATION ausente na convergência
11 nenhum objeto carrega OBJECT_ID — nada pode ser referenciado
12 experts renderiza no Radar, fora de qualquer objeto
```

**Nenhum dos doze é redesenho.** Os doze são campo, estado ou handler.

O patch está em [V8-DESIGN-RECEPTOR-PATCH.md](V8-DESIGN-RECEPTOR-PATCH.md).
