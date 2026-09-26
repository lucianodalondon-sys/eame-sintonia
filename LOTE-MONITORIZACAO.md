# LOTE-MONITORIZACAO · onde as redes públicas publicam o SINAL PRECOCE de praga

Ramo **`micro-prova-lote2b-v1`**, desce do vivo `69b0e23f`. Feito a 26/09 (depois do passo 8 do lote 2B), **sem rede**.
Alinhamento do dono (secções 2–3): capturas em armadilha por semana, ovos/larvas/adultos, voo, limiar, % de infestação —
**antes** do boletim.

## 1 · O que os nossos livros sabem (medido, sem rede)

- **Acervo:** só **IT-T3-005 Terre dell'Etruria** traz contagem — «infestazione attiva prossima al 5 %», «2-3%», «0%» e
  a recomendação larvicida (newsletter pública); as séries por ponto estão atrás de login. As outras 4 «ocorrências» no
  acervo eram falsas («catturare la luce» de um espumante, calor «intrappolato» numa geada).
- **Endereços** (porta, contratos, Atlas, descoberta, GAPS, P1g, observações do coletor): 15 hosts com palavra de
  monitorização, quase todos «monitoraggio» **ambiental** (ARPA, PNRR). Nenhum endereço nosso diz «catture».
- **Conclusão honesta:** nenhum livro nosso diz **onde está a tabela de capturas**, em que formato, com que frequência.
  Isso só se sabe olhando. Por isso o lote vem com uma **sonda** (`curadoria/medir_contagens.py`) e os campos
  `TABELA_EM / FORMATO / FREQUENCIA` ficam **NAO SEI** até a medida.
- **19 dos 20 já são fontes (SOURCE_ID)**, quase todas paradas no canário. O que a sonda achar vira **entrada nova /
  contrato de monitorização** dessas fontes — não número novo.

## 2 · A sonda (`curadoria/medir_contagens.py`) — sem registar nada, sem RAW, sem Sala

