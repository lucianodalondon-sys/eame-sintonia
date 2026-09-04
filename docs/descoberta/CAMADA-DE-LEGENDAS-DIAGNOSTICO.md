# A CAMADA DE LEGENDAS NÃO ESTAVA FECHADA — ESTAVA MENTINDO SOBRE POR QUÊ

**Data:** 2026-09-04 · **Dono canônico:** `scripts/youtube_janela.py` · **Branch:** `claude/human-agricultural-sensors-8fv0fw`

A rodada anterior fechou o piloto com uma frase que este documento **corrige**:

> "O bloqueio é de ambiente (o navegador não completou), não de arquitetura."

A primeira metade estava certa pelo motivo errado. A segunda estava errada.

Havia **quatro muros empilhados**, não um — e o código só sabia falar de um deles, com a
frase trocada. Este documento separa os quatro, com o comando que reproduz cada um.

---

## 0 · PRÉ-VOO

```
HEAD_BEFORE            = 4fbe19a4792a0b8550e6915ed17a6698042813bd
BRANCH                 = claude/human-agricultural-sensors-8fv0fw
git status --short     = (vazio)
SCRAP_CANONICAL_OWNER  = scripts/youtube_janela.py   (último commit c88690c, não meu)
APIFY_USED             = NO
NEW_SCRAPER_CREATED    = NO
```

Estado de `LEGENDAS.json` antes: **10 itens, 10 `PORTA_NAO_ABRIU`**, todos com o motivo
`NAVEGADOR_NAO_ALCANCADO: sem Chrome nesta máquina`.

---

## 1 · AS DEZ HIPÓTESES, SEPARADAS

| # | hipótese | veredito | como se reproduz |
|---|---|---|---|
| **A** | navegador não inicia | ✅ **CONFIRMADA (dupla)** | binário não é achado; achado, morre em 0,4 s |
| **B** | navegador inicia mas página não abre | ✅ **CONFIRMADA** | `ERR_CONNECTION_RESET` em *qualquer* HTTPS |
| **C** | página abre mas DOM esperado não aparece | ⛔ **REFUTADA** | `ytInitialData` e `ytInitialPlayerResponse` presentes em 10/10 |
| **D** | consent/cookie/locale interfere | ⛔ **REFUTADA** | 10 combinações, mesmo resultado |
| **E** | vídeo abre e a rota de legenda não é descoberta | ✅ **CONFIRMADA — e é a causa raiz** | player negado ⇒ bloco `captions` nem existe |
| **F** | rota existe e o download falha | ⛔ não alcançada | sem rota, não há download |
| **G** | legenda baixa e o parser falha | ⛔ não alcançada | — |
| **H** | vídeo realmente não tem legenda | ⛔ **REFUTADA** | controle positivo tem faixa e mede zero |
| **I** | timeout/espera incorreto | ⚠️ **PARCIAL** | 25 s não é curto; é longo para um processo já morto |
| **J** | erro é engolido e vira timeout | ✅ **CONFIRMADA** | `stderr=DEVNULL` + laço sem `poll()` |

### A · o navegador não inicia — por dois motivos diferentes, um depois do outro

**A1 — o binário existe e o código não o encontra.**

```
$ python3 scripts/navegador.py
CHROME_FOUND      : False
WHY               : nenhum Chrome ou Chromium encontrado no PATH nem nos caminhos padrão

$ ls -l /opt/pw-browsers/chromium
/opt/pw-browsers/chromium -> /opt/pw-browsers/chromium-1194/chrome-linux/chrome

$ CHROME_EXECUTABLE=/opt/pw-browsers/chromium python3 scripts/navegador.py
CHROME_FOUND      : True     VERSION : 141.0.7390.37
HOW_FOUND         : CHROME_EXECUTABLE
SANDBOX           : ON — `--no-sandbox` não é padrão
```

