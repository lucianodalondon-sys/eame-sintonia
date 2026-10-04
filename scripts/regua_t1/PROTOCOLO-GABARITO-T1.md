# PROTOCOLO DO GABARITO T1 (CROP & PRODUCTION) PARA JANELAS DE CULTURA — escrito ANTES dos rótulos

T1-JANELA · 2026-09-24 · o mesmo método da T2-REGUA (`scripts/regua_t2/PROTOCOLO-GABARITO-T2.md`):
gabarito primeiro, régua depois, medida no gabarito, vizinhos antes/depois, mutação numa cópia.

## Porque existe

D29 (dono): coletar o que sustenta **janelas de cultura**. A INT mediu que a Collection guarda 6
dos 18 campos mínimos da `CAP-WIN` e faltam as 4 chaves (cultura, região, fase fenológica, janela).
Hoje a porta **não tem régua T1**: todo o par (item, T1) sai `NAO_SE_APLICA` — medido na T2
(`MEDICAO-REGUA-T2-V2.json`, secção T1: 45/45 janelas = NAO_SE_APLICA).

## A pergunta de T1 (para a D29)

> **Este conteúdo diz, para uma CULTURA nomeada, em que fase ela está ou o momento de uma
> operação** — fenologia/estádio, sementeira/plantação, colheita/vindima, momento de tratamento,
> aviso de defesa por cultura?

Atlas `docs/fontes/ATLAS-DE-FONTES-EAME.md:45`: T1 = área, produção, produtividade, **calendário
agrícola, desenvolvimento da cultura**, previsão de safra, regiões produtoras, histórico. Esta régua
cobre a parte «calendário/desenvolvimento» (a que a D29 pede); área/produção/preço ficam fora dela e
isso fica dito.

## Rótulo `T1_JANELA`

- **YES** — cultura nomeada E fase/estádio ou momento de operação (sementeira, colheita, tratamento,
  limiar de intervenção) escritos no texto. Boletins fitossanitários/agrometeorológicos por cultura
  entram aqui.
- **NO** — sem cultura nomeada, ou cultura sem momento: mercado/preços, prémios de vinho, história de
  empresa, menus, administração, ambiente, eventos, legislação sem calendário.
- **NAO_SEI** — só título; mistura em que não se decide; manual de produção integrada do ano inteiro
  (orienta sem dizer o momento); texto regulatório com data de obrigação (data regulatória ≠ janela).

A Admissão **não decide a janela**: só admite e preserva os campos do item. A régua não lê datas
para decidir e não escreve `FACT_TIME`/`FACT_LOCATION`.

## De onde vêm os textos (acervo, sem rede)

O mesmo corpus da T2 (1.309 textos: inventário `REGUA-T2-V1\textos`, derivados do armazém,
lote-76). Escolha dos textos a ler, por regra fixa e declarada:
1. todos os 61 YES do gabarito T2-V3 (boletins de janela — candidatos fortes a T1 YES);
2. todos os textos do corpus com uma palavra de colheita/sementeira (`vendemmia`, `raccolta`,
   `trebbiatura`, `semina`, `colheita`, `semeadura`, `harvest`), até 60 — os positivos que a T2 não
   apanha (notícia de colheita sem tempo) e os negativos difíceis (colheita no mercado);
3. 60 textos ao acaso do resto do corpus (semente 24092026) — o controlo.
Ler-se-á o TEXTO; rótulo e trecho no gabarito; `VALIDADO_POR_HUMANO = NAO`.
A regra do ponto 2 escolhe por palavra e **enviesa** a precisão medida nesse estrato — por isso a
precisão é dada por estrato.

## Critérios de aceitação

≥ 20 YES e ≥ 20 NO distintos; precisão/recall no gabarito (DENTRO da amostra); vizinhos
(T2 T3 T4 T5 T7 T9 T10) antes/depois nos 1.309 = 0 mudanças, ou cada uma listada e lida;
mutação numa cópia com todos os mutantes mortos.
