# ONDA2-PLANO — a 2.ª onda web NO PAPEL, sobre o sistema instalado

Ramo `onda2-plano-v1`, nascido de `5ba9647e` (produção, R1 instalada 01:50).
Medido em 25/09/2026, entre 02:08 e 02:15 (BRT). Não houve **nenhum pedido de rede de coleta**, nem escrita no vivo, na Sala ou no armazém.

**Como se mediu.** Clone de `5ba9647e` em `C:/onda2/clone`, com os 14 livros vivos de
`source-curator-service-v1` copiados por cima. A lista de livros e o sha256 de cada um estão em
`FOTO-DOS-LIVROS-20260925.txt`. Sobre esse clone correram três coisas:
- `scripts/micro_coleta/micro_coleta.py plano`, a ferramenta do runbook e a mesma que a G3 lê;
- `ferramentas/big_collection/coorte_unica.py`, com a saída numa pasta de rascunho;
- `orquestrador/orquestrador.py … --so-plano`.

⚠️ **É uma fotografia das 02:10.** O robô de fontes está a trabalhar agora (tarefas REPAIR_CONTRACT da
R1 criadas às 02:06), e os números abaixo vão mudar nas próximas horas.

---

## 1. A coorte de hoje

**18 prontas, as MESMAS 18 da 1.ª onda.** O ensaio da G3 dá a mesma lista, com as três provas
(contrato executável, rota validada, canário com ≤ 7 dias) em todas.

Painel do portão: 145 READY, das quais 45 pela régua de hoje e 100 pela régua antiga (LEGACY);
39 elegíveis; 5 à espera de revisão humana.

| SOURCE_ID | Domínio | Família | Janela D29 (REND) | Canário (dias) | 1.ª onda |
|---|---|---|---|---|---|
| IT-T10-018 | myfruit.it | T10 mercado | **SIM, forte** (o texto colhido fala de janela) | 1,7 | 3 SIM |
| IT-T10-021 | plantgest.imagelinenetwork.com | T10 mercado | NÃO | 2,4 | 0 docs |
| IT-T10-022 | zootecnicainternational.com | T10 mercado | NÃO | 1,7 | 0 docs |
| IT-T2-034 | arpa.marche.it | T2 clima/agrometeo | NÃO (REND) · ver risco R3 | 2,4 | 0 docs |
| IT-T2-051 | arpae.it | T2 clima/agrometeo | NÃO (REND) · ver risco R3 | 2,4 | 0 docs |
| IT-T5-090 | istat.it | T5 | NÃO | 2,0 | 0 docs |
| IT-T7-017 | riuniteciv.com | T7 | NAO_SEI (só tema) | 1,7 | 0 docs |
| IT-T7-021 | etvilloresi.it | T7 | NÃO | 2,4 | 1 NAO_SEI |
| IT-T7-033 | chianticlassico.com | T7 | NAO_SEI (só tema) | 1,7 | 0 docs |
| IT-T7-042 | consorziobalsamico.it | T7 | NAO_SEI (só tema) | 1,7 | 1 NÃO + 2 NAO_SEI |
| IT-T7-043 | agrofarma.federchimica.it | T7 | NAO_SEI (só tema) | 1,7 | 0 docs |
| IT-T7-112 | cia.it | T7 | NAO_SEI | 2,0 | 0 docs |
| IT-T7-117 | caf-cia.it | T7 | NÃO | 2,0 | 1 NÃO |
| IT-T7-118 | cia.it | T7 | NAO_SEI | 2,0 | 0 docs |
| IT-T7-121 | cia.it | T7 | NÃO | 2,0 | 0 docs |
| IT-T7-123 | cia.it | T7 | NAO_SEI | 2,0 | 0 docs |
| IT-T7-135 | cia.it | T7 | NÃO | 2,0 | 1 NÃO |
| IT-T7-141 | ciatoscana.eu | T7 | NAO_SEI | 1,9 | 0 docs |

**As 21 elegíveis que ficam fora, com o motivo:**
- 10 não têm contrato na tabela do coletor (IT-T2-056, IT-T2-106, IT-T5-101, IT-T7-053, IT-T7-058,
  IT-T7-100, IT-T7-115, IT-T7-120, IT-T12-024 e IT-T12-117);
