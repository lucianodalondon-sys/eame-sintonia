# DERIVACAO-ESTRUTURA — o elo 3 do canário 1149 (B1 + B2)

MISSÃO `nuvem-derivacao-estrutura-v1` · 28/09/2026 (D131) · ramo `claude/derivacao-estrutura-v1-girw5u`
· base `servico-20260923-0923 @ e24139702` (o vivo) · **nada fundido, nada instalado, produção/Sala/coleta/VPN intocadas.**

Insumos lidos em `origin/nuvem/canario-1149-v1:docs/lab-insumos/canario-1149/`: o MAPA DE RESPONSABILIDADE (primeiro
vermelho = elo 3), o parecer do SCRAP ENGINEER (`resp-scrap-1149-derivacao.txt`, que especificou) e o RAW real
(`RAW-2272.html`, sha256 `f2158520f2362956…`, copiado byte a byte para `tests/fixtures/canario_1149/`).

---

## ESTADO

| | |
|---|---|
| B1 · `limpar()` preserva blocos | **FEITO** — `coleta/texto_fonte.py`: etiquetas de BLOCO → `\n`, inline → `' '` como antes. Mesma função, sem biblioteca nova, sem segundo extrator. |
| B1 · régua na receita + versão | **FEITO** — `EXECUTOR_VERSION` 2 → **3**; `receita()` ganha `TEXT_RULE` + `TEXT_RULE_PROBE_SHA256`; `test_a_receita_tem_versao` reprova `limpar()` mudada sem versão (mutação provada). |
| B2 · PUBLISHED_AT estreito | **FEITO** — nível `DIV.content-date (irmão de content-category)`, só depois dos cinco da D61, data italiana `DD mmm AAAA`, PRECISAO = DIA, nunca FACT_TIME. |
| RAW 2272 | 1 → **80** linhas · corpo() vivo 0 → **7 705** car. · PUBLISHED_AT NAO SEI → **2026-06-22 DIA** — os três números do parecer, batidos. |
| Bateria por nome | __BATERIA__ |
| Mutação | **8/8 mortos**, cada um no teste esperado; originais repostos. |
| Replay do acervo (463) | **script entregue, NÃO corrido aqui** (o armazém real não está na nuvem). Corrido sobre os 216 HTML versionados na árvore: controlo negativo PASSA. |
| System Map | regerado pela cadeia; `VALIDAR` __VALIDAR__; carimbo __CARIMBO__ |
| Fora do escopo | não tocados: `admissao/`, `leis/fato_do_texto.py` (`corpo()`), `leis/boletim_do_campo.py`, gazetteer, PROBLEMA/v1, claim/ontologia, Intelligence, pote, casco. Nada reaproveitado de `claude/canario-1149-first-review-3llkwl`. |

---

## O QUE MUDOU (e só isto)

**`coleta/texto_fonte.py`**
- `BLOCOS` (as 31 etiquetas da ordem: `p div li h1–h6 br tr td th section article header footer nav aside blockquote pre
  ul ol table dd dt figure figcaption main form hr`) e `_RE_BLOCO = </?(?:…)\b[^>]*>` → `'\n'`, **antes** da passagem que
  troca o resto por espaço. `\b` impede `<pre>`→`p`, `<thead>`→`th`, `<param>`→`p`. As linhas vazias repetidas já colapsavam
  (`\n\s*\n+` + filtro de linha vazia) — ficou igual.
- `REGUA` (nome), `SONDA` (HTML fixo que exercita cada bloco, inline, script/style, comentário, entidades, `&nbsp;`,
  maiúsculas, atributos, linhas vazias) e `impressao_da_regua()` = sha256 do que `limpar()` devolve para a sonda.

**`coleta/executor_texto_de_html.py`**
- `EXECUTOR_VERSION = "3"`; `receita()` += `TEXT_RULE`, `TEXT_RULE_PROBE_SHA256`.
- `BASE_CONTENT_DATE`, `ORDEM_COMPLETA = ORDEM_DA_PUBLICACAO + (BASE_CONTENT_DATE,)`, `MESES_IT` (12 meses: abreviados,
  com ou sem ponto, e por extenso), `normalizar_data_italiana()`, `_campos_content_date()` (lê a árvore de `div` com
  `html.parser` da biblioteca padrão) e o nível no fim de `tempo_de_publicacao()`. **O laço dos cinco níveis não mudou
  uma linha** (`git diff` mostra só acréscimos, mais a linha da versão).

