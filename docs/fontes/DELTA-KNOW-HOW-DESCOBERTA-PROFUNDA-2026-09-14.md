# DELTA PARA O KNOW-HOW CANÔNICO — ~~§118~~ NÚMERO A ATRIBUIR

> ## ⚠️ CORREÇÃO, 2026-09-14 (missão TAXONOMIA-T1-T12)
>
> **Este ficheiro reivindicava §118, e §118 já está ocupado — por duas seções
> diferentes, em duas branches diferentes.** A medição está em
> [`docs/know-how/SECAO-TAXONOMIA-T1-T12.md`](../know-how/SECAO-TAXONOMIA-T1-T12.md),
> secção *POR QUE O NÚMERO ESTÁ EM BRANCO*:
>
> ```
> SINTONIA-EAME-KNOW-HOW.md existe em 20 branches, com CINCO cabeças
> diferentes, todas de 2026-09-14, declarando §117, §118, §118, §119 e §120.
> Nenhuma delas é a branch-base dos PRs. Não existe `main`.
> ```
>
> O número desta seção passa a ser **a atribuir na cabeça que for decidida como
> canônica** — e essa decisão é do Luciano, não de uma missão.
>
> O erro foi meu e é o mesmo que a missão seguinte veio consertar noutro sítio:
> **afirmar um número sem medir se ele estava livre.**

> **Isto não é o know-how.** O know-how canônico é `SINTONIA-EAME-KNOW-HOW.md` e
> **não vive nesta branch** — a cópia mais avançada que encontrei está em
> `claude/sintonia-local-runner-514cdc` (§117), que é uma branch **local, não
> enviada ao remoto**, e pertence a outra sessão viva.
>
> Copiar o know-how para cá criaria uma segunda verdade, e
> [`AGENTS.md`](../../AGENTS.md) proíbe isso: *"uma lei em dois sítios diverge, e
> a partir daí nenhuma das duas vale"*. Por isso este ficheiro é só o **delta**,
> para ser aplicado ao ficheiro canônico por quem o detém.
>
> **Origem:** missão `ITALY-DEEP-SOURCE-RESEARCH`, branch
> `claude/italy-agricultural-sources-discovery-dfba81`, base `f437ff11`,
> 2026-09-14.

---

## §118.1 — TRÊS CLASSES REAIS DE FONTE QUE O ACERVO NÃO TINHA

Não são categorias inventadas: são donos de informação que apareceram na
medição e que nenhuma gaveta anterior previa.

| classe | exemplo medido | o que ela entrega |
|---|---|---|
| **ordem profissional que publica boletim** | `agronomiforestaliumbria.it` | a Federação dos agrónomos da Umbria publica boletins fitossanitários de olivo e vite. Não representa apenas: produz. |
| **consórcio de seguro agrícola que publica boletim** | `condifesapadova.it`, `codipacal.it` | os *Condifesa* (43 no sistema Asnacodi) existem para seguro, e alguns publicam boletim fitossanitário e agrometeo aos sócios. |
| **organização de produtores dona do próprio boletim** | `oplatium.it`, `assoproli.it` | a OP Latium publica boletim **semanal** de luta guiada à mosca da azeitona, com substância ativa, para ~10.000 sócios. É `PRIMARY`, não intermediária. |

**Consequência:** procurar fonte só em `servizio fitosanitario` + `università` +
`ARPA` deixa de fora quem está mais perto do produtor.

---

## §118.2 — O GRAFO DE LIGAÇÕES ACHA O QUE A BUSCA POR PALAVRA NÃO ACHA

Ferramenta de descoberta canônica desta missão: **andar pelos links das fontes
que a casa já conhece**, e não buscar palavras.

```
240 hosts italianos já conhecidos
  → páginas de rede (link/partner/progetti/bollettini/rete/soci/consorzi)
    → 2.513 hosts raiz novos, cada um com o link que o revelou guardado
```

