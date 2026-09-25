# RELATÓRIO · CAPA-MATERIA — porque a 1.ª onda rendeu pouco, e o que se conserta

Branch `capa-materia-v1`, a partir da produção `7cdb7ea4` (T1 instalada). Offline: zero rede, nada
mexido no vivo (o livro de coletas da produção foi só LIDO). **NÃO instalado.**

## Em palavras simples

Na 1.ª onda, 6 respostas foram NÃO ou NÃO SEI. Olhei uma a uma, nos bytes guardados:

1. **Duas «capas no lugar de matéria» — e são dois erros diferentes:**
   - **IT-T7-135 (cia.it): o coletor escolheu a página de CONTATOS.** O contrato proíbe «contatti»
     só no início do endereço (`cia.it/contatti/`); a página era `cia.it/news/settore-comunicazione-contatti/`,
     era o 1.º link do índice, e como o contrato pede 1 alvo (`MAX_TARGETS = 1`), foi o único.
     **Conserto:** o coletor deixa de aceitar como alvo um endereço cujo ÚLTIMO pedaço ACABA numa
     palavra de página institucional (contatti, chi-siamo, privacy, cookie, newsletter, faq…) —
     `regras/motor_de_rota.mjs::ligacoesDoIndice`, uma linha nova. **Aperta; não afrouxa nada.**
     A mesma página era o 1.º link da **IT-T7-121** (www.cia.it), que na 1.ª onda trouxe 0 porque
     a página já estava no livro. O conserto vale para as duas.
   - **IT-T7-042 (consorziobalsamico.it): o coletor foi a uma matéria de verdade** (uma notícia
     curta do blog). Quem errou foi o **detector de capa**: 786 caracteres de parágrafo, abaixo dos
     800 que ele exige, e 92 links. **Não consertei**, por duas razões: consertar seria afrouxar o
     detector; e **não renderia nada** — a mesma notícia, julgada como matéria, dá NÃO SEI em T7
     (só «consorzio»), como as outras duas notícias do mesmo site.
2. **Os três «só uma palavra do tema»** (IT-T7-021 ×1, IT-T7-042 ×2): **nenhum muda** com as
   réguas T1 e T2 instaladas. São perguntas de T7, e T1/T2 não mexem em T7 (0 mudanças em 9.163,
   medido na T1). Perguntados a T1, T2 ou T10, também não dariam SIM: são notícias sobre aceto
   balsâmico, um prémio e a visita de uma delegação a um consórcio de rega.
3. O «outro universo» (IT-T7-117, caf-cia.it) é uma página de serviço fiscal (730). Continua NÃO,
   e está certo.

## Medidas (sem rede)

| O quê | Resultado |
|---|---|
| Endereços já coletados pela produção (livro de coletas) | 169 |
| Quantos a regra nova teria recusado | **2** — a mesma página de contatos da cia.it (IT-T7-121 e IT-T7-135); **0 matérias** (`MEDICAO-FILTRO-INSTITUCIONAL-V1.json`) |
| Testes do motor (`regras/motor_de_rota_test.mjs`) | 50/50 (3 novos: contatos saem e o 1.º alvo passa a ser o artigo; «contatti» no meio do título continua a passar; privacy/chi-siamo/newsletter/faq saem) |
| Mutação | tirar o filtro → 2 testes caem; a palavra valer em qualquer sítio → 1 teste cai |
| Outros testes | `incrementalidade_test` 31/31, `recollection_test` 31/31, `paridade_test` 32/32; `italy_contract_test` 348/77 — **as mesmas 77 falhas na produção sem a mudança** (lista comparada, igual) |
| Rejulgar a 1.ª onda com T1+T2 | 0 mudanças (`REJULGAR-1A-ONDA-V1.json`) |

## Previsão honesta do MICRO com a coorte atual

- Base (REND/ONDA2-PLANO): ~**3 SIM em 18 = 16,7 %** — IT-T10-018 (2) e IT-T7-141 (1). **Não passa**:
  a D35 exige ESTRITAMENTE acima de 16,7 %.
- Com este conserto: as duas fontes da cia.it (IT-T7-121 e IT-T7-135) passam a ir ao **primeiro
  artigo** do índice em vez da página de contatos. **Se esse artigo for novo E for T7, cada uma
  soma 1 SIM**: 4/18 = 22,2 % ou 5/18 = 27,8 %.
- ⚠️ **NÃO SEI se isso acontece.** Não guardámos o índice da cia.it (só o alvo); saber qual é o
  primeiro artigo pede 1 visita ao índice (rede). E o que a cia.it publica em «news» é sobretudo
  política e vida sindical — em T7 (rede técnica) o mais provável é NÃO SEI ou NÃO. A minha
  estimativa: **a micro continua em 3/18 = 16,7 % e não passa**, a não ser que o artigo seguinte
  seja técnico.
- O que pesa mais no rendimento **não é capa/matéria**: é que 12 das 18 fontes não trazem nada novo
  (`MAX_TARGETS = 1` e esse primeiro link já está no livro). Isso é outra decisão (coorte/R1/MAX_TARGETS),
  fora desta missão.

## Writeset

| Ficheiro | Muda |
|---|---|
| `regras/motor_de_rota.mjs` | **único código de produção**: `PAGINA_INSTITUCIONAL` + `eInstitucional()` + 1 linha em `ligacoesDoIndice` |
| `regras/motor_de_rota_test.mjs` | 3 testes |
| `scripts/capa_materia/**`, este relatório, `system-map/data/architecture.declared.json` | evidência e mapa |

Instalação: juntar na produção (conflito só nos gerados → cadeia); `node regras/motor_de_rota_test.mjs`
e os outros testes de `regras/`; voltar atrás = reverter o merge. **Ninguém precisa de reiniciar**: o
coletor lê o motor a cada corrida.
