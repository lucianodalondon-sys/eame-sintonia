# LEI DO SINTONIA SYSTEM MAP

**Antes de alterar qualquer parte deste projeto, leia e respeite esta regra.**

Este ficheiro é o **dono canónico** das instruções para agentes de programação
(Claude Code, Codex, Copilot, ou qualquer outro) neste repositório. Os outros
ficheiros de instrução **apontam** para aqui; não repetem a lei.

---

## O QUE É O SYSTEM MAP

O SINTONIA System Map é uma **projeção canónica e auditável da arquitetura real
do repositório**. Vive em [`system-map/`](system-map/) e publica-se em
`/system-map/`.

Ele lê-se em três palavras, da esquerda para a direita:

```
COLETA  →  INTELIGÊNCIA  →  ENTREGA
```

Cada uma é uma faixa colorida com os seus blocos dentro, e **toda zona pertence a
uma delas**. Dentro disso, ele responde sem exigir que se saiba programar: o que
cada peça faz, por que existe, de onde recebe, para onde envia, que régua atua
ali, que ficheiros a implementam, que provas a sustentam, e se está a funcionar,
pendente, quebrada ou desconhecida.

```
        REPOSITÓRIO
             ↓
   scanner + contratos + metadata declarada
             ↓
        SYSTEM MAP
             ↓
           HTML
```

**O mapa é derivado do repo. O repo não é derivado do mapa.**
Nunca no sentido contrário. O mapa não é uma segunda verdade arquitetural.

---

## A OBRIGAÇÃO

Toda alteração que modifique **arquitetura · fonte · coleta · fluxo · contrato ·
régua · motor · dependência · input · output · artefato · responsabilidade ·
owner · departamento atendido · superfície · workflow · persistência**

**DEVE atualizar o System Map na mesma mudança** — seja por deteção automática
(regerar), seja por atualização da metadata declarada.

Na prática, se tocou em qualquer coisa dentro de `scripts/`,
`italia-portale/audit/`, `tests/`, `system-map/`, `.github/workflows/` ou
`italia-portale/client/`, isto aplica-se a si.

### Nenhum agente pode

- deixar o mapa sabidamente desatualizado;
- fabricar ligação que não esteja provada por linha de código;
- preservar verde sem evidência, ou herdar verde de uma validação anterior;
- alterar código só para fazer o mapa ficar verde;
- criar uma segunda verdade arquitetural dentro do mapa;
- esconder um `NÃO SEI` atrás de um status que pareça melhor.

**Se a relação não puder ser provada: NÃO SEI.**
Registar `UNKNOWN` é resultado válido, e obrigatório quando é o caso. Ausência
de prova não é prova de ausência, e também não é prova de presença.

---

## OS COMANDOS

Antes de concluir qualquer mudança relevante, corra:

```bash
py controle/censo_do_controle.py                # 1 · medir quem manda
py system-map/scripts/scan_repo.py              # 2 · medir a árvore
py system-map/scripts/scan_sources.py
py system-map/scripts/scan_casco.py
py system-map/scripts/censo_da_coleta.py
py system-map/scripts/pente_fino_da_coleta.py
py system-map/scripts/generate_system_map.py    # 3 · regerar o mapa
py system-map/scripts/validate_system_map.py    # 4 · provar que ele bate com o repo
py controle/portao_do_controle.py               # 5 · provar que o governo não mentiu
py controle/red_team_do_controle.py             # 6 · os doze ataques
py system-map/tests/test_system_map.py          # 7 · as regras não afrouxaram
```

**A ORDEM DO PASSO 1 NÃO É GOSTO.** O censo do controlo escreve
`SALA-DE-CONTROLE-SINTONIA.md`, que é um ficheiro versionado. Corrê-lo *depois*
do scanner faz o scanner medir a versão anterior dela, e a verificação anti-drift
reprova — não porque alguém errou, mas porque a cadeia correu ao contrário.

Use `python3` em vez de `py` em Linux/CI. Se o validador reprovar, **a mudança
não está pronta** — não é um aviso, é um portão.

Depois de regerar, o que mudou tem de entrar no commit:

```bash
git add system-map/data italia-portale/client/system-map
```

### Quando declarar à mão

O scanner mede sozinho ficheiros, imports, chamadas, workflows e artefatos. O
que ele **não consegue** saber está em
[`system-map/data/architecture.declared.json`](system-map/data/architecture.declared.json):
o nome de gente, a frase que explica para que serve, o porquê, o departamento
atendido e a expectativa arquitetural.