- 8 são T8 sem receita web (o YouTube não é web);
- 3 são T12 sem receita web (duas delas também sem contrato);
- 1 é T9 sem receita web (IT-T9-021);
- 1 tem a rota em CAPABILITY_BLOCK (IT-T5-049).

**Fora do portão ficam 106:** 99 READY_LEGACY, 5 RETIRADA_POR_DECISAO (D9) e 2 HUMAN_REVIEW_REQUIRED
(IT-T5-064 e IT-T8-050).

**A R1 ainda não mexeu na coorte.** Das 46 fontes revistas pela R1, 23 das 25 «READY revistas»
(21 LIMPA e 4 ACESSO_PARCIAL) estão, no livro vivo, em **CONTRACTED_CANARY_FAILED**. Só 2 LIMPA estão
READY/ELIGIBLE (IT-T12-024 e IT-T12-117), e ambas ficam fora por falta de contrato e de receita T12.
A R1 instalou o reparo como **tarefas do robô** (REPAIR_CONTRACT → CANARY_PENDING → VALIDATE_ROUTE), e
não como promoção direta: 63 DONE, 1 IN_PROGRESS, 1 PENDING e 2 BLOCKED. O relatório da R1 prevê
READY 143 → ~168 em 2 a 3 horas de fila **com rede**.

## 2. O disparo previsto (`--so-plano`), para a coorte de 18

- Frase de cada fonte: `orquestrador/orquestrador.py agronomo --filtro fonte=<ID> --filtro universo=<U> --filtro pais=IT`.
  O plano confirmou que todas resolvem para o executor web (`FRASE_RESOLVE`). O `--so-plano` de uma
  delas (IT-T7-112) respondeu: `italia-recorrente -> coleta/italy_executor.py`, HTTP direto, gratuito,
  com os 4 contratos (procedência, tempo do fato, lugar do fato, recibo). «Nada correu.»
- **Pedidos por site:** o teto de 5 continua **intocado** (`CORTESIA_PADRAO.TETO_POR_HOST = 5`, em
  `coleta/italy_pilot_collect.mjs`). Ele conta-se **por site DENTRO DE UMA CORRIDA** e cada fonte é
  uma corrida. Previsão = 1.ª onda, porque o contrato e o MAX_TARGETS são os mesmos: 5 myfruit,
  5 etvilloresi, 5 consorziobalsamico, 4 caf-cia, 3 istat, e 2 a 3 nas outras. **Teto da onda:
  ≤ 90 pedidos** (18 × 5); a 1.ª onda gastou 54.
- **Tempo:** a 1.ª onda levou 359 s de corridas (de 09:05 a 09:12, cerca de 7 min). Previsão: 7 a
  10 min, mais os portões de egresso antes e depois de cada corrida.
- **Disjuntores** (`bc5_big_collection.py`, runbook §6), que param TUDO quando:
  - o egresso sai de IT, antes ou depois;
  - uma contagem da Sala desce;
  - uma corrida passa de 30 min;
  - 3 fontes seguidas dão FAILED;
  - o C6 (bypass) não dá PASS;
  - o C4 tem a cadeia partida;
  - os pedidos por site passam do teto.

  Uma fonte cujo gate no instante não é ELIGIBLE não corre.
- **VPN:** o `micro_coleta.medir_egresso` já pergunta ao **portão de consenso** (`superficie/rede.py`,
  três verificadores). Às 02:10 a VPN estava em IT (vigia: PASS IT às 01:43).

## 3. O que falta para a G3 congelar

1. **Esperar que o robô termine a fila da R1** (REPAIR_CONTRACT e canários, com rede) e **medir de
   novo** o `plano`. Congelar agora congelava as mesmas 18.
2. **A ferramenta de congelar não está na produção.** O `coorte_unica.py` instalado (`5ba9647e`) não
   tem `--congelar`. O protocolo de congelamento (`ESTADO=CONGELADA`, exige `--instalacao=<commit>` e
   `--demotion=<ref B5>`) vive só em `origin/coorte-unica-v1` (`2d605ef6` e `62a7cade`), que não é
   antepassado de `5ba9647e`. Ou se instala essa versão, ou a G3 corre a partir desse ramo.
