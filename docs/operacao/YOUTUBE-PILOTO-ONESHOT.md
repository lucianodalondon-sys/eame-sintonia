# YOUTUBE — O PRIMEIRO PILOTO ONE_SHOT

**2026-09-08** · Estado: **implementado e testado · NÃO EXECUTADO**

---

## 1 · O DEFEITO QUE ESTA MISSÃO CORRIGE — E ELE ERA MEU

Na entrega anterior anunciei `PILOT_READY = SIM`. O `youtube_piloto()` daquele
HEAD passava no pré-voo, imprimia o modo, e terminava assim:

```python
return 4   # ver `youtube-piloto-oneshot`: a execução real é do runner
```

**Não havia execução real depois disso.**

> **PREFLIGHT PASSAR NÃO É PILOTO RODAR.**
> **`PILOT_READY` SEM UMA CHAMADA REAL É ESTADO PROMOVIDO CEDO DEMAIS.**

**Reproduzido antes de corrigir**, com credencial e transporte falsos:

```
RETORNO        = 4
CHAMADAS_A_API = 0   []
```

A trava que impede a repetição está em
`tests/test_youtube_piloto.py::test_TRAVA_passar_no_preflight_sem_chamar_nada_e_FALHA`:
se o piloto passar pelo pré-voo e terminar **sem resolver um único handle**, reprova.

---

## 2 · O QUE O PILOTO FAZ AGORA

Uma `Sessao` para a corrida toda (dois baldes de quota), um `cache_da_execucao()`,
um `run_id`. Por handle:

```
resolver_handle      → channels.list?forHandle   (GERAL, e ZERO busca)
uploads_recentes     → playlistItems.list        (GERAL)
metadata             → videos.list em lote       (GERAL)
comentarios          → commentThreads.list       (GERAL)
                     → comments.list quando a thread veio incompleta
```

**Um canal que falha não apaga os outros quatro.** E `AUTH`, `QUOTA` e `REDE`
nunca viram `ZERO_RESULTS` — o estado canônico diz o que houve. `QUOTA_EXHAUSTED`
e `AUTH_EXPIRED` **param** a corrida: continuar só queimaria o resto do orçamento.

**No ONE_SHOT `conhecidos` fica vazio DE PROPÓSITO**, e o relatório declara
`KNOWN_SOURCE = 'NENHUMA — ONE_SHOT não consulta memória'`. Fingir memória seria
alegar retomada que não existe.

---

## 3 · A PROVA BRUTA

O disco do runner morre no fim do job. RAW recorrente também **não** entra no Git
(P-011). Então:

- o RAW sobe como **artefato do Actions** (`youtube-piloto-raw-<run_id>`, retenção 30 dias);
- o manifesto que **vai ao Git** carrega `SHA256` e `BYTES` de **cada arquivo** — com
  ele a prova é reconciliável mesmo depois de o artefato expirar;
- se o upload falhar, o estado é **`PARTIAL_PROOF`**, nunca `PILOT_PROOF_COMPLETE`.

> **PILOT_PROOF NÃO É OPERATIONAL_STORAGE.** O dono forward do G-42
> (Storage + `raw_asset`) **não** recebeu estes bytes.

---

## 4 · O RUN REAL NÃO ACONTECEU — E O MOTIVO É MECÂNICO

Tentei disparar `scrap-social.yml` na branch atual. O GitHub devolveu **404**.

**Causa medida:** o GitHub só registra um workflow — e só aceita
`workflow_dispatch` por nome de arquivo — quando **o arquivo existe na branch
padrão**. `scrap-social.yml` existe apenas em `claude/scrap-social-na-biblia-v1`.
`actions_list` confirma: 13 workflows registrados, e `scrap-social` não está entre eles.

**O que NÃO fiz, e por quê:** na minha branch, `sintonia-scrap.yml` (esse sim
registrado) é o **outro** workflow da Bíblia — o piloto italiano com navegador,
transcrição e pool da Apify. Dispará-lo para "conseguir um run" rodaria a coisa
errada, na máquina errada, e podia gastar dinheiro. **Um run que não é o piloto
não vale como piloto.**

**O único passo que destrava:** `scrap-social.yml` chegar à `main`. Enquanto isso
não acontece, nada aqui pode subir para `OBSERVED`.

---

## 5 · O ESTADO HONESTO

```
PILOT_ONE_SHOT_IMPLEMENTED = SIM
PILOT_ONE_SHOT_TESTED      = SIM  (16 casos, transporte de fita)
PILOT_ONE_SHOT_OBSERVED    = NÃO  (o workflow não é despachável desta branch)
OPERATIONAL_OBSERVED       = NÃO
```

| medida | valor |
|---|---|
| chamadas ao YouTube | **0** |
| SEARCH_CALLS_USED | **0** |
| GENERAL_UNITS_USED | **0** |
| comentários, vídeos, canais | **0** — nenhum número é reportado porque nenhum existe |
| COST_USD | **0,00** |
| APIFY_CALLS | **0** |
| checkpoint rows before/after | **0 / 0** |
| escrita no Supabase · Storage · migration | **0 · 0 · 0** |

### System Map

```
YOUTUBE official route   DECLARED ✅ · CODE ✅ · OBSERVED ❌
CHECKPOINT               LIVE_SCHEMA = OBSERVED · USAGE = NOT_OBSERVED
RAW                      PILOT_PROOF = NOT_OBSERVED · OPERATIONAL_STORAGE = NOT_OBSERVED
```

**CAN DO ≠ DID DO.** Nenhum método sobe para `OBSERVED` sem um run real.

---

## 6 · OS DOIS PRÓXIMOS PASSOS, NESTA ORDEM

1. **Levar `scrap-social.yml` à `main`** — sem isso o piloto não é despachável.
   Depois: `fase: youtube-piloto-oneshot`.
2. **Só então** ligar o operacional: `YouTube → RAW durável (G-42) → conteúdo
   durável → checkpoint avançado`, nessa ordem. Hoje **não** existe caller provado
   dessa cadeia, e por isso `OPERATIONAL_READY = NO`.
