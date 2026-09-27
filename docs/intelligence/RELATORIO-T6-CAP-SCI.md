# PRÉ-MEDIÇÃO CAP-SCI — 432 TRABALHOS T6 (vite) · EXPERIMENTAL / NAO_PARA_CLIENTE

```text
NATUREZA   DATA DEMAND sobre material FORA da Sala. NÃO é INTELLIGENCE_RUN (INT-LAW-010):
           nenhum sinal, achado, oportunidade ou juízo de força de evidência sai daqui.
ENTRADA    pesquisadores-t6/rede/UNIDADES-T6.json  sha256 3279488ad881acb0…
REFERÊNCIA referencia/adama (ENTRADA B, só leitura) @ int-consertos-v1 c2059e3b
SCRIPT     pre_medicao_cap_sci.py  →  PRE-MEDICAO-CAP-SCI.json
DATA_EXISTS SIM · DATA_QUERIED SIM · DATA_CAN_JOIN PARCIAL · DATA_SUPPORTS_ANALYSIS NÃO (não admitido)
```

## 1 · As chaves da CAP-SCI (Bíblia V0.3 §34), campo a campo

| chave | tem | de 432 | nota |
|---|---|---|---|
| DOI | 429 | 99% | 3 «NAO SEI» |
| TRIAL_ID | **0** | 0% | nenhum ensaio identificado |
| DATASET_ID | 10 | 2% | |
| RESEARCHER_ID (ORCID provado no depósito) | 130 obras | 30% | 297 obras só com autores «SO_INDICE» |
| INSTITUTION_ID (ROR) | 432 | 100% | é a **afiliação**, não o local do estudo |
| CROP_ID | 413 | 96% | vite 413; pomodoro/melo marginais |
| ISSUE_ID | 402 | 93% | |
| MOLECULE | **11** | 3% | léxico = só os 122 ativos ADAMA |
| LOCAL DO ESTUDO escrito | 95 | 22% | 47 com região; **337 só têm afiliação italiana** (INT-LAW-102: não conta) |
| PERÍODO DO ESTUDO | 35 | 8% | publicação ≠ tempo do estudo |
| cultura + problema juntos | 393 | 91% | |
| cultura + problema + local + período | **22** | 5% | |

## 2 · Mesma obra e independência

- INT-LAW-072: 432 unidades dão **413 obras**, porque os 18 grupos «provável mesma obra» do dono fundem preprint e versão final.
- INT-LAW-073/075: **grupos de autoria** por par. Duas obras que partilham um autor ficam no mesmo grupo. É um **limite superior** de independência, e não a prova dela.

| par | obras | grupos de autoria (teto) | com local do estudo | com período | com molécula |
|---|---|---|---|---|---|
| vite × peronospora | 162 | **31** | 25 | 13 | 7 |
| vite × scafoideo | 99 | **19** | 36 | 11 | 2 |
| vite × botrite | 76 | **28** | 17 | 4 | 3 |
| vite × oidio | 65 | **24** | 19 | 6 | 0 |
| vite × tignoletta | 25 | **10** | 8 | 2 | 0 |

Os 162 trabalhos sobre peronospora são, no máximo, 31 equipas.

## 3 · O que a CAP-SCI conseguiria cruzar (CAN_FEED CAP-LABEL: obra × rótulo ADAMA)

17 tentativas com as 11 obras que nomeiam uma molécula.

| estado | n | exemplo |
|---|---|---|
| **PARTIAL** (molécula, cultura e alvo casam um rótulo ADAMA ativo; falta local e/ou período) | 4 | folpet, metalaxyl-M → FOLPAN GOLD e SESTO GOLD; cymoxanil → ANTERLEX, BADGER, CARSON, DAUPHIN, MOXYL MK e VANTEX; fosetyl-Al → MOMENTUM PFNPE; tudo em vite × peronospora |
| RELAÇÃO PROVADA SEM RÓTULO | 6 | fludioxonil em vite × botrite: a ADAMA tem a molécula mas não tem rótulo na vite |
| **UNKNOWN — referência incompleta** | 7 | deltamethrin (scafoideo), hidróxido e oxicloreto de cobre, metalaxyl |
| CANDIDATE (todas as chaves) | **0** | |

- **Defeito novo na referência (dono `referencia/`):** `ACTIVE-INGREDIENTS` tem 122 ativos, mas `PRODUCT-ACTIVE-INGREDIENTS` liga produto a **só 53**. Deltamethrin conta 19 registos na Itália e não está ligada a nenhum produto. A Intelligence **não pode** concluir «ADAMA não tem». Fica NAO SEI.
- **Ao nível do par** (sem molécula na obra), o portfólio ADAMA ativo tem rótulo para:
  - vite × peronospora: 12 produtos;
  - vite × scafoideo: 6;
  - vite × botrite: 3;
  - vite × oidio: 2;
  - vite × tignoletta: 5, mas só como **grupo** (TIGNOLE).

  Isto diz apenas «há ciência e há rótulo no mesmo tema». **Não** é crossing: falta a molécula do lado da obra (INT-LAW-037).

## 4 · Com a Sala: NOT_POSSIBLE

- Nenhum dos 429 DOI aparece nos 94 itens da Sala.
- A Sala tem CROP_ID vazio.
- Mesmo com chave, ciência **não vira** incidência de campo.

## 5 · O que falta (para a Coleta)

1. **Admitir na Sala** (INT-LAW-010). Sem isso a Intelligence não produz nada com estes trabalhos.
2. Molécula como campo com léxico **completo**, e não só os 122 ativos ADAMA. Hoje 421/432 dizem NAO SEI, o que impede ver concorrentes na ciência.
3. **Local do estudo** e **período do estudo**, lidos do método ou do resumo. Hoje 22% e 8%.
4. TRIAL_ID: 0. Sem ele, três papers do mesmo ensaio parecem três evidências (MUST_NOT_DO da CAP-SCI).
5. Resultado e direção (eficácia, resistência). Não existe campo para isso. Sem ele não há força de evidência nem contradição.
6. Para `referencia/`: ligar os 69 ativos com registo a produtos, ou declarar porque não estão ligados (revogados?).
