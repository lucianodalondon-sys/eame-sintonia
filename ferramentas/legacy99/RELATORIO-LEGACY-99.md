# LEGACY-99 — as 99 READY_LEGACY pela régua de hoje (DETAIL/v1)

Ramo `legacy-99-v1`, a partir de `integra-onda2-v1` @ e2f47ed3. **Não instalado; nada no vivo.** Tudo foi feito numa **cópia fiel**: vivo 7cdb7ea4 + livros de 25/09 ~09:15Z, sha256 em `0-copia-livros.sha256`.

## Em palavras simples

As 99 fontes foram aprovadas por uma régua antiga, e o portão de hoje não as deixa entrar. Passámos todas pela régua de hoje, pelo caminho oficial do robô, numa cópia.

**Resultado: das 99, só 1 vira elegível já (e entra no coletor). 3 passam a régua depois do reparo, mas esperam alguém ler a notícia. As outras 95 não passam**, e o motivo quase sempre não está nelas: está em **2 buracos do sistema**.

| Grupo | Quantas | O que acontece | Porquê |
|---|---|---|---|
| **HTML com contrato no Curator** | 26 | **1 elegível** (IT-T7-137, Accademia dei Georgofili); **3 à espera de leitura** depois do reparo (IT-T1-025, IT-T7-040, IT-T8-023); 3 NÃO SEI (robots.txt sem resposta: ligação, não fonte morta); 19 não passam | a notícia aberta não tem corpo claro (11), a capa lista menos de 2 notícias do padrão (8); o reparo da R1 recusou 16 destas: o «item» é uma página fixa (newsletter, regras, albo), a entrada é ela própria uma notícia, ou não há família de itens |
| **YouTube** | 41 | **não passam** | o contrato do Curator usa `feeds/videos.xml`, que o robots do YouTube **proíbe**. O coletor usa outra rota (a página do canal). Medido em 2, com 1 pedido cada; as 41 têm o mesmo contrato (conferido sem rede) |
| **Sem contrato no Curator** | 32 | **não passam** | fontes antigas que só existem no coletor. O Curator pára em «sem contrato», o mesmo buraco dos boletins (MICRO-PRONTO). Medido **sem rede**: 0 pedidos |

**No coletor:** a IT-T7-137 prova a rota e **entra pelo onboarding** (ENTRA=1 na cópia). ⚠️ Há outra ficha do mesmo dono, IT-T7-172 (`georgofili.info`), noutro domínio: pode ser a mesma instituição duas vezes, e a regra de duplicados não a apanha.

## 1 · Contagens e caminho canónico

- **As 99:**
  - contrato no Curator: **67** (26 HTML + 41 YouTube);
  - contrato no coletor: **74**;
  - com canário antigo guardado: **26**;
  - sem contrato no Curator: **32** (todas estas estão no coletor).
- **Caminho canónico de revalidação:**
  1. `curadoria/ready_split.py:291` `remedir()`: READY → CANARY_PENDING + VALIDATE_ROUTE;
  2. `curadoria/worker.py`: VALIDATE_ROUTE → CANARY (`canario.canario_html` abre e retrata um item);
  3. promoção só com a régua dos 4 passos (`ready_split.passos_da_promocao`, `ready_split.py:105-134`; `MINIMO_DE_LIGACOES = 2`, linha 92);
  4. se falhar: CONTRACTED_CANARY_FAILED, e o ciclo do robô manda reparar (`gatilho_discovery.py:261`, REPAIR_CONTRACT da R1). O contrato reparado só sai READY com leitura limpa (`curadoria/revisao_ready.py`, a trava da R1).
- **Porque é que o robô não as revalida sozinho:**
  - `gatilho_discovery.py:228` (`candidatas_a_revalidar`) só re-mede quem **já é ELIGIBLE** (`if sid not in elegiveis ... continue`). Uma READY_LEGACY só é re-medida se o contrato mudar (linha 223);
  - e a revalidação só corre quando a fila está quase vazia (`talvez_alimentar`, linha 429). No vivo, isso quase nunca acontece.
- **A «demotion B5»:** é a prova de que o robô **tira** do portão uma fonte elegível que começa a falhar. Foi feita numa cópia (ramo `b5-demotion-viva-v1`, 23/09): 37/37 re-medidas, ninguém saiu. **Não tem nada a ver com READY_LEGACY**: é sobre sair do portão, não sobre voltar a entrar.

