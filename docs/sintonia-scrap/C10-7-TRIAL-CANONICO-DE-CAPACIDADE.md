# C10.7 — O ENSAIO CANÔNICO DE CAPACIDADE

`C10_7_CANONICAL_TRIAL = PASS`

> A ferramenta recusava tudo o que ainda não tinha provado — o que está certo
> para produção — e não tinha como provar coisa nenhuma por dentro.
>
> ```
> UMA FERRAMENTA QUE RECUSA TUDO O QUE AINDA NÃO PROVOU
> FAZ NASCER TODA CAPACIDADE NOVA FORA DELA.
> ```
>
> O conserto é um terceiro eixo no mesmo executor. A única diferença entre os
> dois modos, em todo o caminho, é o portão epistemológico da capacidade.

---

## 1 · O CICLO ESTAVA FECHADO, E NÃO ERA HIPÓTESE

```
NOT_EXECUTED
  → o CHECK recusa
  → para deixar de o ser, tem de correr uma vez
  → corre por um script lateral
  → alguém «integra»
  → nasce um bypass.
```

Duas capacidades estão presas nesse ciclo **hoje**, com adaptador ligado e
política permitida:

| capacidade | estado | rota | política | `CHECK` normal |
|---|---|---|---|---|
| `bluesky.author.incremental` | NOT_EXECUTED | ligada | ALLOWED | `CAPABILITY_STATE_PROMISES_NOTHING` |
| `mastodon.account.incremental` | NOT_EXECUTED | ligada | ALLOWED | `CAPABILITY_STATE_PROMISES_NOTHING` |

```
FIRST_BLOCK = scrap_executor.CHECK, em `cap.promete_resultado()`
```

E o script lateral não é hipótese tão-pouco: o `piloto` do `social_scrap.py`,
que a C10.6D mediu a chamar o roteador sem passar pelo boundary, é exatamente o
que este ciclo já produziu uma vez.

---

## 2 · PROCUROU-SE ANTES DE CRIAR

O censo varreu `coleta/`, `leis/`, `medidas/`, `ferramentas/` e `guarda/` por
`trial · probe · pilot · piloto · experimental · dry_run · seco · test_mode ·
proof · allow_unproven · force · override · permitir_pago · oneshot`, em código
sem docstring nem comentário.

| achado | o que é de verdade | serve? |
|---|---|---|
| `ONE_SHOT` (`social_scrap.py`) | modo do piloto do YouTube que salta o **checkpoint** | não — outro eixo |
| `seco` (`executor_texto_de_pdf`, orquestrador) | ensaio que **não executa** | não — o ensaio tem de executar |
| `permitir_pago` (`social_rotas`) | o portão do **gasto** | não — eixo ortogonal, e continua intocado |
| `piloto` (`social_scrap.py`) | fase de CLI que chama o roteador direto | não — é o **sintoma** |

```
FOUND = NO · nenhum mecanismo existente mede o eixo da CAPACIDADE.
```

Nome parecido não é semântica igual. `seco` e `TRIAL` são opostos: um não
executa de propósito, o outro executa exatamente para medir.

---

## 3 · OS TRÊS EIXOS

O executor já tratava dois como donos separados. Faltava o terceiro.

```
CAPABILITY_STATE    o que MEDIMOS que sabemos fazer     scrap_capacidades
ROUTE_POLICY        que porta é PERMITIDA               leis/social_matriz
EXECUTION_MODE      que pergunta estou a fazer          scrap_executor   ← novo
```

```
NORMAL   «vou colher, e espero resultado»
TRIAL    «vou MEDIR se consigo, e NÃO espero resultado»
```

Combinações, e por que cada uma é o que é:

| CAPABILITY_STATE | ROUTE_POLICY | MODO | resultado |
|---|---|---|---|
| NOT_EXECUTED | ALLOWED | NORMAL | **recusa** — não promete resultado |
| NOT_EXECUTED | ALLOWED | TRIAL | **passa** — é o que o ensaio existe para medir |
| NOT_EXECUTED | ROUTE_NOT_ALLOWED | TRIAL | **recusa** — a política ganha sempre |
| BLOCKED | qualquer | TRIAL | **recusa** — ver §5 |
| PROVEN | ALLOWED | TRIAL | passa, e continua a dizer `CAN_COLLECT_NOW` |

---

## 4 · A TABELA DE ESTADOS

```
ESTADO         NORMAL   TRIAL   PORQUÊ
PROVEN           SIM     SIM    promete resultado; o ensaio não a rebaixa
PARTIAL          SIM     SIM    promete com teto medido; idem
NOT_EXECUTED     não     SIM    «nunca tentado» é exatamente o que se mede
UNKNOWN          não     SIM    «não medido» é a mesma pergunta por outro nome
BLOCKED          não     não    o estado diz duas coisas — §5
```

`UNKNOWN` entra porque a declaração do próprio ficheiro o define como «não
medido», e não como «não sabemos o contrato». Medir o que ninguém mediu é
precisamente o ato para o qual o ensaio existe.

---

## 5 · O CASO FACEBOOK — UM ACHADO DE MODELO, NÃO UMA CAUTELA

```
CAPABILITY_ROUTE_STATE_CONFLATION = YES
```

`facebook.content = BLOCKED`. A prova citada é
`docs/sintonia-scrap/AP-DISCOVERY-VS-CAPTURA-V1.md`, e ela diz, pelas próprias
palavras:

> `gallery-dl` deslogado dá identidade e endereços. **Todo o conteúdo está
> bloqueado deste IP**.

E arruma essa linha numa tabela intitulada **«o que só o runner local pode
fechar»**, com a coluna «porquê aqui não».

Foi medida **uma rota** (`gallery-dl` anónimo) a partir de **um host**. A
matriz, ao lado, declara `FACEBOOK/FETCH_POST` como `ALLOWED`, por duas rotas
que **não** são a medida: `graph:/{page-id}/posts` e `apify:facebook`.

```
`BLOCKED` NA CAPACIDADE ESTÁ A DESCREVER UMA ROTA NUM AMBIENTE.
```

O mesmo aparece em `youtube.media`, cuja linha já carrega
`EXECUTION_TARGET = LOCAL` e `WHY_LOCAL = DATACENTER_BLOCKED` — o eixo do
ambiente está lá, e o estado repete-o na mesma.

**Não foi corrigido aqui, e a decisão é essa.** Separar os eixos muda a
declaração de cinco capacidades e é ato de quem mede, não de quem passa. O que
se fez foi impedir que o ensaio leia um estado misturado como se estivesse
limpo: `BLOCKED` não entra em ensaio, e o motivo está escrito no código, ao lado
da regra.

---

## 6 · O QUE MUDOU NO CÓDIGO

Um ficheiro: `coleta/scrap_executor.py`.

```python
NORMAL = 'NORMAL'
TRIAL  = 'TRIAL'
MODOS  = (NORMAL, TRIAL)
SEM_ENSAIO = ('BLOCKED',)

CHECK(plataforma, capacidade, *, ambiente=None, modo=NORMAL)
COLLECT(*, platform, capability, run_id, scope='PONTUAL', banco=None, modo=NORMAL, **kwargs)
```

O `CHECK` passa a responder às duas perguntas separadamente, **nos dois modos**:

```
PRODUCTION_READY   dá para colher a sério, com direito a esperar objeto
TRIAL_ELIGIBLE     dá para medir uma vez, sem direito a esperar nada
```

```
UM `CAN = True` QUE NÃO DIGA QUAL DOS DOIS
MENTE PARA METADE DE QUEM O LÊ.
```

E dois estados novos, que não existiam e não se confundem com nada:

```
TRIAL_ELIGIBLE                       o ensaio pode medir esta
TRIAL_REFUSED_BY_CAPABILITY_STATE    o ensaio também não a mede, e diz porquê
```

