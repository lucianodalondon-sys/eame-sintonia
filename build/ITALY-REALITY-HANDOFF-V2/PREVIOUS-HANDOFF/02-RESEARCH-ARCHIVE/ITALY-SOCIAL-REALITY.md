# Redes sociais — o que existe, o que não existe

**Data:** 2026-09-01

Este documento existe para impedir uma mentira fácil: mostrar ícones de rede social num demo
sem ter o dado por trás.

---

## 1 · Quadro seco

| Plataforma | Registros EAME | Registros Itália | Estado |
|---|---:|---:|---|
| Meta Ads Library (**pago**) | 1.340 + 7 próprios | **414 + 5** | canônico, congelado |
| YouTube | 726 vídeos, 1.190 comentários, 15 transcrições | **147 / 265 / 5** | coletado |
| Instagram **orgânico** | 399 materiais | **0** | só creators ES/FR |
| Facebook **orgânico** | **0** | **0** | **não existe** |
| LinkedIn | 372 posts + perfis | **0 úteis** | painel IT medido e reprovado |
| X / Twitter | **0** | **0** | **nunca coletado** |
| TikTok | **0** | **0** | **nunca coletado** |
| Podcast | **0** | **0** | não existe como objeto |

---

## 2 · Facebook: a confusão mais perigosa do projeto

Todo o "Facebook" do acervo é **Meta Ads Library** — a biblioteca de **publicidade paga**. Ela mostra
cartões de anúncio com texto, mídia, datas e país alcançado. Ela **não** mostra:

- posts orgânicos de página
- comentários
- reações
- alcance orgânico
- o que a página publica no dia a dia

**Nunca fazer a Biblioteca de Anúncios parecer escuta de Facebook.** São coisas diferentes, com fontes
diferentes e custo diferente.

---

## 3 · Instagram

399 materiais orgânicos coletados no `CREATOR-CONTENT-CORPUS-EAME` (442 no total, divididos entre
Instagram e YouTube). Culturas cobertas: TOMATO, PEPPER, MAIZE, PROTECTED_HORTICULTURE, PISTACHIO,
BARLEY, RAPESEED, WHEAT. **Nenhum item italiano.**

O que existe de Itália no Instagram é **identidade resolvida, conteúdo não coletado**: 25 handles
italianos resolvidos numa execução de USD 0,062 (`SEED-IT-RESOLVED`), sem coleta de posts.

---

## 4 · LinkedIn: o painel italiano foi medido e reprovado

Este é um resultado que merece ser dito em voz alta, porque custou dinheiro e ensinou algo.

O piloto italiano de sensores humanos rodou LinkedIn via Apify contra 8 alvos nomeados
(Pasquale De Vita, Nicola Pecchioni, Sabrina Locatelli, Francesca Nocente, Daniela Pacifico,
Stefano Biagetti, Giovanni Drei, Federico Cavina). Resultado registrado em `IT-LINKEDIN-IDENTITY`:

> *"todos os 8 itens pagos são a MESMA pessoa — um Cybersecurity Consultant"*
> `CONFIRMED = 0` · `PLAUSIBLE = 0` · `STATE = ALL_TARGETS_NOT_ENOUGH_EVIDENCE`

E o veredito da camada (`IT-SENSORES-HUMANOS-VEREDITO`):

> **`HUMAN_SENSOR_VERDICT = HUMAN_SENSOR_ADDS_NOTHING_IN_THIS_PANEL`**
> *"a rota funciona, a identidade de dois alvos está provada, e eles simplesmente não postaram"*

**Por que isso é um achado e não uma falha:** provou que buscar pesquisador por nome no LinkedIn devolve
homônimo, e que pesquisador italiano de cereais **não usa LinkedIn para falar de campo**. Poupa gastar de
novo na mesma porta.

⚠️ Se o demo mostrar "sensores humanos no LinkedIn na Itália", estará contradizendo uma medição própria.

---

## 5 · X / Twitter e TikTok

**CURRENT REAL DATA = NOT FOUND.**

Nenhuma coleta, em nenhuma branch, em nenhum país. As únicas ocorrências da palavra "twitter" ou "x" nos
arquivos são **campos de esquema vazios** em fichas de creator (`X: null`, `TIKTOK: null`) — estrutura
preparada, dado ausente.

Avaliação de se vale a pena: pesquisa pública sobre agricultura italiana no X não apareceu como camada
viva em nenhuma das buscas desta missão. A conversa técnica italiana que encontramos vive em
**YouTube, boletins regionais, imprensa técnica (AgroNotizie, Terra e Vita, L'Informatore Agrario) e
eventos presenciais** — não no X. Recomendação: **não abrir essa rota** só para ter o ícone na tela.

---

## 6 · O que o demo pode mostrar de rede social, sem mentir

✅ **Pode:** Meta Ads Library com os 414 cartões italianos, rotulado como *publicidade paga observada*,
com a lei `alcançou ≠ foi dirigido`.
✅ **Pode:** YouTube com os 147 vídeos e 265 comentários italianos, com os tipos de fala preservados.
✅ **Pode:** dizer que Instagram/LinkedIn/X estão fora do escopo desta fase — é uma escolha, não uma falha.

❌ **Não pode:** ícone de Facebook sugerindo escuta orgânica.
❌ **Não pode:** ícone de X, TikTok ou Instagram italiano com número ao lado.
❌ **Não pode:** somar anúncio pago com post orgânico num mesmo contador de "menções".
