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