3. **O que congela:** `ferramentas/big_collection/COORTE-BIG-COLLECTION-V1.json`, commitado. A 1.ª onda
   ficou em `62a7cade`, com 18 fontes e os livros vivos com o **mesmo sha256 antes e depois**, com o
   escritor parado.
4. **O que o prova:** `LIVROS_SHA256` no ficheiro, igual à fotografia tirada com o robô parado;
   `ARVORE` = o commit instalado; `PLANO` com hash; as 3 provas por fonte.
5. ⚠️ **O disparador não lê o ficheiro commitado.** `bc5_big_collection.py` lê
   `C:\bc\COORTE-BIG-COLLECTION.json`, fora do Git (o da 1.ª onda tem data de 24/09 00:30). A cópia
   para lá tem de ser feita e provada com sha256 igual ao commit, senão a 2.ª onda corre a coorte velha.
6. Validade dos canários: o mais velho tem 2,44 dias às 05:13Z. Com a regra de ≤ 7 dias, a coorte
   perde canários a partir de **~29/09 à noite**, se ninguém os refizer.

## 4. Riscos

- **R1 · A mesma coorte rende o mesmo que a 1.ª onda.** 14 das 18 trouxeram 0 documentos de matéria na 1.ª onda.
  O MAX_TARGETS é 1 em 12 delas, e esse primeiro link já está no livro. A REND mediu que só IT-T10-018
  (2) e IT-T7-141 (1) trariam matéria nova numa corrida: **~3 SIM em 18 = 16,7 %, que não passa do
  limiar da D35 (> 16,7 %)**. Sem as fontes da R1, ou sem rever o MAX_TARGETS, a micro reprova.
- **R2 · Os NÃO e NAO_SEI da 1.ª onda** (Livro de Decisões):
  - IT-T7-021 e IT-T7-042 (×2): NAO_SEI, porque só aparece uma palavra de T7 («consorzio»), o que é
    indício e não sinal;
  - IT-T7-042 e IT-T7-135: NÃO por **capa ≠ matéria** (o detector diz página de entrada);
  - IT-T7-117 (caf-cia.it): NÃO, porque fala de outro universo (T5, universidade).
- **R3 · A régua T2 já está instalada** (`regua-t2-v1` é antepassado de `5ba9647e`). A tabela da REND
  (24/09) diz «T2 sem régua, nunca SIM», e isso ficou velho. IT-T2-034 (ARPA Marche) e IT-T2-051
  (ARPAE) são boletins agrometeorológicos, o coração da D29. Na próxima corrida podem dar SIM se
  houver boletim novo (MAX_TARGETS = 1). **NÃO SEI** quanto rendem: não medi.
- **R4 · Domínio repetido.** O cia.it aparece em **5 fontes** (IT-T7-112, 118, 121, 123 e 135), e o
  caf-cia.it e o ciatoscana.eu são da mesma casa. Na 1.ª onda o cia.it levou **16 pedidos** na onda,
  em 5 corridas com ≤ 4 cada. O teto de 5 é por corrida. Se a D7 («até 5 pedidos por SITE») valer
  pela **onda inteira**, a onda viola-a sem disjuntor nenhum disparar. **Pergunta para o dono ou a
  coordenação.**
- **R5 · Acesso parcial.** Nenhuma das 18 está marcada ACESSO_PARCIAL. As 4 ACESSO_PARCIAL da R1
  (assinantes) estão em CANARY_FAILED e, quando entrarem, entram com essa marca.
- **R6 · Relevância.** A 3b marca como FICA_FORA 6 das 18: IT-T10-022, IT-T2-034, IT-T2-051, IT-T7-017, IT-T7-033, IT-T7-042. Pela D2/D8 isto não barra a fonte, porque a Admissão decide
  item a item. É ruído esperado na Sala.
- **R7 · Zootecnia.** IT-T10-022 (zootecnicainternational.com) é produção animal. Não é saúde animal
  (D26), mas é fronteira: fica para quem decidir.

## O que eu NÃO fiz
Não congelei, não corri nada com rede e não mexi no vivo. Não medi o rendimento da régua T2 nas duas ARPA.