**Provas**: `tests/test_derivacao_estrutura.py` (36 testes), `tests/test_a_receita_tem_versao.py` (+2),
`provas/derivacao_estrutura/{mutar.py, replay_acervo.py}`, `tests/fixtures/canario_1149/RAW-2272.html` (+ `.gitattributes`
`-text -diff`, para o Windows não lhe meter CRLF). Mapa: 3 ficheiros novos declarados em `C-EXECUTOR-TEXTO-HTML`.

### Onde me afastei do parecer (medido e explicado)

1. **A régua entra na receita por COMPORTAMENTO, não por código.** O parecer deixou em aberto «se a versão da régua entra
   na receita»; a ordem da missão fechou que entra. Pôr o sha do código-fonte faria um comentário mudar a identidade de
   todos os derivados; pôr só um nome (`TEXT_RULE`) deixaria passar quem muda `limpar()` e esquece o nome. A impressão da
   SONDA faz as duas coisas: comportamento mudado → receita mudada → teste vermelho até a versão subir; comentário mexido →
   nada. Limite honesto: uma mudança que não toque em nada que a sonda exercite escapa — por isso a sonda cobre as 31
   etiquetas e cada passo de `limpar()`.
2. **`ORDEM_DA_PUBLICACAO` ficou com os cinco da D61.** Dois testes existentes afirmam essa tupla exata
   (`test_leitor_data_youtube`, `test_tempo_e_lugar_da_publicacao`). O nível novo não é da D61: vive em `ORDEM_COMPLETA` e é
   lido **depois** do laço — não se editou teste nenhum para caber.
3. **«Mais de um campo» = NAO SEI mesmo com valores iguais** (a ordem diz «mais de um campo»; os níveis da D61 aceitam
   duplicados iguais). O parecer mediu 0 páginas com mais de um — custo zero no acervo medido.
4. **`td`/`th` → `\n`** como a ordem manda. Medi a alternativa (`td`/`th` → espaço, `tr` → `\n`, linha = linha da tabela)
   nos 216 HTML da árvore: só 8 têm `<td>`, e o `corpo()` difere em 3 (IT-T10-022, ±61 car.). Não há ganho medido que
   justifique desobedecer; fica registado para quando houver leitor de tabelas.

---

## EVIDÊNCIA

### 1 · RAW 2272, antes × depois (código REAL de cada árvore; `corpo()` VIVO, não mexido)

```
$ python3 medir2272.py <worktree e24139702> tests/fixtures/canario_1149/RAW-2272.html
__ANTES__

$ python3 medir2272.py <este ramo> tests/fixtures/canario_1149/RAW-2272.html
__DEPOIS__
```

Esperado pelo parecer: 1 → ~80 linhas; corpo 0 → ~7 705; PUBLISHED_AT NAO SEI → 2026-06-22 DIA. **Medido: 1 → 80;
0 → 7 705 (1 045 palavras); 2026-06-22 · DIA · BASE `DIV.content-date (irmão de content-category)`.** O PORQUE guarda os
cinco `ausente` antes do valor. O contrato sai sem nenhuma chave `FACT_*`.

E o limite que o parecer já tinha medido, confirmado: das 23 linhas que o `corpo()` devolve, **11 vêm das l.0-31**
(2 são o título `<title>`/`<h1>`, 9 são menu longo). A derivação devolveu a estrutura; separar menu de corpo é do elo
seguinte, não deste.

### 2 · Testes

**Os que chamam `limpar()` / o executor** (grep por `texto_fonte`, `executor_texto_de_html`, `limpar(`):

```
$ python3 -B -m unittest tests.test_derivacao_estrutura tests.test_a_receita_tem_versao
Ran 42 tests … OK
$ for t in test_a_rota_do_html test_tempo_e_lugar_da_publicacao test_leitor_data_youtube \
           test_c4g_a_especie_do_video test_conserto_regua test_quarentena_naosei; do python3 -B tests/$t.py; done
test_a_rota_do_html ................ Ran 30 tests  OK
test_tempo_e_lugar_da_publicacao ... Ran 42 tests  OK
test_leitor_data_youtube ........... Ran 10 tests  OK (skipped=1)
test_c4g_a_especie_do_video ........ Ran 12 tests  OK
test_conserto_regua ................ Ran 10 tests  OK
test_quarentena_naosei ............. Ran 22 tests  OK
```

