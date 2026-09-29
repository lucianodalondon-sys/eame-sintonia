# R9 — automático × manual (D151/D152, PASSO 1: medir, sem construir)

> Pedido do coordenador (D151/D152): rodar o caminho **oficial automático** — o mesmo que o gatilho chama — sobre
> **exatamente** a Sala da R9 e comparar com os 2 objetos que a R9 liberou. O oráculo (`PARA-O-CASCO-R9/`,
> `montar_r9.py`, `CONTRATO-LIBERACAO-POR-OBJETO-v2.2.md`) só foi **lido**. Nada foi construído, instalado nem agendado.
> Medição: `provas/l2/r9_auto_vs_manual.py` → `provas/l2/R9-AUTO-VS-MANUAL.json`.

## Como foi medido

- **A mesma Sala, byte a byte:** `EXPD78-R9-20260928T155047Z/copia/SALA_ATUAL.json`, sha256 `00cb7cb0…d2`, igual ao que a
  própria R9 registou no `SHA256SUMS.txt`. É o export so-leitura que a R9 fez (`PROVA_RO.txt` = `on` no início e no fim,
  275 linhas). **Não houve Postgres:** a cópia só-leitura da R9 **já é** o export; subir um banco exigiria reconstruir a
  Sala a partir dele, e isso seria menos «a mesma Sala», não mais. A Sala real (54330) não foi tocada.
- O envelope `SALA_ATUAL_READ_ONLY/v1` que o motor pede foi posto **por programa** (CORTE e READ_ONLY lidos do `PROVA_RO.txt`).
- **Caminho oficial** (o do gatilho, `admissao/gatilho_da_inteligencia.py`): `cortar_vigente` → `motor_das_capacidades.rodar`
  (HOJE = 28/09, o dia da R9) → `montar_o_pote` (gerador do dono + ENTITY_SOURCE da lei, D142) → `validar_pote_v2`.

## A tabela

```
OBJETOS_LIBERADOS_MANUAL            = 2
OBJETOS_LIBERADOS_AUTO              = 0
MESMOS_OBJETOS                      = NAO
MESMOS_FACT_TIME                    = NAO   (nenhum objeto automático para comparar; ver 3)
MESMOS_FACT_LOCATION                = NAO   (idem; o sinal do livro diz «Puglia ; Lecce», do documento inteiro)
MESMOS_TRECHOS                      = NAO   (0 provas automáticas com trecho, de 21)
MESMOS_RAW_SHA256                   = NAO   (0 provas automáticas com RAW_SHA256, de 21)
MESMAS_DECISOES_DE_LIBERACAO        = NAO   (o caminho oficial não tem etapa de liberação)
HOUVE_INTERVENCAO_HUMANA_NA_GERACAO = NAO   (no automático; na R9 manual, SIM — ver 1)
GERADOR_CANONICO                    = FAIL
```

**Causa (medida):** não existe produtor automático de **afirmação + trecho + tempo próprio + lugar próprio** por objeto
(COL-LAW-202 `ARTIFACT → CLAIM`: «Extração de claim é `TARGET`, nunca `CURRENT`», `IT = ABSENT`,
`BIBLIA-CANONICA-DA-COLETA.md:1804-1823`). A hipótese do coordenador **confirma-se**.

## O que o automático fez sobre a mesma Sala (medido)

| | valor |
|---|---|
| corte vigente | 275 → **269** linhas: `derived:6/56/57/60/62/66` repetidos (fica o pouso mais recente; as 6 de fora declaradas) — os mesmos 6 que o coordenador mediu |
| motor oficial | corrida `IR-5b31893628a09b10b232`, `DONE`; objetos: windows **0**, science 0, future 9, sources 6; 21 sinais no livro; 0 relações D112 |
| sobre o N38 (`derived:11`) | 1 **sinal** no livro: `FACT_TIME 2026-09-07/2026-09-13`, base **`RELATIVA_A_PUBLICACAO`**, `FACT_LOCATION «Puglia ; Lecce»` — documento inteiro. O motor não o manda ao pote (os sinais ficam no livro: `motor/motor_das_capacidades.py`, `"SIGNALS": []` na saída). Objetos do N38 no pote: 1 `future` («5-7 ottobre 2026», lugar NÃO SEI) e 3 `sources` |
| pote oficial | future 9 + sources 6; **15 violações**, todas `ENTITY_SOURCE esconde a ignorancia` (o mapa do motor vira UNKNOWN pela D142, e o fiscal só aceita «NAO SEI» como ignorância); **0** campos de liberação; **0/21** provas com `RAW_SHA256`; **0/21** com trecho |

