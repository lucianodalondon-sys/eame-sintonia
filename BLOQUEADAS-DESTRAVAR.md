# BLOQUEADAS-DESTRAVAR · 26/09 (03:30–05:00 local) · sem rede, só leitura do vivo

Vivo `source-curator-service-v1` @ `83de0ccd`: nada escrito, nada parado; Sala não tocada; 0 pedidos de rede.
Ramo **`destravar-v1`** (a partir de `83de0ccd`), não instalado.

## 1 · «Importar os 2 contratos em falta» — não há o que importar (corrijo o meu relatório anterior)

Ensaio numa **cópia fiel do vivo** (`C:/Users/London1/dv-copia`: `83de0ccd` + os 16 livros sujos do vivo copiados e
conferidos por sha256, 16/16 iguais), rede fechada. `curadoria/importar_do_coletor.py` sem `--aplicar`:
- a ferramenta só importa **READY_LEGACY** com linha na tabela do coletor (`regras/italy_contracts_onboarded.json`,
  226 linhas); **IT-T10-034 e IT-T5-041 não estão lá e JÁ TÊM contrato no Curator**;
- as 2 tarefas «sem contrato nesta árvore» (T01476 e T02077) são **restos de 23/09**: nesse instante o worker não via
  o contrato (`worker.py:758`). **Depois correram tarefas novas das mesmas fontes** (VALIDATE_ROUTE OK, CANARY) —
  e o que as parou hoje é outra coisa, já escrito no ledger:
  - **IT-T10-034** granariamilano.it: `REPARO_RECUSADO: DUPLICADA` de **IT-T10-026** (a mesma casa);
  - **IT-T5-041** crpv.it: `REVISAO_R1: TEXTO_NAO_E_MATERIA` — **crpv.it reencaminha para a Ri.Nova** (outra organização);
  - IT-PROVA-R: fonte de teste.
- **Fontes ganhas: 0.** As tarefas BLOCKED antigas são inertes (BLOCKED não acorda o robô).
**Plano para o coordenador:** nada a instalar. Se quiser a fila limpa, marcar T01476/T02077 como substituídas pelas
tarefas seguintes (mesmas fontes). IT-T5-041: decidir se a Ri.Nova (rinova.eu) é **candidata nova** pela porta
(`fonte_nova.registar`, com prova) — não se muda a identidade de uma fonte por reencaminhamento.

## 2 · Coldiretti ×5 + Unaprol + ANGA + CNR — o que os recibos mostram, e o teste de 1 pedido

**Recibos** (`curadoria/LIFECYCLE-EVIDENCE-V1.json` do vivo, por hora UTC):

| fonte | host | robots | canário |
|---|---|---|---|
| IT-T7-050 | www.coldiretti.it | 404 (não publica) às 17:25 e 00:26; «inacessível» noutras horas | **200 OK** 22/09 17:30 e 23/09 00:26 → **10054** às 17:49, 17:50, 17:55, 18:11, 19:11, 01:27, 24/09 01:28 |
| IT-T7-051/052/053 | puglia/sicilia/veneto.coldiretti.it | 404 | o **mesmo desenho**: OK às 17:30 e 00:26, 10054 minutos depois, **nos 4 hosts na mesma janela** (17:49–17:58) |
| IT-T7-058 | www.unaprol.it | lido (`Disallow:` vazio = tudo permitido) | OK 17:31 e 00:27 → 10054 |
| IT-T7-045 | www.anga.it | 404 | só 10054, e 1× **TLS** (`SSLV3_ALERT_HANDSHAKE_FAILURE`, 23/09 00:24) |
| IT-T5-006 | www.cnr.it | «inacessível após 2 tentativas» 25/09 22:27 → 26/09 06:22 (6×) | — |

Leitura: **não é a fonte nem o nosso leitor.** O 1.º pedido de uma rajada passa; os seguintes, minutos depois, levam
«ligação cortada» — em todos os hosts da Coldiretti ao mesmo tempo. É a cara de um **limite por organização contra a
nossa saída** (já visto a 22/09: 403 → 000 na saída Proton de Milão). O CNR foi colhido pelo coletor no mesmo dia
(`runs.ndjson`: 36 corridas com cnr.it entre 11:19 e 22:58Z, quase todas HEALTHY, host ibba.cnr.it) e o robots de
www.cnr.it falhou a partir das 22:27Z, no meio de várias corridas por minuto — **consistente com o mesmo tipo de
limite, não provado**. Hipótese, não facto.

