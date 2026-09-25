# RELATÓRIO DA 3.ª ONDA WEB — modelo para preencher

> Modelo preparado em 25/09/2026 sobre `e5cd691f` (PREFLIGHT-ONDA3). Cada `⟨…⟩` é um número a
> medir **depois** da onda; cada número leva o denominador ao lado. O que não se conseguir medir
> escreve-se **NAO SEI**, nunca zero nem vazio.
>
> Fontes dos números (todas já existem; nada novo a construir):
> `%ONDA%\ONDA-WEB-ESTADO.json` (por fonte) · `%ONDA%\TETO-ONDA.json` (livro do teto) ·
> `%ONDA%\PROVA-TETO.json` · `%ONDA%\relatorio\RELATORIO-PASSAGEM.md` + `CLASSES.tsv` +
> `CAPAS-A-CONFIRMAR.tsv` · `data\collection-ledger\italy\runs.ndjson` · a Sala real, só `SELECT`
> com `default_transaction_read_only=on`, na vista `sala_de_espera_atual`.

---

## 1. Identidade da onda

| campo | valor |
|---|---|
| pasta da onda (`%ONDA%`) | ⟨…⟩ |
| árvore do vivo (`ARVORE`) | ⟨commit⟩ |
| coorte: sha256 do blob · N fontes · `INSTALACAO` · `DEMOTION_B5` | ⟨sha⟩ · ⟨N⟩ · ⟨commit⟩ · ⟨texto⟩ |
| `--historico=` passado | ⟨caminho(s)⟩ |
| início → fim (hora local) | ⟨INICIO⟩ → ⟨FIM⟩ |
| paragem do robô (`PARAR.flag` posto → retirado) | ⟨hh:mm⟩ → ⟨hh:mm⟩ = ⟨min⟩ |
| backup da Sala (caminho · sha256 · `IGUAL_A_SALA_REAL`) | ⟨…⟩ |
| disjuntor que parou a onda (`PAROU`) | ⟨null / qual⟩ |

## 2. Resultado por fonte (uma linha por fonte da coorte)

De `ONDA-WEB-ESTADO.json` (lista por fonte) e `CLASSES.tsv` (`veredito` por derivado).

| N | SOURCE_ID | STATUS | PORQUE_NAO_CORREU | RUN_ID | s | egresso antes/depois | docs novos (raw_asset Δ) | itens na Sala (sala_de_espera Δ) | SIM | NAO | NAO_SEI | ABORTED? |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | ⟨…⟩ | SUCCESS / FAILED / TETO_DOMINIO | ⟨…⟩ | ⟨…⟩ | ⟨…⟩ | IT/IT | ⟨Δ⟩ | ⟨Δ⟩ | ⟨n⟩ | ⟨n⟩ | ⟨n⟩ | ⟨sim/não⟩ |

- «docs novos» = `SALA_DEPOIS.raw_asset − SALA_ANTES.raw_asset` da fonte; «itens na Sala» =
  o mesmo para `sala_de_espera`.
- SIM / NAO / NAO_SEI = contagem da coluna `veredito` de `CLASSES.tsv` para o `source_id`.
- `ABORTED?` = a linha da corrida em `runs.ndjson` traz o campo `ABORTED` (conserto FECHAR-ONDA2).

**Totais:** correram ⟨n⟩ de ⟨N⟩ · SUCCESS ⟨n⟩ · FAILED ⟨n⟩ · TETO_DOMINIO ⟨n⟩ · docs novos
⟨n⟩ · itens novos na Sala ⟨n⟩ · SIM ⟨n⟩ de ⟨derivados⟩ · NAO ⟨n⟩ · NAO_SEI ⟨n⟩.

Comparação com a 2.ª onda (28 fontes: 20 SUCCESS, 7 TETO_DOMINIO, 1 FAILED; Sala
71→78 / 1441→1474 / 1133→1166 / 943→976 / 408→421): ⟨…⟩.

## 3. Pedidos por domínio (D38, teto 5 por domínio por onda)

| domínio | livro do teto (`TETO-ONDA.json`) | soma em `runs.ndjson` (PEDIDOS_POR_HOST) | iguais? | fontes que gastaram | fontes cortadas por TETO_DOMINIO |
|---|---|---|---|---|---|
| ⟨…⟩ | ⟨n⟩ | ⟨n⟩ | ⟨sim/não⟩ | ⟨…⟩ | ⟨…⟩ |

- **PROVA-TETO:** ⟨PASS / FAIL / NAO_SEI⟩ · corridas ⟨n⟩ · pedidos ⟨n⟩ · máximo por domínio ⟨n⟩ ·
  acima do teto ⟨lista⟩ · sem linha no livro ⟨lista⟩.
