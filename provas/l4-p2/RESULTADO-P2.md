# L4-P2-USOS-SEM-DATA — os consumidores em dois modos, sobre o corte da R9

    MISSAO            L4-P2-USOS-SEM-DATA (D144 do dono real, 28/09/2026 21:27)
    ESPECIE           SO LEITURA / MEDICAO
    RAMO              claude/l4-p2-medir-v1
    SOURCE_HEAD       fd8c94698adc6ffb5f6cf810ced178ed4c732e97
    RUNNER            provas/l4-p2/runner.py
    NUMEROS           provas/l4-p2/RESULTADO-P2.json
    HOJE DECLARADO    2026-09-28
    RULESET           G0/v4

    G0 INTOCADO       SIM. O runner carimba o sha256 de corrida_da_inteligencia.py,
                      motor_das_capacidades.py, capacidade_cientifica.py, cap_win.py e
                      pote_intelligence_casco.py ANTES e DEPOIS de cada modo: iguais nos
                      tres modos (`G0_INTOCADO.IGUAIS = true`). O patch do DEPOIS_P2 vive
                      em memoria. Nada foi escrito em motor/, leis/ ou pacote/.

---

## 1 · Os pontos do pedido, confirmados por leitura no HEAD

18 pontos conferidos, **18/18 confirmam** (`ITEM_1_PONTOS_CONFIRMADOS_NO_HEAD`; cada um
guarda a linha lida, e diz em que linhas o trecho aparece).

### O G0/v4 NAO descarta

| Onde | O que diz |
|---|---|
| `motor/corrida_da_inteligencia.py:155-157` | «O QUE A FALTA DE TEMPO BLOQUEIA — e so isto» |
| `motor/corrida_da_inteligencia.py:158-165` | `USOS_QUE_EXIGEM_TEMPO` = SINAL_TEMPORAL, CROSSING_COM_CHAVE_TIME, ACT_NOW, CAP-WIN, CAP-FUT, CAP-OPP |
| `motor/corrida_da_inteligencia.py:169-173` | `USOS_SEM_TEMPO` = EVIDENCIA_NAVEGAVEL, CROSSING_SEM_CHAVE_TIME, LEITURA_ATEMPORAL_DE_CAPACIDADE |
| `motor/corrida_da_inteligencia.py:177-208` | `estado_temporal` declara `USOS_DISPONIVEIS` / `USOS_BLOQUEADOS` por item |
| `motor/corrida_da_inteligencia.py:206-207` | os usos SEM tempo ficam disponiveis mesmo sem `FACT_TIME`; os COM tempo so se `ANCORADO` |

Medido neste corte: **269 de 269 itens** tem `EVIDENCIA_NAVEGAVEL`,
`CROSSING_SEM_CHAVE_TIME` e `LEITURA_ATEMPORAL_DE_CAPACIDADE` disponiveis
(`INTAKE.COM_USO_SEM_TEMPO = 269`); **248** deles tem SO esses (21 ancorados no tempo).
Na R9 eram 254 de 275 — a diferenca e so o corte (ver §2).

### Quem descarta sao os consumidores

| Onde | O que diz |
|---|---|
| `motor/motor_das_capacidades.py:521-526` (`_admite`) | «so G0 = PASSOU prova» — e a excecao unica e o facto sobre o futuro |
| `motor/motor_das_capacidades.py:606` | `if not _admite(linha, SINAL):` -> o estudo que nao passou G0 sai |
| `pacote/pote_intelligence_casco.py:193-195` | `ADMITIDA = ("G0_PASSOU", "FUTURO_POR_DESENHO", "USO_SEM_TEMPO", "PONTE_V1")` |
| `pacote/pote_intelligence_casco.py:320-340` (`_admite_para`) | se `uso_exige_tempo` e falso, admite `BLOQUEADO_EM_G0` com `so_tempo(G0_FALTA)` |
| `PARA-O-CASCO-R9/montar_r9.py:230` | `for s in LIVRO["SIGNALS"]` — so os sinais, isto e, so `G0 = PASSOU` |

A contradicao do pedido esta confirmada: **o gerador do pote ja aceita o uso sem tempo; o
motor das capacidades nao.**

### Uma correcao ao pedido

O pedido nomeia `motor/corrida_da_inteligencia.py l.155-207, l.169-172` — certo. Mas
`capacidade_cientifica.py:757` **ja respeita a lei**: a CAP-SCI so julga o item com
`LEITURA_ATEMPORAL_DE_CAPACIDADE` disponivel, e nao exige `G0 = PASSOU`. Ou seja: dentro
da CAP-SCI o P2 **ja esta feito**. O que mata o estudo e um passo depois — o `_admite` na
hora de o pos na saida (l.606).

