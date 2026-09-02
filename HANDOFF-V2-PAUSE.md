# SINTONIA V2 · PAUSED HANDOFF

> **Leia este arquivo inteiro antes de tocar em qualquer coisa.** Ele existe para
> que outra sessão do Claude Code, **com acesso apenas a este repositório**,
> continue exatamente daqui — sem a conversa anterior, sem memória de agente, sem
> contexto escondido.

Pausado em **2026-09-02**.

---

## 1. MISSION

**SINTONIA ITALY PILOT** — ferramenta de inteligência **externa** sobre o mercado
agrícola italiano, para a ADAMA (multinacional de defensivos).

A missão corrente é a **REALITY HANDOFF V2.1 · TRUE UNIFIED DESIGN INGEST**:
transformar o material bruto (handoff anterior + coleta *last-mile*) num pacote
único que o time de Design consiga carregar sem adivinhar nada.

O V2 foi **recusado** com quatro defeitos nomeados:

1. handoff anterior e last-mile empacotados lado a lado, **sem índice comum**;
2. `TOP-CROSSINGS` com **junção falsa** — cultura casada por texto livre;
3. datasets operacionais **granulares descartados** (2.945 linhas do ISTAT viraram
   33 frases-resumo);
4. papel de trabalho (demo, auditoria, quarentena) **misturado com o dado**.

Depois, o usuário acrescentou uma exigência: **o Design nunca pode precisar
mostrar prosa de pesquisa em português**. Campos interpretativos client-safe
precisam de `_IT` e `_EN`, com `_ORIGINAL_RESEARCH_TEXT` preservado ao lado — e
**sem** acrescentar fato, fortalecer alegação, mudar escopo geográfico, mudar
confiança ou remover incerteza. Citação pública **permanece na língua original**.

---

## 2. WHY IT WAS PAUSED

Pausado **de propósito**, para preservar o limite de uso desta conta Claude. O
trabalho continua em outra conta.

**A missão não falhou.** O pacote está construído, medido e todos os contadores
de aceitação estão limpos. O que falta está descrito no §5 e no §12.

---

## 3. EXACT GIT STATE

| | |
|---|---|
| repositório | `C:\eame-sintonia` |
| remoto | `https://github.com/lucianodalondon-sys/eame-sintonia.git` |
| **branch desta missão** | **`claude/italy-v2-handoff`** ← use esta |
| criada a partir de | `claude/eame-competitor-public-communication` @ `21c8ec7` |
| HEAD do checkpoint de documentação | `00914816162f013566944b281079a28415bbc687` |
| HEAD final da branch | rode `git rev-parse origin/claude/italy-v2-handoff` |
| estado | empurrada para o remoto; local == remoto verificado |

### Por que uma branch dedicada

A branch de origem é usada **ao mesmo tempo** por outra sessão do Claude, que
cuida do **PORTAL/SITE**. Empurrar o V2 nela misturaria duas missões que precisam
ser integradas com calma, e não por acidente.

> **A branch do site não foi tocada.** Nada de merge, nada de reset, nada de push
> por cima.

### ⚠️ ESTA PASTA É COMPARTILHADA COM OUTRA SESSÃO

`C:\eame-sintonia` é um *worktree* usado por **mais de uma sessão do Claude ao
mesmo tempo**. Durante esta sessão a branch mudou sozinha: começou em
`383e4d2` e chegou a `21c8ec7`, com quatro commits que **não são meus**:

```
21c8ec7 a area de rascunho do splice sai do alcance do git
14747f4 o modelo passa a ser a fronteira unica, e some a fixture de dentro dele
9eb598a o portal italiano entra no repositorio com a regua que mede ele
34fef19 o portao de verdade: 34 quedas resolvidas, e a taxa real era pior do que a missao dizia
```

