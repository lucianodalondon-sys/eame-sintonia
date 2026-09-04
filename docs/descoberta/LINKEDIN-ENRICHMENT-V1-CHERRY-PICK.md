# LINKEDIN ENRICHMENT V1 — CLASSIFICAÇÃO DOS ARQUIVOS PARA CHERRY-PICK

**Data:** 2026-09-04 · **Branch:** `claude/linkedin-enrichment-v1-y1gikl`
**Base do diff:** `c88690c` · **Decisão:** `D-013` / `D-014`

> **Nada foi mergeado. Nada foi implantado. Nenhuma coleta nova.**
> Este documento existe para que o cherry-pick mínimo seja uma escolha informada,
> arquivo por arquivo, e não um `merge` que arrasta experimento junto com capacidade.

A branch mudou **15 arquivos**. Nenhum arquivo canônico de **código** foi tocado.

---

## 1 · `SAFE_OFFLINE_FILES` — a capacidade aprovada

Sem rede, sem chave, sem provider. Lê o `.raw.json.gz` que já está no repositório.

| arquivo | linhas | o que é |
|---|---|---|
| `scripts/linkedin_enriquecimento.py` | 909 | releitura do RAW já pago · data pelo ID com cross-check · os quatro guardas |
| `tests/test_linkedin_enriquecimento.py` | 423 | 45 provas, todas offline |

**Conferido, não afirmado:**
- `grep -cE "requests\.|urlopen|subprocess|httpx"` → **0**. Há teste que executa essa
  proibição (`test_o_arquivo_nao_tem_nenhuma_chamada_de_rede`).
- não importa `coletor` nem `apify_pool` — teste próprio.
- o custo sai nomeado: `REPROCESSAMENTO_DO_RAW_EXISTENTE_API_COST = US$ 0`, com
  `CUSTO_NAO_SIGNIFICA` ao lado. Teste reprova um `API_COST_USD` cru.

### ⚠ DEPENDÊNCIA DURA — estes dois não viajam sozinhos

Levar `tests/test_linkedin_enriquecimento.py` **sem** os arquivos de contagem da
seção 4 **quebra a suíte**: `tests/test_metricas.py` e `tests/test_handoff.py`
comparam o número publicado nos documentos com o número real de testes.

```
cherry-pick =  scripts/linkedin_enriquecimento.py
            +  tests/test_linkedin_enriquecimento.py
            +  os 8 arquivos de contagem (seção 4)
```

Alternativa, se os 8 forem indesejados agora: levar só o `scripts/`, deixar o
`tests/` para depois. **Não recomendado** — a capacidade sem as provas é a parte
que não se pode conferir.

---

## 2 · `CANONICAL_BUG_FILES` — registrados, **intactos nesta branch**

`git diff --name-only` sobre os dois → **0 arquivos**. Nenhuma linha foi tocada.

| arquivo | linha | defeito | dono |
|---|---|---|---|
| `scripts/youtube_transcrever.py` | `199` | retomada por `VIDEO_ID` enquanto a saída depende de `ASR_MODEL`, `ASR_BEAM`/parâmetros e idioma. `medium` depois de `small` preserva o texto do `small` e o reporta feito | camada de transcrição |
| `scripts/speaker_universo.py` | `155`, `193` | teto de páginas e fim de cursor produzem ambos `COLLECTED` com contagem de aparência real | camada de universo |

**Ação:** nenhuma agora. Registrados em `D-014`. **Não abrir missão se disputar o
sprint do Portal Itália.**

---

## 3 · `EXPERIMENT_ONLY_FILES` — medição, não rota

| arquivo | linhas | por que é experimento |
|---|---|---|
| `data/samples/LINKEDIN-ENRICHMENT/MICROTESTE-V1.json` | 274 | contém as sondagens pontuais das rotas públicas: 5 perfis (999/authwall), 56 `HEAD` de vídeo, 12 `HEAD` de PDF, 5 páginas de embed, 3 transcrições |

**Estas rotas estão `DISALLOW` no `robots.txt` do `www.linkedin.com` e do
`dms.licdn.com`.** O arquivo é o registro de que a pergunta "isto é possível?" foi
respondida — **e a resposta não vira rota de produção** (`D-013`).

**Recomendação:** manter na branch como evidência. Se for para o canônico, que vá com
o carimbo `EXPERIMENT_ONLY` visível — ele já traz o bloco
`O_LIMITE_QUE_NAO_E_TECNICO` com os dois `robots.txt` citados.

### Caso à parte — derivado e regenerável

