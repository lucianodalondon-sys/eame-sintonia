# REND — rendimento por fonte antes da próxima onda

Missão: `auditoria-madrugada/missao-rend-coorte.txt` · ramo `rendimento-fontes-v1` (de `origin/bc4-correcoes-v1` @ cffaad2d).
Medido em 24/09/2026, 13:23–13:47 UTC (5 passagens). Nada foi escrito no vivo, no livro do coletor, no armazém ou na Sala.

## TABELA FINAL PARA A PRÓXIMA MICRO (refeita 24/09 à tarde, R1 com contratos REPARADOS)

**Em palavras simples:**

- **Podem correr já (2 fontes, 3 matérias por corrida):** IT-T10-018 myfruit (2) e IT-T7-141 CIA Toscana (1). A myfruit é também a única com **janela de cultura provada** num texto já colhido.
- **Correm logo que a R1 for instalada (2):** IT-T7-031 FederBio e IT-T7-041 Bonifica Romagna. Estas já têm contrato no coletor. ⚠️ Na IT-T7-041, o item que o canário (o teste de entrada) abriu é uma página fixa, «attività / difesa idraulica», e não uma notícia.
- **Precisam da R1 E de contrato na tabela do coletor (16):** a capa anuncia novidade, e hoje o contrato só existe no curador. 3 delas têm **sinal de suspeita** (o item aberto parece página de serviço): IT-T7-150 (curso), IT-T7-105 (serviços), IT-T5-056. ⚠️ O sinal da IT-T5-056 é **falso**: «contributo» contém «tribut», e a página é um artigo do CREA.
- **Não valem, seja qual for a novidade (26 da R1 + 13 do portão):** são de T2, T8 e T12, e estes universos não têm régua.
- **Com os contratos reparados, a R1 mudou muito:** das 40 reparadas, **37 anunciam novidade** na capa (com o contrato antigo eram só 7). 3 não se deixaram pedir: IT-T12-134 (robots.txt ilegível), IT-T5-080 (certificado do site revogado) e IT-T12-075, que gasta sozinha o teto de 5 pedidos em redireccionamentos. Uma corrida real parava no mesmo sítio.
- ⚠️ **O reparo aprova páginas que não são matéria agrícola.** Exemplos: IT-T12-042 e IT-T12-043 abriram «bollo auto / tributi» (imposto automóvel), e IT-T12-102 abriu «uffici e organizzazione». Estão todas em T12 (sem régua), por isso não mudam o veredito, mas confirmam o aviso da R1 de que o juiz de capa aprova páginas institucionais.

Como os contratos reparados foram refeitos (sem depender de pastas temporárias): uma banca `C:/rend/banca` com `git archive origin/reparo-fontes-v2` (2c083a38) e os livros do bot vivo 5c4daf5a por cima (sha256 dos 79 livros em `medidas/banca-livros-sha256.txt`). Depois `scripts/reparo/revisar_ready.py` do próprio ramo, só para as 40 A_REPARO: **40/40 READY**. Os 46 contratos ficam no ramo em `medidas/contratos-r1-reparados.json`, com a revisão (item aberto e sinais). Portão de egresso por consenso (`superficie/rede.py`): PASS IT antes e depois.

| # | Fonte | Grupo | U | Vale? | Janela de cultura | 1 corrida traz | Novas p/ coletor | Sinal da revisão R1 | Cadência sugerida |
|---|---|---|---|---|---|---|---|---|---|
| 1 | IT-T10-018 | portão | T10 | **SIM** | SIM | 2 | 2 | — | DIARIA |
| 2 | IT-T7-141 | portão | T7 | **SIM** | NAO_SEI | 1 | 11 | — | DIARIA |
| 3 | IT-T7-041 | R1 | T7 | **DEPOIS_DA_R1** | NAO | 3 | 7 | SEM_DATA | DIARIA depois da R1 |
| 4 | IT-T7-031 | R1 | T7 | **DEPOIS_DA_R1** | NAO | 1 | 6 | — | DIARIA depois da R1 |
| 5 | IT-T9-019 | R1 | T9 | **DEPOIS_DA_R1_E_DO_CONTRATO** | NAO_SEI | 3 | 19 | — | DIARIA depois da R1 e do contrato |
| 6 | IT-T9-015 | R1 | T9 | **DEPOIS_DA_R1_E_DO_CONTRATO** | NAO_SEI | 2 | 2 | — | DIARIA depois da R1 e do contrato |
| 7 | IT-T7-048 | R1 | T7 | **DEPOIS_DA_R1_E_DO_CONTRATO** | NAO_SEI | 1 | 37 | — | DIARIA depois da R1 e do contrato |
| 8 | IT-T7-049 | R1 | T7 | **DEPOIS_DA_R1_E_DO_CONTRATO** | NAO_SEI | 1 | 24 | — | DIARIA depois da R1 e do contrato |
| 9 | IT-T7-019 | R1 | T7 | **DEPOIS_DA_R1_E_DO_CONTRATO** | NAO_SEI | 1 | 20 | — | DIARIA depois da R1 e do contrato |
| 10 | IT-T3-023 | R1 | T3 | **DEPOIS_DA_R1_E_DO_CONTRATO** | NAO_SEI | 1 | 18 | — | DIARIA depois da R1 e do contrato |
| 11 | IT-T5-104 | R1 | T5 | **DEPOIS_DA_R1_E_DO_CONTRATO** | NAO_SEI | 1 | 14 | — | DIARIA depois da R1 e do contrato |
| 12 | IT-T7-163 | R1 | T7 | **DEPOIS_DA_R1_E_DO_CONTRATO** | NAO_SEI | 1 | 12 | — | DIARIA depois da R1 e do contrato |
| 13 | IT-T7-103 | R1 | T7 | **DEPOIS_DA_R1_E_DO_CONTRATO** | NAO_SEI | 1 | 11 | — | DIARIA depois da R1 e do contrato |
| 14 | IT-T5-111 | R1 | T5 | **DEPOIS_DA_R1_E_DO_CONTRATO** | NAO_SEI | 1 | 8 | SEM_DATA | DIARIA depois da R1 e do contrato |
| 15 | IT-T7-125 | R1 | T7 | **DEPOIS_DA_R1_E_DO_CONTRATO** | NAO_SEI | 1 | 5 | — | DIARIA depois da R1 e do contrato |
| 16 | IT-T5-113 | R1 | T5 | **DEPOIS_DA_R1_E_DO_CONTRATO** | NAO_SEI | 1 | 4 | SEM_DATA | DIARIA depois da R1 e do contrato |
| 17 | IT-T7-139 | R1 | T7 | **DEPOIS_DA_R1_E_DO_CONTRATO** | NAO_SEI | 1 | 3 | — | DIARIA depois da R1 e do contrato |
| 18 | IT-T7-150 | R1 | T7 | **DEPOIS_DA_R1_E_DO_CONTRATO** | NAO_SEI | 1 | 13 | CAMINHO_DE_SERVICO: corso | DIARIA depois da R1 e do contrato |
| 19 | IT-T5-056 | R1 | T5 | **DEPOIS_DA_R1_E_DO_CONTRATO** | NAO_SEI | 1 | 9 | CAMINHO_DE_SERVICO: tribut; SEM_DATA | DIARIA depois da R1 e do contrato |
| 20 | IT-T7-105 | R1 | T7 | **DEPOIS_DA_R1_E_DO_CONTRATO** | NAO_SEI | 1 | 2 | CAMINHO_DE_SERVICO: servizi | DIARIA depois da R1 e do contrato |

