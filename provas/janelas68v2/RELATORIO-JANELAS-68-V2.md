# JANELAS-68-v2 · relatório

Ramo `janelas-68-v2`, a partir de `origin/receitas-182-v1` (41d8751e). **NÃO instalado.** Vivo e Sala
não tocados (livro vivo `source-curator-service-v1` só lido, em df0865e6). Rede fechada por omissão;
rede só na sonda ARSAC (C), com portão IT por consenso antes e depois.

## A · trava no reparo: item aprovado tem de ser NOTÍCIA DATADA

- **Dono único:** `curadoria/reparar_contrato.py` — `data_de_publicacao(html)` e o passo em `inferir`
  logo a seguir a `_e_materia`. Sem data: `RECUSA ITEM_SEM_DATA_DE_PUBLICACAO` (motivo novo, declarado
  no docstring).
- **O que conta como data de publicação** (só no próprio item): meta de publicação
  (`article:published_time`, `datePublished`, `dc.date`...) · JSON-LD / `itemprop` `datePublished` ·
  «pubblicato il <data>» · data logo abaixo de um dos 5 primeiros títulos, **sem** «aggiornamento /
  modificato / revisione» ao lado. Data do dia da visita, futura ou antes de 2000 **não** prova.
- **Testes** (`curadoria/test_reparo_data_publicacao.py`, 9): os bytes reais dos 11 itens
  (`tests/fixtures/janelas68_itens`, sha256 no MANIFESTO) — os **6 falsos reprovam** com motivo, os
  **5 bons passam** com a data certa (Asnacodi 2025-12-01 e 2026-07-28, Horta 2023-05-16 ×2, Marche
  2026-03-18), pela função e pelo reparo inteiro.
- **Mudança declarada no teste antigo:** o item de exemplo de `test_reparar_contrato.py` (`CORPO`) ganhou
  a meta de publicação que uma notícia real traz; sem ela os PADRAO_NOVO antigos perdiam sentido.
- **Achado pelo teste:** a palavra «aggiornat» não apanhava «aggiornamento»; corrigido para «aggiorna».
- **Mutação 5 de 5 mortos** (`MUTACAO-TRAVA-V1.json`).
- **Medido de novo** (`REMEDICAO-COM-TRAVA-V1.json`, sem rede, os mesmos bytes, sha256 conferido,
  0 pedidos): **46 fontes** que o reparo geral já tinha medido (14 da receitas-182 + 32 da JANELAS-68).
  **Passavam 13, passam 6.** Das 7 que caíram, 6 eram páginas fixas; **1 era notícia de verdade sem data
  visível** (IT-T8-067, Società Entomologica: anúncio de congresso) — o custo honesto da regra.
- **Limite:** das 182, só estas 14 tinham sido medidas com bytes; as outras nunca passaram pelo reparo
  com rede, não há «antes» para comparar.

## B · endereço de entrada para MENU (22), PÁGINA=BOLETIM (17) e NÃO SEI (4)

- **Porta:** `curadoria/entrada_janela.py`, molde da `entrada_final.py` (AJUSTES-MICRO): proposta pura,
  só muda `INDEX_URL`, aplicada por `reparar_contrato.aplicar` (marca `PRECISA_DE_REMEDIR`).
  Prova exigida da P1g: célula `PUBLICO_COM_BOLETIM` + exemplo com DATA e `BOLETIM_REAL`, **mesmo host**,
  e **nenhum outro contrato já entra por esse endereço** (senão fazia uma gémea).
  8 testes, mutação 3 de 3.
- **Ensaio numa cópia do livro vivo (43 fontes): 0 trocas.** sha256 da cópia igual antes e depois;
  nada a pôr no canário (0 pedidos).
  - 37: a P1g não mediu boletim datado noutro endereço do mesmo site;
  - **5 teriam virado gémeas**: IT-T12-151 → IT-T3-027 (ERSA), IT-T3-046 → IT-T3-032 (Molise),
    IT-T3-051 → IT-T3-055 (VdA), IT-T3-057 e IT-T3-059 → IT-T3-058 (Veneto 2026);
  - 1 sem contrato (IT-T3-050 Umbria; a P1g provou `bollettini-fitosanitari`, mas não há contrato).
- **A premissa da missão estava metade certa:** a P1g mediu os endereços bons, mas eles **já são** a
  entrada de outra fonte. Essas 4 donas falham porque o boletim é **PDF/anexo** → rota da JANELA-FORMAS
  (que já fez a receita PDF do IT-T3-027 ERSA). As 5 da lista acima são irmãs mais fracas do mesmo
  serviço; se forem retiradas, é pelo caminho canónico, não aqui.

## C · ARSAC (IT-T2-148) → arsac.calabria.it

- **Sonda autorizada:** portão IT PASS antes e depois (IT, IT, US), robots lido (só `/wp-admin/`
  proibido), **5 pedidos no total**. Bytes fora do Git em `C:\Users\London1\j68v2-arsac-bytes`, sha256
  de cada ficheiro em `ARSAC-PROPOSTA-V1.json`.
- **Provado:** é a mesma agência (título «– ARSAC»; a edição de 4/08 aponta para os boletins antigos
  em arsacweb.it) e publica o boletim semanal — a casa lista as edições de 8, 22 e **29/09/2026**.
- **Não corrigido:** o reparo da casa, na casa nova, escolheu a família de notícias (concurso
  «Salumi di Calabria»: MIXED). A edição guardada pela JANELA-FORMAS mede MIXED, 1 033 caracteres,
  **sem data de publicação e sem PDF**: o boletim está escrito na página de cada edição → forma
  `LISTA_POR_EDICAO` da JANELA-FORMAS. Livro não tocado.
- **Erro meu:** a 1.ª rodada escolheu `/category/bandi-e-avvisi-di-gara-arssa/` («avvisi» casava; são
  concursos). Corrigido; os 2 pedidos gastos contam no teto (`ARSAC-SONDA-RODADA1-ENTRADA-ERRADA.json`).

## Coordenação com a JANELA-FORMAS

| o que | quem |
|---|---|
| IT-T3-032, IT-T3-055, IT-T3-058 (boletim PDF/anexo na entrada certa) | JANELA-FORMAS, receita PDF |
| IT-T2-148 ARSAC (uma página por edição, boletim na página) | JANELA-FORMAS, `LISTA_POR_EDICAO` |
| trava da data no reparo HTML | este ramo |

## Testes

`correr_testes.py`, cada ficheiro no seu processo, rede bloqueada (proxy 127.0.0.1:9), 16 ficheiros
(reparo, canário, worker, lifecycle, receitas):
base 41d8751e = 148 OK + 1 FAIL; ramo = 165 OK + 1 FAIL. **0 falhas novas**; a única vermelha
(`test_collection_gate ... test_todo_caminho_ate_ao_coletor_esta_declarado`) já estava vermelha na base.