> **Antes de qualquer commit, rode `git status` e confira o que é seu.** Há
> arquivos modificados de outra frente de trabalho (`italia-portale/`,
> `scripts/instagram_*`, `tests/test_adama_es_gate.py`) que **não devem entrar**
> num commit desta missão.

Há 15 worktrees ativos no disco (`git worktree list`), um por frente de trabalho.

---

## 4. WHAT WAS COMPLETED

Todos os números abaixo saíram de `build/ITALY-REALITY-HANDOFF-V2.1/ACCEPTANCE-REPORT.json`,
que é **recontado dos arquivos a cada build**. Nenhum foi lembrado de cabeça.

### 4.1 · O pacote V2.1

| Artefato | Estado |
|---|---|
| `build/SINTONIA-ITALY-REALITY-HANDOFF-V2.1.zip` (2,0 MB, 153 arquivos) | ✅ **commitado** |
| `build/ITALY-REALITY-HANDOFF-V2.1/` (25 MB, não commitado) | ✅ reconstruível pela cadeia |
| `build/ITALY-REALITY-HANDOFF-V2/` (8 MB, **entrada** da cadeia) | ✅ **commitado** |

**Contadores medidos, todos limpos:**

```
registro central : 6.739 registros · 2.891 client-safe · 0 IDs duplicados
portão de QA     : 0 violações · 0 sem carimbo · 0 contagens divergentes
cruzamentos      : 20 emitidos · 0 apoio órfão · 0 apoio inseguro · 0 cultura errada
fontes           : 185 linhas · 302 chaves resolvem · 0 citada sem cadastro
língua           : 10.202 campos com IT+EN · 0 ainda só em português
separação        : 25 arquivos no ingest · 0 papel de trabalho dentro
```

Origem dos registros: `PREVIOUS_HANDOFF 3.276 · LAST_MILE 3.441 · DERIVED_V2_1 22`.

### 4.2 · Os quatro defeitos do V2

1. **Unificação** — um só `CANONICAL-INTELLIGENCE-MASTER.json`, **0 IDs
   duplicados** (eram 62; as causas eram `FUTURE-EVENTS` e `RELATIONSHIPS` serem
   *vistas* indexadas como coleções, mais colisão de ID em `SOURCES`).
2. **Cruzamentos** — descartados e refeitos por ID normalizado, com 8 invariantes
   provadas por programa antes de emitir. Do V2: **36 IDs com cultura errada** e
   **7 de 19 apoiados em registro não conferido** → agora **0 e 0**.
3. **Granularidade** — 2.945 linhas atômicas do ISTAT de volta, carimbadas
   `LAST_MILE`.
4. **Separação** — `DESIGN-INGEST/` com 25 arquivos e **zero** papel de trabalho;
   12 itens em `INTERNAL-ARCHIVE/`.

### 4.3 · A localização (IT/EN)

- **1.017 frases** distintas traduzidas, cobrindo **10.202 campos**.
- **695 ressalvas subiram** de dentro do bloco `RESEARCH` (onde só existiam em
  português) para campos client-facing traduzidos. Sem isso a tela mostraria
  **nada** no lugar da ressalva.
- Memória de tradução versionada em `data/i18n/v21-traducoes.json` — a chave é o
  próprio texto em português, então frase igual tem tradução igual **por
  construção**.
- **Citação pública NÃO foi traduzida** (é prova).

**Como foi conferida — três camadas:**

| Camada | O que fez |
|---|---|
| trava mecânica (`scripts/v21_traducao_trava.py`) | número, data, negação, incerteza, nome de lugar e CAIXA ALTA preservados |
| conferente adversarial (workflow, 61 lotes) | um agente independente por lote tentou **derrubar** cada tradução → **33 frases refeitas** |
| autoteste da trava (`tests/test_v21_traducao_trava.py`) | **23 testes**, todos passando, com mentiras plantadas de propósito |

### 4.4 · Dois defeitos que só apareceram nesta sessão

