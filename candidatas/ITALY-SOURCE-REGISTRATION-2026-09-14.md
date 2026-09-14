# PROMOVER AS READY_TO_REGISTER — O QUE IMPEDIU, E O QUE FICOU PRONTO

**Data:** 2026-09-14 · **Branch:** `claude/italy-agricultural-sources-discovery-dfba81`
· **Auditoria:** [`ITALY-SOURCE-REGISTRATION-AUDIT-2026-09-14.csv`](ITALY-SOURCE-REGISTRATION-AUDIT-2026-09-14.csv)
(23 linhas, 31 colunas)

> **A pergunta:** das fontes marcadas READY_TO_REGISTER, quais podem virar
> FONTES REGISTRADAS oficiais do SINTONIA agora, sem rodar Collection e sem
> fabricar identidade?
>
> **A resposta medida: nenhuma pode receber identidade agora.** E a razão não é
> falta de qualidade das fontes — é que o registo de identidade da casa está
> partido em quatro lugares, em três branches que não se conhecem.

---

## A RESPOSTA CURTA

```
VEREDITO = BLOCKED
SOURCE_ID_ASSIGNMENT = BLOCKED_SOURCE_ID_ASSIGNMENT
SOURCE_IDS_CREATED = 0
REGISTERED_BEFORE = 23  →  REGISTERED_AFTER = 23  ·  DELTA = 0
```

E o que **ficou feito**, porque não dependia da identidade:

- **23 de 23** com evidência **preservada em ficheiro**, não descrita em prosa
- a evidência **graduada**: 2 FORTE · 2 FORTE_MAS_ANTIGA · 11 FRACA · 8 INSUFICIENTE
- **3** das 23 descobertas como **já registadas** noutro atlas
- a população inteira de `SOURCE_ID` **contada pela primeira vez**: 245 IDs
- o **próximo número livre por território** calculado contra essa união

---

## O QUE BLOQUEIA, MEDIDO

### 1 · O dono do cadastro existe e é claro

| pergunta | resposta medida |
|---|---|
| `SOURCE_REGISTRY_OWNER` | `docs/fontes/ATLAS-DE-FONTES-EAME.md` |
| `SOURCE_ID_OWNER` | o Atlas. `candidatas/fonte_nova.py` escreve-o na própria fila: *«SOURCE_ID: preenchido só quando virar ficha no atlas»* |
| `SOURCE_WRITE_PATH` | editar o Atlas → correr `generate_system_map.py`, que **gera** o Índice |
| `SOURCE_ID_ASSIGNMENT_MECHANISM` | **não existe código.** É à mão, ao escrever a ficha |
| `SOURCE_ID_COLLISION_CHECK` | **não existe** |
| `CANONICAL_SOURCE_DB` | **NÃO para identidade.** Existe `public.fonte_externa` (migration 020), mas a chave é `bigserial`, a única é `url_base`, e **não há coluna de `SOURCE_ID` nem de território** |
| `ATLAS_DB_RELATION` | são **dois sistemas de identidade diferentes** para conceitos vizinhos, sem ponte |

E a migration 020 declara-se, na linha 38: *«NÃO EXECUTADA AQUI. O aplicador é
`scripts/cadeia_canonica.sh`, e as credenciais do Supabase só existem como
segredo do GitHub Actions.»* → `BLOCKED_FOR_LIVE_AUTHORIZATION`, e não usei
produção como laboratório.

### 2 · A população de IDs está partida em quatro, em três branches

O know-how §119 («UM NÚMERO QUE JÁ É DE ALGUÉM») já tinha medido isto **partido
em dois**. Medido agora, atravessando as **247 branches remotas**:

| onde vive | IDs | dos quais italianos |
|---|---|---|
| atlas de `italy-source-qualification-v1` | **182** | 147 |
| atlas de `passport-tags-italy-v1` | 74 | 30 |
| `candidatas/ITALY-SOURCE-MASTER-V1.json` — **nesta mesma branch** | 62 | 56 |
| **atlas desta branch** — o dono declarado | 42 | 7 |
| **união** | **245** | **201** |