---

## 2 · O corte: 275 linhas, 269 itens, e uma recusa medida

    FICHEIRO   EXPD78-R9-20260928T155047Z/copia/SALA_ATUAL.json
    SHA256     00cb7cb0eb689402c38f0fe2859ed75071162523e7a3eb2fd7b7e366108e73d2
               (= CORTE.SALA_ATUAL_SHA256 do livro e do pote da R9)
    LINHAS     275
    ITEM_ID    269 distintos

**O motor das capacidades RECUSA as 275 linhas.** Medido, nao contornado
(`PROVA_DAS_275_LINHAS`): `LeiViolada: ITEM_ID repetido no corte: nao serve de endereco da
prova` (`motor_das_capacidades.py:769-770`). Seis documentos entram duas vezes —
`derived:6`, `derived:56`, `derived:57`, `derived:60`, `derived:62`, `derived:66`.

A R9 nao bateu nisto porque o script dela chama `corrida_da_inteligencia.correr`
directamente, e a corrida aceita o ITEM_ID repetido (marca-o como duplicata, D12). Quem
recusa e o motor.

Nada foi renomeado. A comparacao ANTES x DEPOIS_P2 corre sobre as **MESMAS 269 linhas nos
dois modos** (a 2.a linha de cada repetido fica fora, e esta listada no JSON), o que a
mantem uma comparacao A/B valida. O que ela **nao** e: uma reproducao do total da R9.

    INTAKE (269)      ANCORADO 21 · FUTURO_EM_RELACAO_A_CAPTURA 9 · UNKNOWN_WINDOW 239
    R9 (275)          ANCORADO 21 · FUTURO 11 · UNKNOWN_WINDOW 243

O `INTELLIGENCE_RUN_ID` desta medicao (`IR-117885247a6f3266e164`) **nao pode** ser o da R9
(`IR-56c79b0c78fc3fa1e747`): o RUN_ID leva o `CODE_VERSION` do motor e o universo
(`identidade_da_corrida`), e aqui o codigo e o do HEAD e o universo tem 269 linhas. O
CORTE (o sha256 da copia) e o mesmo.

---

## 3 · O que o DEPOIS_P2 muda no codigo (em memoria, uma linha de regra)

    ANTES        `_admite(linha, SINAL)` -> `linha["G0"] == "PASSOU"`
    DEPOIS_P2    o mesmo, MAIS: se o uso corrente e `LEITURA_ATEMPORAL_DE_CAPACIDADE`,
                 tambem admite `G0 == BLOQUEADO_EM_G0` quando `so_tempo(G0_FALTA)`
                 — a funcao `so_tempo` do PROPRIO gerador do pote, nao uma copia.

Falta de `SOURCE_ID` ou de `RAW_OBSERVATION_ID` continua a bloquear tudo: sem
proveniencia nao ha uso nenhum. `CAP-WIN`, `ACT_NOW`, `CAP-FUT`, `CAP-OPP` e
`SINAL_TEMPORAL` continuam a exigir `G0 = PASSOU`.

### O patch dispara? SIM — provado antes de se ler o zero

| | itens admitidos |
|---|---|
| regra ORIGINAL (`G0 = PASSOU`) | 21 de 269 |
| regra do P2, no uso atemporal | 269 de 269 |
| **abertos pelo P2** | **248** |

Isto importa: sem esta prova, um `P2_RECUPERA = 0` podia ser o patch a nao existir, em vez
de uma medicao.

---

## 4 · A tabela: ANTES x DEPOIS_P2 (n itens)

### Por compartimento do pote

| Compartimento | Uso do G0 | ANTES objetos | ANTES itens na prova | DEPOIS_P2 objetos | DEPOIS_P2 itens | Diferenca |
|---|---|---|---|---|---|---|
| `windows` (Finestre Colturali, CAP-WIN) | CAP-WIN (**exige tempo**) | 0 | 0 | 0 | 0 | **0** |
| `science` (Intelligence Scientifica, CAP-SCI) | LEITURA_ATEMPORAL (sem tempo) | 0 | 0 | 0 | 0 | **0** |
| `future` (Radar Futuro, CAP-FUT) | CAP-FUT (**exige tempo**) | 9 | 9 | 9 | 9 | **0** |
| `sources` (Registro delle fonti) | EVIDENCIA_NAVEGAVEL | 6 | 12 | 6 | 12 | **0** |

