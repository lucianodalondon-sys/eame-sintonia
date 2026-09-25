# Plano — os boletins READY_LEGACY (Campania-Salerno IT-T3-002, APOL IT-T3-010, ARPAV IT-T2-002)

**Só plano.** O desenho mínimo não cabe neste ramo sem mexer no canário e na régua de promoção. O porquê está abaixo.

## Em palavras simples

- Os 3 boletins são **PDF**.
- A régua de promoção de hoje só sabe aprovar uma **página HTML** com corpo. O passo «corpo útil» exige `HTML_KIND == CONTENT` (`curadoria/ready_split.py:133-134`), e o canário do Curator não abre PDF (`curadoria/canario.py`: nenhuma linha trata PDF).
- Por isso, **mesmo que o Curator aprenda o contrato**, um boletim PDF nunca passaria a régua atual. Ficaria outra vez em CONTRACTED_CANARY_FAILED.
- **Faltam duas coisas, e são as duas precisas:**
  1. o Curator aprender o contrato que já existe no coletor;
  2. a régua saber dizer «este PDF tem corpo».

## O que já se sabe (medido no MICRO-PRONTO, cópia do vivo)

- `ready_split.remedir` → VALIDATE_ROUTE **BLOCK «sem contrato»** (`worker.py:93` só lê `italy_contracts_curator.json`).
- REPAIR_CONTRACT → **FAIL `SEM_IDENTIDADE`** (`worker.py:494-498`): sem contrato do Curator e sem alocação HTML.
- O contrato destes 3 vive só como `case` em `coleta/italy_pilot_collect.mjs` (`alvosDe`), sem `ACQUISITION` declarativa.
- A 25/09 os índices tinham edição nova, nunca vista pelo livro: SA-23-09 (Campania) e Mosca n.º 11 de 21/09 (APOL). Para a ARPAV a data não se lê (JavaScript).

## Passos propostos (por ordem; cada um com teste e mutação, como a PONTE-ONBOARD)

1. **Declarar os 3 `case` como contrato** em `regras/italy_contracts_onboarded.json`, e só lá (o dono continua a ser `italy_contracts.mjs`):
   - IT-T3-002 e IT-T3-010 → `HTML_LINK_DISCOVERY`, `MATCH: HTML`, o mesmo padrão do `case` e `MAX_TARGETS: 1`. Já provado como medida em `rendimento-fontes-v1: ferramentas/rendimento/medidas/boletins-contratos.json`.
   - IT-T2-002 → `TEMPLATE_ENUMERATION` com `{ZONA}` ENUM 01, 09, 16 e 24.

   Critério: o motor de rota dá **os mesmos endereços** que o `case` sobre a mesma capa (teste de paridade, sem rede). Só depois o `case` sai do `switch`.
2. **Importar para o Curator como candidata com prova.** Um passo `IMPORTAR_DO_COLETOR` escreve, em `italy_contracts_curator.json`, a mesma `ACQUISITION` da tabela do coletor, com `ONBOARDED_BY: importado do coletor` e a impressão `sha_do_contrato`. Não promove nada; põe a fonte em CANARY_PENDING pelo `ready_split.remedir` que já existe. A ponte de volta usa a mesma impressão da PONTE-ONBOARD: o que se importa é o que o coletor executa.
3. **Ramo PDF no canário do Curator e na régua dos 4 passos.**
   - `ITEM_ABERTO` = bytes com assinatura `%PDF` (a lei `EXPECTED_SIGNATURE` do coletor);
   - `BODY_UTIL` = texto extraído (`pdftotext`, que o coletor já usa) com N caracteres úteis e a data de emissão legível.

   É uma **decisão de régua** (quanto texto chega), e é do coordenador. Proposta: o mesmo limiar de caracteres em parágrafos do HTML.
4. **Revalidar pelas regras atuais, no vivo, pelo caminho canónico:** `ready_split.remedir` → VALIDATE_ROUTE → CANARY → promoção. Com os passos 1-3 instalados, deixa de parar em «sem contrato». Ensaio primeiro numa cópia, como nesta missão.

## Risco a declarar

- O passo 3 muda a régua de promoção para **todas** as fontes PDF, não só estas 3. Precisa da bateria da régua (`test_ready_split*`, `test_worker*`) antes e depois.
- A ARPAV é MUTABLE (o mesmo endereço muda de conteúdo). A régua tem de aceitar «mesmo endereço, edição nova» sem a confundir com a nossa pegada (ver `provas/a_mudanca_e_nossa_pegada.py`).

## Tamanho estimado

Passos 1-2: pequenos (1 ficheiro novo, 1 teste de paridade, 1 de importação). Passo 3: médio (canário + régua + bateria). Passo 4: operação.
