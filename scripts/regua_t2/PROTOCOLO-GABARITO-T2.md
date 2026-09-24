# PROTOCOLO DO GABARITO T2 (CLIMATE / WATER / SOIL) — escrito ANTES dos rótulos novos e de qualquer régua

T2-REGUA · 2026-09-24 · método das réguas já feitas (L1 multilíngue, T8 da YT2): gabarito primeiro,
régua depois, medida no gabarito. Este ficheiro é commitado ANTES do primeiro rótulo novo e antes de
uma única palavra da régua T2 existir em `admissao/admissao.py`.

## Porque existe

Medido na 1.ª onda da Big Collection (BC5, 24/09): as fontes T2 (ARPA Marche, ARPAE) **nunca** podem
dar SIM na Admissão — `PERGUNTAS_DO_UNIVERSO` não tem chave `T2`, e `_do_universo` devolve
`NAO_SE_APLICA` («não há regra escrita do que conta como T2») a tudo.

O gabarito anterior (`curadoria/GABARITO-T2-T12-V1..V3.json`, D4 de 23/09) parou em **13 positivos
T2** — `NAO PRONTO`, abaixo do mínimo de 20. Este protocolo reaproveita esses rótulos (não os refaz)
e junta exemplos que **já estão no acervo** (nada é pedido à rede para o gabarito).

## A pergunta de T2

O universo é uma PERGUNTA ao conteúdo, não à fonte (`ALVO != UNIVERSO`). Para T2:

> **Este conteúdo fala do estado, da previsão ou da tendência do CLIMA, da ÁGUA ou do SOLO?** —
> tempo meteorológico (chuva, temperatura, vento, geada, granizo, humidade), agrometeorologia,
> balanço hídrico, seca, cheia, rega/irrigação e recurso hídrico, humidade/carta/fertilidade do
> solo, eventos extremos, alterações climáticas.

Definição de origem: Atlas `docs/fontes/ATLAS-DE-FONTES-EAME.md:46` — «chuva, temperatura, seca,
geada, ondas de calor, umidade do solo, estresse hídrico, eventos extremos, indicadores
agronômicos» · `leis/territorios.py` (clima, tempo, meteorologia, chuva, seca, solo, água,
irrigação).

## Os rótulos (dois eixos, D2)

`UNIVERSE_MATCH` (é T2?) — o eixo que a régua mede:
- **YES** — o assunto principal é clima/tempo, água (quantidade, rega, seca, cheia) ou solo.
- **NO** — o assunto principal é OUTRO: qualidade do ar urbano (PM10, ozono, dioxinas), ruído,
  radioatividade, resíduos, amianto, campos eletromagnéticos, vida administrativa do organismo
  (concursos, tarifário, carta de serviços, ISO, reclamações), páginas de menu/índice sem conteúdo,
  e conteúdo de outro universo (T3, T5, T10, T12...).
- **NAO_SEI** — texto curto ou mistura em que nenhum assunto domina. Não conta nem como positivo
  nem como negativo; fica declarado com o número.

`SINTONIA_RELEVANT` (a ADAMA — defesa de culturas — quereria isto?): YES / NO / NAO_SEI. Registado,
não medido pela régua. **D2: `UNIVERSE_MATCH != SINTONIA_RELEVANT` → REROUTE**, nunca uma régua
que misture os dois eixos (ex.: solo contaminado é T2 e é irrelevante; boletim agrometeo publicado
por um serviço fitossanitário é T2 mesmo vindo de fonte T3).

Mantém-se a convenção dos rótulos V2/V3: o mesmo texto não é re-rotulado — o rótulo antigo vale.

## Regras do rótulo

1. Lê-se o TEXTO extraído (o mesmo extrator da porta: `coleta/executor_texto_de_html.py` /
   `executor_texto_de_pdf.py`), não o URL nem o nome da fonte.