Criou um ficheiro de código novo? Declare a que peça ele pertence. O validador
reprova código de arquitetura que nenhuma peça do mapa reivindica — porque
código que ninguém consegue apontar no mapa é arquitetura invisível.

Reescreveu uma peça? A descrição humana dela ficou potencialmente desatualizada,
e o mapa cai para 🟡 sozinho. Releia, corrija a frase e recarimbe:

```bash
py system-map/scripts/generate_system_map.py --stamp
```

Recarimbar sem reler é o único jeito de mentir neste sistema. Não faça isso.

---

## O QUE O VALIDADOR PROVA

| | |
|---|---|
| `P1_SEM_DRIFT` | o mapa commitado é o que o repositório de hoje produz |
| `P2_IDS_UNICOS` | nenhum id repetido; todo território existe |
| `P2_ZONA_TEM_FAMILIA` | toda zona pertence a uma família que existe — CONTROL PLANE, COLETA, A ESPERA, INTELIGÊNCIA ou ENTREGA |
| `P2_PASTA_BATE_COM_MAPA` | **todo ficheiro está na gaveta da sua peça** |
| `P3_SEM_PONTA_SOLTA` | nenhuma ligação aponta para peça inexistente |
| `P4_FICHEIROS_REAIS` | todo ficheiro citado pelo mapa existe |
| `P5_ARESTA_PROVADA` | nenhuma ligação técnica sem linha de código que a prove |
| `P6_VERDE_TEM_PROVA` | nenhum verde só por o ficheiro existir, nenhum verde velho |
| `P6_LINHAGEM_DIZ_A_PROVA` | toda peça de linhagem diz se a prova é documento ou medição do git |
| `P7_NAO_SEI_VIVE` | ligação declarada e não provada continua `UNKNOWN` |
| `P8_UM_DONO` | nenhum ficheiro reivindicado por duas peças |
| `P9_CODIGO_DECLARADO` | todo ficheiro de código pertence a uma peça do mapa |
| `P10_STATUS_VALIDO` | status só pode ser um dos quatro valores |

Corre no CI em
[`.github/workflows/system-map.yml`](.github/workflows/system-map.yml), em cada
push e cada pull request. **Falha fechado**: erro inesperado também é `FAIL`.

### E o que o PORTÃO DO CONTROL PLANE prova

| | |
|---|---|
| `DUPLICATE_AUTHORITY_ID` | nenhum cartão com id repetido |
| `DUPLICATE_CONCEPT_OWNER` | **um conceito, um dono** — nenhum conceito com dois donos canónicos |
| `KNOW_HOW_DUPLICATED` | existe exatamente **um** know-how canónico |
| `SUPERSEDED_MARKED_CANONICAL` | nada substituído continua carimbado de canónico |
| `HANDOFF_AS_AUTHORITY` | nenhum handoff governa nada |
| `SYSTEM_MAP_IS_AUTHORITY` | nenhuma peça do mapa governa — mede e reprova, só |
| `DECLARED_EDGE_RENDERED_AS_OBSERVED` | nenhuma relação declarada aparece como observada |
| `OBSERVED_EDGE_HAS_LOCATION` | toda relação observada diz ficheiro e linha |
| `BROKEN_POINTER` | nenhuma autoridade presente aponta para caminho inexistente |
| `CONTROL_PLANE_REGISTRY_DRIFT` | o censo corresponde ao registo de hoje |
| `CANONICAL_CONTROL_ENTRYPOINTS` | existe exatamente **uma** sala de controle |

As de cima reprovam sempre. Abaixo delas vive a **dívida medida** — autoridades
fora desta árvore, cópias divergentes, documentos que se dizem lei e não estão no
registo — e essa não exige zero: exige **não piorar**, contra o teto gravado em
`controle/CHAO-DO-CONTROLE.json`.

**«ESTÁ TUDO CERTO» NÃO É EXECUTÁVEL HOJE. «NÃO PIOROU» É.** Exigir zero na
primeira corrida reprovaria o repositório inteiro, e a primeira coisa que alguém
faria era desligar o portão. A dívida fica à vista, com nome e número, em vez de
virar silêncio; quando alguém a pagar, `--fixar` desce o teto — e ele nunca mais
sobe.

---

## ⚖️ A PRATELEIRA TEM DE BATER COM O MAPA