### O defeito que apareceu ao mexer na introspecção

`CAPABILITIES()` respondia `HAS_ROUTE` com `bool(r and r['EXECUTA'])` — e um
adaptador cumpre o papel por `executa=` **ou** por `rota=`. Onze das catorze
capacidades ligadas apareciam sem rota, enquanto o `CHECK`, na linha ao lado,
dizia `CAN_COLLECT_NOW` para elas.

```
DUAS RESPOSTAS PARA A MESMA PERGUNTA SÃO DOIS DONOS.
```

Passou a delegar em `reg.tem_caminho`, que já era o dono. Divergências: 11 → 0.

---

## 7 · A PROVA, SEM REDE E SEM BANCO

`provas/ensaio_canonico_de_capacidade.py`. O único objeto substituído é
`scrap_http.buscar` — a chamada externa do fornecedor. Executor, roteador,
registo e adaptador correm a sério.

```
MOCKAR O RUNTIME PROVA O MOCK. MOCKAR A PORTA EXTERNA PROVA O RUNTIME.
```

Mesmo pedido, dois modos:

| | NORMAL | TRIAL |
|---|---|---|
| objetos | 0 | 1 |
| `CHECK.STATE` | `CAPABILITY_STATE_PROMISES_NOTHING` | `TRIAL_ELIGIBLE` |
| `EXECUTION_MODE` no trace | `NORMAL` | `TRIAL` |
| `PRODUCTION_READY` | False | False |

```
EXECUTOR_REACHED       YES
ROUTER_REACHED         YES
ADAPTER_REACHED        YES
FAKE_PROVIDER_REACHED  YES
NETWORK_REAL           0
STATE_PROMOTED         NO
ROUTE_NOT_ALLOWED_PROVIDER_CALLS      0
BLOCKED_CAPABILITY_TRIAL_PROVIDER_CALLS 0
ENSAIO_CANONICO=PASS
```

O RAW foi desviado para uma gaveta temporária — uma prova que escreve no acervo
mede o acervo a seguir.

---

## 8 · O QUE O ENSAIO NÃO FAZ

**Não promove estado.** O ficheiro da declaração é comparado por SHA antes e
depois, e o trace carrega `CAPABILITY_STATE_BEFORE == CAPABILITY_STATE_AFTER`
por construção — a prova viaja dentro do próprio artefato. Um ensaio que
devolveu objeto continua `NOT_EXECUTED`.

```
TRIAL PASSADO != CAPACIDADE PROVADA.
OFFLINE FIXTURE PASSADO != CAPACIDADE PROVADA AO VIVO.
```

Promover exige prova definida, artefato, evidência observada e um commit que se
lê. Isso é ato de gente.

**Não sobrescreve política.** `LINKEDIN/FETCH_POST` continua `ROUTE_NOT_ALLOWED`
e o fornecedor não é chamado, com ou sem ensaio.

**Não autoriza gasto.** O executor não conhece `permitir_pago`, `motivo_pago`
nem `MOTIVOS_PAGOS` — quem decide gasto é o roteador, e uma sentinela recusa
que essas palavras apareçam no executor.

**Não criou um segundo runtime.** Nenhum `trial_executor.py`,
`experimental_router.py`, `probe_runtime.py` ou `scrap_v2.py`. O dono continua
a ser `scrap_executor`, e há uma só `COLLECT`.

---

## 9 · O QUE CONTINUA DESCONHECIDO

- Se `bluesky.author.incremental` e `mastodon.account.incremental` funcionam
  **ao vivo**. O ensaio provou o CAMINHO, com fornecedor falso. Elas continuam
  `NOT_EXECUTED`, que é a verdade.
- Se `facebook.content` está bloqueado como capacidade ou só na rota medida.
  `NEEDS_MEASUREMENT` — e a resposta não sai de lógica, sai de medição por uma
  das rotas que a matriz declara.
- O preço de qualquer rota paga. Esta missão não gastou.

```
CAN DO != DID DO.
```
