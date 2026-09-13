# HANDOFF · DELTA DE KNOW-HOW · A ARBITRAGEM DA INTELLIGENCE

**Para aplicar em `claude/sintonia-eame-know-how-v1` →
`SINTONIA-EAME-KNOW-HOW.md`, no PRÓXIMO NÚMERO LIVRE.**

> Quem integrar **lê o último `§` do ficheiro e usa o seguinte.** Este ficheiro
> não carrega número, pela razão que a linha do know-how já pagou duas vezes.
>
> ⚠️ **O know-how andou durante estas missões**: `0de9dd95 → 7b5e50cf`. Ler o
> estado atual antes de aplicar; parte disto pode já lá estar.

```
ORIGEM      C-INT-CENSUS-01 (censo) + C-INT-ARB-01 (arbitragem)
MEDIDO_EM   2026-09-13
BASE        funcional f888776d · trabalho em claude/funny-hypatia-y7ho5s
```

---

# §<PRÓXIMO LIVRE> · CONTAR FICHEIROS MEDE MASSA, E MASSA NÃO É PROPRIEDADE

## O QUÊ

A Intelligence do SINTONIA tem **12 peças** no mapa funcional, uma constituição
candidata, um contrato de motor subordinado, e um gerador canónico que vive
noutra linhagem. Nada disto era sabido em conjunto antes destas duas missões.

## X.1 · POR QUÊ — O CENSO NÃO CONSEGUIU DECIDIR, E ESTAVA CERTO

O censo deixou `OPPORTUNITY_OWNER = NÃO SEI` porque mediu massa:

```
italia-portale  50 ficheiros
build           29 ficheiros
motor            3 ficheiros
```

O maior número está na Entrega. E a Entrega **não** é a dona. A arbitragem
separou quatro funções que a contagem tinha colado:

```
CREATE     motor/v21_oportunidades.py — oito portoes, decide OPPORTUNITY_STATE
STORE      build/OPPORTUNITIES.json — guarda, nao decide
PROJECT    italy-handoff-v21.js — transporta
PRESENT    italy-app-model.js — 5124 linhas, 1 calculo, le CLIENT_SAFE
```

```
QUEM DECIDE QUE UMA COISA EXISTE E O DONO DELA.
QUEM A MOSTRA MAIS VEZES E SO QUEM A MOSTRA MAIS VEZES.
```

E a lição de método: **um censo que diz NÃO SEI e uma arbitragem que decide são
duas missões, e é bom que sejam.** Se o censo tivesse escolhido o maior número,
teria escrito uma resposta errada com ar de facto.

## X.2 · «PROVEN» NO SYSTEM MAP NÃO QUER DIZER FLUXO

Classificadas as 135 linhas de evidência que sustentam as 82 arestas das peças
de Intelligence:

```
co-acesso a ficheiro   56    ← duas pecas nomeiam o mesmo JSON
linha de workflow      45    ← invocacao real
import                 34    ← nao e fluxo
chamada de funcao       0
```

E as 82 estão marcadas `technical/PROVEN`.

```
UMA PECA QUE NINGUEM CHAMA APARECE LIGADA
PORQUE PARTILHA UM NOME DE FICHEIRO COM QUEM E CHAMADO.
```

O caso: `C-V2-LEGADO` tem 3 arestas `PROVEN` e **zero** referências reais.

Vocabulário proposto, e **não implementado** — `"kind": "technical"` está fixo em
7 sítios, em dois geradores divergentes:

```
DECLARED · STATIC_REFERENCE · IMPORT_OBSERVED · CALL_OBSERVED
WORKFLOW_OBSERVED · RUNTIME_OBSERVED
```

## X.3 · UM MOTOR QUE SE RECUSA A CORRER ESTÁ A FUNCIONAR

```
bash motor/v21_cadeia.sh   →   exit 2
  Esta branch e CONSUMIDORA da inteligencia, nao geradora.
```

É a **única prova runtime positiva** do motor nesta árvore: a prova de que ele se
recusa. Corrido, produziria `V21-5d312cb90a0de01d`, uma safra que o portão
rejeita.

```
O QUE ELE NAO ESTA A FAZER E PRODUZIR. ISSO NAO E O MESMO QUE ESTAR PARTIDO.
```

## X.4 · ENTRE DOIS DOCUMENTOS QUE DISCORDAM, GANHA O QUE UM PORTÃO LÊ

```
motor/v21_cadeia.sh:35,47              gerador = 55c2674
CANONICAL-PACKAGE-CONTRACT.json        gerador = 51010733
                                       e a safra de 55c2674 esta listada VELHA
```

