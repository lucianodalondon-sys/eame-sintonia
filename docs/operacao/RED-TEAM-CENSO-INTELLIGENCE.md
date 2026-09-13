# RED TEAM DO CENSO DA INTELLIGENCE

```
MISSAO     C-INT-CENSUS-01 · 2026-09-13
ALVO       o proprio censo, e nao a maquina
```

> Um red team que só confirma o que já se acreditava não é um red team.
> **Quatro destes doze ataques derrubaram uma conclusão minha**, e o censo foi
> corrigido antes de fechar. Ficam escritos com o erro à vista.

---

## ATAQUE 1 · «chamou módulo existente de peça funcional sem provar chamador»

**DEFENDIDO.** Nenhuma peça foi marcada operacional por existir. `C-V2-LEGADO` tem
7 ficheiros que compilam e está classificado `ORPHAN_LEGACY`, porque a busca por
referências deu zero fora do mapa. As 5 peças `CONNECTED_STATIC` dizem-no no nome:
têm chamador **estático**, e nada além disso.

---

## ATAQUE 2 · «chamou import de fluxo»

**DEFENDIDO, e virou achado contra o mapa.** Nenhuma aresta deste censo foi
promovida a fluxo por um import. Ao classificar as 135 linhas de evidência do
próprio System Map, saiu isto:

```
co-acesso a ficheiro   56
linha de workflow      45
import                 34
chamada de funcao       0
```

O ataque não me apanhou a mim — apanhou **o instrumento**. 56 das 135 «provas» do
mapa são duas peças a nomearem o mesmo JSON.

---

## ATAQUE 3 · «contou documentação como execução»

**DEFENDIDO.** O classificador separa `RUNTIME`, `WORKFLOW`, `TEST`, `PROVA`, `DOC`,
`PORTAL` e `SYSTEM_MAP`, e só `RUNTIME + WORKFLOW` contam como referência de
máquina. `C-CADEIA-V21` tem 10 referências em `docs/` e nenhuma delas entrou na
coluna de chamador.

---

## ATAQUE 4 · «contou o System Map como prova da máquina que ele descreve»

**❌ DERRUBOU-ME. Corrigido.**

A primeira corrida deu `C-V2-LEGADO` com 7 referências de `PORTAL`, o que o teria
salvo de ser órfão. Verificadas uma a uma, **todas** vinham de
`italia-portale/client/system-map/state.generated.json` — que é a **cópia do mapa**
que o build serve à Vercel.

```
O MAPA A FALAR DE UMA PECA NAO E A MAQUINA A USA-LA.
```

Conserto no **medidor**, e não na prosa: `client/system-map/` passou a classificar
como `SYSTEM_MAP`. Com o conserto, `C-V2-LEGADO` caiu para zero referências e ficou
órfão, que é a verdade.

---

## ATAQUE 5 · «contou duas rotas do mesmo origin como duas fontes independentes»

**DEFENDIDO, com um risco registado.** O único caso candidato são os três
`lineage_*`, que apontam para **um único ficheiro**. Não foram contados como três
fontes: estão marcados `POSSIBLE_DUPLICATE` e a partilha está escrita.

O risco a registar é `italy-v21.js` × `italy-handoff-v21.js`: dois pacotes de
inteligência que definem a **mesma global**. Hoje só um é carregado.

---

## ATAQUE 6 · «chamou output antigo de runtime atual»

**❌ DERRUBOU-ME. Corrigido.**

Medi que o `BUILD_ID` mais frequente da árvore era `V21-843baf4229d93598` (36
ocorrências), e que o contrato esperava `V21-06c6421d001ea52a`. Concluí que havia
um portão contornado, e ia escrevê-lo como achado grave.

Errado. Corri o portão:

```
node italia-portale/audit/build-gate.mjs  →  exit 0
  PASS ARTEFACTO_SERVIDO_E_CANONICO  [V21-06c6421d001ea52a]
```

O portão confere `italy-handoff-v21.js`, **outro ficheiro**, com o `BUILD_ID`
canónico. O `V21-843baf...` vive em `italy-v21.js`, que nenhuma página carrega.

```
DOIS FICHEIROS COM NOMES PARECIDOS NAO SAO O MESMO FICHEIRO.
```

O achado sobreviveu, mas mudou de espécie: de «portão contornado» para «artefacto
órfão de 10 MB». A diferença entre os dois é a diferença entre um alarme e um facto.

---

## ATAQUE 7 · «chamou branch isolada de estado integrado»

**❌ DERRUBOU A PREMISSA DA MISSÃO, e está no topo do censo.**

Não há «o» System Map. Três linhas, três mapas, três contagens (12 · 30 · 29). As
duas principais divergiram a 2026-09-07 e nenhuma contém a outra. Se eu tivesse
censado a árvore onde estava a trabalhar, teria dado 30 peças — e estaria a
descrever uma linha de governança, não a máquina.

