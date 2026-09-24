# D23 · O VÍDEO DA PÁGINA PÚBLICA DE ORGANIZAÇÃO NO LINKEDIN

**MEDIDO_EM:** 2026-09-23, desta máquina, egresso **IT/datacenter**
(`149.22.91.171` · AS212238 · Palermo) · sem conta, sem login, sem cookie de
sessão, sem navegador e **sem rota paga**.

**O EGRESSO — AS DUAS METADES, E SÓ UMA FOI MEDIDA.**

| ROTA | IP OBSERVADO | ESTADO |
|---|---|---|
| VPN italiana desta máquina (datacenter) | `149.22.91.171` · AS212238 · Datacamp Ltd, Palermo IT | **MEDIDA E SERVE** — 200 na página da organização, sem login e sem cookie; é por aqui que saíram os 2 MP4 e as 2 legendas |
| Sem VPN (IP residencial do Brasil) | — | **NÃO MEDIDA** |

A segunda linha está assim de propósito. Medir a rota sem VPN exige **derrubar a
VPN desta máquina**, que é a mesma que a outra sessão do Scrap (os Reels, na
bancada `scrap-portas-v1`) está a usar — uma acção de máquina, com efeito no
trabalho de outra bancada, que esta missão não tem autorização para tomar
sozinha. Fica como **decisão por tomar**, com o que se sabe: nesta casa a regra
já está escrita noutra fonte — *«a fonte pode responder de outro modo a partir
de um IP não italiano, e isso não foi medido»* — e por isso a rota residencial
não passa a valer por omissão.

**DECISÃO DO DONO:** **D23** — `C:/Users/London1/auditoria-madrugada/DECISOES-DONO-2026-09-23.md`.
O dono REAL autorizou, por escrito e com o risco assumido, a aquisição de
**vídeo** (e da legenda que vem com ele) de páginas de **ORGANIZAÇÕES** no
LinkedIn pelo Sintonia Scrap.

```
OWNER_AUTHORIZED        = SIM          (decisão do dono)
PLATFORM_POLICY_STATUS  = DISALLOWED   (robots.txt do LinkedIn, medido)
LIMITE                  = PUBLIC_ORG_VIDEO_ONLY
```

> **A PLATAFORMA CONTINUA A PROIBIR, E ISSO NÃO SE ESCONDE.** O `robots.txt` do
> LinkedIn abre com *«The use of robots or other automated means to access
> LinkedIn without the express permission of LinkedIn is strictly prohibited.»*
> O que mudou não foi a lei da plataforma — foi **quem assume o risco**. As duas
> frases viajam juntas em cada objeto que sai desta rota.

---

## 1 · O QUE A PÁGINA PÚBLICA SERVE A CONVIDADO

| pedido | resposta medida |
|---|---|
| `GET /company/<slug>/` | **200** · 277 KB a 376 KB · 10 a 18 `urn:li:activity:<id>` |
| `<video data-sources="…">` no HTML servido | presente, com as **rendições MP4 progressivas** |
| `GET` da rendição em `dms.licdn.com` | **206** · `video/mp4` · `Content-Range` conferido |
| `<video data-captions-url="…">` | presente **quando o vídeo tem faixa automática** |
| `GET` da legenda | **200** · `text/vtt` ou `text/plain` · texto legível |

**18 páginas de organizações italianas** medidas ao vivo. **9** delas com pelo
menos um vídeo. O teto conhecido continua a ser a **profundidade**: a página não
expõe endereço de página seguinte.

### As três organizações que decidiram o canário, medidas no mesmo dia

| organização | activity ids | vídeos | legendas |
|---|---|---|---|
| `image-line` (**IT-T8-002**, a única registada no atlas) | 13 | **0** | 0 |
| `gruppocaviro` (candidata `CAND-0094`) | 10 | **2** | **2** (WebVTT) |
| `macfrut-fiera` (candidata `CAND-0097`) | 13 | **2** | 0 |

> O canário foi escolhido por **medição**, e não por lembrança: a organização
> registada não publica vídeo hoje, e isso é um resultado — não uma falha.

