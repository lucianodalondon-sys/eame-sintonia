# S2A · A FRONTEIRA CLIENTE / SERVIDOR

> O que um concorrente consegue copiar hoje, apenas abrindo o SINTONIA.

Medido em 2026-09-09 sobre `release/canonical` (`9ae641bd`), que e a linha que
**producao serve hoje** — e nao sobre a linha de Security, que esta atras dela.
Auditar a superficie errada teria dado um numero tranquilizador e falso.

```
FICHEIROS PUBLICADOS   88
BYTES PUBLICADOS       37.338.284
AUDITADOS              88 (100%)
UNKNOWN                0
```

---

## 1. A CORRECCAO QUE MUDA O DIAGNOSTICO

A S0 concluiu que «o motor e o acervo viajam para o browser». **Metade disso
estava errado, e a metade errada e a que decidia o plano.**

Medido, em todo o codigo de interface publicado: **zero funcoes de pontuacao,
peso, limiar ou classificacao**. Nenhum `WEIGHTS = {`, nenhum `THRESHOLDS = {`,
nenhuma aritmetica de score. O motor **nao corre no browser** — e nunca correu.

E ele nao corre porque a arquitectura ja decidiu isso, e escreveu-o nos proprios
ficheiros:

```
adama-relevance.js        "A LEI vive em leis/adama_relevance.py e decide-se LA.
                           Este ficheiro transporta o veredito para o browser,
                           que nunca o recalcula."
italy-canonical-windows.js "The presentation layer must not compute START_DATE"
italy-label-verdicts.js    "The presentation layer APPLIES these verdicts."
meeting-surface.js         "This module PRESENTS. It does not decide."
```

**A fronteira ja existe. So que e uma fronteira de TEMPO DE BUILD, e nao de
tempo de pedido.** O motor corre em Python, no CI, e escreve pacotes; o browser
recebe respostas.

Isso muda o que a S2 deve fazer. Nao ha motor para mover. Ha um **corpus** e uma
**lei escrita** que viajam ao lado da resposta.

    O CLIENTE PRECISA DA RESPOSTA. NAO PRECISA DA RECEITA.

---

## 2. O QUE ESTA LA, POR CLASSE

| Classe | Ficheiros | Bytes | % |
|---|---:|---:|---:|
| PROPRIETARY_DATA | 16 | 28.452.920 | 76,2 |
| PUBLIC_ASSET | 51 | 5.724.143 | 15,3 |
| PUBLIC_UI | 15 | 2.021.750 | 5,4 |
| INTERNAL_METADATA | 1 | 1.067.491 | 2,9 |
| PROPRIETARY_RULE | 5 | 71.980 | 0,2 |

**Tres quartos do que servimos e corpus.** A apresentacao inteira — todo o
codigo que desenha o portal — sao 2 MB, 5,4%. O sistema de design e as fontes da
ADAMA pesam quase tres vezes mais do que o codigo que os usa.

Nota de honestidade sobre `PROPRIETARY_DATA`: os factos crus vem em boa parte de
fontes publicas — o registo do Ministero della Salute, o ISTAT, a biblioteca de
anuncios, ORCID. O concorrente podia ir busca-los. O que ele nao teria de fazer
e o trabalho: escolher as fontes, normalizar, cruzar, e marcar o que conta como
evidencia. **E isso que viaja junto.**

---

## 3. A MEDICAO QUE INTERESSA — O QUE VIAJA E NINGUEM LE

    DISPLAY INPUT != COMPUTATION INPUT.

Comparando os campos que existem nos pacotes publicados com os campos que
alguma linha de interface efectivamente le (comentarios excluidos, porque um
campo citado num comentario nao chega a ecra nenhum):

```
CAMPOS PUBLICADOS               1.935
LIDOS PELA INTERFACE            1.350
TRANSPORTADOS E NUNCA LIDOS       585   (30%)
```

Os maiores, por ocorrencias em `italy-v21.js`:

```
PROVENANCE_STATE           3.042x     EVIDENCE_STATUS_WHY_IT   2.968x
PROVENANCE_STRENGTH        2.948x     PROVENANCE_RECOVERED_VIA 2.939x
PROVENANCE_RECOVERED_FROM  2.233x     LINK_MEANS_IT            1.512x
```

Isto nao e ruido. E o **metodo**: como uma proveniencia foi recuperada, com que
forca, porque uma evidencia conta, o que uma ligacao significa. E exactamente o
que um concorrente precisaria de reinventar.

**Podar so os campos nao lidos de `italy-v21.js`: 10.320.591 → 4.109.002 bytes.
Menos 60%.** Sem tocar numa linha de interface, porque nenhuma os le.

    UM CAMPO QUE NINGUEM LE NAO E APRESENTACAO. E EXPORTACAO.

---

## 4. O PILOTO — A LEI DEIXOU DE VIAJAR

Escolhido por ser pequeno, deterministico, claramente proprietario e com um
grafo de dependencias de um no.

**Antes.** `adama-relevance.js` levava `LEGGE`: as nove clausulas escritas da
lei de relevancia ADAMA — o que conta como oportunidade, qual cadeia e exigida,
porque uma data de expiracao nao e risco. E `italy-casa.js` levava a **mesma
lei outra vez**, dentro de `OPPORTUNITA_ATTUALI`. 2.342 bytes, duas vezes.

**Medido:** nenhuma linha do portal le `LEGGE` nem `LEGGE_ADAMA`. O unico campo
lido de `ADAMA_RELEVANCE` e `VERDETTI`, em `italy-app-model.js`.

**Depois.** O gerador `superficie/it_casa_dados.py` deixa de transportar o texto
e passa a transportar a impressao digital:

```
LEGGE_SHA256      23d3b1e3527861fe...
LEGGE_CLAUSULAS   9
```

Continua possivel provar QUAL lei produziu aquele veredito. Deixa de ser
possivel reconstrui-la a partir do que foi servido.

    PROVENIENCIA NAO EXIGE DIVULGACAO.

**Provas.**

```
PARIDADE            43 vereditos, identicos byte a byte
LEI NO SERVIDO      0 ocorrencias de APPROVAL_EXPIRY_NAO_E_RISCO,
                    BASTA_UM_PRODUTO, CADEIA_EXIGIDA, NAO_ACEITE
NAVEGADOR           5 paginas carregam e renderizam, 0 recusas de politica
BYTES               adama-relevance.js 8.740 -> 6.586 (-25%)
```

A lei nao se perdeu: vive em `leis/adama_relevance.py`, e o veredito continua a
ser decidido la, como sempre foi. So parou de ser publicada.

---

## 5. CONTRATOS

O piloto nao precisou de um pedido de rede, porque a fronteira ja e de build.
Mas a S3 vai precisar — e a forma fica definida agora, para que ninguem a
invente sob pressao.

**CONTRATO DE ENTRADA.** Identidade, filtros, chaves. Nunca um caminho de
codigo, nunca um nome de campo interno, nunca uma expressao a avaliar.

**CONTRATO DE SAIDA — O MINIMO SEGURO.** Devolver o veredito, os campos que a
tela mostra, e a proveniencia por referencia — um id de fonte e uma impressao
digital, nao o registo interno.

Mover uma funcao para o servidor e depois devolver todos os calculos
intermedios, os pesos e as regras accionadas continua a entregar o motor. O
piloto e a prova pequena disso: bastou parar de enviar o texto da lei.

    EXPLICABLE != SOURCE CODE DISCLOSURE.

O utilizador tem direito a saber **porque** um caso e oportunidade. Nao tem de
receber a regra que o decidiu. Se um dia houver LLM: resultado e justificacao
estruturada, nunca o raciocinio interno em bruto.

