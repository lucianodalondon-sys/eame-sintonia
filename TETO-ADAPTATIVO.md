# TETO-ADAPTATIVO — D124: o limite de coleta é o limite das ferramentas

> Decisão do dono (27/09 ~21:30): «precisamos dos maiores limites ou sem limites de scrap e coleta por
> dia […] quando chegamos no limite, precisamos avisar o scrap engineer». O 5/domínio/24h (D7 teste →
> D38/D41 → D79 → D86) **nunca foi medido** e deixa de ser a regra.

Base: `b273660` (servico-20260923-0923). Branch: `claude/adaptive-collection-ceiling-i3n4jh`.

## 1 · O que mudou

**Um dono só da política:** `coleta/cortesia_adaptativa.py` + gêmeo `coleta/cortesia_adaptativa.mjs`,
números em `regras/POLITICA-CORTESIA-ADAPTATIVA.json` (um sítio só, lido pelos dois).

| API | faz |
|---|---|
| `orcamento_do_dominio(host)` | quantos pedidos ainda cabem **agora** (None = NÃO SEI) |
| `reservar(host, run_id, linha)` | pergunta e escreve num passo, sob o trinco: `RESERVADO` / `ADIADO_ATE` (+`MOTIVO`) / `FAIL` / `UNKNOWN` |
| `registrar_resposta(host, status, headers, …)` | mede o sinal, fecha o «1 de cada vez», recua, alerta |
| `registrar_rendimento(host, pedidos, documentos_novos)` | rendimento baixo → alerta |
| `teto_vigente(host)` | o orçamento de 24 h em vigor (para quem planeia) |
| `--estado <host>` · `--resumo` · `--pergunta [data]` | CLI de leitura e o bilhete do Scrap Engineer |

**Livro append-only** (ndjson) em `SINTONIA_CORTESIA_LIVRO` (o nome antigo `SINTONIA_TETO_24H` aponta
para o mesmo). O estado de cada domínio **não se guarda**: deriva do livro pela mesma dobra em Python e em
Node (paridade provada). Livro ilegível = UNKNOWN; sem livro = `reservar` dá FAIL.

**Política inicial (PROPOSTA declarada, ajustável no JSON — não é medida):**

| classe | domínios | inicial/24 h | teto de segurança | mínimo | pausa |
|---|---|---|---|---|---|
| SITE | o resto | **40** | 640 | 5 | 5 s |
| PLATAFORMA_GRANDE | youtube, linkedin, instagram, facebook | 20 | 320 | 2 | 10 s |
| API_COM_LIMITE_PUBLICADO | openalex, crossref, orcid, googleapis (YouTube Data) | o **publicado** | = publicado (não dobra) | 5 | a publicada |

- **Sobe:** dobra a cada janela de 24 h **sem sinal** e que **usou ≥ metade** do orçamento (um site que
  recebeu 2 pedidos não provou que aguenta 80), até ao teto de segurança.
- **Recua:** 1.º sinal (429, 503, 403 novo, Retry-After, página de desafio/CAPTCHA, 3 timeouts em série,
  queda de bytes na mesma URL) → metade (nunca abaixo do mínimo) e cumpre o Retry-After; **2 sinais em 24 h
  = pausa de 24 h**.
- **Concorrência:** 1 pedido de cada vez por domínio (lease de 150 s se o executor morrer); domínios
  diferentes em paralelo até `LIMITE_GLOBAL_EM_PARALELO = 8`. Crawl-delay maior do robots manda.
- **Porquê 40:** edagricole.it tem 17 fontes × ~2,4 pedidos medidos por fonte ≈ 40 → as 17 cabem num dia
  (hoje: 15 rodadas adiadas 24 h cada). 40 × 5 s ≈ 3,5 min de atividade/dia no domínio. 640 × 5 s ≈ 53 min.
- **APIs:** limites citados da documentação pública (links no JSON) **de memória, NÃO CONFERIDOS** — a
  missão proíbe visitar sites. `ESTADO_DA_CITACAO = NAO_CONFERIDO_NESTA_MISSAO`. Conferir antes de confiar.

