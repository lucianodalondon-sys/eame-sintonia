# KNOW-HOW DELTA — A ESPINHA COMUM DA INTELLIGENCE

```
MISSAO       C-INT-SPINE-01
MEDIDO_EM    2026-09-14
ESPECIE      DELTA. NAO E O KNOW-HOW.
APLICAR_EM   claude/sintonia-eame-know-how-v1 : SINTONIA-EAME-KNOW-HOW.md
```


---

> # ⚠️ ESTE DELTA FOI APLICADO — E A SUA PREMISSA ERA FALSA
>
> ```
> APLICADO_EM   SINTONIA-EAME-KNOW-HOW.md §111-§113
> POR           C-INT-ATOMICITY-01, 2026-09-14
> ```
>
> A secção seguinte diz que este delta vive em `handoff/` porque a branch da
> espinha **não tinha ancestral comum** com o know-how. **Isso estava errado.**
> A causa foi medida: o clone era raso (`.git/shallow` enxertado em `472b4f9d`,
> 2026-09-06) e o ancestral comum — `96933996`, 2026-08-29 — ficava abaixo do
> corte.
>
> ```
> git fetch --unshallow
> git merge-base <espinha> <know-how>   ->   96933996
> ```
>
> O raciocínio de não fundar um segundo know-how continua certo. **A medição que
> o motivou não.** Fica escrito aqui em vez de ser apagado: o §111 do know-how
> canónico nasceu deste erro, e apagá-lo apagaria a razão de ele existir.
>
> ```
> UMA CORRECCAO QUE APAGA O ENGANO APAGA TAMBEM A LICAO.
> ```

---


# POR QUE ISTO É UM DELTA, E NÃO UMA SECÇÃO ESCRITA

O know-how canónico vive em `claude/sintonia-eame-know-how-v1 @ 338e171a`, e a
branch desta missão **não tem ancestral comum com ela** — `git merge-base`
devolve vazio. Escrever a secção aqui criaria um segundo know-how numa árvore
que nem sequer contém o primeiro.

```
ESCREVER UM §NOVO NUMA BRANCH QUE NAO CONTEM O FICHEIRO
NAO E ATUALIZAR O KNOW-HOW: E FUNDAR O SEGUNDO.
```

É o mesmo raciocínio que levou `5ace34a8` a pôr o `§108` em `handoff/`.

## A NUMERAÇÃO — MEDIDA, NÃO HERDADA DO ENUNCIADO

```
git show origin/claude/sintonia-eame-know-how-v1:SINTONIA-EAME-KNOW-HOW.md \
  | grep -n '^# §'   | tail -1

12762:# §110 · PROVA DENTRO DO PROCESSO NAO E DURABILIDADE OPERACIONAL
```

```
TAIL_MEDIDO   §110
PROXIMO       §111  — SE nada mais tiver entrado entre esta medicao e a aplicacao.
              QUEM APLICAR: RE-LER O TAIL. Nao herdar este numero.
```

O enunciado desta missão falava de `§109`, `§110`, `§111` — e mandava, com
razão, não os herdar. Medidos: `§109` e `§110` já existem.

---

# §NEXT · UMA MEDIÇÃO CORRECTA SOBRE UMA FOTOGRAFIA INCOMPLETA PRODUZ UMA CONCLUSÃO ERRADA — E PARECE RIGOROSA

## O QUE MUDOU

A arbitragem `C-INT-ARB-01` declarou, em `INTELLIGENCE-CONCEPT-OWNERSHIP-V1.json`:

```
COLLECTION_GAP
  OWNER = INTELLIGENCE
  CURRENT_IMPLEMENTATION = NAO IMPLEMENTADO — 0 ficheiros na arvore
```

Está correto. E leva a uma conclusão errada.

O conceito **já tem dono**, e tem-no desde `220e0e7a`, 2026-09-08:

```
leis/gestao_da_coleta.py    CONTRATO = 'GESTAO_DA_COLETA/v1'

  CAMPOS_DA_NECESSIDADE   REQUIREMENT_ID · O_QUE · JANELA · FRESCURA_EXIGIDA ·
                          GRAO · PORQUE_IMPORTA · POLICY_VERSION
  CAMPOS_DA_FALTA         GAP_ID · SATISFACTION_STATE · O_QUE_FALTA · ...
  DECISOES                COLLECT_NOW · COLLECT_LATER · DO_NOT_COLLECT ·
                          NEEDS_HUMAN · DEFER_UNKNOWN
  A FRONTEIRA             «O GESTOR DECIDE O QUE E QUANDO;
                           O ORQUESTRADOR DECIDE COMO E POR ONDE»
```

## POR QUÊ

`git cat-file -e origin/claude/funny-hypatia-y7ho5s:leis/gestao_da_coleta.py` → **não existe**.

A branch onde a arbitragem foi feita **não contém o ficheiro**. O `grep` foi
honesto, a fotografia é que estava incompleta. E a arbitragem não podia saber:
ela mediu o que conseguia ver.

## PROVA

