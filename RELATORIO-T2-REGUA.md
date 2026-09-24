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

`scripts/regua_t2/PROVA-D29-PORTA-CANONICA-OFFLINE.json` (driver `prova_d29_porta.py`).

- **Pela VPN IT: BLOQUEADA.** O portão de egresso consulta `ipinfo.io`, que respondeu 429 («limite de
  pedidos», várias sessões na mesma saída) de 16:55Z a 17:10Z. País = UNKNOWN → o portão bloqueia,
  e está certo. Nenhuma página foi pedida.
- **Sem rede, pela porta canónica, numa cópia (worktree destacada) com banco descartável próprio:**
  reprocessei 6 corridas que já estão no ledger do Git (`--so-a-porta --colheita-da-corrida`,
  `universo=T2`, proxy morto). Resultado no banco: RAW 16 · DERIVED 9 · ESTRUTURADO 9 · **Sala 8**.
  Os 8 são todos boletins de janela (ARPAV ×4, Campania SFR, Terre dell'Etruria mosca, ARIF, APOL).
  Nenhuma notícia de mercado entrou. `FACT_TIME`, `FACT_LOCATION` e `SOURCE_LOCATION` chegaram à
  Sala como `NAO SEI` — a porta não inventou tempo nem lugar.
- **Defeito pré-existente achado (não é da régua):** 2 das 6 corridas (Campania e ARIF de 18/09)
  rebentam no ingresso — `coleta/ingresso.py:829`, `TypeError: Artefato() got multiple values for
  keyword argument 'CONTENT_TYPE'`. Os mesmos boletins entraram pela outra corrida.
- **Lição:** `--filtro fonte=` não recorta uma colheita reprocessada — a corrida PILOT trouxe 10
  observações de várias fontes.
- O banco foi desligado (sem `postmaster.pid`).

## Provas fora do Git (caminho e sha256)

- textos do gabarito: `%USERPROFILE%\sintonia-gabarito\REGUA-T2-V1\textos\<id>.txt` — sha256 de
  cada um em `scripts/regua_t2/GABARITO-T2-V2.json` (`TEXTO_SHA256`), conferido pela medição
  (`SHA_NAO_CONFERE = 0`).
- inventário: `%USERPROFILE%\sintonia-gabarito\REGUA-T2-V1\INVENTARIO.json`.
- rótulos brutos: `…\REGUA-T2-V1\rotulos.tsv` e `…\rotulos-janela.tsv` (o conteúdo está nos
  gabaritos do Git).

---

## T2B (24/09, tarde) — com a rede de volta

### Em palavras simples

Fui buscar boletins novos aos sites dos serviços regionais, com o portão de rede novo (consenso) a
confirmar a Itália antes de cada site. Das três idas vieram **16 boletins de janela novos**, de 5
serviços (ARPAE, ARIF Puglia, Campania — 5 províncias —, ARPAV — 4 zonas —, APOL). Juntos com os de
antes, o gabarito tem agora **61 boletins reais que sustentam janela** (o pedido era ≥ 20).

Estes 16 foram a **primeira prova de fora**: a régua nunca os tinha visto e **apanhou os 16**. Mas nas
30 páginas novas que NÃO são janela, disse «sim» a **8** — precisão de fora **0,67** (dentro da amostra
era 0,98). 7 desses 8 entraram pela via «agrometeo + 2 palavras de tempo»: são páginas que
**descrevem** um serviço agrometeorológico (menus, «o que fazemos»), não boletins.

No caminho real, antes da régua, o detector de capa barra 3 dessas páginas e põe 1 em quarentena:
**chegariam à Sala 4 (3 textos distintos)**.

### A decisão que fica para o dono/coordenação (medida, NÃO aplicada)

| Opção | Dentro da amostra | Fora da amostra |
|---|---|---|
| **atual** (`agrometeo` + 2 condições) | 45/45 · 1 erro | 16/16 · **8 erros** (prec 0,67) |
| `agrometeo` + 3 condições | 45/45 · 1 erro | 16/16 · 5 erros (prec 0,76) |
| sem a via `agrometeo` | 39/45 · 1 erro | 14/16 · 2 erros (prec 0,88) |

⚠️ Estas alternativas foram medidas DEPOIS de ver os textos de fora: aplicar uma torna-os dentro da
amostra, e a próxima medida limpa precisa de textos novos outra vez.

### Recolha (sem login, sem pago)

- 3 idas, 15 serviços na 1.ª, **122 pedidos no total**, robots lidos, ≤ 6 pedidos por anfitrião por
  ida, 2 s de pausa, egresso por consenso antes de cada site (PASS em todos). A 1.ª e a 2.ª ida
  trouxeram sobretudo páginas-índice; a 3.ª usou as rotas dos contratos da casa: **14 PDFs em 18
  pedidos**. Protocolo escrito antes de cada ida (`PROTOCOLO-GABARITO-T2.md`, Adenda 2).
- Bytes fora do Git em `%USERPROFILE%\sintonia-gabarito\REGUA-T2-V1\recolha\`, sha256 de cada um
  em `scripts/regua_t2/RECOLHA-BOLETINS-V1..V3.json`.

### Dois defeitos meus achados e consertados

1. EGR: a guarda do ipinfo contava `mutar_egresso.py` e o próprio teste → permitidos com o porquê,
   e contraprova (um consumidor novo com o URL do ipinfo fica vermelho). `egresso-consenso-v1 @ f069cf8a`.
2. EGR: o teste da chave de ambiente da cache falhava quando a máquina já corria com
   `HTTPS_PROXY=127.0.0.1:9`. `egresso-consenso-v1 @ fa17ccdf`. **Os dois estão também neste ramo.**

## PLANO DE INSTALAÇÃO DA RÉGUA T2 (o coordenador instala; eu NÃO instalo)

Base: este ramo já tem a linha instalada (`5c4daf5a`) juntada (merge `2b7c5238`).

**Writeset** (fora os gerados do mapa):

| Ficheiro | O que muda |
|---|---|
| `admissao/admissao.py` | **o único código de produção**: régua T2 (condições + âncoras), `PALAVRA_INTEIRA`/`TRANSVERSAIS = {"T2"}`, `_casa`, prova-noutro-universo por conceito, `VERSAO_DA_REGRA = "8"` |
| `provas/a_regra_de_t2.py` | a prova antiga mede pelo mecanismo antigo (`T2_CANDIDATA_V0`) |
| `tests/test_regua_t2.py` (novo), `tests/test_a_regra_de_t2.py`, `tests/test_o_canario_da_collection.py`, `tests/test_estagio_atravessa_a_fronteira.py` | guardas de T2 seguem `scripts/regua_t2/portao_t2.py` (lê a medição V3); o teste da fronteira passa a usar T1 |
| `tests/test_egresso_consenso.py` | os 2 consertos da EGR (também em `egresso-consenso-v1`) |
| `scripts/regua_t2/**`, `RELATORIO-T2-REGUA.md` | gabaritos, medições, recolha, mutação, prova — evidência, não corre em produção |
| `system-map/data/architecture.declared.json` | peça `C-REGUA-T2-JANELA` |

**Passos**
1. Juntar `regua-t2-v1` na linha instalada (esperar conflito só nos `*.generated.json` do mapa → regerar pela cadeia).
2. Correr `tests.test_regua_t2 tests.test_a_regra_de_t2 tests.test_o_canario_da_collection tests.test_egresso_consenso` (aqui: OK).
3. `pacote/metricas_canonicas.py --sync` com o PyYAML emprestado: há testes novos (aqui mede `NOT_MEASURABLE` por falta do PyYAML).
4. Efeito esperado em produção: pares (item, T2) deixam de sair `NAO_SE_APLICA`. No acervo medido (1.309 textos): **75 SIM · 765 NAO_SEI · 469 NAO** em T2; **0 mudanças** nos outros 6 universos (7.854 julgamentos). O que a v7 deu a T2 pode ser reaberto pela versão 8.
5. Decidir a via `agrometeo` (tabela acima) — ANTES ou DEPOIS de instalar; se mudar, medir de novo com textos novos.
6. Voltar atrás = reverter o merge (a versão da regra volta a 7).
