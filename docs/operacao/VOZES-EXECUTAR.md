# VOZES-EXECUTAR — o comando que o coordenador corre para provar o papel das vozes

> Ramo `vozes-agronomos-v1` (a partir do vivo `69b0e23f`). Missão: coordenação 11:08 (VOZES-EXECUTAR). **Eu não
> corri nada com rede**: só o ensaio a seco com o proxy fechado (0 pedidos). Não é rota de coleta: nada entra em
> RAW, na Sala, na fila ou nos livros do vivo — o robô pode continuar a correr.

## Resposta curta

- **3 peças**, todas em `ferramentas/vozes/`:
  - `montar_plano.py` (sem rede) — monta `PLANO-EXECUCAO.json` só com endereços que **já estão nos nossos livros**:
    a busca do próprio site (lida do `<form>` de uma página desse site já guardada) ou a entrada das
    candidatas/contratos do vivo;
  - `colher_papel.py` (**rede, o coordenador corre**) — reaproveita as peças da casa do clone `C:/g/mprova`
    (`canario.buscar` e `rede.portao_de_egresso`), como o `colher_prova_territorio.py`, mas com o teto desta
    missão;
  - `ler_provas.py` (sem rede) — diz, por voz, **SIM** / **NAO SEI**; **NAO** só por leitura humana.
- **26 pedidos em 12 domínios**: ronda 1 = 22 (11 domínios) · ronda 2 = 2 (Georgofili, 2.ª pessoa) · ronda
  NOTURNA = 2 (Rete Rurale, só 01–03 h UTC). **Máximo 2 por domínio por ronda** (robots.txt + 1 página).
- **Colisão com a 4.ª onda: 0** — medida contra `auditoria-madrugada/C2-ONDA4/rodadas.txt` (e o executor recusa
  sozinho qualquer domínio que lá esteja). myfruit, Koppert e Terra e Vita (edagricole) ficam para **depois**.
- **Já provado sem pedido nenhum (passo 0, as descrições que o HTML guardado já traz): 3 de 30** — Hanspeter
  Felder («direttore della Cooperativa dei produttori sementi della Val Pusteria»), Bruno Basso («prof. … della
  Michigan State University»), Simon Pierce (página oficial, P5).
- **`videos.list`**: só o pedido, em `PEDIDO-VIDEOS-LIST.json` — **26 ids, 1 chamada** pelo Scrap (GitHub).
  ⚠️ Correção à VOZES-AGRONOMOS: lá escrevi «21 ids»; contados, são 29 fichas com vídeo, 26 vídeos distintos
  depois de tirar o V18/V19 (o mesmo vídeo) e os 2 já provados.

## 1. O que o executor recusa, mesmo que o plano peça

| Regra | Onde | Testado |
|---|---|---|
| no máximo **2 pedidos por domínio** por corrida (robots.txt + 1 página) | `TETO_POR_DOMINIO = 2` | ✔ (e o mutante M1 morre) |
| **robots.txt lido e cumprido** (agente «*», como a casa); ilegível = não é licença, pára | `urllib.robotparser` | ✔ M2 |
| **CNR, Coldiretti, ANGA, Unaprol**: 0 pedidos (coordenação 10:13) | `PROIBIDOS` | ✔ M3 (teste próprio: não depende da lista da onda) |
| **domínio da 4.ª onda**: 0 pedidos; sem o ficheiro das rodadas, **não corre** | `--onda4=` | ✔ M4 |
| **reterurale.it** só na ronda `NOTURNA-1` **e** entre 01 h e 03 h UTC | `JANELA_NOTURNA_UTC` | ✔ M5 |
| **portão de egresso IT** antes de cada domínio; sem PASS, 0 pedidos | `rede.portao_de_egresso("IT")` | ✔ M6 |

