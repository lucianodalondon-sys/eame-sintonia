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
   `ANO = 'NAO SEI'`. Um único caminho o completa (D147 itens 1-2, D153): o ano da
   **linha de data / cabeçalho do mesmo documento**, e só quando (a) o cabeçalho é
   inequivocamente da mesma edição, (b) o ano governa a afirmação, (c) **nenhum outro
   ano** pode datar a mesma afirmação — nem na oração dela, nem entre o cabeçalho e ela —,
   (d) os dois trechos ficam citados (`BASIS` + `ANO_BASIS` com offset) e (e) a
   procedência está escrita. Dúvida → `NAO SEI`. Publicação e coleta nunca completam nada.
   Sem dia/mês na frase, a publicação nunca vira `FACT_TIME`.
2b. **Relativa** (D63/D149). «ieri», «lo scorso mese», «questa settimana» contam a partir
   de: o **período impresso** do próprio boletim, a **data impressa** no documento, ou a
   publicação **provada** — nessa ordem. Sai com `ORIGEM=RELATIVO_D63` e a composição
   registada; a precisão é a da expressão («lo scorso mese» dá um mês, nunca um dia). O
   ano da publicação entra ainda num sítio, e só para **reconhecer o carimbo**: um dia sem
   ano cuja combinação dia-mês seja a da publicação é carimbo, não fato — e o valor
   guardado continua `SEM_ANO-...`.
3. **Precisão literal.** Mês fica `MONTH`, semana fica `WEEK`, intervalo guarda
   `VALOR_INICIO` **e** `VALOR_FIM`. Nunca se fabrica um dia a partir de um mês.
4. **Inferência tem nome próprio.** «o achado é anterior à publicação» sai em
   `LIMITES_INFERIDOS` com `INFERENCIA=True`, fora de `FACT_TIME`.

Um **ano sozinho pode datar o fato** (D147 item 3): «ha chiuso il 2025», «La campagna
2026 registra prezzi in calo» = `FACT_TIME` com precisão `ANO`. Esta linha dizia o
contrário até 29/09/2026 — era uma regra minha, e contrariava a decisão do dono.
Continuam de fora: ano que é **nome** de norma/relatório/programa, campanha citada de
passagem para comparar preço, e o ano histórico de **outro** fato (este último apenas
condicional: vale se a afirmação-alvo for esse primeiro acontecimento).

## VOLTA 3 — a regra inverteu-se (R3 item 1)

A prova às cegas deu **0/20** nas duas voltas anteriores. A causa principal medida:
eu exigia uma **âncora de uma lista fechada de verbos** a ≤160 letras da data. Sem
âncora, a data era descartada — inclusive quando estava **na própria oração da
afirmação**. Uma lista fechada de verbos nunca cobre o italiano e o inglês reais
(particípio, fundação, entrada em instituição, «durante o período…»).

Agora:

- **Aceitação por omissão.** Uma data escrita numa oração **é** o tempo do
  acontecimento dessa oração, a menos que algo a desqualifique.
- A âncora deixou de ser condição de entrada. Passou a ser **critério de desempate**
  quando o documento tem várias datas (campo `ANCORADA`).
- Os desqualificadores dividiram-se em dois:
  - **absolutos** — publicação, validade, ato, nome de documento/programa, comparação,
    série de anos, previsão, conselho: nunca são fato de afirmação nenhuma;
  - **condicionais** — «avviata nel 2013», «per la prima volta nel 2004», a data de um
    convegno: datam **outra** afirmação. Se a afirmação-alvo for precisamente essa, valem.
    Quem sabe qual é o alvo é a interface; o nível de documento nunca os escolhe.

Dois erros de raiz apareceram ao medir isto, e valem registro:

1. **O ponto de `n. 15068` e de `26.05.2026` era lido como fim de frase.** A oração
   partia-se no meio, e a data do decreto ficava numa oração que já não tinha a palavra
   «Decreto» — saindo como data do fato. `_RE_FIM_DE_ORACAO` agora sabe distinguir
   abreviatura e número de ponto final.
2. **`osservat` casava dentro de `osservatorio`** — instituição lida como observação.
   A produção já tem uma lei para isso (`ANCORA_DENTRO_DE_OUTRA_PALAVRA`) e eu repeti
   o erro que ela corrige.

Mais: inglês (meses, `June 12, 2026`, `from 1 to 15 June`, relativas), intervalos de
**anos** e de **semanas** inteiros, `NAO_EXISTE` só com sinal **positivo** de
acontecimento, prazo de candidatura como `VALIDITY` e não `ACT`, e relativa ancorada na
data **impressa** no próprio documento quando o metadado da Sala vem vazio.

## Como medir

```bash
py -3.12 provas/l5-p3/avaliar.py <golden.json> --sha256 <golden.sha256>
py -3.12 provas/l5-p3/regressao.py --python <interprete com pytest>
```

`provas/l5-p3/casos_r3.py` (29 casos, um grupo por causa da volta 3, italiano e inglês),
`provas/l5-p3/casos_r2.py` (14 casos da volta 2) e
`provas/l5-p3/casos_lab.json` são o banco de **desenvolvimento** (casos do LAB +
sintéticos). Não é gabarito: a proposta foi escrita contra ele, e por isso acertar
nele não prova nada. O golden set é hold-out, do LAB, congelado com hash.

## O que esta proposta NÃO resolve

- **Tempo por afirmação, no módulo.** `leis_proposta/tempo_tipado.py` continua a
  devolver um valor por documento (com todos os candidatos à vista). Quem faz o tempo
  **por afirmação** é `provas/l5-p3/interface.py`, que recebe o alvo e filtra por ele —
  inclusive os candidatos condicionais. A P1 do LAB (tempo como qualificador de cada
  afirmação, dentro da esteira) continua a ser mudança de dono, não de regex.
- **Contrato da fonte.** `contrato_da_fonte='VALIDADE'|'EDICAO'` melhora muito o
  cabeçalho, e quem o passa é a Collection. Sem ele, a proposta adivinha pelo texto.
- **Idioma.** Italiano e inglês (meses, `June 12, 2026`, `from 1 to 15 June`, relativas,
  e âncoras de desempate). Mais nenhum. Em data numérica ambígua (`05/06/2026` num texto
  inglês) mantém-se a leitura italiana dd/mm — o primeiro número só é lido como mês
  quando o segundo é maior que 12.
