# VOZES-LEITURA-HUMANA — o que as 11 páginas da ronda 1 mostram, lidas à mão

> Ramo `vozes-agronomos-v1`. Missão: coordenação 11:35. **Sem rede**: só os bytes que o coordenador colheu na
> ronda 1 (`C:/Users/London1/sintonia-sala-italia/vozes-agronomos/<ID>/1_ALVO.bin`, conferidos pelo sha256 do
> `RECIBO-RONDA-1.json`). **A regra do leitor não mudou** (`ler_provas.py`: 3 SIM, 27 NAO SEI) — isto é relatório.
> Registo item a item: `data/derivados/VOZES-AGRONOMOS/LEITURA-HUMANA-RONDA-1.json`.

## Resposta curta

- **11 alvos pedidos, 10 abriram** (HTTP 200) e **1 não existe** (V18, Georgofili: a busca deu 404).
- **Nenhuma das 10 páginas prova o papel da pessoa do vídeo.** 5 são páginas iniciais genéricas, 1 é uma busca sem
  resultado, e **4 são úteis de outra forma**: CONAF (lista de artigos sobre defesa das culturas), CRPV (podcast,
  eventos e boletins técnicos), Brunello (lista de vídeos com um nome) e AMAP (o nome do responsável do serviço).
- **Nomes com papel que as páginas mostram** (não são quem fala nos vídeos): **Dott. Sandro Nardi**, referente do
  Serviço Fitossanitário da AMAP Marche (papel provado) · **Prof. José Abramo Marchese**, professor de Fisiologia
  Vegetal na Federal University of Technology, Paraná (Brasil), seminário na DAFNAE (papel provado) · **Gabriele
  Gorelli**, num vídeo do Brunello (papel NÃO SEI).
- **Relatores das séries sem nome: 0 extraídos.** Nenhuma das 5 páginas (CONAF, CRPV, Brunello, AMAP, ANBI) é o
  programa de um evento — são a porta de entrada. Os programas estão um clique adiante, e os links estão **dentro
  das páginas colhidas** (secção 3).
- **Vozes que podem entrar HOJE como fonte T7 pela porta canónica: 0.** Porque a voz não é uma fonte: é quem fala
  **dentro** de fontes que já temos (secção 4).

## 1. Os 11 alvos, um a um

