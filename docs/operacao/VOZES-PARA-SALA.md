# VOZES-PARA-SALA — como os 25 relatores entram pela porta canónica (sem inventar campo)

> Ramo `vozes-agronomos-v1`, **já junto com o vivo `278cd489`** (lote 2, 13:55; sem conflito; `tests.test_vozes_executar`
> 16/16 depois da junção). Missão: coordenação 14:00. **Sem rede**: código do vivo lido pelo git, Sala só leitura
> (`default_transaction_read_only=on`). Nada instalado.

## Resposta curta

- **O contrato que existe não tem «quem fala dentro de um item».** Procurei: o `READY`/Sala não tem campo de
  falante; `PERSON_ID` na Admissão está na lista **`NAO_E_ITEM`** (uma ficha de pessoa não é item);
  `participacao_na_derivacao` (029) liga **bruto → derivado**, não pessoa → item; `SPEAKER_ID` só existe na
  **CAP-FIELD** da Bíblia da Intelligence (chave de junção da Intelligence — atrás da trava D33).
- **O contrato de PESSOA que existe** é o da migração 002 + 016: **pessoa → origem → canal → conteúdo**, e a vista
  `v_human_sensor_admissivel` só aceita um canal **`PERSON_PROFILE` com evidência** de uma **origem que é pessoa**.
  Um canal de organização tem o motivo escrito: **`ORGANIZACAO_NAO_E_VOZ_HUMANA`**. Na Sala real: **1 canal, 0
  pessoas, 1 origem** — esta camada está por usar.
- **Portanto, pelos dois caminhos que existem:**
  - **como candidata (fonte-pessoa): 0 dos 25 podem entrar já.** Nenhum tem, nos nossos livros, um canal PRÓPRIO que
    publique itens — e a porta (QUALIFY → contrato → canário) só aceita quem publica uma família de itens.
  - **como item: os 25 já são conteúdo de fontes que existem**, com nome e cargo **no texto do item** (não num
    campo). **5 já estão na Sala** (Hannes Tauber, Michele Tenore, Francesco Ferraro, Antonio Ferrante, Federica
    Demaria); **17 estão em vídeos do acervo** (canais da rota Scrap, à espera do teste CANAIS-41); **3 estão em
    textos do acervo** fora da Sala (Baruzzi, Rivalta, Ferrini — é a ACERVO-PARA-SALA); **1 é uma página de
    serviço**, não um item (Nardi).
- **O que falta para a «Voci dal Campo» os consumir como PESSOAS é uma decisão de contrato**, não uma coleta: um
  lugar para «esta pessoa, com este cargo provado, fala neste item de um canal de organização». Não o inventei.
- **As 2 visitas (CRPV, ANBI)**: plano `PLANO-PROGRAMAS.json`, **4 pedidos em 2 domínios, 1 ronda**, colisão com a
  4.ª onda 0, ensaio a seco feito (0 pedidos com a rede fechada).

## 1. Os 25, um a um

