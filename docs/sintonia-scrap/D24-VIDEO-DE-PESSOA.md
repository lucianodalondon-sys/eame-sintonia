# D24 · O VÍDEO DE UMA PESSOA DO AGRO — A AUTORIZAÇÃO ESCRITA, E O QUE ELA NÃO ABRIU

**MEDIDO_EM:** 2026-09-23 · **DOIS egressos, e os dois ficam escritos** porque a
máquina mudou de saída a meio da missão (o PC caiu e voltou com outra rota de
VPN) · sem conta, sem login, sem cookie de sessão, sem navegador e **sem rota
paga**.

```
Egresso A · IT/datacenter   149.22.91.171 · AS212238 Datacamp Ltd · Palermo
           └ as medições da manhã: perfil 999, os 4 posts italianos, a amostra
             de 15, e a primeira aquisição do MP4.
Egresso B · US             146.70.98.171 · AS9009 M247 Europe SRL · Miami
           └ depois do reinício: a corrida completa do canário e a conferência
             do perfil.
```

> **E OS DOIS EGRESSOS CONCORDARAM, o que vale mais do que um só:** a página de
> **perfil** respondeu **999** com `authwall` nos dois, e o **MP4** servido nos
> dois tem o **mesmo `sha256`** (`bff909e5…`). O que muda com o país de saída
> não é esta porta.

> ⚠️ E ESTA É A LIÇÃO DE MÉTODO: o egresso que viaja no objeto é o **medido na
> hora**, e não o que estava escrito na missão. Uma corrida que declara «VPN IT»
> porque o pedido dizia «VPN IT» está a inventar uma medição.

**DECISÃO DO DONO:** **D24** — `C:/Users/London1/auditoria-madrugada/DECISOES-DONO-2026-09-23.md`.
O dono REAL autorizou, **por escrito**, a aquisição de **vídeo** (e da
legenda/transcrição e dos metadados públicos do próprio post) publicado por
**PESSOAS do agro** — pesquisador, engenheiro agrônomo, perito agrário,
agrotécnico, creator, influencer — em qualquer plataforma já coberta pela
matriz do Scrap. Risco assumido pelo dono, e por escrito.

```
OWNER_AUTHORIZED        = SIM          (decisão do dono, D24)
PLATFORM_POLICY_STATUS  = DISALLOWED   (LinkedIn: robots.txt, medido)
LIMITE                  = PUBLIC_PERSON_VIDEO_ONLY
```

> **AS DUAS FRASES ANDAM JUNTAS.** A plataforma continua a proibir, e o dono
> assumiu o risco do projeto. Escrever uma sem a outra é a mentira desta rota:
> dizer «autorizado» esconde a proibição; dizer «proibido» esconde quem assumiu
> o risco. Cada objeto que sai daqui carrega as duas.

---

## 1 · A MEDIÇÃO QUE DECIDIU O DESENHO — E NÃO FOI O QUE SE ESPERAVA

A pergunta simples era: «o LinkedIn serve uma página de PESSOA a convidado?».
Medida, a resposta tem DUAS partes, e as duas importam:

| alvo | resposta medida | o que resta fazer |
|---|---|---|
| **PÁGINA DE PERFIL** `linkedin.com/in/<slug>/` | **HTTP 999** com `authwall` no corpo · 1 530 bytes · **zero** `urn:li:activity` | nada. **NÃO SE CONTOURA** |
| **PÁGINA DO POST** `linkedin.com/posts/<slug>-activity-<id>-<hash>` | **HTTP 200** · 93 752 a 115 946 bytes · texto e título servidos | é por aqui que o vídeo se lê |

**A recusa foi provada como sendo DA ROTA, e não do nosso robô.** Três perfis
italianos testados com a UA desta casa deram 999; o **mesmo** alvo com UA de
navegador (Chrome) deu **999 outra vez**; e a **mesma** UA, no **mesmo** egresso,
no **mesmo** minuto, recebeu **200** na página de **organização**. Quem fecha é a
porta — e uma proibição que se confirma pela rede já fez um pedido a ela.

### As quatro páginas de agrônomo italiano, medidas uma a uma

