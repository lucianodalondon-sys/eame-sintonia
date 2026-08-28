# FREEZE DA BASE DO PILOTO

Estado da matéria-prima que vai para o Claude Design.

```
PILOT_INFORMATION_BASE = FROZEN
VERSION                = 2026-08-29 / v1
HEAD                   = registrado no commit de congelamento
TESTES_REAIS           = 43
PROTOTYPE_FROZEN       = SIM
```

> **Congelar não é parar de coletar.** As fontes continuam mudando e o DATA CLOCK
> continua. O que congela é o **pacote enviado ao Design**: daqui em diante, uma
> descoberta nova entra como **nova versão**, com data e HEAD, e não altera em silêncio
> o que já foi entregue.

---

## 0 · RECONCILIAÇÃO DO PRÓPRIO CHECKPOINT

Havia duas contagens de teste no fim da MISSÃO 06:

| onde | número | correto? |
|---|---|---|
| relatório entregue | 37/37 | **sim** |
| mensagem do commit `e37911a` | 38/38 | **não** |
| suíte executada | **37** | — |

**Origem da diferença:** `tests/test_canonico.py` foi de **19 para 21** métodos naquele
commit (`f004765` → `e37911a`), somando **dois** testes, não três. A mensagem do commit
dizia "três testes novos, 38/38". **O relatório estava certo e a mensagem do commit estava
errada.**

**O que foi corrigido:** nada no histórico — a mensagem de um commit publicado não se
reescreve. O erro fica registrado aqui, e a causa foi eliminada: **o total declarado passou
a ser derivado da suíte**. `tests/test_canonico.py::test_o_total_de_testes_declarado_vem_da_suite`
conta a suíte com `unittest.defaultTestLoader.discover` e exige que `TESTES_REAIS` neste
documento seja esse número. Um número escrito à mão volta a divergir; um número derivado não.

---

## 1 · CONDIÇÕES DE CONGELAMENTO

| condição | estado | onde |
|---|---|---|
| deck reconciliado | ✅ 35 claims (22 confirmados · 5 alterados · 1 removido · 6 novos + 1 retirado na M05) | `../apresentacao/RECONCILIACAO-DECK-REAL.md` |
| business questions definidas | ✅ 3, todas `PILOT READY` com escopo declarado | `../piloto/PACOTE-DE-MATERIA-PRIMA-EAME.md` |
| hero cases definidos | ✅ 3 sobreviventes + CASE-015 promovido | `../apresentacao/CASOS-PARA-APRESENTACAO.md` |
| source pack definido | ✅ 12 fontes, 5 CRITICAL | `../piloto/SOURCE-PACK-PILOTO.md` |
| identity model definido | ✅ 7 entidades, teste negativo **medido** em 165 registros | `../regras/MODELO-DE-IDENTIDADE-EAME.md` |
| cross-market reproduzido | ✅ FR · ES · IT, os três **primários**, com a rota de cada um declarada | `CROSS-MARKET-prothioconazole-cereal.json` |
| Ask Sintonia sem resposta errada | ✅ 35 perguntas · 20 respondidas · 14 recusadas · 1 parcial · **0 erradas** | `../piloto/ASK-SINTONIA-BENCHMARK.md` |
| safe claims fechadas | ✅ 14, com auditoria de 7 palavras sob controle | `../piloto/O-QUE-PODEMOS-DIZER.md` |
| forbidden claims fechadas | ✅ 19, incluindo as 2 retiradas nesta missão | idem |
| data clock ativo | ✅ 7 arquivos vigiados + a régua de change event | `../regras/REGUA-DE-CHANGE-EVENT-EAME.md` |

**Todas as dez fecham.** `PILOT_INFORMATION_BASE = FROZEN`.

---

## 2 · O QUE MUDOU NA MISSÃO 07 E ENTRA NA v1

| # | mudança | efeito no pacote |
|---|---|---|
| 1 | rotas públicas do registro espanhol (`ES-T4-005`) | a Espanha deixa de ser a perna fraca: 3.084 registros, ficha completa por registro |
| 2 | ES-01717 **inteiro em fonte primária** | some a única ressalva de fonte do piloto |
| 3 | fabricante corrigido: `ADAMA MAKHTESHIM LTD.` → **`ADAMA Agricultural Solutions Ltd.`** | uma afirmação errada sai do pacote |
| 4 | "2,45× o mercado" e "metade do mercado" **retiradas** | duas frases maiores que o dado saem |
| 5 | recontagem com contrato de coluna: 1.786 / 720 / 363 (18,2%) | os números passam a ter denominador declarado |
| 6 | régua de change event | o DATA CLOCK deixa de ser argumento e vira tipo de evento com veredito |
| 7 | CASE-015 dividido em CORE CLAIM e ADAMA-SPECIFIC CLAIM | o núcleo do hero não depende de nenhum campo frágil |
| 8 | benchmark 25 → 35 perguntas | duas recusas viraram respostas **por fonte nova**, não por régua frouxa |
| 9 | 6 provas novas (37 → 43) | inclui a que deriva este número da própria suíte |

---

## 3 · O QUE **NÃO** ENTRA — e por quê

| descoberto nesta missão | por que fica fora do pacote |
|---|---|
| ADAMA é a titular com **mais registros** na Espanha (188 de 3.084) | é contagem de registros. Sem venda e sem volume, a frase comercial correspondente seria maior que o dado |
| 519 concessionárias que **não** são titulares de nenhum registro | medida interessante e não auditada: o vocabulário de empresas ainda não normaliza `KENOGARD, S.A.` e `KENOGARD S.A.U.` |
| 156 novas denominações e 30 removidas entre as duas versões | os eventos existem, mas nenhum foi verificado um a um como as renomeações foram |
| `STATUS/HOLDER/COMPOSITION/DATE CHANGE` | o campo existe e é comparável; falta a **segunda** versão arquivada do export. `POSSÍVEL, não provado` |

**Nenhuma capacidade nova entrou no pacote só porque apareceu durante a auditoria.**

---

## 4 · DIVERGÊNCIA REGISTRADA E NÃO RESOLVIDA

Duas leituras primárias do mesmo registro espanhol, com minutos de diferença no mesmo dia:

| leitura | Vigente | Cancelado | Total |
|---|---|---|---|
| grade (`ProductosGrid?IdEstado=1` / `=2`) | 1.998 | 1.086 | 3.084 |
| export (`ExportJsonProductos`) | **1.993** | **1.091** | 3.084 |

O total bate; a divisão não. Não sabemos qual campo a grade usa. **Enquanto não soubermos,
nenhum número desta fonte é publicado com precisão maior que a divergência** — por isso
"18,2% dos em vigor", e não "18,21%".

---

## 5 · O QUE O DESIGN RECEBE

`../piloto/ENTRADA-PARA-CLAUDE-DESIGN.md` — pacote factual, sem instrução de layout.
Nenhum número fake. Nenhuma tela. **CLAUDE DESCOBRE O PRODUTO. CLAUDE DESIGN DESENHA O
PRODUTO.**

---

## 6 · COMO SAIR DO FREEZE

Uma descoberta nova **não** edita a v1. Ela abre a v2:

1. registrar a evidência em `data/samples/` com envelope de proveniência;
2. registrar a mudança como `CHANGE EVENT` se vier de comparação de versões;
3. atualizar os documentos canônicos **e** as provas que os amarram;
4. abrir uma linha nova nesta tabela, com `VERSION`, `HEAD` e `DATE`.

| VERSION | DATE | HEAD | o que mudou |
|---|---|---|---|
| **v1** | 2026-08-29 | *commit de congelamento* | primeira base congelada |
