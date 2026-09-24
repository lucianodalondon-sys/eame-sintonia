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

## Como se refaz

```
py ferramentas/rendimento/sala_por_fonte.py --saida C:/rend/sala.json          # Sala, só leitura
node ferramentas/rendimento/medir_entrada.mjs --arvore <bot> --ledger <bot>/data/collection-ledger/italy/observations.ndjson \
     --sala C:/rend/sala.json --curadores <bot>/curadoria/italy_contracts_curator.json --ids ... --saida X.json
py ferramentas/rendimento/tabela.py --r1 <reparo-fontes-v1>/scripts/reparo/R1-REENSAIO-ANTES-DEPOIS-fca4f2b6.json
```

Provas no ramo: `ferramentas/rendimento/medidas/*.json` (cada linha traz `INDEX_SHA256` da capa pedida) e `REND-TABELA-V1.json`.
Fora do Git (bytes das capas, não são prova primária): `C:/rend/indices/`, `C:/rend/indices-r1/`; `C:/rend/sala.json` sha256 `bc7c12377ec387830cba596e405e0770e7c3ff80357ae207b205cf6ca0deb368` (a versão sem URLs está no ramo).

## As 37 do portão (vivo, 24/09)

| Fonte | U | Régua | Onde | Anuncia hoje | Novas p/ coletor | Janela | 1 corrida traz | SIM na Sala (hist.) | Vale agora? | Cadência sugerida | Porquê |
|---|---|---|---|---|---|---|---|---|---|---|---|
| IT-T10-018 | T10 | sim | coorte 1a onda | 33 | 2 | 30 | 2 | 19 | **SIM** | DIARIA | 2 materia(s) nova(s) dentro da janela do contrato |
| IT-T10-021 | T10 | sim | coorte 1a onda | 4 | 3 | 1 | 0 | 0 | **NAO** | SEMANAL ate rever a janela (MAX_TARGETS) | 3 nova(s) anunciada(s), mas FORA da janela: o contrato so olha as primeiras 1 e essas ja estao no livro |
| IT-T10-022 | T10 | sim | coorte 1a onda | 9 | 0 | 14 | 0 | 0 | **NAO** | SEMANAL | nada novo: tudo o que a entrada anuncia ja esta no livro |
| IT-T12-137 | T12 | não | fora da coorte:sem receita web para t12 | 3 | 3 | 1 | 1 | 0 | **NAO** | PARADA ate haver regua | sem regua de Admissao para T12: mesmo materia nova sai NAO_SEI, nunca SIM |
| IT-T2-034 | T2 | não | coorte 1a onda | 10 | 9 | 1 | 0 | 0 | **NAO** | PARADA ate haver regua | sem regua de Admissao para T2: mesmo materia nova sai NAO_SEI, nunca SIM |
| IT-T2-051 | T2 | não | coorte 1a onda | 8 | 7 | 1 | 0 | 0 | **NAO** | PARADA ate haver regua | sem regua de Admissao para T2: mesmo materia nova sai NAO_SEI, nunca SIM |
| IT-T2-056 | T2 | não | fora da coorte:sem contrato de coleta | — | — | 1 | — | 0 | **NAO** | PARADA ate haver regua | sem regua de Admissao para T2: mesmo materia nova sai NAO_SEI, nunca SIM |
| IT-T2-106 | T2 | não | fora da coorte:sem contrato de coleta | — | — | 1 | — | 0 | **NAO** | PARADA ate haver regua | sem regua de Admissao para T2: mesmo materia nova sai NAO_SEI, nunca SIM |
| IT-T5-049 | T5 | sim | fora da coorte:rota:capability block | 5 | 1 | 4 | 0 | 4 | **NAO** | SEMANAL ate rever a janela (MAX_TARGETS) | 1 nova(s) anunciada(s), mas FORA da janela: o contrato so olha as primeiras 4 e essas ja estao no livro |
| IT-T5-090 | T5 | sim | coorte 1a onda | 42 | 41 | 1 | 0 | 1 | **NAO** | SEMANAL ate rever a janela (MAX_TARGETS) | 41 nova(s) anunciada(s), mas FORA da janela: o contrato so olha as primeiras 1 e essas ja estao no livro |
| IT-T5-101 | T5 | sim | fora da coorte:sem contrato de coleta | 7 | 7 | 1 | 1 | 0 | **NAO** | PARADA ate o contrato chegar ao coletor | sem contrato na tabela do coletor: o coletor recusa a fonte |
| IT-T7-017 | T7 | sim | coorte 1a onda | 55 | 24 | 30 | 0 | 0 | **NAO** | SEMANAL ate rever a janela (MAX_TARGETS) | 24 nova(s) anunciada(s), mas FORA da janela: o contrato so olha as primeiras 30 e essas ja estao no livro |
| IT-T7-021 | T7 | sim | coorte 1a onda | 17 | 15 | 1 | 0 | 0 | **NAO** | SEMANAL ate rever a janela (MAX_TARGETS) | 15 nova(s) anunciada(s), mas FORA da janela: o contrato so olha as primeiras 1 e essas ja estao no livro |
| IT-T7-033 | T7 | sim | coorte 1a onda | 15 | 0 | 15 | 0 | 1 | **NAO** | SEMANAL | nada novo: tudo o que a entrada anuncia ja esta no livro |
| IT-T7-042 | T7 | sim | coorte 1a onda | 10 | 0 | 10 | 0 | 0 | **NAO** | SEMANAL | nada novo: tudo o que a entrada anuncia ja esta no livro |
| IT-T7-043 | T7 | sim | coorte 1a onda | 2 | 0 | 2 | 0 | 0 | **NAO** | SEMANAL | nada novo: tudo o que a entrada anuncia ja esta no livro |
| IT-T7-053 | T7 | sim | fora da coorte:sem contrato de coleta | — | — | 1 | — | 0 | **NAO** | PARADA ate o contrato chegar ao coletor | sem contrato na tabela do coletor: o coletor recusa a fonte |
| IT-T7-058 | T7 | sim | fora da coorte:sem contrato de coleta | — | — | 1 | — | 0 | **NAO** | PARADA ate o contrato chegar ao coletor | sem contrato na tabela do coletor: o coletor recusa a fonte |
| IT-T7-100 | T7 | sim | fora da coorte:sem contrato de coleta | 2 | 0 | 1 | 0 | 0 | **NAO** | PARADA ate o contrato chegar ao coletor | sem contrato na tabela do coletor: o coletor recusa a fonte |
| IT-T7-112 | T7 | sim | coorte 1a onda | 4 | 3 | 1 | 0 | 0 | **NAO** | SEMANAL ate rever a janela (MAX_TARGETS) | 3 nova(s) anunciada(s), mas FORA da janela: o contrato so olha as primeiras 1 e essas ja estao no livro |
| IT-T7-115 | T7 | sim | fora da coorte:sem contrato de coleta | 13 | 12 | 1 | 0 | 0 | **NAO** | PARADA ate o contrato chegar ao coletor | sem contrato na tabela do coletor: o coletor recusa a fonte |
| IT-T7-117 | T7 | sim | coorte 1a onda | 7 | 6 | 1 | 0 | 0 | **NAO** | SEMANAL ate rever a janela (MAX_TARGETS) | 6 nova(s) anunciada(s), mas FORA da janela: o contrato so olha as primeiras 1 e essas ja estao no livro |
| IT-T7-118 | T7 | sim | coorte 1a onda | 10 | 9 | 1 | 0 | 0 | **NAO** | SEMANAL ate rever a janela (MAX_TARGETS) | 9 nova(s) anunciada(s), mas FORA da janela: o contrato so olha as primeiras 1 e essas ja estao no livro |
| IT-T7-120 | T7 | sim | fora da coorte:sem contrato de coleta | 6 | 6 | 1 | 1 | 0 | **NAO** | PARADA ate o contrato chegar ao coletor | sem contrato na tabela do coletor: o coletor recusa a fonte |
| IT-T7-121 | T7 | sim | coorte 1a onda | 4 | 3 | 1 | 0 | 0 | **NAO** | SEMANAL ate rever a janela (MAX_TARGETS) | 3 nova(s) anunciada(s), mas FORA da janela: o contrato so olha as primeiras 1 e essas ja estao no livro |
| IT-T7-123 | T7 | sim | coorte 1a onda | 4 | 3 | 1 | 0 | 0 | **NAO** | SEMANAL ate rever a janela (MAX_TARGETS) | 3 nova(s) anunciada(s), mas FORA da janela: o contrato so olha as primeiras 1 e essas ja estao no livro |
| IT-T7-135 | T7 | sim | coorte 1a onda | 5 | 3 | 1 | 0 | 0 | **NAO** | SEMANAL ate rever a janela (MAX_TARGETS) | 3 nova(s) anunciada(s), mas FORA da janela: o contrato so olha as primeiras 1 e essas ja estao no livro |
| IT-T7-141 | T7 | sim | coorte 1a onda | 11 | 11 | 1 | 1 | 0 | **SIM** | DIARIA | 1 materia(s) nova(s) dentro da janela do contrato |
| IT-T8-021 | T8 | não | fora da coorte:sem receita web para t8 | 17 | 17 | 1 | 1 | 0 | **NAO** | PARADA ate haver regua | sem regua de Admissao para T8: mesmo materia nova sai NAO_SEI, nunca SIM |
| IT-T8-028 | T8 | não | fora da coorte:sem receita web para t8 | 4 | 4 | 1 | 1 | 0 | **NAO** | PARADA ate haver regua | sem regua de Admissao para T8: mesmo materia nova sai NAO_SEI, nunca SIM |
| IT-T8-029 | T8 | não | fora da coorte:sem receita web para t8 | 5 | 5 | 1 | 1 | 0 | **NAO** | PARADA ate haver regua | sem regua de Admissao para T8: mesmo materia nova sai NAO_SEI, nunca SIM |
| IT-T8-030 | T8 | não | fora da coorte:sem receita web para t8 | 5 | 5 | 1 | 1 | 0 | **NAO** | PARADA ate haver regua | sem regua de Admissao para T8: mesmo materia nova sai NAO_SEI, nunca SIM |
| IT-T8-034 | T8 | não | fora da coorte:sem receita web para t8 | 5 | 5 | 1 | 1 | 0 | **NAO** | PARADA ate haver regua | sem regua de Admissao para T8: mesmo materia nova sai NAO_SEI, nunca SIM |
| IT-T8-039 | T8 | não | fora da coorte:sem receita web para t8 | 4 | 4 | 1 | 1 | 0 | **NAO** | PARADA ate haver regua | sem regua de Admissao para T8: mesmo materia nova sai NAO_SEI, nunca SIM |
| IT-T8-040 | T8 | não | fora da coorte:sem receita web para t8 | 3 | 3 | 1 | 1 | 0 | **NAO** | PARADA ate haver regua | sem regua de Admissao para T8: mesmo materia nova sai NAO_SEI, nunca SIM |
| IT-T8-051 | T8 | não | fora da coorte:sem receita web para t8 | 9 | 9 | 1 | 1 | 0 | **NAO** | PARADA ate haver regua | sem regua de Admissao para T8: mesmo materia nova sai NAO_SEI, nunca SIM |
| IT-T9-021 | T9 | sim | fora da coorte:sem receita web para t9 | 4 | 4 | 1 | 1 | 0 | **NAO** | PARADA ate sair o bloqueio | a entrada tem novidade, mas a fonte esta fora da coorte: SEM_RECEITA_WEB_PARA_T9 |