```
o atlas desta branch conhece 42 dos 245 IDs em uso  ·  17%
203 IDs estão EM USO e são INVISÍVEIS daqui
```

E as três branches são **paralelas**: nenhuma contém a outra. A base dos PRs
(`claude/sintonia-eame-repo-setup-xccfob`) tem 28 fichas e 7 IDs italianos —
ou seja, **nenhuma delas é a versão canónica por descendência**.

### 3 · Alocar daqui colidiria em 11 dos 12 territórios

A lei do §119 é literal: **`ALOCA-SE CONTRA A POPULAÇÃO INTEIRA, NUNCA CONTRA O
DONO DECLARADO.`** Medido:

| território | usados na união | próximo pela união | próximo pelo meu atlas | |
|---|---|---|---|---|
| IT-T1 | 23 | **24** | 2 | ⚠️ colidiria |
| IT-T2 | 24 | **25** | 1 | ⚠️ colidiria |
| IT-T3 | 21 | **22** | 2 | ⚠️ colidiria |
| IT-T4 | 2 | **3** | 2 | ⚠️ colidiria |
| IT-T5 | 36 | **37** | 1 | ⚠️ colidiria |
| IT-T6 | 36 | **37** | 1 | ⚠️ colidiria |
| IT-T7 | 14 | **15** | 1 | ⚠️ colidiria |
| IT-T8 | 0 | **1** | 1 | ok |
| IT-T9 | 13 | **14** | 2 | ⚠️ colidiria |
| IT-T10 | 16 | **17** | 1 | ⚠️ colidiria |
| IT-T11 | 5 | **6** | 2 | ⚠️ colidiria |
| IT-T12 | 6 | **7** | 2 | ⚠️ colidiria |

### 4 · E a colisão não daria erro — daria uma fonte a menos

Isto é o que torna o bloqueio obrigatório em vez de conservador.
`system-map/scripts/scan_sources.py` indexa as fichas por
`fora[SOURCE_ID] = ...`. Um ID repetido **sobrescreve em silêncio**:

> a colisão não apareceria como erro — apareceria como uma **fonte que
> desapareceu**.

### 5 · Por que não aloquei pela união, já que a medi

Porque seria **collision-safe e mentiroso**. Escrever `IT-T1-024` no meu Atlas
produziria um documento com `IT-T1-001` e `IT-T1-024` e **22 números pelo meio
que existem noutra branch** — um Atlas cujo próprio Índice gerado declararia 24
fichas enquanto a população real tem 169. Seria o **quarto** registo divergente,
criado justamente pela missão encarregada de unificar.

**Isto não é decisão de missão. É decisão de gente** — a mesma família do
know-how bifurcado.

---

## O QUE FICOU FEITO

### As 23, estado final — e a soma fecha

```
REGISTERED_NEW        0
ALREADY_REGISTERED    3
TRUE_DUPLICATES       0
BLOCKED_IDENTITY     14
BLOCKED_EVIDENCE      6
REVIEW                0
UNKNOWN               0
                    ───
SOMA                 23  ✓
```

Escrevi o constrangimento que **morde primeiro**, não o mais dramático: quem
falha por prova conserta-se abrindo o arquivo da fonte (não depende da
reconciliação de IDs); quem só falha por identidade espera a decisão.

### As 3 que já estavam registadas

Descobertas por **rota exata** contra o Atlas de `italy-source-qualification-v1`:

| fonte | já é |
|---|---|
| Protezione delle Piante (Servizio Fitosanitario Nazionale) | `IT-T3-014` |
| Dati di maturazione dell'uva (Institut Agricole Régional) | `IT-T5-007` |
| Monitoraggio dei costi medi di produzione (ISMEA) | `IT-T10-007` |

Não se cria identidade nova para quem já tem uma — o §119 diz que o ID, uma vez
atribuído, não é reciclado.

### A evidência, preservada e graduada

`CAN DO ≠ DID DO`. A missão anterior **descreveu** exemplos; descrever não é
preservar. Agora há, por fonte, em
`data/samples/IT-SOURCE-EVIDENCE-2026-09-14/<fonte>/`:

```
pagina.txt      o corpo servido
exemplo.json    título, rota, tipo, data observada, sha256, ROTA DE SAÍDA
```

E a evidência é **graduada**, porque o §119.2 avisa que um exemplo pode ser
verdadeiro e não provar nada:

| grau | quantas | o que significa |
|---|---|---|
| **FORTE** | 2 | data **e** tópico específico **e** recente |
| **FORTE_MAS_ANTIGA** | 2 | data e tópico, mas o exemplo tem 2 ou 4 anos |
| **FRACA** | 11 | uma das duas coisas, não as duas |
| **INSUFICIENTE** | 8 | não prova, ou está fora do assunto |

As duas FORTE:

- **Valle d'Aosta** — `Avviso del 19 giugno 2026 - lotta alla popillia japonica`
- **Rete Rurale Nazionale** — `Bollettino fenologico - 10 settembre 2026`
  *(quatro dias antes de hoje)*

---

## QUATRO DEFEITOS MEUS, APANHADOS ANTES DE PUBLICAR

### 1 · Eu declarei "saída direta" e havia uma VPN italiana ligada

A migration 020 escreve a lei: *«UM 200 NÃO DIZ NADA SOBRE A ROTA SE VOCÊ NÃO
SABE POR ONDE SAIU»* — e documenta que em 02/09/2026 um coletor concluiu que *«a
ISMEA nunca esteve bloqueada»* porque recebeu 200, com uma VPN italiana ligada
que ele desconhecia.

**Eu fiz o mesmo.** Na missão passada declarei «saída direta, sem proxy» depois
de olhar só a variável `HTTPS_PROXY`, que estava vazia. Medido agora pelo IP
público:

```
149.22.91.179 · Palermo, Sicily (IT) · AS212238 Datacamp Limited
```

**Todas as 50 rotas que eu validei na missão anterior abriram por rota
italiana.** Não está provado que abram de outra saída — e o coletor de produção
pode não sair por Itália. `rota_de_saida = IT_VPN` viaja agora dentro de cada
`exemplo.json`.

### 2 · A ARSAC não é semanal — a rota serve 2022

Na missão passada declarei a ARSAC `HIGH — semanal` com recorrência
**OBSERVADA**, porque vi **seis títulos datados de 2026**. Vi-os nos
**resultados de busca**, não na rota. Aberta a rota, o link datado mais visível
é:

```
BOLLETTINO agrometeorologico e fitosanitario – agrumi e olivo
valido fino al 29 novembre 2022
```

Quatro anos. E o Veneto viticoli serve `Bollettino del 30 agosto 2024`. Ambos
rebaixados a **FORTE_MAS_ANTIGA**. **Resultado de busca não é a página.**

### 3 · O meu extrator de exemplo devolvia fragmentos de menu

Primeira passagem: 17 exemplos, todos do tipo mais fraco, com textos como
*«orare al Servizio Fitosanitario Laboratorio»*. A causa: eu passava ao extrator
o **texto limpo** da cache da sonda, que não tem etiquetas — sem `<a>` e sem
`<h2>`, ele caía sempre no último recurso. Corrigido buscando o **HTML cru**:
5 títulos de link datados apareceram.

E um exemplo que sobreviveu à primeira versão era
**`Avviso del 08/06/2026 - Concorso per 374 funzionari`** — um concurso público,
apresentado como prova de que o MASAF publica existências de vinho. Verdadeiro,
datado, no sítio certo, e prova de coisa nenhuma. É o erro do §119.2, repetido
por mim. Entrou uma tabela de exclusão para concurso, nomeação e formação.

### 4 · Uma regex quebrada de um modo invisível

A verificação de idade do exemplo não funcionava: escrita por heredoc do shell,
o `\b` tornou-se um caractere de **backspace (0x08)** dentro da regex. Ela
compila, corre e **nunca casa** — os exemplos de 2024 e 2022 passavam como
recentes. E a ferramenta de leitura **não mostra o defeito**, porque backspace
não se vê.

Havia **5** desses caracteres nos meus ficheiros. Todos removidos, e a varredura
final dá zero.

