# LIMITES DE DADO PESSOAL — EAME

**Data:** 2026-08-29 · **MISSÃO 10C** · estado **PROVISÓRIO**

> **Este documento NÃO é parecer jurídico e não substitui um.** Ele registra os limites
> que o produto assume **enquanto** a revisão jurídica não existe, para que nenhuma tela e
> nenhuma coleta avancem por omissão. Quem decide conformidade é revisão jurídica da ADAMA,
> não este repositório.

A pendência de origem é **P-008** no `docs/decisoes/DIARIO-DE-DECISOES.md`: perfilamento de
pesquisadores nomeados, identificados via OpenAlex. Ela **bloqueia** qualquer tela que liste
pessoas nomeadas — e as duas filas prontas (`RESEARCHER_PUBLIC_VOICE_QUEUE_ES` e
`PUBLIC_TECHNICAL_VOICE_QUEUE_ES`) são exatamente listas de pessoas nomeadas.

---

## ESTADOS DECLARADOS

```
NAMED_RESEARCHER_PUBLIC_SCREEN = BLOCKED_PENDING_LEGAL_REVIEW
PERSONAL_SCORING               = PROHIBITED_FOR_CURRENT_PILOT
SENSITIVE_PERSONAL_DATA        = OUT_OF_SCOPE
EMAIL                          = OUT_OF_SCOPE
PHONE                          = OUT_OF_SCOPE
PRIVATE_CONTACT                = OUT_OF_SCOPE
PUBLIC_PROFESSIONAL_EVIDENCE   = TECHNICALLY_IN_SCOPE / LEGALLY_UNDECLARED
```

| estado | o que significa na prática |
|---|---|
| `NAMED_RESEARCHER_PUBLIC_SCREEN` | **nenhuma tela** do produto lista pessoas nomeadas até haver revisão jurídica. O quadro dos 152 e as duas filas de 20 continuam artefatos **internos de trabalho** |
| `PERSONAL_SCORING` | **proibido** pontuar, ranquear, classificar ou pontuar autoridade/influência de pessoa física neste piloto. Já era proibido por método — `FOLLOWERS ≠ AUTHORITY`, `ENGAGEMENT ≠ INFLUENCE` — e agora é proibido também por precaução |
| `SENSITIVE_PERSONAL_DATA` | fora de escopo. Nada de saúde, opinião política, religião, filiação sindical, origem racial, vida sexual |
| `EMAIL` · `PHONE` · `PRIVATE_CONTACT` | fora de escopo. Não coletar, não derivar, não inferir, não armazenar |
| `PUBLIC_PROFESSIONAL_EVIDENCE` | evidência profissional pública **já coletada** (afiliação declarada, ORCID, cargo declarado, publicação indexada) continua tratável **tecnicamente**. **Ser público não declara conformidade jurídica** |

---

## A LEI QUE ESTE DOCUMENTO ACRESCENTA

```
PÚBLICO ≠ LÍCITO DE PROCESSAR
DISPONÍVEL ≠ AUTORIZADO
COLETADO TECNICAMENTE ≠ CONFORME JURIDICAMENTE
```

A camada de voz inteira foi construída sobre fonte pública. **Isso resolve o acesso e não
resolve a base legal.** Confundir os dois seria a mesma classe de erro que o repositório já
mediu em outros lugares: `HTTP 200 ≠ FONTE VIVA`, `REGISTRATION ≠ COMMERCIAL AVAILABILITY`.
Acesso técnico possível nunca foi permissão de uso — o README já dizia isso na regra 6 das
fichas de fonte, e aqui isso vale para **pessoas**.

---

## O QUE ISTO **NÃO** DIZ

- **Não** declara que a coleta feita foi ilícita.
- **Não** declara que foi lícita.
- **Não** interpreta GDPR, base legal, interesse legítimo ou período de retenção.
- **Não** libera nem bloqueia a execução das filas por argumento jurídico — a fila segue
  `NOT_TESTED` por decisão de **missão**, e este documento acrescenta um segundo motivo
  para não correr: falta a revisão.

`NÃO SEI` continua sendo resposta válida, e aqui ela é a resposta correta.