**CONTRATO DE ERRO.** Codigo, e uma frase. Nunca traceback, caminho de
ficheiro, nome de modulo, SQL ou nome de segredo.

**DENY BY DEFAULT.** Um campo interno novo nao aparece no browser por acidente:
`NEW_INTERNAL_FIELD_EXPOSED_TO_CLIENT` entrou no ratchet da S1, com os 585
campos de hoje congelados como divida conhecida. Divida herdada nao bloqueia;
campo novo bloqueia.

---

## 6. ARQUITECTURA RECOMENDADA

**Manter a fronteira onde ela ja esta: em tempo de build.**

Nao ha vantagem de seguranca em transformar um ficheiro estatico numa funcao
serverless para servir a mesma resposta. Havia um novo dominio de falha, uma
latencia nova, uma superficie de API nova e um endpoint sem autenticacao — em
troca de nada, porque o motor ja nao viaja.

    MORE SERVICES != MORE SECURITY.

O trabalho da S2 e a **projeccao**: o gerador escreve o que a tela le, e nada
mais. Uma decisao por pacote, no dono que ja existe.

Uma funcao de pedido so se justifica quando o cliente precisar de uma resposta
que dependa de **quem** pergunta — e isso e a S3, quando houver identidade.
Nessa altura o dono natural e uma Vercel Function ao lado do portal, porque o
portal ja vive la e a Vercel ja tem os segredos, os logs e o rollback.

---

## 7. AS DUAS PERGUNTAS, QUE SAO DIFERENTES

```
UM CONCORRENTE DESCARREGA O MOTOR PELO BROWSER?
   Antes da S2A   nao o motor, mas o corpus e a lei escrita
   Depois         a lei de relevancia, nao. O corpus, ainda sim.

UM CONCORRENTE DESCARREGA O MOTOR PELO GITHUB?
   SIM. leis/, motor/, coleta/, portoes/, superficie/ — tudo publico.
```

**A segunda pergunta nao melhorou nada, e nao podia.** Mover codigo para o lado
do servidor num repositorio publico nao esconde o codigo: so muda onde ele
corre.

    SERVER-SIDE CODE EM REPO PUBLICO CONTINUA PUBLICO.
    REPO PRIVADO COM MOTOR NO BROWSER CONTINUA A ENTREGAR O MOTOR.

Sao dois controlos, e sao precisos os dois. A ordem importa: a projeccao
primeiro, porque um repositorio privado nao tira do browser o que ja la esta.

---

## 8. REPOSITORIO PRIVADO — PRE-CONDICOES MEDIDAS

Nao foi tornado privado. Medido o que muda:

**1 · O System Map perde a frescura, mas nao mente.** `system-map/app/map.js`
chama `api.github.com` **do browser e sem credencial** — `/commits/{ramo}`,
`/compare`, `/check-runs`. Num repositorio privado essas chamadas passam a 404.
O mapa ja preve isso: fica `UNKNOWN`, com o motivo escrito, e nunca verde.
Degrada, nao parte. A solucao futura e um proxy de leitura do lado do servidor.

**2 · A integracao Git da Vercel continua a funcionar.** E uma app instalada com
acesso concedido, e nao depende de visibilidade.

**3 · Os workflows continuam a funcionar.** `GITHUB_TOKEN` e do repositorio.

**4 · O `system-map-deploy-verify` ja usa token autenticado** para a API, e um
pedido **anonimo** para o URL de preview. O primeiro sobrevive; o segundo e o
mesmo pre-requisito que a S1 ja tinha registado para a proteccao de previews.

**5 · Os links publicos nos handoffs deixam de abrir** para quem nao for
colaborador. Sao documentos internos; o custo e conhecido.

**6 · Nao ha `raw.githubusercontent` no que e servido.** Medido: zero.

```
PRIVATE_REPO_READY_FOR_NEXT_STEP = YES, com uma condicao:
o proxy de leitura para a frescura do System Map antes de virar a chave.
```

---

## 9. O QUE FICA PARA A S2B