- **A chave das fontes não ligava em nada.** Fontes cadastradas como
  `IT-SRC-MINISTERO` e `SRCX_ARPAE_IT`; coleções citando `SRC_ARPAE_IT`. De
  **13.280 citações, 56% não encontravam ninguém**. Corrigido: chave primária
  passou a ser a que o pacote já citava, o nome antigo resolve por `ID_ALIASES`,
  e 15 fontes citadas sem linha foram cadastradas a partir da URL que o próprio
  registro citante já declarava. **0 órfãs.**
- **Os cruzamentos não tinham carimbo.** O cabeçalho declarava 20 client-safe e
  os registros não traziam `CLIENT_SAFE` nem `QA_STATUS` — a tela teria filtrado
  os 20 e mostrado vazio. Ver §8.

---

## 5. WHAT IS CURRENTLY PARTIAL

### 5.1 · ⚠️ A AUDITORIA INDEPENDENTE — 99 ACHADOS NÃO REFUTADOS

**Este é de longe o item mais importante deste handoff.**

`handoff/paused-v2/ACHADOS-DA-AUDITORIA-NAO-REFUTADOS.json`

- **Já feito:** 38 agentes concluíram, em 12 dimensões. Produziram **99 achados
  brutos**: 35 `BLOQUEIA_ENTREGA`, 42 `CORRIGIR_ANTES`, 22 `ANOTAR`.
- **O que falta:** a **fase de refutação inteira**. O desenho previa 3 céticos
  independentes por achado, sobrevivendo só o que 2 de 3 não derrubassem. **Ela
  não rodou.**
- **Risco conhecido, e ele é grande nos dois sentidos:**
  - A auditoria rodou **enquanto eu reescrevia o pacote** — um dos próprios
    achados diz isso (*"SOURCES.json mudou 6 vezes durante a auditoria"*).
    Vários achados já foram corrigidos depois de medidos.
  - Mas outros **soam reais e sobreviveriam**, por exemplo:
    `PROVINCIAL virou REGIONAL em 24 registros client-safe`,
    `11 de 14 cruzamentos de rótulo casam a cultura certa com o problema errado`,
    `um boletim do Friuli aparece carimbado também como Toscana`,
    `«Trentino» virou «Trentino-Alto Adige»`,
    `2.222 registros que vão à tela citam "fonte não declarada" como única fonte`.
- **Seguro continuar?** Sim — mas **nenhum achado pode ser tratado como
  confirmado** sem reverificação contra o pacote atual.

> **Um achado não refutado não é um defeito: é uma suspeita.** Tratar suspeita
> como defeito faz o time consertar o que não está quebrado; tratar como ruído
> deixa o defeito passar. Os dois erros custam caro, e por isso a refutação
> existia no desenho.

### 5.2 · A conferência de sentido — não produziu nada

`handoff/paused-v2/conferencia-de-sentido.json` está **vazio**: zero agentes
concluíram antes da interrupção.

Ela ia cobrir o buraco que a trava mecânica **declara não alcançar**: se
`autorizza` quer mesmo dizer `autoriza`. Hoje a garantia semântica vem só do
conferente adversarial que rodou durante a tradução (§4.3) — que é boa, mas
verificou a tradução **no momento em que foi feita**, não numa segunda leitura
independente.

### 5.3 · Supabase — pausado por decisão anterior do usuário

As migrations `019`, `020` e `021` existem em `supabase/migrations/` e **não
foram aplicadas**. O despacho foi negado por permissão em sessão anterior, e os
comandos exatos foram entregues ao usuário. Não retomar sem pedido explícito.

---

## 6. WHAT HAS NOT STARTED

- **Nenhuma tela foi construída.** Este pacote é contrato de dado; o Design ainda
  não consumiu nada dele.
- **Nenhuma validação com o cliente.** Nada aqui foi mostrado à ADAMA.
- **Nenhuma coleta nova.** A missão V2.1 proíbe explicitamente coletar mais dado
  — ela é de organização, não de descoberta.