```
grep COLLECTION_GAP  em dc00583d              ->  0 ficheiros   (verdade)
grep GAP_ID          em dc00583d              ->  4 ficheiros
                                                  leis/gestao_da_coleta.py  <-- o dono
                                                  provas/os_portoes_da_collection.py
                                                  tests/test_portoes_da_collection.py
                                                  data/derivados/COLLECTION-V1-CLOSE-GATES.json
git log --diff-filter=A -- leis/gestao_da_coleta.py   ->  220e0e7a  2026-09-08
git cat-file -e 87712a01:leis/gestao_da_coleta.py     ->  ausente
```

## CONSEQUÊNCIA

**Duas, e a segunda é maior que a primeira.**

### 1 · `COLLECTION_GAP` parte-se em dois donos

```
INTELLIGENCE_REQUIREMENT     dono: INTELLIGENCE
                             a pergunta que a evidencia nao sustenta,
                             com janela, grao, frescura e porque importa

GAP · SATISFACTION · DECISION · ROTA · EXECUTOR
                             dono: COLLECTION (GESTAO_DA_COLETA/v1)
```

Um nome único cobria dois conceitos com donos diferentes. O `ONE CONCEPT → ONE
OWNER` estava a ser violado **ao contrário do habitual**: não havia dois donos
para um conceito; havia um nome para dois.

### 2 · Um `grep` num censo só vale dentro da fotografia onde correu

```
CONTROL_PLANE_ATOMICITY = FAIL NAO E UMA QUEIXA DE ARRUMACAO.
E UMA MEDIDA DE QUANTAS DAS NOSSAS MEDICOES PODEM ESTAR ERRADAS.
```

Um censo escrito numa branch lateral carrega um pressuposto invisível: *o que
eu não vejo não existe*. Quando as autoridades vivem em cinco branches
desconexas, esse pressuposto é falso em cinco direções ao mesmo tempo.

**Regra a adoptar:** todo censo/arbitragem declara, no topo, contra que commit
correu — e essa declaração é parte do resultado, não do cabeçalho.

```
UM CENSO SEM A FOTOGRAFIA DECLARADA E UM NUMERO SEM DENOMINADOR.
```

---

# §NEXT+1 · UM PORTÃO QUE SÓ SE SATISFAZ À MÃO NÃO É UM PORTÃO: É UM LEMBRETE

## O QUE MUDOU

`scripts/metricas_canonicas.py --sync` reescreve todo número publicado a partir
do seu dono. `tests/test_handoff.py` exige que `HANDOFF-...md` e
`PROMPT-...md` publiquem a contagem de testes atual.

Mas `sync()` só percorria `docs/`. **Os dois ficheiros estão na raiz.**

```
O TESTE EXIGIA O NUMERO CERTO.
O SINCRONIZADOR NAO CHEGAVA LA.
LOGO O UNICO JEITO DE PASSAR O PORTAO ERA DIGITAR O NUMERO
— EXACTAMENTE O QUE O LEDGER EXISTE PARA IMPEDIR.
```

O defeito era invisível enquanto ninguém acrescentasse testes. Esta missão
acrescentou 39, e ele apareceu.

## PROVA

```
python3 -m unittest discover -s tests    antes:  329, OK
                                         depois: 368, 6 falhas de metrica
python3 scripts/metricas_canonicas.py --sync
                                         corrigiu 6 documentos em docs/
                                         e NENHUM na raiz
                                         -> 1 falha, insatisfazivel sem digitar
```

E um segundo defeito, latente por trás do primeiro: ao alargar o walk à raiz, o
`--sync` rebentou com

```
ValueError: Cannot specify ',' with 's'
```

porque `HANDOFF-...md` contém `<!--M:NOME-->` — que é o **exemplo da sintaxe**,
escrito em prosa. O `repl()` tentava reformatar a própria string.

```
UM SINCRONIZADOR NAO REESCREVE O QUE NAO SABE DERIVAR.
```

## CONSEQUÊNCIA

Três correções **na fonte**, nunca no número:

1. `_marcados()` inclui os `.md` da raiz;
2. `repl()` devolve o marcador intacto quando a métrica não tem dono no ledger;
3. os dois números da raiz ganharam marcador, e o teste aceita o marcador
   continuando a exigir o valor certo.

```
UM NUMERO DIGITADO ENVELHECE EM SILENCIO — E UM PORTAO QUE OBRIGA
A DIGITA-LO ENVELHECE COM ELE.
```

---

# §NEXT+2 · UM ESTADO QUE NÃO TEM ONDE SER ESCRITO NÃO EXISTE, POR MAIS LEI QUE TENHA

## O QUE MUDOU

A espinha comum da Intelligence foi arbitrada e provada em máquina de estados
descartável: sete portões, quinze conceitos com dono, 39 provas, 0 ataques
sobreviventes como argumento.

E o portão `G0` — o primeiro de todos — **recusa tudo**.

## POR QUÊ

```
admissao.pronto_para_inteligencia()  ->  12 campos
EVIDENCE_SPECIES                     ->  nao e um deles
```

