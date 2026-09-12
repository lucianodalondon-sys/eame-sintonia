# CLAUDE.md — instruções permanentes do SINTONIA EAME

> ## ⚖️ LEI OBRIGATÓRIA DO PROJETO
>
> **Leia [`AGENTS.md`](AGENTS.md) antes de fazer qualquer alteração.**
>
> O SINTONIA System Map tem de continuar sincronizado com **toda** mudança
> relevante de arquitetura. **Rode o validador do System Map antes de fechar a
> tarefa:**
>
> ```bash
> py system-map/scripts/generate_system_map.py
> py system-map/scripts/validate_system_map.py
> ```
>
> A lei inteira vive em `AGENTS.md` e **não** é repetida aqui — uma lei em dois
> sítios diverge, e a partir daí nenhuma das duas vale.

---

Este arquivo é o **dono canônico** das instruções permanentes para o Claude Code neste
repositório. Regra registrada aqui vale para **todas as missões futuras** e não depende de
alguém lembrar dela na conversa.

Método, estados de evidência e disciplina `SOURCE → EVIDENCE → … → PORTAL` continuam em
[`README.md`](README.md). Este arquivo não os repete.

---

## LEI DE FOCO, ENCERRAMENTO E ENTREGA — A MISSÃO NÃO PODE ENGOLIR O PROJETO

```
MISSÃO TEM UM OBJETIVO.
VAI ATÉ ELE.
PROVA.
ENTREGA.
PARA.
```

O SINTONIA existe para **funcionar e gerar valor**, não para transformar cada achado numa
nova frente de engenharia. Engenharia rigorosa continua obrigatória; perfeccionismo sem
critério de saída, não.

**Prazo do cliente é requisito de engenharia.** Não autoriza quebrar contrato, identidade,
procedência, segurança ou prova; mas obriga a escolher o **menor caminho seguro que entrega o
objetivo pedido**.

### 1. Toda missão nasce com uma pergunta principal e um fim mensurável

Antes de tocar no código, declarar:

- `OBJECTIVE` — o que esta missão precisa fazer funcionar;
- `PASS` — qual prova encerra a missão;
- `IN_SCOPE` — o que pode mudar para atingir esse objetivo;
- `OUT_OF_SCOPE` — o que não será puxado para dentro;
- `HARD_STOP` — onde termina depois da prova.

Se o objetivo puder ser cumprido com segurança, a missão **não continua** só porque encontrou
algo que também poderia ser melhorado.

### 2. Achado novo não vira missão automaticamente

Todo achado durante a execução recebe uma destas classes:

- `BLOCKER_DO_OBJETIVO` — impede a missão atual de funcionar ou tornaria a entrega insegura;
- `DEFEITO_RELEVANTE_MAS_NAO_BLOQUEANTE` — existe, deve ser registado, mas não impede a entrega;
- `MELHORIA` — deixaria melhor, mais elegante, mais rápido ou mais completo;
- `FORA_DO_ESCOPO` — pertence a outro owner, camada ou momento.

Só `BLOCKER_DO_OBJETIVO` pode ampliar a implementação da missão atual.

Os outros três entram no fechamento como dívida, risco ou próximo passo mínimo. **Não são
executados por impulso.**

### 3. O blocker só entra se houver relação causal direta

Antes de abrir uma frente lateral, responder:

```
SEM CORRIGIR ISTO, O OBJECTIVE FALHA OU FICA INSEGURO?
```

- `SIM` → corrigir o mínimo necessário e voltar imediatamente ao objetivo;
- `NÃO` → registar e seguir;
- `NÃO SEI` → medir o suficiente para decidir, sem transformar a medição numa nova missão.

**“É importante” não é sinónimo de “bloqueia esta missão”.**

### 4. HARD STOP não serve para fragmentar artificialmente o trabalho

O `HARD STOP` existe para impedir expansão depois do objetivo ou para parar diante de uma
decisão que exige autorização humana. Não deve transformar cada subpasso técnico numa missão
nova.

Uma missão pode conter todos os passos necessários para atingir o mesmo objetivo:

```
problema → contrato → baseline → implementação → testes → red team → regressão → integração
→ validação → evidência → veredito → HARD STOP
```

Se todos esses passos respondem à mesma pergunta principal, **continuam sendo a mesma
missão**.

### 5. Fundação precisa de critério de encerramento

Nenhuma camada fica “em fundação” indefinidamente.

Antes de continuar fortalecendo uma base já funcional, perguntar:

```
O QUE FALTA PARA O USO REAL QUE TEMOS AGORA?
```

Se a resposta for apenas robustez adicional, limpeza de legado, generalização para casos não
usados ou perfeição futura, a fundação fecha e o sistema volta a produzir valor.

Caminho antigo que não é usado pode ficar **marcado, medido e bloqueado**, e ser migrado
quando voltar a ser necessário. Não é obrigatório reformar toda a casa antes de usar um
cômodo que já está seguro.

### 6. Não criar 20 missões para entregar um único resultado de negócio

Quando várias tarefas pequenas pertencem ao **mesmo objetivo**, agrupá-las na mesma missão.
Separar somente quando existir uma destas razões reais:

- owner diferente e independência arquitetural verdadeira;
- risco que exige autorização humana separada;
- mudança estrutural que precisa de cerimónia própria (`LIVE`, Bíblia, contrato, migration);
- prova independente cujo resultado decide se o restante deve sequer existir.

Ausente uma dessas razões, criar outra missão é overhead, não rigor.

### 7. “Bom o bastante para cumprir o contrato” é estado válido

