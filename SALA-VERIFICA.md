# SALA-VERIFICA · verificação independente da 033 na Sala real · ramo `sala-verifica-v1`

Base: o vivo `origin/servico-20260923-0923` @ `e5cd691f`. **Só SELECT**: a sessão foi forçada a
`default_transaction_read_only=on` e o script confere isso (`SHOW`) antes de tudo. Rede fechada.
O vivo e a Sala não foram tocados. Script: `provas/sala_verifica.py`.

**Independente de quem gravou:** a data da página foi relida do HTML bruto pelo medidor do
ponto 1 (`provas/tempo_e_lugar_medir.py`), e não pelo leitor da nuvem que a gravou. O texto foi
tirado **de novo do bruto** (HTML sem etiquetas; PDF por `pdftotext`), e não da coluna `texto`
da Sala. A regra: o TRECHO da base tem de estar no bruto, e o VALOR tem de estar no trecho. Os
brutos foram achados pelo `storage_path`, com o sha256 conferido.

## 1. A migração e o caderno de revisões

| pergunta | resposta |
|---|---|
| a 033 na Sala é o ficheiro do ramo? | `schema_migracao`: `033 APLICADA b980c76e…` = sha do ficheiro no checkout ✅ |
| revisões | **478**: 455 da versão `a6a28e6a` (19:07) + 23 da `0efef9cf` (19:54, só onde o valor mudou) |
| sequências com buraco (uma revisão apagada deixaria buraco) | **0** |
| revisões sem linha na Sala | **0** |
| a vista lê a ÚLTIMA revisão? | as 8 leituras da vista usam `order by r.revisao desc` ✅ |

O coordenador disse 468. O número medido é **478** (455 + 23). **Não sei** de onde veio o 468;
a minha hipótese, não medida, é o «já eram assim = 468» da 2.ª passagem do ensaio na cópia.

## 2. As linhas originais não mudaram

As 24 colunas de antes da 033, com `\copy` só-leitura agora, comparadas com o dump só-leitura de
**25/09 13:58** (antes da 033 das 16:05):

```
linhas antes 78 · agora 78 · IGUAIS BYTE A BYTE · sha256 dos dois = 2070e09d17c2efe7…
```

Ninguém escreveu nelas: nem a migração, nem o reprocessamento, nem a 2.ª passagem.

## 3. Os gatilhos recusam UPDATE, DELETE e TRUNCATE (lido na definição, sem escrever nada)

```
sala_de_espera_revisao_nao_muda     | O | BEFORE DELETE OR UPDATE ON public.sala_de_espera_revisao FOR EACH ROW
sala_de_espera_revisao_nao_esvazia  | O | BEFORE TRUNCATE ON public.sala_de_espera_revisao FOR EACH STATEMENT
função: raise exception 'SALA_REVISAO_SO_ACRESCENTA: …' — só levanta, não tem RETURN
regras (pg_rules) na tabela: 0
```

`O` = ligado no modo normal. ⚠️ **Limite, dito:** um superutilizador consegue sempre desligar um
gatilho (`ALTER TABLE … DISABLE TRIGGER`, ou `session_replication_role = replica`). O gatilho
impede o **erro** e a escrita **calada**; não impede quem tenha as chaves do banco inteiro.

## 4. Os 15 itens, contra o bruto

A escolha cobre um item de cada caso: boletim T3 por edição, por validade e com semana
calculada; PDF T5 vazio e com lugar; eventos; mercado; o «2025» suspeito; «oggi» calculado;
Popdays; pólen; publicação por `meta` e por `<time>`; uma publicação em 2009. O N37 fica de fora
porque não tem bruto em lado nenhum.

**Mecânico** (o trecho no bruto, o valor no trecho, a base certa): publicação **15/15** ·
lugar da fonte **15/15** · data do facto **15/15** · lugar do facto **13/15**.

**Leitura humana** (uma pessoa, contra o bruto; pode ter erro de um item):

