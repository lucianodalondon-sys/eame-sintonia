# CONSERTO-REGUA · tempo e lugar · ramo `conserto-regua-v1` (a partir de `ce28040c`)

Os quatro erros que a SALA-VERIFICA achou, consertados com teste e **sem piorar nenhum item**.
Nada foi instalado. A Sala real foi só lida (`default_transaction_read_only`); nada de rede; o RAW
não foi tocado; o vivo não foi tocado.

## 1. O que estava errado, e o conserto

| # | erro (item da Sala) | conserto | ficheiro |
|---|---|---|---|
| 1 | **«2025» de comparação** virava data do facto: «Il valore resta sotto i circa 2,80 euro/kg **del 2025**» (IT-T10-018, 1333) | o **termo de comparação** entra na lista do que NÃO é tempo do facto: um ano logo depois de uma quantidade com unidade (euro/kg, %, t…) ou de «rispetto al / contro / sotto / oltre…» é tapado. «Nel 2025 il gruppo … ha raggiunto» continua a valer | `leis/fato_do_texto.py` (`NAO_E_TEMPO_DO_FACTO`) |
| 2 | **trecho da prova cortado antes do lugar**: «… colpito la **Sicilia**» ficava fora das 200 letras (1331); a base inteira cortada em 1000 letras perdia a prova de «Napoli» (1415) | o trecho de cada lugar é uma **janela em volta do lugar** (a frase, 150 letras de cada lado, o nome sempre dentro), e a base do lugar **deixa de ser cortada** | `leis/fato_do_texto.py` (`_janela_do_lugar`) |
| 3 | **página que é uma lista de eventos** juntava cidades de eventos diferentes: Popdays (Roma, 1-4/02/2023) + Milano, Brescia, Padova, Napoli de outros eventos (1415) | com 2+ datas de evento **diferentes** na página, um lugar de evento só vale se a sua frase tiver a data do evento escolhido; os outros ficam escritos como citados. Datas **dentro** do intervalo escolhido são o mesmo evento (Didacta 21-23/10 com sessões a 21, 22, 23) | `leis/fato_do_texto.py` |
| 4 | **publicação 2009** de uma página institucional (IT-T7-013, CONAF): o JSON-LD tinha só um nó **WebPage** (a data em que a PÁGINA foi criada) | a data de publicação por JSON-LD só vale de um nó que **publica** (Article, NewsArticle, BlogPosting…) ou sem tipo. Um nó com tipo de página (WebPage, WebSite…) fica como evidência no porquê, e o leitor passa ao nível seguinte (meta, `<time>`), senão NAO SEI | `coleta/executor_texto_de_html.py` |
| + | mesma classe de erro nas **datas de evento**: trecho cortado a meio («dal 21 al 23 ottob…», IT-T9-021) e trecho tirado do texto já tapado (sem o «oggi», 1426) — o trecho não se re-encontrava no bruto | o trecho da data de evento é uma janela em volta da data, tirada do texto **original** | `leis/fato_do_texto.py` (`_tempos_de_evento`) |

## 2. Antes / depois — a mesma conferência, nos mesmos itens

`provas/conserto_regua_recalcular.py` recalcula, sem banco, o que o código dá a cada linha da Sala
(fotografia só-leitura: **94 linhas**, porque a Sala cresceu desde a SALA-VERIFICA). A mesma estrada do
reprocessamento: livro, bytes guardados com o sha conferido, texto guardado.
`provas/sala_verifica.py --vista-json` confere os valores **contra o bruto**, com parse próprio:

- o trecho tem de estar no bruto e o valor no trecho;
- a base da publicação é conferida no bruto pela família dela (meta, `<time>`, JSON-LD de artigo).

| | publicação | lugar da fonte | data do facto | lugar do facto |
|---|---|---|---|---|
| **os 15 da SALA-VERIFICA · antes** (código do vivo = o que a Sala tem) | 14/15 | 15/15 | 15/15 | 13/15 |
| **os 15 · depois** | **15/15** | 15/15 | **15/15** | **15/15** |
| **as 94 · antes** | 86/94 | 94/94 | 91/94 | 91/94 |
| **as 94 · depois** | **94/94** | 94/94 | **94/94** | **94/94** |