## Cada diferença — de quem é o erro

| # | diferença | veredito | onde |
|---|---|---|---|
| 1 | Os 2 objetos da R9 existem porque as **afirmações, os trechos, a data, o lugar e o FACT_TIME foram escritos à mão** no script | **o automático está incompleto** (falta a etapa ARTIFACT→CLAIM, que é da Collection); a R9 manual **não é reproduzível** por programa | `montar_r9.py:107-135` (`AFIRMACOES = [...]`, 8 literais: `AFIRMACAO`, `DATA`, `LUGAR`, `FACT_TIME`, `FACT_LOCATION`) · `BIBLIA-CANONICA-DA-COLETA.md:1804-1823` |
| 2 | O sinal automático do N38 tem a mesma data (`2026-09-07/2026-09-13`) mas base `RELATIVA_A_PUBLICACAO` e lugar do documento inteiro → falha C2/C3 | **o automático está certo em não liberar**; a própria R9 marcou este sinal (`SG-a5d48c8cb6f73f24`) como não liberável pelo mesmo motivo | `montar_r9.py:227-252` (`objetos_do_motor`: C2 e C3 «FALHOU: … documento inteiro») · `MANIFESTO-R9.json` `CONFERENCIAS` |
| 3 | FACT_TIME/FACT_LOCATION dos 2 objetos: a R9 põe-nos em `FORA_DO_CONTRATO` e deixa `CROP_ID/REGION_ID/ISSUE_ID` em NÃO SEI | **contrato ambíguo**: `windows` não tem chave de lugar/tempo do fato no contrato (`DATE_OR_STAGE` recebe o período) | `pacote/ponte_intelligence_casco.py:100-102` (chaves de `windows`) · `POTE-R9-PARA_CLIENTE.json` |
| 4 | `RAW_SHA256` e `RAW_STORAGE_PATH` nas provas: a R9 acrescenta-os **depois** do gerador | **o automático está incompleto**: o export do motor não os lê e o gerador do dono não os carrega | `motor/r7_export_da_copia.sql` (só `source_url`, `document_key`, `document_key_basis`) · `montar_r9.py:13-14` («o gerador do dono ainda NAO carrega estes campos») e `:307-308` |
| 5 | `LIBERACAO` e `CONFERENCIA_DE_LIBERACAO` (C1–C8) | **o automático não tem a etapa**, e o **contrato v2.2 vive fora do repositório** (só em `PARA-O-CASCO-R9/`); C8 é uma decisão do dono **escrita à mão** como frase | `montar_r9.py:175-224` (`conferencia`), `:36-40` (`C8_N38`, `C8_MYFRUIT`) · `CONTRATO-LIBERACAO-POR-OBJETO-v2.2.md` (não versionado) |
| 6 | `ENTITY_SOURCE = "TRECHO_DA_AFIRMACAO"` nos 2 objetos da R9 | **a R9 manual está errada** diante da D142: não é valor da lei COL-LAW-221 (`SPAN · PARAGRAPH_CONTEXT · SECTION_TITLE · DOCUMENT_TITLE · UNKNOWN`); pela decisão do owner viraria UNKNOWN — e aí o fiscal de hoje reprova | `montar_r9.py:157` · `leis/afirmacao_da_fonte.py:41-42` · `pacote/pote_intelligence_casco.py:825-827` |
| 7 | A R9 correu **outro motor**: G0/v4 do ramo `int-intake-g0v4-v1` @ `a5db06c4`, não o da produção | **não é o caminho oficial desta árvore**: o motor da produção (`motor_das_capacidades`) dá outros objetos (21 sinais iguais em número; 0 windows) | `montar_r9.py:259` (`SOURCE_HEAD.MOTOR`) · LIVRO R9 `CODE_VERSION 2505b66cae899638` |
| 8 | Conflito de leis no pote: a D142 manda `UNKNOWN`; `conferir_pote` só aceita ignorância escrita «NAO SEI» | **contrato ambíguo** (duas leis no mesmo campo). Não contornei: o fiscal não foi mudado. Decisão do dono do pote | `pacote/pote_intelligence_casco.py:825-827` · `admissao/gatilho_da_inteligencia.py::montar_o_pote` |