`navegador.py` procura no `PATH` e nos caminhos padrão de **Windows e macOS**. Não tem
nenhum caminho de instalação de Linux. O Chromium deste contêiner mora em `/opt`, fora do
`PATH` — então o módulo diz, com toda a razão do mundo, que não achou.

**A ponta de extensão já existe e não exige mexer no código:** `CHROME_EXECUTABLE` manda
em tudo, por decisão declarada no próprio arquivo. **Não** acrescentei `/opt/pw-browsers`
à busca automática, e de propósito: o mesmo arquivo explica que trocar silenciosamente o
binário troca User-Agent, codecs e TLS, e duas coletas deixam de ser comparáveis sem que
ninguém tenha mudado nada. Um caminho novo na busca é escolha do dono, não minha.

**A2 — achado o binário, ele se recusa a subir.**

```
$ /opt/pw-browsers/chromium --user-data-dir=/tmp/p1 --no-first-run \
    --no-default-browser-check --remote-debugging-port=9333 about:blank
[ERROR:zygote_host_impl_linux.cc:101] Running as root without --no-sandbox is not supported.
                                       See https://crbug.com/638180.
EXIT=1 em 0,43 s
```

E, passado esse, um segundo: `Missing X server or $DISPLAY` — porque `navegador.argumentos`
monta a linha **com janela** (`headless=False`) e `cdp.subir` nunca pede headless.

**Os dois se resolvem sem desligar a sandbox.** Medido:

```
$ runuser -u nobody -- env HOME=/tmp/nrtest/home \
    xvfb-run -a --server-args='-screen 0 1280x1024x24' \
    /opt/pw-browsers/chromium --user-data-dir=/tmp/nrtest/prof \
    --no-first-run --no-default-browser-check --remote-debugging-port=9332 about:blank

$ curl -s http://127.0.0.1:9332/json/version
{"Browser":"Chrome/141.0.7390.37", "webSocketDebuggerUrl":"ws://127.0.0.1:9332/devtools/..."}
```

**Navegador com janela, sandbox LIGADA, sem `--no-sandbox` em lugar nenhum.** A recusa do
Chromium é a `root`, não ao contêiner: basta não ser `root`. `Xvfb` já está instalado aqui.

> **Não apliquei isso ao dono canônico.** Rodar a coleta como outro usuário e sob `Xvfb` é
> mudança de **como a casa executa**, não de como ela mede — e a decisão em
> `navegador.py:45-49` é do dono. O que este documento entrega é a prova de que o caminho
> honesto existe: **não é preciso desligar a sandbox para ter navegador aqui.**

### J · o erro real ia para o lixo, e o código afirmava outra coisa

Era este o trecho (`scripts/cdp.py`, função `subir`):

```python
p = subprocess.Popen([achado['EXECUTABLE']] + args,
                     stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
fim = time.time() + segundos
while time.time() < fim:
    try:
        abas(porta, timeout=2); return p
    except Erro:
        time.sleep(1)
raise Erro('o Chrome subiu mas a porta %d não passou a escutar em %ds' % (porta, segundos))
```

Três defeitos numa função só:

1. `stderr=DEVNULL` **destrói** a frase `Running as root without --no-sandbox is not supported`.
2. o laço **nunca pergunta** `p.poll()` — dorme os 25 s inteiros esperando um processo que
   morreu no segundo 0,43.
3. a mensagem final **afirma o falso**: "o Chrome subiu". Ele não subiu. Manda o operador
   caçar defeito de rede onde havia binário que se recusou a iniciar.

**Custo medido:** `OBJETOS.json` tem 150 objetos e o lote do dono tem 240. A 25,02 s por
item, são **60 a 100 minutos** imprimindo `PORTA_NAO_ABRIU` a cada 25 s. É literalmente o
"não completou em >15 min" do relatório anterior — não era lentidão, era espera por um morto.

### B · o navegador sobe e não alcança HTTPS nenhum

Com o navegador vivo (sandbox ligada, `Xvfb`), pela porta CDP do próprio repositório:

```
CONTROLE_REDE  https://example.com/                     bytes=186143  ERR_CONNECTION_RESET
CONTROLE_YT    https://www.youtube.com/                 bytes=186159  ERR_CONNECTION_RESET
POSITIVO       https://www.youtube.com/watch?v=jNQXAC9IVRw  bytes=186197  ERR_CONNECTION_RESET
```

`example.com` também falha — então **não é o YouTube**. O proxy do ambiente nomeia a causa
do lado dele:

```
{"kind":"ws_closed_mid_exchange",
 "detail":"tunnel closed (code 1006, Connection ended) after 6s; 1795 B sent, 39 B received",
 "host":"www.youtube.com:443"}
```

`urllib` passa pelo mesmo proxy e funciona; o Chromium não. Testei `--disable-quic` e
`--disable-features=EncryptedClientHello,PostQuantumKyber,TLS13EarlyData`: **nenhum muda o
resultado**. O `README` do proxy classifica esta família como *reportar, não contornar*.

> **A rota de navegador está fechada neste ambiente por motivo de rede, não de código.**

### C e D · refutadas, e a alavanca funcionou

Dez combinações de `Cookie` (nenhum · `SOCS=CAI` · `SOCS` real · `CONSENT=YES+` ·
`PREF=hl=en&gl=US`) × `Accept-Language` (nenhum · `es-ES` · `en-US` · `it-IT`) na mesma URL:
**mesmo `playabilityStatus` em 10/10**.

O controle que fecha o caso: o campo `reason` **volta traduzido** conforme o
`Accept-Language` enviado — *"Inicia sesión…"* / *"Sign in…"* / *"Accedi…"*. O servidor lê e
obedece o cabeçalho. A alavanca funciona; o bloqueio não depende dela.

Nenhuma das ~60 requisições passou por `consent.youtube.com`. O único redirecionamento que
existe vai para `google.com/sorry/index` — a página de abuso.

`ytInitialData` e `ytInitialPlayerResponse` presentes em 10/10, corpo de 1,1–1,2 MB. **O DOM
aparece. O que vem negado é o player.**

---

## 2 · A CAUSA RAIZ, E O REGIME QUE NINGUÉM TINHA MEDIDO

A rota barata (`_por_urllib`) **funciona** aqui: HTTP 200, 1,19 MB, `_bloqueado()` = `False`,
`ytInitialPlayerResponse` presente. Dentro dele:

```
playabilityStatus.status = LOGIN_REQUIRED
playabilityStatus.reason = "Accedi per confermare di non essere un bot"
description              = "Questa operazione aiuta a proteggere la nostra community"
captions                 = AUSENTE
```

**Quando o player volta negado, o YouTube não manda o bloco `captions`.** Faixa nenhuma.
E o corpo do 429, quando ele vem, diz de quem é a culpa:

> *"Nuestros sistemas han detectado tráfico inusual procedente de tu red de ordenadores…
> El bloqueo caducará poco después de que se detengan esas solicitudes."*

Não é bloqueio de conteúdo. É **reputação de IP de datacenter**, e ela escala:

```
VERDE     HTTP 200 · playabilityStatus = OK              · captionTracks PRESENTES
ÂMBAR     HTTP 200 · playabilityStatus = LOGIN_REQUIRED  · captionTracks AUSENTES
VERMELHO  HTTP 429 · redirect → google.com/sorry         · nada
```

O mesmo vídeo, do mesmo IP, no mesmo dia, atravessou os três estados. Os dois fatos que
pareciam se contradizer — "a rota barata funciona" e "tudo dá LOGIN_REQUIRED" — são
**instantâneos de janelas diferentes**, não medições em conflito.

### O defeito que isso expõe, e que é o mais grave desta rodada

`ÂMBAR` é o estado perigoso, porque **passa em todas as verificações que o código tem**:

| verificação | em ÂMBAR |
|---|---|
| HTTP | 200 |
| tamanho | 1,2 MB |
| `_bloqueado()` | `False` — não há `captcha-form`, há `ytInitialData` |
| `ytInitialPlayerResponse` | presente |
| `captionTracks` | **`[]`** |

E o código concluía:

```python
if not faixas:
    r.update({'CAPTION_STATE': 'AUSENTE', 'WHISPER_CANDIDATO': True})
```

**Ausência falsa, com autorização para pagar transcrição.** No controle positivo
`jNQXAC9IVRw` — que tem duas faixas, `de` e `en` — seria gravado "vídeo sem legenda" e
mandado para o Whisper. É o desastre que o cabeçalho do próprio arquivo promete evitar:

> *"Quem confundir os dois vai registrar SEM_LEGENDA num vídeo legendado, e mandar o whisper
> transcrever seis horas de som que já existia escrito."*

---

## 3 · O QUE FOI CORRIGIDO, E O QUE NÃO FOI

### Corrigido — `scripts/cdp.py`, função `subir`

Captura o `stderr` em arquivo, consulta `p.poll()` e para de afirmar o que não aconteceu.

```
ANTES  25,02 s → "o Chrome subiu mas a porta 9341 não passou a escutar em 25s"   (falso)
DEPOIS  1,00 s → "o Chrome NÃO subiu: morreu em 1.0s com código 1, sem abrir a porta 9341.
                  Ele disse: Running as root without --no-sandbox is not supported."
```

Numa passada de 150 objetos: de **~63 minutos de silêncio enganoso** para **1 segundo de
diagnóstico verdadeiro**.

### Corrigido — `scripts/youtube_janela.py`, `_abrir`

O truncamento em 120 caracteres cortava a mensagem exatamente onde ela começava a servir.
Passou para 400.

### Corrigido — `scripts/youtube_janela.py`, `fase_legendas`: o estado que faltava

```
PRESENTE             há texto
AUSENTE              o player veio OK e disse que não há faixa          ← definição estreitada
DECLARADA_MAS_VAZIA  há faixa e o corpo não veio
PLAYER_NEGADO        a página veio inteira e o player voltou negado     ← NOVO
PORTA_NAO_ABRIU      não é sobre o vídeo, é sobre a rede
```

`PLAYER_NEGADO` grava `WHISPER_CANDIDATO = False`.

**Este patch não afrouxa régua nenhuma.** Ele não transforma fracasso em sucesso: move casos
de `sem` (ausência, com whisper autorizado) para `barrado` (porta, sem whisper) — a direção
conservadora. `com` não muda em cenário nenhum. `tests/test_legendas.py` prende os três
ramos com controles sintéticos, sem rede.

### **NÃO** corrigido, de propósito

| o quê | por quê |
|---|---|
| `--no-sandbox` como padrão | `navegador.py:45-49` decide o contrário, e é decisão de segurança. Ligar por conta própria seria mudar a régua para o resultado passar. **E é desnecessário:** não-root + `Xvfb` sobe com sandbox ligada. |
| `/opt/pw-browsers` na busca automática | trocar o binário em silêncio quebra comparabilidade entre coletas. `CHROME_EXECUTABLE` já é a porta declarada. |
| `navegador_primeiro=True` → `False` em `fase_legendas` | a inversão foi escrita contra um 429 que **é real**. Trocar isso é decisão de política de coleta, com o regime medido na mão — não conserto de bug. |
| `_bloqueado()` endurecido | é compartilhado com `fase_canais` e `fase_objetos`, onde a página de canal passa normalmente. A checagem de `playabilityStatus` só faz sentido onde há player. |
| `cdp._vivo` usa `tasklist` (comando do Windows) | **defeito real, reportado, não consertado nesta missão.** Medido: `cdp._vivo(1)` = `False` num Linux onde o PID 1 existe. Consequência: a trava de "um dono por porta" **nunca dispara** aqui — um sensor de medição errada que está morto. Fora do escopo desta rodada. |

---

## 4 · O QUE ISTO NÃO RESOLVE

