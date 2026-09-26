# GAPS-CANDIDATAS — onde, no que já temos, estão as fontes que cruzam

> Ramo `gaps-candidatas-v1` (a partir do vivo `69b0e23f`), **só documento e registos — nenhum código do
> sistema**. Missão: `auditoria-madrugada/missao-gaps-candidatas.txt` (INT-LAW-151: a Intelligence pede
> prova, não escolhe rota; aqui é a Collection a procurar). **Sem rede**, sem coleta; o vivo e a Sala só
> lidos (`default_transaction_read_only=on`). Cópia em `auditoria-madrugada/GAPS-CANDIDATAS.md`.

## Resposta curta

- **Os tipos 1 (fitossanitário) e 4 (agrometeo) JÁ ESTÃO na casa**, quase região a região: há **76
  fontes destes tipos com contrato do Curator em `CONTRACTED_CANARY_FAILED`** — sobretudo os Serviços
  Fitossanitários (`IT-T3-022…063`) e as agrometeorologias (`IT-T2-132…159`), mais 10 da Granaria (preços). O canário não falhou por território: falhou
  pela **forma** — «a entrada não lista 2+ boletins parecidos», «só páginas fixas», «o item aberto não é
  matéria» (anexo PDF, menu). É o problema das formas da D42 (boletim em PDF; página = boletim).
- **9 fontes destes tipos já estão `READY_FOR_COLLECTION` e NÃO estão na coorte 64**: Umbria bollettini
  (IT-T3-053), SFR Marche (IT-T3-045), Marche agrometeo (IT-T2-157), ARPAS mensile (IT-T2-143), ARPAV
  agrometeo (IT-T2-002), Agrometeo Puglia (IT-T3-008), ARPAE (IT-T2-001), Granaria (IT-T10-030/035). Não
  precisam de micro-prova; precisam do canário do coletor e do onboarding. **Porque não estão na coorte:
  NÃO SEI** (a coorte é do plano C2-ONDA4; pergunta para o coordenador).
- **Lotes para a MICRO-PROVA (revistos pela D84, ver o ADENDO): lote 1 com 20 candidatas / 20 domínios / ≤ 80
  pedidos; lote 2 com 30 consorzi di difesa / 30 domínios / ≤ 120 pedidos** — `data/derivados/GAPS-CANDIDATAS/MICRO-PROVA-GAPS-LOTE1.json`, no formato do MICRO-PROVA-LOTE1.
- **Onde não há NENHUMA candidata (gap real, exige descoberta nova):** preços em 19 de 21 regiões/províncias;
  calamidade em quase todas; agrometeo da **Umbria** e do **Piemonte**; vídeo com pessoa + transcrição em
  todas. (Puglia fitossanitário e Sicília agrometeo existem mas estão fechados por robots — ver o ADENDO.)

## ADENDO D84 (coordenação 07:30) — a ordem de busca, e mais do MESMO tipo

A D84 confirma esta missão e dá a ordem: **1)** boletins fitossanitários regionais datados (serviços
oficiais, consórcios de defesa, cooperativas) · **2)** agrometeo e fenologia **com cultura** · **3)**
agrónomos com vídeo/webinar **só com pessoa identificada + transcrição**. **Não:** páginas genéricas de
universidades, anúncios de eventos, mercado sem preço. A micro-prova de hoje **aprovou** Condifesa Ravenna,
Condifesa TVB, Liguria Bollettini e LaMMA Toscana.

**O que mudou por causa da D84:**

- **Lote 1 (`MICRO-PROVA-GAPS-LOTE1.json`) passa a 20 candidatas / 20 domínios / ≤ 80 pedidos**, só tipos 1 e 2
  da D84. Saem a Granaria (preço) e o MASAF (calamidade) — não recusados, fora da ordem da D84.