2. Rotulador: Claude (Opus 5.5), com o trecho que decidiu citado ao lado.
   `VALIDADO_POR_HUMANO = NAO` até o dono validar.
3. Exemplos **distintos**: um por sha256 do texto normalizado (espaços colapsados). Dois boletins
   da mesma série com textos diferentes são dois exemplos — e a série fica anotada (`SERIE`), para
   se ver quanto do gabarito vem de um só molde.
4. Nenhuma palavra da régua é escrita antes de o gabarito ter **≥ 20 YES e ≥ 20 NO**. Se não
   chegar: `NAO PRONTO` com o número, e não se escreve régua.
5. Precisão/recall medidos no mesmo gabarito são **medidos DENTRO da amostra** — ditos assim.
6. Os vizinhos (T3 T4 T5 T7 T9 T10) julgados antes/depois sobre o corpus inteiro:
   `VEREDITOS_VIZINHOS_MUDADOS` tem de ser 0, ou cada mudança explicada.

## De onde vêm os textos (só acervo, sem rede)

- bytes dos gabaritos V2/V3 (`%USERPROFILE%\sintonia-gabarito\GABARITO-T2-T12-V*`), com o rótulo
  que já têm;
- armazém operacional `%USERPROFILE%\sintonia-sala-italia\armazem\XX\it-t2-*` e `it-t12-*`
  (HTML/PDF; os `OBSERVATION` do YouTube não têm texto e ficam fora);
- `data/collection-store/italy/**` e `data/derivados/texto/RAW-*.txt` do Git (os boletins já
  preservados), com a fonte lida do ledger;
- `%USERPROFILE%\sintonia-gabarito\CATALOGO-PROVA-V1` (páginas de entrada — quase só menu).

