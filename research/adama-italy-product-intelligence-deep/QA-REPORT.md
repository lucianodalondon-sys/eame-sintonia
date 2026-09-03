# QA REPORT — ADAMA ITALY PRODUCT INTELLIGENCE (rodada 3)

**Data:** 2026-09-02 · **Semente:** 20260902 (reproduzível)

**Método:** cada checagem reabre a **fonte bruta** — o CSV do Ministero, o censo do catálogo,
a tabela FRAC e o Anexo do 540/2011 — e tenta derrubar o registro publicado.

---
## Resultado

| | |
|---|---:|
| QA_SAMPLE_SIZE | 49 |
| QA_PASS | 46 |
| QA_CORRECTED | 2 |
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
| CORRECAO_DO_BASELINE | 2 | 0 |

---
## As duas correções registradas

Reportar `QA_CORRECTED = 0` tendo corrigido defeito de substância seria esconder a falha.

### separador de mistura em sostanze_attive

- a missao anterior dividia a mistura por '+', mas o registro separa por '|' e nunca por '+' — 148 dos 602 registros ADAMA tem mistura
- consequencia: NENHUMA mistura foi separada, e cada uma virou um MoA artificial, o oposto da regra declarada
- corrigido em scripts/adama_it_intelligence.py (_componentes); as substancias ativas cairam de 169 falsas para 122 reais
- o defeito passou pelo QA anterior porque nenhuma checagem olhava separacao de mistura; a checagem agora existe e faz parte da amostra

### Powerfilm — numero de registro publicado contradito

- a pagina da ADAMA publica 'Numero di registrazione n° 17052', que no registro e o COCTEL GOLD da LAINCO S.A., glifosato + MCPA
- a mesma pagina declara oleo de colza metilestere — nome E composicao discordam do registro apontado ao mesmo tempo
- existe POWERFILM registrado 017852 em nome da ADAMA ITALIA com PLANT OILS / RAPE SEED OIL: um digito trocado, 17852 -> 17052
- a rodada anterior aceitou o numero publicado sem conferir e criou do nada um setimo 'produto de outro titular'. Sao SEIS, e o V2.1 ja tinha seis — quem estava errado era eu
- corrigido com regra, nao a mao: quando nome e composicao discordam juntos do registro apontado, o numero publicado cede e o desempate e o nome exato unico no registro inteiro

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

---
## Sem revisão, e por quê

- **ROTULOS_MULTI_CULTURA** — nenhum uso de rotulo foi extraido: 7 rotas de recuperacao tentadas, 0 documentos recuperados — ver RECOVERY em LABEL-MANIFEST.json

## Portão de segurança (§21)

- **48** registros são `QA_PASS` ou `QA_CORRECTED`.
- **0** pares de uso de rótulo novos foram criados neste pacote. Os 2.030 que o V2.1 já tinha,
  lidos dos rótulos ministeriais, seguem intactos e não foram rebaixados.
- `QUARANTINE.json` está vazio.
