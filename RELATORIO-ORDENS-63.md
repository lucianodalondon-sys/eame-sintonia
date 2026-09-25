# RELATÓRIO — ORDENS-63 (os sites das ordens de agrónomos)

Ramo `ordens-63-v1`, a partir de `integra-onda2-v1 @ d235c32a`. **Não instalado.** Nenhum código mudou.

## O que são as 63

Da classificação da RECEITAS-182 (`receitas-182-v1`, forma SITE_DE_ORDEM_PROFISSIONAL):

| grupo | sites | o que o robô viu |
|---|---:|---|
| ordens provinciais `ordine*.conaf.it` (um sistema só, alojado pelo CONAF) | 54 | 44 só famílias de páginas fixas; 10 com item curto (223–547 letras em parágrafos) |
| federações regionais `federazione*.conaf.it` | 5 | sem família de itens |
| sites próprios (Enna, Messina, Palermo, Ragusa) | 4 | 2 sem família, 2 com item curto |

Antes de medir, procurei trabalho anterior: a P3 (23/09) mediu os sites **próprios** das ordens (Palermo, Napoli e
Cagliari têm feed) mas **não** os subdomínios `*.conaf.it`.

## A medida (1 pedido por domínio + robots pela casa, portão PASS IT; 10 pedidos no total)

`scripts/ordens_63/MEDIDA-ORDENS-V1.json`; bytes fora do Git em `C:/Users/London1/ordens-63-20260925/`, sha256 no JSON.
Para `conaf.it` — um só domínio para as 59 — o pedido foi o feed de UMA ordem com posts datados (Livorno): o feed
traz data e texto de cada post.

| grupo | o que publica | frequência | corpo | forma útil? |
|---|---|---|---|---|
| **Ordens CONAF (54) + federações (5)** | fecho de secretaria, exame de Estado, Páscoa, lista de inscritos, código deontológico, assembleia | **10 posts em 9 meses** (~1/mês) | resumo 0–169 letras; itens que o robô abriu: 223–547 | **NÃO — só institucional** |
| **Palermo** (IT-T7-226) | editais (crise hídrica, serviços florestais), lei regional, cursos, webinar «do solo aos créditos de carbono», organismos de certificação | **10 em 15 dias** (~0,7/dia) | texto inteiro 393–1 131 letras; **6 de 10 ≥ 800** | **SIM — notícias datadas com corpo** |
| **Ragusa** (IT-T7-232) | 3 notícias institucionais (tomada de posse, compêndio da profissão) | esparsas | página 411 letras | NÃO |
| **Enna** (IT-T7-210) | menus «notizie-contatti», avisos, compromissos; nada datado | — | 450 letras | NÃO (NÃO SEI se «avvisi» tem algo técnico: sem 2.º pedido) |
| **Messina** (IT-T7-221) | um único aviso, de 2023 | parado | — | NÃO |

⚠️ **Amostra:** 1 ordem de 54 para o sistema CONAF. Pesa a favor dela a prova guardada das outras: nenhuma das 44
com página fixa mostra sequer posts datados na entrada, e as 10 com item mostram avisos curtos. Mas é uma amostra.

## Receita

**Nenhuma nova.** Palermo publica na **raiz** do WordPress, e 9 dos 10 endereços do feed casam o padrão de «títulos
longos na raiz» que a RECEITAS-182 já pôs no reparo (`receitas-182-v1 @ 41d8751e`, não instalado). Duplicar seria
escrever o mesmo conserto duas vezes.

⚠️ **Palermo pode falhar o canário por azar da ordem:** o canário abre o **1.º link por ordem alfabética**, não o mais
recente. Entre os 9, o 1.º é `agenzia-delle-entrate-precisazioni…` — **478 letras**, abaixo das 800 da régua.
**NÃO SEI** o resultado sem a página de entrada (não pedida). Mede-se depois de instalar a RECEITAS-182.

## As institucionais: ficar fora com motivo — decisão do dono

As 62 sem forma útil estão em CONTRACTED_CANARY_FAILED, e o gatilho do robô volta a pedir o reparo de cada uma **a
cada 24 h** (`curadoria/gatilho_discovery.py:284`, 20 por volta). Para as 59 do CONAF isso é sempre o mesmo domínio
registável `conaf.it`: até 5 pedidos por reparo, dia após dia, para nada. O caminho para «fora com motivo» sem apagar
é a marca de catálogo `RETIRADA_POR_DECISAO` (D9, reversível) — decisão do dono, não desta bancada.
Pergunta escrita em `PERGUNTA-BOT-LUCIANO-ORDENS-63.md`.

## Resumo

| resultado | sites |
|---|---:|
| tem forma útil | **1** (Palermo) — pela receita da RECEITAS-182, canário a medir depois de instalar |
| só institucional, fica fora com motivo (pedido ao dono) | **62** (59 CONAF + Ragusa, Enna, Messina) |
