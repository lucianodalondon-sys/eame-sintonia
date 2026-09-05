# RADAR FUTURO ITÁLIA — CONGELADO

Entrega aceite e fechada em `707b684`. Este ficheiro regista os factos de
encerramento. **Nada aqui reabre nada.**

---

## Uma correcção ao registo, antes dos factos

A lista de encerramento recebida dizia «ITFC-006 permanece DERRUBADO».
**Não é.** `ITFC-006` é **`PARCIAL`**, e o único `DERRUBADO` dos 45 é
`ITFC-027`.

| candidato | estado | como lá chegou |
|---|---|---|
| `ITFC-006` | **PARCIAL** | passou no primeiro refutador como `SINAL_COMPLETO`; o segundo adversário independente rebaixou-o |
| `ITFC-027` | **DERRUBADO** | único derrube dos 45, por estado do tempo estagnado |

A consequência prática é a mesma — nenhum dos dois entra no `TOP_3` e nenhum é
para recuperar — mas os dois estados dizem coisas diferentes. `PARCIAL` é «o
núcleo aguenta e falta-lhe coisa»; `DERRUBADO` é «isto não se apresenta». Guardar
`ITFC-006` como derrubado apagaria o facto de o núcleo dele ter aguentado duas
leituras e ter caído por uma atribuição errada de secção, e não por ser falso.

Registo os factos abaixo com essa correcção incorporada.

## Factos de encerramento

1. **O segundo julgamento independente prevalece quando é mais severo.** Regra
   declarada antes de correr, não depois de ver o resultado.
2. **6 candidatos chegaram a `SINAL_COMPLETO` no primeiro julgamento; 4
   sobreviveram ao adversário independente.**
3. **`ITFC-006` fica `PARCIAL` e não é para recuperar. `ITFC-027` fica
   `DERRUBADO`.**
4. **`TOP_3_ADAMA` = `ITFC-009`, `ITFC-016`, `ITFC-018`.**
5. **Nenhum dos 45 é `AGIR_AGORA`** — 24 `PREPARAR`, 21 `MONITORAR`.
6. **38 dos 39 sinais aplicáveis ainda não têm gatilho futuro observado ou
   respondido.** As fontes são de Outubro de 2025 a Maio de 2026; a leitura é de
   Setembro de 2026, e a campanha intermédia correu sem ninguém olhar.
7. **Portanto o Radar Futuro NÃO pode ser apresentado como radar de acções para
   hoje.** Um cartão que diga «aja agora» sobre este material mente sobre o
   calendário.
8. **O bug de contagem `DERRUBADO`/`ESTADO` foi corrigido antes da entrega** e não
   sobrevive em nenhum artefacto final. Verificado em `IT-FUTURO-SINAIS-V1.json`:
   `DERRUBADO = 1`, `ESTADO = COMPLETO`.
9. **O achado `ESCORIOSI` / `BLACK_ROT` é um falso negativo de ferramenta, não
   ausência de portefólio.** Ver secção seguinte.

## O falso negativo de vocabulário — registado, NÃO corrigido

Hoje, a pergunta interna «temos alguma coisa para black rot na vinha?» devolve
**zero**. Existem **10 registos ADAMA com folpet** cujo texto de rótulo declara
`VITE` contra `Marciume nero (Guignardia bidwellii)` e/ou `Escoriosi (Phomopsis
viticola)`.

> **Isto é um falso negativo de ferramenta e de vocabulário. Não é ausência de
> autorização.**

São **dois defeitos com dois donos diferentes**, e é por isso que não toco em
nenhum nesta ronda:

| defeito | onde | dono | estado |
|---|---|---|---|
| não existe token `BLACK_ROT` nem `ESCORIOSI`; `marciume` colapsa marciume nero, bianco, secundários e radicais num só balde | `scripts/it_rotulo_vocab.py` (camada de rótulos) | esta branch | **por medir** — mexer aqui altera o conjunto publicado de 2.928 pares e exige gabarito e portão |
| `ISSUE_BLACK_ROT` não existe entre os 24 `ISSUE_*` do motor | `v21_normalizar.py` @ `b3935bd` (camada do motor) | `claude/opportunity-commercial-priority-v1` | **proposto e medido** em `IT-VOCAB-HANDOFF-V1.json`, com teste verde, à espera do dono |
| `010587 FOLPAN SC` e `011501 PARIFOL` têm os dois alvos no texto do rótulo e não publicam um único par `VITE` | parser | esta branch | sub-declaração conhecida, na fila de cauda longa |

O que falta antes de corrigir, e que esta ronda não faz: **identificar qual das
duas camadas é o dono canónico da pergunta** «temos algo para X?» — porque
responder nas duas cria o segundo dono que passámos a semana a evitar — e **medir
o impacto** da separação de `marciume` sobre os pares já publicados.

## Congelamento

```
ESTADO                     CONGELADO
CHECKPOINT                 707b684
READY_FOR_CANONICAL_REVIEW SIM
READY_FOR_PORTAL           NÃO
```

Não se altera o portal, não se publica nada como `AGIR_AGORA`, não se converte
`PREPARAR` nem `MONITORAR` em oportunidade actual, não se reabrem os 45, não se
relaxa o segundo julgamento, não se recupera `ITFC-006`, não se colhe mais nada e
não se cria dono novo para pergunta que já tem dono.

## A missão seguinte, desenhada e NÃO executada

Desenhar os **gatilhos observáveis** dos sinais `PREPARAR` e `MONITORAR`,
começando pelo `TOP_3`: qual mudança concreta, observável e datável transforma
«prepare-se» em «aja agora».

O material para isso já existe e não precisa de recolha nova: cada um dos 45
candidatos entra em `IT-FUTURO-JULGADOS-V1.json` com um `TRIGGER` e um
`INVALIDATION_TRIGGER` escritos pela régua, e cada ficha traz `T_BASE_DA_JANELA`
com a frase do documento que a sustenta. O que falta é transformá-los em algo que
uma máquina possa vigiar — fonte, cadência, e o valor que muda de estado.

**Não começa até nova decisão.**
