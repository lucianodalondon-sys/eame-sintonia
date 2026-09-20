# MISSÃO CURTA — FECHAR OS RESÍDUOS DA BC2

**Missão de fecho, não de arquitetura.** Fechar **só** o necessário para deixar
a Collection estável e seguir em frente. **Sem red team extra. Sem reabrir
arquitetura.** `HARD STOP` ao concluir.

BANCADA: `C:/Users/London1/orca/workspaces/eame-sintonia/cutover-v2`
BRANCH: `claude/contract-provenance-cutover-v1`

---

## 0 · MEDIDO PELO COORDENADOR AGORA — confirma, não confies

```
INITIAL_HEAD = a6a9809fc62814f9a131588e41f57a64fff3135c
REMOTE       = a6a9809f · 0/0 sincronizado · DIRTY = 0
```

Estado herdado da missão anterior (a reconfirmar): `STORAGE OPERACIONAL =
PROTEGIDO` · `TEST_CAN_DELETE_OPERATIONAL_STORAGE = NO` · HTML **42** derivados,
**4** falharam a gravar, **0** `NOT_APPLICABLE` · `ADMISSION +11 SIM` ·
`SALA 17 → 28` · `NEW_FAILURES 0` · `SHA_MISMATCH 0` ·
`RECONCILIATION_STRUCTURAL_ERRORS 0` · `SYSTEM_MAP_CHECK PASS` · `PAID_USD 0`.

### ⚠️ O que eu já medi sobre `data/colheita/italia` — muda o trabalho do ponto 1

```
data/colheita/italia/      NÃO EXISTE no disco neste momento
data/colheita/             existe, com _prova/ e scrap/ lá dentro
git ls-files data/colheita →  0 ficheiros rastreados
.gitignore:89  data/colheita/   →  a pasta é IGNORADA pelo Git
```

E quem a nomeia no código é a **zona de largada dos executores**:

```
pedido/receitas.py      "larga_em": ["data/colheita/italia/"]   (≥4 receitas)
pedido/receitas.py      "retorno": {"ENVELOPE": "data/colheita/italia/RETORNO.json"}
leis/retorno_da_coleta.py   o envelope de retorno por corrida
coleta/italy_executor.py:45 data/colheita/italia/colheita.json
```

**Isto é medição, não veredito.** A classificação (`OPERATIONAL · TEMPORARY ·
GENERATED · RECONSTRUCTIBLE · TEST-ONLY`) é o teu primeiro trabalho, e o facto
de estar no `.gitignore` e de a pasta já ter desaparecido **sem ninguém dar por
falta** é evidência forte — mas **não** é prova por si só: um envelope de
retorno que a Collection ainda não consumiu seria operacional e não
reconstruível.

> **A pergunta certa: pode existir ali conteúdo operacional NÃO-reconstruível?**

Se **sim** → neutraliza os 3 cleanups com a **mesma** proteção já aplicada ao
storage (marcador + falha fechada). Se for comprovadamente descartável →
**documenta e NÃO crias proteção artificial.** Proteger o que não precisa custa
manutenção e ensina a lição errada.

Entrega: `CLEANUPS_FOUND · CLEANUPS_DANGEROUS · CLEANUPS_FIXED`.

---

## 1 · OS 4 HTML QUE FALHARAM A GRAVAR

**Só a partir do RAW já existente. `NETWORK_CALLS = 0`.**

Por cada um: `RAW_ID · SOURCE_ID · FAILURE_STAGE · FAILURE_REASON ·
BYTES_PRESENT · HTML_PARSE_RESULT · WRITE_RESULT`.

A missão anterior chegou à consulta de identidade e **não conseguiu provar a
causa** — ficou `NÃO SEI`, honestamente. Retoma daí, não do princípio.

- causa pequena e reutilizável → **corrige e reprocessa os 4**;
- realmente impossível → mantém `FAIL`/`UNKNOWN` **com prova**.

**Não alteres a Admission.** Entrega: `HTML_FAILED_BEFORE = 4 ·
HTML_RECOVERED · HTML_STILL_FAILED`.

---

## 2 · OS 7 HISTÓRICOS SEM BYTES

> **NÃO inventes ficheiros. NÃO vás à rede só para deixar um número a zero.**

Por cada um: `OBJECT_ID · SOURCE_ID · RUN_ID · EXPECTED_BYTES · WHY_MISSING ·
RECOVERABLE_FROM_EXISTING_LOCAL_DATA · RECOVERABLE_ONLY_WITH_NETWORK ·
HISTORICAL_ONLY`.

São anteriores à BC2 (ids 6, 9, 11, 12, 19, 25, 28 · 18–19/09 · SIAS ×2, Puglia
N36, LinkedIn mp4 ×2, YouTube wav, monitoraggio), de corridas noutras bancadas.

Se não forem necessários à integridade **atual**: regista como **dívida
histórica conhecida** e segue. Isso é resultado completo, não desistência.

---

## 3 · GATES MÍNIMOS

```
NEW_FAILURES = 0                          SHA_MISMATCH = 0
RECONCILIATION_STRUCTURAL_ERRORS = 0      TEST_CAN_DELETE_OPERATIONAL_STORAGE = NO
SYSTEM_MAP_CHECK = PASS                   PAID_USD = 0
```

`TEST_CAN_DELETE_OPERATIONAL_STORAGE = NO` **re-prova-se**, não se herda do
relatório anterior.

## 4 · NÃO FAZER

Nova Big Collection · fontes novas · Source Curator · **Intelligence** ·
**Portal** · CLAIM/FACT · ORCID · LinkedIn/Instagram.

## 5 · ENTREGA

Escreve `RELATORIO-RESIDUOS-BC2.md` na raiz **e** no último turno:

`INITIAL_HEAD · FINAL_HEAD · REMOTE_HEAD · WORKTREE ·
CLEANUPS_DANGEROUS_BEFORE/AFTER · HTML_FAILED_BEFORE = 4 · HTML_RECOVERED ·
HTML_STILL_FAILED · HISTORICAL_MISSING_BYTES = 7 · HISTORICAL_RECOVERABLE ·
HISTORICAL_IRRECOVERABLE · NEW_FAILURES · RECONCILIATION_STRUCTURAL_ERRORS ·
SYSTEM_MAP_CHECK · COMMITS · PUSH_STATE · KNOW_HOW_DELTA · MODEL_EFFECTIVE`

Não medido = `NOT_MEASURED`. Não alcançado = `NOT_REACHED`. **Nunca um número
plausível.** Commits pequenos, push frequente, sem force.

**Fecha com a secção em português simples** para o dono, que não é engenheiro,
respondendo exactamente a: (1) o que ainda podia apagar dados; (2) o que
aconteceu aos 4 HTML; (3) o que são os 7 ficheiros históricos; (4) **se a
Collection está finalmente estável para seguir adiante** — e se não estiver,
o que falta, pelo nome.

**HARD STOP ao concluir.** Não avances para outra missão.
