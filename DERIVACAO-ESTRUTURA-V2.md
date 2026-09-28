# DERIVACAO-ESTRUTURA-V2 — uma etiqueta não atravessa outro «<»

MISSÃO `nuvem-derivacao-estrutura-v2` · 28/09/2026 (D131/D132) · ramo `claude/derivacao-estrutura-v2-d76w9o`,
filho de `origin/claude/derivacao-estrutura-v1-girw5u @ 1aa4beb92` · **nada fundido, nada instalado;
produção/Sala/coleta/VPN intocadas.** Lido antes: `DERIVACAO-ESTRUTURA.md` (v1).

---

## ESTADO

| | |
|---|---|
| Defeito do «</» órfão | **CORRIGIDO** — `coleta/texto_fonte.py::limpar` (mesmo lugar, regra geral, nada de site). |
| Régua | `REGUA` = `limpar/3`; a SONDA passa a ter `</</div>`, `</<b>`, `<!-- <div> -->`, `<!doctype` e `<?` sem fecho, `a < 5 e b >= 2`. |
| Versão | `EXECUTOR_VERSION` 3 → **4**; receita `bb811cae…` registada; `test_a_receita_tem_versao` apanha a volta à régua 2 com a versão 4 (teste novo). |
| Testes | `tests/test_derivacao_estrutura_v2.py` (13) com 2 recortes REAIS do balsâmico; `test_derivacao_estrutura` +0 (1 número ajustado e explicado: RAW 2272 80 → 82 linhas, `corpo()` igual). |
| Mutação | **11/11 mortos**, todos no teste esperado (8 da v1 + 3 novos: M9 duas passagens, M10 etiqueta atravessa «<», M11 órfão fica). |
| Replay | `replay_acervo.py` ganhou a medida de CONTEÚDO (`PALAVRAS_PERDIDAS_DO_TEXTO`, `PAGINAS_COM_PERDA_NO_TEXTO`, `MELHORARAM/IGUAIS/PIORARAM`). Árvore (216): **perda 0**; com a régua 2 no lugar, a mesma medida acha as **6** páginas do balsâmico. **Armazém (536): NÃO corrido aqui** — é do coordenador. |
| Prova «não é regra para a Xylella» | `provas/derivacao_estrutura/nao_e_regra_de_site.py`: 136 linhas de CÓDIGO acrescentadas em `coleta/` desde `e24139702`, **0** citam site/CREA/Xylella/URL/`IT-T…` (as 5 menções estão em comentários que contam de onde veio a medida). |
| System Map | regerado pela cadeia; ver §6. |
| Fora | `corpo()`/`leis/fato_do_texto.py`, `admissao/`, datas do fato, ontologia — não tocados. |

---

## O QUE MUDOU (e só isto)

**`coleta/texto_fonte.py::limpar`** — as duas linhas

```python
t = _RE_BLOCO.sub('\n', t)          # régua 2: 1.ª passagem, bloco -> \n
t = re.sub(r'<[^>]+>', ' ', t)      #          2.ª passagem, o resto -> espaço
```

viraram

```python
t = _RE_ETIQUETA.sub(_etiqueta, t)  # régua 3: UMA passagem; bloco ou inline decidido ali
t = _RE_ORFAO.sub(' ', t)           #          «<» de marcação sem «>» -> espaço
```

com `_RE_ETIQUETA = <!--[^>]*> | <[A-Za-z/!?][^<>]*>`, `_RE_ORFAO = <[/!?][^\s<>]*` e `_RE_BLOCO` agora só
a cabeça `</?(bloco)\b` aplicada à etiqueta já recortada (as mesmas 31 etiquetas de bloco, o mesmo `\b`).

**Porquê assim — decidido medindo** (216 HTML da árvore; `v2` = `limpar()` do vivo `e24139702`, `v3` = régua 2 do
ramo v1; «perde» = palavra de conteúdo ≥4 letras do `corpo()` da v2 que não existe em lugar nenhum do texto novo):