| Voz | Quem se procurava | Alvo | O que a página é | Veredito humano |
|---|---|---|---|---|
| V03 | Giulia Zuecco | `dafnae.unipd.it/` (entrada) | página inicial do DAFNAE; o nome não aparece | **inútil (home)** |
| V04 | Silvia Toffolati | busca do DiSAA | «Nessun risultato trovato» | **busca sem resultado** (não prova ausência) |
| V05 | Riccardo Castaldi | `terremerse.it/` (entrada) | página inicial (serviços, «Agronomica», eventos); o nome não aparece | **inútil (home)** |
| V16 | Pietro Baroncini | `conserveitalia.it/` (entrada) | página inicial; o nome não aparece; há a secção «Attività agronomiche» | **inútil (home)** |
| V17 | Ernesto Comite | `agraria.unina.it/` (entrada) | página inicial; o nome não aparece; há «Docenti e Ricercatori» | **inútil (home)** |
| V18 | Mario Enrico Pè | busca do Georgofili | **HTTP 404** — a busca que tirámos de uma página guardada já não existe nesse endereço | **página não existe** |
| V23 | relatores CRPV | `crpv.it/` (entrada) | sem nomes; mas **PODCAST** próprio, EVENTI, e fontes T3: «Bollettini di produzione integrata», «Monitoraggio cimice asiatica», «Note tecniche 2026 difesa dalle gelate» | **útil de outra forma** |
| V24 | relatores CONAF | busca «difesa delle colture» | lista de 16 artigos: 16/05/2025 (Festival ASviS), 11/06/2024 «Razionalizzare l'uso dei fitofarmaci» («oltre 500 presenze»)… — os relatores estão no artigo | **útil de outra forma** |
| V25 | quem apresenta a «annata agronomica» | `consorziobrunellodimontalcino.it/` | lista de vídeos: «Presentation of the agronomic year 2023» (sem nome) e «Gabriele Gorelli – 2008-2018 Brunello – ten years challenge» | **útil de outra forma** |
| V26 | técnicos AMAP | `amap.marche.it/servizi/fitosanitario` | «REFERENTE: **Dott. Sandro Nardi**» (telefone e e-mail do órgão) | **útil de outra forma** |
| V30 | relatores ANBI | `anbi.it/` (entrada) | lista de eventos (Forum euromediterraneo dell'acqua, Remtech, Macfrut 2026), sem nomes | **inútil (home)** |

**Aviso para a ronda 2:** o V19 (Marina Carcea) usa **a mesma busca** do Georgofili que deu 404 no V18. **Não vale
a pena corrê-la** — gastaria 2 pedidos para um 404 esperado.

## 2. As séries sem nome: relatores

| Série | O que veio | Relatores extraídos |
|---|---|---|
| CONAF «Sostenibilità e difesa delle colture» | a lista de artigos da busca | **0** — estão no artigo «Razionalizzare l'uso dei fitofarmaci» (link na página) |
| CRPV webinars | a página inicial | **0** — a página liga a EVENTI e PODCAST |
| Brunello «annata agronomica» | a lista de vídeos | **0** para a annata (sem nome); 1 nome noutro vídeo (Gabriele Gorelli, papel NÃO SEI) |
| AMAP «mosca delle olive» | a página do serviço fitossanitário | **0** relatores; 1 responsável do serviço (Dott. Sandro Nardi) |
| ANBI «agronomia moderna» (Macfrut) | a página inicial | **0** — a página liga a EVENTI |

Não inventei nenhum relator: onde o programa não veio, fica 0.

## 3. O próximo passo de pedidos (proposta — só links que ESTÃO nas páginas colhidas)

Mesmo teto (robots.txt + 1 página por domínio por ronda), mesma regra de colisão (nenhum destes está na 4.ª onda):

| Ronda | Voz | Link (tirado da própria página) | Para quê |
|---|---|---|---|
| A | V17 Comite | `agraria.unina.it/il-dipartimento/persone/docenti-e-ricercatori` | a lista dos docentes (o papel) |
| A | V03 Zuecco | `dafnae.unipd.it/category/ruoli/personale-docente` | idem |
| A | V24 CONAF | `conaf.it/news/razionalizzare-luso-dei-fitofarmaci/` | os relatores do evento |
| A | V23 CRPV | `crpv.it/it/eventi/` | programas dos webinars |
| A | V16/V28 Conserve | `conserveitalia.it/it/attivita-agronomiche/pratiche-fitosanitarie` | quem assina a parte técnica |
| A | V25 Brunello | `consorziobrunellodimontalcino.it/it/eventi/archivio-eventi` | quem apresenta a annata |
| A | V26 AMAP | `amap.marche.it/agenzia/amministrazione-trasparente/personale` | os técnicos do serviço |
| A | V30 ANBI | `anbi.it/p/eventi` | programas |
| A | V05 Castaldi | `terremerse.it/eventi/` | idem |
| B | V03 | `dafnae.unipd.it/webinar-dafnae` | webinars com relator (2.ª página do DAFNAE) |
| B | V23 | `crpv.it/it/podcast/` | o **podcast** do CRPV — texto possível sem YouTube |

**Ronda A: 18 pedidos em 9 domínios · ronda B: 4 pedidos em 2 domínios.** Para o V04 (Toffolati), a rubrica da
UNIMI (a mesma que provou o Pierce na P5) é o caminho; o endereço exato **não** está em nenhuma página colhida —
fica DESCOBRIR.

## 4. Quem pode entrar como fonte T7 pela porta canónica, e o que falta

**Hoje: 0.** As razões, medidas:

1. **Uma voz não é uma fonte.** A porta canónica (candidata → QUALIFY → BUILD_CONTRACT → VALIDATE_ROUTE → CANÁRIO)
   aceita quem **publica uma família de itens**. Uma pessoa com uma página de perfil é uma página fixa — o canário
   recusa-a (`FAMILIA_ESTATICA`, o mesmo motivo que parou os Serviços Fitossanitários na GAPS-CANDIDATAS). As 22
   pessoas falam **dentro** de canais que **já são fontes** (IT-T8-006 L'Informatore Agrario, IT-T9-016 CAI,
   IT-T10-017 myfruit, IT-T9-014 Conserve Italia, IT-T5-038 UNINA, IT-T7-035 Georgofili, IT-T8-004 Terra e Vita…).
   O que falta à «Voci dal Campo» não é fonte nova — é o campo **`SPEAKER_ID`** (quem fala, com o papel provado)
   **nos itens** dessas fontes.
2. **Os 3 SIM não são agrónomos/técnicos italianos:** Hanspeter Felder é **diretor** de uma cooperativa (papel
   provado, mas não técnico); Bruno Basso é **professor nos EUA** (Michigan State); Simon Pierce é **investigador**
   (T6, não T7) — e o QUALIFY ainda não tem regra T6 (consertado no ramo `pesquisadores-t6-v1`, **não instalado**).
3. **Os dois nomes novos com papel provado** — Dott. Sandro Nardi (referente do Serviço Fitossanitário da AMAP) e
   Prof. José Abramo Marchese (Brasil) — também não são fonte: o Nardi é a pessoa por trás de uma fonte que **já
   está pronta** (`IT-T3-045`, SFR Marche, READY_FOR_COLLECTION); o Marchese é um item (um seminário) do DAFNAE.
4. **Os vídeos continuam sem texto:** os canais YouTube são da rota Scrap (CANAIS-41: `CANARY_PENDING`, P1 por
   fazer) e a transcrição de terceiro não abre (D53, III.I.7).

**O que falta, por ordem de ganho:**

| Falta | Quem | Nota |
|---|---|---|
| `SPEAKER_ID` + papel nos itens das fontes que já temos | Collection (extrator), depois Intelligence | as 22 pessoas estão lá; o papel prova-se pela página oficial (secção 3) |
| texto da fala | fontes com texto próprio: **podcast do CRPV**, artigos da CONAF, páginas de webinar do DAFNAE, boletins assinados | sem YouTube |
| regra T6 no QUALIFY | instalar `pesquisadores-t6-v1` | só para investigadores (Pierce, Marchese) |
| o teste dos canais pelo Scrap | CANAIS-41 (P1/P2) | para a descrição e a data dos vídeos (a `videos.list` pedida) |

**Candidatas a fonte NOVA (organizações, não pessoas) que esta leitura revelou:** o **podcast do CRPV**
(`crpv.it/it/podcast/`) e as **notícias da CONAF** (`conaf.it/news/`) — cada uma publica uma família de itens com
pessoas identificadas. Entram pela porta canónica como qualquer candidata (registo → QUALIFY → canário).

Mapa: não regerado (PRONTO-SEM-MAPA).
