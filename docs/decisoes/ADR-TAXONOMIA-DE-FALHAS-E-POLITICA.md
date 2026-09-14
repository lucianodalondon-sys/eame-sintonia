# ADR — TAXONOMIA CANÔNICA DE FALHAS E CORREÇÃO DA POLÍTICA DE SESSÃO

**Data:** 2026-09-08 · **Estado:** IMPLEMENTADO
**Base:** `docs/decisoes/ADR-SINTONIA-SCRAP-EVOLUTION.md` (ADR-02, ADR-12)

---

## 1 · O QUE FOI MEDIDO ANTES DE INTEGRAR

Os hashes informados na missão foram conferidos, não aceitos.

| O quê | Commit medido |
|---|---|
| SCRAP social composto | `cf3aec60` — já estava na minha branch |
| Estudo profundo (5 documentos) | `1770f0b5` + **`34702814`** (são **dois** commits, não um) |
| LOCAL_SESSION | **`946107d4`** — hash informado **confere** |
| `merge-base` do LOCAL_SESSION com a minha HEAD | `cf3aec60` — divergência de **1 commit**, integração limpa |

**Uma branch que a missão não citou e que precisa ser dita:**
`origin/claude/sintonia-eame-repo-setup-xccfob` (`c88690ca`) menciona
"Sintonia Scrap vê YouTube de graça" no assunto e parece relevante — **mas
`git merge-base` com a nossa HEAD é VAZIO: são histórias não relacionadas.**
1.104 arquivos e 982 mil linhas de diferença. **DO_NOT_INTEGRATE nesta missão** —
integrar histórias sem ancestral comum no escuro era exatamente o risco que a
missão mandou não correr.

---

## 2 · QUADRO DE INTEGRAÇÃO DO `946107d4`

| Peça | Veredito | Razão |
|---|---|---|
| `social_sessao.preflight()` | **KEEP** | fato técnico sobre esta máquina, e é isso que ele diz ser |
| `SESSION_MISSING` · `SESSION_EXPIRED` · `MFA_REQUIRED` · `LOGIN_REQUIRED` | **KEEP** | distinções materiais, todas absorvidas pela taxonomia |
| `classificar_pagina()` | **KEEP** | muro de login ≠ MFA ≠ bloqueio é distinção cara e correta |
| `SINTONIA_BROWSER_PROFILE_DIR` + `_dentro_do_repo()` | **KEEP** | perfil fora do repositório, verificado por teste |
| `social_guarda.py` (guarda de segredo) | **KEEP** | e **pegou defeito meu** nesta missão — ver §6 |
| Runner local no workflow | **KEEP** | |
| `POLITICA` com cláusula + fonte por plataforma | **KEEP** | negar citando o contrato é o padrão certo |
| `redigir()` | **KEEP_WITH_CHANGE** | tinha brecha real — ver §6 |
| `automacao_permitida(platform, ownership)` | **KEEP_WITH_CHANGE** | assinatura sem capacidade nem rota; reescrita sobre `usabilidade()` |
| `OWN_PROPERTY → True` nas sete | **CORRIGIDO** | ver §3 |
| `CLAUSULA` misturando robots e termos | **CORRIGIDO** | `ROBOTS_STATUS` ≠ `TERMS_STATUS` |
| `AVAILABLE` no raio-X para LOCAL_SESSION | **CORRIGIDO** | `AVAILABLE` ≠ `USABLE` |
| `test_conta_propria_e_permitida` | **CORRIGIDO** | canonizava a simplificação; agora afirma o contrário |

---

## 3 · A CORREÇÃO DE SEMÂNTICA

A versão anterior decidia com **um eixo só**: de quem é a conta.
Isso acerta o caso perigoso e **erra dos dois lados**:

- **erra para menos** — `THIRD_PARTY` não é proibido em si. Ler comentário de canal
  alheio pela Data API oficial do YouTube, com chave, é o uso para o qual a API
  existe. A recusa valia para a **sessão**, e a doutrina generalizou para tudo.
- **erra para mais** — `OWN_PROPERTY` não é autorização automática. Os Termos §3 do
  YouTube proíbem *"any automated means"* e **não abrem exceção ao dono do canal**.
  Pior: a nota `OWN_NOTA` de cada uma das sete plataformas **já mandava usar a API
  oficial** para conta própria. **O valor dizia SIM enquanto a nota ao lado dizia
  "não por aqui".**