**Bateria por NOME, antes × depois** — cada `tests/test_*.py` num processo próprio (`python3 -m unittest -v`), numa
worktree limpa de `e24139702` e noutra do commit deste ramo, comparadas teste a teste:

```
__BATERIA_DETALHE__
```

**Mutação** (`python3 -B provas/derivacao_estrutura/mutar.py` → `provas/derivacao_estrutura/MUTACAO-DERIVACAO-ESTRUTURA.json`):

| mutante | o que faz | vermelho em |
|---|---|---|
| M1_B1_revertido | tira a linha `_RE_BLOCO.sub('\n', t)` (a `limpar()` antiga) | `test_derivacao_estrutura` **e** `test_a_receita_tem_versao` |
| M2_regua_muda_sem_versao | `td`/`th` deixam de ser bloco, versão fica | `test_a_receita_tem_versao` |
| M3_versao_nao_subiu | `EXECUTOR_VERSION = "2"` | `test_a_receita_tem_versao` |
| M4_regua_fora_da_receita | tira `TEXT_RULE_PROBE_SHA256` da receita | `test_a_receita_tem_versao` |
| M5_B2_qualquer_classe_date | aceita qualquer classe com «date» | `test_derivacao_estrutura` |
| M6_B2_sem_irmao_categoria | não exige o irmão `content-category` | `test_derivacao_estrutura` |
| M7_B2_data_em_qualquer_parte_do_valor | `search` sem âncoras (rótulo/evento passam) | `test_derivacao_estrutura` |
| M8_B2_mais_de_um_campo_fica_o_primeiro | ignora a ambiguidade | `test_derivacao_estrutura` |

`"MORTOS": 8, "DE": 8, "ORIGINAIS_REPOSTOS": true`. Todos os mutantes, além de mortos, ficaram vermelhos **no teste
esperado** (`ESPERADOS_CUMPRIDOS: true`). A mutação em memória do M1 também vive dentro do próprio
`test_a_receita_tem_versao::test_mudar_limpar_sem_subir_a_versao_reprova`.

**Conjunto controlado do B2** (`tests/test_derivacao_estrutura.py`): 30 positivos (12 meses × abreviado/ponto/extenso,
maiúsculas, `&nbsp;`, 29 fev bissexto) e 23 venenos de valor, incluídos os do parecer §3 — `2 settimane fa`,
`3 settimane fa`, `Data di aggiornamento…`, `Data di verifica…`, `Data di pubblicazione dell'evento: MERCOLEDÌ…`,
`15/09/2026, 14/09/2026, 24/06/2026`, `6 November 2022`, `27 September 2026`, intervalos, dia da semana à frente, ano de
2 algarismos, `31 feb`. Venenos de ESTRUTURA: sem irmão categoria, categoria sobrinha, fora de `content-metadata`, neta de
`content-metadata`, `event-date`/`date`/`post-date`/`content-date-evento`/`data`/`entry-date`, barra lateral de últimos
artigos, `<span>` em vez de `<div>`, dois campos (iguais e diferentes), dois `content-date` no mesmo metadata. Controlo:
cada um dos cinco níveis da D61 continua a mandar com um `content-date` válido na mesma página.

### 3 · Medidores que chamam `limpar()` / `extrair()` — **A REGERAR NO WINDOWS COM O ACERVO**

Não regerei nenhum JSON: os dados que eles leem (Sala, armazém, coortes) não estão aqui, e um JSON regerado sobre o que
não tenho seria inventado.

| medidor | chama | JSON que fica velho |
|---|---|---|
| `medidas/porque_a_sala_nao_recebeu.py` | `limpar()` | `PORQUE-A-SALA-NAO-RECEBEU-V1.json` |
| `medidas/o_contrato_do_universo.py` | `limpar()` | `O-CONTRATO-DO-UNIVERSO-V1.json` |
| `scripts/lugar_fato/medir_moldura_html.py` | `limpar()` | `MEDIDA-MOLDURA-HTML-V1.json` |
| `scripts/regua_t2/inventariar_t2.py` | `executor.extrair()` | `INVENTARIO.json` / `CATALOGO-PROVA-V1.json` |
| `medidas/gabarito_t2_t12.py` | `executor.extrair()` | `GABARITO-T2-T12-V*.json` |
| `medidas/relevancia_antes_da_coleta.py` | `executor.extrair()` | `RELEVANCIA-ELEGIVEIS-V1.json` / `ROTAS-ELEGIVEIS-V1.json` |