### Por capacidade / dentro das capacidades

| | ANTES | DEPOIS_P2 |
|---|---|---|
| SINAIS no livro da corrida (`G0 = PASSOU`) | 21 | 21 |
| CAP-WIN: janelas (`CROP_WINDOWS`) | 0 | 0 |
| CAP-WIN: `ACT_NOW` | 0 | 0 |
| CAP-WIN: `ANALYTIC_OUTPUT` | `NOT_POSSIBLE` | `NOT_POSSIBLE` |
| CAP-WIN: pedidos a Coleta | 269 | 269 |
| CAP-SCI: itens recebidos | 269 | 269 |
| CAP-SCI: estudos JULGADOS | 0 | 0 |
| CAP-SCI: FORA | 269 | 269 |
| Objetos nao enviados ao pote | 73 (todos `sources/RENDIMENTO_SEM_PROVA`) | 73 |

### Os nomes que o pedido usou — o nome REAL no codigo

| Pedido | Nome real | Existe? |
|---|---|---|
| **CIENCIA** | compartimento `science` («Intelligence Scientifica»); capacidade `CAP-SCI` (`capacidade_cientifica.py:65`) | **SIM** · 0 objetos ANTES e DEPOIS |
| **ESTUDO** | a especie de objeto `ANALYTIC_JUDGMENT/ESTUDO` dentro de `science` (`motor_das_capacidades.py:642`); o julgamento vive em `CAP_SCI.ESTUDOS` | **SIM** · 0 julgados ANTES e DEPOIS |
| **CONHECIMENTO** | — | **NAO EXISTE.** Nenhuma capacidade, compartimento nem especie se chama assim. A palavra e do LAB (`CONTRAPROVA-TEMPORAL.md:145`, «CONHECIMENTO_SEM_FACT_TIME»). O equivalente em codigo e o **uso** `LEITURA_ATEMPORAL_DE_CAPACIDADE` (`corrida_da_inteligencia.py:172`) — um uso, nao um compartimento |
| **FICHA_TECNICA** | — | **NAO EXISTE neste motor.** O mais proximo e o compartimento `portfolio` («Portafoglio / Etichette», lido pela CAP-LABEL), e o motor das capacidades **nao o alimenta**: `CHAVES_DO_POTE` (`motor_das_capacidades.py:144-151`) so tem `windows`, `science`, `future`, `sources` |

### Por que a tabela e toda zeros — os dois portoes que estao ANTES do `_admite`

O P2 nao recupera nada neste corte, e **nao e porque o patch nao funcione** (§3: abre 248
itens). E porque nenhum item chega ao sitio onde o `_admite` decide.

**Portao 1 — a TRIAGEM, pelo envelope `FATO`** (`PORQUE_A_CIENCIA_E_ZERO`):

    FATO dos 269 itens       269/269 = o TEXTO "NAO_SE_APLICA" (nao e nem um objeto)
    e_estudo() = SIM         0 de 269
    ITEM_ID que JA E um DOI  99 de 269

`e_estudo` (`motor_das_capacidades.py:319-334`) le SO o envelope `FATO`, e so aceita DOI,
`TRIAL_ID` ou especie cientifica. Os 53 artigos cientificos do feed EU-T5-001 trazem o DOI
**no proprio ITEM_ID** (`https://doi.org/10.1002/arch.21655`), e o `FATO` deles diz
`NAO_SE_APLICA`. Logo: 0 estudos, e o `_admite` da l.606 nunca e chamado.

**Portao 2 — o LUGAR, D112(a)**: a CAP-WIN nao formou nenhuma janela porque
`JANELA_DECLARADA.REGIAO_DO_FATO` e `NAO SEI` em **todos** os itens do cruzamento. Dos 269
pedidos que a CAP-WIN emitiu, o motivo mais comum (149) e
`PROBLEMA fora do contrato PROBLEMA/v1 + REGIAO_DO_FATO: VALOR = NAO SEI`.

**Conclusao medida: o P2, sozinho, nao vale nada neste corte.** Ele conserta o portao
certo (§1 confirma a contradicao), mas ha dois portoes a montante dele — triagem pelo
`FATO` e lugar pela D112(a) — que apanham 100% dos itens primeiro.

---

## 5 · ACT_NOW_NAO_AUMENTOU_INCORRETAMENTE = **PASS**

15 clausulas conferidas (10 de SAIDA + 5 de REGRA), **0 falhas**.