## As 46 READY que a R1 traria (R1 NÃO instalada)

| Fonte | U | Régua | Onde | Anuncia hoje | Novas p/ coletor | Janela | 1 corrida traz | SIM na Sala (hist.) | Vale agora? | Cadência sugerida | Porquê |
|---|---|---|---|---|---|---|---|---|---|---|---|
| IT-T12-023 | T12 | não | r1 nao instalada:a reparo | 13 | 13 | 1 | 1 | 0 | **NAO** | PARADA ate haver regua | sem regua de Admissao para T12: mesmo materia nova sai NAO_SEI, nunca SIM [medido com o contrato de ANTES do reparo: o reparado so existia nas bancas da R1, apagadas antes desta medicao] |
| IT-T12-024 | T12 | não | r1 nao instalada:b recanario | 6 | 6 | 1 | 1 | 0 | **NAO** | PARADA ate haver regua | sem regua de Admissao para T12: mesmo materia nova sai NAO_SEI, nunca SIM |
| IT-T12-042 | T12 | não | r1 nao instalada:a reparo | — | — | 1 | — | 0 | **NAO** | PARADA ate haver regua | sem regua de Admissao para T12: mesmo materia nova sai NAO_SEI, nunca SIM [medido com o contrato de ANTES do reparo: o reparado so existia nas bancas da R1, apagadas antes desta medicao] |
| IT-T12-043 | T12 | não | r1 nao instalada:a reparo | 0 | — | 1 | — | 0 | **NAO** | PARADA ate haver regua | sem regua de Admissao para T12: mesmo materia nova sai NAO_SEI, nunca SIM [medido com o contrato de ANTES do reparo: o reparado so existia nas bancas da R1, apagadas antes desta medicao] |
| IT-T12-044 | T12 | não | r1 nao instalada:a reparo | 0 | — | 1 | — | 0 | **NAO** | PARADA ate haver regua | sem regua de Admissao para T12: mesmo materia nova sai NAO_SEI, nunca SIM [medido com o contrato de ANTES do reparo: o reparado so existia nas bancas da R1, apagadas antes desta medicao] |
| IT-T12-073 | T12 | não | r1 nao instalada:a reparo | 0 | — | 1 | — | 0 | **NAO** | PARADA ate haver regua | sem regua de Admissao para T12: mesmo materia nova sai NAO_SEI, nunca SIM [medido com o contrato de ANTES do reparo: o reparado so existia nas bancas da R1, apagadas antes desta medicao] |
| IT-T12-075 | T12 | não | r1 nao instalada:a reparo | 0 | — | 1 | — | 0 | **NAO** | PARADA ate haver regua | sem regua de Admissao para T12: mesmo materia nova sai NAO_SEI, nunca SIM [medido com o contrato de ANTES do reparo: o reparado so existia nas bancas da R1, apagadas antes desta medicao] |
| IT-T12-081 | T12 | não | r1 nao instalada:a reparo | 0 | — | 1 | — | 0 | **NAO** | PARADA ate haver regua | sem regua de Admissao para T12: mesmo materia nova sai NAO_SEI, nunca SIM [medido com o contrato de ANTES do reparo: o reparado so existia nas bancas da R1, apagadas antes desta medicao] |
| IT-T12-102 | T12 | não | r1 nao instalada:a reparo | 0 | — | 1 | — | 0 | **NAO** | PARADA ate haver regua | sem regua de Admissao para T12: mesmo materia nova sai NAO_SEI, nunca SIM [medido com o contrato de ANTES do reparo: o reparado so existia nas bancas da R1, apagadas antes desta medicao] |
| IT-T12-104 | T12 | não | r1 nao instalada:a reparo | 0 | — | 1 | — | 0 | **NAO** | PARADA ate haver regua | sem regua de Admissao para T12: mesmo materia nova sai NAO_SEI, nunca SIM [medido com o contrato de ANTES do reparo: o reparado so existia nas bancas da R1, apagadas antes desta medicao] |
| IT-T12-117 | T12 | não | r1 nao instalada:b recanario | 2 | 2 | 1 | 1 | 0 | **NAO** | PARADA ate haver regua | sem regua de Admissao para T12: mesmo materia nova sai NAO_SEI, nunca SIM |
| IT-T12-129 | T12 | não | r1 nao instalada:a reparo | 0 | — | 1 | — | 0 | **NAO** | PARADA ate haver regua | sem regua de Admissao para T12: mesmo materia nova sai NAO_SEI, nunca SIM [medido com o contrato de ANTES do reparo: o reparado so existia nas bancas da R1, apagadas antes desta medicao] |
| IT-T12-130 | T12 | não | r1 nao instalada:a reparo | 0 | — | 1 | — | 0 | **NAO** | PARADA ate haver regua | sem regua de Admissao para T12: mesmo materia nova sai NAO_SEI, nunca SIM [medido com o contrato de ANTES do reparo: o reparado so existia nas bancas da R1, apagadas antes desta medicao] |
| IT-T12-131 | T12 | não | r1 nao instalada:a reparo | 0 | — | 1 | — | 0 | **NAO** | PARADA ate haver regua | sem regua de Admissao para T12: mesmo materia nova sai NAO_SEI, nunca SIM [medido com o contrato de ANTES do reparo: o reparado so existia nas bancas da R1, apagadas antes desta medicao] |
| IT-T12-134 | T12 | não | r1 nao instalada:a reparo | — | — | 1 | — | 0 | **NAO** | PARADA ate haver regua | sem regua de Admissao para T12: mesmo materia nova sai NAO_SEI, nunca SIM [medido com o contrato de ANTES do reparo: o reparado so existia nas bancas da R1, apagadas antes desta medicao] |
| IT-T2-032 | T2 | não | r1 nao instalada:a reparo | 0 | — | 1 | — | 0 | **NAO** | PARADA ate haver regua | sem regua de Admissao para T2: mesmo materia nova sai NAO_SEI, nunca SIM [medido com o contrato de ANTES do reparo: o reparado so existia nas bancas da R1, apagadas antes desta medicao] |
| IT-T2-033 | T2 | não | r1 nao instalada:a reparo | 0 | — | 1 | — | 0 | **NAO** | PARADA ate haver regua | sem regua de Admissao para T2: mesmo materia nova sai NAO_SEI, nunca SIM [medido com o contrato de ANTES do reparo: o reparado so existia nas bancas da R1, apagadas antes desta medicao] |
| IT-T2-037 | T2 | não | r1 nao instalada:a reparo | 8 | 8 | 1 | 1 | 0 | **NAO** | PARADA ate haver regua | sem regua de Admissao para T2: mesmo materia nova sai NAO_SEI, nunca SIM [medido com o contrato de ANTES do reparo: o reparado so existia nas bancas da R1, apagadas antes desta medicao] |
| IT-T2-050 | T2 | não | r1 nao instalada:a reparo | 4 | 4 | 1 | 1 | 0 | **NAO** | PARADA ate haver regua | sem regua de Admissao para T2: mesmo materia nova sai NAO_SEI, nunca SIM [medido com o contrato de ANTES do reparo: o reparado so existia nas bancas da R1, apagadas antes desta medicao] |
| IT-T2-063 | T2 | não | r1 nao instalada:a reparo | 0 | — | 1 | — | 0 | **NAO** | PARADA ate haver regua | sem regua de Admissao para T2: mesmo materia nova sai NAO_SEI, nunca SIM [medido com o contrato de ANTES do reparo: o reparado so existia nas bancas da R1, apagadas antes desta medicao] |
| IT-T2-070 | T2 | não | r1 nao instalada:a reparo | 0 | — | 1 | — | 0 | **NAO** | PARADA ate haver regua | sem regua de Admissao para T2: mesmo materia nova sai NAO_SEI, nunca SIM [medido com o contrato de ANTES do reparo: o reparado so existia nas bancas da R1, apagadas antes desta medicao] |
| IT-T3-023 | T3 | sim | r1 nao instalada:a reparo | 0 | — | 1 | — | 0 | **NAO** | PARADA ate o contrato chegar ao coletor | sem contrato na tabela do coletor: o coletor recusa a fonte [medido com o contrato de ANTES do reparo: o reparado so existia nas bancas da R1, apagadas antes desta medicao] |
| IT-T5-041 | T5 | sim | r1 nao instalada:b recanario | — | — | 6 | — | 0 | **NAO** | PARADA ate o contrato chegar ao coletor | sem contrato na tabela do coletor: o coletor recusa a fonte |
| IT-T5-056 | T5 | sim | r1 nao instalada:a reparo | 0 | — | 1 | — | 0 | **NAO** | PARADA ate o contrato chegar ao coletor | sem contrato na tabela do coletor: o coletor recusa a fonte [medido com o contrato de ANTES do reparo: o reparado so existia nas bancas da R1, apagadas antes desta medicao] |
| IT-T5-080 | T5 | sim | r1 nao instalada:a reparo | — | — | 1 | — | 0 | **NAO** | PARADA ate o contrato chegar ao coletor | sem contrato na tabela do coletor: o coletor recusa a fonte [medido com o contrato de ANTES do reparo: o reparado so existia nas bancas da R1, apagadas antes desta medicao] |
| IT-T5-104 | T5 | sim | r1 nao instalada:a reparo | 0 | — | 1 | — | 0 | **NAO** | PARADA ate o contrato chegar ao coletor | sem contrato na tabela do coletor: o coletor recusa a fonte [medido com o contrato de ANTES do reparo: o reparado so existia nas bancas da R1, apagadas antes desta medicao] |
| IT-T5-111 | T5 | sim | r1 nao instalada:a reparo | 0 | — | 1 | — | 0 | **NAO** | PARADA ate o contrato chegar ao coletor | sem contrato na tabela do coletor: o coletor recusa a fonte [medido com o contrato de ANTES do reparo: o reparado so existia nas bancas da R1, apagadas antes desta medicao] |
| IT-T5-113 | T5 | sim | r1 nao instalada:a reparo | 0 | — | 1 | — | 0 | **NAO** | PARADA ate o contrato chegar ao coletor | sem contrato na tabela do coletor: o coletor recusa a fonte [medido com o contrato de ANTES do reparo: o reparado so existia nas bancas da R1, apagadas antes desta medicao] |
| IT-T7-019 | T7 | sim | r1 nao instalada:a reparo | — | — | 1 | — | 0 | **NAO** | PARADA ate o contrato chegar ao coletor | sem contrato na tabela do coletor: o coletor recusa a fonte [medido com o contrato de ANTES do reparo: o reparado so existia nas bancas da R1, apagadas antes desta medicao] |
| IT-T7-031 | T7 | sim | r1 nao instalada:b recanario | 6 | 6 | 1 | 1 | 0 | **DEPOIS_DA_R1** | DIARIA depois da R1 | a entrada tem novidade; so corre quando a R1 for instalada e a fonte passar o portao |
| IT-T7-041 | T7 | sim | r1 nao instalada:a reparo | 7 | 7 | 7 | 3 | 1 | **DEPOIS_DA_R1** | DIARIA depois da R1 | a entrada tem novidade; so corre quando a R1 for instalada e a fonte passar o portao [medido com o contrato de ANTES do reparo: o reparado so existia nas bancas da R1, apagadas antes desta medicao] |
| IT-T7-048 | T7 | sim | r1 nao instalada:a reparo | 0 | — | 1 | — | 0 | **NAO** | PARADA ate o contrato chegar ao coletor | sem contrato na tabela do coletor: o coletor recusa a fonte [medido com o contrato de ANTES do reparo: o reparado so existia nas bancas da R1, apagadas antes desta medicao] |
| IT-T7-049 | T7 | sim | r1 nao instalada:a reparo | — | — | 1 | — | 0 | **NAO** | PARADA ate o contrato chegar ao coletor | sem contrato na tabela do coletor: o coletor recusa a fonte [medido com o contrato de ANTES do reparo: o reparado so existia nas bancas da R1, apagadas antes desta medicao] |
| IT-T7-103 | T7 | sim | r1 nao instalada:a reparo | 1 | 1 | 1 | 1 | 0 | **NAO** | PARADA ate o contrato chegar ao coletor | sem contrato na tabela do coletor: o coletor recusa a fonte [medido com o contrato de ANTES do reparo: o reparado so existia nas bancas da R1, apagadas antes desta medicao] |
| IT-T7-105 | T7 | sim | r1 nao instalada:a reparo | 0 | — | 1 | — | 0 | **NAO** | PARADA ate o contrato chegar ao coletor | sem contrato na tabela do coletor: o coletor recusa a fonte [medido com o contrato de ANTES do reparo: o reparado so existia nas bancas da R1, apagadas antes desta medicao] |
| IT-T7-125 | T7 | sim | r1 nao instalada:a reparo | 0 | — | 1 | — | 0 | **NAO** | PARADA ate o contrato chegar ao coletor | sem contrato na tabela do coletor: o coletor recusa a fonte [medido com o contrato de ANTES do reparo: o reparado so existia nas bancas da R1, apagadas antes desta medicao] |
| IT-T7-139 | T7 | sim | r1 nao instalada:a reparo | 0 | — | 1 | — | 0 | **NAO** | PARADA ate o contrato chegar ao coletor | sem contrato na tabela do coletor: o coletor recusa a fonte [medido com o contrato de ANTES do reparo: o reparado so existia nas bancas da R1, apagadas antes desta medicao] |
| IT-T7-150 | T7 | sim | r1 nao instalada:a reparo | 1 | 1 | 1 | 1 | 0 | **NAO** | PARADA ate o contrato chegar ao coletor | sem contrato na tabela do coletor: o coletor recusa a fonte [medido com o contrato de ANTES do reparo: o reparado so existia nas bancas da R1, apagadas antes desta medicao] |
| IT-T7-163 | T7 | sim | r1 nao instalada:a reparo | 0 | — | 1 | — | 0 | **NAO** | PARADA ate o contrato chegar ao coletor | sem contrato na tabela do coletor: o coletor recusa a fonte [medido com o contrato de ANTES do reparo: o reparado so existia nas bancas da R1, apagadas antes desta medicao] |
| IT-T8-010 | T8 | não | r1 nao instalada:a reparo | — | — | 1 | — | 0 | **NAO** | PARADA ate haver regua | sem regua de Admissao para T8: mesmo materia nova sai NAO_SEI, nunca SIM [medido com o contrato de ANTES do reparo: o reparado so existia nas bancas da R1, apagadas antes desta medicao] |
| IT-T8-022 | T8 | não | r1 nao instalada:a reparo | 0 | — | 1 | — | 0 | **NAO** | PARADA ate haver regua | sem regua de Admissao para T8: mesmo materia nova sai NAO_SEI, nunca SIM [medido com o contrato de ANTES do reparo: o reparado so existia nas bancas da R1, apagadas antes desta medicao] |
| IT-T8-024 | T8 | não | r1 nao instalada:a reparo | 0 | — | 1 | — | 0 | **NAO** | PARADA ate haver regua | sem regua de Admissao para T8: mesmo materia nova sai NAO_SEI, nunca SIM [medido com o contrato de ANTES do reparo: o reparado so existia nas bancas da R1, apagadas antes desta medicao] |
| IT-T8-041 | T8 | não | r1 nao instalada:a reparo | 15 | 15 | 1 | 1 | 0 | **NAO** | PARADA ate haver regua | sem regua de Admissao para T8: mesmo materia nova sai NAO_SEI, nunca SIM [medido com o contrato de ANTES do reparo: o reparado so existia nas bancas da R1, apagadas antes desta medicao] |
| IT-T8-042 | T8 | não | r1 nao instalada:a reparo | 0 | — | 1 | — | 0 | **NAO** | PARADA ate haver regua | sem regua de Admissao para T8: mesmo materia nova sai NAO_SEI, nunca SIM [medido com o contrato de ANTES do reparo: o reparado so existia nas bancas da R1, apagadas antes desta medicao] |
| IT-T9-015 | T9 | sim | r1 nao instalada:b recanario | 2 | 2 | 2 | 2 | 0 | **NAO** | PARADA ate o contrato chegar ao coletor | sem contrato na tabela do coletor: o coletor recusa a fonte |
| IT-T9-019 | T9 | sim | r1 nao instalada:b recanario | 19 | 19 | 19 | 3 | 0 | **NAO** | PARADA ate o contrato chegar ao coletor | sem contrato na tabela do coletor: o coletor recusa a fonte |
