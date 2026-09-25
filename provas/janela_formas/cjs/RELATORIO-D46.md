# D46 · provas da Emilia-Romagna e da agrometeopuglia (seguimento da C-JS)

25/09/2026, trabalho leve. **NÃO instalado.** Portão de consenso PASS IT antes de cada corrida.

## Pedidos (D38: no máximo 5 por domínio)

| domínio | pedidos | quais |
|---|---:|---|
| emilia-romagna.it | 4 | 1 `++api++` por província (robots: cópia da medição RFC, o grupo `*` só proíbe `/search` e afins) |
| agrometeopuglia.it | 4 | robots **vivo** pelo leitor da casa (guardado inteiro) · `/bollettini` (visita nova, cookies só dessa visita, apagados no fim) · `custom.js` · `extend_home.js` |

A API e o PDF da Puglia **não** foram pedidos (ver abaixo). Os 2 pedidos que seriam deles foram usados para
ler os 2 JS do tema, sem chave nenhuma, para testar a condição (1).

## agrometeopuglia · condição (1) NÃO confirmada → API NÃO chamada

- (2) Robots vivo: `/api/bollettini` e `/bollettini` **permitidos**.
- A página ao vivo (`/bollettini`, HTTP 200, sem login) entrega em `drupalSettings`:
  `key` (128 caracteres; em base64 é um hex de 96) e `REMOTE_ADDR` = o nosso IP. **Não entrega `api`.**
- `Bollettini.js` monta `/api/bollettini?api='+drupalSettings.api+'…`. Nenhum dos JS da página
  (`Bollettini.js`, `custom.js`, `extend_home.js`) copia `key` para `api`. **Medido:** zero ocorrências.
- Conclusão: **a chave entregue NÃO é o parâmetro `api`.** No navegador de uma pessoa, o site envia
  literalmente `api=undefined`. Pôr a `key` no `api` seria inventar um pedido que o site não faz. Não o fiz.
- O que isto quer dizer, sem prova: ou o servidor ignora o `api`, ou a lista do site está partida. **NÃO SEI.**
- A página ao vivo não tem os boletins no HTML. Só há um link para `wwwold…/Agrometeo/registrazione`
  («registo»): pode ser um indício de muro de login na parte antiga. **NÃO SEI.**

**Decisão do dono (nova):** autorizar 1 pedido `…/api/bollettini?api=undefined&tipologia=Settimanale`,
exatamente o que o navegador do site envia? Se responder com a lista: contrato abaixo (sem chave).
Se responder vazio ou erro: a fonte fica **fora** (ou headless, D42). A chave por visita deixa de
ser precisa em qualquer dos casos.

Contrato proposto (**só se** esse pedido der lista):
```
FORMA            = LISTA_E_DETALHE (API JSON → PDF)
LISTING          = /api/bollettini?api=undefined&tipologia=Quotidiano|Settimanale   (como o navegador do site)
DETAIL           = PDF por PATH_COMP (www…/bollettino-elettronico ou wwwold…/opencms/Documenti — robots de cada anfitrião)
OUTPUT_TYPE      = PDF
DOCUMENT_ID      = IT-T2-150:BOLETIM:<tipologia>:<NUMBER>
PUBLICATION_TIME = DATA_EMISSIONE_FORMAT ; FACT_TIME = DATA_VALIDITA_FORMAT ; COLLECTION_TIME = captura
```

## Emilia-Romagna · CONFIRMADA: boletins em PDF, com número e data

| província | o que o `++api++` devolve | boletins |
|---|---|---|
| Bologna e Ferrara | 44 filhos `File` (PDF), 25 por página (`batching.next` = `?b_start=25`) | 15 na 1.ª página: n.º 29 de 16/09/2026 … n.º 15 de 20/05/2026; mais «Orticole … Allegato» |
| Forlì-Cesena, Ravenna e Rimini | 45 filhos `File` (PDF), 25 por página | 15 na 1.ª página: n.º 29 de 16/09/2026 … n.º 16 de 27/05/2026 |
| Modena e Reggio Emilia | 2 `Document`: «Bollettini di Modena», «… di Reggio Emilia» | **mais um andar** (não pedido) |
| Parma e Piacenza | 2 `Document`: «Bollettini di Parma», «… di Piacenza» | **mais um andar** (não pedido) |