- **Lote 2 novo (`MICRO-PROVA-GAPS-LOTE2-CONSORZI.json`): os 30 consorzi di difesa** que só estão na tabela da
  P1g (`origin/janelas-regioes-v1`, `curadoria/JANELAS-REGIOES-V1.json`, medida em 24/09 a partir de
  `asnacodi.it/le-sedi-condifesa/`) e ainda não são candidatas no vivo. 30 domínios, 1 ronda, ≤ 4 pedidos.
  - **Porque se re-verifica o que a P1g julgou «sem boletim datado»:** a P1g mediu a **Condifesa TVB** como
    `PUBLICO_SEM_BOLETIM_DATADO` (login na página, última data 2026-09-01) — e a micro-prova de hoje
    **aprovou-a**. A medida da P1g (data legível na página + 2 subpáginas) falha neste tipo de site.
  - ⚠️ **Esperar poucos SIM:** a lista Asnacodi é de consórcios de **seguro** (granizo, adversidades); a P1g
    viu quase todos sem aviso de defesa. A TVB prova que a P1g erra, não que os outros publicam.
  - Ordem: data recente na página primeiro (sinal de que publicam); robots ilegível no fim, com o robots.txt
    como 1.º pedido. **Condifesa Foggia** (Puglia, página com data 2026-09-24) vem primeiro — é a única pista
    fitossanitária da Puglia que está aberta.
  - Regiões **sem nenhum consórcio na lista Asnacodi**: Campania, Lazio, Liguria, Molise, Valle d'Aosta.

| # | Região | Consórcio | URL | Última data na página (P1g) | Robots (P1g) |
|---|---|---|---|---|---|
| 1 | Puglia | Condifesa Foggia | http://www.condifesafoggia.it/ | 2026-09-24 | ROBOTS_AUSENTE |
| 2 | Calabria | CODIPACAL — Consorzio di difesa Calabria | https://codipacal.it/ | 2026-09-18 | ROBOTS_200 |
| 3 | Emilia-Romagna | Condifesa Modena | https://www.condifesamodena.it/ | 2026-09-17 | ROBOTS_200 |
| 4 | Piemonte | Condifesa Vercelli Biella | https://www.condifesa-vcbi.it/ | 2026-09-16 | ROBOTS_200 |
| 5 | Lombardia | Condifesa Brescia | https://www.condifesabrescia.it/ | 2026-08-12 | ROBOTS_AUSENTE |
| 6 | Friuli Venezia Giulia | Condifesa FVG | https://www.condifesafvg.it/ | 2026-07-31 | ROBOTS_200 |
| 7 | Lombardia | CODIMA Mantova | https://www.codima.info/ | 2026-06-30 | ROBOTS_200 · login |
| 8 | Trentino-Alto Adige | CODIPRA Trento | https://www.codipratn.it/ | 2026-06-30 | ROBOTS_200 |
| 9 | Piemonte | Condifesa Cuneo | https://www.condifesacuneo.it/ | 2026-06-30 | ROBOTS_200 · login |
| 10 | Emilia-Romagna | Condifesa Emilia | https://condifesa-emilia.it/ | 2026-06-18 | ROBOTS_200 · login |
| 11 | Puglia | Agridifesa del Mediterraneo | https://agridifesadelmediterraneo.eu/ | 2026-05-15 | ROBOTS_200 · login |
| 12 | Umbria | Condifesa Umbria | https://www.condifesaumbria.it/ | 2026-05-15 | ROBOTS_200 · login |
| 13 | Piemonte | COSMAN Piemonte | https://www.cosmanpiemonte.it/ | 2026-05-15 | ROBOTS_200 |
| 14 | Trentino-Alto Adige | Hagelschutzkonsortium (Alto Adige) | https://www.hagelschutzkonsortium.com/ | 2026-04-24 | ROBOTS_200 |
| 15 | Lombardia | COPROVI | https://www.coprovi.it/ | 2026-04-03 | ROBOTS_200 |
| 16 | Veneto | CODIVE | https://www.codive.it/ | 2026-04-02 | ROBOTS_200 |
| 17 | Lombardia | Condifesa Lombardia (federazione) | https://www.condifesalombardia.it/ | 2025-11-16 | ROBOTS_200 |
| 18 | Abruzzo | CODIPE — Consorzio di difesa (Abruzzo) | https://www.codipe.it/ | nenhuma | ROBOTS_AUSENTE |
| 19 | Toscana | CODIPRA Toscano | https://www.codipratoscano.it/ | nenhuma | ROBOTS_200 |
| 20 | Basilicata | Condifesa Basilicata | https://www.condifesa-basilicata.it/ | nenhuma | ROBOTS_200 · login |
| 21 | Lombardia | Condifesa Milano Lodi | https://www.condifesa-mi-lo.it/ | nenhuma | ROBOTS_200 |
| 22 | Sardegna | Condifesa Sassari | http://www.condifesa.sassari.it/ | nenhuma | ROBOTS_AUSENTE |
| 23 | Sicilia | Condifesa Catania | https://www.condifesacatania.it/ | nenhuma | ROBOTS_200 |
| 24 | Piemonte | Condifesa Novara | https://www.condifesanovara.it/ | nenhuma | ROBOTS_200 |
| 25 | Sardegna | Condifesa Oristano | https://www.condifesaor.it/ | nenhuma | ROBOTS_AUSENTE |
| 26 | Emilia-Romagna | Condifesa (condifesa.it) | https://www.condifesa.it/ | nenhuma | ROBOTS_ILEGIVEL_URLError |
| 27 | Marche | Condifesa Ancona Macerata | https://www.condifesaanmc.it/ | nenhuma | ROBOTS_ILEGIVEL_500 |
| 28 | Sardegna | Condifesa Cagliari | https://www.condifesaca.it/home.html | nenhuma | ROBOTS_ILEGIVEL_URLError |
| 29 | Piemonte | Condifesa Piemonte | https://www.condifesapiemonte.com/ | nenhuma | ROBOTS_ILEGIVEL_URLError |
| 30 | Veneto | Condifesa Veneto Est | https://condifesavenetoest.it/ | nenhuma | ROBOTS_ILEGIVEL_403 |