```
UM NUMERO DE PECAS SEM A LINHA EM QUE FOI MEDIDO NAO E UM NUMERO.
```

---

## ATAQUE 8 · «classificou algo como Intelligence só porque tem a palavra no nome»

**DEFENDIDO.** A população não veio de `grep intelligence`. Veio do mecanismo do
próprio mapa (`componente.territory → territory.family`), extraído
programaticamente. Nenhuma peça entrou por nome.

O contra-exemplo está dentro do universo: `motor/cadeia_canonica.sh` está numa peça
de Intelligence e **aplica migrations de banco**. Entrou por classificação, e o
censo diz que a classificação está errada — em vez de a aceitar por estar lá.

---

## ATAQUE 9 · «ignorou uma peça porque ela não tem intelligence no path»

**PARCIALMENTE PROCEDENTE, e assumido.** O censo tem 12 peças porque o mapa tem 12.
Mas a matriz de conceitos mostra que a massa de `OPPORTUNITY`, `PORTFOLIO`,
`SCIENCE` e `SIGNAL` vive em `italia-portale/`, `data/` e `build/` — fora da família.

```
A INTELLIGENCE DO MAPA TEM 12 PECAS.
OS CONCEITOS DELA VIVEM SOBRETUDO NA ENTREGA E EM DADOS CONGELADOS.
```

Não mudei a classificação para melhorar o censo — a missão proíbe, e com razão. Fica
como achado.

---

## ATAQUE 10 · «chamou UNKNOWN de ausência»

**❌ DERRUBOU-ME. Corrigido.**

Primeira varredura da fronteira: **18** ficheiros do motor «tocam Collection». Ia
escrever 18 caminhos paralelos.

Medidas as **importações** por AST em vez das menções por texto, restou **uma**:
`motor/normalize_agro.py` → `coleta/eppo_gd.py`. As outras 17 escreviam a palavra
num comentário ou numa string.

```
NOMEAR UMA GAVETA NAO E IMPORTAR DELA.
```

É a terceira vez nesta sessão que o mesmo erro aparece com outra roupa: casar com a
**menção** quando a pergunta era sobre o **comportamento**.

E o inverso também foi respeitado: os conceitos sem dono provado ficaram `NÃO SEI`,
e não «sem dono». `NÃO SEI` aparece 11 vezes na matriz de conceitos.

---

## ATAQUE 11 · «chamou ZERO de zero sem universo»

**DEFENDIDO, com o universo declarado.** Os dois zeros do censo são:

```
COLLECTION_GAP   = 0 ficheiros
INTELLIGENCE_RUN = 0 ficheiros
```

Universo: **1 596 ficheiros de texto** da árvore funcional, excluindo `.git`,
`node_modules`, `BASELINE`, binários, o System Map e a sua cópia. O padrão de busca
está escrito no instrumento e cobre as duas grafias (`_` e `-`).

```
ZERO_SEMANTICS_SAFE = YES para estes dois. UNIVERSE_PROVEN = YES.
```

Já os «zeros» de segurança são mais fracos e dizem-no: `0 segredos` e `0 chamadas de
rede` valem **para as 12 peças**, e não para a árvore inteira.

---

## ATAQUE 12 · «ignorou colisão ONE CONCEPT → ONE OWNER»

**DEFENDIDO.** Duas colisões provadas, ambas escritas com ficheiro e linha:

1. **gerador canónico** — `motor/v21_cadeia.sh:35,47` diz `55c2674`;
   `CANONICAL-PACKAGE-CONTRACT.json` diz `51010733` e lista a safra de `55c2674`
   como velha.
2. **OPPORTUNITY** — calculada em `motor/`, com a maior massa em `italia-portale/`.

Na primeira arbitrei, e disse por que meio: **ganha o documento que um portão
executa**, porque esse é o que decide na prática. Na segunda **não** arbitrei:
`PROVEN_OWNER = NÃO SEI`, porque escolher exigia ler três camadas e isso é
arbitragem, não censo.

```
NAO ESCOLHER O FAVORITO EM SILENCIO E PARTE DO TRABALHO.
```

---

## PLACAR

```
ATAQUES              12
DEFENDIDOS            8
DERRUBARAM O CENSO    4   (4 · 6 · 7 · 10)
CORRIGIDOS ANTES DE FECHAR  4
```

Os quatro que passaram têm todos a mesma forma: **eu tratei uma semelhança de texto
como se fosse um facto de comportamento.** Cópia do mapa lida como uso; nome
parecido lido como mesmo ficheiro; branch onde eu estava lida como a árvore; menção
lida como importação.

```
O ATALHO MAIS CURTO ENTRE UMA PERGUNTA E UMA RESPOSTA
E UM GREP — E E POR ISSO QUE ELE E O QUE SE ANDA SEM QUERER.
```
