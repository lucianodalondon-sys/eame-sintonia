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