- **Nenhuma verificação humana** dos 2.891 registros client-safe um a um. O que
  existe é amostragem e invariantes de máquina.

---

## 7. CURRENT COUNTS / MEASUREMENTS

Lidos de `build/ITALY-REALITY-HANDOFF-V2.1/ACCEPTANCE-REPORT.json` (dentro do ZIP
commitado). Para recontar: `py scripts/v21_aceitacao.py`.

| Coleção | Total | Client-safe |
|---|---:|---:|
| CROP-ECONOMIC-WEIGHT | 2978 | 14 |
| PRODUCT-RELATIONSHIPS | 2030 | 1512 |
| COMPETITOR-ACTIVITIES | 577 | 569 |
| SOURCES | 185 | 31 |
| PRODUCTS-REGULATORY | 163 | 163 |
| MARKET-OBSERVATIONS | 157 | 91 |
| CURRENT-FIELD-SIGNALS | 122 | 87 |
| SCIENCE | 88 | 88 |
| PUBLIC-VOICES | 79 | 65 |
| PUBLIC-CHANNELS | 62 | 62 |
| RESEARCHERS | 60 | 60 |
| PRODUCTS-COMMERCIAL | 51 | 51 |
| AGROMET-CONDITIONS | 44 | 14 |
| EVENTS | 40 | 26 |
| RESISTANCE | 34 | 34 |
| REGULATORY-FUTURE | 28 | 8 |
| FUTURE-EVENTS *(vista)* | 23 | 9 |
| CLIENT-SAFE-CROSSINGS | 20 | **0** — ver §8 |
| RELATIONSHIPS *(vista)* | 20 | **0** |
| NEWS | 8 | 8 |
| CROP-WINDOWS | 7 | 7 |
| OPPORTUNITIES | 3 | 0 |
| FUTURE-SIGNALS | 3 | 1 |

Cruzamentos por tipo: `FIELD_SIGNAL_X_LABEL_USE 14 · MARKET_X_FIELD_SIGNAL 3 ·
COMPETITOR_X_CROP_WINDOW_X_PORTFOLIO 2 · IDENTIFIED_VOICE_X_SCIENCE_X_RESISTANCE 1`.

Testes: **23 do autoteste da trava** passam. A suíte geral do repositório roda com
**1 falha pré-existente** (`test_comunicacao.py :: "nenhuma casa nasce
autorizada"`), de outra frente de trabalho — o arquivo está intocado no Git e lê
`scripts/comunicacao_*`, que esta missão não encostou.

---

## 8. IMPORTANT DECISIONS / LAWS

Estas decisões custaram trabalho para descobrir. **Não reabra sem motivo novo.**

### O portão de QA

```
CLIENT_SAFE=true  ← QA_PASS · QA_CORRECTED · EVIDENCE_DOCUMENTED · EVIDENCE_SOURCED
CLIENT_SAFE=false ← QA_UNREVIEWED · QA_REJECTED · EVIDENCE_DERIVED
```

> **O dado que não foi conferido pode abrir uma pergunta. Não pode fechar uma
> afirmação.**

### O cruzamento não sai pela porta dos fundos

Os 20 cruzamentos têm `CLIENT_SAFE=false` **de propósito**, com
`ALL_SUPPORT_CLIENT_SAFE=true` e `RENDERABLE_WITH_METHOD=true`. O apoio passou no
portão; a junção é leitura nossa.

> **A regra vale para o que nós mesmos produzimos, ou não é regra.**

⚠️ Consequência prática: **se a interface filtrar por `CLIENT_SAFE=true`, nenhum
cruzamento aparece.** Filtrar por `RENDERABLE_WITH_METHOD`.

### As leis do domínio