| autor | HTTP | bytes | vídeo |
|---|---|---|---|
| Alessandro Columella | 200 | 115 946 | não |
| Alberto de Rosa | 200 | 103 123 | não |
| Alberto Grimelli (1) | 200 | 94 074 | não |
| Alberto Grimelli (2) | 200 | 93 752 | não |

> **UM POST SEM VÍDEO É UM RESULTADO, E NÃO UMA FALHA.** O que se mediu foi a
> PORTA, e ela está aberta.

### A amostra que mediu a FREQUÊNCIA, não só a existência

15 posts públicos de PESSOA, do acervo da própria casa, um a um, com pausa:

```
HTTP 200 ......... 15 de 15      (nenhum bloqueio, nenhum muro)
com vídeo .......... 1 de 15      (`data-sources` + `data-captions-url`)
```

**Vídeo em post de pessoa é MINORIA.** Dizer isso é o resultado; não dizê-lo
faria a próxima missão prometer cobertura que não existe.

---

## 2 · O CANÁRIO REAL — `provas/canario_d24_video_de_pessoa.py`

A pessoa: **Celestino Domínguez Infante**, profissional do agro (UPL Iberia),
com perfil público `es.linkedin.com/in/celestino-domínguez-infante-423b4957…`.
O alvo foi o **post público** dele — e o perfil **nunca** foi tocado.

| medido | valor |
|---|---|
| `ROUTE` | `linkedin:data-sources-mp4-de-pessoa` |
| `EXECUTOR` | `adaptador_linkedin.video_de_post_publico` |
| `DECISAO_DO_DONO` | **D24** · `LIMITE = PUBLIC_PERSON_VIDEO_ONLY` |
| `MP4` | **6 935 096 bytes** · sha `bff909e5…` · `video/mp4` |
| `LEGENDA` | **1 371 bytes** · sha `09712870…` · `text/vtt` **WebVTT** real |
| `PUBLISHED_AT` | **2026-04-01T16:05:33.664Z** — declarado pela plataforma no JSON-LD `VideoObject` |
| contraprova de identidade | `CONFIRMADA_PELO_ASSET_DO_JSON_LD` |
| `DERIVED` | `AUTHOR_TEXT` 1 061 car. + `NATIVE_CAPTION` 1 358 car. |
| pedidos de rede | **4** — página do post, 1 salto IT→ES, o MP4 e a legenda |
| `CUSTO_USD` | **0.0** |
| limites | sem conta · sem login · sem cookie · sem contornar muro · só público |

Os bytes estão em disco e o `sha256sum` confere com o que o objeto declara. O
bruto está **commitado** (`data/samples/SOCIAL-IT/raw-free/LINKEDIN/`).

> **A PLATAFORMA DECLARA UMA LÍNGUA E SERVE OUTRA**, e isso já era conhecido na
> D23: `data-language` diz `en` e o texto é espanhol. O campo guarda o que a
> plataforma **declarou** — inferir do texto seria fabricar.

### O vídeo que NÃO se encontrou — a metade italiana

O pedido era «1 vídeo de pesquisador ou agrônomo **italiano**». O que existe:

```
posts de PESSOA italiana no acervo da casa ....... 4  (todos medidos: 0 com vídeo)
posts de PESSOA com vídeo, medidos hoje .......... 1  (Celestino — Espanha/agro)
```

**`ITALIANO = NÃO ENCONTRADO NA AMOSTRA`**, e a razão fica escrita em vez de
escondida: a porta que acharia mais perfis de pessoa sem buscador é o próprio
acervo, e nele os italianos com vídeo ainda não apareceram. Não se inventou um
italiano para fechar a frase.

---

## 3 · O QUE A D24 **NÃO** ABRIU — E CADA UM COM O SEU DONO

```
PERFIL DE PESSOA .............. recusado — 999/authwall (medido, não contornado)
CONTATOS ...................... recusado
SEGUIDORES · CONEXÕES ......... recusado
MENSAGENS (DM) ................ recusado
COMENTÁRIOS DE TERCEIROS ...... recusado
ECRÃ DE LOGIN ................. recusado
PERSONAL_SCORING .............. proibido (dono: `docs/regras/LIMITES-DE-DADO-PESSOAL-EAME.md`)
NAMED_RESEARCHER_PUBLIC_SCREEN  BLOCKED_PENDING_LEGAL_REVIEW (dono: revisão jurídica)
```