| arquivo | linhas | bytes |
|---|---|---|
| `data/samples/LINKEDIN-ENRICHMENT/ENRIQUECIMENTO-V1.json` | 55.426 | 2,7 MB |

É **saída** do script da seção 1 sobre o RAW já no repositório: `SAFE_OFFLINE` quanto à
origem, mas **regenerável em um comando** e **duplica no repositório texto que já está
em `raw-paid/`** (372 posts + 138 perfis de pessoas nomeadas — mesma questão de GDPR já
aberta em `P-008`, sem exposição nova).

**Medido:** duas execuções seguidas são idênticas **exceto pelos carimbos
`CAPTURED_AT`**. Ou seja, cada regeneração produz um diff de 2,7 MB que não significa
nada.

**Recomendação:** **não** levar no cherry-pick. Regenerar com
`py scripts/linkedin_enriquecimento.py enriquecer` quando precisar. Se for levado,
congelar `CAPTURED_AT` primeiro, ou o arquivo vira ruído permanente no histórico.

---

## 4 · `DOC_ONLY_FILES`

### 4a · Documentação nova desta frente

| arquivo | linhas |
|---|---|
| `docs/descoberta/LINKEDIN-ENRICHMENT-V1.md` | 411 |
| `docs/descoberta/LINKEDIN-ENRICHMENT-V1-CHERRY-PICK.md` | este |
| `docs/decisoes/DIARIO-DE-DECISOES.md` | `D-013`, `D-014`, `P-010`, `P-011` |

### 4b · Contagem de testes — **acoplados à seção 1**

Oito arquivos, e a mudança em cada um é **exclusivamente** `329 → 374`. Conferido:
o diff inteiro dos oito são pares de linhas com o marcador
`<!--M:TEST_COUNT_CURRENT-->`, e nada mais.

```
HANDOFF-CONTA-CLAUDE-SINTONIA-EAME.md
PROMPT-PARA-NOVA-CONTA-CLAUDE.md
docs/apresentacao/PILOTO-CLASSIFICACAO.md
docs/ferramentas/ARQUITETURA-DE-INFORMACAO-EAME.md
docs/piloto/EXTERNAL-ONLY-BUSINESS-CASE.md
docs/piloto/O-QUE-PODEMOS-DIZER.md
docs/piloto/PACOTE-DE-MATERIA-PRIMA-EAME.md
docs/piloto/VEREDITO-M10-HANDOFF.md
```

São gerados por `py scripts/metricas_canonicas.py --sync`. **Se o cherry-pick levar
outro número de testes, rode o `--sync` em vez de copiar estes arquivos** — o número
tem de sair do ledger, não da cópia.

---

## 5 · RESUMO DA DECISÃO DE CHERRY-PICK

| levar | arquivo |
|---|---|
| ✅ | `scripts/linkedin_enriquecimento.py` |
| ✅ | `tests/test_linkedin_enriquecimento.py` |
| ✅ | os 8 da seção 4b — ou rodar `metricas_canonicas.py --sync` |
| ✅ | `docs/descoberta/LINKEDIN-ENRICHMENT-V1.md` · `D-013` / `D-014` no diário |
| ⚠ | `MICROTESTE-V1.json` — só com carimbo `EXPERIMENT_ONLY` |
| ❌ | `ENRIQUECIMENTO-V1.json` — regenerar, não copiar |
| ❌ | nada em `scripts/youtube_transcrever.py` ou `scripts/speaker_universo.py` — **não há nada a levar; eles estão intactos** |

**Nenhum deploy. Nenhuma coleta nova. Nenhuma escala.**

---

## 6 · O QUE VEM DEPOIS — e a ordem importa

1. **PONTE DE IDENTIDADE** (`P-010`) — somente leitura, sem fuzzy-match.
   `PERSON_ID` ↔ `ORIGIN_ID`, com `EVIDENCE`, `MATCH_RULE` e
   `CONFIDENCE ∈ {PROVED, CANDIDATE, NO_MATCH}`. Nome parecido sozinho **não é match**.
   Não criar pessoa, não fundir pessoa, não escrever no dono canônico.
2. **`POST_BY_PROFILE`** (`P-011`) — só depois da ponte, em no máximo 3 pessoas
   `PROVED`, **com custo estimado informado antes** e sem rodar sem autorização.
3. **VÍDEO** — terceiro. A microamostra é 3 vídeos: **não inferir 33% de rendimento.**
4. **DOCUMENTO** — depois da apresentação. `0/3` úteis; mojibake é
   `DOCUMENT_NOT_DECODED`, não "documento sem conteúdo".