## 2 · Como se mediu (a disciplina de rede)

- **Script:** `revalidar_em_rondas.py` (neste ramo). Na cópia: `remedir` e depois o worker, **rodada a rodada**, com a fila só com as fontes da rodada.
- **Rede fechada por omissão** (D41.3): o `urlopen` embrulhado falha com REDE_FECHADA. As 32 sem contrato correram assim, com **0 pedidos**.
- **Rede aberta só para as 26 HTML e a amostra YouTube**, com três guardas:
  - **1 fonte por domínio registável por rodada**;
  - **contador por domínio que recusa o 6.º pedido** (D38). Recusou 4 na rodada de reparo (teatronaturale.it ×2, parmigianoreggiano.com, edagricole.it), e essas 3 fontes foram adiadas, não chumbadas;
  - **portão de consenso PASS IT antes de cada rodada**.
- **Pedidos no total:** 72 (revalidar) + 2 (YouTube) + 68 (reparo) + 8 (continuação) + ~4 (prova de rota da IT-T7-137). Máximo de 5 por domínio por rodada.

## 3 · O que correr no vivo (decisão e execução do coordenador; um escritor)

**A. Já (1 + 3 fontes, 4 domínios diferentes, um lote só):**
```
py -c "import sys; sys.path.insert(0,'curadoria'); import ready_split as RS; print(RS.remedir(['IT-T7-137','IT-T1-025','IT-T7-040','IT-T8-023'], motivo='LEGACY-99: revalidar pela regua DETAIL/v1 (medido em copia 25/09)'))"
```
Depois o robô faz o resto sozinho:
- IT-T7-137 → READY/DETAIL/v1 → ELIGIBLE (na cópia, 1 rodada);
- as outras 3 → PASS_PARCIAL → reparo R1 → **REVISAO_PENDENTE**, à espera de leitura humana ou da IA-CUR, e aí READY.

Para a IT-T7-137 chegar ao coletor é preciso a PONTE-ONBOARD instalada (prova de rota e onboarding).

**Desfazer:** as 4 voltam ao estado de antes por uma transição nova no livro (o livro é append-only). Não se apaga nada. Se precisar, repor os livros `curadoria/LIFECYCLE-*.json` e `LIFECYCLE-QUEUE` do corte tirado antes.

**B. NÃO correr `remedir` nas outras 95:**
- **as 22 HTML** repetiriam o resultado da cópia: pedidos gastos e descida para FAILED sem ganho;
- **as 41 YouTube e as 32 sem contrato** parariam em BLOCK sem ganho (as YouTube ainda gastavam um pedido cada).

**C. Os consertos de código que faltam (as 3 bolsas grandes) — só plano:**
1. **YouTube (41):** o contrato do Curator `LOTE-YOUTUBE-FEED` (`canario.py:56`) aponta para `feeds/videos.xml` (Disallow). Tem de passar a usar a rota que o coletor já usa (página pública do canal, `CANAL_PUBLICO_YOUTUBE_V1`), e o canário do Curator tem de a saber provar.
2. **Sem contrato no Curator (32):** importar o contrato do coletor como candidata com prova. É o mesmo plano dos boletins (`ponte-onboard-v1: ferramentas/ponte_onboard/PLANO-BOLETINS-READY-LEGACY.md`). As que são PDF precisam também do ramo PDF na régua.
3. **Defeito:** o reparo rebenta com `ValueError: Invalid IPv6 URL` na IT-T12-019 (`ersaf.lombardia.it`). Hipótese, não reproduzida: um link da página com `[`, e `urlparse` sem proteção em `curadoria/reparar_contrato.py` (~linhas 160/232/238).
4. **Opcional:** `gatilho_discovery.py:228` passar a re-medir também READY_LEGACY com contrato HTML, devagar. Visto este resultado (1 em 26), **não recomendo** gastar rede nisso antes dos consertos 1 e 2.

## O que isto não prova

- Que a IT-T7-137 dá SIM (é T7, com régua; o item provado é um evento).
- Que as 3 em REVISAO_PENDENTE passam a leitura.
- O resultado YouTube das 41 foi **medido em 2** e estendido às outras pelo contrato igual. É uma inferência estrutural, não 41 medições.