Por alvo, **≤ 5 pedidos** (teto D38): robots.txt (cumprido) · a entrada · até 3 páginas escolhidas pelos links com cara
de monitorização (âncora ou endereço: catture, trappole, monitoraggio, voli, ovideposizione, infestazione, soglia +
pragas: cimice asiatica, Popillia, mosca dell'olivo, tignoletta, Drosophila suzukii, carpocapsa, flavescenza…). Portão IT
antes de cada alvo; bytes fora do Git com sha256. Links para **CSV/XLS/PDF** com nome de monitorização: diz **onde**
estão (não os abre). Por página: tabelas numéricas de monitorização, contagens («34 catture», «adulti: 12»), % de
infestação (nos dois sentidos da frase), limiar, pragas, culturas, datas; **frequência** = mediana dos intervalos entre
datas. Veredito: `CONTAGEM_PUBLICA` (número + data, sem login) · `TABELA_EM_FICHEIRO` · `SO_BOLETIM` · `LOGIN` · `NAO_SEI`.
O formulário de login no menu de todas as páginas **não** fecha a página (só conta como login quando pede senha e quase
não tem texto — medido na Terre dell'Etruria).
Testes **14/14**; mutação **9/10** (a que sobrevive é o teto conferido em dois sítios — o laço já pára antes).
Verificação nos bytes reais do acervo: a newsletter da Terre dell'Etruria dá `PCT_INFESTACAO` = «5 %», «2-3%», «0%» e
`LOGIN` = falso.

## 3 · Os 20 alvos (`curadoria/LOTE-MONITORIZACAO.json`) — um por domínio, colisão 0

Fora pela **4.ª onda (rodada 1)**: `regione.veneto.it` (SFR Veneto), `regione.sicilia.it`, ARPAE/ARPAV/ARPAL/ARPAT/
ARPA Marche/ARPA Campania. Fora por **robots** (P1g): Lombardia SFR, Puglia SIT e emergenzaxylella, SIAS, Beratungsring.
**Colisão** medida contra o vivo (`--vivo`): rodada 1 = 38 domínios, colhidos em 24 h = 33 domínios, **0 em comum**.
⚠️ **Cortesia:** `fmach.it` (LM-03), `agriligurianet.it` (LM-04) e `sardegnaagricoltura.it` (LM-14) receberam 5, 5 e 2
pedidos da micro-prova do lote 1 hoje de manhã — a ferramenta de colisão não vê a micro-prova; usar `--sem=LM-03,LM-04,LM-14`
se preferires deixá-los para amanhã.

| ID | Fonte | Região | O que se procura | No robô hoje | Formato (P1g) |
|---|---|---|---|---|---|
| LM-01 | IT-T3-027 | Friuli Venezia Giulia | bollettini di difesa integrata: tabelas de catture por zona (tignoletta, carpocapsa, cimic | CONTRACTED_CANARY_FAILED | PDF |
| LM-02 | IT-T3-028 | Emilia-Romagna | bollettini territoriali di produzione integrata por provincia (catture, voli) | CONTRACTED_CANARY_FAILED | HTML |
| LM-03 | IT-T3-030 | Trentino (FEM) | flavescenza dorata / scafoideo: monitoraggio e bollettini di difesa | CONTRACTED_CANARY_FAILED | NÃO SEI |
| LM-04 | IT-T3-031 | Liguria | sorveglianza del territorio: carte di diffusione e monitoraggio organismi nocivi | CONTRACTED_CANARY_FAILED | HTML |
| LM-05 | IT-T3-026 | Campania | SIMFITO: sistema informativo de monitoraggio fitosanitario | CONTRACTED_CANARY_FAILED | HTML |
| LM-06 | IT-T3-033 | Piemonte | bacheca dei bollettini fitosanitari (monitoraggi) | CONTRACTED_CANARY_FAILED | HTML |
| LM-07 | IT-T3-041 | Lazio | servizio fitosanitario regionale (reti di monitoraggio) | CONTRACTED_CANARY_FAILED | HTML |
| LM-08 | IT-T3-043 | Marche | AMAP servizio fitosanitario (rete di monitoraggio tignoletta/mosca olearia) | CONTRACTED_CANARY_FAILED | HTML |
| LM-09 | IT-T3-049 | Toscana | servizio fitosanitario regionale (monitoraggi organismi nocivi) | CONTRACTED_CANARY_FAILED | HTML |
| LM-10 | IT-T3-053 | Umbria | bollettini fitosanitari (catture/voli nos boletins) | READY_FOR_COLLECTION | NÃO SEI |
| LM-11 | IT-T3-055 | Valle d'Aosta | avvisi fitosanitari frutticoltura (voli carpocapsa) | CONTRACTED_CANARY_FAILED | HTML |
| LM-12 | IT-T3-037 | Basilicata | ufficio fitosanitario (monitoraggi) | CONTRACTED_CANARY_FAILED | HTML |
| LM-13 | IT-T3-032 | Molise | bollettini e comunicati fitosanitari | CONTRACTED_CANARY_FAILED | HTML |
| LM-14 | IT-T3-048 | Sardegna | servizio fitosanitario regionale (monitoraggi) | CONTRACTED_CANARY_FAILED | NÃO SEI |
| LM-15 | IT-T3-038 | Alto Adige | Pflanzenschutzdienst / servizio fitosanitario Bolzano (Popillia, cimice) | CONTRACTED_CANARY_FAILED | NÃO SEI |
| LM-16 | IT-T3-036 | Abruzzo | servizio fitosanitario (monitoraggi) | RETRY_AFTER | HTML |
| LM-17 | — (página nova) | Calabria | ARSAC prevenzione fitosanitaria: a pagina «consigli di difesa del nocciolo — monitoraggio  | sem SOURCE_ID | NÃO SEI |
| LM-18 | IT-T2-141 | Sardegna | ARPAS bollettino fenologico (fase por cultura) | CONTRACTED_CANARY_FAILED | TABELA_HTML |
| LM-19 | IT-T2-151 | Puglia | Agrometeo Puglia bollettini (avisos por cultura, modelos) | CONTRACTED_CANARY_FAILED | HTML |
| LM-20 | IT-T2-159 | Lazio | SIARL/ARSIAL agrometeorologia (modelos de infecao, boletins por cultura) | CONTRACTED_CANARY_FAILED | HTML |

## 4 · O COMANDO (coordenador, VPN IT; o robô pode continuar ligado — nada disto escreve livro)

```bash
V=C:/Users/London1/orca/workspaces/eame-sintonia/source-curator-service-v1 ; M=C:/g/mprova
S=C:/Users/London1/sintonia-sala-italia/monitorizacao/lm-$(date +%H%M) ; mkdir -p $S
git -C $M fetch origin micro-prova-lote2b-v1 && git -C $M rev-parse FETCH_HEAD     # = o SHA do relatório
git -C $M checkout --detach FETCH_HEAD ; cd $M
py superficie/rede.py --portao-de-egresso IT | tee $S/PORTAO-ANTES.txt             # PASS, senão PARAR
py curadoria/micro_prova_colisao.py --rodadas=C:/Users/London1/auditoria-madrugada/C2-ONDA4/rodadas.txt \
   --lote=curadoria/LOTE-MONITORIZACAO.json --vivo=$V                               # código 0
py curadoria/medir_contagens.py --lote=curadoria/LOTE-MONITORIZACAO.json --bytes=$S/paginas \
   --saida=$S/CONTAGENS-LM.json [--sem=LM-03,LM-04,LM-14] | tee $S/stdout.txt
py superficie/rede.py --portao-de-egresso IT | tee $S/PORTAO-DEPOIS.txt
```
≤ 5 pedidos × 20 domínios = **≤ 100 pedidos**, pausa 3 s → ~10 min. **Depois (sem rede):** eu leio os bytes das páginas
com `CONTAGEM_PUBLICA` / `TABELA_EM_FICHEIRO`, confirmo à mão o que é contagem de verdade (a sonda só aponta), e
escrevo por fonte: onde está a tabela, formato, frequência, cultura/praga, região — e o contrato de monitorização a
propor (entrada nova da fonte que já existe).

## EM PALAVRAS SIMPLES

- **O que o dono quer:** o primeiro sinal da praga — quantos insetos caíram nas armadilhas esta semana — antes de o
  boletim mandar tratar.
- **O que temos hoje:** só um site (Terre dell'Etruria) com números de infestação. Nos nossos cadernos não há o
  endereço de nenhuma tabela de capturas; isso só se descobre olhando os sites.
- **O que preparei:** uma lista de 20 serviços públicos (serviços fitossanitários regionais, a FEM, ARSAC, boletins
  agrometeorológicos) e um programa que, em cada site, segue só os links que falam de armadilhas, capturas e pragas, e
  diz se achou tabela com números, em que formato e de quanto em quanto tempo. No máximo 5 visitas por site.
- **Nada colide** com a 4.ª onda nem com o que o robô visitou nas últimas 24 horas. Três sites foram visitados hoje de
  manhã pela outra prova — dá para deixá-los para amanhã.