Custo: 3.081 páginas, ~20 minutos de máquina local, 0 EUR de API.

O que o grafo achou e a busca por palavra não acharia: as 15 federações
regionais da CIA de uma vez, os 4 consórcios fitossanitários provinciais da
Emilia (o acervo tinha 1), o Südtiroler Beratungsring.

**O que o grafo NÃO acha:** pessoas e contas sociais. Para essas, busca por
`cultura + problema` em italiano **e** inglês continua a ser o único caminho.

---

## §118.3 — UM DIRETÓRIO QUE RESOLVE T3 EM 20 REGIÕES DE UMA VEZ

```
fitogest.imagelinenetwork.com/it/pan-piano-uso-sostenibile/bollettini-tecnici-provinciali-zonali/
```

Devolve **uma rota de boletim fitossanitário por região, para as 20 regiões**.
Foi o achado mais eficiente da missão: uma página substituiu vinte buscas.

Lição geral: antes de varrer região por região, procurar **quem já varreu**.

---

## §118.4 — ERRO MEDIDO: A RAIZ ENCURTADA FAZ FONTE CONHECIDA PARECER NOVA

O heurístico de "domínio registável" (últimos dois rótulos) encurtava
`agricoltura.regione.emilia-romagna.it` para `emilia-romagna.it`. Efeito: fontes
que o acervo **já tinha** apareciam como novas, e donos diferentes
(`bo.camcom.gov.it`, `fg.camcom.it`) fundiam-se num só.

**Regra nova:** o dedupe compara **três chaves, da mais forte para a mais fraca**
— (1) URL normalizado, (2) host **completo**, (3) só então a raiz. E quando a
raiz junta subdomínios diferentes, a linha leva aviso escrito.

---

## §118.5 — ERRO MEDIDO: DETECTOR MONOLÍNGUE CEGA NUMA CASA BILÍNGUE

O filtro de "é italiano?" contava palavras italianas. Recusou **duas fontes
italianas de primeira linha**:

- `laimburg.it` — Versuchszentrum Laimburg, o centro de experimentação agrícola
  da Província de Bolzano. Publica em **alemão**.
- `riviste.fupress.net` — *Italian Journal of Agrometeorology*, da Firenze
  University Press, órgão da AIAM. Publica em **inglês**.

