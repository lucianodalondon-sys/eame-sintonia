# PROVA VISUAL — `G7` · `G8` · `G8B`

```
BRANCH     claude/system-map-g7-g8-visual-clarity-v1
BASE       claude/system-map-g6-dependency-order-v1 @ 4224a234
TIRADAS    chromium, 1600x1000, servindo `italia-portale/client`
GITHUB     interceptado e recusado — a frescura não é o objecto desta prova,
           e uma rede lenta tornaria a fotografia não-determinista
```

> **ISTO NÃO É UM PORTÃO, E DIZÊ-LO É PARTE DO TRABALHO.**
> `test_papel_e_leitura_humana.py` prova a LEI (passo `4t` do `MAP RULES
> CHECK`). Estas imagens provam que a lei chegou ao pixel — e nenhum teste
> unitário sabe dizer se um painel ficou compreensível.

O script que as produz corre **fora** do repositório, com o playwright instalado
à parte, tal como `verificar_a_tela.mjs`: a cadeia do mapa não carrega
dependência de terceiro.

---

## O QUE CADA PAR MOSTRA

| ficheiro | o que provar |
|---|---|
| `01-geral` | a câmara abre numa escala em que o cartão se lê · os mostradores dizem de que universo falam |
| `02-coleta` | ligar uma faixa leva a câmara até ela |
| `03-selecao` | `C-ADMISSAO` · papel `ETAPA` medido · dono · o que entra e o que sai · a montante e a jusante |
| `04-unknown` | `C-READY` · papel `ARMAZÉM` **só declarado** · entra 0 · sai 0 · a seta que chega diz **NÃO SEI** |
| `05-busca` | buscar «admissao» · sete achados espalhados, e a câmara **não** se mexe porque não caberiam legíveis |
| `06-portal` | `C-PORTAL-DADOS` · `TELA` · 16 ficheiros a entrar, 1 a sair · o leque de setas sem prova para os cartões do portal |
| `07-controlo` | `C-MAPA-GERADOR` · o System Map olhado como mais uma peça, e não como autoridade |
| `08-caminho` | «mostrar caminho completo» · a montante a azul, a jusante a âmbar, e o caminho **pára** onde a prova acaba |

Não há `ANTES-08`: o caminho completo existia, atravessava 45 ligações por
provar, e por isso a imagem dele antes não é comparável com a de agora — é
outra afirmação.

---

## O DEFEITO, VISÍVEL NAS DUAS IMAGENS

Em `ANTES-04` e `DEPOIS-04`, a mesma peça (`C-READY`) e a mesma ligação
(`C-ADMISSAO -PRODUZ-> C-READY`, `PROVEN = UNKNOWN`):

```
ANTES    seta contínua, ponta cheia, igual às 612 provadas
         dica: «LIGAÇÃO PROVADA»
DEPOIS   seta cinzenta, tracejada, ponta vazada, anel no meio
         selo no painel: NÃO SEI
```

---

## O QUE ESTAS IMAGENS **NÃO** PROVAM

- não provam que o mapa está actualizado (o botão diz `FRESHNESS UNKNOWN`
  porque o GitHub foi recusado de propósito);
- não provam que a árvore fotografada é a que está implantada;
- não provam que as 39 peças sem papel medido passaram a ter papel. Não
  passaram, e os mostradores dizem o número.