As outras 63 fontes (NÃO) estão na tabela completa, no fim, com o porquê de cada uma.


## Em palavras simples (1.ª medição, de manhã)

A 1.ª onda trouxe 3 SIM de 18 fontes. A pergunta era: **vale a pena correr de novo agora?**
Para responder, abrimos só a **página de entrada** de cada fonte (a «capa» do site), uma vez, pela VPN da Itália,
respeitando o robots.txt, e contámos quantos endereços de matéria ela anuncia que **o coletor nunca guardou**.

- Das **37 do portão**, só **2** trariam matéria nova numa corrida agora: **IT-T10-018 (myfruit, 2 matérias)** e **IT-T7-141 (CIA Toscana, 1)**. Juntas: **3 matérias** por corrida.
- **11 fontes anunciam novidade (128 endereços novos), mas o coletor não as vê.** O contrato manda olhar só os primeiros N links (`MAX_TARGETS`, quase sempre **1**) e esse primeiro link já está no livro. Exemplo: ISTAT (IT-T5-090) anuncia **41 novas em 42**, e uma corrida traz **0**. É como ler só a primeira linha do jornal todos os dias: se ela não muda, parece que não há notícia.
- **13 fontes nunca podem dar SIM hoje**, tenham ou não novidade: são T2, T8 e T12, e esses universos **não têm régua na Admissão** (a régua é a lista de perguntas que decide SIM/NÃO).
- **6 fontes** passaram o portão, mas **não têm contrato na tabela do coletor**: o coletor recusa-as.
- **4 fontes** não têm nada novo: tudo o que a capa mostra já está guardado.
- Das **46 que a R1 traria**, **nenhuma** corre hoje (a R1 não está instalada). Depois da R1, só **2** teriam novidade com régua e contrato no coletor (IT-T7-031, IT-T7-041). 26 são T2/T8/T12 (sem régua). 18 não têm contrato no coletor.

**Cadência sugerida (o Curator/Collection decide, a agenda não foi mexida):** diária para IT-T10-018 e IT-T7-141;
semanal para as outras da coorte até alguém rever a janela `MAX_TARGETS`; parada para quem não tem régua, contrato ou acesso.

## Ressalvas (não são detalhe)

1. «Anuncia» = endereços na capa que casam com o padrão do contrato. **Não abrimos nenhuma matéria**: alguns podem ser páginas institucionais (o juiz de capa já errou assim antes). É um teto, não uma contagem de matérias boas.
2. «Nova» = o livro do coletor (`observations.ndjson` do bot, 541 linhas) não tem documento desse endereço. A coluna `NOVAS_PARA_O_ACERVO` confere também contra os 979 endereços já guardados na Sala: deu igual em quase todas.
3. *(RESOLVIDO à tarde, ver a tabela final)* **De manhã, as 40 da R1 que precisavam de reparo foram medidas com o contrato de ANTES do reparo.** O contrato reparado só existia nas bancas temporárias da R1 (`%TEMP%\r1v3-banca-0..3`), que foram apagadas por outra sessão depois de eu as ler (antes de 13:23 UTC) e antes da medição da R1 (13:41 UTC); a hora exacta não sei. Por isso, para essas 40, o número da capa é **indicativo**. Não muda o veredito: nenhuma delas tem contrato no coletor.
4. IT-T7-141 deu `EMPTY_LIST` na BC5 de manhã e hoje a capa anuncia 11 endereços. Não sei se a capa mudou ou se foi outra coisa. Vale confirmar antes de contar com ela.
5. A régua conta pelo código instalado (fca4f2b6): T3, T4, T5, T7, T9, T10. A régua T8 do ramo `youtube-regua-t8-v1` não está instalada.
6. Cortesia: teto de 5 pedidos por site por corrida. O cia.it e o terraevita.edagricole.it precisaram de 2 a 3 passagens separadas. Total: 173 pedidos (68+5+3+93+4) em 5 passagens, egresso IT (Proton, Milão) antes e depois de cada uma.

## Retoma com a rede de volta (24/09, depois das 15:45)

As 4 fontes cujo robots.txt «não respondeu» foram repetidas com o portão de egresso por consenso (`superficie/rede.py`, bot 5c4daf5a): **PASS IT antes e depois**. Continuam paradas, e a culpa é **do site, não da nossa rede** (google.it respondeu 200 no mesmo minuto):