- **Cooperativas (tipo 1):** nos nossos livros há ~50 pistas «cooperativa», mas quase todas são páginas da
  Confcooperative (genéricas — a D84 manda deixar). Cooperativas/OP reais (Terremerse CAND-0151, OP Alegra
  CAND-0148, Caviro CAND-0139, Conserve Italia CAND-0140, UNAPROL CAND-0152): **nenhuma prova** nos nossos livros
  de que publicam boletim técnico datado. Não entram no lote; é descoberta nova (a página de «assistenza
  tecnica» de cada uma).
- **Vídeo com pessoa identificada + transcrição (tipo 3): 0.** A YT3 (`canais-pessoas-v1`) achou 14 canais, **todos
  organizações, 0 pessoas**; os 612 vídeos guardados são só o título; a única candidata pessoa com YouTube
  (CAND-1199) não tem transcrição. Os canais institucionais candidatos (ARSAC, ASSAM, CRPV, CONAF, L'Informatore
  Agrario…) não identificam quem fala. **Gap real.**

**Correções ao que escrevi antes (a P1g já sabia):**

| Escrevi | Certo |
|---|---|
| «Serviço Fitossanitário da Puglia: nenhuma candidata» | a P1g achou 2 (SIT Puglia e emergenzaxylella) **fechadas por robots** (302); e há a **Condifesa Foggia** no lote 2 |
| «agrometeo da Sicília: nenhuma candidata» | o **SIAS** é conhecido e está **fechado daqui** (robots ilegível, URLError) |
| (Piemonte agrometeo contado com 2 pistas) | as 2 eram contas sociais da ARPA Piemonte (bloqueio de política); a P1g: `SEM_FONTE_ACHADA` — **gap real, como a Umbria** |
| «a ARSAC é a mais adiantada» | a P1g viu o último boletim da ARSAC em **2022-11-29** (arsac.calabria.it); a descoberta viu endereços com 2026 (arsacweb.it). **Não sei** qual vale — é para a micro-prova ver |

## 1. Onde procurei, e o que achei

`data/derivados/GAPS-CANDIDATAS/varrer.py.txt` → `VARRIDO.json` (1.243 pistas) e `estado.py.txt` →
`ESTADO.json` (o último estado de cada uma no livro do ciclo de vida). Lido do **vivo, só leitura**:
`candidatas/FONTES-CANDIDATAS.json` (1.199), `curadoria/italy_contracts_curator.json` (574 contratos),
`regras/italy_contracts_onboarded.json` (193), `curadoria/DISCOVERY-VISITED.json` (1.822 recusados),
`curadoria/LIFECYCLE-LEDGER-V1.json`; do ramo, `docs/fontes/ATLAS-DE-FONTES-EAME.md`; da Sala, o
`source_url` de cada bruto.