- Cada ficheiro traz `title`, `mime_type` `application/pdf`, `getObjSize`, `UID`, `Date`.
  **`effective` vem vazio.** `Date` é a hora de carregamento no site: o boletim 29 de 16/09 foi carregado
  em 16/09 às 15:48 (+02:00). O `modified` da pasta só acompanha o último ficheiro carregado.
- **A data do boletim está no título** («Bollettino 29 del 16 settembre 2026 di …»). Há casos que a regra
  tem de aguentar: «23 BIS … Aggiornamento irrigazione»; os títulos dos Allegati sem ano («del 24
  settembre»); o id do n.º 24 sem `.pdf`.
- O PDF (`@@download`) **não** foi pedido: falta provar o corpo (camada de texto) de 1 boletim.

Contrato proposto (receita por província, API JSON → PDF):
```
FORMA            = LISTA_E_DETALHE (API JSON → PDF)
LISTING          = <provincia>/++api++  (+ ?b_start=N enquanto houver batching.next)
                   Modena, Reggio Emilia, Parma e Piacenza: <provincia>/<cidade>/++api++  (1 andar a mais)
FILTRO           = @type File, mime_type application/pdf, título «Bollettino <n.º> [BIS] del <dia> <mês> <ano>»
                   (os «Orticole … Allegato» ficam de fora, ou são outro tipo — decisão do dono)
DETAIL           = <@id>/@@download/file
OUTPUT_TYPE      = PDF
DOCUMENT_ID      = IT-T3-013:BOLETIM:<PROVINCIA>:<n.º>[BIS]:<AAAA-MM-DD do título>   (sem hash, sem UID)
PUBLICATION_TIME = Date (hora de carregamento) ; FACT_TIME = data do título ; effective = ignorado (vazio)
RECOLLECTION     = LISTING mutável ; DETAIL imutável (um BIS é documento próprio)
```
Falta, antes de onboardar: 1 PDF de prova (corpo ≥ 800 caracteres, régua DETAIL/v1) e 1 pedido por cidade
nas províncias de 3 andares (4 pedidos). IT-T3-013 e IT-T3-028 apontam para esta mesma árvore:
**qual SOURCE_ID fica com cada província é decisão do dono** (não há prova nas páginas).

## Provas (fora do Git; memória 4,3 GB < 5 GB, por isso sem commit)

| ficheiro | sha256 |
|---|---|
| `C:/cur/cjs/provas_d46.py` | `5971169a5621a3c74eb1ab1a9e5383ac2b503a8bc2dc43259ab04bc2ab3577bf` |
| `C:/cur/cjs/provas_d46_js.py` | `d1ab5c571eaeb66fee1dbce2784d3914c5a0b101262360df0d4523887a854081` |
| `C:/cur/cjs/d46/RESULTADO-D46.json` | `6b7c300fae8e467e36d534549b2c90e5e70e49192d7ddaae6bd151d01106df2d` |
| `C:/cur/cjs/d46/robots-www.agrometeopuglia.it.txt` | `3200f655bd0e859a4fb1a7237cc64d4cec38824f6f5ee914c37d0b9de0f9c554` |
| `C:/cur/cjs/d46/pagina-bollettini.html` | `a550b018f66ae6957f01eb118f5c202ee2131cce1ade1491a42fbb8922e6ee21` |
| `C:/cur/cjs/d46/custom.js` | `d62e09c517acaab60a8a95515fa6a06d568f8101f5cda7077f96b7ac43bb96fe` |
| `C:/cur/cjs/d46/extend_home.js` | `147ca8d0c76f78ae43a293ee911c77324b3736913ab7b79dd198c69acbf81cb0` |
| `C:/cur/cjs/d46/er-bologna-e-ferrara.json` | `b324dd6356de0580c7c07c120bcd5bfe36939eb9b77b6a0bfda859759659b970` |
| `C:/cur/cjs/d46/er-forli-cesena-ravenna-rimini.json` | `f7e5d8f17d8cb15e4338b9d30f828b32f0d1311c8344a6e49107e0ed48e50927` |
| `C:/cur/cjs/d46/er-modena-reggio-emilia.json` | `46f0fcb10a98202534c28cc2327492bd566606f556523e1a0dbc19cfe0e87edc` |
| `C:/cur/cjs/d46/er-parma-piacenza.json` | `cd899af6bb425701a6aedf27c42200a7b480f5ba370b7ab236e2673b589aaafa` |
