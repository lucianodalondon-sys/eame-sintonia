# Três hero cases da Espanha — fechados com prova e contraprova

Data: 2026-08-30 · Branch `claude/sintonia-eame-collection-es` · 365 testes OK

---

## O que esta rodada tinha que provar

Que dá para transformar dado em decisão. O teste era: o que está acontecendo, onde, é incomum, a ADAMA tem resposta, essa resposta é explícita, ainda dá tempo, e o que é fato contra o que é interpretação.

Três casos foram fechados. Nenhum foi forçado a sobreviver — e dois quase não sobreviveram do jeito que eu tinha escrito.

## Os três

| | CASO A · olivo | CASO C · cereal | CASO B · milho |
|---|---|---|---|
| tipo | **AGIR AGORA** | **PREPARAR** | **PLANEJAR** |
| issue | repilo | gramíneas / vallico | *Amaranthus palmeri* |
| região | Cádiz e Huelva | nacional | Huesca e Lleida |
| sinal | alta em 2 províncias | nenhum reivindicado | 3 avisos oficiais |
| janela | **aberta** | 2–5 meses | fechada até abr/2027 |
| resposta ADAMA | 2 de 180 | 10 genéricos + 1 com espécie | genérica, sem espécie |
| conflito regulatório | sim | não | não |

## As quatro contraprovas que mudaram alguma coisa

**1 · O máximo de Huelva sobreviveu ao teste que podia matá-lo.** Se as 7 parcelas que restaram fossem as historicamente mais doentes, a alta seria artefato de cobertura. Medi ano a ano, 2017–2025, a média só dessas 7 contra a média de toda a província: 5,04/4,20 · 4,88/5,36 · 2,98/3,68 · 3,76/3,73 · 2,47/3,05 · 1,57/1,45 · 1,17/1,19 · 3,00/3,26 · 6,26/6,45. Elas acompanham a província e na maioria dos anos ficam abaixo. A alta não vem de quem sobrou.

**2 · Mas "sinal de 6 dias" era meu erro.** Era a data de geração do arquivo. As leituras de repilo de Huelva vão até 14/06 e as de Cádiz até 27/05 — 77 e 95 dias. E o caso não é de Huelva: é do oeste. Huelva tem o maior valor da série sobre **18 leituras**; Cádiz sustenta o mesmo nível com **141** e rede estável.

**3 · O zero do Amaranthus só vale porque a ficha sabe dizer espécie.** Li o texto das fichas dos 7 produtos ADAMA de folha larga em milho: Amaranthus 0, bledo 0, palmeri 0. Um zero assim não vale sozinho — então varri as 96 fichas ADAMA preservadas: 7 citam espécie pelo nome (halepense, Echinochloa, Sorghum, Abutilon, Cyperus, Convolvulus), e uma delas é o próprio NICOPERTS. O formato sabe, a ADAMA usa, e Amaranthus não aparece em nenhuma das 96. `GENERIC_WEED_RESPONSE`.

**4 · Duas hipóteses minhas foram refutadas pela minha própria medição.** No olivo: "15-08-2026 é vencimento de substância" — são 16 tebuconazóis no par e 13 vão até 2028. No cereal: "a ADAMA depende de um único modo de ação" — são 10 registros por cultura com pelo menos quatro químicas.

## O que ficou mais interessante do que a hipótese

**Olivo.** O produto com problema regulatório (NEPTUNE) é justamente o que já estava fora de janela — "primeira aplicação antes da floração", prazo de 120 dias. O produto **em** janela (CUPROXI FLO, BBCH 10-85, prazo 7 dias) não tem problema regulatório, e a fenologia **observada** em agosto está em BBCH ~75-81. São duas conversas, não uma.

**Cereal.** O estreito não é a química, é o *claim por espécie*. ACCRESTO e TOPIK 24 EC não são duas respostas: são o mesmo formulado (IdFormulado 3710), mesma caducidad, mesma inscrição de 1994 — e são o único lugar onde a ADAMA nomeia espécie. E a etiqueta exclui a cebada. Cebada × vallico: 3 registros no país, 0 ADAMA. Cebada × avenas locas: 10, 0 ADAMA. Sobre a maior cultura do país em área.

**O padrão que se repete nos dois:** cobertura genérica ampla, cobertura por espécie estreita. Duas culturas, mesmo método, mesmo instrumento. Dois não é amostra, mas já é padrão para investigar.

## Ask Sintonia — 12 perguntas

7 respondíveis, 3 parciais, **2 recusadas**. As recusas são de propósito: *"o Neptune ainda pode ser vendido?"* e *"quanto vale em euros?"*. Nas duas, recusar é a resposta certa — e no caso do Neptune a resposta útil não é sim nem não, é a assimetria medida.

Erros de falsa confiança encontrados nesta rodada: **3**, todos meus, todos achados só porque a pergunta virou medição.

## O que continua faltando

Nomes dos municípios de Huesca (código catastral não mapeado por aproximação, de propósito). Motivo do 15-08-2026 no Neptune. Resistência a ACCase em *Lolium rigidum* espanhol. Leitura de repilo em Huelva/Cádiz depois de junho. Fonte de aviso de cereal para Castilla y León. Equivalente aragonês das ADV catalãs. `COMMERCIAL_CLOCK` nos três casos.
