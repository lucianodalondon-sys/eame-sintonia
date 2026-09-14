# Estudo da aba **CANAL E MERCADO** — o dado já está guardado, a tela ainda não existe

**Data:** 2026-09-14 · **Estado:** estudo de ferramenta. **Não entra no portal nesta rodada.**
**Coletor:** `coleta/canal_mercado.py` · **Fonte:** IT-T10-001 (ARPAV) × IT-T4-001 (registro)

> Esta aba responde a pergunta que o SINTONIA ainda não respondia: **onde o produto
> efetivamente se move**. Não é tela de portfólio (isso é o registro) nem de problema (isso é
> o boletim). É a terceira camada: **movimento**.

---

## 1 · O que a aba responde — quatro perguntas, nesta ordem

| # | Pergunta | Tabela que responde | Estado |
|---|---|---|---|
| 1 | **Quanto pesa este território?** | `DIM-TERRITORIO` | COMPROVADO |
| 2 | **Quem está forte aqui, e em quê?** | `DIM-TITOLARE` + `FATO-FORCA-DE-MARCA` | COMPROVADO |
| 3 | **Onde há espaço para nós?** | `FATO-OPORTUNIDADE` | COMPROVADO, com ressalva escrita |
| 4 | **Com quem eu falo?** | `comprador_candidato` (semente de 6) | **PARCIAL — a fonte não traz o comprador** |

---

## 2 · Como o dado está guardado — a cadeia inteira

```
ARPAV (CSV, CC BY 4.0)
  │  py coleta/canal_mercado.py --coletar
  ├─► data/collection-store/italy/IT-T10-001/ARPAV_VENDITE_2025/v1_<sha12>/*.csv   ← BRUTO, antes de parse
  ├─► data/collection-ledger/italy/observations.ndjson   ← o documento, com sha256, saúde e rodapé
  ├─► data/collection-ledger/italy/runs.ndjson           ← a corrida, com IP de saída e GIT_HEAD
  └─► data/samples/RUN-MANIFEST.json                     ← RUN_ID que RESOLVE (contrato CAMPOS_RUN)
         │  --normalizar  (lê o bruto do store, nunca da rede)
         ├─► DIM-TERRITORIO · DIM-TITOLARE · DIM-PRODUTO
         ├─► FATO-VENDA-DECLARADA · FATO-FORCA-DE-MARCA · FATO-OPORTUNIDADE
         ├─► PACOTE-RTV-POR-PROVINCIA        ← o rollup que o Field Sales lê
         └─► MANIFESTO-DAS-TABELAS           ← QA, avisos e sha256 de cada tabela
                │  --sql
                └─► supabase/importacoes/IT-VENETO-CANAL-2026-09-14.sql  (migration 022; NÃO executada)
```

**Números da corrida de 2026-09-14:** 10.716 linhas válidas · **3 descartadas com motivo** ·
**0 órfãs no registro (casamento de 100%)** · 167 titulares · 1.885 produtos vendidos ·
726 linhas de oportunidade · 16.265.861,79 kg/l.

---

## 3 · As quatro leis que viajam **dentro** do dado, não no rodapé de uma reunião

1. **Volume não é valor.** A unidade é kg/litro. Enxofre e cobre dominam o volume e custam
   pouco por quilo. A coluna chama-se `quota_volume_pct`, nunca `market_share`.
2. **Ausência na declaração não é ausência de venda.** A tabela de oportunidade tem `classe`
   com dois valores, e nenhum diz "não vendido".
3. **O comprador não está na fonte.** Por isso `comprador_candidato` é tabela separada, com
   `estado_evidencia` e `fonte` por linha.
4. **Nada aqui é dado interno da ADAMA** (P-003 `EXTERNAL-ONLY`; a distinção está em D-027).

O aviso 1 e o aviso 2 estão gravados em **todas** as tabelas geradas, no manifesto e no
cabeçalho do SQL. Quem copiar uma tabela leva o aviso junto.

---

## 4 · Esboço da tela (ainda sem uma linha de CSS)

```
┌─ CANAL E MERCADO ─────────────────── região: Vêneto ▾   ano: 2025 ▾ ─┐
│                                                                      │
│  MAPA DA REGIÃO            │  A PRATELEIRA DESTA PROVÍNCIA           │
│  província pintada pelo    │  ┌────────────────────────────────┐     │
│  volume declarado          │  │ UPL           1.665.128  25,5% │     │
│  (VR 6,5 mi · TV 4,8 mi …) │  │ Syngenta        521.775   8,0% │     │
│  ● ponto de venda (OSM)    │  │ ADAMA Italia    276.674   4,2% │     │
│                            │  └────────────────────────────────┘     │
│                            │  mix: fungicida 60% · herbicida 16% …   │
│                                                                      │
│  ONDE HÁ ESPAÇO                         COM QUEM FALAR               │
│  ┌───────────────────────────────┐      ┌──────────────────────────┐ │
│  │ SOLOFOL      fungicida  63 t  │      │ Cons. Treviso e Belluno  │ │
│  │ vende no Vêneto, não aqui     │      │ €18,1 mi de defesa/2024  │ │
│  │ ⚠ sem venda DECLARADA         │      │ 3 filiais localizadas    │ │
│  └───────────────────────────────┘      └──────────────────────────┘ │
└──────────────────────────────────────────────────────────────────────┘
```

O problema e o produto que responde já existem no acervo (X-004/X-006) e entram como a
faixa de cima da tela — não como outra aba.

---

## 5 · O que falta antes de isto virar tela

| # | Falta | Custo | Quem decide |
|---|---|---|---|
| 1 | **O comprador com nome e endereço** | pedido às 9 ULSS (€0) **ou** extração do Registro Imprese (pago) | quem paga |
| 2 | **Segundo ano de série** (2024) para dizer "cresceu/caiu" | um `--ano 2024` | ninguém — é rodar |
| 3 | **Outras regiões** — só o Vêneto foi aberto | verificar se cada região publica o equivalente | pesquisa |
| 4 | **Quota em valor** | painel pago | quem paga |
| 5 | **Aplicar a migration 022 e a importação** | credenciais são secrets do CI | operação |
| 6 | **Decidir se esta camada aparece ao cliente** | — | **P-010, aberta** |

**A primeira delas é a única que muda a natureza da aba.** As outras cinco melhoram uma aba
que já funciona com o que está guardado hoje.
