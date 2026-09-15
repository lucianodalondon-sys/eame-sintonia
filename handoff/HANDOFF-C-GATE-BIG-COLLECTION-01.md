# HANDOFF — C-GATE-BIG-COLLECTION-01 (pausada, nada perdido)

```
BRANCH        claude/big-collection-gate-01
HEAD          ver `git log -1` nesta branch — publicada no origin
WORKTREE      C:\eame-sintonia\.claude\worktrees\youtube-italia-caption-audio-8b460b
              (⚠️ o nome da pasta é da missão ANTERIOR; a branch é esta)
ESTADO        árvore LIMPA · SYSTEM_MAP_CHECK = PASS
PAUSADA EM    2026-09-14, a pedido, para continuar noutra aba
```

> **Não há trabalho por commitar.** Tudo o que esta missão mediu e escreveu está
> em commits publicados. Quem continuar não precisa de reconstruir nada.

---

## 1 · ONDE A MISSÃO PAROU

Ela **não** parou a meio de uma construção. Parou **depois** de a estrada estar
provada, com um veredito escrito:

```
BIG_COLLECTION_GATE = PARTIAL
BIG_COLLECTION_READY = NO
```

Dez dos onze critérios estão `PASS`/`PROVEN`. A entrega inteira está em
[`docs/sintonia-scrap/C-GATE-BIG-COLLECTION-01.md`](../docs/sintonia-scrap/C-GATE-BIG-COLLECTION-01.md)
— **ler esse ficheiro primeiro**, este handoff é só o mapa para ele.

---

## 2 · O QUE JÁ ESTÁ PROVADO (não repetir)

Contra `postgres:16` descartável, no CI, job **`portao-big-collection`**:

```
MIGRATION_032_APPLIED            True
READY_CONTRACT_FIELDS            19      (e 17 têm coluna homónima; 2 têm
                                          equivalência DECLARADA e verificada)
ADMISSION_DECISION_CANARIO       SIM     (IT-T3-010, boletim italiano real)
CONTROLO_NEGATIVO                NAO_SEI (texto de mercado continua fora de T3)
READY_FIELD_COUNT                19
WAITING_ROWS                     1       (contadas NA TABELA, não no recibo)
READY_EXISTS_AFTER_PROCESS_EXIT  True
LEITURA_CAMPOS                   19      (via sala_de_espera.ler, outro processo)

PORTAO_BIG_COLLECTION = PROVADO · 18 passaram · 0 falharam
```

E no job **`ponte-de-midia`** (também SUCCESS, na candidata integrada):

```
MEDIA → RUN → RAW → STORAGE → DERIVED(TRANSCRIPTION) → STRUCTURED → ADMISSION
ADMISSION_DECISION = NAO_SEI   →  a Sala fica VAZIA, e isso está certo
```

⚠️ **Não chamar isto de `FULL_MEDIA_TO_WAITING_ROOM`.** A porta disse `NAO_SEI`.
A verdade anterior foi preservada de propósito.

---

## 3 · O ÚNICO PASSO QUE FALTA — e é um só

```
DECIDIR O `2b5` DO JOB `postgres-descartavel`.
```

`provas/a_sala_sobrevive_ao_processo.py` falha com:

```
ValueError: item NAO SEI nao passou a porta (NAO_SEI)
```

**Não é 12 vs 19 campos.** O ataque 26 daquela prova precisa de dois itens com o
**mesmo `ITEM_ID` ambíguo** para verificar que `espera.retirar` os recusa. A
prova comenta, por escrito, *«`admissao.decidir()` devolve "?" quando o item não
traz id nem url»*. Hoje já não devolve: `"?"` virou `NAO SEI`, e **a porta
recusa item sem identidade**.

```
A CASA FICOU MAIS ESTRITA, E O ATAQUE DEIXOU DE SER CONSTRUÍVEL PELA PORTA.
```

**A pergunta para quem continuar:**

```
· se a guarda de ambiguidade em `retirar` AINDA é alcançável
      → a prova reconstrói o par ambíguo por outro caminho (não pela porta)
· se já NÃO é
      → a prova declara o ataque defendido a montante, e diz ONDE
```

Isto é **mudança arquitectural**, e foi por isso que esta missão parou aqui em
vez de escolher sozinha. Medido: **já falhava na própria FACTS**, no HEAD dela,
antes desta fusão. Não é dívida criada aqui.