| # | Relator | Onde já está | Como entraria hoje | Prova do cargo | O que falta |
|---|---|---|---|---|---|
| 1–5 | Sambo, Tosini, Colla, Mariotti, Ronga | vídeos `IT-T8-006` (L'Informatore Agrario) no acervo | **item** (vídeo pela rota Scrap, D53: página, título, data, canal) | descrição do dono do canal (Ronga: só a instituição) | o teste CANAIS-41 (P1/P2); a descrição entra como texto do item via `videos.list` |
| 6–8 | Fagioli, Foschi, Onofri | vídeos `IT-T9-014` (Conserve Italia) no acervo | idem | descrição do dono do canal | idem |
| 9–10 | Niederegger, Felder | vídeos `IT-T10-017` (myfruit) no acervo | idem | descrição do dono do canal | idem |
| 11 | Hannes Tauber | **Sala** (`IT-T10-018`, notícia myfruit) + vídeo `IT-T10-017` | **já é item** | notícia («responsabile marketing di Vog») | — (e não é técnico: cargo comercial) |
| 12–13 | Gorelli MW, Lonardi MW | vídeos `IT-T7-034` (Brunello) no acervo | item (rota Scrap) | descrição («testo a cura di») | idem ao 1–5 |
| 14–17 | Tosi, Zari, Latino, Ferretti | vídeos `IT-T7-026` (CONAF) no acervo | item (rota Scrap) | descrição (Tosi, Zari: cargo NÃO SEI) | idem; o cargo de Tosi e Zari está no artigo CONAF de 16/05/2025 (1 pedido) |
| 18 | Gianluca Baruzzi | acervo (`IT-T10-021`, Plantgest 25/09/2026), fora da Sala | item | notícia («ricercatore del Crea-Ofa») | a ACERVO-PARA-SALA |
| 19 | Stefano Rivalta | acervo (`IT-T10-021`), fora da Sala | item | NÃO SEI (sem cargo formal) | cargo |
| 20–21 | Michele Tenore, Francesco Ferraro | **Sala** (`IT-T3-008`, boletim ARIF 2026, 2 linhas) | **já é item** | boletim oficial («Dott. Agr., Dirigente della Sezione Fitosanitaria» / «Direttore Generale») | — |
| 22 | Sandro Nardi | página de serviço colhida na ronda 1 (AMAP) | **não é item** (página fixa) | página oficial («REFERENTE») | a fonte dele já é `IT-T3-045` (SFR Marche, READY) |
| 23 | Antonio Ferrante | **Sala** (`IT-T5-025`, 2 linhas) | **já é item** | notícia da Sant'Anna | — |
| 24 | Francesco Ferrini | acervo (`IT-T7-139`), fora da Sala | item | notícia | a ACERVO-PARA-SALA |
| 25 | Federica Demaria | **Sala** (`IT-T5-056`) | **já é item** | notícia CREA | — |

Conferido na Sala pelo **nome completo** (só o apelido dava falsos positivos: «Colla», «Tosi», «Zari», «Nardi»
aparecem noutros textos).

## 2. Porque nenhum entra como fonte-pessoa (candidata T7/T8)

- A porta: candidata → **QUALIFY** (`curadoria/atribuir_source_id.territorio_de`, pelo NOME + URL: «… Consorzio
  Agrario …» → T7, «… Università …» → T5) → **BUILD_CONTRACT** → **VALIDATE_ROUTE** → **CANÁRIO** (uma família de
  itens publicados). Uma pessoa sem canal próprio não tem URL que publique itens: o canário recusa-a como recusou os
  Serviços Fitossanitários (`FAMILIA_ESTATICA`).
- A camada humana (`v_human_sensor_admissivel`) só consome **`PERSON_PROFILE` + origem-pessoa**. Os 17 vídeos estão
  em canais de **organização** → `ORGANIZACAO_NAO_E_VOZ_HUMANA`, por contrato.
- Para uma destas pessoas virar fonte-pessoa seria preciso achar **um canal PRÓPRIO** (página pessoal com
  publicações, canal pessoal) — nos nossos livros não há nenhum para os 25. (O Simon Pierce da P5 tem canal
  próprio, `CAND-1199`, mas não está entre os 25.)

## 3. O que falta, por ordem

| Falta | De quem | Nota |
|---|---|---|
| **decidir o contrato de «pessoa que fala num item de organização»** (onde fica, com que prova) | dono | sem ele, os 25 entram como texto de item e a camada humana não os vê como pessoas |
| o teste dos canais pelo Scrap (CANAIS-41, P1/P2) + a `videos.list` já pedida | coordenador | leva 17 dos 25 (os vídeos) para a Sala com a descrição |
| a ACERVO-PARA-SALA | a missão dela | leva Baruzzi e Ferrini |
| os cargos de Tosi e Zari | 1 pedido ao artigo CONAF de 16/05/2025 | link na página colhida na ronda 1 |
| os relatores do CRPV e da ANBI | as 2 visitas abaixo | |

## 4. As 2 visitas — CRPV e ANBI (o coordenador corre; VPN IT)

`data/derivados/VOZES-AGRONOMOS/PLANO-PROGRAMAS.json` — os dois alvos são **links que estão nas páginas colhidas na
ronda 1** (nada inventado):

| Ficha | Alvo | Para quê |
|---|---|---|
| P01 | `https://www.crpv.it/it/eventi/` | relatores dos webinars CRPV (Emepaclima/elateridi, Innova Drupe/albicocco, DATI.METEO4.0/gelate) |
| P02 | `https://www.anbi.it/p/eventi` | relatores da ANBI no Macfrut 2025 (agronomia moderna, difesa attiva) |

```bash
B=C:/Users/London1/orca/workspaces/eame-sintonia/vozes-agronomos-v1     # ou um clone de origin/vozes-agronomos-v1
P=$B/data/derivados/VOZES-AGRONOMOS
S=C:/Users/London1/sintonia-sala-italia/vozes-agronomos
cd C:/g/mprova
py superficie/rede.py --portao-de-egresso IT                              # PASS
py $B/ferramentas/vozes/colher_papel.py --casa=. --plano=$P/PLANO-PROGRAMAS.json --ronda=PROGRAMAS-1 \
   --saida=$S --onda4=C:/Users/London1/auditoria-madrugada/C2-ONDA4/rodadas.txt
#   4 pedidos: robots.txt + 1 pagina em crpv.it e em anbi.it; o crpv.it e o anbi.it ja levaram 2 cada na ronda 1
#   -> correr NOUTRO DIA (janela de 24 h), como a ronda 2
```

Depois: leitura humana dos 2 alvos (como na VOZES-LEITURA-HUMANA) — o leitor automático dá sempre NAO SEI às
séries sem nome, de propósito.

**Ensaio a seco (feito):** o mesmo comando com `HTTP(S)_PROXY=127.0.0.1:9` — portão BLOCKED, **0 pedidos**, 0
recusadas (`ENSAIO-A-SECO-PROGRAMAS/`).

Mapa: não regerado (PRONTO-SEM-MAPA).