| item | publicação | lugar da fonte | data do facto | lugar do facto |
|---|---|---|---|---|
| 1 IT-T3-010 APOL | ✅ NAO SEI (a data é de VALIDADE) | ✅ Lecce | ✅ NAO SEI | ✅ NAO SEI (Lecce e Brindisi são a área do boletim, não um facto) |
| 7 IT-T3-002 | ✅ 16/09, edição (livro + nome `SA-16-09`) | ✅ Napoli | ✅ NAO SEI | ✅ NAO SEI |
| 36 IT-T3-008 N38 | ✅ 16/09 | ✅ Bari | ✅ 07–13/09 («settimana scorsa», conta refeita) | ✅ Puglia |
| 76 IT-T5-009 PDF | ✅ NAO SEI | ✅ NAO SEI | ✅ NAO SEI | ✅ NAO SEI |
| 77 IT-T5-010 PDF | ✅ NAO SEI (a data do PDF é de geração) | ✅ | ✅ campagna 2010 | ✅ Ferrara |
| 164 IT-T5-015 | ✅ NAO SEI | ✅ | ✅ 12–13/11/2026 | ✅ Napoli (CNR) |
| 169 IT-T5-030 | ✅ | ✅ | ✅ 8/10/2026 | ✅ Teramo |
| 170 IT-T5-033 | ✅ | ✅ | ✅ 29/09/2026 | ✅ NAO SEI (não inventou) |
| 174 IT-T7-013 | ⚠️ **2009-12-18**: a própria página declara isto no JSON-LD (o medidor independente leu o mesmo). A BASE está certa, mas o valor parece ser a data de criação da página, e não da notícia | ✅ | ✅ | ✅ |
| 1331 IT-T10-018 | ✅ meta | ✅ | ✅ NAO SEI | ⚠️ Sicilia e Verona **certos no bruto**, mas o trecho guardado foi **cortado antes de «Sicilia»**: a prova de «Sicilia» não está na base |
| 1333 IT-T10-018 | ✅ meta | ✅ | ❌ «2025» é ano de **comparação** de preço, não o tempo do facto | ✅ NAO SEI |
| 1406 IT-T10-018 | ✅ meta | ✅ | ✅ 23/09/2026 | ✅ Firenze |
| 1415 IT-T5-090 | ✅ NAO SEI | ✅ | ✅ 1–4/02/2023 | ❌ só **Roma** é do Popdays. Milano, Brescia, Padova e Napoli vêm de **outros eventos** da mesma página (uma lista), e a prova de «Napoli» ficou fora da base (cortada nas 1000 letras) |
| 1450 IT-T2-034 | ✅ `<time>` | ✅ | ✅ maio (pico de pólen) | ✅ NAO SEI (conservador: Marche só mencionada) |
| 1466 IT-T5-185 | ✅ meta | ✅ | ✅ NAO SEI | ✅ NAO SEI |

**Total humano:** publicação **15/15** com a base certa (1 valor suspeito, ver 174) · lugar da
fonte **15/15** · data do facto **14/15** · lugar do facto **14/15** no valor, e **13/15** com a
prova inteira guardada.

## 5. Achados para os donos (nenhum foi mexido aqui)

1. **LUGAR-FATO — o trecho da prova é cortado antes do lugar** (1331) e a base inteira é cortada
   em 1000 letras (1415, «Napoli»). Pedido: o trecho tem de conter sempre o lugar que prova, e a
   lista não pode perder provas no corte.
2. **LUGAR-FATO — página que é uma LISTA de eventos** (1415): mistura lugares de eventos
   diferentes num só facto. Pedido: numa lista, um lugar só vale junto da data do mesmo evento.
3. **LUGAR-FATO — «2025» de comparação** (1333): já tinha sido declarado por ela; continua.
4. **nuvem tempo-publicacao — IT-T7-013 com JSON-LD de 2009** (174): o leitor faz o que a regra
   manda, mas uma data 17 anos antes da colheita merece um alarme (por exemplo, marcar precisão
   baixa quando a publicação é muito anterior à captura). Decisão do dono.
5. **Nada disto pede UPDATE:** qualquer correção entra como revisão nova pela porta
   (`admissao/reprocessar_tempo_lugar.py`), e o original fica.

## 6. Provas fora do Git (caminho + sha256)

`C:/Users/London1/auditoria-madrugada/tempo-lugar/`:
```
9b8bc4d1ea5986456b7eee4ceb9f186a7c35c244c3e1e9e1130612af1fec2e5e  sala-verifica.json      (o resultado deste script)
e798a4847f7506bac276d2129af34c214105cdbb92524173b04049c46622dead  vista-verifica.json     (SELECT só-leitura da vista)
179b76339560fc21b3a38a196c892ebc4e44162ed2f3620c3c6e25b9f40d0b20  sala-real-copia.dump    (pg_dump só-leitura, 13:58)
```

## EM PALAVRAS SIMPLES

- **O que eu fiz:** conferi, só olhando, sem mudar nada, se a Sala ficou certa depois da reforma.
  Peguei 15 notícias e comparei cada resposta com o arquivo original guardado, usando uma régua
  diferente da que escreveu as respostas.
- **As notícias originais não mudaram nem uma letra**, e o caderno de correções não deixa apagar
  nem rasurar: vi isso nas regras do próprio banco.
- **Das 15 notícias:**
  - data de publicação e lugar de quem publica: **15 certas**;
  - data do fato: **14 certas**;
  - lugar do fato: **14 certas**.
  - As erradas: um "2025" que era só comparação de preço, e uma página com uma lista de eventos em
    que as cidades de vários eventos foram juntadas num só.
- **Atenção:** uma página diz ter sido publicada em 2009. A regra foi cumprida, mas a data parece
  ser a de criação da página, não a da notícia.
- **O que muda para você:** nada precisa ser desfeito. Os erros achados vão para quem faz a
  leitura do texto; quando consertarem, a correção entra como página nova do caderno.