| candidata | difere da v3 | perde (páginas) | texto ≠ v2 a menos de brancos | ruído |
|---|---|---|---|---|
| v3 (régua 2, o defeito) | — | **6** | 8 | — |
| C1 · a sugestão: 2.ª passagem `<[^<>]*>` depois do bloco | 191 | 0 | 191 | 371 linhas com `<` solto (`<!--`, `</`) |
| C3 · uma passagem `<[^<>]+>` + órfão → espaço | 191 | 0 | 191 | 264 linhas `!--`; comentários de programador vazam (1 página: «Logo a home dinamico DISABILITATO») |
| C4 · C3 + comentário inteiro até `-->` (como o navegador) | 162 | **1** | 162 | apaga texto que a `limpar()` sempre mostrou em 71 páginas — outra mudança |
| A · uma passagem, as MESMAS etiquetas da v2 `<[^>]+>` | 92 | 0 | **0** | nenhum — mas a etiqueta ainda atravessa «<» (`</</div>` inteiro) |
| **escolhida** · uma passagem, `<[A-Za-z/!?][^<>]*>`, comentário até ao 1.º «>», órfão → espaço | 92 | **0** | **0** | nenhum além do que a v2 já tinha |

1. **Uma passagem, não duas.** O buraco nasceu da ORDEM: a 1.ª passagem apagava o `</div>` que fechava o «</» órfão.
   Com as duas decisões (bloco/inline) no mesmo passo, não há passagem anterior que abra buraco — por construção uma
   etiqueta também **não atravessa quebra de linha criada por bloco** (a 2.ª metade do item 1 da ordem fica cumprida
   sem regra extra; proibir quebra de linha dentro da etiqueta partiria etiquetas legítimas de várias linhas,
   ex. `<img\r\nsrc=…\r\n/>`, que a página do mixology tem).
2. **A etiqueta não atravessa outro «<»** (`[^<>]`) e começa por letra, `/`, `!` ou `?` (o que o leitor do navegador
   trata como marcação). `a < 5 e b >= 2` era engolido pelas três réguas anteriores; agora é texto. Na árvore: 0
   páginas com isso — custo zero medido, e fecha a mesma classe de buraco.
3. **Exceção medida: o comentário.** Dentro de `<!--` o «<» não abre etiqueta (é conteúdo do comentário), e o
   comentário acaba no 1.º «>», **como sempre acabou**. Tratá-lo até `-->` (C4) é o certo pelo navegador, mas muda o
   texto de 71/216 páginas e tira palavras do `corpo()` de 1 — não é esta missão (ver PROBLEMA 2).
4. **Órfão de marcação → espaço, só até o próximo branco.** `</`, `<!--`, `<!x`, `<?x` sem «>» não são texto para
   ninguém; `[^\s<>]*` não pode atravessar linha nem palavra seguinte.

**Resultado que dá para dizer numa linha:** nas 216 páginas da árvore o texto da régua 3 é **letra a letra o da
`limpar()` do vivo**, a menos de espaços/quebras (`A_dif_v2_semespaco = 0`). E vale em geral, não só na amostra:
cada etiqueta da régua 3 é um pedaço de uma etiqueta da v2 que acaba no mesmo «>», e cada órfão apagado estava
dentro de uma etiqueta da v2 — a régua 3 só apaga o que a v2 já apagava (única exceção: um órfão `</x` no fim do
ficheiro, sem nenhum «>» depois).

**`coleta/executor_texto_de_html.py`** — `EXECUTOR_VERSION = "4"` e o parágrafo que diz porquê. Nada mais.

**Testes / provas** — `tests/test_derivacao_estrutura_v2.py`; `tests/test_a_receita_tem_versao.py` (+ receita "4",
+ `test_voltar_a_limpar_de_duas_passagens_sem_subir_a_versao_reprova`); `tests/test_derivacao_estrutura.py` (80 → 82,
comentado); `tests/fixtures/balsamico_orfao/{mixology,filiera-del-vino}.recorte.html` (+ `.gitattributes -text -diff`);
`provas/derivacao_estrutura/{mutar.py (M1 reescrito, M3 4→3, M9-M11), replay_acervo.py (medida de conteúdo),
nao_e_regra_de_site.py}`. Mapa: fixture declarada em `C-EXECUTOR-TEXTO-HTML`.