A camada de legendas **não passou a completar**. Ela passou a **dizer a verdade sobre por
que não completa**, em 1 segundo em vez de uma hora.

Para completar, é preciso resolver a reputação do IP de saída — e isso não é código deste
repositório. As rotas gratuitas que continuam funcionando daqui, medidas:

| rota | estado |
|---|---|
| `/feeds/videos.xml?channel_id=…` | ✅ HTTP 200, 21 kB |
| `oembed` | ✅ HTTP 200 |
| página de canal `/@handle/videos` | ✅ HTTP 200, 1,2 MB |
| `/watch?v=…` | ⚠️ 200 em VERDE, 200-negado em ÂMBAR, 429 em VERMELHO |
| `/api/timedtext` sem assinatura | ❌ HTTP 200 com **0 bytes** (é o desenho, não o defeito) |
| `/api/timedtext?type=list` | ❌ HTTP 429 |

O bloqueio é **específico de `/watch`**: a página de canal responde 200 no mesmo instante em
que `/watch` do mesmo canal responde 429. Isso confirma o que o cabeçalho do dono canônico já
sustentava.

---

## 5 · AS DUAS CONDIÇÕES DO PORTÃO NÃO TÊM A MESMA CAUSA

A rodada anterior (D-034) afirmou: *"as duas falham pela mesma causa: a legenda."*
Isso era **hipótese**, e a medição agora a **refuta pela metade**.

### Condição 6 · a família pesquisador não tem canal de YouTube neste universo

Medição offline, sobre os 89 canais monitoráveis já registrados — nenhuma requisição de
rede, reprodutível a qualquer momento a partir de `SOURCES.json` e `ENTITIES.json` com a
mesma regra de grupo que o piloto usou (`sensor_piloto_social_it.selecionar`):

| grupo | facebook | instagram | linkedin | tiktok | twitter | **youtube** | total |
|---|---|---|---|---|---|---|---|
| **A** — papel de campo provado | 2 | 2 | 0 | 0 | 0 | **4** | 8 |
| **B** — pesquisador/professor | 0 | 0 | 1 | 0 | 1 | **0** | **2** |
| **C** — sem papel provado | 14 | 13 | 8 | 3 | 0 | **41** | 79 |
| | | | | | | **45** | **89** |

Os dois únicos canais da família pesquisador são:

```
twitter    Riccardo Baroncelli   https://twitter.com/R_Baroncelli
linkedin   Andrea Milani         https://www.linkedin.com/in/andrea-milani-ab8aab68
```

**Zero canais de YouTube na família pesquisador.** Cruzando pelo papel da entidade em vez do
grupo do piloto, o resultado é o mesmo: dos 40 canais técnicos de YouTube, **0** pertencem a
entidade com papel científico `PROVADO` — embora existam **84 entidades** com esse papel no
registro.

Legenda é uma camada **de YouTube**. Ela não pode tocar uma família que não está no YouTube.

```
CONDITION_6_TESTABLE_WITH_CURRENT_YOUTUBE_UNIVERSE = NÃO
```

E o motivo **não é a legenda**: é que o universo monitorável autorizado não contém a família.
Abrir Twitter ou LinkedIn está fora desta rodada por lei da missão. A condição 6 permanece
**BLOQUEADA / NÃO SEI**, e continuará bloqueada mesmo com a legenda funcionando perfeitamente.

**D-034 fica corrigida neste ponto:** as duas condições falham, mas por causas diferentes.
Só a condição 5 depende da legenda.

### Condição 5 · depende da legenda, e a legenda não trouxe texto novo

```
HAS_CAPTION             = 0    (dos 150 documentos do piloto)
TRANSCRIPTIONS_EXECUTED = 0
NOT_JUDGEABLE_TITLE_ONLY = 82
```

Nenhum texto novo entrou. A lei da rodada é explícita: *"não reclassificar os 150 documentos
enquanto não houver texto novo real."* Reclassificar sem texto seria inventar.