`tests/test_vozes_executar.py`: **16/16**. Mutação (`data/derivados/VOZES-AGRONOMOS/mutacao.py.txt`): **8/8 mortos**
(M7: SIM sem palavra de papel; M8: sha256 do recibo não conferido). O M3 sobreviveu na 1.ª corrida — o `cnr.it`
também está na lista da 4.ª onda e o teste não separava as duas regras; ganhou teste próprio.

## 2. Os comandos (o coordenador corre; VPN IT)

```bash
B=C:/Users/London1/orca/workspaces/eame-sintonia/vozes-agronomos-v1      # o ramo (ou um checkout de origin/vozes-agronomos-v1)
P=$B/data/derivados/VOZES-AGRONOMOS
S=C:/Users/London1/sintonia-sala-italia/vozes-agronomos                   # saida: bytes + recibos, fora do Git
O4=C:/Users/London1/auditoria-madrugada/C2-ONDA4/rodadas.txt
cd C:/g/mprova                                                            # a casa: canario.py e rede.py

# 0. o portao (o executor volta a pedi-lo antes de cada dominio)
py superficie/rede.py --portao-de-egresso IT                              # tem de dar PASS

# 1. ronda 1 — 22 pedidos, 11 dominios, ~2 min (3 s entre os 2 pedidos de um dominio)
py $B/ferramentas/vozes/colher_papel.py --casa=. --plano=$P/PLANO-EXECUCAO.json --ronda=1 --saida=$S --onda4=$O4

# 2. ronda 2 — 2 pedidos (georgofili.it, a 2.a pessoa). NOUTRO DIA (janela de 24 h: o georgofili.it ja levou 2 na ronda 1)
py $B/ferramentas/vozes/colher_papel.py --casa=. --plano=$P/PLANO-EXECUCAO.json --ronda=2 --saida=$S --onda4=$O4

# 3. ronda NOTURNA — comando a parte, entre 01:00 e 03:00 UTC (robots Visit-time da Rete Rurale)
py $B/ferramentas/vozes/colher_papel.py --casa=. --plano=$P/PLANO-EXECUCAO.json --ronda=NOTURNA-1 --saida=$S --onda4=$O4

# 4. a leitura das provas — sem rede, depois de cada ronda (le todos os RECIBO-RONDA-*.json da pasta)
cd $B
py ferramentas/vozes/ler_provas.py --plano=$P/PLANO-EXECUCAO.json --vozes=$P/VOZES.json --provas=$S
#    -> $S/LEITURA-DAS-PROVAS.json
```

O que fica em `$S`: `<ID>/0_ROBOTS.bin`, `<ID>/1_ALVO.bin` (os bytes) e `RECIBO-RONDA-<r>.json` (URL, HTTP,
sha256, bytes, hora, egresso de cada pedido; e as fichas RECUSADAS com o porquê).

## 3. As rondas (de `PLANO-EXECUCAO.json`)

| Ronda | Voz | Pessoa / série | Pedido | Alvo |
|---|---|---|---|---|
| 1 | V03 | Giulia Zuecco | ENTRADA | `https://www.dafnae.unipd.it/` |
| 1 | V04 | Silvia Toffolati | BUSCA | `https://disaa.unimi.it/it/cerca-nel-sito?search_term=Silvia+Toffolati` |
| 1 | V05 | Riccardo Castaldi | ENTRADA | `https://www.terremerse.it/` |
| 1 | V16 | Pietro Baroncini (e V28, a mesma página) | ENTRADA | `https://www.conserveitalia.it/` |
| 1 | V17 | Ernesto Comite | ENTRADA | `https://www.agraria.unina.it/` |
| 1 | V18 | Mario Enrico Pè | BUSCA | `https://georgofili.it/search.html?q=Mario+Enrico+P%C3%A8` |
| 1 | V23 | webinars CRPV | ENTRADA | `https://www.crpv.it/` |
| 1 | V24 | CONAF «difesa delle colture» | BUSCA | `https://www.conaf.it/?s=difesa+delle+colture` |
| 1 | V25 | Brunello «annata agronomica» | ENTRADA | `https://www.consorziobrunellodimontalcino.it/` |
| 1 | V26 | AMAP «mosca delle olive» | ENTRADA | `https://www.amap.marche.it/servizi/fitosanitario` |
| 1 | V30 | ANBI «agronomia moderna» | ENTRADA | `https://www.anbi.it/` |
| 2 | V19 | Marina Carcea | BUSCA | `https://georgofili.it/search.html?q=Marina+Carcea` |
| NOTURNA-1 | V29 | Rete Rurale «monitoraggio fenologico» | ENTRADA | `https://www.reterurale.it/` |

