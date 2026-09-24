# KNOW-HOW DELTA — D24 · O REEL DE PESSOA NO INSTAGRAM

**QUANDO:** 2026-09-23 · **BRANCH:** `scrap-linkedin-v1` · **DONO DA DECISÃO:**
D22 + D24 (`C:/Users/London1/auditoria-madrugada/DECISOES-DONO-2026-09-23.md`).
**FORMA:** delta interino (o know-how canónico passa a §199 numa missão de
coordenação; este ficheiro não é um segundo know-how).

## O QUE MUDOU

| antes | depois |
|---|---|
| `INSTAGRAM/FETCH_TRANSCRIPT` · `NAO` · `ROUTE_NOT_ALLOWED` | `SIM` · `PROVED`, com os **três eixos**: `OWNER_AUTHORIZED = SIM` · `PLATFORM_POLICY_STATUS = DISALLOWED` · `LIMITE = PUBLIC_PERSON_VIDEO_ONLY` |
| as três fases do Reel (`captura-reel`, `audio-reel`, `transcricao-reel`) eram **recusadas** pela porta operacional citando a política | entram pela **porta canónica** (orquestrador com `fase`, `pais`, `fonte`, `url`); quem ainda trava é a **falta de `SOURCE_ID`**, dito pelo coletor (`FONTES_AUSENTES`) |
| o canário do Instagram **não tinha corrido** («recusa antes da rede») | canário real corrido: Reel público de pessoa do agro, 696 245 bytes, sha256 `ea372eeb…`, egresso IT nas duas pontas, US$ 0 |

## POR QUÊ

A recusa **colapsava os dois eixos num só**: dizia «a plataforma proíbe» e
escondia quem já tinha assumido o risco. A casa nunca usou uma leitura de um eixo
só para o YouTube (D17.4/C13) nem para o LinkedIn (D23) — e a **D22** já tinha
autorizado os Reels do Instagram por URL directa. A D24 estendeu a mesma
autorização às **PESSOAS** do agro.

```
UMA LEITURA DE UM EIXO SÓ NÃO É UMA DECISÃO: É METADE DELA.
A PLATAFORMA CONTINUA A PROIBIR. QUEM MUDOU FOI O DONO DO RISCO.
```

## PROVA

```
provas/canario_d24_reel_de_pessoa.py            canário real, base descartável
provas/_mutantes_d24.py                         10 mutações · 10 mortes
tests/test_d24_video_de_pessoa.py               22 provas (6 novas, do Instagram)
tests/test_c14c_permissao_instagram.py          ALLOWED só com os dois eixos
tests/test_c13_route_gate.py                    âncora com a linha mudada e a razão
tests/test_as_duas_portas_do_scrap.py           fase autorizada entra canónica
docs/sintonia-scrap/D24-VIDEO-DE-PESSOA.md §6   o documento da prova
```

## CONSEQUÊNCIA PARA QUEM VEM DEPOIS

1. **O PERFIL continua fechado** — Instagram (muro de login na grade por HTTP) e
   LinkedIn (999/`authwall`). Não se contorna.
2. **`URL` não é `SOURCE_ID`** — a publicação de uma pessoa ainda **não tem
   fonte**. É o item aberto nº 1 da D24, e é do dono do catálogo (candidata →
   Curador), não do Scrap.
3. **O vocabulário de limites continua fechado** e cresce **declarado**:
   `PUBLIC_PERSON_VIDEO_ONLY` entrou com prova; ampliá-lo exige decisão escrita.
4. **`PLATFORM_POLICY_STATUS = DISALLOWED` viaja em cada objeto.** Apagar essa
   frase é reescrever a evidência.
5. **A tela de pessoas nomeadas continua com a revisão jurídica** — autorizar a
   coleta não autoriza nenhuma tela a listar quem publicou.
---

## PARA QUEM JUNTAR COM O `scrap-portas-v1` — AS LINHAS QUE MUDARAM, E POR QUÊ

**De:** `scrap-linkedin-v1` (blocos 7b–9). **Regra desta secção:** só entram
ficheiros que EU toquei. Onde não toquei, digo que não toquei — uma lista
incompleta é pior do que nenhuma, porque quem junta confia nela.