| Fonte | Site | O que acontece |
|---|---|---|
| IT-T7-053 | veneto.coldiretti.it | o site corta a ligação (a Coldiretti já recusava a saída Proton) |
| IT-T7-058 | unaprol.it | o site corta a ligação |
| IT-T5-080 | creafuturo.crea.gov.it | certificado do site **revogado** |
| IT-T7-049 | copagri.it | certificado emitido para **outro nome** |

Não se contorna certificado inválido. Prova: `medidas/entrada-retoma-rede.json`. A tabela não muda: as 4 já estavam «NÃO».

## Prova (a) — conferência independente da 1.ª onda na Sala real (só leitura)

`ferramentas/rendimento/conferir_1a_onda.py` → `medidas/conferencia-1a-onda.json`. Pergunta ao banco e ao disco, a partir só dos 18 RUN_ID.

| Pergunta | Esperado | Medido |
|---|---|---|
| linhas novas na sala_de_espera | 3 (66→69) | **3** (as 3 da IT-T10-018; a Sala tem 69 agora) |
| raw_asset da onda | 9 + 1 registo de falha | **9 + 1** (a falha é o JSON da IT-T7-141) |
| derived_artifact | 9 | **9** |
| ficheiro no armazém com sha256 igual ao registado | todos | **19 de 19** (10 raw + 9 derived) |
| país | IT | RUN_ID com prefixo IT **18/18** · VPN_COUNTRY=IT no livro **18/18** · `collection_run.source_country` = **NAO_SEI** (já decidido na BC4c) |

Duas coisas a saber:
- Só **6** das 18 corridas têm linha em `collection_run`, o que bate com o +6 da BC5 (396→402). As outras 12 são as corridas sem nada novo, e isto **não** está verificado linha a linha.
- O raw 1424 da IT-T7-135 é `cia.it/news/settore-comunicazione-contatti/`, uma **página de contactos**, não uma matéria. Não entrou na Sala.

## Prova (b) — as falhas do job postgres-descartavel (passo 2b5)

`medidas/prova-b-postgres-descartavel-2b5.json`. **HERDADA, não é nova.**
- O que acontece: o workflow cria um banco chamado `sala`. A guarda `guarda/banco_descartavel.py` só aceita escrever nos bancos `descartavel, derivado, social, objeto`. Recusa antes de escrever: `RECUSADO: banco fora da lista descartavel`.
- Desde quando: a mesma recusa já está em **17/09 16:20Z** (308df986). O passo já falhava desde 14/09, primeiro por outra causa (um erro de Python). Amostrámos a primeira e a última corrida vermelha de cada dia, de 17/09 a 24/09: o primeiro passo vermelho é sempre o 2b5. As 162 corridas lidas estão todas vermelhas desde 14/09.
- Em dfec8873: só o `postgres-descartavel` falha; o `portao-big-collection` e o `ponte-de-midia` passam.
- ⚠️ O job pára no primeiro passo vermelho. **Há 7 dias que os passos depois do 2b5 não correm.** Não sabemos se passariam.
- Conserto: não foi feito, porque está fora desta missão. Basta uma linha, no workflow ou na guarda. A decisão é do coordenador.

## Como se refaz

```
py ferramentas/rendimento/sala_por_fonte.py --saida C:/rend/sala.json          # Sala, só leitura
node ferramentas/rendimento/medir_entrada.mjs --arvore <bot> --ledger <bot>/data/collection-ledger/italy/observations.ndjson \
     --sala C:/rend/sala.json --curadores <bot>/curadoria/italy_contracts_curator.json --ids ... --saida X.json
py ferramentas/rendimento/tabela.py --r1 <reparo-fontes-v1>/scripts/reparo/R1-REENSAIO-ANTES-DEPOIS-fca4f2b6.json
```

Provas no ramo: `ferramentas/rendimento/medidas/*.json` (inclui `janelas.json`) (cada linha traz `INDEX_SHA256` da capa pedida) e `REND-TABELA-V1.json`.
Fora do Git (bytes das capas, não são prova primária): `C:/rend/indices/`, `C:/rend/indices-r1/`; `C:/rend/sala.json` sha256 `bc7c12377ec387830cba596e405e0770e7c3ff80357ae207b205cf6ca0deb368` (a versão sem URLs está no ramo).

## D29 — janelas de cultura (pedido do dono)

Janela = a fonte diz **quando agir**: boletim fitossanitário ou agrometeo, fase fenológica, aviso de praga, tratamento aconselhado, data de sementeira ou colheita.
Procurámos em dois sítios, **sem nova ida à rede**: as ligações da capa já pedida, e os textos já colhidos desta fonte na Sala (só leitura).

