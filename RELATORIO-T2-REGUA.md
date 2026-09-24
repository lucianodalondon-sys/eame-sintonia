# RELATÓRIO · MISSÃO T2-REGUA — a régua da Admission para T2, com foco D29 (janelas de cultura)

Branch `regua-t2-v1`, a partir de `origin/bc4-correcoes-v1` (= instalado). **NÃO instalado** — quem
instala é o coordenador.

## Em palavras simples

- A Admissão é a porta que decide o que entra na Sala. Para T2 ela não tinha regra nenhuma: dizia
  «não se aplica» a tudo. Por isso as fontes T2 da 1.ª onda nunca podiam dar SIM.
- Agora T2 tem uma régua — uma lista de palavras que a porta procura no texto. Por ordem do dono
  (D29), ela deixa entrar o que ajuda a saber **a janela da cultura**: o momento de semear, tratar
  ou colher, em cada cultura e região. Para dizer SIM, o texto tem de ter **as duas coisas juntas**:
  uma condição do campo (chuva, temperatura, seca, rega…) **e** uma ligação agrícola escrita (fase
  da planta, floração, limiar de intervenção, capturas de praga, tratamento fitossanitário, boletim
  agrometeorológico). Só metade → «não sei» (não entra e não é rejeitado).
- A porta **não decide a janela**. Só deixa entrar e guarda o que o texto traz. A janela é trabalho
  da Intelligence (`CAP-WIN`).

## Números (todos com o denominador)

| O quê | Resultado |
|---|---|
| Textos juntados do acervo, sem rede | **504** distintos (`scripts/regua_t2/inventariar_t2.py`) |
| Gabarito T2-V2 (eixo JANELA), rotulado à mão | **45 YES / 225 NO / 117 NAO_SEI** (mínimo era 20/20) |
| Régua no gabarito | **45 de 45** YES entram; **1 de 225** NO entra → precisão **0,978**, recall **1,0** |
| Sem a série ARPAV (8 boletins do mesmo molde) | precisão **0,974**, recall **1,0** |
| Fora do gabarito (1.259 textos do acervo) | **2** SIM, que são **1** texto (artigo sobre a pera Conference, em 2 cópias): lido, **não** é janela |
| Outros universos (T3 T4 T5 T7 T9 T10) antes/depois | **0** vereditos mudados em **7.554** julgamentos |
| Mutação (partir o código de propósito, numa cópia) | **9 de 9** mutantes mortos |
| T1 (CROP & PRODUCTION) | **não tem régua**: as 45 janelas do gabarito dão **45/45 NAO_SE_APLICA** em T1 |

## ⚠️ Ressalvas — sem arredondar

1. **O número é de dentro da amostra.** As palavras foram escolhidas olhando para o gabarito e
   medidas nele. E a leitura «fora do gabarito» (14 SIM na 1.ª versão) serviu para apertar a régua —
   depois disso, ela já não é inteiramente de fora. Um teste limpo pede textos novos que ninguém viu.
2. **Os rótulos são meus** (Claude). `VALIDADO_POR_HUMANO = NAO`.
3. **Houve uma medição que proibia a régua T2** (`provas/a_regra_de_t2.py`, 23/09): para a pergunta
   antiga («isto é clima e não praga?»), uma lista de palavras treinada num publicador acertava
   0 de 10 no outro. Essa conclusão **continua certa para a pergunta antiga**. A D29 mudou a
   pergunta: os boletins fitossanitários, que aquela prova tinha de deixar de fora, agora são o que
   tem de entrar. As duas guardas que travavam T2 passaram a ler o portão da medição nova
   (`scripts/regua_t2/portao_t2.py`), com a razão escrita. A prova antiga continua a medir pelo
   mecanismo antigo, sem mudança.
4. **20 dos 45 YES não têm fonte identificada no Git** (`SOURCE_ID = NAO SEI`): são textos já
   derivados em `data/derivados/texto/`, cujo registo não guarda a fonte. Os publicadores leem-se
   no próprio texto (Serviço Fitossanitário do Veneto, FEM, Campania, Molise, Lazio/Tuscia, ARIF).
5. **Inglês não foi medido**: não há nenhum texto inglês de janela no gabarito. A lista inglesa
   existe para a porta não se calar, e o número dela é NÃO SEI.