| Clausula | ANTES | DEPOIS_P2 |
|---|---|---|
| SINAIS do livro (SINAL_TEMPORAL), por SIGNAL_ID | 21 | 21, os mesmos |
| itens com `G0 = PASSOU`, por ITEM_ID | 21 | 21, os mesmos |
| `ACT_NOW` — janelas da CAP-WIN | 0 | 0 |
| `ACT_NOW` — objetos no pote | 0 | 0 |
| `windows`: objetos · itens na prova · prova fora da regra original | 0 · 0 · 0 | 0 · 0 · 0 |
| `future`: objetos · itens na prova · prova fora da regra original | 9 · 9 · 0 | 9 · 9 · 0 |
| o patch abriu `SINAL_TEMPORAL` / `ACT_NOW` / `CAP-WIN` / `CAP-FUT` / `CAP-OPP`? | — | **nao, em nenhum dos 5** |

**Nota sobre `future`**: as 9 provas dali tem `G0 = BLOQUEADO_EM_G0` — e isso e **por
desenho**, nao regressao: `_admite(linha, FUTURO)` ja aceita o item que o G0 bloqueou SO
por a data ser depois da captura (`motor_das_capacidades.py:524-525`). Por isso a clausula
nao e «tem G0 = PASSOU», e sim «**a regra ORIGINAL admitiria esta prova**». A 1.a versao
deste teste usava a clausula errada e dava FAIL sobre o ANTES — corrigido.

**P2_CAUSA_REGRESSAO_ACT_NOW = NAO.**

---

## 6 · O mutante: o teste reprova? **SIM**

    MUTANTE   o mesmo patch, com `CAP-WIN` TAMBEM na lista de usos abertos — ou seja,
              a janela e o «agir agora» passam a aceitar item bloqueado so pelo tempo.
              Exactamente o que o P2 promete NAO fazer.

    RESULTADO DO TESTE               FAIL
    O TESTE REPROVA O MUTANTE        SIM
    CLAUSULA QUE O APANHOU           «o patch abriu o uso CAP-WIN, que EXIGE tempo»
                                     (clausula de REGRA)
    CLAUSULAS DE SAIDA QUE O APANHARAM   NENHUMA

### E aqui esta a ressalva, e ela e importante

**As clausulas de SAIDA, sozinhas, NAO apanhariam o mutante neste corte.** Medido:
`windows` = 0 objetos no ANTES **e** 0 no mutante; `ACT_NOW` = 0 nos dois. Duas razoes, as
duas medidas:

1. a CAP-WIN nao produz janela nenhuma neste corte por falta de `REGIAO_DO_FATO`
   sustentada (D112a) — nao ha objeto de janela para o mutante estragar;
2. a CAP-WIN tem uma **segunda tranca de tempo**: `cap_win.py:459` — sem
   `TEMPORAL_STATE = ANCORADO` o estado nao e `CURRENT`, e o W8 do `ACT_NOW`
   (`cap_win.py:717-730`) exige `CURRENT`. Mesmo com o `_admite` aberto, o `ACT_NOW` nao
   sobe.

Por isso o teste tem uma clausula de **REGRA**, que interroga o proprio patch linha a
linha do LINEAGE real, em vez de esperar que a saida denuncie. Foi ela que apanhou o
mutante. Um teste que so olhasse a saida teria dado PASS num patch errado — e este corte e
exactamente o corte onde isso aconteceria.

---

## 7 · Os itens que o DEPOIS_P2 recupera, e o cruzamento com o LAB

    P2_RECUPERA = 0   (0 itens, 0 objetos)

Lista vazia. O cruzamento por ITEM_ID, com os dois conjuntos do LAB:

| Conjunto do LAB | n | reconstruido | recuperados pelo P2 |
|---|---|---|---|
| os 100 A+B nao detetados (`AB-DETECCAO-V1.json`, `DETECTOU = NAO`) | 100 registos = **98 ITEM_ID** distintos | sim | **0** |
| os 69 «conhecimento sem FACT_TIME» (`CONTRAPROVA-TEMPORAL.md:145-147`) | **69** | sim, e o runner CONFERE: 53 artigos EU-T5-001/REGUA + 7 fichas + 9 da lista 2D = 69 (`OS_69_CONFERE = SIM`) | **0** |
| uniao dos dois | **98** (os 69 estao TODOS dentro dos 98) | — | **0** |

    SHA256 AB-DETECCAO-V1.json        e9ad50616f072ab047804caf3b73a6c7e2972e9b434b2d3900190fb58353f97e
    SHA256 CONTRAPROVA-TEMPORAL.md    aa1e862d10fda95b0e7f7ee7d4bb314093d17a24f743b7b4c260afdd969e7f43