---

## EVIDÊNCIA

### 1 · O defeito, reproduzido na árvore antes de mexer

A página do coordenador (`97c93e649a689d3f-…-mixology.html`) não está na nuvem, mas **a mesma página** (`IT-T7-042`,
três versões) está versionada em `data/collection-store/italy/IT-T7-042/`. Com a régua 2:

```
$ python3 (a 1.ª passagem de bloco, depois lista toda etiqueta <[^>]+> com \n ou < dentro)
89  '</\n\n\r\n…\t<a class="social" href="https://twitter.com/tutelabalsamico" target="_blank">'
328 '</\n\n\n\n\r\n…\n\nL’ACETO BALSAMICO DI MODENA IGP DIVENTA L’INGREDIENTE SEGRETO DELLA MIXOLOGY \n\n
     L’utilizzo dell’Aceto Balsamico di Modena IGP nella preparazione dei cocktail è un trend in continua crescita \n\n\n
     <a href="https://www.consorziobalsamico.it">'
```

Os mesmos **328 caracteres** que o coordenador mediu. Na árvore, 30 páginas têm `</` não seguido de letra (todas
consorziobalsamico, 2 ocorrências cada); 0 páginas têm «<» órfão de outro tipo.

### 2 · Os recortes reais e a mutação «voltar à v3»

`tests/fixtures/balsamico_orfao/` = recortes **contíguos, byte a byte** (1 109 e 1 200 bytes), do 2.º `</</div>` até
o fim da migalha, de:

| recorte | sha256 do recorte | página de origem (sha256) |
|---|---|---|
| `mixology` | `420803ca…c6fc34` | `…/v3_114bdcdb5c31/co-di-modena-igp-diventa-lingrediente-segreto-della-mixology.html` (`114bdcdb…7751`) |
| `filiera-del-vino` | `f2858d63…1db88` | `…/v3_2797e324a40f/a-sostegno-della-filiera-del-vino-italiano.html` (`2797e324…4325`) |

```
$ python3 -B tests/test_derivacao_estrutura_v2.py
Ran 13 tests … OK
```

`limpar/3` sobre o recorte do mixology:
```
FR
ES
L’ACETO BALSAMICO DI MODENA IGP DIVENTA L’INGREDIENTE SEGRETO DELLA MIXOLOGY
L’utilizzo dell’Aceto Balsamico di Modena IGP nella preparazione dei cocktail è un trend in continua crescita
Home / News / L’ACETO BALSAMICO DI MODENA IGP DIVENTA L’INGREDIENTE SEGRETO DELLA MIXOLOGY
```
Com a régua 2 (mesma entrada): `['FR', 'ES Home / News / L’ACETO … MIXOLOGY']` — título e subtítulo somem como linha;
o subtítulo some do texto inteiro. (No mixology o título ainda chega ao `corpo()` porque a migalha o repete; o
teste mutante exige, nos dois recortes, TÍTULO e SUBTÍTULO fora do TEXTO e SUBTÍTULO fora do `corpo()`.)

### 3 · Testes

```
$ python3 -B -m unittest tests.test_derivacao_estrutura tests.test_a_receita_tem_versao tests.test_derivacao_estrutura_v2
Ran 56 tests … OK
$ for t in test_a_rota_do_html test_tempo_e_lugar_da_publicacao test_leitor_data_youtube \
           test_c4g_a_especie_do_video test_conserto_regua test_quarentena_naosei test_m2_rota_forward; do …; done
OK · OK · OK (skipped=1) · OK · OK · OK · OK (skipped=23)
$ python3 -B tests/test_c10_6d_portas_canonicas.py
FAIL: test_8_a_rota_da_janela_e_a_que_a_matriz_nomeia     ← IGUAL com as mudanças guardadas (git stash): pré-existente
```

