# SOC-PESSOAS · o que as pessoas do agro publicam (D24) — 24/09/2026

Pergunta: as pessoas com prova oficial (P4: 16; P5b: 8; P1d: 0 perfis pessoais) publicam
conteúdo técnico agro e de JANELA DE CULTURA (D29)? Pelo caminho já provado do Scrap, sem login,
com o portão de egresso por CONSENSO (PASS IT antes e depois de cada bloco), sem instalar nada.

## O caminho, medido

| alvo | resposta | fonte da medida |
|---|---|---|
| perfil LinkedIn `/in/<slug>` | HTTP 999 `authwall` — **fechado; não se contorna** | D24 (`docs/sintonia-scrap/D24-VIDEO-DE-PESSOA.md`, scrap-linkedin-v1) |
| publicação LinkedIn `/posts/<slug>-activity-<id>` | HTTP 200 a convidado | D24 + esta missão (5/5, 103 kB, sem authwall) |
| listar Reels de uma conta Instagram (`janela`) | ROUTE_NOT_ALLOWED na matriz | SOC-ONDA2 |
| listar vídeos de um canal YouTube | só a Data API; chave só no GitHub | YT3 / P5 |

**Consequência:** ler «as 5 publicações recentes» de uma pessoa exige o ENDEREÇO de cada publicação.
A casa não tem porta de descoberta de publicações de pessoa (lacuna já escrita na D24 §5.3).
Procurei os endereços por busca web (só endereços; toda leitura pela VPN IT): **24 pessoas, 2 com
publicações próprias encontradas** (Giulio Senes 4, Francesca Sparvoli 1). As outras 22: 0 endereços
(os resultados eram homónimos ou o perfil fechado).

O executor da SOC-ONDA2 (`video-linkedin`, capacidade `linkedin.org.video`) é de ORGANIZAÇÃO; o de
PESSOA é o da D24 (`adaptador_linkedin.video_de_post_publico`) — foi esse o usado, sem executor novo.

## Defeito encontrado no leitor da D24 (não corrigido: é do Scrap)

`video_de_post_publico` devolve `TEXT = None` e `PUBLISHED_AT = UNKNOWN` quando o post NÃO tem vídeo
(`IDENTITY_CROSSCHECK = SEM_JSON_LD_NA_PAGINA_DO_POST`), mas a mesma página, pela mesma função de busca
(`_buscar_texto`), traz 103 480 bytes, sem `authwall`, com JSON-LD `SocialMediaPosting` (`articleBody`,
`datePublished`). Post só de texto sai em branco. O texto aqui foi lido do JSON-LD, só do autor
(os comentários de terceiros do mesmo bloco foram descartados — minimização D24).

## Tabela final

| pessoa | origem | publicações lidas | técnico agro | janela D29 | trecho / motivo |
|---|---|---|---|---|---|
| Giulio Senes (Unimi DISAA) | P5b CAND-0914 | 4 (2023-05 → 2025-06) | NÃO | NÃO | paisagismo e horticultura terapêutica: «Orticoltura Terapeutica e Benessere… Hortus Medicus», «Giardino Alzheimer», forum de arquitetura paisagística, curso healing gardens |
| Francesca Sparvoli (CNR IBBA) | P5b CAND-0912 | 1 (2022-12) | NÃO_SEI | NÃO_SEI | a publicação não tem texto do autor na página pública |
| Simon Pierce (Unimi DISAA), YouTube | P5b CAND-0913 | 0 | NÃO_SEI | NÃO_SEI | listar o canal exige a Data API (chave só no GitHub) |
| Fernanda Giorda, Instagram (o LinkedIn dela está na linha de baixo) | P4 CAND-1130 | 0 | NÃO_SEI | NÃO_SEI | listar a conta = `janela` ROUTE_NOT_ALLOWED |
| 16 pessoas P4 (LinkedIn) + 5 P5b (LinkedIn: Menin, Perna, Frugis, Gattolin, Bobbo) | P4 CAND-1131..1146; P5b 0907–0911 | 0 | NÃO_SEI | NÃO_SEI | perfil fechado (999) e 0 endereços de publicação encontrados |

**Totais:** 24 pessoas · 5 publicações lidas (2 pessoas) · técnico agro SIM = 0 · janela D29 SIM = 0 ·
NÃO = 1 pessoa · NÃO_SEI = 23 pessoas.

## Quais merecem virar fonte

**Nenhuma, hoje, pela régua da D29.** Giulio Senes publica, mas sobre paisagismo terapêutico — fora
da janela de cultura. As outras 23 ficam NÃO_SEI: não há rota permitida para ver o que publicam.
Recomendação: não promover; as candidatas ficam como estão (o Curator decide). Para mudar isto é preciso
uma decisão nova — uma porta de descoberta de publicações de pessoa (hoje não existe), ou a chave do
YouTube fora do GitHub para o canal de Simon Pierce.

## Provas

`curadoria/SOC-PESSOAS-LEITURAS-V1.json` (tabela, trechos ≤200 caracteres, sha256 do texto inteiro).
Fora do Git, com sha256: ver `C:/Users/London1/auditoria-madrugada/SOC-PESSOAS-PROVAS-SHA256.txt`.
Rede: 3 blocos de leitura (5 + 1 diagnóstico + 5 pedidos de publicação), todos com portão PASS IT
antes e depois; 0 bytes de vídeo (nenhuma das 5 publicações tinha vídeo); nenhum banco aberto.

---

