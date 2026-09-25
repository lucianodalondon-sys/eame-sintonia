# ROBOTS-RFC (D34) · um leitor único de robots.txt, pela RFC 9309

Ramo `robots-rfc9309-v1`, sobre a produção `5ba9647e` (junta em 7df18f5d). **NÃO instalado.**

## 1 · O que foi feito

| peça | o que mudou |
|---|---|
| `coleta/robots_rfc9309.py` (novo) | o **leitor único**: grupo do nosso token (senão `*`); regra mais específica vence; empate → Allow; `*` e `$`; %-escape; `/robots.txt` sempre permitido; 4xx = sem robots (pode, §2.3.1.3); 5xx/rede = NÃO SEI → recusa (§2.3.1.4); HTML no lugar do robots = ilegível → recusa (regra da casa, mantida pela D34). Devolve a **regra que decidiu**. |
| `curadoria/gate_de_rota.py` | busca o ficheiro e pergunta ao dono; 5xx tenta 2 vezes; `decisao()` devolve a regra; a prova do `main()` passa a listar Allow **e** Disallow do nosso grupo |
| `curadoria/descobrir.py` | busca e pergunta ao dono |
| `coleta/scrap_http.py` | busca e pergunta ao dono; 401/403 passam de ILEGÍVEL a AUSENTE (norma); rede em baixo continua INDISPONÍVEL (levanta, não é recusa) |
| `curadoria/worker.py` | RETRY/BLOCK pelo **estado** do leitor (antes: procurava a palavra «inacessivel» no texto — um 5xx caía em BLOCK); guarda ROBOTS_SHA256, caracteres, REGRA e versão do leitor (antes: só os primeiros 120 caracteres) |
| `coleta/italy_pilot_collect.mjs` (gémeo Node) | qualquer 4xx = AUSENTE (antes só 404/410) — a leitura das regras já era pela norma |
| `provas/medir_validadores_coorte.py` | o 4.º leitor (instrumento EGR) também pergunta ao dono |
| testes | `tests/test_robots_rfc9309.py` (14): casos da RFC + SFR Lombardia, estados da resposta, paridade com o Node, «nenhum 2.º leitor», os 3 pontos decidem pelo dono; `provas/cortesia_http_local.mjs` ganhou C9b (robots 403 → passa); os 2 testes que registavam a dívida de 3 leitores foram actualizados (dívida paga) |

**Bateria antes/depois** (os 23 ficheiros de teste que tocam robots/portão/validação de rota, com a
saída de rede fechada; o `test_c10_8a_bluesky_ao_vivo` fica de fora por ir à rede de propósito):
produção `5ba9647e` 577 testes, 7 falhas · este ramo 591 testes, 6 falhas. **Nenhuma falha nova**; a
que sai é a lei «um só leitor de robots» (`test_so_um_ficheiro_le_o_robots`), que estava vermelha na
produção. As 6 que ficam já falhavam antes e são as mesmas nas duas árvores (test_38 POST,
test_8 rota da janela, «as três verdes», rt51/rt52/rt53 da autorização).

**Mutação:** 11 ataques ao leitor/pontos Python, 11 apanhados; 1 ataque ao gémeo Node (4xx volta a só 404/410), apanhado pelo C9b (30/31).

## 2 · A medição no livro inteiro

**Offline** (os robots que o robô guardou; `ROBOTS-LIVRO-INTEIRO.json`): o robô guardava o robots **cortado aos 120 caracteres** — 228 dos 391 lidos ficaram sem a regra que decidia. Por isso foi medido **com rede**.

**Com rede** (`ROBOTS-COM-REDE.json`): 300 sites, **1 pedido por site**, portão de consenso PASS IT no início e de 25 em 25; 703 fontes (livro do robô + tabela do coletor).

