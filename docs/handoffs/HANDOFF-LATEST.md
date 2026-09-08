# HANDOFF — ÚLTIMO ESTADO · 2026-09-08

> O ficheiro grande é
> [`HANDOFF-EMERGENCIA-COLLECTION-FOUNDATION-2026-09-08.md`](HANDOFF-EMERGENCIA-COLLECTION-FOUNDATION-2026-09-08.md).
> **Este é só o ponteiro para onde o trabalho parou.**

```
WORK_BRANCH   claude/collection-foundation-integration-v1
WORK_HEAD     96cbb2e7          (medir outra vez: git fetch)
WORKTREE      limpa
```

## Checkpoints já empurrados

| commit | o que fechou |
|---|---|
| `51a26550` | **M1A** · a trava da inteligência, congelada por espécie |
| `be73768e` | **reconciliação M1** · a trava consome o veredito, não o redefine |
| `a9979c2c` | **O1** · censo dos donos — 7 de 15 conceitos com dono duplicado |
| `6e26e4a7` | **O2** · o contrato da telemetria, sem instalar nada |
| `96cbb2e7` | **O3** · o fluxo no seco — `NOT_RUN` ≠ `ERROR`, provado |

## Os três vereditos, separados

```
M1_CLASSIFICATION_PASS        CLOSED       a classificação acabou
SOURCE_NETWORK_COVERAGE       INCOMPLETE   47 fontes sem rota provada
COLLECTION_FOUNDATION_CLOSED  NÃO          0 classes fechadas
```

⚠️ **Podem discordar sem se contradizer.** Um veredito só obrigaria a mentir em
dois. `ONE QUESTION → ONE OWNER`: a trava **lê** `leis/fundacao_da_coleta.py`,
não recalcula.

## Próximo checkpoint

**O4 — relatórios**: por `RUN` · hora · `source` · `route` · `executor` ·
`stage`. Mostrando input, output, grão, pass, reject, unknown, error,
accounted, unaccounted, duração, custo.

Depois: `O5` collection management · `O6` source learning · `O7` evolution
foundation · `O8` System Map com `NOT_MEASURED` em vez de verde por silêncio.

**Não começar a M2.**

## Verificar em quatro comandos

```bash
cd /f/eame-sintonia && git fetch origin && git status --porcelain
python system-map/scripts/validate_system_map.py
python provas/trava_da_inteligencia_morde.py
python provas/fluxo_no_seco.py
```

Esperado: worktree limpa · `SYSTEM_MAP_CHECK=PASS` · `TRAVA_MORDE=PASS` ·
`FLUXO_NO_SECO=PASS`.

**Zero escritas em produção. Zero rede. Inteligência congelada.**