> Regex que não casa nada não acusa erro: devolve lista vazia, e lista vazia
> parece «sem ano».

---

## ENTREGA

```
A  BRANCH                        claude/italy-agricultural-sources-discovery-dfba81
B  INITIAL_HEAD                  f055fc87
C  FINAL_HEAD                    (o commit desta missão)
D  REMOTE_HEAD                   f055fc87 no início · já preservado, sem push necessário
E  WORKTREE                      limpo no início
F  PUSH_STATE                    o trabalho anterior já estava no remoto

G  READY_INPUT                   23
H  ANALYZED                      23

I  REGISTERED_NEW                 0
J  ALREADY_REGISTERED             3
K  TRUE_DUPLICATES                0
L  BLOCKED_IDENTITY              14
M  BLOCKED_EVIDENCE               6
N  REVIEW                         0
O  UNKNOWN                        0

P  REGISTERED_BEFORE             23 fichas (índice gerado)
Q  REGISTERED_AFTER              23
R  REGISTERED_DELTA               0

S  SOURCE_IDS_CREATED             0
T  SOURCE_ID_COLLISIONS           0 criadas · 11 de 12 territórios colidiriam se eu alocasse daqui

U  EVIDENCE_EXAMPLES             23 preservadas em ficheiro · 2 FORTE · 2 FORTE_MAS_ANTIGA · 11 FRACA · 8 INSUFICIENTE
V  PRIMARY_SOURCES_REGISTERED     0

W  CANONICAL_SOURCE_DB           NÃO para identidade · `public.fonte_externa` existe mas sem SOURCE_ID nem território
X  SOURCE_TABLE                  public.fonte_externa (migration 020, não aplicada daqui)
Y  DB_ROWS_BEFORE                NÃO SEI — credenciais são segredo do GitHub Actions
Z  DB_ROWS_INSERTED               0
AA DB_ROWS_AFTER                 NÃO SEI — e não se mede o que não se pode ler

AB SOURCE_TOOL_MAPPING_PRESERVED SIM — 23 fontes, 81 ligações, no CSV de auditoria
AC SOURCE_TOOL_MAPPING_SCHEMA_GAP YES — nem o Atlas nem `fonte_externa` têm lugar
                                  para RAW_NEED nem TOOL_SUPPORTED. Preservado no
                                  artefato desta missão, sem alterar schema canónico

AD INDEX_REGENERATED             SIM, pelo processo canónico · 23 → 23, sem diferença a explicar
AE SYSTEM_MAP_RESULT             MAPA=OK · 101 peças · 338 ligações · peça nova
                                  C-IT-PROMOVER-FONTE · 12 de 13 provas passam;
                                  P9 reprova por `.github/workflows/scrap-social.yml`,
                                  commitado em df165da9 e já não declarado em 191dbda4
                                  — PRE_EXISTING_FAILURE

AF RED_TEAM_RESULT               20 ataques · 15 OK · 5 SALA_VAZIA · 0 falhas · 0 detetores cegos
AG REGRESSION_RESULT             708 testes · 37 falhas = igual à base f055fc87 · NEW_FAILURE = 0

AH COLLECTION_RUNS_DELTA          0
AI RAW_DELTA                      0
AJ WAITING_ROOM_DELTA             0
   DERIVED / STRUCTURED / ADMISSION_DELTA   0 · 0 · 0

AK AUDIT_FILE                    candidatas/ITALY-SOURCE-REGISTRATION-AUDIT-2026-09-14.csv
AL KNOW_HOW_DELTA                ATUALIZAÇÃO NECESSÁRIA — texto final abaixo
```

⚠️ **`SALA_VAZIA` não é aprovação.** Cinco dos 20 ataques não tinham onde
morder, porque nenhuma ficha foi escrita. Dizer «20 de 20 OK» seria contar
vitória por sala vazia. Os detetores foram provados a acender contra entrada
falsa; só não havia entrega para atacar.

---

## KNOW_HOW_DELTA — *atualização necessária*

> Não crio cabeça nova. Texto em forma final, número em branco.

