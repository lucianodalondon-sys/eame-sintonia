# AJUSTES-MICRO — Plantgest no universo errado e saltos que gastam o teto

Ramo `ajustes-micro-v1`, a partir da produção `origin/servico-20260923-0923` @ `df0865e6`.
**Rede fechada, nenhum pedido.** O vivo e a Sala não foram tocados: tudo foi lido de **cópias**,
listadas com sha256 em `INSUMOS-E-ENSAIO.txt` e `TEXTOS-DO-MICRO-FORA-DO-GIT.sha256`. A 2.ª onda
terminou às 08:25:41, antes das cópias.

## 1. Plantgest (IT-T10-021): as matérias são técnicas, a fonte está em T10

**O que o cadastro diz** (`docs/fontes/ATLAS-DE-FONTES-EAME.md:9655`): «Plantgest — banca dati varietà»,
`TERRITORY: T10`, `TOPICS: MARKET, SCIENCE, AGRICULTURAL_NEWS, CLIMATE, REGULATORY`, culturas pesco, uva,
vite e orticole. O Atlas já via que ela é mais do que mercado. O universo T10 está **no próprio
SOURCE_ID**.

**O que o conteúdo guardado diz.** Os 3 textos do MICRO foram rejulgados com a **mesma função** da
Admissão (`admissao._do_universo`), em todos os universos. Em T10 reproduzem exatamente o que a corrida
deu (NÃO, NÃO SEI «commodity», NÃO). Nos outros universos (`REJULGAR-16-DOCS-DO-MICRO.json`):

| Matéria | T10 (declarado) | T1 janela | T2 clima | T5 pesquisa | T9 |
|---|---|---|---|---|---|
| «Gelate, come scegliere il sistema antibrina» | NÃO | **SIM** | **SIM** | **SIM** | SIM |
| «MicroRna: migliori processi biologici delle piante» | NÃO SEI | NÃO SEI | NÃO | **SIM** | SIM |
| «Vigneto e cambiamento climatico» | NÃO | NÃO SEI | NÃO SEI | **SIM** | NÃO SEI |

**3 de 3 são SIM em T5 e 0 de 3 em T10.** A da geada é SIM também em **T1** (janela de cultura, D29) e em T2.

⚠️ **Ressalva.** As páginas trazem o menu do site («Notizie Agrofarmaci Fertilizzanti…») e parte das
palavras de T5/T9 pode vir do menu, não da matéria. A de T1 («nomeia uma cultura e fala de fenologia,
fioritura») tem cara de conteúdo. **Não li à mão.**

**Mudar o universo é decisão de identidade:** o T10 está no SOURCE_ID e no Atlas. Não mudei nada. A
pergunta para o bot Luciano está no fim.

### O REROUTE da D2 não existe: defeito da Admissão

A D2 do dono: `UNIVERSE_MATCH = NO · SINTONIA_RELEVANT = YES · ACTION = REROUTE` — «não descartar informação
boa só porque a fonte está na gaveta errada».

- **`admissao/admissao.py:910-925`** (`_do_universo`): quando o item «fala claramente de outro universo»,
  devolve **NÃO**, com `achado_noutro` na evidência, e **acaba aí**. Nenhum código reencaminha nem rejulga
  o item no outro universo. O único REROUTE que existe é a marca `REROUTE_POSSIVEL` do caminho T2
  (`admissao.py:883-886`).
- A Sala **já está preparada**: a identidade é (item_id, universo) «porque o mesmo documento reencaminhado
  (D2, REROUTE) a outra pergunta é outra entrada» (`admissao/sala_de_espera.py:684-686`). O que falta é
  quem reencaminhe.
- **O tamanho, medido nos 16 documentos do MICRO:** os **8 NÃO** foram todos «de outro universo».
  **4 dos 8 dariam SIM noutro universo:**
  - as 2 da Plantgest (geada em T1, T2, T5 e T9; vinha e clima em T5);
  - 2 da ARPA Marche (T5: reunião e evento sobre dados ambientais; fraco, são eventos).

  Os outros 4 (algas no mar, portal da ARPAE, dois prémios de vinho) não dão SIM em nenhum.
- **Não corrigi.** A Admissão tem dono. A correção, desenhada: quando `noutros` não está vazio, devolver
  NÃO para o universo declarado **e** marcar `d2 = REROUTE`, com os universos candidatos; um passo depois
  julga o item nesses universos e, se der SIM, entra na Sala com o outro universo. Fica uma pergunta de
  desenho para o dono da Admissão: **se der SIM em vários universos, qual vale?** A geada dá SIM em 4.

