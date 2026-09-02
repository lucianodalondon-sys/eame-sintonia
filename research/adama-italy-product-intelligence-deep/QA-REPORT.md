# QA REPORT — ADAMA ITALY PRODUCT INTELLIGENCE

**Data:** 2026-09-02 · **Semente da amostra:** 20260902 (reproduzível)

**Método:** cada checagem **reabre a fonte bruta** — o CSV do Ministero e o censo do catálogo — e tenta
derrubar o registro publicado. Um QA que só confere o pacote contra ele mesmo não mede nada: foi o mesmo
código que escreveu os dois lados.

---
## Resultado

| | |
|---|---:|
| QA_SAMPLE_SIZE | 36 |
| QA_PASS | 35 |
| QA_CORRECTED | 0 |
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

## O detector prova que reprova

Taxa de erro zero não vale nada sem isto. Injeção de defeito, QA reexecutado, arquivo restaurado:

- defeitos plantados: **4**
- caíram dentro da amostra sorteada: **3**
- reprovados: **3** — recall **1.0**
- tipos provados: `HOLDER_MISMATCH`, `REGISTRATION_NOT_IN_SOURCE`, `INFERENCE_STRONGER_THAN_SOURCE__MARKETABLE`
- não exercitado por sorteio: `CATEGORY_NOT_THE_PRINTED_ONE — o produto adulterado nao foi sorteado`

## O que ficou sem revisão, e por quê

- **ROTULOS_MULTI_CULTURA** — nenhum uso de rotulo foi extraido: os 51 PDF nao sao alcancaveis deste ambiente

## Portão de segurança para o cliente (§21)

- **35** registros são `QA_PASS` e podem sustentar sozinhos afirmação forte ao cliente.
- Os demais registros do mapa de identidade são `QA_UNREVIEWED`: **pesquisa válida**, mas não sustentam
  sozinhos `VERIFIED MATCH`, `CURRENTLY AUTHORIZED`, `CURRENTLY MARKETED`, `REGULATORY RISK`,
  `OPPORTUNITY` nem `ACT NOW`.
- `QUARANTINE.json` está vazio: nada foi reprovado nesta rodada.