**Alerta ao Scrap Engineer:** recuo, pausa 24 h, teto de segurança esgotado, limite publicado esgotado e
rendimento < 0,25 doc/pedido (amostra ≥ 20) → bilhete em `ALERTAS-SCRAP-ENGINEER.ndjson` (ao lado do
livro: domínio, classe, linha, sinal medido, recibos, o que estudar: feed, sitemap, conditional GET, rota
JSON, lote de API). Um por domínio e tipo a cada 24 h. `--pergunta` monta `PERGUNTA-SCRAP-ENGINEER-<data>.txt`
(texto montado, **sem LLM**).

## 2 · Onde (os sítios que tinham o 5 agora perguntam à política)

| sítio | antes | agora |
|---|---|---|
| `coleta/dominio_registavel.py` | `TETO_D38 = 5` | saiu; fica só QUEM paga (domínio + D41) |
| `coleta/reserva_24h.py` | teto 5 em JSON de 24 h | **fachada** de `cortesia_adaptativa` (qtd=1; `teto=` recusado) |
| `coleta/italy_pilot_collect.mjs` | `TETO_POR_HOST: 5`, `reservar24h` próprio | `tetoDe(host)` = vigente; reserva/regista na política; `%header{retry-after}` e `cf-mitigated` no reboque do curl; timeout (curl 28) vira marca; sem livro, sinal corta o domínio na corrida |
| `regras/motor_de_rota.mjs` (D40) | 3 alvos (= 5 − 2) | `alvosPorFonte` = o que cabe no domínio − 2 (mín. 3); 3 fica só como omissão |
| `coleta/teto_da_onda.py` + `scrap_http.py` | `TETO_POR_OMISSAO = 5` | teto por domínio; com livro, reserva e regista a resposta (handler `http_response`) |
| `ferramentas/big_collection/onda_web.py` | `TETO = 5` | `teto_do_dominio(d)`; fonte sem histórico **prevê** 5 (previsão, não teto) |
| `ferramentas/big_collection/rodadas.py` | `TETO = PT.TETO_D38`, janela D79 ligada | teto por domínio; D79 **desligada por omissão** (`--janela-24h` liga); fontes sem orçamento agora ficam ADIADAS (`TETO_ADAPTATIVO`); `--cortesia=` |
| `ferramentas/maestro_social/maestro_social.py` + `curadoria/plano_onda_social.py` | `TETO = 5`, `TETO_D38 = 5` | teto por domínio |
| `coleta/pesquisadores_t6.py` + `coleta/lista_mestra_mur.py` | `TETO_POR_DOMINIO = 5` | `teto_por_dominio(d)` = limite publicado da API |
| `provas/prova_teto_dominio.py` | «passou de 5?» | «passou do **orçamento vigente**?» + `--cortesia`: reproduz o livro (pausa, Retry-After, rajada, pausa mínima, teto de segurança, orçamento vigente) + nenhum pedido sem reserva |
| `medidas/materia_prima_por_dia.py` | — | **painel** documentos novos/dia e itens novos na Sala/dia por linha, só leitura |

**Continua (não é limite de quantidade):** robots.txt (D91) — ilegível continua **não** sendo permissão
(provado: C1 e mutante M4); Crawl-delay; sem login/cookie/CAPTCHA/contorno/rota paga; D88 desligado; VPN IT;
um escritor da Sala; Admission. Nada disto foi tocado.

**Override manual:** `SINTONIA_TETO_POR_HOST=N` e `SINTONIA_PAUSA_POR_HOST_S=N` continuam valendo como
decisão do operador escrita no ambiente (os testes antigos usam-nas).

**Não feito (declarado):**
- `TETO_LINKEDIN_NA_ONDA = 1` (C2) ficou: é vídeos por conta, não teto de domínio. Com PLATAFORMA_GRANDE
  em 20, a razão aritmética dele (6 > 5) desapareceu — o coordenador pode subi-lo para o 2 do contrato.