**O visual e o projeto contam a mesma história. Sempre. Sem exceção.**

Cada zona do mapa tem uma pasta no repositório, e todo ficheiro de código vive na
pasta da sua peça:

| passo | zona | pasta |
|---|---|---|
| | **CONTROL PLANE** *(faixa roxa, por cima de tudo)* | |
|  | O REGISTO E A SUA MAQUINA | `controle/` |
|  | INSTRUÇÕES · BÍBLIAS · CONTRATOS · DECISÕES · KNOW-HOW · HANDOFFS · PORTÕES · OBSERVADORES | *(sem pasta — cartões medidos)* |
| | **COLETA** | |
| 1 | O PEDIDO E O PLANO | `pedido/` + `.github/workflows/` |
| 2 | DE ONDE VEM UMA FONTE | `candidatas/` |
| 3 | AS FONTES | `fontes/` |
| 4 | AS FERRAMENTAS | `ferramentas/` |
| 5 | OS VEICULOS | *(sem pasta — cartões medidos)* |
| 6 | AS REGUAS QUE CARIMBAM | `regras/` |
| 7 | AS ACOES DA COLETA | `coleta/` |
| 8 | A PORTA DE ADMISSAO | `admissao/` |
| 9 | AS MEDIDAS DA COLETA | `medidas/` |
| | **A ESPERA** *(faixa cinzenta)* | |
|  | A SALA DE ESPERA | `guarda/` |
| | **INTELIGÊNCIA** | |
|  | LINHAGENS E DONOS | *(sem pasta — cartões medidos)* |
|  | REGUAS E LEIS | `leis/` |
|  | MOTOR — CADEIA V2.1 | `motor/` |
|  | PROVAS E MEDICAO | `provas/` |
| | **ENTREGA** | |
|  | PACOTE CANONICO | `pacote/` |
|  | FRONTEIRA E PORTOES | `portoes/` |
|  | SUPERFICIES | `superficie/` |
|  | AS ONZE FERRAMENTAS DO PORTAL | *(sem pasta — cartões medidos)* |

`P2_PASTA_BATE_COM_MAPA` **reprova** quando um ficheiro está numa gaveta que não é
a da sua peça. Mover ficheiro sem mover a peça reprova. Mudar a peça de zona sem
mover o ficheiro reprova. As duas verdades não voltam a divergir em silêncio.

### O CONTROL PLANE FICA POR CIMA, E NÃO À DIREITA

`COLETA → INTELIGÊNCIA → ENTREGA` é o caminho do dado, e lê-se da esquerda para a
direita. Quem governa esse caminho **não é o passo seguinte dele**:

```
CONTROL PLANE          quem manda      ← faixa roxa, atravessada por cima
─────────────────────────────────────    nenhum dado cruza esta linha
COLETA → … → ENTREGA   a máquina       ← as faixas de sempre
```

Uma quinta família colocada na fila cairia à direita da ENTREGA, e o olho leria
`ENTREGA → CONTROL PLANE` — isto é, que governar é o que se faz depois de
entregar. **Não existe `DADO → CONTROL PLANE`.**

Por isso a faixa do governo é **roxa** (fora da rampa das etapas — nada que corre
é roxo), a seta de governo é **ponto-e-traço** e acaba em **losango**, e não na
ponta de seta do fluxo. Uma ponta de seta diz *«entra aqui»*; governo não entra
em lado nenhum.

| | dono | o que é |
|---|---|---|
| **quem manda** | [`SALA-DE-CONTROLE-SINTONIA.md`](SALA-DE-CONTROLE-SINTONIA.md) | a porta humana — **gerada**, não editar à mão |
| **o registo** | [`controle/AUTORIDADES-CANONICAS.json`](controle/AUTORIDADES-CANONICAS.json) | o índice de quem manda, escrito por gente |
| **a medição** | [`controle/censo_do_controle.py`](controle/censo_do_controle.py) | mede o registo contra esta árvore |
| **os dentes** | [`controle/portao_do_controle.py`](controle/portao_do_controle.py) | reprova quem mentir |
| **os ataques** | [`controle/red_team_do_controle.py`](controle/red_team_do_controle.py) | os doze ataques conhecidos |

**O registo não é uma bíblia, não é o know-how e não é este ficheiro.** Ele não
possui lei nenhuma: possui a lista de quem possui. Um índice que se declarasse
dono do que indexa passaria a competir com o que indexa.

#### Uma relação de governo declarada não é uma relação provada