O «antes» usa a mesma versão de código que gravou a Sala (`tempo-lugar@0efef9cf…`).
**Nenhum item piorou.**

### Os 9 valores que mudam (de 94 linhas) — lidos à mão

| linha | fonte | campo | antes → depois | leitura |
|---|---|---|---|---|
| 174, 309 | IT-T7-013 | publicação | 2009-12-18 → **NAO SEI** | ✅ o JSON-LD só tem um WebPage (a página «Consiglio dell'Ordine», criada em 2009) |
| 1460, 1483, 1519 | IT-T5-160 | publicação | 2020-02-20 → **NAO SEI** | ✅ o mesmo caso: a página do departamento «BIOCEL», só WebPage/WebSite, modificada em 2026 |
| 1333 | IT-T10-018 | data do facto | 2025 → **2026** | ✅ «mentre **nel 2026** il prezzo resta vicino ai minimi»: o preço da safra atual (precisão: ano) |
| 1415 | IT-T5-090 | lugar do facto | Roma;Milano;Brescia;Padova;Napoli → **Roma** | ✅ só Roma é do Popdays |
| 1426 | IT-T10-018 | lugar do facto | Rimini;Piemonte → **Rimini** | ✅ o Salone é em Rimini; «il Piemonte come Regione partner» é o parceiro, não o lugar |
| 1520 | IT-T5-186 | lugar do facto | Brindisi;Roma → **NAO SEI** | ✅ o evento é em L'Aia (Países Baixos, fora da lista de lugares); Brindisi e Roma eram de outros eventos |

Além destes, 16 linhas mudam **só a base**, porque o trecho passa a conter o lugar ou a data (por
exemplo, 1331 passa a provar «Sicilia»), ou mudam a evidência. Leitura à mão de uma pessoa, contra o
bruto: pode ter erro de um item.

## 3. Testes e mutação

- `tests/test_conserto_regua.py`: **10 testes**, cada um com um **exemplo real** da Sala (trechos
  curtos de páginas públicas; nomes de pessoas tirados). Inclui os dois lados: «Nel 2025 il gruppo…»
  continua a valer, e um artigo com um nó NewsArticle continua a publicar.
- `tests/mutacao_conserto_regua.py`: **9/9 pegas**.
  - **M0** repõe os dois ficheiros do vivo (`ce28040c`) e os testes **reprovam** (6 falhas): os testes
    apanham os defeitos reais.
  - M1–M8 desligam um conserto de cada vez.
- Suítes dos donos, sem vermelho:
  - `test_fato_do_texto` (44), `test_tempo_e_lugar_da_publicacao` (42),
    `test_tempo_e_lugar_atravessa` (43), `test_artefato_tempo_do_fato` (14) e `test_a_rota_do_html`
    (30): **183 verdes**.
  - `test_migracao_033_sala`: 15 verdes.
- **A mutação da LUGAR-FATO** (`scripts/lugar_fato/mutar_fato_do_texto.py`): parava na M22, porque a
  linha em que se apoiava mudou com o conserto 2. Mudei **só a âncora**; o mutante continua o mesmo.
  Agora dá **45/45 mortos**. O ficheiro de resultado dela (`MUTACAO-FATO-DO-TEXTO-V1.json`) foi
  reescrito pela corrida, com o código novo.
- ⚠️ Rodei o `test_migracao_033_sala` (Postgres descartável) **sem a trava**, por descuido: 3,5 min,
  14 GB livres, o banco foi desligado no fim. Não se repetiu.

## 4. Plano (NÃO executado)

**Instalar.** Juntar `conserto-regua-v1` pela via de sempre (o coordenador). Só código de leitura muda;
**nenhuma migração**: as colunas da 033 já existem.

**Reprocessar os afetados** (sem rede; o RAW nunca é tocado; a linha original nunca muda). Com o
código instalado, pelo roteiro da `MIGRACAO-SALA.md`, passos 7–9, a porta que já existe:

```bash
PYTHONUTF8=1 py admissao/reprocessar_tempo_lugar.py --livros "$LIV" --raizes "$RZ" --saida /tmp/plano-regua.json          # sem escrever
PYTHONUTF8=1 py admissao/reprocessar_tempo_lugar.py --livros "$LIV" --raizes "$RZ" --aplicar --saida $S/reprocesso-regua-1.json
PYTHONUTF8=1 py admissao/reprocessar_tempo_lugar.py --livros "$LIV" --raizes "$RZ" --aplicar --saida $S/reprocesso-regua-2.json   # tem de dar INSERIDAS: 0
```

**Previsto**, contra a fotografia de hoje: revisões novas em **25 das 94 linhas**. Por campo:
lugar do facto 13, data do facto 15, publicação 8, evidência 6 (mais a completude das 5 que perdem a
publicação). O **valor** muda em 9 (a tabela acima). Cada revisão leva a versão nova do extrator
(`tempo-lugar@…`, o sha256 do código), a data e o motivo. As revisões antigas **ficam**.

**Depois de reprocessar:**
```bash
py provas/sala_verifica.py --dump <backup> --livros "$LIV" --raizes "$RZ" --itens todos --saida <out.json>
```
Esperado: 94/94 nos quatro campos, `TODAS_AS_DO_DUMP_IGUAIS: true` (as linhas novas da Sala contam-se à parte, em `SO_AGORA`), e os gatilhos intactos.

**Desfazer:** não há nada a desfazer na Sala; as revisões são novas páginas do caderno. Para voltar ao
comportamento antigo, basta reinstalar o código anterior. As revisões novas ficam como histórico, que
é a lei.

## 5. Para os donos

- **LUGAR-FATO** (`leis/fato_do_texto.py`) e **nuvem tempo-publicacao**
  (`coleta/executor_texto_de_html.py`): os consertos estão nos ficheiros deles, cada um com o motivo
  escrito e o exemplo real. Peço que revejam antes de o coordenador instalar.
- Fica em aberto, e **não** foi mexido: numa lista de eventos, «Italy» / «Italia» como lugar continua
  recusado (regra da LUGAR-FATO); os eventos fora da lista de lugares (L'Aia) dão NAO SEI.

## 6. Provas fora do Git (caminho + sha256)

`C:/Users/London1/auditoria-madrugada/tempo-lugar/`: `sala-78-conserto.json` (fotografia
só-leitura das 94 linhas, com texto), `regua-antes.json`, `regua-depois.json` e os
`regua-*-verifica-*.json`. Os sha256 estão no fim deste ficheiro.

## EM PALAVRAS SIMPLES

- **O que eu fiz:** consertei os 4 erros que achei na verificação. Um ano de comparação de preço
  virava data do fato. Numa página com vários eventos, as cidades de todos eram juntadas num só.
  O trecho de prova às vezes era cortado antes do nome do lugar. E uma página que não é notícia
  aparecia como publicada em 2009.
- **Como sei que não piorei nada:** refiz a mesma conferência, contra o arquivo original, em todas as
  94 notícias da Sala. Antes: 86, 94, 91 e 91 certas nos quatro campos. Depois: **94 em todos**.
- **Como sei que os testes funcionam:** coloquei o código antigo de volta e os testes reclamaram. E
  estraguei cada conserto de propósito, um por um: os testes pegaram todos.
- **Nada foi instalado nem mudado na Sala.** O plano diz como aplicar. Quando o coordenador instalar,
  25 notícias ganham uma correção nova no caderno. As anteriores ficam lá.

```
2b944c993b5a26d1e85e7257911a9300f2758458646a0778a1be87aac133fe12  sala-78-conserto.json
b3619f6f0efb863c671a72f3b14505920d903c3782b2b2ac1419a437cbed24c3  regua-antes.json
6750fcd5a9698abed853ad001921e27398f373fac12e20259d38b22104a1e960  regua-depois.json
f7aabc1ff8845fa53bf8fd4cc2c74dc183c576a309d7c296666aa7b40cf59024  regua-antes-verifica-quinze.json
e1913c300ce27f5f266ffd387661f7537967a362361af565dcf692cd37007e77  regua-antes-verifica-todos.json
f89b33ed3f2ddc7bd7784825c0afd571ff9403d3125f45696bf46b3208bc8edf  regua-depois-verifica-quinze.json
958cf8fbe8a112ee6d1af03c88c17ca76a054958bcb54e8b7817e27b60921d41  regua-depois-verifica-todos.json
```