### § — O REGISTO DE IDENTIDADE PARTIU-SE OUTRA VEZ, E AGORA EM QUATRO

O §119 mediu o registo de `SOURCE_ID` partido em **dois** e escreveu a lei:
**aloca-se contra a população inteira, nunca contra o dono declarado.** Medido
em 14/09/2026, atravessando as 247 branches remotas, ele está partido em
**quatro**, e as partes vivem em **três branches paralelas que não se contêm**:

```
atlas de italy-source-qualification-v1      182 IDs
atlas de passport-tags-italy-v1              74
ITALY-SOURCE-MASTER-V1.json (outra branch)   62
atlas da branch corrente                     42   <- o dono declarado
união                                       245
```

**Nenhuma branch vê mais de 17% da população que ela própria governa.** E a
base dos PRs vê 42.

**Lei:** enquanto a reconciliação não acontecer, **nenhuma missão atribui
`SOURCE_ID`** — nem pelo atlas local (colide em 11 de 12 territórios) nem pela
união (não colide, e cria o quarto registo divergente). A missão mede, prepara
a ficha com o número em branco, e para.

**E o detetor continua a não existir:** `scan_sources.py` indexa por
`fora[SOURCE_ID]`, logo uma colisão sobrescreve em silêncio e aparece como uma
fonte que desapareceu, não como erro.

### § — A ROTA DE SAÍDA NÃO SE MEDE NA VARIÁVEL DE AMBIENTE

A migration 020 já escrevia que um 200 não diz nada se não se souber por onde a
medição saiu. Em 14/09/2026 repeti o erro que ela documenta: declarei «saída
direta, sem proxy» após ler `HTTPS_PROXY`, que estava vazia. O IP público dizia
**Palermo, Itália** — havia VPN de sistema, que não passa por variável de
ambiente.

**Lei:** `rota_de_saida` mede-se pelo **IP público observado**, nunca por
`HTTPS_PROXY`/`https_proxy`, e viaja junto de cada medição de acesso. Sem isso,
50 validações de rota valem para uma saída que ninguém declarou.

### § — TRÊS PERGUNTAS DIFERENTES SOBRE O MESMO EXEMPLO

Um exemplo real responde a três coisas, e juntá-las faz uma tabela mentir:

| pergunta | o que prova |
|---|---|
| está **no assunto**? | que a fonte publica **isto** |
| tem **data**? | que a fonte **publicou** |
| a data é **recente**? | que a fonte publica **ainda** |

Medido: de 5 exemplos que passavam as duas primeiras, **dois eram de 2022 e
2024**. E um exemplo datado, no sítio certo, era *«Concorso per 374
funzionari»* — verdadeiro e irrelevante, a mesma família dos *«Codice Etico»*
do §119.2.

**Lei:** grau de evidência em quatro valores — `FORTE`, `FORTE_MAS_ANTIGA`,
`FRACA`, `INSUFICIENTE` — com tabela de exclusão para concurso, nomeação e
formação. Só `FORTE` fecha o gate de REGISTADA.

### § — UM CARACTERE INVISÍVEL PODE DESLIGAR UMA VERIFICAÇÃO

`\b` escrito por heredoc do shell torna-se **backspace (0x08)** dentro da
regex. Ela compila, corre e nunca casa — e a ferramenta de leitura não mostra o
defeito, porque backspace não se vê. Em 14/09/2026 havia 5 desses caracteres, e
por causa deles dois exemplos de 2022 e 2024 passavam como recentes.

**Lei:** conteúdo com escapes de regex escreve-se pela ferramenta de ficheiro,
nunca por heredoc do shell. E vale varrer `chr(8)` no código depois de o gerar:
**uma verificação que não casa nada não falha — passa.**

---

## EM PORTUGUÊS SIMPLES

**Começamos com 23 fontes prontas.**

Antes de dar nome oficial a qualquer uma, fui ver como é que esta casa dá nome.
Descobri duas coisas.

