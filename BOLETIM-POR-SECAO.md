# BOLETIM-POR-SECAO — D18/D19 (Intelligence R6) + D112 do dono

Missão `nuvem-boletim-por-secao-v1`. Código no extrator canônico que já existia
(`leis/boletim_do_campo.py`, lido pela porta em `admissao.janela_declarada`), **sem segundo extrator**.
As Bíblias não foram editadas; o gold e o ESPERADO não foram editados.

## O defeito

- **D18** — cultura, praga e lugar saíam **por documento**. Medido na base: no A.P.OL. n.9 a lista de pragas
  do documento inteiro era `cercosporiosi, cocciniglia, lebbra, mosca dell'olivo, occhio di pavone, xylella`
  (o anexo do Disciplinare entrava junto) e nenhum trecho sabia de que comprensorio era.
- **D19** — reproduzido na base com a notícia SINTÉTICA da Xylella: `fact_location = «Matera ; Basilicata»` e
  cultura da chave `nocciolo`, as duas vindas da manchete vizinha («Ultime notizie»), nunca da notícia.

## O que foi feito

| peça | onde |
|---|---|
| vocabulário do gold (margaronia, prays/tignola delle olive, oziorrinco, rogna) | `leis/boletim_do_campo.py:62-66`, `:103-105` |
| `ler_boletim` tira a barra lateral antes e diz os `TERRITORIOS` | `leis/boletim_do_campo.py:164`, `:221-224` |
| as fontes: `ENTITY_SOURCE` e `LOCATION_SOURCE` (vocabulário fechado) | `leis/boletim_do_campo.py:259-264` |
| cabeçalho territorial **escrito no texto** (`COMPRENSORIO - BR - …`, nome partido em 2 linhas, exclusão «ESCLUSO» não resolve, rodapé/página fecha a seção) | `leis/boletim_do_campo.py:268`, `:310-356` |
| título do documento (o dado + a linha repetida no topo de cada página) | `leis/boletim_do_campo.py:359` |
| janela do parágrafo: frase anterior + começo da própria, cortada por rótulo («Programma di Difesa:»), marcador ou linha em branco | `leis/boletim_do_campo.py:401` |
| título da seção: «• Mosca delle olive (…)», linha de cultura | `leis/boletim_do_campo.py:419` |
| a escada SPAN → SECTION_TITLE → DOCUMENT_TITLE → PARAGRAPH_CONTEXT → UNKNOWN; concorrente e troca de seção = UNKNOWN | `leis/boletim_do_campo.py:447` |
| lugar no trecho (zona/fascia + gazetteer); expressão sem nome = UNRESOLVED, sem ponto | `leis/boletim_do_campo.py:477` |
| `ler_afirmacao`: cabeçalho só na imagem = `VISUAL_HEADER_CANDIDATE`, **nunca** FACT_LOCATION | `leis/boletim_do_campo.py:500-563` |
| `aplicacoes_territoriais`: mesma frase em N seções = N aplicações, 1 instituição | `leis/boletim_do_campo.py:572` |
| D19: `vizinhos`/`sem_vizinhos` (menu, bloco «Ultime notizie/Leggi anche…», rótulo em linha), mesmo comprimento | `leis/fato_do_texto.py:89-151` |
| D19 aplicado em `titulo()` e `corpo()` | `leis/fato_do_texto.py:182`, `:199` |
| D19 aplicado na chave de cultura da porta | `admissao/admissao.py:2063-2071` |

**Limite declarado (D19):** manchete vizinha **sem** rótulo nem menu não se distingue, só pelo texto, de um
intertítulo da própria notícia — essa fica, e a proveniência (SPAN/PARAGRAPH_CONTEXT/…) continua a dizê-lo.

## O gold — quanto passa antes e depois

`scripts/lugar_fato/medir_gold_puglia.py` → `scripts/lugar_fato/MEDIDA-GOLD-PUGLIA-V1.json`. O mesmo harness
(`scripts/lugar_fato/gold_puglia.py`) nos dois lados; antes = `leis/` da base `8a0727e` lido por documento.

| | antes (base 8a0727e) | depois |
|---|---|---|
| casos PASS | **0 / 9** | **9 / 9** |
| chaves PASS | 10 / 34 | **34 / 34** |
| casos NÃO MEDIDOS | 1 (C10) | 1 (C10) |

- Só as chaves que **este** extrator produz são comparadas (lugar, praga, cultura, a fonte de cada uma,
  aplicações). CLASSE, FACT_TIME, PUBLISHED_AT, fidelidade da tradução, RELATION/CONTRADICTION = 20 chaves
  **FORA_DESTE_EXTRATOR** (outros donos) — não contam nem como passe nem como falha. Por isso o C10
  (só relação entre fichas) fica NÃO MEDIDO.
- C07 `APLICACOES_TERRITORIAIS=3 / INSTITUICOES=1`: o A.P.OL. **n.10 não está no repo** (só 400 letras de
  contexto) → NÃO MEDIDO no gold. Medido no boletim irmão **real** A.P.OL. n.9 (mesmo parágrafo nos 3
  comprensori): 3 aplicações, 1 instituição — teste `test_real_mesma_frase_em_tres_secoes_…`.
- Texto de cada ficha: o derivado real do repo quando o trecho aparece lá com o contexto inteiro (C03, C08,
  C09 ×2, C10 SA-28); senão reconstruído do próprio gold (contexto + o cabeçalho que a ficha cita). Declarado
  no harness, igual nos dois lados.

## Testes

`tests/test_boletim_por_secao.py` — 36 testes (gold, A.P.OL. n.9 real, SINTÉTICAS incl. Xylella).

Bateria inteira por nome (`provas/integra_noite/bateria_inteira_por_nome.py`), base × ramo:
_(preenchido abaixo)_

## Mutação

`scripts/lugar_fato/mutar_boletim_por_secao.py` → `MUTACAO-BOLETIM-POR-SECAO-V1.json`: **21 / 21 mortos**
(seção do documento, cabeçalho visual vira fato, sem corte de seção, sem concorrente, parágrafo inteiro, só a
1.ª praga, expressão sem nome vira ponto, exclusão resolve, título vence o trecho, documento vence a seção,
rodapé não fecha, cabeçalho partido, repetição conta instituições, as 4 barras laterais, sem margaronia,
oliveto concorre com olivo, sem janela do parágrafo).

## EM PALAVRAS SIMPLES

Um boletim regional é um caderno com várias páginas, e cada página fala de um lugar e às vezes de uma praga
diferente. Antes, o sistema lia o caderno inteiro e colava em cada frase **tudo** o que o caderno dizia. Agora
cada frase olha só para a **sua** página: se o nome da praga está na frase, diz «estava na frase»; se veio do
título, diz «veio do título»; se o lugar só aparece no desenho da página (e não no texto), fica como
**candidato** e nunca vira lugar do fato. E o que está na barra do lado da notícia (as manchetes de outras
notícias) é apagado antes de ler.
