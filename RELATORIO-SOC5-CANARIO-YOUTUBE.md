# RELATÓRIO SOC5 — BANCOS DE TESTE ÓRFÃOS E O CANÁRIO REAL DO YOUTUBE

> Branch `youtube-canario-v1` a partir de `youtube-pronto-v1 @ 92da130e` · 2026-09-23.
> VPN IT medida antes e depois de CADA vídeo; US$ 0; sem login, cookie ou conta; só vídeo público.
> Sala real NÃO tocada (ela está ligada desde as 15:13 na 54330, aberta por outra sessão).

```
BANCOS_ORFAOS     = 4 vivos, 4 provados descartáveis, 4 desligados (0 postgres de teste depois)
CANARIO_YOUTUBE   = 5 canais × 2 vídeos = 10 · RAW 9 · DERIVED 8 · ADMISSÃO SIM 1 · SALA 1
                    (banco descartável próprio, porta canónica, VPN IT antes/depois)
```

## 1. Os bancos de teste ligados

Tabela completa em `docs/operacao/SOC5-BANCOS-DE-TESTE-DESLIGADOS.md`. Resumo:
* Vivos eram **4**, não 10: os outros 6 diretórios só tinham `postmaster.pid` esquecido no disco.
* Os 4: `127.0.0.1`, porta aleatória, base `descartavel` (`banco_descartavel.e_descartavel` = True),
  pasta `pg-prova-cli-*` da `Bancada` das provas, **0 clientes ligados**, sem atividade há 23–60
  min, e **o processo que os abriu já não existia** (órfãos). Nenhum era da SOC1–SOC5.
* `pg_ctl stop -m fast` nos 4 (rc 0). Depois: 0 bancos de teste vivos; memória livre 7,7 GB.
* Contribuição para a tela azul: **NÃO SEI**. 4 servidores parados pesam pouco; não há prova.

## 2. O canário real

**Como.** A lista dos vídeos foi feita onde a chave vive: workflow `curator-youtube-canario`
(disparado por push, run 35901103902) pede ao Scrap `youtube.channel.discovery` — 5 canais, um por
território, 2 vídeos cada, e guarda só os VIDEO_ID (`curadoria/CANARIO-YOUTUBE-SOC5-VIDEOS.json`). O
resto correu nesta máquina, pela porta canónica: orquestrador → `scrap-colheita` fase
`audio-youtube` → ingresso (RAW) → derivação (ASR na GPU) → Admissão → Sala, num Postgres
descartável NOVO numa pasta própria (outro processo apaga `%TEMP%\pg-prova-cli-*`), 32 migrações;
Sala apontada a esse mesmo banco. Portão de egresso IT antes e depois de cada vídeo; 20 s entre
vídeos. O banco foi desligado no fim; os bytes (252 MB) ficaram FORA do repositório.

**Resultado por vídeo** (`curadoria/CANARIO-YOUTUBE-SOC5-RESULTADO.json`):

| Fonte | Universo | Vídeo | RAW | DERIVED | Admissão | Porquê |
|---|---|---|---|---|---|---|
| IT-T2-025 ARPA Lazio | T2 | G-AJsmMac24 | áudio 104 MB | texto 48 KB | NAO_SE_APLICA | **não há régua T2** |
| IT-T2-025 | T2 | 4TP_D8t5e5s | ✔ | ✔ | NAO_SE_APLICA | não há régua T2 |
| IT-T5-037 | T5 | v8KLSChzhrg | áudio 243 s | ✘ | NAO_SEI | o ASR devolveu vazio (`REQUESTED_EMPTY`) — sem fala? NÃO SEI |
| IT-T5-037 | T5 | VEdmSRMTMGA | ✔ | ✔ | NAO_SEI | só uma palavra de T5 («ricerca»); palavra solta não promove |
| IT-T7-015 | T7 | f-Up25Lyn9I | ✔ | ✔ | **SIM** | fala de consorzio → **entrou na Sala** |
| IT-T7-015 | T7 | hwEWEvYFAoQ | ✔ | ✔ | NAO | fala de outro universo (T9: prodotto) — NÃO com prova |
| IT-T10-017 | T10 | wUU1EZ9L-44 | ✘ | ✘ | — | `SOURCE_UNAVAILABLE`: o Scrap não conseguiu o áudio; causa exata NÃO SEI |
| IT-T10-017 | T10 | n26xEq3oR8k | ✔ | ✔ | NAO | fala de outro universo (T7/T9) |
| IT-T12-007 | T12 | ZYZ5bbBVK7I | ✔ | ✔ | NAO_SE_APLICA | **não há régua T12** |
| IT-T12-007 | T12 | A1TKG1wp3KI | ✔ | ✔ | NAO_SE_APLICA | não há régua T12 |

**O que o canário ensina:**
1. **A estrada do YouTube funciona de ponta a ponta:** 9/10 guardados, 8/10 transcritos, 1 na Sala.
2. **Quatro dos 10 pararam por falta de régua, não por defeito do vídeo:** a Admissão desta linha
   só tem régua para T3, T4, T5, T7, T9 e T10. **T2 e T12 não têm** — e há 12 canais YouTube nesses
   dois territórios (4 T2 + 8 T12). A régua T8 existe noutra branch (`youtube-regua-t8-v1`).
3. **Os NAO com prova estão certos pela régua:** um canal T7 (consórcio) que fala de produto cai em
   T9; isso é o vídeo, não a porta. O canal é da fonte; o universo é de cada vídeo.
4. **Um defeito real do ASR:** a transcrição do 1.º vídeo (54 min) repete «di un progetto»
   dezenas de vezes — o reconhecedor «empancou». Passou na Admissão como legível. Para o dono do
   ASR (engenheiro do Scrap): um detetor de repetição antes de declarar o texto legível.
5. **O vigia do egresso funcionou:** a VPN saiu de IT a meio (depois do 3.º vídeo); o canário
   PAROU antes do 4.º, e só continuou quando o portão voltou a dizer IT.

## O que ficou por fazer (e de quem é)
* Régua T2 e T12 na Admissão — dono da Admissão; decisão de gabarito como a da T8 (YT2).
* Juntar a YT2 (régua T8) — coordenação.
* Detetor de repetição do ASR — engenheiro do Scrap.
* Os dois «NÃO SEI» (ASR vazio em 243 s; `SOURCE_UNAVAILABLE`) ficam ditos, sem adivinhar a causa.

## Know-how
§210 (a unificacao-v1 ja ocupa §202-§208).