Critério: palavras do tipo no **nome, endereço e «para que serve»** (lista em `VARRIDO.json` → `TIPOS`).
A região é a do **domínio ou nome do órgão** (arpae → Emilia-Romagna, regione.veneto → Veneto…), só para
agrupar candidatas — nenhum lugar do facto sai disto.

⚠️ Erro meu, corrigido: na 1.ª corrida «arpal» (Liguria) casava dentro de «arpalazio» e «arpalombardia»;
ARPA Lazio e ARPA Lombardia saíam como Liguria. A ordem dos padrões foi corrigida e a corrida refeita.

### Região × tipo (todas as pistas dos tipos 1–4; `n(R pronta / F canário falhou / C outra)`)

| Região | 1 fitossanitário | 2 preços | 3 calamidade | 4 agrometeo |
|---|---|---|---|---|
| Piemonte | 6 (R0/F1/C5) | — | — | 2 (C2) |
| Valle d'Aosta | 6 (F3/C3) | — | — | 1 (C1) |
| Lombardia | 4 (F1/C3) | 27 (R2/F10/C15) — só Granaria | — | 8 (F2/C6) |
| Trentino (TN) | 7 (F3/C4) | — | — | 1 (C1) |
| Alto Adige (BZ) | 2 (F1/C1) | — | — | 1 (C1) |
| Veneto | 10 (F5/C5) | — | — | 9 (R1/F1/C7) |
| Friuli-Venezia Giulia | 6 (F2/C4) | — | — | 1 (C1) |
| Liguria | 8 (F2/C6) | — | — | 3 (F1/C2) |
| Emilia-Romagna | 7 (F2/C5) | (Borsa Merci Bologna, IT-T10-009) | 1 (C1, siccità ARPAE) | 9 (R1/F2/C6) |
| Toscana | 4 (F2/C2) | — | — | 8 (F3/C5) |
| Umbria | 4 (R1/C3) | — | — | **—** |
| Marche | 11 (R1/F2/C8) | — | — | 11 (R1/F2/C8) |
| Lazio | 2 (F1/C1) | — | — | 5 (F2/C3) |
| Abruzzo | 3 (C3) — endereços 404 | — | — | 2 (C2) — 404 |
| Molise | 4 (F2/C2) | — | — | 2 (F1/C1) |
| Campania | 8 (F4/C4) | — | — | 2 (F1/C1) |
| Puglia | **—** | — | — | 6 (R1/F2/C3) |
| Basilicata | 2 (F1/C1) | — | — | 2 (F1/C1) |
| Calabria | 10 (F3/C7) | — | — | 5 (F2/C3) |
| Sicilia | 5 (F2/C3) | — | — | **—** |
| Sardegna | 2 (F1/C1) | — | 2 (F1/C1, siccità ARPAS) | 7 (R1/F1/C5) |
| Nacional | 13 (SFN, ASNACODI, CREA…) | (BMTI, Terra e Vita) | 1 (MASAF declaratoria) | — |

(«C outra» = candidata ainda sem SOURCE_ID no robô, ou uma entrada do Atlas / da descoberta; várias são a
MESMA fonte vista por dois caminhos — a contagem é de pistas, não de fontes distintas.)

## 2. As candidatas do lote — URL, classe, prova, o que falta

Lote 1, revisto pela D84 (só tipos 1 e 2 da D84). Uma por região e tipo, domínios todos diferentes. A «prova que já existe» é a que está nos nossos livros
(contrato, canário, registo da candidata, a descoberta); «o que falta provar» vem do **porquê do canário**
no livro do ciclo de vida.