| | fontes |
|---|---:|
| proibida → **permitida** | **2** (robots responde 403 = sem robots pela norma: pianetapsr.it, tv.lombardianotizie.online) |
| permitida → **proibida** | **50** |
| · por HTML no lugar do robots (ilegível) | 37 |
| · por regra real que a leitura antiga não entendia | 13 (ARPAE `Disallow: /*?` ×12, ARPAL `Disallow: */albo/albo_pretorio.php` ×1) |
| das 50, **READY hoje** | **9** (6 ARPAE, simei.it, agraria.unirc.it, parmigianoreggiano.it) |
| proibições reais que continuam bloqueadas | 53 |
| iguais | 651 |

**As 9 READY que fecham:** corri o gémeo Node (o coletor, que já lia pela norma) sobre os mesmos robots guardados — **ele recusa as mesmas 9**. Eram READY que não se colhem: o robô de fontes dizia «pode», o coletor dizia «não».

**SFR Lombardia (IT-T3-022):** a rota do contrato é a página inicial (as duas leituras deixam passar); a página para onde ela salta, `/wps/portal/site/sfr`, era PROIBIDA pela leitura antiga e é **PERMITIDA** pela nova (`Allow: /wps/portal/site/sfr`).

**Diferença com a medição offline:** offline davam 11 a abrir (regione.abruzzo.it respondia 403 ao robots); hoje o regione.abruzzo.it responde 200 com regras. A de rede é a de hoje.

**Fora da Git:** os 298 robots baixados em `C:/cur/rfc/rede/robots/` (8,7 MB — muitos são páginas HTML inteiras); sha256 de cada um em `ROBOTS-BAIXADOS.sha256`.

## 3 · Plano de instalação (writeset)

Ficheiros que mudam na produção (`git diff --name-status 5ba9647e robots-rfc9309-v1`):

```
A coleta/robots_rfc9309.py            M coleta/scrap_http.py
M coleta/italy_pilot_collect.mjs      M curadoria/gate_de_rota.py
M curadoria/descobrir.py              M curadoria/worker.py
M provas/cortesia_http_local.mjs      M provas/medir_validadores_coorte.py
M tests/test_c10_5_collection_flow.py M tests/test_integracao_04a_curator.py
A tests/test_robots_rfc9309.py        A provas/robots_rfc/* (5 ficheiros)
M system-map/* (regerado pela cadeia)
```

Nenhum livro de estado, fila, contrato ou decisão é tocado pela instalação.

Passos (quando o dono mandar):
1. parar o bot entre voltas (supervisor), guardar `git status`/`git diff` do serviço;
2. na produção: `git merge --no-ff robots-rfc9309-v1` (ensaiado: sem conflitos sobre 5ba9647e);
3. no serviço: avançar para o merge (`git merge --ff-only`; se houver ficheiros locais, `reset --keep`, nunca `--hard`);
4. `py -m unittest tests.test_robots_rfc9309` e `node provas/cortesia_http_local.mjs` no serviço;
5. religar o bot.

**Efeito depois de instalado (não é automático):** o portão só volta a ler o robots destas fontes quando a VALIDATE_ROUTE correr de novo. Para as 52 que mudam (lista em `ROBOTS-COM-REDE.json → MUDAM`) o dono decide se se enfileira a revalidação já; as 9 READY que fecham passariam a CONTRACT_READY_ROUTE_BLOCKED (as 6 ARPAE por Disallow real; as 3 com HTML como «NÃO SEI — ilegível»). O coletor já as recusa hoje, por isso a coleta não perde nada que colha hoje.

## 4 · Decisões para o dono

- **HTML no lugar do robots = recusa.** É a regra da casa (a D34 mandou manter). A RFC sozinha deixaria passar (lê o HTML como robots sem regras). Fecha 37 fontes, 3 delas READY.
- **4xx = sem robots**, incluindo 401/403 (norma). Hoje abre 2 fontes; muitas vezes um 403 ao robots é um muro anti-robô, e a página também vai dar 403.