`ANÚNCIO ALCANÇOU ≠ ANÚNCIO MIRAVA` · `COMENTÁRIO ≠ AGRICULTOR` ·
`TERMO DA CULTURA PRESENTE ≠ AUTORIZADO NA CULTURA` · `PRORROGAÇÃO ≠ RENOVAÇÃO` ·
`CONDIÇÃO ≠ PRESENÇA` · `PROVINCIAL ≠ REGIONAL` · `PIAZZA ≠ NACIONAL` ·
`CATÁLOGO ≠ TITULAR DE REGISTRO` · `VOZ ≠ INCIDÊNCIA` ·
`COMUNICAÇÃO ≠ PARTICIPAÇÃO DE MERCADO` · `CRUZAMENTO ≠ OPORTUNIDADE`

### A citação não se traduz

> **A citação é o documento. A leitura é a nossa opinião sobre ele. Só a segunda
> muda de língua.**

Ficam na língua original: `TEXT_ORIGINAL`, `CREATIVE_TEXT`, `DESCRIPTION`,
`SPECIES_IT`, `PHENOLOGICAL_STAGE_DECLARED`, `NAME`, e todo trecho após
`literal:`.

### Sem default silencioso

`ORIGIN_LAYER` já teve um `or 'DERIVED_V2_1'` que apagou a origem de 2.945 linhas
do ISTAT: dado externo passou a aparecer como dedução nossa.

> **O default silencioso é pior que o campo vazio. O vazio se vê; o default mente
> com confiança.**

### Vista não é coleção

`FUTURE-EVENTS` é recorte de `EVENTS`; `RELATIONSHIPS` espelha os cruzamentos.
As duas **não entram** no registro central (`VIEWS_NOT_INDEXED`). Carregá-las
junto conta o mesmo registro duas vezes.

### A trava precisa de autoteste

A trava da tradução foi corrigida **seis vezes** até parar de reprovar tradução
correta. Cada correção afrouxou algo.

> **Uma trava corrigida até passar pode ter virado um carimbo.**

Por isso `tests/test_v21_traducao_trava.py` planta mentiras de propósito. **Se
esses testes começarem a falhar, a trava parou de proteger.**

### O passo que apaga sem avisar

`scripts/v21_ingest.py` faz `rmtree` da pasta do pacote. Rodar um passo do meio
da cadeia sozinho apaga em silêncio carimbos, rechaveamento e traduções.

> **O passo que apaga sem avisar é pior que o passo que falha. O que falha, se
> vê.** Rode sempre `bash scripts/v21_cadeia.sh` inteiro.

---

## 9. KNOWN FAILURES / QUARANTINE

**Não promova nem reintroduza:**

- **`build/ITALY-REALITY-HANDOFF-V2/TOP-CROSSINGS.json`** — descartado, não
  remendado. Tinha 36 IDs com cultura errada e 7 de 19 cruzamentos contaminados.
  O método era o defeito (casamento por substring: "riso" batia dentro de
  "compa*riso*n"), não os exemplos.
- **A voz rejeitada em `PUBLIC-VOICES`** — a frase estava em `<blockquote>` sem
  aspas: é destaque editorial do jornal, não fala do rizicultor. `QA_REJECTED`
  permanente. Reescrever campo não devolve frase à boca de ninguém.
- **`fullpage` e `max-ace` como produtos de cultura** — aparecem nas 7 páginas de
  cultura do site da ADAMA porque são banner do site, não associação de cultura.
- **`_COLECOES.json` dentro de `DESIGN-INGEST/`** — é rascunho de build e vira um
  segundo índice ao lado do `APP-MANIFEST`. A cadeia agora o move sozinha para
  `INTERNAL-ARCHIVE/`.
- **`OPPORTUNITIES.json`** — 3 registros, **nenhum client-safe**. Não promova.

---

## 10. ACTIVE OR RECENT BACKGROUND TASKS

**Tarefas pesadas rodando após a pausa: 0.**