**Regra nova:** em Itália, o teste de italianidade tem de aceitar alemão
(Alto Adige), francês (Valle d'Aosta) e inglês (produção científica). Um
detector monolíngue não é conservador — é cego de um olho.

---

## §118.6 — LIMITE MEDIDO DO WebFetch, E O CONTORNO QUE FUNCIONA

`WebFetch` devolveu **HTTP 403** em `agronotizie.imagelinenetwork.com`. A sonda
local em `urllib` com User-Agent de navegador leu **as mesmas páginas com HTTP
200**.

Isto **estende** o padrão já registado para os rótulos do Ministero (curl
devolve 0 bytes, urllib lê). Agora são duas famílias de sítios italianos onde a
ferramenta padrão falha e o urllib local passa.

**Regra:** quando uma leitura falhar por 403, tentar a sonda local com UA de
navegador **antes** de declarar a fonte inacessível.

---

## §118.7 — ERRO MEDIDO NO PRÓPRIO TESTE DE FRESCURA

A segunda prova procurava "há uma data completa de 2025 ou 2026 nesta rota?".
Declarei **dois controles negativos antes de medir** — um portal de programação
encerrada (`psrveneto.it`) e uma página de login (`assam-agrometeo.invionews.net`).

**Os dois passaram como CONFIRMED.** Falso positivo: 2 de 2.

**Conclusão:** o teste prova que *existe uma data recente na página*, **não** que
*a fonte publicou recentemente*. Uma data de prazo, de validade ou de rodapé
passa igual. `CONFIRMED` por este método é **evidência fraca**; a prova forte é
abrir o arquivo e contar edições, e isso é trabalho de gente.

---

## §118.8 — A CLASSE NÃO PODE SOMAR ALCANCE COM AUTORIDADE

Medidas separadas, nunca somadas: `REACH`, `FIELD_AUTHORITY`,
`TECHNICAL_AUTHORITY`, `COMMERCIAL_INFLUENCE`.

Prova de que a separação importa, com números reais desta missão:

| canal | alcance | classe final | porquê |
|---|---|---|---|
| Spicy Moustache | 4,5 M (Instagram) | **REJECT** | horta urbana **em Londres** |
| Giovanni Storti | 1 M (Instagram) | **REJECT** | ator de comédia |
| Vito Vitelli, agrónomo | 15 mil (YouTube) | **A** | 25 anos de consultoria, diretor do CO.VI.L., 306 vídeos |

O canal em A tem **300 vezes menos alcance** que o primeiro recusado.

---

## §118.9 — REGIÃO SÓ SE AFIRMA PELO TEXTO, E O BURACO FICA À VISTA

Nenhuma linha recebeu região por dedução do nome do domínio. Resultado honesto:
**1.004 linhas ficaram com `REGION = NÃO SEI`**.

A alternativa — deduzir pelo domínio — enchia a coluna e tornava a tabela de
cobertura regional uma ficção. `agrisicilia.it` pode ser uma empresa de Milão.

**Regra:** a coluna `REGION_EVIDENCE` acompanha sempre `REGION`, e diz de onde a
região veio. Coluna vazia é resultado; coluna cheia e errada é dano.

---

## §118.10 — REGIÃO POBRE PODE SER FALHA DO MÉTODO, E ISSO MEDE-SE

Na rodada 1 (grafo), seis regiões ficaram com zero fonte de classe A.
Nas rodadas 2 e 3 (busca dirigida a essas regiões), oito consultas devolveram
**~25 hosts novos**, incluindo três de classe A que faltavam no acervo:

- `crsfa.it` — CRSFA "Basile Caramia", Locorotondo (**Puglia**)
- `horta-srl.it` — HORTA srl, que declara operar a **maior rede agrometeorológica
  de Itália** (nacional)
- `laimburg.it` — Versuchszentrum Laimburg (**Alto Adige**)

**Conclusão:** o grafo de ligações é **enviesado** para regiões com tecido
institucional denso. Zero fonte numa região pequena, depois de uma rodada de
grafo, **não é sinal de ausência** — é sinal de que falta a rodada dirigida.

**Regra:** medir saturação por rodadas e por região. Só se pode falar de
saturação quando **três rodadas seguidas** devolvem pouca fonte forte nova.
Nesta missão, as regiões fracas **não** atingiram saturação.

---

## §118.11 — O QUE ESTA MISSÃO NÃO PROVOU

Escrito para que ninguém herde estes números como se fossem mais do que são:

- **nenhuma afiliação de pesquisador foi verificada** num perfil institucional.
  As 60 linhas de pessoas vêm de fontes que as citam;
- **nenhum exemplo de conteúdo foi guardado**. Há endereço e prova de que abriu
  — não há ficheiro;
- **64 linhas de classe B ninguém abriu**: a classe é da máquina. Cada uma diz
  isso na própria linha;
- **reaproveitamento de domínio não é detetável** aqui: exigiria histórico
  (WHOIS, arquivo da web), e nenhum foi consultado;
- nenhuma fonte foi registada no Atlas, nenhum `SOURCE_ID` foi criado, nenhuma
  coleta rodou.

---

## COMO APLICAR ESTE DELTA

1. abrir `SINTONIA-EAME-KNOW-HOW.md` na branch que o detém
   (`claude/sintonia-local-runner-514cdc`, §117);
2. acrescentar `§118` com as secções acima;
3. atualizar a linha **"Última atualização material"** do cabeçalho;
4. **não** copiar este ficheiro para lá: ele é o delta, não a lei.

**Quem decide se entra:** Luciano.
