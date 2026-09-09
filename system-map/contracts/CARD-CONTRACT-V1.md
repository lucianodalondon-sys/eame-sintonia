# CARD CONTRACT V1 — a forma operacional da PARTE XXI

```
AUTHORITY          BIBLIA-CANONICA-DA-COLETA.md · PARTE XXI · COL-LAW-601 a COL-LAW-617
ESTE FICHEIRO      NÃO é autoridade. É a leitura operacional da lei que está lá.
BIBLE_VERSION      V1.4
MEDIDO_EM          572647dc · 2026-09-09
```

> **UM DONO. MÚLTIPLOS PONTEIROS.** Se este ficheiro discordar da Bíblia, **a Bíblia
> vence e este ficheiro está errado**. Ele existe para três coisas que a Bíblia não deve
> carregar, porque não são lei:
>
> 1. o contrato em forma pronta para virar *schema*, no dia em que houver *schema*;
> 2. o **vocabulário de hoje medido** contra a lei — quantos cartões, que tipos, que estado;
> 3. o registo do que foi **recusado**, e por quê.
>
> **Nada aqui foi aplicado.** Nenhum cartão foi renomeado, movido, partido, fundido ou
> recarimbado. Nenhuma aresta foi criada ou apagada. Nenhum ficheiro gerado do mapa foi
> tocado. O censo em curso mede uma fotografia, e esta missão não entrou nela.

---

## 1 · O CONTRATO, CAMPO A CAMPO

Isto **não é** um `card.schema.json`. É o que um `card.schema.json` teria de conter no dia
em que for escrito — e ele **não foi escrito nesta missão**, de propósito (a migração dos
cartões atuais vem depois de o censo AS-IS fechar).

### 1.1 · Identidade — COL-LAW-602

| campo | obrigatório | valores | nota |
|---|---|---|---|
| `CARD_ID` | **sim** | estável, `C-…` | não muda quando o ficheiro muda de nome |
| `NAME` | **sim** | texto | nome de gente, não nome de módulo |
| `TYPE` | **sim** | ver §2 | lista fechada |
| `OWNER` | **sim** | pessoa ou equipa | quem responde, não quem escreveu |
| `LIFECYCLE` | **sim** | `PROPOSED` · `ACTIVE` · `DEPRECATED` · `RETIRED` | eixo separado da evidência |

### 1.2 · Responsabilidade — COL-LAW-602

| campo | obrigatório | nota |
|---|---|---|
| `PURPOSE` | **sim** | para que existe, numa frase |
| `OWNS_QUESTION` | **sim** | **a pergunta de que ele é dono.** Duas peças com a mesma pergunta são duas verdades |

### 1.3 · Portas — COL-LAW-603

Todas **opcionais**, e todas com a mesma regra: **ausência é ausência**. Porta inaplicável
fica de fora, ou fica `NOT_APPLICABLE` — e `NOT_APPLICABLE` nunca é `UNKNOWN`
(COL-LAW-035).

```
CONTROL_IN   CONTROL_OUT      quem manda em mim · em quem eu mando
DATA_IN      DATA_OUT         o que atravessa a linha, nos dois sentidos
POLICY_IN    POLICY_OUT       a regra que recebo · a decisão que publico
CONFIG_IN                     o que me parametriza sem me mandar
READS        WRITES           o que leio · o que escrevo
STATE_OUT                     onde parei
PROOF_OUT                     a evidência que deixo
META_OUT                      o que digo sobre mim — contagens, custo, tempo
```

### 1.4 · Autoridade — COL-LAW-604

| campo | obrigatório | nota |
|---|---|---|
| `DECIDES` | **sim** | lista das decisões que lhe pertencem |
| `MUST_NOT_DECIDE` | **sim** | lista das decisões que, se ele tomar, são `ARCHITECTURE_MISMATCH` |

**`MUST_NOT_DECIDE` vazio é uma declaração, não uma omissão.** Um cartão que não consegue
nomear nada que não deve decidir provavelmente não tem fronteira — e isso é o próprio
achado.

### 1.5 · Partes — COL-LAW-611

| campo | obrigatório | nota |
|---|---|---|
| `SUBCOMPONENTS` | não | partes com autoridade própria continuam inspecionáveis |

---

## 2 · OS DEZASSEIS TIPOS, E O QUE HOJE ESTÁ NO LUGAR DELES

A lista canônica está na COL-LAW-605. A coluna da direita é **medição, não carimbo**: diz
que valor de `kind` os cartões de hoje carregam, e **nenhum deles foi alterado**.