| Task | Estado | Saída | Encerrada? | Falta integrar? |
|---|---|---|---|---|
| `v21-localizar-resto` (`wf_8918345b-2e3`) | **concluída** | 726 frases IT/EN, 33 refeitas, 0 lotes perdidos | sim, naturalmente | **não** — 100% integrado em `data/i18n/v21-traducoes.json` |
| `v21-auditar-pacote` (`wf_2c05414f-38d`) | **interrompida** por `TaskStop` | 38 agentes → 99 achados brutos | sim | **SIM** — ver §5.1 |
| `v21-conferir-sentido` (`wf_2afbff77-eb9`) | **interrompida** por `TaskStop` | nenhuma | sim | não há o que integrar |
| localização inicial (`wimgu1ear`) | **concluída** | 94 registros / 300 campos | sim | **não** — integrado |

Saída parcial preservada em `handoff/paused-v2/` com manifesto próprio.

---

## 11. FILE MAP

**Leia nesta ordem:**

```
HANDOFF-V2-PAUSE.md            ← este arquivo
HANDOFF-V2-PAUSE.json          ← o mesmo, legível por máquina
handoff/paused-v2/MANIFESTO.json
handoff/paused-v2/ACHADOS-DA-AUDITORIA-NAO-REFUTADOS.json   ← o próximo passo mora aqui
docs/design/ITALY-V2.1-README-FIRST.md   ← a porta de entrada do pacote
```

**A cadeia de construção, em ordem de execução:**

```
scripts/v21_cadeia.sh              ← rode ISTO, não os passos soltos
  1 v21_ingest.py                  ⚠️ faz rmtree da pasta do pacote
    v21_ingest_b.py
  2 v21_crossings.py               as 8 invariantes
  3 v21_vozes_reconciliar.py       §13
  4 v21_carimbar_origem.py         camada de origem, sem default
  5 v21_fontes_rechavear.py        a chave que liga
    v21_fontes_faltantes.py
  6 v21_traducao_trava.py --aplicar  recusa gravar se falhar
  7 v21_fechar.py                  índice, manifesto, arquivo interno
  8 v21_aceitacao.py               §19, todo número recontado
```

**Apoio:**

```
scripts/v21_normalizar.py          CROP/ISSUE/REGION_ID + guarda anti-prosa
scripts/v21_campos_de_lingua.py    qual campo se traduz e qual não
scripts/v21_tm_colher.py           colhe saída de workflow para a memória
data/i18n/v21-traducoes.json       1.017 frases PT→IT/EN (a memória)
data/i18n/v21-traducoes-nucleo.json  as 11 que se repetem milhares de vezes
tests/test_v21_traducao_trava.py   23 testes com mentiras plantadas
build/ITALY-REALITY-HANDOFF-V2/    ⚠️ ENTRADA da cadeia (commitada)
build/SINTONIA-ITALY-REALITY-HANDOFF-V2.1.zip   a saída (commitada)
```

---

## 12. EXACT NEXT STEP

**Reverificar os 35 achados `BLOQUEIA_ENTREGA` de
`handoff/paused-v2/ACHADOS-DA-AUDITORIA-NAO-REFUTADOS.json`, um a um, contra o
`DESIGN-INGEST` atual — e só então corrigir o que sobreviver.**

Comece pelos que soam mais reais e mais caros:

1. `PROVINCIAL virou REGIONAL em 24 registros client-safe`
2. `11 de 14 cruzamentos de rótulo casam a cultura certa com o problema errado`
3. `um boletim do Friuli aparece carimbado também como Toscana`
4. `2.222 registros citam "fonte não declarada" como única fonte`

Se um achado não reproduzir contra o pacote atual, ele já foi corrigido —
registre isso e siga. **Não corrija o que não reproduziu.**

---

## 13. EXACT RESUME COMMANDS

