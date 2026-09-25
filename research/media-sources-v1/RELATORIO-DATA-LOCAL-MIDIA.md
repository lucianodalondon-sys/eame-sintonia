# DATA E LOCAL NAS 5 FONTES DE MÍDIA (D61/D62/D63) — só leitura, rede fechada

**Data:** 2026-09-25 · **Pedidos novos à rede:** 0. Tudo lido dos 15 bytes já guardados em `prova/` (sha256 em `PEDIDOS.jsonl`).
**Não instalado.** Nomes de campo = os que a casa já usa (`published_at` → PUBLICATION_TIME em `admissao/admissao.py:360`; `fact_time_basis`, `fact_location_basis`; regra do contrato YouTube em `curadoria/escrever_contratos.py:135-142`).

## 1. O que as páginas oficiais guardadas mostram

| Fonte | Data de publicação POR EPISÓDIO/VÍDEO | Onde está | Feed RSS | Lugar |
|---|---|---|---|---|
| CAND «TEA alle 5» (CREA) | **NÃO SEI**: a página só tem a data da notícia (08 ott 2025), não a dos 5 episódios | a página oficial só liga ao canal YouTube da CREA `UCJ8RdeFgPyGA8eyVHulEiOg` (**já na fila**); onde estão os episódios não está provado | nenhum ligado | SOURCE: CREA, Roma (rodapé). FACT: NÃO SEI |
| CAND «Agrifuturo» (CREA/Life ADA) | **NÃO SEI** por episódio; só a notícia (18 apr 2023) | a página liga ao ep. 3 no Spreaker (`spreaker.com/user/17008151/life-ada-episodio-3`), Spotify e Apple — **não abertos** | não ligado; Spreaker tem feed por show, show não identificado | SOURCE: CREA, Roma. FACT_TIME no texto: «estate 2022» (intervalo explícito). FACT_LOCATION: «Europa» (Copernicus); região NÃO SEI |
| CAND reterurale.it/podcast | **SIM, 9/9** episódios visíveis com `published_at` (ex.: 2024-09-20 07:26:29) | página do show no Spreaker, ligada pela página oficial | **anunciado**: `spreaker.com/show/5506797/episodes/feed` — robots **ALLOW**; **não aberto** → `pubDate` NÃO SEI até 1 pedido | SOURCE: Rete PAC (FEASR); cidade NÃO SEI na prova. FACT: só **1/9** cita região (Agrirobot: Basilicata, Campania) |
| CAND «Madre Terra» (Sole 24 Ore) | **SIM, mas 1 episódio** visível: «Episodio 1 · 2 dicembre 2024» (+ `slugDate` 2024-12-02, 27:51). 2023-09-28 é a data da **série**, não de um episódio | página oficial da série | **anunciado** via link Google Podcasts → `anchor.fm/s/724a46c0/podcast/rss`; robots do anchor.fm **não medido** | SOURCE: morada do editor **não está** na página guardada → NÃO SEI. FACT ep.1: «Lombardia» (projetos PSR da Regione) |
| CAND canal agrifake | **SIM por vídeo, exato** na página do vídeo: `uploadDate` 2025-05-14T09:01:03-07:00. Na página do **canal** só há datas relativas («1 anno fa»: 108 ocorrências) | 1 página por vídeo | `feeds/videos.xml?channel_id=…` — robots **DISALLOW** (medido) | SOURCE: NÃO SEI (o canal não declara país; `"gl":"IT"` na página é a NOSSA saída IT, não o canal). FACT: nunca pelo canal |

Resumo: **data por episódio provada em 3 de 5** (RRN 9/9, Madre Terra 1/1 visível, agrifake por vídeo). **Lugar do fato no texto em 3 de 5**, e sempre parcial (1/9 na RRN; 1 episódio no Madre Terra; «Europa»/«estate 2022» no Agrifuturo).

## 2. Proposta de como entrariam (D62/D63), sem instalar

1. **PUBLICATION_TIME = `published_at` do episódio/vídeo**, com base escrita: `SPREAKER_PUBLISHED_AT`, `RSS_PUBDATE`, `YT_UPLOADDATE_JSONLD`, `PAGINA_EPISODIO_TEXTO` (ex.: «2 dicembre 2024», precisão = dia).
   - Spreaker sem fuso na prova → guardar como veio, **fuso NÃO SEI** (não assumir UTC sem prova).
   - YouTube traz fuso (-07:00) → guardar como veio.
   - Data da **notícia** da CREA ≠ data do episódio → não se usa como PUBLICATION_TIME do episódio.
   - «1 anno fa» da página do canal é relativa à **nossa visita**, não à publicação → **não** vira PUBLICATION_TIME (a D63 fala de datas relativas no texto do fato, contadas a partir de uma publicação provada; esta não tem). Usar a página do vídeo.
2. **FACT_TIME** = NÃO SEI por omissão. Só com data explícita no texto do episódio (ex.: «estate 2022» → intervalo jun–ago 2022, precisão = estação) ou relativa contada a partir de PUBLICATION_TIME provada (D63/D64), com `fact_time_basis` + a expressão original.
3. **SOURCE_LOCATION** = sede do publicador **só com prova na página** (CREA: rodapé de Roma, sim; Sole 24 Ore e agrifake: NÃO SEI até haver prova).
4. **FACT_LOCATION** = só o que o texto do episódio diz (Lombardia, Basilicata/Campania), com `fact_location_basis=TEXTO_DO_EPISODIO`. Nunca pelo publicador nem pelo canal (regra que já existe no contrato YouTube). Sem menção = NÃO SEI; o item **não** é descartado (D62.2).
5. **Rota mínima para medir o resto (quando o coordenador autorizar rede):** 3 pedidos no total, 1 por domínio, com robots antes:
   - `spreaker.com/show/5506797/episodes/feed` (RRN), para provar se o RSS tem `pubDate` e descrição por episódio;
   - robots + feed do `anchor.fm/s/724a46c0` (Madre Terra), para ver quantos episódios há e com que data;
   - a página do ep. 3 do Agrifuturo no Spreaker, para achar o show e o feed.
   YouTube: só página por vídeo (feed com Disallow), dentro da D38 (máx. 5 por corrida, youtube + googlevideo somados).
6. **Continua o bloqueio de antes:** áudio de podcast não tem saída de contrato nem coletor (NOT_IMPLEMENTED). Mesmo com data e lugar, as 4 fontes de podcast só entram com uma rota de **metadados do episódio** (título, data, série, descrição), no desenho da D53, que precisa de decisão do dono.

## 3. Prioridade sugerida (depois da D61)
1. **RRN**: já tem data em 9/9 e feed com robots ALLOW → a melhor candidata.
2. **agrifake**: data exata por vídeo; a rota de vídeo já existe (D53).
3. **Madre Terra**: depende do feed anchor.fm.
4. **Agrifuturo**: série de 2023, atividade atual NÃO SEI.
5. **TEA alle 5**: onde estão os episódios NÃO SEI.