> **AUTORIZAR A COLETA NÃO VIRA CONFORMIDADE JURÍDICA.**
> O dono assumiu o risco da **aquisição de um vídeo público**. Isso **não** abre
> nenhuma tela do produto para listar pessoas nomeadas: aquele bloqueio é de
> **tela**, e o dono dele é a revisão jurídica da ADAMA. As duas coisas vivem em
> donos diferentes, e nenhuma missão de Scrap troca uma pela outra.

E o **Instagram**, medido lendo o `robots.txt` vivo:

```
«Collection of data on Instagram through automated means is prohibited unless
  you have express written permission from Instagram»
```

> ⚠️ **CORRIGIDO PELO §6 — 2026-09-23.** O parágrafo que aqui estava dizia que
> «o Reel de pessoa segue **RECUSADO** (D19), e o canário do D24 **não foi
> corrido por isso**». **Isso deixou de ser verdade, e a correção é do
> coordenador.** Aquela leitura colapsava os **dois eixos num só**: dizia a
> proibição da plataforma e escondia quem já tinha assumido o risco — que é
> exactamente o desenho que a casa usa no áudio do YouTube (D17.4/C13) e no
> vídeo de organização do LinkedIn (D23), e que a **D22** já tinha aplicado aos
> Reels do Instagram. O parágrafo fica, porque apagá-lo apagaria a medição do
> `robots.txt`, que continua verdadeira: **a plataforma proíbe**. O que se
> acrescenta é o segundo eixo. Ver o §6.

---

## 4 · AS PROVAS DESTA ROTA

| prova | o que mede |
|---|---|
| `tests/test_d24_video_de_pessoa.py` (**16**) | a pessoa passa pelo post; perfil, contatos, seguidores, DM e comentários recusados; a D23 não mudou por efeito lateral; um post sem vídeo não vira vídeo |
| `tests/test_c14c_permissao_instagram.py::test_3` | o vocabulário dos limites é **FECHADO**, e cresceu **declarado** (D24) |
| `tests/test_c10_4_route_gate.py` | `PERMITIDA` continua escrita **só** pela matriz — e reprovou o primeiro mutante, corretamente |
| `provas/_mutantes_d24.py` | **6 mutações · 6 mortes** |
| `tests/test_as_duas_portas_do_scrap.py` | as duas portas não divergem |

```
MUTANTES = 6 · SOBREVIVERAM = 0
```

> **UM MUTANTE QUE SOBREVIVE NÃO É UM INCÓMODO: É UMA PROVA EM FALTA.**
> O primeiro a sobreviver (o `ESTADO`) disse o que faltava — e a resposta certa
> não foi apagar o mutante: foi escrever a prova que faltava **e corrigir a
> matriz**, porque o canário tinha medido o vídeo de pessoa e o estado ainda
> dizia `POSSIBLE_NOT_PROVED`.

---

## 5 · O QUE CONTINUA ABERTO

```
1 · PROMOVER A PESSOA A FONTE     a pessoa entra como FONTE só pela porta canônica
                                  (candidata → Curador), com identidade e território
                                  provados. Sem isso, o RAW fica sem identidade — a
                                  mesma medição que a D23 já fez.
2 · O ASR PARA VÍDEO SEM LEGENDA  dono único, `ferramentas/fala_local.py`. Vídeo sem
                                  faixa sai com `DERIVED_TEXT = ASR_REQUIRED`.
3 · A PORTA DE DESCOBERTA ITALIANA  achar perfis de pessoa do agro italiano sem
                                  buscador: hoje só o acervo da casa. É a lacuna que
                                  a metade italiana desta missão deixou medida.
4 · A TELA DE PESSOAS NOMEADAS    continua bloqueada por revisão jurídica, e esta
                                  missão não a desbloqueia.
```

---

## 6 · O REEL DO INSTAGRAM — a mesma D24 na outra plataforma

**ACRESCENTADO EM 2026-09-23**, por correção do coordenador. A D24 diz «em
qualquer plataforma já coberta pela matriz do Scrap», e a D22 já tinha
autorizado os Reels por URL directa. Faltava **medir** a metade do Instagram, e
não recusá-la.

### O que estava errado, em uma linha

A recusa colapsava os **dois eixos** num só:

```
LEITURA ANTIGA   «a plataforma proíbe»                    -> NAO, antes da rede
LEITURA CERTA    «a plataforma proíbe» + «o dono assumiu» -> SIM, com as duas
```

A segunda linha é a que a casa já escrevia no áudio do YouTube (D17.4/C13), no
vídeo de organização do LinkedIn (D23) e — decisivo — nos **Reels do Instagram
pela D22**.

### O canário real — `provas/canario_d24_reel_de_pessoa.py`

A pessoa: **Alessandro Giglietti**, dottore agronomo (laureado em Agraria,
Univ. Firenze), divulgador — perfil público `@dr.agricultura`, identificado por
**imprensa italiana** (Gazzetta di Siena, Corriere.it), não por inferência nossa
sobre o handle. **O perfil nunca foi usado como fonte.**

| medido | valor |
|---|---|
| `DISCOVERY_METHOD` | janela pública do próprio perfil, **deslogada** (`coleta/instagram_janela.py`) — nenhum buscador |
| `ALVO` | `https://www.instagram.com/reel/DdW2PPWAqht/` — **a publicação**, não o perfil |
| `EGRESS` | **IT** nas **duas** pontas (antes e depois), AS212238 · Palermo |
| `MEDIA_STATE` | **`MEDIA_OK`** · `AUDIO_ONLY_ACQUISITION = PROVEN` |
| bytes | **696 245**, sha256 `ea372eeb…` — **duas corridas devolveram o mesmo** |
| `CAPTION_TEXT` | **731 caracteres** (legenda do autor, marcada como legenda) |
| oficina | `tempfile.mkdtemp` — **base descartável** (`guardar=False`), nada entra no acervo |
| pedidos | sem conta · sem login · sem cookie · sem contornar muro |
| `CUSTO_USD` | **0.0** |
| matriz | estagiada **em memória** durante a medição e **restaurada** no fim |

> **O ESTÁGIO É DECLARADO.** A lei só passou a `PROVED` depois de o canário
> devolver os números — não antes. Um canário que mudasse a lei para si próprio
> não mediria nada.

### O que a D24 abriu no Instagram, e o que **não** abriu

```
ABERTO    o REEL público por URL directa (vídeo/áudio, legenda/metadados do
          próprio post) · limite PUBLIC_PERSON_VIDEO_ONLY
FECHADO   o PERFIL (muro de login medido na grade por HTTP) · login · conta ·
          cookie de sessão · CAPTCHA/bloqueio · CONTATOS · SEGUIDORES · DM ·
          COMENTÁRIOS DE TERCEIROS · rota paga · PERSONAL_SCORING ·
          NAMED_RESEARCHER_PUBLIC_SCREEN (dono: revisão jurídica)
```

### As duas portas passaram a concordar

A porta operacional (`​.github/workflows/sintonia-scrap.yml`) **recusava** as três
fases do Reel citando a política. Com a matriz a autorizar, isso passou a ser
**duas verdades sobre a mesma rota**. O ramo passou a ser o **canónico**: manda
ao orquestrador com `fase`, `pais`, `fonte` e `url`. Quem continua a travar não é
a política — é a **falta de `SOURCE_ID`** para a publicação de uma pessoa, e quem
o diz é o coletor (`FONTES_AUSENTES`), no sítio onde essa pergunta tem dono.

> `URL` NÃO É `SOURCE_ID` — e a porta operacional **não inventa** uma fonte.

### As provas desta metade

| prova | o que mede |
|---|---|
| `tests/test_d24_video_de_pessoa.py` (**22**) | as rotas do Instagram com os três eixos; o perfil fechado nas duas plataformas; o que a D24 não abre, nomeado; o canário reproduzível |
| `provas/_mutantes_d24.py` | **10 mutações · 10 mortes** (4 delas novas, do Instagram) |
| `tests/test_c13_route_gate.py` | a **âncora** das decisões antigas ganhou a linha do Instagram **com a razão escrita** — mudou declarada |
| `tests/test_c14c_permissao_instagram.py` | o gate passou a exigir: **ALLOWED só com os dois eixos declarados** |
| `tests/test_as_duas_portas_do_scrap.py` | a fase autorizada pela matriz entra pela porta canónica |