Os textos ficam FORA do Git (`%USERPROFILE%\sintonia-gabarito\REGUA-T2-V1\`); no Git fica o
manifesto com sha256, a origem e o trecho que decidiu o rótulo.

---

## ADENDA 1 · D29 — A PERGUNTA MUDA PARA JANELAS DE CULTURA (2026-09-24, escrita ANTES do re-rótulo)

A coordenação trouxe a prioridade do dono (D29, `DECISOES-DONO-2026-09-23.md`): «na coleta precisamos
coletar informações relevantes sobre as JANELAS DE CULTURA». A régua T2 passa a servir isto.
Base: Bíblia da Intelligence `CAP-WIN` (`BIBLIA-DE-ENGENHARIA-DA-INTELLIGENCE.md:1795`) — join keys
`CROP × REGION × PHENOLOGY_STAGE × TIME_WINDOW`.

O que ficou do corpo acima: a origem dos textos, o extractor, a regra dos distintos, o `NAO_SEI`
fora da conta, o mínimo 20/20, os vizinhos a 0. O que muda é o **eixo que a régua mede**.

### O eixo novo: `JANELA` (é isto que a régua T2 mede a partir daqui)

> **Este conteúdo sustenta uma janela de cultura?** — diz, para uma cultura agrícola, em que
> estado ela está ou em que condição o campo está, de forma a abrir ou fechar o momento de agir.

- **YES** — boletim agrometeorológico; boletim fitossanitário regional / de defesa integrada;
  fenologia ou estádio; alerta de praga ou doença com monitorização (capturas, voos, infestação,
  limiar de intervenção); sementeira ou colheita com data/estádio; momento de tratamento; condição
  meteorológica ligada por escrito a uma cultura ou prática agrícola (rega, balanço hídrico da
  cultura, geada na floração...). Tem de haver **ligação agrícola escrita** no texto.
- **NO** — ambiente sem ligação agrícola (ar urbano, pólen, radioatividade, resíduos, solo
  contaminado industrial, balneares), vida administrativa, menu/índice, e conteúdo agrícola que não
  fala de momento de agir (mercado, prémio de vinho, história de associação, programa de fundos).
  Os que são clima/água/solo **sem** ligação agrícola levam `ACTION = REROUTE` (D2): não são lixo,
  são de outra pergunta.
- **NAO_SEI** — tempo meteorológico puro (previsão, tabela de chuva) sem uma palavra de cultura ou
  prática: pode abrir uma janela, mas o texto não o diz — fica fora da conta, contado. E o resto
  do costume (texto curto, só título).

`UNIVERSE_MATCH` (clima/água/solo, a pergunta antiga) e `SINTONIA_RELEVANT` continuam registados
nos itens que já os tinham; não são re-rotulados.

### O que a Admissão faz e NÃO faz com isto (leis da coordenação)

- A Admissão **não decide a janela** — isso é da Intelligence (`CAP-WIN`). Só admite e preserva os
  campos (cultura, região, tempo) que o item traz.
- data de calendário ≠ janela · data regulatória ≠ janela · `FACT_TIME` ≠ `PUBLICATION_TIME` ·
  `SOURCE_LOCATION` ≠ `FACT_LOCATION`. A régua não lê datas e não escreve nenhum destes campos.

### Material acrescentado ao corpus (só acervo, sem rede)

- `data/derivados/texto/RAW-*.txt` do Git — os 43 textos já derivados, que incluem o gabarito de
  46 documentos de `provas/a_regra_de_t2.py` (boletins ARPAV fitossanitário, Campania SFR, FEM,
  APOL, ARIF, Molise, Direttive frutticoltura). Esse gabarito foi rotulado por OUTRA sessão para a
  pergunta antiga (clima vs praga); aqui é re-lido para a pergunta nova, e a diferença fica dita.

### T1

Pedido da coordenação: medir se T1 (CROP & PRODUCTION) já cobre fenologia/tratamento. Mede-se
lendo `PERGUNTAS_DO_UNIVERSO` e julgando o gabarito com T1 — sem escrever régua T1.

---

## ADENDA 2 · RECOLHA PELA REDE DE BOLETINS REAIS (2026-09-24, escrita ANTES da corrida)

A coordenação pediu, com a rede de volta (EGR instalado), exemplos REAIS de boletins
fitossanitários/agrometeorológicos regionais no gabarito, **≥ 20 distintos**. A régua não muda
antes de o gabarito crescer; depois de rotulado, mede-se de novo — e estes textos são **novos**
para a régua (não serviram para escolher palavra nenhuma): é a primeira medida FORA da amostra.

- **Onde**: páginas de boletins de serviços regionais (lista fixa em
  `scripts/regua_t2/recolher_boletins.py::SITES`, com a origem de cada endereço: contrato da casa,
  catálogo, ou página inicial do serviço). Pelo menos 8 serviços de regiões diferentes.
- **Como se escolhe o documento (regra fixa, não pelo conteúdo)**: na página de entrada, os links do
  mesmo anfitrião cujo endereço OU texto do link contém `bollettin`, `notiziario`, `agrometeo`,
  `fitosanitar`, `difesa` ou termina em `.pdf`, pela ordem da página, até 3. Se o 1.º alvo for outra
  página de índice (HTML sem esse conteúdo), segue-se UM nível com a mesma regra, dentro do teto.
- **Cortesia**: robots.txt pelo leitor da casa (`gate_de_rota`), teto de **6 pedidos por site**
  (robots + entrada + até 4), 2 s de pausa, sem login, sem pago.
- **Egresso**: `superficie/rede.py::portao_de_egresso("IT")` (consenso) antes de CADA site; se não
  for PASS, a recolha PARA.
- **Bytes fora do Git** (`%USERPROFILE%\sintonia-gabarito\REGUA-T2-V1\recolha\`), sha256 no manifesto
  `scripts/regua_t2/RECOLHA-BOLETINS-V1.json`.
- **Rótulo**: o eixo JANELA da Adenda 1, lido à mão no texto extraído, com o trecho que decidiu.