A lei que já valia para as setas técnicas vale igual aqui, e é a mesma lei:

```
GOVERNS DECLARADA  ≠  GOVERNS OBSERVADA
```

Uma `GOVERNS` só passa a observada quando **o texto da própria autoridade nomeia
o caminho do alvo**, com ficheiro e linha. Não conta o ficheiro existir; não conta
o mundo mencionar o alvo; não conta estar desenhado. Enquanto não houver essa
linha, a seta é `expected` — e `P7_NAO_SEI_VIVE` obriga-a a ficar em NÃO SEI, tal
como obriga qualquer outra.

#### Uma autoridade pode existir no Git e não existir aqui

Foi o que esta faixa encontrou: `BIBLIA-CANONICA-DA-COLETA.md` e
`SINTONIA-EAME-KNOW-HOW.md` estão no repositório e **não estão em `main`**. Um
agente que clone o ramo padrão é mandado consultar ficheiros que ali não existem.

O registo diz onde cada autoridade realmente vive (`CANONICAL_REF`), e o censo
vai lá medir. **Medir noutra ref não a traz para cá — só diz onde ela está.** O
cartão dela fica 🔴 `ABSENT_FROM_SNAPSHOT`, que é a verdade.

### Não existe mais `scripts/`

Uma pasta com 149 ficheiros empilhados deixava o mapa dizer "isto é uma regra" e
"aquilo é uma ferramenta" sem que nada no repositório confirmasse. Quem abria a
pasta via a verdade errada primeiro.

**Ficheiro novo vai direto para a gaveta do que ele é.**

### Ferramenta, veículo e ação são TRÊS coisas

Esta pergunta já foi respondida errado uma vez, e a gaveta chamada «OS VEÍCULOS»
passou meses sem conter um único veículo — as oito peças lá dentro eram todas
ações. O teste que eu usava (*«sai para a rede?»*) não separava nada: sair para a
rede é o que uma **ação faz**, não o que um **veículo é**.

| | pergunta | exemplos | gaveta |
|---|---|---|---|
| **FERRAMENTA** | com **que** se viaja | Apify, o navegador, a transcrição, abrir PDF | `ferramentas/` |
| **VEÍCULO** | de **onde** o dado vem | YouTube, Instagram, LinkedIn, Facebook, HTTP | — |
| **AÇÃO** | quem **vai buscar** e **guarda** | colher o YouTube, baixar os rótulos | `coleta/` |

**A seta segue o dado, e o dado VEM do canal — não vai para ele.** A ação chama o
YouTube (isso é controlo), mas o que atravessa a linha é a colheita, e ela corre
no sentido contrário: `YOUTUBE → Colher o YouTube → o ficheiro onde ela guarda`.
Por isso o veículo vem **antes** da ação: ele é o início do caminho, não o fim.

Ação é **verbo**. Se o nome começa por «colher», «baixar», «montar», «ler» — é
ação, mesmo que o canal esteja no nome dela. O veículo é o **lugar**.

Os cartões de veículo **não se escrevem à mão**: nascem de procurar o canal
dentro do código de cada ação, e cada seta carrega o ficheiro e a linha onde ele
aparece. Canal que ninguém chama fica em NÃO SEI, e é a verdade.

### Régua que carimba não é régua que mede

`regras/` e `medidas/` são coisas diferentes, e juntá-las escondia a mais
importante das duas:

| | quando trabalha | exemplos | gaveta |
|---|---|---|---|
| **CARIMBA** | no momento em que o item entra | de onde veio, quem está autorizado, as palavras, o contrato da fonte | `regras/` |
| **MEDE** | depois, olhando para trás | o padrão da coleta, a saúde de cada fonte | `medidas/` |

**Medir não é filtrar.** Uma régua que mede não barra nada — ela conta quanto
falta. Pô-la antes das ações faz parecer que há peneira onde só há termômetro, e
foi exatamente essa confusão que deixou a coleta anos sem porta de admissão.

A divisão é **medida**, não escolhida: carimba quem é usada por uma ação no
momento em que ela colhe. O teste `regua_que_carimba_nao_e_regua_que_mede`
reprova se a gaveta deixar de bater com a medição.

### Fonte nasce; não aparece pronta

`candidatas/` vem **antes** de `fontes/`, e não é redundância:

- **candidata** — apareceu no meio de uma coleta ou à mão, ainda não se sabe o
  que entrega;
- **fonte** — já foi aberta, olhada, e há prova guardada do que ela entrega.