1. **Podar `italy-v21.js`** — 110 campos, menos 6,2 MB, no gerador que o escreve.
2. **Podar os outros pacotes** — 475 campos restantes, um dono de cada vez.
3. **Contrato de projeccao por ecra** — a lista do que cada tela precisa, para
   que o deny-by-default tenha o que comparar.
4. **Proxy de leitura do GitHub** — a pre-condicao do repositorio privado.

E so entao o repositorio privado, que fecha a segunda pergunta.

---

# APÊNDICE · S2A-R — os números remedidos na árvore reconciliada

Este documento nasceu na linha de segurança, que partiu de uma árvore anterior
às duas missões de topologia. **Os números acima são os de lá.** A missão S2A-R
juntou as duas linhas, e cada número foi medido outra vez aqui — nenhum foi
herdado.

```
                                       S2A (árvore antiga)   S2A-R (reconciliada)
CAMPOS PUBLICADOS                              —                 1946 -> 1935
TRANSPORTADOS E NUNCA LIDOS                  585                  586 ->  585
BYTES DO CORPUS PÚBLICO (.js)                  —          21.442.219 -> 21.437.624
LEGGE — texto integral servido                 —                    1 ->     0
LEGGE_SHA256                                   —                 presente
LEGGE_CLAUSULAS                                —                        9
VERDETTI                                       —              43 casos, idênticos
VERDICT_DIFFERENCES                            —                        0
FICHEIROS PUBLICADOS                          87                       87
BYTES PUBLICADOS                        30,4 MB                30.430.652
UNKNOWN na classificação do cliente            0                        0
```

**O 585 continua 585, e isso é uma medição, não uma cópia.** A topologia não
mexeu na superfície servida ao browser; o que a S2A tirou foi o texto da lei, e
isso vale 11 campos publicados e 4.595 bytes.

## O ataque que passou, e o portão que nasceu dele

A reconciliação repôs o texto integral da lei no payload, de propósito, para ver
o ratchet reprovar.

**Ele passou.**

`checar_projeccao` só olha para campos que aparecem **duas ou mais vezes** no
pacote — uma regra certa, que existe para não contar identificadores. Mas
`LEGGE` aparece **uma vez só**, no topo. A trava do campo novo nunca foi uma
trava do texto da lei.

```
UM PORTÃO QUE NÃO REPROVA O ATAQUE QUE O ORIGINOU NÃO É UM PORTÃO.
```

Entra `RELEVANCE_LAW_TEXT_PUBLIC`: lê as frases da lei no dono
(`leis/adama_relevance.py`), procura-as nos bytes que o deploy serve, e reprova
se alguma aparecer. Não é heurística de nome de campo — é o texto em si. Só
frases de 60 caracteres ou mais entram, porque um rótulo curto aparece em
qualquer sítio e daria falso positivo. **Cinco frases** vigiadas hoje.

Repetido o ataque com o portão novo:

```
RELEVANCE_LAW_TEXT_PUBLIC
  ficheiro : italia-portale/client/adama-relevance.js
  marcador : todo caso promovido como inteligencia re…
RATCHET = FALHA
```

## O motor, remedido — e o número não é zero

```
SCORE_FUNCTIONS_PUBLIC          1     portale.html:2875
WEIGHTS_PUBLIC                  0
THRESHOLDS_PUBLIC               0
CLASSIFICATION_ARITHMETIC_PUBLIC 0
```

A única função é `const score = (r) => (anyWord(r.issueHay) ? 3 : 0) + …` — um
**ordenador de busca por texto**: decide qual linha já calculada mostrar primeiro
quando alguém escreve na caixa de pesquisa. Não usa pesos da lei, não produz
classe e não altera veredito nenhum.

`ENGINE_CODE_IN_BROWSER = 0` continua verdadeiro para o motor de relevância. E
**não foi criado backend nenhum** para o dizer: `MORE SERVICES != MORE SECURITY`.
