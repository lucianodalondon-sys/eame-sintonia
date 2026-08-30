# Madrugada EAME — congelar, revisar, abrir a França, contratar a comparabilidade

`2026-08-30` · entrada `afcadd8` · saída `fbe8f6b` · 7 commits na branch principal + 1 branch nova

---

## O que esta madrugada não fez

Não coletou "mais Espanha". Nenhuma cultura nova, nenhum crawl amplo, nenhuma rota paga. **Custo em rotas pagas: US$ 0,00.** Tudo veio de API pública gratuita, de derivação sobre o acervo, ou de `git show` nas branches paralelas.

## O freeze deixou de ser adjetivo

`SPAIN-DEMO-CONTENT-V1` agora carrega sha256, tamanho e último commit de cada um dos 13 artefatos canônicos, mais o HEAD que os sustenta. `scripts/freeze_es.py` confere e sai com código 1 se qualquer um divergir.

**E ele reprovou sozinho no meio da noite** — quando o cartão do cereal mudou. O re-freeze para `V1.1` é deliberado e datado, com a lista dos dois artefatos que mudaram e o motivo. Era exatamente para isso que ele existia.

## A geografia do Lolium inverteu o que eu tinha publicado

Os dois levantamentos nacionais que o artigo de 2021 citava estavam sem resumo no Crossref e no Semantic Scholar. Os resumos completos estavam no **DIGITAL.CSIC, no modo full de metadados**. Duas chamadas.

Levantamento aleatório 2012-13, Castilla y León e Cataluña:

| | Castilla y León | Cataluña |
|---|---|---|
| chlortoluron (PSII) | 51 % R | 92 % R |
| chlorsulfuron (ALS) | 75 % R | 75 % R |
| diclofop (ACCase) | **74 % ainda suscetível** | 83 % R |

Eu tinha escrito que "o produto com claim de espécie está no grupo comprometido". O clodinafop é ACCase — e o ACCase é o modo de ação com o quadro **mais favorável exatamente onde está a área**. A frase generalizava uma região para o país: verdadeira na Cataluña, falsa em Castilla y León.

`CASE_GEOGRAPHY` passou de `MEASURED_SAMPLING_LOCATIONS_ONLY` para `REGIONAL_SURVEY_MEASURED`. A perna fraca está dita: o dado é de 2012-2013 com tendência de alta.

## As paralelas, revisadas sem merge

**ADAMA datacenter** (`8680c58`) — `USABLE`: mapa regulatório do milho (foi ele que deu os 7 produtos do teste decisivo), vocabulário 448×708, portão de acesso com 5 rotas 403 inclusive `/robots.txt`. `PARTIAL`: o `PRODUCT-INTELLIGENCE`, vazio e corretamente marcado. `USABLE MAS NÃO EXERCITADO`: o coletor de 937 linhas, que nunca rodou contra o site porque o site nega o cliente.

**ADAMA local** — nenhuma branch casa os prefixos. `PENDING`, e não afirmo que a missão não existe.

**Itália** (`1401f23` na revisão) — gate camada a camada. `REGULATORY` YES, `SOURCE_UNIVERSE` YES, `DEMO_CONTENT` YES para 3 casos, `PRODUCT_INTELLIGENCE` PARTIAL, `RESEARCHER` PARTIAL, e `TECHNICAL_NETWORK` / `CREATORS` / `PUBLIC_VOICE` todos NO. **A camada que falta tem nome: voz.**

## França aberta em branch própria

Quatro das onze camadas já estavam no acervo e não foram refeitas: E-Phy da ANSES (15 140 produtos, 267 da ADAMA), usos autorizados já tabelados (18 558 / 504), área NUTS2 do Eurostat, distribuição via SIRENE.

**O número que muda a prioridade EAME:** milho grão 2024 — França **1 593,9 mil ha** contra 239,1 da Espanha. 6,7 vezes. A antiga Aquitaine sozinha tem 276,4 mil ha, mais que a Espanha inteira.

Dois bloqueios medidos: os 17 subdomínios `draaf.*` dão timeout de 50 s depois do CONNECT aceito (o domínio-mãe responde em 0,97 s), e `adama.com/france` dá 403 de borda Akamai — **terceiro país, mesmo bloqueio**.

## O contrato de comparabilidade, e por que EAME continua NO

3 dimensões `COMPARABLE`, 5 `PARTIAL`, 2 `NOT`.

`REGULATORY_EXPIRY` só é comparável porque fui conferir a convenção no código: a Espanha soma **meses de calendário**, igual à Itália. A Itália mediu que a outra convenção muda 13 registros. Sem essa checagem os números pareceriam comparáveis e não seriam.

A distinção mais cara ficou parcial: a Espanha tem data de **amostragem** por leitura, a Itália tem data de **publicação** de boletim. Um "sinal de 26/08" não significa a mesma coisa nos dois.

O contrato de relação tem os 17 campos, os 9 tipos e **zero registros**. Documentei a relação que mais tentava entrar — `REGULATORY_STATUS_LAG`, que *seria* comparável — e por que não entrou: `ACTIONABILITY` vazia. Uma relação que não muda decisão é enfeite.

## Um protótipo, oito perguntas, oito nãos

`scripts/proto_es.py` gera a tela inteira do pacote congelado. **Nenhum texto de caso foi escrito na interface.**

O componente que carrega a tese é a **tripla**: valor, suporte amostral e idade do dado em três células inseparáveis. Huelva aparece com 8,83 % — o maior número da página — e ao lado, no mesmo peso, "18 leituras · 7 parcelas · menor n da série".

E o protótipo revelou o que o freeze escondia: **o pacote é de máquina, não de tela**. Os artefatos foram escritos sem acentuação e a tela os renderiza literalmente. Corrigir na tela quebraria a propriedade que dá valor ao protótipo. `DISPLAY_LAYER = MISSING`.
