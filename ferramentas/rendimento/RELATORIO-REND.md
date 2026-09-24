# REND — rendimento por fonte antes da próxima onda

Missão: `auditoria-madrugada/missao-rend-coorte.txt` · ramo `rendimento-fontes-v1` (de `origin/bc4-correcoes-v1` @ cffaad2d).
Medido em 24/09/2026, 13:23–13:47 UTC (5 passagens). Nada foi escrito no vivo, no livro do coletor, no armazém ou na Sala.

## Em palavras simples

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
3. **As 40 da R1 que precisavam de reparo foram medidas com o contrato de ANTES do reparo.** O contrato reparado só existia nas bancas temporárias da R1 (`%TEMP%\r1v3-banca-0..3`), que foram apagadas por outra sessão depois de eu as ler (antes de 13:23 UTC) e antes da medição da R1 (13:41 UTC); a hora exacta não sei. Por isso, para essas 40, o número da capa é **indicativo**. Não muda o veredito: nenhuma delas tem contrato no coletor.
4. IT-T7-141 deu `EMPTY_LIST` na BC5 de manhã e hoje a capa anuncia 11 endereços. Não sei se a capa mudou ou se foi outra coisa. Vale confirmar antes de contar com ela.
5. A régua conta pelo código instalado (fca4f2b6): T3, T4, T5, T7, T9, T10. A régua T8 do ramo `youtube-regua-t8-v1` não está instalada.
6. Cortesia: teto de 5 pedidos por site por corrida. O cia.it e o terraevita.edagricole.it precisaram de 2 a 3 passagens separadas. Total: 173 pedidos (68+5+3+93+4) em 5 passagens, egresso IT (Proton, Milão) antes e depois de cada uma.

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

## A tabela, por ordem de prioridade (D29: a janela de cultura pesa)

Ordem: 1.º quem vale correr agora, 2.º quem vale depois da R1, 3.º o resto; dentro de cada degrau, janela forte > média > sem prova > NÃO; depois o que uma corrida traria.