### Onde morre cada um dos 98 — item a item no JSON, resumido aqui

    ITENS CRUZADOS                        98 (98 no corte, 0 fora dele)
    G0                                    98/98 = BLOQUEADO_EM_G0
    bloqueado SO pelo tempo               98/98 = SIM
    USOS_SEM_TEMPO disponiveis            98/98 (os tres)
    e_estudo() = SIM                      0/98
    REGIAO_DO_FATO sustentada (D112a)     0/98
    portao que segura                     98/98 = «TRIAGEM + LUGAR»
    O P2 muda este item?                  98/98 = NAO

Por fonte, os 98: EU-T5-001 = 53 · IT-T10-018 = 8 · CAND-1209 = 3 · IT-T9-011, CAND-1210,
CAND-1213, CAND-1236, IT-T12-018 = 2 cada · o resto 1 cada.

**Ou seja: todos os 98 estao exactamente na situacao que o P2 descreve — bloqueados SO
pelo tempo, com os tres usos sem tempo declarados disponiveis pelo G0/v4 — e nenhum deles
e recuperado, porque morre num portao anterior.**

---

## 8 · Medido e NAO aplicado

### `sources` / RENDIMENTO_DE_FONTE

    fontes no corte                                             79
    com objeto de rendimento (ANTES e DEPOIS_P2)                 6
    sem rendimento                                              73
    sem NENHUM item com G0 = PASSOU, mas com proveniencia COMPLETA   66

`_rendimentos` (`motor_das_capacidades.py:718`) **nao passa pelo `_admite`**: conta
`G0 == PASSOU` a mao. O patch do P2 nao lhe chega. E a lei do pote diz que aquele uso nao
exige tempo: `uso_exige_tempo` devolve falso para a especie `RENDIMENTO`. Logo estas **66
fontes tambem seriam recuperaveis** por um P2 mais largo.

Nao foi aplicado aqui de proposito: mudar `ITENS_QUE_PASSARAM_G0` mudava um **facto**
(quantos passaram) e nao um **uso**. Fica medido, e e decisao do dono.

---

## 9 · O que esta medicao NAO prova

- Nao prova que o P2 e inutil em geral. Prova que **neste corte** ele nao recupera nada,
  porque a triagem pelo `FATO` e o lugar da D112(a) apanham 100% dos itens primeiro.
  Num corte onde o `FATO` declare DOI/especie e a `REGIAO_DO_FATO` tenha base, o numero
  seria outro — e este runner corre igual sobre ele.
- Nao prova nada sobre as 6 linhas repetidas que ficaram fora (`derived:6`, `56`, `57`,
  `60`, `62`, `66`): o motor recusa-as, e nao se lhes inventou identidade.
- Nao mede `CROSSING_SEM_CHAVE_TIME` (o terceiro uso sem tempo): o motor das capacidades
  nao produz crossings, e `cruzamentos_max.py` nao entrou nesta medicao.
- Nao reproduz a R9: RUN_ID diferente (codigo do HEAD, universo de 269), e o pote nao foi
  gerado nem publicado.
- Nao diz se a P1 da contraprova (tempo por afirmacao, tipado) resolveria o resto. Nao foi
  medida.

---

## 10 · Em palavras simples

O portao G0 nao joga nada no lixo: ele marca cada item com o que ele ainda pode servir
sem data. Neste corte, 269 de 269 itens ficaram com essa marca. Quem joga fora e uma linha
de codigo mais adiante, que continua a exigir data para tudo — e a prova disso e que o
gerador do pote, no mesmo repositorio, ja aceita item sem data para uso que nao usa data.

Consertei essa linha em memoria, sem tocar no ficheiro, e corri os dois modos sobre o
mesmo material. O conserto funciona (abre 248 itens dos 269). Mas nao entrou nem um item
novo em nenhuma prateleira — **zero** — porque ha duas portas antes dela: uma pergunta se o
item e estudo e le isso num campo que nesses 269 itens diz literalmente «nao se aplica»
(mesmo nos 53 artigos cientificos, que trazem o DOI no proprio endereco); a outra exige a
regiao do fato com base, e nenhum item tem. O «agir agora» nao subiu nem um caso, e nao
podia: continuou fechado nas 15 conferencias, e o mutante que o abriu foi reprovado.