`PASS` não significa “o sistema inteiro está perfeito”. Significa:

- o objetivo declarado funciona;
- as leis aplicáveis foram preservadas;
- os blockers conhecidos do objetivo foram eliminados;
- a prova exigida passou;
- o risco restante está escrito;
- o que ficou fora está nomeado.

```
PASS_DA_MISSAO != PERFEICAO_DO_SISTEMA
```

### 8. Formato obrigatório de fechamento

Toda missão relevante termina declarando:

```
OBJECTIVE_REACHED = YES | NO
SCOPE_EXPANDED = NO | YES_JUSTIFIED
BLOCKERS_FOUND = N
BLOCKERS_RESOLVED = N
DEFERRED_FINDINGS = N
CLIENT_VALUE_DELIVERED = <o que passou a funcionar>
NEXT_MINIMUM_STEP = <um só, ou NENHUM>
```

E responde, em linguagem simples:

1. O que mudou?
2. Qual a prova?
3. O que não mudou?
4. O que ficou desconhecido?
5. Que risco restou?
6. O que foi deliberadamente adiado?
7. `KNOW_HOW_DELTA`?
8. Bíblia/contrato precisa mudar?
9. Qual é o próximo passo mínimo — **sem iniciá-lo**?

### 9. Regra de prioridade quando houver conflito

Se houver tensão entre “deixar mais perfeito” e “entregar o objetivo provado”, vale:

```
SEGURANÇA / LEI / CONTRATO
        ↓
OBJETIVO DA MISSÃO
        ↓
VALOR PARA O CLIENTE / PRAZO
        ↓
ROBUSTEZ NECESSÁRIA
        ↓
MELHORIA / LIMPEZA / GENERALIZAÇÃO
```

A última linha nunca puxa as anteriores para trás.

> **O SINTONIA NÃO OTIMIZA PARA TER MAIS MISSÕES. OTIMIZA PARA FUNCIONAR COM PROVA.**
>
> **ACHADO NÃO É CONVOCAÇÃO. MELHORIA NÃO É BLOCKER. FUNDAÇÃO NÃO É DESTINO.**

---

## LEI DE DESIGN — O ADAMA DESIGN SYSTEM É A FONTE VISUAL OFICIAL

```
DESIGN_SOURCE_OF_TRUTH = ADAMA_DESIGN_SYSTEM
```

**Referência oficial — ADAMA DESIGN SYSTEM no Claude Design:**
<https://claude.ai/design/p/eb7480c7-6d86-43af-8315-a711143f8169?via=share>

Para qualquer trabalho de design, UI ou implementação visual do SINTONIA EAME, **consultar
primeiro** o ADAMA Design System nesse endereço. Componentes, padrões e ícones oficiais
devem ser reutilizados antes da criação de alternativas próprias.

### Quando esta lei se aplica

Sempre que a missão tocar em qualquer um destes: **design · UI · UX · casco · portal ·
componentes visuais · cards · navegação · tipografia · cores · espaçamentos · botões ·
ícones · ícones de culturas · ícones de doenças · padrões de interação · layout ·
responsividade · identidade visual.**

### NÃO INVENTAR ANTES DE CONSULTAR

Antes de criar qualquer componente visual novo:

1. **consultar** o ADAMA Design System no Claude Design;
2. **verificar** se já existe componente, padrão, ícone, estilo, comportamento, token visual
   ou solução equivalente;
3. **reutilizar ou adaptar** o padrão oficial quando ele existir.

Criar algo novo **somente** quando o Design System não possuir solução aplicável. Nesse caso,
declarar explicitamente na entrega:

```
ADAMA_DESIGN_SYSTEM_MATCH = NOT_FOUND
NEW_PATTERN_REQUIRED = YES
```

e escrever o motivo.

### Ícones

Regra especialmente importante. Havendo ícone oficial da ADAMA para **cultura, doença, praga,
categoria, produto ou funcionalidade**, usa-se o ícone oficial.

Não substituir por **emoji, ícone genérico, ícone inventado ou biblioteca externa** quando o
equivalente oficial existir.

### O link não é inspiração

O Design System não é referência visual opcional: é a fonte de verdade visual do projeto.
Decisão visual que se afaste dele precisa estar declarada e justificada na entrega — não
acontece em silêncio.

### O que está versionado aqui é extrato parcial, não a fonte

`italia-portale/client/_ds/adama-brandwell/` e `italia-portale/BASELINE/_ds/adama-brandwell/`
carregam apenas um extrato: tokens (`colors` · `typography` · `spacing` · `patterns` · `base`),
as fontes (LL Brown, Aleo) e `styles.css`. O próprio `_ds_manifest.json` descreve mais do que
está no repositório — componentes (`Button`, `Badge`, `Tag`, `Card`, `ProductIcon`),
guidelines, regras de marca, ícones de marca e de setor, logos, formas 'A' e templates **não
estão** versionados aqui. Esses vivem no Claude Design.

**Extrato local ≠ Design System.** O extrato serve para não divergir dos tokens em código; a
consulta continua sendo no Claude Design.

### Limite desta lei

O ADAMA Design System decide a **forma**. O
[`docs/design/CONTRATO-DE-DESIGN-SINTONIA.md`](docs/design/CONTRATO-DE-DESIGN-SINTONIA.md)
decide o que a forma **não pode esconder** (`NÃO SEI` visível, idade do dado ao lado do
número, fato ≠ interpretação ≠ ação). Em conflito entre os dois, o contrato de design vence:
nenhuma decisão visual revoga uma linha dele.