| # | Fonte | Grupo | U | Régua | Vale agora? | Janela de cultura | Exemplo de janela | Anuncia hoje | Novas p/ coletor | Janela do contrato | 1 corrida traz | SIM na Sala (hist.) | Cadência sugerida | Porquê |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | IT-T10-018 | portão | T10 | sim | **SIM** | SIM (forte) | https://www.myfruit.it/news/pere-conference-il-belgio-guarda-allitalia | 33 | 2 | 30 | 2 | 19 | DIARIA | 2 materia(s) nova(s) dentro da janela do contrato |
| 2 | IT-T7-141 | portão | T7 | sim | **SIM** | NAO_SEI |  | 11 | 11 | 1 | 1 | 0 | DIARIA | 1 materia(s) nova(s) dentro da janela do contrato |
| 3 | IT-T7-041 | R1 | T7 | sim | **DEPOIS_DA_R1** | NAO |  | 7 | 7 | 7 | 3 | 1 | DIARIA depois da R1 | a entrada tem novidade; so corre quando a R1 for instalada e a fonte passar o portao [medido com o contrato de ANTES do reparo: o reparado so existia nas bancas da R1, apagadas antes desta medicao] |
| 4 | IT-T7-031 | R1 | T7 | sim | **DEPOIS_DA_R1** | NAO |  | 6 | 6 | 1 | 1 | 0 | DIARIA depois da R1 | a entrada tem novidade; so corre quando a R1 for instalada e a fonte passar o portao |
| 5 | IT-T12-023 | R1 | T12 | não | **NAO** | SIM (media) | http://www.agrometeopuglia.it/ | 13 | 13 | 1 | 1 | 0 | PARADA ate haver regua | sem regua de Admissao para T12: mesmo materia nova sai NAO_SEI, nunca SIM [medido com o contrato de ANTES do reparo: o reparado so existia nas bancas da R1, apagadas antes desta medicao] |
| 6 | IT-T8-034 | portão | T8 | não | **NAO** | SIM (media) | https://terraevita.edagricole.it/agrometeo/ | 5 | 5 | 1 | 1 | 0 | PARADA ate haver regua | sem regua de Admissao para T8: mesmo materia nova sai NAO_SEI, nunca SIM |
| 7 | IT-T9-019 | R1 | T9 | sim | **NAO** | NAO_SEI |  | 19 | 19 | 19 | 3 | 0 | PARADA ate o contrato chegar ao coletor | sem contrato na tabela do coletor: o coletor recusa a fonte |
| 8 | IT-T9-015 | R1 | T9 | sim | **NAO** | NAO_SEI (so_tema) | https://www.conserveitalia.it/it/attivita-agronomiche/pratiche-fitosanitarie | 2 | 2 | 2 | 2 | 0 | PARADA ate o contrato chegar ao coletor | sem contrato na tabela do coletor: o coletor recusa a fonte |
| 9 | IT-T8-021 | portão | T8 | não | **NAO** | NAO_SEI (so_tema) | https://terraevita.edagricole.it/agrofarmaci-difesa/ | 17 | 17 | 1 | 1 | 0 | PARADA ate haver regua | sem regua de Admissao para T8: mesmo materia nova sai NAO_SEI, nunca SIM |
| 10 | IT-T8-041 | R1 | T8 | não | **NAO** | NAO_SEI (so_tema) | https://vigneviniequalita.edagricole.it/territori-prodotti/langhe-vendemmia-anticipata-di-10-giorni/ | 15 | 15 | 1 | 1 | 0 | PARADA ate haver regua | sem regua de Admissao para T8: mesmo materia nova sai NAO_SEI, nunca SIM [medido com o contrato de ANTES do reparo: o reparado so existia nas bancas da R1, apagadas antes desta medicao] |
| 11 | IT-T8-051 | portão | T8 | não | **NAO** | NAO_SEI (so_tema) | https://terraevita.edagricole.it/agrofarmaci-difesa/ | 9 | 9 | 1 | 1 | 0 | PARADA ate haver regua | sem regua de Admissao para T8: mesmo materia nova sai NAO_SEI, nunca SIM |
| 12 | IT-T2-037 | R1 | T2 | não | **NAO** | NAO_SEI |  | 8 | 8 | 1 | 1 | 0 | PARADA ate haver regua | sem regua de Admissao para T2: mesmo materia nova sai NAO_SEI, nunca SIM [medido com o contrato de ANTES do reparo: o reparado so existia nas bancas da R1, apagadas antes desta medicao] |
| 13 | IT-T5-101 | portão | T5 | sim | **NAO** | NAO_SEI |  | 7 | 7 | 1 | 1 | 0 | PARADA ate o contrato chegar ao coletor | sem contrato na tabela do coletor: o coletor recusa a fonte |
| 14 | IT-T12-024 | R1 | T12 | não | **NAO** | NAO_SEI (so_tema) | http://www.regione.veneto.it/web/fitosanitario | 6 | 6 | 1 | 1 | 0 | PARADA ate haver regua | sem regua de Admissao para T12: mesmo materia nova sai NAO_SEI, nunca SIM |
| 15 | IT-T7-120 | portão | T7 | sim | **NAO** | NAO_SEI |  | 6 | 6 | 1 | 1 | 0 | PARADA ate o contrato chegar ao coletor | sem contrato na tabela do coletor: o coletor recusa a fonte |
| 16 | IT-T8-029 | portão | T8 | não | **NAO** | NAO_SEI |  | 5 | 5 | 1 | 1 | 0 | PARADA ate haver regua | sem regua de Admissao para T8: mesmo materia nova sai NAO_SEI, nunca SIM |
| 17 | IT-T8-030 | portão | T8 | não | **NAO** | NAO_SEI |  | 5 | 5 | 1 | 1 | 0 | PARADA ate haver regua | sem regua de Admissao para T8: mesmo materia nova sai NAO_SEI, nunca SIM |
| 18 | IT-T2-050 | R1 | T2 | não | **NAO** | NAO_SEI |  | 4 | 4 | 1 | 1 | 0 | PARADA ate haver regua | sem regua de Admissao para T2: mesmo materia nova sai NAO_SEI, nunca SIM [medido com o contrato de ANTES do reparo: o reparado so existia nas bancas da R1, apagadas antes desta medicao] |
| 19 | IT-T8-028 | portão | T8 | não | **NAO** | NAO_SEI (so_tema) | https://rivistafrutticoltura.edagricole.it/colture/frutta-mediterranea/mango-intelligenza-artificiale-monitorare-fenologia/ | 4 | 4 | 1 | 1 | 0 | PARADA ate haver regua | sem regua de Admissao para T8: mesmo materia nova sai NAO_SEI, nunca SIM |
| 20 | IT-T8-039 | portão | T8 | não | **NAO** | NAO_SEI |  | 4 | 4 | 1 | 1 | 0 | PARADA ate haver regua | sem regua de Admissao para T8: mesmo materia nova sai NAO_SEI, nunca SIM |
| 21 | IT-T9-021 | portão | T9 | sim | **NAO** | NAO_SEI |  | 4 | 4 | 1 | 1 | 0 | PARADA ate sair o bloqueio | a entrada tem novidade, mas a fonte esta fora da coorte: SEM_RECEITA_WEB_PARA_T9 |
| 22 | IT-T12-137 | portão | T12 | não | **NAO** | NAO_SEI |  | 3 | 3 | 1 | 1 | 0 | PARADA ate haver regua | sem regua de Admissao para T12: mesmo materia nova sai NAO_SEI, nunca SIM |
| 23 | IT-T8-040 | portão | T8 | não | **NAO** | NAO_SEI |  | 3 | 3 | 1 | 1 | 0 | PARADA ate haver regua | sem regua de Admissao para T8: mesmo materia nova sai NAO_SEI, nunca SIM |
| 24 | IT-T12-117 | R1 | T12 | não | **NAO** | NAO_SEI |  | 2 | 2 | 1 | 1 | 0 | PARADA ate haver regua | sem regua de Admissao para T12: mesmo materia nova sai NAO_SEI, nunca SIM |
| 25 | IT-T7-103 | R1 | T7 | sim | **NAO** | NAO_SEI |  | 1 | 1 | 1 | 1 | 0 | PARADA ate o contrato chegar ao coletor | sem contrato na tabela do coletor: o coletor recusa a fonte [medido com o contrato de ANTES do reparo: o reparado so existia nas bancas da R1, apagadas antes desta medicao] |
| 26 | IT-T7-150 | R1 | T7 | sim | **NAO** | NAO_SEI |  | 1 | 1 | 1 | 1 | 0 | PARADA ate o contrato chegar ao coletor | sem contrato na tabela do coletor: o coletor recusa a fonte [medido com o contrato de ANTES do reparo: o reparado so existia nas bancas da R1, apagadas antes desta medicao] |
| 27 | IT-T7-017 | portão | T7 | sim | **NAO** | NAO_SEI (so_tema) |  | 55 | 24 | 30 | 0 | 0 | SEMANAL ate rever a janela (MAX_TARGETS) | 24 nova(s) anunciada(s), mas FORA da janela: o contrato so olha as primeiras 30 e essas ja estao no livro |
| 28 | IT-T7-115 | portão | T7 | sim | **NAO** | NAO_SEI |  | 13 | 12 | 1 | 0 | 0 | PARADA ate o contrato chegar ao coletor | sem contrato na tabela do coletor: o coletor recusa a fonte |
| 29 | IT-T7-118 | portão | T7 | sim | **NAO** | NAO_SEI |  | 10 | 9 | 1 | 0 | 0 | SEMANAL ate rever a janela (MAX_TARGETS) | 9 nova(s) anunciada(s), mas FORA da janela: o contrato so olha as primeiras 1 e essas ja estao no livro |
| 30 | IT-T7-112 | portão | T7 | sim | **NAO** | NAO_SEI |  | 4 | 3 | 1 | 0 | 0 | SEMANAL ate rever a janela (MAX_TARGETS) | 3 nova(s) anunciada(s), mas FORA da janela: o contrato so olha as primeiras 1 e essas ja estao no livro |
| 31 | IT-T7-123 | portão | T7 | sim | **NAO** | NAO_SEI |  | 4 | 3 | 1 | 0 | 0 | SEMANAL ate rever a janela (MAX_TARGETS) | 3 nova(s) anunciada(s), mas FORA da janela: o contrato so olha as primeiras 1 e essas ja estao no livro |
| 32 | IT-T12-042 | R1 | T12 | não | **NAO** | NAO_SEI |  | — | — | 1 | — | 0 | PARADA ate haver regua | sem regua de Admissao para T12: mesmo materia nova sai NAO_SEI, nunca SIM [medido com o contrato de ANTES do reparo: o reparado so existia nas bancas da R1, apagadas antes desta medicao] |
| 33 | IT-T12-043 | R1 | T12 | não | **NAO** | NAO_SEI (so_tema) | https://fitosanitario.regione.lombardia.it/wps/portal/site/sfr | 0 | — | 1 | — | 0 | PARADA ate haver regua | sem regua de Admissao para T12: mesmo materia nova sai NAO_SEI, nunca SIM [medido com o contrato de ANTES do reparo: o reparado so existia nas bancas da R1, apagadas antes desta medicao] |
| 34 | IT-T12-044 | R1 | T12 | não | **NAO** | NAO_SEI |  | 0 | — | 1 | — | 0 | PARADA ate haver regua | sem regua de Admissao para T12: mesmo materia nova sai NAO_SEI, nunca SIM [medido com o contrato de ANTES do reparo: o reparado so existia nas bancas da R1, apagadas antes desta medicao] |
| 35 | IT-T12-073 | R1 | T12 | não | **NAO** | NAO_SEI |  | 0 | — | 1 | — | 0 | PARADA ate haver regua | sem regua de Admissao para T12: mesmo materia nova sai NAO_SEI, nunca SIM [medido com o contrato de ANTES do reparo: o reparado so existia nas bancas da R1, apagadas antes desta medicao] |
| 36 | IT-T12-075 | R1 | T12 | não | **NAO** | NAO_SEI |  | 0 | — | 1 | — | 0 | PARADA ate haver regua | sem regua de Admissao para T12: mesmo materia nova sai NAO_SEI, nunca SIM [medido com o contrato de ANTES do reparo: o reparado so existia nas bancas da R1, apagadas antes desta medicao] |
| 37 | IT-T12-081 | R1 | T12 | não | **NAO** | NAO_SEI |  | 0 | — | 1 | — | 0 | PARADA ate haver regua | sem regua de Admissao para T12: mesmo materia nova sai NAO_SEI, nunca SIM [medido com o contrato de ANTES do reparo: o reparado so existia nas bancas da R1, apagadas antes desta medicao] |
| 38 | IT-T12-102 | R1 | T12 | não | **NAO** | NAO_SEI |  | 0 | — | 1 | — | 0 | PARADA ate haver regua | sem regua de Admissao para T12: mesmo materia nova sai NAO_SEI, nunca SIM [medido com o contrato de ANTES do reparo: o reparado so existia nas bancas da R1, apagadas antes desta medicao] |
| 39 | IT-T12-104 | R1 | T12 | não | **NAO** | NAO_SEI |  | 0 | — | 1 | — | 0 | PARADA ate haver regua | sem regua de Admissao para T12: mesmo materia nova sai NAO_SEI, nunca SIM [medido com o contrato de ANTES do reparo: o reparado so existia nas bancas da R1, apagadas antes desta medicao] |
| 40 | IT-T12-129 | R1 | T12 | não | **NAO** | NAO_SEI |  | 0 | — | 1 | — | 0 | PARADA ate haver regua | sem regua de Admissao para T12: mesmo materia nova sai NAO_SEI, nunca SIM [medido com o contrato de ANTES do reparo: o reparado so existia nas bancas da R1, apagadas antes desta medicao] |
| 41 | IT-T12-130 | R1 | T12 | não | **NAO** | NAO_SEI (so_tema) | https://terraevita.edagricole.it/agrofarmaci-difesa/ | 0 | — | 1 | — | 0 | PARADA ate haver regua | sem regua de Admissao para T12: mesmo materia nova sai NAO_SEI, nunca SIM [medido com o contrato de ANTES do reparo: o reparado so existia nas bancas da R1, apagadas antes desta medicao] |
| 42 | IT-T12-131 | R1 | T12 | não | **NAO** | NAO_SEI (so_tema) | https://terraevita.edagricole.it/agrofarmaci-difesa/ | 0 | — | 1 | — | 0 | PARADA ate haver regua | sem regua de Admissao para T12: mesmo materia nova sai NAO_SEI, nunca SIM [medido com o contrato de ANTES do reparo: o reparado so existia nas bancas da R1, apagadas antes desta medicao] |
| 43 | IT-T12-134 | R1 | T12 | não | **NAO** | NAO_SEI |  | — | — | 1 | — | 0 | PARADA ate haver regua | sem regua de Admissao para T12: mesmo materia nova sai NAO_SEI, nunca SIM [medido com o contrato de ANTES do reparo: o reparado so existia nas bancas da R1, apagadas antes desta medicao] |
| 44 | IT-T2-032 | R1 | T2 | não | **NAO** | NAO_SEI |  | 0 | — | 1 | — | 0 | PARADA ate haver regua | sem regua de Admissao para T2: mesmo materia nova sai NAO_SEI, nunca SIM [medido com o contrato de ANTES do reparo: o reparado so existia nas bancas da R1, apagadas antes desta medicao] |
| 45 | IT-T2-033 | R1 | T2 | não | **NAO** | NAO_SEI |  | 0 | — | 1 | — | 0 | PARADA ate haver regua | sem regua de Admissao para T2: mesmo materia nova sai NAO_SEI, nunca SIM [medido com o contrato de ANTES do reparo: o reparado so existia nas bancas da R1, apagadas antes desta medicao] |
| 46 | IT-T2-056 | portão | T2 | não | **NAO** | NAO_SEI |  | — | — | 1 | — | 0 | PARADA ate haver regua | sem regua de Admissao para T2: mesmo materia nova sai NAO_SEI, nunca SIM |
| 47 | IT-T2-063 | R1 | T2 | não | **NAO** | NAO_SEI |  | 0 | — | 1 | — | 0 | PARADA ate haver regua | sem regua de Admissao para T2: mesmo materia nova sai NAO_SEI, nunca SIM [medido com o contrato de ANTES do reparo: o reparado so existia nas bancas da R1, apagadas antes desta medicao] |
| 48 | IT-T2-070 | R1 | T2 | não | **NAO** | NAO_SEI |  | 0 | — | 1 | — | 0 | PARADA ate haver regua | sem regua de Admissao para T2: mesmo materia nova sai NAO_SEI, nunca SIM [medido com o contrato de ANTES do reparo: o reparado so existia nas bancas da R1, apagadas antes desta medicao] |
| 49 | IT-T2-106 | portão | T2 | não | **NAO** | NAO_SEI |  | — | — | 1 | — | 0 | PARADA ate haver regua | sem regua de Admissao para T2: mesmo materia nova sai NAO_SEI, nunca SIM |
| 50 | IT-T3-023 | R1 | T3 | sim | **NAO** | NAO_SEI (so_tema) | https://terraevita.edagricole.it/agrofarmaci-difesa/ | 0 | — | 1 | — | 0 | PARADA ate o contrato chegar ao coletor | sem contrato na tabela do coletor: o coletor recusa a fonte [medido com o contrato de ANTES do reparo: o reparado so existia nas bancas da R1, apagadas antes desta medicao] |
| 51 | IT-T5-041 | R1 | T5 | sim | **NAO** | NAO_SEI |  | — | — | 6 | — | 0 | PARADA ate o contrato chegar ao coletor | sem contrato na tabela do coletor: o coletor recusa a fonte |
| 52 | IT-T5-056 | R1 | T5 | sim | **NAO** | NAO_SEI |  | 0 | — | 1 | — | 0 | PARADA ate o contrato chegar ao coletor | sem contrato na tabela do coletor: o coletor recusa a fonte [medido com o contrato de ANTES do reparo: o reparado so existia nas bancas da R1, apagadas antes desta medicao] |
| 53 | IT-T5-080 | R1 | T5 | sim | **NAO** | NAO_SEI |  | — | — | 1 | — | 0 | PARADA ate o contrato chegar ao coletor | sem contrato na tabela do coletor: o coletor recusa a fonte [medido com o contrato de ANTES do reparo: o reparado so existia nas bancas da R1, apagadas antes desta medicao] |
| 54 | IT-T5-104 | R1 | T5 | sim | **NAO** | NAO_SEI |  | 0 | — | 1 | — | 0 | PARADA ate o contrato chegar ao coletor | sem contrato na tabela do coletor: o coletor recusa a fonte [medido com o contrato de ANTES do reparo: o reparado so existia nas bancas da R1, apagadas antes desta medicao] |
| 55 | IT-T5-111 | R1 | T5 | sim | **NAO** | NAO_SEI (so_tema) | https://www.crea.gov.it/web/guest/-/xylella-fastidiosa-dalla-ricerca-crea-nuove-strategie-per-l-olivicoltura | 0 | — | 1 | — | 0 | PARADA ate o contrato chegar ao coletor | sem contrato na tabela do coletor: o coletor recusa a fonte [medido com o contrato de ANTES do reparo: o reparado so existia nas bancas da R1, apagadas antes desta medicao] |
| 56 | IT-T5-113 | R1 | T5 | sim | **NAO** | NAO_SEI |  | 0 | — | 1 | — | 0 | PARADA ate o contrato chegar ao coletor | sem contrato na tabela do coletor: o coletor recusa a fonte [medido com o contrato de ANTES do reparo: o reparado so existia nas bancas da R1, apagadas antes desta medicao] |
| 57 | IT-T7-019 | R1 | T7 | sim | **NAO** | NAO_SEI |  | — | — | 1 | — | 0 | PARADA ate o contrato chegar ao coletor | sem contrato na tabela do coletor: o coletor recusa a fonte [medido com o contrato de ANTES do reparo: o reparado so existia nas bancas da R1, apagadas antes desta medicao] |
| 58 | IT-T7-033 | portão | T7 | sim | **NAO** | NAO_SEI (so_tema) | https://www.chianticlassico.com/vino/vendemmia/ | 15 | 0 | 15 | 0 | 1 | SEMANAL | nada novo: tudo o que a entrada anuncia ja esta no livro |
| 59 | IT-T7-042 | portão | T7 | sim | **NAO** | NAO_SEI (so_tema) |  | 10 | 0 | 10 | 0 | 0 | SEMANAL | nada novo: tudo o que a entrada anuncia ja esta no livro |
| 60 | IT-T7-043 | portão | T7 | sim | **NAO** | NAO_SEI (so_tema) |  | 2 | 0 | 2 | 0 | 0 | SEMANAL | nada novo: tudo o que a entrada anuncia ja esta no livro |
| 61 | IT-T7-048 | R1 | T7 | sim | **NAO** | NAO_SEI |  | 0 | — | 1 | — | 0 | PARADA ate o contrato chegar ao coletor | sem contrato na tabela do coletor: o coletor recusa a fonte [medido com o contrato de ANTES do reparo: o reparado so existia nas bancas da R1, apagadas antes desta medicao] |
| 62 | IT-T7-049 | R1 | T7 | sim | **NAO** | NAO_SEI |  | — | — | 1 | — | 0 | PARADA ate o contrato chegar ao coletor | sem contrato na tabela do coletor: o coletor recusa a fonte [medido com o contrato de ANTES do reparo: o reparado so existia nas bancas da R1, apagadas antes desta medicao] |
| 63 | IT-T7-053 | portão | T7 | sim | **NAO** | NAO_SEI |  | — | — | 1 | — | 0 | PARADA ate o contrato chegar ao coletor | sem contrato na tabela do coletor: o coletor recusa a fonte |
| 64 | IT-T7-058 | portão | T7 | sim | **NAO** | NAO_SEI |  | — | — | 1 | — | 0 | PARADA ate o contrato chegar ao coletor | sem contrato na tabela do coletor: o coletor recusa a fonte |
| 65 | IT-T7-100 | portão | T7 | sim | **NAO** | NAO_SEI (so_tema) | https://agrofarma.federchimica.it/news-ed-eventi/dettaglio-news/2026/06/08/agrofarma-e-federbio-lanciano-il-manifesto-per-il-biocontrollo | 2 | 0 | 1 | 0 | 0 | PARADA ate o contrato chegar ao coletor | sem contrato na tabela do coletor: o coletor recusa a fonte |
| 66 | IT-T7-105 | R1 | T7 | sim | **NAO** | NAO_SEI |  | 0 | — | 1 | — | 0 | PARADA ate o contrato chegar ao coletor | sem contrato na tabela do coletor: o coletor recusa a fonte [medido com o contrato de ANTES do reparo: o reparado so existia nas bancas da R1, apagadas antes desta medicao] |
| 67 | IT-T7-125 | R1 | T7 | sim | **NAO** | NAO_SEI |  | 0 | — | 1 | — | 0 | PARADA ate o contrato chegar ao coletor | sem contrato na tabela do coletor: o coletor recusa a fonte [medido com o contrato de ANTES do reparo: o reparado so existia nas bancas da R1, apagadas antes desta medicao] |
| 68 | IT-T7-139 | R1 | T7 | sim | **NAO** | NAO_SEI |  | 0 | — | 1 | — | 0 | PARADA ate o contrato chegar ao coletor | sem contrato na tabela do coletor: o coletor recusa a fonte [medido com o contrato de ANTES do reparo: o reparado so existia nas bancas da R1, apagadas antes desta medicao] |
| 69 | IT-T7-163 | R1 | T7 | sim | **NAO** | NAO_SEI |  | 0 | — | 1 | — | 0 | PARADA ate o contrato chegar ao coletor | sem contrato na tabela do coletor: o coletor recusa a fonte [medido com o contrato de ANTES do reparo: o reparado so existia nas bancas da R1, apagadas antes desta medicao] |
| 70 | IT-T8-010 | R1 | T8 | não | **NAO** | NAO_SEI |  | — | — | 1 | — | 0 | PARADA ate haver regua | sem regua de Admissao para T8: mesmo materia nova sai NAO_SEI, nunca SIM [medido com o contrato de ANTES do reparo: o reparado so existia nas bancas da R1, apagadas antes desta medicao] |
| 71 | IT-T8-022 | R1 | T8 | não | **NAO** | NAO_SEI (so_tema) | https://terraevita.edagricole.it/agrofarmaci-difesa/ | 0 | — | 1 | — | 0 | PARADA ate haver regua | sem regua de Admissao para T8: mesmo materia nova sai NAO_SEI, nunca SIM [medido com o contrato de ANTES do reparo: o reparado so existia nas bancas da R1, apagadas antes desta medicao] |
| 72 | IT-T8-024 | R1 | T8 | não | **NAO** | NAO_SEI (so_tema) | https://terraevita.edagricole.it/agrofarmaci-difesa/ | 0 | — | 1 | — | 0 | PARADA ate haver regua | sem regua de Admissao para T8: mesmo materia nova sai NAO_SEI, nunca SIM [medido com o contrato de ANTES do reparo: o reparado so existia nas bancas da R1, apagadas antes desta medicao] |
| 73 | IT-T8-042 | R1 | T8 | não | **NAO** | NAO_SEI (so_tema) | https://terraevita.edagricole.it/agrofarmaci-difesa/ | 0 | — | 1 | — | 0 | PARADA ate haver regua | sem regua de Admissao para T8: mesmo materia nova sai NAO_SEI, nunca SIM [medido com o contrato de ANTES do reparo: o reparado so existia nas bancas da R1, apagadas antes desta medicao] |
| 74 | IT-T5-090 | portão | T5 | sim | **NAO** | NAO |  | 42 | 41 | 1 | 0 | 1 | SEMANAL ate rever a janela (MAX_TARGETS) | 41 nova(s) anunciada(s), mas FORA da janela: o contrato so olha as primeiras 1 e essas ja estao no livro |
| 75 | IT-T7-021 | portão | T7 | sim | **NAO** | NAO |  | 17 | 15 | 1 | 0 | 0 | SEMANAL ate rever a janela (MAX_TARGETS) | 15 nova(s) anunciada(s), mas FORA da janela: o contrato so olha as primeiras 1 e essas ja estao no livro |
| 76 | IT-T2-034 | portão | T2 | não | **NAO** | NAO |  | 10 | 9 | 1 | 0 | 0 | PARADA ate haver regua | sem regua de Admissao para T2: mesmo materia nova sai NAO_SEI, nunca SIM |
| 77 | IT-T2-051 | portão | T2 | não | **NAO** | NAO |  | 8 | 7 | 1 | 0 | 0 | PARADA ate haver regua | sem regua de Admissao para T2: mesmo materia nova sai NAO_SEI, nunca SIM |
| 78 | IT-T7-117 | portão | T7 | sim | **NAO** | NAO |  | 7 | 6 | 1 | 0 | 0 | SEMANAL ate rever a janela (MAX_TARGETS) | 6 nova(s) anunciada(s), mas FORA da janela: o contrato so olha as primeiras 1 e essas ja estao no livro |
| 79 | IT-T10-021 | portão | T10 | sim | **NAO** | NAO |  | 4 | 3 | 1 | 0 | 0 | SEMANAL ate rever a janela (MAX_TARGETS) | 3 nova(s) anunciada(s), mas FORA da janela: o contrato so olha as primeiras 1 e essas ja estao no livro |
| 80 | IT-T7-121 | portão | T7 | sim | **NAO** | NAO |  | 4 | 3 | 1 | 0 | 0 | SEMANAL ate rever a janela (MAX_TARGETS) | 3 nova(s) anunciada(s), mas FORA da janela: o contrato so olha as primeiras 1 e essas ja estao no livro |
| 81 | IT-T7-135 | portão | T7 | sim | **NAO** | NAO |  | 5 | 3 | 1 | 0 | 0 | SEMANAL ate rever a janela (MAX_TARGETS) | 3 nova(s) anunciada(s), mas FORA da janela: o contrato so olha as primeiras 1 e essas ja estao no livro |
| 82 | IT-T5-049 | portão | T5 | sim | **NAO** | NAO |  | 5 | 1 | 4 | 0 | 4 | SEMANAL ate rever a janela (MAX_TARGETS) | 1 nova(s) anunciada(s), mas FORA da janela: o contrato so olha as primeiras 4 e essas ja estao no livro |
| 83 | IT-T10-022 | portão | T10 | sim | **NAO** | NAO |  | 9 | 0 | 14 | 0 | 0 | SEMANAL | nada novo: tudo o que a entrada anuncia ja esta no livro |
