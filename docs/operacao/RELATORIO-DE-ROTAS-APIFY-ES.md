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
| consumido | **US$ 1,897** | **US$ 2,680** |
| restante | US$ 3,10 | US$ 2,32 |
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