| # | Candidata | Região | Tipo | URL | Classe provável | Estado no robô | Prova que já existe | O que falta provar |
|---|---|---|---|---|---|---|---|---|
| 1 | CAND-0941 `IT-T2-148` | Calabria | 1+4 FITO+AGROMETEO | https://www.arsacweb.it/bollettino-agrometeorologico-e-fitosanitario-agrumi-olivo-e-vite/ | T2 | canário falhou | contrato do Curator IT-T2-148 (LOTE-HTML-ARTIGO); canario falhou em 2026-09-25; candidata registada por curadoria/pesquisadores.py (P1b) em 2026-09-25; a descoberta ja viu 3 boletins com cultura e data no proprio endereco (DISCOVERY-VISITED; HTTP_0 = falha de ligacao, nao fonte morta): bollettino-agrometeorologico-e-fitosanitario-agrumi-olivo-vite-e-kiwi-1-8-settembre-2026, limone-bollettino-difesa-fitosanitaria...valido-fino-al-30-settembre-2026, consigli-di-difesa-fitosanitaria-del-nocciolo...settembre-2026 | que o item aberto e um BOLETIM (cultura + zona + data); o canario abriu https://www.arsacweb.it/news/10/ |
| 2 | CAND-0948 `IT-T3-025` | Campania | 1 FITO | http://www.agricoltura.regione.campania.it/difesa/bollettini/bollettini_2026.html | T3 | canário falhou | contrato do Curator IT-T3-025 (LOTE-HTML-ARTIGO); canario falhou em 2026-09-25; candidata registada por curadoria/pesquisadores.py (P1b) em 2026-09-25 | a FAMILIA de itens: a entrada nao lista 2+ boletins com o mesmo esqueleto; provar onde a lista dos boletins esta (outra pagina, PDF, arquivo por ano) |
| 3 | CAND-0952 `IT-T3-028` | Emilia-Romagna | 1 FITO | https://agricoltura.regione.emilia-romagna.it/fitosanitario/difesa-sostenibile/bollettini | T3 | canário falhou | contrato do Curator IT-T3-028 (LOTE-HTML-ARTIGO); canario falhou em 2026-09-25; candidata registada por curadoria/pesquisadores.py (P1b) em 2026-09-25 | que o item aberto e um BOLETIM (cultura + zona + data); o canario abriu https://agricoltura.regione.emilia-romagna.it/fitosanitario/vivaismo-e |
| 4 | CAND-0951 `IT-T3-027` | Friuli-Venezia Giulia | 1 FITO | http://www.ersa.fvg.it/cms/aziende/in-formazione/Bollettini/index.html | T3 | canário falhou | contrato do Curator IT-T3-027 (LOTE-HTML-ARTIGO); canario falhou em 2026-09-25; candidata registada por curadoria/pesquisadores.py (P1b) em 2026-09-25 | a FAMILIA de itens: a entrada nao lista 2+ boletins com o mesmo esqueleto; provar onde a lista dos boletins esta (outra pagina, PDF, arquivo por ano) |
| 5 | CAND-0972 `IT-T3-041` | Lazio | 1 FITO | https://www.regione.lazio.it/cittadini/agricoltura/servizio-fitosanitario-regionale | T3 | canário falhou | contrato do Curator IT-T3-041 (LOTE-HTML-ARTIGO); canario falhou em 2026-09-25; candidata registada por curadoria/pesquisadores.py (P1b) em 2026-09-25 | o ALVO certo: o padrao do contrato aponta para outra seccao (revisao R1) |
| 6 | CAND-0959 `IT-T3-032` | Molise | 1 FITO | https://www.regione.molise.it/flex/cm/pages/ServeBLOB.php/L/IT/IDPagina/18077 | T3 | canário falhou | contrato do Curator IT-T3-032 (LOTE-HTML-ARTIGO); canario falhou em 2026-09-25; candidata registada por curadoria/pesquisadores.py (P1b) em 2026-09-25 | a FAMILIA de itens: a entrada nao lista 2+ boletins com o mesmo esqueleto; provar onde a lista dos boletins esta (outra pagina, PDF, arquivo por ano) |
| 7 | CAND-0961 `IT-T3-033` | Piemonte | 1 FITO | https://www.regione.piemonte.it/web/temi/agricoltura/servizi-fitosanitari-pan/bacheca-dei-bollettini | T3 | canário falhou | canario falhou em 2026-09-25; candidata registada por curadoria/pesquisadores.py (P1b) em 2026-09-25 | a FORMA: a entrada nao e HTML (PDF ou outro); provar a forma A da D42 (boletim em PDF) e a lista onde os PDF se publicam |
| 8 | CAND-0979 `IT-T3-048` | Sardegna | 1 FITO | http://www.sardegnaagricoltura.it/index.html | T3 | canário falhou | contrato do Curator IT-T3-048 (LOTE-HTML-ARTIGO); canario falhou em 2026-09-25; candidata registada por curadoria/pesquisadores.py (P1b) em 2026-09-25 | a FAMILIA de itens: a entrada nao lista 2+ boletins com o mesmo esqueleto; provar onde a lista dos boletins esta (outra pagina, PDF, arquivo por ano) |
| 9 | CAND-0985 `IT-T5-159` | Sicilia | 1 FITO | https://www.regione.sicilia.it/istituzioni/regione/strutture-regionali/assessorato-agricoltura-sviluppo-rurale-pesca-mediterranea/dipartimento-agricoltura/difesa-fitosanitaria | T5 ⚠️ | canário falhou | contrato do Curator IT-T5-159 (LOTE-HTML-ARTIGO); canario falhou em 2026-09-25; candidata registada por curadoria/pesquisadores.py (P1b) em 2026-09-25 | que o item aberto e um BOLETIM (cultura + zona + data); o canario abriu https://www.regione.sicilia.it/istituzioni/regione/assemblea-regionale |
| 10 | CAND-0981 `IT-T3-049` | Toscana | 1 FITO | https://www.regione.toscana.it/speciali/servizio-fitosanitario-regionale | T3 | canário falhou | contrato do Curator IT-T3-049 (LOTE-HTML-ARTIGO); canario falhou em 2026-09-25; candidata registada por curadoria/pesquisadores.py (P1b) em 2026-09-25 | que existe uma lista DATADA de boletins/avisos (a entrada so tem paginas fixas de servico) |
| 11 | CAND-0968 `IT-T3-038` | Trentino-Alto Adige (BZ) | 1 FITO | https://www.provincia.bz.it/agricoltura-foreste/agricoltura/default.asp | T3 | canário falhou | contrato do Curator IT-T3-038 (LOTE-HTML-ARTIGO); canario falhou em 2026-09-25; candidata registada por curadoria/pesquisadores.py (P1b) em 2026-09-25 | a FAMILIA de itens: a entrada nao lista 2+ boletins com o mesmo esqueleto; provar onde a lista dos boletins esta (outra pagina, PDF, arquivo por ano) |
| 12 | CAND-0988 `IT-T3-056` | Valle d'Aosta | 1+4 FITO+AGROMETEO | https://www.regione.vda.it/agricoltura/per_gli_agricoltori/fitosanitario/avvisi/viticoltura_i.asp | T3 | canário falhou | contrato do Curator IT-T3-056 (LOTE-HTML-ARTIGO); canario falhou em 2026-09-25; candidata registada por curadoria/pesquisadores.py (P1b) em 2026-09-25 | que o item aberto e um BOLETIM (cultura + zona + data); o canario abriu https://www.regione.vda.it/allegato.aspx?pk=126256 |
| 13 | CAND-0989 `IT-T3-058` | Veneto | 1 FITO | https://www.regione.veneto.it/web/fitosanitario/bollettini-fitosanitari-2026 | T3 | canário falhou | contrato do Curator IT-T3-058 (LOTE-HTML-ARTIGO); canario falhou em 2026-09-25; candidata registada por curadoria/pesquisadores.py (P1b) em 2026-09-25 | a pagina-indice: a entrada do contrato e um so boletim |
| 14 | CAND-0967 `IT-T3-037` | Basilicata | 1 FITO | https://www.regione.basilicata.it/giunta/site/giunta/department.jsp?dep=100049&area=104835&level=1 | T3 | canário falhou | contrato do Curator IT-T3-037 (LOTE-HTML-ARTIGO); canario falhou em 2026-09-25; candidata registada por curadoria/pesquisadores.py (P1b) em 2026-09-25 | que existe uma lista DATADA de boletins/avisos (a entrada so tem paginas fixas de servico) |
| 15 | CAND-1160 `IT-T2-136` | Lombardia | 4 AGROMETEO | https://www.arpalombardia.it/temi-ambientali/meteo-e-clima/bollettini-meteorologici/agrometeo/ | T2 | canário falhou | contrato do Curator IT-T2-136 (LOTE-HTML-ARTIGO); canario falhou em 2026-09-25; candidata registada por curadoria/janelas_regioes.py (P1g) em 2026-09-25 | que o item aberto e um BOLETIM (cultura + zona + data); o canario abriu https://www.arpalombardia.it/temi-ambientali/campi-elettromagnetici/ |
| 16 | CAND-0935 `IT-T2-141` | Sardegna | 4 AGROMETEO | http://www.sar.sardegna.it/servizi/agro/bollfenologico.asp | T2 | canário falhou | contrato do Curator IT-T2-141 (LOTE-HTML-ARTIGO); canario falhou em 2026-09-25; candidata registada por curadoria/pesquisadores.py (P1b) em 2026-09-25 | a FAMILIA de itens: a entrada nao lista 2+ boletins com o mesmo esqueleto; provar onde a lista dos boletins esta (outra pagina, PDF, arquivo por ano) |
| 17 | CAND-1170 `IT-T2-159` | Lazio | 4 AGROMETEO | https://siarl.arsial.it/ | T2 | canário falhou | contrato do Curator IT-T2-159 (LOTE-HTML-ARTIGO); canario falhou em 2026-09-25; candidata registada por curadoria/janelas_regioes.py (P1g) em 2026-09-25 | que existe uma lista DATADA de boletins/avisos (a entrada so tem paginas fixas de servico) |
| 18 | CAND-0947 `IT-T2-151` | Puglia | 4 AGROMETEO | https://www.agrometeopuglia.it/bollettini | T2 | canário falhou | contrato do Curator IT-T2-151 (LOTE-HTML-ARTIGO); canario falhou em 2026-09-25; candidata registada por curadoria/pesquisadores.py (P1b) em 2026-09-25 | que o item aberto e um BOLETIM (cultura + zona + data); o canario abriu https://www.agrometeopuglia.it/osservazioni/mappa-dati-rilevati |
| 19 | CAND-0943 `IT-T2-149` | Molise | 4 AGROMETEO | https://www.arsarp.it/category/agrometeorologia-2/ | T2 | canário falhou | contrato do Curator IT-T2-149 (LOTE-HTML-ARTIGO); canario falhou em 2026-09-25; candidata registada por curadoria/pesquisadores.py (P1b) em 2026-09-25 | que o item aberto e um BOLETIM (cultura + zona + data); o canario abriu https://www.arsarp.it/?p=1454 |
| 20 | CAND-1161 `IT-T2-138` | Emilia-Romagna | 4 AGROMETEO | https://www.arpae.it/it/temi-ambientali/meteo/dati-e-osservazioni/mappe-settimanali | T2 | canário falhou | contrato do Curator IT-T2-138 (LOTE-HTML-ARTIGO); canario falhou em 2026-09-25; candidata registada por curadoria/janelas_regioes.py (P1g) em 2026-09-25 | a FAMILIA de itens: a entrada nao lista 2+ boletins com o mesmo esqueleto; provar onde a lista dos boletins esta (outra pagina, PDF, arquivo por ano) |

