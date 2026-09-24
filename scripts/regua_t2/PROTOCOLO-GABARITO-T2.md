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