- Na 3.ª onda **NAO_SEI é defeito** (os dois consertos da FECHAR-ONDA2 estão instalados).
- **Rotação justa** (`onda_web.py:100-135`): por domínio, a ordem aplicada foi ⟨…⟩; quem ficou
  de fora nesta onda e foi primeiro na 2.ª ⟨…⟩.

## 4. Data e local de cada item (migration 033)

Os quatro campos, **cada um com a sua base** (a vista `sala_de_espera_atual` já devolve a última
revisão). Consulta só de leitura, com os RUN_ID da onda:

```sql
set default_transaction_read_only = on;
select source_id, item_id,
       published_at,    published_at_basis,
       source_location, source_location_basis,
       fact_time,       fact_time_basis,
       fact_location,   fact_location_basis,
       completude_tempo_lugar, revisoes
from public.sala_de_espera_atual
where run_id in (⟨RUN_ID da onda⟩)
order by source_id, ordem;
```

### 4a. Por item (anexo, uma linha por item novo)

| SOURCE_ID | item_id | publicação · base | local da fonte · base | data do fato · base | local do fato · base | completude (P/C/N por campo) |
|---|---|---|---|---|---|---|
| ⟨…⟩ | ⟨…⟩ | ⟨valor⟩ · ⟨base⟩ | ⟨…⟩ · ⟨…⟩ | ⟨…⟩ · ⟨…⟩ | ⟨…⟩ · ⟨…⟩ | ⟨…⟩ |

### 4b. Resumo dos quatro campos (denominador = itens novos na Sala)

| campo | PROVADA | CALCULADA | NAO SEI | total |
|---|---|---|---|---|
| publicação (`published_at`) | ⟨n⟩ | ⟨n⟩ | ⟨n⟩ | ⟨N⟩ |
| local da fonte (`source_location`) | ⟨n⟩ | ⟨n⟩ | ⟨n⟩ | ⟨N⟩ |
| data do fato (`fact_time`) | ⟨n⟩ | ⟨n⟩ | ⟨n⟩ | ⟨N⟩ |
| local do fato (`fact_location`) | ⟨n⟩ | ⟨n⟩ | ⟨n⟩ | ⟨N⟩ |

- PROVADA / CALCULADA / NAO SEI vêm de `completude_tempo_lugar` (D62). CALCULADA na data do fato
  = contada a partir da publicação (D63); a conta está em `tempo_lugar_evidencia.FACT_TIME_CALCULO`.
- Lembrar as separações: publicação ≠ data do fato; local da fonte ≠ local do fato; a REGION do
  Atlas **não** é sede.

## 5. Critérios da passagem (`RELATORIO-PASSAGEM.md`)

| critério | 2.ª onda | 3.ª onda |
|---|---|---|
| C1 egresso IT por corrida | FAIL | ⟨…⟩ |
| C2 matéria não capa | PENDENTE_HUMANO | ⟨…⟩ (capas a confirmar: ⟨n⟩) |
| C3 ponte em runtime | FAIL | ⟨…⟩ |
| C4 proveniência completa | PASS | ⟨…⟩ |
| C5 fact time/location | PASS | ⟨…⟩ |
| C6 zero bypass | PASS | ⟨…⟩ |
| C7 proporção por fonte e classe | PASS | ⟨…⟩ |
| C8 duas perguntas | NAO_SE_APLICA | ⟨…⟩ |
| C9 idioma não dá NAO SEI | FAIL | ⟨…⟩ |

## 6. Sala antes / depois e religar

| tabela | antes | depois | Δ | desceu? |
|---|---|---|---|---|
| sala_de_espera | ⟨n⟩ | ⟨n⟩ | ⟨n⟩ | ⟨não⟩ |
| raw_asset | ⟨n⟩ | ⟨n⟩ | ⟨n⟩ | ⟨não⟩ |
| storage_object | ⟨n⟩ | ⟨n⟩ | ⟨n⟩ | ⟨não⟩ |
| derived_artifact | ⟨n⟩ | ⟨n⟩ | ⟨n⟩ | ⟨não⟩ |
| collection_run | ⟨n⟩ | ⟨n⟩ | ⟨n⟩ | ⟨não⟩ |
| sala_de_espera_revisao | ⟨n⟩ | ⟨n⟩ | ⟨n⟩ | ⟨não⟩ |

- Livros do bot: sha256 + linhas antes/depois dos ficheiros sujos ⟨iguais salvo os que a onda
  escreve: `runs.ndjson`, `observations.ndjson`, …⟩.
- `PARAR.flag` retirado ⟨hh:mm⟩ · supervisor no SO: ⟨1⟩ (PID ⟨…⟩) · local == remoto ⟨sim⟩.

## 7. Veredito

⟨ONDA3 FECHADA / FECHADA COM NAO SEI / PARADA POR DISJUNTOR⟩ — em palavras simples: ⟨…⟩.