Fonte nova entra sempre por `candidatas/`. Escrever ficha em `fontes/` sem passar
por ali é dizer que se sabe o que ela entrega sem ter olhado.

### A SALA DE ESPERA é cinzenta de propósito

Entre a coleta e a inteligência há uma faixa neutra: o que já foi colhido, limpo
e guardado, à espera de ser processado. **Não é coleta** (o trabalho acabou) e
**não é inteligência** (ainda não começou). Enquanto viveu pintada de azul, o mapa
dizia que guardar era colher.

Nada é transformado ali — só guardado. Por isso não tem cor de etapa.

### As gavetas ficam na RAIZ, e isso não é gosto

90 dos ficheiros acham a raiz do projeto com
`dirname(dirname(abspath(__file__)))` — sobem duas pastas. De `coleta/x.py` isso
dá na raiz, tal como dava de `scripts/x.py`. Se as gavetas estivessem dentro de
`scripts/`, esses 90 passariam a apontar para o sítio errado e escreveriam dado
onde não devem — **sem dar erro**.

### País dentro da gaveta

Peça que serve **um país só** mora em `<gaveta>/<país>/`:

```
guarda/es/adama_es_gate.py      a gaveta é `guarda` — a etapa
coleta/es/corpus_es.py          `es` vem depois — o país
```

**A gaveta continua dizendo a ETAPA.** O país entra depois dela, e por isso
`P2_PASTA_BATE_COM_MAPA` continua valendo — ela olha o primeiro pedaço do caminho.

Peça que serve mais de um país, ou nenhum, fica na raiz da gaveta. Não invente
subpasta de país para uma peça transversal: `TRANSVERSAL` é a verdade sobre ela.

**Descer um nível muda a profundidade.** `dirname(dirname(abspath(__file__)))`
de `guarda/x.py` dá a raiz; de `guarda/es/x.py` dá `guarda`. Cada ficheiro que
desce ganha um `dirname` a mais — senão escreve dado dentro da gaveta e **não dá
erro nenhum**.

### Três estados, e não dois

| estado | o que quer dizer |
|---|---|
| `official` | rota de hoje |
| `futuro` | construído e provado, **guardado à espera do seu momento** |
| `legacy` | ficou para trás |

`futuro` e `legacy` não são a mesma coisa, e confundi-las custa caro: legado é o
que morreu; futuro é o que está pronto e parado. Marcar o piloto de Espanha como
legado seria enterrá-lo vivo.

### Import entre gavetas

Os scripts importam-se pelo nome curto (`import proveniencia`). Como cada um vive
agora na sua gaveta, quem precisa de um vizinho de outra gaveta leva duas linhas
à vista, no topo:

```python
sys.path.insert(0, os.path.dirname(HERE))   # a raiz
import _gavetas  # noqa: E402,F401 — poe as gavetas do processo no caminho
```

[`_gavetas.py`](_gavetas.py) é o **único** sítio com a lista das gavetas. O
scanner do mapa lê-a de lá. Duas listas seriam duas verdades.

---

## TRAZER FICHEIRO DE OUTRA BRANCH — compare antes

Este repositório tem 68 branches, e **uma branch mais antiga pode conter uma versão
mais velha do mesmo ficheiro**. `git checkout <branch> -- <ficheiro>` sobrescreve
sem perguntar e sem avisar.

Aconteceu nesta missão: ao trazer `sintonia-scrap.yml` da branch antiga, veio junto
um `PORTOES-DE-COLETA-10B.md` **54 linhas mais curto** — apagando o registo inteiro
da verificação adversarial da Missão 10C. O `git diff --stat` mostrou; se ninguém
tivesse olhado, a prova de que seis dos sete portões foram refutados teria sumido.

**Antes de trazer, compare. Depois de trazer, confira o que saiu:**

```bash
git diff --numstat origin/main -- . | awk '$2>0 {print "APAGOU "$2" linhas: "$3}'
```

Linha apagada que você não pretendia apagar é regressão, mesmo quando o ficheiro
é "só documentação". Documentação apagada não dá erro em teste nenhum.

---

## VAI COLETAR? COMECE POR UMA PORTA SÓ

```
regras/LEIA-ANTES-DE-COLETAR.md
```

Toda missão de coleta começa procurando as réguas, e cada uma procura num sítio
diferente — uma acha a procedência, outra acha a regra de coleta externa, outra
não acha nada e **reinventa a lei**. A lei reinventada nunca é igual à que já
existia.

