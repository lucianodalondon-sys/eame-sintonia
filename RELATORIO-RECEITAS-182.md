# RELATÓRIO — RECEITAS-182

Ramo `receitas-182-v1`, a partir de `integra-onda2-v1 @ e2f47ed3`. **Não instalado.**
Rede fechada por omissão (D41.3); rede só na captura e na medida, com o portão de consenso
PASS IT, fila filtrada (14 fontes, 1 por domínio) e o teto D38 (5 pedidos por domínio, no total).

## 1 · As 183 pela forma real (sem rede)

Hoje são **183** (a medida 7 da ACOMPANHAR-FILA dizia 182; uma mudou de estado desde então).
Fonte: o livro vivo `7cdb7ea4`, só leitura (`scripts/receitas_182/EXTRACAO-182-V1.json`, com o
sha256 dos 4 livros lidos). ⚠️ Estas fontes já **não** param no molde antigo: o robô tentou
repará-las (`reparar_contrato.py`, R1) e o reparo recusou cada uma com um nome. O robô **não
guardou as páginas** — só o retrato da entrada, os bytes e endereços lidos e a frase do motivo. A
forma decide-se por regras declaradas (`classificar_182.py`), e onde a prova não chega diz-se.

| forma | fontes | o que é |
|---|---:|---|
| SITE_DE_ORDEM_PROFISSIONAL | 63 | ordens e federações de agrónomos (`ordine*.conaf.it`, `agronomi*`): páginas fixas e avisos curtos |
| MENU_INSTITUCIONAL | 25 | páginas de serviço/região sem lista de publicações |
| PASSOU_A_REGUA_ESPERA_LEITURA | 14 | o reparo passou a régua; falta **uma pessoa ler o item** (REVISAO_PENDENTE) |
| PAGINA_BOLETIM | 13 | a entrada é a página de um boletim ou de um mapa |
| PAGINA_UNICA | 13 | a entrada é ela própria um texto (centros do CREA, ordens da ER) |
| **LISTA_MOLDE_NAO_ACHOU** | **13** | lista de publicações, e o reparo não achou 2+ itens |
| LISTA_CERTA_JUIZ_DIZ_CAPA | 9 | havia item com ≥ 800 letras em parágrafos e o juiz disse capa/não sei (menu grande) — régua, não molde |
| **LISTA_MOLDE_ESCOLHEU_MENU** | **9** | lista de publicações, e o reparo gastou as 3 tentativas no menu do site |
| JS_OU_VAZIA | 8 | a entrada vem quase vazia (< 3 000 bytes, ≤ 10 ligações): desenha-se no navegador |
| ITEM_CURTO_OU_NAO_ABRIU | 5 | o item tentado não tem corpo, ou deu erro |
| NAO_HTML_A_CONFIRMAR | 5 | 21–31 KB que o reparo diz não começar por `<` — **NÃO SEI** porquê sem os bytes (hipótese: BOM + quebra de linha antes do HTML) |
| DUPLICADA_DE_OUTRA_FONTE | 4 | o item achado já é de outra fonte (CREA) |
| LISTA_DE_ANEXOS_PDF | 2 | os itens são anexos (`allegato.aspx`) |

**O grupo «lista → notícia com molde errado» são 22** (13 + 9). Não é o maior: o maior (63) são
sites de ordens profissionais, e isso não é um defeito do molde.

## 2 · O conserto, no dono único

**Dono:** `curadoria/reparar_contrato.py::familias` (o gerador de receita do reparo R1; o canário
usa a receita que ele escreve). Mudança em `_junta` (a guarda) e duas peças novas
(`_so_titulos_longos`, `RECUSAS_POR_NAVEGACAO`), com o porquê no código.

**O defeito, medido nas páginas capturadas:** em 4 sites WordPress da fila (asnacodi, iret.cnr,
societaentomologicaitaliana, horta-srl) as notícias vivem na **raiz** (`/<título-da-notícia>/`),
ao lado de páginas fixas (`/cookie-policy-ue/`, `/tesi-di-laurea/`). O esqueleto junta-as; a
guarda da 6-PREP-d vê que o padrão casa navegação (`/chi-siamo` sintético) e **recusa a família
inteira** → SEM_FAMILIA_DE_ITENS com a lista à vista.

**O conserto:** quando — e só quando — a guarda recusa por **navegação**, tenta-se UMA versão
mais estrita do mesmo padrão: o último pedaço tem de ser um **título longo** (≥ 6 palavras, a
mesma medida `FLUXO_PALAVRAS` do fluxo) sem vocabulário institucional (privacy, cookie,
trasparenza, statuto…). Essa versão passa pela **mesma guarda** e pelo resto de `_junta`. Os outros
motivos da guarda (INDEX_URL, capa conhecida, > 80 % dos links) não se contornam. A régua
DETAIL/v1, o juiz de capa e o canário não mudaram.

**Tentei e desfiz** (diff guardado fora do Git, sha256 `911fda8f…`): mudar a ORDEM das famílias
para o menu não ser tentado primeiro. Medido nas páginas: o que subia para a frente eram páginas
fixas de título longo (amministrazione-trasparente, serviços) — não notícias; e no CREA as notícias
já são de outras fontes. Ganho 0, risco de aprovar página fixa.

**O leitor de links relativos** (`5239309a`, CUR-PRONTA/D32, não instalado) não entrou: nas 14
páginas capturadas não muda nenhuma família.