| `TYPE` | gaveta | `kind` que hoje ocupa este espaço |
|---|---|---|
| `TRIGGER` | `.github/workflows/` | `workflow` (6) |
| `CONTRACT` | `pedido/` | `contract` (25, misturado com outras funções) |
| `REGISTRY` | `fontes/` · `candidatas/` | `contract` · `engine` |
| `POLICY` | `pedido/receitas.py` · parte de `regras/` | `engine` |
| `ORCHESTRATOR` | `orquestrador/` | `engine` |
| `EXECUTOR` | `coleta/` | `engine` |
| `TOOL` | `ferramentas/` | `library` (5) · `engine` |
| `ADAPTER` | **sem gaveta** | — não existe como tipo |
| `GATE` | `admissao/` · `portoes/` | `gate` (16) |
| `RULE` | `regras/` | `contract` · `engine` — papel medido `STAMPS` (3) |
| `TRANSFORM` | `motor/` | `chain` (1) · `engine` |
| `STORE` | `guarda/` | `store` (1) · `engine` |
| `MEASURE` | `medidas/` | `engine` — papel medido `MEASURES` (15) |
| `PROOF` | `provas/` · `tests/` | `test` (6) · `proof` (1) |
| `SURFACE` | `superficie/` · `pacote/` | `surface` (4) |
| `EXTERNAL` | **sem gaveta**, de propósito | `veiculo` (no gerado) |

### O que a medição diz, sem opinião

```
COMPONENTES DECLARADOS      130
CARTÕES NO MAPA             157
ARESTAS                     608

kind = engine               63   de 130   (48%)
kind com 1 único ocupante    5   proof · chain · artifact · store · scanner
TYPE canônico declarado      0   de 130
OWNS_QUESTION declarado      0   de 130
DECIDES declarado            0   de 130
LIFECYCLE declarado          0   de 130
```

**`engine` não é um tipo: é o sítio onde se põe o que não se classificou.** Quase metade
dos cartões está lá. E `artifact` não devia ser tipo de cartão nenhum — artefato é
**entidade** (COL-LAW-009), não responsabilidade.

**Isto não é uma crítica ao mapa.** O `kind` nasceu para pintar ícone e agrupar visual, e
faz isso bem. O que ele nunca foi é um contrato de responsabilidade — e por isso não
reprova nada.

---

## 3 · A ARESTA — COL-LAW-612

```
FROM · TO · TYPE · DIRECTION            obrigatórios
PAYLOAD / CONTRACT                      quando aplicável
```

`TYPE` vem da COL-LAW-048, e **são estes sete, medidos nesta árvore**:

| `TYPE` | quantas | o que significa |
|---|---:|---|
| `READ` | 171 | leio o que outro escreveu |
| `PROOF` | 170 | provo alguma coisa sobre o outro |
| `RULE` | 91 | uma regra atravessa daqui para ali |
| `CODE` | 70 | importo, logo dependo — **e só isso** |
| `CONTROL` | 63 | mando o outro correr |
| `DATA` | 36 | dado atravessa a linha |
| `WRITE` | 7 | escrevo onde o outro é dono |

O campo `payload` já existe e já diz o que passa: `artefacto` · `codigo` · `execucao` ·
`dado` · `coleta` · `rota` · `contas`.

---

## 4 · O QUE FOI RECUSADO — e por quê

> **Princípio aplicado, o mesmo da emenda V1.1:** *não criar nome novo se um nome existente
> resolve.* Recusar em silêncio seria pior do que aceitar: daqui a três meses alguém
> proporia de novo, sem saber que já tinha sido pesado.

| candidato | veredito | porquê |
|---|---|---|
| um **segundo contrato de componente** | ❌ **recusado** | a COL-LAW-104 já é o contrato de exibição. A PARTE XXI **estende**, e diz isso na primeira linha. Duas autoridades sobre componente seriam o defeito que esta lei existe para impedir |
| `ARCHETYPE` como nome do tipo | ❌ **recusado** | a palavra já tem dono nesta casa: `O3_RESISTANCE_MOA`, `O4_COMPETITIVE_OPENING`, `O5_REGULATORY_PREPARATION`, do motor V2.1. O campo chama-se `TYPE` |
| `WIRED` no eixo da evidência | ❌ **é `CODE`** | «há implementação real que permite» já tem nome na COL-LAW-102. Dois nomes para um conceito é o começo de duas verdades |
| aresta `POLICY` | ❌ **é `RULE`** | a decisão de política atravessa como `RULE`, que é o nome medido em 91 arestas desta árvore |
| aresta `CONFIG` | ❌ **por agora** | zero arestas desta árvore foram medidas como configuração. Entra no dia em que uma medição a exigir |
| aresta `META` | ❌ **por agora** | idem. `META_OUT` existe como **porta do cartão** (COL-LAW-603); como tipo de aresta, não tem referente medido |
| uma taxonomia de tipos inteiramente nova | ❌ **recusado** | os dezasseis tipos saíram das gavetas que já existem (`AGENTS.md`) e dos papéis já medidos (`STAMPS`/`MEASURES`/`DECLARES`). Inventar nomes teria criado um terceiro vocabulário |
| `SURFACE` como tipo | ✅ **aceite** | não estava na lista pedida, mas existe nesta árvore: 4 cartões `surface` e as onze telas do portal. Deixá-lo de fora obrigaria a tipá-los de `engine` |
| `RULE` separado de `MEASURE` | ✅ **aceite** | o `AGENTS.md` já separa `regras/` de `medidas/`, e há um teste no CI que reprova quando a divisão deixa de bater com a função |