- Outros 5 próprios fora da lista da missão continuam: `curadoria/colher_prova_territorio.py`,
  `ferramentas/legacy99/revalidar_em_rondas.py`, `ferramentas/seguir_pesquisadores/*` (S.TETO),
  `scripts/capa_materia/medir_d40.mjs`, provas antigas (`provas/t2_boletins`, `boletins_data_local`).
- O transporte do T6 (`corpus_pesquisador._get`) não reserva no livro: o T6 lê o orçamento, mas os pedidos
  dele não entram no livro. O Scrap Python regista só status + cabeçalhos (sem corpo: sem desafio/queda de bytes).
- O livro cresce sem compactação (previsão: ~300 bytes/pedido; 10 000 pedidos/dia ≈ 3 MB/dia). Rodar por
  mês é o próximo passo se o volume vier.

## 3 · Instalar (coordenador)

```bash
git fetch origin claude/adaptive-collection-ceiling-i3n4jh
git merge --no-ff origin/claude/adaptive-collection-ceiling-i3n4jh     # na linha de serviço
# o livro da cortesia (append-only), partilhado por TODAS as linhas de rede:
set SINTONIA_CORTESIA_LIVRO=C:\...\eame-sintonia\data\cortesia\LIVRO-CORTESIA.ndjson    (PowerShell: $env:...)
py -m unittest tests.test_cortesia_adaptativa tests.test_contador_24h        # deve dar OK
py ferramentas/big_collection/rodadas.py --correr --sha256=<coorte> --base=<pasta> --cortesia=%SINTONIA_CORTESIA_LIVRO%
py coleta/cortesia_adaptativa.py --resumo                                     # estado de cada domínio
py coleta/cortesia_adaptativa.py --pergunta                                   # gera PERGUNTA-SCRAP-ENGINEER-<hoje>.txt
bash C:/Users/London1/orca-tools/consultar_scrap_engineer.sh  < data/cortesia/PERGUNTA-SCRAP-ENGINEER-<data>.txt   # forma de passar o texto: NÃO SEI (não li o script)
py medidas/materia_prima_por_dia.py --estados=<pasta das ondas> --cortesia=%SINTONIA_CORTESIA_LIVRO%
py provas/prova_teto_dominio.py --cortesia %SINTONIA_CORTESIA_LIVRO%          # reprodução do livro
```

`data/cortesia/` não existe no repositório: nasce no primeiro pedido. Nenhum livro vivo foi tocado.

## 4 · Previsão ≠ medido

| | |
|---|---|
| **MEDIDO (aqui, sem internet)** | servidor local: 1 pedido de cada vez com 2 executores concorrentes (máx. em curso = 1); orçamento respeitado; livro = servidor; 429+Retry-After → metade e 0 pedidos durante a espera; desafio 2× → pausa 24 h + bilhete; 503 → sinal; dia limpo → dobra (6 → 12) e o servidor vê > 6; robots ilegível → só o robots |
| **PREVISÃO (não medido)** | que 40/24 h não irrita nenhum site real; que edagricole.it cabe num dia; que o volume sobe ~8× por domínio no 1.º dia e até 128× no teto; os limites das APIs (citados, não conferidos) |
| **NÃO SEI** | o limite real de cada site (é isso que o livro vai medir); o formato de argumentos do `consultar_scrap_engineer.sh` |

## 5 · Provas

RESULTADOS_AQUI

## EM PALAVRAS SIMPLES

Antes, o SINTONIA só podia bater 5 vezes por dia na porta de cada site — um número de teste que virou lei
sem nunca ser medido. Agora cada site começa com 40 batidas por dia, uma de cada vez e com calma entre
elas. Se o site não reclama, no dia seguinte pode 80, depois 160, até um teto de segurança. Se o site
reclama (manda «espere», mostra um CAPTCHA, fica lento), o SINTONIA corta pela metade, espera o que o site
pediu, e se reclamar duas vezes no mesmo dia para 24 horas naquele site. Toda vez que isso acontece, sai um
bilhete pronto para o Scrap Engineer estudar um caminho mais esperto (feed, sitemap, API). As regras de
educação (robots.txt, sem login, sem disfarce) continuam iguais. E há um painel novo que conta o que importa:
quantos documentos novos entraram por dia.