**Testes:** `curadoria/test_reparo_titulos_longos.py` 6/6; com `test_reparar_contrato` e
`test_canario_detalhe`, 54/54. **Mutação 4/4** (`MUTACAO-TITULOS-LONGOS-V1.json`, cópia
`C:/capa-base @ 5ba62386`). Um 5.º mutante sobreviveu e mostrou uma linha **redundante** — tirada
do código, não do teste.

## 3 · Medida com rede, em cópia

- **Captura** (`CAPTURA-ENTRADAS-V1.json`): 14 fontes, 1 por domínio, robots pela casa + entrada =
  **28 pedidos**, todos HTTP 200. Bytes fora do Git em `C:/Users/London1/receitas-182-20260925/entradas/`,
  sha256 no JSON.
- **Medida** (`MEDICAO-COM-REDE-V1.json`): o reparo com o conserto, como o worker o chama (guarda
  DUPLICADA com as READY e as já reparadas do livro vivo), entrada e robots vindos da captura
  (sha256 conferido), itens pela rede com no máximo 3 por domínio: **24 pedidos**. O canário
  (`canario_html`, com o portão capa/matéria) correu sobre as páginas que o reparo já tinha lido: 0 pedidos.
- Total por domínio: nunca mais de 5.

| fonte | antes | agora | item aberto pelo canário | corpo |
|---|---|---|---|---:|
| IT-T3-062 asnacodi /news/ | SEM_FAMILIA | **canário PASS** | `agrifondo-giuseppe-boatto-e-il-nuovo-direttore` | 1 629 |
| IT-T5-164 iret.cnr /news/ | SEM_FAMILIA | **canário PASS** | `notte-della-ricerca-a-napoli-la-scienza-diventa-un-gioco` | 1 514 |
| IT-T8-067 soc. entomologica /category/news/ | SEM_FAMILIA | **canário PASS** | `1-congresso-italiano-di-ortotterologia-26-27-settembre-2026-bolzano` | 1 600 |
| IT-T8-069 horta /news/ | SEM_FAMILIA | **canário PASS** | `cambiamento-climatico-come-aiutare-le-piante-a-produrre-...-2` | 1 125 |
| as outras 10 medidas | recusa | recusa igual | — | — |

**4 de 14 medidas passam; nas 22 do grupo, a previsão honesta é +4 fontes**, uma por site:
asnacodi tem 3 fontes no mesmo site, horta 2, iret 2 (T5-163) — a guarda DUPLICADA dá o padrão só à
primeira; as outras saem DUPLICADA. A isafom (IT-T5-165, outro site do CNR) **não foi medida** (D38:
o domínio cnr.it já tinha gasto).

⚠️ **Passar no canário não é ficar elegível.** Um contrato reparado vai para REVISAO_PENDENTE:
«passou a régua, mas ninguém leu o item». As 14 PASSOU_A_REGUA_ESPERA_LEITURA acima estão **aí
paradas** — é o ganho mais rápido das 183, e não precisa de código: precisa de quem leia.

## 4 · PDF e «a página é o boletim»: da JANELA-FORMAS (não duplicado)

Pela prova da própria JANELA-FORMAS (`janela-formas-v1 @ d0093df0`, canários reais), das 183:
- **resolve 3**: IT-T3-027 ERSA FVG (PDF), IT-T3-025 Campania (PDF, só a província NA), IT-T2-152
  LaMMA (a página é o boletim);
- **em espera de 1–2 pedidos de estudo JS: até 4** — Emilia-Romagna (IT-T3-028; as outras do estudo, IT-T3-008/013/018,
  não são das 183), agrometeopuglia (IT-T2-150, IT-T2-151), SIMfito (IT-T3-026);
- ISPA (IT-T5-166): fora pela D39 (robots em HTML);
- e a JANELA-FORMAS mostrou que várias das minhas PAGINA_BOLETIM são outra coisa (lista semanal,
  imagens, boletim fora do texto). A minha classe é pela prova guardada; a dela é pelo canário.

A JANELA-FORMAS **não está** na `integra-onda2-v1`; ensaio `git merge-tree`: o código junta sem
conflito (só `docs/fontes/INDICE-DE-FONTES.md` e o censo das ligações, gerados).

## 5 · Resumo das 183

| caminho | fontes |
|---|---:|
| este conserto (canário PASS medido) | +4 (22 no grupo) |
| JANELA-FORMAS (canário PASS medido) | +3 |
| JANELA-FORMAS em espera (JS) | até 4 |
| só falta leitura humana (REVISAO_PENDENTE) | 14 |
| régua, não molde (juiz diz capa com corpo ≥ 800) | 9 — não mexi |
| ordens profissionais, menus, páginas únicas, JS, duplicadas | ~120 — não são «molde errado» |

## 6 · Plano de instalação — NÃO instalar

Writeset (só o 1.º muda comportamento):
```
curadoria/reparar_contrato.py                 (familias/_junta + _so_titulos_longos)
curadoria/test_reparo_titulos_longos.py
scripts/receitas_182/*                         (extracao, classificacao, captura, medida, mutacao)
RELATORIO-RECEITAS-182.md · system-map (declarado + gerados)
```
Depois de instalado não é preciso enfileirar nada: o gatilho do robô volta a pedir REPAIR_CONTRACT
para cada CONTRACTED_CANARY_FAILED HTML 24 h depois do último reparo falhado
(`curadoria/gatilho_discovery.py:284`, `REPARO_RETOMA_S`), 20 por volta. Os 4 reparados param em
REVISAO_PENDENTE à espera de leitura, como os 14 de hoje.
