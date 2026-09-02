# QA REPORT — ADAMA ITALY PRODUCT INTELLIGENCE (rodada 2)

**Data:** 2026-09-02 · **Semente:** 20260902 (reproduzível)

**Método:** cada checagem reabre a **fonte bruta** — o CSV do Ministero, o censo do catálogo,
a tabela FRAC e o Anexo do 540/2011 — e tenta derrubar o registro publicado.

---
## Resultado

| | |
|---|---:|
| QA_SAMPLE_SIZE | 48 |
| QA_PASS | 46 |
| QA_CORRECTED | 1 |
| QA_REJECTED | 0 |
| QA_UNREVIEWED | 1 |
| **MEASURED_ERROR_RATE** | **0.0** |

## Estratos
| Estrato | Registros | Reprovados |
|---|---:|---:|
| HERBICIDAS | 5 | 0 |
| FUNGICIDAS | 5 | 0 |
| INSETICIDAS | 5 | 0 |
| SPECIALI_TODOS | 5 | 0 |
| OUTRO_TITULAR | 5 | 0 |
| VENCIMENTO_SENSIVEL | 5 | 0 |
| MOA | 5 | 0 |
| ROTULOS_MULTI_CULTURA | 1 | 0 |
| FRAC | 5 | 0 |
| EU | 5 | 0 |
| MISTURAS | 1 | 0 |
| CORRECAO_DO_BASELINE | 1 | 0 |

---
## A correção registrada

**separador de mistura em sostanze_attive**

- a missao anterior dividia a mistura por '+', mas o registro separa por '|' e nunca por '+' — 148 dos 602 registros ADAMA tem mistura
- consequencia: NENHUMA mistura foi separada, e cada uma virou um MoA artificial, o oposto da regra declarada
- corrigido em scripts/adama_it_intelligence.py (_componentes); as substancias ativas cairam de 169 falsas para 122 reais
- o defeito passou pelo QA anterior porque nenhuma checagem olhava separacao de mistura; a checagem agora existe e faz parte da amostra

Reportar `QA_CORRECTED = 0` tendo corrigido um defeito de substância seria esconder a falha.

---
## O detector prova que reprova

fault injection DENTRO das linhas efetivamente sorteadas — corromper linha que a amostra nao alcanca nao testa detector nenhum. Rodado em 2026-09-02, arquivos restaurados depois.

| Rodada | Camada | Plantados | Na amostra | Pegos |
|---|---|---:|---:|---:|
| 1 | identidade e estado | 4 | 3 | 3 |
| 2 | FRAC, EU e misturas | 7 | 7 | 7 |
| **total** | | **11** | **10** | **10** |

Recall sobre o que a amostra alcançou: **1.0**.

> um dos defeitos plantados foi o proprio 'M 0' — o digito perdido que derrubou a leitura anterior do FRAC. O detector reprovou.

Tipos de defeito provados: `HOLDER_MISMATCH`, `REGISTRATION_NOT_IN_SOURCE`, `INFERENCE_STRONGER_THAN_SOURCE__MARKETABLE`, `FRAC_CODE_DIFFERS_FROM_TABLE`, `FRAC_MATCH_METHOD_NOT_DECLARED`, `EU_EXPIRY_DIFFERS_FROM_ANNEX`, `EU_APPROVAL_DATE_DIFFERS_FROM_ANNEX`, `RENEWAL_STATE_STRONGER_THAN_SOURCE`, `MISTURA_COLADA`.

---
## Sem revisão, e por quê

- **ROTULOS_MULTI_CULTURA** — nenhum uso de rotulo foi extraido: 7 rotas de recuperacao tentadas, 0 documentos recuperados — ver RECOVERY em LABEL-MANIFEST.json

## Portão de segurança (§21)

- **47** registros são `QA_PASS` ou `QA_CORRECTED` e podem sustentar sozinhos afirmação forte ao cliente.
- **0** pares de uso de rótulo são client-safe: não existem.
- `QUARANTINE.json` está vazio.