**Sem pedido nesta missão:** DEPOIS da 4.ª onda — V10, V11 (myfruit.it), V20 (edagricole), V27 (koppert.it) ·
FORA — V21 (CNR) · JÁ PROVADO — V22 · DESCOBRIR o site — V01, V02, V06, V07, V08, V09, V12–V15 (domínio fora
dos nossos livros) · MESMA PÁGINA — V28 (lê a do V16).

⚠️ **O que esperar, com honestidade:** as 6 BUSCAS podem dar a pessoa com o papel; as 7 ENTRADAS são a página
inicial do site — é **provável que deem NAO SEI** (a pessoa raramente está na página inicial). Não inventei
endereços de página pessoal: onde não havia busca guardada, fica a entrada que os livros têm.

## 4. A leitura das provas

`ler_provas.py`, sem rede. **SIM** só quando o **apelido** da pessoa (sem acentos) e uma **palavra de papel**
(agronom·, docente, professor/prof., ricercat·, tecnic·, responsabile, direttor·, dott., universit·,
dipartimento…) aparecem no **mesmo trecho** (±200 letras). Tudo o resto é **NAO SEI**, com o porquê. **NAO**
(«a prova diz outro papel») **nunca é automático**: fica o campo `LEITURA_HUMANA` e o trecho para quem ler.

- **Passo 0 (já corrido, sem rede):** a descrição do vídeo que o HTML guardado já traz — **só a descrição**, nunca
  o título (o título é o que se quer provar; julgar com ele seria circular — foi o meu 1.º erro nesta missão:
  dava 9 SIM, 6 deles do próprio título). Resultado em `LEITURA-PASSO0-SEM-REDE.json`: **3 SIM**.
- **Passo 1:** a página colhida — os bytes conferidos contra o **sha256 do recibo** antes de ler.
- As séries sem nome (V23–V30) nunca dão SIM automático: a pessoa lê-se à mão nos trechos.

## 5. O pedido da `videos.list` (só o pedido)

`data/derivados/VOZES-AGRONOMOS/PEDIDO-VIDEOS-LIST.json`: **1 chamada**
`GET https://www.googleapis.com/youtube/v3/videos?part=snippet&id=<26 ids>&key=<YOUTUBE_DATA_API_KEY>`, pelo
Scrap (`sintonia-scrap.yml`, fases oficiais do YouTube; a chave só existe no segredo do GitHub). Guardar
`snippet.title/description/publishedAt/channelId/channelTitle`. **Não:** `captions.download` (exige o dono),
áudio (III.I.7), páginas `/watch`. A descrição que voltar entra no passo 0 com a mesma regra.

## 6. Ensaio a seco (feito)

`cd C:/g/mprova` + o comando da ronda 1 com `HTTP(S)_PROXY=127.0.0.1:9`: as peças da casa carregaram, o portão
deu **BLOCKED**, o executor fez **0 pedidos** e escreveu o recibo (`data/derivados/VOZES-AGRONOMOS/ENSAIO-A-SECO/`).
O clone `C:/g/mprova` ficou como estava (os mesmos ficheiros modificados antes e depois).

Mapa: não regerado (PRONTO-SEM-MAPA).