```bash
cd /c/eame-sintonia
git fetch origin
git rev-parse --abbrev-ref HEAD          # esperado: claude/eame-competitor-public-communication
git rev-parse HEAD                       # compare com HANDOFF-V2-PAUSE.json > head
git status --short                       # ⚠️ há trabalho de OUTRA sessão aqui
```

```bash
export PYTHONIOENCODING=utf-8:replace && py scripts/v21_aceitacao.py
```

```bash
export PYTHONIOENCODING=utf-8:replace && py -c "import sys;sys.path[:0]=['tests','scripts'];import test_v21_traducao_trava as T;[getattr(T,n)() for n in dir(T) if n.startswith('test_')];print('23 testes da trava: ok')"
```

```bash
export PYTHONIOENCODING=utf-8:replace && bash scripts/v21_cadeia.sh
```

**Receitas que custaram para descobrir — não redescubra:**

- O Python deste ambiente é `py`, não `python`. **Sempre** com
  `export PYTHONIOENCODING=utf-8:replace`, senão a acentuação quebra a saída.
- **Windows não distingue maiúscula:** apagar `Scripts/` apaga `scripts/`. Já
  aconteceu, e custou 75 arquivos.
- **`curl` devolve 0 bytes com HTTP 200** nos PDFs do Ministero della Salute.
  `urllib` devolve 222 KB. A ferramenta recusa; a porta está aberta.
  > **FERRAMENTA QUE RECUSA ≠ PORTA FECHADA.**
- **VPN italiana** abre ISMEA, ISTAT e ARPAV. **Não abre a ADAMA**, que bloqueia
  por navegador (Akamai) — só janela gráfica passa.
- **Um HTTP 200 não diz nada sobre a rota se você não sabe por onde saiu.** Um
  coletor já concluiu "o ISMEA nunca foi bloqueado" porque recebeu 200 — com a
  VPN ligada, sem saber.
- **Catálogo da ADAMA:** a listagem por categoria é bloqueada, mas as páginas por
  cultura (`/vite`, `/mais`, `/riso`, `/cereali`, `/pomodoro`, `/pomacee`,
  `/soia`) abrem e estão no menu da própria página 404.

---

## 14. DO NOT DO

- ❌ **Não colete dado novo.** A missão V2.1 é de organização. Coleta é outra
  missão.
- ❌ **Não recolete os 163 rótulos do Ministero** nem os 51 produtos do catálogo
  ADAMA. Estão prontos e conferidos.
- ❌ **Não retraduza** o que já está em `data/i18n/v21-traducoes.json`. São 1.017
  frases que passaram por trava mecânica **e** conferente adversarial.
- ❌ **Não reabra** a decisão de `CLIENT_SAFE=false` nos cruzamentos (§8).
- ❌ **Não reabra** a decisão de não traduzir citação.
- ❌ **Não reintroduza** `TOP-CROSSINGS.json` do V2.
- ❌ **Não rode um passo do meio da cadeia sozinho** — rode `v21_cadeia.sh`.
- ❌ **Não trate os 99 achados da auditoria como confirmados.** Eles não passaram
  pela refutação, e parte foi medida enquanto o pacote mudava.
- ❌ **Não commite** os arquivos de `italia-portale/`, `scripts/instagram_*`,
  `tests/test_adama_es_gate.py`, `act.json`, `b.json`, `st*.json`, `tmp_ce/` —
  são de **outra sessão** trabalhando na mesma pasta.
- ❌ **Não aplique as migrations do Supabase** sem pedido explícito do usuário.

---

## 15. RESUME PROMPT

## COPY-PASTE PROMPT FOR NEW CLAUDE ACCOUNT