---

## 2 · O CANÁRIO REAL — `provas/canario_d23_linkedin_video.py`

Corre pela **porta canónica**, com a **mesma linha de comando que o workflow
corre**, em subprocesso:

```
coleta/scrap_colheita.py video-linkedin --run-id=… --pagina=… --teto=3
```

| medido | valor |
|---|---|
| `VIDEO_MP4_ADQUIRIDOS` | **2** — 2 587 646 e 3 776 684 bytes, com `sha256` |
| `LEGENDAS_ADQUIRIDAS` | **2** — 529 e 819 bytes (`text/vtt`, WebVTT real) |
| `PUBLISHED_AT` | **2026-07-29T12:58:07.800Z** e **2026-08-05T08:12:12.630Z** — declarados pela plataforma no JSON-LD `VideoObject` |
| contraprova de identidade | `CONFIRMADA_PELO_ASSET_DO_JSON_LD` nos dois |
| `INGRESSO_ACEITES` / `RECUSAS` | **2 / 0** |
| `DERIVED` | `NATIVE_CAPTION` · base `DECLARED_BY_PROVIDER` · relação `ORIGINAL` · **1 335 caracteres** de fala real |
| `DOCUMENT_ID` | **`NAO SEI`** — ver §4 |
| pedidos de rede | landing + 1 página por publicação + 1 MP4 + 1 legenda por vídeo |
| `CUSTO_USD` | **0.0** |

**Limites, cumpridos e verificados:** sem rota paga · sem conta · sem login · sem
cookie de sessão · sem contornar login wall, CAPTCHA ou bloqueio · **só páginas de
ORGANIZAÇÃO** (perfil de pessoa é recusado por guarda estática, antes da rede) ·
ritmo baixo, com pausa entre chamadas.

### A cadeia, com o bruto já em disco

```
unidade()  ->  coleta/ingresso.py  ->  o dono do RAW
```

contra uma **base descartável** (SQLite + armazém em pasta temporária — **nada
toca a Sala real**).

> **A REDE MEDE-SE UMA VEZ; A CADEIA MEDE-SE QUANTAS VEZES FOR PRECISO.**
> Repetir a rede para medir a cadeia gasta banda do dono sem medir nada de novo.

---

## 3 · O DEFEITO QUE O CANÁRIO APANHOU — E QUE ERA DESTA MISSÃO

A primeira corrida da cadeia recusou **as duas observações** com
`INGRESS_CONTRATO_QUEBRADO`: o adaptador escrevia dois nomes **inventados** no
campo `DERIVATION_METHOD`, que tem **vocabulário fechado e dono**
(`regras/proveniencia.py`).

| onde | o que eu escrevi | o nome que já existia |
|---|---|---|
| texto do autor | `PLATAFORMA_PUBLICOU_NO_JSON_LD` | **`READ_FROM_SOURCE_FIELD`** |
| legenda automática | `FAIXA_DE_LEGENDA_DA_PLATAFORMA` | **`PROVIDER_ASR`** |

```
UM NOME INVENTADO NUM CAMPO DE VOCABULÁRIO FECHADO
NÃO É UM DETALHE DE ESTILO: É UMA OBSERVAÇÃO QUE NÃO ENTRA.
```

Depois da correção: **`quebras = NENHUMA`**, e o ingresso aceita os dois.

---

## 4 · A MEDIÇÃO QUE IMPORTA: QUEM RECUSA, E PORQUÊ

```
RAW_RECUSADOS_SEM_IDENTIDADE = 2
PORQUE: «sem SOURCE_ID real nao ha estado de identidade possivel,
         e nenhum se inventa»
```

A porta **aceitou** as observações; quem recusa a linha é o **dono do RAW**, com
o nome e o motivo escritos. Isto **não é defeito desta missão**: é a lei da casa
a funcionar —

```
SEM SOURCE_ID REAL NÃO HÁ ESTADO NENHUM. A COLLECTION SEMPRE SOUBE A QUE
FONTE PEDIU; NÃO SABER ISSO NÃO É UMA IDENTIDADE INCOMPLETA,
É UM PEDIDO SEM ORIGEM.
```