⚠️ **Não *skippar* e não pôr `continue-on-error`.** O job está vermelho a dizer
uma verdade.

---

## 4 · O QUE ESTA MISSÃO INTEGROU

Duas linhas funcionais, complementares e divergentes, fundidas numa candidata:

```
MEDIA  claude/youtube-italia-caption-audio-8b460b @ fa980fe7
       ponte de mídia · executor_para · dispatch por unidade
FACTS  claude/collection-preserve-facts-2139eb @ 4708f772
       migration 032 · CAMPOS_READY de 19 · o fato na Sala
merge-base 56617781 · 23 commits de um lado, 4 do outro
```

O único conflito de código era **a mesma lei escrita duas vezes** (CRLF no
gerador do mapa). Ficou a versão que trata binário, por medição. Os JSON gerados
foram **regenerados**, nunca editados à mão.

---

## 5 · O QUE MAIS SE CONSERTOU PELO CAMINHO

```
provas/o_egresso_antes_da_aquisicao.py   ModuleNotFoundError: yaml
```

Abortava **há dias, em todas as branches**. Era só PyYAML ausente no runner —
declarado agora no passo que o usa. Medido depois: `34/34 PASS`,
`RED_TEAM_SURVIVORS = 0` → `CANONICAL_COLLECTION_GATE = RUNNABLE`.

E o know-how voltou ao processo da casa: `docs/know-how/` foi **retirada** e o
texto virou `handoff/KNOW-HOW-DELTA-A-PONTE-DE-MIDIA.md`, com a cabeça canónica
medida (`know-how-v1 @ 5705ac7b`, última secção `§119`, número **por atribuir**).

---

## 6 · DÍVIDAS ABERTAS, DECLARADAS E NÃO ESCONDIDAS

| dívida | onde está escrita | de quem é |
|---|---|---|
| `2b5` — o ataque ambíguo deixou de ser construível | secção J da entrega | FACTS (anterior) |
| retry: duas observações do mesmo conteúdo não partilham derivado | secção I | herdada (a mesma trava do PDF) |
| `test_a_sala_de_espera_tem_um_dono` constrói READY de 12 à mão | secção K | FACTS (anterior) |
| `fcntl` ausente no Windows mata 3 suítes locais | secção K | ambiente |
| quatro documentos publicam `TEST_COUNT_CURRENT = 3.952` e **nenhuma** das três árvores o produz | secção K | anterior aos dois pais |

```
REGRESSÃO MEDIDA NOS DOIS PAIS, com worktrees temporários:
TEST_COUNT  MEDIA 3831 · FACTS 3802 · CANDIDATA 3878
DISAPPEARED_TESTS = 0 · NEW_FAILURES = 0
```

---

## 7 · COMO RETOMAR

```bash
git fetch --all --prune
git log --oneline -1 origin/claude/big-collection-gate-01   # GIT VENCE
```

Ler, por esta ordem:

1. `docs/sintonia-scrap/C-GATE-BIG-COLLECTION-01.md` — a entrega, com as
   secções A–S
2. a secção **J** dela — é onde o trabalho recomeça
3. `provas/a_sala_sobrevive_ao_processo.py`, à volta da linha 583

Para reproduzir o verde que já existe:

```bash
gh workflow run banco-descartavel.yml --ref claude/big-collection-gate-01
# jobs `portao-big-collection` e `ponte-de-midia` devem ficar SUCCESS
# `postgres-descartavel` deve ficar FAILURE no 2b5 — é o que falta
```

---

## 8 · O QUE NÃO FAZER

```
NÃO iniciar Big Collection — o portão está PARTIAL, e isso é a resposta
NÃO iniciar Intelligence
NÃO tocar LIVE
NÃO enfraquecer a Admissão para a mídia entrar (ela diz NAO_SEI, e está certa)
NÃO recriar `docs/know-how/` — o delta vive em `handoff/`
NÃO desenvolver em paralelo nas branches MEDIA e FACTS: a candidata é esta
```

E o maior risco, que não é técnico:

```
A ESTRADA ESTÁ PROVADA DE PONTA A PONTA. O QUE ENTRA NELA, HOJE, É PDF.
A ponte de mídia funciona e não tem quem lhe entregue bytes numa corrida
real — nenhuma rota de aquisição de mídia está autorizada.
```