---

## 5 · O TESTE DA LEI — só leitura, nada consertado

Aqui a lei é aplicada a achados **já medidos** por outras missões. **Nenhum foi
consertado.** O que se testa é se o contrato consegue **nomear** o problema — porque uma
lei que não nomeia o defeito que já existe não iria nomear o próximo.

| # | achado, já medido | a lei que o nomeia | o que ela diz, em uma linha |
|---|---|---|---|
| 1 | `C-INGRESSO` é `gate` e vive em `Z-ACOES`, a zona dos executores | `COL-LAW-601` | a gaveta e o tipo respondem a perguntas diferentes; a gaveta não decide o que a peça é |
| 2 | `COL-008` — dois botões chamam a Apify pelo nome | `COL-LAW-604` + `605` | `TRIGGER.MUST_NOT_DECIDE` inclui «qual ferramenta». Isto é `ARCHITECTURE_MISMATCH`, não gosto |
| 3 | `COL-010` — a rota é decidida em três sítios | `COL-LAW-602` | três donos para «como atender este pedido»: duas das três autoridades não deviam existir |
| 4 | `C-SINTONIA-SCRAP` media 24 fases dentro da zona «AS FERRAMENTAS» | `COL-LAW-609` | `TOOL` ≠ `EXECUTOR`. Usar ferramenta não torna a peça ferramenta *(já fechado pelo censo — aqui só se mostra que a lei o teria dito numa linha)* |
| 5 | `C-LUGAR-COLETA` — «o motor importa esta lei» e o motor não importa nada | `COL-LAW-613` | `NOME DE COMPONENTE ≠ EVIDÊNCIA DE RESPONSABILIDADE`. São cinco leis nesta condição, não uma |
| 6 | a aresta `V-LINKEDIN → C-SCRAP-SOCIAL`, provada por uma linha de bloco adversarial | `COL-LAW-613` | `COMMENT ≠ EDGE`. O mapa desenhava como travessia a rota que aquele bloco existe para provar **fechada** |
| 7 | `RUN-MANIFEST` com três escritores e dono eleito por ordem alfabética | `COL-LAW-602` | `OWNS_QUESTION` não se sorteia. Executar a corrida não é ser autoridade sobre a procedência dela |
| 8 | `COL-009` — «Apify é o último recurso» aparece em texto em 2 ficheiros e em código em **nenhum** | `COL-LAW-614` | `BIBLE = SIM`, `CODE = NÃO`. Declarado nunca promove a observado |
| 9 | o `STRUCTURED` tem cinco escritores e nenhum dono único | `COL-LAW-610` | um `STORE` tem de dizer **que estágio** preserva; sem isso, o buraco do meio some por arrumação |
| 10 | `C-GESTAO-COLETA` juntava política e diagnóstico | `COL-LAW-616` | `SPLIT_CANDIDATE` — e quem decidiu foram os chamadores, não a opinião |

**Dez achados, dez nomes.** Nenhum precisou de lei nova para além das dezassete, e nenhum
ficou sem nome.

### O que a lei **não** consegue dizer, e é honesto admitir

- **Não distingue chamador de teste de chamador de produção.** É o `G-55`, e enquanto
  existir, `TEST CALLER ≠ PRODUCTION CALLER` é uma proibição sem medidor.
- **Não calcula `SPLIT_CANDIDATE` sozinha.** Os dois precedentes desta árvore foram
  encontrados por gente. É o `G-52`.
- **Não sabe se um `MEASURE` começou a colher.** A prova de hoje cobre régua × medida, não
  medida × executor. É o `G-53`.

> **LEI QUE NINGUÉM MEDE É COMENTÁRIO.** Estes três são, hoje, comentário — e ficam
> escritos aqui por isso, não apesar disso.

---

## 6 · O QUE ESTA MISSÃO DELIBERADAMENTE NÃO FEZ

- **Não criou** `card.schema.json`, `edge.schema.json`, `cardctl.py`, validador, *hook*,
  passo de CI, Skill, nem geração nova do mapa.
- **Não migrou** nenhum dos 130 componentes declarados para a taxonomia nova.
- **Não alterou** cartão, aresta, zona, família ou carimbo.
- **Não regenerou** o System Map, e não tocou em nenhum `.generated.json`.
- **Não corrigiu** nenhum dos dez achados do §5. Eles continuam abertos onde já estavam.