⚠️ **Classe:** IT-T5-159 (Sicília) e IT-T5-157 (Calábria, fora do lote) são Serviços Fitossanitários
regionais com contrato em **T5** (pesquisa); a provável é T3. Não se muda aqui — é decisão semântica
(canal `DECISOES-SEMANTICAS`).

**O que já se sabe sem abrir nada:** a ARSAC (Calábria) é a mais adiantada — a descoberta já viu, pelo
endereço, boletins com **cultura + data** («…agrumi-olivo-vite-e-kiwi-1-8-settembre-2026»,
«limone-bollettino-difesa-fitosanitaria…valido-fino-al-30-settembre-2026», «…nocciolo…settembre-2026»);
só falhou a ligação (HTTP_0 = falha de ligação, não fonte morta).

## 3. O LOTE para a MICRO-PROVA

`data/derivados/GAPS-CANDIDATAS/MICRO-PROVA-GAPS-LOTE1.json` — o formato do `curadoria/MICRO-PROVA-LOTE1.json`
(`destravar-v1`): `CANDIDATAS`, `GRUPOS`, `CRITERIO`, `FORA_E_PORQUE`, `DOMINIOS`, mais `FICHAS` (a tabela acima).

| | |
|---|---|
| Candidatas | 20 — 1 FITO: 12 · 1+4 FITO+AGROMETEO: 2 · 4 AGROMETEO: 6 |
| Domínios | 20 distintos → **1 ronda** |
| Pedidos | **≤ 4 por domínio** (índice, 2 boletins de datas diferentes, reserva para robots/PDF) → ≤ 80 |
| O que se prova | **conteúdo e forma**, não só território: a lista datada existe? o item é um boletim com cultura, zona e data? em HTML ou PDF (D42)? |

