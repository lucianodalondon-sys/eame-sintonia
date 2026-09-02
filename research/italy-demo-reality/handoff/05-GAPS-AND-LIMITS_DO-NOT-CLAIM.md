# NÃO AFIRME — leia antes de escrever qualquer texto de tela

Cada frase proibida tem, ao lado, **a frase permitida que a substitui**. Não é censura: é a
diferença entre o que os dados sustentam e o que eles não sustentam.

---

## 1 · Portfólio — a mais perigosa de todas

> ⛔ **«A ADAMA não tem produto para *alvo* em *cultura*.»**
> ⛔ «Não há registro» · «não existe» · «não consta»

**Por quê:** a cobertura de uso lido é **19 de 163 produtos (11,7%)**. Os outros 144 não
têm linha ligando cultura e alvo porque **não foi lida**, não porque não exista. O número
de capa `LABEL_COVERAGE: 163/163 (100%)` conta **rótulo baixado**, não uso lido.

✅ **Diga:** *«nesta leitura do rótulo publicado pelo Ministero, capturada em 30/08/2026,
não encontramos linha que ligue cultura e alvo para este produto. Isso é o que a nossa
coleta leu — não é o que o registro contém. Não sei.»*

> É a lição que o Portal Sintonia Brasil pagou: o Nimitz EC tinha 3 culturas no catálogo e
> 19 no registro. **Afirmar que o cliente não tem produto quando ele tem é o pior erro
> possível deste sistema.**

---

## 2 · Vozes públicas — e a armadilha nova

> ⛔ «o produtor relatou» · «produtores italianos estão dizendo» · «a voz do agricultor»
> ⛔ «X% dos produtores»
> ⛔ ⭐ **apresentar as 58 vozes italianas como um número só**

**Por quê:** o `fonte_id` de um comentário é o **canal**, não o autor — comentário é
**plateia daquele canal**. E a varredura de 02/09 mediu uma divisão que muda tudo:

| plateia do canal | falas |
|---|---:|
| `PROFESSIONAL_FIELD_AUDIENCE` | **24** |
| `HOBBY_GARDEN_AUDIENCE` | **32** |
| `NOT_KNOWN` | 2 |

As 32 falam de **roseira, limoeiro e aveleira de quintal**. São vozes reais, de gente real,
e **não são lavoura**.

> **Relato em primeira pessoa sobre um vaso não é voz de lavoura.**

✅ **Diga:** *«um comentarista, sob o vídeo do canal X (plateia profissional), escreveu:
"…"»* — com a classe de plateia e o denominador ao lado.

---

## 3 · Publicidade de concorrente

> ⛔ «o anúncio foi dirigido à Itália» · «a campanha teve sucesso» · «a BASF investiu X»

**Por quê:** a Meta publica que o anúncio **ALCANÇOU** o país.
`AD_REACHED_COUNTRY ≠ AD_TARGETED_COUNTRY`. E não publica gasto, alcance nem impressão.

✅ **Diga:** *«414 cartões de anúncio de 6 concorrentes alcançaram a Itália, observados em
31/08/2026.»*

---

## 4 · Resistência e eficácia

> ⛔ «há resistência aqui» · «o produto falhou» · «o produto não controlou»

**Por quê:** resistência só se declara com base oficial — na Itália, o GIRE. E «falha de
controle» **não tem dono** neste sistema: não existe detector, e não se criou um.

✅ **Diga:** *«o GIRE publica resistência confirmada ao mecanismo X na espécie Y na cultura
Z, primeiro caso em ANO. A ADAMA tem N registros italianos que declaram esse grupo.»*

---

## 5 · Ocorrência e escala

> ⛔ «o problema está aumentando na Itália» · «a praga está ocorrendo em *região*»

**Por quê:** temos **6 regiões de 20**, e um boletim provincial não representa a região.
O nível 2 (proporção entre janelas) está `NAO_MEDIDO`: só há uma janela.

✅ **Diga:** *«o boletim do serviço fitossanitário de X, publicado em DD/MM/2026, registra
Y.»* — com a região e a data.

---

## 6 · Regulatório

> ⛔ «o produto vai sair do mercado» · «a substância será proibida» · «há desabastecimento»

**Por quê:** os atos europeus lidos **estendem** o prazo; nenhum decide a renovação.

✅ **Diga:** *«a aprovação europeia do tau-fluvalinate expira em 31/01/2027, foi estendida
pelo Reg. (UE) 2024/1206 — que registra avaliação de risco não finalizada — e nenhum ato
posterior nomeando a substância foi publicado até 02/09/2026.»*

---

## 7 · Mercado

> ⛔ «mercado quente» · «os clientes vão comprar» · nota de 0 a 100
> ⛔ «importação subindo = demanda subindo»
> ⛔ ⭐ **«a ISMEA não tem dado» / «a ISTAT está fora do ar»**

**Por quê:** importação pode ser quebra de safra, recomposição de estoque ou arbitragem. E
preço alto de cultura **não é** lucro do produtor.

E sobre a última: as duas **estão no ar e respondem para outros**. A ISMEA devolve 301
normal de Milão, Berlim, Helsinque e Miami; recusa o **nosso** IP com `GEO_IP_BLOCK`.

> **Fonte bloqueada por IP não é fonte inexistente. É problema de rota.**

✅ **Diga:** a temperatura em uma palavra — `SUPPORTIVE` / `BALANCED` / `PRESSURED` /
`COOLING` / `TIGHTENING` / `VOLATILE` / `MIXED SIGNALS` — **sempre** com o bloco «POR QUÊ»
aberto e rotulada **INTERPRETAÇÃO DO SINTONIA**.

⚠️ E: **praça que parou de cotar mantém a última cotação.** Azeite em Salerno: €630, de
**2015**. Todo preço traz `SERIES_STATE`.

---

## 8 · Negócio da ADAMA

> ⛔ vendas · sell-in · sell-out · share · margem · estoque · pedidos · intenção de compra

✅ **Diga:** *«dado interno não conectado.»*

---

## 9 · Eventos

> ⛔ «X vai participar da feira Y»

✅ **Diga:** o confirmado, com fonte — *«a ADAMA publicou a própria presença no Enovitis in
Campo 2026, Stand Área B, número B2.»* — e `NÃO SEI` para o resto.

---

## 10 · A regra que cobre o resto

> **Campo vazio sai como `NÃO SEI`, jamais como «não há».**
> **`NOT_OBTAINED` ≠ `DOES_NOT_EXIST`.** Cobertura é sempre um piso.
> **Porta ausente ≠ rendeu zero.** Nunca abrimos o Instagram italiano — «0 menções no
> Instagram» seria mentira, não medição.
