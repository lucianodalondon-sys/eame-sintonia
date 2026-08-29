# RELATÓRIO DE ROTAS PAGAS — APIFY · ESPANHA

Conforme a **POLÍTICA DE CHAVES DESCARTÁVEIS**. **Nenhum valor de token aparece neste
documento, e não deve aparecer em nenhum outro.**

Data: **2026-08-29**

---

## FLUXO OBRIGATÓRIO CUMPRIDO

`DISCOVERY → TESTE PEQUENO → MEDIÇÃO → ESCOLHA → ESCALA CONTROLADA`

Nenhum Actor foi escalado antes de um teste pequeno medido.

---

## CHAVES

| | chave 1 | chave 2 |
|---|---|---|
| orçamento | US$ 5,00 | US$ 5,00 |
| consumido | **US$ 2,738** | **US$ 2,680** |
| restante | US$ 2,26 | US$ 2,32 |
| estado | **ATIVA** | **ATIVA** |

Orçamentos independentes. Saldo de uma nunca presumido para a outra.

---

## ROTAS TESTADAS E MEDIDAS

| Actor | o que entrega | preço | teste | escala | veredito |
|---|---|---|---|---|---|
| `harvestapi/linkedin-profile-search` | perfis por **cargo declarado** + local | US$ 0,004/perfil | 10 perfis, 9 s | 69 perfis | **MELHOR ROTA DE IDENTIDADE.** 10/10 do teste com cargo técnico declarado |
| `harvestapi/linkedin-profile-scraper` | enriquecimento de perfil conhecido | US$ 0,004/perfil | 10 perfis | 120 perfis | **ESSENCIAL.** É o que dá país e papel; sem ele o LinkedIn fica em NÃO SEI |
| `harvestapi/linkedin-post-search` | autores de posts por termo | por evento | 4 termos | 18 termos · 472 posts | **ÚTIL, ENVIESADO.** 46% das origens são páginas de empresa |
| YouTube (busca + transcrição) | vídeos e fala | por evento | 1 termo | 252 vídeos · 15 transcrições | **MELHOR CUSTO/CONTEÚDO.** 705 mil caracteres |
| `apify/instagram-hashtag-scraper` | posts por hashtag | por evento | **60 itens** | **NÃO ESCALADO** | **REPROVADO NA MEDIÇÃO.** 24 de 32 contas sem país declarado |

---

## A DECISÃO QUE O ORÇAMENTO COMPROU

O Instagram **não foi escalado** porque o teste pequeno mostrou que ele falha na identidade.
Um Actor com muitos itens e identidade fraca é pior que um Actor com poucos itens e
identidade forte — e desta vez isso foi **medido**, não presumido.

O crédito que sobrou de não escalar o Instagram financiou a rota de **busca por cargo**, que
era a que faltava para a identidade do LinkedIn.

---

## A COMPARAÇÃO NAS CINCO DIMENSÕES QUE A REGRA EXIGE

`custo × qualidade × identidade × transcript × atualização`

| Actor | custo medido | qualidade | **identidade** | transcript | atualização |
|---|---|---|---|---|---|
| `harvestapi/linkedin-profile-search` | US$ 0,004/perfil | 10/10 do teste com cargo técnico declarado | **FORTE** — cargo e local vêm de campo declarado | n/a | contínua, sem data de captura da plataforma |
| `harvestapi/linkedin-profile-scraper` | US$ 0,004/perfil | 202 perfis, 179 com país declarado | **FORTE** — é o que resolve país e papel | n/a | idem |
| `harvestapi/linkedin-post-search` | por evento | 472 brutos → **372 únicos** | **FRACA** — o post não declara autor com papel; 46% das origens são páginas de empresa | n/a | `postedAt` absoluto ✅ |
| YouTube (busca) | por evento | 252 vídeos, 27 de 32 campos do contrato | **MÉDIA** — canal declarado, país não | ✅ legendas quando existem | `date` absoluto ✅ |
| `streamers/youtube-comments-scraper` | por evento | 346 comentários, **44,5% com conteúdo** | **AUSENTE** — só *handle*; todo autor entra `UNVERIFIED` | n/a | ❌ só tempo relativo ("hace 2 años") |
| `apify/instagram-hashtag-scraper` | por evento | 39 de 60 itens agronômicos | **AUSENTE** — 24 de 32 contas sem país | n/a | `timestamp` absoluto ✅ |

**A dimensão que decidiu foi identidade, nas duas direções.**
O Instagram foi reprovado apesar de 65% de itens agronômicos. E a busca por cargo foi escalada
apesar de não trazer conteúdo nenhum — porque entrega exatamente o que faltava.

**A dimensão que quase passou despercebida foi atualização.** O Actor de comentários devolve
**tempo relativo**, não data. Isso não impede a coleta, mas impede qualquer uso temporal dos
comentários — e só apareceu porque a comparação obriga a olhar as cinco.

---

## LIMITES DA PLATAFORMA ENCONTRADOS

| limite | efeito | resposta |
|---|---|---|
| plano gratuito: 10 itens por execução | enriquecimento em lotes | 12 lotes de 10 |
| consultas sobre-restritas devolvem **0** | `titulo + termo + região` esvazia | falha fechada, não errada — a consulta foi afrouxada |
| `run-sync` expira | execuções longas caem | `nohup` + gravação incremental |

**Consulta sobre-restrita devolvendo zero é o comportamento correto.** Devolver um número
menor sem avisar seria o erro.

---

## ONDE A CHAVE ESTEVE

Apenas no scratchpad da sessão, fora do repositório, durante a execução.
**Nunca em:** arquivo versionado · commit · README · documentação · fixture · dataset ·
relatório.