## 2. Saltos que gastam o teto (D38 intocado)

**Medição** (`ferramentas/rendimento/medir_saltos.py` → `SALTOS-DA-COORTE.json`). Cada corrida foi ligada à
sua fonte pelo RUN_ID dos estados da 1.ª onda (BC5), do MICRO e da 2.ª onda: **25 das 28 fontes têm
corrida** (IT-T2-050, IT-T2-146 e IT-T5-186/187 só aparecem saltadas por TETO_DOMINIO ou não medidas).
Desperdício = pedidos − (1 robots + 1 índice + matérias). **17 pedidos gastos em 3 ondas:**

| Tipo | Fontes | Pedidos gastos | Corrige-se pela entrada? |
|---|---|---|---|
| **Salto de origem** (o transporte leu o robots de 2 origens) | **IT-T7-021** Villoresi (`www.etvilloresi.it` → `etvilloresi.it`, 2 por corrida × 3 ondas) e **IT-T5-160** CNR IBBA (`www.ibba.cnr.it` → `ibba.cnr.it`, 2 na 2.ª onda) | 8 | **SIM** |
| **Salto no próprio robots.txt** (2 pedidos ao robots, 1 só origem, 404 no fim) | as 5 do cia.it e IT-T7-117 caf-cia.it | 8 | **NÃO**: o salto é do robots, não da entrada. Para onde salta não está no livro (medir com rede autorizada) |
| índice com 1 pedido a mais, mesma origem | IT-T5-090 ISTAT (fora da coorte) | 1 | não medido |

**A correção** (`curadoria/entrada_final.py`), pelo dono único do contrato. Usa a porta do reparo
(`curadoria/reparar_contrato.aplicar`, a mesma que o `worker.etapa_repair_contract` usa):
- **só muda a INDEX_URL**; o LINK_PATTERN fica;
- guarda a ACQUISITION anterior, passa pelo validador da casa e marca **`PRECISA_DE_REMEDIR`**. O
  canário seguinte decide; isto nunca promove;
- **só propõe com prova sem rede:** o salto de origem medido **e** um endereço já colhido na origem final
  que o LINK_PATTERN aceita. Provas: `etvilloresi.it/news/imprese/nella-darsena-di-milano-…` e
  `ibba.cnr.it/ricerca/biocel-biologia-cellulare-e-strutturale/`. ⚠️ Esta última é uma página de
  secção, não uma notícia: prova que o padrão casa com a origem, não que o alvo é bom.

**Ensaio numa cópia do livro do Curator** (`ENTRADA-FINAL-ENSAIO-NA-COPIA.json`):
- das 801 fontes, **só 2 mudam**, e só em ACQUISITION, REPARO_DE_CONTRATO, ROUTE_PROVENANCE e SOURCE_CONTRACT_HASH;
- sha `42f0d9af` → `9d674182`; **desfazer = repor o ficheiro**, e o sha volta a `42f0d9af`.

**Testes:** `tests/test_entrada_final.py` **6/0**, sem saltados. O 6.º usa o **contrato real** da
Villoresi (`tests/fixtures/entrada_final_villoresi.json`), e o validador da casa aprova-o.

**Instalar:** com o bot quieto, correr
`py curadoria/entrada_final.py --saltos=<SALTOS> --contratos=curadoria/italy_contracts_curator.json --observacoes=data/collection-ledger/italy/observations.ndjson --aplicar`
na árvore do bot. Depois, o canário das 2 (a prova tem de ser refeita, porque o sha mudou) e o
onboarding (PONTE) levam a entrada nova à tabela do coletor. **Não o fiz.**

## Pergunta curta para o bot Luciano

> A Plantgest (IT-T10-021) publica técnica agronómica: nas 3 matérias do MICRO, 3 são SIM em T5
> (pesquisa), 1 também em T1 (janela), e 0 são SIM em T10 (mercado). O que se faz?
> **A** · recatalogar a fonte como T5, com SOURCE_ID novo pela porta do Curator e retirada da T10 por decisão;
> **B** · manter T10 e ligar o REROUTE da D2 na Admissão (o item cai na gaveta certa sem mudar a fonte;
>   resolve também os outros 2 dos 8 NÃO do MICRO);
> **C** · as duas.
> Recomendo **B**. É a lei que já existe (D2), corrige a classe e não só esta fonte, e a Sala já aceita
> (item_id, universo). Falta a regra «SIM em vários universos: qual vale?».