| ficheiro | o que mudou | por quê |
|---|---|---|
| `provas/canario_d24_video_de_pessoa.py` | porta de egresso do DONO (`superficie/rede.py`) **antes e depois**; `EGRESSO_EXIGIDO`; `'superficie'` no `sys.path`; `import rede as superficie` | o canário media o egresso com um `ipinfo` próprio e **não** usava o portão do dono, nem media as duas pontas. Fora de IT a corrida não começa e o artefacto não é escrito |
| `provas/canario_d24_video_youtube_de_pessoa.py` | **NOVO** — o canário do vídeo de agrónomo italiano no YouTube | era a metade que faltava (§7 do D24) |
| `provas/canario_d24_reel_de_pessoa.py` | **NÃO TOQUEI** | — |
| `tests/test_c10_4_route_gate.py` | **SÓ UMA linha de asserção**, em `test_o_check_conhece_a_capacidade_da_matriz`: `assertEqual(mz.PERMITIDA_SIM, v['STATE'])` → `assertEqual(scrap.PODE, v['STATE'])`, **mais** a contraprova com `_PoliticaNegativa()` | a linha antiga exigia `ALLOWED` (palavra da **matriz**) de um campo que é do **portão** (`CAN_COLLECT_NOW`). O portão **espelha** a matriz quando ela RECUSA e diz a palavra dele quando pode colher — a contraprova nova guarda esse espelho |
| `tests/test_c10_4b_um_caminho_so.py` | **NÃO TOQUEI** | ⚠️ é do `scrap-portas-v1`; o conflito é dele |
| `tests/test_c10_5d_decisao_instagram.py` | **NÃO TOQUEI** | ⚠️ idem — o `test_T10` falha em disco por uma pasta VAZIA (`data/raw/REEL-MIDIA`, ignorada, 0 ficheiros) e **passa em clone limpo**; não é regressão da árvore |
| `tests/test_c10_6d_portas_canonicas.py` | **NÃO TOQUEI** | ⚠️ `test_8_a_rota_da_janela_e_a_que_a_matriz_nomeia` **falha igual na base `f5b61ec6`** (`'ROUTE_NOT_ALLOWED' != 'ALLOWED'`) — é herdada, não desta missão |
| `docs/sintonia-scrap/D24-VIDEO-DE-PESSOA.md` | §1 ganhou o **Egresso C** (IT) e a comparação campo a campo Miami × Palermo; §2 ganhou a linha do `EGRESSO` e o aviso de correção; **§7 novo** | a repetição pela VPN IT e a metade italiana precisavam de ficar escritas onde o dono lê |
| `system-map/data/architecture.declared.json` | **DUAS peças novas**: `C-PROVA-CANARIO-D24-REEL-PESSOA` e `C-PROVA-CANARIO-D24-YOUTUBE-PESSOA` | o validador reprovava `P9_CODIGO_DECLARADO`: os dois canários eram código que nenhuma peça do mapa reivindicava |
| `data/samples/CANARIO-D24-PESSOA-V1.json` | **reescrito** pela corrida de IT | o egresso que viaja no objeto é o **medido na hora**. A corrida de Miami (**US**, `146.70.98.171`) fica registada no §1 do D24 — as duas concordaram em 12 dos 13 campos |
| `data/samples/CANARIO-D24-YOUTUBE-PESSOA-V1.json` | **NOVO** | artefacto do canário do YouTube |

### O confronto que vai dar trabalho, e como o ler

```
c10_4    → eu mexi (1 asserção + contraprova). Conflito esperado: resolver TOMANDO a minha versão
             se o outro ramo não tocou nesta função.
c10_4b   → eu NÃO mexi. Se houver conflito, é entre o `scrap-portas-v1` e a base.
c10_5d   → eu NÃO mexi (a falha era do meu disco, não da árvore).
c10_6d   → eu NÃO mexi; falha na base também.
```

> **A BATERIA CONTA POR NOME, E O NOME É O CAMINHO INTEIRO.** Comparar
> `test_c10_5d_decisao_instagram.py` com `...::ADecisaoNaoTrouxeNadaAtrasDela::test_T10`
> é comparar coisas diferentes: o número «3 falhas» que eu vi primeiro no meu
> disco era **1 nova + 1 do disco + 1 da base**, e só a comparação em clone
> limpo, por nome completo, separou as três.