(Os três últimos o parecer não listou; o grep achou-os. `coleta/linha_busca.py` também chama `extrair()` — é produção, e
recebe a mudança por desenho, como a derivação.)

### 4 · Replay offline do acervo — `provas/derivacao_estrutura/replay_acervo.py`

```
py provas/derivacao_estrutura/replay_acervo.py --armazem C:\Users\London1\sintonia-sala-italia\armazem --saida <pasta>
```

- ANTES = `limpar()` do base por **cópia literal marcada** no script, conferida em runtime contra
  `git show e24139702:coleta/texto_fonte.py` (`COPIA_LITERAL_CONFERIDA`); `tempo_de_publicacao()` do base lido de
  `git show e24139702:coleta/executor_texto_de_html.py` para a memória (ou `--executor-base <ficheiro>`; sem nenhum dos dois o
  script PÁRA — não inventa o antes). DEPOIS = esta árvore. `corpo()` = o vivo, nos dois.
- Só leitura: `sys.dont_write_bytecode`, `socket.socket` trocado por uma armadilha antes de qualquer import da casa, e
  a única escrita é `<saida>/REPLAY-DERIVACAO-ESTRUTURA.json`. Sai com código ≠ 0 se o controlo negativo falhar.
- RESUMO: páginas, erros, saem de 1 linha, mediana de linhas, corpo vazio antes/depois, cresce/encolhe/igual, corpo < 20
  palavras depois (lista), `PUBLISHED_AT_MUDA_ENTRE_AS_QUE_RESPONDIAM` (**tem de ser []**), `PUBLISHED_AT_PERDE`
  (**tem de ser []**), `PUBLISHED_AT_GANHA` (lista com o texto do campo), e um alarme para o elo 4:
  `PAGINAS_COM_DATA_EM_PROSA_QUE_SAI_DO_CORPO`.

**Corrido aqui só sobre o que a árvore tem** — os 216 HTML versionados em `data/collection-store/italy/` (não é o armazém;
não há pasta `OBSERVATION/`, por isso `--qualquer-html`). Saída guardada em
`provas/derivacao_estrutura/replay-arvore-216/`:

```
$ python3 -B provas/derivacao_estrutura/replay_acervo.py --armazem data/collection-store/italy \
      --saida provas/derivacao_estrutura/replay-arvore-216 --qualquer-html
COPIA_LITERAL_CONFERIDA: SIM · EXECUTOR_BASE_DE: git show e24139702:coleta/executor_texto_de_html.py · 3.4 s
PAGINAS 216 · ERROS 0
SAEM_DE_1_LINHA 28 (UMA_LINHA_ANTES 28 → DEPOIS 0) · MEDIANA_LINHAS 73 → 106
CORPO_VAZIO 28 → 0 · CRESCE 42 · ENCOLHE 105 · IGUAL 69 · CORPO < 20 PALAVRAS DEPOIS: 0
PUBLISHED_AT_RESPONDIA_ANTES 202 · MUDA_ENTRE_AS_QUE_RESPONDIAM [] · PERDE [] · GANHA [] (nenhum content-date na árvore)
PAGINAS_COM_DATA_EM_PROSA_QUE_SAI_DO_CORPO 33 · QUE_ENTRA 3
CONTROLO_NEGATIVO: PASSA
```

E o mesmo script sobre um armazém de uma página (o RAW 2272 numa pasta `…/OBSERVATION/`): `GANHA = [2026-06-22,
DIV.content-date (irmão de content-category), "22 giu 2026"]`, `CONTROLO_NEGATIVO: PASSA`.

### 5 · System Map

```
__MAPA__
```

### 6 · KNOW-HOW

`docs/sintonia-scrap/KNOW-HOW-DERIVACAO-ESTRUTURA.md` — um parágrafo: «`limpar()` achatava a estrutura; a régua de extração
precisa estar na receita». Está em `docs/sintonia-scrap/` (a capability de parsing é do Scrap Engineer) como
`KNOW_HOW_DELTA`; o livro canónico é `SINTONIA-EAME-KNOW-HOW.md` e o § é o coordenador que numera — numerar aqui
colidiria com as outras linhas.

---

## PROBLEMA

