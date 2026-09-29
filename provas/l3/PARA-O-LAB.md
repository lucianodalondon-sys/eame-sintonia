# L3 → LAB · caminhos para a prova reversa TELA → POTE → INTELLIGENCE → SALA → RAW → FONTE

Escrito em 28/09/2026 (missao L3, com a correcao do dono das ~20:37). So caminhos e SHAs: nenhum dado do pote
entra no Git (as fotos e o registo ficam em `%TEMP%`, fora do repositorio, como manda
`portoes/PUBLICACAO-AUTOMATICA.json` → REGISTRO.NO_GIT).

## ⚠️ O que a tela e, e o que nao e (atualizado D152, 29/09)

- Os 2 objetos da R9 **nao** estao no Opportunity Radar (sao FATOS). Radar LIVE = 0.
- Destino semantico = familia `agrometConditions`, **sem tela de cliente** (adendo do coordenador D152).
- A unica tela que os desenha e a rota **interna de debug** `/debug/intelligence-pot` → `/portale#debug-intelligence-pot`,
  com a faixa «EXPERIMENTAL · NON PER IL CLIENTE», dentro do bloco do compartimento `windows` (escolhido pelo pote).
  As telas de cliente sao o casco original e nao os mostram (conferido no ar: C6_NO_AR_CLIENTE_SEM_CAMADA_TECNICA).

## 1 · TELA (preview, NAO producao)

| | |
|---|---|
| endereco | `https://sintonia-eame-preview-qae9eearx-london-creative.vercel.app/debug/intelligence-pot` (307 → `/portale#debug-intelligence-pot`) |
| deployment | `dpl_J4gXk9bnLmiHAvwZtXhNnv9NVEaD` (preview, sem `--prod`) |
| codigo servido | `c7671ff7eef9f767016dce326fa03f6d9f572016` (ramo `claude/l3-radar-original-v1`) |
| envelope no ar | `/sintonia-pote-publicado.js` → `POTE_SHA256 = 276b490fd698c46188f4f5ec1a04de79503b0fc11c6ec82c5ea29fa833b87feb` (C6_NO_AR_SHA = PASS) |
| no DOM | `[data-pote-compartimento="windows"]`, `[data-pote-objeto="AF-2cc19f200815fa06"]`, `[data-pote-objeto="AF-11c9e6b6ee8caa6e"]`; em cada prova `[data-pote-trecho]` (o trecho literal) e `[data-pote-raw]` (RAW sha256 + caminho) |
| fotos e contagens | `%TEMP%/l3-pub/2026-09-28/222403-334445-276b490f/DEPOIS/` (debug-intelligence-pot.png, CONTAGENS.json) · `REGISTO.json` na mesma pasta |
| publicado por | `portoes/publicar_preview_da_pasta.py --raiz …/intelligence-experimental --modo preview` → `publicar_portal_sozinho.py` (C0..C6 todas PASS) |

## 2 · POTE

| | |
|---|---|
| ficheiro | `C:/Users/London1/sintonia-sala-italia/intelligence-experimental/PARA-O-CASCO-R9/POTE-R9-PARA_CLIENTE.json` |
| sha256 do ficheiro | `9aa916e328845c8c10b17a6c392c3ac9b23279f105e4a1e5e07d3aae1bc8d963` (= SHA256SUMS.txt = MANIFESTO-R9.json) |
| sha256 canonico | `276b490fd698c46188f4f5ec1a04de79503b0fc11c6ec82c5ea29fa833b87feb` (= o do envelope no ar) |
| completude | SHA256SUMS.txt da pasta: 10/10 linhas conferem (lido 28/09) |
| contrato | `CONTRATO-LIBERACAO-POR-OBJETO-v2.2.md` sha256 `f10879923a3a…907e`; os 2 objetos com C1..C7 = PASSOU e C8 = decisao do dono |

## 3 · INTELLIGENCE

| | |
|---|---|
| corrida | `IR-56c79b0c78fc3fa1e747` · RESULT_STATE DONE · RULESET G0/v4 |
| livro | `…/EXPD78-R9-20260928T155047Z/saida/LIVRO-IR-56c79b0c78fc3fa1e747.json` sha256 `a11a9f1522fa…516f` |
| gerador e validador | producao `e24139702b8216ad54127cf63a14b550bcd4aeab` |

## 4 · SALA

| | |
|---|---|
| copia lida | `…/EXPD78-R9-20260928T155047Z/copia/SALA_ATUAL.json` sha256 `00cb7cb0eb68…73d2` (275 linhas) |
| item | `ITEM_ID derived:11` · `RAW_OBSERVATION_ID 36` · `SOURCE_ID IT-T3-008` · `DOCUMENT_ID ARIF:SETTIMANALE:2026:N38` · run `IT-T3-2026-09-20-110656-6e4ffc27a86c5269` |
| ⚠️ estado na fila | `estado_da_fila = WAITING`, `consumido_em = None` (lido na copia, 28/09). O LAB decide se isto importa. |
| lugar | `source_location = Bari` (sede da fonte) ≠ `fact_location` do objeto (Puglia / Nociglia e Otranto) — o casco nao troca um pelo outro |

## 5 · RAW

| | |
|---|---|
| RAW_STORAGE_PATH | `XX/it-t3-008/DOCUMENT/85cb86ebd6582997-ubddcacce8c34dc87-Notiziario_Agrometeorologico_N38_16-09-2026.pdf` |
| no disco | `C:/Users/London1/sintonia-sala-italia/armazem/` + o caminho acima |
| RAW_SHA256 | `85cb86ebd6582997d66c363d568e82e6172d78cc9a3c72db3c9eadcc7ec4d8b1` — **relido do byte em 28/09 pela L3: igual** |
| trechos | TRECHO_DA_AFIRMACAO / TRECHO_DA_DATA / TRECHO_DO_LUGAR + SECAO (inicio 9085, fim 13512) em cada PROVA do pote |

## 6 · FONTE

`https://www.agrometeopuglia.it/bollettino-elettronico/settimanale/2026/Notiziario_Agrometeorologico_N38_16-09-2026.pdf`
— publicado 2026-09-16, colhido 2026-09-20 11:07:15 UTC. FACT_TIME 2026-09-07/2026-09-13 (≠ publicacao).

## A casa

`/casa` e `/casa.html` no mesmo preview redirecionam para `/accesso` (C6_NO_AR_REDIRECIONADA_CASA = PASS; 43/44
antigos visiveis = 0). `casa.html` continua no Git e na pasta; so o endereco deixou de a mostrar.