```
Estou retomando a missão SINTONIA ITALY · REALITY HANDOFF V2.1, que foi pausada
de propósito para preservar o limite de uso de outra conta Claude. A missão não
falhou.

Você tem acesso apenas a este repositório. Não existe conversa anterior para
consultar — tudo o que você precisa está no Git.

FAÇA NESTA ORDEM:

1. Leia HANDOFF-V2-PAUSE.md inteiro, na raiz do repositório. Ele tem 15 seções.
2. Leia HANDOFF-V2-PAUSE.json.
3. Confirme a branch e o HEAD:
       cd /c/eame-sintonia
       git fetch origin
       git rev-parse --abbrev-ref HEAD
       git rev-parse HEAD
   Compare o HEAD com o campo "head" do JSON.
4. Rode `git status --short`. ⚠️ ATENÇÃO: esta pasta é um worktree COMPARTILHADO
   com outra sessão do Claude. Há arquivos modificados que NÃO são desta missão
   (italia-portale/, scripts/instagram_*, tests/test_adama_es_gate.py, act.json,
   b.json, st*.json, tmp_ce/). Nunca os inclua num commit desta missão.
5. Rode a verificação leve, que reconta tudo dos arquivos:
       export PYTHONIOENCODING=utf-8:replace && py scripts/v21_aceitacao.py
   Esperado: 0 violações de QA, 0 IDs duplicados, 0 cruzamento com apoio inseguro,
   0 fonte citada sem cadastro, 0 campo só em português.
6. Rode os 23 testes da trava de tradução:
       export PYTHONIOENCODING=utf-8:replace && py -c "import sys;sys.path[:0]=['tests','scripts'];import test_v21_traducao_trava as T;[getattr(T,n)() for n in dir(T) if n.startswith('test_')];print('ok')"
   Se algum falhar, a trava parou de proteger — conserte antes de qualquer outra
   coisa.

DEPOIS DISSO, FAÇA APENAS O PRÓXIMO PASSO DA §12:

Reverifique, um a um, os 35 achados marcados BLOQUEIA_ENTREGA em
handoff/paused-v2/ACHADOS-DA-AUDITORIA-NAO-REFUTADOS.json, contra o pacote
atual em build/ITALY-REALITY-HANDOFF-V2.1/DESIGN-INGEST/.

Esses achados NÃO estão confirmados: a fase de refutação do workflow foi
interrompida, e parte deles foi medida enquanto o pacote ainda estava sendo
reescrito. Um achado que não reproduzir contra o pacote atual já foi corrigido —
registre isso e siga, sem consertar o que não está quebrado.

Comece por: (1) "PROVINCIAL virou REGIONAL em 24 registros client-safe";
(2) "11 de 14 cruzamentos de rótulo casam a cultura certa com o problema errado";
(3) "um boletim do Friuli aparece carimbado também como Toscana";
(4) "2.222 registros citam 'fonte não declarada' como única fonte".

NÃO FAÇA:
- não colete dado novo (esta missão é de organização, não de descoberta);
- não retraduza o que está em data/i18n/v21-traducoes.json;
- não reabra as decisões da §8 do handoff (portão de QA, cruzamento com
  CLIENT_SAFE=false, citação que não se traduz, vista que não é coleção);
- não rode um passo do meio da cadeia sozinho — o passo 1 faz rmtree da pasta do
  pacote e apaga em silêncio o que veio depois. Rode `bash scripts/v21_cadeia.sh`
  inteiro;
- não aplique as migrations do Supabase sem pedido explícito do usuário.

PRESERVE as leis de verdade e de QA descritas na §8 do handoff. Elas custaram
trabalho para descobrir e cada uma existe porque alguém já errou daquele jeito.

Ao terminar um bloco de trabalho, faça um commit na branch atual e um push
normal. Não faça merge para a main, não reescreva histórico, não force push.

E, no chat, explique tudo em linguagem simples — frase curta, palavra do dia a
dia, número sempre com a unidade e o denominador do lado. Simplifique a
linguagem, nunca o conteúdo: ressalva, margem de erro e "não sei" continuam
inteiros.
```