1. **O `corpo()` é filtro POR LINHA, e agora vê linhas de verdade — nos dois sentidos.** Ele deixa de estar cego (28/216
   corpos vazios → 0 na árvore; 75/463 → 0 pelo parecer), mas também **larga linhas curtas que antes viajavam coladas numa
   linha longa**. Medido na árvore: 105/216 corpos encolhem; olhados à mão, a maior parte é menu que sai (Chianti:
   «Territorio Zona di produzione UGA…» desaparece do corpo). Mas **33/216 páginas perdem do corpo uma data em prosa**
   (medido pelo alarme do replay, conferido linha a linha):
   - 30 × IT-T7-042 e 1 × IT-T2-004: a data fica **sozinha numa linha** (110 ocorrências) — datas de lista/cabeçalho de
     tabela que antes iam coladas numa linha longa; não sei, página a página, se alguma era a do artigo;
   - IT-T7-043: a **dataline** «Milano, 15 aprile 2026» (lugar **e** data) vira linha curta e sai do corpo;
   - IT-T7-033: «Wine Paris – 9-11 febbraio 2026» (título de evento) e «… – 26 gennaio 2026.» saem; no Chianti Classico
     Collection saem «16 – 17 Febbraio 2026» / «Stazione Leopolda, Firenze», mas a frase «…il 16 e 17 febbraio presso la
     Stazione Leopolda a Firenze.» fica.

   **O texto derivado continua a ter todas estas linhas** — quem as larga é o filtro por linha do elo 4. Não mexi
   (`corpo()` está fora do escopo); é o primeiro número a olhar no replay de 463.
2. **`C-FONTES-EU` passou de PROVEN a PENDING no mapa** — `coleta/texto_fonte.py` pertence-lhe e mudou depois de declarado.
   É o mapa a dizer a verdade. Não recarimbei: `--stamp` carimba a árvore inteira, e há 129 ficheiros com descrição
   anterior à mudança deles que eu não li — recarimbar seria abençoá-los. (E `texto_fonte.py` a morar em «bases oficiais
   da Europa» em vez de no executor de HTML é um desencontro de gaveta anterior a esta missão; não o mudei — «não amplie».)
3. **Versão 3 = derivados novos.** Toda re-derivação de um RAW HTML passa a escrever uma linha nova `texto-de-html` "3" em
   vez de reencontrar a "2" (é o objectivo: identidades diferentes). A D79 (`versao_do_documento`) re-extrai o RAW anterior
   com o extrator novo antes de comparar — o desenho aguenta, mas não o corri contra a Sala.

## O QUE NÃO SEI

- **Os números das 463 páginas.** O script está entregue; o replay no armazém real é do coordenador, no Windows. Sei que
  na árvore (216) o controlo negativo passa e que 0 páginas ficam com corpo < 20 palavras; **não sei** se as 5 que o parecer
  mediu com corpo < 20 continuam lá, nem se as 15 com `content-date` ganham todas a data (o parecer previu 14 + 1 falso
  positivo que a régua de valor recusa).
- **O efeito na Admissão.** O texto que a porta julga passa a ter `\n` onde tinha espaço. A régua T5 é por substring no
  item inteiro (Defeito A, fora do escopo): uma expressão de duas palavras partida por uma etiqueta de bloco deixa de casar,
  e o contrário não acontece. Não medi decisões de admissão antes × depois.
- **O elo 4 e seguintes do 1149.** Com o corpo a 7 705 car. e a data com base, não sei se o 1149 fica verde no lugar/tempo
  do facto (o parecer e o mapa dizem que o lugar depende do gazetteer — Salento — e o PROBLEMA de B3, ambos fora).
- **O `reprocessar_tempo_lugar`** (`admissao/`) relê a publicação com este executor: se alguém o correr, itens antigos com
  `content-date` ganham PUBLISHED_AT. É o comportamento certo, mas não o corri.
- A sonda cobre o que `limpar()` decide hoje; uma mudança futura em algo que a sonda não exercite escapa ao teste da
  receita. Quem mudar `limpar()` deve estender a SONDA (o comentário dela diz isto).

---

## EM PALAVRAS SIMPLES

1. O leitor de páginas juntava a página inteira numa linha só; agora respeita onde cada parágrafo acaba, e o texto da
   notícia do 1149 aparece (antes 0, agora 7.705 letras).
2. A data «22 giu 2026» passou a ser lida só naquela caixinha ao lado de «COMUNICATO STAMPA», e só se for uma data
   inteira em italiano; qualquer outra coisa continua «NÃO SEI».
3. A «receita» de cada texto agora registra como ele foi lido, então texto velho e texto novo nunca se confundem.