6. **3 dos YES do eixo antigo (clima) saíam NAO** pela regra antiga de «prova de outro universo»
   (páginas de solo contaminado com «decreto», uma brochura com «ricerca»). No eixo D29 esses textos
   são NO/REROUTE, e o problema desaparece — mas a regra de prova das réguas antigas continua a
   casar por pedaço de palavra, o que é outra missão.
7. **O que a 1.ª onda trouxe de T2** (ARPAE: oferta de emprego; ARPA Marche: jornadas de pólen)
   **continua a não entrar**, e está certo: não é janela.

## O que está feito

- `admissao/admissao.py`, `VERSAO_DA_REGRA = "8"`:
  - `PERGUNTAS_DO_UNIVERSO["T2"]`: 18 conceitos de **condição** (it/pt), por palavra inteira, cada
    conceito conta uma vez («pioggia|piogge|…»); `PERGUNTAS_EN["T2"]` idem.
  - `ANCORAS["T2"]`: 6 conceitos **fortes** (fenologia, estádio, defesa integrada, limiar, capturas,
    tratamento fitossanitário) + `agrometeo` (só conta com 2 condições, porque é nome de menu).
  - O que ficou de fora e porquê está escrito ao lado de cada lista: `clima`, `meteorologia`,
    `suolo`, `acque`, `trattamento`, `raccolta`, nomes de cultura… Cada um com o número medido.
  - T2 é **transversal**: uma palavra de tempo nunca serve de prova para dizer NAO a outro universo
    (o boletim de praga fala de chuva e continua T3). Mesmo desenho e mesmos nomes da régua T8
    (`youtube-regua-t8-v1`), para as duas se juntarem: `PALAVRA_INTEIRA`/`TRANSVERSAIS` passam a
    `{"T2","T8"}`. **Conflito de merge esperado** em `_do_universo` e nesses dois conjuntos.
  - Metade do sinal → NAO_SEI com motivo `SEM_LIGACAO_AGRICOLA` (+ marca `d2: REROUTE_POSSIVEL`)
    ou `SEM_CONDICAO_DO_CAMPO`. Nunca NAO.
- Gabaritos, medições e mutação: `scripts/regua_t2/` (protocolo commitado **antes** de cada rótulo).
- Testes: `tests/test_regua_t2.py` (21), guardas de T2 ajustadas com razão escrita
  (`tests/test_a_regra_de_t2.py`, `tests/test_o_canario_da_collection.py`), e
  `tests/test_estagio_atravessa_a_fronteira.py` passou a usar T1 (o teste usava T2 por não ter
  régua; a pergunta dele é o tempo do facto).
- Nos testes tocados, as falhas que sobram **já existiam antes** (medido no instalado):
  `test_o_mapa_da_porta_vive_num_sitio_so` (barra do Windows) e
  `test_correr_julga_a_unidade_da_fronteira` (erro).

## T1 — o que falta

T1 **não tem régua nenhuma** na porta. O Atlas (`docs/fontes/ATLAS-DE-FONTES-EAME.md:45`) põe em T1
«calendário agrícola, desenvolvimento da cultura, previsão de safra, área, produção,
produtividade». Fenologia e estádio são hoje as âncoras de T2; para T1 falta: (1) um gabarito T1
(≥ 20/20) — não existe; (2) conceitos de **produção** (superfície/área, produção, rendimento/resa,
estimativa de colheita, regiões produtoras); (3) decidir com o dono se a fenologia fica em T2
(janela) e em T1 (desenvolvimento) ao mesmo tempo — pela régua transversal pode ficar nas duas.

## Prova pela porta canónica com banco descartável

Ver a secção «PROVA D29» abaixo (preenchida no fim).

## Provas fora do Git (caminho e sha256)

- textos do gabarito: `%USERPROFILE%\sintonia-gabarito\REGUA-T2-V1\textos\<id>.txt` — sha256 de
  cada um em `scripts/regua_t2/GABARITO-T2-V2.json` (`TEXTO_SHA256`), conferido pela medição
  (`SHA_NAO_CONFERE = 0`).
- inventário: `%USERPROFILE%\sintonia-gabarito\REGUA-T2-V1\INVENTARIO.json`.
- rótulos brutos: `…\REGUA-T2-V1\rotulos.tsv` e `…\rotulos-janela.tsv` (o conteúdo está nos
  gabaritos do Git).
