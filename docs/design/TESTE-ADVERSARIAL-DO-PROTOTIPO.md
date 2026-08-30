# Teste adversarial do protótipo — Espanha

`2026-08-30` · gerado por `scripts/proto_es.py` do pacote congelado `V1.1` (HEAD `9ee2716`)
Publicado: https://claude.ai/code/artifact/b6abefbc-896a-49f9-86b2-1fa4b11c2567

---

## As oito perguntas

| # | Pergunta | Veredito | Por quê |
|---|---|---|---|
| 1 | Faz `window open` parecer "aplique agora"? | **NÃO** | a banda de autorização vem logo abaixo do sinal e diz, em Aleo e em tamanho maior que o resto: *"VERIFICAR O CAMPO no oeste andaluz. Não aplicar produto."* Abaixo dela, `necessidade de campo agora = NOT_KNOWN`. E o próprio campo de estado da janela carrega a frase "ABERTA significa que a aplicação é permitida neste estágio, não que há necessidade de aplicar". |
| 2 | Esconde que o dado de campo está velho? | **NÃO** | a idade é uma das três células da tripla e aparece 7 vezes na página, sempre ao lado do valor. Cádiz: "última observação 27/05/2026". Nunca há número sem idade. |
| 3 | Faz `NONE explicit` parecer "a ADAMA não tem produto"? | **NÃO** | o campo de resposta regulatória do milho traz as duas metades na mesma frase: `EXPLICIT_SPECIES_RESPONSE = NONE` e `GENERIC_WEED_RESPONSE = 7 produtos`. |
| 4 | Faz adjacência parecer cobertura? | **NÃO** | não há mapa. A rede técnica é texto e declara o nível da medida — comarca de um lado, município do outro — e diz "não é voz". |
| 5 | Mostra claim de fabricante como fato? | **NÃO** | não há claim de fabricante na página: `ADAMA · catálogo público` e `Concorrente · público` são ambos `NOT_COLLECTED`, com o motivo. |
| 6 | Esconde `NOT_KNOWN`? | **NÃO** | `.nao-sei` é **mais pesado** que o texto normal (600), não mais claro. "Não sabemos" é uma das três colunas iguais, nunca colapsada. |
| 7 | Sugere disponibilidade comercial? | **NÃO** | `COMMERCIAL_CLOCK = NÃO SEI` no bloco de relógios e `NÃO QUANTIFICADO` na consequência econômica, ambos com o tratamento de ausência. Commercial aparece no mapa como `WAIT FOR INTERNAL DATA`. |
| 8 | Mostra a camada EAME como se tivesse conteúdo? | **NÃO** | a seção existe, em moldura tracejada, e o maior número dela é **"0 relações"**, seguido do motivo. |

**Resultado: 8 de 8. Aprovado.**

---

## Onde o meu próprio teste estava errado

A primeira execução do teste automatizado marcou 2 reprovas. As duas eram bugs **do teste**, não da tela: eu comparei uma string acentuada contra um texto que eu mesmo havia des-acentuado pela metade, e procurei a palavra "enfeite" num campo que não é o renderizado. A tela passava nos dois casos.

Registro isso porque é o mesmo padrão de erro que já apareceu quatro vezes neste projeto: **a medição falha antes do objeto medido**, e o resultado se parece com um achado.

---

## O que o protótipo revelou e o freeze não mostrava

**O pacote congelado é de máquina, não de tela.** Os artefatos foram escritos sem acentuação, por segurança de codificação, e o gerador os renderiza literalmente. A tela mostra "Cadiz", "visivel", "Nao aplicar", "aplicacoes". Está fiel à fonte e está errado para um cliente.

Corrigir isso na tela quebraria a propriedade que dá valor ao protótipo — a de que **nenhum texto de caso foi escrito na interface**. A correção pertence a uma camada de exibição entre o freeze e a tela, e ela não existe.

Do mesmo tipo: o relógio de observação do olivo renderiza *"ver OBSERVATION_DATE — difere por província"*, que é uma referência interna vazando para a superfície.

`DISPLAY_LAYER = MISSING` é o achado desta etapa de design.

---

## Contrato técnico verificado

- 17 tokens de cor definidos no `:root` nu, redefinidos integralmente em `prefers-color-scheme: dark` (guardado por `:not([data-theme="light"])`) e em `[data-theme="dark"]`. Nenhum token existe só dentro de um bloco de tema.
- `body` pinta fundo a partir de token.
- Tabela de ações em contêiner com `overflow-x: auto`; o corpo da página nunca rola na horizontal.
- `:focus-visible` com contorno próprio; `prefers-reduced-motion` respeitado.
- Renderizado nos dois temas em Chromium headless e conferido a olho.