Do lado da Intelligence, hoje, um boletim agroclimático e um relato de campo
são o mesmo texto. `AGROCLIMATIC_SIGNAL != PEST_OCCURRENCE` está escrita nos
contratos das fontes `IT-T2-001/002` — e não atravessa a fronteira.

## PROVA

`tests/test_espinha_da_intelligence.py::FronteiraMedida`, três testes:

```
o contrato de entrada tem DOZE campos
nenhum dos 8 campos agronomicos necessarios esta entre eles
o item real de hoje NAO PRODUZ SINAL — produz um REQUISITO
```

E este último é deliberadamente frágil: **se o contrato READY passar a
transportar a espécie, o teste falha** — e falhar é o comportamento certo. É o
sinal de que o bloqueio caiu.

## CONSEQUÊNCIA

```
UM PORTAO QUE NAO RECEBE O DADO NAO RECUSA: DEIXA PASSAR.
E UM QUE RECUSA TUDO POR OMISSAO E HONESTO, E NAO E UTIL.
```

A distinção que isto obriga a fazer, e que vale para lá da Intelligence:

```
LEI ESCRITA            != LEI QUE ATRAVESSA A FRONTEIRA
CONTRATO TEM O CAMPO   != A ROTA POE O CAMPO NO ITEM
```

A régua de doença fica onde o benchmark agro a deixou — `NIVEL 2` — e esta
missão **confirma** o tecto em vez de o mover. Subir exige matéria-prima, e a
matéria-prima de `NIVEL 3` é dado do agricultor: problema de contrato, não de
engenharia.

---

# §NEXT+3 · TRÊS NOMES QUE PARECIAM ESTÁGIOS E ERAM OUTRA COISA

## O QUE MUDOU

O enunciado propunha dez estágios. Três não sobreviveram como entidade, e a
razão é a mesma nos três: **o conceito já tinha dono com outro nome.**

```
EVIDENCE            ja e o READY_ITEM             dono: COLLECTION
JUDGMENT            ja e metade do FINDING        «FINDING / ANALYTIC_JUDGMENT»
VALIDATION_QUEUE    ja e um ESTADO no objeto      a fila e a leitura dele
CANDIDATE_FINDING   ja e a ANALYTIC_HYPOTHESIS    mesmo objeto, nome existente
```

## POR QUÊ

O teste que cada um falhou é o mesmo:

```
1. Que pergunta deixa de ter resposta se este estagio nao existir?
2. Ja existe um objeto que responde a essa pergunta?
```

Nenhum dos quatro passou o `2`.

## PROVA

Estrutural, e é a parte que interessa guardar: **a recusa está no desenho das
classes, não numa regra a correr.**

```
Cruzamento   nao tem campo APOIA/CONTRADIZ/SUFICIENTE/CONCLUSAO/VEREDITO
             -> nao consegue julgar, e o teste falha se alguem lho acrescentar
fila         e uma list comprehension, sem id e sem persistencia
             -> nao consegue divergir do objeto
ItemPronto   e frozen
             -> a Intelligence nao consegue reescrever identidade upstream
Requisito    recusa 12 palavras da Collection
             -> nao consegue nomear uma rota
```

## CONSEQUÊNCIA

```
UMA LEI QUE CORRE E UMA LEI QUE ALGUEM PODE ESQUECER DE CHAMAR.
UMA LEI QUE E A FORMA DO OBJETO NAO SE ESQUECE:
O CODIGO NEM COMPILA A VIOLACAO.
```

E o corolário para quem desenhar o `INTELLIGENCE_RUN` produtivo: **antes de
criar um estado, procurar quem já responde àquela pergunta.** Cinco recusas
contra dois acréscimos foi o saldo desta missão, e os dois acréscimos
(`SCREENING`, `INTELLIGENCE_REQUEST`) têm origem externa medida ou já estavam
arbitrados.

---

# O QUE ESTE DELTA **NÃO** AUTORIZA

```
NAO promove a BIBLIA-DE-ENGENHARIA-DA-INTELLIGENCE
NAO implementa INTELLIGENCE_RUN
NAO altera a Collection, a Sala de Espera nem o Portal
NAO decide RELEVANCE nem PRIORITY
NAO cria Disease/Climate/Market/Science Intelligence
```

---

# ARTEFATOS DESTA MISSÃO

```
research/intelligence/INTELLIGENCE-SPINE-CONTRACT-V1.md       a espinha e os contratos
research/intelligence/INTELLIGENCE-SPINE-ARBITRATION-V1.json  arbitragem, em maquina
research/intelligence/RED-TEAM-INTELLIGENCE-SPINE-V1.md       14 ataques · 11 KILLED
provas/espinha_da_intelligence.py                             a maquina de estados
tests/test_espinha_da_intelligence.py                         P1..P12 · 39 testes
```

```
KNOW_HOW_DELTA = ATUALIZACAO NECESSARIA
CONTROL_PLANE_ATOMICITY = FAIL
```
