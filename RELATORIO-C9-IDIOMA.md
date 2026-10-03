# RELATÓRIO — C9-IDIOMA (dívida do MICRO-V3, D54)

Ramo `c9-idioma-v1`, a partir da produção `origin/servico-20260923-0923 @ df0865e6`. **Não instalado.**
Rede: 0 pedidos. Sala: só `SELECT` com `default_transaction_read_only` (`micro_coleta.sql`); vivo e Sala intocados.

## 1 · O que são os 2 documentos

| RAW | derivado | o que é | palavras comuns (it / pt / en) |
|---|---|---|---|
| 1436 | 937 | notícia ARPAE «Mare, riviera interamente balneabile» (15/9/2026): a costa inteira da Emilia-Romagna está própria para banho | 17 / 1 / 0 (302 palavras) |
| 1437 | 938 | notícia ARPAE «Aggiornamento al portale prelievi» (18/9/2026): dados actualizados após as chuvas | 9 / 0 / 0 (230 palavras) |

Os dois: HTML com texto, **italiano claro**, notícias curtas com o menu do site à volta. Textos extraídos no
armazém em `NAO_SEI/derivados/TEXT_EXTRACTION/texto-de-html-1-0b76a7ef…` e `…-cb97a09c…` (sha256 `33a0015c…`,
`8a1525fe…`); cópias iguais em `tests/dados/c9-idioma/`.

**Porque o detector disse NÃO SEI:** `scripts/micro_coleta/micro_coleta.py:475` (era `:463`) — `idioma()` conta, em
cada língua, as 10 palavras mais comuns, e só responde se a vencedora tiver **20 ou mais**. Uma notícia curta
italiana tem 9 ou 17. E o C9 (`:694`) conta como violação tudo o que não for `it`/`pt` — o «NÃO SEI» do
detector entrava como «estrangeiro».

O NÃO_SEI da **Admission** destes dois é outra coisa, escrita no livro: «QUARENTENA (D11): o detector não sabe
se isto é matéria ou página de entrada». Nada tem a ver com idioma.

## 2 · Classificação: **(A) defeito do detector** — texto italiano não reconhecido

Não é (B): os documentos têm texto útil (corpo de notícia datado). A dúvida que os pôs em NÃO_SEI é a D11
(matéria/entrada), que é de outro juiz e não foi mexida.

## 3 · O conserto (dono único: `idioma()`), sem mudar a regra C9

Medido nos **761 textos extraídos do armazém** (só leitura, 25/09): acima de 20 nada muda; abaixo, há um **vão**
— nenhum texto tem entre 5 e 8 palavras comuns — e por baixo dele só restos de 30–40 palavras (menus).

- `>= 20`: igual a antes.
- `8 a 19`: conta **só com domínio claro**, 3 vezes ou mais a 2.ª língua (`IDIOMA_MINIMO_CURTO = 8`,
  `IDIOMA_DOMINIO = 3`, `:470-472`).
- resto: NÃO SEI, como antes.

Efeito nos 761: **10** passam de NÃO SEI a `it` (entre elas as 2 do MICRO-V3); **0** línguas já decididas mudam;
«11 contra 6» continua NÃO SEI. A regra C9 (`:694-708`) ficou igual: um texto estrangeiro com NÃO_SEI sem sinal
continua a contar (testado).

## 4 · C1 e C3 em FAIL com IT,IT e ELIGIBLE registados

O relatório global da onda foi pedido pela **linha de comando** (`micro_coleta.py relatorio --run-id=…`), e a linha de
comando chamava `relatorio(ids, saida=saida)` **sem as corridas** (`:757` antes). É nas corridas que o C1 procura o
egresso (`EGRESSO_ANTES/DEPOIS`) e o C3 o portão (`GATE_NO_INSTANTE`): com a lista vazia, `MEDIDO: []` e FAIL. O
`onda_web` grava isso por fonte no `ONDA-WEB-ESTADO.json` (`ferramentas/big_collection/onda_web.py:314-315`: `GATE`,
`EGRESSO [antes, depois]`), e ninguém o entregava ao relatório.

**Conserto:** `relatorio --estado=<ONDA-WEB-ESTADO.json>` (`:800`) e `corridas_do_estado()` (`:748`), que só **traduz**
o que o estado diz — o que falta fica `None` e o critério, o mesmo, reprova. Fontes que não correram (sem RUN_ID)
não entram. Com o estado do MICRO-V3, o relatório pode ser pedido assim:

```
py scripts/micro_coleta/micro_coleta.py relatorio --estado=<ondas/MICRO-V3-20260925-0803/ONDA-WEB-ESTADO.json> --saida=<pasta>
```

(Não o corri: pede leitura da Sala por consulta, e a 2.ª onda está a correr. Fica para o coordenador.)

## 5 · Testes e mutação

- `tests/test_c9_idioma.py` **9/9**: as amostras são as do armazém (sha256); as 2 notícias saem `it`; acima de 20
  igual; banda curta só com domínio (11×6, 8×3, 4×0, 7×0 → NÃO SEI; 9×0 inglês → `en`); o C9 já não as conta; o C9
  continua a contar estrangeiro sem sinal; C1/C3 leem o estado; o critério não afrouxou (IT,US / egresso em falta /
  BLOCKED reprovam); a linha de comando passa as corridas do estado.
- Testes que já existiam (`test_micro_coleta_instrumento`, `test_ensaio_offline_micro`, `test_micro_rede_real`):
  56 testes, **as mesmas 5 falhas** com e sem a mudança (na produção `df0865e6` também).
- **Mutação 7/7** (`scripts/micro_coleta/MUTACAO-C9-IDIOMA-V1.json`, cópia `C:/capa-base`).
- As 2 amostras ficam `-text` no `.gitattributes`: com `core.autocrlf` ligado o checkout trocaria LF por CRLF e o
  teste do sha256 cairia na máquina instalada.

## Writeset

```
scripts/micro_coleta/micro_coleta.py        (idioma: banda curta; relatorio --estado; corridas_do_estado)
tests/test_c9_idioma.py · tests/dados/c9-idioma/raw-1436-*.txt · raw-1437-*.txt · .gitattributes
scripts/micro_coleta/mutar_c9.py · MUTACAO-C9-IDIOMA-V1.json · RELATORIO-C9-IDIOMA.md · system-map (declarado)
```