```
AUTH É MODO DE ENTRAR. NÃO É PERMISSÃO DE AUTOMATIZAR.
ROBOTS NÃO É TERMS.
SESSION_AVAILABLE NÃO É AUTHORIZATION_ALLOWED.
OWN_PROPERTY NÃO É AUTOMATION_ALLOWED.
```

A pergunta certa nunca é "posso usar o Instagram?". É:

    (PLATAFORMA, CAPACIDADE, ROTA, DE QUEM É A CONTA) -> posso?

**Uma estrutura de dados, seis campos, um veredito — não seis motores.**
`social_sessao.usabilidade()` devolve `TECHNICAL_STATUS`, `ROBOTS_STATUS`,
`TERMS_STATUS`, `AUTH_STATUS`, `AUTHORIZATION_STATUS` e `ROUTE_STATUS`.

`AUTH_STATUS` e `AUTHORIZATION_STATUS` são colunas **separadas de propósito**:
ter a sessão aberta é fato sobre esta máquina; poder automatizá-la é fato sobre o
contrato. Quando as duas moram na mesma variável, a primeira decide — **e foi assim
que "estou logado" virou "posso".**

### O exemplo da missão, executando

```
YOUTUBE · FETCH_COMMENTS · OFFICIAL_API   · THIRD_PARTY  -> USABLE
YOUTUBE · FETCH_COMMENTS · LOCAL_SESSION  · THIRD_PARTY  -> NOT_USABLE
YOUTUBE · FETCH_POST     · LOCAL_SESSION  · OWN_PROPERTY -> NEEDS_REVIEW
```

**`NEEDS_REVIEW`, não `ALLOWED`.** Nenhuma das sete cláusulas lidas abre exceção
escrita ao dono. Afirmar `ALLOWED` seria inventar uma permissão que ninguém leu —
e `automacao_permitida()` **não deixa `NEEDS_REVIEW` passar: revisão pendente não é
licença.**

### `ROBOTS_STATUS` não é decorado

`robots.txt` governa **robô anônimo sobre HTTP**. Para API contratada e para sessão
de gente ele sai `NOT_APPLICABLE` — aplicar a regra errada seria tão errado quanto
não aplicar nenhuma. Para rota pública sai **`UNKNOWN`**, porque quem lê o robots é
`social_rotas.permitido()`, **na hora, com o User-agent real**. Decorar no código o
que precisa ser lido no host é o defeito que aquele portão existe para impedir.

---

## 4 · A TAXONOMIA CANÔNICA — `scripts/falhas.py`

**21 estados. 49 nomes antigos mapeados.** É o menor vocabulário que preserva as
diferenças que os módulos desta casa **já faziam** — cada estado carrega, no campo
`absorve`, o nome antigo que substitui, para que a migração seja conferível.

```
ERRO NÃO É ZERO.  ·  BLOCKED NÃO É EMPTY.
AUTH EXPIRED NÃO É NO CONTENT.  ·  PARSER QUEBRADO NÃO É FONTE VAZIA.
ROTA CAÍDA NÃO É FONTE CAÍDA.
```

### As três camadas

| Camada | Quem quebrou | Exemplo medido |
|---|---|---|
| `SOURCE` | a fonte | 5xx, alvo removido |
| `ROUTE` | o caminho até ela | quota, sessão vencida, termo proíbe |
| `EXECUTOR` | **a nossa ferramenta** | Chrome não subiu, **parser quebrou** |

`degrada_fonte()` devolve `True` **só** para a camada `SOURCE`. É a função que
impede a casa de publicar um zero que não mediu nada.

### A flag `esperado`

`esperado=False` só para defeito **nosso** — `PARSER_DRIFT`, `CONTRACT_DRIFT`,
`EXECUTOR_UNAVAILABLE`, `PERMANENT_HTTP_ERROR`, `ITEM_ERROR`, `UNKNOWN_ERROR`.
É a única classe que pede pessoa. O resto é notícia do mundo e sai no relatório.

### Duas decisões que a medição corrigiu

1. **`QUOTA_EXHAUSTED` ≠ `BUDGET_EXHAUSTED`.** Colapsei os dois na primeira versão,
   e o teste de coerência contra a regra de rotação da rota paga reprovou:
   `TOKEN_EXHAUSTED` **rotaciona** (outra chave do pool pode ter cota), enquanto uma
   recusa de gasto da casa **não**. Trocar de chave não resolve uma decisão nossa.