**Fora, e porquê:**
- já no MICRO-PROVA-LOTE1: Condifesa Ravenna, Condifesa Lombardia NE, Condifesa TVB, FEM bollettini,
  Liguria bollettini, LaMMA;
- já READY (secção «Resposta curta»): só canário do coletor + onboarding;
- **robots**: SFR Lombardia (`/wps/portal`) e `fitosanitario.venezia.it` — `ROBOTS_BLOCKED` na descoberta;
- **endereço morto**: SFR e Agrometeo Abruzzo (HTTP 404, `RETRY_AFTER`) — precisam de endereço novo;
- segundo do mesmo domínio (agrometeo Campania, ASNACODI ×3) → lote 2.

**Como correr** (o coordenador; nada disto foi corrido): pela mesma ferramenta e roteiro do MICRO-PROVA-LOTE1
(`curadoria/colher_prova_territorio.py --lote=… --bytes=<fora do Git>`), VPN IT e portão de egresso PASS antes
de cada candidata. ⚠️ Essa ferramenta colhe **3 páginas por papel de território**; para prova de FORMA
(índice + boletins) os papéis são outros — ou se ajusta o lote aos papéis dela, ou a leitura humana (passo B)
lê as 3 páginas com esta pergunta. Decisão do coordenador.

## 4. Onde NÃO há candidata nenhuma (gap real — descoberta nova)