- **SIM, com prova: 3 de 83.**
  - **IT-T10-018 myfruit**: forte. Um texto já colhido dá a data de colheita da pera Conference: "de 15 de agosto até ao fim do mês; antes era 15 de setembro" (https://www.myfruit.it/news/pere-conference-il-belgio-guarda-allitalia).
  - **IT-T12-023 Regione Puglia**: média. A capa liga ao agrometeopuglia.it, que é outro site.
  - **IT-T8-034 Macchine Agricole News**: média. A capa liga à secção agrometeo do terraevita.
- **NÃO: 12**. A capa foi lida, a Sala tem textos da fonte, e nada fala de janela.
- **NÃO SEI: 68**. Destas, 21 **falam do assunto** (vindima, praga, "fitossanitário") sem janela provada. As outras não têm nenhum texto colhido e não têm nada na capa.

⚠️ Primeiro contei qualquer palavra do assunto como janela e saíram 22 SIM. Estava errado. «Vendemmia» num menu do site e «in fase di semina» num artigo sobre preços falam do assunto, mas não dizem quando agir. Separei as palavras em dois níveis. Os termos estão à vista em `janelas.py`.
⚠️ É um **indício por palavra**, não uma leitura. Uma ligação «agrometeo» na capa não prova que a fonte publique janelas com regularidade.
⚠️ O que isto quer dizer para a D29: **das 37 do portão, só a myfruit tem janela provada, e por acaso (um artigo).** Os boletins fitossanitários regionais (os SFR, Serviços Fitossanitários Regionais) aparecem aqui só como **ligação** numa capa (ex.: IT-T12-043 liga a fitosanitario.regione.lombardia.it). Nenhum SFR está no portão como fonte com contrato no coletor.

## A tabela completa, por ordem de prioridade (D29: a janela de cultura pesa)

Ordem: agora > depois da R1 > depois da R1 e do contrato > NÃO; dentro de cada degrau, sem suspeita > com suspeita, depois janela forte > média > sem prova > NÃO, depois o que uma corrida traria.

| # | Fonte | Grupo | U | Régua | Vale? | Janela de cultura | Exemplo de janela | Anuncia hoje | Novas p/ coletor | Janela do contrato | 1 corrida traz | SIM na Sala (hist.) | Cadência sugerida | Porquê |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | IT-T10-018 | portão | T10 | sim | **SIM** | SIM (forte) | https://www.myfruit.it/news/pere-conference-il-belgio-guarda-allitalia | 33 | 2 | 30 | 2 | 19 | DIARIA | 2 materia(s) nova(s) dentro da janela do contrato |
| 2 | IT-T7-141 | portão | T7 | sim | **SIM** | NAO_SEI |  | 11 | 11 | 1 | 1 | 0 | DIARIA | 1 materia(s) nova(s) dentro da janela do contrato |
| 3 | IT-T7-041 | R1 | T7 | sim | **DEPOIS_DA_R1** | NAO |  | 7 | 7 | 7 | 3 | 1 | DIARIA depois da R1 | a entrada tem novidade; corre quando a R1 for instalada e a fonte passar o portao [sinal: SEM_DATA] |
| 4 | IT-T7-031 | R1 | T7 | sim | **DEPOIS_DA_R1** | NAO |  | 6 | 6 | 1 | 1 | 0 | DIARIA depois da R1 | a entrada tem novidade; corre quando a R1 for instalada e a fonte passar o portao |
| 5 | IT-T9-019 | R1 | T9 | sim | **DEPOIS_DA_R1_E_DO_CONTRATO** | NAO_SEI |  | 19 | 19 | 19 | 3 | 0 | DIARIA depois da R1 e do contrato | a entrada tem novidade; falta a R1 E o contrato na tabela do coletor (hoje so existe no curador) |
| 6 | IT-T9-015 | R1 | T9 | sim | **DEPOIS_DA_R1_E_DO_CONTRATO** | NAO_SEI (so_tema) | https://www.conserveitalia.it/it/attivita-agronomiche/pratiche-fitosanitarie | 2 | 2 | 2 | 2 | 0 | DIARIA depois da R1 e do contrato | a entrada tem novidade; falta a R1 E o contrato na tabela do coletor (hoje so existe no curador) |
| 7 | IT-T7-048 | R1 | T7 | sim | **DEPOIS_DA_R1_E_DO_CONTRATO** | NAO_SEI |  | 37 | 37 | 1 | 1 | 0 | DIARIA depois da R1 e do contrato | a entrada tem novidade; falta a R1 E o contrato na tabela do coletor (hoje so existe no curador) |
| 8 | IT-T7-049 | R1 | T7 | sim | **DEPOIS_DA_R1_E_DO_CONTRATO** | NAO_SEI |  | 24 | 24 | 1 | 1 | 0 | DIARIA depois da R1 e do contrato | a entrada tem novidade; falta a R1 E o contrato na tabela do coletor (hoje so existe no curador) |
| 9 | IT-T7-019 | R1 | T7 | sim | **DEPOIS_DA_R1_E_DO_CONTRATO** | NAO_SEI (so_tema) | https://www.confagricolturabergamo.it/news/varie/103100/popillia-japonica-in-lombardia-al-via-gli-interventi-di-lotta-integrata.html | 20 | 20 | 1 | 1 | 0 | DIARIA depois da R1 e do contrato | a entrada tem novidade; falta a R1 E o contrato na tabela do coletor (hoje so existe no curador) |
| 10 | IT-T3-023 | R1 | T3 | sim | **DEPOIS_DA_R1_E_DO_CONTRATO** | NAO_SEI (so_tema) | https://terraevita.edagricole.it/agrofarmaci-difesa/ | 18 | 18 | 1 | 1 | 0 | DIARIA depois da R1 e do contrato | a entrada tem novidade; falta a R1 E o contrato na tabela do coletor (hoje so existe no curador) |
| 11 | IT-T5-104 | R1 | T5 | sim | **DEPOIS_DA_R1_E_DO_CONTRATO** | NAO_SEI |  | 14 | 14 | 1 | 1 | 0 | DIARIA depois da R1 e do contrato | a entrada tem novidade; falta a R1 E o contrato na tabela do coletor (hoje so existe no curador) |
| 12 | IT-T7-163 | R1 | T7 | sim | **DEPOIS_DA_R1_E_DO_CONTRATO** | NAO_SEI |  | 12 | 12 | 1 | 1 | 0 | DIARIA depois da R1 e do contrato | a entrada tem novidade; falta a R1 E o contrato na tabela do coletor (hoje so existe no curador) |
| 13 | IT-T7-103 | R1 | T7 | sim | **DEPOIS_DA_R1_E_DO_CONTRATO** | NAO_SEI |  | 11 | 11 | 1 | 1 | 0 | DIARIA depois da R1 e do contrato | a entrada tem novidade; falta a R1 E o contrato na tabela do coletor (hoje so existe no curador) |
| 14 | IT-T5-111 | R1 | T5 | sim | **DEPOIS_DA_R1_E_DO_CONTRATO** | NAO_SEI (so_tema) | https://www.crea.gov.it/web/guest/-/xylella-fastidiosa-dalla-ricerca-crea-nuove-strategie-per-l-olivicoltura | 8 | 8 | 1 | 1 | 0 | DIARIA depois da R1 e do contrato | a entrada tem novidade; falta a R1 E o contrato na tabela do coletor (hoje so existe no curador) [sinal: SEM_DATA] |
| 15 | IT-T7-125 | R1 | T7 | sim | **DEPOIS_DA_R1_E_DO_CONTRATO** | NAO_SEI |  | 5 | 5 | 1 | 1 | 0 | DIARIA depois da R1 e do contrato | a entrada tem novidade; falta a R1 E o contrato na tabela do coletor (hoje so existe no curador) |
| 16 | IT-T5-113 | R1 | T5 | sim | **DEPOIS_DA_R1_E_DO_CONTRATO** | NAO_SEI |  | 4 | 4 | 1 | 1 | 0 | DIARIA depois da R1 e do contrato | a entrada tem novidade; falta a R1 E o contrato na tabela do coletor (hoje so existe no curador) [sinal: SEM_DATA] |
| 17 | IT-T7-139 | R1 | T7 | sim | **DEPOIS_DA_R1_E_DO_CONTRATO** | NAO_SEI |  | 3 | 3 | 1 | 1 | 0 | DIARIA depois da R1 e do contrato | a entrada tem novidade; falta a R1 E o contrato na tabela do coletor (hoje so existe no curador) |
| 18 | IT-T7-150 | R1 | T7 | sim | **DEPOIS_DA_R1_E_DO_CONTRATO** | NAO_SEI |  | 13 | 13 | 1 | 1 | 0 | DIARIA depois da R1 e do contrato | a entrada tem novidade; falta a R1 E o contrato na tabela do coletor (hoje so existe no curador) [SUSPEITA: o item que o canario abriu e pagina de servico — CAMINHO_DE_SERVICO: corso; ler antes de correr] |
| 19 | IT-T5-056 | R1 | T5 | sim | **DEPOIS_DA_R1_E_DO_CONTRATO** | NAO_SEI |  | 9 | 9 | 1 | 1 | 0 | DIARIA depois da R1 e do contrato | a entrada tem novidade; falta a R1 E o contrato na tabela do coletor (hoje so existe no curador) [SUSPEITA: o item que o canario abriu e pagina de servico — CAMINHO_DE_SERVICO: tribut; SEM_DATA; ler antes de correr] |
| 20 | IT-T7-105 | R1 | T7 | sim | **DEPOIS_DA_R1_E_DO_CONTRATO** | NAO_SEI |  | 2 | 2 | 1 | 1 | 0 | DIARIA depois da R1 e do contrato | a entrada tem novidade; falta a R1 E o contrato na tabela do coletor (hoje so existe no curador) [SUSPEITA: o item que o canario abriu e pagina de servico — CAMINHO_DE_SERVICO: servizi; ler antes de correr] |
| 21 | IT-T12-023 | R1 | T12 | não | **NAO** | SIM (media) | http://www.agrometeopuglia.it/ | 17 | 17 | 1 | 1 | 0 | PARADA ate haver regua | sem regua de Admissao para T12: mesmo materia nova sai NAO_SEI, nunca SIM |
| 22 | IT-T8-034 | portão | T8 | não | **NAO** | SIM (media) | https://terraevita.edagricole.it/agrometeo/ | 5 | 5 | 1 | 1 | 0 | PARADA ate haver regua | sem regua de Admissao para T8: mesmo materia nova sai NAO_SEI, nunca SIM |
| 23 | IT-T2-070 | R1 | T2 | não | **NAO** | NAO_SEI |  | 22 | 22 | 1 | 1 | 0 | PARADA ate haver regua | sem regua de Admissao para T2: mesmo materia nova sai NAO_SEI, nunca SIM [sinal: SEM_DATA] |
| 24 | IT-T8-024 | R1 | T8 | não | **NAO** | NAO_SEI (so_tema) | https://terraevita.edagricole.it/agrofarmaci-difesa/ | 19 | 19 | 1 | 1 | 0 | PARADA ate haver regua | sem regua de Admissao para T8: mesmo materia nova sai NAO_SEI, nunca SIM |
| 25 | IT-T8-021 | portão | T8 | não | **NAO** | NAO_SEI (so_tema) | https://terraevita.edagricole.it/agrofarmaci-difesa/ | 17 | 17 | 1 | 1 | 0 | PARADA ate haver regua | sem regua de Admissao para T8: mesmo materia nova sai NAO_SEI, nunca SIM |
| 26 | IT-T8-042 | R1 | T8 | não | **NAO** | NAO_SEI (so_tema) | https://terraevita.edagricole.it/agrofarmaci-difesa/ | 15 | 15 | 1 | 1 | 0 | PARADA ate haver regua | sem regua de Admissao para T8: mesmo materia nova sai NAO_SEI, nunca SIM |
| 27 | IT-T12-131 | R1 | T12 | não | **NAO** | NAO_SEI (so_tema) | https://terraevita.edagricole.it/agrofarmaci-difesa/ | 10 | 10 | 1 | 1 | 0 | PARADA ate haver regua | sem regua de Admissao para T12: mesmo materia nova sai NAO_SEI, nunca SIM |
| 28 | IT-T12-130 | R1 | T12 | não | **NAO** | NAO_SEI (so_tema) | https://terraevita.edagricole.it/agrofarmaci-difesa/ | 9 | 9 | 1 | 1 | 0 | PARADA ate haver regua | sem regua de Admissao para T12: mesmo materia nova sai NAO_SEI, nunca SIM |
| 29 | IT-T8-051 | portão | T8 | não | **NAO** | NAO_SEI (so_tema) | https://terraevita.edagricole.it/agrofarmaci-difesa/ | 9 | 9 | 1 | 1 | 0 | PARADA ate haver regua | sem regua de Admissao para T8: mesmo materia nova sai NAO_SEI, nunca SIM |
| 30 | IT-T5-101 | portão | T5 | sim | **NAO** | NAO_SEI |  | 7 | 7 | 1 | 1 | 0 | PARADA ate o contrato chegar ao coletor | sem contrato na tabela do coletor: o coletor recusa a fonte |
| 31 | IT-T12-024 | R1 | T12 | não | **NAO** | NAO_SEI (so_tema) | http://www.regione.veneto.it/web/fitosanitario | 6 | 6 | 1 | 1 | 0 | PARADA ate haver regua | sem regua de Admissao para T12: mesmo materia nova sai NAO_SEI, nunca SIM |
| 32 | IT-T7-120 | portão | T7 | sim | **NAO** | NAO_SEI |  | 6 | 6 | 1 | 1 | 0 | PARADA ate o contrato chegar ao coletor | sem contrato na tabela do coletor: o coletor recusa a fonte |
| 33 | IT-T8-041 | R1 | T8 | não | **NAO** | NAO_SEI (so_tema) | https://vigneviniequalita.edagricole.it/territori-prodotti/langhe-vendemmia-anticipata-di-10-giorni/ | 6 | 6 | 1 | 1 | 0 | PARADA ate haver regua | sem regua de Admissao para T8: mesmo materia nova sai NAO_SEI, nunca SIM |
| 34 | IT-T12-081 | R1 | T12 | não | **NAO** | NAO_SEI |  | 5 | 5 | 1 | 1 | 0 | PARADA ate haver regua | sem regua de Admissao para T12: mesmo materia nova sai NAO_SEI, nunca SIM |
| 35 | IT-T8-029 | portão | T8 | não | **NAO** | NAO_SEI |  | 5 | 5 | 1 | 1 | 0 | PARADA ate haver regua | sem regua de Admissao para T8: mesmo materia nova sai NAO_SEI, nunca SIM |
| 36 | IT-T8-030 | portão | T8 | não | **NAO** | NAO_SEI |  | 5 | 5 | 1 | 1 | 0 | PARADA ate haver regua | sem regua de Admissao para T8: mesmo materia nova sai NAO_SEI, nunca SIM |
| 37 | IT-T2-037 | R1 | T2 | não | **NAO** | NAO_SEI |  | 4 | 4 | 1 | 1 | 0 | PARADA ate haver regua | sem regua de Admissao para T2: mesmo materia nova sai NAO_SEI, nunca SIM |
| 38 | IT-T2-050 | R1 | T2 | não | **NAO** | NAO_SEI |  | 4 | 4 | 1 | 1 | 0 | PARADA ate haver regua | sem regua de Admissao para T2: mesmo materia nova sai NAO_SEI, nunca SIM [sinal: SEM_DATA] |
| 39 | IT-T8-028 | portão | T8 | não | **NAO** | NAO_SEI (so_tema) | https://rivistafrutticoltura.edagricole.it/colture/frutta-mediterranea/mango-intelligenza-artificiale-monitorare-fenologia/ | 4 | 4 | 1 | 1 | 0 | PARADA ate haver regua | sem regua de Admissao para T8: mesmo materia nova sai NAO_SEI, nunca SIM |
| 40 | IT-T8-039 | portão | T8 | não | **NAO** | NAO_SEI |  | 4 | 4 | 1 | 1 | 0 | PARADA ate haver regua | sem regua de Admissao para T8: mesmo materia nova sai NAO_SEI, nunca SIM |
| 41 | IT-T9-021 | portão | T9 | sim | **NAO** | NAO_SEI |  | 4 | 4 | 1 | 1 | 0 | PARADA ate sair o bloqueio | a entrada tem novidade, mas a fonte esta fora da coorte: SEM_RECEITA_WEB_PARA_T9 |
| 42 | IT-T12-073 | R1 | T12 | não | **NAO** | NAO_SEI |  | 3 | 3 | 1 | 1 | 0 | PARADA ate haver regua | sem regua de Admissao para T12: mesmo materia nova sai NAO_SEI, nunca SIM [sinal: SEM_DATA] |
| 43 | IT-T12-104 | R1 | T12 | não | **NAO** | NAO_SEI |  | 3 | 3 | 1 | 1 | 0 | PARADA ate haver regua | sem regua de Admissao para T12: mesmo materia nova sai NAO_SEI, nunca SIM [sinal: SEM_DATA] |
| 44 | IT-T12-137 | portão | T12 | não | **NAO** | NAO_SEI |  | 3 | 3 | 1 | 1 | 0 | PARADA ate haver regua | sem regua de Admissao para T12: mesmo materia nova sai NAO_SEI, nunca SIM |
| 45 | IT-T8-040 | portão | T8 | não | **NAO** | NAO_SEI |  | 3 | 3 | 1 | 1 | 0 | PARADA ate haver regua | sem regua de Admissao para T8: mesmo materia nova sai NAO_SEI, nunca SIM |
| 46 | IT-T12-044 | R1 | T12 | não | **NAO** | NAO_SEI |  | 2 | 2 | 1 | 1 | 0 | PARADA ate haver regua | sem regua de Admissao para T12: mesmo materia nova sai NAO_SEI, nunca SIM |
| 47 | IT-T12-117 | R1 | T12 | não | **NAO** | NAO_SEI |  | 2 | 2 | 1 | 1 | 0 | PARADA ate haver regua | sem regua de Admissao para T12: mesmo materia nova sai NAO_SEI, nunca SIM |
| 48 | IT-T2-033 | R1 | T2 | não | **NAO** | NAO_SEI |  | 2 | 2 | 1 | 1 | 0 | PARADA ate haver regua | sem regua de Admissao para T2: mesmo materia nova sai NAO_SEI, nunca SIM |
| 49 | IT-T8-022 | R1 | T8 | não | **NAO** | NAO_SEI (so_tema) | https://terraevita.edagricole.it/agrofarmaci-difesa/ | 2 | 2 | 1 | 1 | 0 | PARADA ate haver regua | sem regua de Admissao para T8: mesmo materia nova sai NAO_SEI, nunca SIM |
| 50 | IT-T7-017 | portão | T7 | sim | **NAO** | NAO_SEI (so_tema) |  | 55 | 24 | 30 | 0 | 0 | SEMANAL ate rever a janela (MAX_TARGETS) | 24 nova(s) anunciada(s), mas FORA da janela: o contrato so olha as primeiras 30 e essas ja estao no livro |
| 51 | IT-T7-115 | portão | T7 | sim | **NAO** | NAO_SEI |  | 13 | 12 | 1 | 0 | 0 | PARADA ate o contrato chegar ao coletor | sem contrato na tabela do coletor: o coletor recusa a fonte |
| 52 | IT-T7-118 | portão | T7 | sim | **NAO** | NAO_SEI |  | 10 | 9 | 1 | 0 | 0 | SEMANAL ate rever a janela (MAX_TARGETS) | 9 nova(s) anunciada(s), mas FORA da janela: o contrato so olha as primeiras 1 e essas ja estao no livro |
| 53 | IT-T7-112 | portão | T7 | sim | **NAO** | NAO_SEI |  | 4 | 3 | 1 | 0 | 0 | SEMANAL ate rever a janela (MAX_TARGETS) | 3 nova(s) anunciada(s), mas FORA da janela: o contrato so olha as primeiras 1 e essas ja estao no livro |
| 54 | IT-T7-123 | portão | T7 | sim | **NAO** | NAO_SEI |  | 4 | 3 | 1 | 0 | 0 | SEMANAL ate rever a janela (MAX_TARGETS) | 3 nova(s) anunciada(s), mas FORA da janela: o contrato so olha as primeiras 1 e essas ja estao no livro |
| 55 | IT-T12-075 | R1 | T12 | não | **NAO** | NAO_SEI |  | — | — | 1 | — | 0 | PARADA ate haver regua | sem regua de Admissao para T12: mesmo materia nova sai NAO_SEI, nunca SIM |
| 56 | IT-T2-056 | portão | T2 | não | **NAO** | NAO_SEI |  | — | — | 1 | — | 0 | PARADA ate haver regua | sem regua de Admissao para T2: mesmo materia nova sai NAO_SEI, nunca SIM |
| 57 | IT-T2-106 | portão | T2 | não | **NAO** | NAO_SEI |  | — | — | 1 | — | 0 | PARADA ate haver regua | sem regua de Admissao para T2: mesmo materia nova sai NAO_SEI, nunca SIM |
| 58 | IT-T5-041 | R1 | T5 | sim | **NAO** | NAO_SEI |  | — | — | 6 | — | 0 | PARADA (robots/acesso) | a porta de entrada nao se deixou pedir: ROBOTS_ILEGIVEL |
| 59 | IT-T5-080 | R1 | T5 | sim | **NAO** | NAO_SEI |  | — | — | 1 | — | 0 | PARADA (robots/acesso) | a porta de entrada nao se deixou pedir: ROBOTS_INDISPONIVEL |
| 60 | IT-T7-033 | portão | T7 | sim | **NAO** | NAO_SEI (so_tema) | https://www.chianticlassico.com/vino/vendemmia/ | 15 | 0 | 15 | 0 | 1 | SEMANAL | nada novo: tudo o que a entrada anuncia ja esta no livro |
| 61 | IT-T7-042 | portão | T7 | sim | **NAO** | NAO_SEI (so_tema) |  | 10 | 0 | 10 | 0 | 0 | SEMANAL | nada novo: tudo o que a entrada anuncia ja esta no livro |
| 62 | IT-T7-043 | portão | T7 | sim | **NAO** | NAO_SEI (so_tema) |  | 2 | 0 | 2 | 0 | 0 | SEMANAL | nada novo: tudo o que a entrada anuncia ja esta no livro |
| 63 | IT-T7-053 | portão | T7 | sim | **NAO** | NAO_SEI |  | — | — | 1 | — | 0 | PARADA ate o contrato chegar ao coletor | sem contrato na tabela do coletor: o coletor recusa a fonte |
| 64 | IT-T7-058 | portão | T7 | sim | **NAO** | NAO_SEI |  | — | — | 1 | — | 0 | PARADA ate o contrato chegar ao coletor | sem contrato na tabela do coletor: o coletor recusa a fonte |
| 65 | IT-T7-100 | portão | T7 | sim | **NAO** | NAO_SEI (so_tema) | https://agrofarma.federchimica.it/news-ed-eventi/dettaglio-news/2026/06/08/agrofarma-e-federbio-lanciano-il-manifesto-per-il-biocontrollo | 2 | 0 | 1 | 0 | 0 | PARADA ate o contrato chegar ao coletor | sem contrato na tabela do coletor: o coletor recusa a fonte |
| 66 | IT-T5-090 | portão | T5 | sim | **NAO** | NAO |  | 42 | 41 | 1 | 0 | 1 | SEMANAL ate rever a janela (MAX_TARGETS) | 41 nova(s) anunciada(s), mas FORA da janela: o contrato so olha as primeiras 1 e essas ja estao no livro |
| 67 | IT-T7-021 | portão | T7 | sim | **NAO** | NAO |  | 17 | 15 | 1 | 0 | 0 | SEMANAL ate rever a janela (MAX_TARGETS) | 15 nova(s) anunciada(s), mas FORA da janela: o contrato so olha as primeiras 1 e essas ja estao no livro |
| 68 | IT-T2-034 | portão | T2 | não | **NAO** | NAO |  | 10 | 9 | 1 | 0 | 0 | PARADA ate haver regua | sem regua de Admissao para T2: mesmo materia nova sai NAO_SEI, nunca SIM |
| 69 | IT-T2-051 | portão | T2 | não | **NAO** | NAO |  | 8 | 7 | 1 | 0 | 0 | PARADA ate haver regua | sem regua de Admissao para T2: mesmo materia nova sai NAO_SEI, nunca SIM |
| 70 | IT-T7-117 | portão | T7 | sim | **NAO** | NAO |  | 7 | 6 | 1 | 0 | 0 | SEMANAL ate rever a janela (MAX_TARGETS) | 6 nova(s) anunciada(s), mas FORA da janela: o contrato so olha as primeiras 1 e essas ja estao no livro |
| 71 | IT-T10-021 | portão | T10 | sim | **NAO** | NAO |  | 4 | 3 | 1 | 0 | 0 | SEMANAL ate rever a janela (MAX_TARGETS) | 3 nova(s) anunciada(s), mas FORA da janela: o contrato so olha as primeiras 1 e essas ja estao no livro |
| 72 | IT-T7-121 | portão | T7 | sim | **NAO** | NAO |  | 4 | 3 | 1 | 0 | 0 | SEMANAL ate rever a janela (MAX_TARGETS) | 3 nova(s) anunciada(s), mas FORA da janela: o contrato so olha as primeiras 1 e essas ja estao no livro |
| 73 | IT-T7-135 | portão | T7 | sim | **NAO** | NAO |  | 5 | 3 | 1 | 0 | 0 | SEMANAL ate rever a janela (MAX_TARGETS) | 3 nova(s) anunciada(s), mas FORA da janela: o contrato so olha as primeiras 1 e essas ja estao no livro |
| 74 | IT-T5-049 | portão | T5 | sim | **NAO** | NAO |  | 5 | 1 | 4 | 0 | 4 | SEMANAL ate rever a janela (MAX_TARGETS) | 1 nova(s) anunciada(s), mas FORA da janela: o contrato so olha as primeiras 4 e essas ja estao no livro |
| 75 | IT-T10-022 | portão | T10 | sim | **NAO** | NAO |  | 9 | 0 | 14 | 0 | 0 | SEMANAL | nada novo: tudo o que a entrada anuncia ja esta no livro |
| 76 | IT-T12-102 | R1 | T12 | não | **NAO** | NAO_SEI |  | 32 | 32 | 1 | 1 | 0 | PARADA ate haver regua | sem regua de Admissao para T12: mesmo materia nova sai NAO_SEI, nunca SIM [SUSPEITA: o item que o canario abriu e pagina de servico — CAMINHO_DE_SERVICO: uffic; ler antes de correr] |
| 77 | IT-T12-043 | R1 | T12 | não | **NAO** | NAO_SEI (so_tema) | https://fitosanitario.regione.lombardia.it/wps/portal/site/sfr | 8 | 8 | 1 | 1 | 0 | PARADA ate haver regua | sem regua de Admissao para T12: mesmo materia nova sai NAO_SEI, nunca SIM [SUSPEITA: o item que o canario abriu e pagina de servico — CAMINHO_DE_SERVICO: tribut; ler antes de correr] |
| 78 | IT-T8-010 | R1 | T8 | não | **NAO** | NAO_SEI |  | 8 | 8 | 1 | 1 | 0 | PARADA ate haver regua | sem regua de Admissao para T8: mesmo materia nova sai NAO_SEI, nunca SIM [SUSPEITA: o item que o canario abriu e pagina de servico — CAMINHO_DE_SERVICO: servizi; SEM_DATA; ler antes de correr] |
| 79 | IT-T2-032 | R1 | T2 | não | **NAO** | NAO_SEI |  | 5 | 5 | 1 | 1 | 0 | PARADA ate haver regua | sem regua de Admissao para T2: mesmo materia nova sai NAO_SEI, nunca SIM [SUSPEITA: o item que o canario abriu e pagina de servico — CAMINHO_DE_SERVICO: corso; ler antes de correr] |
| 80 | IT-T12-042 | R1 | T12 | não | **NAO** | NAO_SEI (so_tema) | https://fitosanitario.regione.lombardia.it/wps/portal/site/sfr | 3 | 3 | 1 | 1 | 0 | PARADA ate haver regua | sem regua de Admissao para T12: mesmo materia nova sai NAO_SEI, nunca SIM [SUSPEITA: o item que o canario abriu e pagina de servico — CAMINHO_DE_SERVICO: tribut; ler antes de correr] |
| 81 | IT-T12-129 | R1 | T12 | não | **NAO** | NAO_SEI |  | 3 | 3 | 1 | 1 | 0 | PARADA ate haver regua | sem regua de Admissao para T12: mesmo materia nova sai NAO_SEI, nunca SIM [SUSPEITA: o item que o canario abriu e pagina de servico — CAMINHO_DE_SERVICO: tribut; ler antes de correr] |
| 82 | IT-T2-063 | R1 | T2 | não | **NAO** | NAO_SEI |  | 2 | 2 | 1 | 1 | 0 | PARADA ate haver regua | sem regua de Admissao para T2: mesmo materia nova sai NAO_SEI, nunca SIM [SUSPEITA: o item que o canario abriu e pagina de servico — CAMINHO_DE_SERVICO: accreditament; SEM_DATA; ler antes de correr] |
| 83 | IT-T12-134 | R1 | T12 | não | **NAO** | NAO_SEI |  | — | — | 1 | — | 0 | PARADA ate haver regua | sem regua de Admissao para T12: mesmo materia nova sai NAO_SEI, nunca SIM [SUSPEITA: o item que o canario abriu e pagina de servico — CAMINHO_DE_SERVICO: alunni; SEM_DATA; ler antes de correr] |

## ~~ESTACIONADO~~ → retomado no mesmo dia (FORÇA TOTAL)

Parado aqui; retoma-se depois do piloto IA-CUR e da revisão da R1. Para retomar:
1. ~~Medir de novo as 40 da R1 com o contrato REPARADO~~ **feito** (tabela final no topo). (o de hoje é o de antes do reparo; os reparados perderam-se com as bancas `%TEMP%\r1v3-banca-*`). Só faz sentido depois de a R1 ser revista/instalada ou de as bancas serem refeitas.
2. Voltar a correr `medir_entrada.mjs` nas 37 do portão (a memória do coletor muda a cada corrida) e `tabela.py`.
3. Pontos em aberto para o coordenador: rever `MAX_TARGETS` (128 novas escondidas), régua para T2/T8/T12, contrato no coletor para as fontes só do curador, e o passo 2b5 do banco-descartavel (herdado).