**A primeira:** três delas **já estavam cadastradas**. Estavam num caderno que
vive noutra cópia do projeto, que eu não conhecia — e já tinham número:
`IT-T3-014`, `IT-T5-007`, `IT-T10-007`. Dar-lhes número novo seria dar dois
nomes à mesma pessoa.

**A segunda, e é a que travou tudo:** o caderno de nomes desta casa **está
partido em quatro pedaços, guardados em três gavetas diferentes**, e nenhuma
gaveta sabe o que está nas outras. Juntando tudo, há **245 nomes já dados**. A
gaveta em que eu estou a trabalhar conhece **42** deles — menos de um em cada
cinco.

Se eu tivesse dado o próximo número olhando só a minha gaveta, **em 11 dos 12
assuntos eu teria escolhido um nome que já é de outra fonte**. E o pior: o
programa que lê o caderno não reclamaria. Ele guarda cada fonte pelo nome — dois
nomes iguais, e uma das fontes **simplesmente desaparece da lista**, sem erro,
sem aviso. Alguém procuraria por ela meses depois e não estaria lá.

Por isso **não dei nome a nenhuma**. Isso não é desistir: é a lei que esta casa
já escreveu, depois de ter tropeçado nisso antes.

**O que ficou pronto, e é bastante:**

Guardei, para todas as 23, **a prova em ficheiro** — a página, o título de um
item real, a data e a impressão digital do conteúdo. Antes isso era só uma
frase minha; agora é um arquivo que qualquer pessoa reabre.

E **classifiquei a força dessa prova**, porque prova fraca é pior que prova
nenhuma. Só **duas** são fortes de verdade: o aviso da Valle d'Aosta de junho, e
o boletim de fenologia nacional de **10 de setembro — quatro dias antes de
hoje**. Duas outras têm data, mas de **2022 e 2024**: provam que a fonte já
publicou, não que publique ainda.

**E encontrei quatro erros meus**, três deles da missão passada:

1. Eu disse que a minha internet saía direto. **Sai pela Itália** — há uma VPN
   ligada. Então tudo o que eu testei funciona *vindo da Itália*, e não está
   provado que funcione de outro lugar.
2. Eu disse que a ARSAC publica toda semana. **A página dela serve um boletim de
   2022.** Eu tinha visto títulos de 2026 — na *busca do Google*, não no site.
3. O meu extrator de exemplos estava a apanhar **pedaços de menu**, e um deles
   era um **concurso público para 374 funcionários** apresentado como prova de
   que o ministério publica estoques de vinho.
4. Uma verificação minha estava **desligada por um caractere invisível** — os
   exemplos velhos passavam como novos.

**Nenhuma coleta foi rodada. Nada foi cadastrado. O cadastro continua com 23
fichas.**

**O próximo passo não é meu:** alguém precisa decidir qual das três gavetas é a
verdadeira, e juntar as outras nela. Depois disso, estas 20 fontes recebem nome
numa tarde.

---

## VEREDITO

```
VEREDITO = BLOCKED
```

**Por que BLOCKED e não PARTIAL.** O §35 exige, para PASS, «mecanismo
SOURCE_ID provado» e «nenhum ID fabricado». O mecanismo foi **medido e provado
inseguro**: não há código que atribua, não há detetor de colisão, a população
está partida em quatro e o dono declarado vê 17% dela. Com esse mecanismo,
**qualquer atribuição seria fabricação** — e o §11 manda, nesse caso,
`BLOCKED_SOURCE_ID_ASSIGNMENT` e não improvisar.

**Por que não é FAIL.** Tudo o que não dependia da identidade foi entregue: as
23 analisadas, o dedupe resolvido contra a população inteira, 3 já-registadas
descobertas, a evidência preservada em ficheiro e graduada, o mapeamento
fonte→ferramenta preservado sem alterar schema, Índice e System Map regenerados
pelo processo canónico, red team sem falha, regressão sem falha nova, e
`COLLECTION_RUNS_DELTA = 0`.

**O que desbloqueia:** decidir qual Atlas é canónico e reconciliar os quatro
registos num só. É uma missão própria, e o dono da decisão é o Luciano — a mesma
decisão que o know-how bifurcado já esperava.

```
HARD STOP
```