| Tipo | Onde falta | O que se viu |
|---|---|---|
| **2 · listas de preço com praça e dia** | **19 de 21** regiões/províncias | só Granaria (Milano), Borsa Merci Bologna, BMTI e Terra e Vita (nacionais). Nenhum mercado ortofrutícola grossista (Verona, Fondi, Vittoria, CAAB, SogeMi…) nem listino de câmara de comércio fora de Bologna. A myfruit (a fonte que mais rende) é revista, não praça. |
| **3 · calamidade com data, província e culturas** | todas menos o nacional | 1 declaratoria do MASAF (PDF, nacional) e 2 boletins de seca (ARPAS, ARPAE). Nenhuma lista regional de «declaratoria / delimitazione delle aree danneggiate». O IT-T12-024 (Regione Veneto, notícia de ventos fortes em Verona) mostra que o conteúdo existe dentro de notícias regionais. |
| **1 · Serviço Fitossanitário** | **Puglia** | ~~nenhuma candidata~~ — corrigido no ADENDO: SIT e emergenzaxylella fechados por robots; Condifesa Foggia no lote 2. |
| **4 · agrometeo com cultura** | **Umbria, Piemonte** | nenhuma (P1g: SEM_FONTE_ACHADA). A Sicília tem o SIAS, conhecido na P1g e fechado por robots (corrigido no ADENDO). |
| **1/4** | **Abruzzo** | há candidatas, mas os endereços dão 404: a fonte existe, o endereço é que é novo. |
| **5 · vídeo com descrição/transcrição** | todas | não é falta de fonte: os 41 canais e os canais de ARPA Lombardia, ASSAM, ARSAC, Regione Piemonte existem como candidatas; o que falta é **conteúdo** (guardamos só o título). Não se escolhe rota aqui. |

## Ficheiros (todos no ramo, só registos)

| Ficheiro | O quê |
|---|---|
| `data/derivados/GAPS-CANDIDATAS/varrer.py.txt` → `VARRIDO.json` | as 1.243 pistas, com tipo, região e origem |
| `…/estado.py.txt` → `ESTADO.json` | o último estado de cada uma no robô, e se está na coorte 64 |
| `…/lote.py.txt` → `MICRO-PROVA-GAPS-LOTE1.json` | o lote 1 (revisto pela D84) |
| `…/lote2.py.txt` → `MICRO-PROVA-GAPS-LOTE2-CONSORZI.json` | o lote 2: os 30 consorzi di difesa (lê a tabela da P1g, `.p1g.json` fora do Git: `git show origin/janelas-regioes-v1:curadoria/JANELAS-REGIOES-V1.json`) |
| `…/ler_sala.py.txt` | leitor só-leitura da Sala (DSN nunca impresso) |