**O teste** — `curadoria/sonda_um_pedido.py` (commit `8bbc7ab4`): **1 pedido por fonte**, ao `robots.txt` do host da
entrada do contrato, pelo leitor da casa (`canario.buscar`); **no máximo 1 por organização por ronda** (os subdomínios
`coldiretti.it` são uma), pausa entre rondas (20 min por omissão); **portão IT por consenso antes de cada ronda** e no
fim — sem PASS não pede nada. Não lê página, não guarda bytes, não escreve em livro; não é rota nova. Resultado por
fonte: OK · RECUSA_HTTP · FECHO_DE_LIGACAO · TLS · SEM_RESPOSTA. Testes: `test_sonda_um_pedido` 5/5; mutação 2/2
(sem portão; sem limite por organização). Plano para as 7 fontes (lido sem rede): **7 pedidos em 4 rondas**
(ronda 1: CNR, ANGA, Coldiretti nacional, Unaprol; rondas 2–4: Puglia, Sicília, Vêneto), ~1 h.

**Comando** (coordenador, VPN IT ligada, numa cópia do vivo com rede autorizada):
```
py curadoria/sonda_um_pedido.py --fontes=IT-T5-006,IT-T7-045,IT-T7-050,IT-T7-051,IT-T7-052,IT-T7-053,IT-T7-058 --saida=SONDA-UM-PEDIDO.json
```
Depois: as que derem **OK** → re-enfileirar a tarefa pelo caminho canónico, **uma organização por corrida** (a
tarefa do robô faz robots + entrada + item: 3 pedidos seguidos, que é exatamente o que o limite corta); as que
derem FECHO/TLS de novo → a saída IT é recusada: pedir outra saída IT ao dono, não mexer no código.

## 3 · MICRO-PROVA dos 89 que esperam território (80 PRECISA_DECISAO + 9 classes mistas)

Plano sem rede em `curadoria/MICRO-PROVA-PLANO-V1.json` (gerado por `curadoria/micro_prova_plano.py`):

| | |
|---|---|
| candidatas | **89** (48 «prova insuficiente» da revisão anterior, 40 nunca revistas, 1 janela de robots) |
| domínios | **83** (5 com mais de uma: normattiva.it ×3, masaf.gov.it, agriligurianet.it, pagepressjournals.org, tesaf.unipd.it ×2) |
| pedidos previstos | **356** = 89 × (1 robots + 3 páginas) |
| por domínio por ronda | **≤ 4** (teto D38 = 5; 1 de margem para um redireccionamento) |
| rondas | 3 (ronda 1: 83 candidatas; 2: 5; 3: 1) — recomendo **lotes de 10–20 candidatas** por corrida |
| janela | CAND-0009 Rete Rurale Nazionale: robots `Visit-time` 01:00–03:00 UTC |
| país na ficha | IT 78 · NÃO SEI 9 · EU 1 · OUTRO 1 (se a prova der fora de IT, cai na decisão do dono sobre EU/INT) |

**O que conta como prova** (canal `DECISOES-SEMANTICAS-V1` / `decisao_semantica.py`, nada novo): URL da candidata,
**≥1 página INSTITUCIONAL/LEI + ≥2 páginas de CONTEÚDO com URLs distintos e sha256**, `DECIDIDO_POR`, `PAIS` vindo da
prova. Uma página só **não** decide (medido a 23/09: 1 item fabrica território — ≥4 de 6 na gaveta errada). O nome
manda mais que o tema («uma empresa que fala de clima não é um serviço climático»). Por gaveta:

| gaveta | página INSTITUCIONAL mostra | 2 CONTEÚDOS mostram |
|---|---|---|
| T1 CROP & PRODUCTION | produtor, OP, consórcio de produção/tutela | campanha, produção, colheita, qualidade |
| T2 CLIMATE / WATER / SOIL | serviço meteo/agrometeo, ARPA, bonifica | boletins meteo/agrometeo, água, solo — datados |
| T3 PEST / DISEASE / WEEDS | serviço fitossanitário, consórcio de defesa | boletins/avisos fitossanitários datados |
| T4 REGULATORY | quem emite ou compila norma | decretos, circulares, registos |
| T5 SCIENCE | universidade, departamento, instituto | publicações, projetos, resultados |
| T6 RESEARCHERS | página oficial da PESSOA na instituição (D21/D24) | produção da pessoa |
| T7 TECHNICAL NETWORK | associação, cooperativa, ordem, federação | notícias técnicas, circulares, eventos técnicos |
| T8 FARMERS & INFLUENCERS / MEDIA | redação/testata | artigos agrícolas da redação |
| T9 COMPETITORS | empresa (P.IVA, catálogo) | comunicados da empresa |
| T10 MARKET / TRADE / INDUSTRY | bolsa, câmara de comércio, observatório | cotações/análises datadas |
| T11 FAIRS / EVENTS | organizador da feira | programa, expositores, edição |
| T12 PUBLIC ADMINISTRATION | ente público | atos, avisos, notícias agrícolas |

Coletar as provas pela saída IT (portão antes de cada ronda), bytes fora do Git com sha256, e a decisão entra por
`DECISOES-SEMANTICAS-V1.json` (Opus/humano) — o QUALIFY só o consulta quando o nome dá NÃO SEI.

## 4 · Os 22 canais YouTube → CANAIS-41-RUNBOOK

Ficheiro **`auditoria-madrugada/CANAIS-YOUTUBE-22-PARA-CANAIS-41.json`** (sha256 `54dfc490…42aa2e`; cópia no ramo),
dirigido à bancada **CANAIS-41-RUNBOOK (term_5fb7d544)**. Atenção: **não são dos 41** — são CANDIDATAS (sem SOURCE_ID),
paradas no QUALIFY por capacidade YouTube. Cada linha traz CAND, nome, URL, CHANNEL_ID/handle, o site onde foi visto,
os SOURCE_ID e classes desse site e a herança D21 já medida: **8 com CHANNEL_ID**, **12 vistos num site de uma só
classe**, **4 com D21 já medido** (p.ex. CREA → T5, Regione Sicilia → T12). Precisam do QUALIFY (D21: herdar a classe
do site só com ligação oficial canal↔site escrita na ficha) **antes** do teste de qualificação dos 41.

## Código (ramo `destravar-v1`)

- `8bbc7ab4` — `curadoria/sonda_um_pedido.py` + `test_sonda_um_pedido.py` (5/5; mutação 2/2).
- commit seguinte — `curadoria/micro_prova_plano.py` + `MICRO-PROVA-PLANO-V1.json`, a lista dos 22 canais, este
  relatório e a peça `C-BLOQUEADAS-DESTRAVAR` no mapa. Mapa: fica para a INTEGRA (PRONTO-SEM-MAPA).
Nada disto corre no robô: são ferramentas que o coordenador corre com VPN, e planos.

## EM PALAVRAS SIMPLES

- **Os «2 contratos em falta» não faltavam.** Eu tinha lido mal: eram duas tarefas velhas. Uma das fontes é cópia de
  outra que já temos; a outra agora aponta para outra organização. Não há o que importar — corrigi o que disse ontem.
- **Coldiretti:** o site deixa entrar o primeiro pedido e corta os seguintes, minutos depois, em todos os seus sites ao
  mesmo tempo. Não é defeito nosso nem do site «morto»: é um porteiro que não gosta de muitas visitas seguidas da nossa
  VPN. Escrevi um teste que bate **uma vez só** em cada site, uma organização de cada vez, com pausa. O coordenador corre
  com a VPN italiana; se abrir, as fontes voltam para a fila devagar; se não abrir, é preciso outra VPN.
- **As 89 fontes sem «gaveta»:** o plano diz, fonte a fonte, que 3 páginas ler (quem ela é + 2 coisas que publica),
  quantos pedidos (356 no total, nunca mais de 4 por site de cada vez) e o que conta como prova em cada gaveta.
- **Os 22 canais do YouTube:** mandei a lista à equipe dos canais, avisando que ainda precisam de «nome de família»
  (a gaveta) antes de entrar no teste deles.