(São os 7 ficheiros que o grep por `texto_fonte`/`limpar(` acha em `tests/`, mais os 4 que a v1 corria por chamarem o
executor — 11 ficheiros. A bateria inteira
por nome — 26 min na v1 — **não** foi recorrida aqui; ver O QUE NÃO SEI.)

### 4 · Mutação

```
$ python3 -B provas/derivacao_estrutura/mutar.py   → provas/derivacao_estrutura/MUTACAO-DERIVACAO-ESTRUTURA.json
M1_B1_revertido                     MORTO  test_derivacao_estrutura, test_a_receita_tem_versao, test_derivacao_estrutura_v2
M2_regua_muda_sem_versao            MORTO  test_a_receita_tem_versao
M3_versao_nao_subiu (4 -> 3)        MORTO  test_a_receita_tem_versao
M4_regua_fora_da_receita            MORTO  test_a_receita_tem_versao
M9_V2_duas_passagens                MORTO  test_derivacao_estrutura, test_a_receita_tem_versao, test_derivacao_estrutura_v2
M10_V2_etiqueta_atravessa_menor     MORTO  test_a_receita_tem_versao, test_derivacao_estrutura_v2
M11_V2_orfao_fica                   MORTO  test_a_receita_tem_versao, test_derivacao_estrutura_v2
M5..M8 (B2)                         MORTO  test_derivacao_estrutura
"MORTOS": 11, "DE": 11, "ORIGINAIS_REPOSTOS": true   (ESPERADOS_CUMPRIDOS: true em todos)
```

M9 é literalmente a volta à v3 (as duas linhas antigas no lugar das duas novas).

### 5 · Replay — a medida de CONTEÚDO

Critério gravado no próprio JSON (`CRITERIO_DO_VEREDITO`): **PIOROU** = alguma palavra de conteúdo (≥4 letras,
minúsculas) do `corpo()` ANTES não aparece em NENHUM lugar do TEXTO DEPOIS; **MELHOROU** = não piorou e o `corpo()`
DEPOIS tem palavras de conteúdo que o `corpo()` ANTES não tinha; **IGUAL** = o resto. Palavra que sai do `corpo()` mas
continua no TEXTO não é piora desta mudança — é o filtro do elo 4, contado à parte
(`PAGINAS_EM_QUE_SO_O_CORPO_LARGA_PALAVRAS`).

```
$ python3 -B provas/derivacao_estrutura/replay_acervo.py --armazem data/collection-store/italy \
      --saida provas/derivacao_estrutura/replay-arvore-216 --qualquer-html
COPIA_LITERAL_CONFERIDA SIM · EXECUTOR_BASE_DE git show e24139702:… · EXECUTOR_VERSION_DEPOIS 4 · 3.0 s
PAGINAS 216 · ERROS []
SAEM_DE_1_LINHA 28 · MEDIANA_LINHAS 73 → 106 · CORPO_VAZIO 28 → 0 · CRESCE 42 · ENCOLHE 105 · IGUAL 69
CORPO_MENOS_DE_20_PALAVRAS_DEPOIS []
PAGINAS_COM_PERDA_NO_TEXTO []
MELHORARAM 43 · IGUAIS 173 · PIORARAM 0
PAGINAS_EM_QUE_SO_O_CORPO_LARGA_PALAVRAS 105        ← elo 4 (filtro por linha), só medido
PUBLISHED_AT_RESPONDIA_ANTES 202 · MUDA [] · PERDE [] · GANHA []
PAGINAS_COM_DATA_EM_PROSA_QUE_SAI_DO_CORPO 33 · QUE_ENTRA 3   ← elo 4, iguais à v1
CONTROLO_NEGATIVO PASSA
```

