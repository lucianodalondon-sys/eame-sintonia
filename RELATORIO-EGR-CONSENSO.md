# RELATÓRIO · MISSÃO EGR — portão de egresso com consenso

Branch `egresso-consenso-v1` (de `origin/bc4-correcoes-v1` = instalado). **NÃO instalado.**

## Em palavras simples

Antes, para saber se a máquina saía pela Itália, o portão perguntava a UM site (ipinfo.io). Quando
esse site disse «já perguntaste demais» (429), o portão ficou sem resposta e fechou tudo — das
13:05 às 15:05 nada que usa rede andou, com a VPN certa. Agora pergunta a TRÊS sites e decide por
maioria: 2 a dizer Itália → passa; 2 a dizer outro país → fecha; menos de 2 respostas ou empate →
«não sei», que continua a fechar. Quem discorda sozinho não tem veto, mas fica escrito quem disse o
quê. A resposta fica guardada 3 minutos e serve a todos os programas da máquina.

## Provas

| O quê | Resultado |
|---|---|
| Testes da votação (`tests/test_egresso_consenso.py`) | 24 de 24 passam: 2×IT+1×US=PASS · 2×US+1×IT=BLOCKED · 1×IT+2×429=UNKNOWN (bloqueia) · empate=UNKNOWN · cache lida / expirada aos 180 s / outro ambiente de rede não a lê · escrita atómica (falha a meio deixa o ficheiro velho inteiro, sem temporário órfão) |
| Mutação numa cópia (`scripts/egresso/MUTACAO-EGRESSO-CONSENSO-V1.json`) | **11 de 11** mutantes mortos (≥2→≥1, veto ao discordante, 429 a votar, empate a escolher, ipinfo a votar, sem discordância, cache sem validade, cache sem chave de ambiente, escrita não atómica…) |
| Canário real (`scripts/egresso/CANARIO-EGRESSO-CONSENSO-V1.json`) | **2×IT (ipwho.is, ip-api.com) + 1×US (ifconfig.co) = PASS**; ipinfo.io = HTTP 429, só telemetria; 2.ª leitura e um processo Node leram a cache |
| Testes antigos tocados | as falhas que sobram são as MESMAS no instalado (2× PyYAML ausente, 2× micro-coleta 3b) |
| Mapa | `SYSTEM_MAP_CHECK=PASS` (cadeia, com LOCK-PESADO) |

## O que mudou

- `superficie/rede.py` (o dono): `VERIFICADORES`, `voto()`, `consenso()`, `medir()`, cache
  (`ler_cache`/`gravar_cache`, `SINTONIA_EGRESSO_CACHE` ou `%LOCALAPPDATA%\sintonia\egresso-cache.json`),
  `--sem-cache`. O JSON mantém `EGRESS_GATE`, `EGRESS_COUNTRY_CODE`, `EGRESS_REQUIRED`, `CHECKER` e
  acrescenta `VOTOS`, `VOTOS_VALIDOS`, `DISCORDANCIA`, `TELEMETRIA_SEM_VOTO`, `DA_CACHE`, `EGRESS_VERDICT`.
- A chave da cache inclui as variáveis de proxy e `CURL_HOME`: uma prova offline nunca herda o «IT»
  medido pela VPN.
- Consumidores que perguntavam ao ipinfo passam pelo rede.py: coletores Node
  (`italy_recurrent_collect.mjs` — o portão dele —, `italy_pilot_collect.mjs`), `micro_coleta.py`,
  `instagram_janela.py`, `canario_desbloqueio.py`, `colher_gabarito.py`, 3 medidas e 4 canários.
  A guarda do arranque e o vigia já chamavam `rede.py --portao-de-egresso IT`: não mudam de código.
- ⚠️ O dono não devolve IP, cidade nem operadora: onde se gravava isso fica `null`/`NAO_REGISTADO`
  (o piloto) ou `NAO_SEI` (região/operadora no Instagram). Um teste impede nova chamada direta ao ipinfo.

## Incidente meu (dito)

Ao testar se o coletor recorrente carregava, **o Node correu o coletor de verdade** (~2 min, dentro da
minha worktree `C:/egr-v1`): 7 fontes coletadas pela VPN IT, 7 linhas no ledger, um lock. **Nada foi
commitado nem empurrado.** Guardei tudo em `~/egr-residuo-20260924/` (tar sha256
`a8256b4c5f19…c80e`, diff do ledger `b77263b5bff9…2bec`, status) e só depois limpei esses caminhos.

## Plano de instalação (o coordenador instala)

1. Juntar `egresso-consenso-v1` (3 commits + mapa) na linha instalada; conflito provável só nos
   `*.generated.json` do mapa → regerar pela cadeia.
2. A guarda do arranque lê o runtime instalado (`$VIVA`): fica com o consenso ao actualizar a árvore.
3. **O vigia (`~/orca-tools/vigia_vpn.sh`) lê `REPO=C:/g/a3`** — outra árvore: actualizá-la também
   (ou apontar o vigia para o runtime instalado). Sem isto, o vigia continua no ipinfo.
4. Conferir: `py superficie/rede.py --portao-de-egresso IT` → `EGRESS_GATE: PASS` com `VOTOS` e
   `DISCORDANCIA`; segunda chamada em < 3 min → `DA_CACHE: true`.
5. Voltar atrás = reverter o merge; a cache é só um ficheiro em `%LOCALAPPDATA%\sintonia\`.