2. **`PLATFORM_FAILURE` → `UNKNOWN_ERROR`.** O nome antigo **acusava a plataforma sem
   prova**. `NÃO SEI` é mais honesto que culpar a fonte — e `degrada_fonte()` devolve
   `False`, como tem de ser.

### O balde `FAILED` foi desmontado

Em `social_rotas`, `except Exception → 'FAILED'` cobria transporte, parser e 4xx
no mesmo nome. Agora:

| Exceção | Estado | Camada |
|---|---|---|
| `HTTPError` | por código (`falhas.classificar`) | conforme |
| `URLError`, `TimeoutError`, `ConnectionError` | `TRANSIENT_NETWORK_ERROR` | `ROUTE` |
| `KeyError`, `IndexError`, `AttributeError`, `TypeError`, `ValueError` | **`PARSER_DRIFT`** | **`EXECUTOR`** |
| resto | `UNKNOWN_ERROR` | `EXECUTOR` |

O selo é aplicado **envolvendo** `executar()`, não em cada `return` — um `return`
novo daqui a três meses esqueceria de selar. Envolver é a única forma que não
depende de alguém lembrar.

---

## 5 · REUSO DAS PEÇAS ÓRFÃS

| Peça | Veredito | Prova |
|---|---|---|
| `coleta_checkpoint.py` | **COMPATIBLE** | `coletar()` recebe `trabalho(unidade, token) -> (itens, estado)`; o `estado` é livre e a taxonomia entra como está. Nenhuma linha alterada |
| `source_health.py` | **NEEDS_ADAPTER** (feito, 12 linhas, fora dele) | ver abaixo |

**A armadilha que o adapter evita.** `source_health.version_state(fetch_ok=...)`
devolve `SOURCE_FAILED` quando `fetch_ok` é falso. Passar qualquer falha para lá
faria **sessão vencida, quota esgotada e parser quebrado virarem "a fonte falhou"** —
exatamente o erro que esta taxonomia existe para impedir.

`falhas.pode_julgar_a_fonte()` responde antes: **só quem olhou a fonte pode opinar
sobre ela.** Quando devolve `False`, `version_state` **não é chamado** e a saúde da
fonte fica `UNKNOWN` — que é a resposta certa.

`source_health.py` **não foi tocado.**

---

## 6 · O QUE A INTEGRAÇÃO PEGOU DE DEFEITO REAL

1. **Brecha em `redigir()`.** `social_sessao._SEGREDOS` casava só `rótulo=valor`, e
   `token` **não estava na lista de rótulos**. Um `apify_api_…` solto dentro de uma
   URL de traceback **passava inteiro** — e essa função é a que `social_rotas` usa em
   **toda** exceção. Acrescentado `_SEGREDOS_POR_FORMA` (token da Apify, JWT, token do
   GitHub, chave do Google): **redigir por rótulo não basta, o valor também tem forma.**
2. **O guarda de segredo reprovou um documento meu.** `SINTONIA-SCRAP-EVOLUTION-PLAN.md`
   continha um padrão de caminho pessoal Windows em prosa. **Corrigi o texto, não o
   guarda** — guarda que a gente afrouxa para passar deixa de ser guarda.
3. **Um teste que canonizava o defeito.** `test_conta_propria_e_permitida` afirmava
   `OWN_PROPERTY → True`. Foi reescrito para afirmar o contrário, com o motivo no corpo.

---

## 7 · BASELINE

Medido **antes** de qualquer alteração e **depois**:

| | PASS | FAIL |
|---|---|---|
| Antes | 26 | 4 — `adama_es_gate`, `comunicacao`, `evidence`, `handoff` |
| Depois | **28** | **4 — as mesmas quatro** |

```
NEW_FAILURES = 0
```

As quatro falhas são **herdadas** e estão fora do escopo desta missão. Não foram
tocadas. `tests/test_falhas.py` acrescenta **38 testes de propriedade**, todos verdes.

---

## 8 · O QUE ESTA MISSÃO NÃO FEZ

Nenhuma dependência nova. Crawlee **não** instalado. Nenhuma plataforma nova.
Nenhum coletor reescrito. Os três dicts `ATORES` **não** foram migrados — o dono
futuro está identificado (`social_matriz.MATRIZ`, que já tem a forma certa:
plataforma × capacidade × lista de rotas com classe, permissão, estado, custo e
evidência), e a migração é missão própria.