Esse ficheiro é **gerado do mapa**: lista toda régua da coleta, o que ela manda e
o ficheiro onde ela vive. Régua nova aparece lá sozinha; régua apagada some de
lá. Não fica parágrafo órfão mandando em ninguém.

Ele entra na verificação anti-drift — porta de entrada desatualizada é pior que
nenhuma, porque quem a lê acredita nela.

---

## FONTE NOVA — a porta, e a escada

O acervo de fontes é **capital parado**: consulta-se antes de coletar, não se
coleta para descobrir o que já se sabe. Fonte nova entra por uma porta só:

```bash
py candidatas/fonte_nova.py --tipos     # os tipos aceites
py candidatas/fonte_nova.py --listar    # a fila, agrupada por tipo
```

**O que entra pela porta é candidata, nunca fonte.** Escrever direto no
`ATLAS-DE-FONTES-EAME.md` é afirmar que existe uma fonte sem ninguém ter olhado —
e o próprio atlas proíbe isso: *"uma linha só existe aqui depois que alguém abriu
a fonte, olhou o que ela entrega e guardou evidência disso."*

| # | degrau | mora em | sobe escrevendo |
|---|---|---|---|
| 1 | **CANDIDATA** | `candidatas/FONTES-CANDIDATAS.json` | a ficha no atlas, com exemplo real |
| 2 | **REGISTADA** | `docs/fontes/ATLAS-DE-FONTES-EAME.md` | o contrato de busca |
| 3 | **CONTRATADA** | `docs/operacao/CONTRATOS-DAS-FONTES-EAME.md` | o workflow que a roda sozinha |
| 4 | **AUTOMÁTICA** | `.github/workflows/` | — |

`--para-que` é obrigatório: fonte sem uso declarado vira entulho.
`docs/fontes/INDICE-DE-FONTES.md` é **gerado** — não o edite à mão.

---

## O QUE O STATUS SIGNIFICA

| | | |
|---|---|---|
| 🟢 | `PROVEN` | a prova própria do tipo de peça passou, e a descrição humana ainda vale |
| 🟡 | `PENDING` | existe e está ligada, mas falta a prova própria do tipo — ou o ficheiro mudou depois da última leitura humana |
| 🔴 | `BROKEN` | foi declarada no mapa e não existe no repositório |
| ⚪ | `UNKNOWN` | **NÃO SEI** — existe, e nada aponta para ela nem ela aponta para nada |

**Verde nunca significa "o ficheiro existe".** Existir é o mínimo para não ser
vermelho, não um motivo para ser verde. A prova exigida é diferente por tipo de
peça — exigir de um teste a mesma prova que de um artefato seria exigir o
impossível de um deles. As regras estão em `prova_do_tipo()` no gerador.

---

## MUDAR PELO MAPA — NÃO

A interface é **leitura**. Clicar nela não altera código, e não deve passar a
alterar. A ordem é sempre:

```
agente → implementação no repo → testes → commit → CI → mapa regenerado
```

Nunca `browser → desenha seta → vira verdade`.

---

## LEIS DO SINTONIA QUE O MAPA NÃO PODE VIOLAR

O mapa é mais um consumidor destas leis, não uma exceção a elas:

- NÃO SEI continua NÃO SEI;
- ausência não vira negativo; sinal não vira pedido; oportunidade não vira pedido;
- ciência não vira incidência de campo;
- data regulatória não vira janela agronómica;
- fonte/location do documento não vira local do fato;
- publicação não vira *fact time*;
- *generated artifact* não vira dono da lei;
- consumidor não vira dono do gerador;
- tela não recalcula decisão do motor;
- contrato tem um dono; snapshot é derivado;
- código não é deformado para deixar o mapa verde.

---

## RELAÇÃO COM OS OUTROS FICHEIROS

| ficheiro | papel |
|---|---|
| **`AGENTS.md`** (este) | **dono da lei do mapa** |
| [`CLAUDE.md`](CLAUDE.md) | instruções permanentes do projeto; aponta para aqui |
| [`README.md`](README.md) | método e estados de evidência; aponta agentes para aqui |
| [`system-map/README.md`](system-map/README.md) | como o mapa funciona por dentro |

**Um dono. Múltiplos ponteiros.** Não copie esta lei para outro ficheiro: uma
lei em dois sítios diverge, e a partir daí nenhuma das duas vale.