O vídeo chega, os bytes ficam em disco com `sha256`, o texto da legenda tem
espécie e linhagem — e a **linha canónica não se escreve**, porque a organização
é **candidata** e não fonte provada. **`URL` não é `SOURCE_ID`.**

### A via que resta, e ela é de CATÁLOGO — não de aquisição

A página do `gruppocaviro` é a candidata **`CAND-0094`**, com prova (a
organização publica este endereço no próprio site). O molde já existe nesta casa:

```
IT-T8-002 · «Image Line — pagina aziendale LinkedIn»   docs/fontes/ATLAS-DE-FONTES-EAME.md
```

— uma **página de LinkedIn como fonte registada**. Com a ficha no atlas, o mesmo
canário passa a gravar RAW com identidade, e o `DOCUMENT_ID` deixa de ser
`NAO SEI`. **Promover a candidata é decisão de quem é dono do catálogo.**

---

## 5 · UMA DISCREPÂNCIA MEDIDA, GUARDADA AO LADO

A plataforma declara **`data-language="en"`** nas páginas do `gruppocaviro`
**e serve legenda em italiano** — o texto das legendas e dos posts é italiano
legível.

O campo guarda o que a plataforma **declarou** (`en`). Inferir `it` do texto
seria exactamente o que a lei da casa proíbe:

```
LÍNGUA ITALIANA NÃO PROVA ITÁLIA, E TEXTO ITALIANO NÃO PROVA `it`.
REGER A LÍNGUA PELO TEXTO É FABRICAR UM CAMPO DECLARADO.
```

A divergência viaja em `DECLARED_LANGUAGE_NOTE`, para que a Inteligência saiba
que este campo precisa de companhia antes de decidir língua.

---

## 6 · O QUE MUDOU NA MÁQUINA, EM NOMES

| peça | o que passou a existir |
|---|---|
| `leis/social_matriz.py` | limiar **`PUBLIC_ORG_VIDEO_ONLY`** e três rotas com os três eixos: `linkedin:pagina-publica-da-organizacao` (`DISCOVER_POST`), `linkedin:data-sources-mp4` (`FETCH_VIDEO_BYTES`), `linkedin:data-captions-url` (`FETCH_TRANSCRIPT`) |
| `coleta/scrap_http.py` | **`autorizacao_do_dono(…)`** — a exceção nomeada que deixa a rota declarada atravessar um `robots` que proíbe, escrevendo as duas frases; e **`buscar_bytes`**, o GET de bytes pelo mesmo portão |
| `coleta/adaptador_linkedin.py` | a descoberta (`cartoes_com_video`), a identidade (`video_do_post`), os bytes e o texto — com parsers puros |
| `coleta/scrap_capacidades.py` | `linkedin.org.posts` · `linkedin.org.video` · `linkedin.org.caption`, todas `PROVEN` e `ONLINE` |
| **as duas portas** | fase `video-linkedin` em `FASES` + `NOMEADOS` + `serve_fases` + `filtros_nomeados` e o ramo canónico no workflow |

**Prova das duas portas:** `tests/test_as_duas_portas_do_scrap.py` — **25/25**.

---

## 7 · O QUE ESTA ROTA NÃO PERMITE

Lista fechada, e ela é o limite da autorização:

- conteúdo de **perfil de PESSOA** (dado pessoal);
- **autenticação**, conta, cookie de sessão;
- **contornar** login wall, CAPTCHA ou bloqueio — se aparecer um muro, mede-se e
  para-se; não se atravessa;
- texto de **comentários** e lista de quem reagiu;
- **rota paga** (a Apify paga continua fora, por decisão do dono);
- qualquer **escrita**, publicação ou interação.

E ela **não se herda**: `LINKEDIN/FETCH_POST` continua `ROUTE_NOT_ALLOWED`, e
`linkedin.native_video` / `linkedin.native_caption` / `linkedin.direct_post`
continuam `BLOCKED` — elas falam de **outras** rotas, e uma capacidade nova não
revoga uma recusa antiga.
