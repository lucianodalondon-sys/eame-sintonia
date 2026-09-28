# leis_proposta/ — PROPOSTA L5-P3 (D144, 28/09/2026). NÃO INSTALADA.

Cópia isolada. **Não substitui `leis/`.** Nada em `leis/`, `orquestrador/`,
`admissao/` ou `motor/` importa este pacote. Existe para ser medida antes de
qualquer decisão do dono.

## O problema medido (LAB, 28/09/2026)

O campo vivo `fact_time` é **um só** para cinco coisas diferentes. Resultado medido
na cópia da Sala (275 itens):

- **15 fatos com data no texto não foram extraídos** (9 com ano, 6 sem ano);
- **5 datas erradas passaram** e viraram sinal: uma semana de *validade*
  (derived:7), «campagna 2024» num boletim de 2026, «2016» de histórico, «2025/2026»
  que é o nome do DPI, «2004» da primeira deteção na Europa;
- formas que o extrator vivo simplesmente não lê: `dd/mm/aaaa`, `dd.mm.aaaa`,
  `aaaa-mm-dd`, «(gennaio 2026)», «settimana 39/2026»;
- «mese di maggio 2026» perdia o ano; «dal 1 al 4 settembre 2026» virava só «4»;
- 123 dos 275 itens têm o texto todo numa linha, e o filtro «corpo, não página»
  achava **0 linhas de corpo** — devolvia NÃO SEI por forma do ficheiro.

## O que esta proposta faz

Cinco baldes em vez de um campo:

| tipo | o que é | exemplo |
|---|---|---|
| `FACT_TIME` | o acontecimento no campo | «monitoraggio effettuato dal 1 al 4 settembre 2026» |
| `VALIDITY_TIME` | até quando uma regra vale | «validità dal 01/03/2026 al 28/06/2026», «scadenza utilizzo 30/06/2026» |
| `PUBLICATION_TIME` | o carimbo de quem publicou | «N° 27 del 16/09/2026», «Aggiornato al: 04.05.2026» |
| `ACT_TIME` | a data do ato | «Decreto Dirigenziale n. 15068 DEL 08/09/2026» |
| `MARKET_PERIOD` | safra, campanha, semana de preço | «campagna 2024», «settimana 39/2026» |
| `PERIODO_DA_EDICAO` | de que dias a edição fala | «BOLLETTINO settimana 39 dal 22/09 al 29/09» |

**O período da edição nunca vira validade** (D147). «De que dias este boletim fala» e
«até quando esta derroga vale» são duas coisas, e misturá-las foi o erro medido em
derived:7.

Quatro leis que o código cumpre, não só declara:

1. **`PUBLISHED_AT` nunca preenche `FACT_TIME`.** A publicação serve para reconhecer
   o carimbo e para marcar limites inferidos, e nada mais.
2. **Ano ausente fica ausente.** Sem ano escrito, o valor é `SEM_ANO-09-17` e
   `ANO = 'NAO SEI'`. Um único caminho o completa (D147): um ano de 4 algarismos
   **escrito no mesmo documento, na mesma oração, a ≤40 letras e inequívoco** — um só
   ano naquela janela. Sai com `ORIGEM=CABECALHO` e **os dois trechos** (o da expressão
   e `ANO_BASIS`, com o offset do ano). Dois anos diferentes na janela, ou nenhum: o ano
   fica `NAO SEI`. Publicação e coleta nunca completam nada.
2b. **Relativa só com publicação provada** (D63). «ieri», «lo scorso mese» só contam com
   `PUBLISHED_AT` **e** base que não seja NÃO SEI, e saem com `ORIGEM=RELATIVO_D63`; a
   precisão é a da expressão («lo scorso mese» dá um mês, nunca um dia). O ano da
   publicação entra ainda num sítio, e só para **reconhecer o carimbo**: um dia sem ano
   cuja combinação dia-mês seja a da publicação é carimbo, não facto — e o valor
   guardado continua `SEM_ANO-...`.
3. **Precisão literal.** Mês fica `MONTH`, semana fica `WEEK`, intervalo guarda
   `VALOR_INICIO` **e** `VALOR_FIM`. Nunca se fabrica um dia a partir de um mês.
4. **Inferência tem nome próprio.** «o achado é anterior à publicação» sai em
   `LIMITES_INFERIDOS` com `INFERENCIA=True`, fora de `FACT_TIME`.

Um **ano sozinho nunca data uma observação**: nos cinco casos medidos pelo LAB
(«2013», «2016», «2004», «2025», «campagna 2024») era sempre outra coisa — início
de monitoramento, histórico, preço de referência, nome de programa.

## Como medir

```bash
py -3.12 provas/l5-p3/avaliar.py <golden.json> --sha256 <golden.sha256>
py -3.12 provas/l5-p3/regressao.py --python <interprete com pytest>
```

`provas/l5-p3/casos_lab.json` é o banco de **desenvolvimento** (casos do LAB +
sintéticos). Não é gabarito: a proposta foi escrita contra ele, e por isso acertar
nele não prova nada. O golden set é hold-out, do LAB, congelado com hash.

## O que esta proposta NÃO resolve

- **Tempo por afirmação.** Continua um valor escolhido por documento (com os outros
  candidatos à vista). A P1 do LAB — tempo como qualificador de cada afirmação —
  é mudança de dono (Intelligence), não de regex.
- **Contrato da fonte.** `contrato_da_fonte='VALIDADE'|'EDICAO'` melhora muito o
  cabeçalho, e quem o passa é a Collection. Sem ele, a proposta adivinha pelo texto.
- **Idioma.** Só italiano, como o vivo.