## O MENOR PASSO no caminho existente da Collection (proposta — NÃO implementado)

Fronteira decidida (adendo D152): quem produz o claim é a **Collection** (COL-LAW-201/202; INT-LAW-030/031). O que já
existe e serve, medido:

- `leis/boletim_do_campo.py:545` **`ler_afirmacao(texto, inicio, fim)`** — já lê, para UM trecho, praga, cultura e lugar,
  cada um com a procedência (trava COL-LAW-221 em `_trava_da_entidade`, `:525`; trava COL-LAW-032 em `_trava_do_lugar`,
  `:535`). **Falta-lhe quem lhe dê o `inicio/fim`**: hoje só o gabarito (`scripts/lugar_fato/gold_puglia.py:179`, à mão).
- `leis/boletim_do_campo.py:354` `secoes_territoriais(texto)` — já divide o boletim em secções.
- `leis/fato_do_texto.py:849` `_periodo_do_cabecalho` — lê um período de boletim, **mas só nas primeiras linhas do
  documento** e só com o **nome do mês** (`_RE_PERIODO_DO_CABECALHO`, `:845-846`: «dal 7 al 13 settembre 2026»). O
  cabeçalho da secção do N38 é **numérico e com letras dobradas** no texto da Sala
  («SSIITTUUAAZZIIOONNEE PPRREECCEEDDEENNTTEE DDaall 0077--0099--22002266 …»); a forma normal que a R9 usa
  («SITUAZIONE PRECEDENTE Dal 07-09-2026 al 13-09-2026») foi **escrita à mão** (`montar_r9.py`, `CAB_NORMAL`).
  **Não existe** no repo quem desfaça as letras dobradas nem quem leia a data numérica da secção (medi: `_dobrar`,
  `leis/boletim_do_campo.py:127`, só tira acentos e põe minúsculas).

**O menor passo:** uma função na Collection, em `leis/boletim_do_campo.py`, `afirmacoes_do_boletim(texto, titulo)`, que
(1) percorre as secções que o próprio ficheiro já acha; (2) parte cada secção em frases por regra (há `_frases` em
`leis/fato_local.py`); (3) chama `ler_afirmacao` em cada frase; (4) lê o período **da secção** — a regra de
`_periodo_do_cabecalho` estendida ao início da secção, à data numérica «dd-mm-aaaa» e ao cabeçalho de letras dobradas
(as duas últimas **não existem** hoje: são a parte nova, por regra); (5) só devolve a afirmação
com **data e lugar próprios na mesma secção** (C2/C3 por regra), senão NÃO SEI. Nenhum trecho da R9 fixo: a prova seria
o oráculo — a função tem de reencontrar, sozinha, os 2 trechos do N38 e **não** liberar o sinal de documento inteiro.
Onde o claim mora depois (Sala? tabela nova? migration?) é decisão do dono da Sala; não proponho coluna.

## O que isto NÃO diz

- Não diz que a R9 está errada nos factos: os 2 trechos existem literalmente no texto do N38 (o oráculo confere-os).
- Não diz que a mesma medição daria 0 com o motor `a5db06c4`: a R9 com esse motor também deu 0 automáticos (os 2 são
  manuais); não corri esse motor aqui.
- `OBJETOS_LIBERADOS_AUTO = 0` é resultado válido, com causa medida — não foi forçada igualdade.

FIM