**Contraprova — a medida apanha o defeito:** o mesmo `replay_acervo.main()` com `limpar_depois` trocado pela régua 2
(script de rascunho, não versionado):

```
COM A limpar/2 · PAGINAS_COM_PERDA_NO_TEXTO 6
   IT-T7-042 …/v1_6296ba29a21e/a-sostegno-della-filiera-del-vino-italiano.html ['fino', 'imitazioni']
   IT-T7-042 …/v2_7d6ff716cde2/…                                               ['fino', 'imitazioni']
   IT-T7-042 …/v3_2797e324a40f/…                                               ['fino', 'imitazioni']
   IT-T7-042 …-mixology.html (×3)                                              ['continua', 'crescita', 'preparazione']
MELHORARAM 43 · IGUAIS 167 · PIORARAM 6
```

As palavras são as que o coordenador listou («fino a 60 milioni … eliminando le imitazioni», «… continua crescita»).

**No armazém (536), a correr pelo coordenador:**
```
py provas/derivacao_estrutura/replay_acervo.py --armazem C:\Users\London1\sintonia-sala-italia\armazem --saida <pasta>
```
Esperado: `PAGINAS_COM_PERDA_NO_TEXTO` **vazio** (pelo argumento de §O QUE MUDOU a régua 3 só apaga o que a v2 apagava;
a cand-1205, stack Java, perdia com a régua 2 e deve deixar de perder), `PIORARAM 0`, controlo negativo PASSA, e os
mesmos 21 `GANHA` (a régua 3 não toca em `tempo_de_publicacao`, que lê o HTML cru).

### 6 · «Não é regra para a Xylella»

```
$ python3 provas/derivacao_estrutura/nao_e_regra_de_site.py
BASE e24139702 · coleta/ · padrao crea|xylella|balsamic|consorzio|https?:|www\.|\.it\b|IT-T\d|dominio|hostname|netloc|urlparse
LINHAS_DE_CODIGO_ACRESCENTADAS 136 · CITAM_SITE 0 · (em comentario/docstring: 5, que contam de onde veio a medida)
RC=0
```
Contraprova do detector: com `_SO_CREA = "www.crea.gov.it"` acrescentado a `texto_fonte.py`, `CITAM_SITE 1` e `RC=1`
(ficheiro reposto). E o grep cru, para quem não quer confiar no tokenizador:
```
$ git diff e24139702 -- coleta/ | grep -niE '^\+.*(crea|xylella|balsamic|consorzio)'
29:+# e um «</» orfao (`…</a></</div>…`, balsamico IT-T7-042) engolia titulo e
43:+# Medido no RAW 2272 (CREA, derived:1149): a página escreve a publicação só
240:+# Até aqui TODA etiqueta virava espaço. Medido no RAW 2272 (CREA, derived:1149):
```
Três linhas, todas `+#` (comentário).

**As 21 que ganham data no armazém** (números do replay do coordenador; as páginas não estão na nuvem, não as
reli): **IT-T5-056 ×9 · IT-T5-111 ×8 · IT-T5-113 ×4**, todas CREA, todas pela base
`DIV.content-date (irmão de content-category)`.

**Observação honesta:** o seletor é genérico — duas classes (`content-metadata` › `content-date` + irmão
`content-category`) e uma data italiana completa, sem domínio, sem URL, sem nome de fonte. **Mas, no acervo medido,
só o molde CREA o usa**: 21/21 ganhos são CREA, e na árvore versionada (216) não há `content-date` em página
nenhuma (`grep -rl content-date data/collection-store | wc -l` → 0). Genérico no código não é o mesmo que provado em
mais de um site: hoje a regra só foi vista a responder num molde. Se amanhã outro site usar as mesmas classes com
outra semântica, a régua de valor (data completa, âncoras `^…$`, nunca FACT_TIME) é o que segura — os 23 venenos da v1.

### 7 · System Map