## Retomada OFFLINE · 25/09 (portão de consenso BLOCKED BR às 01:40 → zero pedidos de rede)

**1 · A janela medida pela régua da casa, e não pelo meu olho.** A régua T1-janela (cultura + dois
momentos) e a T2 (clima/agrometeo), `admissao._do_universo` da `regua-t1-janela-v1` @ ba246704
(VERSAO_DA_REGRA 9), correram offline sobre os 5 textos já lidos:

| publicação | T1 | T2 | janela D29 |
|---|---|---|---|
| Senes 2025-06 (fórum de paisagismo) | NAO | NAO | NÃO |
| Senes 2024-09 (jardim Alzheimer) | NAO | NAO | NÃO |
| Senes 2024-04 (horticultura terapêutica) | NAO_SEI | NAO_SEI | NÃO_SEI |
| Senes 2023-05 (curso healing gardens) | NAO_SEI | NAO_SEI | NÃO_SEI |
| Sparvoli 2022-12 (sem texto do autor) | NAO_SEI | NAO_SEI | NÃO_SEI |
| controle positivo (texto do teste da régua) | **SIM** | NAO_SEI | SIM |

A régua confirma: **0 SIM de janela** em 5 publicações; a régua funciona (controle SIM).

**2 · Numeração.** A lista usa agora os números da **FILA-ÚNICA** (`fila-unica-v1` @ c78da580):
P4 = CAND-1156..1172, P5b = CAND-1148..1155, + CAND-1173 (Claudio Zaccone, P5b @ 754b4f8a).
Os CAND-1130..1146 da `pessoas-agro-v4` ficam **superados** pela fila única (não juntar a v4 como fila).
Lista completa em `curadoria/SOC-PESSOAS-LEITURAS-V1.json` → `LISTA_DAS_PESSOAS` (26 perfis de 25 pessoas:
1 NÃO, 25 NÃO_SEI, cada um com o PORQUÊ e o PRÓXIMO passo).

**3 · O método, pronto para quando a VPN voltar** (fora do Git, com sha256 em
`C:/Users/London1/auditoria-madrugada/SOC-PESSOAS-PROVAS-SHA256.txt`):
- `_soc_pessoas_runner.py` — lê uma lista de endereços de PUBLICAÇÃO; a trava e o pedido são os do
  `adaptador_linkedin` da D24 (sem executor novo); o texto vem do envelope do Scrap e só cai para o
  JSON-LD **do autor** quando o envelope vem vazio (o defeito), dizendo qual usou; a régua T1/T2 corre
  **num processo próprio**, na cópia dela (as duas branches têm módulos com o mesmo nome — misturá-los
  no mesmo processo partiu o `dataclass`); portão de consenso antes de cada publicação, e fora de IT
  **zero pedidos** e estado `ESPERA VPN`.
- **Testes offline 9/9** (rede, portão e páginas são duplos): comentário de terceiro nunca sai; perfil e
  comentários recusados antes da rede; fora de IT zero pedidos; VPN a cair a meio pára; o texto do Scrap
  tem precedência; o fallback declara-se; a régua diz SIM a um boletim e não a um texto sem janela.
- **Mutação 7/7 mortos** (cópia nova por mutante, sem .pyc). Ressalva: M3 (sem portão a meio) morreu por
  ERROR do teste, não por FAIL — morto, mas pela porta mais fraca.

**4 · O que fica à espera**

| o quê | estado |
|---|---|
| procurar endereços de publicação de Claudio Zaccone (P5b, novo) | **ESPERA VPN** |
| reler Sparvoli quando o leitor do Scrap estiver corrigido | **ESPERA VPN** + correção do Scrap |
| listar o canal de Simon Pierce | **ESPERA** chave do YouTube / runner do GitHub |
| as 21 pessoas LinkedIn sem endereço de publicação | **ESPERA DECISÃO**: a casa não tem porta de descoberta de publicações de pessoa (D24 §5.3) |
| Instagram de Fernanda Giorda | **ESPERA DECISÃO** (`janela` ROUTE_NOT_ALLOWED) |
| `git push` desta branch | **ESPERA VPN** (commit só local até o portão dar PASS IT) |

---

## Rede de volta · 25/09 ~01:50 (portão de consenso PASS IT antes e depois; 4 visitas ao LinkedIn, limite 5/site)

**Claudio Zaccone** (UniVR Biotecnologie, CAND-1173 na fila única; nova da P5b): 4 endereços de publicação
achados por busca, 2 lidos (o limite de 5 visitas/site deixou ler 2):

| publicação | técnico agro | T1 | T2 | janela D29 |
|---|---|---|---|---|
| 2023-09 carbono orgânico do solo × clima × beterraba (Belfiore, Verona) | SIM | NAO_SEI | NAO | NÃO_SEI |
| 2026-04 digestato em prados de montanha (com Fondazione Mach), feno | SIM | NAO | NAO | NÃO |

**Executor medido:** o leitor do Scrap (`video_de_post_publico`) devolveu texto em **0 de 6** publicações
(5 de 24/09 + 1 de hoje); o texto veio sempre do JSON-LD do autor. Uma 7.ª publicação foi lida só pelo
JSON-LD, sem o executor, para caber nas 5 visitas.

**Totais atualizados:** 25 pessoas · 7 publicações lidas (3 pessoas) · técnico agro SIM = 1 pessoa (Zaccone) ·
**janela D29 SIM = 0** · merecem virar fonte pela D29: **nenhuma**. Zaccone é fonte possível de CIÊNCIA do
solo (não de janela) — o Curator decide.
