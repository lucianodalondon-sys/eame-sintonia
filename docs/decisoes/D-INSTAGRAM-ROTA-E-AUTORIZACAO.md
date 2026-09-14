# A ROTA DO INSTAGRAM, E QUEM AUTORIZOU O QUÊ

**Data:** 2026-09-02 · **Missão:** 14 — Comunicação Pública do Concorrente
**Quem decidiu:** Luciano, expressamente, com o `robots.txt` na mesa.

Este arquivo existe para que ninguém, daqui a seis meses, tenha de reconstruir
por que a coleta de Instagram foi feita do jeito que foi. Ele registra **o que a
fonte escreveu**, **o que a régua da casa manda**, e **o que foi decidido apesar
disso** — nessa ordem, porque é a ordem que torna a decisão auditável.

---

## 1. O que o Instagram escreveu

`https://www.instagram.com/robots.txt`, lido em 2026-09-02, 295 linhas.

No cabeçalho, em prosa:

> *"Collection of data on Instagram through automated means is **prohibited**
> unless you have express written permission from Instagram and may only be
> conducted for the limited purpose contained in said permission."*

Na última diretiva do arquivo:

```
User-agent: *
Disallow: /
```

E 14 agentes nomeados um a um com `Disallow: /` — entre eles `ClaudeBot`,
`GPTBot`, `Scrapy`, `Amazonbot`, `PerplexityBot`.

Não há ambiguidade a resolver: o dono fechou para todos, e escreveu por quê.

## 2. O que a régua desta casa manda fazer nesse caso

`PROTOCOLO-coleta.md` do `portal-sintonia`, citando o próprio Luciano:

> *"O crawler deve respeitar regras de acesso, termos aplicáveis e o protocolo
> `robots.txt`… Não tentaria contornar bloqueios."*

E a distinção que o protocolo faz, que é a que decide aqui:

| | o que quer dizer | tem conserto? |
|---|---|---|
| INDISPONÍVEL | a porta não abriu **daqui** | ✅ sim |
| **NÃO AUTORIZADO** | o dono **escreveu** que não quer | ❌ não. E procurar um jeito **é** contornar bloqueio |

A casa já aplicou isso, sem exceção, a três fontes boas que saíram por causa
disso: **Google Patents** (52 patentes da Adama Agan, de graça), **busca do
DOU** e **Fundação MT** — *"fica fora, o dono disse não"*.

Pela régua, o Instagram é **NÃO AUTORIZADO**.

## 3. A decisão

Em 2026-09-02, apresentado o arquivo e a régua, o Luciano autorizou
expressamente seguir pela rota do navegador deslogado.

    A DECISÃO É DELE, ESTÁ DATADA, E NÃO É UMA LEITURA MINHA DA REGRA.

O que a decisão **não** cobre, e continua trancado:

- **o dado pessoal de quem comenta.** Termos de uso são contrato com a Meta;
  GDPR é gente. `instagram_pessoal.py` segue sendo o dono: pseudônimo HMAC no
  lugar do handle, bruto fora do Git, retenção `UNDECLARED_PENDING_LEGAL_REVIEW`,
  e o portão fechado por padrão. Quem abre esse é a revisão jurídica da ADAMA.
- **login, cookie de terceiro, CAPTCHA.** Nenhuma rota desta casa usa, e a
  autorização acima não muda isso.

## 4. O que fica marcado em cada artefato

Todo item colhido carrega `ROUTE_AUTHORIZATION`, para que ninguém confunda
depois o que veio de onde:

| valor | significa |
|---|---|
| `OFFICIAL_API` | Instagram Graph API / `business_discovery` — autorizado pela Meta por escrito |
| `AD_LIBRARY` | Biblioteca de Anúncios da UE — obrigação de transparência do DSA |
| `BROWSER_UNLOGGED` | rota do navegador deslogado — **contra o `robots.txt`, por decisão de 2026-09-02** |
| `THIRD_PARTY_PAID` | intermediário (Apify) — move quem faz, não torna autorizado |

Sem esse campo, um relatório futuro misturaria material de regimes diferentes e
ninguém saberia qual parte pode ser publicada e qual não.

## 5. A rota autorizada, e o que ela NÃO entrega

Vale registrar que a rota oficial foi levantada antes, e por que ela não basta
sozinha. `business_discovery` da Instagram Graph API entrega, de conta de
empresa de terceiro:

- perfil: `biography`, `followers_count`, `id`, `media_count`, `username`, `website`
- por post: `caption`, `comments_count`, `like_count`, `view_count`, `media_type`,
  `media_url`, `permalink`, `timestamp`, `children`

E **não** entrega, com a doc fechando a porta por escrito:

> *"Note that this does not grant you permission to access media objects
> directly — performing a `GET` on any returned IG Media will fail due to
> insufficient permissions."*

Ou seja: **texto de comentário e stories não existem por rota oficial nenhuma**,
em nível de acesso nenhum. Não é cota nem App Review — não há permissão a pedir.

Exige: aplicativo Meta + conta Instagram Business própria + Página do Facebook
própria + `instagram_basic`, `instagram_manage_insights`, `pages_read_engagement`.
Limite: ~200 chamadas por hora.

## 6. O caminho que ninguém tentou, e que talvez resolva sem atrito

O cabeçalho do próprio `robots.txt` diz *"unless you have **express written
permission** from Instagram"*. A ADAMA é anunciante da Meta. Pedir essa permissão
é conversa comercial, não técnica — e é a única saída que tira este arquivo da
seção 3 e o coloca na seção 5.