O contrato é lido e executado por `build-gate.mjs` (exit 0) e
`stale-generator-gate.mjs` (9/9 com controlos negativos). O cabeçalho da cadeia é
prosa.

```
GENERATOR_OWNER = CONTRACT_WINS
```

Quem seguisse a instrução da cadeia geraria um pacote que o portão recusa.

## X.5 · UMA COLISÃO DE NOME NÃO É UMA COLISÃO DE DONO

O censo apontou `FACT/CLAIM → v21_dominio_da_alegacao.py`, o que colidiria com
`INT-LAW-000` (o `CLAIM/FACT` é da Collection). Lido o comportamento:

```
grep CLAIM_ID motor/*.py          VAZIO
grep sha256|uuid|hashlib          VAZIO
opera sobre ids upstream          IT-CAN-…
```

O módulo julga se uma alegação já admitida é **sobre o mundo** ou **sobre o nosso
encanamento**. Não cria facto.

```
FACT_CLAIM_COLLISION = NAME_COLLISION
CLAIM_DOMAIN_JUDGMENT   ← o nome canonico do que ele faz
```

```
LER O NOME DO FICHEIRO E UMA HIPOTESE. LER O QUE ELE ESCREVE E A MEDICAO.
```

## X.6 · «Ran 0 tests ... OK» NÃO É PASS

Quatro módulos de teste da V2.1 contêm **50 funções** em estilo pytest. O CI da
casa corre `python3 -m unittest` (5 workflows), pytest não está declarado nem
instalado, e o loader canónico vê 3 892 testes em 152 ficheiros.

```
148 de 152 ficheiros seguem a convencao. A Intelligence e a unica area que a quebra.
```

E a decisão do runner **já existia** (`DIARIO-DE-DECISOES`, D-009: contar a suíte
com `unittest.defaultTestLoader.discover`). Ia tomá-la outra vez.

```
UMA DECISAO QUE JA EXISTE E TOMADA OUTRA VEZ
PASSA A EXISTIR DUAS VEZES, E DIVERGE NA TERCEIRA.
```

## X.7 · UM TETO DE DÍVIDA QUE SOBE PORQUE A DÍVIDA PASSOU A SER CONTADA

Registar a Bíblia da Intelligence e o Motor V2 no Control Plane fez
`STALE_AUTHORITY` subir de 4 para 6, e o portão reprovou.

As duas autoridades **sempre** viveram fora desta árvore. O que mudou foi passarem
a estar no registo.

```
A DIVIDA NAO PIOROU. ELA PASSOU A SER CONTADA.
```

O teto foi levantado **com a razão escrita dentro do ficheiro do chão**, porque a
alternativa — não registar uma autoridade conhecida para manter um número verde —
é exatamente a doença que o portão existe para apanhar.

```
UM TETO QUE SOBE EM SILENCIO E UM PORTAO DESLIGADO.
```

## X.8 · O QUE FICOU DECIDIDO

```
BIBLE_STATUS          CANDIDATE (inalterado)
MOTOR_V2_STATUS       SUBORDINATE_IMPLEMENTATION_CONTRACT
CONFLITOS ESTRUTURAIS 0
CANONICAL_GENERATOR   claude/acervo-to-package-intelligence-v1 @ 51010733
FACT/CLAIM            COLLECTION
CLAIM_DOMAIN_JUDGMENT INTELLIGENCE
OPPORTUNITY           C-V21-OPORTUNIDADE
INTELLIGENCE_RUN      contrato pronto, 0 implementado
COLLECTION_GAP        contrato pronto, 0 implementado
BIBLE_PROMOTION_READY NO — bloqueia na condicao 5 da propria Biblia
```

## X.9 · CONSEQUÊNCIA

O bloqueador da Intelligence não é técnico. É de **endereço**:

```
Biblia V0.2      research/intelligence-bible-engineering-v1
Motor V2         claude/intelligence-backlog-canonical
Censo + Controle claude/funny-hypatia-y7ho5s
Know-how         claude/sintonia-eame-know-how-v1
Runtime + Coleta claude/raw-observation-identity-3jbwco

NENHUM COMMIT CONTEM TODAS.
```

```
UMA CONSTITUICAO QUE VIVE NUMA BRANCH QUE NINGUEM CLONA
GOVERNA EXATAMENTE NINGUEM.
```

E mover a Bíblia de uma branch lateral para outra branch lateral **não** resolve:
só muda de qual ramo ela é invisível. Foi por isso que esta missão a registou em
vez de a mudar de sítio.