```
$ python3 system-map/scripts/correr_a_cadeia.py REGERAR
  … frescura CURRENT · a arvore e as entradas sao as que foram medidas
  CADEIA=OK · REGERAR
$ python3 system-map/scripts/correr_a_cadeia.py VALIDAR
  PASS P1_SEM_DRIFT … PASS P8_UM_DONO   (23 PASS, 0 FAIL)
  SYSTEM_MAP_CHECK=PASS · o mapa corresponde ao repositorio
  CADEIA=OK · VALIDAR
$ python3 system-map/scripts/impressao_da_arvore.py --conferir-carimbo     (depois do commit final)
```
Declarado à mão (e só isto) em `architecture.declared.json`: a fixture `tests/fixtures/balsamico_orfao/*.html` em
`C-EXECUTOR-TEXTO-HTML` (+ uma frase no `what`); o script novo já cabia no `provas/derivacao_estrutura/*.py` de
`C-PROVA-ROTA-DO-HTML`. O resto dos `*.generated.json` e do censo saiu da cadeia. O `--conferir-carimbo` vai na
mensagem de entrega (este ficheiro é FONTE; escrever aqui o carimbo moveria a impressão que ele mede).

---

## PROBLEMA

1. **Versão 4 = derivados novos outra vez.** Cada re-derivação escreve `texto-de-html` "4". Se a "3" chegou a ser
   instalada/escrita na Sala (não sei — ver abaixo), os derivados "3" dos 14 HTML com «</» órfão têm título/subtítulo
   em falta e continuam lá até alguém re-derivar.
2. **Comentários HTML continuam a vazar como sempre vazaram** (`-->`, e o conteúdo de `<!-- … <tag> … -->` depois
   do 1.º «>»). A régua 2 escondia parte disso **por acidente** — o mesmo buraco que comia o título comia
   `<!--\nPDF\n-->`. Por isso o RAW 2272 passa de 80 para 82 linhas (duas linhas `-->` dos anexos PDF; `corpo()`
   igual, 7 705). Tratar o comentário como o navegador (até `-->`) está medido (C4: muda 162/216 textos, 1 página
   perde palavras de conteúdo comentado) e **não foi feito**: é outra régua, com outra versão.
3. O filtro por linha do `corpo()` (elo 4) continua a largar palavras que o TEXTO tem: **105/216** páginas. A
   maioria é menu que sai (v1 PROBLEMA 1); as 33 datas em prosa que saem do corpo são as mesmas da v1. Só medido.

## O QUE NÃO SEI

- **Os números do armazém (536) com a régua 3.** Não está na nuvem. Espero perda 0 e 21 ganhos iguais (argumento
  acima); não o vi.
- **A bateria inteira por nome** (7 241 nomes na v1) não foi recorrida: corri os 11 ficheiros que tocam `limpar()`/o
  executor e o `mutar.py`. A régua 3 dá o mesmo texto da v2 a menos de brancos na árvore, mas um teste que conte
  linhas de outra fixture com `<!-- <div>` mudaria como o do RAW 2272.
- **Se a versão "3" chegou a escrever derivados** em algum lado (o ramo v1 não foi fundido; não verifiquei a Sala —
  fora do escopo).
- **A página IT-T10-018 (fruttivendoli)** não está na árvore; não a vi — conto com o mesmo mecanismo (o coordenador
  mediu-a no mesmo grupo).
- Um órfão `</x` no **fim** do ficheiro, sem «>» depois, é apagado pela régua 3 e era texto na v2 — caso teórico, 0
  na árvore.

---

## EM PALAVRAS SIMPLES

1. Em algumas páginas mal escritas (um «</» sobrando, como no site do balsâmico), o leitor novo apagava o título e o
   subtítulo da notícia; agora não apaga mais.
2. A correção é uma regra geral de leitura de HTML, sem nome de site nenhum, e nas 216 páginas guardadas o texto
   voltou a ter exatamente as mesmas palavras de antes — só com as quebras de linha certas.
3. A «receita» mudou de versão (3 → 4), então texto lido do jeito velho e do jeito novo nunca se confundem.
